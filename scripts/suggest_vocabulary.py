#!/usr/bin/env python3
"""
Vocabulary Suggestion Script - Generate word lists for story prompts.

This script helps you create AI story prompts by suggesting:
- High-priority unused words (to introduce)
- Previously-used words (for reinforcement/repetition)
- Balanced vocabulary based on semantic themes

Usage:
    python scripts/suggest_vocabulary.py --new 5 --reuse 10
    python scripts/suggest_vocabulary.py --theme food --new 8
    python scripts/suggest_vocabulary.py --level 1
"""

import sys
import argparse
from pathlib import Path
from database import LatinDatabase


def suggest_new_words(db, count=5, theme=None, level=None):
    """
    Suggest high-priority unused words to introduce.

    Args:
        db: LatinDatabase instance
        count: Number of new words to suggest
        theme: Optional semantic theme filter (e.g., 'food', 'motion')
        level: Optional level filter (only suggest words appropriate for this level)

    Returns:
        List of (latin_word, english_gloss, part_of_speech, tier) tuples
    """
    cursor = db.conn.cursor()

    # Build query based on filters
    if theme:
        # Search both FF625 categories and DCC semantic groups
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_tier,
                   COALESCE(ff625_rank, dcc_rank, 9999) as rank
            FROM lexicon
            WHERE frequency_score = 0
              AND (ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL)
              AND (LOWER(ff625_category) LIKE ? OR LOWER(dcc_semantic_group) LIKE ?)
            ORDER BY rank
            LIMIT ?
        """
        theme_pattern = f"%{theme.lower()}%"
        words = cursor.execute(query, (theme_pattern, theme_pattern, count)).fetchall()
    else:
        # Get highest-priority unused words (lowest rank numbers)
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_tier,
                   COALESCE(ff625_rank, dcc_rank, 9999) as rank
            FROM lexicon
            WHERE frequency_score = 0
              AND (ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL)
            ORDER BY rank
            LIMIT ?
        """
        words = cursor.execute(query, (count,)).fetchall()

    # Return without rank column
    return [(w[0], w[1], w[2], w[3]) for w in words]


def suggest_reuse_words(db, count=10, prioritize_recent=True):
    """
    Suggest previously-used words for reinforcement.

    Args:
        db: LatinDatabase instance
        count: Number of reuse words to suggest
        prioritize_recent: If True, favor recently-used words; if False, favor least-used

    Returns:
        List of (latin_word, english_gloss, part_of_speech, frequency_score) tuples
    """
    cursor = db.conn.cursor()

    if prioritize_recent:
        # Get words used in stories, prioritize those used more often (need reinforcement)
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_score
            FROM lexicon
            WHERE frequency_score > 0
            ORDER BY frequency_score DESC, RANDOM()
            LIMIT ?
        """
    else:
        # Get words used least often (at risk of being forgotten)
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_score
            FROM lexicon
            WHERE frequency_score > 0
            ORDER BY frequency_score ASC, RANDOM()
            LIMIT ?
        """

    return cursor.execute(query, (count,)).fetchall()


def get_available_themes(db):
    """Get list of available semantic themes from database."""
    cursor = db.conn.cursor()

    # Get FF625 categories
    ff625_themes = cursor.execute("""
        SELECT DISTINCT ff625_category
        FROM lexicon
        WHERE ff625_category IS NOT NULL
        ORDER BY ff625_category
    """).fetchall()

    # Get DCC semantic groups
    dcc_themes = cursor.execute("""
        SELECT DISTINCT dcc_semantic_group
        FROM lexicon
        WHERE dcc_semantic_group IS NOT NULL
        ORDER BY dcc_semantic_group
    """).fetchall()

    return [t[0] for t in ff625_themes + dcc_themes]


