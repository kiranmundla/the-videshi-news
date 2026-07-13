#!/usr/bin/env python3
"""
article-cards.py — Generate branded 4:5 portrait cards from article hero images.

Each card: hero image fills top, navy gradient bar at bottom with headline + category.
Output: 1080×1350 JPEG, uploaded to Supabase storage, URL saved in article_cards JSON feed.

Usage:
  python3 article-cards.py [--category sports] [--limit 10] [--preview]
  --preview: generate cards to /tmp and skip upload (for testing)
"""

import os, sys, json, hashlib, subprocess, textwrap, argparse
from io import BytesIO
from pathlib import Path

# Pillow
from PIL import Image, ImageDraw, ImageFont

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
DB_HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

PIPELINE_DIR = Path(__file__).parent
ASSETS_DIR = PIPELINE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "logo-transparent.png"
OUTPUT_DIR = Path(os.path.expanduser("~/workspace/the-videshi-news/public/data"))

# Card dimensions (4:5 portrait)
CARD_W, CARD_H = 1080, 1350

# Brand colors
NAVY = (11, 29, 58)        # #0B1D3A
GOLD = (212, 168, 67)      # #D4A843
WHITE = (255, 255, 255)
LIGHT_GRAY = (203, 213, 225)

# Fonts
FONT_DIR = PIPELINE_DIR / "fonts"

def get_font(name, size):
    """Try to load a font, fall back to default."""
    candidates = [
        FONT_DIR / name,
        Path(f"/usr/share/fonts/truetype/{name}"),
        Path(f"/usr/share/fonts/{name}"),
    ]
    for p in candidates:
        if p.exists():
            return ImageFont.truetype(str(p), size)
    # fallback: try system
    try:
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()


# ─── Category config ─────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "immigration": "#A32D2D",
    "technology": "#2563EB",
    "entertainment": "#9333EA",
    "sports": "#16A34A",
    "news": "#DC2626",
    "markets-finance": "#D97706",
    "nri-world": "#0891B2",
    "travel": "#0D9488",
    "lifestyle-health": "#EC4899",
    "food": "#EA580C",
}

CATEGORY_LABELS = {
    "immigration": "IMMIGRATION",
    "technology": "TECHNOLOGY",
    "entertainment": "ENTERTAINMENT",
    "sports": "SPORTS",
    "news": "NEWS",
    "markets-finance": "MARKETS & FINANCE",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "food": "FOOD",
}


# ─── Image download ──────────────────────────────────────────────────────────

def download_image(url, timeout=15):
    """Download image via curl, return PIL Image or None."""
    tmp = f"/tmp/card_hero_{hashlib.md5(url.encode()).hexdigest()[:12]}.jpg"
    result = subprocess.run(
        ["curl", "-sS", "-L", "-o", tmp, "--max-time", str(timeout),
         "-A", "TheVideshi/1.0 (thevideshi.com)", url],
        capture_output=True, timeout=timeout+5
    )
    if result.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) < 1000:
        return None
    try:
        return Image.open(tmp).convert("RGB")
    except:
        return None


# ─── Card generation ─────────────────────────────────────────────────────────

