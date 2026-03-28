"""
Configuration for Latin Book System.
"""

from pathlib import Path

# Project paths
PROJECTS_DIR = Path("projects")
ENV_FILE = ".env"

# Image generation — primary (Google Gemini)
GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_IMAGE_RESOLUTION = "512"

# Image generation — fallback (OpenAI)
OPENAI_IMAGE_MODEL = "gpt-image-1"
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_QUALITY = "medium"

# Book defaults
DEFAULT_TARGET_PAGES = 20

# Public domain sources
GUTENBERG_IMAGE_DIR = "source_images"
SUPPORTED_IMAGE_FORMATS = (".png", ".jpg", ".jpeg", ".gif", ".tiff")
