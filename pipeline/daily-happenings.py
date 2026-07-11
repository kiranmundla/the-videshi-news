#!/usr/bin/env python3
"""
daily-happenings.py — Populate the daily_happenings table with today's events.

Uses Gemini 2.5 Flash with Google Search grounding to discover what's happening
today, then inserts the top items into Supabase for the Happening Today strip
on the homepage.

Usage:
    # Dry run — prints what would be inserted
    python3 pipeline/daily-happenings.py --dry-run

    # Real run — clears today's old entries, inserts new ones
    python3 pipeline/daily-happenings.py

Env vars required:
    GOOGLE_AI_API_KEY   — Gemini API key
    SUPABASE_URL        — Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY — Supabase service role key
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

# ── Timezone helpers ──────────────────────────────────────────────────────────
PT = timezone(timedelta(hours=-7))  # PDT


def today_pt():
    return datetime.now(PT).strftime("%Y-%m-%d")


def weekday_pt():
    return datetime.now(PT).strftime("%A")


# ── Gemini call ───────────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """\
Today is {weekday}, {date}. What are the major events happening TODAY that \
would interest an Indian diaspora audience in the United States?

Include:
- Sports events with exact matchups, times (in PT and ET), and TV channels \
(FIFA World Cup, Wimbledon, cricket, MLC, IPL, Olympics, etc.)
- Major political/policy events (only if actually scheduled today)
- Market/economic events (only if markets are open today)
- Entertainment releases, premieres, Bollywood
- India-related news events, diplomatic meetings
- Indian community festivals and events in major US cities

Rules — follow these strictly:
1. ONLY include events you can confirm are happening TODAY ({date}). \
Do NOT include events from other days. Do NOT guess.
2. Saturday/Sunday = US stock markets closed, US courts closed — skip those.
3. If a match has already concluded today, note "(concluded)" in detail.
4. Keep label short (under 50 chars). Put times, players, channels in detail.
5. Limit to the 6-8 MOST important/interesting items.

Prioritize: World Cup / cricket matches > major diaspora events > \
policy / immigration news > entertainment.

Return as a JSON array with NO markdown fencing:
[{{"emoji":"⚽","label":"Short event name","detail":"Key info, time PT, channel","category":"sports","sort_order":1}}]

category must be one of: sports, news, markets, entertainment

