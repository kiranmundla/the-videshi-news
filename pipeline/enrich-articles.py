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


def fetch_wikipedia_image(subject):
    """Get the main Wikipedia image for a subject."""
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
            if img:
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

    # Try Wikipedia first for named subjects (skip logos/PNGs)
    if subject:
        wiki_img = fetch_wikipedia_image(subject)
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
    """Load social embed registry."""
    path = os.path.join(PIPELINE_DIR, "social-embed-registry.json")
    with open(path) as f:
        return json.load(f)


def find_matching_handles(headline, registry, platform="instagram"):
    """Find registry handles that match an article headline."""
    matches = []
    headline_lower = headline.lower()

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
                # Filter stopwords
                stopwords = {"the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to"}
                significant = [p for p in name_parts if p not in stopwords and len(p) > 2]
                if not significant:
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
    for post in posts:
        caption = (post.get('caption', '') or '').lower()
        if not caption:
            continue
        hits = sum(1 for kw in keywords if kw in caption)
        if hits >= 2 or (hits >= 1 and len(keywords) <= 2):
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

    urls = [f"https://www.instagram.com/{h}/" for h in handles]
    payload = json.dumps({
        'directUrls': urls,
        'resultsType': 'posts',
        'resultsLimit': results_limit,
        'searchType': 'user',
        'searchLimit': 1,
    })

    try:
        result = subprocess.run(
            ['curl', '-sS', '-X', 'POST',
             f'https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={token}',
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


def find_inline_images(headline, body, hero_url=""):
    """Find up to 3 inline Wikipedia images for entities in the article.
    Returns list of (entity, image_url, caption) tuples."""
    entities = extract_entities(headline, body)
    results = []
    hero_norm = (hero_url or "").split("?")[0].lower()
    # Extract hero filename for cross-host comparison (Supabase vs Wikimedia)
    hero_fname = _wikimedia_filename(hero_url) if hero_url else ""
    # Build a slugified version of hero URL path for entity-name matching
    hero_slug = re.sub(r'[^a-z0-9]', '', hero_norm)

    for entity in entities:
        if len(results) >= 3:
            break

        img_url = fetch_wikipedia_image(entity)
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

        caption = f"{entity} — Photo: Wikimedia Commons"
        results.append((entity, img_url, caption))
        print(f"    ✓ Inline image for '{entity}'")

    return results


def _is_html_body(body):
    """Check if article body is HTML (starts with HTML block tags)."""
    return bool(re.match(r'^\s*<(?:p|h[1-6]|div|section|article)\b', body, re.IGNORECASE))


def insert_inline_images(body, images):
    """Insert inline images at natural break points in the article body.
    Places images between paragraphs, spaced evenly through the article."""
    if not images:
        return body

    is_html = _is_html_body(body)

    paragraphs = body.split("\n\n")
    if len(paragraphs) < 3:
        return body

    # Calculate insertion points — evenly spaced, skip first paragraph
    n_images = len(images)
    step = max(2, (len(paragraphs) - 1) // (n_images + 1))

    # Insert in reverse order so indices stay valid
    for i in range(len(images) - 1, -1, -1):
        entity, url, caption = images[i]
        idx = min(step * (i + 1), len(paragraphs) - 1)
        if is_html:
            cap_escaped = caption.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
            img_md = f'\n<figure style="margin:28px 0;text-align:center"><img src="{url}" alt="{cap_escaped}" style="max-width:100%;border-radius:8px" loading="lazy"><figcaption style="font-size:0.85rem;color:#666;margin-top:8px">{caption}</figcaption></figure>\n'
        else:
            img_md = f"\n![{caption}]({url})\n"
        paragraphs.insert(idx, img_md)

    return "\n\n".join(paragraphs)


# ═══════════════════════════════════════════
# PULL QUOTE ENRICHMENT
# ═══════════════════════════════════════════

def extract_pull_quote(body):
    """Find the most impactful sentence for a pull quote.
    Prefers sentences with quotes, strong language, or statistics."""
    # Split into sentences (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', body)
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
    return bool(re.search(r'>\s*\*\*["\u201c]', body or ""))


# ═══════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════

def get_recent_articles(hours=24, category=None):
    """Fetch recent published articles."""
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    params = {
        "select": "id,headline,slug,category,image_url,image_caption,body,published_at",
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
    parser.add_argument("--max", type=int, default=10, help="Max articles to enrich per run")
    args = parser.parse_args()

    apply = args.apply and not args.dry_run
    registry = load_registry()

    # Scope control
    only_mode = args.images_only or args.embeds_only or args.trailers_only or args.inline_only
    run_images = not only_mode or args.images_only
    run_trailers = not only_mode or args.trailers_only
    run_embeds = not only_mode or args.embeds_only
    run_inline = not only_mode or args.inline_only

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
        # Run tweet enricher
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

                shortcodes = search_instagram_posts(
                    m["handle"],
                    article["headline"].split()[:5],
                )
                if shortcodes:
                    url = f"https://www.instagram.com/p/{shortcodes[0]}/"
                    print(f"     → Found post: {url}")
                    if apply:
                        body = article.get("body", "")
                        embed_line = f"\n\n{url}\n"
                        # Insert after second </p> tag (works with HTML bodies)
                        import re as _re
                        _p_ends = [m.end() for m in _re.finditer(r'</p>', body, _re.IGNORECASE)]
                        if len(_p_ends) >= 2:
                            insert_at = _p_ends[1]
                            new_body = body[:insert_at] + embed_line + body[insert_at:]
                        elif len(_p_ends) == 1:
                            insert_at = _p_ends[0]
                            new_body = body[:insert_at] + embed_line + body[insert_at:]
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
                images = find_inline_images(headline, body, hero_url)
                if images:
                    new_body = insert_inline_images(new_body, images)
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

    print("\n✅ Enrichment complete!")


if __name__ == "__main__":
    main()
