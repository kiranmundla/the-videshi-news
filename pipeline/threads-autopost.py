#!/usr/bin/env python3
"""
Threads auto-poster for The Videshi (@the.videshi).

Mirrors the article picks of the other text channels onto Threads,
with one shared ledger so no article ever posts twice:

  * Facebook picks (pipeline/.state/fb-posted.json) — always carry the
    article link (Threads posts are free; the link is the point).
  * X picks (pipeline/tweet-log.json) — carry the article link only
    when the X post itself did (the run's top pick, flagged with_link);
    the rest mirror as plain text, matching Kiran's cross-channel
    policy: important ones with links, the rest as plain text.

Text is reformatted for Threads' 500-character limit
(headline + subheadline [+ link]).

DELAYED-PUBLISH (default, what the slot crons run): STAGE mode —
compose the exact Threads text and append it to the shared social
publish queue (pipeline/.state/social-publish-queue.json). FB
sources include picks already STAGED in the queue by fb-autopost,
so at flush time the Facebook original (created earlier) publishes
before its Threads mirror. No Threads calls are made in stage mode;
social-publish-flush.py publishes the queue later while Kiran is
present to approve each post.

Each mirror also carries the pick's social card (card_file /
card_track): shared from the staged FB entry when it has one,
generated for the pick otherwise (social_card.py; the <600px skip
rule leaves card_file null and the flush posts text-only, as
before cards existed).

Usage: python3 -u threads-autopost.py [--dry-run]   stage (default)
       python3 -u threads-autopost.py --publish-now [--dry-run]
           legacy immediate publish (unchanged behavior)

State: pipeline/.state/threads-posted.json
  posted_slugs  — mirrored (or seeded as historical, never posted)
  pending_slugs — publish outcome unknown; re-verified next run,
                  abandoned after PENDING_TTL_SECS (never re-attempted)

First run seeds the ledger with every pick whose article is older
than SEED_AGE_HOURS, so Threads starts from today's picks instead of
dumping the whole back-catalogue.
"""
import json
import os
import subprocess
import sys
import time

DRY_RUN = "--dry-run" in sys.argv
PUBLISH_NOW = "--publish-now" in sys.argv
STAGE = not PUBLISH_NOW

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_queue  # noqa: E402

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
ACCOUNT_ID = "17841436385342619"  # Threads @the.videshi
THREADS_CLI = "/opt/hatch/bin/threads-cli"

BASE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.state")
FB_STATE = os.path.join(BASE, "fb-posted.json")
TWEET_LOG = os.path.expanduser(
    "~/workspace/the-videshi-news/pipeline/tweet-log.json")
STATE_FILE = os.path.join(BASE, "threads-posted.json")

MAX_PER_RUN = 3           # drains FB (5/day) + X (12/day) across 5 slots
MIRROR_WINDOW_HOURS = 48  # only mirror picks still fresh enough to matter
SEED_AGE_HOURS = 24       # older picks are seeded as already-mirrored
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
        "p2_articles?select=headline,subheadline,slug,published_at,category,tags,image_url"
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


def build_text(article, with_link=True):
    headline = (article.get("headline") or "").strip()
    summary = (article.get("subheadline") or "").strip()
    url = f"https://www.thevideshi.com/articles/{article['slug']}"
    tail = (f"\n\n{url}" if with_link else "") + f"\n\n{hashtag_line(article)}"
    if summary and summary.lower() not in headline.lower():
        candidate = f"{headline}\n\n{summary}{tail}"
        if len(candidate) <= CHAR_LIMIT:
            return candidate
        budget = CHAR_LIMIT - len(headline) - len(tail) - 3  # \n\n + slack
        if budget > 40:
            trimmed = summary[:budget].rsplit(" ", 1)[0] + "…"
            return f"{headline}\n\n{trimmed}{tail}"
    text = f"{headline}{tail}"
    if len(text) > CHAR_LIMIT:
        keep = CHAR_LIMIT - len(tail) - 1
        text = headline[:keep].rsplit(" ", 1)[0] + "…" + tail
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


def verify_pending(slug, headline=None):
    """True if a recent brand Threads post carries this article's URL —
    or, for plain-text mirrors with no URL, its headline."""
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
        caption = post.get("post_caption_text") or ""
        if url in caption:
            return True
        if headline and headline[:60] in caption:
            return True
    return False


