#!/usr/bin/env python3
"""
Generate AI prompts for book translation and review workflow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookProject
from scripts.book_manager import load_project
from scripts.database import LatinDatabase


def suggest_vocabulary_for_book(db, theme=None, count=15):
    """
    Get vocabulary suggestions for book translation.

    Args:
        db: LatinDatabase instance
        theme: Optional theme to filter by (not currently used)
        count: Number of words to return

    Returns:
        List of tuples: (lemma, english, part_of_speech, mastery_level)
    """
    cursor = db.conn.cursor()

    # Get known words, prioritizing by frequency of use (times_seen)
    # and mastery level (lower = needs more practice)
    query = """
        SELECT lemma, english, part_of_speech, mastery_level
        FROM known_words
        ORDER BY times_seen DESC, mastery_level ASC
        LIMIT ?
    """
    words = cursor.execute(query, (count,)).fetchall()

    return words


def generate_translation_prompt(project: BookProject, db: LatinDatabase) -> str:
    """
    Generate prompt for translating story to Latin.
    This is for you to use while planning your story with AI.
    """
    lines = []

    lines.append("# 📖 LATIN STORY CREATION PROMPT")
    lines.append("")
    lines.append("You are helping create a Latin children's story.")
    lines.append("")
    lines.append("=" * 70)
    lines.append("")

    # Story guidelines
    lines.append("## STORY GUIDELINES")
    lines.append("")
    lines.append("### Language Requirements")
    lines.append("- Use Classical Latin with proper macrons (ā, ē, ī, ō, ū)")
    lines.append("- Keep sentences SHORT: 3-7 words maximum")
    lines.append("- Use primarily present tense")
    lines.append("- Simple subject-verb-object structure")
    lines.append("- Avoid complex subordinate clauses")
    lines.append("- Use concrete, physical vocabulary (no abstract concepts)")
    lines.append("")

    lines.append("### Story Structure")
    lines.append(f"- Target length: {project.target_pages} pages")
    lines.append("- 1-2 sentences per page maximum")
    lines.append("- Beginning: Introduce character/setting (2-3 sentences)")
    lines.append("- Middle: Action/event occurs (4-6 sentences)")
    lines.append("- End: Simple resolution (2-3 sentences)")
    lines.append("")

    lines.append("### Pedagogical Principles")
    lines.append("- **Repetition**: Repeat key words multiple times")
    lines.append("- **Actions**: Focus on physical actions children can gesture")
    lines.append("- **Concrete**: Use tangible objects and visible actions")
    lines.append("- **Positive**: Happy/playful tone")
    lines.append("- **Progressive**: Each sentence builds on the previous")
    lines.append("")

    # Vocabulary suggestions
    lines.append("=" * 70)
    lines.append("")
    lines.append("## 📝 SUGGESTED VOCABULARY")
    lines.append("")
    lines.append("These are high-frequency Latin words. Try to use these when possible:")
    lines.append("")

    vocab = suggest_vocabulary_for_book(db, theme=project.theme, count=20)

    lines.append("| Latin | English | Part of Speech | Mastery |")
    lines.append("|-------|---------|----------------|---------|")

    for lemma, english, pos, mastery in vocab:
        pos_display = pos or "—"
        mastery_display = ["New", "Familiar", "Mastered"][min(mastery or 1, 3) - 1] if mastery else "—"
        lines.append(f"| {lemma} | {english} | {pos_display} | {mastery_display} |")

    lines.append("")
    lines.append("*Note: You don't have to use all of these - they're just suggestions.*")
    lines.append("")

    # Story planning space
    lines.append("=" * 70)
    lines.append("")
    lines.append("## 📚 YOUR STORY")
    lines.append("")
    lines.append(f"**Theme**: {project.theme or 'open'}")
    lines.append(f"**Title**: {project.title_english}")
    if project.level:
        lines.append(f"**Level**: {project.level}")
    lines.append("")
    lines.append("### Instructions")
    lines.append("1. Plan your story in English first")
    lines.append("2. Translate to Latin following the guidelines above")
    lines.append("3. Use the suggested vocabulary when possible")
    lines.append("4. Keep it simple and fun!")
    lines.append("")
    lines.append("### Your Story (Latin)")
    lines.append("")
    lines.append("[Write your Latin story here, one sentence per line]")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("💡 **TIP**: After writing, use this for the review/pagination step!")
    lines.append("")

    return "\n".join(lines)


def generate_review_prompt(project: BookProject, latin_text: str, english_text: str = None) -> str:
    """
    Generate prompt for reviewing Latin and creating paginated JSON output.
    """
    lines = []

    lines.append("# 📋 LATIN STORY REVIEW & PAGINATION")
    lines.append("")
    lines.append("You are preparing a Latin children's story for publication.")
    lines.append("")
    lines.append("=" * 70)
    lines.append("")

    # Input texts
    lines.append("## LATIN TRANSLATION")
    lines.append("")
    lines.append("```")
    lines.append(latin_text)
    lines.append("```")
    lines.append("")

    if english_text:
        lines.append("## ENGLISH ORIGINAL")
        lines.append("")
        lines.append("```")
        lines.append(english_text)
        lines.append("```")
        lines.append("")

    # Instructions
    lines.append("=" * 70)
    lines.append("")
    lines.append("## YOUR TASK")
    lines.append("")
    lines.append("Review and prepare the Latin story:")
    lines.append("")
    lines.append("1. **Check idiomatic usage** - Make sure Latin sounds natural")
    lines.append("2. **Verify macrons** - Add/fix all macron marks (ā, ē, ī, ō, ū)")
    lines.append("3. **Paginate** - Divide into 8-12 pages (1-2 sentences per page)")
    lines.append("4. **Create image prompts** - Detailed prompt for each page illustration")
    lines.append("5. **Extract vocabulary** - List all unique words with dictionary forms")
    lines.append("")

    # JSON format
    lines.append("=" * 70)
    lines.append("")
    lines.append("## OUTPUT FORMAT")
    lines.append("")
    lines.append("Return ONLY valid JSON (no other text):")
    lines.append("")
    lines.append("```json")
    lines.append("{")
    lines.append(f'  "title_latin": "...",')
    lines.append(f'  "title_english": "{project.title_english}",')
    lines.append('  "pages": [')
    lines.append('    {')
    lines.append('      "page_number": 1,')
    lines.append('      "latin_text": "Puer porcum videt.",')
    lines.append('      "english_text": "The boy sees a pig.",')
    lines.append('      "image_prompt": "A young boy in a tunic looking at a friendly pink pig in a sunny farm yard, children\'s book illustration, watercolor style, warm colors",')
    lines.append('      "vocabulary_used": ["puer", "porcus", "videō"]')
    lines.append('    },')
    lines.append('    {')
    lines.append('      "page_number": 2,')
    lines.append('      "latin_text": "...",')
    lines.append('      "..."')
    lines.append('    }')
    lines.append('  ],')
    lines.append('  "vocabulary_list": [')
    lines.append('    {')
    lines.append('      "latin": "puer",')
    lines.append('      "english": "boy",')
    lines.append('      "part_of_speech": "noun",')
    lines.append('      "dictionary_form": "puer, puerī, m."')
    lines.append('    },')
    lines.append('    {')
    lines.append('      "latin": "videō",')
    lines.append('      "english": "see",')
    lines.append('      "part_of_speech": "verb",')
    lines.append('      "dictionary_form": "videō, vidēre, vīdī, vīsum"')
    lines.append('    }')
    lines.append('  ]')
    lines.append('}')
    lines.append("```")
    lines.append("")

    lines.append("**IMPORTANT**: ")
    lines.append("- Return ONLY the JSON (no markdown code blocks, no explanations)")
    lines.append("- Dictionary forms: ")
    lines.append("  - Nouns: nominative, genitive, gender (puer, puerī, m.)")
    lines.append("  - Verbs: all principal parts (videō, vidēre, vīdī, vīsum)")
    lines.append("  - Adjectives: all genders (magnus, magna, magnum)")
    lines.append(f"- Art style for images: {project.image_config.art_style}")
    lines.append("")

    return "\n".join(lines)


def main():
    """Test prompt generation."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate AI prompts for book workflow')
    parser.add_argument('project_id', help='Project ID')
    parser.add_argument('step', choices=['translate', 'review'], help='Which prompt to generate')
    parser.add_argument('--output', '-o', help='Save to file')

    args = parser.parse_args()

    # Load project
    project = load_project(args.project_id)
    if not project:
        print(f"❌ Project '{args.project_id}' not found")
        sys.exit(1)

    # Load database
    db = LatinDatabase('data/lexicon.db')

    try:
        if args.step == 'translate':
            prompt = generate_translation_prompt(project, db)

            if args.output:
                Path(args.output).write_text(prompt, encoding='utf-8')
                print(f"✅ Translation prompt saved to {args.output}")
            else:
                print(prompt)

        elif args.step == 'review':
            # Need Latin text from translation folder
            latin_file = Path(project.project_folder) / 'translation' / 'latin_raw.txt'

            if not latin_file.exists():
                print(f"❌ Latin translation not found at {latin_file}")
                print("   Expected: projects/{project_id}/translation/latin_raw.txt")
                sys.exit(1)

            latin_text = latin_file.read_text(encoding='utf-8')

            # Optional: load English original
            english_file = Path(project.project_folder) / 'source' / 'story_english.txt'
            english_text = None
            if english_file.exists():
                english_text = english_file.read_text(encoding='utf-8')

            prompt = generate_review_prompt(project, latin_text, english_text)

            if args.output:
                Path(args.output).write_text(prompt, encoding='utf-8')
                print(f"✅ Review prompt saved to {args.output}")
            else:
                print(prompt)

    finally:
        db.close()


if __name__ == '__main__':
    main()
