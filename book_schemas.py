#!/usr/bin/env python3
"""
JSON schemas for book projects.
Defines the structure for storing book data throughout the workflow.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# --- Story Outline (source) ---

class CharacterOutline(BaseModel):
    """Character in the story outline."""
    name: str
    description: str  # Visual description
    source: Optional[str] = None  # e.g., "Toon Link from Wind Waker" for established characters
    is_established: bool = False  # True if well-known character (better image consistency)


class LocationOutline(BaseModel):
    """Location in the story outline."""
    name: str
    description: str


class PageOutline(BaseModel):
    """Single page in the story outline."""
    page_number: int
    english_text: str
    scene_description: str  # What the illustration should show
    characters_present: List[str] = Field(default_factory=list)
    location: Optional[str] = None


class StoryOutline(BaseModel):
    """Complete story outline (output of Story Architect)."""
    title_english: str
    title_latin: Optional[str] = None
    target_pages: int = 20
    characters: List[CharacterOutline] = Field(default_factory=list)
    locations: List[LocationOutline] = Field(default_factory=list)
    pages: List[PageOutline] = Field(default_factory=list)


# --- Translation ---

class BookPage(BaseModel):
    """Single page in the translated book."""
    page_number: int
    latin_text: str
    english_text: str
    image_prompt: str  # Carried from outline, refined by Art Director
    image_path: Optional[str] = None
    characters: List[str] = Field(default_factory=list)
    location: Optional[str] = None


class BookTranslation(BaseModel):
    """Complete book translation (output of Latin Scribe, reviewed by Latin Censor)."""
    title_latin: str
    title_english: str
    pages: List[BookPage]


# --- Visual Bible (Art Direction) ---

class StyleSpec(BaseModel):
    """Art style specification."""
    medium: str  # e.g., "cel-shaded digital art in the style of Wind Waker"
    palette: str  # e.g., "warm saturated colors, teal ocean, golden sand"
    line_weight: str  # e.g., "bold black outlines, clean simple shapes"
    lighting: str  # e.g., "bright, flat lighting with soft shadows"
    mood: str  # e.g., "cheerful, adventurous, whimsical"
    technical: str = "square aspect ratio, child-friendly illustration, no text in image"


class CharacterVisual(BaseModel):
    """Character visual specification for image prompts."""
    source: Optional[str] = None  # e.g., "Toon Link from Wind Waker"
    is_established: bool = False
    visual_description: str  # Detailed, exact visual description
    expression_default: str = "neutral"
    height_reference: Optional[str] = None
    reference_image_path: Optional[str] = None  # Optional single reference image


class LocationVisual(BaseModel):
    """Location visual specification for image prompts."""
    visual_description: str
    time_of_day_default: str = "bright daylight"
    reference_image_path: Optional[str] = None  # Path to location reference image


class VisualBible(BaseModel):
    """Complete visual specification for a book (output of Art Director)."""
    style: StyleSpec
    characters: Dict[str, CharacterVisual]
    locations: Dict[str, LocationVisual]
    composition_rules: List[str] = Field(default_factory=list)
    reference_images: List[str] = Field(default_factory=list)  # Default ref image paths for all pages


class PagePrompt(BaseModel):
    """Self-contained image prompt for a single page."""
    page_number: int
    prompt: str  # Full self-contained prompt (style + characters + location + scene)
    characters_in_scene: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    reference_images: Optional[List[str]] = None  # Page-specific refs (overrides visual bible defaults)


class ImagePrompts(BaseModel):
    """All page prompts for a book (output of Art Director)."""
    pages: List[PagePrompt]


# --- Public Domain Adaptation ---

class PublicDomainSource(BaseModel):
    """Metadata for a public domain illustration source."""
    title: str
    author: str
    illustrator: str
    source_url: str
    year: Optional[int] = None
    license: str = "Public Domain"


class ImageMapping(BaseModel):
    """Single page-to-image mapping."""
    page_number: int
    source: str = "existing"  # "existing" or "generate"
    image_filename: Optional[str] = None
    original_caption: Optional[str] = None
    generate_prompt: Optional[str] = None


class ImageManifest(BaseModel):
    """Page-to-image mapping for projects using pre-existing illustrations."""
    pd_source: PublicDomainSource
    mappings: List[ImageMapping]


# --- Project ---

class BookProject(BaseModel):
    """Complete book project configuration."""
    project_id: str
    title_english: str
    title_latin: Optional[str] = None

    # Source
    source_type: str = "original"  # "original", "adaptation", or "public_domain_adaptation"
    public_domain_source: Optional[PublicDomainSource] = None

    # Metadata
    theme: Optional[str] = None
    target_pages: int = 20

    # Virtue ratings (0-5 scale)
    virtue_ratings: Dict[str, int] = Field(default_factory=dict)  # 0-5 scale per virtue

    # Workflow status
    status: str = "initialized"
    # Statuses: initialized → outlined → translated → reviewed → art_directed → images_generated → pdf_built
    date_created: str = Field(default_factory=lambda: datetime.now().isoformat())
    date_modified: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Project folder path
    project_folder: str

    def save(self, path: str):
        """Save project to JSON file."""
        self.date_modified = datetime.now().isoformat()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def load(cls, path: str) -> 'BookProject':
        """Load project from JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            return cls.model_validate_json(f.read())
