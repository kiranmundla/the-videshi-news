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

def get_sports(date: str) -> list[dict]:
    """Fetch sports events from TheSportsDB."""
    items = []
    
    # Cricket
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date}&s=Cricket")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_cricket(e):
                items.append({
                    "emoji": "🏏",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
                    "start_time_utc": e.get("strTimestamp"),
                    "search_terms": [
                        (e.get("strHomeTeam") or "").lower(),
                        (e.get("strAwayTeam") or "").lower(),
                    ],
                })
    
    # Soccer — only FIFA/Champions League/major tournaments
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date}&s=Soccer")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_soccer(e):
                items.append({
                    "emoji": "⚽",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
                    "start_time_utc": e.get("strTimestamp"),
                    "search_terms": [
                        (e.get("strHomeTeam") or "").lower(),
                        (e.get("strAwayTeam") or "").lower(),
                    ],
                })
    
    # Tennis — only Grand Slams
    data = curl_json(f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={date}&s=Tennis")
    if data and data.get("events"):
        for e in data["events"]:
            if _is_relevant_tennis(e):
                items.append({
                    "emoji": "🎾",
                    "label": _format_sport_label(e),
                    "detail": _sport_detail(e),
                    "category": "sports",
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
        
        items.append({
            "emoji": "📊",
            "label": f"{name} Earnings",
            "detail": detail,
            "category": "markets",
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
            "start_time_utc": None,
            "search_terms": [],
        }]
    
    # Normal open days — not interesting enough to show
    return []


# ── 5. FESTIVALS & HOLIDAYS ─────────────────────────────────────────────────

FESTIVALS_2026 = {
    # Indian festivals (dates for 2026)
    "2026-01-14": ("🪁", "Makar Sankranti / Pongal"),
    "2026-01-26": ("🇮🇳", "India Republic Day"),
    "2026-03-04": ("🎨", "Holi — Festival of Colors"),
    "2026-03-19": ("🛕", "Ugadi / Gudi Padwa"),
    "2026-03-26": ("🕉️", "Ram Navami"),
    "2026-04-14": ("🪔", "Baisakhi / Tamil New Year"),
    "2026-05-01": ("🙏", "Buddha Purnima"),
    "2026-05-26": ("☪️", "Eid al-Adha"),
    "2026-06-16": ("☪️", "Muharram"),
    "2026-08-15": ("🇮🇳", "India Independence Day"),
    "2026-08-28": ("🪢", "Raksha Bandhan"),
    "2026-09-04": ("🕉️", "Janmashtami"),
    "2026-09-05": ("📚", "Teachers' Day (India)"),
    "2026-09-14": ("🐘", "Ganesh Chaturthi"),
    "2026-08-26": ("☪️", "Milad un-Nabi"),
    "2026-10-11": ("🔱", "Navratri Begins"),
    "2026-10-20": ("🏹", "Dussehra / Vijayadashami"),
    "2026-11-08": ("🪔", "Diwali — Festival of Lights"),
    "2026-11-10": ("🎊", "Bhai Dooj"),
    "2026-11-24": ("🕯️", "Guru Nanak Jayanti"),
    "2026-12-25": ("🎄", "Christmas"),
    # US holidays
    "2026-01-01": ("🎆", "New Year's Day"),
    "2026-01-19": ("✊", "Martin Luther King Jr. Day"),
    "2026-02-16": ("🇺🇸", "Presidents' Day"),
    "2026-05-25": ("🎖️", "Memorial Day"),
    "2026-06-19": ("✊", "Juneteenth"),
    "2026-07-04": ("🇺🇸", "Independence Day (USA)"),
    "2026-09-07": ("⚙️", "Labor Day"),
    "2026-11-26": ("🦃", "Thanksgiving"),
}

def get_festivals(date: str) -> list[dict]:
    """Check if today is a festival or holiday."""
    items = []
    if date in FESTIVALS_2026:
        emoji, label = FESTIVALS_2026[date]
        items.append({
            "emoji": emoji,
            "label": label,
            "detail": None,
            "category": "news",
            "start_time_utc": None,
            "search_terms": [],
        })
    print(f"  Festivals: {len(items)}")
    return items


# ── Article matching (reused from v1) ────────────────────────────────────────

def match_articles(items: list[dict]) -> list[dict]:
    """Match happenings to recent Videshi articles."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return items

    cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
    matched = 0

    for item in items:
        if item.get("link"):  # Already has a link (e.g. movie slug)
            matched += 1
            continue

        terms = item.get("search_terms", [])
        terms = [t for t in terms if t and len(t) >= 3]
        if len(terms) < 2:
            continue

        # Build ILIKE patterns from pairs of terms
        STOP = {"india", "indian", "world", "cup", "cricket", "open", "league",
                "major", "the", "men", "women", "match", "final", "test"}
        words = [t for t in terms if t not in STOP]
        if len(words) < 2:
            continue

        # Try first pair
        pattern = f"*{words[0]}*{words[1]}*"
        query_url = (
            f"{sb_url}/rest/v1/p2_articles"
            f"?select=slug,headline"
            f"&status=eq.published"
            f"&headline=ilike.{pattern}"
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
            if isinstance(rows, list) and rows:
                item["link"] = f"/articles/{rows[0]['slug']}"
                matched += 1
                continue
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

    print(f"  Article matching: {matched}/{len(items)} linked")
    return items


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
    args = parser.parse_args()

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

    if args.dry_run:
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


if __name__ == "__main__":
    main()
