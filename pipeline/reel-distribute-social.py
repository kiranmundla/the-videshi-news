#!/usr/bin/env python3
"""
Reel social distribution for The Videshi.

For every NEW gate-passed reel (prebuilt_reels row created on/after
DEPLOY_GUARD_UTC — the pre-existing backlog is Kiran's manual domain
and must never be auto-duplicated):

  1. Facebook: create an UNPUBLISHED Page draft immediately
     (facebook-cli pages drafts create). Kiran publishes it himself.
  2. Instagram + Threads: post ONLY after Kiran flips the YouTube
     Short public — his flip is the release signal. Until then the
     reel stays YouTube-unlisted and nothing goes out on IG/Threads.

State: pipeline/.state/reel-distribution.json keyed by yt_video_id.

DELAYED-PUBLISH (default, what the cron runs): STAGE mode — the FB
unpublished-draft entry and (once the Short is public) the IG +
Threads post entries are staged, fully ready (final MP4, cover,
caption, alt text), in the shared social publish queue
(pipeline/.state/social-publish-queue.json). No connector calls are
made; social-publish-flush.py creates the draft / posts later while
Kiran is present to approve each one, and the flush writes the
reel-distribution.json outcomes. YouTube privacy reads still happen
here (flip detection is read-only and token-based).

CARD DECKS (Kiran, 2026-10-25): once the Short is public, the
reel's article ALSO gets a card-carousel post staged for Facebook
and Threads (social_card.make_card_set — per-card entity sourcing,
hero on the hook card only). IG carries the reel itself; ordinary
articles without reels get single hero-image posts instead
(fb-autopost.py / threads-autopost.py).

Usage: python3 -u reel-distribute-social.py [--dry-run]   stage (default)
       python3 -u reel-distribute-social.py --publish-now [--dry-run]
           legacy immediate distribution (unchanged behavior)
Env: .env.supabase + .env.youtube sourced by the caller.
"""
import json
import os
import re
import subprocess
import sys

DRY_RUN = "--dry-run" in sys.argv
PUBLISH_NOW = "--publish-now" in sys.argv
STAGE = not PUBLISH_NOW

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_publish  # noqa: E402  (get_access_token + sb helpers)
import social_queue  # noqa: E402

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PAGE_ID = "1243823795489375"
IG_ACCOUNT_ID = "17841426005310230"       # @the.videshi
THREADS_ACCOUNT_ID = "17841436385342619"   # @the.videshi
FB_CLI = "/opt/hatch/bin/facebook-cli"
IG_CLI = "/opt/hatch/bin/instagram-cli"
THREADS_CLI = "/opt/hatch/bin/threads-cli"
PIPELINE = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
STATE_FILE = os.path.join(PIPELINE, ".state/reel-distribution.json")
COVER_DIR = os.path.join(PIPELINE, ".state/reel-covers")

# Only reels created at/after this instant are auto-distributed.
# Everything older is the manual backlog (already hand-posted by Kiran).
DEPLOY_GUARD_UTC = "2026-10-24T20:00:00+00:00"
FB_TEXT_LIMIT = 1024
THREADS_TEXT_LIMIT = 500


def sb_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-s", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


def sb_patch(path, payload):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    cmd = ["curl", "-s", "-X", "PATCH", url,
           "-H", f"apikey: {SUPABASE_KEY}",
           "-H", f"Authorization: Bearer {SUPABASE_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", json.dumps(payload)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=1)


def trim(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit - 1].rsplit(" ", 1)[0] + "…"


_MODULES = {}


def _producer(mod_name, filename):
    """Load a hyphenated producer module by path (same pattern as
    social-publish-flush.py) so deck staging reuses the exact FB /
    Threads text builders and the shared card-set renderer."""
    if mod_name not in _MODULES:
        if mod_name in sys.modules:
            _MODULES[mod_name] = sys.modules[mod_name]
            return _MODULES[mod_name]
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            mod_name, os.path.join(PIPELINE, filename))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        _MODULES[mod_name] = mod
    return _MODULES[mod_name]


