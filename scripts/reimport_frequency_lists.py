#!/usr/bin/env python3
"""
Re-import frequency lists with proper lemmatization and deduplication.
"""

import csv
import sys
from pathlib import Path
from database import LatinDatabase
from lemmatizer import extract_base_form, normalize_macrons

def import_fluent_forever_625(db, csv_file='data/frequency_lists/fluent_forever_625_latin.csv'):
    """Import Fluent Forever 625 list with lemmatization."""
    print("\n" + "="*60)
    print("Importing Fluent Forever 625...")
    print("="*60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    added = 0
    updated = 0
    skipped = 0

    for i, row in enumerate(rows, 1):
        latin = row['latin'].strip()
        english = row['english'].strip()
        category = row['category'].strip()
        part_of_speech = row['part_of_speech'].strip()
        notes = row['notes'].strip()

        # Normalize for searching (strip macrons)
        latin_normalized = normalize_macrons(latin)

        # Check if word already exists (case-insensitive, macron-insensitive)
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, latin_word FROM lexicon
            WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                latin_word, 'ā', 'a'), 'ē', 'e'), 'ī', 'i'), 'ō', 'o'), 'ū', 'u'))
            = LOWER(?)
        """, (latin_normalized,))

        existing = cursor.fetchone()

        if existing:
            # Update existing word with FF625 info
            cursor.execute("""
                UPDATE lexicon
                SET ff625_rank = ?,
                    ff625_category = ?,
                    frequency_tier = CASE
                        WHEN frequency_tier IS NULL THEN 'ff625'
                        ELSE frequency_tier
                    END
                WHERE id = ?
            """, (i, category, existing[0]))
            updated += 1
            print(f"  Updated: {latin} (matched {existing[1]})")
        else:
            # Check if this is a duplicate within FF625 itself
            if any(normalize_macrons(r['latin']) == latin_normalized for r in rows[:i-1]):
                skipped += 1
                print(f"  Skipped duplicate: {latin}")
                continue

            # Add new word
            db.add_word(
                latin_word=latin,
                english_gloss=english,
                part_of_speech=part_of_speech,
                semantic_field=category,
                story_hooks=notes,
                ff625_rank=i,
                ff625_category=category,
                frequency_tier='ff625'
            )
            added += 1

    db.conn.commit()

    print(f"\n✅ Added {added} new words")
    print(f"✅ Updated {updated} existing words")
    print(f"⏭️  Skipped {skipped} duplicates")
    print(f"   Total FF625: {len(rows)}")


def import_dcc_latin_core(db, csv_file='data/frequency_lists/dcc_latin_core.csv'):
    """Import DCC Latin Core list with lemmatization."""
    print("\n" + "="*60)
    print("Importing DCC Latin Core...")
    print("="*60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    added = 0
    updated = 0
    skipped = 0

    for row in rows:
        headword = row['headword'].strip()
        definition = row['definition'].strip()
        part_of_speech = row['part_of_speech'].strip()
        semantic_group = row['semantic_group'].strip()
        frequency_rank = int(row['frequency_rank'])

        # Extract base form (e.g., "currō currere cucurrī cursum" -> "currō")
        latin_base = extract_base_form(headword)
        latin_normalized = normalize_macrons(latin_base)

        # Check if word already exists
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, latin_word, ff625_rank FROM lexicon
            WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                latin_word, 'ā', 'a'), 'ē', 'e'), 'ī', 'i'), 'ō', 'o'), 'ū', 'u'))
            = LOWER(?)
        """, (latin_normalized,))

        existing = cursor.fetchone()

        if existing:
            # Update with DCC info
            cursor.execute("""
                UPDATE lexicon
                SET dcc_rank = ?,
                    dcc_semantic_group = ?,
                    morph_variants = ?
                WHERE id = ?
            """, (frequency_rank, semantic_group, headword, existing[0]))

            # Update tier if not already FF625
            if not existing[2]:  # ff625_rank is None
                tier = 'core' if frequency_rank <= 100 else 'common' if frequency_rank <= 500 else 'supplemental'
                cursor.execute("""
                    UPDATE lexicon
                    SET frequency_tier = ?
                    WHERE id = ?
                """, (tier, existing[0]))

            updated += 1
            if existing[1] != latin_base:
                print(f"  Updated: {latin_base} (matched {existing[1]})")
        else:
            # Check for duplicates within DCC list
            # Check if we've seen this normalized form already
            cursor.execute("""
                SELECT COUNT(*) FROM lexicon
                WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
                    latin_word, 'ā', 'a'), 'ē', 'e'), 'ī', 'i'), 'ō', 'o'), 'ū', 'u'))
                = LOWER(?)
            """, (latin_normalized,))

            if cursor.fetchone()[0] > 0:
                skipped += 1
                continue

            # Add new word
            tier = 'core' if frequency_rank <= 100 else 'common' if frequency_rank <= 500 else 'supplemental'

            db.add_word(
                latin_word=latin_base,
                english_gloss=definition,
                part_of_speech=part_of_speech,
                semantic_field=semantic_group,
                dcc_rank=frequency_rank,
                dcc_semantic_group=semantic_group,
                frequency_tier=tier,
                morph_variants=headword
            )
            added += 1

    db.conn.commit()

    print(f"\n✅ Added {added} new words")
    print(f"✅ Updated {updated} existing words")
    print(f"⏭️  Skipped {skipped} duplicates")
    print(f"   Total DCC Core: {len(rows)}")


