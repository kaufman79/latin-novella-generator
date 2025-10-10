# 📚 Book Production Workflow - Design Document

## Overview

This document outlines the complete workflow for creating illustrated Latin children's books from English stories.

---

## Workflow Steps

```
1. CREATE PROJECT
   ├─ Input: English story title
   ├─ Output: Project folder structure + config.json
   └─ CLI: python cli.py new-book "The Boy and the Pig" --theme animal --pages 10

2. TRANSLATE TO LATIN
   ├─ Input: English story + vocabulary suggestions from database
   ├─ AI Prompt: "Translate using these words..."
   ├─ Output: Latin translation (plain text)
   └─ CLI: python cli.py translate book_001

3. REVIEW & PAGINATE
   ├─ Input: Latin translation + English original
   ├─ AI Prompt: "Fix macrons, make idiomatic, paginate, create image prompts"
   ├─ Output: JSON with pages array
   └─ CLI: python cli.py review book_001

4. GENERATE IMAGES
   ├─ Input: Image prompts from JSON
   ├─ Process:
   │  ├─ Generate reference image (character/style consistency)
   │  └─ Generate each page image using reference
   ├─ Output: PNG files in projects/book_001/images/
   └─ CLI: python cli.py generate-images book_001

5. BUILD PDF
   ├─ Input: JSON + images
   ├─ Process:
   │  ├─ Generate LaTeX from template
   │  ├─ Format vocabulary dictionary
   │  ├─ Add play-based extensions
   │  └─ Compile to PDF
   ├─ Output: projects/book_001/output/book.pdf
   └─ CLI: python cli.py build-pdf book_001

6. APPROVE & UPDATE DATABASE
   ├─ Input: Completed book project
   ├─ Process:
   │  ├─ Preview vocabulary to be added
   │  ├─ User confirms
   │  └─ Update database frequency scores
   ├─ Output: Updated lexicon.db
   └─ CLI: python cli.py approve-book book_001
```

---

## Project Folder Structure

```
projects/
└── book_001_puer_et_porcus/
    ├── config.json                 # BookProject model
    ├── source/
    │   └── story_english.txt       # Original English story
    ├── translation/
    │   ├── latin_raw.txt           # Step 2 output
    │   └── translation.json        # Step 3 output (BookTranslation model)
    ├── images/
    │   ├── reference.png           # Character/style reference
    │   ├── page_01.png
    │   ├── page_02.png
    │   └── generation_log.json     # API call records
    ├── latex/
    │   ├── book.tex               # Generated LaTeX
    │   └── book.pdf               # Compiled PDF
    └── status.txt                 # Current workflow status
```

---

## JSON Schemas

### config.json (BookProject)
```json
{
  "project_id": "book_001",
  "title_english": "The Boy and the Pig",
  "title_latin": "Puer et Porcus",
  "source_text": "...",
  "theme": "animals",
  "target_pages": 10,
  "level": 1,
  "status": "pdf_built",
  "image_config": {
    "reference_image_path": "images/reference.png",
    "art_style": "watercolor, soft edges, warm tones",
    "provider": "nano_banana"
  }
}
```

### translation.json (BookTranslation)
```json
{
  "title_latin": "Puer et Porcus",
  "title_english": "The Boy and the Pig",
  "pages": [
    {
      "page_number": 1,
      "latin_text": "Puer porcum videt.",
      "english_text": "The boy sees a pig.",
      "image_prompt": "A young boy looking at a friendly pig...",
      "image_path": "images/page_01.png",
      "vocabulary_used": ["puer", "porcus", "videō"]
    }
  ],
  "vocabulary_list": [
    {
      "latin": "puer",
      "english": "boy",
      "part_of_speech": "noun",
      "dictionary_form": "puer, puerī, m.",
      "frequency_tier": "common"
    }
  ],
  "play_extensions": [
    {
      "category": "physical",
      "title": "Act It Out",
      "description": "Use toy animals to act out the story"
    }
  ]
}
```

---

## AI Prompts

### Prompt 1: Translation
```
You are translating an English children's story to Classical Latin.

VOCABULARY TO USE:
[Table of suggested words from database]

STORY TO TRANSLATE:
[English text]

INSTRUCTIONS:
1. Use ONLY the vocabulary provided above when possible
2. Keep sentences simple (3-7 words)
3. Use present tense primarily
4. Use proper macrons (ā, ē, ī, ō, ū)
5. Make it natural and idiomatic for children

OUTPUT:
Provide ONLY the Latin translation, one sentence per line.
```

### Prompt 2: Review & Paginate
```
You are reviewing and preparing a Latin children's story for publication.

LATIN TRANSLATION:
[Latin text from Step 1]

ENGLISH ORIGINAL:
[English text]

INSTRUCTIONS:
1. Review Latin for idiomatic usage
2. Verify/fix all macrons
3. Divide into 8-12 pages (1-2 sentences per page max)
4. Create detailed image prompt for each page
5. Extract vocabulary list with lemmas

OUTPUT FORMAT (JSON):
{
  "title_latin": "...",
  "title_english": "...",
  "pages": [
    {
      "page_number": 1,
      "latin_text": "...",
      "english_text": "...",
      "image_prompt": "...",
      "vocabulary_used": ["lemma1", "lemma2"]
    }
  ],
  "vocabulary_list": [
    {
      "latin": "puer",
      "english": "boy",
      "part_of_speech": "noun",
      "dictionary_form": "puer, puerī, m."
    }
  ]
}

IMPORTANT: Return ONLY valid JSON, no other text.
```

