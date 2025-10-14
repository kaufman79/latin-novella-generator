"""
Multi-stage workflow helper functions for Latin Book Engine.
Generates prompts for each stage of the book creation process.
"""

from typing import List, Dict, Optional
import json


def generate_stage_1_prompt(project, known_words: List[Dict]) -> str:
    """
    Stage 1: Story Planning (English only, no Latin yet)

    Goal: Plan a simple, visual story suitable for Latin translation.
    """

    # Get known concepts (English translations)
    known_concepts = [f"{w['english']} ({w['lemma']})" for w in known_words[:30]]
    concepts_text = ", ".join(known_concepts) if known_concepts else "basic concepts like animals, family, actions"

    prompt = f"""You are an expert children's author and language educator helping to create a graded reader book for a young learner.

### Project Details
- Target language: Latin
- Child's known vocabulary: {concepts_text}
- Target known-word ratio: 80% (approx.)
- Age of learner: 3-6 years
- Desired theme: {project.theme or 'General'}
- Title idea: {project.title_english}
- Length: 100–200 words
- Tone: warm, simple, imaginative
- Audience: early readers (ages 3–6)
- Goal: Use approximately 80% known words and introduce new words naturally through context and repetition.

### Your Task
1. **Do not write in Latin yet.**
   First, plan and write the story in **English**.
2. Make the story simple, clear, and visual enough for easy illustration later.
3. Keep sentences short (ideally under 10 words).
4. Limit characters (2–3) and actions per scene.
5. Maintain strong cause-and-effect links between sentences to aid comprehension.
6. Choose a setting that allows playful action (e.g., home, park, forest, space).
7. End the story with a satisfying or funny twist suitable for children.

### Output Format
Return only:
- **Story Title (English)**
- **Story Outline (1–2 sentences)**
- **Full English Story Text**

### Example of a good story concept
Title: Cicadas and the dragon
Outline: Bored Cicadas go into town. Townsfolk are scared of a dragon. The Cicadas go kill the dragon. The grateful townsfolk get the Dragon's gold.
Story: [A bunch of cicadas were bored one day. So they all flew to a local town, but they noticed that everybody in the town was scared. There was a dragon that they were scared of who lived in a cave in a mountain near the town. The cicadas decided to go and take care of the dragon. So they all flew to the cave. The cicadas entered the cave, fearless. They navigated through tunnels. And then they found the dragon's lair. The dragon was sleeping on a mound of gold and treasures and gems. The dragon was red in color. And had big teeth. The cicadas all flew at it, trying to hurt the dragon. But they were unable to hurt the dragon. They just woke it up. The dragon was mad and flew around his lair, chomping and swiping at the cicadas. He killed some. The cicadas didn't know what to do - how would they defeat this dragon? One cicada, named Antonius, had an idea. They would all be really, really loud, with their cicada screams. Antonius started screaming, and then the rest of the cicadas also screamed. The noise was so loud it hurt the dragon's ears. It made the dragon go crazy. He flew around his lair, flying this way and that, aimlessly and recklessly. He was smashing into walls. And then he flew headfirst right into a wall in his frenzy. And he died from the impact. The cicadas rejoiced, they had won! And there was a bunch of gold, and no dragon to protect it. The cicadas all flew back to the town. They told the people that the dragon was dead and they didn't need to be scared anymore. The people were all so thankful and happy. The cicadas told the people "hey there is a bunch of gold in that cave, you can have it." So the people marched to the cave and gathered up the gold. The people came back to town with the gold, and they all shared it, because some people were old or unable to walk and so they couldn't go get gold for themselves. And everybody was happy, and had a lot of gold.]

Note: Vocabulary will be automatically extracted later after translation to Latin.

---

Please follow these steps faithfully.
We will later translate and adapt this story into Latin, then add macrons, page divisions, and image prompts based on a visual style sheet.
"""

    return prompt


