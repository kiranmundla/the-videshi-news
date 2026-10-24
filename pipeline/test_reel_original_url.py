#!/usr/bin/env python3
"""Tests for reel_produce.original_url — render-time original fetcher.

Kiran's resolution pick (2026-10-24): article heroes stay at the 1920
article rung; reels fetch originals at render time (pipeline-side
download, zero reader cost). Run: python3 -u test_reel_original_url.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "reel_produce", os.path.join(HERE, "reel_produce.py"))
rp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp)

PASSED, FAILED = [], []


def check(name, got, want):
    (PASSED if got == want else FAILED).append(name)
    print(f"  {'PASS' if got == want else 'FAIL'} {name}: "
          f"got {str(got)[:110]!r}, want {str(want)[:110]!r}")


ou = rp.original_url

CAP_THUMB = ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/"
             "Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg")
CAP_ORIG = ("https://upload.wikimedia.org/wikipedia/commons/1/1a/"
            "Capitol_at_Dusk_2.jpg")
check("wikimedia thumb 1280 -> original", ou(CAP_THUMB), CAP_ORIG)
check("wikimedia thumb 1920 -> original",
      ou(CAP_THUMB.replace("1280px", "1920px")), CAP_ORIG)
check("wikimedia original untouched", ou(CAP_ORIG), CAP_ORIG)

# The Commons API's real shape (measured 2026-10-24): thumbs come from
# thumb.wikimedia.org with utm tracking params appended.
API_THUMB = ("https://thumb.wikimedia.org/wikipedia/commons/thumb/6/64/"
             "Capitol_at_Dusk_2.jpg/1920px-Capitol_at_Dusk_2.jpg"
             "?utm_source=commons.wikimedia.org&utm_campaign=imageinfo"
             "&utm_content=thumbnail")
API_ORIG = ("https://upload.wikimedia.org/wikipedia/commons/6/64/"
            "Capitol_at_Dusk_2.jpg")
check("API thumb.wikimedia.org + utm -> clean original",
      ou(API_THUMB), API_ORIG)

TIF_THUMB = ("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/"
             "Old_map.tif/1280px-Old_map.tif.jpg")
check("tif thumb not upgraded (renderer needs raster)",
      ou(TIF_THUMB), TIF_THUMB)
SVG_THUMB = ("https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/"
             "Diagram.svg/1280px-Diagram.svg.png")
check("svg thumb not upgraded", ou(SVG_THUMB), SVG_THUMB)

SFP = ("https://commons.wikimedia.org/wiki/Special:FilePath/"
       "Capitol_at_Dusk_2.jpg?width=1280")
check("Special:FilePath width dropped",
      ou(SFP), "https://commons.wikimedia.org/wiki/Special:FilePath/"
               "Capitol_at_Dusk_2.jpg")
check("Special:FilePath without width untouched",
      ou(SFP.split("?")[0]), SFP.split("?")[0])

NASA = ("https://images-assets.nasa.gov/image/GSFC_20171208_Archive_e001982/"
        "GSFC_20171208_Archive_e001982~large.jpg")
check("NASA ~large -> ~orig", ou(NASA), NASA.replace("~large.", "~orig."))
BLOG_LARGE = "https://example.com/images/photo~large.jpg"
check("non-NASA ~large untouched", ou(BLOG_LARGE), BLOG_LARGE)

PEX = ("https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg"
       "?auto=compress&cs=tinysrgb&w=1880&h=1058&dpr=1")
check("Pexels size params dropped",
      ou(PEX), "https://images.pexels.com/photos/12345/"
               "pexels-photo-12345.jpeg?auto=compress&cs=tinysrgb")
check("Pexels without params untouched",
      ou("https://images.pexels.com/photos/1/x.jpeg"),
      "https://images.pexels.com/photos/1/x.jpeg")

OG = "https://cdn.example.com/sites/default/files/hero-1200x630.jpg"
check("publisher og:image untouched", ou(OG), OG)
check("empty/garbage untouched", ou("not a url"), "not a url")

print()
if FAILED:
    print(f"FAILURES: {len(FAILED)} -> {FAILED}")
    sys.exit(1)
print(f"ALL PASS ({len(PASSED)} checks)")
