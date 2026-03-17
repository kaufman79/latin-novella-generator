# Latin Children's Book System

A tool for creating illustrated Latin children's books using Claude Code agents and AI image generation.

## Project Overview

This system creates picture books in Latin for a toddler (~3.5 years old) learning Latin as a living language. His father speaks Latin to him daily; his comprehension is roughly at a 1-year-old level but growing. Books are 15-30 pages, with simple Latin text (3-7 words per sentence) and full-page illustrations.

These are real children's books, not language textbooks. No vocab lists, no grammar drills. The pictures do a lot of the heavy lifting for comprehension — a child who doesn't fully understand the Latin should be able to follow the story through the illustrations.

## Workflow

The book creation pipeline has review gates between each stage. **All gates are iterative** — the user gives feedback, you edit the existing draft. Never start from scratch unless explicitly asked.

### 1. Story Planning → `@story-architect`
- Interactive back-and-forth to develop a story concept
- Output: `projects/{id}/source/outline.json`
- **REVIEW GATE**: User approves story before proceeding

### 2. Latin Translation → `@latin-scribe`
- Translates the English outline into natural Latin
- Output: `projects/{id}/translation/translation.json`

### 3. Latin Review → `@latin-censor`
- Reviews Latin for grammar, macrons, naturalness
- Updates translation in place, writes review to `projects/{id}/translation/review.md`
- **REVIEW GATE**: User approves Latin before proceeding

### 4. Art Direction → `@art-director`
- Creates Visual Bible and per-page image prompts
- Output: `projects/{id}/art/visual_bible.json` and `projects/{id}/art/prompts.json`
- **REVIEW GATE**: User approves art direction before image generation (this is where $$ gets spent)

### 5. Image Generation
```bash
python scripts/image_generator.py {project_id}
python scripts/image_generator.py {project_id} --pages 3 7 12   # regenerate specific pages
```
- Generates images using OpenAI API (`gpt-image-1`)
- **REVIEW GATE**: User reviews images, can regenerate individual pages

### 6. PDF Assembly
```bash
python scripts/pdf_builder.py {project_id}
```
- Assembles final PDF in `projects/{id}/output/book.pdf`

## Latin Guidelines

- **Living language, not academic.** Write Latin like you'd find in a children's picture book — simple, clear, natural. Not textbook prose, not literary/archaic.
- **Don't shelter grammar.** Let tense, case, and construction come naturally from the story. Simple past (perfect) is fine for narratives. Don't artificially restrict to present tense or nominative case.
- **Macrons on long vowels.** Mark all long vowels. Wrong macrons are worse than missing ones — if unsure, leave unmarked.
- **Minor latinity compromises are OK.** Perfection isn't the goal, natural readability is. Some English influence in word order is tolerable.
- **Modern concepts.** When Latin lacks a clean equivalent, paraphrase or borrow. There are reference Latin picture books in `existing_stories/` that handle modern vocabulary well.
- **Sentences: 3-7 words.** This is a picture book for a toddler. Keep it short.
- **Repetition is good.** Repeated phrases across pages help language learning naturally.

## Image Consistency Strategy

The Visual Bible approach: every image prompt is fully self-contained with identical style and character descriptions. Consistency comes from repeating the same text descriptions, not from reference images (which APIs handle poorly).

- **Established characters** (Toon Link, Mario, etc.) are a huge consistency win — the image model already knows them. Text prompt alone produces more consistent results than any reference image system.
- **Original characters** need extremely specific visual descriptions: exact colors, proportions, clothing, features. The more specific, the more consistent.
- **Every prompt** = [STYLE block] + [CHARACTER descriptions] + [LOCATION] + [SCENE]. Style and character blocks are identical across all pages.

## Secondary Pipeline: Translate Existing Books

For translating English kids' books into Latin:
1. Scan/photograph the pages
2. Extract or transcribe the English text
3. Use `@latin-scribe` to translate to Latin
4. Keep the original illustrations
5. Assemble new PDF with Latin text + original images

## Project Structure

```
projects/{project_id}/
├── config.json              # Project metadata
├── source/
│   └── outline.json         # English story outline
├── translation/
│   ├── translation.json     # Latin text + English
│   └── review.md            # Latin review notes
├── art/
│   ├── visual_bible.json    # Style guide, character sheets, locations
│   └── prompts.json         # Per-page image prompts (self-contained)
├── images/
│   └── page_*.png           # Generated page images
└── output/
    ├── book.html
    └── book.pdf
```

## Creating a New Project

```bash
python scripts/project_manager.py create "My Book Title"
python scripts/project_manager.py create "My Book Title" --theme adventure --pages 20
python scripts/project_manager.py list
```

## Reference Material

### Existing books we've made (for Latin level reference)
- `projects/dada_and_the_cockroach/` — simplest Latin, best baseline for new books
- `projects/augustine_steals_the_pears/` — slightly more complex
- `projects/locusts_and_dragon/` — action-heavy adventure
- `projects/lion_witch_wardobe/` — adapted story, most complex Latin

### Published Latin picture books (in `existing_stories/`)
- Candidus et dies horribilis, Iulus et pugna, Minimus et umbra
- Octavus Octopus (Rose Williams), Taurus Rex
- Vibrissa amissa est, Vibrissa et ballista
- These are useful for vocabulary and style reference, especially for modern concepts

## Environment

- **Image generation**: OpenAI API (`gpt-image-1`) — requires `OPENAI_API_KEY` in `.env`
- **PDF generation**: WeasyPrint
- **Schemas**: Pydantic models in `book_schemas.py`
- **Python deps**: `pip install -r requirements.txt`

## Key Files

- `book_schemas.py` — data models (StoryOutline, BookTranslation, VisualBible, BookProject)
- `config.py` — configuration constants
- `scripts/project_manager.py` — create/load/list projects
- `scripts/image_generator.py` — OpenAI image generation + CLI
- `scripts/pdf_builder.py` — HTML→PDF assembly + CLI
- `.claude/agents/` — agent definitions (story-architect, latin-scribe, latin-censor, art-director)
