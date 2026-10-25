#!/usr/bin/env python3
"""
test_reel_v7.py — unit checks for the Reels v7 scene planner +
composition (reel_renderer_v7.py): image-source order + fallback
chain, the per-scene crispness gate (incl. a low-res case
demoting to backdrop), the no-upscale invariant, the CONSTANT
composed size rule (rev.2: backdrop scenes vary by crop REGION,
never by shrinking), the subject-keep-inside shift, the stage
colour switch, supplementary (extras) assignment, and the xfade
timing math.

Run:  python3 test_reel_v7.py    (exits 1 on any failure)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer_v7 as V7
from PIL import Image

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
check_eq("grid falls to a hero region window",
         sources(plans)[3], "hero-win:subject")
check_eq("diaspora takes the next region window",
         sources(plans)[4], "hero-win:left")
check_eq("payoff is always the plain-stage closer",
         sources(plans)[5], "stage")

plans = V7.plan_scene_images(BEATS, [1599, 1200], [])
check_eq("no inlines: beats ride the region-window chain",
         sources(plans)[1:5],
         ["hero-win:subject", "hero-win:left", "hero-win:right",
          "hero-win:bottom"])
check_eq("window scenes keep the hero as their source pixels",
         [p["source_px"] for p in plans[1:5]],
         [[1599, 1200]] * 4)

plans = V7.plan_scene_images(BEATS, [700, 500], [])
check_eq("tiny hero: windows under 480px wide are skipped",
         sources(plans)[1:5], ["stage", "stage", "stage", "stage"])

print("── planner: supplementary (extras) assignment ──")
extras = {"news": {"label": "campus-wide", "size": [4160, 3120]},
          "payoff": {"label": "ceo", "size": [1200, 1500]}}
plans = V7.plan_scene_images(BEATS, [1599, 1200], [], extras)
check_eq("assigned beat takes its supplementary photo",
         sources(plans)[1], "extra:campus-wide")
check_eq("payoff with an assignment is a photo scene, not stage",
         sources(plans)[5], "extra:ceo")
check_eq("unassigned beats still fall back to hero windows",
         sources(plans)[2], "hero-win:subject")

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
check_eq("no image is the plain stage track",
         V7.scene_track(None), ("stage", 1.0, None))

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

print("── rev.2: CONSTANT composed size, variance by REGION ──")
hero = [1599, 1200]
box = V7.stage_box(hero)
check_eq("stage box is the hook fit clamped to the safe column",
         box, (834, 625, 834 / 1599))
anchor = (0.497, 0.445)
rects = {}
for region, frac in V7.WINDOW_REGIONS:
    rect, dscale = V7.backdrop_window(hero, box, anchor,
                                      region=region, frac=frac)
    rects[region] = rect
    check(f"{region} window displays at the box size "
          f"(scale {dscale:.3f} <= 1.0)", dscale <= 1.0 + 1e-9)
    check(f"{region} window has the box aspect",
          abs((rect[2] - rect[0]) / (rect[3] - rect[1])
              - box[0] / box[1]) < 0.01)
check("regions actually differ (variance by region, not size)",
      len({(r[0], r[1]) for r in rects.values()}) >= 3)
check_eq("left window hugs the left edge", rects["left"][0], 0)
check_eq("right window hugs the right edge", rects["right"][2],
         hero[0])
check_eq("bottom window hugs the bottom edge", rects["bottom"][3],
         hero[1])
img = Image.new("RGB", hero, (90, 100, 110))
want_px = V7.SAFE_BOX_X0 + (V7.SAFE_BOX_X1 - V7.SAFE_BOX_X0
                            - box[0]) // 2
for region, frac in V7.WINDOW_REGIONS:
    rect, _ = V7.backdrop_window(hero, box, anchor, region=region,
                                 frac=frac)
    bg, pl = V7.compose_scene_bg(img, "backdrop", anchor,
                                 V7.STAGE_COLORS["navy"], box=box,
                                 window=rect)
    check(f"{region} composes at the constant display size",
          (pl["w"], pl["h"], pl["x"], pl["y"]) ==
          (box[0], box[1], want_px, V7.PHOTO_TOP))

print("── rev.2: zoom-safe placement (QA edge bands) ──")
z = 1.07     # max Ken Burns zoom (R.ZOOM_MAX over the reel)
bg, pl = V7.compose_scene_bg(img, "backdrop", anchor,
                             V7.STAGE_COLORS["navy"], box=box,
                             window=rects["subject"])
out_l = pl["x"] * z - 0.5 * V7.W * (z - 1)
out_r = (pl["x"] + pl["w"]) * z - 0.5 * V7.W * (z - 1)
out_t = pl["y"] * z - 0.3 * V7.H * (z - 1)
check(f"photo left edge stays out of the x<48 band ({out_l:.0f})",
      out_l >= 48)
check(f"photo right edge stays out of the x>952 band ({out_r:.0f})",
      out_r <= 952)
check(f"photo top stays out of the y<118 band ({out_t:.0f})",
      out_t >= 118)

print("── rev.2: subject-keep-inside ──")
# Sign-like subject low in the frame; a subject-region window
# anchored high would clip its bottom without the shift.
subject = (600, 800, 1100, 1150)     # x0,y0,x1,y1 in a 1599x1200
rect, _ = V7.backdrop_window(hero, box, (0.5, 0.30),
                             region="subject", frac=0.74,
                             subject=subject)
check("shifted window keeps the subject's bottom inside",
      rect[3] >= subject[3])
check("shifted window keeps the subject's top inside",
      rect[1] <= subject[1])
rect2, _ = V7.backdrop_window(hero, box, (0.5, 0.30),
                              region="subject", frac=0.74)
check("without a subject the same window rides higher (the old "
      "clip)", rect2[3] < subject[3])
r = V7.shift_subject_inside((0, 0, 500, 400), (450, 300, 700, 500))
check_eq("unit shift: window moves the minimum to contain",
         r, (200, 100, 700, 500))
check_eq("unit shift: no subject -> window unchanged",
         V7.shift_subject_inside((1, 2, 3, 4), None), (1, 2, 3, 4))

print("── rev.2: stage colour switch ──")
check_eq("navy stage is the house colour",
         V7.STAGE_COLORS["navy"], (11, 29, 58))
check_eq("black stage is pure black",
         V7.STAGE_COLORS["black"], (0, 0, 0))
for name, rgb in V7.STAGE_COLORS.items():
    bg, pl = V7.compose_scene_bg(None, "stage", (0.5, 0.5), rgb)
    check(f"{name} plain-stage scene paints the stage colour",
          bg.getpixel((10, 10)) == rgb and pl["mode"] == "stage")
    bg, pl = V7.compose_scene_bg(img, "backdrop", anchor, rgb,
                                 box=box,
                                 window=rects["subject"])
    check(f"{name} backdrop scene: stage colour around the photo",
          bg.getpixel((10, 10)) == rgb)
    check(f"{name} backdrop scene: photo at the constant size",
          (pl["w"], pl["h"]) == (box[0], box[1]))

print("── rev.2: xfade timing math ──")
plan = V7.xfade_plan(V7.BEATS)
check_eq("offsets sit on the beat boundaries",
         [p["offset"] for p in plan],
         [None, 4.0, 10.0, 16.0, 23.0, 30.0])
fade_frames = int(V7.XFADE_S * V7.FPS)
check("every segment but the last is extended by the fade",
      all(p["frames"] == int(d * V7.FPS) + fade_frames
          for p, (_k, _s, d) in zip(plan[:-1], V7.BEATS[:-1]))
      and plan[-1]["frames"] == int(V7.BEATS[-1][2] * V7.FPS))
total_out = plan[-1]["offset"] + plan[-1]["frames"] / V7.FPS
check_eq("chained output length is exactly the reel duration",
         total_out, V7.TOTAL)

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("✅ all v7 checks passed")
