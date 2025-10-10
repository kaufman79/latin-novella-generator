# 📚 Book Production System - Complete Guide

## ✅ What's Built

Your complete workflow for creating illustrated Latin children's books is now ready!

---

## 🚀 Complete Workflow

### 1. Create Book Project

```bash
python cli.py book-new "The Hungry Cat" --theme animal --pages 8 --level 1
```

**What it does:**
- Creates `projects/the_hungry_cat/` folder structure
- Initializes config.json with project settings
- Sets up subdirectories for source, translation, images, latex

**Output:**
```
✅ Created book project: the_hungry_cat
📚 PROJECT: The Hungry Cat
ID: the_hungry_cat
Status: initialized
Theme: animal
Level: 1
Target pages: 8

📋 WORKFLOW PROGRESS:
  🔄 Project created (current)
  ⬜ Story translated to Latin
  ⬜ Translation reviewed and paginated
  ⬜ Images generated
  ⬜ PDF assembled
  ⬜ Vocabulary approved and added to database

💡 Next step: python cli.py book-translate the_hungry_cat
```

---

### 2. Generate Translation Prompt

```bash
python cli.py book-translate the_hungry_cat --output prompts/story.txt
```

**What it does:**
- Loads vocabulary suggestions from database (theme-based)
- Combines with story creation guidelines
- Generates complete prompt for AI story planning

**The prompt includes:**
- Story guidelines (3-7 words/sentence, present tense, etc.)
- Suggested high-frequency vocabulary (20 words from theme)
- Instructions for planning and translating
- Space for your Latin story

**Your workflow:**
1. Open `prompts/story.txt`
2. Copy entire contents
3. Paste into Claude/ChatGPT
4. Plan your English story with AI
5. Translate to Latin following guidelines
6. Save Latin output to: `projects/the_hungry_cat/translation/latin_raw.txt`

---

### 3. Generate Review/Pagination Prompt

```bash
python cli.py book-review the_hungry_cat --output prompts/review.txt
```

**What it does:**
- Reads your Latin text from `latin_raw.txt`
- Generates prompt for AI to review, fix macrons, and paginate
- Asks AI to return structured JSON

**The prompt asks AI to:**
- Check idiomatic Latin usage
- Verify/fix macrons (ā, ē, ī, ō, ū)
- Divide into 8-12 pages (1-2 sentences per page)
- Create detailed image prompts for each page
- Generate vocabulary list with proper dictionary forms

**Your workflow:**
1. Open `prompts/review.txt`
2. Copy to AI
3. AI returns JSON with pages, image prompts, vocabulary
4. Save JSON to: `projects/the_hungry_cat/translation/translation.json`

**JSON structure:**
```json
{
  "title_latin": "Fēlēs Ēsuriēns",
  "title_english": "The Hungry Cat",
  "pages": [
    {
      "page_number": 1,
      "latin_text": "Fēlēs ēsurit.",
      "english_text": "The cat is hungry.",
      "image_prompt": "A hungry tabby cat with big eyes...",
      "vocabulary_used": ["fēlēs", "ēsuriō"]
    }
  ],
  "vocabulary_list": [
    {
      "latin": "fēlēs",
      "english": "cat",
      "part_of_speech": "noun",
      "dictionary_form": "fēlēs, fēlis, f."
    }
  ]
}
```

---

### 4. Generate Images

```bash
python cli.py book-images the_hungry_cat
```

**What it does:**
- Loads `translation.json`
- Generates reference image for character consistency
- For each page:
  - Reads image_prompt from JSON
  - Calls Gemini 2.5 Flash Image API
  - Uses reference image for consistency
  - Saves to `projects/the_hungry_cat/images/page_01.png`, etc.
- Updates JSON with image paths
- Saves generation log

**Requirements:**
- `GEMINI_API_KEY` in `.env` file (✅ already set)
- `translation.json` must exist

**Output:**
```
📷 Using existing reference image: projects/the_hungry_cat/images/reference.png

🎨 Generating 8 page images...

   Page 1/8:
   Latin: Fēlēs ēsurit.
   Generating image...
   ✅ Saved to projects/the_hungry_cat/images/page_01.png

   [... continues for all pages ...]

✅ All images generated!
   Images: 8/8

💡 Next step: python cli.py book-pdf the_hungry_cat
```

**Cost:** ~$0.039 per image × 9 images (8 pages + 1 reference) = **~$0.35 per book**

---

### 5. Build PDF

```bash
python cli.py book-pdf the_hungry_cat
```

**What it does:**
- Loads `translation.json` and images
- Generates HTML with:
  - Title page
  - Story pages (image + Latin + English)
  - Vocabulary dictionary (proper formatting)
  - Play-based activities
  - Repetition tracker
- Converts HTML to PDF using WeasyPrint
- Saves to `projects/the_hungry_cat/latex/book.pdf`

