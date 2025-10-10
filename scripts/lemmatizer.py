#!/usr/bin/env python3
"""
Latin lemmatization utilities using CLTK.
Handles conversion of inflected forms to dictionary forms.
"""

import re
from typing import List, Optional, Tuple
from functools import lru_cache

# Lazy load CLTK (expensive import)
_nlp = None

def get_nlp():
    """Lazy-load CLTK NLP pipeline."""
    global _nlp
    if _nlp is None:
        from cltk import NLP
        print("Loading CLTK Latin models (this may take a moment on first run)...")
        _nlp = NLP('lat', suppress_banner=True)
    return _nlp


def normalize_macrons(word: str) -> str:
    """
    Normalize macron variations.
    CLTK might not use macrons, but our database does.
    """
    # Map common macron variations
    # For now, just strip macrons for matching
    macron_map = {
        'ā': 'a', 'ē': 'e', 'ī': 'i', 'ō': 'o', 'ū': 'u',
        'Ā': 'A', 'Ē': 'E', 'Ī': 'I', 'Ō': 'O', 'Ū': 'U'
    }

    result = word
    for macron, base in macron_map.items():
        result = result.replace(macron, base)

    return result


def clean_latin_word(word: str) -> str:
    """Clean a Latin word for lemmatization."""
    # Remove punctuation
    word = re.sub(r'[.,;:!?"\'\[\]\(\)]', '', word)

    # Remove numbers
    word = re.sub(r'\d+', '', word)

    # Strip whitespace
    word = word.strip()

    # Lowercase
    word = word.lower()

    return word


def extract_base_form(headword: str) -> str:
    """
    Extract base lemma from DCC-style headword.

    Examples:
        'canis -is m.' -> 'canis'
        'currō currere cucurrī cursum' -> 'currō'
        'sum esse fuī futūrum' -> 'sum'
        'bonus -a -um' -> 'bonus'
    """
    # Take first word/token
    parts = headword.strip().split()
    if not parts:
        return headword

    base = parts[0]

    # Remove any trailing punctuation
    base = re.sub(r'[.,;:!?]$', '', base)

    return base


@lru_cache(maxsize=1000)
def lemmatize_word(word: str) -> List[Tuple[str, str]]:
    """
    Lemmatize a Latin word to its dictionary form.

    Args:
        word: Latin word (may be inflected)

    Returns:
        List of (lemma, part_of_speech) tuples
        Returns empty list if unable to lemmatize

    Examples:
        'currit' -> [('curro', 'verb')]
        'pueri' -> [('puer', 'noun')]
    """
    # Clean the word first
    cleaned = clean_latin_word(word)

    if not cleaned:
        return []

    # Skip very short words or numbers
    if len(cleaned) <= 1 or cleaned.isdigit():
        return []

    try:
        nlp = get_nlp()
        doc = nlp.analyze(text=cleaned)

        results = []

        # CLTK 2.0 returns a document with words
        if hasattr(doc, 'words') and doc.words:
            for word_obj in doc.words:
                if hasattr(word_obj, 'lemma') and word_obj.lemma:
                    lemma = word_obj.lemma.lower()
                    # Get POS tag if available
                    if hasattr(word_obj, 'upos') and word_obj.upos:
                        pos = str(word_obj.upos.tag).lower() if hasattr(word_obj.upos, 'tag') else 'unknown'
                    else:
                        pos = 'unknown'
                    results.append((lemma, pos))

        # If no results, return the cleaned word as-is
        if not results:
            results = [(cleaned, 'unknown')]

        return results

    except Exception as e:
        print(f"Warning: Could not lemmatize '{word}': {e}")
        return [(cleaned, 'unknown')]


def find_best_lemma(word: str, candidates: List[str]) -> Optional[str]:
    """
    Given a word and list of candidate lemmas in database,
    find the best match.

    Uses both lemmatization and fuzzy matching.
    """
    # First try lemmatization
    lemmas = lemmatize_word(word)

    # Normalize candidates for comparison
    normalized_candidates = {normalize_macrons(c.lower()): c for c in candidates}

    # Try each lemma result
    for lemma, pos in lemmas:
        normalized_lemma = normalize_macrons(lemma)

        # Exact match (ignoring macrons)
        if normalized_lemma in normalized_candidates:
            return normalized_candidates[normalized_lemma]

    # No match found
    return None


def extract_latin_words_from_text(text: str) -> List[str]:
    """
    Extract all Latin words from text.
    Filters out common English/markup artifacts.
    """
    # Remove markdown formatting
    text = re.sub(r'#+\s+', '', text)  # Headers
    text = re.sub(r'\*\*?(.*?)\*\*?', r'\1', text)  # Bold/italic
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links

    # Split into words
    words = re.findall(r'\b[a-zāēīōūäëïöüæœ]+\b', text, re.IGNORECASE)

    # Common English words to filter out
    english_stopwords = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were',
        'a', 'an', 'this', 'that', 'these', 'those', 'latin', 'text',
        'translation', 'english', 'vocabulary', 'story', 'note', 'notes'
    }

    # Filter and clean
    cleaned_words = []
    for word in words:
        cleaned = clean_latin_word(word)
        if cleaned and len(cleaned) > 1 and cleaned not in english_stopwords:
            cleaned_words.append(word)  # Keep original case/macrons

    return cleaned_words


def test_lemmatizer():
    """Test the lemmatizer with common forms."""
    test_cases = [
        "currit",
        "pueri",
        "videt",
        "sunt",
        "māter",
        "domum",
        "aquam",
    ]

    print("Testing lemmatizer:")
    print("=" * 60)

    for word in test_cases:
        results = lemmatize_word(word)
        print(f"{word:15s} -> {results}")

    print("=" * 60)


if __name__ == '__main__':
    test_lemmatizer()
