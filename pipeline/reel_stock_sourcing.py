#!/usr/bin/env python3
"""
reel_stock_sourcing.py — topical STOCK scenes for concept/policy
reels (REELS ONLY; adopted 2026-11-11 on Kiran's approval of the
GPT-benchmark sample for the India visa-categories story).

Why this exists: the production visa reel (Short 9X70oEiE-sE)
carried exactly ONE photo — a Commons entry stamp — re-cropped
at different sizes across every beat, because the story's
entities are concepts ('Visitor Visa', 'Visa Manual') and the
identity ladder correctly sources NOTHING for concepts (the
2026-11-11 concept block). A concept/policy story has no entity
to photograph, so the reel either holds or illustrates the TOPIC
with credited stock. Kiran's call (spec:
research_notes/reel-style-gpt-benchmark-2026-11-11/spec.md):
topical Pexels scenes, credited in the reel footer ("Stock
imagery: Pexels"), REELS ONLY. Article heroes/inlines are
untouched — articles stay verified-or-nothing.

ELIGIBILITY (fail closed, all must hold):
  * NO named-person dependency: no extracted entity reads as a
    person (reel_entity_sourcing._looks_like_person) and no
    entity resolves to a person through entity_resolve. A
    named-person story NEVER falls back to stock — and stock
    queries are topical scenes (places, objects, travel), never
    a person's name, so this route cannot produce a wrong-person
    picture by construction.
  * The story is concept/policy shaped: a policy keyword in the
    headline/script (visa, policy, rule, fee, ban, scheme, ...)
    or a concept entity among the script's key_entities (an
    entity the resolver marks generic-concept, or one that
    carries no verified identity at all).

SELECTION RULES:
  * Pexels API originals only; the ORIGINAL must be large
    (max dimension >= 1920 and min dimension >= 1200) so the
    9:16 cover-crop never upscales.
  * SIGNAGE SCREEN: for an India/US story, a photo whose Pexels
    alt text carries non-Latin script or names an unrelated
    country/city is rejected — the approved sample's one nit
    was a Vietnamese-signage airport photo behind an India visa
    scene. This is a text-evidence screen (alt text), not pixel
    OCR: it removes the known failure shape, it does not
    guarantee no foreign signage anywhere.
  * Distinctness: one Pexels photo id per reel, ever; the
    caller additionally dedupes by file hash against the
    article's own images.
  * Provenance per scene is recorded (photo id, page URL,
    photographer, dimensions, query) in the run's
    stock/provenance.json — the same ledger discipline as the
    identity ladder.

Network goes through curl (urllib/requests fail through this
box's proxy). The Pexels API is free; the key comes from
PEXELS_API_KEY (~/workspace/.env.pexels).
"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_entity_sourcing as RES

PEXELS_SEARCH = "https://api.pexels.com/v1/search"
MIN_STOCK_LONG = 1920        # original's long edge floor (px)
MIN_STOCK_SHORT = 1200       # original's short edge floor (px)

_POLICY_WORDS = {
    "visa", "policy", "rule", "rules", "fee", "fees", "ban",
    "scheme", "categories", "category", "application", "permit",
    "immigration", "citizenship", "passport", "tariff",
    "regulation", "reform", "law", "act", "tax", "quota",
    "deadline", "process", "manual", "guideline", "guidelines",
}

# Scene query slots, in beat order of need: (keywords that
# trigger the slot, query). The story's own place entities are
# prepended as landmark queries before these (see
# build_stock_queries).
_QUERY_SLOTS = (
    ({"airport", "flight", "travel", "visa", "tourist",
      "visitor", "trip", "journey"},
     "airport departure terminal travelers"),
    ({"passport", "visa", "document", "documents", "id"},
     "passport travel documents flat lay"),
    ({"form", "application", "paperwork", "fields", "apply"},
     "hand writing on a paper form"),
    ({"family", "spouse", "relatives", "friends", "visit",
      "visiting", "diaspora", "home"},
     "family arriving at airport travel"),
    ({"city", "capital", "landmark", "gate", "monument"},
     "india gate new delhi golden hour"),
)
_FALLBACK_QUERIES = (
    "taj mahal india travel",
    "airplane wing sunset travel",
    "traveler with suitcase airport",
    "india city street travel",
    "passport and boarding pass travel",
)

# Alt-text evidence of an unrelated locale: non-Latin script is
# screened separately; these are Latin-script place names that
# mark signage/scene locales outside an India/US diaspora story.
_FOREIGN_LOCALE_WORDS = {
    "vietnam", "vietnamese", "hanoi", "saigon", "bangkok",
    "thailand", "beijing", "shanghai", "china", "chinese",
    "tokyo", "japan", "japanese", "seoul", "korea", "korean",
    "dubai", "emirates", "istanbul", "turkey", "moscow",
    "russia", "russian", "paris", "france", "french",
    "berlin", "germany", "german", "madrid", "spain",
    "spanish", "rome", "italy", "italian", "london",
    "sydney", "australia", "toronto", "canada", "canadian",
    "mexico", "mexican", "brazil", "egypt", "cairo",
    "hong", "kong", "amsterdam", "schiphol", "netherlands",
    "ukraine", "ukrainian", "kyiv", "barcelona",
    "dutch", "singapore", "malaysia", "jakarta", "indonesia",
    "manila", "philippines", "taipei", "taiwan", "austria",
    "vienna", "switzerland", "zurich", "swiss", "portugal",
    "lisbon", "portuguese", "poland", "warsaw", "polish",
    "greece", "athens", "greek", "finland", "helsinki",
    "finnish", "norway", "oslo", "sweden", "stockholm",
    "swedish", "denmark", "copenhagen", "danish", "ireland",
    "dublin", "irish", "iceland", "hungary", "budapest",
    "czech", "prague", "frankfurt", "munich", "hamburg",
}
_STORY_LOCALE_WORDS = {"india", "indian", "delhi", "mumbai",
                       "usa", "america", "american", "york",
                       "angeles", "francisco", "chicago",
                       "houston", "dallas", "seattle", "boston",
                       "atlanta", "jersey", "washington"}


def _headline_words(article, script):
    text = " ".join([
        article.get("headline") or article.get("title") or "",
        (script or {}).get("hook_line") or "",
        (script or {}).get("news_summary") or ""])
    return set(re.findall(r"[a-z]+", text.lower()))


# Tokens that mark an entity as a THING/place/concept however
# person-shaped its capitalization looks ('Visitor Visa',
# 'Visa Manual', 'Chennai Stadium' all pass the shared
# _looks_like_person shape test — two capitalized tokens, no
# org word). A real person's name does not contain these.
_NONPERSON_TOKENS = {
    "visa", "manual", "stadium", "airport", "policy",
    "passport", "permit", "scheme", "category", "categories",
    "fee", "fees", "tax", "court", "house", "street", "park",
    "river", "bridge", "tower", "building", "museum",
    "temple", "church", "school", "college", "hospital",
    "station", "market", "markets", "index", "fund", "bank",
    "airlines", "airways", "express", "limited", "group",
}


def _entity_is_person(e, context_text=""):
    """Person determination for the stock gate — STRICTER than
    the sourcing ladder's shape heuristic, because this gate is
    what stands between a named-person story and stock photos:
    a verified resolution type wins when one exists; otherwise
    the shape test must pass AND no token may be non-person
    vocabulary."""
    import entity_resolve as ER
    try:
        res = ER.resolve(e, context_text)
    except Exception:
        res = None
    if res and res.get("type"):
        return res["type"] == "person"
    if not RES._looks_like_person(e):
        return False
    toks = {t.lower().strip(".,") for t in e.split()}
    return not (toks & _NONPERSON_TOKENS)


def story_person_names(article, script):
    """Entities that are named people — strict determination
    (see _entity_is_person)."""
    ctx = " ".join([article.get("headline") or "",
                    (script or {}).get("hook_line") or ""])
    persons = []
    for e in RES.extract_entities(article, script or {}):
        if _entity_is_person(e, ctx):
            persons.append(e)
    return persons


def is_concept_policy_story(article, script, log=print):
    """(eligible, reason). Fail closed: any named-person
    dependency, or no concept/policy signal, is ineligible."""
    persons = story_person_names(article, script)
    if persons:
        return False, (f"named-person story ({', '.join(persons)})"
                       " — stock fallback forbidden")
    words = _headline_words(article, script)
    if words & _POLICY_WORDS:
        return True, "policy keyword in headline/script"
    # Concept signal: a key entity the resolver marks a generic
    # concept, or that carries no verified identity at all.
    import entity_resolve as ER
    for e in (script or {}).get("key_entities") or []:
        try:
            res = ER.resolve(e, article.get("headline") or "")
        except Exception:
            res = None
        if ER.is_generic_concept(e, (res or {}).get("type")):
            return True, f"concept entity {e!r} has no identity " \
                         "to photograph"
    return False, "no concept/policy signal — not a stock story"


# Off-topic contamination: medical/pandemic content words. A
# "health passport / COVID-19 QR code" flat lay is NOT a visa
# photo (measured on the first per-beat proof, 2026-11-11 —
# the alt said so verbatim and nothing screened it). These
# words reject UNLESS the story itself uses them.
_CONTAMINATION_WORDS = {"covid", "coronavirus", "vaccine",
                        "vaccination", "pandemic"}


def alt_text_locale_ok(alt_text, story_words):
    """The signage screen: alt text with non-Latin script, or
    naming a locale unrelated to the story's locales, rejects.
    Story locales = India/US by default (the diaspora frame),
    widened by any locale word the story itself uses. Also
    screens off-topic contamination (COVID/vaccine content
    in a story that is not about it)."""
    alt = (alt_text or "").lower()
    if any(ord(c) > 0x250 for c in alt):
        return False, "alt text carries non-Latin script " \
                      "(foreign signage risk)"
    alt_words = set(re.findall(r"[a-z]+", alt))
    foreign = alt_words & _FOREIGN_LOCALE_WORDS
    allowed = _STORY_LOCALE_WORDS | (story_words &
                                     _FOREIGN_LOCALE_WORDS)
    bad = foreign - allowed
    if bad:
        return False, f"alt text names unrelated locale(s): " \
                      f"{', '.join(sorted(bad))}"
    contam = (alt_words & _CONTAMINATION_WORDS) - story_words
    if contam:
        return False, f"alt text carries off-topic content " \
                      f"({', '.join(sorted(contam))}) the story " \
                      "is not about"
    if {"health", "passport"} <= alt_words \
            and "health" not in story_words:
        return False, "alt text describes a health passport — " \
                      "not this story's document"
    return True, ""


def dims_ok_stock(w, h):
    return bool(w) and bool(h) \
        and max(w, h) >= MIN_STOCK_LONG \
        and min(w, h) >= MIN_STOCK_SHORT


HARD_FLOOR_W = 1080          # reel scenes: never below this wide
COVER_WINDOW_MIN = 800       # the 9:16 window must reach this
                             # (else the scene demotes to nothing)


def cover_window_w(w, h):
    """Width of the 9:16 cover window of a w x h original."""
    return min(w, int(h * 9 / 16)) if w and h else 0


def photo_acceptable(ph):
    """(ok, reason) — the HARD floors for one Pexels photo:
    >= 1080px wide (Kiran's floor for reel scenes) and a 9:16
    cover window that can actually fill a scene."""
    w, h = ph.get("width") or 0, ph.get("height") or 0
    if w < HARD_FLOOR_W:
        return False, f"width {w} below the {HARD_FLOOR_W}px " \
                      "hard floor for reel scenes"
    if cover_window_w(w, h) < COVER_WINDOW_MIN:
        return False, f"9:16 cover window " \
                      f"{cover_window_w(w, h)}px below " \
                      f"{COVER_WINDOW_MIN} — would demote to " \
                      "an empty scene"
    return True, ""


def rank_photos(photos):
    """Order acceptable candidates by resolution preference:
    originals >= 1920px wide first (the approved sample used
    4000px+ originals), widest first within each class."""
    return sorted(
        photos,
        key=lambda ph: ((ph.get("width") or 0) >= 1920,
                        ph.get("width") or 0),
        reverse=True)


def beat_query_tiers(article, script, beat):
    """(primary, fallback) query lists for ONE scene: primary
    = the slots the beat's own rendered words trigger (the
    scene's picture illustrates the scene's TEXT — a form-
    fields beat gets the form close-up); fallback = the
    story's general topical queries, used only when no
    primary candidate clears the screens. Topicality ranks
    above resolution: a generic 4000px photo must not beat
    the beat's own 2400px subject."""
    import reel_renderer as R
    category = str(article.get("category") or "News") \
        .replace("-", " ").title()
    try:
        text = " ".join(R.SCENE_TEXTS[beat](script or {},
                                            category))
    except Exception:
        text = ""
    words = set(re.findall(r"[a-z]+", text.lower()))
    primary, seen = [], set()
    for keys, q in _QUERY_SLOTS:
        if words & keys and q.lower() not in seen:
            seen.add(q.lower())
            primary.append(q)
    fallback = [q for q in build_stock_queries(article, script)
                if q.lower() not in seen]
    return primary[:3], fallback[:3]


