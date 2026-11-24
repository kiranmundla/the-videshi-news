# Enrichment Audit — 2026-11-23

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 68 unique articles on the homepage feed (down from 97 on 2026-11-16). Live feed generated 2026-11-23 15:24 UTC; the live slug set and the local feed file are identical (68/68). All 68 found in `p2_articles`. Zero articles with zero sources; zero with only one source — the ≥2-source gate holds for the sixth straight week. All 68 homepage articles were published 2026-11-20 to 2026-11-23, so every finding below describes current production, not legacy stock.

**Reportable items this week (details below):**
1. **Data cards collapsed: 32 of 68 articles (47.1%) have zero data cards, vs 6 of 97 (6.2%) on 2026-11-16 — and the card vocabulary shrank to 4 types.** Last week: stat_grid 59, comparison 33, timeline 15, highlights 6, checklist 3, recipe 1. This week all six are at **zero**; the only cards in use are `price_compare` 46, `key_dates` 8, `match_scorecard` 2, `movie_review_ratings` 1. Something in the writer/enricher changed in the Nov 20–23 window: articles either get a `price_compare` table or nothing. This is the week's critical gap — a pipeline investigation, not a per-article fix (the 32 no-card slugs are listed below).
2. **`price_compare` misuse worsened: 27 of 68 articles carry 46 `price_compare` cards (last week 23 articles / 34 cards), and every sampled card is still a generic Item/Value stat list, not a price comparison** (Canada immigration targets, Hormuz tanker traffic, bullet-train construction progress, Wall Street index closes). Same writer-side defect named on 2026-11-16, unfixed at source.
3. **Embed/inline richness fell back: 12 of 68 articles (17.6%) carry any inline image, social embed, gallery or YouTube element, down from 30.9% (30/97) last week.** Only 5 articles have an inline `<img>` beyond the hero (last week 26). X embeds are still 0 (TwitterAPI.io depleted; top-up still Kiran's).
4. **Performance flags: 3 category payloads crossed the +25% line (entertainment +43.0%, sports +39.5%, markets-finance +42.7%; food +25.0% at the line) — all volume-driven.** Per-article gzipped bytes are flat (~620–690 across categories), the JS/CSS bundles are byte-identical to 2026-11-16 (same hashes), and the homepage feed itself shrank 33.0%. Explained below; not a code/asset regression, nothing auto-fixed.
5. **The sourcer overwrote a good caption again — new variant:** run on the week's one unblocked imageless article, it replaced the article's full writer caption with the two-word name "Taylor Swift". Restored in this run (below). The Nov 16 one-word-caption defect is the same fallback: the sourcer emits a bare entity name and clobbers an existing non-empty caption. Pipeline fix: never overwrite an existing caption; never emit a name-only caption.

No zero-source article, no visual story without an image (no article on this feed is flagged `is_visual_story` at all), no utility external-link breach, and no new dead travel-gallery key.

## Hero-image coverage — 29 no-hero at start, 28 of them deliberate blocks

**29 of 68 homepage articles (42.6%) had no hero at audit start, vs 43 of 97 (44.3%) on 2026-11-16. After this run's sourcer fix, 28 of 68 (41.2%); homepage with-hero density 58.8%.**

Of the 29: **28 carry `image_backfill_blocked = true`** (deliberate stay-imageless per the verified-or-nothing bar). Only 1 was unblocked — `dpiff-awards-2026-winners-dhurandhar-taylor-swift` — run through `image_sourcer.py --apply`: Gulte og:image landed (1600×1200, Taylor Swift / James Cameron), DB-confirmed. Its caption had to be restored after the sourcer overwrote it (item 5 above).

The 28 blocked: `cert-in-ai-assisted-cyberattacks-unauthorized-payments-indian-banks`, `delhi-high-court-fresh-notice-amrit-wilson-oci-cancellation`, `fssai-bisleri-prosecution-unsafe-water-sample-bromate`, `fssai-suspends-licences-five-nutraceutical-makers-safety`, `google-iit-kharagpur-5-million-ai-research-funding`, `google-willow-quantum-contextuality-magic-square-science`, `hyderabad-popvax-rna-foundry-personalised-cancer-vaccine`, `ice-custody-raghul-anandakrishnan-texas-photo-case`, `india-720-wellington-highest-test-total-new-zealand`, `india-ai-funding-1-6-billion-mumbai-bengaluru-tracxn`, `india-blind-cricket-boycott-asia-cup-final-pakistan-dhaka`, `kl-rahul-sena-century-sweep-wellington-hundred`, `manipur-spurious-liquor-death-toll-rises-17`, `modi-dedicates-nitish-setu-ganga-bridge-bihar`, `modi-three-state-tour-bihar-projects-34470-crore`, `nps-kyc-nri-seafarers-employment-contract-cdc-pfrda`, `pune-swasti-patil-first-indian-gold-egoi-informatics`, `ramayana-part-1-kerala-box-office-64-crore-17-days`, `rishabh-pant-first-asian-wicketkeeper-sena-centuries`, `salman-khan-apologises-shraddha-kapoor-maatrubhumi-eetha-clash`, `saudi-qvp-disruptions-work-visa-processing-delays`, `senate-bill-perm-premium-processing-dol-plan`, `sensex-falls-1100-points-profit-booking-november-23-2026`, `surrey-walmart-shooting-victims-identified-rehal-kaur`, `texas-state-employee-daca-renewal-stalls-job-december`, `us-perm-overhaul-proposal-90-day-recruitment-eb2-eb3`, `vinita-somani-jaipur-cancer-survivor-trained-200-women-cooking`, `wall-street-ai-selloff-sp500-dow-correction-nasdaq`.

**Captions:** among the 39 articles that had a hero at audit start, **0 were missing `image_caption` and 0 were one-word** — the Nov 16 one-word problem did not recur in writer-produced captions; it lives only in the sourcer's own writes (item 5).

**Sourcer environment note:** `cv2 4.10.0` with `CascadeClassifier` verified present — no reinstall needed, second straight week.

## Health snapshot

| Check | 2026-11-16 | 2026-11-23 |
|---|---|---|
| Articles audited | 97 | 68 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 0 | 0 |
| Utility external-link flags | 0 | 0 |
| No hero image | 43 → 39 after fix (40.2%; 37 of 43 blocked by design) | 29 → 28 after fix (41.2%; 28 of 29 blocked by design) |
| Visual story with no image | 0 | 0 (0 visual stories on the feed) |
| Missing key_takeaways column | 1 → 0 after fix | 1 → 0 after fix |
| Missing data cards | 6 (1 by design) | **32 (1 by design)** |
| word_count NULL/0 | 2 → 0 after fix | 1 → 0 after fix |
| Articles with any embed/social/gallery/YouTube element | 30 of 97 (30.9%) | **12 of 68 (17.6%)** |

Other measured gaps:

- **Data-card collapse (item 1) — the 32 no-card articles:** 1 by design (`daayra-kareena-kapoor-prithviraj-meghna-gulzar-trailer-out`, trailer brief — its Film information card is body HTML), plus 31 genuine: `air-india-crash-investigation-final-stage-supreme-court` (580w), `anthropic-co-founder-tom-brown-trump-accounts-gift` (559w), `anthropic-mathematician-claude-riemann-hypothesis-proof-claim` (802w), `ar-rahman-ramayana-three-years-turned-down-films-iffi` (605w), `caa-bryan-lourd-no-fakes-act-deepfakes-congress` (731w), `cert-in-ai-assisted-cyberattacks-unauthorized-payments-indian-banks` (672w, also hero-blocked), `deported-brooklyn-man-partition-sale-shared-home-nelson-ruling` (653w), `diljit-dosanjh-ahmedabad-stadium-double-standards-coldplay` (504w), `edmonton-sneha-joy-wins-5-million-lotto-649` (352w), `fssai-bisleri-prosecution-unsafe-water-sample-bromate` (628w, hero-blocked), `fssai-suspends-licences-five-nutraceutical-makers-safety` (566w, hero-blocked), `gargi-agrawalla-sivogo-ai-alarm-deaf-dyson-award` (623w), `google-iit-kharagpur-5-million-ai-research-funding` (468w, hero-blocked), `google-willow-quantum-contextuality-magic-square-science` (695w, hero-blocked), `hyderabad-popvax-rna-foundry-personalised-cancer-vaccine` (622w, hero-blocked), `ice-custody-raghul-anandakrishnan-texas-photo-case` (640w, hero-blocked), `india-blind-cricket-boycott-asia-cup-final-pakistan-dhaka` (750w, hero-blocked), `kl-rahul-sena-century-sweep-wellington-hundred` (759w, hero-blocked), `krish-ashok-masala-body-food-myths` (661w), `manipur-chandel-spurious-liquor-11-dead-181-hospitalised` (628w), `manipur-spurious-liquor-death-toll-rises-17` (515w, hero-blocked), `modi-canada-visit-december-nadjibulla-reset-ties` (754w), `modi-three-state-tour-bihar-projects-34470-crore` (618w, hero-blocked), `navdeep-bains-elected-ontario-liberal-leader` (832w), `nps-kyc-nri-seafarers-employment-contract-cdc-pfrda` (615w, hero-blocked), `persistent-employee-immigration-data-us-law-firm-cyber-incident` (544w), `rishabh-pant-first-asian-wicketkeeper-sena-centuries` (591w, hero-blocked), `salman-khan-apologises-shraddha-kapoor-maatrubhumi-eetha-clash` (575w, hero-blocked), `saudi-qvp-disruptions-work-visa-processing-delays` (604w, hero-blocked), `texas-state-employee-daca-renewal-stalls-job-december` (699w, hero-blocked), `trump-look-at-india-fed-interest-rates-growth` (733w). Not auto-added — never-pad reasoning as previous weeks, and at this scale the fix belongs in the writer/enricher, not in 31 hand edits.
- **price_compare misuse (item 2):** 27 articles carry `price_compare` (46 cards): `adani-energy-west-bengal-1750-mw-renewable-power-award`, `airbnb-raichand-house-k3g-mumbai-experience-december`, `anthropic-ipo-record-81-billion-nasdaq-debut` (×2), `ayodhya-janakpur-express-modi-balen-shah-flag-off-november-23`, `canada-extends-student-arrivals-target-2029-levels-plan` (×3), `congress-sp-up-seat-sharing-talks-open-delhi` (×2), `dpiff-awards-2026-winners-dhurandhar-taylor-swift` (×2), `hormuz-tanker-hit-khasab-traffic-65-percent-below-pre-war` (×3), `ice-arrests-sea-tac-jetway-flight-1306` (×2), `india-720-wellington-highest-test-total-new-zealand` (×2), `india-ai-funding-1-6-billion-mumbai-bengaluru-tracxn` (×2), `india-crosses-1-crore-hpv-vaccine-doses-nine-months` (×2), `india-first-bullet-train-last-quarter-2027-surat-vapi` (×2), `microsoft-brad-smith-defends-overseas-data-centres-trump-threat`, `modi-dedicates-nitish-setu-ganga-bridge-bihar` (×2), `modi-iit-kharagpur-platinum-jubilee-break-limits-coin`, `openai-pachocki-common-ai-limits-perplexity-proposal`, `pune-swasti-patil-first-indian-gold-egoi-informatics` (×2), `ramayana-day-18-box-office-1693-crore-passes-dhurandhar-2-us` (×2), `ramayana-part-1-kerala-box-office-64-crore-17-days` (×2), `senate-bill-perm-premium-processing-dol-plan`, `sensex-falls-1100-points-profit-booking-november-23-2026` (×2), `surrey-walmart-shooting-victims-identified-rehal-kaur`, `trump-threatens-tax-us-firms-data-centers-abroad`, `vinita-somani-jaipur-cancer-survivor-trained-200-women-cooking`, `wall-street-ai-selloff-sp500-dow-correction-nasdaq` (×3), `yash-ramayana-kgf-2-five-language-50-crore-milestone`. Items 1 and 2 are one defect seen from both sides: the writer's generic numbers table is its only card move, emitted as `price_compare`, and on roughly half of articles it now emits nothing at all. Fix belongs in the writer instructions / card-type gate (map Item/Value tables to `stat_grid`; restore stat_grid/comparison/timeline emission; reserve `price_compare` for actual price comparisons).
- **Embed mix:** X-bearing articles 0 (TwitterAPI.io depletion, unchanged cause). Instagram-bearing 4 (`diljit-dosanjh-ahmedabad-stadium-double-standards-coldplay`, `ice-custody-raghul-anandakrishnan-texas-photo-case`, `modi-dedicates-nitish-setu-ganga-bridge-bihar`, `navdeep-bains-elected-ontario-liberal-leader`). `social_embeds` column non-empty on 1 (`texas-state-employee-daca-renewal-stalls-job-december`). YouTube via `<youtube>` tag 5 (`aakasamlo-oka-tara-review-roundup-critics`, `daayra-kareena-kapoor-prithviraj-meghna-gulzar-trailer-out`, `ramayana-part-1-kerala-box-office-64-crore-17-days`, `texas-state-employee-daca-renewal-stalls-job-december`, `yash-ramayana-kgf-2-five-language-50-crore-milestone`) — the audit script's embed-tag regex does not count `<youtube>` tags, so the headline richness figure (17.6%) already includes them; on the script's strict basis it is 13.2%. Inline `<img>` beyond the hero: only 5 articles (`daayra…` ×2, `dpiff-awards…`, `ice-arrests-sea-tac…`, `navdeep-bains…`, `us-perm-overhaul…` — 5 articles, 6 images).
- **Social-native stories:** the audit script flagged **none** — no homepage headline matching instagram/viral/reel/youtube/tiktok/twitter lacks an embed. Clean.
- **Utility links:** zero flags. All 10 immigration and 1 travel homepage articles carry external links; the official-source links are present where it matters most (`uscis.gov` on the Texas DACA story, `federalregister.gov` on the PERM overhaul, `govinfo.gov` on the Senate PERM bill, `hrsd.gov.sa` on the Saudi QVP story). Soft notes only: `ice-arrests-sea-tac-jetway-flight-1306` links CNN/Fox/Reuters and no ICE/DHS page; `persistent-employee-immigration-data-us-law-firm-cyber-incident` links two news outlets and no official filing — not breaches of the zero-link rule.
- **Word count:** 1 stored NULL fixed (below). Genuine stored sub-400: `edmonton-sneha-joy-wins-5-million-lotto-649` (stored 352; body measures 401 with takeaways/pull-quotes included — a thin lotto story either way; not rewritten by the audit). By design: `daayra-kareena-kapoor-prithviraj-meghna-gulzar-trailer-out` (93 measured — trailer brief format).
- **Review bar (Nov 15 synthesized-voice standard):** the feed's one review, `aakasamlo-oka-tara-review-roundup-critics` (689 words after this run's backfill, published 2026-11-21), is **fully compliant** — zero outlet/critic names in prose (scanned: Times of India, Filmfare, NDTV, The Hindu, Gulte, Eenadu, 123telugu — none), judgments rendered directly, specific scenes/performances discussed (Dulquer Salmaan / Satvika Veeravalli performances, Sujith Sarang cinematography, G. V. Prakash Kumar score, second-half pacing), `movie_review_ratings` card present, YouTube embed present. Despite its legacy `-review-roundup-critics` slug, the content is the new single voice.
- **Homepage composition note:** no `lifestyle-health` article appears on this week's feed (categories: nri-world 12, technology 12, news 11, immigration 10, entertainment 9, sports 7, food 3, markets-finance 3, travel 1). Consistent with the Nov 14 policy letting the budget + hold rule starve the weakest category — flagged here only so the absence is on record, not as a defect.

