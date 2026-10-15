#!/usr/bin/env python3
"""
Search-interest fetcher for the destination trending pilot (2026-10-15).

Design: goals/flight-deals-price-calendar/research/
        actual-trending-data-2026-10-15.md (read it before changing this).

Two independent signals per destination, both expressed as MOMENTUM —
recent window vs the destination's own prior baseline, so no
cross-destination scaling/stitching is needed at fetch time:

  1. Wikimedia pageviews (PRIMARY today — free, official, no key).
     Per-article daily human views (agent=user) for the destination's
     Wikipedia article(s). momentum = mean(last 28d) / mean(prior 84d) - 1.
     Measures encyclopedic attention, not travel intent — it is the
     interim signal and stays on as a cross-check once Trends lands.

  2. Google Trends via a hosted Apify actor (activates when a token
     lands in ~/workspace/.env.apify as APIFY_TOKEN — Kiran approved
     this route 2026-10-15). Same momentum shape per geo, blended
     US 70% / IN 30%. Absent token = clean skip, never an error.

Outputs:
  pipeline/.state/search-interest.json         latest snapshot
  pipeline/.state/search-interest-history.jsonl  append-only, one line
      per run: {"date", "destinations": {slug: {"trends_momentum",
      "wiki_momentum"}}}

Both live under pipeline/.state/ (gitignored local state, by design).

Usage:
  python3 fetch-search-interest.py            fetch wiki (+ trends if token)
  python3 fetch-search-interest.py --wiki-only
  python3 fetch-search-interest.py --check    validate Apify token/actor
                                              config without fetching
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

REPO = Path.home() / "workspace" / "the-videshi-news"
STATE_DIR = REPO / "pipeline" / ".state"
SNAPSHOT_FILE = STATE_DIR / "search-interest.json"
HISTORY_FILE = STATE_DIR / "search-interest-history.jsonl"
APIFY_ENV_FILE = Path.home() / "workspace" / ".env.apify"

RECENT_DAYS = 28          # "last 4 weeks"
PRIOR_DAYS = 84           # "prior 12 weeks"
# A window counts as usable only if most of its days came back; sparse
# coverage would manufacture momentum out of gaps.
MIN_RECENT_COVERAGE = 21  # of 28
MIN_PRIOR_COVERAGE = 56   # of 84

UA = "TheVideshi/1.0 (search-interest pilot; contact via thevideshi.com)"

# Destination slug -> en.wikipedia article title(s). Multiple titles are
# SUMMED (national-parks' guide is Yellowstone, Grand Canyon & Yosemite).
# A slug maps only where one clean article (or a clean small set) exists —
# the point is a trustworthy attention series, not forced coverage.
WIKI_ARTICLES = {
    # India
    "goa": ["Goa"],
    "kerala": ["Kerala"],
    "karnataka": ["Karnataka"],
    "tamil-nadu": ["Tamil Nadu"],
    "rajasthan": ["Rajasthan"],
    "kashmir": ["Kashmir"],
    "himachal-pradesh": ["Himachal Pradesh"],
    "uttarakhand": ["Uttarakhand"],
    "northeast-india": ["Northeast India"],
    # USA
    "alaska": ["Alaska"],
    "florida": ["Florida"],
    "hawaii": ["Hawaii"],
    "new-york-city": ["New York City"],
    "national-parks": ["Yellowstone National Park",
                       "Grand Canyon National Park",
                       "Yosemite National Park"],
    # International
    "abu-dhabi": ["Abu Dhabi"],
    "dubai": ["Dubai"],
    "oman": ["Oman"],
    "bali": ["Bali"],
    "thailand": ["Thailand"],
    "vietnam": ["Vietnam"],
    "singapore": ["Singapore"],
    "japan": ["Japan"],
    "australia": ["Australia"],
    "new-zealand": ["New Zealand"],
    "fiji": ["Fiji"],
    "maldives": ["Maldives"],
    "sri-lanka": ["Sri Lanka"],
    "cancun": ["Cancún"],
    "riviera-maya": ["Riviera Maya"],
    "puerto-vallarta": ["Puerto Vallarta"],
    "cabo": ["Cabo San Lucas"],
    "mexico": ["Mexico"],
    "aruba": ["Aruba"],
    "bahamas": ["The Bahamas"],
    "jamaica": ["Jamaica"],
    "dominican-republic": ["Dominican Republic"],
    "banff": ["Banff National Park"],
    "france": ["France"],
    "italy": ["Italy"],
    "spain": ["Spain"],
    "portugal": ["Portugal"],
    "greece": ["Greece"],
    "switzerland": ["Switzerland"],
    "scandinavia": ["Scandinavia"],
    "iceland": ["Iceland"],
    "london": ["London"],
    "egypt": ["Egypt"],
    "morocco": ["Morocco"],
    "kenya": ["Kenya"],
    "south-africa": ["South Africa"],
}

# ═══════════════════════════════════════════════════════════════════════
# Apify / Google Trends config — THE one place actor specifics live.
#
# ⚠ UNVERIFIED until a token exists: the actor id and its input field
# names below follow Apify platform conventions and the research doc's
# description of hosted Trends actors, but the exact actor schema can
# only be confirmed against the live API. `python3
# fetch-search-interest.py --check` performs that validation (token
# auth + actor lookup) the moment ~/workspace/.env.apify appears; if
# the actor id or input shape is wrong, fix it HERE and nowhere else.
# ═══════════════════════════════════════════════════════════════════════
APIFY_API_BASE = "https://api.apify.com/v2"
APIFY_TRENDS_ACTOR_ID = "apify/google-trends-scraper"   # ⚠ unverified
APIFY_RUN_TIMEOUT_S = 600
TRENDS_GEOS = {"US": 0.70, "IN": 0.30}   # reader blend (research doc §4)
TRENDS_TIMEFRAME = "today 4-m"           # weekly points cover 4wk + 12wk

# Trends search terms per destination. The research doc's rule is to use
# Trends TOPICS (entity ids) rather than raw keywords wherever the actor
# supports them, to dodge Cabo/Cabo-San-Lucas-style ambiguity. Topic ids
# are curated here; until an entry has one, the term falls back to the
# destination's display name (still a single unambiguous proper noun for
# most of our list). Fill "topic" values during the --check validation
# pass once the actor's topic handling is confirmed.
TRENDS_TERMS = {}   # slug -> {"topic": "<trends topic id>"|None, "term": str}
# (empty = derive term from the destination name at runtime)


def load_destination_names():
    """slug -> display name, from the destinations generator's META."""
    spec = importlib.util.spec_from_file_location(
        "build_travel_destinations",
        REPO / "pipeline" / "build-travel-destinations.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    names = {}
    for slug in mod.META:
        names[slug] = mod.NAME_OVERRIDES.get(
            slug, slug.replace("-", " ").title())
    return names


# ── momentum math (pure; unit-tested) ─────────────────────────────────

def compute_momentum(daily_views, recent_days=RECENT_DAYS,
                     prior_days=PRIOR_DAYS):
    """Momentum from a {date: views} series (or {date: views} subset).

    Windows are anchored on the LATEST date present in the series:
    recent = the `recent_days` ending on that date, prior = the
    `prior_days` immediately before the recent window.

    Returns {"momentum", "recent_mean", "prior_mean",
             "recent_days_present", "prior_days_present"} or None when
    coverage is too thin to trust (missing days are NOT zero-filled —
    a gap must not manufacture a rise or a fall).
    """
    if not daily_views:
        return None
    end = max(daily_views)
    recent_start = end - timedelta(days=recent_days - 1)
    prior_end = recent_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=prior_days - 1)

    recent = [v for d, v in daily_views.items() if recent_start <= d <= end]
    prior = [v for d, v in daily_views.items()
             if prior_start <= d <= prior_end]
    if len(recent) < MIN_RECENT_COVERAGE or len(prior) < MIN_PRIOR_COVERAGE:
        return None
    recent_mean = sum(recent) / len(recent)
    prior_mean = sum(prior) / len(prior)
    if prior_mean <= 0:
        return None
    return {
        "momentum": recent_mean / prior_mean - 1.0,
        "recent_mean": recent_mean,
        "prior_mean": prior_mean,
        "recent_days_present": len(recent),
        "prior_days_present": len(prior),
        "window_end": end.isoformat(),
    }


