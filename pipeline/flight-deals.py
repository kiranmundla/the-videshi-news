#!/usr/bin/env python3
"""
Flight deals price fetcher for The Videshi. (Phase B)

Searches Duffel for round-trip fares on US-India routes and writes
price data for the frontend price calendar, plus a snapshot history
used for fare-drop detection ("down $X since <date>" is the return
trigger — deals are the #1 reason readers come back).

Specs (Kiran's decisions):
- Max 1 stop (no 2+ stops)
- Round-trip, per person, economy
- Exclude basic economy — only fares with 2+ checked bags
- Discovery only: honest price ranges with as-of timestamps,
  direct links, no affiliates
- Departure sampling defaults to Tue/Wed/Thu (cheapest days to fly)

Scope (Kiran, 2026-10-15 — Travel Phase 1: get one thing right, expand
later): rolling next 3 months, ONE duration band per market instead of
the old 2/3/4-week grid:
- India matrix (default): ~3-week trips — durations sampled inside
  19-23 days; the cell value is the cheapest fare found in the band
  and the cell reports the winning trip's actual dates + duration.
  12 routes x 3 months x 2 departure samples x 2 duration samples
  = 144 requests max — inside the observed daily provider ceiling
  (~283 requests before the 2026-10-15 run aborted at the old scope).
- International matrix (--intl, weekly): top non-India destinations
  (TYO/MCT/CDG/FCO/NAN/ATH/SYD/CAI/DPS/HNL/SJD) x 5 origins, ~1-week
  trips (5-9 days), same sampling shape = 660 requests max per week,
  run sliced per destination across the week (single-route runs
  merge into the snapshot). Writes
  a SEPARATE snapshot (flight-deals-intl.json) labelled weekly /
  indicative; the daily India job never touches it.

History: every run appends one JSON line per route/month/duration cell
to pipeline/.state/flight-deals-history.jsonl. Drops are computed vs the
previous snapshot for the same cell, and vs the trailing average once
>=3 prior snapshots exist. The Phase 1 output (2026-10-11) seeds the
first baseline honestly (baseline_as_of is carried on every drop).

Usage:
  python3 flight-deals.py --all                      (full Tier-1+2 India matrix)
  python3 flight-deals.py --tier 1                   (Tier-1 only)
  python3 flight-deals.py --route SFO-DEL            (single India route)
  python3 flight-deals.py --all --dry-run            (search + print, no writes)
  python3 flight-deals.py --all --samples 3          (denser dep sampling)
  python3 flight-deals.py --intl                     (weekly international matrix)
  python3 flight-deals.py --intl --route SFO-SYD     (single intl route)
  python3 flight-deals.py --metros                   (daily slice of the
        India metros grid: the 38 origin x metro pairs the daily core
        does not cover, refreshed on a weekly rhythm — see
        select_metros_slice; separate flight-deals-metros.json)
  python3 flight-deals.py --all --resume             (skip searches that
        already have a fresh cached response; finish an interrupted run
        spending requests only on the missing searches. Resume runs
        process routes with cells MISSING from the current snapshot
        first — a run that dies at the provider limit advances the
        unfinished tail instead of re-verifying finished routes — and
        the cache TTL defaults to 48h so responses survive the daily
        boundary. Cells completed from cache keep their true fetch
        date in `fetched_as_of` (snapshot + history), never today's.)

Rate-limit etiquette (honor the provider's own signals, never circumvent):
live searches are PACED — a minimum interval between live request
starts (default 7s ≈ 8.6/min, headroom under Duffel's published
10-requests/60s search limit; --pace-seconds or DUFFEL_PACE_SECONDS,
0 disables) is the PRIMARY defense, so runs spread their requests
instead of bursting into the per-user throttle whose retry_after
escalates to 3600s. Cache replays are never paced. As BACKSTOP, a
response carrying the per-user limit WITH a retry_after is honored —
the run pauses for the stated duration (plus small jitter) and resumes
the SAME run, up to a bounded pause budget (default: max 10 pauses or
20 minutes of total waiting per invocation). A hard 429 WITHOUT a
retry_after signal, an auth error, or an exhausted pause budget aborts
the run: nothing is written (existing flight-deals.json stays intact)
and the exit code is non-zero.
"""

import argparse
import json
import os
import random
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

# Tier 1 (research: build first) — (origin, destination, origin_metro, dest_metro)
TIER1_ROUTES = [
    ("SFO", "DEL", "Bay Area", "Delhi"),
    ("SFO", "BLR", "Bay Area", "Bengaluru"),
    ("JFK", "DEL", "New York", "Delhi"),
    ("JFK", "BOM", "New York", "Mumbai"),
    ("ORD", "DEL", "Chicago", "Delhi"),
    ("DFW", "HYD", "Dallas", "Hyderabad"),
]

# Tier 2 (research)
TIER2_ROUTES = [
    ("LAX", "DEL", "Los Angeles", "Delhi"),
    ("SEA", "DEL", "Seattle", "Delhi"),
    ("EWR", "BOM", "New York", "Mumbai"),
    ("IAD", "DEL", "Washington DC", "Delhi"),
    ("ATL", "DEL", "Atlanta", "Delhi"),
    ("BOS", "DEL", "Boston", "Delhi"),
]

ALL_ROUTES = TIER1_ROUTES + TIER2_ROUTES

# Duration bands (Kiran, 2026-10-15): one band per market. The band is
# sampled at 2 durations spread across [min_days, max_days]; the cell
# keeps the cheapest fare found and reports its actual duration_days.
BAND_INDIA = {"id": "in-3wk", "label": "~3-week trips", "center_days": 21,
              "min_days": 19, "max_days": 23}
BAND_INTL = {"id": "intl-1wk", "label": "~1-week trips", "center_days": 7,
             "min_days": 5, "max_days": 9}

# International matrix (weekly): the trending top destinations x 5
# diaspora-metro origins. Destination-major order (trending rank) so
# an interrupted run works the list in the order readers care about.
# Slugs are travel-destinations.json ids. Expanded 2026-10-16
# (Kiran): the original top-8 list predated the real-signal trending
# flip and missed the rail's top — Tokyo (japan #1), Muscat (oman #2)
# and Rome (italy #4) added; Bali/Cabo/Egypt/Hawaii kept at Kiran's
# word. 11 destinations x 5 origins x 3 months x 2 samples x 2
# durations = 660 requests per full sweep — run as per-destination
# route batches (single-route runs merge) sliced across the week,
# never as one run.
INTL_ORIGINS = [
    ("SFO", "Bay Area"),
    ("LAX", "Los Angeles"),
    ("JFK", "New York"),
    ("ORD", "Chicago"),
    ("DFW", "Dallas"),
]
INTL_DESTINATIONS = [  # (airport, metro, destination slug)
    ("TYO", "Tokyo", "japan"),
    ("MCT", "Muscat", "oman"),
    ("CDG", "Paris", "france"),
    ("FCO", "Rome", "italy"),
    ("NAN", "Nadi", "fiji"),
    ("ATH", "Athens", "greece"),
    ("SYD", "Sydney", "australia"),
    ("CAI", "Cairo", "egypt"),
    ("DPS", "Bali", "bali"),
    ("HNL", "Honolulu", "hawaii"),
    ("SJD", "Cabo", "cabo"),
]
INTL_ROUTES = [(o, d, om, dm)
               for d, dm, _slug in INTL_DESTINATIONS
               for o, om in INTL_ORIGINS]
INTL_AIRPORT_SLUG = {d: slug for d, _dm, slug in INTL_DESTINATIONS}

