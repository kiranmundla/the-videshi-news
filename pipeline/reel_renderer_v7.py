#!/usr/bin/env python3
"""
reel_renderer_v7.py — SAMPLE-ONLY "Reels v7" renderer (2026-10-24):
tonight's production v6 reel re-skinned in the Cards v1 design
system (Kiran: "new format everywhere" — sample first; production
reel_renderer.py / reel_produce.py are untouched).

WHAT STAYS FROM v6 (the pipeline): the 6-beat Pulse arc and timing,
the script schema, real-font-metrics text fitting (overflow excluded
by construction), face-aware placement (YuNet-first detection from
reel_renderer), the smooth full-frame gradient on photo scenes, the
global-phase Ken Burns zoom, ffmpeg assembly, and the manifest
contract that reel_frame_qa.py verifies.

WHAT CHANGES (the Cards v1 skin — "Firstpost revised style":
serif-led, photo-forward, navy/gold/red):

  * PER-SCENE IMAGES (Kiran's deck ideal): each beat is composed as
    a card with its OWN image — hero first, then the article's
    inline images (body order, hero excluded), then progressively
    tighter hero detail-crops around the focal anchor, then plain
    navy text scenes. The payoff beat is always the navy closer
    (brand scene), exactly as the closer card is in a Cards v1 set.
  * CRISPNESS GATE per scene (the core of the new format): a scene
    photo may fill the 9:16 frame ONLY if its cover-crop render
    scale stays <= 1.0 — the demotion logic of
    social_card.choose_track, re-derived for 9:16 geometry.
    Otherwise the scene is a BACKDROP composition: the photo at
    native scale (downscale only) on the navy #0B1D3A stage, text
    precisely in the backdrop zone below it. NEVER upscale any
    photo, in any scene. (v6, by contrast, cover-fills every scene
    from a 2x-supersampled master — on a 1599x1200 hero that is a
    1.6x upscale of the 9:16 centre slice, which is the softness
    Kiran flagged.) The static cards' extra 1920px width floor is a
    4:5-canvas rule and is not imported; the never-upscale scale
    test — the system's core rule — is.
  * NO 2x supersample grade: photos are graded at native
    resolution (the v6 colour values, minus the upscale), so what
    the gate measures is what the viewer gets.
  * TYPOGRAPHY: Playfair Display for headlines and stats (the
    Cards v1 serif), Inter for kickers and labels. Kicker = tracked
    caps over a thin rule, left-aligned on the v6 text column
    (x in [70, 930]): gold kicker + gold rule on backdrop/navy
    scenes, white kicker + red rule on full-bleed photo scenes —
    the two card tracks, verbatim.
  * GATE-DRIVEN MICRO-ADAPTATIONS (recorded honestly): on-screen
    text keeps v6's thin dark stroke + soft shadow — invisible at
    these sizes against the card treatments, and it is the pixel
    signature reel_frame_qa.py detects text by (plain card text on
    flat navy would be undetectable to the QA gate, which may not
    be edited). On full-bleed scenes the "V." mark sits at y=150,
    just inside the reel safe zone (cards put it at the corner;
    the QA edge bands forbid glyphs above y=118).

This module NEVER writes to prebuilt_reels and NEVER uploads.

REVISION (2026-10-24 late, Kiran's spot-check of the first sample):
  1. CONSTANT COMPOSED SIZE — the first sample's progressive
     hero-crop shrink (0.62 -> 0.50 -> 0.40 -> 0.32, the photo
     getting smaller on the stage every scene) is abolished.
     Every backdrop scene now shows its photo at ONE composed
     size: the stage box = the hook scene's backdrop fit. Scenes
     vary by crop REGION at that same display size (focal-anchored
     windows of the source), never by shrinking. Supplied images
     (inline / supplementary) are windowed into the same box.
  2. CONTINUOUS TRANSITIONS — measured on the first sample, the
     cuts were frame-exact but the frame-to-frame change at the
     hook->news cut spiked ~28x over the within-scene motion
     baseline (MAD 27.9 vs ~0.6): two differently scaled renderings
     of the photo swapped in a single frame while the camera zoom
     advanced 0.2%. Assembly now crossfades every scene boundary
     (xfade, offsets on the beat boundaries, the shared global
     Ken Burns phase running underneath both sides), and fix 1
     removes the size/position jump itself.
  3. STAGE VARIANTS — the stage colour is a render parameter:
     "navy" (house #0B1D3A) or "black" (#000000), so Kiran can
     A/B the identical composition on both. Gold kicker/rule and
     white text are unchanged; the brand chip fill follows the
     stage.
  4. SUPPLEMENTARY ENTITY IMAGES — a scene may be assigned a
     verified supplementary photo (campus / HQ / person / org
     building) from the sourcing ladder, with provenance recorded
     in the manifest per scene. The article's own hero stays the
     hook; beats without an assignment fall back to inlines, then
     hero region windows, then the plain stage closer.
  5. The full-bleed branch now crops through the module's own
     9:16 cover_window (the first build called social_card's 4:5
     cover_crop with a wrong signature — dead code, because no
     scene in that sample earned full-bleed; the path is live now
     that high-res supplementary originals can earn it).
"""
import json, math, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer as R
import social_card as SC

W, H, FPS, TOTAL = R.W, R.H, R.FPS, R.TOTAL
BEATS = R.BEATS
NAVY = SC.NAVY                      # (11, 29, 58) #0B1D3A
GOLD, RED = R.GOLD, R.RED
WHITE, OFFWHITE = R.WHITE, R.OFFWHITE

