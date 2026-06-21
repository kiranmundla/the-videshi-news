#!/usr/bin/env python3
"""
music_selector.py — mood-driven, deterministically-rotating music picker for
The Videshi reel pipeline.

Importable with no side effects. Main entry point:

    select_music(category, story_mood=None, target_variant="30s",
                 article_id=None, index_path=None) -> dict

Returns a dict:
    {
      "filename":   "<full track filename>",
      "path":       "<absolute path to the requested-variant file>",
      "family":     "<mood family / category>",
      "mood_tags":  [...],
      "duration_s": <int of the FULL track>,
      "license":    "CC0" | "CC-BY-4.0",
      "attribution":"" | "<required attribution string>",
    }

Selection logic
---------------
1. If `story_mood` is given and present in the index `story_mood_map`, walk the
   ordered preferred families and use the first family that has tracks.
2. Else, map the article `category` to a family via the `categories` block's
   `article_categories` (reverse lookup); if the category IS itself a family
   name, use it directly.
3. Else fall back to a safe default family ("breaking-news").
4. Within the chosen family, ROTATE deterministically:
       idx = hash(article_id) % len(candidates)
   so the same article always gets the same track (stable re-renders) while
   different articles vary. If article_id is None, pick at random.
5. Resolve the requested variant from the track's `variants`; fall back to the
   full file if the variant is missing.
"""
import json
import os
import hashlib
import random

_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_INDEX = os.path.join(_DIR, "music-index.json")
_SAFE_DEFAULT_FAMILY = "breaking-news"


def _load_index(index_path=None):
    path = index_path or _DEFAULT_INDEX
    with open(path) as f:
        return json.load(f)


def _tracks_in_family(index, family):
    return [t for t in index.get("tracks", []) if t.get("category") == family]


def _family_from_category(index, category):
    """Resolve an article category to a mood family.

    - If `category` is already a family name (a key in `categories`), use it.
    - Else reverse-look-up which family lists this category in its
      `article_categories`.
    - Else None.
    """
    if not category:
        return None
    cats = index.get("categories", {})
    if category in cats:
        return category
    cl = str(category).strip().lower()
    for family, meta in cats.items():
        for ac in meta.get("article_categories", []):
            if ac.strip().lower() == cl:
                return family
    # loose contains-match as a last resort (e.g. "markets" in "markets & finance")
    for family, meta in cats.items():
        for ac in meta.get("article_categories", []):
            a = ac.strip().lower()
            if a and (a in cl or cl in a):
                return family
    return None


def _resolve_family(index, category, story_mood):
    # 1) story mood preference order
    if story_mood:
        smap = index.get("story_mood_map", {})
        prefs = smap.get(str(story_mood).strip().lower())
        if prefs:
            for fam in prefs:
                if _tracks_in_family(index, fam):
                    return fam, "story_mood"
    # 2) category -> family
    fam = _family_from_category(index, category)
    if fam and _tracks_in_family(index, fam):
        return fam, "category"
    # 3) safe default
    if _tracks_in_family(index, _SAFE_DEFAULT_FAMILY):
        return _SAFE_DEFAULT_FAMILY, "default"
    # 4) absolute last resort: first family that has any track
    for t in index.get("tracks", []):
        return t.get("category"), "fallback-any"
    return None, "none"


def _stable_index(article_id, n):
    if n <= 0:
        return 0
    if article_id is None:
        return random.randrange(n)
    h = hashlib.sha256(str(article_id).encode("utf-8")).hexdigest()
    return int(h, 16) % n


def _variant_filename(track, target_variant):
    variants = track.get("variants", {})
    if target_variant in variants:
        return variants[target_variant]
    if target_variant == "full":
        return track["filename"]
    # graceful fallbacks: prefer 30s, then 15s, then full file
    for v in ("30s", "15s"):
        if v in variants:
            return variants[v]
    return track["filename"]


def select_music(category, story_mood=None, target_variant="30s",
                 article_id=None, index_path=None):
    """Pick a music track. See module docstring for full semantics."""
    index = _load_index(index_path)
    family, _reason = _resolve_family(index, category, story_mood)
    candidates = _tracks_in_family(index, family) if family else []
    if not candidates:
        # final safety net — any track at all
        candidates = list(index.get("tracks", []))
        family = candidates[0].get("category") if candidates else None
    if not candidates:
        raise RuntimeError("music-index has no tracks")

    # deterministic rotation, sorted by filename for a stable ordering
    candidates = sorted(candidates, key=lambda t: t["filename"])
    pick = candidates[_stable_index(article_id, len(candidates))]

    fname = _variant_filename(pick, target_variant)
    path = os.path.join(os.path.dirname(index_path or _DEFAULT_INDEX), fname)

    return {
        "filename": pick["filename"],
        "path": os.path.abspath(path),
        "family": family,
        "mood_tags": pick.get("mood_tags", []),
        "duration_s": pick.get("duration_s"),
        "license": pick.get("license", "CC0"),
        "attribution": pick.get("attribution", "") if pick.get("license") == "CC-BY-4.0" else "",
    }


if __name__ == "__main__":
    # Smoke test: print selections across moods/categories and assert files exist.
    print("=== music_selector smoke test ===")
    combos = [
        # (category, story_mood, variant, article_id)
        ("technology", "tech", "30s", "spacex-ipo-001"),
        ("technology", "triumphant", "30s", "spacex-ipo-001"),
        ("technology", "triumphant", "15s", "another-article-xyz"),
        ("news", "somber", "30s", "immigration-tragedy-77"),
        ("news", "tense", "30s", "border-standoff-12"),
        ("news", "neutral-news", "30s", "policy-update-5"),
        ("entertainment", "cultural", "30s", "diwali-9"),
        ("sports", "celebratory", "30s", "cricket-win-3"),
        ("travel", "chill", "30s", "goa-trip-1"),
        ("markets & finance", None, "30s", "rupee-44"),   # category-only path
        ("totally-unknown-cat", None, "30s", "x-1"),        # default path
        ("technology", "tech", "30s", None),                # random rotation
    ]
    missing = 0
    seen_rotation = {}
    for cat, mood, var, aid in combos:
        sel = select_music(cat, story_mood=mood, target_variant=var, article_id=aid)
        ok = os.path.exists(sel["path"])
        if not ok:
            missing += 1
        lic = sel["license"]
        print(f"[{cat:20s} | mood={str(mood):12s} | {var}] -> {sel['family']:16s} "
              f"{os.path.basename(sel['path']):48s} {lic:9s} {'OK' if ok else 'MISSING!!'}")
        seen_rotation.setdefault((cat, mood), set()).add(sel["filename"])

    # Determinism check: same article+mood always returns same file
    a = select_music("technology", story_mood="triumphant", article_id="spacex-ipo-001")
    b = select_music("technology", story_mood="triumphant", article_id="spacex-ipo-001")
    assert a["filename"] == b["filename"], "determinism FAILED"
    print("\ndeterminism check: PASS (same article+mood -> same track)")

    # Variety check: different articles in same family should not all collapse to one
    fams = {}
    for i in range(12):
        s = select_music("technology", story_mood="triumphant", article_id=f"art-{i}")
        fams.setdefault(s["filename"], 0)
        fams[s["filename"]] += 1
    print(f"variety check: {len(fams)} distinct tracks across 12 articles in 'anthemic-triumph'")

    assert missing == 0, f"{missing} selections pointed at missing files"
    print(f"\nALL SELECTIONS RESOLVE TO ON-DISK FILES ✓ (0 missing)")
