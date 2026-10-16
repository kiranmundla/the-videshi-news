#!/usr/bin/env python3
"""
reel_frame_qa.py — Phase 1 post-render frame QA for The Videshi reels.

Real, computed QA on the rendered MP4 — the replacement for the old
system's fabricated QA state (research/reel-quality-strategy-2026-10-12
.md §1.3: `register_reel()` hardcoded qa_passed=True and qa_score=8
without measuring anything). Here, qa_passed and qa_score are COMPUTED
from pixel-level checks on the actual video, stored per-check in the
report. A failure holds the reel with the failing check named.

Checks (per beat frame, extracted at each beat's midpoint):
  (a) SAFE-ZONE / EDGE-OVERFLOW — text glyphs are detected in the
      rendered frame itself (near-pure white or brand-gold cores with
      the renderer's near-black stroke adjacent — a signature photo
      content does not produce). Any glyph-sized cluster inside the
      forbidden bands (x<48, x>952, y<118, y>1602 — outside the design
      safe zone plus stroke bleed) FAILS the reel. This is the D1
      (edge-cropped text) check, in pixels.
  (b) FACE OVERLAP — the face is re-detected in the rendered frame
      with cv2 (fallback: the manifest face box mapped through the
      Ken Burns zoom). Detected text pixels inside the face box FAIL.
  (c) LEGIBILITY CONTRAST — median luminance of detected text pixels
      vs the background ring around the expected text region, per
      beat. Δ < 30 fails; Δ < 50 loses score.
  (d) FULL-RES PHOTO — the source photo file is opened and MEASURED
      (the manifest's numbers are never trusted): dimensions must
      meet the renderer's floor and match the manifest.
  (+) TECHNICAL — ffprobe: 1080x1920, ~35 s, audio stream present.

Score (computed, /10): edge 3.0 + face 2.0 + contrast 3.0 x
(beats passing / beats) + photo 1.0 + technical 1.0. Hard-check
failure zeroes its component. qa_passed = all hard checks pass AND
score >= 7.0. Nothing here is a constant; identical inputs recompute
identical outputs because every input is measured from the artifact.

Usage:
  python3 -u reel_frame_qa.py --video reel.mp4 \
      --manifest render-manifest.json [--outdir qa/] [--out qa.json]
Exit codes: 0 pass · 1 QA fail (reel held) · 4 input error.
"""
import argparse, json, subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reel_renderer import (W, H, TOTAL, MIN_PHOTO_W, MIN_PHOTO_H,
                           zoom_at, bg_to_out_x, bg_to_out_y)

# Forbidden bands for glyph pixels: design safe zone is x in [70,930],
# y in [140,1580]; glyph stroke (~9px) + shadow (~3px) may bleed a few
# px past the measured advance box. Anything glyph-like beyond these
# bands is real overflow (the D1 signature).
EDGE_X0, EDGE_X1 = 48, 952
EDGE_Y0, EDGE_Y1 = 118, 1602
MIN_GLYPH_CLUSTER = 80          # px — smaller specks are detection noise
FACE_OVERLAP_TOL = 30           # text px tolerated inside the face box
CONTRAST_HARD = 30.0            # Δ luminance below this = illegible, fail
CONTRAST_PASS = 50.0
PASS_SCORE = 7.0


# ── Pixel helpers ───────────────────────────────────────────────────────────
def luminance(arr):
    return (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1]
            + 0.0722 * arr[..., 2])


def detect_text_mask(frame_rgb):
    """Glyph mask: near-pure white or brand-gold cores whose pixels sit
    within ~4px of the renderer's near-black stroke color. Returns a
    boolean array (H, W)."""
    import cv2
    arr = frame_rgb.astype(np.int16)
    lum = luminance(frame_rgb.astype(np.float32))
    white_core = (arr[..., 0] > 235) & (arr[..., 1] > 235) \
        & (arr[..., 2] > 235)
    gold_core = (np.abs(arr[..., 0] - 212) < 40) \
        & (np.abs(arr[..., 1] - 168) < 40) & (arr[..., 2] < 115) \
        & (arr[..., 0] > arr[..., 2] + 60)
    core = white_core | gold_core
    stroke = (arr[..., 0] <= 30) & (arr[..., 1] <= 34) \
        & (arr[..., 2] <= 40) & (lum < 45)
    near_stroke = cv2.dilate(stroke.astype(np.uint8),
                             np.ones((9, 9), np.uint8)) > 0
    return core & near_stroke


