#!/usr/bin/env python3
"""
Portrait Fix for HeyGen Avatar Videos
======================================
Detects landscape-letterboxed content in portrait (9:16) frames and converts
them into a professional news reel layout:

  ┌──────────────────┐
  │  THE VIDESHI      │  ← branded header (gold logo, BREAKING badge, headline)
  │  BREAKING         │
  │  Headline text    │
  ├══════════════════╡  ← gold accent line
  │                  │
  │  [Avatar video]  │  ← cropped content (landscape band extracted)
  │                  │
  ├══════════════════╡  ← gold accent line
  │                  │
  │  [Caption zone]  │  ← navy zone for ASS-positioned captions
  │                  │
  ├──────────────────┤
  │ thevideshi.com   │  ← bottom branding bar
  └──────────────────┘

Usage:
  from portrait_fix import detect_letterbox, fix_avatar_portrait, create_positioned_captions

  info = detect_letterbox("avatar-raw.mp4")
  if info['is_letterboxed']:
      fix_avatar_portrait("avatar-raw.mp4", "avatar-fixed.mp4", headline, info)
      create_positioned_captions("captions.srt", "captions.ass")
"""

import subprocess, json, re, os
from pathlib import Path

PIPELINE_DIR = Path(__file__).parent


def detect_letterbox(video_path, threshold=0.55):
    """
    Detect if a portrait video has letterboxed landscape content.
    
    Returns dict with:
      - is_letterboxed: bool
      - content_top: int (row where content starts)
      - content_bottom: int (row where content ends)
      - content_height: int
      - frame_height: int
      - content_ratio: float (content_height / frame_height)
    """
    video_path = str(video_path)
    
    # Extract a frame
    tmp_frame = "/tmp/letterbox_detect.png"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "3", "-i", video_path,
         "-frames:v", "1", tmp_frame],
        capture_output=True, timeout=30
    )
    
    if not os.path.exists(tmp_frame):
        return {"is_letterboxed": False, "error": "Could not extract frame"}
    
    try:
        from PIL import Image
        import numpy as np
        
        img = Image.open(tmp_frame)
        arr = np.array(img)
        h, w = arr.shape[:2]
        
        row_brightness = arr.mean(axis=(1, 2))
        
        # Content rows: brightness between 5 and 240 (not near-white, not near-black)
        content_rows = np.where((row_brightness > 5) & (row_brightness < 240))[0]
        
        if len(content_rows) == 0:
            return {"is_letterboxed": False, "frame_height": h}
        
        top = int(content_rows[0])
        bottom = int(content_rows[-1])
        content_height = bottom - top + 1
        ratio = content_height / h
        
        result = {
            "is_letterboxed": ratio < threshold,
            "content_top": top,
            "content_bottom": bottom,
            "content_height": content_height,
            "frame_width": w,
            "frame_height": h,
            "content_ratio": ratio
        }
        
        if result["is_letterboxed"]:
            print(f"  📐 Letterbox detected: content is {ratio*100:.0f}% of frame "
                  f"(rows {top}-{bottom}, {content_height}px of {h}px)")
        
        return result
        
    except ImportError:
        # Fallback: just check video dimensions
        return {"is_letterboxed": False, "error": "PIL not available"}
    finally:
        if os.path.exists(tmp_frame):
            os.remove(tmp_frame)


def fix_avatar_portrait(video_path, output_path, headline, letterbox_info=None,
                        badge_text="BREAKING"):
    """
    Convert a letterboxed avatar video into a professional news reel layout.
    
    Args:
        video_path: Path to raw avatar video
        output_path: Path for output fixed video
        headline: Article headline (will be word-wrapped to 3 lines)
        letterbox_info: Output from detect_letterbox() (auto-detected if None)
        badge_text: Badge text (BREAKING, DEVELOPING, etc.)
    
    Returns:
        True if fix was applied, False otherwise
    """
    video_path = str(video_path)
    output_path = str(output_path)
    
    if letterbox_info is None:
        letterbox_info = detect_letterbox(video_path)
    
    if not letterbox_info.get("is_letterboxed"):
        print("  ℹ️ No letterbox detected, skipping portrait fix")
        return False
    
    ct = letterbox_info.get("content_top", 0)
    ch = letterbox_info.get("content_height", 1080)
    fw = letterbox_info.get("frame_width", 1080)
    fh = letterbox_info.get("frame_height", 1920)
    
    # Detect if input is native 16:9 (1920x1080) vs letterboxed portrait (1080x1920)
    is_native_landscape = fw == 1920 and fh == 1080
    
    # Word-wrap headline into max 3 lines
    headline_lines = _wrap_headline(headline, max_chars=28, max_lines=3)
    
    # Build ffmpeg filter: navy canvas + content + branding + captions zone
    drawtext_parts = []
    
    # Logo
    drawtext_parts.append(
        "drawtext=text='THE VIDESHI':"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "fontsize=32:fontcolor=#D4AF37:x=(w-text_w)/2:y=30"
    )
    
    # Badge
    if badge_text:
        drawtext_parts.append(
            f"drawtext=text='{badge_text}':"
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            "fontsize=20:fontcolor=#0D1B2A:x=(w-text_w)/2:y=80:"
            "box=1:boxcolor=#D4AF37:boxborderw=6"
        )
    
    # Headline lines
    y_start = 130
    for i, line in enumerate(headline_lines):
        escaped = line.replace("'", "'\\''").replace("$", "\\$").replace(":", "\\:")
        drawtext_parts.append(
            f"drawtext=text='{escaped}':"
            "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontsize=40:fontcolor=white:x=(w-text_w)/2:y={y_start + i * 55}"
        )
    
    # Bottom branding
    drawtext_parts.append(
        "drawtext=text='thevideshi.com':"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        "fontsize=22:fontcolor=#D4AF37:x=(w-text_w)/2:y=1870"
    )
    drawtext_parts.append(
        "drawtext=text='@thevideshi':"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
        "fontsize=18:fontcolor=#888888:x=(w-text_w)/2:y=1895"
    )
    
    drawtext_chain = ",\n    ".join(drawtext_parts)
    
    # Avatar content zone: starts at y=340, gold accent lines above and below
    avatar_y = 340
    # Target content height: scale to fill 1080px wide, maintain aspect ratio
    if is_native_landscape:
        # Input is 1920x1080 — scale to 1080 wide → height = 607
        scaled_h = 607
        filter_complex = f"""
    [1:v]scale=1080:{scaled_h}:flags=lanczos[content];
    [0:v]setpts=PTS-STARTPTS[canvas];
    [canvas][content]overlay=0:{avatar_y}:shortest=1[base];
    [base]
    drawbox=x=0:y={avatar_y - 5}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y={avatar_y + scaled_h + 2}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y=1840:w=1080:h=80:c=#0A1520:t=fill,
    {drawtext_chain}
    [out]
    """
    else:
        # Input is letterboxed portrait (1080x1920) — crop content band out
        filter_complex = f"""
    [1:v]crop=1080:{ch}:0:{ct}[content];
    [0:v]setpts=PTS-STARTPTS[canvas];
    [canvas][content]overlay=0:{avatar_y}:shortest=1[base];
    [base]
    drawbox=x=0:y={avatar_y - 5}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y={avatar_y + ch + 2}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y=1840:w=1080:h=80:c=#0A1520:t=fill,
    {drawtext_chain}
    [out]
    """
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0D1B2A:s=1080x1920:r=25",
        "-i", video_path,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "1:a",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-shortest",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    
    if result.returncode != 0:
        print(f"  ❌ Portrait fix failed: {result.stderr[-300:]}")
        return False
    
    print(f"  ✅ Portrait fix applied — news layout created")
    return True


