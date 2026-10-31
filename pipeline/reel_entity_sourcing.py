#!/usr/bin/env python3
"""
reel_entity_sourcing.py — supplementary ENTITY image sourcing for
Reels v7 (production, 2026-10-24).

Kiran's reel image doctrine: every reel carries at least 4–5
pictures tied to the article's ENTITIES (company campus/HQ, the
CEO/person, the place, the org building). Priority ladder: the
article's own imagery first (the hero is the closest picture to
the news), then verified sourced entity pictures. This module is
the second rung — it runs INSIDE reel_produce.py when the story's
own assets (hero + inline images) total fewer than TARGET_DISTINCT
usable scene images.

THE LADDER (2026-10-31 — identity route ONLY; the open-search
routes this module originally ran are abolished):
  Supplementary images come exclusively from identity by
  construction, the standard the article/card paths adopted in
  the image rebuild (design.md, 2026-10-30): each extracted
  entity is resolved through entity_resolve.py +
  entity_registry.json (registry first, then sitelink-primacy
  Wikidata adjudication), and the only candidates are the
  resolved item's screened P18 and its depicts (P180) Commons
  files, each re-run through this module's file gates
  (photograph type, title denylist, true dimensions, CC /
  public-domain license, corpus blocklist). An entity that
  cannot be resolved to a verified Wikidata identity — or
  whose resolution fails the names_agree standard, is
  ambiguous, is a language (non-visual), or has no QID —
  sources NOTHING: the scene falls back to the article's own
  imagery / a navy text card. There is no Commons text search,
  no Brave discovery, and no official-page route in this
  ladder anymore. (commons_search / brave_links /
  evaluate_hosted_page survive below as library functions for
  article_picture_pass.py and social_card.py, which gate their
  own routes; source_extras never calls them.)

  Why: five reels passed fact-check + frame QA 10.0 and were
  withheld on visual check (2026-10-29→31) because keyword
  search cannot tell a word's senses apart — Caterpillar the
  company sourced insect photos, Blackstone the firm sourced
  Blackstone, MA/VA town photos, Chevron sourced a military
  shoulder patch and a chevron-pattern masonry photo, the
  pseudo-entity 'Markets Finance' sourced a World Bank panel
  portrait into two earnings reels, and 'Sun Pictures'
  decomposed to 'Sun' sourced a NASA solar eruption.

HARD RULES (never relaxed): provably the named entity or skip —
and the entity must be the file's SUBJECT (a warbler photographed
IN Central Park is not a picture OF Central Park; a district map
is not a scene photograph); license clean (CC / public domain,
attribution recorded) or skip; true dimensions at the file,
at/above the reel photo floor, never upscaled; no AI images, no
stock stand-ins for named entities. Sourcing NEVER blocks the
reel: any failure yields fewer (or zero) extras and the v7
planner falls back to the hero chain. (Gate discipline proven on
the first production run, 2026-10-24: a district-map full-bleed
tripped frame QA's edge_overflow and the reel held — the
relevance rejections below were added from that run's ledger.)

IDENTITY GATES (2026-10-27, ported from the article picture
pass via picture_gate_shared.py — the 2026-10-26 pulse run
proved this module had none of them): a news OUTLET is never a
picture entity ('Times of India' sourced a portrait of its
journalist Jug Suraiya); a candidate whose own evidence places
it in a country/domain the story is not about is a NAMESAKE
('PERM' the labor programme sourced Perm, Russia; the Moscow
'White House' sourced for Washington); a portrait of a named
person who is not one of the story's subjects is rejected
(depicted-person gate); and a PERSON candidate must pass the
picture pass's namesake gate — no profession/domain
contradiction with the story, and a story-context token (or
the person's own Commons category) in its evidence.

Output: a provenance dict in the exact schema the sample used —
{"built", "story", "trigger", "candidate_ledger", "extras"} —
where each extra is {beat, label, path, size, role, subject,
route, source_page, file_url, license, artist, anchor?} and `path`
is a filename inside the destination dir (the caller resolves it
against the provenance file's directory, as reel_produce_v7's
load_extras does). Files are downloaded into the destination dir
as they are assigned.
"""
import html as html_lib
import json, re, subprocess, sys, urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_renderer as R   # BEATS / SCENE_TEXTS only (no render)
import picture_gate_shared as G   # the identity gates shared
                                  # with the article picture
                                  # pass (single source of truth)
import entity_resolve as ER   # identity by construction:
                              # registry + Wikidata resolution,
                              # depicts candidates, blocklist,
                              # the names_agree standard

# Re-exported for parity with article_picture_pass: the outlet
# blocklist itself lives ONLY in picture_gate_shared.py.
OUTLET_ENTITIES = G.OUTLET_ENTITIES
is_outlet_entity = G.is_outlet_entity

TARGET_DISTINCT = 5          # doctrine: >= 4–5 pictures per reel
MIN_EXTRA_W, MIN_EXTRA_H = R.MIN_PHOTO_W, R.MIN_PHOTO_H   # 1080x600
MAX_ENTITIES = 6
MAX_POOL = 8                 # accepted candidates kept for assignment
PER_ENTITY_CAP = 2           # at most 2 scenes per entity
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
UA_BROWSER = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36")

# Title fragments that mark a file as NOT a scene photograph.
DENY_TITLE = ("logo", "icon", "diagram", "chart", "graph", "map",
              "locator", "signature", "poster", "seal of",
              "flag of", "coat of arms", "wordmark", "cover art",
              "screenshot")
# Map/graphic fragments checked against title + description: a
# council-district outline is a map even when the word "map"
# never appears (first production run's ledger, 2026-10-24).
MAP_FRAGMENTS = ("district", "boundaries", "redistricting",
                 "outline of")
# Category markers whose presence means the file's SUBJECT is
# wildlife (species category, a "birds of …" category, a Latin
# binomial) — photographed AT a place is not a picture OF it.
_WILDLIFE_CAT_MARKERS = ("birds", "fauna", "flora", "insects",
                         "butterflies", "moths", "passeriformes",
                         "wildlife")
_BINOMIAL_RE = re.compile(r"^[A-Z][a-z]+ [a-z]{3,}$")
# A binomial category may carry a descriptor tail ("Corvus
# splendens heads" — the category that let a crow illustrate
# Tamil Nadu in the 2026-10-25 article picture pass). The pair
# still marks a wildlife subject when the remaining words are
# only body/view descriptors, and the genus word is not a
# category-administration starter ("Quality images", ...).
_BINOMIAL_TAIL = {"heads", "head", "male", "female", "juvenile",
                  "juveniles", "flight", "view", "views", "close",
                  "portrait", "portraits", "specimen", "specimens",
                  "eggs", "nest", "nests", "calls", "sounds"}
