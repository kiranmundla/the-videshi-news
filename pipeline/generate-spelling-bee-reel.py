#!/usr/bin/env python3
"""
Custom 5-scene celebration reel for the Spelling Bee editorial.
Scenes:
  1. Hook: 🏆 SHREY PARIKH WINS THE SCRIPPS SPELLING BEE
  2. Image + headline chyron  
  3. Dynasty stats
  4. Dramatic: Bromocriptine. B-R-O-M-O-C-R-I-P-T-I-N-E.
  5. Standard CTA: THE VIDESHI / thevideshi.com
"""
import os, sys, json, shutil, subprocess, tempfile, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Config ──
W, H = 1080, 1920
FPS = 25
XFADE_DUR = 0.5

NAVY = (26, 26, 46)
GOLD = (212, 168, 67)
WHITE = (255, 255, 255)
WHITE_DIM = (200, 200, 210)
SHADOW = (0, 0, 0)

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "reels"
OUTPUT_DIR.mkdir(exist_ok=True)

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

def rounded_rect(draw, xy, r, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy, sa, ea in [
        (x0+r, y0+r, 180, 270), (x1-r, y0+r, 270, 360),
        (x0+r, y1-r, 90, 180),  (x1-r, y1-r, 0, 90)]:
        draw.pieslice([cx-r, cy-r, cx+r, cy+r], sa, ea, fill=fill)

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

# ── Scene 1: Hook ──
def render_scene1_hook(tmp_dir):
    """🏆 SHREY PARIKH WINS THE SCRIPPS SPELLING BEE"""
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle dot pattern
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    pad = 80

    # Trophy emoji / "BREAKING" badge
    badge_f = ImageFont.truetype(FONT_BOLD, 26)
    badge_txt = "🏆 BREAKING"
    bb = draw.textbbox((0, 0), badge_txt, font=badge_f)
    bw, bh = bb[2]-bb[0]+36, bb[3]-bb[1]+18
    badge_x = (W - bw) // 2
    badge_y = H // 2 - 280
    rounded_rect(draw, (badge_x, badge_y, badge_x+bw, badge_y+bh), 10, (220, 53, 53))
    draw.text((badge_x + 18, badge_y + 6), badge_txt, font=badge_f, fill=WHITE)

    # Gold line
    line_y = badge_y + bh + 40
    draw.rectangle([W//2-80, line_y, W//2+80, line_y+5], fill=GOLD)

    # Main text
    main_txt = "SHREY PARIKH WINS THE SCRIPPS SPELLING BEE"
    font, lines, lh = fit_text(draw, main_txt, W - pad*2, 400, FONT_EXTRABOLD,
                                sizes=(72, 66, 60, 56, 52, 48, 44))
    
    text_y = line_y + 5 + 50
    for line in lines:
        lb = draw.textbbox((0, 0), line, font=font)
        lw = lb[2] - lb[0]
        x = (W - lw) // 2
        # Shadow
        draw.text((x+3, text_y+3), line, font=font, fill=SHADOW)
        draw.text((x, text_y), line, font=font, fill=GOLD)
        text_y += lh

    # Subtitle
    sub_f = ImageFont.truetype(FONT_REGULAR, 34)
    sub_txt = "2026 Scripps National Spelling Bee Champion"
    sb = draw.textbbox((0, 0), sub_txt, font=sub_f)
    sw = sb[2] - sb[0]
    draw.text(((W-sw)//2, text_y + 30), sub_txt, font=sub_f, fill=WHITE_DIM)

    # Branding at bottom
    brand_f = ImageFont.truetype(FONT_BOLD, 28)
    brand_txt = "THE VIDESHI"
    brb = draw.textbbox((0, 0), brand_txt, font=brand_f)
    brw = brb[2] - brb[0]
    draw.text(((W-brw)//2, H - 120), brand_txt, font=brand_f, fill=GOLD)

    out = os.path.join(tmp_dir, "scene1.png")
    img.save(out, quality=95)
    return out

# ── Scene 2: Image + headline chyron ──
def render_scene2_image(tmp_dir, img_path):
    """Hero image with headline chyron overlay."""
    # Load and scale image to cover
    src = Image.open(img_path).convert("RGB")
    iw, ih = src.size
    # Create zoompan source (slightly larger)
    scale = max(W / iw, H / ih) * 1.2
    src = src.resize((int(iw * scale), int(ih * scale)), Image.LANCZOS)
    nw, nh = src.size
    x0, y0 = (nw - W) // 2, (nh - H) // 2
    
    # For zoompan, save the full oversized image
    zp_w, zp_h = nw, nh
    
    # Create display version (cropped)
    display = src.crop((x0, y0, x0 + W, y0 + H))
    draw = ImageDraw.Draw(display)
    
    # Dark gradient at bottom for chyron
    for y in range(H - 500, H):
        alpha = int(220 * (y - (H - 500)) / 500)
        draw.rectangle([0, y, W, y+1], fill=(0, 0, 0, alpha) if alpha > 0 else (0,0,0))
    # Solid block to ensure readability
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(H - 450, H):
        a = min(220, int(240 * (y - (H - 450)) / 450))
        od.rectangle([0, y, W, y+1], fill=(0, 0, 0, a))
    display = Image.alpha_composite(display.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(display)
    
    # Chyron text
    hl_txt = "32 words in 90 seconds.\nA new spell-off record."
    font_big = ImageFont.truetype(FONT_EXTRABOLD, 56)
    
    lines = hl_txt.split("\n")
    text_y = H - 300
    for line in lines:
        lb = draw.textbbox((0, 0), line, font=font_big)
        lw = lb[2] - lb[0]
        lh = lb[3] - lb[1]
        x = (W - lw) // 2
        draw.text((x+2, text_y+2), line, font=font_big, fill=SHADOW)
        draw.text((x, text_y), line, font=font_big, fill=WHITE)
        text_y += lh + 20
    
    # Winning word
    word_f = ImageFont.truetype(FONT_SEMIBOLD, 36)
    word_txt = 'Winning word: "bromocriptine"'
    wb = draw.textbbox((0, 0), word_txt, font=word_f)
    ww = wb[2] - wb[0]
    draw.text(((W-ww)//2, text_y + 15), word_txt, font=word_f, fill=GOLD)
    
    # Save the zoompan source (full size with chyron)
    # Re-draw on the full-size image
    full = src.copy()
    full_draw = ImageDraw.Draw(full)
    # We need to apply chyron to full image too
    # For simplicity, save the cropped display as static
    out = os.path.join(tmp_dir, "scene2.png")
    display.save(out, quality=95)
    return out

# ── Scene 3: Dynasty Stats ──
def render_scene3_stats(tmp_dir):
    """Indian Americans have won 28 of the last 34 Spelling Bees"""
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Dot pattern
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    pad = 80

    # Section label
    label_f = ImageFont.truetype(FONT_BOLD, 24)
    label_txt = "THE DYNASTY"
    lb = draw.textbbox((0, 0), label_txt, font=label_f)
    lw, lh_label = lb[2]-lb[0]+30, lb[3]-lb[1]+14
    lx = (W - lw) // 2
    ly = H // 2 - 350
    rounded_rect(draw, (lx, ly, lx+lw, ly+lh_label), 8, GOLD)
    draw.text((lx + 15, ly + 4), label_txt, font=label_f, fill=NAVY)

    # Gold line
    gl_y = ly + lh_label + 35
    draw.rectangle([W//2-60, gl_y, W//2+60, gl_y+4], fill=GOLD)

    # Big stat: 28 of 34
    stat_big_f = ImageFont.truetype(FONT_EXTRABOLD, 120)
    stat_txt = "28 / 34"
    sb = draw.textbbox((0, 0), stat_txt, font=stat_big_f)
    sw = sb[2] - sb[0]
    stat_y = gl_y + 4 + 50
    # Glow
    for ox, oy in [(-2,-2),(2,-2),(-2,2),(2,2)]:
        draw.text(((W-sw)//2+ox, stat_y+oy), stat_txt, font=stat_big_f, fill=(180,140,40))
    draw.text(((W-sw)//2, stat_y), stat_txt, font=stat_big_f, fill=GOLD)

    # Explanation
    exp_f = ImageFont.truetype(FONT_SEMIBOLD, 38)
    exp_txt = "Indian Americans have won"
    exp2_txt = "28 of the last 34 Spelling Bees"
    for txt, yoff in [(exp_txt, 180), (exp2_txt, 230)]:
        eb = draw.textbbox((0, 0), txt, font=exp_f)
        ew = eb[2] - eb[0]
        draw.text(((W-ew)//2, stat_y+yoff), txt, font=exp_f, fill=WHITE)

    # Timeline markers
    timeline_y = stat_y + 310
    t_f = ImageFont.truetype(FONT_BOLD, 28)
    
    # First and latest
    draw.rectangle([pad, timeline_y, W-pad, timeline_y+3], fill=GOLD)
    
    first_txt = "1985"
    first_name = "Balu Natarajan"
    last_txt = "2026"
    last_name = "Shrey Parikh"
    
    name_f = ImageFont.truetype(FONT_REGULAR, 26)
    
    draw.text((pad, timeline_y + 15), first_txt, font=t_f, fill=GOLD)
    draw.text((pad, timeline_y + 50), first_name, font=name_f, fill=WHITE_DIM)
    
    lb = draw.textbbox((0, 0), last_txt, font=t_f)
    lw_t = lb[2] - lb[0]
    draw.text((W-pad-lw_t, timeline_y + 15), last_txt, font=t_f, fill=GOLD)
    nb = draw.textbbox((0, 0), last_name, font=name_f)
    nw = nb[2] - nb[0]
    draw.text((W-pad-nw, timeline_y + 50), last_name, font=name_f, fill=WHITE_DIM)

    # Sub-stat
    sub_f = ImageFont.truetype(FONT_REGULAR, 32)
    sub_txt = "31 champions · 22 winning years"
    sub_b = draw.textbbox((0, 0), sub_txt, font=sub_f)
    sub_w = sub_b[2] - sub_b[0]
    draw.text(((W-sub_w)//2, timeline_y + 120), sub_txt, font=sub_f, fill=WHITE_DIM)

    # Branding at bottom
    brand_f = ImageFont.truetype(FONT_BOLD, 28)
    brand_txt = "THE VIDESHI"
    brb = draw.textbbox((0, 0), brand_txt, font=brand_f)
    brw = brb[2] - brb[0]
    draw.text(((W-brw)//2, H - 120), brand_txt, font=brand_f, fill=GOLD)

    out = os.path.join(tmp_dir, "scene3.png")
    img.save(out, quality=95)
    return out

# ── Scene 4: Bromocriptine ──
def render_scene4_bromocriptine(tmp_dir):
    """Dramatic: Bromocriptine. B-R-O-M-O-C-R-I-P-T-I-N-E."""
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle dot pattern
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    # Vertical center point
    cy = H // 2

    # ── The word: "Bromocriptine." ──
    word_f = ImageFont.truetype(FONT_EXTRABOLD, 90)
    word_txt = "Bromocriptine."
    wb = draw.textbbox((0, 0), word_txt, font=word_f)
    ww = wb[2] - wb[0]
    wh = wb[3] - wb[1]
    word_y = cy - 180

    # Glow effect for the word
    glow = (180, 140, 40)
    for ox, oy in [(-3,-3),(3,-3),(-3,3),(3,3),(0,4),(4,0),(-4,0),(0,-4)]:
        draw.text(((W-ww)//2+ox, word_y+oy), word_txt, font=word_f, fill=glow)
    draw.text(((W-ww)//2, word_y), word_txt, font=word_f, fill=GOLD)

    # ── Gold accent line ──
    line_y = word_y + wh + 35
    draw.rectangle([W//2 - 100, line_y, W//2 + 100, line_y + 4], fill=GOLD)

    # ── Spelled out: B-R-O-M-O-C-R-I-P-T-I-N-E ──
    spell_f = ImageFont.truetype(FONT_BOLD, 52)
    spell_txt = "B-R-O-M-O-C-R-I-P-T-I-N-E"
    sb = draw.textbbox((0, 0), spell_txt, font=spell_f)
    sw = sb[2] - sb[0]
    spell_y = line_y + 4 + 45
    
    # If too wide, use smaller font
    if sw > W - 100:
        spell_f = ImageFont.truetype(FONT_BOLD, 42)
        sb = draw.textbbox((0, 0), spell_txt, font=spell_f)
        sw = sb[2] - sb[0]
    
    # Shadow + gold text
    draw.text(((W-sw)//2 + 3, spell_y + 3), spell_txt, font=spell_f, fill=SHADOW)
    draw.text(((W-sw)//2, spell_y), spell_txt, font=spell_f, fill=WHITE)

    # ── Closing line ──
    close_f = ImageFont.truetype(FONT_SEMIBOLD, 40)
    close_txt = "Spell that one out"
    close2_txt = "for the history books."

    close_y = spell_y + (sb[3]-sb[1]) + 60

    cb = draw.textbbox((0, 0), close_txt, font=close_f)
    cw = cb[2] - cb[0]
    draw.text(((W-cw)//2, close_y), close_txt, font=close_f, fill=WHITE_DIM)

    cb2 = draw.textbbox((0, 0), close2_txt, font=close_f)
    cw2 = cb2[2] - cb2[0]
    draw.text(((W-cw2)//2, close_y + (cb[3]-cb[1]) + 15), close2_txt, font=close_f, fill=WHITE_DIM)

    # Branding at bottom
    brand_f = ImageFont.truetype(FONT_BOLD, 28)
    brand_txt = "THE VIDESHI"
    brb = draw.textbbox((0, 0), brand_txt, font=brand_f)
    brw = brb[2] - brb[0]
    draw.text(((W-brw)//2, H - 120), brand_txt, font=brand_f, fill=GOLD)

    out = os.path.join(tmp_dir, "scene4_bromo.png")
    img.save(out, quality=95)
    return out

# ── Scene 5: CTA ──
def render_scene5_cta(tmp_dir):
    """Standard TheVideshi.com CTA frame."""
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Dot pattern
    dot_f = ImageFont.truetype(FONT_REGULAR, 14)
    for dy in range(0, H, 120):
        for dx in range(0, W, 120):
            draw.text((dx, dy), "·", font=dot_f, fill=(40, 40, 65))

    # Category badge
    bf_cat = ImageFont.truetype(FONT_BOLD, 26)
    cat_label = "NEWS"
    cb = draw.textbbox((0, 0), cat_label, font=bf_cat)
    bw, bh = cb[2]-cb[0]+36, cb[3]-cb[1]+18
    badge_x = (W - bw) // 2
    badge_y = H // 2 - 300
    rounded_rect(draw, (badge_x, badge_y, badge_x+bw, badge_y+bh), 10, (220, 53, 53))
    draw.text((badge_x + 18, badge_y + 6), cat_label, font=bf_cat, fill=WHITE)

    # Gold line 1
    l1y = badge_y + bh + 45
    draw.rectangle([W//2-80, l1y, W//2+80, l1y+5], fill=GOLD)

    # Brand
    brand_f = ImageFont.truetype(FONT_EXTRABOLD, 80)
    brand_txt = "THE VIDESHI"
    bb = draw.textbbox((0, 0), brand_txt, font=brand_f)
    bw_brand = bb[2] - bb[0]
    brand_y = l1y + 5 + 45
    draw.text(((W-bw_brand)//2, brand_y), brand_txt, font=brand_f, fill=GOLD)

    # URL — THE STAR
    url_f = ImageFont.truetype(FONT_EXTRABOLD, 90)
    url_txt = "TheVideshi.com"
    ub = draw.textbbox((0, 0), url_txt, font=url_f)
    uw = ub[2] - ub[0]
    url_y = brand_y + (bb[3]-bb[1]) + 30
    # Glow
    for ox, oy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,3),(3,0)]:
        draw.text(((W-uw)//2+ox, url_y+oy), url_txt, font=url_f, fill=(180,140,40))
    draw.text(((W-uw)//2, url_y), url_txt, font=url_f, fill=GOLD)

    # Tagline
    tag_f = ImageFont.truetype(FONT_REGULAR, 34)
    tag_txt = "Your daily source for Indian diaspora news"
    tb = draw.textbbox((0, 0), tag_txt, font=tag_f)
    tw = tb[2] - tb[0]
    tag_y = url_y + (ub[3]-ub[1]) + 40
    draw.text(((W-tw)//2, tag_y), tag_txt, font=tag_f, fill=WHITE_DIM)

    # Gold line 2
    l2y = tag_y + (tb[3]-tb[1]) + 45
    draw.rectangle([W//2-60, l2y, W//2+60, l2y+5], fill=GOLD)

    # Read more CTA
    cta_f = ImageFont.truetype(FONT_SEMIBOLD, 48)
    cta_txt = "Read the full editorial  ↗"
    ctb = draw.textbbox((0, 0), cta_txt, font=cta_f)
    ctw = ctb[2] - ctb[0]
    cta_y = l2y + 5 + 40
    draw.text(((W-ctw)//2, cta_y), cta_txt, font=cta_f, fill=WHITE)

    # Follow
    follow_f = ImageFont.truetype(FONT_REGULAR, 32)
    follow_txt = "Follow @the.videshi"
    fb = draw.textbbox((0, 0), follow_txt, font=follow_f)
    fw = fb[2] - fb[0]
    draw.text(((W-fw)//2, cta_y + (ctb[3]-ctb[1]) + 35), follow_txt, font=follow_f, fill=WHITE_DIM)

    # Social
    social_f = ImageFont.truetype(FONT_REGULAR, 26)
    social_txt = "X: @thevideshi  ·  YT: @the.videshi"
    sbb = draw.textbbox((0, 0), social_txt, font=social_f)
    ssw = sbb[2] - sbb[0]
    draw.text(((W-ssw)//2, cta_y + (ctb[3]-ctb[1]) + 35 + (fb[3]-fb[1]) + 20),
              social_txt, font=social_f, fill=WHITE_DIM)

    out = os.path.join(tmp_dir, "scene5_cta.png")
    img.save(out, quality=95)
    return out

# ── Assembly ──
def assemble_5scene_reel(tmp_dir, scenes, output_path):
    """Assemble 5 static scenes with xfade transitions + music."""
    n = len(scenes)
    xf = XFADE_DUR

    filter_parts = []
    input_args = []

    for i, sc in enumerate(scenes):
        input_args.extend(["-i", sc["path"]])
        nframes = int(sc["dur"] * FPS)
        filter_parts.append(
            f"[{i}:v]loop=loop={nframes - 1}:size=1:start=0,"
            f"setpts=PTS-STARTPTS,fps={FPS}[v{i}]"
        )

    # Chain xfade
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

    filter_complex = ";".join(filter_parts)
    total_dur = sum(s["dur"] for s in scenes) - xf * (n - 1)

    # Music
    music_dir = SCRIPT_DIR / "music"
    music_track = None
    if music_dir.exists():
        tracks = sorted(music_dir.glob("*.mp3"))
        # Prefer 30s track
        for t in tracks:
            if "30" in t.name:
                music_track = str(t)
                break
        if not music_track and tracks:
            music_track = str(tracks[0])

    audio_idx = n
    if music_track:
        probe_a = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", music_track], capture_output=True, text=True)
        track_dur = float(probe_a.stdout.strip()) if probe_a.stdout.strip() else 0
        print(f"  🎵 Music: {os.path.basename(music_track)} ({track_dur:.1f}s for {total_dur:.1f}s video)")
        if track_dur >= total_dur:
            audio_inputs = ["-i", music_track]
            audio_filter = ["-af", f"atrim=0:{total_dur},afade=out:st={total_dur-2}:d=2"]
        else:
            loops = int(total_dur / track_dur) + 1
            audio_inputs = ["-stream_loop", str(loops), "-i", music_track]
            audio_filter = ["-af", f"atrim=0:{total_dur},afade=out:st={total_dur-2}:d=2"]
    else:
        print("  🔇 No music — silent")
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
        print(f"  ⚠️  FFmpeg error: {result.stderr[-500:]}")
        return None
    return output_path

# ── Main ──
def main():
    print("🎬 Spelling Bee Celebration Reel — 5 Scenes")
    print("=" * 50)

    img_path = os.path.expanduser("~/workspace/the-videshi-news/public/images/shrey-parikh-winner.jpg")
    if not os.path.exists(img_path):
        sys.exit(f"❌ Hero image not found: {img_path}")

    tmp_dir = tempfile.mkdtemp(prefix="bee-reel-")
    slug = "shrey-parikh-scripps-spelling-bee-2026-indian-american-dynasty"
    out = str(OUTPUT_DIR / f"reel-{slug}.mp4")

    try:
        # Scene durations
        S1_DUR = 3.0   # Hook
        S2_DUR = 5.0   # Image + stat
        S3_DUR = 6.0   # Dynasty stats
        S4_DUR = 5.0   # Bromocriptine
        S5_DUR = 4.0   # CTA

        print("🏆 Scene 1 (hook)...")
        s1 = render_scene1_hook(tmp_dir)
        print("  ✓")

        print("🖼️  Scene 2 (image + record)...")
        s2 = render_scene2_image(tmp_dir, img_path)
        print("  ✓")

        print("📊 Scene 3 (dynasty stats)...")
        s3 = render_scene3_stats(tmp_dir)
        print("  ✓")

        print("✨ Scene 4 (bromocriptine)...")
        s4 = render_scene4_bromocriptine(tmp_dir)
        print("  ✓")

        print("📢 Scene 5 (CTA)...")
        s5 = render_scene5_cta(tmp_dir)
        print("  ✓")

        scenes = [
            {"type": "static", "path": s1, "dur": S1_DUR},
            {"type": "static", "path": s2, "dur": S2_DUR},
            {"type": "static", "path": s3, "dur": S3_DUR},
            {"type": "static", "path": s4, "dur": S4_DUR},
            {"type": "static", "path": s5, "dur": S5_DUR},
        ]

        total = sum(s["dur"] for s in scenes) - XFADE_DUR * 4
        print(f"\n🔗 Assembling 5-scene reel (~{total:.0f}s)...")
        result = assemble_5scene_reel(tmp_dir, scenes, out)

        if result:
            # Verify
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", out],
                capture_output=True, text=True)
            info = json.loads(probe.stdout)
            dur = float(info["format"]["duration"])
            sz = os.path.getsize(out) / (1024 * 1024)

            print(f"\n✅ Reel generated!")
            print(f"  📁 {out}")
            print(f"  ⏱️  {dur:.1f}s")
            print(f"  📐 {W}x{H}")
            print(f"  💾 {sz:.1f}MB")

            # Save cover
            cover = str(OUTPUT_DIR / f"reel-{slug}-cover.jpg")
            cover_img = Image.open(s2)
            cover_img.save(cover, quality=90)
            print(f"  📸 Cover: {cover}")
        else:
            print("❌ Assembly failed")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
