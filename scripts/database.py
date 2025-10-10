"""
Database module for Latin Book Engine.
Tracks known vocabulary and book history for personalized story creation.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class LatinDatabase:
    """Manages known vocabulary and book tracking."""

    def __init__(self, db_path: str = "data/lexicon.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.create_tables()

    def create_tables(self):
        """Create known_words and books tables if they don't exist."""
        cursor = self.conn.cursor()

        # Known words table - tracks vocabulary the child knows
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS known_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lemma TEXT NOT NULL UNIQUE,
                english TEXT NOT NULL,
                part_of_speech TEXT,
                dictionary_form TEXT,
                date_learned TEXT,
                times_seen INTEGER DEFAULT 0,
                last_seen_date TEXT,
                mastery_level INTEGER DEFAULT 1,
                notes TEXT
            )
        """)

        # Books table - tracks which books have been created and what words they used
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL UNIQUE,
                title_latin TEXT,
                title_english TEXT,
                date_created TEXT,
                words_used TEXT,
                new_words_introduced TEXT,
                total_words INTEGER DEFAULT 0,
                known_word_percentage REAL DEFAULT 0
            )
        """)

        self.conn.commit()

    # ==================== KNOWN WORDS METHODS ====================

    def add_known_word(self, lemma: str, english: str, part_of_speech: str = None,
                       dictionary_form: str = None, notes: str = None) -> int:
        """
        Add a new known word to the database.

        Args:
            lemma: Base form (currō, canis, puer)
            english: English translation
            part_of_speech: noun, verb, adjective, etc.
            dictionary_form: Full dictionary entry (e.g., "puer, puerī, m.")
            notes: Optional notes

        Returns:
            int: ID of inserted word
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO known_words (lemma, english, part_of_speech, dictionary_form,
                                     date_learned, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (lemma, english, part_of_speech, dictionary_form,
              datetime.now().isoformat(), notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_all_known_words(self) -> List[Dict]:
        """Get all known words."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM known_words ORDER BY lemma")
        return [dict(row) for row in cursor.fetchall()]

    def get_known_word_by_lemma(self, lemma: str) -> Optional[Dict]:
        """Get a known word by its lemma."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM known_words WHERE lemma = ?", (lemma,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_word_seen(self, lemma: str):
        """Increment times_seen and update last_seen_date for a word."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE known_words
            SET times_seen = times_seen + 1,
                last_seen_date = ?
            WHERE lemma = ?
        """, (datetime.now().isoformat(), lemma))
        self.conn.commit()

    def update_mastery_level(self, lemma: str, level: int):
        """Update mastery level (1=new, 2=familiar, 3=mastered)."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE known_words
            SET mastery_level = ?
            WHERE lemma = ?
        """, (level, lemma))
        self.conn.commit()

    def delete_known_word(self, lemma: str):
        """Delete a known word."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM known_words WHERE lemma = ?", (lemma,))
        self.conn.commit()

    def search_known_words(self, search_term: str) -> List[Dict]:
        """Search known words by lemma or English."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM known_words
            WHERE lemma LIKE ? OR english LIKE ?
            ORDER BY lemma
        """, (f'%{search_term}%', f'%{search_term}%'))
        return [dict(row) for row in cursor.fetchall()]

    def get_words_by_pos(self, part_of_speech: str) -> List[Dict]:
        """Get all words of a specific part of speech."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM known_words
            WHERE part_of_speech = ?
            ORDER BY lemma
        """, (part_of_speech,))
        return [dict(row) for row in cursor.fetchall()]

    def get_words_needing_review(self, days: int = 7) -> List[Dict]:
        """Get words that haven't been seen in N days."""
        cursor = self.conn.cursor()
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute("""
            SELECT * FROM known_words
            WHERE last_seen_date < datetime('now', '-{} days')
               OR last_seen_date IS NULL
            ORDER BY last_seen_date ASC NULLS FIRST
        """.format(days))
        return [dict(row) for row in cursor.fetchall()]

    # ==================== BOOKS METHODS ====================

    def add_book(self, project_id: str, title_latin: str = None, title_english: str = None,
                 words_used: List[str] = None, new_words: List[str] = None,
                 total_words: int = 0, known_percentage: float = 0.0):
        """
        Record a completed book.

        Args:
            project_id: Unique project identifier
            title_latin: Latin title
            title_english: English title
            words_used: List of lemmas used in the book
            new_words: List of new lemmas introduced
            total_words: Total word count
            known_percentage: Percentage of known words
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO books (project_id, title_latin, title_english, date_created,
                              words_used, new_words_introduced, total_words, known_word_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, title_latin, title_english, datetime.now().isoformat(),
              json.dumps(words_used or []), json.dumps(new_words or []),
              total_words, known_percentage))
        self.conn.commit()

    def get_all_books(self) -> List[Dict]:
        """Get all books."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY date_created DESC")
        books = []
        for row in cursor.fetchall():
            book = dict(row)
            # Parse JSON fields
            book['words_used'] = json.loads(book['words_used']) if book['words_used'] else []
            book['new_words_introduced'] = json.loads(book['new_words_introduced']) if book['new_words_introduced'] else []
            books.append(book)
        return books

    def get_book_by_project_id(self, project_id: str) -> Optional[Dict]:
        """Get a book by project ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE project_id = ?", (project_id,))
        row = cursor.fetchone()
        if row:
            book = dict(row)
            book['words_used'] = json.loads(book['words_used']) if book['words_used'] else []
            book['new_words_introduced'] = json.loads(book['new_words_introduced']) if book['new_words_introduced'] else []
            return book
        return None

    # ==================== STATISTICS ====================

    def get_summary_stats(self) -> Dict:
        """Get summary statistics."""
        cursor = self.conn.cursor()

        # Total known words
        cursor.execute("SELECT COUNT(*) as count FROM known_words")
        total_known = cursor.fetchone()['count']

        # Words by mastery level
        cursor.execute("""
            SELECT mastery_level, COUNT(*) as count
            FROM known_words
            GROUP BY mastery_level
        """)
        mastery_dist = {row['mastery_level']: row['count'] for row in cursor.fetchall()}

        # Words by POS
        cursor.execute("""
            SELECT part_of_speech, COUNT(*) as count
            FROM known_words
            GROUP BY part_of_speech
        """)
        pos_dist = {row['part_of_speech']: row['count'] for row in cursor.fetchall()}

        # Total books
        cursor.execute("SELECT COUNT(*) as count FROM books")
        total_books = cursor.fetchone()['count']

        # Average known word percentage
        cursor.execute("SELECT AVG(known_word_percentage) as avg FROM books")
        avg_known_pct = cursor.fetchone()['avg'] or 0

        return {
            'total_known_words': total_known,
            'mastery_distribution': mastery_dist,
            'pos_distribution': pos_dist,
            'total_books': total_books,
            'avg_known_percentage': round(avg_known_pct, 1)
        }

    def close(self):
        """Close database connection."""
        self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
