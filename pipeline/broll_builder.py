#!/usr/bin/env python3
"""
B-Roll Builder for The Videshi Reel Pipeline

Handles:
1. Segmented script generation (ANCHOR vs BROLL segments)
2. Image sourcing for B-roll segments (article images, Pexels, web)
3. B-roll portrait frame rendering (branded layout with image instead of avatar)
4. Segment timeline mapping (SRT timestamps → segment boundaries)
5. Video assembly with crossfade transitions between anchor and B-roll
"""

import json
import os
import re
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from difflib import SequenceMatcher

import requests

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
BUILD_DIR = Path(__file__).parent / "reels" / "build"


# ─── 1. Segmented Script Generation ─────────────────────────────────────────

def generate_segmented_script(article):
    """
    Generate a structured script with ANCHOR and BROLL segments.
    
    Returns dict:
    {
        "full_script": "continuous spoken text for HeyGen",
        "segments": [
            {"type": "anchor", "text": "...", "word_count": N},
            {"type": "broll", "text": "...", "word_count": N, "image_query": "...", "image_description": "..."},
            ...
        ]
    }
    """
    headline = article.get('headline', '')
    body = (article.get('body') or '')[:3000]
    category = article.get('category', '')
    image_url = article.get('image_url', '')

    prompt = f"""You are a scriptwriter for The Videshi, an Indian diaspora news platform.
Write a 20-30 second news anchor script with B-ROLL visual cues.

The script will be read by a video anchor (Kavya). Some segments she appears on camera (ANCHOR),
and some segments her voice continues but we show a relevant image instead (BROLL).

Rules:
- Open with ANCHOR (the hook — she appears on camera)
- Alternate between ANCHOR and BROLL segments (2-4 segments total)
- BROLL segments should describe things that are VISUAL: people, places, events, data
- Each segment should be 15-30 words (natural breath groups)
- Total script: 60-90 words
- End with ANCHOR for the sign-off
- End with "Full story at thevideshi.com"
- NO greetings, NO "breaking news"
- Natural conversational tone
- NO emoji, NO hashtags

For each BROLL segment, provide:
- image_query: a specific search query to find that exact image (real person name, event, place)
- image_description: what the ideal image shows

Article headline: {headline}
Category: {category}
Article image: {image_url}
Article body:
{body}

Return ONLY valid JSON (no markdown fences):
{{
    "segments": [
        {{"type": "anchor", "text": "..."}},
        {{"type": "broll", "text": "...", "image_query": "...", "image_description": "..."}},
        {{"type": "anchor", "text": "..."}},
        ...
    ]
}}"""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500,
        },
        timeout=30,
    )
    if r.status_code != 200:
        print(f"  ❌ Segmented script generation failed: {r.status_code}")
        return None

    raw = r.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  ❌ Failed to parse segmented script JSON: {raw[:200]}")
        return None

    segments = data.get("segments", [])
    if not segments:
        print("  ❌ No segments in script")
        return None

    # Build the full continuous script (what HeyGen speaks)
    full_script = " ".join(seg["text"] for seg in segments)
    
    # Add word counts
    for seg in segments:
        seg["word_count"] = len(seg["text"].split())

    total_words = sum(s["word_count"] for s in segments)
    broll_count = sum(1 for s in segments if s["type"] == "broll")
    
    print(f"  📝 Segmented script: {total_words} words, {len(segments)} segments ({broll_count} B-roll)")
    for i, seg in enumerate(segments):
        marker = "🎬" if seg["type"] == "anchor" else "🖼️"
        print(f"    {marker} [{seg['type'].upper()}] ({seg['word_count']}w) {seg['text'][:60]}...")
        if seg["type"] == "broll":
            print(f"       → Image: {seg.get('image_query', 'N/A')}")

    return {"full_script": full_script, "segments": segments}


# ─── 2. Image Sourcing ──────────────────────────────────────────────────────

