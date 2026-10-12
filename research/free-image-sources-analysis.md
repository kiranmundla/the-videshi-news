# Free Image Sources — Landscape Analysis

**Date:** 2026-10-11
**Directive:** Kiran — "Instead of adding piecemeal we should come up with analysis, research and then implement."
**Status:** Research only. No implementation until Kiran reviews.

---

## Current Pipeline State (for reference)

The existing `image_sourcer.py` chain:
1. og:image from source article URL
2. RSS signal images (media:thumbnail)
3. Media library cache (verified person images)
3.5. YouTube maxres thumbnails (1280×720)
3.55. Brand official site (30+ Indian brands mapped)
3.6. Official source auto-discovery (65-keyword govt/company domain map)
3.7. PR Newswire India
4. Wikipedia (800px+ minimum)
5. Wikimedia Commons
6. Pexels (existing API key; **new keys paused as of Oct 2026**)

Plus `enrich-articles.py` has Openverse search for inline images.

**Key vulnerability:** Pexels paused new API key issuance. If the current key is revoked, the last-resort fallback disappears. This makes adding Pixabay (or similar) urgent, not optional.

---

## Source Evaluations

### Tier 1 — Build Now

#### 1. Pixabay API
- **License:** Pixabay Content License — free for commercial use, no attribution required. Clean.
- **Quality:** Professional stock photography. 1280px wide on free tier (sufficient for heroes).
- **Access:** Free API key, shown inline at pixabay.com/api/docs — **no approval step**. 100 req/min, no monthly cap. Must cache results 24h; hotlinking not permitted (download or proxy).
- **Coverage:** Strong general stock (people, lifestyle, business, food, travel). Weak on India-specific topics (same as Pexels).
- **Reliability:** Long-established, stable API. No signs of access changes.
- **Why now:** Direct Pexels replacement. Fills the exact gap if Pexels key dies. Same use case, better terms (no monthly cap).
- **Effort:** Low — same pattern as existing Pexels integration. ~2 hours.
- **Endpoint:** `https://pixabay.com/api/?key={KEY}&q={query}&image_type=photo&orientation=horizontal&min_width=800`

#### 2. Openverse API (expand existing)
- **License:** Varies per asset — but has `license_type=commercial` and `license_type=modification` filters. 800M+ images from Flickr, Smithsonian, NASA, Wikimedia.
- **Quality:** Highly variable (aggregator). But the license filters + source filters let us target quality.
- **Access:** **No API key required.** ~20 req/min anonymous, 200/day. Free token available for higher limits.
- **Coverage:** Excellent breadth — aggregates 45+ sources. Better India coverage than pure stock sites (Flickr has strong India travel content).
- **Reliability:** Maintained by WordPress Foundation. Stable.
- **Why now:** Already partially integrated in enrich-articles.py. Should be promoted to the main hero chain as a Commons supplement — especially with `license=cc0,pdm` filter for zero-attribution images.
- **Effort:** Low — extend existing integration. ~3 hours.
- **Endpoint:** `https://api.openverse.org/v1/images/?q={query}&license=cc0,pdm&license_type=commercial&page_size=20`

#### 3. PIB (Press Information Bureau) Direct Scraping
- **License:** **Explicitly free.** PIB copyright policy: "Material featured on this website may be reproduced free of charge and there is no need for any prior approval." Attribution required ("source must be prominently acknowledged").
- **Quality:** Professional government press photography. High-res (4000-5000px seen in the wild).
- **Access:** No API. Press releases at pib.gov.in have embedded images. Scrapable via curl.
- **Coverage:** **Excellent for Indian government/politics stories** — PM events, minister visits, G20, national events. This is our core news category and we have zero dedicated sourcing for it.
- **Reliability:** Government site, stable. Structure changes occasionally.
- **Why now:** Biggest India-specific gap. Every political/government story could use a PIB image instead of a wire-service photo we can't use.
- **Effort:** Medium — need press-release search + image extraction. ~1 day.
- **Approach:** Search pib.gov.in press releases by keyword, extract article images, validate (not logos).

#### 4. Kerala Tourism + Incredible India Galleries
- **License:** Government tourism sites. Images provided for promotional use — standard practice allows news/travel editorial use with attribution. (Verify per-site terms before building.)
- **Quality:** Professional destination photography. Kerala Tourism explicitly offers "high resolution images."
- **Access:** No API. Gallery pages scrapable: `keralatourism.org/photo-gallery/` has categorized galleries (beaches, backwaters, artforms, festivals, cuisine, wildlife, hills).
- **Coverage:** **Excellent for travel articles** — Kerala backwaters, beaches, Kathakali, Ayurveda, festivals. Directly serves our travel category.
- **Reliability:** Government sites, stable.
- **Why now:** Travel is a growing category. Current travel images come from generic stock. Official tourism photos are dramatically better and on-topic.
- **Effort:** Medium — per-board scraper. Start with Kerala (best gallery), add Rajasthan/others later. ~1 day for Kerala.
- **Note:** Incredible India (incredibleindia.gov.in) also has galleries but the site structure is less scraper-friendly. Kerala first.

### Tier 2 — Nice to Have

#### 5. ESA (European Space Agency) Image Library
- **License:** Free for educational/editorial/informational use (press articles explicitly included). Newer content under CC BY-SA 3.0 IGO. Must credit ©ESA.
- **Quality:** Professional space photography, up to 6000×4000px.
- **Access:** Multimedia gallery at esa.int, scrapable. No API.
- **Coverage:** Space/science only. Supplements NASA (already via API).
- **Effort:** Medium. Lower priority than NASA since NASA API already covers space well.

