#!/usr/bin/env python3
"""
Google Indexing API client for The Videshi.
Notifies Google to crawl/index new or updated article URLs.

Usage:
  python3 google-indexing.py <slug>                    # Submit one article
  python3 google-indexing.py --recent [hours]          # Submit articles from last N hours (default: 4)
  python3 google-indexing.py --check <url>             # Check indexing status of a URL
  python3 google-indexing.py --batch <slug1> <slug2>   # Submit multiple slugs

Requires: ~/.google-indexing-key.json (service account key)
The service account must be added as Owner in Google Search Console.
"""

import sys
import os
import json
import requests
from datetime import datetime, timezone, timedelta
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/indexing"]
KEY_PATH = os.path.expanduser("~/workspace/.google-indexing-key.json")
SITE_URL = "https://www.thevideshi.com"
INDEXING_API = "https://indexing.googleapis.com/v3/urlNotifications:publish"
BATCH_API = "https://indexing.googleapis.com/batch"

# Persistent ledger of URLs already submitted to the Indexing API.
# The Indexing API counts EVERY publish request against the 200/day quota,
# even re-submissions of the same URL. The --recent window (4h) overlaps the
# cron cadence (3h), so without de-dup each article is submitted 2-3x, burning
# the daily quota on duplicates. We skip any URL submitted within the last
# LEDGER_TTL_DAYS so each article is submitted once and the budget goes to
# genuinely new URLs.
LEDGER_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/indexing-submitted.json")
LEDGER_TTL_DAYS = 14

# Google Indexing API allows 200 publish requests/day. On heavy publishing days
# the 3h cron can cumulatively cross that and 429 on every URL. We cap how many
# we submit per Pacific calendar day, leaving headroom, and let the rest ride on
# the PubSubHubbub + IndexNow pings (which have no such cap). Resets at midnight PT.
DAILY_BUDGET = int(os.environ.get("VIDESHI_INDEXING_DAILY_BUDGET", "180"))
PACIFIC_TZ = timezone(timedelta(hours=-7))  # PDT; ledger only needs day-bucketing


def submitted_today(ledger):
    """Count ledger entries submitted during the current Pacific calendar day."""
    today = datetime.now(PACIFIC_TZ).date()
    n = 0
    for ts in ledger.values():
        try:
            if datetime.fromisoformat(ts).astimezone(PACIFIC_TZ).date() == today:
                n += 1
        except (ValueError, TypeError):
            continue
    return n


def load_ledger():
    """Load the submitted-URL ledger: {url: iso_timestamp}."""
    try:
        with open(LEDGER_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_ledger(ledger):
    """Persist the ledger, pruning entries older than LEDGER_TTL_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=LEDGER_TTL_DAYS)
    pruned = {}
    for url, ts in ledger.items():
        try:
            if datetime.fromisoformat(ts) >= cutoff:
                pruned[url] = ts
        except (ValueError, TypeError):
            pruned[url] = ts  # keep unparseable entries rather than lose them
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(pruned, f, indent=2, sort_keys=True)
    os.replace(tmp, LEDGER_PATH)


def recently_submitted(url, ledger):
    """True if url was submitted within the last LEDGER_TTL_DAYS."""
    ts = ledger.get(url)
    if not ts:
        return False
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=LEDGER_TTL_DAYS)
        return datetime.fromisoformat(ts) >= cutoff
    except (ValueError, TypeError):
        return False

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def get_credentials():
    """Load service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH, scopes=SCOPES
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials


def get_access_token():
    """Get a fresh access token."""
    import google.auth.transport.requests
    credentials = service_account.Credentials.from_service_account_file(
        KEY_PATH, scopes=SCOPES
    )
    credentials.refresh(google.auth.transport.requests.Request())
    return credentials.token


def submit_url(url, action="URL_UPDATED"):
    """Submit a single URL to the Indexing API."""
    token = get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    body = {
        "url": url,
        "type": action,  # URL_UPDATED or URL_DELETED
    }
    resp = requests.post(INDEXING_API, headers=headers, json=body, timeout=15)
    data = resp.json()

    if resp.status_code == 200:
        notify_time = data.get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "")
        print(f"  ✅ {url}")
        print(f"     Notified: {notify_time}")
    else:
        error = data.get("error", {})
        print(f"  ❌ {url}")
        print(f"     Error {error.get('code')}: {error.get('message')}")

    return resp.status_code == 200