def generate_stage_2_prompt(project, known_words: List[Dict], english_story: str) -> str:
    """
    Stage 2: Translation to Latin

    Goal: Translate the English story using known vocabulary with natural inflections.
    """

    # Group words by POS for better readability
    nouns = [w for w in known_words if w.get('part_of_speech') == 'noun']
    verbs = [w for w in known_words if w.get('part_of_speech') == 'verb']
    adjectives = [w for w in known_words if w.get('part_of_speech') == 'adjective']
    other_words = [w for w in known_words if w.get('part_of_speech') not in ['noun', 'verb', 'adjective']]

    prompt = f"""# Stage 2: Translation to Latin

## Your Task
Translate the English story below into simple Latin.

## English Story
{english_story}

## Known Vocabulary - USE THESE WORDS!

**CRITICAL**: The child knows these LEMMAS. You MUST use inflected forms naturally.

"""

    if nouns:
        prompt += "**Nouns** (use any case/number):\n"
        for word in nouns[:15]:
            dict_form = word.get('dictionary_form') or f"{word['lemma']} ({word['english']})"
            prompt += f"- {dict_form}\n"
        if len(nouns) > 15:
            prompt += f"  ... and {len(nouns) - 15} more nouns\n"
        prompt += "\n"

    if verbs:
        prompt += "**Verbs** (use any tense/person/number):\n"
        for word in verbs[:10]:
            dict_form = word.get('dictionary_form') or f"{word['lemma']} ({word['english']})"
            prompt += f"- {dict_form}\n"
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
        prompt += "**No known words yet** - Use simple, concrete Latin vocabulary suitable for beginners.\n\n"

    prompt += """
## Translation Guidelines
1. **Use inflected forms**: Don't just use "canis" → use "canis, canem, canī, canēs" as grammar requires
2. **Vary verb forms**: Don't repeat "currit" → use "currit, currunt, cucurrit, curre" naturally
3. **Target coverage**: Try to use 80%+ known vocabulary
4. **Keep it simple**: 3-7 words per sentence
5. **You may introduce 2-3 new words** if absolutely necessary

## Output Format
Translate scene by scene, maintaining the same structure:

```
Scene 1: [Latin translation]
Scene 2: [Latin translation]
Scene 3: [Latin translation]
...
```

**DO NOT add macrons yet** - we'll do that in the next stage.

Begin!
"""

    return prompt


def generate_stage_3_prompt(latin_text: str) -> str:
    """
    Stage 3: Macronization

    Goal: Add proper macrons to the Latin text.
    """

    prompt = f"""# Stage 3: Add Macrons

## Your Task
Add proper macrons (ā, ē, ī, ō, ū) to the Latin text below.

## Latin Text (without macrons)
{latin_text}

## Guidelines
1. Add macrons where vowels are long
2. Be consistent with classical Latin pronunciation
3. **Do not change any words** - only add macrons
4. Keep the same structure (scene by scene)

## Output Format
Return the same text with macrons added:

```
Scene 1: [Latin with macrons]
Scene 2: [Latin with macrons]
...
```

Begin!
"""

    return prompt


