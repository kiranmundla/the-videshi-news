#!/usr/bin/env python3
"""
daily-happenings-v2.py — Populate the daily_happenings table with today's events
using REAL data sources instead of AI guessing.

Sources:
  1. Sports: TheSportsDB free API (cricket, soccer, tennis)
  2. Bollywood releases: now-in-theaters.json static feed
  3. Earnings: Nasdaq free earnings calendar API
  4. US Markets: Deterministic weekday/holiday check
  5. Indian festivals & US holidays: Static calendar
  6. Happening briefs: GPT-4o-mini generates a concise info article for any
     entry with no matching Videshi article, so every entry links somewhere.

Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (required); OPENAI_API_KEY
(required for brief generation — entries stay unlinked without it).

Usage:
    python3 pipeline/daily-happenings-v2.py --dry-run
    python3 pipeline/daily-happenings-v2.py
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import source_gate  # ≥2-source publish gate (Kiran, 2026-10-14)

PT = timezone(timedelta(hours=-7))  # PDT

def today_pt():
    return datetime.now(PT).strftime("%Y-%m-%d")

def weekday_pt():
    return datetime.now(PT).strftime("%A")

def curl_json(url, timeout=15, headers=None):
    """Fetch JSON via curl. Returns parsed dict/list or None."""
    cmd = ["curl", "-s", "--max-time", str(timeout), url]
    if headers:
        for h in headers:
            cmd.extend(["-H", h])
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        return None


# ── 1. SPORTS (TheSportsDB) ──────────────────────────────────────────────────

# Leagues/events we care about for diaspora audience
CRICKET_KEYWORDS = [
    "india", "ipl", "icc", "world cup", "champions trophy",
    "mlc", "major league cricket", "global super league",
    "the hundred", "asia cup", "t20 world cup",
    "odi world cup", "wtc", "test championship",
]

# Teams with Indian connection or major global events
SOCCER_KEYWORDS = [
    "world cup", "champions league", "euro ", "copa america",
    "india", "mohun bagan", "east bengal",
]

TENNIS_KEYWORDS = [
    "wimbledon", "us open", "australian open", "french open",
    "roland garros",
]

def _is_relevant_cricket(event: dict) -> bool:
    """Check if a cricket event is relevant for diaspora audience.
    
    Only: India matches, ICC events, IPL, MLC. Skip regional/domestic
    leagues (The Hundred, BBL, CPL, Global Super League, county cricket).
    """
    home = (event.get("strHomeTeam") or "").lower()
    away = (event.get("strAwayTeam") or "").lower()
    league = (event.get("strLeague") or "").lower()
    event_name = (event.get("strEvent") or "").lower()
    text = f"{event_name} {league}"

    # Any match involving India national team
    if "india" in home or "india" in away:
        return True

    # ICC events (World Cup, Champions Trophy, WTC, T20 WC)
    if "icc" in text or "world cup" in text or "champions trophy" in text or "world test" in text:
        return True

    # IPL
    if "ipl" in text or "indian premier league" in text:
        return True

    # MLC — US-based, directly relevant to diaspora
    if "mlc" in text or "major league cricket" in text:
        return True

    # Asia Cup
    if "asia cup" in text:
        return True

    # Skip everything else (The Hundred, BBL, CPL, GSL, county, etc.)
    return False

def _is_relevant_soccer(event: dict) -> bool:
    text = f"{event.get('strEvent', '')} {event.get('strLeague', '')}".lower()
    return any(kw in text for kw in SOCCER_KEYWORDS)

def _is_relevant_tennis(event: dict) -> bool:
    text = f"{event.get('strEvent', '')} {event.get('strLeague', '')}".lower()
    return any(kw in text for kw in TENNIS_KEYWORDS)

def _clean_team_name(name: str) -> str:
    """Strip sport suffixes from team names for better article matching.
    e.g. 'West Indies Cricket' → 'west indies', 'India Cricket' → 'india'."""
    name = (name or "").lower().strip()
    for suffix in [" cricket", " football", " soccer", " tennis"]:
        if name.endswith(suffix):
            name = name[: -len(suffix)].strip()
    return name

def _format_sport_label(event: dict) -> str:
    """Build a clean label like 'Zimbabwe vs India 1st T20I'."""
    label = event.get("strEvent", "")
    # Truncate to 60 chars
    return label[:60] if label else ""

def _sport_detail(event: dict) -> str:
    """Build detail like 'Harare Sports Club, Harare'."""
    parts = []
    venue = event.get("strVenue", "")
    city = event.get("strCity", "")
    country = event.get("strCountry", "")
    if venue:
        parts.append(venue)
    if city and city not in (venue or ""):
        parts.append(city)
    elif country and not city:
        parts.append(country)
    return ", ".join(parts)[:120] if parts else None

# ── Sports sources (≥2-source gate, Kiran 2026-10-14) ──────────────────────
# A sports brief's legitimate provenance is (1) the feed it came from — the
# event's own TheSportsDB page (URL format verified live 2026-10-14: HTTP 200,
# page title is the exact event) — plus (2) the competition's OFFICIAL
# fixtures/schedule page. Every official URL below was verified live on
# 2026-10-14 (curl: HTTP 200 and page title/content checked; for JS-app
# shells — FIFA, MLC — the route was confirmed inside the official app's
# own JS bundle). Competitions whose official page could NOT be verified
# are deliberately ABSENT, so their briefs stay suppressed by the gate in
# ensure_happening_briefs() rather than publishing with one source:
#   - UEFA Champions League / UEFA Euro: uefa.com is unreachable from
#     this environment (connection fails outright, retried) — unverifiable.
#   - Copa América: copaamerica.com has no live fixtures/matches page
#     between editions (every candidate route returns a real 404).
#   - Indian Super League (Mohun Bagan / East Bengal club matches):
#     indiansuperleague.com returns 404 for every probed path.
#   - India soccer (AIFF): the-aiff.com returns 404 for every probed
#     fixtures/national-team path.
#   - FIFA Women's World Cup: different tournament path than the men's
#     schedule page below; not yet verified.
# Add a competition only after verifying its official page the same way.

def _sports_official_source(event: dict, sport: str) -> dict | None:
    """The competition's official fixtures/schedule page for an event,
    or None when no verified official page covers it (brief then stays
    suppressed — feed provenance alone is one source)."""
    league = (event.get("strLeague") or "").lower()
    name = (event.get("strEvent") or "").lower()
    text = f"{name} {league}"
    home = (event.get("strHomeTeam") or "").lower()
    away = (event.get("strAwayTeam") or "").lower()

    if sport == "cricket":
        if "indian premier league" in text or re.search(r"\bipl\b", text):
            return {"name": "IPL — Official Fixtures",
                    "url": "https://www.iplt20.com/matches/fixtures"}
        if "major league cricket" in text or re.search(r"\bmlc\b", text):
            return {"name": "Major League Cricket — Official Fixtures",
                    "url": "https://www.majorleaguecricket.com/fixtures"}
        if "asia cup" in text:
            return {"name": "Asian Cricket Council — Official Matches",
                    "url": "https://www.asiancricket.org/matches"}
        if ("icc" in text or "world cup" in text or "champions trophy" in text
                or "world test" in text):
            return {"name": "ICC — Official Fixtures & Results",
                    "url": "https://www.icc-cricket.com/fixtures-results"}
        if "india" in home or "india" in away:
            # Bilateral internationals: India's board publishes the fixtures.
            return {"name": "BCCI — Official Fixtures",
                    "url": "https://www.bcci.tv/fixtures"}
        return None

    if sport == "soccer":
        if "world cup" in text and "women" not in text:
            return {"name": "FIFA World Cup — Official Match Schedule",
                    "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/match-schedule"}
        # Champions League / Euro (UEFA — unverifiable), Copa América (no
        # live fixtures page), India soccer (AIFF — unverifiable): no
        # verified official page, so no second source.
        return None

    if sport == "tennis":
        if "wimbledon" in text:
            return {"name": "Wimbledon — Official Schedule",
                    "url": "https://www.wimbledon.com/en_GB/scores/schedule.html"}
        if "us open" in text:
            return {"name": "US Open — Official Schedule",
                    "url": "https://www.usopen.org/en_US/scores/schedule.html"}
        if "australian open" in text:
            return {"name": "Australian Open — Official Match Schedule",
                    "url": "https://ausopen.com/schedule"}
        if "roland garros" in text or "french open" in text:
            return {"name": "Roland-Garros — Official Order of Play",
                    "url": "https://www.rolandgarros.com/en-us/order-of-play"}
        return None

    return None


def _sports_sources(event: dict, sport: str) -> list[dict]:
    """Provenance for a sports item: the TheSportsDB event page (the feed)
    plus the competition's verified official page when one covers it."""
    sources = []
    event_id = event.get("idEvent")
    if event_id:
        sources.append({
            "name": "TheSportsDB — Event Details",
            "url": f"https://www.thesportsdb.com/event/{event_id}",
        })
    official = _sports_official_source(event, sport)
    if official:
        sources.append(official)
    return sources


