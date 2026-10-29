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

CARD SETS (make_card_set, Kiran's format map 2026-10-24 — card
carousels for Threads / X / Facebook): an ordered set of 2-4 cards —
the hook card (make_card) + up to 2 key-takeaway cards + a closer
card, all in the Sample C navy/gold system. X's 4-image cap is the
binding constraint, so ONE set serves all three surfaces. A skipped
hook (<600px) means no set at all; surfaces fall back to today's
single-image behavior. Each middle card carries its OWN picture,
sourced for that card's subject (Kiran's cross-format doctrine,
2026-10-25 — the Reels v7 per-scene model applied to decks): the
article's inline body images in order, else the ENTITY-SOURCING
ladder (reel_entity_sourcing: Commons -> official -> Brave
discovery, license-gated, provenance recorded), else a plain navy
text card. The hero appears ONLY on the hook card and no image is
ever rendered twice in one deck. Theme-gated per card — never
upscaled.
"""

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.parse
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


_INTER_FILES = {"400": "Inter-400.ttf", "600": "Inter-600.ttf",
                "700": "Inter-700.ttf", "800": "Inter-800.ttf"}


def inter(size, weight="700"):
    path = FONT_DIR / _INTER_FILES.get(str(weight), "Inter-700.ttf")
    if not path.exists():
        path = INTER_700
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
def render_full_bleed(img, headline, kicker, anchor=None,
                      fit_start=60, fit_floor=HEADLINE_FLOOR,
                      fit_max_lines=6):
    probe = ImageDraw.Draw(Image.new("RGB", (W, H)))
    font, lines, size, truncated = fit_headline(
        probe, headline, CW, max_lines=fit_max_lines,
        start=fit_start, floor=fit_floor)
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


def render_backdrop(img, headline, kicker, backdrop="navy",
                    fit_start=HEADLINE_START, fit_floor=HEADLINE_FLOOR):
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
    size, truncated = fit_start, False
    while size > fit_floor:
        f = pf(size, "Bold")
        ls = wrap(probe, headline, f, CW)
        if block_height(len(ls), size) <= avail:
            font, lines = f, ls
            break
        size -= 2
    if font is None:
        size = fit_floor
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
           "&select=id,slug,headline,subheadline,category,image_url,"
           "key_takeaways,body")
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


# ── Card sets: takeaway cards + closer (Sample C system) ─────────────
MAX_SET_TAKEAWAYS = 2        # hook + 2 middles + closer = 4 (X's cap)
TAKEAWAY_START = 58
TAKEAWAY_FLOOR = 34
MARKER_FILL = (168, 180, 198)
SUBTLE_FILL = (166, 178, 198)

_IMG_SRC_RE = re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.I)
_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)\)")


def extract_inline_images(body):
    """Image URLs embedded in an article body, in document order.

    Sources: HTML <img src> (the writer wraps them in <figure>) and
    markdown ![..](url). These images already passed the image
    sourcer's relevance/identity gates and sit near the text they
    illustrate — the only approved pool for per-card backgrounds."""
    if not body:
        return []
    found = [(m.start(), m.group(1)) for m in _IMG_SRC_RE.finditer(body)]
    found += [(m.start(), m.group(1)) for m in _MD_IMG_RE.finditer(body)]
    found.sort(key=lambda t: t[0])
    out, seen = [], set()
    for _pos, url in found:
        url = url.strip()
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def _img_filename(url):
    name = (url or "").split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    return re.sub(r"^\d+px-", "", name).lower()


def _same_image(a, b):
    """True when two URLs point at the same underlying image —
    exact match, or a Wikimedia-style thumbnail variant (the thumb
    URL's final segment is '<width>px-<original filename>')."""
    if not a or not b:
        return False
    if a == b:
        return True
    fa, fb = _img_filename(a), _img_filename(b)
    return bool(fa) and fa == fb


def _elog(msg):
    """Deck-build diagnostics go to stderr: stdout carries the
    CLI's single JSON line, and queue producers import this
    module."""
    print(f"social_card: {msg}", file=sys.stderr)


# ── Per-card entity sourcing (the Reels v7 ladder, adapted) ──────
ENTITY_CACHE_DIR = CACHE_DIR / "entity"
MAX_CARD_ENTITIES = 3


_BRAND_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z&.'-]*")


# An entity may not BEGIN or END on a function word: those are
# phrase fragments, not names ('For Indian' out of 'For Indian
# workers…' sourced wildlife photos for an H-1B deck,
# 2026-10-28). Same hygiene the article picture pass shipped
# 2026-10-26.
_EDGE_STOPWORDS = {"the", "a", "an", "of", "in", "on", "at",
                   "to", "and", "for", "by", "with", "from"}


def _card_entity_hygiene(e):
    """Why this card entity may never be sourced, or None:
    phrase fragments (edge stopwords), possessive forms, and
    news outlets (sources, never picture subjects)."""
    if not e:
        return "empty entity"
    # Sentence-boundary span (the article pass's rule, same
    # masking): 'GeekWire. Microsoft' is two fragments glued
    # by a period, not a name.
    probe = re.sub(r"\b(?:Dr|Mr|Mrs|Ms|St|Prof|Sr|Jr|Mt|Ft|"
                   r"Gen|Sen|Rep|Gov|Capt|Lt|Col)\.", "X", e)
    probe = re.sub(r"\b[A-Z]\.", "X", probe)
    if re.search(r"[.!?]\s+[A-Za-z]", probe):
        return ("spans a sentence boundary — a fragment, "
                "not a name")
    toks = e.split()
    if toks:
        first = toks[0].strip(".,'’-").lower()
        last = toks[-1].strip(".,'’-").lower()
        if first in _EDGE_STOPWORDS or last in _EDGE_STOPWORDS:
            return ("begins or ends on a stopword — a phrase "
                    "fragment, not a name")
        if toks[-1].lower().endswith(("'s", "’s")):
            return "a possessive form — not a name"
    try:
        import picture_gate_shared as _G
        if _G.is_outlet_entity(e):
            return ("a news outlet — a source, never a picture "
                    "subject")
    except Exception:
        pass
    return None


def _card_entities(text, article_ctx):
    """Picture-worthy entities for ONE takeaway card, best first:
    the card's OWN subjects in text order — capitalized phrases
    (_PHRASE_RE) plus mixed-case brand tokens the phrase regex
    misses (IndiGo, YouTube, WhatsApp carry an internal capital)
    — then the article's entities from reel_entity_sourcing's
    extractor, ranked by token overlap with the card text.
    Article-level entities with zero overlap stay as honest
    fallbacks."""
    import reel_entity_sourcing as res
    seen = set()
    own = []

    def add(e, bucket):
        e = res._clean_entity(e)
        if e and e.lower() not in seen:
            if _card_entity_hygiene(e):
                return
            seen.add(e.lower())
            bucket.append(e)

    hits = [(m.start(), m.group(0))
            for m in res._PHRASE_RE.finditer(text or "")]
    for m in _BRAND_TOKEN_RE.finditer(text or ""):
        tok = m.group(0)
        if any(ch.isupper() for ch in tok[1:]):
            hits.append((m.start(), tok))
    for _pos, e in sorted(hits):
        add(e, own)
    art = []
    for e in res.extract_entities(article_ctx, None):
        add(e, art)
    toks = set(res._tokens(text))

    def overlap(e):
        return sum(1 for t in res.entity_tokens(e) if t in toks)

    art.sort(key=lambda e: -overlap(e))
    return own + art


_NON_PHOTO_RE = re.compile(
    r"\b(maps?|diagrams?|charts?|graphs?|logos?|destinations|"
    r"routes|timetable|flags?|coat of arms|screenshots?|"
    r"blank document)\b", re.I)


def _card_photo_ok(cand):
    """Cards carry PHOTOGRAPHS of the entity. The ladder's gates
    reject map fragments in descriptions, but a whole-file graphic
    whose subject IS a map/diagram (e.g. an airline's destinations
    map) still passes them — useless as a card picture, so the
    adapter skips it by title and keeps scanning. UI screenshots
    are the same class: a blank Google Docs page passed every
    ladder gate for 'Google Services' (2026-10-28) — the check
    therefore also scans the candidate's subject/description
    text, where a screenshot declares itself."""
    return not _NON_PHOTO_RE.search(
        f"{cand.get('title') or ''} {cand.get('subject') or ''}")


def _download_entity_image(url):
    """Download an entity-sourced file into the card cache and
    load it. Returns (img, raw) like load_local_image."""
    import reel_entity_sourcing as res
    ENTITY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    dest = ENTITY_CACHE_DIR / f"{key}.img"
    if not dest.exists():
        res.download_file(url, dest)
    return load_local_image(dest)


def _entity_image_for_card(text, article_ctx, used, log=None):
    """Source ONE picture for a takeaway card's own subject via
    the Reels v7 entity ladder (reel_entity_sourcing — Kiran's
    cross-format doctrine, 2026-10-25, proven on the Infosys
    reel): Route A Wikimedia Commons originals, Route B official
    sources, Route C Brave discovery -> Commons. Every candidate
    passes the ladder's gates at its hosting page (provably the
    entity, license clean CC/PD with attribution, true dimensions
    at the file) and must not duplicate an image already in the
    deck (`used` — the hero included).

    Returns (img, raw, prov) with prov = {entity, route,
    source_page, file_url, license, artist, bg_px}, or None on an
    honest miss (logged). NEVER raises."""
    log = log or _elog
    try:
        import reel_entity_sourcing as res
    except Exception as e:
        log(f"entity sourcing unavailable ({e})")
        return None
    used = [u for u in (used or []) if u]

    def is_used(url):
        return any(_same_image(url, u) for u in used)

    try:
        entities = _card_entities(text, article_ctx)
    except Exception as e:
        log(f"entity extraction failed ({e})")
        return None
    if not entities:
        log("entity sourcing: no entities for this card — navy")
        return None
    hint = ""
    try:
        hint = res.topical_hint(article_ctx, entities)
    except Exception:
        pass
    # ── Story context (2026-10-29, Kiran's go): the shared
    # identity gates in reel_entity_sourcing are INERT without
    # a context — context_reject_reason returns None on a falsy
    # context, so every deck sourced namesakes the reel/article
    # gates had already killed (Campagnolo bike brakes for
    # 'EPS', an actress for 'NSE', Gaisano Capital mall photos
    # for 'Spark Capital', foreign supreme courts for India's).
    # Build the context exactly as the reel sourcer does: the
    # article plus a script stub carrying this card's text and
    # the card's entities as its key entities.
    context = None
    try:
        context = res.build_story_context(
            article_ctx,
            {"key_entities": entities, "news_summary": text},
            entities)
    except Exception as e:
        log(f"entity sourcing: story context build failed ({e})")
    # Vocabulary for the single-token agreement gate below:
    # the headline + this card's text + the article's LEDE
    # (first ~600 chars) + the deck's entities — what THIS
    # card is actually about. The full body is deliberately
    # NOT scanned: a long window mentions too much of the
    # world, and coincidence is the failure being gated; the
    # lede carries the story's own summary vocabulary (the
    # Microsoft campus keeper agrees via its lede's 'United
    # States'). Tokens are compared in a light singular form
    # ('stocks' ~ 'stock') — the live smoke test showed the
    # exchanges' own building photos dying on that plural.
    def _aform(w):
        return w[:-1] if len(w) > 3 and w.endswith("s") \
            and not w.endswith("ss") else w

    agree_base = set()
    try:
        import picture_gate_shared as _G
        raw_ctx = " ".join([article_ctx.get("headline") or "",
                            text or "",
                            (article_ctx.get("body") or "")
                            [:600]])
        for w in re.findall(r"[a-z0-9]+", raw_ctx.lower()):
            if len(w) >= 4 and not w.isdigit() \
                    and w not in _G.HINT_FUNCTION_WORDS:
                agree_base.add(_aform(w))
        for e in entities:
            for t in res.entity_tokens(e):
                if len(t) >= 4:
                    agree_base.add(_aform(t))
    except Exception:
        agree_base = set()

    def accept(entity, c, page=None):
        """Card-level acceptance on top of the ladder's gates:
        a real photograph, not already in the deck, and — for a
        SINGLE-TOKEN entity — at least one story-context token
        in the candidate's own evidence. One token is coincidence
        bait on Commons ('EPS' the earnings metric vs Campagnolo
        EPS bike brakes; 'NSE' the exchange vs actress Nse
        Ikpe-Etim): identity alone cannot tell them apart, but
        a genuine file's page talks about the story's world and
        a namesake's never does. The evidence includes the
        file's Commons categories when the caller has the raw
        page: an exchange's own building is filed under the
        exchange's full name ('National Stock Exchange of
        India'), which is exactly the agreement that counts."""
        if c is None:
            return False
        if not _card_photo_ok(c):
            log(f"entity sourcing: skipped non-photo graphic "
                f"for {entity}: {(c['title'] or '')[:60]}")
            return False
        if is_used(c["file_url"]):
            return False
        if len(entity.split()) == 1 and agree_base:
            ev_text = f"{c.get('title') or ''} " \
                      f"{c.get('subject') or ''}"
            if page is not None:
                try:
                    info = (page.get("imageinfo") or [{}])[0]
                    ev_text += " " + res._meta(
                        info, "ImageDescription") + " " \
                        + res._meta(info, "Categories")
                except Exception:
                    pass
            ev = {_aform(w) for w in re.findall(
                r"[a-z0-9]+", ev_text.lower()) if len(w) >= 4}
            ev -= {_aform(t) for t in res.entity_tokens(entity)}
            if not (ev & (agree_base
                          - {_aform(t) for t
                             in res.entity_tokens(entity)})):
                log(f"entity sourcing: single-token entity "
                    f"{entity!r} candidate shares no story "
                    f"token — skip: {(c['title'] or '')[:60]}")
                return False
        return True

    for entity in entities[:MAX_CARD_ENTITIES]:
        cand = None
        # Route A — Wikimedia Commons originals
        try:
            for q in res.queries_for(entity, hint):
                if cand:
                    break
                for page in res.commons_search(q, limit=8):
                    c, _row = res.evaluate_commons_page(
                        page, entity, "A — Wikimedia Commons",
                        context=context)
                    if accept(entity, c, page=page):
                        cand = c
                        break
        except Exception as e:
            log(f"entity sourcing route A failed ({entity}): {e}")
        # Route B — official sources (newsroom / org / .gov)
        if cand is None:
            try:
                links = res.brave_links(
                    f"{entity} official newsroom press media", 6)
                ent_tok = res.entity_tokens(entity)
                for link in links[:3]:
                    host = urllib.parse.urlparse(
                        link).netloc.lower()
                    if not (host.endswith((".gov", ".mil"))
                            or (ent_tok and ent_tok[0] in host)):
                        continue
                    c, _row = res.evaluate_hosted_page(
                        link, entity, "B — official sources",
                        res.DEFAULT_NET, context=context)
                    if accept(entity, c):
                        cand = c
                        break
            except Exception as e:
                log(f"entity sourcing route B failed ({entity}): {e}")
        # Route C — web search as discovery only -> Commons gates
        if cand is None:
            try:
                links = res.brave_links(
                    f"{entity} site:commons.wikimedia.org", 6)
                for link in links:
                    m = re.search(r"/wiki/(File:[^/?#]+)", link)
                    if not m:
                        continue
                    title = urllib.parse.unquote(
                        m.group(1)).replace("_", " ")
                    page = res.commons_file_info(title)
                    if not page:
                        continue
                    c, _row = res.evaluate_commons_page(
                        page, entity,
                        "C — web search (discovery) → Commons",
                        context=context)
                    if accept(entity, c, page=page):
                        cand = c
                        break
            except Exception as e:
                log(f"entity sourcing route C failed ({entity}): {e}")
        if cand is None:
            continue
        try:
            img, raw = _download_entity_image(cand["file_url"])
        except Exception as e:
            log(f"entity sourcing: download failed ({entity}): {e}")
            continue
        if not res.dims_ok(*img.size):
            log(f"entity sourcing: {entity} file below the floor "
                f"at true size {img.size[0]}x{img.size[1]} — skip")
            continue
        prov = {"entity": entity, "route": cand["route"],
                "source_page": cand["source_page"],
                "file_url": cand["file_url"],
                "license": cand["license"],
                "artist": cand.get("artist") or "",
                "bg_px": list(img.size)}
        log(f"entity sourcing: {entity} ← "
            f"{(cand['title'] or '')[:64]} "
            f"({img.size[0]}x{img.size[1]}, {cand['license']}) "
            f"via {cand['route']}")
        return img, raw, prov
    log(f"entity sourcing: honest miss for this card "
        f"(tried: {', '.join(entities[:MAX_CARD_ENTITIES])}) — navy")
    return None


def normalize_takeaways(raw):
    """p2_articles.key_takeaways -> a clean list of strings.

    The column is a JSON list of strings when populated (NULL on
    some writer rows); be liberal: also accept a JSON string, a
    newline-joined string, or dicts with a text-ish value."""
    if raw is None:
        return []
    items = raw
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        try:
            parsed = json.loads(s)
        except (ValueError, TypeError):
            parsed = None
        if isinstance(parsed, list):
            items = parsed
        else:
            items = [ln.strip() for ln in s.splitlines() if ln.strip()] \
                or [s]
    out = []
    if isinstance(items, list):
        for it in items:
            if isinstance(it, dict):
                it = (it.get("text") or it.get("takeaway")
                      or it.get("point") or "")
            t = str(it).strip()
            if t:
                out.append(t)
    return out


def _position_marker(draw, pos, total):
    """Discreet '2 / 4' in the bottom-right corner."""
    f = inter(26, "700")
    label = f"{pos} / {total}"
    tw = draw.textlength(label, font=f)
    draw.text((W - M - tw, H - 74), label, font=f, fill=MARKER_FILL)


def render_text_card(text, kicker, pos, total):
    """A key-takeaway card: pure navy field in the Sample C system —
    gold kicker + gold rule + the takeaway in large Playfair white
    serif, 'V.' mark top-left, position marker bottom-right. The
    block is vertically centred on the tall field."""
    card = Image.new("RGB", (W, H), NAVY)
    brand_mark_v(card)
    probe = ImageDraw.Draw(card)
    font, lines, size, truncated = fit_headline(
        probe, text, CW, max_lines=10, start=TAKEAWAY_START,
        floor=TAKEAWAY_FLOOR)
    bh = block_height(len(lines), size)
    y0 = max(170, (H - bh) // 2)
    draw_text_block(card, y0, kicker, GOLD, GOLD, font, lines, size)
    _position_marker(ImageDraw.Draw(card), pos, total)
    info = {"render_scale": 1.0, "truncated": truncated,
            "text_size": size, "text_lines": len(lines)}
    return card, info


def render_middle_card(text, kicker, pos, total, bg_img=None,
                       bg_raw=None):
    """A takeaway card with its OWN background (Kiran's steering,
    2026-10-24), theme-gated exactly like the hook:

      bg image >=1920px with a no-upscale cover-crop -> photo card
      (text over the smooth bottom gradient, white kicker + red
      rule, same type system as a full-bleed hook);
      bg image below the gate -> backdrop composition for this
      card (photo at native scale on navy, gold kicker + rule,
      text in the backdrop zone);
      no bg image -> the navy text card (render_text_card).

    bg_track in the returned info is "photo" / "backdrop" / "navy"."""
    if bg_img is not None:
        track, _scale, _note = choose_track(*bg_img.size)
        if track == "full-bleed":
            card, info = render_full_bleed(
                bg_img, text, kicker,
                anchor=focal_anchor(bg_img, bg_raw),
                fit_start=TAKEAWAY_START, fit_floor=TAKEAWAY_FLOOR,
                fit_max_lines=9)
            info["bg_track"] = "photo"
        else:
            card, info = render_backdrop(
                bg_img, text, kicker, fit_start=TAKEAWAY_START,
                fit_floor=TAKEAWAY_FLOOR)
            info["bg_track"] = "backdrop"
        _position_marker(ImageDraw.Draw(card), pos, total)
        info.setdefault("text_size", info.get("headline_size"))
        info.setdefault("text_lines", info.get("headline_lines"))
        return card, info
    card, info = render_text_card(text, kicker, pos, total)
    info["bg_track"] = "navy"
    return card, info


LOGO_ASSET = HERE / "assets" / "logo-transparent.png"
OFFWHITE = (233, 229, 218)
_lockup_cache = None


def load_v_lockup():
    """The V+compass brand glyph in white ink on transparency,
    derived from the tracked brand asset (assets/logo-transparent.png)
    the same way the cover family derived it (build_covers.py):
    crop to the glyph, recolor the navy ink white, keep the gold
    compass rose. Cached; None when the asset is unavailable (the
    closer then draws the mark in Playfair)."""
    global _lockup_cache
    if _lockup_cache is not None:
        return _lockup_cache or None
    try:
        im = Image.open(LOGO_ASSET).convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox:
            im = im.crop(bbox)
        # The asset also bakes a small 'THE VIDESHI' caption under
        # the mark; keep only the top ink cluster (the glyph) —
        # the closer draws its own fitted label.
        alpha = im.getchannel("A")
        w2, h2 = im.size
        apx = alpha.load()
        cut = h2
        for yy in range(h2):
            if all(apx[xx, yy] == 0 for xx in range(w2)):
                cut = yy
                break
        if 0 < cut < h2:
            im = im.crop((0, 0, w2, cut))
        px = im.load()
        w, h = im.size
        for yy in range(h):
            for xx in range(w):
                r, g, b, a = px[xx, yy]
                if a and r < 130 and b >= r:   # navy ink -> white
                    px[xx, yy] = (255, 255, 255, a)
        _lockup_cache = im
    except Exception:
        _lockup_cache = False
    return _lockup_cache or None


def render_closer_card(kicker, slug=None, pos=None, total=None):
    """The set closer (redesigned 2026-10-25 — the old closer read
    as an empty navy slab): the full brand lockup, centred — the
    V+compass glyph with 'THE VIDESHI' fitted under it (the
    avatar/cover treatment from build_covers.py), then the
    Playfair wordmark 'The Videshi', a gold rule, the tagline and
    thevideshi.com in gold. kicker/slug are accepted for call
    compatibility but no longer compete with the lockup."""
    card = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(card)
    cx = W // 2

    def th(text, font):
        b = d.textbbox((0, 0), text, font=font)
        return b[3] - b[1], b[1]

    glyph = load_v_lockup()
    wm_f = pf(96, "Bold")
    wm_h, wm_top = th("The Videshi", wm_f)
    tag_f = inter(33, "400")
    tag = "Your daily source for Indian diaspora news."
    tag_h, tag_top = th(tag, tag_f)
    url_f = inter(36, "600")
    url_h, url_top = th("thevideshi.com", url_f)
    g_wm, g_rule, g_tag, g_url = 58, 16, 15, 14
    if glyph is not None:
        glyph_h = 296
        glyph_w = int(glyph_h * glyph.width / glyph.height)
        lab_size = 30
        while lab_size > 10:
            lf = inter(lab_size, "600")
            if tracked_w(d, "THE VIDESHI", lf,
                         lab_size * 0.32) <= glyph_w:
                break
            lab_size -= 1
        lab_f, lab_tr = inter(lab_size, "600"), lab_size * 0.32
        lab_h = lab_size
        lab_gap = int(glyph_h * 0.07)
        group_h = (glyph_h + lab_gap + lab_h + g_wm + wm_h + g_rule
                   + RULE_H + g_tag + tag_h + g_url + url_h)
        y = (H - group_h) // 2
        g = glyph.resize((glyph_w, glyph_h), Image.LANCZOS)
        card.paste(g, (cx - glyph_w // 2, y), g)
        d = ImageDraw.Draw(card)
        lw_ = tracked_w(d, "THE VIDESHI", lab_f, lab_tr)
        draw_tracked(d, (cx - lw_ / 2, y + glyph_h + lab_gap),
                     "THE VIDESHI", lab_f, lab_tr, WHITE)
        y += glyph_h + lab_gap + lab_h + g_wm
    else:
        vf = pf(190, "ExtraBold")
        vh, _vt = th("V", vf)
        lab_h = 44
        group_h = (vh + 18 + lab_h + g_wm + wm_h + g_rule + RULE_H
                   + g_tag + tag_h + g_url + url_h)
        y = (H - group_h) // 2
        vw = d.textlength("V", font=vf)
        d.text((cx - vw / 2, y), "V", font=vf, fill=WHITE)
        y += vh + 18 + lab_h + g_wm
    wm_w = d.textlength("The Videshi", font=wm_f)
    d.text((cx - wm_w / 2, y - wm_top), "The Videshi", font=wm_f,
           fill=WHITE)
    y += wm_h + g_rule
    d.rectangle((cx - 60, y, cx + 60, y + RULE_H), fill=GOLD)
    y += RULE_H + g_tag
    tw_ = d.textlength(tag, font=tag_f)
    d.text((cx - tw_ / 2, y - tag_top), tag, font=tag_f,
           fill=OFFWHITE)
    y += tag_h + g_url
    uw = d.textlength("thevideshi.com", font=url_f)
    d.text((cx - uw / 2, y - url_top), "thevideshi.com",
           font=url_f, fill=GOLD)
    if pos:
        _position_marker(ImageDraw.Draw(card), pos, total)
    return card, {"render_scale": 1.0, "truncated": False,
                  "lockup": "asset" if glyph is not None
                  else "drawn"}


def _set_base(slug, headline):
    if slug and re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        return slug
    return "card-" + hashlib.sha1(headline.encode()).hexdigest()[:12]


def make_card_set(headline, category, image_url=None, image_path=None,
                  key_takeaways=None, subheadline=None, slug=None,
                  out_dir=None, backdrop="navy", body=None):
    """Render a full card SET for one article.

    Order: hook (make_card) -> up to MAX_SET_TAKEAWAYS takeaway
    cards (one takeaway each; the subheadline stands in as a single
    middle card when key_takeaways is empty) -> closer. Set size is
    therefore 2-4. A skipped hook (<600px rule) yields NO set —
    {"track": "skipped", "files": [], ...} — and callers fall back
    to today's behavior. Returns the info dict with "files" (the
    ordered PNG paths) and "cards" (per-card role/alt/truncated —
    takeaway cards also carry bg_source / bg_track / bg_px).

    Each middle card gets its OWN picture, sourced for that
    card's subject (Kiran's cross-format doctrine, 2026-10-25):
      a. inline images from the article body, in body order
         (hero and its thumbnail variants excluded) — middle i
         uses inline i;
      b. else ENTITY SOURCING for that card's subject via the
         Reels v7 ladder (_entity_image_for_card — Commons ->
         official -> Brave discovery, license-gated, provenance
         recorded on the card entry as bg_provenance);
      c. else the plain navy text card.
    The hero renders ONLY on the hook card, exactly once per
    deck, and no image renders on more than one card (a deck-level
    guard re-checks every candidate against the images already
    used). Each background is theme-gated like the hook (see
    render_middle_card): never upscaled."""
    out_dir = Path(out_dir) if out_dir else DEFAULT_OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    base = _set_base(slug, headline)
    kicker = kicker_for(category)
    hook_path = str(out_dir / f"{base}-1.png")
    hook = make_card(headline, category, image_url=image_url,
                     image_path=image_path, out_path=hook_path,
                     backdrop=backdrop)
    if hook.get("track") == "skipped":
        return {"track": "skipped", "reason": hook.get("reason"),
                "source_px": hook.get("source_px"), "files": [],
                "cards": [], "set_size": 0, "slug": slug,
                "kicker": kicker}
    middles = normalize_takeaways(key_takeaways)[:MAX_SET_TAKEAWAYS]
    middle_source = "key_takeaways" if middles else None
    if not middles and subheadline and str(subheadline).strip():
        middles = [str(subheadline).strip()]
        middle_source = "subheadline"
    total = 2 + len(middles)

    # ── Middle-card pictures: inline -> entity ladder -> navy.
    # The hero is NEVER a middle background; `used` tracks every
    # image identity already in the deck so nothing renders twice.
    inlines = [u for u in extract_inline_images(body)
               if not _same_image(u, image_url)]
    article_ctx = {"headline": headline, "body": body or "",
                   "slug": slug, "category": category}
    hook_id = (hook.get("fetched_url") or image_url
               or (str(image_path) if image_path else None))
    used = [u for u in (image_url, hook.get("fetched_url"),
                        str(image_path) if image_path else None)
            if u]

    files = [hook["out_path"]]
    cards = [{"role": "hook", "path": hook["out_path"],
              "alt": headline, "track": hook["track"],
              "image_id": hook_id,
              "truncated": bool(hook.get("truncated"))}]
    for i, text in enumerate(middles):
        pos = i + 2
        path = str(out_dir / f"{base}-{pos}.png")
        bg_img = bg_raw = bg_url = prov = None
        bg_source = "navy"
        if i < len(inlines):
            try:
                bg_img, _u, bg_raw = fetch_image(inlines[i])
                bg_url = inlines[i]
                if any(_same_image(bg_url, u) for u in used):
                    bg_img = bg_raw = bg_url = None
                else:
                    bg_source = f"inline:{i + 1}"
            except Exception:
                bg_img = bg_raw = bg_url = None
        if bg_img is None:
            got = _entity_image_for_card(text, article_ctx, used)
            if got is not None:
                bg_img, bg_raw, prov = got
                if any(_same_image(prov["file_url"], u)
                       for u in used):
                    # Deck-level guard: the adapter already
                    # filters, but a deck never repeats an image.
                    bg_img = bg_raw = prov = None
                else:
                    bg_source = "entity"
                    bg_url = prov["file_url"]
        card, rinfo = render_middle_card(text, kicker, pos, total,
                                         bg_img=bg_img, bg_raw=bg_raw)
        card.save(path, "PNG")
        files.append(path)
        entry = {"role": "takeaway", "path": path, "alt": text,
                 "truncated": rinfo["truncated"],
                 "text_size": rinfo.get("text_size"),
                 "text_lines": rinfo.get("text_lines"),
                 "bg_source": bg_source,
                 "bg_track": rinfo.get("bg_track"),
                 "bg_px": list(bg_img.size) if bg_img else None,
                 "image_id": bg_url}
        if prov is not None:
            entry["bg_entity"] = prov["entity"]
            entry["bg_provenance"] = {
                k: prov[k] for k in ("entity", "route",
                                     "source_page", "file_url",
                                     "license", "artist")}
        cards.append(entry)
        if bg_url:
            used.append(bg_url)
    closer_path = str(out_dir / f"{base}-{total}.png")
    card, _ = render_closer_card(kicker, slug=slug, pos=total,
                                 total=total)
    card.save(closer_path, "PNG")
    files.append(closer_path)
    cards.append({"role": "closer", "path": closer_path,
                  "alt": "The Videshi — Your daily source for "
                         "Indian diaspora news. thevideshi.com",
                  "truncated": False})
    info = {"track": hook["track"],
            "source_px": hook.get("source_px"),
            "render_scale": hook.get("render_scale"),
            "files": files, "cards": cards, "set_size": total,
            "middle_source": middle_source,
            "takeaways_used": len(middles)
            if middle_source == "key_takeaways" else 0,
            "inline_images": len(inlines),
            "truncated": any(c["truncated"] for c in cards),
            "kicker": kicker, "slug": slug,
            "backdrop": backdrop if hook["track"] == "backdrop"
            else None}
    if hook.get("track_note"):
        info["track_note"] = hook["track_note"]
    if hook.get("fetched_url"):
        info["fetched_url"] = hook["fetched_url"]
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
    ap.add_argument("--set", dest="set_mode", action="store_true",
                    help="render a full card SET (hook + takeaway "
                         "cards + closer) instead of a single card")
    ap.add_argument("--key-takeaways",
                    help="JSON list of takeaway strings (explicit "
                         "mode; with --slug/--id the article's own "
                         "key_takeaways are used)")
    ap.add_argument("--subheadline")
    args = ap.parse_args(argv)

    headline, category = args.headline, args.category
    image_url, slug = args.image_url, args.slug
    subheadline, key_takeaways, body = args.subheadline, None, None
    if args.key_takeaways:
        try:
            key_takeaways = json.loads(args.key_takeaways)
        except ValueError:
            key_takeaways = args.key_takeaways
    if args.slug or args.article_id:
        art = fetch_article(slug=args.slug, article_id=args.article_id)
        headline = headline or art["headline"]
        category = category or art["category"]
        image_url = image_url or art["image_url"]
        slug = art["slug"]
        if subheadline is None:
            subheadline = art.get("subheadline")
        if key_takeaways is None:
            key_takeaways = art.get("key_takeaways")
        body = art.get("body")
    if not headline or not category or not (image_url or args.image_path):
        ap.error("need --slug/--id, or --headline + --category + "
                 "--image-url/--image-path")
    if args.set_mode:
        info = make_card_set(headline, category, image_url=image_url,
                             image_path=args.image_path,
                             key_takeaways=key_takeaways,
                             subheadline=subheadline, slug=slug,
                             backdrop=args.backdrop, body=body)
        print(json.dumps(info))
        return 0
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
