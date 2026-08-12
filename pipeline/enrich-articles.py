#!/usr/bin/env python3
"""
Article enrichment pipeline:
1. Replace generic Pexels hero images with better CC-licensed images (Openverse + Wikimedia Commons + Google CSE)
2. Add YouTube trailer embeds for movie/series articles
3. Add Instagram embeds for entertainment articles with matching celebrity handles
4. Add X/Twitter embeds for articles with matching registry handles (calls tweet-enricher)
5. Add inline Wikipedia images for key entities mentioned in articles
6. Add pull quotes for visual richness

Usage:
  python3 enrich-articles.py --hours 24 --dry-run    # preview changes
  python3 enrich-articles.py --hours 24 --apply       # apply changes
  python3 enrich-articles.py --images-only --apply     # only fix images
  python3 enrich-articles.py --embeds-only --apply     # only add embeds
  python3 enrich-articles.py --trailers-only --apply   # only add YouTube trailers
  python3 enrich-articles.py --inline-only --apply     # only add inline images + pull quotes
"""

import os, sys, json, re, time, argparse, subprocess
import requests
from urllib.parse import quote

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)

from importlib.machinery import SourceFileLoader
media_sources = SourceFileLoader("media_sources", os.path.join(PIPELINE_DIR, "media-sources.py")).load_module()

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.twitter"))
load_env(os.path.expanduser("~/workspace/.env.openai"))
load_env(os.path.expanduser("~/workspace/.env.google-ai"))
load_env(os.path.expanduser("~/workspace/.env.apify"))

# ── Reuse the vision wrong-photo gate from the reviewer ──
# A hero swap on a LIVE article must never push a clearly wrong-subject photo
# (Gandalf meme on a visa story, Miss-America pageant on an immigration story).
# review-articles.py already has a vision judge with an OpenAI→Gemini fallback;
# import it rather than re-implement. Guarded so enrichment still runs if the
# reviewer module can't be loaded for any reason.
try:
    _review = SourceFileLoader("review_articles", os.path.join(PIPELINE_DIR, "review-articles.py")).load_module()
    _vision_image_match = getattr(_review, "vision_image_match", None)
except Exception as _e:
    _vision_image_match = None
    print(f"  ⚠️  Could not load vision check from review-articles.py: {_e}")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

_session = requests.Session()
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
_session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5)))


# ═══════════════════════════════════════════
# IMAGE ENRICHMENT — Openverse + Wikimedia
# ═══════════════════════════════════════════

# Generic geo/common tokens that must NOT, on their own, justify a hero-image
# swap. A title that overlaps the headline only on words like "india"/"america"/
# "visa" is not a real subject match. Mirrors the tweet enricher's set.
_GENERIC_TOKENS = {
    'india','indian','indians','uk','britain','british','us','usa','america',
    'american','china','chinese','pakistan','europe','european','world',
    'global','nation','national','country','government','govt','state','states',
    'president','minister','ministry','official','officials','leader','leaders',
    'trade','deal','talks','summit','meeting','market','markets','economy',
    'economic','political','politics','policy','news','report','update','latest',
    'breaking','will','your','just','door','sell','now','visa','visas',
    'legal','immigration','people','workers','study','abroad',
}


def search_openverse(query, limit=5):
    """Search Openverse for CC-licensed images."""
    try:
        r = _session.get(
            "https://api.openverse.org/v1/images/",
            params={
                "q": query,
                "license": "by,by-sa,by-nd,pdm,cc0",
                "page_size": limit,
            },
            timeout=15,
        )
        if r.status_code == 200:
            results = []
            for item in r.json().get("results", []):
                w = item.get("width", 0)
                h = item.get("height", 0)
                if w < 400 or h < 300:
                    continue
                results.append({
                    "url": item["url"],
                    "title": item.get("title", ""),
                    "source": item.get("source", ""),
                    "license": item.get("license", ""),
                    "width": w,
                    "height": h,
                    "creator": item.get("creator", ""),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Openverse error: {e}")
    return []


def search_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    try:
        r = _session.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "generator": "search",
                "gsrsearch": query,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": "1200",
                "format": "json",
            },
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 400:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                    "source": "wikimedia",
                    "width": w,
                    "height": ii.get("height", 0),
                })
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia error: {e}")
    return []


def fetch_wikipedia_image(subject, article_context=None):
    """Get the main Wikipedia image for a subject.

    If article_context (headline or body snippet) is provided, validates that
    the Wikipedia page is actually about the same topic — not a disambiguation
    or generic concept page whose image has nothing to do with the article.
    """
    try:
        encoded = quote(subject.replace(" ", "_"))
        r = _session.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if not img:
                return None

            # ── Relevance guard ──
            # Reject images from generic/disambiguation Wikipedia pages that
            # match a common phrase but have nothing to do with the article.
            wiki_title = (data.get("title") or "").lower()
            wiki_desc = (data.get("description") or "").lower()
            wiki_type = (data.get("type") or "")

            # Reject disambiguation pages outright
            if wiki_type == "disambiguation" or "disambiguation" in wiki_desc:
                print(f"    ⊘ Skipping Wikipedia image for '{subject}' — disambiguation page")
                return None

            # Reject generic concept pages (no specific person/place/org)
            _GENERIC_WIKI_DESCRIPTIONS = {
                "international competition", "competition", "sporting event",
                "award", "awards ceremony", "trophy", "memorial",
                "concept", "term", "phrase", "expression", "song",
                "album", "single", "film", "television series",
                "video game", "book", "novel", "poem",
                # Newspapers / publications — images are front pages, not useful
                "newspaper", "daily newspaper", "indian newspaper",
                "english-language newspaper", "publication", "news media",
                "magazine", "journal", "tabloid", "news agency",
                "indian english-language daily newspaper",
                "indian english-language newspaper",
                # More generic categories
                "sports competition", "tournament", "cup", "league",
                "recurring sporting event", "annual sporting event",
                "festival", "ceremony", "event",
                # Awards/prizes — medal/logo images are misleading on
                # articles about a *different* award
                "prize", "prizes", "medal", "honour", "honor",
            }
            # Also catch partial matches (wiki descriptions can be verbose)
            _GENERIC_WIKI_DESC_KEYWORDS = {
                "newspaper", "publication", "tabloid", "magazine",
                "front page", "news agency", "media company",
            }
            if wiki_desc in _GENERIC_WIKI_DESCRIPTIONS:
                print(f"    ⊘ Skipping Wikipedia image for '{subject}' — generic concept: '{wiki_desc}'")
                return None
            if any(kw in wiki_desc for kw in _GENERIC_WIKI_DESC_KEYWORDS):
                print(f"    ⊘ Skipping Wikipedia image for '{subject}' — publication/media: '{wiki_desc}'")
                return None

            # Reject images whose URL contains known-bad patterns
            # (newspaper scans, album covers, generic event logos)
            _BAD_IMAGE_URL_PATTERNS = [
                "front_page", "newspaper", "album_cover", "logo",
                "Kitzbuehel_slalom", "Indian_Express",
            ]
            if any(pat.lower() in img.lower() for pat in _BAD_IMAGE_URL_PATTERNS):
                print(f"    ⊘ Skipping Wikipedia image for '{subject}' — bad image URL pattern")
                return None

            # If article context is provided, check the Wikipedia page shares
            # at least one distinctive keyword with the article
            if article_context:
                context_lower = article_context.lower()
                wiki_extract = (data.get("extract") or "").lower()
                # Extract distinctive words from wiki page (skip short/common words)
                _COMMON = {"the", "of", "in", "and", "for", "a", "an", "is", "at",
                           "on", "to", "with", "by", "from", "as", "it", "that",
                           "this", "or", "was", "were", "are", "be", "been", "has",
                           "had", "have", "not", "but", "its", "which", "who",
                           "their", "can", "will", "may", "more", "also", "than",
                           "about", "such", "other", "into", "some", "these",
                           "world", "international", "first", "one", "two",
                           "new", "most", "all", "any", "many", "each", "event",
                           "competition", "championship", "champion", "title"}
                subject_words = {w.lower() for w in subject.split() if len(w) > 2}
                wiki_words = {w for w in re.findall(r'\b[a-z]{4,}\b', wiki_extract[:500])
                              if w not in _COMMON and w not in subject_words}
                context_words = {w for w in re.findall(r'\b[a-z]{4,}\b', context_lower[:1000])
                                 if w not in _COMMON and w not in subject_words}
                overlap = wiki_words & context_words
                if not overlap:
                    print(f"    ⊘ Skipping Wikipedia image for '{subject}' — page topic "
                          f"('{data.get('description', '')[:50]}') has no keyword overlap with article")
                    return None

                # Landmark/geographic guard: if Wikipedia describes this as a
                # physical place (monument, tower, building, shipyard, etc.),
                # require the entity's FULL NAME to appear in the article text.
                # Geographic-only keyword overlap (city/country names) is not
                # enough — "Gateway of India" shouldn't illustrate an Air India
                # article just because both mention "Mumbai".
                _PLACE_DESC_KEYWORDS = {
                    "monument", "landmark", "tower", "gate", "fort", "palace",
                    "temple", "mosque", "church", "cathedral", "mausoleum",
                    "bridge", "dam", "statue", "memorial", "building",
                    "skyscraper", "shipyard", "factory", "port", "airport",
                    "stadium", "arena", "park", "garden", "museum", "library",
                    "observatory", "pier", "lighthouse", "arch", "obelisk",
                    "stupa", "pagoda", "citadel", "fortress", "tomb",
                    "residence", "house", "mansion", "hall", "complex",
                    "city", "town", "village", "district", "municipality",
                }
                if any(kw in wiki_desc for kw in _PLACE_DESC_KEYWORDS):
                    subject_lower = subject.lower()
                    if subject_lower not in context_lower:
                        print(f"    ⊘ Skipping Wikipedia image for '{subject}' — "
                              f"landmark/place ('{wiki_desc[:50]}') not mentioned by name in article")
                        return None

            return img
    except:
        pass
    return None