def momentum_from_weekly(values):
    """Momentum from a weekly interest series (oldest → newest).

    Google Trends interest-over-time at weekly granularity: last 4
    points vs the 12 before them. Values are relative (0-100) but the
    ratio is self-normalized, which is exactly why momentum is the
    design's Trends metric. Returns the momentum fraction or None.
    """
    if not values or len(values) < 16:
        return None
    recent = values[-4:]
    prior = values[-16:-4]
    prior_mean = sum(prior) / len(prior)
    if prior_mean <= 0:
        return None
    return (sum(recent) / len(recent)) / prior_mean - 1.0


# ── Wikimedia pageviews ───────────────────────────────────────────────

def _curl_json(url, timeout=30):
    """GET JSON via curl (urllib/requests fail through this proxy)."""
    r = subprocess.run(
        ["curl", "-sS", "-m", str(timeout), "-A", UA, url],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed ({r.returncode}): {r.stderr.strip()}")
    return json.loads(r.stdout)


def fetch_wiki_daily(article, start, end):
    """Daily human pageviews for one en.wikipedia article.

    Returns {date: views}. Raises on HTTP/parse failure — the caller
    turns that into a null for the destination, never a fake zero.
    """
    title = urllib.parse.quote(article.replace(" ", "_"), safe="")
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
           f"en.wikipedia/all-access/user/{title}/daily/"
           f"{start.strftime('%Y%m%d')}00/{end.strftime('%Y%m%d')}00")
    data = _curl_json(url)
    out = {}
    for item in data.get("items", []):
        ts = item["timestamp"]  # YYYYMMDDHH
        d = date(int(ts[0:4]), int(ts[4:6]), int(ts[6:8]))
        out[d] = item["views"]
    if not out:
        raise RuntimeError(f"no pageview items for {article!r}")
    return out