def _stage_reel_decks(row):
    """Stage the reel article's CARD DECK posts for FB + Threads.

    Runs once the Short is public (same gate as the IG/Threads reel
    legs). The deck is rendered NOW, with the current social_card
    code — queued decks are never re-rendered later, so a deck must
    never be staged by old code and flushed blind (2026-10-25
    lesson). A slug already queued as an article_post on a channel
    (e.g. it was also a regular FB pick) is skipped there — the
    flush's published-ledger check is the second line of defence.
    Returns the number of entries staged."""
    slug = row.get("article_slug")
    if not slug:
        return 0
    from urllib.parse import quote
    rows = sb_get(
        "p2_articles?select=headline,subheadline,slug,category,"
        "image_url,tags,key_takeaways,body"
        f"&slug=eq.{quote(slug, safe='')}&status=eq.published")
    if not isinstance(rows, list) or not rows:
        print(f"  Deck skipped for {slug}: article not found")
        return 0
    article = rows[0]
    fb = _producer("fb_autopost", "fb-autopost.py")
    th = _producer("threads_autopost", "threads-autopost.py")
    card_files, card_track, card_texts = fb.generate_card_set(article)
    if not card_files:
        print(f"  Deck skipped for {slug}: no card set "
              f"(track={card_track})")
        return 0
    article_url = f"https://www.thevideshi.com/articles/{slug}"
    staged = 0
    fb_entry = {
        "channel": "facebook",
        "kind": "article_post",
        "slug": slug,
        "headline": article["headline"],
        "text": fb.build_post_text(article),
        "link": article_url,
        "image_url": article.get("image_url"),
        "card_file": card_files[0],
        "card_files": card_files,
        "card_texts": card_texts,
        "card_track": card_track,
        "media_file": None,
        "cover_file": None,
        "alt_text": None,
        "source": "reel-distribute-social",
    }
    if slug in social_queue.queued_slugs("facebook", "article_post"):
        print(f"  FB deck skipped (already queued): {slug}")
    elif social_queue.add_entry(fb_entry):
        staged += 1
        print(f"  Staged FB card deck for {slug}")
    th_entry = {
        "channel": "threads",
        "kind": "article_post",
        "slug": slug,
        "headline": article["headline"],
        "text": th.build_text(article),
        "link": article_url,
        "with_link": True,
        "image_url": article.get("image_url"),
        "card_file": card_files[0],
        "card_files": card_files,
        "card_texts": card_texts,
        "card_track": card_track,
        "media_file": None,
        "cover_file": None,
        "alt_text": None,
        "source": "reel-distribute-social",
    }
    if slug in social_queue.queued_slugs("threads", "article_post"):
        print(f"  Threads deck skipped (already queued): {slug}")
    elif social_queue.add_entry(th_entry):
        staged += 1
        print(f"  Staged Threads card deck for {slug}")
    return staged


def yt_privacy(video_ids):
    """Batched privacy lookup. Returns {video_id: privacyStatus}."""
    if not video_ids:
        return {}
    token = reel_publish.get_access_token()
    ids = ",".join(video_ids)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=status&id={ids}"
    r = subprocess.run(["curl", "-s", url, "-H",
                        f"Authorization: Bearer {token}"],
                       capture_output=True, text=True, timeout=30)
    data = json.loads(r.stdout)
    out = {}
    for item in data.get("items", []):
        out[item["id"]] = (item.get("status") or {}).get("privacyStatus")
    return out


def make_cover(mp4_path, video_id):
    os.makedirs(COVER_DIR, exist_ok=True)
    cover = os.path.join(COVER_DIR, f"{video_id}.jpg")
    if os.path.exists(cover):
        return cover
    r = subprocess.run(
        ["ffmpeg", "-y", "-ss", "1.2", "-i", mp4_path,
         "-frames:v", "1", "-q:v", "3", cover],
        capture_output=True, text=True, timeout=60)
    return cover if r.returncode == 0 and os.path.exists(cover) else None


STORY_URL_BASE = "https://thevideshi.com/articles/"
_STORY_LINE_RE = re.compile(
    r"^(?:Read the full story|Full story):\s*https?://\S+\s*$", re.M)


