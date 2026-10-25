#!/usr/bin/env python3
"""
test_reel_v7.py — unit checks for the Reels v7 scene planner
(reel_renderer_v7.py): image-source order + fallback chain, the
per-scene crispness gate (incl. a low-res case demoting to
backdrop), and the no-upscale invariant on scene scales.

Run:  python3 test_reel_v7.py    (exits 1 on any failure)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer_v7 as V7

FAILS = []


def check(name, cond):
    print(("  ✓ " if cond else "  ✗ ") + name)
    if not cond:
        FAILS.append(name)


def check_eq(name, got, want):
    check(f"{name} (got {got!r})", got == want)


BEATS = ["hook", "news", "hero", "grid", "diaspora", "payoff"]


def sources(plans):
    return [p["source"] for p in plans]


print("── planner: source order + fallback chain ──")
plans = V7.plan_scene_images(BEATS, [2400, 1600],
                             [[1600, 900], [1400, 1000]])
check_eq("hook takes the hero", sources(plans)[0], "hero")
check_eq("news takes inline 1", sources(plans)[1], "inline:1")
check_eq("hero beat takes inline 2", sources(plans)[2], "inline:2")
check_eq("grid falls to first hero crop",
         sources(plans)[3], "hero-crop:0.62")
check_eq("diaspora takes the tighter crop",
         sources(plans)[4], "hero-crop:0.5")
check_eq("payoff is always the navy closer",
         sources(plans)[5], "navy")

plans = V7.plan_scene_images(BEATS, [1599, 1200], [])
check_eq("no inlines: news..diaspora ride the crop chain",
         sources(plans)[1:5],
         ["hero-crop:0.62", "hero-crop:0.5", "hero-crop:0.4",
          "hero-crop:0.32"])
check_eq("crop sizes shrink progressively",
         [p["source_px"] for p in plans[1:5]],
         [[991, 744], [799, 600], [639, 480], [511, 384]])

plans = V7.plan_scene_images(BEATS, [700, 500], [])
check_eq("tiny hero: crops under 480px wide are skipped -> navy",
         sources(plans)[1:5], ["navy", "navy", "navy", "navy"])

plans = V7.plan_scene_images(BEATS, [1000, 800], [])
check_eq("mid hero: only crops >= 480px wide are used",
         sources(plans)[1:5],
         ["hero-crop:0.62", "hero-crop:0.5", "navy", "navy"])

print("── track gate: 9:16 cover-crop scale test ──")
check_eq("Infosys hero 1599x1200 would upscale 1.60x",
         round(V7.full_bleed_scale_916(1599, 1200), 2), 1.6)
track, scale, note = V7.scene_track([1599, 1200])
check_eq("Infosys hero demotes to backdrop", track, "backdrop")
check("demotion is explained", bool(note) and "upscale" in note)
check_eq("portrait original 1600x2400 earns full-bleed",
         V7.scene_track([1600, 2400])[0], "full-bleed")
check_eq("portrait render scale is a downscale (0.80)",
         round(V7.scene_track([1600, 2400])[1], 2), 0.8)
check_eq("exact-frame 1080x1920 is full-bleed at 1.00",
         V7.scene_track([1080, 1920])[:2], ("full-bleed", 1.0))
check_eq("wide-short 2560x1440 demotes (centre slice upscales)",
         V7.scene_track([2560, 1440])[0], "backdrop")
check_eq("low-res 800x600 demotes to backdrop",
         V7.scene_track([800, 600])[0], "backdrop")
check_eq("no image is the navy track",
         V7.scene_track(None), ("navy", 1.0, None))

print("── backdrop fit: native scale, never upscale ──")
pw, ph, s = V7.backdrop_fit_916(1599, 1200)
check_eq("1599x1200 fits the width at 0.675", (pw, ph),
         (1080, 810))
check("scale recorded honestly", abs(s - 1080 / 1599) < 1e-3)
pw, ph, s = V7.backdrop_fit_916(800, 600)
check_eq("800x600 stays native (no upscale to fill)",
         (pw, ph, s), (800, 600, 1.0))
pw, ph, s = V7.backdrop_fit_916(800, 2400)
check_eq("tall photo is height-capped, still downscaled only",
         (pw, ph), (340, V7.PHOTO_MAX_H))

print("── invariant: NO scene ever upscales ──")
battery = [(4000, 3000), (300, 200), (1080, 1080), (720, 1280),
           (5000, 1000), (1000, 5000), (1599, 1200), (640, 480),
           (3840, 2160), (1200, 628)]
for w, h in battery:
    track, scale, _ = V7.scene_track([w, h])
    check(f"{w}x{h} -> {track} at {scale:.3f} <= 1.0",
          scale <= 1.0 + 1e-9)
    _, _, bs = V7.backdrop_fit_916(w, h)
    check(f"{w}x{h} backdrop fit {bs:.3f} <= 1.0", bs <= 1.0 + 1e-9)

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("✅ all v7 planner checks passed")
