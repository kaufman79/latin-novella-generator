# Character References Implementation Plan

## Overview
Replace single cover image with individual character reference sheets that can be selectively applied to each page.

## Changes Required

### 1. Update `app.py` - Step 3 Image Generation

Replace lines 666-748 (cover generation + page generation) with:

#### Step 1: Generate Character References
- Check if `json_data` has `characters` array
- For each character, generate a reference image:
  - Prompt: `{style_sheet}. {character.description}. Standing in neutral pose on plain background.`
  - Save to: `projects/{project_id}/images/char_{character_name}.png`
  - Update `project.characters` with Character objects including reference_image_path

#### Step 2: Character Selection UI (for each page)
- For pages WITHOUT images yet:
  - Show each page in an expander
  - Display: page number, Latin text, image prompt
  - Character selection: Multi-select dropdown with all character names
  - Save selection button that updates `page.characters` list

#### Step 3: Generate Page Images
- Button appears only after character selection is done
- For each page:
  - Get selected character names from `page.characters`
  - Build reference_paths list from matching character reference images
  - Generate image with multiple references (if supported) or composite prompt
  - Save to `page_{num:02d}.png`

### 2. Backwards Compatibility

Support old projects with `cover_image_prompt`:
- If `json_data` has `cover_image_prompt` but no `characters`, use old flow
- Migration path: manual or automatic conversion to character references

### 3. Image Generator Updates

May need to update `generate_image()` to support:
- Multiple reference images (if Gemini API supports)
- OR: Composite/merged reference image creation
- OR: Sequential application of references

### 4. UI Flow

```
Step 3: Generate Images
├── Section 1: Character References
│   ├── List of characters from Stage 4
│   ├── Button: "Generate Character References"
│   └── Display: Grid of generated character images
│
├── Section 2: Select Characters Per Page
│   ├── For each page (expandable):
│   │   ├── Show Latin text + image prompt
│   │   ├── Multi-select: Choose which characters appear
│   │   └── Save button
│   └── Status: X/Y pages configured
│
└── Section 3: Generate Page Images
    ├── Button: "Generate All Page Images"
    └── Progress bar with page-by-page generation
```

## Implementation Order

1. ✅ Update schemas (Character, BookPage.characters, BookProject.characters)
2. ✅ Update Stage 4 prompt and validation
3. ⏳ Update Step 3 UI in app.py
4. Update image generation logic
5. Add character regeneration UI
6. Test end-to-end flow
