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


def _resolve_ref_path(path_str: str, ref_images_dir: Path, project_dir: Path | None = None) -> Path | None:
    """Resolve a reference image path, trying multiple base directories."""
    p = Path(path_str)
    if p.exists():
        return p
    # Try relative to reference_images/
    candidate = ref_images_dir / path_str
    if candidate.exists():
        return candidate
    # Try relative to project dir
    if project_dir:
        candidate = project_dir / path_str
        if candidate.exists():
            return candidate
    return None


def _select_reference_images(
    visual_bible: dict | None,
    page_prompt: dict,
    ref_images_dir: Path,
    project_dir: Path | None = None,
    max_refs: int = 6,
) -> list[tuple[str, str]]:
    """
    Automatically select reference images for a page based on scene content.

    Returns list of (path, label) tuples. Labels help the model understand
    each image's role (per Google's recommendation to explicitly label refs).

    Priority: explicit override > style refs + location ref + character refs.
    """
    # Escape hatch: explicit per-page override (no labels — legacy compat)
    explicit = page_prompt.get("reference_images")
    if explicit is not None:
        resolved = []
        for p in explicit:
            rp = _resolve_ref_path(p, ref_images_dir, project_dir)
            if rp:
                resolved.append((str(rp), "Reference image"))
        return resolved

    if not visual_bible:
        return []

    refs = []
    seen_paths = set()

    # 1. Style refs (global defaults — official artwork)
    for i, p in enumerate(visual_bible.get("reference_images", [])):
        rp = _resolve_ref_path(p, ref_images_dir, project_dir)
        if rp and str(rp) not in seen_paths:
            refs.append((str(rp), f"Art style reference"))
            seen_paths.add(str(rp))

    # 2. Location ref
    location = page_prompt.get("location")
    if location and location in visual_bible.get("locations", {}):
        loc_ref = visual_bible["locations"][location].get("reference_image_path")
        if loc_ref:
            rp = _resolve_ref_path(loc_ref, ref_images_dir, project_dir)
            if rp and str(rp) not in seen_paths:
                refs.append((str(rp), f"Location reference — {location}"))
                seen_paths.add(str(rp))

    # 3. Character refs — prioritize non-established characters
    characters = page_prompt.get("characters_in_scene", [])
    char_entries = visual_bible.get("characters", {})
    sorted_chars = sorted(
        characters,
        key=lambda c: char_entries.get(c, {}).get("is_established", False),
    )
    for char_name in sorted_chars:
        if len(refs) >= max_refs:
            break
        char = char_entries.get(char_name, {})
        char_ref = char.get("reference_image_path")
        if char_ref:
            rp = _resolve_ref_path(char_ref, ref_images_dir, project_dir)
            if rp and str(rp) not in seen_paths:
                refs.append((str(rp), f"Character reference — {char_name}"))
                seen_paths.add(str(rp))

    if len(refs) > max_refs:
        print(f"    Warning: {len(refs)} refs exceed budget of {max_refs}, trimming")
        refs = refs[:max_refs]

    return refs


def _load_reference_images(ref_paths: list[str]) -> list[types.Part]:
    """Load reference images as Gemini content parts."""
    parts = []
    for path_str in ref_paths:
        path = Path(path_str)
        if not path.exists():
            print(f"    Warning: reference image not found: {path}")
            continue
        mime = "image/png" if path.suffix == ".png" else "image/jpeg"
        parts.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))
    return parts


