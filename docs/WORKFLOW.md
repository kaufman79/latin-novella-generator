# 📝 Complete Workflow Guide

This guide shows the complete workflow for creating Latin stories with the tracking system.

## 🎯 Overview

The system uses a **tracking-first, leveled approach**:

1. **Generate vocabulary suggestions** for your next story
2. **Create story with AI** using the suggested vocabulary
3. **Ingest story** to track vocabulary usage and assign level
4. **Check dashboard** to see coverage and plan next story
5. **Repeat** with progressive difficulty levels

---

## 🚀 Step-by-Step Workflow

### Step 1: Check Your Progress

See what level/story you should write next:

```bash
python scripts/list_stories.py --progression
```

**Example output:**
```
📈 STORY PROGRESSION

Level 1:
  Stories completed: 1
  Cumulative vocabulary: ~14 words
  Average unique words per story: 14

💡 NEXT: Write Level 1, Story 2
   Goal: Basic vocabulary (animals, family, actions)
   Progress: 1/10 stories
   Target vocab: ~50 cumulative words
```

---

### Step 2: Generate Vocabulary Suggestions

Get a list of words to use in your next story:

```bash
# Basic usage (5 new words, 10 reuse words)
python scripts/suggest_vocabulary.py --new 5 --reuse 10

# With a theme
python scripts/suggest_vocabulary.py --new 8 --reuse 5 --theme animal

# For a specific level
python scripts/suggest_vocabulary.py --new 5 --reuse 10 --level 1

# Save to file for easy copy/paste
python scripts/suggest_vocabulary.py --new 5 --reuse 10 -o prompts/story_2_vocab.txt
```

**Example output:**
```
======================================================================
📖 LATIN STORY PROMPT
======================================================================

## 🆕 NEW VOCABULARY (introduce these words)

| Latin | English | Part of Speech | Priority |
|-------|---------|----------------|----------|
| quī | who, which, what | Pronoun | core |
| que | and (postpositive) | Conjunction | core |
| porcus | pig | noun | ff625 |
| nōn | no | adverb | core |
| mūs | mouse | noun | ff625 |

**Goal:** Use each new word 8-12 times in the story.

## 🔄 REUSE VOCABULARY (reinforce these words)

| Latin | English | Part of Speech | Previous Uses |
|-------|---------|----------------|---------------|
| puer | boy | noun | 5 |
| canis | dog | noun | 5 |
| currō | run | Verb | 3 |
...
```

---

### Step 3: Create Story with AI

1. **Copy the vocabulary prompt** from Step 2
2. **Open Claude/ChatGPT**
3. **Paste the system prompt** from [stories/README.md](../stories/README.md)
4. **Paste the vocabulary list** and ask for a story:

```
Use the vocabulary above to write a Latin story for Level 1, Story 2.
Theme: A boy and a pig playing in the forest.
```

5. **Save the story** as `stories/level_1/story_02_puer_et_porcus.md`

**AI will generate:**
- Latin text with repetition
- English translation
- Vocabulary table
- Teaching notes
- Play-based extensions (from template)

---

### Step 4: Ingest the Story

Track the vocabulary and record metadata:

```bash
python scripts/ingest_story.py stories/level_1/story_02_puer_et_porcus.md \
  --level 1 \
  --number 2 \
  --theme animals
```

**Output shows:**
- Total words and unique forms
- Matched words in database
- Coverage by frequency tier
- New words not in database
- Story recorded as "Level 1, Story 2"

---

### Step 5: Check Coverage Dashboard

See overall vocabulary usage:

```bash
python scripts/coverage_dashboard.py
```

**Analyze:**
- Story coverage percentage (goal: increase over time)
- FF625 coverage (goal: 100% eventually)
- DCC Core coverage by tier
- Unused high-frequency words
- Vocabulary clusters with gaps

**Use this to plan themes for next stories!**

---

### Step 6: View Story Library

See all your stories organized by level:

```bash
python scripts/list_stories.py
```

**Shows:**
- All stories by level and number
- Words per story (unique/total)
- Theme tags
- Read counts
- File paths

---

## 📊 Level Guidelines

| Level | Target Stories | Cumulative Vocab | Focus |
|-------|---------------|------------------|-------|
| **1** | 10 stories | ~50 words | Basic vocabulary (animals, family, simple actions) |
| **2** | 10 stories | ~100 words | Common verbs and adjectives, expand to everyday situations |
| **3** | 15 stories | ~200 words | More complex sentences, introduce conjunctions |
| **4** | 15 stories | ~300 words | Past tense introduction, narrative stories |
| **5+** | 15-20 stories | 400+ words | Increase complexity gradually |

