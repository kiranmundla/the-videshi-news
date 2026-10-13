# Diaspora Suburb Clusters — Local News Coverage Plan

**Date:** 2026-10-13 · **Status:** Research for approval — nothing built yet · **Author:** Muse (research pass commissioned by Kiran)

## TL;DR

- The US Asian Indian ("Asian Indian alone") population is **4,625,449** (ACS 2024 5-year, table B02015, variable B02015_021E). **80.7%** of them (3,734,550) live in Census "places" (cities/CDPs); the rest live in unincorporated or township geographies a place-based system cannot see directly.
- Pooling places within an 18-mile radius produces **120 clusters**. The **top 35 clusters hold 52.6%** of the entire US Asian Indian population; top 50 hold 59.3%; **all 120 together hold 70.3%**. Reaching 85% with place-based buckets is **impossible** (ceiling is 80.7% before pooling losses) — anyone who needs a number: ~70% is the practical maximum of this approach, and the last 10 points cost 70 extra micro-buckets.
- Of the top 35 clusters, today's 27 metros **fully cover 22, partially cover 9** (a metro is nearby, but its bucket never queries their suburbs — Frisco/Plano, Naperville, Schaumburg, Loudoun County, Johns Creek…), **and miss 4 entirely**: Orange County CA (56,151 people, #16), Sacramento (42,709), Charlotte (41,983), Indianapolis (26,669). Five of today's metros are actually two clusters wearing one label and should **split**: Dallas (→ Frisco/Plano + Irving), Chicago (→ Naperville + Schaumburg), Washington DC (→ Loudoun County), Atlanta (→ Johns Creek), Houston (→ Sugar Land).
- **Yield reality check (the uncomfortable part):** running the pipeline's own Google News RSS query + filters for the top net-new clusters over 30 days returned **0 qualifying headlines** for Orange County, Charlotte, St. Louis, Fresno, Cleveland, Eastvale and Sugar Land, 2 for Sacramento (a national UC Davis story), 4 for Indianapolis (3 real — Carmel/Fishers Diwali festivals). This was measured *during Diwali season*, the best-case window. **RSS alone will not fill new buckets** — exactly what the Tri-Valley taught us (its bucket today is 3 of our own articles + 1 RSS item). Events and directory, which are already coordinate-based, are strong in most target clusters and must carry them; news fills in as our own writer pipeline covers their festivals and stories.
- **Recommendation:** Phase 1 = generalize the builder to a data-driven cluster table and launch **~35 buckets covering ~53%** of the US diaspora (the 22 covered + 9 partials completed + 4 net-new), with the picker switched to city/zip search. Phase 2 = top 50 (~59%). Beyond that, returns diminish below ~0.3% of the diaspora per added bucket.

## 1. Data & method (everything cited, everything reproducible)

- **Population:** ACS **2024 5-year** (release `acs2024_5yr`, covering 2020–2024), table **B02015** "Asian Alone by Selected Groups", variable **B02015_021E** = "South Asian: Asian Indian". Total population per place from **B01003_001E**. Variable codes verified against the Census API's own group documentation (`api.census.gov/data/2024/acs/acs5/groups/B02015.json`).
- **Access note:** `api.census.gov` data queries now redirect to a "Missing Key" page without an API key (metadata/group endpoints still work keyless). The identical release and tables were therefore pulled from **Census Reporter** (`api.censusreporter.org/1.0/data/show/acs2024_5yr`), 51 state files, `geo_ids=160|04000US{state}` — 28,978 places with data. Cross-checks: Fremont city CA = 68,299 Asian Indians (29.9% of 228,295); US total = 4,625,449.
- **Centroids:** Census **Gazetteer** national places file (`Gaz_places_national.zip`, www2.census.gov), fields INTPTLAT/INTPTLONG, 29,514 places. Known quirk: San Francisco's internal point sits offshore (−123.03) because city territory includes the Farallon Islands — it split SF into a singleton cluster here; the build should use the existing METRO_PICKER coordinates or population-weighted centers, not raw Gazetteer points.
- **Clustering:** seeds = places with ≥2,000 Asian Indians (344 places). Greedy, largest first: each unassigned seed claims every unassigned place with AI > 0 within **18 miles** (haversine on centroids); cluster population = sum of members. 120 clusters result. Membership is by place centroid, so clusters ignore state lines (correctly: DC suburbs span MD/VA; the NY cluster includes Jersey City).
- **Yield check:** the pipeline's own `GNEWS_QUERY_TMPL` and `RSS_KEEP_RX`/`RSS_DROP_RX` imported from `pipeline/build-local-news.py`, 30-day window, per pooled city, counting only headlines that **name a pooled city in the title** (the production rule), deduped. Validated against known buckets first: Tri-Valley pooled = 4 desi-filter headlines (matches the 2026-10-13 morning measurement), Fremont = 3.
- **Readiness:** Supabase `directory_listings` and `events` counted per cluster center within a ~20-mile bounding box (PostgREST `count=exact` on latitude/longitude); events restricted to `date >= 2026-10-13` (upcoming only).

## 2. Where the diaspora actually lives

Top places by Asian Indian population (place-level; township caveat in §3):

