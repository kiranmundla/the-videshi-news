#!/usr/bin/env python3
"""
article_picture_pass.py — enricher-side article picture pass.

Brings the Reels v7 entity-sourcing standard (reel_entity_sourcing.py,
Kiran's doctrine, 2026-10-24) to ARTICLE images: pictures tied to the
article's ENTITIES, sourced through the same hardened ladder, with a
provenance ledger for every proposal.

WHAT IT DOES per published article (last N hours, default 12, max 30):
  1. Extracts + ranks picture-worthy entities (headline-named first,
     then the article's image_entities when sane, then frequent body
     proper nouns). Generic/category entities are skipped.
  2. HERO — acts ONLY when the hero is missing, broken, a Pexels URL,
     or a generic stock/og image. A verified hero is never replaced
     and a replacement never downgrades resolution. Floor: accept
     >=1200px wide, prefer >=1920px originals.
  3. INLINES — when the body has <2 inline figures, sources up to 2–3
     entity pictures (>=800px) and places them with the enricher's
     own insert_inline_images() (after the intro, spread across H2
     sections, never clustered, never before the first paragraph),
     with factual two-sentence captions in the enricher's format.

GATES (never relaxed — inherited from the reel ladder + sourcer):
  * Provably the named entity or skip: the entity must be the file's
    SUBJECT, evidenced on the file's own page (Commons title /
    description / categories), with the phrase-contiguity rule for
    3+ token names and the wildlife-subject denial.
  * License clean or skip: CC / public domain only (official US
    federal .gov/.mil = PD, or an explicit CC/PD statement on the
    hosting page). Attribution is recorded for every proposal.
  * Named-person gates are absolute: exact-name verification only —
    person_images cache (already-verified portraits), Commons files
    whose page evidences the exact name, and (under --apply only)
    image_sourcer's Source 3.8 person-profile lookup. No photo found
    means an empty slot, honestly logged — never a stock stand-in.
  * image_backfill_blocked=true articles are NEVER touched (the
    intentional-null payload convention): the whole article is
    skipped before any probing or sourcing.
  * No AI images, no Pexels/stock for named entities, true
    dimensions verified at the downloaded file.
  * Hero subject gate (2026-10-26): a hero is sourced ONLY
    for headline-subject entities (headline-named or the
    writer's image_entities) — never for body-only mentions,
    quoted analysts/sources, or place mentions on a story
    about something else; no subject picture means an honest
    miss. Entity hygiene: no entity may span a sentence
    boundary or a possessive, end on a stopword or a
    possessive form, or be a news outlet. Era gate: a file
    dated (in its title) to a different year than the
    headline's story, or marked archival, is a different
    event — rejected for current stories. An inline never
    duplicates the hero, another inline, or a picture the
    body already carries.

MODES:
  --dry-run (DEFAULT) — writes .state/picture-pass-report.json and
    .state/picture-pass-report.html and makes ZERO writes to
    Supabase. (The person-profile route is not even attempted in
    dry-run: on success it uploads to storage and caches into
    person_images — both writes. It is logged as deferred-to-apply.)
  --apply — PATCHes hero (image_url/image_caption/image_attribution)
    and body (inline figures) for the proposals that cleared the
    gates. Built for the enricher cron; run only on Kiran's go.

Supabase access is curl-subprocess only (urllib/requests fail
through this box's proxy). Scratch/downloads live in
pipeline/.state/ (never /tmp — 512MB ramdisk).
"""
import argparse
import html as html_lib
import json
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_entity_sourcing as RES
import image_sourcer as IS
# The identity gates shared with the reel sourcer live in
# picture_gate_shared.py (single source of truth since
# 2026-10-27 — the reel sourcer never had them, which is how
# it sourced Perm, Russia for a US immigration story). They
# are imported back under their historical private names so
# nothing else in this module changes.
from picture_gate_shared import (
    OUTLET_ENTITIES as _OUTLET_ENTITIES,
    HINT_FUNCTION_WORDS as _HINT_FUNCTION_WORDS,
    PERSON_DOMAIN_TOKENS as _PERSON_DOMAIN_TOKENS,
    ctx_token_match as _ctx_token_match,
    domain_contradiction_markers as
    _domain_contradiction_markers,
    title_core as _title_core,
    head_segment as _head_segment,
)
import picture_gate_shared as _SHARED_GATES

STATE_DIR = Path(__file__).resolve().parent / ".state"
DOWNLOAD_DIR = STATE_DIR / "picture-pass-downloads"

# ── floors / caps ───────────────────────────────────────────────────
HERO_MIN_W = 1200          # accept floor for a hero proposal
HERO_PREF_W = 1920         # preferred (Cards v1 full-bleed line)
HERO_MIN_H = 500
HERO_SITE_FLOOR_W = 800    # image_sourcer's own hero quality bar —
                           # a live hero below it fails the site bar
INLINE_MIN_W = 800
INLINE_MIN_H = 450
MAX_ENTITIES = 6
MAX_INLINE_TOTAL = 3       # figures per article after the pass
MIN_ARTICLE_WORDS = 350    # shorter pieces don't get inlines
PER_ENTITY_INLINE_CAP = 1  # inlines spread across entities
MAX_SERVE_BYTES = 8 * 1024 * 1024  # web budget for a SERVED file:
# a pick whose original exceeds it is compress-and-kept — host
# variant (Wikimedia 1920px thumb) first, else self-compressed
# and self-hosted; rejected only if both fail. Originals-at-
# any-size are a reels-render rule, never a served-article rule
# (the 2026-10-25 Cyclone Arnab hero was a topical but ~105 MB
# original GIF).
SERVE_THUMB_W = 1920

# Category labels that show up as junk in image_entities (the
# Romanch ledger's "Nri World" finding) + generic non-entities.
_CATEGORY_JUNK = {
    "news", "entertainment", "sports", "technology",
    "markets finance", "markets-finance", "nri world", "nri-world",
    "immigration", "lifestyle health", "lifestyle-health",
    "travel", "food", "india news", "world news", "the videshi",
    "indian diaspora", "united states", "india",
}


# ── Supabase (curl only) ────────────────────────────────────────────
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def _headers():
    return ["-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}"]


def fetch_recent_articles(hours=12, limit=30):
    """Published articles from the last `hours`, newest first."""
    since = (datetime.now(timezone.utc)
             - timedelta(hours=hours)).isoformat()
    params = {
        "select": "id,headline,slug,category,image_url,image_caption,"
                  "image_attribution,body,image_entities,"
                  "image_backfill_blocked,published_at,sources",
        "status": "eq.published",
        "published_at": f"gte.{since}",
        "order": "published_at.desc",
        "limit": str(limit),
    }
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles?"
           + urllib.parse.urlencode(params))
    r = subprocess.run(["curl", "-sS", "--max-time", "60", url]
                       + _headers(),
                       capture_output=True, text=True, timeout=70)
    if r.returncode != 0:
        raise RuntimeError(f"article fetch failed: {r.stderr[:200]}")
    return json.loads(r.stdout or "[]")


def patch_article(article_id, payload):
    """The ONLY write path. Called exclusively under --apply."""
    r = subprocess.run(
        ["curl", "-sS", "-X", "PATCH",
         f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload), "-o", "/dev/null",
         "-w", "%{http_code}"] + _headers(),
        capture_output=True, text=True, timeout=30)
    return (r.stdout or "").strip() in ("200", "204")


# ── entity hygiene (2026-10-26 live-run guards) ────────────────────
# The Oct 25–26 runs kept sourcing from BROKEN entities: a
# fragment spanning a sentence boundary ('Reuters. The' — the
# phrase regex's token pattern swallows the period), a fragment
# spanning a possessive ("Secret Toronto" out of "Victoria's
# Secret Toronto"), possessive FORMS standing as names
# ("New Zealand's"), and news OUTLETS standing as subjects
# (a Reuters vehicle photo + the Reuters Building, sourced for
# the entity 'Reuters'). None of these may ever be sourced.
# The outlet set itself is _OUTLET_ENTITIES, imported from
# picture_gate_shared.py at the top of this module.

# An entity may not BEGIN or END on a function word ('... of',
# 'The ...' leftovers): those are phrase fragments, not names.
_EDGE_STOPWORDS = {"the", "a", "an", "of", "in", "on", "at",
                   "to", "and", "for", "by", "with", "from"}


def _entity_hygiene_reject(name):
    """Why this entity string may never be sourced, or None.
    Pure string rules (the possessive-span rule needs the
    article text — see _possessive_fragment)."""
    if not name:
        return "empty entity"
    # Sentence-boundary span — but honorifics and initials
    # ('Dr. Arun Raghavan', 'U.S. Congress', 'Yvette D.
    # Clarke') carry periods that end no sentence: mask
    # them before the check.
    probe = re.sub(r"\b(?:Dr|Mr|Mrs|Ms|St|Prof|Sr|Jr|Mt|Ft|"
                   r"Gen|Sen|Rep|Gov|Capt|Lt|Col)\.", "X", name)
    probe = re.sub(r"\b[A-Z]\.", "X", probe)
    if re.search(r"[.!?]\s+[A-Za-z]", probe):
        return ("entity spans a sentence boundary "
                f"({name!r}) — a fragment, not a name")
    low = name.strip().lower()
    if low in _OUTLET_ENTITIES or \
            low.removeprefix("the ") in _OUTLET_ENTITIES:
        return (f"{name!r} is a news outlet — outlets are "
                "sources, never picture subjects")
    toks = name.split()
    if toks:
        first = toks[0].strip(".,'’-").lower()
        last = toks[-1].strip(".,'’-").lower()
        if first in _EDGE_STOPWORDS or last in _EDGE_STOPWORDS:
            return (f"entity {name!r} begins or ends on a "
                    "stopword — a phrase fragment, not a name")
        if toks[-1].lower().endswith(("'s", "’s")):
            return (f"entity {name!r} is a possessive form — "
                    "the possessed name is the entity, not "
                    "its owner fragment")
    return None


def _possessive_fragment(name, texts):
    """True when EVERY verbatim occurrence of `name` in the
    article texts sits immediately after a possessive 's —
    the 'entity' is the tail of a possessive phrase
    ('Secret Toronto' occurs only inside "Victoria's Secret
    Toronto"). A name that also occurs standing on its own
    is a real entity."""
    occ = 0
    for t in texts:
        if not t:
            continue
        i = t.find(name)
        while i != -1:
            occ += 1
            if t[max(0, i - 3):i] not in ("'s ", "’s "):
                return False
            i = t.find(name, i + 1)
    return occ > 0


