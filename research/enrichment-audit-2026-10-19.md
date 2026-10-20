# Enrichment Audit — 2026-10-19

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 108 unique articles on the homepage feed (generated 2026-10-19 13:20 UTC). All 108 found in `p2_articles`. Zero articles with zero sources; zero with only one source; no visual story without an image; zero utility articles missing external links.

## ⚠️ Critical finding — homepage hero-image coverage collapsed

**25 of 108 homepage articles (23%) have no hero image, vs 3 of 115 (2.6%) in the 2026-10-12 audit.** This is a reader-facing regression in how the homepage looks, even though the underlying cause is the quality gate working as designed (see below).

DB-wide imageless share by publish date (published articles, measured today):

| Date | Published | No hero | of which `image_backfill_blocked` |
|---|---|---|---|
| Oct 5–13 | ~540 | 0–6/day (≤1 typical, 6 on Oct 12) | most |
| Oct 14 | 54 | 7 | 7 |
| Oct 15 | 71 | 12 | 7 |
| Oct 16 | 73 | 26 | 14 |
| Oct 17 | 59 | 10 | 7 |
| Oct 18 | 50 | 8 | 7 |
| Oct 19 | 32 | 7 | 6 |

The break starts Oct 14–16, not this week. Of the 25 homepage cases: 19 carry `image_backfill_blocked = true`; the other 6 were run through `image_sourcer.py --apply` in this audit (see Auto-fixes) and the sourcer found **no verified image for any of them** — several are named-person stories where the sourcer deliberately stays imageless rather than risk a wrong photo (`chinmay-sutar-unbeaten-400-ranji-trophy-second-indian`, `min-woo-lee-withdraws-delhi-stomach-illness-back-spasms`, `rakesh-nidagundi-para-shooting-asian-para-games-gold`). None of the 25 is flagged `is_visual_story`, so the "visual story with no image" red line is not breached.

**Systemic wart found while sourcing:** the named-person entity extraction feeding the sourcer produces garbage/truncated entities that trigger the stay-imageless rule — `'British Mother'` (for `british-mother-referred-prevent-counter-extremism-programme-israel-trip`), `'Para Shooter'` (Rakesh Nidagundi article), `'Unbeaten Only'` (a second "person" extracted from the Chinmay Sutar headline), `'Min Woo'` (truncated from Min Woo Lee). Fixing entity extraction would let some of these articles take a legitimate non-person hero (venue/event/object) instead of none.

The 25: `anshul-kamboj-test-recall-new-zealand-india-squad`, `anthropic-junior-tech-hiring-falls-ai-agents-report`, `bodies-three-keralites-germany-fire-arrive-kochi-october-20`, `british-mother-referred-prevent-counter-extremism-programme-israel-trip`, `chinmay-sutar-unbeaten-400-ranji-trophy-second-indian`, `eight-mgnrega-workers-killed-speeding-car-sangrur`, `flavors-of-bollywood-nycwff-indian-cuisine-maneet-chauhan-vijay-kumar`, `fssai-proposes-ban-added-sugars-infant-food-under-six-months`, `google-adopts-pyrefly-python-type-checker`, `india-diwali-gulf-war-tighter-budgets-spending`, `indian-national-ice-arrest-false-citizenship-claim-vote-2024-minnesota`, `jay-patel-flowers-of-forest-hills-new-york-stage`, `karnataka-night-time-attendance-doctors-taluk-hospitals-phcs`, `kenya-ebola-cases-rise-seven-health-workers`, `kkr-6000-crore-investment-petronas-gentari-renewable-india`, `madurai-influencer-veeramani-diwali-sweets-cod-prank`, `manipur-four-killed-firewood-ambush-protest-cm-bungalow`, `manjit-singh-bedi-snap-fraud-returned-from-india`, `min-woo-lee-withdraws-delhi-stomach-illness-back-spasms`, `nri-capital-gains-basic-exemption-limit-guide`, `rahul-agarwal-polygons-shark-tank-350000-deal`, `rakesh-nidagundi-para-shooting-asian-para-games-gold`, `sammy-west-indies-india-series-sponsors-finances-draw`, `seven-arrested-kolkata-pandal-collapse-warning-crush`, `simran-sharma-replaces-bhavina-patel-flag-bearer-para-asian-games`.

