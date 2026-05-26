#!/usr/bin/env python3
"""
The Videshi — Instagram Reel Generator (v3)
2-scene reel: Article Image + Headline Chyron → CTA Card
Output: 1080x1920, ~15 seconds, H.264+AAC MP4
"""
import argparse
import json
import os
import random
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

IMAGE_DUR = 11.0   # Scene 1: article image + headline chyron
CTA_DUR   = 4.0    # Scene 2: CTA card
XFADE_DUR = 0.5

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

def render_image_scene(article, tmp_dir, img_path):
    """Article image with headline chyron overlay for Ken Burns zoom.
    Crops to (W*1.20) x (H*1.20) with gradient + category badge + headline + branding
    composited via PIL. This is the hero scene of the reel."""

    headline = article["headline"]
    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.open(img_path).convert("RGB")
    # Scale to cover 1080x1920 with 20% margin for zoom
    tw, th = int(W * 1.20), int(H * 1.20)
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    # Center crop to tw x th
    nw, nh = img.size
    x0 = (nw - tw) // 2
    y0 = (nh - th) // 2
    img = img.crop((x0, y0, x0 + tw, y0 + th))

    # ── Dark gradient overlay on bottom 50% ──
    gradient = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    grad_draw = ImageDraw.Draw(gradient)
    grad_start = int(th * 0.45)
    for y in range(grad_start, th):
        progress = (y - grad_start) / (th - grad_start)
        alpha = int(210 * (progress ** 1.3))
        grad_draw.rectangle([0, y, tw, y + 1], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, gradient)

    draw = ImageDraw.Draw(img)

    # Overlay positions relative to the zoompan-visible centre area.
    ox = (tw - W) // 2
    oy = (th - H) // 2
    pad = 70

    # ── Category badge ──
    bf = ImageFont.truetype(FONT_BOLD, 24)
    bb = draw.textbbox((0, 0), cat_label, font=bf)
    bw_txt, bh_txt = bb[2] - bb[0], bb[3] - bb[1]
    bw, bh = bw_txt + 36, bh_txt + 18
    badge_x = ox + pad
    badge_y = oy + int(H * 0.58)
    rounded_rect(draw, (badge_x, badge_y, badge_x + bw, badge_y + bh), 14, cat_color)
    draw.text((badge_x + (bw - bw_txt) // 2, badge_y + (bh - bh_txt) // 2 - 1),
              cat_label, font=bf, fill=WHITE)

    # ── Headline text ──
    max_w = W - 2 * pad
    zone_top = badge_y + bh + 20
    zone_bot = oy + H - 90
    max_h = zone_bot - zone_top - 50

    font, lines, lh = fit_text(draw, headline, max_w, max_h, FONT_EXTRABOLD,
                               sizes=(52, 48, 44, 40, 36, 32, 28))
    y_cursor = zone_top
    for line in lines:
        draw.text((ox + pad + 2, y_cursor + 2), line, font=font, fill=(0, 0, 0))
        draw.text((ox + pad, y_cursor), line, font=font, fill=WHITE)
        y_cursor += lh

    # ── Gold accent line ──
    line_y = y_cursor + 14
    draw.rectangle([ox + pad, line_y, ox + pad + 80, line_y + 3], fill=GOLD)

    # ── Bottom branding ──
    site_f = ImageFont.truetype(FONT_SEMIBOLD, 22)
    site_txt = "thevideshi.com"
    sb = draw.textbbox((0, 0), site_txt, font=site_f)
    site_w = sb[2] - sb[0]
    site_y = oy + H - 55
    draw.text((ox + (W - site_w) // 2, site_y), site_txt, font=site_f, fill=WHITE_DIM)

    img = img.convert("RGB")
    out = os.path.join(tmp_dir, "image_scene.png")
    img.save(out, quality=95)
    return out, tw, th


def render_cta_card(article, tmp_dir):
    """CTA card — vertically centred with category context."""
    cat = (article.get("category") or "news").lower().replace(" ", "-")
    cat_color = CATEGORY_COLORS.get(cat, CATEGORY_COLORS["news"])
    cat_label = cat.upper().replace("-", " ")

    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # ── Subtle decorative dots pattern ──
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    # Vertically centre content block.
    block_h = 420
    base_y = (H - block_h) // 2

    # ── Category badge ──
    bf_cat = ImageFont.truetype(FONT_BOLD, 22)
    cb = draw.textbbox((0, 0), cat_label, font=bf_cat)
    cw, ch = cb[2] - cb[0] + 34, cb[3] - cb[1] + 16
    cx = (W - cw) // 2
    cy = base_y
    rounded_rect(draw, (cx, cy, cx + cw, cy + ch), 12, cat_color)
    draw.text((cx + (cw - (cb[2] - cb[0])) // 2, cy + (ch - (cb[3] - cb[1])) // 2 - 1),
              cat_label, font=bf_cat, fill=WHITE)

    # ── Gold decorative line ──
    draw.rectangle([W // 2 - 80, cy + ch + 30, W // 2 + 80, cy + ch + 33], fill=GOLD)

    # ── Brand ──
    bf = ImageFont.truetype(FONT_EXTRABOLD, 72)
    txt = "THE VIDESHI"
    bb = draw.textbbox((0, 0), txt, font=bf)
    brand_y = cy + ch + 55
    draw.text(((W - (bb[2] - bb[0])) // 2, brand_y), txt, font=bf, fill=GOLD)

    # ── Tagline ──
    tf = ImageFont.truetype(FONT_REGULAR, 28)
    tag = "Your daily source for Indian diaspora news"
    bb2 = draw.textbbox((0, 0), tag, font=tf)
    tag_y = brand_y + (bb[3] - bb[1]) + 24
    draw.text(((W - (bb2[2] - bb2[0])) // 2, tag_y), tag, font=tf, fill=WHITE_DIM)

    # ── Divider ──
    div_y = tag_y + (bb2[3] - bb2[1]) + 30
    draw.rectangle([W // 2 - 50, div_y, W // 2 + 50, div_y + 3], fill=GOLD)

    # ── CTA ──
    cf = ImageFont.truetype(FONT_SEMIBOLD, 38)
    cta = "Read the full story"
    bb3 = draw.textbbox((0, 0), cta, font=cf)
    cta_y = div_y + 30
    draw.text(((W - (bb3[2] - bb3[0])) // 2, cta_y), cta, font=cf, fill=WHITE)

    # ── Link in bio with arrow ──
    lf = ImageFont.truetype(FONT_BOLD, 34)
    link = "Link in bio"
    bb4 = draw.textbbox((0, 0), link, font=lf)
    lx = (W - (bb4[2] - bb4[0])) // 2
    arrow_y = cta_y + (bb3[3] - bb3[1]) + 24
    af = ImageFont.truetype(FONT_BOLD, 40)
    ab = draw.textbbox((0, 0), "↑", font=af)
    draw.text(((W - (ab[2] - ab[0])) // 2, arrow_y), "↑", font=af, fill=GOLD)
    draw.text((lx, arrow_y + (ab[3] - ab[1]) + 6), link, font=lf, fill=GOLD)

    out = os.path.join(tmp_dir, "cta.png")
    img.save(out, quality=95)
    return out


def _pick_music_track():
    """Pick a random background music track from the music pool."""
    music_dir = os.path.join(SCRIPT_DIR, "music")
    if not os.path.isdir(music_dir):
        return None
    tracks = [os.path.join(music_dir, f) for f in os.listdir(music_dir)
              if f.endswith("-15s.mp3")]
    if tracks:
        return random.choice(tracks)
    return None


def assemble_reel(tmp_dir, img_src, img_w, img_h, cta_png, output_path):
    """Assemble 2 scenes with ffmpeg: image zoom + crossfade to CTA + music."""

    img_dur = IMAGE_DUR
    cta_dur = CTA_DUR
    xf = XFADE_DUR

    # Zoompan: slow zoom from 1.0x → 1.12x over img_dur
    zp_frames = int(img_dur * FPS)
    z_expr = f"1+0.12*(on/{zp_frames})"

    filter_parts = []

    # Scene 1 (image): zoompan + fade-in from black over 0.5s
    filter_parts.append(
        f"[0:v]zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={zp_frames}:s={W}x{H}:fps={FPS},"
        f"setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d=0.5"
        f"[imgv]"
    )

    # Scene 2 (CTA): static card
    filter_parts.append(
        f"[1:v]loop=loop={int(cta_dur*FPS)-1}:size=1:start=0,"
        f"setpts=PTS-STARTPTS,fps={FPS}[ctav]"
    )

    # Crossfade image → CTA
    xf_offset = img_dur - xf
    filter_parts.append(
        f"[imgv][ctav]xfade=transition=fade:duration={xf}:offset={xf_offset}[vout]"
    )

    filter_complex = ";".join(filter_parts)
    total_dur = img_dur + cta_dur - xf

    # Pick background music or silent audio
    music_track = _pick_music_track()
    if music_track:
        print(f"  🎵 Music: {os.path.basename(music_track)}")
        audio_inputs = ["-i", music_track]
        audio_map = ["-map", "2:a"]
        audio_filter = ["-af", f"atrim=0:{total_dur},afade=out:st={total_dur-1.5}:d=1.5"]
    else:
        print("  🔇 No music tracks found, using silent audio")
        audio_inputs = ["-f", "lavfi", "-i",
                        f"anullsrc=channel_layout=stereo:sample_rate=44100:duration={total_dur}"]
        audio_map = ["-map", "2:a"]
        audio_filter = []

    cmd = [
        "ffmpeg", "-y",
        "-i", img_src,          # input 0: image with chyron overlay
        "-i", cta_png,          # input 1: CTA card
        *audio_inputs,          # input 2: music or silent audio
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        *audio_map,
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
        print(f"  ⚠️  FFmpeg error: {result.stderr[-500:]}")
        print("  Falling back to simple concat...")
        _fallback_concat(tmp_dir, img_src, img_w, img_h, cta_png, output_path)

    return output_path


def _fallback_concat(tmp_dir, img_src, img_w, img_h, cta_png, output_path):
    """Simpler assembly without xfade (2 scenes)."""
    zp_frames = int(IMAGE_DUR * FPS)
    z_expr = f"1+0.12*(on/{zp_frames})"
    total = IMAGE_DUR + CTA_DUR

    imgv = os.path.join(tmp_dir, "img.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", img_src,
        "-vf", (
            f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={zp_frames}:s={W}x{H}:fps={FPS},"
            f"fade=t=in:st=0:d=0.5,format=yuv420p"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        imgv
    ], capture_output=True)

    ctav = os.path.join(tmp_dir, "cta.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", cta_png,
        "-t", str(CTA_DUR), "-r", str(FPS),
        "-vf", f"scale={W}:{H},format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        ctav
    ], capture_output=True)

    concat_file = os.path.join(tmp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        f.write(f"file '{imgv}'\nfile '{ctav}'\n")

    # Pick music for fallback too
    music_track = _pick_music_track()
    if music_track:
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", concat_file,
            "-i", music_track,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-af", f"atrim=0:{total},afade=out:st={total-1.5}:d=1.5",
            "-shortest",
            output_path
        ], capture_output=True)
    else:
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

    print("🎬 The Videshi Reel Generator v3")
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

        print("🖼️  Article image + headline chyron...")
        t0 = time.time()
        img_scene, iw, ih = render_image_scene(article, tmp_dir, img_path)
        print(f"  ✓ prepared {iw}x{ih} ({time.time()-t0:.1f}s)")

        print("✨ CTA card...")
        t0 = time.time()
        cta = render_cta_card(article, tmp_dir)
        print(f"  ✓ {time.time()-t0:.1f}s")

        print("🔗 Assembling reel...")
        t0 = time.time()
        assemble_reel(tmp_dir, img_scene, iw, ih, cta, out)
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
        print(f"  📐 {W}x{H}")
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
