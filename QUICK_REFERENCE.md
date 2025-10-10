# ⚡ Quick Reference Card

## 📚 Make a Book (Copy-Paste These Commands)

```bash
# Create project
python cli.py book-new "My Book Title" --theme animal --pages 8 --level 1

# Get story planning prompt
python cli.py book-translate my_book_title -o prompts/translate.txt

# [Copy prompts/translate.txt to AI, save Latin to:]
#  projects/my_book_title/translation/latin_raw.txt

# Get pagination prompt
python cli.py book-review my_book_title -o prompts/review.txt

# [Copy to AI, save JSON to:]
#  projects/my_book_title/translation/translation.json

# Generate images (~$0.35)
python cli.py book-images my_book_title

# Build PDF
python cli.py book-pdf my_book_title

# View it!
open projects/my_book_title/latex/book.pdf
```

---

## 📝 Track a Story (Copy-Paste These Commands)

```bash
# Get vocab prompt
python cli.py prompt --auto --theme food -o prompts/story.txt

# [Write story in AI, save as stories/level_1/story_01.md]

# Track it
python cli.py ingest stories/level_1/story_01.md --level 1 --number 1 --theme food

# Check stats
python cli.py coverage
```

---

## 🔧 Setup (One Time Only)

```bash
# Install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Import vocab database
python cli.py setup

# Set API key (if not done)
echo "GEMINI_API_KEY=your_key_here" > .env
```

---

## 📂 File Locations

**For books:**
```
projects/PROJECT_ID/
├── translation/
│   ├── latin_raw.txt        ← YOU paste here (Step 2)
│   └── translation.json     ← YOU paste here (Step 3)
├── images/
│   └── page_*.png           ← AUTO generated
└── latex/
    └── book.pdf             ← FINAL BOOK ✨
```

**For stories:**
```
stories/
└── level_1/
    └── story_01.md          ← YOU save here
```

---

## 📋 All Commands

### Book Commands
```bash
book-new "Title" --theme X --pages N --level L
book-translate PROJECT_ID -o FILE
book-review PROJECT_ID -o FILE
book-images PROJECT_ID
book-pdf PROJECT_ID
book-list
book-status PROJECT_ID
```

### Story Commands
```bash
setup
prompt --auto --theme THEME -o FILE
ingest FILE --level L --number N --theme THEME
progress
list
coverage
```

---

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| "Translation file not found" | Save AI output to correct location (see File Locations above) |
| "GEMINI_API_KEY not found" | Add key to `.env` file |
| "No images found" | Run `book-images` before `book-pdf` |
| Images look different | Delete `images/reference.png` and regenerate |

---

## 💡 Quick Tips

- **Themes**: animal, family, food, nature, home
- **Pages**: 8-10 pages ideal for young children
- **Cost**: ~$0.04 per image, ~$0.35 per 8-page book
- **Art style**: Edit in `projects/PROJECT_ID/config.json`

---

## 📖 Need More Help?

- **Getting started**: [USER_GUIDE.md](USER_GUIDE.md)
- **Book workflow**: [BOOK_SYSTEM_COMPLETE.md](BOOK_SYSTEM_COMPLETE.md)
- **Story tracking**: [WORKFLOW.md](docs/WORKFLOW.md)
- **All docs**: [README.md](README.md)

---

**Print this page and keep it handy!** 📄
