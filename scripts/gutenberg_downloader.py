#!/usr/bin/env python3
"""
Download all illustrations from a Project Gutenberg HTML page.

Usage:
    python scripts/gutenberg_downloader.py {project_id} --url {gutenberg_html_url}
"""

import sys
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GUTENBERG_IMAGE_DIR, SUPPORTED_IMAGE_FORMATS


class ImageExtractor(HTMLParser):
    """Extract img tags from HTML."""

    def __init__(self):
        super().__init__()
        self.images = []  # list of {"src": ..., "alt": ...}

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            attr_dict = dict(attrs)
            src = attr_dict.get("src", "")
            alt = attr_dict.get("alt", "")
            if src:
                self.images.append({"src": src, "alt": alt})


def download_gutenberg_images(project_id: str, url: str) -> list[dict]:
    """
    Download all illustrations from a Gutenberg HTML page.

    Args:
        project_id: Project ID
        url: Gutenberg HTML page URL

    Returns:
        List of dicts with image metadata
    """
    project_dir = Path("projects") / project_id
    images_dir = project_dir / GUTENBERG_IMAGE_DIR
    images_dir.mkdir(parents=True, exist_ok=True)

    # Fetch the HTML page
    print(f"Fetching: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Parse HTML and extract img tags
    parser = ImageExtractor()
    parser.feed(response.text)

    if not parser.images:
        print("No images found on page.")
        return []

    # Filter to supported image formats
    images = []
    for img in parser.images:
        src = img["src"]
        ext = Path(src.split("?")[0]).suffix.lower()
        if ext in SUPPORTED_IMAGE_FORMATS:
            images.append(img)

    if not images:
        print(f"No images with supported formats found ({', '.join(SUPPORTED_IMAGE_FORMATS)}).")
        return []

    print(f"Found {len(images)} image(s). Downloading...\n")

    manifest_entries = []
    for i, img in enumerate(images, 1):
        src = img["src"]
        alt = img["alt"]

        # Resolve relative URLs
        full_url = urljoin(url, src)

        # Determine extension from URL
        ext = Path(src.split("?")[0]).suffix.lower()
        if not ext:
            ext = ".jpg"

        filename = f"image_{i:03d}{ext}"
        save_path = images_dir / filename

        try:
            img_response = requests.get(full_url, timeout=30)
            img_response.raise_for_status()
            save_path.write_bytes(img_response.content)
            print(f"  {i:3d}. {filename:20s}  {alt or '(no caption)'}")

            manifest_entries.append({
                "index": i,
                "filename": filename,
                "original_url": full_url,
                "alt_text": alt,
            })
        except Exception as e:
            print(f"  {i:3d}. FAILED: {full_url} — {e}")

    # Write manifest
    manifest_path = images_dir / "manifest.json"
    manifest_data = {
        "source_url": url,
        "download_count": len(manifest_entries),
        "images": manifest_entries,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"\nDownloaded {len(manifest_entries)} image(s) to {images_dir}/")
    print(f"Manifest written to {manifest_path}")

    return manifest_entries


def main():
    """CLI for Gutenberg image downloading."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download illustrations from a Project Gutenberg HTML page"
    )
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--url", required=True, help="Gutenberg HTML page URL")

    args = parser.parse_args()

    project_dir = Path("projects") / args.project_id
    if not project_dir.exists():
        print(f"Error: Project not found: {args.project_id}")
        sys.exit(1)

    download_gutenberg_images(args.project_id, args.url)


if __name__ == "__main__":
    main()