def get_sports(date: str) -> list[dict]:
    """Fetch sports events from TheSportsDB."""
    items = []
    
    # Cricket
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={date}&s=Cricket")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_cricket(e):
                items.append({
                    "emoji": "🏏",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
                    "league": e.get("strLeague"),
                    "sources": _sports_sources(e, "cricket"),
                    "start_time_utc": e.get("strTimestamp"),
                    "search_terms": [
                        _clean_team_name(e.get("strHomeTeam")),
                        _clean_team_name(e.get("strAwayTeam")),
                    ],
                })
    
    # Soccer — only FIFA/Champions League/major tournaments
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={date}&s=Soccer")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_soccer(e):
                items.append({
                    "emoji": "⚽",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
                    "league": e.get("strLeague"),
                    "sources": _sports_sources(e, "soccer"),
                    "start_time_utc": e.get("strTimestamp"),
                    "search_terms": [
                        _clean_team_name(e.get("strHomeTeam")),
                        _clean_team_name(e.get("strAwayTeam")),
                    ],
                })
    
    # Tennis — only Grand Slams
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={date}&s=Tennis")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_tennis(e):
                items.append({
                    "emoji": "🎾",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
                    "league": e.get("strLeague"),
                    "sources": _sports_sources(e, "tennis"),
                    "start_time_utc": e.get("strTimestamp"),
                    "search_terms": [],
                })
    
    print(f"  Sports: {len(items)} relevant events")
    return items


# ── 2. BOLLYWOOD RELEASES ────────────────────────────────────────────────────

def get_movie_releases(date: str) -> list[dict]:
    """Check now-in-theaters.json for Indian movies releasing today."""
    items = []
    feed_path = os.path.join(
        os.path.dirname(__file__), "..", "public", "data", "now-in-theaters.json"
    )
    # Normalize path
    feed_path = os.path.normpath(feed_path)
    if not os.path.exists(feed_path):
        # Try alternate location
        feed_path = os.path.join(os.path.dirname(__file__), "public", "data", "now-in-theaters.json")
    
    try:
        with open(feed_path) as f:
            movies = json.load(f)
        if not isinstance(movies, list):
            movies = movies.get("movies", movies.get("items", []))
    except (FileNotFoundError, json.JSONDecodeError):
        print("  Movies: could not load now-in-theaters.json")
        return []
    
    for m in movies:
        rel_date = m.get("release_date", "")
        if rel_date == date:
            lang = m.get("language", "")
            is_indian = m.get("is_indian", False) or lang in ("Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Marathi", "Punjabi")
            title = m.get("title", "")
            
            if is_indian:
                label = f"Bollywood Movie Release: {title}"
            else:
                label = f"Movie Release: {title}"
            
            link = f"/movies/{m['slug']}" if m.get("slug") else None
            
            items.append({
                "emoji": "🎬",
                "label": label[:60],
                "detail": "Theaters",
                "category": "entertainment",
                "start_time_utc": None,
                "link": link,
                "search_terms": [title.lower()],
                "movie": {
                    "title": title,
                    "language": lang,
                    "genre": m.get("genre", ""),
                    "director": m.get("director", ""),
                    "cast": (m.get("cast") or [])[:4],
                    "release_date": rel_date,
                    "slug": m.get("slug"),
                    "poster_url": m.get("poster_url"),
                    "ticket_url": m.get("ticket_url"),
                },
            })
    
    print(f"  Movies: {len(items)} releasing today")
    return items


# ── 3. EARNINGS ──────────────────────────────────────────────────────────────

# Prominent US/global companies — skip Indian companies per user request
EARNINGS_WATCHLIST = {
    # FAANG+ / Big Tech
    "AAPL", "GOOGL", "GOOG", "AMZN", "META", "NFLX", "MSFT", "NVDA", "TSLA",
    # Indian-CEO companies (US-listed)
    "ADBE", "IBM",
    # Big banks
    "JPM", "BAC", "GS", "MS", "C", "WFC", "AXP",
    # Tech
    "CRM", "ORCL", "INTC", "AMD", "QCOM", "AVGO", "MU", "NOW", "SNOW",
    "UBER", "ABNB", "COIN", "SQ", "PYPL", "SHOP",
    # Consumer
    "KO", "PEP", "PG", "NKE", "DIS", "SBUX", "MCD", "WMT", "TGT", "COST",
    # Healthcare
    "JNJ", "UNH", "PFE", "LLY", "ABBV", "MRK",
    # Payments
    "V", "MA",
    # Energy / Industrial
    "XOM", "CVX", "BA", "CAT", "HON", "GE",
    # Telecom
    "T", "VZ", "CMCSA", "TMUS",
    # Other notable
    "BRK.B", "NEE", "HCA", "CHTR", "BKNG", "MMM",
}

NASDAQ_EARNINGS_CALENDAR_URL = "https://www.nasdaq.com/market-activity/earnings?date={date}"

# Investor-relations pages for watchlist companies. Every URL verified live on
# 2026-10-13 (HTTP 200 via curl, or rendered in a real browser where the site
# bot-blocks curl). A ticker with no verified IR URL stays ABSENT, so the
# source gate in ensure_happening_briefs() suppresses its earnings briefs
# rather than publishing with an unverified or missing second source.
# ABBV, CAT and CMCSA were absent from 2026-10-13 (unverifiable then) until
# 2026-10-17, when all three rendered live in a real browser and were added.
# Add new entries only after verifying the URL.
EARNINGS_IR_URLS = {
    "AAPL": "https://investor.apple.com/",
    "GOOGL": "https://abc.xyz/investor/",
    "GOOG": "https://abc.xyz/investor/",
    "AMZN": "https://ir.aboutamazon.com/",
    "META": "https://investor.atmeta.com/",
    "NFLX": "https://ir.netflix.net/",
    "MSFT": "https://www.microsoft.com/en-us/investor",
    "NVDA": "https://investor.nvidia.com/",
    "TSLA": "https://ir.tesla.com/",
    "ADBE": "https://www.adobe.com/investor-relations.html",
    "IBM": "https://www.ibm.com/investor",
    "JPM": "https://www.jpmorganchase.com/ir",
    "BAC": "https://investor.bankofamerica.com/",
    "GS": "https://www.goldmansachs.com/investor-relations",
    "MS": "https://www.morganstanley.com/about-us-ir",
    "C": "https://www.citigroup.com/global/investors",
    "WFC": "https://www.wellsfargo.com/about/investor-relations/",
    "AXP": "https://ir.americanexpress.com/",
    "CRM": "https://investor.salesforce.com/",
    "ORCL": "https://investor.oracle.com/",
    "INTC": "https://www.intc.com/",
    "AMD": "https://ir.amd.com/",
    "QCOM": "https://investor.qualcomm.com/",
    "AVGO": "https://investors.broadcom.com/",
    "MU": "https://investors.micron.com/",
    "NOW": "https://investors.servicenow.com/",
    "SNOW": "https://investors.snowflake.com/",
    "UBER": "https://investor.uber.com/",
    "ABNB": "https://investors.airbnb.com/",
    "COIN": "https://investor.coinbase.com/",
    "SQ": "https://investors.block.xyz/",
    "PYPL": "https://investor.pypl.com/",
    "SHOP": "https://investors.shopify.com/",
    "KO": "https://investors.coca-colacompany.com/",
    "PEP": "https://www.pepsico.com/investors",
    "PG": "https://www.pginvestor.com/",
    "NKE": "https://investors.nike.com/",
    "DIS": "https://thewaltdisneycompany.com/investor-relations/",
    "SBUX": "https://investor.starbucks.com/",
    "MCD": "https://corporate.mcdonalds.com/corpmcd/investors.html",
    "WMT": "https://stock.walmart.com/",
    "TGT": "https://corporate.target.com/investors",
    "COST": "https://investor.costco.com/",
    "JNJ": "https://www.investor.jnj.com/",
    "UNH": "https://www.unitedhealthgroup.com/investors.html",
    "PFE": "https://www.pfizer.com/about/investors",
    "LLY": "https://investor.lilly.com/",
    "MRK": "https://www.merck.com/investor-relations/",
    "ABBV": "https://investors.abbvie.com/",
    "V": "https://investor.visa.com/",
    "MA": "https://investor.mastercard.com/",
    "XOM": "https://investor.exxonmobil.com/",
    "CVX": "https://www.chevron.com/investors",
    "BA": "https://investors.boeing.com/",
    "HON": "https://investor.honeywell.com/",
    "GE": "https://www.geaerospace.com/investor-relations",
    "CAT": "https://investors.caterpillar.com/",
    "T": "https://investors.att.com/",
    "VZ": "https://www.verizon.com/about/investors/",
    "TMUS": "https://investor.t-mobile.com/",
    "BRK.B": "https://www.berkshirehathaway.com/",
    "NEE": "https://www.investor.nexteraenergy.com/",
    "HCA": "https://investor.hcahealthcare.com/",
    "CHTR": "https://ir.charter.com/",
    "CMCSA": "https://www.cmcsa.com/",
    "BKNG": "https://ir.bookingholdings.com/",
    "MMM": "https://investors.3m.com/",
}

# Source + length gate for generated earnings briefs (2026-10-13): earnings
# briefs previously published with sources=[] and ~110-word bodies against a
# 200-300 word spec. An earnings brief now needs >= EARNINGS_MIN_SOURCES
# attached sources and >= EARNINGS_BRIEF_MIN_WORDS words, or it is suppressed.
EARNINGS_MIN_SOURCES = 2
EARNINGS_BRIEF_MIN_WORDS = 200


