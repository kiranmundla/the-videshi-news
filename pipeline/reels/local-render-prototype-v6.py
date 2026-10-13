#!/usr/bin/env python3
"""
local-render-prototype-v6.py — Option B prototype v6: no white cloud.

Lineage: v5 (local-render-prototype-v5.py) — NO-BOXES + gradient +
face-aware placement. Kiran's review of v5 found one more defect:

  The tight close-up uses the FIT composition (photo seated upper-frame
  over a blurred copy of itself). The photo's lower region is a white
  shirt, so the blurred extension reads as a milky WHITE CLOUD across
  the bottom of the frame.

v6 fixes it, in priority order:

  FIX A — avoid the fit composition when possible. The cover-fill
  planner's minimum scale drops 0.60 → 0.50, so more photos can run
  full-bleed cover-fill (no backdrop at all) with every scene's block
  still below the chin. (For THIS photo the chin sits at 62% of the
  source height, so under cover-fill the grid scene's zone is ~310px
  against a ~370px floor — cover is still rejected by the planner,
  which prints the reason; FIX B is what this photo ships with.)

  FIX B — when the fit composition is unavoidable, its blurred
  backdrop is DARK: blurred, darkened hard (brightness x0.40), and
  tinted toward deep navy. The lower frame then reads as a deliberate
  dark stage under the photo; the photo's feathered bottom edge fades
  into darkness, never into a white cloud.

Composition stays consistent across the whole reel (one branch, chosen
once by the planner) — no per-scene switching.

Lineage: v4 (local-render-prototype-nobox.py) removed the navy panels;
legibility came from a localized feathered scrim pooled behind each text
block + glyph stroke/shadow. Kiran's review of v4 found two defects:

  1. The localized scrim reads as a visible "dark cloud" — pooled over
     the subject's face, its feathered boundary is perceptible as a
     smudge, especially over skin.
  2. Text blocks sit across the subject's face (blocks were centered at
     a fixed y regardless of where the face is).

v5 fixes both, as production approaches (detection-driven, no
hand-placed coordinates):

  FIX 1 — gradient, not blob. The localized scrims are GONE. Legibility
  now comes from a smooth FULL-FRAME vertical gradient overlay
  (transparent at the top, deepening toward the bottom — a gradient has
  no boundary, so there is no cloud) plus the v4 glyph stroke + soft
  drop shadow.

  FIX 2 — face-aware placement. The face is detected in the hero photo
  (OpenCV Haar cascades, frontal → profile, largest face — the same
  cascade approach as pipeline/focal_point.py; if detection fails, the
  focal-point heuristic synthesizes the box and the run REPORTS that).
  The background is composed so the face sits in the UPPER portion of
  the frame, and every scene's text block is placed BELOW the chin:
  the text zone starts under the detected chin (mapped through the
  Ken Burns zoom, worst case at each scene's end) plus a margin, and
  ends at the bottom safe line. If a block is too tall for the zone,
  type shrinks within the measured-fit system — text never climbs back
  over the face.

  Composition is chosen automatically: a face-anchored cover-fill crop
  is tried first; if any scene cannot fit below the chin at a sane
  scale (>= 0.50 in v6), the composer falls back to a fit-width composition
  (photo seated in the upper frame over its own blurred backdrop —
  the standard aspect-mismatch treatment), which seats the face higher
  and opens a taller text zone. The chosen branch and the reason are
  printed and saved to layout-report.json in the outdir.

All earlier guarantees kept: text measured with real font metrics
before compositing, wrapped/fitted, right side clear of the Shorts
rail (930px), nothing below the bottom safe line, bright v3 hero
enhancement, article full-res photo as the source.

Usage:
  python3 local-render-prototype-v6.py \
      --stats pipeline/reels/build/pulse-stats-<slug>.json \
      --hero /path/hero-fullres.jpg --music /path/bed.mp3 \
      --outdir /path/out --name <file-stem>
"""
import argparse, json, math, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# ── Canvas / design standard (strategy §4.1–4.2) ────────────────────────────
W, H = 1080, 1920
FPS = 30
MARGIN = 70                      # left margin for the text column
RAIL_CLEAR = 150                 # right clearance: Shorts action rail
PANEL_X0 = MARGIN                # 70
PANEL_X1 = W - RAIL_CLEAR        # 930
PANEL_W = PANEL_X1 - PANEL_X0    # 860
PANEL_CX = (PANEL_X0 + PANEL_X1) // 2   # 500 — text centers on the column
PANEL_PAD = 44
TEXT_MAX_W = PANEL_W - 2 * PANEL_PAD   # 772 — enforced for every text block
TOP_SAFE, BOT_SAFE = 140, 1580   # no text outside this vertical band
MIN_FONT = 28

