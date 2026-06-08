#!/usr/bin/env python3
"""
AI Quality Feedback Loop for The Videshi Reels
===============================================
Reviews a generated reel, identifies issues, and auto-fixes them.
Loops until the reel passes or max iterations hit.

Issues it catches and fixes:
- Captions too large / covering avatar → re-chunk + resize + reposition
- Audio too quiet / too loud → re-mix with adjusted levels
- Video too long / too short → flag for re-generation
- Avatar not visible enough → adjust caption placement
- Bad framing → flag for different avatar look

Usage:
  from reel_quality_loop import review_and_fix_reel
  final_path = review_and_fix_reel(raw_avatar_path, article, avatar_info)
"""

import os, sys, json, subprocess, re, tempfile
from pathlib import Path
from datetime import datetime

import requests

PIPELINE_DIR = Path(__file__).parent
BUILD_DIR = PIPELINE_DIR / "reels" / "build"
MUSIC_DIR = PIPELINE_DIR / "music"


def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                raw = line
                if raw.startswith('export '): raw = raw[7:]
                k, v = raw.split('=', 1)
                env[k] = v.strip('"').strip("'")
    return env


# Load keys
OPENAI_KEY = ""
for p in ["~/workspace/.env.openai", "~/.env.openai"]:
    ep = os.path.expanduser(p)
    if os.path.exists(ep):
        e = load_env(p)
        OPENAI_KEY = e.get("OPENAI_API_KEY", "")
        if OPENAI_KEY: break


# ─── Word-level caption generation ──────────────────────────────────────────

def get_word_timestamps(video_path):
    """Get word-level timestamps from Whisper API."""
    r = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        files={"file": ("audio.mp4", open(video_path, "rb"), "video/mp4")},
        data={
            "model": "whisper-1",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word",
            "language": "en"
        },
        timeout=60
    )
    if r.status_code != 200:
        print(f"  ⚠️ Whisper failed: {r.status_code}")
        return None
    return r.json().get('words', [])


def words_to_chunked_srt(words, max_words_per_chunk=3):
    """Convert word timestamps to SRT with short 2-3 word chunks."""
    if not words:
        return None

    srt_lines = []
    idx = 1
    i = 0

    while i < len(words):
        chunk_words = words[i:i + max_words_per_chunk]
        start = chunk_words[0]['start']
        end = chunk_words[-1]['end']
        text = " ".join(w['word'] for w in chunk_words)

        # Format timestamps
        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt_lines.append(f"{idx}")
        srt_lines.append(f"{fmt(start)} --> {fmt(end)}")
        srt_lines.append(text)
        srt_lines.append("")

        idx += 1
        i += max_words_per_chunk

    return "\n".join(srt_lines)


# ─── Video analysis helpers ─────────────────────────────────────────────────

def get_video_info(path):
    """Get video duration and dimensions."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, timeout=60
    )
    data = json.loads(result.stdout)
    info = {"duration": float(data['format']['duration'])}
    for s in data.get('streams', []):
        if s['codec_type'] == 'video':
            info['width'] = int(s['width'])
            info['height'] = int(s['height'])
    return info


def get_audio_levels(path):
    """Get mean and max volume in dB."""
    result = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "volumedetect", "-f", "null", "/dev/null"],
        capture_output=True, text=True, timeout=30
    )
    stderr = result.stderr
    mean = max_vol = None
    for line in stderr.split('\n'):
        if 'mean_volume' in line:
            m = re.search(r'mean_volume:\s*([-\d.]+)', line)
            if m: mean = float(m.group(1))
        if 'max_volume' in line:
            m = re.search(r'max_volume:\s*([-\d.]+)', line)
            if m: max_vol = float(m.group(1))
    return {"mean_db": mean, "max_db": max_vol}


def extract_frame(video_path, timestamp, output_path):
    """Extract a single frame at given timestamp."""
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(timestamp), "-i", str(video_path),
         "-frames:v", "1", "-q:v", "2", str(output_path)],
        capture_output=True, timeout=15
    )
    return output_path.exists()


# ─── AI Review ──────────────────────────────────────────────────────────────

def ai_review_reel(video_path, article_headline, avatar_name):
    """AI reviews the reel and returns structured feedback with severity."""

    info = get_video_info(video_path)
    audio = get_audio_levels(video_path)

    # Extract frames at key moments for review
    frames_data = []
    check_times = [1.0, 3.5, info['duration'] / 2, info['duration'] - 4]
    for t in check_times:
        if t < 0 or t > info['duration']:
            continue
        frame_path = BUILD_DIR / f"review_frame_{int(t*10)}.jpg"
        if extract_frame(video_path, t, frame_path):
            import base64
            with open(frame_path, 'rb') as f:
                frames_data.append({
                    "time": t,
                    "base64": base64.b64encode(f.read()).decode()
                })

    # Build review prompt
    prompt = f"""You are a quality reviewer for short-form news reels (Instagram Reels / YouTube Shorts) for The Videshi, an Indian diaspora news platform.