**Data-card adoption (68 articles):** price_compare 46 (see misuse above), key_dates 8, match_scorecard 2, movie_review_ratings 1. **Zero this week: stat_grid, comparison, timeline, highlights, checklist, recipe, how_to, critic_table** (critic_table's absence remains expected under the synthesized-voice standard; the other seven were all in use last week — see item 1).

## Auto-fixes applied this run (all verified after patch)

1. **word_count backfilled (2):** `aakasamlo-oka-tara-review-roundup-critics` NULL → 689, `daayra-kareena-kapoor-prithviraj-meghna-gulzar-trailer-out` 75 → 93 (pipeline convention: strip tags, unescape, split; both DB-verified). The writer's NULL-word_count bug is still not fixed at source — seventh week running it has produced homepage cases.
2. **key_takeaways backfilled (1):** `daayra-kareena-kapoor-prithviraj-meghna-gulzar-trailer-out` column NULL → the 3 items already present in its body takeaways div (DB-verified).
3. **Image sourcer run on the 1 unblocked imageless article:** `dpiff-awards-2026-winners-dhurandhar-taylor-swift` landed a hero (Gulte og:image, 1600×1200) and was DB-verified. The 28 blocked articles were not forced.
4. **Caption restored (1):** the sourcer overwrote `dpiff-awards…`'s full writer caption ("Taylor Swift and James Cameron. Swift was named International Artist of the Year…") with the name-only "Taylor Swift"; the original caption was restored verbatim and DB-verified.
5. **Not auto-fixed (named for pipeline fixes):** the data-card collapse + `price_compare` default (items 1–2) and the sourcer's name-only caption overwrite (item 5) — all producer-side defects; per-article edits would recur next run.

## Performance watch — 3 payloads over the +25% flag line, all volume-driven

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded):

