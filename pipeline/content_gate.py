#!/usr/bin/env python3
"""Pre-publish content gate — deterministic failure-case checks, shared
by every article insert path. Companion to source_gate.py.

ROOT-CAUSE PROGRAM part 2 (2026-10-30, from the GPT critique of the
Dallas BAPS article — see ~/workspace/research_notes/
gpt-brief-baps-2026-10-30/brief.md): reviewers kept catching the same
claim-construction failures AFTER publication. These checks move the
deterministic subset LEFT, to the insert choke point, so an article
carrying one is HELD (never inserted as published) — the same failure
semantics as the ≥2-source gate: fix the staged JSON and re-run.

All checks are deterministic regex/structure checks. No LLM calls, no
scoring, no thresholds. Each is deliberately CONSERVATIVE: it only
fires on the specific failure construction, and hedged/attributed
versions of the same claims pass.

Covered (brief failure cases d, e, and 5-related):
  1. unknown-value comparison — a concrete figure compared against an
     unknown placeholder ("to be determined", "TBD", "unknown",
     "not announced") in body text or data_cards. Brief case: the
     "2,000 pounds (2025) vs to be determined (2026)" card.
     SCHEMA NOTE (2026-10-30, BAPS acceptance test): the card scan is
     schema-agnostic — it evaluates comparison units across every card
     shape the pipeline actually emits (surveyed 6,202 cards: the
     polish/enrich `card_type`+`items[]` family, the writer
     `type`+`rows[]`/`dates[]`/`steps[]` family, and flat field dicts).
     The original scan keyed on `type` and treated one dict as one
     unit, so the live BAPS card (`card_type` + sibling `{name,
     value}` items) passed silently. Checks 2–5 were audited for the
     same assumption: they read body prose only and make no data-card
     schema assumptions; card-carried instances of those constructions
     are out of their scope by design (a card's label/value pairs carry
     no sentence context for attribution judgement).
  2. inferred admission — an event article affirmatively asserting
     free admission/entry with no attribution in the sentence.
     LIMIT (honest): sources at insert time carry only name+URL — the
     gate cannot read source pages — so it enforces the strongest
     checkable form of the rule: a free-admission claim must be
     ATTRIBUTED in text ("according to…", "organizers said…") or it
     is held for verification. An attributed claim the source does not
     actually support is NOT caught here (reviewer/LLM layer).
  3. sub-event start-time invention — a sub-attraction (fireworks,
     aarti, concert…) given a specific start time equal to the event's
     own end time. Catches the "event 3–8pm, fireworks begin at
     8 p.m." construction. LIMIT: only fires when the event's time
     range is itself stated in the body and the sentence carries no
     attribution; a legitimately scheduled closing-time start that is
     properly attributed passes, an unattributed one is held for a
     human to verify — by design.
  4. unestablished superlative lede — "season peaks", "biggest ever",
     "first of its kind" etc. in the OPENING paragraph with no
     attribution/hedge in the same sentence.
  5. estimate-as-fact attendance — in an article that frames its event
     as UPCOMING, an attendance figure stated with no expectation or
     attribution marker ("expected", "organizers say", "according
     to"…). LIMIT: post-event reportage is out of scope — once an
     event has happened, a turnout figure is a factual claim whose
     provenance a regex cannot judge; the check only runs when the
     body frames the event in the future, and explicitly historical
     sentences ("drew 12,000 last year") always pass.

NOT covered here (other parts of the program): image venue identity
and image rights (brief cases a–c — picture gate, part 3), related-
coverage relevance (case f — enforced as a hard filter in
related_coverage.find_related since 2026-10-31, not in this gate).
This module never touches images or related links.
"""
import html as _html
import re
from datetime import datetime

# ---------------------------------------------------------------- text utils