**Decision for Kiran (not auto-fixed):** 23% imageless is the price of the current strictness. Options: (a) accept it (bar holds, homepage looks text-heavy), (b) fix the entity-extraction wart above and re-run the sourcer on the non-person cases, (c) allow verified non-person heroes (stadium/venue/object) on named-person stories when no verified portrait exists.

## Health snapshot

| Check | 2026-10-12 | 2026-10-19 |
|---|---|---|
| Articles audited | 115 | 108 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 12 | **0 — the Oct 15 ≥2-source gate (commit 4ffd217e0) is holding** |
| Utility (immigration/travel) with no external links | 5 | **0 — all 14 have ≥2 external links** |
| No hero image | 3 | 25 (see critical finding) |
| Missing key_takeaways column | 8 | 1 → 0 after fix |
| Missing data cards | 11 (after fixes) | 11 (2 are briefs by design) |
| word_count NULL/0 | 10 | 2 → 0 after fix |

Other measured gaps:

- **Hero captions:** 33 of 83 articles with a hero (40%) have no `image_caption`. (Today's commit cd6fada9d added verified captions to some; the column is still empty for these 33 — full slug list in the raw JSON.)
- **Inline richness:** 94 of 108 bodies have zero inline `<img>` beyond the hero; 55 of 108 have at least one embed/social/gallery element (YouTube, X, Instagram, social_embeds, or gallery).
- **Word count:** only real flags — `mughal-mahal-mississauga-expanding-brampton-amritsari-kulcha` stored 381 but body measures 513 (stored value stale; body is fine, ≥400 either way it was flagged on the stored number), `akka-keerthy-suresh-radhika-apte-teaser-out` 70 words is a trailer brief by design (~75-word bar) with the film-info card in-body.
- **Review bar:** the one homepage review, `prahaar-review-roundup-critics`, names the rating publications with scores (IANS 4.5, Bollywood Hungama 4, India Forums 3.5, IWMBuzz 3.5, GG2 3) and specific performances/scenes (Lalit Prabhakar's Kasab, Rajkummar Rao's Nikam, Jaideep Ahlawat's post-interval entry, 140-minute runtime reservation). Better than last week's roundup; individual critic *names* are still absent — publications only.

**Data-card adoption (108 articles):** stat_grid 94, comparison 51, timeline 20, key_dates 8, highlights 7, match_scorecard 2, price_compare 2, checklist 2, how_to 1, movie_review_ratings 1. **Still zero adoption: recipe, critic_table.**

**No data cards (11):** `akka-…teaser-out` (trailer brief, film-info card in body — by design), `happening-2026-10-18-south-africa-cricket-vs-australia-cricket` (brief — by design), plus 9 genuine fits for the enricher's card pass: `iit-kharagpur-solar-powered-vending-cart-street-vendors`, `katie-zacharia-out-white-house-press-secretary-five-days`, `kkr-6000-crore-investment-petronas-gentari-renewable-india`, `manipur-four-killed-firewood-ambush-protest-cm-bungalow`, `min-woo-lee-withdraws-delhi-stomach-illness-back-spasms`, `mughal-mahal-mississauga-expanding-brampton-amritsari-kulcha`, `mythily-rasika-venkatesa-williamsburg-south-indian-restaurant`, `siblings-indigo-flight-rahul-dravid-front-row-jaipur`, `ucla-nashaa-bollywood-dance-team-best-of-the-best-netflix`. Not auto-added: the two bodies read closely (KKR, IIT Kharagpur) have too few hard numbers for an honest stat_grid — padding a card would break the never-pad rule.

## Auto-fixes applied this run

1. **word_count backfilled (2, verified after patch):** `prahaar-review-roundup-critics` NULL → 721; `happening-2026-10-18-south-africa-cricket-vs-australia-cricket` NULL → 134. (Pipeline convention: strip tags, unescape, split — same as the 2026-10-12 autofix. The NULL-word_count insert bug from last week is still not fixed at the writer; these are the only 2 homepage cases.)
2. **key_takeaways column backfilled (1):** `akka-keerthy-suresh-radhika-apte-teaser-out` — body already rendered the takeaways div (3 items); column was empty. Extracted verbatim, verified 3 items stored. Same writer column-sync bug as last week, now down to 1 homepage case.
3. **Image sourcer run on all 6 unblocked imageless articles** (`chinmay-sutar…`, `british-mother…`, `indian-national-ice-arrest…`, `manjit-singh-bedi…`, `min-woo-lee…`, `rakesh-nidagundi…`): zero images applied — sourcer found no verified candidate for any (correct behaviour per the wrong-photo bar). The other 19 are `image_backfill_blocked` and were not forced.

## Performance watch — NO regression

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded), with git-history comparators for the same files:

| Payload | Oct 12 (git) | Oct 17 (git) | Oct 19 live | WoW |
|---|---|---|---|---|
| `data/homepage-feed.json` gz | 101,447 | 88,552 | 89,954 | +1.6% vs Oct 17 local-gz 89,123 — flat |
| `data/category/news.json` gz | 62,852 | 47,055 | 42,901 | **−9%** |
| `data/category/entertainment.json` gz | 34,021 | 30,568 | 27,787 | **−9%** |
| `data/category/sports.json` gz | — | — | 28,378 | — |
| `data/category/markets-finance.json` gz | — | — | 29,327 | — |
| `data/category/immigration.json` gz | — | — | 29,147 | — |
| `data/category/travel.json` gz | 15,827 | 17,122 | 17,286 | +1% — flat |
| Main JS `/assets/index-DE4dLYcE.js` gz | — | — | 244,393 | first baseline recorded |
| Main CSS `/assets/index-DYX09FXp.css` gz | — | — | 31,204 | first baseline recorded |
| Homepage HTML | — | — | 6,563 raw | — |

No payload grew >25% WoW; nothing is over ~500 KB gzipped (largest is the JS bundle at 244 KB). Note on the standing baseline: the "category JSON ≈ 21 KB gzipped" figure from 2026-10-17 does not match any full category file in git at Oct 12/17/19 — these files carry 23–64 articles and have run 16–63 KB gz throughout, trending *down*. The ≈8 KB / 18-row archive-fetch baseline is a different (paginated) payload and is unaffected.

## Travel gallery coverage — no NEW dead keys or uncovered experiences

Simulation of the page's exact matching rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 11** — bali: `Tegallalang Rice Terraces`, `Tanah Lot`; goa: `Spice Plantation`; kerala: `Kathakali`; london: `Tower of London`, `Neasden Temple`; maldives: `Bioluminescent Beach`, `Whale Shark`; new-zealand: `Hobbiton`; sri-lanka: `Nine Arches Bridge`; switzerland: `Bernina Express`.
- **Uncovered experiences (b): 29** — bahamas: Thunderball Grotto, Exumas · bali: Seminyak Beach Clubs; Tirta Empul Water Temple, Tampaksiring · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora · kerala: Varkala Cliff Beach · london: West End Theatre; Day Trip to Oxford or Bath · maldives: Malé Fish Market & Hukuru Miskiiy; Sunset Dolphin Cruise · mexico: San Miguel de Allende · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge) · new-zealand: Abel Tasman Coastal Track, South Island · sri-lanka: Jaffna & the North · switzerland: Grindelwald First Cliff Walk.
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (both guides have 7 experiences each).

**Newness check (git):** the dead/uncovered/no-block sets are *identical* at the 2026-10-17 post-fix commit (6789f4ba3), at both 2026-10-18 gallery commits (45d645ae9, b5e56d5d9), and today. Guides unchanged since Oct 17. **All of the above is the known legacy baseline — nothing new this week.** Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/travel_gallery_check.py`, results `/tmp/gallery_2026-10-19.json`). Not auto-fixed per instructions (key renames are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-10-19_raw.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-10-19.py` — word_count / takeaways fixes
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (new this run; diffs cleanly against git baselines)