TEXT_X = R.PANEL_X0                 # 70 — the v6 text column
TEXT_MAX_W = R.PANEL_X1 - R.PANEL_X0   # 860 (left-aligned card block)
SAFE_TOP, SAFE_BOTTOM = R.TOP_SAFE, R.BOT_SAFE   # 140 / 1580
PHOTO_MAX_H = 1020                  # backdrop: photo zone cap (~53%)
# The zoom-safe photo column. The frame-QA gate's forbidden bands
# (x<48, x>952, y<118) are sized for TEXT; a backdrop photo that
# spans the canvas gets pushed INTO them by the Ken Burns zoom
# (out = bg*z - centre*(z-1), z up to 1.07): measured on this
# sample, the facade photo's edges formed glyph-like clusters in
# the side bands and the campus photo's top row formed a 2893px
# strip in the top band. So the stage box lives inside the region
# that stays clear of every band at max zoom — which, happily,
# is almost exactly the v6 text column (x 81..925 vs text
# 70..930): photo and text share one column, as on the cards.
SAFE_BOX_X0, SAFE_BOX_X1 = 86, 920
PHOTO_TOP = 156                     # backdrop photo top: clears
                                    # the y<118 band at max zoom
                                    # (156*1.07 - 0.3*1920*0.07 =
                                    # 126.6); the static cards sit
                                    # photos at y=0, the reel cannot
ZONE_TOP_GAP = 64                   # photo bottom -> text block gap
ZONE_BOTTOM_PAD = 24
MIN_FONT = R.MIN_FONT
STAGE_COLORS = {"navy": NAVY, "black": (0, 0, 0)}
XFADE_S = 0.4                       # scene-boundary crossfade (s)
# Backdrop crop regions, cycled for hero-window scenes: windows of
# the source at the stage box's aspect, differing by REGION only.
# Widths are fractions of the largest box-aspect window and are
# clamped so a window never goes below the box (no upscale).
WINDOW_REGIONS = (("subject", 0.88), ("left", 0.80),
                  ("right", 0.80), ("bottom", 0.74))
MIN_WINDOW_W = 480                  # windows narrower than this
                                    # stop the chain (stage takes over)


# ── 9:16 track gate (social_card.choose_track logic, 9:16 geometry) ──
def full_bleed_scale_916(w, h):
    """Render scale of the 9:16 cover-crop for a w x h source."""
    win_w = h * (9 / 16) if w >= h * (9 / 16) else w
    return W / win_w


def backdrop_fit_916(w, h):
    """(placed_w, placed_h, scale): fit to canvas width, cap height
    at PHOTO_MAX_H, NEVER upscale (scale <= 1.0 always)."""
    scale = min(W / w, 1.0)
    if h * scale > PHOTO_MAX_H:
        scale = PHOTO_MAX_H / h
    return int(w * scale), int(h * scale), scale


def choose_track_916(w, h):
    """(track, render_scale, note) — the Cards v1 demotion logic:
    full-bleed is earned only when the cover-crop itself needs no
    upscale; anything else is demoted to backdrop (never upscale)."""
    s = full_bleed_scale_916(w, h)
    if s <= 1.0:
        return "full-bleed", s, None
    _, _, bs = backdrop_fit_916(w, h)
    return ("backdrop", bs,
            f"9:16 cover-crop would upscale {s:.2f}x — demoted to "
            f"backdrop (never upscale)")


def scene_track(source_px):
    """Track decision for one scene image (None -> plain stage)."""
    if source_px is None:
        return "stage", 1.0, None
    return choose_track_916(source_px[0], source_px[1])


# ── Constant composed size: the stage box + region windows ──────
def stage_box(hero_size):
    """(box_w, box_h, hook_scale) — THE composed photo size for
    every backdrop scene in the reel: the hook scene's backdrop
    fit of the hero, clamped into the zoom-safe column (see
    SAFE_BOX_X0/X1) so no scene's photo can enter the QA edge
    bands under the Ken Burns zoom. All backdrop photos render
    at exactly this size, at the same stage position; only their
    crop region varies (Kiran, 2026-10-24: the progressive
    shrink is out)."""
    bw, bh, _s = backdrop_fit_916(hero_size[0], hero_size[1])
    max_w = SAFE_BOX_X1 - SAFE_BOX_X0
    if bw > max_w:
        bh = int(bh * max_w / bw)
        bw = max_w
    return bw, bh, bw / hero_size[0]


def max_window(src_size, box):
    """The largest rect of the box's aspect inside the source."""
    sw, sh = src_size
    bw, bh = box[0], box[1]
    aspect = bw / bh
    if sw / sh >= aspect:
        win_h, win_w = sh, int(sh * aspect)
    else:
        win_w, win_h = sw, int(sw / aspect)
    return win_w, win_h


def shift_subject_inside(rect, subject):
    """Shift a crop window the minimum amount so the subject rect
    lies fully inside it (per axis, only when the window is at
    least as large as the subject on that axis). Keeps a crop from
    clipping the subject — the first sample's scene-3 sign clip."""
    if subject is None:
        return rect
    x0, y0, x1, y1 = rect
    sx0, sy0, sx1, sy1 = subject
    if x1 - x0 >= sx1 - sx0:
        if sx0 < x0:
            x1 -= x0 - sx0
            x0 = sx0
        elif sx1 > x1:
            x0 += sx1 - x1
            x1 = sx1
    if y1 - y0 >= sy1 - sy0:
        if sy0 < y0:
            y1 -= y0 - sy0
            y0 = sy0
        elif sy1 > y1:
            y0 += sy1 - y1
            y1 = sy1
    return (x0, y0, x1, y1)


