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
PHOTO_TOP = 128                     # backdrop photo head margin:
                                    # static cards sit the photo
                                    # flush at y=0; on the reel the
                                    # frame-QA edge band (and the
                                    # Shorts UI) reserves the top
                                    # 118px, so the photo starts
                                    # just below it on the navy stage
ZONE_TOP_GAP = 64                   # photo bottom -> text block gap
ZONE_BOTTOM_PAD = 24
MIN_FONT = R.MIN_FONT
CROP_FRACS = (0.62, 0.50, 0.40, 0.32)
MIN_CROP_W = 480                    # crops narrower than this stop
                                    # the chain (navy takes over)


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
    """Track decision for one scene image (None -> navy text scene)."""
    if source_px is None:
        return "navy", 1.0, None
    return choose_track_916(source_px[0], source_px[1])


# ── Per-scene image planner (Kiran's deck ideal) ─────────────────────
def plan_scene_images(beat_keys, hero_size, inline_sizes):
    """Assign each beat its own image. Order (the approved chain):
    hook -> the hero; payoff -> navy (the closer); every other beat
    consumes, in order: the article's inline images (body order),
    then progressively tighter hero detail-crops (skipping crops
    narrower than MIN_CROP_W), then navy. Pure function of sizes —
    unit-tested in test_reel_v7.py."""
    plans = []
    inline_i = 0
    crop_i = 0
    for key in beat_keys:
        if key == "hook":
            plans.append({"beat": key, "source": "hero",
                          "source_px": list(hero_size)})
            continue
        if key == "payoff":
            plans.append({"beat": key, "source": "navy",
                          "source_px": None})
            continue
        if inline_i < len(inline_sizes):
            plans.append({"beat": key,
                          "source": f"inline:{inline_i + 1}",
                          "inline_index": inline_i,
                          "source_px": list(inline_sizes[inline_i])})
            inline_i += 1
            continue
        placed = False
        while crop_i < len(CROP_FRACS):
            frac = CROP_FRACS[crop_i]
            crop_i += 1
            cw, ch = int(hero_size[0] * frac), int(hero_size[1] * frac)
            if cw >= MIN_CROP_W:
                plans.append({"beat": key,
                              "source": f"hero-crop:{frac}",
                              "crop_frac": frac,
                              "source_px": [cw, ch]})
                placed = True
                break
        if not placed:
            plans.append({"beat": key, "source": "navy",
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
def compose_scene_bg(img, track, anchor):
    """Compose one scene's text-free 1080x1920 background.

    Returns (bg, placement) where placement records the photo
    geometry: {mode, x, y, w, h, scale} — the face mapper and the
    manifest read it. full-bleed: 9:16 cover-crop anchored on the
    focal point (exact face, else the damped heuristic — the card
    system's focal_anchor) + the v6 smooth gradient + the "V."
    mark inside the safe zone. backdrop: photo at native scale,
    top-centred on the navy stage + the gold "THE VIDESHI" chip on
    the photo's top-left (the card treatment). navy: the stage."""
    if track == "navy" or img is None:
        return Image.new("RGB", (W, H), NAVY), {
            "mode": "navy", "x": 0, "y": 0, "w": 0, "h": 0,
            "scale": 1.0}
    if track == "full-bleed":
        bg = SC.cover_crop(img, anchor, canvas=(W, H)).convert("RGB")
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
                    "scale": full_bleed_scale_916(*img.size)}
    pw, ph, scale = backdrop_fit_916(*img.size)
    photo = img if scale >= 0.999 else img.resize((pw, ph),
                                                  Image.LANCZOS)
    bg = Image.new("RGB", (W, H), NAVY)
    px = (W - pw) // 2
    bg.paste(photo, (px, PHOTO_TOP))
    SC.brand_chip(bg, x=px + 48, y=PHOTO_TOP + 44)
    return bg, {"mode": "backdrop", "x": px, "y": PHOTO_TOP,
                "w": pw, "h": ph, "scale": scale}


def map_face_to_bg(face_box, img_size, track, placement, crop_rect):
    """Map a source-image face box into scene-background coords.
    crop_rect is the cover-crop window (full-bleed only)."""
    if face_box is None:
        return None
    fx, fy, fw, fh = face_box
    if track == "full-bleed":
        x0, y0, x1, y1 = crop_rect
        sc = W / (x1 - x0)
        return [round((fx - x0) * sc), round((fy - y0) * sc),
                round(fw * sc), round(fh * sc)]
    if track == "backdrop":
        s = placement["scale"]
        return [round(fx * s) + placement["x"],
                round(fy * s) + placement["y"],
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


# ── Assembly (v6 ffmpeg shape, per-scene segments) ───────────────────
def assemble_v7(outdir, video_path, music_path, log=print):
    """One ffmpeg pass: each scene segment = its background still
    under the GLOBAL-phase Ken Burns zoom (the same curve v6 uses,
    phase-continuous across scene cuts, so the QA plate/overlay
    warps stay exact) + its text overlay faded in/out; segments
    concatenated; music bed with the v6 fades."""
    cmd = ["ffmpeg", "-y"]
    for key, _st, dur in BEATS:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / f"bg-{key}.jpg")]
    for key, _st, dur in BEATS:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(outdir / f"overlay-{key}.png")]
    cmd += ["-i", str(music_path)]
    n = len(BEATS)
    fc = []
    segs = []
    for i, (key, start, dur) in enumerate(BEATS):
        off = int(start * FPS)
        frames = int(dur * FPS)
        fc.append(
            f"[{i}:v]scale=2160:3840:flags=lanczos,"
            f"zoompan=z='1+0.07*(on+{off})/{int(TOTAL * FPS)}'"
            f":x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.30'"
            f":d={frames}:s={W}x{H}:fps={FPS},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS[bgv{i}]")
        fc.append(
            f"[{n + i}:v]format=rgba,"
            f"fade=t=in:st=0:d=0.35:alpha=1,"
            f"fade=t=out:st={max(dur - 0.3, 0):.2f}:d=0.3:alpha=1,"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS[ovf{i}]")
        fc.append(f"[bgv{i}][ovf{i}]overlay=0:0[seg{i}]")
        segs.append(f"[seg{i}]")
    fc.append("".join(segs) + f"concat=n={n}:v=1:a=0,format=yuv420p"
              "[vout]")
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
        "(global-phase Ken Burns)")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg assembly failed: "
                           + r.stderr[-600:])