def submit_slug(slug):
    """Submit an article by slug."""
    url = f"{SITE_URL}/articles/{slug}"
    return submit_url(url)


def fetch_recent_articles(hours=4):
    """Fetch recently published articles from Supabase."""
    global SUPABASE_URL, SUPABASE_KEY
    if not SUPABASE_URL or not SUPABASE_KEY:
        # Try loading from env file
        env_path = os.path.expanduser("~/workspace/.env.supabase")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
            # Refresh module-level vars from newly loaded env
            SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
            SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            if not SUPABASE_URL or not SUPABASE_KEY:
                print("❌ Supabase credentials not found in env file")
                return []
        else:
            print("❌ Supabase credentials not found")
            return []

    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    params = {
        "select": "slug,headline,published_at",
        "status": "eq.published",
        "published_at": f"gte.{since}",
        "order": "published_at.desc",
        "limit": "50",
    }
    headers = {
        "apikey": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""),
        "Authorization": f"Bearer {os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')}",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"❌ Supabase error: {resp.status_code} (could not fetch recent articles)")
        sys.exit(1)
    return resp.json()


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    if args[0] == "--recent":
        hours = int(args[1]) if len(args) > 1 else 4
        articles = fetch_recent_articles(hours)
        if not articles:
            print(f"No articles published in the last {hours}h")
            return
        ledger = load_ledger()
        # De-dup: only submit URLs not already submitted within the TTL window.
        pending = []
        skipped = 0
        for a in articles:
            slug = a.get("slug")
            if not slug:
                continue
            url = f"{SITE_URL}/articles/{slug}"
            if recently_submitted(url, ledger):
                skipped += 1
            else:
                pending.append((slug, url))
        print(f"{len(articles)} recent articles; {skipped} already submitted (skipped), "
              f"{len(pending)} new to submit:\n")
        used_today = submitted_today(ledger)
        remaining = max(0, DAILY_BUDGET - used_today)
        if len(pending) > remaining:
            print(f"⚠️  Daily budget guard: {used_today}/{DAILY_BUDGET} already submitted today; "
                  f"capping this run to {remaining} (rest ride on IndexNow, retry after midnight PT).")
            pending = pending[:remaining]
        ok = 0
        for slug, url in pending:
            success = submit_url(url)
            if success:
                ok += 1
                ledger[url] = datetime.now(timezone.utc).isoformat()
        save_ledger(ledger)
        print(f"\n✅ {ok}/{len(pending)} submitted successfully")

    elif args[0] == "--batch":
        slugs = args[1:]
        if not slugs:
            print("Usage: google-indexing.py --batch <slug1> <slug2> ...")
            return
        print(f"Submitting {len(slugs)} URLs:\n")
        ok = 0
        for slug in slugs:
            if submit_slug(slug):
                ok += 1
        print(f"\n✅ {ok}/{len(slugs)} submitted successfully")

    elif args[0] == "--check":
        if len(args) < 2:
            print("Usage: google-indexing.py --check <url>")
            return
        url = args[1]
        if not url.startswith("http"):
            url = f"{SITE_URL}/articles/{url}"
        token = get_access_token()
        resp = requests.get(
            f"https://indexing.googleapis.com/v3/urlNotifications/metadata?url={url}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        print(json.dumps(resp.json(), indent=2))

    else:
        # Single slug
        slug = args[0]
        if slug.startswith("http"):
            submit_url(slug)
        else:
            submit_slug(slug)


if __name__ == "__main__":
    main()
