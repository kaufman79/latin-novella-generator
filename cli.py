#!/usr/bin/env python3
"""
Latin Story Engine - Main CLI
Simple command interface for the entire workflow.
"""

import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Latin Story Engine - Create and track Latin children\'s stories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate prompt for next story
  %(prog)s prompt --auto --theme animal

  # Ingest a completed story
  %(prog)s ingest stories/level_1/story_02.md --level 1 --number 2 --theme animal

  # Check progress
  %(prog)s progress

  # View story library
  %(prog)s list

  # Check vocabulary coverage
  %(prog)s coverage
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # PROMPT command
    prompt_parser = subparsers.add_parser('prompt', help='Generate AI story prompt')
    prompt_parser.add_argument('--auto', action='store_true', help='Auto-detect next level/number')
    prompt_parser.add_argument('--new', '-n', type=int, default=5, help='Number of new words (default: 5)')
    prompt_parser.add_argument('--reuse', '-r', type=int, default=10, help='Number of reuse words (default: 10)')
    prompt_parser.add_argument('--theme', '-t', help='Theme (animal, food, family, etc.)')
    prompt_parser.add_argument('--level', '-l', type=int, help='Story level')
    prompt_parser.add_argument('--number', type=int, help='Story number')
    prompt_parser.add_argument('--output', '-o', help='Save to file')

    # INGEST command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest story and track vocabulary')
    ingest_parser.add_argument('story_file', help='Path to story markdown file')
    ingest_parser.add_argument('--level', '-l', type=int, help='Story level')
    ingest_parser.add_argument('--number', '-n', type=int, help='Story number')
    ingest_parser.add_argument('--theme', '-t', help='Story theme')
    ingest_parser.add_argument('--name', help='Story name (defaults to filename)')

    # LIST command
    list_parser = subparsers.add_parser('list', help='List all stories')

    # PROGRESS command
    progress_parser = subparsers.add_parser('progress', help='Show story progression')

    # COVERAGE command
    coverage_parser = subparsers.add_parser('coverage', help='Show vocabulary coverage dashboard')

    # SETUP command (now just creates database)
    setup_parser = subparsers.add_parser('setup', help='Initialize database')

    # BOOK COMMANDS
    book_new_parser = subparsers.add_parser('book-new', help='Create new book project')
    book_new_parser.add_argument('title', help='Book title in English')
    book_new_parser.add_argument('--theme', '-t', help='Theme (animal, family, food, etc.)')
    book_new_parser.add_argument('--pages', '-p', type=int, default=10, help='Target pages (default: 10)')
    book_new_parser.add_argument('--level', '-l', type=int, help='Story level')
    book_new_parser.add_argument('--style', help='Art style description')

    book_translate_parser = subparsers.add_parser('book-translate', help='Generate translation prompt')
    book_translate_parser.add_argument('project_id', help='Project ID')
    book_translate_parser.add_argument('--output', '-o', help='Save prompt to file')

    book_review_parser = subparsers.add_parser('book-review', help='Generate review/pagination prompt')
    book_review_parser.add_argument('project_id', help='Project ID')
    book_review_parser.add_argument('--output', '-o', help='Save prompt to file')

    book_images_parser = subparsers.add_parser('book-images', help='Generate images from Nano Banana')
    book_images_parser.add_argument('project_id', help='Project ID')

    book_pdf_parser = subparsers.add_parser('book-pdf', help='Build PDF from images and text')
    book_pdf_parser.add_argument('project_id', help='Project ID')

    book_approve_parser = subparsers.add_parser('book-approve', help='Approve book and update database')
    book_approve_parser.add_argument('project_id', help='Project ID')

    book_list_parser = subparsers.add_parser('book-list', help='List all book projects')

    book_status_parser = subparsers.add_parser('book-status', help='Show book project status')
    book_status_parser.add_argument('project_id', help='Project ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to appropriate script
    if args.command == 'prompt':
        cmd = ['python3', 'scripts/generate_prompt.py']
        if args.auto:
            cmd.append('--auto')
        if args.new:
            cmd.extend(['--new', str(args.new)])
        if args.reuse:
            cmd.extend(['--reuse', str(args.reuse)])
        if args.theme:
            cmd.extend(['--theme', args.theme])
        if args.level:
            cmd.extend(['--level', str(args.level)])
        if args.number:
            cmd.extend(['--number', str(args.number)])
        if args.output:
            cmd.extend(['--output', args.output])

        import subprocess
        subprocess.run(cmd)

    elif args.command == 'ingest':
        cmd = ['python3', 'scripts/ingest_story.py', args.story_file]
        if args.level:
            cmd.extend(['--level', str(args.level)])
        if args.number:
            cmd.extend(['--number', str(args.number)])
        if args.theme:
            cmd.extend(['--theme', args.theme])
        if args.name:
            cmd.extend(['--name', args.name])

        import subprocess
        subprocess.run(cmd)

    elif args.command == 'list':
        import subprocess
        subprocess.run(['python3', 'scripts/list_stories.py'])

    elif args.command == 'progress':
        import subprocess
        subprocess.run(['python3', 'scripts/list_stories.py', '--progression'])

    elif args.command == 'coverage':
        import subprocess
        subprocess.run(['python3', 'scripts/coverage_dashboard.py'])

    elif args.command == 'setup':
        print("🚀 Initializing database...\n")
        from scripts.database import LatinDatabase
        db = LatinDatabase('data/lexicon.db')
        db.close()
        print("✅ Database created!")
        print("\n💡 Next steps:")
        print("   1. Run the Streamlit app: ./run_app.sh")
        print("   2. Add known words in the 'Vocabulary Database' tab")
        print("   3. Create your first book!")

    # BOOK COMMANDS
    elif args.command == 'book-new':
        from scripts.book_manager import create_project, show_project_status
        project = create_project(
            title=args.title,
            theme=args.theme,
            pages=args.pages,
            level=args.level,
            art_style=args.style
        )
        print(f"\n✅ Created book project: {project.project_id}")
        show_project_status(project)
        print("\n💡 Next step: python cli.py book-translate", project.project_id)

    elif args.command == 'book-translate':
        import subprocess
        cmd = ['python3', 'scripts/generate_book_prompts.py', args.project_id, 'translate']
        if args.output:
            cmd.extend(['--output', args.output])
        subprocess.run(cmd)

    elif args.command == 'book-review':
        import subprocess
        cmd = ['python3', 'scripts/generate_book_prompts.py', args.project_id, 'review']
        if args.output:
            cmd.extend(['--output', args.output])
        subprocess.run(cmd)

    elif args.command == 'book-images':
        import subprocess
        subprocess.run(['python3', 'scripts/image_generator.py', args.project_id])

    elif args.command == 'book-pdf':
        import subprocess
        subprocess.run(['python3', 'scripts/pdf_builder.py', args.project_id])

    elif args.command == 'book-approve':
        print("✅ Approving book...")
        print("⚠️  Approval workflow not yet implemented")
        print("   TODO: Implement database update with approval")

    elif args.command == 'book-list':
        from scripts.book_manager import list_all_projects
        projects = list_all_projects()
        if not projects:
            print("\n📚 No book projects found")
            print("   Create one with: python cli.py book-new \"Title\"")
        else:
            print("\n📚 BOOK PROJECTS")
            print("=" * 70)
            for p in projects:
                status_emoji = {
                    'initialized': '🆕',
                    'translated': '📝',
                    'reviewed': '✅',
                    'images_generated': '🎨',
                    'pdf_built': '📄',
                    'approved': '✨'
                }.get(p.status, '❓')
                print(f"{status_emoji} {p.project_id:30s} - {p.title_english:30s} [{p.status}]")
            print()

    elif args.command == 'book-status':
        from scripts.book_manager import load_project, show_project_status
        project = load_project(args.project_id)
        if not project:
            print(f"❌ Project '{args.project_id}' not found")
            sys.exit(1)
        show_project_status(project)


if __name__ == '__main__':
    main()
