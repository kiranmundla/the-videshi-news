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
- Entertainment releases, premieres, Bollywood (ONLY if releasing TODAY)
- Indian community festivals and events in major US cities

Rules — follow these strictly:
1. ONLY include events you can confirm are SCHEDULED for TODAY ({date}). \
Do NOT include events from yesterday, tomorrow, or any other day. Do NOT guess.
2. Saturday/Sunday = US stock markets closed, US courts closed — skip those.
3. Only include NATIONALLY or INTERNATIONALLY significant events — things \
any NRI in any US city would care about.
4. NO local community events (city-specific festivals, temple events, local \
Bollywood nights, regional melas). Those are local, not national.
5. NO travel updates like "PM Modi returns to India" — those are not events.
6. Keep label short (under 50 chars). detail = venue/channel info, NO times.
7. Limit to 4-6 MOST important items. Quality over quantity.
8. NO breaking news or developing news stories (missing persons, accidents, \
diplomatic tensions). "Happening Today" means SCHEDULED events only.
9. For movie releases: verify the EXACT theatrical release date. A movie \
releasing on July 17 must NOT be listed on July 12. Double-check release dates.
10. For sports tournaments with multiple rounds: verify which ROUND is today. \
If quarter-finals were yesterday and semi-finals are Tuesday, there is NO \
match today — do NOT list the tournament.
11. Verify the VENUE for each event. A match at Marine Park, New York should \
NOT say Grand Prairie, Dallas.

Prioritize: Major sports (World Cup, Wimbledon, cricket internationals, MLC) \
> Major policy/immigration decisions > Big entertainment releases > \
Significant diplomatic events (not travel updates).

CRITICAL for sports: You MUST provide start_time_utc for every sports event. \
Every scheduled match has a kickoff/start time — look it up and convert to UTC.

Return as a JSON array with NO markdown fencing. Each item MUST have:
- "search_terms": 2-4 specific, distinctive keywords (proper nouns, team \
names, player names). Avoid generic words like "india", "cricket", "sports". \
Good: ["noskova", "muchova", "wimbledon"], ["norway", "england", "quarterfinal"].
- "start_time_utc": ISO 8601 UTC timestamp (e.g. "2026-07-11T21:00:00Z"). \
Convert from ET/PT/BST/IST. REQUIRED for sports. Set null only for non-timed \
events (all-day, news).

[{{"emoji":"⚽","label":"Short event name","detail":"Venue, channel (NO times)",\
"category":"sports","sort_order":1,"search_terms":["keyword1","keyword2"],\
"start_time_utc":"2026-07-11T21:00:00Z"}}]

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

        # Preserve search_terms from Gemini
        raw_terms = item.get("search_terms", [])
        search_terms = [t.lower().strip() for t in raw_terms if isinstance(t, str) and len(t.strip()) >= 2]

        valid.append({
            "emoji": (item.get("emoji") or "📌").strip(),
            "label": label[:80],
            "detail": (item.get("detail") or "")[:200] or None,
            "category": item.get("category", "news"),
            "sort_order": item.get("sort_order", i + 1),
            "search_terms": search_terms,
            "start_time_utc": item.get("start_time_utc"),
        })

    return valid[:10]  # cap at 10


# ── Verification pass ─────────────────────────────────────────────────────────

VERIFY_PROMPT = """\
Today is {weekday}, {date} (Pacific Time). I need you to verify FACTUAL DETAILS \
for each of these events.

For each item, check:
1. Is the VENUE/LOCATION correct? Search for the actual venue. \
For example, MI New York's home ground is Marine Park in New York, not Texas.
2. Is it a real SCHEDULED event (not a breaking news story or developing situation)?
3. Is this NATIONALLY/INTERNATIONALLY significant (not a local community event)?
4. For movie releases: verify the movie title and that it's a real movie.
5. For sports: has this specific match ALREADY BEEN PLAYED? Search for the \
result. If the match has a final score, it's OVER — mark invalid. \
Also verify the round/stage is correct for today's date.
6. For sports tournaments: verify which stage is actually scheduled today. \
If the quarter-finals ended yesterday and the semi-finals start in 2 days, \
there is NO match today.

Items to verify:
{items_json}

Return a JSON array with one object per item, in the same order:
[{{"index": 0, "valid": true/false, "reason": "why valid or invalid"}}]

Be STRICT. If you cannot confirm the event is today, mark it invalid.
Return ONLY the raw JSON array — no explanation, no code fences.\
"""