def extract_main_subject(headline):
    """Extract the primary subject (person/show/movie) from a headline."""
    # Common patterns: "Name Has/Is/Just/Was..." or "Name's..."
    patterns = [
        r"^(.+?)\s+(?:Has|Is|Was|Will|Just|Opens|Returns|Launches|Endorsed|Premiered|Plays|Crosses|Delivers|Confessed|Blocks|Acquired|Revealed)",
        r"^(.+?)'s\s",
        r"^(.+?)\s+(?:—|–|-)\s",
    ]
    for pat in patterns:
        m = re.match(pat, headline)
        if m:
            subject = m.group(1).strip()
            # Filter out generic openers
            if len(subject) > 3 and subject not in {"The", "This", "What", "How", "Why", "Nine", "Four"}:
                return subject
    return None


def is_relevant_image(result, subject, headline):
    """Check if an image result is actually relevant to the article.

    Hardened (2026-06-23): a 2-word headline overlap is NOT enough when both
    words are generic geo/common tokens — that's how "America" matched a
    Miss-America pageant photo and a Gandalf meme landed on a visa story. The
    overlap must include at least one DISTINCTIVE (non-generic) word, the same
    distinctive-entity floor used in the tweet enricher.
    """
    title = (result.get("title", "") or "").lower()
    headline_lower = headline.lower()
    subject_lower = (subject or "").lower()

    # Skip obvious junk: book scans, documents, SVGs, logos, internet memes
    junk_patterns = [".djvu", "notes and queries", "volume ", "series ", "hitty",
                     "meme", "use the force", "harry", "gandalf",
                     "pageant", "miss america", "mrs. america", "mrs america"]
    if any(j in title for j in junk_patterns):
        return False

    # For named subjects, check if result title contains any part of the subject
    parts = [p for p in subject_lower.split() if len(p) > 2] if subject_lower else []
    if parts and any(p in title for p in parts):
        return True

    # Check headline keyword overlap — but require a DISTINCTIVE word in it.
    headline_words = {w.lower() for w in headline.split() if len(w) > 3}
    title_words = {w.lower() for w in title.split() if len(w) > 3}
    overlap = headline_words & title_words
    distinctive_overlap = {w for w in overlap if w not in _GENERIC_TOKENS}
    # Need >=2 total overlapping words AND at least one of them distinctive.
    if len(overlap) >= 2 and distinctive_overlap:
        return True

    # If it's from wikimedia/flickr and has a reasonable title, accept with lower bar
    source = result.get("source", "")
    if source in ("wikimedia", "flickr") and len(title) > 10:
        if any(p in title for p in parts[:1]):
            return True

    return False


def find_better_image(headline, current_url):
    """Find a better CC image for an article."""
    subject = extract_main_subject(headline)

    # Try YouTube thumbnail first for named subjects — specific, recent photos
    if subject and len(subject) > 2:
        try:
            from image_sourcer import fetch_youtube_thumbnail
            yt_thumb, yt_title, yt_channel = fetch_youtube_thumbnail(subject, headline)
            if yt_thumb:
                print(f"    ✓ YouTube thumbnail for '{subject}' → \"{yt_title[:50]}\"")
                return yt_thumb, f"YouTube / {yt_channel}" if yt_channel else "YouTube"
        except Exception as e:
            print(f"    ⚠ YouTube thumbnail lookup failed: {e}")

    # Try Wikipedia for named subjects (skip logos/PNGs)
    if subject:
        wiki_img = fetch_wikipedia_image(subject, article_context=headline)
        if wiki_img and "wikimedia" in wiki_img and not wiki_img.endswith(".png"):
            print(f"    ✓ Wikipedia image for '{subject}'")
            return wiki_img, f"Wikimedia Commons / Wikipedia (CC)"

    # Try Openverse
    query = subject or headline[:60]
    openverse = search_openverse(query, limit=8)
    # Filter for relevance
    relevant = [r for r in openverse if is_relevant_image(r, subject, headline)]
    if relevant:
        # Prefer larger, landscape images
        best = sorted(relevant, key=lambda x: x["width"] * x["height"], reverse=True)[0]
        print(f"    ✓ Openverse: {best['title'][:50]} ({best['width']}x{best['height']}) [{best['license']}]")
        credit = f"{best.get('creator', 'Unknown')} via {best['source']} ({best['license'].upper()})"
        return best["url"], credit

    # Try Wikimedia Commons
    commons = search_wikimedia_commons(query, limit=8)
    relevant = [r for r in commons if is_relevant_image(r, subject, headline)]
    if relevant:
        best = sorted(relevant, key=lambda x: x["width"] * x["height"], reverse=True)[0]
        print(f"    ✓ Commons: {best['title'][:50]} ({best['width']}x{best['height']})")
        return best["url"], "Wikimedia Commons (CC)"

    return None, None


# ═══════════════════════════════════════════
# SOCIAL EMBED ENRICHMENT — Instagram + X
# ═══════════════════════════════════════════

def load_registry():
    """Load social embed registry from Supabase."""
    sys.path.insert(0, PIPELINE_DIR)
    from social_registry import load_registry as _lr
    return _lr()


