#!/usr/bin/env python3
"""
social_card.py — The Videshi social-card generator (1080x1350, 4:5).

Dual-track design, approved by Kiran 2026-10-24 from the design study in
~/workspace/research_notes/social-card-design-2026-10-24/ (samples A-D are
the visual spec):

  FULL-BLEED  — only when the fetched source ORIGINAL is >=1920px wide
                AND the 4:5 cover-crop needs no upscale. Photo fills the
                frame; white Playfair headline over a smooth full-frame
                bottom gradient; spaced-caps kicker over a thin RED rule;
                tiny "V." mark top-left. (Sample A)
  BACKDROP    — everything else. Photo at native scale (NEVER enlarged)
                on a solid NAVY #0B1D3A stage (black option for breaking
                cards); gold kicker + gold rule + Playfair headline laid
                out in the backdrop zone; "THE VIDESHI" chip on the photo.
                (Sample C)

The core rule is NEVER UPSCALE: a 1200-1500px hero blown to a 4:5
full-bleed needs a ~1.9x upscale and goes soft; on a backdrop the same
photo renders at a downscale and stays crisp. The track gate is keyed to
the fetched ORIGINAL (Wikimedia thumb -> original, NASA ~large -> ~orig,
Pexels params dropped — reel_produce.original_url), not the stored rung.

Usage:
  set -a; source ~/workspace/.env.supabase; set +a
  python3 social_card.py --slug <slug> [--out card.png]
  python3 social_card.py --id <uuid>
  python3 social_card.py --headline "..." --category technology \
      --image-url https://... [--backdrop navy|black]

Prints one JSON line: {track, source_px, render_scale, out_path, ...}.
Importable: make_card(headline, category, image_url=...|image_path=...).

SKIP RULE: if the best available image (after the original-upgrade
fetch) is <600px wide, make_card renders nothing and returns
{track: "skipped", reason: "hero_under_600px", source_px: [w, h]} —
callers (the social queue producers) fall back to the plain-hero
post. --track overrides the skip, for testing.
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# cv2 (focal/face detection) lives in the pipeline-local pylibs dir.
for _p in (HERE / ".pylibs",):
    if _p.exists() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from PIL import Image, ImageDraw, ImageFont, ImageOps  # noqa: E402

try:
    from reel_produce import original_url as _original_url
except Exception as _e:  # pragma: no cover - env guard
    print(f"social_card: original_url import failed ({_e}); "
          "no URL upgrade will be applied", file=sys.stderr)

    def _original_url(url):
        return url


# ── Canvas / brand ────────────────────────────────────────────────────
W, H = 1080, 1350
M = 64                       # side margin
CW = W - 2 * M               # content width (952)
NAVY = (11, 29, 58)          # #0B1D3A
GOLD = (212, 168, 67)        # #D4A843
RED = (163, 45, 47)          # #A32D2F
WHITE = (255, 255, 255)
BLACK = (5, 5, 5)
BACKDROPS = {"navy": NAVY, "black": BLACK}

GATE_MIN_WIDTH = 1920        # full-bleed gate: fetched-original width
SKIP_MIN_WIDTH = 600         # skip rule: best image under this width
                             # renders NO card (callers fall back to
                             # the plain-hero post)
MAX_PHOTO_H = 880            # backdrop: photo never eats the text zone
HEADLINE_START = 62
HEADLINE_FLOOR = 42
LINE_RATIO = 1.16
KICKER_SIZE = 30
KICKER_TRACKING = 11
# text-block internal geometry (matches the approved samples)
KICKER_TO_RULE = 52
RULE_W, RULE_H = 72, 7
RULE_TO_HEADLINE = 34
BLOCK_FIXED_H = KICKER_TO_RULE + RULE_H + RULE_TO_HEADLINE  # 93
ZONE_TOP_GAP = 56
ZONE_BOTTOM_MARGIN = 48

FONT_DIR = HERE / "reels" / "fonts-local"
PLAYFAIR = FONT_DIR / "PlayfairDisplay-Bold.ttf"
INTER_700 = FONT_DIR / "Inter-700.ttf"
INTER_800 = FONT_DIR / "Inter-800.ttf"

CACHE_DIR = HERE / ".state" / "social-card-cache"
DEFAULT_OUT_DIR = HERE / ".state" / "social-cards"

CATEGORY_LABELS = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "technology": "TECHNOLOGY",
    "entertainment": "ENTERTAINMENT",
    "sports": "SPORTS",
    "markets-finance": "MARKETS & FINANCE",
    "nri-world": "NRI WORLD",
    "food": "FOOD",
    "travel": "TRAVEL",
    "lifestyle-health": "LIFESTYLE & HEALTH",
}


def kicker_for(category):
    """Category slug -> spaced-caps kicker label."""
    key = (category or "").strip().lower()
    if key in CATEGORY_LABELS:
        return CATEGORY_LABELS[key]
    return key.replace("-", " ").upper() or "NEWS"


# ── Fonts ─────────────────────────────────────────────────────────────
def pf(size, weight="Bold"):
    f = ImageFont.truetype(str(PLAYFAIR), size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def inter(size, weight="700"):
    path = INTER_800 if weight == "800" else INTER_700
    return ImageFont.truetype(str(path), size)


# ── Text measuring (real font metrics, as the samples did) ───────────
def tracked_w(draw, text, font, tr):
    return sum(draw.textlength(ch, font=font) + tr for ch in text) - tr


def draw_tracked(draw, xy, text, font, tr, fill):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tr
    return x


def wrap(draw, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def _truncate_lines(draw, lines, font, maxw, max_lines):
    """Keep max_lines, ellipsise the last kept line to fit. -> (lines, True)"""
    kept = lines[:max_lines]
    last = kept[-1]
    while last and draw.textlength(last + "…", font=font) > maxw:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    kept[-1] = last + "…"
    return kept, True


def fit_headline(draw, text, maxw, max_lines, start=HEADLINE_START,
                 floor=HEADLINE_FLOOR):
    """Largest Playfair size whose wrap fits max_lines.
    Returns (font, lines, size, truncated). At the floor size, excess
    lines are truncated with an ellipsis and flagged — last resort only."""
    size = start
    while size > floor:
        f = pf(size, "Bold")
        lines = wrap(draw, text, f, maxw)
        if len(lines) <= max_lines:
            return f, lines, size, False
        size -= 2
    f = pf(floor, "Bold")
    lines = wrap(draw, text, f, maxw)
    if len(lines) <= max_lines:
        return f, lines, floor, False
    lines, _ = _truncate_lines(draw, lines, f, maxw, max_lines)
    return f, lines, floor, True


def block_height(n_lines, size):
    return BLOCK_FIXED_H + int(size * LINE_RATIO) * n_lines


# ── Brand marks ───────────────────────────────────────────────────────
def brand_mark_v(img):
    """Tiny 'V.' — white Playfair V, red dot (full-bleed track)."""
    d = ImageDraw.Draw(img)
    f = pf(58, "ExtraBold")
    d.text((52, 36), "V", font=f, fill=WHITE, stroke_width=1,
           stroke_fill=(0, 0, 0))
    wv = d.textlength("V", font=f)
    d.text((52 + wv + 2, 36), ".", font=f, fill=RED)


def brand_chip(img, x, y):
    """'THE VIDESHI' chip — navy pill, gold outline + gold tracked caps.
    Placed on the photo (backdrop track), per Sample C."""
    d = ImageDraw.Draw(img)
    f = inter(25, "800")
    label = "THE VIDESHI"
    tw = tracked_w(d, label, f, 6)
    box = (x, y, x + tw + 36, y + 52)
    d.rounded_rectangle(box, radius=10, fill=NAVY, outline=GOLD, width=2)
    draw_tracked(d, (x + 18, y + 12), label, f, 6, GOLD)


# ── Track gate ────────────────────────────────────────────────────────
def full_bleed_scale(w, h):
    """Render scale of the 4:5 cover-crop for a w x h source."""
    win_w = h * 0.8 if w >= h * 0.8 else w
    return W / win_w


def backdrop_fit(w, h):
    """(placed_w, placed_h, scale) for the photo on a backdrop:
    fit to canvas width, cap height at MAX_PHOTO_H, never upscale."""
    scale = min(W / w, 1.0)
    if h * scale > MAX_PHOTO_H:
        scale = MAX_PHOTO_H / h
    return int(w * scale), int(h * scale), scale


def choose_track(w, h):
    """(track, render_scale, note). The core rule: NEVER UPSCALE.
    Width gate >=1920 earns full-bleed only if the cover-crop itself
    also stays at scale <= 1.0 (a wide-but-short hero would still need
    an upscale of its centre slice — it is demoted to backdrop)."""
    if w >= GATE_MIN_WIDTH:
        s = full_bleed_scale(w, h)
        if s <= 1.0:
            return "full-bleed", s, None
        _, _, bs = backdrop_fit(w, h)
        return ("backdrop", bs,
                f"width gate passed ({w}px) but full-bleed cover-crop "
                f"would upscale {s:.2f}x — demoted to backdrop "
                f"(never upscale)")
    _, _, bs = backdrop_fit(w, h)
    return "backdrop", bs, None


# ── Focal / face anchor for the full-bleed crop ──────────────────────
def focal_anchor(img, img_bytes=None):
    """(fx, fy, method) in source fractions for the cover crop.
    Face-detected boxes (reel_renderer's YuNet-first detector) are
    exact and never damped; heuristic anchors are damped halfway
    toward centre per the house rule (2026-10-23)."""
    try:
        from reel_renderer import detect_face_box
        box, method = detect_face_box(img)
        if method.startswith(("yunet", "haar")):
            bx, by, bw, bh = box
            w, h = img.size
            return ((bx + bw / 2) / w, (by + bh / 2) / h,
                    f"face:{method}")
    except Exception:
        pass
    fx, fy = 0.5, 0.5
    method = "centre (no focal available)"
    try:
        if img_bytes is None:
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92)
            img_bytes = buf.getvalue()
        from focal_point import compute_focal_point
        fx, fy = compute_focal_point(img_bytes)
        from reel_renderer import damp_anchor
        fx, fy = damp_anchor(fx, fy)
        method = "focal-heuristic (damped 0.5)"
    except Exception:
        pass
    return fx, fy, method


def cover_crop(img, fx, fy):
    """4:5 cover crop anchored on (fx, fy); resized to canvas.
    Returns (image, scale). Caller guarantees scale <= ~1.0."""
    w, h = img.size
    if w >= h * 0.8:
        win_w, win_h = int(h * 0.8), h
        x0 = min(max(int(fx * w - win_w / 2), 0), w - win_w)
        y0 = 0
    else:
        win_w, win_h = w, int(w / 0.8)
        x0 = 0
        y0 = min(max(int(fy * h - win_h / 2), 0), h - win_h)
    scale = W / win_w
    cropped = img.crop((x0, y0, x0 + win_w, y0 + win_h))
    return cropped.resize((W, H), Image.LANCZOS), scale


# ── Shared text block ─────────────────────────────────────────────────
def draw_text_block(img, y_top, kicker, kicker_fill, rule_fill,
                    font, lines, size):
    d = ImageDraw.Draw(img)
    kf = inter(KICKER_SIZE, "700")
    draw_tracked(d, (M, y_top), kicker, kf, KICKER_TRACKING, kicker_fill)
    ry = y_top + KICKER_TO_RULE
    d.rectangle((M, ry, M + RULE_W, ry + RULE_H), fill=rule_fill)
    lh = int(size * LINE_RATIO)
    y = ry + RULE_TO_HEADLINE
    for ln in lines:
        d.text((M, y), ln, font=font, fill=WHITE)
        y += lh
    return y - y_top


def bottom_gradient(img, top_frac=0.42, max_alpha=228):
    """Smooth full-frame-width bottom gradient (Sample A) — a smooth
    ramp, never a localized scrim blob."""
    ov = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, (y / H - top_frac) / (1 - top_frac))
        ov.putpixel((0, y), int(max_alpha * (t ** 1.55)))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img.paste(Image.composite(black, img, ov.resize((W, H))), (0, 0))


# ── Track renderers ───────────────────────────────────────────────────
def render_full_bleed(img, headline, kicker, anchor=None):
    probe = ImageDraw.Draw(Image.new("RGB", (W, H)))
    font, lines, size, truncated = fit_headline(
        probe, headline, CW, max_lines=6, start=60)
    bh = block_height(len(lines), size)
    if anchor is None:
        anchor = focal_anchor(img)
    fx, fy, method = anchor
    card, scale = cover_crop(img, fx, fy)
    bottom_gradient(card)
    brand_mark_v(card)
    draw_text_block(card, H - 64 - bh, kicker, WHITE, RED,
                    font, lines, size)
    info = {"render_scale": round(scale, 4), "truncated": truncated,
            "headline_size": size, "headline_lines": len(lines),
            "focal": method}
    return card, info


def render_backdrop(img, headline, kicker, backdrop="navy"):
    color = BACKDROPS[backdrop]
    card = Image.new("RGB", (W, H), color)
    pw, ph, scale = backdrop_fit(*img.size)
    photo = img.resize((pw, ph), Image.LANCZOS) if (pw, ph) != img.size \
        else img.copy()
    px = (W - pw) // 2
    card.paste(photo, (px, 0))
    brand_chip(card, px + 48, 44)
    zone_top = ph
    zone_h = H - zone_top
    # Fit the headline against the real zone height.
    probe = ImageDraw.Draw(card)
    avail = zone_h - ZONE_TOP_GAP - ZONE_BOTTOM_MARGIN
    font = lines = None
    size, truncated = HEADLINE_START, False
    while size > HEADLINE_FLOOR:
        f = pf(size, "Bold")
        ls = wrap(probe, headline, f, CW)
        if block_height(len(ls), size) <= avail:
            font, lines = f, ls
            break
        size -= 2
    if font is None:
        size = HEADLINE_FLOOR
        font = pf(size, "Bold")
        lines = wrap(probe, headline, font, CW)
        max_lines = max(1, (avail - BLOCK_FIXED_H) // int(size * LINE_RATIO))
        if len(lines) > max_lines:
            lines, truncated = _truncate_lines(
                probe, lines, font, CW, max_lines)
    bh = block_height(len(lines), size)
    y0 = zone_top + max(ZONE_TOP_GAP, (zone_h - bh) // 2)
    kicker_fill = GOLD if backdrop == "navy" else WHITE
    rule_fill = GOLD if backdrop == "navy" else RED
    draw_text_block(card, y0, kicker, kicker_fill, rule_fill,
                    font, lines, size)
    info = {"render_scale": round(scale, 4), "truncated": truncated,
            "headline_size": size, "headline_lines": len(lines),
            "photo_px": [pw, ph], "focal": "n/a (no crop)"}
    return card, info


# ── Image acquisition ─────────────────────────────────────────────────
def _curl_download(url, dest):
    r = subprocess.run(
        ["curl", "-sSL", "-A", "TheVideshi/1.0", "--max-time", "120",
         "-o", str(dest), url],
        capture_output=True, text=True, timeout=150)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed for {url}: {r.stderr[:200]}")
    if not dest.exists() or dest.stat().st_size < 5000:
        raise RuntimeError(f"download too small for {url}")


def fetch_image(image_url):
    """Download the ORIGINAL upgrade of image_url (fallback: stored
    URL). Returns (PIL image RGB, fetched_url, raw_bytes)."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    upgraded = _original_url(image_url)
    last_err = None
    for url in dict.fromkeys([upgraded, image_url]):
        key = hashlib.sha1(url.encode()).hexdigest()[:16]
        dest = CACHE_DIR / f"{key}.img"
        try:
            if not dest.exists():
                _curl_download(url, dest)
            raw = dest.read_bytes()
            img = Image.open(io.BytesIO(raw))
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.load()
            return img, url, raw
        except Exception as e:
            last_err = e
            try:
                dest.unlink()
            except OSError:
                pass
    raise RuntimeError(f"could not fetch image {image_url}: {last_err}")


def load_local_image(image_path):
    raw = Path(image_path).read_bytes()
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.load()
    return img, raw


# ── Supabase article lookup (curl — urllib fails through the proxy) ──
def fetch_article(slug=None, article_id=None):
    base = os.environ["SUPABASE_URL"].rstrip("/")
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    filt = f"slug=eq.{slug}" if slug else f"id=eq.{article_id}"
    url = (f"{base}/rest/v1/p2_articles?{filt}"
           "&select=id,slug,headline,category,image_url")
    r = subprocess.run(
        ["curl", "-sS", url, "-H", f"apikey: {key}",
         "-H", f"Authorization: Bearer {key}"],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"supabase fetch failed: {r.stderr[:200]}")
    rows = json.loads(r.stdout)
    if not rows:
        raise RuntimeError(f"article not found: {slug or article_id}")
    return rows[0]


# ── Top level ─────────────────────────────────────────────────────────
def make_card(headline, category, image_url=None, image_path=None,
              out_path=None, backdrop="navy", force_track=None):
    """Render one card. Returns the info dict (also the CLI's JSON)."""
    if image_path:
        img, raw = load_local_image(image_path)
        fetched_url = None
    elif image_url:
        img, fetched_url, raw = fetch_image(image_url)
    else:
        raise ValueError("image_url or image_path required")
    src_w, src_h = img.size
    kicker = kicker_for(category)
    # SKIP RULE (Kiran, go-live 2026-10-24): if the best available
    # image — after the original-upgrade fetch above — is under
    # 600px wide, render nothing and report the skip; queue callers
    # fall back to the plain-hero post. force_track (--track) still
    # forces a render, for testing.
    if not force_track and src_w < SKIP_MIN_WIDTH:
        info = {"track": "skipped", "reason": "hero_under_600px",
                "source_px": [src_w, src_h], "out_path": None,
                "render_scale": None, "truncated": False,
                "kicker": kicker, "backdrop": None}
        if fetched_url:
            info["fetched_url"] = fetched_url
        return info
    if force_track:
        track = force_track
        if track == "full-bleed":
            _, note = full_bleed_scale(src_w, src_h), None
        else:
            note = None
        track_note = "forced via --track"
    else:
        track, _scale, track_note = choose_track(src_w, src_h)
    if track == "full-bleed":
        card, rinfo = render_full_bleed(
            img, headline, kicker, anchor=focal_anchor(img, raw))
    else:
        card, rinfo = render_backdrop(img, headline, kicker,
                                      backdrop=backdrop)
    if out_path is None:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        name = hashlib.sha1(headline.encode()).hexdigest()[:12]
        out_path = str(DEFAULT_OUT_DIR / f"card-{name}.png")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    card.save(out_path, "PNG")
    info = {
        "track": track,
        "source_px": [src_w, src_h],
        "render_scale": rinfo["render_scale"],
        "out_path": str(out_path),
        "truncated": rinfo["truncated"],
        "headline_size": rinfo["headline_size"],
        "headline_lines": rinfo["headline_lines"],
        "kicker": kicker,
        "backdrop": backdrop if track == "backdrop" else None,
        "focal": rinfo["focal"],
    }
    if track_note:
        info["track_note"] = track_note
    if fetched_url:
        info["fetched_url"] = fetched_url
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--slug")
    ap.add_argument("--id", dest="article_id")
    ap.add_argument("--headline")
    ap.add_argument("--category")
    ap.add_argument("--image-url")
    ap.add_argument("--image-path")
    ap.add_argument("--out")
    ap.add_argument("--backdrop", choices=sorted(BACKDROPS),
                    default="navy")
    ap.add_argument("--track", choices=["full-bleed", "backdrop"],
                    default=None, help="override the width gate (testing)")
    args = ap.parse_args(argv)

    headline, category = args.headline, args.category
    image_url, slug = args.image_url, args.slug
    if args.slug or args.article_id:
        art = fetch_article(slug=args.slug, article_id=args.article_id)
        headline = headline or art["headline"]
        category = category or art["category"]
        image_url = image_url or art["image_url"]
        slug = art["slug"]
    if not headline or not category or not (image_url or args.image_path):
        ap.error("need --slug/--id, or --headline + --category + "
                 "--image-url/--image-path")
    out = args.out
    if out is None and slug:
        DEFAULT_OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = str(DEFAULT_OUT_DIR / f"{slug}.png")
    info = make_card(headline, category, image_url=image_url,
                     image_path=args.image_path, out_path=out,
                     backdrop=args.backdrop, force_track=args.track)
    if slug:
        info["slug"] = slug
    print(json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
