#!/usr/bin/env python3
"""
Story Ingestion Script - Extract and track vocabulary from Latin stories.
"""

import sys
import re
from pathlib import Path
from collections import Counter
from datetime import datetime

from database import LatinDatabase
from lemmatizer import extract_latin_words_from_text, lemmatize_word, normalize_macrons

def ingest_story_file(story_path, db, story_name=None, level=None, story_number=None, theme=None):
    """
    Ingest a story from a markdown file.

    Args:
        story_path: Path to story markdown file
        db: LatinDatabase instance
        story_name: Optional story name (defaults to filename)
        level: Optional story level (1, 2, 3...)
        story_number: Optional story number within level
        theme: Optional theme/category
    """
    story_path = Path(story_path)

    if not story_path.exists():
        print(f"❌ File not found: {story_path}")
        return None

    # Read file
    with open(story_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Latin text section
    latin_text = extract_latin_section(content)

    if not latin_text:
        print(f"⚠️  No Latin text section found in {story_path.name}")
        print("   Looking for text between '### Latin Text' and next heading")
        latin_text = content  # Fall back to full content

    story_name = story_name or story_path.stem

    return ingest_story_text(
        latin_text, db, story_name,
        file_path=str(story_path),
        level=level,
        story_number=story_number,
        theme=theme
    )


def extract_latin_section(markdown_content):
    """Extract text between '### Latin Text' and next heading."""
    # Look for Latin text section
    pattern = r'###\s+Latin Text\s*\n(.*?)(?=\n###|\n##|$)'
    match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    # Alternative: look for section labeled "Latin"
    pattern = r'##\s+Latin\s*\n(.*?)(?=\n###|\n##|$)'
    match = re.search(pattern, markdown_content, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return None


def ingest_story_text(latin_text, db, story_name, file_path=None, level=None, story_number=None, theme=None):
    """
    Ingest Latin story text.

    Args:
        latin_text: Raw Latin text
        db: LatinDatabase instance
        story_name: Name of the story

    Returns:
        Dictionary with ingestion results
    """
    print(f"\n{'='*60}")
    print(f"Ingesting Story: {story_name}")
    print(f"{'='*60}\n")

    # Extract all Latin words
    words = extract_latin_words_from_text(latin_text)

    print(f"Extracted {len(words)} words (with repetitions)")

    # Count frequency
    word_freq = Counter(words)
    print(f"Found {len(word_freq)} unique word forms\n")

    # Lemmatize and look up each word
    results = {
        'story_name': story_name,
        'date_ingested': datetime.now().isoformat(),
        'total_words': len(words),
        'unique_forms': len(word_freq),
        'matched': [],
        'unmatched': [],
        'ff625_coverage': 0,
        'dcc_coverage': 0,
    }

    cursor = db.conn.cursor()

    print("Analyzing vocabulary...")
    print("-" * 60)

    for word_form, count in word_freq.most_common():
        # Lemmatize
        lemmas = lemmatize_word(word_form)

        if not lemmas:
            results['unmatched'].append((word_form, count, 'no_lemma'))
            continue

        lemma, pos = lemmas[0]  # Take first result

        # Look up in database (macron-insensitive)
        lemma_normalized = normalize_macrons(lemma)

        cursor.execute("""
            SELECT id, latin_word, english_gloss, ff625_rank, dcc_rank, frequency_tier
            FROM lexicon
            WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                latin_word, 'ā', 'a'), 'ē', 'e'), 'ī', 'i'), 'ō', 'o'), 'ū', 'u'))
            = LOWER(?)
        """, (lemma_normalized,))

        match = cursor.fetchone()

        if match:
            word_id, latin_word, gloss, ff_rank, dcc_rank, tier = match

            # Track match
            results['matched'].append({
                'form': word_form,
                'lemma': lemma,
                'db_entry': latin_word,
                'gloss': gloss,
                'count': count,
                'pos': pos,
                'ff625_rank': ff_rank,
                'dcc_rank': dcc_rank,
                'tier': tier
            })

            # Update stats
            if ff_rank:
                results['ff625_coverage'] += 1
            if dcc_rank:
                results['dcc_coverage'] += 1

            # Update database (track usage)
            # You could add columns like: story_appearances, last_seen_in_story, etc.
            # For now, just increment frequency_score
            cursor.execute("""
                UPDATE lexicon
                SET frequency_score = COALESCE(frequency_score, 0) + ?
                WHERE id = ?
            """, (count, word_id))

            print(f"  ✓ {word_form:15s} → {latin_word:15s} ({gloss:20s}) [{tier or 'unlisted'}]")

        else:
            results['unmatched'].append((word_form, count, lemma))
            print(f"  ? {word_form:15s} → {lemma:15s} (not in database)")

    db.conn.commit()

    # Summary
    print("\n" + "="*60)
    print("Ingestion Summary")
    print("="*60)
    print(f"Story: {story_name}")
    print(f"Total words (with repetition): {results['total_words']}")
    print(f"Unique word forms: {results['unique_forms']}")
    print(f"Matched in database: {len(results['matched'])}")
    print(f"Not in database: {len(results['unmatched'])}")

    if results['matched']:
        print(f"\nCoverage:")
        print(f"  FF625: {results['ff625_coverage']} words")
        print(f"  DCC Core: {results['dcc_coverage']} words")

        # Show tier breakdown
        tier_counts = Counter(m['tier'] for m in results['matched'] if m['tier'])
        if tier_counts:
            print(f"\nBy frequency tier:")
            for tier, count in tier_counts.most_common():
                print(f"  {tier:15s}: {count}")

    if results['unmatched']:
        print(f"\nWords not in database ({len(results['unmatched'])}):")
        for form, count, lemma in results['unmatched'][:10]:  # Show first 10
            print(f"  - {form} ({count}x) [lemma: {lemma}]")
        if len(results['unmatched']) > 10:
            print(f"  ... and {len(results['unmatched']) - 10} more")

    # Record story in stories table
    if level or story_number or file_path:
        cursor.execute("""
            INSERT OR REPLACE INTO stories
            (story_name, story_level, story_number, file_path, date_created,
             total_words, unique_words, new_words_introduced, theme, read_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            story_name,
            level or 1,
            story_number,
            file_path,
            datetime.now().isoformat(),
            results['total_words'],
            results['unique_forms'],
            len(results['unmatched']),  # Words not in database = new
            theme,
        ))
        db.conn.commit()

        if level and story_number:
            print(f"\n📚 Recorded as Level {level}, Story {story_number}")

    print("\n✅ Story ingestion complete!")

    return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Ingest Latin story and track vocabulary')
    parser.add_argument('story_file', help='Path to story markdown file')
    parser.add_argument('--name', help='Story name (defaults to filename)')
    parser.add_argument('--level', type=int, help='Story level (1, 2, 3...)')
    parser.add_argument('--number', type=int, help='Story number within level')
    parser.add_argument('--theme', help='Story theme/category (e.g., animals, family)')
    parser.add_argument('--text', action='store_true', help='Treat first arg as text instead of file')

    args = parser.parse_args()

    db = LatinDatabase('data/lexicon.db')

    try:
        if args.text:
            # Direct text input
            latin_text = args.story_file
            story_name = args.name or "Direct Input"
            ingest_story_text(
                latin_text, db, story_name,
                level=args.level,
                story_number=args.number,
                theme=args.theme
            )
        else:
            # File input
            ingest_story_file(
                args.story_file, db,
                story_name=args.name,
                level=args.level,
                story_number=args.number,
                theme=args.theme
            )
    finally:
        db.close()


if __name__ == '__main__':
    main()
