# Public Domain Adaptation Pipeline

How to adapt books with existing public domain illustrations (vs. AI-generated images).

**Implementation status (2026-03-28):** All schema changes and scripts are implemented and tested. See `book_schemas.py` (PublicDomainSource, ImageMapping, ImageManifest), `scripts/gutenberg_downloader.py`, `scripts/image_mapper.py`, and modifications to `project_manager.py`, `image_generator.py`, `pdf_builder.py`. Not yet tested end-to-end with a real PD book.

## Key Insight

The current `pdf_builder.py` doesn't care where images come from — it just reads `image_path` from the translation. So the PDF assembly step needs minimal changes. Most work is upstream.

## New Workflow (vs. Original)

```
Original:     outline → translation → visual_bible + prompts → image_generator → pdf_builder
PD Adaptation: outline → translation → download PD art → map images to pages → (generate gaps) → pdf_builder
```

### Step by Step

1. **Create project** with `--source-type public_domain_adaptation`
   ```bash
   python scripts/project_manager.py create "The Tale of Peter Rabbit" \
     --source-type public_domain_adaptation \
     --source-url "https://www.gutenberg.org/ebooks/14838" \
     --illustrator "Beatrix Potter" \
     --author "Beatrix Potter"
   ```

2. **Download illustrations**: `python scripts/gutenberg_downloader.py {id} --url {gutenberg_html_url}`
   - Fetches all `<img>` tags from the Gutenberg HTML page
   - Saves to `projects/{id}/source_images/`
   - Prints numbered list with original captions

3. **Story planning** → `@story-architect` (plan Latin story *around* available illustrations)

4. **Latin translation** → `@latin-scribe` + `@latin-censor` (unchanged)

5. **Map images to pages**: `python scripts/image_mapper.py {id}`
   - Interactive CLI: for each page, assign a source image or mark for AI generation
   - Writes `art/image_manifest.json`
   - Copies/converts selected images to `images/page_XX.png`

6. **Generate missing images**: `python scripts/image_generator.py {id}` (skips pages with existing images per manifest)

7. **Build PDF**: `python scripts/pdf_builder.py {id}` (includes attribution page)

## Implementation Changes (Done)

### Schema Changes (`book_schemas.py`) — IMPLEMENTED

```python
class PublicDomainSource(BaseModel):
    title: str
    author: str
    illustrator: str
    source_url: str
    year: Optional[int] = None
    license: str = "Public Domain"

class ImageMapping(BaseModel):
    page_number: int
    source: str = "existing"          # "existing" or "generate"
    image_filename: Optional[str] = None
    original_caption: Optional[str] = None
    generate_prompt: Optional[str] = None

class ImageManifest(BaseModel):
    source: PublicDomainSource
    mappings: List[ImageMapping]
```

Add to `BookProject`:
- `source_type` accepts `"public_domain_adaptation"`
- `public_domain_source: Optional[PublicDomainSource] = None`

### New Scripts — IMPLEMENTED

| Script | Purpose |
|--------|---------|
| `scripts/gutenberg_downloader.py` | Download all images from a Gutenberg HTML page |
| `scripts/image_mapper.py` | Interactive CLI to assign PD images to pages (+ `--batch` mode) |

### Modified Scripts — IMPLEMENTED

| Script | Change |
|--------|--------|
| `scripts/project_manager.py` | `--source-type`, `--source-url`, `--illustrator`, `--author` args; creates `source_images/` dir |
| `scripts/image_generator.py` | Load `image_manifest.json` if present; skip pages where `source == "existing"` |
| `scripts/pdf_builder.py` | `object-fit: contain` for variable aspect ratios; attribution page at end |

### PDF Builder Details

- Replace fixed `max-height: 7in` with flexible layout + `object-fit: contain`
- Add `.attribution-page` at end with illustrator credit and source URL
- Handle variable image formats (Gutenberg serves GIF, JPEG, PNG)

## What Doesn't Change

- `@latin-scribe` and `@latin-censor` — text-only, source-agnostic
- `@art-director` — not needed for pure PD reuse; still works for mixed mode
- `BookTranslation` / `BookPage` schema — `image_path` already works for any source
- Core `generate_image()` function — only orchestration gains manifest awareness

## Potential Challenges

1. **Gutenberg HTML varies** — downloader should be robust but not over-engineered
2. **Low resolution** — PD images often 300-600px. AI images are 1024x1024. Accept the vintage aesthetic for now; upscaling optional later
3. **Aspect ratio variation** — some illustrations are tall plates, others are small vignettes. CSS must handle both
4. **Mixed mode style mismatch** — when mixing PD + AI images, the Art Director's visual bible should describe the PD style so AI pages are at least somewhat harmonious

## Project Structure (PD Adaptation)

```
projects/{project_id}/
├── config.json                 # source_type: "public_domain_adaptation"
├── source_images/              # Raw downloads from Gutenberg
├── source/outline.json
├── translation/
│   ├── translation.json
│   └── review.md
├── art/
│   └── image_manifest.json    # Page-to-image mapping (replaces prompts.json)
├── images/page_*.png          # Curated images (PD + generated)
└── output/book.pdf
```