def backdrop_window(src_size, box, anchor, region="subject",
                    frac=1.0, subject=None):
    """The crop window of `src_size` shown in the stage box.

    The window has the box's aspect and is sized `frac` of the
    largest such window (clamped so it never goes below the box —
    display scale <= 1.0 — and never exceeds the source). Position
    is set by `region` around the focal anchor, then shifted by
    the subject-keep-inside rule. Returns (rect, display_scale);
    when the source is smaller than the box the window is the
    largest available and display_scale > 1.0 tells the caller to
    contain-fit at native scale instead (never upscale)."""
    sw, sh = src_size
    bw, bh = box[0], box[1]
    mw, mh = max_window(src_size, box)
    win_w = min(mw, max(bw, int(mw * frac)))
    win_h = int(win_w * bh / bw)
    if win_h > mh:                      # rounding guard
        win_h = mh
        win_w = int(win_h * bw / bh)
    fx, fy = anchor
    if region == "left":
        x0 = 0
        y0 = int(fy * sh - win_h / 2)
    elif region == "right":
        x0 = sw - win_w
        y0 = int(fy * sh - win_h / 2)
    elif region == "bottom":
        x0 = int(fx * sw - win_w / 2)
        y0 = sh - win_h
    else:                               # "subject" / "wide"
        x0 = int(fx * sw - win_w / 2)
        y0 = int(fy * sh - win_h / 2)
    x0 = min(max(x0, 0), sw - win_w)
    y0 = min(max(y0, 0), sh - win_h)
    rect = shift_subject_inside((x0, y0, x0 + win_w, y0 + win_h),
                                subject)
    # Keep-inside may push the window out of frame on an axis
    # where the subject touches the edge — re-clamp (the window
    # still contains as much of the subject as the frame allows).
    x0 = min(max(rect[0], 0), sw - win_w)
    y0 = min(max(rect[1], 0), sh - win_h)
    rect = (x0, y0, x0 + win_w, y0 + win_h)
    return rect, bw / win_w


def xfade_plan(beats, fade_s=XFADE_S):
    """Pure timing math for the crossfade assembly: per-segment
    frame counts (every segment but the last is extended by the
    fade so its tail blends into the next scene) and the xfade
    offsets (the beat boundaries). Total output frames are
    exactly the reel's."""
    plan = []
    n = len(beats)
    for i, (key, start, dur) in enumerate(beats):
        frames = int(dur * FPS) + (int(fade_s * FPS) if i < n - 1
                                   else 0)
        plan.append({"beat": key, "frames": frames,
                     "offset": start if i else None})
    return plan


# ── Per-scene image planner (Kiran's deck ideal) ─────────────────────
def plan_scene_images(beat_keys, hero_size, inline_sizes,
                      extras=None):
    """Assign each beat its own image. Order (the approved chain):
    hook -> the hero; a beat with a supplementary assignment
    (extras, from the verified sourcing ladder) takes it; payoff
    without an assignment is the plain-stage closer; every other
    beat consumes, in order: the article's inline images (body
    order), then hero region windows (constant composed size —
    WINDOW_REGIONS), then the plain stage. Pure function of
    sizes — unit-tested in test_reel_v7.py."""
    extras = extras or {}
    plans = []
    inline_i = 0
    win_i = 0
    for key in beat_keys:
        if key == "hook":
            plans.append({"beat": key, "source": "hero",
                          "source_px": list(hero_size),
                          "region": "wide", "frac": 1.0})
            continue
        if key in extras:
            plans.append({"beat": key,
                          "source": f"extra:{extras[key]['label']}",
                          "extra": extras[key],
                          "source_px": list(extras[key]["size"]),
                          "region": "subject", "frac": 1.0})
            continue
        if key == "payoff":
            plans.append({"beat": key, "source": "stage",
                          "source_px": None})
            continue
        if inline_i < len(inline_sizes):
            plans.append({"beat": key,
                          "source": f"inline:{inline_i + 1}",
                          "inline_index": inline_i,
                          "source_px": list(inline_sizes[inline_i]),
                          "region": "subject", "frac": 1.0})
            inline_i += 1
            continue
        placed = False
        box_w = stage_box(hero_size)[0]
        mw, _mh = max_window(hero_size, stage_box(hero_size))
        while win_i < len(WINDOW_REGIONS):
            region, frac = WINDOW_REGIONS[win_i]
            win_i += 1
            # A window scene must fill the stage box WITHOUT
            # upscaling (window >= box width) and clear the size
            # floor — on a hero barely wider than its box the
            # regions degenerate to the full frame, so the beat
            # falls through to the plain stage instead.
            if int(mw * frac) >= max(MIN_WINDOW_W, box_w):
                plans.append({"beat": key,
                              "source": f"hero-win:{region}",
                              "region": region, "frac": frac,
                              "source_px": list(hero_size)})
                placed = True
                break
        if not placed:
            plans.append({"beat": key, "source": "stage",
                          "source_px": None})
    return plans


# ── Native-resolution grade (v6 colour values, NO 2x supersample) ───
def grade_native(img):
    """The v6 bright grade at the photo's native resolution. The
    locked v6 recipe supersamples the source 2x before cropping —
    an upscale the v7 crispness gate exists to refuse — so v7 keeps
    the colour science (gamma/brightness/contrast/saturation 1.18/
    warmth + unsharp) and drops the resize."""
    img = img.convert("RGB")
    img = img.filter(ImageFilter.UnsharpMask(
        radius=R.ENH["unsharp"][0], percent=R.ENH["unsharp"][1],
        threshold=R.ENH["unsharp"][2]))
    g = R.ENH["gamma"]
    img = img.point(lambda v: min(255, int(255 * (v / 255) ** (1 / g))))
    img = ImageEnhance.Brightness(img).enhance(R.ENH["brightness"])
    img = ImageEnhance.Contrast(img).enhance(R.ENH["contrast"])
    img = ImageEnhance.Color(img).enhance(R.ENH["saturation"])
    wr, wg, wb = R.ENH["warmth"]
    chans = img.split()
    return Image.merge("RGB", (
        chans[0].point(lambda v: min(255, int(v * wr))),
        chans[1].point(lambda v: min(255, int(v * wg))),
        chans[2].point(lambda v: min(255, int(v * wb)))))


# ── Text fitting (real font metrics, before compositing) ────────────
_probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def _wrap(font, text, max_w):
    return SC.wrap(_probe, text, font, max_w)


def fit_playfair(text, size0, max_lines, max_w=TEXT_MAX_W,
                 weight="Bold"):
    """Shrink Playfair from size0 until the wrap fits max_lines.
    Returns (font, lines, size). Raises R.TextFitError."""
    size = int(size0)
    while size >= MIN_FONT:
        font = SC.pf(size, weight)
        lines = _wrap(font, text, max_w)
        if len(lines) <= max_lines and all(
                _probe.textlength(ln, font=font) <= max_w
                for ln in lines):
            return font, lines, size
        size -= 2
    raise R.TextFitError(f"Playfair cannot fit {text!r} in "
                         f"{max_w}px x {max_lines} lines")


