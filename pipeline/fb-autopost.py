#!/usr/bin/env python3
"""
Facebook auto-poster for TheVideshi Page.
Picks the top recent published article not yet posted to Facebook,
publishes it to the Page, and records it to avoid duplicates.

Usage: python3 -u fb-autopost.py [--dry-run]
"""
import json
import os
import subprocess
import sys
import urllib.parse

DRY_RUN = "--dry-run" in sys.argv

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PAGE_ID = "1243823795489375"

STATE_FILE = os.path.expanduser(
    "~/workspace/the-videshi-news/pipeline/.state/fb-posted.json")


def sb_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-s", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


def load_posted():
    try:
        with open(STATE_FILE) as f:
            return set(json.load(f).get("posted_slugs", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_posted(slugs):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"posted_slugs": sorted(slugs)}, f)


def pick_article(posted):
    # Top published articles from the last 12h, preferring key categories
    rows = sb_get(
        "p2_articles?select=headline,subheadline,slug,category,image_url"
        "&status=eq.published"
        "&published_at=gte." + _hours_ago(12) +
        "&order=published_at.desc&limit=30")
    if not isinstance(rows, list):
        return None
    # Prefer diaspora-relevant categories, skip already-posted
    preferred = {"immigration", "news", "nri-world", "entertainment",
                 "markets-finance", "technology"}
    candidates = [r for r in rows if r.get("slug") not in posted]
    if not candidates:
        return None
    for r in candidates:
        if r.get("category") in preferred:
            return r
    return candidates[0]


def _hours_ago(h):
    from datetime import datetime, timezone, timedelta
    return (datetime.now(timezone.utc) - timedelta(hours=h)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def build_post_text(article):
    headline = article["headline"].strip()
    sub = (article.get("subheadline") or "").strip()
    url = f"https://www.thevideshi.com/news/{article['slug']}"
    # Keep it tight: headline + one-line summary + link
    summary = sub.split(".")[0].strip() + "." if sub else ""
    text = headline
    if summary and summary.lower() not in headline.lower():
        text += f"\n\n{summary}"
    text += f"\n\nRead the full story: {url}"
    return text[:1000]


def download_image(url):
    """Download article hero image to /tmp for FB attachment."""
    if not url:
        return None
    import tempfile
    ext = ".jpg"
    if ".png" in url.lower():
        ext = ".png"
    path = os.path.join(tempfile.gettempdir(),
                        f"fb-post-{os.getpid()}{ext}")
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "30",
             "-A", "TheVideshi/1.0", "-o", path, url],
            capture_output=True, timeout=35)
        if r.returncode == 0 and os.path.getsize(path) > 1024:
            return path
    except Exception as e:
        print(f"WARN: image download failed: {e}", file=sys.stderr)
    return None


def publish(text, article_url, image_url=None):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", PAGE_ID, "--text", text, "--privacy", "PUBLIC"]
    img_path = download_image(image_url) if image_url else None
    if img_path:
        cmd.extend(["--file", img_path])
        print(f"Attaching image: {img_path}", file=sys.stderr)
    # Retry on connector write lock ("already running") with backoff.
    # The lock is transient — a previous write hanging server-side blocks
    # the next one until it clears.
    import time
    try:
        for attempt in range(3):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=180)  # longer for image upload
            except subprocess.TimeoutExpired:
                # The CLI can hang after the post actually goes live.
                # Don't treat timeout as failure — verify via posts list.
                print("WARN: publish timed out; verifying via posts list...",
                      file=sys.stderr)
                return _verify_recent_post(article_url)
            output = r.stdout + r.stderr
            if "already running" in output.lower():
                wait = 60 * (attempt + 1)  # 60s, 120s
                print(f"WARN: connector write lock held, "
                      f"retrying in {wait}s (attempt {attempt + 1}/3)...",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            try:
                data = json.loads(r.stdout)
            except json.JSONDecodeError:
                print(f"ERROR: facebook-cli output not JSON: {r.stdout[:300]}",
                      file=sys.stderr)
                return _verify_recent_post(article_url)
            if data.get("state") == "published":
                return data
            print(f"ERROR: publish failed: {r.stdout[:500]}", file=sys.stderr)
            return None
        print("ERROR: connector write lock never cleared after 3 attempts",
              file=sys.stderr)
        return None
    finally:
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)


def _verify_recent_post(article_url):
    """Check the Page's recent posts for our article URL.

    Matches on the full article URL (unique per article) instead of
    headline fragments, which caused false positives.
    """
    import time
    cmd = ["facebook-cli", "pages", "posts", "list",
           "--page-id", PAGE_ID]
    # A fresh post may take a few seconds to appear in the list; poll.
    for attempt in range(4):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(r.stdout)
        except Exception as e:
            print(f"ERROR: verify failed (attempt {attempt + 1}): {e}",
                  file=sys.stderr)
            break
        for post in data.get("results", []):
            meta = post.get("metadata") or {}
            post_text = (post.get("text") or meta.get("caption_excerpt")
                         or "")
            if article_url in post_text:
                post_id = post.get("post_id") or post.get("object_id")
                print(f"Verified live post: {post.get('post_url') or post_id}")
                return {"state": "published",
                        "post_url": post.get("post_url"),
                        "post_id": post_id}
        if attempt < 3:
            time.sleep(10)
    print("ERROR: post not found in recent posts after timeout",
          file=sys.stderr)
    return None


def main():
    posted = load_posted()
    article = pick_article(posted)
    if not article:
        print("No fresh article to post (all recent ones already posted).")
        return
    text = build_post_text(article)
    article_url = f"https://www.thevideshi.com/news/{article['slug']}"
    print(f"Picked: {article['headline'][:80]}")
    print(f"Text preview: {text[:150]}...")
    if DRY_RUN:
        print("DRY RUN — not publishing.")
        return
    result = publish(text, article_url, article.get("image_url"))
    if result:
        posted.add(article["slug"])
        save_posted(posted)
        print(f"Published: {result.get('post_url')}")
    else:
        print("Publish failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
