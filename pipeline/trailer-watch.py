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

First run: videos older than 3 days are marked seen without action, so only
recent drops surface. Subsequent runs: only genuinely new uploads.
"""
import json, os, re, sys, subprocess, html, unicodedata
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET
try:
    from cast_strip import render_cast_strip_block
except ImportError:  # cast_strip optional; Cast falls back to flat text stat
    render_cast_strip_block = None

PIPE = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
STATE = os.path.join(PIPE, ".state")
SEEN_PATH = os.path.join(STATE, "trailer-watch-seen.json")
FEED_PATH = os.path.join(STATE, "trailer-watch-feed.json")
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
    r"trailer\s*launch|launch\s*event|launch\s*coverage|"
    r"কেমন\s*লাগল|দর্শকদের|অনুরাগীদের|পৌঁছে|পুরো\s*team|কী\s*বলল|বিশেষ\s*কথা",
    re.IGNORECASE,
)
# Live-event videos (trailer launches, press meets) are rail-eligible but must
# never generate brief articles — their titles mangle film-name extraction
# (e.g. "Ranabaali Trailer launch Event LIVE | Vijay Deverakonda ..." produced
# a 3/10 stub on 2026-10-07).
_LIVE_EVENT_RE = re.compile(
    r"\blive\b|livestream|launch event|press meet|success meet|pre-release event",
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


def split_film_title(title):
    """'Bhogi - Official Teaser | Sharwanand' -> ('Bhogi', 'Sharwanand').

    Hyphenated film names keep every word up to the teaser/trailer keyword:
    'The Eken: Kerela - e Kurukshetra Official Trailer' -> ('The Eken:
    Kerela - e Kurukshetra', ...), not just ('The Eken', ...).

    Marketing-first titles like 'Our Story. Our History. Our Truth. |
    Ranabaali Trailer on October 8th | ...' put a tagline in parts[0], so
    prefer the part carrying the teaser/trailer keyword: the text before it
    is the film name ('Ranabaali'). Falls back to parts[0]."""
    parts = re.split(r"\s*[|\-–—:]\s*", title)
    first = parts[0].strip() if parts else ""
    # parts[0] is the film unless it looks like a marketing tagline
    # (sentence punctuation = tagline, e.g. "Our Story. Our History. Our Truth.")
    film_like = first and not re.search(r"[.!?]", first) and len(first) < 60
    if film_like:
        # Keep hyphenated subtitles: cut the title at the teaser/trailer
        # keyword instead of using the first hyphen-separated fragment.
        m = re.search(r"(?i)^(.+?)\s*(?:official\s+)?(?:teaser|trailer)\b", title)
        if m:
            cand = clean_film_name(re.sub(r"\s*[-–—:|]\s*$", "", m.group(1)).strip())
            if cand:
                film = cand
            else:
                film = first
        else:
            film = first
    elif not film_like:
        for p in parts:
            m = re.search(r"(?i)^(.+?)\s+(?:official\s+)?(?:teaser|trailer)\b", p)
            if m:
                cand = clean_film_name(m.group(1).strip())
                if cand and cand.lower() not in ("official",):
                    rest_bits = [q for q in parts[1:]
                                 if q and not _TITLE_RE.search(q) and not re.search(r"(?i)4k|hd|official", q)]
                    return cand, " | ".join(rest_bits[:2]).strip()
    if not film_like:
        film = first or title
        film = re.sub(r"(?i)\s*\(?(official\s+)?(teaser|trailer)(\s+\d+)?\)?\s*$", "", film).strip()
        film = re.sub(r"(?i)^(official\s+)?(teaser|trailer)\s*(of|for)?\s*", "", film).strip()
    rest_bits = [p for p in parts[1:]
                 if p and not _TITLE_RE.search(p) and not re.search(r"(?i)4k|hd|official", p)]
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
        q = re.sub(r"(?i)\s*\(?(official\s+)?(teaser|trailer)(\s+\d+)?\)?\s*$", "", p).strip()
        q = re.sub(r"(?i)^\s*(official\s+)?(teaser|trailer)\s*", "", q).strip()
        if re.search(r"(?i)(teaser|trailer)", q):
            continue  # trailer-announcement fragment, not a subtitle
        if q.startswith("@"):
            continue  # channel handle, not a subtitle (e.g. "| @TejaSajjaOffl |")
        if q and len(q) > 2 and not _STUDIO_RE.search(q):
            return q
    return ""


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
    elif re.search(r"(?i)\bseason\s+\d+\b", text):
        media_type = "Series"
    release = None
    m = re.search(
        r"(?i)\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
        r"dec(?:ember)?)\s+(\d{1,2})\b", text)
    if m:
        release = f"{m.group(1)[:3].capitalize()} {m.group(2)}"
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


def _cast_from_title(title):
    """Extract cast names from a trailer video title.

    e.g. "Mandaadi | Hindi Trailer | Soori, Suhas, Mahima Nambiar"
      -> "Soori, Suhas, Mahima Nambiar"
    Only the trailing pipe-segment is considered, and only when it looks
    like 2+ person names (not a date, episode tag, or channel name).
    """
    segs = [s.strip() for s in (title or "").split("|")]
    if len(segs) < 3:
        return ""
    tail = segs[-1]
    # Skip obvious non-cast tails
    if re.search(r"(?i)trailer|teaser|episode|part\s*\d|official|promo", tail):
        return ""
    names = _clean_names(tail)
    # Require at least 2 names to avoid mistaking a single director/producer
    # credit or show title for cast
    return names if names and "," in names else ""


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
                    v = _clean_names(m.group(1))
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

    thumb_vid = live_versions[0]["video_id"] if live_versions else versions[0]["video_id"]
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
        "sources": [{"name": v["channel"], "url": v["url"]} for v in versions],
        "image_url": f"https://i.ytimg.com/vi/{thumb_vid}/hqdefault.jpg",
        "image_caption": f"Still from the official {kind.lower()} of {film}.",
        "image_attribution": f"{html.escape(versions[0]['channel'])} / YouTube",
        "diaspora_angle": "US theatrical release tracking for diaspora audiences.",
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
    if WRITE and majors:
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
        for key, drops in groups[:MAX_ARTICLES_PER_RUN]:
            art = build_brief_article(drops, channels_by_name)
            if sb_check_slug(art["slug"]):
                print(f"  skip (slug exists): {art['slug']}")
                continue
            ok = mod.process_article(art)
            articles_written += 1 if ok else 0
        print(f"Brief articles inserted: {articles_written}/{min(len(groups), MAX_ARTICLES_PER_RUN)}")
    elif majors:
        print(f"(dry run — {len(majors)} major drops would get brief articles with --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