_BINOMIAL_GENUS_STOP = {"quality", "featured", "valued", "self",
                        "taken", "files", "images", "pictures",
                        "photographs", "commons", "wikipedia",
                        "media", "category"}


def _binomial_subject(seg):
    """True when a category segment names a species: an exact
    Latin binomial, or a binomial plus a descriptor tail."""
    if _BINOMIAL_RE.match(seg):
        return True
    words = seg.split()
    if not (3 <= len(words) <= 5):
        return False
    if not re.fullmatch(r"[A-Z][a-z]+", words[0]) \
            or not re.fullmatch(r"[a-z]{3,}", words[1]):
        return False
    if words[0].lower() in _BINOMIAL_GENUS_STOP:
        return False
    return all(w.lower() in _BINOMIAL_TAIL for w in words[2:])
_WILDLIFE_WORDS = {"bird", "birds", "eagle", "owl", "fish", "deer",
                   "bear", "wolf", "whale", "shark", "snake",
                   "frog", "butterfly", "bee", "spider"}

_STOP_TOKENS = {
    "the", "of", "and", "for", "in", "on", "at", "to", "a", "an",
    "us", "inc", "llc", "ltd", "corp", "corporation", "company",
    "co", "mr", "mrs", "dr",
}
# Acronym <-> full-name aliases for the beat-relevance scorer:
# beat text says "DOJ", the entity record says "Department of
# Justice" (expanded forms as lowercase token strings).
ALIASES = {
    "department of justice": ("doj",),
    "federal bureau of investigation": ("fbi",),
    "national aeronautics and space administration": ("nasa",),
    "securities and exchange commission": ("sec",),
    "food and drug administration": ("fda",),
    "citizenship and immigration services": ("uscis",),
    "internal revenue service": ("irs",),
    "federal reserve": ("fed",),
    "department of homeland security": ("dhs",),
    "environmental protection agency": ("epa",),
}
_ORG_TOKENS = {
    "corp", "inc", "university", "institute", "bank", "department",
    "agency",
    "commission", "bureau", "authority", "foundation", "hospital",
    "airlines", "airways", "motors", "technologies", "systems",
    "group", "holdings", "studios", "networks", "labs",
    "laboratories", "ministry", "council", "court", "senate",
    "congress", "administration", "services", "solutions",
}

_ROLE_KEYWORDS = (
    ("portrait", ("portrait", "headshot")),
    ("people", ("employees", "students", "workers", "crowd",
                "people", "passengers", "fans", "devotees",
                "pilgrims", "visitors")),
    ("detail", ("sign", "entrance", "door", "gate", "plaque",
                "detail", "inscription")),
    ("interior", ("cafeteria", "interior", "inside", "lobby",
                  "atrium", "office", "hall")),
    ("establishing", ("campus", "headquarters", "hq", "building",
                      "facade", "exterior", "head office", "tower",
                      "complex", "headquarter")),
)
# Editorial beat affinity (role preferences, best first).
_BEAT_ROLES = {
    "news": ("establishing", "detail", "people", "interior",
             "portrait"),
    "hero": ("establishing", "detail", "portrait", "people",
             "interior"),
    "grid": ("detail", "establishing", "interior", "people",
             "portrait"),
    "diaspora": ("people", "interior", "establishing", "portrait",
                 "detail"),
    "payoff": ("portrait", "interior", "establishing", "people",
               "detail"),
}
_BEATS_NEEDING = ("news", "hero", "grid", "diaspora", "payoff")


# ── small pure helpers ──────────────────────────────────────────────
def _strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    return re.sub(r"\s+", " ", html_lib.unescape(text)).strip()


def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9][a-z0-9'\-]*",
                                  (text or "").lower())
            if len(t) >= 2 and t not in _STOP_TOKENS]


def entity_tokens(entity):
    return [t for t in _tokens(entity)]


def _contains_all(tokens, text):
    words = set(re.findall(r"[a-z0-9][a-z0-9'\-]*",
                           (text or "").lower()))
    return all(t in words for t in tokens)


def slugify(text, fallback="image"):
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s[:44].rstrip("-") or fallback)


# ── the gates (pure; unit-tested) ───────────────────────────────────
def license_verdict(extmetadata):
    """(ok, label) from Commons extmetadata. Accepts CC0 / CC BY*
    / public domain only; everything else (GFDL, fair use, missing
    metadata) rejects — the doctrine is CC/PD with attribution."""
    meta = extmetadata or {}
    short = ((meta.get("LicenseShortName") or {}).get("value")
             or "").strip()
    terms = ((meta.get("UsageTerms") or {}).get("value")
             or "").strip()
    probe = f"{short} {terms}".lower()
    if "public domain" in probe or probe.startswith("pd") \
            or "cc0" in probe:
        return True, short or "Public domain"
    if re.search(r"\bcc[ -]by\b", probe) or "creative commons" in probe:
        return True, short or terms
    return False, short or terms or "(no license metadata)"


def _phraseish(toks, evidence):
    """The entity's significant tokens appear IN ORDER in the
    evidence token stream, with at most ONE filler token
    between neighbours (stopwords never enter the stream, so
    'Department of Justice' is a zero-gap phrase) — that
    evidences the DOJ; 'New York City, home of the Security
    Council' (a UN photo scattering the words) does not
    evidence the New York City Council."""
    stream = _tokens(evidence)

    def chain_from(start):
        pos = start
        for t in toks[1:]:
            found = None
            for i in range(pos + 1, min(len(stream), pos + 3)):
                if stream[i] == t:
                    found = i
                    break
            if found is None:
                return False
            pos = found
        return True

    return any(chain_from(i) for i, t in enumerate(stream)
               if t == toks[0])


def identity_ok(entity, title, description, categories_text):
    """The entity's significant tokens must ALL appear, as whole
    words, in the file page's own evidence (title + description +
    categories). 'Salil Parekh' rejects 'Asha Parekh' (missing
    'salil'); a spider macro rejects for 'Infosys' (neither
    token present). Entities with 3+ significant tokens must
    additionally appear as a near-contiguous phrase — scattered
    tokens across a long description are coincidence, not
    identity (the UN-building / City-Council scatter)."""
    toks = entity_tokens(entity)
    if not toks:
        return False
    evidence = f"{title} {_strip_html(description)} {categories_text}"
    if not _contains_all(toks, evidence):
        return False
    if len(toks) >= 3:
        return _phraseish(toks, evidence)
    return True


