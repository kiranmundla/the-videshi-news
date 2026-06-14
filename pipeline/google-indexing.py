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
        print(f"❌ Supabase error: {resp.status_code}")
        return []
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
        print(f"Submitting {len(articles)} articles from the last {hours}h:\n")
        ok = 0
        for a in articles:
            if a.get("slug"):
                success = submit_slug(a["slug"])
                if success:
                    ok += 1
        print(f"\n✅ {ok}/{len(articles)} submitted successfully")

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
