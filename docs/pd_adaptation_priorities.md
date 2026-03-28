# Public Domain Adaptation Priorities

Prioritized plan for which stories to adapt first, based on virtue gaps, story quality, and practical considerations.

## Current Virtue Coverage

> **Note:** The ratings table below is from the initial planning phase and may be outdated. The authoritative virtue ratings live in each book's `config.json`. For the most current coverage data, run `python scripts/virtue_chart.py`. For detailed rating rubrics (what each 0-5 level means), see `docs/cardinal_virtues_deep_dive.md` and `docs/theological_virtues_deep_dive.md`.

Ratings from existing books (0-5 scale) — **snapshot from initial planning, may not reflect re-ratings**:

| Virtue | Augustine Pears | Dada Cockroach | Locusts Dragon | Lion/Witch/Wardrobe | Link Treasure | **Total** | **Gap?** |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|:--|
| **Prudentia** | 0 | 0 | 2 | 1 | 1 | 4 | LARGE GAP |
| **Iustitia** | 3 | 0 | 0 | 3 | 0 | 6 | Moderate |
| **Fortitudo** | 1 | 1 | 4 | 3 | 2 | 11 | Saturated |
| **Temperantia** | 4 | 0 | 0 | 2 | 0 | 6 | Carried by 1 book |
| **Fides** | 2 | 0 | 0 | 4 | 0 | 6 | Carried by 1 book |
| **Spes** | 0 | 0 | 0 | 3 | 0 | 3 | LARGE GAP |
| **Caritas** | 2 | 1 | 1 | 5 | 0 | 9 | Carried by 1 book |

**Biggest gaps**: Prudentia and Spes. Fortitudo is saturated — new books shouldn't lead with courage.

---

## Priority Order

### 1. The Lion and the Mouse (Aesop)

**Fills gaps**: Caritas (3) + Fides (3) + Iustitia (3) — three under-represented virtues in one story
**Story evaluation score**: 5/5
**Art**: Generate new. Milo Winter (1919) and Rackham (1912) only have 1-2 illustrations per fable — nowhere near enough for a 15-18 page picture book (we need ~1 image per page).
**Adaptation ease**: High — two characters, clear physical action, short

**Virtue ratings**:
| prud | iust | fort | temp | fid | spes | car |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 3 | 2 | 0 | 3 | 0 | 3 |

**Through-line**: "Even the smallest creature can repay the greatest kindness."

**Want/Obstacle**:
- Act 1: Mouse wants to survive → Lion has caught her
- Act 2: Lion wants to escape → Trapped in a net

**Key choice**: The lion holds the mouse in his paw. He could eat her. She begs for mercy. He opens his paw. That single act of mercy is the hinge.

**Latin refrain**: *"Mūs parva est. Sed mūs memor est."* ("The mouse is small. But the mouse remembers.")

**Modifications**:
- Simplify hunters to just "a net" (less frightening)
- Make the mouse female for protagonist diversity
- Expand the gnawing-through-rope section to 2-3 pages for tension
- End with lion and mouse walking away together

**Pages**: 15-18

---

### 2. The Little Engine That Could

**Fills gaps**: Spes (5) — the single biggest gap. No existing book models hope as primary virtue.
**Story evaluation score**: 5/5
**Art**: Lois Lenski's 1930 black-and-white illustrations now PD. Need to verify illustration count — may have enough for reuse, or may need to supplement with generated art.
**Adaptation ease**: Medium — needs condensing, but the refrain carries everything

**Virtue ratings**:
| prud | iust | fort | temp | fid | spes | car |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 0 | 3 | 0 | 0 | 5 | 2 |

**Through-line**: "When everyone says you cannot, choosing to try is what matters."

**Want/Obstacle**: Get toys over the mountain to children on the other side. The engine is small; big engines refuse; the mountain is steep.

**Key choice**: The big engines say no. The little engine looks at the toys, looks at the mountain, and says: *"Temptābō."* ("I will try.")

**Latin refrain**: *"Possum, putō! Possum, putō!"* building to *"Potuī! Potuī!"* on the downhill.

**Modifications**:
- Condense to two refusing engines (one haughty, one tired)
- 5-6 pages of straining uphill with building refrain
- Joyful downhill with past-tense refrain
- End with children receiving toys (connecting effort to purpose = caritas)

**Pages**: 20-22

---

### 3. The Three Little Pigs

**Fills gaps**: Prudentia (4) — the biggest gap after spes.
**Story evaluation score**: 5/5
**Art**: Generate new (or supplement heavily). Brooke's 1905 illustrations only have ~8-10 images in the Three Little Pigs section of The Golden Goose Book — not enough for a 20-24 page book. Could use a few Brooke originals as reference/supplements, but would need mostly generated art.
**Adaptation ease**: Low-medium — natural repetition, great refrain

**Virtue ratings**:
| prud | iust | fort | temp | fid | spes | car |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 0 | 2 | 1 | 0 | 0 | 0 |

**Through-line**: "The one who builds carefully stands firm when the storm comes."

