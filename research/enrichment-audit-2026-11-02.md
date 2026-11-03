# Enrichment Audit — 2026-11-02

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 94 unique articles on the homepage feed. Live feed generated 2026-11-02 13:17 UTC; the local feed file (generated 16:13 UTC) carries the identical 94-slug set. All 94 found in `p2_articles`. Zero articles with zero sources; zero with only one source — the ≥2-source gate is holding for the third straight week.

**No critical trigger this week:** no zero-source article, no visual story without an image (last week's Diwali decor case is resolved / off the feed), no utility external-link breach, no performance regression, and no new dead travel-gallery key. Two trends are worth watching (hero coverage, below, and the writer word_count bug, fourth week running).

## Hero-image coverage — share rose, driven by blocked articles

**27 of 94 homepage articles (28.7%) had no hero at audit start, vs 20 of 112 (17.9%) on 2026-10-26. After this run's sourcer fixes, 24 of 94 (25.5%).**

Of the 27: 21 carry `image_backfill_blocked = true` (deliberate stay-imageless per the wrong-photo bar — the rise is mostly more blocked articles landing on the homepage, not sourcer failures). The 6 unblocked were run through `image_sourcer.py --apply` — 3 images landed and were DB-verified:

- `fed-logan-musalem-more-rate-hikes-needed-soon-december` — CNBC og:image (Musalem), DB-confirmed
- `jai-moondra-six-wickets-ireland-namibia-fourth-odi-record` — BBC og:image, DB-confirmed
- `kla-ai-demand-chip-equipment-2027-semiconductor-growth` — Benzinga semiconductor photo, DB-confirmed

3 found no verified candidate (correct behaviour, not a sourcer failure): `exxonmobil-earnings-q3-2026-refining-profit-15-4-billion`, `prasidh-krishna-ruled-out-new-zealand-odi-series-siraj-india-a` (named-person guard — staying imageless), `preston-silk-route-restaurant-licence-immigration-raid` (named-person guard).

The 21 blocked: `amitabh-bachchan-bulletproof-shield-jalsa-bomb-threat`, `australia-visa-biometrics-india-five-checks-booking-october-2026`, `beyond-marigold-seven-flowers-diwali-home-decor`, `canada-ircc-international-students-work-study-permit-conditions`, `dc-mayors-office-diwali-celebration-november-6-moapia`, `gambhir-india-ruthlessness-t20i-series-win-new-zealand`, `harmanpreet-hat-trick-india-beat-malaysia-4-2-asian-champions-trophy`, `how-india-celebrates-diwali-five-days-regions`, `infosys-opens-1-1-million-sq-ft-block-pocharam-hyderabad`, `jurel-unbeaten-99-padikkal-80-india-a-new-zealand-a-day-1`, `manisha-bhanwala-gold-india-best-womens-wrestling-worlds`, `polio-threat-persists-india-virus-free-experts-warn`, `pradeep-khullar-bhaturewala-chole-bhature-dubai`, `priyanka-chopra-nick-jonas-diwali-party-los-angeles`, `ravindra-chapman-ruled-out-new-zealand-odi-series-india`, `sridhar-vembu-zoho-shut-down-business-schools-india`, `st-lng-indian-american-8-2-billion-texas-deepwater-port-approval`, `supreme-court-clears-tax-probe-former-cji-sabharwal-sons`, `syhiba-wakefield-authentic-punjabi-indian-restaurant`, `tennessee-daca-drivers-license-law-lawsuit-hb6001`, `triangle-restaurants-yelp-top-100-indian-restaurants-lime-lemon`.

## Health snapshot

| Check | 2026-10-26 | 2026-11-02 |
|---|---|---|
| Articles audited | 112 | 94 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 0 | 0 |
| Utility external-link flags | 1 (not genuine) | 0 |
| No hero image | 21 → 20 after fix (17.9%) | 27 → 24 after fix (25.5%) |
| Visual story with no image | **1 ⚠️** | 0 |
| Missing key_takeaways column | 2 → 0 after fix | 1 → 0 after fix |
| Missing data cards | 19 (3 by design) | 8 (2 by design) |
| word_count NULL/0 | 1 → 0 after fix | 1 → 0 after fix |

Other measured gaps:

- **Hero captions improved sharply:** 15 of 67 articles with a hero (22%) have no `image_caption`, vs 45% (41/91) on 2026-10-26.
- **Inline richness:** 64 of 94 bodies have zero inline `<img>` beyond the hero; 39 of 94 (41%) have any embed/social/gallery element (YouTube, X, Instagram, social_embeds, or gallery) — up from 32 of 112 (29%).
- **Social-native stories:** only one homepage headline is social-native this week — `bhavitha-mandava-instagram-rings-award-chanel-hyderabad` (an Instagram story) carries an X embed but no Instagram embed and an empty `social_embeds`. Not flagged critical (it does carry an embed), but the platform-native embed is still missing.
- **Utility links:** no breaches. Immigration/travel/government links present where owed: `australia-visa-biometrics-india-five-checks-booking-october-2026` (immi.homeaffairs.gov.au, india.highcommission.gov.au), `bengaluru-mumbai-vande-bharat-sleeper-bookings-open-november-3` (irctc.co.in), `upi-bookings-burj-khalifa-resorts-world-sentosa` (ticket.atthetop.ae, RWS Sentosa), `h1b-worker-ohio-child-pornography-charges-kumar` (justice.gov), `us-appeals-court-denies-bond-hearings-detained-migrants` (ca5.uscourts.gov, justice.gov), `preston-silk-route-restaurant-licence-immigration-raid` (gov.uk). Soft note (not a breach — both have external links): `canada-ircc-international-students-work-study-permit-conditions` links only 7globe.in / immigration.ca and `canada-extends-work-permit-measures-haitians-sudanese-2027` links cicnews.com / youtube.com — neither links canada.ca, where a government link would be stronger.
- **Word count:** the only stored-value flag was `udta-teer-review-roundup-critics` (NULL, body measures 691 — fixed, see below). Genuine sub-400: `gujarat-diwali-parole-143-prisoners-november-6` (stored 310, body measures 365 — a thin breaking story). By design: `dune-movie-filmedforimax-trailer-out` (109, trailer brief with YouTube embed + Film information card in body) and `happening-2026-11-02-apple-earnings` (207, happening brief).
- **Review bar — split result.** `ramayana-part-1-review-critics-praise-spectacle-split-story` (889 words) **exceeds the bar**: five named critics with scores (Taran Adarsh / Bollywood Hungama 5/5, Christian Zilko / IndieWire B, Brandon Zachary / Screen Rant 7/10, Giovanni Lago / Next Best Picture 5/10, Siddhant Adlakha / IGN 4/10), specific scenes (the Brahma–Ravana opening, the Sita Swayamvar, the pre-interval stretch), and the pipeline's **first-ever `critic_table`** card. The audit script's `review_thin_scenes:4` flag on it is a regex false positive — verified by reading the body. `udta-teer-review-roundup-critics` is thinner: publications only (Times of India, Outlook India, Hindustan Times, Filmfare, Bollywood Hungama), no individual critic names, general performance/pacing material.

**Data-card adoption (94 articles):** stat_grid 69, comparison 44, timeline 23, highlights 13, key_dates 9, match_scorecard 5, checklist 3, how_to 3, critic_table 1 (first adoption), movie_review_ratings 1. **Zero this week: price_compare, recipe** (homepage composition — both appeared in earlier weeks).

**No data cards (8):** 2 by design (the Dune trailer brief + the Apple earnings happening brief), plus 6 genuine enricher-fit candidates: `ar-rahman-brooke-bond-taj-mahal-tea-awaken-your-masterpiece` (470w), `dc-mayors-office-diwali-celebration-november-6-moapia` (470w, also blocked/no-hero), `diwali-gift-guide-2026-craft-textiles-food-beyond-mithai` (609w), `five-fresh-diwali-design-ideas-tablescapes-cosy-corners` (763w), `sridhar-vembu-zoho-shut-down-business-schools-india` (533w, also blocked/no-hero), `us-appeals-court-denies-bond-hearings-detained-migrants` (797w). Not auto-added — same never-pad reasoning as previous weeks; the genuine count falling 16 → 6 is an improvement.

## Auto-fixes applied this run (all verified after patch)

1. **word_count backfilled (1):** `udta-teer-review-roundup-critics` NULL → 691 (pipeline convention: strip tags, unescape, split). The writer's NULL-word_count bug is still not fixed at source — fourth week running it has produced a homepage case (2, 1, 1, 1 across the last four audits).
2. **key_takeaways column backfilled (1):** `dune-movie-filmedforimax-trailer-out` (3 items) — the body already rendered the takeaways div; the column was empty. Extracted verbatim from the body. Same writer column-sync bug as previous weeks.
3. **Image sourcer run on all 6 unblocked imageless articles:** 3 applied and DB-verified (`fed-logan-musalem-more-rate-hikes-needed-soon-december`, `jai-moondra-six-wickets-ireland-namibia-fourth-odi-record`, `kla-ai-demand-chip-equipment-2027-semiconductor-growth`). The other 3 found no verified candidate (correct per the wrong-photo bar). The 21 blocked articles were not forced.

## Performance watch — NO regression

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded):

