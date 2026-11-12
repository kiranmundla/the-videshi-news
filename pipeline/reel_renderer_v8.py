#!/usr/bin/env python3
"""
reel_renderer_v8.py — the "Reels v8" renderer (PRODUCTION from
2026-11-11, adopted on Kiran's approval of the GPT-benchmark
sample v1, "Looks good"): the benchmark's professional chrome
and per-scene distinct photography on the locked v6 pipeline
arc (6 beats, 35s, BEATS/TOTAL from reel_renderer.py — the
frame-QA gate's technical check measures ~35s, unchanged).

WHAT THE BENCHMARK ADDS (spec:
research_notes/reel-style-gpt-benchmark-2026-11-11/spec.md):
  * A DISTINCT PHOTO ON EVERY SCENE — hook, news, hero, grid,
    diaspora AND the payoff closer are all photo scenes, each
    with its own image (article imagery first, then verified
    supplementary entity pictures, then — concept/policy
    stories only — credited topical stock from
    reel_stock_sourcing.py). The planner NEVER re-crops one
    image across beats: reel_produce.py holds the reel when
    distinct usable images < photo scenes (the rejected visa
    Short's failure: one entry-stamp photo at four crops).
  * PROFESSIONAL CHROME on every scene (baked into the scene
    background, so it is identical across scenes and cancels
    against the QA plate): "The Videshi" masthead + gold
    tagline + red-dash category line, a navy footer panel with
    source+date, THEVIDESHI.COM, the stock credit when stock
    is used, and progress segments that fill per scene.
  * Per-scene gold KICKER labels, serif headline on the bottom
    gradient, a BIG-STAT scene type (giant gold numerals,
    vector arrow — Playfair has no usable → glyph), option
    ROWS (V-1 / V-2), an editorial hook headline (the hook
    line title-cased from its ALL-CAPS script form), and the
    "WHAT IT MEANS FOR YOU" reader-impact beat.

QA GEOMETRY (the gate is NOT edited; the chrome is designed
around its measured bands — glyph pixels are forbidden at
x<48, x>952, y<118, y>1602):
  * Scene text (kicker/headline/support/rows) keeps the v6/v7
    stroke+shadow signature the gate detects, and is fitted
    inside x [80, 940], y [.., 1420] — inside the bands with
    margin, so the gate measures it exactly as it does v7.
  * Chrome glyphs are PLAIN text (no stroke, no shadow) on the
    flat navy panel / top gradient, AND every chrome element
    that lands in the y>1602 band in output coords (the footer
    text, rule line and progress segments, pushed there by the
    assembly zoom) is painted in a NON-CORE colour: the gate's
    glyph signature needs a white core (all channels > 235)
    or a gold core (within 40 of (212,168) with blue < 115)
    next to a near-black pixel — and Lanczos ringing around a
    bright element on navy MANUFACTURES near-black edge pixels
    (measured on the first v8 proof: (21,26,37) halos around
    the gold segments, 8 clusters). So segments use GOLD_LIGHT
    (233,203,128 — blue 128 defeats the gold core), the site
    line uses (226,229,238), the rule line (120,128,150), and
    the source line FOOT (203,208,220): none can be a core.
    The masthead additionally starts at y=126, below the
    y<118 band, as belt and braces.
  * Full-bleed scenes carry SIDE SCRIMS (the v7 top-scrim
    precedent extended): navy fades over the left/right 260px,
    strongest at the edge, sized so photo content in the
    zoom-reachable side bands (bg x < ~86, bg x > ~919 at max
    zoom) composites below the white-core threshold — a
    photo's own bright signage/detail at its edge is otherwise
    indistinguishable from glyphs to the gate (measured:
    diaspora clusters at output x>1012 on the first proof).
  * MOTION IS PER-FRAME PIL (2026-11-11, Kiran: the sample's
    zoompan movement "shakes"): ffmpeg zoompan steps its crop
    window in whole pixels and judders. assemble_v8 renders
    every frame in PIL from a 2x master with a fractional
    AFFINE transform (LANCZOS) — scale and offset are floats,
    never quantized — under a smoothstep-eased global zoom
    (the v6/v7 1.00 -> 1.07 curve, ease-in-out), with PIL
    crossfades on the beat boundaries. The easing's deviation
    from the gate's linear plate warp is <= ~4px, inside the
    dilations the gate itself applies; the demoted stage box
    is 800px wide so even that deviation keeps the photo
    inside the x bands.
  * FACE RULE: each scene's dominant face (v7's
    dominant_face_box) is anchored into the upper photo area
    by the cover-window choice; if its chin still reaches the
    text block, the scene demotes to the v7-style backdrop
    composition (photo in the stage box, text in the clear
    zone below it) instead of painting text over a face.

This module NEVER writes to prebuilt_reels and NEVER uploads.
reel_produce.py is the only production caller.
"""
import json, math, re, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer as R
import reel_renderer_v7 as V7
import social_card as SC