def fetch_wikimedia(names):
    """slug -> wiki momentum record or None, for every mapped slug."""
    end = date.today() - timedelta(days=1)   # yesterday: last complete day
    start = end - timedelta(days=RECENT_DAYS + PRIOR_DAYS - 1)
    results = {}
    for slug, articles in WIKI_ARTICLES.items():
        if slug not in names:
            continue
        try:
            combined = {}
            for art in articles:
                for d, v in fetch_wiki_daily(art, start, end).items():
                    combined[d] = combined.get(d, 0) + v
            m = compute_momentum(combined)
            if m is None:
                print(f"  wiki {slug}: series too thin — null",
                      file=sys.stderr)
                results[slug] = None
            else:
                results[slug] = {"articles": articles, **m}
        except Exception as e:   # per-destination failure → null, not fatal
            print(f"  wiki {slug}: fetch failed ({e}) — null",
                  file=sys.stderr)
            results[slug] = None
    return results


# ── Google Trends via Apify (token-gated) ─────────────────────────────

def read_apify_token():
    """APIFY_TOKEN from ~/workspace/.env.apify, or None."""
    if not APIFY_ENV_FILE.exists():
        return None
    for line in APIFY_ENV_FILE.read_text().splitlines():
        line = line.strip()
        if line.startswith(("APIFY_TOKEN=", "APIFY_API_TOKEN=")):
            return line.split("=", 1)[1].strip().strip("'\"") or None
    return None


def apify_api(path, token, timeout=30):
    sep = "&" if "?" in path else "?"
    return _curl_json(f"{APIFY_API_BASE}{path}{sep}token={token}",
                      timeout=timeout)


