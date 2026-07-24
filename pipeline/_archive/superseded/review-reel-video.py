#!/usr/bin/env python3
"""
AI Video Quality Gate for The Videshi Reels/Shorts.
Extracts frames from a video, sends to GPT-4o + Gemini for review.
Both must pass (or be unavailable) for the video to proceed.

Usage:
  python3 review-reel-video.py <video_path> [--title "..."] [--headline "..."]
  
Exit codes: 0 = pass, 1 = fail, 2 = error
"""

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile

import requests

# ── Load keys ─────────────────────────────────────────────────────
def _load_env(path):
    env = {}
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

_ai = _load_env("~/workspace/.env.openai")
_gm = _load_env("~/workspace/.env.google-ai")
OPENAI_KEY = _ai.get("OPENAI_API_KEY", "")
GEMINI_KEY = _gm.get("GOOGLE_AI_API_KEY", "")


def extract_frames(video_path, count=5):
    """Extract evenly-spaced frames from the video as JPEG base64 strings."""
    # Get duration
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    duration = float(r.stdout.strip())
    
    frames = []
    tmpdir = tempfile.mkdtemp(prefix="review-")
    
    # Extract frames at evenly spaced intervals
    for i in range(count):
        t = (duration / (count + 1)) * (i + 1)
        out_path = os.path.join(tmpdir, f"frame_{i}.jpg")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", video_path,
             "-vframes", "1", "-q:v", "2", out_path],
            capture_output=True
        )
        if os.path.exists(out_path):
            with open(out_path, "rb") as f:
                frames.append(base64.b64encode(f.read()).decode())
    
    # Cleanup
    for f in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, f))
    os.rmdir(tmpdir)
    
    return frames, duration


def extract_audio_snippet(video_path):
    """Check if video has audio and if there's speech."""
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_name,bit_rate",
         "-of", "csv=p=1", video_path],
        capture_output=True, text=True
    )
    audio_info = r.stdout.strip()
    has_audio = bool(audio_info)
    
    # Check if audio is silent (very low bitrate = likely generated silence)
    is_likely_silent = False
    if has_audio:
        try:
            parts = audio_info.split(",")
            bitrate = int(parts[-1]) if len(parts) > 1 else 0
            # Under 10kbps is likely synthetic silence
            is_likely_silent = bitrate < 10000
        except (ValueError, IndexError):
            pass
    
    return has_audio, is_likely_silent


def review_with_openai(frames, title, headline, duration, has_audio):
    """Send frames to GPT-4o for visual + metadata review."""
    if not OPENAI_KEY:
        return None
    
    content = [
        {"type": "text", "text": f"""You are a quality reviewer for The Videshi, an Indian diaspora news platform.
Review this video reel before it's published to YouTube Shorts and Instagram Reels.

VIDEO METADATA:
- Title: {title}
- Article Headline: {headline}
- Duration: {duration:.1f}s
- Has Audio: {has_audio}

I'm showing you {len(frames)} frames extracted at equal intervals from the video.

Check for these issues (score 1-10):
1. VIDEO QUALITY: Is the video clear, not pixelated, not distorted? Are dimensions correct (9:16 portrait)?
2. LIP SYNC / AVATAR: If there's a person/avatar, do they look natural? Any glitches, artifacts, or frozen frames?
3. TEXT READABILITY: Can you read the text overlays? Any cut-off text, garbled text, or overlapping elements?
4. BRANDING: Does it look professional? Consistent styling? THE VIDESHI branding visible?
5. CONTENT MATCH: Does the visual content match the title/headline? Any mismatched or wrong content?
6. DUPLICATES: Do multiple frames look identical (suggesting a static/broken video)?
7. TRANSITION: Any visual glitches at frame boundaries (different styles, sudden jumps)?

Respond in JSON:
{{"score": N, "pass": true/false, "issues": ["specific issue 1", "specific issue 2"], "details": "brief summary"}}

Score 7+ = pass. Be strict — this affects brand reputation."""}
    ]
    
    for i, frame_b64 in enumerate(frames):
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{frame_b64}", "detail": "low"}
        })
    
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
                "max_tokens": 500
            },
            timeout=60
        )
        if r.status_code == 200:
            return json.loads(r.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"  ⚠️ OpenAI vision review failed: {e}")
    
    return None


