#!/usr/bin/env python3
"""
local-render-prototype-nobox.py — Option B prototype v4: NO-BOXES variant.

Same renderer as local-render-prototype.py (v3 state: translucent panels,
bright enhanced hero) but with the navy panel fills and gold borders
REMOVED. Text sits directly on the brightened photo. Legibility comes
from a system instead of boxes:
  - a soft feathered dark scrim localized behind each text block (drawn
    on its own layer, heavily Gaussian-blurred — every edge dissolves
    into the photo; no hard edges, no border, reads as a shadow area),
  - strong glyph treatment: dark stroke + soft drop shadow on every
    text element drawn over the photo,
  - the small gold eyebrow pill stays (a badge, not a box).

All v1–v3 guarantees kept: text measured with real font metrics before
compositing, wrapped/fitted, right side clear of the Shorts rail
(930px), nothing in the bottom UI zone, same bright hero enhancement.

Usage:
  python3 local-render-prototype-nobox.py \
      --stats pipeline/reels/build/pulse-stats-<slug>.json \
      --hero /path/hero-fullres.jpg --music /path/bed.mp3 \
      --outdir /path/out
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# ── Canvas / design standard (strategy §4.1–4.2) ────────────────────────────
W, H = 1080, 1920
FPS = 30
MARGIN = 70                      # left margin for panels
RAIL_CLEAR = 150                 # right clearance: Shorts action rail buttons
                                 # sit ~110px from the right edge — keep panels
                                 # (and ALL panel text) clear of that zone
PANEL_X0 = MARGIN                # 70
PANEL_X1 = W - RAIL_CLEAR        # 930
PANEL_W = PANEL_X1 - PANEL_X0    # 860
PANEL_CX = (PANEL_X0 + PANEL_X1) // 2   # 500 — text centers on the PANEL,
                                 # not the canvas (margins are asymmetric)
PANEL_PAD = 44
TEXT_MAX_W = PANEL_W - 2 * PANEL_PAD   # 772 — enforced for every text block
TOP_SAFE, BOT_SAFE = 140, 1580   # no text outside this vertical band
MIN_FONT = 28
# ── No-boxes legibility system (v4) ──────────────────────────────────
# No panel fills, no borders. Each text block gets a feathered scrim:
# a dark patch drawn well inside the block bounds and blurred hard, so
# after the blur only a gentle shadow area remains behind the glyphs.
SCRIM_FILL = (5, 9, 18)          # near-black navy
SCRIM_ALPHA = 175                # drawn alpha BEFORE blur (peak drops)
SCRIM_ALPHA_STRONG = 215         # for dense body text (news scene)
SCRIM_BLUR = 46                  # Gaussian radius — edges fully dissolve
TEXT_SHADOW = (0, 0, 0, 190)     # soft drop shadow under photo text
STROKE_FILL = (7, 11, 20, 255)   # dark outline painted around glyphs


def stroke_for(font):
    """Stroke width ~10% of font size, clamped — ~5px at body sizes,
    ~7–9px at headline sizes, heavier on the giant stat numerals."""
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


def draw_tracked(draw, cx, y, text, font, fill, tracking=0, shadow=False,
                 stroke=0):
    """Draw letterspaced text centered at cx. Widths are measured, so the
    block is centered on its true advance width, tracking included.
    shadow=True first paints the same glyphs offset (+2,+3) in TEXT_SHADOW.
    stroke>0 outlines every glyph in STROKE_FILL — with no panel behind
    the text, the stroke + shadow + feathered scrim carry legibility."""
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


# ── Scene furniture ──────────────────────────────────────────────────────────
def scrim(base, box, alpha=SCRIM_ALPHA):
    """Feathered dark patch behind a text block. The rect is drawn at
    the block bounds on its own layer, then blurred with a radius
    comparable to the padding — the alpha fades to zero well before any
    visible edge could form. It must read as a gentle shadow area in
    the photo, never as a box: no border, no corners, no hard edges."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    sd.rounded_rectangle(box, 48, fill=SCRIM_FILL + (alpha,))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(SCRIM_BLUR)))