def find_matching_handles(headline, registry, platform="instagram"):
    """Find registry handles that match an article headline.
    
    Strict matching: multi-word names require ALL significant words in headline.
    Single-word residuals from stopword filtering are rejected if generic.
    """
    matches = []
    headline_lower = headline.lower()

    # Stopwords to filter from entity names
    stopwords = {"the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to",
                 "india", "indian", "world", "national", "new", "south", "west",
                 "east", "north", "global", "daily", "times", "news", "media"}

    # Generic residual words — too common to match alone after stopword filtering
    GENERIC_RESIDUALS = {
        "abroad", "open", "today", "live", "express", "online", "post",
        "standard", "first", "star", "free", "press", "report", "watch",
        "inside", "real", "forward", "point", "review", "show", "talk",
        "take", "view", "voice", "wire", "print", "beat", "pulse", "buzz",
        "hour", "minute", "central", "morning", "evening", "night",
        "weekly", "monthly", "herald", "mirror", "gazette", "monitor",
        "chronicle", "dispatch", "journal", "tribune", "sentinel",
        "games", "sports", "tech", "film", "food", "travel", "health",
        "money", "market", "trade", "business", "finance",
    }

    for category, data in registry.items():
        if category.startswith("_"):
            continue
        if not isinstance(data, dict):
            continue

        for group_key in ["persons", "organizations"]:
            entries = data.get(group_key, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                name = entry.get("name", "")
                handle = entry.get(platform, entry.get(f"{platform}_handle", ""))
                if not handle:
                    continue

                # Check if name appears in headline
                name_parts = name.lower().split()
                original_word_count = len([p for p in name_parts if len(p) > 2])
                significant = [p for p in name_parts if p not in stopwords and len(p) > 2]
                if not significant:
                    continue

                # Reject single generic residuals from multi-word names
                if len(significant) == 1 and original_word_count > 1:
                    if significant[0] in GENERIC_RESIDUALS:
                        continue

                import re as _re_match
                if all(_re_match.search(r'\b' + _re_match.escape(word) + r'\b', headline_lower) for word in significant):
                    matches.append({
                        "name": name,
                        "handle": handle,
                        "category": category,
                        "platform": platform,
                    })

    return matches


def search_instagram_posts(handle, topic_keywords, limit=3):
    """Fetch recent posts from an IG handle via Apify and match to topic keywords.

    Returns list of shortcodes that are relevant to the topic keywords.
    Uses a module-level cache (_ig_post_cache) so each handle is fetched only once per run.
    """
    global _ig_post_cache
    if not hasattr(search_instagram_posts, '_cache'):
        search_instagram_posts._cache = {}

    cache = search_instagram_posts._cache
    handle_lower = handle.lower()

    # Fetch posts if not cached
    if handle_lower not in cache:
        posts = _fetch_ig_posts_apify([handle_lower])
        cache[handle_lower] = posts.get(handle_lower, [])

    posts = cache.get(handle_lower, [])
    if not posts:
        return []

    # Match posts to topic keywords
    keywords = [w.lower().strip('.,!?:;-') for w in topic_keywords if len(w) > 2]
    if not keywords:
        return []

    scored = []
    # Words too generic to count as topic matches in IG captions
    GENERIC_CAPTION_WORDS = {
        "post", "new", "love", "like", "just", "today", "link", "bio",
        "comment", "share", "follow", "check", "watch", "live", "story",
        "come", "back", "best", "look", "make", "take", "about", "more",
        "over", "real", "show", "time", "good", "join", "open", "here",
        "know", "last", "next", "been", "stay", "feel", "made", "keep",
    }
    # Filter keywords to remove generic ones
    strong_keywords = [kw for kw in keywords
                       if kw.lower().strip('.,!?:;-') not in GENERIC_CAPTION_WORDS
                       and len(kw) > 3]

    for post in posts:
        caption = (post.get('caption', '') or '').lower()
        if not caption:
            continue
        # Count hits using ONLY strong (non-generic) keywords
        hits = sum(1 for kw in strong_keywords if kw.lower().strip('.,!?:;-') in caption)
        # Require at least 2 strong keyword hits, or 1 if very few strong keywords
        if hits >= 2 or (hits >= 1 and len(strong_keywords) <= 2 and len(strong_keywords) > 0):
            shortcode = post.get('shortCode', '')
            if shortcode:
                scored.append((hits, shortcode))

    scored.sort(key=lambda x: -x[0])
    return [sc for _, sc in scored[:limit]]


def _fetch_ig_posts_apify(handles, results_limit=12):
    """Batch-fetch recent posts from multiple IG handles via Apify.

    Returns dict: {handle_lower: [post_dict, ...]}
    """
    token = os.environ.get('APIFY_API_TOKEN', '')
    if not token:
        print("     ⚠ APIFY_API_TOKEN not set, skipping IG enrichment")
        return {}

    payload = json.dumps({
        'username': handles,
        'resultsLimit': results_limit,
    })

    try:
        result = subprocess.run(
            ['curl', '-sS', '-X', 'POST',
             f'https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset-items?token={token}',
             '-H', 'Content-Type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            print(f"     ⚠ Apify curl failed: {result.stderr[:200]}")
            return {}
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"     ⚠ Apify call failed: {e}")
        return {}

    by_handle = {}
    for item in data:
        owner = (item.get('ownerUsername') or '').lower()
        if not owner:
            # Try to infer from inputUrl
            input_url = item.get('inputUrl', '')
            m = re.search(r'instagram\.com/([^/]+)', input_url)
            owner = m.group(1).lower() if m else ''
        if owner:
            by_handle.setdefault(owner, []).append(item)

    return by_handle


def prefetch_ig_posts(handles):
    """Pre-fetch posts for multiple handles in one batch call. Populates the cache."""
    if not handles:
        return
    if not hasattr(search_instagram_posts, '_cache'):
        search_instagram_posts._cache = {}
    cache = search_instagram_posts._cache

    # Only fetch handles not already cached
    to_fetch = [h.lower() for h in handles if h.lower() not in cache]
    if not to_fetch:
        return

    # Batch in groups of 10 to avoid timeout
    BATCH_SIZE = 10
    for i in range(0, len(to_fetch), BATCH_SIZE):
        batch = to_fetch[i:i + BATCH_SIZE]
        print(f"     Fetching IG posts for {len(batch)} handles via Apify...")
        results = _fetch_ig_posts_apify(batch)
        for h in batch:
            cache[h] = results.get(h, [])
        if i + BATCH_SIZE < len(to_fetch):
            time.sleep(2)  # brief pause between batches


def article_has_social_embed(body, platform):
    """Check if article body already has a social embed."""
    if platform == "instagram":
        return bool(re.search(r'instagram\.com/(?:p|reel|tv)/', body or ""))
    elif platform in ("twitter", "x"):
        return bool(re.search(r'(?:twitter|x)\.com/\w+/status/', body or ""))
    elif platform == "youtube":
        return bool(re.search(r'<youtube>.*?</youtube>', body or ""))
    return False


def verify_ig_embeds(body):
    """Verify Instagram embed URLs in article body are real (not hallucinated).

    Checks each IG /p/, /reel/, /tv/ URL by fetching the embed page and
    looking for Instagram's "may be broken" / "post may have been removed"
    markers. Returns (cleaned_body, removed_count).

    Writer LLMs fabricate /reel/ shortcode URLs that look valid but point to
    nothing. IG returns HTTP 200 for all embed pages (even broken ones), so
    we must inspect the HTML body for removal markers.
    """
    ig_pattern = re.compile(
        r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)/?[^\s]*'
    )
    matches = list(ig_pattern.finditer(body))
    if not matches:
        return body, 0

    removed = 0
    for m in matches:
        shortcode = m.group(1)
        full_url = m.group(0)
        try:
            r = subprocess.run(
                ["curl", "-s", "--connect-timeout", "5", "--max-time", "10",
                 "-A", "Mozilla/5.0",
                 f"https://www.instagram.com/p/{shortcode}/embed/"],
                capture_output=True, text=True, timeout=15
            )
            html = (r.stdout or "").lower()
            is_broken = (
                "may be broken" in html
                or "post may have been removed" in html
                or "embedisbroken" in html.replace(" ", "")
            )
            # Tiny page with no embed scaffold = also broken
            if not is_broken and len(r.stdout or "") < 2000 and 'class="Embed' not in (r.stdout or ""):
                is_broken = True

            if is_broken:
                print(f"     💀 Fake/dead IG embed: {full_url[:60]} — stripping")
                # Remove the URL line and surrounding blank lines
                body = re.sub(r'\n?\n?' + re.escape(full_url) + r'\n?\n?', '\n\n', body)
                removed += 1
            else:
                print(f"     ✅ IG embed verified: {full_url[:60]}")
        except Exception as e:
            print(f"     ⚠️  Could not verify IG {shortcode}: {e}")

    if removed:
        body = re.sub(r'\n{3,}', '\n\n', body)
    return body, removed


# ═══════════════════════════════════════════
# INLINE IMAGE ENRICHMENT — Wikipedia entities
# ═══════════════════════════════════════════

# Named entities that should NOT get inline images (too generic or noise)
_SKIP_ENTITIES = {
    "india", "us", "usa", "america", "united states", "uk", "china", "world",
    "government", "court", "congress", "parliament", "supreme court",
    "the", "this", "what", "how", "why", "new", "breaking", "report",
}

# Minimum word count for an article to get inline images
_MIN_WORDS_FOR_INLINE = 200


# Pronouns, verbs, and quantity words that must NOT appear in a "named entity".
# News headlines are title-cased (every word capitalized), so the proper-noun
# regex otherwise treats ordinary phrases like "Trap Them" or "Three Tankers"
# as names and fetches a wrong Wikipedia image (e.g. the band "Trap Them").
_ENTITY_BANNED_WORDS = {
    'they','them','their','it','its','this','that','these','those','he','she',
    'we','you','us','his','her','him','my','our','your',
    'tried','got','get','told','made','make','makes','tries','trying','keeps',
    'kept','finally','out','again','now','then','here','there','just','still',
    'three','four','five','six','seven','eight','nine','ten','two','one',
    'who','what','when','where','why','how','a','an','and','but','or','so',
    'tankers','sailors','crew','strait',  # generic nouns from this story class
}
_ENTITY_CONNECTORS = {'of','the','and','de','van','von','al','el','bin','da','del','la'}


def _entity_confirmed_in_body(name, body):
    """True only if `name` appears capitalized MID-sentence in the body.
    Body prose is sentence-cased (unlike the title-cased headline), so a word
    capitalized in the middle of a sentence is a genuine proper noun. This
    filters out title-case artifacts that are not real names."""
    for m in re.finditer(re.escape(name), body or ""):
        j = m.start() - 1
        while j >= 0 and body[j] in ' \t':
            j -= 1
        if j < 0:
            continue  # start of body — capitalization not meaningful
        if body[j] in '.!?\n>*#-':  # sentence/heading start — not meaningful
            continue
        return True
    return False


def _is_safe_entity(name, body):
    """Guard before fetching a Wikipedia image for a headline-derived entity.
    Rejects pronoun/verb/quantity phrases and anything not confirmed as a real
    proper noun in the body. Protects the person/identity-match rule."""
    words = [w.lower() for w in name.split()]
    if any(w in _ENTITY_BANNED_WORDS for w in words):
        return False
    distinctive = [w for w in words if w not in _ENTITY_CONNECTORS]
    if not distinctive:
        return False
    return _entity_confirmed_in_body(name, body)


def extract_entities(headline, body):
    """Extract notable entities (people, places, orgs) from headline + first few paragraphs.
    Returns a list of entity names, most important first."""
    # Work line-by-line to avoid matching across paragraphs
    paras = (headline + "\n\n" + "\n\n".join(body.split("\n\n")[:4])).split("\n")
    text_lines = [l.strip() for l in paras if l.strip()]

    entities = []
    seen = set()

    # Common English words and verbs to strip from matches
    _STRIP_TRAILING = {
        "confirms", "unveils", "launches", "announces", "reveals", "says", "joins",
        "signs", "wins", "loses", "beats", "enters", "leaves", "faces", "leads",
        "hits", "crosses", "blocks", "delivers", "opens", "returns", "plays",
        "backs", "calls", "cuts", "drops", "eyes", "fires", "gets", "gives",
        "grabs", "hails", "inks", "kicks", "lifts", "makes", "moves", "names",
        "picks", "pulls", "pushes", "puts", "raises", "runs", "sees", "sets",
        "shows", "slams", "sparks", "takes", "talks", "targets", "tells",
        "tests", "tops", "turns", "urges", "wants", "warns",
        "film", "movie", "show", "series", "game", "match", "deal", "plan",
        "new", "big", "top", "first", "next", "last", "old",
        "annual", "press", "developer", "conference", "summit", "forum",
        "report", "study", "survey", "review", "update", "statement",
    }

    for line in text_lines:
        # Pattern: Capitalized multi-word names (2-4 words)
        for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+(?:(?:de|von|van|al|el|bin|the|of)\s+)?[A-Z][a-z]+){1,3})\b', line):
            name = m.group(1).strip()
            # Strip trailing common words/verbs
            words = name.split()
            while len(words) > 1 and words[-1].lower() in _STRIP_TRAILING:
                words.pop()
            # Strip leading filler words
            _STRIP_LEADING = {"new", "big", "top", "first", "last", "old", "annual", "latest", "recent", "former", "current"}
            while len(words) > 1 and words[0].lower() in _STRIP_LEADING:
                words.pop(0)
            # If a verb appears in the middle, split and take the longer part
            _VERBS_MID = {"confirms", "unveils", "launches", "announces", "reveals", "says",
                         "joins", "wins", "loses", "beats", "faces", "leads", "enters",
                         "backs", "calls", "gets", "makes", "shows", "takes", "tells",
                         "warns", "opens", "returns", "plays", "hits", "fires", "drops"}
            for vi in range(1, len(words) - 1):
                if words[vi].lower() in _VERBS_MID:
                    left = words[:vi]
                    right = words[vi+1:]
                    words = left if len(left) >= len(right) else right
                    break
            name = " ".join(words)

            if name.lower() in _SKIP_ENTITIES or len(name) < 4 or len(name.split()) < 2:
                continue
            # Guard: reject title-case artifacts (pronouns/verbs/quantities) and
            # require the name to be a genuine proper noun confirmed in the body.
            if not _is_safe_entity(name, body):
                continue
            key = name.lower()
            if key not in seen:
                seen.add(key)
                entities.append(name)

    # Pattern 2: Known place patterns (single-word places that are notable)
    full_text = "\n".join(text_lines)
    for m in re.finditer(r'\b(New Delhi|Washington D\.?C\.?|Silicon Valley|Wall Street|Bollywood|Hollywood|Mumbai|Chennai|Hyderabad|Bangalore|Bengaluru)\b', full_text, re.IGNORECASE):
        name = m.group(1).strip()
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(name)

    return entities[:6]  # limit to top 6 candidates


