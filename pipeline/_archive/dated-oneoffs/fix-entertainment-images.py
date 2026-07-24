#!/usr/bin/env python3
"""Fix images for the 3 entertainment articles — use home .env.supabase key."""

import os, io, urllib.parse, requests
from PIL import Image

# Load only home env first (has valid JWT)
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)  # setdefault so first wins

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = "TheVideshi/1.0 (thevideshi.com)"

print(f"Key length: {len(SB_KEY)} (should be 219)")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def download_compress_upload(image_url, slug):
    """Download, compress, upload. Returns public URL or None."""
    try:
        r = requests.get(image_url, headers={"User-Agent": UA}, timeout=15)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code})")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Too small ({len(r.content)} bytes)")
            return None

        compressed = compress_image(r.content)
        filename = f"{slug}.jpg"
        print(f"  → Uploading {filename} ({len(compressed)} bytes)...")

        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers={
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true"
            },
            data=compressed,
            timeout=20
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url[:80]}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({up.status_code}): {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia: {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error: {e}")
    return None


def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": query,
        "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                results.append(ii.get("thumburl") or ii.get("url", ""))
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []


def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": 3, "orientation": "landscape"},
                         headers={"Authorization": PEXELS_KEY}, timeout=10)
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def update_article_image(slug, image_url, attribution):
    """Patch article with image."""
    r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}",
        headers=HEADERS,
        json={"image_url": image_url, "image_attribution": attribution},
        timeout=10
    )
    if r.status_code in (200, 204):
        print(f"  ✓ Article updated with image: {slug}")
    else:
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:200]}")


# ── Image tasks ──

tasks = [
    {
        "slug": "imax-returns-hyderabad-amb-cinemas-mahesh-babu-varanasi-nri-20260603",
        "persons": ["Mahesh Babu"],
        "commons_queries": ["IMAX Hyderabad cinema", "AMB Cinemas Hyderabad"],
        "pexels_query": "IMAX cinema theater premium"
    },
    {
        "slug": "drishyam-3-hindi-wraps-shoot-ajay-devgn-october-2-jaideep-ahlawat-nri-20260603",
        "persons": ["Ajay Devgn"],
        "commons_queries": ["Ajay Devgn actor", "Drishyam film"],
        "pexels_query": "Indian cinema suspense thriller"
    },
    {
        "slug": "jee-le-zaraa-farhan-akhtar-priyanka-alia-katrina-road-trip-nri-20260603",
        "persons": ["Farhan Akhtar", "Priyanka Chopra"],
        "commons_queries": ["Jee Le Zaraa Bollywood", "Farhan Akhtar filmmaker"],
        "pexels_query": "Rajasthan desert road trip India"
    }
]

import time

for task in tasks:
    slug = task["slug"]
    print(f"\n{'='*50}")
    print(f"Image for: {slug[:50]}...")
    print(f"{'='*50}")

    uploaded = None
    attr = None

    # Try Wikipedia person images
    for name in task["persons"]:
        img = fetch_wikipedia_person_image(name)
        if img:
            uploaded = download_compress_upload(img, slug)
            if uploaded:
                attr = "Wikimedia Commons"
                break
        time.sleep(1)

    # Try Wikimedia Commons
    if not uploaded:
        for q in task["commons_queries"]:
            results = fetch_wikimedia_commons(q, limit=3)
            for url in results:
                uploaded = download_compress_upload(url, slug)
                if uploaded:
                    attr = "Wikimedia Commons"
                    break
            if uploaded:
                break
            time.sleep(1)

    # Try Pexels
    if not uploaded:
        img = fetch_pexels(task["pexels_query"])
        if img:
            uploaded = download_compress_upload(img, slug)
            if uploaded:
                attr = "The Videshi"

    if uploaded:
        update_article_image(slug, uploaded, attr)
    else:
        print(f"  ✗ No image sourced for {slug}")

print("\nDone!")
