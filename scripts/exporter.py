"""
Export module for Latin Story Engine.
Handles export of batch plans and vocab lists to various formats.
"""

from typing import Dict, List
from pathlib import Path
from datetime import datetime


class BatchExporter:
    """Exports batch data to Markdown and other formats."""

    def __init__(self, export_dir: str = "exports"):
        """
        Initialize exporter.

        Args:
            export_dir: Directory for exported files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_batch_plan(self, batch_data: Dict, filename: str = None) -> Path:
        """
        Export batch plan to Markdown file.

        Args:
            batch_data: Batch dictionary from generator
            filename: Optional custom filename

        Returns:
            Path: Path to created file
        """
        if filename is None:
            batch_id = batch_data.get('batch_id', 'unknown')
            filename = f"batch_{batch_id:03d}_plan.md"

        filepath = self.export_dir / filename

        content = self._format_batch_plan_markdown(batch_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def export_vocab_list(
        self,
        batch_data: Dict,
        word_details: List[Dict],
        filename: str = None
    ) -> Path:
        """
        Export detailed vocabulary list to Markdown.

        Args:
            batch_data: Batch dictionary
            word_details: List of full word dictionaries from database
            filename: Optional custom filename

        Returns:
            Path: Path to created file
        """
        if filename is None:
            batch_id = batch_data.get('batch_id', 'unknown')
            filename = f"batch_{batch_id:03d}_vocab.md"

        filepath = self.export_dir / filename

        content = self._format_vocab_list_markdown(batch_data, word_details)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def export_vocab_csv(
        self,
        word_details: List[Dict],
        filename: str = None
    ) -> Path:
        """
        Export vocabulary to CSV format.

        Args:
            word_details: List of word dictionaries
            filename: Optional custom filename

        Returns:
            Path: Path to created file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"vocab_export_{timestamp}.csv"

        filepath = self.export_dir / filename

        # CSV header
        headers = [
            'latin_word', 'english_gloss', 'part_of_speech',
            'semantic_field', 'gesture_prompt', 'introduced_in_batch',
            'frequency_score', 'print_count'
        ]

        lines = [','.join(headers)]

        for word in word_details:
            row = [
                self._csv_escape(str(word.get(h, '')))
                for h in headers
            ]
            lines.append(','.join(row))

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return filepath

    def export_printable_flashcards(
        self,
        word_details: List[Dict],
        filename: str = None
    ) -> Path:
        """
        Export printable flashcard format (Markdown).

        Args:
            word_details: List of word dictionaries
            filename: Optional custom filename

        Returns:
            Path: Path to created file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"flashcards_{timestamp}.md"

        filepath = self.export_dir / filename

        content = self._format_flashcards_markdown(word_details)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath

    def _format_batch_plan_markdown(self, batch_data: Dict) -> str:
        """Format batch plan as Markdown."""
        lines = [
            f"# Batch {batch_data.get('batch_id', 'N/A')} — Story Plan",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## 📊 Batch Overview",
            "",
            f"- **Total Unique Words:** {batch_data.get('total_unique', 0)}",
            f"- **Reuse Percentage:** {batch_data.get('reuse_percentage', 0)}%",
            f"- **New Words:** {len(batch_data.get('new_words', []))}",
            f"- **Reused Words:** {len(batch_data.get('reused_words', []))}",
            "",
            "---",
            "",
            "## 🔄 Reused Vocabulary",
            "",
            self._format_word_list(batch_data.get('reused_words', [])),
            "",
            "## ✨ New Vocabulary",
            "",
            self._format_word_list(batch_data.get('new_words', [])),
            "",
            "---",
            "",
            "## 🎯 Semantic Focus",
            "",
        ]

        for field in batch_data.get('semantic_focus', []):
            lines.append(f"- **{field.title()}**")

        lines.extend([
            "",
            "---",
            "",
            "## 📖 Suggested Story Titles",
            "",
        ])

        for i, title in enumerate(batch_data.get('suggested_titles', []), 1):
            lines.append(f"{i}. **{title}**")

        lines.extend([
            "",
            "---",
            "",
            "## ✍️ Story Development Notes",
            "",
            "_Use this space to draft story ideas, plot points, and character actions._",
            "",
            "### Story 1:",
            "",
            "",
            "### Story 2:",
            "",
            "",
            "### Story 3:",
            "",
            "",
        ])

        return '\n'.join(lines)

    def _format_vocab_list_markdown(
        self,
        batch_data: Dict,
        word_details: List[Dict]
    ) -> str:
        """Format detailed vocabulary list as Markdown."""
        lines = [
            f"# Batch {batch_data.get('batch_id', 'N/A')} — Vocabulary Reference",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            "## Complete Vocabulary List",
            "",
            "| Latin | English | Part of Speech | Semantic Field | Gesture Prompt |",
            "|-------|---------|----------------|----------------|----------------|",
        ]

        for word in word_details:
            latin = word.get('latin_word', '')
            english = word.get('english_gloss', '')
            pos = word.get('part_of_speech', '')
            field = word.get('semantic_field', '')
            gesture = word.get('gesture_prompt', '')

            lines.append(
                f"| **{latin}** | {english} | {pos} | {field} | {gesture} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Vocabulary by Category",
            "",
        ])

        # Group by semantic field
        by_field = {}
        for word in word_details:
            field = word.get('semantic_field', 'general')
            if field not in by_field:
                by_field[field] = []
            by_field[field].append(word)

        for field, words in sorted(by_field.items()):
            lines.append(f"### {field.title()}")
            lines.append("")
            for word in words:
                lines.append(
                    f"- **{word['latin_word']}** — {word['english_gloss']}"
                )
            lines.append("")

        return '\n'.join(lines)

    def _format_flashcards_markdown(self, word_details: List[Dict]) -> str:
        """Format printable flashcards."""
        lines = [
            "# Latin Vocabulary Flashcards",
            "",
            f"**Print Date:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "_Cut along dotted lines. Fold in half for double-sided cards._",
            "",
            "---",
            "",
        ]

        for word in word_details:
            latin = word.get('latin_word', '')
            english = word.get('english_gloss', '')
            gesture = word.get('gesture_prompt', '')
            pos = word.get('part_of_speech', '')

            lines.extend([
                f"## {latin}",
                "",
                f"**Translation:** {english}",
                "",
                f"**Type:** {pos}",
                "",
                f"**Gesture:** {gesture}" if gesture else "",
                "",
                "---",
                "",
            ])

        return '\n'.join(lines)

    def _format_word_list(self, words: List[str]) -> str:
        """Format list of words as bullet points."""
        if not words:
            return "_No words_"

        return '\n'.join([f"- **{word}**" for word in words])

    def _csv_escape(self, value: str) -> str:
        """Escape CSV field value."""
        if ',' in value or '"' in value or '\n' in value:
            value = value.replace('"', '""')
            return f'"{value}"'
        return value


def export_full_batch(
    batch_data: Dict,
    word_details: List[Dict],
    export_dir: str = "exports"
) -> Dict[str, Path]:
    """
    Export all formats for a batch.

    Args:
        batch_data: Batch dictionary
        word_details: List of word dictionaries
        export_dir: Export directory

    Returns:
        dict: Map of format names to file paths
    """
    exporter = BatchExporter(export_dir)

    batch_id = batch_data.get('batch_id', 'unknown')

    return {
        'plan': exporter.export_batch_plan(batch_data),
        'vocab': exporter.export_vocab_list(batch_data, word_details),
        'csv': exporter.export_vocab_csv(
            word_details,
            filename=f"batch_{batch_id:03d}_vocab.csv"
        ),
        'flashcards': exporter.export_printable_flashcards(
            word_details,
            filename=f"batch_{batch_id:03d}_flashcards.md"
        )
    }
