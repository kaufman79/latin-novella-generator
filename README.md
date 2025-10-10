# 🏛️ Latin Story Engine

**Create illustrated Latin children's books with AI-powered image generation and intelligent vocabulary tracking.**

---

## 📖 Two Complete Systems

### 📚 Book Production System (NEW!)

Create professional illustrated PDF books:
- 🎨 **AI image generation** via Gemini 2.5 Flash Image
- 📄 **PDF assembly** with images, Latin text, vocabulary dictionary
- 🎭 **Play-based activities** built into every book
- 💰 **~$0.35 per 8-page book**

### 📝 Story Tracking System

Track vocabulary from simple Latin stories:
- 📊 **1,405 high-frequency Latin words** (FF625 + DCC Core)
- 🔄 **Lemmatization** handles inflected forms automatically
- 📈 **Coverage dashboard** shows vocabulary progress
- 🎯 **Progressive levels** guide story creation

---

## ⚡ Quick Start

**READ THIS FIRST:** [USER_GUIDE.md](USER_GUIDE.md) - 5-minute getting started guide

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Import vocabulary database (one-time setup)
python cli.py setup
```

### Make Your First Book (5 minutes) - Streamlit App

**Easiest method:**

```bash
# Start the web app
./run_app.sh

# Opens in browser at http://localhost:8501
```

Then:
1. Fill in book details (title, theme, pages)
2. Copy prompt → paste in Claude/ChatGPT → paste JSON back
3. Click "Generate Images" → Click "Build PDF" → Download!

**Cost:** ~$0.35 per 8-page book

### Alternative: CLI Workflow

```bash
# 1. Create project
python cli.py book-new "The Hungry Cat" --theme animal --pages 8

# 2. Get AI prompt for story planning
python cli.py book-translate the_hungry_cat -o prompts/story.txt

# 3. [Use prompts/story.txt in Claude/ChatGPT to plan & translate story]
#    [Save Latin to: projects/the_hungry_cat/translation/latin_raw.txt]

# 4. Get pagination/image prompt
python cli.py book-review the_hungry_cat -o prompts/review.txt

# 5. [Copy to AI, save JSON to: projects/the_hungry_cat/translation/translation.json]

# 6. Generate images (~$0.35)
python cli.py book-images the_hungry_cat

# 7. Build PDF
python cli.py book-pdf the_hungry_cat

# 8. Open your book!
open projects/the_hungry_cat/book.pdf
```

**Full workflow:** See [USER_GUIDE.md](USER_GUIDE.md)

---

## 📋 Command Reference

### Book Production

```bash
python cli.py book-new "Title" --theme animal --pages 8 --level 1
python cli.py book-translate project_id -o prompts/story.txt
python cli.py book-review project_id -o prompts/review.txt
python cli.py book-images project_id
python cli.py book-pdf project_id
python cli.py book-list
python cli.py book-status project_id
```

### Story Tracking

```bash
python cli.py setup                              # One-time database setup
python cli.py prompt --auto --theme animal       # Generate story vocab prompt
python cli.py ingest stories/story.md --level 1  # Track vocabulary
python cli.py progress                           # What to write next
python cli.py coverage                           # Vocabulary stats
python cli.py list                               # List all stories
```

---

## 📚 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Quick start guide (READ THIS FIRST!)
- **[BOOK_SYSTEM_COMPLETE.md](BOOK_SYSTEM_COMPLETE.md)** - Complete book workflow documentation
- **[BOOK_WORKFLOW_DESIGN.md](BOOK_WORKFLOW_DESIGN.md)** - Technical design details
- **[WORKFLOW.md](docs/WORKFLOW.md)** - Story tracking workflow
- **[COVERAGE_DASHBOARD.md](docs/COVERAGE_DASHBOARD.md)** - Dashboard guide
- **[PEDAGOGY.md](docs/PEDAGOGY.md)** - Research & methodology

---

## 🏗️ Project Structure

### 1. **Add Vocabulary**

**Option A: Import frequency lists (recommended)**
```bash
# Import Fluent Forever 625 + DCC Latin Core (1,405 words total)
python scripts/import_frequency_lists.py
```

This imports two curated vocabulary lists:
- **Fluent Forever 625**: High-frequency modern/conversational Latin words
- **DCC Latin Core**: 997 classical Latin words from authentic texts

**Option B: Use seed data**
```bash
python scripts/seed_data.py
```

**Option C: Add words manually**
```bash
python main.py add
```

**Option D: Programmatically**
```python
from scripts.database import LatinDatabase

