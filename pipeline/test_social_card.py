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

print(f"\n{TOTAL[0] - len(FAILURES)}/{TOTAL[0]} checks passed"
      if not FAILURES else f"\nFAILURES: {FAILURES}")
sys.exit(1 if FAILURES else 0)