def ig_reel_caption(caption, slug):
    """Instagram reel caption: the full article URL as a
    'Full story: <url>' line immediately before the hashtag block
    (Kiran, 2026-10-25 — article links go wherever allowed and
    free; the URL rides as text even though IG doesn't make it
    tappable). The stored reel caption is the YouTube description,
    whose 'Read the full story:' line sits mid-text; on IG that
    line is normalised to 'Full story:' and moved to just above
    the hashtags. FB drafts and Threads keep the stored caption —
    their 'Read the full story:' line already carries the URL."""
    if not slug:
        return caption
    story = f"Full story: {STORY_URL_BASE}{slug}"
    text = _STORY_LINE_RE.sub("", caption or "")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return story
    lines = text.split("\n")
    idx = len(lines)
    while idx > 0 and lines[idx - 1].strip().startswith("#"):
        idx -= 1
    if idx < len(lines):
        head = "\n".join(lines[:idx]).rstrip()
        tags = "\n".join(lines[idx:])
        return f"{head}\n\n{story}\n\n{tags}" if head else \
            f"{story}\n\n{tags}"
    return f"{text}\n\n{story}"


def fb_draft(mp4_path, caption):
    cmd = [FB_CLI, "pages", "drafts", "create", "--page-id", PAGE_ID,
           "--text", trim(caption, FB_TEXT_LIMIT), "--file", mp4_path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: fb draft output not JSON: {r.stdout[:200]}",
              file=sys.stderr)
        return None
    return data.get("draft_id") or data.get("id") or data


def ig_post(mp4_path, cover, caption):
    cmd = [IG_CLI, "post-feed", "--account-id", IG_ACCOUNT_ID,
           "--file", mp4_path, "--caption", caption]
    if cover:
        cmd += ["--cover", cover]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: ig post output not JSON: {r.stdout[:200]}",
              file=sys.stderr)
        return None


def threads_post(mp4_path, cover, caption):
    item = {"file": mp4_path}
    if cover:
        item["cover"] = cover
    cmd = [THREADS_CLI, "publish-post", "--account-id", THREADS_ACCOUNT_ID,
           "--text", trim(caption, THREADS_TEXT_LIMIT),
           "--media-item", json.dumps(item)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: threads post output not JSON: {r.stdout[:200]}",
              file=sys.stderr)
        return None


