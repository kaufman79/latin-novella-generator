#!/usr/bin/env python3
"""
Coverage dashboard for tracking vocabulary usage across stories.
Shows FF625 and DCC Core coverage, suggests vocabulary for next stories.
"""

import sys
from pathlib import Path
from database import LatinDatabase


def show_overall_statistics(db):
    """Show high-level database statistics."""
    print("\n" + "="*70)
    print("📊 OVERALL VOCABULARY STATISTICS")
    print("="*70)

    cursor = db.conn.cursor()

    # Total words in database
    total = cursor.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    print(f"\nTotal words in database: {total}")

    # Words by frequency tier
    tiers = cursor.execute("""
        SELECT frequency_tier, COUNT(*)
        FROM lexicon
        WHERE frequency_tier IS NOT NULL
        GROUP BY frequency_tier
        ORDER BY
            CASE frequency_tier
                WHEN 'ff625' THEN 1
                WHEN 'core' THEN 2
                WHEN 'common' THEN 3
                WHEN 'supplemental' THEN 4
            END
    """).fetchall()

    print("\nWords by frequency tier:")
    for tier, count in tiers:
        print(f"  {tier:15s}: {count:4d}")

    # Words from both lists
    overlap = cursor.execute("""
        SELECT COUNT(*)
        FROM lexicon
        WHERE ff625_rank IS NOT NULL AND dcc_rank IS NOT NULL
    """).fetchone()[0]
    print(f"\nWords in both FF625 and DCC: {overlap}")


def show_story_coverage(db):
    """Show how many words have been used in stories."""
    print("\n" + "="*70)
    print("📖 STORY COVERAGE")
    print("="*70)

    cursor = db.conn.cursor()

    # Words that have been used in stories
    used = cursor.execute("""
        SELECT COUNT(*)
        FROM lexicon
        WHERE frequency_score > 0
    """).fetchone()[0]

    total = cursor.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]

    percent = (used / total * 100) if total > 0 else 0
    print(f"\nWords used in stories: {used}/{total} ({percent:.1f}%)")

    # FF625 coverage
    ff625_used = cursor.execute("""
        SELECT COUNT(*)
        FROM lexicon
        WHERE ff625_rank IS NOT NULL AND frequency_score > 0
    """).fetchone()[0]

    ff625_total = cursor.execute("""
        SELECT COUNT(*)
        FROM lexicon
        WHERE ff625_rank IS NOT NULL
    """).fetchone()[0]

    ff625_percent = (ff625_used / ff625_total * 100) if ff625_total > 0 else 0
    print(f"\nFF625 coverage: {ff625_used}/{ff625_total} ({ff625_percent:.1f}%)")

    # DCC Core coverage by tier
    print("\nDCC Core coverage by tier:")
    for tier in ['core', 'common', 'supplemental']:
        tier_used = cursor.execute("""
            SELECT COUNT(*)
            FROM lexicon
            WHERE frequency_tier = ? AND frequency_score > 0
        """, (tier,)).fetchone()[0]

        tier_total = cursor.execute("""
            SELECT COUNT(*)
            FROM lexicon
            WHERE frequency_tier = ?
        """, (tier,)).fetchone()[0]

        tier_percent = (tier_used / tier_total * 100) if tier_total > 0 else 0
        print(f"  {tier:15s}: {tier_used:3d}/{tier_total:3d} ({tier_percent:.1f}%)")


def show_most_frequent_used(db, limit=20):
    """Show most frequently used words in stories."""
    print("\n" + "="*70)
    print(f"⭐ TOP {limit} MOST USED WORDS IN STORIES")
    print("="*70)

    cursor = db.conn.cursor()

    top_words = cursor.execute("""
        SELECT latin_word, english_gloss, frequency_score, frequency_tier
        FROM lexicon
        WHERE frequency_score > 0
        ORDER BY frequency_score DESC
        LIMIT ?
    """, (limit,)).fetchall()

    if not top_words:
        print("\n(No words used in stories yet)")
        return

    print("\n{:<20s} {:<30s} {:>6s} {:>12s}".format(
        "Latin", "English", "Uses", "Tier"
    ))
    print("-" * 70)

    for latin, english, score, tier in top_words:
        tier_display = tier or "custom"
        print(f"{latin:<20s} {english:<30s} {score:>6d} {tier_display:>12s}")


