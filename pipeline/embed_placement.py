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


def official_trailer_channels():
    """Lowercased official channel names from pipeline/trailer-channels.json."""
    global _OFFICIAL_CHANNELS_CACHE
    if _OFFICIAL_CHANNELS_CACHE is None:
        names = set()
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "trailer-channels.json")
            with open(path) as f:
                cfg = json.load(f)
            names = {c["name"].strip().lower()
                     for c in cfg.get("channels", []) if c.get("name")}
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
    overlap with the headline), the English-title filter, the canonical
    score threshold (>=6, or >=8 for single-word entity names), and a
    floor of >=2 headline-keyword matches in the title — so an
    off-topic video can never ride in on channel authority alone.
    """
    title = result.get("title", "")
    channel = result.get("channelTitle", "")
    reason = youtube_embed_reject_reason(title, channel, headline=headline)
    if reason:
        return 0, reason
    if is_non_english_title(title):
        return 0, "non-English title"
    score = score_youtube_result(result, entity_name, keywords)
    title_lower = title.lower()
    kw_hits = sum(1 for kw in keywords if kw and kw in title_lower)
    if kw_hits < 2:
        return score, f"only {kw_hits} headline-keyword match(es) in title"
    min_score = 8 if len((entity_name or "").split()) == 1 else 6
    if score < min_score:
        return score, f"score {score} below threshold {min_score}"
    return score, None