_ATTR_VERBS = ("said", "says", "told", "according to", "noted",
               "argued", "wrote", "explained", "added",
               "pointed out", "estimates", "expects", "warned",
               "urged", "claimed", "observed", "reckons")


def _is_quoted_source(name, body_text):
    """True when every mention of `name` in the body sits
    inside quotation marks or beside an attribution verb —
    the person is a QUOTED SOURCE (an analyst cited for a
    view), not the story's subject. Quoted sources are never
    hero subjects (the redistricting story's hero was sourced
    to a photo keyed to its quoted analyst)."""
    if not name or not body_text:
        return False
    starts = [m.start()
              for m in re.finditer(re.escape(name), body_text)]
    if not starts:
        return False
    for i in starts:
        window = body_text[max(0, i - 90):i + len(name) + 90]
        low = window.lower()
        if any(v in low for v in _ATTR_VERBS):
            continue
        if any(q in window for q in ('"', "“", "”", "‘", "’")):
            continue
        return False
    return True


# ── entity extraction + ranking (pure) ──────────────────────────────
def _sane_image_entity(raw):
    """image_entities is trusted only when sane: a clean short
    proper-name string, not a category label or generic phrase
    (the Romanch ledger carried 'Nri World' as an 'entity')."""
    if not isinstance(raw, str):
        return None
    e = RES._clean_entity(raw)
    if not e or e.lower() in _CATEGORY_JUNK:
        return None
    if len(e) > 60 or len(e.split()) > 5 or "/" in e:
        return None
    if _entity_hygiene_reject(e):
        return None
    return e


# Single capitalized headline tokens are entities only when the
# body repeats them capitalized (a name/place, not a headline
# verb) and they are not generic role/institution words.
_SINGLE_TOKEN_STOP = {
    "centre", "center", "government", "court", "minister",
    "ministers", "team", "city", "state", "states", "indian",
    "india", "first", "second", "third", "final", "grand",
    "national", "federal", "supreme", "high", "prime", "chief",
    "home", "world", "global", "annual", "special", "royal",
    "american", "british", "with", "where", "when", "while",
    "here", "there", "this", "that", "more", "most", "many",
    "after", "before", "under", "over", "amid", "about",
}

# Extracted phrases built on function words are headline-ese,
# not entities ('Kid Again', 'Feels Like' from a Diwali-parcel
# headline) — left in, they source literal junk photos.
_PHRASE_TOKEN_DENY = {"again", "like", "yesterday", "tomorrow"}

# Place/org marker tokens: RES._looks_like_person reads ANY two
# Title Case words as a person's name — including 'Main
# Street', 'White House', 'Magic Kingdom', 'Diwali Dance Fest'
# (validation run 3: all classified 'person', which exempted
# them from the topicality gate). A marker token settles kind.
_KIND_PLACE_MARKERS = {
    "street", "house", "park", "road", "square", "bridge",
    "castle", "kingdom", "centre", "center", "temple", "church",
    "station", "airport", "university", "museum", "palace",
    "tower", "gate", "hall", "garden", "gardens", "beach",
    "island", "islands", "river", "lake", "mount", "fort",
    "stadium", "arena", "hotel", "mall", "market", "port",
    "bay", "falls", "valley", "desert", "forest", "harbour",
    "harbor", "news", "fest", "festival", "school", "college",
    "hospital", "library", "theatre", "theater", "zoo",
    # Indian states/UTs and their distinctive tokens: 'Tamil
    # Nadu' and 'Andhra Pradesh' are two Title Case words, so
    # the person heuristic claimed them — and as 'persons' they
    # were EXEMPT from the topicality and subject gates, which
    # is how a silk-dyeing photo and an art collage were
    # proposed for them in the post-hardening dry-run.
    "nadu", "pradesh", "bengal", "kashmir", "punjab",
    "gujarat", "karnataka", "kerala", "maharashtra",
    "rajasthan", "odisha", "assam", "bihar", "haryana",
    "jharkhand", "chhattisgarh", "telangana", "manipur",
    "meghalaya", "mizoram", "nagaland", "sikkim", "tripura",
    "uttarakhand", "goa", "delhi", "ladakh", "puducherry",
    "india",
}


# ── fragment entities (never sourced) ───────────────────────────────
# A grade/class label is a fragment, not a picture-worthy entity:
# 'Class XII' was sourced in the first live run (2026-10-25) and
# matched a photo of the Louis XII wing at Blois — 'xii' via the
# king's name, 'class' via the French 'classé' in the file's
# heritage description. Numerals and generic label words carry
# no identity.
_FRAGMENT_HEADS = {"class", "grade", "standard", "std", "form",
                   "level", "part", "phase", "round"}


def _is_numeral_token(tok):
    if tok.isdigit():
        return True
    return bool(tok) and len(tok) <= 6 \
        and all(c in "ivxlcdm" for c in tok)


def _is_fragment_entity(name):
    toks = RES.entity_tokens(name)
    if not toks:
        return True
    if toks[0] in _FRAGMENT_HEADS:
        return all(_is_numeral_token(t) or t in _FRAGMENT_HEADS
                   for t in toks[1:])
    return any(_is_numeral_token(t) for t in toks) and all(
        _is_numeral_token(t) or t in _FRAGMENT_HEADS
        for t in toks)


def extract_article_entities(article):
    """Ranked picture-worthy entities for one article:
    headline-named first, then sane image_entities, then frequent
    body proper nouns. Returns [{name, kind, source}] with kind in
    {person, org/place} (RES._looks_like_person)."""
    out, seen = [], set()

    def add(name, source):
        name = RES._clean_entity(name) if name else None
        if not name:
            return
        if name.lower() in _CATEGORY_JUNK:
            return
        if _entity_hygiene_reject(name):
            return
        if _possessive_fragment(name, (headline, body_text)):
            return
        if source != "image_entities" and any(
                t.strip(".,'’-").lower() in _PHRASE_TOKEN_DENY
                for t in name.split()):
            return
        k = name.lower()
        if k in seen:
            # A curated image_entities entry upgrades an
            # extracted duplicate in place (curation beats
            # extraction — it restores sourceability for a
            # single-token company name).
            if source == "image_entities":
                for prev in out:
                    if prev["name"].lower() == k:
                        prev["source"] = "image_entities"
                        prev["sourceable"] = \
                            not _is_fragment_entity(name)
            return
        # A fuller name supersedes a bare surname token added
        # earlier ('Modi' -> 'Narendra Modi').
        if len(name.split()) > 1:
            last = name.split()[-1].lower()
            for prev in list(out):
                if prev["name"].lower() == last:
                    out.remove(prev)
                    seen.discard(last)
        seen.add(k)
        # Single tokens from headline/body extraction are
        # fragments or common words ('Mann' from 'Mann Ki Baat',
        # 'Host', 'American') — a lone token in a file's evidence
        # is NOT identity proof, so they are recorded but never
        # sourced. Curated image_entities single tokens (a real
        # company name, e.g. 'Infosys') stay sourceable.
        sourceable = (len(name.split()) > 1 or source == \
            "image_entities") and not _is_fragment_entity(name)
        kind = "person" if RES._looks_like_person(name) \
            else "org/place"
        if kind == "person" and any(
                t.strip(".,'’-").lower() in _KIND_PLACE_MARKERS
                for t in name.split()):
            kind = "org/place"
        out.append({
            "name": name,
            "kind": kind,
            "source": source,
            "sourceable": sourceable,
        })

    headline = article.get("headline") or ""
    body = article.get("body") or ""
    body_text = RES._strip_html(body)
    # 1. Headline phrases the body itself repeats as a unit, with
    #    the SAME capitalization (the reel extractor's guard is
    #    case-insensitive; on articles that leaks headline-ese —
    #    'Coming Weeks' matched the body's lowercase 'coming
    #    weeks' and briefly became an 'entity').
    for m in RES._PHRASE_RE.finditer(headline):
        phrase = RES._clean_entity(m.group(0))
        if phrase and phrase in body_text:
            add(phrase, "headline")
    # 1b. Single capitalized headline tokens the body repeats
    #     capitalized (Dhoni, Bhubaneswar, Modi).
    body_caps = {}
    for tok in re.findall(r"\b[A-Z][A-Za-z.'\-]{3,}\b", body_text):
        body_caps[tok] = body_caps.get(tok, 0) + 1
    for tok in re.findall(r"\b[A-Z][A-Za-z.'\-]{3,}\b", headline):
        if tok.lower() in _SINGLE_TOKEN_STOP:
            continue
        if body_caps.get(tok, 0) >= 1:
            add(tok, "headline")
    # 2. image_entities, when sane.
    for e in article.get("image_entities") or []:
        sane = _sane_image_entity(e)
        if sane:
            add(sane, "image_entities")
    # 3. Frequent body phrases (2+ mentions).
    counts = {}
    for m in RES._PHRASE_RE.finditer(RES._strip_html(body)):
        counts[m.group(0)] = counts.get(m.group(0), 0) + 1
    for phrase, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        if n >= 2:
            add(phrase, "body")
    # Fragment suppression: an entity whose tokens are a strict
    # subset of another's is a phrase fragment, not an entity
    # ('Mann'/'Baat' inside 'Mann Ki Baat', 'Aamir' inside
    # 'Aamir Khan').
    tok_sets = [(e, set(RES.entity_tokens(e["name"]))) for e in out]
    kept = []
    for e, toks in tok_sets:
        if toks and any(other is not e and toks < otoks
                        for other, otoks in tok_sets):
            continue
        kept.append(e)
    # Quoted-source tag: a person the body only QUOTES (an
    # analyst cited for a view) is not the story's subject —
    # the hero gate refuses them even if they rank highly.
    for e in kept:
        e["quoted_source"] = e["kind"] == "person" and \
            _is_quoted_source(e["name"], body_text)
    return kept[:MAX_ENTITIES]


# ── hero state classification (pure, given a probe) ─────────────────
def _is_pexels(url):
    try:
        return urllib.parse.urlparse(url or "").netloc.lower() \
            .endswith("pexels.com")
    except Exception:
        return False


