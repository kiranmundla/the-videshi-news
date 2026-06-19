#!/usr/bin/env python3
"""
media_library_lookup — the fallback hook for article writers and the reel pipeline.

Fallback-priority contract (the CALLER enforces ordering):
    X / Threads / Instagram social card  OR  dynamic search   →  FIRST
    media_library (this helper)                                →  SECOND
    existing chain (Pexels generic, etc.)                      →  LAST

Usage:
    from media_library_lookup import find_media

    asset = find_media(subject="Narendra Modi", subject_type="person",
                       media_type="image", min_quality=50)
    if asset:
        url         = asset["url"]          # Supabase-hosted, never rots
        caption     = asset["caption"]      # ready to use as an article caption
        attribution = asset["attribution"]  # e.g. "Wikimedia Commons / PMO, GODL-India"

`find_media` prefers highest quality_score, then least-recently-used, and bumps
last_used/times_used (in both the JSON mirror and the Supabase table) when it
returns an asset. Pass bump_usage=False for a dry read.

Matching:
    - subject     : case-insensitive exact OR substring match on subject + tags
    - tags        : any-overlap match against the asset's tags
    - subject_type: 'person'|'place'|'thing'|'event'|'concept'
    - media_type  : 'image'|'video'
    - min_quality : floor on quality_score

NOTE for article photos: pass exclude_concept=True (default) so generic 'concept'
stock is NOT returned as an article photo — concept assets are reserved for
abstract reel b-roll. Reels that explicitly want b-roll can pass
exclude_concept=False.
"""

import time, json
import media_library_store as store


def _matches(asset, subject, tags, subject_type, media_type, min_quality, exclude_concept):
    if media_type and asset.get("media_type") != media_type:
        return False
    if subject_type and asset.get("subject_type") != subject_type:
        return False
    if exclude_concept and asset.get("subject_type") == "concept":
        return False
    if (asset.get("quality_score") or 0) < min_quality:
        return False

    asset_subject = (asset.get("subject") or "").lower()
    asset_tags = [str(t).lower() for t in (asset.get("tags") or [])]

    matched = False
    if subject:
        s = subject.lower().strip()
        if s == asset_subject or s in asset_subject or asset_subject in s:
            matched = True
        elif any(s in t or t in s for t in asset_tags):
            matched = True
    if tags:
        want = [str(t).lower() for t in tags]
        if any(w in asset_tags or any(w in at or at in w for at in asset_tags) for w in want):
            matched = True
    if not subject and not tags:
        matched = True  # type/quality-only query (e.g. any high-quality concept b-roll)
    return matched


def find_media(subject=None, tags=None, subject_type=None, media_type=None,
               min_quality=0, exclude_concept=True, bump_usage=True):
    """Return the best matching asset dict, or None."""
    candidates = [
        a for a in store.mirror_assets()
        if _matches(a, subject, tags, subject_type, media_type, min_quality, exclude_concept)
    ]
    if not candidates:
        return None

    # Highest quality first, then least-recently-used (None last_used = never used = preferred)
    def sort_key(a):
        lu = a.get("last_used") or ""
        return (-(a.get("quality_score") or 0), lu, a.get("times_used") or 0)

    candidates.sort(key=sort_key)
    best = candidates[0]

    if bump_usage:
        _bump(best)
    return best


def _bump(asset):
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    asset["last_used"] = now
    asset["times_used"] = (asset.get("times_used") or 0) + 1
    # mirror
    try:
        store.upsert_mirror(asset)
    except Exception:
        pass
    # table (best-effort)
    try:
        import requests
        requests.patch(
            f"{store.SUPABASE_URL}/rest/v1/media_library?id=eq.{asset['id']}",
            headers=store.sb_headers({"Content-Type": "application/json",
                                      "Prefer": "return=minimal"}),
            data=json.dumps({"last_used": now, "times_used": asset["times_used"]}),
            timeout=10)
    except Exception:
        pass


if __name__ == "__main__":
    import sys
    subj = sys.argv[1] if len(sys.argv) > 1 else None
    a = find_media(subject=subj, bump_usage=False)
    if a:
        print(json.dumps({k: a.get(k) for k in
              ("id", "media_type", "subject", "subject_type", "quality_score",
               "caption", "attribution", "license", "url")}, indent=2, ensure_ascii=False))
    else:
        print(f"No media_library match for subject={subj!r}")
