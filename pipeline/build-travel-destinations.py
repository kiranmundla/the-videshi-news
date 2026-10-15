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

Usage:
  python3 build-travel-destinations.py            (write JSON)
  python3 build-travel-destinations.py --dry-run  (print summary only)
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path.home() / "workspace" / "the-videshi-news"
GUIDES_DIR = REPO / "public" / "data" / "travel-guides"
GALLERIES_FILE = REPO / "public" / "data" / "travel-galleries.json"
DEALS_FILE = REPO / "public" / "data" / "flight-deals.json"
OUTPUT_FILE = REPO / "public" / "data" / "travel-destinations.json"

# Which flight-deals routes genuinely serve a guide destination.
# Deliberately conservative: the fare must be FOR that destination.
# US→BOM is not a Goa fare; US→DEL is not a Rajasthan fare.
ROUTE_MAP = {
    "karnataka": ["SFO-BLR", "JFK-BLR", "ORD-BLR", "DFW-BLR",
                  "LAX-BLR", "SEA-BLR", "EWR-BLR", "IAD-BLR",
                  "ATL-BLR", "BOS-BLR"],
}

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


def destination_fares(slug, deals):
    """fare_from + cheapest_month for a destination, from real deals data.

    Returns (fare_from, cheapest_month). Both None when no tracked route
    serves this destination or the route has no fare data yet.
    """
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
                "date_range": co["date_range"],
                "weeks": co["weeks"],
                "as_of": deals.get("as_of"),
            }
        for weeks, cal in (r.get("calendars_by_weeks") or {}).items():
            for cell in cal:
                if cell.get("cheapest_month"):
                    cand = {"month": cell["month"], "year": cell["year"],
                            "price_min": cell["price_min"], "route": rk,
                            "weeks": int(weeks), "source": "fare data"}
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
        for cal in (r.get("calendars_by_weeks") or {}).values():
            for cell in cal:
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
        fare_from, cheapest_month = destination_fares(slug, deals)
        drop = destination_drop(slug, deals)

        rec = {
            "slug": slug,
            "name": NAME_OVERRIDES.get(slug, slug.replace("-", " ").title()),
            "guide_url": f"/travel/{slug}",
            "group": group,
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
        rec["trending"] = trending_for(rec, today.month, today.year, drop)
        records.append(rec)

    if missing_meta:
        print(f"⚠ Guides with no metadata (skipped): {missing_meta}", file=sys.stderr)

    # Deterministic rankings for the frontend.
    trending_now = [r["slug"] for r in sorted(
        records, key=lambda r: (-r["trending"]["score"], r["name"]))]
    best_by_month = {}
    for m in range(1, 13):
        ranked = sorted(
            records,
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
        },
        "trending_now": trending_now,
        "best_by_month": best_by_month,
        "destinations": records,
    }

    if args.dry_run:
        print(f"{len(records)} destinations; top trending: {trending_now[:5]}")
        for r in records[:3]:
            print(json.dumps(r, indent=2)[:1200])
        return

    OUTPUT_FILE.write_text(json.dumps(out, indent=2))
    print(f"✅ Wrote {OUTPUT_FILE} ({len(records)} destinations)")
    print(f"   Trending now: {', '.join(trending_now[:5])}")


if __name__ == "__main__":
    main()