def fit_playfair_single(text, size0, max_w=TEXT_MAX_W,
                        weight="Bold"):
    size = int(size0)
    while size >= MIN_FONT:
        font = SC.pf(size, weight)
        if _probe.textlength(text, font=font) <= max_w:
            return font, size
        size -= 2
    raise R.TextFitError(f"Playfair single line cannot fit {text!r}")


def fit_inter_block(text, weight, size0, max_lines, max_w=TEXT_MAX_W,
                    uppercase=False):
    if uppercase:
        text = text.upper()
    size = int(size0)
    while size >= MIN_FONT:
        font = R.get_font(weight, size)
        lines = R._wrap(font, text, max_w)
        if len(lines) <= max_lines and all(
                R.text_width(font, ln) <= max_w for ln in lines):
            return font, lines, size
        size -= 2
    raise R.TextFitError(f"Inter cannot fit {text!r}")


def S(base, s):
    return R.S(base, s)


def G(base, s):
    return R.G(base, s)


# ── Painters (left-aligned card grammar; v6 stroke+shadow on text) ──
def _tracked_left(draw, x, y, text, font, tr, fill, stroke=0):
    """Letterspaced text, left-aligned (social_card.draw_tracked
    geometry) with the v6 shadow + stroke passes."""
    for dx, dy, f, sf in ((2, 3, R.TEXT_SHADOW, R.TEXT_SHADOW),
                          (0, 0, fill, R.STROKE_FILL)):
        cx = x + dx
        for ch in text:
            draw.text((cx, y + dy), ch, font=font, fill=f,
                      stroke_width=stroke, stroke_fill=sf)
            cx += draw.textlength(ch, font=font) + tr


def _block_left(draw, x, y, lines, font, fill, lh, stroke=0):
    for ln in lines:
        draw.text((x + 2, y + 3), ln, font=font, fill=R.TEXT_SHADOW,
                  stroke_width=stroke, stroke_fill=R.TEXT_SHADOW)
        draw.text((x, y), ln, font=font, fill=fill,
                  stroke_width=stroke, stroke_fill=R.STROKE_FILL)
        y += lh
    return y


def _header(draw, x, y, kicker, dark_bg):
    """Card header: tracked-caps kicker + thin rule. Gold on
    backdrop/navy scenes, white + red rule on full-bleed scenes."""
    kf = R.get_font(700, SC.KICKER_SIZE)
    kicker_fill = GOLD if dark_bg else WHITE
    rule_fill = GOLD if dark_bg else RED
    _tracked_left(draw, x, y, kicker.upper(), kf, SC.KICKER_TRACKING,
                  kicker_fill + (255,), stroke=2)
    ry = y + SC.KICKER_TO_RULE
    draw.rectangle([x, ry, x + SC.RULE_W, ry + SC.RULE_H],
                   fill=rule_fill + (255,))
    return y + SC.BLOCK_FIXED_H


# Scene measurers — measure(stats, s, category) -> (content_h,
# painter) in the v6 pattern, re-typeset in the Cards v1 grammar.
# painter(ov, top, dark_bg) draws the block with its top at `top`.

def measure_hook_v7(stats, s, category):
    f, lines, sz = fit_playfair(stats["hook_line"], S(78, s), 3)
    lh = int(sz * SC.LINE_RATIO)
    content_h = SC.BLOCK_FIXED_H + lh * len(lines)

    def paint(ov, top, dark_bg):
        y = _header(ImageDraw.Draw(ov), TEXT_X, top, category, dark_bg)
        _block_left(ImageDraw.Draw(ov), TEXT_X, y, lines, f,
                    WHITE + (255,), lh, stroke=R.stroke_for(f))
    return content_h, paint


def measure_news_v7(stats, s, category):
    f, lines, sz = fit_playfair(stats["news_summary"], S(54, s), 5)
    lh = int(sz * 1.24)
    content_h = SC.BLOCK_FIXED_H + lh * len(lines)

    def paint(ov, top, dark_bg):
        y = _header(ImageDraw.Draw(ov), TEXT_X, top, "What Happened",
                    dark_bg)
        _block_left(ImageDraw.Draw(ov), TEXT_X, y, lines, f,
                    WHITE + (255,), lh, stroke=R.stroke_for(f))
    return content_h, paint


def measure_hero_v7(stats, s, category):
    hs = stats["hook_stat"]
    f_big, big_sz = fit_playfair_single(hs["big"], S(196, s),
                                        weight="ExtraBold")
    f_sub, sub_lines, sub_sz = fit_playfair(hs["sub"], S(52, s), 2)
    lh = int(sub_sz * 1.2)
    big_h = int(big_sz * 1.04)
    gap = G(18, s)
    content_h = SC.BLOCK_FIXED_H + big_h + gap + lh * len(sub_lines)

    def paint(ov, top, dark_bg):
        d = ImageDraw.Draw(ov)
        y = _header(d, TEXT_X, top, hs["eyebrow"], dark_bg)
        _block_left(d, TEXT_X, y, [hs["big"]], f_big, GOLD + (255,),
                    big_h, stroke=R.stroke_for(f_big))
        y += big_h + gap
        _block_left(d, TEXT_X, y, sub_lines, f_sub, WHITE + (255,),
                    lh, stroke=R.stroke_for(f_sub))
    return content_h, paint