def classify_hero(article, probe):
    """Decide the hero action. probe = None when there is no URL,
    else {ok, width, height} from a download verification.
    Returns (action, reason); action in
    {skip-blocked, fill, replace, keep}. A verified hero is never
    replaced; broken / Pexels / generic-stock / below-the-site-bar
    heroes are the only replacements."""
    if article.get("image_backfill_blocked"):
        return "skip-blocked", "image_backfill_blocked=true — " \
                                "intentional null, never touched"
    url = article.get("image_url")
    if not url:
        return "fill", "no hero image"
    if _is_pexels(url):
        return "replace", "hero is a Pexels URL (stock — sourcer " \
                          "policy replaces Pexels heroes)"
    if "upload.wikimedia.org" not in url \
            and IS._is_generic_og_image(url):
        # IS._is_generic_og_image is an og-scrape heuristic (it
        # blanket-rejects .gif as tracking-pixel class). A
        # Wikimedia Commons file URL is curated content, not an
        # og scrape — the reviewer's captioned Cyclone Mocha
        # satellite GIF hero was misclassified 'generic' by the
        # .gif rule and marked for replacement.
        return "replace", "hero is a generic og/stock image " \
                          "(root social filename / blocklist)"
    if probe is not None:
        if not probe.get("ok"):
            return "replace", "hero URL is broken (download/PIL " \
                              "verification failed)"
        w = probe.get("width") or 0
        if w and w < HERO_SITE_FLOOR_W:
            return "replace", f"hero is {w}px wide — below the " \
                              f"site's {HERO_SITE_FLOOR_W}px hero " \
                              f"quality bar"
    return "keep", "hero present and verified — never replaced"


def hero_width_floor(current_width):
    """Minimum width a replacement hero must clear: the accept
    floor, raised so a replacement never downgrades resolution
    (capped at the preferred width — a 4000px original does not
    force a 4000px replacement)."""
    if not current_width:
        return HERO_MIN_W
    return max(HERO_MIN_W, min(current_width, HERO_PREF_W))


# ── candidate evaluation (reel gates, article floors) ───────────────
# (_HINT_FUNCTION_WORDS is imported from picture_gate_shared.py.)


def _story_hint_terms(article, entity_name, all_entities=None):
    """Topical vocabulary of the story: headline content words
    (headline verbs and function words stopped, pure numbers
    dropped) plus the tokens of the article's OTHER entities,
    minus this entity's own tokens. A non-person candidate's
    file evidence must share at least TWO of these (one when
    the story offers fewer than three) — exact-token identity
    alone let Gibraltar's Main Street illustrate Disney World
    and the RUSSIAN White House illustrate US midterms in
    validation (the name matched, the subject did not), and a
    Christmas tree passed on the single word 'where'. Persons
    are exempt (the caller passes an empty set): an exact-name
    verified portrait of a person the story names is on-topic
    by construction."""
    toks = set()
    for w in re.findall(r"[a-z0-9]+",
                        (article.get("headline") or "").lower()):
        if len(w) >= 4 and not w.isdigit() \
                and w not in RES._HINT_STOP \
                and w not in _HINT_FUNCTION_WORDS:
            toks.add(w)
    for other in (all_entities or []):
        oname = other["name"] if isinstance(other, dict) else other
        if oname and oname.lower() != (entity_name or "").lower():
            for t in RES.entity_tokens(oname):
                if len(t) >= 4 and t not in _HINT_FUNCTION_WORDS:
                    toks.add(t)
    return toks - set(RES.entity_tokens(entity_name))


# ── person namesake gate (2026-10-25, second live-run lesson) ─────
# Persons were EXEMPT from topicality on the theory that an
# exact-name portrait is on-topic by construction. Namesakes break
# it: the Commons file for Shadab Khan the Indian ACTOR passes
# exact-name identity perfectly for a story about Shadab Khan the
# Pakistani CRICKETER (and in Oct a businessman Abhishek Sharma
# illustrated the cricketer of the same name). A Commons person
# candidate must therefore ALSO agree with the story's context:
# at least one context token — headline/other-entity vocabulary
# or the article category's domain vocabulary — must appear in
# the file's own evidence. No agreement (or no context at all)
# means Commons cannot distinguish this person from a namesake:
# reject, and let the verified routes (person cache, Source 3.8
# profile lookup) or an honest miss carry the story instead.
# (_PERSON_DOMAIN_TOKENS is imported from
# picture_gate_shared.py at the top of this module.)


def _person_context_terms(article, entity_name, all_entities=None):
    """Context vocabulary for the person namesake gate: the
    story's hint terms (headline content words + other entities'
    tokens, this entity's own tokens removed) plus the domain
    vocabulary of the article's category."""
    toks = set(_story_hint_terms(article, entity_name,
                                 all_entities=all_entities))
    cat = (article.get("category") or "").strip().lower()
    toks.update(_PERSON_DOMAIN_TOKENS.get(cat, ()))
    for t in re.findall(r"[a-z]+", cat):
        if len(t) >= 4:
            toks.add(t)
    return frozenset(toks)


# (_ctx_token_match is imported from picture_gate_shared.py.)


# ── subject gates (2026-10-25 live-run hardening) ───────────────────
# The first live run applied junk that the token gates had all
# passed, because identity_ok() counts the entity's tokens
# ANYWHERE in the file evidence (title + description +
# categories pooled): a file merely LOCATED at the entity (a
# crow photographed in Tamil Nadu), a file whose categories
# mention the entity while its subject is a person (a portrait
# of Bryan Traynor, filed under Breakthrough Prize winners), a
# namesake building in another city (Bangalore's Raj Bhavan,
# renamed Lok Bhavan, for Manipur's Lok Bhavan), and a fragment
# entity whose tokens collide with unrelated words ('Class XII'
# -> the Louis XII wing at Blois). The gates below require the
# evidence to establish the entity as the file's SUBJECT.

_GRAPHIC_MARKERS = ("openstreetmap", "overpass", "mandal",
                    "maps of ", "map of ")


def _phrase_span(toks, stream):
    """Start index of the entity's tokens as a contiguous run in
    the (stopword-filtered) token stream, else None."""
    if not toks:
        return None
    for i in range(len(stream) - len(toks) + 1):
        if stream[i:i + len(toks)] == toks:
            return i
    return None


# (_title_core and _head_segment are imported from
# picture_gate_shared.py.)


def _phrase_is_trailing_location(toks, text):
    """The phrase's only occurrence in the text is a trailing
    location phrase — '... in Kumbakonam, Tamil Nadu' at the
    very end (at most digit tokens after it, e.g. a file's
    serial number). That is a location mention, not the
    subject."""
    raw = re.findall(r"[a-z0-9]+", (text or "").lower())
    for i in range(len(raw) - len(toks) + 1):
        if raw[i:i + len(toks)] == toks:
            return i > 0 and raw[i - 1] == "in" and all(
                t.isdigit() for t in raw[i + len(toks):])
    return False


def _subject_position_ok(entity, title, desc):
    """The entity must be the file's SUBJECT, evidenced by its
    full token phrase in subject position:
      * inside the title's head segment ('Dr. Ashoke Sen at
        Scottish Church College', 'Umhlanga Rocks'), or
      * in the title following a year — participation at a
        dated event ('Aremi Fuentes Zavala ... at the 2019
        World Weightlifting Championships'), or
      * in the first sentence of the description
        ('Alexander Stadium at the opening ceremony to
        Birmingham 2022 Commonwealth Games').
    A phrase that appears only in a trailing location phrase
    ('Crow in Tamil Nadu'), only in categories, or nowhere in
    title/description subject positions does not qualify."""
    toks = RES.entity_tokens(entity)
    if not toks:
        return False
    core = _title_core(title)
    head = _head_segment(core)
    if _phrase_span(toks, RES._tokens(head)) is not None \
            and not _phrase_is_trailing_location(toks, head):
        return True
    stream = RES._tokens(core)
    span = _phrase_span(toks, stream)
    if span is not None and span > 0 \
            and re.fullmatch(r"(19|20)\d{2}", stream[span - 1]):
        # Participation at a dated event: the phrase directly
        # follows the year ('... at the 2019 World
        # Weightlifting Championships'). A year elsewhere in
        # the title ('Crow in Tamil Nadu, 2024') is not this.
        return True
    first_sentence = re.split(r"(?<=[.!?])\s+",
                              RES._strip_html(desc) or "",
                              maxsplit=1)[0]
    return _phrase_span(toks, RES._tokens(first_sentence)) \
        is not None and not _phrase_is_trailing_location(
            toks, first_sentence)


def _depicted_person_name(title, entity):
    """When the file's title head is a portrait-style person
    name (2–4 capitalized words, optionally led by an honorific)
    that is NOT the entity, return the name. A posed portrait
    of a specific person cannot illustrate a non-person entity
    merely because the person is associated with it (Bryan
    Traynor for 'Breakthrough Prize'). The heuristic itself
    lives in picture_gate_shared.py (shared with the reel
    sourcer); this wrapper pins the tokeniser to
    RES.entity_tokens, as before."""
    return _SHARED_GATES.depicted_person_name(
        title, entity, RES.entity_tokens)


def _desc_binomial_subject(desc, entity):
    """A parenthesised Latin binomial in the description —
    'Crow (Corvus splendens) in Tamil Nadu' — names the file's
    true subject: a species, not the story entity."""
    m = re.search(r"\(([A-Z][a-z]+ [a-z]{3,})\)",
                  RES._strip_html(desc) or "")
    if not m:
        return None
    if set(RES._tokens(m.group(1))) & set(
            RES.entity_tokens(entity)):
        return None
    return m.group(1)


def _wikimedia_thumb_url(url, width):
    """The <=width px served variant of a Wikimedia original:
    .../commons/a/ab/Name.ext -> .../commons/thumb/a/ab/
    Name.ext/<width>px-Name.ext. None when the URL is not a
    Commons original (already a thumb, or another host)."""
    if not url:
        return None
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/"
                 r"commons)/([0-9a-f])/([0-9a-f]{2})/([^/?#]+)$",
                 url.split("?")[0])
    if not m:
        return None
    base, a, ab, fname = m.groups()
    return f"{base}/thumb/{a}/{ab}/{fname}/{width}px-{fname}"


# (_domain_contradiction_markers is imported from
# picture_gate_shared.py.)


