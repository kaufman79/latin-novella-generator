#!/usr/bin/env python3
"""
Gemini API integration for automated Latin book creation.
Handles translation, pagination, and vocabulary extraction.
"""

import json
import os
from typing import Dict, List, Optional
import google.generativeai as genai

from book_schemas import BookProject
from scripts.database import LatinDatabase
from config import GEMINI_TEXT_MODEL, ERROR_MESSAGES


def get_gemini_model():
    """
    Get configured Gemini model for text generation.

    Returns:
        Configured GenerativeModel instance

    Raises:
        ValueError: If API key is not found
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError(ERROR_MESSAGES["api_key_missing"])

    genai.configure(api_key=api_key)
    return genai.GenerativeModel(GEMINI_TEXT_MODEL)


def translate_to_latin(
    english_story: str,
    project: BookProject,
    db: LatinDatabase,
    max_retries: int = 2
) -> str:
    """
    Translate English story to Latin using Gemini API.

    Args:
        english_story: The English text to translate
        project: BookProject with metadata (theme, level, pages)
        db: LatinDatabase for vocabulary suggestions
        max_retries: Number of retry attempts if API fails

    Returns:
        Latin translation as plain text

    Raises:
        ValueError: If API key is missing or response is invalid
        RuntimeError: If API call fails after retries
    """
    model = get_gemini_model()

    # Get known vocabulary for context
    known_words = db.get_all_known_words()
    known_vocab_list = ", ".join([w['lemma'] for w in known_words[:30]])  # Top 30

    # Build comprehensive translation prompt
    prompt = f"""You are an expert Latin teacher creating a children's story.

TASK: Translate the following English story into Classical Latin.

STORY DETAILS:
- Theme: {project.theme or 'general'}
- Target pages: {project.target_pages}
- Age level: {project.target_age}
- Level: {project.level or 1}

TRANSLATION GUIDELINES:
1. Use Classical Latin with proper macrons (ā, ē, ī, ō, ū)
2. Keep sentences SHORT: 3-7 words per sentence
3. Use present tense primarily (easier for beginners)
4. Simple subject-verb-object structure
5. Avoid complex subordinate clauses
6. Use concrete, physical vocabulary (no abstract concepts)
7. Prioritize these known words when possible: {known_vocab_list}

PEDAGOGICAL PRINCIPLES:
- REPETITION: Repeat key words multiple times throughout the story
- ACTIONS: Focus on physical actions children can gesture
- CONCRETE: Use tangible objects and visible actions
- POSITIVE: Happy/playful tone
- PROGRESSIVE: Each sentence builds on the previous

OUTPUT FORMAT:
- Return ONLY the Latin translation
- One sentence per line
- No explanations, no English
- Include proper macrons on all long vowels

ENGLISH STORY TO TRANSLATE:
{english_story}

LATIN TRANSLATION:"""

    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            latin_text = response.text.strip()

            if not latin_text:
                raise ValueError("Empty response from Gemini API")

            return latin_text

        except Exception as e:
            if attempt < max_retries:
                print(f"   Retry {attempt + 1}/{max_retries} due to error: {e}")
                continue
            else:
                raise RuntimeError(f"Failed to translate after {max_retries + 1} attempts: {e}")


def create_pages_and_vocabulary(
    latin_text: str,
    english_text: str,
    project: BookProject,
    max_retries: int = 2
) -> Dict:
    """
    Create paginated book structure with vocabulary from Latin text.

    Args:
        latin_text: The Latin story text
        english_text: The original English text for reference
        project: BookProject with metadata
        max_retries: Number of retry attempts if API fails

    Returns:
        Dictionary with structure:
        {
            "title_latin": str,
            "title_english": str,
            "pages": [
                {
                    "page_number": int,
                    "latin_text": str,
                    "english_text": str,
                    "image_prompt": str,
                    "vocabulary_used": [str],
                    "characters": [str]  # if project has characters defined
                },
                ...
            ],
            "vocabulary_list": [
                {
                    "latin": str,
                    "english": str,
                    "part_of_speech": str,
                    "dictionary_form": str
                },
                ...
            ]
        }

    Raises:
        ValueError: If API key is missing or response is invalid JSON
        RuntimeError: If API call fails after retries
    """
    model = get_gemini_model()

    # Build character context if available
    char_context = ""
    if project.characters:
        char_list = ", ".join([f"{c.name} ({c.description})" for c in project.characters])
        char_context = f"\nCHARACTERS IN THIS STORY: {char_list}\n"

    # Build comprehensive pagination prompt
    prompt = f"""You are preparing a Latin children's story for publication with illustrations.

TASK: Create a paginated book structure with image prompts and vocabulary.

