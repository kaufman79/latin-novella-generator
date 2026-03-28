#!/usr/bin/env python3
"""
PDF book builder using HTML templates and WeasyPrint.
Assembles images and Latin/English text into a picture book PDF.
"""

import sys
import json
from pathlib import Path
from weasyprint import HTML

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookTranslation


ALL_VIRTUES = ["prudentia", "iustitia", "fortitudo", "temperantia", "fides", "spes", "caritas"]
VIRTUE_DISPLAY = {
    "prudentia": "Prudentia",
    "iustitia": "Iūstitia",
    "fortitudo": "Fortitūdō",
    "temperantia": "Temperantia",
    "fides": "Fidēs",
    "spes": "Spēs",
    "caritas": "Cāritās",
}


def _get_primary_virtue(config: dict) -> str | None:
    """Get the highest-rated virtue from config."""
    ratings = config.get("virtue_ratings", {})
    if not ratings:
        return None
    best = max(ALL_VIRTUES, key=lambda v: ratings.get(v, 0))
    if ratings.get(best, 0) == 0:
        return None
    return VIRTUE_DISPLAY.get(best, best.capitalize())


def _load_glossary(project_folder: str) -> list[tuple[str, str]] | None:
    """Load glossary from project's translation/glossary.json if it exists.

    Format: [{"latin": "arx, arcis (f.)", "english": "fortress"}, ...]
    Returns list of (latin, english) tuples, or None if no glossary file.
    """
    glossary_path = Path(project_folder) / "translation" / "glossary.json"
    if not glossary_path.exists():
        return None
    with open(glossary_path) as f:
        entries = json.load(f)
    return [(e["latin"], e["english"]) for e in entries]