def beat_queries(article, script, beat):
    primary, fallback = beat_query_tiers(article, script,
                                         beat)
    return (primary + fallback)[:4]


def build_stock_queries(article, script):
    """Ordered topical queries for this story: place-entity
    landmarks first, then keyword-triggered scene slots, then
    generic travel fallbacks. Never a person's name."""
    words = _headline_words(article, script)
    queries, seen = [], set()

    def add(q):
        q = re.sub(r"\s+", " ", (q or "").strip())
        if q and q.lower() not in seen:
            seen.add(q.lower())
            queries.append(q)

    persons = set(story_person_names(article, script))
    for e in RES.extract_entities(article, script or {}):
        if e in persons:
            continue
        toks = RES.entity_tokens(e)
        if any(t in ("india", "delhi", "mumbai", "york",
                     "angeles") for t in toks) or \
                any(t in RES._PLACE_TOKENS for t in
                    [t.lower() for t in e.split()]):
            add(f"{e} landmark")
    for keys, q in _QUERY_SLOTS:
        if words & keys:
            add(q)
    for q in _FALLBACK_QUERIES:
        add(q)
    return queries


def _pexels_search(query, key, per_page=8):
    url = (f"{PEXELS_SEARCH}?query={query.replace(' ', '%20')}"
           f"&per_page={per_page}&orientation=any")
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "30", "-A", "TheVideshi/1.0",
         "-H", f"Authorization: {key}", url],
        capture_output=True, text=True, timeout=45)
    if r.returncode != 0:
        raise RuntimeError(f"pexels search failed: "
                           f"{(r.stderr or '')[:160]}")
    return json.loads(r.stdout).get("photos") or []


