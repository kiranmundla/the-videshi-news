#!/usr/bin/env python3
"""
test_image_sourcer_hero_hosts.py — regression tests for the
aggregator/social-graphic host rejection in image_sourcer's
og:image guard (2026-11-14).

Live failure: the U19 Asia Cup final article shipped with a
media.inshorts.com graphic of the PM's X post as its hero —
a screenshot-style composite ABOUT a social post, containing
no cricket, hotlinked from an aggregator CDN. Aggregator
graphics and social-post graphics are never heroes: the host
itself rejects, whatever the filename looks like.

Run: python3 test_image_sourcer_hero_hosts.py   (exit 0 = all pass)
"""
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
S = SourceFileLoader(
    "image_sourcer",
    str(Path(__file__).resolve().parent / "image_sourcer.py"),
).load_module()

FAILS = []


def check(name, cond, extra=""):
    print(("  ✓ " if cond else "  ✗ ") + name
          + (f" — {extra}" if extra and not cond else ""))
    if not cond:
        FAILS.append(name)


print("_is_generic_og_image — aggregator hosts rejected")
check("the live U19 failure URL is rejected",
      S._is_generic_og_image(
          "https://media.inshorts.com/inshorts/images/v1/variants/png/l/"
          "2026/11_nov/14_sat/img_1794666059547_187.png") is True)
check("bare inshorts.com host rejected",
      S._is_generic_og_image(
          "https://inshorts.com/images/hero-photo.jpg") is True)
check("any inshorts subdomain rejected",
      S._is_generic_og_image(
          "https://cdn.images.inshorts.com/photos/match.jpg") is True)
check("lookalike host NOT rejected by the aggregator rule",
      S._is_generic_og_image(
          "https://notinshorts.com/photos/cricket-final-celebration.jpg")
      is False)
check("normal news CDN photo still allowed",
      S._is_generic_og_image(
          "https://www.espncricinfo.com/media/india-u19-celebration.jpg")
      is False)

print("_is_generic_og_image — pre-existing behaviour unchanged")
check("root-level og.jpg still generic",
      S._is_generic_og_image("https://example.com/og.jpg") is True)
check("empty URL still generic",
      S._is_generic_og_image("") is True)
check("ordinary article photo still allowed",
      S._is_generic_og_image(
          "https://images.example.com/2026/11/stadium-floodlights.jpg")
      is False)

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
