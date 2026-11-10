# Enrichment Audit — 2026-11-09

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 116 unique articles on the homepage feed (up from 94 on 2026-11-02). Live feed generated 2026-11-09 15:50 UTC; the local feed file (16:18 UTC) carries the identical 116-slug set. All 116 found in `p2_articles`. Zero articles with zero sources; zero with only one source — the ≥2-source gate holds for the fourth straight week. Zero articles missing the `key_takeaways` column.

**Two reportable items this week (details below):**
1. **Embed richness collapsed — X embeds fell from 37 homepage articles (2026-11-02) to 2.** Cause is known: TwitterAPI.io is fully depleted (zero balance since 2026-11-06), so enrichment runs without X-embed sourcing until Kiran tops it up. This is the one item needing Kiran's hands.
2. **Four category payloads grew >25% week over week** (news, sports, markets-finance, food) — traced to article volume, not a code/asset regression: per-article gzipped bytes are flat, and the JS/CSS/HTML are byte-identical to last week. Flagged per the >25% rule, explained below.

No zero-source article, no visual story without an image, no genuine utility external-link breach, and no new dead travel-gallery key.

## Hero-image coverage — 35 no-hero, but 32 are deliberate blocks

**35 of 116 homepage articles (30.2%) had no hero at audit start, vs 27 of 94 (28.7%) on 2026-11-02. After this run's sourcer fixes, 33 of 116 (28.4%).**

Of the 35: **32 carry `image_backfill_blocked = true`** (deliberate stay-imageless per the wrong-photo bar — not sourcer failures). Only 3 were unblocked; all 3 were run through `image_sourcer.py --apply` — 2 landed and were DB-verified:

- `health-insurance-pollution-illness-cover-india-guide` — Policybazaar Partners og:image (rising air pollution, 1201×631), DB-confirmed
- `maharashtra-fda-suspends-105-food-licences-diwali-seizes-1-35-crore` — Moneycontrol og:image (seized paneer, 1280×720), DB-confirmed

1 found no verified candidate (correct behaviour): `major-curry-affair-tipton-restaurant-of-the-year-bca-2026`.

The 32 blocked: `army-debunks-fake-50km-chinese-incursion-arunachal-claim`, `best-indian-restaurants-london-cn-traveller-27`, `captain-amit-bhardwaj-kargil-promise-next-diwali`, `dalal-street-week-ahead-inflation-earnings-foreign-flows`, `delhi-teen-aadvik-jain-wins-diana-award-menstrual-health`, `dhanush-bjp-backing-speculation-political-debut-response`, `diwali-three-item-plate-rule-nutritionist-tips-overeating`, `himachali-feast-himachal-bhawan-delhi-rs-709`, `house-democrats-majority-healthcare-iran-war-tariff-votes`, `hyderabad-student-summitsathi-satellite-weather-receiver-himalayan-villages`, `india-markets-decoupled-global-rout-analysts-rotation`, `india-pacers-arshdeep-gurnoor-nabi-stay-back-new-zealand-tests`, `indigo-air-india-parliamentary-panel-airfares-fuel-pakistan-airspace`, `instagram-features-long-videos-500000-creator-deals-no-revenue-share`, `ipl-trade-ashutosh-sharma-gt-dc-talks`, `israel-hostile-aircraft-alert-false-identification-zarit-shomera`, `makemytrip-india-arm-sebi-nod-ipo`, `mtr-1924-malaysia-michelin-bib-gourmand-2027`, `new-zealand-tickner-ferguson-out-india-odis-clarke-cover`, `nit-trichy-tata-ai-centre-tcs-foundation`, `rekha-arya-husband-girdhari-sahu-arrested-jhansi`, `rjd-mp-sanjay-yadav-president-action-du-professor-ragi`, `santner-tricky-wicket-new-zealand-india-wellington-odi`, `sensex-nifty-end-muhurat-trading-lower-first-time-in-nine-years`, `shadman-islam-ruled-out-south-africa-tour-ankle-injury`, `sitanshu-kotak-kl-rahul-versatility-third-odi-new-zealand`, `soham-basanwar-uic-computer-science-competition-honors`, `thane-raheja-garden-fire-50-rescued-mumbai-diwali-fires`, `triangle-restaurants-yelp-top-100-indian-list`, `uk-budget-2026-skilled-worker-graduate-hpi-visa-changes`, `vikas-khanna-indian-food-abroad-baby-steps-bungalow-authenticity`, `vix-fear-gauge-jumps-11-points-bespoke-history-six-months`.

**Sourcer environment note:** the sourcer again logged `focal-point detection unavailable (No module named 'cv2')` — the VM had wiped the Python package again. Reinstalled `opencv-python-headless==4.10.0.84 --no-deps` during this run and verified `cv2 4.10.0` with `CascadeClassifier` present; the 2 heroes above were center-cropped before the reinstall.