db = LatinDatabase('data/lexicon.db')
db.add_word(
    latin_word='currō',
    english_gloss='run',
    part_of_speech='verb',
    semantic_field='motion',
    action_level='physical',
    gesture_prompt='Running motion with arms',
    story_hooks='Chase scenes, races, escaping'
)
db.close()
```

---

### 2. **Write Stories (Tracking-First Approach)**

The system uses a **tracking-first approach**: write stories naturally using vocabulary you choose, then let the system track what you've used.

#### Option A: Integrated CLI (Recommended)

The easiest way to create stories:

```bash
# 1. Generate complete AI prompt (auto-detects next level/story)
python cli.py prompt --auto --theme animal --output prompts/story.txt

# 2. Copy prompts/story.txt and paste into Claude/ChatGPT

# 3. Save generated story, then ingest it
python cli.py ingest stories/level_1/story_02.md --level 1 --number 2 --theme animal

# 4. Check progress
python cli.py progress
```

**The CLI combines:**
- Vocabulary suggestions (new + reuse words)
- AI system prompt from [stories/README.md](stories/README.md)
- Story metadata (level, number, theme)
- Everything ready to copy/paste!

#### Option B: Manual Scripts

If you prefer more control:

```bash
# Generate vocabulary suggestions
python scripts/suggest_vocabulary.py --new 5 --reuse 10 --theme animal

# [Copy vocab + stories/README.md prompt to AI]

# Ingest completed story
python scripts/ingest_story.py stories/your_story.md --level 1 --number 1 --theme animal
```

**Output example:**
```
📖 Story: "Puer et Canis"
==================================================
Total words (with repetition): 23
Unique word forms: 14
Matched in database: 13/14 (92.9%)

Coverage by source:
  FF625: 1 words
  DCC Core: 12 words

Coverage by frequency tier:
  supplemental: 4 words
  core: 4 words
  common: 3 words
  ff625: 1 words
```

---

### 3. **Check Progress & Coverage**

Use the integrated CLI:

```bash
# Check what to write next
python cli.py progress

# View all stories
python cli.py list

# Check vocabulary coverage
python cli.py coverage
```

**The dashboard shows:**
- 📊 Overall vocabulary statistics (total words, frequency tiers)
- 📖 Story coverage (% of vocabulary used)
- ⭐ Most frequently used words in stories
- 🎯 Top unused high-frequency words
- 🔤 Vocabulary clusters (semantic groups with unused words)
- 💡 Suggested vocabulary for next story

---

### 4. **Generate a Batch (Legacy Approach)**

*Note: The tracking-first approach (above) is now recommended. The batch generation system is kept for reference.*

```bash
python main.py generate
```

**You'll be prompted for:**
- Total words per batch (default: 15)
- Reuse ratio (default: 0.75 = 75% reused, 25% new)
- Semantic focus (optional: e.g., "motion,family,emotion")
- Notes (optional)

**Output example:**
```
Batch 1 Vocabulary Plan
==================================================

**Reuse:** currō, saliō, puer, māter
**New:** canis, rīdeō, aqua

**Total Unique Words:** 11
**Reuse Percentage:** 63.6%

**Semantic Focus:** motion, family, animals

**Suggested Story Ideas:**
 1. Puer in Motion
 2. The Happy Dog
 3. Currō Rīdeō
 4. Chase scenes, races, escaping
 5. A Story About Motion

✅ Batch 1 saved to database
```

---

### 3. **Export Materials**

After generating a batch, you'll be prompted:
```
Export batch files? (y/n) [y]: y

✅ Files exported:
  plan         → exports/batch_001_plan.md
  vocab        → exports/batch_001_vocab.md
  csv          → exports/batch_001_vocab.csv
  flashcards   → exports/batch_001_flashcards.md
```

**Exported files include:**
- **Batch plan** — vocabulary lists + story development template
- **Vocab reference** — detailed table with translations, gestures, semantic fields
- **CSV export** — import into spreadsheets
- **Flashcards** — printable study cards

---

### 4. **Write Stories**

Use the exported Markdown files as templates:

**Example from `exports/batch_001_plan.md`:**
```markdown
## ✍️ Story Development Notes

### Story 1: "Puer Currō"