Review this reel and identify ALL issues. Be strict — this goes to real audiences.

## Reel metadata
- Article: {article_headline}
- Avatar: {avatar_name}
- Duration: {info['duration']:.1f}s
- Resolution: {info.get('width', '?')}x{info.get('height', '?')}
- Mean audio: {audio.get('mean_db', '?')} dB
- Max audio: {audio.get('max_db', '?')} dB

## Check these areas and rate each as PASS, LOW (minor), MEDIUM, or HIGH (must fix):

1. **CAPTIONS_SIZE**: Are subtitles/captions readable but not overwhelming? Should be lower-third, max 3 words, clean font. If they cover more than 30% of frame → HIGH.
2. **AVATAR_VISIBILITY**: Is the avatar/anchor clearly visible and not obscured? Face should be unobstructed.
3. **AUDIO_LEVELS**: Mean should be -18 to -12 dB. Below -22 = too quiet (HIGH). Above -8 = too loud (HIGH).
4. **DURATION**: 20-45s is ideal. Over 60s = HIGH. Under 15s = HIGH.
5. **HOOK_FRAME**: Does the opening (0-3s) grab attention? Text should be punchy, readable.
6. **END_CARD**: Does the video end cleanly with branding?
7. **FRAMING**: Is the overall composition good for mobile vertical viewing? Avatar should be prominent.