def generate_card(article):
    """Generate a branded 4:5 card from an article dict. Returns PIL Image or None."""
    hero = download_image(article["image_url"])
    if not hero:
        return None

    # Create canvas
    card = Image.new("RGB", (CARD_W, CARD_H), NAVY)

    # --- Hero image: fills almost everything, crop to fit ---
    # Scale hero to fill full card width, crop vertically (top-biased for faces)
    scale = CARD_W / hero.width
    scaled_h = int(hero.height * scale)
    hero_resized = hero.resize((CARD_W, scaled_h), Image.LANCZOS)

    if scaled_h >= CARD_H:
        # Crop — top-biased (keep faces)
        crop_top = min(int(scaled_h * 0.08), scaled_h - CARD_H)
        hero_cropped = hero_resized.crop((0, crop_top, CARD_W, crop_top + CARD_H))
    else:
        # Image shorter — center it
        hero_cropped = hero_resized
        y_offset = (CARD_H - scaled_h) // 2
        card.paste(hero_cropped, (0, y_offset))
        hero_cropped = None

    if hero_cropped:
        card.paste(hero_cropped, (0, 0))

    # --- Bottom gradient overlay (subtle, just enough for text) ---
    overlay = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    gradient_h = 420
    gradient_start = CARD_H - gradient_h
    for y in range(gradient_h):
        alpha = int(220 * (y / gradient_h) ** 2.0)
        draw_overlay.rectangle(
            [(0, gradient_start + y), (CARD_W, gradient_start + y + 1)],
            fill=(0, 0, 0, alpha)
        )
    card = Image.alpha_composite(card.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(card)

    # --- Category pill (small, above headline) ---
    cat = article.get("category", "news")
    cat_color = CATEGORY_COLORS.get(cat, "#64748B")
    cat_label = CATEGORY_LABELS.get(cat, cat.upper())
    cat_font = get_font("InterDisplay-Bold.otf", 20)

    cc = cat_color.lstrip('#')
    pill_rgb = tuple(int(cc[i:i+2], 16) for i in (0, 2, 4))

    # Position from bottom
    headline_font = get_font("NotoSerif-Bold.ttf", 36)
    headline = article["headline"]

    # Short wrap — max 4 lines
    lines = textwrap.wrap(headline, width=32)
    max_lines = 4
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        if len(last) > 28:
            lines[-1] = last[:28] + "…"

    line_spacing = 44
    total_text_h = len(lines) * line_spacing
    headline_y = CARD_H - total_text_h - 70

    # Category pill just above headline
    pill_y = headline_y - 38
    pill_x = 40
    cat_bbox = draw.textbbox((0, 0), cat_label, font=cat_font)
    cat_w = cat_bbox[2] - cat_bbox[0]
    cat_h = cat_bbox[3] - cat_bbox[1]
    pill_pad_x, pill_pad_y = 12, 5
    draw.rounded_rectangle(
        [(pill_x, pill_y), (pill_x + cat_w + pill_pad_x * 2, pill_y + cat_h + pill_pad_y * 2)],
        radius=5,
        fill=pill_rgb
    )
    draw.text((pill_x + pill_pad_x, pill_y + pill_pad_y - 1), cat_label, font=cat_font, fill=WHITE)

    # --- Headline (white, bold, over gradient) ---
    for i, line in enumerate(lines):
        draw.text(
            (40, headline_y + i * line_spacing),
            line,
            font=headline_font,
            fill=WHITE
        )

    # --- Small branding bottom-right ---
    brand_font = get_font("InterDisplay-Bold.otf", 16)
    brand_text = "THEVIDESHI.COM"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=brand_font)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text((CARD_W - brand_w - 40, CARD_H - 40), brand_text, font=brand_font, fill=GOLD)

    return card


# ─── Upload to Supabase storage ──────────────────────────────────────────────

def upload_card(card_img, slug):
    """Upload card JPEG to Supabase storage. Returns public URL or None."""
    buf = BytesIO()
    card_img.save(buf, format="JPEG", quality=88, optimize=True)
    buf.seek(0)

    bucket = "article-cards"
    path = f"{slug}.jpg"
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"

    result = subprocess.run(
        ["curl", "-sS", "-X", "POST", upload_url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", "@-"],
        input=buf.read(), capture_output=True, timeout=30
    )

    if result.returncode == 0:
        try:
            resp = json.loads(result.stdout)
            if "Key" in resp or "Id" in resp:
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
                return public_url
        except:
            pass

    # Check if error
    print(f"  ⚠ Upload failed for {slug}: {result.stdout.decode()[:200]}", file=sys.stderr)
    return None


# ─── Main ─────────────────────────────────────────────────────────────────────

def fetch_articles(category=None, limit=12):
    """Fetch recent published articles via curl."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&image_url=not.is.null&order=published_at.desc&limit={limit}&select=slug,headline,image_url,category"
    if category:
        url += f"&category=eq.{category}"

    result = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, timeout=15
    )
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default=None, help="Filter by category")
    parser.add_argument("--limit", type=int, default=12, help="Max articles")
    parser.add_argument("--preview", action="store_true", help="Save to /tmp, skip upload")
    args = parser.parse_args()

    articles = fetch_articles(category=args.category, limit=args.limit)
    print(f"📸 Generating cards for {len(articles)} articles...")

    results = []
    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article['headline'][:60]}...")
        card = generate_card(article)
        if not card:
            print(f"    ⚠ Failed to generate (bad hero image)")
            continue

        if args.preview:
            out_path = f"/tmp/card_{article['slug'][:40]}.jpg"
            card.save(out_path, quality=88)
            print(f"    ✓ Preview: {out_path}")
            results.append({
                "slug": article["slug"],
                "headline": article["headline"],
                "category": article["category"],
                "card_url": out_path,
            })
        else:
            card_url = upload_card(card, article["slug"])
            if card_url:
                print(f"    ✓ Uploaded")
                results.append({
                    "slug": article["slug"],
                    "headline": article["headline"],
                    "category": article["category"],
                    "card_url": card_url,
                })
            else:
                print(f"    ⚠ Upload failed")

    print(f"\n✅ {len(results)}/{len(articles)} cards generated")

    # Write feed JSON
    if not args.preview:
        feed_path = OUTPUT_DIR / "article-cards.json"
        feed_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"📄 Feed: {feed_path}")

    return results


if __name__ == "__main__":
    main()
