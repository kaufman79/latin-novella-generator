#!/usr/bin/env python3
"""Test LatinCy Latin lemmatization."""

import spacy

# Test text from the locusts book
test_text = """
Cicadae multae in silva vivebant.
Draco in spelunca dormit.
"""

print("=" * 60)
print("Testing LatinCy Latin Processing")
print("=" * 60)

# Load LatinCy model
print("\n1. Loading LatinCy model...")
try:
    nlp = spacy.load('la_core_web_lg')
    print("✓ Model loaded")
except Exception as e:
    print(f"✗ Error loading: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Process text
print("\n2. Processing text...")
try:
    doc = nlp(test_text)
    print("✓ Text analyzed")
except Exception as e:
    print(f"✗ Error analyzing: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n3. Extracted tokens, lemmas, and POS:")
print("-" * 80)
print(f"  {'Token':<15} {'Lemma':<15} {'POS':<10} {'Tag':<15} {'Morph'}")
print("-" * 80)
for token in doc:
    if token.text.strip() and token.text not in ['.', ',', '!', '?', '\n']:
        morph = str(token.morph)[:30] if token.morph else ''
        print(f"  {token.text:<15} {token.lemma_:<15} {token.pos_:<10} {token.tag_:<15} {morph}")

print("\n4. Vocabulary summary:")
print("-" * 60)
lemmas = set()
for token in doc:
    if token.text.strip() and token.text not in ['.', ',', '!', '?', '\n'] and token.pos_ not in ['PUNCT', 'SPACE']:
        lemmas.add(token.lemma_)

print(f"  Unique lemmas found: {len(lemmas)}")
print(f"  Lemmas: {', '.join(sorted(lemmas))}")

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
