#!/usr/bin/env python3
"""
Travel destinations data layer for The Videshi.

Builds public/data/travel-destinations.json — one record per travel
guide destination (public/data/travel-guides/*.md), joining:
  - guide content (highlights mined from each guide's own
    "Top Experiences" section — no invented attractions),
  - galleries (public/data/travel-galleries.json photos, where present),
  - seasonality (curated best/peak months — mainstream season knowledge
    cross-checked against research/diaspora-travel-patterns.md),
  - REAL fare data only (public/data/flight-deals.json): a destination
    gets fare_from / cheapest_month ONLY when a tracked flight-deals
    route actually serves it. Otherwise those fields are null and the
    record says so — accuracy over coverage (Kiran's bar).

Trending score (for the CURRENT month) is transparent: three labeled
components with per-component reasons, never a black-box number:
  - season_fit     (0-50)  current month in best months / shoulder / off
  - fare_drop      (0-30)  a notable drop exists on the mapped route
  - offpeak_value  (0-20)  shoulder-season value vs peak-demand pricing
Components that can't be computed (no fare route tracked) are null and
listed in data_quality, and the score reports its own max possible.

Also emits season_fit_by_month (2 = in season, 1 = shoulder, 0 = off)
per destination so the frontend can rank "best in <month>"
deterministically, plus precomputed trending_now / best_by_month slug
rankings.

Destination tiering (Kiran, 2026-10-14): curated picks and the
trending/best-by-month rankings feature international + in-India
destinations plus TOP-TIER US destinations only (TOP_TIER_US below).
Second-tier US destinations are deferred — their records stay in the
output (guides remain in the full All Destinations index) flagged
eligible_for_picks=False, but they never appear in the rankings.

Usage:
  python3 build-travel-destinations.py            (write JSON)
  python3 build-travel-destinations.py --dry-run  (print summary only)

Also writes a SHADOW trending ranking (pilot, 2026-10-15) to
pipeline/.state/trending-shadow.json using the rebalanced weights and
the search-interest signal — see write_shadow(). Live output above is
never affected by it.
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

REPO = Path.home() / "workspace" / "the-videshi-news"
GUIDES_DIR = REPO / "public" / "data" / "travel-guides"
GALLERIES_FILE = REPO / "public" / "data" / "travel-galleries.json"
DEALS_FILE = REPO / "public" / "data" / "flight-deals.json"
METROS_DEALS_FILE = REPO / "public" / "data" / "flight-deals-metros.json"
INTL_DEALS_FILE = REPO / "public" / "data" / "flight-deals-intl.json"
OUTPUT_FILE = REPO / "public" / "data" / "travel-destinations.json"

# International matrix destinations (flight-deals.py --intl, weekly):
# slug -> arrival airport. Same conservative rule as ROUTE_MAP: the
# fare shown must be FOR that destination (US->SYD is an Australia
# fare; US->CDG is a France fare).
INTL_AIRPORT_MAP = {
    "australia": "SYD",
    "bali": "DPS",
    "cabo": "SJD",
    "egypt": "CAI",
    "fiji": "NAN",
    "france": "CDG",
    "greece": "ATH",
    "hawaii": "HNL",
}

# Which flight-deals routes genuinely serve a guide destination.
# Deliberately conservative: the fare must be FOR that destination.
# US→BOM is not a Goa fare; US→DEL is not a Rajasthan fare.
ROUTE_MAP = {
    "karnataka": ["SFO-BLR", "JFK-BLR", "ORD-BLR", "DFW-BLR",
                  "LAX-BLR", "SEA-BLR", "EWR-BLR", "IAD-BLR",
                  "ATL-BLR", "BOS-BLR"],
}

# Destination tiering (Kiran, 2026-10-14): US destinations are eligible
# for curated picks / trending rankings ONLY if top-tier. Kiran's named
# top tier: Hawaii, Alaska, Yellowstone — Yellowstone is covered by the
# national-parks guide (Yellowstone, Grand Canyon & Yosemite), so that
# guide is the top-tier US entry. Deferred (second-tier) US guides
# today: florida, new-york-city.
TOP_TIER_US = {"hawaii", "alaska", "national-parks"}


def pick_eligible(slug, group):
    """Curated-pick eligibility under the destination tiering scope."""
    return group != "usa" or slug in TOP_TIER_US

NAME_OVERRIDES = {
    "abu-dhabi": "Abu Dhabi",
    "dominican-republic": "Dominican Republic",
    "himachal-pradesh": "Himachal Pradesh",
    "national-parks": "US National Parks",
    "new-york-city": "New York City",
    "new-zealand": "New Zealand",
    "northeast-india": "Northeast India",
    "puerto-vallarta": "Puerto Vallarta",
    "riviera-maya": "Riviera Maya",
    "south-africa": "South Africa",
    "tamil-nadu": "Tamil Nadu",
}

# slug -> (group, region, best_months, peak_months, season_note)
# best = when the destination is at its best; peak = high-demand months
# (subset of best) when prices/crowds spike. Mainstream season knowledge,
# cross-checked with research/diaspora-travel-patterns.md for India.
META = {
    # ── India ──────────────────────────────────────────────────────
    "goa": ("india", "India — West Coast", [11, 12, 1, 2], [12, 1],
            "Dry, sunny winter season; monsoon (Jun–Sep) shuts most beach shacks."),
    "kerala": ("india", "India — South", [10, 11, 12, 1, 2, 3], [12, 1],
               "Post-monsoon green and cool; peak over Christmas–New Year."),
    "karnataka": ("india", "India — South", [10, 11, 12, 1, 2], [12],
                  "Bengaluru is mild year-round; Hampi and Coorg shine Oct–Feb."),
    "tamil-nadu": ("india", "India — South", [11, 12, 1, 2], [1],
                   "Coolest months; Pongal in mid-January. Coastal rain peaks Oct–Dec."),
    "rajasthan": ("india", "India — West", [10, 11, 12, 1, 2, 3], [12, 1, 2],
                  "Desert winter is the season — summers are dangerously hot."),
    "kashmir": ("india", "India — Himalayas", [4, 5, 6, 7, 8, 9, 10], [5, 6],
                "Spring blossom to autumn chinar colours; houseboats Apr–Oct."),
    "himachal-pradesh": ("india", "India — Himalayas", [3, 4, 5, 6, 9, 10, 11], [5, 6],
                         "Spring and autumn are clearest; avoid Jul–Aug monsoon landslides."),
    "uttarakhand": ("india", "India — Himalayas", [3, 4, 5, 6, 9, 10, 11], [5, 6],
                    "Char Dham season May–Jun and Sep–Oct; winters are bitter at altitude."),
    "northeast-india": ("india", "India — Northeast", [10, 11, 12, 1, 2, 3, 4], [12],
                        "Dry season; Hornbill Festival in early December."),
    # ── USA ────────────────────────────────────────────────────────
    "alaska": ("usa", "US — Alaska", [6, 7, 8], [7],
               "Midnight-sun summer; cruise season. Aurora viewing is Sep–Mar."),
    "florida": ("usa", "US — Southeast", [11, 12, 1, 2, 3, 4], [12, 3],
                "Dry, mild winter–spring; summer is hot, humid and hurricane-prone."),
    "hawaii": ("usa", "US — Hawaii", [4, 5, 6, 9, 10, 11, 12], [12, 7],
               "Great most of the year; whale season Dec–Apr, surf peaks in winter."),
    "new-york-city": ("usa", "US — East Coast", [4, 5, 6, 9, 10, 11], [10, 12],
                      "Spring and autumn are peak NYC — foliage mid-Oct to early Nov."),
    "national-parks": ("usa", "US — National Parks", [5, 6, 9, 10], [7],
                        "Shoulder months beat the summer crowds at most major parks."),
    # ── International ──────────────────────────────────────────────
    "abu-dhabi": ("international", "Middle East", [11, 12, 1, 2, 3], [12, 1],
                  "Winter sun season; summers are extremely hot."),
    "dubai": ("international", "Middle East", [11, 12, 1, 2, 3], [12, 1, 2],
              "Winter is peak — outdoor weather, festivals, highest prices."),
    "oman": ("international", "Middle East", [10, 11, 12, 1, 2, 3], [12],
             "Cool season for wadis and desert camps; Salalah's khareef is Jun–Aug."),
    "bali": ("international", "Southeast Asia", [4, 5, 6, 7, 8, 9, 10], [7, 8, 12],
             "Dry season Apr–Oct; rainy season Nov–Mar (mornings usually clear)."),
    "thailand": ("international", "Southeast Asia", [11, 12, 1, 2, 3], [12, 1],
                 "Cool, dry season; Songkran in mid-April."),
    "vietnam": ("international", "Southeast Asia", [11, 12, 2, 3, 4], [12],
                "Drier months overall — the country spans three climate zones."),
    "singapore": ("international", "Southeast Asia", [2, 3, 4, 6, 7, 9], [9, 12],
                  "Near-equatorial: visit anytime; F1 (Sep) and year-end spike prices."),
    "japan": ("international", "East Asia", [3, 4, 5, 10, 11], [4, 11],
              "Cherry blossom (late Mar–Apr) and autumn colours (Nov) are the peaks."),
    "australia": ("international", "Oceania", [9, 10, 11, 3, 4, 5], [12, 1],
                  "Southern-hemisphere spring/autumn are the sweet spots for Sydney & Melbourne."),
    "new-zealand": ("international", "Oceania", [12, 1, 2, 3], [12, 1],
                    "Southern summer Dec–Feb; March is quieter with settled weather."),
    "fiji": ("international", "Oceania", [5, 6, 7, 8, 9, 10], [7],
             "Dry season May–Oct; cyclone season is Nov–Apr."),
    "maldives": ("international", "Indian Ocean", [11, 12, 1, 2, 3, 4], [12, 1, 2],
                 "Dry northeast-monsoon season; best visibility for diving Jan–Mar."),
    "sri-lanka": ("international", "Indian Ocean", [12, 1, 2, 3], [12, 1],
                  "West/south coasts and hill country are at their best Dec–Mar."),
    "cancun": ("international", "Mexico & Caribbean", [12, 1, 2, 3, 4], [12, 3],
               "Dry season; avoid the Jun–Oct hurricane window where possible."),
    "riviera-maya": ("international", "Mexico & Caribbean", [11, 12, 1, 2, 3, 4], [12, 3],
                      "Dry season Nov–Apr; sargassum is worst in summer."),
    "puerto-vallarta": ("international", "Mexico & Caribbean", [11, 12, 1, 2, 3, 4], [12, 2],
                        "Dry season; whale watching Dec–Mar in Banderas Bay."),
    "cabo": ("international", "Mexico & Caribbean", [10, 11, 12, 1, 2, 3, 4, 5], [12, 3],
             "Whale season Dec–Apr; late summer is hot with storm risk."),
    "mexico": ("international", "Mexico & Caribbean", [11, 12, 1, 2, 3, 4, 5], [11, 12],
               "Mexico City is best Mar–May and for Day of the Dead (early Nov)."),
    "aruba": ("international", "Mexico & Caribbean", [12, 1, 2, 3, 4], [12, 2],
              "Outside the hurricane belt — reliably dry and breezy most of the year."),
    "bahamas": ("international", "Mexico & Caribbean", [12, 1, 2, 3, 4], [12, 3],
                "Dry season; hurricane risk peaks Aug–Oct."),
    "jamaica": ("international", "Mexico & Caribbean", [11, 12, 1, 2, 3, 4], [12, 3],
                "Dry season Nov–Apr; rains build from May."),
    "dominican-republic": ("international", "Mexico & Caribbean", [12, 1, 2, 3, 4], [12, 2],
                            "Dry season Dec–Apr; whale season in Samaná is Jan–Mar."),
    "banff": ("international", "Canada", [1, 2, 6, 7, 8, 9, 12], [7, 12],
              "Two seasons: summer lakes (Jun–Sep) and ski season (Dec–Mar)."),
    "france": ("international", "Europe", [4, 5, 6, 9, 10], [6, 7],
               "Late spring and early autumn beat the August crowds and closures."),
    "italy": ("international", "Europe", [4, 5, 6, 9, 10], [6, 7, 8],
              "Shoulder months have the weather without the peak crowds."),
    "spain": ("international", "Europe", [4, 5, 6, 9, 10], [7, 8],
              "Spring and autumn; August is hot and crowded on the coasts."),
    "portugal": ("international", "Europe", [5, 6, 9, 10], [7, 8],
                 "May–Jun and Sep–Oct are warm, bright and less crowded."),
    "greece": ("international", "Europe", [5, 6, 7, 9, 10], [7, 8],
               "Islands are best late May–early Oct; July–August is peak-price."),
    "switzerland": ("international", "Europe", [1, 2, 6, 7, 8, 9, 12], [7, 12],
                    "Summer hiking (Jun–Sep) and ski season (Dec–Mar)."),
    "scandinavia": ("international", "Europe", [5, 6, 7, 8], [7],
                    "Midnight-sun summers; aurora season runs Sep–Mar."),
    "iceland": ("international", "Europe", [2, 3, 6, 7, 8, 9, 10], [7],
                "Summer for the full ring road; Sep–Oct and Feb–Mar for auroras with daylight."),
    "london": ("international", "Europe", [4, 5, 6, 7, 9], [7, 12],
               "Late spring to early autumn; long June evenings are the highlight."),
    "egypt": ("international", "North Africa & Middle East", [10, 11, 12, 1, 2, 3, 4], [12, 2],
              "Cool season for the Nile valley; summers are fiercely hot."),
    "morocco": ("international", "North Africa & Middle East", [3, 4, 5, 10, 11], [4, 10],
                "Spring and autumn; the Sahara is best Oct–Apr."),
    "kenya": ("international", "Africa", [1, 2, 7, 8, 9, 10], [8],
              "Great Migration in the Maasai Mara Jul–Oct; dry Jan–Feb is also excellent."),
    "south-africa": ("international", "Africa", [5, 6, 7, 8, 9], [8, 12],
                     "Dry-season safari May–Sep; Cape Town is best Nov–Mar (see guide)."),
}


def season_fit(month, best_months):
    """2 = in season, 1 = shoulder (adjacent month), 0 = off season."""
    if month in best_months:
        return 2
    for b in best_months:
        if abs(month - b) == 1 or abs(month - b) == 11:
            return 1
    return 0


def mine_highlights(md_text, limit=5):
    """Extract Top Experiences titles + snippets from a guide's own text."""
    m = re.search(r"^##\s+Top Experiences\s*$", md_text, re.M)
    if not m:
        return []
    section = md_text[m.end():]
    nxt = re.search(r"^##\s+", section, re.M)
    if nxt:
        section = section[:nxt.start()]
    out = []
    for title, desc in re.findall(r"\*\*\d+\.\s*(.+?)\*\*\s*—\s*(.+?)(?=\n\s*\n|\Z)",
                                  section, re.S):
        snippet = " ".join(desc.split())
        if len(snippet) > 200:  # trim at a sentence boundary where possible
            cut = snippet[:200].rsplit(". ", 1)[0]
            snippet = (cut + ".") if len(cut) > 80 else snippet[:197] + "…"
        out.append({"title": " ".join(title.split()), "snippet": snippet})
        if len(out) >= limit:
            break
    return out