STORY DETAILS:
- Title: {project.title_english}
- Theme: {project.theme or 'general'}
- Target pages: {project.target_pages}
- Art style: {project.image_config.art_style}
{char_context}
LATIN TEXT:
{latin_text}

ENGLISH TEXT (for reference):
{english_text}

YOUR TASK:
1. Divide the story into {project.target_pages} pages (1-2 sentences per page)
2. Create a detailed image prompt for each page that:
   - Describes the scene/action (NOT character appearance)
   - Specifies which characters appear (by name if applicable)
   - Matches the art style: {project.image_config.art_style}
   - Is child-friendly and clear
3. Extract all unique Latin vocabulary with:
   - Simple English translation (1-3 words)
   - Part of speech (noun, verb, adjective, etc.)
   - Dictionary form (e.g., "puer, puerī, m." for nouns, "videō, vidēre, vīdī, vīsum" for verbs)
4. List which vocabulary appears on each page (use lemmas/dictionary headwords)

OUTPUT FORMAT:
Return ONLY valid JSON (no markdown, no explanations):

{{
  "title_latin": "{project.title_latin or 'Fabula Latina'}",
  "title_english": "{project.title_english}",
  "pages": [
    {{
      "page_number": 1,
      "latin_text": "First sentence or two from the Latin text",
      "english_text": "Corresponding English translation",
      "image_prompt": "Detailed scene description for illustration",
      "vocabulary_used": ["lemma1", "lemma2"],
      "characters": ["CharacterName1", "CharacterName2"]
    }}
  ],
  "vocabulary_list": [
    {{
      "latin": "puer",
      "english": "boy",
      "part_of_speech": "noun",
      "dictionary_form": "puer, puerī, m."
    }}
  ]
}}

IMPORTANT:
- Return ONLY the JSON object
- No code blocks, no explanations
- Ensure all JSON is valid (proper quotes, commas, brackets)
- Image prompts should describe SCENES not character appearance (character refs are handled separately)"""

    for attempt in range(max_retries + 1):
        try:
            response = model.generate_content(prompt)
            json_text = response.text.strip()

            # Clean up any markdown code blocks
            if json_text.startswith("```"):
                lines = json_text.split("\n")
                json_text = "\n".join(lines[1:-1])  # Remove first and last lines
            if json_text.startswith("json"):
                json_text = json_text[4:].strip()

            # Parse JSON
            data = json.loads(json_text)

            # Validate required fields
            if "pages" not in data or "vocabulary_list" not in data:
                raise ValueError("Missing required fields in response")

            return data

        except json.JSONDecodeError as e:
            if attempt < max_retries:
                print(f"   Retry {attempt + 1}/{max_retries} due to JSON error: {e}")
                continue
            else:
                raise ValueError(f"Invalid JSON response after {max_retries + 1} attempts: {e}")
        except Exception as e:
            if attempt < max_retries:
                print(f"   Retry {attempt + 1}/{max_retries} due to error: {e}")
                continue
            else:
                raise RuntimeError(f"Failed to create pages after {max_retries + 1} attempts: {e}")


def check_latin_quality(latin_text: str) -> Dict[str, any]:
    """
    Check Latin text for common errors and provide feedback.

    Args:
        latin_text: Latin text to check

    Returns:
        Dictionary with:
        {
            "has_macrons": bool,
            "avg_sentence_length": float,
            "suggestions": [str],
            "quality_score": float  # 0-1
        }
    """
    model = get_gemini_model()

    prompt = f"""You are a Latin language expert. Analyze this Latin text for a children's book and provide feedback.

LATIN TEXT:
{latin_text}

ANALYSIS CRITERIA:
1. Are macrons used correctly on long vowels?
2. Is the grammar correct for Classical Latin?
3. Are sentences simple enough for children (3-7 words)?
4. Is vocabulary appropriate for beginners?

Respond in JSON format:
{{
  "has_macrons": true/false,
  "grammar_issues": ["list of any grammar problems"],
  "avg_sentence_length": <number>,
  "suggestions": ["list of improvement suggestions"],
  "quality_score": <0.0 to 1.0>
}}"""

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip()

        # Clean markdown
        if json_text.startswith("```"):
            lines = json_text.split("\n")
            json_text = "\n".join(lines[1:-1])

        return json.loads(json_text)
    except Exception as e:
        # Fallback to basic checks
        has_macrons = any(c in latin_text for c in "āēīōū")
        sentences = latin_text.split(".")
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

        return {
            "has_macrons": has_macrons,
            "avg_sentence_length": avg_length,
            "suggestions": ["Could not perform detailed analysis"],
            "quality_score": 0.7 if has_macrons else 0.5
        }