def evaluate_article_candidate(page, entity, route, min_w, min_h,
                               hint_terms=frozenset(),
                               entity_kind=None,
                               person_context=None,
                               person_domain=None,
                               story_years=frozenset(),
                               story_historical=False):
    """One Commons search hit -> (candidate | None, ledger_row).
    Same gates as reel_entity_sourcing.evaluate_commons_page
    (photograph type, subject denylist, license, exact identity,
    wildlife-subject denial) with article resolution floors,
    plus a topicality gate when hint_terms are supplied, plus
    the person namesake gate when person_context is supplied
    (a set, possibly empty — None leaves the gate off).
    person_domain is the article's category, for the gate's
    contradiction markers."""
    title = page.get("title") or ""
    info = (page.get("imageinfo") or [{}])[0]
    row = {"candidate": title, "route": route, "entity": entity}

    def reject(reason):
        row.update({"verdict": "rejected", "reason": reason})
        return None, row

    if info.get("mime") not in ("image/jpeg", "image/png"):
        return reject(f"not a photograph file "
                      f"({info.get('mime') or 'unknown type'})")
    desc = RES._meta(info, "ImageDescription")
    cats = RES._meta(info, "Categories")
    if RES.subject_denied(title, desc):
        return reject("title/description marks it as a logo/"
                      "diagram/map-type file, not a scene "
                      "photograph")
    graphic_text = (f"{title} {RES._strip_html(desc)} {cats}"
                    ).lower()
    if any(m in graphic_text for m in _GRAPHIC_MARKERS):
        return reject("title/description/categories mark it "
                      "as a map/graphic file (OpenStreetMap/"
                      "overpass/mandal-type), not a scene "
                      "photograph")
    w, h = info.get("width") or 0, info.get("height") or 0
    if not (w >= min_w and h >= min_h):
        return reject(f"resolution: {w}x{h} — below the "
                      f"{min_w}x{min_h} floor for this slot")
    ok, label = RES.license_verdict(info.get("extmetadata"))
    if not ok:
        return reject(f"license: {label} — not CC / public domain")
    if not RES.identity_ok(entity, title, desc, cats):
        return reject(f"identity: the file page's description/"
                      f"categories do not evidence {entity!r}")
    if RES.wildlife_subject(entity, cats):
        return reject("identity: the file's subject is wildlife "
                      "photographed AT the entity, not the entity "
                      "itself (species-marked categories)")
    binomial = _desc_binomial_subject(desc, entity)
    if binomial:
        return reject("identity: the file's subject is wildlife "
                      f"({binomial} in the description) photo-"
                      "graphed AT the entity, not the entity "
                      "itself")
    if entity_kind == "person" and person_context is not None:
        ev_text = _SHARED_GATES.mask_title_phrases(
            f"{title} {RES._strip_html(desc)} {cats}")
        ev_tokens = set(RES._tokens(ev_text))
        # 1. Contradiction: the evidence marks a DIFFERENT
        # profession/domain than the story's — a parenthesised
        # disambiguator ('Shadab Khan (actor)') or a profession
        # marker unique to another domain ('businessman' on a
        # sports story). This is the namesake signature.
        bad = _domain_contradiction_markers(person_domain)
        contra = {t for t in bad if _ctx_token_match(t, ev_tokens)}
        disambig = re.findall(r"\(([^)]+)\)", ev_text)
        for d in disambig:
            d_toks = set(RES._tokens(d))
            contra |= {t for t in bad
                       if any(_ctx_token_match(t, {x})
                              for x in d_toks)}
        if contra:
            return reject(
                "namesake guard: the file's evidence marks a "
                f"different domain ({', '.join(sorted(contra))}) "
                f"than this {person_domain or 'story'} article — "
                f"a same-name different person, not {entity!r} "
                "the subject of this story")
        # 2. Agreement: a story-context token in the evidence.
        matched = {t for t in person_context
                   if _ctx_token_match(t, ev_tokens)}
        # 3. Own category: the file sits in the person's OWN
        # Commons category (a segment exactly equal to the
        # name) — filed under this person, no contradiction.
        own_cat = any(
            seg.strip().lower().removeprefix("category:")
            == (entity or "").strip().lower()
            for seg in (cats or "").split("|"))
        if not matched and not own_cat:
            return reject(
                "namesake guard: the file page's evidence shares "
                "no story-context token with this article and "
                "the file is not in the person's own Commons "
                "category, so it cannot be told apart from a "
                f"same-name different person ({entity!r}) — "
                "verified routes only (person cache / profile "
                "lookup), else no picture")
    if entity_kind != "person":
        if not _subject_position_ok(entity, title, desc):
            return reject("subject: the entity is not the "
                          "file's subject — it appears only as "
                          "a location, a category mention or a "
                          "namesake, not in the title/description "
                          "subject position")
        person = _depicted_person_name(title, entity)
        if person and _phrase_span(RES.entity_tokens(entity),
                                   RES._tokens(
                                       _title_core(title))) \
                is None:
            return reject("subject: the file is a portrait of "
                          f"{person}, a specific person who is "
                          "not the entity — association is not "
                          "depiction")
    # Era gate (2026-10-26 live-run lesson): a dated file
    # whose date is not the story's date is a different event,
    # however well the name matches — a 1939 archival Queen
    # Street photograph inside a 2026 Diwali story, a 2022
    # White House Diwali photo captioned as Times Square
    # 2026. A year in the file TITLE is the file dating
    # itself: pre-2000 means archival; a modern year disjoint
    # from the headline's years means a different year's
    # event. Historical stories (story_historical) are
    # exempt — a look-back piece may carry archival pictures.
    if not story_historical:
        # A person's birth/lifespan years in a title
        # ('(born 1993)', '(1939–2021)') date the PERSON,
        # not the photograph — strip them before dating
        # the file.
        title_dated = re.sub(
            r"\(\s*(?:born\s+)?\d{4}\s*[–—-]\s*\d{4}\s*\)"
            r"|\(\s*born\s+\d{4}\s*\)"
            r"|\b(?:born|died)\s+\d{4}\b",
            " ", title)
        title_years = {int(y) for y in re.findall(
            r"\b(?:18|19|20)\d{2}\b", title_dated)}
        archival_years = {y for y in title_years if y < 2000}
        if archival_years:
            return reject(
                "era: the file is dated "
                f"{sorted(archival_years)[0]} in its title — "
                "an archival/historical photograph, not this "
                "current story's event")
        if title_years and story_years and \
                title_years.isdisjoint(story_years):
            return reject(
                "era: the file is dated "
                f"{sorted(title_years)[0]} in its title but "
                "this story is dated "
                f"{sorted(story_years)[0]} — a different "
                "year's event, not this story's")
        arch_text = f"{title} {cats}".lower()
        if any(m in arch_text for m in
               ("archival", "glass negative", "glass plate",
                "vintage photograph")):
            return reject(
                "era: the file's title/categories mark it as "
                "an archival/vintage photograph, not this "
                "current story's event")
        m = re.search(
            r"\b(?:photograph|photo|taken|image)\s+"
            r"(?:in|from|of)\s+((?:18|19)\d{2})\b",
            RES._strip_html(desc).lower())
        if m:
            return reject(
                f"era: the file's description dates the "
                f"photograph to {m.group(1)} — an archival "
                "photograph, not this current story's event")
    if hint_terms:
        evidence = (f"{title} {RES._strip_html(desc)} {cats}"
                    ).lower()
        ev_tokens = set(RES._tokens(evidence))
        matched = {t for t in hint_terms if t in ev_tokens}
        need = 2 if len(hint_terms) >= 3 else 1
        if len(matched) < need:
            return reject("topicality: the file page's evidence "
                          f"matches {len(matched)} of the "
                          f"story's terms (needs {need}) — a "
                          "namesake/generic match, not this "
                          "story's subject")
    # Serve-size gate (compress-and-keep, Kiran's steer
    # 2026-10-25): an original over the web budget is never
    # hotlinked as-is (the Cyclone Arnab hero was a ~105 MB
    # original GIF). In order: (1) a host-side resized variant
    # (Wikimedia 1920px thumb) when one is derivable; (2) the
    # pick is flagged oversize and _verify_pick downloads the
    # original, self-compresses it to <=1920px and uploads it
    # to Supabase Storage; (3) reject only if both paths fail
    # (decided at verify time, where the bytes are in hand).
    file_url = info.get("url")
    serve_note = ""
    oversize_bytes = 0
    size_bytes = info.get("size") or 0
    if size_bytes > MAX_SERVE_BYTES:
        thumb = _wikimedia_thumb_url(file_url, SERVE_THUMB_W)
        if thumb:
            if w > SERVE_THUMB_W:
                h = round(h * SERVE_THUMB_W / w)
                w = SERVE_THUMB_W
            serve_note = (f"original {size_bytes} bytes exceeds "
                          f"the web budget — served via its "
                          f"{SERVE_THUMB_W}px variant")
            file_url = thumb
        else:
            oversize_bytes = size_bytes
            serve_note = (f"original {size_bytes} bytes exceeds "
                          f"the web budget — flagged for "
                          "self-compression at verify time")
    artist = RES._meta(info, "Artist")[:80]
    cand = {
        "entity": entity, "title": title,
        "file_url": file_url, "size": [w, h],
        "source_page": info.get("descriptionurl")
        or ("https://commons.wikimedia.org/wiki/"
            + urllib.parse.quote(title.replace(" ", "_"))),
        "license": label, "artist": artist,
        "subject": (desc or title)[:240],
        "role": RES.classify_role(title, desc),
        "route": route,
        "verification": "entity evidenced in the Commons file "
                        "page's own title/description/categories; "
                        "license read from its extmetadata",
        "attribution": (f"Photo: {artist} via Wikimedia Commons "
                        f"({label})" if artist else
                        f"Wikimedia Commons ({label})"),
    }
    if serve_note:
        cand["verification"] += "; " + serve_note
    if oversize_bytes:
        cand["oversize_original"] = oversize_bytes
        cand["needs_dims_check"] = True  # force the download
        # path in _verify_pick: the bytes are needed to
        # self-compress, and dims must be re-verified there
    elif serve_note:
        cand["serve_variant"] = True
    row.update({"verdict": "accepted",
                "reason": f"{w}x{h}, {label}, identity evidenced "
                          f"on the file page"
                          + (f"; {serve_note}" if serve_note
                             else "")})
    return cand, row


# ── network defaults (injectable for tests) ─────────────────────────
def _verify_url(url):
    ok, _ctype, width = IS.verify_image_url(url, min_width=1)
    return {"ok": ok, "width": width}


def _download_verify(url, dest):
    """Download + PIL-verify; returns [w, h] at the actual file."""
    RES.download_file(url, dest)
    from PIL import Image
    with Image.open(dest) as im:
        return list(im.size)


