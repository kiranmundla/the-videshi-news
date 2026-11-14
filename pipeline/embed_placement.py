"""Shared embed placement logic — place embeds high but never cluster media."""

import json
import os
import re
import unicodedata
from datetime import datetime, timezone

# Media patterns to detect existing embeds/images in a section
_MEDIA_PATTERNS = [
    r'<youtube>',
    r'<twitter>',
    r'<instagram>',
    r'instagram\.com/p/',
    r'x\.com/\w+/status/',
    r'twitter\.com/\w+/status/',
    r'<figure[\s>]',
    r'<img[\s>]',
    r'youtube\.com/watch',
]
_MEDIA_RE = re.compile('|'.join(_MEDIA_PATTERNS), re.IGNORECASE)


def _count_media(text):
    return len(_MEDIA_RE.findall(text))


def insert_embed_high(body, embed_line):
    """Insert an embed as high as possible without clustering with existing media.
    
    Walks sections top-down. Picks the first section with zero media.
    If all sections have media, picks the first section anyway (engagement > aesthetics).
    Within the chosen section, inserts after the first </p>.
    """
    h2_splits = list(re.finditer(r'<h2[^>]*>', body, re.IGNORECASE))

    if not h2_splits:
        # No sections — insert after 1st </p>
        p_ends = [m.end() for m in re.finditer(r'</p>', body, re.IGNORECASE)]
        if p_ends:
            return body[:p_ends[0]] + embed_line + body[p_ends[0]:]
        return body + embed_line

    # Build section boundaries
    sections = []
    intro_text = body[:h2_splits[0].start()]
    if intro_text.strip() and not intro_text.strip().startswith('<div class="key-takeaways'):
        sections.append((0, h2_splits[0].start()))

    for i, m in enumerate(h2_splits):
        s = m.start()
        e = h2_splits[i + 1].start() if i + 1 < len(h2_splits) else len(body)
        sections.append((s, e))

    if not sections:
        return body + embed_line

    # Top-down: pick first section with no media
    best_idx = 0  # fallback to first section
    for i, (s, e) in enumerate(sections):
        if _count_media(body[s:e]) == 0:
            best_idx = i
            break

    # Insert after first </p> in chosen section
    s, e = sections[best_idx]
    section_text = body[s:e]
    p_ends = [m.end() for m in re.finditer(r'</p>', section_text, re.IGNORECASE)]
    if p_ends:
        insert_pos = s + p_ends[0]
    else:
        insert_pos = e

    return body[:insert_pos] + embed_line + body[insert_pos:]


def reposition_bottom_trailer(body):
    """Move a <youtube> trailer from the bottom 20% of the article to after the 2nd paragraph.

    Returns (new_body, moved: bool). Only moves if the trailer is in the
    bottom 20% by character position — mid-article trailers are left alone.
    """
    m = re.search(r'<youtube>.*?</youtube>', body, re.IGNORECASE | re.DOTALL)
    if not m:
        return body, False

    pos = m.start()
    total = len(body)
    if pos / total < 0.80:
        return body, False  # not at the bottom, leave it

    trailer_tag = m.group(0)
    # Remove from current position
    body_without = body[:m.start()] + body[m.end():]
    # Clean up leftover empty lines
    body_without = re.sub(r'\n{3,}', '\n\n', body_without)

    # Insert after 2nd </p> (skip key-takeaways div if present)
    # Find paragraphs outside the key-takeaways block
    kt_end = 0
    kt_match = re.search(r'<div class="key-takeaways".*?</div>', body_without,
                         re.IGNORECASE | re.DOTALL)
    if kt_match:
        kt_end = kt_match.end()

    search_from = kt_end
    p_ends = [me.end() for me in re.finditer(r'</p>', body_without[search_from:],
                                             re.IGNORECASE)]
    if len(p_ends) >= 2:
        insert_pos = search_from + p_ends[1]
    elif p_ends:
        insert_pos = search_from + p_ends[0]
    else:
        insert_pos = search_from

    new_body = (body_without[:insert_pos]
                + f"\n\n{trailer_tag}\n"
                + body_without[insert_pos:])
    return new_body, True


