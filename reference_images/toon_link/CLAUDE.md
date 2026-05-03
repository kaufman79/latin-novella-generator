# Toon Link / Wind Waker Series

Ongoing series of Latin picture books using characters and settings from The Legend of Zelda: The Wind Waker.

**Cross-Zelda shared conventions** (Lincus, Zelda, Ganondorf, Moblīnus, Hyrule, Master Sword, Triforce, etc.) live in [`../zelda/CLAUDE.md`](../zelda/CLAUDE.md). Add new shared-across-Zelda names there. Wind-Waker-specific names (Tetra, Aryll, Helmaroc King, Bokoblin, Korok/Foliolus, Outset Island, Forsaken Fortress, etc.) stay below.

## Latinized Names

| English | Latin (nom.) | Genitive | Declension | Notes |
|---------|-------------|----------|------------|-------|
| Link | Lincus | Lincī | 2nd masc. | Always fully declined in Latin text |
| Tetra | Tetra | Tetrae | 1st fem. | |
| Aryll | Arulla | Arullae | 1st fem. | Wind Waker Book 1 sister |
| Grandma | Avia | Aviae | 1st fem. | Natural Latin for grandmother |
| Moblin (sg.) | Moblīnus | Moblīnī | 2nd masc. | Long ī in first syllable |
| Moblins (pl.) | Moblīnī | Moblīnōrum | 2nd masc. pl. | |
| Bokoblin | Bocoblinus | Bocoblinī | 2nd masc. | Gray goblin-like enemy |
| Korok | Foliolus | Foliolī | 2nd masc. | Diminutive of folium ("little leaf") |
| Helmaroc King | Avis Magna | — | noun phrase | "Great Bird" — simpler for toddler comprehension |

- Use Latinized names in all Latin text. English text and image prompts still use the English names (the image gen API knows them that way).

## Image Generation

- **Model**: `gemini-3.1-flash-image-preview` (Nano Banana 2) — handles Nintendo characters well
- **Reference images**: Always pass 2 official artwork files as reference images for style consistency:
  - `official/zww-link1.jpg` (standing pose, green hero tunic)
  - `official/zww-link2.jpg` (action pose, green hero tunic)
  - Add `official/zww-tetra.jpg` when Tetra is in the scene
- **Link's outfits**: Link wears his blue Outset Island shirt (lobster embroidery) and orange pants BEFORE his birthday in Wind Waker Book 1. After receiving the hero's clothes, he wears the green tunic and cap.
  - For pre-tunic scenes (Book 1 pages 1-5): use `characters/link_island_outfit.png` as the character ref instead of the official green-tunic art
  - For all other scenes: use the default green-tunic refs
- **Location screenshots as refs**: For canonical Wind Waker locations (Outset Island, Forsaken Fortress, Dragon Roost, etc.), pass a game screenshot from `locations/` as a location reference image. Combined with the character art as style reference, the model translates the game's actual location design into our illustration style. This ensures settings match the game, not generic placeholders.
- **Style instruction prefix**: "Using the exact art style from these reference images — the textured cel-shading, brush-stroke coloring, thick black outlines, and character proportions — generate a new scene:"
- **Never mention** "book", "commercial", or "publication" in prompts
- **Aspect ratio**: Square (1:1) for all pages
- **Resolution**: 512px (cheapest tier, fine for picture books)
- **Batch API**: Use `--batch` flag for 50% discount when generating full books
- **Grounding**: Always pass `--grounding` for Wind Waker books. Enables `Tool(google_search=GoogleSearch())` so the model looks up canonical Wind Waker imagery at generation time. No extra cost. Significantly improves accuracy for the Forsaken Fortress, Helmaroc King, Dragon Roost, etc.

## Art Style

The Wind Waker cel-shaded look: textured brush-stroke coloring (not smooth/clean vector), bold black outlines, bright saturated colors, chibi proportions (large heads, small bodies). Nighttime scenes use teal ocean, moonlight, and warm torchlight.

## Official Artwork Reference

`official/` directory contains ~30 official Wind Waker character artworks from Creative Uncut. These are the canonical designs — use them as reference images to keep generated art faithful to the source material.

## Characters & Locations Directories

- `characters/` — Generated character reference sheets in our illustration style
  - `link_island_outfit.png` — Link pre-tunic (Book 1 pages 1-5)
  - `link_back_green.png` — Link green tunic, back view
  - `link_side_green.png` — Link green tunic, side profile
  - `link_looking_back.png` — Link green tunic, looking back over shoulder (for "respexit" / farewell scenes)
  - `aryll_ref.png` — Aryll in canonical blue sundress with red hibiscus flower
  - `orca_ref.png` — old swordmaster with long white beard
  - `bokoblin_ref.png` — gray goblin enemy
  - `moblin_brown_ref.png` — brown pig-boar warrior
  - `moblin_blue_ref.png` — blue Moblin variant
  - `korok_ref.png` — Foliolus (Korok leaf-face spirit)
  - `grunio_ref.png` — original character from Thief's Lantern
  - `poe_ref.png` — single Poe ghost
  - `poes_group_ref.png` — four colored Poes
  - `gohma_ref.png` — Dragon Roost boss (armored centipede)
  - `magtail_ref.png` — dragon-insect enemy
  - `darknut_ref.png` — armored knight with giant sword
- `locations/` — Location reference images in our illustration style
  - `outset_island_ref.png` — Outset Island village/hillside
  - `forsaken_fortress_ref.png` — the skull-shaped fortress
  - `fortress_courtyard.png` — interior courtyard
  - `pirate_ship_deck.png` — Tetra's ship deck
  - `dragon_roost_island_ref.png` — Dragon Roost Island exterior
  - `dragon_roost_village_ref.png` — Rito village entrance
  - `dragon_roost_cavern_ref.png` — cavern interior with lava
  - `king_of_red_lions_sailing.png` — Link aboard the red dragon boat with sail raised
  - `king_of_red_lions_empty.png` — the dragon boat alone (establishing/empty)

These are supplementary to the official art. Generate new ones as needed for new books.

## Converting Game Assets to Our Style (`_to_process/`)

When adding new Wind Waker locations or creatures from the game:
1. Drop official artwork or game screenshots into `_to_process/`
2. Run them through Gemini with our style reference: pass the screenshot as IMAGE 2 (design) and `official/zww-link1.jpg` as IMAGE 1 (style) — the model translates the game design into our illustration style
3. Save the generated version to `characters/` or `locations/` with a clean name
4. Delete the original from `_to_process/` once the clean ref is approved

This keeps our ref library consistent in style while preserving faithful game-accurate designs.

## Books in This Series

1. **Link and the Stolen Treasure** (`projects/link_and_the_stolen_treasure/`) — Forsaken Fortress heist, fortitudo (perseverance through failure)
2. **Link and the Thief's Lantern** (`projects/link_and_the_thiefs_lantern/`) — Windfall lantern thief, iustitia/misericordia (justice tempered by mercy)
3. **Link and the Voice in the Well** (`projects/link_and_the_voice_in_the_well/`) — Outset Island well rescue, fides (trust through voice alone)