def _near_miss_band(words: int) -> bool:
    """True when an earnings brief landed just under the publish floor —
    close enough that one deficit-aware expansion retry can plausibly save
    it (2026-10-20: the 3M brief died at 198/200 after the generic retry)."""
    return EARNINGS_BRIEF_MIN_WORDS - 20 <= words < EARNINGS_BRIEF_MIN_WORDS

def get_earnings(date: str) -> list[dict]:
    """Fetch earnings from Nasdaq calendar API, filtered to watchlist."""
    items = []
    
    data = curl_json(
        f"https://api.nasdaq.com/api/calendar/earnings?date={date}",
        headers=["User-Agent: Mozilla/5.0 (compatible; TheVideshi/1.0)"],
    )
    
    if not data or "data" not in data:
        print("  Earnings: could not fetch Nasdaq calendar")
        return []
    
    rows = data.get("data", {}).get("rows", [])
    if not rows:
        print("  Earnings: no earnings today")
        return []
    
    # Filter to watchlist
    matched = []
    for r in rows:
        symbol = (r.get("symbol") or "").upper()
        if symbol in EARNINGS_WATCHLIST:
            matched.append(r)
    
    if not matched:
        print(f"  Earnings: {len(rows)} total, 0 from watchlist")
        return []
    
    # Sort by name for consistency, show max 3
    matched.sort(key=lambda r: r.get("name", ""))
    
    for r in matched[:3]:
        symbol = r.get("symbol", "")
        name = r.get("name", "")
        # Clean up corporate suffixes for shorter labels
        for suffix in [", Inc.", " Inc.", ", Corp.", " Corp.", " Company", " Limited",
                       ", Ltd.", " Ltd.", " Holdings", ", L.P.", " S.p.A.", " N.V."]:
            name = name.replace(suffix, "")
        name = name.strip().rstrip(",")
        
        time_str = r.get("time", "")
        
        # Parse timing
        if "pre-market" in time_str:
            timing = "Before Market"
        elif "after-hours" in time_str:
            timing = "After Hours"
        else:
            timing = ""
        
        detail = f"{symbol}" + (f" · {timing}" if timing else "")

        # Consensus expectations from the Nasdaq calendar row itself
        # (epsForecast / noOfEsts / lastYearEPS). These are GIVEN facts for
        # the brief prompt — the earnings spec requires the brief to state
        # them (2026-10-21, Kiran: an earnings preview without the number
        # the market expects is half a brief). Never let the writer model
        # invent figures beyond these.
        eps_forecast = (r.get("epsForecast") or "").strip()
        no_of_ests = (r.get("noOfEsts") or "").strip()
        last_year_eps = (r.get("lastYearEPS") or "").strip()
        fiscal_quarter = (r.get("fiscalQuarterEnding") or "").strip()

        # Sources for the generated brief: the Nasdaq calendar (this data's
        # origin) plus the company's verified investor-relations page when we
        # have one. The brief gate in ensure_happening_briefs() requires >= 2.
        sources = [{
            "name": "Nasdaq Earnings Calendar",
            "url": NASDAQ_EARNINGS_CALENDAR_URL.format(date=date),
        }]
        ir_url = EARNINGS_IR_URLS.get(symbol)
        if ir_url:
            sources.append({"name": f"{name} Investor Relations", "url": ir_url})

        items.append({
            "emoji": "📊",
            "label": f"{name} Earnings",
            "detail": detail,
            "category": "markets",
            "kind": "earnings",
            "symbol": symbol,
            "eps_forecast": eps_forecast,
            "no_of_ests": no_of_ests,
            "last_year_eps": last_year_eps,
            "fiscal_quarter": fiscal_quarter,
            "sources": sources,
            "start_time_utc": None,
            "search_terms": [symbol.lower(), name.lower().split()[0]],
        })
    
    print(f"  Earnings: {len(rows)} total, {len(matched)} from watchlist, showing {min(len(matched), 3)}")
    return items


# ── 4. US MARKETS ────────────────────────────────────────────────────────────

US_MARKET_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03",
    "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07",
    "2026-11-26", "2026-12-25",
}

# Official exchange holiday calendars — the canonical sources for a
# market-holiday brief under the ≥2-source gate (Kiran, 2026-10-14). Both
# verified live on 2026-10-14 (curl HTTP 200; titles "Holidays & Trading
# Hours" for NYSE and "US & Nordic Stock Market Schedule" for Nasdaq).
# The holiday determination itself is deterministic (the static calendar
# above), so the two exchanges' own published calendars are the brief's
# provenance — no feed source is claimed.
MARKET_HOLIDAY_SOURCES = [
    {"name": "NYSE — Holidays & Trading Hours",
     "url": "https://www.nyse.com/markets/hours-calendars"},
    {"name": "Nasdaq — U.S. Stock Market Holiday Schedule",
     "url": "https://www.nasdaq.com/market-activity/stock-market-holiday-schedule"},
]

def get_market_status(date: str) -> list[dict]:
    """Only show market status when it's notable (holiday closure)."""
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return []
    
    # Holiday closure is noteworthy
    if d.weekday() < 5 and date in US_MARKET_HOLIDAYS_2026:
        return [{
            "emoji": "🏛️",
            "label": "US Stock Markets Closed (Holiday)",
            "detail": "NYSE, Nasdaq",
            "category": "markets",
            "sources": [dict(s) for s in MARKET_HOLIDAY_SOURCES],
            "start_time_utc": None,
            "search_terms": [],
        }]
    
    # Normal open days — not interesting enough to show
    return []


# ── 5. FESTIVALS & HOLIDAYS ─────────────────────────────────────────────────

FESTIVALS_2026 = {
    # (emoji, label, event-search keyword)
    # Indian festivals (dates for 2026)
    "2026-01-14": ("🪁", "Makar Sankranti / Pongal", "pongal"),
    "2026-01-26": ("🇮🇳", "India Republic Day", "republic day"),
    "2026-03-04": ("🎨", "Holi — Festival of Colors", "holi"),
    "2026-03-19": ("🛕", "Ugadi / Gudi Padwa", "ugadi"),
    "2026-03-26": ("🕉️", "Ram Navami", "ram navami"),
    "2026-04-14": ("🪔", "Baisakhi / Tamil New Year", "baisakhi"),
    "2026-05-01": ("🙏", "Buddha Purnima", "buddha purnima"),
    "2026-05-26": ("☪️", "Eid al-Adha", "eid"),
    "2026-06-16": ("☪️", "Muharram", "muharram"),
    "2026-08-15": ("🇮🇳", "India Independence Day", "independence day"),
    "2026-08-28": ("🪢", "Raksha Bandhan", "raksha bandhan"),
    "2026-09-04": ("🕉️", "Janmashtami", "janmashtami"),
    "2026-09-05": ("📚", "Teachers' Day (India)", "teachers day"),
    "2026-09-14": ("🐘", "Ganesh Chaturthi", "ganesh"),
    "2026-08-26": ("☪️", "Milad un-Nabi", "milad"),
    "2026-10-11": ("🔱", "Navratri Begins", "navratri"),
    "2026-10-20": ("🏹", "Dussehra / Vijayadashami", "dussehra"),
    "2026-11-08": ("🪔", "Diwali — Festival of Lights", "diwali"),
    "2026-11-10": ("🎊", "Bhai Dooj", "bhai dooj"),
    "2026-11-24": ("🕯️", "Guru Nanak Jayanti", "guru nanak"),
    "2026-12-25": ("🎄", "Christmas", "christmas"),
    # US holidays
    "2026-01-01": ("🎆", "New Year's Day", "new year"),
    "2026-01-19": ("✊", "Martin Luther King Jr. Day", "martin luther king"),
    "2026-02-16": ("🇺🇸", "Presidents' Day", "presidents day"),
    "2026-05-25": ("🎖️", "Memorial Day", "memorial day"),
    "2026-06-19": ("✊", "Juneteenth", "juneteenth"),
    "2026-07-04": ("🇺🇸", "Independence Day (USA)", "july 4th"),
    "2026-09-07": ("⚙️", "Labor Day", "labor day"),
    "2026-11-26": ("🦃", "Thanksgiving", "thanksgiving"),
}

