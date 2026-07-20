#!/usr/bin/env python3
"""
verify-embeds.py — Liveness checker for social embeds and inline media.

Checks that embedded X tweets, IG posts, YouTube videos, and hero images
are still live. Strips anything dead — bad content is worse than no content.

Usage:
    python3 -u verify-embeds.py --hours 48           # dry run, last 48h
    python3 -u verify-embeds.py --hours 48 --apply    # strip dead embeds
    python3 -u verify-embeds.py --hours 168 --apply   # weekly sweep
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

# ─── Env ───────────────────────────────────────────────────────────────────────
def load_env(path):
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except FileNotFoundError:
        pass

load_env("~/workspace/.env.supabase")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
VERIFY_TWEET_SCRIPT = os.path.join(PIPELINE_DIR, "verify-tweet.sh")

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# ─── Helpers ───────────────────────────────────────────────────────────────────

def sb_get(endpoint, params=None):
    """GET from Supabase REST API via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{qs}"
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "15", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=20,
    )
    return json.loads(result.stdout)


def sb_patch(article_id, updates):
    """PATCH an article in Supabase via curl."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    result = subprocess.run(
        ["curl", "-sS", "--max-time", "10", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", json.dumps(updates)],
        capture_output=True, text=True, timeout=15,
    )
    return result.returncode == 0 and "error" not in result.stdout.lower()


def check_url(url, timeout=8):
    """Check if a URL is live. Returns HTTP status code as string."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
             "--max-time", str(timeout),
             "-A", "Mozilla/5.0 (compatible; TheVideshi/1.0)",
             "-L",  # follow redirects
             url],
            capture_output=True, text=True, timeout=timeout + 5,
        )
        return result.stdout.strip()
    except Exception:
        return "000"


