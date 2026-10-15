#!/usr/bin/env python3
"""Trailer watch — poll official YouTube channel RSS feeds for trailer/teaser drops.

- Reads pipeline/trailer-channels.json (42 verified official channels).
- Fetches each channel's videos.xml via curl (no API key needed).
- Keeps uploads whose titles look like official trailers/teasers.
- Dedupes against pipeline/.state/trailer-watch-seen.json.
- Writes new drops to pipeline/.state/trailer-watch-feed.json (merged into
  the trailers rail by prebuild-feeds.py).
- With --write: generates brief "teaser out" articles for tier-1 (major)
  channels and inserts them via v3-batch-insert.process_article.
- Briefs held by the film-card completeness gate are NOT discarded: they
  are queued in pipeline/.state/trailer-watch-held.json and retried on
  every subsequent run (with any newer drops for the same film merged in)
  until they publish or age out after HELD_MAX_DAYS.

First run: videos older than 3 days are marked seen without action, so only
recent drops surface. Subsequent runs: only genuinely new uploads.
"""
import json, os, re, sys, subprocess, html, unicodedata
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote
from xml.etree import ElementTree as ET
try:
    from cast_strip import render_cast_strip_block
except ImportError:  # cast_strip optional; Cast falls back to flat text stat
    render_cast_strip_block = None

PIPE = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
STATE = os.path.join(PIPE, ".state")
SEEN_PATH = os.path.join(STATE, "trailer-watch-seen.json")
FEED_PATH = os.path.join(STATE, "trailer-watch-feed.json")
HELD_PATH = os.path.join(STATE, "trailer-watch-held.json")
# A held brief retries every run; after this many days it is declared
# terminal (loudly, in the run report) instead of being retried forever.
HELD_MAX_DAYS = 14
CHANNELS_PATH = os.path.join(PIPE, "trailer-channels.json")

WRITE = "--write" in sys.argv
LOOKBACK_DAYS_FIRST_RUN = 3
MAX_ARTICLES_PER_RUN = 6

_TITLE_RE = re.compile(r"trailer|teaser", re.IGNORECASE)
# 2026-10-07: added trailer-launch event coverage block. SVF uploaded 9 "Grand
# Trailer Launch" videos (interviews/audience reactions at the launch event, Bengali
# titles like "Launch-এ এসে কী বলল"), which is_trailer() let through because they
# contain "trailer" — producing a bogus "Grand Trailer Out" brief. Block the event
# pattern, not the word.
_BLOCK_RE = re.compile(
    r"#?shorts?\b|box[\s-]?office|collection|\bvs\.?\b|comparison|reaction|"
    r"review|interview|behind the scenes|\bbts\b|first look|mashup|tribute|"
    r"fancast|day\s*\d+|episode\s*\d+|song|audio|lyrical|"
    # 2026-10-14: extended trailer->(trailer|teaser) + launch->(launch|lunch)
    # and added speech block. Lahari Music uploaded 6 "Speech at Haindava
    # Teaser Launch" videos + a "Haindava Teaser Lunch Event Live" — all
    # launch-event coverage, none the teaser itself — which slipped past the
    # Oct-7 pattern (it only blocked "trailer launch") and reached the rail.
    r"(trailer|teaser)\s*(launch|lunch)|launch\s*event|launch\s*coverage|"
    r"\bspeech(es)?\b|"
    r"কেমন\s*লাগল|দর্শকদের|অনুরাগীদের|পৌঁছে|পুরো\s*team|কী\s*বলল|বিশেষ\s*কথা",
    re.IGNORECASE,
)
# Live-event videos (trailer launches, press meets) are rail-eligible but must
# never generate brief articles — their titles mangle film-name extraction
# (e.g. "Ranabaali Trailer launch Event LIVE | Vijay Deverakonda ..." produced
# a 3/10 stub on 2026-10-07).
_LIVE_EVENT_RE = re.compile(
    r"\blive\b|livestream|(launch|lunch)\s*event|press meet|success meet|pre-release event",
    re.IGNORECASE,
)


def curl_get(url, timeout=25):
    r = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout), "-A", "TheVideshi/1.0", url],
        capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout if r.returncode == 0 else ""


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def fetch_channel_videos(channel_id):
    xml = curl_get(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")
    if not xml or "<feed" not in xml:
        return []
    try:
        root = ET.fromstring(xml)
    except Exception:
        return []
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
          "m": "http://search.yahoo.com/mrss/"}
    out = []
    for e in root.findall("a:entry", ns):
        vid = (e.findtext("yt:videoId", default="", namespaces=ns) or "").strip()
        title = html.unescape(e.findtext("a:title", default="", namespaces=ns) or "").strip()
        pub = (e.findtext("a:published", default="", namespaces=ns) or "").strip()
        desc = html.unescape(e.findtext("m:group/m:description", default="", namespaces=ns) or "").strip()
        if vid and title:
            out.append({"video_id": vid, "title": title, "published": pub, "description": desc})
    return out


def is_trailer(title):
    return bool(_TITLE_RE.search(title)) and not bool(_BLOCK_RE.search(title))


