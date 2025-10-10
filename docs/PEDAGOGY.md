# 🎓 Pedagogical Foundation: Latin Story Engine

**Research-backed principles for vocabulary acquisition and language learning in early childhood.**

---

## 📚 Core Research Principles

### 1. Spaced Repetition (Ebbinghaus, Wozniak)

**What it is:**
- Reviewing material at increasing intervals prevents forgetting
- Optimal intervals follow exponential growth: 1 day → 7 days → 16 days → 35 days
- The "forgetting curve" shows memory decay without reinforcement

**Research findings:**
- School-age children learning from spaced presentations performed **70% vs 53%** better than massed practice (Rea & Modigliani, 1985)
- Children benefit **MORE** from spaced practice than adults during acquisition phase
- Ideal recall threshold: **80% retention** when scheduling next review (Lingvist research)
- Modern algorithms (Duolingo, Anki) show learners memorize **significantly more effectively** with optimized spacing

**Application to Latin Story Engine:**
- ✅ **Current:** Reuses 75% of vocabulary from recent batches (enforces repetition)
- ❌ **Missing:** No temporal tracking — doesn't know if last batch was yesterday or last month
- 🎯 **Improvement needed:** Track `last_seen_date` and enforce 7/14/30-day intervals

**Recommended intervals for toddlers:**
- **Day 1:** Initial exposure (new word in story)
- **Day 2-3:** First review (same word in different story)
- **Day 7:** Second review
- **Day 14:** Third review
- **Day 30+:** Maintenance reviews

---

### 2. Zipf's Law and Word Frequency

**What it is:**
- In any language, a small number of words account for most usage
- The most common 100 words = ~50% of all speech
- The most common 1,000 words = ~80% of everyday communication
- Word frequency follows a power-law distribution (Zipfian distribution)

**Research findings:**
- Zipfian distributions are **universal** across languages
- Found in child-directed speech and children's language output (< 32 months old)
- Zipfian distributions **facilitate word segmentation** and learning in context
- Children learn words better in **low-entropy environments** (predictable patterns)
- Learning high-frequency words first provides **maximum communicative power**

**Pedagogical implications:**
- Teaching the 1,000 most common words >>> teaching 1,000 random words
- Foundation vocabulary should prioritize frequency over thematic diversity
- High-frequency words enable comprehension of new contexts