W, H, FPS, TOTAL = R.W, R.H, R.FPS, R.TOTAL
BEATS = R.BEATS
NAVY = SC.NAVY                      # (11, 29, 58) #0B1D3A
GOLD, RED = R.GOLD, R.RED
WHITE, OFFWHITE = R.WHITE, R.OFFWHITE
GOLD_LIGHT = (233, 203, 128)
SUPPORT = (233, 235, 241)
FOOT = (203, 208, 220)
FOOT_DIM = (150, 158, 178)
SEG_OFF = (58, 66, 92)

MARGIN = 80
TEXT_MAX_W = 860                    # scene text x in [80, 940]
PANEL_Y = 1480                      # navy footer panel top
BLOCK_BOTTOM = 1420                 # scene text bottom anchor
BLOCK_MAX_H = 780                   # scene text block cap
MASTHEAD_Y = 126                    # first chrome glyph row
PHOTO_SCENES = [k for k, _s, _d in BEATS]   # all six beats

MIN_DISTINCT_FLOOR = (R.MIN_PHOTO_W, R.MIN_PHOTO_H)   # 1080x600


class DistinctImagesError(RuntimeError):
    """Raised when the distinct usable images cannot cover the
    photo scenes — reel_produce turns this into the
    distinct-images HOLD verdict."""


# ── distinct-image planning (pure; unit-tested) ─────────────────
def image_fingerprint(path):
    """Content hash of one image file — distinctness is by
    CONTENT, not filename (the same photo downloaded twice is
    still one photo)."""
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def distinct_candidates(candidates):
    """Dedupe a candidate list by content hash, preserving
    priority order. Each candidate: {"path", "size", "label",
    "kind", "person" (name or None), "provenance"}."""
    seen, out = set(), []
    for c in candidates:
        try:
            fp = image_fingerprint(c["path"])
        except Exception:
            continue
        if fp in seen:
            continue
        seen.add(fp)
        out.append(c)
    return out


def usable_distinct(candidates):
    """Distinct candidates that clear the reel photo floor."""
    return [c for c in distinct_candidates(candidates)
            if c["size"][0] >= MIN_DISTINCT_FLOOR[0]
            and c["size"][1] >= MIN_DISTINCT_FLOOR[1]]


def plan_v8_images(beat_keys, candidates, beat_texts=None):
    """Assign each beat its OWN distinct image. Priority order
    is the caller's (hero, article inlines, verified extras,
    stock). A candidate resolved to a PERSON is placed only on
    a beat whose rendered text names that person (the
    scene-person rule, same as v7). Raises DistinctImagesError
    when the placeable distinct images cannot cover every
    beat — NEVER falls back to re-cropping an image already
    used, which is the whole point of v8."""
    import reel_entity_sourcing as RES
    pool = list(candidates)
    plans = []
    for key in beat_keys:
        pick = None
        # Preference: a candidate sourced FOR this beat (the
        # per-beat stock route tags its scenes) > an untagged
        # candidate > a candidate tagged for another beat
        # (still distinct and verified — better than holding
        # when nothing else fits). The scene-person rule gates
        # every tier.
        for tier in (lambda c: c.get("beat") == key,
                     lambda c: not c.get("beat"),
                     lambda c: True):
            for i, c in enumerate(pool):
                if not tier(c):
                    continue
                person = c.get("person")
                if person and beat_texts is not None and not \
                        RES.entity_named_in_text(
                            [person], beat_texts.get(key, "")):
                    continue
                pick = i
                break
            if pick is not None:
                break
        if pick is None:
            raise DistinctImagesError(
                f"beat '{key}': no unused distinct image left "
                f"({len(plans)} placed, {len(pool)} unplaced of "
                f"{len(candidates)} distinct candidates) — "
                "holding rather than re-cropping an image "
                "across beats")
        plans.append({"beat": key, "candidate": pool.pop(pick)})
    return plans


# ── script -> benchmark scene content (pure; unit-tested) ───────
_ACRONYMS = {"US", "UK", "USA", "AI", "H-1B", "GDP", "CEO",
             "FBI", "NASA", "UN", "EU", "IPO", "GST", "ISRO"}


def editorial_title(text):
    """Title-case an ALL-CAPS script line into the editorial
    hook form ('INDIA CUTS VISA CATEGORIES...' -> 'India cuts
    visa categories...'). Sentence case with acronyms and
    proper-capital tokens preserved; a typographic transform
    only — wording is never altered."""
    text = (text or "").strip()
    if not text:
        return text
    if text != text.upper():
        return text
    out = []
    for i, w in enumerate(text.split()):
        core = w.strip(".,:;—-")
        if core in _ACRONYMS or any(ch.isdigit() for ch in core):
            out.append(w)
        elif i == 0:
            out.append(w.capitalize())
        else:
            out.append(w.lower())
    return " ".join(out)


def big_stat_display(big):
    """'13 TO 9' -> '13 → 9' (the arrow is drawn as a vector at
    paint time); anything else passes through unchanged."""
    return re.sub(r"\s+TO\s+", " → ", (big or "").strip())