def _block(content_h, center_y=1120, pad_y=46):
    """Layout without panels: returns (content_top_y, scrim_box).
    The scrim box spans the text column, padded vertically; the heavy
    blur eats the padding, leaving the shadow pooled behind the text."""
    y0 = center_y - content_h // 2
    return y0, [PANEL_X0, y0 - pad_y, PANEL_X1, y0 + content_h + pad_y]


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


# ── Hero enhancement (v3) ───────────────────────────────────────────────────
# v2's background looked dull/dark for two reasons: (1) the navy grade
# composited up to 59% navy over the bottom of the frame, and (2) the
# reel-broll hero was itself an upscale of a small thumbnail (face-region
# Laplacian variance 6.3 vs 126.9 for the article's full-res original).
# v3: feed the best legitimate source (the article image_url at full size),
# enhance deterministically, and let the translucent panels + text shadow
# carry legibility — the grade drops to ~15% of its old strength.
ENH = {
    "upscale": 2,            # 2x Lanczos supersample before crop/resize
    "denoise_blur": 0.6,     # Gaussian radius on the upscaled image
    "unsharp": (2.0, 55, 3),  # radius, percent, threshold — mild
    "gamma": 1.08,           # midtone lift
    "brightness": 1.08,
    "contrast": 1.10,
    "saturation": 1.25,
    "warmth": (1.03, 1.00, 0.96),  # per-channel R/G/B multipliers
    "grade_scale": 0.15,     # navy grade at 15% of v2 strength
}


