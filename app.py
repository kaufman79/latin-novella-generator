#!/usr/bin/env python3
"""
Latin Book Engine - Streamlit App
JSON processor for creating illustrated Latin children's books.
"""

import streamlit as st
import sqlite3
import pandas as pd
import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from scripts.book_manager import (
    create_project,
    load_project,
    update_project_status,
    list_all_projects
)
from scripts.database import LatinDatabase
from scripts.image_generator import generate_page_images, generate_image, get_reference_images_for_page
from scripts.pdf_builder import build_pdf
from scripts.vocabulary_parser import LatinVocabularyParser
from book_schemas import BookProject, BookTranslation, BookPage, VocabularyEntry


# Page config
st.set_page_config(
    page_title="Latin Book Engine",
    page_icon="🏛️",
    layout="wide"
)


def init_session_state():
    """Initialize session state variables."""
    if 'current_project' not in st.session_state:
        st.session_state.current_project = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'json_data' not in st.session_state:
        st.session_state.json_data = None
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = None

    # Multi-stage workflow state
    if 'workflow_stage' not in st.session_state:
        st.session_state.workflow_stage = 0  # 0 = not started, 1-5 = stages
    if 'english_story' not in st.session_state:
        st.session_state.english_story = None
    if 'latin_text' not in st.session_state:
        st.session_state.latin_text = None
    if 'macronized_latin' not in st.session_state:
        st.session_state.macronized_latin = None
    if 'paginated_data' not in st.session_state:
        st.session_state.paginated_data = None
    if 'vocabulary_data' not in st.session_state:
        st.session_state.vocabulary_data = None
    if 'images_generated' not in st.session_state:
        st.session_state.images_generated = False
    if 'style_sheet_template' not in st.session_state:
        st.session_state.style_sheet_template = ""


def get_known_vocabulary() -> list:
    """Get all known words from database."""
    db = LatinDatabase('data/lexicon.db')
    words = db.get_all_known_words()
    db.close()
    return words


def generate_ai_prompt(project: BookProject, known_words: list) -> str:
    """Generate the AI prompt with guidelines and known vocabulary."""

    # Group words by POS for better readability
    nouns = [w for w in known_words if w.get('part_of_speech') == 'noun']
    verbs = [w for w in known_words if w.get('part_of_speech') == 'verb']
    adjectives = [w for w in known_words if w.get('part_of_speech') == 'adjective']
    other_words = [w for w in known_words if w.get('part_of_speech') not in ['noun', 'verb', 'adjective']]

    prompt = f"""# Latin Children's Book: {project.title_english}

## Your Task
Create a simple Latin children's story using words the child KNOWS.

## Story Guidelines
- **Target Pages**: {project.target_pages} pages
- **Sentence Length**: 3-7 words per sentence
- **Sentences Per Page**: 1-2 sentences maximum
- **Tense**: Use present tense primarily (easier for beginners)
- **Vocabulary**: Concrete, visual nouns and action verbs
- **Theme**: {project.theme or 'General'}
- **Target**: Use 80%+ known words (you may introduce 2-3 new words maximum)

## Known Vocabulary - USE THESE WORDS (Any Inflected Form!)

**CRITICAL:** The child knows these LEMMAS. You MUST use any inflected form of these words.

"""

    if nouns:
        prompt += "**Nouns** (use any case/number):\n"
        for word in nouns[:15]:  # Limit to avoid huge prompts
            dict_form = word.get('dictionary_form') or f"{word['lemma']} ({word['english']})"
            prompt += f"- {dict_form}\n"
            prompt += f"  → Can use: nominative, genitive, dative, accusative, ablative (singular/plural)\n"
        if len(nouns) > 15:
            prompt += f"  ... and {len(nouns) - 15} more nouns\n"
        prompt += "\n"

    if verbs:
        prompt += "**Verbs** (use any tense/person/number):\n"
        for word in verbs[:10]:
            dict_form = word.get('dictionary_form') or f"{word['lemma']} ({word['english']})"
            prompt += f"- {dict_form}\n"
            prompt += f"  → Can use: present, imperfect, perfect, etc. - all persons/numbers\n"
        if len(verbs) > 10:
            prompt += f"  ... and {len(verbs) - 10} more verbs\n"
        prompt += "\n"

    if adjectives:
        prompt += "**Adjectives** (use any gender/case/number):\n"
        for word in adjectives[:10]:
            dict_form = word.get('dictionary_form') or f"{word['lemma']} ({word['english']})"
            prompt += f"- {dict_form}\n"
        if len(adjectives) > 10:
            prompt += f"  ... and {len(adjectives) - 10} more adjectives\n"
        prompt += "\n"

    if other_words:
        prompt += "**Other Words**:\n"
        for word in other_words[:10]:
            prompt += f"- {word['lemma']} ({word['english']})\n"
        if len(other_words) > 10:
            prompt += f"  ... and {len(other_words) - 10} more words\n"
        prompt += "\n"

    if not known_words:
        prompt += "**No known words yet** - Feel free to use simple, concrete Latin vocabulary suitable for beginners.\n\n"

    prompt += f"""
## IMPORTANT: Use Different Inflected Forms!
- Don't just use "canis" every time → use "canis, canem, canī, canēs, canibus" as grammar requires
- Don't just use "currit" every time → use "currit, currunt, cucurrit, curre" etc.
- Vary your forms to create natural, grammatically correct Latin

## Art Style
{project.image_config.art_style or 'Colorful, child-friendly illustration'}

## Output Format

Please output a JSON object with this exact structure:

```json
{{
  "title_latin": "Latin Title Here",
  "pages": [
    {{
      "page_number": 1,
      "latin_text": "Latin sentence here.",
      "english_text": "English translation here.",
      "image_prompt": "Detailed image description including style, characters, setting, and mood.",
      "vocabulary_used": ["lemma1", "lemma2"]
    }}
  ],
  "vocabulary": [
    {{
      "latin": "puer",
      "english": "boy",
      "part_of_speech": "noun",
      "dictionary_form": "puer, puerī, m."
    }}
  ]
}}
```

## Important Notes
- Include proper macrons (ā, ē, ī, ō, ū) where appropriate
- In "vocabulary_used", list the LEMMA form even if you used an inflected form in the text
- Image prompts should be detailed and consistent across pages
- Keep the same characters/style throughout the story
- In the vocabulary section, include ALL unique words (known + new)
- Dictionary forms:
  - Nouns: "puer, puerī, m." (nominative, genitive, gender)
  - Verbs: "videō, vidēre, vīdī, vīsum" (principal parts)
  - Adjectives: "bonus, bona, bonum" (masculine, feminine, neuter)

Begin!
"""

    return prompt