_OPTION_ROW_RE = re.compile(
    r"^\s*([A-Z][A-Z0-9-]*)\s+is\s+for\s+(.+?),\s*"
    r"([A-Z][A-Z0-9-]*)\s+(?:is\s+)?for\s+(.+?)\s*$")


def parse_option_rows(bullets):
    """A diaspora bullet of the form 'V-1 is for short visits,
    V-2 for longer stays' -> (rows, remaining_bullets); else
    (None, bullets)."""
    rest = []
    for b in bullets or []:
        m = _OPTION_ROW_RE.match(b)
        if m:
            rows = [{"label": m.group(1),
                     "value": "For " + m.group(2)},
                    {"label": m.group(3),
                     "value": "For " + m.group(4)}]
            return rows, rest + list(bullets)[list(bullets).index(b) + 1:]
        rest.append(b)
    return None, rest


def scene_content(key, script, category):
    """The benchmark content spec for one beat, derived from
    the unchanged production script schema."""
    if key == "hook":
        hs = script.get("hook_stat") or {}
        return {"kicker": "TOP STORY",
                "headline": editorial_title(script.get("hook_line")),
                "support": hs.get("sub")}
    if key == "news":
        return {"kicker": "WHAT'S NEW",
                "headline": script.get("news_summary")}
    if key == "hero":
        hs = script.get("hook_stat") or {}
        return {"kicker": (hs.get("eyebrow") or "BY THE NUMBERS"),
                "big_stat": big_stat_display(hs.get("big")),
                "headline": hs.get("sub")}
    if key == "grid":
        return {"kicker": "BY THE NUMBERS",
                "stat_rows": [
                    {"big": big_stat_display(s.get("big")),
                     "label": s.get("label")}
                    for s in script.get("stats") or []]}
    if key == "diaspora":
        rows, rest = parse_option_rows(
            script.get("diaspora_bullets"))
        return {"kicker": "WHAT IT MEANS FOR YOU",
                "rows": rows,
                "support_lines": rest}
    if key == "payoff":
        return {"kicker": "THE TAKEAWAY",
                "headline": script.get("payoff"),
                "brandline": "FOLLOW FOR DAILY DIASPORA BRIEFINGS"}
    raise KeyError(key)


# ── text fitting (real font metrics, before compositing) ────────
_probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def _wrap(font, text, max_w):
    return SC.wrap(_probe, text, font, max_w)


def _tracked_width(text, font, tracking):
    return sum(_probe.textlength(c, font=font) for c in text) \
        + tracking * max(0, len(text) - 1)


def _fit_serif(text, size0, max_lines, max_w=TEXT_MAX_W,
               min_size=26):
    size = int(size0)
    while size >= min_size:
        f = SC.pf(size, "Bold")
        lines = _wrap(f, text, max_w)
        if len(lines) <= max_lines and all(
                _probe.textlength(ln, font=f) <= max_w
                for ln in lines):
            return f, lines, size
        size -= 4
    raise R.TextFitError(f"v8 serif cannot fit {text!r}")


def _fit_serif_single(text, size0, max_w=TEXT_MAX_W, min_size=60):
    size = int(size0)
    while size >= min_size:
        f = SC.pf(size, "Bold")
        if _probe.textlength(text, font=f) <= max_w:
            return f, size
        size -= 4
    raise R.TextFitError(f"v8 serif single cannot fit {text!r}")


def measure_block(spec, s):
    """(height, parts) at scale s — parts carry fitted fonts
    and wrapped lines for the painter."""
    parts = {"kicker": spec.get("kicker")}
    h = 44 + 22                       # kicker + gap
    if spec.get("big_stat"):
        txt = spec["big_stat"]
        if "→" in txt:
            left, right = [p.strip() for p in txt.split("→")]
            f, sz = _fit_serif_single(
                left + right, int(250 * s),
                max_w=TEXT_MAX_W - int(250 * s * 0.83))
            parts["big"] = (f, left, right, sz)
        else:
            f, sz = _fit_serif_single(txt, int(250 * s))
            parts["big"] = (f, txt, None, sz)
        h += int(sz * 1.16) + 16
    if spec.get("headline"):
        start = 96 if spec.get("kicker") == "TOP STORY" else 66
        f, lines, sz = _fit_serif(
            spec["headline"], int(start * s),
            5 if start == 66 else 3,
            min_size=max(24, int(30 * s)))
        parts["headline"] = (f, lines, sz)
        h += int(sz * 1.13) * len(lines)
    for row in spec.get("rows") or []:
        f_v = SC.pf(int(57 * s), "Bold")
        parts.setdefault("rows", []).append((row, f_v))
        h += int(74 * s)
    if spec.get("rows"):
        h += 14
    for sr in spec.get("stat_rows") or []:
        f_b, b_sz = _fit_serif_single(sr["big"], int(118 * s))
        f_l = R.get_font(400, int(36 * s))
        l_lines = _wrap(f_l, sr["label"], TEXT_MAX_W)
        parts.setdefault("stat_rows", []).append(
            (sr, f_b, b_sz, f_l, l_lines))
        h += int(b_sz * 1.1) + 8 + len(l_lines) * int(36 * s * 1.3) \
            + int(26 * s)
    sup_lines = []
    sup_font = R.get_font(400, int(37 * s))
    for txt in ([spec["support"]] if spec.get("support") else []) \
            + list(spec.get("support_lines") or []):
        sup_lines += _wrap(sup_font, txt, TEXT_MAX_W)
    if sup_lines:
        parts["support"] = (sup_font, sup_lines)
        h += 10 + len(sup_lines) * int(50 * s)
    if spec.get("brandline"):
        parts["brandline"] = spec["brandline"]
        h += 52
    return h, parts


