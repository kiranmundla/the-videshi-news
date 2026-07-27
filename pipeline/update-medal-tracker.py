#!/usr/bin/env python3
"""
Generic medal tracker updater for developing stories.

Finds all active storylines with a medal_tracker in metadata,
scrapes the Wikipedia medal table source URL for the tracked country,
and updates the counts if they changed.

Works for any multi-sport event (CWG, Olympics, Asian Games, etc.)
as long as the storyline metadata has:
  medal_tracker.source_url — Wikipedia medal table page
  medal_tracker.country    — country name to look for (default: "India")

Usage:
  python3 update-medal-tracker.py          # update all active trackers
  python3 update-medal-tracker.py --dry-run  # preview changes
"""

import os, sys, json, re, subprocess

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

def supabase_get(path):
    """GET from Supabase REST API."""
    url = f"https://{SUPABASE_URL.replace('https://', '')}/rest/v1/{path}"
    r = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(r.stdout) if r.stdout.strip() else []

def supabase_patch(table, filter_str, data):
    """PATCH Supabase REST API."""
    url = f"https://{SUPABASE_URL.replace('https://', '')}/rest/v1/{table}?{filter_str}"
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", json.dumps(data)],
        capture_output=True, text=True, timeout=30
    )
    return r.returncode == 0

def fetch_wikipedia_medal_table(source_url, country="India"):
    """
    Scrape a Wikipedia medal table page and extract the row for a country.
    Returns (gold, silver, bronze, total) or None if not found.
    """
    r = subprocess.run(
        ["curl", "-sL", source_url,
         "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode != 0 or not r.stdout:
        print(f"  ✗ Failed to fetch {source_url}")
        return None

    html = r.stdout

    # Wikipedia medal tables use <th> for the country cell (with flag img + link),
    # followed by <td> cells for gold, silver, bronze, total:
    #   <th ...>...<a ...>India</a></th><td>1</td><td>3</td><td>2</td><td>6</td>
    # The closing tag before medal cells can be </th> or </td>.
    four_medals = r'<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>\s*(\d+)\s*</td>'
    patterns = [
        # Country link inside <th> (standard Wikipedia medal table)
        rf'>\s*{re.escape(country)}\s*</a>.*?</th>\s*{four_medals}',
        # Country link inside <td>
        rf'>\s*{re.escape(country)}\s*</a>.*?</td>\s*{four_medals}',
        # Country as plain text in <th>
        rf'>\s*{re.escape(country)}\s*</th>\s*{four_medals}',
        # Country as plain text in <td>
        rf'>\s*{re.escape(country)}\s*</td>\s*{four_medals}',
        # Broadest: country name anywhere, then 4 consecutive <td> numbers
        rf'{re.escape(country)}.*?</t[hd]>\s*{four_medals}',
    ]

    for source_html in [html]:
        for pat in patterns:
            m = re.search(pat, source_html, re.DOTALL | re.IGNORECASE)
            if m:
                g, s, b, t = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                return (g, s, b, t)

    # Fallback: try REST API for potentially cleaner HTML
    wiki_title = source_url.split("/wiki/")[-1] if "/wiki/" in source_url else None
    if wiki_title:
        r2 = subprocess.run(
            ["curl", "-s",
             f"https://en.wikipedia.org/api/rest_v1/page/html/{wiki_title}",
             "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)"],
            capture_output=True, text=True, timeout=30
        )
        if r2.returncode == 0 and r2.stdout:
            for pat in patterns:
                m = re.search(pat, r2.stdout, re.DOTALL | re.IGNORECASE)
                if m:
                    g, s, b, t = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
                    return (g, s, b, t)

    print(f"  ✗ Could not find {country} in medal table at {source_url}")
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    # Find all active storylines with medal_tracker metadata
    storylines = supabase_get("storylines?select=id,slug,title,metadata&status=eq.active")
    
    trackers = []
    for s in storylines:
        meta = s.get("metadata") or {}
        mt = meta.get("medal_tracker")
        if mt and mt.get("source_url"):
            trackers.append(s)

    if not trackers:
        # No active trackers — exit silently (cron-friendly)
        return

    print(f"Found {len(trackers)} storyline(s) with medal trackers\n")

    for s in trackers:
        meta = s["metadata"]
        mt = meta["medal_tracker"]
        country = mt.get("country", "India")
        source_url = mt["source_url"]

        print(f"📊 {s['title']}")
        print(f"   Source: {source_url}")
        print(f"   Tracking: {country}")
        print(f"   Current: {mt.get('gold',0)}G {mt.get('silver',0)}S {mt.get('bronze',0)}B = {mt.get('total',0)}")

        result = fetch_wikipedia_medal_table(source_url, country)
        if result is None:
            print(f"   ✗ Could not fetch updated tally\n")
            continue

        gold, silver, bronze, total = result
        print(f"   Wikipedia: {gold}G {silver}S {bronze}B = {total}")

        # Check if anything changed
        if (gold == mt.get("gold", 0) and silver == mt.get("silver", 0)
                and bronze == mt.get("bronze", 0)):
            print(f"   ✓ No change\n")
            continue

        # Update
        from datetime import date
        mt["gold"] = gold
        mt["silver"] = silver
        mt["bronze"] = bronze
        mt["total"] = total
        mt["updated"] = date.today().isoformat()

        if dry_run:
            print(f"   [DRY RUN] Would update to {gold}G {silver}S {bronze}B = {total}\n")
        else:
            meta["medal_tracker"] = mt
            if supabase_patch("storylines", f"id=eq.{s['id']}", {"metadata": meta}):
                print(f"   ✅ Updated to {gold}G {silver}S {bronze}B = {total}\n")
            else:
                print(f"   ✗ Update failed\n")


if __name__ == "__main__":
    main()
