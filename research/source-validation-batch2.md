# Source Validation — Batch 2 (GPT-Suggested Sources)
**Date:** 2026-10-11
**Status:** All three tested. All three REJECTED. Nothing built.
**Rule honored:** Kiran's "test before building" — same pattern as PIB.

---

## Summary

| Source | Verdict | Failing Dimension |
|--------|---------|-------------------|
| Incredible India (incredibleindia.org) | ❌ REJECTED | Copyright — prior written consent required |
| Brand press kits (Tata, Mahindra) | ❌ REJECTED | Quality — abstract art, tiny cards, or absent |
| Diaspora org sites (FIA, AIA-NY, GOPIO) | ❌ REJECTED | Copyright — "All Rights Reserved" everywhere |

**Key lesson:** All three failed on a *different* dimension — copyright, quality, and copyright respectively. This validates the multi-axis validation approach (license + quality + access + coverage). One dimension failing is disqualifying.

---

## Source 1: Incredible India — REJECTED (Copyright)

**Test articles:**
1. `chennai-beaches-bioluminescence-kovalam-thiruvanmiyur` — II alternative: 1920×1080 aerial of Marina Beach, visually verified sharp and correct identity. **Big upgrade** over current generic microplankton stock photo.
2. `lucknow-1949-heritage-home-slow-living` — II alternative: 1600×900 crisp Bada Imambara. **Clear upgrade** over dated Wikimedia photo.
3. `diwali-2026-best-places-india-experience-festival-of-lights` — II alternative: 1600×900 golden-hour Varanasi ghats. **Modest upgrade.**

**Technical assessment (all excellent):**
- Adobe Scene7 CDN (`s7ap1.scene7.com/is/image/incredibleindia/<asset>`), dynamic resize works without key (`?wid=1600&qlt=85&fmt=jpg`)
- No hotlink protection (verified with foreign Referer → 200 OK)
- `incredibleindia.gov.in` serves server-rendered AEM pages, fully scrapable; per-city galleries with 50+ assets
- No public API; Content Hub requires login
- Coverage patchy: major cities great, smaller destinations (Banswara) placeholder-only

**Copyright (disqualifying):** Terms of Use explicitly cover both `INCREDIBLEINDIA.ORG` and `INCREDIBLEINDIA.GOV.IN` — **prior written consent required** to reproduce any Content. Content Hub states all rights remain with contributing orgs; "unauthorized use, reproduction, or distribution of these assets for commercial purposes or personal gain is strictly prohibited."

**Correction to standing assumption:** The pipeline's standing note that "Indian govt = free for news" does **not** extend to Incredible India content.

**Path forward (Kiran decision, not automation):** Write to dg-tourism@nic.in requesting blanket editorial-use permission. If granted, this becomes a Tier 1 source immediately — the technicals are perfect.

---

## Source 2: Brand Press Kits — REJECTED (Quality)

**Brands tested:** Tata (tata.com/media-kit, tata.com/newsroom) and Mahindra (mahindra.com/newsroom).

**Tata:**
- Open, no login. Newsroom is AEM server-rendered HTML — scrapable with plain curl.
- Individual press pages carry **generic abstract brand art** (verified visually): e.g. 1440×530 purple gradient swirl; Tata Sierra launch page only has a 390×362 card thumbnail (unusable).
- One real asset: Chandrasekaran headshot zip, ~3600×5600 print-quality, but subject-locked to that exec.
- **Blocked:** tatamotors.com press → 403 bot-block; tcs.com/newsroom → 403 bot-block.
- Copyright: "you may not, without our permission, copy and distribute this information" — ambiguous, not cleanly safe.

**Mahindra:**
- Open, no login. Drupal SSR HTML — scrapable.
- Press-release pages carry **zero images** (verified on Tech Mahindra AI release and Mahindra Lifespaces launch — only logos). No `/media-library` (404). Only 954×390 abstract template thumbnails on listing pages.
- Copyright: prohibits use "without our prior written consent" — ambiguous/negative.

**Test articles:**
1. `tcs-beats-estimates-q2-profit-rises-15-percent` — no TCS Q2 press release existed on tata.com at all (curated brand-marketing stories, not earnings). Current Wikimedia office photo wins by default.
2. `tech-mahindra-infinite-uptime-physical-ai-partnership` — matching press release on mahindra.com has zero images. Alternative is literally nothing.

**Structural problems:**
- Mapping sparsity: press kits only cover what the company publishes; our articles cover fresh news. Even perfect images wouldn't match most articles.
- Banners are brand art, not news photos (visually confirmed for both brands).

**Narrow exception (not pipeline-worthy):** Tata's exec-headshot zips are genuine print-quality with implicit journalist intent — manual fallback for articles *about* N. Chandrasekaran specifically.

---

## Source 3: Diaspora Org Sites — REJECTED (Copyright)

**Sites checked:**

1. **FIA Chicago (fia-il.us)** — Public WordPress galleries per event (Holi 2024, Republic Day, etc.). Sample: Holi 2024 photo at 1400×933, sharp professional event photography. But gallery padded with text-baked e-magazine covers. Copyright: "All Rights Reserved." No reuse terms. Real photos credited to **"Asian Media USA ©"** (commercial media company) — rights likely sit with them, not FIA. Scrapable but must not be automated without rights.

2. **FIA NY-NJ-CT-NE (fianynjct.org)** — 14 event sub-galleries, public. Copyright: "Copyright © Federation of Indian Associations 2026." No reuse terms. Next.js client-side rendering — manual-only for automation. Homepage imagery is mostly Instagram embeds (Meta-walled).

3. **AIA-NY (aia-ny.org)** — No photo gallery at all. Bare landing page. Festival photos circulate only via press as "Photo courtesy: AIA-NY" (credit-based, not free license).

4. **GOPIO (gopio.net)** — Stale/legacy (content from 2004–2019). Dated group shots. Zero relevance.

**Relevance test:** Recent festival articles (Navratri, Diwali, Aqua Garba) are about *general festival culture* — org galleries contain posed VIP/group shots at specific gala events, thematically *worse* than current generic imagery, and trigger named-person photo risk. No article-type match: org photos only fit articles *about that org's event*.

**Narrow exception (not pipeline source):** When an article is specifically about an org's own event, requesting their photo with explicit permission/credit is legitimate editorial practice — a manual, per-article workflow.

---

## What This Means for the Strategy

**Remaining viable Tier 1 sources (untested):** Pixabay, Openverse, PMO scraper, Kerala Tourism.

**Pattern emerging:** Government/official sites have the best *technical* images (PMO 1556×908, Incredible India 1920×1080) but the worst *copyright* terms. This is the fundamental tension: the highest-quality free sources are either public-domain (NASA, US govt) or rights-restricted.

**Revised priority based on all validation so far:**
1. **PMO scraper** — government, but PMO's terms need the same copyright check before building
2. **Openverse** — CC0/PDM filter gives clean copyright by design
3. **Pixabay** — explicit free-for-commercial-use license, Pexels insurance
4. **Kerala Tourism** — needs copyright validation like Incredible India got

**Recommendation:** Apply the same copyright-first validation to PMO and Kerala Tourism before building either. Incredible India proves that "government site" ≠ "free to use."