def show_unused_high_frequency(db, limit=30):
    """Show high-frequency words not yet used in stories."""
    print("\n" + "="*70)
    print(f"🎯 TOP {limit} UNUSED HIGH-FREQUENCY WORDS")
    print("="*70)

    cursor = db.conn.cursor()

    # Get unused FF625 words first
    ff625_unused = cursor.execute("""
        SELECT latin_word, english_gloss, ff625_rank, 'ff625' as source
        FROM lexicon
        WHERE ff625_rank IS NOT NULL AND frequency_score = 0
        ORDER BY ff625_rank
        LIMIT ?
    """, (limit,)).fetchall()

    # Get unused DCC Core words
    dcc_unused = cursor.execute("""
        SELECT latin_word, english_gloss, dcc_rank, 'dcc_core' as source
        FROM lexicon
        WHERE dcc_rank IS NOT NULL AND frequency_score = 0 AND ff625_rank IS NULL
        ORDER BY dcc_rank
        LIMIT ?
    """, (limit,)).fetchall()

    # Merge and sort by rank
    all_unused = sorted(
        ff625_unused + dcc_unused,
        key=lambda x: x[2]  # Sort by rank
    )[:limit]

    if not all_unused:
        print("\n✅ All high-frequency words have been used!")
        return

    print("\n{:<4s} {:<20s} {:<30s} {:<10s}".format(
        "Rank", "Latin", "English", "Source"
    ))
    print("-" * 70)

    for latin, english, rank, source in all_unused:
        print(f"{rank:<4d} {latin:<20s} {english:<30s} {source:<10s}")


def show_vocabulary_clusters(db):
    """Show semantic clusters of unused vocabulary."""
    print("\n" + "="*70)
    print("🔤 VOCABULARY CLUSTERS (Unused High-Frequency Words)")
    print("="*70)

    cursor = db.conn.cursor()

    # Get FF625 categories with unused words
    ff625_categories = cursor.execute("""
        SELECT ff625_category, COUNT(*) as unused_count
        FROM lexicon
        WHERE ff625_rank IS NOT NULL
          AND frequency_score = 0
          AND ff625_category IS NOT NULL
        GROUP BY ff625_category
        ORDER BY unused_count DESC
        LIMIT 10
    """).fetchall()

    if ff625_categories:
        print("\nFF625 Categories (top 10 by unused words):")
        for category, count in ff625_categories:
            print(f"  {category:20s}: {count:3d} unused words")

    # Get DCC semantic groups with unused words
    dcc_groups = cursor.execute("""
        SELECT dcc_semantic_group, COUNT(*) as unused_count
        FROM lexicon
        WHERE dcc_rank IS NOT NULL
          AND frequency_score = 0
          AND dcc_semantic_group IS NOT NULL
        GROUP BY dcc_semantic_group
        ORDER BY unused_count DESC
        LIMIT 10
    """).fetchall()

    if dcc_groups:
        print("\nDCC Semantic Groups (top 10 by unused words):")
        for group, count in dcc_groups:
            print(f"  {group:20s}: {count:3d} unused words")


def show_suggested_vocabulary(db, category=None, limit=15):
    """Suggest vocabulary for next story."""
    print("\n" + "="*70)
    if category:
        print(f"💡 SUGGESTED VOCABULARY: {category.upper()}")
    else:
        print("💡 SUGGESTED VOCABULARY FOR NEXT STORY")
    print("="*70)

    cursor = db.conn.cursor()

    if category:
        # Get unused words from specific category/group
        ff625_words = cursor.execute("""
            SELECT latin_word, english_gloss, part_of_speech, ff625_rank
            FROM lexicon
            WHERE ff625_category = ? AND frequency_score = 0
            ORDER BY ff625_rank
            LIMIT ?
        """, (category, limit)).fetchall()

        dcc_words = cursor.execute("""
            SELECT latin_word, english_gloss, part_of_speech, dcc_rank
            FROM lexicon
            WHERE dcc_semantic_group = ? AND frequency_score = 0 AND ff625_rank IS NULL
            ORDER BY dcc_rank
            LIMIT ?
        """, (category, limit)).fetchall()

        words = ff625_words + dcc_words
    else:
        # Get highest-priority unused words
        words = cursor.execute("""
            SELECT latin_word, english_gloss, part_of_speech,
                   COALESCE(ff625_rank, dcc_rank, 9999) as rank
            FROM lexicon
            WHERE frequency_score = 0
              AND (ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL)
            ORDER BY rank
            LIMIT ?
        """, (limit,)).fetchall()

    if not words:
        print(f"\nNo unused words found" + (f" in category '{category}'" if category else ""))
        return

    print("\n{:<20s} {:<30s} {:<15s}".format(
        "Latin", "English", "Part of Speech"
    ))
    print("-" * 70)

    for word_info in words[:limit]:
        latin, english, pos = word_info[0], word_info[1], word_info[2]
        pos_display = pos or "unknown"
        print(f"{latin:<20s} {english:<30s} {pos_display:<15s}")


def main():
    """Run the coverage dashboard."""
    db_path = 'data/lexicon.db'

    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        sys.exit(1)

    db = LatinDatabase(db_path)

    try:
        # Show all dashboard sections
        show_overall_statistics(db)
        show_story_coverage(db)
        show_most_frequent_used(db)
        show_unused_high_frequency(db)
        show_vocabulary_clusters(db)
        show_suggested_vocabulary(db)

        print("\n" + "="*70)
        print("✨ Dashboard complete!")
        print("="*70)

    finally:
        db.close()


if __name__ == '__main__':
    main()