# India metros grid (weekly cadence via daily slices — Kiran,
# 2026-10-15, "India Metros Scroll"): the full 10-origin x 5-metro
# India grid the daily core does NOT cover. The core's 12 routes stay
# daily; these 38 pairs refresh on a weekly rhythm through a small
# daily slice (see select_metros_slice), so the week's ~456 searches
# never hit the provider's per-user wall in one sitting. Same India
# band semantics as the core (BAND_INDIA); the output is a SEPARATE
# snapshot labelled weekly / indicative, and the frontend merges it
# UNDER the daily data (daily wins per route — see lib/flightDeals.ts).
METROS_ORIGINS = [
    ("SFO", "Bay Area"),
    ("LAX", "Los Angeles"),
    ("SEA", "Seattle"),
    ("JFK", "New York"),
    ("EWR", "New York"),
    ("ORD", "Chicago"),
    ("DFW", "Dallas"),
    ("IAD", "Washington DC"),
    ("ATL", "Atlanta"),
    ("BOS", "Boston"),
]
METROS_DESTS = [
    ("DEL", "Delhi"),
    ("BOM", "Mumbai"),
    ("BLR", "Bengaluru"),
    ("HYD", "Hyderabad"),
    ("CCU", "Kolkata"),
]
CORE_ROUTE_KEYS = {f"{o}-{d}" for o, d, _om, _dm in ALL_ROUTES}
METROS_ROUTES = [(o, d, om, dm)
                 for o, om in METROS_ORIGINS
                 for d, dm in METROS_DESTS
                 if f"{o}-{d}" not in CORE_ROUTE_KEYS]
METROS_SLICE_SIZE = 6      # routes per daily slice (~72 searches)
METROS_REFRESH_DAYS = 7    # weekly rhythm: data staleness / no-fare rest

DATA_DIR = Path.home() / "workspace" / "the-videshi-news" / "public" / "data"
STATE_DIR = Path.home() / "workspace" / "the-videshi-news" / "pipeline" / ".state"
OUTPUT_FILE = DATA_DIR / "flight-deals.json"
HISTORY_FILE = STATE_DIR / "flight-deals-history.jsonl"
INTL_OUTPUT_FILE = DATA_DIR / "flight-deals-intl.json"
INTL_HISTORY_FILE = STATE_DIR / "flight-deals-intl-history.jsonl"
INTL_RUN_STATE_FILE = STATE_DIR / "flight-deals-intl-run-state.json"
METROS_OUTPUT_FILE = DATA_DIR / "flight-deals-metros.json"
METROS_HISTORY_FILE = STATE_DIR / "flight-deals-metros-history.jsonl"
METROS_RUN_STATE_FILE = STATE_DIR / "flight-deals-metros-run-state.json"
METROS_STATE_FILE = STATE_DIR / "flight-deals-metros-state.json"

MIN_LEAD_DAYS = 2          # earliest departure = today + 2 days
MIDWEEK = (1, 2, 3)        # Tue, Wed, Thu (date.weekday(): Mon=0)
DROP_MIN_PCT = 4.0         # a drop is "notable" at >= 4% ...
DROP_MIN_ABS = 40          # ... and >= $40 vs the previous snapshot

# Festival seasons: id, name, window, book_by_months (research doc §2/§5)
FESTIVAL_SEASONS = [
    {
        "id": "diwali-2026",
        "name": "Diwali",
        "emoji": "🪔",
        "start": (2026, 11, 6),
        "end": (2026, 11, 10),
        "book_by_months": 4,
        "note": "5-day festival",
    },
    {
        "id": "thanksgiving-2026",
        "name": "Thanksgiving",
        "emoji": "🦃",
        "start": (2026, 11, 25),
        "end": (2026, 11, 29),
        "book_by_months": 2,
        "note": "Long-weekend trips",
    },
    {
        "id": "christmas-2026",
        "name": "Christmas & New Year",
        "emoji": "🎄",
        "start": (2026, 12, 20),
        "end": (2027, 1, 5),
        "book_by_months": 5,
        "note": "Peak holiday season",
    },
    {
        "id": "holi-2027",
        "name": "Holi",
        "emoji": "🎨",
        "start": (2027, 3, 22),
        "end": (2027, 3, 22),
        "book_by_months": 2,
        "note": "Shoulder season — moderate fares",
    },
    {
        "id": "diwali-2027",
        "name": "Diwali",
        "emoji": "🪔",
        "start": (2027, 10, 29),
        "end": (2027, 11, 2),
        "book_by_months": 4,
        "note": "5-day festival",
    },
]

REQUEST_COUNT = 0
FAILED_COUNT = 0
ABORTED = False
ABORT_REASON = None
CACHE_MODE = False
RESUME_MODE = False
# Cached responses younger than this are reusable by --resume. 48h = two
# daily cycles: a response fetched on day N must still be reusable when
# day N+1's run reaches it (the job cadence is 24h, and a long run plus
# rate-limit pauses can push reuse past the 24h mark — at 24h the cache
# expired exactly when the tail routes needed it, starving them forever).
# Prices served from cache are honestly dated via each cell's
# fetched_as_of, so the longer TTL never masquerades as fresh data.
RESUME_TTL_S = 48 * 3600
RESUMED_COUNT = 0
ATTEMPTED = {}  # route_key -> searches with a cache file present (cache mode)
# Per-route search accounting for the CURRENT process, used by the
# metros grid to stamp honest attempt outcomes: route_key ->
# {"attempted": searches that produced a response (live, resumed or
# replayed), "failed": searches that errored / were rate-limited}.
ROUTE_SEARCH_STATS = {}


def note_route_search(route_key, failed=False):
    stats = ROUTE_SEARCH_STATS.setdefault(
        route_key, {"attempted": 0, "failed": 0})
    stats["attempted"] += 1
    if failed:
        stats["failed"] += 1
COMPLETED_ROUTES = []
COMPLETED_CELLS = []  # "ROUTE:YYYY-MM:<band-id>" per finished calendar cell
RUN_STATE_FILE = STATE_DIR / "flight-deals-run-state.json"

# Injectable for tests.
SLEEP_FN = time.sleep
NOW_FN = time.monotonic
JITTER_FN = lambda: random.uniform(0, 5)  # noqa: E731


class PauseBudget:
    """Bounded rate-limit pause budget for one invocation.

    A pause is allowed only while BOTH bounds hold: fewer than
    max_pauses pauses taken AND cumulative wait (including the new
    pause) within max_total_wait_s.
    """

    def __init__(self, max_pauses=10, max_total_wait_s=1200):
        self.max_pauses = max_pauses
        self.max_total_wait_s = max_total_wait_s
        self.pauses_taken = 0
        self.total_wait_s = 0.0

    def try_consume(self, wait_s):
        if self.pauses_taken >= self.max_pauses:
            return False
        if self.total_wait_s + wait_s > self.max_total_wait_s:
            return False
        self.pauses_taken += 1
        self.total_wait_s += wait_s
        return True


PAUSES = PauseBudget()

# Pacing (Kiran, 2026-10-15: "Let's pace our queries"). Duffel's
# published search limit is 10 requests/60s; 7s between live request
# starts caps us at ~8.6/min sustained — real headroom, not riding
# the line — and removes the burst pattern that trips the per-user
# throttle with its escalating retry_after. The interval is between
# request STARTS: a search that itself takes >= the interval adds no
# wait at all, so slow provider days pace themselves.
DEFAULT_PACE_SECONDS = 7.0


class Pacer:
    """Minimum spacing between LIVE Duffel request starts.

    Every real provider attempt passes through wait() exactly once
    (in _duffel_search_once — the single choke point shared by the
    daily, --intl and --metros modes). Cache replays never reach it:
    cached work stays free AND instant. The PauseBudget etiquette is
    untouched and remains the backstop for when the provider
    throttles anyway.
    """

    def __init__(self, interval_s=DEFAULT_PACE_SECONDS):
        self.interval_s = max(0.0, float(interval_s))
        self.last_start = None
        self.requests = 0       # live attempts that passed through
        self.total_wait_s = 0.0

    def wait(self):
        """Sleep until >= interval since the previous live request
        start, then stamp this request's start. Returns the seconds
        waited (0 for the first request, and when pacing is off)."""
        now = NOW_FN()
        waited = 0.0
        if self.interval_s > 0 and self.last_start is not None:
            shortfall = self.interval_s - (now - self.last_start)
            if shortfall > 0:
                SLEEP_FN(shortfall)
                waited = shortfall
                now = NOW_FN()
        self.last_start = now
        self.requests += 1
        self.total_wait_s += waited
        return waited


