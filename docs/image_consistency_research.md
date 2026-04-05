# Image Consistency Research

Findings from testing and research on maintaining consistent illustrations across a picture book using AI image generation (Gemini Nano Banana 2).

## Reference Image Findings

### How Gemini handles multiple reference images
- **No API parameter distinguishes ref types.** The model figures out what each image is from your prompt text.
- **Label refs explicitly in the prompt**: "Using the art style from IMAGE 1, the tower design from IMAGE 2, and maintaining character appearance from IMAGE 3..."
- **Markdown formatting helps** — Nano Banana is "extremely responsive" to structured prompts
- **Limits**: Up to 14 refs total (10 object fidelity + 4 character consistency for Flash model)
- **We typically use 4-6**: 2 style + 1 location + 1-3 characters

### What reference images CAN do
- Anchor **visual style** (colors, line weight, shading technique)
- Anchor **character identity** (what a character looks like — face, clothing, proportions)
- Anchor **location appearance** (what a building/place looks like — materials, shape)

### What reference images CANNOT do
- Maintain **scale/proportions** between objects across images (Link's size relative to a well)
- Maintain **spatial layout** (where objects are positioned in the scene)
- Guarantee **no duplication** (the model sometimes reproduces the ref AND generates it in the scene)
- Control **character orientation** (front-facing refs bias front-facing output)

## Chained vs Standard Generation (Tower Test)

Tested 10-page "Link Climbs the Tower" story with two approaches:

### Standard (location ref for every page)
- **Pros**: Bookend consistency (tower looks the same on p1 and p10), no accumulated drift
- **Cons**: Interior scenes (p3-6) were inconsistent — different stone textures, different Moblin designs
- **Best for**: Scenes that need to match a canonical look (the same well, the same fortress)

### Chained (each page refs the previous page)
- **Pros**: Consecutive same-setting scenes were more coherent (interior staircase p3-6 looked like the same place)
- **Cons**: Drift accumulated over 10 pages — tower changed from tall cylinder to squat hut by p10
- **Best for**: Sequences of 3-5 pages in the same setting

### Hybrid (recommended)
- Use **location ref** as the anchor for each setting
- Use **chaining** (previous page as ref) within consecutive pages at the same location
- **Reset to location ref** when the setting changes
- This gets the best of both: canonical look from the location ref, scene-to-scene coherence from chaining

## Prompt Engineering for Consistency

### Deduplication
The model sometimes reproduces the reference image AND generates the scene object, creating doubles (two wells, two towers). Fix:
- Explicitly state "only one well" / "single tower" in every prompt
- Say "Do not duplicate objects from the reference images"

### Scale anchoring
Without explicit size cues, the model invents proportions randomly. Fix:
- Specify relative sizes: "the well rim comes up to Link's waist"
- Use consistent language across all prompts for the same object

### Orientation/facing
The model defaults to front-facing for known characters because most training data shows them that way. Fix:
- Generate **multi-angle reference sheets** (front, side, back views)
- Pass the relevant angle's ref for each scene
- Don't try to describe "from behind" with a front-facing ref — use a back-facing ref

### The 70/30 Rule
Expect ~70% of first-batch images to be usable. Budget for 1-2 rounds of selective regeneration.
- Archive old images before regenerating (good versions might be lost)
- The cost of 2 rounds is still cheap (~$1.50/book vs $0.50)

## Alternative Approaches (researched, not yet tested)

### Midjourney
- **--cref** (character reference) is purpose-built for character consistency
- **--cw** (character weight 0-100) controls how strictly to match
- **Omni Reference (oref)** in V7 handles objects + characters + style
- $10/month, ~$0.11/final image including retries
- Best consistency tool available in 2026, but no official API

### LoRA Fine-Tuning
- Train a custom model on 15-30 character images
- 95%+ consistency across poses/backgrounds
- 50-70 hours setup per character — overkill unless doing 10+ books with same characters

### Gemini Interactions API
- Multi-turn conversation API, but does NOT maintain visual context across turns
- Each image generation is still independent
- You must explicitly pass previous images back as references
- Same pricing as single-shot — no advantage for consistency

## Sources
- [Gemini Image Generation Docs](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini 14 Reference Images Guide](https://help.apiyi.com/en/gemini-14-reference-images-object-fidelity-character-consistency-guide-en.html)
- [Consistent Characters Pipeline for 20+ Pages](https://www.musketeerstech.com/for-ai/consistent-characters-ai-childrens-books/)
- [Midjourney Character Reference](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Nano Banana Common Problems](https://www.spielcreative.com/blog/nano-banana-problems-and-fixes/)
