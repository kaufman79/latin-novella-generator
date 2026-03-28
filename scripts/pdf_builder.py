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


def generate_html(title_latin: str, title_english: str, translation: BookTranslation, project_folder: str, config: dict = None) -> str:
    """Generate HTML for the book."""
    html_parts = []

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
        </div>
    </div>
""")
    else:
        html_parts.append(f"""
    <div class="title-page">
        <h1>{title_latin}</h1>
        <p class="english">{title_english}</p>
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