def _wikimedia_filename(url):
    """Extract the Wikimedia filename portion from a URL, lowercased.
    E.g. 'upload.wikimedia.org/.../File:Nikesh_Arora.jpg' → 'nikesh_arora.jpg'"""
    from urllib.parse import unquote
    path = unquote(url.split("?")[0])
    fname = path.rsplit("/", 1)[-1].lower()
    # Strip common prefixes like 'thumb/' residual or size suffixes
    # e.g. '800px-nikesh_arora.jpg' → 'nikesh_arora.jpg'
    fname = re.sub(r'^\d+px-', '', fname)
    return fname


# ── Visual-category subject extraction (food, travel, entertainment, lifestyle) ──
_VISUAL_CATEGORIES = {"food", "travel", "entertainment", "lifestyle-health"}


def extract_visual_subjects(headline, body, category):
    """Use GPT-4o-mini to extract 3-5 specific visual subjects from a
    food/travel/entertainment/lifestyle article — places, landmarks, dishes,
    restaurants, or venues that would benefit from a photo.

    Returns a list of subject name strings, most photogenic first.
    Falls back to an empty list on any error (caller will use regex extractor).
    """
    # Strip HTML and truncate body to keep prompt cheap
    body_text = re.sub(r'<[^>]+>', ' ', body)
    body_text = re.sub(r'\s+', ' ', body_text).strip()[:1200]

    prompt_system = (
        "You extract specific named visual subjects from articles for photo illustration. "
        "Return ONLY a JSON array of 3-5 strings. Each string must be a specific "
        "proper name of a well-known place, landmark, monument, palace, fort, temple, "
        "national park, heritage site, famous dish, or iconic venue that is likely to "
        "have a Wikipedia page with a good photo. "
        "IMPORTANT: Only include subjects that the article is specifically ABOUT or discusses in detail. "
        "Do NOT include famous city landmarks (e.g., Gateway of India, Eiffel Tower, CN Tower, "
        "Taj Mahal, Statue of Liberty) just because the article mentions that city. "
        "If the article is about an airline route to Toronto, do NOT include CN Tower. "
        "If the article is about a business in Mumbai, do NOT include Gateway of India. "
        "Prioritize the actual subjects of the story over geographic decoration. "
        "Be specific: 'Amer Fort' not 'a fort in Rajasthan', 'Falaknuma Palace' not 'palace in Hyderabad'. "
        "Omit generic terms, people's names, countries, cities, and restaurant brand names that are unlikely to have Wikipedia photos."
    )
    prompt_user = f"Category: {category}\nHeadline: {headline}\n\nArticle excerpt:\n{body_text}"

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        print("    ⚠ No OPENAI_API_KEY — skipping visual subject extraction")
        return []

    try:
        import subprocess as _sp
        payload = json.dumps({
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user},
            ],
            "temperature": 0.2,
            "max_tokens": 200,
        })
        result = _sp.run(
            ["curl", "-s", "-X", "POST", "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {openai_key}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"    ⚠ GPT curl failed: {result.stderr[:100]}")
            return []

        resp = json.loads(result.stdout)
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Parse JSON array from response (may be wrapped in ```json ... ```)
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
        subjects = json.loads(content)
        if isinstance(subjects, list):
            subjects = [s for s in subjects if isinstance(s, str) and len(s) > 2]
            print(f"    🎨 Visual subjects ({category}): {subjects}")
            return subjects[:6]
    except Exception as e:
        print(f"    ⚠ Visual subject extraction error: {e}")

    return []


def find_inline_images(headline, body, hero_url="", category=None):
    """Find inline Wikipedia images for entities in the article.
    Returns list of (entity, image_url, caption) tuples.

    For visual categories (food, travel, entertainment, lifestyle-health),
    uses GPT to extract specific places/landmarks/venues. For other categories,
    uses the regex-based entity extractor. Visual categories get up to 3 images;
    others get up to 2.
    """
    # Choose entity source based on category
    if category and category in _VISUAL_CATEGORIES:
        entities = extract_visual_subjects(headline, body, category)
        if not entities:
            # Fallback to regex extractor
            entities = extract_entities(headline, body)
        max_images = 3
    else:
        entities = extract_entities(headline, body)
        max_images = 2
    results = []
    hero_norm = (hero_url or "").split("?")[0].lower()
    # Extract hero filename for cross-host comparison (Supabase vs Wikimedia)
    hero_fname = _wikimedia_filename(hero_url) if hero_url else ""
    # Build a slugified version of hero URL path for entity-name matching
    hero_slug = re.sub(r'[^a-z0-9]', '', hero_norm)

    # Strip HTML for sentence extraction
    body_text = re.sub(r'<[^>]+>', ' ', body)
    body_text = re.sub(r'\s+', ' ', body_text).strip()

    for entity in entities:
        if len(results) >= max_images:
            break

        img_url = fetch_wikipedia_image(entity, article_context=headline + " " + body_text[:500])

        # For visual categories, fall back to Wikimedia Commons search if
        # Wikipedia page summary has no image (e.g. lesser-known venues)
        if not img_url and category and category in _VISUAL_CATEGORIES:
            commons = search_wikimedia_commons(entity, limit=5)
            entity_lower = entity.lower()
            entity_words = [w.lower() for w in entity.split() if len(w) > 2]
            for c in commons:
                title = (c.get("title") or "").lower()
                # Require at least 2 entity words in the title, or the full
                # entity name, to avoid false matches like "Adaa Khan" for "Adaa"
                matching_words = sum(1 for w in entity_words if w in title)
                full_match = entity_lower in title
                if full_match or (len(entity_words) > 1 and matching_words >= 2) or (len(entity_words) == 1 and matching_words == 1 and len(entity_lower) >= 5):
                    # Extra guard: reject obvious person photos (portrait, award, headshot)
                    _person_hints = {"award", "portrait", "headshot", "actor", "actress", "khan,", "singer", "politician"}
                    if any(h in title for h in _person_hints):
                        continue
                    img_url = c.get("url")
                    print(f"    📷 Commons fallback for '{entity}': {title[:60]}")
                    break

        if not img_url:
            continue

        # Skip if same as hero image (exact URL match)
        if hero_norm and img_url.split("?")[0].lower() == hero_norm:
            continue

        # Skip if Wikimedia filename matches hero filename (cross-host dedup)
        candidate_fname = _wikimedia_filename(img_url)
        if hero_fname and candidate_fname and candidate_fname == hero_fname:
            print(f"    ⊘ Skipping inline for '{entity}' — same image file as hero")
            continue

        # Skip if entity name appears in the hero URL slug (hero was sourced
        # from Wikipedia for this same person, then re-uploaded to Supabase
        # with the entity name in the storage path)
        entity_slug = re.sub(r'[^a-z0-9]', '', entity.lower())
        if hero_slug and len(entity_slug) >= 6 and entity_slug in hero_slug:
            print(f"    ⊘ Skipping inline for '{entity}' — entity name found in hero URL")
            continue

        # Skip SVGs and tiny images
        if img_url.endswith(".svg") or img_url.endswith(".png"):
            continue

        # Build two-sentence caption: what image shows + article context
        # Extract a body sentence mentioning the entity for context
        sentences = re.split(r'(?<=[.!?])\s+', body_text)
        context = ""
        entity_lower = entity.lower()
        for s in sentences:
            if entity_lower in s.lower() and 20 < len(s) < 250:
                context = s.strip()
                break
        if context:
            caption = f"{entity}. {context}"
        else:
            caption = f"{entity}. Photo: Wikimedia Commons"
        results.append((entity, img_url, caption))
        print(f"    ✓ Inline image for '{entity}'")

    return results


def _is_html_body(body):
    """Check if article body is HTML (starts with HTML block tags)."""
    return bool(re.match(r'^\s*<(?:p|h[1-6]|div|section|article)\b', body, re.IGNORECASE))


def _count_media_elements(text):
    """Count media elements in a chunk of HTML (figures, embeds, YouTube tags)."""
    pats = [r'<figure[^>]*>', r'<youtube>', r'<blockquote[^>]*class="pull-quote"',
            r'https?://(?:x|twitter)\.com/\w+/status/',
            r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/']
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in pats)


def insert_inline_images(body, images, max_cap=2):
    """Insert inline images distributed across article sections.

    Uses H2 sections to spread images out — one per section max, placed in
    sections that have the fewest existing media elements. Caps at max_cap
    inline images per article (default 2, visual categories pass 3).
    """
    if not images:
        return body

    is_html = _is_html_body(body)

    # Cap at max_cap inline images per article
    images = images[:max_cap]

    # Split body into sections by <h2> tags
    h2_splits = list(re.finditer(r'<h2[^>]*>', body, re.IGNORECASE))

    if not h2_splits:
        # No H2s — fall back to old paragraph-spacing logic
        paragraphs = body.split("\n\n")
        if len(paragraphs) < 3:
            return body
        step = max(2, (len(paragraphs) - 1) // (len(images) + 1))
        for i in range(len(images) - 1, -1, -1):
            entity, url, caption = images[i]
            idx = min(step * (i + 1), len(paragraphs) - 1)
            if is_html:
                cap_escaped = caption.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
                img_md = f'\n<figure style="margin:28px auto;text-align:center"><img src="{url}" alt="{cap_escaped}" style="max-width:100%;border-radius:8px" loading="lazy"><figcaption style="font-size:0.85rem;color:#666;margin-top:8px">{caption}</figcaption></figure>\n'
            else:
                img_md = f"\n![{caption}]({url})\n"
            paragraphs.insert(idx, img_md)
        return "\n\n".join(paragraphs)

    # Build sections: (start, end) boundaries
    sections = []
    # Intro before first H2 — skip for image placement (usually key-takeaways)
    for i, m in enumerate(h2_splits):
        s = m.start()
        e = h2_splits[i + 1].start() if i + 1 < len(h2_splits) else len(body)
        sections.append((s, e))

    # Score sections by media count and pick the emptiest ones
    scored = []
    for idx, (s, e) in enumerate(sections):
        mc = _count_media_elements(body[s:e])
        scored.append((mc, idx))
    scored.sort()  # fewest media first

    # Assign each image to a different section (fewest-media-first)
    result = body
    offset = 0  # track offset from prior insertions
    for img_i, (entity, url, caption) in enumerate(images):
        if img_i >= len(scored):
            break
        _, sec_idx = scored[img_i]
        s, e = sections[sec_idx]
        s += offset
        e += offset
        section_text = result[s:e]

        # Find </p> tags in this section — insert after the last one
        p_ends = [m.end() for m in re.finditer(r'</p>', section_text, re.IGNORECASE)]
        if not p_ends:
            continue  # no paragraph to insert after

        # Prefer inserting after the last </p> in the section (before next H2)
        insert_rel = p_ends[-1] if len(p_ends) > 1 else p_ends[0]
        insert_pos = s + insert_rel

        if is_html:
            cap_escaped = caption.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
            img_md = f'\n\n<figure style="margin:28px auto;text-align:center"><img src="{url}" alt="{cap_escaped}" style="max-width:100%;border-radius:8px" loading="lazy"><figcaption style="font-size:0.85rem;color:#666;margin-top:8px">{caption}</figcaption></figure>\n'
        else:
            img_md = f"\n\n![{caption}]({url})\n"

        result = result[:insert_pos] + img_md + result[insert_pos:]
        offset += len(img_md)

    return result


# ═══════════════════════════════════════════
# PULL QUOTE ENRICHMENT
# ═══════════════════════════════════════════

def extract_pull_quote(body):
    """Find the most impactful sentence for a pull quote.
    Prefers sentences with quotes, strong language, or statistics."""
    # Strip HTML tags for sentence analysis
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text).strip()
    # Split into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) < 5:
        return None

    scored = []
    for i, sent in enumerate(sentences):
        if len(sent) < 40 or len(sent) > 200:
            continue
        # Skip if it's the first sentence (already visible)
        if i == 0:
            continue
        # Skip if it's already a quote block or image
        if sent.startswith(">") or sent.startswith("!["):
            continue
        # Skip sentence fragments — must end with proper punctuation
        if not re.search(r'[.!?"\u201d]$', sent.strip()):
            continue
        # Skip sentences that look truncated (end mid-word or with abbreviation)
        if re.search(r'\b[A-Z][a-z]?\."?$', sent.strip()):
            # Ends like "Dr." or "Mr." — likely truncated
            continue

        score = 0
        # Prefer actual quoted speech
        if '"' in sent or '\u201c' in sent:
            score += 5
        # Prefer sentences with numbers/stats
        if re.search(r'\d+[%$]|\$\d|billion|million|crore|lakh', sent, re.IGNORECASE):
            score += 3
        # Prefer strong language
        strong_words = ["historic", "unprecedented", "first-ever", "record", "landmark",
                       "stunning", "massive", "crucial", "breakthrough", "revolutionary",
                       "shocking", "dramatic", "critical"]
        if any(w in sent.lower() for w in strong_words):
            score += 2
        # Prefer mid-article sentences (not too early, not too late)
        relative_pos = i / max(len(sentences), 1)
        if 0.2 < relative_pos < 0.6:
            score += 1

        if score > 0:
            scored.append((score, i, sent))

    if not scored:
        return None

    # Pick the highest-scoring sentence
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][2]


def insert_pull_quote(body, quote):
    """Insert a pull quote roughly 1/3 into the article."""
    if not quote:
        return body

    paragraphs = body.split("\n\n")
    if len(paragraphs) < 4:
        return body

    # Place at ~1/3 point
    insert_at = max(2, len(paragraphs) // 3)

    if _is_html_body(body):
        quote_escaped = quote.strip().replace("&", "&amp;").replace("<", "&lt;")
        quote_block = f'\n\n<blockquote class="pull-quote"><p>"{quote_escaped}"</p></blockquote>\n'
    else:
        quote_block = f'\n\n> **"{quote.strip()}"**\n'
    paragraphs.insert(insert_at, quote_block)

    return "\n\n".join(paragraphs)


def article_has_inline_images(body):
    """Check if article body already has inline markdown or HTML images."""
    # Count actual inline images (not social embeds or tracking pixels)
    imgs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', body or "")
    if len(imgs) > 0:
        return True
    # Also check for HTML figure/img tags from enrichment
    html_imgs = re.findall(r'<figure[^>]*>.*?<img\s', body or "", re.DOTALL)
    return len(html_imgs) > 0


def article_has_pull_quote(body):
    """Check if article body already has a pull quote."""
    if not body:
        return False
    # Check for HTML blockquote pull quotes (current format)
    if '<blockquote class="pull-quote">' in body:
        return True
    # Check for legacy markdown-style pull quotes
    if re.search(r'>\s*\*\*["\u201c]', body):
        return True
    return False


# ═══════════════════════════════════════════
# YOUTUBE EMBED ENRICHMENT
# ═══════════════════════════════════════════

_YT_ENV = None
def _load_yt_env():
    global _YT_ENV
    if _YT_ENV is None:
        yt_env = {}
        path = os.path.expanduser("~/workspace/.env.youtube")
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        yt_env[k.strip()] = v.strip()
        _YT_ENV = yt_env
    return _YT_ENV

_YT_ACCESS_TOKEN = None
_YT_TOKEN_EXPIRY = 0

def _get_youtube_access_token():
    """Get OAuth access token from refresh token, caching for ~50 min."""
    global _YT_ACCESS_TOKEN, _YT_TOKEN_EXPIRY
    import time as _t
    if _YT_ACCESS_TOKEN and _t.time() < _YT_TOKEN_EXPIRY:
        return _YT_ACCESS_TOKEN
    env = _load_yt_env()
    cid = env.get("YOUTUBE_CLIENT_ID", "")
    csec = env.get("YOUTUBE_CLIENT_SECRET", "")
    rtok = env.get("YOUTUBE_REFRESH_TOKEN", "")
    if not (cid and csec and rtok):
        print("  ⚠ YouTube OAuth credentials not found in .env.youtube")
        return None
    try:
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": cid,
            "client_secret": csec,
            "refresh_token": rtok,
            "grant_type": "refresh_token",
        }, timeout=10)
        data = r.json()
        _YT_ACCESS_TOKEN = data.get("access_token")
        _YT_TOKEN_EXPIRY = _t.time() + data.get("expires_in", 3600) - 120
        return _YT_ACCESS_TOKEN
    except Exception as e:
        print(f"  ⚠ YouTube token refresh failed: {e}")
        return None

