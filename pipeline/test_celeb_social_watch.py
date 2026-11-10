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


# ── reel spec / scene plan (network-free) ─────────────────────────
VIJAY_CELEB = {"name": "Vijay Deverakonda",
               "handle": "thedeverakonda", "enabled": True,
               "note": ""}
VIJAY_POST = {"post_id": "17997368079023648", "url": VIJAY_URL,
              "post_caption": VIJAY_CAPTION, "media_type": "carousel"}


def test_reel_article_body_is_caption_plus_source_line():
    art = cw.build_reel_article(VIJAY_CELEB, VIJAY_POST)
    assert art["slug"] == "celeb-thedeverakonda-17997368079023648"
    assert art["body"].startswith("When you find a way to do GOMA")
    assert "Source: Vijay Deverakonda (@thedeverakonda)" \
        in art["body"]
    assert VIJAY_URL in art["body"]
    # the v7 hook kicker slot (category) carries the celeb's name
    assert art["category"] == "vijay-deverakonda"


def test_scene_plan_never_repeats_a_photo():
    for n in (1, 2, 3, 4, 6):
        plan = cw.build_scene_plan(VIJAY_CELEB, VIJAY_POST, n)
        photos = [s["source"] for s in plan
                  if s["source"].startswith("photo:")]
        assert len(photos) == len(set(photos)), (n, photos)
        assert len(photos) == min(n, 5)
        assert plan[0]["source"] == "photo:0"
        assert len(plan) == 6      # the locked 6-beat v7 arc


def test_scene_plan_ends_with_credit_closer():
    plan = cw.build_scene_plan(VIJAY_CELEB, VIJAY_POST, 1)
    last = plan[-1]
    assert last["beat"] == "payoff" and last["source"] == "credit"
    text = " ".join(last["texts"])
    assert "@thedeverakonda" in text
    assert "Dfe2WJqn9ak" in text       # the original post URL


def test_reel_texts_come_only_from_the_caption():
    caption = ("Celebrating Diwali with a small Homam in Japan "
               "this year.\n\nSending love to everyone back home "
               "and wishing you all light and happiness.")
    post = {"post_id": "42", "url": VIJAY_URL,
            "post_caption": caption, "media_type": "photo"}
    script = cw.build_reel_script(VIJAY_CELEB, post)
    import re as _re2
    allowed = set(_re2.findall(r"[a-z][a-z']+",
                               cw.clean_text(caption).lower()))
    allowed |= {"photos", "from", "instagram", "post", "https",
                "www", "com", "p", "dfe2wjqn9ak", "thedeverakonda's",
                "thedeverakonda"}
    allowed |= {w.lower() for w in VIJAY_CELEB["name"].split()}
    on_screen = [script["hook_line"], script["news_summary"],
                 script["hook_stat"]["big"],
                 script["hook_stat"]["sub"], script["payoff"]]
    for s in script["stats"]:
        on_screen += [s["big"], s["label"]]
    on_screen += script["diaspora_bullets"]
    import re as _re
    for text in on_screen:
        # URLs are verified separately (credit-closer test); strip
        # them before the word-level caption-provenance check.
        text = _re.sub(r"https?://\S+", "", text)
        for word in _re.findall(r"[A-Za-z][A-Za-z']+", text):
            assert word.lower() in allowed, (word, text)


def test_caption_sentences_split_on_lines():
    # Instagram captions separate their lines without sentence
    # punctuation; the splitter must still see two sentences.
    sents = cw.caption_sentences(VIJAY_CAPTION)
    assert len(sents) == 2
    assert sents[1].startswith("Sending you all lots of love")


def test_reel_script_has_no_invented_fallback_text():
    # Regression (first sample, held at fact-check): the builder
    # must never fall back to prose it wrote itself — every
    # string is the caption's own words or the credit template.
    script = cw.build_reel_script(VIJAY_CELEB, VIJAY_POST)
    blob = json.dumps(script)
    assert "latest update" not in blob
    assert script["hook_stat"]["sub"].startswith(
        "Sending you all lots of love")
    labels = [s["label"] for s in script["stats"]]
    assert len(labels) == len(set(labels))     # no duplicate labels
    assert {s["big"] for s in script["stats"]} == {"JAPAN", "DIWALI"}


def test_pick_music_is_festive_and_never_banned():
    pick = cw.pick_music(VIJAY_CAPTION)
    assert pick is not None and "diwali" in pick.name.lower()
    for caption in ("A quiet evening at home with family",
                    "Breaking story about markets", ""):
        pick = cw.pick_music(caption)
        assert pick is not None
        assert pick.name not in cw.BANNED_MUSIC
        assert not pick.name.lower().startswith("breaking-")


def test_celeb_tiktok_caption_shape():
    text = cw.build_celeb_tiktok_caption(VIJAY_CELEB, VIJAY_POST)
    assert "📸 @thedeverakonda" in text
    assert VIJAY_URL in text
    tags = [t for t in text.split() if t.startswith("#")]
    assert 0 < len(tags) <= 4


