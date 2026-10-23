"""Regression test: signature/autograph artifact guard for Wikipedia/Commons.

Real failure (2026-10-23): for the article 'min-woo-lee-withdraws-delhi-
stomach-illness-back-spasms', image_sourcer's wikipedia_headline_guard
produced 'Min_Woo_Lee_signature.jpg' from Wikimedia Commons — a scan of
the golfer's autograph (marker strokes on white), not a photograph of
him. It passed the filename-vs-entity cross-check (the name matches),
the >=800px floor, and the relevance guards. A human reviewer rejected
it visually; a write-enabled automated run could have published it.

Guard: _is_signature_artifact() — whole-token matching on the filename /
Commons title (plus description tokens when provided). Wired into
fetch_wikipedia_image() (covers the 'wikipedia' source and the
wikipedia_headline_guard) and commons_relevance_ok() (Commons search).

Run: python3 test_signature_artifact_guard.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "image_sourcer", os.path.join(HERE, "image_sourcer.py"))
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)

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


is_sig = src._is_signature_artifact

# ── The real failure ──
check("Min_Woo_Lee_signature.jpg rejected",
      is_sig("Min_Woo_Lee_signature.jpg") is True)
check("full upload.wikimedia.org signature URL rejected",
      is_sig("https://upload.wikimedia.org/wikipedia/commons/1/1a/"
             "Min_Woo_Lee_signature.jpg") is True)
check("camelCase signature filename rejected",
      is_sig("MinWooLeeSignature.jpg") is True)

# ── Other signature/autograph forms ──
check("'X signature.svg' rejected",
      is_sig("X signature.svg") is True)
check("autograph filename rejected",
      is_sig("Sachin_Tendulkar_autograph.png") is True)
check("signed-item filename rejected",
      is_sig("Lee_signed_ball.jpg") is True)
check("signature in description rejected",
      is_sig("Portrait_file.jpg", "Signature of Min Woo Lee") is True)
check("autograph in description rejected",
      is_sig("Portrait_file.jpg", "Autograph of the golfer, 2023") is True)

# ── Legitimate photos survive ──
check("normal portrait filename accepted",
      is_sig("Min_Woo_Lee_2024.jpg") is False)
check("'Design...' filename accepted (design != signed)",
      is_sig("Design_Museum_exterior.jpg") is False)
check("'Signal...' filename accepted (signal != signed)",
      is_sig("Signal_Hill_sunset.jpg") is False)
check("'consigned' filename accepted (whole-token matching)",
      is_sig("Consigned_artwork_opening.jpg") is False)
check("'unsigned' filename accepted",
      is_sig("Unsigned_editorial_photo.jpg") is False)
check("person description accepted",
      is_sig("Portrait_file.jpg", "Australian professional golfer") is False)
check("'signed' in narrative description accepted (ceremony photo)",
      is_sig("Signing_ceremony.jpg",
             "The president signed the bill into law") is False)

# ── End-to-end through the Commons relevance gate ──
# Titles carry a distinctive headline word ('Delhi') so the pre-existing
# relevance logic would ACCEPT both — verified against the pre-fix code:
# the signature title returned True there. Only the new guard rejects it.
# (A bare 'File:Min Woo Lee 2024.jpg' is rejected by the old gate too:
# every name token is <4 letters, so no distinctive word matches.)
check("Commons relevance rejects signature title despite full match",
      src.commons_relevance_ok(
          "File:Min Woo Lee signature at Delhi Open.jpg",
          "Min Woo Lee withdraws from Delhi event with back spasms") is False)
check("Commons relevance still accepts a matching real photo",
      src.commons_relevance_ok(
          "File:Min Woo Lee at Delhi Open 2024.jpg",
          "Min Woo Lee withdraws from Delhi event with back spasms") is True)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
