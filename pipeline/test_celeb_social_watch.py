#!/usr/bin/env python3
"""Network-free tests for celeb_social_watch.py.

Covers: whitelist loading, the ad/collab caption filter, scontent
URL grouping + largest-variant selection from an embed page, and
queue-caption composition (credit + hashtag cap + FB post URL).

Run: python3 -m pytest pipeline/test_celeb_social_watch.py
 or: python3 pipeline/test_celeb_social_watch.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import celeb_social_watch as cw  # noqa: E402


# ── whitelist loading ─────────────────────────────────────────────
def test_whitelist_loads_with_ranbir_disabled():
    entries = cw.load_whitelist()
    assert len(entries) == 15
    by_name = {e["name"]: e for e in entries}
    ranbir = by_name["Ranbir Kapoor"]
    assert ranbir["enabled"] is False
    assert ranbir["handle"] == ""
    assert "fan" in ranbir["note"].lower()
    enabled = cw.enabled_entries(entries)
    assert len(enabled) == 14
    assert all(e["handle"] for e in enabled)


def test_whitelist_handles_match_the_verified_set():
    by_name = {e["name"]: e["handle"]
               for e in cw.enabled_entries(cw.load_whitelist())}
    assert by_name["Vijay Deverakonda"] == "thedeverakonda"
    assert by_name["Shah Rukh Khan"] == "iamsrk"
    assert by_name["Sai Pallavi"] == "saipallavi.senthamarai"
    assert by_name["A. R. Rahman"] == "arrahman"


# ── ad / collab filter ────────────────────────────────────────────
def test_ad_filter_catches_markers():
    assert cw.ad_marker_in("New drop! #ad") == "#ad"
    assert cw.ad_marker_in("Paid partnership with BrandX")
    assert cw.ad_marker_in("In collaboration with @brand") \
        == "in collaboration with"
    assert cw.ad_marker_in("Use code DIWALI20 for 20% off today") \
        == "use code"
    assert cw.ad_marker_in("Shop now at the link in bio") == "shop now"
    assert cw.ad_marker_in("#Sponsored post") == "#sponsored"
    assert cw.ad_marker_in("My new #collab collection") == "#collab"


def test_ad_filter_passes_personal_updates():
    caption = ("When you find a way to do GOMA (Homam) in Japan on "
               "Happy DIWALI ❤️ Sending you all lots of love")
    assert cw.ad_marker_in(caption) is None
    assert cw.ad_marker_in("") is None
    assert cw.ad_marker_in(None) is None
    assert cw.ad_marker_in("Happy birthday to my dearest friend") \
        is None


# ── scontent grouping / largest variant ───────────────────────────
SAMPLE_EMBED_HTML = """
<html><body>
<img src="https://scontent.cdninstagram.com/v/t51.82787-15/111_aaa_n.jpg?stp=dst-jpg_e35_s640x640&amp;foo=1">
<img src="https://scontent.cdninstagram.com/v/t51.82787-15/111_aaa_n.jpg?stp=dst-jpg_e35_s1080x1080&amp;foo=2">
<img src="https://scontent.cdninstagram.com/v/t51.82787-15/222_bbb_n.jpg?stp=dst-jpg_e35_s1080x1350">
<img src="https://scontent.cdninstagram.com/v/t51.82787-15/222_bbb_n.jpg?stp=dst-jpg_e35_s320x400">
<img src="https://static.cdninstagram.com/rsrc.php/yr/r/icon.webp">
</body></html>
"""


def test_extract_groups_by_stem_and_picks_largest():
    photos = cw.extract_scontent_photos(SAMPLE_EMBED_HTML)
    assert [p["stem"] for p in photos] == ["111_aaa", "222_bbb"]
    assert (photos[0]["width"], photos[0]["height"]) == (1080, 1080)
    assert (photos[1]["width"], photos[1]["height"]) == (1080, 1350)


def test_extract_empty_when_page_has_no_media():
    assert cw.extract_scontent_photos("<html><title>Instagram"
                                      "</title>login</html>") == []
    assert cw.extract_scontent_photos("") == []


def test_feed_post_filter_excludes_stories():
    assert cw.is_feed_post({"url": VIJAY_URL}) is True
    assert cw.is_feed_post(
        {"url": "https://www.instagram.com/reel/DfMMAaOpl6E/"}) is True
    assert cw.is_feed_post(
        {"url": "https://www.instagram.com/stories/highlights/"
                "17949556117453526/?story_media_id=2635"}) is False
    assert cw.is_feed_post({"url": None}) is False


def test_shortcode_from_url():
    assert cw.shortcode_from_url(
        "https://www.instagram.com/p/Dfe2WJqn9ak/") == "Dfe2WJqn9ak"
    assert cw.shortcode_from_url(
        "https://www.instagram.com/reel/AbC123/") == "AbC123"
    assert cw.shortcode_from_url("https://example.com/x") is None
    assert cw.shortcode_from_url(None) is None


# ── caption / credit composition ──────────────────────────────────
VIJAY_CAPTION = ("When you find a way to do GOMA (Homam) in Japan on "
                 "Happy DIWALI ❤️\n\nSending you all lots of love, "
                 "biggest hugs and Diwali wishes to you and all your "
                 "family from the Deverakonda family ❤️")
VIJAY_URL = "https://www.instagram.com/p/Dfe2WJqn9ak/"


def test_headline_comes_from_caption_not_invented():
    h = cw.derive_headline("Vijay Deverakonda", VIJAY_CAPTION)
    assert "GOMA (Homam) in Japan" in h
    assert "❤" not in h


def test_headline_fallback_is_plain_and_factual():
    assert cw.derive_headline("A. R. Rahman", "") \
        == "A. R. Rahman shares a new post"


def test_caption_carries_credit_everywhere():
    for channel in ("facebook", "threads", "instagram"):
        text = cw.compose_caption("Vijay Deverakonda",
                                  "thedeverakonda", VIJAY_CAPTION,
                                  VIJAY_URL, channel)
        assert "📸 @thedeverakonda" in text
        tags = [t for t in text.split() if t.startswith("#")]
        assert 0 < len(tags) <= 4
    fb = cw.compose_caption("Vijay Deverakonda", "thedeverakonda",
                            VIJAY_CAPTION, VIJAY_URL, "facebook")
    assert VIJAY_URL in fb
    th = cw.compose_caption("Vijay Deverakonda", "thedeverakonda",
                            VIJAY_CAPTION, VIJAY_URL, "threads")
    assert len(th) <= cw.THREADS_TEXT_LIMIT


def test_hashtags_capped_at_four():
    tags = cw.hashtags_for(
        "Deepika Padukone",
        "diwali birthday trailer wedding song festival movie film")
    assert len(tags) <= 4
    assert tags[0] == "#DeepikaPadukone"
    assert "#TheVideshi" in tags


def test_excerpt_strips_hashtags_and_emoji():
    ex = cw.caption_excerpt("Happy DIWALI ❤️ #Diwali #Family\n\n"
                            "Second para")
    assert "#" not in ex
    assert "Happy DIWALI" in ex


def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
