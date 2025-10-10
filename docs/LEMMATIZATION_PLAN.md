# 🔤 Lemmatization Implementation Plan

**Goal:** Add lemma-based vocabulary tracking to properly handle Latin morphology.

---

## 🎯 The Problem We're Solving

**Current state:** Every inflected form is treated as a separate word
- `currō` (I run) and `currit` (he runs) are counted as 2 different words
- System doesn't recognize they're the same verb

**After lemmatization:**
- Both forms grouped under lemma `currō`
- System recognizes: "Child knows the verb, just seeing new form"
- Vocabulary counts are accurate (lemmata, not surface forms)

---

## 🛠️ Lemmatizer Options

### **Option 1: lamonpy** (Recommended)

**Pros:**
- ✅ Easy installation: `pip install lamonpy`
- ✅ Modern (BiLSTM neural network)
- ✅ Trained on Perseus + 440k sentences
- ✅ Returns: lemma + POS tag + morphology
- ✅ 80-94% accuracy

**Cons:**
- ⚠️ Newer tool (less documentation)
- ⚠️ May have issues with rare/archaic forms

**Example usage:**
```python
from lamonpy import Lamon
lamon = Lamon()

text = "Candidus cenam parat et piscem coquit."
score, tagged = lamon.tag(text)[0]

# Returns: [(start, end, lemma, tag), ...]
# tag format: POS_case_number_gender_tense_mood_voice
```

---

### **Option 2: CLTK Backoff Lemmatizer**

**Pros:**
- ✅ Established tool (since 2015)
- ✅ Multi-stage backoff (dictionary → ML → regex)
- ✅ Handles ambiguity well
- ✅ Detailed documentation

**Cons:**
- ⚠️ Slower (multiple lookup stages)
- ⚠️ Requires tokenization first
- ⚠️ Less morphological detail than lamonpy

**Example usage:**
```python
from cltk.lemmatize.latin.backoff import BackoffLatinLemmatizer

lemmatizer = BackoffLatinLemmatizer()
tokens = ['Candidus', 'cenam', 'parat', 'et', 'piscem', 'coquit']

lemmas = lemmatizer.lemmatize(tokens)
# Returns: [('Candidus', 'Candidus'), ('cenam', 'cena'), ('parat', 'paro'), ...]
```

---

### **Decision: Use lamonpy as primary, CLTK as fallback**

**Rationale:**
- lamonpy gives morphological detail we need
- CLTK provides backup for edge cases
- Can compare outputs for validation

---

## 📊 Updated Database Schema

```sql
-- Enhanced lexicon table
CREATE TABLE lexicon_v2 (
    id INTEGER PRIMARY KEY,

    -- Surface form (what actually appears in text)
    surface_form TEXT NOT NULL,

    -- Lemma (dictionary headword)
    lemma TEXT NOT NULL,

    -- English translation
    english_gloss TEXT,

    -- Core classification
    part_of_speech TEXT,      -- noun, verb, adjective, adverb, etc.

    -- Morphological details (from lemmatizer)
    morph_case TEXT,          -- nominative, accusative, genitive, dative, ablative
    morph_number TEXT,        -- singular, plural
    morph_gender TEXT,        -- masculine, feminine, neuter
    morph_person TEXT,        -- 1, 2, 3 (for verbs)
    morph_tense TEXT,         -- present, imperfect, perfect, pluperfect, future
    morph_mood TEXT,          -- indicative, subjunctive, imperative
    morph_voice TEXT,         -- active, passive
    morph_degree TEXT,        -- positive, comparative, superlative (for adjectives)

    -- Full morphological tag (from lemmatizer)
    morph_tag TEXT,           -- Raw tag: "V3SPIA---" or similar

    -- Irregular forms
    irregular_group TEXT,     -- Groups forms like sum/est/sunt

    -- Tracking
    introduced_in_batch INTEGER,
    reused_in_batches TEXT,
    frequency_score INTEGER DEFAULT 0,
    print_count INTEGER DEFAULT 0,
    last_seen_date TEXT,

    -- Metadata
    semantic_field TEXT,
    gesture_prompt TEXT,
    story_hooks TEXT,
    notes TEXT,

    -- Unique constraint on surface form
    UNIQUE(surface_form)
);

-- Index for fast lemma grouping
CREATE INDEX idx_lemma ON lexicon_v2(lemma);
CREATE INDEX idx_pos ON lexicon_v2(part_of_speech);
```