# Verified reference sources per festival (≥2-source gate, Kiran
# 2026-10-14) — same pattern as EARNINGS_IR_URLS: every URL below was
# verified live on 2026-10-14 via curl (HTTP 200 AND the fetched page
# title confirms it is about that festival). Keyed by the festival
# keyword from FESTIVALS_2026. A festival with no entry here gets no
# sources and its brief is suppressed by the gate — add entries only
# after verifying both pages the same way.
FESTIVAL_SOURCES = {
    # Makar Sankranti / Pongal
    "pongal": [
        {"name": "Pongal — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Pongal_(festival)"},
        {"name": "Makar Sankranti — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/makar-sankranti/makar-sankranti.html"},
    ],
    "republic day": [
        {"name": "Republic Day (India) — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Republic_Day_(India)"},
        {"name": "Delhi Republic Day Parade — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Delhi_Republic_Day_parade"},
    ],
    "holi": [
        {"name": "Holi — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Holi"},
        {"name": "Holika Dahan — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/holi/holika-dahan.html"},
    ],
    # Ugadi / Gudi Padwa
    "ugadi": [
        {"name": "Ugadi — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Ugadi"},
        {"name": "Gudi Padwa — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/gudi-padwa/gudi-padwa.html"},
    ],
    "ram navami": [
        {"name": "Rama Navami — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Rama_Navami"},
        {"name": "Rama Navami — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/rama-navami/rama-navami.html"},
    ],
    # Baisakhi / Tamil New Year (Puthandu)
    "baisakhi": [
        {"name": "Vaisakhi — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Vaisakhi"},
        {"name": "Puthandu (Tamil New Year) — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Puthandu"},
    ],
    "buddha purnima": [
        {"name": "Vesak — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Vesak"},
        {"name": "Vesak — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Vesak"},
    ],
    "eid": [
        {"name": "Eid al-Adha — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Eid_al-Adha"},
        {"name": "Eid al-Adha — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Eid-al-Adha"},
    ],
    "muharram": [
        {"name": "Muharram — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Muharram"},
        {"name": "Muharram — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Muharram"},
    ],
    "independence day": [
        {"name": "Independence Day (India) — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Independence_Day_(India)"},
        {"name": "Independence Day (India) — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Independence-Day-Indian-holiday"},
    ],
    "raksha bandhan": [
        {"name": "Raksha Bandhan — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Raksha_Bandhan"},
        {"name": "Rakhi — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/rakhi/rakhi.html"},
    ],
    "janmashtami": [
        {"name": "Krishna Janmashtami — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Krishna_Janmashtami"},
        {"name": "Krishna Janmashtami — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/krishna-janmashtami/krishna-janmashtami.html"},
    ],
    "teachers day": [
        {"name": "Teachers' Day — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Teachers%27_Day"},
        {"name": "National Teachers Awards — Ministry of Education, Govt. of India",
         "url": "https://nationalawardstoteachers.education.gov.in/"},
    ],
    "ganesh": [
        {"name": "Ganesh Chaturthi — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Ganesh_Chaturthi"},
        {"name": "Ganesh Chaturthi — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Ganesh-Chaturthi"},
    ],
    "milad": [
        {"name": "Mawlid — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Mawlid"},
        {"name": "Mawlid — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Mawlid"},
    ],
    "navratri": [
        {"name": "Navaratri — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Navaratri"},
        {"name": "Navratri — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/navratri/navratri.html"},
    ],
    "dussehra": [
        {"name": "Vijayadashami — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Vijayadashami"},
        {"name": "Dussehra — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/dussehra/dussehra.html"},
    ],
    "diwali": [
        {"name": "Diwali — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Diwali"},
        {"name": "Diwali — DrikPanchang",
         "url": "https://www.drikpanchang.com/hindu-festivals/diwali/diwali.html"},
    ],
    "bhai dooj": [
        {"name": "Bhai Dooj — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Bhai_Dooj"},
        {"name": "Bhai Dooj — DrikPanchang",
         "url": "https://www.drikpanchang.com/festivals/bhai-dooj/bhai-dooj-date-time.html"},
    ],
    "guru nanak": [
        {"name": "Guru Nanak Gurpurab — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Guru_Nanak_Gurpurab"},
        {"name": "Guru Nanak — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/biography/Guru-Nanak"},
    ],
    "christmas": [
        {"name": "Christmas — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Christmas"},
        {"name": "Christmas — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Christmas"},
    ],
    "new year": [
        {"name": "New Year's Day — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/New_Year%27s_Day"},
        {"name": "New Year Festival — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/New-Year-festival"},
    ],
    "martin luther king": [
        {"name": "Martin Luther King Jr. Day — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Martin_Luther_King_Jr._Day"},
        {"name": "Martin Luther King, Jr., Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Martin-Luther-King-Jr-Day"},
    ],
    "presidents day": [
        {"name": "Presidents' Day — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Presidents%27_Day"},
        {"name": "Presidents' Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Presidents-Day"},
    ],
    "memorial day": [
        {"name": "Memorial Day — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Memorial_Day"},
        {"name": "Memorial Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Memorial-Day"},
    ],
    "juneteenth": [
        {"name": "Juneteenth — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Juneteenth"},
        {"name": "Juneteenth — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Juneteenth"},
    ],
    "july 4th": [
        {"name": "Independence Day (United States) — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Independence_Day_(United_States)"},
        {"name": "Independence Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Independence-Day-United-States-holiday"},
    ],
    # en.wikipedia.org/wiki/Labor_Day currently lands on the international
    # "Labour Day" article (title verified 2026-10-14), so the US pair is
    # Britannica's US-specific Labor Day article + USA.gov's official
    # federal-holidays listing.
    "labor day": [
        {"name": "Labor Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Labor-Day"},
        {"name": "American Holidays — USA.gov",
         "url": "https://www.usa.gov/holidays"},
    ],
    "thanksgiving": [
        {"name": "Thanksgiving (United States) — Wikipedia",
         "url": "https://en.wikipedia.org/wiki/Thanksgiving_(United_States)"},
        {"name": "Thanksgiving Day — Encyclopaedia Britannica",
         "url": "https://www.britannica.com/topic/Thanksgiving-Day"},
    ],
}

def get_festivals(date: str) -> list[dict]:
    """Check if today is a festival or holiday."""
    items = []
    if date in FESTIVALS_2026:
        emoji, label, keyword = FESTIVALS_2026[date]
        items.append({
            "emoji": emoji,
            "label": label,
            "detail": None,
            "category": "news",
            "start_time_utc": None,
            "search_terms": [],
            "festival_key": keyword,
            # Verified reference sources for the ≥2-source gate; a
            # festival missing from FESTIVAL_SOURCES gets [] and its
            # brief is suppressed rather than published source-less.
            "sources": [dict(s) for s in FESTIVAL_SOURCES.get(keyword, [])],
        })
    print(f"  Festivals: {len(items)}")
    return items


# ── Article matching (reused from v1) ────────────────────────────────────────

