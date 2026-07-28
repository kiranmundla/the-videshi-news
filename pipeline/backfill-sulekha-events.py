#!/usr/bin/env python3
"""
backfill-sulekha-events.py — Enrich existing Sulekha events in the DB
that are missing descriptions, addresses, or have wrong categories.

Visits each event's detail page and updates:
  - long_description (if missing)
  - description (if same as title or very short)
  - street_address (if missing)
  - zip_code (if missing)
  - category (re-detect from full content)
"""

import json
import os
import re
import sys
import time

sys.stdout.reconfigure(line_buffering=True)

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q", "--break-system-packages"])
    import requests

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
SB_ACCESS = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
SB_PROJECT = os.environ.get("SUPABASE_PROJECT_REF", "lboecaekpynbpyijrbfz")
REST = f"{SB_URL}/rest/v1"
MGMT = f"https://api.supabase.com/v1/projects/{SB_PROJECT}/database/query"

HEADERS = {
    "User-Agent": "TheVideshi/1.0 (thevideshi.com; diaspora event aggregator)"
}

# Import category detection and description extraction from scraper
sys.path.insert(0, os.path.dirname(__file__))
from importlib import import_module
scraper = import_module("scrape-sulekha")
detect_category = scraper.detect_category
extract_event_description = scraper.extract_event_description


def fetch_sulekha_events():
    """Get all Sulekha events from DB."""
    try:
        r = requests.get(
            f"{REST}/events?source=eq.sulekha&select=id,title,description,long_description,street_address,zip_code,category,source_id&order=date.asc&limit=500",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        if r.status_code == 200:
            return r.json()
        else:
            print(f"⚠ Failed to fetch events: {r.status_code} {r.text[:200]}")
            return []
    except Exception as e:
        print(f"⚠ Fetch error: {e}")
        return []


def needs_enrichment(ev):
    """Check if this event needs backfill."""
    # Missing long description
    if not ev.get("long_description"):
        return True
    # Description is same as title (old scraper bug)
    if ev.get("description") == ev.get("title"):
        return True
    # Missing street address
    if not ev.get("street_address"):
        return True
    # Missing zip code
    if not ev.get("zip_code"):
        return True
    # Category is generic "Entertainment" — might be wrong
    if ev.get("category") == "Entertainment":
        return True
    return False


def update_event_mgmt(event_id, updates):
    """Update event via Management API SQL endpoint."""
    set_parts = []
    for key, val in updates.items():
        if val is None:
            set_parts.append(f"{key} = NULL")
        elif isinstance(val, str):
            escaped = val.replace("'", "''")
            set_parts.append(f"{key} = '{escaped}'")
        else:
            set_parts.append(f"{key} = {val}")

    sql = f"UPDATE events SET {', '.join(set_parts)}, updated_at = NOW() WHERE id = '{event_id}'"

    try:
        r = requests.post(
            MGMT,
            headers={
                "Authorization": f"Bearer {SB_ACCESS}",
                "Content-Type": "application/json",
            },
            json={"query": sql},
            timeout=15
        )
        return r.status_code == 200 or r.status_code == 201
    except Exception as e:
        print(f"  ⚠ Update error: {e}")
        return False


def main():
    if not SB_URL or not SB_KEY or not SB_ACCESS:
        print("ERROR: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, and SUPABASE_ACCESS_TOKEN required")
        sys.exit(1)

    events = fetch_sulekha_events()
    print(f"📊 Found {len(events)} Sulekha events in DB")

    to_enrich = [ev for ev in events if needs_enrichment(ev)]
    print(f"📋 {len(to_enrich)} need enrichment\n")

    if not to_enrich:
        print("✅ All Sulekha events are already enriched!")
        return

    session = requests.Session()
    updated = 0
    failed = 0

    for i, ev in enumerate(to_enrich):
        detail_url = ev.get("source_id", "")
        if not detail_url or not detail_url.startswith("http"):
            print(f"  [{i+1}/{len(to_enrich)}] ⚠ No detail URL for '{ev['title'][:40]}'")
            failed += 1
            continue

        print(f"  [{i+1}/{len(to_enrich)}] {ev['title'][:50]}...")

        try:
            r = session.get(detail_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    ⚠ HTTP {r.status_code}")
                failed += 1
                time.sleep(1)
                continue
        except Exception as e:
            print(f"    ⚠ Request failed: {e}")
            failed += 1
            time.sleep(1)
            continue

        html = r.text
        updates = {}

        # Extract full description
        if not ev.get("long_description"):
            long_desc = extract_event_description(html)
            if long_desc:
                updates["long_description"] = long_desc
                # Fix short description too if it's just the title
                if ev.get("description") == ev.get("title") or not ev.get("description") or len(ev.get("description", "")) < 30:
                    first_para = long_desc.split("\n")[0].strip()
                    if len(first_para) > 20:
                        updates["description"] = first_para[:500]

        # Extract street address
        if not ev.get("street_address"):
            street_match = re.search(r'"streetAddress"\s*:\s*"([^"]+)"', html)
            if street_match:
                updates["street_address"] = street_match.group(1).strip()

        # Extract zip code
        if not ev.get("zip_code"):
            postal_match = re.search(r'"postalCode"\s*:\s*"([^"]+)"', html)
            if postal_match:
                updates["zip_code"] = postal_match.group(1).strip()

        # Re-detect category
        desc_text = updates.get("long_description") or ev.get("long_description") or ev.get("description", "")
        new_cat = detect_category(ev["title"], desc_text)
        if new_cat != ev.get("category"):
            updates["category"] = new_cat

        if updates:
            success = update_event_mgmt(ev["id"], updates)
            if success:
                updated += 1
                changes = ", ".join(f"{k}={'✓' if v else '∅'}" for k, v in updates.items() if k != "description")
                print(f"    ✅ Updated: {changes}")
            else:
                failed += 1
                print(f"    ⚠ Update failed")
        else:
            print(f"    ⏭ No new data found on detail page")

        time.sleep(1.0)

    print(f"\n🏁 Backfill complete: {updated} updated, {failed} failed, {len(to_enrich) - updated - failed} unchanged")


if __name__ == "__main__":
    main()