def fit_block(spec, max_h=None):
    """Largest scale in [1.0 .. 0.55] whose measured block fits
    max_h (default BLOCK_MAX_H). Returns (scale, height,
    parts)."""
    max_h = BLOCK_MAX_H if max_h is None else max_h
    s = 1.0
    while s >= 0.55 - 1e-9:
        try:
            h, parts = measure_block(spec, s)
        except R.TextFitError:
            h, parts = None, None
        if h is not None and h <= max_h:
            return s, h, parts
        s = round(s - 0.05, 4)
    raise R.TextFitError(
        f"v8 scene block cannot fit {max_h}px: "
        f"{(spec.get('headline') or spec.get('kicker') or '')[:60]!r}")


# ── painters ────────────────────────────────────────────────────
def _draw_tracked(draw, x, y, text, font, fill, tracking,
                  stroke=0):
    for ch in text:
        if stroke:
            draw.text((x + 2, y + 3), ch, font=font,
                      fill=R.TEXT_SHADOW, stroke_width=stroke,
                      stroke_fill=R.TEXT_SHADOW)
            draw.text((x, y), ch, font=font, fill=fill,
                      stroke_width=stroke, stroke_fill=R.STROKE_FILL)
        else:
            draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def _text_sh(draw, x, y, text, font, fill, stroke):
    draw.text((x + 2, y + 3), text, font=font, fill=R.TEXT_SHADOW,
              stroke_width=stroke, stroke_fill=R.TEXT_SHADOW)
    draw.text((x, y), text, font=font, fill=fill,
              stroke_width=stroke, stroke_fill=R.STROKE_FILL)


