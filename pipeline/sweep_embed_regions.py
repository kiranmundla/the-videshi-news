#!/usr/bin/env python3
"""Sweep every <youtube> embed in published articles for US playability.

Born 2026-10-25 from the PCB highlights incident: a video can be
embeddable (oEmbed 200) yet unplayable for the US audience via
contentDetails.regionRestriction (allowed=["PK"]). First full sweep of
5,412 published articles found 3 problem embeds (2 US-blocked, 1 deleted)
out of 583 distinct videos.

Usage: python3 -u sweep_embed_regions.py [--apply-remove]
  Default is a dry-run report. --apply-remove strips ONLY embeds whose
  video is missing/deleted or not embeddable (safe mechanical fix);
  US-blocked embeds are reported, not auto-removed, because a
  US-playable alternate cut often exists and choosing it is editorial.

Env: ~/workspace/.env.supabase + ~/workspace/.env.youtube (YOUTUBE_API_KEY).
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def _vid_of(raw):
    raw = raw.strip()
    if re.match(r"^[A-Za-z0-9_-]{11}$", raw):
        return raw
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", raw) or re.search(
        r"(?:youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})", raw)
    return m.group(1) if m else None


def main():
    apply_remove = "--apply-remove" in sys.argv
    sb = _load_env("~/workspace/.env.supabase")
    yt = _load_env("~/workspace/.env.youtube")
    url, key, akey = sb["SUPABASE_URL"], sb["SUPABASE_SERVICE_ROLE_KEY"], \
        yt["YOUTUBE_API_KEY"]

    def sb_get(path):
        r = subprocess.run(
            ["curl", "-sS", f"{url}/rest/v1/{path}",
             "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}"],
            capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout)

    rows, off = [], 0
    while True:
        page = sb_get("p2_articles?status=eq.published&select=id,slug,body"
                      f"&order=published_at.desc&limit=1000&offset={off}")
        if not page:
            break
        rows.extend(page)
        off += 1000
        if len(page) < 1000:
            break
    print(f"published articles scanned: {len(rows)}")

    by_id = {}
    for row in rows:
        for raw in re.findall(r"<youtube>([^<]+)</youtube>",
                              row.get("body") or ""):
            vid = _vid_of(raw)
            if vid:
                by_id.setdefault(vid, []).append(row)
    print(f"distinct embedded videos: {len(by_id)}")

    problems = []  # (video_id, kind, [rows])
    ids = list(by_id)
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        r = subprocess.run(
            ["curl", "-sS", "https://www.googleapis.com/youtube/v3/videos"
             "?part=contentDetails,status&id=" + ",".join(chunk)
             + "&key=" + akey],
            capture_output=True, text=True, timeout=60)
        data = json.loads(r.stdout)
        found = set()
        for it in data.get("items", []):
            found.add(it["id"])
            rr = (it.get("contentDetails") or {}).get(
                "regionRestriction") or {}
            allowed, blocked = rr.get("allowed"), rr.get("blocked")
            us_ok = ("US" in allowed) if allowed is not None else (
                ("US" not in blocked) if blocked is not None else True)
            if not us_ok:
                problems.append((it["id"], "US-blocked", by_id[it["id"]]))
            elif not it["status"].get("embeddable", True):
                problems.append((it["id"], "not-embeddable",
                                 by_id[it["id"]]))
        for missing in set(chunk) - found:
            problems.append((missing, "missing", by_id[missing]))

    print(f"problem embeds: {len(problems)}")
    for vid, kind, arows in problems:
        print(f"  {vid} [{kind}] in: "
              + ", ".join(a["slug"] for a in arows))

    if apply_remove:
        os.environ["VIDESHI_OFFICIAL_VIDEO_PASS_APPLY"] = "1"
        import official_video_pass as ovp
        for vid, kind, arows in problems:
            if kind not in ("missing", "not-embeddable"):
                continue
            for a in arows:
                new_body = re.sub(
                    r"\s*<youtube>[^<]*" + re.escape(vid) + r"[^<]*</youtube>",
                    "", a["body"] or "")
                if new_body != (a["body"] or ""):
                    ok = ovp.sb_patch_body(a["id"], new_body)
                    print(f"  removed {vid} from {a['slug']}: {ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
