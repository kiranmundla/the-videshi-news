"""Regression: the bare name "Pink Line" must never resolve to
Chicago's CTA Pink Line (Q3112661).

History: the registry auto-resolved "Pink Line" via
wikidata-sitelinks from a PUNE Metro story's context (its own
notes recorded "rapid transit line in Chicago, Illinois"). The
resolved item's depicts files — a 1924 Chicago Tribune photo of
the Berwyn "L" extension and Washington Junction — then passed
identity-by-construction and illustrated the Pune article
(2026-11-03) and, after the Nov 3 instance cleanup never touched
the registry entry, the Bengaluru Pink Line article
(2026-11-14). The entry is now de-resolved (fail closed) with
the Chicago files blocklisted, until per-city entries with
context_hints exist.

Also covers the enrich-articles provenance gap closed the same
day: placements sourced through enrich-articles Step 0 now reach
the shared provenance ledger under their own producer name.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import entity_resolve as ER  # noqa: E402

FAILS = []


def check(label, cond):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


# ── the registry entry itself ────────────────────────────────
entries = ER.load_registry()["entities"]
pink = [e for e in entries if e.get("name") == "Pink Line"]
check("exactly one 'Pink Line' registry entry", len(pink) == 1)
pink = pink[0] if pink else {}
check("'Pink Line' carries NO wikidata qid (fail closed)",
      not pink.get("wikidata_qid"))
check("'Pink Line' carries NO p18 file", not pink.get("p18_file"))
for f in ("Celebrate Extension of L to Berwyn, 1924.jpg",
          "Washington Junction.jpg",
          "Pink Line at State and Lake.jpg"):
    check(f"blocklisted: {f}", f in (pink.get("blocked_files")
                                     or []))

# ── resolution from Indian-story contexts ────────────────────
for city in ("Bengaluru", "Pune", "Delhi"):
    r = ER.resolve("Pink Line",
                   f"{city} Metro Pink Line opens to passengers "
                   f"in {city}, Karnataka commuters welcomed "
                   "with roses")
    check(f"resolve('Pink Line', {city} context) has no qid",
          r is not None and not r.get("qid"))
    check(f"resolve('Pink Line', {city} context) has no p18",
          r is not None and not r.get("p18_file"))

# ── the blocklist helper recognises every surface form ──────
check("entry_blocks: File: title form",
      ER.entry_blocks(pink,
                      "File:Celebrate Extension of L to Berwyn, "
                      "1924.jpg"))
check("entry_blocks: original URL form",
      ER.entry_blocks(pink,
                      "https://upload.wikimedia.org/wikipedia/"
                      "commons/9/9d/Washington_Junction.jpg"))

# ── provenance: enrich-articles placements are ledgered ─────
import article_picture_pass as app  # noqa: E402

with tempfile.TemporaryDirectory() as td:
    ledger_file = os.path.join(td, "ledger.jsonl")
    os.environ["IMAGE_LEDGER_PATH"] = ledger_file
    cand = {"entity": "Pink Line", "title": "File:Example.jpg",
            "file_url": "https://example.invalid/x.jpg",
            "route": "identity: depicts (P180)",
            "source_page": "https://commons.wikimedia.org/wiki/"
                           "File:Example.jpg",
            "original_file_url": "https://example.invalid/x.jpg",
            "license": "Public domain",
            "attribution": "Example",
            "verified_how": "test fixture"}
    app._ledger_inlines({"id": "test-id", "slug": "test-slug"},
                        [cand], producer="enrich-articles")
    rows = [json.loads(l) for l in open(ledger_file)]
    check("ledger row written for enrich-articles placement",
          len(rows) == 1)
    check("ledger row carries the enrich-articles producer",
          rows and rows[0].get("producer") == "enrich-articles")
    check("ledger row carries the article identity",
          rows and rows[0].get("article_id") == "test-id"
          and rows[0].get("slug") == "test-slug")
    del os.environ["IMAGE_LEDGER_PATH"]

print()
if FAILS:
    print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
    sys.exit(1)
print("ALL CHECKS PASSED")
