# Phase 2 Build Report — Local News Clusters (2026-10-13)

**Status: built, QA'd, committed + pushed, live-verified.**
Final numbers: **47 buckets · 194 items · 37/47 buckets non-empty · junk scans 0 hits · guard unit tests 51/51.**

Approved by Kiran 2026-10-13: "launch the ready buckets + Yonkers split, queue events ingestion for the rest."

---

## 1. New buckets (all data from research/data/clusters.json, Phase 1 conventions)

| Bucket | Rank | Members | Day-one headline items |
|---|---|---|---|
| St. Louis, MO | #40 | 40 | 6 |
| Milwaukee, WI | #50 | 30 | 2 |
| Cleveland, OH | #47 | 40 | 1 |
| Orlando, FL | #49 | 35 | 0 |
| Yonkers / Bergen, NY-NJ | #29 | 43 | 0 |

- Members: research-cluster places, ai-descending, cap 40 (Phase 1 convention), coords rounded to 4dp. St. Louis center = Maryland Heights (where the cluster's diaspora is — the Detroit precedent).
- Orlando and Yonkers/Bergen launched with **zero headline items** — the readiness research predicted exactly this (0 bucket-ready headlines in 30 days for net-new clusters); the buckets are carried by events + directory (Orlando 69 upcoming events / 198 listings; Yonkers/Bergen 121 events / 1,046 listings — the strongest readiness of any candidate). Empty buckets hide in the news rail until coverage lands, same as 8 Phase 1 buckets.
- Milwaukee's 2 items are both genuinely Milwaukee stories (JD Vance's H-1B fraud-probe event was held in Milwaukee; announcement + lawyers' pushback follow-up).
- Cleveland's 1 item is a Cleveland Clinic sleep-study story (matched via excerpt; the Clinic is the city's flagship institution — legitimate local news).
- St. Louis's 6: three Praggnanandhaa chess stories (Saint Louis Chess Club), a Missouri crash story, two British Airways India-route stories naming St. Louis.

## 2. The Yonkers / Bergen split

- New bucket `yonkers-bergen-ny-nj` ("Yonkers / Bergen, NY-NJ"): all 62 research cluster-#29 members (top 40 by population) **plus** the Bergen County towns the research had pooled into cluster #1, **plus** parent-named Palisades Park, Ridgefield, Leonia as editorial adds past the cap (Long Island precedent) = 43 members.
- Removed from `new-york-ny`: 12 Bergen County members (Hackensack, Rutherford, Fort Lee, Tenafly, Maywood, Wood-Ridge, Edgewater, Englewood, East Rutherford, Cliffside Park, Garfield, Lodi) and the "Hackensack" title alias.
- Overlap mechanism (verified in code): the builder title-matches on `aliases` only, so disjoint alias sets = no double-claiming. Guard tests assert Bergen/Yonkers headlines match the new bucket and do NOT match New York. Junk scan: **split leakage into New York = 0** (the Secaucus Diwali item in NYC is correct — Hudson County stays in the NYC bucket).
- Resolution check (frontend logic simulated on the built data): Fort Lee coords → Yonkers/Bergen at 0.0 mi (was NYC); Yonkers coords → Yonkers/Bergen at 1.9 mi; news falls back to the nearest non-empty bucket until the new bucket fills (designed behavior).

## 3. Guards (data-level, Phase 1 style)

- **Cleveland, OH** blocklist: `cleveland, mississippi|tennessee|georgia|texas|oklahoma`, `cleveland county`. "Avon" kept members-only (Avon Products is the bigger namesake).
- **St. Louis, MO** blocklist: `east st. louis` (a different city, Illinois side).
- **Orlando, FL** blocklist: `orlando bloom`, `orlando brown` (people, not the city).
- **Milwaukee, WI**: "Brookfield" is members-only, NOT a title alias (see §4). "Germantown" likewise members-only (MD/TN namesakes).
- Corpus check for the other new aliases (Westlake, Chesterfield, Winter Park, Paterson, Maitland, New Berlin): **0 published articles** mention them — no live traps; aliases kept so real town stories match.
- **Tests**: `pipeline/test_local_news_guards.py` is NEW — Phase 1's 33 guard tests were never committed as a file (the generator script was lost with a /tmp wipe in that session). The file now permanently covers the Phase 1 regression set (Costa Rica, Dublin mirror pair, Thomas Edison, Fishers occupation, Washington/Portland context, Orange County namesakes) + all Phase 2 cases + the split assertions: **51/51 pass**.

