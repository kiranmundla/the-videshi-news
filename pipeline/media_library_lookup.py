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


# Words that must never, on their own, qualify an asset as a relevance match.
# These brushed loose substring matches before (e.g. "a" inside "india",
# "indian" inside the tag "india") and let high-quality off-topic assets
# hijack scenes. Tokens shorter than _MIN_TOKEN_LEN are also dropped.
_STOPWORDS = {
    "a", "an", "the", "of", "at", "in", "on", "to", "for", "and", "or", "with",
    "from", "by", "as", "is", "are", "was", "were", "be", "this", "that",
    "these", "those", "it", "its", "his", "her", "their", "they", "up", "out",
    "close", "shot", "view", "wide", "angle", "closeup", "scene", "background",
    "people", "person", "group", "crowd", "celebrating", "speaking", "holding",
    "standing", "sitting", "walking", "smiling", "during", "over", "near",
    # generic geo/identity words that are too broad to carry relevance alone
    "india", "indian", "indians", "american", "americans", "us", "usa",
    "city", "street", "building", "skyline", "flag", "public", "event",
}
_MIN_TOKEN_LEN = 4


def _tokens(text):
    """Lowercased, meaningful word tokens: drops stopwords and short fragments."""
    import re
    out = []
    for w in re.split(r"[^a-z0-9]+", (text or "").lower()):
        if len(w) >= _MIN_TOKEN_LEN and w not in _STOPWORDS:
            out.append(w)
    return out


def _matches(asset, subject, tags, subject_type, media_type, min_quality, exclude_concept):
    if media_type and asset.get("media_type") != media_type:
        return False
    if subject_type and asset.get("subject_type") != subject_type:
        return False
    if (asset.get("quality_score") or 0) < min_quality:
        return False

    a_type = (asset.get("subject_type") or "").lower().strip()
    # Unlabeled assets are treated as the STRICTEST tier (person/name-only), so a
    # mis-/un-tagged asset can never slip through as generic filler.
    if not a_type:
        a_type = "person"

    if exclude_concept and a_type == "concept":
        return False

    asset_subject = (asset.get("subject") or "").lower().strip()
    asset_subject_tokens = set(_tokens(asset_subject))
    asset_tag_set = set()
    for t in (asset.get("tags") or []):
        t = str(t).lower().strip()
        if t:
            asset_tag_set.add(t)
            asset_tag_set.update(_tokens(t))

    # Build the set of query name-tokens (from `subject`) and query tag-tokens.
    q_subject = (subject or "").lower().strip()
    q_subject_tokens = set(_tokens(q_subject))
    q_tag_tokens = set()
    for t in (tags or []):
        q_tag_tokens.update(_tokens(str(t)))

    # ── PERSON / ORG: EXACT IDENTITY ONLY. Tags are IGNORED entirely — a person
    # photo may be used only when the article actually names that person. This is
    # the hard safety gate (no "Modi via #politics"). ────────────────────────────
    if a_type in ("person", "org", "organization"):
        if not q_subject:
            return False  # a tag-only query must never pull a person photo
        # Full-name equality / containment is the strongest signal.
        if q_subject == asset_subject:
            return True
        if asset_subject and len(asset_subject) >= _MIN_TOKEN_LEN and (
                asset_subject in q_subject or q_subject in asset_subject):
            return True
        # Distinctive-name match: the asset's LAST name token (surname / acronym,
        # len>=3) must appear as a whole token in the query, and the query must
        # look like a name (<=3 tokens). This lets "Modi" match "Narendra Modi"
        # while never matching "Nithya Raman".
        asset_name_tokens = [t for t in asset_subject.split() if len(t) >= 3]
        if asset_name_tokens and len(q_subject.split()) <= 3:
            distinctive = asset_name_tokens[-1]
            if distinctive in q_subject_tokens:
                return True
        return False

    # ── PLACE / EVENT: NAME MATCH. Looser than persons, but still name-anchored
    # (a place/event photo needs its name to appear), not generic-tag driven. ─────
    if a_type in ("place", "location", "event"):
        if q_subject_tokens and (q_subject_tokens & (asset_subject_tokens | asset_tag_set)):
            return True
        if q_tag_tokens and (q_tag_tokens & asset_subject_tokens):
            return True
        return False

    # ── THING / OBJECT (and anything else non-sensitive): TAG-TOKEN MATCH is
    # appropriate — generic B-roll (currency, cricket bat, passport, ballot box)
    # should match on tags/subject tokens. Whole-token only, no substring brush. ──
    # Short alphanumeric domain subjects (h1b, h-1b, eb5, l1, opt, cbp) tokenize to
    # nothing under the 4-char minimum, so a punctuation-insensitive normalized
    # compare rescues them. THING-only, so this never relaxes person/org identity.
    if a_type not in ("person", "org", "organization"):
        import re as _re
        a_norm = _re.sub(r"[^a-z0-9]", "", asset_subject)
        q_norm = _re.sub(r"[^a-z0-9]", "", q_subject)
        if a_norm and len(a_norm) >= 3 and q_norm and (
                a_norm == q_norm or a_norm in q_norm or q_norm in a_norm):
            return True
    if q_subject_tokens and (q_subject_tokens & (asset_subject_tokens | asset_tag_set)):
        return True
    if q_tag_tokens and (q_tag_tokens & (asset_tag_set | asset_subject_tokens)):
        return True
    if not subject and not tags:
        return True  # explicit type/quality-only query (e.g. any high-q thing b-roll)
    return False


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


