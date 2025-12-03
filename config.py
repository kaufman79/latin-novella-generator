"""
Configuration constants for Latin Novella Generator.

This module centralizes all hardcoded values, paths, and configuration
settings to make the application easier to maintain and configure.
"""

from pathlib import Path

# ==================== DATABASE CONFIGURATION ====================

# Database file path
DB_PATH = "data/lexicon.db"

# Default database directory
DB_DIR = Path("data")

# ==================== PROJECT CONFIGURATION ====================

# Projects base directory
PROJECTS_DIR = Path("projects")

# Default project subdirectories
PROJECT_SUBDIRS = {
    "images": "images",
    "translation": "translation",
    "source": "source",
    "character_references": "character_references"
}

# ==================== IMAGE GENERATION ====================

# Default Gemini model for image generation
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"

# Default Gemini model for text processing
GEMINI_TEXT_MODEL = "gemini-2.0-flash-exp"

# Image generation providers
IMAGE_PROVIDERS = ["nano_banana", "gemini"]

# Default image dimensions
DEFAULT_IMAGE_SIZE = (512, 512)

# ==================== BOOK CONFIGURATION ====================

# Default book parameters
DEFAULT_TARGET_PAGES = 8
MIN_TARGET_PAGES = 4
MAX_TARGET_PAGES = 20

DEFAULT_LEVEL = 1
MIN_LEVEL = 1
MAX_LEVEL = 10

DEFAULT_TARGET_AGE = "2-5"

# ==================== VOCABULARY CONFIGURATION ====================

# Mastery levels
MASTERY_LEVELS = {
    1: "New",
    2: "Familiar",
    3: "Mastered"
}

# Default vocabulary suggestion count
DEFAULT_VOCAB_COUNT = 20

# ==================== STREAMLIT UI CONFIGURATION ====================

# Page title and icon
PAGE_TITLE = "Latin Book Engine"
PAGE_ICON = "🏛️"

# ==================== VALIDATION SETTINGS ====================

# Stage 1 validation (English story)
MIN_WORD_COUNT_STAGE_1 = 30
MAX_WORD_COUNT_STAGE_1 = 500

# Stage 2 validation (Latin translation)
MIN_WORD_COUNT_STAGE_2 = 30
MAX_WORD_COUNT_STAGE_2 = 500

# Stage 4 validation (paginated JSON)
# (No specific constants yet, but can be added)

# ==================== FILE PATHS ====================

# Environment file
ENV_FILE = ".env"

# ==================== ERROR MESSAGES ====================

ERROR_MESSAGES = {
    "db_not_found": "Database not found at {path}",
    "project_not_found": "Project '{project_id}' not found",
    "api_key_missing": "GEMINI_API_KEY not found in environment variables",
    "invalid_json": "Invalid JSON format: {error}",
    "image_generation_failed": "Failed to generate image: {error}",
    "pdf_generation_failed": "Failed to generate PDF: {error}",
}

# ==================== SUCCESS MESSAGES ====================

SUCCESS_MESSAGES = {
    "project_created": "✅ Project created successfully",
    "images_generated": "✅ Images generated successfully",
    "pdf_built": "✅ PDF built successfully",
    "db_initialized": "✅ Database initialized successfully",
}
