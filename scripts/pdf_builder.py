#!/usr/bin/env python3
"""
PDF book builder using HTML templates and WeasyPrint.
Assembles images, Latin text, vocabulary, and play extensions into a PDF.
"""

import sys
import json
from pathlib import Path
from weasyprint import HTML, CSS
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookProject, BookTranslation, PlayExtension
from scripts.book_manager import load_project, update_project_status


def generate_html(project: BookProject, translation: BookTranslation) -> str:
    """Generate HTML for the book."""
    html_parts = []

    # HTML header with CSS
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

        /* Title page */
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

        /* Story pages */
        .story-page {
            page-break-after: always;
            text-align: center;
        }

        .story-page img {
            max-width: 100%;
            max-height: 7in;
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

        /* Vocabulary section */
        .vocabulary-section {
            page-break-before: always;
        }

        .vocabulary-section h2 {
            font-size: 24pt;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 0.2in;
            margin-bottom: 0.3in;
        }

        .vocab-entry {
            margin-bottom: 0.05in;
            page-break-inside: avoid;
            line-height: 1.0;
        }

        .vocab-entry .headword {
            font-size: 11pt;
            font-weight: bold;
            color: #2c3e50;
        }

        .vocab-entry .definition {
            font-size: 10pt;
            color: #34495e;
            margin-left: 0.15in;
        }

        .vocab-entry .pos {
            font-size: 9pt;
            color: #7f8c8d;
            font-style: italic;
        }

        /* Play extensions */
        .extensions-section {
            page-break-before: always;
        }

        .extensions-section h2 {
            font-size: 24pt;
            color: #2c3e50;
            border-bottom: 3px solid #e74c3c;
            padding-bottom: 0.2in;
            margin-bottom: 0.3in;
        }

        .extension-category h3 {
            font-size: 16pt;
            color: #e74c3c;
            margin-top: 0.3in;
            margin-bottom: 0.1in;
        }

        .extension {
            margin-bottom: 0.15in;
            margin-left: 0.2in;
        }

        .extension strong {
            color: #2c3e50;
        }

        .repetition-tracker {
            margin-top: 0.3in;
            padding: 0.2in;
            background-color: #ecf0f1;
            border-radius: 5px;
        }

        .repetition-tracker h3 {
            font-size: 14pt;
            color: #2c3e50;
            margin-bottom: 0.1in;
        }

        .checkbox {
            display: inline-block;
            width: 0.15in;
            height: 0.15in;
            border: 1px solid #34495e;
            margin-right: 0.1in;
            vertical-align: middle;
        }
    </style>
</head>
<body>
""")

    # Cover page (if exists)
    cover_path = Path(project.project_folder) / 'images' / 'cover.png'
    if cover_path.exists():
        abs_cover_path = cover_path.resolve()
        html_parts.append(f"""
    <div class="story-page" style="position: relative;">
        <img src="file://{abs_cover_path}" alt="Cover" style="max-height: 10in; width: 100%;">
        <div style="position: absolute; bottom: 10%; left: 50%; transform: translateX(-50%); text-align: center; width: 90%; background-color: rgba(255, 255, 255, 0.65); padding: 20px; border-radius: 10px;">
            <h1 style="font-size: 48pt; margin: 0; color: #2c3e50; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">{translation.title_latin}</h1>
            <p style="font-size: 28pt; margin: 10px 0 0 0; color: #7f8c8d; font-style: italic;">{translation.title_english}</p>
        </div>
    </div>
""")
    else:
        # Title page fallback if no cover
        html_parts.append(f"""
    <div class="title-page">
        <h1>{translation.title_latin}</h1>
        <p class="english">{translation.title_english}</p>
    </div>
""")

    # Story pages
    for page in translation.pages:
        image_path = page.image_path
        if image_path and Path(image_path).exists():
            # Convert to absolute path for WeasyPrint
            abs_image_path = Path(image_path).resolve()

            html_parts.append(f"""
    <div class="story-page">
        <img src="file://{abs_image_path}" alt="Page {page.page_number}">
        <p class="latin-text">{page.latin_text}</p>
        <p class="english-text">{page.english_text}</p>
        <span class="page-number">{page.page_number}</span>
    </div>
""")
        else:
            # Page without image
            html_parts.append(f"""
    <div class="story-page">
        <p class="latin-text">{page.latin_text}</p>
        <p class="english-text">{page.english_text}</p>
        <span class="page-number">{page.page_number}</span>
    </div>
""")

    # Vocabulary dictionary
    html_parts.append("""
    <div class="vocabulary-section">
        <h2>📖 Vocabulary</h2>
""")

    for entry in translation.vocabulary_list:
        html_parts.append(f"""
        <div class="vocab-entry">
            <span class="headword">{entry.dictionary_form}</span>
            <span class="definition">{entry.english}</span>
            <span class="pos">({entry.part_of_speech})</span>
        </div>
""")

    html_parts.append("    </div>")

    # Close HTML
    html_parts.append("""
</body>
</html>
""")

    return '\n'.join(html_parts)


def add_default_play_extensions(translation: BookTranslation):
    """Add default play-based extensions if none exist."""
    if translation.play_extensions:
        return  # Already has extensions

    default_extensions = [
        PlayExtension(
            category="retelling",
            title="Gesture Retelling",
            description="Parent reads while child acts out all verbs"
        ),
        PlayExtension(
            category="retelling",
            title="Echo Reading",
            description="Child repeats each sentence after parent"
        ),
        PlayExtension(
            category="physical",
            title="Act It Out",
            description="Use toy animals or objects to act out the story"
        ),
        PlayExtension(
            category="creative",
            title="Draw the Story",
            description="Child illustrates each sentence"
        ),
        PlayExtension(
            category="vocabulary",
            title="Point and Name",
            description="Look at illustrations and identify objects in Latin"
        ),
        PlayExtension(
            category="real_world",
            title="Daily Connections",
            description="Use story vocabulary during daily activities"
        )
    ]

    translation.play_extensions = default_extensions


def build_pdf(project: BookProject, translation: BookTranslation, output_path: Path) -> Path:
    """
    Build PDF book from project and translation.

    Args:
        project: BookProject instance
        translation: BookTranslation with pages and vocabulary
        output_path: Where to save the PDF

    Returns:
        Path to generated PDF
    """
    # Add default play extensions if none
    add_default_play_extensions(translation)

    # Generate HTML
    print("📝 Generating HTML...")
    html_content = generate_html(project, translation)

    # Save HTML for debugging
    html_file = output_path.parent / f"{output_path.stem}.html"
    html_file.write_text(html_content, encoding='utf-8')
    print(f"   HTML saved to {html_file}")

    # Convert to PDF
    print("📄 Converting to PDF...")
    HTML(string=html_content).write_pdf(str(output_path))

    print(f"   ✅ PDF saved to {output_path}")

    return output_path


def main():
    """CLI for PDF building."""
    import argparse

    parser = argparse.ArgumentParser(description='Build PDF book')
    parser.add_argument('project_id', help='Project ID')

    args = parser.parse_args()

    # Load project
    project = load_project(args.project_id)
    if not project:
        print(f"❌ Project '{args.project_id}' not found")
        sys.exit(1)

    # Load translation
    translation_file = Path(project.project_folder) / 'translation' / 'translation.json'
    if not translation_file.exists():
        print(f"❌ Translation file not found: {translation_file}")
        print("   Run: python cli.py book-review", args.project_id)
        sys.exit(1)

    with open(translation_file) as f:
        translation_data = json.load(f)

    translation = BookTranslation(**translation_data)

    # Check for images
    images_dir = Path(project.project_folder) / 'images'
    if not images_dir.exists() or not list(images_dir.glob('page_*.png')):
        print("⚠️  Warning: No page images found")
        print("   Run: python cli.py book-images", args.project_id)
        response = input("   Continue without images? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    # Build PDF
    latex_dir = Path(project.project_folder) / 'latex'
    latex_dir.mkdir(exist_ok=True)

    output_path = latex_dir / 'book.pdf'

    print(f"\n📚 Building PDF: {project.title_english}")
    print(f"   Pages: {len(translation.pages)}")
    print(f"   Vocabulary: {len(translation.vocabulary_list)} words")
    print()

    pdf_path = build_pdf(project, translation, output_path)

    # Update project status
    update_project_status(project, 'pdf_built')

    print(f"\n✅ PDF book complete!")
    print(f"   📄 {pdf_path}")
    print(f"\n💡 Next step: python cli.py book-approve {args.project_id}")


if __name__ == '__main__':
    main()