def generate_stage_4_prompt(project, macronized_latin: str, english_story: str) -> str:
    """
    Stage 4: Pagination + Image Prompts

    Goal: Split into pages and create detailed image prompts.
    """

    prompt = f"""# Stage 4: Pagination & Image Prompts

## Your Task
Split the story into {project.target_pages} pages and create detailed image prompts.

## Macronized Latin Story (PRIMARY SOURCE)
{macronized_latin}

**Important**: Use the Latin text above as your primary source. It may have been expanded or modified during translation - that's intentional.

## Original English Story (for reference only)
{english_story}

**Note**: This is the original concept. The Latin may contain additional details or changes - follow the Latin version.

## Style Sheet
{project.image_config.art_style}

## Guidelines
1. **Pages**: Create exactly {project.target_pages} pages
2. **Text per page**: 1-2 sentences maximum
3. **Split the LATIN text** into pages (not the English)
4. **Image prompts**: Detailed visual descriptions following the style sheet above
5. **Consistency**: Keep characters, colors, and style consistent across pages
6. **No text in images**: Image prompts should NOT include text overlays

## Image Prompt Best Practices
- Describe character appearance, pose, expression
- Describe setting, lighting, mood
- Reference the style sheet elements
- Be specific about colors, composition, camera angle
- Keep focus on the main action

## Character References
First, identify all main characters in the story and create character reference descriptions. Each character needs:
- Name (e.g., "Pater", "Mater", "Dragon", "Cicadas")
- Detailed visual description for generating a reference image (appearance, clothing, colors, distinctive features)

## Output Format
Output as JSON:

```json
{{
  "title_latin": "Title in Latin (2-5 words)",
  "characters": [
    {{
      "name": "Pater",
      "description": "32-year-old man with red hair and a short red beard, wearing a blue tunic. Standing in a neutral pose with a kind expression. Simple, clean character design with flat colors."
    }},
    {{
      "name": "Filia",
      "description": "6-year-old girl with blonde hair in pigtails, wearing a yellow dress. Standing with arms at sides, cheerful expression. Simple, child-friendly design with bright colors."
    }}
  ],
  "pages": [
    {{
      "page_number": 1,
      "latin_text": "Full Latin sentence(s) for this page.",
      "english_text": "Full English translation for this page.",
      "image_prompt": "Detailed scene description: setting, action, mood, lighting. Do NOT repeat character appearances.",
      "characters": ["Pater", "Filia"]
    }},
    {{
      "page_number": 2,
      "latin_text": "...",
      "english_text": "...",
      "image_prompt": "...",
      "characters": ["Pater"]
    }}
  ]
}}
```

**CRITICAL**:
- List ALL main characters in the `characters` array with detailed visual descriptions
- For each page, specify which character names appear in that scene using the `characters` array
- Character descriptions will be used to generate reference images for consistency
- Page image prompts should focus on SCENE/ACTION/SETTING only, not character appearance (that comes from references)

**Important**: Output ONLY the JSON, no additional text.

Begin!
"""

    return prompt


def generate_stage_5_prompt(paginated_json: str) -> str:
    """
    Stage 5: Vocabulary Extraction

    Goal: Create vocabulary list with proper dictionary forms.
    """

    prompt = f"""# Stage 5: Vocabulary List

## Your Task
Extract all unique vocabulary from the story and provide dictionary forms.

## Story Pages (JSON)
{paginated_json}

## Guidelines
1. **List ALL unique Latin words** used in the story (lemmas, not inflected forms)
   - Include EVERYTHING: nouns, verbs, adjectives, conjunctions, prepositions, etc.
   - Even common words like "et" (and), "in" (in), "est" (is) should be listed
2. **Provide proper dictionary forms**:
   - Nouns: "puer, puerī, m." (nominative, genitive, gender)
   - Verbs: "currō, currere, cucurrī, cursum" (principal parts)
   - Adjectives: "magnus, magna, magnum" (three forms)
   - Other: appropriate form for the word type
3. **Include part of speech**
4. **Provide English translation**

## Output Format
Output as JSON:

```json
{{
  "vocabulary": [
    {{
      "latin": "puer",
      "english": "boy",
      "part_of_speech": "noun",
      "dictionary_form": "puer, puerī, m."
    }},
    {{
      "latin": "currō",
      "english": "run",
      "part_of_speech": "verb",
      "dictionary_form": "currō, currere, cucurrī, cursum"
    }}
  ]
}}
```

**Important**:
- List LEMMAS (base forms), not inflected forms
- Output ONLY the JSON, no additional text

Begin!
"""

    return prompt