| # | Place | Asian Indian | Share of place |
|---|-------|-------------:|---------------:|
| 1 | New York city, NY | 210,910 | 2.5% |
| 2 | San Jose city, CA | 80,168 | 8.1% |
| 3 | Fremont city, CA | 68,299 | 29.9% |
| 4 | Chicago city, IL | 47,034 | 1.7% |
| 5 | Frisco city, TX | 42,375 | 19.3% |
| 6 | Los Angeles city, CA | 42,244 | 1.1% |
| 7 | Irving city, TX | 41,284 | 16.1% |
| 8 | Jersey City city, NJ | 36,527 | 12.4% |
| 9 | Houston city, TX | 36,303 | 1.6% |
| 10 | Plano city, TX | 35,949 | 12.4% |
| 11 | Austin city, TX | 33,180 | 3.4% |
| 12 | San Diego city, CA | 32,726 | 2.4% |
| 13 | Sunnyvale city, CA | 27,642 | 17.9% |
| 14 | San Francisco city, CA | 24,900 | 3.0% |
| 15 | Seattle city, WA | 24,644 | 3.3% |

Highest *share* (places with ≥2,000 Asian Indians) — the suburbs where the diaspora is the local mainstream: Monmouth Junction NJ 46.6%, Princeton Meadows NJ 45.5%, Belle Mead NJ 44.7%, Loudoun Valley Estates VA 40.8%, Iselin NJ 40.2%, Mountain House CA 36.9%, Morrisville NC 34.1%, **Fremont CA 29.9%**, **Dublin CA 29.7%**, Cupertino CA 29.2%. Note how many are New Jersey CDPs inside townships — see §3.

Cumulative coverage as clusters are added in rank order: top 10 = 28.8% · top 20 = 41.1% · top 27 = 47.3% · **top 35 = 52.6%** · top 40 = 55.2% · top 50 = 59.3% · top 60 = 62.4% · top 120 (all) = 70.3%.

## 3. The township blind spot (read before trusting any NJ/PA/MI number)

ACS place-level data does **not** include townships — they are county subdivisions (summary level 060), not places (160). New Jersey is the extreme case: NJ's Asian Indian total is **426,992**, but its *places* sum to only **246,756 (58%)**. Verified flagship: **Edison township alone has 42,521 Asian Indians** (total pop 108,164; GEO_ID 0600000US3402320230, pulled from the official ACS 2024 table-based summary file) — more than all but a handful of US "places" — and it is entirely absent from place-level data. The #8 "Iselin" cluster (74,026) is therefore a floor: adding Edison township alone lifts the Middlesex cluster to **≥116,547**, i.e. top-4 nationally. The same effect, smaller, applies in PA, MI, MN, WI and New England town states. **Build implication:** the cluster table must be generated from place + county-subdivision geographies in township states, or NJ/PA clusters will be understated and mis-centered.

## 4. The cluster map — top 35, mapped to today's 27 metros

Status: **Covered** = an existing metro center within 20 mi of the cluster center · **Partial** = 20–35 mi (readers there resolve to the metro, but its bucket never queries their suburbs) · **Net-new** = >35 mi.