def measure_grid_v7(stats, s, category):
    groups = []
    for st in stats["stats"]:
        f_v, v_sz = fit_playfair_single(st["big"], S(104, s),
                                        weight="ExtraBold")
        f_l, l_lines, l_sz = fit_inter_block(
            st["label"], 700, S(38, s), 2, uppercase=True)
        llh = R.line_h(l_sz, 1.2)
        group_h = int(v_sz * 1.05) + G(10, s) + llh * len(l_lines)
        groups.append((st, f_v, v_sz, f_l, l_lines, llh, group_h))
    rule_zone = G(34, s)
    content_h = SC.BLOCK_FIXED_H + sum(g[6] for g in groups) \
        + rule_zone * (len(groups) - 1)

    def paint(ov, top, dark_bg):
        d = ImageDraw.Draw(ov)
        y = _header(d, TEXT_X, top, "By The Numbers", dark_bg)
        for i, (st, f_v, v_sz, f_l, l_lines, llh, group_h) \
                in enumerate(groups):
            if i:
                ry = y - rule_zone // 2 - 2
                d.rectangle([TEXT_X, ry, TEXT_X + 190, ry + 3],
                            fill=GOLD + (190,))
            _block_left(d, TEXT_X, y, [st["big"]], f_v,
                        GOLD + (255,), int(v_sz * 1.05),
                        stroke=R.stroke_for(f_v))
            ty = y + int(v_sz * 1.05) + G(10, s)
            _block_left(d, TEXT_X, ty, l_lines, f_l, WHITE + (255,),
                        llh, stroke=R.stroke_for(f_l))
            y += group_h + rule_zone
    return content_h, paint


def measure_diaspora_v7(stats, s, category):
    items = []
    for b in stats["diaspora_bullets"]:
        f, lines, sz = fit_playfair(b, S(50, s), 3,
                                    max_w=TEXT_MAX_W - 56)
        items.append((f, lines, int(sz * 1.26)))
    bgap = G(24, s)
    content_h = SC.BLOCK_FIXED_H \
        + sum(i[2] * len(i[1]) for i in items) \
        + bgap * (len(items) - 1)

    def paint(ov, top, dark_bg):
        d = ImageDraw.Draw(ov)
        y = _header(d, TEXT_X, top, "Why It Matters To You", dark_bg)
        tx = TEXT_X + 56
        for f, lines, lh in items:
            d.rounded_rectangle([TEXT_X + 4, y + 16, TEXT_X + 24,
                                 y + 36], 5, fill=GOLD + (255,),
                                outline=R.STROKE_FILL, width=2)
            y = _block_left(d, tx, y, lines, f, WHITE + (255,), lh,
                            stroke=R.stroke_for(f))
            y += bgap
    return content_h, paint


def measure_payoff_v7(stats, s, category):
    f, lines, sz = fit_playfair(stats["payoff"], S(56, s), 3)
    lh = int(sz * SC.LINE_RATIO)
    gap, gap2 = G(30, s), G(22, s)
    content_h = SC.BLOCK_FIXED_H + lh * len(lines) + gap + 4 + gap2 + 44

    def paint(ov, top, dark_bg):
        d = ImageDraw.Draw(ov)
        y = _header(d, TEXT_X, top, "The Takeaway", dark_bg)
        y = _block_left(d, TEXT_X, y, lines, f, WHITE + (255,), lh,
                        stroke=R.stroke_for(f))
        y += gap
        d.rectangle([TEXT_X, y, TEXT_X + 120, y + 4],
                    fill=GOLD + (255,))
        y += 4 + gap2
        f_brand = R.get_font(800, 34)
        f_tail = R.get_font(600, 31)
        _tracked_left(d, TEXT_X, y, "THE VIDESHI", f_brand, 4,
                      GOLD + (255,), stroke=2)
        bx = TEXT_X + SC.tracked_w(d, "THE VIDESHI", f_brand, 4)
        d.text((bx + 2, y + 3), " · thevideshi.com", font=f_tail,
               fill=R.TEXT_SHADOW, stroke_width=2,
               stroke_fill=R.TEXT_SHADOW)
        d.text((bx, y + 3), " · thevideshi.com", font=f_tail,
               fill=OFFWHITE + (255,), stroke_width=2,
               stroke_fill=R.STROKE_FILL)
    return content_h, paint


MEASURERS_V7 = {
    "hook": measure_hook_v7,
    "news": measure_news_v7,
    "hero": measure_hero_v7,
    "grid": measure_grid_v7,
    "diaspora": measure_diaspora_v7,
    "payoff": measure_payoff_v7,
}


def fit_scene_v7(key, stats, category, zone_h, floor=0.5):
    """Shrink scale from 1.0 until the scene's measured content
    fits the zone (v6 fit_scene pattern). (scale, content_h,
    painter) or None."""
    s = 1.0
    while s >= floor - 1e-9:
        try:
            content_h, painter = MEASURERS_V7[key](stats, s, category)
        except R.TextFitError:
            content_h, painter = None, None
        if content_h is not None and content_h <= zone_h:
            return s, content_h, painter
        s = round(s - 0.025, 4)
    return None


# ── Scene background composition ─────────────────────────────────────
def _brand_chip_stage(img, x, y, stage_rgb):
    """'THE VIDESHI' chip on the photo (backdrop track): pill fill
    follows the stage variant, gold outline + tracked gold caps
    (social_card.brand_chip geometry)."""
    d = ImageDraw.Draw(img)
    f = R.get_font(800, 25)
    label = "THE VIDESHI"
    tw = SC.tracked_w(d, label, f, 6)
    d.rounded_rectangle((x, y, x + tw + 36, y + 52), radius=10,
                        fill=stage_rgb, outline=GOLD, width=2)
    cx = x + 18
    for ch in label:
        d.text((cx, y + 12), ch, font=f, fill=GOLD)
        cx += d.textlength(ch, font=f) + 6