# ── YouTube embed quality guard (shared) ─────────────────────────────
# Added 2026-10-12 after a pirate-bait upload ("Movies RYS" — title stuffed
# with "full movie" + a song name) was embedded as the "official trailer"
# on a box-office article. Rules:
#   1. Pirate-bait titles are ALWAYS rejected ("full movie", "watch online",
#      "free download", ...).
#   2. A video whose title says trailer/teaser must come from an official
#      channel on the trailer-channels.json allowlist — the same single
#      source of truth trailer-watch.py polls and prebuild-feeds.py gates
#      the trailers rail on. A missing trailer beats a fake one.

_PIRATE_BAIT_RE = re.compile(
    r"full\s+movie|full\s+film|watch\s+online|free\s+download|download\s+link",
    re.IGNORECASE,
)
_TRAILERISH_RE = re.compile(r"\b(?:trailer|teaser)\b", re.IGNORECASE)

_OFFICIAL_CHANNELS_CACHE = None
_OFFICIAL_IDS_CACHE = None
_OFFICIAL_NAMES_CACHE = None
_TITLE_EXCEPTION_CACHE = None


def _load_channel_configs():
    """Parsed channel configs: (trailer-channels.json, official-video-channels.json)."""
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for fname in ("trailer-channels.json", "official-video-channels.json"):
        try:
            with open(os.path.join(here, fname)) as f:
                out.append(json.load(f))
        except Exception:
            out.append({})
    return out


def official_channel_ids():
    """Channel IDs from BOTH channel allowlists (trailer + official-video).

    This is the merged channel-authority universe for embed gates: a
    video whose channelId is in here is on a verified official channel,
    whichever surface (trailer rail or rights-holder pass) vetted it.
    """
    global _OFFICIAL_IDS_CACHE
    if _OFFICIAL_IDS_CACHE is None:
        ids = set()
        for cfg in _load_channel_configs():
            for c in cfg.get("channels", []):
                cid = (c.get("channel_id") or "").strip()
                if cid:
                    ids.add(cid)
        _OFFICIAL_IDS_CACHE = ids
    return _OFFICIAL_IDS_CACHE


def official_channel_names():
    """Lowercased channel names + aliases from BOTH channel allowlists."""
    global _OFFICIAL_NAMES_CACHE
    if _OFFICIAL_NAMES_CACHE is None:
        names = set()
        for cfg in _load_channel_configs():
            for c in cfg.get("channels", []):
                if c.get("name"):
                    names.add(c["name"].strip().lower())
                for alias in c.get("aliases") or []:
                    if alias and alias.strip():
                        names.add(alias.strip().lower())
        _OFFICIAL_NAMES_CACHE = names
    return _OFFICIAL_NAMES_CACHE


def region_allows_us(region_restriction):
    """Pure rule: may this video play for a US viewer?

    Twin of official_video_pass.region_allows_us (kept there because
    that module imports this one — the rule is 8 lines and must agree;
    the 2026-10-25 Shadab/PCB incident is why it exists: an `allowed`
    list is exhaustive, a `blocked` list plays everywhere else, and
    neither field means no restriction).
    """
    rr = region_restriction or {}
    allowed = rr.get("allowed")
    if allowed is not None:
        return "US" in allowed
    blocked = rr.get("blocked")
    if blocked is not None:
        return "US" not in blocked
    return True


# Established news organisations whose channels are verified official
# sources for a generic (non-trailer) news embed — the NDTV Profit
# pattern (an entity's results video on a broadcaster's channel). This
# is NOT a trailer authority: trailer/teaser embeds still require the
# channel allowlists above, enforced by youtube_embed_reject_reason
# and trailer_embed_gate. Fan/news-aggregator channels (Narayanatv,
# Rahil Store, Filmy Star, ...) are deliberately absent.
NEWS_ORG_CHANNELS = {
    "ndtv", "ndtv profit", "ndtv india", "ndtv 24x7",
    "times now", "times now navbharat", "times now world",
    "india today", "aaj tak", "zee news", "zee business", "zee 24 taas",
    "cnbc-tv18", "cnbc awaaz", "cnbc bajar", "et now", "et now swadesh",
    "republic tv", "republic bharat", "republic world", "wion",
    "firstpost", "moneycontrol", "ani news", "news18", "news18 india",
    "news18 punjab", "abp news", "abp live", "abp ananda", "abp majha",
    "sun news", "thanthi tv", "polimer news", "news7 tamil",
    "puthiya thalaimurai", "asianet news", "manorama news",
    "mathrubhumi news", "media one", "24 news", "etv bharat",
    "tv9 bharatvarsh", "tv9 telugu", "tv9 kannada", "tv9 marathi",
    "tv9 bangla", "tv5 news telugu", "ntv telugu", "abn telugu",
    "sakshi tv", "10tv news telugu", "v6 news telugu", "raj news telugu",
    "reuters", "associated press", "bbc news", "cnn", "al jazeera english",
    "bloomberg television", "bloomberg podcasts", "the hindu",
    "the shillong times", "shethepeople tv",
    "hindustan times", "the indian express", "india tv", "newsx",
    "mirchi", "good news today", "the quint", "the wire", "scroll india",
    "deccan herald", "the print", "livemint", "business today",
    "business standard", "the economic times", "financial express",
    "dd news", "sansad tv", "pib india",
}


