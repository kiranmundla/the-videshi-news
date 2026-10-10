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
                        _clean_team_name(e.get("strHomeTeam")),
                        _clean_team_name(e.get("strAwayTeam")),
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
                        _clean_team_name(e.get("strHomeTeam")),
                        _clean_team_name(e.get("strAwayTeam")),
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

    earnings_spec = f"""Write a concise earnings preview (200-300 words) for this company reporting today.
Company: {label}
Detail: {detail}
Include: what the company does (one sentence), what to watch in the report (revenue trends, guidance, key business segments), and why it matters to investors.
NEVER invent EPS estimates, revenue figures, or analyst price targets. If expectations are unknown, say "analysts will be watching" without numbers."""

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

    return f"""You are writing a brief info article for The Videshi, a news site for the Indian diaspora.
Today is {datetime.now(PT).strftime('%B %d, %Y')}.

{spec}

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
    return {
        "headline": art.get("headline", item.get("label", ""))[:150],
        "subheadline": art.get("subheadline", ""),
        "body_html": body,
        "key_takeaways": art.get("key_takeaways", [])[:3],
        "tags": ["happening-brief", "movies"] + ([title_tag] if title_tag else []),
    }

def _insert_brief(article: dict) -> bool:
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
        if _insert_brief(row):
            item["link"] = f"/articles/{slug}"
            made += 1
            print(f"  ✅ brief published: {slug}")
        else:
            print(f"  ⚠️  brief insert failed for '{item.get('label')}' — left unlinked")

    print(f"  Happening briefs: {made} generated, {reused} reused")
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

    # Generate brief info pages for anything still unlinked (Kiran's rule:
    # every entry must link to something useful)
    print("  Generating briefs for unlinked entries...")
    all_items = ensure_happening_briefs(all_items, date, dry_run=args.dry_run)

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
