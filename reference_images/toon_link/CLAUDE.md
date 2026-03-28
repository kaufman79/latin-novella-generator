# Toon Link / Wind Waker Series

Ongoing series of Latin picture books using characters and settings from The Legend of Zelda: The Wind Waker.

## Latinized Names

| English | Latin (nom.) | Genitive | Declension | Notes |
|---------|-------------|----------|------------|-------|
| Link | Lincus | Lincī | 2nd masc. | Always fully declined in Latin text |
| Tetra | Tetra | Tetrae | 1st fem. | |
| Moblin (sg.) | Moblīnus | Moblīnī | 2nd masc. | Long ī in first syllable |
| Moblins (pl.) | Moblīnī | Moblīnōrum | 2nd masc. pl. | |

- Use Latinized names in all Latin text. English text and image prompts still use the English names (the image gen API knows them that way).

## Image Generation

- **Model**: `gemini-3.1-flash-image-preview` (Nano Banana 2) — handles Nintendo characters well
- **Reference images**: Always pass 2 official artwork files as reference images for style consistency:
  - `official/zww-link1.jpg` (standing pose)
  - `official/zww-link2.jpg` (action pose)
  - Add `official/zww-tetra.jpg` when Tetra is in the scene
- **Style instruction prefix**: "Using the exact art style from these reference images — the textured cel-shading, brush-stroke coloring, thick black outlines, and character proportions — generate a new scene:"
- **Never mention** "book", "commercial", or "publication" in prompts
- **Aspect ratio**: Square (1:1) for all pages
- **Resolution**: 512px (cheapest tier, fine for picture books)
- **Batch API**: Use `--batch` flag for 50% discount when generating full books

## Art Style

The Wind Waker cel-shaded look: textured brush-stroke coloring (not smooth/clean vector), bold black outlines, bright saturated colors, chibi proportions (large heads, small bodies). Nighttime scenes use teal ocean, moonlight, and warm torchlight.

## Official Artwork Reference

`official/` directory contains ~30 official Wind Waker character artworks from Creative Uncut. These are the canonical designs — use them as reference images to keep generated art faithful to the source material.

## Characters & Locations Directories

- `characters/` — Generated character reference sheets (front, side, back, expressions)
- `locations/` — Generated location reference images (empty scenes, no characters)

These are supplementary to the official art. Generate new ones as needed for new books.

## Books in This Series

1. **Link and the Stolen Treasure** (`projects/link_and_the_stolen_treasure/`) — Forsaken Fortress heist, fortitudo (perseverance through failure)
