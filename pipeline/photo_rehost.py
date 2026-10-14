#!/usr/bin/env python3
"""Re-host Google Places photos into our own Supabase storage at ingest.

WHY (2026-10-14, Kiran's screenshots): directory listings stored LIVE Google
photo URLs — legacy `maps.googleapis.com/maps/api/place/photo?photo_reference=…`
and v1 `places.googleapis.com/v1/…/media?key=…`. Stale references do not 404:
Google answers with a 100x100 "map with a red X" placeholder PNG, which
browsers render as if it were the business's photo. Listing covers resolve as
`image_url || photos[0]`, so thousands of listings (doctors, dentists, a
Hayward temple gallery) showed the red-X graphic while neighbours with
re-hosted covers looked fine.

RULE: a live googleapis photo URL is never a durable reference. At ingest,
download the bytes, validate them (real image, NOT Google's placeholder),
upload to the `directory-photos` bucket, and store only our own URL. If a
download fails validation or the daily Places budget is exhausted, the photo
is dropped (field stays NULL) — no photo beats a placeholder photo.

Placeholder signature (measured 2026-10-14 from stale references of Vijay's
Sherawali Temple, Hayward): 4,038-byte PNG, 100x100,
md5 3c4c46dac4b154446d054d8016438e7e — byte-identical for every stale ref.

Budget: every photo download is a Places API call. When use_budget=True this
module checks/records through places_budget (shared 90/day total + the
caller's per-consumer cap when the caller registered one via set_consumer).
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BUCKET = "directory-photos"
PLACEHOLDER_MD5 = "3c4c46dac4b154446d054d8016438e7e"
PLACEHOLDER_SIZE = 4038

_MAGIC = (
    (b"\xff\xd8\xff", "jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "png", "image/png"),
    (b"GIF87a", "gif", "image/gif"),
    (b"GIF89a", "gif", "image/gif"),
)


def _sniff(data):
    """Return (ext, content_type) from magic bytes, or (None, None)."""
    for magic, ext, ctype in _MAGIC:
        if data.startswith(magic):
            return ext, ctype
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp", "image/webp"
    return None, None


def is_placeholder_bytes(data):
    """True if these bytes are Google's stale-reference placeholder graphic."""
    if not data:
        return False
    if hashlib.md5(data).hexdigest() == PLACEHOLDER_MD5:
        return True
    # Fallback signature: same byte size + PNG + 100x100 (a legit 800px-wide
    # PNG of similar size must NOT match — dimensions decide when PIL exists).
    if len(data) == PLACEHOLDER_SIZE and data.startswith(b"\x89PNG"):
        try:
            from PIL import Image
            import io
            with Image.open(io.BytesIO(data)) as im:
                return im.size == (100, 100)
        except Exception:
            return True
    return False


def validate_photo_bytes(data):
    """True if `data` is a real photo we may store — never the placeholder.

    Layers: exact placeholder signature, real-image magic bytes, a sanity
    size floor, and (when PIL is available) a dimension floor — the
    placeholder is 100x100; real Places photos at maxWidthPx=800 are far
    larger in at least one dimension (a known-legit 800x326 banner passes).
    """
    if not data or is_placeholder_bytes(data):
        return False
    ext, _ = _sniff(data)
    if ext is None:
        return False
    if len(data) < 1500:
        return False
    try:
        from PIL import Image
        import io
        with Image.open(io.BytesIO(data)) as im:
            w, h = im.size
        if max(w, h) < 300 or (w == 100 and h == 100):
            return False
    except Exception:
        pass  # PIL unavailable/broken: magic + signature + size checks stand
    return True