def _norm_channel(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def channel_authority_reason(channel_title, channel_id=None, entity_name=None):
    """Channel authority for a SEARCH-selected embed. Returns a reject
    reason, or None when the channel is a verified official source:

      1. channelId on the merged official allowlists, or
      2. channel name/alias on the merged official allowlists, or
      3. the entity's OWN channel (the full entity name appears in the
         channel title — Air India's announcements on 'Air India',
         ISRO footage on 'ISRO', a representative's own channel), or
      4. an established news organisation's channel (NEWS_ORG_CHANNELS).

    Anything else — fan channels, aggregators, random uploaders — has
    no verifiable authority and must not carry an embed. Added
    2026-10-31 after a Narayanatv box-office video was embedded as the
    Jailer 2 'trailer': the shared gate's channel rule only fired on
    trailer/teaser TITLES, so a non-trailer video from a fan channel
    sailed through every search-based route.
    """
    ch = _norm_channel(channel_title)
    if channel_id and channel_id.strip() in official_channel_ids():
        return None
    if ch and ch in official_channel_names():
        return None
    ent = _norm_channel(entity_name)
    if ent and len(ent) >= 3 and re.search(
            r"\b" + re.escape(ent) + r"\b", ch):
        return None
    if ch in NEWS_ORG_CHANNELS:
        return None
    return (f"channel '{channel_title}' has no verified authority "
            f"(not allowlisted, not the entity's own channel, "
            f"not a recognized news channel)")


# Words that carry no film-identity signal in a title.
_FILM_TITLE_STOPWORDS = {"the", "a", "an", "of", "part", "chapter"}


def title_names_film(video_title, film_title):
    """True when every significant token of the film title appears in
    the video title (the wrong-film-on-the-right-channel check)."""
    def toks(text):
        words = re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).split()
        return [w for w in words if w not in _FILM_TITLE_STOPWORDS]
    significant = [t for t in toks(film_title) if len(t) >= 3] \
        or toks(film_title)
    vtoks = set(toks(video_title))
    return all(t in vtoks for t in significant)


# ── Language-version evidence (2026-11-06) ──────────────────────────
# Twins of trailer-watch.py's extract_language /
# extract_description_language — kept here for the same reason
# region_allows_us is twinned below: embed_placement is imported BY
# the modules that would otherwise have to load a 1,600-line hyphenated
# script (trailer-watch.py reads sys.argv at module level), and the
# rules are small and must agree. If trailer-watch's patterns change,
# mirror them here (test_trailer_language_version.py pins the shared
# behaviors on the incident fixtures).
#
# A language is only ever DETECTED from an explicit statement — a word
# in the title, a hashtag / "language:" line / adjective phrase in the
# description. Absence of evidence returns None; nothing is inferred
# from a channel's industry: trailer-channels.json's industry is a
# channel-level primary label, and multi-language distributors make it
# affirmatively misleading per-video (Panorama Studios is rostered as
# industry "marathi" yet produced the Hindi Drishyam: The Conclusion
# AND distributed its Malayalam namesake). Channel industry is
# therefore deliberately NOT a language signal for a candidate video.

_TITLE_LANG_RE = (r"hindi|tamil|telugu|kannada|malayalam|bengali|"
                  r"marathi|punjabi|gujarati|english")

# Languages a description may state outright — a superset of the title
# list (adds Assamese, Odia, Urdu, which title tags don't use but
# description prose does). Mirrors trailer-watch._DESC_LANGS.
_STATED_LANGS = ["Hindi", "Bengali", "Telugu", "Tamil", "Malayalam",
                 "Kannada", "Marathi", "Punjabi", "Assamese", "Odia",
                 "Gujarati", "Urdu", "English"]
