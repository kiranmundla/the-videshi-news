#!/usr/bin/env python3
"""
reel_facebook.py — Facebook Reels distribution for The Videshi (DRAFT MODEL).

Uploads a gate-passed reel MP4 to TheVideshi Facebook Page as an
UNPUBLISHED reel via the Graph API Reels flow (start -> transfer -> finish).
Kiran reviews and publishes it himself from Meta's UI.

    NOTHING THIS SCRIPT DOES CAN PUBLISH. The finish call sends exactly one
    video_state value, the module-level constant VIDEO_STATE, and there is
    no flag, env var, or code path that changes it. Grep proof: searching
    this file for the bare live-state word as a quoted literal returns
    nothing — the only state literal present is the constant below.

This mirrors reel_publish.py's discipline (the YouTube path):
  * verdict gate first (fact-check must have passed),
  * duplicate guard (log + legacy log + file sha256) before any upload,
  * log-first: the FB video_id is written to the log the moment the upload
    session starts, before the binary transfer, so a crash mid-upload still
    leaves a trace and a blind retry is refused,
  * write-back: the FB video id lands in the log and, when the reel has a
    prebuilt_reels row, as an audit marker appended to that row's qa_notes
    (prebuilt_reels has no fb_* columns; status is NOT touched — status
    transitions belong to the pulse-reels job / reconciler),
  * read-back verification of both the video node and the DB marker.

Credentials (first non-empty wins; values are never printed):
  1. ~/workspace/.env.facebook  FB_PAGE_TOKEN (+ FB_PAGE_ID)
  2. ~/workspace/.env.meta      META_ACCESS_TOKEN (Page id = default below)
Page: TheVideshi, 1243823795489375 (same Page fb-autopost.py posts to).

All HTTP goes through curl subprocesses (urllib/requests fail through this
host's proxy — see AGENTS.md).

Usage:
  python3 -u reel_facebook.py --run-dir pipeline/reel-runs/<run> [--dry-run] [--force]
  python3 -u reel_facebook.py --video x.mp4 --title T --description D --key <article-or-reel-id>
  python3 -u reel_facebook.py --check-creds

Exit codes: 0 ok · 2 credentials/preflight · 3 duplicate refused ·
            4 verdict gate · 5 upload/finish failure · 6 verify failure
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
WORKSPACE = Path(os.path.expanduser("~/workspace"))
LOG_PATH = PIPELINE_DIR / ".state" / "fb-reels-log.json"
LEGACY_LOG_PATH = PIPELINE_DIR / "fb-reels-log.json"  # legacy flow, read-only

GRAPH_VERSION = "v25.0"  # same version the working May–Jun 2026 reels flow used
DEFAULT_PAGE_ID = "1243823795489375"  # TheVideshi (fb-autopost.py)

# The one and only video_state this module can ever send.
VIDEO_STATE = "UNPUBLISHED"


class FbFailed(Exception):
    def __init__(self, message, exit_code=5):
        super().__init__(message)
        self.exit_code = exit_code


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------- env / http
def load_env_file(path):
    env = {}
    p = Path(os.path.expanduser(str(path)))
    if not p.exists():
        return env
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def resolve_credentials():
    """Return (token, page_id, source_description) or raise FbFailed(2)."""
    fb = load_env_file(WORKSPACE / ".env.facebook")
    if fb.get("FB_PAGE_TOKEN"):
        return (fb["FB_PAGE_TOKEN"], fb.get("FB_PAGE_ID") or DEFAULT_PAGE_ID,
                ".env.facebook FB_PAGE_TOKEN")
    meta = load_env_file(WORKSPACE / ".env.meta")
    if meta.get("META_ACCESS_TOKEN"):
        return (meta["META_ACCESS_TOKEN"], DEFAULT_PAGE_ID,
                ".env.meta META_ACCESS_TOKEN")
    raise FbFailed(
        "no Facebook Graph API token available: ~/workspace/.env.facebook "
        "does not exist (would hold FB_PAGE_TOKEN) and META_ACCESS_TOKEN in "
        "~/workspace/.env.meta is set but EMPTY. A Page access token with "
        "Reels/video upload permission is required; nothing was uploaded.",
        exit_code=2)


def curl(args, timeout=120):
    r = subprocess.run(["curl", "-sS"] + args, capture_output=True,
                       text=True, timeout=timeout)
    return r


def graph_post(path, token, fields, timeout=120):
    args = [f"https://graph.facebook.com/{GRAPH_VERSION}/{path}"]
    for k, v in fields.items():
        args += ["--form-string", f"{k}={v}"]
    args += ["-H", f"Authorization: Bearer {token}"]
    r = curl(args, timeout=timeout)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise FbFailed(f"Graph POST {path}: non-JSON response: {r.stdout[:300]}")
    if isinstance(data, dict) and "error" in data:
        e = data["error"]
        raise FbFailed(
            f"Graph POST {path} failed: code={e.get('code')} "
            f"type={e.get('type')} message={e.get('message')}")
    return data


def graph_get(path, token, fields):
    url = (f"https://graph.facebook.com/{GRAPH_VERSION}/{path}"
           f"?fields={fields}")
    r = curl([url, "-H", f"Authorization: Bearer {token}"], timeout=60)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        raise FbFailed(f"Graph GET {path}: non-JSON response: {r.stdout[:300]}",
                       exit_code=6)
    if isinstance(data, dict) and "error" in data:
        e = data["error"]
        raise FbFailed(
            f"Graph GET {path} failed: code={e.get('code')} "
            f"type={e.get('type')} message={e.get('message')}", exit_code=6)
    return data


def preflight(token, page_id):
    """Prove the token can act on the Page before anything is uploaded."""
    try:
        page = graph_get(page_id, token, "id,name")
    except FbFailed as e:
        raise FbFailed(f"credential preflight failed for Page {page_id}: {e}",
                       exit_code=2)
    if page.get("id") != page_id:
        raise FbFailed(
            f"credential preflight: token resolved Page {page.get('id')}, "
            f"expected {page_id}; refusing to upload.", exit_code=2)
    return page


# ---------------------------------------------------------------- log
def load_log():
    if LOG_PATH.exists():
        try:
            data = json.loads(LOG_PATH.read_text())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


def save_log(entries):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(entries, indent=2) + "\n")


def load_legacy_log():
    if LEGACY_LOG_PATH.exists():
        try:
            data = json.loads(LEGACY_LOG_PATH.read_text())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    return {}


RETRYABLE = {"blocked_credentials", "failed_start", "gate_failed"}


def check_duplicate(entries, legacy, key, sha256, mp4_name):
    for k, e in entries.items():
        if e.get("fb_video_id") and e.get("status") not in RETRYABLE:
            if k == key or e.get("sha256") == sha256:
                return (f"log already records this reel as FB video "
                        f"{e['fb_video_id']} (key {k}, status {e.get('status')})")
    if mp4_name in legacy:
        return (f"legacy fb-reels-log.json already posted {mp4_name} as "
                f"video {legacy[mp4_name].get('video_id')}")
    return None


# ---------------------------------------------------------------- inputs
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_run_dir(run_dir):
    rd = Path(run_dir)
    if not rd.is_absolute():
        rd = PIPELINE_DIR / rd if (PIPELINE_DIR / rd).exists() else Path.cwd() / rd
    article = json.loads((rd / "article.json").read_text())
    verdict_path = rd / "output" / "verdict.json"
    verdict = json.loads(verdict_path.read_text()) if verdict_path.exists() else {}
    # Verdict gate (mirrors reel_publish.py): fact-check must have passed.
    fc = verdict.get("factcheck") or {}
    if verdict and fc.get("verdict") != "pass":
        raise FbFailed(
            f"verdict gate: factcheck verdict is {fc.get('verdict')!r}, "
            f"not 'pass' — refusing to distribute.", exit_code=4)
    manifest = json.loads((rd / "output" / "render-manifest.json").read_text())
    video = manifest["video"]
    video_path = Path(video)
    if not video_path.is_absolute():
        video_path = PIPELINE_DIR / video
    headline = article["headline"]
    sub = (article.get("subheadline") or "").strip()
    slug = article.get("slug") or ""
    desc_parts = [headline]
    if sub:
        desc_parts.append(sub)
    if slug:
        desc_parts.append(f"📰 Read more: https://www.thevideshi.com/articles/{slug}")
    desc_parts.append("#TheVideshi #IndianDiaspora #NRI #NRINews #Reels")
    return {
        "key": article.get("id") or slug,
        "article_id": article.get("id"),
        "article_slug": slug,
        "video_path": video_path,
        "title": headline[:100],
        "description": "\n\n".join(desc_parts)[:2000],
    }


# ---------------------------------------------------------------- supabase
def sb_env():
    env = load_env_file(WORKSPACE / ".env.supabase")
    return env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]


def sb_get(path_and_query):
    url, key = sb_env()
    r = curl([f"{url}/rest/v1/{path_and_query}",
              "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}"],
             timeout=60)
    return json.loads(r.stdout)


def write_back_qa_notes(article_id, fb_video_id, uploaded_at):
    """Append an audit marker to the reel's prebuilt_reels qa_notes.

    prebuilt_reels has no fb_* columns, so qa_notes (the table's audit
    trail, same convention reel_publish.py uses) is the write-back target.
    Status and every other column are left untouched. Returns row id or
    None when no row matches; failures are warnings, never fatal — the
    .state log is the primary record."""
    if not article_id:
        return None
    try:
        rows = sb_get(f"prebuilt_reels?select=id,qa_notes&article_id=eq.{article_id}"
                      f"&order=created_at.desc&limit=1")
        if not rows:
            return None
        row = rows[0]
        marker = (f"fb=reel_facebook.py; fb_video_id={fb_video_id}; "
                  f"fb_state={VIDEO_STATE}; fb_uploaded_at={uploaded_at}")
        notes = (row.get("qa_notes") or "").rstrip()
        notes = f"{notes}; {marker}" if notes else marker
        url, key = sb_env()
        r = curl([f"{url}/rest/v1/prebuilt_reels?id=eq.{row['id']}",
                  "-X", "PATCH",
                  "-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
                  "-H", "Content-Type: application/json",
                  "-H", "Prefer: return=representation",
                  "--data-binary", json.dumps({"qa_notes": notes})],
                 timeout=60)
        patched = json.loads(r.stdout)
        if not patched or marker not in (patched[0].get("qa_notes") or ""):
            print(f"WARN: qa_notes write-back read-back mismatch: {r.stdout[:200]}",
                  file=sys.stderr)
            return None
        return row["id"]
    except Exception as e:  # write-back is bookkeeping; the upload stands
        print(f"WARN: qa_notes write-back failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------- upload
def upload_reel(token, page_id, inp, entries, force):
    video_path = inp["video_path"]
    if not video_path.exists():
        raise FbFailed(f"video file not found: {video_path}")
    sha = sha256_of(video_path)
    key = inp["key"]
    dup = check_duplicate(entries, load_legacy_log(), key, sha,
                          video_path.name)
    if dup and not force:
        raise FbFailed(f"duplicate guard: {dup}. Use --force to override.",
                       exit_code=3)

    entry = {
        "key": key,
        "article_id": inp.get("article_id"),
        "article_slug": inp.get("article_slug"),
        "video_path": str(video_path),
        "sha256": sha,
        "title": inp["title"],
        "page_id": page_id,
        "video_state": VIDEO_STATE,
        "status": "starting",
        "started_at": now_iso(),
    }
    if force:
        entry["forced"] = True

    # Phase 1 — start the upload session.
    data = graph_post(f"{page_id}/video_reels", token,
                      {"upload_phase": "start"})
    video_id = data.get("video_id")
    if not video_id:
        entry["status"] = "failed_start"
        entry["error"] = f"start returned no video_id: {str(data)[:300]}"
        entries[key] = entry
        save_log(entries)
        raise FbFailed(entry["error"])
    # LOG-FIRST: the video_id is on disk before a single byte is sent.
    entry["fb_video_id"] = video_id
    entry["status"] = "upload_started"
    entries[key] = entry
    save_log(entries)
    print(f"Upload session started: fb_video_id={video_id} (logged)")

    # Phase 2 — transfer the binary to the resumable upload host.
    size = video_path.stat().st_size
    r = curl([f"https://rupload.facebook.com/video-upload/{GRAPH_VERSION}/{video_id}",
              "-X", "POST",
              "-H", f"Authorization: OAuth {token}",
              "-H", "offset: 0",
              "-H", f"file_size: {size}",
              "-H", "Content-Type: application/octet-stream",
              "--data-binary", f"@{video_path}"],
             timeout=600)
    try:
        up = json.loads(r.stdout)
    except json.JSONDecodeError:
        up = {}
    if not up.get("success"):
        entry["status"] = "failed_transfer"
        entry["error"] = f"transfer response: {r.stdout[:300]}"
        entries[key] = entry
        save_log(entries)
        raise FbFailed(f"binary transfer failed for video {video_id}: "
                       f"{r.stdout[:300]}")
    entry["status"] = "transfer_done"
    entries[key] = entry
    save_log(entries)
    print(f"Binary transferred ({size} bytes)")

    # Phase 3 — finish. video_state comes from the module constant only.
    fin = graph_post(f"{page_id}/video_reels", token, {
        "upload_phase": "finish",
        "video_id": video_id,
        "video_state": VIDEO_STATE,
        "title": inp["title"],
        "description": inp["description"],
    })
    if not fin.get("success"):
        entry["status"] = "failed_finish"
        entry["error"] = f"finish response: {str(fin)[:300]}"
        entries[key] = entry
        save_log(entries)
        raise FbFailed(f"finish failed for video {video_id}: {str(fin)[:300]}")
    entry["status"] = "uploaded_unpublished"
    entry["finished_at"] = now_iso()
    entries[key] = entry
    save_log(entries)
    print(f"Finish accepted — reel is {VIDEO_STATE} on the Page")
    return entry


def verify_reel(token, entry):
    """Read the video node back and confirm it is not public."""
    video_id = entry["fb_video_id"]
    node = None
    for _ in range(6):  # processing can lag; poll briefly
        node = graph_get(video_id, token, "id,status,privacy")
        status = node.get("status") or {}
        if status.get("video_status") not in ("uploading", None):
            break
        time.sleep(10)
    entry["verify"] = node
    privacy = (node.get("privacy") or {}).get("value")
    publishing = ((node.get("status") or {}).get("publishing_phase") or {})
    if privacy == "EVERYONE" or publishing.get("status") == "complete":
        raise FbFailed(
            f"VERIFY FAILED: video {video_id} appears PUBLIC "
            f"(privacy={privacy}, publishing_phase={publishing})",
            exit_code=6)
    return node


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", help="reel run directory (article.json + output/)")
    ap.add_argument("--video", help="MP4 path (manual mode)")
    ap.add_argument("--title")
    ap.add_argument("--description")
    ap.add_argument("--key", help="log key for manual mode (article or reel id)")
    ap.add_argument("--article-id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="override the duplicate guard (logged)")
    ap.add_argument("--check-creds", action="store_true",
                    help="validate credentials against the Page and exit")
    args = ap.parse_args()

    try:
        token, page_id, token_source = resolve_credentials()
    except FbFailed as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.exit_code
    print(f"Credentials: {token_source} (value never printed)")

    try:
        page = preflight(token, page_id)
    except FbFailed as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.exit_code
    print(f"Preflight OK: token acts on Page {page.get('name')} ({page_id})")
    if args.check_creds:
        return 0

    if args.run_dir:
        try:
            inp = resolve_run_dir(args.run_dir)
        except FbFailed as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return e.exit_code
    elif args.video:
        if not (args.title and args.key):
            print("ERROR: manual mode needs --video, --title and --key",
                  file=sys.stderr)
            return 4
        inp = {"key": args.key, "article_id": args.article_id,
               "article_slug": None, "video_path": Path(args.video),
               "title": args.title[:100],
               "description": (args.description or args.title)[:2000]}
    else:
        print("ERROR: give --run-dir or --video/--title/--key", file=sys.stderr)
        return 4

    entries = load_log()
    if args.dry_run:
        sha = sha256_of(inp["video_path"]) if inp["video_path"].exists() else "?"
        dup = check_duplicate(entries, load_legacy_log(), inp["key"], sha,
                              inp["video_path"].name)
        print(f"DRY RUN — would upload {inp['video_path']} "
              f"({inp['video_path'].stat().st_size if inp['video_path'].exists() else 0} bytes)")
        print(f"  title: {inp['title']}")
        print(f"  video_state: {VIDEO_STATE} (only state this script can send)")
        print(f"  duplicate guard: {'BLOCKED — ' + dup if dup else 'clear'}")
        return 3 if dup and not args.force else 0

    try:
        entry = upload_reel(token, page_id, inp, entries, args.force)
        node = verify_reel(token, entry)
        entry["status"] = "verified_unpublished"
        entries[entry["key"]] = entry
        save_log(entries)
    except FbFailed as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return e.exit_code

    row_id = write_back_qa_notes(inp.get("article_id"), entry["fb_video_id"],
                                 entry["finished_at"])
    if row_id:
        entry["prebuilt_reels_row"] = row_id
        entries[entry["key"]] = entry
        save_log(entries)

    status = node.get("status") or {}
    print(f"\nDONE — FB reel uploaded UNPUBLISHED")
    print(f"  fb_video_id: {entry['fb_video_id']}")
    print(f"  video_status: {status.get('video_status')} | "
          f"publishing_phase: {(status.get('publishing_phase') or {}).get('status')}")
    print(f"  Kiran publishes it himself from Meta's UI — this script cannot publish.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