def parse_dt(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


_MONTH_NUM = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"])}
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")


def resolve_release(release, ref_dt):
    """Pin a bare 'Mon D' release to a full date: 'Dec 2' -> 'Dec 2, 2026'.

    Uses the next occurrence of that month/day on/after the drop date (7-day
    grace for just-released titles). Strings already carrying a year pass
    through unchanged. The year matters: a card reading 'Jan 15' under an
    October trailer means NEXT January (the River brief shipped 'Jan 15'
    for a Jan 15, 2027 film)."""
    if not release or _YEAR_RE.search(release):
        return release
    m = re.match(r"^([A-Za-z]{3,})\.?\s+(\d{1,2})(?:st|nd|rd|th)?$",
                 release.strip())
    if not m or ref_dt is None:
        return release
    mon = _MONTH_NUM.get(m.group(1)[:3].lower())
    if not mon:
        return release
    day = int(m.group(2))
    year = ref_dt.year
    try:
        cand = datetime(year, mon, day, tzinfo=timezone.utc)
    except ValueError:
        return release
    if cand < ref_dt - timedelta(days=7):
        year += 1
    return f"{m.group(1)[:3].capitalize()} {day}, {year}"


def _film_from_hashtag(segment):
    """'#EbhabeoPhireAshaJaye' -> 'Ebhabeo Phire Asha Jaye'.

    Hoichoi-style titles lead with a tagline phrase and hide the real film
    name in a hashtag: 'বন্ধুরা পাশে থাকলে #EbhabeoPhireAshaJaye'. The
    hashtagged CamelCase word is the film name; the rest is marketing copy.
    """
    m = re.search(r"#([A-Za-z][A-Za-z0-9]*)", segment)
    if not m:
        return None
    word = re.sub(
        r"(?<=[a-z])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])",
        " ", m.group(1))
    return word.strip() or None


def split_film_title(title):
    """'Bhogi - Official Teaser | Sharwanand' -> ('Bhogi', 'Sharwanand').

    Hyphenated film names keep every word up to the teaser/trailer keyword:
    'The Eken: Kerela - e Kurukshetra Official Trailer' -> ('The Eken:
    Kerela - e Kurukshetra', ...), not just ('The Eken', ...).

    Marketing-first titles like 'Our Story. Our History. Our Truth. |
    Ranabaali Trailer on October 8th | ...' put a tagline in parts[0], so
    prefer the part carrying the teaser/trailer keyword: the text before it
    is the film name ('Ranabaali'). Falls back to parts[0].

    Announcement-first titles ('Official Trailer - Birangana 2 | ...') and
    tagline+hashtag titles ('... #EbhabeoPhireAshaJaye | ...') hide the film
    name after the announcement or inside the hashtag; hyphen-joined
    descriptors the subtitle extractor identifies are stripped back out
    ('Hanuman Ansh - A Powerful Divine Story' -> 'Hanuman Ansh')."""
    parts = re.split(r"\s*[|]\s*", title)
    seg0 = parts[0].strip() if parts else ""

    # Announcement-first: 'Official Trailer - Birangana 2 | Sandipta Sen'
    m = re.match(r"(?i)^(?:official\s+)?(?:teaser|trailer)\s*[-\u2013\u2014:]\s*(.+)$", seg0)
    if m:
        seg0 = m.group(1).strip()

    # Tagline + hashtag: the film name is the hashtagged CamelCase word
    ht = _film_from_hashtag(seg0)
    if ht:
        rest_bits = [q for q in parts[1:]
                     if q and not _TITLE_RE.search(q)
                     and not re.search(r"(?i)4k|hd|official", q)]
        return ht, " | ".join(rest_bits[:2]).strip()

    # Tagline-first (sentence punctuation) or empty lead: prefer the part
    # carrying the teaser/trailer keyword.
    if not seg0 or (re.search(r"[.!?]", seg0) and len(seg0) < 200):
        for p in parts:
            m = re.search(r"(?i)^(.+?)\s+(?:official\s+)?(?:teaser|trailer)\b", p)
            if m:
                cand = clean_film_name(m.group(1).strip())
                if cand and cand.lower() not in ("official",):
                    rest_bits = [q for q in parts[1:]
                                 if q and not _TITLE_RE.search(q)
                                 and not re.search(r"(?i)4k|hd|official", q)]
                    return cand, " | ".join(rest_bits[:2]).strip()

    # Normal case: run-up to the teaser/trailer keyword inside the first
    # segment (keeps hyphenated subtitles like 'Kerela - e Kurukshetra').
    m = re.search(r"(?i)^(.+?)\s*(?:official\s+)?(?:teaser|trailer)\b", seg0)
    if m:
        cand = re.sub(r"\s*[-\u2013\u2014:|]\s*$", "", m.group(1)).strip()
    else:
        cand = re.sub(r"\s*[-\u2013\u2014:|]\s*$", "", seg0).strip()
    # '- NEW TRAILER' suffix branding: "RAMAYANA: RISE OF A LEGEND - NEW
    # TRAILER" leaves a dangling "- New" on the film name.
    cand = re.sub(r"(?i)\s*[-\u2013\u2014]\s*new\s*$", "", cand).strip()
    film = clean_film_name(cand) or seg0
    # Strip a hyphen-joined descriptor the subtitle extractor identifies:
    # 'Hanuman Ansh - A Powerful Divine Story' -> 'Hanuman Ansh'.
    sub = extract_subtitle(title)
    if sub and len(film) > len(sub) and film.lower().endswith(sub.lower()):
        film = re.sub(r"\s*[-\u2013\u2014:|]\s*$", "", film[: -len(sub)]).strip()
        film = film or clean_film_name(cand)
    if film.lower() in ("official", "trailer", "teaser",
                        "official trailer", "official teaser"):
        film = ""
    rest_bits = [p for p in parts[1:]
                 if p and not _TITLE_RE.search(p)
                 and not re.search(r"(?i)4k|hd|official", p)]
    rest = " | ".join(rest_bits[:2]).strip()
    return film or title, rest


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:70].strip("-")


_STUDIO_RE = re.compile(
    r"(?i)\b(makers?|films?|studios?|pictures|entertainment|media|music|"
    r"series|originals|video|prime|netflix|hotstar|jio|sony|zee|ott)\b")


def extract_subtitle(title):
    """'Drive - The Pretenders Official Teaser | Prime Video India'
    -> 'The Pretenders' (skips studio/channel fragments)."""
    parts = re.split(r"\s*[|\-–—:]\s*", title)
    for p in parts[1:3]:
        q = re.sub(r"(?i)\s*\(?(official\s+)?(teaser|trailer)(\s+out)?(\s+\d+)?\)?\s*$", "", p).strip()
        q = re.sub(r"(?i)^\s*(official\s+)?(teaser|trailer)(\s+out)?\s*", "", q).strip()
        if re.search(r"(?i)(teaser|trailer)", q):
            continue  # trailer-announcement fragment, not a subtitle
        if q.lower() in ("official",):
            continue  # bare announcement leftover, not a subtitle
        if re.search(r"(?i)\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
                     r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
                     r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}\b|"
                     r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|"
                     r"jul|aug|sep|oct|nov|dec)[a-z]*\b", q):
            continue  # date fragment ("15th October"), not a subtitle
        if q.startswith("@"):
            continue  # channel handle, not a subtitle (e.g. "| @TejaSajjaOffl |")
        if q and len(q) > 2 and not _STUDIO_RE.search(q):
            return q
    return ""