_STATED_LANG_RE = "|".join(_STATED_LANGS)
_STATED_LANG_LOWER_RE = "|".join(l.lower() for l in _STATED_LANGS)


def detect_title_language(title):
    """Language word stated in a title ('... (Kannada) | Official
    Trailer' -> 'Kannada'), else None. Twin of trailer-watch's
    extract_language."""
    m = re.search(r"\b(" + _TITLE_LANG_RE + r")\b", title or "", re.I)
    return m.group(1).capitalize() if m else None


def detect_stated_language(text):
    """Language a text states outright, or None.

    Only explicit statements count, strongest first: a language hashtag
    (#BengaliWebSeries, #bengali), a 'language: Bengali' credit line, an
    adjective phrase ('Bengali series', 'Malayalam cinema'), or 'in
    Bengali' (subtitle mentions excluded — 'subtitles in English'
    describes the subtitles, not the work). If a pattern names several
    languages the work is not single-language: return None rather than
    guess (a wrong label is worse than none). Twin of trailer-watch's
    extract_description_language."""
    text = unicodedata.normalize("NFKD", text or "")
    patterns = (
        r"#(" + _STATED_LANG_RE + r")(?=[A-Z]|[^A-Za-z]|$)",
        r"#(" + _STATED_LANG_LOWER_RE + r")(?=[^a-z]|$)",
        r"(?i)\blanguage\s*[:\-]\s*(" + _STATED_LANG_RE + r")\b",
        r"(?i)\b(" + _STATED_LANG_RE + r")\s+"
        r"(?:web\s+series|series|films?|movies?|shows?|cinema)\b",
    )
    for pat in patterns:
        found = {m.group(1).capitalize() for m in re.finditer(pat, text)}
        if len(found) == 1:
            return found.pop()
        if len(found) > 1:
            return None
    # 'in X' last: a list continuation ('in Hindi, Tamil and Telugu')
    # names every language in the list, not just the first.
    found = set()
    for m in re.finditer(
            r"(?i)(?<!subtitle )(?<!subtitles )\bin\s+(" + _STATED_LANG_RE
            + r")\b", text):
        found.add(m.group(1).capitalize())
        tail = text[m.end():m.end() + 60]
        while True:
            lm = re.match(r"\s*(?:,|and|&)\s*(" + _STATED_LANG_RE + r")\b",
                          tail, re.I)
            if not lm:
                break
            found.add(lm.group(1).capitalize())
            tail = tail[lm.end():]
    if len(found) == 1:
        return found.pop()
    return None


def candidate_language(title, description=None):
    """The language version a trailer candidate positively IS, from
    per-video evidence only: (1) a language word in the video title,
    (2) an explicit language statement in its description. None when
    neither states one — an undetected language is NOT a mismatch and
    must never reject a candidate (the Hindi Drishyam trailer states
    no language anywhere; its Malayalam namesake's description says
    'Malayalam cinema' outright)."""
    return detect_title_language(title) \
        or detect_stated_language(description)


def title_exception_channels():
    """(ids, names) of trailer-roster channels flagged title_exception.

    Loads ONLY trailer-channels.json (never the merged official-video
    allowlist): the entries flagged `"title_exception": true` are the
    producer/studio-owned channels whose featured film videos may pass
    trailer_embed_gate's title leg without trailer/teaser wording
    (2026-11-13, Kiran-approved — see the gate's docstring). Names are
    normalized like the gate compares them and include aliases.
    """
    global _TITLE_EXCEPTION_CACHE
    if _TITLE_EXCEPTION_CACHE is None:
        ids, names = set(), set()
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "trailer-channels.json")
            with open(path) as f:
                cfg = json.load(f)
            for c in cfg.get("channels", []):
                if not c.get("title_exception"):
                    continue
                cid = (c.get("channel_id") or "").strip()
                if cid:
                    ids.add(cid)
                for nm in [c.get("name")] + list(c.get("aliases") or []):
                    if nm and nm.strip():
                        names.add(_norm_channel(nm))
        except Exception:
            ids, names = set(), set()
        _TITLE_EXCEPTION_CACHE = (ids, names)
    return _TITLE_EXCEPTION_CACHE


