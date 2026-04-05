#!/usr/bin/env python3
"""
Experimental: Chained image generation using Gemini.

Each page uses the PREVIOUS page's image as a reference, creating
a visual chain for consistency testing. Compare against standard
batch approach to see which produces more consistent results.

Usage:
    python scripts/image_generator_interactive.py tower_test --chained
    python scripts/image_generator_interactive.py tower_test --standard
"""

import os
import sys
import json
import time
import base64
from pathlib import Path
from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GEMINI_IMAGE_MODEL, DEFAULT_IMAGE_RESOLUTION, ENV_FILE


def _load_api_key() -> str:
    env_file = Path(__file__).parent.parent / ENV_FILE
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found")
    return key


# --- The 10 page prompts for "Link Climbs the Tower" ---

STYLE = "Cel-shaded illustration in the style of The Legend of Zelda: The Wind Waker. Bold black outlines, textured cel-shaded coloring, bright saturated colors."

PAGES = [
    {
        "page": 1,
        "prompt": f"{STYLE}\n\nWide establishing shot. A tall stone lookout tower stands on a grassy cliff overlooking the ocean. The tower is made of gray stone blocks, has a wooden door at the base, narrow windows spiraling up, and a pointed wooden roof at the top. Toon Link stands at the bottom looking up at the tower, small against it. Blue sky, green grass, ocean behind. Only one tower. No text in image.",
    },
    {
        "page": 2,
        "prompt": f"{STYLE}\n\nToon Link pushes open the heavy wooden door at the base of the same stone tower. Dark interior visible through the doorway. Link's expression is determined. The tower's gray stone blocks and narrow window are visible. Grassy cliff and ocean behind Link. Only one tower, same tower as previous image. No text in image.",
    },
    {
        "page": 3,
        "prompt": f"{STYLE}\n\nInside the tower. A spiral stone staircase winds upward. Torches on the walls cast warm orange light against cool gray stone. Toon Link begins climbing the stairs, looking up. Dark and atmospheric. The stairs curve around the interior wall of the same round stone tower. No text in image.",
    },
    {
        "page": 4,
        "prompt": f"{STYLE}\n\nInside the tower staircase. Toon Link encounters a Moblin guard on a landing halfway up the stairs. The Moblin is large, pig-faced, holding a spear. Link draws his sword. Torchlight flickers on the stone walls. Tense confrontation on the narrow staircase. Same tower interior. No text in image.",
    },
    {
        "page": 5,
        "prompt": f"{STYLE}\n\nAction scene inside the tower. Toon Link swings his sword at the Moblin, who stumbles backward on the stairs. Dynamic motion. Sparks from the sword clash. Torchlight and stone walls of the same tower interior. Link is small but fierce. No text in image.",
    },
    {
        "page": 6,
        "prompt": f"{STYLE}\n\nToon Link continues climbing the spiral staircase higher in the tower. Through a narrow window, the ocean and sky are visible far below — he's high up now. Warm torchlight on gray stone. He looks tired but determined. Sword on his back. Same stone tower interior. No text in image.",
    },
    {
        "page": 7,
        "prompt": f"{STYLE}\n\nToon Link reaches the top of the stairs and pushes through a wooden trapdoor into bright sunlight. Dramatic contrast — dark staircase below, bright sky above. His eyes squint in the light. He climbs out onto the flat stone roof of the tower. No text in image.",
    },
    {
        "page": 8,
        "prompt": f"{STYLE}\n\nOn top of the tower roof. Toon Link stands next to an ornate golden treasure chest on the flat stone roof. Blue sky all around, ocean stretching to the horizon far below. The tower's pointed wooden roof peak is behind him. Wind blows his cap. He reaches for the chest. Only one chest. No text in image.",
    },
    {
        "page": 9,
        "prompt": f"{STYLE}\n\nThe classic Zelda item-get pose. Toon Link holds a glowing red Piece of Heart above his head with both hands. Light radiates from the heart piece. He grins triumphantly. Standing on the tower roof with blue sky and ocean behind him. Iconic moment. No text in image.",
    },
    {
        "page": 10,
        "prompt": f"{STYLE}\n\nWide final shot. The same stone lookout tower on the grassy cliff, seen from a distance. Sunset paints the sky orange and pink. Toon Link is a tiny silhouette on top of the tower, arms raised in victory. Ocean sparkles with sunset light. Peaceful, triumphant ending. Only one tower. No text in image.",
    },
]


