# Vocabulary Database Redesign - Complete

## Summary

Redesigned the vocabulary system from a static frequency-list database to a dynamic "known words" tracker focused on pedagogical effectiveness and inflection awareness.

## Key Changes

### 1. Database Schema (scripts/database.py)

**Old System:**
- `lexicon` table with 1,405+ words from FF625 + DCC Core
- `batches` table for story tracking
- `stories` table for metadata
- Complex frequency tiers and semantic fields

**New System:**
```sql
known_words (
    id, lemma, english, part_of_speech, dictionary_form,
    date_learned, times_seen, last_seen_date, mastery_level, notes
)

books (
    id, project_id, title_latin, title_english, date_created,
    words_used (JSON), new_words_introduced (JSON),
    total_words, known_word_percentage
)
```

**Purpose:** Track words your son actually knows, not generic frequency lists.

### 2. AI Prompt Strategy (app.py)

**Problem:** AIs only use lemma forms (canis, currō) when given word lists.

**Solution:** Inflection-aware prompts explicitly instruct AI to use any inflected form:

```markdown
## Known Vocabulary - USE THESE WORDS (Any Inflected Form!)

**Nouns** (use any case/number):
- puer, puerī, m. (boy)
  → Can use: nominative, genitive, dative, accusative, ablative (singular/plural)

**Verbs** (use any tense/person/number):
- currō, currere (run)
  → Can use: present, imperfect, perfect, etc. - all persons/numbers

## IMPORTANT: Use Different Inflected Forms!
- Don't just use "canis" every time → use "canis, canem, canī, canēs" as grammar requires
- Don't just use "currit" → use "currit, currunt, cucurrit, curre" etc.
```

### 3. App Features (app.py)

**Vocabulary Database Tab:**
- ✅ Add known words with simple form (lemma, English, POS, dictionary form)
- ✅ Search and filter by POS
- ✅ Display mastery levels (1=New, 2=Familiar, 3=Mastered)
- ✅ Track times_seen and last_seen_date for spaced repetition
- ✅ Export to CSV

**Book Creation Workflow:**
- ✅ Generates prompts using ALL known words (grouped by POS)
- ✅ Explicit inflection instructions in prompt
- ✅ Post-book tracking: extracts vocabulary, updates database
- ✅ Displays coverage stats: Total words, known words, new words, percentage

**Automatic Word Tracking:**
When you build a PDF:
1. Extracts lemmas from `vocabulary_used` in JSON
2. Updates `times_seen` for known words
3. Adds new words to database with `mastery_level=1`
4. Records book in `books` table
5. Displays stats: "85% known words, 3 new words introduced"

### 4. CLI Changes (cli.py)

**Old setup:**
```bash
python cli.py setup  # Imported FF625 + DCC Core (1,405 words)
```

**New setup:**
```bash
python cli.py setup  # Just initializes empty database
```

Then add words via the Streamlit app.

## Pedagogical Rationale

### Target: 80%+ Known Words
- Research recommends 95-98% comprehensible input
- You're targeting 80%+ with parental support (acceptable)
- Lower than old 75% minimum

### Inflection Awareness
- Knowing "currō" means knowing "currit, currunt, cucurrit, curre"
- AI must use varied forms, not just lemmas
- Creates natural, grammatically diverse Latin

### Spaced Repetition Ready
- Tracks `last_seen_date` for each word
- Can query words needing review (not seen in 7+ days)
- Foundation for future spaced repetition scheduling

### Personalized Learning
- Database reflects YOUR son's actual knowledge
- Not bloated with 1,400 words he doesn't know
- Can add words incrementally as he learns them

## Migration Path

1. ✅ Deleted old `data/lexicon.db`
2. ✅ New schema auto-creates on first run
3. ⚠️ **Action Required:** Add your son's known words via app
4. ⚠️ **Optional:** Import starter list (10-20 basic words)

## Example Starter Words

Suggested first 10-20 words to add:

**Nouns:**
- puer, puerī, m. (boy)
- canis, canis, m./f. (dog)
- mater, matris, f. (mother)
- pater, patris, m. (father)

**Verbs:**
- sum, esse (be)
- currō, currere (run)
- videō, vidēre (see)
- habeō, habēre (have)

**Adjectives:**
- magnus, magna, magnum (large)
- parvus, parva, parvum (small)

## Usage

### Adding Words
1. Go to "Vocabulary Database" tab
2. Click "➕ Add New Known Word"
3. Fill in: lemma, English, POS, dictionary form
4. Submit

### Creating Books
1. "Create Project" tab → fill form
2. "Get AI Story" tab → copy prompt (includes known words with inflection instructions)
3. Paste in Claude/ChatGPT → get JSON
4. Paste JSON back → "Generate Book" tab
5. Build PDF → see coverage stats → words auto-tracked

### Tracking Progress
- Check "Vocabulary Database" tab for word stats
- See "Times Seen" to know which words need review
- Mastery levels: 1=New, 2=Familiar, 3=Mastered (manual for now)

## Future Enhancements

- [ ] Automated mastery level updates based on times_seen
- [ ] Spaced repetition scheduler (suggest review intervals)
- [ ] Bulk import from CSV
- [ ] Word difficulty ratings
- [ ] Theme-based word grouping