[Write your simple Latin story here using only the vocabulary above]
```

**Pedagogical goals:**
- Use ONLY vocabulary from the batch
- Keep sentences simple and repetitive
- Focus on action verbs and concrete nouns
- Aim for 3-5 sentences per story

---

## 🗂️ Project Structure

```
Latin_book_system/
│
├── data/
│   ├── lexicon.db              # SQLite database (auto-created)
│   └── frequency_lists/        # Source vocabulary lists
│       ├── fluent_forever_625_latin.csv
│       └── dcc_latin_core.csv
│
├── scripts/
│   ├── database.py             # Database CRUD operations
│   ├── generator.py            # Batch generation logic
│   ├── exporter.py             # Export to Markdown/CSV
│   ├── seed_data.py            # Sample vocabulary loader
│   ├── lemmatizer.py           # Latin lemmatization using CLTK
│   ├── import_frequency_lists.py  # Import FF625 + DCC Core
│   ├── suggest_vocabulary.py   # Generate vocabulary lists for AI prompts
│   ├── ingest_story.py         # Extract and track story vocabulary
│   ├── list_stories.py         # View stories by level with progression
│   ├── coverage_dashboard.py   # Vocabulary usage statistics
│   └── __init__.py
│
├── stories/                    # Latin stories with vocabulary
│   ├── README.md               # AI prompt for story generation
│   └── test_story.md           # Example story
│
├── exports/                    # Generated batch files
│   ├── batch_001_plan.md
│   ├── batch_001_vocab.md
│   └── ...
│
├── docs/
│   ├── AI_DOCUMENTATION.md     # Full system specification
│   ├── PEDAGOGY.md             # Research + algorithm rationale
│   └── ROADMAP.md              # Future improvements
│
├── main.py                     # CLI entry point
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

---

## 🧮 Database Schema

### `lexicon` Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Unique word ID |
| `latin_word` | TEXT | Word with macrons (e.g., *currō*) |
| `english_gloss` | TEXT | Simple translation |
| `part_of_speech` | TEXT | noun / verb / adjective / adverb |
| `semantic_field` | TEXT | motion / emotion / family / nature / etc. |
| `action_level` | TEXT | physical / emotional / sensory / abstract |
| `introduced_in_batch` | INTEGER | First batch number |
| `reused_in_batches` | TEXT | Comma-separated batch IDs |
| `frequency_score` | INTEGER | Usage count in stories |
| `print_count` | INTEGER | Number of printouts |
| `gesture_prompt` | TEXT | Physical cue for reinforcement |
| `story_hooks` | TEXT | Suggested story contexts |
| `morph_variants` | TEXT | Declensions/conjugations |
| `child_reaction_note` | TEXT | Observational notes |
| `ff625_rank` | INTEGER | Rank in Fluent Forever 625 list |
| `ff625_category` | TEXT | FF625 category (Verbs, Animals, etc.) |
| `dcc_rank` | INTEGER | Rank in DCC Latin Core list |
| `dcc_semantic_group` | TEXT | DCC semantic group |
| `frequency_tier` | TEXT | Tier: ff625, core, common, supplemental |

### `batches` Table

| Column | Type | Description |
|--------|------|-------------|
| `batch_id` | INTEGER | Unique batch ID |
| `date_created` | TEXT | ISO timestamp |
| `new_words` | TEXT | Comma-separated new words |
| `reused_words` | TEXT | Comma-separated reused words |
| `total_unique` | INTEGER | Total words in batch |
| `semantic_focus` | TEXT | Dominant semantic fields |
| `suggested_titles` | TEXT | Auto-generated story ideas |
| `notes` | TEXT | User comments |

---

## ⚙️ How the Algorithm Works

### Batch Generation Process

1. **Calculate word distribution**
   - Default: 75% reused, 25% new
   - Example: 15-word batch = 11 reused + 4 new

2. **Select reused words**
   - Query recent batches (last 3 by default)
   - Score by `frequency_score * 2 + print_count`
   - Take top 60% guaranteed, remaining 40% randomized
   - **Goal:** Reinforce high-frequency vocabulary

3. **Select new words**
   - Query unused words from database
   - Balance semantic fields (avoid over-concentration)
   - Prioritize diversity unless semantic focus specified
   - **Goal:** Gradual, balanced expansion

4. **Analyze & suggest**
   - Identify dominant semantic fields
   - Generate 5 story title ideas using templates
   - Combine nouns, verbs, adjectives creatively

5. **Update database**
   - Save batch record
   - Increment word usage stats
   - Track reuse history