# ── v5 legibility: full-frame gradient (replaces v4's localized scrims) ─────
# alpha(t) = 0 for t <= GRAD_T0; GRAD_AMAX * ((t - T0)/(1 - T0))**EXP after.
# Smooth and full-width: no boundary anywhere, so no "cloud".
GRAD_COLOR = (5, 9, 18)          # near-black navy, same tone as v4 scrim
GRAD_T0 = 0.25                   # gradient starts 25% down the frame
GRAD_EXP = 1.35                  # ease exponent
GRAD_AMAX = 165                  # alpha at the very bottom (~65%)
TEXT_SHADOW = (0, 0, 0, 190)     # soft drop shadow under photo text
STROKE_FILL = (7, 11, 20, 255)   # dark outline painted around glyphs

# ── v5 face-aware placement ─────────────────────────────────────────────────
FACE_MARGIN = 48                 # px gap between chin and text-zone top
COVER_MIN_SCALE = 0.50           # v6: lowered 0.60 -> 0.50 so cover-fill
                                 # (no backdrop at all) wins whenever every
                                 # scene still fits below the chin
FIT_MIN_SCALE = 0.45             # hard floor in the fallback composition
ZOOM_MAX = 0.07                  # Ken Burns zoom range (matches ffmpeg)

# ── v6 fit-backdrop treatment: DARK stage, never a white cloud ─────────────
# The fit composition's backdrop is a blurred copy of the photo; when the
# photo's lower region is bright (white shirt), the blur reads as a milky
# cloud. Darken it hard and tint it toward deep navy so the lower frame
# reads as a deliberate dark stage under the photo.
BACKDROP_BLUR = 30               # Gaussian radius (unchanged from v5)
BACKDROP_BRIGHTNESS = 0.40       # hard darkening (v5 used 0.78)
BACKDROP_NAVY_TINT = 0.50        # blend factor toward solid NAVY


def stroke_for(font):
    """Stroke width ~10% of font size, clamped."""
    return max(3, min(18, round(font.size * 0.10)))

NAVY = (11, 29, 58)              # #0B1D3A
GOLD = (212, 168, 67)            # #D4A843
RED = (163, 45, 47)              # #A32D2F
WHITE = (255, 255, 255)
OFFWHITE = (232, 236, 242)

FONT_DIR = Path(__file__).parent / "fonts-local"
FONTS = {400: "Inter-400.ttf", 600: "Inter-600.ttf", 700: "Inter-700.ttf",
         800: "Inter-800.ttf", 900: "Inter-900.ttf"}
_font_cache = {}


def get_font(weight, size):
    key = (weight, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / FONTS[weight]), size)
    return _font_cache[key]


# ── Text measurement — the production approach being evaluated ──────────────
class TextFitError(Exception):
    pass


def text_width(font, s, tracking=0):
    w = font.getlength(s)
    if tracking and len(s) > 1:
        w += tracking * (len(s) - 1)
    return w


def _wrap(font, text, max_w, tracking=0):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if text_width(font, trial, tracking) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_block(text, weight, size, max_w=TEXT_MAX_W, max_lines=2,
              tracking=0, uppercase=False):
    """Wrap + shrink `text` until every line measures <= max_w and the line
    count fits. Returns (font, lines, final_size). Raises TextFitError."""
    if uppercase:
        text = text.upper()
    size = int(size)
    while size >= MIN_FONT:
        font = get_font(weight, size)
        lines = _wrap(font, text, max_w, tracking)
        if len(lines) <= max_lines and all(
                text_width(font, ln, tracking) <= max_w for ln in lines):
            return font, lines, size
        size -= 2
    raise TextFitError(f"cannot fit {text!r} in {max_w}px x {max_lines} lines")


def fit_single_line(text, weight, size, max_w=TEXT_MAX_W, tracking=0,
                    uppercase=False):
    """Shrink-to-fit for text that must never wrap (big stats, eyebrows)."""
    if uppercase:
        text = text.upper()
    size = int(size)
    while size >= MIN_FONT:
        font = get_font(weight, size)
        if text_width(font, text, tracking) <= max_w:
            return font, size
        size -= 2
    raise TextFitError(f"cannot fit single line {text!r} in {max_w}px")


