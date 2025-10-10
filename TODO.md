# 📋 Latin Story Engine — TODO

**Current Status:** Batch 0 created ✅ | Lemmatization planned 🔄 | Ready for testing ⚡

---

## ✅ Completed

- [x] Core database system (SQLite)
- [x] Batch generation algorithm (75% reuse)
- [x] Export system (Markdown, CSV, flashcards)
- [x] CLI interface with interactive mode
- [x] Vision-based vocabulary extraction from PDFs
- [x] Batch 0 created (41 words from "Candidus et dies horribilis")
- [x] Full documentation suite (README, PEDAGOGY, ROADMAP, AI_DOCS)
- [x] Frequency list resources downloaded (DCC + Fluent Forever)
- [x] Stories directory structure

---

## 🔄 In Progress

### **Phase 1: Lemmatization Integration**

- [ ] Install and test `lamonpy` lemmatizer
- [ ] Install and test `cltk` backoff lemmatizer
- [ ] Create `scripts/lemmatizer.py` wrapper
- [ ] Test lemmatizers on Batch 0 vocabulary (41 words)
- [ ] Update database schema with lemma + morphology fields
- [ ] Migrate existing Batch 0 data to new schema
- [ ] Re-process Batch 0 with lemmatization
- [ ] Update generator to group by lemma (not surface form)

**See:** [docs/LEMMATIZATION_PLAN.md](docs/LEMMATIZATION_PLAN.md)

---

## 📅 Next Up

### **Phase 2: Morphological Diversity (Future)**

- [ ] Build morphology coverage tracker
  - Track which tenses have been introduced per lemma
  - Track which cases have been introduced per lemma
  - Ensure variety (not just 3rd person, not just accusative)

- [ ] Add diversity scoring to generator
  - Prioritize underrepresented forms when reusing lemmata
  - "You've used `currō` (1st sg) and `currit` (3rd sg), consider `currunt` (3rd pl)"

### **Phase 3: Quick Wins (ROADMAP Phase 1)**

- [ ] Change default reuse ratio from 0.75 → 0.85
  - Edit [scripts/generator.py:26](scripts/generator.py:26)

- [ ] Extract remaining 6 existing books
  - Expand Batch 0 to ~150-200 words
  - More realistic baseline vocabulary

- [ ] Import DCC Latin Core List frequency rankings
  - Add `frequency_rank` field to database
  - Prioritize high-frequency words in early batches

### **Phase 4: Frequency-Based Intelligence (ROADMAP Phase 2)**

- [ ] Parse DCC Latin Core List HTML
- [ ] Create frequency ranking for all words
- [ ] Modify generator to prioritize high-frequency lemmata
  - Batches 1-3: Only top 100 most frequent
  - Batches 4-10: Top 500
  - Later: Any frequency

### **Phase 5: Story-Target Mode (ROADMAP Phase 4)**

- [ ] Create `target_stories` table
- [ ] Build story import workflow (OCR → extract vocab → check gaps)
- [ ] Generate prerequisite batches to reach story readiness
- [ ] "Work toward reading 'Cattus in Pileō'" feature

---

## 🎯 Immediate Next Session

**Goal:** Get lemmatization working

1. Install lemmatizers:
   ```bash
   pip install lamonpy cltk
   ```

2. Test on sample:
   ```python
   from lamonpy import Lamon
   lamon = Lamon()

   text = "Candidus cenam parat et piscem coquit."
   score, tagged = lamon.tag(text)[0]
   print(tagged)
   ```

3. Compare outputs from both tools

4. Create `scripts/lemmatizer.py`:
   - Function: `lemmatize_word(surface_form, context=None)`
   - Returns: `{'lemma': str, 'pos': str, 'morphology': dict}`

5. Update database schema (add lemma fields)

6. Re-process Batch 0 with lemmatization

7. Test generator with lemma grouping

**Expected outcome:** Batch 0 vocabulary grouped by ~35 lemmata instead of 41 surface forms