def show_statistics(db):
    """Show import statistics."""
    print("\n" + "="*60)
    print("Database Statistics")
    print("="*60)

    cursor = db.conn.cursor()

    # Total words
    total = cursor.execute("SELECT COUNT(*) FROM lexicon").fetchone()[0]
    print(f"Total words: {total}")

    # By tier
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

    print("\nBy frequency tier:")
    for tier, count in tiers:
        print(f"  {tier:15s}: {count:4d}")

    # Words in both lists
    overlap = cursor.execute("""
        SELECT COUNT(*)
        FROM lexicon
        WHERE ff625_rank IS NOT NULL AND dcc_rank IS NOT NULL
    """).fetchone()[0]
    print(f"\nWords in both lists: {overlap}")

    # Show some overlap examples
    print("\nExample overlapping words:")
    examples = cursor.execute("""
        SELECT latin_word, english_gloss, ff625_rank, dcc_rank
        FROM lexicon
        WHERE ff625_rank IS NOT NULL AND dcc_rank IS NOT NULL
        ORDER BY dcc_rank
        LIMIT 10
    """).fetchall()

    for word, gloss, ff, dcc in examples:
        print(f"  {dcc:3d}. {word:15s} - {gloss:30s} (FF#{ff})")

    # Sample high-frequency words
    print("\nTop 10 words (by DCC rank):")
    top10 = cursor.execute("""
        SELECT latin_word, english_gloss, dcc_rank, ff625_rank
        FROM lexicon
        WHERE dcc_rank IS NOT NULL
        ORDER BY dcc_rank
        LIMIT 10
    """).fetchall()

    for word, gloss, dcc, ff in top10:
        ff_str = f"FF#{ff}" if ff else ""
        print(f"  {dcc:3d}. {word:20s} - {gloss:30s} {ff_str}")


def main():
    """Main re-import process."""
    db_path = 'data/lexicon.db'

    print(f"Opening database: {db_path}")
    db = LatinDatabase(db_path)

    print("\nClearing old frequency data...")
    cursor = db.conn.cursor()
    cursor.execute("DELETE FROM lexicon WHERE ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL")
    deleted = cursor.rowcount
    db.conn.commit()
    print(f"Deleted {deleted} old frequency list entries")

    # Re-import both lists
    import_fluent_forever_625(db)
    import_dcc_latin_core(db)

    # Show statistics
    show_statistics(db)

    db.close()
    print("\n✅ Re-import complete!")


if __name__ == '__main__':
    main()
