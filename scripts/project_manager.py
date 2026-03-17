#!/usr/bin/env python3
"""
Project management for Latin book system.
Create, load, list, and update book projects.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from book_schemas import BookProject


PROJECTS_DIR = Path("projects")


def generate_project_id(title: str) -> str:
    """Generate unique project ID from title."""
    slug = title.lower().replace(' ', '_')
    slug = ''.join(c for c in slug if c.isalnum() or c == '_')

    existing = [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()] if PROJECTS_DIR.exists() else []

    base_slug = slug
    counter = 1
    while slug in existing:
        slug = f"{base_slug}_{counter}"
        counter += 1

    return slug


def create_project(title: str, theme: Optional[str] = None, target_pages: int = 20) -> BookProject:
    """Create a new book project with folder structure."""
    PROJECTS_DIR.mkdir(exist_ok=True)

    project_id = generate_project_id(title)
    project_folder = PROJECTS_DIR / project_id

    # Create directory structure
    for subdir in ['source', 'translation', 'art', 'images', 'output']:
        (project_folder / subdir).mkdir(parents=True, exist_ok=True)

    project = BookProject(
        project_id=project_id,
        title_english=title,
        theme=theme,
        target_pages=target_pages,
        project_folder=str(project_folder),
    )

    config_path = project_folder / 'config.json'
    project.save(str(config_path))

    print(f"Created project: {project_id}")
    print(f"  Folder: {project_folder}")

    return project


def load_project(project_id: str) -> Optional[BookProject]:
    """Load a project by ID."""
    config_file = PROJECTS_DIR / project_id / 'config.json'
    if not config_file.exists():
        return None
    return BookProject.load(str(config_file))


def update_status(project: BookProject, new_status: str):
    """Update project status and save."""
    project.status = new_status
    config_file = Path(project.project_folder) / 'config.json'
    project.save(str(config_file))


def list_projects() -> list[BookProject]:
    """List all book projects, newest first."""
    if not PROJECTS_DIR.exists():
        return []

    projects = []
    for project_dir in PROJECTS_DIR.iterdir():
        if project_dir.is_dir():
            config_file = project_dir / 'config.json'
            if config_file.exists():
                try:
                    projects.append(BookProject.load(str(config_file)))
                except Exception as e:
                    print(f"Warning: Could not load {project_dir.name}: {e}")

    return sorted(projects, key=lambda p: p.date_created, reverse=True)


def main():
    """CLI for project management."""
    import argparse

    parser = argparse.ArgumentParser(description="Latin Book Project Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Create
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("title", help="Book title in English")
    create_parser.add_argument("--theme", help="Story theme")
    create_parser.add_argument("--pages", type=int, default=20, help="Target page count")

    # List
    subparsers.add_parser("list", help="List all projects")

    # Status
    status_parser = subparsers.add_parser("status", help="Show project status")
    status_parser.add_argument("project_id", help="Project ID")

    args = parser.parse_args()

    if args.command == "create":
        create_project(args.title, theme=args.theme, target_pages=args.pages)
    elif args.command == "list":
        for p in list_projects():
            print(f"  {p.project_id:35s} {p.title_english:35s} [{p.status}]")
    elif args.command == "status":
        project = load_project(args.project_id)
        if project:
            print(f"Project: {project.title_english}")
            print(f"Status:  {project.status}")
            print(f"Pages:   {project.target_pages}")
            print(f"Created: {project.date_created}")
        else:
            print(f"Project not found: {args.project_id}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