## Health snapshot

| Check | 2026-11-02 | 2026-11-09 |
|---|---|---|
| Articles audited | 94 | 116 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 0 | 0 |
| Utility external-link flags | 0 | 1 (not genuine, see below) |
| No hero image | 27 → 24 after fix (25.5%) | 35 → 33 after fix (28.4%; 32 of 35 blocked by design) |
| Visual story with no image | 0 | 0 (only 1 visual story on the feed; it has a hero) |
| Missing key_takeaways column | 1 → 0 after fix | 0 |
| Missing data cards | 8 (2 by design) | 17 (2 by design) |
| word_count NULL/0 | 1 → 0 after fix | 3 → 0 after fix |
| Articles with any embed/social/gallery element | 39 of 94 (41%) | **10 of 116 (8.6%) ⚠️** |

Other measured gaps:

- **Hero captions near-complete:** only 3 of 81 articles with a hero (3.7%) have no `image_caption`, vs 22% (15/67) on 2026-11-02.
- **Inline richness fell with the embeds:** 81 of 116 bodies have zero inline `<img>` beyond the hero. Embed-bearing articles by type: Instagram 9 (up from 5), X 2 (down from 37), social_embeds 1, YouTube 0 by the script's embed-tag regex (plain `youtube.com/watch?v=` URLs in bodies, e.g. the Cult review's trailer link, are not counted — same measurement basis as previous weeks).
- **Social-native stories (3 flagged, 1 genuine):** `instagram-features-long-videos-500000-creator-deals-no-revenue-share` is a genuine Instagram-platform story with no Instagram embed, empty `social_embeds`, and a blocked hero. The other two are headline-keyword flags only: `viral-dhokla-chaat-diwali-party-starter-recipe` ("Viral" in the headline; it does carry a `recipe` card) and `ninja-crispi-glass-air-fryer-india-review-roundup` ("viral" product roundup). Positive note: `tyra-banks-lehenga-maneesh-goyal-new-york-diwali` now carries the Instagram embed of Banks' own post (`p/DfgDC0EnQn7`) in its body — the gap logged on 2026-11-09 in memory is closed on the live article.
- **Utility links:** the single script flag, `hyderabad-diwali-celebrations-communities-charminar` (travel category, zero external links), is a city Diwali-celebrations report with 2 inline images — not a booking/how-to utility piece, so not a genuine breach of the external-link rule. No immigration article was flagged; all carry external links.
- **Word count:** 3 stored NULLs fixed (below). Genuine measured sub-400: only `affair-with-masala-indian-cuisine-henderson-nevada` (stored 374, body measures 391 — a thin restaurant-opening story, and it also has no data cards). The other stored sub-400s all measure over 400 (`demonte-colony-3-pongal-2027-release-arulnithi` 447, `farmer-mauled-death-tiger-beed-maharashtra-fodder` 441, `soham-basanwar-uic-computer-science-competition-honors` 401). By design: the two `happening-2026-11-*` briefs (293 and 109 measured).
- **Review bar:** the week's one review roundup, `cult-review-roundup-critics` (731 words measured), names publications only (The Hindu, Times of India), gives an average 2.5/5 and a `movie_review_ratings` card, with climax/performance material but no individual critic names — the same thinner pattern as last week's `udta-teer` roundup. No `critic_table` this week (last week's Ramayana first adoption was homepage composition, not a regression).

**Data-card adoption (116 articles):** stat_grid 89, comparison 47, timeline 24, checklist 4, highlights 3, key_dates 2, how_to 2, match_scorecard 2, movie_review_ratings 1, recipe 1. **Zero this week: price_compare, critic_table** (both seen in earlier weeks; homepage composition).

**No data cards (17):** 2 by design (the two happening briefs), plus 15 genuine enricher-fit candidates — up from 6 genuine last week: `affair-with-masala-indian-cuisine-henderson-nevada` (374w), `army-debunks-fake-50km-chinese-incursion-arunachal-claim` (467w, also blocked/no-hero), `celina-jaitly-second-diwali-away-from-sons-emotional-message` (598w), `daler-mehndi-diwali-message-mika-singh-uttarakhand-stage-row` (596w), `dhanush-bjp-backing-speculation-political-debut-response` (567w, also blocked/no-hero), `dhanush-diwali-pongal-solomon-pappaiah-tribute` (660w), `dhanush-sai-pallavi-sita-ramayana-no-one-else` (648w), `farah-khan-era-of-superstars-over-double-date` (799w), `indian-truck-simulator-delhi-real-roads-2027-steam` (510w), `kanpur-roof-collapse-kills-three-family-newborn-panki` (772w), `rjd-mp-sanjay-yadav-president-action-du-professor-ragi` (565w, also blocked/no-hero), `samay-raina-medha-shankr-diwali-photo` (679w), `sitanshu-kotak-kl-rahul-versatility-third-odi-new-zealand` (526w, also blocked/no-hero), `trump-cbs-60-minutes-deportation-policy-too-tough` (532w), `tyra-banks-lehenga-maneesh-goyal-new-york-diwali` (507w). Not auto-added — same never-pad reasoning as previous weeks.

## Auto-fixes applied this run (all verified after patch)

1. **word_count backfilled (3):** `cult-review-roundup-critics` NULL → 731, `happening-2026-11-08-diwali-festival-of-lights` NULL → 293, `happening-2026-11-09-pakistan-cricket-vs-sri-lanka-cricket` NULL → 109 (pipeline convention: strip tags, unescape, split; all DB-verified). The writer's NULL-word_count bug is still not fixed at source — fifth week running it has produced homepage cases.
2. **Image sourcer run on all 3 unblocked imageless articles:** 2 applied and DB-verified (`health-insurance-pollution-illness-cover-india-guide`, `maharashtra-fda-suspends-105-food-licences-diwali-seizes-1-35-crore`); `major-curry-affair-tipton-restaurant-of-the-year-bca-2026` found no verified candidate (correct per the wrong-photo bar). The 32 blocked articles were not forced.
3. **cv2 reinstalled** (`opencv-python-headless==4.10.0.84`, `--no-deps`) after the VM wipe, restoring focal-point detection for subsequent sourcer runs; import verified.

## Performance watch — 4 payloads over the +25% flag line, all volume-driven

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded):