def create_positioned_captions(srt_path, ass_path, margin_v=700, font_size=48):
    """
    Convert SRT to ASS with precise positioning for the caption zone.
    
    Captions will appear in the dark navy zone below the avatar content,
    above the bottom branding bar.
    
    Args:
        srt_path: Path to input SRT file
        ass_path: Path for output ASS file
        margin_v: Margin from bottom (px) — 700 puts captions in the navy zone
        font_size: Caption font size
    """
    with open(srt_path) as f:
        content = f.read()
    
    # ASS header
    ass_header = f"""[Script Info]
Title: Videshi Reel Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80142A0D,1,0,0,0,100,100,0,0,4,0,0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Parse SRT
    blocks = re.split(r'\n\n+', content.strip())
    events = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        time_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})',
            lines[1]
        )
        if not time_match:
            continue
        g = time_match.groups()
        start = f"{g[0]}:{g[1]}:{g[2]}.{g[3][:2]}"
        end = f"{g[4]}:{g[5]}:{g[6]}.{g[7][:2]}"
        text = ' '.join(lines[2:]).strip()
        if not text:
            continue
        events.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")
    
    with open(ass_path, 'w') as f:
        f.write(ass_header + '\n'.join(events) + '\n')
    
    print(f"  📝 Created positioned captions: {len(events)} events, MarginV={margin_v}")
    return len(events) > 0


def burn_captions_news_layout(video_path, srt_path, output_path):
    """
    Burn captions positioned for the news layout.
    Uses ASS format for precise positioning in the caption zone.
    """
    ass_path = str(srt_path).rsplit('.', 1)[0] + '_positioned.ass'
    
    if not create_positioned_captions(srt_path, ass_path):
        return False
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        str(output_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode != 0:
        print(f"  ⚠️ Caption burn failed: {result.stderr[-200:]}")
        return False
    
    return os.path.exists(output_path)


def _wrap_headline(headline, max_chars=28, max_lines=3):
    """Word-wrap headline into lines of max_chars, up to max_lines."""
    words = headline.split()
    lines = []
    current = ""
    
    for word in words:
        test = f"{current} {word}".strip() if current else word
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) >= max_lines - 1:
                # Last line gets remaining words
                remaining_words = words[words.index(word):]
                lines.append(' '.join(remaining_words))
                current = ""
                break
    
    if current:
        lines.append(current)
    
    return lines[:max_lines]


def normalize_audio_social(video_path, output_path, target_lufs=-14):
    """Normalize audio to social media loudness standard (-14 LUFS)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-af", f"loudnorm=I={target_lufs}:TP=-1:LRA=11",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ⚠️ Audio normalization failed: {result.stderr[-200:]}")
        return False
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fix letterboxed HeyGen avatar videos")
    parser.add_argument("video", help="Raw avatar video path")
    parser.add_argument("--headline", required=True, help="Article headline")
    parser.add_argument("--srt", help="SRT file for captions")
    parser.add_argument("--output", "-o", help="Output path")
    parser.add_argument("--badge", default="BREAKING", help="Badge text")
    args = parser.parse_args()
    
    output = args.output or args.video.replace(".mp4", "-fixed.mp4")
    
    info = detect_letterbox(args.video)
    print(json.dumps(info, indent=2))
    
    if info["is_letterboxed"]:
        fix_avatar_portrait(args.video, output, args.headline, info, args.badge)
        
        if args.srt:
            captioned = output.replace(".mp4", "-captioned.mp4")
            burn_captions_news_layout(output, args.srt, captioned)
            print(f"\n✅ Final output: {captioned}")
        else:
            print(f"\n✅ Fixed output: {output}")
    else:
        print("No letterbox detected.")