PACER = Pacer()


def resolve_pace_seconds(cli_value):
    """Pacing interval resolution: --pace-seconds beats the
    DUFFEL_PACE_SECONDS env var beats DEFAULT_PACE_SECONDS. An
    unparseable env value is ignored (with a warning) rather than
    crashing a scheduled run."""
    if cli_value is not None:
        return float(cli_value)
    raw = os.environ.get("DUFFEL_PACE_SECONDS")
    if raw:
        try:
            return float(raw)
        except ValueError:
            print(f"  ⚠ DUFFEL_PACE_SECONDS={raw!r} is not a number; "
                  f"using the {DEFAULT_PACE_SECONDS:g}s default",
                  file=sys.stderr)
    return DEFAULT_PACE_SECONDS


def _set_abort(reason):
    global ABORTED, ABORT_REASON
    if not ABORTED:
        ABORTED = True
        ABORT_REASON = reason
        print(f"  🛑 Aborting run: {reason}", file=sys.stderr)


def _parse_retry_after(data):
    """Seconds from a payload's retry_after field, or None."""
    if not isinstance(data, dict):
        return None
    raw = data.get("retry_after")
    if raw is None:
        return None
    try:
        secs = float(raw)
    except (TypeError, ValueError):
        return None
    return secs if secs > 0 else None


def classify_duffel_result(data, returncode, stderr_text):
    """Classify one Duffel attempt. Returns (kind, info):

      ("ok", offers)     — payload ok:true
      ("pause", seconds) — per-user limit WITH retry_after: honor + resume
      ("abort", reason)  — hard 429 without retry_after, or auth error
      ("fail", reason)   — any other failed search (non-fatal, as before)
    """
    if isinstance(data, dict) and data.get("ok"):
        return ("ok", data.get("offers", []))

    err_text = ""
    status = None
    if isinstance(data, dict):
        resp = data.get("response")
        if isinstance(resp, dict):
            err_text = str(resp.get("error") or "")
        if not err_text:
            err_text = str(data.get("error") or data.get("message") or "")
        status = data.get("status")
    blob = (json.dumps(data)[:400] if data is not None else "")
    combined = f"{err_text} {blob} {(stderr_text or '')[:300]}"
    low = combined.lower()

    is_limit = (status == 429 or "429" in combined or "rate_limit" in low
                or "rate limit" in low or "per-user" in low)
    if is_limit:
        retry = _parse_retry_after(data)
        if retry:
            return ("pause", retry)
        return ("abort", "Duffel 429 without a retry_after signal "
                         "(hard rate limit)")

    if isinstance(data, dict):
        return ("fail", f"search not ok: {json.dumps(data)[:200]}")
    err_low = (stderr_text or "").lower()
    if ("401" in err_low or "403" in err_low or "unauthor" in err_low
            or "auth" in err_low):
        return ("abort", f"Duffel auth/permission error: "
                         f"{(stderr_text or '')[:200]}")
    return ("fail", f"search failed (rc={returncode}): "
                    f"{(stderr_text or '')[:200]}")


def cache_file_path(origin, dest, dep_date, ret_date):
    return Path(f"/tmp/duffel-{origin}{dest}-{dep_date}-{ret_date}.json")


def cached_ok_offers(origin, dest, dep_date, ret_date):
    """Offers from a FRESH ok:true cached response for this exact search,
    or None when there is no reusable cache (missing, stale, unparseable,
    or a saved error). This is the persisted per-search completion state
    that --resume builds on: a completed search is never re-spent."""
    tmp = cache_file_path(origin, dest, dep_date, ret_date)
    if not tmp.exists():
        return None
    try:
        if time.time() - tmp.stat().st_mtime > RESUME_TTL_S:
            return None
        data = json.loads(tmp.read_text())
    except Exception:
        return None
    if not data.get("ok"):
        return None
    return data.get("offers", [])


def cached_fetched_date(origin, dest, dep_date, ret_date):
    """ISO date a cached raw response was actually fetched (its file
    mtime), or None if there is no cache file. Provenance for
    cache-served cells: their prices are as of THIS date, not the
    date of the run that reused them."""
    tmp = cache_file_path(origin, dest, dep_date, ret_date)
    try:
        return date.fromtimestamp(tmp.stat().st_mtime).isoformat()
    except Exception:
        return None


def write_run_state(status):
    """Persist run progress (routes/cells completed, pauses, counts) so
    an interrupted invocation leaves a resumable, inspectable record."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        RUN_STATE_FILE.write_text(json.dumps({
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": status,
            "abort_reason": ABORT_REASON,
            "requests_made": REQUEST_COUNT,
            "requests_resumed_from_cache": RESUMED_COUNT,
            "failed": FAILED_COUNT,
            "pauses_taken": PAUSES.pauses_taken,
            "pause_wait_s": round(PAUSES.total_wait_s, 1),
            "pace_interval_s": PACER.interval_s,
            "paced_requests": PACER.requests,
            "pace_wait_s": round(PACER.total_wait_s, 1),
            "routes_completed": list(COMPLETED_ROUTES),
            "cells_completed": sorted(COMPLETED_CELLS),
        }, indent=2))
    except Exception:
        pass


def cache_search(origin, dest, dep_date, ret_date):
    """Cache-mode stand-in for run_duffel_search: replays a raw Duffel
    response saved by an earlier live run. Makes NO API calls. Returns
    offers, [] for a saved error response, or None if no file exists
    (search never attempted)."""
    global REQUEST_COUNT, FAILED_COUNT
    REQUEST_COUNT += 1
    route_key = f"{origin}-{dest}"
    tmp = Path(f"/tmp/duffel-{origin}{dest}-{dep_date}-{ret_date}.json")
    if not tmp.exists():
        return None
    ATTEMPTED[route_key] = ATTEMPTED.get(route_key, 0) + 1
    try:
        data = json.loads(tmp.read_text())
    except Exception:
        FAILED_COUNT += 1
        note_route_search(route_key, failed=True)
        return []
    if not data.get("ok"):
        # The saved response is a FAILED live search — it counts as an
        # attempt but never as evidence for a no-fare conclusion.
        FAILED_COUNT += 1
        note_route_search(route_key, failed=True)
        return []
    note_route_search(route_key)
    return data.get("offers", [])


def _duffel_search_once(origin, dest, dep_date, ret_date, limit=100):
    """One Duffel CLI attempt; returns classify_duffel_result(...).
    REQUEST_COUNT increments per real provider attempt (retries after a
    pause are real requests and are counted as such). This is the single
    choke point for live requests in every mode, so pacing hooks in
    here: PACER.wait() spaces this attempt's start from the previous
    live attempt's start. Cache paths never call this function."""
    global REQUEST_COUNT
    PACER.wait()
    REQUEST_COUNT += 1
    cmd = [
        "duffel", "search",
        "--origin", origin,
        "--destination", dest,
        "--departure-date", dep_date,
        "--return-date", ret_date,
        "--adults", "1",
        "--cabin", "economy",
        "--max-connections", "1",
        "--limit", str(limit),
        "--compact",
    ]
    # Write to temp file (don't pipe, per connector instructions).
    # Ret date in the name: durations share dep dates. The file doubles
    # as the persisted raw-response cache that --resume reuses.
    tmp = cache_file_path(origin, dest, dep_date, ret_date)
    try:
        with open(tmp, "w") as fh:
            result = subprocess.run(cmd, stdout=fh, stderr=subprocess.PIPE,
                                    timeout=180)
    except subprocess.TimeoutExpired:
        return ("fail", "Duffel search timed out")
    stderr_text = (result.stderr.decode(errors="replace")
                   if result.stderr else "")
    data = None
    try:
        data = json.loads(tmp.read_text())
    except Exception:
        data = None
    return classify_duffel_result(data, result.returncode, stderr_text)