def generate_chained(project_dir: Path):
    """Generate pages where each uses the previous page as a reference."""
    client = genai.Client(api_key=_load_api_key())
    out_dir = project_dir / "images" / "chained"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load style refs
    ref_link = Path("reference_images/toon_link/official/zww-link1.jpg")
    style_ref = types.Part.from_bytes(data=ref_link.read_bytes(), mime_type="image/jpeg")

    prev_image_path = None

    for page_data in PAGES:
        pn = page_data["page"]
        prompt = page_data["prompt"]

        print(f"  Chained page {pn}/10...")

        # Build content: style ref + previous page ref (if exists) + prompt
        parts = [style_ref]

        if prev_image_path:
            prev_data = Path(prev_image_path).read_bytes()
            parts.append(types.Part.from_bytes(data=prev_data, mime_type="image/png"))
            instruction = "Using the art style from the first reference image and maintaining visual consistency with the second reference image (the previous page), generate a new scene:\n\n"
        else:
            instruction = "Using the art style from this reference image, generate a new scene:\n\n"

        parts.append(instruction + prompt)

        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=parts,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(
                        image_size=DEFAULT_IMAGE_RESOLUTION,
                        aspect_ratio="1:1",
                    ),
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img = Image.open(BytesIO(part.inline_data.data))
                    img_path = out_dir / f"page_{pn:02d}.png"
                    img.save(img_path)
                    prev_image_path = str(img_path)
                    print(f"    Saved: {img_path}")
                    break

        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(2)

    print(f"\nChained generation complete: {out_dir}")


def generate_standard(project_dir: Path):
    """Generate pages using standard approach (location ref + style refs, no chaining)."""
    client = genai.Client(api_key=_load_api_key())
    out_dir = project_dir / "images" / "standard"
    refs_dir = project_dir / "art" / "references"
    out_dir.mkdir(parents=True, exist_ok=True)
    refs_dir.mkdir(parents=True, exist_ok=True)

    # Load style ref
    ref_link = Path("reference_images/toon_link/official/zww-link1.jpg")
    style_ref = types.Part.from_bytes(data=ref_link.read_bytes(), mime_type="image/jpeg")

    # First, generate a tower reference image
    tower_ref_path = refs_dir / "tower_ref.png"
    if not tower_ref_path.exists():
        print("  Generating tower reference image...")
        response = client.models.generate_content(
            model=GEMINI_IMAGE_MODEL,
            contents=[
                style_ref,
                f"Using the art style from this reference image, generate:\n\n{STYLE}\n\nA tall stone lookout tower on a grassy cliff overlooking the ocean. Gray stone blocks, wooden door at base, narrow windows spiraling up, pointed wooden roof. No characters. Empty establishing shot. Only one tower. No text in image.",
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
                image_config=types.ImageConfig(
                    image_size=DEFAULT_IMAGE_RESOLUTION,
                    aspect_ratio="1:1",
                ),
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                img = Image.open(BytesIO(part.inline_data.data))
                img.save(tower_ref_path)
                print(f"    Tower ref saved: {tower_ref_path}")
                break
        time.sleep(2)

    tower_ref = types.Part.from_bytes(data=tower_ref_path.read_bytes(), mime_type="image/png")

    # Generate each page with style ref + tower ref (no chaining)
    for page_data in PAGES:
        pn = page_data["page"]
        prompt = page_data["prompt"]

        print(f"  Standard page {pn}/10...")

        parts = [style_ref, tower_ref]
        instruction = "Using the art style from the first reference image and the tower design from the second reference image, generate a new scene:\n\n"
        parts.append(instruction + prompt)

        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=parts,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    image_config=types.ImageConfig(
                        image_size=DEFAULT_IMAGE_RESOLUTION,
                        aspect_ratio="1:1",
                    ),
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img = Image.open(BytesIO(part.inline_data.data))
                    img_path = out_dir / f"page_{pn:02d}.png"
                    img.save(img_path)
                    print(f"    Saved: {img_path}")
                    break

        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(2)

    print(f"\nStandard generation complete: {out_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Chained vs standard image generation test")
    parser.add_argument("project_id", help="Project ID")
    parser.add_argument("--chained", action="store_true", help="Generate with chaining (each page refs the previous)")
    parser.add_argument("--standard", action="store_true", help="Generate with standard approach (location ref only)")
    parser.add_argument("--both", action="store_true", help="Generate both for comparison")

    args = parser.parse_args()
    project_dir = Path("projects") / args.project_id

    if args.both or (args.chained and args.standard):
        print("=== CHAINED APPROACH ===")
        generate_chained(project_dir)
        print("\n=== STANDARD APPROACH ===")
        generate_standard(project_dir)
    elif args.chained:
        generate_chained(project_dir)
    elif args.standard:
        generate_standard(project_dir)
    else:
        print("Specify --chained, --standard, or --both")


if __name__ == "__main__":
    main()
