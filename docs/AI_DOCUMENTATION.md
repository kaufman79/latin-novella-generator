# 🧠 AI Documentation: Latin Story Engine

**Version:** 1.0
**Date:** October 2025
**Prepared for:** Claude / Coding Assistant
**Author:** Ryan Kaufman
**Project Goal:** Build an intelligent content system that generates, tracks, and evolves Latin storybooks for early childhood immersion learning.

---

## 🔍 Overview

The **Latin Story Engine** is a curriculum-generation system designed to manage and produce short illustrated Latin storybooks for children.
Its purpose is to:

1. Log every Latin word introduced to the child.
2. Generate new storybook batches that intelligently *reuse* old words while introducing *new* ones.
3. Output ready-to-write story plans, vocab sheets, and printable summaries.

Each "book batch" (≈3 short stories) expands vocabulary while maintaining 75–80% reuse from earlier material.
The system should be modular, local-first, and capable of manual or AI-assisted story generation.

---

## 🧩 Core Objectives

* Maintain a **Living Lexicon Database** with full vocab lifecycle tracking.
* Generate **Batch Plans** (3 books per cycle) based on reuse rules.
* Provide **suggested themes** and **story prompts** from vocab clusters.
* Track each word's introduction, reuse, and frequency.
* Export reports and printable vocab lists.
* Optional: integrate later with LLM for story text generation.

---

## 🗂️ System Architecture

### 1. Components

| Component                  | Description                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------- |
| **Lexicon Database**       | SQLite or Google Sheets dataset storing all words, metadata, and usage.                |
| **Batch Generator**        | Core logic that selects vocab for new storybooks (based on rules).                     |
| **Story Prompt Generator** | Creates human-readable summaries of what each story could be about (based on vocab).   |
| **Exporter**               | Outputs vocab lists and story plans in Markdown or PDF format.                         |
| **GUI (optional)**         | PyQt or web dashboard for viewing vocab, generating new batches, and logging progress. |

---

## 🧮 Data Model

### Table: `lexicon`

| Column                | Type                | Description                                 |
| --------------------- | ------------------- | ------------------------------------------- |
| `id`                  | INTEGER PRIMARY KEY | Unique word ID                              |
| `latin_word`          | TEXT                | Word with macrons (e.g., *currō*)           |
| `english_gloss`       | TEXT                | Simple translation                          |
| `part_of_speech`      | TEXT                | e.g. noun / verb / adjective                |
| `semantic_field`      | TEXT                | Category: motion, emotion, nature, etc.     |
| `action_level`        | TEXT                | physical / emotional / sensory / abstract   |
| `introduced_in_batch` | INTEGER             | First batch number word appeared in         |
| `reused_in_batches`   | TEXT                | Comma-separated list of batch numbers       |
| `frequency_score`     | INTEGER             | Weighted score of usage (1–5)               |
| `morph_variants`      | TEXT                | Optional: declensions/conjugations          |
| `story_hooks`         | TEXT                | Notes on likely settings or story types     |
| `gesture_prompt`      | TEXT                | Physical motion or cue to reinforce meaning |
| `child_reaction_note` | TEXT                | Optional observational note                 |
| `print_count`         | INTEGER             | How many times word appears in printouts    |

### Table: `batches`

| Column             | Type                | Description                    |
| ------------------ | ------------------- | ------------------------------ |
| `batch_id`         | INTEGER PRIMARY KEY |                                |
| `date_created`     | TEXT                |                                |
| `new_words`        | TEXT                | Comma-separated                |
| `reused_words`     | TEXT                | Comma-separated                |
| `total_unique`     | INTEGER             |                                |
| `semantic_focus`   | TEXT                | Comma-separated                |
| `suggested_titles` | TEXT                | Optional auto-generated titles |
| `notes`            | TEXT                | Comments or overrides          |

---

## ⚙️ Batch Generation Logic

### Inputs

* Database (`lexicon.db`)
* Current batch number (e.g. 5)
* Parameters:
  * `reuse_ratio` = 0.75
  * `new_word_target` = 15–20
  * `semantic_focus` = 2–3 categories (optional override)

### Process

1. **Identify last batch used.**
2. **Select reused words:** choose ~75–80% from high-frequency pool of recent batches.
3. **Select new words:** pick 8–10 unintroduced words from unassigned pool.
4. **Balance semantic fields:** prioritize diversity or match given theme.
5. **Output combined word list** for each new book in batch.
6. **Update database:**
   * Append current batch ID to `reused_in_batches`.
   * Increment `print_count`.
   * Adjust `frequency_score` (+1).

### Output Example

```
Batch 4 Vocabulary Plan
=======================
Reuse: currō, saliō, aquam, puer, māter, laetus
New: portō, rideō, vinum, canis, fēmina, frangō

Semantic Focus: Family + Motion + Emotion
Suggested Story Ideas:
 - "Pānis Mātris" — Family dinner story
 - "Canis in Horto" — Dog causes chaos
 - "Rīdeō et Portō" — Carrying and laughing game
```

---

## 🖥️ Program Modules

### `database.py`

