#!/usr/bin/env python3
"""
Import frequency lists into the database.
Handles both Fluent Forever 625 and DCC Latin Core lists.
"""

import csv
import sys
from pathlib import Path
from database import LatinDatabase

def import_fluent_forever_625(db, csv_file='data/frequency_lists/fluent_forever_625_latin.csv'):
    """Import Fluent Forever 625 list."""
    print("\n" + "="*60)
    print("Importing Fluent Forever 625...")
    print("="*60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    added = 0
    updated = 0

    for i, row in enumerate(rows, 1):
        latin = row['latin'].strip()
        english = row['english'].strip()
        category = row['category'].strip()
        part_of_speech = row['part_of_speech'].strip()
        notes = row['notes'].strip()

        # Check if word already exists
        existing = db.get_word_by_latin(latin)

        if existing:
            # Update existing word with FF625 info
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE lexicon
                SET ff625_rank = ?,
                    ff625_category = ?,
                    frequency_tier = 'ff625'
                WHERE id = ?
            """, (i, category, existing['id']))
            updated += 1
        else:
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

    print(f"✅ Added {added} new words")
    print(f"✅ Updated {updated} existing words")
    print(f"   Total FF625: {len(rows)}")


def import_dcc_latin_core(db, csv_file='data/frequency_lists/dcc_latin_core.csv'):
    """Import DCC Latin Core list."""
    print("\n" + "="*60)
    print("Importing DCC Latin Core...")
    print("="*60)

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    added = 0
    updated = 0

    for row in rows:
        headword = row['headword'].strip()
        definition = row['definition'].strip()
        part_of_speech = row['part_of_speech'].strip()
        semantic_group = row['semantic_group'].strip()
        frequency_rank = int(row['frequency_rank'])

        # Extract just the first Latin word from headword (may have forms)
        # e.g., "sum esse fuī futūrum" -> "sum"
        latin_base = headword.split()[0]

        # Check if word already exists (by matching the base form)
        existing = db.get_word_by_latin(latin_base)

        if existing:
            # Update with DCC info
            cursor = db.conn.cursor()
            cursor.execute("""
                UPDATE lexicon
                SET dcc_rank = ?,
                    dcc_semantic_group = ?
                WHERE id = ?
            """, (frequency_rank, semantic_group, existing['id']))

            # Update tier if not already FF625
            if not existing.get('ff625_rank'):
                tier = 'core' if frequency_rank <= 100 else 'common' if frequency_rank <= 500 else 'supplemental'
                cursor.execute("""
                    UPDATE lexicon
                    SET frequency_tier = ?
                    WHERE id = ?
                """, (tier, existing['id']))

            updated += 1
        else:
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
                morph_variants=headword  # Store full forms
            )
            added += 1

    db.conn.commit()

    print(f"✅ Added {added} new words")
    print(f"✅ Updated {updated} existing words")
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
    """Main import process."""
    db_path = 'data/lexicon.db'

    print(f"Opening database: {db_path}")
    db = LatinDatabase(db_path)

    # Add new columns if they don't exist
    print("\nAdding frequency tracking columns...")
    columns_to_add = [
        ("ff625_rank", "INTEGER"),
        ("ff625_category", "TEXT"),
        ("dcc_rank", "INTEGER"),
        ("dcc_semantic_group", "TEXT"),
        ("frequency_tier", "TEXT"),  # 'ff625', 'core', 'common', 'supplemental'
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor = db.conn.cursor()
            cursor.execute(f"ALTER TABLE lexicon ADD COLUMN {col_name} {col_type}")
            print(f"  Added column: {col_name}")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print(f"  Column {col_name} already exists")
            else:
                print(f"  Error adding {col_name}: {e}")

    db.conn.commit()

    # Import both lists
    import_fluent_forever_625(db)
    import_dcc_latin_core(db)

    # Show statistics
    show_statistics(db)

    db.close()
    print("\n✅ Import complete!")


if __name__ == '__main__':
    main()