def _curl_bytes(url, headers=None, timeout=30):
    """GET url via curl (proxy-safe), return (bytes|None, content_type|None)."""
    fd, tmp = tempfile.mkstemp(prefix="photo_rehost_")
    os.close(fd)
    try:
        cmd = ["curl", "-sS", "-L", "--max-time", str(timeout), "-o", tmp,
               "-w", "%{http_code} %{content_type}", url]
        for k, v in (headers or {}).items():
            cmd += ["-H", f"{k}: {v}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        parts = (r.stdout or "").split(" ", 1)
        code = parts[0] if parts else ""
        ctype = parts[1].strip() if len(parts) > 1 else None
        if code != "200":
            return None, None
        with open(tmp, "rb") as f:
            data = f.read()
        return (data or None), ctype
    except Exception:
        return None, None
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def download_v1_photo(photo_name, api_key, max_width=800):
    """Download a Places API (New) photo by resource name. 1 Places call.

    Returns (bytes, content_type) or (None, None)."""
    url = (f"https://places.googleapis.com/v1/{photo_name}/media"
           f"?maxWidthPx={max_width}&skipHttpRedirect=true")
    data, _ = _curl_bytes(url, headers={"X-Goog-Api-Key": api_key})
    if not data:
        return None, None
    try:
        photo_uri = json.loads(data).get("photoUri")
    except Exception:
        return None, None
    if not photo_uri:
        return None, None
    return _curl_bytes(photo_uri)


def upload_to_bucket(path, data, content_type):
    """Upload bytes to the directory-photos bucket; return public URL or None."""
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not supabase_key:
        return None
    url = f"{supabase_url}/storage/v1/object/{BUCKET}/{path}"
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "30", "-X", "POST", "--data-binary", "@-",
         "-H", f"apikey: {supabase_key}",
         "-H", f"Authorization: Bearer {supabase_key}",
         "-H", f"Content-Type: {content_type}",
         "-H", "x-upsert: true",
         "-w", "\n%{http_code}", url],
        input=data, capture_output=True)
    code = (r.stdout or b"").rsplit(b"\n", 1)[-1].decode(errors="ignore").strip()
    if code in ("200", "201"):
        return f"{supabase_url}/storage/v1/object/public/{BUCKET}/{path}"
    return None


def _budget_ok():
    try:
        from places_budget import check_budget
        return check_budget()
    except Exception:
        return True  # budget module unavailable: don't block ingest on it


def _budget_record():
    try:
        from places_budget import record_call
        record_call()
    except Exception:
        pass


def _store_validated(data, stem, idx):
    """Validate downloaded bytes and upload; return our public URL or None."""
    if not validate_photo_bytes(data):
        return None
    ext, ctype = _sniff(data)
    return upload_to_bucket(f"{stem}__{idx}.{ext}", data, ctype)


def rehost_v1_photos(photos, stem, api_key, max_photos=5, use_budget=True):
    """Re-host Places (New) photo dicts ([{'name': 'places/…/photos/…'}]).

    Returns a list of our storage URLs (possibly empty, possibly shorter than
    the input — failed/placeholder/budget-blocked photos are dropped, never
    stored as live Google URLs)."""
    out = []
    for p in (photos or [])[:max_photos]:
        name = (p or {}).get("name")
        if not name:
            continue
        if use_budget and not _budget_ok():
            break
        data, _ = download_v1_photo(name, api_key)
        if use_budget:
            _budget_record()
        if not data:
            continue
        url = _store_validated(data, stem, len(out))
        if url:
            out.append(url)
    return out


def rehost_raw_urls(urls, stem, max_photos=5, use_budget=True):
    """Re-host already-built photo URLs (legacy photo_reference URLs).

    Same contract as rehost_v1_photos: only our durable URLs come back;
    anything that fails validation is dropped."""
    out = []
    for u in (urls or [])[:max_photos]:
        if not u:
            continue
        if use_budget and not _budget_ok():
            break
        data, _ = _curl_bytes(u)
        if use_budget:
            _budget_record()
        if not data:
            continue
        url = _store_validated(data, stem, len(out))
        if url:
            out.append(url)
    return out
