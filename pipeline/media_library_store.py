#!/usr/bin/env python3
"""
Shared store + helpers for The Videshi media_library.

Provides:
  - load_env / supabase headers
  - JSON-mirror read/write (pipeline/media-library.json)  [always works]
  - Supabase table upsert/select (best-effort; no-op if table absent)
  - Supabase Storage upload (article-images bucket, media-library/ prefix)
  - quality_score computation + quality gates
  - slug/id helpers

Imported by:
  - media-library-source.py   (writes assets)
  - media_library_lookup.py    (reads + bumps usage)
  - media-library-enqueue.py   (reads coverage)
"""

import os, re, json, hashlib, subprocess, time, html
import requests

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
MIRROR_PATH  = os.path.join(PIPELINE_DIR, "media-library.json")
QUEUE_PATH   = os.path.join(PIPELINE_DIR, "media-library-queue.json")

# Storage: reuse the existing public 'article-images' bucket under a media-library/ prefix.
STORAGE_BUCKET = "article-images"
STORAGE_PREFIX = "media-library"

# Hard quality gates (Kiran's top requirement)
MIN_IMAGE_LONGEST_SIDE = 1600     # px
MIN_VIDEO_SHORT_SIDE   = 720      # px  (>=720p; prefer 1080p)
MIN_VIDEO_DURATION     = 4.0      # sec
MAX_VIDEO_DURATION     = 90.0     # sec (avoid huge downloads; usable b-roll length)

UA = "TheVideshi/1.0 (thevideshi.com)"


# ── env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.replace("export ", "").strip()
                os.environ.setdefault(k, v.strip().strip('"').strip("'"))


load_env("~/workspace/.env.supabase")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def sb_headers(extra=None):
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    if extra:
        h.update(extra)
    return h


# ── slug / id ────────────────────────────────────────────────────────────────
def slugify(s, maxlen=60):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:maxlen] or "x"


def make_id(subject_type, subject, source_url, media_type):
    h = hashlib.sha1(f"{source_url}|{media_type}".encode()).hexdigest()[:6]
    return f"{subject_type}--{slugify(subject)}--{h}"


# ── JSON mirror ──────────────────────────────────────────────────────────────
def load_mirror():
    if os.path.exists(MIRROR_PATH):
        try:
            with open(MIRROR_PATH) as f:
                d = json.load(f)
            if isinstance(d, dict) and "assets" in d:
                return d
        except Exception:
            pass
    return {"_description": "Media library mirror — high-quality, attribution-clean images+videos for article/reel fallback. Source of truth is the Supabase media_library table; this mirror lets the pipeline read without a DB round-trip.",
            "_updated": None, "assets": []}


