#!/usr/bin/env python3
"""Sports writer – 2026-06-01 batch"""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────
def sb_insert(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    rows = r.json()
    return rows[0] if isinstance(rows, list) and rows else rows

def sb_patch(table, filters, data):
    qs = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{qs}", headers=HEADERS, json=data, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return r

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            cmd = [
                "curl", "-sS",
                f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                "-H", f"Authorization: {PEXELS_KEY}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("large")
                alt = (p.get("alt") or "").lower()
                # Skip bad alt text
                bad = ["satellite", "aerial", "map", "flag", "icon", "logo"]
                if any(b in alt for b in bad):
                    continue
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Some servers don't support HEAD well, try GET
        if r.status_code != 200:
            r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                             headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            ct2 = r2.headers.get("Content-Type", "")
            cl2 = int(r2.headers.get("Content-Length", 0))
            if r2.status_code == 200 and "image" in ct2:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=15,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None
        ct = r.headers.get("Content-Type", "image/jpeg")
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": ct,
            "x-upsert": "true",
        }
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=r.content,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

# ── articles ─────────────────────────────────────────────────────────
articles = []

# ─── ARTICLE 1: India's Golden Week in Athletics ───
articles.append({
    "headline": "Five Barriers in Ten Days. Indian Athletics Has Never Seen a Week Like This.",
    "subheadline": "Gulveer Singh ran a sub-four-minute mile. Gurindervir Singh went under 10.10 in the 100m. Vishal TK broke 45 seconds in the 400m. Pooja Singh cleared 1.93m. Tejaswin Shankar crossed 8,000 decathlon points. All within ten days.",
    "slug": "india-athletics-golden-week-five-national-records-ten-days-gulveer-gurindervir-vishal-pooja-tejaswin-nri",
    "category": "sports",
    "body": """The numbers arrived so fast they almost blurred together. In the span of ten days — from the Federation Cup in Ranchi to a Continental Tour meet in Cleveland, Ohio — five Indian athletes broke five barriers that had stood for years, in some cases for decades. Nothing like it has happened before in Indian athletics.

## The Fastest Indian Ever

It started in Ranchi on May 22, when the men's 100m semifinals at the Federation Cup produced a shock. **Gurindervir Singh**, a 25-year-old Punjab sprinter from the Indian Army, clocked 10.17 seconds to set a new national record. Minutes later, **Animesh Kujur** answered with 10.15 to reclaim it. But in the final the next day, Gurindervir obliterated both marks with **10.09 seconds** — the first time an Indian had ever run below 10.10. It was not merely fast. It was dominant, finishing over two-tenths clear of his nearest rival and instantly securing Commonwealth Games and Asian Games qualification.

The time made him the second-fastest man in Asia this year, behind only Japan's Fukuto Komuro at 10.08. For context, the Indian men's 100m record moved only 0.04 seconds between 2005 and 2021. In Ranchi, it moved 0.08 in a single day.

Bollywood actor Akshay Kumar, himself a fitness icon, captured the national mood on social media: "Everyone used to say Indians couldn't do it. Now everyone says it was bound to happen."

## Sub-45 in the 400m

On the same evening in Ranchi, Kerala's **Vishal TK** shattered his own national record in the men's 400m with a time of **44.98 seconds**, becoming the first Indian to break the 45-second barrier. The mark had been an unofficial ceiling for Indian quarter-milers for as long as anyone could remember. Vishal had been inching toward it for two seasons, and when he finally dipped under, the Birsa Munda Stadium erupted.

## 8,000 Points in the Decathlon

While the track events dominated headlines, **Tejaswin Shankar** was quietly making his own history in the combined events. The former NCAA high jump champion, who trained at Kansas State University before turning professional, crossed **8,000 decathlon points** for the first time in India — a threshold that places him firmly in the conversation for a podium at the Asian Games and a possible Olympic qualifying mark.

For the Indian diaspora in the United States, Tejaswin's journey carries particular resonance. He was one of the first Indian athletes to thrive in the American collegiate system, earning an NCAA title while studying in Manhattan, Kansas. His progression into the decathlon has been a case study in how the diaspora pathway can produce world-class multi-sport athletes.

## 1.93 Metres in Hong Kong

The week's momentum carried to the 22nd Asian U20 Athletics Championships in Hong Kong, where **Pooja Singh**, a teenager from Haryana, cleared **1.93 metres** in the women's high jump to win gold and set a new national record. She erased the decade-old mark of 1.92m held by Sahana Kumari since 2012, and her clearance also bettered the Asian U20 meet record of 1.90m set by Uzbekistan's Svetlana Radzivil in 2006.

Pooja's backstory deepens the significance. She trained for years with bamboo poles and rice-husk sacks, without access to a proper high jump pit, before entering the federation system. At nineteen, she has already cleared a height that would have been competitive in the senior medals bracket at the last Asian Games.

## A Sub-Four Mile in Cleveland

The crescendo came on Saturday, May 30, across the Atlantic. **Gulveer Singh**, a 27-year-old Indian Army runner who has been training in the United States, clocked **3:55.63** in the Men's 1 Mile Pro event at the Music City Track Carnival in Cleveland — becoming the first Indian in history to run a sub-four-minute mile. He won the race by over four seconds, with the American runners Christopher Knight (3:59.72) and Tristan Trevino (4:00.27) finishing behind him.

Gulveer is no stranger to barriers. He already holds the Indian 10,000m national record at 27:00.22, was the first Indian to break 13 minutes for the indoor 5,000m (12:59.77), and won bronze at the Asian Games in the 10,000m. Based in the US while preparing for the Glasgow Commonwealth Games and the Japan Asian Games, he has methodically dismantled every distance milestone available to an Indian runner.

## What It Means

Five athletes. Five events. Five national barriers. In ten days.

The cluster is not coincidental. Indian athletics has been quietly building infrastructure — high-performance centres at SAI Bengaluru and Patiala, overseas training stints funded by the government's Target Olympic Podium Scheme, and an increasing number of Indian athletes competing on the American and European circuits. The Federation Cup in Ranchi served as the proving ground; the international meets confirmed it.

For the NRI community, which has watched Indian cricket dominate global sports coverage for decades, this week was different. These were individual athletes, many of them from modest backgrounds, competing against the best in the world in the most elemental events in sport — running, jumping, throwing. And winning.

The Asian Games in Aichi-Nagoya later this year will be the next major test. But this week, Indian athletics needed no external validation. The stopwatch said enough.

**Sources:** Athletics Federation of India, IANS, IndiaSportsHub, Nation Press""",
    "image_search_person": "Gulveer Singh athlete",
    "image_pexels_query": "athletics track sprint india",
    "image_pexels_fallback": "running track stadium",
    "sources": ["Athletics Federation of India", "IANS", "IndiaSportsHub", "Nation Press", "InShorts"],
    "is_editorial": False,
})

# ─── ARTICLE 2: India's Wrestling Squad for Asian Games ───
articles.append({
    "headline": "World No. 1 Kalkal, Olympic Medallist Sehrawat, and Punia at 97 Kilos. India's Wrestling Squad for Aichi-Nagoya Is Set.",
    "subheadline": "The Wrestling Federation of India finalized the men's squad after trials in Lucknow. One hundred and sixty-nine wrestlers competed for eleven spots. The team for the 2026 Asian Games features a world number one, an Olympic bronze medallist, and an Asian Games silver medallist moving up in weight.",
    "slug": "india-wrestling-squad-asian-games-2026-kalkal-sehrawat-punia-aichi-nagoya-nri",
    "category": "sports",
    "body": """The trials ran all day Sunday at the Sports Authority of India centre in Lucknow, with 169 wrestlers across freestyle and Greco-Roman divisions fighting for a place in the Indian contingent heading to the 2026 Asian Games in Aichi-Nagoya. By evening, the Wrestling Federation of India had its squad. It is built around three pillars: a world number one, an Olympic bronze medallist, and one of the most experienced grapplers in Indian wrestling history.

## The Headliners

**Sujeet Kalkal**, currently ranked number one in the world at 65 kilograms freestyle, punched his ticket with a composed 2-0 victory over Vishal Kaliramana in the final. Kalkal's rise has been rapid — he won gold at the Asian Championships earlier this year and has been on an unbeaten run that has carried him to the top of the United World Wrestling rankings. At 24, he enters Aichi-Nagoya as a legitimate medal favourite.

**Aman Sehrawat**, the Paris Olympic bronze medallist, was dominant at 57 kilograms. He dispatched Rahul 11-1 in a lopsided final that was effectively over before the first period ended. Sehrawat's Olympic pedigree makes him the most decorated wrestler in the squad, and his form in Lucknow suggests he is nowhere near done.

The most intriguing selection was **Deepak Punia**. The 2019 World Championship silver medallist and 2022 Asian Games silver medallist has spent most of his career at 86 kilograms. In Lucknow, he moved up to 97 — a full weight class higher — and won convincingly, overpowering Jointy Kumar 8-0. At 26, Punia is reinventing himself at a heavier weight, and the ease of his win suggests the transition has been planned, not improvised.

## The Full Freestyle Lineup

Beyond the three marquee names, the freestyle contingent features **Sagar Jaglan** at 74 kilograms, who edged past Jaideep 8-6 in a closely contested final that showcased his improving tactical awareness. **Mukul Dahiya** secured the 86-kilogram spot with a 4-2 win over Amit, while **Rajat Rahal** dominated the 125-kilogram heavyweight category with a 10-6 victory against Dinesh.

The trials exposed the depth of Indian wrestling. Several bouts went to the wire, with wrestlers who narrowly missed selection likely to serve as alternates or travel reserves. The 74-kilogram and 86-kilogram categories, in particular, produced finals where the margins were thin enough that either finalist could have plausibly represented India.

## Greco-Roman Confidence

The Greco-Roman unit arrives in Aichi-Nagoya with quiet momentum. Led by **Sunil Kumar**, the 2023 Asian Games bronze medallist, the squad has been on an upward trajectory following strong results at the recent Asian Championships. Greco-Roman has historically been India's weaker wrestling discipline, but the recent cycle has produced a group of technically refined competitors who are no longer content with participation medals.

## The Diaspora Angle

Wrestling remains one of India's most deeply traditional sports, rooted in the akharas of Haryana, Punjab, and western Uttar Pradesh. But the globalisation of the sport has not passed it by. Several wrestlers on the squad have trained extensively overseas — Punia at the University of Michigan wrestling programme, Sehrawat at camps in Georgia and Dagestan. The NRI community has also played a quiet role: diaspora-funded wrestling academies in Haryana have produced multiple national-level competitors in the last five years, and Indian-American wrestling enthusiasts have helped connect Indian coaches with American collegiate programmes.

For the diaspora watching from abroad, the Asian Games will carry particular weight. Wrestling is one of the few Olympic sports where India has a realistic shot at multiple medals in a single edition. In Hangzhou in 2023, India won five wrestling medals. The squad finalized in Lucknow on Sunday has the credentials to match or exceed that total.

## What's Next

The squad is expected to enter a centralized training camp in the coming weeks, with a possible overseas training stint before the Asian Games. The women's wrestling trials will follow shortly, with Antim Panghal and Vinesh Phogat expected to feature prominently.

The 2026 Asian Games wrestling competition in Aichi-Nagoya is scheduled for September.

**Sources:** IANS, ANI, Wrestling Federation of India, IndiaSportsHub""",
    "image_search_person": "Aman Sehrawat wrestler",
    "image_pexels_query": "wrestling competition India mat",
    "image_pexels_fallback": "wrestling sport competition",
    "sources": ["IANS", "ANI", "Wrestling Federation of India", "LatestLY"],
    "is_editorial": False,
})

# ── publish ──────────────────────────────────────────────────────────
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
published = 0

for art in articles:
    print(f"\n{'='*60}")
    print(f"Publishing: {art['headline'][:70]}...")

    # Image sourcing — Wikipedia first for person articles
    img_url = None
    person = art.get("image_search_person")
    if person:
        img_url = fetch_wikipedia_person_image(person)
        # Try alternate name forms
        if not img_url and " " in person:
            # Try just the first part
            alt = person.split()[0] + " " + person.split()[1] if len(person.split()) > 1 else person
            img_url = fetch_wikipedia_person_image(alt)

    if not img_url:
        img_url = fetch_pexels_image(art.get("image_pexels_query"), art.get("image_pexels_fallback"))

    if img_url and not validate_image(img_url):
        print(f"  ⚠ Image validation failed, trying Pexels fallback")
        img_url = fetch_pexels_image(art.get("image_pexels_query"), art.get("image_pexels_fallback"))
        if img_url and not validate_image(img_url):
            print(f"  ⚠ Pexels fallback also failed validation, skipping image")
            img_url = None

    # Determine attribution
    img_attr = None
    if img_url:
        if "wikimedia" in img_url or "wikipedia" in img_url:
            img_attr = "Wikimedia Commons"
        elif "pexels" in img_url:
            img_attr = "Pexels"
        else:
            img_attr = "The Videshi"

    # Build payload
    word_count = len(art["body"].split())
    reading_time = max(1, round(word_count / 250))

    payload = {
        "headline": art["headline"],
        "subheadline": art["subheadline"],
        "slug": art["slug"],
        "category": art["category"],
        "body": art["body"],
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "sources": art["sources"],
        "word_count": word_count,
        "vertical": "sports",
        "urgency": "daily",
    }

    if img_url:
        payload["image_url"] = img_url
    if img_attr:
        payload["image_attribution"] = img_attr

    result = sb_insert("p2_articles", payload)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id={art_id})")
        print(f"    Words: {word_count}, Reading time: {reading_time} min")
        if img_url:
            print(f"    Image: {img_url[:80]}...")
            # Upload to Supabase storage for permanence
            if "wikimedia" in (img_url or "") or "wikipedia" in (img_url or ""):
                uploaded = upload_to_supabase_storage(img_url, f"{art_id}.jpg")
                if uploaded:
                    sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": uploaded, "image_attribution": "Wikimedia Commons"})
                    print(f"    ✓ Replaced with Supabase storage URL")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"Done. Published {published}/{len(articles)} articles.")