# Song/music markers that DENY the title exception (2026-11-13
# tightening, Kiran-approved). The exception exists for a producer
# channel's FEATURED film video; on first live use it also passed a
# Vels song video ("Mahasakthi Trance Video | Mookuthi Amman 2…",
# 7H4SOzsX8m4) — right channel, title names the film, but a song, not
# the film's featured video. On the exception path ONLY, a title
# carrying any of these markers rejects. The normal trailer/teaser
# path never sees this screen: a properly-titled "Official Trailer"
# is unaffected even if its title also mentions a song. Multi-word
# markers are listed first so the reported marker is the specific one.
_TITLE_EXCEPTION_MARKERS = (
    "behind the scenes", "music video", "video song", "promo song",
    "song promo", "cover song", "dance video", "full video",
    "song", "songs", "lyrical", "lyric", "jukebox", "audio", "bgm",
    "theme", "trance", "mashup", "remix", "making", "bts",
)
_TITLE_EXCEPTION_MARKER_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(m) for m in _TITLE_EXCEPTION_MARKERS)
    + r")\b", re.IGNORECASE)


def _title_exception_marker(title):
    """First song/music marker in a title, or None (exception screen)."""
    m = _TITLE_EXCEPTION_MARKER_RE.search(title or "")
    return m.group(0).lower() if m else None


def trailer_embed_gate(title, channel_title, channel_id=None,
                       region_restriction=None, region_checked=False,
                       film_title=None, film_language=None,
                       description=None):
    """THE gate for any embed PRESENTED AS A TRAILER (the trailer pass
    in enrich-articles, source-image --trailer, media-sources). Returns
    a reject reason, or None when the video may be embedded as a
    trailer. Fail-closed on every leg:

      1. the shared gate (pirate-bait / unofficial-trailer /
         first-person) — WITHOUT the generic route's topical-overlap
         rule: a trailer's identity anchor is legs 2–4, and a
         box-office headline legitimately shares only the film's name
         with its trailer's title;
      2. the VERIFIED title must actually say trailer/teaser — the
         search snippet that surfaced the candidate is not evidence
         (the scrape's title array misaligns with its video IDs).
         NARROW EXCEPTION (2026-11-13, Kiran-approved): on a
         producer/studio-owned channel flagged `"title_exception":
         true` in trailer-channels.json (see
         title_exception_channels()), a featured film video whose
         title does NOT say trailer/teaser may still pass this leg —
         but ONLY when the film is known (film_title given) and the
         title names it (leg 4's check, applied here). Rationale:
         Vels Music International, the producer channel for Mookuthi
         Amman 2, titled the film's official video "World Of
         Mahasakthi" with no trailer/teaser wording, and no
         trailer-titled official upload exists. The exception covers
         producer/studio channels only — music labels, distributors
         and streaming channels are NOT flagged — and every other leg
         (channel authority, language version, US region) applies
         unchanged. TIGHTENING (2026-11-13, Kiran-approved): on the
         exception path only, a title carrying a song/music marker
         (song, lyrical, jukebox, audio, bgm, theme, trance, music
         video, making, behind the scenes, … — see
         _TITLE_EXCEPTION_MARKERS) is denied the waiver: the
         exception's first live use passed a Vels SONG video
         ("Mahasakthi Trance Video"), which the channel + film-name
         checks alone cannot distinguish from the featured film
         video. The screen never applies to the normal
         trailer/teaser path;
      3. channel authority: channelId or channel name on the merged
         official allowlists ONLY (news-org status does not make a
         trailer official);
      4. when the film is known, the title must name it;
      5. when the film's language is known, the candidate must not
         positively be a DIFFERENT language version of the film
         (candidate_language: an explicit language word in its title
         or statement in its description). An undetected candidate
         language is not a mismatch — only a positive conflict
         rejects, so an unlabeled right-version trailer still passes;
      6. US region: the caller must have LOOKED (region_checked) and
         the restriction must allow US — an embed that renders is not
         an embed that plays.

    The 2026-10-31 Narayanatv case failed legs 2+3 simultaneously and
    the old _verify_official_trailer checked neither. Leg 5 is the
    2026-11-06 Drishyam 3 case: the Malayalam trailer (Mohanlal) is a
    legitimate official trailer that passed legs 1–4 for the HINDI
    article — same title, official channel, US-playable — and only
    its description ('Malayalam cinema') betrays the version.
    """
    reason = youtube_embed_reject_reason(title, channel_title)
    if reason:
        return reason
    # Channel authority is determined first: the title leg's exception
    # needs it, and a non-allowlisted channel rejects with the exact
    # existing message below regardless of the title.
    ch = _norm_channel(channel_title)
    id_ok = bool(channel_id) and channel_id.strip() \
        in official_channel_ids()
    name_ok = ch in official_channel_names()
    if not _TRAILERISH_RE.search((title or "").lower()):
        # Title exception (2026-11-13, Kiran-approved): a featured
        # film video on a producer/studio channel flagged
        # title_exception may pass without trailer/teaser wording —
        # only when the film is known AND the title names it. The
        # channel must ALSO be allowlisted (checked next); exception
        # membership never substitutes for channel authority.
        exc_ids, exc_names = title_exception_channels()
        exc_ok = (bool(channel_id)
                  and channel_id.strip() in exc_ids) or ch in exc_names
        if exc_ok and film_title \
                and title_names_film(title, film_title):
            # Waiver would apply — but a song/music title is not the
            # film's featured video (2026-11-13 tightening).
            marker = _title_exception_marker(title)
            if marker:
                return ("title-exception denied: title carries a "
                        f"song/music marker '{marker}' — not the "
                        "film's featured video")
        else:
            return ("video title does not say trailer/teaser "
                    "— not a trailer")
    if not id_ok and not name_ok:
        return (f"trailer channel '{channel_title}' is not on the "
                f"official-channel allowlist")
    if film_title and not title_names_film(title, film_title):
        return f"video title does not name the film '{film_title}'"
    if film_language:
        cand_lang = candidate_language(title, description)
        if cand_lang and cand_lang.lower() \
                != film_language.strip().lower():
            return (f"trailer is the {cand_lang} version of the film "
                    f"— the article's film is {film_language} "
                    f"(wrong language version)")
    if not region_checked:
        return "region restriction unverified — rejected (fail-closed)"
    if not region_allows_us(region_restriction):
        return f"region-blocked for US audience: {region_restriction}"
    return None