_YT_QUOTA_USED = 0
_YT_QUOTA_LIMIT = 9500  # leave buffer under 10K daily limit

def search_youtube_data_api(query, max_results=5, published_after_days=60):
    """Search YouTube Data API v3. Returns list of {videoId, title, channelTitle, publishedAt}."""
    global _YT_QUOTA_USED
    if _YT_QUOTA_USED >= _YT_QUOTA_LIMIT:
        print(f"  ⚠ YouTube quota near limit ({_YT_QUOTA_USED}/{_YT_QUOTA_LIMIT}), skipping")
        return []
    token = _get_youtube_access_token()
    if not token:
        return []
    from datetime import datetime, timedelta, timezone
    after = (datetime.now(timezone.utc) - timedelta(days=published_after_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": "relevance",
            "publishedAfter": after,
            "relevanceLanguage": "en",
        }, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        _YT_QUOTA_USED += 100  # search.list = 100 units
        if r.status_code != 200:
            print(f"  ⚠ YouTube API {r.status_code}: {r.text[:200]}")
            return []
        data = r.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"],
                "description": item["snippet"].get("description", ""),
            })
        return results
    except Exception as e:
        print(f"  ⚠ YouTube search error: {e}")
        return []

# Junk content indicators in YouTube titles
_YT_SKIP_TITLE_WORDS = {
    "compilation", "top 10", "top 5", "top 20", "meme", "memes", "funny",
    "prank", "reaction video", "fan edit", "whatsapp status",
    "#shorts", "tiktok", "roast", "exposed", "scam",
}

