#!/usr/bin/env python3
"""
test_source_image_guards.py — regression battery for the
2026-11-11 manual-route guards in source-image.py.

The disease: the manual scribe route applied NEITHER of the
automated pipeline's Commons guards — its Wikipedia path had
no resolution floor (it tried 335×410 and 308×402 portraits
as heroes) and its Commons keyword search had no relevance
guard (it placed a 1904 Harper's magazine scan on the UBC
article). Both routes now fail closed: ≥800px long side, and
Commons hits must pass image_sourcer.commons_relevance_ok.

All network is stubbed. Run:
  python3 test_source_image_guards.py  (exit 0 = all pass)
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

spec = importlib.util.spec_from_file_location(
    "source_image", HERE / "source-image.py")
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


class Resp:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


STATE = {"summary": None, "search_pages": None, "sizes": {}}


def fake_get(url, params=None, headers=None, timeout=None):
    params = params or {}
    if "page/summary/" in url:
        return Resp(STATE["summary"] or {})
    if "commons.wikimedia.org" in url:
        if params.get("generator") == "search":
            return Resp({"query": {"pages": STATE["search_pages"]
                                   or {}}})
        title = (params.get("titles") or "").removeprefix("File:")
        wh = STATE["sizes"].get(title)
        if wh:
            return Resp({"query": {"pages": {"1": {
                "title": f"File:{title}",
                "imageinfo": [{"width": wh[0],
                               "height": wh[1]}]}}}})
        return Resp({"query": {"pages": {}}})
    raise AssertionError(f"unexpected URL in stub: {url}")


_orig_get = si.requests.get
si.requests.get = fake_get

try:
    # ── Wikipedia floor ────────────────────────────────────
    print("Wikipedia path — ≥800px long-side floor")
    STATE["summary"] = {"originalimage": {
        "source": "https://upload.wikimedia.org/wikipedia/"
                  "commons/a/ab/Small_Portrait.jpg",
        "width": 335, "height": 410}}
    url, _attr = si.fetch_wikipedia("Some Person")
    check("a 335×410 Wikipedia portrait is rejected",
          url is None, str(url))

    STATE["summary"] = {"originalimage": {
        "source": "https://upload.wikimedia.org/wikipedia/"
                  "commons/c/cd/Big_Portrait.jpg",
        "width": 2400, "height": 1600}}
    url, _attr = si.fetch_wikipedia("Some Person")
    check("a 2400×1600 Wikipedia image still returns",
          url is not None and "Big_Portrait" in url, str(url))

    STATE["summary"] = {"originalimage": {
        "source": "https://upload.wikimedia.org/wikipedia/"
                  "commons/e/ef/NoDims.jpg"}}
    STATE["sizes"] = {"NoDims.jpg": (308, 402)}
    url, _attr = si.fetch_wikipedia("Some Person")
    check("dims absent from the summary are verified via "
          "Commons and a 308×402 is rejected",
          url is None, str(url))
    STATE["sizes"] = {}

    STATE["summary"] = {"originalimage": {
        "source": "https://upload.wikimedia.org/wikipedia/"
                  "commons/e/ef/NoDims.jpg"}}
    url, _attr = si.fetch_wikipedia("Some Person")
    check("an unverifiable size fails closed",
          url is None, str(url))

    # ── Commons relevance guard + floor ────────────────────
    print("Commons path — relevance guard + floor")
    HEADLINE = ("UBC Okanagan Campus Expansion Wins "
                "Provincial Funding")
    QUERY = "University of British Columbia Okanagan"
    STATE["search_pages"] = {
        "11": {"title": "File:Harper's magazine cover, "
                        "1904.jpg", "index": 1,
               "imageinfo": [{"mime": "image/jpeg",
                              "width": 2000, "height": 2600,
                              "url": "https://upload.wikimedia."
                                     "org/harpers.jpg",
                              "thumburl": "https://upload."
                                          "wikimedia.org/"
                                          "harpers-t.jpg"}]},
        "12": {"title": "File:UBC Okanagan campus aerial "
                        "view 2023.jpg", "index": 2,
               "imageinfo": [{"mime": "image/jpeg",
                              "width": 2400, "height": 1600,
                              "url": "https://upload.wikimedia."
                                     "org/ubc.jpg",
                              "thumburl": "https://upload."
                                          "wikimedia.org/"
                                          "ubc-t.jpg"}]},
    }
    url, _attr = si.fetch_commons(QUERY, HEADLINE)
    check("the Harper's-scan pattern (no headline overlap) "
          "is skipped and the relevant hit is returned",
          url is not None and "ubc" in url.lower(), str(url))

    STATE["search_pages"] = {
        "11": {"title": "File:Harper's magazine cover, "
                        "1904.jpg", "index": 1,
               "imageinfo": [{"mime": "image/jpeg",
                              "width": 2000, "height": 2600,
                              "url": "https://upload.wikimedia."
                                     "org/harpers.jpg",
                              "thumburl": "https://upload."
                                          "wikimedia.org/"
                                          "harpers-t.jpg"}]},
    }
    url, _attr = si.fetch_commons(QUERY, HEADLINE)
    check("with only the irrelevant hit, Commons fails "
          "closed (no image)", url is None, str(url))

    STATE["search_pages"] = {
        "13": {"title": "File:UBC Okanagan campus 2019.jpg",
               "index": 1,
               "imageinfo": [{"mime": "image/jpeg",
                              "width": 500, "height": 375,
                              "url": "https://upload.wikimedia."
                                     "org/ubc-small.jpg",
                              "thumburl": "https://upload."
                                          "wikimedia.org/"
                                          "ubc-small-t.jpg"}]},
    }
    url, _attr = si.fetch_commons(QUERY, HEADLINE)
    check("a relevant but sub-800 Commons hit fails closed",
          url is None, str(url))
finally:
    si.requests.get = _orig_get

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
