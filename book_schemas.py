#!/usr/bin/env python3
"""
JSON schemas for book projects.
Defines the structure for storing book data throughout the workflow.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class VocabularyEntry(BaseModel):
    """Single vocabulary entry with dictionary formatting."""
    latin: str
    english: str
    part_of_speech: str  # noun, verb, adjective, etc.
    dictionary_form: str  # "puer, puerī, m." or "videō, vidēre, vīdī, vīsum"
    frequency_tier: Optional[str] = None  # ff625, core, common, supplemental
    notes: Optional[str] = None


class BookPage(BaseModel):
    """Single page in the book."""
    page_number: int
    latin_text: str
    english_text: str
    image_prompt: str
    image_path: Optional[str] = None  # Filled after image generation
    vocabulary_used: List[str] = Field(default_factory=list)  # Lemmas used on this page


class PlayExtension(BaseModel):
    """Play-based activity extension."""
    category: str  # "retelling", "physical", "creative", "vocabulary", "real_world"
    title: str
    description: str
    checked: bool = False


class ImageGenerationConfig(BaseModel):
    """Configuration for image generation."""
    reference_image_path: Optional[str] = None
    art_style: str = "children's book illustration, warm colors, simple shapes"
    seed: Optional[int] = None
    provider: str = "nano_banana"  # Could support multiple providers
    consistency_mode: str = "reference_image"  # or "seed" or "style_description"


class BookTranslation(BaseModel):
    """Complete book translation with pages and vocabulary."""
    title_latin: str
    title_english: str
    pages: List[BookPage]
    vocabulary_list: List[VocabularyEntry]
    play_extensions: List[PlayExtension] = Field(default_factory=list)


class BookProject(BaseModel):
    """Complete book project configuration."""
    project_id: str
    title_english: str
    title_latin: Optional[str] = None

    # Source story
    source_text: str  # Original English story
    source_type: str = "original"  # or "existing"

    # Translation
    translation: Optional[BookTranslation] = None

    # Image generation
    image_config: ImageGenerationConfig = Field(default_factory=ImageGenerationConfig)
    cover_image_prompt: Optional[str] = None  # Store cover prompt for regeneration

    # Metadata
    theme: Optional[str] = None
    target_age: str = "2-5"
    target_pages: int = 10
    level: Optional[int] = None

    # Workflow status
    status: str = "initialized"  # initialized, translated, reviewed, images_generated, pdf_built, approved
    date_created: str = Field(default_factory=lambda: datetime.now().isoformat())
    date_modified: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Paths
    project_folder: str

    def save(self, path: str):
        """Save project to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str) -> 'BookProject':
        """Load project from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return cls.model_validate_json(f.read())


class VocabularySuggestion(BaseModel):
    """Vocabulary suggestions for translation."""
    high_priority: List[Dict[str, str]]  # New words to introduce
    reuse: List[Dict[str, str]]  # Words from previous books
    theme_words: List[Dict[str, str]]  # Theme-specific words


# Example usage and validation
if __name__ == '__main__':
    # Test creating a book project
    project = BookProject(
        project_id="book_001",
        title_english="The Boy and the Pig",
        source_text="Once upon a time, a boy saw a pig. The pig was big!",
        theme="animals",
        target_pages=8,
        level=1,
        project_folder="projects/book_001"
    )

    print("Created project:")
    print(project.model_dump_json(indent=2))

    # Test creating a translation
    translation = BookTranslation(
        title_latin="Puer et Porcus",
        title_english="The Boy and the Pig",
        pages=[
            BookPage(
                page_number=1,
                latin_text="Puer porcum videt.",
                english_text="The boy sees a pig.",
                image_prompt="A young boy looking at a friendly pig in a sunny farm yard",
                vocabulary_used=["puer", "porcus", "videō"]
            ),
            BookPage(
                page_number=2,
                latin_text="Porcus magnus est!",
                english_text="The pig is big!",
                image_prompt="Close-up of a large, happy pig",
                vocabulary_used=["porcus", "magnus", "sum"]
            )
        ],
        vocabulary_list=[
            VocabularyEntry(
                latin="puer",
                english="boy",
                part_of_speech="noun",
                dictionary_form="puer, puerī, m.",
                frequency_tier="common"
            ),
            VocabularyEntry(
                latin="porcus",
                english="pig",
                part_of_speech="noun",
                dictionary_form="porcus, porcī, m.",
                frequency_tier="ff625"
            )
        ]
    )

    print("\nCreated translation:")
    print(translation.model_dump_json(indent=2))
