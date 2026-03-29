# Latin Children's Book System

A tool for creating illustrated Latin children's books using Claude Code agents and AI image generation.

## Project Overview

This system creates picture books in Latin for a toddler (~3.5 years old) learning Latin as a living language. His father speaks Latin to him daily; his comprehension is roughly at a 1-year-old level but growing. Books are 15-30 pages, with simple Latin text (3-7 words per sentence) and full-page illustrations.

These are real children's books, not language textbooks. No vocab lists, no grammar drills. The pictures do a lot of the heavy lifting for comprehension — a child who doesn't fully understand the Latin should be able to follow the story through the illustrations.

---

## Story Philosophy: Classical Virtue Formation

These books are not just entertainment — they are forming a child's moral imagination. The framework is the classical and Christian virtue tradition (Aristotle → Aquinas).

### The Virtues

**Cardinal Virtues (Aristotelian):**
- **Prudentia** (Prudence / Practical Wisdom) — perceiving what a situation really is and determining the right response, then acting decisively on that judgment. Not caution or timidity — the prudent person sees reality clearly and commands action. The charioteer of the virtues (*auriga virtutum*).
- **Iustitia** (Justice) — the settled disposition to recognize and render to each person what genuinely belongs to them: their rights, their due, their fair share. Relational by nature — it always faces outward toward other persons. The minimum of love.
- **Fortitudo** (Fortitude / Courage) — the firm disposition to endure dangers and hardships for the sake of a genuine good, without being broken. The principal act is *sustinere* (endurance), not *aggredi* (attack) — holding firm over time, not the dramatic charge.
- **Temperantia** (Temperance / Self-Governance) — the inner ordering of the self, so that desires and appetites serve one's genuine good rather than ruling one's life. Not denial of pleasure but right proportion — the temperate person is free; the intemperate person is enslaved.

**Theological Virtues (Pauline/Scholastic):**
- **Fides** (Faith / Trust) — entrusting yourself to another person based on their character; faithfulness and loyalty. Not blind credulity but relational trust that involves vulnerability — the decision to trust when you could choose not to.
- **Spes** (Hope) — the confident, active pursuit of a genuine good that is difficult to reach, sustained through hardship and delay. Not optimism or wishful thinking — spes looks the difficulty in the face and moves forward anyway. Hope gives fortitudo its direction; fortitudo gives spes its backbone.
- **Caritas** (Charity / Love) — actively willing and doing the genuine good of another person, even at cost to yourself. Not "being nice" or sentimentality — caritas is a choice sustained over time, expressed through sacrifice, mercy, patience, and joy in the other's flourishing.

**Related Virtues:**
- Humilitas, Patientia, Misericordia, Gratitudo, Pietas, Magnanimitas, Mansuetudo

### Story Evaluation Framework

Every story should be checked against these five questions before production:

1. **Would this story be interesting if the child already knew the "lesson"?** The story must work as a story first. The virtue is depth, not the point.
2. **Does the character WANT something and face a genuine obstacle?** Want + obstacle = story. Without these, you have a lecture.
3. **Is emotion shown, not told?** "Link did not breathe" > "Link was afraid." Concrete, visible actions over abstract statements.
4. **Does the resolution come from the character's own choice?** The protagonist must be the agent of the decisive action.
5. **Is there one clear emotional through-line?** State the arc in one sentence. If you can't, the story is trying to do too much.

### Virtue Ratings & Tracking

Each book's `config.json` carries a `virtue_ratings` object rating how strongly it models each virtue (0-5 scale for each of the 7 cardinal + theological virtues). The collection should be balanced across virtues over time.

For detailed rubrics, rating guidelines (with examples at each level 0-5), and philosophical background on each virtue, see:
- `docs/cardinal_virtues_deep_dive.md` — Prudentia, Iustitia, Fortitudo, Temperantia
- `docs/theological_virtues_deep_dive.md` — Fides, Spes, Caritas

**Virtue badge on cover:** The PDF builder reads the highest-rated virtue from `config.json` and displays it as a badge on the front cover (e.g. "Fortitudo") in Latin with proper macrons, small-caps, and a decorative border.

**Inside cover virtue display:** The PDF builder renders a dot chart on the inside cover page showing all 7 virtues with filled/empty dots (out of 5) under the heading "Virtūtēs."

**Virtue coverage chart:** Run `python scripts/virtue_chart.py` to generate a bubble chart at `output/virtue_chart.png` showing ratings across all books, plus a text summary of coverage gaps. Use it to identify underrepresented virtues when planning new books.

