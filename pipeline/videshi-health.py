#!/usr/bin/env python3
"""
videshi-health.py — Pipeline health monitor for The Videshi.
Run by Hatch cron every 6 hours. Checks for:
  1. Stale publishing (>6h since last article + unprocessed signals exist)
  2. Articles stuck in 'review' status → auto-publish them
  3. Published articles with null published_at → fix them
  4. Published articles older than 7 days → archive them (set status=archived)

Usage:
  python3 videshi-health.py check     — Run all health checks, print JSON report
  python3 videshi-health.py fix       — Run checks AND auto-fix issues found
"""

import json
import sys
import os
import requests
from datetime import datetime, timezone, timedelta

SB_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SB_KEY:
    # Try loading from .env.supabase
    env_path = os.path.expanduser("~/workspace/.env.supabase")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SB_KEY = line.split("=", 1)[1].strip()
REST = f"{SB_URL}/rest/v1"
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}


def sb_get(table, params):
    r = requests.get(f"{REST}/{table}?{params}", headers=HEADERS)
    return r.json() if r.ok else []


def sb_get_count(table, params):
    h = {**HEADERS, "Prefer": "count=exact"}
    r = requests.get(f"{REST}/{table}?{params}&select=id&limit=1", headers=h)
    cr = r.headers.get("content-range", "")
    try:
        return int(cr.split("/")[1])
    except:
        return 0


def sb_patch(table, filters, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{REST}/{table}?{filters}", headers=h, json=data)
    return r.json() if r.ok and r.text else []


def check_stale_publishing():
    """Check if no articles were published in the last 6 hours while signals are waiting."""
    cutoff_6h = (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
    recent = sb_get("p2_articles",
        f"status=eq.published&published_at=gte.{cutoff_6h}&select=id&limit=1")
    has_recent = len(recent) > 0

    cutoff_48h = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    unprocessed_count = sb_get_count("p2_signals",
        f"is_processed=eq.false&published_at=gte.{cutoff_48h}")

    stale = not has_recent and unprocessed_count > 0
    return {
        "check": "stale_publishing",
        "stale": stale,
        "has_recent_articles": has_recent,
        "unprocessed_signals": unprocessed_count,
        "action_needed": "trigger_writer" if stale else None,
    }


def check_stuck_review(fix=False):
    """Find articles stuck in 'review' status and optionally auto-publish."""
    stuck = sb_get("p2_articles",
        "status=eq.review&select=id,headline&limit=50")
    fixed = 0
    if fix and stuck:
        now = datetime.now(timezone.utc).isoformat()
        result = sb_patch("p2_articles", "status=eq.review",
            {"status": "published", "published_at": now})
        fixed = len(result) if isinstance(result, list) else 0
    return {
        "check": "stuck_review",
        "count": len(stuck),
        "fixed": fixed,
        "headlines": [a["headline"] for a in stuck[:5]],
    }


def check_null_published_at(fix=False):
    """Find published articles with null published_at and optionally fix."""
    broken = sb_get("p2_articles",
        "status=eq.published&published_at=is.null&select=id,headline&limit=50")
    fixed = 0
    if fix and broken:
        now = datetime.now(timezone.utc).isoformat()
        result = sb_patch("p2_articles", "status=eq.published&published_at=is.null",
            {"published_at": now})
        fixed = len(result) if isinstance(result, list) else 0
    return {
        "check": "null_published_at",
        "count": len(broken),
        "fixed": fixed,
    }


def check_aged_articles(fix=False):
    """Archive articles older than 7 days to keep the site fresh."""
    cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    # Only count non-travel articles (travel guides are evergreen)
    old = sb_get("p2_articles",
        f"status=eq.published&published_at=lt.{cutoff_7d}&category=neq.travel&select=id&limit=200")
    archived = 0
    if fix and old:
        result = sb_patch("p2_articles",
            f"status=eq.published&published_at=lt.{cutoff_7d}&category=neq.travel",
            {"status": "archived"})
        archived = len(result) if isinstance(result, list) else 0
    return {
        "check": "aged_articles",
        "older_than_7d": len(old),
        "archived": archived,
    }


def run_all(fix=False):
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "fix" if fix else "check",
        "checks": [
            check_stale_publishing(),
            check_stuck_review(fix=fix),
            check_null_published_at(fix=fix),
            check_aged_articles(fix=fix),
        ],
    }

    # Compute overall health
    issues = sum(1 for c in report["checks"]
                 if c.get("stale") or c.get("count", 0) > 0 or c.get("older_than_7d", 0) > 0)
    report["health"] = "healthy" if issues == 0 else f"{issues} issue(s) found"

    return report


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    fix = mode == "fix"
    report = run_all(fix=fix)
    print(json.dumps(report, indent=2))
