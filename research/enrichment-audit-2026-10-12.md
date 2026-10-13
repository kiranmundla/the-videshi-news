# Enrichment Audit — 2026-10-12

Weekly audit per Kiran's standing directive (2026-10-11): "constantly evolve this and make it foolproof, rich, useful and attractive enough and complete."

**Scope:** 115 unique articles on the homepage feed (generated 2026-10-12 06:50 PDT). All 115 found in `p2_articles`. Zero articles with zero sources. No visual-story-without-image.

## Health snapshot (after auto-fixes)

| Check | Before | After |
|---|---|---|
| Articles with < 2 sources | 12 (all exactly 1) | 12 — cannot fabricate, see below |
| Utility articles with no external links (rule #2) | 10 | 5 |
| Missing key_takeaways column | 8 | 0 |
| Missing data cards | 15 | 11 |
| Stale word_count = 0 | 9 (+1 NULL brief) | 0 |
| No hero image | 3 | 3 — all deliberately backfill-blocked, see below |
| Miscategorized (trade story in immigration) | 1 | 0 |

New-component adoption (real numbers — earlier draft undercounted because new components use `type`, not `card_type`): key_dates 7, match_scorecard 3, recipe 2, checklist 1, movie_review_ratings 1. **Zero adoption:** how_to, price_compare, critic_table.

## Auto-fixes applied this run

1. **External links added (4, editorial rule #2)** — all URLs verified via search today, anchored on existing body text, site link convention (`target="_blank" rel="noopener"`):
   - `air-india-student-discount-domestic-fares` → "airindia.com" now links to Air India's official student offer page (`airindia.com/in/en/book/exclusive-deals/student-flight-offer.html`)
   - `canada-fast-track-ontario-licensing-physicians` → "Practice Ready Ontario" now links to Touchstone Institute eligibility page
   - `canadian-colleges-indian-student-recruitment-pipeline-probe` → "Ontario's official career-college registry" now links to `ontario.ca/page/search-career-college-ontario`
   - `us-denaturalization-push-40-citizenship-largest-effort` → "USCIS form N-400" now links to `uscis.gov/n-400`
2. **Data cards added (4, obvious fits, facts from each article's own body):**
   - `sai-kung-indian-restaurant-diwali-fireworks-november-7` → key_dates (Diwali Oct 20, fireworks Nov 7)
   - `tahir-hussain-convicted-delhi-riots-dayalpur` → timeline (Feb 2020 riots → Apr 2020 arrest → Oct 10 2026 conviction → Nov 16 sentencing arguments)
   - `adani-green-h1-capacity-up-24-percent-20763-mw` → stat_grid (20,763 MW, 25,747 MU, 6,632 MWh storage, Rs 1,255.80)
   - `three-indians-rescued-black-sea-vessel-fly-home-romania` → timeline (Oct 5 attack → Oct 6 rescue → Oct 7 embassy visit → Oct 10 departure)
3. **word_count recomputed (10 rows)** — 9 rows had `word_count = 0` with full bodies (667–1,026 real words), 1 brief had NULL. Recomputed with the pipeline convention (strip tags, unescape, split).
4. **key_takeaways column backfilled (8 rows)** — bodies already rendered the takeaways div; the column was NULL. Extracted verbatim from the body.
5. **Category fix:** `montana-governor-lands-in-india-to-rescue-lentil-exports` was in `immigration`; moved to `markets-finance` (US-India trade/tariffs story).

## Remaining gaps (not auto-fixed — need a decision or research)

**A. Single-source regression (12 articles, all published Oct 8–12).** The mandatory ≥2 sources gate from the 2026-06-25 fix is not holding on the current writer path. Articles: `canada-fast-track-ontario-licensing-physicians`, `chennai-beaches-bioluminescence-kovalam-thiruvanmiyur`, `ganesh-dust-to-stardust-trailer-december-11`, `gulshan-devaiah-bollywood-violence-illusion`, `india-mobile-congress-2026-concludes`, `indian-founder-australia-bakery-shifts-seven-figure-revenue`, `lucknow-1949-heritage-home-slow-living`, `muslim-artisans-durga-hair-howrah-harmony`, `nepal-gorkha-flash-flood-budhi-gandaki`, `saina-nehwal-haryanvi-diet-aloo-paratha-ghee`, `south-sri-lanka-5-day-itinerary`, `us-fighter-jet-disables-cargo-vessel-iran-blockade`. Adding sources requires real research per article — not safe to automate without it. **Pipeline fix needed:** re-assert ≥2 sources at insert on the current writer path.

**B. Utility articles still linkless (5).** `hud-fha-loans-nonpermanent-residents-near-zero` (no official hud.gov Mortgagee Letter 2025-09 URL found in search — only third-party coverage; will not link a guess), `chennai-beaches-bioluminescence-kovalam-thiruvanmiyur`, `south-sri-lanka-5-day-itinerary`, `lucknow-1949-heritage-home-slow-living`, `indian-workers-sign-milan-consulate-settlement-payout-deals` (no clean official booking/government anchor exists in the copy). Recommend the enricher's link pass handle these with verified URLs.

**C. Imageless × 3 — reviewed, correctly blocked.** `saritha-komatireddy-challenges-letitia-james-ny-ag`, `telangana-woman-dies-missouri-crash-toddler`, `west-indies-plan-b-against-abhishek-sharma` all have `image_backfill_blocked = true` (no verified identity-safe photo / sensitivity). The sourcer already ran and conservatively blocked. Not re-runnable without new sourcing. None are visual stories.

**D. Review roundup thin on the critic bar.** `bethlehem-kudumba-unit-review-roundup-critics` names no critics and cites no specific scenes (it has the ratings card + 2 social embeds). It's a roundup, not a narrative review — but Kiran's 2026-10-09 bar wants named critics + specific scenes. Needs research, not automation.

**E. Data-card fits not taken (11).** `harshal-patel-ranji-gujarat-new-ball`, `hpv-vaccine-before-pregnancy-lower-preterm-birth-risk`, `mediterranean-mind-diets-linked-better-cognitive-performance`, `rajinikanth-autobiography-tamil-english-release-hint`, `russian-strikes-zaporizhzhia-11-killed-trump-diesel-deal`, `tiger-victim-posed-photos-witnesses-yorkshire-update`, `weta-cto-kimball-thurston-ai-tools-creatives` (+ 4 already fixed this run). Fits exist (stat_grid/timeline/checklist) but each needs judgment on which facts to lift — left for the enricher's card pass.

## Systemic bugs found (paired-work rule)

1. **Sources ≥2 assertion bypassed** — see A above. The 2026-06-25 fix's pre-insert assertion isn't firing on the current writer path. All 12 violations are from the last 5 days.
2. **word_count not computed on some inserts** — 9 recent rows got literal `0`, 1 brief got NULL. Legacy: 6,412 older rows have NULL word_count (pre-migration, untouched).
3. **key_takeaways column NULL on 7,558 rows** while bodies render the takeaways div — the writer populates the body but not the column. Backfilled the 8 homepage rows; the column-sync should be fixed at the writer.
4. **New components use `type`, old use `card_type`** — two schemas coexist in `data_cards`. Any audit/monitoring that reads only `card_type` undercounts adoption (this audit did, initially).
5. **image_backfill_blocked has no reason field** — the 3 blocked rows carry no record of *why* (identity unverifiable vs. sensitivity), so a future audit can't distinguish "correctly blocked" from "sourcer gave up."

## Scripts (reproducible)

- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_audit.py` — the audit
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_autofix.py` — word_count / takeaways / category fixes
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_linkfix.py` — the 4 link fixes
- `~/workspace/goals/article-content-quality-improvements/hidden_files/enrichment_cardfix.py` — the 4 card fixes
- Raw results: `/tmp/audit_2026-10-12_v2.json` (post-fix snapshot)
