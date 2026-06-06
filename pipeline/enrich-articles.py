#!/usr/bin/env python3
"""
Article enrichment pipeline:
1. Replace generic Pexels hero images with better CC-licensed images (Openverse + Wikimedia Commons)
2. Add Instagram embeds for entertainment articles with matching celebrity handles
3. Add X/Twitter embeds for articles with matching registry handles (calls tweet-enricher)

Usage:
  python3 enrich-articles.py --hours 24 --dry-run    # preview changes
  python3 enrich-articles.py --hours 24 --apply       # apply changes
  python3 enrich-articles.py --images-only --apply     # only fix images
  python3 enrich-articles.py --embeds-only --apply     # only add embeds
"""

import os, sys, json, re, time, argparse, subprocess
import requests
from urllib.parse import quote

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    return False


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
    parser.add_argument("--max", type=int, default=10, help="Max articles to enrich per run")
    args = parser.parse_args()

    apply = args.apply and not args.dry_run
    registry = load_registry()

    # ── 1. IMAGE ENRICHMENT ──
    if not args.embeds_only:
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

    # ── 2. SOCIAL EMBED ENRICHMENT ──
    if not args.images_only:
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

    print("\n✅ Enrichment complete!")


if __name__ == "__main__":
    main()
