#!/usr/bin/env python3
"""Image sourcing for entertainment articles — 2026-05-18."""

import os, json, time, urllib.request, urllib.parse, subprocess, sys

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip('"').strip("'")

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ["PEXELS_API_KEY"]
UA = "TheVideshiBot/1.0 (thevideshi.com; editorial)"

import requests

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def get_wiki_image(file_title):
    encoded = urllib.parse.quote(file_title)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded}&prop=imageinfo&iiprop=url|extmetadata&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        for pid, pdata in data.get('query',{}).get('pages',{}).items():
            ii = pdata.get('imageinfo',[{}])[0]
            em = ii.get('extmetadata',{})
            import re
            artist_raw = em.get('Artist',{}).get('value','')
            artist_clean = re.sub(r'<[^>]+>', '', artist_raw).strip()[:100]
            return {
                'url': ii.get('url',''),
                'license': em.get('LicenseShortName',{}).get('value',''),
                'artist': artist_clean,
            }
    except Exception as e:
        print(f"  Wiki error for {file_title}: {e}")
    return None

def search_pexels(query, per_page=5):
    """Search Pexels for images."""
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page={per_page}"
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        results = []
        BAD_ALT_RE = r'(?i)(satellite|aerial|map|terrain|globe|earth from)'
        import re
        for photo in data.get('photos', []):
            alt = photo.get('alt', '')
            if re.search(BAD_ALT_RE, alt):
                continue
            results.append({
                'url': photo['src']['large2x'],
                'photographer': photo.get('photographer', ''),
                'alt': alt,
                'pexels_url': photo.get('url', ''),
            })
        return results
    except Exception as e:
        print(f"  Pexels error: {e}")
    return []