* CRUD functions for `lexicon` and `batches`
* Connects to SQLite
* Helper functions:
  * `get_unused_words()`
  * `get_recent_words(n_batches)`
  * `update_word_usage(word, batch_id)`
  * `get_summary_stats()`

### `generator.py`

* Implements vocab selection logic
* Functions:
  * `generate_batch(batch_num, reuse_ratio, new_word_target)`
  * `select_semantic_focus()`
  * `suggest_story_titles(vocab_list)`
  * Returns JSON or dict of batch data

### `exporter.py`

* Converts batch data → Markdown or PDF
* Optional: exports vocab CSV
* Example outputs:
  * `/exports/batch_004_vocab.md`
  * `/exports/batch_004_plan.pdf`

### `writer.py` *(optional integration)*

* Uses API (e.g. GPT or Claude) to generate simple stories from vocab lists.
* Can apply a "style guide" (simple sentences, repetitive phrasing, action emphasis).

### `ui/main_window.py` *(optional)*

* PyQt GUI for:
  * Viewing vocab table
  * Adding new words
  * Generating new batch
  * Exporting reports

---

## 🧠 Example Workflow

1. User opens app → clicks "Generate New Batch."
2. Program queries database:
   * Finds high-frequency words from last batch.
   * Picks new words from unused set.
3. System outputs:
   * Vocabulary lists per story.
   * Suggested themes/titles.
   * Markdown export.
4. User reviews output and writes/LLM-generates stories.
5. After finalizing stories, user updates the batch → database logs reuse and frequency.

---

## 📊 Metrics to Track

* Total unique words introduced
* Average reuse ratio per batch
* Frequency histogram (per part of speech)
* Reuse efficiency (how many words appear in ≥3 batches)
* Time-to-forget metric (optional via child recall notes)

---

## 🪄 Future Expansion

* **LLM Integration:** auto-generate story drafts using vocab lists and semantic hints.
* **Voice assistant mode:** read stories aloud for oral repetition.
* **Spaced Repetition Engine:** reintroduce words at strategic intervals.
* **Visualization Dashboard:** show word frequency clouds, reuse graphs.

---

## 🧰 Tech Stack Summary

| Function                  | Preferred Tool                               |
| ------------------------- | -------------------------------------------- |
| Data storage              | SQLite (local file)                          |
| Logic engine              | Python 3                                     |
| GUI                       | PyQt6                                        |
| Export                    | Markdown → PDF via `pypandoc` or `reportlab` |
| Optional story generation | OpenAI / Claude API                          |
| Optional tracking         | Google Sheets sync                           |

---

## 📁 Suggested Folder Layout

```
latin_story_engine/
│
├── data/
│   └── lexicon.db
│
├── scripts/
│   ├── database.py
│   ├── generator.py
│   ├── exporter.py
│   ├── writer.py
│   └── utils.py
│
├── ui/
│   └── main_window.py
│
├── exports/
│   └── batch_001_vocab.md
│
└── main.py
```

---

## ✅ Success Criteria

* System can:
  * Generate batch vocab plans automatically from DB.
  * Enforce reuse % logic.
  * Log reuse + print count per word.
  * Export readable reports.
* Database remains consistent and human-readable.
* (Optional) LLM story integration produces coherent toddler-level Latin text.

---

## 🧩 Generator Logic Pseudocode

```python
def generate_batch(batch_num, reuse_ratio=0.75, new_word_target=15):
    """
    Generate a new vocabulary batch with intelligent reuse.

    Args:
        batch_num: Current batch number
        reuse_ratio: Percentage of words to reuse (0.75 = 75%)
        new_word_target: Total words in batch

    Returns:
        dict: {
            'batch_id': int,
            'reused_words': list,
            'new_words': list,
            'semantic_focus': list,
            'suggested_titles': list
        }
    """

    # Calculate word counts
    reuse_count = int(new_word_target * reuse_ratio)
    new_count = new_word_target - reuse_count

    # Get candidate pools
    recent_words = get_recent_words(n_batches=3)  # Last 3 batches
    unused_words = get_unused_words()

    # Select reused words (prioritize high frequency)
    reused = select_by_frequency(recent_words, count=reuse_count)

    # Select new words (balance semantic fields)
    new = select_balanced_semantic(unused_words, count=new_count)

    # Analyze combined vocabulary
    all_words = reused + new
    semantic_focus = analyze_semantic_fields(all_words)

    # Generate story suggestions
    titles = suggest_story_titles(all_words, semantic_focus)

    return {
        'batch_id': batch_num,
        'reused_words': reused,
        'new_words': new,
        'total_unique': len(all_words),
        'semantic_focus': semantic_focus,
        'suggested_titles': titles
    }
```

---

## 🎯 Example Prompt for Claude (meta instruction)

> You are building the *Latin Story Engine*, a curriculum generator for Latin children's books.
> Use the schema and logic above to implement the Python modules.
> Begin by coding `database.py` and `generator.py`, connecting them via SQLite.
> When tested, `generator.py` should output a full batch plan dictionary (reused + new words, semantic focus, and suggested story titles).
> Ensure modularity, readability, and easy future expansion.

---