def build_trends_actor_input(slug, name, geo):
    """Actor input for ONE destination + geo (one report).

    Kept deliberately small and in one function: if --check shows the
    actor wants different field names, this is the only place to fix.
    """
    cfg = TRENDS_TERMS.get(slug) or {}
    term = cfg.get("topic") or cfg.get("term") or name
    return {
        "searchTerms": [term],
        "geo": geo,
        "timeRange": TRENDS_TIMEFRAME,
        "category": "Travel",   # ignored by actors that don't support it
    }


def extract_weekly_series(dataset_items):
    """Pull a weekly interest series out of actor dataset items.

    Actor output shapes vary; this accepts the common shapes (an
    interestOverTime / timelineData list of {value|values|interest}).
    Returns a list of floats oldest → newest, or None. If --check
    reveals the real shape differs, fix it here.
    """
    for item in dataset_items or []:
        for key in ("interestOverTime", "timelineData", "timeline",
                    "interest_over_time"):
            series = item.get(key)
            if isinstance(series, list) and series:
                vals = []
                for pt in series:
                    if isinstance(pt, (int, float)):
                        vals.append(float(pt))
                    elif isinstance(pt, dict):
                        v = pt.get("value", pt.get("values", pt.get("interest")))
                        if isinstance(v, list):
                            v = v[0] if v else None
                        if isinstance(v, (int, float)):
                            vals.append(float(v))
                if len(vals) >= 16:
                    return vals
    return None


def fetch_trends(names, token):
    """slug -> {"us_momentum", "in_momentum", "blended"} or None.

    Runs the actor once per destination per geo (momentum needs no
    cross-term anchoring). Any failure → null for that destination.
    """
    results = {}
    actor_path = APIFY_TRENDS_ACTOR_ID.replace("/", "~")
    for slug, name in names.items():
        try:
            per_geo = {}
            for geo in TRENDS_GEOS:
                # Start a run and wait for it (Apify REST v2).
                r = subprocess.run(
                    ["curl", "-sS", "-m", "60", "-X", "POST",
                     "-H", "Content-Type: application/json",
                     "-d", json.dumps(build_trends_actor_input(slug, name, geo)),
                     f"{APIFY_API_BASE}/acts/{actor_path}/runs?token={token}"],
                    capture_output=True, text=True)
                run_data = json.loads(r.stdout).get("data") or {}
                run_id = run_data.get("id")
                if not run_id:
                    raise RuntimeError("actor run did not start")
                # Poll to completion (bounded).
                import time as _time
                deadline = _time.time() + APIFY_RUN_TIMEOUT_S
                status = run_data.get("status")
                dataset_id = run_data.get("defaultDatasetId")
                while status in ("READY", "RUNNING") and _time.time() < deadline:
                    _time.sleep(10)
                    info = apify_api(f"/actor-runs/{run_id}", token).get("data") or {}
                    status = info.get("status")
                    dataset_id = info.get("defaultDatasetId", dataset_id)
                if status != "SUCCEEDED":
                    raise RuntimeError(f"actor run ended {status}")
                items = apify_api(
                    f"/datasets/{dataset_id}/items", token, timeout=60)
                series = extract_weekly_series(
                    items if isinstance(items, list) else items.get("items"))
                m = momentum_from_weekly(series)
                if m is None:
                    raise RuntimeError("no usable interest series in output")
                per_geo[geo] = m
            blended = sum(per_geo[g] * w for g, w in TRENDS_GEOS.items()
                          if g in per_geo)
            weight = sum(w for g, w in TRENDS_GEOS.items() if g in per_geo)
            results[slug] = {
                "us_momentum": per_geo.get("US"),
                "in_momentum": per_geo.get("IN"),
                "blended_momentum": blended / weight if weight else None,
            }
        except Exception as e:
            print(f"  trends {slug}: failed ({e}) — null", file=sys.stderr)
            results[slug] = None
    return results