---

## 🔧 Implementation Steps

### **Phase 1: Setup & Testing (Today)**

1. **Install lemmatizers**
   ```bash
   pip install lamonpy
   pip install cltk
   ```

2. **Test on sample text**
   ```python
   # Test both lemmatizers on Batch 0 vocabulary
   # Compare outputs
   # Choose best approach
   ```

3. **Create lemmatization utility script**
   ```bash
   scripts/lemmatizer.py
   ```

---

### **Phase 2: Database Migration (1-2 hours)**

4. **Create migration script**
   - Backup existing `lexicon.db`
   - Create new `lexicon_v2` table with expanded schema
   - Migrate existing data

5. **Add lemmatization function**
   ```python
   def lemmatize_and_tag(surface_form: str, context: str = None):
       """
       Returns: {
           'lemma': 'currō',
           'pos': 'verb',
           'tense': 'present',
           'person': '3',
           'number': 'singular',
           'mood': 'indicative',
           'voice': 'active',
           'tag': 'V3SPIA---'
       }
       """
   ```

---

### **Phase 3: Re-process Batch 0 (30 mins)**

6. **Run lemmatizer on all Batch 0 words**
   - `Candidus` → lemma: `Candidus` (proper noun, unchanged)
   - `cenam` → lemma: `cena`, case: accusative, number: singular
   - `parat` → lemma: `parō`, person: 3, tense: present, mood: indicative
   - `est` → lemma: `sum`, person: 3, tense: present (irregular!)
   - `currit` → lemma: `currō`, person: 3, tense: present

7. **Update database with lemma info**

8. **Verify grouping**
   - Query: "How many unique lemmata?" (should be <41)
   - Query: "Show all forms of lemma `sum`" → `est`, `sunt`

---

### **Phase 4: Update Generator (1-2 hours)**

9. **Modify reuse selection to group by lemma**
   ```python
   # OLD: Select surface forms by frequency
   # NEW: Select lemmata by frequency, allow any form

   def _select_reuse_lemmata(candidates, count):
       # Group by lemma
       lemmata_groups = group_by_lemma(candidates)

       # Score by lemma frequency (sum of all forms)
       lemma_scores = {
           lemma: sum(form['frequency_score'] for form in forms)
           for lemma, forms in lemmata_groups.items()
       }

       # Select top lemmata
       selected_lemmata = top_n(lemma_scores, count)

       return selected_lemmata
   ```

10. **Vocabulary diversity tracking**
    ```python
    # Ensure variety of morphological forms
    def ensure_morphological_diversity(lemma_id):
        """
        Check which forms of this lemma have been introduced.
        Prioritize underrepresented forms for next batch.
        """
        forms = get_forms_for_lemma(lemma_id)

        # Count by tense
        tenses = Counter(f['morph_tense'] for f in forms)

        # Count by case (for nouns)
        cases = Counter(f['morph_case'] for f in forms)

        # Return underrepresented categories
        return {
            'underrepresented_tenses': least_common(tenses),
            'underrepresented_cases': least_common(cases)
        }
    ```

---

### **Phase 5: Future Enhancements**

11. **Form suggestion system**
    - "You've introduced present tense of `currō`, consider perfect next"
    - "Lemma `puella` only in accusative so far, add nominative"

12. **Morphological coverage report**
    - Export: "Which tenses have been covered?"
    - Export: "Which cases are underrepresented?"

13. **Irregular form handling**
    - Special grouping for `sum/est/sunt/eram/...`
    - Manual overrides for highly irregular verbs

---

## 📋 Example: Batch 0 → Batch 1 with Lemmatization

### **Batch 0 (41 surface forms → ~35 lemmata)**