| Payload | Oct 26 live | Nov 2 live | WoW |
|---|---|---|---|
| `data/homepage-feed.json` gz | 97,282 | 81,603 | −16.1% |
| `data/category/news.json` gz | 48,749 | 24,370 | −50.0% |
| `data/category/entertainment.json` gz | 20,937 | 23,622 | +12.8% |
| `data/category/sports.json` gz | 27,405 | 21,438 | −21.8% |
| `data/category/markets-finance.json` gz | 36,186 | 28,951 | −20.0% — last week's watch item cleared |
| `data/category/immigration.json` gz | 24,006 | 19,725 | −17.8% |
| `data/category/travel.json` gz | 13,730 | 14,331 | +4.4% |
| `data/category/technology.json` gz | — | 26,786 | new baseline |
| `data/category/food.json` gz | — | 16,395 | new baseline |
| Main JS gz | 244,562 (`index-BW3d401e.js`) | 244,539 (`index-Dv_LXwyI.js`) | −0.0% — flat |
| Main CSS gz | 31,204 (`index-DYX09FXp.css`) | 31,208 (`index-D8GMxP0j.css`) | +0.0% — flat |
| Homepage HTML | 6,563 raw | 6,563 raw | 0% |

No payload grew >25% WoW; nothing is over ~500 KB gzipped (largest is the JS bundle at 244 KB). All category payloads remain far above the 2026-10-17 ~21 KB baseline mainly on story volume, but every one except entertainment (+12.8%) and travel (+4.4%) shrank this week.