| # | Cluster (working name) | Asian Indian | Cum. % | Nearest metro today | Status | Top member places |
|---|------------------------|-------------:|-------:|---------------------|--------|------|
| 1 | New York City metro | 321,730 | 7.0% | New York, NY (5 mi) | COVERED | New York (210,910), Jersey City (36,527), Secaucus (5,298), Carteret borough (4,543), Clifton (4,030), Hoboken (3,693) |
| 2 | Silicon Valley / South Bay | 261,145 | 12.6% | San Jose, CA (5 mi) | COVERED | San Jose (80,168), Fremont (68,299), Sunnyvale (27,642), Santa Clara (24,582), Milpitas (18,955), Cupertino (17,112) |
| 3 | North Dallas — Frisco/Plano (Collin County) | 152,584 | 15.9% | Dallas, TX (26 mi) | PARTIAL | Frisco (42,375), Plano (35,949), McKinney (15,658), Allen (8,974), Coppell (7,898), Richardson (6,795) |
| 4 | Seattle–Eastside | 126,565 | 18.6% | Seattle, WA (1 mi) | COVERED | Seattle (24,644), Bellevue (21,090), Redmond (16,997), Sammamish (11,969), Mill Creek East (6,709), Kent (5,151) |
| 5 | Tri-Valley & East Bay | 101,359 | 20.8% | Dublin, CA (2 mi) | COVERED | Dublin (21,004), San Ramon (20,395), Pleasanton (16,963), Union City (10,396), Hayward (6,824), Newark (6,385) |
| 6 | Chicago — city & near suburbs | 82,274 | 22.6% | Chicago, IL (4 mi) | COVERED | Chicago (47,034), Des Plaines (4,376), Skokie (3,840), Morton Grove (2,790), Lombard (2,514), Niles (1,813) |
| 7 | Dallas–Irving / Mid-Cities | 78,940 | 24.3% | Dallas, TX (12 mi) | COVERED | Irving (41,284), Dallas (13,682), Flower Mound (5,964), Arlington (5,430), Southlake (2,158), Euless (1,813) |
| 8 | Edison–Middlesex County, NJ | 74,026 | 25.9% | Edison, NJ (6 mi) | COVERED | Iselin (7,857), Sayreville borough (4,823), Monmouth Junction (4,261), Franklin Park (3,802), Bradley Gardens (3,719), Short Hills (3,516) |
| 9 | Naperville / DuPage County, IL | 69,490 | 27.4% | Chicago, IL (29 mi) | PARTIAL | Naperville (20,365), Aurora (11,873), Bolingbrook (4,239), Carol Stream (4,222), Bartlett (3,546), Hanover Park (3,280) |
| 10 | Washington, DC & inner suburbs | 64,604 | 28.8% | Washington, DC (1 mi) | COVERED | Washington (8,197), Arlington (6,435), Rockville (2,944), Bethesda (2,370), North Potomac (2,336), Potomac (2,256) |
| 11 | NW Chicago suburbs — Schaumburg | 63,721 | 30.2% | Chicago, IL (26 mi) | PARTIAL | Schaumburg (10,151), Buffalo Grove (7,523), Hoffman Estates (6,269), Mount Prospect (3,731), Palatine (3,265), Vernon Hills (3,190) |
| 12 | Los Angeles | 62,659 | 31.5% | Los Angeles, CA (10 mi) | COVERED | Los Angeles (42,244), Torrance (4,058), Glendale (1,733), Burbank (1,574), Redondo Beach (1,485), Santa Monica (1,263) |
| 13 | Loudoun County, VA | 61,747 | 32.9% | Washington, DC (27 mi) | PARTIAL | Brambleton (7,298), South Riding (6,348), McNair (5,461), Ashburn (4,239), Loudoun Valley Estates (4,190), Centreville (3,315) |
| 14 | Research Triangle — Cary/Morrisville, NC | 59,995 | 34.2% | Raleigh, NC (10 mi) | COVERED | Cary (21,628), Morrisville (10,730), Apex (9,711), Raleigh (7,453), Durham (4,487), Holly Springs (2,639) |
| 15 | Boston & MetroWest suburbs | 59,419 | 35.5% | Boston, MA (3 mi) | COVERED | Boston (11,420), Cambridge (6,029), Quincy (4,041), Lexington (3,768), Malden (3,128), Newton (2,533) |
| 16 | Orange County, CA | 56,151 | 36.7% | Los Angeles, CA (37 mi) | NET-NEW | Irvine (20,236), Anaheim (5,222), Tustin (3,333), Corona (3,095), Yorba Linda (2,824), Fullerton (2,522) |
| 17 | Houston — inner | 54,331 | 37.9% | Houston, TX (2 mi) | COVERED | Houston (36,303), Missouri City (6,966), Pearland (4,961), Stafford (1,598), Bellaire (905), Atascocita (655) |
| 18 | Detroit suburbs — Oakland County, MI | 53,405 | 39.0% | Detroit, MI (18 mi) | COVERED | Troy (14,252), Farmington Hills (7,926), Warren (7,105), Rochester Hills (4,867), Sterling Heights (4,826), Detroit (3,456) |
| 19 | Austin & Round Rock | 49,582 | 40.1% | Austin, TX (3 mi) | COVERED | Austin (33,180), Cedar Park (6,193), Round Rock (5,687), Pflugerville (1,462), Brushy Creek (1,060), Lakeway (525) |
| 20 | North Atlanta — Johns Creek/Alpharetta | 49,206 | 41.1% | Atlanta, GA (22 mi) | PARTIAL | Johns Creek (10,919), Alpharetta (8,914), Milton (5,177), Dunwoody (4,770), Sandy Springs (4,014), Duluth (1,958) |
| 21 | Philadelphia & Main Line | 43,659 | 42.1% | Philadelphia, PA (4 mi) | COVERED | Philadelphia (23,628), King of Prussia (3,087), Echelon (1,975), Montgomeryville (1,602), Audubon (1,293), Lansdale borough (1,254) |
| 22 | Sacramento, CA | 42,709 | 43.0% | Dublin, CA (65 mi) | NET-NEW | Sacramento (15,030), Elk Grove (5,482), Roseville (4,259), Vineyard (3,953), Rancho Cordova (2,993), Davis (2,441) |
| 23 | Charlotte, NC | 41,983 | 43.9% | Raleigh, NC (129 mi) | NET-NEW | Charlotte (23,935), Concord (6,496), Huntersville (2,397), Harrisburg (1,903), Tega Cay (1,180), Fort Mill (1,102) |
| 24 | Howard County / Baltimore suburbs, MD | 39,997 | 44.8% | Washington, DC (28 mi) | PARTIAL | Ellicott City (9,485), Baltimore (3,643), Columbia (3,381), Ilchester (1,949), Elkridge (1,912), Woodlawn (1,676) |
| 25 | Long Island — Nassau County, NY | 38,926 | 45.6% | New York, NY (25 mi) | PARTIAL | Hicksville (7,370), East Meadow (2,740), Jericho (2,033), Levittown (1,747), Dix Hills (1,722), Plainview (1,638) |
| 26 | Oakland–Berkeley & the Peninsula | 38,172 | 46.4% | San Francisco, CA (11 mi) | COVERED | Oakland (4,808), Berkeley (4,782), Foster City (4,694), San Mateo (4,504), Redwood City (2,552), Alameda (1,731) |
| 27 | Phoenix–Tempe–Scottsdale | 37,154 | 47.3% | Phoenix, AZ (9 mi) | COVERED | Phoenix (22,446), Tempe (7,493), Scottsdale (5,050), Glendale (1,550), Paradise Valley (329), Litchfield Park (180) |
| 28 | San Diego, CA | 36,382 | 48.0% | San Diego, CA (7 mi) | COVERED | San Diego (32,726), Chula Vista (892), Poway (860), Encinitas (535), El Cajon (340), La Mesa (221) |
| 29 | Westchester, NY / Bergen fringe, NJ | 32,806 | 48.7% | New York, NY (18 mi) | COVERED | Yonkers (4,172), Paterson (4,066), Paramus borough (2,611), New City (2,530), Fair Lawn borough (2,291), Nanuet (1,408) |
| 30 | Tampa Bay, FL | 31,778 | 49.4% | Tampa, FL (2 mi) | COVERED | Tampa (7,613), Brandon (2,972), Riverview (2,305), St. Petersburg (1,986), Pebble Creek (1,383), Town 'n' Country (1,301) |
| 31 | Broward County, FL | 30,426 | 50.1% | Miami, FL (20 mi) | PARTIAL | Pembroke Pines (3,863), Coral Springs (3,425), Weston (3,113), Plantation (2,735), Miramar (2,682), Davie (2,115) |
| 32 | Tracy–Mountain House, CA | 30,134 | 50.7% | Dublin, CA (27 mi) | PARTIAL | Tracy (9,901), Mountain House (9,412), Manteca (5,958), Lathrop (4,385), Ripon (330), Byron (50) |
| 33 | Twin Cities West — Plymouth/Eden Prairie, MN | 29,099 | 51.4% | Minneapolis, MN (10 mi) | COVERED | Plymouth (4,302), Eden Prairie (4,158), Minneapolis (3,866), Maple Grove (2,389), Shakopee (1,659), Minnetonka (1,377) |
| 34 | Columbus, OH | 28,754 | 52.0% | Columbus, OH (2 mi) | COVERED | Columbus (16,666), Dublin (5,368), Powell (1,324), Hilliard (1,027), Reynoldsburg (1,027), Upper Arlington (1,014) |
| 35 | Indianapolis — Carmel/Fishers, IN | 26,669 | 52.6% | Chicago, IL (165 mi) | NET-NEW | Indianapolis (balance) (8,478), Carmel (5,207), Fishers (4,311), Greenwood (3,832), Plainfield (1,460), Westfield (861) |

