#!/usr/bin/env python3
"""
Image sourcing executor for The Videshi.
Takes structured instructions from the LLM agent and fetches images.

The LLM agent analyzes each article and tells this script EXACTLY what to do:
  - Which Wikipedia page to check
  - What search queries to use
  - What the ideal image should show
  - What caption to use

Usage:
  # Fetch from Wikipedia person page
  python3 source-image.py --article-id UUID --wikipedia "Ajay_Devgn" --caption "Ajay Devgn (Wikimedia Commons)" --apply

  # Fetch from Wikipedia season page
  python3 source-image.py --article-id UUID --wikipedia "House_of_the_Dragon_season_3" --caption "HOTD S3 poster (Wikipedia)" --apply

  # Search Wikimedia Commons
  python3 source-image.py --article-id UUID --commons "Ajay Devgn film premiere" --caption "Ajay Devgn at a premiere" --apply

  # Try multiple sources in order (first match wins)
  python3 source-image.py --article-id UUID \
    --wikipedia "Ajay_Devgn" \
    --commons "Ajay Devgn 2024" \
    --openverse "Ajay Devgn actor" \
    --caption "Ajay Devgn (Wikimedia Commons)" \
    --apply

  # YouTube trailer
  python3 source-image.py --article-id UUID --trailer "Drishyam 3 Hindi official trailer" --apply

  # Just check what the current image is
  python3 source-image.py --article-id UUID --check

  # Batch mode: read JSON instructions from stdin
  echo '[{"article_id":"UUID","wikipedia":"Ajay_Devgn","caption":"..."}]' | python3 source-image.py --batch --apply
"""

import os, sys, json, re, argparse, time
import requests
from urllib.parse import quote, quote_plus

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
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}


# ═══════════════════════════════════════════
# FETCH FUNCTIONS — each returns (url, attribution) or (None, None)
# ═══════════════════════════════════════════

def fetch_wikipedia(page_name):
    """Fetch main image from a Wikipedia page by exact page name."""
    encoded = quote(page_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = (data.get("originalimage", {}).get("source")
                   or data.get("thumbnail", {}).get("source"))
            if img:
                print(f"  ✓ Wikipedia [{page_name}]: {img[:100]}")
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia error [{page_name}]: {e}")
    print(f"  ✗ Wikipedia [{page_name}]: no image found")
    return None, None


def fetch_commons(query):
    """Search Wikimedia Commons for CC images."""
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "generator": "search",
                "gsrsearch": query, "gsrnamespace": "6", "gsrlimit": "5",
                "prop": "imageinfo", "iiprop": "url|size|mime",
                "iiurlwidth": "1200", "format": "json",
            },
            headers=UA, timeout=15,
        )
        if r.status_code != 200:
            return None, None
        pages = r.json().get("query", {}).get("pages", {})
        for pid, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            w = ii.get("width", 0)
            if w < 400:
                continue
            url = ii.get("thumburl") or ii.get("url", "")
            if url:
                print(f"  ✓ Commons [{query}]: {url[:100]}")
                return url, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Commons error [{query}]: {e}")
    print(f"  ✗ Commons [{query}]: no image found")
    return None, None


