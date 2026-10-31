#!/usr/bin/env python3
"""
picture_gate_shared.py — the identity gates SHARED by the
article picture pass (article_picture_pass.py) and the reel
entity sourcer (reel_entity_sourcing.py).

Single source of truth: the news-outlet blocklist, the person
namesake-gate vocabulary (domain tokens, context matching,
contradiction markers), the depicted-person title heuristic,
and the country/domain marker scan used to reject candidates
placed in a country the story is not about. These lived only
in article_picture_pass.py until 2026-10-27, which is exactly
how the reel sourcer — written earlier and never given the
gates — came to source Perm, Russia for a US PERM-program
story and a Moscow "White House" for Washington: the fix now
lives here so neither consumer can drift away from it again.

Pure stdlib (re / collections): no env, no network, no imports
from either consumer — consumers import THIS, never each
other (article_picture_pass imports reel_entity_sourcing, so
the reverse import would be circular).
"""
import re
from collections import Counter


# ── news outlets are sources, never picture subjects ─────────
# (Moved verbatim from article_picture_pass.py, 2026-10-27 —
# the Oct 26 runs sourced a Reuters vehicle + the Reuters
# Building for the entity 'Reuters', and a Jug Suraiya portrait
# for the entity 'Times of India'.)
OUTLET_ENTITIES = {
    "reuters", "associated press", "press trust of india",
    "bloomberg", "hindustan times", "times of india",
    "the times of india", "indian express", "the indian express",
    "the hindu", "ndtv", "bbc", "bbc news", "cnn",
    "al jazeera", "the guardian", "new york times",
    "the new york times", "washington post",
    "the washington post", "wall street journal",
    "the wall street journal", "financial times",
    "the financial times", "the economist", "dow jones",
    "cnbc", "fox news", "nbc news", "abc news",
    "deccan chronicle", "deccan herald", "tribune india",
    "the tribune", "telegraph india", "ani", "ians", "afp",
    "upi", "xinhua", "ap",
}


def is_outlet_entity(name):
    """True when the entity string names a news outlet (exact
    match, ignoring a leading 'the'). Outlets are cited
    sources, never picture subjects."""
    if not name:
        return False
    low = name.strip().lower()
    return low in OUTLET_ENTITIES \
        or low.removeprefix("the ") in OUTLET_ENTITIES


# ── language names are not visual entities ───────────────────
# (The 22-name list from social_card.py, commit 129c06101,
# moved here 2026-10-31 so the reel sourcer shares it: there
# is no photograph OF 'Hindi' — a search for one returns
# alphabet wall charts and token-coincidence junk; the
# Jailer 2 Hindi box-office reel sourced a Hindi alphabet
# chart and a language-speakers map for the entity 'Hindi'.)
LANGUAGE_ENTITIES = {
    "hindi", "english", "telugu", "tamil", "malayalam",
    "kannada", "bengali", "marathi", "punjabi", "gujarati",
    "urdu", "odia", "assamese", "sanskrit", "spanish",
    "french", "german", "arabic", "persian", "chinese",
    "japanese", "korean", "russian",
}


def is_language_entity(name):
    """True when the entity string is a language name.
    Languages are non-visual: they never source an image."""
    if not name:
        return False
    return name.strip().lower() in LANGUAGE_ENTITIES


# ── person namesake-gate vocabulary ──────────────────────────
# (Moved verbatim from article_picture_pass.py, 2026-10-27.)
HINT_FUNCTION_WORDS = {
    "where", "when", "what", "which", "while", "there", "their",
    "about", "would", "could", "should", "these", "those",
    "other", "more", "most", "many", "much", "such", "each",
    "every", "been", "were", "have", "will", "with", "from",
    "into", "onto", "upon", "over", "under", "after", "before",
    "again",
}

PERSON_DOMAIN_TOKENS = {
    "sports": ("cricket", "cricketer", "football", "soccer",
               "tennis", "hockey", "badminton", "kabaddi",
               "athlete", "olympic", "boxer", "boxing",
               "wrestler", "wrestling", "golfer", "sprinter",
               "chess", "squash", "baseball", "basketball",
               "weightlifting", "archery"),
    "entertainment": ("actor", "actress", "film", "cinema",
                      "singer", "singing", "musician", "director",
                      "composer", "bollywood", "hollywood"),
    "technology": ("engineer", "scientist", "researcher",
                   "professor", "founder", "programmer",
                   "astronaut", "executive", "entrepreneur"),
    "markets-finance": ("executive", "founder", "entrepreneur",
                        "businessman", "businesswoman", "investor",
                        "banker", "economist", "chief"),
    "news": ("politician", "minister", "diplomat", "ambassador",
             "activist", "official", "senator", "congressman"),
    "nri-world": ("politician", "minister", "diplomat",
                  "ambassador", "activist", "official",
                  "senator", "congressman"),
    "immigration": ("politician", "minister", "diplomat",
                    "ambassador", "activist", "official",
                    "lawyer", "judge"),
    "lifestyle-health": ("doctor", "physician", "surgeon",
                         "scientist", "researcher", "professor",
                         "chef"),
    "food": ("chef", "cook", "restaurateur"),
}