## Travel gallery coverage — dead keys 1 → 0; no new issues

Simulation of the page's exact first-match rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 0.** Last week's NEW dead key is fixed: the Bali guide was split (commit `eaf534385`, "travel: split Bali guide item 2 so Monkey Forest gallery key matches") — the old combined paragraph "2. Ubud Rice Terraces & Monkey Forest" is now two experiences, "2. Ubud Rice Terraces" and "3. Monkey Forest", so the `Monkey Forest` key (order in bali: `Ubud Rice Terraces`, `Uluwatu Temple`, `Monkey Forest`, `Mount Batur`, `Seminyak Beach Clubs`, `Tirta Empul`) matches its own paragraph and renders.
- **Uncovered experiences (b): 18 — identical legacy baseline, nothing new:** bahamas: Thunderball Grotto, Exumas · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora (left empty on purpose in the Oct 24 fill — no verified photo of the Arpora market exists on Commons) · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge).
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (neither has a gallery entry at all; unchanged legacy baseline).

**Week-over-week:** dead keys 1 → 0, uncovered 18 → 18 (same list). Every remaining item is the known legacy baseline. Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/gallery_2026-11-02.json`). Nothing auto-fixed per instructions (key renames/reorders are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-11-02_raw.json`; extra visual/blocked/caption pass: `hidden_files/extra_2026-11-02.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-11-02.py` — word_count / takeaways fixes (image fixes via `pipeline/image_sourcer.py --apply` on the 6 unblocked slugs)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (results: `hidden_files/gallery_2026-11-02.json`)