def reader_date_range(iso_range):
    """'2026-10-21 → 2026-10-27' -> 'Oct 21 → Oct 27'.

    fare_from.date_range is rendered verbatim on destination cards;
    ISO dates must never reach readers (holistic audit item 23,
    2026-10-15). Falls back to the input on an unexpected shape."""
    try:
        dep, ret = [p.strip() for p in (iso_range or "").split("→")]
        d1 = datetime.strptime(dep, "%Y-%m-%d")
        d2 = datetime.strptime(ret, "%Y-%m-%d")
        return f"{d1.strftime('%b')} {d1.day} → {d2.strftime('%b')} {d2.day}"
    except Exception:
        return iso_range


def route_cells(r):
    """All calendar cells of a deals route (band-model `calendar`,
    plus legacy `calendars_by_weeks` for pre-2026-10-15 snapshots)."""
    cells = list(r.get("calendar") or [])
    for cal in (r.get("calendars_by_weeks") or {}).values():
        cells.extend(cal or [])
    return cells


def intl_destination_fares(slug, intl_deals):
    """fare_from from the WEEKLY international matrix, or None.

    These fares are indicative (checked weekly at reduced depth) and
    the record says so — the rail card renders the cadence label.
    """
    airport = INTL_AIRPORT_MAP.get(slug)
    if not airport or not intl_deals:
        return None
    fare_from = None
    for rk, r in (intl_deals.get("routes") or {}).items():
        if r.get("destination") != airport:
            continue
        co = r.get("cheapest_overall")
        if co and (fare_from is None
                   or co["price_min"] < fare_from["price_min"]):
            fare_from = {
                "price_min": co["price_min"],
                "route": rk,
                "origin_metro": r.get("origin_metro"),
                "dest_metro": r.get("dest_metro"),
                "date_range": reader_date_range(co.get("date_range")),
                "duration_days": co.get("duration_days"),
                "as_of": intl_deals.get("as_of"),
                "cadence": "weekly",
                "indicative": True,
            }
    return fare_from


