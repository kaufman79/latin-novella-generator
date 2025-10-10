#!/usr/bin/env python3
"""
Create Batch 0 from existing story vocabulary.
This establishes baseline vocabulary that the child has already been exposed to.
"""

import sys
from pathlib import Path
from typing import Dict, List
from database import LatinDatabase


def load_extracted_vocabulary(vocab_file: Path) -> Dict[str, Dict]:
    """
    Load vocabulary from extracted text file.

    Args:
        vocab_file: Path to vocabulary file (format: word|translation|frequency)

    Returns:
        Dictionary of {word: {'translation': str, 'frequency': int}}
    """
    vocab = {}

    with open(vocab_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse word|translation|frequency
            parts = line.split('|')
            if len(parts) == 3:
                word, translation, freq = parts
                vocab[word.strip()] = {
                    'translation': translation.strip(),
                    'frequency': int(freq.strip())
                }

    return vocab


def create_batch_zero(vocab: Dict[str, Dict], db_path: str = 'data/lexicon.db'):
    """
    Create Batch 0 from extracted vocabulary.

    Args:
        vocab: Dictionary of {word: {'translation': str, 'frequency': int}}
        db_path: Path to database
    """
    db = LatinDatabase(db_path)

    print(f"\n{'='*60}")
    print("📦 Creating Batch 0 (Baseline Vocabulary)")
    print(f"{'='*60}\n")

    added_to_db = 0
    already_existed = 0
    batch_zero_words = []

    print("📝 Adding words to lexicon...\n")

    # Sort by frequency descending
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1]['frequency'], reverse=True)

    for word, data in sorted_vocab:
        translation = data['translation']
        freq = data['frequency']

        # Check if word already exists
        existing = db.get_word_by_latin(word)

        if existing:
            print(f"  ⏭️  '{word}' already exists (skipping)")
            already_existed += 1
            batch_zero_words.append(word)
            continue

        # Add new word to lexicon with translation
        try:
            word_id = db.add_word(
                latin_word=word,
                english_gloss=translation,
                part_of_speech="[needs classification]",  # Still need to classify
                semantic_field="baseline",
                frequency_score=freq,
                print_count=freq  # Word appeared freq times in existing books
            )

            print(f"  ✅ Added '{word}' ({translation}) — freq: {freq}x → ID {word_id}")
            added_to_db += 1
            batch_zero_words.append(word)

        except Exception as e:
            print(f"  ❌ Error adding '{word}': {e}")

    # Create Batch 0 record
    print(f"\n{'='*60}")
    print("📊 Creating Batch 0 Record")
    print(f"{'='*60}\n")

    batch_id = db.create_batch(
        new_words=batch_zero_words,
        reused_words=[],
        semantic_focus=['baseline', 'existing_stories'],
        suggested_titles=[],
        notes="Baseline vocabulary extracted from existing Latin storybooks. "
              "Child has been exposed to these words already."
    )

    # Update all words to mark as introduced in Batch 0
    print("🔄 Updating word records...\n")

    for word in batch_zero_words:
        word_data = db.get_word_by_latin(word)
        if word_data:
            db.update_word_usage(word_data['id'], batch_id)

    db.close()

    # Print summary
    print(f"\n{'='*60}")
    print("✅ BATCH 0 CREATED SUCCESSFULLY")
    print(f"{'='*60}\n")

    print(f"📊 Summary:")
    print(f"  Batch ID: {batch_id}")
    print(f"  New words added to database: {added_to_db}")
    print(f"  Words already in database: {already_existed}")
    print(f"  Total Batch 0 vocabulary: {len(batch_zero_words)}")

    print(f"\n📝 Next Steps:")
    print(f"  1. Review vocabulary: python main.py list")
    print(f"  2. Add English translations manually (optional)")
    print(f"  3. Generate Batch 1: python main.py generate")
    print(f"\n  ⚠️  Note: New batches will automatically prioritize")
    print(f"     reusing words from Batch 0 (familiar vocabulary)")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create Batch 0 from extracted vocabulary"
    )

    parser.add_argument(
        'vocab_file',
        help='Path to extracted vocabulary file',
        nargs='?',
        default='data/extracted_vocabulary.txt'
    )

    parser.add_argument(
        '--db',
        help='Database path',
        default='data/lexicon.db'
    )

    args = parser.parse_args()

    vocab_file = Path(args.vocab_file)

    if not vocab_file.exists():
        print(f"❌ Vocabulary file not found: {vocab_file}")
        print(f"\n💡 Run OCR extraction first:")
        print(f"   python scripts/ocr_extractor.py existing_stories/")
        sys.exit(1)

    # Load vocabulary
    print(f"📖 Loading vocabulary from: {vocab_file}")
    vocab = load_extracted_vocabulary(vocab_file)

    print(f"   Found {len(vocab)} unique words")
    total_instances = sum(data['frequency'] for data in vocab.values())
    print(f"   Total instances: {total_instances}")

    # Confirm
    response = input(f"\n❓ Create Batch 0 with {len(vocab)} words? (y/n) [y]: ").strip().lower()

    if response and response != 'y':
        print("❌ Cancelled")
        sys.exit(0)

    # Create Batch 0
    create_batch_zero(vocab, db_path=args.db)


if __name__ == '__main__':
    main()
