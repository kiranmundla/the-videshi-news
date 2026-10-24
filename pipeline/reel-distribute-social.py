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
Usage: python3 -u reel-distribute-social.py [--dry-run]
Env: .env.supabase + .env.youtube sourced by the caller.
"""
import json
import os
import subprocess
import sys

DRY_RUN = "--dry-run" in sys.argv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_publish  # noqa: E402  (get_access_token + sb helpers)

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
    acted = 0
    for row in rows:
        vid = row["yt_video_id"]
        entry = state.setdefault(vid, {})
        mp4 = os.path.join(PIPELINE, row.get("video_path") or "")
        caption = row.get("caption") or row.get("headline") or ""
        if not os.path.exists(mp4):
            print(f"SKIP {vid}: video file missing ({mp4})", file=sys.stderr)
            continue

        # 1. Facebook draft — immediate, unpublished.
        if not entry.get("fb_draft_id"):
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
                    print(f"  FB draft failed for {vid}", file=sys.stderr)

        # 2. IG + Threads — only once Kiran flips the Short public.
        if privacy.get(vid) == "public" and not entry.get("ig_done"):
            cover = make_cover(mp4, vid)
            print(f"FLIPPED PUBLIC: {row['article_slug']} ({vid}) "
                  f"— posting IG + Threads")
            if DRY_RUN:
                print("  DRY RUN — not posting.")
            else:
                ig = ig_post(mp4, cover, caption)
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
