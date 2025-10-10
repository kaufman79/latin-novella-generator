#!/usr/bin/env python3
"""
Vocabulary parser using LatinCy for lemmatization.
Extracts vocabulary from Latin text and generates child-friendly definitions.
"""

import spacy
from typing import List, Dict, Optional
from pathlib import Path
import google.generativeai as genai


class LatinVocabularyParser:
    """Parse Latin text to extract vocabulary with lemmas, POS, and definitions."""

    def __init__(self):
        """Initialize the parser with LatinCy model."""
        try:
            self.nlp = spacy.load('la_core_web_lg')
        except OSError:
            raise RuntimeError(
                "LatinCy model not found. Install with:\n"
                "pip install https://huggingface.co/latincy/la_core_web_lg/resolve/main/la_core_web_lg-any-py3-none-any.whl"
            )

    def extract_lemmas(self, text: str) -> List[Dict[str, str]]:
        """
        Extract unique lemmas from Latin text with POS tags.

        Args:
            text: Latin text to parse

        Returns:
            List of dicts with 'lemma', 'pos', and 'forms' (example forms seen in text)
        """
        doc = self.nlp(text)

        # Group by lemma to collect different forms
        lemma_data = {}

        for token in doc:
            # Skip punctuation and whitespace
            if token.pos_ in ['PUNCT', 'SPACE'] or not token.text.strip():
                continue

            lemma = token.lemma_

            if lemma not in lemma_data:
                lemma_data[lemma] = {
                    'lemma': lemma,
                    'pos': token.pos_,  # NOUN, VERB, ADJ, etc.
                    'forms': set()
                }

            # Collect the actual forms seen in text
            lemma_data[lemma]['forms'].add(token.text.lower())

        # Convert forms sets to lists and sort
        result = []
        for data in lemma_data.values():
            data['forms'] = sorted(list(data['forms']))
            result.append(data)

        return sorted(result, key=lambda x: x['lemma'])

    def generate_definitions(self, lemmas: List[Dict[str, str]], api_key: str) -> List[Dict]:
        """
        Generate child-friendly English definitions for Latin lemmas using AI.

        Args:
            lemmas: List of dicts with 'lemma' and 'pos'
            api_key: Gemini API key

        Returns:
            List of vocabulary entries with lemma, english, pos, and dictionary_form
        """
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Build prompt
        lemma_list = "\n".join([f"- {item['lemma']} ({item['pos']})" for item in lemmas])

        prompt = f"""You are a Latin teacher creating vocabulary definitions for young children learning Latin.

For each Latin word below, provide:
1. A simple, child-friendly English translation (1-3 words)
2. The part of speech (noun, verb, adjective, adverb, preposition, etc.)
3. The dictionary form (e.g., for nouns: "puella, puellae, f." or for verbs: "amo, amare, amavi, amatus")

Latin words to define:
{lemma_list}

Output as JSON array:
```json
[
  {{
    "latin": "lemma",
    "english": "simple English translation",
    "part_of_speech": "noun/verb/adjective/etc",
    "dictionary_form": "full dictionary entry"
  }}
]
```

Keep translations simple and appropriate for children. For example:
- "ambulo" → "to walk" (not "to ambulate")
- "puella" → "girl"
- "magnus" → "big" or "large"
"""

        # Call AI
        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # Extract JSON from markdown code block if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        # Parse JSON
        import json
        vocab_list = json.loads(response_text)

        return vocab_list

    def parse_book_vocabulary(self, text: str, api_key: str) -> List[Dict]:
        """
        Complete pipeline: extract lemmas and generate definitions.

        Args:
            text: Latin text from the book
            api_key: Gemini API key

        Returns:
            List of vocabulary entries ready for database
        """
        # Step 1: Extract lemmas using LatinCy
        lemmas = self.extract_lemmas(text)

        if not lemmas:
            return []

        # Step 2: Generate definitions using AI
        vocab_list = self.generate_definitions(lemmas, api_key)

        return vocab_list


def main():
    """Test the vocabulary parser."""
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')

    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment")
        return

    parser = LatinVocabularyParser()

    # Test text
    test_text = """
    Cicadae multae in silva vivebant.
    Draco magnus in spelunca dormit.
    Cicadae cantare amabant.
    """

    print("Testing Vocabulary Parser")
    print("=" * 60)

    print("\n1. Extracting lemmas...")
    lemmas = parser.extract_lemmas(test_text)
    print(f"Found {len(lemmas)} unique lemmas:")
    for item in lemmas:
        print(f"  - {item['lemma']} ({item['pos']}): forms seen: {', '.join(item['forms'])}")

    print("\n2. Generating definitions...")
    vocab_list = parser.generate_definitions(lemmas, api_key)
    print("Vocabulary with definitions:")
    for entry in vocab_list:
        print(f"  - {entry['latin']}: {entry['english']} ({entry['part_of_speech']})")
        print(f"    Dictionary form: {entry['dictionary_form']}")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == '__main__':
    main()
