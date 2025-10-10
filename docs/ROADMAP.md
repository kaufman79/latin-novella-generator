# 🗺️ Roadmap: Latin Story Engine

**Prioritized development plan for pedagogically-sound improvements.**

---

## 🎯 Development Philosophy

1. **Start simple, iterate based on real use**
2. **Validate with actual child learning data**
3. **Research-backed improvements only**
4. **Keep system modular and maintainable**

---

## 📅 Phase 1: Foundation Fixes (Immediate Priority)

**Goal:** Make current system pedagogically sound without major rewrites.

**Timeline:** 1-2 weeks

### 1.1 Lemmatization Integration
**Priority:** 🔥 CRITICAL

**What:**
- Integrate CLTK lemmatizer for handling inflected Latin forms
- Add lemma lookup for vocabulary management
- Support both dictionary form and inflected forms in database

**Why:**
- Latin is heavily inflected (nouns: 5 cases × 2 numbers, verbs: multiple tenses/moods)
- Children learn words in context (inflected forms)
- Need to track that "currō", "currit", "currunt" are the same word

**Implementation:**
```python
# scripts/lemmatizer.py
from cltk import NLP

def lemmatize_latin_word(word):
    """Convert inflected form to dictionary form."""
    nlp = NLP('lat')
    doc = nlp.analyze(text=word)
    return doc.lemmata[0] if doc.lemmata else word
```

**Database changes:**
- Add `lemma` TEXT column to `lexicon` table
- Add `inflected_forms` TEXT column for storing variants

**Estimated effort:** 6-8 hours

---

### 1.2 Adjust Default Reuse Ratio
**Priority:** 🔥 CRITICAL

**What:**
- Change default `reuse_ratio` from 0.75 → 0.85
- Make ratio configurable per batch progression
- Early batches: 0.90, middle: 0.85, advanced: 0.80

**Why:**
- 75% reuse = 25% new is too aggressive for toddlers
- Comprehensible input research recommends 90-95% known material
- Reduces cognitive overload

**Implementation:**
```python
# scripts/generator.py
def get_adaptive_reuse_ratio(batch_num):
    """Return progressively decreasing reuse ratio."""
    if batch_num <= 5:
        return 0.90  # Very conservative early on
    elif batch_num <= 15:
        return 0.85  # Standard mid-game
    else:
        return 0.80  # Advanced learners
```

**Database changes:**
- None required

**Estimated effort:** 30 minutes

---

### 1.3 Add Temporal Tracking
**Priority:** 🔥 CRITICAL

**What:**
- Add `last_seen_date` column to `lexicon` table
- Update on every batch generation
- Display "days since last exposure" in stats

**Why:**
- Enables future spaced repetition features
- Helps identify stale vocabulary
- Foundation for interval-based selection

**Implementation:**
```sql
ALTER TABLE lexicon ADD COLUMN last_seen_date TEXT;
```

```python
# scripts/database.py
def update_word_usage(word_id, batch_id):
    cursor.execute("""
        UPDATE lexicon
        SET last_seen_date = ?,
            frequency_score = frequency_score + 1
        WHERE id = ?
    """, (datetime.now().isoformat(), word_id))
```

**Database changes:**
- Add `last_seen_date` TEXT column

**Estimated effort:** 2 hours

---

## 📅 Phase 2: Frequency-Based Intelligence (High Priority)

**Goal:** Prioritize high-value vocabulary using frequency data.

**Timeline:** 2-3 weeks

### 2.1 Source Latin Word Frequency Data
**Priority:** 🟡 HIGH

**What:**
- Research available Latin frequency corpora
- Alternatives:
  - Use Dickinson College Commentaries frequency lists
  - Extract from Perseus Digital Library
  - Create custom list from children's book OCR
  - Translate English toddler frequency list

**Why:**
- Ensures most useful words taught first
- Aligns with Zipf's Law (80/20 principle)
- Maximizes communicative power early on