def run_duffel_search(origin, dest, dep_date, ret_date, limit=100):
    """Run a Duffel search and return the offers list (None on failure).

    Rate-limit etiquette: a per-user limit carrying retry_after pauses
    the run for the stated duration (+ jitter) and retries the SAME
    search, bounded by PAUSES (max pauses / max total wait). A hard 429
    without retry_after, an auth error, or an exhausted pause budget
    aborts the whole run (nothing is written by main()).
    """
    global FAILED_COUNT
    while True:
        kind, info = _duffel_search_once(origin, dest, dep_date, ret_date,
                                         limit)
        if kind == "ok":
            return info
        if kind == "fail":
            FAILED_COUNT += 1
            print(f"  ❌ {info}", file=sys.stderr)
            return None
        if kind == "abort":
            FAILED_COUNT += 1
            _set_abort(info)
            return None
        # kind == "pause": provider asked us to wait `info` seconds.
        wait = info + JITTER_FN()
        if not PAUSES.try_consume(wait):
            FAILED_COUNT += 1
            _set_abort(
                f"pause budget exhausted ({PAUSES.pauses_taken} pauses, "
                f"{PAUSES.total_wait_s:.0f}s waited) and the provider is "
                f"still rate-limiting")
            return None
        print(f"  ⏸  Duffel per-user limit — pausing {wait:.0f}s "
              f"(pause {PAUSES.pauses_taken}/{PAUSES.max_pauses}, waited "
              f"{PAUSES.total_wait_s:.0f}s of {PAUSES.max_total_wait_s}s "
              f"budget), then resuming the same search",
              file=sys.stderr)
        SLEEP_FN(wait)


def filter_qualifying_offers(offers):
    """
    Filter to qualifying offers per Kiran's specs:
    - 2+ checked bags (excludes basic economy)
    - Max 1 stop per direction (already enforced by search, double-check)
    Returns list of {price, airline, stops, fare_brand, currency}.
    """
    qualifying = []
    for o in offers:
        bags = o.get("bags") or {}
        checked = bags.get("checked") or 0
        if checked < 2:
            continue
        slices = o.get("slices", [])
        max_stops = max((s.get("stops", 0) for s in slices), default=0)
        if max_stops > 1:
            continue
        try:
            price = float(o["price"])
        except (KeyError, ValueError, TypeError):
            continue
        qualifying.append({
            "price": price,
            "airline": o.get("airline", "Unknown"),
            "stops": max_stops,
            "fare_brand": (slices[0].get("fare_brand") if slices else "N/A"),
            "currency": o.get("currency", "USD"),
        })
    return qualifying


def midweek_dates(year, month, min_date):
    """All Tue/Wed/Thu dates in (year, month) on/after min_date."""
    first = date(year, month, 1)
    if month == 12:
        last = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    out = []
    d = first
    while d <= last:
        if d >= min_date and d.weekday() in MIDWEEK:
            out.append(d)
        d += timedelta(days=1)
    return out


def sample_departures(year, month, samples, min_date):
    """Pick `samples` midweek departure dates spread across the month."""
    cands = midweek_dates(year, month, min_date)
    if not cands:
        return []
    if len(cands) <= samples:
        return cands
    picks = []
    for i in range(samples):
        # Middle of each equal slice of the candidate list (spread).
        idx = (2 * i + 1) * len(cands) // (2 * samples)
        picks.append(cands[idx])
    return picks


def rolling_months(months_ahead, min_date):
    """Next `months_ahead` (year, month) pairs that have >=1 sample date."""
    out = []
    y, m = min_date.year, min_date.month
    guard = 0
    while len(out) < months_ahead and guard < 24:
        if midweek_dates(y, m, min_date):
            out.append((y, m))
        m += 1
        if m > 12:
            m, y = 1, y + 1
        guard += 1
    return out