**Want/Obstacle**: Each pig wants a house. The wolf tests each choice.

**Key choice**: The third pig chooses bricks when straw and sticks would be easier. His brothers laugh. He keeps building. The choice is made *before* the wolf arrives — that's what makes it prudentia, not fortitudo.

**Latin refrain**: *"Flābō et sufflābō et domum tuam dēiciam!"* Counter: *"Flā! Domus mea stat."*

**Modifications**:
- Soften ending: wolf runs away exhausted (not boiled alive)
- First two pigs NOT eaten — they run to the brick house (learning from mistakes, not punishment)
- Wolf is scary but cartoonish — force of nature, not malicious

**Pages**: 20-24

---

### 4. The Enormous Turnip

**Fills gaps**: Caritas (4) + Spes (3) — cooperative effort and persistence
**Story evaluation score**: 4/5 (loses a point on "resolution from character choice" — the mouse just happens to be enough)
**Art**: Generate new (no canonical PD illustrations)
**Adaptation ease**: Lowest difficulty on the entire list
**Status**: Prototyped through Latin review (`projects/the_enormous_turnip/`). Latin is clean but outline was too terse — non-refrain pages had only 3-word sentences, felt thin. Better suited for a younger child (~2yo). Would need outline revision (denser English source text) before production.

**Virtue ratings**:
| prud | iust | fort | temp | fid | spes | car |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 0 | 0 | 2 | 0 | 0 | 3 | 4 |

**Through-line**: "No one is too small to make the difference."

**Want/Obstacle**: Pull up the enormous turnip. It's stuck. Each puller alone is not enough.

**Key choice**: Distributed — each character chooses to help when asked. The mouse's tiny addition is what finally works.

**Latin refrain**: *"Trahunt... trahunt... NŌN POSSUNT!"* → final: *"Trahunt... trahunt... POSSUNT!"*

**Character chain** (good Latin vocab): avus, avia, puella, canis, fēlēs, mūs

**Modifications**: Minimal. This story is already in picture-book format. The turnip popping out should be a full-page spread — everyone falls backward.

**Pages**: 15-18

---

### 5. Henny Penny (modified ending)

**Fills gaps**: Prudentia (4) — different angle than Three Pigs (discernment/critical thinking vs. planning ahead)
**Story evaluation score**: 4/5 (with modified ending)
**Art**: Generate new
**Adaptation ease**: Medium — cumulative parade is great for Latin; ending needs rework

**Virtue ratings**:
| prud | iust | fort | temp | fid | spes | car |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 4 | 0 | 0 | 0 | 2 | 0 | 0 |

**Through-line**: "Stop and think before you follow the crowd."

**Want/Obstacle**: Warn the king the sky is falling. Henny Penny is wrong (acorn hit her head), and Foxy Loxy exploits her panic.

**Key choice (modified)**: When Foxy Loxy says "Follow me into this cave," one animal stops: *"Expectā! Vidēāmus!"* They go back, find the acorn, realize the sky is fine. The fox slinks away.

**Latin refrain**: *"Caelum cadit! Caelum cadit!"* → turning point: *"Expectā! Vidēāmus!"*

**Playful Latin names**: Gallīna Pennīna, Gallus Lallus, Anas Banas, Ānser Ganser, Meleagris Lurkey

**Modifications**:
- Ending changed: one animal chooses to stop and think → transforms tragedy into prudentia tale
- Foxy Loxy should be visibly sly in illustrations (narrow eyes, pointed smile) to telegraph danger

**Pages**: 18-22

---

## After These Five

The virtue coverage becomes well-balanced:
- **Prudentia**: Filled (Three Pigs + Henny Penny)
- **Iustitia**: Filled (Augustine + Lion/Witch + Lion/Mouse)
- **Fortitudo**: Saturated (already was)
- **Temperantia**: Adequate (Augustine). Next candidate: Millions of Cats
- **Fides**: Filled (Lion/Witch + Lion/Mouse)
- **Spes**: Filled (Little Engine primary, Enormous Turnip secondary)
- **Caritas**: Well covered (Lion/Witch + Lion/Mouse + Enormous Turnip)

## Deferred Stories

| Story | Why deferred |
|-------|-------------|
| **Goldilocks** | Great language structure, terrible virtue content. No character arc. Use only as pure Latin-acquisition book. |
| **Peter Rabbit** | Good story but overlaps with Augustine (temperantia). Hardest Tier 2 adaptation. |
| **Velveteen Rabbit** | Richest virtue story on the list but far too complex for 3-7 word sentences. Revisit at age 5-6. |
| **Fierce Bad Rabbit / Miss Moppet** | Very easy to adapt but almost no virtue content. Good as lightweight bonus books. |
| **Millions of Cats** | Would be #6. Strong temperantia/caritas, excellent Gag illustrations, great refrain. |
| **Little Red Hen** | Outstanding Latin structure but vindictive ending clashes with caritas. Enormous Turnip covers similar ground better. |
| **Gingerbread Man** | Great chase refrain, very weak virtue content. Protagonist makes no meaningful choice. |