## 4. QA round 1 catch (fixed, rebuilt)

Build 1 put **5 items in Milwaukee, 3 of them junk**: "Brookfield" matched **Brookfield Asset Management** in excerpts (CDK Global is Brookfield-owned; the Nvidia $500B financing story lists Brookfield as a partner; a Wall Street India-bets story quotes Brookfield's deployment plans). Same class as Phase 1's Finn Allen/Donavan McKinney surname collisions. Fix at the data level (alias removed, member kept), 2 regression tests added, rebuilt: Milwaukee = the 2 real Milwaukee stories, junk scans 0.

Note: the first post-fix rebuild was lost when /tmp was wiped mid-run (log + scratch scripts vanished — the recurring VM overlay issue); the successful rebuild logged to the home disk. Final build: 194 items vs build 1's 198 (−3 Brookfield junk, −1 RSS churn).

## 5. Builder change

`build-local-news.py`: `STATE_NAMES` gained WI (Wisconsin) and MO (Missouri) so the thin-cluster state fallback works for the new buckets — same pattern as Phase 1's VA/MD/IN addition. No other builder logic changed; the frontend needed **zero changes** (picker loads `public/data/clusters.json` dynamically — verified in `useHubLocation.ts`/`YourHubPage.tsx`; no hand list remains).

TypeScript: `tsc -p tsconfig.app.json --noEmit` — 91 errors repo-wide, all pre-existing; 0 in the hub files; no frontend files touched.

## 6. Events ingestion queue (config only — no buckets launched)

Added to `pipeline/scrape-allevents.py` CITIES (a79070e5 Tri-Valley pattern) + documented in `pipeline/event-sources.md`. Every slug verified live against allevents.in before adding:

| Slug | City | Why |
|---|---|---|
| `fresno` | Fresno, CA | Fresno cluster: 0 upcoming events |
| `tracy` | Tracy, CA | Tracy bucket: 4 events (weakest live) — `tracy-ca` 404s, bare slug is CA |
| `eastvale` | Eastvale, CA | Inland Empire cluster: 8 events |
| `corona-ca` | Corona, CA | Inland Empire — bare `corona` is Corona, **NY** |
| `riverside` | Riverside, CA | Inland Empire (canonical slug) |
| `overland-park` | Overland Park, KS | Kansas City cluster: 8 events (pairs with existing `kansas-city`) |
| `germantown` | Germantown, MD | Germantown cluster: 7 events — allevents' canonical page is the Maryland one (verified via DMV event links, not Tennessee) |
| `leesburg-va` | Leesburg, VA | Loudoun County: 10 events (bare `leesburg` 404s) |
| `sterling` | Sterling, VA | Loudoun County (bare slug resolves to VA) |
| `chantilly-va` | Chantilly, VA | Loudoun County (bare `chantilly` 404s) |

Ashburn/Herndon/Fairfax (Loudoun) and Kansas City were already covered. Eventbrite/Sulekha scrapers take no explicit city lists, so allevents is the only config touched. A targeted `--dry-run --city fresno` validated the config end-to-end. **Executing job: `videshi-events-refresh`** (weekly sweep, Mondays 06:17 America/Los_Angeles) runs `scrape-allevents.py` over the full CITIES list — the queue executes automatically on the next run; no full sweep was run as part of this build.

## 7. Left imperfect (honest list)

- Orlando + Yonkers/Bergen headline buckets are empty at launch (events/directory carry them — see §1). They fill as the writer/RSS produce title-matching stories; the 4h enricher rebuild picks that up automatically.
- NYC's bucket still shows pre-existing V1 behavior (3 RSS variants of the Times Square garba story under the 0.55 near-dup threshold; a Toronto Moosewala story matched on an excerpt mention) — unchanged from Phase 1, not a Phase 2 regression; threshold changes remain Kiran's call.
- Cluster names remain working names (Kiran may rename).
