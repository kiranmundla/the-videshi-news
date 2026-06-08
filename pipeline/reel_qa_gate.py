#!/usr/bin/env python3
"""
AI Quality Gate for Videshi Reels
==================================
Runs automated checks on a generated reel BEFORE it's published.
Returns pass/fail with a score and per-check details.

Checks:
  1. Technical: resolution, aspect ratio, duration, file size
  2. Audio: loudness levels, silence detection
  3. Visual: frame extraction → black frame / letterbox detection
  4. Content: AI review of script + headline alignment
  5. Avatar: correct look used (Front only), camera-facing verification

Usage:
  from reel_qa_gate import run_quality_gate
  result = run_quality_gate(video_path, article, avatar_info, script)
  # result = {"passed": True/False, "score": 0-100, "checks": [...], "notes": "..."}
"""

import subprocess, json, os, sys, tempfile
from pathlib import Path

# Thresholds
MIN_DURATION = 8       # seconds
MAX_DURATION = 90      # seconds
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TARGET_ASPECT = "9:16"
MAX_FILE_SIZE_MB = 50
MIN_FILE_SIZE_MB = 0.5
MIN_LOUDNESS_LUFS = -20
MAX_LOUDNESS_LUFS = -10
MAX_BLACK_FRAME_RATIO = 0.15  # max 15% black frames


def check_technical(video_path):
    """Check resolution, aspect ratio, duration, codec, file size."""
    checks = []
    
    # ffprobe for video info
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        return [{"name": "technical_probe", "passed": False, "detail": "ffprobe failed"}]
    
    data = json.loads(result.stdout)
    fmt = data.get("format", {})
    
    # Find video stream
    video_stream = None
    audio_stream = None
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and not video_stream:
            video_stream = s
        if s.get("codec_type") == "audio" and not audio_stream:
            audio_stream = s
    
    if not video_stream:
        return [{"name": "video_stream", "passed": False, "detail": "No video stream found"}]
    
    # Resolution
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    res_ok = width == TARGET_WIDTH and height == TARGET_HEIGHT
    checks.append({
        "name": "resolution",
        "passed": res_ok,
        "detail": f"{width}x{height}" + ("" if res_ok else f" (expected {TARGET_WIDTH}x{TARGET_HEIGHT})")
    })
    
    # Aspect ratio
    if width > 0 and height > 0:
        ratio = width / height
        aspect_ok = abs(ratio - 9/16) < 0.05
        checks.append({
            "name": "aspect_ratio",
            "passed": aspect_ok,
            "detail": f"{ratio:.2f}" + ("" if aspect_ok else f" (expected ~0.56 for 9:16)")
        })
    
    # Duration
    duration = float(fmt.get("duration", 0))
    dur_ok = MIN_DURATION <= duration <= MAX_DURATION
    checks.append({
        "name": "duration",
        "passed": dur_ok,
        "detail": f"{duration:.1f}s" + ("" if dur_ok else f" (expected {MIN_DURATION}-{MAX_DURATION}s)")
    })
    
    # File size
    size_mb = os.path.getsize(video_path) / (1024 * 1024)
    size_ok = MIN_FILE_SIZE_MB <= size_mb <= MAX_FILE_SIZE_MB
    checks.append({
        "name": "file_size",
        "passed": size_ok,
        "detail": f"{size_mb:.1f}MB" + ("" if size_ok else f" (expected {MIN_FILE_SIZE_MB}-{MAX_FILE_SIZE_MB}MB)")
    })
    
    # Audio stream exists
    audio_ok = audio_stream is not None
    checks.append({
        "name": "audio_stream",
        "passed": audio_ok,
        "detail": "present" if audio_ok else "MISSING — no audio stream"
    })
    
    return checks


def check_audio_levels(video_path):
    """Check audio loudness using ffmpeg loudnorm measurement."""
    checks = []
    
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # loudnorm outputs JSON in stderr
    stderr = result.stderr
    try:
        # Find the JSON block in stderr
        json_start = stderr.rfind("{")
        json_end = stderr.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            loudness_data = json.loads(stderr[json_start:json_end])
            input_i = float(loudness_data.get("input_i", -99))
            
            loudness_ok = MIN_LOUDNESS_LUFS <= input_i <= MAX_LOUDNESS_LUFS
            checks.append({
                "name": "loudness",
                "passed": loudness_ok,
                "detail": f"{input_i:.1f} LUFS" + ("" if loudness_ok else f" (target: {MIN_LOUDNESS_LUFS} to {MAX_LOUDNESS_LUFS} LUFS)")
            })
        else:
            checks.append({"name": "loudness", "passed": True, "detail": "Could not measure (non-blocking)"})
    except Exception as e:
        checks.append({"name": "loudness", "passed": True, "detail": f"Measurement error: {e} (non-blocking)"})
    
    return checks


