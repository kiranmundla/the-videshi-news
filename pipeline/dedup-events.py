#!/usr/bin/env python3
"""
Deduplicate events in the Videshi events table.

Groups future events by (date, normalized_venue, city, state) and identifies
duplicates within each group by:
  1. exact content-fingerprint match (identity — always merges), or
  2. exact title match after suffix normalization, or
  3. CONSERVATIVE fuzzy title match (added 2026-10-14, Kiran: the same
     Pancham Beats Garba at Shubham Halls was listed 4x — allevents x2 +
     sulekha x2 — under different titles and slipped past exact matching).

Fuzzy matching stays deliberately narrow because fuzzy matching burned us
before (2026-10-12: Josh Wolf vs Luenell at the same club on the same night,
Screening #3 vs #4, 2pm vs 6pm shows, Skanda Sashti vs Soorasamharam,
In-Person vs Online sessions). A fuzzy merge requires ALL of:
  - same (date, normalized venue, city, state) group,
  - start times within 90 minutes when both parse (missing times demand
    much stronger title evidence),
  - strong title agreement on content tokens (filler, venue/city names,
    years stripped; OCR-split letters like "NI G H T" rejoined): overlap
    coefficient >= 0.6, Jaccard >= 0.25, >= 2 shared content tokens, and
    at least one shared token that is not an ultra-generic word,
  - no conflicts: titles differing only in showtime/session, differing
    edition numbers (#3 vs #4, Session 1 vs 2), online-vs-in-person mode
    mismatch, organizers that contradict each other (both present,
    disjoint, and neither corroborated by the other's title/description),
    a start time embedded in one title that contradicts the other
    listing's time, or a "distinctive difference": each title naming a
    content word the other lacks (Fashion vs Finance networking, Parade
    vs Vendor application, Self-Guided vs Shuttle tour) — the template-
    series pattern, where a shared boilerplate title dominates token
    overlap but the differing word IS the product. Cross-source dupes
    instead look like one title being (nearly) a subset of the other,
    the longer one only adding description, never a rival subject.
Clusters containing a fuzzy edge are re-validated as a whole (every pair
shares a content token or an exact/fingerprint link; time spread <= 120
min) or the fuzzy edges are dropped.

Keeps the event with the most complete data (plus a bonus when its
organizer is corroborated by a sibling listing's title), fills fields the
keeper lacks from the duplicates (never overwrites good data), deletes the
rest, and appends a recovery record per deletion to
pipeline/reports/event-dedup-YYYY-MM-DD.jsonl.

Usage:
    python3 -u pipeline/dedup-events.py              # live run
    python3 -u pipeline/dedup-events.py --dry-run    # preview only
"""

import json, os, re, subprocess, sys, unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────
DRY_RUN = "--dry-run" in sys.argv
SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
REPORTS_DIR = Path(__file__).resolve().parent / "reports"

# Fuzzy thresholds (see module docstring — do not loosen casually)
FUZZY_MAX_TIME_GAP_MIN = 90        # both times parse: max start-time gap
FUZZY_MAX_CLUSTER_SPREAD_MIN = 120  # whole-cluster time spread cap
FUZZY_MIN_OVERLAP = 0.6            # |A∩B| / min(|A|,|B|) on content tokens
FUZZY_MIN_JACCARD = 0.25
FUZZY_MIN_SHARED = 2               # shared content tokens
# When a start time is missing, title evidence must be much stronger:
FUZZY_NOTIME_MIN_OVERLAP = 0.8
FUZZY_NOTIME_MIN_JACCARD = 0.4
FUZZY_NOTIME_MIN_SHARED = 3

# Venues that are placeholders, not real locations — skip grouping on these
GENERIC_VENUES = frozenset([
    "location provided after booking",
    "refer eventbrite ticket link",
    "regus center",
    "online",
    "virtual",
    "tbd",
    "to be announced",
])

# Title words that carry no event identity (dropped before token compare)
FILLER_TOKENS = frozenset([
    "the", "a", "an", "and", "of", "in", "at", "on", "for", "with", "by",
    "to", "presents", "presented", "present", "live", "night", "nights",
    "evening", "event", "events", "special", "bay", "area", "usa", "us",
])

# Shared tokens from this set alone are too weak to prove sameness
GENERIC_CONTENT_TOKENS = frozenset([
    "yoga", "meditation", "comedy", "concert", "show", "party", "festival",
    "fest", "music", "dance", "dancing", "class", "classes", "workshop",
    "meetup", "dinner", "brunch", "celebration", "puja", "aarti", "temple",
    "tour", "expo", "fair", "market", "league", "game", "match", "night",
    "live", "day", "fest", "celebrations", "program", "programme",
])

