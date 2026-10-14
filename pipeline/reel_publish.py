#!/usr/bin/env python3
"""reel_publish.py — the SINGLE sanctioned YouTube publish path for Videshi reels.

Phase 2 (approved by Kiran 2026-10-14). Publish model, locked 2026-10-12:
the pipeline uploads finished reels as UNLISTED YouTube Shorts only; Kiran
spot-checks in Studio and flips them public himself. Nothing auto-publishes,
ever. This module is the only code allowed to upload a reel:

  * Input is a reel_produce.py verdict.json. Unless the verdict is a full
    PASS (status "ready" + fact-check "pass" + frame QA passed at/above
    threshold), the publish is REFUSED before any network call. There is no
    code path that uploads an arbitrary MP4.
  * Privacy is the module-level constant PRIVACY_STATUS below. It is not a
    parameter, not an env var, not a CLI flag. The upload payload is built
    from the constant in exactly one place (build_upload_body).
  * Idempotent: a reel whose article already has a YouTube video (per
    prebuilt_reels, the Phase 2 publish log, or the legacy youtube-log.json)
    is refused, never re-uploaded.
  * Write-back BEFORE success is reported: prebuilt_reels is updated with
    yt_video_id / yt_posted_at / gate verdicts, the publish log is appended,
    and the DB row is read back and verified. If write-back fails, the run
    reports failure (the publish log still records the video_id, so a retry
    refuses as a duplicate instead of double-uploading).

All HTTP goes through curl subprocesses (urllib/requests fail through the
proxy on this box). Credentials come from ~/workspace/.env.youtube and
~/workspace/.env.supabase (already-exported env wins).

Usage:
    python3 -u reel_publish.py --verdict path/to/output/verdict.json [--dry-run]

Exit codes: 0 published (or dry-run OK) · 2 refused (gate/duplicate) ·
3 upload, verification, or write-back failure.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
WORKSPACE = Path.home() / "workspace"
PUBLISH_LOG_PATH = PIPELINE_DIR / "reel-publish-log.json"
LEGACY_LOG_PATH = PIPELINE_DIR / "youtube-log.json"

# --- THE publish model, as a constant. Do not parameterize this. ---
PRIVACY_STATUS = "unlisted"

QA_PASS_THRESHOLD = 7.0  # must match reel_frame_qa.py / reel_produce.py
YOUTUBE_CATEGORY_NEWS = "25"
ARTICLE_URL_BASE = "https://www.thevideshi.com/articles/"

REFUSED = 2
FAILED = 3


class PublishRefused(Exception):
    """Gate or duplicate refusal — raised before any upload happens."""


class PublishFailed(Exception):
    """Upload / verification / write-back failure after the gate passed."""


# ---------------------------------------------------------------- env / http

def load_env_file(path):
    """Fill os.environ from a KEY=VALUE file, without overriding real env."""
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip("'\""))
    except FileNotFoundError:
        pass


def load_env():
    load_env_file(WORKSPACE / ".env.youtube")
    load_env_file(WORKSPACE / ".env.supabase")


def curl(args, input_data=None, timeout=120):
    cmd = ["curl", "-s", "-S"] + args
    proc = subprocess.run(cmd, input=input_data, capture_output=True,
                          text=True, timeout=timeout)
    if proc.returncode != 0:
        raise PublishFailed(f"curl failed ({proc.returncode}): {proc.stderr.strip()[:300]}")
    return proc.stdout


def curl_json(args, input_data=None, timeout=120):
    out = curl(args, input_data=input_data, timeout=timeout)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        raise PublishFailed(f"non-JSON response: {out[:300]}")


def get_access_token():
    load_env()
    for var in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"):
        if not os.environ.get(var):
            raise PublishFailed(f"missing env var {var} (see ~/workspace/.env.youtube)")
    data = curl_json(
        ["-X", "POST", "https://oauth2.googleapis.com/token",
         "-d", f"client_id={os.environ['YOUTUBE_CLIENT_ID']}",
         "-d", f"client_secret={os.environ['YOUTUBE_CLIENT_SECRET']}",
         "-d", f"refresh_token={os.environ['YOUTUBE_REFRESH_TOKEN']}",
         "-d", "grant_type=refresh_token"])
    token = data.get("access_token")
    if not token:
        raise PublishFailed(f"OAuth token exchange failed: {json.dumps(data)[:300]}")
    return token


# ---------------------------------------------------------------- supabase

def _sb_headers():
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    return ["-H", f"apikey: {key}", "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Type: application/json"]


def sb_get(path_and_query):
    load_env()
    host = os.environ["SUPABASE_URL"].removeprefix("https://")
    return curl_json([f"https://{host}/rest/v1/{path_and_query}"] + _sb_headers())


def sb_write(method, path_and_query, payload, prefer):
    load_env()
    host = os.environ["SUPABASE_URL"].removeprefix("https://")
    # --data-binary @- is load-bearing: without it curl sends NO body and
    # PostgREST answers with an error object (this exact bug bit the first
    # Phase 2 write-back attempt on 2026-10-14; regression-tested below in
    # test_reel_publish.py).
    return curl(["-X", method, f"https://{host}/rest/v1/{path_and_query}"]
                + _sb_headers() + ["-H", f"Prefer: {prefer}",
                                   "--data-binary", "@-"],
                input_data=json.dumps(payload))


def db_find_rows_by_slug(slug):
    return sb_get(f"prebuilt_reels?select=*&article_slug=eq.{slug}")


def db_fetch_article(slug):
    rows = sb_get(f"p2_articles?select=id,slug,headline,subheadline,category"
                  f"&slug=eq.{slug}")
    return rows[0] if rows else None


def db_write_back(row_id, payload):
    """PATCH an existing row (row_id) or INSERT a new one. Returns the row."""
    if row_id:
        out = sb_write("PATCH", f"prebuilt_reels?id=eq.{row_id}", payload,
                       "return=representation")
    else:
        out = sb_write("POST", "prebuilt_reels", payload, "return=representation")
    parsed = json.loads(out) if out.strip() else []
    if isinstance(parsed, dict):
        # PostgREST error object, e.g. {"code": ..., "message": ...}
        raise PublishFailed(
            f"Supabase write-back error: {parsed.get('message') or out[:300]}")
    if not parsed:
        raise PublishFailed(f"write-back returned no row: {out[:300]}")
    return parsed[0]


# ---------------------------------------------------------------- logs

def load_publish_log():
    if PUBLISH_LOG_PATH.exists():
        data = json.loads(PUBLISH_LOG_PATH.read_text())
        return data if isinstance(data, list) else data.get("uploads", [])
    return []


def save_publish_log(entries):
    PUBLISH_LOG_PATH.write_text(json.dumps(entries, indent=2) + "\n")


def append_publish_log(entry):
    entries = load_publish_log()
    entries.append(entry)
    save_publish_log(entries)


def load_legacy_log():
    if LEGACY_LOG_PATH.exists():
        data = json.loads(LEGACY_LOG_PATH.read_text())
        return data if isinstance(data, dict) else {}
    return {}


# ---------------------------------------------------------------- the gate

def check_verdict(verdict):
    """Return a list of problems. Empty list = the reel may be published."""
    problems = []
    if not isinstance(verdict, dict):
        return ["verdict is not a JSON object"]
    if verdict.get("status") != "ready":
        problems.append(
            f"verdict status is {verdict.get('status')!r}, not 'ready' "
            f"(held at stage {verdict.get('stage')!r})")
    fc = verdict.get("factcheck") or {}
    if fc.get("verdict") != "pass":
        problems.append(f"fact-check verdict is {fc.get('verdict')!r}, not 'pass' "
                        f"(held claims: {fc.get('held_claims')})")
    qa = verdict.get("qa") or {}
    if qa.get("passed") is not True:
        problems.append(f"frame QA passed is {qa.get('passed')!r}, not true "
                        f"(failing checks: {qa.get('failing_checks')})")
    score = qa.get("score")
    if not isinstance(score, (int, float)) or score < QA_PASS_THRESHOLD:
        problems.append(f"frame QA score is {score!r}, below threshold "
                        f"{QA_PASS_THRESHOLD}")
    if not verdict.get("video"):
        problems.append("verdict has no video path")
    if not verdict.get("article_slug"):
        problems.append("verdict has no article_slug")
    return problems


def is_superseded_row(row):
    """A prebuilt_reels row is superseded if its status says so OR its
    qa_notes carry the `superseded=` marker. The marker form exists
    because the live prebuilt_reels_status_check does not (yet) allow
    the 'superseded' status value — see
    pipeline/migrations/add-superseded-status.sql. supersede_video
    writes the status when the schema allows it and the marker always,
    so both forms must be honoured everywhere."""
    if row.get("status") == "superseded":
        return True
    return "superseded=" in (row.get("qa_notes") or "")


def find_duplicates(slug, video_sha256, db_rows, publish_entries, legacy_log):
    """Return a list of duplicate reasons. Empty = safe to upload.

    Superseded records never block: a video the channel owner deleted in
    Studio (marked via supersede_video) is history, not a duplicate.
    """
    reasons = []
    for row in db_rows:
        if is_superseded_row(row):
            continue
        if row.get("yt_video_id"):
            reasons.append(
                f"prebuilt_reels row {row.get('id')} for this article already "
                f"has yt_video_id={row['yt_video_id']}")
    for entry in publish_entries:
        if entry.get("superseded"):
            continue
        if entry.get("article_slug") == slug:
            reasons.append(
                f"publish log already records this article as video "
                f"{entry.get('video_id')} ({entry.get('uploaded_at')})")
        elif video_sha256 and entry.get("video_sha256") == video_sha256:
            reasons.append(
                f"publish log already records this exact file (sha256) as "
                f"video {entry.get('video_id')}")
    for fname, entry in legacy_log.items():
        vid = (entry or {}).get("video_id") or ""
        if entry.get("article_slug") == slug and vid and not vid.startswith("skipped"):
            reasons.append(
                f"legacy youtube-log.json already uploaded this article as "
                f"{vid} on {entry.get('uploaded_at')} (file {fname})")
    return reasons


# ---------------------------------------------------------------- metadata

TOPIC_RULES = [
    (("h-1b", "h1b"), "H1B"),
    (("dark matter",), "DarkMatter"),
    (("green card",), "GreenCard"),
    (("ballot", "election", "midterm"), "USElections2026"),
    (("cricket",), "Cricket"),
    (("bollywood",), "Bollywood"),
    (("visa",), "VisaNews"),
    (("sensex", "nifty", "stock market"), "Markets"),
]
CATEGORY_TOPIC = {
    "nri-world": "NRI", "immigration": "Immigration",
    "markets-finance": "Markets", "entertainment": "Entertainment",
    "sports": "Sports", "technology": "TechNews", "food": "Foodie",
    "travel": "Travel", "news": "News", "lifestyle-health": "Health",
}
CATEGORY_HASHTAG = {
    "nri-world": "NRI", "immigration": "Immigration",
    "markets-finance": "Markets", "entertainment": "Entertainment",
    "sports": "Sports", "technology": "Tech", "food": "Food",
    "travel": "Travel", "lifestyle-health": "Health",
}


def topic_hashtag(article, script):
    text = " ".join([
        article.get("headline") or "",
        script.get("news_summary") or "",
        " ".join(script.get("key_entities") or []),
    ]).lower()
    for needles, tag in TOPIC_RULES:
        if any(n in text for n in needles):
            return tag
    return CATEGORY_TOPIC.get(article.get("category") or "", "TheVideshi")


def _tail_trim(base, suffix):
    budget = 100 - len(suffix)
    return base[:budget].rsplit(" ", 1)[0].rstrip(",;:-— ")


def build_title(article, script, topic):
    base = (script.get("youtube_title") or script.get("shorts_title")
            or article.get("headline") or "").strip()
    suffix = f" #Shorts #{topic}"
    if len(base) + len(suffix) <= 100:
        return base + suffix
    trimmed = _tail_trim(base, suffix)
    # If the tail trim cut into a proper-noun phrase (the first dropped word
    # is capitalized — e.g. "…Fellow of American | Physical Society"), the
    # title reads broken. Prefer dropping leading descriptor words while
    # the following word is capitalized, keeping the full news tail intact.
    dropped = base[len(trimmed):].strip().split(" ", 1)[0] if len(base) > len(trimmed) else ""
    if dropped[:1].isupper():
        words = base.split(" ")
        while (len(" ".join(words)) + len(suffix) > 100 and len(words) > 3
               and words[1][:1].isupper()):
            words.pop(0)
        head_trimmed = " ".join(words)
        if len(head_trimmed) + len(suffix) <= 100:
            return head_trimmed + suffix
    return trimmed + suffix


def build_metadata(article, script):
    topic = topic_hashtag(article, script)
    title = build_title(article, script, topic)
    slug = article.get("slug") or ""
    summary = (script.get("news_summary")
               or article.get("subheadline") or "").strip()
    payoff = (script.get("payoff") or "").strip()
    desc_parts = [summary]
    if payoff and payoff not in summary:
        desc_parts.append(payoff)
    desc_parts.append(f"Read the full story: {ARTICLE_URL_BASE}{slug}")
    cat_tag = CATEGORY_HASHTAG.get(article.get("category") or "")
    hashtags = ["#Shorts", f"#{topic}", "#IndianAmerican", "#IndianDiaspora",
                "#TheVideshi"]
    if cat_tag and f"#{cat_tag}" not in hashtags:
        hashtags.append(f"#{cat_tag}")
    desc_parts.append(" ".join(hashtags))
    description = "\n\n".join(p for p in desc_parts if p)

    tags, seen = [], set()
    candidates = list(script.get("key_entities") or [])
    low = " ".join(candidates).lower()
    if "dark matter" in low:
        candidates.append("dark matter research")
    if "h-1b" in low or "h1b" in low:
        candidates += ["H-1B visa", "H1B news"]
    candidates += ["Indian American", "Indian diaspora", "The Videshi",
                   "NRI news"]
    for cand in candidates:
        cand = cand.strip()
        if cand and cand.lower() not in seen:
            seen.add(cand.lower())
            tags.append(cand)
    tags = tags[:12]
    while sum(len(t) for t in tags) + len(tags) > 480 and len(tags) > 1:
        tags.pop()
    return {"title": title, "description": description, "tags": tags,
            "topic": topic}


def build_upload_body(metadata):
    """The ONLY place an upload payload is constructed. Privacy comes from
    the module constant — there is deliberately no way to override it."""
    return {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": YOUTUBE_CATEGORY_NEWS,
        },
        "status": {
            "privacyStatus": PRIVACY_STATUS,
            "selfDeclaredMadeForKids": False,
        },
    }


# ---------------------------------------------------------------- youtube

def youtube_upload(token, video_path, body):
    """Resumable upload via curl. Returns the new video id."""
    body_file = PIPELINE_DIR / ".reel-publish-body.json"
    body_file.write_text(json.dumps(body))
    try:
        headers_out = curl(
            ["-D", "-", "-o", "/dev/null", "-X", "POST",
             "https://www.googleapis.com/upload/youtube/v3/videos"
             "?uploadType=resumable&part=snippet,status",
             "-H", f"Authorization: Bearer {token}",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{body_file}"])
    finally:
        body_file.unlink(missing_ok=True)
    match = re.search(r"^location:\s*(\S+)", headers_out, re.I | re.M)
    if not match:
        raise PublishFailed(f"no resumable session URL in response: {headers_out[:300]}")
    session_url = match.group(1).strip()
    result = curl_json(
        ["-X", "PUT", session_url,
         "-H", "Content-Type: video/mp4",
         "--data-binary", f"@{video_path}"],
        timeout=1800)
    video_id = result.get("id")
    if not video_id:
        raise PublishFailed(f"upload returned no video id: {json.dumps(result)[:300]}")
    return video_id


def youtube_verify(token, video_id):
    """Read the video back from the API. Returns (privacy, title)."""
    data = curl_json(
        ["https://www.googleapis.com/youtube/v3/videos"
         f"?part=snippet,status&id={video_id}",
         "-H", f"Authorization: Bearer {token}"])
    items = data.get("items") or []
    if not items:
        raise PublishFailed(f"video {video_id} not visible via API after upload")
    item = items[0]
    return item["status"]["privacyStatus"], item["snippet"]["title"]


def youtube_exists(token, video_id):
    """True if the video is still visible on the channel via the API."""
    data = curl_json(
        ["https://www.googleapis.com/youtube/v3/videos"
         f"?part=id&id={video_id}",
         "-H", f"Authorization: Bearer {token}"])
    return bool(data.get("items"))


def db_rows_by_video(video_id):
    return sb_get(f"prebuilt_reels?select=*&yt_video_id=eq.{video_id}")


def supersede_video(video_id, note, deps=None):
    """Mark a Phase 2 upload superseded after the channel owner deleted
    the video in Studio (e.g. to redo it with a different music bed).

    Ledger truth, kept in BOTH records:
    * the reel-publish-log.json entry gains `superseded` (timestamp),
      `superseded_reason` and `superseded_note` — find_duplicates ignores
      superseded entries, so a redo of the same story may publish;
    * the prebuilt_reels row keeps its yt_video_id (the upload DID
      happen) and is marked superseded — status "superseded" when the
      table's status CHECK allows it, otherwise the `superseded=`
      marker in qa_notes (is_superseded_row honours both) — so
      find_duplicates ignores it and reel_reconcile.py reports it as
      superseded, not a ghost.

    Refuses if the video is still on the channel: superseding a live
    video would corrupt the duplicate guard. The DB is patched BEFORE
    the log is saved, so a failure can never leave the log claiming a
    supersede the DB doesn't show. Re-running after a partial failure
    completes the unfinished side instead of refusing. deps injects
    fakes for tests: {get_token, video_exists, db_rows, patch_row,
    publish_entries, save_log}.
    """
    deps = deps or {}
    token = (deps.get("get_token") or get_access_token)()
    exists = (deps.get("video_exists") or youtube_exists)(token, video_id)
    if exists:
        raise PublishRefused(
            f"video {video_id} is still on the channel — refusing to "
            "supersede a live video. Delete it in Studio first.")
    entries = (deps.get("publish_entries") or load_publish_log)()
    entry = next((e for e in entries if e.get("video_id") == video_id), None)
    if entry is None:
        raise PublishFailed(
            f"no publish-log entry for video {video_id}; nothing to supersede")
    rows = (deps.get("db_rows") or db_rows_by_video)(video_id)
    pending_rows = [r for r in rows if not is_superseded_row(r)]
    if entry.get("superseded") and not pending_rows:
        raise PublishRefused(f"video {video_id} is already superseded")
    now_iso = entry.get("superseded") or datetime.now(
        timezone.utc).isoformat()
    marker = (f"superseded={now_iso}; reason=owner_deleted_in_studio; "
              f"note={note}")
    patched = []
    status_fallback = False
    for row in pending_rows:
        notes = row.get("qa_notes") or ""
        payload = {"status": "superseded",
                   "qa_notes": (notes + "; " + marker) if notes else marker}
        try:
            (deps.get("patch_row") or db_write_back)(row["id"], payload)
        except PublishFailed as e:
            if "status_check" not in str(e) and "check constraint" not in str(e):
                raise
            # The live status CHECK rejects 'superseded' (the migration
            # in pipeline/migrations/add-superseded-status.sql lifts
            # this). Fall back to the qa_notes marker alone — the row
            # keeps its historical status and is_superseded_row still
            # recognises it everywhere it matters.
            payload = {"qa_notes": payload["qa_notes"]}
            (deps.get("patch_row") or db_write_back)(row["id"], payload)
            status_fallback = True
        patched.append(row["id"])
    if deps.get("db_rows") is None:
        for row in db_rows_by_video(video_id):
            if row["id"] in patched and not is_superseded_row(row):
                raise PublishFailed(
                    f"supersede read-back mismatch for row {row['id']}")
    if not entry.get("superseded"):
        entry["superseded"] = now_iso
        entry["superseded_reason"] = "owner_deleted_in_studio"
        entry["superseded_note"] = note
        (deps.get("save_log") or save_publish_log)(entries)
    return {"video_id": video_id, "superseded_at": now_iso,
            "article_slug": entry.get("article_slug"),
            "db_rows_superseded": patched,
            "status_fallback_marker_only": status_fallback}


# ---------------------------------------------------------------- publish

def resolve_inputs(verdict_path):
    verdict_path = Path(verdict_path).resolve()
    if not verdict_path.exists():
        raise PublishRefused(f"verdict file not found: {verdict_path}")
    try:
        verdict = json.loads(verdict_path.read_text())
    except json.JSONDecodeError as e:
        raise PublishRefused(f"verdict file is not valid JSON: {e}")
    problems = check_verdict(verdict)
    if problems:
        raise PublishRefused("verdict gate failed:\n  - " + "\n  - ".join(problems))

    video_rel = verdict["video"]
    video_path = PIPELINE_DIR / video_rel
    if not video_path.exists():
        alt = verdict_path.parent / Path(video_rel).name
        if alt.exists():
            video_path = alt
        else:
            raise PublishFailed(f"video file not found: {video_rel}")

    script = {}
    script_rel = verdict.get("script")
    if script_rel and (PIPELINE_DIR / script_rel).exists():
        script = json.loads((PIPELINE_DIR / script_rel).read_text())
    article = None
    if script_rel:
        article_file = (PIPELINE_DIR / script_rel).parent / "article.json"
        if article_file.exists():
            article = json.loads(article_file.read_text())
    if article is None:
        article = db_fetch_article(verdict["article_slug"])
    if article is None:
        raise PublishFailed(
            f"no article.json beside the script and no p2_articles row for "
            f"slug {verdict['article_slug']}")
    article.setdefault("slug", verdict["article_slug"])
    return verdict, video_path, script, article


def write_back(article, verdict, video_path, video_id, metadata, now_iso):
    slug = article["slug"]
    qa = verdict.get("qa") or {}
    fc = verdict.get("factcheck") or {}
    notes = (f"publisher=reel_publish.py; privacy={PRIVACY_STATUS}; "
             f"factcheck={fc.get('verdict')}; frame_qa_score={qa.get('score')}; "
             f"gate=phase2")
    payload = {
        "article_id": article.get("id"),
        "article_slug": slug,
        "headline": article.get("headline"),
        "video_path": verdict.get("video"),
        "caption": metadata["description"],
        "status": "yt_posted",
        "yt_video_id": video_id,
        "yt_posted_at": now_iso,
        "source": "pipeline",
        "reel_format": "pulse",
        "qa_passed": True if qa.get("passed") is True else None,
        "qa_score": qa.get("score"),
        "qa_checks": {
            "factcheck_verdict": fc.get("verdict"),
            "factcheck_held_claims": fc.get("held_claims"),
            "frame_qa_passed": qa.get("passed"),
            "frame_qa_score": qa.get("score"),
            "frame_qa_failing_checks": qa.get("failing_checks"),
        },
        "qa_notes": notes,
    }
    existing = [r for r in db_find_rows_by_slug(slug) if not r.get("yt_video_id")]
    row_id = existing[0]["id"] if existing else None
    try:
        row = db_write_back(row_id, payload)
    except PublishFailed:
        # The live status CHECK may not accept 'yt_posted' on this table
        # vintage; fall back to 'ready' (the value most historical uploaded
        # rows carry) and say so in qa_notes rather than failing silently.
        payload["status"] = "ready"
        payload["qa_notes"] = notes + "; status_fallback=ready"
        row = db_write_back(row_id, payload)
    # Read-back verification: success is only real if the DB shows it.
    check = sb_get(f"prebuilt_reels?select=id,yt_video_id,yt_posted_at,status"
                   f"&id=eq.{row['id']}")
    if not check or check[0].get("yt_video_id") != video_id:
        raise PublishFailed(
            f"write-back read-back mismatch for row {row.get('id')}: {check}")
    return check[0]


def publish(verdict_path, dry_run=False, deps=None):
    """Run the full publish chain. deps allows tests to inject fakes:
    {get_token, db_rows, legacy_log, publish_entries, upload, verify,
     write_back, append_log}. Returns a result dict."""
    deps = deps or {}
    verdict, video_path, script, article = resolve_inputs(verdict_path)
    slug = article["slug"]
    sha256 = hashlib.sha256(Path(video_path).read_bytes()).hexdigest()

    db_rows = (deps.get("db_rows") or db_find_rows_by_slug)(slug)
    publish_entries = (deps.get("publish_entries") or load_publish_log)()
    legacy_log = (deps.get("legacy_log") or load_legacy_log)()
    dupes = find_duplicates(slug, sha256, db_rows, publish_entries, legacy_log)
    if dupes:
        raise PublishRefused("duplicate check failed:\n  - " + "\n  - ".join(dupes))

    metadata = build_metadata(article, script)
    body = build_upload_body(metadata)
    assert body["status"]["privacyStatus"] == PRIVACY_STATUS  # paranoia, cheap

    if dry_run:
        return {"dry_run": True, "slug": slug, "video": str(video_path),
                "metadata": metadata, "body": body}

    token = (deps.get("get_token") or get_access_token)()
    video_id = (deps.get("upload") or youtube_upload)(token, video_path, body)
    privacy, live_title = (deps.get("verify") or youtube_verify)(token, video_id)
    if privacy != PRIVACY_STATUS:
        raise PublishFailed(
            f"post-upload verification: video {video_id} privacy is "
            f"{privacy!r}, expected {PRIVACY_STATUS!r}. NOT flipping it — "
            f"manual review required.")

    now_iso = datetime.now(timezone.utc).isoformat()
    entry = {
        "video_id": video_id,
        "article_slug": slug,
        "article_id": article.get("id"),
        "title": metadata["title"],
        "privacy": PRIVACY_STATUS,
        "uploaded_at": now_iso,
        "video_path": verdict.get("video"),
        "video_sha256": sha256,
        "factcheck_verdict": (verdict.get("factcheck") or {}).get("verdict"),
        "qa_score": (verdict.get("qa") or {}).get("score"),
        "publisher": "reel_publish.py",
    }
    # Publish log FIRST: if the DB write below fails, the log still records
    # the video_id and any retry refuses as a duplicate.
    (deps.get("append_log") or append_publish_log)(entry)
    row = (deps.get("write_back") or write_back)(
        article, verdict, video_path, video_id, metadata, now_iso)
    entry["prebuilt_reels_id"] = row.get("id")
    return {"dry_run": False, "slug": slug, "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "shorts_url": f"https://youtube.com/shorts/{video_id}",
            "privacy": privacy, "live_title": live_title,
            "metadata": metadata, "prebuilt_reels_row": row,
            "uploaded_at": now_iso}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--verdict",
                    help="path to a reel_produce.py verdict.json")
    ap.add_argument("--dry-run", action="store_true",
                    help="gate + duplicate checks + metadata only, no upload")
    ap.add_argument("--supersede", metavar="VIDEO_ID",
                    help="mark a Studio-deleted Phase 2 upload superseded "
                         "in both ledgers so its story may be re-published "
                         "(no upload happens)")
    ap.add_argument("--note", default="",
                    help="reason note recorded with --supersede")
    args = ap.parse_args(argv)
    load_env()
    if args.supersede:
        try:
            result = supersede_video(
                args.supersede,
                args.note or "owner deleted the video in Studio")
        except PublishRefused as e:
            print(f"REFUSED — nothing was changed.\n{e}")
            return REFUSED
        except PublishFailed as e:
            print(f"FAILED: {e}")
            return FAILED
        print(json.dumps(result, indent=2))
        print("\nSUPERSEDED — the story may be re-published from a fresh "
              "verdict; the old video stays in the ledgers as history.")
        return 0
    if not args.verdict:
        ap.error("--verdict is required unless --supersede is given")
    try:
        result = publish(args.verdict, dry_run=args.dry_run)
    except PublishRefused as e:
        print(f"REFUSED — nothing was uploaded.\n{e}")
        return REFUSED
    except PublishFailed as e:
        print(f"FAILED: {e}")
        return FAILED
    print(json.dumps(result, indent=2))
    if result.get("dry_run"):
        print("\nDRY RUN — nothing was uploaded.")
    else:
        print(f"\nPUBLISHED (unlisted): {result['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