def _build_glossary_from_translation(translation: BookTranslation) -> list[tuple[int, str, str]]:
    """Build a page-by-page glossary from the translation.

    Returns list of (page_number, latin_text, english_text) tuples.
    For pages with multiple sentences, splits into separate entries so each
    Latin sentence is paired with its English equivalent.
    """
    import re

    entries = []
    for page in translation.pages:
        latin = page.latin_text.strip()
        english = page.english_text.strip()

        # Split multi-sentence pages into individual sentence pairs.
        # Sentences end with . ! or ? (possibly inside quotes).
        # We split both Latin and English the same way and pair them up.
        latin_sentences = _split_sentences(latin)
        english_sentences = _split_sentences(english)

        if len(latin_sentences) == len(english_sentences) and len(latin_sentences) > 1:
            # Matched split — pair each sentence
            for lat, eng in zip(latin_sentences, english_sentences):
                entries.append((page.page_number, lat.strip(), eng.strip()))
        else:
            # Can't split evenly — keep as one entry
            entries.append((page.page_number, latin, english))

    return entries


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping punctuation attached.

    Handles quoted speech and standard sentence-ending punctuation.
    """
    import re
    # Split on sentence-ending punctuation followed by whitespace.
    # Use alternation in the lookbehind for fixed-width patterns:
    # match after .  !  ?  or closing-quote variants like ."  !"  ?"
    parts = re.split(
        r'(?:(?<=[.!?])|(?<=[.!?]["»\u201d]))\s+',
        text.strip()
    )
    # Filter out empty strings
    return [p for p in parts if p.strip()]


def generate_html(title_latin: str, title_english: str, translation: BookTranslation, project_folder: str, config: dict = None) -> str:
    """Generate HTML for the book."""
    html_parts = []

    # Get primary virtue for cover badge
    primary_virtue = _get_primary_virtue(config) if config else None

    html_parts.append("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: 8.5in 11in;
            margin: 0.5in;
        }

        body {
            font-family: 'Palatino', 'Georgia', serif;
            line-height: 1.6;
            color: #333;
        }

        .title-page {
            text-align: center;
            page-break-after: always;
            padding-top: 3in;
        }

        .title-page h1 {
            font-size: 36pt;
            margin-bottom: 0.5in;
            color: #2c3e50;
        }

        .title-page .english {
            font-size: 24pt;
            color: #7f8c8d;
            font-style: italic;
        }

        .story-page {
            page-break-after: always;
            text-align: center;
        }

        .story-page img {
            max-width: 100%;
            max-height: 7in;
            object-fit: contain;
            display: block;
            margin: 0 auto 0.5in auto;
        }

        .story-page .latin-text {
            font-size: 20pt;
            font-weight: bold;
            color: #2c3e50;
            margin: 0.3in 0;
        }

        .story-page .english-text {
            font-size: 14pt;
            color: #7f8c8d;
            font-style: italic;
        }

        .story-page .page-number {
            position: absolute;
            bottom: 0.3in;
            right: 0.3in;
            font-size: 12pt;
            color: #bdc3c7;
        }

        .virtue-badge {
            display: inline-block;
            border: 2px solid #8e7c5a;
            border-radius: 20px;
            padding: 4px 18px;
            font-size: 13pt;
            font-variant: small-caps;
            letter-spacing: 2px;
            color: #8e7c5a;
            background-color: rgba(255, 255, 255, 0.75);
            margin-top: 15px;
        }

        .inside-cover {
            page-break-after: always;
            padding-top: 2.5in;
            text-align: center;
        }

        .inside-cover h2 {
            font-size: 16pt;
            font-variant: small-caps;
            letter-spacing: 3px;
            color: #8e7c5a;
            margin-bottom: 0.4in;
            border-bottom: 1px solid #d5c9b1;
            display: inline-block;
            padding-bottom: 6px;
        }

        .virtue-row {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 8px 0;
            font-size: 12pt;
        }

        .virtue-name {
            width: 140px;
            text-align: right;
            padding-right: 15px;
            font-variant: small-caps;
            letter-spacing: 1px;
            color: #5a5a5a;
        }

        .virtue-dots {
            display: flex;
            gap: 6px;
        }

        .virtue-dot {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 1.5px solid #8e7c5a;
        }

        .virtue-dot.filled {
            background-color: #8e7c5a;
        }

        .virtue-dot.empty {
            background-color: transparent;
        }

        .glossary-page {
            page-break-after: always;
            padding-top: 0.5in;
        }

        .glossary-page h2 {
            font-size: 16pt;
            font-variant: small-caps;
            letter-spacing: 3px;
            color: #8e7c5a;
            text-align: center;
            margin-bottom: 0.3in;
            border-bottom: 1px solid #d5c9b1;
            padding-bottom: 6px;
        }

        .glossary-table {
            width: 100%;
            border-collapse: collapse;
        }

        .glossary-table td {
            padding: 4px 8px;
            vertical-align: top;
            font-size: 10pt;
            line-height: 1.4;
            border-bottom: 1px solid #f0ebe3;
        }

        .glossary-table td.glossary-page-num {
            width: 30px;
            text-align: right;
            color: #bdc3c7;
            font-size: 9pt;
            padding-right: 10px;
            white-space: nowrap;
        }

        .glossary-table td.glossary-latin {
            width: 48%;
            font-weight: bold;
            color: #2c3e50;
        }

        .glossary-table td.glossary-english {
            width: 48%;
            color: #7f8c8d;
            font-style: italic;
        }

        /* Legacy single-word glossary styles (for glossary.json overrides) */
        .glossary-columns {
            column-count: 2;
            column-gap: 0.4in;
            column-rule: 1px solid #e0d9cc;
        }

        .glossary-entry {
            margin: 0;
            padding: 3px 0;
            break-inside: avoid;
            font-size: 10pt;
            line-height: 1.4;
        }

        .glossary-entry .glossary-latin {
            font-weight: bold;
            color: #2c3e50;
        }

        .glossary-entry .glossary-english {
            color: #7f8c8d;
            font-style: italic;
        }
    </style>
</head>
<body>
""")

    # Cover page
    cover_path = Path(project_folder) / 'images' / 'cover.png'
    if cover_path.exists():
        abs_cover = cover_path.resolve()
        html_parts.append(f"""
    <div class="story-page" style="position: relative;">
        <img src="file://{abs_cover}" alt="Cover" style="max-height: 10in; width: 100%;">
        <div style="position: absolute; bottom: 10%; left: 50%; transform: translateX(-50%); text-align: center; width: 90%; background-color: rgba(255, 255, 255, 0.65); padding: 20px; border-radius: 10px;">
            <h1 style="font-size: 48pt; margin: 0; color: #2c3e50; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">{title_latin}</h1>
            <p style="font-size: 28pt; margin: 10px 0 0 0; color: #7f8c8d; font-style: italic;">{title_english}</p>
            {"<div class='virtue-badge'>" + primary_virtue + "</div>" if primary_virtue else ""}
        </div>
    </div>
""")
    else:
        html_parts.append(f"""
    <div class="title-page">
        <h1>{title_latin}</h1>
        <p class="english">{title_english}</p>
        {"<div class='virtue-badge'>" + primary_virtue + "</div>" if primary_virtue else ""}
    </div>
""")

    # Inside cover — virtue ratings
    ratings = config.get("virtue_ratings", {}) if config else {}
    if any(ratings.get(v, 0) > 0 for v in ALL_VIRTUES):
        virtue_rows = []
        for v in ALL_VIRTUES:
            score = ratings.get(v, 0)
            display_name = VIRTUE_DISPLAY.get(v, v.capitalize())
            dots = ''.join(
                f'<span class="virtue-dot {"filled" if i < score else "empty"}"></span>'
                for i in range(5)
            )
            virtue_rows.append(
                f'<div class="virtue-row">'
                f'<span class="virtue-name">{display_name}</span>'
                f'<span class="virtue-dots">{dots}</span>'
                f'</div>'
            )
        html_parts.append(f"""
    <div class="inside-cover">
        <h2>Virtūtēs</h2>
        {''.join(virtue_rows)}
    </div>
""")

    # Story pages
    for page in translation.pages:
        image_html = ""
        if page.image_path and Path(page.image_path).exists():
            abs_path = Path(page.image_path).resolve()
            image_html = f'<img src="file://{abs_path}" alt="Page {page.page_number}">'

        html_parts.append(f"""
    <div class="story-page">
        {image_html}
        <p class="latin-text">{page.latin_text}</p>
        <p class="english-text">{page.english_text}</p>
        <span class="page-number">{page.page_number}</span>
    </div>
""")

    # Glossary — use manual glossary.json if it exists, otherwise auto-generate
    # from the translation (page-by-page Latin/English reading aid)
    manual_glossary = _load_glossary(project_folder)
    if manual_glossary:
        # Manual glossary: two-column word/phrase list (legacy format)
        entries_html = []
        for lat, eng in manual_glossary:
            entries_html.append(
                f'<div class="glossary-entry">'
                f'<span class="glossary-latin">{lat}</span> — '
                f'<span class="glossary-english">{eng}</span>'
                f'</div>'
            )
        page_size = 40
        for chunk_start in range(0, len(entries_html), page_size):
            chunk = entries_html[chunk_start:chunk_start + page_size]
            header = "Glossārium" if chunk_start == 0 else "Glossārium (cont.)"
            html_parts.append(f"""
    <div class="glossary-page">
        <h2>{header}</h2>
        <div class="glossary-columns">
            {''.join(chunk)}
        </div>
    </div>
""")
    else:
        # Auto-generated glossary: page-by-page reading aid
        auto_glossary = _build_glossary_from_translation(translation)
        if auto_glossary:
            rows_html = []
            for pg, lat, eng in auto_glossary:
                rows_html.append(
                    f'<tr>'
                    f'<td class="glossary-page-num">{pg}</td>'
                    f'<td class="glossary-latin">{lat}</td>'
                    f'<td class="glossary-english">{eng}</td>'
                    f'</tr>'
                )
            # Split into pages of ~25 rows (table rows are taller than column entries)
            page_size = 25
            for chunk_start in range(0, len(rows_html), page_size):
                chunk = rows_html[chunk_start:chunk_start + page_size]
                header = "Glossārium" if chunk_start == 0 else "Glossārium (cont.)"
                html_parts.append(f"""
    <div class="glossary-page">
        <h2>{header}</h2>
        <table class="glossary-table">
            {''.join(chunk)}
        </table>
    </div>
""")

    # Attribution page for public domain adaptations
    if config and config.get("public_domain_source"):
        source = config["public_domain_source"]
        html_parts.append(f"""
    <div class="story-page" style="padding-top: 3in; text-align: center;">
        <p style="font-size: 14pt; color: #7f8c8d;">Illustrations by {source['illustrator']}</p>
        <p style="font-size: 12pt; color: #95a5a6;">from <em>{source['title']}</em> ({source.get('year', '')})</p>
        <p style="font-size: 10pt; color: #bdc3c7;">{source.get('license', 'Public Domain')}</p>
    </div>
""")

    html_parts.append("""
</body>
</html>
""")

    return '\n'.join(html_parts)