def generate_story_prompt(new_words, reuse_words, theme=None, level=None):
    """
    Generate a complete AI story prompt with vocabulary lists.

    Args:
        new_words: List of new word tuples
        reuse_words: List of reuse word tuples
        theme: Optional theme description
        level: Optional story level

    Returns:
        Formatted prompt string
    """
    prompt = []

    # Header
    prompt.append("=" * 70)
    if level:
        prompt.append(f"📖 LATIN STORY PROMPT - LEVEL {level}")
    else:
        prompt.append("📖 LATIN STORY PROMPT")
    prompt.append("=" * 70)
    prompt.append("")

    if theme:
        prompt.append(f"**Theme:** {theme}")
        prompt.append("")

    # Instructions
    prompt.append("Please generate a pedagogically-sound Latin story using the vocabulary")
    prompt.append("below. Follow the guidelines in stories/README.md:")
    prompt.append("")
    prompt.append("- Simple sentences (3-7 words)")
    prompt.append("- Present tense focus")
    prompt.append("- Concrete, action-based vocabulary")
    prompt.append("- Heavy repetition of new words (8-12 times each)")
    prompt.append("- Include reuse words for reinforcement")
    prompt.append("")

    # New vocabulary to introduce
    prompt.append("## 🆕 NEW VOCABULARY (introduce these words)")
    prompt.append("")
    prompt.append("| Latin | English | Part of Speech | Priority |")
    prompt.append("|-------|---------|----------------|----------|")

    for latin, english, pos, tier in new_words:
        pos_display = pos or "—"
        tier_display = tier or "—"
        prompt.append(f"| {latin} | {english} | {pos_display} | {tier_display} |")

    prompt.append("")
    prompt.append(f"**Goal:** Use each new word 8-12 times in the story.")
    prompt.append("")

    # Reuse vocabulary
    if reuse_words:
        prompt.append("## 🔄 REUSE VOCABULARY (reinforce these words)")
        prompt.append("")
        prompt.append("| Latin | English | Part of Speech | Previous Uses |")
        prompt.append("|-------|---------|----------------|---------------|")

        for latin, english, pos, freq_score in reuse_words:
            pos_display = pos or "—"
            prompt.append(f"| {latin} | {english} | {pos_display} | {freq_score} |")

        prompt.append("")
        prompt.append(f"**Goal:** Use each reuse word 2-5 times in the story.")
        prompt.append("")

    # Footer
    total_vocab = len(new_words) + len(reuse_words)
    new_percent = (len(new_words) / total_vocab * 100) if total_vocab > 0 else 0

    prompt.append("---")
    prompt.append("")
    prompt.append(f"**Total vocabulary:** {total_vocab} words")
    prompt.append(f"**New words:** {len(new_words)} ({new_percent:.0f}%)")
    prompt.append(f"**Reuse words:** {len(reuse_words)} ({100-new_percent:.0f}%)")
    prompt.append("")
    prompt.append("**Target:** 95% comprehensibility (mostly reuse words)")
    prompt.append("")
    prompt.append("=" * 70)

    return "\n".join(prompt)


def main():
    parser = argparse.ArgumentParser(
        description="Generate vocabulary suggestions for Latin story prompts"
    )
    parser.add_argument(
        '--new', '-n',
        type=int,
        default=5,
        help='Number of new words to introduce (default: 5)'
    )
    parser.add_argument(
        '--reuse', '-r',
        type=int,
        default=10,
        help='Number of reuse words for reinforcement (default: 10)'
    )
    parser.add_argument(
        '--theme', '-t',
        type=str,
        help='Semantic theme filter (e.g., food, motion, family)'
    )
    parser.add_argument(
        '--level', '-l',
        type=int,
        help='Story level (affects word difficulty)'
    )
    parser.add_argument(
        '--list-themes',
        action='store_true',
        help='List available themes and exit'
    )
    parser.add_argument(
        '--prioritize-recent',
        action='store_true',
        default=True,
        help='Prioritize recently-used words for reuse (default: True)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save prompt to file instead of printing to stdout'
    )

    args = parser.parse_args()

    # Connect to database
    db_path = 'data/lexicon.db'
    if not Path(db_path).exists():
        print(f"❌ Database not found at {db_path}")
        print("   Run 'python scripts/import_frequency_lists.py' first")
        sys.exit(1)

    db = LatinDatabase(db_path)

    try:
        # List themes if requested
        if args.list_themes:
            themes = get_available_themes(db)
            print("\n📚 Available Themes:\n")
            for theme in themes:
                print(f"  - {theme}")
            print()
            return

        # Generate vocabulary suggestions
        print(f"\n🔍 Generating vocabulary suggestions...")
        print(f"   New words: {args.new}")
        print(f"   Reuse words: {args.reuse}")
        if args.theme:
            print(f"   Theme: {args.theme}")
        if args.level:
            print(f"   Level: {args.level}")
        print()

        new_words = suggest_new_words(db, args.new, args.theme, args.level)
        reuse_words = suggest_reuse_words(db, args.reuse, args.prioritize_recent)

        if not new_words and not reuse_words:
            print("⚠️  No vocabulary found matching criteria")
            return

        # Generate prompt
        prompt = generate_story_prompt(new_words, reuse_words, args.theme, args.level)

        # Output prompt
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"✅ Prompt saved to {output_path}")
        else:
            print(prompt)

    finally:
        db.close()


if __name__ == '__main__':
    main()