# ── Main entry ───────────────────────────────────────────────────────
def render_reel_v7(script, hero_path, inline_paths, music_path,
                   outdir, name="reel", category="News",
                   photo_url=None, article_slug=None, article_id=None,
                   log=print):
    """Render the v7 sample. inline_paths: [(path, (w, h)), ...] in
    article body order (hero excluded). Returns (video_path,
    manifest dict) — the same contract shape as
    reel_renderer.render_reel, plus per-scene v7 records."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    hero_path = Path(hero_path)

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
    hero_anchor = SC.focal_anchor(hero_img, None)
    face_box, face_method = R.detect_face_box(hero_raw)
    # Only a real detector hit creates a face (the v6 rule).
    has_face = face_method.startswith(("yunet", "haar"))

    beat_keys = [k for k, _s, _d in BEATS]
    inline_sizes = [(p[1]) for p in inline_paths]
    plans = plan_scene_images(beat_keys, list(hero_src_size),
                              [list(s) for s in inline_sizes])
    plan_by_beat = {p["beat"]: p for p in plans}

    # Materialise each scene's source image (graded hero, graded
    # inline, or a focal detail-crop of the graded hero).
    inline_imgs = {}
    for idx, (path, _size) in enumerate(inline_paths):
        inline_imgs[idx] = grade_native(Image.open(path))
    scene_src = {}
    for p in plans:
        src = p["source"]
        if src == "hero":
            scene_src[p["beat"]] = hero_img
        elif src.startswith("inline:"):
            scene_src[p["beat"]] = inline_imgs[p["inline_index"]]
        elif src.startswith("hero-crop:"):
            scene_src[p["beat"]] = SC.detail_crop(
                hero_img, hero_anchor[0], hero_anchor[1],
                p["crop_frac"])
        else:
            scene_src[p["beat"]] = None

    scenes = {}
    for key, start, dur in BEATS:
        plan = plan_by_beat[key]
        track, render_scale, track_note = scene_track(plan["source_px"])
        img = scene_src[key]
        anchor = SC.focal_anchor(img, None) if img is not None \
            else (0.5, 0.5)
        bg, placement = compose_scene_bg(img, track, anchor)
        bg.save(outdir / f"bg-{key}.jpg", quality=92)
        if key == "hook":
            bg.save(outdir / "background.jpg", quality=92)

        # Text zone for this scene's composition.
        if track == "backdrop":
            zone_top = placement["y"] + placement["h"] + ZONE_TOP_GAP
            zone_h = (SAFE_BOTTOM - ZONE_BOTTOM_PAD) - zone_top
        elif track == "full-bleed":
            zone_top = SAFE_TOP
            zone_h = SAFE_BOTTOM - zone_top
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
        if track == "backdrop":
            block_top = zone_top + max(
                0, (zone_h - content_h) // 2)
        elif track == "full-bleed":
            block_top = SAFE_BOTTOM - content_h
            # Face-aware: the block must start below the chin,
            # mapped through the scene-end zoom (v6 plan_layout).
            fmap = None
            if has_face and plan["source"] == "hero":
                fmap = map_face_to_bg(
                    face_box, hero_src_size, track, placement,
                    cover_window(hero_src_size, hero_anchor))
            elif img is not None:
                fb2, fm2 = R.detect_face_box(img)
                if fm2.startswith(("yunet", "haar")):
                    fmap = map_face_to_bg(
                        fb2, img.size, track, placement,
                        cover_window(img.size, anchor))
            if fmap:
                chin_out = R.bg_to_out_y(
                    fmap[1] + fmap[3],
                    R.zoom_at(start + dur, TOTAL))
                block_top = max(block_top,
                                math.ceil(chin_out) + R.FACE_MARGIN)
        else:
            block_top = zone_top + max(0, (zone_h - content_h) // 2)
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
                "render_scale": round(render_scale, 3),
                "photo_px": plan["source_px"],
                "placement": placement,
                "track_note": track_note,
            },
        }
        log(f"  scene {key:9s} src={plan['source']:14s} "
            f"track={track:11s} scale={render_scale:.3f} "
            f"text@{scale:.2f}")

    video_path = outdir / f"{name}.mp4"
    assemble_v7(outdir, video_path, Path(music_path), log=log)

    # Manifest face record: the hero face mapped into the HOOK
    # scene's background coords (the QA plate geometry).
    hook_plan = plan_by_beat["hook"]
    hook_track = scenes["hook"]["v7"]["track"]
    hook_place = scenes["hook"]["v7"]["placement"]
    if hook_track == "full-bleed":
        fmap = map_face_to_bg(face_box, hero_src_size, hook_track,
                              hook_place,
                              cover_window(hero_src_size, hero_anchor))
    elif hook_track == "backdrop":
        fmap = map_face_to_bg(face_box, hero_src_size, hook_track,
                              hook_place, None)
    else:
        fmap = None

    manifest = {
        "renderer": "reel_renderer_v7.py (SAMPLE v7 — Cards v1 "
                    "design system on the v6 pipeline; NOT "
                    "production)",
        "design_system": "Cards v1 — Firstpost revised style "
                         "(serif-led, photo-forward, navy/gold/red)",
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
                     "backdrop (native scale on navy), else navy",
            "never_upscale": True,
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