def validate_stage_1_input(text: str) -> tuple[bool, Optional[str]]:
    """Validate Stage 1 (English story) input."""
    if not text or not text.strip():
        return False, "Please enter the English story"

    # Check for reasonable word count (expecting 100-200+ word story)
    word_count = len(text.split())
    if word_count < 30:
        return False, f"Story seems too short ({word_count} words). Expected 100-200 words."

    if word_count > 500:
        return False, f"Story seems too long ({word_count} words). Expected 100-200 words."

    return True, None


def validate_stage_2_input(text: str) -> tuple[bool, Optional[str]]:
    """Validate Stage 2 (Latin translation) input."""
    if not text or not text.strip():
        return False, "Please enter the Latin translation"

    # Check for Latin characters (basic check)
    if not any(c.isalpha() for c in text):
        return False, "Text doesn't appear to contain Latin text"

    return True, None


def validate_stage_3_input(text: str) -> tuple[bool, Optional[str]]:
    """Validate Stage 3 (Macronized Latin) input."""
    if not text or not text.strip():
        return False, "Please enter the macronized Latin text"

    # Check for at least some macrons
    macrons = ['ā', 'ē', 'ī', 'ō', 'ū', 'Ā', 'Ē', 'Ī', 'Ō', 'Ū']
    if not any(m in text for m in macrons):
        return False, "No macrons detected. Please add macrons (ā, ē, ī, ō, ū)"

    return True, None


def validate_stage_4_input(json_text: str) -> tuple[bool, Optional[str], Optional[dict]]:
    """Validate Stage 4 (Pagination JSON) input."""
    try:
        data = json.loads(json_text)

        # Check for title_latin
        if 'title_latin' not in data:
            return False, "Missing 'title_latin' field in JSON", None

        if not isinstance(data['title_latin'], str) or not data['title_latin'].strip():
            return False, "'title_latin' must be a non-empty string", None

        # Check for characters array (new format)
        if 'characters' in data:
            if not isinstance(data['characters'], list):
                return False, "'characters' must be an array", None

            for i, char in enumerate(data['characters']):
                if 'name' not in char:
                    return False, f"Character {i+1} missing 'name' field", None
                if 'description' not in char:
                    return False, f"Character {i+1} missing 'description' field", None
        # Fallback to old format for backwards compatibility
        elif 'cover_image_prompt' not in data:
            return False, "Missing either 'characters' array or 'cover_image_prompt' field in JSON", None

        if 'pages' not in data:
            return False, "Missing 'pages' array in JSON", None

        if not isinstance(data['pages'], list):
            return False, "'pages' must be an array", None

        if len(data['pages']) == 0:
            return False, "'pages' array is empty", None

        # Validate each page
        for i, page in enumerate(data['pages']):
            required = ['page_number', 'latin_text', 'english_text', 'image_prompt']
            for field in required:
                if field not in page:
                    return False, f"Page {i+1} missing required field: {field}", None

            # Check for characters field in new format (optional but recommended)
            if 'characters' in data and 'characters' not in page:
                # Auto-add empty characters list if using new format but page doesn't have it
                page['characters'] = []

        return True, None, data

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}", None


def validate_stage_5_input(json_text: str) -> tuple[bool, Optional[str], Optional[dict]]:
    """Validate Stage 5 (Vocabulary JSON) input."""
    try:
        data = json.loads(json_text)

        if 'vocabulary' not in data:
            return False, "Missing 'vocabulary' array in JSON", None

        if not isinstance(data['vocabulary'], list):
            return False, "'vocabulary' must be an array", None

        if len(data['vocabulary']) == 0:
            return False, "'vocabulary' array is empty", None

        # Validate each entry
        for i, vocab in enumerate(data['vocabulary']):
            required = ['latin', 'english', 'part_of_speech', 'dictionary_form']
            for field in required:
                if field not in vocab:
                    return False, f"Vocabulary entry {i+1} missing required field: {field}", None

        return True, None, data

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}", None