### Story Principles

- **Build the virtue into the structure, not the ending.** Don't sermonize. Let cause-and-effect carry the moral weight.
- **Show, don't tell.** Illustrations do most of the emotional heavy lifting. Every moral beat must be visible in the art.
- **Give the hero one real choice.** The best stories hinge on a moment where the character chooses.
- **Failure is valuable.** Characters who fail and try again teach more than effortless success.
- **Repetition carries both language and values.** A repeated Latin phrase teaches vocabulary AND a virtue simultaneously.
- **One book, one primary virtue.** Secondary virtues can appear, but one should be central.
- **Respect the child's intelligence.** No moralizing, no "and so we learn that..." endings. Trust the story.

---

## Workflow

The book creation pipeline has review gates between each stage. **All gates are iterative** — the user gives feedback, you edit the existing draft. Never start from scratch unless explicitly asked.

### 1. Story Planning → `@story-architect`
- Interactive back-and-forth to develop a story concept
- **Check the story against the 5 evaluation questions and virtue framework**
- Output: `projects/{id}/source/outline.json`
- **REVIEW GATE**: User approves story before proceeding

### 2. Latin Translation → `@latin-scribe`
- Translates the English outline into natural Latin
- Output: `projects/{id}/translation/translation.json`

### 3. Latin Review → `@latin-censor`
- Reviews Latin for grammar, macrons, naturalness
- Updates translation in place, writes review to `projects/{id}/translation/review.md`
- **REVIEW GATE**: User approves Latin before proceeding

### 3b. Glossary
- Generate `projects/{id}/translation/glossary.json` — word-by-word vocabulary list
- Format: `[{"latin": "arx, arcis (f.)", "english": "fortress"}, ...]`
- Dictionary headword forms (nom. for nouns, 1st person for verbs), with principal parts abbreviation, gender, macrons
- Alphabetical, 30-80 entries per book. Skip proper names and common function words (et, in, nōn, sed, est)
- The PDF builder renders this as a two-column glossary page at the end of the book
- **Fallback**: If no `glossary.json` exists, the PDF builder auto-generates a page-by-page reading aid from the translation (3-column table: page number, Latin sentence, English sentence). A proper glossary.json is preferred.

### 4. Art Direction → `@art-director`
- Creates Visual Bible and per-page image prompts
- Output: `projects/{id}/art/visual_bible.json` and `projects/{id}/art/prompts.json`
- **REVIEW GATE**: User approves art direction before image generation (this is where $$ gets spent)

### 4b. Reference Image Pre-Production
```bash
python scripts/image_generator.py {project_id} --generate-refs
```
- Generates reference images for non-established characters and locations
- Reads the visual bible, identifies what needs refs, generates establishing shots and character sheets
- Output: `projects/{id}/art/references/*.png`
- After generation, add `reference_image_path` to each character/location in `visual_bible.json`
- The image generator automatically selects refs per page based on `characters_in_scene` and `location`
- **REVIEW GATE**: User approves refs before full page generation

### 5. Image Generation
```bash
# Generate all pages (synchronous, one at a time)
python scripts/image_generator.py {project_id}

# Regenerate specific pages only
python scripts/image_generator.py {project_id} --pages 3 7 12

# Batch mode — 50% cheaper, asynchronous
python scripts/image_generator.py {project_id} --batch

# Check batch job status
python scripts/image_generator.py {project_id} --batch-status {JOB_NAME}

# Download completed batch results
python scripts/image_generator.py {project_id} --batch-download {JOB_NAME}

# Custom resolution (default: 512)
python scripts/image_generator.py {project_id} --size 1024
```
- Generates images using Gemini API
- Automatically skips pages with existing public domain images (reads `art/image_manifest.json`)
- Updates `translation/translation.json` with image paths after generation
- **REVIEW GATE**: User reviews images, can regenerate individual pages

### 6. PDF Assembly
```bash
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib python scripts/pdf_builder.py {project_id}
```
- Assembles final PDF in `projects/{id}/output/book.pdf`
- Also saves HTML version at `projects/{id}/output/book.html`
- Includes cover page (with cover image if `images/cover.png` exists), virtue badge, inside cover virtue dots, story pages, and attribution page for public domain adaptations
- **macOS note**: WeasyPrint requires `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` to find native libraries

---

## Latin Guidelines