---

## 🎨 Quick Reference Commands

### Planning
```bash
# What's next?
python scripts/list_stories.py --progression

# What themes are available?
python scripts/suggest_vocabulary.py --list-themes
```

### Story Creation
```bash
# Get vocabulary for next story
python scripts/suggest_vocabulary.py --new 5 --reuse 10 --theme food

# Ingest completed story
python scripts/ingest_story.py stories/level_1/story_03.md --level 1 --number 3 --theme food
```

### Tracking
```bash
# See all stories
python scripts/list_stories.py

# Check vocabulary coverage
python scripts/coverage_dashboard.py
```

---

## 💡 Tips for Success

### 1. **Follow the 95% Rule**
- Each story should be ~95% reuse words, ~5% new words
- Use `suggest_vocabulary.py` to get balanced suggestions
- Example: 15 total words = 10 reuse + 5 new

### 2. **Stick to Levels**
- Complete all stories in a level before moving to the next
- Use `--progression` to track your progress
- Level progression ensures gradual difficulty increase

### 3. **Use Themes**
- Group stories by theme (animals, family, food, etc.)
- This naturally creates semantic clusters
- Makes vocabulary more memorable for children

### 4. **Track Everything**
- Always ingest stories with `--level` and `--number` flags
- Use `--theme` to categorize stories
- This enables progression tracking and recommendations

### 5. **Check Dashboard Regularly**
- Run coverage dashboard after every 3-5 stories
- Identify gaps in high-frequency vocabulary
- Plan themed stories to fill those gaps

### 6. **Repetition is Key**
- Aim for 8-12 uses of each new word per story
- Reuse words from previous stories 2-5 times each
- Use play-based extensions to reinforce learning

---

## 🔄 Example Full Cycle

Here's a complete example from start to finish:

```bash
# 1. Check progress
$ python scripts/list_stories.py --progression
# Output: "NEXT: Write Level 1, Story 2"

# 2. Generate vocabulary
$ python scripts/suggest_vocabulary.py --new 5 --reuse 10 --theme animal -o prompts/l1_s2.txt
# Output: Vocabulary prompt saved to prompts/l1_s2.txt

# 3. Create story with AI
# - Open Claude/ChatGPT
# - Paste stories/README.md system prompt
# - Paste vocabulary from prompts/l1_s2.txt
# - Ask: "Write Level 1, Story 2 about a boy and pig"
# - Save as stories/level_1/story_02_puer_et_porcus.md

# 4. Ingest story
$ python scripts/ingest_story.py stories/level_1/story_02_puer_et_porcus.md \
  --level 1 --number 2 --theme animals
# Output: "✅ Story ingestion complete! 📚 Recorded as Level 1, Story 2"

# 5. Check coverage
$ python scripts/coverage_dashboard.py
# Output: Coverage increased, see unused words for next story

# 6. Repeat!
```

---

## 📁 Recommended File Structure

Organize stories by level:

```
stories/
├── level_1/
│   ├── story_01_puer_et_canis.md
│   ├── story_02_puer_et_porcus.md
│   ├── story_03_feles_et_mus.md
│   └── ...
├── level_2/
│   ├── story_01_familia_laeta.md
│   └── ...
└── prompts/
    ├── l1_s2_vocab.txt
    ├── l1_s3_vocab.txt
    └── ...
```

---

## 🎯 Goals

### Short-term (Level 1)
- [ ] Complete 10 stories
- [ ] Introduce ~50 core words
- [ ] Focus on: animals, family, basic actions
- [ ] Establish reading routine with child

### Medium-term (Levels 2-3)
- [ ] Complete 25 total stories
- [ ] Cover 80% of FF625 list
- [ ] Cover 100% of DCC Core (top 100)
- [ ] Introduce past tense

### Long-term (Levels 4-5+)
- [ ] 50+ total stories
- [ ] 100% FF625 coverage
- [ ] 80%+ DCC Core coverage (all tiers)
- [ ] Begin reading classical texts with support

---

## 📚 Additional Resources

- [README.md](../README.md) - Full system documentation
- [stories/README.md](../stories/README.md) - AI story generation prompt
- [COVERAGE_DASHBOARD.md](COVERAGE_DASHBOARD.md) - Dashboard guide
- [PEDAGOGY.md](PEDAGOGY.md) - Research and methodology

---

**Happy story writing!** 🏛️