def track_book_vocabulary(project: BookProject, translation: BookTranslation):
    """Update database with words used in the book."""
    db = LatinDatabase('data/lexicon.db')

    # Check if this book already exists in the database
    existing_book = db.get_book_by_project_id(project.project_id)
    is_first_build = existing_book is None

    # Get all lemmas used in the book from vocabulary_list
    all_lemmas = set()
    for vocab_entry in translation.vocabulary_list:
        all_lemmas.add(vocab_entry.latin)

    # Check which are known vs new
    known_words = db.get_all_known_words()
    known_lemmas = {w['lemma'] for w in known_words}

    used_known = all_lemmas & known_lemmas
    new_words = all_lemmas - known_lemmas

    # Only update times_seen and add new words on FIRST build
    if is_first_build:
        # Update times_seen for known words
        for lemma in used_known:
            db.update_word_seen(lemma)

        # Add new words to database as mastery_level=1
        for vocab_entry in translation.vocabulary_list:
            if vocab_entry.latin in new_words:
                # Check if word already exists before attempting to add
                existing_word = db.get_known_word_by_lemma(vocab_entry.latin)
                if not existing_word:
                    try:
                        db.add_known_word(
                            lemma=vocab_entry.latin,
                            english=vocab_entry.english,
                            part_of_speech=vocab_entry.part_of_speech,
                            dictionary_form=vocab_entry.dictionary_form,
                            notes=f"Introduced in: {project.title_latin or project.title_english}"
                        )
                    except sqlite3.IntegrityError as e:
                        # Only ignore if it's truly a duplicate (UNIQUE constraint)
                        if "UNIQUE constraint failed" in str(e):
                            st.warning(f"Word '{vocab_entry.latin}' already exists, skipping.")
                        else:
                            # Re-raise for other integrity errors (foreign key, NOT NULL, etc.)
                            raise

    # Calculate coverage percentage
    total_words = len(all_lemmas)
    known_percentage = (len(used_known) / total_words * 100) if total_words > 0 else 0

    # Record book in database
    if is_first_build:
        db.add_book(
            project_id=project.project_id,
            title_latin=project.title_latin or "",
            title_english=project.title_english,
            words_used=list(all_lemmas),
            new_words=list(new_words),
            total_words=total_words,
            known_percentage=known_percentage
        )
    else:
        # Book already exists, just update the metadata (in case text was edited)
        cursor = db.conn.cursor()
        cursor.execute("""
            UPDATE books
            SET words_used = ?, new_words_introduced = ?, total_words = ?, known_word_percentage = ?
            WHERE project_id = ?
        """, (json.dumps(list(all_lemmas)), json.dumps(list(new_words)), total_words, known_percentage, project.project_id))
        db.conn.commit()

    db.close()

    return {
        'total_words': total_words,
        'known_words': len(used_known),
        'new_words': len(new_words),
        'coverage': known_percentage,
        'is_first_build': is_first_build
    }


