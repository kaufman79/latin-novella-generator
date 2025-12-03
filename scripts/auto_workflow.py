#!/usr/bin/env python3
"""
Automated workflow functions for the Streamlit app.
Provides simplified, automated book creation with review points.
"""

import streamlit as st
from pathlib import Path
import json

from book_schemas import BookProject, BookTranslation, BookPage, VocabularyEntry
from scripts.gemini_integration import translate_to_latin, create_pages_and_vocabulary
from scripts.database import LatinDatabase
from scripts.book_manager import update_project_status
from config import DB_PATH


def auto_step_1_translate(project: BookProject):
    """
    Auto Step 1: English input → Latin translation

    Shows:
    - Text area for English story
    - Button to auto-translate
    - Editable Latin output
    - Button to proceed to pagination
    """
    st.header("Step 1: English Story → Latin Translation")

    # English input
    st.subheader("📝 Your English Story")
    st.caption(f"Theme: {project.theme or 'General'} | Target pages: {project.target_pages}")

    english_story = st.text_area(
        "Paste or write your English story here",
        height=300,
        placeholder="Once upon a time, there was a curious cat who loved to explore...",
        key="english_story_input",
        value=st.session_state.get('english_story', project.source_text or '')
    )

    # Word count helper
    if english_story:
        word_count = len(english_story.split())
        st.caption(f"📊 Word count: {word_count}")
        if word_count < 50:
            st.warning("⚠️ Story might be too short for {project.target_pages} pages")
        elif word_count > 300:
            st.warning("⚠️ Story might be too long for a simple children's book")

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🌐 Auto-Translate to Latin", type="primary", disabled=not english_story):
            st.session_state.english_story = english_story
            project.source_text = english_story
            update_project_status(project, 'translating')

            with st.spinner("Calling Gemini API to translate... This may take 30-60 seconds..."):
                try:
                    db = LatinDatabase(DB_PATH)
                    latin_text = translate_to_latin(english_story, project, db)
                    db.close()

                    # Store in session state
                    st.session_state.latin_text = latin_text
                    st.success("✅ Translation complete!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Translation failed: {str(e)}")
                    st.info("💡 Tip: Check that GEMINI_API_KEY is set in your .env file")

    with col2:
        st.caption("This will use Gemini API to translate your English story to simple Latin suitable for children.")

    # Show Latin output if available
    if st.session_state.get('latin_text'):
        st.markdown("---")
        st.subheader("🏛️ Latin Translation")

        edited_latin = st.text_area(
            "Review and edit the Latin translation if needed",
            value=st.session_state.latin_text,
            height=250,
            key="latin_text_editor"
        )

        st.session_state.latin_text = edited_latin

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📖 Create Pages & Vocabulary", type="primary"):
                st.session_state.auto_workflow_step = 2
                st.rerun()
        with col2:
            st.caption("This will automatically paginate the story and extract vocabulary.")


