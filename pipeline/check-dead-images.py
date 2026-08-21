#!/usr/bin/env python3
"""
check-dead-images.py — Scan published articles and diaspora leaders for broken image URLs.
Nulls out any image_url / photo_url that returns 404 or other errors.

Strategy:
  - Always check ALL Wikimedia/Wikipedia URLs (these get deleted)
  - Check non-Wikimedia article images only from the last 30 days
  - Always check ALL diaspora_leaders photos (only ~225)
  - Rate-limit: 0.1s sleep between requests
  - Uses curl subprocess (Python requests/urllib fail through proxy)
"""

import json
import os
import subprocess
import sys
import time

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"].strip().strip('"')

HEADERS_CLI = [
    "-H", f"apikey: {SUPABASE_KEY}",
    "-H", f"Authorization: Bearer {SUPABASE_KEY}",
]

BATCH_SIZE = 500          # Supabase pagination
CHECK_SLEEP = 0.1         # seconds between image checks
RECENT_DAYS = 30          # non-Wikimedia: only check articles this recent
TIMEOUT_SECS = 10         # per-image curl timeout


def sb_get(table, select, filters, limit=BATCH_SIZE, offset=0):
    """Fetch rows from Supabase via curl."""
    url = (
        f"{SUPABASE_URL}/rest/v1/{table}"
        f"?select={select}&{filters}&limit={limit}&offset={offset}"
    )
    result = subprocess.run(
        ["curl", "-s", url] + HEADERS_CLI,
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"  [ERROR] curl failed for {table}: {result.stderr}", flush=True)
        return []
    try:
        data = json.loads(result.stdout)
        if isinstance(data, dict) and "code" in data:
            print(f"  [ERROR] Supabase error: {data.get('message')}", flush=True)
            return []
        return data
    except json.JSONDecodeError:
        print(f"  [ERROR] Bad JSON from {table}: {result.stdout[:200]}", flush=True)
        return []


def sb_patch(table, filters, payload):
    """PATCH a row in Supabase via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}"
    result = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url]
        + HEADERS_CLI
        + ["-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=15,
    )
    return result.returncode == 0


def fetch_all(table, select, filters):
    """Paginate through all matching rows."""
    rows = []
    offset = 0
    while True:
        batch = sb_get(table, select, filters, limit=BATCH_SIZE, offset=offset)
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < BATCH_SIZE:
            break
        offset += BATCH_SIZE
    return rows


def check_image_url(url):
    """
    Check if an image URL is alive via HEAD request.
    Returns (alive: bool, status_code: int|None).
    For Wikimedia, sets a custom User-Agent.
    """
    is_wikimedia = "wikimedia.org" in url or "wikipedia.org" in url

    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-I",
        "--max-time", str(TIMEOUT_SECS),
        "-L",   # follow redirects
    ]
    if is_wikimedia:
        cmd += ["-A", "TheVideshi/1.0"]
    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECS + 5)
        code_str = result.stdout.strip()
        if code_str.isdigit():
            code = int(code_str)
            # Treat 400 from Wikimedia as alive (known quirk, may recur)
            if is_wikimedia and code == 400:
                return True, code
            alive = 200 <= code < 400
            return alive, code
        return False, None
    except (subprocess.TimeoutExpired, Exception) as e:
        return False, None


def main():
    print("=== Dead Image Checker ===", flush=True)
    start = time.time()

    broken_articles = []
    broken_leaders = []
    checked = 0

    # ── 1. Articles with Wikimedia URLs (always check all) ──
    print("\n[1/3] Fetching articles with Wikimedia image URLs...", flush=True)
    wiki_articles = fetch_all(
        "p2_articles",
        "id,slug,headline,image_url",
        "status=eq.published&image_url=not.is.null&or=(image_url.like.*wikimedia.org*,image_url.like.*wikipedia.org*)",
    )
    print(f"  Found {len(wiki_articles)} articles with Wikimedia images", flush=True)

    for art in wiki_articles:
        alive, code = check_image_url(art["image_url"])
        checked += 1
        if not alive:
            print(f"  BROKEN [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            broken_articles.append(art)
        if checked % 200 == 0:
            print(f"  ... checked {checked} images so far", flush=True)
        time.sleep(CHECK_SLEEP)

    # ── 2. Recent non-Wikimedia articles (last 30 days) ──
    print(f"\n[2/3] Fetching recent non-Wikimedia articles (last {RECENT_DAYS} days)...", flush=True)
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - RECENT_DAYS * 86400))
    recent_articles = fetch_all(
        "p2_articles",
        "id,slug,headline,image_url",
        f"status=eq.published&image_url=not.is.null&image_url=not.like.*wikimedia*&image_url=not.like.*wikipedia*&published_at=gte.{cutoff}",
    )
    print(f"  Found {len(recent_articles)} recent non-Wikimedia articles", flush=True)

    for art in recent_articles:
        alive, code = check_image_url(art["image_url"])
        checked += 1
        if not alive:
            print(f"  BROKEN [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            broken_articles.append(art)
        if checked % 200 == 0:
            print(f"  ... checked {checked} images so far", flush=True)
        time.sleep(CHECK_SLEEP)

    # ── 3. Diaspora leaders ──
    print("\n[3/3] Fetching diaspora leaders with photos...", flush=True)
    leaders = fetch_all(
        "diaspora_leaders",
        "id,name,photo_url",
        "photo_url=not.is.null",
    )
    print(f"  Found {len(leaders)} leaders with photos", flush=True)

    for leader in leaders:
        alive, code = check_image_url(leader["photo_url"])
        checked += 1
        if not alive:
            print(f"  BROKEN [{code}] leader '{leader['name']}': {leader['photo_url'][:80]}", flush=True)
            broken_leaders.append(leader)
        time.sleep(CHECK_SLEEP)

    # ── Fix broken URLs ──
    fixed_articles = 0
    fixed_leaders = 0

    if broken_articles:
        print(f"\nFixing {len(broken_articles)} broken article images...", flush=True)
        for art in broken_articles:
            ok = sb_patch("p2_articles", f"id=eq.{art['id']}", {"image_url": None, "image_caption": None})
            if ok:
                fixed_articles += 1
                print(f"  FIXED: {art['slug']}", flush=True)
            else:
                print(f"  FAILED to fix: {art['slug']}", flush=True)

    if broken_leaders:
        print(f"\nFixing {len(broken_leaders)} broken leader photos...", flush=True)
        for leader in broken_leaders:
            ok = sb_patch("diaspora_leaders", f"id=eq.{leader['id']}", {"photo_url": None})
            if ok:
                fixed_leaders += 1
                print(f"  FIXED: {leader['name']}", flush=True)
            else:
                print(f"  FAILED to fix: {leader['name']}", flush=True)

    # ── Summary ──
    elapsed = time.time() - start
    print(f"\n=== Summary ===", flush=True)
    print(f"  Images checked: {checked}", flush=True)
    print(f"  Broken found:   {len(broken_articles)} articles, {len(broken_leaders)} leaders", flush=True)
    print(f"  Fixed:           {fixed_articles} articles, {fixed_leaders} leaders", flush=True)
    print(f"  Elapsed:         {elapsed:.1f}s", flush=True)

    if broken_articles or broken_leaders:
        print(f"\nBroken URLs cleared:", flush=True)
        for art in broken_articles:
            print(f"  article: {art['headline'][:70]}", flush=True)
        for leader in broken_leaders:
            print(f"  leader:  {leader['name']}", flush=True)

    # Exit 0 even if we found broken images (we fixed them)
    # Exit 1 only if the script itself had errors
    sys.exit(0)


if __name__ == "__main__":
    main()
