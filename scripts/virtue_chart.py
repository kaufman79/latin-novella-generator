#!/usr/bin/env python3
"""
Generate a bubble chart visualization of virtue ratings across all Latin books.

Scans projects/ for config.json files, reads virtue_ratings, and produces:
  - output/virtue_chart.png  (bubble chart)
  - stdout text summary of coverage gaps

Usage:
    python scripts/virtue_chart.py
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CARDINAL_VIRTUES = ["prudentia", "iustitia", "fortitudo", "temperantia"]
THEOLOGICAL_VIRTUES = ["fides", "spes", "caritas"]
ALL_VIRTUES = CARDINAL_VIRTUES + THEOLOGICAL_VIRTUES

# Display labels (Latin with English gloss)
VIRTUE_LABELS = {
    "prudentia": "Prudentia\n(Prudence)",
    "iustitia": "Iustitia\n(Justice)",
    "fortitudo": "Fortitudo\n(Courage)",
    "temperantia": "Temperantia\n(Temperance)",
    "fides": "Fides\n(Faith)",
    "spes": "Spes\n(Hope)",
    "caritas": "Caritas\n(Love)",
}

COLOR_CARDINAL = "#4A90D9"      # steel blue
COLOR_THEOLOGICAL = "#D4763A"   # warm orange
MAX_RATING = 5


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_projects(projects_dir: Path) -> list[dict]:
    """Load all project configs, returning list of {id, title, virtue_ratings}."""
    projects = []
    if not projects_dir.is_dir():
        print(f"Error: projects directory not found: {projects_dir}", file=sys.stderr)
        sys.exit(1)

    for config_path in sorted(projects_dir.glob("*/config.json")):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not read {config_path}: {e}", file=sys.stderr)
            continue

        project_id = config.get("project_id", config_path.parent.name)
        title = config.get("title_english", project_id)
        ratings = config.get("virtue_ratings", {})

        # Normalise: ensure every virtue key exists, default to 0
        normalised = {v: ratings.get(v, 0) for v in ALL_VIRTUES}
        projects.append({
            "id": project_id,
            "title": title,
            "ratings": normalised,
        })

    return projects


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------

def generate_chart(projects: list[dict], output_path: Path) -> None:
    """Create and save the bubble chart."""
    n_books = len(projects)
    n_virtues = len(ALL_VIRTUES)

    if n_books == 0:
        print("No projects found. Nothing to chart.", file=sys.stderr)
        return

    # --- Build data arrays ---
    xs = []  # book index
    ys = []  # virtue index
    sizes = []
    colors = []

    for bx, proj in enumerate(projects):
        for vy, virtue in enumerate(ALL_VIRTUES):
            rating = proj["ratings"][virtue]
            xs.append(bx)
            ys.append(vy)
            # Scale bubble area: 0 -> 0, 5 -> large
            sizes.append((rating / MAX_RATING) ** 1.0 * 600 if rating > 0 else 0)
            colors.append(COLOR_CARDINAL if virtue in CARDINAL_VIRTUES else COLOR_THEOLOGICAL)

    # --- Figure setup ---
    fig_width = max(8, 2 + n_books * 1.6)
    fig_height = max(6, 1 + n_virtues * 0.9)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.scatter(xs, ys, s=sizes, c=colors, alpha=0.75, edgecolors="white", linewidths=1.2)

    # Annotate ratings inside bubbles
    for bx, proj in enumerate(projects):
        for vy, virtue in enumerate(ALL_VIRTUES):
            rating = proj["ratings"][virtue]
            if rating > 0:
                ax.text(bx, vy, str(rating), ha="center", va="center",
                        fontsize=9, fontweight="bold", color="white")

    # --- Axes ---
    book_labels = [p["title"] for p in projects]
    ax.set_xticks(range(n_books))
    ax.set_xticklabels(book_labels, rotation=30, ha="right", fontsize=9)

    virtue_labels = [VIRTUE_LABELS[v] for v in ALL_VIRTUES]
    ax.set_yticks(range(n_virtues))
    ax.set_yticklabels(virtue_labels, fontsize=9)

    # Grid and limits
    ax.set_xlim(-0.6, n_books - 0.4)
    ax.set_ylim(-0.6, n_virtues - 0.4)
    ax.set_axisbelow(True)
    ax.grid(True, color="#E0E0E0", linestyle="-", linewidth=0.5)
    ax.set_facecolor("#FAFAFA")

    # Title
    ax.set_title("Virtue Coverage Across Latin Books", fontsize=14, fontweight="bold", pad=16)

    # Legend
    cardinal_patch = mpatches.Patch(color=COLOR_CARDINAL, label="Cardinal Virtues")
    theological_patch = mpatches.Patch(color=COLOR_THEOLOGICAL, label="Theological Virtues")
    ax.legend(handles=[cardinal_patch, theological_patch], loc="upper right",
              fontsize=9, framealpha=0.9)

    # Dividing line between cardinal and theological
    ax.axhline(y=len(CARDINAL_VIRTUES) - 0.5, color="#BBBBBB", linestyle="--", linewidth=0.8)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Chart saved to {output_path}")


# ---------------------------------------------------------------------------
# Text summary
# ---------------------------------------------------------------------------

def print_summary(projects: list[dict]) -> None:
    """Print a text summary highlighting coverage gaps."""
    if not projects:
        return

    print("\n" + "=" * 60)
    print("VIRTUE COVERAGE SUMMARY")
    print("=" * 60)

    # Per-virtue averages
    print("\nAverage rating per virtue (across all books):")
    print("-" * 40)
    for virtue in ALL_VIRTUES:
        vals = [p["ratings"][virtue] for p in projects]
        avg = sum(vals) / len(vals)
        max_val = max(vals)
        bar = "#" * int(round(avg * 4))  # simple text bar
        label = virtue.capitalize()
        print(f"  {label:<14s} avg={avg:.1f}  max={max_val}  {bar}")

    # Coverage gaps: virtues with avg < 1
    print("\nCoverage gaps (average < 1.0):")
    print("-" * 40)
    gaps_found = False
    for virtue in ALL_VIRTUES:
        vals = [p["ratings"][virtue] for p in projects]
        avg = sum(vals) / len(vals)
        if avg < 1.0:
            gaps_found = True
            books_with = [p["title"] for p in projects if p["ratings"][virtue] > 0]
            if books_with:
                print(f"  {virtue.capitalize():<14s} (avg {avg:.1f}) -- only in: {', '.join(books_with)}")
            else:
                print(f"  {virtue.capitalize():<14s} (avg {avg:.1f}) -- NOT covered in any book")
    if not gaps_found:
        print("  No major gaps found.")

    # Per-book totals
    print("\nPer-book virtue totals:")
    print("-" * 40)
    max_possible = MAX_RATING * len(ALL_VIRTUES)
    for proj in projects:
        total = sum(proj["ratings"].values())
        pct = total / max_possible * 100
        print(f"  {proj['title']:<35s} {total:>2d}/{max_possible}  ({pct:.0f}%)")

    # Strongest virtue per book
    print("\nStrongest virtue per book:")
    print("-" * 40)
    for proj in projects:
        best_virtue = max(ALL_VIRTUES, key=lambda v: proj["ratings"][v])
        best_val = proj["ratings"][best_virtue]
        if best_val == 0:
            print(f"  {proj['title']:<35s} (no virtues rated)")
        else:
            print(f"  {proj['title']:<35s} {best_virtue.capitalize()} ({best_val})")

    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Resolve paths relative to project root (parent of scripts/)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    projects_dir = project_root / "projects"
    output_path = project_root / "output" / "virtue_chart.png"

    projects = load_projects(projects_dir)

    if not projects:
        print("No projects found in projects/ directory.", file=sys.stderr)
        sys.exit(1)

    generate_chart(projects, output_path)
    print_summary(projects)


if __name__ == "__main__":
    main()
