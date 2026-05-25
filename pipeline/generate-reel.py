#!/usr/bin/env python3
"""
The Videshi — Instagram Reel Generator
Generates 9:16 vertical video (1080x1920) from an article for Instagram Reels.

Usage:
  python3 generate-reel.py                    # Latest unposted article
  python3 generate-reel.py --slug my-article  # Specific article
  python3 generate-reel.py --dry-run          # Preview without generating
  python3 generate-reel.py --upload            # Also upload to Supabase storage
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REELS_DIR = SCRIPT_DIR / "reels"
REELS_DIR.mkdir(exist_ok=True)

WIDTH, HEIGHT = 1080, 1920
DURATION = 12  # seconds
FPS = 25
TOTAL_FRAMES = DURATION * FPS

FONT_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not os.path.exists(FONT_REGULAR):
    FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GOLD = "#d4a843"
GOLD_RGB = "0xd4a843"

# Category colors for the pill badge
CATEGORY_COLORS = {
    "news": "#e74c3c",
    "immigration": "#3498db",
    "sports": "#27ae60",
    "entertainment": "#9b59b6",
    "lifestyle": "#e67e22",
    "travel": "#1abc9c",
    "markets": "#f39c12",
    "technology": "#2980b9",
    "food": "#d35400",
    "nri-world": "#8e44ad",
}


def load_supabase_env():
    """Load Supabase credentials."""
    env = {}
    env_path = Path.home() / "workspace" / ".env.supabase"
    with open(env_path) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    return env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]


def fetch_article(sb_url, sb_key, slug=None):
    """Fetch article from Supabase."""
    headers = {"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
    fields = "id,slug,headline,subheadline,category,image_url"

    if slug:
        r = requests.get(
            f"{sb_url}/rest/v1/p2_articles?slug=eq.{slug}&select={fields}",
            headers=headers,
        )
    else:
        r = requests.get(
            f"{sb_url}/rest/v1/p2_articles?status=eq.published"
            f"&instagrammed_at=is.null&image_url=not.is.null"
            f"&order=published_at.desc&limit=1&select={fields}",
            headers=headers,
        )

    data = r.json()
    if not data:
        print("❌ No article found.")
        sys.exit(1)
    return data[0]


def download_image(url, dest):
    """Download image to local path."""
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(dest, "wb") as f:
        f.write(r.content)
    return dest


def prepare_background(img_path, out_path):
    """Scale and crop image to exactly 1080x1920 (cover fit)."""
    img = Image.open(img_path)
    w, h = img.size

    # Compute scale to cover 1080x1920
    scale = max(WIDTH / w, HEIGHT / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop to 1080x1920
    left = (new_w - WIDTH) // 2
    top = (new_h - HEIGHT) // 2
    img = img.crop((left, top, left + WIDTH, top + HEIGHT))
    img.save(out_path, quality=95)
    return out_path


def create_gradient_overlay(out_path):
    """Create a gradient overlay PNG: transparent top → dark bottom."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Bottom 60% gets a gradient
    gradient_start = int(HEIGHT * 0.35)
    for y in range(gradient_start, HEIGHT):
        progress = (y - gradient_start) / (HEIGHT - gradient_start)
        # Ease in for smoother gradient
        alpha = int(220 * (progress ** 1.5))
        alpha = min(alpha, 220)
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, alpha))

    # Also add a subtle top vignette for the category tag
    for y in range(0, int(HEIGHT * 0.15)):
        progress = 1 - (y / (HEIGHT * 0.15))
        alpha = int(100 * (progress ** 2))
        draw.rectangle([(0, y), (WIDTH, y + 1)], fill=(0, 0, 0, alpha))

    img.save(out_path)
    return out_path