---

## Image Generation Strategy

### Nano Banana API Flow

1. **Generate Reference Image**
   ```python
   # Create character/style reference
   reference_prompt = "Main character: young boy, brown hair, simple tunic, " + art_style
   reference_image = generate_image(reference_prompt)
   save(reference_image, "images/reference.png")
   ```

2. **Generate Page Images**
   ```python
   for page in pages:
       # Use reference image for consistency
       page_image = generate_image(
           prompt=page.image_prompt + ", " + art_style,
           reference_image="images/reference.png"
       )
       save(page_image, f"images/page_{page.number:02d}.png")
   ```

### API Configuration
- Provider: Gemini 2.5 Flash Image (Nano Banana)
- Cost: ~$0.039 per image
- Total: ~$0.40 per 10-page book
- Consistency: Reference image method

---

## Dictionary Formatting

### Strategy
Since CLTK doesn't provide full dictionary forms, use a hybrid approach:

**Option 1: Database Lookup**
- For words in FF625/DCC: Use pre-stored forms

**Option 2: AI Generation**
- During review/pagination prompt, ask AI to provide proper dictionary forms
- AI knows Latin grammar and can generate: "puer, puerī, m."

**Option 3: Morphology Library** (future)
- Use Latin morphology generator (e.g., Collatinus)

**Implemented**: Option 2 (AI generates during review step)

---

## LaTeX Template

### Structure
```latex
\documentclass[letterpaper]{book}
\usepackage{graphicx}
\usepackage{fontspec}
\setmainfont{Latin Modern Roman}

\begin{document}

% Title Page
\title{Puer et Porcus \\ {\normalsize The Boy and the Pig}}
\maketitle

% Story Pages
\foreach \page in {1,...,10} {
  \begin{figure}
    \includegraphics[width=\textwidth]{images/page_\page.png}
  \end{figure}
  \begin{center}
    \Large [Latin text]
  \end{center}
  \newpage
}

% Vocabulary Dictionary
\chapter*{Vocabulary}
\begin{description}
  \item[puer, puerī, m.] boy
  \item[porcus, porcī, m.] pig
  \item[videō, vidēre, vīdī, vīsum] see, look at
\end{description}

% Play-Based Extensions
\chapter*{Activities}
...

\end{document}
```

---

## CLI Commands

```bash
# 1. Create new book project
python cli.py new-book "The Boy and the Pig" \
  --theme animal \
  --pages 10 \
  --level 1 \
  --story "path/to/english_story.txt"

# 2. Generate translation prompt (with vocab suggestions)
python cli.py translate book_001

# 3. [Copy prompt to AI, paste response back]
# Save AI output to projects/book_001/translation/latin_raw.txt

# 4. Generate review/pagination prompt
python cli.py review book_001

# 5. [Copy prompt to AI, paste JSON response]
# Save JSON to projects/book_001/translation/translation.json

# 6. Generate images (requires API key)
python cli.py generate-images book_001 \
  --style "watercolor, soft edges, warm tones"

# 7. Build PDF
python cli.py build-pdf book_001

# 8. Preview vocabulary impact
python cli.py preview-vocab book_001

# 9. Approve and update database
python cli.py approve-book book_001

# Utilities
python cli.py list-books              # Show all projects
python cli.py status book_001         # Show project status
python cli.py edit-config book_001    # Edit project config
```

---

## Database Update Workflow

### Preview Mode
```bash
$ python cli.py preview-vocab book_001

📊 VOCABULARY IMPACT PREVIEW

New words to add to database:
  1. porcus (pig) - ff625
  2. equus (horse) - common

Words already tracked:
  1. puer (boy) - will update frequency_score: 5 → 7
  2. canis (dog) - will update frequency_score: 5 → 6

Summary:
  - 2 new words
  - 2 existing words updated
  - Total vocabulary: 14 unique words

Approve? (y/n)
```

### Approval
```bash
$ python cli.py approve-book book_001

✅ Book approved!
✅ Updated database:
   - Added 2 new words
   - Updated 2 existing words
   - Recorded as story in database (Level 1)

📊 Updated coverage:
   - Total stories: 3
   - Vocabulary coverage: 12.3% (173/1405)
```

---

## Implementation Priority

### Phase 1: Core Structure ✅
- [x] JSON schemas (book_schemas.py)
- [x] Design document

### Phase 2: Project Management (Next)
- [ ] Project creation (cli.py new-book)
- [ ] Folder structure initialization
- [ ] Status tracking

### Phase 3: AI Prompts
- [ ] Translation prompt generator
- [ ] Review/pagination prompt generator
- [ ] Vocabulary suggestion integration

### Phase 4: Image Generation
- [ ] Nano Banana API wrapper
- [ ] Reference image generation
- [ ] Page image generation

### Phase 5: PDF Assembly
- [ ] LaTeX template
- [ ] Dictionary formatter
- [ ] Play extensions formatter
- [ ] PDF compilation

### Phase 6: Database Integration
- [ ] Vocabulary preview
- [ ] Approval workflow
- [ ] Database updates

---

## Questions Resolved

1. **Dictionary forms**: AI generates during review step
2. **Image consistency**: Reference image method with Nano Banana
3. **Pages per book**: 8-12 pages
4. **Art style**: Configurable per project
5. **Vocab suggestions**: Same algorithm as current system
6. **Database timing**: Manual approval after PDF built

---

**Ready to implement Phase 2!**