_MONTH_ALT = (r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
              r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
              r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?")
_DATE_MF_RE = re.compile(
    rf"(?i)\b({_MONTH_ALT})\s+(\d{{1,2}})(?:st|nd|rd|th)?\b")
_DATE_DF_RE = re.compile(
    rf"(?i)\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH_ALT})\b")


def _is_teaser_announced_date(text, pos):
    """True when the date at `pos` is announced as the TEASER/TRAILER's own
    date, not the work's release date — e.g. 'Aakasamlo Oka Tara Teaser on
    October 17th' or '#AOTTeaser introduces you to its world on October
    17th'. Such a date must never land on the card as the release date;
    the matcher skips it and keeps looking for a real release date.
    Fail-closed: a false positive costs a hold, never a wrong date."""
    window = text[max(0, pos - 90):pos]
    window = window[window.rfind("\n") + 1:]
    return bool(re.search(r"(?i)(teaser|trailer)[^.\n]{0,70}?\bon\s*$",
                          window))


def _find_release_date(text):
    """First plausible release date in `text`, 'Mon D' form or None.

    Accepts month-first ('November 5') and day-first ('23 October' —
    Netflix India's house style) dates, in text order, skipping any date
    announced as the teaser/trailer's own drop date."""
    cands = []
    for m in _DATE_MF_RE.finditer(text):
        cands.append((m.start(), m.group(1), m.group(2)))
    for m in _DATE_DF_RE.finditer(text):
        cands.append((m.start(), m.group(2), m.group(1)))
    for pos, mon, day in sorted(cands):
        if _is_teaser_announced_date(text, pos):
            continue
        return f"{mon[:3].capitalize()} {day}"
    return None


def parse_description(desc):
    """Extract (clean_line, media_type, release_date) from a video description.

    e.g. '...don't lose control 🏎 #DriveThePretendersOnPrime, New Movie, Oct 28'
    -> ('Go full throttle, ... don't lose control', 'Movie', 'Oct 28')
    """
    text = unicodedata.normalize("NFKD", desc or "")
    first = text.split("\n")[0].strip()
    media_type = None
    m = re.search(r"(?i)\bnew\s+(movie|series)\b", text)
    if m:
        media_type = m.group(1).capitalize()
    elif re.search(r"(?i)\blimited\s+series\b", text):
        media_type = "Series"
    elif re.search(r"(?i)\bseason\s+\d+\b", text):
        media_type = "Series"
    elif re.search(r"(?i)\bmovie\b", "\n".join(text.split("\n")[:3])):
        # e.g. "Here's the Official Kannada Trailer of #418 movie" — the
        # work calls itself a movie in its own opening lines.
        media_type = "Movie"
    elif re.search(r"(?im)^\s*(?:movie|film)\s*:", text):
        # Credit-block label, e.g. Geetha Arts' "Movie: Aakasamlo Oka Tara"
        # sitting below the opening lines — the production's own label.
        media_type = "Movie"
    elif re.search(r"(?i)\bin theatres\b|\bin theaters\b", text):
        # A theatrical release is a film (Sony: "exclusively in theatres").
        media_type = "Movie"
    elif re.search(r"(?i)\b(?:the|this) film (?:is|follows|stars|tells|"
                   r"chronicles|releases|opens|hits|arrives)\b", text):
        # Narrative self-reference: "The film is produced by ..."
        media_type = "Movie"
    release = _find_release_date(text)
    clean = re.sub(r"https?://\S+", "", first)
    clean = re.sub(r"#\w+", "", clean)
    clean = re.sub(r"[^\x00-\x7F\u201c\u201d\u2018\u2019\u2014\u2013\u2026\u20b9]", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip(" -–—|")
    ok = (20 < len(clean) < 220
          and len(re.findall(r"[A-Za-z]", clean)) >= 0.6 * max(len(clean), 1)
          and not re.search(r"(?i)subscribe|follow us|copyright|click here", clean))
    return (clean if ok else ""), media_type, release


_LANG_RE = r"hindi|tamil|telugu|kannada|malayalam|bengali|marathi|punjabi|gujarati|english"


# Labels official channels use for credits in trailer descriptions.
# Order matters: multi-word labels must be tried before their fragments.
_CREDIT_LABELS = [
    ("cast", [r"star\s*cast", r"starring", r"featuring", r"starcast",
              r"\bcast\b", r"actors?"]),
    ("director", [r"directed\s+by", r"direction", r"\bdirector\b"]),
    ("host", [r"hosted\s+by", r"\bhost\b"]),
    ("producer", [r"produced\s+by", r"producers?", r"production"]),
    ("music", [r"music\s+director", r"music\s+by", r"\bmusic\b"]),
]

_CREDIT_JUNK = re.compile(
    r"(?i)subscribe|follow|watch now|click here|copyright|link in|"
    r"https?://|www\.|\.com|@|#")


def _clean_names(value):
    """'X, Y and Z' -> 'X, Y, Z' or '' if it doesn't look like people."""
    value = (value or "").strip().strip(" -–—|:;.,")
    if not value or len(value) > 180:
        return ""
    if _CREDIT_JUNK.search(value):
        return ""
    value = re.sub(r"\s+", " ", value)
    tokens = [t.strip(" .") for t in
              re.split(r"\s*,\s*|\s+&\s+|\s+and\s+|\s+/\s+|\s*\|\s*", value)]
    names = [t for t in tokens if t and len(t) <= 42
             and re.search(r"[A-Z]", t)
             and not re.search(r"\d", t)
             and re.fullmatch(r"[A-Za-z .'\-()&]+", t)
             and not _CREDIT_JUNK.search(t)]
    return ", ".join(names[:6]) if names else ""


# Words that mark a pipe-segment as a studio/label/promo, not a person
_NON_NAME_RE = re.compile(
    r"(?i)\b(trailer|teaser|official|promo|episode|films?|movies?|pictures?|"
    r"studios?|entertainment|productions?|media|music|series|records?|arts|"
    r"originals?|presents?|features?|featuring)\b")


def _looks_like_name(seg):
    """Single pipe-segment that looks like one person's name."""
    seg = (seg or "").strip().strip(" -–—|:;.,")
    if not seg or len(seg) > 42:
        return False
    words = seg.split()
    if not 1 <= len(words) <= 3:
        return False
    if re.search(r"\d", seg):
        return False
    if not re.fullmatch(r"[A-Za-z .'\-()&]+", seg):
        return False
    if not all(w[:1].isupper() for w in words):
        return False
    if _CREDIT_JUNK.search(seg):
        return False
    if _NON_NAME_RE.search(seg):
        return False
    return True


def _cast_from_title(title):
    """Extract cast names from a trailer video title.

    e.g. "Mandaadi | Hindi Trailer | Soori, Suhas, Mahima Nambiar"
      -> "Soori, Suhas, Mahima Nambiar"
    e.g. "বন্ধুরা পাশে থাকলে #... | Rahul Dev Bose | Traya | 10 OCT | hoichoi"
      -> "Rahul Dev Bose, Traya"  (cast spread across pipe segments)

    Scans trailing pipe-segments for one that looks like 2+ person names,
    skipping channel names, dates, and trailer/teaser labels. The cast
    segment is often second-to-last (channel name comes last).
    """
    segs = [s.strip() for s in (title or "").split("|")]
    if len(segs) < 3:
        return ""
    # Format 1: comma-separated names inside one segment
    for tail in reversed(segs[1:]):
        # Skip obvious non-cast segments
        if re.search(r"(?i)trailer|teaser|episode|part\s*\d|official|promo", tail):
            continue
        names = _clean_names(tail)
        # Require at least 2 names to avoid mistaking a single director/
        # producer credit, channel name, or date for cast
        if names and "," in names:
            return names
    # Format 2: cast as consecutive name-like pipe segments
    # ("Film | Actor One | Actor Two | 10 OCT | channel").
    # The run must be followed by a date-like segment — this anchors the
    # "Film | Cast | Date | Channel" pattern and avoids mistaking crew
    # credits (director, music) for cast, e.g. "#418 | Prashanth Neel |
    # Kirtan | Hombale Films" has no date after the names.
    _DATE_RE = re.compile(
        r"(?i)\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b|"
        r"\b(19|20)\d{2}\b")
    segs_tail = segs[1:]
    i = 0
    while i < len(segs_tail):
        if _looks_like_name(segs_tail[i]):
            j = i
            while j < len(segs_tail) and _looks_like_name(segs_tail[j]):
                j += 1
            run = [s.strip() for s in segs_tail[i:j]]
            following = segs_tail[j] if j < len(segs_tail) else ""
            if len(run) >= 2 and _DATE_RE.search(following):
                return ", ".join(run)
            i = j
        else:
            i += 1
    return ""


def _video_is_live(video_id):
    """Check a YouTube video is still playable via oEmbed.

    Returns False for removed/private/deleted videos. Uploaders do pull
    trailers (e.g. T-Series removed the Ranabaali Hindi trailer hours after
    posting) — embedding a dead video shows an ugly "Video unavailable" box.
    """
    import urllib.request
    try:
        req = urllib.request.Request(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def _trim_credit_tail(value):
    """Cut a prose credit capture at its non-name tail: '& Others',
    ', only on Netflix', ', on 23 October' would otherwise validate as
    'names' in _clean_names."""
    value = re.split(
        r"(?i)\s*&\s*others?\b|,\s*only\s+on\b|,\s*on\s+(?=\d)|\s+only\s+on\b",
        value, maxsplit=1)[0]
    return value.strip(" ,;")


# separators that split one line into independent "Label: value" segments
_SEG_SPLIT = re.compile(
    r"\s*[|;]\s*|\.\s+(?=(?:star\s*cast|starcast|starring|featuring|"
    r"\bcast\b|\bactors?\b|directed\s+by|direction|\bdirector\b|"
    r"hosted\s+by|\bhost\b|produced\s+by|producers?|production|"
    r"music\s+director|music\s+by|\bmusic\b))", re.I)

# "X by Name" phrasing without a colon
_BY_PHRASE = re.compile(
    r"(?i)^\s*(directed|hosted|produced)\s+by\s+(.+)$")


def extract_credits(desc):
    """Pull cast/director/host/producer/music from an official description.

    e.g. 'Starring: Ranveer Singh, Deepika Padukone\\nDirected by: Rohit Shetty'
    -> {'cast': 'Ranveer Singh, Deepika Padukone', 'director': 'Rohit Shetty'}
    Only returns values that pass name validation; {} when nothing reliable.
    """
    text = unicodedata.normalize("NFKD", desc or "")
    credits = {}
    pending_cast = False  # a bare "Credits:" line -> the next names-only line is cast
    for raw in text.split("\n"):
        line = raw.strip()
        if not line or len(line) > 220:
            continue
        if pending_cast:
            pending_cast = False
            if "cast" not in credits:
                v = _clean_names(line)
                if v and "," in v:
                    credits["cast"] = v
                    continue
        if re.match(r"(?i)^\s*credits?\s*[:\-–—]?\s*$", line):
            pending_cast = True
            continue
        for seg in _SEG_SPLIT.split(line):
            seg = seg.strip()
            if not seg:
                continue
            for key, labels in _CREDIT_LABELS:
                if key in credits:
                    continue
                lab = "|".join(labels)
                m = re.match(rf"(?i)^\s*(?:{lab})\s*[:\-–—|]\s*(.+)$", seg)
                v = _clean_names(m.group(1)) if m else ""
                if not v and key in ("director", "host", "producer"):
                    m2 = _BY_PHRASE.match(seg)
                    if m2 and m2.group(1).lower() in (
                            "directed" if key == "director" else
                            "hosted" if key == "host" else "produced"):
                        v = _clean_names(m2.group(2))
                if v:
                    credits[key] = v
                    break
            else:
                # mid-line fallback: "... starring Teja Sajja, Manchu Manoj"
                m = re.search(
                    r"(?i)\bstarring\s*[:\-–—]?\s+([A-Z][^.\n|;]{1,150})", seg)
                if m and "cast" not in credits:
                    v = _clean_names(_trim_credit_tail(m.group(1)))
                    if v:
                        credits["cast"] = v
    # Prose-credit fallback (2026-10-15): Netflix India and studio
    # descriptions state credits mid-sentence with no labels or colons —
    # "Watch Gajab Raat, directed by Neeraj Pandey, staring Manoj
    # Bajpayee, Nushrratt Bharuccha & Others, on 23 October, only on
    # Netflix" (note the house typo "staring") and Sony's "It stars
    # Ranbir Kapoor, Yash and Sai Pallavi." Only fills fields the formal
    # parsing above left empty; values still pass _clean_names.
    if "director" not in credits:
        m = re.search(
            r"(?i)\bdirected by\s+([A-Z][A-Za-z .'\-]{1,42}?)"
            r"(?=\s*[,;]|\s+and\s|\s+starring\b|\s+staring\b|\s+stars\b|"
            r"\s+on\s|\s+only\s|\s*$)", text)
        if m:
            v = _clean_names(m.group(1))
            if v and "," not in v:
                credits["director"] = v
    if "cast" not in credits:
        m = re.search(
            r"(?i)\b(?:starring|staring|stars)\s+"
            r"([A-Z][^.\n|;]{1,180})", text)
        if m:
            v = _clean_names(_trim_credit_tail(m.group(1)))
            if v:
                credits["cast"] = v
    return credits


def extract_language(title):
    """'... (Kannada) | Official Trailer' -> 'Kannada'. None if not found."""
    m = re.search(r"\b(" + _LANG_RE + r")\b", title, re.I)
    return m.group(1).capitalize() if m else None


def clean_film_name(film):
    """Strip language tags from a film name: '#418 (Kannada)' -> '#418'."""
    film = re.sub(r"\s*\((?:" + _LANG_RE + r")\)\s*", " ", film, flags=re.I)
    film = re.sub(r"\s*\b(" + _LANG_RE + r")\b\s*$", "", film, flags=re.I)
    return re.sub(r"\s+", " ", film).strip()


def film_key(title):
    """Grouping key: same movie across language versions -> same key."""
    t = unicodedata.normalize("NFKD", title)
    film, _ = split_film_title(t)
    key = re.sub(r"[^a-z0-9]+", "", clean_film_name(film).lower())
    return key or re.sub(r"[^a-z0-9]+", "", t.lower())[:40]


_NETFLIX_TITLE_RE = re.compile(r"netflix\.com/title/(\d+)")


def _curl_browser(url, timeout=30):
    """curl with a browser UA — Netflix serves a login wall to bot UAs."""
    r = subprocess.run(
        ["curl", "-sS", "--max-time", str(timeout),
         "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/126.0 Safari/537.36", url],
        capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout if r.returncode == 0 else ""


def _unescape_js(s):
    def _rep(m):
        try:
            return chr(int(m.group(1), 16))
        except Exception:
            return m.group(0)
    s = re.sub(r"\\x([0-9a-fA-F]{2})", _rep, s)
    return re.sub(r"\\u([0-9a-fA-F]{4})", _rep, s)


def netflix_title_completion(drops):
    """Verified completion from the official Netflix title page.

    Netflix India's trailer descriptions are prose-minimal (STEPS carried
    no type and no credits at all), but they link the title's own page
    (netflix.com/title/<id>), whose embedded model states the title's
    type and cast — the platform is the authoritative source for its own
    catalogue. Extraction is anchored to the block whose topLevelVideoId
    equals the id from the description URL; anything else on the page
    (recommendation rails share the markup) is never read. Fail-closed:
    no anchor, no match, no fetch -> {} and the brief stays held.
    Returns {media_type, cast, director} with only verified fields.
    """
    if os.environ.get("TRAILER_WATCH_NO_NETFLIX_COMPLETION"):
        return {}
    tid = None
    for d in drops:
        m = _NETFLIX_TITLE_RE.search(d.get("description", "") or "")
        if m:
            tid = m.group(1)
            break
    if not tid:
        return {}
    try:
        page = _curl_browser(f"https://www.netflix.com/title/{tid}")
    except Exception:
        return {}
    if not page:
        return {}
    anchor = page.find(f'"topLevelVideoId":{tid}')
    if anchor < 0:
        return {}
    window = page[anchor:anchor + 6000]
    out = {}
    m = re.search(r'"type":"(Movie|TVSeries)"', window)
    if m:
        out["media_type"] = "Movie" if m.group(1) == "Movie" else "Series"
    for role, key in (("actors", "cast"), ("directors", "director")):
        m = re.search(rf'"{role}":\[(.*?)\]', window, re.S)
        if not m:
            continue
        names = [_unescape_js(n).strip()
                 for n in re.findall(r'"name":"([^"]+)"', m.group(1))]
        names = [n for n in names if n]
        if names:
            v = _clean_names(", ".join(names[:6]))
            if v:
                out[key] = v
    return out


def build_brief_article(drops, channels_by_name):
    """One article per film; every language version listed with its own embed."""
    # Primary = most descriptive title (some channels post stub titles like
    # "#418 - Official Trailer (Hindi)" while others include the subtitle)
    first = max(drops, key=lambda d: len(d.get("title", "")))
    title = unicodedata.normalize("NFKD", first["title"])
    kind = "Teaser" if re.search(r"teas", title, re.I) else "Trailer"
    film, rest = split_film_title(title)
    film = clean_film_name(film) or "New release"
    subtitle = extract_subtitle(title)
    subtitle = clean_film_name(subtitle)
    if subtitle and subtitle.lower() not in film.lower():
        film = f"{film} \u2013 {subtitle}"
    hook = clean_film_name(rest.split("|")[0].strip()) if rest else ""
    # Don't let a studio/channel name or @handle become the headline hook,
    # and don't repeat a word that's already in the film name.
    if hook.startswith("@") or _STUDIO_RE.search(hook) or \
            (hook and hook.lower() in film.lower()):
        hook = ""
    headline = f"{film} {kind} Out" + (f": {hook[:60]}" if hook else "")
    pub = parse_dt(first["published"])
    pub_str = pub.strftime("%B %d, %Y") if pub else "today"

    versions = []
    for d in drops:
        lang = extract_language(unicodedata.normalize("NFKD", d["title"]))
        ch = channels_by_name.get(d["channel"], {})
        lang = lang or ch.get("language")  # None if unknown — no fake label
        watch_url = f"https://www.youtube.com/watch?v={d['video_id']}"
        versions.append({"lang": lang, "channel": d["channel"], "url": watch_url,
                         "video_id": d["video_id"]})
    # de-dupe identical uploads, keep language order stable
    uniq, seen_urls = [], set()
    for v in versions:
        if v["url"] not in seen_urls:
            uniq.append(v); seen_urls.add(v["url"])
    versions = uniq
    langs = sorted({v["lang"] for v in versions if v["lang"]})

    desc_line, media_type, release = parse_description(first.get("description", ""))
    if not release:
        # Release dates often live only in the video title ("Oct 23rd Rel",
        # "| 15th October"). Description still wins when both have one.
        # Same matcher: day-first allowed, teaser-announced dates skipped.
        release = _find_release_date(title)
    # Pin the year at build time so the card, takeaways and subheadline all
    # carry the full date (see resolve_release).
    release = resolve_release(release, pub)
    # Game trailers (e.g. a channel posting a gameplay trailer) are not films —
    # use game-appropriate language instead of "film's US release / theaters".
    is_game = bool(re.search(r"\bgameplay\b|\bgame\b", title, re.I))
    work = "game" if is_game else ("series" if media_type == "Series" else "film")

    # Credits may live in any language version's description; merge, preferring
    # the primary drop's values. (first is the longest-titled drop, not drops[0])
    credits = extract_credits(first.get("description", ""))
    # Fallback: cast names often live in the video title itself, e.g.
    # "Mandaadi | Hindi Trailer | Soori, Suhas, Mahima Nambiar" — the
    # description may have no parseable credits at all.
    if "cast" not in credits:
        title_cast = _cast_from_title(first.get("title", ""))
        if title_cast:
            credits["cast"] = title_cast
    for d in drops:
        if d is first:
            continue
        more = extract_credits(d.get("description", ""))
        for k, v in more.items():
            credits.setdefault(k, v)

    # Type/release may live only in another language version's
    # description (the primary drop is picked by title length, not by
    # description richness) — fill still-missing fields from the other
    # drops, same official sources, before consulting anything external.
    if not media_type or not release:
        for d in drops:
            if d is first:
                continue
            _, mt2, rel2 = parse_description(d.get("description", ""))
            if not media_type and mt2:
                media_type = mt2
            if not release and rel2:
                release = resolve_release(rel2, pub)
            if media_type and release:
                break

    # Verified completion (2026-10-15): when the gate would still fail on
    # type or credits, consult the platform's own title page — currently
    # Netflix, whose title URL is printed in the drop's own description.
    if not media_type or not any(credits.get(k) for k in
                                 ("cast", "director", "host",
                                  "producer", "music")):
        completion = netflix_title_completion(drops)
        if not media_type and completion.get("media_type"):
            media_type = completion["media_type"]
        for k in ("cast", "director"):
            if k not in credits and completion.get(k):
                credits[k] = completion[k]

    main_ch = channels_by_name.get(first["channel"], {})
    takeaways = [
        f"The {kind.lower()} for <b>{html.escape(film)}</b> dropped {pub_str}.",
    ]
    if media_type and release:
        takeaways.append(
            f"New {media_type.lower()} premiering {release} on {html.escape(first['channel'])}.")
    elif media_type:
        takeaways.append(f"New {media_type.lower()} on {html.escape(first['channel'])}.")
    elif release:
        takeaways.append(f"Releasing {release}.")
    if desc_line:
        takeaways.append(html.escape(desc_line))
    if langs:
        takeaways.append(f"Out in {', '.join(langs)} \u2014 pick your language below.")

    body = (
        '<div class="key-takeaways"><ul>'
        + "".join(f"<li>{t}</li>" for t in takeaways)
        + "</ul></div>"
        + f"<p>The makers of <b>{html.escape(film)}</b> have released the official {kind.lower()}, "
        + f"unveiled {pub_str}.</p>"
    )
    if desc_line and len(takeaways) < 3:
        body += f"<p>{html.escape(desc_line)}</p>"
    dest = "streaming" if main_ch.get("industry") == "streamer" else "theaters"
    if is_game:
        body += (f"<p>For diaspora gamers, the {kind.lower()} is the first "
                 f"real look at what's ahead"
                 + (f", with the game releasing {html.escape(release)}." if release else ".")
                 + "</p>")
    else:
        body += (f"<p>For diaspora audiences tracking the {work}'s US release, the {kind.lower()} is the first "
                 f"real look at what's headed to {dest}.</p>")
    info_rows = []
    # Cast renders as a headshot strip below the stat grid, not a flat text
    # stat — comma-joined name lists are unreadable on mobile.
    cast_strip_html = ""
    if credits.get("cast") and render_cast_strip_block:
        try:
            cast_strip_html = render_cast_strip_block(credits["cast"])
        except Exception:
            cast_strip_html = ""
    if credits.get("director"):
        info_rows.append(("Director", credits["director"]))
    if credits.get("host"):
        info_rows.append(("Host", credits["host"]))
    if credits.get("producer"):
        info_rows.append(("Producer", credits["producer"]))
    if credits.get("music"):
        info_rows.append(("Music", credits["music"]))
    if media_type:
        info_rows.append(("Type", media_type))
    if release:
        info_rows.append(("Release", release))
    if langs:
        info_rows.append(("Languages", ", ".join(langs)))
    # A lone "Languages" row isn't worth a navy card — require at least one
    # real credit, type, or release date. The cast strip counts as content too.
    if (info_rows or cast_strip_html) and (any(credits.get(k) for k in
                          ("cast", "director", "host", "producer", "music"))
                      or media_type or release):
        body += ('<div class="vdc"><div class="vdc-glow"></div>'
                 f'<div class="vdc-title">{"Game info" if is_game else "Film information"}</div>'
                 '<div class="vdc-grid">'
                 + "".join(
                     f'<div class="vdc-stat"><div class="vdc-stat-val">{html.escape(v)}</div>'
                     f'<div class="vdc-stat-lbl">{k}</div></div>'
                     for k, v in info_rows)
                 + "</div>"
                 + cast_strip_html
                 + "</div>")
    # Filter out dead videos first — uploaders do remove trailers after posting
    live_versions = [v for v in versions if _video_is_live(v["video_id"])]
    for v in live_versions:
        label = (f"<b>{html.escape(v['lang'])}</b> \u2014 {html.escape(v['channel'])}"
                 if v["lang"] else f"<b>{html.escape(v['channel'])}</b>")
        body += f"<p>{label}</p><youtube>{v['url']}</youtube>"

    # Film-card completeness gate (2026-10-13): a brief whose card lacks a
    # type, a full release date WITH year, or any director/cast credit is a
    # thin stub — main() holds it instead of publishing. Games are exempt
    # from the credit/type bar (they are not films) but still need a date.
    has_credit = any(credits.get(k) for k in
                     ("cast", "director", "host", "producer", "music"))
    card_missing = []
    if is_game:
        if not release:
            card_missing.append("release date")
    else:
        if not media_type:
            card_missing.append("type")
        if not release:
            card_missing.append("release date")
        elif not _YEAR_RE.search(release):
            card_missing.append("release year")
        if not has_credit:
            card_missing.append("director/cast credit")

    thumb_vid = live_versions[0]["video_id"] if live_versions else versions[0]["video_id"]

    # ≥2-source gate compliance (Kiran, 2026-10-14): one source per video
    # version means a single-version drop would carry only ONE source and
    # the insert gate would hold the brief. The legitimate second source
    # is the official channel page of the uploading channel — its
    # canonical URL is built from the channel_id already held in
    # trailer-channels.json (never invented). Add channel pages, in drop
    # order, until the brief has 2 distinct sources.
    brief_sources = [{"name": v["channel"], "url": v["url"]} for v in versions]
    _src_urls = {s["url"] for s in brief_sources}
    for d in drops:
        if len(_src_urls) >= 2:
            break
        _cid = channels_by_name.get(d["channel"], {}).get("channel_id")
        if not _cid:
            continue
        _chan_url = f"https://www.youtube.com/channel/{_cid}"
        if _chan_url not in _src_urls:
            brief_sources.append({
                "name": f"{d['channel']} — Official YouTube Channel",
                "url": _chan_url})
            _src_urls.add(_chan_url)

    sub = f"Official {kind.lower()} for {film}"
    if release:
        sub += f" \u2014 premieres {release}"
    elif langs:
        sub += f" \u2014 out in {', '.join(langs)}"
    sub += "."
    return {
        "headline": headline,
        "subheadline": sub,
        "slug": slugify(headline) or f"trailer-{thumb_vid}",
        "body": body,
        "category": "entertainment",
        "tags": ["trailers", main_ch.get("industry", ""), film] + [l.lower() for l in langs],
        "sources": brief_sources,
        "image_url": f"https://i.ytimg.com/vi/{thumb_vid}/hqdefault.jpg",
        "image_caption": f"Still from the official {kind.lower()} of {film}.",
        "image_attribution": f"{html.escape(versions[0]['channel'])} / YouTube",
        "diaspora_angle": "US theatrical release tracking for diaspora audiences.",
        # Gate metadata for main(); process_article builds an explicit row
        # dict, so these extra keys never reach the insert payload.
        "card_complete": not card_missing,
        "card_missing": card_missing,
    }


def sb_check_slug(slug):
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return False
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "15",
         f"{sb_url}/rest/v1/p2_articles?select=id&slug=eq.{slug}&limit=1",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=20)
    try:
        return bool(json.loads(r.stdout))
    except Exception:
        return False


def _published_briefs_query(since_iso, limit):
    """Query string for sb_fetch_published_briefs, fully URL-encoded.

    2026-10-14: the old hand-built query embedded the ISO timestamp raw,
    and its '+00:00' suffix decoded as a SPACE in the query string —
    PostgREST rejected the timestamp (Postgres 22007, HTTP 400) and
    returned an error OBJECT, which the caller silently treated as "no
    briefs", leaving the cross-run duplicate guard inert in production.
    Every value is now urlencode()d so no character can break it again."""
    return urlencode([
        ("select", "id,slug,headline,body,sources"),
        ("status", "eq.published"),
        ("category", "eq.entertainment"),
        ("published_at", f"gte.{since_iso}"),
        ("or", "(headline.like.*Trailer Out*,headline.like.*Teaser Out*)"),
        ("order", "published_at.desc"),
        ("limit", str(limit)),
    ], quote_via=quote)


def _guard_inert(reason):
    """Loud warning when the cross-run duplicate guard cannot run.

    A silently-empty guard looks exactly like "no duplicates exist" —
    that failure mode shipped the duplicate #418 brief on 2026-10-13's
    class of bug. Print to stdout AND stderr so no run report can miss
    that this run had NO cross-run duplicate protection."""
    msg = (f"  ⚠️⚠️ CROSS-RUN DUPLICATE GUARD INERT: {reason} — "
           "proceeding WITHOUT protection against duplicate briefs")
    print(msg)
    print(msg, file=sys.stderr)


def sb_fetch_published_briefs(limit=400):
    """Recent published trailer/teaser briefs, for cross-run film matching.

    The within-run grouping in main() cannot see last week's article, and
    the exact-slug check cannot see that '#418 – The Last Warning Trailer
    Out: Prashanth Neel Presents' is the same film as '#418 Trailer Out:
    The Last Warning' — that gap published a duplicate #418 article on
    2026-10-13. Matching is by film_key, computed from headlines here and
    from video titles in main()."""
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        _guard_inert("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set")
        return []
    since = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
    q = _published_briefs_query(since, limit)
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "20",
         f"{sb_url}/rest/v1/p2_articles?{q}",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}"],
        capture_output=True, text=True, timeout=25)
    if r.returncode != 0:
        _guard_inert(f"curl failed (exit {r.returncode}): "
                     f"{r.stderr.strip()[:200]}")
        return []
    try:
        rows = json.loads(r.stdout)
    except Exception as e:
        _guard_inert(f"unparseable Supabase response: {e}")
        return []
    if not isinstance(rows, list):
        detail = rows.get("message") if isinstance(rows, dict) else str(rows)[:200]
        _guard_inert(f"Supabase returned a non-list response: {detail}")
        return []
    return rows


def find_cross_run_match(key, briefs):
    """The published brief for this film, or None.

    Exact key match always counts. Prefix match (the within-run grouping
    rule, for subtitle-extended keys) requires >=5 chars on the shorter
    side, so a short numeric key like '418' can only match itself."""
    if not key:
        return None
    for b in briefs:
        bk = film_key(b.get("headline", ""))
        if not bk:
            continue
        if bk == key:
            return b
        if min(len(bk), len(key)) >= 5 and \
                (bk.startswith(key) or key.startswith(bk)):
            return b
    return None


def sb_patch_article(article_id, payload):
    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        return False
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "25", "-X", "PATCH",
         f"{sb_url}/rest/v1/p2_articles?id=eq.{article_id}",
         "-H", f"apikey: {sb_key}", "-H", f"Authorization: Bearer {sb_key}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=30)
    return r.returncode == 0


def sb_merge_embeds(existing, drops, channels_by_name):
    """Append embeds for drops not already in the published article's body.

    New language versions land just before the related-coverage block when
    one exists. Returns how many embeds were added (0 = nothing new, all
    dead, or the PATCH failed)."""
    body = existing.get("body") or ""
    additions, new_sources = [], []
    for d in drops:
        vid = d["video_id"]
        if vid in body or not _video_is_live(vid):
            continue
        t = unicodedata.normalize("NFKD", d["title"])
        lang = extract_language(t)
        ch = channels_by_name.get(d["channel"], {})
        lang = lang or ch.get("language")
        label = (f"<b>{html.escape(lang)}</b> \u2014 {html.escape(d['channel'])}"
                 if lang else f"<b>{html.escape(d['channel'])}</b>")
        url = f"https://www.youtube.com/watch?v={vid}"
        additions.append(f"<p>{label}</p><youtube>{url}</youtube>")
        new_sources.append({"name": d["channel"], "url": url})
    if not additions:
        return 0
    marker = '<div class="related-coverage">'
    if marker in body:
        body = body.replace(marker, "".join(additions) + marker, 1)
    else:
        body = body + "".join(additions)
    payload = {"body": body}
    sources = existing.get("sources") or []
    have = {s.get("url") for s in sources if isinstance(s, dict)}
    merged = sources + [s for s in new_sources if s["url"] not in have]
    if len(merged) != len(sources):
        payload["sources"] = merged
    return len(additions) if sb_patch_article(existing["id"], payload) else 0


# ------------------------------------------------------------- held queue
# A brief held by the film-card gate used to be DISCARDED: the drops were
# already marked seen, so no later run ever reconsidered the film — four
# tier-1 drops in a row vanished this way on 2026-10-15 (Aakasamlo Oka
# Tara, Gajab Raat, STEPS, Ramayana). Held briefs now persist in
# trailer-watch-held.json (full drop records, incl. descriptions) and are
# retried every run: parser/completion improvements apply retroactively,
# channels edit descriptions, and a later drop for the same film unions
# into the queued entry. Entries expire loudly after HELD_MAX_DAYS.

def load_held():
    h = load_json(HELD_PATH, {})
    return h if isinstance(h, dict) else {}


def save_held(held):
    with open(HELD_PATH, "w") as f:
        json.dump(held, f, ensure_ascii=False, indent=1)


def _same_film_key(a, b):
    """Within-run grouping rule: prefix match in either direction."""
    return bool(a) and bool(b) and (a.startswith(b) or b.startswith(a))


def _held_entry_for(held, key):
    for qk, entry in held.items():
        if _same_film_key(qk, key):
            return qk, entry
    return None, None


def queue_hold(held, key, drops, missing, now_iso,
               first_held_at=None, attempts=0):
    held[key] = {
        "drops": drops,
        "first_held_at": first_held_at or now_iso,
        "last_attempt_at": now_iso,
        "attempts": attempts,
        "last_missing": missing,
    }


def dequeue_film(held, key):
    for qk in [k for k in held if _same_film_key(k, key)]:
        held.pop(qk, None)


def merge_held_into_groups(groups, held):
    """Combine fresh groups with the held queue into one work list.

    Queued drops union into a matching fresh group (more descriptions =
    more completion chances); queue-only films become retry groups and
    go FIRST (oldest stories first). `held` is not mutated — the caller
    applies outcomes."""
    work = [[k, list(drops)] for k, drops in groups]
    retries = []
    for qk, entry in held.items():
        qdrops = entry.get("drops") or []
        if not qdrops:
            continue
        for w in work:
            if _same_film_key(w[0], qk):
                have = {d["video_id"] for d in w[1]}
                w[1].extend(d for d in qdrops if d["video_id"] not in have)
                if len(qk) > len(w[0]):
                    w[0] = qk
                break
        else:
            retries.append([qk, list(qdrops)])
    return retries + work


def attempt_brief(key, drops, channels_by_name, published_briefs, insert_fn):
    """One brief attempt for a film group.

    Returns (outcome, art): 'published' | 'merged' | 'skip' | 'held' |
    'failed'. The film-card gate itself is unchanged (2026-10-13): a
    brief whose card lacks a type, a full release date with year, or any
    director/cast credit is held, never published as a thin stub."""
    art = build_brief_article(drops, channels_by_name)
    existing = find_cross_run_match(key, published_briefs)
    if existing:
        added = sb_merge_embeds(existing, drops, channels_by_name)
        print(f"  merged into published article ({existing['slug']}): "
              f"+{added} embed(s) — no new article")
        return "merged", art
    if sb_check_slug(art["slug"]):
        print(f"  skip (slug exists): {art['slug']}")
        return "skip", art
    if not art.get("card_complete"):
        print(f"  HOLD brief (incomplete film card — missing: "
              f"{', '.join(art.get('card_missing') or [])}): "
              f"{art['slug']}")
        return "held", art
    if insert_fn(art):
        return "published", art
    print(f"  insert failed (will retry from queue): {art['slug']}")
    return "failed", art


def main():
    os.makedirs(STATE, exist_ok=True)
    cfg = load_json(CHANNELS_PATH, {})
    channels = cfg.get("channels", [])
    if not channels:
        print("No channels configured"); return 1
    seen = load_json(SEEN_PATH, {})
    first_run = not seen
    cutoff = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS_FIRST_RUN)

    new_drops = []
    for ch in channels:
        videos = fetch_channel_videos(ch["channel_id"])
        for v in videos:
            vid = v["video_id"]
            if vid in seen:
                continue
            pub = parse_dt(v["published"])
            if first_run and pub and pub < cutoff:
                seen[vid] = {"title": v["title"], "seen_at": datetime.now(timezone.utc).isoformat(),
                             "seeded": True}
                continue
            if not is_trailer(v["title"]):
                seen[vid] = {"title": v["title"], "seen_at": datetime.now(timezone.utc).isoformat(),
                             "not_trailer": True}
                continue
            seen[vid] = {"title": v["title"], "channel": ch["name"],
                         "seen_at": datetime.now(timezone.utc).isoformat()}
            new_drops.append({"video_id": vid, "title": v["title"], "published": v["published"],
                              "description": v.get("description", ""),
                              "channel": ch["name"], "industry": ch["industry"], "tier": ch["tier"],
                              "thumbnail": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"})

    # Merge into persistent watch feed (prebuild merges this into trailers.json)
    feed = load_json(FEED_PATH, [])
    have = {d["video_id"] for d in feed}
    for d in new_drops:
        if d["video_id"] not in have:
            feed.append(d)
    # keep feed fresh: last 30 days only
    fresh_cut = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    feed = [d for d in feed if d.get("published", "") >= fresh_cut]
    feed.sort(key=lambda d: d.get("published", ""), reverse=True)

    with open(SEEN_PATH, "w") as f:
        json.dump(seen, f, ensure_ascii=False)
    with open(FEED_PATH, "w") as f:
        json.dump(feed, f, ensure_ascii=False, indent=1)

    print(f"Channels polled: {len(channels)} | new trailer/teaser drops: {len(new_drops)}")
    majors = [d for d in new_drops if d["tier"] == 1 and not _LIVE_EVENT_RE.search(d["title"])]
    for d in new_drops:
        print(f"  [{'MAJOR' if d['tier']==1 else 'rail '} ] {d['channel']}: {d['title'][:80]}")

    articles_written = 0
    held_queue = load_held() if WRITE else {}
    if WRITE and (majors or held_queue):
        # Import the batch inserter's per-article processor
        sys.path.insert(0, PIPE)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "v3_batch_insert", os.path.join(PIPE, "v3-batch-insert.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        channels_by_name = {c["name"]: c for c in channels}
        # Group by film: one article per movie, all language versions inside.
        # Prefix-merge handles channels that post stub titles ("#418 - Official
        # Trailer") alongside full ones ("#418 The Last Warning (Hindi) | ...").
        groups = []  # [key, drops]
        for d in majors:
            k = film_key(d["title"])
            placed = False
            for g in groups:
                if k and g[0] and (g[0].startswith(k) or k.startswith(g[0])):
                    if len(k) > len(g[0]):
                        g[0] = k
                    g[1].append(d)
                    placed = True
                    break
            if not placed:
                groups.append([k, [d]])
        # Held briefs from earlier runs join the work list (pure retries
        # first; queued drops union into matching fresh groups) — a run
        # with zero new drops still works the queue.
        work = merge_held_into_groups(groups, held_queue)
        # Cross-run guard: a film whose brief already published (an earlier
        # run, possibly days ago) gets the new version MERGED into that
        # article — never a second article for the same film.
        published_briefs = sb_fetch_published_briefs()
        merged_groups = 0
        held_count = 0
        expired = 0
        retried = 0
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        for idx, (key, drops) in enumerate(work):
            old_qk, old_entry = _held_entry_for(held_queue, key)
            if old_qk and old_qk != key:
                held_queue.pop(old_qk, None)
            if idx >= MAX_ARTICLES_PER_RUN:
                # Beyond this run's cap: stay queued for the next run
                # instead of being discarded (drops are already 'seen').
                queue_hold(held_queue, key, drops,
                           (old_entry or {}).get("last_missing")
                           or ["deferred: run article cap"],
                           now_iso,
                           first_held_at=(old_entry or {}).get(
                               "first_held_at"),
                           attempts=(old_entry or {}).get("attempts", 0))
                continue
            if old_entry is not None:
                retried += 1
            outcome, art = attempt_brief(key, drops, channels_by_name,
                                         published_briefs,
                                         mod.process_article)
            if outcome == "published":
                articles_written += 1
                dequeue_film(held_queue, key)
            elif outcome == "merged":
                merged_groups += 1
                dequeue_film(held_queue, key)
            elif outcome == "skip":
                dequeue_film(held_queue, key)
            else:  # held / failed -> (re)queue, or expire loudly
                first_held = (old_entry or {}).get("first_held_at") or now_iso
                attempts = (old_entry or {}).get("attempts", 0) + 1
                held_since = parse_dt(first_held)
                age_days = (now - held_since).days if held_since else 0
                missing = art.get("card_missing") or ["insert failed"]
                if age_days >= HELD_MAX_DAYS:
                    dequeue_film(held_queue, key)
                    expired += 1
                    print(f"  ⚠️ HELD-EXPIRED (held {age_days}d, still "
                          f"missing: {', '.join(missing)}): {art['slug']} "
                          f"— brief will not be published")
                else:
                    queue_hold(held_queue, key, drops, missing, now_iso,
                               first_held_at=first_held, attempts=attempts)
                    held_count += 1
        save_held(held_queue)
        print(f"Brief articles inserted: {articles_written}/{min(len(work), MAX_ARTICLES_PER_RUN)}"
              f" | merged into existing: {merged_groups} | held (thin card): {held_count}"
              f" | retried from queue: {retried} | held expired: {expired}"
              f" | queue size: {len(held_queue)}")
    elif majors:
        print(f"(dry run — {len(majors)} major drops would get brief articles with --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