def bg_plate(bg_path, t):
    """The renderer's text-free background plate, warped into frame
    coords at time t (same Ken Burns mapping as the overlays)."""
    bg = Image.open(bg_path).convert("RGB")
    z = zoom_at(t, TOTAL)
    zw, zh = round(W * z), round(H * z)
    big = bg.resize((zw, zh), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(big, (round(-0.5 * W * (z - 1)),
                       round(-0.3 * H * (z - 1))))
    return np.array(canvas)


def expected_mask(overlay_path, t):
    """Map a scene overlay (background coords) into frame coords at
    time t through the Ken Burns zoom. Returns boolean array."""
    ov = Image.open(overlay_path).convert("RGBA")
    alpha = np.array(ov.split()[3])
    z = zoom_at(t, TOTAL)
    zw, zh = round(W * z), round(H * z)
    big = Image.fromarray(alpha).resize((zw, zh), Image.NEAREST)
    canvas = Image.new("L", (W, H), 0)
    canvas.paste(big, (round(-0.5 * W * (z - 1)),
                       round(-0.3 * H * (z - 1))))
    return np.array(canvas) > 40


def clusters_in_zones(mask):
    """Connected components of `mask` restricted to forbidden bands.
    Returns (offending_px, n_clusters, largest_cluster)."""
    import cv2
    zone = np.zeros_like(mask, dtype=bool)
    zone[:, :EDGE_X0] = True
    zone[:, EDGE_X1:] = True
    zone[:EDGE_Y0, :] = True
    zone[EDGE_Y1:, :] = True
    bad = (mask & zone).astype(np.uint8)
    n, _, stats, _ = cv2.connectedComponentsWithStats(bad, 8)
    sizes = [int(stats[i, cv2.CC_STAT_AREA]) for i in range(1, n)
             if stats[i, cv2.CC_STAT_AREA] >= MIN_GLYPH_CLUSTER]
    return int(bad.sum()), len(sizes), (max(sizes) if sizes else 0)


def detect_face_in_frame(frame_rgb):
    """Re-detect the face in the rendered frame. Returns box or None.

    Uses the SAME YuNet detector as the renderer (shared helper), so
    QA measures overlap against the same face the layout protected —
    and inherits YuNet's precision on architecture/textures, where
    Haar false-positives. YuNet available but no face found -> None
    (the caller falls back to the manifest-mapped box); Haar is
    consulted only when YuNet itself is unavailable, mirroring the
    renderer's fallback."""
    from reel_renderer import yunet_faces
    faces = yunet_faces(frame_rgb)
    if faces is not None:
        if not faces:
            return None, "manifest-mapped"
        fx, fy, fw, fh, score = max(faces, key=lambda f: f[2] * f[3])
        return (int(fx), int(fy), int(fw), int(fh)), \
            f"frame-yunet (score {score:.2f})"
    import cv2
    gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape[:2]
    min_size = (int(w * 0.04), int(h * 0.04))
    for name in ("haarcascade_frontalface_default.xml",
                 "haarcascade_profileface.xml"):
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + name)
        faces = cascade.detectMultiScale(gray, 1.1, 5, minSize=min_size)
        if len(faces) > 0:
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            return (int(fx), int(fy), int(fw), int(fh)), \
                f"frame-haar:{name} (yunet unavailable)"
    return None, "manifest-mapped"


def extract_frame(video, t, out_png):
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i",
         str(video), "-frames:v", "1", str(out_png)],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"frame extract failed at {t}s: "
                           f"{r.stderr[-300:]}")


def ffprobe(video):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(video)], capture_output=True, text=True)
    return json.loads(r.stdout)