def official_trailer_channels():
    """Lowercased official channel names from pipeline/trailer-channels.json.

    A channel's "aliases" count as that channel: YouTube's live display
    name can differ from the config label (Sun Pictures uploads under
    "Sun TV"). Aliases extend acceptance only — a trailer/teaser title
    is still required, and pirate-bait is still rejected first.
    (2026-10-30: the gate rejected an official Sun TV trailer and a fan
    video was embedded in its place.)
    """
    global _OFFICIAL_CHANNELS_CACHE
    if _OFFICIAL_CHANNELS_CACHE is None:
        names = set()
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "trailer-channels.json")
            with open(path) as f:
                cfg = json.load(f)
            for c in cfg.get("channels", []):
                if c.get("name"):
                    names.add(c["name"].strip().lower())
                for alias in c.get("aliases") or []:
                    if alias and alias.strip():
                        names.add(alias.strip().lower())
        except Exception:
            names = set()
        _OFFICIAL_CHANNELS_CACHE = names
    return _OFFICIAL_CHANNELS_CACHE


# ── First-person / review / rant / vlog gate (2026-10-15) ────────────
# Added after the reviewer had to strip two junk embeds in 12 hours:
# a first-person rant ("My NIGHTMARE Experience Flying Air India Economy
# class to Delhi") embedded on the Air India Delhi–Osaka route-launch
# article, and an off-topic video that scored on channel authority alone
# (see the topical-overlap rule in youtube_embed_reject_reason).
# A personal vlog/review is never a news embed, however relevant the
# entity match looks — hard reject, not a score penalty.
_FIRST_PERSON_RE = re.compile(
    r"\bmy\s+(?:nightmare|experience|honest|journey|story|review|trip|flight|"
    r"travel|stay|visit|adventure|reaction)\b"
    r"|\bmy\s+first\s+(?:time|flight|trip|visit|class)\b"
    r"|\bi\s+(?:tried|flew|travelled|traveled|visited|stayed|ate|booked|"
    r"survived|reviewed)\b"
    r"|\bhonest\s+review\b"
    r"|\bworst\s+(?:flight|airline|experience|airport|hotel|train)\b"
    r"|\bvlog\b"
    r"|\bcome\s+with\s+me\b"
    r"|\bday\s+in\s+(?:my|the)\s+life\b"
    r"|\bpov\s*[:|]"
    r"|\b(?:trailer|teaser|song|music\s+video|mv)\s+reaction\b"
    r"|\breaction\s+video\b",
    re.IGNORECASE,
)

