#!/usr/bin/env python3
"""
Threads auto-poster for The Videshi (@the.videshi).

Mirrors the Facebook autopost picks: every article the FB job posts to
the Page is also posted to Threads, in the same order discipline, with
its own ledger so nothing ever double-posts. Text is reformatted for
Threads' 500-character limit (headline + subheadline + link).

Usage: python3 -u threads-autopost.py [--dry-run]

State: pipeline/.state/threads-posted.json
  posted_slugs  — mirrored (or seeded as historical, never posted)
  pending_slugs — publish outcome unknown; re-verified next run,
                  abandoned after PENDING_TTL_SECS (never re-attempted)

First run seeds the ledger with every FB pick whose article is older
than SEED_AGE_HOURS, so Threads starts from today's picks instead of
dumping the whole FB back-catalogue.
"""
import json
import os
import subprocess
import sys
import time

DRY_RUN = "--dry-run" in sys.argv

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
ACCOUNT_ID = "17841436385342619"  # Threads @the.videshi
THREADS_CLI = "/opt/hatch/bin/threads-cli"

BASE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.state")
FB_STATE = os.path.join(BASE, "fb-posted.json")
STATE_FILE = os.path.join(BASE, "threads-posted.json")

MAX_PER_RUN = 2          # mirrors FB's pace; catch-up drains over runs
MIRROR_WINDOW_HOURS = 48  # only mirror picks still fresh enough to matter
SEED_AGE_HOURS = 24       # older FB picks are seeded as already-mirrored
PENDING_TTL_SECS = 3 * 3600
CHAR_LIMIT = 500


def sb_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-s", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def load_state():
    data = load_json(STATE_FILE, None)
    if data is None:
        return None
    return (set(data.get("posted_slugs", [])),
            set(data.get("pending_slugs", [])),
            set(data.get("abandoned_slugs", [])),
            dict(data.get("pending_since", {})),
            dict(data.get("post_ids", {})))


def save_state(posted, pending, abandoned, pending_since, post_ids):
    pending_since = {s: t for s, t in pending_since.items() if s in pending}
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump({"posted_slugs": sorted(posted),
                   "pending_slugs": sorted(pending),
                   "abandoned_slugs": sorted(abandoned),
                   "pending_since": pending_since,
                   "post_ids": post_ids}, f)


def fetch_articles(slugs):
    """Bulk-fetch article rows for a set of slugs, keyed by slug."""
    if not slugs:
        return {}
    in_list = ",".join(sorted(slugs))
    rows = sb_get(
        "p2_articles?select=headline,subheadline,slug,published_at"
        f"&slug=in.({in_list})")
    if not isinstance(rows, list):
        return {}
    return {r["slug"]: r for r in rows if r.get("slug")}


def hours_since(iso_ts):
    import calendar
    try:
        ts = calendar.timegm(time.strptime(iso_ts[:19], "%Y-%m-%dT%H:%M:%S"))
        return (time.time() - ts) / 3600.0
    except Exception:
        return None


def build_text(article):
    headline = (article.get("headline") or "").strip()
    summary = (article.get("subheadline") or "").strip()
    url = f"https://www.thevideshi.com/articles/{article['slug']}"
    text = headline
    if summary and summary.lower() not in headline.lower():
        candidate = f"{headline}\n\n{summary}\n\n{url}"
        if len(candidate) <= CHAR_LIMIT:
            return candidate
        # Trim the summary at a word boundary to fit.
        budget = CHAR_LIMIT - len(headline) - len(url) - 5  # \n\n x2 + slack
        if budget > 40:
            trimmed = summary[:budget].rsplit(" ", 1)[0] + "…"
            return f"{headline}\n\n{trimmed}\n\n{url}"
    text = f"{headline}\n\n{url}"
    if len(text) > CHAR_LIMIT:
        text = headline[:CHAR_LIMIT - len(url) - 3].rsplit(" ", 1)[0] \
            + "…\n\n" + url
    return text