**Splits hiding inside today's metros** (one label, two populations): Dallas → #3 Frisco/Plano (152,584) + #7 Irving (78,940); Chicago → #9 Naperville (69,490) + #11 Schaumburg (63,721) on top of #6; Washington DC → #13 Loudoun County (61,747); Atlanta → #20 Johns Creek (49,206); Houston → #39 Sugar Land (24,090, Fort Bend). Each split cluster out-populates entire metros we already run (e.g. Loudoun 61,747 > Boston cluster's diaspora-in-bucket terms and 4× Denver's cluster 20,708).

**Net-new in the top 50 beyond the top 35:** #40 St. Louis MO (22,775), #41 Fresno CA (22,362), #44 Inland Empire West CA (19,305), #47 Cleveland OH (17,565), #48 Kansas City–Overland Park KS (17,559), #49 Orlando FL (17,098), #50 Milwaukee WI (15,777). 60 of the 120 clusters are net-new overall.

## 5. Yield reality check — would the new buckets have news?

Pipeline-identical method, 30-day window, Diwali season (best case). "City-in-title" is the production bar; the funnel shows where stories die.

| Cluster | Raw RSS | After desi filter | City-in-title (bucket-ready) | Sample |
|---------|--------:|------------------:|------------------------------:|--------|
| Indianapolis, IN | — | — | **4** | "City of Carmel and Diwali committee invite community to 3rd annual Diwali Festival of Lights", "Fishers is lighting up for Diwali this Saturday" (+1 false friend: "India Deep-Sea Fishing Push: What Changes for **Fishers**" — the occupation, not the town) |
| Sacramento, CA | — | — | **2** | Both are one national story: "Vance alleges J-1 visa fraud at UC Davis" — local peg, national content |
| Orange County, CA | — | — | **0** | — |
| Charlotte, NC | — | — | **0** | — |
| St. Louis, MO | — | — | **0** | — |
| Fresno, CA | — | — | **0** | — |
| Inland Empire West, CA | — | — | **0** | — |
| Cleveland, OH | — | — | **0** | — |
| Sugar Land, TX | 11 | 3 | **0** | 3 desi stories surfaced but none named Sugar Land/Katy in the headline |
| *Validation:* Tri-Valley (existing) | 94 | 4 | **1** | "Association of Indo Americans Hosts Dussehra Diwali Dhamaka 2026 in Pleasanton" |
| *Validation:* Fremont (existing) | 31 | 3 | **1** | "India Currents' Vandana Kumar Wins Inaugural Gaurai Khela Award In Fremont" |
| *Validation:* Naperville/Schaumburg (partial) | 7 | 2 | **1** | "ISKCON Naperville Raises $600,000 At Tulabharam Fundraiser For Temple Expansion" |

Interpretation, honestly: (1) Even established buckets live on **our own articles** (V1) — the Dublin bucket is 3 own + 1 RSS. New clusters start near-empty on RSS and fill only as the writer pipeline covers their events/stories. (2) Yield is **seasonal** — this is the Diwali peak; a February window would be thinner. A bucket that is empty in February must hide (current rule) — events/directory carry it. (3) The festival/temple/fundraiser genre is what local desi headline news *is* at suburb scale — the same stories our events pipeline already finds, which is why pairing the launch with events coverage matters more than RSS tuning.

## 6. Readiness — events & directory already there?

Counts within ~20 mi of cluster center, queried live from Supabase on 2026-10-13. Directory is healthy everywhere (135–2,116 listings). Events are the weak layer in a few otherwise-ready clusters (Fresno: 0 upcoming).

