# Enrichment Audit — 2026-11-16

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 97 unique articles on the homepage feed (down from 116 on 2026-11-09). Live feed generated 2026-11-16 16:12 UTC; the live slug set and the local feed file are identical (97/97). All 97 found in `p2_articles`. Zero articles with zero sources; zero with only one source — the ≥2-source gate holds for the fifth straight week. Only 1 article missing the `key_takeaways` column at audit start (a trailer brief; fixed below).

**Reportable items this week (details below):**
1. **`price_compare` is being used as the writer's default stat table — 23 of 97 articles carry 34 `price_compare` cards, up from 0 cards last week, and the sampled cards are generic Item/Value lists, not price comparisons** (Earthshot "in Numbers", a VT-4B tank spec sheet, the Gates Foundation funding split). The cards render (they are `type`-keyed), but the type is semantically wrong and it inflates the price_compare adoption metric to meaninglessness. Writer-side fix, named below.
2. **Every hero the sourcer landed this run carries a one-word caption** ("Four", "Mysuru", "KPMG", "LangChain") — the Nov 14 caption standard says one-word captions fail (caption must name the depicted subject + credit/license). Pipeline defect in the sourcer's fallback caption, named below.
3. **One category payload crossed the +25% flag line: travel +43.9%** — traced to article volume (21 → 31 articles, +48%), per-article bytes flat. Explained below; not a code/asset regression.
4. **X embeds are still 0** (TwitterAPI.io depleted since 2026-11-06; top-up still Kiran's). Partially offset: embed/inline richness recovered from 8.6% to 30.9% of homepage articles on inline images + Instagram embeds.

No zero-source article, no visual story without an image, no utility external-link breach, and no new dead travel-gallery key.

## Hero-image coverage — 43 no-hero at start, 37 of them deliberate blocks

**43 of 97 homepage articles (44.3%) had no hero at audit start, vs 35 of 116 (30.2%) on 2026-11-09. After this run's sourcer fixes, 39 of 97 (40.2%).**

Of the 43: **37 carry `image_backfill_blocked = true`** (deliberate stay-imageless per the verified-or-nothing bar — the quality-first posture working as designed, not sourcer failures). Only 6 were unblocked; all 6 were run through `image_sourcer.py --apply` — 4 landed and were DB-verified:

- `four-earthquakes-jammu-kashmir-doda-kishtwar-leh-no-damage` — Kashmir Horizon og:image (earthquake graphic, 1920×1080), DB-confirmed; caption written as "Four" (see item 2)
- `iaf-helicopter-modi-convoy-technical-snag-grounded-mysuru` — BizzBuzz og:image (1500×900), DB-confirmed; caption "Mysuru"
- `kpmg-sports-tech-hub-bengaluru-40-billion-industry-2030` — ascendants.in og:image (1600×900), DB-confirmed; caption "KPMG"
- `langchain-raises-300-million-3-billion-valuation-capitalg` — YouTube thumbnail (1280×720, "The Daily Orb" channel video on the raise), DB-confirmed; caption "LangChain". Note: a third-party channel's thumbnail is a weaker relevance claim than an official/og source — flagged here for reviewer awareness; not reverted.

2 found no verified candidate (correct fail-closed behaviour):
- `h1b-extension-deference-rule-comment-period-closed` — sourcer's headline entity extraction produced garbage lookups ("Comment Window", "End Deference") and the named-person guard then held it imageless. Same headline-extraction defect family as the Oct 22 "Backlash Sareen" finding; the article itself is a policy story that could carry a generic official image.
- `titan-shukriya-karigar-diwali-film-16000-artisans` — no verified candidate; the article already carries 1 social embed, so it is not bare.

The 37 blocked: `air-india-us-flights-on-schedule-ground-stop-update`, `anthropic-claude-login-outage-november-13`, `bihar-teen-adarsh-kumar-diana-award-skillzo`, `chris-wood-jefferies-india-reverse-ai-trade-iran-energy-hedge`, `faa-ground-stop-l3harris-router-copper-fibre-upgrade-duffy`, `gambhir-concerned-india-batting-collapses-new-zealand-odi`, `goldman-sachs-india-growth-2027-china-forecast`, `gondhal-director-santosh-davakhar-india-oscar-entry-anxiety`, `goyal-egypt-india-startup-forum-upi-instapay-cairo`, `harmanpreet-kaur-wax-statue-jaipur-171-knock`, `india-beat-pakistan-one-wicket-last-ball-u19-asia-cup-final`, `india-clears-26-new-border-roads-arunachal-icbr-iii-hindu-reports`, `india-government-health-spending-triples-nha-2023-24`, `india-pakistan-u19-asia-cup-2026-final-preview-al-amerat-oman`, `india-positive-ties-bangladesh-mea-hasina-extradition`, `india-reportedly-sets-two-conditions-sheikh-hasina-return-bangladesh`, `india-seal-odi-series-new-zealand-no1-ranking`, `india-votes-against-un-death-penalty-moratorium`, `indian-accent-top-standalone-restaurant-hospitality-horizon-2026`, `indian-students-us-fall-6-5-percent-open-doors-2026`, `jay-shah-reappointed-icc-chair-second-term-bali`, `lakshya-raichandani-never-stopped-believing-u19-asia-cup-final`, `lalit-modi-british-citizenship-extradition`, `man-dies-explosive-handed-as-rasgulla-dindori-madhya-pradesh`, `mattancherry-taunton-kerala-restaurant-tripadvisor-best`, `megna-jain-dream-a-dozen-cupcakes-rs-5000-bakery`, `microsoft-november-2026-patch-tuesday-1094-flaws-outlook-zero-day`, `mookuthi-amman-2-review-roundup-critics`, `new-toyota-fortuner-spied-argentina-india-launch-2027`, `priya-sundareshan-arizona-senate-president-elect`, `ramayana-11-day-worldwide-record-dhurandhar-2-sacnilk`, `tanker-hits-american-heritage-new-orleans-all-accounted-for`, `tata-jlr-targets-double-digit-earnings-growth-fiscal-2028-guidance-cut`, `u19-cricketer-nandini-17-dies-suicide-telangana-family-alleges-harassment`, `us-prosecutors-seek-293-months-nikhil-gupta-pannun-sentencing`, `wellfed-bengaluru-couple-quits-it-rs-56-lakh-meals`, `who-el-nino-health-emergency-india-high-risk`.

**Watch item:** the blocked share is growing (32 of 116 → 37 of 97) as the feed shrinks under quality-first. Intentional nulls are correct per-article, but homepage visual density is now 59.8% with-hero. If the trend continues it becomes a homepage-design question for Kiran, not a sourcer problem.

**Captions:** among the 54 articles that had a hero at audit start, **0 were missing `image_caption` (100%)**, vs 3.7% missing on 2026-11-09. Presence is perfect; the defect is quality on the sourcer's own new writes (item 2).

**Sourcer environment note:** `cv2 4.10.0` with `CascadeClassifier` verified present this week — no reinstall needed (first week in three the VM wipe did not recur).

## Health snapshot

| Check | 2026-11-09 | 2026-11-16 |
|---|---|---|
| Articles audited | 116 | 97 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 0 | 0 |
| Utility external-link flags | 1 (not genuine) | 0 |
| No hero image | 35 → 33 after fix (28.4%) | 43 → 39 after fix (40.2%; 37 of 43 blocked by design) |
| Visual story with no image | 0 | 0 (only 1 visual story on the feed; it has a hero) |
| Missing key_takeaways column | 0 | 1 → 0 after fix |
| Missing data cards | 17 (2 by design) | 6 (1 by design) |
| word_count NULL/0 | 3 → 0 after fix | 2 → 0 after fix |
| Articles with any embed/social/gallery element | 10 of 116 (8.6%) | **30 of 97 (30.9%)** |

Other measured gaps:

- **Embed mix:** X-bearing articles 0 (was 2 last week, 37 the week before — TwitterAPI.io depletion, unchanged cause). Instagram-bearing 4 (`air-india-restores-nonstop-new-york-flights`, `air-india-us-flights-on-schedule-ground-stop-update`, `india-beat-pakistan-one-wicket-last-ball-u19-asia-cup-final` ×2 embeds, `rahul-gandhi-fascists-bharat-summit-hyderabad-gig-workers`). `social_embeds` column non-empty on 1 (`titan-shukriya-karigar-diwali-film-16000-artisans`). YouTube 0 by the embed-tag regex (plain `youtube.com/watch?v=` URLs in bodies are not counted — same basis as previous weeks; both review articles carry one). 69 of 97 bodies have zero inline `<img>` beyond the hero, but 26 articles carry 1–2 inline images — the recovery from last week's 8.6% is inline-image driven.
- **Social-native stories:** the audit script flagged **none** this week — no homepage headline matching instagram/viral/reel/youtube/tiktok/twitter lacks an embed. Clean.
- **Utility links:** zero flags. All 8 immigration and 5 travel homepage articles carry external links; the immigration set links official sources where it matters (`canada.ca` ×2, `govinfo.gov` + `regulations.gov` on the H-1B deference story, `irishimmigration.ie`). Soft note only: `air-india-us-flights-on-schedule-ground-stop-update` (travel) links two news outlets and no airline/FAA page — not a breach of the zero-link rule.
- **Word count:** 2 stored NULLs fixed (below). Genuine measured sub-400: only `mattancherry-taunton-kerala-restaurant-tripadvisor-best` (stored 362, body measures 377 — a thin restaurant-recognition story; it is also hero-blocked). By design: `raviteja-mouli-trailer-out` (93 measured — a trailer brief, ~75-word format).
- **Review bar — now measured against the Nov 15 synthesized-voice standard** (single-voice Videshi review, no outlet/critic names in prose): the feed's two reviews split exactly on the gate date. `scene-review-roundup-critics` (published 2026-11-15, 810 words) is fully compliant — zero outlet/critic names, judgments rendered directly, `movie_review_ratings` 3.5★. `mookuthi-amman-2-review-roundup-critics` (published 2026-11-13, 666 words, **before** the voice gate shipped) is old-style throughout: names The Times of India, Filmfare, NDTV, Gulte, The Hindu and a named critic (Latha Srinivasan, NDTV), "Critics broadly agree… averaging a 2-star rating" in its ratings card. Not a gate leak — a pre-gate legacy article still on the homepage. Rewriting it to the new voice is Kiran's call, not an audit auto-fix.
- **price_compare misuse (item 1):** 23 articles carry `price_compare`: `apple-health-ai-usage-study-openevidence-200000-iphone`, `bharat-semi-24-million-seed-ai-image-sensors` (×2), `china-upgrades-vt4b-tank-pakistan-anti-drone-armour`, `chris-wood-jefferies-india-reverse-ai-trade-iran-energy-hedge` (×2), `earthshot-prize-awards-mumbai-november-17-indian-finalists`, `fpi-7-5-billion-november-indian-equities-five-year-high` (×2), `gates-foundation-1-billion-family-planning-womens-health-2030`, `goyal-egypt-india-startup-forum-upi-instapay-cairo`, `h1b-extension-deference-rule-comment-period-closed` (×2), `india-2029-champions-trophy-2031-world-cup-icc-calendar-2035`, `india-government-health-spending-triples-nha-2023-24` (×2), `indian-students-us-fall-6-5-percent-open-doors-2026` (×2), `jay-shah-reappointed-icc-chair-second-term-bali`, `jefferies-buy-ratings-six-adani-stocks-51-billion-capex`, `lakshya-raichandani-never-stopped-believing-u19-asia-cup-final` (×2), `lalit-modi-british-citizenship-extradition`, `masala-omelette-anda-bhurji-tasteatlas-50-best-egg-dishes` (×3, alongside a genuine `recipe` card), `mattancherry-taunton-kerala-restaurant-tripadvisor-best`, `microsoft-november-2026-patch-tuesday-1094-flaws-outlook-zero-day` (×2), `modi-manila-asean-india-east-asia-summits-agenda`, `priya-sundareshan-arizona-senate-president-elect`, `ramayana-11-day-worldwide-record-dhurandhar-2-sacnilk` (×2), `us-prosecutors-seek-293-months-nikhil-gupta-pannun-sentencing`. Sampled cards are all Item/Value stat lists — the writer is emitting its generic numbers table as `price_compare` instead of `stat_grid`. Fix belongs in the writer instructions / card-type gate (map Item/Value tables to `stat_grid`; reserve `price_compare` for actual price comparisons), not in per-article edits.

**Data-card adoption (97 articles):** stat_grid 59, price_compare 34 (see misuse above — true stat-table total is effectively 59 + most of 34), comparison 33, timeline 15, key_dates 10, highlights 6, checklist 3, match_scorecard 3, movie_review_ratings 2, recipe 1. **Zero this week: how_to, critic_table** (critic_table's absence is now expected under the synthesized-voice standard — it is reserved for explicitly framed roundups; how_to had 2 last week — homepage composition).

**No data cards (6):** 1 by design (`raviteja-mouli-trailer-out`, trailer brief — its Film information card is body HTML, not a data card), plus 5 genuine enricher-fit candidates: `delhi-police-special-cell-arrests-shooters-bollywood-actor-plot` (611w), `iaf-helicopter-modi-convoy-technical-snag-grounded-mysuru` (446w; gained a hero this run), `janakpur-dham-ayodhya-weekly-train-service-604-km` (463w, has 2 inline images), `jd-vance-weighs-skipping-2028-presidential-race-midterm-losses-cnn` (792w, has 2 inline images), `u19-cricketer-nandini-17-dies-suicide-telangana-family-alleges-harassment` (525w, also hero-blocked). Down from 15 genuine last week. Not auto-added — same never-pad reasoning as previous weeks.

## Auto-fixes applied this run (all verified after patch)

1. **word_count backfilled (3):** `mookuthi-amman-2-review-roundup-critics` NULL → 666, `scene-review-roundup-critics` NULL → 810, `raviteja-mouli-trailer-out` 74 → 93 (pipeline convention: strip tags, unescape, split; all DB-verified). The writer's NULL-word_count bug is still not fixed at source — sixth week running it has produced homepage cases.
2. **key_takeaways backfilled (1):** `raviteja-mouli-trailer-out` column NULL → the 3 items already present in its body takeaways div (DB-verified).
3. **Image sourcer run on all 6 unblocked imageless articles:** 4 applied and DB-verified (`four-earthquakes-jammu-kashmir-doda-kishtwar-leh-no-damage`, `iaf-helicopter-modi-convoy-technical-snag-grounded-mysuru`, `kpmg-sports-tech-hub-bengaluru-40-billion-industry-2030`, `langchain-raises-300-million-3-billion-valuation-capitalg`); `h1b-extension-deference-rule-comment-period-closed` and `titan-shukriya-karigar-diwali-film-16000-artisans` found no verified candidate (correct per the wrong-photo bar). The 37 blocked articles were not forced.
4. **Not auto-fixed (named for pipeline fixes):** the sourcer's one-word fallback captions (item 2) and the writer's `price_compare` default (item 1) — both are producer-side defects; per-article edits would recur next run.

## Performance watch — 1 payload over the +25% flag line, volume-driven

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded):

| Payload | Nov 9 live | Nov 16 live | WoW |
|---|---|---|---|
| `data/homepage-feed.json` gz | 99,237 | 88,229 | −11.1% (slugs 116 → 97) |
| `data/category/news.json` gz | 35,806 | 39,675 | +10.8% (articles 51 → 61) |
| `data/category/entertainment.json` gz | 24,413 | 21,717 | −11.0% |
| `data/category/sports.json` gz | 31,203 | 21,928 | −29.7% |
| `data/category/markets-finance.json` gz | 38,238 | 24,508 | −35.9% |
| `data/category/immigration.json` gz | 19,465 | 21,310 | +9.5% |
| `data/category/travel.json` gz | 15,366 | 22,114 | **+43.9% ⚠️** (articles 21 → 31, +48%) |
| `data/category/technology.json` gz | 27,028 | 25,456 | −5.8% |
| `data/category/food.json` gz | 28,427 | 13,834 | −51.3% |
| `data/category/lifestyle-health.json` gz | — (new baseline) | 14,564 | — (19 articles) |
| `data/category/nri-world.json` gz | — (new baseline) | 31,161 | — (47 articles) |
| Main JS gz | 244,539 (`index-Dv_LXwyI.js`) | 244,560 (`index-DWdQcfSU.js`) | +0.0% — new build hash, same size |
| Main CSS gz | 31,208 (`index-D8GMxP0j.css`) | 31,359 (`index-NBv6aZlI.css`) | +0.5% — new build hash |
| Homepage HTML | 6,563 raw | 6,563 raw | 0% |

**Verdict:** the single >25% flag (travel) tracks its article count almost 1:1 (per-article gzipped bytes: 732 → 713, flat), so it is story volume, not an un-minified/duplicated asset or a feed-format regression, and nothing was auto-fixed. The homepage feed itself shrank 11.1%. Nothing is over ~500 KB gzipped (largest is the JS bundle at 244,560). Article counts for travel/news are from the local category files' git history at the Nov 9 audit point (commits `a64fc87b` era) vs today's files.

## Travel gallery coverage — no change: dead keys 0, uncovered 18 (all legacy)

Simulation of the page's exact first-match rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 0** — unchanged, no new dead key.
- **Uncovered experiences (b): 18 — identical legacy baseline, nothing new:** bahamas: Thunderball Grotto, Exumas · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora (left empty on purpose in the Oct 24 fill — no verified photo of the Arpora market exists on Commons) · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge).
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (neither has a gallery entry at all; unchanged legacy baseline).

**Week-over-week:** dead keys 0 → 0, uncovered 18 → 18 (same list). Every remaining item is the known legacy baseline. Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/gallery_2026-11-16.json`). Nothing auto-fixed per instructions (key renames/reorders are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-11-16_raw.json`; extra visual/blocked/caption pass: `hidden_files/extra_2026-11-16.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-11-16.py` — word_count + key_takeaways fixes (image fixes via `pipeline/image_sourcer.py --apply` on the 6 unblocked slugs)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (results: `hidden_files/gallery_2026-11-16.json`)