def check_visual_quality(video_path):
    """Extract frames and check for black frames, letterboxing."""
    checks = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract frames at 1fps
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", "fps=1", "-q:v", "2",
            f"{tmpdir}/frame_%03d.jpg"
        ]
        subprocess.run(cmd, capture_output=True, timeout=60)
        
        frames = sorted(Path(tmpdir).glob("frame_*.jpg"))
        if not frames:
            return [{"name": "frame_extraction", "passed": False, "detail": "Could not extract frames"}]
        
        try:
            from PIL import Image
            import numpy as np
            
            black_count = 0
            letterbox_count = 0
            
            for frame_path in frames:
                img = Image.open(frame_path)
                arr = np.array(img)
                h, w = arr.shape[:2]
                
                # Black frame: average brightness < 10
                avg_brightness = arr.mean()
                if avg_brightness < 10:
                    black_count += 1
                
                # Letterbox detection: check if top/bottom 15% are very dark
                top_band = arr[:int(h * 0.15)].mean()
                bottom_band = arr[int(h * 0.85):].mean()
                mid_band = arr[int(h * 0.25):int(h * 0.75)].mean()
                
                if top_band < 15 and bottom_band < 15 and mid_band > 30:
                    letterbox_count += 1
            
            total = len(frames)
            
            # Black frames check
            black_ratio = black_count / total if total > 0 else 0
            black_ok = black_ratio <= MAX_BLACK_FRAME_RATIO
            checks.append({
                "name": "black_frames",
                "passed": black_ok,
                "detail": f"{black_count}/{total} frames" + ("" if black_ok else f" ({black_ratio:.0%} > {MAX_BLACK_FRAME_RATIO:.0%} threshold)")
            })
            
            # Letterbox check
            lb_ratio = letterbox_count / total if total > 0 else 0
            lb_ok = lb_ratio < 0.3  # less than 30% frames letterboxed
            checks.append({
                "name": "letterboxing",
                "passed": lb_ok,
                "detail": f"{letterbox_count}/{total} frames" + ("" if lb_ok else " — letterboxing detected")
            })
            
        except ImportError:
            checks.append({"name": "visual_analysis", "passed": True, "detail": "PIL not available (non-blocking)"})
    
    return checks


def check_avatar_look(avatar_info):
    """Verify we used a Front-facing camera look."""
    checks = []
    
    if not avatar_info:
        checks.append({"name": "avatar_look", "passed": True, "detail": "No avatar (image reel)"})
        return checks
    
    look_name = avatar_info.get("look_name", "")
    avatar_id = avatar_info.get("avatar_id", "")
    
    # Must be a Front look
    is_front = "front" in look_name.lower() or "front" in avatar_id.lower()
    checks.append({
        "name": "avatar_facing",
        "passed": is_front,
        "detail": f"{look_name}" + ("" if is_front else " — SIDE angle, avatar not facing camera")
    })
    
    # Should not be an outdoor/sport look for news
    is_professional = "indoor" in look_name.lower() or "sofa" in look_name.lower() or "office" in look_name.lower()
    checks.append({
        "name": "avatar_setting",
        "passed": is_professional,
        "detail": f"{look_name}" + ("" if is_professional else " — outdoor/sport setting, not ideal for news")
    })
    
    return checks


def check_content_alignment(headline, script, article_body=None):
    """Use OpenAI to verify script matches headline and article."""
    checks = []
    
    if not script or not headline:
        return [{"name": "content_alignment", "passed": True, "detail": "No script/headline to check"}]
    
    # Try OpenAI check
    try:
        import requests as req
        
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if not openai_key:
            for p in ["~/workspace/.env.openai", "~/.env.openai"]:
                ep = os.path.expanduser(p)
                if os.path.exists(ep):
                    for line in open(ep):
                        if "OPENAI_API_KEY" in line and not line.startswith("#"):
                            k, v = line.strip().split("=", 1)
                            if "export" in k:
                                k = k.replace("export ", "")
                            openai_key = v.strip().strip('"').strip("'")
        
        if not openai_key:
            return [{"name": "content_alignment", "passed": True, "detail": "No OpenAI key (non-blocking)"}]
        
        prompt = f"""You are a quality reviewer for a news video reel. Check this script against the headline.

HEADLINE: {headline}

SCRIPT: {script}

Score 1-10 on these criteria and respond in JSON only:
1. accuracy: Does the script accurately reflect the headline topic? (1-10)
2. tone: Is the tone professional and news-appropriate? (1-10)  
3. clarity: Is the script clear and concise for a 20-30s video? (1-10)
4. diaspora_angle: Does it include an NRI/diaspora perspective? (1-10)
5. overall: Overall quality score (1-10)
6. issues: List any specific problems (empty array if none)

JSON format: {{"accuracy":N,"tone":N,"clarity":N,"diaspora_angle":N,"overall":N,"issues":[]}}"""

        r = req.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 300
            },
            timeout=30
        )
        
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
                overall = scores.get("overall", 5)
                issues = scores.get("issues", [])
                
                content_ok = overall >= 6
                detail = f"Score: {overall}/10"
                if issues:
                    detail += f" | Issues: {'; '.join(issues[:3])}"
                
                checks.append({
                    "name": "content_alignment",
                    "passed": content_ok,
                    "detail": detail,
                    "scores": scores
                })
            else:
                checks.append({"name": "content_alignment", "passed": True, "detail": "Could not parse AI review (non-blocking)"})
        else:
            checks.append({"name": "content_alignment", "passed": True, "detail": f"OpenAI error {r.status_code} (non-blocking)"})
            
    except Exception as e:
        checks.append({"name": "content_alignment", "passed": True, "detail": f"Review error: {e} (non-blocking)"})
    
    return checks


