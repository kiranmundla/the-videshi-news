# Phase 1 Build Report — Diaspora Suburb-Cluster Local News (2026-10-13)

**Status: built, QA'd, NOT committed/pushed.** All changes are in the working tree for parent review.
Final numbers: **42 buckets · 184 items · 34/42 buckets non-empty · junk scans 0 hits · guard unit tests 33/33.**

---

## 1. What was built

1. **Research data preserved** — `/tmp/diaspora/` copied to `research/data/` (`clusters.json`, `yield.json`, `readiness.json`, `mapping.json`) before anything else.
2. **One canonical cluster table** — `public/data/clusters.json` (147 KB, 42 clusters). The builder reads it; the frontend fetches the same file at `/data/clusters.json`. Both hand lists (builder `METROS`, frontend `METRO_PICKER`) are retired. Fields per cluster: `id, label, state, center{lat,lon}, anchor, query_cities[], aliases[], members[{name,state,lat,lon}], block[], context_guard, source_ranks[]`.
3. **Builder refactor** — `pipeline/build-local-news.py` now compiles its title-match patterns, RSS pooling, blocklists, and guards entirely from the table. Preserved exactly: EXCLUDE_RX, RSS keep/drop filters, title-match gate, near-dup dedup (Jaccard 0.55), PER_METRO=8, state fallback (wider window + state-level query), `--no-rss`, output format (`local-news.json` keyed by label under `"metros"`). STATE_NAMES gained VA/MD/IN.
4. **Frontend** — `useHubLocation.ts` drops `METRO_PICKER` for a cached `loadClusters()` + `getCachedClusters()` with a built-in 12-cluster fallback (hub never breaks if the fetch fails). `YourHubPage.tsx`: the picker is now a **search box** over cluster labels AND member city names (a matched member stores that city's own coordinates and the cluster's label); the full cluster list shows as a scrollable grid when the search is empty; `resolveMetroNews` = exact label, else nearest cluster within 100 mi measured to the closest of center + member cities (a Frisco reader lands in Frisco / Plano, not Irving).

## 2. Final bucket list + counts (own articles + RSS kept, post-dedup, cap 8)

| Bucket | Items | Bucket | Items |
|---|---|---|---|
| New York, NY | 8 | Raleigh, NC | 5 |
| San Jose, CA | 8 | Dublin, CA | 4 |
| Seattle, WA | 8 | Austin, TX | 4 |
| Chicago, IL | 8 | Long Island, NY | 4 |
| Irving, TX | 8 | Indianapolis, IN | 4 |
| Los Angeles, CA | 8 | Fremont, CA | 3 |
| Boston, MA | 8 | Tampa, FL | 3 |
| Houston, TX | 8 | Columbus, OH | 3 |
| Detroit, MI | 8 | Orange County, CA | 2 |
| Atlanta, GA | 8 | Charlotte, NC | 2 |
| San Francisco, CA | 8 | Minneapolis, MN | 2 |
| Phoenix, AZ | 8 | Naperville, IL | 1 |
| San Diego, CA | 8 | Tracy, CA | 1 |
| Miami, FL | 8 | Cerritos, CA | 1 |
| Las Vegas, NV | 7 | Schaumburg, IL | 0 |
| Sacramento, CA | 6 | Loudoun County, VA | 0 |
| Frisco / Plano, TX | 5 | Johns Creek, GA | 0 |
| Edison, NJ | 5 | Howard County, MD | 0 |
| Washington, DC | 5 | Broward County, FL | 0 |
| Philadelphia, PA | 5 | Portland, OR | 0 |
| | | Sugar Land, TX | 0 |
| | | Denver, CO | 0 |

Empty buckets hide on the hub (existing rule). **Portland and Denver were also 0 in the pre-Phase-1 production file** — seasonal thinness, not a regression. Most net-new buckets at 0–2 matches the readiness research ("live on our own articles + events/directory first").

## 3. Adjustments vs the appendix (all decided or discovered during the build)

