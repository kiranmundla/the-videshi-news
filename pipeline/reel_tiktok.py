#!/usr/bin/env python3
"""reel_tiktok.py — the SINGLE sanctioned TikTok path for Videshi reels.

Distribution model, approved by Kiran 2026-10-14 (inbox/draft model): the
pipeline uploads a finished reel to Kiran's TikTok INBOX as a draft via the
Content Posting API; Kiran reviews it in the TikTok app and posts it himself.
Nothing posts publicly through this module, ever:

  * The ONLY publish endpoint this module knows is the inbox init URL
    (INBOX_INIT_URL below). There is deliberately no direct-post URL, no
    privacy parameter and no `video.publish` scope anywhere in this file —
    the direct-post endpoint is not referenced at all, so no code path here
    can put a reel on the public profile. TikTok's app audit is therefore
    not required; inbox upload works for an unaudited app.
  * Input is a reel run directory (pipeline/reel-runs/<date>-<slug>/). The
    MP4 is taken from its output/ folder. There is no flag to upload an
    arbitrary file.
  * Log-first + duplicate guard, mirroring reel_publish.py: the upload log
    (pipeline/.state/tiktok-reels-log.json, git-ignored with the rest of
    .state) gets an entry BEFORE the first network call, keyed by
    slug + sha256 of the MP4. A reel already uploaded, in the inbox, or with
    an attempt in flight is REFUSED, never re-uploaded. If an earlier
    attempt looks in flight, its TikTok-side status is checked before any
    decision — an uncertain write is reconciled, never blindly retried.

Credentials: the custom.tiktok connector (see
~/workspace/custom-connectors/custom.tiktok/CONNECTOR.md) holds the OAuth
credential in Muse's secure store; this module pulls `hsurr:` surrogates
from dynamic_credentials.py and never sees or prints real token values on
that path. Fallback for local/manual runs: TIKTOK_* env vars, optionally
filled from ~/workspace/.env.tiktok.local (outside the repo, mode 0600).
No credential is ever written to this repo or to the upload log.

Token lifecycle (TikTok OAuth): access tokens live 24 h, refresh tokens
365 d. On an access_token_invalid response the module refreshes once via
/v2/oauth/token/ (grant_type=refresh_token) and retries. Refreshed tokens
are persisted to ~/workspace/.env.tiktok.local (mode 0600) and never
printed; if the connector vault was the source, the local file shadows it
until the next secure-flow reconnect refreshes the vault copy.

All HTTP goes through curl subprocesses (urllib/requests fail through the
proxy on this box), same as reel_publish.py.

Usage:
    python3 -u reel_tiktok.py --run-dir pipeline/reel-runs/<date>-<slug> [--dry-run]
    python3 -u reel_tiktok.py --status <publish_id>
    python3 -u reel_tiktok.py --auth-url            # print the OAuth authorize URL
    python3 -u reel_tiktok.py --exchange-code CODE  # manual fallback: code -> tokens

Exit codes: 0 uploaded / checked OK · 2 refused (duplicate) ·
3 upload, auth, or status failure.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
WORKSPACE = Path.home() / "workspace"
LOG_PATH = PIPELINE_DIR / ".state" / "tiktok-reels-log.json"
TOKEN_LOCAL_PATH = WORKSPACE / ".env.tiktok.local"
CONNECTOR_NAME = "custom.tiktok"

# --- The distribution model, as constants. Do not parameterize these. ---
# Inbox init is the only publish endpoint. The direct-post endpoint is
# intentionally ABSENT from this file — not a constant, not a code path.
INBOX_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
REDIRECT_URI = "https://www.thevideshi.com/auth/tiktok/callback"
SCOPES = "user.info.basic,video.upload"

# TikTok media-transfer rules: regular chunks 5 MB..64 MB, final chunk up to
# 128 MB, up to 1000 chunks, video up to 4 GB. 32 MB chunks keep every
# non-final chunk in range for any reel size this pipeline produces.
CHUNK_SIZE = 32_000_000
SINGLE_PUT_MAX = 64_000_000
MAX_CHUNKS = 1000

STATUS_IN_INBOX = {"SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"}
# Log states in which a repeat upload of the same reel is refused outright.
LOG_BLOCKING_STATES = {"uploading", "initialized", "uploaded", "processing",
                       "sent_to_inbox", "publish_complete"}

REFUSED = 2
FAILED = 3


class TikTokRefused(Exception):
    """Duplicate-guard refusal — raised before any upload happens."""


class TikTokFailed(Exception):
    """Auth / upload / status failure."""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- env / creds

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


def _surrogate(entry_name):
    """Return the hsurr: surrogate for one custom.tiktok entry, or None.

    The surrogate is a stand-in value that the egress layer swaps for the
    real credential on approved requests to registered hosts. It is safe to
    place in a header or form body; it is never the real secret.
    """
    try:
        sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
        from dynamic_credentials import (DynamicCredentialError,
                                         dynamic_credential_entry)
        try:
            entry = dynamic_credential_entry(CONNECTOR_NAME, entry_name)
        except DynamicCredentialError:
            return None
        value = str(entry.get("surrogate", "")).strip()
        return value if value.startswith("hsurr:") else None
    except Exception:
        return None


def load_creds():
    """Gather TikTok credentials: real env first, connector surrogates second.

    Returns a dict with any of access_token / refresh_token / client_key /
    client_secret. Values from the connector path are surrogates, never real
    secrets. Nothing here is logged.
    """
    load_env_file(TOKEN_LOCAL_PATH)
    creds = {}
    for var, name in (("TIKTOK_ACCESS_TOKEN", "access_token"),
                      ("TIKTOK_REFRESH_TOKEN", "refresh_token"),
                      ("TIKTOK_CLIENT_KEY", "client_key"),
                      ("TIKTOK_CLIENT_SECRET", "client_secret")):
        if os.environ.get(var):
            creds[name] = os.environ[var]
    for name in ("access_token", "refresh_token", "client_key", "client_secret"):
        if name not in creds:
            value = _surrogate(name)
            if value:
                creds[name] = value
    return creds


def persist_tokens(access_token, refresh_token):
    """Write refreshed tokens outside the repo, owner-only, never printed."""
    lines = []
    if TOKEN_LOCAL_PATH.exists():
        for line in TOKEN_LOCAL_PATH.read_text().splitlines():
            if line.startswith(("TIKTOK_ACCESS_TOKEN=", "TIKTOK_REFRESH_TOKEN=")):
                continue
            lines.append(line)
    lines.append(f"TIKTOK_ACCESS_TOKEN={access_token}")
    if refresh_token:
        lines.append(f"TIKTOK_REFRESH_TOKEN={refresh_token}")
    TOKEN_LOCAL_PATH.write_text("\n".join(lines) + "\n")
    os.chmod(TOKEN_LOCAL_PATH, 0o600)
    os.environ["TIKTOK_ACCESS_TOKEN"] = access_token
    if refresh_token:
        os.environ["TIKTOK_REFRESH_TOKEN"] = refresh_token


# ---------------------------------------------------------------- http (curl)

def curl(args, input_data=None, timeout=180):
    cmd = ["curl", "-s", "-S"] + args
    proc = subprocess.run(cmd, input=input_data, capture_output=True,
                          timeout=timeout)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", "replace").strip()
        raise TikTokFailed(f"curl failed ({proc.returncode}): {stderr[:300]}")
    return proc.stdout


def curl_json(args, input_data=None, timeout=180):
    out = curl(args, input_data=input_data, timeout=timeout)
    try:
        return json.loads(out.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise TikTokFailed(f"non-JSON response: {out[:300]!r}")


def tt_error(resp):
    """Extract (code, message) from a TikTok response, or None if it is ok.

    Posting endpoints wrap results in {"data": ..., "error": {"code": "ok"}};
    the OAuth token endpoint answers flat, with a top-level "error" string on
    failure. Handle both shapes.
    """
    if not isinstance(resp, dict):
        return ("bad_response", "response was not a JSON object")
    err = resp.get("error")
    if isinstance(err, dict):
        code = err.get("code", "")
        if code and code != "ok":
            return (code, err.get("message", "") or code)
        return None
    if isinstance(err, str) and err:
        return (err, resp.get("error_description", "") or err)
    return None


def api_post(url, access_token, payload):
    return curl_json(
        ["-X", "POST", url,
         "-H", f"Authorization: Bearer {access_token}",
         "-H", "Content-Type: application/json; charset=UTF-8",
         "--data-binary", "@-"],
        input_data=json.dumps(payload).encode("utf-8"))


def token_post(form):
    body = urllib.parse.urlencode(form).encode("utf-8")
    return curl_json(
        ["-X", "POST", TOKEN_URL,
         "-H", "Content-Type: application/x-www-form-urlencoded",
         "--data-binary", "@-"],
        input_data=body)


def refresh_access_token(creds):
    """Exchange the refresh token for a fresh access token. Returns creds."""
    for name in ("refresh_token", "client_key", "client_secret"):
        if not creds.get(name):
            raise TikTokFailed(
                f"cannot refresh: {name} unavailable (connector not connected "
                "or TIKTOK_* env missing) — Kiran must reconnect via the "
                "secure flow; see custom.tiktok CONNECTOR.md")
    resp = token_post({"client_key": creds["client_key"],
                       "client_secret": creds["client_secret"],
                       "grant_type": "refresh_token",
                       "refresh_token": creds["refresh_token"]})
    err = tt_error(resp)
    if err:
        raise TikTokFailed(f"token refresh failed: {err[0]} — {err[1]}")
    access = resp.get("access_token")
    if not access:
        raise TikTokFailed(f"token refresh returned no access_token: "
                           f"{json.dumps(resp)[:200]}")
    creds["access_token"] = access
    if not access.startswith("hsurr:"):
        persist_tokens(access, resp.get("refresh_token"))
    if resp.get("refresh_token") and not resp["refresh_token"].startswith("hsurr:"):
        creds["refresh_token"] = resp["refresh_token"]
    return creds


def get_access_token(creds):
    if not creds.get("access_token"):
        if creds.get("refresh_token"):
            return refresh_access_token(creds)["access_token"]
        raise TikTokFailed(
            "no TikTok access token available — the custom.tiktok connector "
            "is not connected yet (Kiran's setup steps in the connector doc "
            "come first)")
    return creds["access_token"]


def api_post_authed(url, creds, payload):
    """POST with the access token; on access_token_invalid, refresh + retry once."""
    token = get_access_token(creds)
    resp = api_post(url, token, payload)
    err = tt_error(resp)
    if err and err[0] == "access_token_invalid":
        token = refresh_access_token(creds)["access_token"]
        resp = api_post(url, token, payload)
        err = tt_error(resp)
    if err:
        raise TikTokFailed(f"{url.rsplit('/', 3)[-2]} failed: {err[0]} — {err[1]}")
    return resp


# ---------------------------------------------------------------- upload log

def load_log():
    try:
        data = json.loads(LOG_PATH.read_text())
        if isinstance(data, dict) and "uploads" in data:
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"version": 1, "uploads": {}, "by_key": {}}


def save_log(log):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LOG_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(log, indent=2))
    tmp.replace(LOG_PATH)


def log_update(log, record_id, **fields):
    entry = log["uploads"][record_id]
    entry.update(fields)
    entry["updated_at"] = now_iso()
    if entry.get("key"):
        log["by_key"][entry["key"]] = record_id
    save_log(log)


# ---------------------------------------------------------------- run dir

def resolve_run_dir(run_dir):
    """Return (mp4_path, slug, headline) for a reel run directory."""
    rd = Path(run_dir).expanduser()
    if not rd.is_dir():
        raise TikTokFailed(f"run dir not found: {rd}")
    slug = None
    headline = None
    article_path = rd / "article.json"
    if article_path.exists():
        try:
            article = json.loads(article_path.read_text())
            slug = article.get("slug") or slug
            headline = article.get("headline") or headline
        except json.JSONDecodeError:
            pass
    if not slug:
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", rd.name)
    output_dir = rd / "output"
    mp4s = sorted(output_dir.glob("*.mp4")) if output_dir.is_dir() else []
    if not mp4s:
        raise TikTokRefused(f"no MP4 under {output_dir} — nothing to upload")
    preferred = output_dir / f"{slug}.mp4"
    mp4 = preferred if preferred.exists() else mp4s[0]
    return mp4, slug, headline


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------- tiktok api

def fetch_status(creds, publish_id):
    resp = api_post_authed(STATUS_URL, creds, {"publish_id": publish_id})
    data = resp.get("data") or {}
    return data.get("status", ""), data


def upload_chunks(upload_url, mp4_path, video_size):
    """PUT the video to TikTok's upload URL in spec-sized chunks.

    Single chunk when the whole video fits the 64 MB single-PUT ceiling;
    otherwise sequential 32 MB chunks with the remainder merged into the
    final chunk. Expects 201 on the final chunk, 201 or 206 before it.
    """
    if video_size <= SINGLE_PUT_MAX:
        plan = [(0, video_size)]
    else:
        total_chunks = -(-video_size // CHUNK_SIZE)  # ceil
        if total_chunks > MAX_CHUNKS:
            raise TikTokFailed(f"video needs {total_chunks} chunks, over "
                               f"TikTok's {MAX_CHUNKS} chunk limit")
        plan = []
        for i in range(total_chunks):
            start = i * CHUNK_SIZE
            end = video_size if i == total_chunks - 1 else (i + 1) * CHUNK_SIZE
            plan.append((start, end))
    with open(mp4_path, "rb") as fh:
        for idx, (start, end) in enumerate(plan):
            length = end - start
            fh.seek(start)
            blob = fh.read(length)
            if len(blob) != length:
                raise TikTokFailed("short read on MP4 while chunking")
            out = curl(
                ["-X", "PUT", upload_url,
                 "-H", "Content-Type: video/mp4",
                 "-H", f"Content-Length: {length}",
                 "-H", f"Content-Range: bytes {start}-{end - 1}/{video_size}",
                 "--data-binary", "@-",
                 "-o", "/dev/null", "-w", "%{http_code}"],
                input_data=blob, timeout=600)
            code = int(out.decode("utf-8", "replace").strip() or "0")
            is_last = idx == len(plan) - 1
            if is_last and code != 201:
                raise TikTokFailed(f"final chunk PUT returned HTTP {code} "
                                   f"(want 201)")
            if not is_last and code not in (201, 206):
                raise TikTokFailed(f"chunk {idx + 1} PUT returned HTTP {code} "
                                   f"(want 201/206)")


# ---------------------------------------------------------------- commands

def check_existing(log, key, creds):
    """Duplicate guard. Raises TikTokRefused, or clears a dead attempt.

    If the log shows this exact reel already uploaded / in the inbox, refuse.
    If an attempt is stuck mid-flight, ask TikTok for its real status before
    deciding: in the inbox means refuse, FAILED means the retry may proceed.
    """
    record_id = log["by_key"].get(key)
    if not record_id:
        return
    entry = log["uploads"].get(record_id, {})
    state = entry.get("status", "")
    if state not in LOG_BLOCKING_STATES:
        return
    publish_id = entry.get("publish_id")
    if publish_id and state in {"initialized", "uploaded", "processing",
                                "uploading"}:
        try:
            status, _ = fetch_status(creds, publish_id)
        except TikTokFailed:
            status = ""
        if status in STATUS_IN_INBOX:
            log_update(log, record_id, status="sent_to_inbox",
                       tiktok_status=status)
            raise TikTokRefused(
                f"already in the TikTok inbox (publish_id {publish_id}) — "
                "refusing a duplicate upload")
        if status == "FAILED":
            log_update(log, record_id, status="failed",
                       fail_reason="previous attempt FAILED on TikTok")
            return
        raise TikTokRefused(
            f"an upload for this reel is still in flight on TikTok "
            f"(publish_id {publish_id}, status {status or 'unknown'}) — "
            "check --status before retrying")
    raise TikTokRefused(
        f"this reel is already logged as {state} "
        f"(publish_id {publish_id}) — refusing a duplicate upload")


def cmd_upload(args):
    mp4, slug, headline = resolve_run_dir(args.run_dir)
    video_size = mp4.stat().st_size
    digest = sha256_of(mp4)
    key = f"{slug}:{digest[:16]}"
    creds = load_creds()
    log = load_log()
    check_existing(log, key, creds)

    if args.dry_run:
        print(f"DRY RUN — would upload to TikTok inbox:")
        print(f"  mp4:      {mp4}")
        print(f"  slug:     {slug}")
        print(f"  headline: {headline}")
        print(f"  size:     {video_size} bytes, sha256 {digest[:16]}…")
        print(f"  endpoint: {INBOX_INIT_URL} (inbox/draft only)")
        return 0

    # Log-first: the entry exists BEFORE the first network call, so a crash
    # or a retry can see the attempt and refuse/reconcile instead of
    # double-uploading.
    record_id = f"{slug}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    log["uploads"][record_id] = {
        "key": key, "slug": slug, "headline": headline,
        "mp4": str(mp4.relative_to(PIPELINE_DIR.parent))
        if mp4.is_relative_to(PIPELINE_DIR.parent) else str(mp4),
        "sha256": digest, "video_size": video_size,
        "status": "uploading", "publish_id": None,
        "started_at": now_iso(), "updated_at": now_iso(),
    }
    log["by_key"][key] = record_id
    save_log(log)

    try:
        if video_size <= SINGLE_PUT_MAX:
            chunk_size, total_chunks = video_size, 1
        else:
            chunk_size = CHUNK_SIZE
            total_chunks = -(-video_size // CHUNK_SIZE)
        resp = api_post_authed(INBOX_INIT_URL, creds, {
            "source_info": {"source": "FILE_UPLOAD",
                            "video_size": video_size,
                            "chunk_size": chunk_size,
                            "total_chunk_count": total_chunks}})
        data = resp.get("data") or {}
        publish_id = data.get("publish_id")
        upload_url = data.get("upload_url")
        if not publish_id or not upload_url:
            raise TikTokFailed(f"inbox init returned no publish_id/upload_url: "
                               f"{json.dumps(resp)[:300]}")
        # publish_id is safe to log; the upload URL carries a token and is not.
        log_update(log, record_id, status="initialized", publish_id=publish_id)

        upload_chunks(upload_url, mp4, video_size)
        log_update(log, record_id, status="uploaded")

        deadline = time.time() + 240
        status = ""
        while time.time() < deadline:
            status, sdata = fetch_status(creds, publish_id)
            if status in STATUS_IN_INBOX:
                log_update(log, record_id, status="sent_to_inbox",
                           tiktok_status=status)
                print(f"OK sent_to_inbox — publish_id {publish_id}")
                print("The reel is a draft in the TikTok app inbox. "
                      "It is NOT public; Kiran posts it from the app.")
                return 0
            if status == "FAILED":
                reason = sdata.get("fail_reason", "unknown")
                log_update(log, record_id, status="failed",
                           tiktok_status=status, fail_reason=reason)
                raise TikTokFailed(f"TikTok reported FAILED: {reason}")
            time.sleep(10)
        log_update(log, record_id, status="processing", tiktok_status=status)
        print(f"Uploaded; TikTok still processing (publish_id {publish_id}). "
              f"Re-check with: --status {publish_id}")
        return 0
    except TikTokFailed as exc:
        current = log["uploads"][record_id].get("status")
        if current in LOG_BLOCKING_STATES and current != "failed":
            log_update(log, record_id, status="error", error=str(exc)[:300])
        raise


def cmd_status(args):
    creds = load_creds()
    status, data = fetch_status(creds, args.status)
    log = load_log()
    for record_id, entry in log["uploads"].items():
        if entry.get("publish_id") == args.status:
            mapped = ("sent_to_inbox" if status in STATUS_IN_INBOX
                      else status.lower() if status else entry["status"])
            log_update(log, record_id, status=mapped, tiktok_status=status,
                       **({"fail_reason": data.get("fail_reason")}
                          if status == "FAILED" else {}))
            break
    print(json.dumps({"publish_id": args.status, "status": status,
                      "fail_reason": data.get("fail_reason")}, indent=2))
    return 0


def cmd_auth_url(_args):
    load_env_file(TOKEN_LOCAL_PATH)
    client_key = os.environ.get("TIKTOK_CLIENT_KEY", "<CLIENT_KEY>")
    query = urllib.parse.urlencode({
        "client_key": client_key,
        "scope": SCOPES,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": secrets.token_hex(8),
    })
    print(f"{AUTHORIZE_URL}?{query}")
    if client_key == "<CLIENT_KEY>":
        print("\n(TIKTOK_CLIENT_KEY is not set, so the key above is a "
              "placeholder. Set it from the developer portal value first.)",
              file=sys.stderr)
    return 0


def cmd_exchange_code(args):
    load_env_file(TOKEN_LOCAL_PATH)
    client_key = os.environ.get("TIKTOK_CLIENT_KEY")
    client_secret = os.environ.get("TIKTOK_CLIENT_SECRET")
    if not client_key or not client_secret:
        raise TikTokFailed("TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET must be "
                           "set (env or ~/workspace/.env.tiktok.local) to "
                           "exchange a code")
    resp = token_post({"client_key": client_key,
                       "client_secret": client_secret,
                       "code": urllib.parse.unquote(args.exchange_code),
                       "grant_type": "authorization_code",
                       "redirect_uri": REDIRECT_URI})
    err = tt_error(resp)
    if err:
        raise TikTokFailed(f"code exchange failed: {err[0]} — {err[1]}")
    if not resp.get("access_token"):
        raise TikTokFailed(f"code exchange returned no access_token: "
                           f"{json.dumps(resp)[:200]}")
    persist_tokens(resp["access_token"], resp.get("refresh_token"))
    # Print only non-secret facts: never the token values themselves.
    print(json.dumps({
        "open_id": resp.get("open_id"),
        "scope": resp.get("scope"),
        "access_token_expires_in": resp.get("expires_in"),
        "refresh_token_expires_in": resp.get("refresh_expires_in"),
        "tokens_saved_to": str(TOKEN_LOCAL_PATH),
    }, indent=2))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Upload a Videshi reel to the TikTok inbox (draft only).")
    parser.add_argument("--run-dir", help="reel run directory under "
                                          "pipeline/reel-runs/")
    parser.add_argument("--dry-run", action="store_true",
                        help="resolve + guard-check only, no network")
    parser.add_argument("--status", metavar="PUBLISH_ID",
                        help="fetch and record the status of one upload")
    parser.add_argument("--auth-url", action="store_true",
                        help="print the TikTok OAuth authorization URL")
    parser.add_argument("--exchange-code", metavar="CODE",
                        help="manual fallback: exchange an OAuth code for tokens")
    args = parser.parse_args(argv)
    try:
        if args.status:
            return cmd_status(args)
        if args.auth_url:
            return cmd_auth_url(args)
        if args.exchange_code:
            return cmd_exchange_code(args)
        if args.run_dir:
            return cmd_upload(args)
        parser.error("one of --run-dir, --status, --auth-url, "
                     "--exchange-code is required")
    except TikTokRefused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return REFUSED
    except TikTokFailed as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return FAILED


if __name__ == "__main__":
    sys.exit(main())