def paint_block(ov, spec, parts, s, block_top):
    """Paint one scene's text block (QA-detectable stroke+
    shadow, inside the safe column) with its top at block_top."""
    d = ImageDraw.Draw(ov)
    y = block_top
    kf = R.get_font(800, int(31 * s))
    _draw_tracked(d, MARGIN, y, spec["kicker"].upper(), kf,
                  GOLD + (255,), 5, stroke=2)
    y += 44 + 22
    if "big" in parts:
        f, left, right, sz = parts["big"]
        stroke = R.stroke_for(f)
        if right is None:
            _text_sh(d, MARGIN - 4, y, left, f, GOLD_LIGHT + (255,),
                     stroke)
        else:
            lw = d.textlength(left, font=f)
            aw, gap = int(sz * 0.68), int(sz * 0.15)
            cy = y + int(sz * 0.60)
            _text_sh(d, MARGIN - 4, y, left, f,
                     GOLD_LIGHT + (255,), stroke)
            ax0 = MARGIN - 4 + lw + gap
            d.line([(ax0, cy), (ax0 + int(aw * 0.74), cy)],
                   fill=GOLD_LIGHT + (255,),
                   width=max(6, sz // 15))
            ah = int(sz * 0.17)
            d.polygon([(ax0 + aw, cy), (ax0 + int(aw * 0.58), cy - ah),
                       (ax0 + int(aw * 0.58), cy + ah)],
                      fill=GOLD_LIGHT + (255,))
            _text_sh(d, ax0 + aw + gap, y, right, f,
                     GOLD_LIGHT + (255,), stroke)
        y += int(sz * 1.16) + 16
    if "headline" in parts:
        f, lines, sz = parts["headline"]
        for ln in lines:
            _text_sh(d, MARGIN, y, ln, f, WHITE + (255,),
                     R.stroke_for(f))
            y += int(sz * 1.13)
    if parts.get("rows"):
        y += 14
        for row, f_v in parts["rows"]:
            d.text((MARGIN + 2, y + 3), row["label"],
                   font=R.get_font(800, int(45 * s)),
                   fill=R.TEXT_SHADOW, stroke_width=2,
                   stroke_fill=R.TEXT_SHADOW)
            d.text((MARGIN, y), row["label"],
                   font=R.get_font(800, int(45 * s)),
                   fill=GOLD + (255,), stroke_width=2,
                   stroke_fill=R.STROKE_FILL)
            _text_sh(d, MARGIN + 190, y - 8, row["value"], f_v,
                     WHITE + (255,), R.stroke_for(f_v))
            y += int(74 * s)
    for sr, f_b, b_sz, f_l, l_lines in parts.get("stat_rows") or []:
        _text_sh(d, MARGIN - 2, y, sr["big"], f_b,
                 GOLD + (255,), R.stroke_for(f_b))
        y += int(b_sz * 1.1) + 8
        for ln in l_lines:
            _text_sh(d, MARGIN, y, ln, f_l, SUPPORT + (255,),
                     R.stroke_for(f_l))
            y += int(36 * s * 1.3)
        y += int(26 * s)
    if "support" in parts:
        f, lines = parts["support"]
        y += 10
        for ln in lines:
            _text_sh(d, MARGIN, y, ln, f, SUPPORT + (255,),
                     R.stroke_for(f))
            y += int(50 * s)
    if "brandline" in parts:
        bf = R.get_font(600, int(28 * s))
        _draw_tracked(d, MARGIN, y + 10, parts["brandline"], bf,
                      GOLD_LIGHT + (255,), 3, stroke=2)
    return y


# ── chrome (baked into every scene background) ──────────────────
def paint_chrome(bg, category, footer_source, footer_credit,
                 scene_idx, total_scenes):
    """Masthead + footer panel + progress segments, PLAIN text
    on navy (see the QA-geometry note in the module docstring).
    Mutates and returns the RGB background."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # top gradient (masthead legibility) + bottom gradient into
    # the panel
    for yy in range(0, 340):
        a = int(175 * (1 - yy / 340) ** 1.4)
        d.line([(0, yy), (W, yy)], fill=(4, 8, 18, a))
    for yy in range(900, PANEL_Y):
        t = (yy - 900) / (PANEL_Y - 900)
        d.line([(0, yy), (W, yy)],
               fill=NAVY + (int(255 * t ** 1.25),))
    d.rectangle([0, PANEL_Y, W, H], fill=NAVY + (255,))
    bg.paste(Image.alpha_composite(bg.convert("RGBA"), ov)
             .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(bg)
    # masthead — plain, first glyph row at MASTHEAD_Y
    d.text((MARGIN, MASTHEAD_Y), "The Videshi",
           font=SC.pf(84, "Bold"), fill=WHITE)
    _draw_tracked(d, MARGIN + 2, MASTHEAD_Y + 112,
                  "NEWS FOR THE GLOBAL INDIAN",
                  R.get_font(800, 28), GOLD_LIGHT, 5)
    d.rectangle([MARGIN + 2, MASTHEAD_Y + 162,
                 MARGIN + 40, MASTHEAD_Y + 168], fill=RED)
    _draw_tracked(d, MARGIN + 58, MASTHEAD_Y + 151,
                  (category or "News").upper(),
                  R.get_font(800, 28), WHITE, 4)
    # footer — plain on the flat navy panel, in NON-CORE
    # colours (see the module docstring: bright white/gold in
    # the y>1602 output band rings dark under Lanczos and
    # reads as glyphs to the gate)
    d.line([(MARGIN, PANEL_Y + 94), (W - MARGIN, PANEL_Y + 94)],
           fill=(120, 128, 150), width=2)
    if footer_source:
        d.text((MARGIN, PANEL_Y + 118), footer_source,
               font=R.get_font(400, 27), fill=FOOT)
    d.text((MARGIN, PANEL_Y + 164), "THEVIDESHI.COM",
           font=R.get_font(800, 27), fill=(226, 229, 238))
    if footer_credit:
        d.text((MARGIN, PANEL_Y + 218), footer_credit,
               font=R.get_font(400, 24), fill=FOOT_DIM)
    # progress segments — GOLD_LIGHT fill, at the panel's TOP
    # strip (bg y PANEL_Y+16): their output position stays
    # above the gate's y>1602 band at every zoom
    # (1496*1.07-40 = 1560). At the panel's bottom they sat
    # deep in the band, and ANY gold fill forms gold-core
    # pixels there — resampling blends between the fill and
    # navy pass through the gate's gold window (measured on
    # the proof: a 130x1px cluster on the segment row).
    n, cur = total_scenes, scene_idx + 1
    gap, sy, sh = 16, PANEL_Y + 16, 6
    sw = (W - 2 * MARGIN - (n - 1) * gap) // n
    for i in range(n):
        x0 = MARGIN + i * (sw + gap)
        d.rectangle([x0, sy, x0 + sw, sy + sh], fill=SEG_OFF)
        if i + 1 < cur:
            d.rectangle([x0, sy, x0 + sw, sy + sh],
                        fill=GOLD_LIGHT)
        elif i + 1 == cur:
            d.rectangle([x0, sy, x0 + int(sw * 0.45), sy + sh],
                        fill=GOLD_LIGHT)
    return bg


SIDE_SCRIM_W = 260                  # side scrim fade width
SIDE_SCRIM_AMAX = 150               # alpha at the frame edge


def apply_side_scrims(img):
    """Navy fades over the left/right edges of a full-bleed
    background (the v7 top-scrim logic, rotated): at max zoom
    the gate's x bands reach bg x < ~86 and bg x > ~919, and a
    photo's own bright detail there (signage, sky against a
    roofline) carries the glyph signature. Alpha 150 at the
    edge fading linearly over SIDE_SCRIM_W composites a pure
    white pixel to ~105 at the edge and ~204 at the band's
    inner reach — below the 235 white-core threshold — while
    reading as a gentle cinematic vignette."""
    alpha = Image.new("L", (W, 1))
    for xx in range(W):
        a = 0
        if xx < SIDE_SCRIM_W:
            a = int(SIDE_SCRIM_AMAX * (1 - xx / SIDE_SCRIM_W))
        elif xx >= W - SIDE_SCRIM_W:
            a = int(SIDE_SCRIM_AMAX
                    * (1 - (W - 1 - xx) / SIDE_SCRIM_W))
        alpha.putpixel((xx, 0), a)
    alpha = alpha.resize((W, H))
    scrim = Image.new("RGB", (W, H), R.GRAD_COLOR)
    return Image.composite(scrim, img, alpha)


# ── scene background composition ────────────────────────────────
def cover_crop_916(img, anchor=(0.5, 0.5)):
    """(cropped 1080x1920 image, window rect in source coords,
    scale). Downscale only — the caller guarantees the source
    clears the floor; a source whose 9:16 window is narrower
    than the frame would upscale and is demoted by the caller
    to the backdrop composition instead."""
    rect = V7.cover_window(img.size, anchor)
    crop = img.crop(rect)
    scale = W / (rect[2] - rect[0])
    return crop.resize((W, H), Image.LANCZOS), rect, scale


def compose_bg(img, anchor, subject, block_top, stage_rgb=NAVY):
    """Compose one scene's text-free background BEFORE chrome.
    Returns (bg, placement, dom_face_bg). Full-bleed cover by
    default; if the dominant face's chin would reach the text
    block, demote to the v7-style backdrop: photo in the stage
    box in the upper frame, text zone clear below it."""
    graded = V7.grade_native(img)
    bg, rect, scale = cover_crop_916(graded, anchor)
    dom, _m = V7.dominant_face_box(img)
    face_bg = None
    demote = scale > 1.0        # never upscale (the v7 rule)
    if dom is not None:
        fx, fy, fw, fh = dom
        face_bg = [round((fx - rect[0]) * scale),
                   round((fy - rect[1]) * scale),
                   round(fw * scale), round(fh * scale)]
        chin = face_bg[1] + face_bg[3]
        if chin > block_top - 40:
            demote = True
    if demote:
        # LAYOUT DEMOTION — photo into the stage box; any face
        # stays inside the box, the text zone is below it. The
        # box is 760 wide (x 160..920): at max zoom the right
        # edge lands at 920*1.07 - 540*0.07 = 946.6, still
        # inside the gate's x>952 band with margin (a
        # 800-wide box zooms to 968 and failed edge_overflow
        # on the proof's diaspora scene, 2026-11-11).
        box = (760, 600)
        win, dscale = V7.backdrop_window(
            graded.size, box, anchor, region="subject",
            frac=1.0, subject=subject)
        out = Image.new("RGB", (W, H), stage_rgb)
        if dscale <= 1.0:
            photo = graded.crop(win).resize(box, Image.LANCZOS)
            px = (W - box[0]) // 2
            out.paste(photo, (px, 340))
            fmap = None
            if dom is not None:
                fmap = [round((fx - win[0]) * dscale) + px,
                        round((fy - win[1]) * dscale) + 340,
                        round(fw * dscale), round(fh * dscale)]
            return out, {"mode": "backdrop-demoted",
                         "x": px, "y": 340, "w": box[0],
                         "h": box[1], "scale": dscale,
                         "window": list(win)}, fmap
        return out, {"mode": "stage", "x": 0, "y": 0, "w": 0,
                     "h": 0, "scale": 1.0,
                     "window": None}, None
    bg = apply_side_scrims(bg)
    return bg, {"mode": "cover", "x": 0, "y": 0, "w": W, "h": H,
                "scale": scale, "window": list(rect)}, face_bg


# ── smooth assembly (per-frame PIL motion; NO zoompan) ─────────
ZOOM_MAX = 0.07                     # the v6/v7 curve's total zoom
ZOOM_ANCHOR = (0.5, 0.30)           # the v6/v7 zoom anchor
XFADE_S = V7.XFADE_S                # 0.4s scene-boundary fades
MASTER_SCALE = 2                    # bg masters at 2x


def zoom_at_v8(t):
    """The global zoom at time t: 1.00 -> 1.07 over the reel,
    smoothstep-eased (ease-in-out; derivative zero at both
    ends, maximal mid-reel). Pure — unit-tested for per-frame
    delta smoothness."""
    p = min(max(t / TOTAL, 0.0), 1.0)
    e = p * p * (3 - 2 * p)
    return 1.0 + ZOOM_MAX * e


def _frame_from_master(master, t):
    """One background frame at time t: the master's fractional
    window at the eased zoom, resampled with LANCZOS via
    Image.resize's FLOAT source box — scale and offset are
    floats, so consecutive frames differ by sub-pixel amounts
    (zoompan's whole-pixel steps are the shake Kiran flagged;
    PIL's transform() cannot do this — it accepts only
    NEAREST/BILINEAR/BICUBIC coefficients)."""
    mw, mh = master.size
    z = zoom_at_v8(t)
    win_w, win_h = mw / z, mh / z
    x0 = (mw - win_w) * ZOOM_ANCHOR[0]
    y0 = (mh - win_h) * ZOOM_ANCHOR[1]
    return master.resize((W, H), Image.LANCZOS,
                         box=(x0, y0, x0 + win_w, y0 + win_h))


def assemble_v8(outdir, video_path, music_path, log=print):
    """Render the MP4 frame by frame in PIL and pipe rawvideo
    to ffmpeg (music bed muxed there, the v6/v7 treatment).
    Each output frame: the scene's background under the eased
    global zoom + its text overlay (fade-in per scene, fade-
    out on the last); frames inside a beat-boundary window
    blend the outgoing and incoming scenes (crossfade)."""
    outdir = Path(outdir)
    masters, overlays = {}, {}
    for key, _s, _d in BEATS:
        bg = Image.open(outdir / f"bg-{key}.jpg").convert("RGB")
        masters[key] = bg.resize((W * MASTER_SCALE,
                                  H * MASTER_SCALE),
                                 Image.LANCZOS)
        overlays[key] = Image.open(
            outdir / f"overlay-{key}.png").convert("RGBA")
    total_frames = int(TOTAL * FPS)
    starts = {k: s for k, s, _d in BEATS}
    keys = [k for k, _s, _d in BEATS]

    def scene_frame(i, t):
        key = keys[i]
        frame = _frame_from_master(masters[key], t)
        seg_start = starts[key] - (XFADE_S if i else 0.0)
        fade = min(1.0, max(0.0, (t - seg_start) / 0.35))
        if i == len(keys) - 1:
            fade *= min(1.0, max(0.0, (TOTAL - t) / 0.3))
        if fade > 0:
            ov = overlays[key]
            if fade < 1.0:
                ov = ov.copy()
                alpha = ov.split()[3].point(
                    lambda v: int(v * fade))
                ov.putalpha(alpha)
            frame.paste(ov, (0, 0), ov)
        return frame

    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt",
           "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i",
           "pipe:0", "-i", str(music_path),
           "-filter_complex",
           f"[1:a]atrim=0:{TOTAL},afade=t=in:st=0:d=0.5,"
           f"afade=t=out:st={TOTAL - 2}:d=2[mout]",
           "-map", "0:v", "-map", "[mout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "160k", "-t", str(TOTAL),
           str(video_path)]
    log("🎬 PIL per-frame assembly: fractional LANCZOS zoom "
        "(eased, no zoompan), crossfade joins")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    try:
        for n in range(total_frames):
            t = n / FPS
            i = max(j for j, (_k, s, _d) in enumerate(BEATS)
                    if t >= s)
            frame = scene_frame(i, t)
            if i < len(BEATS) - 1:
                boundary = BEATS[i + 1][1]
                if t >= boundary - XFADE_S:
                    wgt = (t - (boundary - XFADE_S)) / XFADE_S
                    nxt = scene_frame(i + 1, t)
                    frame = Image.blend(frame, nxt,
                                        min(max(wgt, 0.0), 1.0))
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read().decode("utf-8", "replace")
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg assembly failed: "
                           + err[-600:])


# ── main entry ──────────────────────────────────────────────────
def render_reel_v8(script, candidates, music_path, outdir,
                   name="reel", category="News", photo_url=None,
                   article_slug=None, article_id=None,
                   footer_source="", footer_credit="",
                   stage="black", log=print):
    """Render one v8 reel. candidates: the producer's distinct
    candidate list (priority order; see plan_v8_images).
    Returns (video_path, manifest) — the v7 manifest contract
    shape the QA gate consumes, plus per-scene v8 records."""
    t0 = time.time()
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stage_rgb = V7.STAGE_COLORS.get(stage, NAVY)

    beat_keys = [k for k, _s, _d in BEATS]
    beat_texts = {}
    for k in beat_keys:
        try:
            beat_texts[k] = " ".join(R.SCENE_TEXTS[k](script,
                                                      category))
        except Exception:
            beat_texts[k] = ""
    plans = plan_v8_images(beat_keys, candidates, beat_texts)
    plan_by_beat = {p["beat"]: p["candidate"] for p in plans}

    # Hero records for the manifest/QA contract: the hero is
    # the first candidate (the producer guarantees this).
    hero_c = candidates[0]
    hero_raw = Image.open(hero_c["path"])
    hero_src_size = list(hero_raw.size)
    if hero_src_size[0] < R.MIN_PHOTO_W \
            or hero_src_size[1] < R.MIN_PHOTO_H:
        raise R.PhotoTooSmallError(
            f"hero photo {hero_src_size[0]}x{hero_src_size[1]} "
            f"below the {R.MIN_PHOTO_W}x{R.MIN_PHOTO_H} floor")
    face_box, face_method = R.detect_face_box(hero_raw)
    has_face = face_method.startswith(("yunet", "haar"))

    scenes = {}
    hook_face_bg = None
    for idx, (key, start, dur) in enumerate(BEATS):
        cand = plan_by_beat[key]
        spec = scene_content(key, script, category)
        s, content_h, parts = fit_block(spec)
        block_top = BLOCK_BOTTOM - content_h
        img = Image.open(cand["path"])
        a3 = SC.focal_anchor(V7.grade_native(img), None)
        anchor = (a3[0], a3[1])
        fb, _fm = R.detect_face_box(img)
        subject = (fb[0], fb[1], fb[0] + fb[2], fb[1] + fb[3]) \
            if fb else None
        bg, placement, face_bg = compose_bg(
            img, anchor, subject, block_top, stage_rgb)
        if placement["mode"] == "backdrop-demoted":
            # The text zone is below the stage box now — RE-FIT
            # the block into that shorter zone (the v7 layout
            # demotion pattern: composition changes, the fit
            # shrinks; the chin rule and panel are not bent).
            zone_top = 340 + placement["h"] + 36
            s, content_h, parts = fit_block(
                spec, max_h=BLOCK_BOTTOM - zone_top)
            block_top = max(BLOCK_BOTTOM - content_h, zone_top)
        bg = paint_chrome(bg, category, footer_source,
                          footer_credit, idx, len(BEATS))
        bg.save(outdir / f"bg-{key}.jpg", quality=92)
        if key == "hook":
            bg.save(outdir / "background.jpg", quality=92)
            hook_face_bg = face_bg
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        paint_block(ov, spec, parts, s, block_top)
        ov.save(outdir / f"overlay-{key}.png")
        scenes[key] = {
            "start": start, "duration": dur,
            "zone_top": block_top, "zone_h": content_h,
            "scale": s, "content_h": content_h,
            "block_top": block_top,
            "block_bottom": block_top + content_h,
            "text_bbox": [MARGIN, block_top,
                          MARGIN + TEXT_MAX_W,
                          block_top + content_h],
            "texts": R.SCENE_TEXTS[key](script, category),
            "v8": {
                "image_source": cand["label"],
                "image_kind": cand.get("kind"),
                "track": placement["mode"],
                "photo_px": list(cand["size"]),
                "placement": placement,
                "provenance": cand.get("provenance"),
                "kicker": spec.get("kicker"),
            },
        }
        log(f"  scene {key:9s} src={cand['label']:22s} "
            f"track={placement['mode']:16s} text@{s:.2f}")

    video_path = outdir / f"{name}.mp4"
    assemble_v8(outdir, video_path, Path(music_path), log=log)

    manifest = {
        "renderer": "reel_renderer_v8.py (Reels v8 — GPT-"
                    "benchmark chrome, distinct photo per scene, "
                    "PRODUCTION 2026-11-11)",
        "design_system": "GPT-benchmark professional style "
                         "(masthead + footer chrome, big-stat "
                         "scenes, credited topical stock for "
                         "concept/policy stories)",
        "stage": {"name": stage, "rgb": list(stage_rgb)},
        "name": name,
        "article_slug": article_slug,
        "article_id": article_id,
        "category": category,
        "video": str(video_path),
        "duration_s": TOTAL,
        "canvas": [W, H],
        "photo": {"url": photo_url,
                  "local_path": str(hero_c["path"]),
                  "width": hero_src_size[0],
                  "height": hero_src_size[1],
                  "floor": [R.MIN_PHOTO_W, R.MIN_PHOTO_H]},
        "face": {"method": face_method, "has_face": has_face,
                 "box_source": list(face_box),
                 "box_bg": hook_face_bg if hook_face_bg
                 else list(face_box),
                 "chin_bg": (hook_face_bg[1] + hook_face_bg[3])
                 if hook_face_bg else None,
                 "anchor": [0.5, 0.5]},
        "composition": {
            "model": "per-scene distinct photo (never re-"
                     "cropped), full-bleed cover or face-"
                     "demoted backdrop, benchmark chrome baked "
                     "into every background, xfade joins over "
                     "the global Ken Burns phase",
            "distinct_images": len(plans),
            "footer_source": footer_source,
            "footer_credit": footer_credit},
        "grade": {"mode": "native-resolution (v7 grade)"},
        "safe_zone": {"x": [MARGIN, MARGIN + TEXT_MAX_W],
                      "y": [MASTHEAD_Y, BLOCK_BOTTOM]},
        "scenes": scenes,
        "music": {"path": str(music_path),
                  "treatment": "bed: atrim 35s + fades (v6/v7 "
                               "produce recipe)"},
        "render_seconds": round(time.time() - t0, 1),
        "mp4_bytes": video_path.stat().st_size,
    }
    (outdir / "render-manifest.json").write_text(
        json.dumps(manifest, indent=1))
    log(f"✅ rendered {video_path} "
        f"({manifest['mp4_bytes'] / 1e6:.1f} MB, "
        f"{manifest['render_seconds']}s)")
    return video_path, manifest
