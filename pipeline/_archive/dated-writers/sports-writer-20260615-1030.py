#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (10:30 UTC run)
Article:
1. India men's hockey 2-3 loss to Netherlands in FIH Pro League Rotterdam opener;
   Manpreet Singh's 412th cap milestone; World Cup prep angle
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
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
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
                print(f"  \u2713 Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
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
                print(f"  \u2713 Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  \u26a0 Pexels error for '{query}': {e}")
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
            print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
            return None
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  \u2717 Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  \u2717 Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  \U0001f4e6 Compressed to {size_kb:.0f} KB")

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
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        else:
            print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
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
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE: India men's hockey 2-3 Netherlands, Pro League opener
# ============================================================
print("\n" + "="*60)
print("ARTICLE: India men's hockey 2-3 Netherlands, Pro League Rotterdam")
print("="*60)

art_slug = "india-hockey-2-3-netherlands-fih-pro-league-rotterdam-manpreet-singh-412-caps-world-cup-2026-nri"
art_headline = "Manpreet Singh Equalled a 412-Cap Record. In Rotterdam, a Late Drag Still Broke Indian Hearts."
art_subheadline = "India twice clawed level against the Olympic champions before Tijmen Reyenga's 40th-minute strike sealed a 2-3 defeat in the FIH Pro League's European leg — a dress rehearsal on the very turf that hosts the World Cup in August."
art_vertical = "sports"

art_body = """Hockey is the sport that India once owned. Eight Olympic golds, an unbroken run of dominance from Amsterdam in 1928 to Tokyo in 1964, a national identity stitched into a stick and a ball. For the diaspora that grew up on those stories — passed down by grandfathers who remembered Dhyan Chand the way others remembered freedom — every Indian hockey match abroad carries a weight that the scoreline alone never captures. On Sunday in Rotterdam, that weight pressed down again, and again it ended in heartbreak.

The Indian men's hockey team lost 2-3 to the Netherlands in their opening fixture of the European leg of the FIH Pro League 2025-26, played at Hockey Club Rotterdam. It was the kind of defeat that stings precisely because it was so nearly something else. India trailed twice and equalised twice, matching the reigning Olympic champions and world number one side for long stretches, before a 40th-minute penalty-corner strike from Tijmen Reyenga proved the difference.

## A Record on a Quiet Sunday

The match carried a milestone that deserved a bigger stage. Veteran midfielder Manpreet Singh, the former captain and the metronome of India's midfield for over a decade, made his 412th international appearance — drawing level with the all-time Indian record held by former skipper Dilip Tirkey. There were no fireworks, no trophy presentation, just a 33-year-old from Mithapur, Jalandhar, quietly logging another cap in a foreign city, the way he has done since 2011.

That Manpreet reached the mark in a losing cause felt almost fitting for a generation of Indian hockey players who have spent their careers chasing the ghosts of a glorious past. The applause, when it comes, is rarely loud. But for the families in Surrey, Southall, and the Punjabi enclaves of California who still follow the game, the number means something: longevity, loyalty, and a refusal to let the sport fade.

## Twice Down, Twice Level

The Dutch began on the front foot, winning four early penalty corners and drawing first blood in the third minute when Miles Bukkens fired an upright reverse finish past Indian goalkeeper Suraj Karkera. India's response was swift and stylish. In the 10th minute, captain Harmanpreet Singh — the world's most feared drag-flicker — turned creator, threading a sensational long pass that found Dilpreet Singh, who finished from a narrow angle to level the score.

The Netherlands reasserted control in the second quarter, dominating possession and eventually retaking the lead through Koen Bijen's first-time strike in the 23rd minute after a defensive lapse let the ball linger in the circle. Half-time: 2-1 to the hosts.

India came out for the third quarter with intent, stringing together passes and dictating tempo. They earned their first penalty corner and made it count, Sukhjeet Singh finishing a cleverly worked set-piece routine in the 33rd minute to make it 2-2. But the parity lasted only minutes. The Dutch won a penalty corner of their own, and Reyenga rifled his effort home in the 40th minute. India pushed for an equaliser through the final quarter but could not breach the Dutch defence again.

## More Than a League Game

This was not merely another fixture on a crowded calendar. The European leg of the Pro League is unfolding on the very turf that will host the 2026 FIH Hockey World Cup in August, co-hosted by the Netherlands and Belgium. For Craig Fulton's India, every minute in Rotterdam is reconnaissance — a chance to acclimatise to the conditions, the surface, and the relentless intensity of the world's best before the sport's biggest prize is contested in a matter of weeks.

The schedule offers little respite. India face four-time world champions Germany next, on June 17, in another marquee test against a side widely tipped to challenge for the World Cup. The men's team is competing across Europe even as the Indian women's team chases promotion at the FIH Hockey Women's Nations Cup in Auckland — a rare fortnight in which two Indian national hockey sides take the field on opposite sides of the planet, almost every day from June 14 to June 28.

## Why It Matters to the Diaspora

For NRIs, hockey occupies a tender corner of the national memory. It is the sport India dominated when it had little else to celebrate on the world stage, and its slow eclipse by cricket has felt, to many, like the loss of a birthright. A bronze at the Tokyo Olympics in 2021 — India's first hockey medal in 41 years — rekindled the flame, and a generation led by Harmanpreet, Manpreet, and a fearless young core now carries the hope of a first World Cup title since 1975.

A 2-3 loss to the Olympic champions is no disgrace. India matched the best team in the world for three quarters and fell to a single set-piece. But with the World Cup looming on this very ground, the margins that decided Sunday — a defensive lapse, a conceded penalty corner — are exactly the ones Fulton's men must erase. For the diaspora watching from afar, the dream of August is alive. It just needs sharpening.
"""

# Image: Wikipedia for the captain / record-holder. Try Harmanpreet Singh first, then Manpreet.
print("\nSourcing image...")
img_url = fetch_wikipedia_person_image("Harmanpreet Singh (field hockey)")
img_caption = "India captain Harmanpreet Singh, who assisted India's first goal in Rotterdam"
person_used = "Harmanpreet Singh"
if not img_url:
    img_url = fetch_wikipedia_person_image("Harmanpreet Singh")
if not img_url:
    img_url = fetch_wikipedia_person_image("Manpreet Singh (field hockey)")
    img_caption = "India midfielder Manpreet Singh, who equalled the national record of 412 international caps"
    person_used = "Manpreet Singh"
if not img_url:
    commons = fetch_wikimedia_commons_images("India men's national field hockey team", limit=4)
    if commons:
        img_url = commons[0]["url"]
        img_caption = "The India men's national field hockey team in action"
        person_used = "team"

img_final = None
img_attribution = "Wikimedia Commons"
if img_url:
    if "pexels.com" in img_url:
        img_attribution = "Pexels"
    img_final = upload_to_supabase(img_url, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image found — inserting without image")

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
        {"name": "IANS Live", "url": "https://www.ianslive.in"},
        {"name": "News Dive", "url": "https://www.newsdive.net"},
        {"name": "RevSportz", "url": "https://www.revsportz.in"},
        {"name": "FIH", "url": "https://www.fih.hockey"},
    ]),
    "diaspora_angle": "Hockey is the sport India once owned, and its fortunes carry deep emotional weight for NRIs; with the FIH World Cup looming in August on the same Dutch turf, India's narrow 2-3 loss to the Olympic champions is a high-stakes dress rehearsal for the diaspora's oldest sporting dream.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

# ── SUMMARY ──
print("\n" + "="*60)
print("DONE")
print("="*60)
print(f"Article: {'\u2713' if art_id else '\u2717'} {art_slug}")
print(f"Image person used: {person_used}")
print("Set to status='review'")
