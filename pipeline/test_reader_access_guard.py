#!/usr/bin/env python3
"""
test_reader_access_guard.py — regression battery for the
2026-11-11 reader-access guard in image_sourcer.verify_image_url.

The disease: hotlink-protected CDNs (img.indiaforums.com) serve
images to the pipeline's direct fetch (bot UA, no Referer), so
verification passed, but 403 every reader whose browser sends
Referer: thevideshi.com — the Hina Khan / Rajan Shahi article
rendered the navy placeholder under a caption describing the
photo. verify_image_url now also probes the URL the way a
reader's browser fetches it (browser UA + site Referer) and
rejects on a proven 401/403. The probe fails open on every
other outcome and never runs for known-open CDNs (Wikimedia,
our storage, Pexels, YouTube thumbs, Flickr).

All network is stubbed. Run:
  python3 test_reader_access_guard.py  (exit 0 = all pass)
"""
import importlib.util
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location(
    "image_sourcer", HERE / "image_sourcer.py")
iso = importlib.util.module_from_spec(spec)
spec.loader.exec_module(iso)

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


# A real 900x600 PNG (>1000 bytes, clears the 800px hero floor).
from PIL import Image
_buf = io.BytesIO()
Image.new("RGB", (900, 600), (17, 34, 68)).save(_buf, format="PNG")
IMG_BYTES = _buf.getvalue()
assert len(IMG_BYTES) > 1000

STATE = {"probe_code": "200", "probe_exc": None, "probe_calls": []}


class _Result:
    def __init__(self, stdout, returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def fake_run(cmd, capture_output=False, text=False, timeout=None, **kw):
    # The reader probe is the only call carrying a Referer flag.
    if "-e" in cmd:
        STATE["probe_calls"].append(cmd[-1])
        if STATE["probe_exc"] is not None:
            raise STATE["probe_exc"]
        return _Result(STATE["probe_code"])
    # Main verification fetch: hand back real image bytes.
    return _Result(IMG_BYTES)


iso.subprocess.run = fake_run

THIRD_PARTY = "https://img.example-news.com/article/1280x720/photo.webp"
WIKIMEDIA = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Person.jpg"


def reset(code="200", exc=None):
    STATE["probe_code"] = code
    STATE["probe_exc"] = exc
    STATE["probe_calls"] = []


# 1. Proven hotlink protection (403 under reader conditions) rejects.
reset("403")
ok, _, _ = iso.verify_image_url(THIRD_PARTY)
check("403 under browser UA + site referer -> rejected", ok is False)

# 2. 401 also rejects.
reset("401")
ok, _, _ = iso.verify_image_url(THIRD_PARTY)
check("401 under reader conditions -> rejected", ok is False)

# 3. Reader fetch succeeds (200 / 206 range) -> image accepted.
for code in ("200", "206"):
    reset(code)
    ok, ct, w = iso.verify_image_url(THIRD_PARTY)
    check(f"reader probe {code} -> accepted",
          ok is True and w == 900)

# 4. Probe errors fail OPEN (never kill a proven-good image).
reset(exc=TimeoutError("probe timed out"))
ok, _, _ = iso.verify_image_url(THIRD_PARTY)
check("probe exception -> accepted (fail open)", ok is True)

# 5. A 404 probe is not a hotlink signal -> fail open (the main
#    fetch already proved the bytes; contradictory statuses are
#    the CDN's range quirk, not reader blocking).
reset("404")
ok, _, _ = iso.verify_image_url(THIRD_PARTY)
check("probe 404 -> accepted (fail open)", ok is True)

# 6. Exempt hosts skip the probe entirely.
reset("403")
ok, _, _ = iso.verify_image_url(WIKIMEDIA)
check("wikimedia exempt -> accepted despite probe 403",
      ok is True and STATE["probe_calls"] == [])

# 7. Helper unit behaviour.
reset("403")
check("_reader_access_blocked true on 403",
      iso._reader_access_blocked(THIRD_PARTY) is True)
check("_reader_access_blocked false for exempt host",
      iso._reader_access_blocked(WIKIMEDIA) is False)
check("_reader_access_blocked false on garbage URL",
      iso._reader_access_blocked("not a url") is False)
reset("301")
check("_reader_access_blocked false on 301 (fail open)",
      iso._reader_access_blocked(THIRD_PARTY) is False)

print()
if FAILS:
    print(f"FAIL: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("PASS: all reader-access guard checks green")
