#!/usr/bin/env python3
"""
Facebook auto-poster for TheVideshi Page.
Picks the top recent published article not yet posted to Facebook
and records it to avoid duplicates.

DELAYED-PUBLISH (default, what the slot crons run): STAGE mode —
pick + compose the exact post text and append it to the shared
social publish queue (pipeline/.state/social-publish-queue.json).
No Facebook calls are made; social-publish-flush.py publishes the
queue later while Kiran is present to approve each post.

Each staged pick also renders its social CARD SET (social_card.py
make_card_set: hook + key-takeaway cards + closer, 2-4 cards) into
the queue entry (card_files/card_texts/card_track; the <600px skip
rule leaves the set empty and the flush falls back to the plain
hero), and — when a set exists — stages a matching Instagram card
post carrying the single hook card, since IG stays single-card.

Usage: python3 -u fb-autopost.py [--dry-run]   stage (default)
       python3 -u fb-autopost.py --publish-now [--dry-run]
           legacy immediate publish (unchanged behavior)
"""
import json
import os
import subprocess
import sys
import urllib.parse

DRY_RUN = "--dry-run" in sys.argv
PUBLISH_NOW = "--publish-now" in sys.argv
STAGE = not PUBLISH_NOW

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_queue  # noqa: E402

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


# A pending slug means a publish timed out and the post MIGHT still land
# via a late approval. Observed late landing: 2026-10-11 Chennai Metro post
# was live within ~11 minutes, and publish() itself already polls ~6 min
# before a slug is ever marked pending. 3 hours is a generous window; past
# it the approval is dead, so the slug is abandoned (never re-attempted,
# so no duplicate risk) instead of bricking every later run forever.
PENDING_TTL_SECS = 3 * 3600


def load_posted():
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
            return (set(data.get("posted_slugs", [])),
                    set(data.get("pending_slugs", [])),
                    set(data.get("abandoned_slugs", [])),
                    dict(data.get("pending_since", {})))
    except (FileNotFoundError, json.JSONDecodeError):
        return set(), set(), set(), {}


def save_posted(slugs, pending, abandoned=None, pending_since=None):
    abandoned = abandoned or set()
    pending_since = {s: t for s, t in (pending_since or {}).items()
                     if s in pending}
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"posted_slugs": sorted(slugs),
                   "pending_slugs": sorted(pending),
                   "abandoned_slugs": sorted(abandoned),
                   "pending_since": pending_since}, f)


