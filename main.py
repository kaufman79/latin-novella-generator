#!/usr/bin/env python3
"""
Latin Story Engine - Main CLI Interface
Interactive command-line tool for managing Latin vocabulary and generating story batches.
"""

import sys
import argparse
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.database import LatinDatabase
from scripts.generator import BatchGenerator, format_batch_summary
from scripts.exporter import BatchExporter, export_full_batch


def add_word_interactive(db: LatinDatabase):
    """Interactive word addition."""
    print("\n=== Add New Word to Lexicon ===\n")

    latin_word = input("Latin word (with macrons): ").strip()
    if not latin_word:
        print("❌ Latin word is required")
        return

    english_gloss = input("English translation: ").strip()
    if not english_gloss:
        print("❌ English translation is required")
        return

    part_of_speech = input("Part of speech (noun/verb/adj/adv): ").strip()
    semantic_field = input("Semantic field (motion/emotion/nature/family/etc): ").strip()
    action_level = input("Action level (physical/emotional/sensory/abstract): ").strip()
    gesture_prompt = input("Gesture prompt (optional): ").strip()
    story_hooks = input("Story hooks (optional): ").strip()

    try:
        word_id = db.add_word(
            latin_word=latin_word,
            english_gloss=english_gloss,
            part_of_speech=part_of_speech,
            semantic_field=semantic_field,
            action_level=action_level,
            gesture_prompt=gesture_prompt if gesture_prompt else None,
            story_hooks=story_hooks if story_hooks else None
        )
        print(f"\n✅ Word added successfully (ID: {word_id})")
    except Exception as e:
        print(f"\n❌ Error adding word: {e}")


def list_words(db: LatinDatabase, filter_unused: bool = False):
    """List all words in lexicon."""
    if filter_unused:
        words = db.get_unused_words()
        print("\n=== Unused Words ===\n")
    else:
        words = db.get_all_words()
        print("\n=== All Words in Lexicon ===\n")

    if not words:
        print("No words found.")
        return

    print(f"{'ID':<5} {'Latin':<15} {'English':<20} {'POS':<10} {'Field':<15} {'Batch':<8}")
    print("-" * 85)

    for word in words:
        batch = word.get('introduced_in_batch', '-')
        print(
            f"{word['id']:<5} "
            f"{word['latin_word']:<15} "
            f"{word['english_gloss']:<20} "
            f"{word.get('part_of_speech', ''):<10} "
            f"{word.get('semantic_field', ''):<15} "
            f"{str(batch):<8}"
        )

    print(f"\nTotal: {len(words)} words")


def show_stats(db: LatinDatabase):
    """Display database statistics."""
    stats = db.get_summary_stats()

    print("\n=== Latin Story Engine Statistics ===\n")
    print(f"Total Words in Lexicon:    {stats['total_words']}")
    print(f"Words Introduced:          {stats['introduced_words']}")
    print(f"Words Unused:              {stats['unused_words']}")
    print(f"Total Batches Generated:   {stats['total_batches']}")
    print(f"Average Word Reuse:        {stats['avg_reuse']:.2f}x")

    print("\nWords by Part of Speech:")
    for pos, count in stats['pos_distribution'].items():
        print(f"  {pos or 'unspecified':<15} {count:>3}")


def generate_batch_interactive(db: LatinDatabase):
    """Interactive batch generation."""
    generator = BatchGenerator(db)

    print("\n=== Generate New Batch ===\n")

    # Get parameters
    try:
        total_words = int(input("Total words per batch [15]: ").strip() or "15")
        reuse_ratio = float(input("Reuse ratio (0.0-1.0) [0.75]: ").strip() or "0.75")
    except ValueError:
        print("❌ Invalid input")
        return

    semantic_input = input("Semantic focus (comma-separated, optional): ").strip()
    semantic_focus = [s.strip() for s in semantic_input.split(',')] if semantic_input else None

    notes = input("Notes (optional): ").strip()

    print("\n⚙️  Generating batch...\n")

    try:
        batch_data, batch_id = generator.generate_and_save(
            total_words=total_words,
            reuse_ratio=reuse_ratio,
            semantic_focus=semantic_focus,
            notes=notes
        )

        print(format_batch_summary(batch_data))
        print(f"\n✅ Batch {batch_id} saved to database")

        # Ask about export
        export_choice = input("\nExport batch files? (y/n) [y]: ").strip().lower()
        if export_choice != 'n':
            export_batch(db, batch_data)

    except Exception as e:
        print(f"❌ Error generating batch: {e}")