### Current Limitations

⚠️ **Areas for improvement** (see [PEDAGOGY.md](docs/PEDAGOGY.md) and [ROADMAP.md](docs/ROADMAP.md)):

- **No temporal spacing** — doesn't track days between exposures (optimal: 1, 7, 14, 30 days)
- **No frequency ranking** — treats all words equally (should prioritize most common 100-500 words)
- **Fixed reuse ratio** — doesn't adapt based on child performance
- **No story-target mode** — can't work backward from a specific book
- **Basic semantic balancing** — doesn't account for syntactic roles (needs verbs + nouns, not just nouns)

---

## 🎓 Pedagogical Foundation

This system is inspired by research in:

- **Spaced Repetition** (Ebbinghaus, Wozniak) — optimal review intervals
- **Zipf's Law** — high-frequency words provide maximum communicative power
- **Comprehensible Input (Krashen)** — i+1 theory (95-98% comprehensible material)
- **Task-Based Language Teaching** — learning toward meaningful goals

**Key insight:** A child learning 100 high-frequency Latin words gains more communicative ability than learning 1000 random words.

See [docs/PEDAGOGY.md](docs/PEDAGOGY.md) for full research summary.

---

## 🧪 CLI Command Reference

### List Commands

```bash
# List all words in database
python main.py list

# List only unused words
python main.py list --unused
```

### Add Words

```bash
# Interactive word entry
python main.py add
```

### Statistics

```bash
# View database statistics (legacy)
python main.py stats

# View comprehensive coverage dashboard (recommended)
python scripts/coverage_dashboard.py
```

### Generate Batch

```bash
# Interactive batch generation
python main.py generate
```

### View Batches

```bash
# List all generated batches
python main.py batches
```

### Interactive Mode

```bash
# Launch full menu interface
python main.py interactive
```

---

## 🔮 Future Features

**Completed:**
- ✅ **Frequency ranking** — FF625 + DCC Latin Core imported (1,405 words)
- ✅ **Lemmatization integration** — CLTK handles inflected forms
- ✅ **Story ingestion** — track vocabulary usage from written stories
- ✅ **Coverage dashboard** — visualize vocabulary usage statistics

**High Priority:**
- ⏰ **Temporal spacing** — enforce 7/14/30-day review intervals
- 🎯 **Story-target mode** — generate batches to reach a specific book

**Medium Priority:**
- 🤖 **AI story generation** — auto-write stories from vocab lists
- 📈 **Adaptive difficulty** — adjust reuse ratio based on child recall
- 🔊 **Audio pronunciation** — integrate with TTS for listening practice
- 📱 **Web dashboard** — visual interface for batch management

**Long Term:**
- 🧠 **Forgetting curve tracking** — predict when words need review
- 👥 **Multi-child support** — track progress for multiple learners
- 🌍 **Cloud sync** — backup database to Google Sheets
- 📖 **Story library** — share completed stories with other users

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed implementation plan.

---

## 🛠️ Development

### Running Tests

```bash
# (Tests not yet implemented)
pytest tests/
```

### Database Management

```bash
# View database directly
sqlite3 data/lexicon.db

# Useful queries:
SELECT * FROM lexicon LIMIT 10;
SELECT * FROM batches;
SELECT COUNT(*) FROM lexicon WHERE introduced_in_batch IS NULL;
```

### Backup Database

```bash
cp data/lexicon.db data/lexicon_backup_$(date +%Y%m%d).db
```

---

## 🤝 Contributing

This is a personal project for early childhood Latin education. Contributions welcome for:

- Additional seed vocabulary
- Pedagogical algorithm improvements
- Story templates and examples
- Lemmatization and morphology improvements
- Test coverage

---

## 📄 License

MIT License — free for personal and educational use.

---

## 🙏 Acknowledgments

- Inspired by Stephen Krashen's comprehensible input theory
- Spaced repetition algorithms from Anki/SuperMemo research
- Latin frequency data from Dickinson College Commentaries
- Built for a real parent teaching Latin to their toddler

---

## 📞 Support

For questions or issues:
- See [docs/AI_DOCUMENTATION.md](docs/AI_DOCUMENTATION.md) for full system spec
- See [docs/PEDAGOGY.md](docs/PEDAGOGY.md) for research background
- See [docs/ROADMAP.md](docs/ROADMAP.md) for planned improvements

---

**Happy Latin learning! Bonam fortunam!** 🏛️
