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
    """Check if an image result is actually relevant to the article."""
    title = (result.get("title", "") or "").lower()
    headline_lower = headline.lower()
    subject_lower = (subject or "").lower()

    # Skip obvious junk: book scans, documents, SVGs, logos
    junk_patterns = [".djvu", "notes and queries", "volume ", "series ", "hitty"]
    if any(j in title for j in junk_patterns):
        return False

    # For named subjects, check if result title contains any part of the subject
    if subject_lower:
        parts = [p for p in subject_lower.split() if len(p) > 2]
        if parts and any(p in title for p in parts):
            return True

    # Check headline keyword overlap (at least 2 significant words)
    headline_words = {w.lower() for w in headline.split() if len(w) > 3}
    title_words = {w.lower() for w in title.split() if len(w) > 3}
    overlap = headline_words & title_words
    if len(overlap) >= 2:
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

                if all(word in headline_lower for word in significant):
                    matches.append({
                        "name": name,
                        "handle": handle,
                        "category": category,
                        "platform": platform,
                    })

    return matches


def search_instagram_posts(handle, topic_keywords, limit=3):
    """Search for relevant Instagram posts via web search."""
    # Use browser search to find Instagram posts
    query = f"site:instagram.com @{handle} {' '.join(topic_keywords[:3])}"
    try:
        r = _session.get(
            "https://www.google.com/search",
            params={"q": query, "num": 5},
            headers={"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"},
            timeout=10,
        )
        # Extract Instagram post URLs
        urls = re.findall(r'https://www\.instagram\.com/p/([A-Za-z0-9_-]+)', r.text)
        return list(dict.fromkeys(urls))[:limit]  # unique, preserve order
    except:
        return []


def article_has_social_embed(body, platform):
    """Check if article body already has a social embed."""
    if platform == "instagram":
        return bool(re.search(r'instagram\.com/(?:p|reel|tv)/', body or ""))
    elif platform in ("twitter", "x"):
        return bool(re.search(r'(?:twitter|x)\.com/\w+/status/', body or ""))
    elif platform == "youtube":
        return bool(re.search(r'<youtube>.*?</youtube>', body or ""))
    return False


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


def extract_entities(headline, body):
    """Extract notable entities (people, places, orgs) from headline + first few paragraphs.
    Returns a list of (entity, context_sentence) tuples, most important first."""
    text = headline + "\n\n" + "\n\n".join(body.split("\n\n")[:4])

    entities = []
    seen = set()

    # Pattern 1: Capitalized multi-word names (most likely people/places/orgs)
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+(?:(?:de|von|van|al|el|bin|the|of)\s+)?[A-Z][a-z]+){1,3})\b', text):
        name = m.group(1).strip()
        if name.lower() in _SKIP_ENTITIES or len(name) < 4:
            continue
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(name)

    # Pattern 2: Known place patterns
    for m in re.finditer(r'\b(New Delhi|Washington D\.?C\.?|Silicon Valley|Wall Street|Bollywood|Hollywood|Mumbai|Chennai|Hyderabad|Bangalore|Bengaluru)\b', text, re.IGNORECASE):
        name = m.group(1).strip()
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(name)

    return entities[:6]  # limit to top 6 candidates


def find_inline_images(headline, body, hero_url=""):
    """Find up to 3 inline Wikipedia images for entities in the article.
    Returns list of (entity, image_url, caption) tuples."""
    entities = extract_entities(headline, body)
    results = []
    hero_norm = (hero_url or "").split("?")[0].lower()

    for entity in entities:
        if len(results) >= 3:
            break

        img_url = fetch_wikipedia_image(entity)
        if not img_url:
            continue

        # Skip if same as hero image
        if hero_norm and img_url.split("?")[0].lower() == hero_norm:
            continue

        # Skip SVGs and tiny images
        if img_url.endswith(".svg") or img_url.endswith(".png"):
            continue

        caption = f"{entity} — Photo: Wikimedia Commons"
        results.append((entity, img_url, caption))
        print(f"    ✓ Inline image for '{entity}'")

    return results


def insert_inline_images(body, images):
    """Insert inline images at natural break points in the article body.
    Places images between paragraphs, spaced evenly through the article."""
    if not images:
        return body

    paragraphs = body.split("\n\n")
    if len(paragraphs) < 3:
        return body

    # Calculate insertion points — evenly spaced, skip first paragraph
    n_images = len(images)
    # Space them out: after paragraph 2, 4, 6, etc.
    step = max(2, (len(paragraphs) - 1) // (n_images + 1))
    insert_points = []
    pos = step
    for img in images:
        if pos >= len(paragraphs):
            pos = len(paragraphs) - 1
        insert_points.append(pos)
        pos += step

    # Insert in reverse order so indices stay valid
    for i, (entity, url, caption) in reversed(list(zip(range(len(images)), *zip(*[(e, u, c) for e, u, c in images])))):
        if i < len(insert_points):
            idx = insert_points[i]
            img_md = f"\n\n![{caption}]({url})\n"
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

    quote_block = f'\n\n> **"{quote.strip()}"**\n'
    paragraphs.insert(insert_at, quote_block)

    return "\n\n".join(paragraphs)


def article_has_inline_images(body):
    """Check if article body already has inline markdown images."""
    # Count actual inline images (not social embeds or tracking pixels)
    imgs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', body or "")
    return len(imgs) > 0


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

    r = _session.get(f"{SUPABASE_URL}/rest/v1/p2_articles", params=params, headers=HEADERS, timeout=30)
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
                if apply:
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

        # Instagram embed enrichment for entertainment
        print("\n══ Instagram Embed Enrichment ══")
        ent_articles = get_recent_articles(hours=args.hours, category="entertainment")
        print(f"Found {len(ent_articles)} entertainment articles")

        ig_enriched = 0
        for article in ent_articles[:args.max]:
            if article_has_social_embed(article.get("body", ""), "instagram"):
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
                        # Insert after first paragraph
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
