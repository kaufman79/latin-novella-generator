# 📚 Latin Book System - Quick User Guide

## ⚡ Quick Start (5 Minutes)

### First Time Setup

```bash
# 1. Create and activate virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Import vocabulary database
python cli.py setup
```

**Note:** Activate the venv each time: `source venv/bin/activate`

---

## 🌐 Streamlit Web App (RECOMMENDED)

The easiest way to create books:

```bash
# Start the app
./run_app.sh
# Or: streamlit run app.py

# Opens in browser at http://localhost:8501
```

**Workflow:**
1. **Create Project** - Fill in title, theme, pages, art style
2. **Get AI Story** - Copy prompt → paste in Claude/ChatGPT → paste JSON back
3. **Generate Book** - Click buttons to generate images and build PDF

**That's it!** The app handles all file paths and validation automatically.

---

## 📖 Make Your First Book (CLI Alternative)

### Step 1: Create Project (30 seconds)

```bash
python cli.py book-new "The Hungry Cat" --theme animal --pages 8 --level 1
```

### Step 2: Plan Your Story (5 minutes)

```bash
# Get AI prompt with vocab suggestions
python cli.py book-translate the_hungry_cat -o prompts/story.txt

# Copy prompts/story.txt → paste into Claude/ChatGPT
# Plan your English story with AI
# Translate to Latin
# Save Latin text to: projects/the_hungry_cat/translation/latin_raw.txt
```

### Step 3: Paginate & Get Image Prompts (2 minutes)

```bash
# Get review prompt
python cli.py book-review the_hungry_cat -o prompts/review.txt

# Copy to AI → get JSON back
# Save JSON to: projects/the_hungry_cat/translation/translation.json
```

### Step 4: Generate Images (2-3 minutes)

```bash
python cli.py book-images the_hungry_cat
```

**Cost:** ~$0.35 per book

### Step 5: Build PDF (10 seconds)

```bash
python cli.py book-pdf the_hungry_cat

# Open it!
open projects/the_hungry_cat/latex/book.pdf
```

---

## 🎯 The Two Workflows

### A) Quick Story Tracking (Existing)

For tracking vocabulary from simple stories:

```bash
# Get vocab prompt
python cli.py prompt --auto --theme animal

# Write story in AI

# Track it
python cli.py ingest stories/story.md --level 1 --number 1

# Check coverage
python cli.py coverage
```

### B) Full Book Production (New!)

For creating illustrated PDF books:

```bash
# Create → Translate → Review → Images → PDF
python cli.py book-new "Title" --theme X --pages 10
python cli.py book-translate project_id -o prompts/story.txt
python cli.py book-review project_id -o prompts/review.txt
python cli.py book-images project_id
python cli.py book-pdf project_id
```

---

## 📋 All Commands Reference

### Book Production

| Command | What It Does |
|---------|--------------|
| `book-new "Title" --theme X` | Create new book project |
| `book-translate project_id -o file.txt` | Generate AI prompt for story planning |
| `book-review project_id -o file.txt` | Generate AI prompt for pagination |
| `book-images project_id` | Generate images via Gemini API |
| `book-pdf project_id` | Build final PDF |
| `book-list` | List all book projects |
| `book-status project_id` | Show project status |

### Story Tracking

| Command | What It Does |
|---------|--------------|
| `setup` | Import 1,405 Latin frequency words |
| `prompt --auto --theme X` | Generate story vocab prompt |
| `ingest file.md --level 1` | Track story vocabulary |
| `list` | List all tracked stories |
| `progress` | Show what to write next |
| `coverage` | Vocabulary coverage stats |

---

## 📂 Where Files Go

```
projects/the_hungry_cat/
├── translation/
│   ├── latin_raw.txt        ← YOU paste Latin here (Step 2)
│   └── translation.json     ← YOU paste JSON here (Step 3)
├── images/
│   ├── page_01.png          ← AUTO generated (Step 4)
│   └── ...
└── latex/
    └── book.pdf             ← AUTO generated (Step 5) ✨
```

---

## 🎨 Customize Art Style

```bash
# Default style: watercolor, warm colors, simple shapes

# Custom style:
python cli.py book-new "Title" --style "digital art, vibrant colors"

# Or edit projects/project_id/config.json:
{
  "image_config": {
    "art_style": "pencil sketch, black and white, detailed"
  }
}
```

---

## ⚠️ Troubleshooting

### "GEMINI_API_KEY not found"
Check `.env` file exists with your key:
```bash
cat .env
# Should show: GEMINI_API_KEY=your_key_here
```

### "Translation file not found"
You need to save AI outputs to the right files:
- Step 2 output → `projects/PROJECT_ID/translation/latin_raw.txt`
- Step 3 output → `projects/PROJECT_ID/translation/translation.json`

### Images look inconsistent
Delete `images/reference.png` and regenerate:
```bash
rm projects/PROJECT_ID/images/reference.png
python cli.py book-images PROJECT_ID
```

### PDF missing images
Run `book-images` before `book-pdf`:
```bash
python cli.py book-images PROJECT_ID
python cli.py book-pdf PROJECT_ID
```

---

## 💡 Pro Tips

1. **Theme consistency**: Use same theme across multiple books for vocabulary building
2. **Page count**: 8-10 pages is ideal for young children
3. **Test images first**: Generate reference image only with `--reference-only` flag
4. **Save prompts**: Keep `prompts/*.txt` files for reference
5. **Reuse vocab**: Check `python cli.py coverage` to see what words to reuse

---

## 📊 What's in the PDF?

Your PDF book includes:

✅ Title page (Latin + English)
✅ Story pages (image + Latin text + English translation)
✅ Vocabulary dictionary (proper Latin forms: "puer, puerī, m.")
✅ Play-based activities (retelling, physical play, creative, vocabulary games)
✅ Repetition tracker (checkboxes for Day 1, 2, 7, 14, 30)

---

## 🎯 Example Session

```bash
# Create project
$ python cli.py book-new "Canis Parvus" --theme animal --pages 8

# Get story planning prompt
$ python cli.py book-translate canis_parvus -o prompts/story.txt

# [Use prompts/story.txt in Claude]
# [Save Latin to: projects/canis_parvus/translation/latin_raw.txt]

# Get pagination prompt
$ python cli.py book-review canis_parvus -o prompts/review.txt

# [Copy to Claude, get JSON]
# [Save to: projects/canis_parvus/translation/translation.json]

# Generate images
$ python cli.py book-images canis_parvus

# Build PDF
$ python cli.py book-pdf canis_parvus

# Done!
$ open projects/canis_parvus/latex/book.pdf
```

---

## 💰 Costs

- **Gemini 2.5 Flash Image**: $0.039 per image
- **8-page book**: 9 images = **$0.35**
- **10-page book**: 11 images = **$0.43**

Text generation (your AI chats) is separate.

---

## 🆘 Need Help?

- **Full docs**: See `BOOK_SYSTEM_COMPLETE.md`
- **Workflow design**: See `BOOK_WORKFLOW_DESIGN.md`
- **All commands**: Run `python cli.py --help`
- **Book commands**: Run `python cli.py book-new --help`

---

**Ready to create your first Latin book!** 🏛️✨