def publish(text):
    cmd = [THREADS_CLI, "publish-post", "--account-id", ACCOUNT_ID,
           "--text", text]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return None  # ambiguous — caller marks pending and verifies later
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: threads-cli output not JSON: {r.stdout[:300]}",
              file=sys.stderr)
        return None
    if data.get("post_id"):
        return data
    print(f"ERROR: publish failed: {r.stdout[:400]}", file=sys.stderr)
    return None


def verify_pending(slug):
    """True if a recent brand Threads post carries this article's URL."""
    url = f"https://www.thevideshi.com/articles/{slug}"
    cmd = [THREADS_CLI, "profile-threads", "--account-id", ACCOUNT_ID,
           "--user-id", ACCOUNT_ID, "--first", "10"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        data = json.loads(r.stdout)
    except Exception as e:
        print(f"ERROR: verify failed: {e}", file=sys.stderr)
        return False
    for post in data.get("posts", []):
        if url in (post.get("post_caption_text") or ""):
            return True
    return False


def main():
    fb = load_json(FB_STATE, {})
    fb_posted = set(fb.get("posted_slugs", []))
    if not fb_posted:
        print("FB ledger empty — nothing to mirror.")
        return

    state = load_state()
    if state is None:
        # First run: seed historical FB picks so they are never mirrored.
        articles = fetch_articles(fb_posted)
        seeded = set()
        for slug in fb_posted:
            row = articles.get(slug)
            age = hours_since(row["published_at"]) if row else None
            if age is None or age > SEED_AGE_HOURS:
                seeded.add(slug)
        print(f"Seeding ledger: {len(seeded)} historical FB picks marked "
              f"already-mirrored; {len(fb_posted) - len(seeded)} recent.")
        if DRY_RUN:
            print("DRY RUN — seed not saved.")
            posted, pending, abandoned, pending_since, post_ids = \
                seeded, set(), set(), {}, {}
        else:
            posted, pending, abandoned, pending_since, post_ids = \
                seeded, set(), set(), {}, {}
            save_state(posted, pending, abandoned, pending_since, post_ids)
    else:
        posted, pending, abandoned, pending_since, post_ids = state

    # Resolve pending publishes from earlier runs before posting new ones.
    for slug in sorted(pending):
        if verify_pending(slug):
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
            print(f"Pending post expired unverified; slug abandoned: {slug}")
            continue
        if since is None:
            pending_since[slug] = time.time()
        print(f"ERROR: pending post still unverifiable: {slug}; "
              f"not posting anything new this run.", file=sys.stderr)
        if not DRY_RUN:
            save_state(posted, pending, abandoned, pending_since, post_ids)
        sys.exit(1)
    if not DRY_RUN:
        save_state(posted, pending, abandoned, pending_since, post_ids)

    candidates = fb_posted - posted - pending - abandoned
    if not candidates:
        print("Threads mirror is up to date with Facebook.")
        return
    articles = fetch_articles(candidates)
    fresh = []
    for slug in candidates:
        row = articles.get(slug)
        if not row:
            continue
        age = hours_since(row.get("published_at") or "")
        if age is not None and age <= MIRROR_WINDOW_HOURS:
            fresh.append(row)
    fresh.sort(key=lambda r: r.get("published_at") or "", reverse=True)
    batch = fresh[:MAX_PER_RUN]
    if not batch:
        print("No fresh FB picks inside the mirror window.")
        return

    for article in batch:
        text = build_text(article)
        print(f"Mirror: {article['headline'][:80]}")
        print(f"Text ({len(text)} chars): {text[:160]}...")
        if DRY_RUN:
            print("DRY RUN — not publishing.")
            continue
        result = publish(text)
        if result:
            posted.add(article["slug"])
            post_ids[article["slug"]] = result["post_id"]
            save_state(posted, pending, abandoned, pending_since, post_ids)
            print(f"Published to Threads: post {result['post_id']}")
        else:
            pending.add(article["slug"])
            pending_since[article["slug"]] = time.time()
            save_state(posted, pending, abandoned, pending_since, post_ids)
            print("Publish outcome unknown; slug marked pending for "
                  "re-verification.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