def _extract_yt_search_keywords(headline, entity_name):
    """Extract 2-4 keywords from headline, excluding the entity name and stopwords."""
    import re as _re
    clean = _re.sub(_re.escape(entity_name), "", headline, flags=_re.IGNORECASE).strip()
    clean = _re.sub(r"[^\w\s]", " ", clean)
    words = clean.lower().split()
    stopwords = {
        "the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to",
        "with", "by", "from", "as", "its", "it", "that", "this", "but", "or",
        "has", "had", "was", "were", "are", "be", "been", "being", "have",
        "his", "her", "he", "she", "they", "their", "we", "our", "you", "your",
        "about", "after", "before", "how", "why", "what", "when", "where", "who",
        "new", "says", "said", "could", "would", "will", "can", "may", "more",
        "into", "over", "up", "out", "just", "also", "than", "most", "first",
    }
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return keywords[:4]


def score_youtube_result(result, entity_name, keywords):
    """Score a YouTube search result for relevance. Higher = better."""
    title_lower = result["title"].lower()
    channel_lower = result["channelTitle"].lower()
    entity_lower = entity_name.lower()
    entity_parts = [p for p in entity_lower.split() if len(p) > 2]

    score = 0

    # Entity name in video title
    if entity_lower in title_lower:
        score += 4
    elif all(p in title_lower for p in entity_parts):
        score += 3

    # Entity name in channel name (official channel)
    if entity_lower in channel_lower:
        score += 3
    elif any(p in channel_lower for p in entity_parts if p not in {"the", "of", "in"}):
        score += 1

    # Keyword matches in title
    kw_hits = sum(1 for kw in keywords if kw in title_lower)
    score += kw_hits * 1.5

    # Penalty for junk content
    for skip_word in _YT_SKIP_TITLE_WORDS:
        if skip_word in title_lower:
            score -= 5

    # Penalty for non-English videos (Telugu, Hindi, Arabic, etc.)
    # Check for non-Latin script in title — strong signal of non-English content
    _NON_LATIN_RE = re.compile(r'[\u0900-\u097F\u0980-\u09FF\u0C00-\u0C7F\u0C80-\u0CFF\u0B80-\u0BFF'
                               r'\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0D00-\u0D7F'
                               r'\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF'
                               r'\uAC00-\uD7AF]')
    title_raw = result["title"]
    channel_raw = result["channelTitle"]
    non_latin_in_title = len(_NON_LATIN_RE.findall(title_raw))
    non_latin_in_channel = len(_NON_LATIN_RE.findall(channel_raw))
    if non_latin_in_title >= 3:
        score -= 10  # heavy penalty — title is in a non-English script
    elif non_latin_in_title >= 1:
        score -= 3
    if non_latin_in_channel >= 2:
        score -= 3  # channel name in non-English script

    # Bonus for news/official/interview content
    official_words = {"official", "press conference", "interview", "statement",
                      "announcement", "keynote", "launch", "podcast", "speech"}
    for ow in official_words:
        if ow in title_lower:
            score += 1
            break

    # Recency bonus
    try:
        from datetime import datetime, timezone
        pub = datetime.fromisoformat(result["publishedAt"].replace("Z", "+00:00"))
        days_old = (datetime.now(timezone.utc) - pub).days
        if days_old <= 3:
            score += 2
        elif days_old <= 7:
            score += 1
    except:
        pass

    return score


def find_matching_entities(headline, registry):
    """Find registry entity names that appear in an article headline (platform-agnostic)."""
    import re as _re
    matches = []
    headline_lower = headline.lower()

    for category, data in registry.items():
        if category.startswith("_") or not isinstance(data, dict):
            continue
        for group_key in ["persons", "organizations"]:
            entries = data.get(group_key, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                name = entry.get("name", "")
                name_parts = name.lower().split()
                stopwords = {"the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to"}
                significant = [p for p in name_parts if p not in stopwords and len(p) > 2]
                if not significant:
                    continue
                if all(_re.search(r'\b' + _re.escape(word) + r'\b', headline_lower) for word in significant):
                    matches.append({
                        "name": name,
                        "category": category,
                    })

    return matches


def _is_non_english_yt_title(title: str) -> bool:
    """Return True if >25% of alpha chars are non-Latin script (Telugu, Hindi, etc.)."""
    import unicodedata
    alpha_chars = [c for c in title if c.isalpha()]
    if len(alpha_chars) < 3:
        return False
    non_latin = sum(1 for c in alpha_chars if unicodedata.category(c).startswith('L') and ord(c) > 0x024F)
    return (non_latin / len(alpha_chars)) > 0.25


def _check_yt_video_language_api(video_ids: list) -> dict:
    """Check defaultAudioLanguage for a batch of video IDs via videos.list. Returns {id: lang_code}."""
    global _YT_QUOTA_USED
    if not video_ids or _YT_QUOTA_USED >= _YT_QUOTA_LIMIT:
        return {}
    token = _get_youtube_access_token()
    if not token:
        return {}
    try:
        r = subprocess.run(
            ["curl", "-sS",
             "https://www.googleapis.com/youtube/v3/videos",
             "-H", f"Authorization: Bearer {token}",
             "-G",
             "-d", "part=snippet",
             "-d", f"id={','.join(video_ids[:10])}"],
            capture_output=True, text=True, timeout=15,
        )
        _YT_QUOTA_USED += 1
        data = json.loads(r.stdout)
        result = {}
        for item in data.get("items", []):
            lang = item.get("snippet", {}).get("defaultAudioLanguage") or item.get("snippet", {}).get("defaultLanguage") or ""
            result[item["id"]] = lang.lower()
        return result
    except:
        return {}


def find_best_youtube_embed(entity_name, headline, max_results=5):
    """Search YouTube for a relevant video about entity_name in context of headline."""
    keywords = _extract_yt_search_keywords(headline, entity_name)
    query = f"{entity_name} {' '.join(keywords[:3])}"

    results = search_youtube_data_api(query, max_results=max_results, published_after_days=60)
    if not results:
        return None

    # ── English language filter ──
    # Step 1: Hard-reject non-Latin script titles
    results = [r for r in results if not _is_non_english_yt_title(r["title"])]
    if not results:
        return None

    # Step 2: Check audio language via API, drop confirmed non-English
    video_ids = [r["videoId"] for r in results]
    lang_map = _check_yt_video_language_api(video_ids)
    results = [r for r in results if not lang_map.get(r["videoId"], "").startswith(("hi", "te", "ta", "bn", "kn", "ml", "mr", "gu", "pa", "ur", "ar", "zh", "ja", "ko", "th"))]
    if not results:
        return None

    scored = []
    for r in results:
        s = score_youtube_result(r, entity_name, keywords)
        scored.append((s, r))

    scored.sort(key=lambda x: x[0], reverse=True)

    best_score, best = scored[0]
    if best_score < 3:
        return None

    url = f"https://youtube.com/watch?v={best['videoId']}"
    return {
        "url": url,
        "title": best["title"],
        "channel": best["channelTitle"],
        "score": best_score,
    }


# ═══════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════

def get_recent_articles(hours=24, category=None):
    """Fetch recent published articles."""
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    params = {
        "select": "id,headline,slug,category,image_url,image_caption,body,published_at,sources,topic_id",
        "status": "eq.published",
        "published_at": f"gte.{since}",
        "order": "published_at.desc",
        "limit": "100",
    }
    if category:
        params["category"] = f"eq.{category}"

    r = _session.get(f"{SUPABASE_URL}/rest/v1/p2_articles", params=params, headers=HEADERS, timeout=60)
    return r.json() if r.status_code == 200 else []


def update_article(article_id, updates):
    """Patch an article in Supabase."""
    r = _session.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        json=updates,
        headers=HEADERS,
        timeout=15,
    )
    return r.status_code in (200, 204)


def run_tweet_enricher(hours=24, apply=False):
    """Run the tweet enricher script."""
    cmd = [sys.executable, os.path.join(PIPELINE_DIR, "tweet-enricher.py"), "--hours", str(hours)]
    if apply:
        cmd.append("--apply")
    print("\n══ Tweet Enricher ══")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    print(result.stdout[-500:] if result.stdout else "")
    if result.returncode != 0:
        print(f"⚠ Tweet enricher error: {result.stderr[-200:]}")


