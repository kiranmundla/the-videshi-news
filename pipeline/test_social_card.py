#!/usr/bin/env python3
"""Tests for social_card.py — the dual-track social-card generator
(Kiran-approved design, 2026-10-24).

Core invariants under test:
  - Track gate: fetched-original width >=1920 AND cover-crop scale
    <=1.0 -> full-bleed; anything else -> backdrop. NEVER UPSCALE in
    either track.
  - A wide-but-short hero (>=1920 wide, short height) passes the width
    gate but its centre-slice crop would upscale -> demoted to
    backdrop, with the reason recorded.
  - Backdrop places the photo at native scale (downscale or 1:1 only),
    centred when narrower than the canvas.
  - Headline fitting: long headlines shrink to fit their zone; only as
    a last resort do they truncate, and truncation is flagged.
  - Kicker category mapping (nri-world -> NRI WORLD etc.).
  - Skip rule (go-live, 2026-10-24): a best image <600px wide makes
    make_card render nothing and return track "skipped" /
    reason "hero_under_600px"; exactly 600px renders; force_track
    (--track) overrides the skip.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
if os.path.isdir(os.path.join(HERE, ".pylibs")):
    sys.path.insert(0, os.path.join(HERE, ".pylibs"))

from PIL import Image  # noqa: E402

import social_card as sc  # noqa: E402

FAILURES = []
TOTAL = [0]


def check(name, got, want):
    TOTAL[0] += 1
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'} {name}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(name)


def check_true(name, cond, detail=""):
    TOTAL[0] += 1
    print(f"  {'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAILURES.append(name)


def solid(w, h, color=(90, 120, 160)):
    return Image.new("RGB", (w, h), color)


# ── Track gate ────────────────────────────────────────────────────────
t, s, _ = sc.choose_track(2560, 1440)
check("gate: 2560x1440 -> full-bleed", t, "full-bleed")
check("gate: 2560x1440 scale = 1080/1152", round(s, 4), 0.9375)

t, s, _ = sc.choose_track(1920, 1440)
check("gate: 1920x1440 (4:3) -> full-bleed", t, "full-bleed")
check_true("gate: 1920x1440 no upscale", s <= 1.0, f"scale={s:.3f}")

t, s, _ = sc.choose_track(1280, 720)
check("gate: 1280x720 -> backdrop", t, "backdrop")
check("gate: 1280x720 backdrop scale", round(s, 4), 0.8438)

t, s, note = sc.choose_track(1920, 800)
check("gate: 1920x800 wide-short -> demoted to backdrop", t, "backdrop")
check_true("gate: demotion explains itself",
           note is not None and "upscale" in note, f"note={note!r}")
check_true("gate: demoted scale <= 1.0", s <= 1.0, f"scale={s:.3f}")

t, s, _ = sc.choose_track(1919, 1400)
check("gate: 1919 wide (1px under) -> backdrop", t, "backdrop")

# ── Backdrop fit: never upscale, height capped ────────────────────────
pw, ph, s = sc.backdrop_fit(1280, 720)
check("backdrop_fit 1280x720 placed", (pw, ph), (1080, 607))
pw, ph, s = sc.backdrop_fit(800, 600)
check("backdrop_fit 800x600 stays native", (pw, ph), (800, 600))
check("backdrop_fit 800x600 scale 1.0", s, 1.0)
pw, ph, s = sc.backdrop_fit(1080, 2000)
check_true("backdrop_fit tall photo height-capped",
           ph <= sc.MAX_PHOTO_H and s < 1.0, f"placed={pw}x{ph} scale={s:.3f}")

# ── Full-bleed scale math ─────────────────────────────────────────────
check("fb scale 2560x1440", round(sc.full_bleed_scale(2560, 1440), 4),
      0.9375)
check_true("fb scale 1920x1080 would upscale (gate must demote)",
           sc.full_bleed_scale(1920, 1080) > 1.0,
           f"{sc.full_bleed_scale(1920, 1080):.3f}")
t, _, note = sc.choose_track(1920, 1080)
check("gate: 1920x1080 -> backdrop (centre-slice upscale)", t, "backdrop")

# ── Kicker mapping ────────────────────────────────────────────────────
check("kicker nri-world", sc.kicker_for("nri-world"), "NRI WORLD")
check("kicker markets-finance", sc.kicker_for("markets-finance"),
      "MARKETS & FINANCE")
check("kicker lifestyle-health", sc.kicker_for("lifestyle-health"),
      "LIFESTYLE & HEALTH")
check("kicker technology", sc.kicker_for("technology"), "TECHNOLOGY")
check("kicker unknown falls back", sc.kicker_for("science"),
      "SCIENCE")

# ── Renders: invariants on real pixels ────────────────────────────────
import tempfile  # noqa: E402

tmp = tempfile.mkdtemp(prefix="social-card-test-")

img = solid(2560, 1440)
card, info = sc.render_full_bleed(img, "A Short Headline", "TECHNOLOGY",
                                  anchor=(0.5, 0.5, "test"))
check("full-bleed canvas", card.size, (1080, 1350))
check_true("full-bleed render scale <= 1.0",
           info["render_scale"] <= 1.0, f"{info['render_scale']}")
check("full-bleed short headline not truncated", info["truncated"], False)

img = solid(1280, 720)
card, info = sc.render_backdrop(img, "A Short Headline", "TECHNOLOGY")
check("backdrop canvas", card.size, (1080, 1350))
check("backdrop photo placed at fit width", info["photo_px"], [1080, 607])
check("backdrop render scale", info["render_scale"], 0.8438)

img = solid(800, 600)
card, info = sc.render_backdrop(img, "Narrow Photo Headline", "NEWS")
check("backdrop narrow photo unscaled", info["photo_px"], [800, 600])
check("backdrop narrow photo centred on stage",
      card.getpixel((10, 10)), sc.NAVY)
check("backdrop narrow photo present at centre",
      card.getpixel((540, 300)), (90, 120, 160))

# ── Text fitting ──────────────────────────────────────────────────────
from PIL import ImageDraw  # noqa: E402

probe = ImageDraw.Draw(Image.new("RGB", (1080, 1350)))
LONG = ("India and the United States Announce a Sweeping New Trade and "
        "Technology Partnership Covering Semiconductors, Defence, Space "
        "and Critical Minerals Supply Chains")
font, lines, size, trunc = sc.fit_headline(probe, LONG, sc.CW, 6, start=60)
check_true("long headline fits 6 lines untruncated",
           len(lines) <= 6 and not trunc,
           f"size={size} lines={len(lines)}")
font, lines, size, trunc = sc.fit_headline(probe, LONG, sc.CW, 4, start=60)
check_true("long headline fits 4 lines by shrinking",
           len(lines) <= 4 and not trunc and size < 60,
           f"size={size} lines={len(lines)}")

font, lines, size, trunc = sc.fit_headline(probe, LONG * 3, sc.CW, 3,
                                           start=60)
check("absurd headline truncates with flag", trunc, True)
check_true("truncated headline ends with ellipsis",
           lines[-1].endswith("…"), f"last={lines[-1]!r}")
check_true("truncated lines within width",
           all(probe.textlength(ln, font=font) <= sc.CW for ln in lines))

# Backdrop: very tall photo leaves a small zone — headline must fit it
img = solid(1080, 2000)
card, info = sc.render_backdrop(img, LONG, "TECHNOLOGY")
check_true("backdrop tall-photo headline fits zone",
           info["headline_lines"] >= 1, f"info={info}")

# ── End-to-end via make_card on a local file ──────────────────────────
p = os.path.join(tmp, "hero.jpg")
solid(2560, 1440).save(p, "JPEG")
out = os.path.join(tmp, "card.png")
info = sc.make_card("End to End Headline Test", "nri-world",
                    image_path=p, out_path=out)
check("e2e track", info["track"], "full-bleed")
check("e2e source_px", info["source_px"], [2560, 1440])
check("e2e kicker", info["kicker"], "NRI WORLD")
check_true("e2e output written", os.path.exists(out))

p2 = os.path.join(tmp, "hero2.jpg")
solid(1200, 900).save(p2, "JPEG")
info = sc.make_card("End to End Backdrop Test", "sports",
                    image_path=p2, out_path=os.path.join(tmp, "c2.png"))
check("e2e backdrop track", info["track"], "backdrop")
check("e2e backdrop no upscale", info["render_scale"], 0.9)

# ── Skip rule: best image <600px wide renders NOTHING ────────────────
p3 = os.path.join(tmp, "hero-small.jpg")
solid(480, 360).save(p3, "JPEG")
out3 = os.path.join(tmp, "card-small.png")
info = sc.make_card("Tiny Hero Should Skip", "entertainment",
                    image_path=p3, out_path=out3)
check("skip: 480px track", info["track"], "skipped")
check("skip: reason", info["reason"], "hero_under_600px")
check("skip: source_px", info["source_px"], [480, 360])
check_true("skip: nothing rendered", not os.path.exists(out3))

p4 = os.path.join(tmp, "hero-599.jpg")
solid(599, 400).save(p4, "JPEG")
info = sc.make_card("One Pixel Under Still Skips", "news",
                    image_path=p4, out_path=os.path.join(tmp, "c599.png"))
check("skip: 599px still skips", info["track"], "skipped")

p5 = os.path.join(tmp, "hero-600.jpg")
solid(600, 450).save(p5, "JPEG")
out5 = os.path.join(tmp, "c600.png")
info = sc.make_card("Exactly Six Hundred Renders", "news",
                    image_path=p5, out_path=out5)
check("skip: 600px renders (backdrop)", info["track"], "backdrop")
check_true("skip: 600px output written", os.path.exists(out5))

# --track (force_track) overrides the skip, for testing
out6 = os.path.join(tmp, "c-forced.png")
info = sc.make_card("Forced Tiny Render", "entertainment",
                    image_path=p3, out_path=out6, force_track="backdrop")
check("skip: force_track overrides", info["track"], "backdrop")
check_true("skip: forced output written", os.path.exists(out6))

# ── Card sets: composition, takeaways, per-card backgrounds ──────────
from unittest import mock  # noqa: E402

check("takeaways: list passes through",
      sc.normalize_takeaways([" One ", "", "Two"]), ["One", "Two"])
check("takeaways: None -> []", sc.normalize_takeaways(None), [])
check("takeaways: JSON string",
      sc.normalize_takeaways('["A", "B"]'), ["A", "B"])
check("takeaways: dict items",
      sc.normalize_takeaways([{"text": "X"}, {"takeaway": "Y"}]),
      ["X", "Y"])

BODY_HTML = (
    '<p>Intro.</p>'
    '<figure><img src="https://img.example/hero.jpg" alt="hero">'
    '</figure>'
    '<p>Body text.</p>'
    '<img src="https://img.example/inline1.jpg">'
    '<p>More.</p>'
    '![chart](https://img.example/inline2.jpg)'
    '<img src="https://img.example/inline1.jpg">'
    '<youtube>abc123</youtube>')
check("inline extraction: order + dedup + hero present",
      sc.extract_inline_images(BODY_HTML),
      ["https://img.example/hero.jpg",
       "https://img.example/inline1.jpg",
       "https://img.example/inline2.jpg"])
check("inline extraction: empty body", sc.extract_inline_images(""), [])
check("inline extraction: None body", sc.extract_inline_images(None), [])

check_true("same_image: exact", sc._same_image(
    "https://upload.wikimedia.org/wikipedia/commons/a/ab/Foo.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/ab/Foo.jpg"))
check_true("same_image: wikimedia thumb variant", sc._same_image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/"
    "Foo.jpg/1280px-Foo.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/ab/Foo.jpg"))
check_true("same_image: different files differ", not sc._same_image(
    "https://img.example/foo.jpg", "https://img.example/bar.jpg"))

# Set composition via a local hero (no body -> hero-crop middles)
p6 = os.path.join(tmp, "hero-set.jpg")
solid(2560, 1440, (120, 60, 30)).save(p6, "JPEG")
info = sc.make_card_set(
    "Set Composition Headline", "sports", image_path=p6,
    key_takeaways=["First takeaway for the set.",
                   "Second takeaway for the set.",
                   "Third takeaway must be capped."],
    slug="set-comp", out_dir=tmp)
check("set: hook+2 takeaways+closer = 4", info["set_size"], 4)
check("set: files ordered", [os.path.basename(f) for f in info["files"]],
      ["set-comp-1.png", "set-comp-2.png", "set-comp-3.png",
       "set-comp-4.png"])
check("set: roles", [c["role"] for c in info["cards"]],
      ["hook", "takeaway", "takeaway", "closer"])
check("set: takeaways capped at 2", info["takeaways_used"], 2)
check_true("set: all files written",
           all(os.path.exists(f) for f in info["files"]))
check("set: no body -> middles are hero-crops",
      [c["bg_source"] for c in info["cards"][1:3]],
      ["hero-crop", "hero-crop"])
check("set: closer alt", info["cards"][-1]["alt"],
      "Full story at thevideshi.com")

info = sc.make_card_set(
    "Subheadline Fallback Set", "news", image_path=p6,
    key_takeaways=None, subheadline="The subheadline stands in.",
    slug="set-sub", out_dir=tmp)
check("set: subheadline fallback = 3 cards", info["set_size"], 3)
check("set: middle_source subheadline", info["middle_source"],
      "subheadline")
check("set: subheadline is the middle alt",
      info["cards"][1]["alt"], "The subheadline stands in.")

info = sc.make_card_set("Bare Set No Middles", "news", image_path=p6,
                        slug="set-bare", out_dir=tmp)
check("set: no takeaways/sub = hook+closer", info["set_size"], 2)

info = sc.make_card_set("Tiny Hero Set Skips", "news", image_path=p3,
                        key_takeaways=["Never rendered."],
                        slug="set-skip", out_dir=tmp)
check("set: <600px hook -> no set", info["track"], "skipped")
check("set: skip files empty", info["files"], [])

# Takeaway truncation is flagged, never silent
info = sc.make_card_set(
    "Truncation Flag Set", "news", image_path=p6,
    key_takeaways=[" ".join(["filler"] * 900)],
    slug="set-trunc", out_dir=tmp)
check_true("set: absurd takeaway truncates with flag",
           info["cards"][1]["truncated"] is True)

# Per-card backgrounds: inline images in body order, hero excluded,
# each theme-gated on its own pixels (fake fetch serves local solids)
FAKE_IMGS = {
    "https://img.example/hero.jpg": solid(2560, 1440, (200, 30, 30)),
    "https://img.example/inline1.jpg": solid(1200, 800, (30, 200, 30)),
    "https://img.example/inline2.jpg": solid(2600, 1500, (30, 30, 200)),
}


def fake_fetch(url):
    return FAKE_IMGS[url].copy(), url, b"rawbytes"


with mock.patch.object(sc, "fetch_image", fake_fetch):
    info = sc.make_card_set(
        "Inline Background Set", "technology",
        image_url="https://img.example/hero.jpg",
        key_takeaways=["Middle one gets the low-res inline.",
                       "Middle two gets the high-res inline."],
        slug="set-inline", out_dir=tmp, body=BODY_HTML)
check("set: inline count excludes hero", info["inline_images"], 2)
check("set: middle 1 source", info["cards"][1]["bg_source"], "inline:1")
check("set: low-res inline -> backdrop middle",
      info["cards"][1]["bg_track"], "backdrop")
check("set: middle 2 source", info["cards"][2]["bg_source"], "inline:2")
check("set: high-res inline -> photo middle",
      info["cards"][2]["bg_track"], "photo")

# Fallback chain: inline fetch fails -> hero detail crop -> navy
def flaky_fetch(url):
    if "inline" in url:
        raise RuntimeError("boom")
    return FAKE_IMGS[url].copy(), url, b"rawbytes"


with mock.patch.object(sc, "fetch_image", flaky_fetch):
    info = sc.make_card_set(
        "Fallback Chain Set", "technology",
        image_url="https://img.example/hero.jpg",
        key_takeaways=["Falls back to a hero crop."],
        slug="set-fallback", out_dir=tmp, body=BODY_HTML)
check("set: failed inline -> hero-crop",
      info["cards"][1]["bg_source"], "hero-crop")

with mock.patch.object(sc, "fetch_image", fake_fetch), \
        mock.patch.object(sc, "detail_crop",
                          side_effect=RuntimeError("no crop")):
    info = sc.make_card_set(
        "Navy Last Resort Set", "technology",
        image_url="https://img.example/hero.jpg",
        key_takeaways=["Nothing left but navy."],
        slug="set-navy", out_dir=tmp, body="<p>no images here</p>")
check("set: no inline + crop fails -> navy",
      info["cards"][1]["bg_source"], "navy")
check("set: navy middle track", info["cards"][1]["bg_track"], "navy")

# A big hero's detail crop can itself clear the photo gate
BIG = {"https://img.example/big.jpg": solid(4000, 2600, (99, 88, 77))}
with mock.patch.object(
        sc, "fetch_image",
        lambda url: (BIG[url].copy(), url, b"raw")):
    info = sc.make_card_set(
        "Big Hero Crop Set", "news",
        image_url="https://img.example/big.jpg",
        key_takeaways=["Crop of a 4000px hero stays photo-grade."],
        slug="set-bigcrop", out_dir=tmp)
check("set: big-hero crop source", info["cards"][1]["bg_source"],
      "hero-crop")
check("set: big-hero crop -> photo middle",
      info["cards"][1]["bg_track"], "photo")

# Navy text card + closer render directly
card, tinfo = sc.render_text_card("A lone takeaway on navy.",
                                  "NRI WORLD", 2, 4)
check("text card canvas", card.size, (1080, 1350))
check("text card navy field", card.getpixel((10, 700)), sc.NAVY)
card, tinfo = sc.render_middle_card("No background at all.",
                                    "NEWS", 3, 4, bg_img=None)
check("middle card no-bg -> navy", tinfo["bg_track"], "navy")
card, cinfo = sc.render_closer_card("SPORTS", slug="some-slug",
                                    pos=4, total=4)
check("closer canvas", card.size, (1080, 1350))
check("closer navy field", card.getpixel((10, 10)), sc.NAVY)

print(f"\n{TOTAL[0] - len(FAILURES)}/{TOTAL[0]} checks passed"
      if not FAILURES else f"\nFAILURES: {FAILURES}")
sys.exit(1 if FAILURES else 0)
