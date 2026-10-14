#!/usr/bin/env python3
"""
event_image_rehost.py — Shared helper: re-host a hotlinked event image into
our own Supabase storage (bucket `article-images`, prefix `events/`), the
same pattern the article image pipeline uses (image_sourcer.upload_to_supabase).

Approved by Kiran 2026-10-14: event images were hotlinked to source CDNs
(Eventbrite / AllEvents / Sulekha / BAPS / ...), which made event pages slow
(Sulekha TTFB measured 1.4s) and exposed us to link rot / hotlink blocking.

Contract: rehost_image(url) returns OUR public storage URL on success and
returns the ORIGINAL url unchanged on ANY failure — re-hosting must never
break or blank an event image.

Dedupe: the storage object name is a hash of the source URL, so an event
series sharing one poster produces exactly one object; a local JSON cache
(pipeline/.state/event-image-rehost-cache.json) maps source URL -> our URL
across runs. Uploads use x-upsert: true, so a re-upload is idempotent.

All HTTP goes through curl subprocesses (urllib/requests fail through this
box's proxy — see AGENTS.md).
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading

sys.stdout.reconfigure(line_buffering=True)

BUCKET = "article-images"
PREFIX = "events"
MAX_BYTES = 6 * 1024 * 1024  # skip anything larger than 6 MB
UA = "Mozilla/5.0 (compatible; TheVideshi/1.0; +https://www.thevideshi.com)"

_HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(_HERE, ".state", "event-image-rehost-cache.json")


def _load_env():
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if url and key:
        return url.rstrip("/"), key
    # Fall back to parsing the env file (jobs normally `source` it first).
    for candidate in (os.path.expanduser("~/workspace/.env.supabase"),
                      os.path.expanduser("~/.env.supabase")):
        if os.path.exists(candidate):
            vals = {}
            for line in open(candidate):
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    vals[k.strip()] = v.strip().strip('"').strip("'")
            url = url or vals.get("SUPABASE_URL", "")
            key = key or vals.get("SUPABASE_SERVICE_ROLE_KEY", "")
            if url and key:
                break
    return url.rstrip("/"), key


SUPABASE_URL, SUPABASE_KEY = _load_env()
STORAGE_HOST_FRAGMENT = ".supabase.co/storage/v1/object/public/"


def is_ours(url: str) -> bool:
    """True if the URL already points at our Supabase storage."""
    if not url or STORAGE_HOST_FRAGMENT not in url:
        return False
    if SUPABASE_URL:
        from urllib.parse import urlparse
        return urlparse(url).netloc == urlparse(SUPABASE_URL).netloc
    return True


# ---------------------------------------------------------------------------
# Local source-URL -> our-URL cache (cross-run dedupe)
# ---------------------------------------------------------------------------
_cache = None
_cache_lock = threading.Lock()


def _load_cache():
    global _cache
    if _cache is None:
        try:
            with open(CACHE_FILE) as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}
    return _cache


def _save_cache():
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        tmp = CACHE_FILE + f".tmp-{os.getpid()}-{threading.get_ident()}"
        with open(tmp, "w") as f:
            json.dump(_cache, f)
        os.replace(tmp, CACHE_FILE)
    except Exception:
        pass  # cache is an optimization; never fail the rehost over it


# ---------------------------------------------------------------------------
# Image sniffing (magic bytes, never trust headers)
# ---------------------------------------------------------------------------
def sniff_image(data: bytes):
    """Return (ext, content_type) if data starts with real image magic bytes."""
    if len(data) < 12:
        return None
    if data[:3] == b"\xff\xd8\xff":
        return ("jpg", "image/jpeg")
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ("png", "image/png")
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ("gif", "image/gif")
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ("webp", "image/webp")
    if data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis"):
        return ("avif", "image/avif")
    return None


def _compress_to_jpeg(data: bytes):
    """Mirror image_sourcer.compress_image: max width 1200, JPEG q80.
    Returns JPEG bytes, or None if PIL can't handle it (caller uploads raw)."""
    try:
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(data))
        if img.format == "GIF" and getattr(img, "is_animated", False):
            return None  # keep animated GIFs as-is
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")
        w, h = img.size
        if w > 1200:
            img = img.resize((1200, int(h * 1200 / w)), Image.LANCZOS)
        out = BytesIO()
        img.save(out, format="JPEG", quality=80, optimize=True)
        return out.getvalue()
    except Exception:
        return None