def source_broll_images(segments, article):
    """
    Find images for each BROLL segment from the article's own assets only.
    No external search — the article pipeline already sourced the best images.
    
    Sources (in order):
    1. Article image_url
    2. Images embedded in article body (markdown ![](url) or <img>)
    3. YouTube thumbnails from <youtube> tags in body
    
    If no images available, B-roll segments fall back to anchor (Kavya stays on screen).
    
    Returns list of image paths (same length as segments, None for ANCHOR segments).
    """
    # Collect all available images from the article
    available_images = []
    
    # 1. Article main image
    article_image = article.get("image_url", "")
    if article_image:
        available_images.append(("article_main", article_image))
    
    # 2. Images in article body
    body = article.get("body") or ""
    
    # Markdown images: ![alt](url)
    md_images = re.findall(r'!\[.*?\]\((https?://[^\s)]+)\)', body)
    for url in md_images:
        if url != article_image:  # Don't duplicate main image
            available_images.append(("body_image", url))
    
    # HTML images: <img src="url">
    html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', body)
    for url in html_images:
        if url not in [u for _, u in available_images]:
            available_images.append(("body_image", url))
    
    # 3. YouTube thumbnails
    yt_ids = re.findall(r'<youtube>.*?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+).*?</youtube>', body)
    if not yt_ids:
        yt_ids = re.findall(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', body)
    for yt_id in yt_ids:
        # maxresdefault is 1280x720 — perfect for our 16:9 content band
        available_images.append(("youtube_thumb", f"https://img.youtube.com/vi/{yt_id}/maxresdefault.jpg"))
    
    if not available_images:
        print("  ⚠️ No images found in article — B-roll segments will use anchor")
    else:
        print(f"  📸 Found {len(available_images)} images in article: {', '.join(src for src, _ in available_images)}")

    # Assign images to BROLL segments (round-robin if more B-roll than images)
    image_paths = []
    img_idx = 0
    broll_count = sum(1 for s in segments if s["type"] == "broll")

    for i, seg in enumerate(segments):
        if seg["type"] != "broll":
            image_paths.append(None)
            continue

        if not available_images:
            image_paths.append(None)
            continue

        source_type, url = available_images[img_idx % len(available_images)]
        img_path = BUILD_DIR / f"broll-img-{i}.jpg"

        if _download_image(url, img_path):
            print(f"  🖼️ B-roll {i}: {source_type} — {url[:80]}")
            image_paths.append(str(img_path))
            img_idx += 1
        else:
            print(f"  ⚠️ B-roll {i}: Failed to download {source_type}")
            image_paths.append(None)
            img_idx += 1

    return image_paths


def _download_image(url, output_path):
    """Download image from URL. Returns True on success."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", str(output_path), "--max-time", "10", url],
            capture_output=True, timeout=15
        )
        if result.returncode == 0 and Path(output_path).exists() and Path(output_path).stat().st_size > 1000:
            return True
    except Exception as e:
        print(f"    Download error: {e}")
    return False


# ─── 3. B-Roll Frame Rendering ──────────────────────────────────────────────

def render_broll_frame(image_path, headline, badge_text, output_path, duration, fps=25):
    """
    Create a portrait video frame (1080x1920) with the B-roll image
    in the branded news layout. Unlike the anchor frame where the avatar
    sits in a small 16:9 band, B-roll images fill most of the frame.
    
    Layout:
    - Navy header: THE VIDESHI logo + badge + headline (~300px)
    - Gold accent line
    - Image area (fills from y=300 to y=1500 = ~1200px tall, much larger than avatar band)
    - Gold accent line  
    - Caption zone (~340px for captions)
    - Bottom branding bar (80px)
    
    Returns path to silent video segment.
    """
    image_path = str(image_path)
    output_path = str(output_path)

    # Probe image dimensions
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", image_path],
        capture_output=True, text=True, timeout=10
    )
    if probe.returncode != 0:
        print(f"  ❌ Can't probe image: {image_path}")
        return None

    img_w, img_h = map(int, probe.stdout.strip().split("x"))

    # B-roll image gets a MUCH larger area than the avatar band
    # Header takes ~300px, caption zone ~340px, branding 80px = 720px overhead
    # Image area: 1920 - 720 = 1200px tall
    image_y = 300       # Start below header
    image_h = 1200      # Much taller than avatar's 607px
    target_w = 1080

    # Scale image to fill the area (cover mode: fill width and height, crop excess)
    scale_by_w = target_w / img_w
    scale_by_h = image_h / img_h
    scale = max(scale_by_w, scale_by_h)  # Cover: use larger scale to fill
    scaled_w = int(img_w * scale)
    scaled_h = int(img_h * scale)

    # Word-wrap headline
    headline_lines = _wrap_headline(headline, max_chars=28, max_lines=3)

    # Build drawtext parts (same branding as anchor)
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

    # Headline
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

    # Ken Burns: very gentle slow zoom for subtle motion (no shake)
    # Scale to cover the target area, then crop to exact size
    # Slow zoom from 100% to 103% — smooth and subtle, no jitter
    zoom_filter = f"zoompan=z='min(zoom+0.00008,1.03)':d={int(duration * fps)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={scaled_w}x{scaled_h}:fps={fps}"
    crop_filter = f"crop={target_w}:{image_h}:(in_w-{target_w})/2:(in_h-{image_h})/2"

    filter_complex = f"""
    [1:v]{zoom_filter},{crop_filter}[content];
    [0:v]setpts=PTS-STARTPTS[canvas];
    [canvas][content]overlay=0:{image_y}:shortest=1[base];
    [base]
    drawbox=x=0:y={image_y - 3}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y={image_y + image_h}:w=1080:h=3:c=#D4AF37:t=fill,
    drawbox=x=0:y=1840:w=1080:h=80:c=#0A1520:t=fill,
    {drawtext_chain}
    [out]
    """

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=#0D1B2A:s=1080x1920:r={fps}:d={duration}",
        "-i", image_path,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        print(f"  ❌ B-roll frame render failed: {result.stderr[-300:]}")
        return None

    print(f"  ✅ B-roll frame rendered: {duration:.1f}s")
    return output_path


# ─── 4. Segment Timeline Mapping ────────────────────────────────────────────

def parse_srt(srt_path):
    """Parse SRT file into list of {index, start, end, text}."""
    entries = []
    with open(srt_path) as f:
        content = f.read()

    blocks = re.split(r'\n\n+', content.strip())
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        try:
            idx = int(lines[0])
        except ValueError:
            continue
        time_match = re.match(r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})', lines[1])
        if not time_match:
            continue
        start = _srt_time_to_seconds(time_match.group(1))
        end = _srt_time_to_seconds(time_match.group(2))
        text = ' '.join(lines[2:]).strip()
        entries.append({"index": idx, "start": start, "end": end, "text": text})

    return entries


def _srt_time_to_seconds(ts):
    """Convert SRT timestamp (HH:MM:SS,mmm) to float seconds."""
    ts = ts.replace(',', '.')
    parts = ts.split(':')
    return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])


def map_segments_to_timeline(segments, srt_entries):
    """
    Map script segments to actual SRT timestamps using fuzzy text matching.
    
    Returns segments with added 'start_time' and 'end_time' fields.
    """
    if not srt_entries:
        print("  ⚠️ No SRT entries for timeline mapping, using word-count estimation")
        return _estimate_timeline(segments)

    # Build full SRT text with timestamps for each word
    srt_words = []
    for entry in srt_entries:
        words = entry["text"].split()
        duration = entry["end"] - entry["start"]
        for j, word in enumerate(words):
            # Distribute time evenly across words in each SRT entry
            t = entry["start"] + (j / max(len(words), 1)) * duration
            srt_words.append({"word": word.lower().strip('.,!?;:'), "time": t})

    # For each segment, find the best matching position in the SRT word stream
    seg_pointer = 0
    for seg in segments:
        seg_words = [w.lower().strip('.,!?;:') for w in seg["text"].split()]
        if not seg_words:
            continue

        # Find the first word of this segment in the SRT stream (from current pointer)
        best_start_idx = _find_best_match(srt_words, seg_words, seg_pointer)
        
        if best_start_idx is not None:
            seg["start_time"] = srt_words[best_start_idx]["time"]
            end_idx = min(best_start_idx + len(seg_words) - 1, len(srt_words) - 1)
            seg["end_time"] = srt_words[end_idx]["time"] + 0.3  # Small buffer
            seg_pointer = end_idx + 1
        else:
            # Fallback: estimate based on word count
            print(f"  ⚠️ Could not map segment: {seg['text'][:40]}...")

    # Fill in any missing timestamps using neighbors
    _fill_missing_timestamps(segments, srt_entries)

    # Ensure last segment extends to the actual end of audio
    # (prevents end card from cutting off Kavya mid-sentence)
    if segments and srt_entries:
        audio_end = srt_entries[-1]["end"] + 0.5  # 500ms buffer after last word
        segments[-1]["end_time"] = max(segments[-1].get("end_time", 0), audio_end)

    for seg in segments:
        dur = seg.get('end_time', 0) - seg.get('start_time', 0)
        print(f"    ⏱️ [{seg['type'].upper()}] {seg.get('start_time', 0):.1f}s → {seg.get('end_time', 0):.1f}s ({dur:.1f}s)")

    return segments


def _find_best_match(srt_words, seg_words, start_from):
    """Find the best starting position for seg_words in srt_words using fuzzy matching."""
    first_word = seg_words[0]
    best_score = 0
    best_idx = None

    # Search from start_from onwards, with some lookback tolerance
    search_start = max(0, start_from - 5)
    
    for i in range(search_start, len(srt_words)):
        if srt_words[i]["word"] == first_word or SequenceMatcher(None, srt_words[i]["word"], first_word).ratio() > 0.8:
            # Check how many subsequent words match
            match_count = 0
            for j in range(min(len(seg_words), len(srt_words) - i)):
                if j >= len(seg_words):
                    break
                ratio = SequenceMatcher(None, srt_words[i + j]["word"], seg_words[j]).ratio()
                if ratio > 0.7:
                    match_count += 1

            score = match_count / len(seg_words)
            if score > best_score:
                best_score = score
                best_idx = i

    if best_score > 0.3:  # At least 30% of words matched
        return best_idx
    return None


def _fill_missing_timestamps(segments, srt_entries):
    """Fill in any segments missing timestamps."""
    total_duration = srt_entries[-1]["end"] if srt_entries else 30.0
    total_words = sum(s.get("word_count", len(s["text"].split())) for s in segments)
    
    cumulative = 0
    for seg in segments:
        wc = seg.get("word_count", len(seg["text"].split()))
        if "start_time" not in seg:
            seg["start_time"] = (cumulative / total_words) * total_duration
        if "end_time" not in seg:
            seg["end_time"] = ((cumulative + wc) / total_words) * total_duration
        cumulative += wc


def _estimate_timeline(segments):
    """Fallback: estimate timestamps from word counts assuming ~2.5 words/sec."""
    wps = 2.5
    t = 0
    for seg in segments:
        wc = seg.get("word_count", len(seg["text"].split()))
        seg["start_time"] = t
        seg["end_time"] = t + wc / wps
        t = seg["end_time"]
    return segments


# ─── 5. Assembly with Crossfade ──────────────────────────────────────────────

def assemble_broll_reel(anchor_video, segments, broll_image_paths, headline, badge_text, output_path, fps=25, fullframe_anchor=None):
    """
    Assemble the final reel by interleaving anchor video and B-roll frames.
    
    - anchor_video: the portrait-fixed Kavya video (branded layout, with audio)
    - segments: list with type, start_time, end_time
    - broll_image_paths: list of image paths (None for anchor segments)
    - output_path: final assembled video
    - fullframe_anchor: optional full-frame center-cropped Kavya video (immersive).
                        If provided, ANCHOR segments use this instead of branded layout.
    
    Strategy:
    1. Extract the full audio track from anchor_video
    2. For each segment, create either:
       - An anchor clip (from fullframe_anchor if available, else anchor_video)
       - A B-roll clip (render image frame, no audio)
    3. Concatenate all clips with crossfade transitions
    4. Lay the continuous audio back over the assembled video
    """
    anchor_video = str(anchor_video)
    output_path = str(output_path)
    # Use full-frame crop for anchor segments when available
    anchor_source = str(fullframe_anchor) if fullframe_anchor else anchor_video

    # Step 1: Extract full audio
    audio_path = str(BUILD_DIR / "broll-full-audio.aac")
    subprocess.run(
        ["ffmpeg", "-y", "-i", anchor_video, "-vn", "-acodec", "copy", audio_path],
        capture_output=True, timeout=30
    )

    # Step 2: Create individual segment clips
    clip_paths = []
    for i, seg in enumerate(segments):
        start = seg.get("start_time", 0)
        end = seg.get("end_time", start + 3)
        duration = end - start

        if duration < 0.5:
            continue

        clip_path = str(BUILD_DIR / f"broll-clip-{i}.mp4")

        if seg["type"] == "anchor":
            # Trim from the full-frame anchor (or branded layout fallback)
            subprocess.run(
                ["ffmpeg", "-y", "-i", anchor_source,
                 "-ss", str(start), "-t", str(duration),
                 "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                 clip_path],
                capture_output=True, timeout=60
            )
        elif seg["type"] == "broll" and broll_image_paths[i]:
            # Render B-roll frame
            render_broll_frame(
                broll_image_paths[i], headline, badge_text,
                clip_path, duration, fps
            )
        else:
            # No image available for B-roll, fall back to full-frame anchor
            subprocess.run(
                ["ffmpeg", "-y", "-i", anchor_source,
                 "-ss", str(start), "-t", str(duration),
                 "-an", "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                 clip_path],
                capture_output=True, timeout=60
            )

        if Path(clip_path).exists():
            clip_paths.append(clip_path)

    if not clip_paths:
        print("  ❌ No clips generated")
        return None

    # Step 3: Normalize and concatenate clips with crossfade
    concat_video = str(BUILD_DIR / "broll-concat-video.mp4")
    
    if len(clip_paths) == 1:
        concat_video = clip_paths[0]
    else:
        # Use xfade filter for smooth crossfade transitions
        xfade_duration = 0.3  # 300ms crossfade
        
        # Build filter chain for sequential xfade
        inputs = []
        for cp in clip_paths:
            inputs.extend(["-i", cp])
        
        # For N clips we need N-1 xfade operations
        # Each xfade shortens total by xfade_duration
        filter_parts = []
        
        # Get clip durations
        clip_durations = []
        for cp in clip_paths:
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", cp],
                capture_output=True, text=True, timeout=10
            )
            clip_durations.append(float(probe.stdout.strip()))
        
        if len(clip_paths) == 2:
            offset = clip_durations[0] - xfade_duration
            filter_parts.append(
                f"[0:v][1:v]xfade=transition=fade:duration={xfade_duration}:offset={max(0, offset)}[out]"
            )
            filter_str = ";".join(filter_parts)
            cmd = ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", filter_str,
                "-map", "[out]",
                "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                "-pix_fmt", "yuv420p",
                concat_video
            ]
        else:
            # Chain xfades: [0][1]xfade→[v1], [v1][2]xfade→[v2], ...
            cumulative_offset = 0
            prev_label = "0:v"
            for j in range(1, len(clip_paths)):
                cumulative_offset += clip_durations[j - 1] - (xfade_duration if j > 1 else 0)
                offset = cumulative_offset - xfade_duration
                out_label = "out" if j == len(clip_paths) - 1 else f"v{j}"
                filter_parts.append(
                    f"[{prev_label}][{j}:v]xfade=transition=fade:duration={xfade_duration}:offset={max(0, offset)}[{out_label}]"
                )
                prev_label = out_label

            filter_str = ";".join(filter_parts)
            cmd = ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", filter_str,
                "-map", "[out]",
                "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                "-pix_fmt", "yuv420p",
                concat_video
            ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  ⚠️ Crossfade failed, falling back to concat: {result.stderr[-200:]}")
            # Fallback: simple concat
            list_file = str(BUILD_DIR / "broll-concat-list.txt")
            with open(list_file, "w") as f:
                for cp in clip_paths:
                    f.write(f"file '{cp}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
                 "-c:v", "libx264", "-crf", "18", "-preset", "fast",
                 "-pix_fmt", "yuv420p", concat_video],
                capture_output=True, timeout=60
            )

    # Step 4: Mux the continuous audio back onto the assembled video
    # Use -shortest on VIDEO stream only — pad video with last frame to match audio
    # This prevents xfade transitions from eating Kavya's last words
    # Get audio duration to pad video if needed
    audio_dur_probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, timeout=10
    )
    video_dur_probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", concat_video],
        capture_output=True, text=True, timeout=10
    )
    audio_dur = float(audio_dur_probe.stdout.strip()) if audio_dur_probe.stdout.strip() else 0
    video_dur = float(video_dur_probe.stdout.strip()) if video_dur_probe.stdout.strip() else 0

    if video_dur < audio_dur - 0.1:
        # Video is shorter than audio (xfade ate time) — pad video with tpad (freeze last frame)
        pad_time = audio_dur - video_dur + 0.5  # small extra buffer
        print(f"  📐 Padding video +{pad_time:.1f}s to match audio ({video_dur:.1f}s → {audio_dur:.1f}s)")
        subprocess.run(
            ["ffmpeg", "-y",
             "-i", concat_video, "-i", audio_path,
             "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={pad_time}[v]",
             "-map", "[v]", "-map", "1:a",
             "-c:v", "libx264", "-crf", "18", "-preset", "fast",
             "-c:a", "aac", "-shortest",
             output_path],
            capture_output=True, timeout=120
        )
    else:
        subprocess.run(
            ["ffmpeg", "-y",
             "-i", concat_video, "-i", audio_path,
             "-c:v", "copy", "-c:a", "aac",
             "-shortest",
             output_path],
            capture_output=True, timeout=60
        )

    if Path(output_path).exists():
        dur_probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", output_path],
            capture_output=True, text=True, timeout=10
        )
        print(f"  ✅ B-roll assembly complete: {float(dur_probe.stdout.strip()):.1f}s")
        return output_path

    print("  ❌ B-roll assembly failed")
    return None


# ─── Utility ─────────────────────────────────────────────────────────────────

def _wrap_headline(text, max_chars=28, max_lines=3):
    """Word-wrap headline into lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
        else:
            current = f"{current} {word}".strip() if current else word
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines


if __name__ == "__main__":
    # Test
    print("B-Roll Builder module loaded successfully")
