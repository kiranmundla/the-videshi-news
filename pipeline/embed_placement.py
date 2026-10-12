"""Shared embed placement logic — place embeds high but never cluster media."""

import json
import os
import re

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


def youtube_embed_reject_reason(title, channel):
    """Return a short reason if a YouTube result must NOT be embedded, else None."""
    t = (title or "").lower()
    if _PIRATE_BAIT_RE.search(t):
        return "pirate-bait title"
    if _TRAILERISH_RE.search(t):
        officials = official_trailer_channels()
        ch = (channel or "").strip().lower()
        if officials and ch not in officials:
            return f"trailer from non-official channel '{channel}'"
    return None