def review_with_gemini(frames, title, headline, duration, has_audio):
    """Send frames to Gemini for visual review."""
    if not GEMINI_KEY:
        return None
    
    parts = [
        {"text": f"""You are a quality reviewer for The Videshi, an Indian diaspora news platform.
Review this video reel before publishing to YouTube Shorts and Instagram.

METADATA: Title: {title} | Headline: {headline} | Duration: {duration:.1f}s | Audio: {has_audio}

I'm showing you {len(frames)} frames from the video. Check:
1. Video quality (clear, correct 9:16 dimensions, no artifacts)
2. Avatar/person appearance (natural, no glitches, lip sync plausible)
3. Text readability (no cut-off, overlap, garbled text)
4. Branding consistency (THE VIDESHI visible, professional look)
5. Content matches headline (no mismatched content)
6. No duplicate/frozen frames
7. Clean transitions between segments

Respond in JSON: {{"score": N, "pass": true/false, "issues": ["issue1"], "details": "summary"}}
Score 7+ = pass. Be strict about quality."""}
    ]
    
    for frame_b64 in frames:
        parts.append({
            "inline_data": {"mime_type": "image/jpeg", "data": frame_b64}
        })
    
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": parts}],
                "generationConfig": {"responseMimeType": "application/json", "temperature": 0.3}
            },
            timeout=60
        )
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        print(f"  ⚠️ Gemini vision review failed: {e}")
    
    return None


def main():
    parser = argparse.ArgumentParser(description="AI video quality gate")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--title", default="", help="Video title")
    parser.add_argument("--headline", default="", help="Article headline")
    parser.add_argument("--json", action="store_true", help="Output JSON result")
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"❌ Video not found: {args.video}")
        sys.exit(2)
    
    print(f"🔍 Reviewing: {os.path.basename(args.video)}")
    
    # Extract frames
    frames, duration = extract_frames(args.video, count=5)
    if not frames:
        print("❌ Could not extract frames")
        sys.exit(2)
    print(f"  📸 Extracted {len(frames)} frames from {duration:.1f}s video")
    
    # Check audio
    has_audio, is_silent = extract_audio_snippet(args.video)
    print(f"  🔊 Audio: {'yes' if has_audio else 'NO'} | Likely silent: {is_silent}")
    
    # Review with both AIs
    results = {}
    
    print("  🤖 GPT-4o review...")
    gpt_result = review_with_openai(frames, args.title, args.headline, duration, has_audio)
    if gpt_result:
        results["gpt4o"] = gpt_result
        print(f"     Score: {gpt_result.get('score', '?')}/10 — {'✅ PASS' if gpt_result.get('pass') else '❌ FAIL'}")
        if gpt_result.get("issues"):
            for issue in gpt_result["issues"]:
                print(f"     ⚠️ {issue}")
    else:
        print("     ⚠️ Unavailable")
    
    print("  🤖 Gemini review...")
    gem_result = review_with_gemini(frames, args.title, args.headline, duration, has_audio)
    if gem_result:
        results["gemini"] = gem_result
        print(f"     Score: {gem_result.get('score', '?')}/10 — {'✅ PASS' if gem_result.get('pass') else '❌ FAIL'}")
        if gem_result.get("issues"):
            for issue in gem_result["issues"]:
                print(f"     ⚠️ {issue}")
    else:
        print("     ⚠️ Unavailable")
    
    # Decision: both must pass (or be unavailable)
    all_pass = True
    any_reviewed = False
    for name, result in results.items():
        any_reviewed = True
        if not result.get("pass", True):
            all_pass = False
    
    # If no reviewer available, pass by default (fail-safe)
    if not any_reviewed:
        print("\n⚠️ No AI reviewer available — passing by default")
        final_pass = True
    else:
        final_pass = all_pass
    
    if args.json:
        print(json.dumps({"pass": final_pass, "results": results}, indent=2))
    
    if final_pass:
        print(f"\n✅ PASSED — video approved for upload")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED — video has quality issues, do NOT upload")
        sys.exit(1)


if __name__ == "__main__":
    main()
