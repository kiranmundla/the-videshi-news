#!/usr/bin/env python3
"""
Sweep published Videshi articles for dead Instagram and YouTube embeds.
Verifies each embed URL, reports dead ones, and optionally strips them.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS_CLI = [
    "-H", f"apikey: {SUPABASE_KEY}",
    "-H", f"Authorization: Bearer {SUPABASE_KEY}",
]

DRY_RUN = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv

# ── Supabase helpers ──────────────────────────────────────────────────

def supabase_get(path):
    """GET from Supabase REST API, returns parsed JSON."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-s", url] + HEADERS_CLI
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)

def supabase_patch(table, row_id, data):
    """PATCH a row in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    payload = json.dumps(data)
    cmd = [
        "curl", "-s", "-X", "PATCH", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", payload,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and result.stdout.strip() == ""

# ── URL extraction ────────────────────────────────────────────────────

# Instagram patterns: /p/CODE/ or /reel/CODE/ or /tv/CODE/
IG_URL_RE = re.compile(
    r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?',
    re.IGNORECASE
)

# YouTube patterns: watch?v=, /embed/, youtu.be/, /shorts/
YT_URL_RE = re.compile(
    r'https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})',
    re.IGNORECASE
)

# Full URL extraction (for stripping)
IG_FULL_URL_RE = re.compile(
    r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/[A-Za-z0-9_-]+/?(?:\?[^\s"<\]]*)?',
    re.IGNORECASE
)
YT_FULL_URL_RE = re.compile(
    r'https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|shorts/)[A-Za-z0-9_-]{11}[^\s"<\]]*|youtu\.be/[A-Za-z0-9_-]{11}[^\s"<\]]*)',
    re.IGNORECASE
)

def extract_ig_urls(body):
    """Return list of unique IG embed URLs from article body."""
    urls = []
    seen = set()
    for m in IG_FULL_URL_RE.finditer(body):
        url = m.group(0).rstrip(')')
        # Normalize: strip query params for dedup
        code_match = IG_URL_RE.match(url)
        if code_match:
            code = code_match.group(1)
            if code not in seen:
                seen.add(code)
                canonical = f"https://www.instagram.com/{url.split('instagram.com/')[1].split('?')[0]}"
                if not canonical.endswith('/'):
                    canonical += '/'
                urls.append((canonical, url))  # (check_url, original_url)
    return urls

def extract_yt_urls(body):
    """Return list of unique YT embed URLs from article body."""
    urls = []
    seen = set()
    for m in YT_URL_RE.finditer(body):
        vid = m.group(1)
        if vid not in seen:
            seen.add(vid)
            # Find the full URL in the body for stripping
            full_match = YT_FULL_URL_RE.search(body[m.start():])
            full_url = full_match.group(0) if full_match else m.group(0)
            canonical = f"https://www.youtube.com/watch?v={vid}"
            urls.append((canonical, full_url.rstrip(')')))
    return urls

# ── Verification ──────────────────────────────────────────────────────

def check_yt_oembed(url):
    """Check YouTube embed via oEmbed. Returns True if alive."""
    oembed_url = f"https://www.youtube.com/oembed?url={urllib.parse.quote(url, safe='')}&format=json"
    cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", oembed_url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        code = int(result.stdout.strip())
        return code == 200
    except Exception:
        return True  # assume alive on error (don't strip unknowns)

def check_ig_oembed(url):
    """
    Check Instagram embed via oEmbed, then fallback to direct GET.
    Returns True if alive, False if definitely dead.
    """
    # Try oEmbed first
    oembed_url = f"https://api.instagram.com/oembed?url={urllib.parse.quote(url, safe='')}"
    cmd = ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-L", oembed_url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        code = int(result.stdout.strip())
        if code == 200:
            return True
        if code == 404:
            return False
        # 400/401 may mean API issue, try direct GET
    except Exception:
        pass

    # Fallback: direct GET the URL, check for 404 or redirect-to-login
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-L", "--max-redirs", "3",
        "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        url
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        code = int(result.stdout.strip())
        if code == 404:
            return False
        # For 200, check if it's a login redirect page
        if code == 200:
            # Fetch actual content to check for login wall
            cmd2 = [
                "curl", "-s", "-L", "--max-redirs", "3",
                "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                url
            ]
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=15)
            body = result2.stdout[:5000]
            # Dead IG content shows login page with "Page Not Found" or "Sorry, this page"
            if "Page Not Found" in body or "Sorry, this page isn" in body:
                return False
            # Content-not-available patterns
            if '"HttpErrorPage"' in body:
                return False
        return True
    except Exception:
        return True  # assume alive on error

# ── Body stripping ────────────────────────────────────────────────────

def strip_embed_from_body(body, dead_url):
    """
    Remove an embed URL and its surrounding markup from the article body.
    Handles: bare URLs, markdown links, blockquote embeds, iframe embeds.
    """
    escaped_url = re.escape(dead_url)
    original_body = body

    # Pattern 1: Full blockquote Instagram embed block
    # <blockquote class="instagram-media" ...>...</blockquote><script ...></script>
    if 'instagram.com' in dead_url:
        code_match = IG_URL_RE.search(dead_url)
        if code_match:
            code = code_match.group(1)
            # Remove entire blockquote+script for this embed
            bq_pattern = re.compile(
                r'<blockquote[^>]*instagram-media[^>]*>.*?' + re.escape(code) + r'.*?</blockquote>\s*(?:<script[^>]*instgrm[^>]*></script>\s*)?',
                re.DOTALL | re.IGNORECASE
            )
            body = bq_pattern.sub('', body)

    # Pattern 2: iframe embeds
    iframe_pattern = re.compile(
        r'<iframe[^>]*' + escaped_url.replace(r'https\:', r'https?\:') + r'[^>]*>\s*</iframe>\s*',
        re.IGNORECASE
    )
    body = iframe_pattern.sub('', body)

    # Pattern 3: Markdown-style link with the URL
    # [text](url) or [![text](img)](url)
    md_pattern = re.compile(
        r'\[(?:[^\]]*)\]\(' + escaped_url + r'[^)]*\)\s*',
        re.IGNORECASE
    )
    body = md_pattern.sub('', body)

    # Pattern 4: Bare URL on its own line or in text
    bare_pattern = re.compile(
        r'(?:^|\n)\s*' + escaped_url + r'\s*(?:\n|$)',
        re.IGNORECASE
    )
    body = bare_pattern.sub('\n', body)

    # Pattern 5: Any remaining occurrence of the URL
    body = body.replace(dead_url, '')

    # Also try with/without trailing slash
    alt_url = dead_url.rstrip('/') if dead_url.endswith('/') else dead_url + '/'
    body = body.replace(alt_url, '')

    # Clean up double newlines left behind
    body = re.sub(r'\n{3,}', '\n\n', body)

    return body.strip()

# ── Main ──────────────────────────────────────────────────────────────

def fetch_articles(embed_type):
    """Fetch published articles containing a specific embed type."""
    if embed_type == "instagram":
        filter_param = "body=like.*instagram.com*"
    elif embed_type == "youtube":
        filter_param = "body=like.*youtube.com*"
    elif embed_type == "youtu.be":
        filter_param = "body=like.*youtu.be*"
    else:
        return []
    
    path = f"p2_articles?select=id,slug,headline,body&status=eq.published&{filter_param}&order=created_at.desc"
    return supabase_get(path)

def main():
    print("=" * 70)
    print("VIDESHI DEAD EMBED SWEEP")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE (will patch articles)'}")
    print("=" * 70)

    dead_embeds = []  # (article_id, slug, headline, url, platform)
    alive_count = {"ig": 0, "yt": 0}
    articles_checked = set()
    articles_to_patch = {}  # id -> (slug, headline, new_body, dead_urls)

    # ── Instagram sweep ──
    print("\n📸 Fetching articles with Instagram embeds...")
    ig_articles = fetch_articles("instagram")
    print(f"   Found {len(ig_articles)} articles")

    for art in ig_articles:
        aid, slug, headline = art["id"], art["slug"], art.get("headline", "?")
        body = art.get("body", "")
        articles_checked.add(aid)

        ig_urls = extract_ig_urls(body)
        if not ig_urls:
            continue

        for check_url, orig_url in ig_urls:
            if VERBOSE:
                print(f"   Checking IG: {check_url} (in {slug})")
            alive = check_ig_oembed(check_url)
            time.sleep(0.3)  # rate limit
            if alive:
                alive_count["ig"] += 1
                if VERBOSE:
                    print(f"     ✅ alive")
            else:
                print(f"   ❌ DEAD IG: {check_url} in [{slug}]")
                dead_embeds.append((aid, slug, headline, orig_url, "instagram"))
                if aid not in articles_to_patch:
                    articles_to_patch[aid] = (slug, headline, body, [])
                articles_to_patch[aid][3].append(orig_url)

    # ── YouTube sweep ──
    print("\n▶️  Fetching articles with YouTube embeds...")
    yt_articles = fetch_articles("youtube")
    ytbe_articles = fetch_articles("youtu.be")

    # Merge, dedup by article id
    yt_map = {a["id"]: a for a in yt_articles}
    for a in ytbe_articles:
        if a["id"] not in yt_map:
            yt_map[a["id"]] = a
    all_yt = list(yt_map.values())
    print(f"   Found {len(all_yt)} articles")

    for art in all_yt:
        aid, slug, headline = art["id"], art["slug"], art.get("headline", "?")
        body = art.get("body", "")
        articles_checked.add(aid)

        yt_urls = extract_yt_urls(body)
        if not yt_urls:
            continue

        for check_url, orig_url in yt_urls:
            if VERBOSE:
                print(f"   Checking YT: {check_url} (in {slug})")
            alive = check_yt_oembed(check_url)
            time.sleep(0.2)  # rate limit
            if alive:
                alive_count["yt"] += 1
                if VERBOSE:
                    print(f"     ✅ alive")
            else:
                print(f"   ❌ DEAD YT: {check_url} in [{slug}]")
                dead_embeds.append((aid, slug, headline, orig_url, "youtube"))
                if aid not in articles_to_patch:
                    articles_to_patch[aid] = (slug, headline, body, [])
                articles_to_patch[aid][3].append(orig_url)

    # ── Report ──
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Articles checked: {len(articles_checked)}")
    print(f"Alive IG embeds: {alive_count['ig']}")
    print(f"Alive YT embeds: {alive_count['yt']}")
    print(f"Dead embeds found: {len(dead_embeds)}")

    if dead_embeds:
        print("\n🪦 Dead embeds:")
        for aid, slug, headline, url, platform in dead_embeds:
            print(f"  [{platform.upper():>9}] {slug}")
            print(f"             {url}")
            print(f"             \"{headline}\"")
    else:
        print("\n✅ No dead embeds found! All clear.")

    # ── Patch ──
    if articles_to_patch and not DRY_RUN:
        print(f"\n🔧 Patching {len(articles_to_patch)} articles...")
        patched = 0
        for aid, (slug, headline, body, dead_urls) in articles_to_patch.items():
            new_body = body
            for durl in dead_urls:
                new_body = strip_embed_from_body(new_body, durl)

            if new_body == body:
                print(f"  ⚠️  {slug}: body unchanged after strip (embed may be in unusual format)")
                continue

            ok = supabase_patch("p2_articles", aid, {"body": new_body})
            if ok:
                print(f"  ✅ {slug}: stripped {len(dead_urls)} dead embed(s)")
                patched += 1
            else:
                print(f"  ❌ {slug}: PATCH failed!")

        print(f"\nPatched {patched}/{len(articles_to_patch)} articles")
    elif articles_to_patch and DRY_RUN:
        print(f"\n⏸️  DRY RUN: would patch {len(articles_to_patch)} articles")

    # ── Summary JSON ──
    summary = {
        "articles_checked": len(articles_checked),
        "alive_ig": alive_count["ig"],
        "alive_yt": alive_count["yt"],
        "dead_embeds": [
            {"article_id": aid, "slug": slug, "url": url, "platform": p}
            for aid, slug, _, url, p in dead_embeds
        ],
        "articles_patched": len(articles_to_patch) if not DRY_RUN else 0,
    }
    print(f"\n__SUMMARY__ {json.dumps(summary)}")

if __name__ == "__main__":
    main()