DEFAULT_NET = {
    "commons_search": RES.commons_search,
    "commons_file_info": RES.commons_file_info,
    "brave_links": RES.brave_links,
    "fetch_text": RES.fetch_text,
    "download_verify": _download_verify,
    "verify_url": _verify_url,
    "person_cache": IS.fetch_cached_person_image,
    "upload_image": IS.upload_to_supabase,
}


# ── sourcing one entity ─────────────────────────────────────────────
def source_entity_images(entity_rec, article, hint, net, min_w,
                         min_h, want=2, seen_titles=None, log=print,
                         all_entities=None):
    """Run the ladder for one entity. Returns (candidates,
    ledger_rows). Candidates are best-first (widest, then
    preferred-width bonus). Downloads are NOT done here — the
    caller verifies the selected pick at the file."""
    name = entity_rec["name"]
    seen_titles = seen_titles if seen_titles is not None else set()
    cands, ledger = [], []
    if not entity_rec.get("sourceable", True):
        ledger.append(
            {"candidate": "(entity)", "route": "all",
             "entity": name, "verdict": "rejected",
             "reason": "single-token fragment/common word from "
                       "headline/body extraction — a lone token "
                       "in a file's evidence is not identity "
                       "proof; never sourced"})
        return cands, ledger
    # Topicality vocabulary for the gates below. Non-persons use
    # it as the topicality gate; persons are exempt from THAT
    # gate but get the namesake gate instead — their Commons
    # candidates must agree with the story's context vocabulary
    # (see _person_context_terms).
    is_person = entity_rec.get("kind") == "person"
    hint_terms = frozenset() if is_person \
        else _story_hint_terms(article, name,
                               all_entities=all_entities)
    person_context = _person_context_terms(
        article, name, all_entities=all_entities) if is_person \
        else None
    # Era context for the candidate era gate: the years the
    # HEADLINE dates the story to, and whether the story is
    # itself a historical/look-back piece (exempt — archival
    # pictures are legitimate there).
    _headline = article.get("headline") or ""
    story_years = frozenset(
        int(y) for y in re.findall(r"\b(?:19|20)\d{2}\b",
                                   _headline))
    story_historical = bool(
        any(y < 2000 for y in story_years)
        or re.search(r"\b(history|historical|anniversary|"
                     r"years ago|throwback|archives?|vintage|"
                     r"centenary)\b", _headline.lower()))

    def consider(cand, row):
        ledger.append(row)
        if cand and cand["title"] not in seen_titles:
            seen_titles.add(cand["title"])
            cands.append(cand)

    # Route A: Wikimedia Commons originals.
    try:
        for q in RES.queries_for(name, hint):
            if len(cands) >= want:
                break
            try:
                pages = net["commons_search"](q)
            except Exception as e:
                ledger.append({"candidate": f"Commons search {q!r}",
                               "route": "A — Wikimedia Commons",
                               "entity": name, "verdict": "rejected",
                               "reason": f"search failed: {e}"[:200]})
                break
            for page in pages:
                if len(cands) >= want:
                    break
                if page.get("title") in seen_titles:
                    continue
                cand, row = evaluate_article_candidate(
                    page, name, "A — Wikimedia Commons", min_w,
                    min_h, hint_terms=hint_terms,
                    entity_kind=entity_rec.get("kind"),
                    person_context=person_context,
                    person_domain=(article.get("category") or "")
                    .strip().lower(),
                    story_years=story_years,
                    story_historical=story_historical)
                consider(cand, row)
    except Exception as e:
        ledger.append({"candidate": "(route A)", "entity": name,
                       "route": "A — Wikimedia Commons",
                       "verdict": "rejected",
                       "reason": f"route error: {e}"[:200]})

    # Route C: web search as discovery -> Commons file pages.
    if len(cands) < want:
        try:
            for link in net["brave_links"](
                    f"{name} site:commons.wikimedia.org", 6):
                if len(cands) >= want:
                    break
                m = re.search(r"/wiki/(File:[^/?#]+)", link)
                if not m:
                    continue
                title = urllib.parse.unquote(m.group(1)) \
                    .replace("_", " ")
                if title in seen_titles:
                    continue
                try:
                    page = net["commons_file_info"](title)
                except Exception:
                    page = None
                if not page:
                    continue
                cand, row = evaluate_article_candidate(
                    page, name, "C — web search (discovery) → "
                    "Commons", min_w, min_h, hint_terms=hint_terms,
                    entity_kind=entity_rec.get("kind"),
                    person_context=person_context,
                    person_domain=(article.get("category") or "")
                    .strip().lower(),
                    story_years=story_years,
                    story_historical=story_historical)
                consider(cand, row)
        except Exception as e:
            ledger.append({"candidate": "(route C)", "entity": name,
                           "route": "C — web search (discovery)",
                           "verdict": "rejected",
                           "reason": f"route error: {e}"[:200]})

    # Route B: official sources — multi-token orgs/places only.
    # A hosted page's og:image of a PERSON has no face/identity
    # check at the file, so person entities never take this route
    # (persons go through the cache / Commons exact-name /
    # Source 3.8 gates instead). Single tokens are excluded too:
    # a bare surname/place token may be a person.
    if len(cands) < want and entity_rec["kind"] != "person" \
            and not RES._looks_like_person(name) \
            and len(name.split()) > 1:
        try:
            for link in net["brave_links"](
                    f"{name} official newsroom press media", 6)[:3]:
                host = urllib.parse.urlparse(link).netloc.lower()
                toks = RES.entity_tokens(name)
                official = host.endswith((".gov", ".mil")) or (
                    toks and toks[0] in host)
                if not official:
                    continue
                cand, row = RES.evaluate_hosted_page(
                    link, name, "B — official sources", net)
                dropped = False
                if cand and hint_terms:
                    ev_tokens = set(RES._tokens(
                        f"{cand.get('title', '')} "
                        f"{cand.get('subject', '')}"))
                    matched = {t for t in hint_terms
                               if t in ev_tokens}
                    need = 2 if len(hint_terms) >= 3 else 1
                    if len(matched) < need:
                        ledger.append(
                            {"candidate": cand.get("title"),
                             "route": "B — official sources",
                             "entity": name, "verdict": "rejected",
                             "reason": "topicality: the hosted "
                                       "image's evidence shares no "
                                       "headline term with this "
                                       "story — a namesake/generic "
                                       "match, not this story's "
                                       "subject"})
                        cand, dropped = None, True
                if cand:
                    cand["verification"] = (
                        "identity evidenced on the official page; "
                        "license basis recorded on the page "
                        "(federal PD or explicit CC/PD statement); "
                        "dimensions verified at download")
                    cand["attribution"] = (
                        "Official source — "
                        + (host or "publisher"))
                if not dropped:
                    # (When dropped, the topicality row above is
                    # the ledger entry — the hosted evaluator's
                    # own row would falsely read 'accepted'.)
                    consider(cand, row)
                if cand:
                    break
        except Exception as e:
            ledger.append({"candidate": "(route B)", "entity": name,
                           "route": "B — official sources",
                           "verdict": "rejected",
                           "reason": f"route error: {e}"[:200]})

    cands.sort(key=lambda c: (-(c["size"][0] if c.get("size") else 0),
                              c["title"]))
    return cands, ledger


# ── captions + inline placement ─────────────────────────────────────
def count_inline_figures(body):
    """Inline figures in a body (enrich-articles' own patterns:
    markdown images + HTML <figure><img)."""
    if not body:
        return 0
    md = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", body))
    figs = len(re.findall(r"<figure[^>]*>.*?<img\s", body,
                          re.DOTALL))
    return md + figs


def word_count(body):
    return len(RES._strip_html(body or "").split())


def build_caption(entity, cand, article):
    """Factual two-sentence caption in the enricher's convention:
    what the image shows, then one context sentence drawn from
    the article body itself. No invented facts."""
    subject = RES._strip_html(cand.get("subject") or "")
    subject = re.split(r"(?<=[.!?])\s+", subject)[0].strip()
    if not subject or len(subject) < 12 or len(subject) > 180 \
            or subject.lower() == entity.lower():
        subject = cand.get("title", "").replace("File:", "") \
            .rsplit(".", 1)[0].replace("_", " ").strip() or entity
        subject = f"{entity}: {subject}" \
            if entity.lower() not in subject.lower() else subject
    body_text = RES._strip_html(article.get("body") or "")
    toks = [t for t in RES.entity_tokens(entity) if len(t) >= 4]
    context = ""
    for s in re.split(r"(?<=[.!?])\s+", body_text):
        s = s.strip()
        if 20 < len(s) < 250 and toks and \
                any(t in s.lower() for t in toks):
            context = s
            break
    caption = subject if subject.endswith((".", "!", "?")) \
        else subject + "."
    if context and context.lower() not in caption.lower():
        caption = f"{caption} {context}"
    parts = re.split(r"(?<=[.!?])\s+", caption)
    return " ".join(parts[:2]).strip()


_ENRICH_MOD = None


def _enrich_module():
    """Load enrich-articles.py lazily (hyphenated filename) for
    its insert_inline_images() — the enricher's exact figure
    format + placement logic."""
    global _ENRICH_MOD
    if _ENRICH_MOD is None:
        from importlib.machinery import SourceFileLoader
        _ENRICH_MOD = SourceFileLoader(
            "enrich_articles",
            str(Path(__file__).resolve().parent
                / "enrich-articles.py")).load_module()
    return _ENRICH_MOD


def propose_body_with_inlines(body, picks):
    """picks = [(entity, file_url, caption)] in the enricher's
    tuple shape. Returns the proposed body (pure string op)."""
    if not picks:
        return body
    mod = _enrich_module()
    return mod.insert_inline_images(body, picks,
                                    max_cap=len(picks))


# ── per-article processing ──────────────────────────────────────────
def _provenance(cand, verified_size=None):
    return {
        "entity": cand["entity"],
        "title": cand["title"],
        "file_url": cand["file_url"],
        "original_file_url": cand.get("original_file_url"),
        "source_page": cand["source_page"],
        "license": cand["license"],
        "attribution": cand["attribution"],
        "resolution": verified_size or cand.get("size"),
        "route": cand["route"],
        "role": cand.get("role"),
        "depicts": cand["entity"],
        "verified_how": cand["verification"],
    }