def generate_image(
    prompt: str,
    resolution: str = DEFAULT_IMAGE_RESOLUTION,
    reference_images: list[str] | list[tuple[str, str]] | None = None,
) -> Image.Image:
    """
    Generate an image using Google Gemini's image generation.

    Args:
        prompt: Full self-contained image prompt (style + characters + scene)
        resolution: Image resolution for Gemini (default from config)
        reference_images: Either:
            - list of (path, label) tuples from _select_reference_images()
            - list of plain path strings (legacy compat — labeled generically)

    Returns:
        PIL Image object
    """
    client = get_gemini_client()

    # Build content with labeled reference images (per Google's recommendation)
    if reference_images:
        contents = []

        # Normalize to (path, label) tuples
        labeled_refs = []
        for ref in reference_images:
            if isinstance(ref, tuple):
                labeled_refs.append(ref)
            else:
                labeled_refs.append((ref, "Reference image"))

        # Build interleaved text-label + image structure
        contents.append("## Reference Images\n")
        for i, (ref_path, label) in enumerate(labeled_refs, 1):
            path = Path(ref_path)
            if not path.exists():
                print(f"    Warning: reference image not found: {path}")
                continue
            mime = "image/png" if path.suffix == ".png" else "image/jpeg"
            contents.append(f"\n**IMAGE {i} — {label}:**\n")
            contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))

        contents.append(f"\n\n## Scene to Generate\n\nUsing the art style, location, and character appearances from the labeled reference images above, generate this scene:\n\n{prompt}")
    else:
        contents = prompt

    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(
                image_size=resolution,
                aspect_ratio="1:1",
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

    ref_images_dir = Path("reference_images")

    for i, page_prompt in enumerate(page_prompts):
        page_num = page_prompt["page_number"]
        prompt = build_prompt_from_visual_bible(visual_bible, page_prompt)
        prompt = _sanitize_prompt(prompt)

        # Auto-select refs based on characters and location in scene
        page_refs = _select_reference_images(visual_bible, page_prompt, ref_images_dir, project_dir)

        print(f"  Page {page_num} ({i+1}/{total})...")

        try:
            image = generate_image(prompt, resolution=size, reference_images=page_refs)

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


def generate_book_images_batch(
    project_id: str,
    pages: Optional[list[int]] = None,
    size: str = DEFAULT_IMAGE_RESOLUTION,
) -> str:
    """
    Submit a batch job for all book images (50% cheaper, async).

    Returns the batch job name for polling.
    """
    project_dir = Path("projects") / project_id
    prompts_file = project_dir / "art" / "prompts.json"
    images_dir = project_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    if not prompts_file.exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

    with open(prompts_file) as f:
        prompts_data = json.load(f)

    visual_bible_file = project_dir / "art" / "visual_bible.json"
    visual_bible = None
    if visual_bible_file.exists():
        with open(visual_bible_file) as f:
            visual_bible = json.load(f)

    page_prompts = prompts_data["pages"]
    if pages:
        page_prompts = [p for p in page_prompts if p["page_number"] in pages]

    ref_images_dir = Path("reference_images")

    # Build JSONL requests
    jsonl_file = project_dir / "batch_requests.jsonl"

    with open(jsonl_file, "w") as f:
        for page_prompt in page_prompts:
            page_num = page_prompt["page_number"]
            prompt = build_prompt_from_visual_bible(visual_bible, page_prompt)
            prompt = _sanitize_prompt(prompt)

            # Auto-select labeled refs based on characters and location in scene
            page_refs = _select_reference_images(visual_bible, page_prompt, ref_images_dir, project_dir)

            # Build content parts with labeled markdown structure
            parts = []
            if page_refs:
                parts.append({"text": "## Reference Images\n"})
                for i, (ref_path, label) in enumerate(page_refs, 1):
                    ref = Path(ref_path)
                    if ref.exists():
                        mime = "image/png" if ref.suffix == ".png" else "image/jpeg"
                        b64 = base64.b64encode(ref.read_bytes()).decode()
                        parts.append({"text": f"\n**IMAGE {i} — {label}:**\n"})
                        parts.append({"inlineData": {"mimeType": mime, "data": b64}})

                parts.append({"text": f"\n\n## Scene to Generate\n\nUsing the art style, location, and character appearances from the labeled reference images above, generate this scene:\n\n{prompt}"})
            else:
                parts.append({"text": prompt})

            request = {
                "key": f"page_{page_num:02d}",
                "request": {
                    "contents": [{"parts": parts}],
                    "generation_config": {
                        "responseModalities": ["TEXT", "IMAGE"],
                    },
                },
            }
            f.write(json.dumps(request) + "\n")

    print(f"Created batch request file with {len(page_prompts)} pages")

    # Upload and submit batch job
    client = get_gemini_client()

    uploaded_file = client.files.upload(
        file=str(jsonl_file),
        config=types.UploadFileConfig(
            display_name=f"{project_id}-image-batch",
            mime_type="jsonl",
        ),
    )
    print(f"Uploaded request file: {uploaded_file.name}")

    batch_job = client.batches.create(
        model=GEMINI_IMAGE_MODEL,
        src=uploaded_file.name,
        config={"display_name": f"{project_id}-images"},
    )
    print(f"Batch job created: {batch_job.name}")
    print(f"Status: {batch_job.state.name}")
    print(f"\nTo check status: python scripts/image_generator.py {project_id} --batch-status {batch_job.name}")
    print(f"To download results: python scripts/image_generator.py {project_id} --batch-download {batch_job.name}")

    return batch_job.name


def check_batch_status(batch_name: str) -> str:
    """Check the status of a batch job."""
    client = get_gemini_client()
    batch_job = client.batches.get(name=batch_name)
    print(f"Job: {batch_job.name}")
    print(f"Status: {batch_job.state.name}")
    return batch_job.state.name


def download_batch_results(project_id: str, batch_name: str) -> dict[int, str]:
    """Download completed batch results and save images."""
    client = get_gemini_client()
    batch_job = client.batches.get(name=batch_name)

    if batch_job.state.name != "JOB_STATE_SUCCEEDED":
        print(f"Job not complete. Status: {batch_job.state.name}")
        return {}

    project_dir = Path("projects") / project_id
    images_dir = project_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    result_file_name = batch_job.dest.file_name
    print(f"Downloading results from {result_file_name}...")
    file_content_bytes = client.files.download(file=result_file_name)
    file_content = file_content_bytes.decode("utf-8")

    image_paths = {}
    for line in file_content.splitlines():
        if not line:
            continue
        parsed = json.loads(line)
        key = parsed.get("key", "")
        page_num = int(key.replace("page_", ""))

        if "response" in parsed and parsed["response"]:
            for part in parsed["response"]["candidates"][0]["content"]["parts"]:
                if part.get("inlineData"):
                    data = base64.b64decode(part["inlineData"]["data"])
                    img = Image.open(BytesIO(data))
                    image_path = images_dir / f"page_{page_num:02d}.png"
                    img.save(image_path)
                    image_paths[page_num] = str(image_path)
                    print(f"  Saved page {page_num}: {image_path}")
                    break
        elif "error" in parsed:
            print(f"  Page {page_num} error: {parsed['error']}")
            image_paths[page_num] = None

    success = sum(1 for v in image_paths.values() if v)
    print(f"\nDone: {success}/{len(image_paths)} images saved.")
    return image_paths


def generate_reference_images(
    project_id: str,
    size: str = DEFAULT_IMAGE_RESOLUTION,
) -> dict[str, str]:
    """
    Generate reference images for non-established characters and locations.

    Reads the visual bible, identifies characters/locations that need refs,
    generates them, and prints instructions to add paths to visual_bible.json.
    """
    import re

    project_dir = Path("projects") / project_id
    visual_bible_file = project_dir / "art" / "visual_bible.json"
    ref_images_dir = Path("reference_images")

    if not visual_bible_file.exists():
        raise FileNotFoundError(f"Visual bible not found: {visual_bible_file}")

    with open(visual_bible_file) as f:
        visual_bible = json.load(f)

    refs_dir = project_dir / "art" / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)

    # Load style refs for consistency
    style_refs = []
    for p in visual_bible.get("reference_images", []):
        rp = _resolve_ref_path(p, ref_images_dir, project_dir)
        if rp:
            style_refs.append(str(rp))

    style_desc = visual_bible.get("style", {}).get("medium", "Cel-shaded illustration")
    generated = {}

    def _slug(name: str) -> str:
        return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

    # Generate character refs
    for char_name, char_data in visual_bible.get("characters", {}).items():
        if char_data.get("is_established", False):
            continue
        if char_data.get("reference_image_path"):
            rp = _resolve_ref_path(char_data["reference_image_path"], ref_images_dir, project_dir)
            if rp:
                print(f"  Character '{char_name}': ref already exists at {rp}")
                continue

        desc = char_data.get("visual_description", char_name)
        prompt = f"{style_desc}. {desc}. Character reference sheet. Full body, front-facing neutral pose, simple solid-color background. Single character only. Square aspect ratio. No text in image."

        print(f"  Generating character ref: {char_name}...")
        try:
            image = generate_image(prompt, resolution=size, reference_images=style_refs)
            out_path = refs_dir / f"{_slug(char_name)}_ref.png"
            image.save(out_path)
            rel_path = f"art/references/{out_path.name}"
            generated[char_name] = rel_path
            print(f"    Saved: {out_path}")
        except Exception as e:
            print(f"    Error: {e}")

    # Generate location refs
    for loc_name, loc_data in visual_bible.get("locations", {}).items():
        if loc_data.get("reference_image_path"):
            rp = _resolve_ref_path(loc_data["reference_image_path"], ref_images_dir, project_dir)
            if rp:
                print(f"  Location '{loc_name}': ref already exists at {rp}")
                continue

        desc = loc_data.get("visual_description", loc_name)
        prompt = f"{style_desc}. {desc}. Empty establishing shot of this location. No characters present. Wide shot showing the full environment. Square aspect ratio. No text in image."

        print(f"  Generating location ref: {loc_name}...")
        try:
            image = generate_image(prompt, resolution=size, reference_images=style_refs)
            out_path = refs_dir / f"{_slug(loc_name)}_ref.png"
            image.save(out_path)
            rel_path = f"art/references/{out_path.name}"
            generated[loc_name] = rel_path
            print(f"    Saved: {out_path}")
        except Exception as e:
            print(f"    Error: {e}")
        time.sleep(REQUEST_DELAY)

    # Print instructions
    if generated:
        print(f"\n{'='*60}")
        print("Generated reference images. Add these to visual_bible.json:")
        print(f"{'='*60}")
        for name, path in generated.items():
            print(f'  "{name}": set "reference_image_path": "{path}"')
    else:
        print("\nNo new reference images needed — all refs already exist.")

    return generated


def main():
    """CLI for image generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate images for a book project")
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--pages", type=int, nargs="+", help="Specific page numbers to generate")
    parser.add_argument("--size", default=DEFAULT_IMAGE_RESOLUTION,
                        help=f"Image resolution (default: {DEFAULT_IMAGE_RESOLUTION})")
    parser.add_argument("--batch", action="store_true", help="Use batch API (50%% cheaper, async)")
    parser.add_argument("--batch-status", metavar="JOB_NAME", help="Check batch job status")
    parser.add_argument("--batch-download", metavar="JOB_NAME", help="Download batch job results")
    parser.add_argument("--generate-refs", action="store_true",
                        help="Generate reference images for characters and locations")

    args = parser.parse_args()

    if args.generate_refs:
        generate_reference_images(args.project_id, size=args.size)
    elif args.batch_status:
        check_batch_status(args.batch_status)
    elif args.batch_download:
        download_batch_results(args.project_id, args.batch_download)
    elif args.batch:
        generate_book_images_batch(
            project_id=args.project_id,
            pages=args.pages,
            size=args.size,
        )
    else:
        generate_book_images(
            project_id=args.project_id,
            pages=args.pages,
            size=args.size,
        )


if __name__ == "__main__":
    main()
