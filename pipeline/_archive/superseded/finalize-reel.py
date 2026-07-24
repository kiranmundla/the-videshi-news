#!/usr/bin/env python3
"""
Finalize reel: add hook + end card + music, upload, generate caption/tags.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

for envfile in ['~/.env.supabase']:
    try:
        os.environ.update(load_env(envfile))
    except FileNotFoundError:
        pass

import requests
from portrait_fix import normalize_audio_social

BUILD_DIR = Path(__file__).parent / "reels" / "build"
REELS_DIR = Path(__file__).parent / "reels"
MUSIC_DIR = Path(__file__).parent / "music"
PIPELINE_DIR = Path(__file__).parent

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_ANON_KEY", "") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}

# ─── Config ──────────────────────────────────────────────────────────────────
AVATAR_VIDEO = REELS_DIR / "reel-welcome-to-the-jungle-fullframe-final.mp4"
HOOK_VIDEO = BUILD_DIR / "hook_25fps.mp4"
SLUG = "welcome-to-the-jungle-fullframe"

ARTICLE = {
    "id": "6a036999-cf7e-48b2-961e-c089efe7f1ea",
    "headline": "Welcome To The Jungle Has Akshay Kumar, Fifteen Co-Stars, and the Promise That Nobody Has to Think for Two Hours.",
    "subheadline": "The Welcome franchise returns with its biggest cast yet. Here's what NRIs need to know about the June 26 release.",
    "slug": "welcome-to-the-jungle-akshay-kumar-ensemble-comedy-june-26-nri-20260603",
    "category": "entertainment",
}

ARTICLE_URL = f"https://thevideshi.com/articles/{ARTICLE['slug']}"


def get_video_duration(path):
    p = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10
    )
    return float(p.stdout.strip()) if p.stdout.strip() else 0


def get_or_create_end_card():
    end_card = BUILD_DIR / "end_card_25fps_silent.mp4"
    if end_card.exists():
        return end_card
    png = BUILD_DIR / "end_card.png"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=#1a1a2e:s=1080x1920:d=1",
        "-vf",
        "drawtext=text='THE VIDESHI':fontsize=56:fontcolor=#d4af37:x=(w-text_w)/2:y=(h/2)-60:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
        "drawtext=text='thevideshi.com':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=(h/2)+20:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
        "drawtext=text='Follow for more':fontsize=24:fontcolor=#aaaaaa:x=(w-text_w)/2:y=(h/2)+80:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "-frames:v", "1", str(png)
    ], capture_output=True, timeout=15)
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png),
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", "3", "-c:v", "libx264", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-r", "25", "-s", "1080x1920",
        "-c:a", "aac", "-b:a", "128k", "-shortest", str(end_card)
    ], capture_output=True, timeout=30)
    return end_card


def normalize_segment(input_path, output_path):
    """Re-encode to consistent format for concat."""
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-r", "25", "-s", "1080x1920",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)


def concat_segments(segments, output_path):
    inputs = []
    filter_parts = []
    for i, seg in enumerate(segments):
        inputs.extend(["-i", str(seg)])
        filter_parts.append(f"[{i}:v][{i}:a]")
    filter_str = "".join(filter_parts) + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_str,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"  ❌ Concat failed: {result.stderr[-300:]}")
        return False
    return output_path.exists()


def add_music(video_path, output_path, kavya_duration=None):
    hook_path = MUSIC_DIR / "breaking-news-breaking-news-30s.mp3"
    under_path = MUSIC_DIR / "dramatic-dark-suspense-thriller.mp3"
    outro_path = MUSIC_DIR / "breaking-news-breaking-news-30s.mp3"

    # Entertainment profile volumes
    hook_vol, under_vol, outro_vol = 0.5, 0.05, 0.4

    total_dur = get_video_duration(video_path)
    hook_dur = 3.0
    end_dur = 3.0
    kavya_dur = kavya_duration or (total_dur - hook_dur - end_dur)
    outro_start_ms = int((total_dur - end_dur) * 1000)

    # Ensure underscore doesn't try to trim beyond file length
    under_trim = min(kavya_dur, 25)  # Cap at 25s

    filter_complex = (
        f"[0:a]volume=1.0[voice];"
        f"[1:a]atrim=0:{hook_dur},asetpts=PTS-STARTPTS,volume={hook_vol},afade=t=out:st={hook_dur-0.5}:d=0.5[hook_sting];"
        f"[2:a]atrim=0:{under_trim},asetpts=PTS-STARTPTS,volume={under_vol},afade=t=in:st=0:d=1,afade=t=out:st={under_trim-1.2}:d=1.2[underscore];"
        f"[3:a]atrim=25:28,asetpts=PTS-STARTPTS,volume={outro_vol},afade=t=in:st=0:d=0.3,afade=t=out:st=2.5:d=0.5[outro_sting];"
        f"[hook_sting]adelay=0|0[hook_delayed];"
        f"[underscore]adelay={int(hook_dur*1000)}|{int(hook_dur*1000)}[under_delayed];"
        f"[outro_sting]adelay={outro_start_ms}|{outro_start_ms}[outro_delayed];"
        f"[voice][hook_delayed][under_delayed][outro_delayed]amix=inputs=4:duration=first:dropout_transition=0:weights=1 1 1 1,volume=4.0[audio_out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(hook_path),
        "-i", str(under_path),
        "-i", str(outro_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[audio_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"  ❌ Music mix failed: {result.stderr[-300:]}")
        return False
    return True


def upload_to_supabase(local_path, storage_name):
    with open(local_path, 'rb') as f:
        r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{storage_name}",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "video/mp4",
                "x-upsert": "true"
            },
            data=f.read(),
            timeout=120
        )
    if r.status_code in (200, 201):
        url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{storage_name}"
        print(f"  ✅ Uploaded: {url}")
        return url
    else:
        print(f"  ❌ Upload failed: {r.status_code} {r.text[:200]}")
        return None


def main():
    print("🎬 Finalizing reel with hook + end card + music")

    # 1. Normalize avatar video for concat
    print("\n1️⃣ Normalizing avatar segment...")
    normalized = BUILD_DIR / "avatar_normalized_final.mp4"
    normalize_segment(AVATAR_VIDEO, normalized)

    # 2. Get end card
    print("2️⃣ Getting end card...")
    end_card = get_or_create_end_card()

    # 3. Concat: hook + avatar + end card
    print("3️⃣ Assembling: hook + avatar + end card...")
    assembled = REELS_DIR / f"reel-{SLUG}-assembled.mp4"
    if not concat_segments([HOOK_VIDEO, normalized, end_card], assembled):
        print("❌ Assembly failed")
        return

    kavya_dur = get_video_duration(AVATAR_VIDEO)

    # 4. Add music
    print("4️⃣ Adding music...")
    music_mixed = REELS_DIR / f"reel-{SLUG}-music.mp4"
    if not add_music(assembled, music_mixed, kavya_duration=kavya_dur):
        print("❌ Music mix failed")
        return

    # 5. Normalize audio (-14 LUFS)
    print("5️⃣ Normalizing audio...")
    final = REELS_DIR / f"reel-{SLUG}-final-v2.mp4"
    normalize_audio_social(music_mixed, final)

    if not final.exists():
        final = music_mixed

    dur = get_video_duration(final)
    size_mb = final.stat().st_size / (1024 * 1024)
    print(f"\n✅ Final reel: {final}")
    print(f"   Duration: {dur:.1f}s | Size: {size_mb:.1f}MB")

    # 6. Upload to Supabase
    print("\n6️⃣ Uploading to Supabase...")
    storage_name = f"reels/{SLUG}-final.mp4"
    video_url = upload_to_supabase(final, storage_name)

    # 7. Build caption and metadata
    print("\n7️⃣ Caption & metadata:")
    caption = f"""{ARTICLE['headline']}