**Output:**
```
📚 Building PDF: The Hungry Cat
   Pages: 8
   Vocabulary: 12 words

📝 Generating HTML...
   HTML saved to projects/the_hungry_cat/latex/book.html
📄 Converting to PDF...
   ✅ PDF saved to projects/the_hungry_cat/latex/book.pdf

✅ PDF book complete!
   📄 projects/the_hungry_cat/latex/book.pdf

💡 Next step: python cli.py book-approve the_hungry_cat
```

**PDF includes:**
- Title page with Latin and English titles
- 8 story pages with illustrations
- Vocabulary dictionary with proper forms:
  - Nouns: `fēlēs, fēlis, f.`
  - Verbs: `ēsuriō, ēsurīre, —, —`
  - Adjectives: `magnus, magna, magnum`
- Play-based activities (retelling, physical, creative, vocabulary, real-world)
- Repetition tracker checkboxes

---

### 6. Approve and Update Database

```bash
python cli.py book-approve the_hungry_cat
```

**What it does:**
- Parses vocabulary from `translation.json`
- Shows preview of what will be added to database
- Asks for confirmation
- Updates `lexicon.db` with:
  - New words (if not already tracked)
  - Frequency scores (usage counts)
- Records book as a "story" in database
- Updates coverage statistics

**⚠️ Not yet implemented** - Still need to build this final step!

---

## 📂 Project Folder Structure

```
projects/the_hungry_cat/
├── config.json                      # Project metadata
├── status.txt                       # Current workflow status
├── source/
│   └── story_english.txt            # Original English (optional)
├── translation/
│   ├── latin_raw.txt                # Your Latin text (Step 2)
│   └── translation.json             # Paginated JSON (Step 3)
├── images/
│   ├── reference.png                # Character reference
│   ├── page_01.png                  # Page images
│   ├── page_02.png
│   ├── ...
│   └── generation_log.json          # API call log
└── latex/
    ├── book.html                    # Generated HTML
    └── book.pdf                     # Final PDF ✨
```

---

## 🎨 Art Style Configuration

Default style: `"children's book illustration, watercolor style, warm colors, simple shapes"`

**Customize per project:**
```bash
python cli.py book-new "Title" --style "digital art, vibrant colors, modern style"
```

**Or edit** `config.json` manually:
```json
{
  "image_config": {
    "art_style": "your custom style here"
  }
}
```

---

## 📊 Utility Commands

```bash
# List all book projects
python cli.py book-list

# Show detailed status
python cli.py book-status the_hungry_cat

# Check vocabulary coverage (for story tracking system)
python cli.py coverage
```

---

## 🔑 API Key Setup

Your Gemini API key is stored in `.env`:
```bash
GEMINI_API_KEY=your_api_key_here
```

The `.gitignore` file protects this from being committed.

---

## 💰 Cost Estimate

- **Gemini 2.5 Flash Image**: $0.039 per image
- **Typical 10-page book**: 11 images (10 pages + 1 reference) = **$0.43**
- **Text API calls**: Included in your story planning (separate from this system)

---

## 🎯 Example Complete Session

```bash
# 1. Create project
$ python cli.py book-new "Canis et Mūs" --theme animal --pages 10 --level 1

# 2. Get translation prompt
$ python cli.py book-translate canis_et_mus -o prompts/translate.txt

# 3. [Use prompts/translate.txt in AI chat]
#    [Save Latin to: projects/canis_et_mus/translation/latin_raw.txt]

# 4. Get review prompt
$ python cli.py book-review canis_et_mus -o prompts/review.txt

# 5. [Copy to AI, get JSON back]
#    [Save to: projects/canis_et_mus/translation/translation.json]

# 6. Generate images (~2-3 minutes)
$ python cli.py book-images canis_et_mus

# 7. Build PDF (~10 seconds)
$ python cli.py book-pdf canis_et_mus

# 8. Open and review
$ open projects/canis_et_mus/latex/book.pdf

# 9. If happy, approve (updates database)
$ python cli.py book-approve canis_et_mus
```

---

## ⚠️ Known Limitations

1. **Approval workflow not yet implemented** - Can't update database yet
2. **No image regeneration** - If you don't like an image, need to delete and regenerate all
3. **Fixed page layout** - HTML template is not customizable yet
4. **No batch operations** - Can't generate multiple books at once

---

## 🔮 Future Enhancements

- [ ] Approval workflow (database updates)
- [ ] Regenerate single page images
- [ ] Custom HTML templates
- [ ] Batch book generation
- [ ] PDF optimization (smaller file sizes)
- [ ] Image editing (crop, adjust colors)
- [ ] Multiple art styles per book (different illustrators)
- [ ] Export to EPUB format

---

## 🎉 You're Ready!

Everything is working except the final approval step. You can now:

1. Create book projects
2. Get AI prompts with vocab suggestions
3. Generate images with Gemini
4. Build professional PDFs

**Start creating your first book!**

```bash
python cli.py book-new "My First Latin Book" --theme family --pages 8 --level 1
```
