#!/usr/bin/env python3
"""
The Videshi — Instagram Reel Generator (v2)
3-scene reel: Headline Card → Article Image → CTA Card
Output: 1080x1920, ~14 seconds, H.264+AAC MP4
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

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

SCENE1_DUR = 5.0
SCENE2_DUR = 6.0
SCENE3_DUR = 4.0
XFADE_DUR  = 0.5

NAVY = (26, 26, 46)
GOLD = (212, 168, 67)
WHITE = (255, 255, 255)
WHITE_DIM = (200, 200, 210)

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
    if slug:
        r = requests.get(
            f"{url}/rest/v1/p2_articles?slug=eq.{slug}"
            "&select=id,slug,headline,subheadline,category,image_url",
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
                "&order=published_at.desc&limit=1"
                "&select=id,slug,headline,subheadline,category,image_url",
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


# ── Scene Renderers ────────────────────────────────────────────────────

def render_scene1(article, tmp_dir):
    """Headline card → single PNG, ffmpeg handles fade-in + duration."""
    headline = article["headline"]
    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # ── Category badge ──
    bf = ImageFont.truetype(FONT_BOLD, 28)
    bb = draw.textbbox((0, 0), cat_label, font=bf)
    bw, bh = bb[2]-bb[0]+50, bb[3]-bb[1]+28
    bx = (W - bw) // 2
    by = 280
    rounded_rect(draw, (bx, by, bx+bw, by+bh), 18, cat_color)
    tx = bx + (bw - (bb[2]-bb[0])) // 2
    ty = by + (bh - (bb[3]-bb[1])) // 2 - 2
    draw.text((tx, ty), cat_label, font=bf, fill=WHITE)

    # ── Headline ──
    pad = 90
    max_w = W - 2*pad
    zone_top = by + bh + 80
    zone_bot = H - 300
    max_h = zone_bot - zone_top

    font, lines, lh = fit_text(draw, headline, max_w, max_h, FONT_EXTRABOLD)
    total_h = lh * len(lines)
    y0 = zone_top + (max_h - total_h) // 2

    for i, line in enumerate(lines):
        y = y0 + i * lh
        draw.text((pad+3, y+3), line, font=font, fill=(0, 0, 0))  # shadow
        draw.text((pad, y), line, font=font, fill=WHITE)

    # ── Gold accent line ──
    ly = y0 + total_h + 35
    draw.rectangle([pad, ly, pad+120, ly+5], fill=GOLD)

    # ── Bottom branding ──
    brand_f = ImageFont.truetype(FONT_EXTRABOLD, 36)
    site_f = ImageFont.truetype(FONT_REGULAR, 24)
    for txt, f, color, yoff in [
        ("THE VIDESHI", brand_f, GOLD, H-180),
        ("thevideshi.com", site_f, WHITE_DIM, H-130),
    ]:
        bb = draw.textbbox((0, 0), txt, font=f)
        draw.text(((W - (bb[2]-bb[0])) // 2, yoff), txt, font=f, fill=color)

    out = os.path.join(tmp_dir, "scene1.png")
    img.save(out, quality=95)
    return out


def render_scene2_image(article, tmp_dir, img_path):
    """Prepare article image for Ken Burns — crop to 1080x1920, padded for zoom."""
    img = Image.open(img_path).convert("RGB")
    # Scale to cover 1080x1920 with 20% margin for zoom
    tw, th = int(W * 1.20), int(H * 1.20)
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((int(iw*scale), int(ih*scale)), Image.LANCZOS)
    # Center crop to tw x th
    nw, nh = img.size
    x0 = (nw - tw) // 2
    y0 = (nh - th) // 2
    img = img.crop((x0, y0, x0+tw, y0+th))

    out = os.path.join(tmp_dir, "scene2_src.png")
    img.save(out, quality=95)
    return out, tw, th


def render_scene3(tmp_dir):
    """CTA card → single PNG."""
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Decorative line
    draw.rectangle([W//2-100, 600, W//2+100, 603], fill=GOLD)

    # Brand
    bf = ImageFont.truetype(FONT_EXTRABOLD, 72)
    txt = "THE VIDESHI"
    bb = draw.textbbox((0, 0), txt, font=bf)
    draw.text(((W-(bb[2]-bb[0]))//2, 680), txt, font=bf, fill=GOLD)

    # Tagline
    tf = ImageFont.truetype(FONT_REGULAR, 32)
    tag = "Your daily source for Indian diaspora news"
    bb2 = draw.textbbox((0, 0), tag, font=tf)
    draw.text(((W-(bb2[2]-bb2[0]))//2, 790), tag, font=tf, fill=WHITE_DIM)

    # Divider
    draw.rectangle([W//2-60, 870, W//2+60, 873], fill=(*GOLD, ))

    # CTA
    cf = ImageFont.truetype(FONT_SEMIBOLD, 40)
    cta = "Read the full story"
    bb3 = draw.textbbox((0, 0), cta, font=cf)
    draw.text(((W-(bb3[2]-bb3[0]))//2, 940), cta, font=cf, fill=WHITE)

    # Link in bio
    lf = ImageFont.truetype(FONT_BOLD, 36)
    link = "Link in bio"
    bb4 = draw.textbbox((0, 0), link, font=lf)
    lx = (W-(bb4[2]-bb4[0]))//2
    # Arrow above
    af = ImageFont.truetype(FONT_BOLD, 44)
    arrow = "↑"
    ab = draw.textbbox((0, 0), arrow, font=af)
    draw.text(((W-(ab[2]-ab[0]))//2, 1005), arrow, font=af, fill=GOLD)
    draw.text((lx, 1060), link, font=lf, fill=GOLD)

    out = os.path.join(tmp_dir, "scene3.png")
    img.save(out, quality=95)
    return out


def assemble_reel(tmp_dir, s1_png, s2_src, s2_w, s2_h, s3_png, output_path):
    """Assemble 3 scenes with ffmpeg: fade-in, zoompan, crossfades, silent audio."""

    s1_dur = SCENE1_DUR
    s2_dur = SCENE2_DUR
    s3_dur = SCENE3_DUR
    xf = XFADE_DUR

    # Zoompan: zoom from 1.0 to 1.15 over s2_dur
    # zoompan z expression: start at zoom that shows WxH in the s2_w x s2_h image
    # We want to go from showing the full padded image (zoom=1.0) to cropped (zoom=1.15)
    zp_frames = int(s2_dur * FPS)
    # The input is s2_w x s2_h. We want output W x H.
    # zoom=1 means show WxH area; zoom=1.15 means show W/1.15 x H/1.15 area
    # zoompan uses zoom relative to output size vs input size
    # z = s2_w/W at start (showing full width), increasing to s2_w/W * 1.15

    base_z = s2_w / W  # ≈ 1.20
    end_z = base_z * 1.15 / 1.20  # back to ~1.0 to simulate zoom in from content

    # Actually simpler: start z=1.0 (crops to WxH from center of s2_w x s2_h),
    # end z = s2_w/W (shows "more" = zoom out effect). But we want zoom IN.
    # For zoom IN on zoompan: z starts lower and increases.
    # z='min(zoom+0.0015,1.5)' is a common pattern
    # Let's use: z = 1.0 + 0.15*(on/total) to go from 1.0x to 1.15x zoom
    z_expr = f"1+0.15*(on/{zp_frames})"

    # Build filter graph
    # Input 0: scene1 PNG (looped for s1_dur)
    # Input 1: scene2 source image (zoompan)
    # Input 2: scene3 PNG (looped for s3_dur)

    # The overlay bar on scene2 is tricky in pure ffmpeg. Let's add it as a
    # drawtext overlay instead.
    bar_font = FONT_SEMIBOLD.replace("'", "\\'")

    filter_parts = []

    # Scene 1: fade in from black over 0.5s, hold for s1_dur
    filter_parts.append(
        f"[0:v]loop=loop={int(s1_dur*FPS)-1}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,fps={FPS},"
        f"fade=t=in:st=0:d=0.5[s1v]"
    )

    # Scene 2: zoompan + bottom bar overlay
    filter_parts.append(
        f"[1:v]zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={zp_frames}:s={W}x{H}:fps={FPS},"
        f"setpts=PTS-STARTPTS,"
        # Dark bar at bottom
        f"drawbox=x=0:y=ih-70:w=iw:h=70:color=black@0.55:t=fill,"
        # Text on bar
        f"drawtext=text='thevideshi.com':fontfile='{bar_font}'"
        f":fontsize=26:fontcolor=white:x=(w-text_w)/2:y=h-70+(70-text_h)/2"
        f"[s2v]"
    )

    # Scene 3: hold for s3_dur
    filter_parts.append(
        f"[2:v]loop=loop={int(s3_dur*FPS)-1}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,fps={FPS}[s3v]"
    )

    # Crossfade 1→2
    off1 = s1_dur - xf
    filter_parts.append(
        f"[s1v][s2v]xfade=transition=fade:duration={xf}:offset={off1}[v12]"
    )

    # Crossfade (1+2)→3
    off2 = s1_dur + s2_dur - 2*xf
    filter_parts.append(
        f"[v12][s3v]xfade=transition=fade:duration={xf}:offset={off2}[vout]"
    )

    filter_complex = ";".join(filter_parts)

    total_dur = s1_dur + s2_dur + s3_dur - 2*xf

    cmd = [
        "ffmpeg", "-y",
        "-i", s1_png,           # input 0: scene1 image
        "-i", s2_src,           # input 1: scene2 source image
        "-i", s3_png,           # input 2: scene3 image
        "-f", "lavfi", "-i",    # input 3: silent audio
        f"anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_dur}",
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "3:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-preset", "medium", "-crf", "22",
        "-r", str(FPS),
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(total_dur),
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️  FFmpeg error: {result.stderr[-500:]}")
        # Fallback: simple concat without crossfade
        print("  Falling back to simple concat...")
        _fallback_concat(tmp_dir, s1_png, s2_src, s2_w, s2_h, s3_png, output_path)

    return output_path


def _fallback_concat(tmp_dir, s1_png, s2_src, s2_w, s2_h, s3_png, output_path):
    """Simpler assembly without xfade."""
    zp_frames = int(SCENE2_DUR * FPS)
    z_expr = f"1+0.15*(on/{zp_frames})"
    bar_font = FONT_SEMIBOLD.replace("'", "\\'")
    total = SCENE1_DUR + SCENE2_DUR + SCENE3_DUR

    # Make individual scene videos first
    s1v = os.path.join(tmp_dir, "s1.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", s1_png,
        "-t", str(SCENE1_DUR), "-r", str(FPS),
        "-vf", f"fade=t=in:st=0:d=0.5,scale={W}:{H},format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        s1v
    ], capture_output=True)

    s2v = os.path.join(tmp_dir, "s2.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", s2_src,
        "-vf", (
            f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={zp_frames}:s={W}x{H}:fps={FPS},"
            f"drawbox=x=0:y=ih-70:w=iw:h=70:color=black@0.55:t=fill,"
            f"drawtext=text='thevideshi.com':fontfile='{bar_font}'"
            f":fontsize=26:fontcolor=white:x=(w-text_w)/2:y=h-70+(70-text_h)/2,"
            f"format=yuv420p"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        s2v
    ], capture_output=True)

    s3v = os.path.join(tmp_dir, "s3.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", s3_png,
        "-t", str(SCENE3_DUR), "-r", str(FPS),
        "-vf", f"scale={W}:{H},format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        s3v
    ], capture_output=True)

    concat_file = os.path.join(tmp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        f.write(f"file '{s1v}'\nfile '{s2v}'\nfile '{s3v}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file,
        "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100:duration={total}",
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

    print("🎬 The Videshi Reel Generator v2")
    print("=" * 50)

    article = fetch_article(args.slug)
    slug = article["slug"]
    print(f"📰 {article['headline']}")
    print(f"📁 {article.get('category', 'news')}")
    print(f"🔗 {slug}")

    if args.dry_run:
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
        download_image(article["image_url"], img_path)
        print(f"  ✓ {os.path.getsize(img_path)} bytes")

        print("🎨 Scene 1 (headline card)...")
        t0 = time.time()
        s1 = render_scene1(article, tmp_dir)
        print(f"  ✓ {time.time()-t0:.1f}s")

        print("🖼️  Scene 2 (article image)...")
        t0 = time.time()
        s2, s2w, s2h = render_scene2_image(article, tmp_dir, img_path)
        print(f"  ✓ prepared {s2w}x{s2h} ({time.time()-t0:.1f}s)")

        print("✨ Scene 3 (CTA card)...")
        t0 = time.time()
        s3 = render_scene3(tmp_dir)
        print(f"  ✓ {time.time()-t0:.1f}s")

        print("🔗 Assembling reel...")
        t0 = time.time()
        assemble_reel(tmp_dir, s1, s2, s2w, s2h, s3, out)
        print(f"  ✓ {time.time()-t0:.1f}s")

        # Verify
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", out],
            capture_output=True, text=True)
        info = json.loads(probe.stdout)
        dur = float(info["format"]["duration"])
        sz = os.path.getsize(out) / (1024*1024)

        print(f"\n✅ Reel generated!")
        print(f"  📁 {out}")
        print(f"  ⏱️  {dur:.1f}s")
        print(f"  📐 1080x1920")
        print(f"  💾 {sz:.1f}MB")

        if args.upload:
            print("\n☁️  Uploading...")
            url = upload_to_supabase(out, slug[:80])
            if url:
                print(f"  ✅ {url}")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