def destination_fares(slug, deals, intl_deals=None):
    """fare_from + cheapest_month for a destination, from real deals data.

    Returns (fare_from, cheapest_month). Both None when no tracked route
    serves this destination or the route has no fare data yet.
    India destinations read the daily India matrix (own-metro routes
    only, per ROUTE_MAP); international destinations read the weekly
    intl matrix (INTL_AIRPORT_MAP).
    """
    if slug in INTL_AIRPORT_MAP:
        return intl_destination_fares(slug, intl_deals), None
    route_keys = ROUTE_MAP.get(slug)
    if not route_keys or not deals:
        return None, None
    routes = deals.get("routes") or {}
    fare_from = None
    cheapest = None
    for rk in route_keys:
        r = routes.get(rk)
        if not r:
            continue
        co = r.get("cheapest_overall")
        if co and (fare_from is None or co["price_min"] < fare_from["price_min"]):
            fare_from = {
                "price_min": co["price_min"],
                "route": rk,
                "origin_metro": r.get("origin_metro"),
                "dest_metro": r.get("dest_metro"),
                "date_range": reader_date_range(co.get("date_range")),
                "duration_days": co.get("duration_days"),
                "weeks": co.get("weeks"),
                "as_of": deals.get("as_of"),
                "cadence": "daily",
            }
        for cell in route_cells(r):
            if cell.get("cheapest_month"):
                cand = {"month": cell["month"], "year": cell["year"],
                        "price_min": cell["price_min"], "route": rk,
                        "duration_days": cell.get("duration_days"),
                        "weeks": cell.get("weeks"),
                        "source": "fare data"}
                if cheapest is None or cand["price_min"] < cheapest["price_min"]:
                    cheapest = cand
    return fare_from, cheapest