# ── Rung 0 provenance writes (records only — image_ledger.py) ────
def _ledger_hero(article, cand, replaced_url):
    """Record a hero placement this pass just applied; a replaced
    hero gets a removal event first so its history is preserved."""
    try:
        import image_ledger
        if replaced_url and replaced_url != cand["file_url"]:
            image_ledger.record_removal(
                article_id=article.get("id"), slug=article.get("slug"),
                surface="hero", removed_url=replaced_url,
                producer="article_picture_pass",
                reason="replaced by picture-pass hero pick")
        image_ledger.record_provenance(
            article_id=article.get("id"), slug=article.get("slug"),
            surface="hero", producer="article_picture_pass",
            source_route=image_ledger.route_from_picture_pass(
                cand.get("route")),
            image_url=cand["file_url"],
            source_page_url=cand.get("source_page"),
            original_file_url=cand.get("original_file_url"),
            license_text=cand.get("license"),
            attribution=cand.get("attribution"),
            entity=cand.get("entity"),
            extra={"title": cand.get("title"),
                   "verified_how": cand.get("verification")})
    except Exception:
        pass


def _ledger_inlines(article, proposed):
    """Record each inline placement this pass just applied."""
    try:
        import image_ledger
        for p in proposed:
            image_ledger.record_provenance(
                article_id=article.get("id"), slug=article.get("slug"),
                surface="inline", producer="article_picture_pass",
                source_route=image_ledger.route_from_picture_pass(
                    p.get("route")),
                image_url=p.get("file_url"),
                source_page_url=p.get("source_page"),
                original_file_url=p.get("original_file_url"),
                license_text=p.get("license"),
                attribution=p.get("attribution"),
                entity=p.get("entity"),
                extra={"title": p.get("title"),
                       "verified_how": p.get("verified_how")})
    except Exception:
        pass


def process_article(article, net=None, apply=False, log=print,
                    patch_fn=None, download_dir=None):
    """Full pass for one article. Returns the report record.
    patch_fn is invoked ONLY when apply=True."""
    net = {**DEFAULT_NET, **(net or {})}
    patch_fn = patch_fn or patch_article
    slug = article.get("slug") or "(no slug)"
    rec = {
        "id": article.get("id"), "slug": slug,
        "headline": article.get("headline") or "",
        "category": article.get("category"),
        "published_at": article.get("published_at"),
        "url": f"https://www.thevideshi.com/articles/{slug}",
        "blocked": bool(article.get("image_backfill_blocked")),
        "entities": [], "hero": {"action": "none"},
        "inlines": {"existing": count_inline_figures(
            article.get("body")), "proposed": []},
        "ledger": [], "notes": [], "applied": [],
    }
    body = article.get("body") or ""

    # The intentional-null convention is absolute: a blocked
    # article is not probed, not sourced, not touched.
    if rec["blocked"]:
        rec["hero"] = {"action": "skip-blocked",
                        "reason": "image_backfill_blocked=true — "
                                  "intentional null, never touched"}
        rec["notes"].append("skipped entirely (backfill blocked)")
        return rec

    entities = extract_article_entities(article)
    rec["entities"] = entities
    hint = RES.topical_hint(article, [e["name"] for e in entities])
    seen_titles = set()
    if article.get("image_url"):
        seen_titles.add(article["image_url"])

    # ── hero ──
    hero_url = article.get("image_url")
    probe = None
    if hero_url:
        try:
            probe = net["verify_url"](hero_url)
        except Exception as e:
            probe = {"ok": False, "width": 0}
            rec["notes"].append(f"hero probe error: {e}"[:160])
    action, reason = classify_hero(article, probe)
    rec["hero"] = {
        "action": action, "reason": reason,
        "current": ({"url": hero_url,
                     "width": (probe or {}).get("width")}
                    if hero_url else None),
        "proposed": None,
    }
    hero_pick = None
    if action in ("fill", "replace"):
        floor = hero_width_floor((probe or {}).get("width")
                                 if action == "replace" else None)
        hero_pick = _source_hero(article, entities, hint, net,
                                 floor, seen_titles, rec, log,
                                 apply=apply)
        if hero_pick:
            rec["hero"]["proposed"] = _provenance(
                hero_pick, hero_pick.get("_verified_size"))
            rec["hero"]["caption"] = _hero_caption(article,
                                                   hero_pick)
        else:
            rec["notes"].append(
                "hero slot left empty — no candidate cleared "
                "the gates (honest miss, logged per entity)")

    # ── inlines ──
    existing = rec["inlines"]["existing"]
    if existing >= 2:
        rec["notes"].append(
            f"body already has {existing} inline figures — "
            "no inline work")
    elif word_count(body) < MIN_ARTICLE_WORDS:
        rec["notes"].append(
            f"body is {word_count(body)} words — below the "
            f"{MIN_ARTICLE_WORDS}-word inline floor")
    else:
        want = min(MAX_INLINE_TOTAL - existing, 3)
        picks = _source_inlines(article, entities, hint, net,
                                want, seen_titles, rec, log,
                                hero_url=hero_url,
                                hero_pick=hero_pick,
                                exclude_urls=_body_image_urls(body))
        rec["inlines"]["proposed"] = [
            {**_provenance(c, c.get("_verified_size")),
             "caption": build_caption(c["entity"], c, article)}
            for c in picks]
        if picks:
            tuples = [(c["entity"], c["file_url"],
                       build_caption(c["entity"], c, article))
                      for c in picks]
            rec["_proposed_body"] = propose_body_with_inlines(
                body, tuples)
        elif entities:
            rec["notes"].append(
                "no inline candidate cleared the gates — "
                "slots left empty")

    # ── apply (never reached in dry-run) ──
    if apply:
        if hero_pick:
            payload = {
                "image_url": hero_pick["file_url"],
                "image_caption": _hero_caption(article, hero_pick),
                "image_attribution": hero_pick["attribution"],
            }
            if patch_fn(article["id"], payload):
                rec["applied"].append("hero")
                _ledger_hero(article, hero_pick, hero_url)
        if rec.get("_proposed_body") and \
                rec["_proposed_body"] != body:
            if patch_fn(article["id"],
                        {"body": rec["_proposed_body"]}):
                rec["applied"].append("body-inlines")
                _ledger_inlines(article, rec["inlines"]["proposed"])
    # The proposed body is a working string, never report data.
    rec.pop("_proposed_body", None)
    return rec


def _hero_caption(article, cand):
    """Hero caption: what the image shows (file-page subject),
    then the article context — the writer's two-sentence rule."""
    return build_caption(cand["entity"], cand, article)


def _self_compress(local_path, max_w=SERVE_THUMB_W):
    """Resize a downloaded original to <=max_w wide and JPEG-
    compress it (q80; one retry at 1600px/q72 if still over
    the serve budget). Returns (jpeg_bytes, [w, h]) or
    (None, None)."""
    from io import BytesIO
    from PIL import Image
    try:
        with Image.open(local_path) as im:
            im.load()
            if im.mode in ("RGBA", "LA", "P", "PA"):
                bg = Image.new("RGB", im.size, (255, 255, 255))
                bg.paste(im, mask=im.convert("RGBA")
                         .split()[-1])
                im = bg
            elif im.mode != "RGB":
                im = im.convert("RGB")
            for width, quality in ((max_w, 80), (1600, 72)):
                work = im
                if work.width > width:
                    work = work.resize(
                        (width, round(work.height * width
                                      / work.width)),
                        Image.LANCZOS)
                out = BytesIO()
                work.save(out, format="JPEG", quality=quality,
                          optimize=True)
                data = out.getvalue()
                if len(data) <= MAX_SERVE_BYTES:
                    return data, [work.width, work.height]
            return None, None
    except Exception:
        return None, None


def _verify_pick(cand, net, download_dir, slug, log,
                 min_w=0, min_h=0):
    """Verify a selected candidate at the downloaded file (true
    dimensions must clear the slot floor). Returns the candidate
    with _verified_size set, or None on failure (ledgered by the
    caller)."""
    if not cand.get("needs_dims_check") and cand.get("size") \
            and cand["route"].startswith(("A —", "C —")):
        # Commons imageinfo dims are the file's true dims
        # (screened from the API, per the reel doctrine); still
        # confirm retrievability cheaply via the verifier.
        try:
            probe = net["verify_url"](cand["file_url"])
        except Exception:
            probe = {"ok": False}
        if not probe.get("ok"):
            return None
        cand["_verified_size"] = cand["size"]
        return cand
    dest_dir = Path(download_dir or DOWNLOAD_DIR) / (slug or "art")
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(urllib.parse.urlparse(
        cand["file_url"]).path).suffix or ".jpg"
    dest = dest_dir / (RES.slugify(cand["title"].replace("File:", "")
                                   .rsplit(".", 1)[0]) + ext.lower())
    try:
        size = net["download_verify"](cand["file_url"], dest)
    except Exception as e:
        log(f"    ⊘ download/verify failed for "
            f"{cand['title'][:50]}: {e}"[:160])
        return None
    if size[0] < min_w or size[1] < min_h:
        log(f"    ⊘ {cand['title'][:50]}: {size[0]}x{size[1]} at "
            f"the file — below the {min_w}x{min_h} floor")
        return None
    if cand.get("oversize_original"):
        # Compress-and-keep path 2: no host variant exists, so
        # self-compress the downloaded original and self-host
        # it. Failure of either step rejects the pick (path 3).
        data, new_size = _self_compress(dest)
        if not data:
            log(f"    ⊘ {cand['title'][:50]}: self-compression "
                f"could not bring the "
                f"{cand['oversize_original']}-byte original "
                "under the serve budget")
            return None
        uploader = net["upload_image"] if "upload_image" in net \
            else IS.upload_to_supabase
        fname = (RES.slugify((slug or "article") + "-" +
                             cand["title"].replace("File:", "")
                             .rsplit(".", 1)[0]) + "-web.jpg")
        try:
            stored_url = uploader(data, fname)
        except Exception:
            stored_url = None
        if not stored_url:
            log(f"    ⊘ {cand['title'][:50]}: self-compressed "
                "upload to Supabase Storage failed")
            return None
        log(f"    ⇓ {cand['title'][:50]}: self-compressed "
            f"{cand['oversize_original']} -> {len(data)} bytes "
            f"({new_size[0]}x{new_size[1]}), self-hosted")
        # Rung 0: remember the pre-swap original for the provenance
        # ledger (records only — see image_ledger.py).
        cand.setdefault("original_file_url", cand["file_url"])
        cand["file_url"] = stored_url
        cand["size"] = new_size
        cand["serve_variant"] = True
        cand["self_compressed"] = True
        cand["verification"] += (
            f"; self-compressed from original "
            f"({cand['oversize_original']} bytes) to "
            f"{new_size[0]}x{new_size[1]} JPEG and self-hosted "
            "in Supabase Storage (article-images)")
        size = new_size
    cand["_verified_size"] = size
    cand["_local_path"] = str(dest)
    return cand