- **Living language, not academic.** Write Latin like a children's picture book — simple, clear, natural. Not textbook prose, not literary/archaic.
- **Don't shelter grammar.** Let tense, case, and construction come naturally. Perfect tense is fine for narratives.
- **Macrons on long vowels.** Mark all long vowels. Wrong macrons are worse than missing ones — if unsure, leave unmarked.
- **Minor latinity compromises are OK.** Natural readability over perfection.
- **Modern concepts.** Paraphrase or borrow. Reference Latin picture books in `existing_stories/` handle modern vocabulary well.
- **Sentences: 3-7 words.** This is a picture book for a toddler.
- **Repetition is good.** Repeated phrases help language learning naturally.

---

## Image Generation

### Primary: Google Gemini API
- **Model**: `gemini-3.1-flash-image-preview` (Nano Banana 2) — best for illustrated/cel-shaded styles and established characters
- **Cost**: ~$0.045/image at 512px resolution
- **Batch mode**: Use `--batch` flag for 50% discount (asynchronous — submit, poll status, then download)
- **Key**: `GEMINI_API_KEY` in `.env`
- **Resolution**: Default 512px (cheapest tier, fine for picture books). Configurable with `--size`.
- **Aspect ratio**: Square (1:1) for all pages
- **Prompt guidelines**: Never mention "book", "commercial", or "publication" in prompts. The script auto-strips these words. Describe art style and scene only.

### Fallback: OpenAI API
- **Model**: `gpt-image-1`
- **Key**: `OPENAI_API_KEY` in `.env`
- **Limitation**: Strict content filter blocks copyrighted characters (Nintendo, Disney, etc.)

### Image Consistency Strategy

Consistency comes from two complementary approaches:

**1. Visual Bible (text-based consistency):**
Every image prompt is fully self-contained with identical style and character descriptions. The Art Director agent assembles each prompt as [STYLE block] + [CHARACTER descriptions] + [LOCATION] + [SCENE], with style and character blocks identical across all pages.

- **Established characters** (Toon Link, Mario, etc.) are a huge consistency win — the image model already knows them.
- **Original characters** need extremely specific visual descriptions: exact colors, proportions, clothing, features.
- **Lock down details** to prevent drift: specify exact colors ("purple-gray skin, beady yellow eyes"), not vague descriptions.

**2. Reference images from official artwork:**
The `visual_bible.json` can specify `reference_images` — file paths to artwork that gets sent alongside every prompt. These are loaded as image inputs to Gemini with a style-matching instruction prefix. This dramatically improves consistency, especially for established characters.

- Reference images are specified in `visual_bible.json` at the top level (applies to all pages) or per-page in `prompts.json` (overrides defaults).
- The style instruction prefix is: "Using the exact art style from these reference images — the textured cel-shading, brush-stroke coloring, thick black outlines, and character proportions — generate a new scene:"
- Paths can be absolute or relative to `reference_images/`.

---

## Book Sources

### Original Stories
Interactive story development with `@story-architect`. Can use established characters (video game, fairy tale) or original characters.

### Toon Link Series
Ongoing series of Wind Waker-themed Latin adventure books. See `reference_images/toon_link/CLAUDE.md` for full details including:
- Latinized character names (Lincus, Tetra, Moblini)
- Official artwork reference images in `reference_images/toon_link/official/` (~30 files from Creative Uncut)
- Always pass 2 official Link artworks as reference images for consistency
- Generated character sheets and location references in `characters/` and `locations/` subdirectories

### Public Domain Adaptations
See `docs/public_domain_story_ideas.md` for a curated list of candidates with links to free illustrations. Key advantage: many have public domain illustrations (Potter, Brooke, Winter, Gag, Caldecott) on Project Gutenberg, saving image generation costs entirely. See also `docs/pd_adaptation_pipeline.md` and `docs/pd_adaptation_priorities.md`.

For PD adaptations, the image generator automatically skips pages that have existing illustrations mapped in `art/image_manifest.json`, only generating images for pages that need them.

### Translate Existing Books
For translating English kids' books into Latin (personal use):
1. Scan/photograph the pages
2. Extract or transcribe the English text
3. Use `@latin-scribe` to translate to Latin
4. Keep the original illustrations
5. Assemble new PDF with Latin text + original images

---

## Project Structure