def destination_drop(slug, deals):
    """Best current fare drop for a destination's mapped routes, or None."""
    route_keys = ROUTE_MAP.get(slug)
    if not route_keys or not deals:
        return None
    for d in deals.get("biggest_drops") or []:
        if d["route"] in route_keys:
            return d
    best = None
    routes = deals.get("routes") or {}
    for rk in route_keys:
        r = routes.get(rk)
        if not r:
            continue
        for cell in route_cells(r):
            ch = cell.get("change_vs_prev") or {}
            if ch.get("delta", 0) > 0 and (best is None or
                                          ch["delta_pct"] > best["drop_pct"]):
                best = {"route": rk, "drop_pct": ch["delta_pct"],
                        "drop_abs": ch["delta"], "was": ch["prev_price_min"],
                        "now": cell["price_min"],
                        "baseline_as_of": ch.get("prev_as_of")}
    return best


def trending_for(rec, month, year, drop):
    """Transparent trending score for `month` with labeled components."""
    best = rec["best_months"]
    peak = rec["peak_months"]
    fit = season_fit(month, best)
    components = []

    if fit == 2:
        components.append({"id": "season_fit", "points": 50, "max": 50,
                           "reason": "In its best season right now"})
        season_pts = 50
    elif fit == 1:
        components.append({"id": "season_fit", "points": 30, "max": 50,
                           "reason": "Shoulder season — season is starting/ending"})
        season_pts = 30
    else:
        components.append({"id": "season_fit", "points": 10, "max": 50,
                           "reason": "Off season this month"})
        season_pts = 10

    if fit == 1:
        value_pts, value_reason = 20, "Shoulder season: good conditions, lower demand and prices"
    elif fit == 2 and month in peak:
        value_pts, value_reason = 8, "Peak demand month — expect top prices and crowds"
    elif fit == 2:
        value_pts, value_reason = 15, "In season without peak-month demand"
    else:
        value_pts, value_reason = 5, "Off season — cheapest, but conditions are a compromise"
    components.append({"id": "offpeak_value", "points": value_pts, "max": 20,
                       "reason": value_reason})

    if drop:
        drop_pts = min(30, round(drop["drop_pct"] * 1.5))
        components.append({
            "id": "fare_drop", "points": drop_pts, "max": 30,
            "reason": (f"Fares down {drop['drop_pct']}% on {drop['route']} "
                       f"(${drop['was']} → ${drop['now']}) vs {drop['baseline_as_of']}")})
    elif rec["slug"] in ROUTE_MAP:
        components.append({"id": "fare_drop", "points": 0, "max": 30,
                           "reason": "Fare route tracked, no notable drop right now"})
    else:
        components.append({"id": "fare_drop", "points": None, "max": 30,
                           "reason": "No fare route tracked for this destination yet"})

    scored = [c for c in components if c["points"] is not None]
    return {
        "month": month,
        "year": year,
        "score": sum(c["points"] for c in scored),
        "max_score": sum(c["max"] for c in scored),
        "components": components,
    }