# ── Topical-overlap guard (2026-10-15) ───────────────────────────────
# A video may embed ONLY if its title shares real topical vocabulary
# with the article headline. Channel authority is NOT evidence of
# topical relevance: the Jayapal voter-roll article got an "AI chatbots"
# video purely because it sat on Pramila Jayapal's own channel.
_CONTENT_STOPWORDS = {
    "the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to",
    "with", "by", "from", "as", "its", "it", "that", "this", "but", "or",
    "has", "had", "was", "were", "are", "be", "been", "being", "have",
    "says", "said", "could", "would", "will", "can", "may", "more",
    "after", "before", "about", "into", "over", "under", "amid",
}


def _content_words(text):
    """Distinctive words (len>=3, non-stopword) of a headline/title."""
    words = re.findall(r"[a-z]{3,}", (text or "").lower())
    return {w for w in words if w not in _CONTENT_STOPWORDS}


def youtube_embed_reject_reason(title, channel, headline=None):
    """Return a short reason if a YouTube result must NOT be embedded, else None.

    Rules 1–2 (pirate-bait, unofficial trailer) need only title+channel.
    Rule 3 (first-person/review/rant/vlog) is title-only. Rule 4
    (topical overlap) applies when the caller supplies the article
    headline: the title must share >= 2 content words with it.
    """
    t = (title or "").lower()
    if _PIRATE_BAIT_RE.search(t):
        return "pirate-bait title"
    if _TRAILERISH_RE.search(t):
        officials = official_trailer_channels()
        ch = (channel or "").strip().lower()
        if officials and ch not in officials:
            return f"trailer from non-official channel '{channel}'"
    if _FIRST_PERSON_RE.search(t):
        return "first-person/review/vlog title — not a news embed"
    if headline:
        headline_words = _content_words(headline)
        if len(headline_words) >= 2:
            overlap = headline_words & _content_words(title)
            if len(overlap) < 2:
                return "no topical overlap with article headline"
    return None


# ── Canonical YouTube scoring (2026-10-15 unification) ────────────────
# enrich-on-publish.py and enrich-articles.py each carried a FORKED copy
# of score_youtube_result with divergent junk lists and — critically —
# divergent acceptance thresholds (enrich-articles accepted at score>=3
# with no keyword floor; that hole let both junk embeds above through).
# This is now the ONLY scorer; both enrichers call youtube_embed_accept().

_YT_SKIP_TITLE_WORDS = {
    "compilation", "top 10", "top 5", "top 20", "meme", "memes", "funny",
    "prank", "reaction video", "fan edit", "whatsapp status",
    "#shorts", "tiktok", "roast", "exposed", "scam",
    # Music / entertainment junk
    "official audio", "official video", "music video", "lyrics",
    "lyric video", "audio only", "full album", "mixtape", "beat",
    "instrumental", "karaoke", "remix", "cover song", "dance cover",
    "fan cam", "fancam",
    # Other irrelevant content types
    "unboxing", "haul", "asmr", "mukbang", "gameplay", "walkthrough",
    "let's play", "speedrun", "tutorial makeup",
    # Pirate-bait (hard gate above; these are belt-and-braces)
    "full movie", "full film", "watch online", "free download",
}

_NON_LATIN_RE = re.compile(
    r'[\u0900-\u097F\u0980-\u09FF\u0C00-\u0C7F\u0C80-\u0CFF\u0B80-\u0BFF'
    r'\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0D00-\u0D7F'
    r'\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]')


def is_non_english_title(title: str) -> bool:
    """Return True if >25% of alpha chars are non-Latin script."""
    alpha_chars = [c for c in (title or "") if c.isalpha()]
    if len(alpha_chars) < 3:
        return False
    non_latin = sum(1 for c in alpha_chars
                    if unicodedata.category(c).startswith('L') and ord(c) > 0x024F)
    return (non_latin / len(alpha_chars)) > 0.25


def _skip_word_hit(title_lower, skip_word):
    """Match a junk phrase in a title. Single words match on word
    boundaries so 'beat' does not penalize a headline about earnings
    ('Wipro Beats Estimates' was collateral damage of substring match)."""
    if " " in skip_word or not skip_word.isalpha():
        return skip_word in title_lower
    return re.search(r'\b' + re.escape(skip_word) + r'\b', title_lower) is not None