def line_h(size, factor=1.24):
    return int(size * factor)


def S(base, scale):
    """Scale a starting font size, never below the measured-fit floor."""
    return max(MIN_FONT, int(round(base * scale)))


def G(base, scale):
    """Scale a layout gap."""
    return int(round(base * scale))


def draw_tracked(draw, cx, y, text, font, fill, tracking=0, shadow=False,
                 stroke=0):
    """Draw letterspaced text centered at cx (measured, so the block is
    centered on its true advance width, tracking included)."""
    total = text_width(font, text, tracking)

    def _pass(dx, dy, f, sw, sf):
        x = cx - total / 2 + dx
        for ch in text:
            draw.text((x, y + dy), ch, font=font, fill=f,
                      stroke_width=sw, stroke_fill=sf)
            x += font.getlength(ch) + tracking

    if shadow:
        _pass(2, 3, TEXT_SHADOW, stroke, TEXT_SHADOW)
    _pass(0, 0, fill, stroke, STROKE_FILL)
    return total


def draw_block(draw, cx, y, lines, font, fill, lh, tracking=0, align="center",
               shadow=False, stroke=0):
    for ln in lines:
        if align == "center":
            draw_tracked(draw, cx, y, ln, font, fill, tracking,
                         shadow=shadow, stroke=stroke)
        else:
            if shadow:
                draw.text((cx + 2, y + 3), ln, font=font, fill=TEXT_SHADOW,
                          stroke_width=stroke, stroke_fill=TEXT_SHADOW)
            draw.text((cx, y), ln, font=font, fill=fill,
                      stroke_width=stroke, stroke_fill=STROKE_FILL)
        y += lh
    return y


def eyebrow_pill(base, cx, y, text):
    """Gold pill with navy letterspaced caps — measured before drawn."""
    font, _ = fit_single_line(text, 700, 32, max_w=TEXT_MAX_W - 80,
                              tracking=6, uppercase=True)
    tw = text_width(font, text.upper(), 6)
    ph = 62
    pw = tw + 56
    box = [cx - pw / 2, y, cx + pw / 2, y + ph]
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, ph // 2, fill=GOLD + (255,))
    draw_tracked(d, cx, y + (ph - 32) // 2 - 3, text.upper(), font,
                 NAVY + (255,), tracking=6)
    return ph


# ── Hero enhancement (v3 values, unchanged) ─────────────────────────────────
# Deterministic bright/vivid lift applied to the article's full-res photo.
# v5 splits v4's enhance+crop: enhancement is geometry-preserving (uniform
# upscale + per-pixel color), composition happens separately so the face
# box can be mapped through it exactly.
ENH = {
    "upscale": 2,            # 2x Lanczos supersample
    "denoise_blur": 0.6,     # Gaussian radius on the upscaled image
    "unsharp": (2.0, 55, 3),  # radius, percent, threshold — mild
    "gamma": 1.08,           # midtone lift
    "brightness": 1.08,
    "contrast": 1.10,
    "saturation": 1.25,
    "warmth": (1.03, 1.00, 0.96),  # per-channel R/G/B multipliers
}


def enhance_raw(img):
    """Enhance the full source image (NO crop — composition is separate)."""
    img = img.resize((img.width * ENH["upscale"],
                      img.height * ENH["upscale"]), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(ENH["denoise_blur"]))
    r, p, t = ENH["unsharp"]
    img = img.filter(ImageFilter.UnsharpMask(radius=r, percent=p,
                                             threshold=t))
    g = ENH["gamma"]
    img = img.point(lambda v: min(255, int(255 * (v / 255) ** (1 / g))))
    img = ImageEnhance.Brightness(img).enhance(ENH["brightness"])
    img = ImageEnhance.Contrast(img).enhance(ENH["contrast"])
    img = ImageEnhance.Color(img).enhance(ENH["saturation"])
    wr, wg, wb = ENH["warmth"]
    chans = img.split()
    img = Image.merge("RGB", (
        chans[0].point(lambda v: min(255, int(v * wr))),
        chans[1].point(lambda v: min(255, int(v * wg))),
        chans[2].point(lambda v: min(255, int(v * wb)))))
    return img