def dims_ok(w, h):
    return bool(w) and bool(h) and w >= MIN_EXTRA_W and h >= MIN_EXTRA_H


def title_denied(title):
    t = (title or "").lower()
    return any(d in t for d in DENY_TITLE)


def subject_denied(title, description=""):
    """Title denylist, plus map/graphic fragments over title +
    description (district outlines, boundary maps)."""
    if title_denied(title):
        return True
    text = f"{title} {_strip_html(description)}".lower()
    return any(f in text for f in MAP_FRAGMENTS)


def wildlife_subject(entity, categories_text):
    """True when the Commons categories mark the file's SUBJECT
    as wildlife unrelated to the entity: a Latin-binomial
    category (Setophaga castanea) or a wildlife category
    (Passeriformes of Central Park, Birds in September 2021)
    whose markers are not part of the entity itself. A nature
    story whose entity IS wildlife is exempt."""
    if not categories_text:
        return False
    ent = set(entity_tokens(entity))
    if ent & _WILDLIFE_WORDS:
        return False
    for seg in categories_text.split("|"):
        seg = seg.strip()
        if _binomial_subject(seg) \
                and not (set(_tokens(seg)) & ent):
            return True
        low = seg.lower()
        if any(m in low for m in _WILDLIFE_CAT_MARKERS) \
                and not any(m in ent
                            for m in _WILDLIFE_CAT_MARKERS):
            return True
    return False


def classify_role(title, description):
    text = f"{title} {_strip_html(description)}".lower()
    for role, keys in _ROLE_KEYWORDS:
        if any(k in text for k in keys):
            return role
    return "establishing"


# ── story context + the shared identity gates (2026-10-27) ────
# Ported from article_picture_pass.py (which caught these
# failure classes on 2026-10-25/26) through
# picture_gate_shared.py. The reel gates run ONLY when the
# caller supplies the context built here — source_extras
# always does; direct evaluator calls (tests, social_card.py)
# without a context keep the pre-2026-10-27 behaviour.

def build_story_context(article, script, entities):
    """Everything the shared identity gates need to know about
    the story: its headline, its category domain, the full
    entity list, the countries/domains its own text places it
    in (headline + script + body), and its SUBJECT persons —
    the script's key_entities / the article's image_entities
    that read as people (a depicted portrait is legitimate
    only for one of those, or for the entity being sourced)."""
    script = script or {}
    headline = article.get("headline") or article.get("title") \
        or ""
    parts = [headline, article.get("summary") or "",
             article.get("excerpt") or ""]
    for key in ("hook_line", "news_summary", "payoff"):
        if script.get(key):
            parts.append(str(script[key]))
    for b in script.get("diaspora_bullets") or []:
        parts.append(str(b))
    for s in script.get("stats") or []:
        if isinstance(s, dict):
            parts.append(str(s.get("label") or ""))
    parts.append((article.get("body") or "")[:20000])
    subjects, seen = [], set()
    raw = list(script.get("key_entities") or []) \
        + list(article.get("image_entities") or [])
    for e in raw:
        e = _clean_entity(e)
        if not e or e.lower() in seen:
            continue
        seen.add(e.lower())
        toks = e.split()
        single_person = len(toks) == 1 and re.fullmatch(
            r"[A-Z][A-Za-z.'\-]+", toks[0]) \
            and toks[0].lower() not in _ORG_TOKENS \
            and toks[0].lower() not in _PLACE_TOKENS
        if _looks_like_person(e) or single_person:
            subjects.append(frozenset(entity_tokens(e)))
    domain = str(article.get("category") or "").strip().lower() \
        .replace(" ", "-")
    return {"headline": headline, "domain": domain,
            "entities": list(entities or []),
            "countries": G.countries_in(" ".join(parts)),
            "subject_persons": subjects}


def _person_context_terms(context, entity):
    """Context vocabulary for the person namesake gate (the
    picture pass's _person_context_terms, same construction):
    headline content words + the OTHER entities' tokens +
    the story category's domain vocabulary, minus this
    entity's own tokens (identity already guarantees those —
    left in, the agreement check would be vacuous)."""
    toks = set()
    for w in re.findall(r"[a-z0-9]+",
                        (context.get("headline") or "").lower()):
        if len(w) >= 4 and not w.isdigit() \
                and w not in _HINT_STOP \
                and w not in G.HINT_FUNCTION_WORDS:
            toks.add(w)
    for other in context.get("entities") or []:
        if other and other.lower() != (entity or "").lower():
            for t in entity_tokens(other):
                if len(t) >= 4 and t not in G.HINT_FUNCTION_WORDS:
                    toks.add(t)
    cat = context.get("domain") or ""
    toks.update(G.PERSON_DOMAIN_TOKENS.get(cat, ()))
    for t in re.findall(r"[a-z]+", cat):
        if len(t) >= 4:
            toks.add(t)
    return frozenset(toks - set(entity_tokens(entity)))