def _download(url, dest):
    r = subprocess.run(
        ["curl", "-sSL", "--max-time", "60", "-A", "TheVideshi/1.0",
         "-o", str(dest), url], capture_output=True, text=True,
        timeout=75)
    if r.returncode != 0 or not Path(dest).exists() \
            or Path(dest).stat().st_size < 10000:
        raise RuntimeError(f"stock download failed: {url}")


def source_stock_scenes(article, script, dest_dir, need,
                        log=print, api_key=None, beats=None):
    """Source up to `need` distinct topical stock scenes,
    PER SCENE: when `beats` names the scenes that need stock,
    each beat is sourced from queries matched to that beat's
    own text (beat_queries), and the best-resolution
    acceptable original wins (>= 1920px wide preferred,
    1080px the hard floor). Each scene records its beat, its
    source dimensions and its provenance. Without `beats`,
    the story-level round-robin is used. NEVER raises —
    failures ledger and yield fewer scenes; the caller's
    distinct-image hold decides the reel's fate."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    prov = {"route": "stock — Pexels topical scenes, per-beat "
                     "matched (reels only, 2026-11-11)",
            "story": article.get("slug"),
            "scenes": [], "rejected": []}
    key = api_key or os.environ.get("PEXELS_API_KEY")
    if not key:
        prov["rejected"].append(
            {"candidate": "(pexels)", "reason": "PEXELS_API_KEY "
             "not in env — stock route unavailable"})
        log("   stock: no PEXELS_API_KEY — route unavailable")
        return prov
    if need <= 0:
        return prov
    story_words = _headline_words(article, script)
    used_ids = set()
    search_cache = {}

    def search(q):
        if q not in search_cache:
            try:
                search_cache[q] = _pexels_search(q, key)
            except Exception as e:
                prov["rejected"].append(
                    {"candidate": f"query {q!r}",
                     "reason": str(e)[:200]})
                search_cache[q] = []
        return search_cache[q]

    def accept(ph, q, beat):
        """Screen + download one photo; returns the scene
        record or None (rejections ledgered)."""
        pid = ph.get("id")
        if pid in used_ids:
            return None
        ok, why = photo_acceptable(ph)
        if not ok:
            prov["rejected"].append(
                {"candidate": f"pexels {pid}", "reason": why})
            return None
        ok, why = alt_text_locale_ok(ph.get("alt") or "",
                                     story_words)
        if not ok:
            prov["rejected"].append(
                {"candidate": f"pexels {pid}",
                 "reason": f"signage screen: {why}"})
            return None
        src = ph.get("src") or {}
        url = src.get("original") or src.get("large2x")
        if not url:
            return None
        fname = f"stock-{pid}.jpg"
        dest = dest_dir / fname
        try:
            _download(url, dest)
            from PIL import Image
            with Image.open(dest) as im:
                true_size = list(im.size)
        except Exception as e:
            prov["rejected"].append(
                {"candidate": f"pexels {pid}",
                 "reason": f"download/verify failed: {e}"[:200]})
            return None
        ok, why = photo_acceptable(
            {"width": true_size[0], "height": true_size[1]})
        if not ok:
            prov["rejected"].append(
                {"candidate": f"pexels {pid}",
                 "reason": f"downloaded file: {why}"})
            return None
        used_ids.add(pid)
        sha = hashlib.sha256(dest.read_bytes()).hexdigest()
        rec = {"path": fname, "size": true_size,
               "pexels_id": pid, "page": ph.get("url"),
               "photographer": ph.get("photographer"),
               "query": q, "beat": beat,
               "alt": (ph.get("alt") or "")[:200],
               "sha256": sha,
               "license": "Pexels License (free use); credited "
                          "in the reel footer"}
        prov["scenes"].append(rec)
        log(f"   stock[{beat or 'story'}]: scene ← pexels "
            f"{pid} ({true_size[0]}x{true_size[1]}, "
            f"query {q!r})")
        return rec

    if beats:
        for beat in beats:
            if len(prov["scenes"]) >= need:
                break
            primary, fallback = beat_query_tiers(
                article, script, beat)
            done = False
            for tier_queries in (primary, fallback):
                if done:
                    break
                seen = set()
                pairs = []
                for q in tier_queries:
                    for ph in search(q):
                        if ph.get("id") in seen:
                            continue
                        seen.add(ph.get("id"))
                        pairs.append((q, ph))
                ranked = sorted(
                    pairs,
                    key=lambda qp: ((qp[1].get("width") or 0)
                                    >= 1920,
                                    qp[1].get("width") or 0),
                    reverse=True)
                for q, ph in ranked:
                    if accept(ph, q, beat):
                        done = True
                        break
    else:
        queries = build_stock_queries(article, script)
        results = {q: search(q) for q in queries}
        passes = [[(q, ph) for q in queries
                   for ph in rank_photos(results[q])[:1]],
                  [(q, ph) for q in queries
                   for ph in rank_photos(results[q])[1:]]]
        for playlist in passes:
            for q, ph in playlist:
                if len(prov["scenes"]) >= need:
                    break
                accept(ph, q, None)
    if not prov["scenes"]:
        log("   stock: no topical scene cleared the screens")
    return prov