def fetch_openverse(query):
    """Search Openverse for CC-licensed images."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "license": "by,by-sa,by-nd,pdm,cc0", "page_size": 5},
            timeout=15,
        )
        if r.status_code != 200:
            return None, None
        for item in r.json().get("results", []):
            if item.get("width", 0) >= 400:
                url = item.get("url", "")
                if url:
                    print(f"  ✓ Openverse [{query}]: {url[:100]}")
                    return url, "Openverse"
    except Exception as e:
        print(f"  ⚠ Openverse error [{query}]: {e}")
    print(f"  ✗ Openverse [{query}]: no image found")
    return None, None


def fetch_google_cse(query, cc_only=True):
    """Search Google CSE for images (when API is enabled)."""
    cse_key = os.environ.get("GOOGLE_CSE_KEY", "")
    cse_id = os.environ.get("GOOGLE_CSE_ID", "")
    if not cse_key or not cse_id:
        return None, None
    params = {
        "key": cse_key, "cx": cse_id, "q": query,
        "searchType": "image", "num": 5,
    }
    if cc_only:
        params["rights"] = "cc_publicdomain|cc_attribute|cc_sharealike"
    try:
        r = requests.get("https://www.googleapis.com/customsearch/v1",
                         params=params, timeout=10)
        if r.status_code == 200:
            items = r.json().get("items", [])
            if items:
                url = items[0]["link"]
                print(f"  ✓ Google CSE [{query}]: {url[:100]}")
                return url, "Google CSE"
    except Exception as e:
        print(f"  ⚠ Google CSE error [{query}]: {e}")
    return None, None


def fetch_youtube_trailer(query):
    """Search YouTube for a trailer via page scrape."""
    try:
        url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', r.text)
        titles = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}', r.text)
        seen = set()
        results = []
        for i, vid in enumerate(video_ids):
            if vid not in seen:
                seen.add(vid)
                title = titles[i] if i < len(titles) else ""
                results.append({"id": vid, "title": title})
            if len(results) >= 5:
                break
        # Prefer trailer/official
        for item in results:
            tl = item["title"].lower()
            if "trailer" in tl or "official" in tl:
                yt = f"https://youtube.com/watch?v={item['id']}"
                print(f"  ✓ YouTube trailer: {yt} ({item['title'][:60]})")
                return yt
        if results:
            yt = f"https://youtube.com/watch?v={results[0]['id']}"
            print(f"  ✓ YouTube video: {yt} ({results[0]['title'][:60]})")
            return yt
    except Exception as e:
        print(f"  ⚠ YouTube error [{query}]: {e}")
    print(f"  ✗ YouTube [{query}]: no video found")
    return None


# ═══════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════

def validate_image_url(url):
    """Check that the URL returns a real image (not a 404 or tiny placeholder)."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if not ct.startswith("image/"):
            print(f"  ⚠ Validation: not an image ({ct})")
            return False
        if cl > 0 and cl < 5000:
            print(f"  ⚠ Validation: too small ({cl} bytes)")
            return False
        return True
    except Exception:
        return True  # If HEAD fails, let it through — might still work


# ═══════════════════════════════════════════
# APPLY TO ARTICLE
# ═══════════════════════════════════════════