def find_media_candidates(subject=None, tags=None, subject_type=None, media_type=None,
                          min_quality=0, exclude_concept=True, limit=6):
    """Return up to `limit` matching asset dicts (highest-quality first), instead
    of just the single best. Used to build a shortlist for the LLM relevance
    judge. Does NOT bump usage — the caller commits the chosen one."""
    candidates = [
        a for a in store.mirror_assets()
        if _matches(a, subject, tags, subject_type, media_type, min_quality, exclude_concept)
    ]
    def sort_key(a):
        lu = a.get("last_used") or ""
        return (-(a.get("quality_score") or 0), lu, a.get("times_used") or 0)
    candidates.sort(key=sort_key)
    return candidates[:limit]


def judge_best_asset(scene_text, candidates, openai_key=None, model="gpt-4o-mini"):
    """LLM relevance judge over an ALREADY-GATED shortlist. Returns the chosen
    asset dict or None. The deterministic gate has already guaranteed identity
    safety (no wrong person), so the judge only picks the best *relevance* fit
    among safe options — and may answer "none". Fails safe: on any error or
    missing key it returns the highest-quality candidate (candidates[0]).

    NOTE: persons should NOT be routed here — exact-match is already correct and
    needs no judgment. Use this for thing/place/event ambiguity only."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    key = openai_key or os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return candidates[0]
    try:
        import requests
        listing = []
        for idx, a in enumerate(candidates):
            desc = a.get("caption") or a.get("subject") or ""
            tg = ", ".join(str(t) for t in (a.get("tags") or [])[:6])
            listing.append(f"[{idx}] {a.get('subject','')} — {desc} (tags: {tg})")
        prompt = (
            "You are selecting B-roll for a news video scene. Pick the ONE "
            "candidate image that best fits the scene, or answer none if none "
            "genuinely fits.\n\n"
            f"SCENE: {scene_text}\n\nCANDIDATES:\n" + "\n".join(listing) +
            '\n\nReturn JSON only: {"choice": <index or null>}'
        )
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model,
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.0,
                  "response_format": {"type": "json_object"},
                  "max_tokens": 50},
            timeout=12,
        )
        if r.status_code != 200:
            return candidates[0]
        choice = json.loads(r.json()["choices"][0]["message"]["content"]).get("choice")
        if choice is None:
            return None  # judge says none fit — caller falls through to Wikipedia/Commons
        ci = int(choice)
        if 0 <= ci < len(candidates):
            return candidates[ci]
        return candidates[0]
    except Exception:
        return candidates[0]


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