def main():
    parser = argparse.ArgumentParser(description="Enrich articles with images and social embeds")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours")
    parser.add_argument("--apply", action="store_true", help="Apply changes to Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--images-only", action="store_true", help="Only enrich images")
    parser.add_argument("--embeds-only", action="store_true", help="Only add embeds")
    parser.add_argument("--trailers-only", action="store_true", help="Only add YouTube trailers")
    parser.add_argument("--inline-only", action="store_true", help="Only add inline images + pull quotes")
    parser.add_argument("--youtube-only", action="store_true", help="Only add YouTube embeds")
    parser.add_argument("--max", type=int, default=10, help="Max articles to enrich per run")
    args = parser.parse_args()

    apply = args.apply and not args.dry_run
    registry = load_registry()

    # Scope control
    only_mode = args.images_only or args.embeds_only or args.trailers_only or args.inline_only or args.youtube_only
    run_images = not only_mode or args.images_only
    run_trailers = not only_mode or args.trailers_only
    run_embeds = not only_mode or args.embeds_only
    run_inline = not only_mode or args.inline_only
    run_youtube = not only_mode or args.youtube_only

    # ── 1. IMAGE ENRICHMENT ──
    if run_images:
        print("\n══ Image Enrichment ══")
        articles = get_recent_articles(hours=args.hours)
        pexels_articles = [a for a in articles if "pexels.com" in (a.get("image_url") or "")]
        print(f"Found {len(pexels_articles)} articles with Pexels images (out of {len(articles)} total)")

        enriched = 0
        for article in pexels_articles[:args.max]:
            print(f"\n  📰 {article['headline'][:70]}")
            print(f"     Current: {(article.get('image_url') or '')[:80]}")

            new_url, credit = find_better_image(article["headline"], article.get("image_url", ""))
            if new_url:
                print(f"     → {new_url[:80]}")
                # Vision sanity-check BEFORE overwriting a live hero. The
                # keyword floor stops most mismatches, but a final pixel-level
                # look is what prevents a Gandalf meme / pageant photo going
                # live. Only block on a clear MISMATCH; allow MATCH, UNVERIFIED,
                # or an unavailable judge (fail-open so enrichment still runs).
                vision_ok = True
                if _vision_image_match:
                    try:
                        probe = dict(article)
                        probe["image_url"] = new_url
                        probe["image_caption"] = credit or article.get("image_caption", "")
                        verdict = _vision_image_match(probe)
                        if verdict and verdict.get("verdict") == "MISMATCH":
                            vision_ok = False
                            print(f"     🚫 Vision MISMATCH — skipping swap: {verdict.get('reason','')[:90]}")
                    except Exception as _ve:
                        print(f"     ⚠️  Vision check errored (allowing swap): {_ve}")
                if not vision_ok:
                    print(f"     — Kept original hero (candidate failed vision check)")
                elif apply:
                    updates = {"image_url": new_url}
                    if credit:
                        updates["image_caption"] = credit
                    if update_article(article["id"], updates):
                        print(f"     ✅ Updated!")
                        enriched += 1
                    else:
                        print(f"     ❌ Update failed")
                else:
                    print(f"     [DRY RUN] Would update")
                    enriched += 1
            else:
                print(f"     — No better image found")

        print(f"\n  Image enrichment: {enriched} articles {'updated' if apply else 'would update'}")

    # ── 2. YOUTUBE TRAILER ENRICHMENT ──
    if run_trailers:
        print("\n══ YouTube Trailer Enrichment ══")
        all_articles = get_recent_articles(hours=args.hours)
        # Filter to entertainment articles (movies/series most likely)
        ent_articles_for_trailers = [
            a for a in all_articles
            if a.get("category") in ("entertainment",)
        ]
        print(f"Found {len(ent_articles_for_trailers)} entertainment articles to check for trailers")

        trailer_enriched = 0
        for article in ent_articles_for_trailers:
            if trailer_enriched >= args.max:
                break
            body = article.get("body", "")
            headline = article.get("headline", "")

            # Skip if already has a YouTube embed
            if article_has_social_embed(body, "youtube"):
                continue

            # Detect content type
            ctype = media_sources.detect_content_type(headline, body)
            if ctype not in ("movie", "series"):
                continue

            print(f"\n  🎬 [{ctype}] {headline[:65]}")

            # Search for trailer
            trailer_url = media_sources.search_youtube_trailer(headline, ctype, body)
            if not trailer_url:
                print(f"     — No trailer found")
                continue

            print(f"     → Trailer: {trailer_url}")
            if apply:
                # Insert <youtube> tag after the first paragraph
                embed_tag = f"\n\n<youtube>{trailer_url}</youtube>\n"
                paras = body.split("\n\n", 2)
                if len(paras) >= 3:
                    new_body = paras[0] + "\n\n" + paras[1] + embed_tag + "\n\n" + paras[2]
                elif len(paras) == 2:
                    new_body = paras[0] + "\n\n" + paras[1] + embed_tag
                else:
                    new_body = body + embed_tag

                if update_article(article["id"], {"body": new_body}):
                    print(f"     ✅ Trailer embedded!")
                    trailer_enriched += 1
                else:
                    print(f"     ❌ Embed failed")
            else:
                print(f"     [DRY RUN] Would embed trailer")
                trailer_enriched += 1

        print(f"\n  Trailer enrichment: {trailer_enriched} articles {'updated' if apply else 'would update'}")

    # ── 3. SOCIAL EMBED ENRICHMENT ──
    if run_embeds:
        # Topic search for tweet embeds in articles
        run_tweet_enricher(hours=args.hours, apply=apply)

        # Instagram embed enrichment — all categories
        print("\n══ Instagram Embed Enrichment ══")
        ig_categories = [
            "entertainment", "sports", "technology", "news",
            "immigration", "nri-world", "markets-finance", "travel",
        ]
        ig_articles = get_recent_articles(hours=args.hours)
        ig_articles = [a for a in ig_articles if a.get("category") in ig_categories]
        print(f"Found {len(ig_articles)} articles across {len(ig_categories)} categories")

        # Pre-fetch IG posts for all matching handles in one batch
        all_ig_handles = set()
        for article in ig_articles[:args.max]:
            body = article.get("body", "")
            if article_has_social_embed(body, "instagram"):
                continue  # skip articles that already have an IG embed
            matches = find_matching_handles(article["headline"], registry, platform="instagram")
            for m in matches[:2]:
                all_ig_handles.add(m["handle"])
        if all_ig_handles:
            print(f"  Pre-fetching {len(all_ig_handles)} unique IG handles via Apify...")
            prefetch_ig_posts(list(all_ig_handles))
        else:
            print(f"  No IG handles matched any articles — skipping Apify calls")

        ig_enriched = 0
        ig_stripped = 0
        for article in ig_articles[:args.max]:
            # ── Verify existing IG embeds before deciding to skip ──
            body = article.get("body", "")
            if article_has_social_embed(body, "instagram"):
                cleaned_body, n_removed = verify_ig_embeds(body)
                if n_removed > 0:
                    ig_stripped += n_removed
                    if apply:
                        if update_article(article["id"], {"body": cleaned_body}):
                            print(f"  ✅ Stripped {n_removed} fake IG embed(s) from: {article['headline'][:60]}")
                            article["body"] = cleaned_body
                        else:
                            print(f"  ❌ Failed to strip fake IG embed(s) from: {article['headline'][:60]}")
                    else:
                        print(f"  [DRY RUN] Would strip {n_removed} fake IG embed(s) from: {article['headline'][:60]}")
                    # If all IG embeds were stripped, fall through to add a real one
                    if not article_has_social_embed(cleaned_body, "instagram"):
                        body = cleaned_body
                        # Fall through — don't continue
                    else:
                        continue
                else:
                    continue

            matches = find_matching_handles(article["headline"], registry, platform="instagram")
            if not matches:
                continue

            print(f"\n  📰 {article['headline'][:70]}")
            for m in matches[:2]:
                print(f"     IG match: @{m['handle']} ({m['name']})")

                # Build topic keywords from FULL headline, excluding the matched
                # person/org name (trivially present in every post by that account)
                # and common stopwords.
                _IG_STOPWORDS = {
                    "the","a","an","in","on","at","to","for","of","and","or","is",
                    "are","was","were","has","had","have","been","be","will","can",
                    "may","with","by","from","as","its","it","his","her","their",
                    "new","says","said","after","over","how","why","what","who",
                    "than","amid","that","this","into","top","first","most","more",
                    "could","would","should","not","but","all","also","just","now",
                    "up","out","back","set","get","one","two","three","four","big",
                    "man","men","year","years","day","days","time","per","vice",
                    "president","minister","prime","ceo","cto","chief","leader",
                }
                name_words = {w.lower().strip(".,!?:;-'\"") for w in m["name"].split()}
                handle_words = {m["handle"].lower().replace("_", "")}
                exclude = _IG_STOPWORDS | name_words | handle_words
                topic_kw = [
                    w for w in article["headline"].split()
                    if len(w) > 2 and w.lower().strip(".,!?:;-'\"") not in exclude
                ]
                shortcodes = search_instagram_posts(
                    m["handle"],
                    topic_kw,
                )
                if shortcodes:
                    url = f"https://www.instagram.com/p/{shortcodes[0]}/"
                    print(f"     → Found post: {url}")
                    if apply:
                        body = article.get("body", "")
                        embed_line = f"\n\n{url}\n"
                        from embed_placement import insert_embed_high
                        new_body_candidate = insert_embed_high(body, embed_line)
                        if new_body_candidate != body:
                            new_body = new_body_candidate
                        else:
                            # Fallback: try old \n\n split for non-HTML bodies
                            paras = body.split("\n\n", 2)
                            if len(paras) >= 2:
                                new_body = paras[0] + "\n\n" + paras[1] + embed_line + "\n\n" + (paras[2] if len(paras) > 2 else "")
                            else:
                                new_body = body + embed_line
                        if update_article(article["id"], {"body": new_body}):
                            print(f"     ✅ Embedded!")
                            ig_enriched += 1
                        else:
                            print(f"     ❌ Embed failed")
                    else:
                        print(f"     [DRY RUN] Would embed")
                        ig_enriched += 1
                    break  # one embed per article
                else:
                    print(f"     — No relevant posts found")

        print(f"\n  Instagram enrichment: {ig_enriched} articles {'updated' if apply else 'would update'}")
        if ig_stripped:
            print(f"  Instagram verification: stripped {ig_stripped} fake/dead embed(s)")

        # ── Verify IG embeds in ALL categories (not just entertainment) ──
        # Writer LLMs can hallucinate /reel/ URLs in any article category.
        print("\n══ Instagram Embed Verification (all categories) ══")
        all_for_ig_verify = get_recent_articles(hours=args.hours)
        # Exclude entertainment articles we already checked above
        ent_ids = {a["id"] for a in ig_articles[:args.max]} if run_embeds else set()
        non_ent = [a for a in all_for_ig_verify if a["id"] not in ent_ids]
        ig_verify_stripped = 0
        for article in non_ent:
            body = article.get("body", "")
            if not article_has_social_embed(body, "instagram"):
                continue
            cleaned_body, n_removed = verify_ig_embeds(body)
            if n_removed > 0:
                ig_verify_stripped += n_removed
                if apply:
                    if update_article(article["id"], {"body": cleaned_body}):
                        print(f"  ✅ Stripped {n_removed} fake IG embed(s) from: {article['headline'][:60]}")
                    else:
                        print(f"  ❌ Failed to strip from: {article['headline'][:60]}")
                else:
                    print(f"  [DRY RUN] Would strip {n_removed} fake IG embed(s) from: {article['headline'][:60]}")
        print(f"  Verification: checked {len(non_ent)} non-entertainment articles, stripped {ig_verify_stripped} fake embed(s)")

    # ── 3.5 YOUTUBE EMBED ENRICHMENT ──
    if run_youtube:
        print("\n══ YouTube Embed Enrichment ══")
        load_env(os.path.expanduser("~/workspace/.env.youtube"))
        yt_categories = [
            "entertainment", "sports", "technology", "news",
            "immigration", "nri-world", "markets-finance", "travel", "food",
        ]
        yt_articles = get_recent_articles(hours=args.hours)
        yt_articles = [a for a in yt_articles if a.get("category") in yt_categories]
        print(f"Found {len(yt_articles)} articles across {len(yt_categories)} categories")

        yt_enriched = 0
        yt_searched = 0
        for article in yt_articles[:args.max]:
            body = article.get("body", "")
            headline = article.get("headline", "")

            # Skip if already has a YouTube embed
            if article_has_social_embed(body, "youtube"):
                continue

            # Skip if already has both X and IG embeds (enough social enrichment)
            has_x = article_has_social_embed(body, "twitter") or article_has_social_embed(body, "x")
            has_ig = article_has_social_embed(body, "instagram")
            if has_x and has_ig:
                continue

            # Match headline to registry entities
            entities = find_matching_entities(headline, registry)
            if not entities:
                continue

            # Try up to 2 matching entities, pick best YouTube result
            best_yt = None
            print(f"\n  📰 {headline[:75]}")
            for entity in entities[:2]:
                print(f"     YT search: {entity['name']}")
                result = find_best_youtube_embed(entity["name"], headline)
                yt_searched += 1
                if result and (best_yt is None or result["score"] > best_yt["score"]):
                    best_yt = result

            if not best_yt:
                print(f"     — No relevant YouTube video found")
                continue

            print(f"     → {best_yt['url']}")
            print(f"       \"{best_yt['title']}\" ({best_yt['channel']}) [score:{best_yt['score']}]")

            if apply:
                from embed_placement import insert_embed_high
                embed_tag = f"\n\n<youtube>{best_yt['url']}</youtube>\n"
                new_body_candidate = insert_embed_high(body, embed_tag)
                if new_body_candidate != body:
                    new_body = new_body_candidate
                else:
                    paras = body.split("\n\n", 2)
                    if len(paras) >= 2:
                        new_body = paras[0] + "\n\n" + paras[1] + embed_tag + "\n\n" + (paras[2] if len(paras) > 2 else "")
                    else:
                        new_body = body + embed_tag

                if update_article(article["id"], {"body": new_body}):
                    print(f"     ✅ Embedded!")
                    yt_enriched += 1
                else:
                    print(f"     ❌ Embed failed")
            else:
                print(f"     [DRY RUN] Would embed")
                yt_enriched += 1

        print(f"\n  YouTube enrichment: {yt_enriched} articles {'updated' if apply else 'would update'} ({yt_searched} searched, {_YT_QUOTA_USED} API units used)")

    # ── 4. INLINE IMAGE + PULL QUOTE ENRICHMENT ──
    if run_inline:
        print("\n══ Inline Image + Pull Quote Enrichment ══")
        all_articles = get_recent_articles(hours=args.hours)
        # Filter: articles with enough body text, no existing inline images
        candidates = [
            a for a in all_articles
            if len((a.get("body") or "").split()) >= _MIN_WORDS_FOR_INLINE
        ]
        print(f"Found {len(candidates)} articles with sufficient body text (out of {len(all_articles)} total)")

        inline_enriched = 0
        for article in candidates[:args.max]:
            body = article.get("body", "")
            headline = article.get("headline", "")
            hero_url = article.get("image_url", "")
            has_images = article_has_inline_images(body)
            has_quote = article_has_pull_quote(body)

            if has_images and has_quote:
                continue

            print(f"\n  📰 {headline[:70]}")
            new_body = body
            changes = []

            # Add inline images if needed
            if not has_images:
                cat = article.get("category", "")
                images = find_inline_images(headline, body, hero_url, category=cat)
                if images:
                    max_cap = 3 if cat in _VISUAL_CATEGORIES else 2
                    new_body = insert_inline_images(new_body, images, max_cap=max_cap)
                    changes.append(f"{len(images)} inline image(s)")
                else:
                    print(f"     — No relevant inline images found")

            # Add pull quote if needed
            if not has_quote:
                quote = extract_pull_quote(new_body)
                if quote:
                    new_body = insert_pull_quote(new_body, quote)
                    changes.append("pull quote")
                    print(f"     ✓ Pull quote: \"{quote[:60]}...\"")

            if changes and new_body != body:
                change_desc = " + ".join(changes)
                if apply:
                    if update_article(article["id"], {"body": new_body}):
                        print(f"     ✅ Added {change_desc}")
                        inline_enriched += 1
                    else:
                        print(f"     ❌ Update failed")
                else:
                    print(f"     [DRY RUN] Would add {change_desc}")
                    inline_enriched += 1

        print(f"\n  Inline enrichment: {inline_enriched} articles {'updated' if apply else 'would update'}")

    # ── 5. HERO IMAGE HEALTH CHECK ──
    # Detect dead hero image URLs (Wikipedia deletions, broken uploads) and re-source
    if not only_mode:
        print("\n══ Hero Image Health Check ══")
        all_articles = get_recent_articles(hours=max(args.hours, 72))  # Check 3 days minimum
        hero_checked = 0
        hero_fixed = 0
        for article in all_articles:
            img_url = article.get("image_url", "")
            if not img_url:
                print(f"\n  ⚠ No image: {article['headline'][:50]}")
                continue
            if not img_url.startswith("http"):
                # Relative path = definitely broken
                print(f"\n  ⚠ Relative URL: {article['headline'][:50]}")
                print(f"    → {img_url[:80]}")
            else:
                continue  # Only flag non-http URLs in this pass; full check below

        # Full health check: verify each image URL loads
        for article in all_articles:
            img_url = article.get("image_url", "")
            if not img_url:
                continue
            hero_checked += 1
            try:
                r = subprocess.run(
                    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '5',
                     '-A', 'Mozilla/5.0', img_url],
                    capture_output=True, text=True, timeout=10
                )
                code = r.stdout.strip()
            except Exception:
                code = "000"

            if code not in ('200', '301', '302'):
                print(f"\n  ❌ [{code}] {article['headline'][:50]}")
                print(f"      {img_url[:80]}")
                if apply:
                    try:
                        sys.path.insert(0, PIPELINE_DIR)
                        from image_sourcer import source_hero_image
                        new_url, attribution, caption = source_hero_image(article)
                        if new_url and new_url != img_url:
                            updates = {'image_url': new_url, 'image_attribution': attribution or ''}
                            if update_article(article['id'], updates):
                                print(f"      ✅ Re-sourced: {new_url[:70]}")
                                hero_fixed += 1
                            else:
                                print(f"      ❌ DB update failed")
                        else:
                            print(f"      ⚠ No replacement found")
                    except Exception as e:
                        print(f"      ❌ Re-source error: {e}")
                else:
                    print(f"      [DRY RUN] Would re-source")

        print(f"\n  Hero check: {hero_checked} checked, {hero_fixed} fixed")

    print("\n✅ Enrichment complete!")


if __name__ == "__main__":
    main()
