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

print("── regression: single-channel hero must not crash face detection ──")
# 2026-10-25: the midterms story's hero reached render_reel_v7 as a
# raw Image.open() (palette mode, mode "P"), np.array() made it a
# single-channel array, YuNet threw on the 1-channel blob, and the
# Haar fallback then crashed in cvtColor (scn=1) — the story was
# dropped. detect_face_box now normalizes to RGB at entry. Build
# real single-channel fixtures (palette PNG + grayscale JPEG, the
# shapes this pipeline actually receives), reopen them UNconverted
# exactly as render_reel_v7 does, and require a sane no-face
# fallback box instead of an exception.
import io as _io
import reel_renderer as _R

_base = Image.new("RGB", (640, 480))
_px = _base.load()
for _y in range(480):
    for _x in range(640):
        _v = (_x * 255) // 640
        _px[_x, _y] = (_v, 255 - _v, (_x + _y) % 256)

for _mode_name, _img, _fmt in (
        ("palette (P)", _base.convert("P"), "PNG"),
        ("grayscale (L)", _base.convert("L"), "JPEG")):
    _buf = _io.BytesIO()
    _img.save(_buf, format=_fmt)
    _buf.seek(0)
    _raw = Image.open(_buf)
    _raw.load()
    check(f"{_mode_name} fixture really is single-channel",
          _raw.mode in ("P", "L"))
    try:
        _box, _method = _R.detect_face_box(_raw)
        _crashed = False
    except Exception as _e:  # the regression: this used to raise
        _box, _method, _crashed = None, repr(_e), True
    check(f"{_mode_name} hero: detect_face_box does not crash",
          not _crashed)
    if not _crashed:
        check(f"{_mode_name} hero: sane fallback box in frame",
              isinstance(_box, tuple) and len(_box) == 4
              and 0 <= _box[0] and 0 <= _box[1]
              and _box[0] + _box[2] <= 640
              and _box[1] + _box[3] <= 480)
        check(f"{_mode_name} hero: no face claimed on a faceless "
              f"gradient ({_method})",
              not _method.startswith(("yunet", "haar")))

print("── planner: scene-person rule (2026-11-02) ──")
# The Ambani reel's stat scene took the article's Gautam
# Adani inline because inlines arrived as bare sizes. With
# inline_persons + beat_texts supplied, a person inline is
# placed only on a scene whose text names that person.
_R = V7.R
_AMBANI_SCRIPT = {
    "hook_line": "AMBANI ADDS $6.3 BILLION IN A DAY",
    "hook_stat": {"big": "$6.3 BILLION",
                  "eyebrow": "BY THE NUMBERS",
                  "sub": "Mukesh Ambani's one-day gain, the "
                         "biggest on Forbes' real-time "
                         "billionaires list"},
    "stats": [{"big": "11.6%",
               "label": "Reliance share jump"}],
    "diaspora_bullets": [
        "Ambani stays India's richest person, ahead of "
        "Gautam Adani at 26th"],
    "news_summary": "Mukesh Ambani added $6.3 billion in a "
                    "single session as Reliance Industries "
                    "shares surged 11.6%.",
    "payoff": "The quarter, not the rich list, is the story.",
}
_BEAT_TEXTS = {k: " ".join(_R.SCENE_TEXTS[k](_AMBANI_SCRIPT,
                                             "Markets Finance"))
               for k in BEATS}
plans = V7.plan_scene_images(
    BEATS, [2400, 1600], [[1280, 900], [1600, 1000]],
    inline_persons=["Gautam Adani", None],
    beat_texts=_BEAT_TEXTS)
_src = sources(plans)
check_eq("news scene skips the Adani inline (text is about "
         "Ambani) and takes the generic inline",
         _src[1], "inline:2")
check("stat/hero scene does NOT take the Adani inline",
      not _src[2].startswith("inline:1"))
check_eq("diaspora scene takes the Adani inline — its "
         "bullet names Gautam Adani", _src[4], "inline:1")
check_eq("payoff stays the plain-stage closer", _src[5],
         "stage")
plans = V7.plan_scene_images(
    BEATS, [2400, 1600], [[1280, 900]],
    inline_persons=["Gautam Adani"], beat_texts=_BEAT_TEXTS)
_src = sources(plans)
check("an inline whose person only the diaspora scene "
      "names is held until that scene",
      _src[1] != "inline:1" and _src[2] != "inline:1"
      and _src[4] == "inline:1")
# Extras carrying a person identity obey the same rule.
_adani_extra = {"label": "adani-protest", "size": [4928, 3280],
                "entity_type": "person",
                "entity_names": ["Gautam Adani"]}
plans = V7.plan_scene_images(
    BEATS, [1599, 1200], [],
    {"payoff": dict(_adani_extra)}, beat_texts=_BEAT_TEXTS)
check_eq("a person extra is refused on the payoff scene "
         "(text names nobody) — stage closer instead",
         sources(plans)[5], "stage")
plans = V7.plan_scene_images(
    BEATS, [1599, 1200], [],
    {"diaspora": dict(_adani_extra)}, beat_texts=_BEAT_TEXTS)
