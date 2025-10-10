#!/usr/bin/env python3
"""
Integrated Story Prompt Generator - Combines vocabulary suggestions with AI prompt.
Generates a complete, copy-paste-ready prompt for Claude/ChatGPT.
"""

import sys
import argparse
from pathlib import Path
from database import LatinDatabase


def suggest_new_words(db, count=5, theme=None):
    """Suggest high-priority unused words."""
    cursor = db.conn.cursor()

    if theme:
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_tier
            FROM lexicon
            WHERE frequency_score = 0
              AND (ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL)
              AND (LOWER(ff625_category) LIKE ? OR LOWER(dcc_semantic_group) LIKE ?)
            ORDER BY COALESCE(ff625_rank, dcc_rank, 9999)
            LIMIT ?
        """
        theme_pattern = f"%{theme.lower()}%"
        words = cursor.execute(query, (theme_pattern, theme_pattern, count)).fetchall()
    else:
        query = """
            SELECT latin_word, english_gloss, part_of_speech, frequency_tier
            FROM lexicon
            WHERE frequency_score = 0
              AND (ff625_rank IS NOT NULL OR dcc_rank IS NOT NULL)
            ORDER BY COALESCE(ff625_rank, dcc_rank, 9999)
            LIMIT ?
        """
        words = cursor.execute(query, (count,)).fetchall()

    return words


def suggest_reuse_words(db, count=10):
    """Suggest previously-used words for reinforcement."""
    cursor = db.conn.cursor()

    query = """
        SELECT latin_word, english_gloss, part_of_speech, frequency_score
        FROM lexicon
        WHERE frequency_score > 0
        ORDER BY frequency_score DESC, RANDOM()
        LIMIT ?
    """
    return cursor.execute(query, (count,)).fetchall()


def get_system_prompt():
    """Load the AI story generation system prompt."""
    prompt_file = Path('stories/README.md')

    if not prompt_file.exists():
        return None

    with open(prompt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract just the system prompt (between triple backticks)
    import re
    match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return None


def generate_complete_prompt(new_words, reuse_words, theme=None, level=None, story_number=None):
    """Generate complete copy-paste-ready prompt."""
    lines = []

    # Get system prompt
    system_prompt = get_system_prompt()

    if not system_prompt:
        lines.append("# Latin Story Generation Prompt")
        lines.append("")
        lines.append("You are a Latin children's book author specializing in comprehensible input.")
        lines.append("Write simple Latin stories using ONLY the vocabulary provided below.")
        lines.append("")
    else:
        lines.append(system_prompt)
        lines.append("")

    lines.append("="*70)
    lines.append("")

    # Story metadata
    if level and story_number:
        lines.append(f"# STORY REQUEST: Level {level}, Story {story_number}")
    elif level:
        lines.append(f"# STORY REQUEST: Level {level}")
    else:
        lines.append("# STORY REQUEST")

    if theme:
        lines.append(f"**Theme:** {theme}")

    lines.append("")
    lines.append("="*70)
    lines.append("")

    # New vocabulary
    lines.append("## 🆕 NEW VOCABULARY TO INTRODUCE")
    lines.append("")
    lines.append("Use each of these words **8-12 times** in the story:")
    lines.append("")

    for i, (latin, english, pos, tier) in enumerate(new_words, 1):
        pos_display = pos or "—"
        tier_display = f"[{tier}]" if tier else ""
        lines.append(f"{i}. **{latin}** = {english} ({pos_display}) {tier_display}")

    lines.append("")

    # Reuse vocabulary
    if reuse_words:
        lines.append("## 🔄 REUSE VOCABULARY FOR REINFORCEMENT")
        lines.append("")
        lines.append("Include each of these words **2-5 times** in the story:")
        lines.append("")

        for i, (latin, english, pos, freq) in enumerate(reuse_words, 1):
            pos_display = pos or "—"
            lines.append(f"{i}. **{latin}** = {english} ({pos_display}) — used {freq}x before")

        lines.append("")

    # Instructions
    lines.append("="*70)
    lines.append("")
    lines.append("## INSTRUCTIONS")
    lines.append("")
    lines.append("1. Write 8-12 simple Latin sentences")
    lines.append("2. Use ONLY the vocabulary listed above")
    lines.append("3. Keep sentences SHORT (3-7 words)")
    lines.append("4. Repeat new words 8-12 times each")
    lines.append("5. Include reuse words 2-5 times each")
    lines.append("6. Focus on concrete actions and objects")
    lines.append("7. Make it fun and engaging for young children!")
    lines.append("")

    # Target ratio
    total_vocab = len(new_words) + len(reuse_words)
    new_percent = (len(new_words) / total_vocab * 100) if total_vocab > 0 else 0

    lines.append(f"**Vocabulary mix:** {len(reuse_words)} reuse ({100-new_percent:.0f}%) + {len(new_words)} new ({new_percent:.0f}%)")
    lines.append(f"**Target:** ~95% comprehensibility (mostly familiar words)")
    lines.append("")

    # Format reminder
    lines.append("="*70)
    lines.append("")
    lines.append("## OUTPUT FORMAT")
    lines.append("")
    lines.append("Please provide your response in this format:")
    lines.append("")
    lines.append("```")
    lines.append("## [Story Title in Latin] — [English Translation]")
    lines.append("")
    lines.append("### Latin Text")
    lines.append("[Your Latin story here, one sentence per line]")
    lines.append("")
    lines.append("### English Translation")
    lines.append("[English translation, matching sentence-by-sentence]")
    lines.append("")
    lines.append("### Vocabulary List")
    lines.append("| Latin | English | Part of Speech | Notes |")
    lines.append("|-------|---------|----------------|-------|")
    lines.append("| ... | ... | ... | ... |")
    lines.append("")
    lines.append("### Teaching Notes")
    lines.append("- **Gestures**: [Suggest 2-3 gestures]")
    lines.append("- **Emphasis**: [Which words to stress]")
    lines.append("```")
    lines.append("")
    lines.append("="*70)
    lines.append("")
    lines.append("📋 **COPY THIS ENTIRE PROMPT AND PASTE INTO CLAUDE/CHATGPT**")
    lines.append("")

    return "\n".join(lines)


def get_next_story_info(db):
    """Get next story level and number from database."""
    cursor = db.conn.cursor()

    # Get the highest level and story number
    result = cursor.execute("""
        SELECT MAX(story_level) as max_level,
               MAX(story_number) as max_number_in_level
        FROM stories
        WHERE story_level = (SELECT MAX(story_level) FROM stories)
    """).fetchone()

    if not result or result[0] is None:
        # No stories yet
        return 1, 1

    max_level, max_number = result

    # Level progression guidelines
    STORIES_PER_LEVEL = {
        1: 10,
        2: 10,
        3: 15,
        4: 15,
    }

    target_stories = STORIES_PER_LEVEL.get(max_level, 15)

    if max_number < target_stories:
        # Continue current level
        return max_level, max_number + 1
    else:
        # Advance to next level
        return max_level + 1, 1


def main():
    parser = argparse.ArgumentParser(
        description='Generate complete AI story prompt with vocabulary suggestions'
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
        help='Theme filter (e.g., animal, food, family)'
    )
    parser.add_argument(
        '--level', '-l',
        type=int,
        help='Story level (auto-detected if not specified)'
    )
    parser.add_argument(
        '--number',
        type=int,
        help='Story number within level (auto-detected if not specified)'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Save prompt to file instead of printing'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Auto-detect next level/number from database'
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
        # Auto-detect level and number if requested
        if args.auto or (not args.level and not args.number):
            level, story_number = get_next_story_info(db)
            print(f"🔍 Auto-detected: Level {level}, Story {story_number}")
        else:
            level = args.level
            story_number = args.number

        # Generate vocabulary suggestions
        print(f"\n📝 Generating prompt...")
        print(f"   Theme: {args.theme or 'any'}")
        print(f"   New words: {args.new}")
        print(f"   Reuse words: {args.reuse}")
        if level:
            print(f"   Level: {level}")
        if story_number:
            print(f"   Story number: {story_number}")
        print()

        new_words = suggest_new_words(db, args.new, args.theme)
        reuse_words = suggest_reuse_words(db, args.reuse)

        if not new_words and not reuse_words:
            print("⚠️  No vocabulary found matching criteria")
            return

        # Generate complete prompt
        prompt = generate_complete_prompt(
            new_words, reuse_words,
            theme=args.theme,
            level=level,
            story_number=story_number
        )

        # Output prompt
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            print(f"✅ Prompt saved to {output_path}")
            print(f"\n💡 Next steps:")
            print(f"   1. Open the file and copy its contents")
            print(f"   2. Paste into Claude/ChatGPT")
            print(f"   3. Wait for the story to be generated")
            print(f"   4. Save story and run: python scripts/ingest_story.py <file> --level {level} --number {story_number}")
        else:
            print(prompt)

    finally:
        db.close()


if __name__ == '__main__':
    main()