#### 6. Unsplash API
- **License:** Unsplash License — free commercial use, no attribution required for direct downloads. API use requires attribution + hotlinking + download tracking.
- **Quality:** Excellent professional photography. 5M+ images.
- **Access:** Free API key required. 50 req/hour demo, 1,000/hr production after approval.
- **Coverage:** Strong general/lifestyle. Weak on India-specific.
- **Caveat:** API terms require hotlinking (can't self-host) and attribution. More engineering overhead than Pixabay.
- **Effort:** Medium. Pixabay is simpler for the same use case — do Pixabay first, Unsplash only if we need more volume.

#### 7. White House Flickr (Public Domain)
- **License:** U.S. government works — public domain. No restrictions for news use.
- **Quality:** Professional White House photography, up to 3000px.
- **Access:** Flickr accounts (whitehouse, whitehouse45, obamawhitehouse). Flickr API needs free key, or scrape directly.
- **Coverage:** U.S. politics only. Useful for White House/Trump/administration stories.
- **Effort:** Low-Medium. Niche but high-value for the right stories.

#### 8. Smithsonian Open Access
- **License:** CC0 — 2.8M+ images, no restrictions.
- **Quality:** Museum-grade. Excellent for history, culture, science topics.
- **Access:** API at api.si.edu, free key from api.data.gov (email signup).
- **Coverage:** History, culture, natural history, aerospace. Not current news.
- **Effort:** Medium. Good for evergreen/cultural content, not breaking news.

#### 9. Library of Congress — Free to Use and Reuse
- **License:** Public domain / no known restrictions. Dedicated portal at loc.gov/free-to-use.
- **Quality:** Historical photography, high-res scans.
- **Access:** No API for the curated sets, but the main catalog has an API. Scrapable.
- **Coverage:** U.S. history. Has Asian American Pacific Islander Heritage collection — some diaspora relevance.
- **Effort:** Medium. Historical only — useful for context/evergreen, not news.

#### 10. Freerange Stock
- **License:** Free for commercial use. Just relaunched Sept 2026 with no registration required.
- **Quality:** Curated stock, decent quality.
- **Access:** No API found — website browsing only. Limits automation.
- **Coverage:** General stock.
- **Effort:** High (no API). Skip unless they add one.

### Tier 3 — Skip

#### 11. ISRO Direct
- No public image library found. ISRO doesn't publish a browsable press photo gallery like NASA. Getty/Alamy have ISRO images but those are paid. **Skip** — use NASA API for space, PIB for Indian government events.

#### 12. PBSHABD (Prasar Bharati)
- Free news wire with photos, but **requires India mobile number for registration** (already known blocker). **Skip** until registration is possible.

#### 13. Business Wire / GlobeNewswire Scraping
- Press release images are embedded and press-approved (same model as PR Newswire which we already do). But no clean API for image search — would require per-release scraping. **Skip** — PR Newswire India already covers this pattern.

#### 14. Burst by Shopify
- Free commercial use, no attribution. But **no public API** — website only. **Skip** for automation.

#### 15. Rawpixel
- Good CC0 collections (NASA, CDC, SpaceX, White House). But **no API** — website browsing only. **Skip** for automation; useful as manual reference.

#### 16. Flickr Direct API
- Requires free API key. CC-licensed search available. But **Openverse already aggregates Flickr** — no need for direct integration. **Skip.**

---

## Recommended Implementation Order

| Priority | Source | Why | Effort |
|----------|--------|-----|--------|
| 1 | **Pixabay API** | Pexels replacement insurance; same pattern, better terms | ~2 hours |
| 2 | **Openverse** (expand) | No key needed; 800M images; promote to hero chain with CC0 filter | ~3 hours |
| 3 | **PIB scraping** | Biggest India-specific gap; explicitly free for news | ~1 day |
| 4 | **Kerala Tourism** | Best travel image source; professional destination photos | ~1 day |
| 5 | ESA | Space supplement | ~1 day |
| 6 | White House Flickr | U.S. politics niche | ~4 hours |

**Total Tier 1 effort:** ~3-4 days of focused work.

---

## Proposed Updated Chain (after Tier 1)

1. og:image from source article URL
2. RSS signal images
3. Media library cache (verified persons)
3.5. YouTube maxres thumbnails
3.55. Brand official site
3.6. Official source auto-discovery (govt/company)
3.65. **PIB press releases** (NEW — Indian government stories)
3.7. PR Newswire India
3.8. **Kerala Tourism / tourism boards** (NEW — travel stories)
4. Wikipedia (800px+)
5. Wikimedia Commons
5.5. **Openverse CC0** (NEW — promoted from inline-only)
6. **Pixabay** (NEW — replaces/augments Pexels)
7. Pexels (existing key, keep as final fallback)

---

## Risks and Mitigations

- **Pexels key loss:** Mitigated by adding Pixabay (Priority 1). Do this first.
- **Scraping fragility:** PIB and Kerala Tourism have no APIs. Build with defensive parsing (multiple selectors, graceful failure). If a site restructures, the chain falls through to the next source — no breakage.
- **License verification:** For PIB, the copyright policy is explicit. For Kerala Tourism, verify terms before building — if unclear, use with attribution and monitor.
- **Rate limits:** Pixabay (100/min), Openverse (20/min anon) are generous for our volume (~50 articles/day). No concerns.
