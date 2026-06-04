#!/usr/bin/env python3
"""Fix images for the 3 news articles published on 2026-06-04."""

import subprocess
import json
import os
import requests
import tempfile
import urllib.parse
from PIL import Image
import io

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or '=' not in line:
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            os.environ[key.strip()] = val.strip('"').strip("'")

# Load workspace env first (has GOOGLE_PLACES etc), then home env (has correct JWT)
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
UA = 'TheVideshi/1.0 (thevideshi.com)'

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

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            return r.content
    except:
        pass
    return None

def upload_via_curl(local_path, filename):
    """Upload to Supabase storage using curl (bypasses Python JWT issue)."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    result = subprocess.run(
        ["curl", "-sS", "-X", "POST", url,
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: image/jpeg",
         "-H", "x-upsert: true",
         "--data-binary", f"@{local_path}"],
        capture_output=True, text=True, timeout=30
    )
    resp = result.stdout
    if '"Key"' in resp:
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {filename}")
        return public_url
    else:
        print(f"  ✗ Upload failed: {resp[:200]}")
        return None

def update_article(slug, updates):
    """Update article in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}"
    result = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", json.dumps(updates)],
        capture_output=True, text=True, timeout=15
    )
    if result.stdout and '"id"' in result.stdout:
        print(f"  ✓ Updated article: {slug[:50]}...")
        return True
    else:
        print(f"  ✗ Update failed: {result.stdout[:200]}")
        return False

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # Use thumbnail AS-IS per rules
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img and 'svg' not in img.lower():
                return img
    except:
        pass
    return None

def fetch_wikimedia_commons(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6", "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
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
                url = ii.get("thumburl") or ii.get("url", "")
                results.append(url)
            return results
    except:
        pass
    return []

def fetch_pexels(*queries):
    if not PEXELS_KEY:
        return None
    for q in queries:
        try:
            r = requests.get("https://api.pexels.com/v1/search",
                             params={"query": q, "per_page": 3, "orientation": "landscape"},
                             headers={"Authorization": PEXELS_KEY}, timeout=10)
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    return photos[0]["src"]["large2x"]
        except:
            pass
    return None

def source_and_upload(slug, person=None, commons_queries=None, pexels_queries=None):
    """Source image, compress, upload via curl, return (url, attribution)."""
    candidates = []
    
    if person:
        url = fetch_wikipedia_person_image(person)
        if url:
            candidates.append(("wikipedia", url))
    
    if commons_queries:
        for q in commons_queries[:2]:
            imgs = fetch_wikimedia_commons(q)
            for img_url in imgs[:2]:
                candidates.append(("wikimedia_commons", img_url))
    
    if pexels_queries:
        url = fetch_pexels(*pexels_queries)
        if url:
            candidates.append(("pexels", url))
    
    for source, url in candidates:
        print(f"  Trying {source}: {url[:70]}...")
        raw = download_image(url)
        if not raw:
            continue
        
        compressed = compress_image(raw)
        size_kb = len(compressed) / 1024
        if size_kb < 10:
            print(f"  ⚠ Too small after compression ({size_kb:.0f} KB)")
            continue
        
        print(f"  📦 {size_kb:.0f} KB")
        
        tmpfile = f"/tmp/{slug}.jpg"
        with open(tmpfile, 'wb') as f:
            f.write(compressed)
        
        public_url = upload_via_curl(tmpfile, f"{slug}.jpg")
        if public_url:
            attr = "Wikimedia Commons" if "wiki" in source else "Pexels"
            return public_url, attr
    
    return None, None

# ─── ARTICLES TO FIX ──────────────────────────────────────────────────────────

articles = [
    {
        "slug": "sebi-rajesh-exports-158-billion-revenue-fraud-rajesh-mehta-barred-20260604",
        "person": "Rajesh Mehta businessman",
        "commons_queries": ["SEBI India securities", "gold refinery India"],
        "pexels_queries": ["gold bars refinery", "gold processing industry"],
        "caption": "Rajesh Exports, headquartered in Bengaluru, is known as the world's largest gold processor by volume",
    },
    {
        "slug": "indian-national-killed-kuwait-airport-iranian-drone-strike-diaspora-gulf-20260604",
        "person": None,
        "commons_queries": ["Kuwait International Airport", "Kuwait airport"],
        "pexels_queries": ["Kuwait city airport", "airport terminal building"],
        "caption": "Kuwait International Airport's Terminal 1 sustained severe damage in the Iranian drone and missile attack on June 3, 2026",
    },
    {
        "slug": "india-lithium-nickel-processing-incentives-ev-battery-critical-minerals-20260604",
        "person": None,
        "commons_queries": ["lithium battery manufacturing", "lithium mine processing"],
        "pexels_queries": ["lithium battery factory", "electric vehicle battery manufacturing"],
        "caption": "India aims to build domestic lithium and nickel processing capacity to secure its electric vehicle supply chain",
    },
]

def main():
    for i, art in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Image fix {i}: {art['slug'][:60]}...")
        print(f"{'='*60}")
        
        img_url, attribution = source_and_upload(
            art["slug"],
            person=art.get("person"),
            commons_queries=art.get("commons_queries"),
            pexels_queries=art.get("pexels_queries"),
        )
        
        if img_url:
            updates = {
                "image_url": img_url,
                "image_caption": art["caption"],
                "image_attribution": attribution,
            }
            update_article(art["slug"], updates)
        else:
            print("  ⚠ No image found for this article")

if __name__ == "__main__":
    main()