def check_apify():
    """--check: validate token + actor config. Exit 0 = ready to fetch."""
    token = read_apify_token()
    if not token:
        print(f"No Apify token yet ({APIFY_ENV_FILE} missing or no "
              "APIFY_TOKEN in it). The Wikimedia signal runs regardless; "
              "Trends lights up automatically once the token lands.")
        return 1
    try:
        me = apify_api("/users/me", token).get("data") or {}
        print(f"Token OK — Apify user: {me.get('username', '?')}")
    except Exception as e:
        print(f"Token present but auth check failed: {e}")
        return 1
    actor_path = APIFY_TRENDS_ACTOR_ID.replace("/", "~")
    try:
        actor = apify_api(f"/acts/{actor_path}", token).get("data") or {}
        print(f"Actor OK: {actor.get('name', APIFY_TRENDS_ACTOR_ID)} "
              f"({APIFY_TRENDS_ACTOR_ID})")
        print("Next: run without --check to fetch; if series parsing "
              "fails, adjust extract_weekly_series/build_trends_actor_input "
              "to the actor's real schema.")
        return 0
    except Exception as e:
        print(f"Actor lookup failed for {APIFY_TRENDS_ACTOR_ID}: {e}\n"
              "Fix APIFY_TRENDS_ACTOR_ID in fetch-search-interest.py "
              "(the one config block at the top).")
        return 1


# ── main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch search-interest signals")
    parser.add_argument("--wiki-only", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="validate Apify token/actor config only")
    args = parser.parse_args()

    if args.check:
        return check_apify()

    names = load_destination_names()
    today = date.today()

    print("Fetching Wikimedia pageviews momentum…")
    wiki = fetch_wikimedia(names)
    wiki_ok = sum(1 for v in wiki.values() if v)
    print(f"  wikimedia: {wiki_ok}/{len(wiki)} destinations with data")

    trends = {}
    trends_status = "skipped — --wiki-only"
    token = None if args.wiki_only else read_apify_token()
    if not args.wiki_only:
        if not token:
            trends_status = ("skipped — no Apify token yet "
                             f"({APIFY_ENV_FILE} not present)")
            print(f"Google Trends via Apify: {trends_status}")
        else:
            print("Fetching Google Trends via Apify…")
            trends = fetch_trends(names, token)
            ok = sum(1 for v in trends.values() if v)
            trends_status = f"ok — {ok}/{len(trends)} destinations"
            print(f"  trends: {trends_status}")

    destinations = {}
    for slug in names:
        w = wiki.get(slug)
        t = trends.get(slug)
        destinations[slug] = {
            "wiki": ({"articles": w["articles"],
                      "recent_mean": round(w["recent_mean"], 1),
                      "prior_mean": round(w["prior_mean"], 1),
                      "momentum": round(w["momentum"], 4),
                      "window_end": w["window_end"]} if w else None),
            "trends": ({"us_momentum": (round(t["us_momentum"], 4)
                                        if t["us_momentum"] is not None else None),
                        "in_momentum": (round(t["in_momentum"], 4)
                                        if t["in_momentum"] is not None else None),
                        "blended_momentum": (round(t["blended_momentum"], 4)
                                             if t["blended_momentum"] is not None
                                             else None)} if t else None),
        }

    snapshot = {
        "generated_at": today.isoformat(),
        "windows": {"recent_days": RECENT_DAYS, "prior_days": PRIOR_DAYS,
                    "definition": "momentum = mean(last 28d) / mean(prior 84d) - 1"},
        "sources": {
            "wikimedia": {"status": "ok", "with_data": wiki_ok,
                          "mapped": len(wiki)},
            "google_trends_apify": {"status": trends_status},
        },
        "destinations": destinations,
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))

    history_line = {
        "date": today.isoformat(),
        "destinations": {
            slug: {
                "trends_momentum": (d["trends"]["blended_momentum"]
                                    if d["trends"] else None),
                "wiki_momentum": (d["wiki"]["momentum"] if d["wiki"] else None),
            } for slug, d in destinations.items()
        },
    }
    with HISTORY_FILE.open("a") as f:
        f.write(json.dumps(history_line) + "\n")

    print(f"✅ Wrote {SNAPSHOT_FILE}")
    print(f"   Appended history line for {today.isoformat()} "
          f"({len(destinations)} destinations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
