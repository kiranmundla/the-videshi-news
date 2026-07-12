#!/usr/bin/env python3
"""
article-cards-v2.py — Moneycontrol-style designed article cards.
Design-forward, not photo-forward: bold category gradients, hero as accent, headline as star.
"""

import os, sys, json, hashlib, subprocess, textwrap, math
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ─── Env ──────────────────────────────────────────────────────────────────────
def load_env(path):
    p = os.path.expanduser(path)
    if os.path.exists(p):
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env("~/workspace/.env.supabase")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

PIPELINE_DIR = Path(__file__).parent
FONT_DIR = PIPELINE_DIR / "fonts"

CARD_W, CARD_H = 1080, 1350
NAVY = (11, 29, 58)
GOLD = (212, 168, 67)
WHITE = (255, 255, 255)
DARK = (8, 15, 35)

def get_font(name, size):
    for p in [FONT_DIR / name, Path(f"/usr/share/fonts/truetype/{name}")]:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    try:
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

# Category themes: (primary, secondary, accent)
CATEGORY_THEMES = {
    "immigration":     ((163, 45, 45),   (90, 20, 20),    (255, 120, 120)),
    "technology":      ((30, 64, 175),   (15, 30, 100),   (100, 160, 255)),
    "entertainment":   ((130, 40, 180),  (60, 15, 100),   (200, 140, 255)),
    "sports":          ((20, 120, 50),   (10, 60, 25),    (80, 220, 120)),
    "news":            ((180, 30, 30),   (90, 15, 15),    (255, 100, 100)),
    "markets-finance": ((200, 120, 10),  (100, 60, 5),    (255, 200, 80)),
    "nri-world":       ((8, 130, 170),   (4, 65, 90),     (80, 200, 240)),
    "travel":          ((13, 148, 136),  (6, 74, 68),     (80, 220, 210)),
    "lifestyle-health":((220, 60, 140),  (110, 30, 70),   (255, 140, 200)),
    "food":            ((220, 80, 10),   (110, 40, 5),    (255, 160, 80)),
}

CATEGORY_LABELS = {
    "immigration": "IMMIGRATION", "technology": "TECHNOLOGY",
    "entertainment": "ENTERTAINMENT", "sports": "SPORTS",
    "news": "NEWS", "markets-finance": "MARKETS & FINANCE",
    "nri-world": "NRI WORLD", "travel": "TRAVEL",
    "lifestyle-health": "LIFESTYLE", "food": "FOOD",
}

def download_image(url, timeout=15):
    tmp = f"/tmp/card_hero_{hashlib.md5(url.encode()).hexdigest()[:12]}.jpg"
    r = subprocess.run(
        ["curl", "-sS", "-L", "-o", tmp, "--max-time", str(timeout),
         "-A", "TheVideshi/1.0 (thevideshi.com)", url],
        capture_output=True, timeout=timeout+5
    )
    if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) < 1000:
        return None
    try:
        return Image.open(tmp).convert("RGB")
    except:
        return None

def draw_gradient(draw, x1, y1, x2, y2, color1, color2, direction="vertical"):
    """Draw a smooth gradient."""
    if direction == "vertical":
        h = y2 - y1
        for y in range(h):
            t = y / max(h - 1, 1)
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            draw.line([(x1, y1 + y), (x2, y1 + y)], fill=(r, g, b))
    else:
        w = x2 - x1
        for x in range(w):
            t = x / max(w - 1, 1)
            r = int(color1[0] + (color2[0] - color1[0]) * t)
            g = int(color1[1] + (color2[1] - color1[1]) * t)
            b = int(color1[2] + (color2[2] - color1[2]) * t)
            draw.line([(x1 + x, y1), (x1 + x, y2)], fill=(r, g, b))

def draw_accent_elements(draw, primary, accent, card_w, card_h):
    """Add subtle geometric design elements."""
    # Diagonal accent lines (top right)
    for i in range(3):
        offset = 60 + i * 25
        alpha_color = (
            min(accent[0], 255),
            min(accent[1], 255),
            min(accent[2], 255),
        )
        draw.line(
            [(card_w - 200 + offset, 0), (card_w, 200 - offset)],
            fill=alpha_color, width=2
        )

    # Small dots pattern (top left)
    dot_color = (primary[0] + 30, primary[1] + 30, primary[2] + 30)
    for row in range(4):
        for col in range(4):
            x = 40 + col * 18
            y = 40 + row * 18
            draw.ellipse([(x, y), (x + 4, y + 4)], fill=dot_color)

    # Bottom accent bar
    draw.rectangle([(0, card_h - 6), (card_w, card_h)], fill=GOLD)

def make_rounded_mask(size, radius):
    """Create a rounded rectangle mask."""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask

def generate_card(article):
    """Generate a Moneycontrol-style designed card."""
    hero = download_image(article["image_url"])
    if not hero:
        return None

    cat = article.get("category", "news")
    primary, secondary, accent = CATEGORY_THEMES.get(cat, CATEGORY_THEMES["news"])
    cat_label = CATEGORY_LABELS.get(cat, cat.upper())

    # Create canvas with gradient background
    card = Image.new("RGB", (CARD_W, CARD_H), DARK)
    draw = ImageDraw.Draw(card)

    # Full gradient: category primary → dark navy
    draw_gradient(draw, 0, 0, CARD_W, CARD_H, primary, DARK)

    # Add subtle geometric accents
    draw_accent_elements(draw, primary, accent, CARD_W, CARD_H)

    # ─── Hero image as rounded inset (top portion) ─────────────
    img_margin = 50
    img_w = CARD_W - img_margin * 2
    img_h = 580
    img_x, img_y = img_margin, 80

    # Scale and crop hero to fill inset
    scale = max(img_w / hero.width, img_h / hero.height)
    scaled_w = int(hero.width * scale)
    scaled_h = int(hero.height * scale)
    hero_resized = hero.resize((scaled_w, scaled_h), Image.LANCZOS)

    # Center crop
    cx = (scaled_w - img_w) // 2
    cy = min(int(scaled_h * 0.08), scaled_h - img_h)  # top-biased for faces
    hero_crop = hero_resized.crop((cx, cy, cx + img_w, cy + img_h))

    # Apply slight darkening at bottom of image for blend
    img_overlay = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    img_draw = ImageDraw.Draw(img_overlay)
    for y in range(100):
        a = int(120 * (y / 100) ** 2)
        img_draw.line([(0, img_h - 100 + y), (img_w, img_h - 100 + y)],
                      fill=(0, 0, 0, a))
    hero_rgba = hero_crop.convert("RGBA")
    hero_blended = Image.alpha_composite(hero_rgba, img_overlay).convert("RGB")

    # Paste with rounded corners
    mask = make_rounded_mask((img_w, img_h), 20)
    card.paste(hero_blended, (img_x, img_y), mask)

    # Thin border around image
    border_draw = ImageDraw.Draw(card)
    border_draw.rounded_rectangle(
        [(img_x - 1, img_y - 1), (img_x + img_w, img_y + img_h)],
        radius=20,
        outline=(255, 255, 255, 40),
        width=2
    )

    # ─── Category pill ─────────────────────────────────────────
    cat_font = get_font("InterDisplay-Bold.otf", 24)
    pill_y = img_y + img_h + 35
    pill_x = img_margin

    cat_bbox = draw.textbbox((0, 0), cat_label, font=cat_font)
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_h = cat_bbox[3] - cat_bbox[1]
    pad_x, pad_y = 16, 8

    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + cat_w + pad_x * 2, pill_y + cat_h + pad_y * 2)],
        radius=6, fill=primary
    )
    draw.text((pill_x + pad_x, pill_y + pad_y - 2), cat_label, font=cat_font, fill=WHITE)

    # ─── Headline ──────────────────────────────────────────────
    headline_font = get_font("NotoSerif-Bold.ttf", 44)
    headline = article["headline"]

    lines = textwrap.wrap(headline, width=26)
    max_lines = 4
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        if len(last) > 23:
            lines[-1] = last[:23] + "…"

    headline_y = pill_y + cat_h + pad_y * 2 + 25
    line_spacing = 56
    for i, line in enumerate(lines):
        draw.text(
            (img_margin, headline_y + i * line_spacing),
            line, font=headline_font, fill=WHITE
        )

    # ─── Gold accent line below headline ───────────────────────
    accent_y = headline_y + len(lines) * line_spacing + 14
    draw.rectangle([(img_margin, accent_y), (img_margin + 80, accent_y + 4)], fill=GOLD)

    # ─── Branding ──────────────────────────────────────────────
    brand_font = get_font("InterDisplay-Bold.otf", 20)
    brand_text = "THEVIDESHI.COM"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text((CARD_W - brand_w - img_margin, CARD_H - 50), brand_text, font=brand_font, fill=GOLD)

    # Small logo icon (V mark)
    logo_path = PIPELINE_DIR / "assets" / "logo-transparent.png"
    if logo_path.exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo = logo.resize((36, 36), Image.LANCZOS)
            card.paste(logo, (img_margin, CARD_H - 52), logo)
        except:
            pass

    return card


# ─── CLI ───────────────────────────────────────────────────────────────────────

def fetch_articles(category=None, limit=12):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&image_url=not.is.null&order=published_at.desc&limit={limit}&select=slug,headline,image_url,category"
    if category:
        url += f"&category=eq.{category}"
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, timeout=15
    )
    return json.loads(r.stdout)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default=None)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    articles = fetch_articles(category=args.category, limit=args.limit)
    print(f"📸 Generating v2 cards for {len(articles)} articles...")

    results = []
    for i, art in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {art['headline'][:55]}...")
        card = generate_card(art)
        if not card:
            print(f"    ⚠ Skip (bad hero image)")
            continue
        out = f"/tmp/cardv2_{art['slug'][:40]}.jpg"
        card.save(out, quality=90)
        print(f"    ✓ {out}")
        results.append({"slug": art["slug"], "headline": art["headline"],
                        "category": art["category"], "path": out})

    print(f"\n✅ {len(results)}/{len(articles)} cards generated")
    return results

if __name__ == "__main__":
    main()