def collect_picks():
    """slug -> with_link across both source channels (FB wins ties:
    an FB pick always carries its link on Threads)."""
    picks = {}
    tweets = load_json(TWEET_LOG, {})
    if isinstance(tweets, dict):
        for entry in tweets.values():
            if isinstance(entry, dict) and entry.get("slug"):
                picks[entry["slug"]] = bool(entry.get("with_link"))
    fb = load_json(FB_STATE, {})
    for slug in fb.get("posted_slugs", []):
        picks[slug] = True
    # Delayed-publish: FB picks staged in the social queue have not
    # landed in fb-posted.json yet (the flush writes it on publish),
    # but their mirrors belong in the same flush — staged after the
    # FB originals, so created-order publishing keeps FB first.
    for entry in social_queue.load_entries():
        if (entry.get("channel") == "facebook"
                and entry.get("kind") == "article_post"
                and entry.get("slug")):
            picks[entry["slug"]] = True
    return picks


def generate_card(article):
    """Render the article's social card via social_card.make_card.

    Returns (card_file, card_track): "full-bleed" / "backdrop" on
    success, "skipped" under the 600px skip rule, None when no card
    could be made. NEVER raises — the mirror stages card-less and
    the flush falls back to the text-only post, as before cards."""
    image_url = article.get("image_url")
    if not image_url:
        return None, None
    try:
        import social_card
        out = os.path.join(str(social_card.DEFAULT_OUT_DIR),
                           f"{article['slug']}.png")
        info = social_card.make_card(article["headline"],
                                     article.get("category"),
                                     image_url=image_url, out_path=out)
    except Exception as e:
        print(f"NOTE: card generation failed for {article['slug']}: {e}")
        return None, None
    if info.get("track") == "skipped":
        print(f"NOTE: card skipped for {article['slug']} "
              f"({info.get('reason')}, source {info.get('source_px')})")
        return None, "skipped"
    print(f"Card rendered: {info.get('track')} -> {info.get('out_path')}")
    return info.get("out_path"), info.get("track")


def _mirror_card(article, fb_entry):
    """(card_file, card_track) for a Threads mirror entry. Shares
    the FB counterpart's card file when the staged FB queue entry
    has one (generate once, share the file) and inherits its <600px
    skip; otherwise — X picks, ledger-only FB picks — generates
    this pick's own card the same way."""
    if fb_entry is not None:
        if fb_entry.get("card_file"):
            return fb_entry["card_file"], fb_entry.get("card_track")
        if fb_entry.get("card_track") == "skipped":
            return None, "skipped"
    return generate_card(article)