def create_category_badge(category, out_path):
    """Create a category pill badge PNG."""
    cat_upper = (category or "news").upper().replace("-", " ")
    color_hex = CATEGORY_COLORS.get(category, "#555555")
    r_c, g_c, b_c = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)

    try:
        font = ImageFont.truetype(FONT_BOLD, 28)
    except Exception:
        font = ImageFont.load_default()

    # Measure text
    dummy = Image.new("RGBA", (1, 1))
    dd = ImageDraw.Draw(dummy)
    bbox = dd.textbbox((0, 0), cat_upper, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    pad_x, pad_y = 24, 12
    pill_w = tw + pad_x * 2
    pill_h = th + pad_y * 2
    radius = pill_h // 2

    img = Image.new("RGBA", (pill_w, pill_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle
    draw.rounded_rectangle(
        [(0, 0), (pill_w - 1, pill_h - 1)],
        radius=radius,
        fill=(r_c, g_c, b_c, 230),
    )

    # Text centered
    tx = (pill_w - tw) // 2 - bbox[0]
    ty = (pill_h - th) // 2 - bbox[1]
    draw.text((tx, ty), cat_upper, font=font, fill=(255, 255, 255, 255))

    img.save(out_path)
    return out_path, pill_w, pill_h


def create_text_overlay(headline, category, out_path):
    """Create the full text overlay PNG with headline + branding."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── Headline ──
    # Truncate if super long — cut at word boundary
    if len(headline) > 150:
        headline = headline[:150]
        # Cut at last space for clean word break
        last_space = headline.rfind(" ")
        if last_space > 100:
            headline = headline[:last_space] + "..."
        else:
            headline = headline + "..."

    try:
        font_headline = ImageFont.truetype(FONT_BOLD, 52)
        font_brand = ImageFont.truetype(FONT_BOLD, 36)
        font_url = ImageFont.truetype(FONT_REGULAR, 26)
    except Exception:
        font_headline = ImageFont.load_default()
        font_brand = font_headline
        font_url = font_headline

    # Word wrap headline to fit ~900px
    max_chars = 28  # rough chars per line at font size 52 in 900px
    lines = []
    for para in headline.split("\n"):
        lines.extend(textwrap.wrap(para, width=max_chars))

    # Limit to 6 lines max
    if len(lines) > 6:
        lines = lines[:6]
        lines[-1] = lines[-1][:max_chars - 3] + "..."

    # Calculate total text block height
    line_height = 64  # px per line
    text_block_h = len(lines) * line_height

    # Position: headline ends ~280px from bottom
    headline_bottom = HEIGHT - 260
    headline_top = headline_bottom - text_block_h

    # Draw each line
    x_margin = 80
    for i, line in enumerate(lines):
        y = headline_top + i * line_height
        # Drop shadow
        draw.text((x_margin + 2, y + 2), line, font=font_headline, fill=(0, 0, 0, 180))
        # Main text
        draw.text((x_margin, y), line, font=font_headline, fill=(255, 255, 255, 255))

    # ── Gold accent line (static, below headline) ──
    line_y = headline_bottom + 20
    draw.rectangle(
        [(x_margin, line_y), (x_margin + 120, line_y + 4)],
        fill=(212, 168, 67, 255),
    )

    # ── Branding at bottom ──
    brand_text = "THE VIDESHI"
    brand_bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    brand_w = brand_bbox[2] - brand_bbox[0]
    brand_x = (WIDTH - brand_w) // 2
    brand_y = HEIGHT - 150

    draw.text((brand_x, brand_y), brand_text, font=font_brand, fill=(212, 168, 67, 255))

    url_text = "thevideshi.com"
    url_bbox = draw.textbbox((0, 0), url_text, font=font_url)
    url_w = url_bbox[2] - url_bbox[0]
    url_x = (WIDTH - url_w) // 2
    url_y = brand_y + 50

    draw.text((url_x, url_y), url_text, font=font_url, fill=(255, 255, 255, 200))

    img.save(out_path)
    return out_path


def create_gold_line_animation(out_dir, frames=TOTAL_FRAMES):
    """Create frame sequence for the animated gold accent line.
    
    Line draws from left to right over first 2 seconds (50 frames).
    """
    line_dir = Path(out_dir) / "gold_line"
    line_dir.mkdir(exist_ok=True)

    max_width = 920  # full line width
    x_start = 80
    line_y = 0  # will be composited at correct position
    anim_frames = FPS * 2  # 2 seconds

    for i in range(frames):
        img = Image.new("RGBA", (WIDTH, 10), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if i < anim_frames:
            progress = i / anim_frames
            # Ease out
            progress = 1 - (1 - progress) ** 3
            current_w = int(max_width * progress)
        else:
            current_w = max_width

        if current_w > 0:
            draw.rectangle(
                [(x_start, 3), (x_start + current_w, 7)],
                fill=(212, 168, 67, 255),
            )

        img.save(line_dir / f"frame_{i:04d}.png")

    return str(line_dir / "frame_%04d.png")


def generate_reel(article, upload=False):
    """Generate the actual reel video."""
    slug = article["slug"]
    headline = article["headline"]
    category = article.get("category", "news")
    image_url = article["image_url"]

    print(f"🎬 Generating reel for: {headline[:60]}...")
    print(f"   Category: {category}")
    print(f"   Image: {image_url[:60]}...")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. Download and prepare background image
        raw_img = tmpdir / "raw.jpg"
        bg_img = tmpdir / "bg.jpg"
        print("   📥 Downloading image...")
        download_image(image_url, raw_img)
        prepare_background(raw_img, bg_img)

        # 2. Create gradient overlay
        gradient = tmpdir / "gradient.png"
        create_gradient_overlay(gradient)

        # 3. Create category badge
        badge, badge_w, badge_h = create_category_badge(category, tmpdir / "badge.png")

        # 4. Create text overlay
        text_overlay = tmpdir / "text.png"
        create_text_overlay(headline, category, text_overlay)

        # 5. Build ffmpeg command
        out_file = REELS_DIR / f"reel-{slug}.mp4"

        # Badge position: centered at top
        badge_x = (WIDTH - badge_w) // 2
        badge_y = 80

        # Using ffmpeg filter chain:
        # - zoompan on background for Ken Burns
        # - overlay gradient
        # - overlay badge
        # - overlay text
        # The gold line animation is baked into the text overlay approach
        # for simplicity — we'll use the static gold line from the text overlay
        # and add a subtle fade-in via ffmpeg

        cmd = [
            "ffmpeg", "-y",
            # Input 0: background image
            "-loop", "1", "-i", str(bg_img),
            # Input 1: gradient overlay
            "-loop", "1", "-i", str(gradient),
            # Input 2: category badge
            "-loop", "1", "-i", str(badge),
            # Input 3: text overlay
            "-loop", "1", "-i", str(text_overlay),
            # Input 4: silent audio
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            # Filter complex
            "-filter_complex",
            # Scale background slightly larger for zoom headroom
            f"[0:v]scale=1296:2304,zoompan=z='1.0+0.012*on/{TOTAL_FRAMES}'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={TOTAL_FRAMES}:s={WIDTH}x{HEIGHT}:fps={FPS}[bg];"
            # Overlay gradient
            f"[bg][1:v]overlay=0:0:shortest=1:format=auto[bg_grad];"
            # Overlay category badge with fade in (0.5s delay, 0.5s fade)
            f"[2:v]format=rgba,fade=in:st=0.3:d=0.5:alpha=1[badge_fade];"
            f"[bg_grad][badge_fade]overlay={badge_x}:{badge_y}:shortest=1:format=auto[bg_badge];"
            # Overlay text with fade in (0.8s delay, 0.8s fade)
            f"[3:v]format=rgba,fade=in:st=0.5:d=0.8:alpha=1[text_fade];"
            f"[bg_badge][text_fade]overlay=0:0:shortest=1:format=auto[out]",
            "-map", "[out]",
            "-map", "4:a",
            "-t", str(DURATION),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-c:a", "aac",
            "-shortest",
            str(out_file),
        ]

        print("   🔨 Running ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            print(f"   ❌ ffmpeg failed:\n{result.stderr[-1000:]}")
            sys.exit(1)

        # Verify output
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", str(out_file)],
            capture_output=True, text=True,
        )
        info = json.loads(probe.stdout)
        duration = float(info["format"]["duration"])
        size_mb = os.path.getsize(out_file) / (1024 * 1024)

        print(f"\n   ✅ Reel generated!")
        print(f"   📁 {out_file}")
        print(f"   ⏱  {duration:.1f}s | 📦 {size_mb:.1f}MB")

        # Upload to Supabase if requested
        if upload:
            print("   ☁️  Uploading to Supabase storage...")
            sb_url, sb_key = load_supabase_env()
            storage_path = f"reels/{slug}.mp4"
            public_url = f"{sb_url}/storage/v1/object/public/article-images/{storage_path}"
            upload_url = f"{sb_url}/storage/v1/object/article-images/{storage_path}"
            try:
                # Use curl for large file upload (more reliable than requests)
                result = subprocess.run(
                    [
                        "curl", "-s", "-w", "%{http_code}", "-o", "/dev/null",
                        "-X", "POST", upload_url,
                        "-H", f"apikey: {sb_key}",
                        "-H", f"Authorization: Bearer {sb_key}",
                        "-H", "Content-Type: video/mp4",
                        "-H", "x-upsert: true",
                        "--data-binary", f"@{out_file}",
                        "--max-time", "60",
                    ],
                    capture_output=True, text=True, timeout=90,
                )
                status_code = result.stdout.strip()
                if status_code in ["200", "201"]:
                    print(f"   🔗 {public_url}")
                else:
                    print(f"   ⚠️  Upload returned HTTP {status_code}")
            except Exception as e:
                print(f"   ⚠️  Upload failed: {e}")
                print(f"   📁 Local file still available at: {out_file}")

        return str(out_file)


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram Reel for The Videshi")
    parser.add_argument("--slug", help="Article slug (default: latest unposted)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    parser.add_argument("--upload", action="store_true", help="Upload to Supabase storage")
    args = parser.parse_args()

    sb_url, sb_key = load_supabase_env()
    article = fetch_article(sb_url, sb_key, slug=args.slug)

    print(f"\n{'='*60}")
    print(f"🎞  The Videshi — Reel Generator")
    print(f"{'='*60}")
    print(f"Article: {article['headline'][:80]}...")
    print(f"Slug:    {article['slug']}")
    print(f"Cat:     {article.get('category', 'news')}")
    print(f"Image:   {article['image_url'][:60]}...")
    print(f"{'='*60}\n")

    if args.dry_run:
        print("🏃 Dry run — would generate reel for above article.")
        return

    generate_reel(article, upload=args.upload)


if __name__ == "__main__":
    main()