---

## 🚧 Known Issues / Decisions

### **Design Decisions**

✅ **No temporal spacing** — Re-reading same books is the spaced repetition
✅ **No grammar progression table** — Don't shelter grammar, expose all forms
✅ **Lemma-based tracking** — Group inflections under headword
✅ **Irregular forms as separate** — Initially track separately, group later

### **Technical Debt**

- [ ] Batch 0 words need lemmatization (currently surface-level only)
- [ ] No part-of-speech classification yet (all marked "[needs classification]")
- [ ] No semantic field auto-tagging
- [ ] Seed data not loaded (optional, can skip)

---

## 📊 Metrics to Track

**Current state:**
- Total lemmata in lexicon: ~35 (once lemmatized)
- Surface forms in lexicon: 41
- Batches created: 1 (Batch 0)
- Books processed: 1 / 7
- Average reuse ratio: N/A (only 1 batch)

**After Phase 1 (Lemmatization):**
- Accurate lemma counts
- Morphological coverage per lemma
- Forms introduced per lemma

**After Phase 2 (Diversity Tracking):**
- Tense distribution (% present / perfect / imperfect)
- Case distribution (% nominative / accusative / etc.)
- Person distribution (% 1st / 2nd / 3rd person)

---

## 🎓 Pedagogical Goals

From [PEDAGOGY.md](docs/PEDAGOGY.md):

1. **High-frequency words first** → Need DCC frequency integration
2. **85-90% reuse ratio** for toddlers → Change generator default
3. **Morphological variety** → Track and ensure diverse forms
4. **Story-target motivation** → Build toward reading specific books

---

## 📝 Documentation Updates Needed

- [ ] Update README with lemmatization info
- [ ] Add morphology section to PEDAGOGY.md
- [ ] Update ROADMAP to reflect lemmatization priority
- [ ] Create user guide for manual lemma corrections

---

## 🛠️ Tools & Resources

**Installed:**
- ✅ Python 3
- ✅ PyPDF2 (PDF text extraction)

**Need to install:**
- [ ] `lamonpy` (Latin lemmatizer)
- [ ] `cltk` (Classical Language Toolkit)

**Resources available:**
- ✅ DCC Latin Core List (HTML, in `data/frequency_lists/`)
- ✅ Fluent Forever 625 word list (PDF, in `data/frequency_lists/`)
- ✅ 7 existing Latin story PDFs (`existing_stories/`)

---

## 🎯 Success Criteria

**Short-term (This week):**
- [ ] Lemmatization working for Batch 0
- [ ] Database updated with lemma info
- [ ] Generator groups by lemma

**Medium-term (This month):**
- [ ] All 7 existing books processed
- [ ] Batch 0 expanded to ~200 words
- [ ] Frequency rankings integrated
- [ ] Batch 1 generated and exported

**Long-term (3 months):**
- [ ] 10 batches generated
- [ ] 20+ stories written
- [ ] Morphological diversity tracked
- [ ] Child reading simple Latin stories independently

---

## 💡 Ideas / Future Features

- [ ] Audio pronunciation (TTS integration)
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Multi-child tracking
- [ ] Google Sheets sync for backup
- [ ] AI story generation (Claude/GPT integration)
- [ ] Spaced repetition reminders (email/notification)
- [ ] Gesture/action prompts in exported materials
- [ ] Illustration suggestions based on vocab
- [ ] Parent observation notes (track child reactions)

---

**Last updated:** 2025-10-06
**Next review:** After lemmatization implementation

---

**Quick links:**
- [README.md](README.md) — User guide
- [QUICK_START.md](docs/QUICK_START.md) — Getting started
- [LEMMATIZATION_PLAN.md](docs/LEMMATIZATION_PLAN.md) — Morphology tracking plan
- [PEDAGOGY.md](docs/PEDAGOGY.md) — Research background
- [ROADMAP.md](docs/ROADMAP.md) — Long-term development plan
