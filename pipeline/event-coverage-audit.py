#!/usr/bin/env python3
"""
event-coverage-audit.py — Weekly coverage audit for Videshi events.

Reports:
- Events per state (flag states with 0 events)
- Events per source (flag sources that stopped producing)
- Events per priority metro (Edison, Jersey City, Plano, Fremont, etc.)
- Stale sources (no new events in 7 days)

Usage:
    python3 pipeline/event-coverage-audit.py              # Full audit
    python3 pipeline/event-coverage-audit.py --alert      # Exit 1 if issues found
"""

import json
import os
import sys
import subprocess
from collections import Counter
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(line_buffering=True)

ENV_FILE = os.path.expanduser("~/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REST = f"{SB_URL}/rest/v1"

# Priority metros from gap analysis (2026-10-09)
PRIORITY_METROS = {
    "Edison": "NJ",
    "Jersey City": "NJ",
    "Plano": "TX",
    "Fremont": "CA",
    "Philadelphia": "PA",
    "Charlotte": "NC",
    "Raleigh": "NC",
    "Irvine": "CA",
    "Minneapolis": "MN",
    "Portland": "OR",
    "Tampa": "FL",
    "Nashville": "TN",
}

# Well-covered reference metros
HEALTHY_METROS = {
    "New York": 20,      # minimum expected
    "Boston": 20,
    "Houston": 15,
    "San Jose": 15,
}

ALL_STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID",
              "IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS",
              "MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK",
              "OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV",
              "WI","WY","DC"]


def sb_get(path):
    cmd = ["curl", "-sS", "--max-time", "30",
           f"{REST}/{path}",
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
    return json.loads(r.stdout)


def main():
    alert_mode = "--alert" in sys.argv
    issues = []

    print("=" * 60)
    print("📊 Videshi Events Coverage Audit")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Fetch all events
    events = sb_get("events?select=id,city,state,source,created_at,date&limit=10000")
    if not isinstance(events, list):
        print("❌ Failed to fetch events")
        sys.exit(2)

    print(f"\nTotal events: {len(events)}")

    # --- Per-state coverage ---
    print("\n── Events per state ──")
    by_state = Counter(e["state"] for e in events if e.get("state"))
    missing_states = [s for s in ALL_STATES if s not in by_state]
    thin_states = {s: c for s, c in by_state.items() if c < 5}

    if missing_states:
        print(f"  ❌ Zero events: {', '.join(missing_states)}")
        issues.append(f"{len(missing_states)} states with zero events")
    else:
        print("  ✅ All 50 states + DC covered")

    if thin_states:
        print(f"  ⚠ Thin (<5 events): " +
              ", ".join(f"{s}({c})" for s, c in sorted(thin_states.items())))

    # Top/bottom
    print(f"\n  Top 5: " + ", ".join(
        f"{s}({c})" for s, c in by_state.most_common(5)))
    print(f"  Bottom 5: " + ", ".join(
        f"{s}({c})" for s, c in by_state.most_common()[-5:]))

    # --- Per-source ---
    print("\n── Events per source ──")
    by_source = Counter(e["source"] for e in events if e.get("source"))
    for src, cnt in by_source.most_common():
        print(f"  {src}: {cnt}")

    # Stale sources: no new events in 7 days
    print("\n── Source freshness (last 7 days) ──")
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    stale = []
    for src in by_source:
        recent = [e for e in events
                  if e.get("source") == src
                  and (e.get("created_at") or "") >= week_ago]
        status = "✅" if recent else "❌"
        print(f"  {status} {src}: {len(recent)} new in 7d")
        if not recent:
            stale.append(src)
    if stale:
        issues.append(f"Stale sources (0 new in 7d): {', '.join(stale)}")

    # --- Priority metros ---
    print("\n── Priority metro coverage ──")
    by_city = Counter()
    for e in events:
        city = (e.get("city") or "").strip()
        if city:
            by_city[city] += 1

    for metro, state in PRIORITY_METROS.items():
        count = sum(v for k, v in by_city.items()
                    if k.lower() == metro.lower())
        icon = "✅" if count >= 5 else ("⚠" if count > 0 else "❌")
        print(f"  {icon} {metro}, {state}: {count} events")
        if count == 0:
            issues.append(f"{metro}, {state} has zero events")

    # --- Healthy metros check ---
    print("\n── Reference metro health ──")
    for metro, minimum in HEALTHY_METROS.items():
        count = sum(v for k, v in by_city.items()
                    if k.lower() == metro.lower())
        icon = "✅" if count >= minimum else "⚠"
        print(f"  {icon} {metro}: {count} (min {minimum})")
        if count < minimum:
            issues.append(f"{metro} dropped below {minimum} ({count})")

    # --- Summary ---
    print("\n" + "=" * 60)
    if issues:
        print(f"⚠ {len(issues)} issues found:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("✅ All coverage checks passed")
    print("=" * 60)

    if alert_mode and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