def context_reject_reason(entity, title, description,
                          categories_text, context):
    """The shared identity gates over one candidate's evidence
    (Commons title + description + categories). Returns the
    rejection reason, or None when the candidate agrees with
    the story's context. Gates, in order:

    1. COUNTRY/DOMAIN CONTRADICTION — the candidate's evidence
       positively places it in a country the story's own text
       never places it in (Perm, Russia for the PERM
       programme; the Moskva River 'White House' for
       Washington). No placement evidence = no verdict: the
       gate rejects namesakes, it does not demand proof of
       place from every file. PERSON entities are exempt —
       a person's verified portrait is the person wherever
       it was taken (the story's own Keith Sonderling
       photographed at the ILO in Geneva); persons are
       policed by gate 3 instead. (The picture pass splits
       its gates by entity kind the same way.)
    2. DEPICTED PERSON — the file is a portrait of a named
       person who is neither the entity nor one of the
       story's subject persons (Jug Suraiya, sourced under
       an outlet entity for a Drishyam story).
    3. PERSON NAMESAKE — for a person entity, the picture
       pass's gate: a profession/domain marker unique to a
       DIFFERENT domain in the evidence is a contradiction,
       and with no story-context agreement and no own Commons
       category the file cannot be told apart from a
       same-name different person."""
    if not context:
        return None
    evidence = G.mask_title_phrases(
        f"{title} {_strip_html(description)} {categories_text}")
    cand_countries = G.countries_in(evidence)
    story_countries = context.get("countries") or frozenset()
    if not _looks_like_person(entity) \
            and cand_countries and story_countries \
            and cand_countries.isdisjoint(story_countries):
        return ("namesake/context: the file's evidence places "
                f"it in {'/'.join(sorted(cand_countries))}, "
                "which this story is not about (story context: "
                f"{'/'.join(sorted(story_countries))}) — a "
                f"namesake, not {entity!r} in this story")
    person = G.depicted_person_name(title, entity,
                                     entity_tokens)
    if person:
        ptoks = frozenset(entity_tokens(person))
        if not any(ptoks == s or ptoks <= s
                   for s in context.get("subject_persons")
                   or ()):
            return (f"depicted person: the file is a portrait "
                    f"of {person}, who is not one of this "
                    f"story's subjects — association is not "
                    f"depiction ({entity!r})")
    if _looks_like_person(entity):
        ev_tokens = set(_tokens(evidence))
        bad = G.domain_contradiction_markers(
            context.get("domain"))
        contra = {t for t in bad
                  if G.ctx_token_match(t, ev_tokens)}
        for d in re.findall(r"\(([^)]+)\)", evidence):
            d_toks = set(_tokens(d))
            contra |= {t for t in bad
                       if any(G.ctx_token_match(t, {x})
                              for x in d_toks)}
        if contra:
            return ("namesake guard: the file's evidence marks "
                    f"a different domain "
                    f"({', '.join(sorted(contra))}) than this "
                    f"{context.get('domain') or 'story'} story "
                    f"— a same-name different person, not "
                    f"{entity!r} the subject of this story")
        ctx_terms = _person_context_terms(context, entity)
        matched = {t for t in ctx_terms
                   if G.ctx_token_match(t, ev_tokens)}
        own_cat = any(
            seg.strip().lower().removeprefix("category:")
            == (entity or "").strip().lower()
            for seg in (categories_text or "").split("|"))
        if not matched and not own_cat:
            return ("namesake guard: the file page's evidence "
                    "shares no story-context token with this "
                    "article and the file is not in the "
                    "person's own Commons category, so it "
                    "cannot be told apart from a same-name "
                    f"different person ({entity!r})")
    return None


# ── entity extraction (article -> picture-worthy entities) ─────────
_MONTHS = {"january", "february", "march", "april", "may", "june",
           "july", "august", "september", "october", "november",
           "december"}
_PHRASE_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z&.'\-]+|[A-Z]{2,})"
    r"(?:\s+(?:[A-Z][A-Za-z&.'\-]+|[A-Z]{2,}|of|the|and|&|for|de))"
    r"{0,3}\s+(?:[A-Z][A-Za-z&.'\-]+|[A-Z]{2,})\b")


def _clean_entity(e):
    e = re.sub(r"\s+", " ", (e or "").strip(" .,;:'\"()[]"))
    if not e or len(e) < 3:
        return None
    toks = e.split()
    if toks[0].lower() in ("the", "a", "an", "in", "on", "at",
                           "after", "before", "as", "but", "under",
                           "amid", "over", "how", "why", "when",
                           "while"):
        toks = toks[1:]
    if not toks:
        return None
    e = " ".join(toks)
    if e.lower() in _MONTHS or e.split()[0].lower() in _MONTHS:
        return None
    if not any(c.isalpha() for c in e):
        return None
    return e


def extract_entities(article, script):
    """Picture-worthy entities for a story, best first: the
    script's key_entities (worker-written from the article), the
    article's image_entities, capitalized phrases from the
    headline, then frequent capitalized phrases from the body."""
    out, seen = [], set()

    def add(e):
        e = _clean_entity(e)
        if not e:
            return
        k = e.lower()
        if k not in seen:
            seen.add(k)
            out.append(e)

    for e in (script or {}).get("key_entities") or []:
        add(e)
    for e in article.get("image_entities") or []:
        add(e)
    headline = article.get("headline") or article.get("title") or ""
    body_low = (article.get("body") or "").lower()
    for m in _PHRASE_RE.finditer(headline):
        # Headline phrases are headline-ese chopped by the regex
        # ("New York Bans Horse-Drawn Carriages") — keep only
        # phrases the article body itself repeats as a unit.
        phrase = _clean_entity(m.group(0))
        if phrase and phrase.lower() in body_low:
            add(phrase)
    # Frequent body phrases (2+ mentions) — single mentions are
    # too often sentence-initial noise.
    body = article.get("body") or ""
    counts = {}
    for m in _PHRASE_RE.finditer(body):
        k = m.group(0)
        counts[k] = counts.get(k, 0) + 1
    for phrase, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n >= 2:
            add(phrase)
    # A single-word entity from key_entities (e.g. 'Infosys') or
    # the slug's lead survives the phrase pass because add() ran
    # on the raw lists above; nothing more to do here.
    return out[:MAX_ENTITIES]


# Geographic-feature nouns: an entity carrying one is a PLACE,
# however person-shaped its name looks ("Central Park" is two
# capitalized tokens with no org word — the first production
# run classified it as a person and lost the subject queries).
_PLACE_TOKENS = {"park", "river", "lake", "lakes", "island",
                 "islands", "beach", "valley", "county", "bridge",
                 "square", "falls", "bay", "cape", "mount",
                 "fort", "port", "harbor", "harbour", "desert",
                 "canyon", "glacier", "volcano", "forest",
                 "peninsula", "strait", "peak", "peaks",
                 # 'house' / 'street': the picture pass's kind
                 # markers (its _KIND_PLACE_MARKERS lesson) —
                 # without them 'White House' and 'Main Street'
                 # read as people's names and take the person
                 # gates instead of the place gates.
                 "house", "street"}


def _looks_like_person(entity):
    toks = entity.split()
    if not (2 <= len(toks) <= 3):
        return False
    low = [t.lower().strip(".,") for t in toks]
    if any(t in _ORG_TOKENS or t in _PLACE_TOKENS for t in low):
        return False
    return all(re.fullmatch(r"[A-Z][A-Za-z.'\-]+", t) for t in toks)