def export_batch(db: LatinDatabase, batch_data: dict):
    """Export batch files."""
    print("\n⚙️  Exporting batch files...\n")

    # Get word details
    all_words = batch_data['reused_words'] + batch_data['new_words']
    word_details = []
    for word in all_words:
        word_data = db.get_word_by_latin(word)
        if word_data:
            word_details.append(word_data)

    try:
        files = export_full_batch(batch_data, word_details)

        print("✅ Files exported:")
        for fmt, path in files.items():
            print(f"  {fmt:<12} → {path}")

    except Exception as e:
        print(f"❌ Error exporting: {e}")


def list_batches(db: LatinDatabase):
    """List all batches."""
    batches = db.get_all_batches()

    print("\n=== Generated Batches ===\n")

    if not batches:
        print("No batches found.")
        return

    print(f"{'ID':<5} {'Date':<20} {'Total Words':<12} {'Semantic Focus':<30}")
    print("-" * 75)

    for batch in batches:
        print(
            f"{batch['batch_id']:<5} "
            f"{batch['date_created'][:19]:<20} "
            f"{batch['total_unique']:<12} "
            f"{batch.get('semantic_focus', ''):<30}"
        )

    print(f"\nTotal: {len(batches)} batches")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Latin Story Engine - Vocabulary and Batch Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--db',
        default='data/lexicon.db',
        help='Database file path (default: data/lexicon.db)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add word command
    subparsers.add_parser('add', help='Add a new word to the lexicon')

    # List words command
    list_parser = subparsers.add_parser('list', help='List words in lexicon')
    list_parser.add_argument('--unused', action='store_true', help='Show only unused words')

    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')

    # Generate batch command
    subparsers.add_parser('generate', help='Generate a new batch')

    # List batches command
    subparsers.add_parser('batches', help='List all batches')

    # Interactive mode
    subparsers.add_parser('interactive', help='Start interactive mode')

    args = parser.parse_args()

    # Initialize database
    db = LatinDatabase(args.db)

    try:
        if args.command == 'add':
            add_word_interactive(db)
        elif args.command == 'list':
            list_words(db, filter_unused=args.unused)
        elif args.command == 'stats':
            show_stats(db)
        elif args.command == 'generate':
            generate_batch_interactive(db)
        elif args.command == 'batches':
            list_batches(db)
        elif args.command == 'interactive':
            interactive_mode(db)
        else:
            parser.print_help()

    finally:
        db.close()


def interactive_mode(db: LatinDatabase):
    """Interactive menu mode."""
    while True:
        print("\n" + "="*50)
        print("Latin Story Engine - Interactive Mode")
        print("="*50)
        print("\n1. Add new word")
        print("2. List all words")
        print("3. List unused words")
        print("4. Show statistics")
        print("5. Generate new batch")
        print("6. List all batches")
        print("7. Exit")

        choice = input("\nSelect option (1-7): ").strip()

        if choice == '1':
            add_word_interactive(db)
        elif choice == '2':
            list_words(db, filter_unused=False)
        elif choice == '3':
            list_words(db, filter_unused=True)
        elif choice == '4':
            show_stats(db)
        elif choice == '5':
            generate_batch_interactive(db)
        elif choice == '6':
            list_batches(db)
        elif choice == '7':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == '__main__':
    main()