Return JSON only:
{{
  "overall": "PASS" | "FAIL",
  "issues": [
    {{
      "area": "CAPTIONS_SIZE",
      "severity": "HIGH",
      "problem": "Captions cover 80% of frame, obscuring avatar",
      "fix": "Split into 2-3 word chunks, FontSize 12, position in lower 20% of frame"
    }}
  ],
  "high_count": 2,
  "summary": "Brief overall assessment"
}}"""

    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

    # Add frame images
    for fd in frames_data:
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{fd['base64']}",
                "detail": "low"
            }
        })

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 800,
        },
        timeout=45
    )

    if r.status_code != 200:
        print(f"  ⚠️ Review API failed: {r.status_code}")
        return None

    text = r.json()['choices'][0]['message']['content']

    # Parse JSON from response
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    print(f"  ⚠️ Could not parse review response")
    return None


# ─── Auto-fix implementations ───────────────────────────────────────────────

def fix_captions(video_path, output_path, words=None, font_size=12, max_words=3, margin_v=120):
    """Re-burn captions: small chunks, lower-third positioning."""
    if not words:
        print("    Getting word timestamps...")
        words = get_word_timestamps(video_path)
        if not words:
            return False

    srt_content = words_to_chunked_srt(words, max_words_per_chunk=max_words)
    if not srt_content:
        return False

    srt_path = BUILD_DIR / "fixed_captions.srt"
    with open(srt_path, 'w') as f:
        f.write(srt_content)

    # Branded lower-third captions: gold on semi-transparent navy
    style = (
        f"FontName=DejaVu Sans Bold,FontSize={font_size},"
        f"PrimaryColour=&H0037AFD4,"  # Gold (#D4AF37) in ABGR
        f"OutlineColour=&HAA2E1A1A,"  # Semi-transparent navy
        f"BackColour=&HAA2E1A1A,"
        f"Bold=1,Outline=2,Shadow=0,"
        f"MarginV={margin_v},Alignment=2"  # Bottom-center
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-c:a", "copy",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=300, text=True)
    if result.returncode != 0:
        print(f"    ⚠️ Caption fix failed: {result.stderr[-200:]}")
        return False
    return output_path.exists()


def fix_audio_levels(video_path, output_path, target_db=-15):
    """Adjust audio to target mean dB level."""
    current = get_audio_levels(video_path)
    if current['mean_db'] is None:
        return False

    adjustment = target_db - current['mean_db']
    adjustment_db = max(-10, min(15, adjustment))  # Clamp

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-af", f"volume={adjustment_db}dB",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    return output_path.exists()


# ─── Main feedback loop ─────────────────────────────────────────────────────

def review_and_fix_reel(video_path, article_headline, avatar_name,
                        max_iterations=3, words=None):
    """
    Main feedback loop:
    1. AI reviews the reel
    2. If HIGH issues found → auto-fix each one
    3. Re-review the fixed version
    4. Repeat until PASS or max iterations
    
    Returns (final_path, review_result, iterations)
    """
    video_path = Path(video_path)
    current = video_path
    iteration = 0

    # Get word timestamps once (reused across caption fixes)
    if words is None:
        print("  📝 Getting word-level timestamps...")
        words = get_word_timestamps(str(video_path))

    while iteration < max_iterations:
        iteration += 1
        print(f"\n  🔍 Review iteration {iteration}/{max_iterations}...")

        review = ai_review_reel(str(current), article_headline, avatar_name)
        if not review:
            print("  ⚠️ Review failed, proceeding with current version")
            return str(current), None, iteration

        high_issues = [i for i in review.get('issues', []) if i.get('severity') == 'HIGH']
        print(f"  📋 Result: {review.get('overall', '?')} — {review.get('summary', '')}")
        print(f"     HIGH issues: {len(high_issues)}")

        if review.get('overall') == 'PASS' or not high_issues:
            print(f"  ✅ Reel passed review after {iteration} iteration(s)")
            return str(current), review, iteration

        # Apply fixes for HIGH issues
        fixed = current
        for issue in high_issues:
            area = issue.get('area', '')
            fix_desc = issue.get('fix', '')
            print(f"    🔧 Fixing {area}: {issue.get('problem', '')[:60]}")

            if area == 'CAPTIONS_SIZE':
                # Parse fix suggestions for parameters
                font_size = 12
                max_w = 3
                margin = 120
                if 'FontSize' in fix_desc:
                    m = re.search(r'FontSize\s*(\d+)', fix_desc)
                    if m: font_size = int(m.group(1))
                if '2 word' in fix_desc.lower() or '2-word' in fix_desc.lower():
                    max_w = 2

                out = BUILD_DIR / f"fix_captions_iter{iteration}.mp4"
                if fix_captions(str(fixed), out, words=words,
                               font_size=font_size, max_words=max_w, margin_v=margin):
                    fixed = out
                    print(f"    ✅ Captions fixed (size={font_size}, chunks={max_w}w)")

            elif area == 'AUDIO_LEVELS':
                out = BUILD_DIR / f"fix_audio_iter{iteration}.mp4"
                if fix_audio_levels(str(fixed), out):
                    fixed = out
                    print(f"    ✅ Audio levels adjusted")

            elif area in ('AVATAR_VISIBILITY', 'FRAMING'):
                # Try portrait fix for letterboxed content
                from portrait_fix import detect_letterbox, fix_avatar_portrait, burn_captions_news_layout
                lb_info = detect_letterbox(str(fixed))
                if lb_info.get("is_letterboxed"):
                    out = BUILD_DIR / f"fix_portrait_iter{iteration}.mp4"
                    if fix_avatar_portrait(str(fixed), str(out), article_headline, lb_info):
                        fixed = out
                        print(f"    ✅ Portrait fix applied (news layout)")
                    else:
                        print(f"    ⚠️ Portrait fix failed, flagging for re-selection")
                else:
                    print(f"    ⚠️ {area} requires avatar re-selection (flagged)")

            elif area == 'DURATION':
                print(f"    ⚠️ Duration requires script re-generation (flagged)")

            else:
                print(f"    ⚠️ Unknown area {area}, skipping")

        if fixed != current:
            current = fixed
        else:
            # No fixes could be applied — break to avoid infinite loop
            print("  ⚠️ No fixes could be applied, stopping loop")
            break

    print(f"  ⚠️ Max iterations ({max_iterations}) reached")
    return str(current), review, iteration


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 reel_quality_loop.py <video_path> [headline] [avatar_name]")
        sys.exit(1)

    video = sys.argv[1]
    headline = sys.argv[2] if len(sys.argv) > 2 else "Test Article"
    avatar = sys.argv[3] if len(sys.argv) > 3 else "Kavya"

    final, review, iters = review_and_fix_reel(video, headline, avatar)
    print(f"\nFinal: {final}")
    print(f"Iterations: {iters}")
    if review:
        print(f"Review: {json.dumps(review, indent=2)}")
