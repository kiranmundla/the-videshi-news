#!/usr/bin/env python3
"""
Update Commonwealth Games 2026 medal tally for India.
Scrapes Wikipedia medal table, updates storyline metadata in Supabase.
Designed to run as part of detect-storylines cron — no new cron needed.

Exits silently if the Games are over or no storyline exists.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
STORYLINE_ID = "46e150c4-6b38-4b5e-a84b-745cb2b4877c"
WIKI_URL = "https://en.wikipedia.org/wiki/India_at_the_2026_Commonwealth_Games"
WIKI_TABLE_URL = "https://en.wikipedia.org/wiki/2026_Commonwealth_Games_medal_table"

# Games run Jul 23 – Aug 3, 2026. Stop updating after Aug 5 to avoid stale scrapes.
CUTOFF_DATE = datetime(2026, 8, 5, tzinfo=timezone.utc)


def fetch_url(url: str) -> str:
    """Fetch URL via curl (requests/urllib fail through proxy)."""
    result = subprocess.run(
        ["curl", "-sL", "-A", "TheVideshi/1.0", "--max-time", "15", url],
        capture_output=True, text=True
    )
    return result.stdout


def parse_india_from_medal_table(html: str) -> dict | None:
    """Parse India's row from the Wikipedia medal table page."""
    # Look for India's row in the medal table: | rank | India | gold | silver | bronze | total |
    # The HTML has links like >India< in table cells
    pattern = r'India</a>\s*</(?:td|th)>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>\s*<td[^>]*>(\d+)</td>'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return {
            "gold": int(match.group(1)),
            "silver": int(match.group(2)),
            "bronze": int(match.group(3)),
            "total": int(match.group(4)),
        }
    return None


def parse_india_medalists(html: str) -> list[dict]:
    """Parse individual Indian medalists from India at 2026 CWG page."""
    medalists = []

    # Look for medal rows — Wikipedia uses medal icon images with alt="Gold/Silver/Bronze"
    # Pattern: athlete name, sport, event, medal type
    # This is best-effort; if it fails, we keep existing medalists
    rows = re.findall(
        r'alt="(Gold|Silver|Bronze)[^"]*"[^<]*</(?:td|th)>\s*'
        r'(?:<td[^>]*>.*?</td>\s*)*'  # skip intermediate cells
        r'<td[^>]*>(.*?)</td>',
        html, re.DOTALL | re.IGNORECASE
    )

    # Alternative: look for structured table rows with medal, sport, event, athlete
    # Try a simpler pattern matching rows in the medals section
    medal_section = re.search(r'(?:Medals|Medal\s+summary)(.*?)(?:See also|References|External links)', html, re.DOTALL | re.IGNORECASE)
    if medal_section:
        section = medal_section.group(1)
        # Find rows with Gold/Silver/Bronze medal indicators
        for medal_match in re.finditer(
            r'alt="(Gold|Silver|Bronze)[^"]*".*?'
            r'title="[^"]*">([^<]+)</a>.*?'  # sport link
            r'(?:<td[^>]*>([^<]*)</td>)',      # event
            section, re.DOTALL
        ):
            medal_type = medal_match.group(1).lower()
            sport = medal_match.group(2).strip()
            event = medal_match.group(3).strip() if medal_match.group(3) else ""
            medalists.append({
                "medal": medal_type,
                "sport": sport,
                "event": event,
            })

    return medalists


def get_current_tracker() -> dict | None:
    """Fetch current medal_tracker from the storyline."""
    url = SUPABASE_URL.rstrip("/")
    result = subprocess.run(
        ["curl", "-s",
         f"{url}/rest/v1/storylines?id=eq.{STORYLINE_ID}&select=metadata",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True
    )
    try:
        data = json.loads(result.stdout)
        if data and isinstance(data, list) and data[0].get("metadata"):
            return data[0]["metadata"].get("medal_tracker")
    except (json.JSONDecodeError, IndexError, KeyError):
        pass
    return None


def update_tracker(tracker: dict) -> bool:
    """Update medal_tracker in storyline metadata via Management API."""
    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
    if not access_token:
        print("⚠️  No SUPABASE_ACCESS_TOKEN, skipping medal tally update")
        return False

    tracker_json = json.dumps(tracker).replace("'", "''")
    sql = f"UPDATE storylines SET metadata = jsonb_set(COALESCE(metadata, '{{}}'), '{{medal_tracker}}', '{tracker_json}'::jsonb) WHERE id = '{STORYLINE_ID}'"

    payload = json.dumps({"query": sql})
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://api.supabase.com/v1/projects/lboecaekpynbpyijrbfz/database/query",
         "-H", f"Authorization: Bearer {access_token}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )

    try:
        resp = json.loads(result.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            return True
        if isinstance(resp, dict) and "error" in resp:
            print(f"⚠️  DB error: {resp['error']}")
            return False
    except json.JSONDecodeError:
        pass

    print(f"⚠️  Unexpected response: {result.stdout[:200]}")
    return False


def main():
    # Check if Games period is over
    if datetime.now(timezone.utc) > CUTOFF_DATE:
        print("ℹ️  CWG 2026 period ended, skipping medal tally update")
        return

    # Fetch Wikipedia medal table
    print("📊 Fetching CWG 2026 medal table from Wikipedia...")
    html = fetch_url(WIKI_TABLE_URL)
    if not html or len(html) < 1000:
        print("⚠️  Failed to fetch Wikipedia medal table")
        return

    # Parse India's counts
    counts = parse_india_from_medal_table(html)
    if not counts:
        print("⚠️  Could not find India in medal table")
        return

    print(f"   India: {counts['gold']}G {counts['silver']}S {counts['bronze']}B = {counts['total']} total")

    # Get current tracker to compare
    current = get_current_tracker()
    if current:
        old_total = current.get("total", 0)
        if counts["total"] == old_total and counts["gold"] == current.get("gold", 0):
            print("ℹ️  Medal count unchanged, skipping update")
            return
        print(f"   Previous: {current.get('gold', 0)}G {current.get('silver', 0)}S {current.get('bronze', 0)}B = {old_total} total")

    # Build updated tracker
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tracker = {
        "gold": counts["gold"],
        "silver": counts["silver"],
        "bronze": counts["bronze"],
        "total": counts["total"],
        "country": "India",
        "updated": today,
        "source_url": WIKI_TABLE_URL,
        # Keep existing medalists if we have them — manual updates are more reliable
        "medalists": current.get("medalists", []) if current else [],
    }

    # Update DB
    if update_tracker(tracker):
        print(f"✅ Medal tally updated: {counts['gold']}G {counts['silver']}S {counts['bronze']}B = {counts['total']}")
    else:
        print("⚠️  Failed to update medal tally in DB")


if __name__ == "__main__":
    main()