def _supabase_search(pattern: str, cutoff: str) -> list[dict]:
    """Search published articles by headline ILIKE pattern."""
    import urllib.parse
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return []
    encoded_pattern = urllib.parse.quote(pattern, safe="*")
    query_url = (
        f"{sb_url}/rest/v1/p2_articles"
        f"?select=slug,headline"
        f"&status=eq.published"
        f"&headline=ilike.{encoded_pattern}"
        f"&published_at=gte.{cutoff}"
        f"&order=published_at.desc"
        f"&limit=3"
    )
    r = subprocess.run(
        ["curl", "-s", "--max-time", "10", query_url,
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=15,
    )
    try:
        rows = json.loads(r.stdout)
        return rows if isinstance(rows, list) else []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


def _supabase_search_rows(pattern: str, cutoff: str, limit: int = 5) -> list[dict]:
    """Like _supabase_search but also returns published_at (for ranking)."""
    import urllib.parse
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return []
    encoded_pattern = urllib.parse.quote(pattern, safe="*")
    query_url = (
        f"{sb_url}/rest/v1/p2_articles"
        f"?select=slug,headline,published_at"
        f"&status=eq.published"
        f"&headline=ilike.{encoded_pattern}"
        f"&published_at=gte.{cutoff}"
        f"&order=published_at.desc"
        f"&limit={limit}"
    )
    r = subprocess.run(
        ["curl", "-s", "--max-time", "10", query_url,
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=15,
    )
    try:
        rows = json.loads(r.stdout)
        return rows if isinstance(rows, list) else []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []


# ── Earnings headline gate (2026-10-14) ─────────────────────────────────────
# Incident: Morgan Stanley's Happening Today row linked to the Oct-13 roundup
# "Bank Earnings Kick Off Mixed: JPMorgan Misses, Citi and Goldman Beat" —
# an article with NO Morgan Stanley results (published before MS reported).
# Root cause: match_articles' single-term fallback searched *morgan* and the
# substring matched "JPMorgan" in the roundup headline. Rule from now on: an
# earnings item may only link to an article whose HEADLINE names the company;
# a roundup qualifies only for the companies its headline names. Matching is
# token-based (word boundaries), never substring, so "morgan" inside
# "JPMorgan" can never match Morgan Stanley again.

_CORP_SUFFIX_TOKENS = {"inc", "corp", "corporation", "company", "co", "ltd",
                       "plc", "sa", "nv", "lp", "llc"}
_NAME_STOP_TOKENS = {"and", "the"}
_GENERIC_NAME_TOKENS = {"bank", "of", "first", "national", "global", "capital",
                        "financial", "services", "trust", "united", "american",
                        "america", "group", "holdings", "bancorp"}


def _company_name_tokens(name: str) -> list[str]:
    """Tokenize a company name: lowercase alnum tokens, connectives and
    trailing corporate suffixes dropped ('J P Morgan Chase & Co' ->
    ['j', 'p', 'morgan', 'chase']; 'Bank of America Corporation' ->
    ['bank', 'of', 'america'])."""
    raw = re.findall(r"[a-z0-9]+", (name or "").lower().replace("&", " and "))
    toks = [t for t in raw if t not in _NAME_STOP_TOKENS]
    while toks and toks[-1] in _CORP_SUFFIX_TOKENS:
        toks.pop()
    return toks


def _company_headline_forms(name: str) -> list[list[str]]:
    """Acceptable headline forms for a company name, as token lists:
    the full name; shorter prefixes that still contain a distinctive token
    (e.g. ['j', 'p', 'morgan'] for JPMorgan Chase); and a suffix-stripped
    variant of a single-token name ('citigroup' -> ['citi']). Prefixes made
    only of generic words (['bank'], ['bank', 'of']) are NOT forms — they
    would match any bank headline."""
    toks = _company_name_tokens(name)
    if not toks:
        return []
    forms = [toks]
    for n in range(len(toks) - 1, 0, -1):
        prefix = toks[:n]
        if any(len(t) >= 4 and t not in _GENERIC_NAME_TOKENS for t in prefix):
            forms.append(prefix)
    if len(toks) == 1:
        t = toks[0]
        for suf in ("corporation", "holdings", "bancorp", "group", "corp",
                    "company", "inc"):
            if t.endswith(suf) and len(t) - len(suf) >= 4:
                forms.append([t[: -len(suf)]])
                break
    seen, out = set(), []
    for f in forms:
        k = tuple(f)
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def headline_names_company(headline: str, company_name: str) -> bool:
    """True only if the headline names the company: some accepted form's
    tokens appear consecutively in the headline, or the form's concatenation
    equals ONE whole headline token ('J P Morgan' -> token 'jpmorgan').
    Whole-token equality is what keeps 'JPMorgan' from matching 'Morgan'."""
    h_tokens = re.findall(r"[a-z0-9]+", (headline or "").lower())
    if not h_tokens:
        return False
    h_set = set(h_tokens)
    for form in _company_headline_forms(company_name):
        if "".join(form) in h_set:
            return True
        n = len(form)
        if n > 1 and any(h_tokens[i:i + n] == form
                         for i in range(len(h_tokens) - n + 1)):
            return True
    return False


_EARNINGS_SIGNAL_RE = re.compile(
    r"\b(results?|reports?|reported|quarter(?:ly)?|q[1-4]|eps|earnings|"
    r"revenue|profits?|estimates?|beats?|miss(?:es|ed)?|guidance|outlook)\b")


def headline_has_earnings_signal(headline: str) -> bool:
    """True if the headline is ABOUT an earnings report/results — not merely
    a headline that happens to name the company."""
    return bool(_EARNINGS_SIGNAL_RE.search((headline or "").lower()))


def headline_is_earnings_coverage(headline: str, company_name: str) -> bool:
    """An earnings happening may link ONLY to genuine earnings coverage:
    the headline must name the company (headline_names_company) AND carry an
    earnings signal. The names-only gate (2026-10-14) linked the Netflix
    Earnings row to a Hindi film-premiere roundup whose headline mentioned
    Netflix — same company, wrong subject entirely (2026-10-20)."""
    return (headline_names_company(headline, company_name)
            and headline_has_earnings_signal(headline))


def _company_from_label(label: str) -> str:
    """'Bank of America Corporation Earnings' -> 'Bank of America Corporation'."""
    name = (label or "").strip()
    if name.lower().endswith(" earnings"):
        name = name[: -len(" earnings")].strip()
    return name


# Tokens too common to search on alone (recall patterns only — precision is
# headline_names_company's job). Deliberately smaller than
# _GENERIC_NAME_TOKENS: 'america' must stay searchable or a name made only of
# generic words ('Bank of America') fetches no candidates at all — that hole
# fired a false RESULTS GAP for BAC on the pass's first live run (2026-10-14).
_SEARCH_STOP_TOKENS = {"bank", "first", "national", "global", "capital",
                       "financial", "services", "trust", "united", "group",
                       "holdings", "bancorp"}


def _company_search_patterns(name: str) -> list[str]:
    """ILIKE patterns that fetch candidate articles for a company: each
    searchable name token, the full name as a phrase, and each accepted
    form's concatenation (catches squashed brand tokens like 'jpmorgan').
    Precision comes from headline_names_company(); these only need recall."""
    patterns = []
    toks = _company_name_tokens(name)
    for t in toks:
        if len(t) >= 4 and t not in _SEARCH_STOP_TOKENS:
            patterns.append(f"*{t}*")
    if len(toks) > 1:
        patterns.append("*" + " ".join(toks) + "*")
    for form in _company_headline_forms(name):
        c = "".join(form)
        if len(c) >= 4:
            patterns.append(f"*{c}*")
    return list(dict.fromkeys(patterns))


def _candidate_articles(patterns: list[str], cutoff: str) -> list[dict]:
    """Fetch published-article candidates for a set of ILIKE patterns,
    deduplicated and sorted newest first."""
    seen, rows = set(), []
    for p in patterns:
        for r in _supabase_search_rows(p, cutoff):
            if r.get("slug") and r["slug"] not in seen:
                seen.add(r["slug"])
                rows.append(r)
    rows.sort(key=lambda r: r.get("published_at") or "", reverse=True)
    return rows


def match_articles(items: list[dict]) -> list[dict]:
    """Match happenings to recent Videshi articles or internal pages."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return items

    cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
    matched = 0

    # Stop words for generic matching (team names like "india" are KEPT for sports)
    STOP = {"indian", "world", "cup", "cricket", "open", "league",
            "major", "the", "men", "women", "match", "final", "test",
            "odi", "t20i", "t20"}

    for item in items:
        if item.get("link"):  # Already has a link (e.g. movie slug)
            matched += 1
            continue

        category = item.get("category", "")

        # Festivals now get rich brief hub pages (context + nearby events)
        # via ensure_happening_briefs — no shortcut link here.

        # ── Earnings headline gate (2026-10-14) ──────────────────────────
        # Earnings items link ONLY to an article whose headline names the
        # company (see headline_names_company above). The generic loose-term
        # matching below is substring-based and matched "morgan" inside
        # "JPMorgan", linking Morgan Stanley to a roundup with no MS results.
        # If no headline-qualifying article exists, the item stays unlinked
        # here and gets a preview brief instead; the results-repoint pass
        # swaps the brief for real coverage once results are published.
        if item.get("kind") == "earnings":
            company = _company_from_label(item.get("label", ""))
            candidates = _candidate_articles(
                _company_search_patterns(company), cutoff)
            hit = next((r for r in candidates
                        if headline_is_earnings_coverage(r.get("headline", ""), company)),
                       None)
            if hit:
                item["link"] = f"/articles/{hit['slug']}"
                matched += 1
            continue

        terms = item.get("search_terms", [])
        terms = [t for t in terms if t and len(t) >= 3]
        if not terms:
            continue

        # For sports: team names are specific — don't filter "india"
        # For others: apply stop-word filter
        if category == "sports":
            words = [t for t in terms if t not in STOP]
        else:
            words = [t for t in terms if t not in STOP]

        if not words:
            continue

        rows = []
        # Try two-word pattern first (most specific)
        if len(words) >= 2:
            pattern = f"*{words[0]}*{words[1]}*"
            rows = _supabase_search(pattern, cutoff)
        # Fallback: single strong term (e.g. "west indies" for cricket)
        if not rows and words:
            # Pick the longest/most specific word
            best = max(words, key=len)
            if len(best) >= 5:
                rows = _supabase_search(f"*{best}*", cutoff)

        if rows:
            item["link"] = f"/articles/{rows[0]['slug']}"
            matched += 1

    print(f"  Article matching: {matched}/{len(items)} linked")
    return items


# ── 6. HAPPENING BRIEFS (generate info pages for unlinked entries) ─────────
# Kiran's rule: every Happening Today entry must link to something useful.
# If no existing Videshi article matches, generate a concise brief article
# (200-300 words) so the entry links to a real internal page.

BRIEF_CATEGORY_MAP = {
    "sports": "sports",
    "entertainment": "entertainment",
    "markets": "markets-finance",
    "news": "news",
}

def _brief_slug(item: dict, date: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (item.get("label") or "").lower()).strip("-")
    return f"happening-{date}-{base}"[:120]

def _brief_exists(slug: str) -> bool:
    """Dedup: don't regenerate a brief that already exists."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return False
    r = subprocess.run(
        ["curl", "-s", "--max-time", "10",
         f"{sb_url}/rest/v1/p2_articles?select=id&slug=eq.{slug}&limit=1",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=15,
    )
    try:
        rows = json.loads(r.stdout)
        return isinstance(rows, list) and len(rows) > 0
    except (json.JSONDecodeError, KeyError, IndexError):
        return False

def _format_pt(utc_iso: str) -> str:
    """Format a UTC timestamp as PT for the brief, e.g. 'Oct 9, 7:00 PM PT'."""
    try:
        dt = datetime.fromisoformat(str(utc_iso).replace("Z", "+00:00")).astimezone(PT)
        return dt.strftime("%b %-d, %-I:%M %p PT")
    except (ValueError, TypeError):
        return ""

def _brief_prompt(item: dict) -> str:
    label = item.get("label", "")
    detail = item.get("detail") or ""
    terms = ", ".join(item.get("search_terms", []))
    when = _format_pt(item.get("start_time_utc") or "")
    when_line = f"Event time: {when}." if when else ""

    sports_spec = f"""Write a concise match preview (200-300 words) for this sports event happening today.
Event: {label}
Venue/location: {detail}
{when_line}
Include: the matchup and format, venue, start time, and what's at stake (series context, standings implications — only if inferable from the event name/league).
Mention star players ONLY if they are globally famous and obviously relevant (e.g. an India match). NEVER invent quotes, scores, predictions, or broadcast details. If you don't know the broadcaster, omit it."""

    # Consensus expectations carried on the item from the Nasdaq calendar
    # row (get_earnings). Given facts: the brief MUST state them — a reader
    # judges an earnings report against the expected number (2026-10-21).
    expectations_block = ""
    if item.get("eps_forecast"):
        expectations_block = (
            f"\nMARKET EXPECTATIONS (given facts from the Nasdaq earnings calendar — state them exactly): "
            f"analyst consensus EPS forecast is {item['eps_forecast']}"
            + (f" (from {item['no_of_ests']} analyst estimates)" if item.get("no_of_ests") else "")
            + (f"; the company reported EPS of {item['last_year_eps']} in the same quarter last year" if item.get("last_year_eps") else "")
            + (f"; fiscal quarter ending {item['fiscal_quarter']}" if item.get("fiscal_quarter") else "")
            + "."
        )

    earnings_spec = f"""Write a concise earnings preview (220-300 words) for this company reporting today.
Company: {label}
Detail: {detail}{expectations_block}
Structure the brief in short paragraphs covering:
1. What the company does and its main business segments.
2. When it reports (from the detail line) and what is at stake this quarter.
3. What the market expects: state the consensus EPS forecast and the year-ago EPS from the MARKET EXPECTATIONS line above, exactly as given. If no expectations line is given, omit figures rather than inventing them.
4. What investors will watch, segment by segment: revenue trends, margin and cost pressures, guidance, and capital returns (dividends/buybacks) — qualitative only.
5. Why this report matters beyond the company (sector read-through, index weight, consumer or business signal).
The body MUST be at least 220 words. Do not pad with filler — add substantive preview detail instead.
NEVER invent EPS estimates, revenue figures, or analyst price targets beyond the given MARKET EXPECTATIONS figures. If expectations are unknown, say "analysts will be watching" without numbers."""

    markets_spec = f"""Write a short market notice (150-200 words).
Event: {label}
Detail: {detail}
Include: which markets are affected, why (the holiday), when regular trading resumes, and one line on what to watch when markets reopen."""

    entertainment_spec = f"""Write a short release-day brief (200-300 words) for this movie releasing today.
Film: {label}
Detail: {detail}
Include: what the film is (language/genre from the label), who's in it / who directed (only if widely known — otherwise omit names), and where it's playing.
NEVER invent reviews, ratings, or box office numbers."""

    specs = {
        "sports": sports_spec,
        "markets": markets_spec,
        "entertainment": entertainment_spec,
    }
    # Earnings entries are category "markets" with an "Earnings" label — use earnings spec
    spec = specs.get(item.get("category", ""), sports_spec)
    if "earnings" in label.lower():
        spec = earnings_spec

    # Expansion retry (earnings word-floor gate): a previous draft was too
    # short — demand a fuller brief, never filler.
    expand_note = ""
    if item.get("expand_brief"):
        expand_note = (f"\n\nIMPORTANT: A previous draft of this brief came to only "
                       f"~{item.get('prev_words', 0)} words. Write a fuller brief of at least "
                       f"220 words with more substantive segment-by-segment preview detail "
                       f"and context. Never pad with filler and never invent figures.")
        if item.get("deficit_words"):
            expand_note += (f" Specifically, add roughly {item['deficit_words']} more "
                            f"words of substantive segment detail than the previous draft.")

    return f"""You are writing a brief info article for The Videshi, a news site for the Indian diaspora.
Today is {datetime.now(PT).strftime('%B %d, %Y')}.

{spec}{expand_note}

FACT RULES (non-negotiable):
- Use ONLY facts given above or universally known facts (e.g. what a company does, what a tournament is).
- NEVER fabricate quotes, statistics, scores, estimates, or schedules.
- If a fact is unknown, omit it or say "details to be confirmed".

Write in a professional, concise news tone. No flowery language.

Return JSON only:
{{
  "headline": "Clear headline (under 90 chars)",
  "subheadline": "One-sentence summary",
  "body_html": "2-4 short <p> paragraphs of HTML",
  "key_takeaways": ["2-3 bullet strings"]
}}"""

def _gpt_brief(item: dict, api_key: str) -> dict | None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": _brief_prompt(item)}],
        "response_format": {"type": "json_object"},
        "max_tokens": 1200,
        "temperature": 0.3,
    }
    r = subprocess.run(
        ["curl", "-s", "--max-time", "60",
         "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {api_key}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=70,
    )
    try:
        data = json.loads(r.stdout)
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print(f"  ⚠️  GPT brief failed for '{item.get('label')}': {e}")
        return None

def _related_events(keyword: str, date: str, limit: int = 6) -> list[dict]:
    """Find upcoming events matching a festival keyword (for brief hub pages)."""
    import urllib.parse
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key or not keyword:
        return []
    kw = urllib.parse.quote(f"*{keyword}*")
    url = (f"{sb_url}/rest/v1/events?select=slug,title,date,venue_name,city"
           f"&or=(title.ilike.{kw},description.ilike.{kw})"
           f"&date=gte.{date}&order=date.asc&limit={limit}")
    r = subprocess.run(
        ["curl", "-s", "--max-time", "10", url,
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=15,
    )
    try:
        rows = json.loads(r.stdout)
        return rows if isinstance(rows, list) else []
    except (json.JSONDecodeError, KeyError, IndexError):
        return []

def _events_section_html(events: list[dict], keyword: str) -> str:
    """Deterministic 'celebrate near you' section with exact event links."""
    if not events:
        return (f"<h2>Find celebrations near you</h2>"
                f"<p>Looking for {keyword} events? "
                f'<a href="/events">Browse all events on The Videshi</a>.</p>')
    rows = []
    for e in events:
        d = e.get("date", "")
        try:
            d = datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d")
        except (ValueError, TypeError):
            pass
        where = ", ".join(p for p in [e.get("venue_name"), e.get("city")] if p)
        rows.append(
            f'<li><a href="/events/{e["slug"]}">{e["title"]}</a>'
            f" — {d}{', ' + where if where else ''}</li>"
        )
    return ("<h2>Celebrate near you</h2>"
            f"<p>Upcoming {keyword} celebrations listed on The Videshi:</p>"
            "<ul>" + "".join(rows) + "</ul>"
            '<p><a href="/events">Find more events near you →</a> · '
            '<a href="/festivals">All festivals</a></p>')

def _festival_prompt(item: dict) -> str:
    label = item.get("label", "")
    return f"""You are writing a festival guide for The Videshi, a news site for the Indian diaspora.
Today is {datetime.now(PT).strftime('%B %d, %Y')}.

Write a warm, informative guide (200-300 words) about: {label}
Cover in short <p> paragraphs:
1. What the festival is and its cultural/religious significance.
2. How it is traditionally celebrated (rituals, food, gatherings).
3. One paragraph on how diaspora families typically mark it abroad.

FACT RULES: use only widely known facts. Do NOT invent dates, rituals, or event listings — event listings are added separately.
Tone: warm, inclusive, knowledgeable. No flowery language.

Return JSON only:
{{
  "headline": "Clear headline naming the festival (under 90 chars)",
  "subheadline": "One-sentence summary",
  "body_html": "3-5 short <p> paragraphs of HTML",
  "key_takeaways": ["2-3 bullet strings"]
}}"""

def _generate_festival_brief(item: dict, date: str, api_key: str) -> dict | None:
    """Festival hub brief: GPT context + related events section."""
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": _festival_prompt(item)}],
        "response_format": {"type": "json_object"},
        "max_tokens": 1200,
        "temperature": 0.3,
    }
    r = subprocess.run(
        ["curl", "-s", "--max-time", "60",
         "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {api_key}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=70,
    )
    try:
        data = json.loads(r.stdout)
        art = json.loads(data["choices"][0]["message"]["content"])
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print(f"  ⚠️  GPT festival brief failed for '{item.get('label')}': {e}")
        return None

    keyword = item.get("festival_key", "")
    events = _related_events(keyword, date)
    body = art.get("body_html", "") + _events_section_html(events, keyword or "festival")

    keyword_tag = re.sub(r"[^a-z0-9]+", "-", keyword.lower()).strip("-")
    return {
        "headline": art.get("headline", item.get("label", ""))[:150],
        "subheadline": art.get("subheadline", ""),
        "body_html": body,
        "key_takeaways": art.get("key_takeaways", [])[:3],
        "tags": ["happening-brief", "festival"] + ([keyword_tag] if keyword_tag else []),
    }

def _find_trailer(title: str) -> str | None:
    """Match a movie title to a trailer video_id in trailers.json."""
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "public", "data", "trailers.json")) as f:
            data = json.load(f)
        trailers = data.get("trailers", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    t = (title or "").lower().strip()
    if not t:
        return None
    for tr in trailers:
        if t in (tr.get("title") or "").lower():
            return tr.get("video_id")
    words = [w for w in re.sub(r"[^a-z0-9 ]", " ", t).split() if len(w) > 3]
    for tr in trailers:
        tt = (tr.get("title") or "").lower()
        if words and all(w in tt for w in words[:3]):
            return tr.get("video_id")
    return None

def _movie_prompt(item: dict) -> str:
    m = item.get("movie") or {}
    title = m.get("title") or item.get("label", "")
    bits = [f'Film: "{title}" releasing today.']
    if m.get("language"):
        bits.append(f"Language: {m['language']}.")
    if m.get("genre"):
        bits.append(f"Genre: {m['genre']}.")
    if m.get("director"):
        bits.append(f"Director: {m['director']}.")
    if m.get("cast"):
        bits.append(f"Cast: {', '.join(m['cast'])}.")
    facts = " ".join(bits)

    return f"""You are writing an anticipation brief for The Videshi, a news site for the Indian diaspora.
Today is {datetime.now(PT).strftime('%B %d, %Y')}.

{facts}

Write 200-300 words on what to expect from this release: what kind of film it is, who's behind it, and why diaspora audiences might care.
This film has NOT been reviewed yet — frame everything as anticipation ("what to expect"), NEVER as a review.
FACT RULES: use only the facts given above plus widely known facts about the people named. NEVER invent reviews, ratings, box office numbers, plot details, or quotes.
End with: "The Videshi's critic review roundup will publish once reviews are in."
Tone: professional, enthusiastic but honest. No flowery language.

Return JSON only:
{{
  "headline": "Clear headline naming the film (under 90 chars)",
  "subheadline": "One-sentence summary",
  "body_html": "2-4 short <p> paragraphs of HTML",
  "key_takeaways": ["2-3 bullet strings"]
}}"""

def _generate_movie_brief(item: dict, date: str, api_key: str) -> dict | None:
    """Anticipation brief for a movie with no review yet: what to expect + trailer."""
    m = item.get("movie") or {}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": _movie_prompt(item)}],
        "response_format": {"type": "json_object"},
        "max_tokens": 1200,
        "temperature": 0.3,
    }
    r = subprocess.run(
        ["curl", "-s", "--max-time", "60",
         "https://api.openai.com/v1/chat/completions",
         "-H", f"Authorization: Bearer {api_key}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=70,
    )
    try:
        data = json.loads(r.stdout)
        art = json.loads(data["choices"][0]["message"]["content"])
    except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
        print(f"  ⚠️  GPT movie brief failed for '{item.get('label')}': {e}")
        return None

    body = art.get("body_html", "")
    trailer_id = _find_trailer(m.get("title", ""))
    if trailer_id:
        body += (f"<p>Watch the trailer:</p>"
                 f"<youtube>https://www.youtube.com/watch?v={trailer_id}</youtube>")
    if m.get("slug"):
        body += (f'<p><a href="/movies/{m["slug"]}">More about this film →</a></p>')

    title_tag = re.sub(r"[^a-z0-9]+", "-", (m.get("title") or "").lower()).strip("-")

    # Legitimate sources for the ≥2-source gate (2026-10-14): the official
    # trailer (already embedded in the body when found) and the film's
    # showtimes/ticketing page from the movie data. Nothing else is
    # claimed — if both are absent the gate suppresses the brief.
    brief_sources = []
    if trailer_id:
        brief_sources.append({
            "name": "Official Trailer — YouTube",
            "url": f"https://www.youtube.com/watch?v={trailer_id}",
        })
    if m.get("ticket_url"):
        brief_sources.append({
            "name": "Showtimes & Tickets",
            "url": m["ticket_url"],
        })

    return {
        "headline": art.get("headline", item.get("label", ""))[:150],
        "subheadline": art.get("subheadline", ""),
        "body_html": body,
        "key_takeaways": art.get("key_takeaways", [])[:3],
        "tags": ["happening-brief", "movies"] + ([title_tag] if title_tag else []),
        "sources": brief_sources,
    }

def _word_count(html: str) -> int:
    """Word count of an HTML body with tags stripped."""
    return len(re.sub(r"<[^>]+>", " ", html or "").split())

def _insert_brief(article: dict) -> bool:
    # ≥2-source gate backstop (2026-10-14): never POST a published brief
    # that fails the gate, whatever the caller did upstream.
    if article.get("status") == "published":
        _reason = source_gate.gate_failure(article.get("sources"))
        if _reason is not None:
            print(f"  🚫 _insert_brief refused '{article.get('slug')}': {_reason}")
            return False
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{sb_url}/rest/v1/p2_articles",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", json.dumps(article)],
        capture_output=True, text=True, timeout=20,
    )
    try:
        rows = json.loads(r.stdout)
        return isinstance(rows, list) and len(rows) > 0
    except json.JSONDecodeError:
        print(f"  ⚠️  brief insert failed: {r.stdout[:200]}")
        return False

def ensure_happening_briefs(items: list[dict], date: str, dry_run: bool = False) -> list[dict]:
    """Give every unlinked happening an internal brief article to link to."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    made = 0
    reused = 0

    for item in items:
        if item.get("link"):
            continue

        slug = _brief_slug(item, date)
        if _brief_exists(slug):
            item["link"] = f"/articles/{slug}"
            reused += 1
            continue

        if dry_run:
            kind = {"news": "festival hub", "entertainment": "movie anticipation"}.get(
                item.get("category", ""), "info")
            print(f"  📝 would generate {kind} brief: {slug}")
            item["link"] = f"/articles/{slug}"
            continue

        if not api_key:
            print(f"  ⚠️  no OPENAI_API_KEY — '{item.get('label')}' left unlinked")
            continue

        category = item.get("category", "")
        if category == "news":
            art = _generate_festival_brief(item, date, api_key)
        elif category == "entertainment":
            art = _generate_movie_brief(item, date, api_key)
        else:
            art = _gpt_brief(item, api_key)
        if not art:
            print(f"  ⚠️  brief generation failed for '{item.get('label')}' — left unlinked")
            continue

        # ── ≥2-source gate (earnings 2026-10-13; ALL briefs 2026-10-14) ──
        # Kiran (2026-10-14): the ≥2-source rule covers every new article,
        # happenings briefs included. Sources are the item's own verified
        # provenance (earnings: Nasdaq calendar + verified IR page;
        # festivals: FESTIVAL_SOURCES reference pages; market holidays:
        # the NYSE + Nasdaq official calendars; sports: the TheSportsDB
        # event page + the competition's verified official page) plus
        # any the generator attached (movie briefs: official trailer +
        # showtimes/ticketing page). A brief that cannot reach 2
        # legitimate sources is suppressed — the happening stays unlinked
        # — rather than published as a source-less stub. Never padded.
        # Earnings briefs ADDITIONALLY keep their 200-word floor with one
        # expansion retry (unchanged from 2026-10-13).
        is_earnings = item.get("kind") == "earnings"
        brief_sources = [s for s in item.get("sources", [])
                         if isinstance(s, dict) and s.get("url")]
        # Generator-attached sources are merged ONLY for movie briefs,
        # where _generate_movie_brief builds them deterministically in
        # code (trailer + ticket page) — never from LLM output.
        if category == "entertainment":
            for _s in art.get("sources") or []:
                if isinstance(_s, dict) and _s.get("url") and \
                        _s["url"] not in {x["url"] for x in brief_sources}:
                    brief_sources.append(_s)
        _valid_sources = source_gate.valid_sources(brief_sources)
        if len(_valid_sources) < source_gate.MIN_SOURCES:
            print(f"  🚫 brief suppressed for '{item.get('label')}': "
                  f"{len(_valid_sources)} verified source(s), need "
                  f"{source_gate.MIN_SOURCES} (≥2-source gate)")
            continue
        brief_words = 0
        if is_earnings:
            brief_words = _word_count(art.get("body_html", ""))
            if brief_words < EARNINGS_BRIEF_MIN_WORDS:
                retry = dict(item, expand_brief=True, prev_words=brief_words)
                art2 = _gpt_brief(retry, api_key)
                if art2 and _word_count(art2.get("body_html", "")) > brief_words:
                    art = art2
                    brief_words = _word_count(art.get("body_html", ""))
                # Near-miss second retry (2026-10-20): a brief landing just
                # under the floor (within 20 words) gets ONE more expansion
                # with the exact deficit spelled out. The 3M brief died at
                # 198/200 after the first retry and its row shipped unlinked.
                if _near_miss_band(brief_words):
                    retry2 = dict(item, expand_brief=True,
                                  prev_words=brief_words,
                                  deficit_words=220 - brief_words)
                    art3 = _gpt_brief(retry2, api_key)
                    if art3 and _word_count(art3.get("body_html", "")) > brief_words:
                        art = art3
                        brief_words = _word_count(art.get("body_html", ""))
                if brief_words < EARNINGS_BRIEF_MIN_WORDS:
                    print(f"  🚫 earnings brief suppressed for '{item.get('label')}': "
                          f"{brief_words} words < {EARNINGS_BRIEF_MIN_WORDS}-word floor "
                          f"after expansion retry")
                    continue

        category = BRIEF_CATEGORY_MAP.get(item.get("category", ""), "news")
        now = datetime.now(timezone.utc).isoformat()
        base_tags = art.get("tags") or (
            ["happening-brief"] + [t for t in item.get("search_terms", []) if t][:4]
        )
        row = {
            "headline": art.get("headline", item.get("label", ""))[:150],
            "slug": slug,
            "body": art.get("body_html", ""),
            "subheadline": art.get("subheadline", ""),
            "category": category,
            "vertical": category,
            "status": "published",
            "tags": base_tags[:5],
            "is_editorial": False,
            "article_type": "brief",
            "score_total": 0,
            "key_takeaways": art.get("key_takeaways", [])[:3],
            "diaspora_angle": "",
            "published_at": now,
            "created_at": now,
        }
        row["sources"] = brief_sources
        if is_earnings:
            row["word_count"] = brief_words
        if _insert_brief(row):
            item["link"] = f"/articles/{slug}"
            made += 1
            print(f"  ✅ brief published: {slug}")
        else:
            print(f"  ⚠️  brief insert failed for '{item.get('label')}' — left unlinked")

    print(f"  Happening briefs: {made} generated, {reused} reused")
    return items


# ── Results repoint pass (2026-10-14) ──────────────────────────────────────
# The morning run publishes a preview brief (happening-* stub) before a
# company reports. Once the report window closes, Happening Today must move
# from the stub to real results coverage — automatically, for every future
# earnings day. On each run, this pass scans today's and yesterday's
# earnings rows that still link to a happening-* stub:
#   - report window passed + a published article whose HEADLINE names the
#     company exists (published on/after the earnings date, stubs excluded)
#     -> repoint the row to it and retire the stub to draft (superseded)
#   - window passed >6h ago and no such article -> loud "⚠️ RESULTS GAP"
#     line in the run output, so a missing-results day is never silent.
# Incident that forced this: on 2026-10-14 the Bank of America row still
# pointed at its pre-report stub hours after BAC reported, because nothing
# ever revisited the link.

def _sb_curl(method: str, path: str, payload: dict | None = None):
    """Minimal Supabase REST helper via curl (urllib fails through the proxy)."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return None
    cmd = ["curl", "-s", "--max-time", "15", "-X", method,
           f"{sb_url}/rest/v1/{path}",
           "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"]
    if payload is not None:
        cmd += ["-H", "Content-Type: application/json",
                "-H", "Prefer: return=representation",
                "-d", json.dumps(payload)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        return json.loads(r.stdout) if r.stdout.strip() else []
    except json.JSONDecodeError:
        return None


def _report_window_end(row: dict):
    """UTC datetime when a happening row's report window closes:
    before-market reporters are done by ~13:00 UTC, after-hours by
    ~21:00 UTC (from the row's detail slot); without slot info, fall back
    to 21:00 UTC on the happening date."""
    try:
        day = datetime.strptime(row.get("date") or "", "%Y-%m-%d").replace(
            tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None
    detail = (row.get("detail") or "").lower()
    if "before market" in detail or "pre-market" in detail:
        return day + timedelta(hours=13)
    return day + timedelta(hours=21)


def _find_results_article(company: str, date_str: str):
    """Newest published results article for a company, published on/after
    the earnings date, whose headline names the company. Preview stubs
    (happening-*) never qualify."""
    cutoff = f"{date_str}T00:00:00"
    for r in _candidate_articles(_company_search_patterns(company), cutoff):
        slug = r.get("slug") or ""
        if slug.startswith("happening-"):
            continue
        if headline_is_earnings_coverage(r.get("headline", ""), company):
            return r
    return None


def results_repoint_pass(dry_run: bool = False, extra_rows: list | None = None) -> dict:
    """Repoint stub-linked earnings rows to results coverage (see header).

    extra_rows lets tests/callers inject synthetic happening rows (used with
    dry_run for the guard proof); they are never written to the DB."""
    now = datetime.now(timezone.utc)
    today = today_pt()
    yesterday = (datetime.strptime(today, "%Y-%m-%d")
                 - timedelta(days=1)).strftime("%Y-%m-%d")
    rows = _sb_curl(
        "GET",
        "daily_happenings?select=id,date,label,detail,link,category"
        "&category=eq.markets&label=ilike.*earnings*"
        "&link=like./articles/happening-*"
        f"&date=in.({yesterday},{today})&order=date.asc") or []
    rows = list(rows) + list(extra_rows or [])

    repointed = gaps = pending = 0
    for row in rows:
        link = row.get("link") or ""
        if not link.startswith("/articles/happening-"):
            continue
        stub_slug = link.rsplit("/", 1)[-1]
        company = _company_from_label(row.get("label", ""))
        window_end = _report_window_end(row)
        if window_end is None or now < window_end:
            pending += 1
            continue
        hit = _find_results_article(company, row.get("date") or today)
        if hit:
            new_link = f"/articles/{hit['slug']}"
            if dry_run:
                print(f"  🔁 [dry-run] would repoint '{row.get('label')}' "
                      f"({row.get('date')}): {link} -> {new_link}; "
                      f"stub {stub_slug} -> draft")
            else:
                if row.get("id"):
                    _sb_curl("PATCH",
                             f"daily_happenings?id=eq.{row['id']}",
                             {"link": new_link})
                _sb_curl("PATCH",
                         f"p2_articles?slug=eq.{stub_slug}&status=eq.published",
                         {"status": "draft"})
                print(f"  🔁 RESULTS REPOINT: '{row.get('label')}' "
                      f"({row.get('date')}) {link} -> {new_link}; "
                      f"stub retired to draft")
            repointed += 1
        elif now > window_end + timedelta(hours=6):
            print(f"  ⚠️ RESULTS GAP: {company} reported on {row.get('date')} "
                  f"and the report window closed over 6h ago, but no published "
                  f"results article names the company in its headline — "
                  f"Happening Today still links to the preview stub {link}")
            gaps += 1
        else:
            pending += 1
    print(f"  Results repoint pass: {repointed} repointed, {gaps} gap(s), "
          f"{pending} not yet due")
    return {"repointed": repointed, "gaps": gaps, "pending": pending}


# ── Supabase ops ─────────────────────────────────────────────────────────────

def supabase_delete_today(date: str):
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    subprocess.run(
        ["curl", "-s", "-X", "DELETE",
         f"{sb_url}/rest/v1/daily_happenings?date=eq.{date}",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=15,
    )

def supabase_insert(items: list[dict], date: str) -> int:
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    rows = []
    for i, item in enumerate(items):
        row = {
            "date": date,
            "emoji": item["emoji"],
            "label": item["label"][:80],
            "detail": (item.get("detail") or "")[:200] or None,
            "link": item.get("link"),
            "category": item.get("category"),
            "sort_order": i + 1,
            "start_time": item.get("start_time_utc"),
        }
        rows.append(row)

    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{sb_url}/rest/v1/daily_happenings",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", json.dumps(rows)],
        capture_output=True, text=True, timeout=15,
    )
    try:
        inserted = json.loads(r.stdout)
        if isinstance(inserted, list):
            return len(inserted)
    except json.JSONDecodeError:
        pass
    return 0


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Populate daily happenings (v2 — real data)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--date", type=str, default=None)
    parser.add_argument("--repoint-only", action="store_true",
                        help="Only run the results-repoint pass (stub -> "
                             "results coverage) and exit")
    args = parser.parse_args()

    if args.repoint_only:
        print("🔁 Results repoint pass only")
        results_repoint_pass(dry_run=args.dry_run)
        return

    date = args.date or today_pt()
    weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%A") if args.date else weekday_pt()

    print(f"📅 Generating happenings for {weekday}, {date} (v2 — real data)")
    print(f"{'─' * 60}")

    # Gather from all sources
    all_items = []

    # Festivals first (most important — one-day events)
    all_items.extend(get_festivals(date))

    # Sports
    all_items.extend(get_sports(date))

    # Movie releases
    all_items.extend(get_movie_releases(date))

    # Earnings
    all_items.extend(get_earnings(date))

    # Market status
    all_items.extend(get_market_status(date))

    if not all_items:
        print("⚠️  No happenings found for today.")
        return

    # Sort: festivals first, then sports (by time), then entertainment, then markets
    CATEGORY_ORDER = {"news": 0, "sports": 1, "entertainment": 2, "markets": 3}
    all_items.sort(key=lambda x: (
        CATEGORY_ORDER.get(x.get("category", ""), 9),
        x.get("start_time_utc") or "9999",
    ))

    print(f"\n{'─' * 60}")
    print(f"  Total: {len(all_items)} happenings")
    for item in all_items:
        detail = f" — {item['detail']}" if item.get("detail") else ""
        time_str = f" [{item['start_time_utc']}]" if item.get("start_time_utc") else ""
        print(f"  {item['emoji']}  {item['label']}{detail}{time_str}")
    print(f"{'─' * 60}\n")

    # Article matching
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("  Matching to recent articles...")
        all_items = match_articles(all_items)

    # Generate brief info pages for anything still unlinked (Kiran's rule:
    # every entry must link to something useful)
    print("  Generating briefs for unlinked entries...")
    all_items = ensure_happening_briefs(all_items, date, dry_run=args.dry_run)

    if args.dry_run:
        print("\n  Repoint pass (dry-run):")
        results_repoint_pass(dry_run=True)
        print("\n🏁 Dry run — no changes made.")
        for item in all_items:
            link_str = f"  → {item.get('link', '')}" if item.get("link") else ""
            print(f"  {item['emoji']}  {item['label']}{link_str}")
        return

    # Insert
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set", file=sys.stderr)
        sys.exit(1)

    print(f"  Clearing old happenings for {date}...")
    supabase_delete_today(date)

    print(f"  Inserting {len(all_items)} happenings...")
    count = supabase_insert(all_items, date)

    if count > 0:
        print(f"✅ Inserted {count} happenings for {date}")
    else:
        print(f"❌ Insert may have failed", file=sys.stderr)
        sys.exit(1)

    # Swap any stub links whose results are now published (today's rows were
    # just rebuilt; yesterday's rows are covered here too) — see
    # results_repoint_pass (2026-10-14).
    print("  Running results repoint pass...")
    results_repoint_pass()


if __name__ == "__main__":
    main()
