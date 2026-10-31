#!/usr/bin/env python3
"""Tests for shadow_run.py — the image rebuild's divergence
runner (fixtures only: fetcher and both decision functions are
stubbed, so nothing touches Supabase, the network, or the
registry).

A. classify_hero — the four divergence categories, incl. the
   unkeyable-live-URL edge (re-hosted under a generated name).
B. run() end-to-end on fixtures: counts per category, the
   inline divergence line, --dry-run writes nothing, a real
   run appends to shadow-report-<date>.md (and appends again).
C. Importing shadow_run disables the resolver's registry
   cache-back for the process (a measurement run must never
   mutate entity_registry.json).

Run: python3 -u test_shadow_run.py
"""
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import shadow_run as sr

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def _shadow(decision, file_key=None, route=None, entity="Ent",
            reason="fixture reason"):
    return {"decision": decision, "file_key": file_key,
            "route": route, "entity": entity, "reason": reason,
            "url": None, "attempts": []}


# ── A. classify_hero ───────────────────────────────────────────
print("A. classify_hero categories")
check("both none -> agree",
      sr.classify_hero(False, None, _shadow("none")) == "agree")
check("same file key -> agree",
      sr.classify_hero(True, "a b.jpg",
                       _shadow("image", "a b.jpg")) == "agree")
check("shadow image, live none -> shadow-image-live-none",
      sr.classify_hero(False, None, _shadow("image", "a b.jpg"))
      == "shadow-image-live-none")
check("shadow none, live image -> shadow-none-live-image",
      sr.classify_hero(True, "a b.jpg", _shadow("none"))
      == "shadow-none-live-image")
check("different keys -> different-image",
      sr.classify_hero(True, "a b.jpg", _shadow("image", "c d.jpg"))
      == "different-image")
check("live image unkeyable (generated storage name) reads as "
      "different-image, never false agreement",
      sr.classify_hero(True, None, _shadow("image", "c d.jpg"))
      == "different-image")
check("live image unkeyable + shadow none -> "
      "shadow-none-live-image",
      sr.classify_hero(True, None, _shadow("none"))
      == "shadow-none-live-image")

# ── B. run() on fixtures ───────────────────────────────────────
print("B. run() end-to-end (stubbed fetch + decisions)")
ARTS = [
    {"slug": "agree-story", "headline": "H1",
     "image_url": "https://upload.wikimedia.org/wikipedia/"
                  "commons/a/ab/Example_Skyline.jpg",
     "body": "<p>x</p>"},
    {"slug": "shadow-only-story", "headline": "H2",
     "image_url": None, "body": "<p>x</p>"},
    {"slug": "live-only-story", "headline": "H3",
     "image_url": "https://upload.wikimedia.org/wikipedia/"
                  "commons/b/bc/Live_Only.jpg",
     "body": "<p>x</p>"},
    {"slug": "different-story", "headline": "H4",
     "image_url": "https://upload.wikimedia.org/wikipedia/"
                  "commons/c/cd/Live_File.jpg",
     "body": ('<p>x</p><figure><img src="https://upload.'
              'wikimedia.org/wikipedia/commons/d/de/'
              'Live_Inline.jpg"></figure>')},
]
DECISIONS = {
    "agree-story": _shadow("image", "example skyline.jpg",
                           "wikidata_p18"),
    "shadow-only-story": _shadow("image", "found file.jpg",
                                 "wikidata_depicts"),
    "live-only-story": _shadow("none", reason="no candidate"),
    "different-story": _shadow("image", "shadow file.jpg",
                               "wikidata_p18"),
}
INLINES = {
    "agree-story": [],
    "shadow-only-story": [],
    "live-only-story": [],
    "different-story": [{"file_key": "shadow inline.jpg"}],
}
NOW = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)
state = Path(tempfile.mkdtemp())

text, stats = sr.run(
    hours=4, dry_run=True, now=NOW, state=state,
    fetch=lambda h: ARTS,
    decide_fn=lambda a: DECISIONS[a["slug"]],
    inline_fn=lambda a, hero: {"inlines": INLINES[a["slug"]]})
check("counts: one of each hero category",
      stats["counts"] == {"agree": 1, "shadow-image-live-none": 1,
                          "shadow-none-live-image": 1,
                          "different-image": 1},
      f"got {stats['counts']}")
check("inline divergence counted once (different-story)",
      stats["inline_divergences"] == 1)
check("no errors", stats["errors"] == 0)
check("report names all four categories",
      all(s in text for s in ("agree: 1",
                              "shadow-image-live-none: 1",
                              "shadow-none-live-image: 1",
                              "different-image: 1")))
check("divergence line carries slug + live key + shadow "
      "decision/route/reason",
      any("different-story" in ln and "live file.jpg" in ln
          and "image/wikidata_p18" in ln and "fixture reason" in ln
          for ln in text.splitlines()))
check("dry-run writes nothing",
      not (state / "shadow-report-2026-10-31.md").exists())

text2, stats2 = sr.run(
    hours=4, dry_run=False, now=NOW, state=state,
    fetch=lambda h: ARTS,
    decide_fn=lambda a: DECISIONS[a["slug"]],
    inline_fn=lambda a, hero: {"inlines": INLINES[a["slug"]]})
report = state / "shadow-report-2026-10-31.md"
check("real run writes the dated report",
      report.exists() and "## Shadow run" in report.read_text())
sr.run(hours=4, dry_run=False, now=NOW, state=state,
       fetch=lambda h: ARTS,
       decide_fn=lambda a: DECISIONS[a["slug"]],
       inline_fn=lambda a, hero: {"inlines": INLINES[a["slug"]]})
check("second run appends, does not overwrite",
      report.read_text().count("## Shadow run") == 2)

# a deciding error is recorded per-article, never fatal
def _boom(a):
    raise RuntimeError("fixture boom")
text3, stats3 = sr.run(
    hours=4, dry_run=True, now=NOW, state=state,
    fetch=lambda h: ARTS[:1], decide_fn=_boom,
    inline_fn=lambda a, hero: {"inlines": []})
check("decision error counted + lined, run survives",
      stats3["errors"] == 1 and "fixture boom" in text3)

# ── C. cache-back disabled by import ───────────────────────────
print("C. registry cache-back disabled in this process")
check("er._cache_back is the no-op (returns False)",
      sr.er._cache_back("Anything",
                        {"qid": "Q1", "name": "Anything"}) is False)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