def auto_step_2_paginate(project: BookProject):
    """
    Auto Step 2: Latin text → Paginated book with vocabulary

    Shows:
    - Latin text (read-only reference)
    - Button to auto-create pages
    - Editable page-by-page view
    - Button to proceed to image generation
    """
    st.header("Step 2: Pagination & Vocabulary")

    latin_text = st.session_state.get('latin_text', '')
    english_text = st.session_state.get('english_story', '')

    # Show Latin text reference
    with st.expander("📜 Latin Text (Reference)", expanded=False):
        st.text_area("", value=latin_text, height=150, disabled=True, label_visibility="collapsed")

    # Check if pages already created
    if not st.session_state.get('pages_data'):
        st.subheader("📄 Create Pages")
        st.caption(f"Target: {project.target_pages} pages with ~1-2 sentences each")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🤖 Auto-Create Pages", type="primary"):
                with st.spinner("Calling Gemini API to create pages... This may take 30-60 seconds..."):
                    try:
                        pages_data = create_pages_and_vocabulary(
                            latin_text,
                            english_text,
                            project
                        )

                        # Store in session
                        st.session_state.pages_data = pages_data
                        st.success("✅ Pages created!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Failed to create pages: {str(e)}")
                        st.info("💡 Tip: Make sure your Latin text is not too long or complex")
        with col2:
            st.caption("This will divide your story into pages, create image prompts, and extract vocabulary.")

    # Show pages for review/editing
    if st.session_state.get('pages_data'):
        st.markdown("---")
        st.subheader("📖 Review Pages")

        pages_data = st.session_state.pages_data

        # Edit title if needed
        col1, col2 = st.columns(2)
        with col1:
            pages_data['title_latin'] = st.text_input(
                "Latin Title",
                value=pages_data.get('title_latin', project.title_latin or ''),
                key="title_latin_edit"
            )
        with col2:
            pages_data['title_english'] = st.text_input(
                "English Title",
                value=pages_data.get('title_english', project.title_english),
                key="title_english_edit"
            )

        # Page editor
        st.markdown("#### Pages")
        for i, page in enumerate(pages_data['pages']):
            with st.expander(f"📄 Page {page['page_number']}", expanded=i < 2):
                col1, col2 = st.columns(2)
                with col1:
                    page['latin_text'] = st.text_area(
                        "Latin Text",
                        value=page['latin_text'],
                        height=80,
                        key=f"page_{i}_latin"
                    )
                with col2:
                    page['english_text'] = st.text_area(
                        "English Text",
                        value=page['english_text'],
                        height=80,
                        key=f"page_{i}_english"
                    )

                page['image_prompt'] = st.text_area(
                    "Image Prompt (describe the scene, not character appearance)",
                    value=page['image_prompt'],
                    height=100,
                    key=f"page_{i}_prompt"
                )

                # Show characters if present
                if page.get('characters'):
                    st.caption(f"🎭 Characters: {', '.join(page['characters'])}")

        # Save and proceed button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            if st.button("💾 Save Changes", type="secondary"):
                st.session_state.pages_data = pages_data
                st.success("✅ Changes saved!")

        with col2:
            if st.button("🎨 Generate Images", type="primary"):
                # Convert to proper schema objects
                try:
                    translation = BookTranslation(
                        title_latin=pages_data['title_latin'],
                        title_english=pages_data['title_english'],
                        pages=[
                            BookPage(**page) for page in pages_data['pages']
                        ],
                        vocabulary_list=[
                            VocabularyEntry(**vocab) for vocab in pages_data['vocabulary_list']
                        ]
                    )

                    project.title_latin = translation.title_latin
                    project.translation = translation
                    update_project_status(project, 'reviewed')

                    # Move to Step 3 (image generation)
                    st.session_state.current_step = 3
                    st.session_state.auto_workflow_step = None
                    st.success("✅ Ready for image generation!")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error saving translation: {str(e)}")

        with col3:
            st.caption("Save your edits, then proceed to image generation.")


def show_auto_workflow(project: BookProject):
    """
    Main automated workflow controller.

    Flow:
    1. English → Latin translation (with review)
    2. Latin → Paginated book (with review)
    3. → Hand off to Step 3 for image generation

    Args:
        project: Current BookProject
    """
    # Initialize workflow step if not set
    if 'auto_workflow_step' not in st.session_state:
        st.session_state.auto_workflow_step = 1

    # Progress indicator
    current_step = st.session_state.auto_workflow_step

    st.progress(current_step / 3)
    st.caption(f"Auto Workflow: Step {current_step}/2")

    # Show appropriate step
    if current_step == 1:
        auto_step_1_translate(project)
    elif current_step == 2:
        auto_step_2_paginate(project)

    # Back button
    st.markdown("---")
    if st.button("⬅️ Back to Manual Workflow"):
        st.session_state.auto_workflow_step = None
        st.rerun()
