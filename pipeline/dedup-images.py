#!/usr/bin/env python3
"""
Image dedup scanner for The Videshi.

Usage:
  python3 dedup-images.py              # scan & report duplicates (last 7 days)
  python3 dedup-images.py --fix        # scan, report, and attempt to replace dupes with alt images
  python3 dedup-images.py --days 14    # scan last 14 days
  python3 dedup-images.py --all        # scan all published articles
"""

import json, os, sys, re, urllib.request, urllib.parse, time, subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# ── Config ──
# Load .env files if env vars not set
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip().lstrip("export ")
                    v = v.strip().strip("'\"")
                    if k and not os.environ.get(k):
                        os.environ[k] = v

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

USER_AGENT = "TheVideshi/1.0 (https://thevideshi.com; editorial image pipeline)"


def supabase_get(path):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    result = subprocess.run(
        ["curl", "-s", url, "-H", f"apikey: {SUPABASE_KEY}", "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    # Supabase returns a list for selects; handle error dicts
    if isinstance(data, dict) and "message" in data:
        print(f"Supabase error: {data}")
        return []
    return data if isinstance(data, list) else []


def supabase_patch(table, filter_str, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}"
    body = json.dumps(data)
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}", "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json", "-d", body],
        capture_output=True, text=True, timeout=30
    )
    return int(result.stdout.strip())


def wiki_images_for_person(person_name):
    """Get alternative image URLs from Wikipedia for a person."""
    # Search Wikipedia for the person's page
    search_url = (
        f"https://en.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(person_name)}&srlimit=1&format=json"
    )
    req = urllib.request.Request(search_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    results = data.get("query", {}).get("search", [])
    if not results:
        return []

    title = results[0]["title"]

    # Get images from their Wikipedia page
    img_url = (
        f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}"
        f"&prop=images&format=json&imlimit=30"
    )
    req = urllib.request.Request(img_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    pages = data.get("query", {}).get("pages", {})
    image_titles = []
    for pid, page in pages.items():
        for img in page.get("images", []):
            t = img["title"]
            # Only keep actual photos (jpg/jpeg/png), skip SVGs, logos, flags
            if re.search(r"\.(jpg|jpeg|png)$", t, re.I):
                tl = t.lower()
                # Skip obviously irrelevant files
                if any(skip in tl for skip in ["flag", "seal", "logo", "icon", "map", "signature", "coat_of_arms"]):
                    continue
                image_titles.append(t)

    if not image_titles:
        return []

    # Get actual URLs for these images (batch up to 10)
    batch = image_titles[:10]
    titles_str = "|".join(batch)
    info_url = (
        f"https://en.wikipedia.org/w/api.php?action=query"
        f"&titles={urllib.parse.quote(titles_str)}&prop=imageinfo&iiprop=url&format=json"
    )
    req = urllib.request.Request(info_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    urls = []
    pages = data.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        for ii in page.get("imageinfo", []):
            url = ii.get("url", "")
            if url:
                urls.append(url)

    return urls


def pexels_search(query, per_page=5):
    """Search Pexels for images. Returns list of URLs."""
    if not PEXELS_KEY:
        return []
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    return [p["src"]["large"] for p in data.get("photos", [])]


def extract_person_from_headline(headline):
    """Try to extract a person's name from a headline for image search."""
    # Common patterns: "X Just Did Y", "X's Z", "X Is Doing Y"
    # Simple heuristic: take first 2-3 capitalized words
    words = headline.split()
    name_words = []
    for w in words:
        clean = re.sub(r"[''']s$", "", w)  # strip possessive
        if clean and clean[0].isupper() and clean.isalpha() and len(clean) > 1:
            name_words.append(clean)
            if len(name_words) >= 3:
                break
        elif name_words:
            break

    if len(name_words) >= 2:
        return " ".join(name_words)
    return None


def main():
    fix_mode = "--fix" in sys.argv
    scan_all = "--all" in sys.argv
    days = 7
    for i, arg in enumerate(sys.argv):
        if arg == "--days" and i + 1 < len(sys.argv):
            days = int(sys.argv[i + 1])

    # Build query
    select = "id,headline,slug,image_url,published_at,image_entities"
    query = f"p2_articles?select={select}&status=eq.published&order=published_at.desc"
    if not scan_all:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        query += f"&published_at=gte.{cutoff}"
    query += "&limit=1000"

    articles = supabase_get(query)
    print(f"Scanned {len(articles)} published articles")

    # Group by image_url
    by_url = defaultdict(list)
    for a in articles:
        url = a.get("image_url", "")
        if url:
            by_url[url].append(a)

    dups = {url: arts for url, arts in by_url.items() if len(arts) > 1}
    print(f"Found {len(dups)} duplicate image URLs affecting {sum(len(v) for v in dups.values())} articles")
    print()

    if not dups:
        print("✅ No duplicate images found!")
        return

    all_used_urls = set(by_url.keys())
    fixed = 0
    failed = 0

    for url, arts in sorted(dups.items(), key=lambda x: -len(x[1])):
        # Keep the most recent article's image, try to replace older ones
        arts_sorted = sorted(arts, key=lambda a: a.get("published_at", ""), reverse=True)
        keeper = arts_sorted[0]
        to_fix = arts_sorted[1:]

        print(f"🔁 {len(arts)}x: {url[:70]}...")
        print(f"  KEEP: [{keeper['published_at'][:10]}] {keeper['headline'][:60]}")

        for a in to_fix:
            print(f"  DUPE: [{a['published_at'][:10]}] {a['headline'][:60]}")

            if not fix_mode:
                continue

            # Try to find an alternative image
            person = extract_person_from_headline(a["headline"])
            alt_url = None

            if person:
                # Try Wikipedia first
                wiki_urls = wiki_images_for_person(person)
                for wu in wiki_urls:
                    if wu != url and wu not in all_used_urls:
                        alt_url = wu
                        break

                # Fallback to Pexels
                if not alt_url and PEXELS_KEY:
                    # Get entities from the article for better search
                    entities = a.get("image_entities") or person
                    pexels_urls = pexels_search(f"{entities} portrait")
                    for pu in pexels_urls:
                        if pu not in all_used_urls:
                            alt_url = pu
                            break

            if alt_url:
                try:
                    status = supabase_patch(
                        "p2_articles",
                        f"id=eq.{a['id']}",
                        {"image_url": alt_url},
                    )
                    if status in (200, 204):
                        all_used_urls.add(alt_url)
                        fixed += 1
                        print(f"    ✅ Replaced with: {alt_url[:70]}...")
                    else:
                        failed += 1
                        print(f"    ❌ Patch failed: HTTP {status}")
                except Exception as e:
                    failed += 1
                    print(f"    ❌ Error: {e}")
                time.sleep(0.3)  # rate limit
            else:
                failed += 1
                print(f"    ⚠️  No alternative found for '{person or 'unknown'}'")

        print()

    if fix_mode:
        print(f"Results: {fixed} fixed, {failed} could not be fixed")
    else:
        print("Run with --fix to attempt automatic replacement of duplicate images")


if __name__ == "__main__":
    main()