def stage_main():
    """Delayed-publish staging: compose exact Threads texts and
    queue them. No Threads calls; threads-posted.json is written by
    the flush on publish, never at stage time. Pending slugs from
    earlier immediate publishes cannot be re-verified here (that
    needs a connector read), so they are excluded and noted."""
    picks = collect_picks()
    if not picks:
        print("No source picks found — nothing to mirror.")
        return

    state = load_state()
    if state is None:
        # First run: seed historical picks so they are never mirrored.
        articles = fetch_articles(set(picks))
        seeded = set()
        for slug in picks:
            row = articles.get(slug)
            age = hours_since(row["published_at"]) if row else None
            if age is None or age > SEED_AGE_HOURS:
                seeded.add(slug)
        print(f"Seeding ledger: {len(seeded)} historical picks marked "
              f"already-mirrored; {len(picks) - len(seeded)} recent.")
        posted, pending, abandoned, pending_since, post_ids = \
            seeded, set(), set(), {}, {}
        if DRY_RUN:
            print("DRY RUN — seed not saved.")
        else:
            save_state(posted, pending, abandoned, pending_since,
                       post_ids)
    else:
        posted, pending, abandoned, pending_since, post_ids = state

    if pending:
        print(f"NOTE: {len(pending)} slug(s) pending verification from "
              f"earlier immediate publishes; excluded from staging "
              f"until a --publish-now run resolves them: "
              f"{sorted(pending)}")

    staged = social_queue.queued_slugs("threads", "article_post")
    # Staged FB entries by slug — their card files are shared with
    # the mirrors below (generate once, share the file).
    fb_cards = {e["slug"]: e for e in social_queue.load_entries()
                if e.get("channel") == "facebook"
                and e.get("kind") == "article_post" and e.get("slug")}
    candidates = {s: link for s, link in picks.items()
                  if s not in posted and s not in pending
                  and s not in abandoned and s not in staged}
    if not candidates:
        print("Threads mirror is up to date.")
        return
    articles = fetch_articles(set(candidates))
    fresh = []
    for slug, with_link in candidates.items():
        row = articles.get(slug)
        if not row:
            continue
        age = hours_since(row.get("published_at") or "")
        if age is not None and age <= MIRROR_WINDOW_HOURS:
            fresh.append((row, with_link))
    fresh.sort(key=lambda t: t[0].get("published_at") or "", reverse=True)
    batch = fresh[:MAX_PER_RUN]
    if not batch:
        print("No fresh picks inside the mirror window.")
        return

    for article, with_link in batch:
        text = build_text(article, with_link=with_link)
        print(f"Mirror: {article['headline'][:80]} "
              f"(link: {with_link})")
        print(f"Text ({len(text)} chars): {text[:160]}...")
        if DRY_RUN:
            print("DRY RUN — not staging.")
            continue
        card_file, card_track = _mirror_card(
            article, fb_cards.get(article["slug"]))
        entry = {
            "channel": "threads",
            "kind": "article_post",
            "slug": article["slug"],
            "headline": article["headline"],
            "text": text,
            "link": (f"https://www.thevideshi.com/articles/"
                     f"{article['slug']}" if with_link else None),
            "with_link": bool(with_link),
            "image_url": article.get("image_url"),
            "card_file": card_file,
            "card_track": card_track,
            "media_file": None,
            "cover_file": None,
            "alt_text": None,
            "source": "threads-autopost",
        }
        if social_queue.add_entry(entry):
            print(f"Staged for Threads: {article['slug']}")
        else:
            print(f"Already staged, skipped: {article['slug']}")


def main():
    if STAGE:
        stage_main()
        return
    picks = collect_picks()
    if not picks:
        print("No source picks found — nothing to mirror.")
        return

    state = load_state()
    if state is None:
        # First run: seed historical picks so they are never mirrored.
        articles = fetch_articles(set(picks))
        seeded = set()
        for slug in picks:
            row = articles.get(slug)
            age = hours_since(row["published_at"]) if row else None
            if age is None or age > SEED_AGE_HOURS:
                seeded.add(slug)
        print(f"Seeding ledger: {len(seeded)} historical picks marked "
              f"already-mirrored; {len(picks) - len(seeded)} recent.")
        posted, pending, abandoned, pending_since, post_ids = \
            seeded, set(), set(), {}, {}
        if DRY_RUN:
            print("DRY RUN — seed not saved.")
        else:
            save_state(posted, pending, abandoned, pending_since, post_ids)
    else:
        posted, pending, abandoned, pending_since, post_ids = state

    # Resolve pending publishes from earlier runs before posting new ones.
    pending_articles = fetch_articles(pending) if pending else {}
    for slug in sorted(pending):
        headline = (pending_articles.get(slug) or {}).get("headline")
        if verify_pending(slug, headline):
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

    candidates = {s: link for s, link in picks.items()
                  if s not in posted and s not in pending
                  and s not in abandoned}
    if not candidates:
        print("Threads mirror is up to date.")
        return
    articles = fetch_articles(set(candidates))
    fresh = []
    for slug, with_link in candidates.items():
        row = articles.get(slug)
        if not row:
            continue
        age = hours_since(row.get("published_at") or "")
        if age is not None and age <= MIRROR_WINDOW_HOURS:
            fresh.append((row, with_link))
    fresh.sort(key=lambda t: t[0].get("published_at") or "", reverse=True)
    batch = fresh[:MAX_PER_RUN]
    if not batch:
        print("No fresh picks inside the mirror window.")
        return

    for article, with_link in batch:
        text = build_text(article, with_link=with_link)
        print(f"Mirror: {article['headline'][:80]} "
              f"(link: {with_link})")
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