| # | Cluster | Asian Indian | Directory listings | Upcoming events |
|---|---------|-------------:|-------------------:|----------------:|
| 1 | New York City metro | 321,730 | 1,189 | 145 |
| 2 | Silicon Valley / South Bay | 261,145 | 756 | 54 |
| 3 | North Dallas — Frisco/Plano (Collin County) | 152,584 | 1,898 | 18 |
| 4 | Seattle–Eastside | 126,565 | 305 | 40 |
| 5 | Tri-Valley & East Bay | 101,359 | 598 | 34 |
| 6 | Chicago — city & near suburbs | 82,274 | 474 | 253 |
| 7 | Dallas–Irving / Mid-Cities | 78,940 | 2,116 | 36 |
| 8 | Edison–Middlesex County, NJ | 74,026 | 1,218 | 158 |
| 9 | Naperville / DuPage County, IL | 69,490 | 245 | 77 |
| 10 | Washington, DC & inner suburbs | 64,604 | 910 | 62 |
| 11 | NW Chicago suburbs — Schaumburg | 63,721 | 353 | 152 |
| 12 | Los Angeles | 62,659 | 419 | 34 |
| 13 | Loudoun County, VA | 61,747 | 176 | 11 |
| 14 | Research Triangle — Cary/Morrisville, NC | 59,995 | 240 | 45 |
| 15 | Boston & MetroWest suburbs | 59,419 | 272 | 85 |
| 16 | Orange County, CA | 56,151 | 246 | 13 |
| 17 | Houston — inner | 54,331 | 539 | 33 |
| 18 | Detroit suburbs — Oakland County, MI | 53,405 | 223 | 23 |
| 19 | Austin & Round Rock | 49,582 | 241 | 33 |
| 20 | North Atlanta — Johns Creek/Alpharetta | 49,206 | 358 | 185 |
| 22 | Sacramento, CA | 42,709 | 107 | 14 |
| 23 | Charlotte, NC | 41,983 | 147 | 64 |
| 35 | Indianapolis — Carmel/Fishers, IN | 26,669 | 737 | 285 |
| 40 | St. Louis, MO | 22,775 | 146 | 14 |
| 41 | Fresno, CA | 22,362 | 84 | 0 |
| 47 | Cleveland, OH | 17,565 | 135 | 19 |

## 7. The plan

### Phase 1 — generalize + complete the top 35 (~53% of the US diaspora)
1. **Cluster table, not a hand list.** Generate `pipeline/clusters.json` from ACS place + county-subdivision data (place level nationally; MCD level for NJ/PA/MI/MN/WI/New England) with fields: label, center lat/lon, query cities, title-match aliases, guard profile. Regenerate annually on the new ACS release; hand-edit only names and guards. This replaces the hand-maintained `METROS` list in `build-local-news.py` and `METRO_PICKER` in `useHubLocation.ts` — the frontend fetches the same table (one source of truth, no more mirror drift).
2. **Buckets:** the 27 metros become their cluster equivalents; add the splits (Frisco/Plano, Naperville, Schaumburg, Loudoun, Johns Creek, Sugar Land) and net-new top-35 clusters (Orange County, Sacramento, Charlotte, Indianapolis, Howard County MD, Long Island–Nassau, Broward, Tracy–Mountain House, Columbus stays, Cerritos, Portland West–Bethany). ~35 buckets.
3. **Picker:** replace the 27-item list with **city/zip search → nearest cluster by distance** (geolocation path already resolves by haversine; reuse it for search results). A reader in an unincorporated area between clusters lands on the nearest bucket — product-level reach is therefore larger than the 52.6% bucket-population figure.
4. **Guards per cluster, declared in the table:** same-name traps already known — San Jose vs Costa Rica, Dublin CA vs Ireland, Portland OR vs ME, Washington DC vs state; new ones found in this research: **Dublin OH** (5,368 AI — inside the Columbus cluster; the two Dublins must never cross-match), **Fishers IN** vs "fishers" the occupation (seen in the wild in this very yield check), **Kansas City** MO vs KS (the diaspora cluster centers on Overland Park, KS), **Springfield** (IL/MO/MA/VA all have some), St. Louis city vs county, and "Orange County" CA vs FL/NC namesakes.
5. **Empty-cluster rule stays:** a bucket with no qualifying items hides; events + directory carry the area. Do not backfill with national stories (that is how Denver got a Hyderabad Navratri story labeled as local news).

### Phase 2 — top 50 (~59%)
Add St. Louis, Fresno, Inland Empire West, Cleveland, Kansas City, Orlando, Milwaukee, San Antonio, Nashville, Jacksonville, Short Pump/Richmond VA and the next tier — **after** an events-coverage pass for the weak ones (Fresno has 0 upcoming events within 20 mi today; launching a Fresno bucket before its events exist repeats the empty-bucket problem in the layer that actually matters locally).

### Phase 3 — the tail (top 60, ~62%) + data refresh discipline
Only if Phase 1–2 buckets demonstrably fill. Beyond ~60 clusters each addition buys <0.3% of the diaspora and adds an often-empty bucket; the remaining ~30 points of the population live in the 344-place long tail and outside places entirely — better served by nearest-cluster resolution than by named buckets.

### Cost & operations
- RSS is free; the builder's cost is wall-clock. Today: 27 metros / ~31 queries ≈ **100–130 s** per rebuild (including the script's 2 s per-query politeness delay). Phase 1 (~35 buckets, ~90 pooled queries) ≈ **5–7 min**; Phase 2 (~50 buckets) ≈ **8–10 min** — comfortably inside the existing 4-hour enricher cycle that already calls `build-local-news.py`. No new API spend.
- Ongoing maintenance: one ACS refresh per year (new 5-year release each December) + guard additions when a false positive is spotted — the same fix-in-pipeline loop as today.

## 8. Risks & open questions for Kiran