_HINT_STOP = {
    "bans", "ban", "says", "said", "calls", "called", "wins", "won",
    "dies", "died", "honouring", "honoring", "announces",
    "announced", "launches", "launched", "unveils", "arrested",
    "charged", "charges", "seeks", "seek", "backs", "backed",
    "slams", "hails", "warns", "faces", "ends", "begins", "raises",
    "cuts", "drops", "rises", "falls", "found", "killed", "kills",
    "opens", "opened", "moves", "takes", "makes", "gets", "talks",
    "first", "after", "over", "under", "amid", "with", "from",
    "into", "their", "there", "will", "would", "than", "then",
}


def topical_hint(article, entities):
    """Up to 3 story-topic words from the headline (entity words
    and headline verbs removed). Turns a bare place search into a
    SUBJECT search: 'Central Park' + 'horse drawn carriages' is
    where the usable frames live (measured on the first
    production run: the bare 'Central Park' query's top hits
    were birds and scenery)."""
    headline = article.get("headline") or article.get("title") or ""
    ent = set()
    for e in entities:
        ent.update(entity_tokens(e))
    words = []
    for tok in re.findall(r"[a-z]+(?:'[a-z]+)?",
                          headline.lower().replace("-", " ")):
        base = tok[:-2] if tok.endswith("'s") else tok
        if len(base) < 4 or base in ent or base in _HINT_STOP:
            continue
        if base not in words:
            words.append(base)
        if len(words) >= 3:
            break
    return " ".join(words)


def queries_for(entity, hint=""):
    """Commons search queries for one entity, most topical first.
    People are searched by name only; orgs/places lead with the
    topical subject variant (the story is ABOUT something
    happening at the entity), then the bare name, then the
    building-oriented variants the test story proved out."""
    if _looks_like_person(entity):
        return [entity]
    qs = []
    if hint:
        qs.append(f"{entity} {hint}")
    qs.append(entity)
    qs += [f"{entity} headquarters", f"{entity} campus",
           f"{entity} building"]
    return qs


# ── network layer (injectable for tests) ────────────────────────────
def _curl(url, ua, timeout=25, dest=None):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "-A", ua]
    if dest:
        cmd += ["-o", str(dest)]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=timeout + 10)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed ({r.returncode}): "
                           f"{(r.stderr or '')[:160]}")
    return r.stdout