_ABBREV = [
    (r"\bp\.m\.", " pm"), (r"\ba\.m\.", " am"),
    (r"\bP\.M\.", " PM"), (r"\bA\.M\.", " AM"),
    (r"\bU\.S\.A\.", "USA"), (r"\bU\.S\.", "US"), (r"\bU\.K\.", "UK"),
    (r"\bSt\.", "St"), (r"\bMt\.", "Mt"), (r"\bDr\.", "Dr"),
    (r"\bNo\.", "No"), (r"\bvs\.", "vs"),
]


def _plain_text(body):
    """HTML body -> plain text with normalized whitespace."""
    if not body:
        return ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body,
                  flags=re.S | re.I)
    text = re.sub(r"</(p|div|li|h\d|tr|figure|blockquote)>", "\n", text,
                  flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = _html.unescape(text)
    return re.sub(r"[ \t]+", " ", text)


def _sentences(text):
    """Split plain text into sentences (abbreviation-tolerant enough
    for gate work: p.m./U.S. style abbreviations are normalized first
    so they don't fragment sentences)."""
    if not text:
        return []
    protected = text
    for pat, rep in _ABBREV:
        protected = re.sub(pat, rep, protected)
    out = []
    for para in protected.split("\n"):
        para = para.strip()
        if not para:
            continue
        parts = re.split(r"(?<=[.!?])\s+(?=[\"“(\[]?[A-Z0-9])", para)
        out.extend(p.strip() for p in parts if p.strip())
    return out


def _first_paragraph_text(body):
    """Plain text of the body's first paragraph (the lede)."""
    if not body:
        return ""
    m = re.search(r"<p[^>]*>(.*?)</p>", body, flags=re.S | re.I)
    chunk = m.group(1) if m else body
    return _plain_text(chunk).strip()


def _snippet(sentence, limit=130):
    s = " ".join(str(sentence).split())
    return s if len(s) <= limit else s[:limit - 1] + "…"


# ---------------------------------------------------------------- check 1

_PLACEHOLDER = re.compile(
    r"\b(to be determined|t\.?b\.?d\.?|yet to be announced|"
    r"not yet announced|not announced|to be announced|unknown)\b", re.I)
# Card values carry a wider placeholder vocabulary than prose: a
# value-position "TBC" / "to be confirmed" is the unknown side of a
# card. In PROSE the same words are routine fixture-schedule language
# ("Venue TBC", "opponent to be confirmed") next to team "vs" cues —
# the 2026-10-30 corpus scan false-fired on exactly those — so the
# prose check keeps the original conservative set above.
_CARD_PLACEHOLDER = re.compile(
    r"\b(to be determined|t\.?b\.?d\.?|yet to be (?:announced|determined)|"
    r"not yet (?:announced|determined)|not announced|to be announced|"
    r"to be confirmed|t\.?b\.?c\.?|unknown)\b", re.I)
_COMPARISON_CUE = re.compile(
    r"\b(vs\.?|versus|compared (?:to|with|against)|up from|down from|"
    r"outpac\w+|surpass\w+|higher than|lower than)\b", re.I)
_YEAR = re.compile(r"\b(?:19|20)\d\d\b")


def _has_number(s):
    return bool(re.search(r"\d", s or ""))


# --- card comparison units, across every emitted schema ----------------
#
# Surveyed shapes (2026-10-30; 6,202 cards in published + staged +
# built articles, 152 structural signatures):
#   polish/enrich family — card_type + card_title, items[] of
#     {label, value} (stat_grid), {name, value, numeric_value?}
#     (comparison), {date, event} (timeline), {text, stat?} /
#     {text, optional_stat} / plain strings (highlights); optional
#     hero_stat {value, label, trend?}.
#   writer family — type + title, price_compare headers[] + rows[] of
#     scalar lists; key_dates dates[] of {date, event} (variant:
#     items[] of {label, value}); how_to steps[] of {step, detail};
#     checklist items[] of {text, note?}; stat_grid/comparison
#     variants with items[] of {context, label, value} /
#     {display_value, label, value}; per-item context/note fields may
#     carry the figure ("vs 2,000 pounds in 2025").
#   flat dicts — match_scorecard, movie_review_ratings, recipe, and an
#     untyped {label, value, context} stat: no entry container; the
#     card's own scalar fields are its single entry.
#
# An ENTRY is one data point as a reader sees it (one item dict, one
# table row, the hero stat). An entry is a VALUE entry when it is a
# table row or carries a value-position field; prose entries (timeline
# events, highlight text without a stat, how-to steps, checklist text)
# are judged only within themselves — a schedule with one 'to be
# announced' entry among dated ones is an honest unknown, not half of
# a comparison. VALUE entries are parallel values for parallel
# subjects, so a placeholder in one while a concrete figure sits in a
# sibling is exactly the banned construction, whatever the card type
# is called.

_CARD_CONTAINERS = ("items", "rows", "dates", "steps")
_CARD_VALUE_FIELDS = ("value", "display_value", "stat", "optional_stat",
                      "optional stat", "numeric_value")

_DATE_TIME_SPAN = re.compile(
    r"\d{4}-\d{2}-\d{2}"                                   # ISO date
    r"|\d{1,2}/\d{1,2}(?:/\d{2,4})?"                       # 11/10/2026
    r"|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
    r"\s+\d{1,2}(?:st|nd|rd|th)?\b"                        # November 10
    r"|\b\d{1,2}(?:st|nd|rd|th)?\s+"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\b"
    r"|\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:[ap]\.?m\.?)?\b"    # 3:00 p.m.
    r"|\b\d{1,2}\s*[ap]\.?m\.?\b"                          # 8 p.m.
    r"|\b(?:19|20)\d\d\b",                                 # bare year
    re.I)
_MONEY_OR_PCT = re.compile(r"[$₹€£]\s*\d|\d\s*%")
_DIGIT_LETTER = re.compile(r"\d[a-zA-Z]")


def _has_quantity(s):
    """True when s carries a concrete figure — a quantity a reader
    could compare. Dates, clock times and bare years are NOT figures
    ('November 10, 2026', '3:00-8:00 p.m.'); a number counts when it
    is digit-grouped (2,000), 3+ digits (500), decimal (4.5),
    money/percent-adjacent ($10, 42%), or digit+unit (2000lbs). Bare
    1–2 digit counts ('50 seats') are deliberately not figures —
    conservative, as elsewhere in this gate."""
    if not s:
        return False
    if _MONEY_OR_PCT.search(s):
        return True
    residue = _DATE_TIME_SPAN.sub(" ", s)
    if _DIGIT_LETTER.search(residue):
        return True
    for tok in re.findall(r"\d[\d,]*(?:\.\d+)?", residue):
        if "," in tok or "." in tok or len(tok.replace(",", "")) >= 3:
            return True
    return False


def _has_value_figure(s):
    """Figure test for VALUE-position strings (a card entry's value /
    display_value / stat field, a table-row cell): once dates, clock
    times and bare years are stripped, any remaining digit is the
    entry's figure — including bare counts the prose-grade test
    ignores ('3 years', age '27', '60'). Producers park junk in
    numeric_value (0 for unknown, 1 for unranked, 2025 for a year),
    so that field never counts as a figure."""
    if not s:
        return False
    return bool(re.search(r"\d", _DATE_TIME_SPAN.sub(" ", s)))


def _entry_strings(el):
    """(strings, value_strings, is_value_entry) for one card entry.
    value_strings are the strings sitting in value positions, judged
    by _has_value_figure; numeric_value is excluded from them (see
    above) but still marks the entry as a value entry."""
    if isinstance(el, dict):
        strings, vstrings = [], []
        for k, v in el.items():
            if not isinstance(v, (str, int, float)) or isinstance(v, bool):
                continue
            strings.append(str(v))
            if k in _CARD_VALUE_FIELDS and k != "numeric_value":
                vstrings.append(str(v))
        is_value = any(k in el for k in _CARD_VALUE_FIELDS)
        return strings, vstrings, is_value
    if isinstance(el, list):
        cells = [str(v) for v in el
                 if isinstance(v, (str, int, float))
                 and not isinstance(v, bool)]
        # table row: every cell is a value position
        return cells, cells, True
    if isinstance(el, (str, int, float)) and not isinstance(el, bool):
        return [str(el)], [], False
    return [], [], False


def _card_entries(card):
    """All comparison entries of a card across the observed schemas."""
    entries = []
    for key in _CARD_CONTAINERS:
        v = card.get(key)
        if isinstance(v, list):
            entries.extend(_entry_strings(el) for el in v)
    hs = card.get("hero_stat")
    if isinstance(hs, dict):
        strings, vstrings, _ = _entry_strings(hs)
        entries.append((strings, vstrings, True))
    if not entries:
        # flat card: its own scalar fields are the single entry
        entries.append(_entry_strings(card))
    return entries


def _card_violation(card):
    """(figure, placeholder) if the card pairs a concrete figure with
    an unknown placeholder, else None. Fires when a placeholder and a
    figure share one entry (any entry kind), or when a placeholder
    sits in a value entry while any sibling value entry of the same
    card carries a figure."""
    value_figure = None
    value_placeholder = None
    for strings, vstrings, is_value in _card_entries(card):
        placeholder = next(
            (s for s in strings if _CARD_PLACEHOLDER.search(s)), None)
        figure = next((s for s in vstrings if _has_value_figure(s)), None)
        if figure is None:
            figure = next((s for s in strings if _has_quantity(s)), None)
        if placeholder and figure:
            return figure, placeholder
        if is_value:
            value_placeholder = value_placeholder or placeholder
            value_figure = value_figure or figure
    if value_placeholder and value_figure:
        return value_figure, value_placeholder
    return None


def check_unknown_value_comparison(article):
    """Brief case: '2,000 pounds in 2025' vs 'to be determined' in 2026 —
    a comparison with an unknown value is not a comparison."""
    failures = []
    # (a) data cards — every schema the pipeline emits (see survey
    # note above); the polish step's card_type + items[] shape is the
    # one the original type-keyed scan missed on the live BAPS card.
    cards = article.get("data_cards") or []
    if isinstance(cards, dict):
        cards = [cards]
    if isinstance(cards, list):
        for card in cards:
            if not isinstance(card, dict):
                continue
            hit = _card_violation(card)
            if not hit:
                continue
            figure, placeholder = hit
            card_type = str(card.get("card_type") or card.get("type")
                            or "")
            title = str(card.get("card_title") or card.get("title")
                        or card_type or "data card")
            failures.append(
                "unknown-value comparison: data card "
                f"'{title}' pairs '{_snippet(figure, 40)}' "
                f"with unknown placeholder '{_snippet(placeholder, 40)}' "
                "— a comparison containing an unknown value is "
                "not publishable; drop the card or the unknown side")
    # (b) body prose: placeholder in a sentence that also carries a
    # concrete figure AND a real comparison frame — a cue word
    # (vs/compared/up from…), or a 'while' contrast with figures on
    # both sides. (A bare year in the same sentence is NOT enough:
    # real-world scan 2026-10-30 flagged regulatory prose like
    # 'the 2026 Unified Agenda… effects unknown' on that basis.)
    for sent in _sentences(_plain_text(article.get("body"))):
        if not _PLACEHOLDER.search(sent) or not _has_number(sent):
            continue
        n_numbers = len(re.findall(r"\d[\d,\.]*", sent))
        if _COMPARISON_CUE.search(sent) or (
                re.search(r"\bwhile\b", sent, re.I) and n_numbers >= 2):
            failures.append(
                "unknown-value comparison: sentence compares a concrete "
                f"figure against an unknown value — '{_snippet(sent)}' — "
                "state the known figure alone or omit the comparison")
    return failures


# ---------------------------------------------------------------- check 2

_FREE_CLAIM = re.compile(
    r"\b(free admission|admission (?:is|will be) free|free entry|"
    r"entry (?:is|will be) free|free to attend|"
    r"admission (?:is )?free of charge|"
    r"no (?:admission|entry) (?:fee|charge)|"
    r"tickets? (?:are|is) free|"
    r"open to (?:the )?public free(?: of charge)?|"
    r"free for (?:all|visitors|everyone|the public))\b", re.I)
_ADMISSION_ATTRIBUTION = re.compile(
    r"\b(according to|organizers? (?:say|says|said|announced)|"
    r"organisers? (?:say|says|said|announced)|"
    r"(?:the )?(?:temple|mandir|venue|organizers?|organisers?|hosts?) "
    r"(?:said|says|announced|confirmed)|announced that|"
    r"per the|on its (?:website|site)|website states|"
    r"in a statement|press release)\b", re.I)
_UNCERTAINTY = re.compile(
    r"\b(whether|unknown|not (?:yet )?(?:announced|specified|confirmed)|"
    r"yet to be (?:announced|confirmed)|has not been announced|"
    r"have not been announced|not been (?:announced|confirmed)|"
    r"check (?:the|with))\b", re.I)


def check_inferred_admission(article):
    """An affirmative free-admission claim with no in-sentence
    attribution is an inference (the announcement not mentioning
    tickets does not establish free admission) — hold it."""
    failures = []
    for sent in _sentences(_plain_text(article.get("body"))):
        m = _FREE_CLAIM.search(sent)
        if not m:
            continue
        if m.start() > 0 and sent[m.start() - 1] == "-":
            # hyphenated compound, not an admission claim:
            # 'visa-free entry', 'duty-free entry' (trade/immigration)
            continue
        if _UNCERTAINTY.search(sent) or _ADMISSION_ATTRIBUTION.search(sent):
            continue
        # negated claim ("admission is not free", "…isn't free")
        before = sent[max(0, m.start() - 24):m.start()].rstrip().lower()
        if (before.endswith("not") or before.endswith("n't")
                or before.endswith("never")):
            continue
        failures.append(
            "inferred admission: the article asserts free admission "
            f"with no attribution — '{_snippet(sent)}' — missing ticket "
            "information does not establish free entry; attribute the "
            "claim to the organizer/venue source in the sentence or "
            "remove it")
    return failures


# ---------------------------------------------------------------- check 3

_TIME_TOKEN = r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?"
_RANGE_PATTERNS = [
    re.compile(r"\bfrom\s+" + _TIME_TOKEN + r"\s*(?:to|-|–|—)\s+" +
               _TIME_TOKEN, re.I),
    re.compile(r"\bbetween\s+" + _TIME_TOKEN + r"\s*and\s+" +
               _TIME_TOKEN, re.I),
    re.compile(r"\b" + _TIME_TOKEN + r"\s*(?:-|–|—)\s*" + _TIME_TOKEN,
               re.I),
]
_ATTRACTIONS = (
    r"fireworks|aarti|concert|parade|procession|performance|keynote|"
    r"lighting(?: ceremony)?|laser show|drone show|cultural program\w*|"
    r"musical evening|dance performance|light and sound(?: show)?")
_ATTRACTION = re.compile(r"\b(" + _ATTRACTIONS + r")\b", re.I)
_START_VERB = re.compile(
    r"\b(begin|begins|began|start|starts|started|kick off|kicks off|"
    r"commence|commences|gets underway)\b", re.I)
_TIME_IN_TEXT = re.compile(_TIME_TOKEN, re.I)
_SUBEVENT_ATTRIBUTION = re.compile(
    r"\b(according to|announced|organizers?|organisers?|"
    r"officials? (?:say|said)|press release|in a statement|"
    r"the (?:temple|mandir|venue|hosts?) (?:said|announced))\b", re.I)


def _to_minutes(hour, minute, meridiem, inherit=None):
    h = int(hour)
    mins = int(minute) if minute else 0
    mer = (meridiem or inherit or "").lower().replace(".", "")
    if mer == "pm" and h != 12:
        h += 12
    elif mer == "am" and h == 12:
        h = 0
    return h * 60 + mins


def _event_end_times(text):
    """All event end times (minutes since midnight) from time ranges
    stated in the text."""
    ends = set()
    for pat in _RANGE_PATTERNS:
        for m in pat.finditer(text):
            g = m.groups()
            # groups: (h1, m1, mer1, h2, m2, mer2)
            end = _to_minutes(g[3], g[4], g[5], inherit=g[2])
            if g[5] or g[2]:  # at least one meridiem anchors the range
                ends.add(end)
    return ends


def _sentence_times(sentence):
    out = []
    for m in _TIME_IN_TEXT.finditer(sentence):
        g = m.groups()
        if g[2] is None and not re.search(
                r"\b(at|from|begin\w*|start\w*)\s*$",
                sentence[max(0, m.start() - 12):m.start()], re.I):
            # bare number with no meridiem and no time preposition —
            # not a clock time we can trust
            continue
        out.append((m, _to_minutes(g[0], g[1], g[2])))
    return out


def check_subevent_start_time(article):
    """Event end time must not be converted into a sub-attraction's
    start time. Fires when a sentence gives an attraction a start (or
    an 'at <time>' slot) equal to the event's stated end time, with
    no attribution in the sentence."""
    text = _plain_text(article.get("body"))
    ends = _event_end_times(text)
    if not ends:
        return []
    failures = []
    for sent in _sentences(text):
        am = _ATTRACTION.search(sent)
        if not am:
            continue
        if _SUBEVENT_ATTRIBUTION.search(sent):
            continue
        for tm, minutes in _sentence_times(sent):
            if minutes not in ends:
                continue
            near = sent[am.start():tm.end() + 8]
            has_start = _START_VERB.search(near) is not None
            has_at = re.search(r"\bat\s*$", sent[max(0, tm.start() - 4):tm.start()]) is not None
            has_label = re.search(r":\s*$", sent[max(0, tm.start() - 3):tm.start()]) is not None
            if has_start or has_at or has_label:
                failures.append(
                    "sub-event start-time invention: "
                    f"'{am.group(0)}' is given a start time equal to the "
                    f"event's end time — '{_snippet(sent)}' — an event "
                    "end time is not a sub-event start time; attribute "
                    "the start time to the organizer's schedule or "
                    "state only that it closes the programme")
                break
    return failures


# ---------------------------------------------------------------- check 4

_SUPERLATIVE = re.compile(
    r"\b(season peaks|biggest ever|largest ever|"
    r"biggest in (?:its |the )?history|largest in (?:its |the )?history|"
    r"first of its kind|first-ever|most spectacular|grandest|"
    r"(?:biggest|largest|grandest|greatest) [^.!?]{0,45}?history|"
    r"the (?:biggest|largest|grandest|greatest) [^.!?]{0,50}? "
    r"in (?:its |the )?(?:history|the (?:state|city|country|region)))\b",
    re.I)
_SUPERLATIVE_CLEAR = re.compile(
    r"\b(expected|anticipated|billed as|described as|dubbed|"
    r"according to|organizers? (?:say|said)|organisers? (?:say|said)|"
    r"set to be|could be|poised to|aims to be)\b", re.I)


def check_superlative_lede(article):
    """An unestablished superlative/comparison in the opening
    paragraph ('Dallas-Fort Worth's Diwali season peaks…') is an
    editorial claim dressed as fact — it needs attribution or a
    hedge in the same sentence."""
    lede = _first_paragraph_text(article.get("body"))
    failures = []
    for sent in _sentences(lede):
        m = _SUPERLATIVE.search(sent)
        if m and not _SUPERLATIVE_CLEAR.search(sent):
            failures.append(
                "unestablished superlative in lede: "
                f"'{m.group(0)}' — '{_snippet(sent)}' — attribute the "
                "claim in the sentence ('organizers say…', 'billed "
                "as…') or remove it")
    return failures


# ---------------------------------------------------------------- check 5

_PREVIEW_FRAMING = re.compile(
    r"\b(will host|will be held|will take place|will celebrate|"
    r"will be celebrated|is scheduled|are scheduled|"
    r"scheduled (?:for|to)|set to (?:host|take place|begin|open)|"
    r"to be held|upcoming|will run from|will open on|"
    r"will be hosted)\b", re.I)
_ATTENDANCE = re.compile(
    r"(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?\s*(?:thousand|lakh|crore|million)|"
    r"\d{4,})\s+(?:more\s+)?"
    r"(visitors|attendees|devotees|guests|spectators|people|"
    r"participants|pilgrims|worshippers|fans)\b", re.I)
_EXPECTATION = re.compile(
    r"\b(expected|expecting|expects|anticipat\w+|estimat\w+|projected|"
    r"projection|forecast|according to|organizers?|organisers?|"
    r"officials? (?:say|said|expect)|could|may|might|up to|"
    r"set to|aim\w+|target\w*|hop\w+|are due|is due)\b", re.I)


def _is_historical(sentence):
    if re.search(r"\blast (year|diwali|edition|festival|season)\b",
                 sentence, re.I):
        return True
    if re.search(r"\bprevious (year|edition)\b", sentence, re.I):
        return True
    now_year = datetime.now().year
    for ym in re.finditer(r"\bin ((?:19|20)\d\d)\b", sentence, re.I):
        if int(ym.group(1)) < now_year:
            return True
    return False


def check_estimate_as_fact(article):
    """Expected attendance is not turnout. In an article framing its
    event as upcoming, an attendance figure with no expectation or
    attribution marker in the sentence states an estimate as fact."""
    text = _plain_text(article.get("body"))
    if not _PREVIEW_FRAMING.search(text):
        return []
    failures = []
    for sent in _sentences(text):
        m = _ATTENDANCE.search(sent)
        if not m:
            continue
        if _EXPECTATION.search(sent) or _is_historical(sent):
            continue
        if re.search(r"\b(serves?|covers?|supplies|supplying)\b[^.]{0,40}$",
                     sent[:m.start()], re.I):
            # utility/service coverage figure ('PJM serves about
            # 65 million people') — a population stat, not attendance
            continue
        if m.group(2) == "people" and not re.search(
                r"\b(attend\w+|gather\w+|turn\w* out|flock\w+|arriv\w+|"
                r"visit\w+|throng\w+|packed|congregat\w+)\b", sent, re.I):
            # bare 'N people' with no participation verb is usually a
            # population/employment/subscriber stat, not a turnout claim
            continue
        failures.append(
            "estimate stated as fact: attendance figure "
            f"'{m.group(0)}' has no expectation/attribution marker — "
            f"'{_snippet(sent)}' — expected attendance is not turnout; "
            "add the marker ('expected', 'organizers say', 'according "
            "to…') or remove the figure")
    return failures


# ---------------------------------------------------------------- API

_CHECKS = [
    check_unknown_value_comparison,
    check_inferred_admission,
    check_subevent_start_time,
    check_superlative_lede,
    check_estimate_as_fact,
]


class ContentGateError(Exception):
    """Raised when an article fails the pre-publish content gate."""


def check_article(article):
    """Return the list of content-gate failure reasons for an article
    dict (empty list = passes). Deterministic; never raises on
    malformed input — a non-dict yields no failures (field validation
    is the inserters' own job, as with source_gate)."""
    if not isinstance(article, dict):
        return []
    failures = []
    for fn in _CHECKS:
        try:
            failures.extend(fn(article))
        except Exception:
            # A check bug must never silently publish OR block the
            # pipeline opaquely: surface it as a failure to inspect.
            failures.append(f"content gate check error in {fn.__name__} "
                            "— inspect before publishing")
    return failures


def gate_failures(article):
    """Alias matching source_gate's naming: failures list (empty=pass)."""
    return check_article(article)


def assert_publishable(article, context="article"):
    """Raise ContentGateError listing every failure; else return True."""
    failures = check_article(article)
    if failures:
        raise ContentGateError(
            f"content gate HOLD for {context}: " + "; ".join(failures))
    return True