def main():
    from urllib.parse import quote
    rows = sb_get(
        "prebuilt_reels?select=id,article_slug,headline,caption,video_path,"
        "yt_video_id,status,created_at"
        f"&status=eq.yt_posted&created_at=gte.{quote(DEPLOY_GUARD_UTC)}"
        "&order=created_at.asc")
    if not isinstance(rows, list):
        print("ERROR: prebuilt_reels fetch failed", file=sys.stderr)
        sys.exit(1)
    rows = [r for r in rows if r.get("yt_video_id")]
    if not rows:
        print("No new reels awaiting distribution.")
        return

    state = load_state()
    privacy = yt_privacy([r["yt_video_id"] for r in rows])
    queued_fb = social_queue.queued_refs("facebook", "reel_draft")
    queued_ig = social_queue.queued_refs("instagram", "reel_post")
    queued_th = social_queue.queued_refs("threads", "reel_post")
    acted = 0
    for row in rows:
        vid = row["yt_video_id"]
        entry = state.setdefault(vid, {})
        mp4 = os.path.join(PIPELINE, row.get("video_path") or "")
        caption = row.get("caption") or row.get("headline") or ""
        ig_text = ig_reel_caption(caption, row.get("article_slug"))
        alt_text = row.get("headline") or row.get("article_slug") or ""
        if not os.path.exists(mp4):
            print(f"SKIP {vid}: video file missing ({mp4})", file=sys.stderr)
            continue

        # 1. Facebook draft — unpublished (staged in delayed mode).
        if not entry.get("fb_draft_id"):
            if STAGE:
                if vid in queued_fb:
                    print(f"FB draft already staged: "
                          f"{row['article_slug']} ({vid})")
                else:
                    print(f"FB draft: {row['article_slug']} ({vid})")
                    if DRY_RUN:
                        print("  DRY RUN — not staging.")
                    else:
                        staged = social_queue.add_entry({
                            "channel": "facebook",
                            "kind": "reel_draft",
                            "reel_id": vid,
                            "slug": row.get("article_slug"),
                            "headline": row.get("headline"),
                            "text": trim(caption, FB_TEXT_LIMIT),
                            "link": None,
                            "media_file": mp4,
                            "cover_file": None,
                            "alt_text": alt_text,
                            "reel_row_id": row.get("id"),
                            "source": "reel-distribute-social",
                        })
                        if staged:
                            queued_fb.add(vid)
                            acted += 1
                            print(f"  Staged FB draft entry for {vid}")
            else:
                print(f"FB draft: {row['article_slug']} ({vid})")
                if DRY_RUN:
                    print("  DRY RUN — not creating.")
                else:
                    draft = fb_draft(mp4, caption)
                    if draft:
                        entry["fb_draft_id"] = str(draft)
                        acted += 1
                        save_state(state)
                    else:
                        print(f"  FB draft failed for {vid}",
                              file=sys.stderr)

        # 2. IG + Threads — only once Kiran flips the Short public.
        if privacy.get(vid) == "public" and not entry.get("ig_done"):
            cover = make_cover(mp4, vid)
            if STAGE:
                print(f"FLIPPED PUBLIC: {row['article_slug']} ({vid}) "
                      f"— staging IG + Threads")
                if DRY_RUN:
                    print("  DRY RUN — not staging.")
                else:
                    if vid not in queued_ig:
                        if social_queue.add_entry({
                            "channel": "instagram",
                            "kind": "reel_post",
                            "reel_id": vid,
                            "slug": row.get("article_slug"),
                            "headline": row.get("headline"),
                            "text": ig_text,
                            "link": None,
                            "media_file": mp4,
                            "cover_file": cover,
                            "alt_text": alt_text,
                            "reel_row_id": row.get("id"),
                            "source": "reel-distribute-social",
                        }):
                            queued_ig.add(vid)
                            acted += 1
                            print(f"  Staged IG post entry for {vid}")
                    if vid not in queued_th:
                        if social_queue.add_entry({
                            "channel": "threads",
                            "kind": "reel_post",
                            "reel_id": vid,
                            "slug": row.get("article_slug"),
                            "headline": row.get("headline"),
                            "text": trim(caption, THREADS_TEXT_LIMIT),
                            "link": None,
                            "media_file": mp4,
                            "cover_file": cover,
                            "alt_text": alt_text,
                            "reel_row_id": row.get("id"),
                            "source": "reel-distribute-social",
                        }):
                            queued_th.add(vid)
                            acted += 1
                            print(f"  Staged Threads post entry for {vid}")
                    # Card decks for this reel's article on FB +
                    # Threads (IG carries the reel itself).
                    acted += _stage_reel_decks(row)
                continue
            print(f"FLIPPED PUBLIC: {row['article_slug']} ({vid}) "
                  f"— posting IG + Threads")
            if DRY_RUN:
                print("  DRY RUN — not posting.")
            else:
                ig = ig_post(mp4, cover, ig_text)
                if ig:
                    entry["ig_done"] = True
                    entry["ig_result"] = ig.get("post_id") or ig.get("id")
                    from datetime import datetime, timezone
                    sb_patch(f"prebuilt_reels?id=eq.{row['id']}",
                             {"ig_media_id": str(entry["ig_result"] or ""),
                              "ig_posted_at": datetime.now(timezone.utc)
                              .isoformat()})
                    acted += 1
                th = threads_post(mp4, cover, caption)
                if th and th.get("post_id"):
                    entry["threads_post_id"] = th["post_id"]
                    acted += 1
                save_state(state)
        elif privacy.get(vid) != "public" and not entry.get("ig_done"):
            print(f"Waiting on flip: {row['article_slug']} ({vid}) "
                  f"is {privacy.get(vid)}")
    print(f"Done. Actions taken: {acted}")


if __name__ == "__main__":
    main()