| Payload | Nov 16 live | Nov 23 live | WoW |
|---|---|---|---|
| `data/homepage-feed.json` gz | 88,229 | 59,111 | −33.0% (slugs 97 → 68) |
| `data/category/news.json` gz | 39,675 | 17,476 | −56.0% (articles 61 → 26) |
| `data/category/entertainment.json` gz | 21,717 | 31,050 | **+43.0% ⚠️** (50 articles; 621 B/article) |
| `data/category/sports.json` gz | 21,928 | 30,587 | **+39.5% ⚠️** (48 articles; 637 B/article) |
| `data/category/markets-finance.json` gz | 24,508 | 34,964 | **+42.7% ⚠️** (52 articles; 672 B/article) |
| `data/category/immigration.json` gz | 21,310 | 17,630 | −17.3% (26 articles) |
| `data/category/travel.json` gz | 22,114 | 8,523 | −61.5% (articles 31 → 11) |
| `data/category/technology.json` gz | 25,456 | 15,061 | −40.8% (25 articles) |
| `data/category/food.json` gz | 13,834 | 17,297 | +25.0% ⚠️ at the line (25 articles; 692 B/article) |
| `data/category/lifestyle-health.json` gz | 14,564 | 14,579 | +0.1% (19 articles) |
| `data/category/nri-world.json` gz | 31,161 | 20,758 | −33.4% (31 articles) |
| Main JS gz | 244,560 (`index-DWdQcfSU.js`) | 244,560 (`index-DWdQcfSU.js`) | 0.0% — identical hash and size |
| Main CSS gz | 31,359 (`index-NBv6aZlI.css`) | 31,359 (`index-NBv6aZlI.css`) | 0.0% — identical hash and size |
| Homepage HTML | 6,563 raw | 6,563 raw | 0% |

