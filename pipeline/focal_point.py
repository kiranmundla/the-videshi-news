#!/usr/bin/env python3
"""
Focal-point detection for article hero images.

Uses OpenCV Haar cascades (face → profile → upper body) then falls back
to an edge-saliency heuristic.  Returns (focal_x, focal_y) in [0-1].

Zero external cost — OpenCV + Pillow are already installed.
"""

import cv2
import numpy as np
from PIL import Image
import io, sys

# ── cascades (loaded lazily, cached) ──────────────────────────────
_CASCADES = {}

def _cascade(name: str):
    if name not in _CASCADES:
        path = cv2.data.haarcascades + name
        _CASCADES[name] = cv2.CascadeClassifier(path)
    return _CASCADES[name]


def compute_focal_point(img_bytes: bytes) -> tuple[float, float]:
    """
    Analyze image bytes and return the best crop focal point.
    Returns (fx, fy) as floats in 0.0–1.0.
    Default / error fallback is (0.5, 0.5).
    """
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return 0.5, 0.5

        h, w = img.shape[:2]

        # Resize for faster detection (keep aspect, max 800px on long side)
        scale = 1.0
        if max(h, w) > 800:
            scale = 800 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sh, sw = gray.shape[:2]

        # ── Stage 1: frontal face ─────────────────────────────────
        faces = _cascade("haarcascade_frontalface_default.xml").detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(int(sw * 0.04), int(sh * 0.04))
        )

        # ── Stage 2: profile face ─────────────────────────────────
        if len(faces) == 0:
            faces = _cascade("haarcascade_profileface.xml").detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(int(sw * 0.04), int(sh * 0.04))
            )

        if len(faces) > 0:
            # bounding box of ALL detected faces
            x_min = min(int(f[0]) for f in faces)
            y_min = min(int(f[1]) for f in faces)
            x_max = max(int(f[0] + f[2]) for f in faces)
            y_max = max(int(f[1] + f[3]) for f in faces)
            fx = round(((x_min + x_max) / 2.0) / sw, 3)
            fy = round(((y_min + y_max) / 2.0) / sh, 3)
            return fx, fy

        # ── Stage 3: upper body ───────────────────────────────────
        bodies = _cascade("haarcascade_upperbody.xml").detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(int(sw * 0.08), int(sh * 0.08))
        )
        if len(bodies) > 0:
            bx, by, bw, bh = bodies[0]
            fx = round((bx + bw / 2) / sw, 3)
            fy = round((by + bh / 3) / sh, 3)   # bias up — face in upper third
            return fx, fy

        # ── Stage 4: edge-saliency heuristic ──────────────────────
        edges = cv2.Canny(gray, 50, 150)
        y_coords, x_coords = np.where(edges > 0)
        if len(x_coords) > 20:
            # centre-biased weighted mean
            wx = 1.0 - 0.3 * np.abs(x_coords / sw - 0.5)
            wy = 1.0 - 0.3 * np.abs(y_coords / sh - 0.5)
            fx = round(float(np.average(x_coords / sw, weights=wx)), 3)
            fy = round(float(np.average(y_coords / sh, weights=wy)), 3)
            return fx, fy

        return 0.5, 0.5

    except Exception as e:
        print(f"    ⚠ focal_point error: {e}", file=sys.stderr)
        return 0.5, 0.5


def image_dimensions(img_bytes: bytes) -> tuple[int, int]:
    """Return (width, height) from raw bytes."""
    try:
        pil = Image.open(io.BytesIO(img_bytes))
        return pil.width, pil.height
    except Exception:
        return 0, 0


# ── CLI smoke test ────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python focal_point.py <image_path>")
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    fx, fy = compute_focal_point(data)
    w, h = image_dimensions(data)
    print(f"Focal point: ({fx}, {fy})  Dimensions: {w}×{h}")