# Spelling variants folded to a canonical token
TOKEN_FOLDS = {"dandiya": "dandia"}

MODE_TOKENS = frozenset(["online", "virtual", "zoom", "webinar"])

# Words exempt from the distinctive-difference guard: they describe
# packaging/format, not the event's subject, so a title having one that
# the other lacks proves nothing. Deliberately much narrower than
# GENERIC_CONTENT_TOKENS — a word can be weak as SHARED evidence yet
# decisive as a DIFFERENCE ("Music ... Networking" vs "Finance ...
# Networking" are different listings; "music" must count there).
DIFFERENCE_EXEMPT_TOKENS = frozenset([
    "free", "annual", "daytime", "outdoor", "outdoors", "indoor",
    "guided", "community", "official", "beginner", "friendly",
    "featuring", "party", "bash",
])

# Location words are never a "distinctive difference" (titles vary in how
# they name the same place: NYC vs Manhattan, -in-City suffixes, ...).
STATIC_GEO_TOKENS = frozenset([
    "nyc", "manhattan", "brooklyn", "queens", "bronx", "downtown",
    "uptown", "midtown", "hudson",
    # US state names (tokenized) and codes:
    "alabama", "al", "alaska", "ak", "arizona", "az", "arkansas", "ar",
    "california", "ca", "colorado", "co", "connecticut", "ct",
    "delaware", "de", "florida", "fl", "georgia", "ga", "hawaii", "hi",
    "idaho", "id", "illinois", "il", "indiana", "in", "iowa", "ia",
    "kansas", "ks", "kentucky", "ky", "louisiana", "la", "maine", "me",
    "maryland", "md", "massachusetts", "ma", "michigan", "mi",
    "minnesota", "mn", "mississippi", "ms", "missouri", "mo", "montana",
    "mt", "nebraska", "ne", "nevada", "nv", "hampshire", "nh", "jersey",
    "nj", "mexico", "nm", "york", "ny", "carolina", "nc", "sc",
    "dakota", "nd", "sd", "ohio", "oh", "oklahoma", "ok", "oregon",
    "or", "pennsylvania", "pa", "rhode", "ri", "tennessee", "tn",
    "texas", "tx", "utah", "ut", "vermont", "vt", "virginia", "va",
    "washington", "wa", "wisconsin", "wi", "wyoming", "wy", "dc",
])

