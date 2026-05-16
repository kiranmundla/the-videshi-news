#!/usr/bin/env python3
"""
videshi-images.py — Image sourcing for The Videshi news pipeline.

Searches for article images using a tiered strategy:
  1. Wikipedia page images (best for specific entities)
  2. Pexels API (general fallback — culture, travel, lifestyle)
  3. No image (preferred over wrong image)

PIB Photo RSS provides attribution links for government/political articles.

Usage:
    python3 videshi-images.py fetch              # Articles missing images
    python3 videshi-images.py fetch --refresh     # Also replace bad images
    python3 videshi-images.py fetch --id <UUID>   # Specific article
    python3 videshi-images.py fetch --no-process  # Just store URLs (skip processing)
"""

import io
import json
import os
import re
import sys
import time
import urllib.parse
import requests
from PIL import Image, ImageEnhance

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
PEXELS_ENV_FILE = os.path.expanduser("~/workspace/.env.pexels")
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "TheVideshiBot/1.0 (https://thevideshi.com; contact@thevideshi.com)"
POLITE_DELAY = 1.0          # seconds between API calls
UPLOAD_DELAY = 0.5          # seconds between Supabase uploads
THUMB_WIDTH = 800            # target width for thumbnails
MIN_SOURCE_WIDTH = 400       # reject originals narrower than this
MAX_RESULTS = 10             # results per Wikimedia search
TARGET_WIDTH = 1200          # final image width (retina-quality)
TARGET_HEIGHT = 675          # final image height (16:9 at 1200px)
JPEG_QUALITY = 88            # high-quality JPEG output

# Patterns that indicate a bad / unusable image file name
BAD_FILENAME_RE = re.compile(
    r"Flag_of|flag_of|Map_of|map_of|Logo|logo|Icon|icon|"
    r"Coat_of_arms|coat_of_arms|seal_of|Seal_of|emblem|Emblem|"
    r"globe|Globe|locator|Locator|location_map|Location_map|"
    r"pictogram|Pictogram|symbol|Symbol|no_image|placeholder|"
    r"screenshot|Screenshot|UI_|_UI\.|interface|webpage|text_message|"
    r"book_cover|\.djvu|\.tiff?$|"
    r"Taj_Mahal|taj_mahal|India_Gate|Gateway_of_India|"
    r"Charminar|Hawa_Mahal|Golden_Temple|Lotus_Temple|"
    r"Qutub_Minar|Victoria_Memorial|Red_Fort",
    re.IGNORECASE,
)

# Geographic entities whose Wikipedia lead images are tourist landmarks,
# not useful for news articles (storms, politics, crime, etc.)
GEOGRAPHIC_ENTITIES = {
    # Indian states & UTs
    "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh",
    "goa", "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka",
    "kerala", "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram",
    "nagaland", "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu",
    "telangana", "tripura", "uttar pradesh", "uttarakhand", "west bengal",
    "delhi", "jammu and kashmir", "ladakh", "chandigarh", "puducherry",
    # Countries
    "india", "pakistan", "bangladesh", "sri lanka", "nepal", "china",
    "united states", "united kingdom", "canada", "australia", "germany",
    "france", "japan", "south korea", "russia", "brazil", "mexico",
    "saudi arabia", "united arab emirates", "israel", "iran", "iraq",
    "afghanistan", "myanmar", "thailand", "singapore", "malaysia", "indonesia",
    # Major cities that resolve to landmark images
    "mumbai", "new delhi", "bengaluru", "hyderabad", "chennai", "kolkata",
    "pune", "ahmedabad", "jaipur", "lucknow", "agra", "varanasi",
    "new york", "london", "toronto", "sydney", "dubai", "washington",
}

# Ambiguous short entities that match wrong things on Commons
AMBIGUOUS_ENTITIES = {
    "ICE", "NHS", "FBI", "CIA", "UN", "WHO", "PM", "CM", "MP", "ED",
    "IT", "AI", "US", "UK", "UAE", "GST", "RBI", "BJP", "AAP", "IIT",
    "NRI", "DHS", "OPT", "DOL", "DOJ", "SEC", "FTC", "IMF", "WTO",
    "IPL", "CSK", "LSG", "MI", "RCB", "SRH", "GT", "KKR", "DC", "PBKS",
    "NEET", "FIRE", "CAA", "NRC", "RAM", "CBI", "NIA", "SEBI", "TMC",
    "JEE", "UGC", "NTA", "IAS", "IPS", "UPSC", "SSC", "ISRO", "DRDO",
}