**Application to Latin Story Engine:**
- ✅ **Current:** Tracks `frequency_score` (usage count within system)
- ❌ **Missing:** No external frequency ranking (doesn't know which Latin words are objectively common)
- 🎯 **Improvement needed:**
  - Add `frequency_rank` field based on Latin corpora
  - Prioritize top 100-500 words in early batches
  - Only after foundation, diversify by semantic fields

**Top Latin words for early learners (frequency-based):**
```
Core pronouns: ego (I), tū (you), is/ea/id (he/she/it)
Core verbs: sum (be), habeō (have), faciō (do/make), dīcō (say), videō (see)
Core motion: eō (go), veniō (come), currō (run)
Core nouns: mater (mother), pater (father), aqua (water), pānis (bread)
```

---

### 3. Comprehensible Input (Krashen's i+1)

**What it is:**
- Learners acquire language through **comprehensible input** slightly above their level
- **i** = current proficiency, **+1** = next step
- Input should be 95-98% comprehensible for optimal acquisition
- Too easy = no progress, too hard = frustration

**Research findings:**
- Readers acquired **45+ foreign words** simply by reading comprehensible texts (no direct instruction)
- Affective filter (anxiety, boredom) blocks acquisition when input is incomprehensible
- Acquisition happens **unconsciously** through meaningful exposure
- Optimal target: **70-90% comprehension** for new material

**Application to Latin Story Engine:**
- ✅ **Current:** 75% reused words = 75% comprehensible
- 🟡 **Borderline:** Should be closer to 85-90% reused for toddlers
- 🎯 **Adjustment needed:**
  - Early batches (1-5): **90% reused, 10% new** (1-2 new words per story)
  - Middle batches (6-15): **85% reused, 15% new** (2-3 new words)
  - Advanced batches (16+): **80% reused, 20% new** (3-4 new words)

**Story writing guidelines:**
- Use ONLY vocabulary from approved batch
- Repeat new words 3-5 times per story (natural repetition)
- Keep sentences simple and formulaic
- Focus on action and concrete concepts
- Pair text with illustrations for maximum comprehensibility

---

### 4. Task-Based Language Teaching (TBLT)

**What it is:**
- Learning organized around meaningful tasks with real-world goals
- Motivation comes from accomplishment, not abstract study
- **Backward design:** start with end goal, build prerequisites

**Application to Latin Story Engine:**
- ❌ **Current:** Generates batches in isolation (no end goal)
- 🎯 **Improvement:** **Story-Target Mode**
  - Parent selects target book (e.g., "Cattus in Pilleō" — Cat in the Hat)
  - System identifies all unique vocabulary
  - Generates prerequisite batches to teach those words
  - Child achieves **tangible goal** (reading the whole book independently)

**Benefits:**
- Intrinsic motivation (child sees progress toward real book)
- Meaningful context for vocabulary
- Celebration milestone when story is unlocked
- Parent can choose culturally relevant texts

---

## 🧮 Current Algorithm Analysis

### What Works Well

✅ **Frequency-weighted reuse selection**
- Words with higher `frequency_score` appear more often
- Mimics natural language exposure patterns

✅ **Semantic field balancing**
- Prevents over-concentration in one category
- Creates thematic coherence for stories

✅ **Graduated introduction**
- Small batches (15 words) prevent overload
- Predictable structure (reuse + new)

✅ **Exportable materials**
- Parents get ready-to-use templates
- Reduces friction in story creation

---

### Critical Gaps

❌ **No temporal spacing**
- **Problem:** System doesn't track days between exposures
- **Impact:** Words might be reviewed too soon (wasted effort) or too late (forgotten)
- **Solution:** Add `last_seen_date` + enforce 7/14/30-day intervals

❌ **No external frequency ranking**
- **Problem:** Treats rare words (e.g., "elephant") same as common words (e.g., "run")
- **Impact:** May teach low-value vocabulary before high-value foundation words
- **Solution:** Add `frequency_rank` based on Latin corpora or custom frequency list from OCR'd books

❌ **Fixed reuse ratio (75%)**
- **Problem:** Doesn't adapt to child performance or batch progression
- **Impact:** May introduce too many new words for struggling learners
- **Solution:**
  - Early batches: 90% reused
  - Middle batches: 85% reused
  - Advanced batches: 80% reused
  - Optional: adaptive based on recall testing

❌ **No story-target mode**
- **Problem:** No clear endgame or motivational goal
- **Impact:** Learning feels abstract and endless
- **Solution:** "Work toward reading [specific book]" feature

❌ **No forgetting curve tracking**
- **Problem:** Doesn't know which words child struggles with
- **Impact:** Treats all words equally regardless of recall difficulty
- **Solution:** Add optional `recall_score` field + prioritize weak words

---

## 🎯 Pedagogically Optimal Workflow

### Phase 0: Baseline Assessment
1. **OCR existing books** child has been exposed to
2. Mark all words as **Batch 0** (baseline vocabulary)
3. Tag high-frequency words from those books
4. Establish known vocabulary foundation

### Phase 1: Core Foundation (Batches 1-5)
**Goal:** Build top 50-100 most common Latin words

- **Reuse ratio:** 90% (very conservative)
- **New words per batch:** 2-3
- **Focus:** Pronouns, core verbs (be, have, go), family nouns
- **Interval:** Generate new batch every 7 days
- **Total time:** ~5 weeks

**Example Batch 1:**
```
Reused (from Batch 0): māter, pater, puer (9 words)
New: ego, tū, currō (3 words)
Total: 12 words
Stories: "Ego currō" (I run), "Tū et māter" (You and mother)
```

### Phase 2: Semantic Expansion (Batches 6-15)
**Goal:** Expand to 200-300 words across semantic fields

- **Reuse ratio:** 85%
- **New words per batch:** 3-4
- **Focus:** Motion, emotion, animals, nature, food
- **Interval:** New batch every 10-14 days (enforce spacing)
- **Total time:** ~3-4 months

**Semantic field distribution:**
- Motion verbs: 15%
- Emotion verbs: 10%
- Family/people: 15%
- Animals: 15%
- Nature: 15%
- Food: 10%
- Description (adjectives): 20%

### Phase 3: Story-Target Mode (Batches 16+)
**Goal:** Read a specific Latin children's book

1. **Select target book** (e.g., 150-word story)
2. **OCR and extract** all unique vocabulary
3. **Identify gaps:** Which words does child not know yet?
4. **Generate prerequisite batches** to teach missing words
5. **Final batch** = complete story vocabulary
6. **Celebration:** Child reads entire book independently

**Example:**
```
Target: "Ursus Brūnus, Ursus Brūnus, Quid Vidēs?" (Brown Bear)
Total unique words: 45
Known from Batches 1-15: 30 words
Missing: 15 words (color names, animal names)
Prerequisite batches: 3 batches (5 new words each)
Timeline: 6 weeks
```

---

## 📊 Research-Backed Metrics to Track

### Vocabulary Growth
- Total unique words introduced
- Words per batch (should stay constant ~15)
- New words per batch (should decrease over time as reuse increases)

### Retention Indicators
- Average reuse frequency (target: 3-5x per word)
- Words reused in 3+ batches (high-retention words)
- Days since last exposure (should match 7/14/30 intervals)

### Comprehensibility
- Reuse percentage per batch (target: 85-90%)
- Semantic field diversity (prevent over-concentration)
- Syntactic completeness (need verbs + nouns, not just nouns)

### Child Performance (Optional Manual Tracking)
- Recall accuracy during story reading
- Spontaneous usage of words in conversation
- Emotional response (engagement vs frustration)
- Time to complete story (fluency indicator)

---

## 🔬 Evidence-Based Recommendations

### DO:
✅ Prioritize high-frequency words in early batches
✅ Enforce 7/14/30-day review intervals
✅ Keep reuse ratio at 85-90% for toddlers
✅ Use meaningful tasks (reading real books) as goals
✅ Repeat new words 3-5x per story naturally
✅ Pair text with images for maximum comprehension
✅ Track temporal spacing, not just batch count
✅ Celebrate milestones (reading a full book)

### DON'T:
❌ Introduce too many new words at once (>3 per batch for toddlers)
❌ Teach rare words before common words
❌ Review too soon (< 7 days) or too late (> 30 days)
❌ Generate batches without end goal or context
❌ Use abstract vocabulary before concrete vocabulary
❌ Force learning when child shows frustration
❌ Ignore forgetting curve (some words need more repetition)

---

## 📖 Recommended Reading

### Spaced Repetition
- Wozniak, P. (1990). *SuperMemo Algorithm SM-2*
- Settles, B. & Meeder, B. (2016). *A Trainable Spaced Repetition Model for Language Learning* (Duolingo)

### Frequency & Zipf's Law
- Conti, G. (2025). *Zipf's Law and Vocabulary Teaching in Second Language Acquisition*
- Zipf, G. K. (1949). *Human Behavior and the Principle of Least Effort*

### Comprehensible Input
- Krashen, S. (1982). *Principles and Practice in Second Language Acquisition*
- Krashen, S. (2004). *The Power of Reading*

### Child Language Acquisition
- Tomasello, M. (2003). *Constructing a Language: A Usage-Based Theory of Language Acquisition*
- Nation, I.S.P. (2001). *Learning Vocabulary in Another Language*

---

## 🎓 Summary

The Latin Story Engine currently implements **good but improvable** pedagogy:

**Strengths:**
- Spaced repetition through batch reuse
- Frequency weighting
- Semantic balancing
- Manageable batch sizes

**Critical improvements needed:**
1. **Temporal spacing** (track days, enforce intervals)
2. **Frequency ranking** (prioritize common words first)
3. **Adaptive reuse ratio** (90% → 85% → 80% progression)
4. **Story-target mode** (work toward real books)

**Bottom line:** The system will work well for teaching Latin to a toddler, but implementing these research-backed improvements will make it **significantly more effective** at vocabulary retention and long-term acquisition.

---

**Next steps:** See [ROADMAP.md](ROADMAP.md) for implementation priorities.