# ── Face detection (Haar cascades — same approach as focal_point.py) ────────
def detect_face_box(src_img):
    """Detect the subject's face in the source image (PIL, RGB).
    Returns (box, method): box = (x, y, w, h) in SOURCE pixels of the
    largest detected face; method says how the box was obtained.
    Falls back to the focal-point heuristic, then to a static
    upper-frame box — and says so; never silently hand-places."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        w, h = src_img.size
        return (int(w * 0.22), int(h * 0.10), int(w * 0.56),
                int(h * 0.40)), "static-fallback (cv2 unavailable)"

    arr = np.array(src_img)
    h, w = arr.shape[:2]
    scale = 1.0
    if max(h, w) > 800:
        scale = 800 / max(h, w)
        arr = cv2.resize(arr, (int(w * scale), int(h * scale)))
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    sh, sw = gray.shape[:2]
    min_size = (int(sw * 0.04), int(sh * 0.04))
    for cascade_name in ("haarcascade_frontalface_default.xml",
                         "haarcascade_profileface.xml"):
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_name)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1,
                                         minNeighbors=5, minSize=min_size)
        if len(faces) > 0:
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            box = tuple(int(round(v / scale)) for v in (fx, fy, fw, fh))
            return box, f"haar:{cascade_name}"

    # No face found — focal-point heuristic box (reported, not hidden).
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from focal_point import compute_focal_point
        import io
        buf = io.BytesIO()
        src_img.save(buf, format="JPEG", quality=92)
        fx, fy = compute_focal_point(buf.getvalue())
    except Exception:
        fx, fy = 0.5, 0.32
    bw, bh = int(w * 0.56), int(h * 0.40)
    bx = min(max(int(fx * w - bw / 2), 0), w - bw)
    by = min(max(int(fy * h - bh * 0.55), 0), h - bh)
    return (bx, by, bw, bh), "focal-heuristic (no face detected)"


# ── Background composition (face-aware) ────────────────────────────────────
def compose_cover(enh, face_enh):
    """Face-anchored cover-fill crop. Returns (bg, face_box_in_bg)."""
    scale = max(W / enh.width, H / enh.height)
    sw, sh = round(enh.width * scale), round(enh.height * scale)
    img = enh.resize((sw, sh), Image.LANCZOS)
    fx, fy, fw, fh = [v * scale for v in face_enh]
    # Horizontal: center the crop window on the face.
    x0 = int(min(max(fx + fw / 2 - W / 2, 0), max(sw - W, 0)))
    # Vertical: seat the face top ~150px into the frame when the crop
    # window has freedom; a tall-aspect source may leave none (y0 = 0).
    y0 = int(min(max(fy - 150, 0), max(sh - H, 0)))
    bg = img.crop((x0, y0, x0 + W, y0 + H))
    face_bg = (fx - x0, fy - y0, fw, fh)
    return bg, face_bg


def compose_fit(enh, face_enh):
    """Fit-width composition: the photo, scaled to frame width, seated
    at the top of the frame over its own blurred cover-fill backdrop
    (feathered bottom edge). Returns (bg, face_box_in_bg).

    v6: the backdrop is a DARK stage — blurred, darkened hard
    (brightness xBACKDROP_BRIGHTNESS) and tinted toward deep navy —
    so a bright lower-photo region (white shirt) can never bleed
    through as a milky white cloud; the photo's feathered bottom
    edge fades into darkness instead."""
    # Backdrop: blurred cover-fill, darkened hard + navy tint.
    backdrop, _ = compose_cover(enh, face_enh)
    backdrop = backdrop.filter(ImageFilter.GaussianBlur(BACKDROP_BLUR))
    backdrop = ImageEnhance.Brightness(backdrop).enhance(
        BACKDROP_BRIGHTNESS)
    navy_stage = Image.new("RGB", backdrop.size, NAVY)
    backdrop = Image.blend(backdrop, navy_stage, BACKDROP_NAVY_TINT)
    # Foreground: fit to width.
    fscale = W / enh.width
    fw_px, fh_px = W, round(enh.height * fscale)
    fg = enh.resize((fw_px, fh_px), Image.LANCZOS).convert("RGBA")
    # Seat the photo so the face top lands ~230px down; never negative
    # (a close-up's face may start higher — top-align is the floor).
    face_top_fg = face_enh[1] * fscale
    y_off = int(max(0, 230 - face_top_fg))
    y_off = min(y_off, H - fh_px) if fh_px < H else 0
    if fh_px > H:  # degenerate: foreground taller than the frame
        fg = fg.crop((0, 0, fw_px, H))
        fh_px = H
        y_off = 0
    # Feather the foreground's bottom edge into the backdrop (mask goes
    # into the foreground's alpha channel, then alpha-composite).
    mask = Image.new("L", (fw_px, fh_px), 255)
    feather = min(150, fh_px // 4)
    md = ImageDraw.Draw(mask)
    for i in range(feather):
        a = int(255 * (feather - i) / feather)
        md.line([(0, fh_px - feather + i), (fw_px, fh_px - feather + i)],
                fill=a)
    fg.putalpha(mask)
    backdrop = backdrop.convert("RGBA")
    backdrop.alpha_composite(fg, (0, y_off))
    fx, fy, fw, fh = [v * fscale for v in face_enh]
    face_bg = (fx, fy + y_off, fw, fh)
    return backdrop.convert("RGB"), face_bg


def apply_gradient(bg):
    """Full-frame vertical gradient overlay (FIX 1). Returns RGB."""
    alpha = Image.new("L", (1, H))
    for yy in range(H):
        t = yy / H
        if t <= GRAD_T0:
            a = 0
        else:
            a = int(GRAD_AMAX * ((t - GRAD_T0) / (1 - GRAD_T0)) ** GRAD_EXP)
        alpha.putpixel((0, yy), a)
    alpha = alpha.resize((W, H))
    grad = Image.new("RGB", (W, H), GRAD_COLOR)
    return Image.composite(grad, bg, alpha)


def zoom_at(t_seconds, total):
    """Ken Burns zoom factor at time t (matches the ffmpeg zoompan)."""
    return 1.0 + ZOOM_MAX * (t_seconds / total)


def bg_to_out_y(bg_y, z):
    """Map a background y to output coords under zoom z. The zoompan
    runs on the 2x canvas with y-offset (2H - 2H/z)*0.30, so in output
    coords: out_y = bg_y*z - 0.3*H*(z - 1)."""
    return bg_y * z - 0.3 * H * (z - 1)


# ── Scene builders — measure/paint pairs ────────────────────────────────────
# Each measure(stats, scale, category) -> (content_h, painter) where
# painter(overlay, top_y) draws the block with its top at top_y.
# No panels, no scrims: bare text (stroke + shadow) over the gradient.

def measure_hook(stats, s, category):
    f_hook, hook_lines, hs = fit_block(stats["hook_line"], 800, S(78, s),
                                       max_lines=2, uppercase=True)
    lh = line_h(hs)
    gap = G(30, s)
    content_h = 62 + gap + lh * len(hook_lines)

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top, category) + gap
        draw_block(ImageDraw.Draw(ov), PANEL_CX, y, hook_lines, f_hook,
                   WHITE + (255,), lh, shadow=True,
                   stroke=stroke_for(f_hook))
    return content_h, paint


def measure_news(stats, s, category):
    f, lines, sz = fit_block(stats["news_summary"], 600, S(49, s),
                             max_lines=4)
    lh = line_h(sz, 1.28)
    gap = G(28, s)
    content_h = 62 + gap + lh * len(lines)

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top, "What Happened") + gap
        draw_block(ImageDraw.Draw(ov), PANEL_CX, y, lines, f,
                   WHITE + (255,), lh, shadow=True, stroke=stroke_for(f))
    return content_h, paint


def measure_hero_stat(stats, s, category):
    hs = stats["hook_stat"]
    f_big, big_sz = fit_single_line(hs["big"], 800, S(330, s),
                                    max_w=TEXT_MAX_W)
    f_sub, sub_lines, sub_sz = fit_block(hs["sub"], 700, S(54, s),
                                         max_lines=2)
    lh = line_h(sub_sz)
    big_h = int(big_sz * 1.02)
    g1, g2 = G(20, s), G(16, s)
    content_h = 62 + g1 + big_h + g2 + lh * len(sub_lines)

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top, hs["eyebrow"]) + g1
        draw_block(ImageDraw.Draw(ov), PANEL_CX, y, [hs["big"]], f_big,
                   GOLD + (255,), big_h, shadow=True,
                   stroke=stroke_for(f_big))
        y += big_h + g2
        draw_block(ImageDraw.Draw(ov), PANEL_CX, y, sub_lines, f_sub,
                   WHITE + (255,), lh, shadow=True,
                   stroke=stroke_for(f_sub))
    return content_h, paint


def measure_stat_grid(stats, s, category):
    groups = []
    for st in stats["stats"]:
        f_v, v_sz = fit_single_line(st["big"], 800, S(92, s),
                                    max_w=TEXT_MAX_W - 56)
        f_l, l_lines, l_sz = fit_block(st["label"], 700, S(38, s),
                                       max_lines=2, uppercase=True)
        llh = line_h(l_sz, 1.2)
        group_h = int(v_sz * 1.04) + G(10, s) + llh * len(l_lines)
        groups.append((st, f_v, v_sz, f_l, l_lines, llh, group_h))
    rule_zone = G(40, s)     # gap between groups; gold rule sits mid-gap
    gap = G(28, s)
    content_h = 62 + gap + sum(g[6] for g in groups) \
        + rule_zone * (len(groups) - 1)

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top, "By The Numbers") + gap
        d = ImageDraw.Draw(ov)
        for i, (st, f_v, v_sz, f_l, l_lines, llh, group_h) \
                in enumerate(groups):
            if i:
                ry = y - rule_zone // 2 - 2
                d.rectangle([PANEL_CX - 190, ry, PANEL_CX + 190, ry + 3],
                            fill=GOLD + (190,))
            draw_block(d, PANEL_CX, y, [st["big"]], f_v, GOLD + (255,),
                       int(v_sz * 1.04), shadow=True,
                       stroke=stroke_for(f_v))
            ty = y + int(v_sz * 1.04) + G(10, s)
            draw_block(d, PANEL_CX, ty, l_lines, f_l, WHITE + (255,), llh,
                       shadow=True, stroke=stroke_for(f_l))
            y += group_h + rule_zone
    return content_h, paint


def measure_diaspora(stats, s, category):
    items = []
    for b in stats["diaspora_bullets"]:
        f, lines, sz = fit_block(b, 600, S(47, s), max_w=TEXT_MAX_W - 56,
                                 max_lines=2)
        items.append((f, lines, line_h(sz, 1.26)))
    gap, bgap = G(30, s), G(20, s)
    content_h = 62 + gap + sum(i[2] * len(i[1]) for i in items) \
        + bgap * (len(items) - 1)

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top,
                               "Why It Matters To You") + gap
        d = ImageDraw.Draw(ov)
        tx = PANEL_X0 + PANEL_PAD + 56
        for f, lines, lh in items:
            d.rounded_rectangle([PANEL_X0 + PANEL_PAD + 4, y + 16,
                                 PANEL_X0 + PANEL_PAD + 24, y + 36], 5,
                                fill=GOLD + (255,), outline=STROKE_FILL,
                                width=2)
            y = draw_block(d, tx, y, lines, f, WHITE + (255,), lh,
                           align="left", shadow=True,
                           stroke=stroke_for(f))
            y += bgap
    return content_h, paint


def measure_payoff(stats, s, category):
    f, lines, sz = fit_block(stats["payoff"], 700, S(56, s), max_lines=2)
    lh = line_h(sz)
    f_brand = get_font(800, 34)
    brand = "THE VIDESHI"
    tail = " · thevideshi.com"
    f_tail = get_font(600, 31)
    gap, gap2 = G(28, s), G(30, s)
    content_h = 62 + gap + lh * len(lines) + gap2 + 10 + 44

    def paint(ov, top):
        y = top + eyebrow_pill(ov, PANEL_CX, top, "The Takeaway") + gap
        draw_block(ImageDraw.Draw(ov), PANEL_CX, y, lines, f,
                   WHITE + (255,), lh, shadow=True, stroke=stroke_for(f))
        y += lh * len(lines) + gap2
        d = ImageDraw.Draw(ov)
        d.rectangle([PANEL_CX - 60, y, PANEL_CX + 60, y + 4],
                    fill=GOLD + (255,))
        y += 24
        bw = text_width(f_brand, brand, 4) + f_tail.getlength(tail)

        def _brand_pass(dx, dy, brand_fill, tail_fill, sw, sf):
            x = PANEL_CX - bw / 2 + dx
            for ch in brand:
                d.text((x, y + dy), ch, font=f_brand, fill=brand_fill,
                       stroke_width=sw, stroke_fill=sf)
                x += f_brand.getlength(ch) + 4
            d.text((x, y + 3 + dy), tail, font=f_tail, fill=tail_fill,
                   stroke_width=sw, stroke_fill=sf)

        _brand_pass(2, 3, TEXT_SHADOW, TEXT_SHADOW, 3, TEXT_SHADOW)
        _brand_pass(0, 0, GOLD + (255,), OFFWHITE + (255,), 3, STROKE_FILL)
    return content_h, paint


MEASURERS = {
    "hook": measure_hook,
    "news": measure_news,
    "hero": measure_hero_stat,
    "grid": measure_stat_grid,
    "diaspora": measure_diaspora,
    "payoff": measure_payoff,
}


def fit_scene(key, stats, category, zone_h, floor):
    """Shrink `scale` from 1.0 until the scene's measured content fits
    the zone. Returns (scale, content_h, painter) or None."""
    s = 1.0
    while s >= floor - 1e-9:
        try:
            content_h, painter = MEASURERS[key](stats, s, category)
        except TextFitError:
            content_h, painter = None, None
        if content_h is not None and content_h <= zone_h:
            return s, content_h, painter
        s = round(s - 0.025, 4)
    return None


# ── Assembly ─────────────────────────────────────────────────────────────────
BEATS = [  # (builder key, start, duration) — mirrors the Shotstack timeline
    ("hook", 0.0, 4.0), ("news", 4.0, 6.0), ("hero", 10.0, 6.0),
    ("grid", 16.0, 7.0), ("diaspora", 23.0, 7.0), ("payoff", 30.0, 5.0),
]
TOTAL = 35.0


def plan_layout(stats, category, face_bg, branch):
    """Given the face box in background coords, compute each scene's
    text zone (below the chin, mapped through the Ken Burns zoom at
    the scene's end) and try to fit every scene. Returns a plan dict
    or None if some scene cannot fit at the branch's scale floor."""
    chin_bg = face_bg[1] + face_bg[3]
    floor = COVER_MIN_SCALE if branch == "cover" else FIT_MIN_SCALE
    plan = {"branch": branch, "chin_bg": round(chin_bg, 1), "scenes": {}}
    for key, start, dur in BEATS:
        z = zoom_at(start + dur, TOTAL)
        chin_out = bg_to_out_y(chin_bg, z)
        zone_top = max(TOP_SAFE, math.ceil(chin_out) + FACE_MARGIN)
        zone_h = BOT_SAFE - zone_top
        fit = fit_scene(key, stats, category, zone_h, floor)
        if fit is None:
            plan["failed_scene"] = key
            return plan
        s, content_h, painter = fit
        shift = min(90, max(0, (zone_h - content_h) // 2))
        plan["scenes"][key] = {
            "zoom_at_end": round(z, 4), "chin_out": round(chin_out, 1),
            "zone_top": zone_top, "zone_h": zone_h, "scale": s,
            "content_h": content_h, "block_top": zone_top + shift,
            "block_bottom": zone_top + shift + content_h,
            "_painter": painter,
        }
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stats", required=True)
    ap.add_argument("--hero", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--category", default="Immigration")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--name", default="local-pulse-sample")
    args = ap.parse_args()

    t0 = time.time()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stats = json.loads(Path(args.stats).read_text())

    # 1. Detect the face in the source photo (automatic; method reported).
    src = Image.open(args.hero).convert("RGB")
    face_src, method = detect_face_box(src)
    print(f"  🔍 face detection: method={method} "
          f"box(x={face_src[0]}, y={face_src[1]}, w={face_src[2]}, "
          f"h={face_src[3]}) in source {src.width}x{src.height}; "
          f"chin at y={face_src[1] + face_src[3]} "
          f"({(face_src[1] + face_src[3]) / src.height:.1%} of height)")

    # 2. Enhance (geometry-preserving), map the face box through the
    #    same 2x upscale the enhancement applies.
    enh = enhance_raw(src)
    face_enh = tuple(v * ENH["upscale"] for v in face_src)

    # 3. Choose the composition automatically: face-anchored cover-fill
    #    first; fit-width composition if any scene cannot fit below
    #    the chin at a sane scale under cover-fill.
    plan = None
    bg = None
    for branch, composer in (("cover", compose_cover),
                             ("fit", compose_fit)):
        cand_bg, cand_face_bg = composer(enh, face_enh)
        cand_plan = plan_layout(stats, args.category, cand_face_bg, branch)
        if "failed_scene" not in cand_plan:
            plan, bg = cand_plan, cand_bg
            plan["face_bg"] = [round(v, 1) for v in cand_face_bg]
            break
        print(f"  ↩ composition '{branch}' rejected: scene "
              f"'{cand_plan['failed_scene']}' cannot fit below the "
              f"chin at scale >= "
              f"{COVER_MIN_SCALE if branch == 'cover' else FIT_MIN_SCALE}")
    if plan is None:
        print("🚫 BUILD FAILED: no composition fits all scenes below "
              "the chin", file=sys.stderr)
        return 1
    print(f"  🖼  composition: {plan['branch']} "
          f"(face in frame: x={plan['face_bg'][0]:.0f}.."
          f"{plan['face_bg'][0] + plan['face_bg'][2]:.0f}, "
          f"y={plan['face_bg'][1]:.0f}.."
          f"{plan['face_bg'][1] + plan['face_bg'][3]:.0f})")

    # 4. Gradient over the composed background (FIX 1), then overlays.
    bg = apply_gradient(bg)
    bg_path = outdir / "background.jpg"
    bg.save(bg_path, quality=92)

    overlay_paths = {}
    for key, _, _ in BEATS:
        sc = plan["scenes"][key]
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sc.pop("_painter")(ov, sc["block_top"])
        p = outdir / f"overlay-{key}.png"
        ov.save(p)
        overlay_paths[key] = p
        print(f"  ✓ scene {key}: zone_top={sc['zone_top']} "
              f"zone_h={sc['zone_h']} scale={sc['scale']} "
              f"block={sc['block_top']}..{sc['block_bottom']} "
              f"(chin_out={sc['chin_out']}, zoom={sc['zoom_at_end']})")

    report = {
        "face_detection_method": method,
        "face_box_source": list(face_src),
        "source_dims": [src.width, src.height],
        "composition_branch": plan["branch"],
        "cover_min_scale": COVER_MIN_SCALE,
        "fit_backdrop": {"blur": BACKDROP_BLUR,
                         "brightness": BACKDROP_BRIGHTNESS,
                         "navy_tint": BACKDROP_NAVY_TINT},
        "gradient": {"color": GRAD_COLOR, "t0": GRAD_T0,
                     "exponent": GRAD_EXP, "amax": GRAD_AMAX},
        "face_margin": FACE_MARGIN,
        "plan": {k: v for k, v in plan.items()},
    }
    (outdir / "layout-report.json").write_text(json.dumps(report,
                                                          indent=2))

    # 5. ffmpeg assembly — same as v1–v4 (Ken Burns + fades + music).
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-loop", "1", "-framerate", str(FPS), "-i", str(bg_path)]
    for key, _, _ in BEATS:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i",
                str(overlay_paths[key])]
    cmd += ["-i", args.music]

    filters = [
        f"[0:v]scale=2160:3840:flags=lanczos,"
        f"zoompan=z='1+0.07*on/{int(TOTAL * FPS)}'"
        f":x='(iw-iw/zoom)/2':y='(ih-ih/zoom)*0.30'"
        f":d={int(TOTAL * FPS)}:s={W}x{H}:fps={FPS}[bg]"
    ]
    last = "bg"
    for i, (key, start, dur) in enumerate(BEATS, start=1):
        filters.append(
            f"[{i}:v]format=rgba,"
            f"fade=t=in:st={start}:d=0.35:alpha=1,"
            f"fade=t=out:st={start + dur - 0.3}:d=0.3:alpha=1[ov{i}]")
        filters.append(f"[{last}][ov{i}]overlay=0:0[out{i}]")
        last = f"out{i}"
    filters.append(f"[{last}]format=yuv420p[vout]")
    music_in = len(BEATS) + 1
    filters.append(
        f"[{music_in}:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={TOTAL - 1.6}:d=1.6[aout]")

    out_path = outdir / f"{args.name}.mp4"
    cmd += ["-filter_complex", ";".join(filters),
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "19",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "160k",
            "-t", str(TOTAL), "-movflags", "+faststart", str(out_path)]
    print("  🎬 ffmpeg assembly…")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        return 1
    print(f"✅ {out_path}  ({out_path.stat().st_size / 1e6:.1f} MB, "
          f"wall time {time.time() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