def build_pdf(project_id: str) -> Path:
    """
    Build PDF book from project files.

    Reads translation.json and images from the project folder.

    Args:
        project_id: Project ID

    Returns:
        Path to generated PDF
    """
    project_dir = Path("projects") / project_id
    config_file = project_dir / "config.json"
    translation_file = project_dir / "translation" / "translation.json"

    if not config_file.exists():
        raise FileNotFoundError(f"Project not found: {project_id}")

    if not translation_file.exists():
        raise FileNotFoundError(f"Translation not found: {translation_file}")

    # Load config for titles
    with open(config_file) as f:
        config = json.load(f)

    # Load translation
    with open(translation_file) as f:
        translation_data = json.load(f)
    translation = BookTranslation(**translation_data)

    title_latin = config.get("title_latin", translation.title_latin)
    title_english = config.get("title_english", translation.title_english)

    # Generate HTML
    print(f"Building PDF: {title_english}")
    html_content = generate_html(title_latin, title_english, translation, str(project_dir), config=config)

    # Save HTML
    output_dir = project_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    html_path = output_dir / "book.html"
    html_path.write_text(html_content, encoding='utf-8')

    # Convert to PDF
    pdf_path = output_dir / "book.pdf"
    HTML(string=html_content).write_pdf(str(pdf_path))

    print(f"  HTML: {html_path}")
    print(f"  PDF:  {pdf_path}")

    return pdf_path


def main():
    """CLI for PDF building."""
    import argparse

    parser = argparse.ArgumentParser(description="Build PDF book from project")
    parser.add_argument("project_id", help="Project ID")

    args = parser.parse_args()

    try:
        pdf_path = build_pdf(args.project_id)
        print(f"\nDone: {pdf_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
