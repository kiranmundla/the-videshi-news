#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (07:30 UTC run)
Article:
1. Sarpreet Singh — Indian-origin NZ midfielder, World Cup debut vs Iran June 16
"""

import os, sys, json, time, uuid, hashlib, io, re
from datetime import datetime, timezone

import requests
from PIL import Image

# ── ENV ──
env_supa = os.path.expanduser("~/.env.supabase")
for line in open(env_supa):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ[k] = v.strip().strip('"').strip("'")

env_pex = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(env_pex):
    for line in open(env_pex):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── HELPERS ──

def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                    "mime": mime,
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10,
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    try:
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        if r.status_code != 200:
            print(f"  ✗ Download failed ({r.status_code}) for {img_url[:80]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ✗ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ✗ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  📦 Compressed to {size_kb:.0f} KB")

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=compressed,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ✗ Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  ✗ Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE: Sarpreet Singh — World Cup debut vs Iran
# ============================================================
print("\n" + "="*60)
print("ARTICLE: Sarpreet Singh — Indian-origin NZ midfielder, WC debut")
print("="*60)

art_slug = "sarpreet-singh-new-zealand-indian-origin-fifa-world-cup-2026-debut-iran-punjab-nri"
art_headline = "India Did Not Qualify. On Tuesday, a Punjabi Mother's Son Carries Its Flag at the World Cup Anyway."
art_subheadline = "Auckland-born Sarpreet Singh, whose parents emigrated from Jalandhar, will line up for New Zealand against Iran in California — the first Indian-origin footballer at a World Cup since 2006."
art_vertical = "diaspora"

art_body = """When New Zealand walk out at the Los Angeles Stadium in Inglewood on Tuesday to face Iran, the Blue Tigers of Indian football will be nowhere on the team sheet. India did not qualify for the FIFA World Cup 2026 — the national side crashed out in the second round of Asian qualifying, extending a wait for a senior men's World Cup appearance that now stretches back to the country's founding. And yet, in the 25-year-old attacking midfielder warming up in the all-white of New Zealand, a piece of India will quietly take the field.

Sarpreet Singh was born in Auckland to parents who emigrated from Jalandhar, Punjab. When he comes on against Iran in California, he will become the first footballer of Indian origin to play at a World Cup since France's Vikash Dhorasoo in 2006. A day's worth of squad announcements later, Qatar's Kerala-rooted winger Tahsin Mohammed Jamshid joins the same rare club. For a diaspora that has spent decades watching the World Cup as outsiders, the 2026 edition offers something new: someone to claim.

## A Mother Who Drove to Training

The story does not begin on a pitch. It begins in a car. In a country where cricket and rugby command the back pages, football is a minority pursuit — and for the child of Punjabi immigrants, an unusual choice. Most Indian parents in the diaspora steer their children toward medicine, engineering, a stable salary. Sarpreet's mother, Sarabjit, did the opposite. She enrolled her younger son at the Wynton Rufer soccer academy when he was seven and drove him to training, a level of support that, as Sarpreet has acknowledged, not every Punjabi kid in New Zealand received.

That early backing carried him through local clubs Papatoetoe and Onehunga Sports, and in 2015 into the Wellington Phoenix academy — the turning point. He made his senior debut for the Phoenix at 16 and quickly established himself as one of the brightest prospects in the Australian A-League.

## From Bayern Munich to a Long Road Back

A standout showing at the 2019 FIFA U-20 World Cup earned Sarpreet a three-year contract with German giants Bayern Munich — a staggering leap for a boy from the Auckland suburbs. The move did not translate into first-team minutes, and what followed was the less glamorous reality of professional football: loan spells and transfers across FC Nürnberg, Jahn Regensburg, Hansa Rostock, União de Leiria in Portugal, and Serbian club FK TSC. In 2026, he returned to Wellington Phoenix on loan, closing a circle that began on a suburban training pitch.

The last few months have not been kind. Injuries threatened his place in New Zealand's final squad. When head coach Darren Bazeley travelled to Wellington to tell him personally that he had made the cut, Sarpreet described it as a reward for hard work through a difficult stretch.

## "No Better Stage to Lift the Names of Indian People"

Sarpreet does not treat his heritage as a burden. "I don't say it's added pressure. I just want to do my best to lift the names of Indian people, and there is no better stage to do it than the World Cup," he said in a recent interview. He framed the moment as a responsibility — to perform, and to inspire the next generation of South Asian children who might otherwise never imagine football as a path.

The task is steep. New Zealand are the lowest-ranked side in Group G at 85th in the world, drawn alongside Iran (21st), Egypt (29th), and Belgium (9th). In six World Cup matches across 1982 and 2010, the All Whites have never won — three defeats, three draws. Their campaign opens against Iran on Tuesday, followed by Egypt on June 22 and Belgium on June 27. Veterans Chris Wood and Tommy Smith, survivors of the unbeaten 2010 run, are the only New Zealanders to feature at two World Cups.

## Why It Matters to the Diaspora

For NRIs scattered across the United States, the United Kingdom, and Canada, the absence of an Indian men's team at the World Cup is an old ache. India qualified for the 1950 tournament and then withdrew, citing travel costs, and has never returned. The expansion to 48 teams briefly rekindled hope before qualifying dashed it again.

Sarpreet Singh does not fill that void — he is a New Zealander, and proudly so. But for the Punjabi families of Fremont, Surrey, and Southall, and for every South Asian kid who has been told football is not for people like them, an Indian flag will fly, however quietly, at the sport's grandest stage. That, this year, is enough.
"""

# Image: Wikipedia for Sarpreet Singh
print("\nSourcing image for Sarpreet Singh...")
img_url = fetch_wikipedia_person_image("Sarpreet Singh")
if not img_url:
    img_url = fetch_wikipedia_person_image("Sarpreet Singh (footballer)")
commons = fetch_wikimedia_commons_images("Sarpreet Singh footballer New Zealand", limit=3)
if not img_url and commons:
    img_url = commons[0]["url"]
if not img_url:
    img_url = fetch_pexels_image("soccer player midfielder action")

img_final = None
img_attribution = "Wikimedia Commons"
img_caption = "Sarpreet Singh training with FC Bayern Munich in 2019"
if img_url:
    if "pexels.com" in img_url:
        img_attribution = "Pexels"
        img_caption = "A midfielder controls the ball during a football match"
    img_final = upload_to_supabase(img_url, f"{art_slug}.jpg")

if not img_final:
    print("  ⚠ No image found — inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": art_vertical,
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "LiveMint", "url": "https://www.livemint.com"},
        {"name": "Inshorts", "url": "https://www.inshorts.com"},
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "FIFA", "url": "https://www.fifa.com"},
    ]),
    "diaspora_angle": "India did not qualify for the 2026 World Cup, but Auckland-born, Jalandhar-rooted Sarpreet Singh becomes the first Indian-origin footballer at a World Cup since 2006 — giving NRIs across the US, UK, and Canada someone to claim at the sport's biggest stage.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

# ── SUMMARY ──
print("\n" + "="*60)
print("DONE")
print("="*60)
print(f"Article: {'✓' if art_id else '✗'} {art_slug}")
print("Set to status='review'")
