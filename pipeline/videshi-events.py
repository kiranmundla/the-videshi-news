#!/usr/bin/env python3
"""
videshi-events.py — Watched Events detector for The Videshi pipeline.

Called by the videshi-live cron after data refresh. Checks recent signals
against watched events config and determines if the writer should be
triggered for event-specific article coverage.

Usage:
    python3 videshi-events.py check              # Check for triggerable events
    python3 videshi-events.py status             # Show active events and last articles
    python3 videshi-events.py update-state <id> <headline>  # Record published article
    python3 videshi-events.py add '<json>'       # Add a watched event
    python3 videshi-events.py deactivate <id>    # Deactivate an event
    python3 videshi-events.py activate <id>      # Activate an event
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone, timedelta

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watched-events.json")
STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watched-events-state.json")

# ---------------------------------------------------------------------------
# Supabase env
# ---------------------------------------------------------------------------
ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

# ---------------------------------------------------------------------------
# Config & State helpers
# ---------------------------------------------------------------------------

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"events": []}
    return json.load(open(CONFIG_PATH))

def save_config(config):
    json.dump(config, open(CONFIG_PATH, "w"), indent=2)
    print(f"  Saved config with {len(config.get('events', []))} events")

def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    return json.load(open(STATE_PATH))

def save_state(state):
    json.dump(state, open(STATE_PATH, "w"), indent=2)

# ---------------------------------------------------------------------------
# Supabase queries
# ---------------------------------------------------------------------------

def get_recent_signals(hours=4):
    """Fetch unprocessed signals from last N hours."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_signals",
            headers=HEADERS,
            params={
                "published_at": f"gte.{cutoff}",
                "order": "published_at.desc",
                "limit": "100",
                "select": "id,title,feed_source_id,published_at"
            },
            timeout=15
        )
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"  ⚠ Error fetching signals: {e}")
        return []

def get_recent_articles_for_category(category, hours=24):
    """Fetch recent published articles in a category (for dedup context)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            headers=HEADERS,
            params={
                "status": "eq.published",
                "category": f"eq.{category}",
                "published_at": f"gte.{cutoff}",
                "order": "published_at.desc",
                "limit": "10",
                "select": "id,headline,published_at"
            },
            timeout=15
        )
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        print(f"  ⚠ Error fetching articles: {e}")
        return []

# ---------------------------------------------------------------------------
# Event detection logic
# ---------------------------------------------------------------------------

def matches_event(signal_title, event):
    """Check if a signal title matches an event's keywords."""
    title_lower = signal_title.lower()
    return any(kw.lower() in title_lower for kw in event["keywords"])

def is_new_phase(signal_titles, last_headline, phase_change_words):
    """
    Detect if signals represent a new phase vs the last published article.
    Returns (bool, reason_string).
    """
    if not last_headline:
        return True, "first_coverage"

    last_lower = last_headline.lower()

    for title in signal_titles:
        title_lower = title.lower()
        for word in phase_change_words:
            wl = word.lower()
            if wl in title_lower and wl not in last_lower:
                return True, f"phase_word:{word} in '{title[:60]}'"

    return False, ""

def cmd_check():
    """Main check: detect triggerable events and output JSON recommendations."""
    config = load_config()
    state = load_state()

    active_events = [e for e in config["events"] if e.get("active")]
    if not active_events:
        print(json.dumps({"trigger": False, "reason": "No active watched events"}))
        return

    signals = get_recent_signals(hours=4)
    if not signals:
        print(json.dumps({"trigger": False, "reason": "No recent signals"}))
        return

    triggers = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for event in active_events:
        event_id = event["id"]
        matching_signals = [s for s in signals if matches_event(s.get("title", ""), event)]

        if len(matching_signals) < 2:
            continue  # Need at least 2 signals to form a cluster

        # Load event state
        event_state = state.get(event_id, {})
        last_headline = event_state.get("last_headline", "")
        last_published = event_state.get("last_published", "")

        # Daily article counter — reset on new day
        articles_today = event_state.get("articles_today", 0)
        if event_state.get("date") != today:
            articles_today = 0

        # Check daily cap
        max_per_day = event.get("max_articles_per_day", 3)
        if articles_today >= max_per_day:
            print(f"  ⏭ {event['name']}: daily cap reached ({articles_today}/{max_per_day})")
            continue

        signal_titles = [s["title"] for s in matching_signals]
        phase_words = event.get("phase_change_words", [])

        # Hours since last article on this event
        hours_since_last = 999
        if last_published:
            try:
                last_dt = datetime.fromisoformat(last_published.replace("Z", "+00:00"))
                hours_since_last = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
            except Exception:
                pass

        new_phase, phase_reason = is_new_phase(signal_titles, last_headline, phase_words)
        time_trigger = hours_since_last > 6

        if new_phase or time_trigger:
            reason = f"new_phase ({phase_reason})" if new_phase else f"time_gap ({hours_since_last:.1f}h)"
            triggers.append({
                "event_id": event_id,
                "event_name": event["name"],
                "category": event["category"],
                "priority": event.get("priority", "normal"),
                "matching_signals": len(matching_signals),
                "signal_titles": signal_titles[:5],
                "reason": reason,
                "last_headline": last_headline or "(none)",
                "hours_since_last": round(hours_since_last, 1),
                "articles_today": articles_today,
                "max_per_day": max_per_day,
            })

    if triggers:
        result = {"trigger": True, "events": triggers}
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"trigger": False, "reason": "No new phases detected for active events"}))

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def cmd_update_state(event_id, headline):
    """Update state after an article is published for a watched event."""
    state = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if event_id not in state:
        state[event_id] = {}

    if state[event_id].get("date") != today:
        state[event_id]["articles_today"] = 0
        state[event_id]["date"] = today

    state[event_id]["last_headline"] = headline
    state[event_id]["last_published"] = datetime.now(timezone.utc).isoformat()
    state[event_id]["articles_today"] = state[event_id].get("articles_today", 0) + 1
    save_state(state)
    print(json.dumps({
        "ok": True,
        "event_id": event_id,
        "articles_today": state[event_id]["articles_today"],
        "headline": headline,
    }))

