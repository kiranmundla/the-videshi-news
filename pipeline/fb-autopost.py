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
        "p2_articles?select=headline,subheadline,slug,category"
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


def publish(text):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", PAGE_ID, "--text", text, "--privacy", "PUBLIC"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        # The CLI can hang after the post actually goes live server-side.
        # Don't treat timeout as failure — verify via the posts list instead.
        print("WARN: publish timed out; verifying via posts list...",
              file=sys.stderr)
        return _verify_recent_post(text)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: facebook-cli output not JSON: {r.stdout[:300]}",
              file=sys.stderr)
        return _verify_recent_post(text)
    if data.get("state") == "published":
        return data
    print(f"ERROR: publish failed: {r.stdout[:500]}", file=sys.stderr)
    return None


def _verify_recent_post(text):
    """Check the Page's recent posts for our text (handles timeout race)."""
    first_line = text.split("\n")[0].strip()[:60]
    cmd = ["facebook-cli", "pages", "posts", "list",
           "--page-id", PAGE_ID]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(r.stdout)
    except Exception as e:
        print(f"ERROR: verify failed: {e}", file=sys.stderr)
        return None
    for post in data.get("results", []):
        if first_line and first_line in (post.get("text") or ""):
            print(f"Verified live post: {post.get('post_url')}")
            return {"state": "published",
                    "post_url": post.get("post_url"),
                    "post_id": post.get("post_id")}
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
    print(f"Picked: {article['headline'][:80]}")
    print(f"Text preview: {text[:150]}...")
    if DRY_RUN:
        print("DRY RUN — not publishing.")
        return
    result = publish(text)
    if result:
        posted.add(article["slug"])
        save_posted(posted)
        print(f"Published: {result.get('post_url')}")
    else:
        print("Publish failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
