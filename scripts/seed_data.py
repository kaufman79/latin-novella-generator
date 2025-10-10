#!/usr/bin/env python3
"""
Seed data script for Latin Story Engine.
Populates the database with initial Latin vocabulary suitable for early childhood learning.
"""

from database import LatinDatabase


SEED_VOCABULARY = [
    # Motion verbs
    {
        'latin_word': 'currō',
        'english_gloss': 'run',
        'part_of_speech': 'verb',
        'semantic_field': 'motion',
        'action_level': 'physical',
        'gesture_prompt': 'Running motion with arms',
        'story_hooks': 'Chase scenes, races, escaping'
    },
    {
        'latin_word': 'saliō',
        'english_gloss': 'jump',
        'part_of_speech': 'verb',
        'semantic_field': 'motion',
        'action_level': 'physical',
        'gesture_prompt': 'Jumping up and down',
        'story_hooks': 'Playing, obstacle crossing'
    },
    {
        'latin_word': 'ambulō',
        'english_gloss': 'walk',
        'part_of_speech': 'verb',
        'semantic_field': 'motion',
        'action_level': 'physical',
        'gesture_prompt': 'Walking in place',
        'story_hooks': 'Journey, exploration'
    },
    {
        'latin_word': 'portō',
        'english_gloss': 'carry',
        'part_of_speech': 'verb',
        'semantic_field': 'motion',
        'action_level': 'physical',
        'gesture_prompt': 'Carrying imaginary object',
        'story_hooks': 'Helping, moving things'
    },
    {
        'latin_word': 'natō',
        'english_gloss': 'swim',
        'part_of_speech': 'verb',
        'semantic_field': 'motion',
        'action_level': 'physical',
        'gesture_prompt': 'Swimming motions',
        'story_hooks': 'Water play, summer fun'
    },

    # Emotion verbs
    {
        'latin_word': 'rīdeō',
        'english_gloss': 'laugh',
        'part_of_speech': 'verb',
        'semantic_field': 'emotion',
        'action_level': 'emotional',
        'gesture_prompt': 'Laughing and smiling',
        'story_hooks': 'Funny moments, joy'
    },
    {
        'latin_word': 'fleō',
        'english_gloss': 'cry',
        'part_of_speech': 'verb',
        'semantic_field': 'emotion',
        'action_level': 'emotional',
        'gesture_prompt': 'Wiping tears',
        'story_hooks': 'Sadness, hurt feelings, resolution'
    },
    {
        'latin_word': 'amō',
        'english_gloss': 'love',
        'part_of_speech': 'verb',
        'semantic_field': 'emotion',
        'action_level': 'emotional',
        'gesture_prompt': 'Hugging self or heart gesture',
        'story_hooks': 'Family bonds, affection'
    },

    # Family nouns
    {
        'latin_word': 'māter',
        'english_gloss': 'mother',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to mother figure',
        'story_hooks': 'Family stories, care, cooking'
    },
    {
        'latin_word': 'pater',
        'english_gloss': 'father',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to father figure',
        'story_hooks': 'Family stories, play, work'
    },
    {
        'latin_word': 'puer',
        'english_gloss': 'boy',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to boy',
        'story_hooks': 'Main character for adventures'
    },
    {
        'latin_word': 'puella',
        'english_gloss': 'girl',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to girl',
        'story_hooks': 'Main character for adventures'
    },
    {
        'latin_word': 'fīlius',
        'english_gloss': 'son',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to son',
        'story_hooks': 'Family relationships'
    },
    {
        'latin_word': 'fīlia',
        'english_gloss': 'daughter',
        'part_of_speech': 'noun',
        'semantic_field': 'family',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to daughter',
        'story_hooks': 'Family relationships'
    },

    # Animals
    {
        'latin_word': 'canis',
        'english_gloss': 'dog',
        'part_of_speech': 'noun',
        'semantic_field': 'animals',
        'action_level': 'physical',
        'gesture_prompt': 'Barking, panting',
        'story_hooks': 'Pet stories, loyalty, playfulness'
    },
    {
        'latin_word': 'fēlēs',
        'english_gloss': 'cat',
        'part_of_speech': 'noun',
        'semantic_field': 'animals',
        'action_level': 'physical',
        'gesture_prompt': 'Meowing, paw gesture',
        'story_hooks': 'Pet stories, independence'
    },
    {
        'latin_word': 'equus',
        'english_gloss': 'horse',
        'part_of_speech': 'noun',
        'semantic_field': 'animals',
        'action_level': 'physical',
        'gesture_prompt': 'Galloping motion',
        'story_hooks': 'Farm, riding, strength'
    },
    {
        'latin_word': 'avis',
        'english_gloss': 'bird',
        'part_of_speech': 'noun',
        'semantic_field': 'animals',
        'action_level': 'physical',
        'gesture_prompt': 'Flapping wings',
        'story_hooks': 'Flight, singing, nests'
    },

    # Nature
    {
        'latin_word': 'arbor',
        'english_gloss': 'tree',
        'part_of_speech': 'noun',
        'semantic_field': 'nature',
        'action_level': 'physical',
        'gesture_prompt': 'Arms up like branches',
        'story_hooks': 'Climbing, shade, seasons'
    },
    {
        'latin_word': 'flōs',
        'english_gloss': 'flower',
        'part_of_speech': 'noun',
        'semantic_field': 'nature',
        'action_level': 'physical',
        'gesture_prompt': 'Sniffing flower',
        'story_hooks': 'Garden, beauty, gifts'
    },
    {
        'latin_word': 'aqua',
        'english_gloss': 'water',
        'part_of_speech': 'noun',
        'semantic_field': 'nature',
        'action_level': 'physical',
        'gesture_prompt': 'Drinking or pouring gesture',
        'story_hooks': 'Rivers, drinking, washing'
    },
    {
        'latin_word': 'sōl',
        'english_gloss': 'sun',
        'part_of_speech': 'noun',
        'semantic_field': 'nature',
        'action_level': 'physical',
        'gesture_prompt': 'Circle arms overhead',
        'story_hooks': 'Day, warmth, summer'
    },
    {
        'latin_word': 'lūna',
        'english_gloss': 'moon',
        'part_of_speech': 'noun',
        'semantic_field': 'nature',
        'action_level': 'physical',
        'gesture_prompt': 'Crescent shape with hands',
        'story_hooks': 'Night, bedtime, mystery'
    },

    # Food
    {
        'latin_word': 'pānis',
        'english_gloss': 'bread',
        'part_of_speech': 'noun',
        'semantic_field': 'food',
        'action_level': 'physical',
        'gesture_prompt': 'Eating motion',
        'story_hooks': 'Meals, sharing, baking'
    },
    {
        'latin_word': 'cibus',
        'english_gloss': 'food',
        'part_of_speech': 'noun',
        'semantic_field': 'food',
        'action_level': 'physical',
        'gesture_prompt': 'General eating',
        'story_hooks': 'Mealtime, hunger, cooking'
    },
    {
        'latin_word': 'mālum',
        'english_gloss': 'apple',
        'part_of_speech': 'noun',
        'semantic_field': 'food',
        'action_level': 'physical',
        'gesture_prompt': 'Holding and biting apple',
        'story_hooks': 'Snacks, orchards, health'
    },

    # Adjectives
    {
        'latin_word': 'magnus',
        'english_gloss': 'big',
        'part_of_speech': 'adjective',
        'semantic_field': 'description',
        'action_level': 'abstract',
        'gesture_prompt': 'Arms wide apart',
        'story_hooks': 'Size comparisons, growth'
    },
    {
        'latin_word': 'parvus',
        'english_gloss': 'small',
        'part_of_speech': 'adjective',
        'semantic_field': 'description',
        'action_level': 'abstract',
        'gesture_prompt': 'Pinching fingers together',
        'story_hooks': 'Size comparisons, tiny things'
    },
    {
        'latin_word': 'laetus',
        'english_gloss': 'happy',
        'part_of_speech': 'adjective',
        'semantic_field': 'emotion',
        'action_level': 'emotional',
        'gesture_prompt': 'Big smile',
        'story_hooks': 'Joy, celebration, good news'
    },
    {
        'latin_word': 'trīstis',
        'english_gloss': 'sad',
        'part_of_speech': 'adjective',
        'semantic_field': 'emotion',
        'action_level': 'emotional',
        'gesture_prompt': 'Frown, droopy face',
        'story_hooks': 'Sadness, comfort, resolution'
    },
    {
        'latin_word': 'pulcher',
        'english_gloss': 'beautiful',
        'part_of_speech': 'adjective',
        'semantic_field': 'description',
        'action_level': 'abstract',
        'gesture_prompt': 'Admiring gesture',
        'story_hooks': 'Beauty, appreciation'
    },

    # Action verbs (continued)
    {
        'latin_word': 'edō',
        'english_gloss': 'eat',
        'part_of_speech': 'verb',
        'semantic_field': 'action',
        'action_level': 'physical',
        'gesture_prompt': 'Eating motion',
        'story_hooks': 'Mealtime, hunger, taste'
    },
    {
        'latin_word': 'bibō',
        'english_gloss': 'drink',
        'part_of_speech': 'verb',
        'semantic_field': 'action',
        'action_level': 'physical',
        'gesture_prompt': 'Drinking from cup',
        'story_hooks': 'Thirst, refreshment'
    },
    {
        'latin_word': 'dormiō',
        'english_gloss': 'sleep',
        'part_of_speech': 'verb',
        'semantic_field': 'action',
        'action_level': 'physical',
        'gesture_prompt': 'Hands together under cheek',
        'story_hooks': 'Bedtime, rest, dreams'
    },
    {
        'latin_word': 'lūdō',
        'english_gloss': 'play',
        'part_of_speech': 'verb',
        'semantic_field': 'action',
        'action_level': 'physical',
        'gesture_prompt': 'Playful bouncing',
        'story_hooks': 'Games, fun, imagination'
    },
    {
        'latin_word': 'dīcō',
        'english_gloss': 'say/tell',
        'part_of_speech': 'verb',
        'semantic_field': 'communication',
        'action_level': 'abstract',
        'gesture_prompt': 'Point to mouth',
        'story_hooks': 'Conversation, storytelling'
    },
    {
        'latin_word': 'audiō',
        'english_gloss': 'hear',
        'part_of_speech': 'verb',
        'semantic_field': 'sensory',
        'action_level': 'sensory',
        'gesture_prompt': 'Hand to ear',
        'story_hooks': 'Listening, sounds, music'
    },
    {
        'latin_word': 'videō',
        'english_gloss': 'see',
        'part_of_speech': 'verb',
        'semantic_field': 'sensory',
        'action_level': 'sensory',
        'gesture_prompt': 'Point to eyes',
        'story_hooks': 'Discovery, observation'
    },

    # Places/Settings
    {
        'latin_word': 'domus',
        'english_gloss': 'house/home',
        'part_of_speech': 'noun',
        'semantic_field': 'place',
        'action_level': 'abstract',
        'gesture_prompt': 'Roof shape with hands',
        'story_hooks': 'Home life, safety, family'
    },
    {
        'latin_word': 'hortus',
        'english_gloss': 'garden',
        'part_of_speech': 'noun',
        'semantic_field': 'place',
        'action_level': 'physical',
        'gesture_prompt': 'Planting motion',
        'story_hooks': 'Growing, nature, play'
    },
    {
        'latin_word': 'via',
        'english_gloss': 'road/way',
        'part_of_speech': 'noun',
        'semantic_field': 'place',
        'action_level': 'abstract',
        'gesture_prompt': 'Path gesture with hand',
        'story_hooks': 'Journey, adventure, travel'
    },
]


def seed_database(db_path: str = "data/lexicon.db"):
    """Populate database with seed vocabulary."""
    print("🌱 Seeding Latin Story Engine database...\n")

    db = LatinDatabase(db_path)

    added_count = 0
    skipped_count = 0

    for word_data in SEED_VOCABULARY:
        try:
            # Check if word already exists
            existing = db.get_word_by_latin(word_data['latin_word'])
            if existing:
                print(f"⏭️  Skipped '{word_data['latin_word']}' (already exists)")
                skipped_count += 1
                continue

            # Add word
            word_id = db.add_word(**word_data)
            print(f"✅ Added '{word_data['latin_word']}' — {word_data['english_gloss']} (ID: {word_id})")
            added_count += 1

        except Exception as e:
            print(f"❌ Error adding '{word_data['latin_word']}': {e}")

    db.close()

    print(f"\n📊 Summary:")
    print(f"  Added: {added_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(SEED_VOCABULARY)}")
    print(f"\n✨ Database seeding complete!")


if __name__ == '__main__':
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/lexicon.db"
    seed_database(db_path)