Return ONLY the raw JSON array — no explanation, no code fences."""


def call_gemini(date: str, weekday: str) -> list[dict]:
    """Call Gemini 2.5 Flash with Google Search grounding and return parsed items."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_AI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={api_key}"
    )

    prompt = PROMPT_TEMPLATE.format(weekday=weekday, date=date)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2000,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }

    result = subprocess.run(
        [
            "curl", "-s", "--max-time", "45",
            "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode != 0:
        print(f"ERROR: curl failed (rc={result.returncode}): {result.stderr}", file=sys.stderr)
        sys.exit(1)

    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse Gemini response as JSON:\n{result.stdout[:500]}", file=sys.stderr)
        sys.exit(1)

    # Extract text from response
    text = None
    if "candidates" in response:
        for part in response["candidates"][0]["content"]["parts"]:
            if "text" in part:
                text = part["text"]
                break

    if not text:
        print("ERROR: No text in Gemini response", file=sys.stderr)
        print(json.dumps(response, indent=2)[:1000], file=sys.stderr)
        sys.exit(1)

    # Strip markdown code fences if present
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()

    try:
        items = json.loads(text)
    except json.JSONDecodeError:
        print(f"ERROR: Gemini returned non-JSON text:\n{text[:500]}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(items, list):
        print(f"ERROR: Expected JSON array, got {type(items).__name__}", file=sys.stderr)
        sys.exit(1)

    # Validate and normalise each item
    valid = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        label = (item.get("label") or "").strip()
        if not label:
            continue
        valid.append({
            "emoji": (item.get("emoji") or "📌").strip(),
            "label": label[:80],
            "detail": (item.get("detail") or "")[:200] or None,
            "category": item.get("category", "news"),
            "sort_order": item.get("sort_order", i + 1),
        })

    return valid[:10]  # cap at 10


# ── Article matching ──────────────────────────────────────────────────────────

# Words too generic to use as standalone search terms
_STOP_WORDS = {
    "the", "a", "an", "of", "in", "on", "at", "to", "for", "and", "or", "vs",
    "is", "are", "was", "were", "be", "been", "has", "have", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "shall", "can",
    "its", "it", "he", "she", "they", "we", "you", "this", "that", "with",
    "from", "by", "as", "but", "not", "no", "all", "new", "day", "today",
    "match", "game", "final", "quarterfinal", "semifinal", "concluded", "annual",
    "festival", "event", "pm", "am", "et", "pt", "ct", "fox", "espn",
    "quarter", "semi", "round", "cup", "league", "cricket", "stadium",
    "super", "kings", "freedom", "royal", "united", "city",
    "released", "releases", "release", "film", "films", "movie", "movies",
    "visit", "visits", "departs", "departed", "free", "family",
    "south", "asian", "north", "east", "west", "park", "center", "church",
    "india", "indian", "bollywood",  # too broad for article search
    "washington", "texas", "chicago", "miami", "york",  # city/state names match wrong articles
}


def _extract_keywords(label: str, detail: str | None) -> list[str]:
    """Pull 2-4 distinctive keywords from label + detail for article search."""
    combined = f"{label} {detail or ''}"
    # Remove parentheticals and punctuation, keep alphanumeric + spaces
    combined = re.sub(r"\([^)]*\)", " ", combined)
    combined = re.sub(r"[^a-zA-Z0-9\s]", " ", combined)
    words = combined.split()

    # Keep words that are >=3 chars and not stop words
    candidates = []
    for w in words:
        wl = w.lower()
        if len(wl) >= 3 and wl not in _STOP_WORDS:
            if wl not in [c.lower() for c in candidates]:  # dedup
                candidates.append(w)

    # Return top 4 most distinctive (longest first as a rough proxy)
    candidates.sort(key=lambda w: -len(w))
    return candidates[:4]


def _build_ilike_queries(keywords: list[str]) -> list[str]:
    """Build a series of ILIKE patterns from most specific to least.

    For keywords [A, B, C, D]:
      - *A*B*  (top two — most specific)
      - *A*C*  (first + third)
      - *A*    (just the top keyword — broadest fallback)
    """
    if not keywords:
        return []
    queries = []
    kl = [k.lower() for k in keywords]

    # Two-keyword combos using first keyword
    if len(kl) >= 2:
        queries.append(f"*{kl[0]}*{kl[1]}*")
    if len(kl) >= 3:
        queries.append(f"*{kl[0]}*{kl[2]}*")
    if len(kl) >= 2:
        # Reversed order in case headline word order differs
        queries.append(f"*{kl[1]}*{kl[0]}*")

    # Single keyword fallback (broadest)
    queries.append(f"*{kl[0]}*")

    return queries


def match_articles(items: list[dict]) -> list[dict]:
    """For each happening, try to find a matching recent article and set link."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        print("   ⚠️  Supabase env not set — skipping article matching", file=sys.stderr)
        return items

    # Date cutoff: articles from last 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")

    matched = 0
    for item in items:
        keywords = _extract_keywords(item["label"], item.get("detail"))
        if not keywords:
            continue

        ilike_patterns = _build_ilike_queries(keywords)
        found = False

        for pattern in ilike_patterns:
            query_url = (
                f"{sb_url}/rest/v1/p2_articles"
                f"?select=slug,headline"
                f"&status=eq.published"
                f"&headline=ilike.{pattern}"
                f"&published_at=gte.{cutoff}"
                f"&order=published_at.desc"
                f"&limit=1"
            )
            result = subprocess.run(
                [
                    "curl", "-s", "--max-time", "10",
                    query_url,
                    "-H", f"apikey: {sb_key}",
                    "-H", f"Authorization: Bearer {sb_key}",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                continue

            try:
                rows = json.loads(result.stdout)
            except json.JSONDecodeError:
                continue

            if isinstance(rows, list) and len(rows) > 0:
                slug = rows[0].get("slug", "")
                headline = (rows[0].get("headline") or "").lower()
                # Relevance check: matched headline must share at least 1
                # distinctive keyword with the happening label
                kw_lower = [k.lower() for k in keywords]
                shared = sum(1 for k in kw_lower if k in headline)
                if slug and shared >= 1:
                    item["link"] = f"/articles/{slug}"
                    matched += 1
                    found = True
                    break

        if not found:
            item["link"] = None

    print(f"   🔗 Matched {matched}/{len(items)} happenings to articles")
    return items


# ── Supabase operations ──────────────────────────────────────────────────────

def supabase_delete_today(date: str):
    """Delete all happenings for the given date."""
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    result = subprocess.run(
        [
            "curl", "-s", "-X", "DELETE",
            f"{sb_url}/rest/v1/daily_happenings?date=eq.{date}",
            "-H", f"apikey: {sb_key}",
            "-H", f"Authorization: Bearer {sb_key}",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        print(f"WARNING: delete curl failed: {result.stderr}", file=sys.stderr)


def supabase_insert(items: list[dict], date: str) -> int:
    """Insert happenings into Supabase. Returns count inserted."""
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    for item in items:
        item["date"] = date

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"{sb_url}/rest/v1/daily_happenings",
            "-H", f"apikey: {sb_key}",
            "-H", f"Authorization: Bearer {sb_key}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", json.dumps(items),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    if result.returncode != 0:
        print(f"ERROR: insert curl failed: {result.stderr}", file=sys.stderr)
        return 0

    try:
        inserted = json.loads(result.stdout)
        if isinstance(inserted, list):
            return len(inserted)
    except json.JSONDecodeError:
        pass

    # Check for error response
    if result.stdout and "error" in result.stdout.lower():
        print(f"ERROR: Supabase insert error: {result.stdout[:300]}", file=sys.stderr)
        return 0

    return len(items)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Populate daily happenings")
    parser.add_argument("--dry-run", action="store_true", help="Print items without inserting")
    parser.add_argument("--date", type=str, default=None, help="Override date (YYYY-MM-DD)")
    args = parser.parse_args()

    date = args.date or today_pt()
    weekday = args.date and datetime.strptime(args.date, "%Y-%m-%d").strftime("%A") or weekday_pt()

    print(f"📅 Generating happenings for {weekday}, {date}")
    print(f"   Calling Gemini 2.5 Flash with Google Search grounding...")

    items = call_gemini(date, weekday)

    if not items:
        print("⚠️  Gemini returned no items — keeping existing happenings unchanged.")
        sys.exit(0)

    print(f"\n{'─' * 60}")
    print(f"   Found {len(items)} happenings:")
    print(f"{'─' * 60}")
    for item in items:
        detail = f" — {item['detail']}" if item.get("detail") else ""
        print(f"   {item['emoji']}  {item['label']}{detail}")
    print(f"{'─' * 60}\n")

    # Match happenings to published articles
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("   Matching happenings to recent articles...")
        items = match_articles(items)
    else:
        print("   ⚠️  Supabase env not set — skipping article matching")

    if args.dry_run:
        print("🏁 Dry run — no changes made.")
        for item in items:
            link_str = f"  → {item['link']}" if item.get("link") else "  (no article match)"
            print(f"   {item['emoji']}  {item['label']}{link_str}")
        print()
        print(json.dumps(items, indent=2))
        return

    # Check Supabase env
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("ERROR: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Delete old, insert new
    print(f"   Clearing old happenings for {date}...")
    supabase_delete_today(date)

    print(f"   Inserting {len(items)} happenings...")
    count = supabase_insert(items, date)

    if count > 0:
        print(f"✅ Inserted {count} happenings for {date}")
    else:
        print(f"❌ Insert may have failed — check Supabase logs", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