def sample_durations(band, samples):
    """Pick `samples` trip durations (days) spread across the band —
    same middle-of-each-slice spread as sample_departures. India band
    (19-23d, 2 samples) -> [20, 22]; intl band (5-9d) -> [6, 8]."""
    days = list(range(band["min_days"], band["max_days"] + 1))
    if len(days) <= samples:
        return days
    return [days[(2 * i + 1) * len(days) // (2 * samples)]
            for i in range(samples)]


def planned_search_keys(routes, band, months, dep_samples, duration_days,
                        min_date):
    """Every (origin, dest, dep_str, ret_str) a run with these settings
    would search — mirrors find_cheapest_window's sampling exactly, so
    --resume can count how many searches still need live requests."""
    keys = []
    for origin, dest, _om, _dm in routes:
        for (y, m) in months:
            for dep in sample_departures(y, m, dep_samples, min_date):
                for days in duration_days:
                    ret = dep + timedelta(days=days)
                    keys.append((origin, dest, dep.isoformat(),
                                 ret.isoformat()))
    return keys


# ── Resume ordering: incomplete routes first ─────────────────────────
# Stall pattern fixed here (2026-10-15): routes were always processed
# in fixed tier order, so when the provider's per-user limit aborted a
# run mid-matrix it always died at the same place (EWR-BOM, route 9 of
# 12) and the tail routes NEVER completed, while finished routes were
# re-verified every day. On --resume runs the work is now ordered by
# need: routes with cells missing go first.

def cell_id(route_key, year, month, band_id):
    """Cell identity, same format as the run state's cells_completed."""
    return f"{route_key}:{year:04d}-{month:02d}:{band_id}"


def load_json_file(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def snapshot_cell_ids(snapshot):
    """Cell ids present in a flight-deals.json snapshot dict.

    Band-model cells carry `band`. Legacy cells (pre-2026-10-15
    snapshots) carry `weeks` instead — they map to a "legacy-<n>w" id
    that never equals a planned band cell, so a legacy snapshot simply
    reads as fully missing for ordering (every route is fresh work
    under the new scope, which is true: the dates/durations changed).
    """
    ids = set()
    for route_key, r in ((snapshot or {}).get("routes") or {}).items():
        calendars = []
        if r.get("calendar"):
            calendars.append(r["calendar"])
        for cal in (r.get("calendars_by_weeks") or {}).values():
            calendars.append(cal or [])
        for cal in calendars:
            for cell in cal:
                band = cell.get("band") or f"legacy-{cell.get('weeks')}w"
                ids.add(cell_id(route_key, cell["year"], cell["month"],
                                band))
    return ids


def prev_run_cell_ids():
    """Cell ids the previous invocation completed (run state file).
    These count as done for ORDERING even when that run aborted before
    writing a snapshot — the work is backed by cached raw responses and
    completes for free on resume. (The run state's routes_completed is
    NOT used: cache-salvage runs list routes they later drop.)"""
    state = load_json_file(RUN_STATE_FILE) or {}
    return set(state.get("cells_completed") or [])


def planned_cell_ids(route_key, band, months):
    return {cell_id(route_key, y, m, band["id"]) for (y, m) in months}


def order_routes_incomplete_first(routes, band, months,
                                  snapshot=None, prev_cells=None):
    """Order routes for a --resume run: incomplete routes first.

    A route's missing cells = planned cells absent from BOTH the
    current snapshot and the previous run's completed cells. Routes
    with missing cells come first, most-missing first (never-completed
    routes ahead of nearly-finished ones), ties in original tier
    order; fully-covered routes follow in original order to be
    re-verified with whatever request budget remains.
    Returns [(route, missing_count), ...] in processing order.
    """
    have = snapshot_cell_ids(snapshot) | set(prev_cells or [])
    decorated = []
    for idx, route in enumerate(routes):
        route_key = f"{route[0]}-{route[1]}"
        missing = planned_cell_ids(route_key, band, months) - have
        decorated.append((0 if missing else 1, -len(missing), idx,
                          route, len(missing)))
    decorated.sort(key=lambda t: (t[0], t[1], t[2]))
    return [(t[3], t[4]) for t in decorated]


# ── Metros grid: slice state + due selection ─────────────────────────
# The slice state is the grid's durable memory. It lives in
# pipeline/.state (on-disk, survives VM restarts — unlike the /tmp
# response cache), and records every route ATTEMPT with its outcome,
# so confirmed no-fare routes rest instead of being re-burned daily,
# and a route whose cells were computed but lost to an aborted write
# is recognised as still owed (its cached responses make the retry
# nearly free under --resume).

def load_metros_state(path=None):
    state = load_json_file(path or METROS_STATE_FILE)
    if not isinstance(state, dict) \
            or not isinstance(state.get("routes"), dict):
        return {"routes": {}}
    return state


def save_metros_state(state, path=None):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        (path or METROS_STATE_FILE).write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def metros_attempt_outcome(calendar, attempted, failed, planned,
                           aborted):
    """Honest outcome for one grid route's attempt.

    "no_fares" is a CLAIM — the route was genuinely searched end to
    end and nothing qualified — so it requires every planned search
    to have produced a response and none to have failed. Anything
    interrupted (provider abort) or incomplete (searches missing or
    failed) is "attempted": still owed, retried by the next slice,
    never rested for a week as if it had been searched. (First-fill
    bug, 2026-10-15: routes whose first search hit the rate wall —
    and routes merely walked by a --from-cache salvage — were stamped
    no_fares without a single genuine search.)"""
    if aborted:
        return "attempted"
    if calendar:
        return "cells" if failed == 0 else "attempted"
    if planned and attempted >= planned and failed == 0:
        return "no_fares"
    return "attempted"


def record_metros_attempt(route_key, calendar, today_iso, outcome=None,
                          path=None):
    """Persist one route attempt. Called per route as it completes,
    so an abort mid-run never loses the finished routes' records.
    `outcome` comes from metros_attempt_outcome in the runner; the
    None default (legacy derive) exists only for older callers."""
    state = load_metros_state(path)
    newest = max((c.get("fetched_as_of") or "" for c in calendar),
                 default="")
    state["routes"][route_key] = {
        "last_attempt": today_iso,
        "outcome": outcome or ("cells" if calendar else "no_fares"),
        "cells": len(calendar),
        "newest_fetched": newest or None,
    }
    state["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_metros_state(state, path)


def snapshot_route_freshness(snapshot):
    """route_key -> newest fetched_as_of among its snapshot cells
    (None when the route is absent or its calendar is empty)."""
    out = {}
    for route_key, r in ((snapshot or {}).get("routes") or {}).items():
        dates = [c.get("fetched_as_of") for c in (r.get("calendar") or [])
                 if c.get("fetched_as_of")]
        out[route_key] = max(dates) if dates else None
    return out


def _days_between(iso_a, iso_b):
    try:
        return (date.fromisoformat(iso_b) - date.fromisoformat(iso_a)).days
    except Exception:
        return None


def metros_route_due(route_key, freshness, record, today, fill=False):
    """(due, sort_key) for one grid route.

    A route is SATISFIED only by cells in the snapshot: an attempt
    that computed cells but never landed in a written snapshot
    (aborted run) leaves the route due — --resume replays its cached
    responses for free. A no-fare outcome rests the route for
    METROS_REFRESH_DAYS so confirmed-empty pairs are not re-burned
    daily; in fill mode only a SAME-DAY no-fare result rests it
    (older empties are retried — the rolling window has moved).
    Sort order: never-attempted first, then owed/no-data routes by
    oldest attempt, then stale-data routes by oldest data.
    """
    today_iso = today.isoformat()
    newest = freshness.get(route_key)
    last_attempt = (record or {}).get("last_attempt")
    outcome = (record or {}).get("outcome")
    if newest:
        age = _days_between(newest, today_iso)
        if age is not None and age < METROS_REFRESH_DAYS:
            return (False, None)
        return (True, (2, newest))  # stale data — refresh
    if outcome == "no_fares" and last_attempt:
        if fill:
            if last_attempt == today_iso:
                return (False, None)
        else:
            age = _days_between(last_attempt, today_iso)
            if age is not None and age < METROS_REFRESH_DAYS:
                return (False, None)
        return (True, (1, last_attempt))
    if last_attempt:
        # Attempted with cells, but nothing reached the snapshot —
        # the write was aborted; still owed.
        return (True, (1, last_attempt))
    return (True, (0, ""))  # never attempted


def select_metros_slice(routes, snapshot, state, today, slice_size,
                        fill=False):
    """The due subset of the metros grid for one invocation, in work
    order (see metros_route_due). slice_size None/0 = every due route."""
    freshness = snapshot_route_freshness(snapshot)
    records = (state or {}).get("routes") or {}
    due = []
    for idx, route in enumerate(routes):
        route_key = f"{route[0]}-{route[1]}"
        is_due, sort_key = metros_route_due(
            route_key, freshness, records.get(route_key), today, fill=fill)
        if is_due:
            due.append((sort_key, idx, route))
    due.sort(key=lambda t: (t[0], t[1]))
    picked = [r for _sk, _i, r in due]
    if slice_size:
        picked = picked[:slice_size]
    return picked


def find_cheapest_window(origin, dest, year, month, band, dep_samples,
                         duration_days, min_date, sleep_s):
    """
    Find the cheapest trip in a given month within the duration band.
    Samples `dep_samples` midweek departure dates spread across the
    month x each duration in `duration_days` (the band's sampled
    durations). The cell value is the cheapest fare found; the cell
    reports the winning trip's actual dep/ret dates + duration_days.
    Returns a calendar cell dict, or None if no qualifying offers found.
    """
    global RESUMED_COUNT
    dep_dates = sample_departures(year, month, dep_samples, min_date)
    results = []
    for dep in dep_dates:
        if ABORTED:
            break
        for days in duration_days:
            if ABORTED:
                break
            ret = dep + timedelta(days=days)
            dep_str, ret_str = dep.isoformat(), ret.isoformat()
            print(f"    Searching {origin}→{dest} {dep_str} → {ret_str} "
                  f"({days}d)...")
            # Provenance for this sample: live searches are fetched
            # today; cache-served samples keep the response's fetch date.
            sample_fetched = date.today().isoformat()
            sample_from_cache = False
            if CACHE_MODE:
                # cache_search keeps the route search stats itself.
                offers = cache_search(origin, dest, dep_str, ret_str)
                if offers:
                    sample_from_cache = True
                    sample_fetched = (cached_fetched_date(
                        origin, dest, dep_str, ret_str) or sample_fetched)
            elif RESUME_MODE:
                offers = cached_ok_offers(origin, dest, dep_str, ret_str)
                if offers is not None:
                    RESUMED_COUNT += 1
                    note_route_search(f"{origin}-{dest}")
                    sample_from_cache = True
                    sample_fetched = (cached_fetched_date(
                        origin, dest, dep_str, ret_str) or sample_fetched)
                    print("    ↩  fresh cached response reused (resume) — "
                          "no request spent")
                else:
                    offers = run_duffel_search(origin, dest, dep_str,
                                               ret_str)
                    note_route_search(f"{origin}-{dest}",
                                        failed=offers is None)
            else:
                offers = run_duffel_search(origin, dest, dep_str, ret_str)
                note_route_search(f"{origin}-{dest}",
                                  failed=offers is None)
            if not offers:
                continue
            qualifying = filter_qualifying_offers(offers)
            if not qualifying:
                print("    ⚠ No 2-bag offers found")
                continue
            prices = sorted(q["price"] for q in qualifying)
            p25_idx = max(0, int(len(prices) * 0.25) - 1)
            results.append({
                "dep": dep_str,
                "ret": ret_str,
                "duration_days": days,
                "min_price": prices[0],
                "p25_price": prices[p25_idx],
                "num_offers": len(qualifying),
                "cheapest_airline": min(
                    qualifying, key=lambda q: q["price"])["airline"],
                "fetched_as_of": sample_fetched,
                "from_cache": sample_from_cache,
            })
            if sleep_s:
                time.sleep(sleep_s)

    if not results:
        return None

    best = min(results, key=lambda r: r["min_price"])
    all_mins = [r["min_price"] for r in results]
    return {
        "date_range": f"{best['dep']} → {best['ret']}",
        "dep_date": best["dep"],
        "ret_date": best["ret"],
        "duration_days": best["duration_days"],
        "band": band["id"],
        "price_min": round(min(all_mins)),
        "price_max": round(max(r["p25_price"] for r in results)),
        "cheapest_airline": best["cheapest_airline"],
        "num_samples": len(results),
        # Honest freshness: the OLDEST fetch date among the samples this
        # cell aggregates. Live-only cells carry today's date; a cell
        # completed (partly) from cached responses is dated by its
        # oldest cached sample, never silently by the reuse date.
        "fetched_as_of": min(r["fetched_as_of"] for r in results),
        "cache_samples": sum(1 for r in results if r["from_cache"]),
        "year": year,
        "month": month,
    }


# ── History / fare-drop detection ────────────────────────────────────

def cell_key(rec):
    """History identity. Band-model records key on the band id; legacy
    records (pre-2026-10-15, keyed by exact weeks) get a legacy key so
    they never compare against band cells — a band minimum over 19-23
    days is not like-for-like with a fixed 21-day price, so drops
    honestly restart at the scope change."""
    band = rec.get("band") or f"legacy-{rec.get('weeks')}w"
    return (rec["route"], rec["year"], rec["month"], band)


def load_history():
    if not HISTORY_FILE.exists():
        return []
    out = []
    for line in HISTORY_FILE.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def seed_history_from_output():
    """Seed history from the existing flight-deals.json (Phase 1 output).

    Used once, when no history file exists yet. The seed lines carry the
    Phase 1 generated_at/as_of so drop baselines are honestly dated.
    Returns a list of history records (not yet written).
    """
    if not OUTPUT_FILE.exists():
        return []
    try:
        old = json.loads(OUTPUT_FILE.read_text())
    except Exception:
        return []
    gen = old.get("generated_at")
    as_of = old.get("as_of")
    seeds = []
    for route_key, r in (old.get("routes") or {}).items():
        for cell in r.get("calendar") or []:
            seeds.append({
                "observed_at": gen,
                "as_of": as_of,
                "source": "phase1-output-seed",
                "route": route_key,
                "origin": r.get("origin"),
                "destination": r.get("destination"),
                "year": cell["year"],
                "month": cell["month"],
                "band": cell.get("band"),
                "weeks": cell.get("weeks"),
                "duration_days": cell.get("duration_days"),
                "dep_date": cell["dep_date"],
                "ret_date": cell["ret_date"],
                "price_min": cell["price_min"],
                "price_max": cell["price_max"],
                "cheapest_airline": cell.get("cheapest_airline"),
                "num_samples": cell.get("num_samples"),
            })
    return seeds


def compute_changes(cells, history):
    """Annotate each cell with change vs previous snapshot (+ trailing avg).

    cells: list of calendar cell dicts (each has 'route' injected).
    history: prior records only (not including the current run).
    Returns the notable-drops list.
    """
    prev_by_key = {}
    priors_by_key = {}
    for rec in history:
        k = cell_key(rec)
        priors_by_key.setdefault(k, []).append(rec)
        prev_by_key[k] = rec  # file order = chronological; last wins

    drops = []
    for cell in cells:
        k = cell_key(cell)
        prev = prev_by_key.get(k)
        if not prev:
            continue
        delta = prev["price_min"] - cell["price_min"]
        delta_pct = round(100.0 * delta / prev["price_min"], 1) if prev["price_min"] else 0.0
        change = {
            "prev_price_min": prev["price_min"],
            "prev_as_of": prev.get("as_of"),
            "delta": delta,
            "delta_pct": delta_pct,
        }
        priors = priors_by_key.get(k, [])
        if len(priors) >= 3:
            avg = sum(p["price_min"] for p in priors) / len(priors)
            change["trailing_avg_price_min"] = round(avg)
            change["delta_vs_trailing_avg"] = round(avg - cell["price_min"])
            change["delta_vs_trailing_avg_pct"] = (
                round(100.0 * (avg - cell["price_min"]) / avg, 1) if avg else 0.0)
        cell["change_vs_prev"] = change
        if delta >= DROP_MIN_ABS and delta_pct >= DROP_MIN_PCT:
            drops.append({
                "route": cell["route"],
                "origin_metro": cell.get("origin_metro"),
                "dest_metro": cell.get("dest_metro"),
                "year": cell["year"],
                "month": cell["month"],
                "band": cell.get("band"),
                "duration_days": cell.get("duration_days"),
                "date_range": cell["date_range"],
                "was": prev["price_min"],
                "now": cell["price_min"],
                "drop_abs": delta,
                "drop_pct": delta_pct,
                "baseline_as_of": prev.get("as_of"),
                "cheapest_airline": cell.get("cheapest_airline"),
            })
    drops.sort(key=lambda d: (-d["drop_pct"], -d["drop_abs"]))
    return drops


def flag_cheapest(calendar):
    """Flag the cheapest-month cell within one route's band calendar."""
    if not calendar:
        return None
    best = min(calendar, key=lambda c: c["price_min"])
    best["cheapest_month"] = True
    return {
        "year": best["year"], "month": best["month"],
        "band": best.get("band"),
        "duration_days": best.get("duration_days"),
        "price_min": best["price_min"], "date_range": best["date_range"],
    }


# ── Main ─────────────────────────────────────────────────────────────

def resolve_routes(args):
    pool = INTL_ROUTES if args.intl else \
        METROS_ROUTES if args.metros else ALL_ROUTES
    if args.route:
        parts = args.route.split("-")
        if len(parts) != 2:
            print("Route must be like SFO-DEL", file=sys.stderr)
            sys.exit(1)
        metro = next((r for r in pool
                      if r[0] == parts[0] and r[1] == parts[1]), None)
        return [(parts[0], parts[1],
                 metro[2] if metro else parts[0],
                 metro[3] if metro else parts[1])]
    if args.intl:
        return INTL_ROUTES
    if args.metros:
        return METROS_ROUTES
    if args.tier == "1":
        return TIER1_ROUTES
    if args.tier == "2":
        return TIER2_ROUTES
    return ALL_ROUTES


def main():
    parser = argparse.ArgumentParser(description="Fetch flight deal prices via Duffel (Phase B)")
    parser.add_argument("--route", help="Single route like SFO-DEL")
    parser.add_argument("--all", action="store_true", help="All Tier-1 + Tier-2 India routes")
    parser.add_argument("--tier", choices=["1", "2"], help="Only this tier (India matrix)")
    parser.add_argument("--intl", action="store_true",
                        help="International matrix (weekly): top non-India "
                             "destinations x 5 origins, ~1-week band, "
                             "separate output/history/run-state files")
    parser.add_argument("--metros", action="store_true",
                        help="India metros grid (weekly cadence via daily "
                             "slices): the 38 origin x metro pairs the "
                             "daily core does not cover, India band, "
                             "separate output/history/run-state files")
    parser.add_argument("--metros-slice", type=int,
                        default=METROS_SLICE_SIZE,
                        help="Max grid routes per --metros invocation "
                             "(default 6 ≈ 72 searches; 0 = all due)")
    parser.add_argument("--metros-fill", action="store_true",
                        help="First-fill mode for --metros: every route "
                             "missing snapshot cells stays due until it "
                             "produces data or a same-day no-fare result")
    parser.add_argument("--months", type=int, default=3,
                        help="Months ahead to search (default 3 — "
                             "Phase 1 scope, Kiran 2026-10-15)")
    parser.add_argument("--samples", type=int, default=2,
                        help="Departure dates sampled per month (default 2)")
    parser.add_argument("--duration-samples", type=int, default=2,
                        help="Durations sampled inside the band per "
                             "departure date (default 2)")
    parser.add_argument("--max-requests", type=int, default=600,
                        help="Abort if the planned matrix exceeds this many Duffel requests")
    parser.add_argument("--sleep", type=float, default=0.5,
                        help="Seconds to sleep between searches (default 0.5)")
    parser.add_argument("--pace-seconds", type=float, default=None,
                        help="Minimum seconds between live Duffel "
                             "request starts — the pacing interval "
                             "(default: DUFFEL_PACE_SECONDS env var, "
                             "else 7; 0 disables pacing). Cache "
                             "replays are never paced.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print results without writing files")
    parser.add_argument("--from-cache", action="store_true",
                        help="Replay saved Duffel responses from /tmp "
                             "(no API calls). Only routes whose planned "
                             "searches were all attempted are kept.")
    parser.add_argument("--resume", action="store_true",
                        help="Live run, but reuse fresh cached responses "
                             "for searches already completed (no request "
                             "spent on them). Finishes an interrupted run.")
    parser.add_argument("--resume-ttl-hours", type=float, default=48,
                        help="Max age of a cached response for --resume "
                             "reuse (default 48h — spans the daily "
                             "boundary; cache-served cells keep their "
                             "true fetched_as_of date)")
    parser.add_argument("--max-pauses", type=int, default=10,
                        help="Max rate-limit pauses per run (default 10)")
    parser.add_argument("--max-pause-wait-min", type=float, default=20,
                        help="Max total minutes spent paused per run "
                             "(default 20)")
    args = parser.parse_args()

    global CACHE_MODE, RESUME_MODE, RESUME_TTL_S
    global OUTPUT_FILE, HISTORY_FILE, RUN_STATE_FILE
    global PACER
    CACHE_MODE = args.from_cache
    RESUME_MODE = args.resume and not args.from_cache
    RESUME_TTL_S = args.resume_ttl_hours * 3600
    PAUSES.max_pauses = args.max_pauses
    PAUSES.max_total_wait_s = args.max_pause_wait_min * 60
    pace_seconds = resolve_pace_seconds(args.pace_seconds)
    if pace_seconds < 0:
        parser.error("--pace-seconds must be >= 0")
    PACER = Pacer(pace_seconds)
    if args.metros and not CACHE_MODE:
        # Grid runs always resume: slices and provider aborts lean on
        # the response cache, so a route whose snapshot write was
        # aborted completes for free on the next slice.
        RESUME_MODE = True

    if not (args.all or args.tier or args.route or args.intl
            or args.metros):
        print("Specify --all, --tier, --route, --intl, or --metros",
              file=sys.stderr)
        sys.exit(1)

    # Market selection: the matrices share the engine but never share
    # files — the weekly intl run and the metros grid slices must not
    # touch the daily India snapshot, history, or run state.
    if args.intl:
        band = BAND_INTL
        OUTPUT_FILE = INTL_OUTPUT_FILE
        HISTORY_FILE = INTL_HISTORY_FILE
        RUN_STATE_FILE = INTL_RUN_STATE_FILE
    elif args.metros:
        band = BAND_INDIA
        OUTPUT_FILE = METROS_OUTPUT_FILE
        HISTORY_FILE = METROS_HISTORY_FILE
        RUN_STATE_FILE = METROS_RUN_STATE_FILE
    else:
        band = BAND_INDIA
    duration_days = sample_durations(band, args.duration_samples)

    routes = resolve_routes(args)
    today = date.today()
    min_date = today + timedelta(days=MIN_LEAD_DAYS)
    months = rolling_months(args.months, min_date)

    if args.metros and not args.route:
        # Daily-slice selection: only the routes the grid still owes
        # (see select_metros_slice) are worked this invocation.
        grid_snapshot = load_json_file(OUTPUT_FILE)
        grid_state = load_metros_state()
        routes = select_metros_slice(
            routes, grid_snapshot, grid_state, today,
            args.metros_slice or None, fill=args.metros_fill)
        if not routes:
            print("Metros grid: no routes due (grid is fresh or "
                  "resting). Nothing to do.")
            return
        print("Metros slice: "
              + ", ".join(f"{o}-{d}" for o, d, _om, _dm in routes))

    estimate = (len(routes) * len(months) * args.samples
                * len(duration_days))
    print(f"Plan: {len(routes)} routes x {len(months)} months "
          f"x {args.samples} departure samples x {len(duration_days)} "
          f"durations {duration_days} (band {band['id']}: "
          f"{band['min_days']}-{band['max_days']} days) "
          f"= up to {estimate} Duffel requests")
    print(f"Months: {[(y, m) for y, m in months]} | earliest departure {min_date}")
    if CACHE_MODE:
        print("CACHE MODE: replaying saved responses, no Duffel calls.")
    elif PACER.interval_s > 0:
        print(f"Pacing: live Duffel requests spaced "
              f">= {PACER.interval_s:g}s apart (minimum interval "
              f"between request starts; cache replays are never paced)")
    else:
        print("Pacing: OFF (pace interval 0) — live requests fire "
              "back-to-back; the pause budget is the only defense")
    live_needed = estimate
    if RESUME_MODE:
        planned = planned_search_keys(routes, band, months, args.samples,
                                      duration_days, min_date)
        cached_ready = sum(1 for k in planned
                           if cached_ok_offers(*k) is not None)
        live_needed = len(planned) - cached_ready
        print(f"RESUME: {cached_ready}/{len(planned)} planned searches "
              f"already have fresh cached responses; ~{live_needed} live "
              f"searches needed")
    if live_needed > args.max_requests and not CACHE_MODE:
        print(f"❌ Plan needs ~{live_needed} live requests, exceeding "
              f"--max-requests {args.max_requests}; narrow the matrix "
              f"(e.g. --tier 1) or raise the cap.",
              file=sys.stderr)
        sys.exit(2)

    if RESUME_MODE:
        # Incomplete routes first (see order_routes_incomplete_first):
        # if the provider limit kills this run too, the requests it did
        # spend went to the unfinished tail, not to re-verifying routes
        # that are already fully covered.
        snapshot = load_json_file(OUTPUT_FILE)
        ordered = order_routes_incomplete_first(
            routes, band, months, snapshot, prev_run_cell_ids())
        routes = [r for r, _missing in ordered]
        todo = [(f"{r[0]}-{r[1]}", m) for r, m in ordered if m]
        if todo:
            print("RESUME ORDER: routes with missing cells first — "
                  + ", ".join(f"{rk} ({m} cells missing)"
                              for rk, m in todo)
                  + "; fully-covered routes are re-verified afterwards")

    all_data = {
        "generated_at": None,
        "as_of": today.isoformat(),
        "market": ("international" if args.intl
                   else "india-metros" if args.metros else "india"),
        "band": band,
        "months_ahead": len(months),
        "routes": {},
        "biggest_drops": [],
        "festival_seasons": [] if args.intl else FESTIVAL_SEASONS,
        "spec": {
            "max_stops": 1,
            "trip_type": "round-trip",
            "pricing": "per-person",
            "cabin": "economy",
            "min_checked_bags": 2,
            "note": "Excludes basic economy. Prices are snapshots, not live.",
        },
    }
    if args.intl or args.metros:
        # Honest cadence labelling, in the data itself: these fares are
        # checked weekly at reduced depth — indicative, not a calendar.
        all_data["cadence"] = "weekly"
        all_data["indicative"] = True

    all_cells = []  # every calendar cell this run, with route context
    for origin, dest, origin_metro, dest_metro in routes:
        if ABORTED:
            break
        route_key = f"{origin}-{dest}"
        ROUTE_SEARCH_STATS[route_key] = {"attempted": 0, "failed": 0}
        print(f"\n✈️  {route_key} ({origin_metro} → {dest_metro})")
        calendar = []
        for (y, m) in months:
            if ABORTED:
                break
            print(f"  📅 {y}-{m:02d} ({band['label']})...")
            cell = find_cheapest_window(origin, dest, y, m, band,
                                         args.samples, duration_days,
                                         min_date, args.sleep)
            if cell:
                calendar.append(cell)
            else:
                print(f"  ⚠ No data for {y}-{m:02d} ({band['id']})")
        for cell in calendar:
            cell["route"] = route_key
            cell["origin_metro"] = origin_metro
            cell["dest_metro"] = dest_metro
            all_cells.append(cell)
            COMPLETED_CELLS.append(
                f"{route_key}:{cell['year']}-{cell['month']:02d}:"
                f"{band['id']}")
        print(f"  ✅ {len(calendar)} months of data ({band['id']})")

        all_data["routes"][route_key] = {
            "origin": origin,
            "destination": dest,
            "origin_metro": origin_metro,
            "dest_metro": dest_metro,
            "band": band["id"],
            "calendar": calendar,
            "cheapest_overall": flag_cheapest(calendar),
        }
        if args.intl:
            all_data["routes"][route_key]["destination_slug"] = \
                INTL_AIRPORT_SLUG.get(dest)
        COMPLETED_ROUTES.append(route_key)
        write_run_state("aborted" if ABORTED else "running")
        if args.metros:
            # Per-route, immediately: the record must survive an abort
            # later in this same invocation. The outcome is computed
            # from this route's real search accounting — an aborted or
            # partially-searched route is "attempted" (still owed),
            # never "no_fares".
            stats = ROUTE_SEARCH_STATS.get(
                route_key, {"attempted": 0, "failed": 0})
            outcome = metros_attempt_outcome(
                calendar, stats["attempted"], stats["failed"],
                len(months) * args.samples * len(duration_days), ABORTED)
            record_metros_attempt(route_key, calendar,
                                  today.isoformat(), outcome=outcome)

    if CACHE_MODE:
        planned_per_route = len(months) * args.samples * len(duration_days)
        kept = []
        for rk in list(all_data["routes"]):
            if ATTEMPTED.get(rk, 0) >= planned_per_route:
                kept.append(rk)
            else:
                print(f"  🗑  {rk}: only {ATTEMPTED.get(rk, 0)}/{planned_per_route} "
                      f"searches attempted — route dropped (incomplete)")
                del all_data["routes"][rk]
        all_cells = [c for c in all_cells if c["route"] in kept]

    print(f"\n{'Cache reads' if CACHE_MODE else 'Duffel requests made'}: "
          f"{REQUEST_COUNT} (failed: {FAILED_COUNT})")
    if RESUME_MODE:
        print(f"Searches served from cache (resume): {RESUMED_COUNT}")
    if PAUSES.pauses_taken:
        print(f"Rate-limit pauses taken: {PAUSES.pauses_taken} "
              f"({PAUSES.total_wait_s:.0f}s total wait)")
    if not CACHE_MODE:
        print(f"Pacing: {PACER.requests} live requests paced at "
              f">= {PACER.interval_s:g}s spacing "
              f"({PACER.total_wait_s:.0f}s total pacing wait)")
    if ABORTED:
        print(f"❌ Aborted: {ABORT_REASON}. No files written — "
              "existing flight-deals.json left untouched.", file=sys.stderr)
        write_run_state("aborted")
        sys.exit(3)

    if not all_cells:
        print("❌ No data collected at all. No files written — "
              "existing flight-deals.json left untouched.", file=sys.stderr)
        sys.exit(1)

    all_data["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # Fetch window of the prices in this snapshot. as_of stays the run
    # date (existing convention); these two fields expose the true
    # oldest/newest price fetch so a snapshot partly served from cache
    # never claims all its prices were fetched on as_of.
    fetched_dates = sorted(c["fetched_as_of"] for c in all_cells
                           if c.get("fetched_as_of"))
    if fetched_dates:
        all_data["fetched_as_of_oldest"] = fetched_dates[0]
        all_data["fetched_as_of_newest"] = fetched_dates[-1]

    # History: seed from the old output (once), then compare, then append.
    history = load_history()
    seeds = []
    if not history:
        seeds = seed_history_from_output()
        history = seeds
        if seeds:
            print(f"Seeded history baseline from existing output: "
                  f"{len(seeds)} cells (as_of {seeds[0].get('as_of')})")

    drops = compute_changes(all_cells, history)
    all_data["biggest_drops"] = drops[:12]
    print(f"Notable drops vs previous snapshot: {len(drops)}")
    for d in drops[:12]:
        print(f"  ↓ {d['route']} {d['year']}-{d['month']:02d} "
              f"({d.get('duration_days')}d, {d.get('band')}): "
              f"${d['was']} → ${d['now']} (-${d['drop_abs']}, -{d['drop_pct']}%) "
              f"baseline {d['baseline_as_of']}")

    if args.dry_run:
        print("\n--- DRY RUN (no files written) ---")
        print(json.dumps(all_data, indent=2)[:3000])
        return

    # Append this run's observations to history.
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = all_data["generated_at"]
    run_source = ("flight-deals.py --from-cache (salvaged live run)"
                  if CACHE_MODE else
                  "flight-deals.py --resume" if RESUME_MODE
                  else "flight-deals.py")
    lines = [json.dumps(s) for s in seeds]
    for cell in all_cells:
        lines.append(json.dumps({
            "observed_at": now_iso,
            # The record's as_of dates the PRICE: the day its offers
            # were actually fetched (a cache-served cell keeps its
            # original fetch date), so drop detection never compares
            # prices under a false date.
            "as_of": cell.get("fetched_as_of") or today.isoformat(),
            "source": run_source,
            "route": cell["route"],
            "origin": cell["route"].split("-")[0],
            "destination": cell["route"].split("-")[1],
            "year": cell["year"],
            "month": cell["month"],
            "band": cell.get("band"),
            "duration_days": cell.get("duration_days"),
            "dep_date": cell["dep_date"],
            "ret_date": cell["ret_date"],
            "price_min": cell["price_min"],
            "price_max": cell["price_max"],
            "cheapest_airline": cell.get("cheapest_airline"),
            "num_samples": cell.get("num_samples"),
        }))
    with open(HISTORY_FILE, "a") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"📜 History: appended {len(lines)} lines to {HISTORY_FILE.name}")

    # Write output. Single-route runs merge into the existing file;
    # metros slice runs merge too — a slice must never shrink the
    # grid snapshot to just the routes it worked today.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if (args.route or args.metros) and OUTPUT_FILE.exists():
        existing = json.loads(OUTPUT_FILE.read_text())
        existing["routes"].update(all_data["routes"])
        existing["generated_at"] = all_data["generated_at"]
        existing["as_of"] = all_data["as_of"]
        existing["market"] = all_data["market"]
        existing["band"] = all_data["band"]
        existing["months_ahead"] = all_data["months_ahead"]
        existing["biggest_drops"] = all_data["biggest_drops"]
        existing["festival_seasons"] = all_data["festival_seasons"]
        if args.intl or args.metros:
            existing["cadence"] = "weekly"
            existing["indicative"] = True
        if args.metros:
            # The fetch window must span the MERGED snapshot, not
            # just today's slice — a slice's dates must never make
            # last week's routes look freshly fetched (or vice versa).
            merged_dates = sorted(
                c["fetched_as_of"]
                for r in existing["routes"].values()
                for c in (r.get("calendar") or [])
                if c.get("fetched_as_of"))
            if merged_dates:
                existing["fetched_as_of_oldest"] = merged_dates[0]
                existing["fetched_as_of_newest"] = merged_dates[-1]
        all_data = existing

    OUTPUT_FILE.write_text(json.dumps(all_data, indent=2))
    print(f"✅ Wrote {OUTPUT_FILE}")
    write_run_state("complete")


if __name__ == "__main__":
    main()
