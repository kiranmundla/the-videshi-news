#!/usr/bin/env python3
"""Tests for reel-distribute-social.py's ig_reel_caption.

Kiran, 2026-10-25: article links go wherever allowed and free.
The Instagram reel caption must carry the full article URL as a
'Full story: <url>' line immediately before the hashtag block.
The stored reel caption is the YouTube description, whose
'Read the full story:' line sits mid-text — the IG form
normalises and repositions it."""
import importlib.util
import os
import sys

os.environ.setdefault("SUPABASE_URL", "https://example.invalid")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_spec = importlib.util.spec_from_file_location(
    "reel_distribute_social",
    os.path.join(_HERE, "reel-distribute-social.py"))
rds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rds)

SLUG = "romanchs-law-new-york-horse-carriage-ban-indian-teen"
STORY = f"Full story: https://thevideshi.com/articles/{SLUG}"

PASSED = 0
FAILED = 0


def check(name, fn):
    global PASSED, FAILED
    try:
        fn()
    except Exception as e:  # noqa: BLE001
        FAILED += 1
        print(f"FAIL: {name}: {e}")
    else:
        PASSED += 1
        print(f"PASS: {name}")


def t_youtube_description_line_normalised_and_moved():
    caption = (
        "New York bans horse-drawn carriages under Romanch's Law.\n\n"
        "The Council voted 40 to 7.\n\n"
        "Read the full story: "
        "https://www.thevideshi.com/articles/" + SLUG + "\n\n"
        "#Shorts #RomanchsLaw #TheVideshi #IndianDiaspora")
    out = rds.ig_reel_caption(caption, SLUG)
    assert STORY in out, out
    assert "Read the full story" not in out, out
    assert "www.thevideshi.com" not in out, out
    lines = [ln for ln in out.split("\n") if ln.strip()]
    assert lines[-2] == STORY, lines
    assert lines[-1].startswith("#Shorts"), lines
    # Body text preserved.
    assert "The Council voted 40 to 7." in out, out


def t_missing_story_line_is_inserted_before_tags():
    caption = "A headline hook.\n\nA summary line.\n\n#TheVideshi #News"
    out = rds.ig_reel_caption(caption, SLUG)
    lines = [ln for ln in out.split("\n") if ln.strip()]
    assert lines[-2] == STORY, lines
    assert lines[-1] == "#TheVideshi #News", lines


def t_no_hashtags_appends_at_end():
    out = rds.ig_reel_caption("Just a headline.", SLUG)
    assert out == f"Just a headline.\n\n{STORY}", out


def t_no_slug_returns_caption_unchanged():
    caption = "Anything.\n\n#Tag"
    assert rds.ig_reel_caption(caption, None) == caption
    assert rds.ig_reel_caption(caption, "") == caption


def t_existing_full_story_line_not_duplicated():
    caption = f"Hook.\n\n{STORY}\n\n#TheVideshi"
    out = rds.ig_reel_caption(caption, SLUG)
    assert out.count("Full story:") == 1, out


def main():
    tests = [
        ("youtube description line normalised + moved",
         t_youtube_description_line_normalised_and_moved),
        ("missing story line inserted before tags",
         t_missing_story_line_is_inserted_before_tags),
        ("no hashtags: story line appended at end",
         t_no_hashtags_appends_at_end),
        ("no slug: caption unchanged", t_no_slug_returns_caption_unchanged),
        ("existing Full story line not duplicated",
         t_existing_full_story_line_not_duplicated),
    ]
    for name, fn in tests:
        check(name, fn)
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
