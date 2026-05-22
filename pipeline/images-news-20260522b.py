#!/usr/bin/env python3
"""Source images for 4 new articles — 2026-05-22 afternoon batch"""

import json, os, sys, urllib.parse, urllib.request, hashlib, tempfile, subprocess

def load_env(path):
    path = os.path.expanduser(path)
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')
load_env('~/workspace/.env.supabase')

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ["PEXELS_API_KEY"]

ARTICLES = [
    {
        "id": "ce26260a-c726-447d-ba74-ccc8916ffcec",
        "name": "India Fuel Shortage",
        "wikimedia_searches": [],
        "pexels_searches": ["India fuel station queue", "India petrol pump trucks", "Indian truck drivers highway"],
    },
    {
        "id": "991448e3-f255-4612-bd6f-57c6e25c9f9c",
        "name": "UK Anti-Hindu Hate Monitor",
        "wikimedia_searches": ["BAPS Shri Swaminarayan Mandir London", "Neasden Temple London"],
        "pexels_searches": ["Hindu temple UK", "London Hindu community"],
    },
    {
        "id": "d5410792-507a-4e01-8e01-dd80247fed93",
        "name": "Bhangra in Habs Jerseys",
        "wikimedia_searches": [],
        "pexels_searches": ["bhangra dance celebration", "Montreal hockey fans celebration", "punjabi dance festival"],
    },
    {
        "id": "484f90c4-3009-471e-8f9c-6d800fee620f",
        "name": "India-South Korea Defense",
        "wikimedia_searches": ["Rajnath Singh 2024", "Rajnath Singh defense minister"],
        "pexels_searches": ["India military cooperation", "Indian defense minister"],
    },
]

BAD_ALT_RE_WORDS = ["satellite", "aerial", "map", "globe", "chart", "graph", "diagram", "icon", "logo", "vector", "illustration", "cartoon", "clipart"]

def search_wikimedia(query, limit=5):
    """Search Wikimedia Commons for images."""
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrlimit={limit}&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=1200&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Videshi/1.0 (https://thevideshi.com)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        pages = data.get("query", {}).get("pages", {})
        results = []
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            thumb = info.get("thumburl", "")
            orig = info.get("url", "")
            meta = info.get("extmetadata", {})
            desc = meta.get("ImageDescription", {}).get("value", "")
            license_short = meta.get("LicenseShortName", {}).get("value", "")
            if thumb and ("jpg" in thumb.lower() or "jpeg" in thumb.lower() or "png" in thumb.lower()):
                # Skip SVGs, PDFs, etc.
                if any(bad in desc.lower() for bad in BAD_ALT_RE_WORDS):
                    continue
                results.append({"url": thumb, "orig": orig, "desc": desc[:200], "license": license_short})
        return results
    except Exception as e:
        print(f"    Wikimedia search error for '{query}': {e}")
        return []

def search_pexels(query, per_page=5):
    """Search Pexels for images."""
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        results = []
        for photo in data.get("photos", []):
            src = photo.get("src", {})
            alt = photo.get("alt", "")
            if any(bad in alt.lower() for bad in BAD_ALT_RE_WORDS):
                continue
            results.append({
                "url": src.get("large2x") or src.get("large") or src.get("original"),
                "alt": alt[:200],
                "photographer": photo.get("photographer", ""),
                "pexels_url": photo.get("url", ""),
            })
        return results
    except Exception as e:
        print(f"    Pexels search error for '{query}': {e}")
        return []

def download_image(url, dest_path):
    """Download an image to a local path."""
    req = urllib.request.Request(url, headers={"User-Agent": "Videshi/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"    Download error: {e}")
        return 0

def upload_to_supabase(local_path, bucket_path):
    """Upload a file to Supabase storage."""
    with open(local_path, 'rb') as f:
        data = f.read()
    
    url = f"{SB_URL}/storage/v1/object/{bucket_path}"
    req = urllib.request.Request(url, data=data, method='POST', headers={
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = resp.read()
        return True
    except urllib.error.HTTPError as e:
        body = e.read().decode() if hasattr(e, 'read') else str(e)
        print(f"    Upload error: {e.code} - {body[:200]}")
        return False
    except Exception as e:
        print(f"    Upload error: {e}")
        return False

def update_article_image(article_id, image_url):
    """Update article with image URL."""
    import urllib.request
    url = f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    data = json.dumps({
        "image_url": image_url,
        "image_attribution": "The Videshi",
    }).encode()
    req = urllib.request.Request(url, data=data, method='PATCH', headers={
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            pass
        return True
    except Exception as e:
        print(f"    DB update error: {e}")
        return False

# Process each article
for article in ARTICLES:
    aid = article["id"]
    print(f"\n{'='*60}")
    print(f"📸 Sourcing image for: {article['name']} ({aid[:8]}...)")
    print(f"{'='*60}")
    
    found_url = None
    
    # Try Wikimedia first
    for query in article.get("wikimedia_searches", []):
        print(f"  🔍 Wikimedia: '{query}'")
        results = search_wikimedia(query)
        if results:
            for r in results[:3]:
                print(f"    → {r['desc'][:80]}... [{r['license']}]")
            # Take first good result
            found_url = results[0]["url"]
            print(f"  ✅ Using Wikimedia image")
            break
    
    # Fall back to Pexels
    if not found_url:
        for query in article.get("pexels_searches", []):
            print(f"  🔍 Pexels: '{query}'")
            results = search_pexels(query)
            if results:
                for r in results[:3]:
                    print(f"    → {r['alt'][:80]}... (by {r['photographer']})")
                found_url = results[0]["url"]
                print(f"  ✅ Using Pexels image")
                break
    
    if not found_url:
        print(f"  ❌ No suitable image found — skipping (no image > wrong image)")
        continue
    
    # Download
    tmp_path = f"/tmp/{aid}.jpg"
    print(f"  ⬇️  Downloading...")
    size = download_image(found_url, tmp_path)
    if size == 0:
        print(f"  ❌ Download failed — skipping")
        continue
    print(f"  ⬇️  Downloaded {size/1024:.0f}KB")
    
    # Upload to Supabase
    bucket_path = f"article-images/{aid}.jpg"
    print(f"  ⬆️  Uploading to Supabase...")
    if upload_to_supabase(tmp_path, bucket_path):
        public_url = f"{SB_URL}/storage/v1/object/public/{bucket_path}"
        print(f"  ⬆️  Uploaded: {public_url[:80]}...")
        
        # Update article
        if update_article_image(aid, public_url):
            print(f"  ✅ Article updated with image!")
        else:
            print(f"  ⚠️  Upload succeeded but DB update failed")
    else:
        print(f"  ❌ Upload failed — skipping")
    
    # Cleanup
    try:
        os.remove(tmp_path)
    except:
        pass

print(f"\n{'='*60}")
print("Image sourcing complete.")
print(f"{'='*60}")
