#!/usr/bin/env python3
"""
Interactive CLI tool to map source images to book pages.

Usage:
    python scripts/image_mapper.py {project_id}
    python scripts/image_mapper.py {project_id} --batch mapping.json
"""

import sys
import json
from pathlib import Path

from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GUTENBERG_IMAGE_DIR
from book_schemas import ImageManifest, ImageMapping, PublicDomainSource, BookProject


def load_translation(project_dir: Path) -> dict:
    """Load translation.json."""
    translation_file = project_dir / "translation" / "translation.json"
    if not translation_file.exists():
        raise FileNotFoundError(f"Translation not found: {translation_file}")
    with open(translation_file) as f:
        return json.load(f)


def load_source_manifest(project_dir: Path) -> dict:
    """Load source_images/manifest.json."""
    manifest_file = project_dir / GUTENBERG_IMAGE_DIR / "manifest.json"
    if not manifest_file.exists():
        raise FileNotFoundError(
            f"Source images manifest not found: {manifest_file}\n"
            f"Run gutenberg_downloader.py first."
        )
    with open(manifest_file) as f:
        return json.load(f)


def copy_as_png(src_path: Path, dst_path: Path):
    """Copy an image to destination, converting to PNG."""
    img = Image.open(src_path)
    img.save(dst_path, "PNG")


def interactive_mapping(project_id: str) -> ImageManifest:
    """Run interactive mapping session."""
    project_dir = Path("projects") / project_id

    translation = load_translation(project_dir)
    source_manifest = load_source_manifest(project_dir)

    # Load project config for PD source metadata
    config = BookProject.load(str(project_dir / "config.json"))
    if config.public_domain_source:
        pd_source = config.public_domain_source
    else:
        pd_source = PublicDomainSource(
            title=config.title_english,
            author="Unknown",
            illustrator="Unknown",
            source_url=source_manifest.get("source_url", ""),
        )

    source_images = source_manifest.get("images", [])
    pages = translation.get("pages", [])
    images_dir = project_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    source_images_dir = project_dir / GUTENBERG_IMAGE_DIR

    # Print available source images
    print(f"\n{'='*60}")
    print(f"Available source images ({len(source_images)}):")
    print(f"{'='*60}")
    for img in source_images:
        alt = img.get("alt_text", "") or "(no caption)"
        print(f"  {img['index']:3d}. {img['filename']:20s}  {alt}")

    print(f"\n{'='*60}")
    print(f"Page mapping — for each page, enter:")
    print(f"  [number]  = assign source image by number")
    print(f"  g         = mark for AI generation")
    print(f"  s         = skip (no image)")
    print(f"{'='*60}\n")

    mappings = []

    for page in pages:
        page_num = page["page_number"]
        latin = page.get("latin_text", "")
        english = page.get("english_text", "")

        print(f"Page {page_num}: {latin}")
        print(f"         {english}")

        while True:
            choice = input(f"  Image for page {page_num}: ").strip().lower()

            if choice == "s":
                # Skip — no image for this page
                mappings.append(ImageMapping(
                    page_number=page_num,
                    source="existing",
                    image_filename=None,
                ))
                print(f"    -> Skipped\n")
                break

            elif choice == "g":
                # Mark for AI generation
                mappings.append(ImageMapping(
                    page_number=page_num,
                    source="generate",
                ))
                print(f"    -> Marked for generation\n")
                break

            else:
                try:
                    img_idx = int(choice)
                    # Find the source image by index
                    match = None
                    for img in source_images:
                        if img["index"] == img_idx:
                            match = img
                            break

                    if match is None:
                        print(f"    Invalid image number. Try again.")
                        continue

                    # Copy/convert to images/page_XX.png
                    src_path = source_images_dir / match["filename"]
                    dst_filename = f"page_{page_num:02d}.png"
                    dst_path = images_dir / dst_filename

                    copy_as_png(src_path, dst_path)

                    mappings.append(ImageMapping(
                        page_number=page_num,
                        source="existing",
                        image_filename=dst_filename,
                        original_caption=match.get("alt_text", ""),
                    ))
                    print(f"    -> Assigned {match['filename']} as {dst_filename}\n")
                    break

                except ValueError:
                    print(f"    Invalid input. Enter a number, 'g', or 's'.")

    manifest = ImageManifest(pd_source=pd_source, mappings=mappings)

    # Write manifest
    manifest_path = project_dir / "art" / "image_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    print(f"\nManifest written to {manifest_path}")

    # Update translation.json with image paths for assigned images
    translation_file = project_dir / "translation" / "translation.json"
    for page in translation.get("pages", []):
        page_num = page["page_number"]
        for mapping in mappings:
            if mapping.page_number == page_num and mapping.image_filename:
                page["image_path"] = str(images_dir / mapping.image_filename)
    with open(translation_file, "w", encoding="utf-8") as f:
        json.dump(translation, f, indent=2, ensure_ascii=False)

    assigned = sum(1 for m in mappings if m.source == "existing" and m.image_filename)
    generate = sum(1 for m in mappings if m.source == "generate")
    skipped = sum(1 for m in mappings if m.source == "existing" and not m.image_filename)

    print(f"\nSummary: {assigned} assigned, {generate} to generate, {skipped} skipped")
    return manifest


