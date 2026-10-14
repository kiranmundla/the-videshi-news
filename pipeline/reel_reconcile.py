#!/usr/bin/env python3
"""reel_reconcile.py — reconcile the YouTube channel against our records.

Phase 2 (approved by Kiran 2026-10-14). Built after the Oct 9–12 breach, in
which a legacy job uploaded PUBLIC Shorts with no write-back to
prebuilt_reels, so the database could not be trusted as the record of what
is live. This tool compares three sources of truth:

  1. the channel's ACTUAL uploads (YouTube API, uploads playlist),
  2. prebuilt_reels (Supabase),
  3. the upload logs: pipeline/reel-publish-log.json (Phase 2) and the
     legacy pipeline/youtube-log.json.

and reports:
  (a) channel videos with NO database record ("unknown"), split into
      legacy-logged (the old path uploaded them; incl. the Oct 2026 rogue
      run) and fully unknown (e.g. uploaded by hand in Studio);
  (b) prebuilt_reels rows whose yt_video_id is NOT on the channel
      ("ghost" rows — deleted videos, or bogus ids);
  (c) privacy flags: Phase 2 uploads that went up unlisted and are now
      public (Kiran's manual flip is the expected cause — listed, never
      auto-changed), and public channel videos with no DB record at all;
  (d) the in-sync count: channel videos backed by a DB/publish-log record.

READ-ONLY by design: this module issues GET requests only. It never
deletes, unlists, retitles, or edits anything on YouTube or in Supabase.

Usage:
    python3 -u reel_reconcile.py [--outdir pipeline/reports]

Writes reel-reconciliation-YYYY-MM-DD.md / .json and prints a summary.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_publish as rp  # env loading + curl helpers (read-only use here)

PIPELINE_DIR = Path(__file__).resolve().parent
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


# ---------------------------------------------------------------- fetching

def fetch_channel_videos(token):
    """All uploads on the channel: {video_id: {title, published_at, privacy}}."""
    me = rp.curl_json(
        ["https://www.googleapis.com/youtube/v3/channels"
         "?part=contentDetails&mine=true",
         "-H", f"Authorization: Bearer {token}"])
    items = me.get("items") or []
    if not items:
        raise RuntimeError(f"could not resolve own channel: {json.dumps(me)[:200]}")
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    video_ids = []
    page_token = ""
    while True:
        url = ("https://www.googleapis.com/youtube/v3/playlistItems"
               f"?part=contentDetails&playlistId={uploads}&maxResults=50")
        if page_token:
            url += f"&pageToken={page_token}"
        page = rp.curl_json([url, "-H", f"Authorization: Bearer {token}"])
        for item in page.get("items") or []:
            video_ids.append(item["contentDetails"]["videoId"])
        page_token = page.get("nextPageToken") or ""
        if not page_token:
            break

    videos = {}
    for i in range(0, len(video_ids), 50):
        batch = ",".join(video_ids[i:i + 50])
        data = rp.curl_json(
            ["https://www.googleapis.com/youtube/v3/videos"
             f"?part=snippet,status&id={batch}",
             "-H", f"Authorization: Bearer {token}"])
        for item in data.get("items") or []:
            videos[item["id"]] = {
                "title": item["snippet"]["title"],
                "published_at": item["snippet"]["publishedAt"],
                "privacy": item["status"]["privacyStatus"],
            }
    # Ids the playlist named but videos.list did not return (e.g. deleted
    # between calls) are surfaced as unknown-privacy entries, not dropped.
    for vid in video_ids:
        videos.setdefault(vid, {"title": "(unavailable)", "published_at": "",
                                 "privacy": "unknown"})
    return videos


def fetch_db_rows():
    return rp.sb_get("prebuilt_reels?select=id,article_slug,headline,status,"
                     "yt_video_id,yt_posted_at,source,reel_format,qa_notes"
                     "&order=created_at.asc")


# ---------------------------------------------------------------- classify

def classify(channel, db_rows, legacy_log, publish_entries):
    """Pure classification — unit-tested in test_reel_publish.py.

    channel: {video_id: {title, published_at, privacy}}
    db_rows: prebuilt_reels rows (dicts)
    legacy_log: youtube-log.json dict (filename -> entry)
    publish_entries: reel-publish-log.json list
    """
    db_by_video = {}
    for row in db_rows:
        vid = row.get("yt_video_id")
        if vid:
            db_by_video.setdefault(vid, []).append(row)
    pub_by_video = {e["video_id"]: e for e in publish_entries if e.get("video_id")}
    log_by_video = {}
    for fname, entry in legacy_log.items():
        vid = (entry or {}).get("video_id") or ""
        if vid and not vid.startswith("skipped"):
            log_by_video[vid] = {**entry, "file": fname}

    in_sync, unknown_legacy, unknown_other = [], [], []
    public_no_record, phase2_now_public = [], []
    for vid, info in sorted(channel.items(),
                            key=lambda kv: kv[1].get("published_at") or ""):
        rec = {**info, "video_id": vid}
        if vid in db_by_video:
            rec["record"] = f"prebuilt_reels:{db_by_video[vid][0]['id']}"
            in_sync.append(rec)
        elif vid in pub_by_video:
            rec["record"] = "reel-publish-log"
            in_sync.append(rec)
            if info.get("privacy") == "public":
                phase2_now_public.append(rec)
        elif vid in log_by_video:
            rec["legacy"] = log_by_video[vid]
            unknown_legacy.append(rec)
        else:
            unknown_other.append(rec)
        if info.get("privacy") == "public" and vid not in db_by_video \
                and vid not in pub_by_video:
            public_no_record.append(rec)

    ghost_rows = []
    superseded_rows = []
    for row in db_rows:
        vid = row.get("yt_video_id")
        if rp.is_superseded_row(row):
            # Owner-deleted / replaced uploads (marked via
            # reel_publish.py --supersede): documented history, NOT
            # ghosts, whether or not the video is still on the channel.
            superseded_rows.append({
                "row_id": row["id"], "article_slug": row.get("article_slug"),
                "yt_video_id": vid, "status": row.get("status"),
                "yt_posted_at": row.get("yt_posted_at"),
                "on_channel": bool(vid and vid in channel),
            })
            continue
        if vid and vid not in channel:
            ghost_rows.append({
                "row_id": row["id"], "article_slug": row.get("article_slug"),
                "yt_video_id": vid, "status": row.get("status"),
                "yt_posted_at": row.get("yt_posted_at"),
                "malformed_id": not bool(VIDEO_ID_RE.match(vid)),
            })

    return {
        "counts": {
            "channel_videos": len(channel),
            "db_rows": len(db_rows),
            "db_rows_with_yt_id": sum(1 for r in db_rows if r.get("yt_video_id")),
            "legacy_log_entries": len(log_by_video),
            "publish_log_entries": len(pub_by_video),
            "in_sync": len(in_sync),
            "unknown_legacy_logged": len(unknown_legacy),
            "unknown_no_record": len(unknown_other),
            "ghost_db_rows": len(ghost_rows),
            "superseded_db_rows": len(superseded_rows),
            "public_without_db_record": len(public_no_record),
            "phase2_uploads_now_public": len(phase2_now_public),
        },
        "in_sync": in_sync,
        "unknown_legacy_logged": unknown_legacy,
        "unknown_no_record": unknown_other,
        "ghost_db_rows": ghost_rows,
        "superseded_rows": superseded_rows,
        "public_without_db_record": public_no_record,
        "phase2_uploads_now_public": phase2_now_public,
    }


# ---------------------------------------------------------------- report

def render_markdown(report, generated_at):
    c = report["counts"]
    lines = [
        "# Reel reconciliation — The Videshi (YouTube @the.videshi)",
        "",
        f"Generated: {generated_at} · Tool: `pipeline/reel_reconcile.py` "
        "(read-only; nothing was changed on YouTube or in the database)",
        "",
        "## Counts",
        "",
        f"- Channel uploads (actual, via API): **{c['channel_videos']}**",
        f"- prebuilt_reels rows: {c['db_rows']} "
        f"({c['db_rows_with_yt_id']} with a yt_video_id)",
        f"- Legacy youtube-log.json entries: {c['legacy_log_entries']}",
        f"- Phase 2 publish-log entries: {c['publish_log_entries']}",
        f"- **In sync** (channel video backed by a DB/publish-log record): "
        f"**{c['in_sync']}**",
        f"- Unknown — legacy-logged only: {c['unknown_legacy_logged']}",
        f"- Unknown — no record anywhere: {c['unknown_no_record']}",
        f"- Ghost DB rows (yt_video_id not on channel): {c['ghost_db_rows']}",
        f"- Superseded DB rows (owner-deleted/replaced; not ghosts): "
        f"{c['superseded_db_rows']}",
        f"- Public with no DB record: {c['public_without_db_record']}",
        f"- Phase 2 uploads now public (manual flip expected): "
        f"{c['phase2_uploads_now_public']}",
        "",
    ]

    def section(title, rows, fmt):
        lines.append(f"## {title} ({len(rows)})")
        lines.append("")
        if not rows:
            lines.append("_None._")
        for r in rows:
            lines.append(fmt(r))
        lines.append("")

    section("(a1) Unknown channel videos — legacy-logged (old upload path)",
            report["unknown_legacy_logged"],
            lambda r: f"- `{r['video_id']}` · {r['privacy']} · "
                      f"{(r['published_at'] or '')[:10]} · {r['title']} "
                      f"(log slug: {r['legacy'].get('article_slug')})")
    section("(a2) Unknown channel videos — no record anywhere",
            report["unknown_no_record"],
            lambda r: f"- `{r['video_id']}` · {r['privacy']} · "
                      f"{(r['published_at'] or '')[:10]} · {r['title']}")
    section("(b) Ghost DB rows — yt_video_id not on the channel",
            report["ghost_db_rows"],
            lambda r: f"- row `{r['row_id']}` · slug {r['article_slug']} · "
                      f"yt_video_id `{r['yt_video_id']}` · "
                      f"status {r['status']}"
                      + (" · MALFORMED ID" if r["malformed_id"] else ""))
    section("(c1) Privacy flag — public channel videos with no DB record",
            report["public_without_db_record"],
            lambda r: f"- `{r['video_id']}` · "
                      f"{(r['published_at'] or '')[:10]} · {r['title']}")
    section("(c2) Privacy flag — Phase 2 (unlisted) uploads now public",
            report["phase2_uploads_now_public"],
            lambda r: f"- `{r['video_id']}` · {r['title']} "
                      f"(flip is Kiran's manual step; listed for visibility)")
    section("(e) Superseded DB rows — owner-deleted or replaced (not ghosts)",
            report["superseded_rows"],
            lambda r: f"- row `{r['row_id']}` · slug {r['article_slug']} · "
                      f"yt_video_id `{r['yt_video_id']}` · "
                      f"on channel: {'yes' if r['on_channel'] else 'no'}")
    section("(d) In sync",
            report["in_sync"],
            lambda r: f"- `{r['video_id']}` · {r['privacy']} · "
                      f"{(r['published_at'] or '')[:10]} · {r['title']} "
                      f"[{r['record']}]")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--outdir", default=str(PIPELINE_DIR / "reports"))
    args = ap.parse_args(argv)
    rp.load_env()
    token = rp.get_access_token()
    channel = fetch_channel_videos(token)
    db_rows = fetch_db_rows()
    legacy_log = rp.load_legacy_log()
    publish_entries = rp.load_publish_log()
    report = classify(channel, db_rows, legacy_log, publish_entries)

    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report["generated_at"] = generated_at
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    md_path = outdir / f"reel-reconciliation-{day}.md"
    json_path = outdir / f"reel-reconciliation-{day}.json"
    md_path.write_text(render_markdown(report, generated_at))
    json_path.write_text(json.dumps(report, indent=2) + "\n")

    c = report["counts"]
    print(f"Channel videos:        {c['channel_videos']}")
    print(f"In sync:               {c['in_sync']}")
    print(f"Unknown (legacy log):  {c['unknown_legacy_logged']}")
    print(f"Unknown (no record):   {c['unknown_no_record']}")
    print(f"Ghost DB rows:         {c['ghost_db_rows']}")
    print(f"Superseded DB rows:    {c['superseded_db_rows']}")
    print(f"Public, no DB record:  {c['public_without_db_record']}")
    print(f"Phase 2 now public:    {c['phase2_uploads_now_public']}")
    print(f"\nReports: {md_path}\n         {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
