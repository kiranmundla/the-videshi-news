#!/usr/bin/env python3
"""
check-dead-images.py — Scan published articles and diaspora leaders for broken image URLs.
Nulls out any image_url / photo_url that returns 404/410/other definitive errors.

Strategy:
  - Check Wikimedia/Wikipedia URLs in rotating batches (~1000/run)
  - Check non-Wikimedia article images only from the last 30 days
  - Always check ALL diaspora_leaders photos (only ~225)
  - Sequential with 1s sleep to avoid proxy rate limits
  - Retry once on connection failures (code 000)
  - Only treat 404, 410, 403 as broken — skip transient failures (000, 5xx)
  - Uses curl subprocess (Python requests/urllib fail through proxy)
  - Tracks rotation offset in a state file
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
WIKI_PER_RUN = 1000       # max Wikimedia images per run (rotate through all)
RECENT_DAYS = 30          # non-Wikimedia: only check articles this recent
TIMEOUT_SECS = 15         # per-image curl timeout
CHECK_SLEEP = 1.0         # seconds between checks — gentle on proxy
RETRY_SLEEP = 5.0         # seconds before retry on connection failure
BROKEN_CODES = {404, 410} # definitively broken — null out
SUSPICIOUS_CODES = {403}  # may be rate limit OR genuinely gone — flag but don't fix
STATE_FILE = os.path.join(os.path.dirname(__file__), ".dead-images-offset.json")


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
    Returns (status: str, code: int|None).
    status is one of: "alive", "broken", "suspicious", "skip"
    """
    is_wikimedia = "wikimedia.org" in url or "wikipedia.org" in url

    def _head(u):
        cmd = [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
            "-I",
            "--max-time", str(TIMEOUT_SECS),
            "-L",
        ]
        if is_wikimedia:
            cmd += ["-A", "TheVideshi/1.0"]
        cmd.append(u)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_SECS + 5)
            code_str = result.stdout.strip()
            return int(code_str) if code_str.isdigit() else 0
        except (subprocess.TimeoutExpired, Exception):
            return 0

    code = _head(url)

    # Connection failure — retry once
    if code == 0:
        time.sleep(RETRY_SLEEP)
        code = _head(url)

    if code == 0:
        return "skip", 0          # transient network issue, don't act
    if 200 <= code < 400:
        return "alive", code
    if is_wikimedia and code == 400:
        return "alive", code      # Wikimedia HEAD quirk
    if code in BROKEN_CODES:
        return "broken", code
    if code in SUSPICIOUS_CODES:
        return "suspicious", code
    if code >= 500:
        return "skip", code       # server error, transient
    return "broken", code         # other 4xx