def headline_subject_names(article, entities):
    """The article's SUBJECT entities — the only ones a hero
    may be sourced for: entities named in the headline
    (extracted with source='headline', or named there
    verbatim) plus the writer's declared primary subjects
    (image_entities). Body-only mentions are NOT subjects:
    the Oct 25–26 runs filled heroes from a place the story
    merely mentioned (a Biman Bangladesh 787 keyed to
    'Toronto Pearson' on an Air India story), a company the
    story merely cited (a Goldman Sachs building on an
    Infosys earnings story) and a person the story merely
    quoted. Those entities stay inline-eligible under the
    inline gates; they can never carry the hero."""
    headline = (article.get("headline") or "").lower()
    subs = set()
    for e in entities:
        name = e["name"]
        if e.get("source") in ("headline", "image_entities"):
            subs.add(name.lower())
        elif re.search(r"\b" + re.escape(name.lower()) + r"\b",
                       headline):
            subs.add(name.lower())
    return subs


def _source_hero(article, entities, hint, net, floor_w, seen_titles,
                 rec, log, apply=False):
    """Hero sourcing across ranked entities. Person entities go
    cache → Commons exact-name → (apply only) Source 3.8.
    HERO SUBJECT GATE: only headline-subject entities are
    tried (see headline_subject_names); a quoted-source person
    is refused even then. No subject candidate clearing the
    gates means the hero stays an honest miss."""
    slug = article.get("slug") or "article"
    subjects = headline_subject_names(article, entities)
    best = None
    for rec_e in entities:
        name = rec_e["name"]
        if name.lower() not in subjects:
            rec["ledger"].append(
                {"candidate": "(entity)", "route": "hero",
                 "entity": name, "verdict": "rejected",
                 "reason": "hero subject gate: not a headline "
                           "subject — heroes source from the "
                           "article's headline subjects only; "
                           "body mentions, quoted sources and "
                           "place mentions are inline-eligible "
                           "but never carry the hero"})
            continue
        if rec_e.get("quoted_source"):
            rec["ledger"].append(
                {"candidate": "(entity)", "route": "hero",
                 "entity": name, "verdict": "rejected",
                 "reason": "hero subject gate: the body only "
                           "QUOTES this person (a cited analyst/"
                           "source), never makes them the "
                           "subject — quoted sources are not "
                           "hero subjects"})
            continue
        cands = []
        # The person_images cache is an exact-name read-only
        # lookup — a hit is itself identity verification, so it
        # is tried for persons and bare single tokens alike.
        if rec_e["kind"] == "person" or len(name.split()) == 1:
            cached = None
            try:
                cached = net["person_cache"](name)
            except Exception:
                cached = None
            if cached and cached not in seen_titles:
                probe = net["verify_url"](cached)
                if probe.get("ok") and \
                        (probe.get("width") or 0) >= floor_w:
                    best = {
                        "entity": name, "title": f"{name} "
                        "(verified portrait, person_images cache)",
                        "file_url": cached,
                        "size": [probe["width"], None],
                        "source_page": "person_images cache "
                        "(identity-verified portrait)",
                        "license": "as recorded in person_images "
                        "at verification time",
                        "attribution": "Portrait via the subject's "
                        "verified profile (person_images cache)",
                        "role": "portrait",
                        "route": "person_images cache",
                        "verification": "portrait identity-verified "
                        "when cached (exact-name profile gate, "
                        "Source 3.8 standard)",
                        "_verified_size": [probe["width"], None],
                    }
                    rec["ledger"].append(
                        {"candidate": name,
                         "route": "person_images cache",
                         "entity": name, "verdict": "accepted",
                         "reason": f"cached verified portrait, "
                                   f"{probe['width']}px wide"})
                    break
                rec["ledger"].append(
                    {"candidate": name,
                     "route": "person_images cache",
                     "entity": name, "verdict": "rejected",
                     "reason": "cached portrait failed "
                               "verification or the width floor"})
        cands, rows = source_entity_images(
            rec_e, article, hint, net, floor_w, HERO_MIN_H,
            want=2, seen_titles=seen_titles, log=log,
            all_entities=entities)
        rec["ledger"].extend(rows)
        # RANK-FIRST selection: the highest-ranked entity that
        # yields a usable hero wins; width only breaks ties
        # WITHIN an entity. (Width-first across entities let a
        # junk entity's huge scan outrank the headline person's
        # verified portrait in the first validation run.)
        # Heroes display wide, so portrait-orientation files
        # (w < h) are rejected for this slot.
        entity_best = None
        for c in cands:
            size = c.get("size") or [0, 0]
            if size[0] and size[1] and size[0] < size[1]:
                rec["ledger"].append(
                    {"candidate": c["title"], "route": c["route"],
                     "entity": name, "verdict": "rejected",
                     "reason": f"portrait orientation "
                               f"{size[0]}x{size[1]} — heroes "
                               f"display wide"})
                continue
            if entity_best is None or size[0] > \
                    (entity_best.get("size") or [0])[0]:
                entity_best = c
        if entity_best is not None:
            best = entity_best
            break
        if (rec_e["kind"] == "person" or len(name.split()) == 1) \
                and not cands:
            if apply:
                rec["notes"].append(
                    f"person-profile route (Source 3.8) would "
                    f"run for {name!r} under --apply")
            else:
                rec["notes"].append(
                    f"person-profile route (Source 3.8) deferred "
                    f"for {name!r}: it uploads + caches on "
                    f"success (writes) — runs under --apply only")
    if best is None:
        return None
    if not best.get("_verified_size"):
        if _verify_pick(best, net, DOWNLOAD_DIR, slug, log,
                        min_w=floor_w, min_h=HERO_MIN_H) is None:
            rec["ledger"].append(
                {"candidate": best["title"], "route": best["route"],
                 "entity": best["entity"], "verdict": "rejected",
                 "reason": "failed verification at the file"})
            return None
    return best


def _body_image_urls(body):
    """Every image URL already inside the body (markdown
    images + HTML <img src>) — an inline must never duplicate
    a picture the article already carries."""
    urls = set()
    for m in re.finditer(r"!\[[^\]]*\]\(\s*([^)\s]+)", body or ""):
        urls.add(m.group(1))
    for m in re.finditer(r"<img[^>]+src=[\"']([^\"']+)", body or ""):
        urls.add(m.group(1))
    return urls


def _wikimedia_file_key(text):
    """Canonical identity of a Wikimedia Commons file from
    any of its surface forms: a 'File:' title, the original
    upload URL, a thumb URL at any width, any of them with
    tracking query params (the Commons API appends
    ?utm_source=... to the URLs it returns). Returns a
    normalized 'name.ext' key, or None when the text does
    not resolve to a filename. Duplicate detection must
    compare THESE keys, never raw URL strings: the same
    file reaches an article body as an original in one run
    and as a 1920px thumb in another, and exact-string
    comparison waves the second copy through."""
    if not text:
        return None
    t = urllib.parse.unquote(str(text))
    t = t.split("?")[0].split("#")[0].strip()
    if "/" in t:
        t = t.rsplit("/", 1)[-1]
    t = re.sub(r"^\d+px-", "", t)  # thumb rendition prefix
    t = re.sub(r"^file:", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t.replace("_", " ")).strip().lower()
    if "." not in t:
        return None
    return t


def _file_stem_slug(text):
    """Alnum-only stem slug of a file title/URL — the form
    a self-hosted storage filename embeds (the
    self-compress path names its upload slugify(article +
    Commons title) + '-web.jpg'), so a Commons candidate
    can still be recognised when an earlier run served it
    from Supabase Storage instead of upload.wikimedia.org."""
    if not text:
        return ""
    t = urllib.parse.unquote(str(text))
    t = t.split("?")[0].split("#")[0].strip()
    if "/" in t:
        t = t.rsplit("/", 1)[-1]
    t = re.sub(r"^\d+px-", "", t)
    t = re.sub(r"^file:", "", t, flags=re.IGNORECASE)
    stem = t.rsplit(".", 1)[0] if "." in t else t
    return re.sub(r"[^a-z0-9]", "", stem.lower())


def _same_file(candidate_texts, used_keys, used_slugs):
    """True when any candidate text names a file already
    in the used sets — by canonical Wikimedia key, or by
    stem-slug containment against the SELF-HOSTED forms in
    used_slugs (those are collected only from
    non-Wikimedia URLs, whose filenames embed the
    slugified Commons title; Wikimedia-to-Wikimedia
    sameness is exact via the key, so containment is
    never needed there and cannot false-positive on
    prefix-related filenames). The candidate slug must
    be long enough for containment to be meaningful."""
    for t in candidate_texts:
        k = _wikimedia_file_key(t)
        if k and k in used_keys:
            return True
        s = _file_stem_slug(t)
        if len(s) >= 18 and any(s in u for u in used_slugs):
            return True
    return False