def ctx_token_match(hint_tok, ev_tokens):
    """Prefix-tolerant token agreement: 'cricket' matches the
    evidence token 'cricketers' (and vice versa) via a shared
    5-character stem; exact equality always matches."""
    if hint_tok in ev_tokens:
        return True
    if len(hint_tok) < 4:
        return False
    stem = hint_tok[:5]
    return any(t.startswith(stem) or hint_tok.startswith(t[:5])
               for t in ev_tokens if len(t) >= 4)


_TITLE_PHRASE_RE = re.compile(r"\bchief executive"
                              r"(?: officer)?\b", re.IGNORECASE)
_CHIEF_MINISTER_RE = re.compile(r"\bchief minister\b",
                                re.IGNORECASE)


def mask_title_phrases(text):
    """Mask job titles whose first word is a domain marker
    only in isolation. 'Chief executive (officer)' is ONE
    title headed by 'executive' — a token two domains share,
    so the title marks no single domain; a bare 'chief' (a
    fund chief, a police chief) still does. Without the mask,
    the contradiction scan reads the 'chief' of 'chief
    executive' as a markets-finance marker and rejects the
    story's own CEO on a technology story. The phrase is
    replaced by 'executive', so context agreement on the
    title still registers.

    'Chief Minister' (and 'Deputy Chief Minister') is the
    mirror-image trap on the AGREEMENT side: it is a
    POLITICAL office (news domain), but its bare 'chief'
    token satisfies the markets-finance domain vocabulary
    ('chief' as in fund chief / chief economist). Without
    the mask, a political felicitation photo of a bank CEO
    — '...with Deputy Chief Minister of Uttar Pradesh' —
    'agrees' with an earnings story's context on the word
    'chief' alone and passes the person namesake gate
    (2026-10-26: the IOB earnings story shipped two such
    self-published ceremony photos of its CEO as hero +
    inlines). The phrase is replaced by 'minister' — a
    token three domains share, so it can neither agree
    with a single domain nor contradict one. Matching is
    case-insensitive: file descriptions capitalise both
    phrases, and the un-masked capitals were exactly how
    the 2026-10-26 files slipped through."""
    t = _TITLE_PHRASE_RE.sub("executive", text or "")
    return _CHIEF_MINISTER_RE.sub("minister", t)


def domain_contradiction_markers(story_domain):
    """Profession/domain tokens that belong to OTHER domains
    only (a token shared by 2+ domains — 'founder', 'scientist'
    — marks no single domain and cannot contradict). An
    'actor' marker on a sports story's candidate is a
    contradiction; on an entertainment story it is agreement."""
    counts = Counter()
    for toks in PERSON_DOMAIN_TOKENS.values():
        counts.update(set(toks))
    story = set(PERSON_DOMAIN_TOKENS.get(story_domain or "", ()))
    return frozenset(t for t, n in counts.items()
                     if n == 1 and t not in story)


# ── depicted-person title heuristic ──────────────────────────
# (Adapted from article_picture_pass._depicted_person_name,
# 2026-10-27: the tokeniser is injected so each consumer keeps
# its own entity-token semantics — for both current consumers
# that is reel_entity_sourcing.entity_tokens.)
NAME_LEADERS = {"dr", "dr.", "mr", "mr.", "mrs", "mrs.", "ms",
                "shri", "smt", "prof", "prof."}


def title_core(title):
    core = (title or "").replace("File:", "", 1).strip()
    return re.sub(r"\.(jpe?g|png|gif|webp|tiff?)$", "", core,
                  flags=re.I).strip()


def head_segment(text):
    """The subject segment of a title/description: the text up
    to the first comma, parenthesis or dash."""
    return re.split(r"[,()—–]|\s-\s", text or "",
                    maxsplit=1)[0].strip()


def depicted_person_name(title, entity, tokens_fn):
    """When the file's title head is a portrait-style person
    name (2–4 capitalized words, optionally led by an honorific)
    that is NOT the entity, return the name. A posed portrait
    of a specific person cannot illustrate a non-person entity
    merely because the person is associated with it (Bryan
    Traynor for 'Breakthrough Prize'; Jug Suraiya for 'Times
    of India')."""
    head = head_segment(title_core(title))
    words = head.split()
    if words and words[0].lower() in NAME_LEADERS:
        words = words[1:]
    if not (2 <= len(words) <= 4):
        return None
    if not all(re.fullmatch(r"[A-Z][A-Za-z.'’\-]+", w)
               for w in words):
        return None
    name = " ".join(words)
    if set(tokens_fn(name)) & set(tokens_fn(entity)):
        return None
    return name