# ── India country card for the /travel trending rail ────────────────
# Kiran (2026-10-15): India belongs in the "Top Destinations" scroll
# like Australia/Bali — but there is NO /travel/india country page and
# India has NO trending rank. The rail APPENDS this card after the
# data-ranked cards; it carries no "#N Trending" badge, is never in
# trending_now / best_by_month, and its score never influences any
# ranking. The card links to the on-page India Destinations section
# (the 9 state guides), not to a guide page.
#
# Everything on the card is derived from real data at build time:
#   - best/peak months: months a MAJORITY of the 9 India state records
#     list as best/peak (the winter core — Oct–Mar today).
#   - fare_from: cheapest tracked fare from the rail's anchor origin
#     (ANCHOR_ORIGIN — the site default the other cards' fare lines
#     use) to ANY of the five India metros, across the daily matrix
#     (flight-deals.json, cadence "daily") and the weekly metros grid
#     (flight-deals-metros.json, cadence "weekly"). The winning file's
#     cadence + as_of ride along so the stamp stays honest.
#   - season components: the same season_fit math as trending_for(),
#     computed on the derived months — the "In season now" chip is
#     earned by the data or not shown at all.
INDIA_METROS = {"DEL", "BOM", "BLR", "HYD", "CCU"}
INDIA_CARD_ORIGIN = "SFO"


def _majority_months(records, field):
    counts = {}
    for r in records:
        for m in r[field]:
            counts[m] = counts.get(m, 0) + 1
    return sorted(m for m, c in counts.items() if c * 2 > len(records))


def india_card_fare(deals, metros_deals):
    """Cheapest ANCHOR_ORIGIN -> India-metro fare across both matrices."""
    best = None
    for source, cadence in ((deals, "daily"), (metros_deals, "weekly")):
        if not source:
            continue
        for rk, r in (source.get("routes") or {}).items():
            if r.get("origin") != INDIA_CARD_ORIGIN:
                continue
            if r.get("destination") not in INDIA_METROS:
                continue
            co = r.get("cheapest_overall")
            if not co:
                continue
            if best is None or co["price_min"] < best["price_min"]:
                best = {
                    "price_min": co["price_min"],
                    "route": rk,
                    "origin_metro": r.get("origin_metro"),
                    "dest_metro": r.get("dest_metro"),
                    "date_range": reader_date_range(co.get("date_range")),
                    "duration_days": co.get("duration_days"),
                    "as_of": source.get("as_of"),
                    "cadence": cadence,
                }
                if cadence == "weekly":
                    best["indicative"] = True
    return best