**Verdict:** the four flagged payloads grew because their category files carry more articles, not because articles got heavier — per-article gzipped bytes sit in a tight 621–692 band across every category, and the two categories with known last-week counts (news, travel) shrank in direct proportion to their article counts. The JS/CSS bundles are literally the same build as Nov 16. No un-minified or duplicated asset, no feed-format regression, nothing auto-fixed. Nothing is over ~500 KB gzipped (largest is the JS bundle at 244,560).

## Travel gallery coverage — no change: dead keys 0, uncovered 18 (all legacy)

Simulation of the page's exact first-match rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 0** — unchanged, no new dead key.
- **Uncovered experiences (b): 18 — identical legacy baseline, nothing new:** bahamas: Thunderball Grotto, Exumas · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora (left empty on purpose in the Oct 24 fill — no verified photo of the Arpora market exists on Commons) · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge).
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (neither has a gallery entry at all; unchanged legacy baseline).

**Week-over-week:** dead keys 0 → 0, uncovered 18 → 18 (same list). Every remaining item is the known legacy baseline. Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/gallery_2026-11-23.json`). Nothing auto-fixed per instructions (key renames/reorders are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-11-23_raw.json`; extra visual/blocked/caption pass: `hidden_files/extra_2026-11-23.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-11-23.py` — word_count + key_takeaways fixes (image fix via `pipeline/image_sourcer.py --apply` on the 1 unblocked slug; caption restore via direct PATCH, verified)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (results: `hidden_files/gallery_2026-11-23.json`)