# ---------------------------------------------------------------------------
# Config management
# ---------------------------------------------------------------------------

def cmd_status():
    """Show status of all watched events."""
    config = load_config()
    state = load_state()
    print("=== Watched Events Status ===")
    for event in config["events"]:
        eid = event["id"]
        active = "✅ ACTIVE" if event.get("active") else "❌ inactive"
        es = state.get(eid, {})
        last = es.get("last_headline", "(no articles yet)")
        count = es.get("articles_today", 0)
        max_d = event.get("max_articles_per_day", 3)
        last_pub = es.get("last_published", "never")
        print(f"\n  {active}  {event['name']} [{eid}]")
        print(f"    Category: {event['category']} | Priority: {event.get('priority','normal')}")
        print(f"    Keywords: {', '.join(event['keywords'][:5])}")
        print(f"    Articles today: {count}/{max_d}")
        print(f"    Last article: {last[:80]}")
        print(f"    Last published: {last_pub}")

def cmd_add(event_json):
    """Add a new watched event from JSON."""
    config = load_config()
    try:
        new_event = json.loads(event_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON — {e}")
        sys.exit(1)

    required = ["id", "name", "keywords", "category"]
    for field in required:
        if field not in new_event:
            print(f"Error: Missing required field '{field}'")
            sys.exit(1)

    # Defaults
    new_event.setdefault("active", True)
    new_event.setdefault("priority", "normal")
    new_event.setdefault("phase_change_words", [])
    new_event.setdefault("max_articles_per_day", 3)

    # Check for duplicate id
    existing_ids = {e["id"] for e in config["events"]}
    if new_event["id"] in existing_ids:
        print(f"Error: Event '{new_event['id']}' already exists. Use deactivate/activate.")
        sys.exit(1)

    config["events"].append(new_event)
    save_config(config)
    print(json.dumps({"ok": True, "added": new_event["id"], "name": new_event["name"]}))

def cmd_toggle(event_id, active):
    """Activate or deactivate an event."""
    config = load_config()
    found = False
    for event in config["events"]:
        if event["id"] == event_id:
            event["active"] = active
            found = True
            break
    if not found:
        print(f"Error: Event '{event_id}' not found")
        sys.exit(1)
    save_config(config)
    status = "activated" if active else "deactivated"
    print(json.dumps({"ok": True, "event_id": event_id, "status": status}))

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        cmd_check()
    elif cmd == "status":
        cmd_status()
    elif cmd == "update-state":
        if len(sys.argv) >= 4:
            cmd_update_state(sys.argv[2], " ".join(sys.argv[3:]))
        else:
            print("Usage: videshi-events.py update-state <event_id> <headline>")
            sys.exit(1)
    elif cmd == "add":
        if len(sys.argv) >= 3:
            cmd_add(sys.argv[2])
        else:
            print("Usage: videshi-events.py add '<json>'")
            sys.exit(1)
    elif cmd == "deactivate":
        if len(sys.argv) >= 3:
            cmd_toggle(sys.argv[2], False)
        else:
            print("Usage: videshi-events.py deactivate <event_id>")
            sys.exit(1)
    elif cmd == "activate":
        if len(sys.argv) >= 3:
            cmd_toggle(sys.argv[2], True)
        else:
            print("Usage: videshi-events.py activate <event_id>")
            sys.exit(1)
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: check, status, update-state, add, deactivate, activate")
        sys.exit(1)