def india_card_trending(best_months, peak_months, month, year, deals,
                        metros_deals):
    """Season/value components for the India card — same labeled math
    as trending_for(), computed on the derived country months. The
    fare_drop component scans both matrices' biggest_drops plus the
    daily cells' change_vs_prev for India-metro routes."""
    fit = season_fit(month, best_months)
    components = []
    if fit == 2:
        components.append({"id": "season_fit", "points": 50, "max": 50,
                           "reason": "In its best season right now"})
    elif fit == 1:
        components.append({"id": "season_fit", "points": 30, "max": 50,
                           "reason": "Shoulder season — season is starting/ending"})
    else:
        components.append({"id": "season_fit", "points": 10, "max": 50,
                           "reason": "Off season this month"})

    if fit == 1:
        value_pts, value_reason = 20, "Shoulder season: good conditions, lower demand and prices"
    elif fit == 2 and month in peak_months:
        value_pts, value_reason = 8, "Peak demand month — expect top prices and crowds"
    elif fit == 2:
        value_pts, value_reason = 15, "In season without peak-month demand"
    else:
        value_pts, value_reason = 5, "Off season — cheapest, but conditions are a compromise"
    components.append({"id": "offpeak_value", "points": value_pts, "max": 20,
                       "reason": value_reason})

    drop = None
    for source in (deals, metros_deals):
        if not source:
            continue
        for d in source.get("biggest_drops") or []:
            rk = d.get("route") or ""
            if rk.split("-")[-1] in INDIA_METROS and (
                    drop is None or d["drop_pct"] > drop["drop_pct"]):
                drop = d
    if drop is None and deals:
        for rk, r in (deals.get("routes") or {}).items():
            if r.get("destination") not in INDIA_METROS:
                continue
            for cell in route_cells(r):
                ch = cell.get("change_vs_prev") or {}
                if ch.get("delta", 0) > 0 and (
                        drop is None or ch["delta_pct"] > drop["drop_pct"]):
                    drop = {"route": rk, "drop_pct": ch["delta_pct"],
                            "drop_abs": ch["delta"], "was": ch["prev_price_min"],
                            "now": cell["price_min"],
                            "baseline_as_of": ch.get("prev_as_of")}
    if drop:
        components.append({
            "id": "fare_drop",
            "points": min(30, round(drop["drop_pct"] * 1.5)), "max": 30,
            "reason": (f"Fares down {drop['drop_pct']}% on {drop['route']} "
                       f"(${drop['was']} → ${drop['now']}) vs {drop['baseline_as_of']}")})
    else:
        components.append({"id": "fare_drop", "points": 0, "max": 30,
                           "reason": "Fare routes tracked, no notable drop right now"})

    scored = [c for c in components if c["points"] is not None]
    return {
        "month": month,
        "year": year,
        "score": sum(c["points"] for c in scored),
        "max_score": sum(c["max"] for c in scored),
        "components": components,
    }


def build_india_card(records, deals, metros_deals, today):
    """The India country card for the trending rail (see block comment
    above). Returns None when there are no India records to derive
    from. NOT a destination record: it stays out of `destinations`,
    `trending_now` and `best_by_month`, and destination_count."""
    india_records = [r for r in records if r["group"] == "india"]
    if not india_records:
        return None
    best_months = _majority_months(india_records, "best_months")
    peak_months = _majority_months(india_records, "peak_months")
    return {
        "slug": "india",
        "name": "India",
        "guide_url": "/travel#india-destinations",
        "group": "india",
        "eligible_for_picks": False,
        "region": "Asia",
        "best_months": best_months,
        "peak_months": peak_months,
        "season_note": ("The winter core (Oct–Mar) suits most of India; "
                        "Kashmir and the Himalayas run spring to autumn."),
        "cheapest_month": None,
        "fare_from": india_card_fare(deals, metros_deals),
        "highlights": [{
            "title": "Delhi, Mumbai, Bengaluru, Hyderabad & Kolkata gateways",
            "snippet": ("State guides for the trip home — Goa, Kerala, "
                        "Karnataka, Rajasthan, Kashmir and more, one tap below."),
        }],
        "photo_count": 0,
        "hero_image": None,
        "trending": india_card_trending(best_months, peak_months,
                                        today.month, today.year,
                                        deals, metros_deals),
        "data_quality": {
            "fare_data": "tracked",
            "notes": ["Country card for the trending rail (Kiran, "
                      "2026-10-15): derived from the India state records "
                      "and the fare matrices; carries no trending rank "
                      "and links to the on-page India Destinations "
                      "section, not a guide."],
        },
    }


# ── Shadow trending (pilot, 2026-10-15) ─────────────────────────────
# Rebalanced score from research/actual-trending-data-2026-10-15.md §4:
# season 40 / search_interest 30 / fare 20 / value 10, computed from
# pipeline/.state/search-interest.json (fetch-search-interest.py).
# SHADOW ONLY: writes pipeline/.state/trending-shadow.json and NEVER
# touches the live records, scores or trending_now. The daily
# flight-deals job runs this same script — the shadow step is wrapped
# so it cannot break or alter the live build.
SEARCH_INTEREST_FILE = REPO / "pipeline" / ".state" / "search-interest.json"
SHADOW_FILE = REPO / "pipeline" / ".state" / "trending-shadow.json"


def _momentum_points(momentum, scale):
    """Map a momentum fraction onto `scale` points (half scale = flat).

    -50% or worse -> 0; flat -> scale/2; +50% or better -> scale.
    """
    frac = min(1.0, max(0.0, 0.5 + momentum))
    return round(scale * frac)


