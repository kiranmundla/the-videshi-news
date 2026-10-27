# Enrichment Audit — 2026-10-26

Weekly audit per Kiran's standing directive (2026-10-11), extended 2026-10-17 to include site speed and the travel-gallery coverage check.

**Scope:** 112 unique articles on the homepage feed (generated 2026-10-26 13:32 UTC). All 112 found in `p2_articles`. Zero articles with zero sources; zero with only one source — the ≥2-source gate is holding for the second straight week.

## ⚠️ Critical finding 1 — a visual story with no hero image

`diwali-home-decor-guide-candles-tableware-statement-pieces` (lifestyle-health, 780 words) is flagged `is_visual_story = true` in the DB and has **no hero image**. This is the exact red line the audit exists to catch ("a visual story with no image"). It carries `image_backfill_blocked = true`, so the sourcer was not forced on it in this run — the block needs a human look: either unblock it so a verified decor photo can be sourced, or clear the visual-story flag if the guide is meant to run text-only. **This one needs Kiran's call.**

## ⚠️ Critical finding 2 — NEW dead travel-gallery key (see step 6 below)

Bali `Monkey Forest` became a dead key this week — it was live on 2026-10-19. Cause is identified and mechanical (Oct 24 re-key preempts it under the page's first-match rule). Details in the travel section.

## Hero-image coverage — improving, still high

**21 of 112 homepage articles (18.8%) had no hero at audit start, vs 25 of 108 (23%) on 2026-10-19.** After this run's sourcer fix (below), 20 of 112 (17.9%).

Of the 21: 15 carry `image_backfill_blocked = true` (deliberate stay-imageless per the wrong-photo bar); the 6 unblocked were run through `image_sourcer.py --apply` — 1 image landed (`zetwerk-ipo-listing-5-percent-premium-peak-xv-30th`, Moneycontrol og:image, DB-verified), 5 found no verified candidate (`418-review-roundup-critics`, `ed-raids-13-sites-nri-housing-loan-fraud-probe`, `india-a-pakistan-a-november-22-asia-cup-rising-stars-2026`, `kairav-mittal-17-project-root-yoga-crewe-virginia`, `the-host-umhlanga-durban-indian-restaurant-vivek-moodley`) — correct behaviour, not a sourcer failure.

The 21: `418-review-roundup-critics`, `abijit-ganguly-leaves-mumbai-bengaluru`, `amritsar-man-shot-dead-scooter-parking-argument-anand-avenue`, `canva-craft-first-in-house-image-model`, `cheeni-durham-named-north-carolinas-best-indian-restaurant-tasting-table`, `chennai-deepavali-mathi-experience-store-women-self-help-groups`, `diwali-home-decor-guide-candles-tableware-statement-pieces` (⚠️ visual story, above), `ed-raids-13-sites-nri-housing-loan-fraud-probe`, `india-a-pakistan-a-november-22-asia-cup-rising-stars-2026`, `india-ai-proof-professions-goyal-commerce-ministry-global-lead`, `india-eu-fta-signing-december-modi-brussels`, `indian-american-voters-lean-democratic-trump-midterms-2026`, `kairav-mittal-17-project-root-yoga-crewe-virginia`, `kl-rahul-hit-wicket-duck-india-a-new-zealand-a-lincoln`, `kolkata-couple-rickshaw-pandal-reel-real-happiness-viral`, `krishnamoorthi-256-cosponsors-july-indian-american-heritage-month-resolution`, `november-2026-hindu-festival-calendar-diwali-chhath-dev-diwali-dates`, `the-host-umhlanga-durban-indian-restaurant-vivek-moodley`, `tilak-varma-51-india-beat-new-zealand-second-t20i-2-0`, `world-polio-day-india-vigilant-nadda-2026`, `zetwerk-ipo-listing-5-percent-premium-peak-xv-30th` (fixed this run).

## Health snapshot

| Check | 2026-10-19 | 2026-10-26 |
|---|---|---|
| Articles audited | 108 | 112 |
| Zero sources | 0 | 0 |
| One source (< 2 gate) | 0 | 0 |
| Utility external-link flags | 0 | 1 (see note — not a genuine utility breach) |
| No hero image | 25 (23%) | 21 → 20 after fix (17.9%) |
| Visual story with no image | 0 | **1 ⚠️** |
| Missing key_takeaways column | 1 → 0 after fix | 2 → 0 after fix |
| Missing data cards | 11 | 19 (3 by design, see below) |
| word_count NULL/0 | 2 → 0 after fix | 1 → 0 after fix |

Other measured gaps:

- **Utility-link note:** the single flag is `air-india-flight-returns-hyderabad-five-minutes-takeoff-109-safe` — category `travel`, but it is a breaking incident story (flight returned 5 minutes after takeoff, 109 safe), not a booking/guide article, so no booking/government link is owed. All 4 homepage immigration articles carry government links (uscis.gov ×2, justice.gov, dol.gov). No genuine utility breach this week.
- **Hero captions:** 41 of 91 articles with a hero (45%) have no `image_caption` — worse share than last week's 40% (33/83).
- **Inline richness:** 91 of 112 bodies have zero inline `<img>` beyond the hero; only 32 of 112 have any embed/social/gallery element (YouTube, X, Instagram, social_embeds, or gallery).
- **Social-native stories without embeds (2):** `kolkata-couple-rickshaw-pandal-reel-real-happiness-viral` (a viral-reel story with no reel embed, no data cards, and a blocked/missing hero — the weakest article on the homepage this week) and `indian-creator-swati-japan-viral-matcha-mont-blanc` (viral story, no social embed in body or `social_embeds`).
- **Word count:** only real stored-value flag was `418-review-roundup-critics` (NULL, body measures 697 — fixed). The other two sub-400s are trailer briefs by design: `dead-end-job-trailer-out` (87) and `kauriburir-mandir-teaser-out-jeetu-kamal-paoli-dam` (53), both with film-info in body; plus the `happening-2026-10-26-verizon-communications-earnings` brief (215) by design.
- **Review bar:** both homepage reviews name publications with scores and specific material — `tu-hai-meri-kiran-review-sonakshi-sinha-zaheer-iqbal` (Bollywood Hungama 2.5/5, India Forums 2/5, Filmfare unrated; first-half vs post-interval split, the unexplained phone rules, runtime/certificate card) and `418-review-roundup-critics` (3/5 consensus across 15 reviews, India Today / The Hindu / Gulte / Cinema Express / Great Andhra named, Chaitra Achar's performance, sound design, weak climax). Individual critic *names* are still absent — publications only, same as last week.

**Data-card adoption (112 articles):** stat_grid 79, comparison 47, timeline 24, key_dates 10, highlights 9, price_compare 4, checklist 3, match_scorecard 3, movie_review_ratings 2, how_to 2, recipe 1 (first recipe adoption — `dry-roasted-poha-chivda-low-oil-diwali-recipe`). **Still zero adoption: critic_table.**

**No data cards (19):** 3 by design (the 2 trailer briefs + the Verizon earnings happening brief), plus 16 genuine enricher-fit candidates: `abijit-ganguly-leaves-mumbai-bengaluru`, `amrita-puri-no-regrets-break-bollywood-masters-edinburgh`, `amritsar-man-shot-dead-scooter-parking-argument-anand-avenue`, `class-12-student-found-severe-burns-delhi-school-dies`, `dhoni-ipl-2027-decision-before-december-csk-fitness`, `ed-raids-13-sites-nri-housing-loan-fraud-probe`, `indian-diaspora-holds-bharat-first-gathering-in-munich-backing-democratic-mandate`, `jaishankar-helpless-spectators-dialogue-diplomacy-un-day`, `jamia-promises-union-polls-revoke-suspensions-students-reject-offer`, `kolkata-couple-rickshaw-pandal-reel-real-happiness-viral`, `kumaraswamy-accuses-karnataka-cm-600-crore-plot-deve-gowda-family`, `over-500-dancers-diwali-disney-world-parade`, `pv-sindhu-bengaluru-home-mahabharata-chessboard`, `rohit-sharma-career-threatening-hip-injury-soham-desai`, `the-host-umhlanga-durban-indian-restaurant-vivek-moodley`, `vasant-bhatt-campus-reform-removal-claim`. Not auto-added: same reasoning as last week — several bodies are quote/politics-led with too few hard numbers for an honest stat_grid, and padding a card breaks the never-pad rule. The count rising 11 → 16 genuine is worth watching next week.

## Auto-fixes applied this run (all verified after patch)

1. **word_count backfilled (1):** `418-review-roundup-critics` NULL → 697 (pipeline convention: strip tags, unescape, split). The writer's NULL-word_count bug is still not fixed at source — third week running it has produced homepage cases (2 last week, 1 this week).
2. **key_takeaways column backfilled (2):** `dead-end-job-trailer-out` (3 items) and `kauriburir-mandir-teaser-out-jeetu-kamal-paoli-dam` (2 items) — both bodies already rendered the takeaways div; the column was empty. Extracted verbatim from the body. Same writer column-sync bug as previous weeks.
3. **Image sourcer run on all 6 unblocked imageless articles:** 1 applied — `zetwerk-ipo-listing-5-percent-premium-peak-xv-30th` (Moneycontrol og:image, confirmed in DB). The other 5 found no verified candidate (correct per the wrong-photo bar). The 15 blocked articles were not forced — including the visual-story case above, which needs Kiran's call rather than a forced source.

## Performance watch — NO regression

Measured live over the wire today (`curl`, `Accept-Encoding: gzip`, bytes downloaded):

| Payload | Oct 19 live | Oct 26 live | WoW |
|---|---|---|---|
| `data/homepage-feed.json` gz | 89,954 | 97,282 | +8.1% |
| `data/category/news.json` gz | 42,901 | 48,749 | +13.6% |
| `data/category/entertainment.json` gz | 27,787 | 20,937 | −24.7% |
| `data/category/sports.json` gz | 28,378 | 27,405 | −3.4% |
| `data/category/markets-finance.json` gz | 29,327 | 36,186 | +23.4% — watch, under the 25% flag line |
| `data/category/immigration.json` gz | 29,147 | 24,006 | −17.6% |
| `data/category/travel.json` gz | 17,286 | 13,730 | −20.6% |
| Main JS gz | 244,393 (`index-DE4dLYcE.js`) | 244,562 (`index-BW3d401e.js`) | +0.1% — flat |
| Main CSS gz | 31,204 (`index-DYX09FXp.css`) | 31,204 (same file) | 0% |
| Homepage HTML | 6,563 raw | 6,563 raw | 0% |

No payload grew >25% WoW; nothing is over ~500 KB gzipped (largest is the JS bundle at 244 KB). `markets-finance.json` at +23.4% is the only payload approaching the flag line — it carries more/longer market stories this week, not an asset change; recheck next week.

## Travel gallery coverage — 1 NEW dead key; big legacy improvement from the Oct 24 fill

Simulation of the page's exact first-match rule over all 50 guides and `travel-galleries.json`:

- **Dead keys (a): 1 — bali: `Monkey Forest` ⚠️ NEW.** On 2026-10-19 this key was live: the guide paragraph is "Ubud Rice Terraces & Monkey Forest", and with the old key set (`Tegallalang Rice Terraces` first, which matches nothing in that paragraph) `Monkey Forest` was the first matching key and rendered. The Oct 24 part-2 commit (d7be9a9f0) re-keyed `Tegallalang Rice Terraces` → `Ubud Rice Terraces`, which sits earlier in JSON order and now wins that paragraph under the first-match rule — so the `Monkey Forest` photo set (key order in bali: `Ubud Rice Terraces`, `Uluwatu Temple`, `Monkey Forest`, `Mount Batur`, `Seminyak Beach Clubs`, `Tirta Empul`) can never render. The Oct 24 commit verified containment ("all 277 keys match a guide experience"), not first-match — that's the gap. Mechanical fix options (not auto-applied, ordering-sensitive per instructions): move `Monkey Forest` before `Ubud Rice Terraces` in the bali `experiences` object (the paragraph would then show the Monkey Forest strip instead of the terraces strip), or accept one strip for the combined paragraph and delete the `Monkey Forest` set. Guide wording, exact: **"2. Ubud Rice Terraces & Monkey Forest"** (one combined experience).
- **Uncovered experiences (b): 18** — bahamas: Thunderball Grotto, Exumas · cabo: Snorkeling at Chileno Bay · dominican-republic: Indigenous Eyes Ecological Park · florida: all 7 (Walt Disney World, Orlando; Kennedy Space Center, Cape Canaveral; The Florida Keys & Key West; Everglades Airboat Tour; Miami Beach & South Beach; Clearwater Beach & Gulf Coast; BAPS Shri Swaminarayan Mandir, Bartow) · goa: Saturday Night Market, Arpora (left empty on purpose in the Oct 24 fill — no verified photo of the Arpora market exists on Commons) · new-york-city: all 7 (Jackson Heights Food Crawl, Queens; Statue of Liberty & Ellis Island; Central Park; The Metropolitan Museum of Art; Broadway Show; Brooklyn Bridge Walk & DUMBO; Top of the Rock or The Edge).
- **No `experiences` block at all (c): 2** — `florida`, `new-york-city` (unchanged legacy baseline).

**Week-over-week:** dead keys 11 → 1, uncovered 29 → 18, thanks to the Oct 24 "Travel galleries part 2" fill (11 experiences filled, 10 orphan sets deleted, Tegallalang re-keyed). Every remaining uncovered/dead item except the new Bali `Monkey Forest` key is the known legacy baseline. Exact guide wording for any future mechanical fix is in the checker output (`hidden_files/gallery_2026-10-26.json`). Not auto-fixed per instructions (key renames/reorders are ordering-sensitive).

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the article audit (raw results: `hidden_files/audit_2026-10-26_raw.json`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_fix_2026-10-26.py` — word_count / takeaways fixes (image fix via `pipeline/image_sourcer.py --slug zetwerk-ipo-listing-5-percent-premium-peak-xv-30th --apply`)
- `~/workspace/goals/article-content-quality-improvements/hidden_files/travel_gallery_check.py` — the gallery simulation (results: `hidden_files/gallery_2026-10-26.json`)