def compose_scene_bg(img, track, anchor, stage_rgb, box=None,
                     window=None):
    """Compose one scene's text-free 1080x1920 background.

    Returns (bg, placement). full-bleed: the 9:16 cover window
    (cover_window) resized to the frame — the track gate has
    already guaranteed scale <= 1.0 — + the v6 smooth gradient +
    the "V." mark inside the safe zone. backdrop: the scene's
    window of the source resized to the CONSTANT stage box
    (box_w x box_h at PHOTO_TOP) — every backdrop scene in the
    reel shows its photo at this identical size — + the brand
    chip. When window is None and the source is smaller than the
    box, the photo is contain-fitted at native scale centred in
    the box area (never upscale). stage: the bare stage."""
    if track == "stage" or img is None:
        return Image.new("RGB", (W, H), stage_rgb), {
            "mode": "stage", "x": 0, "y": 0, "w": 0, "h": 0,
            "scale": 1.0}
    if track == "full-bleed":
        rect = cover_window(img.size, anchor)
        crop = img.crop(rect)
        bg = crop.resize((W, H), Image.LANCZOS).convert("RGB")
        bg = R.apply_gradient(bg)
        # "V." mark in the card style (white Playfair V + red dot),
        # shifted from the card corner (52, 36) to y=150 — just
        # inside the reel safe zone the frame-QA gate enforces.
        d = ImageDraw.Draw(bg)
        f = SC.pf(58, "Bold")
        tw = d.textlength("V", font=f)
        d.text((58, 153), "V", font=f, fill=(0, 0, 0))
        d.text((56, 150), "V", font=f, fill=SC.WHITE)
        d.ellipse((56 + tw + 7, 190, 56 + tw + 17, 200), fill=SC.RED)
        return bg, {"mode": "cover", "x": 0, "y": 0, "w": W, "h": H,
                    "scale": full_bleed_scale_916(*img.size),
                    "window": list(rect)}
    box_w, box_h = box[0], box[1]
    bg = Image.new("RGB", (W, H), stage_rgb)
    px = SAFE_BOX_X0 + (SAFE_BOX_X1 - SAFE_BOX_X0 - box_w) // 2
    if window is not None:
        photo = img.crop(window).resize((box_w, box_h),
                                        Image.LANCZOS)
        bg.paste(photo, (px, PHOTO_TOP))
        _brand_chip_stage(bg, px + 48, PHOTO_TOP + 44, stage_rgb)
        return bg, {"mode": "backdrop", "x": px, "y": PHOTO_TOP,
                    "w": box_w, "h": box_h,
                    "scale": box_w / (window[2] - window[0]),
                    "window": list(window)}
    pw, ph, scale = backdrop_fit_916(*img.size)
    pw, ph = min(pw, box_w), min(ph, box_h)
    photo = img if (pw, ph) == img.size else img.resize(
        (pw, ph), Image.LANCZOS)
    cx = px + (box_w - pw) // 2
    cy = PHOTO_TOP + (box_h - ph) // 2
    bg.paste(photo, (cx, cy))
    _brand_chip_stage(bg, cx + 48, cy + 44, stage_rgb)
    return bg, {"mode": "backdrop-contain", "x": cx, "y": cy,
                "w": pw, "h": ph, "scale": scale, "window": None}


def map_face_to_bg(face_box, img_size, track, placement, crop_rect):
    """Map a source-image face box into scene-background coords.
    crop_rect is the source window the scene shows (the 9:16 cover
    window on full-bleed, the stage-box window on backdrop)."""
    if face_box is None:
        return None
    fx, fy, fw, fh = face_box
    if track in ("full-bleed", "backdrop") and crop_rect is not None:
        x0, y0 = crop_rect[0], crop_rect[1]
        s = placement["scale"]
        return [round((fx - x0) * s) + placement["x"],
                round((fy - y0) * s) + placement["y"],
                round(fw * s), round(fh * s)]
    return None


def cover_window(img_size, anchor):
    """The 9:16 window social_card.cover_crop would take."""
    w, h = img_size
    target = W / H
    if w / h > target:
        win_h, win_w = h, int(h * target)
    else:
        win_w, win_h = w, int(w / target)
    fx, fy = anchor
    x0 = min(max(int(fx * w - win_w / 2), 0), w - win_w)
    y0 = min(max(int(fy * h - win_h / 2), 0), h - win_h)
    return (x0, y0, x0 + win_w, y0 + win_h)


# ── Assembly (per-scene segments + crossfade joins) ─────────────────
def assemble_v7(outdir, video_path, music_path, log=print):
    """One ffmpeg pass: each scene segment = its background still
    under the GLOBAL-phase Ken Burns zoom (the same curve v6 uses,
    phase-continuous across scene cuts, so the QA plate/overlay
    warps stay exact) + its text overlay; segments are joined by
    XFADE crossfades whose offsets sit on the beat boundaries —
    the measured fix for the first sample's boundary jerk (a
    ~28x frame-change spike at every hard cut). Segments before
    the last are extended by the fade length (xfade_plan), so
    the total stays exactly TOTAL and the zoom phase runs
    continuously underneath both sides of every dissolve. Text
    overlays fade in per scene and dissolve out WITH their scene
    (the final scene keeps the v6 end fade)."""
    cmd = ["ffmpeg", "-y"]
    for key, _st, dur in BEATS:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / f"bg-{key}.jpg")]
    for key, _st, dur in BEATS:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / f"overlay-{key}.png")]
    cmd += ["-i", str(music_path)]
    n = len(BEATS)
    plan = {p["beat"]: p for p in xfade_plan(BEATS)}
    fc = []
    for i, (key, start, dur) in enumerate(BEATS):
        off = int(start * FPS)
        frames = plan[key]["frames"]
        fc.append(
            f"[{i}:v]scale=2160:3840:flags=lanczos,"
            f"zoompan=z='1+0.07*(on+{off})/{int(TOTAL * FPS)}'"
            f":x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.30'"
            f":d={frames}:s={W}x{H}:fps={FPS},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS[bgv{i}]")
        fade_tail = (f",fade=t=out:st={max(dur - 0.3, 0):.2f}"
                     f":d=0.3:alpha=1" if i == n - 1 else "")
        fc.append(
            f"[{n + i}:v]format=rgba,"
            f"fade=t=in:st=0:d=0.35:alpha=1{fade_tail},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS[ovf{i}]")
        fc.append(f"[bgv{i}][ovf{i}]overlay=0:0,"
                  f"format=yuv420p,settb=AVTB[seg{i}]")
    cur = "[seg0]"
    for i in range(1, n):
        out = "[vout]" if i == n - 1 else f"[xf{i}]"
        fc.append(f"{cur}[seg{i}]xfade=transition=fade:"
                  f"duration={XFADE_S}:offset={BEATS[i][1]:.2f}"
                  f"{out}")
        cur = out
    fc.append(f"[{2 * n}:a]atrim=0:{TOTAL},"
              f"afade=t=in:st=0:d=0.5,"
              f"afade=t=out:st={TOTAL - 2}:d=2[mout]")
    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[vout]", "-map", "[mout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "160k", "-t", str(TOTAL),
            str(video_path)]
    log("🎬 ffmpeg: per-scene Cards v1 backgrounds + overlays "
        "(global-phase Ken Burns, xfade joins)")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg assembly failed: "
                           + r.stderr[-600:])