### Repository Layout
```
projects/{project_id}/          # One directory per book
├── config.json                 # Metadata, virtue_ratings, status
├── source/outline.json         # English story outline
├── translation/
│   ├── translation.json        # Latin text + English + image paths
│   ├── glossary.json           # Word-by-word vocabulary list (optional — PDF auto-generates if missing)
│   └── review.md               # Latin review notes
├── art/
│   ├── visual_bible.json       # Style guide, character visuals, reference image paths
│   ├── prompts.json            # Per-page self-contained image prompts
│   └── image_manifest.json     # Page-to-image mapping (PD adaptations only)
├── images/
│   ├── cover.png               # Cover image (optional)
│   └── page_*.png              # Generated/sourced page images
├── source_images/              # Original PD illustrations (PD adaptations only)
└── output/
    ├── book.html               # Generated HTML
    └── book.pdf                # Final PDF

reference_images/               # Reusable character/style references
└── toon_link/                  # Toon Link series (official art, character sheets, locations)
    ├── CLAUDE.md               # Series-specific docs and conventions
    ├── official/               # Official Wind Waker character artwork
    ├── characters/             # Generated character reference sheets
    └── locations/              # Generated location reference images

existing_stories/               # Published Latin picture books (PDFs, for vocabulary/style reference)
docs/                           # Project documentation
├── public_domain_story_ideas.md
├── cardinal_virtues_deep_dive.md    # Detailed rubrics for prudentia, iustitia, fortitudo, temperantia
├── theological_virtues_deep_dive.md # Detailed rubrics for fides, spes, caritas
├── pd_adaptation_pipeline.md
├── pd_adaptation_priorities.md
├── potter_books_research.md
├── virtue_ratings_audit.md
├── little_engine_plan.md
└── little_engine_illustrations_research.md
output/                         # Cross-project outputs
└── virtue_chart.png            # Virtue coverage visualization
```

### Creating a New Project
```bash
# Basic project
python scripts/project_manager.py create "My Book Title"

# With options
python scripts/project_manager.py create "My Book Title" --theme adventure --pages 20

# Public domain adaptation
python scripts/project_manager.py create "The Tale of Peter Rabbit" \
    --source-type public_domain_adaptation \
    --source-url "https://www.gutenberg.org/ebooks/14838" \
    --author "Beatrix Potter" \
    --illustrator "Beatrix Potter"

# List all projects
python scripts/project_manager.py list

# Check project status
python scripts/project_manager.py status {project_id}
```

---

## Reference Material

### Existing books we've made
- `projects/dada_and_the_cockroach/` — simplest Latin, domestic comedy, best baseline
- `projects/augustine_steals_the_pears/` — moral arc (temperantia), slightly more complex
- `projects/locusts_and_dragon/` — action-heavy adventure, teamwork (fortitudo)
- `projects/lion_witch_wardobe/` — adapted story, richest virtue content, most complex Latin
- `projects/link_and_the_stolen_treasure/` — Toon Link adventure
- `projects/link_and_the_thiefs_lantern/` — Toon Link adventure (sequel)
- `projects/the_enormous_turnip/` — original retelling of the folk tale
- `projects/the_little_engine_that_could/` — PD adaptation
- `projects/the_tale_of_peter_rabbit/` — PD adaptation of Beatrix Potter
- `projects/the_tale_of_benjamin_bunny/` — PD adaptation of Beatrix Potter
- `projects/the_tale_of_tom_kitten/` — PD adaptation of Beatrix Potter
- `projects/the_tale_of_jemima_puddleduck/` — PD adaptation of Beatrix Potter
- `projects/the_tale_of_two_bad_mice/` — PD adaptation of Beatrix Potter

### Published Latin picture books (in `existing_stories/`)
- Candidus et dies horribilis, Iulus et pugna, Minimus et umbra
- Octavus Octopus (Rose Williams), Taurus Rex
- Vibrissa amissa est, Vibrissa et ballista
- Useful for vocabulary and style reference, especially for modern concepts

---

## Environment & Key Files

- **Python deps**: `pip install -r requirements.txt`
- **PDF generation**: WeasyPrint (requires `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib` on macOS)
- **Schemas**: `book_schemas.py` — Pydantic models (StoryOutline, BookTranslation, VisualBible, ImagePrompts, ImageManifest, BookProject)
- **Config**: `config.py` — constants (model names, default resolution, image formats)
- **Scripts**:
  - `scripts/project_manager.py` — create, list, and check status of projects
  - `scripts/image_generator.py` — generate images (sync or batch), check batch status, download results
  - `scripts/pdf_builder.py` — assemble HTML + PDF from translation and images
  - `scripts/virtue_chart.py` — generate bubble chart of virtue coverage across all books
- **Agents**: `.claude/agents/` — story-architect, latin-scribe, latin-censor, art-director
- **API keys**: `GEMINI_API_KEY` and `OPENAI_API_KEY` in `.env`
