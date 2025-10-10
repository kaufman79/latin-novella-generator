# 🚀 Quick Start Guide

Get started creating Latin stories in 5 minutes.

## Prerequisites

```bash
# Install CLTK (Latin lemmatization)
pip install cltk[stanza]
```

## Setup (One-Time)

```bash
# 1. Import frequency lists (1,405 high-frequency Latin words)
python scripts/import_frequency_lists.py
1
# This imports:
# - Fluent Forever 625 (modern/conversational Latin)
# - DCC Latin Core (997 classical Latin words)
```

## Create Your First Story

### 1. Get Vocabulary Suggestions

```bash
python scripts/suggest_vocabulary.py --new 5 --reuse 0 --theme animal
```

**Output:** A formatted vocabulary list with 5 animal-related words.

### 2. Generate Story with AI

1. Open Claude or ChatGPT
2. Copy the system prompt from stories/README.md
3. Paste the vocabulary list from Step 1
4. Ask: "Write a Latin story using these words"
5. Save the result as `stories/level_1/story_01.md`

**The AI will create:**
- Simple Latin sentences (3-7 words each)
- English translation
- Vocabulary table
- Teaching notes
- Play-based activity suggestions

### 3. Track the Story

```bash
python scripts/ingest_story.py stories/level_1/story_01.md \
  --level 1 \
  --number 1 \
  --theme animals
```

**Output:** Shows which words matched the database and tracks usage.

### 4. Check Your Progress

```bash
# View all stories
python scripts/list_stories.py

# Check vocabulary coverage
python scripts/coverage_dashboard.py

# See what to write next
python scripts/list_stories.py --progression
```

## Create Your Second Story

### 1. Generate Vocabulary (with reuse!)

```bash
# Now include 10 reuse words from Story 1
python scripts/suggest_vocabulary.py --new 5 --reuse 10 --theme food
```

**Key difference:** The `--reuse 10` flag includes words from your previous story for reinforcement.

### 2. Repeat Steps 2-4

Same process as Story 1, but now you're building on previous vocabulary!

## Key Commands Reference

```bash
# Get vocabulary for AI prompt
python scripts/suggest_vocabulary.py --new 5 --reuse 10

# Ingest story and track progress
python scripts/ingest_story.py <file> --level 1 --number 2

# View story library
python scripts/list_stories.py

# Check coverage
python scripts/coverage_dashboard.py

# See progression
python scripts/list_stories.py --progression
```

## Example Complete Workflow

```bash
# Check what to write next
$ python scripts/list_stories.py --progression
# → "NEXT: Write Level 1, Story 2"

# Get vocabulary
$ python scripts/suggest_vocabulary.py --new 5 --reuse 10

# [Create story with AI using the vocabulary]

# Track the story
$ python scripts/ingest_story.py stories/level_1/story_02.md \
  --level 1 --number 2 --theme family

# Check progress
$ python scripts/coverage_dashboard.py
```

## Level Guidelines

| Level | Stories | Focus |
|-------|---------|-------|
| **1** | 10 | Animals, family, basic actions (~50 words) |
| **2** | 10 | Common verbs, adjectives (~100 words) |
| **3** | 15 | Everyday situations, conjunctions (~200 words) |
| **4** | 15 | Past tense introduction (~300 words) |
| **5+** | 15-20 | Gradual complexity increase |

## Tips

1. **Start with Level 1** — Build a strong foundation
2. **Use themes** — Group stories by topic (animals, family, food)
3. **Follow 95% rule** — Mostly reuse words (10) + few new words (5)
4. **Check dashboard often** — Every 3-5 stories, check coverage
5. **Use play extensions** — Act out stories with your child

## Next Steps

- Read the Complete Workflow Guide (WORKFLOW.md)
- Check the AI Story Generation Prompt (stories/README.md)
- Review the Coverage Dashboard Guide (COVERAGE_DASHBOARD.md)
- See Pedagogy Documentation (PEDAGOGY.md) for methodology

---

**You're ready! Start creating your first story.** 🏛️