def download_image(url, local_path):
    """Download image to local path."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(local_path, 'wb') as f:
            f.write(data)
        print(f"  Downloaded: {local_path} ({len(data)} bytes)")
        return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False

def upload_to_supabase(local_path, remote_name):
    """Upload to Supabase article-images bucket."""
    with open(local_path, 'rb') as f:
        data = f.read()
    
    # Determine content type
    ct = 'image/jpeg'
    if local_path.endswith('.png'):
        ct = 'image/png'
    elif local_path.endswith('.webp'):
        ct = 'image/webp'
    
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{remote_name}"
    resp = requests.post(
        upload_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": ct,
            "x-upsert": "true",
        },
        data=data,
    )
    if resp.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{remote_name}"
        print(f"  Uploaded: {public_url}")
        return public_url
    else:
        print(f"  Upload error {resp.status_code}: {resp.text[:200]}")
    return None

def update_article(article_id, updates):
    """Update article in Supabase."""
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=HEADERS,
        json=updates,
    )
    if resp.status_code in (200, 204):
        print(f"  ✅ Article {article_id} updated")
    else:
        print(f"  ❌ Update error: {resp.status_code} {resp.text[:200]}")

# ── Clean up previous temp files ──────────────────────────────────────────────
import glob
for f in glob.glob('/tmp/*_hero.jpg') + glob.glob('/tmp/*_g*.jpg'):
    os.remove(f)

# ══════════════════════════════════════════════════════════════════════════════
# Article 1: Salman Khan
# ══════════════════════════════════════════════════════════════════════════════
ARTICLE_1_ID = "6979cc97-bec5-4da6-b801-dfe77518cd76"
print(f"\n{'='*60}")
print(f"Image sourcing: Article 1 (Salman Khan)")

# Hero: Wikipedia image of Salman Khan
hero_path = f"/tmp/{ARTICLE_1_ID}_hero.jpg"
wiki_img = get_wiki_image("File:Salman's Being Human show at HDIL India Couture Week 2010 (1).jpg")
time.sleep(0.5)

gallery_images = []

if wiki_img and wiki_img['url']:
    if download_image(wiki_img['url'], hero_path):
        pub_url = upload_to_supabase(hero_path, f"{ARTICLE_1_ID}.jpg")
        if pub_url:
            update_article(ARTICLE_1_ID, {
                "image_url": pub_url,
                "image_attribution": f"Photo: {wiki_img['artist']} via Wikimedia Commons ({wiki_img['license']})",
                "image_caption": "Salman Khan at a Being Human charity event — the actor has shed 7-8 kg for two upcoming films, signaling a dramatic shift in his screen persona.",
            })

# Gallery: Pexels fitness / gym images
time.sleep(1)
pexels_results = search_pexels("Bollywood gym fitness workout", per_page=3)
for i, photo in enumerate(pexels_results[:2]):
    g_path = f"/tmp/{ARTICLE_1_ID}_g{i+1}.jpg"
    if download_image(photo['url'], g_path):
        pub_url = upload_to_supabase(g_path, f"{ARTICLE_1_ID}_g{i+1}.jpg")
        if pub_url:
            caption = f"The lean transformation requires intense training discipline — {photo['alt'][:80]}" if i == 0 else f"High-altitude calisthenics in Ladakh form part of Salman's preparation for Maatrubhumi."
            gallery_images.append({"url": pub_url, "caption": caption})

if gallery_images:
    update_article(ARTICLE_1_ID, {"gallery_images": gallery_images})

# ══════════════════════════════════════════════════════════════════════════════
# Article 2: Irrfan Khan's Alvida
# ══════════════════════════════════════════════════════════════════════════════
ARTICLE_2_ID = "1cb3a1bc-f0d7-4818-a418-60604316b592"
print(f"\n{'='*60}")
print(f"Image sourcing: Article 2 (Irrfan Khan's Alvida)")

# Search for Irrfan Khan image on Wikimedia Commons
time.sleep(1)
commons_url = "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=Irrfan+Khan&srnamespace=6&format=json&srlimit=10"
req = urllib.request.Request(commons_url, headers={"User-Agent": UA})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    results = data.get('query', {}).get('search', [])
    irrfan_imgs = [r for r in results if 'irrfan' in r.get('title','').lower()]
    print(f"  Found {len(irrfan_imgs)} Irrfan images on Commons:")
    for r in irrfan_imgs[:5]:
        print(f"    {r['title']}")
except Exception as e:
    irrfan_imgs = []
    print(f"  Commons search error: {e}")

# Try to get Irrfan Khan image from Wikimedia Commons
hero_found = False
for r in irrfan_imgs[:3]:
    time.sleep(0.5)
    img_data = get_wiki_image(r['title'])
    if img_data and img_data['url'] and ('cc' in img_data['license'].lower() or 'public' in img_data['license'].lower()):
        hero_path = f"/tmp/{ARTICLE_2_ID}_hero.jpg"
        if download_image(img_data['url'], hero_path):
            pub_url = upload_to_supabase(hero_path, f"{ARTICLE_2_ID}.jpg")
            if pub_url:
                update_article(ARTICLE_2_ID, {
                    "image_url": pub_url,
                    "image_attribution": f"Photo: {img_data['artist']} via Wikimedia Commons ({img_data['license']})",
                    "image_caption": "Irrfan Khan, the actor who belonged to the world — his unreleased directorial debut 'Alvida' with Nawazuddin Siddiqui has resurfaced online, revealing the filmmaker he might have become.",
                })
                hero_found = True
                break

if not hero_found:
    # Try Pexels as fallback for atmospheric shot
    print("  No suitable Irrfan hero image found — trying Pexels for film/cinema atmosphere")
    time.sleep(1)
    pexels_results = search_pexels("Indian cinema vintage film set", per_page=5)
    for photo in pexels_results[:1]:
        hero_path = f"/tmp/{ARTICLE_2_ID}_hero.jpg"
        if download_image(photo['url'], hero_path):
            pub_url = upload_to_supabase(hero_path, f"{ARTICLE_2_ID}.jpg")
            if pub_url:
                update_article(ARTICLE_2_ID, {
                    "image_url": pub_url,
                    "image_attribution": f"Photo: {photo['photographer']} via Pexels",
                    "image_caption": "A film set in India — Irrfan Khan's unreleased directorial debut 'Alvida' was made with minimal resources and maximum passion.",
                })

# ══════════════════════════════════════════════════════════════════════════════
# Article 3: Raja Shivaji Box Office
# ══════════════════════════════════════════════════════════════════════════════
ARTICLE_3_ID = "c93a028f-02dc-4fc5-91a1-b59b7a36dfd7"
print(f"\n{'='*60}")
print(f"Image sourcing: Article 3 (Raja Shivaji)")

# Hero: Riteish Deshmukh from Wikipedia
hero_path = f"/tmp/{ARTICLE_3_ID}_hero.jpg"
time.sleep(1)
wiki_img = get_wiki_image("File:Riteish Deshmukh.jpg")
gallery_images = []

if wiki_img and wiki_img['url']:
    if download_image(wiki_img['url'], hero_path):
        pub_url = upload_to_supabase(hero_path, f"{ARTICLE_3_ID}.jpg")
        if pub_url:
            update_article(ARTICLE_3_ID, {
                "image_url": pub_url,
                "image_attribution": f"Photo: {wiki_img['artist']} via Wikimedia Commons ({wiki_img['license']})",
                "image_caption": "Riteish Deshmukh, director and star of 'Raja Shivaji' — the Marathi epic that just smashed Sairat's 10-year box-office record.",
            })

# Gallery: Shivaji statue / Maharashtra landmarks from Pexels
time.sleep(1)
pexels_results = search_pexels("Shivaji statue Maharashtra India", per_page=5)
for i, photo in enumerate(pexels_results[:2]):
    g_path = f"/tmp/{ARTICLE_3_ID}_g{i+1}.jpg"
    if download_image(photo['url'], g_path):
        pub_url = upload_to_supabase(g_path, f"{ARTICLE_3_ID}_g{i+1}.jpg")
        if pub_url:
            caption = "Chhatrapati Shivaji Maharaj's legacy looms over Maharashtra — Riteish Deshmukh's epic brought the warrior king to life with blockbuster production values." if i == 0 else "The film's success signals a new era for Marathi cinema in multiplexes worldwide."
            gallery_images.append({"url": pub_url, "caption": caption})

if gallery_images:
    update_article(ARTICLE_3_ID, {"gallery_images": gallery_images})

print(f"\n{'='*60}")
print("Image sourcing complete.")
