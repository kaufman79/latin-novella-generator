#!/usr/bin/env python3
"""
List Stories Script - View all stories organized by level.
"""

import sys
import argparse
from pathlib import Path
from database import LatinDatabase


def list_stories_by_level(db):
    """List all stories organized by level."""
    cursor = db.conn.cursor()

    # Get all stories ordered by level and number
    stories = cursor.execute("""
        SELECT story_id, story_name, story_level, story_number, theme,
               total_words, unique_words, new_words_introduced,
               read_count, date_created, file_path
        FROM stories
        ORDER BY story_level, story_number
    """).fetchall()

    if not stories:
        print("\n📚 No stories found in database")
        print("   Ingest stories using: python scripts/ingest_story.py <file> --level 1 --number 1")
        return

    print("\n" + "="*80)
    print("📚 STORY LIBRARY")
    print("="*80)

    current_level = None
    level_stats = {}

    for story in stories:
        (story_id, name, level, number, theme, total_words, unique_words,
         new_words, read_count, date_created, file_path) = story

        # Track level for header
        if level != current_level:
            current_level = level

            # Show previous level stats
            if current_level > 1 and (current_level - 1) in level_stats:
                show_level_summary(current_level - 1, level_stats[current_level - 1])

            # New level header
            print(f"\n{'─'*80}")
            print(f"  📖 LEVEL {level}")
            print(f"{'─'*80}\n")

            level_stats[level] = {
                'total_stories': 0,
                'total_unique_words': set(),
                'total_new_words': 0
            }

        # Update level stats
        level_stats[level]['total_stories'] += 1
        level_stats[level]['total_new_words'] += new_words or 0

        # Display story
        number_display = f"{number}." if number else "—"
        theme_display = f"[{theme}]" if theme else ""

        print(f"{number_display:4s} {name:30s} {theme_display:15s}")
        print(f"     Words: {unique_words:3d} unique / {total_words:3d} total")
        if new_words:
            print(f"     New: {new_words} words not in database")
        print(f"     Read: {read_count}x")
        if file_path:
            print(f"     File: {file_path}")
        print()

    # Show final level stats
    if current_level and current_level in level_stats:
        show_level_summary(current_level, level_stats[current_level])

    # Overall summary
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY")
    print("="*80)

    total_stories = sum(s['total_stories'] for s in level_stats.values())
    total_levels = len(level_stats)

    print(f"\nTotal levels: {total_levels}")
    print(f"Total stories: {total_stories}")

    for level, stats in sorted(level_stats.items()):
        print(f"  Level {level}: {stats['total_stories']} stories, {stats['total_new_words']} new words introduced")

    print()


def show_level_summary(level, stats):
    """Show summary for a level."""
    print(f"{'─'*80}")
    print(f"  Level {level} Summary: {stats['total_stories']} stories, {stats['total_new_words']} new words")
    print()


def show_story_progression(db):
    """Show recommended story progression and what level to write next."""
    cursor = db.conn.cursor()

    # Get cumulative vocabulary per level
    levels = cursor.execute("""
        SELECT story_level, COUNT(*) as story_count,
               SUM(unique_words) as total_unique_vocab,
               SUM(new_words_introduced) as total_new_words
        FROM stories
        GROUP BY story_level
        ORDER BY story_level
    """).fetchall()

    if not levels:
        print("\n📈 No progression data yet")
        print("   Start with Level 1, Story 1")
        return

    print("\n" + "="*80)
    print("📈 STORY PROGRESSION")
    print("="*80)

    cumulative_vocab = 0

    for level, story_count, unique_vocab, new_words in levels:
        cumulative_vocab += new_words or 0

        print(f"\nLevel {level}:")
        print(f"  Stories completed: {story_count}")
        print(f"  Cumulative vocabulary: ~{cumulative_vocab} words")
        print(f"  Average unique words per story: {unique_vocab // story_count if story_count > 0 else 0}")

    # Suggest next story
    last_level = levels[-1][0]
    last_level_count = levels[-1][1]

    print("\n" + "─"*80)

    # Level progression guidelines
    guidelines = {
        1: {"target_stories": 10, "target_vocab": 50, "description": "Basic vocabulary (animals, family, actions)"},
        2: {"target_stories": 10, "target_vocab": 100, "description": "Add common verbs and adjectives"},
        3: {"target_stories": 15, "target_vocab": 200, "description": "Expand to everyday situations"},
        4: {"target_stories": 15, "target_vocab": 300, "description": "Introduction to past tense"},
    }

    if last_level in guidelines:
        guide = guidelines[last_level]
        if last_level_count < guide['target_stories']:
            print(f"\n💡 NEXT: Write Level {last_level}, Story {last_level_count + 1}")
            print(f"   Goal: {guide['description']}")
            print(f"   Progress: {last_level_count}/{guide['target_stories']} stories")
            print(f"   Target vocab: ~{guide['target_vocab']} cumulative words")
        else:
            print(f"\n💡 NEXT: Advance to Level {last_level + 1}, Story 1")
            if last_level + 1 in guidelines:
                next_guide = guidelines[last_level + 1]
                print(f"   Goal: {next_guide['description']}")
    else:
        print(f"\n💡 NEXT: Continue Level {last_level} or start Level {last_level + 1}")

    print()


def main():
    parser = argparse.ArgumentParser(description='List stories in the database')
    parser.add_argument(
        '--progression', '-p',
        action='store_true',
        help='Show story progression and recommendations'
    )

    args = parser.parse_args()

    db_path = 'data/lexicon.db'
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        sys.exit(1)

    db = LatinDatabase(db_path)

    try:
        if args.progression:
            show_story_progression(db)
        else:
            list_stories_by_level(db)
    finally:
        db.close()


if __name__ == '__main__':
    main()