**Resources:**
- [Perseus Digital Library](http://www.perseus.tufts.edu/)
- [Latin Word Frequency Lists](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Latin)
- [Dickinson College Commentaries](https://dcc.dickinson.edu/)

**Estimated effort:** 4-8 hours (research + data processing)

---

### 2.2 Add Frequency Rank Field
**Priority:** 🟡 HIGH

**What:**
- Add `frequency_rank` column (1 = most common)
- Import frequency data for all words
- Tag words as `core` (top 100), `common` (100-500), `supplemental` (500+)

**Implementation:**
```sql
ALTER TABLE lexicon ADD COLUMN frequency_rank INTEGER;
ALTER TABLE lexicon ADD COLUMN frequency_tier TEXT; -- 'core', 'common', 'supplemental'
```

```python
# scripts/frequency_importer.py
def assign_frequency_ranks(frequency_dict):
    """Assign ranks to all words in database."""
    for word in db.get_all_words():
        rank = frequency_dict.get(word['latin_word'], 9999)
        tier = 'core' if rank <= 100 else 'common' if rank <= 500 else 'supplemental'
        db.update_word_frequency(word['id'], rank, tier)
```

**Database changes:**
- Add `frequency_rank` INTEGER
- Add `frequency_tier` TEXT

**Estimated effort:** 3-4 hours

---

### 2.3 Modify Generator to Prioritize Frequency
**Priority:** 🟡 HIGH

**What:**
- Update `_select_new_words()` to consider `frequency_rank`
- Early batches (1-5): Only select `frequency_tier = 'core'`
- Middle batches (6-15): Prioritize `common` tier
- Advanced batches: Allow `supplemental`

**Implementation:**
```python
def _select_new_words(candidates, count, batch_num):
    # Filter by tier based on batch progression
    if batch_num <= 5:
        candidates = [w for w in candidates if w.get('frequency_tier') == 'core']
    elif batch_num <= 15:
        candidates = [w for w in candidates if w.get('frequency_tier') in ['core', 'common']]

    # Sort by frequency rank (lower = better)
    candidates.sort(key=lambda w: w.get('frequency_rank', 9999))

    # Take top N with some randomization
    top_pool = candidates[:count * 2]
    return random.sample(top_pool, min(count, len(top_pool)))
```

**Database changes:**
- None (uses Phase 2.2 changes)

**Estimated effort:** 2-3 hours

---

## 📅 Phase 3: Temporal Spacing (High Priority)

**Goal:** Enforce optimal review intervals based on spaced repetition research.

**Timeline:** 1-2 weeks

### 3.1 Implement Interval-Based Selection
**Priority:** 🟡 HIGH

**What:**
- Modify `_select_reuse_words()` to consider days since last exposure
- Prioritize words at 7, 14, or 30-day intervals
- Penalize words seen too recently (< 5 days)

**Why:**
- Maximizes retention (spaced repetition research)
- Prevents wasted effort reviewing too soon
- Catches words before forgetting (review at 80% retention)

**Implementation:**
```python
def _select_reuse_words(candidates, count):
    scored = []
    now = datetime.now()
    optimal_intervals = [7, 14, 30]  # days

    for word in candidates:
        if not word.get('last_seen_date'):
            continue

        last_seen = datetime.fromisoformat(word['last_seen_date'])
        days_since = (now - last_seen).days

        # Find closest optimal interval
        interval_proximity = min([abs(days_since - i) for i in optimal_intervals])

        # Penalize recent exposures heavily
        if days_since < 5:
            interval_proximity += 20  # Large penalty

        # Score = frequency * (1 / proximity)
        score = word['frequency_score'] / (interval_proximity + 1)
        scored.append((word, score))

    # Select top scorers
    scored.sort(key=lambda x: x[1], reverse=True)
    return [w for w, s in scored[:count]]
```

**Database changes:**
- Requires `last_seen_date` from Phase 1.3

**Estimated effort:** 4-6 hours

---

### 3.2 Add Next Review Date Prediction
**Priority:** 🟢 MEDIUM

**What:**
- Calculate `next_review_date` for each word
- Display in stats and word listings
- Visual indicator: "Due for review", "Not yet", "Overdue"

**Implementation:**
```python
def calculate_next_review_date(word):
    """Predict optimal next review based on history."""
    last_seen = datetime.fromisoformat(word['last_seen_date'])
    frequency = word['frequency_score']

    # Intervals grow with each exposure: 1, 7, 14, 30, 60, 90 days
    intervals = [1, 7, 14, 30, 60, 90]
    next_interval = intervals[min(frequency - 1, len(intervals) - 1)]

    return last_seen + timedelta(days=next_interval)
```

**Database changes:**
- Add `next_review_date` TEXT column

**Estimated effort:** 3-4 hours

---

## 📅 Phase 4: Story-Target Mode (Medium Priority)

**Goal:** Enable working backward from a specific target book.

**Timeline:** 2-3 weeks

### 4.1 Create Target Stories Database
**Priority:** 🟢 MEDIUM

**What:**
- Add `target_stories` table
- Store target book metadata (title, total words, unique vocab)
- Track prerequisite batches needed

**Implementation:**
```sql
CREATE TABLE target_stories (
    story_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    total_words INTEGER,
    unique_words TEXT,  -- Comma-separated Latin words
    prerequisite_batches TEXT,  -- Comma-separated batch IDs
    completed BOOLEAN DEFAULT 0,
    date_added TEXT,
    target_date TEXT,  -- When child should be ready to read it
    notes TEXT
);
```

**Database changes:**
- Add `target_stories` table

**Estimated effort:** 2 hours

---

### 4.2 Build Story Import Tool
**Priority:** 🟢 MEDIUM

**What:**
- OCR target book
- Extract unique vocabulary
- Identify which words are already known vs needed
- Calculate how many batches required

**Implementation:**
```python
# scripts/story_importer.py
def import_target_story(image_paths, title):
    """OCR story and create target record."""
    # Extract all words
    all_words = ocr_extract_latin_words(image_paths)
    unique_words = list(set(all_words))

    # Check which are already known
    known_words = db.get_known_words()
    needed_words = [w for w in unique_words if w not in known_words]

    # Calculate batches needed (3-4 new words per batch)
    batches_needed = math.ceil(len(needed_words) / 3)

    db.create_target_story(
        title=title,
        total_words=len(all_words),
        unique_words=','.join(unique_words),
        batches_needed=batches_needed
    )
```

**Estimated effort:** 6-8 hours

---

### 4.3 Implement Story Path Generator
**Priority:** 🟢 MEDIUM

**What:**
- Generate batch sequence to achieve story readiness
- Prioritize story-specific vocabulary
- Maintain reuse ratio while incorporating target words

**Implementation:**
```python
def generate_story_path(story_id):
    """Generate batches to reach story readiness."""
    story = db.get_target_story(story_id)
    needed_words = story['unique_words'].split(',')

    # Sort by frequency (teach common words first, even from story)
    needed_words.sort(key=lambda w: db.get_word_frequency_rank(w))

    batches = []
    while needed_words:
        batch = generate_batch(
            total_words=15,
            reuse_ratio=0.85,
            forced_new_words=needed_words[:3]  # Force include 3 story words
        )
        batches.append(batch)
        needed_words = needed_words[3:]

    return batches
```

**Estimated effort:** 8-10 hours

---

## 📅 Phase 5: AI Story Generation (Low-Medium Priority)

**Goal:** Automate story writing using vocabulary lists.

**Timeline:** 1-2 weeks

### 5.1 Build Story Writer Agent
**Priority:** 🟢 MEDIUM

**What:**
- Create script that calls Claude API (or uses Claude Code via Task agent)
- Pass vocabulary list + semantic focus
- Generate 3 simple Latin stories
- Validate all words are in approved vocab list

**Implementation:**
```python
# scripts/story_writer.py
def generate_stories(batch_data, num_stories=3):
    """Use Claude to write Latin stories from vocab list."""
    prompt = f"""
    Write {num_stories} simple Latin stories for toddlers (ages 2-4).

    Vocabulary (ONLY use these words):
    {', '.join(batch_data['reused_words'] + batch_data['new_words'])}

    Requirements:
    - 3-5 sentences per story
    - Repetitive phrasing (repeat new words 3-5x)
    - Action-focused and concrete
    - Simple grammar (present tense, basic syntax)
    - Semantic focus: {', '.join(batch_data['semantic_focus'])}

    Format each story as:
    ## Story Title
    [Latin text]

    ### Translation
    [English translation]
    """

    # Call Claude API or use Task agent
    stories = claude_api_call(prompt)

    # Validate vocabulary compliance
    validate_vocab_usage(stories, batch_data)

    return stories
```

**Estimated effort:** 6-8 hours

---

### 5.2 Build Story Validator
**Priority:** 🟢 LOW

**What:**
- Check that generated story only uses approved vocab
- Flag unknown words
- Suggest approved alternatives

**Implementation:**
```python
def validate_vocab_usage(story_text, approved_words):
    """Ensure story only uses approved vocabulary."""
    story_words = extract_latin_words(story_text)
    approved_set = set(approved_words)

    violations = [w for w in story_words if w not in approved_set]

    if violations:
        print(f"⚠️  Unapproved words detected: {', '.join(violations)}")
        for word in violations:
            suggestions = find_similar_words(word, approved_set)
            print(f"  → Suggestions for '{word}': {suggestions}")
    else:
        print("✅ All vocabulary validated")
```

**Estimated effort:** 4-6 hours

---

## 📅 Phase 6: Advanced Features (Future)

**Goal:** Polish and extend system for long-term use.

**Timeline:** Ongoing

### 6.1 Forgetting Curve Tracking
**What:**
- Add `recall_score` field (manual parent input)
- Track which words child struggles with
- Prioritize struggling words in future batches

**Estimated effort:** 8-10 hours

---

### 6.2 Web Dashboard (Optional)
**What:**
- Flask or FastAPI web interface
- Visual vocab browser
- Batch generation wizard
- Progress graphs and charts

**Estimated effort:** 20-30 hours

---

### 6.3 Audio Pronunciation Integration
**What:**
- Add TTS for Latin pronunciation
- Audio flashcards
- Listening comprehension exercises

**Estimated effort:** 10-15 hours

---

### 6.4 Multi-Child Support
**What:**
- Track progress for multiple children
- Compare learning curves
- Personalized batches per child

**Estimated effort:** 12-16 hours

---

### 6.5 Cloud Sync (Google Sheets Integration)
**What:**
- Two-way sync with Google Sheets
- Collaborative editing
- Backup and portability

**Estimated effort:** 10-15 hours

---

## 📊 Priority Matrix

| Feature | Pedagogical Impact | Implementation Effort | Priority |
|---------|-------------------|----------------------|----------|
| Lemmatization | 🔥 CRITICAL | Medium (8h) | **DO FIRST** |
| Adjust reuse ratio | 🔥 CRITICAL | Trivial (30m) | **DO FIRST** |
| Temporal tracking | 🔥 CRITICAL | Low (2h) | **DO FIRST** |
| Frequency ranking | 🟡 HIGH | Medium (8h) | **DO SECOND** |
| Interval-based selection | 🟡 HIGH | Medium (6h) | **DO SECOND** |
| Story-target mode | 🟢 MEDIUM | High (16h) | **DO THIRD** |
| AI story generation | 🟢 MEDIUM | Medium (8h) | **OPTIONAL** |
| Forgetting curve | 🟢 LOW | Medium (10h) | **FUTURE** |
| Web dashboard | 🔵 NICE-TO-HAVE | High (30h) | **FUTURE** |

---

## ✅ Quick Wins Checklist

**Weekend Project (4-8 hours):**
- [x] Install CLTK lemmatizer
- [ ] Change `reuse_ratio` default to 0.85
- [ ] Add `last_seen_date` column
- [ ] Integrate lemmatization into word lookup
- [ ] Test batch generation with new ratios

**Next Sprint (2-3 weeks):**
- [ ] Source Latin frequency data
- [ ] Add `frequency_rank` field
- [ ] Modify generator to prioritize frequency
- [ ] Implement temporal spacing in reuse selection
- [ ] Add "next review date" predictions

**Long-term (1-3 months):**
- [ ] Build story-target mode
- [ ] Create story import tool
- [ ] Implement AI story generation
- [ ] Add forgetting curve tracking
- [ ] Build web dashboard (optional)

---

## 🎯 Success Metrics

**After Phase 1 (Foundation Fixes):**
- ✅ Lemmatization integrated for handling inflected forms
- ✅ Reuse ratio optimized for toddler comprehension
- ✅ Temporal data tracked for future improvements

**After Phase 2 (Frequency Intelligence):**
- ✅ High-frequency words taught first
- ✅ Core 100 words covered in Batches 1-5
- ✅ Measurable improvement in communicative power

**After Phase 3 (Temporal Spacing):**
- ✅ Words reviewed at optimal 7/14/30-day intervals
- ✅ Reduced wasted effort (no premature reviews)
- ✅ Improved retention (catching words before forgetting)

**After Phase 4 (Story-Target Mode):**
- ✅ Child can read specific target book independently
- ✅ Tangible achievement milestone
- ✅ Increased motivation and engagement

---

## 📞 Decision Points

**Before starting each phase, ask:**

1. **Does this align with research?** (See PEDAGOGY.md)
2. **Is this the highest-impact next step?** (Check priority matrix)
3. **Can I validate with real child data?** (Test with actual use)
4. **Will this maintain system simplicity?** (Avoid over-engineering)

**If answer to any is "no," reconsider priority.**

---

**Ready to start:** Begin with Phase 1 quick wins, validate with real use, then iterate based on feedback.