| Surface Form | Lemma | Morphology |
|-------------|-------|------------|
| Candidus | Candidus | proper noun |
| et | et | conjunction |
| dies | diēs | nominative sg |
| est | sum | 3rd sg present |
| sunt | sum | 3rd pl present |
| cenam | cēna | accusative sg |
| parat | parō | 3rd sg present |
| currit | currō | 3rd sg present |
| piscem | piscis | accusative sg |
| aqua | aqua | nominative/ablative sg |

**Lemmata count:** ~35 unique headwords

---

### **Batch 1 Generation (with lemma grouping)**

**Reuse selection:**
- Pick 11 lemmata (85% reuse of 13 total words)
- Selected: `sum`, `parō`, `currō`, `cēna`, `piscis`, `aqua`, `diēs`...

**Forms available for each lemma:**
- `sum` → can use `est`, `sunt`, `sum`, `sumus` (any present forms)
  - Choose: `sum` (1st sg) — NEW FORM, but familiar lemma
- `currō` → can use `currō`, `currit`, `currunt`
  - Choose: `currō` (1st sg) — NEW FORM
- `cēna` → can use `cēna` (nom), `cenam` (acc), `cēnae` (gen/dat)
  - Choose: `cēna` (nominative) — NEW FORM

**Result:**
- Vocabulary: 13 words (lemmata)
- Surface forms in story: ~15 (some lemmata use 2 forms)
- Child sees "new" forms of familiar roots
- Cognitive load: LOW (meanings already known)

---

## 🎯 Success Metrics

**After implementation:**

1. ✅ Batch 0: 41 surface forms → ~35 lemmata (accurate count)
2. ✅ Generator groups by lemma (not surface form)
3. ✅ Database tracks morphological diversity
4. ✅ Can query: "Show all forms of lemma X"
5. ✅ Can query: "Which tenses/cases are underrepresented?"

---

## 🚨 Edge Cases to Handle

### **1. Ambiguous forms**
- `puellae` = genitive sg OR dative sg OR nominative pl
- **Solution:** Store all possibilities, let context disambiguate

### **2. Lemmatizer errors**
- Rare words might lemmatize incorrectly
- **Solution:** Manual override table for corrections

### **3. Enclitics**
- `puellaque` = `puella` + `-que` (and)
- **Solution:** Pre-process to split enclitics before lemmatizing

### **4. Proper nouns**
- `Candidus`, `Vibrissa` should lemmatize to themselves
- **Solution:** Lemmatizer usually handles this, verify

### **5. Irregular verbs**
- `sum/est/fui/esse` — completely irregular paradigm
- **Solution:** Manual grouping, tag as `irregular_group='sum'`

---

## 🛠️ Testing Plan

```python
# Test cases for lemmatizer
test_words = [
    # Regular verb (various forms)
    ("parō", "parō"),        # 1st sg present
    ("parat", "parō"),       # 3rd sg present
    ("parābat", "parō"),     # 3rd sg imperfect
    ("parāvit", "parō"),     # 3rd sg perfect

    # Regular noun (various cases)
    ("puella", "puella"),    # nominative sg
    ("puellam", "puella"),   # accusative sg
    ("puellae", "puella"),   # genitive/dative sg OR nominative pl
    ("puellārum", "puella"), # genitive pl

    # Irregular verb
    ("sum", "sum"),
    ("est", "sum"),
    ("sunt", "sum"),
    ("eram", "sum"),
    ("fui", "sum"),

    # Adjective
    ("bonus", "bonus"),
    ("bonam", "bonus"),
    ("melior", "bonus"),     # comparative (irregular stem!)

    # Conjunction (shouldn't change)
    ("et", "et"),
]

def test_lemmatizer():
    for surface, expected_lemma in test_words:
        result = lemmatize(surface)
        assert result['lemma'] == expected_lemma, f"Failed: {surface} → {result['lemma']} (expected {expected_lemma})"
```

---

## 📖 Next Steps

1. Install `lamonpy` and `cltk`
2. Test on Batch 0 vocabulary
3. Create `scripts/lemmatizer.py` integration
4. Update database schema
5. Re-process Batch 0 with lemma data
6. Update generator to use lemma grouping

**Want me to start building?** I can:
- Create the lemmatizer integration script
- Test both tools on your Batch 0 data
- Design the database migration