def batch_mapping(project_id: str, batch_file: str) -> ImageManifest:
    """Apply a batch mapping from a JSON file.

    Expected format: {"mappings": {<page_num>: <image_idx_or_"g"_or_"s">}}
    """
    project_dir = Path("projects") / project_id

    translation = load_translation(project_dir)
    source_manifest = load_source_manifest(project_dir)

    config = BookProject.load(str(project_dir / "config.json"))
    if config.public_domain_source:
        pd_source = config.public_domain_source
    else:
        pd_source = PublicDomainSource(
            title=config.title_english,
            author="Unknown",
            illustrator="Unknown",
            source_url=source_manifest.get("source_url", ""),
        )

    source_images = source_manifest.get("images", [])
    pages = translation.get("pages", [])
    images_dir = project_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    source_images_dir = project_dir / GUTENBERG_IMAGE_DIR

    # Load batch mapping
    with open(batch_file) as f:
        batch_data = json.load(f)

    batch_map = batch_data.get("mappings", {})
    mappings = []

    for page in pages:
        page_num = page["page_number"]
        choice = str(batch_map.get(str(page_num), batch_map.get(page_num, "s")))

        if choice == "s":
            mappings.append(ImageMapping(page_number=page_num, source="existing"))
        elif choice == "g":
            mappings.append(ImageMapping(page_number=page_num, source="generate"))
        else:
            img_idx = int(choice)
            match = None
            for img in source_images:
                if img["index"] == img_idx:
                    match = img
                    break

            if match is None:
                print(f"Warning: image {img_idx} not found for page {page_num}, skipping")
                mappings.append(ImageMapping(page_number=page_num, source="existing"))
                continue

            src_path = source_images_dir / match["filename"]
            dst_filename = f"page_{page_num:02d}.png"
            dst_path = images_dir / dst_filename

            copy_as_png(src_path, dst_path)

            mappings.append(ImageMapping(
                page_number=page_num,
                source="existing",
                image_filename=dst_filename,
                original_caption=match.get("alt_text", ""),
            ))
            print(f"Page {page_num}: assigned {match['filename']} as {dst_filename}")

    manifest = ImageManifest(pd_source=pd_source, mappings=mappings)

    manifest_path = project_dir / "art" / "image_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest.model_dump_json(indent=2))

    # Update translation.json with image paths
    translation_file = project_dir / "translation" / "translation.json"
    for page in translation.get("pages", []):
        page_num = page["page_number"]
        for mapping in mappings:
            if mapping.page_number == page_num and mapping.image_filename:
                page["image_path"] = str(images_dir / mapping.image_filename)
    with open(translation_file, "w", encoding="utf-8") as f:
        json.dump(translation, f, indent=2, ensure_ascii=False)

    assigned = sum(1 for m in mappings if m.source == "existing" and m.image_filename)
    generate = sum(1 for m in mappings if m.source == "generate")
    print(f"\nBatch mapping complete: {assigned} assigned, {generate} to generate")
    print(f"Manifest written to {manifest_path}")

    return manifest


def main():
    """CLI for image mapping."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Map source images to book pages"
    )
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--batch", help="JSON file with batch mapping")

    args = parser.parse_args()

    project_dir = Path("projects") / args.project_id
    if not project_dir.exists():
        print(f"Error: Project not found: {args.project_id}")
        sys.exit(1)

    if args.batch:
        batch_mapping(args.project_id, args.batch)
    else:
        interactive_mapping(args.project_id)


if __name__ == "__main__":
    main()