# ── hook face-completeness check (2026-11-09) ─────────────────────
# Regression for the Anil Kapoor birthday deck: frame 1 showed
# only a forehead (YuNet detects no face in it) and staged anyway.
# The geometry/completeness logic is pure; the detector sits
# behind an injectable wrapper so these tests are network-free
# and never depend on YuNet firing on synthetic images.
def _solid_img(w, h):
    from PIL import Image
    return Image.new("RGB", (w, h), (120, 120, 120))


def test_crop_window_backdrop_is_full_frame():
    win, track = cw.hook_crop_window(992, 992)
    assert track == "backdrop"
    assert win == (0.0, 0.0, 992.0, 992.0)


def test_crop_window_full_bleed_wide_source():
    # 2000x1600: cover window is (h*0.8, h) anchored on fx.
    win, track = cw.hook_crop_window(2000, 1600, fx=0.5, fy=0.5)
    assert track == "full-bleed"
    assert win == (360.0, 0.0, 1640.0, 1600.0)


def test_crop_window_full_bleed_tall_source():
    # 1920x2600: cover window is (w, w/0.8) anchored on fy.
    win, track = cw.hook_crop_window(1920, 2600, fx=0.5, fy=0.5)
    assert track == "full-bleed"
    assert win == (0.0, 100.0, 1920.0, 2500.0)


def test_completeness_accepts_face_fully_inside():
    ok, _reason = cw.evaluate_face_completeness(
        [(100.0, 100.0, 200.0, 200.0)], (0.0, 0.0, 992.0, 992.0))
    assert ok


def test_completeness_rejects_face_cut_by_crop_edge():
    ok, reason = cw.evaluate_face_completeness(
        [(1500.0, 100.0, 300.0, 300.0)], (360.0, 0.0, 1640.0, 1600.0))
    assert not ok and "cut" in reason


def test_completeness_rejects_when_largest_face_is_cut():
    # A small face fully inside does not rescue a cut largest face.
    ok, _reason = cw.evaluate_face_completeness(
        [(400.0, 100.0, 50.0, 50.0), (1500.0, 100.0, 300.0, 300.0)],
        (360.0, 0.0, 1640.0, 1600.0))
    assert not ok


def test_completeness_rejects_no_face_detected():
    ok, reason = cw.evaluate_face_completeness(
        [], (0.0, 0.0, 992.0, 992.0))
    assert not ok and "no face" in reason


def test_hook_face_check_stages_face_fully_inside_crop():
    ok, _reason = cw.hook_face_check(
        _solid_img(992, 992),
        detector=lambda im: ([(300.0, 200.0, 200.0, 200.0)], "fake"))
    assert ok


def test_hook_face_check_skips_face_cut_by_crop():
    # Face runs past the frame's right edge (backdrop window =
    # full frame): the rendered card would show it sliced.
    ok, reason = cw.hook_face_check(
        _solid_img(992, 992),
        detector=lambda im: ([(900.0, 200.0, 200.0, 200.0)], "fake"))
    assert not ok and "cut" in reason


def test_hook_face_check_skips_no_face():
    ok, reason = cw.hook_face_check(
        _solid_img(992, 992), detector=lambda im: ([], "fake"))
    assert not ok and "no face" in reason


def test_hook_face_check_skips_when_detector_unavailable():
    ok, reason = cw.hook_face_check(
        _solid_img(992, 992),
        detector=lambda im: (None, "boom"))
    assert not ok and "unavailable" in reason


def _stage_report():
    return {"skipped_ads": [], "skipped_face": [], "no_frames": [],
            "staged": [], "would_stage": [], "notes": []}


_STAGE_POST = {"post_id": "777",
               "url": "https://www.instagram.com/p/AbC777/",
               "post_caption": "A lovely evening with family",
               "media_type": "photo"}
_STAGE_CELEB = {"name": "Test Celeb", "handle": "testceleb",
                "enabled": True, "note": ""}


def test_stage_post_face_skip_records_reason_and_stages_nothing():
    report = _stage_report()
    orig_dl, orig_check = cw.download_frames, cw.hook_face_check
    try:
        cw.download_frames = lambda p: ([_solid_img(992, 992)], "")
        cw.hook_face_check = lambda img: (
            False, "no face detected in the hook photo [test]")
        outcome = cw.stage_post(_STAGE_CELEB, _STAGE_POST,
                                dry_run=False, report=report)
    finally:
        cw.download_frames, cw.hook_face_check = orig_dl, orig_check
    assert outcome == "face-skip"
    assert len(report["skipped_face"]) == 1
    assert "testceleb/777" in report["skipped_face"][0]
    assert report["staged"] == []


def test_stage_post_face_pass_reaches_dry_run():
    report = _stage_report()
    orig_dl, orig_check = cw.download_frames, cw.hook_face_check
    try:
        cw.download_frames = lambda p: ([_solid_img(992, 992)], "")
        cw.hook_face_check = lambda img: (True, "ok [test]")
        outcome = cw.stage_post(_STAGE_CELEB, _STAGE_POST,
                                dry_run=True, report=report)
    finally:
        cw.download_frames, cw.hook_face_check = orig_dl, orig_check
    assert outcome == "dry-run"
    assert report["would_stage"] and "testceleb/777" \
        in report["would_stage"][0]
    assert report["skipped_face"] == []


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