def verify_items(items: list[dict], date: str, weekday: str) -> list[dict]:
    """Second Gemini call to fact-check each item. Returns only verified items."""
    api_key = os.environ.get("GOOGLE_AI_API_KEY", "")
    if not api_key:
        print("   ⚠️  No API key for verification — skipping", file=sys.stderr)
        return items

    # Build a clean list for verification
    verify_list = []
    for i, item in enumerate(items):
        verify_list.append({
            "index": i,
            "label": item["label"],
            "detail": item.get("detail", ""),
            "category": item.get("category", ""),
            "start_time_utc": item.get("start_time_utc"),
        })

    prompt = VERIFY_PROMPT.format(
        weekday=weekday, date=date, items_json=json.dumps(verify_list, indent=2)
    )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-2.5-flash:generateContent?key={api_key}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 1500,
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
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        print("   ⚠️  Verification curl failed — keeping all items", file=sys.stderr)
        return items

    try:
        response = json.loads(result.stdout)
        text = None
        if "candidates" in response:
            for part in response["candidates"][0]["content"]["parts"]:
                if "text" in part:
                    text = part["text"]
                    break
        if not text:
            print("   ⚠️  No text in verification response — keeping all items", file=sys.stderr)
            return items

        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        verdicts = json.loads(text.strip())
    except (json.JSONDecodeError, KeyError, IndexError):
        print("   ⚠️  Could not parse verification response — keeping all items", file=sys.stderr)
        return items

    if not isinstance(verdicts, list):
        return items

    # Build a set of invalid indices
    invalid_indices = set()
    for v in verdicts:
        if isinstance(v, dict) and v.get("valid") is False:
            idx = v.get("index")
            reason = v.get("reason", "unverified")
            if isinstance(idx, int) and 0 <= idx < len(items):
                invalid_indices.add(idx)
                print(f"   ❌ REJECTED: {items[idx]['label']} — {reason}")

    verified = [item for i, item in enumerate(items) if i not in invalid_indices]
    print(f"   ✅ Verified {len(verified)}/{len(items)} items (rejected {len(invalid_indices)})")
    return verified


# ── Local filters (no API call needed) ────────────────────────────────────────

def filter_items(items: list[dict], date: str) -> list[dict]:
    """Apply rule-based filters to catch obvious issues."""
    filtered = []
    for item in items:
        cat = item.get("category", "")
        start = item.get("start_time_utc")
        label = item.get("label", "")

        # Rule 1: News category without a start_time = developing story, not event
        if cat == "news" and not start:
            print(f"   🚫 Filtered (news without time): {label}")
            continue

        # Rule 2: Sports events MUST have a start_time — every match has a scheduled time
        if cat == "sports" and not start:
            print(f"   🚫 Filtered (sports without time): {label}")
            continue

        # Rule 3: If start_time is provided, check it falls on the target date in PT
        if start:
            try:
                # Parse ISO 8601
                ts_str = start.replace("Z", "+00:00")
                ts = datetime.fromisoformat(ts_str)
                ts_pt = ts.astimezone(PT)
                item_date = ts_pt.strftime("%Y-%m-%d")
                if item_date != date:
                    print(f"   🚫 Filtered (wrong date {item_date}≠{date} in PT): {label}")
                    continue
            except (ValueError, TypeError):
                pass  # Can't parse — let it through

        filtered.append(item)

    return filtered


# ── Article matching ──────────────────────────────────────────────────────────


def _build_ilike_queries(terms: list[str]) -> list[str]:
    """Build ILIKE patterns from Gemini-provided search terms.

    Splits compound terms into individual words first so "pm modi" + "new zealand"
    becomes candidates like *modi*zealand* which actually match headlines.
    Only produces two-keyword combos (both orderings). No single-keyword
    fallback — a single generic term is too likely to false-positive.
    """
    # Flatten compound terms into individual words (3+ chars)
    # Skip generic words that cause false-positive article matches
    GENERIC_STOP = {
        "new", "york", "los", "angeles", "san", "francisco", "texas",
        "washington", "super", "kings", "knight", "riders", "freedom",
        "united", "states", "india", "indian", "world", "cup", "final",
        "match", "cricket", "sports", "league", "major", "mlc", "2026",
        "men", "women", "singles", "doubles", "quarter", "semi",
    }
    words = []
    for term in terms:
        for w in term.split():
            wl = w.lower().strip()
            if len(wl) >= 3 and wl not in words and wl not in GENERIC_STOP:
                words.append(wl)

    if len(words) < 2:
        return []

    queries = []
    # All two-word combos (both orderings), capped at 10 patterns
    for i in range(min(len(words), 5)):
        for j in range(min(len(words), 5)):
            if i == j:
                continue
            q = f"*{words[i]}*{words[j]}*"
            if q not in queries:
                queries.append(q)
            if len(queries) >= 10:
                return queries
    return queries


