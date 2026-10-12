# Image Strategy by Article Type — Data-Driven Analysis

**Date:** 2026-10-11
**Directive:** Kiran — "Go look at all the articles recently done, see the types of them, content etc. Based on these we can do what's the best strategy."
**Sample:** Last 100 published articles from Supabase `p2_articles`

---

## Article Type Breakdown

Classified by IMAGE NEED (not news category) — what kind of photo each story actually requires:

| Image Need Type | Count | % | Description |
|---|---|---|---|
| Named person | 47 | 47% | Verified identity photo (politicians, celebrities, athletes, CEOs) |
| Government/policy | 14 | 14% | Official govt photo (courts, parliament, ministries, policy) |
| Concept/illustrative | 12 | 12% | Conceptual/stock (economy, health, abstract topics) |
| Place/destination | 9 | 9% | Location photo (cities, beaches, landmarks, venues) |
| Brand/company | 8 | 8% | Official product/brand photo (company stories) |
| Food | 6 | 6% | Food photography (recipes, restaurants, diets) |
| Entertainment trailer | 2 | 2% | YouTube thumbnail (trailer articles) |
| Sports action | 2 | 2% | Sports photography (matches, tournaments) |

**Key insight:** Nearly half (47%) of our articles need named-person photos. The next biggest needs are government/policy (14%) and concept/illustrative (12%). Together these three types = 73% of all articles.

---

## Current Source by Type → Quality Gap → Ideal Source

### 1. Named Person (47 articles — 47%)

**Current sources:** publisher og:image (24), Wikimedia (18), Supabase cache (3), YouTube (2)

**Quality gap: MEDIUM**
- Wikimedia photos are often dated — the Himesh Reshammiya problem (all 12 photos from 2010-2016)
- Publisher og:images are inconsistent quality
- Identity verification is solid (existing guards work), but freshness suffers

**Ideal source:** Fresher verified photos. No single new source solves this — it's about ranking newer images higher (already built: freshness preference) and expanding the candidate pool.

**Tier 1 mapping:** Openverse (800M images, no key needed, CC0 filter) — supplements with fresher options from Flickr and other aggregators.

---

### 2. Government/Policy (14 articles — 14%)

**Current sources:** Wikimedia (8), publisher og:image (5), Supabase (1)

**Quality gap: HIGH** ⭐
- 57% from Wikimedia — mostly generic (parliament buildings, flags, stock political imagery)
- Zero dedicated sourcing for Indian government stories
- This is our #2 article type and we're serving it with generic stock

**Ideal source:** PIB (Press Information Bureau) — explicitly free for news, professional 4000-5000px government press photography, covers exactly our stories (PM events, court rulings, ministries, national events).

**Tier 1 mapping:** PIB direct scraping — **biggest India-specific gap in the entire pipeline.**

---

### 3. Concept/Illustrative (12 articles — 12%)

**Current sources:** Wikimedia (7), publisher og:image (4), Pexels (1)

**Quality gap: MEDIUM**
- Generic conceptual images, adequate but uninspired
- Pexels is the fallback but new keys are paused — single point of failure

**Ideal source:** Professional stock with better search. Pixabay (same use case as Pexels, better terms) + Openverse (broader pool).

**Tier 1 mapping:** Pixabay (urgent insurance) + Openverse (broader coverage).

---

### 4. Place/Destination (9 articles — 9%)

**Current sources:** Wikimedia (5), publisher og:image (4)

**Quality gap: MEDIUM-HIGH** ⭐
- Wikimedia travel photos are hit-or-miss — amateur uploads mixed with good ones
- No dedicated tourism source
- Travel is a growing category for us

**Ideal source:** Official tourism boards — professional destination photography, government sites (safe for news use).

**Tier 1 mapping:** Kerala Tourism gallery (best-structured, high-res) → expand to Rajasthan, Incredible India later.

---

### 5. Brand/Company (8 articles — 8%)

**Current sources:** publisher og:image (4), Wikimedia (3), brand_official (1)

**Quality gap: HIGH** ⭐
- Only 1/8 from the brand's official site
- The Mother's Recipe test proved the gap: amateur Commons pickle photo vs. professional branded product shot — night and day
- Brand-first sourcing was just built (2026-10-11) — needs the brand map expanded

**Ideal source:** Brand official websites (already building — 30+ brands mapped).

**Tier 1 mapping:** None of the 4 Tier 1 sources directly serve this — it's the brand-first pipeline we just built. Keep expanding the brand map.

---

### 6. Food (6 articles — 6%)

**Current sources:** publisher og:image (4), Wikimedia (2)

**Quality gap: LOW-MEDIUM**
- Publisher food photography is generally decent
- Adequate for now

**Ideal source:** Current chain is fine. Pixabay/Openverse as supplement.

---

### 7. Entertainment Trailer (2%) + Sports Action (2%)

**Quality gap: LOW**
- Trailers use YouTube maxres (1280×720) — already good
- Sports: small sample, adequate

---

## Prioritized Build Order (Volume × Gap Size)

| Priority | Source | Serves | Volume | Gap | Why This Order |
|----------|--------|--------|--------|-----|----------------|
| 1 | **PIB scraping** | Government/policy | 14% | HIGH | Biggest quality gap for a high-volume type. Zero dedicated Indian govt sourcing today. Explicitly free. |
| 2 | **Openverse** (promote to hero chain) | Named person (47%) + Concept (12%) | 59% combined | MEDIUM | Touches the most articles. No API key needed. Fresher CC0 options for our #1 article type. |
| 3 | **Pixabay API** | Concept/illustrative | 12% | MEDIUM + RISK | Pexels key insurance (urgent risk). Same pattern, better terms. |
| 4 | **Kerala Tourism** | Place/destination | 9% | MEDIUM-HIGH | Travel is growing. Dramatic quality difference vs. generic stock. |

### Why PIB First (Not Pixabay)

The free-sources report ranked Pixabay #1 for Pexels insurance. That's valid risk mitigation. But data-driven:

- PIB serves **14% of articles** with a **HIGH quality gap** right now — real, visible improvement on every government story
- Pixabay serves **12% of articles** with a **MEDIUM gap** — and its urgent value is insurance against a future Pexels failure, not current quality
- Kiran's bar is "rich, useful, attractive" — PIB delivers that today, Pixabay prevents a problem tomorrow

**Recommendation:** Build PIB first (visible quality win), Pixabay second (insurance + quality). Both within the same sprint — total ~1.5 days.

### Brand/Company: Already In Progress

The brand-first pipeline (built 2026-10-11) serves 8% of articles with HIGH gap. Not in Tier 1 because it's already being built — but the brand map needs continuous expansion. Add this to the weekly image-source hunt's scope.

---

## Summary for Kiran

**What we publish:** 47% person stories, 14% government/policy, 12% conceptual, 9% places, 8% brands.

**Biggest wins:**
1. **PIB** → fixes government/policy images (14% of articles, currently generic Wikimedia)
2. **Openverse** → fresher options for person stories (47% of articles, our biggest category)
3. **Pixabay** → Pexels insurance + better conceptual stock (12%)
4. **Kerala Tourism** → professional travel photos (9%, growing category)

**Build order:** PIB → Openverse → Pixabay → Kerala Tourism. Total ~3 days.

**Ongoing:** Brand map expansion (8% of articles, HIGH gap) via the weekly image-source hunt.
