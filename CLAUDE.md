# Latin Children's Book System

A tool for creating illustrated Latin children's books using Claude Code agents and AI image generation.

## Project Overview

This system creates picture books in Latin for a toddler learning Latin as a living language. Books are 15-30 pages, with simple Latin text (3-7 words per sentence) and full-page illustrations.

## Workflow

The book creation pipeline has 4 stages with review gates between each:

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

### 5. Image Generation (script)
- Run: `python scripts/generate_images.py {project_id}`
- Generates images using OpenAI API (`gpt-image-1`)
- **REVIEW GATE**: User reviews images, can regenerate individual pages

### 6. PDF Assembly (script)
- Run: `python scripts/build_book.py {project_id}`
- Assembles final PDF from text + images

## Important: Review Gates Are Iterative

Every review gate allows the user to request changes. When they do, edit the existing draft — never start from scratch unless explicitly asked. The agents should read the existing files and make targeted edits.

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
│   └── prompts.json         # Per-page image prompts
├── images/
│   └── page_*.png           # Generated page images
└── output/
    ├── book.html
    └── book.pdf
```

## Creating a New Project

To start a new book, create the project folder and config:
```bash
python scripts/project_manager.py create "My Book Title"
```
This creates the folder structure and a minimal `config.json`.

## Existing Books (for Latin level reference)

- `projects/dada_and_the_cockroach/` — simplest Latin, best baseline
- `projects/augustine_steals_the_pears/` — slightly more complex
- `projects/locusts_and_dragon/` — action-heavy adventure
- `projects/lion_witch_wardobe/` — adapted story, most complex Latin

## Key Design Decisions

- **Image consistency** is achieved through the Visual Bible approach: every image prompt is self-contained with identical style/character descriptions. This beats reference images for consistency.
- **Established characters** (Toon Link, etc.) are a consistency win — the image model already knows them.
- **No vocabulary tracking** — this is not a textbook system. Just write natural Latin.
- **Latin as a living language** — not academic/archival Latin. Use natural constructions, allow modern paraphrases when needed.

## Environment

- Image generation: OpenAI API (`gpt-image-1`) — requires `OPENAI_API_KEY` in `.env`
- PDF generation: WeasyPrint (Python)
- Schemas: Pydantic models in `book_schemas.py`
