# The Videshi Image Sourcing Strategy — Comprehensive Plan
**Date:** 2026-10-11  
**Status:** DRAFT for Kiran's review — no implementation until approved
**Last updated:** 2026-10-11 12:45 PDT (all validations complete)

## Validation Summary (Oct 11)

| Source | Result | Detail |
|--------|--------|--------|
| PIB (pib.gov.in) | ❌ REJECTED | Small infographics (624px), no photo library |
| PMO (pmindia.gov.in) | ✅ VIABLE | 1556×908 pro photos, copyright allows free use with attribution |
| Brand official sites | ✅ VIABLE | Built — Mother's Recipe proved the concept |
| NASA API | ✅ VIABLE | Built — reliable, public domain |
| White House Flickr | ✅ VIABLE | Public domain confirmed, 1024×683, no key needed |
| DHS multimedia | ✅ VIABLE | Public domain, covers USCIS/ICE/CBP — fills immigration gap |
| Incredible India | ⏳ PENDING | Copyright requires written permission — email sent 2026-10-11 |
| Kerala Tourism | ❌ REJECTED | "All rights reserved" — same trap as Incredible India |
| Openverse | ❌ REJECTED | 80-100% Flickr-sourced, rate-limited from our server |
| Brand press kits | ❌ REJECTED | Abstract art or bot-blocked, worse than brand homepages |
| Diaspora org sites | ❌ REJECTED | All rights reserved, commercial photo credits |
| Library of Congress | ❌ REJECTED | Historical only, modern photos have restrictions |
| Pixabay | ⏳ NEEDS KIRAN | Free key, 2-min signup with email verification |

## Article Mix (Last 100 Articles)

| Type | Share | Current Gap | Best Source |
|------|-------|-------------|-------------|
| Named person | 47% | Medium (dated photos) | Publisher og:image, Wikipedia, official |
| Government/policy | 14% | **HIGH** (57% generic Wikimedia) | **PMO site** |
| Concept/illustrative | 12% | Medium | Pixabay (pending key) |
| Place/destination | 9% | Medium-High | Incredible India (pending permission) |
| Brand/company | 8% | **HIGH** | **Brand official site** (built) |
| Food | 6% | Low-Medium | Publisher, brand sites |
| Sports | 4% | Low | YouTube, publisher |
| Immigration | (subset) | **CRITICAL** | **DHS multimedia** (public domain) |

## Reader-Perspective Gaps (Oct 11 Analysis)

1. **🔴 Immigration imagery** — highest-stakes category, weakest images. DHS fills this.
2. **🟡 Festival emotional vibrancy** — our Diwali photos are correct but flat. Needs smarter queries, not new sources.
3. **🟡 Diaspora-specific imagery** — no free source exists. Needs partnerships or reader submissions (Kiran decision).

## Proposed Source Chain (Final)

For **future articles**, in priority order:

1. **Writer-provided `--official-url`** — most reliable, zero search cost
2. **YouTube maxres** (official channels only) — 1280×720 guaranteed
3. **Brand official site** — for company/brand stories ✅ BUILT
4. **PMO site** — for Modi/Indian government stories (validated, to build)
5. **DHS multimedia** — for immigration stories (validated, to build)
6. **White House Flickr** — for US politics stories (validated, to build)
7. **NASA API** — for space stories ✅ BUILT
8. **Official source auto-discovery** — government/company domains ✅ BUILT
9. **PR Newswire** — press images ✅ BUILT
10. **Pixabay** — Pexels insurance + conceptual (needs Kiran's API key)
11. **Incredible India** — travel destinations (pending permission email reply)
12. **Wikipedia** (800px+, freshness-ranked) — person stories
13. **Wikimedia Commons** (freshness-ranked)
14. **Pexels** — last resort only

## Quality Scoring (Built Oct 11)

Every candidate scored on:
- Source reputation (brand_official=100 → pexels=25)
- Resolution (log scale, 800px minimum)
- Freshness (<1yr +15, <5yr +10, <10yr +5)
- Aspect ratio (16:9 ideal, 1.3–2.0 range)
- Named-person safety preserved (verified sources only)

## Implementation Phases

**Phase 1:** PMO scraper (~1 day) — copyright cleared, images validated
**Phase 2:** DHS multimedia (~half day) — fills critical immigration gap
**Phase 3:** White House Flickr (~half day) — US politics coverage
**Phase 4:** Pixabay (~2 hours) — needs Kiran's API key signup first

**Total:** ~2.5 days

**Status:** No implementation until Kiran gives explicit go-ahead per phase.

## Blocked on Kiran

1. **Pixabay API key** — 2-minute signup at pixabay.com/api/docs (email verification required)
2. **Phase approvals** — go/no-go per phase above
3. **Diaspora imagery partnerships** — no free source exists; needs org outreach or reader submissions
4. **Incredible India** — permission email sent; awaiting reply

## Long-Term

- Weekly image-source hunt (Saturdays) continues finding new sources
- Brand domain map expands via weekly hunt (not a separate build)
- Incredible India + Kerala Tourism could unlock with permission emails (template ready)
- Quarterly review: are new sources actually improving quality? Check the data.
