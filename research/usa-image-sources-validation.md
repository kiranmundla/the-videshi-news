# USA Image Sources — Validation Report
**Date:** 2026-10-11
**Status:** VALIDATION ONLY — no implementation until Kiran approves
**Context:** Kiran's directive "let's check also usa resources." We are a US-based diaspora site; 47% of articles are person stories including US politicians and Indian-Americans.

## Verdicts

| Source | Verdict | Why |
|--------|---------|-----|
| White House Flickr | ✅ **VIABLE** | Public domain confirmed, 1024px, no API key, fresh daily |
| Library of Congress | ❌ REJECTED | Historical archive; modern items rights-restricted |
| Smithsonian Open Access | ⚠️ CONDITIONAL | 2.8M CC0 but museum collections, not news; needs key signup |
| State Dept / agencies | ❌ REJECTED | Unreliable (state.gov down); no consistent gallery pattern |
| Congress/House/Senate | ❌ REJECTED | Cloudflare-blocked; no central photo gallery exists |

---

## 1. White House Flickr — ✅ VIABLE

**Copyright:** CONFIRMED public domain. Photo pages carry `"license": "https://www.usa.gov/government-copyright"` with "United States government work" marking. US federal works are public domain under 17 USC §105.

**Quality:** Tested download at `_b` size suffix → **1024×683**, professional White House photographer. Passes our 800px bar. Visually verified: sharp, well-composed (Marine One at White House with crowd).

**Access:** No API key needed. Public RSS/JSON feed:
`https://www.flickr.com/services/feeds/photos_public.gne?id=202101414@N05&format=json&nojsoncallback=1`
Returns 20 most recent photos. Fresh — tested photos dated 2026-10-06 (5 days old).

**Reliability:** Flickr is stable infrastructure. Feed has worked for years.

**Coverage:** President, VP, White House events, bilateral meetings, ceremonies. Directly serves US politics stories and any Modi-Trump / US-India bilateral coverage.

**Caveat — topic matching:** Feed titles are coded (`P20261006MR-2649`), tags are minimal. To match a photo to a story (e.g., "Trump meets Modi"), the pipeline must scrape the individual photo page for its caption/description. This is an extra fetch per candidate but straightforward.

**Automation plan:** Poll feed daily → for person/politics articles, scrape top N photo pages for captions → keyword-match against article → download `_b` size → run through existing quality scorer.

**Effort:** ~half day.

---

## 2. Library of Congress — ❌ REJECTED

**Why:** Two independent failures.

**Failure 1 — Content mismatch.** LOC is a historical archive. Search for "india" returns 1930s travel posters ("See India"). A news site covering current events cannot use 90-year-old images as heroes.

**Failure 2 — Rights trap.** Found one modern photo (Diwali in Times Square, 2024-10-19, access_restricted=false). But its rights advisory reads: *"Publication may be restricted. For information see: 'Camilo Vergara...'"* — the photographer retains rights. LOC's "unrestricted" flag does not mean copyright-free; rights vary per item and must be checked individually. Automating this is a copyright lawsuit waiting to happen.

**API:** Works without key (`loc.gov/...?fo=json`), but that doesn't matter given the above.

**Verdict:** REJECTED for automated news sourcing. Could theoretically serve history/culture features with manual rights review, but that's not our pipeline model.

---

## 3. Smithsonian Open Access — ⚠️ CONDITIONAL

**Copyright:** Clean — 2.8M+ images released as CC0 (public domain dedication). Best copyright terms of any source evaluated.

**Access:** Requires free API key. Signup via api.data.gov (standard US gov key process — email registration, instant issuance). Kiran or operator signs up once; key goes in pipeline env.

**Quality:** Museum-digitized, generally high resolution.

**Coverage problem:** Content is museum collections — art, artifacts, natural history specimens, archival photos. This is not news photography. It will never have a photo of yesterday's White House event or a current Indian-American community leader.

**Use case:** Culture, history, science explainers (e.g., "history of Diwali," artifact stories). Narrow.

**Verdict:** CONDITIONAL — worth the key signup *only* as a low-priority enrichment for culture/history articles. Not a news-hero source. Do not prioritize.

---

## 4. US Government Agencies (State Dept et al.) — ❌ REJECTED

**State Dept:** state.gov returned a "Technical Difficulties" error page during testing. Unreliable as a dependency.

**General pattern:** Unlike the White House, most agencies do not maintain a consistent, scrapable photo gallery. Media is scattered across press releases with no standard structure.

**Verdict:** REJECTED. No reliable automation target.

---

## 5. Congress / House / Senate Photo Galleries — ❌ REJECTED

**Congress.gov:** Cloudflare "Just a moment..." bot challenge — blocked for automated access.

**House.gov:** Loads fine but has no public photo gallery. News pages carry no downloadable photo sets.

**General:** No central congressional photo source exists. Individual members post on social media (X/Instagram), which our copyright bar excludes for re-hosting.

**Verdict:** REJECTED. For US politician stories, fall back to Wikipedia/official portraits (existing chain).

---

## Indian-American Community Orgs — Already Rejected

Batch 2 validation (2026-10-11) already tested FIA, AIA-NY, GOPIO: all "All Rights Reserved," photos credited to commercial agencies. No change.

---

## Recommendation

**Build: White House Flickr** (~half day effort)
- Highest value-to-effort ratio of all US sources tested
- Public domain, no key, fresh, high-res, reliable
- Serves US politics + US-India bilateral stories
- Only caveat (caption scraping for topic match) is solvable

**Later/optional:** Smithsonian key signup for culture/history enrichment.

**Do not build:** LOC, State Dept, Congress galleries.

## Open Question for Kiran
Approve White House Flickr integration? If yes, it slots into the image chain after PMO (for US-politics articles) or as a parallel candidate source in the quality scorer.