| Payload | Nov 2 live | Nov 9 live | WoW |
|---|---|---|---|
| `data/homepage-feed.json` gz | 81,603 | 99,237 | +21.6% (slugs 94 → 116, +23%) |
| `data/category/news.json` gz | 24,370 | 35,806 | **+46.9% ⚠️** (articles 35 → 52, +49%) |
| `data/category/entertainment.json` gz | 23,622 | 24,413 | +3.3% |
| `data/category/sports.json` gz | 21,438 | 31,203 | **+45.5% ⚠️** (articles 33 → 51, +55%) |
| `data/category/markets-finance.json` gz | 28,951 | 38,238 | **+32.1% ⚠️** (articles 42 → 54, +29%) |
| `data/category/immigration.json` gz | 19,725 | 19,465 | −1.3% |
| `data/category/travel.json` gz | 14,331 | 15,366 | +7.2% |
| `data/category/technology.json` gz | 26,786 | 27,028 | +0.9% |
| `data/category/food.json` gz | 16,395 | 28,427 | **+73.4% ⚠️** (articles 22 → 40, +82%) |
| Main JS gz | 244,539 (`index-Dv_LXwyI.js`) | 244,539 (`index-Dv_LXwyI.js`) | 0.0% — identical file |
| Main CSS gz | 31,208 (`index-D8GMxP0j.css`) | 31,208 (`index-D8GMxP0j.css`) | 0.0% — identical file |
| Homepage HTML | 6,563 raw | 6,563 raw | 0% |

**Verdict:** the four >25% flags track their category article counts almost 1:1 (article counts from the Nov 2 commit `b1bfe24e` vs today's local category files), so per-article payload is flat — this is story volume, not an un-minified/duplicated asset or a feed-format regression, and nothing was auto-fixed. Nothing is over ~500 KB gzipped (largest is the JS bundle at 244,539). Watch item for next week: if category counts stay at this level, the category files are now structurally ~30–38 KB gz and the homepage feed ~99 KB; a per-category cap or trim would be a design call for Kiran, not an audit auto-fix.

## Travel gallery coverage — no change: dead keys 0, uncovered 18 (all legacy)

Simulation of the page's exact first-match rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 0** — unchanged, no new dead key.
- **Uncovered experiences (b): 18 — identical legacy baseline, nothing new:** bahamas: Thunderball Grotto, Exumas · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora (left empty on purpose in the Oct 24 fill — no verified photo of the Arpora market exists on Commons) · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge).
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (neither has a gallery entry at all; unchanged legacy baseline).

**Week-over-week:** dead keys 0 → 0, uncovered 18 → 18 (same list). Every remaining item is the known legacy baseline. Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/gallery_2026-11-09.json`). Nothing auto-fixed per instructions (key renames/reorders are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-11-09_raw.json`; extra visual/blocked/caption pass: `hidden_files/extra_2026-11-09.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-11-09.py` — word_count fixes (image fixes via `pipeline/image_sourcer.py --apply` on the 3 unblocked slugs)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (results: `hidden_files/gallery_2026-11-09.json`)