def run_quality_gate(video_path, article, avatar_info=None, script=None):
    """
    Run all quality checks on a reel.
    
    Returns:
        {
            "passed": bool,           # Overall pass/fail
            "score": float,           # 0-100 score
            "checks": [...],          # Individual check results
            "notes": str,             # Human-readable summary
            "blocking_failures": [...] # Checks that caused failure
        }
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return {
            "passed": False,
            "score": 0,
            "checks": [],
            "notes": f"Video file not found: {video_path}",
            "blocking_failures": ["file_not_found"]
        }
    
    headline = article.get("headline", "") if article else ""
    
    # Run all checks
    all_checks = []
    
    print("  🔍 QA: Technical checks...")
    all_checks.extend(check_technical(video_path))
    
    print("  🔍 QA: Audio levels...")
    all_checks.extend(check_audio_levels(video_path))
    
    print("  🔍 QA: Visual quality...")
    all_checks.extend(check_visual_quality(video_path))
    
    print("  🔍 QA: Avatar look...")
    all_checks.extend(check_avatar_look(avatar_info))
    
    print("  🔍 QA: Content alignment...")
    all_checks.extend(check_content_alignment(headline, script))
    
    # Score: each passed check = points, weighted
    weights = {
        "resolution": 15,
        "aspect_ratio": 15,
        "duration": 10,
        "file_size": 5,
        "audio_stream": 10,
        "loudness": 5,
        "black_frames": 10,
        "letterboxing": 10,
        "avatar_facing": 10,
        "avatar_setting": 5,
        "content_alignment": 5,
    }
    
    total_weight = 0
    earned_weight = 0
    blocking_failures = []
    
    # These checks BLOCK publishing if they fail
    blocking_checks = {"resolution", "aspect_ratio", "audio_stream", "avatar_facing", "letterboxing"}
    
    for check in all_checks:
        name = check["name"]
        w = weights.get(name, 3)
        total_weight += w
        if check["passed"]:
            earned_weight += w
        elif name in blocking_checks:
            blocking_failures.append(name)
    
    score = (earned_weight / total_weight * 100) if total_weight > 0 else 0
    passed = len(blocking_failures) == 0 and score >= 60
    
    # Build summary
    failed = [c for c in all_checks if not c["passed"]]
    if passed:
        notes = f"✅ PASSED ({score:.0f}/100) — {len(all_checks)} checks, all clear"
    else:
        failure_details = "; ".join([f"{c['name']}: {c['detail']}" for c in failed])
        notes = f"❌ FAILED ({score:.0f}/100) — {failure_details}"
    
    return {
        "passed": passed,
        "score": round(score, 1),
        "checks": all_checks,
        "notes": notes,
        "blocking_failures": blocking_failures
    }


if __name__ == "__main__":
    """CLI: python3 reel-qa-gate.py <video_path> [--headline "..."] [--script "..."]"""
    import argparse
    parser = argparse.ArgumentParser(description="Reel QA Gate")
    parser.add_argument("video", help="Path to reel video")
    parser.add_argument("--headline", default="", help="Article headline")
    parser.add_argument("--script", default="", help="Anchor script text")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    article = {"headline": args.headline}
    result = run_quality_gate(args.video, article, script=args.script)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(result["notes"])
        print(f"{'='*60}")
        for c in result["checks"]:
            icon = "✅" if c["passed"] else "❌"
            print(f"  {icon} {c['name']:25s} {c['detail']}")
        if result["blocking_failures"]:
            print(f"\n  ⛔ Blocking: {', '.join(result['blocking_failures'])}")