# ── country / domain markers ─────────────────────────────────
# Unambiguous place/domain markers per country: the country
# name, its demonym, its capital and major cities/regions, and
# (for the two home contexts of this newsroom) the institutions
# and programmes that place a text in that country as surely
# as a place name. Deliberately conservative: a marker must be
# hard to read as anything else ('white house' is NOT a US
# marker — Moscow has one too; 'georgia' is a country and a
# US state, so it is absent). The gate built on this scan only
# ever rejects on a POSITIVE foreign placement: a candidate
# whose evidence names no country is untouched by it.
COUNTRY_MARKERS = {
    "russia": ("russia", "russian", "moscow", "moskva",
               "perm krai", "kama river", "saint petersburg",
               "st. petersburg", "siberia", "kazan",
               "yekaterinburg", "novosibirsk", "vladivostok",
               "sochi", "volga"),
    "united states": ("united states", "u.s.", "u.s.a.", "usa",
                      "america", "american", "washington",
                      "district of columbia", "new york",
                      "california", "texas", "las vegas",
                      "nevada", "department of labor",
                      "labor department",
                      "department of homeland security",
                      "federal register", "green card", "h-1b",
                      "uscis", "eb-2", "eb-3", "capitol hill",
                      "pentagon", "wall street", "oval office"),
    "india": ("india", "indian", "new delhi", "delhi", "mumbai",
              "bombay", "bengaluru", "bangalore", "chennai",
              "madras", "kolkata", "calcutta", "hyderabad",
              "kerala", "tamil nadu", "gujarat", "maharashtra",
              "punjab", "bollywood", "rupee", "rupees", "crore",
              "lakh", "lok sabha", "rajya sabha"),
    "united kingdom": ("united kingdom", "u.k.", "britain",
                       "british", "london", "england",
                       "scotland", "wales"),
    "canada": ("canada", "canadian", "toronto", "vancouver",
               "ottawa", "ontario"),
    "australia": ("australia", "australian", "sydney",
                  "melbourne", "brisbane"),
    "china": ("china", "chinese", "beijing", "shanghai",
              "hong kong"),
    "japan": ("japan", "japanese", "tokyo", "osaka", "kyoto"),
    "france": ("france", "french", "paris"),
    "germany": ("germany", "german", "berlin", "munich"),
    "italy": ("italy", "italian", "rome", "milan", "venice"),
    "spain": ("spain", "spanish", "madrid", "barcelona"),
    "brazil": ("brazil", "brazilian", "rio de janeiro",
               "são paulo", "sao paulo"),
    "mexico": ("mexico", "mexican", "mexico city"),
    "pakistan": ("pakistan", "pakistani", "karachi", "lahore",
                 "islamabad"),
    "bangladesh": ("bangladesh", "bangladeshi", "dhaka"),
    "sri lanka": ("sri lanka", "sri lankan", "colombo"),
    "nepal": ("nepal", "nepali", "nepalese", "kathmandu"),
    "united arab emirates": ("united arab emirates", "emirates",
                             "dubai", "abu dhabi", "uae"),
    "singapore": ("singapore", "singaporean"),
    "poland": ("poland", "polish", "warsaw", "fotopolska"),
    "ukraine": ("ukraine", "ukrainian", "kyiv", "kiev"),
    "israel": ("israel", "israeli", "jerusalem", "tel aviv"),
    "korea": ("korea", "korean", "seoul"),
    "new zealand": ("new zealand", "auckland", "wellington"),
    "south africa": ("south africa", "south african",
                     "johannesburg", "cape town"),
    "netherlands": ("netherlands", "dutch", "amsterdam"),
    "switzerland": ("switzerland", "swiss", "zurich", "geneva"),
    "ireland": ("ireland", "irish", "dublin"),
}

_COUNTRY_RES = {
    key: re.compile(
        r"(?<![a-z0-9])(?:"
        + "|".join(re.escape(m) for m in markers)
        + r")(?![a-z0-9])")
    for key, markers in COUNTRY_MARKERS.items()
}


def countries_in(text):
    """The set of country keys a text positively places
    itself in, per COUNTRY_MARKERS. Empty when the text names
    no marked country/domain — which the gates read as 'no
    placement evidence', never as a contradiction."""
    if not text:
        return frozenset()
    low = text.lower()
    return frozenset(k for k, rx in _COUNTRY_RES.items()
                     if rx.search(low))