1. **Cluster names are editorial.** Working names above are mine ("North Dallas — Frisco/Plano", "Edison–Middlesex County"). Residents' own names (e.g. "DFW", "the Triangle", "DMV") should win where they exist — confirm or rename before the picker ships.
2. **Fremont: standalone or inside Silicon Valley?** The algorithm merges Fremont (68,299 — the #3 place in America) into the San Jose cluster; today it is its own metro and its own bucket. Keeping it standalone is defensible (huge, distinct identity) — but then "South Bay" loses its biggest member on paper. Your call.
3. **How much emptiness is acceptable?** Phase 1 launches several buckets whose RSS yield measured 0 this month. They will show our own articles when we cover their stories and hide otherwise. If a mostly-hidden bucket feels like a broken promise, the alternative is launching only clusters with proven yield + events depth (Indianapolis-style) and adding the rest in Phase 2.
4. **How far down the tail?** Top 35 (~53%), top 50 (~59%), or top 60 (~62%)? Each step is cheap to run but adds editorial surface (names, guards, QA).
5. **Township states need MCD data in the build** (§3) — this changes cluster *populations* in NJ/PA/MI (Edison effect) but not the reader experience. Worth doing in Phase 1 so the table is right from day one.
6. **Big-city granularity is out of scope here.** Place-level data treats NYC as one place (210,910) — Queens vs Edison-style suburb needs are different products. This plan covers the suburb gap only.

## Appendix — all 120 clusters

| # | Center place (algorithm) | Asian Indian | Cum. % | Nearest existing metro | Status |
|---|--------------------------|-------------:|-------:|------------------------|--------|
| 1 | New York city, NY | 321,730 | 7.0% | New York, NY (5 mi) | COVERED |
| 2 | San Jose city, CA | 261,145 | 12.6% | San Jose, CA (5 mi) | COVERED |
| 3 | Frisco city, TX | 152,584 | 15.9% | Dallas, TX (26 mi) | PARTIAL |
| 4 | Seattle city, WA | 126,565 | 18.6% | Seattle, WA (1 mi) | COVERED |
| 5 | Dublin city, CA | 101,359 | 20.8% | Dublin, CA (2 mi) | COVERED |
| 6 | Chicago city, IL | 82,274 | 22.6% | Chicago, IL (4 mi) | COVERED |
| 7 | Irving city, TX | 78,940 | 24.3% | Dallas, TX (12 mi) | COVERED |
| 8 | Iselin CDP, NJ | 74,026 | 25.9% | Edison, NJ (6 mi) | COVERED |
| 9 | Naperville city, IL | 69,490 | 27.4% | Chicago, IL (29 mi) | PARTIAL |
| 10 | Washington city, DC | 64,604 | 28.8% | Washington, DC (1 mi) | COVERED |
| 11 | Schaumburg village, IL | 63,721 | 30.2% | Chicago, IL (26 mi) | PARTIAL |
| 12 | Los Angeles city, CA | 62,659 | 31.5% | Los Angeles, CA (10 mi) | COVERED |
| 13 | Brambleton CDP, VA | 61,747 | 32.9% | Washington, DC (27 mi) | PARTIAL |
| 14 | Cary town, NC | 59,995 | 34.2% | Raleigh, NC (10 mi) | COVERED |
| 15 | Boston city, MA | 59,419 | 35.5% | Boston, MA (3 mi) | COVERED |
| 16 | Irvine city, CA | 56,151 | 36.7% | Los Angeles, CA (37 mi) | NET-NEW |
| 17 | Houston city, TX | 54,331 | 37.9% | Houston, TX (2 mi) | COVERED |
| 18 | Troy city, MI | 53,405 | 39.0% | Detroit, MI (18 mi) | COVERED |
| 19 | Austin city, TX | 49,582 | 40.1% | Austin, TX (3 mi) | COVERED |
| 20 | Johns Creek city, GA | 49,206 | 41.1% | Atlanta, GA (22 mi) | PARTIAL |
| 21 | Philadelphia city, PA | 43,659 | 42.1% | Philadelphia, PA (4 mi) | COVERED |
| 22 | Sacramento city, CA | 42,709 | 43.0% | Dublin, CA (65 mi) | NET-NEW |
| 23 | Charlotte city, NC | 41,983 | 43.9% | Raleigh, NC (129 mi) | NET-NEW |
| 24 | Ellicott City CDP, MD | 39,997 | 44.8% | Washington, DC (28 mi) | PARTIAL |
| 25 | Hicksville CDP, NY | 38,926 | 45.6% | New York, NY (25 mi) | PARTIAL |
| 26 | Oakland city, CA | 38,172 | 46.4% | San Francisco, CA (11 mi) | COVERED |
| 27 | Phoenix city, AZ | 37,154 | 47.3% | Phoenix, AZ (9 mi) | COVERED |
| 28 | San Diego city, CA | 36,382 | 48.0% | San Diego, CA (7 mi) | COVERED |
| 29 | Yonkers city, NY | 32,806 | 48.7% | New York, NY (18 mi) | COVERED |
| 30 | Tampa city, FL | 31,778 | 49.4% | Tampa, FL (2 mi) | COVERED |
| 31 | Pembroke Pines city, FL | 30,426 | 50.1% | Miami, FL (20 mi) | PARTIAL |
| 32 | Tracy city, CA | 30,134 | 50.7% | Dublin, CA (27 mi) | PARTIAL |
| 33 | Plymouth city, MN | 29,099 | 51.4% | Minneapolis, MN (10 mi) | COVERED |
| 34 | Columbus city, OH | 28,754 | 52.0% | Columbus, OH (2 mi) | COVERED |
| 35 | Indianapolis city (balance), IN | 26,669 | 52.6% | Chicago, IL (165 mi) | NET-NEW |
| 36 | Cerritos city, CA | 26,457 | 53.1% | Los Angeles, CA (16 mi) | COVERED |
| 37 | Bethany CDP, OR | 25,735 | 53.7% | Portland, OR (8 mi) | COVERED |
| 38 | San Francisco city, CA | 24,900 | 54.2% | San Francisco, CA (34 mi) | PARTIAL |
| 39 | Sugar Land city, TX | 24,090 | 54.8% | Houston, TX (19 mi) | COVERED |
| 40 | Maryland Heights city, MO | 22,775 | 55.2% | Chicago, IL (265 mi) | NET-NEW |
| 41 | Fresno city, CA | 22,362 | 55.7% | San Jose, CA (122 mi) | NET-NEW |
| 42 | Germantown CDP, MD | 21,588 | 56.2% | Washington, DC (22 mi) | PARTIAL |
| 43 | Denver city, CO | 20,708 | 56.6% | Denver, CO (6 mi) | COVERED |
| 44 | Eastvale CDP, CA | 19,305 | 57.1% | Los Angeles, CA (39 mi) | NET-NEW |
| 45 | Chandler city, AZ | 18,305 | 57.5% | Phoenix, AZ (17 mi) | COVERED |
| 46 | Princeton Meadows CDP, NJ | 18,190 | 57.9% | Edison, NJ (15 mi) | COVERED |
| 47 | Cleveland city, OH | 17,565 | 58.2% | Detroit, MI (92 mi) | NET-NEW |
| 48 | Overland Park city, KS | 17,559 | 58.6% | Chicago, IL (425 mi) | NET-NEW |
| 49 | Orlando city, FL | 17,098 | 59.0% | Tampa, FL (78 mi) | NET-NEW |
| 50 | Milwaukee city, WI | 15,777 | 59.3% | Chicago, IL (84 mi) | NET-NEW |
| 51 | Garland city, TX | 15,641 | 59.7% | Dallas, TX (13 mi) | COVERED |
| 52 | Atlanta city, GA | 14,897 | 60.0% | Atlanta, GA (2 mi) | COVERED |
| 53 | Stamford city, CT | 14,652 | 60.3% | New York, NY (35 mi) | PARTIAL |
| 54 | San Antonio city, TX | 14,587 | 60.6% | Austin, TX (72 mi) | NET-NEW |
| 55 | Folsom city, CA | 14,500 | 60.9% | Dublin, CA (80 mi) | NET-NEW |
| 56 | Nashville-Davidson metropolitan government (balance), TN | 13,682 | 61.2% | Atlanta, GA (215 mi) | NET-NEW |
| 57 | Bakersfield city, CA | 13,325 | 61.5% | Los Angeles, CA (98 mi) | NET-NEW |
| 58 | Short Pump CDP, VA | 13,283 | 61.8% | Washington, DC (92 mi) | NET-NEW |
| 59 | Jacksonville city, FL | 13,137 | 62.1% | Tampa, FL (172 mi) | NET-NEW |
| 60 | Palo Alto city, CA | 12,956 | 62.4% | Fremont, CA (13 mi) | COVERED |
| 61 | Novi city, MI | 12,482 | 62.6% | Detroit, MI (25 mi) | PARTIAL |
| 62 | Pittsburgh city, PA | 11,769 | 62.9% | Columbus, OH (163 mi) | NET-NEW |
| 63 | Henderson city, NV | 11,218 | 63.1% | Las Vegas, NV (12 mi) | COVERED |
| 64 | South Jordan city, UT | 10,750 | 63.4% | Las Vegas, NV (348 mi) | NET-NEW |
| 65 | Fort Worth city, TX | 10,527 | 63.6% | Dallas, TX (32 mi) | PARTIAL |
| 66 | Ceres city, CA | 10,118 | 63.8% | San Jose, CA (54 mi) | NET-NEW |
| 67 | Yuba City city, CA | 10,063 | 64.0% | Dublin, CA (100 mi) | NET-NEW |
| 68 | Collierville town, TN | 9,794 | 64.2% | Atlanta, GA (316 mi) | NET-NEW |
| 69 | Nashua city, NH | 9,628 | 64.4% | Boston, MA (35 mi) | PARTIAL |
| 70 | Madison city, WI | 9,558 | 64.7% | Chicago, IL (124 mi) | NET-NEW |
| 71 | Santa Clarita city, CA | 9,464 | 64.9% | Los Angeles, CA (29 mi) | PARTIAL |
| 72 | Buffalo city, NY | 8,731 | 65.0% | Detroit, MI (216 mi) | NET-NEW |
| 73 | Woodbury city, MN | 8,508 | 65.2% | Minneapolis, MN (17 mi) | COVERED |
| 74 | Louisville/Jefferson County metro government (balance), KY | 8,202 | 65.4% | Columbus, OH (189 mi) | NET-NEW |
| 75 | Leander city, TX | 8,098 | 65.6% | Austin, TX (22 mi) | PARTIAL |
| 76 | Mason city, OH | 8,002 | 65.8% | Columbus, OH (81 mi) | NET-NEW |
| 77 | Brentwood city, CA | 7,978 | 65.9% | Dublin, CA (20 mi) | PARTIAL |
| 78 | Oklahoma City city, OK | 7,930 | 66.1% | Dallas, TX (190 mi) | NET-NEW |
| 79 | Bentonville city, AR | 7,756 | 66.3% | Dallas, TX (287 mi) | NET-NEW |
| 80 | Carlsbad city, CA | 7,179 | 66.4% | San Diego, CA (29 mi) | PARTIAL |
| 81 | Miami city, FL | 7,117 | 66.6% | Miami, FL (1 mi) | COVERED |
| 82 | Stockton city, CA | 7,106 | 66.7% | Dublin, CA (39 mi) | NET-NEW |
| 83 | Schenectady city, NY | 6,762 | 66.9% | New York, NY (144 mi) | NET-NEW |
| 84 | Greensboro city, NC | 6,465 | 67.0% | Raleigh, NC (70 mi) | NET-NEW |
| 85 | Horizon West CDP, FL | 6,460 | 67.2% | Tampa, FL (61 mi) | NET-NEW |
| 86 | Bloomington city, IL | 6,086 | 67.3% | Chicago, IL (119 mi) | NET-NEW |
| 87 | Livingston city, CA | 5,931 | 67.4% | San Jose, CA (64 mi) | NET-NEW |
| 88 | Thousand Oaks city, CA | 5,915 | 67.5% | Los Angeles, CA (37 mi) | NET-NEW |
| 89 | Pasadena city, CA | 5,654 | 67.7% | Los Angeles, CA (10 mi) | COVERED |
| 90 | Virginia Beach city, VA | 5,564 | 67.8% | Washington, DC (157 mi) | NET-NEW |
| 91 | Okemos CDP, MI | 5,355 | 67.9% | Detroit, MI (74 mi) | NET-NEW |
| 92 | Cincinnati city, OH | 5,147 | 68.0% | Columbus, OH (98 mi) | NET-NEW |
| 93 | Hoover city, AL | 5,097 | 68.1% | Atlanta, GA (142 mi) | NET-NEW |
| 94 | Omaha city, NE | 5,053 | 68.2% | Minneapolis, MN (292 mi) | NET-NEW |
| 95 | College Station city, TX | 4,937 | 68.3% | Houston, TX (80 mi) | NET-NEW |
| 96 | Ann Arbor city, MI | 4,875 | 68.4% | Detroit, MI (35 mi) | NET-NEW |
| 97 | Worcester city, MA | 4,869 | 68.6% | Boston, MA (39 mi) | NET-NEW |
| 98 | West Lafayette city, IN | 4,853 | 68.7% | Chicago, IL (105 mi) | NET-NEW |
| 99 | Reno city, NV | 4,732 | 68.8% | Dublin, CA (169 mi) | NET-NEW |
| 100 | Champaign city, IL | 4,692 | 68.9% | Chicago, IL (126 mi) | NET-NEW |
| 101 | The Woodlands CDP, TX | 4,683 | 69.0% | Houston, TX (30 mi) | PARTIAL |
| 102 | Tucson city, AZ | 4,097 | 69.0% | Phoenix, AZ (113 mi) | NET-NEW |
| 103 | Peoria city, AZ | 4,074 | 69.1% | Phoenix, AZ (27 mi) | PARTIAL |
| 104 | Tulsa city, OK | 3,903 | 69.2% | Dallas, TX (237 mi) | NET-NEW |
| 105 | Columbus city, IN | 3,793 | 69.3% | Columbus, OH (164 mi) | NET-NEW |
| 106 | League City city, TX | 3,721 | 69.4% | Houston, TX (24 mi) | PARTIAL |
| 107 | Peoria city, IL | 3,689 | 69.5% | Chicago, IL (129 mi) | NET-NEW |
| 108 | Parker town, CO | 3,387 | 69.5% | Denver, CO (20 mi) | COVERED |
| 109 | Gainesville city, FL | 3,196 | 69.6% | Tampa, FL (120 mi) | NET-NEW |
| 110 | Wesley Chapel CDP, FL | 3,185 | 69.7% | Tampa, FL (19 mi) | COVERED |
| 111 | Denton city, TX | 3,073 | 69.7% | Dallas, TX (36 mi) | NET-NEW |
| 112 | Little Rock city, AR | 3,042 | 69.8% | Dallas, TX (288 mi) | NET-NEW |
| 113 | Lexington-Fayette urban county, KY | 2,838 | 69.9% | Columbus, OH (154 mi) | NET-NEW |
| 114 | Albuquerque city, NM | 2,785 | 69.9% | Phoenix, AZ (330 mi) | NET-NEW |
| 115 | Bloomington city, IN | 2,694 | 70.0% | Columbus, OH (196 mi) | NET-NEW |
| 116 | Las Vegas city, NV | 2,661 | 70.0% | Las Vegas, NV (8 mi) | COVERED |
| 117 | Tallahassee city, FL | 2,634 | 70.1% | Tampa, FL (204 mi) | NET-NEW |
| 118 | Wichita city, KS | 2,435 | 70.2% | Dallas, TX (341 mi) | NET-NEW |
| 119 | Columbus city, GA | 2,252 | 70.2% | Atlanta, GA (90 mi) | NET-NEW |
| 120 | Colorado Springs city, CO | 2,181 | 70.3% | Denver, CO (61 mi) | NET-NEW |

---
*Sources: US Census Bureau ACS 2024 5-year (B02015_021E, B01003_001E) via Census Reporter; Census Gazetteer national places file; ACS 2024 table-based summary file (Edison township verification); Google News RSS via pipeline/build-local-news.py (yield check, 2026-10-13); Supabase directory_listings/events (readiness counts, 2026-10-13). Research workspace: /tmp/diaspora (state JSONs, clusters.json, yield.json, readiness.json).*