def match_articles(items: list[dict]) -> list[dict]:
    """For each happening, search for a matching recent Videshi article.

    Rules:
    - Only link to /articles/{slug}. Never external URLs.
    - Require 2+ specific keywords from search_terms to appear in headline.
    - Articles must be from the last 3 days.
    - Default to link=None; only set when confident.
    """
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        print("   ⚠️  Supabase env not set — skipping article matching", file=sys.stderr)
        return items

    # 3-day cutoff — stale articles may be about a different match/round
    cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")

    matched = 0
    for item in items:
        item["link"] = None  # default: no link

        terms = item.get("search_terms", [])
        if len(terms) < 2:
            # Need at least 2 specific terms to avoid false positives
            continue

        ilike_patterns = _build_ilike_queries(terms)
        if not ilike_patterns:
            continue

        for pattern in ilike_patterns:
            query_url = (
                f"{sb_url}/rest/v1/p2_articles"
                f"?select=slug,headline"
                f"&status=eq.published"
                f"&headline=ilike.{pattern}"
                f"&published_at=gte.{cutoff}"
                f"&order=published_at.desc"
                f"&limit=3"
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

            if not isinstance(rows, list) or len(rows) == 0:
                continue

            # Pick the best match: most search terms found in headline
            best_slug = None
            best_score = 0
            # Flatten compound terms for counting
            flat_terms = []
            for t in terms:
                for w in t.split():
                    wl = w.lower().strip()
                    if len(wl) >= 3 and wl not in flat_terms:
                        flat_terms.append(wl)

            for row in rows:
                slug = row.get("slug", "")
                headline = (row.get("headline") or "").lower()
                if not slug:
                    continue

                # Count how many search terms appear in the headline
                hits = sum(1 for t in flat_terms if t in headline)

                # Require at least 2 matching terms
                if hits < 2:
                    continue

                if hits > best_score:
                    best_score = hits
                    best_slug = slug

            if best_slug:
                item["link"] = f"/articles/{best_slug}"
                matched += 1
                break  # stop trying more ILIKE patterns

        # Strip search_terms before DB insert (not a DB column)
        # (kept until after matching for dry-run display)

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

    # Build clean rows — strip search_terms (not a DB column)
    rows = []
    for item in items:
        row = {
            "date": date,
            "emoji": item["emoji"],
            "label": item["label"],
            "detail": item.get("detail"),
            "link": item.get("link"),
            "category": item.get("category"),
            "sort_order": item.get("sort_order", 0),
            "start_time": item.get("start_time_utc"),
        }
        rows.append(row)

    result = subprocess.run(
        [
            "curl", "-s", "-X", "POST",
            f"{sb_url}/rest/v1/daily_happenings",
            "-H", f"apikey: {sb_key}",
            "-H", f"Authorization: Bearer {sb_key}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", json.dumps(rows),
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

    return len(rows)


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
        terms = item.get("search_terms", [])
        terms_str = f"  [{', '.join(terms)}]" if terms else ""
        print(f"   {item['emoji']}  {item['label']}{detail}")
        if terms_str:
            print(f"      search_terms: {terms_str}")
    print(f"{'─' * 60}\n")

    # ── Local rule-based filters ──
    print("   Applying local filters...")
    items = filter_items(items, date)
    if not items:
        print("⚠️  All items filtered out — keeping existing happenings unchanged.")
        sys.exit(0)

    # ── Verification pass (second Gemini call) ──
    print("   Running verification pass (Gemini fact-check)...")
    items = verify_items(items, date, weekday)
    if not items:
        print("⚠️  All items rejected by verification — keeping existing happenings unchanged.")
        sys.exit(0)

    # Match happenings to published articles (only /articles/{slug}, no external)
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        print("   Matching happenings to recent articles (3-day window, ≥2 term match)...")
        items = match_articles(items)
    else:
        print("   ⚠️  Supabase env not set — skipping article matching")
        for item in items:
            item["link"] = None

    if args.dry_run:
        print("🏁 Dry run — no changes made.")
        for item in items:
            link_str = f"  → {item['link']}" if item.get("link") else "  (no match)"
            print(f"   {item['emoji']}  {item['label']}{link_str}")
        print()
        # Strip search_terms for clean JSON display
        clean = [{k: v for k, v in it.items() if k != "search_terms"} for it in items]
        print(json.dumps(clean, indent=2))
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