def save_mirror(mirror):
    mirror["_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = MIRROR_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(mirror, f, indent=1, ensure_ascii=False)
    os.replace(tmp, MIRROR_PATH)


def upsert_mirror(asset):
    """Insert/replace an asset in the JSON mirror by id."""
    mirror = load_mirror()
    assets = [a for a in mirror["assets"] if a.get("id") != asset["id"]]
    assets.append(asset)
    mirror["assets"] = assets
    save_mirror(mirror)


def mirror_assets():
    return load_mirror().get("assets", [])


def coverage_count(subject, media_type=None):
    """How many good assets already exist for a subject (case-insensitive)."""
    s = (subject or "").lower().strip()
    n = 0
    for a in mirror_assets():
        if a.get("subject", "").lower().strip() == s:
            if media_type and a.get("media_type") != media_type:
                continue
            n += 1
    return n


# ── Supabase table (best-effort) ─────────────────────────────────────────────
def table_available():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/media_library?select=id&limit=1",
                          headers=sb_headers(), timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def upsert_table(asset):
    """Upsert one asset row into Supabase. Returns True on success, False if
    table missing/unreachable (mirror is still the durable fallback)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/media_library",
            headers=sb_headers({"Content-Type": "application/json",
                                "Prefer": "resolution=merge-duplicates,return=minimal"}),
            data=json.dumps(asset), timeout=20)
        return r.status_code in (200, 201, 204)
    except Exception:
        return False


# ── Supabase Storage upload ──────────────────────────────────────────────────
def upload_bytes(data, remote_path, content_type):
    """Upload bytes to the public article-images bucket. Returns public URL or None.
    NOTE (AGENTS.md): storage uploads with the new sb_secret_ key need BOTH the
    apikey AND Authorization headers."""
    url = f"{SUPABASE_URL}/storage/v1/object/{STORAGE_BUCKET}/{remote_path}"
    headers = sb_headers({"Content-Type": content_type, "x-upsert": "true"})
    try:
        r = requests.post(url, data=data, headers=headers, timeout=120)
        if r.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{STORAGE_BUCKET}/{remote_path}"
        print(f"  ⚠ storage upload {r.status_code}: {r.text[:160]}")
    except Exception as e:
        print(f"  ⚠ storage upload error: {e}")
    return None


def upload_file(local_path, remote_path, content_type):
    with open(local_path, "rb") as f:
        return upload_bytes(f.read(), remote_path, content_type)


# ── download via curl (proxy-friendly, avoids requests 429 on wikimedia) ─────
def curl_download(src_url, dest_path, timeout=120):
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-A", UA, "-o", dest_path, src_url],
            capture_output=True, text=True, timeout=timeout + 15)
        if r.returncode == 0 and os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
            return True
        print(f"  ⚠ curl download failed rc={r.returncode}: {r.stderr[:160]}")
    except Exception as e:
        print(f"  ⚠ curl download error: {e}")
    return False


# ── quality gates + scoring ──────────────────────────────────────────────────
SOURCE_TRUST = {
    "wikimedia_commons": 1.0,
    "wikipedia": 0.9,
    "pib": 0.95,
    "openverse": 0.7,
    "pexels": 0.5,
    "coverr": 0.5,
}


def image_passes(width, height):
    if not width or not height:
        return False
    return max(width, height) >= MIN_IMAGE_LONGEST_SIDE


def video_passes(width, height, duration):
    if not width or not height or not duration:
        return False
    if min(width, height) < MIN_VIDEO_SHORT_SIDE:
        return False
    if duration < MIN_VIDEO_DURATION or duration > MAX_VIDEO_DURATION:
        return False
    return True


def quality_score(media_type, width, height, source, duration=None):
    """0..100. Resolution component + source-trust weighting.
    Wikimedia/PIB rank above generic stock."""
    trust = SOURCE_TRUST.get(source, 0.5)
    if media_type == "image":
        longest = max(width or 0, height or 0)
        # 1600px -> ~55, 2400px -> ~75, 4000px+ -> capped ~92 before trust
        res = min(92.0, 30.0 + (longest / 4000.0) * 62.0)
    else:
        short = min(width or 0, height or 0)
        # 720p -> ~50, 1080p -> ~72, 1440p+ -> capped ~88 before trust
        res = min(88.0, 30.0 + (short / 1440.0) * 58.0)
    return round(res * (0.55 + 0.45 * trust), 1)


# ── caption / attribution cleaning ───────────────────────────────────────────
_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(s):
    if not s:
        return ""
    s = _TAG_RE.sub("", s)
    s = html.unescape(s)
    return " ".join(s.split())


def probe_video(path):
    """Return (width, height, duration) via ffprobe, or (None,None,None)."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height:format=duration",
             "-of", "json", path],
            capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout or "{}")
        st = (d.get("streams") or [{}])[0]
        dur = float(d.get("format", {}).get("duration", 0) or 0)
        return st.get("width"), st.get("height"), dur
    except Exception:
        return None, None, None


def make_video_poster(video_path, poster_path):
    """Grab a frame ~1s in as the poster/thumb. Returns True/False."""
    try:
        r = subprocess.run(
            ["ffmpeg", "-y", "-ss", "1", "-i", video_path, "-frames:v", "1",
             "-q:v", "3", poster_path],
            capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and os.path.exists(poster_path)
    except Exception:
        return False


if __name__ == "__main__":
    print("media_library_store self-check")
    print("  SUPABASE_URL set:", bool(SUPABASE_URL))
    print("  table_available:", table_available())
    print("  mirror assets:", len(mirror_assets()))