def shadow_search_component(rec, search_entry, wiki_levels):
    """search_interest (0-30) for one destination, or a null component.

    15 pts level + 15 pts momentum. Google Trends is preferred; while
    it has no data, Wikimedia pageviews feed BOTH halves (its absolute
    counts give a real level, log-normalized across this run's cohort).
    With Trends momentum only, momentum stretches across both halves
    until anchored level data exists — marked in the reason either way.
    """
    if not search_entry:
        return {"id": "search_interest", "points": None, "max": 30,
                "reason": "No search-interest data yet"}, None, None, None
    trends = search_entry.get("trends") or {}
    blended = trends.get("blended_momentum")
    if blended is not None:
        pts = _momentum_points(blended, 30)
        return ({"id": "search_interest", "points": pts, "max": 30,
                 "reason": (f"Search interest momentum {blended:+.0%} "
                            f"(US/IN blend, Google Trends)")},
                "google-trends", None, blended)
    wiki = search_entry.get("wiki") or {}
    momentum = wiki.get("momentum")
    if momentum is not None:
        mom_pts = _momentum_points(momentum, 15)
        level_pts = 0
        recent_mean = wiki.get("recent_mean")
        if recent_mean and wiki_levels:
            import math
            lo, hi = wiki_levels
            if hi > lo and recent_mean > 0:
                level_pts = round(15 * (math.log(recent_mean) - lo) / (hi - lo))
        return ({"id": "search_interest", "points": level_pts + mom_pts,
                 "max": 30,
                 "reason": (f"Wikipedia attention {momentum:+.0%} vs prior "
                            f"quarter ({recent_mean:,.0f} views/day)")},
                "wikimedia", recent_mean, momentum)
    return {"id": "search_interest", "points": None, "max": 30,
            "reason": "No search-interest data yet"}, None, None, None


def build_shadow_ranking(records, search_data):
    """Shadow ranking for pick-eligible records. Pure: mutates nothing."""
    import math
    entries = (search_data or {}).get("destinations") or {}
    wiki_means = [e["wiki"]["recent_mean"] for e in entries.values()
                  if e.get("wiki") and e["wiki"].get("recent_mean")]
    wiki_levels = None
    if len(wiki_means) >= 2:
        logs = [math.log(v) for v in wiki_means if v > 0]
        if logs:
            wiki_levels = (min(logs), max(logs))

    shadow = []
    for rec in records:
        if not rec["eligible_for_picks"]:
            continue
        live = {c["id"]: c for c in rec["trending"]["components"]}
        comps = []
        season_pts = round(live["season_fit"]["points"] * 40 / 50)
        comps.append({"id": "season_fit", "points": season_pts, "max": 40,
                      "reason": live["season_fit"]["reason"]})
        search_comp, signal, level, momentum = shadow_search_component(
            rec, entries.get(rec["slug"]), wiki_levels)
        comps.append(search_comp)
        fare_live = live["fare_drop"]
        if fare_live["points"] is None:
            comps.append({"id": "fare_drop", "points": None, "max": 20,
                          "reason": fare_live["reason"]})
        else:
            comps.append({"id": "fare_drop",
                          "points": round(fare_live["points"] * 20 / 30),
                          "max": 20, "reason": fare_live["reason"]})
        comps.append({"id": "offpeak_value",
                      "points": round(live["offpeak_value"]["points"] * 10 / 20),
                      "max": 10, "reason": live["offpeak_value"]["reason"]})
        scored = [c for c in comps if c["points"] is not None]
        shadow.append({
            "slug": rec["slug"],
            "name": rec["name"],
            "score": sum(c["points"] for c in scored),
            "max_score": sum(c["max"] for c in scored),
            "components": comps,
            "signal_source": signal,
            "has_fare_data": rec["fare_from"] is not None,
            "search_level": level,
            "search_momentum": momentum,
        })

    def sort_key(s):
        # Ties: (1) has fare data, (2) has search data, (3) higher search
        # level (falling back to momentum), (4) name — last resort only.
        lvl = s["search_level"] if s["search_level"] is not None \
            else s["search_momentum"]
        return (-s["score"],
                0 if s["has_fare_data"] else 1,
                0 if s["signal_source"] else 1,
                -(lvl if lvl is not None else 0),
                s["name"])

    shadow.sort(key=sort_key)
    top8 = shadow[:8]
    boundary = top8[-1]["score"] if top8 else None
    stats = {
        "top8": [s["slug"] for s in top8],
        "distinct_scores_in_top8": len({s["score"] for s in top8}),
        "largest_tie_group_in_top8": max(
            (sum(1 for s in top8 if s["score"] == sc) for sc in
             {s["score"] for s in top8}), default=0),
        "tied_at_top8_boundary": sum(
            1 for s in shadow if boundary is not None
            and s["score"] == boundary),
        "shadow_with_search_data": sum(1 for s in shadow if s["signal_source"]),
    }
    return shadow, stats


def write_shadow(records):
    """Compute + write the shadow ranking. Never raises into the build."""
    search_data = None
    if SEARCH_INTEREST_FILE.exists():
        search_data = json.loads(SEARCH_INTEREST_FILE.read_text())
    ranking, stats = build_shadow_ranking(records, search_data)
    out = {
        "generated_at": date.today().isoformat(),
        "mode": "SHADOW — live trending_now is NOT affected by this file",
        "weights": {"season_fit": 40, "search_interest": 30,
                    "fare_drop": 20, "offpeak_value": 10},
        "tie_break": "score desc, has fare data, has search data, "
                     "search level/momentum desc, name (last resort)",
        "search_interest_as_of": (search_data or {}).get("generated_at"),
        "stats": stats,
        "ranking": ranking,
    }
    SHADOW_FILE.write_text(json.dumps(out, indent=2))
    print(f"   Shadow trending (pilot): {', '.join(stats['top8'][:5])} "
          f"[{stats['shadow_with_search_data']} with search data]")