def _subject_rect(box_xywh):
    """Detector box (x, y, w, h) -> (x0, y0, x1, y1) or None."""
    if not box_xywh:
        return None
    x, y, w, h = box_xywh
    return (x, y, x + w, y + h)


# ── Main entry ───────────────────────────────────────────────────────
def render_reel_v7(script, hero_path, inline_paths, music_path,
                   outdir, name="reel", category="News",
                   photo_url=None, article_slug=None, article_id=None,
                   stage="navy", extras=None, log=print):
    """Render the v7 sample. inline_paths: [(path, (w, h)), ...] in
    article body order (hero excluded). extras: {beat: {"label",
    "path", "size", "role", "provenance"}} — verified
    supplementary entity photos from the sourcing ladder. stage:
    "navy" | "black". Returns (video_path, manifest dict) — the
    same contract shape as reel_renderer.render_reel, plus
    per-scene v7 records."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    hero_path = Path(hero_path)
    stage_rgb = STAGE_COLORS[stage]
    extras = extras or {}

    stats = script   # v6 measurers/SCENE_TEXTS consume the raw
                     # script dict ("stats" in the v6 signatures)
    hero_raw = Image.open(hero_path)
    hero_src_size = hero_raw.size
    if hero_src_size[0] < R.MIN_PHOTO_W \
            or hero_src_size[1] < R.MIN_PHOTO_H:
        raise R.PhotoTooSmallError(
            f"hero photo {hero_src_size[0]}x{hero_src_size[1]} below "
            f"the {R.MIN_PHOTO_W}x{R.MIN_PHOTO_H} floor")

    hero_img = grade_native(hero_raw)
    hero_anchor3 = SC.focal_anchor(hero_img, None)
    hero_anchor = (hero_anchor3[0], hero_anchor3[1])
    face_box, face_method = R.detect_face_box(hero_raw)
    # Only a real detector hit creates a face (the v6 rule). The
    # detector's box (face or salient heuristic) doubles as the
    # subject rect for the keep-inside crop rule (converted from
    # the detector's XYWH to XYXY).
    has_face = face_method.startswith(("yunet", "haar"))
    hero_subject = _subject_rect(face_box)

    box = stage_box(hero_src_size)     # THE composed size (all
                                       # backdrop scenes)
    beat_keys = [k for k, _s, _d in BEATS]
    inline_sizes = [(p[1]) for p in inline_paths]
    extras_plan = {b: {"label": e["label"], "size": e["size"]}
                   for b, e in extras.items()}
    plans = plan_scene_images(beat_keys, list(hero_src_size),
                              [list(s) for s in inline_sizes],
                              extras_plan)
    plan_by_beat = {p["beat"]: p for p in plans}

    # Materialise each scene's source image (graded hero, graded
    # inline, graded supplementary) + its anchor + subject rect.
    inline_imgs = {}
    for idx, (path, _size) in enumerate(inline_paths):
        inline_imgs[idx] = grade_native(Image.open(path))
    extra_imgs = {}
    for beat, e in extras.items():
        extra_imgs[e["label"]] = grade_native(
            Image.open(e["path"]))
    scene_src, scene_anchor, scene_subject = {}, {}, {}
    for p in plans:
        src, key = p["source"], p["beat"]
        if src in ("hero",) or src.startswith("hero-win:"):
            scene_src[key] = hero_img
            scene_anchor[key] = hero_anchor
            scene_subject[key] = hero_subject
        elif src.startswith("inline:"):
            im = inline_imgs[p["inline_index"]]
            scene_src[key] = im
            a3 = SC.focal_anchor(im, None)
            scene_anchor[key] = (a3[0], a3[1])
            fb, _fm = R.detect_face_box(im)
            scene_subject[key] = _subject_rect(fb)
        elif src.startswith("extra:"):
            im = extra_imgs[p["extra"]["label"]]
            scene_src[key] = im
            hint = extras[key].get("anchor")
            if hint:
                # Sourcing marked the subject location on this
                # photo (e.g. the carved DOJ sign sits right of
                # frame) — the marked anchor wins over the
                # saliency heuristic.
                scene_anchor[key] = (hint[0], hint[1])
            else:
                a3 = SC.focal_anchor(im, None)
                scene_anchor[key] = (a3[0], a3[1])
            fb, _fm = R.detect_face_box(im)
            scene_subject[key] = _subject_rect(fb)
        else:
            scene_src[key] = None
            scene_anchor[key] = (0.5, 0.5)
            scene_subject[key] = None

    scenes = {}
    for key, start, dur in BEATS:
        plan = plan_by_beat[key]
        track, gate_scale, track_note = scene_track(plan["source_px"])
        img = scene_src[key]
        anchor = scene_anchor[key]
        window = None
        if track == "backdrop" and img is not None:
            window, dscale = backdrop_window(
                img.size, box, anchor, region=plan.get("region",
                                                      "subject"),
                frac=plan.get("frac", 1.0),
                subject=scene_subject[key])
            if dscale > 1.0:
                window = None   # contain-fit at native (no upscale)
        bg, placement = compose_scene_bg(
            img, track, anchor, stage_rgb, box=box, window=window)
        bg.save(outdir / f"bg-{key}.jpg", quality=92)
        if key == "hook":
            bg.save(outdir / "background.jpg", quality=92)

        # Text zone for this scene's composition.
        if track == "backdrop":
            zone_top = placement["y"] + placement["h"] + ZONE_TOP_GAP
            zone_h = (SAFE_BOTTOM - ZONE_BOTTOM_PAD) - zone_top
        else:
            zone_top = SAFE_TOP
            zone_h = SAFE_BOTTOM - zone_top
        fit = fit_scene_v7(key, stats, category, zone_h)
        if fit is None:
            c_min, _ = MEASURERS_V7[key](stats, 0.5, category)
            raise R.TextFitError(
                f"beat '{key}': content needs {c_min}px > zone "
                f"{zone_h}px (track {track}) even at scale 0.5")
        scale, content_h, painter = fit
        if track == "full-bleed":
            block_top = SAFE_BOTTOM - content_h
            # Face-aware: the block must start below the chin,
            # mapped through the scene-end zoom (v6 plan_layout).
            fmap = None
            if img is not None:
                if plan["source"] in ("hero",) or \
                        plan["source"].startswith("hero-win:"):
                    if has_face:
                        fmap = map_face_to_bg(
                            face_box, hero_src_size, track, placement,
                            placement.get("window"))
                else:
                    fb2, fm2 = R.detect_face_box(img)
                    if fm2.startswith(("yunet", "haar")):
                        fmap = map_face_to_bg(
                            fb2, img.size, track, placement,
                            placement.get("window"))
            if fmap:
                chin_out = R.bg_to_out_y(
                    fmap[1] + fmap[3],
                    R.zoom_at(start + dur, TOTAL))
                block_top = max(block_top,
                                math.ceil(chin_out) + R.FACE_MARGIN)
        else:
            block_top = zone_top + max(
                0, (zone_h - content_h) // 2)
        block_bottom = block_top + content_h
        if block_bottom > SAFE_BOTTOM + 22:   # stroke bleed margin
            raise R.TextFitError(
                f"beat '{key}': block bottom {block_bottom} past "
                f"the safe zone")

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        painter(ov, block_top, dark_bg=(track != "full-bleed"))
        ov.save(outdir / f"overlay-{key}.png")

        scenes[key] = {
            "start": start, "duration": dur,
            "zone_top": zone_top, "zone_h": zone_h,
            "scale": scale, "content_h": content_h,
            "block_top": block_top, "block_bottom": block_bottom,
            "text_bbox": [TEXT_X, block_top,
                          TEXT_X + TEXT_MAX_W, block_bottom],
            "texts": R.SCENE_TEXTS[key](stats, category),
            "v7": {
                "image_source": plan["source"],
                "track": track,
                "render_scale": round(placement["scale"], 3),
                "photo_px": plan["source_px"],
                "region": plan.get("region"),
                "placement": placement,
                "track_note": track_note,
                "provenance": (extras[key].get("provenance")
                               if key in extras else None),
            },
        }
        log(f"  scene {key:9s} src={plan['source']:18s} "
            f"track={track:11s} scale={placement['scale']:.3f} "
            f"text@{scale:.2f}")

    video_path = outdir / f"{name}.mp4"
    assemble_v7(outdir, video_path, Path(music_path), log=log)

    # Manifest face record: the hero face mapped into the HOOK
    # scene's background coords (the QA plate geometry).
    hook_track = scenes["hook"]["v7"]["track"]
    hook_place = scenes["hook"]["v7"]["placement"]
    fmap = map_face_to_bg(face_box, hero_src_size, hook_track,
                          hook_place, hook_place.get("window"))

    manifest = {
        "renderer": "reel_renderer_v7.py (SAMPLE v7 rev.2 — Cards "
                    "v1 design system on the v6 pipeline; constant "
                    "composed size, xfade transitions, stage "
                    "variants; NOT production)",
        "design_system": "Cards v1 — Firstpost revised style "
                         "(serif-led, photo-forward, navy/gold/red)",
        "stage": {"name": stage, "rgb": list(stage_rgb)},
        "name": name,
        "article_slug": article_slug,
        "article_id": article_id,
        "category": category,
        "video": str(video_path),
        "duration_s": TOTAL,
        "canvas": [W, H],
        "photo": {"url": photo_url, "local_path": str(hero_path),
                  "width": hero_src_size[0],
                  "height": hero_src_size[1],
                  "floor": [R.MIN_PHOTO_W, R.MIN_PHOTO_H]},
        "face": {"method": face_method, "has_face": has_face,
                 "box_source": list(face_box),
                 "box_bg": fmap,
                 "chin_bg": (fmap[1] + fmap[3]) if (has_face and fmap)
                 else None,
                 "anchor": [round(hero_anchor[0], 3),
                            round(hero_anchor[1], 3)]},
        "composition": {
            "model": "per-scene Cards v1: full-bleed only when the "
                     "9:16 cover-crop needs no upscale, else "
                     "backdrop at the CONSTANT stage box (the "
                     "hook's backdrop fit) with per-scene crop "
                     "regions, else the plain stage; scene joins "
                     "are xfade crossfades over the global Ken "
                     "Burns phase",
            "never_upscale": True,
            "stage_box": [box[0], box[1]],
            "text_column": [TEXT_X, TEXT_X + TEXT_MAX_W]},
        "grade": {"mode": "native-resolution (no 2x supersample)",
                  **{k: R.ENH[k] for k in
                     ("gamma", "brightness", "contrast",
                      "saturation")},
                  "unsharp": list(R.ENH["unsharp"]),
                  "warmth": list(R.ENH["warmth"])},
        "gradient": {"color": R.GRAD_COLOR, "t0": R.GRAD_T0,
                     "exp": R.GRAD_EXP, "amax": R.GRAD_AMAX}
        if any(s["v7"]["track"] == "full-bleed"
               for s in scenes.values()) else None,
        "safe_zone": {"x": [TEXT_X, TEXT_X + TEXT_MAX_W],
                      "y": [SAFE_TOP, SAFE_BOTTOM]},
        "scenes": scenes,
        "music": {"path": str(music_path),
                  "treatment": "bed: atrim 35s + fades in 0.5s / "
                               "out 2s (v6 produce recipe)"},
        "render_seconds": round(time.time() - t0, 1),
        "mp4_bytes": video_path.stat().st_size,
    }
    (outdir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=1))
    log(f"✅ rendered {video_path} "
        f"({manifest['mp4_bytes'] / 1e6:.1f} MB, "
        f"{manifest['render_seconds']}s)")
    return video_path, manifest