# ── Supabase helpers ─────────────────────────────────────────────────────
def sb_get(endpoint, params, range_header=None):
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{SB_URL}/rest/v1/{endpoint}?{qs}"
    cmd = [
        "curl", "-s", url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
    ]
    if range_header:
        cmd += ["-H", f"Range: {range_header}"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        print(f"  WARNING: Failed to parse response: {r.stdout[:200]}")
        return []


def sb_delete(ids):
    if not ids:
        return 0
    id_filter = ",".join(ids)
    url = f"{SB_URL}/rest/v1/events?id=in.({id_filter})"
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "DELETE", url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    code = r.stdout.strip()
    if code in ("200", "204"):
        return len(ids)
    else:
        print(f"  WARNING: Delete failed (HTTP {code}) for {len(ids)} events")
        return 0


def sb_patch(event_id, payload):
    if not payload:
        return True
    url = f"{SB_URL}/rest/v1/events?id=eq.{event_id}"
    cmd = [
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "PATCH", url,
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(payload),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    code = r.stdout.strip()
    if code in ("200", "204"):
        return True
    print(f"  WARNING: Patch failed (HTTP {code}) for event {event_id}: {list(payload)}")
    return False


# ── Normalization ────────────────────────────────────────────────────────
def normalize_venue(name):
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r",\s*(usa|u\.s\.a\.?)\s*$", "", s)
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Generic venue-type words that sources append inconsistently
# ("230 Fifth Rooftop" vs "230 Fifth Rooftop Bar", "Astra Rooftop" vs
# "Astra Miami Rooftop"). Used ONLY to build the grouping core below.
VENUE_TYPE_TOKENS = frozenset([
    "bar", "rooftop", "club", "nightclub", "lounge", "hall", "halls",
    "center", "centre", "hotel", "restaurant", "grill", "cafe", "pub",
    "tavern", "brewery", "winery", "theater", "theatre", "venue",
    "ballroom", "pavilion", "garden", "gardens", "museum", "inn",
    "suites", "resort", "casino",
])


def venue_group_core(normalized_venue, city):
    """Grouping core for a normalized venue: drop the city token when it
    is embedded in the name ("astra miami rooftop" in Miami) and strip
    trailing generic venue-type words ("230 fifth rooftop bar" ->
    "230 fifth"). Two names land in one group only if they reduce to
    the same core; all merge guards still apply within the group."""
    toks = normalized_venue.split()
    city_toks = set((city or "").lower().split())
    toks = [t for t in toks if t not in city_toks]
    while toks and toks[-1] in VENUE_TYPE_TOKENS:
        toks.pop()
    return " ".join(toks) if toks else normalized_venue


def strip_title_suffix(title):
    """Strip location, platform, and date suffixes for comparison."""
    if not title:
        return ""
    s = title.lower().strip()
    s = s.replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", '"')
    # Strip trailing platform/org markers
    s = re.sub(r"\s*[|–]\s*(cozymeal|eventbrite|meetup|sulekha).*$", "", s, flags=re.I)
    # Strip trailing "in City, ST" patterns
    s = re.sub(r"\s+in\s+[A-Za-z\s,\.]+,\s*[A-Z]{2}\b.*$", "", s, flags=re.I)
    # Strip trailing "@ Venue"
    s = re.sub(r"\s*@\s*\S.*$", "", s)
    # Strip trailing " | City | Date" chains
    s = re.sub(r"\s*\|\s*[A-Za-z]+\s*\|.*$", "", s)
    # Strip date patterns
    s = re.sub(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(st|nd|rd|th)?\b", "", s, flags=re.I)
    # Strip day-of-week prefixes
    s = re.sub(r"^(monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s*", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def titles_differ_only_in_time(t1, t2):
    """True if titles are identical except for time patterns (different showtimes)."""
    time_pat = re.compile(r'\b\d{1,2}:\d{2}\s*(am|pm)?\b', re.I)
    s1 = time_pat.sub("TIME", t1.lower().strip())
    s2 = time_pat.sub("TIME", t2.lower().strip())
    # Both must have had times, and replacing times makes them equal
    return s1 == s2 and time_pat.search(t1.lower()) and time_pat.search(t2.lower())


def titles_differ_only_in_session(t1, t2):
    """True if titles are identical except for session/part/episode numbers.

    Numbered sessions (e.g. 'BNP Paribas Open: Session 1' vs 'Session 2') are
    distinct events, not duplicates — same rule as different showtimes.
    """
    sess_pat = re.compile(r'\b(session|part|episode|day)\s*\d+\b', re.I)
    s1 = sess_pat.sub("SESSION", t1.lower().strip())
    s2 = sess_pat.sub("SESSION", t2.lower().strip())
    # Both must have had session markers, and replacing them makes titles equal
    return s1 == s2 and sess_pat.search(t1.lower()) and sess_pat.search(t2.lower())


def stripped_titles_equal(t1, t2):
    """True if titles are identical after suffix normalization — same event."""
    n1, n2 = strip_title_suffix(t1), strip_title_suffix(t2)
    return bool(n1) and bool(n2) and n1 == n2


def title_similarity(t1, t2):
    n1 = strip_title_suffix(t1)
    n2 = strip_title_suffix(t2)
    if not n1 or not n2:
        return 0.0
    return SequenceMatcher(None, n1, n2).ratio()


# ── Fuzzy matching (2026-10-14) ──────────────────────────────────────────
def parse_time_minutes(t):
    """Parse a start time ('19:30', '7:30 PM', '9:00 AM - 5:00 PM') to
    minutes since midnight, or None if unparseable."""
    if not t:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)?", str(t), flags=re.I)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        mer = (m.group(3) or "").lower()
        if mer == "pm" and h < 12:
            h += 12
        elif mer == "am" and h == 12:
            h = 0
        if h > 23 or mi > 59:
            return None
        return h * 60 + mi
    m = re.search(r"\b(\d{1,2})\s*(am|pm)\b", str(t), flags=re.I)
    if m:
        h = int(m.group(1))
        if m.group(2).lower() == "pm" and h < 12:
            h += 12
        elif m.group(2).lower() == "am" and h == 12:
            h = 0
        return h * 60
    return None


def _raw_tokens(text):
    if not text:
        return []
    s = unicodedata.normalize("NFKD", str(text))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("&amp;", " ").replace("&#39;", "'").replace("&quot;", " ")
    return re.findall(r"[a-z0-9]+", s)


def _rejoin_ocr(tokens):
    """Rejoin letter-spaced OCR tokens: ['ni','g','h','t'] -> ['night'].
    Runs of >=3 tokens each <=2 chars are joined when the result is a
    plausible word length; leftover single chars are dropped."""
    out, run = [], []

    def flush():
        if len(run) >= 3:
            joined = "".join(run)
            if 3 <= len(joined) <= 10:
                out.append(joined)
                return
        out.extend(t for t in run if len(t) > 1)

    for tok in tokens:
        if len(tok) <= 2:
            run.append(tok)
        else:
            flush()
            run = []
            out.append(tok)
    flush()
    return out


def title_content_tokens(event):
    """Content tokens of a title: OCR-rejoined, spelling-folded, with
    filler words, years, and the event's own venue/city/state tokens
    removed (location words are not event identity)."""
    title = re.sub(r"\S+\.(?:com|in|co|net|org)\b", " ", event.get("title") or "")
    toks = _rejoin_ocr(_raw_tokens(title))
    drop = set(FILLER_TOKENS)
    for field in ("venue_name", "city", "state"):
        drop.update(_raw_tokens(event.get(field)))
    out = set()
    for tok in toks:
        if tok in drop or len(tok) < 2:
            continue
        if re.fullmatch(r"(19|20)\d{2}", tok):
            continue
        tok = TOKEN_FOLDS.get(tok, tok)
        if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss"):
            tok = tok[:-1]
        out.add(tok)
    return out


def title_embedded_times(title):
    """Start times embedded in a title ('7PM', '715P', '7:30 PM').
    Strong facts: organizers put them there because they matter."""
    s = (title or "").lower()
    out = set()
    for h, mi, mer in re.findall(r"(\d{1,2}):(\d{2})\s*(am|pm)", s):
        h = int(h)
        if mer == "pm" and h < 12:
            h += 12
        elif mer == "am" and h == 12:
            h = 0
        out.add(h * 60 + int(mi))
    for digits, mer in re.findall(r"\b(\d{3,4})\s*([ap])\b", s):
        h, mi = int(digits[:-2]), int(digits[-2:])
        if 1 <= h <= 12 and mi < 60:
            if mer == "p" and h < 12:
                h += 12
            elif mer == "a" and h == 12:
                h = 0
            out.add(h * 60 + mi)
    for h, mer in re.findall(r"\b(\d{1,2})\s*([ap])m\b", s):
        h = int(h)
        if mer == "p" and h < 12:
            h += 12
        elif mer == "a" and h == 12:
            h = 0
        out.add(h * 60)
    return out


def edition_numbers(title):
    """Edition/session numbers that distinguish otherwise-identical titles
    ('Screening #3', 'Session 2', 'Part 1')."""
    s = (title or "").lower()
    nums = set(int(n) for n in re.findall(r"#\s*(\d+)", s))
    nums.update(int(n) for n in re.findall(
        r"\b(?:session|part|episode|screening|round|vol(?:ume)?)\s*#?\s*(\d+)", s))
    return nums


def _organizer_tokens(org):
    return set(t for t in _raw_tokens(org) if len(t) >= 3)


def organizers_conflict(e1, e2):
    """Both rows name an organizer, the names share nothing, and neither
    is corroborated by the other listing's title/description — treat as
    different promoters running different events, do not merge.
    (Person-vs-org variants, e.g. 'Atul Shah' vs 'Pancham Beats' where one
    listing's description names the other, are NOT conflicts.)"""
    o1, o2 = _organizer_tokens(e1.get("organizer")), _organizer_tokens(e2.get("organizer"))
    if not o1 or not o2 or (o1 & o2):
        return False
    text1 = f"{e1.get('title') or ''} {e1.get('description') or ''} {e1.get('long_description') or ''}".lower()
    text2 = f"{e2.get('title') or ''} {e2.get('description') or ''} {e2.get('long_description') or ''}".lower()
    corr1 = any(t in text2 for t in o1)  # e1's organizer named in e2's text
    corr2 = any(t in text1 for t in o2)  # e2's organizer named in e1's text
    return not (corr1 or corr2)


def fuzzy_match(e1, e2):
    """Conservative same-event test for two rows in the same
    (date, venue, city, state) group. Returns (ok, reason_dict)."""
    t1, t2 = e1.get("title") or "", e2.get("title") or ""
    reason = {}

    # Hard conflicts first — the 2026-10-12 false-merge classes.
    if titles_differ_only_in_time(t1, t2):
        return False, {"block": "differ-only-in-time"}
    if titles_differ_only_in_session(t1, t2):
        return False, {"block": "differ-only-in-session"}
    n1, n2 = edition_numbers(t1), edition_numbers(t2)
    if n1 and n2 and n1 != n2:
        return False, {"block": f"edition-numbers {sorted(n1)} vs {sorted(n2)}"}
    if bool(MODE_TOKENS & set(_raw_tokens(t1))) != bool(MODE_TOKENS & set(_raw_tokens(t2))):
        return False, {"block": "online-vs-in-person"}
    if organizers_conflict(e1, e2):
        return False, {"block": "organizer-conflict"}
    # A start time embedded in a title is a strong fact: if it puts the
    # two listings more than 45 min apart, they are different sessions
    # (e.g. the 18:00 'Yoga class' vs the 19:15 'TUES 715P Yoga class').
    times1 = title_embedded_times(t1) | {m for m in [parse_time_minutes(e1.get("time"))] if m is not None}
    times2 = title_embedded_times(t2) | {m for m in [parse_time_minutes(e2.get("time"))] if m is not None}
    if times1 and times2:
        closest = min(abs(x - y) for x in times1 for y in times2)
        if closest > 45:
            return False, {"block": f"title/field time conflict ({closest}m apart)"}

    # Start-time proximity.
    m1, m2 = parse_time_minutes(e1.get("time")), parse_time_minutes(e2.get("time"))
    if m1 is not None and m2 is not None:
        gap = abs(m1 - m2)
        reason["time_gap_min"] = gap
        if gap > FUZZY_MAX_TIME_GAP_MIN:
            return False, {"block": f"time-gap {gap}m"}
        min_overlap, min_jac, min_shared = FUZZY_MIN_OVERLAP, FUZZY_MIN_JACCARD, FUZZY_MIN_SHARED
    else:
        reason["time_gap_min"] = None
        min_overlap, min_jac, min_shared = (FUZZY_NOTIME_MIN_OVERLAP,
                                            FUZZY_NOTIME_MIN_JACCARD,
                                            FUZZY_NOTIME_MIN_SHARED)

    # Title agreement on content tokens.
    a, b = title_content_tokens(e1), title_content_tokens(e2)
    if len(a) < 2 or len(b) < 2:
        return False, {"block": "too-few-content-tokens"}
    shared = a & b
    overlap = len(shared) / min(len(a), len(b))
    jaccard = len(shared) / len(a | b)
    distinctive = shared - GENERIC_CONTENT_TOKENS
    reason.update({"shared": sorted(shared), "overlap": round(overlap, 2),
                   "jaccard": round(jaccard, 2)})
    if len(shared) < min_shared:
        return False, {**reason, "block": "too-few-shared"}
    if not distinctive and len(shared) < 3:
        return False, {**reason, "block": "shared-only-generic"}
    if overlap < min_overlap:
        return False, {**reason, "block": "overlap-too-low"}
    # Distinctive-difference guard: if EACH title names a content word
    # the other lacks, the two listings identify different subjects that
    # merely share boilerplate (Fashion vs Finance networking, Parade vs
    # Vendor application, Design Awards Tickets vs Sponsorships). Real
    # cross-source dupes are subset-shaped: the difference sits on one
    # side only (extra description), never rival subjects on both.
    geo = set(STATIC_GEO_TOKENS)
    for e in (e1, e2):
        for field in ("venue_name", "city", "state"):
            geo.update(_raw_tokens(e.get(field)))

    def distinctive_only(side):
        return {t for t in side
                if t not in DIFFERENCE_EXEMPT_TOKENS and t not in geo
                and len(t) >= 3 and not t.isdigit()}

    only1, only2 = distinctive_only(a - b), distinctive_only(b - a)
    reason["only1"] = sorted(only1)
    reason["only2"] = sorted(only2)
    if only1 and only2:
        return False, {**reason, "block": "distinctive-difference"}
    jac_floor = min_jac
    if e1.get("image_url") and e1.get("image_url") == e2.get("image_url"):
        jac_floor = min(jac_floor, 0.2)  # identical poster corroborates
        reason["same_image"] = True
    if jaccard < jac_floor:
        return False, {**reason, "block": "jaccard-too-low"}
    return True, reason


# ── Scoring ──────────────────────────────────────────────────────────────
def completeness_score(event):
    score = 0
    if event.get("image_url"):
        score += 3
    if event.get("organizer"):
        score += 2
    desc = event.get("description") or ""
    score += min(len(desc) / 100, 3)
    long_desc = event.get("long_description") or ""
    score += min(len(long_desc) / 200, 2)
    if event.get("ticket_url"):
        score += 1
    if event.get("price_range"):
        score += 1
    if event.get("latitude") and event.get("longitude"):
        score += 1
    source_pref = {"eventbrite": 2, "sulekha": 1.5, "web": 1.5, "meetup": 1, "allevents": 0.5, "ticketmaster": 0.5}
    score += source_pref.get(event.get("source", ""), 0)
    return score


def keeper_score(event, cluster):
    """Completeness + cross-source corroboration: an organizer named in a
    sibling listing's title (+1) or description (+0.5) is likelier the
    canonical record (e.g. 'Pancham Beats' vs a contact person's name)."""
    score = completeness_score(event)
    org = _organizer_tokens(event.get("organizer"))
    if org and len(cluster) > 1:
        title_hit = desc_hit = False
        for other in cluster:
            if other is event:
                continue
            if org & set(_raw_tokens(other.get("title"))):
                title_hit = True
            elif any(t in f"{other.get('description') or ''} {other.get('long_description') or ''}".lower() for t in org):
                desc_hit = True
        score += 1.0 if title_hit else (0.5 if desc_hit else 0.0)
    return score


# Fields the keeper may inherit from duplicates when its own are empty.
FILL_IF_EMPTY = ["image_url", "ticket_url", "organizer", "price_range",
                 "street_address", "venue_images", "category", "time"]


def build_keeper_patch(keeper, dupes):
    """Fill only what the keeper lacks (or has clearly worse), from the
    best-scored duplicates. Never overwrites a present, good value."""
    patch = {}
    ranked = sorted(dupes, key=completeness_score, reverse=True)
    for field in FILL_IF_EMPTY:
        if not keeper.get(field):
            for d in ranked:
                if d.get(field):
                    patch[field] = d[field]
                    break
    # description: fill if empty, or swap in a much fuller one when the
    # keeper's is a stub (<60 chars).
    kdesc = keeper.get("description") or ""
    longest = max((d.get("description") or "" for d in dupes), key=len, default="")
    if not kdesc or (len(kdesc) < 60 and len(longest) > len(kdesc)):
        if longest:
            patch["description"] = longest
    kld = keeper.get("long_description") or ""
    longest_ld = max((d.get("long_description") or "" for d in dupes), key=len, default="")
    if not kld or (len(kld) < 400 and len(longest_ld) >= 2 * max(len(kld), 1)):
        if longest_ld:
            patch["long_description"] = longest_ld
    # Coordinates travel as a pair.
    if not (keeper.get("latitude") and keeper.get("longitude")):
        for d in ranked:
            if d.get("latitude") and d.get("longitude"):
                patch["latitude"], patch["longitude"] = d["latitude"], d["longitude"]
                break
    return patch


# ── Clustering ───────────────────────────────────────────────────────────
class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def cluster_group(events):
    """Cluster one (date, venue, city, state) group. Returns a list of
    clusters (each a list of events, size >= 2) with the match types and
    fuzzy reasons that formed them."""
    n = len(events)
    dsu = DSU(n)
    edge_types = defaultdict(set)   # (i, j) -> {"fingerprint"|"exact"|"fuzzy"}
    fuzzy_reasons = {}

    def add_edge(i, j, kind, reason=None):
        dsu.union(i, j)
        edge_types[(min(i, j), max(i, j))].add(kind)
        if reason is not None:
            fuzzy_reasons[(min(i, j), max(i, j))] = reason

    for i in range(n):
        for j in range(i + 1, n):
            e1, e2 = events[i], events[j]
            # Fingerprint identity merges unconditionally (as before).
            if e1.get("content_fingerprint") and e1["content_fingerprint"] == e2.get("content_fingerprint"):
                add_edge(i, j, "fingerprint")
                continue
            if titles_differ_only_in_time(e1["title"], e2["title"]):
                continue
            if titles_differ_only_in_session(e1["title"], e2["title"]):
                continue
            if stripped_titles_equal(e1["title"], e2["title"]):
                add_edge(i, j, "exact")
                continue
            ok, reason = fuzzy_match(e1, e2)
            if ok:
                add_edge(i, j, "fuzzy", reason)

    comps = defaultdict(list)
    for i in range(n):
        comps[dsu.find(i)].append(i)

    clusters = []
    for members in comps.values():
        if len(members) < 2:
            continue
        types = set()
        reasons = []
        for (i, j), kinds in edge_types.items():
            if i in members and j in members:
                types |= kinds
                if (i, j) in fuzzy_reasons:
                    reasons.append(fuzzy_reasons[(i, j)])
        # Whole-cluster validation for fuzzy-linked clusters: every pair
        # must share a content token (or an exact/fingerprint link) and
        # the time spread must stay within the cap. Otherwise drop back
        # to exact/fingerprint-only components.
        if "fuzzy" in types:
            valid = True
            minutes = [parse_time_minutes(events[i].get("time")) for i in members]
            known = [m for m in minutes if m is not None]
            if len(known) >= 2 and max(known) - min(known) > FUZZY_MAX_CLUSTER_SPREAD_MIN:
                valid = False
            if valid:
                token_sets = {i: title_content_tokens(events[i]) for i in members}
                for x in range(len(members)):
                    for y in range(x + 1, len(members)):
                        i, j = members[x], members[y]
                        kinds = edge_types.get((min(i, j), max(i, j)), set())
                        if kinds & {"exact", "fingerprint"}:
                            continue
                        if not (token_sets[i] & token_sets[j]):
                            valid = False
            if not valid:
                sub = DSU(len(members))
                for x in range(len(members)):
                    for y in range(x + 1, len(members)):
                        i, j = members[x], members[y]
                        kinds = edge_types.get((min(i, j), max(i, j)), set())
                        if kinds & {"exact", "fingerprint"}:
                            sub.union(x, y)
                subs = defaultdict(list)
                for x, i in enumerate(members):
                    subs[sub.find(x)].append(i)
                for sub_members in subs.values():
                    if len(sub_members) >= 2:
                        clusters.append({"events": [events[i] for i in sub_members],
                                         "types": {"exact/fingerprint (fuzzy rejected)"},
                                         "reasons": []})
                continue
        clusters.append({"events": [events[i] for i in members],
                         "types": types, "reasons": reasons})
    return clusters


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    print(f"{'='*60}")
    print(f"Event Deduplication — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"  Date filter: >= {TODAY}")
    print(f"  Title match: fingerprint / exact (normalized) / conservative fuzzy")
    print(f"{'='*60}\n")

    # 1) Load all future events
    print("── Loading future events ──")
    all_events = []
    offset = 0
    while True:
        page = sb_get("events", {
            "select": "id,title,date,time,venue_name,city,state,source,organizer,description,"
                      "long_description,image_url,ticket_url,price_range,street_address,"
                      "venue_images,category,latitude,longitude,content_fingerprint",
            "date": f"gte.{TODAY}",
            "order": "date.asc,venue_name.asc",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        all_events.extend(page)
        if len(page) < 1000:
            break
        offset += 1000

    print(f"  Total future events: {len(all_events)}")
    by_id = {e["id"]: e for e in all_events}

    # 2) Group by (date, normalized venue, city, state)
    print("\n── Grouping by date + venue + city ──")
    groups = defaultdict(list)
    skipped_empty = 0
    skipped_generic = 0
    for e in all_events:
        vn = normalize_venue(e.get("venue_name"))
        if not vn:
            skipped_empty += 1
            continue
        if vn in GENERIC_VENUES:
            skipped_generic += 1
            continue
        city = (e.get("city") or "").strip().lower()
        state = (e.get("state") or "").strip().lower()
        # Group on the venue core so cross-source venue-name variants
        # ("230 Fifth Rooftop" / "230 Fifth Rooftop Bar") meet in one
        # group; display uses the fullest original name in the group.
        key = (e["date"], venue_group_core(vn, city), city, state)
        groups[key].append(e)

    multi_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"  Unique groups: {len(groups)}")
    print(f"  Groups with >1 event: {len(multi_groups)}")
    print(f"  Skipped (empty venue): {skipped_empty}")
    print(f"  Skipped (generic venue): {skipped_generic}")

    # 3) Cluster duplicates (venue groups, then global fingerprints)
    print("\n── Finding duplicates ──")
    clusters = []          # {"events": [...], "types": set, "reasons": [...], "group": str}

    for (date, venue, city, state), events in sorted(multi_groups.items()):
        loc = f" ({city}, {state})" if city else ""
        for cl in cluster_group(events):
            cl["group"] = f"{date} | {venue}{loc}"
            clusters.append(cl)

    # Fingerprint duplicates across ALL events. Overlap with venue-group
    # clusters is resolved in the merge-plan phase (an event already slated
    # for deletion drops out of later clusters; a cluster's keeper can
    # still head a fingerprint cluster, as before).
    fp_groups = defaultdict(list)
    for e in all_events:
        fp = e.get("content_fingerprint")
        if fp:
            fp_groups[fp].append(e)
    fp_cluster_count = 0
    for fp, events in fp_groups.items():
        if len(events) <= 1:
            continue
        clusters.append({"events": events, "types": {"fingerprint"},
                         "reasons": [], "group": f"fingerprint {fp[:16]}"})
        fp_cluster_count += 1

    # Plan merges: pick keepers, mark deletions, dedupe overlapping plans.
    print(f"\n── Merge plan ({len(clusters)} raw clusters) ──")
    plan = []              # {"keeper": e, "dupes": [...], "types": set, "group": str}
    deleted_ids = set()
    for cl in clusters:
        members = [e for e in cl["events"] if e["id"] not in deleted_ids]
        if len(members) < 2:
            continue
        scored = sorted(members, key=lambda e: keeper_score(e, members), reverse=True)
        keeper, dupes = scored[0], scored[1:]
        for d in dupes:
            deleted_ids.add(d["id"])
        plan.append({"keeper": keeper, "dupes": dupes, "types": cl["types"],
                     "reasons": cl.get("reasons", []), "group": cl["group"],
                     "scores": {e["id"]: round(keeper_score(e, members), 2) for e in members}})

    type_counts = defaultdict(int)
    for p in plan:
        for d in p["dupes"]:
            type_counts["+".join(sorted(p["types"]))] += 1
    for p in plan:
        tag = "+".join(sorted(p["types"])).upper()
        print(f"  [{tag}] {p['group']}:")
        print(f"    KEEP: [{p['keeper']['source']}] {p['keeper']['title'][:70]} (score={p['scores'][p['keeper']['id']]})")
        for d in p["dupes"]:
            print(f"    DEL:  [{d['source']}] {d['title'][:70]} (score={p['scores'][d['id']]})")
        for r in p["reasons"]:
            print(f"    fuzzy: shared={r.get('shared')} overlap={r.get('overlap')} "
                  f"jaccard={r.get('jaccard')} time_gap={r.get('time_gap_min')} "
                  f"only1={r.get('only1')} only2={r.get('only2')}")

    # 4) Summary
    total_delete = sum(len(p["dupes"]) for p in plan)
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total events checked: {len(all_events)}")
    print(f"  Duplicate clusters: {len(plan)} (incl. {fp_cluster_count} fingerprint clusters)")
    print(f"  Events to delete: {total_delete}")
    for tag, cnt in sorted(type_counts.items()):
        print(f"    via {tag}: {cnt}")
    print(f"{'='*60}")

    if not plan:
        print("\nNo duplicates found. Done.")
        return

    if DRY_RUN:
        print(f"\n  DRY RUN — would delete {total_delete} events. Rerun without --dry-run to execute.")
        return

    # 5) Apply: fill keepers, log recovery records, delete duplicates
    REPORTS_DIR.mkdir(exist_ok=True)
    log_path = REPORTS_DIR / f"event-dedup-{TODAY}.jsonl"
    deleted = 0
    to_delete = []
    with open(log_path, "a") as log:
        for p in plan:
            keeper, dupes = p["keeper"], p["dupes"]
            patch = build_keeper_patch(keeper, dupes)
            filled = sorted(patch.keys())
            if patch and not sb_patch(keeper["id"], patch):
                print(f"  WARNING: keeper fill failed for {keeper['id']} — deleting dupes anyway")
            ts = datetime.now(timezone.utc).isoformat()
            for d in dupes:
                log.write(json.dumps({
                    "ts": ts, "match": sorted(p["types"]), "group": p["group"],
                    "keeper_id": keeper["id"], "keeper_title": keeper["title"],
                    "removed_id": d["id"], "removed_title": d["title"],
                    "removed_source": d.get("source"), "keeper_filled_fields": filled,
                }) + "\n")
                to_delete.append(d["id"])
    print(f"\n  Recovery log: {log_path} ({len(to_delete)} records)")

    print(f"\n── Deleting {len(to_delete)} duplicates ──")
    BATCH = 50
    for i in range(0, len(to_delete), BATCH):
        batch = to_delete[i:i + BATCH]
        n = sb_delete(batch)
        deleted += n
        print(f"  Batch {i // BATCH + 1}: deleted {n}")

    print(f"\n  Done. Deleted {deleted} duplicate events.")


if __name__ == "__main__":
    main()