check_eq("the same extra is accepted on the scene that "
         "names him", sources(plans)[4], "extra:adani-protest")
plans = V7.plan_scene_images(
    BEATS, [1599, 1200], [],
    {"payoff": {"label": "ceo", "size": [1200, 1500]}},
    beat_texts=_BEAT_TEXTS)
check_eq("an extra with NO entity identity keeps the legacy "
         "behaviour (assignment honoured)",
         sources(plans)[5], "extra:ceo")

print("── regression: full-bleed top scrim (2026-11-02) ──")
# The Ambani reel's full-bleed hero scene (Forbes Building
# photo) was HELD at frame QA with edge_overflow:hero although
# its text sat well inside the column: the offending pixels
# were the PHOTO's white clouds against its dark roofline at
# y<35 — the QA glyph signature (near-white core within ~4px
# of near-black) inside the y<118 band. A backdrop photo can
# never reach a band; a full-bleed photo reaches all of them,
# and only the bottom was protected (the legibility gradient).
# compose_scene_bg now applies apply_top_scrim on full-bleed
# scenes. Reproduce the failure shape synthetically and run
# the gate's own pixel math (imported, never edited) over the
# composed background exactly as QA does: bg warped into frame
# coords at the beat midpoint vs a black plate.
import numpy as _np
import tempfile as _tf
import reel_frame_qa as _QA

_sky = Image.new("RGB", (1600, 2400), (148, 142, 132))
_spx = _sky.load()
for _y in range(150):                    # near-white sky strip
    for _x in range(1600):
        _spx[_x, _y] = (247, 252, 255)
for _i in range(6):                      # dark roofline posts
    _x0 = 120 + _i * 240
    for _y in range(30, 110):
        for _x in range(_x0, _x0 + 40):
            _spx[_x, _y] = (8, 9, 11)


def _qa_edge_clusters(bg_img, t=13.0):
    """(offending_px, n_clusters, largest) of the gate's edge
    check for a text-free scene bg at time t, vs a black plate
    (the Ambani render's hook plate was black across the top)."""
    with _tf.TemporaryDirectory() as _td:
        _bp = Path(_td) / "bg.jpg"
        bg_img.save(_bp, quality=92)
        _pp = Path(_td) / "plate.jpg"
        Image.new("RGB", (V7.W, V7.H), (0, 0, 0)).save(_pp)
        _frame = _QA.bg_plate(_bp, t)
        _plate = _QA.bg_plate(_pp, t)
    _changed = _np.abs(
        _QA.luminance(_frame.astype(_np.float32))
        - _QA.luminance(_plate.astype(_np.float32))) > 25
    _mask = _QA.detect_text_mask(_frame) & _changed
    return _QA.clusters_in_zones(_mask)


_rect = V7.cover_window(_sky.size, (0.5, 0.5))
_pre = _sky.crop(_rect).resize((V7.W, V7.H),
                               Image.LANCZOS).convert("RGB")
_pre = _R.apply_gradient(_pre)           # the pre-fix composition
_bad, _n, _largest = _qa_edge_clusters(_pre)
check(f"fixture bites pre-fix: sky/roofline forms "
      f"{_n} glyph cluster(s) in the bands ({_bad}px)",
      _n >= 1)
_bg, _pl = V7.compose_scene_bg(_sky, "full-bleed", (0.5, 0.5),
                               V7.STAGE_COLORS["black"])
check_eq("synthetic portrait earns the full-bleed track",
         _pl["mode"], "cover")
_bad2, _n2, _ = _qa_edge_clusters(_bg)
check(f"scrimmed full-bleed bg passes the gate's edge check "
      f"({_bad2}px in bands, {_n2} clusters)", _n2 == 0)
_top = _np.array(_bg.convert("RGB"))[:148]
check("no white-core pixel survives in the zoom-reachable "
      "band (bg y<148)",
      int((_top > 235).all(axis=2).sum()) == 0)
# The stat itself was never the overflow — pin that down too:
# the hero fit for a wide stat string on a full-bleed zone
# paints inside the QA bands, stroke included.
_fit = V7.fit_scene_v7("hero", _AMBANI_SCRIPT, "Markets Finance",
                       V7.SAFE_BOTTOM - V7.SAFE_TOP)
check("hero fit succeeds for the $6.3 BILLION stat", _fit is not None)
if _fit is not None:
    _scale, _ch, _painter = _fit
    _ov = Image.new("RGBA", (V7.W, V7.H), (0, 0, 0, 0))
    _painter(_ov, V7.SAFE_BOTTOM - _ch, dark_bg=False)
    _bbox = _ov.split()[3].getbbox()
    check(f"painted stat block x {_bbox[0]}..{_bbox[2]} stays "
          f"inside the QA x bands",
          _bbox[0] >= _QA.EDGE_X0 and _bbox[2] <= _QA.EDGE_X1)
    check(f"painted stat block y {_bbox[1]}..{_bbox[3]} stays "
          f"inside the QA y bands",
          _bbox[1] >= _QA.EDGE_Y0 and _bbox[3] <= _QA.EDGE_Y1)

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAILURE(S): {FAILS}")
    sys.exit(1)
print("✅ all v7 checks passed")