def enhance_hero(img):
    """Deterministic bright/vivid lift. All values recorded in ENH."""
    img = img.resize((img.width * ENH["upscale"],
                      img.height * ENH["upscale"]), Image.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(ENH["denoise_blur"]))
    r, p, t = ENH["unsharp"]
    img = img.filter(ImageFilter.UnsharpMask(radius=r, percent=p,
                                             threshold=t))
    # Cover-fill 1080x1920 (crop, never stretch) from the enhanced image.
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)),
                     Image.LANCZOS)
    # Focal point: faces/subjects sit in the upper-middle of Pulse heroes.
    fx, fy = img.width // 2, int(img.height * 0.32)
    x0 = min(max(fx - W // 2, 0), img.width - W)
    y0 = min(max(fy - int(H * 0.32), 0), img.height - H)
    img = img.crop((x0, y0, x0 + W, y0 + H))
    # Exposure / color lift.
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


def load_background(hero_path):
    """Enhanced hero + a whisper of the old navy grade (15% strength)."""
    img = enhance_hero(Image.open(hero_path).convert("RGB"))
    gs = ENH["grade_scale"]
    grade = Image.new("L", (1, H))
    for yy in range(H):
        t = yy / H
        grade.putpixel((0, yy), int(
            (46 + 105 * max(0.0, (t - 0.30) / 0.70) ** 1.4) * gs))
    grade = grade.resize((W, H))
    navy = Image.new("RGB", (W, H), NAVY)
    return Image.composite(navy, img, grade)


# ── Scene builders — each returns a full-canvas RGBA overlay ────────────────
# No panels anywhere: scrim() pools a soft shadow behind each block,
# then bare text (stroke + drop shadow) sits directly on the photo.

def scene_hook(stats, category):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f_hook, hook_lines, hs = fit_block(stats["hook_line"], 800, 78,
                                       max_lines=2, uppercase=True)
    lh = line_h(hs)
    content_h = 62 + 30 + lh * len(hook_lines)
    cy, sbox = _block(content_h)
    scrim(ov, sbox)
    cy += eyebrow_pill(ov, PANEL_CX, cy, category) + 30
    draw_block(ImageDraw.Draw(ov), PANEL_CX, cy, hook_lines, f_hook,
               WHITE + (255,), lh, shadow=True, stroke=stroke_for(f_hook))
    return ov


def scene_news(stats):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f, lines, sz = fit_block(stats["news_summary"], 600, 49, max_lines=4)
    lh = line_h(sz, 1.28)
    content_h = 62 + 28 + lh * len(lines)
    cy, sbox = _block(content_h)
    # Dense body text gets the strongest local scrim — still feathered.
    scrim(ov, sbox, alpha=SCRIM_ALPHA_STRONG)
    cy += eyebrow_pill(ov, PANEL_CX, cy, "What Happened") + 28
    draw_block(ImageDraw.Draw(ov), PANEL_CX, cy, lines, f, WHITE + (255,), lh,
               shadow=True, stroke=stroke_for(f))
    return ov


def scene_hero_stat(stats):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hs = stats["hook_stat"]
    f_big, big_sz = fit_single_line(hs["big"], 800, 330, max_w=TEXT_MAX_W)
    f_sub, sub_lines, sub_sz = fit_block(hs["sub"], 700, 54, max_lines=2)
    lh = line_h(sub_sz)
    big_h = int(big_sz * 1.02)
    content_h = 62 + 20 + big_h + 16 + lh * len(sub_lines)
    cy, sbox = _block(content_h)
    scrim(ov, sbox)
    cy += eyebrow_pill(ov, PANEL_CX, cy, hs["eyebrow"]) + 20
    draw_block(ImageDraw.Draw(ov), PANEL_CX, cy, [hs["big"]], f_big,
               GOLD + (255,), big_h, shadow=True, stroke=stroke_for(f_big))
    cy += big_h + 16
    draw_block(ImageDraw.Draw(ov), PANEL_CX, cy, sub_lines, f_sub,
               WHITE + (255,), lh, shadow=True, stroke=stroke_for(f_sub))
    return ov


def scene_stat_grid(stats):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    groups = []
    for st in stats["stats"]:
        f_v, v_sz = fit_single_line(st["big"], 800, 92, max_w=TEXT_MAX_W - 56)
        f_l, l_lines, l_sz = fit_block(st["label"], 700, 38, max_lines=2,
                                       uppercase=True)
        llh = line_h(l_sz, 1.2)
        group_h = int(v_sz * 1.04) + 10 + llh * len(l_lines)
        groups.append((st, f_v, v_sz, f_l, l_lines, llh, group_h))
    rule_zone = 40          # gap between groups; gold rule sits mid-gap
    total_h = 62 + 28 + sum(g[6] for g in groups) \
        + rule_zone * (len(groups) - 1)
    y, sbox = _block(total_h, center_y=1130)
    scrim(ov, sbox)
    y += eyebrow_pill(ov, PANEL_CX, y, "By The Numbers") + 28
    d = ImageDraw.Draw(ov)
    for i, (st, f_v, v_sz, f_l, l_lines, llh, group_h) in enumerate(groups):
        if i:
            ry = y - rule_zone // 2 - 2
            d.rectangle([PANEL_CX - 190, ry, PANEL_CX + 190, ry + 3],
                        fill=GOLD + (190,))
        draw_block(d, PANEL_CX, y, [st["big"]], f_v, GOLD + (255,),
                   int(v_sz * 1.04), shadow=True, stroke=stroke_for(f_v))
        ty = y + int(v_sz * 1.04) + 10
        draw_block(d, PANEL_CX, ty, l_lines, f_l, WHITE + (255,), llh,
                   shadow=True, stroke=stroke_for(f_l))
        y += group_h + rule_zone
    return ov


def scene_diaspora(stats):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    items = []
    for b in stats["diaspora_bullets"]:
        f, lines, sz = fit_block(b, 600, 47, max_w=TEXT_MAX_W - 56,
                                 max_lines=2)
        items.append((f, lines, line_h(sz, 1.26)))
    content_h = 62 + 30 + sum(i[2] * len(i[1]) for i in items) \
        + 20 * (len(items) - 1)
    cy, sbox = _block(content_h)
    scrim(ov, sbox)
    cy += eyebrow_pill(ov, PANEL_CX, cy, "Why It Matters To You") + 30
    d = ImageDraw.Draw(ov)
    tx = PANEL_X0 + PANEL_PAD + 56
    for f, lines, lh in items:
        # gold square marker, vertically centered on the first line
        d.rounded_rectangle([PANEL_X0 + PANEL_PAD + 4, cy + 16,
                             PANEL_X0 + PANEL_PAD + 24, cy + 36], 5,
                            fill=GOLD + (255,), outline=STROKE_FILL, width=2)
        cy = draw_block(d, tx, cy, lines, f, WHITE + (255,), lh,
                        align="left", shadow=True, stroke=stroke_for(f))
        cy += 20
    return ov


def scene_payoff(stats):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f, lines, sz = fit_block(stats["payoff"], 700, 56, max_lines=2)
    lh = line_h(sz)
    f_brand = get_font(800, 34)
    brand = "THE VIDESHI"
    tail = " · thevideshi.com"
    f_tail = get_font(600, 31)
    content_h = 62 + 28 + lh * len(lines) + 30 + 10 + 44
    cy, sbox = _block(content_h)
    scrim(ov, sbox)
    cy += eyebrow_pill(ov, PANEL_CX, cy, "The Takeaway") + 28
    draw_block(ImageDraw.Draw(ov), PANEL_CX, cy, lines, f, WHITE + (255,), lh,
               shadow=True, stroke=stroke_for(f))
    cy += lh * len(lines) + 30
    d = ImageDraw.Draw(ov)
    d.rectangle([PANEL_CX - 60, cy, PANEL_CX + 60, cy + 4],
                fill=GOLD + (255,))
    cy += 24
    bw = text_width(f_brand, brand, 4) + f_tail.getlength(tail)

    def _brand_pass(dx, dy, brand_fill, tail_fill, sw, sf):
        x = PANEL_CX - bw / 2 + dx
        for ch in brand:
            d.text((x, cy + dy), ch, font=f_brand, fill=brand_fill,
                   stroke_width=sw, stroke_fill=sf)
            x += f_brand.getlength(ch) + 4
        d.text((x, cy + 3 + dy), tail, font=f_tail, fill=tail_fill,
               stroke_width=sw, stroke_fill=sf)

    _brand_pass(2, 3, TEXT_SHADOW, TEXT_SHADOW, 3, TEXT_SHADOW)
    _brand_pass(0, 0, GOLD + (255,), OFFWHITE + (255,), 3, STROKE_FILL)
    return ov


# ── Assembly ─────────────────────────────────────────────────────────────────
BEATS = [  # (builder key, start, duration) — mirrors the Shotstack timeline
    ("hook", 0.0, 4.0), ("news", 4.0, 6.0), ("hero", 10.0, 6.0),
    ("grid", 16.0, 7.0), ("diaspora", 23.0, 7.0), ("payoff", 30.0, 5.0),
]
TOTAL = 35.0


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

    builders = {
        "hook": lambda: scene_hook(stats, args.category),
        "news": lambda: scene_news(stats),
        "hero": lambda: scene_hero_stat(stats),
        "grid": lambda: scene_stat_grid(stats),
        "diaspora": lambda: scene_diaspora(stats),
        "payoff": lambda: scene_payoff(stats),
    }
    overlay_paths = {}
    for key, _, _ in BEATS:
        try:
            ov = builders[key]()
        except TextFitError as e:
            print(f"🚫 BUILD FAILED ({key}): {e}", file=sys.stderr)
            return 1
        p = outdir / f"overlay-{key}.png"
        ov.save(p)
        overlay_paths[key] = p
        print(f"  ✓ scene {key}: text measured & fitted")

    bg = load_background(args.hero)
    bg_path = outdir / "background.jpg"
    bg.save(bg_path, quality=92)

    # ffmpeg: Ken Burns on the graded hero, scene overlays faded in/out,
    # music bed with a closing fade. No external render service involved.
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
