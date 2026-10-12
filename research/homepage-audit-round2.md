# Homepage Audit — Round 2
**Date:** 2026-10-11 PDT  
**Scope:** 17 unique homepage articles (feed generated 2026-10-11 17:18 UTC)  
**Method:** Supabase `p2_articles` full-record pull, body HTML analysis

---

## What's Working ✅

The enrichment push landed. Every article now has:
- **Hero image:** 17/17 (was 45% imageless before the push)
- **Key Takeaways:** 17/17
- **Sources:** 17/17 have 1–4 sources (zero source-less articles)
- **Data cards:** 17/17 have 1–3 cards (old-style: stat_grid, comparison, timeline, highlights)
- **Word count:** 16/17 adequate (570–895 words); 1 trailer brief at 310 words (acceptable for format)
- **Social embeds:** 7/17 have X/YouTube embeds where appropriate

---

## Gap #1: ZERO External Links in Article Bodies (0/17) 🔴 CRITICAL

**Finding:** Not a single homepage article contains an outbound link in its body HTML. Zero booking links, zero .gov links, zero application links, zero product links.

**Why it matters:** Editorial rule #2 says "Utility articles ship with named links." An immigration article explaining a rule change without linking to the USCIS page is informative but not actionable. The reader learns *about* the thing but can't *do* the thing.

**Specific fixes needed:**

| Article | Category | Missing Links |
|---------|----------|---------------|
| `federal-court-postpones-duration-of-status-rule` | immigration | USCIS D/S policy page, court filing, SEVP guidance — has specific dates and mentions applications but links to nothing |
| `us-green-card-freeze-eight-tech-firms-h1b-workers` | immigration | DOL PERM page, USCIS case status, each suspended company's career page — mentions "apply" but zero links |
| `chennai-beaches-bioluminescence-kovalam-thiruvanmiyur` | travel | Tamil Nadu tourism page, Kovalam/Thiruvanmiyur location links, best-time-to-visit guides |
| `lucknow-1949-heritage-home-slow-living` | travel | Lucknow tourism, heritage homestay booking platforms |
| `weak-us-jobs-report-october-fed-rate-hike-odds` | markets-finance | BLS jobs report, CME FedWatch tool, Federal Reserve calendar |
| `musk-affordable-starlink-india-ambani-jio-ipo` | markets-finance | Starlink India availability page, Jio IPO prospectus (when filed) |
| `deepinder-goyal-temple-wearable-brain-blood-flow` | technology | Company/product page for the Temple wearable, clinical trial registries if cited |

**Fix:** This is a writer-pipeline issue. The writer instructions already require it (rule #2), but compliance is 0%. Either the writer step isn't enforcing it, or the polish step is stripping links. Audit the writer output *before* polish to find where links are lost.

---

## Gap #2: ZERO Inline Images (0/17) 🟡 HIGH

**Finding:** No article has an inline `<img>`, `<figure>`, or `<picture>` in its body. Only 3 have YouTube embeds (deepinder-goyal, ganesh-trailer, raina-shami).

**Why it matters:** Articles are text walls after the hero image. Kiran's visual-story principle: readers comprehend through pictures, not just words. A 600-word article with one hero and zero inline visuals feels flat.

**Fix:** The enrich-on-publish pipeline should insert 1–2 inline images per article (from the same image_sourcer chain). This is an enricher gap, not a writer gap.

---

## Gap #3: New Components Unused (0/17) 🟡 HIGH

**Finding:** 7 new components were built (match_scorecard, key_dates, how_to, checklist, price_compare, recipe, critic_table). Zero homepage articles use any of them. All data cards are old-style.

**Specific opportunities:**

| Article | Component | Why |
|---------|-----------|-----|
| `federal-court-postpones-duration-of-status-rule` | `key_dates` | Has specific dates in body, D/S rule timeline is deadline-driven — perfect fit |
| `us-green-card-freeze-eight-tech-firms-h1b-workers` | `how_to` | Mentions applications; H-1B workers need step-by-step "what to do now" |
| `us-green-card-freeze-eight-tech-firms-h1b-workers` | `checklist` | "Are you affected?" eligibility checklist for the 8 suspended companies |
| `saina-nehwal-haryanvi-diet-aloo-paratha-ghee` | `recipe` | Mentions recipes; Haryanvi diet breakdown begs for a recipe card |
| `weak-us-jobs-report-october-fed-rate-hike-odds` | `price_compare` or `key_dates` | Fed meeting calendar as key dates; rate-cut odds as comparison |
| `musk-affordable-starlink-india-ambani-jio-ipo` | `price_compare` | Starlink vs Jio vs Airtel pricing comparison |

**Fix:** The writer isn't populating `data_cards` with new types. Either the writer instructions (sections 3e2–3e9) aren't being followed, or the writer doesn't know when to use them. Consider: the enricher could auto-suggest component types based on article category + content signals.

---

## Gap #4: Green-Card Article Missing Promised How-To Card 🟠 MEDIUM

**Finding:** The v2-writer run report claimed "Green-card freeze explainer with how-to card." Reality: the article has old-style `comparison` + `highlights` cards. No `how_to` component. Body has 4 section headings (PERM vs H-1B, who feels it first, political backdrop, what to watch) but no step-by-step.

**Fix:** Backfill the `how_to` data card for this article. The content is there — it just needs structuring into steps.

---

## Gap #5: Trailer Brief Thin on Franchise Context 🟢 LOW

**Finding:** `ganesh-dust-to-stardust-trailer-december-11` — 310 words, 1 source. Has 2 social embeds (good). But editorial rule #9 requires: franchise primer + cast + watch path.

**Fix:** Expand with: what Ganesh Acharya is known for (choreographer background), who's in the biopic, where to watch (theatrical Dec 11). ~150 more words.

---

## Summary Counts

| Metric | Count |
|--------|-------|
| Total homepage articles audited | 17 |
| Imageless articles | 0 ✅ |
| Articles with zero sources | 0 ✅ |
| Articles missing Key Takeaways | 0 ✅ |
| Articles with zero external links | **17** 🔴 |
| Articles with zero inline images | **17** 🟡 |
| Articles using new components | **0** 🟡 |
| Articles under 400 words | 1 (trailer brief, acceptable) |

---

## Prioritized Action List

1. **Fix external links (CRITICAL):** Audit where links are lost in the writer→polish pipeline. Backfill top 5 utility articles manually.
2. **Inline images (HIGH):** Add inline image insertion to enrich-on-publish.
3. **New components (HIGH):** Backfill `key_dates` on D/S article, `how_to` + `checklist` on green-card article, `recipe` on Saina diet article.
4. **Green-card how-to (MEDIUM):** Structure existing content into steps.
5. **Trailer expansion (LOW):** Add franchise primer to Ganesh trailer article.
