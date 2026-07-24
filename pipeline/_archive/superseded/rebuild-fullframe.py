#!/usr/bin/env python3
"""
Rebuild the latest reel with full-frame anchor + branded B-roll layout.
Uses existing raw avatar, SRT, and B-roll images — no HeyGen call needed.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Add pipeline to path
sys.path.insert(0, str(Path(__file__).parent))

from portrait_fix import crop_avatar_fullframe, fix_avatar_portrait, burn_captions_news_layout, normalize_audio_social
from broll_builder import parse_srt, map_segments_to_timeline, assemble_broll_reel

BUILD_DIR = Path(__file__).parent / "reels" / "build"
REELS_DIR = Path(__file__).parent / "reels"

# ─── Config for latest reel ─────────────────────────────────────────────────
VIDEO_ID = "57b62ef993444d33ace7d203608c0625"
HEADLINE = "Welcome to the Jungle Trailer Drops June 11 — Akshay, Suniel, Paresh Rawal Reunite"
BADGE = "ENTERTAINMENT"
SLUG = "welcome-to-the-jungle-fullframe"

RAW_AVATAR = BUILD_DIR / f"avatar-raw-{VIDEO_ID}.mp4"
SRT_PATH = BUILD_DIR / f"avatar-raw-{VIDEO_ID}.srt"

# Segmented script (recreated from the SRT to match the existing content)
# The script has 4 segments: ANCHOR → BROLL → ANCHOR → BROLL → ANCHOR
SEGMENTS = [
    {
        "type": "anchor",
        "text": "Get ready for a laughter ride! The trailer for Welcome to the Jungle drops this Wednesday.",
        "word_count": 16,
    },
    {
        "type": "broll",
        "text": "Catch a glimpse of the star-studded cast at the grand launch event in Mumbai.",
        "word_count": 14,
        "image_query": "Welcome to the Jungle bollywood trailer launch",
    },
    {
        "type": "anchor",
        "text": "It brings back the iconic trio Akshay Kumar, Sunil Shetty and Paresh Rawal.",
        "word_count": 13,
    },
    {
        "type": "broll",
        "text": "Expect hilarious chaos in a jungle setting, with elaborate misunderstandings and wild adventures.",
        "word_count": 13,
        "image_query": "Welcome to the Jungle bollywood movie",
    },
    {
        "type": "anchor",
        "text": "Full story at TheVideshi.com",
        "word_count": 5,
    },
]

# B-roll images from the last build (indices match segment positions)
BROLL_IMAGES = [
    None,                                   # seg 0: anchor
    str(BUILD_DIR / "broll-img-1.jpg"),      # seg 1: broll
    None,                                   # seg 2: anchor
    str(BUILD_DIR / "broll-img-3.jpg"),      # seg 3: broll
    None,                                   # seg 4: anchor
]


def main():
    print("🎬 Rebuilding reel with full-frame anchor approach")
    print(f"   Raw avatar: {RAW_AVATAR}")
    print(f"   Headline: {HEADLINE}")
    print()

    # 1. Create full-frame center crop
    fullframe = BUILD_DIR / f"avatar-fullframe-{VIDEO_ID}.mp4"
    print("1️⃣ Creating full-frame center crop...")
    if not crop_avatar_fullframe(str(RAW_AVATAR), str(fullframe)):
        print("❌ Full-frame crop failed")
        return
    
    # 2. Create branded layout (needed for audio extraction in assembly)
    portrait = BUILD_DIR / f"avatar-portrait-fixed-{VIDEO_ID}.mp4"
    print("\n2️⃣ Creating branded portrait layout...")
    lb_info = {
        "is_letterboxed": True, "content_top": 0, "content_bottom": 1079,
        "content_height": 1080, "frame_width": 1920, "frame_height": 1080,
    }
    fix_avatar_portrait(str(RAW_AVATAR), str(portrait), HEADLINE, lb_info, badge_text=BADGE)

    # 3. Map segments to SRT timeline
    print("\n3️⃣ Mapping segments to SRT timeline...")
    srt_entries = parse_srt(str(SRT_PATH))
    segments = map_segments_to_timeline(SEGMENTS, srt_entries)

    # 4. Assemble with full-frame anchor + branded B-roll
    print("\n4️⃣ Assembling: full-frame anchor ↔ branded B-roll...")
    broll_assembled = BUILD_DIR / f"avatar-broll-fullframe-{VIDEO_ID}.mp4"
    result = assemble_broll_reel(
        str(portrait), segments, BROLL_IMAGES,
        HEADLINE, BADGE, str(broll_assembled),
        fullframe_anchor=str(fullframe)
    )
    
    if not result:
        print("❌ Assembly failed")
        return

    # 5. Burn captions (lower position for mixed layout)
    print("\n5️⃣ Burning captions...")
    captioned = BUILD_DIR / f"avatar-captioned-fullframe-{VIDEO_ID}.mp4"
    burn_captions_news_layout(str(broll_assembled), str(SRT_PATH), str(captioned), margin_v=250)

    final_video = captioned if captioned.exists() else broll_assembled

    # 6. Normalize audio
    print("\n6️⃣ Normalizing audio...")
    normalized = REELS_DIR / f"reel-{SLUG}-final.mp4"
    normalize_audio_social(str(final_video), str(normalized))

    # Check result
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(normalized)],
        capture_output=True, text=True, timeout=10
    )
    dur = float(probe.stdout.strip()) if probe.stdout.strip() else 0
    size_mb = normalized.stat().st_size / (1024 * 1024)

    print(f"\n✅ Done! Final reel: {normalized}")
    print(f"   Duration: {dur:.1f}s | Size: {size_mb:.1f}MB")
    print(f"   Resolution: 1080x1920 (9:16 portrait)")


if __name__ == "__main__":
    main()
