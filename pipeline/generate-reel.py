#!/usr/bin/env python3
"""
The Videshi — Instagram Reel Generator (v4)
4-scene news reel: Hook → Story Image → Key Takeaways → CTA
Output: 1080x1920, ~30 seconds, H.264+AAC MP4
"""
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ── Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "reels"
ENV_SUPABASE = Path.home() / "workspace" / ".env.supabase"

# Font paths with fallbacks
def _find_font(candidates):
    for f in candidates:
        if os.path.exists(f):
            return f
    return candidates[0]

FONT_BOLD = _find_font([
    "/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])
FONT_EXTRABOLD = _find_font([
    "/usr/share/fonts/truetype/inter/InterDisplay-ExtraBold.ttf",
    "/usr/share/fonts/truetype/inter/Inter-ExtraBold.ttf",
    FONT_BOLD,
])
FONT_SEMIBOLD = _find_font([
    "/usr/share/fonts/truetype/inter/Inter-SemiBold.ttf",
    "/usr/share/fonts/truetype/inter/Inter-Medium.ttf",
    FONT_BOLD,
])
FONT_REGULAR = _find_font([
    "/usr/share/fonts/truetype/inter/Inter-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])

# ── Constants ──────────────────────────────────────────────────────────
W, H = 1080, 1920
FPS = 25

HOOK_DUR    = 3.0    # Scene 1: hook / scroll-stopper
IMAGE_DUR   = 7.0    # Scene 2: article image + full headline chyron
BULLET_DUR  = 8.0    # Scene 3: key takeaways (skipped if no subheadline)
CTA_DUR     = 4.0    # Scene 4: CTA / TheVideshi.com ad
XFADE_DUR   = 0.5

NAVY = (26, 26, 46)
GOLD = (212, 168, 67)
WHITE = (255, 255, 255)
WHITE_DIM = (200, 200, 210)
SHADOW = (0, 0, 0)

CATEGORY_COLORS = {
    "news":          (220, 53, 53),
    "immigration":   (59, 130, 246),
    "sports":        (34, 197, 94),
    "entertainment": (147, 51, 234),
    "travel":        (20, 184, 166),
    "lifestyle":     (236, 72, 153),
    "markets":       (245, 158, 11),
    "technology":    (99, 102, 241),
    "food":          (249, 115, 22),
    "nri-world":     (59, 130, 246),
}


# ── Helpers ────────────────────────────────────────────────────────────
def load_env(path):
    env = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env


def fetch_article(slug=None):
    env = load_env(ENV_SUPABASE)
    url, key = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    fields = "id,slug,headline,subheadline,category,image_url"
    if slug:
        r = requests.get(
            f"{url}/rest/v1/p2_articles?slug=eq.{slug}&select={fields}",
            headers=headers)
        articles = r.json()
        if not articles:
            sys.exit(f"❌ No article with slug: {slug}")
        return articles[0]
    else:
        for filt in [
            "status=eq.published&instagrammed_at=is.null&image_url=not.is.null",
            "status=eq.published&image_url=not.is.null",
        ]:
            r = requests.get(
                f"{url}/rest/v1/p2_articles?{filt}"
                f"&order=published_at.desc&limit=1&select={fields}",
                headers=headers)
            if r.json():
                return r.json()[0]
        sys.exit("❌ No articles found")


def download_image(url, dest):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    Path(dest).write_bytes(r.content)


def word_wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, max_w, max_h, font_path,
             sizes=(72, 66, 60, 54, 50, 46, 42, 38, 34)):
    for sz in sizes:
        font = ImageFont.truetype(font_path, sz)
        lines = word_wrap(draw, text, font, max_w)
        a, d = font.getmetrics()
        lh = a + d + int(sz * 0.22)
        if lh * len(lines) <= max_h:
            return font, lines, lh
    font = ImageFont.truetype(font_path, sizes[-1])
    lines = word_wrap(draw, text, font, max_w)
    a, d = font.getmetrics()
    return font, lines, a + d + int(sizes[-1] * 0.22)


def rounded_rect(draw, xy, r, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy, sa, ea in [
        (x0+r, y0+r, 180, 270), (x1-r, y0+r, 270, 360),
        (x0+r, y1-r, 90, 180),  (x1-r, y1-r, 0, 90)]:
        draw.pieslice([cx-r, cy-r, cx+r, cy+r], sa, ea, fill=fill)


def draw_text_shadow(draw, xy, text, font, fill, shadow_offset=3):
    x, y = xy
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=SHADOW)
    draw.text((x, y), text, font=font, fill=fill)


def extract_hook(headline):
    """Extract the punchiest quote or phrase from a headline for the hook."""
    # Try quoted text first (single or double quotes)
    quotes = re.findall(r"['\u2018\u2019\u201c\u201d\"](.*?)['\u2018\u2019\u201c\u201d\"]", headline)
    if quotes:
        # Pick the longest quote that's reasonable length
        best = max(quotes, key=len)
        if 10 <= len(best) <= 100:
            return f'"{best}"'

    # Try text after a colon
    if ":" in headline:
        after = headline.split(":", 1)[1].strip()
        first_sent = re.split(r'[.!]', after)[0].strip()
        if 10 <= len(first_sent) <= 100:
            return first_sent

    # First sentence
    sentences = re.split(r'(?<=[.!?])\s+', headline)
    if sentences and len(sentences[0]) <= 100:
        return sentences[0]

    # Fallback: first ~60 chars on word boundary
    if len(headline) <= 60:
        return headline
    cut = headline[:60].rsplit(" ", 1)[0]
    return cut + "..."


def split_subheadline(subheadline):
    """Split subheadline into 2-4 bullet points."""
    if not subheadline:
        return []

    # Try splitting on sentence boundaries — but be careful with abbreviations
    # First, protect common abbreviations from being split
    protected = subheadline
    for abbr in ["D.Litt.", "D.Sc.", "Ph.D.", "M.D.", "B.A.", "M.A.", "Mr.", "Mrs.",
                 "Dr.", "Jr.", "Sr.", "vs.", "etc.", "U.S.", "U.K.", "A.R.", "A.P.",
                 "St.", "Lt.", "Gov.", "Gen.", "Sgt.", "Corp.", "Inc.", "Ltd."]:
        protected = protected.replace(abbr, abbr.replace(".", "●"))

    sentences = re.split(r'(?<=[.!?])\s+', protected.strip())
    # Restore dots
    sentences = [s.replace("●", ".").strip() for s in sentences if s.strip()]

    # Filter: must be >15 chars AND start with uppercase (not a fragment)
    good = [s for s in sentences if len(s.strip()) > 15 and s.strip()[0].isupper()]

    if len(good) <= 1:
        # If only one sentence, try splitting on em-dash or semicolon
        parts = re.split(r'\s*[—;]\s*', subheadline.strip())
        parts = [p.strip() for p in parts if len(p.strip()) > 15 and p.strip()[0].isupper()]
        if len(parts) > 1:
            good = parts

    if not good:
        return [subheadline.strip()]

    # Pick up to 3 of the most informative sentences
    # Prefer shorter, punchier ones and skip very long ones
    picked = []
    for s in good:
        if len(s) <= 150:
            picked.append(s)
        if len(picked) >= 3:
            break

    # If all were too long, truncate the best ones
    if not picked:
        for s in good[:3]:
            if len(s) > 150:
                # Truncate at last space before 147 chars
                cut = s[:147].rsplit(" ", 1)[0] + "..."
                picked.append(cut)
            else:
                picked.append(s)

    return picked


def _make_bg_image(img_path, blur=True):
    """Load article image, scale to cover WxH, optionally blur."""
    img = Image.open(img_path).convert("RGB")
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    nw, nh = img.size
    x0, y0 = (nw - W) // 2, (nh - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=12))
    return img


# ── Scene Renderers ────────────────────────────────────────────────────

def fetch_wikipedia_image(headline):
    """Try to fetch a Wikipedia image for a named person in the headline.
    Returns local file path on success, None on failure."""
    # Common non-name words to filter
    STOP_WORDS = {
        "India", "Indian", "Indians", "America", "American", "Britain", "British",
        "Europe", "European", "Dubai", "Paris", "London", "Delhi", "Kerala",
        "Mumbai", "What", "When", "Where", "Which", "That", "This", "These",
        "Those", "Here", "There", "Their", "They", "Have", "From", "With",
        "About", "After", "Before", "Between", "Under", "Over", "Into",
        "Every", "Some", "Most", "Many", "Much", "Such", "Just", "Also",
        "Even", "Still", "Back", "Down", "Away", "Why", "How",
        "Your", "More", "Than", "Then", "Could", "Would", "Should",
        "Will", "Been", "Being", "Were", "Was", "Are", "The",
        "New", "Old", "Next", "Last", "First", "Third", "Second",
        "Killed", "Supposed", "Receive", "Instead", "Accepting",
        "Today", "Tomorrow", "Yesterday", "Quietly", "Slowly",
        "Gulf", "Carriers", "Flights", "Card", "Means", "Digital",
        "Booklet", "Blue", "Million", "Overseas", "Pushed",
        "Turned", "Weeks", "Trial", "Smartphone", "Cognitive",
        "Highest", "Civilian", "Honour", "Honor", "Doctorate",
        "University", "Award", "Awards", "President", "Minister",
        "Kottayam", "Rashtrapat", "Padma", "Says", "Said",
    }

    # Extract all capitalized words from the headline
    all_caps = re.findall(r"\b([A-Z][a-z]+(?:\.[A-Z]\.?)*)\b", headline)
    # Filter to potential name words (not stop words)
    name_words = [w for w in all_caps if w not in STOP_WORDS and len(w) >= 3]

    # Build candidate names: try consecutive pairs first, then singles
    candidates = []
    # Look for consecutive name words in original headline order
    for i in range(len(name_words)):
        # Check if two consecutive name_words appear next to each other in headline
        if i + 1 < len(name_words):
            pair = f"{name_words[i]} {name_words[i+1]}"
            if pair in headline and pair not in candidates:
                candidates.append(pair)
        # Single name
        if name_words[i] not in candidates:
            candidates.append(name_words[i])

    if not candidates:
        return None

    print(f"  🔍 Wikipedia candidates: {candidates[:5]}")

    for name in candidates[:5]:  # Try up to 5 candidates
        try:
            wiki_name = name.replace(" ", "_")
            r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=10
            )
            if r.status_code != 200:
                continue
            data = r.json()
            img_url = data.get("originalimage", {}).get("source")
            if not img_url:
                img_url = data.get("thumbnail", {}).get("source")
            if not img_url:
                continue

            # Download the image
            img_r = requests.get(img_url, timeout=15, headers={
                "User-Agent": "TheVideshi/1.0 (thevideshi.com; mailto:hello@thevideshi.com)"
            })
            img_r.raise_for_status()
            ext = ".jpg" if "jpeg" in img_url.lower() or "jpg" in img_url.lower() else ".png"
            tmp_path = os.path.join(tempfile.gettempdir(), f"wiki_{wiki_name}{ext}")
            Path(tmp_path).write_bytes(img_r.content)

            # Verify it's a valid image
            test_img = Image.open(tmp_path)
            test_img.verify()
            print(f"  ✓ Wikipedia image for '{name}': {len(img_r.content)} bytes")
            return tmp_path
        except Exception as e:
            print(f"  ⚠️  Wikipedia lookup failed for '{name}': {e}")
            continue

    return None


def render_hook(article, tmp_dir, img_path):
    """Scene 1: Hook — branded navy bg + punchy text. No article image.
    Clean, professional news-alert card that stands on its own."""
    headline = article["headline"]
    cat = (article.get("category") or "news").lower().replace("-", " ").replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat.replace(" ", "-"), CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    hook_text = extract_hook(headline)

    # Navy background
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle dot pattern for texture (same as CTA scene)
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    pad = 80

    # ── Measure all element heights for vertical centering ──

    # 1. "THE VIDESHI" logo text
    logo_f = ImageFont.truetype(FONT_EXTRABOLD, 36)
    logo_txt = "THE VIDESHI"
    logo_bb = draw.textbbox((0, 0), logo_txt, font=logo_f)
    logo_w = logo_bb[2] - logo_bb[0]
    logo_h = logo_bb[3] - logo_bb[1]

    # 2. Gold accent line
    gold_line_h = 4

    # 3. Category badge
    bf = ImageFont.truetype(FONT_BOLD, 28)
    bb = draw.textbbox((0, 0), cat_label, font=bf)
    bw_txt, bh_txt = bb[2] - bb[0], bb[3] - bb[1]
    bw, bh = bw_txt + 44, bh_txt + 22

    # 4. Hook text — fit to available space
    max_w = W - 2 * pad
    # Pre-measure with a large zone
    hook_font, hook_lines, hook_lh = fit_text(
        draw, hook_text, max_w, 800, FONT_EXTRABOLD,
        sizes=(82, 76, 70, 64, 58, 52, 46)
    )
    hook_text_h = hook_lh * len(hook_lines)

    # 5. Gold accent line below hook
    gold_line2_h = 5

    # 6. Bottom site text
    site_f = ImageFont.truetype(FONT_SEMIBOLD, 24)
    site_txt = "thevideshi.com"
    site_bb = draw.textbbox((0, 0), site_txt, font=site_f)
    site_w = site_bb[2] - site_bb[0]
    site_h = site_bb[3] - site_bb[1]

    # Spacing
    sp_logo_line = 30
    sp_line_badge = 50
    sp_badge_hook = 60
    sp_hook_line2 = 40
    sp_line2_site = 50

    total_h = (logo_h + sp_logo_line + gold_line_h + sp_line_badge
               + bh + sp_badge_hook + hook_text_h + sp_hook_line2
               + gold_line2_h + sp_line2_site + site_h)

    # Centre the whole block vertically
    y0 = (H - total_h) // 2

    # ── Draw from y0 ──

    # "THE VIDESHI" logo
    draw.text(((W - logo_w) // 2, y0), logo_txt, font=logo_f, fill=GOLD)

    # Gold accent line 1
    line1_y = y0 + logo_h + sp_logo_line
    draw.rectangle([W // 2 - 80, line1_y, W // 2 + 80, line1_y + gold_line_h], fill=GOLD)

    # Category badge (centered)
    badge_y = line1_y + gold_line_h + sp_line_badge
    bx = (W - bw) // 2
    rounded_rect(draw, (bx, badge_y, bx + bw, badge_y + bh), 16, cat_color)
    draw.text((bx + (bw - bw_txt) // 2, badge_y + (bh - bh_txt) // 2 - 1),
              cat_label, font=bf, fill=WHITE)

    # Giant hook text — centered
    hook_y = badge_y + bh + sp_badge_hook
    for i, line in enumerate(hook_lines):
        y = hook_y + i * hook_lh
        # Center each line
        line_bb = draw.textbbox((0, 0), line, font=hook_font)
        line_w = line_bb[2] - line_bb[0]
        lx = (W - line_w) // 2
        draw.text((lx, y), line, font=hook_font, fill=WHITE)

    # Gold accent line 2
    line2_y = hook_y + hook_text_h + sp_hook_line2
    draw.rectangle([pad, line2_y, pad + 140, line2_y + gold_line2_h], fill=GOLD)

    # Bottom branding
    site_y = line2_y + gold_line2_h + sp_line2_site
    draw.text(((W - site_w) // 2, site_y), site_txt, font=site_f, fill=WHITE_DIM)

    out = os.path.join(tmp_dir, "hook.png")
    img.save(out, quality=95)
    return out


def render_image_scene(article, tmp_dir, img_path):
    """Scene 2: Article image with headline chyron overlay for Ken Burns zoom.
    Handles long headlines with font reduction, line cap, truncation, and
    an adaptive gradient that expands to cover the text."""
    headline = article["headline"]
    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.open(img_path).convert("RGB")
    # Scale to cover with 20% margin for zoom
    tw, th = int(W * 1.20), int(H * 1.20)
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    nw, nh = img.size
    x0, y0 = (nw - tw) // 2, (nh - th) // 2
    img = img.crop((x0, y0, x0 + tw, y0 + th))

    # Overlay positions relative to visible centre area
    ox = (tw - W) // 2
    oy = (th - H) // 2
    pad = 70
    max_w = W - 2 * pad
    MAX_HEADLINE_LINES = 7

    # ── Pick headline font size ──
    # Use a temp draw for text measurement before the real draw exists
    _meas_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    # For long headlines (>100 chars), start with smaller sizes
    if len(headline) > 120:
        sizes = (40, 36, 34, 32, 30, 28, 26)
    elif len(headline) > 100:
        sizes = (44, 40, 36, 34, 32, 30, 28)
    else:
        sizes = (52, 48, 44, 40, 36, 32, 28)

    # Fit text with line cap
    chosen_font = None
    chosen_lines = None
    chosen_lh = 0
    for sz in sizes:
        font = ImageFont.truetype(FONT_EXTRABOLD, sz)
        lines = word_wrap(draw=_meas_draw,
                          text=headline, font=font, max_w=max_w)
        a, d = font.getmetrics()
        lh = a + d + int(sz * 0.22)
        if len(lines) <= MAX_HEADLINE_LINES:
            chosen_font, chosen_lines, chosen_lh = font, lines, lh
            break
    else:
        # Smallest size still exceeds line cap — truncate
        font = ImageFont.truetype(FONT_EXTRABOLD, sizes[-1])
        lines = word_wrap(draw=_meas_draw,
                          text=headline, font=font, max_w=max_w)
        a, d = font.getmetrics()
        lh = a + d + int(sizes[-1] * 0.22)
        # Cap and add ellipsis
        lines = lines[:MAX_HEADLINE_LINES]
        last = lines[-1]
        if last.endswith("."):
            lines[-1] = last + ".."
        else:
            # Trim last word and add ...
            trimmed = last.rsplit(" ", 1)[0] if " " in last else last[:-3]
            lines[-1] = trimmed + "..."
        chosen_font, chosen_lines, chosen_lh = font, lines, lh

    # ── Calculate chyron area ──
    # Badge + headline + gold line + site branding
    bf = ImageFont.truetype(FONT_BOLD, 24)
    badge_bb = _meas_draw.textbbox((0, 0), cat_label, font=bf)
    bw_txt, bh_txt = badge_bb[2] - badge_bb[0], badge_bb[3] - badge_bb[1]
    bw_badge, bh_badge = bw_txt + 36, bh_txt + 18

    text_block_h = chosen_lh * len(chosen_lines)
    # Total chyron content: badge + gap + text + gap + gold line + gap + site text
    chyron_content_h = bh_badge + 20 + text_block_h + 14 + 3 + 20 + 22
    chyron_bottom_pad = 40
    chyron_top_pad = 80

    # Position chyron content so it ends near the bottom
    chyron_end_y = oy + H - chyron_bottom_pad
    chyron_start_y = chyron_end_y - chyron_content_h
    # Gradient starts well above the content for smooth fade
    grad_start_y = chyron_start_y - chyron_top_pad

    # Clamp: gradient should start no lower than 35% of frame and no higher than 20%
    min_grad_start = int(th * 0.20)
    max_grad_start = int(th * 0.45)
    grad_start_y = max(min_grad_start, min(grad_start_y, max_grad_start))

    # ── Draw adaptive dark gradient ──
    gradient = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(grad_start_y, th):
        progress = (y - grad_start_y) / max(1, th - grad_start_y)
        alpha = int(220 * (progress ** 1.2))
        grad_draw.rectangle([0, y, tw, y + 1], fill=(0, 0, 0, min(alpha, 220)))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(img)

    # ── Draw chyron content ──
    # Category badge
    badge_x = ox + pad
    badge_y = chyron_start_y
    rounded_rect(draw, (badge_x, badge_y, badge_x + bw_badge, badge_y + bh_badge), 14, cat_color)
    draw.text((badge_x + (bw_badge - bw_txt) // 2, badge_y + (bh_badge - bh_txt) // 2 - 1),
              cat_label, font=bf, fill=WHITE)

    # Headline text
    y_cursor = badge_y + bh_badge + 20
    for line in chosen_lines:
        draw.text((ox + pad + 2, y_cursor + 2), line, font=chosen_font, fill=SHADOW)
        draw.text((ox + pad, y_cursor), line, font=chosen_font, fill=WHITE)
        y_cursor += chosen_lh

    # Gold accent line
    line_y = y_cursor + 14
    draw.rectangle([ox + pad, line_y, ox + pad + 80, line_y + 3], fill=GOLD)

    # Bottom branding
    site_f = ImageFont.truetype(FONT_SEMIBOLD, 22)
    site_txt = "thevideshi.com"
    sb = draw.textbbox((0, 0), site_txt, font=site_f)
    site_w = sb[2] - sb[0]
    draw.text((ox + (W - site_w) // 2, chyron_end_y - 22), site_txt, font=site_f, fill=WHITE_DIM)

    img = img.convert("RGB")
    out = os.path.join(tmp_dir, "image_scene.png")
    img.save(out, quality=95)
    return out, tw, th


def render_takeaways(article, tmp_dir):
    """Scene 3: Key takeaways from the subheadline on dark navy bg.
    Content is vertically centred on the frame.
    Returns None if no subheadline."""
    subheadline = article.get("subheadline")
    if not subheadline:
        return None

    bullets = split_subheadline(subheadline)
    if not bullets:
        return None

    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    pad = 80
    max_w = W - 2 * pad - 40  # indent for bullet marker

    # ── Measure all content heights first ──
    # 1. Category badge
    bf = ImageFont.truetype(FONT_BOLD, 28)
    bb = draw.textbbox((0, 0), cat_label, font=bf)
    bw_txt, bh_txt = bb[2] - bb[0], bb[3] - bb[1]
    bw, bh = bw_txt + 40, bh_txt + 20

    # 2. Header
    hf = ImageFont.truetype(FONT_EXTRABOLD, 44)
    header = "KEY TAKEAWAYS"
    hb = draw.textbbox((0, 0), header, font=hf)
    header_h = hb[3] - hb[1]

    # 3. Bullets — pick font size; start very large to fill frame
    for sz in (58, 54, 50, 46, 42, 38, 34, 30):
        test_font = ImageFont.truetype(FONT_SEMIBOLD, sz)
        total_lines = 0
        for b in bullets:
            total_lines += len(word_wrap(draw, b, test_font, max_w))
        a, d = test_font.getmetrics()
        test_lh = a + d + int(sz * 0.35)
        test_gap = int(sz * 1.8)
        bullets_h = total_lines * test_lh + (len(bullets) - 1) * test_gap
        if bullets_h <= 1000:
            break

    bullet_font = ImageFont.truetype(FONT_SEMIBOLD, sz)
    a, d = bullet_font.getmetrics()
    lh = a + d + int(sz * 0.35)
    gap = int(sz * 1.8)

    # 4. Bottom branding
    brand_f = ImageFont.truetype(FONT_EXTRABOLD, 44)
    site_f = ImageFont.truetype(FONT_REGULAR, 28)
    brand_bb = draw.textbbox((0, 0), "THE VIDESHI", font=brand_f)
    brand_h = brand_bb[3] - brand_bb[1]
    site_bb = draw.textbbox((0, 0), "thevideshi.com", font=site_f)
    site_h = site_bb[3] - site_bb[1]

    # Spacing between elements (generous)
    sp_badge_header = 65
    sp_header_line = 25
    gold_line_h = 4
    sp_line_bullets = 60
    sp_bullets_brand = 80
    sp_brand_site = 20

    total_h = (bh + sp_badge_header + header_h + sp_header_line + gold_line_h
               + sp_line_bullets + bullets_h + sp_bullets_brand
               + brand_h + sp_brand_site + site_h)

    # Centre the whole block vertically (true center, no offset)
    y0 = (H - total_h) // 2

    # ── Draw everything from y0 ──
    # Category badge
    bx = (W - bw) // 2
    by = y0
    rounded_rect(draw, (bx, by, bx + bw, by + bh), 12, cat_color)
    draw.text((bx + (bw - bw_txt) // 2, by + (bh - bh_txt) // 2 - 1),
              cat_label, font=bf, fill=WHITE)

    # "KEY TAKEAWAYS" header
    header_y = by + bh + sp_badge_header
    draw.text(((W - (hb[2] - hb[0])) // 2, header_y), header, font=hf, fill=GOLD)

    # Gold line under header
    line_y = header_y + header_h + sp_header_line
    draw.rectangle([W // 2 - 60, line_y, W // 2 + 60, line_y + gold_line_h], fill=GOLD)

    # Bullet points
    bullet_x = pad + 40
    y_cursor = line_y + gold_line_h + sp_line_bullets
    for i, bullet in enumerate(bullets):
        lines = word_wrap(draw, bullet, bullet_font, max_w)

        # Gold bullet marker (circle) — sized to match text
        marker_y = y_cursor + lh // 2 - 12
        draw.ellipse([pad + 4, marker_y, pad + 28, marker_y + 24], fill=GOLD)

        for j, line in enumerate(lines):
            draw.text((bullet_x + 2, y_cursor + 2), line, font=bullet_font, fill=(15, 15, 30))
            draw.text((bullet_x, y_cursor), line, font=bullet_font, fill=WHITE)
            y_cursor += lh

        if i < len(bullets) - 1:
            y_cursor += gap

    # Bottom branding
    brand_y = y_cursor + sp_bullets_brand
    brand_txt_w = brand_bb[2] - brand_bb[0]
    draw.text(((W - brand_txt_w) // 2, brand_y), "THE VIDESHI", font=brand_f, fill=GOLD)

    site_y = brand_y + brand_h + sp_brand_site
    site_txt_w = site_bb[2] - site_bb[0]
    draw.text(((W - site_txt_w) // 2, site_y), "thevideshi.com", font=site_f, fill=WHITE_DIM)

    out = os.path.join(tmp_dir, "takeaways.png")
    img.save(out, quality=95)
    return out


def render_cta(article, tmp_dir):
    """Scene 4: CTA / advertisement card — TheVideshi.com is the star.
    Entire content block is vertically centred on the frame."""
    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle dot pattern for texture
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    # ── Measure all element heights ──
    # 1. Category badge
    bf_cat = ImageFont.truetype(FONT_BOLD, 26)
    cb = draw.textbbox((0, 0), cat_label, font=bf_cat)
    bw_txt, bh_txt = cb[2] - cb[0], cb[3] - cb[1]
    bw, bh = bw_txt + 36, bh_txt + 18

    # 2. Brand text
    brand_f = ImageFont.truetype(FONT_EXTRABOLD, 80)
    brand_txt = "THE VIDESHI"
    brand_bb = draw.textbbox((0, 0), brand_txt, font=brand_f)
    brand_w = brand_bb[2] - brand_bb[0]
    brand_h = brand_bb[3] - brand_bb[1]

    # 3. URL text (the star) — HUGE
    url_f = ImageFont.truetype(FONT_EXTRABOLD, 100)
    url_txt = "TheVideshi.com"
    url_bb = draw.textbbox((0, 0), url_txt, font=url_f)
    url_w = url_bb[2] - url_bb[0]
    url_h = url_bb[3] - url_bb[1]

    # 4. Tagline
    tag_f = ImageFont.truetype(FONT_REGULAR, 34)
    tag_txt = "Your daily source for Indian diaspora news"
    tag_bb = draw.textbbox((0, 0), tag_txt, font=tag_f)
    tag_w = tag_bb[2] - tag_bb[0]
    tag_h = tag_bb[3] - tag_bb[1]

    # 5. CTA text
    cta_f = ImageFont.truetype(FONT_SEMIBOLD, 48)
    cta_txt = "Read more on our site  ↗"
    cta_bb = draw.textbbox((0, 0), cta_txt, font=cta_f)
    cta_w = cta_bb[2] - cta_bb[0]
    cta_h = cta_bb[3] - cta_bb[1]

    # 6. Follow text
    follow_f = ImageFont.truetype(FONT_REGULAR, 32)
    follow_txt = "Follow @the.videshi"
    follow_bb = draw.textbbox((0, 0), follow_txt, font=follow_f)
    follow_w = follow_bb[2] - follow_bb[0]
    follow_h = follow_bb[3] - follow_bb[1]

    # 7. Social line
    social_f = ImageFont.truetype(FONT_REGULAR, 26)
    social_txt = "X: @thevideshi  ·  YT: @the.videshi"
    social_bb = draw.textbbox((0, 0), social_txt, font=social_f)
    social_w = social_bb[2] - social_bb[0]
    social_h = social_bb[3] - social_bb[1]

    # Spacing constants (generous)
    gold_line_h = 5
    sp_badge_line1 = 50
    sp_line1_brand = 50
    sp_brand_url = 30
    sp_url_tag = 40
    sp_tag_line2 = 50
    sp_line2_cta = 45
    sp_cta_follow = 40
    sp_follow_social = 20

    total_h = (bh + sp_badge_line1 + gold_line_h + sp_line1_brand
               + brand_h + sp_brand_url + url_h + sp_url_tag
               + tag_h + sp_tag_line2 + gold_line_h + sp_line2_cta
               + cta_h + sp_cta_follow + follow_h
               + sp_follow_social + social_h)

    # Centre the whole block (true center, no offset)
    y0 = (H - total_h) // 2

    # ── Draw from y0 ──
    # Category badge
    badge_x = (W - bw) // 2
    badge_y = y0
    rounded_rect(draw, (badge_x, badge_y, badge_x + bw, badge_y + bh), 10, cat_color)
    draw.text((badge_x + (bw - bw_txt) // 2, badge_y + (bh - bh_txt) // 2 - 1),
              cat_label, font=bf_cat, fill=WHITE)

    # Gold accent line 1
    line1_y = badge_y + bh + sp_badge_line1
    draw.rectangle([W // 2 - 80, line1_y, W // 2 + 80, line1_y + gold_line_h], fill=GOLD)

    # "THE VIDESHI" brand text
    brand_y = line1_y + gold_line_h + sp_line1_brand
    draw.text(((W - brand_w) // 2, brand_y), brand_txt, font=brand_f, fill=GOLD)

    # ★ "TheVideshi.com" — THE STAR
    url_y = brand_y + brand_h + sp_brand_url
    # Glow effect
    glow_color = (180, 140, 40)
    for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3), (3, 0)]:
        draw.text(((W - url_w) // 2 + ox, url_y + oy), url_txt, font=url_f, fill=glow_color)
    draw.text(((W - url_w) // 2, url_y), url_txt, font=url_f, fill=GOLD)

    # Tagline
    tag_y = url_y + url_h + sp_url_tag
    draw.text(((W - tag_w) // 2, tag_y), tag_txt, font=tag_f, fill=WHITE_DIM)

    # Gold accent line 2
    line2_y = tag_y + tag_h + sp_tag_line2
    draw.rectangle([W // 2 - 60, line2_y, W // 2 + 60, line2_y + gold_line_h], fill=GOLD)

    # "Read more on our site ↗"
    cta_y = line2_y + gold_line_h + sp_line2_cta
    draw.text(((W - cta_w) // 2, cta_y), cta_txt, font=cta_f, fill=WHITE)

    # "Follow @the.videshi"
    follow_y = cta_y + cta_h + sp_cta_follow
    draw.text(((W - follow_w) // 2, follow_y), follow_txt, font=follow_f, fill=WHITE_DIM)

    # "X: @thevideshi  ·  YT: @the.videshi"
    social_y = follow_y + follow_h + sp_follow_social
    draw.text(((W - social_w) // 2, social_y), social_txt, font=social_f, fill=WHITE_DIM)

    out = os.path.join(tmp_dir, "cta.png")
    img.save(out, quality=95)
    return out


def _pick_music_track():
    """Pick a random background music track (30s preferred, trimmed to reel length in assembly)."""
    music_dir = os.path.join(SCRIPT_DIR, "music")
    if not os.path.isdir(music_dir):
        return None
    # Prefer 30s tracks
    tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir)
              if f.endswith("-30s.mp3")]
    if not tracks:
        tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir)
                  if f.endswith("-15s.mp3")]
    if tracks:
        return random.choice(tracks)
    return None


def assemble_reel(tmp_dir, scenes, output_path):
    """Assemble N scenes with ffmpeg xfade transitions + background music.

    scenes: list of dicts with keys:
        type: 'static' or 'zoompan'
        path: image file path
        dur:  duration in seconds
        (for zoompan) zw, zh: source image dimensions
    """
    n = len(scenes)
    xf = XFADE_DUR

    filter_parts = []
    input_args = []

    for i, sc in enumerate(scenes):
        input_args.extend(["-i", sc["path"]])

        if sc["type"] == "zoompan":
            zp_frames = int(sc["dur"] * FPS)
            z_expr = f"1+0.10*(on/{zp_frames})"
            filter_parts.append(
                f"[{i}:v]zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={zp_frames}:s={W}x{H}:fps={FPS},"
                f"setpts=PTS-STARTPTS[v{i}]"
            )
        else:
            nframes = int(sc["dur"] * FPS)
            fade_in = ",fade=t=in:st=0:d=0.5" if i == 0 else ""
            filter_parts.append(
                f"[{i}:v]loop=loop={nframes - 1}:size=1:start=0,"
                f"setpts=PTS-STARTPTS,fps={FPS}{fade_in}[v{i}]"
            )

    # Chain xfade transitions
    if n == 1:
        filter_parts.append(f"[v0]null[vout]")
    else:
        # First xfade
        offset = scenes[0]["dur"] - xf
        filter_parts.append(
            f"[v0][v1]xfade=transition=fade:duration={xf}:offset={offset}[vx1]"
        )
        cumulative = scenes[0]["dur"] + scenes[1]["dur"] - xf
        for i in range(2, n):
            prev = f"vx{i-1}"
            offset = cumulative - xf
            out_label = "vout" if i == n - 1 else f"vx{i}"
            filter_parts.append(
                f"[{prev}][v{i}]xfade=transition=fade:duration={xf}:offset={offset}[{out_label}]"
            )
            cumulative += scenes[i]["dur"] - xf

        if n == 2:
            # Rename vx1 to vout
            filter_parts[-1] = filter_parts[-1].replace("[vx1]", "[vout]")

    filter_complex = ";".join(filter_parts)
    total_dur = sum(s["dur"] for s in scenes) - xf * (n - 1)

    # Audio
    audio_idx = n  # audio input index
    music_track = _pick_music_track()
    if music_track:
        print(f"  🎵 Music: {os.path.basename(music_track)}")
        audio_inputs = ["-i", music_track]
        audio_filter = ["-af", f"atrim=0:{total_dur},afade=out:st={total_dur-2}:d=2"]
    else:
        print("  🔇 No music tracks, silent audio")
        audio_inputs = ["-f", "lavfi", "-i",
                        f"anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_dur}"]
        audio_filter = []

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        *audio_inputs,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "22",
        "-r", str(FPS),
        "-c:a", "aac", "-b:a", "128k",
        *audio_filter,
        "-t", str(total_dur),
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  FFmpeg xfade error, trying fallback concat...")
        print(f"  stderr: {result.stderr[-300:]}")
        _fallback_concat(tmp_dir, scenes, output_path)

    return output_path


def _fallback_concat(tmp_dir, scenes, output_path):
    """Simple concat without xfade."""
    parts = []
    for i, sc in enumerate(scenes):
        part = os.path.join(tmp_dir, f"part{i}.mp4")
        if sc["type"] == "zoompan":
            zp_frames = int(sc["dur"] * FPS)
            z_expr = f"1+0.10*(on/{zp_frames})"
            subprocess.run([
                "ffmpeg", "-y", "-i", sc["path"],
                "-vf", (f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                        f":d={zp_frames}:s={W}x{H}:fps={FPS},format=yuv420p"),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", part
            ], capture_output=True)
        else:
            fade = f"fade=t=in:st=0:d=0.5," if i == 0 else ""
            subprocess.run([
                "ffmpeg", "-y", "-loop", "1", "-i", sc["path"],
                "-t", str(sc["dur"]), "-r", str(FPS),
                "-vf", f"{fade}scale={W}:{H},format=yuv420p",
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", part
            ], capture_output=True)
        parts.append(part)

    concat_file = os.path.join(tmp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")

    total = sum(s["dur"] for s in scenes)
    music_track = _pick_music_track()
    audio_args = ["-i", music_track, "-af",
                  f"atrim=0:{total},afade=out:st={total-2}:d=2"] if music_track else \
                 ["-f", "lavfi", "-i",
                  f"anullsrc=channel_layout=stereo:sample_rate=44100:duration={total}"]

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        *audio_args,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        output_path
    ], capture_output=True)


def upload_to_supabase(local_path, slug):
    env = load_env(ENV_SUPABASE)
    url, key = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    filename = f"reels/{slug}.mp4"
    r = requests.post(
        f"{url}/storage/v1/object/article-images/{filename}",
        headers={"apikey": key, "Authorization": f"Bearer {key}",
                 "Content-Type": "video/mp4", "x-upsert": "true"},
        data=Path(local_path).read_bytes())
    if r.status_code in [200, 201]:
        return f"{url}/storage/v1/object/public/article-images/{filename}"
    print(f"  ⚠️  Upload failed: {r.status_code} {r.text[:200]}")
    return None


# ── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate Instagram Reel for The Videshi")
    parser.add_argument("--slug", help="Article slug")
    parser.add_argument("--upload", action="store_true", help="Upload to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    print("🎬 The Videshi Reel Generator v4")
    print("=" * 50)

    article = fetch_article(args.slug)
    slug = article["slug"]
    print(f"📰 {article['headline']}")
    print(f"📁 {article.get('category', 'news')}")
    print(f"🔗 {slug}")
    if article.get("subheadline"):
        print(f"📝 Subheadline: {article['subheadline'][:80]}...")
    else:
        print("📝 No subheadline — will skip takeaways scene")

    if args.dry_run:
        hook = extract_hook(article["headline"])
        print(f"\n🎣 Hook text: {hook}")
        if article.get("subheadline"):
            bullets = split_subheadline(article["subheadline"])
            for i, b in enumerate(bullets):
                print(f"  • {b}")
        print("\n🏃 Dry run — skipping generation")
        return

    if not article.get("image_url"):
        sys.exit("❌ No image URL")

    OUTPUT_DIR.mkdir(exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="reel-")
    out = str(OUTPUT_DIR / f"reel-{slug[:80]}.mp4")

    try:
        print("\n⬇️  Downloading image...")
        img_path = os.path.join(tmp_dir, "article.jpg")

        # Try Wikipedia image first for person-specific articles
        wiki_img = fetch_wikipedia_image(article["headline"])
        if wiki_img:
            img_path = wiki_img
            print(f"  ✓ Using Wikipedia image")
        else:
            download_image(article["image_url"], img_path)
            # Validate the downloaded image
            try:
                test = Image.open(img_path)
                test.verify()
                print(f"  ✓ Article image: {os.path.getsize(img_path)} bytes")
            except Exception:
                print(f"  ⚠️  Article image invalid ({os.path.getsize(img_path)} bytes), using branded fallback")
                # Create a branded fallback image (navy bg with logo)
                fb = Image.new("RGB", (W, H), NAVY)
                fbd = ImageDraw.Draw(fb)
                # THE VIDESHI logo centered
                logo_f = ImageFont.truetype(FONT_EXTRABOLD, 72)
                logo_txt = "THE VIDESHI"
                lb = fbd.textbbox((0, 0), logo_txt, font=logo_f)
                fbd.text(((W - (lb[2]-lb[0]))//2, (H - (lb[3]-lb[1]))//2), logo_txt, font=logo_f, fill=GOLD)
                fb.save(img_path, quality=95)

        # Build scene list
        scene_list = []

        print("🎣 Scene 1 (hook)...")
        t0 = time.time()
        hook_png = render_hook(article, tmp_dir, img_path)
        hook_text = extract_hook(article["headline"])
        print(f"  ✓ \"{hook_text}\" ({time.time()-t0:.1f}s)")
        scene_list.append({"type": "static", "path": hook_png, "dur": HOOK_DUR})

        print("🖼️  Scene 2 (image + headline)...")
        t0 = time.time()
        img_scene, iw, ih = render_image_scene(article, tmp_dir, img_path)
        print(f"  ✓ prepared {iw}x{ih} ({time.time()-t0:.1f}s)")
        scene_list.append({"type": "zoompan", "path": img_scene, "dur": IMAGE_DUR,
                          "zw": iw, "zh": ih})

        # Save Scene 2 as cover image for Instagram (thumb_offset unreliable)
        cover_path = str(OUTPUT_DIR / f"reel-{slug[:80]}-cover.jpg")
        cover_img = Image.open(img_scene)
        # Crop to 1080x1920 from center of the zoompan source
        cw, ch = cover_img.size
        cx0, cy0 = (cw - W) // 2, (ch - H) // 2
        cover_img = cover_img.crop((cx0, cy0, cx0 + W, cy0 + H))
        cover_img.save(cover_path, quality=90)
        print(f"  📸 Cover image saved: {cover_path}")

        if article.get("subheadline"):
            print("📋 Scene 3 (key takeaways)...")
            t0 = time.time()
            takeaways_png = render_takeaways(article, tmp_dir)
            if takeaways_png:
                bullets = split_subheadline(article["subheadline"])
                print(f"  ✓ {len(bullets)} bullet(s) ({time.time()-t0:.1f}s)")
                scene_list.append({"type": "static", "path": takeaways_png, "dur": BULLET_DUR})
            else:
                print("  ⚠️  Skipped (empty)")
        else:
            print("📋 Scene 3 — skipped (no subheadline)")

        print("✨ Scene 4 (CTA)...")
        t0 = time.time()
        cta_png = render_cta(article, tmp_dir)
        print(f"  ✓ {time.time()-t0:.1f}s")
        scene_list.append({"type": "static", "path": cta_png, "dur": CTA_DUR})

        expected_dur = sum(s["dur"] for s in scene_list) - XFADE_DUR * (len(scene_list) - 1)
        print(f"\n🔗 Assembling {len(scene_list)}-scene reel (~{expected_dur:.0f}s)...")
        t0 = time.time()
        assemble_reel(tmp_dir, scene_list, out)
        print(f"  ✓ {time.time()-t0:.1f}s")

        # Verify
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", out],
            capture_output=True, text=True)
        info = json.loads(probe.stdout)
        dur = float(info["format"]["duration"])
        sz = os.path.getsize(out) / (1024 * 1024)

        print(f"\n✅ Reel generated!")
        print(f"  📁 {out}")
        print(f"  ⏱️  {dur:.1f}s")
        print(f"  📐 {W}x{H}")
        print(f"  💾 {sz:.1f}MB")

        if args.upload:
            print("\n☁️  Uploading...")
            pub_url = upload_to_supabase(out, slug[:80])
            if pub_url:
                print(f"  ✅ {pub_url}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