def _download(url: str):
    """Download url to a temp file via curl. Returns (path, size) or (None, reason)."""
    fd, path = tempfile.mkstemp(prefix="evrehost-", suffix=".bin")
    os.close(fd)
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "30",
             "--max-filesize", str(MAX_BYTES),
             "-A", UA, "-o", path, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=40)
        code = (r.stdout or "").strip()[-3:]
        if r.returncode != 0 or code != "200":
            os.unlink(path)
            if r.returncode == 63:
                return None, "too-big"
            return None, f"http-{code or 'err'}-{r.returncode}"
        size = os.path.getsize(path)
        if size == 0:
            os.unlink(path)
            return None, "empty"
        if size > MAX_BYTES:
            os.unlink(path)
            return None, "too-big"
        return path, size
    except Exception as e:
        try:
            os.unlink(path)
        except Exception:
            pass
        return None, f"exc-{type(e).__name__}"


def _upload(path: str, object_name: str, content_type: str):
    """Upload file to storage with the article-pipeline pattern.
    Returns (ok, detail) where detail is the raw response body on failure."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{object_name}"
    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "60", "-X", "POST", url,
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}",
             "-H", f"Content-Type: {content_type}",
             "-H", "x-upsert: true",
             "--data-binary", f"@{path}",
             "-w", "\n%{http_code}"],
            capture_output=True, text=True, timeout=75)
        body, _, code = (r.stdout or "").rpartition("\n")
        code = code.strip()
        if code == "200":
            try:
                resp = json.loads(body)
                if "Key" in resp or "Id" in resp:
                    return True, ""
            except Exception:
                pass
            return True, ""  # 200 with empty body is a success per image_sourcer
        return False, f"http-{code}: {body[:200]}"
    except Exception as e:
        return False, f"exc-{type(e).__name__}: {e}"


def rehost_image(image_url: str, event_key: str = ""):
    """
    Re-host one image. Returns (url, status, detail, nbytes):
      status "ours"     — already on our storage, returned unchanged
      status "cached"   — previously re-hosted, our URL from local cache
      status "uploaded" — downloaded, validated, uploaded now
      status "kept"     — something failed; original URL returned unchanged
    detail carries the failure reason for "kept" (http-404, not-image,
    too-big, upload:http-413:...) and is empty otherwise.
    """
    if not image_url or not isinstance(image_url, str):
        return image_url, "kept", "no-url", 0
    if image_url.startswith("//"):  # protocol-relative URL: give curl a scheme
        image_url = "https:" + image_url
    if is_ours(image_url):
        return image_url, "ours", "", 0
    if not SUPABASE_URL or not SUPABASE_KEY:
        return image_url, "kept", "no-env", 0

    cache = _load_cache()
    if image_url in cache:
        return cache[image_url], "cached", "", 0

    path, info = _download(image_url)
    if path is None:
        return image_url, "kept", info, 0
    try:
        with open(path, "rb") as f:
            data = f.read()
        sniffed = sniff_image(data)
        if not sniffed:
            return image_url, "kept", "not-image", 0
        ext, ctype = sniffed

        # Mirror the article pipeline: normalize big raster images to JPEG.
        payload_path, payload_ext, payload_ctype = path, ext, ctype
        tmp2 = None
        if ext in ("jpg", "png", "webp", "avif"):
            jpeg = _compress_to_jpeg(data)
            if jpeg:
                fd, tmp2 = tempfile.mkstemp(prefix="evrehost-j-", suffix=".jpg")
                with os.fdopen(fd, "wb") as f:
                    f.write(jpeg)
                payload_path, payload_ext, payload_ctype = tmp2, "jpg", "image/jpeg"

        digest = hashlib.sha256(image_url.encode("utf-8")).hexdigest()[:32]
        object_name = f"{PREFIX}/{digest}.{payload_ext}"
        nbytes = os.path.getsize(payload_path)
        ok, detail = _upload(payload_path, object_name, payload_ctype)
        if tmp2:
            try:
                os.unlink(tmp2)
            except Exception:
                pass
        if not ok:
            return image_url, "kept", f"upload:{detail}", 0
        our_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{object_name}"
        with _cache_lock:
            cache[image_url] = our_url
            _save_cache()
        return our_url, "uploaded", "", nbytes
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


if __name__ == "__main__":
    # Smoke test: python3 event_image_rehost.py <image-url>
    if len(sys.argv) > 1:
        print(rehost_image(sys.argv[1], "smoke-test"))
    else:
        print("usage: event_image_rehost.py <image-url>")
