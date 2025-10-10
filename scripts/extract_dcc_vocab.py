#!/usr/bin/env python3
"""
Extract Latin vocabulary from DCC Latin Core HTML file.
"""

import re
import csv
from pathlib import Path

def extract_dcc_vocabulary(html_file):
    """Extract vocabulary from DCC HTML file."""

    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Find all table rows
    # Pattern: extract data from table cells
    pattern = r'<td headers="view-field-display-headwords-table-column"[^>]*>.*?<a[^>]*>(.*?)</a>.*?</td>\s*<td headers="view-field-definition-table-column"[^>]*>(.*?)</td>\s*<td headers="view-field-part-of-speech-table-column"[^>]*>(.*?)</td>\s*<td headers="view-field-semantic-group-table-column"[^>]*>(.*?)</td>\s*<td headers="view-field-frequency-rank-table-column"[^>]*>(.*?)</td>'

    matches = re.findall(pattern, html, re.DOTALL)

    vocab = []
    for match in matches:
        headword = match[0].strip()
        definition = match[1].strip()
        part_of_speech = match[2].strip()
        semantic_group = match[3].strip()
        frequency_rank = match[4].strip()

        # Clean up HTML entities and whitespace
        headword = re.sub(r'\s+', ' ', headword)
        definition = re.sub(r'\s+', ' ', definition)

        vocab.append({
            'headword': headword,
            'definition': definition,
            'part_of_speech': part_of_speech,
            'semantic_group': semantic_group,
            'frequency_rank': int(frequency_rank) if frequency_rank.isdigit() else 9999
        })

    return vocab


def save_to_csv(vocab, output_file):
    """Save vocabulary to CSV file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['frequency_rank', 'headword', 'definition', 'part_of_speech', 'semantic_group'])
        writer.writeheader()

        # Sort by frequency rank
        for item in sorted(vocab, key=lambda x: x['frequency_rank']):
            writer.writerow(item)

    print(f"✅ Saved {len(vocab)} words to {output_path}")


if __name__ == '__main__':
    input_file = 'data/frequency_lists/dcc_latin_core.html'
    output_file = 'data/frequency_lists/dcc_latin_core.csv'

    print("Extracting DCC Latin Core vocabulary...")
    vocab = extract_dcc_vocabulary(input_file)

    print(f"Found {len(vocab)} vocabulary entries")
    print("\nTop 10 by frequency:")
    for item in sorted(vocab, key=lambda x: x['frequency_rank'])[:10]:
        print(f"  {item['frequency_rank']:3d}. {item['headword']:30s} - {item['definition']}")

    save_to_csv(vocab, output_file)