def main():
    parser = argparse.ArgumentParser(description="Build travel-destinations.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today = date.today()
    galleries = {}
    if GALLERIES_FILE.exists():
        galleries = json.loads(GALLERIES_FILE.read_text())
    deals = None
    if DEALS_FILE.exists():
        deals = json.loads(DEALS_FILE.read_text())
    metros_deals = None
    if METROS_DEALS_FILE.exists():
        metros_deals = json.loads(METROS_DEALS_FILE.read_text())
    intl_deals = None
    if INTL_DEALS_FILE.exists():
        intl_deals = json.loads(INTL_DEALS_FILE.read_text())

    records = []
    missing_meta = []
    for md_path in sorted(GUIDES_DIR.glob("*.md")):
        slug = md_path.stem
        meta = META.get(slug)
        if not meta:
            missing_meta.append(slug)
            continue
        group, region, best_months, peak_months, season_note = meta
        text = md_path.read_text()
        highlights = mine_highlights(text)
        gal = galleries.get(slug) or {}
        photos = gal.get("photos") or []
        fare_from, cheapest_month = destination_fares(slug, deals,
                                                      intl_deals)
        drop = destination_drop(slug, deals)

        rec = {
            "slug": slug,
            "name": NAME_OVERRIDES.get(slug, slug.replace("-", " ").title()),
            "guide_url": f"/travel/{slug}",
            "group": group,
            "eligible_for_picks": pick_eligible(slug, group),
            "region": region,
            "best_months": best_months,
            "peak_months": peak_months,
            "season_note": season_note,
            "cheapest_month": cheapest_month,
            "fare_from": fare_from,
            "highlights": highlights,
            "photo_count": len(photos),
            "hero_image": photos[0]["src"] if photos else None,
            "season_fit_by_month": {str(m): season_fit(m, best_months)
                                    for m in range(1, 13)},
            "data_quality": {
                "fare_data": "tracked" if fare_from else "none",
                "guide_highlights": len(highlights),
                "notes": [],
            },
        }
        if slug in ROUTE_MAP and not fare_from:
            rec["data_quality"]["notes"].append(
                "Fare route mapped but no fare data in the latest snapshot")
        if slug not in ROUTE_MAP:
            rec["data_quality"]["notes"].append(
                "No flight-deals route tracked yet — fare fields are null by design")
        if len(highlights) < 3:
            rec["data_quality"]["notes"].append(
                "Guide has fewer than 3 structured highlights to mine")
        if not rec["eligible_for_picks"]:
            rec["data_quality"]["notes"].append(
                "Second-tier US destination (Kiran 2026-10-14 tiering): "
                "guide stays in the full index, excluded from curated "
                "picks and trending rankings for now")
        rec["trending"] = trending_for(rec, today.month, today.year, drop)
        records.append(rec)

    if missing_meta:
        print(f"⚠ Guides with no metadata (skipped): {missing_meta}", file=sys.stderr)

    # Deterministic rankings for the frontend — pick-eligible records
    # only (tiering scope above); ineligible records stay in the file.
    eligible = [r for r in records if r["eligible_for_picks"]]
    trending_now = [r["slug"] for r in sorted(
        eligible, key=lambda r: (-r["trending"]["score"], r["name"]))]
    best_by_month = {}
    for m in range(1, 13):
        ranked = sorted(
            eligible,
            key=lambda r: (-r["season_fit_by_month"][str(m)],
                           -r["trending"]["score"], r["name"]))
        best_by_month[str(m)] = [r["slug"] for r in ranked
                                 if r["season_fit_by_month"][str(m)] > 0]

    out = {
        "generated_at": today.isoformat(),
        "current_month": today.month,
        "current_year": today.year,
        "destination_count": len(records),
        "legend": {
            "season_fit_by_month": "2 = in best season, 1 = shoulder (adjacent month), 0 = off season",
            "trending": "Sum of labeled components; max_score shows what was computable — a null fare_drop component means no fare route is tracked, not a zero fare.",
            "cheapest_month": "Only set from real flight-deals fare data; null everywhere else by design.",
            "eligible_for_picks": "False = second-tier US destination deferred from curated picks/trending (Kiran 2026-10-14 tiering); the record and its guide remain in the full index.",
        },
        "trending_now": trending_now,
        "best_by_month": best_by_month,
        "destinations": records,
        # Country card for the /travel trending rail (Kiran, 2026-10-15)
        # — separate from `destinations` on purpose: it is not a guide,
        # not ranked, and destination_count stays the guide count.
        "india_card": build_india_card(records, deals, metros_deals, today),
    }

    if args.dry_run:
        print(f"{len(records)} destinations; top trending: {trending_now[:5]}")
        for r in records[:3]:
            print(json.dumps(r, indent=2)[:1200])
        return

    OUTPUT_FILE.write_text(json.dumps(out, indent=2))
    print(f"✅ Wrote {OUTPUT_FILE} ({len(records)} destinations)")
    print(f"   Trending now: {', '.join(trending_now[:5])}")

    # Shadow trending pilot — must never break or alter the live build.
    try:
        write_shadow(records)
    except Exception as e:
        print(f"⚠ Shadow trending skipped (live build unaffected): {e}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
