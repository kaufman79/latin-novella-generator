#!/usr/bin/env python3
"""
Image generation using Gemini 2.5 Flash Image API.
Handles reference images for character consistency.
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from io import BytesIO
import base64

from google import genai
from google.genai import types
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookProject, BookTranslation, Character
from scripts.book_manager import load_project, update_project_status
from config import GEMINI_IMAGE_MODEL, ENV_FILE, ERROR_MESSAGES


def get_client() -> genai.Client:
    """
    Get configured Gemini client.

    Raises:
        ValueError: If GEMINI_API_KEY is not found
    """
    # Try .env file first
    env_file = Path(__file__).parent.parent / ENV_FILE
    api_key = None

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break

    # Try environment variable if not found in .env
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        raise ValueError(ERROR_MESSAGES["api_key_missing"])

    return genai.Client(api_key=api_key)


def generate_image(
    prompt: str,
    character_references: Optional[list[dict]] = None,
    reference_image_paths: Optional[list[str]] = None  # DEPRECATED: Use character_references instead
) -> Image.Image:
    """
    Generate image using Gemini 2.5 Flash Image API with character consistency.

    Args:
        prompt: Text description of scene/action (NOT character appearance)
        character_references: List of character dicts with keys:
            - name: Character name (e.g., "Pater")
            - description: Visual description (e.g., "red hair, beard, blue tunic")
            - image_path: Path to reference image
        reference_image_paths: DEPRECATED - Use character_references instead.
            If provided without character_references, will use old generic prompting.

    Returns:
        PIL Image object

    Example:
        characters = [
            {"name": "Pater", "description": "man with red hair and beard", "image_path": "char_pater.png"},
            {"name": "Mater", "description": "woman with blonde hair", "image_path": "char_mater.png"}
        ]
        generate_image("Pater and Mater reading a book", character_references=characters)
    """
    client = get_client()

    # Build contents list
    contents = []

    # New improved approach with character metadata
    if character_references:
        # Build explicit prompt naming each character
        char_descriptions = []
        for i, char in enumerate(character_references, 1):
            char_descriptions.append(
                f"Reference {i}: {char['name']} ({char['description']})"
            )

        # Enhanced prompt with explicit character mapping
        char_intro = ". ".join(char_descriptions)
        enhanced_prompt = (
            f"{char_intro}. "
            f"Using these character reference images for consistency, generate: {prompt}"
        )
        contents.append(enhanced_prompt)

        # Add reference images in the same order
        for char in character_references:
            img_path = char.get('image_path')
            if img_path and Path(img_path).exists():
                ref_image = Image.open(img_path)
                img_byte_arr = BytesIO()
                ref_image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                contents.append(
                    types.Part.from_bytes(
                        data=img_byte_arr.read(),
                        mime_type='image/png'
                    )
                )

    # Fallback to old generic approach (deprecated)
    elif reference_image_paths:
        enhanced_prompt = f"Using the character styles from the reference images provided, {prompt}"
        contents.append(enhanced_prompt)

        for ref_path in reference_image_paths:
            if ref_path and Path(ref_path).exists():
                ref_image = Image.open(ref_path)
                img_byte_arr = BytesIO()
                ref_image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                contents.append(
                    types.Part.from_bytes(
                        data=img_byte_arr.read(),
                        mime_type='image/png'
                    )
                )
    else:
        # No references, just the prompt
        contents = [prompt]

    # Generate image with configuration
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=['Image']
        )
    )

    # Extract image from response
    image_parts = [
        part.inline_data.data
        for part in response.candidates[0].content.parts
        if part.inline_data
    ]

    if not image_parts:
        raise ValueError(f"No image returned from Gemini API. Response: {response}")

    # Convert to PIL Image
    image = Image.open(BytesIO(image_parts[0]))
    return image


def generate_reference_image(project: BookProject) -> str:
    """
    Generate a reference image for character consistency.

    Args:
        project: BookProject instance

    Returns:
        Path to saved reference image
    """
    print("🎨 Generating reference image for character consistency...")

    # Create reference prompt based on theme
    theme_characters = {
        'animal': 'a friendly young boy in simple tunic with a happy animal companion',
        'family': 'a happy Roman family with simple clothing',
        'food': 'a cheerful child with simple food items',
    }

    character_desc = theme_characters.get(
        project.theme,
        'a young child in simple classical clothing'
    )

    reference_prompt = (
        f"Character reference sheet: {character_desc}. "
        f"Style: {project.image_config.art_style}. "
        "Full body view, neutral background, clear details for consistency."
    )

    # Generate image
    print(f"   Prompt: {reference_prompt[:100]}...")
    image = generate_image(reference_prompt)

    # Save reference image
    images_dir = Path(project.project_folder) / 'images'
    images_dir.mkdir(exist_ok=True)

    ref_path = images_dir / 'reference.png'
    image.save(ref_path)

    print(f"   ✅ Saved to {ref_path}")

    return str(ref_path)


def generate_page_images(project: BookProject, translation: BookTranslation) -> dict:
    """
    Generate all page images for a book.

    Args:
        project: BookProject instance
        translation: BookTranslation with pages and image prompts

    Returns:
        Dictionary mapping page numbers to image paths
    """
    images_dir = Path(project.project_folder) / 'images'
    images_dir.mkdir(exist_ok=True)

    # Generate each page image
    image_paths = {}
    total_pages = len(translation.pages)

    print(f"\n🎨 Generating {total_pages} page images...")

    for page in translation.pages:
        page_num = page.page_number
        print(f"\n   Page {page_num}/{total_pages}:")
        print(f"   Latin: {page.latin_text}")

        # Enhance prompt with art style
        full_prompt = f"{page.image_prompt}. Style: {project.image_config.art_style}"
        print(f"   Generating image...")

        try:
            # Build character references for this page (new improved method)
            char_refs = []
            if project.characters and page.characters:
                for char in project.characters:
                    if char.name in page.characters and char.reference_image_path:
                        char_refs.append({
                            'name': char.name,
                            'description': char.description,
                            'image_path': char.reference_image_path
                        })
                if char_refs:
                    print(f"   Using character references: {', '.join(c['name'] for c in char_refs)}")

            # Fallback: Use page 1 as reference if no character references (legacy)
            ref_paths = None
            if not char_refs and page_num > 1:
                page_1_path = images_dir / 'page_01.png'
                if page_1_path.exists():
                    ref_paths = [str(page_1_path)]
                    print(f"   Using page 1 as reference (legacy method)")

            # Generate with references for consistency
            image = generate_image(
                full_prompt,
                character_references=char_refs if char_refs else None,
                reference_image_paths=ref_paths
            )

            # Save image
            image_path = images_dir / f'page_{page_num:02d}.png'
            image.save(image_path)

            image_paths[page_num] = str(image_path)
            print(f"   ✅ Saved to {image_path}")

        except Exception as e:
            print(f"   ❌ Error generating image: {e}")
            image_paths[page_num] = None

    # Save generation log
    log_file = images_dir / 'generation_log.json'
    page_1_ref = images_dir / 'page_01.png'
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'model': GEMINI_IMAGE_MODEL,
        'reference_strategy': 'page_1_as_reference',
        'reference_image': str(page_1_ref) if page_1_ref.exists() else None,
        'art_style': project.image_config.art_style,
        'pages': {
            page.page_number: {
                'prompt': page.image_prompt,
                'image_path': image_paths.get(page.page_number),
                'latin_text': page.latin_text
            }
            for page in translation.pages
        }
    }

    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)

    print(f"\n✅ Generation log saved to {log_file}")

    return image_paths


def main():
    """CLI for image generation."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate images for book')
    parser.add_argument('project_id', help='Project ID')
    parser.add_argument('--reference-only', action='store_true',
                       help='Only generate reference image')

    args = parser.parse_args()

    # Load project
    project = load_project(args.project_id)
    if not project:
        print(f"❌ Project '{args.project_id}' not found")
        sys.exit(1)

    # Check if translation exists
    translation_file = Path(project.project_folder) / 'translation' / 'translation.json'

    if args.reference_only:
        # Just generate reference
        ref_path = generate_reference_image(project)
        print(f"\n✅ Reference image ready: {ref_path}")
        return

    if not translation_file.exists():
        print(f"❌ Translation file not found: {translation_file}")
        print("   Run: python cli.py book-review", args.project_id)
        print("   Then save the JSON output to:", translation_file)
        sys.exit(1)

    # Load translation
    with open(translation_file) as f:
        translation_data = json.load(f)

    translation = BookTranslation(**translation_data)

    # Generate images
    print(f"📚 Generating images for: {project.title_english}")
    print(f"   Theme: {project.theme}")
    print(f"   Style: {project.image_config.art_style}")
    print(f"   Pages: {len(translation.pages)}")
    print()

    image_paths = generate_page_images(project, translation)

    # Update translation JSON with image paths
    for page in translation.pages:
        if page.page_number in image_paths:
            page.image_path = image_paths[page.page_number]

    # Save updated translation
    with open(translation_file, 'w') as f:
        f.write(translation.model_dump_json(indent=2))

    # Update project status
    update_project_status(project, 'images_generated')

    print(f"\n✅ All images generated!")
    print(f"   Images: {len([p for p in image_paths.values() if p])}/{len(translation.pages)}")
    print(f"\n💡 Next step: python cli.py book-pdf {args.project_id}")


if __name__ == '__main__':
    main()