def commons_search(query, limit=10):
    """Commons API file search -> raw page dicts with imageinfo."""
    params = {
        "action": "query", "format": "json",
        "generator": "search", "gsrsearch": query,
        "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    data = json.loads(_curl(url, "TheVideshi/1.0"))
    pages = ((data or {}).get("query") or {}).get("pages") or {}
    return [p for p in pages.values() if p.get("imageinfo")]


def commons_file_info(title):
    """imageinfo for one File: title (route-C verification)."""
    params = {
        "action": "query", "format": "json",
        "titles": title, "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    data = json.loads(_curl(url, "TheVideshi/1.0"))
    pages = ((data or {}).get("query") or {}).get("pages") or {}
    for p in pages.values():
        if p.get("imageinfo"):
            return p
    return None


def brave_links(query, max_results=8):
    """Brave Search HTML result URLs (the image_sourcer-proven
    route: no API key, honors site:/quoted queries from this
    box). Discovery only — nothing is fetched from a result
    without passing the gates at the hosting page."""
    try:
        q = urllib.parse.quote(query)
        out_html = _curl(f"https://search.brave.com/search?q={q}",
                         UA_BROWSER, timeout=15)
    except Exception:
        return []
    links, seen = [], set()
    for link in re.findall(r'href="(https?://[^"]+)"', out_html or ""):
        try:
            host = urllib.parse.urlparse(link).netloc.lower()
        except Exception:
            continue
        if host.endswith("brave.com") or link in seen:
            continue
        if link.lower().split("?")[0].endswith(
                (".css", ".js", ".svg", ".ico", ".woff2")):
            continue
        seen.add(link)
        links.append(link)
        if len(links) >= max_results:
            break
    return links


def fetch_text(url, timeout=15):
    try:
        return _curl(url, UA_BROWSER, timeout=timeout) or ""
    except Exception:
        return ""


def download_file(url, dest):
    _curl(url, "TheVideshi/1.0", timeout=60, dest=dest)
    dest = Path(dest)
    if not dest.exists() or dest.stat().st_size < 10000:
        raise RuntimeError(f"download too small: {url}")


DEFAULT_NET = {"commons_search": commons_search,
               "commons_file_info": commons_file_info,
               "brave_links": brave_links,
               "fetch_text": fetch_text,
               "download": download_file,
               # The identity route (2026-10-31): entity
               # resolution + depicts candidates. source_extras
               # uses ONLY these two network seams plus
               # commons_file_info / download.
               "resolve_entity": ER.resolve,
               "depicts": ER.depicts_candidates}


# ── candidate evaluation ────────────────────────────────────────────
def _meta(info, key):
    return _strip_html(((info.get("extmetadata") or {}).get(key)
                        or {}).get("value") or "")


def evaluate_commons_page(page, entity, route, context=None,
                          identity_verified=False,
                          blocked_keys=None):
    """One Commons file page -> (candidate | None, ledger_row).
    The gates, in order: photograph type, title denylist, TRUE
    dimensions, license, identity at the file page — plus,
    when a story context is supplied, the shared identity
    gates (outlet / country contradiction / depicted person
    / person namesake; see context_reject_reason).

    identity_verified=True is the identity-route form
    (2026-10-31): the file reached us as the resolved entity's
    P18 or a depicts (P180) file OF the entity's Wikidata
    item, so identity is established by construction and the
    token-identity + story-context gates are skipped (they
    exist to police search hits, and their country scan would
    false-reject a verified file photographed abroad). Every
    other gate still runs — photograph type, denylist,
    dimensions, license, wildlife subject — plus the corpus
    blocklist: a file whose canonical key is in blocked_keys
    (the resolved registry entry's blocked_files) rejects even
    on this route, because the blocklist records files proven
    wrong for this entity in the failure corpus."""
    title = page.get("title") or ""
    info = (page.get("imageinfo") or [{}])[0]
    row = {"candidate": title, "route": route}

    def reject(reason):
        row.update({"verdict": "rejected", "reason": reason})
        return None, row

    if G.is_outlet_entity(entity):
        return reject(f"outlet: {entity!r} is a news outlet — "
                      "outlets are sources, never picture "
                      "subjects")
    if G.is_language_entity(entity):
        return reject(f"non-visual: {entity!r} is a language "
                      "name — languages are never picture "
                      "subjects")
    if blocked_keys and ER.file_key(title) in blocked_keys:
        return reject("blocklist: this file is on the entity's "
                      "corpus blocklist — proven wrong for "
                      f"{entity!r} in a prior run")
    if info.get("mime") not in ("image/jpeg", "image/png"):
        return reject(f"not a photograph file "
                      f"({info.get('mime') or 'unknown type'})")
    desc = _meta(info, "ImageDescription")
    cats = _meta(info, "Categories")
    if subject_denied(title, desc):
        return reject("title/description marks it as a logo/"
                      "diagram/map-type file, not a scene "
                      "photograph")
    w, h = info.get("width") or 0, info.get("height") or 0
    if not dims_ok(w, h):
        return reject(f"resolution: {w}x{h} — below the "
                      f"{MIN_EXTRA_W}x{MIN_EXTRA_H} floor; would "
                      f"force an upscale")
    ok, label = license_verdict(info.get("extmetadata"))
    if not ok:
        return reject(f"license: {label} — not CC / public domain")
    if not identity_verified and not identity_ok(
            entity, title, desc, cats):
        return reject(f"identity: the file page's description/"
                      f"categories do not evidence {entity!r}")
    if wildlife_subject(entity, cats):
        return reject("identity: the file's subject is wildlife "
                      "photographed AT the entity, not the "
                      "entity itself (species-marked categories)")
    if not identity_verified:
        reason = context_reject_reason(entity, title, desc, cats,
                                       context)
        if reason:
            return reject(reason)
    cand = {
        "entity": entity, "title": title,
        "file_url": info.get("url"), "size": [w, h],
        "source_page": info.get("descriptionurl")
        or ("https://commons.wikimedia.org/wiki/"
            + urllib.parse.quote(title.replace(" ", "_"))),
        "license": label,
        "artist": _meta(info, "Artist")[:80],
        "subject": (desc or title)[:240],
        "role": classify_role(title, desc),
        "route": route, "anchor": None,
    }
    row.update({"verdict": "accepted",
                "reason": f"{w}x{h}, {label}, "
                          + ("identity by construction "
                             "(P18/depicts of the resolved "
                             "Wikidata item)"
                             if identity_verified else
                             "identity evidenced on the file "
                             "page")})
    return cand, row


_CC_PD_RE = re.compile(
    r"(creative commons|cc[ -]by|cc0|public domain)", re.I)


def evaluate_hosted_page(url, entity, route, net, context=None):
    """Route B/C page gate: fetch the hosting page, find its lead
    image (og:image), and accept ONLY with a license basis —
    US federal .gov/.mil (public domain) or an explicit CC/PD
    statement on the page — plus identity evidence on the page
    and true dimensions at the downloaded file. Returns
    (candidate | None, ledger_row); the image itself is NOT
    downloaded here (dims verified at assignment download)."""
    row = {"candidate": url, "route": route}
    if G.is_outlet_entity(entity):
        row.update({"verdict": "rejected",
                    "reason": f"outlet: {entity!r} is a news "
                              "outlet — outlets are sources, "
                              "never picture subjects"})
        return None, row
    host = urllib.parse.urlparse(url).netloc.lower()
    page = net["fetch_text"](url)
    if not page:
        row.update({"verdict": "rejected",
                    "reason": "retrieval: page not fetchable"})
        return None, row
    og = re.search(r'property=["\']og:image["\']\s+content=["\']'
                   r'([^"\']+)', page) or re.search(
                       r'content=["\']([^"\']+)["\']\s+property='
                       r'["\']og:image["\']', page)
    if not og:
        row.update({"verdict": "rejected",
                    "reason": "no lead image (og:image) on the page"})
        return None, row
    img_url = urllib.parse.urljoin(url, og.group(1))
    img_name = urllib.parse.urlparse(img_url).path \
        .rsplit("/", 1)[-1]
    title_m = re.search(r"<title[^>]*>(.*?)</title>", page,
                        re.S | re.I)
    page_title = _strip_html(title_m.group(1)) if title_m else ""
    if subject_denied(page_title, img_name) \
            or title_denied(img_name):
        row.update({"verdict": "rejected",
                    "reason": "the page's lead image is a map/"
                              "diagram-type graphic, not a scene "
                              "photograph"})
        return None, row
    federal = host.endswith((".gov", ".mil"))
    if federal:
        basis = "US federal government work — public domain"
    elif _CC_PD_RE.search(page):
        basis = "explicit CC / public-domain statement on the page"
    else:
        row.update({"verdict": "rejected",
                    "reason": "license: no license grant on the "
                              "hosting page"})
        return None, row
    if not identity_ok(entity, page_title, page[:6000], ""):
        row.update({"verdict": "rejected",
                    "reason": f"identity: the page does not "
                              f"evidence {entity!r}"})
        return None, row
    if context:
        # Country/domain contradiction, hosted form: the
        # page title + lead-image name are the placement
        # evidence a hosted page offers (its body text is too
        # noisy to scan — navigation alone names countries).
        cand_countries = G.countries_in(
            f"{page_title} {img_name}")
        story_countries = context.get("countries") \
            or frozenset()
        if cand_countries and story_countries \
                and cand_countries.isdisjoint(story_countries):
            row.update({"verdict": "rejected",
                        "reason": "namesake/context: the page "
                                  "places its subject in "
                                  f"{'/'.join(sorted(cand_countries))}, "
                                  "which this story is not "
                                  "about — a namesake, not "
                                  f"{entity!r} in this story"})
            return None, row
    cand = {"entity": entity, "title": page_title or img_url,
            "file_url": img_url, "size": None,
            "source_page": url, "license": basis,
            "artist": "", "subject": (page_title or entity)[:240],
            "role": classify_role(page_title, ""),
            "route": route, "anchor": None,
            "needs_dims_check": True}
    row.update({"verdict": "accepted",
                "reason": f"license basis: {basis}; dimensions "
                          f"verified at download"})
    return cand, row


# ── beat assignment (editorial scoring) ─────────────────────────────
def _beat_texts(script, category):
    texts = {}
    for beat in _BEATS_NEEDING:
        try:
            texts[beat] = " ".join(R.SCENE_TEXTS[beat](script,
                                                       category))
        except Exception:
            texts[beat] = ""
    return texts


def _score(beat, cand, beat_text, topical_toks=frozenset()):
    """Relevance of one candidate for one beat: the entity is
    mentioned in the beat's text (directly or by known acronym),
    plus role affinity, plus description-token overlap, plus a
    title-subject bonus — the entity (or the story's topical
    words) as the file's TITLE subject outranks a passing
    mention scattered through a long description."""
    toks = set(_tokens(beat_text))
    score = 0
    ent = cand["entity"].lower()
    ent_toks = entity_tokens(cand["entity"])
    if ent_toks and all(t in toks for t in ent_toks):
        score += 10
    else:
        for alias in ALIASES.get(ent, ()):  # acronym in the text
            if alias in toks:
                score += 10
                break
    prefs = _BEAT_ROLES[beat]
    if cand["role"] in prefs:
        score += 6 - prefs.index(cand["role"])
    desc_toks = {t for t in _tokens(cand.get("subject") or "")
                 if len(t) >= 4}
    score += min(4, len(desc_toks & toks))
    title_toks = set(_tokens(cand.get("title") or ""))
    score += 2 * len(set(ent_toks) & title_toks)
    if topical_toks:
        score += 2 * len(topical_toks & title_toks)
    return score


def assign_beats(pool, script, category, need, topical=""):
    """Greedy best-first assignment: returns {beat: candidate}.
    At most one image per beat, at most PER_ENTITY_CAP images per
    entity, never more than `need` extras; a pair must clear the
    relevance bar (role affinity alone can qualify — the pool is
    entity-verified by construction)."""
    if need <= 0 or not pool:
        return {}
    texts = _beat_texts(script, category)
    topical_toks = {t for t in _tokens(topical) if len(t) >= 4}
    pairs = []
    for beat in _BEATS_NEEDING:
        for cand in pool:
            s = _score(beat, cand, texts[beat], topical_toks)
            if s >= 5:
                pairs.append((s, beat, cand))
    pairs.sort(key=lambda p: -p[0])
    assigned, used_c, used_e = {}, set(), {}
    for _s, beat, cand in pairs:
        if len(assigned) >= need:
            break
        if beat in assigned or id(cand) in used_c:
            continue
        if used_e.get(cand["entity"], 0) >= PER_ENTITY_CAP:
            continue
        assigned[beat] = cand
        used_c.add(id(cand))
        used_e[cand["entity"]] = used_e.get(cand["entity"], 0) + 1
    return assigned


# ── the ladder ──────────────────────────────────────────────────────
def source_extras(article, script, dest_dir, own_count, log=print,
                  net=None):
    """Run the sourcing ladder for one story. own_count = usable
    scene images the article itself supplies (hero + inlines).
    Downloads assigned files into dest_dir and returns the
    provenance dict. NEVER raises — any route failure is ledgered
    and the reel falls back to the hero chain."""
    net = {**DEFAULT_NET, **(net or {})}
    dest_dir = Path(dest_dir)
    slug = article.get("slug") or "reel"
    need = max(0, TARGET_DISTINCT - own_count)
    prov = {"built": "reel_entity_sourcing.py (production v7)",
            "story": slug,
            "trigger": {"own_images": own_count,
                        "target_distinct": TARGET_DISTINCT,
                        "extras_needed": need},
            "entities": [], "candidate_ledger": [], "extras": []}
    if need <= 0:
        log("   sourcing: article supplies enough images itself")
        return prov
    entities = extract_entities(article, script)
    prov["entities"] = entities
    if not entities:
        prov["candidate_ledger"].append(
            {"candidate": "(entity extraction)",
             "route": "all",
             "verdict": "rejected",
             "reason": "no picture-worthy entities extracted "
                       "from the article"})
        log("   sourcing: no entities extracted — hero chain only")
        return prov
    # The shared identity gates' story context, built once.
    context = build_story_context(article, script, entities)
    ledger = prov["candidate_ledger"]

    # ── Entity triage (2026-10-31): an entity may source ONLY
    # with a verified identity. In order: outlet (never a
    # picture subject) → language (non-visual, the card path's
    # rule ported via picture_gate_shared) → category label
    # (a body-phrase pseudo-entity equal to the article's own
    # category — 'Markets Finance' on a markets-finance story
    # is the section name, not a subject; it sourced a World
    # Bank panel portrait into two earnings reels) → shared
    # resolution through entity_resolve, with verified_
    # sourcer.decide()'s checks: unresolved → fail closed;
    # a LIVE resolution must bear the queried name
    # (names_agree; registry resolutions are exact by
    # construction and exempt); low-confidence + ambiguous →
    # abstain; resolved type language → non-visual; no QID →
    # no identity anchor, fail closed. Compound entities are
    # resolved AS WHOLES ('Sun Pictures' the studio) — nothing
    # here ever decomposes an entity into a bare token.
    ctx_parts = [article.get("headline") or article.get("title")
                 or "", article.get("summary") or "",
                 article.get("excerpt") or ""]
    for key in ("hook_line", "news_summary", "payoff"):
        if script.get(key):
            ctx_parts.append(str(script[key]))
    for b in script.get("diaspora_bullets") or []:
        ctx_parts.append(str(b))
    ctx_parts.append((article.get("body") or "")[:4000])
    resolve_context = " ".join(p for p in ctx_parts if p)
    category_toks = set(entity_tokens(
        str(article.get("category") or "").replace("-", " ")))
    resolved = {}
    sourceable = []
    for e in entities:
        def triage_reject(reason):
            ledger.append({"candidate": "(entity)",
                           "route": "identity — entity triage",
                           "verdict": "rejected",
                           "reason": reason})

        if G.is_outlet_entity(e):
            triage_reject(
                f"outlet: {e!r} is a news outlet — outlets are "
                "sources, never picture subjects; never queried")
            continue
        if G.is_language_entity(e):
            triage_reject(
                f"non-visual: {e!r} is a language name — "
                "languages are never picture subjects")
            continue
        if category_toks \
                and set(entity_tokens(e)) == category_toks:
            triage_reject(
                f"category label: {e!r} is this article's "
                "category name, not a picture subject")
            continue
        try:
            res = net["resolve_entity"](e, resolve_context)
        except Exception as ex:
            triage_reject(f"identity: resolution failed for "
                          f"{e!r} ({ex}) — fail closed"[:200])
            continue
        if not res:
            triage_reject(
                f"identity: {e!r} has no verified identity "
                "(no registry entry, no Wikidata resolution) "
                "— fail closed, no open-search fallback")
            continue
        method = res.get("method") or ""
        if not method.startswith("registry") \
                and not ER.names_agree(e, res.get("name"),
                                       res.get("aliases")):
            triage_reject(
                f"namesake: live resolution of {e!r} named "
                f"{res.get('name')!r}, which does not bear the "
                "queried name — not an identity; fail closed")
            continue
        if res.get("confidence") == "low" \
                and "ambiguous" in (res.get("notes") or ""):
            triage_reject(
                f"ambiguous: {e!r} is ambiguous between "
                "confusables and the story context did not "
                "discriminate — abstaining (fail closed)")
            continue
        if res.get("type") == "language":
            triage_reject(
                f"non-visual: {e!r} resolves to a language — "
                "languages are never picture subjects")
            continue
        if not res.get("qid"):
            triage_reject(
                f"identity: {e!r} has no Wikidata identity "
                "anchor (QID null) — identity routes "
                "unavailable; fail closed")
            continue
        resolved[e] = res
        sourceable.append(e)
    entities = sourceable
    if not entities:
        ledger.append(
            {"candidate": "(entity extraction)",
             "route": "identity — entity triage",
             "verdict": "rejected",
             "reason": "no extracted entity carried a verified "
                       "identity — nothing sourceable"})
        log("   sourcing: no identity-verified entities — "
            "hero chain only")
        return prov
    log(f"   sourcing: own={own_count} < {TARGET_DISTINCT} — "
        f"identity-verified entities: {', '.join(entities)}")
    pool = []
    seen_titles = set()   # a file is evaluated once per run,
                          # however many routes surface it

    def pool_full():
        return len(pool) >= min(MAX_POOL, need + 2)

    # ── Identity route: screened P18, then depicts ──
    # The ONLY candidate sources (2026-10-31): for each
    # identity-verified entity, its Wikidata item's P18 image
    # and the Commons files whose depicts (P180) statement IS
    # that item — identity by construction. Each file is
    # fetched by exact title and run through the file gates
    # (evaluate_commons_page with identity_verified=True plus
    # the entity's corpus blocklist). No text search of any
    # kind: a file that is not the resolved item's P18 or a
    # depicts file of it can never enter the pool.
    hint = topical_hint(article, entities)
    if hint:
        log(f"   sourcing: topical hint {hint!r}")
    try:
        for entity in entities:
            if pool_full():
                break
            res = resolved[entity]
            qid = res["qid"]
            blocked_keys = {ER.file_key(b)
                            for b in res.get("blocked_files")
                            or [] if ER.file_key(b)}
            cand_in = []
            p18 = res.get("p18_file")
            if p18:
                title = p18 if p18.startswith("File:") \
                    else "File:" + p18
                cand_in.append(
                    (title, f"identity — Wikidata P18 ({qid})"))
            try:
                deps = net["depicts"](qid) or []
            except Exception as ex:
                ledger.append(
                    {"candidate": f"depicts lookup ({qid})",
                     "route": "identity — depicts",
                     "verdict": "rejected",
                     "reason": f"depicts lookup failed: {ex}"[:200]})
                deps = []
            for d in deps:
                t = d.get("title") if isinstance(d, dict) \
                    else None
                if t:
                    cand_in.append(
                        (t, f"identity — depicts (P180={qid})"))
            got_for_entity = 0
            for title, route in cand_in:
                if pool_full() \
                        or got_for_entity >= PER_ENTITY_CAP:
                    break
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                try:
                    page = net["commons_file_info"](title)
                except Exception:
                    page = None
                if not page:
                    ledger.append(
                        {"candidate": title, "route": route,
                         "verdict": "rejected",
                         "reason": "file info unavailable on "
                                   "Commons — cannot verify the "
                                   "file; fail closed"})
                    continue
                cand, row = evaluate_commons_page(
                    page, entity, route, context=context,
                    identity_verified=True,
                    blocked_keys=blocked_keys)
                ledger.append(row)
                if cand:
                    cand["_row"] = row
                    pool.append(cand)
                    got_for_entity += 1
    except Exception as e:                      # never block the reel
        ledger.append({"candidate": "(identity route)",
                       "route": "identity — P18/depicts",
                       "verdict": "rejected",
                       "reason": f"route error: {e}"[:200]})

    # ── assignment + download (true dims verified at the file) ──
    category = str(article.get("category") or "News") \
        .replace("-", " ").title()
    assigned = assign_beats(pool, script, category, need,
                            topical=hint)
    dest_dir.mkdir(parents=True, exist_ok=True)
    used_labels = set()
    for beat in _BEATS_NEEDING:
        cand = assigned.get(beat)
        if not cand:
            continue
        base = slugify(cand["title"].replace("File:", "")
                       .rsplit(".", 1)[0])
        label, n = base, 2
        while label in used_labels:
            label = f"{base}-{n}"
            n += 1
        used_labels.add(label)
        ext = Path(urllib.parse.urlparse(
            cand["file_url"]).path).suffix or ".jpg"
        fname = f"{label}{ext.lower()}"
        dest = dest_dir / fname
        try:
            net["download"](cand["file_url"], dest)
            from PIL import Image
            with Image.open(dest) as im:
                true_size = list(im.size)
        except Exception as e:
            ledger.append(
                {"candidate": cand["title"], "route": cand["route"],
                 "verdict": "rejected",
                 "reason": f"download/verify failed: {e}"[:200]})
            continue
        if not dims_ok(*true_size):
            ledger.append(
                {"candidate": cand["title"], "route": cand["route"],
                 "verdict": "rejected",
                 "reason": f"resolution at the file: "
                           f"{true_size[0]}x{true_size[1]} — below "
                           f"the floor"})
            continue
        row = cand.get("_row")
        if row is not None:
            row["verdict"] = f"USED ({beat})"
        entry = {"beat": beat, "label": label, "path": fname,
                 "size": true_size, "role": cand["role"],
                 "subject": cand["subject"],
                 "route": cand["route"],
                 "source_page": cand["source_page"],
                 "file_url": cand["file_url"],
                 "license": cand["license"],
                 "artist": cand.get("artist") or ""}
        if cand.get("anchor"):
            entry["anchor"] = cand["anchor"]
        prov["extras"].append(entry)
        log(f"   sourcing: {beat} ← {label} "
            f"({true_size[0]}x{true_size[1]}, {cand['license']})")
    if not prov["extras"]:
        log("   sourcing: no supplementary image cleared the "
            "gates — hero chain only")
    return prov