def load_offset():
    """Load the rotation offset for Wikimedia scanning."""
    try:
        with open(STATE_FILE) as f:
            return json.load(f).get("offset", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def save_offset(offset):
    """Save the rotation offset."""
    with open(STATE_FILE, "w") as f:
        json.dump({"offset": offset, "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)


def main():
    print("=== Dead Image Checker ===", flush=True)
    start = time.time()

    broken_articles = []
    suspicious_articles = []
    broken_leaders = []
    total_checked = 0
    total_skipped = 0
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 10  # abort if proxy is down

    # ── 1. Articles with Wikimedia URLs (rotating batch) ──
    print("\n[1/3] Fetching Wikimedia article count...", flush=True)
    # Get total count first
    all_wiki = fetch_all(
        "p2_articles",
        "id",
        "status=eq.published&image_url=not.is.null&or=(image_url.like.*wikimedia.org*,image_url.like.*wikipedia.org*)",
    )
    total_wiki = len(all_wiki)
    offset = load_offset()
    if offset >= total_wiki:
        offset = 0  # wrap around

    print(f"  Total Wikimedia articles: {total_wiki}, starting at offset {offset}", flush=True)

    wiki_batch = sb_get(
        "p2_articles",
        "id,slug,headline,image_url",
        "status=eq.published&image_url=not.is.null&or=(image_url.like.*wikimedia.org*,image_url.like.*wikipedia.org*)&order=id",
        limit=WIKI_PER_RUN,
        offset=offset,
    )
    print(f"  Checking {len(wiki_batch)} Wikimedia images (batch {offset}–{offset + len(wiki_batch)})...", flush=True)

    for art in wiki_batch:
        status, code = check_image_url(art["image_url"])
        total_checked += 1

        if status == "broken":
            print(f"  BROKEN [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            broken_articles.append(art)
            consecutive_failures = 0
        elif status == "suspicious":
            print(f"  SUSPICIOUS [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            suspicious_articles.append(art)
            consecutive_failures = 0
        elif status == "skip":
            total_skipped += 1
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"  ABORT: {MAX_CONSECUTIVE_FAILURES} consecutive connection failures — proxy may be down", flush=True)
                break
        else:
            consecutive_failures = 0

        if total_checked % 200 == 0:
            print(f"  ... checked {total_checked} (skipped {total_skipped})", flush=True)

        time.sleep(CHECK_SLEEP)

    # Save next offset for rotation
    next_offset = offset + len(wiki_batch)
    if next_offset >= total_wiki:
        next_offset = 0
    save_offset(next_offset)

    # Early abort if proxy is completely down
    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        print(f"\nProxy appears down. Checked {total_checked}, skipped {total_skipped}.", flush=True)
        print("Exiting without fixing anything (all failures may be transient).", flush=True)
        sys.exit(0)

    # ── 2. Recent non-Wikimedia articles (last 30 days) ──
    print(f"\n[2/3] Fetching recent non-Wikimedia articles (last {RECENT_DAYS} days)...", flush=True)
    cutoff = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - RECENT_DAYS * 86400))
    recent_articles = fetch_all(
        "p2_articles",
        "id,slug,headline,image_url",
        f"status=eq.published&image_url=not.is.null&image_url=not.like.*wikimedia*&image_url=not.like.*wikipedia*&published_at=gte.{cutoff}",
    )
    print(f"  Found {len(recent_articles)} recent non-Wikimedia articles", flush=True)

    consecutive_failures = 0
    for art in recent_articles:
        status, code = check_image_url(art["image_url"])
        total_checked += 1

        if status == "broken":
            print(f"  BROKEN [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            broken_articles.append(art)
            consecutive_failures = 0
        elif status == "suspicious":
            print(f"  SUSPICIOUS [{code}] {art['slug']}: {art['image_url'][:80]}", flush=True)
            suspicious_articles.append(art)
            consecutive_failures = 0
        elif status == "skip":
            total_skipped += 1
            consecutive_failures += 1
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                print(f"  ABORT: proxy appears down", flush=True)
                break
        else:
            consecutive_failures = 0

        time.sleep(CHECK_SLEEP)

    # ── 3. Diaspora leaders ──
    if consecutive_failures < MAX_CONSECUTIVE_FAILURES:
        print("\n[3/3] Fetching diaspora leaders with photos...", flush=True)
        leaders = fetch_all(
            "diaspora_leaders",
            "id,name,photo_url",
            "photo_url=not.is.null",
        )
        print(f"  Found {len(leaders)} leaders with photos", flush=True)

        consecutive_failures = 0
        for leader in leaders:
            status, code = check_image_url(leader["photo_url"])
            total_checked += 1

            if status == "broken":
                print(f"  BROKEN [{code}] leader '{leader['name']}': {leader['photo_url'][:80]}", flush=True)
                broken_leaders.append(leader)
                consecutive_failures = 0
            elif status == "skip":
                total_skipped += 1
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    print(f"  ABORT: proxy appears down", flush=True)
                    break
            else:
                consecutive_failures = 0

            time.sleep(CHECK_SLEEP)

    # ── Fix broken URLs (only definitive 404/410) ──
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
    print(f"  Images checked:  {total_checked}", flush=True)
    print(f"  Skipped (conn):  {total_skipped}", flush=True)
    print(f"  Broken found:    {len(broken_articles)} articles, {len(broken_leaders)} leaders", flush=True)
    print(f"  Suspicious:      {len(suspicious_articles)} articles", flush=True)
    print(f"  Fixed:           {fixed_articles} articles, {fixed_leaders} leaders", flush=True)
    print(f"  Elapsed:         {elapsed:.1f}s", flush=True)
    print(f"  Next wiki offset: {next_offset}", flush=True)

    if broken_articles or broken_leaders:
        print(f"\nBroken URLs cleared:", flush=True)
        for art in broken_articles:
            print(f"  article: {art['headline'][:70]}", flush=True)
        for leader in broken_leaders:
            print(f"  leader:  {leader['name']}", flush=True)

    if suspicious_articles:
        print(f"\nSuspicious (403 — check manually):", flush=True)
        for art in suspicious_articles:
            print(f"  article: {art['slug']}", flush=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