def get_article(article_id):
    """Fetch article from Supabase."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}&select=id,headline,image_url,image_caption,image_attribution,body",
        headers=HEADERS, timeout=10,
    )
    data = r.json()
    return data[0] if data else None


def update_article_image(article_id, image_url, caption, attribution, dry_run=True):
    """Update article hero image."""
    if dry_run:
        print(f"  [DRY RUN] Would update image to: {image_url[:80]}")
        print(f"  [DRY RUN] Caption: {caption}")
        return True
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        json={
            "image_url": image_url,
            "image_caption": caption,
            "image_attribution": attribution,
        },
        headers=HEADERS, timeout=15,
    )
    if r.status_code == 204:
        print(f"  ✅ Image updated!")
        return True
    print(f"  ❌ Update failed: {r.status_code} {r.text[:100]}")
    return False


def embed_trailer(article_id, trailer_url, dry_run=True):
    """Add YouTube trailer embed to article body."""
    article = get_article(article_id)
    if not article:
        print(f"  ❌ Article not found")
        return False
    body = article.get("body", "")
    if "<youtube>" in body:
        print(f"  ℹ Already has a YouTube embed, skipping")
        return False

    # Insert after first paragraph
    tag = f"\n\n<youtube>{trailer_url}</youtube>\n"
    paras = body.split("\n\n", 1)
    if len(paras) >= 2:
        new_body = paras[0] + tag + "\n" + paras[1]
    else:
        new_body = body + tag

    if dry_run:
        print(f"  [DRY RUN] Would embed trailer: {trailer_url}")
        return True

    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        json={"body": new_body},
        headers=HEADERS, timeout=15,
    )
    if r.status_code == 204:
        print(f"  ✅ Trailer embedded!")
        return True
    print(f"  ❌ Embed failed: {r.status_code}")
    return False


# ═══════════════════════════════════════════
# PROCESS ONE ARTICLE'S INSTRUCTIONS
# ═══════════════════════════════════════════

def process_instruction(instr, apply=False):
    """
    Process one instruction dict from the LLM agent.
    Fields:
      article_id (required)
      wikipedia: Wikipedia page name to check
      commons: Wikimedia Commons search query
      openverse: Openverse search query
      google: Google CSE search query
      caption: desired caption text
      attribution: image attribution (default: "Wikimedia Commons")
      trailer: YouTube trailer search query
    Sources are tried in the order: wikipedia → commons → openverse → google
    """
    aid = instr.get("article_id", "")
    if not aid:
        print("  ❌ No article_id provided")
        return

    article = get_article(aid)
    if not article:
        print(f"  ❌ Article {aid} not found")
        return

    print(f"\n{'─'*60}")
    print(f"  📰 {article['headline'][:80]}")
    print(f"  Current image: {(article.get('image_url') or 'none')[:80]}")

    # Image sourcing — try sources in order
    image_url = None
    attribution = instr.get("attribution", "Wikimedia Commons")

    sources = []
    if instr.get("wikipedia"):
        sources.append(("wikipedia", instr["wikipedia"]))
    if instr.get("commons"):
        sources.append(("commons", instr["commons"]))
    if instr.get("openverse"):
        sources.append(("openverse", instr["openverse"]))
    if instr.get("google"):
        sources.append(("google", instr["google"]))

    for source_type, query in sources:
        if source_type == "wikipedia":
            image_url, attr = fetch_wikipedia(query)
        elif source_type == "commons":
            image_url, attr = fetch_commons(query)
        elif source_type == "openverse":
            image_url, attr = fetch_openverse(query)
        elif source_type == "google":
            image_url, attr = fetch_google_cse(query)

        if image_url and validate_image_url(image_url):
            attribution = attr or attribution
            break
        image_url = None
        time.sleep(0.3)

    if image_url:
        caption = instr.get("caption", f"{article['headline'][:50]} ({attribution})")
        update_article_image(aid, image_url, caption, attribution, dry_run=not apply)
    elif sources:
        print(f"  ✗ No suitable image found from any source")

    # Trailer embedding
    if instr.get("trailer"):
        trailer_url = fetch_youtube_trailer(instr["trailer"])
        if trailer_url:
            embed_trailer(aid, trailer_url, dry_run=not apply)

    # Check-only mode
    if instr.get("check_only"):
        print(f"  Image URL: {article.get('image_url', 'none')}")
        print(f"  Caption: {article.get('image_caption', 'none')}")
        print(f"  Attribution: {article.get('image_attribution', 'none')}")


# ═══════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Image sourcing executor for The Videshi")
    parser.add_argument("--article-id", help="Article UUID")
    parser.add_argument("--wikipedia", help="Wikipedia page name (e.g. 'Ajay_Devgn')")
    parser.add_argument("--commons", help="Wikimedia Commons search query")
    parser.add_argument("--openverse", help="Openverse search query")
    parser.add_argument("--google", help="Google CSE search query")
    parser.add_argument("--caption", help="Image caption text")
    parser.add_argument("--attribution", default="Wikimedia Commons", help="Image attribution")
    parser.add_argument("--trailer", help="YouTube trailer search query")
    parser.add_argument("--check", action="store_true", help="Just show current image info")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--batch", action="store_true", help="Read JSON instructions from stdin")
    args = parser.parse_args()

    if args.batch:
        instructions = json.loads(sys.stdin.read())
        if isinstance(instructions, dict):
            instructions = [instructions]
        print(f"Processing {len(instructions)} articles...")
        for instr in instructions:
            process_instruction(instr, apply=args.apply)
        return

    if not args.article_id:
        parser.error("--article-id is required (or use --batch)")

    instr = {"article_id": args.article_id}
    if args.wikipedia:
        instr["wikipedia"] = args.wikipedia
    if args.commons:
        instr["commons"] = args.commons
    if args.openverse:
        instr["openverse"] = args.openverse
    if args.google:
        instr["google"] = args.google
    if args.caption:
        instr["caption"] = args.caption
    if args.attribution:
        instr["attribution"] = args.attribution
    if args.trailer:
        instr["trailer"] = args.trailer
    if args.check:
        instr["check_only"] = True

    process_instruction(instr, apply=args.apply)


if __name__ == "__main__":
    main()