def check_tweet(tweet_id):
    """Check if a tweet exists using verify-tweet.sh. Returns True if valid."""
    try:
        result = subprocess.run(
            ["bash", VERIFY_TWEET_SCRIPT, str(tweet_id)],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0 and "VALID" in result.stdout
    except Exception:
        return False


def check_youtube(video_id):
    """Check if a YouTube video is available via oEmbed API."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    code = check_url(url, timeout=8)
    return code == "200"


def extract_tweet_ids_from_body(body):
    """Extract tweet IDs from x.com/twitter.com URLs in body."""
    return re.findall(r'https?://(?:x|twitter)\.com/\w+/status/(\d+)', body)


def extract_ig_shortcodes_from_body(body):
    """Extract Instagram shortcodes from body embed URLs."""
    return re.findall(r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)', body)


def extract_youtube_ids_from_body(body):
    """Extract YouTube video IDs from body."""
    ids = set()
    # <youtube>ID</youtube> tags
    ids.update(re.findall(r'<youtube>([A-Za-z0-9_-]{11})</youtube>', body))
    # iframe src or href
    ids.update(re.findall(r'youtube\.com/embed/([A-Za-z0-9_-]{11})', body))
    # watch?v= links
    ids.update(re.findall(r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', body))
    # youtu.be short links
    ids.update(re.findall(r'youtu\.be/([A-Za-z0-9_-]{11})', body))
    return list(ids)


def strip_tweet_from_body(body, tweet_id):
    """Remove a tweet embed URL/block from body."""
    # Remove full paragraph or bare link containing the tweet
    pattern = rf'<p>\s*<a[^>]*href="https?://(?:x|twitter)\.com/\w+/status/{tweet_id}[^"]*"[^>]*>[^<]*</a>\s*</p>'
    body = re.sub(pattern, '', body, flags=re.IGNORECASE)
    # Remove bare URL line
    body = re.sub(rf'\n?\s*https?://(?:x|twitter)\.com/\w+/status/{tweet_id}\S*\s*\n?', '\n', body)
    return body.strip()


def strip_ig_from_body(body, shortcode):
    """Remove an Instagram embed from body."""
    # Remove iframe/blockquote embeds
    pattern = rf'<[^>]*instagram\.com/(?:p|reel)/{re.escape(shortcode)}[^>]*>.*?</[^>]+>'
    body = re.sub(pattern, '', body, flags=re.IGNORECASE | re.DOTALL)
    # Remove bare URL
    body = re.sub(rf'\n?\s*https?://(?:www\.)?instagram\.com/(?:p|reel)/{re.escape(shortcode)}\S*\s*\n?', '\n', body)
    return body.strip()


def strip_youtube_from_body(body, video_id):
    """Remove a YouTube embed from body."""
    vid = re.escape(video_id)
    # <youtube>ID</youtube>
    body = re.sub(rf'<youtube>{vid}</youtube>', '', body)
    # iframe
    body = re.sub(rf'<iframe[^>]*youtube\.com/embed/{vid}[^>]*>\s*</iframe>', '', body, flags=re.IGNORECASE)
    # Bare link in paragraph
    body = re.sub(rf'<p>\s*<a[^>]*youtube\.com/watch\?v={vid}[^"]*"[^>]*>[^<]*</a>\s*</p>', '', body, flags=re.IGNORECASE)
    return body.strip()


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Verify liveness of social embeds.")
    parser.add_argument("--hours", type=int, default=48, help="Check articles from last N hours")
    parser.add_argument("--apply", action="store_true", help="Strip dead embeds (default: dry run)")
    parser.add_argument("--limit", type=int, default=200, help="Max articles to check")
    args = parser.parse_args()

    since = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"══ Embed Liveness Check ({mode}) ══")
    print(f"   Window: last {args.hours}h (since {since})")

    # Fetch recent published articles
    articles = sb_get("p2_articles", {
        "select": "id,headline,slug,category,body,social_embeds,image_url",
        "status": "eq.published",
        "published_at": f"gte.{since}",
        "order": "published_at.desc",
        "limit": str(args.limit),
    })

    if not isinstance(articles, list):
        print(f"  ❌ DB fetch failed: {str(articles)[:200]}")
        return

    print(f"   Articles to check: {len(articles)}")

    report = {
        "articles_checked": len(articles),
        "social_embeds_checked": 0,
        "social_embeds_removed": 0,
        "body_embeds_checked": 0,
        "body_embeds_removed": 0,
        "hero_images_checked": 0,
        "hero_images_dead": 0,
        "details": [],
    }

    for article in articles:
        aid = article["id"]
        headline = article.get("headline", "")[:70]
        body = article.get("body", "") or ""
        raw_embeds = article.get("social_embeds") or []
        # social_embeds may come back as a JSON string from Supabase
        if isinstance(raw_embeds, str):
            try:
                raw_embeds = json.loads(raw_embeds)
            except (json.JSONDecodeError, TypeError):
                raw_embeds = []
        social_embeds = raw_embeds if isinstance(raw_embeds, list) else []
        image_url = article.get("image_url", "") or ""
        updates = {}
        body_changed = False

        # ── 1. Check social_embeds field ──
        if social_embeds:
            live_embeds = []
            for embed in social_embeds:
                platform = embed.get("platform", "")
                url = embed.get("url", "")
                report["social_embeds_checked"] += 1

                if platform == "youtube":
                    vid_match = re.search(r'[?&]v=([A-Za-z0-9_-]{11})', url)
                    if vid_match:
                        vid = vid_match.group(1)
                        if check_youtube(vid):
                            live_embeds.append(embed)
                        else:
                            report["social_embeds_removed"] += 1
                            report["details"].append({
                                "article": headline,
                                "type": "social_embed",
                                "platform": "youtube",
                                "url": url,
                                "action": "removed" if args.apply else "would_remove",
                            })
                            print(f"  ❌ Dead YouTube embed: {headline}")
                            print(f"      {url}")
                    else:
                        live_embeds.append(embed)  # keep if can't parse ID

                elif platform == "x" or "x.com" in url or "twitter.com" in url:
                    tid_match = re.search(r'/status/(\d+)', url)
                    if tid_match:
                        tid = tid_match.group(1)
                        if check_tweet(tid):
                            live_embeds.append(embed)
                        else:
                            report["social_embeds_removed"] += 1
                            report["details"].append({
                                "article": headline,
                                "type": "social_embed",
                                "platform": "x",
                                "url": url,
                                "action": "removed" if args.apply else "would_remove",
                            })
                            print(f"  ❌ Dead tweet embed: {headline}")
                            print(f"      {url}")
                    else:
                        live_embeds.append(embed)

                elif platform == "instagram" or "instagram.com" in url:
                    code = check_url(url, timeout=8)
                    if code in ("200", "301", "302"):
                        live_embeds.append(embed)
                    else:
                        report["social_embeds_removed"] += 1
                        report["details"].append({
                            "article": headline,
                            "type": "social_embed",
                            "platform": "instagram",
                            "url": url,
                            "status": code,
                            "action": "removed" if args.apply else "would_remove",
                        })
                        print(f"  ❌ Dead IG embed [{code}]: {headline}")
                        print(f"      {url}")

                else:
                    # Unknown platform — check URL directly
                    code = check_url(url, timeout=8)
                    if code in ("200", "301", "302"):
                        live_embeds.append(embed)
                    else:
                        report["social_embeds_removed"] += 1
                        print(f"  ❌ Dead embed [{code}]: {headline}")
                        print(f"      {url}")

            if len(live_embeds) != len(social_embeds):
                updates["social_embeds"] = live_embeds

        # ── 2. Check inline body embeds ──
        # X tweets in body
        body_tweet_ids = extract_tweet_ids_from_body(body)
        for tid in body_tweet_ids:
            report["body_embeds_checked"] += 1
            if not check_tweet(tid):
                report["body_embeds_removed"] += 1
                report["details"].append({
                    "article": headline,
                    "type": "body_tweet",
                    "tweet_id": tid,
                    "action": "stripped" if args.apply else "would_strip",
                })
                print(f"  ❌ Dead body tweet: {headline}")
                print(f"      tweet_id={tid}")
                body = strip_tweet_from_body(body, tid)
                body_changed = True

        # YouTube in body
        body_yt_ids = extract_youtube_ids_from_body(body)
        for vid in body_yt_ids:
            report["body_embeds_checked"] += 1
            if not check_youtube(vid):
                report["body_embeds_removed"] += 1
                report["details"].append({
                    "article": headline,
                    "type": "body_youtube",
                    "video_id": vid,
                    "action": "stripped" if args.apply else "would_strip",
                })
                print(f"  ❌ Dead body YouTube: {headline}")
                print(f"      video_id={vid}")
                body = strip_youtube_from_body(body, vid)
                body_changed = True

        # IG in body (less common but check)
        body_ig_codes = extract_ig_shortcodes_from_body(body)
        for sc in body_ig_codes:
            report["body_embeds_checked"] += 1
            code = check_url(f"https://www.instagram.com/p/{sc}/embed/", timeout=8)
            if code not in ("200", "301", "302"):
                report["body_embeds_removed"] += 1
                report["details"].append({
                    "article": headline,
                    "type": "body_instagram",
                    "shortcode": sc,
                    "status": code,
                    "action": "stripped" if args.apply else "would_strip",
                })
                print(f"  ❌ Dead body IG [{code}]: {headline}")
                print(f"      shortcode={sc}")
                body = strip_ig_from_body(body, sc)
                body_changed = True

        if body_changed:
            updates["body"] = body

        # ── 3. Check hero image ──
        if image_url and image_url.startswith("http"):
            report["hero_images_checked"] += 1
            code = check_url(image_url, timeout=8)
            if code not in ("200", "301", "302"):
                report["hero_images_dead"] += 1
                report["details"].append({
                    "article": headline,
                    "type": "hero_image",
                    "url": image_url[:80],
                    "status": code,
                    "action": "nulled" if args.apply else "would_null",
                })
                print(f"  ❌ Dead hero image [{code}]: {headline}")
                print(f"      {image_url[:80]}")
                updates["image_url"] = None
                updates["image_caption"] = None

        # ── Apply updates ──
        if updates and args.apply:
            if sb_patch(aid, updates):
                actions = []
                if "social_embeds" in updates:
                    actions.append(f"social_embeds: {len(social_embeds)}→{len(updates['social_embeds'])}")
                if "body" in updates:
                    actions.append("body: stripped dead embeds")
                if "image_url" in updates:
                    actions.append("hero: nulled")
                print(f"      ✅ Patched: {', '.join(actions)}")
            else:
                print(f"      ❌ Patch failed for {aid}")

    # ── Summary ──
    print(f"\n══ Summary ══")
    print(f"   Articles checked:       {report['articles_checked']}")
    print(f"   Social embeds checked:  {report['social_embeds_checked']}")
    print(f"   Social embeds removed:  {report['social_embeds_removed']}")
    print(f"   Body embeds checked:    {report['body_embeds_checked']}")
    print(f"   Body embeds removed:    {report['body_embeds_removed']}")
    print(f"   Hero images checked:    {report['hero_images_checked']}")
    print(f"   Hero images dead:       {report['hero_images_dead']}")

    total_issues = report["social_embeds_removed"] + report["body_embeds_removed"] + report["hero_images_dead"]
    if total_issues == 0:
        print(f"\n   ✅ All embeds healthy!")
    else:
        print(f"\n   ⚠ {total_issues} dead embeds {'stripped' if args.apply else 'found (dry run)'}")

    # Return report for cron use
    return report


if __name__ == "__main__":
    main()