def validate_json_structure(data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate the JSON structure from AI.

    Args:
        data: Dictionary containing book translation data

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check required top-level keys
        if 'title_latin' not in data:
            return False, "Missing 'title_latin'"
        if 'pages' not in data or not isinstance(data['pages'], list):
            return False, "Missing 'pages' array"
        if 'vocabulary' not in data or not isinstance(data['vocabulary'], list):
            return False, "Missing 'vocabulary' array"

        # Check each page
        for i, page in enumerate(data['pages']):
            required = ['page_number', 'latin_text', 'english_text', 'image_prompt']
            for field in required:
                if field not in page:
                    return False, f"Page {i+1} missing '{field}'"

        # Check vocabulary entries
        for i, vocab in enumerate(data['vocabulary']):
            required = ['latin', 'english', 'part_of_speech', 'dictionary_form']
            for field in required:
                if field not in vocab:
                    return False, f"Vocabulary entry {i+1} missing '{field}'"

        return True, None

    except (TypeError, AttributeError) as e:
        return False, f"Invalid data structure: {str(e)}"


def step_1_create_project():
    """Step 1: Create new book project."""

    # Load default style sheet button (outside form)
    if st.button("📋 Load Default Style Sheet Template"):
        try:
            with open('data/default_style_sheet.txt', 'r') as f:
                st.session_state.style_sheet_template = f.read()
        except FileNotFoundError:
            st.session_state.style_sheet_template = "children's book illustration, watercolor style, warm colors, simple shapes"

    with st.form("project_form"):
        title = st.text_input("Book Title (English)", placeholder="The Hungry Cat")

        col1, col2 = st.columns(2)
        with col1:
            theme = st.text_input("Theme", placeholder="animal, family, food, etc.")
            pages = st.number_input("Target Pages", min_value=4, max_value=20, value=8)

        with col2:
            level = st.number_input("Level (optional)", min_value=1, max_value=10, value=1)

        # Style Sheet Editor
        st.markdown("---")
        st.subheader("🎨 Style Sheet")
        st.caption("Define the visual style for your book. Click 'Load Default Style Sheet Template' above for a starter template.")

        # Get template if loaded
        default_value = st.session_state.get('style_sheet_template', "")

        art_style = st.text_area(
            "Art Style & Visual Guidelines",
            value=default_value,
            height=300,
            placeholder="Define UNIVERSAL visual style only (art style, composition, technical specs).\n\nDO NOT include specific character designs or environment details here.\nThose will be defined separately as reference images in Stage 4.\n\nExample:\nART STYLE:\nWatercolor, whimsical, bright colors\n\nCOMPOSITION:\n- Center framing, eye-level angle\n- Simple perspective\n\nTECHNICAL:\n- Square aspect ratio\n- Bright, flat colors"
        )

        submitted = st.form_submit_button("Create Project")

        if submitted:
            if not title:
                st.error("Please enter a book title")
            else:
                # Create project
                project = create_project(
                    title=title,
                    theme=theme if theme else None,
                    pages=pages,
                    level=level if level else None,
                    art_style=art_style if art_style else None
                )

                st.session_state.current_project = project
                st.session_state.current_step = 2
                # Clear template after use
                if 'style_sheet_template' in st.session_state:
                    del st.session_state.style_sheet_template
                st.success(f"✅ Created project: {project.project_id}")
                st.rerun()


def step_2_get_ai_story():
    """Step 2: Multi-stage guided workflow for story creation."""
    from app_stages import (
        generate_stage_1_prompt, generate_stage_2_prompt, generate_stage_3_prompt,
        generate_stage_4_prompt, generate_stage_5_prompt,
        validate_stage_1_input, validate_stage_2_input, validate_stage_3_input,
        validate_stage_4_input, validate_stage_5_input
    )

    project = st.session_state.current_project

    # Safety check
    if not project:
        st.warning("⚠️ Please create a project first in the 'Create Project' tab")
        return

    st.write(f"**Project**: {project.title_english} (`{project.project_id}`)")

    # Get workflow stage (default to 1 if not started)
    if st.session_state.workflow_stage == 0:
        st.session_state.workflow_stage = 1

    stage = st.session_state.workflow_stage

    # Progress indicator
    st.progress(stage / 5, text=f"Stage {stage} of 5")

    st.markdown("---")

    # Get known vocabulary (needed for stages 1 & 2)
    known_words = get_known_vocabulary()

    # ========== STAGE 1: Story Planning (English) ==========
    if stage == 1:
        st.header("📝 Stage 1: Story Planning (English)")
        st.write("Plan your story in simple English. We'll translate to Latin in the next stage.")

        prompt = generate_stage_1_prompt(project, known_words)

        st.subheader("1️⃣ Copy this prompt to your AI chat")
        st.code(prompt, language="markdown")

        st.markdown("---")
        st.subheader("2️⃣ Paste the AI's response below")
        st.write("Paste the full story text, including title, outline, story, and new words list.")

        english_input = st.text_area(
            "English Story (from AI)",
            value=st.session_state.english_story or "",
            height=300,
            placeholder="Title: Cicadas and the Dragon\nOutline: Bored cicadas...\nStory: [A bunch of cicadas were bored one day...]\nNew words: [\"dragon\", \"gold\", ...]"
        )

        col1, col2 = st.columns([1, 5])
        with col2:
            if st.button("Next: Translate to Latin →", type="primary"):
                valid, error = validate_stage_1_input(english_input)
                if not valid:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.english_story = english_input
                    st.session_state.workflow_stage = 2
                    st.rerun()

    # ========== STAGE 2: Translation to Latin ==========
    elif stage == 2:
        st.header("🏛️ Stage 2: Translation to Latin")
        st.write("Translate your English story using known vocabulary with natural inflections.")

        prompt = generate_stage_2_prompt(project, known_words, st.session_state.english_story)

        st.subheader("1️⃣ Copy this prompt to your AI chat")
        st.code(prompt, language="markdown")

        st.markdown("---")
        st.subheader("2️⃣ Paste the Latin translation below")

        latin_input = st.text_area(
            "Latin Translation (no macrons yet)",
            value=st.session_state.latin_text or "",
            height=300,
            placeholder="Scene 1: Canis in horto currit.\nScene 2: Canis pilam videt.\n..."
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back: Edit Story"):
                st.session_state.workflow_stage = 1
                st.rerun()
        with col2:
            if st.button("Next: Add Macrons →", type="primary"):
                valid, error = validate_stage_2_input(latin_input)
                if not valid:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.latin_text = latin_input
                    st.session_state.workflow_stage = 3
                    st.rerun()

    # ========== STAGE 3: Macronization ==========
    elif stage == 3:
        st.header("✏️ Stage 3: Add Macrons")
        st.write("Add proper macrons (ā, ē, ī, ō, ū) to mark long vowels.")

        prompt = generate_stage_3_prompt(st.session_state.latin_text)

        st.subheader("1️⃣ Copy this prompt to your AI chat")
        st.code(prompt, language="markdown")

        st.markdown("---")
        st.subheader("2️⃣ Paste the macronized Latin below")

        macronized_input = st.text_area(
            "Latin with Macrons",
            value=st.session_state.macronized_latin or "",
            height=300,
            placeholder="Scene 1: Canis in hortō currit.\nScene 2: Canis pilam videt.\n..."
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back: Edit Translation"):
                st.session_state.workflow_stage = 2
                st.rerun()
        with col2:
            if st.button("Next: Create Pages →", type="primary"):
                valid, error = validate_stage_3_input(macronized_input)
                if not valid:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.macronized_latin = macronized_input
                    st.session_state.workflow_stage = 4
                    st.rerun()

    # ========== STAGE 4: Pagination + Image Prompts ==========
    elif stage == 4:
        st.header("📖 Stage 4: Pagination & Image Prompts")
        st.write("Split the story into pages and create detailed image prompts.")

        prompt = generate_stage_4_prompt(
            project,
            st.session_state.macronized_latin,
            st.session_state.english_story
        )

        st.subheader("1️⃣ Copy this prompt to your AI chat")
        st.code(prompt, language="markdown")

        st.markdown("---")
        st.subheader("2️⃣ Paste the JSON output below")

        pagination_input = st.text_area(
            "Pagination JSON",
            value=st.session_state.paginated_data or "",
            height=300,
            placeholder='{\n  "title_latin": "Cicadae et Draco",\n  "cover_image_prompt": "Cover showing all characters...",\n  "pages": [\n    {\n      "page_number": 1,\n      "latin_text": "...",\n      "english_text": "...",\n      "image_prompt": "..."\n    }\n  ]\n}'
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back: Edit Macrons"):
                st.session_state.workflow_stage = 3
                st.rerun()
        with col2:
            if st.button("Next: Extract Vocabulary →", type="primary"):
                valid, error, data = validate_stage_4_input(pagination_input)
                if not valid:
                    st.error(f"❌ {error}")
                else:
                    st.session_state.paginated_data = pagination_input
                    st.session_state.workflow_stage = 5
                    if data:
                        st.success(f"✅ Validated {len(data['pages'])} pages")
                    st.rerun()

    # ========== STAGE 5: Vocabulary Extraction ==========
    elif stage == 5:
        st.header("📚 Stage 5: Vocabulary List")
        st.write("Automatically extract vocabulary using LatinCy (94.66% lemmatization accuracy).")

        # Check if vocabulary has already been extracted
        if st.session_state.vocabulary_data:
            vocab_data = json.loads(st.session_state.vocabulary_data)
            st.success(f"✅ Vocabulary extracted: {len(vocab_data['vocabulary'])} words")

            with st.expander("📖 View Vocabulary", expanded=False):
                for entry in vocab_data['vocabulary'][:10]:  # Show first 10
                    st.write(f"**{entry['latin']}** - {entry['english']} ({entry['part_of_speech']})")
                if len(vocab_data['vocabulary']) > 10:
                    st.write(f"... and {len(vocab_data['vocabulary']) - 10} more")
        else:
            st.info("👉 Click 'Extract Vocabulary' to automatically parse all Latin words from your book.")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back: Edit Pages"):
                st.session_state.workflow_stage = 4
                st.rerun()

        with col2:
            if st.button("🔍 Extract Vocabulary", type="secondary"):
                # Get all Latin text from pages
                page_valid, page_error, page_data = validate_stage_4_input(st.session_state.paginated_data)
                if not page_valid or not page_data:
                    st.error(f"❌ Error in pagination data: {page_error}")
                    return

                # Combine all Latin text
                all_latin_text = "\n".join([page['latin_text'] for page in page_data['pages']])

                with st.spinner("Parsing Latin vocabulary with LatinCy..."):
                    try:
                        api_key = os.getenv('GEMINI_API_KEY')
                        if not api_key:
                            st.error("❌ GEMINI_API_KEY not found in environment")
                            return

                        parser = LatinVocabularyParser()
                        vocab_list = parser.parse_book_vocabulary(all_latin_text, api_key)

                        vocab_data = {"vocabulary": vocab_list}
                        st.session_state.vocabulary_data = json.dumps(vocab_data, indent=2)

                        st.success(f"✅ Extracted {len(vocab_list)} vocabulary words!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error extracting vocabulary: {e}")
                        import traceback
                        st.code(traceback.format_exc())

        with col3:
            if st.button("Complete & Generate Book →", type="primary", disabled=not st.session_state.vocabulary_data):
                # Validate pagination data
                page_valid, page_error, page_data = validate_stage_4_input(st.session_state.paginated_data)
                if not page_valid or not page_data:
                    st.error(f"❌ Error in pagination data: {page_error}")
                    return

                vocab_data = json.loads(st.session_state.vocabulary_data)

                # Combine all data into final JSON structure
                combined_json = {
                    "title_latin": page_data.get('title_latin', project.title_english),
                    "cover_image_prompt": page_data.get('cover_image_prompt', ''),
                    "characters": page_data.get('characters', []),  # Include characters from Stage 4
                    "locations": page_data.get('locations', []),  # Include locations from Stage 4
                    "pages": page_data['pages'],
                    "vocabulary": vocab_data['vocabulary']
                }

                st.session_state.json_data = combined_json
                st.session_state.current_step = 3
                st.session_state.workflow_stage = 0  # Reset for next project
                st.success(f"✅ Complete! {len(vocab_data['vocabulary'])} vocabulary entries extracted.")
                st.rerun()


def step_3_generate_book():
    """Step 3: Generate images and build PDF."""
    project = st.session_state.current_project
    json_data = st.session_state.json_data

    # Safety check
    if not project:
        st.warning("⚠️ Please create a project first in the 'Create Project' tab")
        return

    st.write(f"**Project**: {project.title_english} (`{project.project_id}`)")

    # Use existing translation if available, otherwise create from JSON
    if project.translation:
        translation = project.translation
        st.write(f"**Latin Title**: {translation.title_latin}")
        st.write(f"**Pages**: {len(translation.pages)}")
    elif json_data:
        st.write(f"**Latin Title**: {json_data['title_latin']}")
        st.write(f"**Pages**: {len(json_data['pages'])}")

        # Convert JSON to BookTranslation object
        translation = BookTranslation(
            title_latin=json_data['title_latin'],
            title_english=project.title_english,
            pages=[BookPage(**page) for page in json_data['pages']],
            vocabulary_list=[VocabularyEntry(**v) for v in json_data['vocabulary']]
        )

        # Update project
        project.title_latin = translation.title_latin
        project.translation = translation
        project.cover_image_prompt = json_data.get('cover_image_prompt', '')
        update_project_status(project, 'reviewed')
    else:
        st.error("No translation data available. Please go back to Step 2.")
        return

    st.markdown("---")

    # Parse characters from JSON if using new format
    if json_data and 'characters' in json_data:
        # Update project with characters from Stage 4
        from book_schemas import Character
        project.characters = [Character(**char_data) for char_data in json_data['characters']]
        # Save to project
        update_project_status(project, project.status)

    # Clean art_style if project has characters/locations (remove redundant sections)
    if (project.characters or project.locations) and project.image_config.art_style:
        from scripts.book_manager import clean_art_style
        cleaned = clean_art_style(project.image_config.art_style)
        if cleaned != project.image_config.art_style:
            project.image_config.art_style = cleaned
            update_project_status(project, project.status)
            st.info("ℹ️ Cleaned redundant CHARACTER DESIGN and ENVIRONMENT sections from art style (now using reference images)")

    images_dir = Path('projects') / project.project_id / 'images'
    images_dir.mkdir(parents=True, exist_ok=True)

    # ===================================================================
    # SECTION 1: Generate Character References
    # ===================================================================
    st.header("📋 Step 1: Character References")

    if project.characters:
        # Check if all character references are generated
        all_refs_exist = all(
            c.reference_image_path and Path(c.reference_image_path).exists()
            for c in project.characters
        )

        if not all_refs_exist:
            st.info(f"Found {len(project.characters)} characters. Generate reference images for consistency.")

            # Show character list with editable prompts
            st.write("**Review and edit prompts before generating:**")

            # Store edited prompts in session state
            if 'char_prompts' not in st.session_state:
                st.session_state.char_prompts = {}

            for char in project.characters:
                with st.expander(f"**{char.name}**"):
                    # Default character-specific prompt (just the character part, not the full style guide)
                    # Check if description already has the reference sheet suffix to avoid duplication
                    if "Character reference sheet style" in char.description:
                        default_char_prompt = char.description
                    else:
                        default_char_prompt = f"{char.description}. Standing in neutral pose on plain white background. Character reference sheet style."

                    # Get or initialize prompt (store only the character-specific part)
                    if char.name not in st.session_state.char_prompts:
                        st.session_state.char_prompts[char.name] = default_char_prompt

                    # Editable prompt (only shows character-specific part)
                    st.session_state.char_prompts[char.name] = st.text_area(
                        f"Character prompt for {char.name}:",
                        value=st.session_state.char_prompts[char.name],
                        key=f"char_prompt_{char.name}",
                        height=100,
                        help="Edit the character-specific part. The full style guide will be automatically added when generating."
                    )

                    st.caption("💡 The full art style guide will be prepended automatically during generation.")

            if st.button("🎨 Generate Character References", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, char in enumerate(project.characters):
                    status_text.text(f"Generating reference for {char.name}...")

                    try:
                        # Build full prompt: style guide + character-specific prompt
                        char_specific_prompt = st.session_state.char_prompts.get(char.name, char.description)
                        full_prompt = f"{project.image_config.art_style}. {char_specific_prompt}"

                        img = generate_image(full_prompt, reference_image_paths=None)

                        # Save reference image
                        ref_path = images_dir / f'char_{char.name.lower().replace(" ", "_")}.png'
                        img.save(ref_path)

                        # Update character
                        char.reference_image_path = str(ref_path)

                        progress_bar.progress((i + 1) / len(project.characters))

                    except Exception as e:
                        st.error(f"Error generating {char.name}: {e}")

                # Save project with updated character paths
                update_project_status(project, project.status)
                status_text.text("✅ All character references generated!")
                st.success("Character references complete!")

                # Clear session state prompts after successful generation
                st.session_state.char_prompts = {}
                st.rerun()

        else:
            st.success(f"✅ {len(project.characters)} character references ready!")

            # Display character reference grid
            cols = st.columns(min(len(project.characters), 4))
            for i, char in enumerate(project.characters):
                with cols[i % 4]:
                    if char.reference_image_path and Path(char.reference_image_path).exists():
                        st.image(char.reference_image_path, caption=char.name, use_container_width=True)

                        # Regeneration option
                        with st.expander(f"🔄 Regenerate {char.name}"):
                            edited_desc = st.text_area(
                                "Character description:",
                                value=char.description,
                                key=f"edit_char_{char.name}",
                                height=100
                            )

                            if st.button(f"Regenerate", key=f"regen_char_{char.name}"):
                                try:
                                    full_prompt = f"{project.image_config.art_style}. {edited_desc}. Standing in neutral pose on plain white background."
                                    img = generate_image(full_prompt)
                                    img.save(char.reference_image_path)

                                    # Update description
                                    char.description = edited_desc
                                    update_project_status(project, project.status)

                                    st.success(f"✅ {char.name} regenerated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    else:
        # No characters (old format with cover_image_prompt)
        st.info("Using legacy cover image format. No character references needed.")

    st.markdown("---")

    # ===================================================================
    # SECTION 1B: Generate Location References
    # ===================================================================
    st.header("🏠 Step 1b: Location References")

    # Parse locations from JSON if using new format
    if json_data and 'locations' in json_data:
        from book_schemas import Location
        project.locations = [Location(**loc_data) for loc_data in json_data['locations']]
        update_project_status(project, project.status)

    if project.locations:
        # Check if all location references are generated
        all_loc_refs_exist = all(
            l.reference_image_path and Path(l.reference_image_path).exists()
            for l in project.locations
        )

        if not all_loc_refs_exist:
            st.info(f"Found {len(project.locations)} locations. Generate reference images for consistent settings.")

            # Show location list with editable prompts
            st.write("**Review and edit prompts before generating:**")

            # Store edited prompts in session state
            if 'loc_prompts' not in st.session_state:
                st.session_state.loc_prompts = {}

            for loc in project.locations:
                with st.expander(f"**{loc.name}**"):
                    # Default location-specific prompt (just the location part, not the full style guide)
                    # Check if description already has the reference sheet suffix to avoid duplication
                    if "Location reference image" in loc.description:
                        default_loc_prompt = loc.description
                    else:
                        default_loc_prompt = f"{loc.description}. Empty room with no people, neutral eye-level angle. Location reference image for consistent setting across multiple scenes."

                    # Get or initialize prompt (store only the location-specific part)
                    if loc.name not in st.session_state.loc_prompts:
                        st.session_state.loc_prompts[loc.name] = default_loc_prompt

                    # Editable prompt (only shows location-specific part)
                    st.session_state.loc_prompts[loc.name] = st.text_area(
                        f"Location prompt for {loc.name}:",
                        value=st.session_state.loc_prompts[loc.name],
                        key=f"loc_prompt_{loc.name}",
                        height=120,
                        help="Edit the location-specific part. The full style guide will be automatically added when generating."
                    )

                    st.caption("💡 The full art style guide will be prepended automatically during generation.")

            if st.button("🎨 Generate Location References", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, loc in enumerate(project.locations):
                    status_text.text(f"Generating reference for {loc.name}...")

                    try:
                        # Build full prompt: style guide + location-specific prompt
                        loc_specific_prompt = st.session_state.loc_prompts.get(loc.name, loc.description)
                        full_prompt = f"{project.image_config.art_style}. {loc_specific_prompt}"

                        img = generate_image(full_prompt, reference_image_paths=None)

                        # Save reference image
                        ref_path = images_dir / f'loc_{loc.name.lower().replace(" ", "_")}.png'
                        img.save(ref_path)

                        # Update location
                        loc.reference_image_path = str(ref_path)

                        progress_bar.progress((i + 1) / len(project.locations))

                    except Exception as e:
                        st.error(f"Error generating {loc.name}: {e}")

                # Save project with updated location paths
                update_project_status(project, project.status)
                status_text.text("✅ All location references generated!")
                st.success("Location references complete!")

                # Clear session state prompts after successful generation
                st.session_state.loc_prompts = {}
                st.rerun()

        else:
            st.success(f"✅ {len(project.locations)} location references ready!")

            # Display location reference grid
            cols = st.columns(min(len(project.locations), 3))
            for i, loc in enumerate(project.locations):
                with cols[i % 3]:
                    if loc.reference_image_path and Path(loc.reference_image_path).exists():
                        st.image(loc.reference_image_path, caption=loc.name, use_container_width=True)

                        # Regeneration option
                        with st.expander(f"🔄 Regenerate {loc.name}"):
                            edited_desc = st.text_area(
                                "Location description:",
                                value=loc.description,
                                key=f"edit_loc_{loc.name}",
                                height=100
                            )

                            if st.button(f"Regenerate", key=f"regen_loc_{loc.name}"):
                                try:
                                    full_prompt = f"{project.image_config.art_style}. {edited_desc}. Empty room with no people."
                                    img = generate_image(full_prompt)
                                    img.save(loc.reference_image_path)

                                    # Update description
                                    loc.description = edited_desc
                                    update_project_status(project, project.status)

                                    st.success(f"✅ {loc.name} regenerated!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    else:
        st.info("No locations defined. Add locations to your project configuration.")

    st.markdown("---")

    # ===================================================================
    # SECTION 2: Select Characters Per Page
    # ===================================================================

    if project.characters or project.locations:
        st.header("👥🏠 Step 2: Configure Each Page")
        st.write("Choose which characters and location appear in each scene. This controls which reference images are used.")

        # Check how many pages have selections
        pages_configured = sum(1 for p in translation.pages if (p.characters or (hasattr(p, 'location') and p.location)))
        st.write(f"**Progress:** {pages_configured}/{len(translation.pages)} pages configured")

        # Show all pages with character and location selection
        for page in translation.pages:
            with st.expander(f"📄 Page {page.page_number}: {page.latin_text[:50]}..."):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write("**Latin:**")
                    st.text(page.latin_text)
                    st.write("**English:**")
                    st.text(page.english_text)
                    st.write("**Scene Description:**")
                    st.text(page.image_prompt[:150] + "...")

                with col2:
                    # Initialize variables
                    selected_location = None
                    selected_chars = []

                    # Location selectbox (if locations exist)
                    if project.locations:
                        location_names = [l.name for l in project.locations]
                        location_names = ["(None)"] + location_names  # Add None option

                        current_location = page.location if hasattr(page, 'location') and page.location else "(None)"

                        selected_location = st.selectbox(
                            "Location/Setting:",
                            options=location_names,
                            index=location_names.index(current_location) if current_location in location_names else 0,
                            key=f"loc_select_page_{page.page_number}",
                            help="Select the location for this scene"
                        )

                    # Character multiselect
                    if project.characters:
                        character_names = [c.name for c in project.characters]

                        selected_chars = st.multiselect(
                            "Characters in this scene:",
                            options=character_names,
                            default=page.characters if page.characters else [],
                            key=f"chars_select_page_{page.page_number}",
                            help="Select which characters should appear in this image"
                        )

                    # Save button
                    if st.button("💾 Save Selection", key=f"save_page_{page.page_number}"):
                        # Save location
                        if project.locations and selected_location is not None:
                            page.location = None if selected_location == "(None)" else selected_location

                        # Save characters
                        if project.characters:
                            page.characters = selected_chars

                        update_project_status(project, project.status)
                        st.success(f"✅ Page {page.page_number} updated!")
                        st.rerun()

                    # Show current selection
                    status_parts = []
                    if hasattr(page, 'location') and page.location:
                        status_parts.append(f"📍 {page.location}")
                    if page.characters:
                        status_parts.append(f"👥 {', '.join(page.characters)}")

                    if status_parts:
                        st.write(f"**Current:** {' | '.join(status_parts)}")
                    else:
                        st.warning("No characters or location selected")

        st.markdown("---")

    # ===================================================================
    # SECTION 3: Generate Page Images
    # ===================================================================

    st.header("🎨 Step 3: Generate Page Images")

    # Check if page images exist
    page_images_exist = len(list(images_dir.glob('page_*.png'))) > 0

    if not page_images_exist:
        # Check if we can generate (need references if using new format)
        can_generate = True
        warnings = []

        if project.characters:
            # New format: need character references
            if not all(c.reference_image_path for c in project.characters):
                can_generate = False
                warnings.append("⚠️ Generate character references first (Step 1)")

        if project.locations:
            # Need location references
            if not all(l.reference_image_path for l in project.locations):
                can_generate = False
                warnings.append("⚠️ Generate location references first (Step 1b)")

        for warning in warnings:
            st.warning(warning)

        if can_generate:
            if st.button("🎨 Generate All Page Images", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                num_pages = len(translation.pages)
                for i, page in enumerate(translation.pages):
                    status_text.text(f"Generating page {page.page_number}/{num_pages}...")

                    try:
                        # Get reference paths using priority system (location + characters, max 3)
                        ref_paths = get_reference_images_for_page(page, project)

                        # Build prompt
                        full_prompt = f"{project.image_config.art_style}. {page.image_prompt}"

                        # Generate image with location and character references
                        img = generate_image(full_prompt, reference_image_paths=ref_paths)

                        # Save
                        img_path = images_dir / f'page_{page.page_number:02d}.png'
                        img.save(img_path)
                        page.image_path = str(img_path)

                        progress_bar.progress((i + 1) / num_pages)

                    except Exception as e:
                        st.error(f"Error generating page {page.page_number}: {e}")

                status_text.text("✅ All page images generated!")
                update_project_status(project, 'images_generated')
                st.success("🎨 Page images complete!")
                st.rerun()

    else:
        st.success("✅ All page images generated!")

    # ===================================================================
    # Display Generated Page Images
    # ===================================================================

    if page_images_exist:
        st.subheader("📖 Generated Page Images")

        image_files = sorted(images_dir.glob('page_*.png'))

        for img_path in image_files:
            # Extract page number from filename
            page_num = int(img_path.stem.split('_')[1])
            page = next((p for p in translation.pages if p.page_number == page_num), None)

            if page:
                with st.expander(f"Page {page_num}", expanded=False):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.image(str(img_path), use_container_width=True)

                    with col2:
                        st.write("**Latin:**")
                        st.text(page.latin_text)
                        st.write("**English:**")
                        st.text(page.english_text)
                        st.write("**Scene Setup:**")
                        info_parts = []
                        if hasattr(page, 'location') and page.location:
                            info_parts.append(f"📍 {page.location}")
                        if page.characters:
                            info_parts.append(f"👥 {', '.join(page.characters)}")
                        if info_parts:
                            st.write(" | ".join(info_parts))
                        else:
                            st.write("(No references selected)")

                        # Regeneration UI (without nested expander)
                        st.write("---")
                        st.write("**🔄 Regenerate This Image**")

                        custom_instructions = st.text_area(
                            "Custom instructions:",
                            key=f"custom_page_{page_num}",
                            placeholder="e.g., 'Make background darker', 'Add more trees'",
                            height=68
                        )

                        use_current = st.checkbox(
                            "Use current image as reference (for small tweaks)",
                            key=f"use_current_{page_num}"
                        )

                        if st.button(f"🔄 Regenerate", key=f"regen_page_{page_num}"):
                            try:

                                # Get references
                                ref_paths = []
                                if use_current:
                                    # Use current image as reference for tweaking
                                    ref_paths = [str(img_path)]
                                else:
                                    # Use location + character references with priority system
                                    ref_paths = get_reference_images_for_page(page, project)

                                # Build prompt
                                base_prompt = f"{project.image_config.art_style}. {page.image_prompt}"
                                if custom_instructions.strip():
                                    base_prompt = f"{base_prompt}. {custom_instructions}"

                                # Generate
                                img = generate_image(base_prompt, reference_image_paths=ref_paths)
                                img.save(img_path)

                                st.success(f"✅ Page {page_num} regenerated!")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error: {e}")

    st.markdown("---")

    # Edit text section
    st.subheader("✏️ Edit Text Before Building PDF")

    with st.form("edit_text_form"):
        st.write("**Edit titles and text for each page:**")

        # Edit titles
        col1, col2 = st.columns(2)
        with col1:
            edited_title_latin = st.text_input(
                "Latin Title",
                value=translation.title_latin,
                key="edit_title_latin"
            )
        with col2:
            edited_title_english = st.text_input(
                "English Title",
                value=translation.title_english,
                key="edit_title_english"
            )

        st.markdown("---")
        st.write("**Edit page text:**")

        # Edit each page
        edited_pages = []
        for i, page in enumerate(translation.pages):
            st.write(f"**Page {page.page_number}**")
            col1, col2 = st.columns(2)

            with col1:
                edited_latin = st.text_area(
                    f"Latin (Page {page.page_number})",
                    value=page.latin_text,
                    height=100,
                    key=f"edit_latin_{i}"
                )

            with col2:
                edited_english = st.text_area(
                    f"English (Page {page.page_number})",
                    value=page.english_text,
                    height=100,
                    key=f"edit_english_{i}"
                )

            edited_pages.append({
                'page_number': page.page_number,
                'latin': edited_latin,
                'english': edited_english,
                'image_path': page.image_path,
                'image_prompt': page.image_prompt
            })

        # Save edits button
        if st.form_submit_button("💾 Save Edits", type="primary"):
            # Update translation with edited text
            translation.title_latin = edited_title_latin
            translation.title_english = edited_title_english

            for i, page in enumerate(translation.pages):
                page.latin_text = edited_pages[i]['latin']
                page.english_text = edited_pages[i]['english']

            # Update project
            project.title_latin = edited_title_latin
            project.translation = translation

            st.success("✅ Text edits saved!")
            st.rerun()

    st.markdown("---")

    # Build PDF button
    if st.button("📄 Build PDF"):
        with st.spinner("Building PDF..."):
            try:
                output_path = Path('projects') / project.project_id / 'book.pdf'
                build_pdf(project, translation, output_path)
                update_project_status(project, 'pdf_built')

                # Track vocabulary usage
                stats = track_book_vocabulary(project, translation)

                st.success(f"✅ PDF built: {output_path}")

                # Display vocabulary stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Unique Words", stats['total_words'])
                with col2:
                    st.metric("Known Words", stats['known_words'])
                with col3:
                    st.metric("New Words", stats['new_words'])
                with col4:
                    st.metric("Coverage", f"{stats['coverage']:.1f}%")

                # Show what was added to database
                if stats['new_words'] > 0:
                    st.info(f"📚 Added {stats['new_words']} new words to your vocabulary database! Check the 'Vocabulary Database' tab to see them.")
                else:
                    st.info("📚 All words in this book were already in your vocabulary database. Updated 'times_seen' counters for known words.")

                # Download button
                with open(output_path, 'rb') as f:
                    st.download_button(
                        label="📥 Download PDF",
                        data=f.read(),
                        file_name=f"{project.project_id}.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"Error building PDF: {e}")

    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Project"):
        st.session_state.current_project = None
        st.session_state.current_step = 1
        st.session_state.json_data = None
        st.rerun()


def vocab_database_viewer():
    """Known vocabulary database viewer and manager."""
    db = LatinDatabase('data/lexicon.db')

    # Get summary stats
    stats = db.get_summary_stats()

    # Header with stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Known Words", stats['total_known_words'])
    with col2:
        mastery = stats['mastery_distribution']
        st.metric("Mastered", mastery.get(3, 0))
    with col3:
        st.metric("Familiar", mastery.get(2, 0))
    with col4:
        st.metric("Books Created", stats['total_books'])

    st.markdown("---")

    # Add new word form
    with st.expander("➕ Add New Known Word", expanded=False):
        with st.form("add_word_form"):
            col1, col2 = st.columns(2)
            with col1:
                lemma = st.text_input("Lemma (base form)", placeholder="puer, currō, magnus")
                english = st.text_input("English", placeholder="boy, run, large")
            with col2:
                pos = st.selectbox("Part of Speech", ["noun", "verb", "adjective", "adverb", "pronoun", "preposition", "conjunction", "other"])
                dict_form = st.text_input("Dictionary Form (optional)", placeholder="puer, puerī, m.")

            notes = st.text_area("Notes (optional)", placeholder="Son uses this frequently...")

            if st.form_submit_button("Add Word"):
                if lemma and english:
                    try:
                        db.add_known_word(lemma, english, pos, dict_form, notes)
                        st.success(f"✅ Added: {lemma} ({english})")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"❌ Word '{lemma}' already exists in database")
                else:
                    st.error("Please enter both lemma and English translation")

    st.markdown("---")

    # Search and filter controls
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("🔍 Search Latin/English", placeholder="puer, boy, etc.")
    with col2:
        filter_pos = st.selectbox("Filter by Part of Speech", ["All", "noun", "verb", "adjective", "adverb", "pronoun", "preposition", "other"])

    # Get words
    if search_term:
        all_words = db.search_known_words(search_term)
    elif filter_pos != "All":
        all_words = db.get_words_by_pos(filter_pos)
    else:
        all_words = db.get_all_known_words()

    # Display words
    if all_words:
        st.write(f"**Showing {len(all_words)} words**")

        # Convert to DataFrame
        df = pd.DataFrame(all_words)

        # Display table with actions
        display_columns = ['lemma', 'english', 'part_of_speech', 'dictionary_form', 'mastery_level', 'times_seen', 'last_seen_date']
        available_columns = [col for col in display_columns if col in df.columns]

        st.dataframe(
            df[available_columns].rename(columns={
                'lemma': 'Latin',
                'english': 'English',
                'part_of_speech': 'POS',
                'dictionary_form': 'Dict. Form',
                'mastery_level': 'Mastery',
                'times_seen': 'Seen',
                'last_seen_date': 'Last Seen'
            }),
            use_container_width=True,
            hide_index=True
        )

        # Mastery level legend
        st.caption("**Mastery:** 1=New, 2=Familiar, 3=Mastered")

        # Export button
        st.markdown("---")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name="known_latin_words.csv",
            mime="text/csv"
        )
    else:
        st.info("📚 No known words yet. Add your first word above!")

    db.close()


def sidebar():
    """Sidebar with project selector."""
    st.sidebar.title("🏛️ Latin Book Engine")

    st.sidebar.markdown("---")

    # Project selector
    st.sidebar.subheader("📚 Existing Projects")
    projects = list_all_projects()

    if projects:
        project_names = [f"{p.project_id} ({p.status})" for p in projects]
        selected = st.sidebar.selectbox("Load Project", ["-- New Project --"] + project_names)

        if selected == "-- New Project --":
            # Reset to new project mode
            if st.sidebar.button("New Project"):
                st.session_state.current_project = None
                st.session_state.current_step = 1
                st.session_state.json_data = None
                st.rerun()
        else:
            # Load existing project
            project_id = selected.split(" (")[0]

            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("Load", key="load_btn"):
                    project = load_project(project_id)
                    if project:
                        st.session_state.current_project = project
                        st.session_state.json_data = None
                        st.session_state.delete_confirm = None
                        # Determine step based on status
                        if project.status == 'initialized':
                            st.session_state.current_step = 2
                        elif project.status in ['translated', 'reviewed', 'images_generated', 'pdf_built']:
                            st.session_state.current_step = 3
                        st.rerun()

            with col2:
                if st.button("🗑️", key="delete_btn", help="Delete project"):
                    st.session_state.delete_confirm = project_id

            # Show confirmation if delete was clicked
            if st.session_state.delete_confirm == project_id:
                st.sidebar.warning(f"⚠️ Delete **{project_id}**?")
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("✅ Yes", key="confirm_yes"):
                        import shutil
                        project_path = Path('projects') / project_id
                        if project_path.exists():
                            shutil.rmtree(project_path)
                            # Clear current project if it was deleted
                            if st.session_state.current_project and st.session_state.current_project.project_id == project_id:
                                st.session_state.current_project = None
                                st.session_state.current_step = 1
                                st.session_state.json_data = None
                            st.session_state.delete_confirm = None
                            st.rerun()
                with col2:
                    if st.button("❌ No", key="confirm_no"):
                        st.session_state.delete_confirm = None
                        st.rerun()
    else:
        st.sidebar.write("No projects yet")

    st.sidebar.markdown("---")
    st.sidebar.caption("💡 Use tabs above to navigate between steps")


def main():
    """Main app."""
    init_session_state()
    sidebar()

    # Use tabs for navigation
    tab1, tab2, tab3, tab4 = st.tabs(["📚 Create Project", "📝 Get AI Story", "🎨 Generate Book", "📖 Vocabulary Database"])

    with tab1:
        step_1_create_project()

    with tab2:
        step_2_get_ai_story()

    with tab3:
        step_3_generate_book()

    with tab4:
        vocab_database_viewer()


if __name__ == '__main__':
    main()