{ARTICLE['subheadline']}

Read the full story: {ARTICLE_URL}

#bollywood #entertainment #celebrity #india #akshaykumar #welcometothejungle #comedy #nri #indiandiaspora #thevideshi"""

    yt_title = "Welcome to the Jungle — Akshay Kumar Returns with 15 Stars | The Videshi"
    yt_description = f"""{ARTICLE['headline']}

{ARTICLE['subheadline']}

📰 Full story: {ARTICLE_URL}

The Welcome franchise is back with its biggest ensemble cast ever — Akshay Kumar, Suniel Shetty, Paresh Rawal, and 12 more stars come together for a wild comedy adventure releasing June 26.

🔔 Subscribe to The Videshi for daily Indian diaspora news
🌐 thevideshi.com

#Shorts #WelcomeToTheJungle #AkshayKumar #Bollywood #Comedy #NRI #IndianDiaspora #TheVideshi"""

    yt_tags = "Welcome to the Jungle,Akshay Kumar,Suniel Shetty,Paresh Rawal,Bollywood,Comedy,Indian Movie,NRI,Indian Diaspora,The Videshi,Bollywood 2026"

    print(f"\n{'='*60}")
    print("📱 INSTAGRAM REEL CAPTION:")
    print(f"{'='*60}")
    print(caption)
    print(f"\n{'='*60}")
    print("📺 YOUTUBE SHORT:")
    print(f"{'='*60}")
    print(f"Title: {yt_title}")
    print(f"\nDescription:\n{yt_description}")
    print(f"\nTags: {yt_tags}")
    print(f"\n{'='*60}")

    # 8. Register in prebuilt_reels
    if video_url:
        print("\n8️⃣ Registering prebuilt reel...")
        payload = {
            "article_id": ARTICLE['id'],
            "article_slug": ARTICLE['slug'],
            "headline": ARTICLE['headline'],
            "video_path": str(final),
            "video_url": video_url,
            "caption": caption,
            "status": "ready",
            "source": "heygen",
            "avatar_look": "Kavya_standing_indoor_front",
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
            headers={**SB_HEADERS, "Prefer": "return=representation"},
            json=payload
        )
        if r.status_code in (200, 201):
            print(f"  ✅ Registered (status=ready)")
        else:
            print(f"  ⚠️ Register: {r.status_code} {r.text[:200]}")

    # Copy final to your_files for download
    import shutil
    dl_path = Path.home() / "workspace" / "your_files" / "welcome-jungle-reel-final.mp4"
    shutil.copy2(final, dl_path)
    print(f"\n📥 Download: {dl_path}")


if __name__ == "__main__":
    main()
