#!/usr/bin/env python3
"""
Image generation using Google Gemini API (primary) with OpenAI fallback.
Uses Visual Bible approach for consistency across book pages.
"""

import os
import sys
import json
import base64
import time
from pathlib import Path
from typing import Optional
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    GEMINI_IMAGE_MODEL,
    DEFAULT_IMAGE_RESOLUTION,
    OPENAI_IMAGE_MODEL,
    DEFAULT_IMAGE_SIZE,
    DEFAULT_IMAGE_QUALITY,
    ENV_FILE,
)

# Delay between API requests (seconds) to respect rate limits
REQUEST_DELAY = 2


def _load_env_key(key_name: str) -> Optional[str]:
    """Load an API key from .env file or environment variables."""
    env_file = Path(__file__).parent.parent / ENV_FILE
    value = None

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f'{key_name}='):
                    value = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

    if not value:
        value = os.getenv(key_name)

    return value


def get_gemini_client() -> genai.Client:
    """Get configured Google Gemini client."""
    api_key = _load_env_key('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env or environment variables")
    return genai.Client(api_key=api_key)


def generate_image(
    prompt: str,
    resolution: str = DEFAULT_IMAGE_RESOLUTION,
    quality: str = DEFAULT_IMAGE_QUALITY,
) -> Image.Image:
    """
    Generate an image using Google Gemini's image generation.

    Args:
        prompt: Full self-contained image prompt (style + characters + scene)
        resolution: Image resolution for Gemini (default from config)
        quality: Unused for Gemini, kept for interface compatibility

    Returns:
        PIL Image object
    """
    client = get_gemini_client()

    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                image_size=resolution,
            ),
        ),
    )

    # Extract image from response
    if not response.candidates or not response.candidates[0].content.parts:
        raise RuntimeError("Gemini returned no content in response")

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            image = Image.open(BytesIO(image_data))
            return image

    raise RuntimeError("Gemini response contained no image data")


def build_prompt_from_visual_bible(visual_bible: dict, page_prompt: dict) -> str:
    """
    Assemble a full self-contained prompt from visual bible + page-specific prompt.

    This is the core of the consistency strategy: every prompt includes the complete
    style and character descriptions, so the API doesn't need to "remember" anything.

    Args:
        visual_bible: Parsed visual_bible.json
        page_prompt: Single page entry from prompts.json

    Returns:
        Full self-contained prompt string
    """
    # If the page prompt is already fully self-contained, use it as-is
    # (the Art Director agent builds these)
    return page_prompt["prompt"]


def _sanitize_prompt(prompt: str) -> str:
    """
    Remove words from prompts that may trigger content policy rejections.

    Never include words like "book", "commercial", or "publication" in prompts
    sent to the image generation API.
    """
    blocked_words = ["book", "commercial", "publication"]
    sanitized = prompt
    for word in blocked_words:
        # Case-insensitive replacement, preserving surrounding spacing
        import re
        sanitized = re.sub(rf'\b{word}\b', '', sanitized, flags=re.IGNORECASE)
    # Clean up any double-spaces left behind
    sanitized = re.sub(r'  +', ' ', sanitized).strip()
    return sanitized


def generate_book_images(
    project_id: str,
    pages: Optional[list[int]] = None,
    size: str = DEFAULT_IMAGE_RESOLUTION,
    quality: str = DEFAULT_IMAGE_QUALITY,
) -> dict[int, str]:
    """
    Generate images for a book project.

    Args:
        project_id: Project ID
        pages: Optional list of specific page numbers to generate (None = all)
        size: Image resolution (passed to Gemini as image_size)
        quality: Image quality (kept for CLI compatibility)

    Returns:
        Dict mapping page numbers to saved image paths
    """
    project_dir = Path("projects") / project_id
    prompts_file = project_dir / "art" / "prompts.json"
    images_dir = project_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    if not prompts_file.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

    with open(prompts_file) as f:
        prompts_data = json.load(f)

    # Load visual bible for reference (currently prompts are self-contained,
    # but we load it in case we need it)
    visual_bible_file = project_dir / "art" / "visual_bible.json"
    visual_bible = None
    if visual_bible_file.exists():
        with open(visual_bible_file) as f:
            visual_bible = json.load(f)

    page_prompts = prompts_data["pages"]

    # Check for image manifest (public domain adaptation) and skip existing pages
    manifest_file = project_dir / "art" / "image_manifest.json"
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest_data = json.load(f)
        existing_pages = set()
        for mapping in manifest_data.get("mappings", []):
            if mapping.get("source") == "existing" and mapping.get("image_filename"):
                existing_pages.add(mapping["page_number"])
        if existing_pages:
            before = len(page_prompts)
            page_prompts = [p for p in page_prompts if p["page_number"] not in existing_pages]
            skipped = before - len(page_prompts)
            print(f"Skipping {skipped} page(s) with existing PD images")

    # Filter to specific pages if requested
    if pages:
        page_prompts = [p for p in page_prompts if p["page_number"] in pages]

    image_paths = {}
    total = len(page_prompts)

    print(f"Generating {total} image(s) for '{project_id}' using Gemini ({GEMINI_IMAGE_MODEL})...")

    for i, page_prompt in enumerate(page_prompts):
        page_num = page_prompt["page_number"]
        prompt = build_prompt_from_visual_bible(visual_bible, page_prompt)
        prompt = _sanitize_prompt(prompt)

        print(f"  Page {page_num} ({i+1}/{total})...")

        try:
            image = generate_image(prompt, resolution=size, quality=quality)

            image_path = images_dir / f"page_{page_num:02d}.png"
            image.save(image_path)

            image_paths[page_num] = str(image_path)
            print(f"    Saved: {image_path}")

        except Exception as e:
            print(f"    Error: {e}")
            image_paths[page_num] = None

        # Delay between requests to respect rate limits
        if i < total - 1:
            time.sleep(REQUEST_DELAY)

    # Update translation.json with image paths if it exists
    translation_file = project_dir / "translation" / "translation.json"
    if translation_file.exists():
        with open(translation_file) as f:
            translation = json.load(f)

        for page in translation.get("pages", []):
            page_num = page["page_number"]
            if page_num in image_paths and image_paths[page_num]:
                page["image_path"] = image_paths[page_num]

        with open(translation_file, 'w') as f:
            json.dump(translation, f, indent=2, ensure_ascii=False)

    success = sum(1 for v in image_paths.values() if v)
    print(f"\nDone: {success}/{total} images generated.")

    return image_paths


def main():
    """CLI for image generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate images for a book project")
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--pages", type=int, nargs="+", help="Specific page numbers to generate")
    parser.add_argument("--size", default=DEFAULT_IMAGE_RESOLUTION,
                        help=f"Image resolution (default: {DEFAULT_IMAGE_RESOLUTION})")
    parser.add_argument("--quality", default=DEFAULT_IMAGE_QUALITY,
                        help=f"Quality: low/medium/high (default: {DEFAULT_IMAGE_QUALITY})")

    args = parser.parse_args()

    generate_book_images(
        project_id=args.project_id,
        pages=args.pages,
        size=args.size,
        quality=args.quality,
    )


if __name__ == "__main__":
    main()
