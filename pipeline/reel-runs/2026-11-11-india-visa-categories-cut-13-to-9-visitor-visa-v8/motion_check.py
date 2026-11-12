"""Motion-smoothness check for the v8 proof MP4 (not a gate).

Extracts EVERY frame across 2s of the news scene's zoom
(t=5.0..7.0, a full-bleed cover scene) and phase-correlates
consecutive frames in a fixed content window. Under ffmpeg
zoompan the crop window advances in whole pixels, so the
per-frame shift series staircases: runs of ~0.00px punctuated
by ~1.00px jumps. Under the v8 per-frame fractional render
the shifts should be small, near-uniform, and smoothly
varying (the eased zoom's derivative changes slowly).

Also samples every 0.25s across the whole news scene
(t=4.25..9.75) as a coarse cross-check.
"""
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np

RUN = Path(__file__).parent
MP4 = RUN / "india-visa-categories-cut-13-to-9-visitor-visa.mp4"
WORK = RUN / "motion-frames"
WORK.mkdir(exist_ok=True)

# fixed content window (photo area, away from text/chrome)
WIN = (slice(500, 1100), slice(120, 960))


def grab(t0, t1, fps, tag):
    out = WORK / f"{tag}-%03d.png"
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t0), "-to", str(t1),
         "-i", str(MP4), "-vf", f"fps={fps}", str(out)],
        capture_output=True, check=True)
    return sorted(WORK.glob(f"{tag}-*.png"))


def shifts(frames):
    prev = None
    series = []
    for f in frames:
        img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
        win = img[WIN].astype(np.float32)
        if prev is not None:
            (dx, dy), _resp = cv2.phaseCorrelate(prev, win)
            series.append((round(float(dx), 3),
                           round(float(dy), 3)))
        prev = win
    return series


fine = shifts(grab(5.0, 7.0, 30, "fine"))
mags = [abs(dx) + abs(dy) for dx, dy in fine]
coarse = shifts(grab(4.25, 9.75, 4, "coarse"))
result = {
    "window_frames": len(fine) + 1,
    "per_frame_shifts_px": fine,
    "shift_magnitude_min": round(min(mags), 3),
    "shift_magnitude_max": round(max(mags), 3),
    "shift_magnitude_mean": round(float(np.mean(mags)), 3),
    "shift_magnitude_std": round(float(np.std(mags)), 3),
    "zero_shift_frames": sum(1 for m in mags if m < 0.01),
    "jumps_over_0.5px": sum(1 for m in mags if m > 0.5),
    "coarse_0.25s_shifts_px": coarse,
}
print(json.dumps(result, indent=2))
(RUN / "motion-check.json").write_text(json.dumps(result,
                                                  indent=2))
