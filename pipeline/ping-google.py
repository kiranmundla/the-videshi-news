#!/usr/bin/env python3
"""
Ping Google's PubSubHubbub hub to notify about new content.
This tells Google "my feed changed, come re-crawl" — no API key or 
Search Console ownership needed.

Usage:
  python3 ping-google.py                  # Ping RSS feed
  python3 ping-google.py --sitemap        # Ping sitemap too
  python3 ping-google.py --url <url>      # Ping specific URL via IndexNow

Works via two mechanisms:
1. PubSubHubbub: pings Google's hub about RSS feed changes
2. IndexNow: pings Bing/Yandex/others about specific URLs (free, key-based)
"""

import sys
import requests

SITE = "https://www.thevideshi.com"
RSS_URL = f"{SITE}/rss.xml"
SITEMAP_URL = f"{SITE}/sitemap.xml"

# Google's PubSubHubbub hub
GOOGLE_HUB = "https://pubsubhubbub.appspot.com/"

# IndexNow endpoint (Bing, Yandex, etc.)
INDEXNOW_KEY = "e47f3c0bb278aa31c2aa883b57fac5ba"
INDEXNOW_ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
]


def ping_pubsubhubbub(feed_url=RSS_URL):
    """Ping Google's PubSubHubbub hub about feed updates."""
    resp = requests.post(
        GOOGLE_HUB,
        data={
            "hub.mode": "publish",
            "hub.url": feed_url,
        },
        timeout=15,
    )
    if resp.status_code == 204:
        print(f"✅ Google PubSubHubbub pinged: {feed_url}")
        return True
    else:
        print(f"❌ PubSubHubbub error {resp.status_code}: {resp.text}")
        return False


def ping_indexnow(urls):
    """Ping IndexNow for Bing/Yandex indexing."""
    if isinstance(urls, str):
        urls = [urls]
    
    body = {
        "host": "www.thevideshi.com",
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    
    for endpoint in INDEXNOW_ENDPOINTS:
        try:
            resp = requests.post(
                endpoint,
                json=body,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            if resp.status_code in (200, 202):
                print(f"✅ IndexNow pinged ({endpoint}): {len(urls)} URLs")
            else:
                print(f"⚠️  IndexNow {endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"⚠️  IndexNow {endpoint}: {e}")


def ping_sitemap():
    """Ping Google and Bing about sitemap updates."""
    # Google (deprecated but still sometimes works)
    try:
        resp = requests.get(
            f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
            timeout=10,
        )
        print(f"{'✅' if resp.status_code == 200 else '⚠️'} Google sitemap ping: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Google sitemap ping: {e}")
    
    # Bing
    try:
        resp = requests.get(
            f"https://www.bing.com/ping?sitemap={SITEMAP_URL}",
            timeout=10,
        )
        print(f"{'✅' if resp.status_code == 200 else '⚠️'} Bing sitemap ping: {resp.status_code}")
    except Exception as e:
        print(f"⚠️  Bing sitemap ping: {e}")


def main():
    args = sys.argv[1:]
    
    if not args:
        # Default: ping Google about RSS feed
        ping_pubsubhubbub()
        return
    
    if args[0] == "--sitemap":
        ping_pubsubhubbub()
        ping_sitemap()
        return
    
    if args[0] == "--url" and len(args) > 1:
        urls = args[1:]
        full_urls = []
        for u in urls:
            if not u.startswith("http"):
                u = f"{SITE}/articles/{u}"
            full_urls.append(u)
        ping_pubsubhubbub()
        ping_indexnow(full_urls)
        return
    
    if args[0] == "--recent":
        # Fetch recent articles and ping everything
        import os
        from datetime import datetime, timezone, timedelta
        
        env_path = os.path.expanduser("~/workspace/.env.supabase")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
        
        hours = int(args[1]) if len(args) > 1 else 4
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        
        supabase_url = os.environ.get("SUPABASE_URL", "")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        
        resp = requests.get(
            f"{supabase_url}/rest/v1/p2_articles",
            params={
                "select": "slug,headline",
                "status": "eq.published",
                "published_at": f"gte.{since}",
                "order": "published_at.desc",
                "limit": "50",
            },
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
            },
            timeout=10,
        )
        articles = resp.json() if resp.status_code == 200 else []
        
        if not articles:
            print(f"No articles in the last {hours}h")
            return
        
        urls = [f"{SITE}/articles/{a['slug']}" for a in articles if a.get("slug")]
        print(f"Found {len(urls)} articles in the last {hours}h\n")
        
        ping_pubsubhubbub()
        ping_indexnow(urls)
        print()

    print(__doc__)


if __name__ == "__main__":
    main()
