#!/usr/bin/env python3
"""
Book project management - create, initialize, track book projects.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookProject, ImageGenerationConfig
from scripts.database import LatinDatabase


def generate_project_id(title: str, existing_projects: list) -> str:
    """Generate unique project ID from title."""
    # Create slug from title
    slug = title.lower()
    slug = slug.replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')

    # Check for conflicts
    base_slug = slug
    counter = 1
    while slug in existing_projects:
        slug = f"{base_slug}_{counter}"
        counter += 1

    return slug


def list_existing_projects(projects_dir: Path) -> list:
    """List all existing project IDs."""
    if not projects_dir.exists():
        return []

    return [p.name for p in projects_dir.iterdir() if p.is_dir()]


def create_project(
    title: str,
    theme: Optional[str] = None,
    pages: int = 10,
    level: Optional[int] = None,
    art_style: Optional[str] = None,
    story_text: Optional[str] = None
) -> BookProject:
    """
    Create a new book project.

    Args:
        title: Book title in English
        theme: Theme/category (animal, family, food, etc.)
        pages: Target number of pages (8-12 recommended)
        level: Story level (1, 2, 3...)
        art_style: Art style description for image generation
        story_text: Source story text (optional, can add later)

    Returns:
        BookProject instance
    """
    # Setup paths
    projects_dir = Path('projects')
    projects_dir.mkdir(exist_ok=True)

    # Generate unique project ID
    existing = list_existing_projects(projects_dir)
    project_id = generate_project_id(title, existing)

    # Create project folder structure
    project_folder = projects_dir / project_id
    project_folder.mkdir(exist_ok=True)

    (project_folder / 'source').mkdir(exist_ok=True)
    (project_folder / 'translation').mkdir(exist_ok=True)
    (project_folder / 'images').mkdir(exist_ok=True)
    (project_folder / 'latex').mkdir(exist_ok=True)

    # Create image config
    default_style = "children's book illustration, watercolor style, warm colors, simple shapes"
    image_config = ImageGenerationConfig(
        art_style=art_style or default_style
    )

    # Create project
    project = BookProject(
        project_id=project_id,
        title_english=title,
        source_text=story_text or "",
        theme=theme,
        target_pages=pages,
        level=level,
        project_folder=str(project_folder),
        image_config=image_config
    )

    # Save source text if provided
    if story_text:
        source_file = project_folder / 'source' / 'story_english.txt'
        source_file.write_text(story_text, encoding='utf-8')

    # Save project config
    config_file = project_folder / 'config.json'
    project.save(str(config_file))

    # Create status file
    status_file = project_folder / 'status.txt'
    status_file.write_text(
        f"Status: {project.status}\n"
        f"Created: {project.date_created}\n"
        f"Last modified: {project.date_modified}\n",
        encoding='utf-8'
    )

    return project


def load_project(project_id: str) -> Optional[BookProject]:
    """Load a project by ID."""
    config_file = Path('projects') / project_id / 'config.json'

    if not config_file.exists():
        return None

    return BookProject.load(str(config_file))


def update_project_status(project: BookProject, new_status: str):
    """Update project status and save."""
    project.status = new_status
    project.date_modified = datetime.now().isoformat()

    config_file = Path(project.project_folder) / 'config.json'
    project.save(str(config_file))

    status_file = Path(project.project_folder) / 'status.txt'
    status_file.write_text(
        f"Status: {project.status}\n"
        f"Created: {project.date_created}\n"
        f"Last modified: {project.date_modified}\n",
        encoding='utf-8'
    )


def list_all_projects() -> list[BookProject]:
    """List all book projects."""
    projects_dir = Path('projects')
    if not projects_dir.exists():
        return []

    projects = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            config_file = project_dir / 'config.json'
            if config_file.exists():
                try:
                    project = BookProject.load(str(config_file))
                    projects.append(project)
                except Exception as e:
                    print(f"Warning: Could not load {project_dir.name}: {e}")

    return sorted(projects, key=lambda p: p.date_created, reverse=True)


def show_project_status(project: BookProject):
    """Display project status."""
    print(f"\n📚 PROJECT: {project.title_english}")
    print("=" * 70)

    print(f"\nID: {project.project_id}")
    print(f"Status: {project.status}")
    print(f"Theme: {project.theme or 'none'}")
    print(f"Level: {project.level or 'not set'}")
    print(f"Target pages: {project.target_pages}")

    if project.title_latin:
        print(f"Latin title: {project.title_latin}")

    print(f"\nCreated: {project.date_created}")
    print(f"Modified: {project.date_modified}")

    print(f"\nFolder: {project.project_folder}")

    # Show workflow progress
    print("\n📋 WORKFLOW PROGRESS:")
    workflow_steps = [
        ("initialized", "Project created"),
        ("translated", "Story translated to Latin"),
        ("reviewed", "Translation reviewed and paginated"),
        ("images_generated", "Images generated"),
        ("pdf_built", "PDF assembled"),
        ("approved", "Vocabulary approved and added to database")
    ]

    current_index = next((i for i, (status, _) in enumerate(workflow_steps) if status == project.status), 0)

    for i, (status, description) in enumerate(workflow_steps):
        if i < current_index:
            print(f"  ✅ {description}")
        elif i == current_index:
            print(f"  🔄 {description} (current)")
        else:
            print(f"  ⬜ {description}")

    print()


def main():
    """Test book manager."""
    # Test creating a project
    print("Creating test project...")

    project = create_project(
        title="The Boy and the Pig",
        theme="animals",
        pages=10,
        level=1,
        story_text="A boy sees a pig. The pig is big! The boy runs to the pig."
    )

    print(f"\n✅ Created project: {project.project_id}")
    print(f"   Folder: {project.project_folder}")

    # Show status
    show_project_status(project)

    # List all projects
    print("\n📚 ALL PROJECTS:")
    print("=" * 70)
    all_projects = list_all_projects()
    for p in all_projects:
        print(f"  {p.project_id:30s} - {p.title_english:30s} [{p.status}]")


if __name__ == '__main__':
    main()