def _source_inlines(article, entities, hint, net, want, seen_titles,
                    rec, log, hero_url=None, hero_pick=None,
                    exclude_urls=frozenset()):
    """Inline sourcing: at most one pick per entity, distinct
    files, never the hero's file, never a file already in the
    body or already picked as an inline, inline floors.
    Sameness is judged by canonical file identity (see
    _wikimedia_file_key), not raw URL strings — the
    2026-10-26 IOB article carried the same Commons file
    twice because one run's original-URL figure was
    invisible to the next run's comparison, and a hero
    served as a thumb can still be re-picked as an inline
    in its original form."""
    slug = article.get("slug") or "article"
    picks = []
    used_entities = {}
    used_urls = set(exclude_urls)
    hero_exact = set()
    if hero_url:
        hero_exact.add(hero_url)
    if hero_pick:
        hero_exact.add(hero_pick["file_url"])
        hero_exact.add(hero_pick["title"])
    used_keys, used_slugs = set(), set()

    def _note_used(text):
        if not text:
            return
        k = _wikimedia_file_key(text)
        if k:
            used_keys.add(k)
        # Stem slugs are collected only from self-hosted
        # storage URLs (never from 'File:' titles or
        # Wikimedia URLs — title-to-title sameness is
        # exact via the canonical key). See _same_file.
        if "://" in str(text) and \
                "wikimedia.org" not in str(text):
            s = _file_stem_slug(text)
            if s:
                used_slugs.add(s)

    for u in exclude_urls:
        _note_used(u)
    if hero_url:
        used_urls.add(hero_url)
        _note_used(hero_url)
    if hero_pick:
        used_urls.add(hero_pick["file_url"])
        used_urls.add(hero_pick["title"])
        _note_used(hero_pick["file_url"])
        _note_used(hero_pick["title"])
    for rec_e in entities:
        if len(picks) >= want:
            break
        if used_entities.get(rec_e["name"], 0) \
                >= PER_ENTITY_INLINE_CAP:
            continue
        cands, rows = source_entity_images(
            rec_e, article, hint, net, INLINE_MIN_W, INLINE_MIN_H,
            want=2, seen_titles=seen_titles, log=log,
            all_entities=entities)
        rec["ledger"].extend(rows)
        for c in cands:
            if c["file_url"] in hero_exact or \
                    c["title"] in hero_exact:
                continue
            if c["file_url"] in used_urls or \
                    _same_file((c["title"], c["file_url"]),
                               used_keys, used_slugs):
                rec["ledger"].append(
                    {"candidate": c["title"], "route": c["route"],
                     "entity": c["entity"], "verdict": "rejected",
                     "reason": "duplicate: this file is already "
                               "in the article body, is the "
                               "article's hero, or was already "
                               "picked as an inline (matched by "
                               "canonical file identity, not "
                               "the raw URL) — never illustrate "
                               "one article twice with the "
                               "same picture"})
                continue
            if _verify_pick(c, net, DOWNLOAD_DIR, slug, log,
                            min_w=INLINE_MIN_W,
                            min_h=INLINE_MIN_H) is None:
                rec["ledger"].append(
                    {"candidate": c["title"], "route": c["route"],
                     "entity": c["entity"], "verdict": "rejected",
                     "reason": "failed verification at the file"})
                continue
            picks.append(c)
            used_urls.add(c["file_url"])
            _note_used(c["title"])
            _note_used(c["file_url"])
            used_entities[rec_e["name"]] = 1
            break
    return picks


# ── report + review page ────────────────────────────────────────────
def summarize(records):
    s = {"articles_scanned": len(records), "heroes_filled": 0,
         "heroes_replaced": 0, "heroes_kept": 0,
         "blocked_skipped": 0, "inlines_proposed": 0,
         "articles_unchanged": 0, "entities_failed": []}
    failed = set()
    for r in records:
        a = r["hero"]["action"]
        if a == "fill" and r["hero"].get("proposed"):
            s["heroes_filled"] += 1
        elif a == "replace" and r["hero"].get("proposed"):
            s["heroes_replaced"] += 1
        elif a == "keep":
            s["heroes_kept"] += 1
        elif a == "skip-blocked":
            s["blocked_skipped"] += 1
        s["inlines_proposed"] += len(r["inlines"]["proposed"])
        if not r["hero"].get("proposed") \
                and not r["inlines"]["proposed"]:
            s["articles_unchanged"] += 1
        proposed_ents = set()
        if r["hero"].get("proposed"):
            proposed_ents.add(r["hero"]["proposed"]["entity"])
        proposed_ents.update(p["entity"]
                             for p in r["inlines"]["proposed"])
        for e in r["entities"]:
            if e["name"] not in proposed_ents:
                failed.add(e["name"])
    s["entities_failed"] = sorted(failed)
    return s


def _esc(x):
    return html_lib.escape(str(x or ""), quote=True)


def render_html(report):
    s = report["summary"]
    parts = ["""<!doctype html><html><head><meta charset="utf-8">
<title>Article Picture Pass — review</title><style>
body{font-family:Georgia,serif;background:#0B1D3A;color:#eee;
margin:0;padding:24px}h1{color:#D4A843;font-size:22px}
h2{font-size:17px;margin:0 0 4px}a{color:#D4A843}
.card{background:#12294d;border:1px solid #D4A84355;border-radius:10px;
padding:16px;margin:18px 0}.meta{color:#9db6d9;font-size:12px}
img{max-width:320px;border-radius:6px;display:block;margin:6px 0}
.prov{font-size:12px;color:#cfe0f5;background:#0B1D3A;padding:8px;
border-radius:6px;white-space:pre-wrap;word-break:break-word}
.grid{display:flex;gap:24px;flex-wrap:wrap}.col{flex:1;min-width:300px}
.tag{display:inline-block;background:#A32D2F;color:#fff;border-radius:4px;
padding:1px 7px;font-size:11px;margin-right:6px}
.tag.gold{background:#D4A843;color:#0B1D3A}.note{font-size:13px;color:#ffd98a}
</style></head><body>"""]
    parts.append(
        f"<h1>Article Picture Pass — {report['mode']} review</h1>"
        f"<p class='meta'>Generated {report['generated_at']} · "
        f"window {report['hours']}h · scanned "
        f"{s['articles_scanned']} · heroes filled "
        f"{s['heroes_filled']} · heroes replaced "
        f"{s['heroes_replaced']} · inlines proposed "
        f"{s['inlines_proposed']} · blocked skipped "
        f"{s['blocked_skipped']} · unchanged "
        f"{s['articles_unchanged']}</p>")
    for r in report["articles"]:
        h = r["hero"]
        parts.append("<div class='card'>")
        parts.append(
            f"<h2><a href='{_esc(r['url'])}'>"
            f"{_esc(r['headline'])}</a></h2>"
            f"<p class='meta'>{_esc(r['category'])} · "
            f"{_esc(r['published_at'])} · slug {_esc(r['slug'])}</p>")
        parts.append("<div class='grid'><div class='col'>"
                     "<b>BEFORE</b>")
        cur = h.get("current")
        if cur:
            parts.append(
                f"<img src='{_esc(cur['url'])}'>"
                f"<p class='meta'>hero width: "
                f"{_esc(cur.get('width'))}px</p>")
        else:
            parts.append("<p class='meta'>no hero image</p>")
        parts.append(
            f"<p class='meta'>inline figures: "
            f"{r['inlines']['existing']}</p></div>")
        parts.append("<div class='col'><b>PROPOSED</b>")
        parts.append(
            f"<p><span class='tag'>{_esc(h['action'])}</span>"
            f"{_esc(h['reason'])}</p>")
        if h.get("proposed"):
            p = h["proposed"]
            parts.append(f"<img src='{_esc(p['file_url'])}'>")
            parts.append(
                f"<div class='prov'>HERO — depicts: "
                f"{_esc(p['depicts'])}\nresolution: "
                f"{_esc(p['resolution'])}\nlicense: "
                f"{_esc(p['license'])}\nattribution: "
                f"{_esc(p['attribution'])}\nsource: "
                f"{_esc(p['source_page'])}\nverified: "
                f"{_esc(p['verified_how'])}\ncaption: "
                f"{_esc(h.get('caption'))}</div>")
        for p in r["inlines"]["proposed"]:
            parts.append(f"<img src='{_esc(p['file_url'])}'>")
            parts.append(
                f"<div class='prov'>INLINE — depicts: "
                f"{_esc(p['depicts'])}\nresolution: "
                f"{_esc(p['resolution'])}\nlicense: "
                f"{_esc(p['license'])}\nattribution: "
                f"{_esc(p['attribution'])}\nsource: "
                f"{_esc(p['source_page'])}\nverified: "
                f"{_esc(p['verified_how'])}\ncaption: "
                f"{_esc(p['caption'])}</div>")
        if not h.get("proposed") and not r["inlines"]["proposed"]:
            parts.append("<p class='meta'>no changes proposed</p>")
        parts.append("</div></div>")
        for n in r["notes"]:
            parts.append(f"<p class='note'>⚠ {_esc(n)}</p>")
        parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def run_pass(hours=12, max_articles=30, apply=False, net=None,
             log=print, report_path=None, html_path=None,
             articles=None, patch_fn=None):
    """One pass over recent articles. Dry-run by default: the
    patch function is never invoked unless apply=True."""
    if articles is None:
        articles = fetch_recent_articles(hours=hours,
                                         limit=max_articles)
    records = []
    for art in articles[:max_articles]:
        log(f"── {art.get('slug')}")
        try:
            rec = process_article(art, net=net, apply=apply,
                                  log=log, patch_fn=patch_fn)
        except Exception as e:  # one bad article never kills a run
            rec = {"id": art.get("id"), "slug": art.get("slug"),
                   "headline": art.get("headline") or "",
                   "category": art.get("category"),
                   "published_at": art.get("published_at"),
                   "url": "", "blocked": False, "entities": [],
                   "hero": {"action": "error", "reason": str(e),
                            "current": None, "proposed": None},
                   "inlines": {"existing": 0, "proposed": []},
                   "ledger": [], "notes": [f"error: {e}"[:200]],
                   "applied": []}
        records.append(rec)
        hp = rec["hero"].get("proposed")
        log(f"   hero: {rec['hero']['action']}"
            + (f" → {hp['resolution']} {hp['entity']}" if hp
               else "")
            + f" · inlines +{len(rec['inlines']['proposed'])}")
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if apply else "dry-run",
        "hours": hours,
        "summary": summarize(records),
        "articles": records,
    }
    rp = Path(report_path or STATE_DIR / "picture-pass-report.json")
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text(json.dumps(report, indent=1, default=str))
    hp_path = Path(html_path or STATE_DIR / "picture-pass-report.html")
    hp_path.write_text(render_html(report))
    log(f"\nreport: {rp}\nreview: {hp_path}")
    log(json.dumps(report["summary"], indent=1))
    return report


def main():
    ap = argparse.ArgumentParser(
        description="Enricher-side article picture pass "
                    "(entity-sourced hero + inline pictures)")
    ap.add_argument("--hours", type=int, default=12)
    ap.add_argument("--max", type=int, default=30)
    ap.add_argument("--apply", action="store_true",
                    help="PATCH proposals into Supabase "
                         "(default is dry-run report-only)")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicit dry-run (the default)")
    args = ap.parse_args()
    run_pass(hours=args.hours, max_articles=args.max,
             apply=bool(args.apply and not args.dry_run))
    return 0


if __name__ == "__main__":
    sys.exit(main())