- **Fremont split out** of cluster #2 into its own bucket (Kiran's request); #2 relabeled "San Jose, CA".
- **SF merged**: clusters #26 (Oakland) + #38 (SF singleton) → one "San Francisco, CA" bucket.
- **Portland pooled**: cluster #37 (Bethany) members include Portland itself → one "Portland, OR" bucket.
- **Las Vegas pooled**: clusters #63 (Henderson) + #116 (Las Vegas) → one bucket.
- **Cluster #29 (Yonkers / Bergen fringe, 32,806) deliberately NOT split out** — the parent's net-new list didn't include it and the research marks it COVERED by NYC at ~18 mi. Flagged here for a rename/add decision in Phase 2.
- **Nassau reassignment**: five places the algorithm put in the NYC cluster (Valley Stream, Elmont, Franklin Square, North New Hyde Park, Garden City Park) were moved to the Long Island bucket's members + aliases — editorially they are Long Island, and a headline naming Elmont is Long Island news.
- **Irving, TX carries "Dallas"**: with Dallas split into Frisco/Plano + Irving clusters, the Irving bucket (which contains Dallas city as a member) takes the Dallas/D FW aliases. Stored user locations labeled "Dallas, TX" resolve by distance to Irving (~9 mi). No reader loses coverage.
- **Detroit center = Troy** (where the cluster's diaspora actually is), label stays "Detroit, MI".
- **Bare-name aliases dropped where the name is also a common surname or a bigger namesake** (they stay in `members[]` for picker search): Allen + McKinney TX (Finn Allen the cricketer and Rep. Donavan McKinney both false-matched in QA round 1), Newark CA (Newark NJ airport/court + Newark-on-Trent UK dominated), Duluth GA, Plymouth MN, Richmond TX, Aurora CO (Aurora kept only in Naperville's aliases — Aurora IL is the larger cluster member; a documented either/or), Columbia MD, Vancouver WA.
- **Charlotte, NC blocklist += "charlotte county"** — QA round 1 caught a Florida python story whose excerpt names Charlotte County, FL.

## 4. Guard profiles implemented (data + code)

`context_guard` profiles in `build-local-news.py`, blocklists as data in the table:

- **san_jose** — block `costa rica`; accented "San José" rejected without California context.
- **dublin_ca** — bare "Dublin" requires CA context within 80 chars; block `ireland|dáil|tánaiste|garda`; a Dublin story with Ohio context is rejected here.
- **dublin_oh** (Columbus) — mirror image: bare "Dublin" requires Ohio context; CA-context Dublins rejected. The two Dublins cannot cross-match (verified both directions in unit tests).
- **washington_dc** — "Washington" requires DC context (state references rejected).
- **portland_or** — "Portland" requires Oregon context (Maine rejected); pooled names (Bethany, Beaverton, …) match freely.
- **fishers_in** — "Fishers" matches at title start, after in/at/near, or with Indiana context; occupation uses blocked ("for Fishers", fishing/fisheries/deep-sea contexts, scoped to titles naming Fishers).
- **orange_county** — "Orange County" matches blocked when the title also carries Florida/Orlando/Chapel Hill/North Carolina context.
- **edison-nj** block `thomas edison` (data).

## 5. QA results

- **Guard unit tests: 33/33 pass** — this morning's known cases (Costa Rica mission ×2 variants, United A321XLR Dublin route, Trinity College Dublin, Pippal Dublin opening, Thomas Edison Musk headline) plus Dublin OH both directions, Fishers town vs occupation, Washington state, Portland ME, Orange County FL/NC.
- **Full builds**: run twice (~9 min each — 173 pooled queries; slower than the plan's ~5–7 min estimate because query lists run to 6/bucket; acceptable inside the 4 h enricher cycle, noted for Phase 2 tuning). Build 1: 192 items; after QA fixes (§3 surname/Newark/Charlotte-County), build 2: **184 items**.
- **Junk scans across ALL buckets (final build): 0 hits** — Costa Rica, Ireland-in-Dublin-CA, Thomas Edison, fishers-occupation, Dublin CA↔OH cross-matches, Orlando-in-Orange-County.
- **Focus buckets eyeballed in full** (all new/split + 4 Bay Area): Frisco/Plano, Indianapolis (Fishers + Carmel Diwali — exactly the predicted yield), Long Island (3 on-topic Diwali items), Tracy (Manteca Durga Puja via pooling), Naperville (ISKCON temple), San Jose, Fremont, Dublin CA, SF all read clean after fixes.
- **TypeScript**: `npx tsc -p tsconfig.app.json --noEmit` — **0 errors in both touched files, before and after** (repo total 91 pre-existing errors elsewhere, untouched).

## 6. Picker behavior + zip status

- Search filters by label + member names; selecting a member row ("Hicksville, NY — Long Island, NY area") stores the member's coordinates with the cluster's label, so news, events, and distance all resolve locally.
- "Use my location" unchanged (geolocation → stored point → nearest-cluster resolution).
- **Zip search: WIRED, no follow-up needed.** The repo already has a full local zip database (`src/lib/geo.ts` → `/data/zipcodes.json`, 41,488 zips, lazy-loaded, `lookupZip()` already used by Events/Directory). The hub's zip submit now tries the local DB first (falls back to the previous zippopotam.us API on a miss); the resulting coordinates resolve to the nearest cluster with news within 100 mi via member-city distances.

## 7. Files changed (working tree, uncommitted)

- `research/data/clusters.json`, `research/data/yield.json`, `research/data/readiness.json`, `research/data/mapping.json` — new (research data preserved from /tmp).
- `public/data/clusters.json` — new, canonical cluster table.
- `pipeline/build-local-news.py` — rewritten to consume the table (guards as profiles + data).
- `public/data/local-news.json` — regenerated (184 items, 42 buckets).
- `src/hooks/useHubLocation.ts` — clusters loader + fallback; `METRO_PICKER` removed.
- `src/pages/YourHubPage.tsx` — search picker, cluster-based `resolveMetroNews`, local-DB zip.
- `research/phase1-build-report-2026-10-13.md` — this report.

## 8. Left imperfect (honest list)

- **Two borderline SF-bucket items** from V1 excerpt matching (pre-existing behavior, not a regression): an LA mayoral story whose excerpt cites a *Berkeley* IGS poll, and a Toronto Moosewala story whose excerpt mentions the Bay Area. Excerpt-mention matching is the shipped V1 trade-off; tightening it is an editorial call, not patched unilaterally.
- **One same-story RSS pair** in Sacramento (two wordings of the Vance/UC Davis story; token overlap 0.35, below the 0.55 near-dup threshold Kiran approved this morning). Threshold not changed without approval.
- **8 empty buckets** — expected per readiness research for most; they fill from our own articles/events as coverage lands. Schaumburg/Loudoun/Johns Creek/Howard/Broward/Sugar Land had zero bucket-ready headlines in the 30-day window.
- **Build time ~9 min** vs the plan's 5–7 min estimate (173 queries). Fine for the 4 h cycle; Phase 2 may want query-list trimming for tail clusters.
- **Township blind spot** (research §1) is only partially addressed: Edison's members come from place data; NJ/PA/MI county-subdivision membership (e.g. Edison township's full weight) is a Phase 2 data upgrade, as is the #29 Yonkers/Bergen bucket decision.
- The one-off generator script used to author `clusters.json` was lost when /tmp was wiped mid-session; the JSON itself is the canonical artifact and is fully self-describing (`source_ranks` trace every bucket back to the appendix).