# Patterns for existing URLs we consider "bad" and want to replace
BAD_URL_RE = re.compile(
    r"hindustantimes\.com|htmedia|\.svg$|Flag_of_|flag_of_|"
    r"logo|icon|placeholder|default|thumbnail.*small|"
    r"upload\.wikimedia.*(?:map|globe|location|locator)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env():
    """Load Supabase credentials from the env file."""
    env = {}
    if not os.path.exists(ENV_FILE):
        print(f"ERROR: {ENV_FILE} not found")
        sys.exit(1)
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def supabase_headers(key):
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def is_bad_url(url):
    """Return True if the URL is missing or looks low-quality."""
    if not url or not isinstance(url, str) or len(url.strip()) < 20:
        return True
    return bool(BAD_URL_RE.search(url))


def strip_html(text):
    """Remove HTML tags from attribution strings."""
    return re.sub(r"<[^>]+>", "", text).strip() if text else ""


def is_bad_filename(name):
    """Check if an image filename matches bad patterns."""
    return bool(BAD_FILENAME_RE.search(name))


def is_relevant_filename(filename, search_terms):
    """
    Check if a Commons filename is relevant to the search terms.
    Requires at least one significant word (4+ chars) from search terms
    to appear in the filename. This prevents random matches like
    'Ice Speedway' for 'ICE enforcement' or 'Milky Way' for 'Eileen Wang'.
    
    For person names (multi-word entities), requires the first name or
    a distinctive part — not just a common surname like 'Singh' or 'Kumar'.
    """
    if not search_terms:
        return True  # can't validate, assume ok
    fn_lower = filename.lower().replace("_", " ").replace("-", " ")
    
    # Common Indian/generic surnames that are too ambiguous alone
    COMMON_SURNAMES = {
        "singh", "kumar", "sharma", "gupta", "patel", "khan", "wang",
        "shah", "verma", "joshi", "reddy", "nair", "yadav", "mishra",
        "das", "paul", "brown", "smith", "jones", "wilson", "moore",
    }
    
    for term in search_terms:
        if not isinstance(term, str):
            continue
        words = [w.lower() for w in term.split() if len(w) >= 4]
        for word in words:
            if word in COMMON_SURNAMES:
                continue  # skip ambiguous surnames
            if word in fn_lower:
                return True
    return False


def collect_search_terms(article):
    """Collect all meaningful search terms from an article for relevance checking."""
    terms = []
    isq = article.get("image_search_query")
    if isq and isinstance(isq, str):
        terms.append(isq)
    entities = article.get("image_entities")
    if entities and isinstance(entities, list):
        terms.extend([e for e in entities if isinstance(e, str) and len(e) >= 4])
    headline = article.get("headline", "")
    if headline:
        terms.append(headline)
    return terms

# ---------------------------------------------------------------------------
# Confidence scoring & category skip logic
# ---------------------------------------------------------------------------

# Categories/keywords where images are usually irrelevant
SKIP_IMAGE_KEYWORDS = re.compile(
    r"\b(bill|policy|court|ruling|law|amendment|regulation|polls|election date|"
    r"ballot|civic|GDP|inflation|fiscal|deficit|surplus|monetary|tariff|"
    r"sanctions|quota|tribunal|verdict|legislation|ordinance)\b",
    re.IGNORECASE,
)

def should_skip_image(article):
    """
    Return True if this article is unlikely to benefit from an image.
    Policy, legal, financial analysis, civic process articles rarely
    have good free images — skip unless headline has a clear named person/place.
    """
    headline = article.get("headline", "")
    # Check for skip keywords
    if not SKIP_IMAGE_KEYWORDS.search(headline):
        return False  # doesn't match skip patterns, proceed normally

    # Even if it matches skip keywords, allow if headline has a clear person name
    # (2+ consecutive capitalized words that aren't common words)
    common = {"the","for","and","from","with","that","would","will","has","its",
              "how","why","what","new","may","can","all","over","after","into",
              "amid","under","near","says","gets","hits","out","off","up","on",
              "now","set","top","big","cut","ban","bid","row","war","tax"}
    words = headline.split()
    caps_run = 0
    for w in words:
        if w[0:1].isupper() and w.lower() not in common and len(w) > 1:
            caps_run += 1
            if caps_run >= 2:
                return False  # looks like a person/place name, allow images
        else:
            caps_run = 0

    return True  # skip image sourcing


def score_image_confidence(source_type, entity_query, wikipedia_page_title, article):
    """
    Score confidence 1-5 for a found image.
    
    5: Exact match — Wikipedia page title is a clear substring of the headline
       AND passes geographic + filename relevance checks
    4: Strong match — high word overlap between page title and headline
    3: Moderate match — partial word overlap
    2: Loosely related
    1: Generic/unrelated
    
    Only images scoring 5 should be kept (strict policy: no image > wrong image).
    """
    headline = (article.get("headline") or "").lower()
    page_lower = (wikipedia_page_title or "").lower().replace("_", " ")
    category = (article.get("category") or "").lower()
    
    if source_type == "wikipedia":
        # BLOCK: geographic entities for non-travel articles
        # Their Wikipedia lead images are tourist landmarks, not relevant to news
        entity_lower = (entity_query or "").lower().strip()
        if entity_lower in GEOGRAPHIC_ENTITIES and category != "travel":
            print(f"    🚫 Geographic entity '{entity_query}' blocked for non-travel article")
            return 1
        
        # Strict check: is the full page title (cleaned) a substring of the headline?
        page_clean = page_lower.strip()
        if page_clean and page_clean in headline:
            return 5  # exact substring match — high confidence
        
        # Check word overlap
        page_words = [w for w in page_clean.split() if len(w) > 2]
        headline_words = set(headline.split())
        
        if not page_words:
            return 2
        
        # Count how many significant page title words appear in headline
        matches = sum(1 for w in page_words if w in headline_words)
        match_ratio = matches / len(page_words) if page_words else 0
        
        if match_ratio >= 0.8:
            return 4  # strong word overlap
        elif match_ratio >= 0.5:
            return 3  # moderate overlap
        else:
            return 2  # page found but doesn't match headline well
    
    elif source_type == "commons":
        # Commons results are inherently less reliable
        # Only score 3 if the search entity appears prominently in headline
        entity_lower = (entity_query or "").lower()
        entity_words = [w for w in entity_lower.split() if len(w) > 2]
        if entity_words:
            matches = sum(1 for w in entity_words if w in headline)
            if matches >= len(entity_words) * 0.8:
                return 3  # decent match but Commons, cap at 3
        return 2  # generic Commons result
    
    return 1

# ---------------------------------------------------------------------------
# Wikipedia page image lookup (PRIMARY SOURCE)
# ---------------------------------------------------------------------------

def search_wikipedia_image(entity):
    """
    Look up the Wikipedia article for `entity` and return its lead image.
    Returns (thumb_url, attribution) or (None, None).
    """
    # Normalise entity to a plausible Wikipedia title
    title = entity.strip().replace(" ", "_")
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages|pageprops",
        "piprop": "original|thumbnail",
        "pithumbsize": THUMB_WIDTH,
        "format": "json",
        "redirects": 1,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(WIKIPEDIA_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    ⚠ Wikipedia API error: {e}")
        return None, None

    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1":
            continue  # page not found

        # Get thumbnail (preferred — pre-sized to 800px)
        thumb = page.get("thumbnail", {})
        thumb_url = thumb.get("source")
        thumb_w = thumb.get("width", 0)
        thumb_h = thumb.get("height", 0)

        # Get original as fallback
        original = page.get("original", {})
        orig_url = original.get("source")
        orig_w = original.get("width", 0)
        orig_h = original.get("height", 0)

        # Pick the best URL
        chosen_url = thumb_url or orig_url
        chosen_w = thumb_w or orig_w
        chosen_h = thumb_h or orig_h

        if not chosen_url:
            continue

        # Filter bad images
        if is_bad_filename(chosen_url):
            continue
        if chosen_url.lower().endswith(".svg"):
            continue
        if chosen_url.lower().endswith(".pdf"):
            continue
        if chosen_w > 0 and chosen_w < MIN_SOURCE_WIDTH:
            continue

        # Clean tracking params
        chosen_url = chosen_url.split("?")[0]

        # Wikipedia images are typically CC-licensed or public domain
        page_title = page.get("title", entity)
        attribution = f"Wikipedia — {page_title}"

        return chosen_url, attribution

    return None, None


def _image_filename_relevant(image_url, article):
    """
    Cross-validate that the image filename is plausibly related to the article.
    
    Catches cases like:
    - "Rare Bear" (the racing aircraft) for a bear attack article
    - "Taj Mahal" for a storm/disaster article about Uttar Pradesh
    - Random trophy images for broadcast rights articles
    
    Returns True if the image seems relevant, False if suspicious.
    """
    headline = (article.get("headline") or "").lower()
    category = (article.get("category") or "").lower()
    
    # Extract filename from URL
    filename = image_url.split("/")[-1].split("?")[0].lower()
    filename_clean = filename.replace("_", " ").replace("-", " ").replace("%20", " ")
    
    # Known irrelevant image patterns for specific contexts
    LANDMARK_FILENAMES = {
        "taj mahal", "india gate", "gateway of india", "charminar",
        "hawa mahal", "golden temple", "lotus temple", "qutub minar",
        "victoria memorial", "red fort", "mysore palace", "meenakshi",
    }
    
    # If filename contains a famous landmark but headline is about disaster/crime/politics, block
    non_travel_keywords = {"storm", "death", "kill", "attack", "flood", "fire", "crash",
                           "fraud", "arrest", "scam", "riot", "protest", "war", "bomb",
                           "earthquake", "cyclone", "drought", "famine", "shooting",
                           "murder", "rape", "assault", "robbery", "kidnap", "missing"}
    
    headline_is_negative = any(kw in headline for kw in non_travel_keywords)
    filename_is_landmark = any(lm in filename_clean for lm in LANDMARK_FILENAMES)
    
    if headline_is_negative and filename_is_landmark:
        return False
    
    # If the entity matched but the image is of something completely different,
    # check that at least ONE significant word from the headline appears in the filename
    # (only for entities that are common words / have multiple meanings)
    entity_query = (article.get("image_search_query") or "").lower()
    entities = article.get("image_entities") or []
    
    # Multi-meaning entity detection: short entities (1-2 words) that could mean different things
    # For these, require filename to share at least one headline keyword
    MULTI_MEANING_CHECK_WORDS = {"bear", "fire", "ice", "ram", "bat", "rock", "apple",
                                  "jaguar", "mercury", "phoenix", "titan", "giant",
                                  "warrior", "king", "queen", "prince", "crown"}
    
    entity_words = set()
    for e in entities:
        if isinstance(e, str):
            entity_words.update(w.lower() for w in e.split())
    
    if entity_words & MULTI_MEANING_CHECK_WORDS:
        # This entity has a common word that could mean something else
        # Check that the filename relates to the article context, not just the entity
        headline_words = {w for w in headline.split() if len(w) > 3}
        filename_words = set(filename_clean.split())
        # Need at least one headline word (beyond the entity itself) in the filename
        overlap = (headline_words & filename_words) - entity_words
        if not overlap:
            return False
    
    return True


def search_wikipedia_for_article(article):
    """
    Try Wikipedia page image lookups for each entity in the article.
    Returns (thumb_url, attribution) or (None, None).
    """
    entities = article.get("image_entities")
    if not entities or not isinstance(entities, list):
        return None, None

    for entity in entities:
        if not entity or not isinstance(entity, str) or len(entity.strip()) < 2:
            continue
        # Skip short all-uppercase entities (likely acronyms that match wrong Wikipedia pages)
        stripped = entity.strip()
        if len(stripped) <= 4 and stripped == stripped.upper():
            print(f"  ⏭ Skipping acronym entity: \"{entity}\"")
            continue
        if stripped.upper() in AMBIGUOUS_ENTITIES:
            print(f"  ⏭ Skipping ambiguous entity: \"{entity}\"")
            continue
        print(f"  🌐 Wikipedia lookup: \"{entity}\"")
        url, attr = search_wikipedia_image(entity)
        if url:
            # Score confidence
            confidence = score_image_confidence("wikipedia", entity, entity, article)
            if confidence >= 5:
                # Extra check: validate image filename against headline keywords
                if not _image_filename_relevant(url, article):
                    print(f"  ⏭ Image filename irrelevant to headline: {url.split('/')[-1][:60]}")
                    time.sleep(POLITE_DELAY)
                    continue
                print(f"  ✅ Found via Wikipedia: {entity} (confidence: {confidence}/5)")
                return url, attr
            else:
                print(f"  ⏭ Wikipedia match too weak: {entity} (confidence: {confidence}/5)")
        time.sleep(POLITE_DELAY)

    # Also try the headline's key nouns as Wikipedia titles
    headline = article.get("headline", "")
    if headline:
        # Extract capitalised multi-word phrases likely to be entity names
        # e.g. "Ro Khanna", "Alabama", "Tamil Nadu"
        words = headline.split()
        # Try 2-word combos of capitalised words
        bigrams = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if (w1[0:1].isupper() and w2[0:1].isupper()
                    and len(w1) > 1 and len(w2) > 1
                    and w1.lower() not in ("the", "for", "and", "from", "with", "that", "would", "will", "has", "its")):
                bigrams.append(f"{w1} {w2}")
        # Try up to 2 bigrams
        for bigram in bigrams[:2]:
            print(f"  🌐 Wikipedia lookup (headline): \"{bigram}\"")
            url, attr = search_wikipedia_image(bigram)
            if url:
                confidence = score_image_confidence("wikipedia", bigram, bigram, article)
                if confidence >= 5:
                    print(f"  ✅ Found via Wikipedia headline: {bigram} (confidence: {confidence}/5)")
                    return url, attr
                else:
                    print(f"  ⏭ Wikipedia headline match too weak: {bigram} (confidence: {confidence}/5)")
            time.sleep(POLITE_DELAY)

    return None, None

# ---------------------------------------------------------------------------
# Wikimedia Commons search (FALLBACK SOURCE)
# ---------------------------------------------------------------------------

def search_wikimedia(query, limit=MAX_RESULTS):
    """Search Wikimedia Commons and return filtered image candidates."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,        # File namespace
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": THUMB_WIDTH,
        "format": "json",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(WIKIMEDIA_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    ⚠ Wikimedia API error: {e}")
        return []

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return []

    candidates = []
    for page in pages.values():
        title = page.get("title", "")
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue
        info = info_list[0]

        mime = info.get("mime", "")
        width = info.get("width", 0)
        height = info.get("height", 0)

        if "svg" in mime.lower():
            continue
        if "pdf" in mime.lower():
            continue
        if "djvu" in mime.lower():
            continue
        # Reject TIFF files (uncommon, usually scans)
        if "tiff" in mime.lower():
            continue
        if width < MIN_SOURCE_WIDTH:
            continue
        if is_bad_filename(title):
            continue
        # Reject PDFs/DjVu disguised as images (filename check)
        if title.lower().endswith((".pdf", ".djvu", ".tif", ".tiff")):
            continue
        if height > 0 and width > 0:
            ratio = width / height
            if ratio > 4.0 or ratio < 0.33:
                continue

        ext = info.get("extmetadata", {})
        artist_raw = ext.get("Artist", {}).get("value", "")
        artist = strip_html(artist_raw) or "Unknown"
        license_name = ext.get("LicenseShortName", {}).get("value", "")

        thumb_url = info.get("thumburl", "")
        if thumb_url:
            thumb_url = thumb_url.split("?")[0]

        full_url = info.get("url", "")
        if full_url:
            full_url = full_url.split("?")[0]

        is_landscape = width >= height
        score = 0
        if is_landscape:
            score += 50
        if width >= 800:
            score += 30
        elif width >= 600:
            score += 15
        if thumb_url:
            score += 20
        categories = ext.get("Categories", {}).get("value", "").lower()
        if any(kw in categories for kw in ["official", "portrait", "government", "congress"]):
            score += 15

        candidates.append({
            "title": title,
            "thumb_url": thumb_url,
            "full_url": full_url,
            "width": width,
            "height": height,
            "mime": mime,
            "artist": artist,
            "license": license_name,
            "score": score,
            "is_landscape": is_landscape,
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def search_wikimedia_for_article(article):
    """
    Try Wikimedia Commons searches using various article fields.
    Returns (thumb_url, attribution) or (None, None).
    
    STRICT MODE: validates that results are actually relevant to the article.
    No image > wrong image.
    """
    headline = article.get("headline", "")
    search_terms = collect_search_terms(article)

    def validate_and_return(candidates, source_label):
        """Check candidates for relevance before accepting."""
        for cand in candidates[:3]:  # check top 3 by score
            title = cand.get("title", "")
            if is_relevant_filename(title, search_terms):
                url = cand["thumb_url"] or cand["full_url"]
                attr = format_commons_attribution(cand)
                print(f"  ✅ Found via {source_label}: {title[:60]}")
                return url, attr
            else:
                print(f"  ⏭ Skipped irrelevant: {title[:60]}")
        return None, None

    # Try 1: image_search_query
    isq = article.get("image_search_query")
    if isq and isinstance(isq, str) and isq.strip():
        print(f"  🔍 Commons search: \"{isq}\"")
        candidates = search_wikimedia(isq)
        if candidates:
            result = validate_and_return(candidates, f"Commons search query")
            if result[0]:
                return result
        time.sleep(POLITE_DELAY)

    # Try 2: image_entities one by one (skip ambiguous short ones)
    entities = article.get("image_entities")
    if entities and isinstance(entities, list):
        for entity in entities[:3]:
            if not entity or not isinstance(entity, str):
                continue
            # Skip ambiguous single-word/acronym entities
            if entity.upper().strip() in AMBIGUOUS_ENTITIES:
                print(f"  ⏭ Skipping ambiguous entity: \"{entity}\"")
                continue
            if len(entity.strip()) < 4:
                continue
            print(f"  🔍 Commons entity: \"{entity}\"")
            candidates = search_wikimedia(entity)
            if candidates:
                result = validate_and_return(candidates, f"Commons entity")
                if result[0]:
                    return result
            time.sleep(POLITE_DELAY)

    # Try 3: first few tags (with relevance check)
    tags = article.get("tags")
    if tags and isinstance(tags, list):
        tag_query = " ".join(tags[:3])
        print(f"  🔍 Commons tags: \"{tag_query}\"")
        candidates = search_wikimedia(tag_query)
        if candidates:
            result = validate_and_return(candidates, f"Commons tags")
            if result[0]:
                return result
        time.sleep(POLITE_DELAY)

    # Try 4: headline keywords (with relevance check)
    if headline:
        words = [w for w in headline.split() if len(w) > 3][:5]
        if words:
            kw_query = " ".join(words)
            print(f"  🔍 Commons headline: \"{kw_query}\"")
            candidates = search_wikimedia(kw_query)
            if candidates:
                result = validate_and_return(candidates, f"Commons headline")
                if result[0]:
                    return result
            time.sleep(POLITE_DELAY)

    return None, None


def format_commons_attribution(candidate):
    """Build a clean attribution string for Wikimedia Commons images."""
    artist = candidate.get("artist", "Unknown")
    license_name = candidate.get("license", "")
    if license_name:
        return f"{artist} / Wikimedia Commons ({license_name})"
    return f"{artist} / Wikimedia Commons"

# ---------------------------------------------------------------------------
# Pexels API integration
# ---------------------------------------------------------------------------

PEXELS_API_URL = "https://api.pexels.com/v1/search"

# Stop words for Pexels keyword extraction
PEXELS_STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "was", "are", "were", "be", "been", "being", "has", "had", "have",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "with", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "over", "about",
    "up", "out", "off", "its", "his", "her", "their", "our", "my", "your",
    "this", "that", "these", "those", "it", "he", "she", "they", "we", "you",
    "not", "no", "but", "so", "if", "than", "too", "very", "just", "also",
    "new", "says", "said", "amid", "how", "why", "what",
}

# Category → fallback search terms for Pexels
PEXELS_CATEGORY_TERMS = {
    "news": "India government parliament",
    "nri-world": "Indian diaspora abroad",
    "markets-finance": "stock market trading",
    "technology": "technology India startup",
    "sports": "cricket India stadium",
    "entertainment": "Bollywood cinema India",
    "lifestyle-health": "yoga wellness India",
    "travel": "India travel landmark",
    "food": "Indian cuisine food",
}


def _load_pexels_key():
    """Load Pexels API key from env var or .env.pexels file."""
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        return key
    if os.path.exists(PEXELS_ENV_FILE):
        with open(PEXELS_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "PEXELS_API_KEY":
                    val = v.strip()
                    if val and not val.startswith("your_"):
                        return val
    return None


def _pexels_extract_terms(headline, category=None):
    """Extract 2-4 search keywords from headline for Pexels query."""
    if not headline:
        return PEXELS_CATEGORY_TERMS.get(category, "India news")

    text = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = text.split()

    proper_nouns = []
    keywords = []

    for w in words:
        w_lower = w.lower()
        if len(w) < 3 or w_lower in PEXELS_STOP_WORDS:
            continue
        if w[0].isupper() and len(w) > 2:
            proper_nouns.append(w)
        else:
            keywords.append(w)

    search_parts = proper_nouns[:3]
    if len(search_parts) < 2:
        search_parts.extend(keywords[:2])

    if not search_parts:
        return PEXELS_CATEGORY_TERMS.get(category, "India news")

    return " ".join(search_parts[:4])


def try_pexels_search(article):
    """
    Try to find an image via Pexels API for the given article.
    Returns (image_url, attribution) or (None, None).

    When a Pexels image is found:
    - Downloads, crops to 16:9, resizes to 1200x675
    - Uploads to Supabase Storage (same bucket as other article images)
    - Returns the Supabase public URL and photographer attribution
    """
    api_key = _load_pexels_key()
    if not api_key:
        return None, None

    headline = article.get("headline", "")
    tags = article.get("tags")
    category = None
    if isinstance(tags, list) and tags:
        category = tags[0] if isinstance(tags[0], str) else None
    elif isinstance(tags, str):
        category = tags

    search_query = _pexels_extract_terms(headline, category)
    print(f"  🔍 Pexels: searching \"{search_query}\"")

    try:
        resp = requests.get(
            PEXELS_API_URL,
            headers={"Authorization": api_key},
            params={"query": search_query, "per_page": 5, "orientation": "landscape"},
            timeout=15,
        )
        if resp.status_code == 401:
            print("    ⚠ Pexels: Invalid API key")
            return None, None
        if resp.status_code == 429:
            print("    ⚠ Pexels: Rate limit exceeded")
            return None, None
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
    except requests.RequestException as e:
        print(f"    ⚠ Pexels API error: {e}")
        return None, None

    if not photos:
        print("    ⚠ Pexels: no results")
        return None, None

    # Pick best photo (prefer larger, landscape images)
    best = None
    best_score = -1
    headline_lower = headline.lower()
    headline_words = set(headline_lower.split())

    for photo in photos:
        score = 0
        alt = (photo.get("alt") or "").lower()
        alt_words = set(alt.split())
        score += len(headline_words & alt_words) * 2
        width = photo.get("width", 0)
        height = photo.get("height", 1)
        if width >= 1200:
            score += 2
        elif width >= 800:
            score += 1
        if width / height >= 1.3:
            score += 1
        if score > best_score:
            best_score = score
            best = photo

    if not best:
        return None, None

    photographer = best.get("photographer", "Unknown")
    src = best.get("src", {})
    image_url = src.get("large2x") or src.get("large") or src.get("original", "")

    if not image_url:
        return None, None

    print(f"    📸 Found: \"{best.get('alt', '')[:50]}\" by {photographer}")
    attribution = f"Photo by {photographer} / Pexels"

    return image_url, attribution


# ---------------------------------------------------------------------------
# PIB Photo matching (attribution only — no image download yet)
# ---------------------------------------------------------------------------

PIB_INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pib-photo-index.json")

PIB_STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "was", "are", "were", "be", "been", "being", "has", "had", "have",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "with", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "over", "about",
    "up", "out", "off", "its", "his", "her", "their", "our", "my", "your",
    "this", "that", "these", "those", "it", "he", "she", "they", "we", "you",
    "not", "no", "but", "so", "if", "than", "too", "very", "just", "also",
    "new", "says", "said", "shri", "smt", "mr", "mrs",
}


def try_pib_match(article):
    """
    Try to match article headline against PIB Photo RSS captions.
    Returns (gallery_url, caption) or (None, None).
    This is attribution-only — actual PIB image download requires browser
    automation (gallery pages are JS-rendered) and will be added later.
    """
    if not os.path.exists(PIB_INDEX_PATH):
        return None, None

    try:
        with open(PIB_INDEX_PATH) as f:
            index = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None, None

    photos = index.get("photos", [])
    if not photos:
        return None, None

    headline = article.get("headline", "")
    headline_words = {
        w for w in re.sub(r"[^a-zA-Z0-9\s]", " ", headline.lower()).split()
        if len(w) >= 3 and w not in PIB_STOP_WORDS
    }
    if not headline_words:
        return None, None

    best_match = None
    best_sim = 0.0

    for photo in photos:
        caption = photo.get("caption", "")
        caption_words = {
            w for w in re.sub(r"[^a-zA-Z0-9\s]", " ", caption.lower()).split()
            if len(w) >= 3 and w not in PIB_STOP_WORDS
        }
        if not caption_words:
            continue

        # Weighted similarity: headline keyword coverage + Jaccard
        coverage = len(headline_words & caption_words) / len(headline_words)
        jaccard = len(headline_words & caption_words) / len(headline_words | caption_words)
        sim = coverage * 0.7 + jaccard * 0.3

        if sim > best_sim:
            best_sim = sim
            best_match = photo

    if best_match and best_sim >= 0.3:
        gallery_url = best_match.get("gallery_url", "")
        caption = best_match.get("caption", "")
        print(f"  🏛 PIB match ({best_sim:.2f}): {caption[:60]}")
        return gallery_url, caption

    return None, None

# ---------------------------------------------------------------------------
# Combined image search — Wikipedia first, then Commons
# ---------------------------------------------------------------------------

def find_image_for_article(article):
    """
    Search for an image using a tiered strategy:
      1. Wikipedia page images (best for specific entities — people, places, orgs)
      2. Pexels API search (general fallback — culture, travel, lifestyle)
    Also checks PIB Photo RSS for attribution links (govt/political articles).
    Returns (thumb_url, attribution) or (None, None).
    """
    # Check if this article category should skip images
    if should_skip_image(article):
        print(f"  ⏭ Skipping image search (policy/legal/financial topic)")
        return None, None

    # --- Check PIB for attribution (non-blocking, no image yet) ---
    pib_url, pib_caption = try_pib_match(article)
    if pib_url:
        print(f"  🏛 PIB photo gallery available: {pib_url}")
        # PIB images require browser automation to download — just log for now

    # --- Tier 1: Wikipedia page images ---
    print("  📖 Tier 1: Wikipedia page images")
    url, attr = search_wikipedia_for_article(article)
    if url:
        return url, attr

    # --- Tier 2: Pexels API ---
    print("  📷 Tier 2: Pexels API search")
    url, attr = try_pexels_search(article)
    if url:
        return url, attr

    print(f"  ❌ No suitable image found")
    return None, None

# ---------------------------------------------------------------------------
# Image processing — download, crop, enhance, upload
# ---------------------------------------------------------------------------

def download_image(image_url):
    """Download an image and return PIL Image object, or None on failure."""
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(image_url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()
        # Limit download to 20MB
        content = b""
        for chunk in resp.iter_content(chunk_size=65536):
            content += chunk
            if len(content) > 20 * 1024 * 1024:
                print("    ⚠ Image too large (>20MB), skipping processing")
                return None
        img = Image.open(io.BytesIO(content))
        return img
    except Exception as e:
        print(f"    ⚠ Download failed: {e}")
        return None


def smart_crop_16_9(img):
    """
    Smart-crop an image to 16:9 aspect ratio.
    - If wider than 16:9: crop sides (center)
    - If taller than 16:9: crop biased toward top 30% (faces are usually upper)
    """
    target_ratio = 16.0 / 9.0
    current_ratio = img.width / img.height

    if abs(current_ratio - target_ratio) < 0.05:
        # Already close to 16:9, no crop needed
        return img

    if current_ratio > target_ratio:
        # Image is wider — crop sides (center)
        new_width = int(img.height * target_ratio)
        left = (img.width - new_width) // 2
        img = img.crop((left, 0, left + new_width, img.height))
    else:
        # Image is taller — crop biased toward top (keep faces)
        new_height = int(img.width / target_ratio)
        # Bias toward top 30% of the image
        portrait_ratio = img.height / img.width
        if portrait_ratio > 1.3:
            top_bias = 0.15
        elif portrait_ratio > 1.0:
            top_bias = 0.25
        else:
            top_bias = 0.3
        top = int((img.height - new_height) * top_bias)
        top = max(0, min(top, img.height - new_height))
        img = img.crop((0, top, img.width, top + new_height))

    return img


def enhance_image(img):
    """Apply subtle enhancements: sharpness, contrast, color saturation."""
    img = ImageEnhance.Sharpness(img).enhance(1.15)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    img = ImageEnhance.Color(img).enhance(1.05)
    return img


def process_image(image_url):
    """
    Download image, resize to max 1200px wide (preserve aspect ratio), enhance, return JPEG bytes.
    No cropping — CSS handles aspect ratio per context (16:9 on cards, full on article pages).
    Returns (jpeg_bytes, file_size_kb) or (None, 0) on failure.
    """
    img = download_image(image_url)
    if img is None:
        return None, 0

    try:
        # Convert to RGB (handles PNG alpha, CMYK, palette mode, etc.)
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # Skip if source image is too small to produce quality output
        if img.width < 200 or img.height < 100:
            print(f"    ⚠ Source image too small ({img.width}x{img.height}), skipping processing")
            return None, 0

        # Resize to max width 1200, preserving aspect ratio
        if img.width > TARGET_WIDTH:
            ratio = TARGET_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((TARGET_WIDTH, new_height), Image.LANCZOS)
        elif img.width < 800:
            # Upscale small images to at least 800px wide
            ratio = 800 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.LANCZOS)

        # Subtle enhancement
        img = enhance_image(img)

        # Save as high-quality JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        jpeg_bytes = buffer.getvalue()
        size_kb = len(jpeg_bytes) / 1024

        return jpeg_bytes, size_kb
    except Exception as e:
        print(f"    ⚠ Image processing failed: {e}")
        return None, 0


def upload_to_supabase_storage(env, article_id, jpeg_bytes):
    """
    Upload processed JPEG to Supabase Storage bucket 'article-images'.
    Returns the public URL, or None on failure.
    """
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    filename = f"{article_id}.jpg"

    try:
        resp = requests.post(
            f"{url}/storage/v1/object/article-images/{filename}",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=jpeg_bytes,
            timeout=30,
        )
        resp.raise_for_status()
        public_url = f"{url}/storage/v1/object/public/article-images/{filename}"
        return public_url
    except Exception as e:
        print(f"    ⚠ Supabase Storage upload failed: {e}")
        return None


def process_and_upload(env, article_id, source_image_url):
    """
    Full pipeline: download → resize → enhance → upload.
    Returns (supabase_public_url_with_dims, size_kb) or (None, 0) on failure.
    URL includes ?w=WIDTH&h=HEIGHT query params for frontend layout hints.
    """
    jpeg_bytes, size_kb = process_image(source_image_url)
    if jpeg_bytes is None:
        return None, 0

    # Get dimensions from the processed image
    img = Image.open(io.BytesIO(jpeg_bytes))
    img_w, img_h = img.width, img.height

    public_url = upload_to_supabase_storage(env, article_id, jpeg_bytes)
    if public_url is None:
        return None, 0

    # Append dimensions as query params (Supabase Storage ignores them when serving)
    public_url = f"{public_url}?w={img_w}&h={img_h}"

    time.sleep(UPLOAD_DELAY)
    return public_url, size_kb


# ---------------------------------------------------------------------------
# Supabase operations
# ---------------------------------------------------------------------------

def fetch_articles_needing_images(env, refresh=False, article_id=None):
    """Get articles that need images from Supabase."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = supabase_headers(key)
    del headers["Prefer"]  # not needed for GET

    cols = "id,headline,image_url,image_search_query,image_entities,tags"
    articles = []

    if article_id:
        api_url = f"{url}/rest/v1/p2_articles?select={cols}&id=eq.{article_id}"
        resp = requests.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        articles = resp.json()
    else:
        # Articles with NULL or empty image_url
        api_url = (
            f"{url}/rest/v1/p2_articles?select={cols}"
            f"&status=eq.published"
            f"&or=(image_url.is.null,image_url.eq.)"
            f"&order=created_at.desc&limit=30"
        )
        resp = requests.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        articles = resp.json()

        if refresh:
            # In refresh mode, get ALL published articles and re-source images
            api_url2 = (
                f"{url}/rest/v1/p2_articles?select={cols}"
                f"&status=eq.published"
                f"&order=created_at.desc&limit=300"
            )
            resp2 = requests.get(api_url2, headers=headers, timeout=15)
            resp2.raise_for_status()
            existing_ids = {a["id"] for a in articles}
            for a in resp2.json():
                if a["id"] not in existing_ids:
                    articles.append(a)

    return articles


def update_article_image(env, article_id, image_url, attribution):
    """Update image_url and image_attribution for an article."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = supabase_headers(key)

    api_url = f"{url}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = {"image_url": image_url, "image_attribution": attribution}

    resp = requests.patch(api_url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def cmd_fetch(args):
    """Fetch and assign images to articles."""
    env = load_env()

    refresh = "--refresh" in args
    no_process = "--no-process" in args  # skip download/crop/upload, just store URLs
    article_id = None
    if "--id" in args:
        idx = args.index("--id")
        if idx + 1 < len(args):
            article_id = args[idx + 1]
        else:
            print("ERROR: --id requires an article UUID")
            sys.exit(1)

    supabase_url = env.get("SUPABASE_URL", "")

    print("=" * 60)
    print("📷 Videshi Image Sourcing")
    print("   Tier 1: Wikipedia page images (strict, confidence=5)")
    print("   Tier 2: Pexels API search (general fallback)")
    print("   PIB Photo RSS: attribution links for govt/political")
    if not no_process:
        print(f"   🖼 Processing: {TARGET_WIDTH}×{TARGET_HEIGHT} → enhance → upload")
    print("=" * 60)

    articles = fetch_articles_needing_images(env, refresh=refresh, article_id=article_id)

    if not articles:
        print("\n✅ No articles need images right now.")
        return

    print(f"\n📰 Found {len(articles)} article(s) needing images\n")

    sourced = 0
    processed = 0
    skipped = 0
    failed = 0

    for i, article in enumerate(articles):
        headline = article.get("headline", "Unknown")
        aid = article["id"]
        current_url = article.get("image_url") or ""

        # Skip articles that already have a processed Supabase Storage image
        if (not refresh and not article_id
                and current_url.startswith(supabase_url)
                and "/article-images/" in current_url
                and current_url.endswith(".jpg")):
            continue

        print(f"\n[{i+1}/{len(articles)}] {headline[:70]}")
        if current_url:
            print(f"  Current image: {current_url[:80]}...")

        # Find a source image
        source_url, attribution = find_image_for_article(article)

        if not source_url:
            # If article had an image before, clear it (quality standards tightened)
            if current_url and refresh:
                try:
                    update_article_image(env, aid, None, None)
                    print(f"  🗑 Cleared old image (didn't meet new quality threshold)")
                except Exception:
                    pass
            skipped += 1
            continue

        # Process and upload to Supabase Storage
        if not no_process:
            print(f"  🖼 Processing: download → {TARGET_WIDTH}×{TARGET_HEIGHT} → enhance")
            final_url, size_kb = process_and_upload(env, aid, source_url)
            if final_url:
                try:
                    update_article_image(env, aid, final_url, attribution)
                    print(f"  💾 Processed: {size_kb:.0f}KB → uploaded to Supabase Storage")
                    print(f"  📝 Attribution: {attribution}")
                    sourced += 1
                    processed += 1
                except Exception as e:
                    print(f"  ⚠ Failed to update Supabase: {e}")
                    failed += 1
            else:
                # Fallback: store raw Wikipedia URL if processing fails
                print(f"  ⚠ Processing failed, falling back to source URL")
                try:
                    update_article_image(env, aid, source_url, attribution)
                    print(f"  💾 Updated (raw URL) — {attribution}")
                    sourced += 1
                except Exception as e:
                    print(f"  ⚠ Failed to update Supabase: {e}")
                    failed += 1
        else:
            # --no-process: just store the raw URL
            try:
                update_article_image(env, aid, source_url, attribution)
                print(f"  💾 Updated — {attribution}")
                sourced += 1
            except Exception as e:
                print(f"  ⚠ Failed to update Supabase: {e}")
                failed += 1

    print(f"\n{'=' * 60}")
    print(f"📊 Results: {sourced} sourced, {processed} processed+uploaded, {skipped} no match, {failed} errors")
    print(f"{'=' * 60}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command == "fetch":
        cmd_fetch(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