# ── QA entry point ──────────────────────────────────────────────────────────
def run_qa(video, manifest_path, outdir):
    import cv2  # noqa: F401  (hard dep of the pixel checks)
    video = Path(video)
    manifest = json.loads(Path(manifest_path).read_text())
    outdir = Path(outdir)
    frames_dir = outdir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = Path(manifest_path).resolve().parent

    checks = {}

    # (+) Technical.
    probe = ffprobe(video)
    vstreams = [s for s in probe["streams"] if s["codec_type"] == "video"]
    astreams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    dur = float(probe["format"]["duration"])
    tech_ok = (len(vstreams) == 1 and vstreams[0]["width"] == W
               and vstreams[0]["height"] == H
               and abs(dur - TOTAL) <= 2.0 and len(astreams) >= 1)
    checks["technical"] = {
        "pass": bool(tech_ok),
        "width": vstreams[0]["width"] if vstreams else None,
        "height": vstreams[0]["height"] if vstreams else None,
        "duration_s": round(dur, 2), "audio_streams": len(astreams)}

    # (d) Full-res photo — measured from the file, never the manifest.
    photo = manifest["photo"]
    photo_path = Path(photo["local_path"])
    measured = None
    sharpness = None
    if photo_path.exists():
        pim = Image.open(photo_path)
        measured = [pim.width, pim.height]
        gray = cv2.cvtColor(np.array(pim.convert("RGB")),
                            cv2.COLOR_RGB2GRAY)
        ch, cw = gray.shape[0] // 3, gray.shape[1] // 3
        center = gray[ch:2 * ch, cw:2 * cw]
        sharpness = float(cv2.Laplacian(center, cv2.CV_64F).var())
    photo_ok = (measured is not None
                and measured[0] >= MIN_PHOTO_W
                and measured[1] >= MIN_PHOTO_H
                and measured == [photo["width"], photo["height"]])
    checks["photo"] = {
        "pass": bool(photo_ok), "measured_dims": measured,
        "manifest_dims": [photo["width"], photo["height"]],
        "floor": [MIN_PHOTO_W, MIN_PHOTO_H],
        "center_sharpness_laplacian_var": (
            round(sharpness, 1) if sharpness is not None else None),
        "url": photo.get("url")}

    # Per-beat pixel checks.
    beats = []
    face_bg = manifest["face"]["box_bg"]
    # The manifest box is a real face only when a detector found one.
    # A focal-heuristic/static anchor box is NOT a face (2026-10-16):
    # falling back to it made QA fail faceless reels for "overlapping"
    # a person who isn't there. Older manifests predate has_face, so
    # derive it from the detection method.
    _face_info = manifest.get("face", {})
    manifest_has_face = _face_info.get(
        "has_face",
        str(_face_info.get("method", "")).startswith(("yunet", "haar")))
    for key, sc in manifest["scenes"].items():
        t = sc["start"] + sc["duration"] / 2.0
        frame_png = frames_dir / f"frame-{key}.png"
        extract_frame(video, t, frame_png)
        frame = np.array(Image.open(frame_png).convert("RGB"))
        # Text = glyph-signature pixels that DIFFER from the text-free
        # background plate. Bright photo features inside a face (teeth,
        # eye whites next to dark pupils) mimic the glyph signature —
        # the plate cancels them; only painted text survives.
        plate = bg_plate(manifest_dir / "background.jpg", t)
        changed = np.abs(luminance(frame.astype(np.float32))
                         - luminance(plate.astype(np.float32))) > 25
        mask = detect_text_mask(frame) & changed
        exp = expected_mask(manifest_dir / f"overlay-{key}.png", t)

        # (a) edge / safe-zone.
        bad_px, n_clusters, largest = clusters_in_zones(mask)
        edge_ok = n_clusters == 0

        # (b) face overlap.
        fbox, fmethod = detect_face_in_frame(frame)
        if fbox is None and manifest_has_face:
            z = zoom_at(t, TOTAL)
            fx, fy, fw, fh = face_bg
            fbox = (round(bg_to_out_x(fx, z)), round(bg_to_out_y(fy, z)),
                    round(fw * z), round(fh * z))
        if fbox is None:
            # No face in the rendered frame and none in the manifest:
            # nothing to protect — the check passes by construction.
            fbox, fmethod = (0, 0, 0, 0), "no-face"
            overlap_px, face_ok = 0, True
        else:
            fx, fy, fw, fh = fbox
            face_region = np.zeros_like(mask)
            face_region[max(fy, 0):fy + fh, max(fx, 0):fx + fw] = True
            # Count only pixels that can actually be text: glyph cores
            # (a) survive a 3x3 erosion — painted glyphs are fat, while
            # plate-misalignment filaments along high-frequency photo
            # detail (firework spark edges) are 1-2 px and vanish — and
            # (b) lie within the renderer's painted region dilated
            # 40 px: text cannot exist anywhere else, so pixels out
            # there are plate artifacts by construction. The pixels
            # counted are still measured from the rendered frame.
            mask_er = cv2.erode(mask.astype(np.uint8),
                                np.ones((3, 3), np.uint8)) > 0
            exp_zone = cv2.dilate(exp.astype(np.uint8),
                                  np.ones((81, 81), np.uint8)) > 0
            overlap_px = int((mask_er & exp_zone & face_region).sum())
            face_ok = overlap_px <= FACE_OVERLAP_TOL

        # (c) contrast: detected text within the expected region vs the
        # background ring around it.
        exp_d = cv2.dilate(exp.astype(np.uint8),
                           np.ones((37, 37), np.uint8)) > 0
        exp_core = cv2.erode(exp.astype(np.uint8),
                             np.ones((9, 9), np.uint8)) > 0
        text_px = mask & exp_d
        ring = exp_d & ~cv2.dilate(exp.astype(np.uint8),
                                   np.ones((15, 15), np.uint8)).astype(bool)
        lum = luminance(frame.astype(np.float32))
        if text_px.sum() >= 50 and ring.sum() >= 200:
            lt = float(np.median(lum[text_px]))
            lb = float(np.median(lum[ring]))
            delta = lt - lb
        else:
            lt = lb = delta = 0.0
        contrast_ok = delta >= CONTRAST_HARD
        contrast_full = delta >= CONTRAST_PASS

        beats.append({
            "beat": key, "t": t, "frame": str(frame_png),
            "text_px_detected": int(mask.sum()),
            "edge": {"pass": bool(edge_ok), "offending_px": bad_px,
                     "clusters": n_clusters, "largest_cluster": largest},
            "face": {"pass": bool(face_ok), "method": fmethod,
                     "box": [int(v) for v in fbox],
                     "overlap_px": overlap_px},
            "contrast": {"pass": bool(contrast_ok),
                         "full_marks": bool(contrast_full),
                         "text_luminance": round(lt, 1),
                         "bg_luminance": round(lb, 1),
                         "delta": round(delta, 1)},
        })

    edge_all = all(b["edge"]["pass"] for b in beats)
    face_all = all(b["face"]["pass"] for b in beats)
    contrast_frac = (sum(1 for b in beats if b["contrast"]["full_marks"])
                     / len(beats)) if beats else 0.0
    contrast_hard_ok = all(b["contrast"]["pass"] for b in beats)

    # Computed score — every point is earned by a measured check.
    score = 0.0
    score += 3.0 if edge_all else 0.0
    score += 2.0 if face_all else 0.0
    score += 3.0 * contrast_frac
    score += 1.0 if photo_ok else 0.0
    score += 1.0 if tech_ok else 0.0
    score = round(score, 2)

    qa_passed = bool(edge_all and face_all and contrast_hard_ok
                     and photo_ok and tech_ok and score >= PASS_SCORE)
    failing = []
    if not tech_ok:
        failing.append("technical")
    if not photo_ok:
        failing.append("photo_fullres")
    for b in beats:
        if not b["edge"]["pass"]:
            failing.append(f"edge_overflow:{b['beat']}")
        if not b["face"]["pass"]:
            failing.append(f"face_overlap:{b['beat']}")
        if not b["contrast"]["pass"]:
            failing.append(f"contrast:{b['beat']}")

    return {
        "qa": "reel_frame_qa.py",
        "video": str(video),
        "qa_passed": qa_passed,
        "qa_score": score,
        "pass_threshold": PASS_SCORE,
        "failing_checks": failing,
        "checks": checks,
        "beats": beats,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--video", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--outdir", default=None,
                    help="frames dir parent (default: alongside video)")
    ap.add_argument("--out", default=None, help="write report JSON here")
    args = ap.parse_args()

    if not Path(args.video).exists() or not Path(args.manifest).exists():
        print("🚫 video or manifest missing", file=sys.stderr)
        return 4
    outdir = Path(args.outdir) if args.outdir \
        else Path(args.video).resolve().parent / "qa"
    try:
        report = run_qa(args.video, args.manifest, outdir)
    except Exception as e:
        print(f"🚫 QA could not run: {e}", file=sys.stderr)
        return 4
    out_path = Path(args.out) if args.out else outdir / "qa-report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(f"frame QA: score {report['qa_score']}/10 · "
          f"{'PASS' if report['qa_passed'] else 'FAIL'}")
    for b in report["beats"]:
        print(f"  {b['beat']:9s} edge={'✓' if b['edge']['pass'] else '✗'} "
              f"face={'✓' if b['face']['pass'] else '✗'} "
              f"contrast Δ={b['contrast']['delta']}")
    if not report["qa_passed"]:
        print(f"🚫 HELD — failing: {', '.join(report['failing_checks'])}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