def pick_article(posted):
    # Top published articles from the last 12h, preferring key categories
    rows = sb_get(
        "p2_articles?select=headline,subheadline,slug,category,image_url,tags,key_takeaways,body"
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


CATEGORY_HASHTAGS = {
    "news": "#IndiaNews",
    "immigration": "#Immigration",
    "technology": "#TechNews",
    "entertainment": "#Bollywood",
    "sports": "#SportsNews",
    "markets-finance": "#Markets",
    "nri-world": "#IndianDiaspora",
    "food": "#IndianFood",
    "travel": "#Travel",
    "lifestyle-health": "#Lifestyle",
}


def _tagify(raw):
    import re
    words = re.sub(r"[^A-Za-z0-9 ]", " ", str(raw)).split()
    tag = "".join(w[:1].upper() + w[1:] for w in words)
    return f"#{tag}" if len(tag) >= 3 else None


def hashtag_line(article):
    """#TheVideshi + the category tag + up to 2 topic tags from the
    article's own tags. Max 4 tags total — discovery without spam
    (Kiran approved hashtags on article posts 2026-10-24)."""
    tags = ["#TheVideshi"]
    cat = CATEGORY_HASHTAGS.get(article.get("category") or "")
    if cat:
        tags.append(cat)
    for raw in (article.get("tags") or []):
        if len(tags) >= 4:
            break
        t = _tagify(raw)
        if t and t not in tags:
            tags.append(t)
    return " ".join(tags)


def build_post_text(article):
    headline = article["headline"].strip()
    sub = (article.get("subheadline") or "").strip()
    url = f"https://www.thevideshi.com/articles/{article['slug']}"
    # Keep it tight: headline + one-line summary + link + hashtags
    summary = sub.split(".")[0].strip() + "." if sub else ""
    tags = hashtag_line(article)
    budget = 1000 - len(tags) - 2  # reserve room so tags never get cut
    text = headline
    if summary and summary.lower() not in headline.lower():
        text += f"\n\n{summary}"
    text += f"\n\nRead the full story: {url}"
    if len(text) > budget:
        text = text[:budget]
    return text + f"\n\n{tags}"


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


def publish(text, article_url, image_url=None, image_path=None,
            image_paths=None):
    cmd = ["facebook-cli", "pages", "posts", "create",
           "--page-id", PAGE_ID, "--text", text, "--privacy", "PUBLIC"]
    # image_path / image_paths are caller-owned local files (e.g. a
    # rendered social card or card SET from the flush) — attach them
    # directly and never delete them. facebook-cli accepts --file
    # repeated (up to 80) in post order, so a set attaches as one
    # multi-image post. Otherwise fall back to downloading the
    # article hero, as before.
    own_img = None
    img_paths = []
    if image_paths:
        img_paths = [p for p in image_paths
                     if p and os.path.exists(p)]
    if not img_paths and image_path and os.path.exists(image_path):
        img_paths = [image_path]
    if not img_paths and image_url:
        img_paths = [download_image(image_url)]
        own_img = img_paths[0]
    for img_path in img_paths:
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
        if own_img and os.path.exists(own_img):
            os.unlink(own_img)


def _verify_recent_post(article_url):
    """Check the Page's recent posts for our article URL.

    Matches on the full article URL (unique per article) instead of
    headline fragments, which caused false positives.
    """
    import time
    cmd = ["facebook-cli", "pages", "posts", "list",
           "--page-id", PAGE_ID]
    # A fresh post may take a few seconds to appear in the list; poll.
    # Post-timeout publishes can land minutes later (approval lag), so keep
    # the window generous: 12 polls x 30s (~6 min).
    for attempt in range(12):
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
        if attempt < 11:
            time.sleep(30)
    print("ERROR: post not found in recent posts after timeout",
          file=sys.stderr)
    return None


def generate_card_set(article):
    """Render the article's social CARD SET via
    social_card.make_card_set (hook + key-takeaway cards + closer).

    Returns (card_files, card_track, card_texts): card_files is the
    ordered list of set PNGs (card_files[0] is the hook card),
    card_track the hook's track ("full-bleed" / "backdrop"),
    card_texts the per-card alt texts parallel to card_files. On
    the <600px skip rule returns ([], "skipped", []); on no image
    or a fetch/render failure ([], None, []). NEVER raises —
    staging degrades to the plain-hero post, exactly as before
    cards existed."""
    image_url = article.get("image_url")
    if not image_url:
        return [], None, []
    try:
        import social_card
        info = social_card.make_card_set(
            article["headline"], article.get("category"),
            image_url=image_url,
            key_takeaways=article.get("key_takeaways"),
            subheadline=article.get("subheadline"),
            slug=article.get("slug"),
            body=article.get("body"))
    except Exception as e:
        print(f"NOTE: card set generation failed for "
              f"{article['slug']}: {e}")
        return [], None, []
    if info.get("track") == "skipped":
        print(f"NOTE: card set skipped for {article['slug']} "
              f"({info.get('reason')}, source {info.get('source_px')})")
        return [], "skipped", []
    files = info.get("files") or []
    texts = [c.get("alt") or "" for c in info.get("cards") or []]
    print(f"Card set rendered: {info.get('track')}, "
          f"{len(files)} cards -> {files[0] if files else None}")
    return files, info.get("track"), texts


def build_ig_caption(article):
    """Instagram caption for the card post: headline + one-line
    summary + 'Full story at thevideshi.com' + the same hashtags as
    the FB post. No article URL — IG captions aren't clickable."""
    headline = article["headline"].strip()
    sub = (article.get("subheadline") or "").strip()
    summary = sub.split(".")[0].strip() + "." if sub else ""
    parts = [headline]
    if summary and summary.lower() not in headline.lower():
        parts.append(summary)
    parts.append("Full story at thevideshi.com")
    parts.append(hashtag_line(article))
    return "\n\n".join(parts)


def stage_main():
    """Delayed-publish staging: pick + compose + queue. No FB calls.

    fb-posted.json is NOT written at stage time (the flush writes it
    on publish); already-staged slugs are read back from the queue so
    later slots never re-pick the same article."""
    posted, pending, abandoned, _pending_since = load_posted()
    if pending:
        print(f"NOTE: {len(pending)} slug(s) pending verification from "
              f"earlier immediate publishes; excluded from staging "
              f"until a --publish-now run resolves them: "
              f"{sorted(pending)}")
    staged = social_queue.queued_slugs("facebook", "article_post")
    article = pick_article(posted | pending | abandoned | staged)
    if not article:
        print("No fresh article to stage (all recent ones already "
              "posted or staged).")
        return
    text = build_post_text(article)
    article_url = f"https://www.thevideshi.com/articles/{article['slug']}"
    print(f"Picked: {article['headline'][:80]}")
    print(f"Text preview: {text[:150]}...")
    if DRY_RUN:
        print("DRY RUN — not staging.")
        return
    card_files, card_track, card_texts = generate_card_set(article)
    card_file = card_files[0] if card_files else None
    entry = {
        "channel": "facebook",
        "kind": "article_post",
        "slug": article["slug"],
        "headline": article["headline"],
        "text": text,
        "link": article_url,
        "image_url": article.get("image_url"),
        "card_file": card_file,
        "card_files": card_files or None,
        "card_texts": card_texts or None,
        "card_track": card_track,
        "media_file": None,
        "cover_file": None,
        "alt_text": None,
        "source": "fb-autopost",
    }
    if social_queue.add_entry(entry):
        print(f"Staged for Facebook: {article['slug']}")
    else:
        print(f"Already staged, skipped: {article['slug']}")
    # Instagram stays a SINGLE-card channel: stage a card post for
    # the same pick carrying the set's hook card (same file, IG
    # caption). A skipped set (<600px hero) means NO IG entry —
    # the pick simply doesn't go to IG.
    if card_file:
        ig_entry = {
            "channel": "instagram",
            "kind": "article_post",
            "slug": article["slug"],
            "headline": article["headline"],
            "text": build_ig_caption(article),
            "link": None,
            "image_url": article.get("image_url"),
            "card_file": card_file,
            "card_track": card_track,
            "media_file": None,
            "cover_file": None,
            "alt_text": article["headline"],
            "source": "fb-autopost",
        }
        if social_queue.add_entry(ig_entry):
            print(f"Staged for Instagram (card): {article['slug']}")
        else:
            print(f"IG entry already staged, skipped: {article['slug']}")


def main():
    import time
    if STAGE:
        stage_main()
        return
    posted, pending, abandoned, pending_since = load_posted()
    # Re-check anything left pending from a previous timed-out run: if it's
    # live now, record it. If it is still not live past PENDING_TTL_SECS,
    # the approval is dead — abandon the slug (it is never re-attempted,
    # so there is no duplicate risk) and let the queue move on instead of
    # bailing out forever. Inside the window, bail out as before.
    for slug in sorted(pending):
        url = f"https://www.thevideshi.com/articles/{slug}"
        if _verify_recent_post(url):
            pending.discard(slug)
            pending_since.pop(slug, None)
            posted.add(slug)
            print(f"Pending post confirmed live: {slug}")
            continue
        since = pending_since.get(slug)
        if since is not None and time.time() - since > PENDING_TTL_SECS:
            pending.discard(slug)
            pending_since.pop(slug, None)
            abandoned.add(slug)
            save_posted(posted, pending, abandoned, pending_since)
            print(f"Pending post expired unverified after "
                  f"{PENDING_TTL_SECS // 3600}h; slug abandoned "
                  f"(never re-attempted): {slug}")
            continue
        if since is None:
            # Legacy pending entry with no timestamp: start its clock now.
            pending_since[slug] = time.time()
        print(f"ERROR: pending post still unverifiable: {slug}; "
              f"not posting a duplicate.", file=sys.stderr)
        save_posted(posted, pending, abandoned, pending_since)
        sys.exit(1)
    staged = social_queue.queued_slugs("facebook", "article_post")
    article = pick_article(posted | pending | abandoned | staged)
    if not article:
        print("No fresh article to post (all recent ones already posted).")
        return
    text = build_post_text(article)
    article_url = f"https://www.thevideshi.com/articles/{article['slug']}"
    print(f"Picked: {article['headline'][:80]}")
    print(f"Text preview: {text[:150]}...")
    if DRY_RUN:
        print("DRY RUN — not publishing.")
        return
    result = publish(text, article_url, article.get("image_url"))
    if result:
        posted.add(article["slug"])
        save_posted(posted, pending, abandoned, pending_since)
        print(f"Published: {result.get('post_url')}")
    else:
        # Could be a late-approval post that went live after the CLI timed
        # out — mark pending (with a timestamp) so the next run re-verifies
        # instead of double-posting. After PENDING_TTL_SECS unverified it
        # is abandoned, not retried forever.
        pending.add(article["slug"])
        pending_since[article["slug"]] = time.time()
        save_posted(posted, pending, abandoned, pending_since)
        print("Publish failed; slug marked pending for re-verification.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
