"""
Configuration for Latin Book System.
"""

from pathlib import Path

# Project paths
PROJECTS_DIR = Path("projects")
ENV_FILE = ".env"

# Image generation (OpenAI)
OPENAI_IMAGE_MODEL = "gpt-image-1"
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_QUALITY = "medium"

# Book defaults
DEFAULT_TARGET_PAGES = 20
