#!/usr/bin/env python3
"""
Image generation using OpenAI API (gpt-image-1).
Uses Visual Bible approach for consistency across book pages.
"""

import os
import sys
import json
import base64
from pathlib import Path
from typing import Optional
from io import BytesIO

from openai import OpenAI
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OPENAI_IMAGE_MODEL, DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_QUALITY, ENV_FILE


def get_client() -> OpenAI:
    """Get configured OpenAI client."""
    env_file = Path(__file__).parent.parent / ENV_FILE
    api_key = None

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break

    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env or environment variables")

    return OpenAI(api_key=api_key)


def generate_image(
    prompt: str,
    reference_image_path: Optional[str] = None,
    size: str = DEFAULT_IMAGE_SIZE,
    quality: str = DEFAULT_IMAGE_QUALITY,
) -> Image.Image:
    """
    Generate an image using OpenAI's gpt-image-1 model.

    Args:
        prompt: Full self-contained image prompt (style + characters + scene)
        reference_image_path: Optional single reference image for character consistency
        size: Image size (1024x1024, 1536x1024, 1024x1536)
        quality: Image quality (low, medium, high)

    Returns:
        PIL Image object
    """
    client = get_client()

    result = client.images.generate(
        model=OPENAI_IMAGE_MODEL,
        prompt=prompt,
        n=1,
        size=size,
        quality=quality,
    )

    # Decode the base64 image
    image_data = base64.b64decode(result.data[0].b64_json)
    image = Image.open(BytesIO(image_data))

    return image


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


def generate_book_images(
    project_id: str,
    pages: Optional[list[int]] = None,
    size: str = DEFAULT_IMAGE_SIZE,
    quality: str = DEFAULT_IMAGE_QUALITY,
) -> dict[int, str]:
    """
    Generate images for a book project.

    Args:
        project_id: Project ID
        pages: Optional list of specific page numbers to generate (None = all)
        size: Image size
        quality: Image quality

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

    # Filter to specific pages if requested
    if pages:
        page_prompts = [p for p in page_prompts if p["page_number"] in pages]

    image_paths = {}
    total = len(page_prompts)

    print(f"Generating {total} image(s) for '{project_id}'...")

    for i, page_prompt in enumerate(page_prompts):
        page_num = page_prompt["page_number"]
        prompt = build_prompt_from_visual_bible(visual_bible, page_prompt)

        print(f"  Page {page_num} ({i+1}/{total})...")

        try:
            image = generate_image(prompt, size=size, quality=quality)

            image_path = images_dir / f"page_{page_num:02d}.png"
            image.save(image_path)

            image_paths[page_num] = str(image_path)
            print(f"    Saved: {image_path}")

        except Exception as e:
            print(f"    Error: {e}")
            image_paths[page_num] = None

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
    parser.add_argument("--size", default=DEFAULT_IMAGE_SIZE, help=f"Image size (default: {DEFAULT_IMAGE_SIZE})")
    parser.add_argument("--quality", default=DEFAULT_IMAGE_QUALITY, help=f"Quality: low/medium/high (default: {DEFAULT_IMAGE_QUALITY})")

    args = parser.parse_args()

    generate_book_images(
        project_id=args.project_id,
        pages=args.pages,
        size=args.size,
        quality=args.quality,
    )


if __name__ == "__main__":
    main()
