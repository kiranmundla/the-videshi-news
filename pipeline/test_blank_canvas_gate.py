"""Regression test: person-profile blank-canvas (logo placeholder) gate.

Real failure (2026-10-22): image_sourcer Source 3.8 accepted Khel Now's
site-logo placeholder as Anahat Singh's verified portrait — the player
page's <img> carried alt="Anahat Singh" but the file was a white canvas
with a small KN logo (1200x675, 8.7 KB). It passed every existing gate
(exact-name alt, page-about-person, >=800px, filename has no 'logo',
0 faces is not >=2). Measured calibration: logo dominant quantized
color share 0.984; verified portraits 0.05-0.11. Gate rejects >=0.80.

Run: python3 test_blank_canvas_gate.py  (exit 0 = all pass)
"""
import importlib.util
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "image_sourcer", os.path.join(HERE, "image_sourcer.py"))
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)

from PIL import Image, ImageDraw

fails = 0
total = 0


def check(name, cond, extra=""):
    global fails, total
    total += 1
    if cond:
        print(f"ok   {name}")
    else:
        fails += 1
        print(f"FAIL {name} {extra}")


def to_bytes(im):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=88)
    return buf.getvalue()


# Logo placeholder: white canvas, small dark logo mark in the centre
logo = Image.new("RGB", (1200, 675), (255, 255, 255))
d = ImageDraw.Draw(logo)
d.rectangle([520, 280, 680, 395], fill=(40, 40, 40))
check("white-canvas logo placeholder rejected",
      src._is_blank_canvas_image(to_bytes(logo)) is True)

# Photo-like: varied gradient + shapes (portrait-ish colour diversity)
photo = Image.new("RGB", (1200, 675))
px = photo.load()
for y in range(675):
    for x in range(1200):
        px[x, y] = ((x * 255) // 1200, (y * 255) // 675,
                    ((x + y) * 255) // 1875)
check("colour-varied photo accepted",
      src._is_blank_canvas_image(to_bytes(photo)) is False)

# Studio headshot on white: person block occupies the centre ~40%
shot = Image.new("RGB", (1200, 675), (250, 250, 250))
d = ImageDraw.Draw(shot)
d.ellipse([450, 120, 750, 480], fill=(198, 150, 110))
d.rectangle([400, 470, 800, 675], fill=(30, 40, 90))
check("white-background headshot accepted",
      src._is_blank_canvas_image(to_bytes(shot)) is False)

# Undecodable bytes: gate abstains (other gates decide)
check("garbage bytes not rejected by this gate",
      src._is_blank_canvas_image(b"not an image") is False)

# The real poisoned file, if a copy is still around from the review run
real = "/tmp/rev1022/hero_anahat.jpg"
if os.path.exists(real):
    with open(real, "rb") as f:
        check("actual Khel Now logo file rejected",
              src._is_blank_canvas_image(f.read()) is True)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
