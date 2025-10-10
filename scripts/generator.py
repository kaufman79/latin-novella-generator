"""
Batch generation module for Latin Story Engine.
Implements intelligent vocabulary selection with reuse logic.
"""

import random
from typing import List, Dict, Optional, Tuple
from collections import Counter
from .database import LatinDatabase


class BatchGenerator:
    """Generates vocabulary batches with intelligent word reuse."""

    def __init__(self, db: LatinDatabase):
        """
        Initialize generator with database connection.

        Args:
            db: LatinDatabase instance
        """
        self.db = db

    def generate_batch(
        self,
        reuse_ratio: float = 0.75,
        total_words: int = 15,
        semantic_focus: Optional[List[str]] = None,
        prioritize_recent: int = 3
    ) -> Dict:
        """
        Generate a new vocabulary batch with intelligent reuse.

        Args:
            reuse_ratio: Percentage of words to reuse (0.75 = 75%)
            total_words: Total words in batch
            semantic_focus: Optional list of semantic fields to prioritize
            prioritize_recent: Number of recent batches to prioritize for reuse

        Returns:
            dict: {
                'batch_id': int,
                'reused_words': list,
                'new_words': list,
                'total_unique': int,
                'semantic_focus': list,
                'suggested_titles': list,
                'reuse_percentage': float
            }
        """
        # Calculate word counts
        reuse_count = int(total_words * reuse_ratio)
        new_count = total_words - reuse_count

        # Get candidate pools
        recent_words = self.db.get_recent_words(n_batches=prioritize_recent)
        unused_words = self.db.get_unused_words()

        # Select reused words
        reused = self._select_reuse_words(recent_words, reuse_count)

        # Select new words
        new = self._select_new_words(
            unused_words,
            new_count,
            semantic_focus,
            existing_words=reused
        )

        # Combine and analyze
        all_words = reused + new
        semantic_fields = self._analyze_semantic_fields(all_words)

        # Generate story suggestions
        titles = self._suggest_story_titles(all_words, semantic_fields)

        # Get next batch ID
        next_batch_id = self.db.get_latest_batch_id() + 1

        return {
            'batch_id': next_batch_id,
            'reused_words': [w['latin_word'] for w in reused],
            'new_words': [w['latin_word'] for w in new],
            'total_unique': len(all_words),
            'semantic_focus': semantic_fields[:3],  # Top 3 semantic fields
            'suggested_titles': titles,
            'reuse_percentage': round((len(reused) / len(all_words)) * 100, 1)
        }

    def _select_reuse_words(self, candidates: List[Dict], count: int) -> List[Dict]:
        """
        Select words to reuse based on frequency and strategic importance.

        Args:
            candidates: Pool of recently used words
            count: Number of words to select

        Returns:
            List of selected word dictionaries
        """
        if not candidates:
            return []

        # If not enough candidates, return all
        if len(candidates) <= count:
            return candidates

        # Score words by frequency and recency
        scored = []
        for word in candidates:
            score = word['frequency_score'] * 2 + word['print_count']
            scored.append((word, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Take top performers with some randomization
        # Top 60% guaranteed, remaining 40% random from pool
        guaranteed = int(count * 0.6)
        random_pool_size = min(count * 2, len(scored))

        selected = [w for w, s in scored[:guaranteed]]

        # Add random selections from next tier
        remaining_needed = count - len(selected)
        if remaining_needed > 0:
            pool = [w for w, s in scored[guaranteed:random_pool_size]]
            selected.extend(random.sample(pool, min(remaining_needed, len(pool))))

        return selected[:count]

    def _select_new_words(
        self,
        candidates: List[Dict],
        count: int,
        semantic_focus: Optional[List[str]] = None,
        existing_words: List[Dict] = None
    ) -> List[Dict]:
        """
        Select new words with semantic field balancing.

        Args:
            candidates: Pool of unused words
            count: Number of words to select
            semantic_focus: Optional semantic fields to prioritize
            existing_words: Already selected words (for balance)

        Returns:
            List of selected word dictionaries
        """
        if not candidates:
            return []

        if len(candidates) <= count:
            return candidates

        # Analyze existing semantic distribution
        existing_fields = Counter()
        if existing_words:
            for word in existing_words:
                if word.get('semantic_field'):
                    existing_fields[word['semantic_field']] += 1

        # Filter by semantic focus if provided
        if semantic_focus:
            focused = [
                w for w in candidates
                if w.get('semantic_field') in semantic_focus
            ]
            # Use focused pool if sufficient
            if len(focused) >= count:
                candidates = focused

        # Balance selection across semantic fields
        selected = []
        remaining = candidates.copy()

        # Diversify by semantic field
        while len(selected) < count and remaining:
            # Find underrepresented fields
            field_counts = Counter(existing_fields)
            for word in selected:
                if word.get('semantic_field'):
                    field_counts[word['semantic_field']] += 1

            # Sort remaining by field rarity
            def field_priority(word):
                field = word.get('semantic_field', 'unknown')
                return (field_counts[field], random.random())

            remaining.sort(key=field_priority)

            # Select next word
            selected.append(remaining.pop(0))

        return selected[:count]

    def _analyze_semantic_fields(self, words: List[Dict]) -> List[str]:
        """
        Analyze and rank semantic fields in word list.

        Args:
            words: List of word dictionaries

        Returns:
            List of semantic fields, ordered by frequency
        """
        fields = [
            w.get('semantic_field', 'general')
            for w in words
            if w.get('semantic_field')
        ]

        field_counts = Counter(fields)
        return [field for field, count in field_counts.most_common()]

    def _suggest_story_titles(
        self,
        words: List[Dict],
        semantic_fields: List[str]
    ) -> List[str]:
        """
        Generate story title suggestions based on vocabulary.

        Args:
            words: List of word dictionaries
            semantic_fields: Dominant semantic fields

        Returns:
            List of suggested story titles
        """
        titles = []

        # Group words by type
        nouns = [w for w in words if w.get('part_of_speech') == 'noun']
        verbs = [w for w in words if w.get('part_of_speech') == 'verb']
        adjectives = [w for w in words if w.get('part_of_speech') == 'adjective']

        # Template-based title generation
        templates = [
            # Noun + semantic field theme
            lambda: f"{random.choice(nouns)['latin_word'].title()} in {semantic_fields[0].title()}"
            if nouns and semantic_fields else None,

            # The [Adjective] [Noun]
            lambda: f"The {random.choice(adjectives)['english_gloss'].title()} {random.choice(nouns)['english_gloss'].title()}"
            if adjectives and nouns else None,

            # [Noun] [Verb]s
            lambda: f"{random.choice(nouns)['latin_word'].title()} {random.choice(verbs)['latin_word'].title()}"
            if nouns and verbs else None,

            # Based on story hooks
            lambda: random.choice([
                w['story_hooks'] for w in words if w.get('story_hooks')
            ]) if any(w.get('story_hooks') for w in words) else None,
        ]

        # Generate 3-5 title suggestions
        for _ in range(5):
            template = random.choice(templates)
            try:
                title = template()
                if title and title not in titles:
                    titles.append(title)
            except (IndexError, KeyError):
                continue

        # Fallback generic titles
        if len(titles) < 3:
            titles.extend([
                f"A Story About {semantic_fields[0].title()}" if semantic_fields else "A Latin Story",
                f"Learning {', '.join([w['latin_word'] for w in words[:3]])}",
                "Adventure Time"
            ])

        return titles[:5]

    def save_batch(self, batch_data: Dict, notes: str = "") -> int:
        """
        Save generated batch to database.

        Args:
            batch_data: Batch dictionary from generate_batch()
            notes: Optional notes about the batch

        Returns:
            int: Created batch ID
        """
        return self.db.create_batch(
            new_words=batch_data['new_words'],
            reused_words=batch_data['reused_words'],
            semantic_focus=batch_data['semantic_focus'],
            suggested_titles=batch_data['suggested_titles'],
            notes=notes
        )

    def generate_and_save(
        self,
        reuse_ratio: float = 0.75,
        total_words: int = 15,
        semantic_focus: Optional[List[str]] = None,
        notes: str = ""
    ) -> Tuple[Dict, int]:
        """
        Generate a batch and immediately save to database.

        Args:
            reuse_ratio: Percentage of words to reuse
            total_words: Total words in batch
            semantic_focus: Optional semantic fields to prioritize
            notes: Optional notes

        Returns:
            tuple: (batch_data dict, batch_id)
        """
        batch_data = self.generate_batch(
            reuse_ratio=reuse_ratio,
            total_words=total_words,
            semantic_focus=semantic_focus
        )

        batch_id = self.save_batch(batch_data, notes)

        return batch_data, batch_id


def format_batch_summary(batch_data: Dict) -> str:
    """
    Format batch data as human-readable summary.

    Args:
        batch_data: Batch dictionary

    Returns:
        str: Formatted text summary
    """
    lines = [
        f"Batch {batch_data['batch_id']} Vocabulary Plan",
        "=" * 50,
        "",
        f"**Reuse:** {', '.join(batch_data['reused_words'])}",
        "",
        f"**New:** {', '.join(batch_data['new_words'])}",
        "",
        f"**Total Unique Words:** {batch_data['total_unique']}",
        f"**Reuse Percentage:** {batch_data['reuse_percentage']}%",
        "",
        f"**Semantic Focus:** {', '.join(batch_data['semantic_focus'])}",
        "",
        "**Suggested Story Ideas:**"
    ]

    for i, title in enumerate(batch_data['suggested_titles'], 1):
        lines.append(f" {i}. {title}")

    return '\n'.join(lines)
