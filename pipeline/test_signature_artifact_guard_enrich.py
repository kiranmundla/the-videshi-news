"""Regression test: signature/autograph artifact guard — enrich-articles.py
mirror copy.

The guard landed first in image_sourcer.py (commit 116e51a7c, covered by
test_signature_artifact_guard.py). enrich-articles.py carries a MIRRORED
copy of the Wikipedia relevance guards — its own fetch_wikipedia_image()
and is_relevant_image() — so a signature scan (e.g.
'Min_Woo_Lee_signature.jpg', the Min Woo Lee page's lead image) could
still be accepted as a hero through the enricher path. This test pins
the mirrored _is_signature_artifact() and its two wiring points:

- is_relevant_image() (the Commons/Openverse relevance gate — every
  search_wikimedia_commons() result flows through it)
- fetch_wikipedia_image() shares the same helper (checked here via the
  helper itself; the gate's placement mirrors image_sourcer.py)

Sibling file rather than an extension of test_signature_artifact_guard.py
so each test loads exactly one pipeline module.

Run: python3 test_signature_artifact_guard_enrich.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "enrich_articles", os.path.join(HERE, "enrich-articles.py"))
enr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enr)

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


is_sig = enr._is_signature_artifact

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

# ── End-to-end through the enricher's relevance gate ──
# is_relevant_image() accepts any result whose title contains a subject
# name part — both titles below contain 'Min'/'Woo'/'Lee', so without
# the guard BOTH would return True. Only the guard rejects the scan.
check("relevance gate rejects signature title despite name match",
      enr.is_relevant_image(
          {"title": "File:Min Woo Lee signature at Delhi Open.jpg",
           "source": "wikimedia"},
          "Min Woo Lee",
          "Min Woo Lee withdraws from Delhi event with back spasms") is False)
check("relevance gate still accepts a matching real photo",
      enr.is_relevant_image(
          {"title": "File:Min Woo Lee at Delhi Open 2024.jpg",
           "source": "wikimedia"},
          "Min Woo Lee",
          "Min Woo Lee withdraws from Delhi event with back spasms") is True)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