def score_youtube_result(result, entity_name, keywords):
    """Canonical relevance score for a YouTube search result."""
    title_lower = result["title"].lower()
    channel_lower = result["channelTitle"].lower()
    entity_lower = (entity_name or "").lower()
    entity_parts = [p for p in entity_lower.split() if len(p) > 2]

    score = 0
    # Entity name in video title
    if entity_lower and entity_lower in title_lower:
        score += 4
    elif entity_parts and all(p in title_lower for p in entity_parts):
        score += 3
    # Entity name in channel name (official channel)
    if entity_lower and entity_lower in channel_lower:
        score += 3
    elif any(p in channel_lower for p in entity_parts if p not in {"the", "of", "in"}):
        score += 1

    # Keyword matches in title
    kw_hits = sum(1 for kw in keywords if kw and kw in title_lower)
    score += kw_hits * 1.5

    # Junk-content penalty
    for skip_word in _YT_SKIP_TITLE_WORDS:
        if _skip_word_hit(title_lower, skip_word):
            score -= 5

    # Non-English script penalty (title/channel)
    non_latin_in_title = len(_NON_LATIN_RE.findall(result["title"]))
    non_latin_in_channel = len(_NON_LATIN_RE.findall(result["channelTitle"]))
    if non_latin_in_title >= 3:
        score -= 10
    elif non_latin_in_title >= 1:
        score -= 3
    if non_latin_in_channel >= 2:
        score -= 3

    # "official" bonus — but NOT for music content (official audio/video/music)
    _music_official = {"official audio", "official music", "official video",
                       "official mv"}
    if not any(mo in title_lower for mo in _music_official):
        official_words = {"official", "press conference", "interview",
                          "statement", "announcement", "keynote", "launch",
                          "podcast", "speech"}
        for ow in official_words:
            if ow in title_lower:
                score += 1
                break

    # Channel relevance penalty — a channel with zero overlap with the
    # entity or keywords is likely unrelated (random music, gaming, ...)
    _channel_words = set(re.findall(r'[a-z]{3,}', channel_lower))
    _entity_words = set(re.findall(r'[a-z]{3,}', entity_lower))
    _all_relevant = _entity_words | {k for k in keywords if k}
    if _channel_words and not (_channel_words & _all_relevant):
        score -= 2

    # Recency bonus
    try:
        pub = datetime.fromisoformat(result["publishedAt"].replace("Z", "+00:00"))
        days_old = (datetime.now(timezone.utc) - pub).days
        if days_old <= 3:
            score += 2
        elif days_old <= 7:
            score += 1
    except Exception:
        pass

    return score


def youtube_embed_accept(result, entity_name, keywords, headline=None):
    """THE gate every embed-selecting path must use.

    Returns (score, None) if the video may be embedded, else
    (score_or_0, reason). Applies, in order: the shared reject gate
    (pirate-bait / unofficial trailer / first-person-rant / topical
    overlap with the headline), the English-title filter, channel
    authority (channel_authority_reason — allowlisted, entity's own,
    or recognized news channel), the canonical score threshold (>=6,
    or >=8 for single-word entity names), and a floor of >=2
    headline-keyword matches in the title — so an off-topic video can
    never ride in on channel authority alone, and an on-topic video
    can never ride in from a fan channel.
    """
    title = result.get("title", "")
    channel = result.get("channelTitle", "")
    reason = youtube_embed_reject_reason(title, channel, headline=headline)
    if reason:
        return 0, reason
    if is_non_english_title(title):
        return 0, "non-English title"
    # Channel authority (2026-10-31): a search result may only embed
    # from a verified official source — allowlisted channel, the
    # entity's own channel, or a recognized news organisation. Runs
    # AFTER the reject gate so the standing specific reasons (pirate-
    # bait, unofficial trailer, first-person, topical) keep precedence.
    authority = channel_authority_reason(
        channel, result.get("channelId"), entity_name)
    if authority:
        return 0, authority
    score = score_youtube_result(result, entity_name, keywords)
    title_lower = title.lower()
    kw_hits = sum(1 for kw in keywords if kw and kw in title_lower)
    if kw_hits < 2:
        return score, f"only {kw_hits} headline-keyword match(es) in title"
    min_score = 8 if len((entity_name or "").split()) == 1 else 6
    if score < min_score:
        return score, f"score {score} below threshold {min_score}"
    return score, None
