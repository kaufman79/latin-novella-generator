# Character Consistency Improvement

## The Problem

Previously, when generating images with multiple character references, the AI had **no idea which character was which**.

### Before (Broken) ❌

**What we sent to the AI:**
```
Prompt: "Using the character styles from the reference images provided, Pater reads a book to Filia"
Reference Image 1: [image bytes]
Reference Image 2: [image bytes]
```

**Issues:**
- AI doesn't know which image is "Pater" vs "Filia"
- No character descriptions provided
- Results in random mixing of features from both references
- Inconsistent character appearances across pages

### After (Fixed) ✅

**What we now send to the AI:**
```
Prompt: "Reference 1: Pater (man with red hair and short beard, wearing blue tunic).
         Reference 2: Filia (young girl with blonde hair, wearing white dress).
         Using these character reference images for consistency, generate: Pater reads a book to Filia"
Reference Image 1: [image bytes - Pater]
Reference Image 2: [image bytes - Filia]
```

**Improvements:**
- ✅ AI knows "Reference 1 = Pater"
- ✅ AI knows "Reference 2 = Filia"
- ✅ Character descriptions reinforce visual features
- ✅ Explicit instruction to use references for consistency
- ✅ Scene description clearly names which characters appear

## How to Use

The system now automatically builds proper character prompts when:

1. **Characters are defined** in your project with:
   - `name`: Character name (e.g., "Pater", "Mater")
   - `description`: Visual description (e.g., "man with red hair and beard")
   - `reference_image_path`: Path to character reference image

2. **Pages specify characters** via the `characters` field:
   ```json
   {
     "page_number": 1,
     "latin_text": "Pater librum legit",
     "characters": ["Pater", "Filia"]
   }
   ```

The system will automatically:
- Extract character metadata (name + description)
- Build an explicit prompt naming each character reference
- Pass reference images in the correct order
- Tell the AI which characters should appear in the scene

## Code Changes

### Main Update: `scripts/image_generator.py`

Changed `generate_image()` function signature:

```python
# OLD (deprecated but still works)
generate_image(prompt, reference_image_paths=['char1.png', 'char2.png'])

# NEW (recommended)
generate_image(
    prompt,
    character_references=[
        {'name': 'Pater', 'description': 'man with red hair', 'image_path': 'char1.png'},
        {'name': 'Filia', 'description': 'girl with blonde hair', 'image_path': 'char2.png'}
    ]
)
```

### Automatic in Streamlit App

The app.py automatically uses the new method when generating images. You don't need to change anything in your workflow.

## Results

**Expected improvements:**
- 🎨 **Better character consistency** across multiple pages
- 👥 **Correct character features** from reference images
- 🎯 **Fewer regenerations needed** due to character mix-ups
- ⚡ **Clearer AI understanding** of which character is which

## Backward Compatibility

The old `reference_image_paths` parameter still works for:
- Projects without character definitions
- "Use current image" tweaking mode
- Legacy workflows

But we strongly recommend using the character reference system for all new books.
