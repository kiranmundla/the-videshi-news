#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (01:30 UTC run)
Article: Selva Prabhu wins the 2026 NCAA Outdoor triple jump title at Hayward
Field, Eugene — India's first NCAA outdoor athletics title in four years (since
Tejaswin Shankar's high jump gold in 2022). A 21-year-old from Madurai at Kansas
State, leaping 16.92m to beat a 24-man field. Diaspora angle: the NCAA has become
the off-ramp pipeline through which a generation of Indian track-and-field talent
is now developing inside the US college system.
"""

import os, sys, json, io
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

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def fetch_wikipedia_person_image(person_name):
    encoded = person_name.replace(" ", "_")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
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
        import subprocess
        tmp = f"/tmp/{filename}"
        subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
        if not (os.path.exists(tmp) and os.path.getsize(tmp) > 5000):
            print(f"  \u2717 Download failed for {img_url[:80]}")
            return None
        content = open(tmp, "rb").read()

        compressed = compress_image(content)
        print(f"  \U0001f4e6 Compressed to {len(compressed)/1024:.0f} KB")

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
        headers=HEADERS, json=article, timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


print("\n" + "="*60)
print("ARTICLE: Selva Prabhu — NCAA Outdoor triple jump champion")
print("="*60)

art_slug = "selva-prabhu-ncaa-outdoor-triple-jump-champion-2026-kansas-state-madurai-hayward-field-india-college-pipeline-nri"
art_headline = "A 21-Year-Old From Madurai Just Won an NCAA Title in Eugene. It Was India's First in Four Years."
art_subheadline = "Selva Prabhu leapt 16.92m at Hayward Field to take the 2026 NCAA Outdoor triple jump crown for Kansas State \u2014 India's first NCAA outdoor athletics title since Tejaswin Shankar in 2022, and the latest proof that the American college system has become a real pathway for Indian track and field."

art_body = """When Selva Prabhu came down the runway at Hayward Field on Friday evening, the most storied track-and-field venue in the United States, he was carrying more than his own ambitions. He fouled four of his six attempts, struggling to find the board on a stage built for exactly this kind of pressure. But his second jump \u2014 16.92m, into a legal wind \u2014 was enough. It topped a 24-man field, held the lead to the final attempt, and made the 21-year-old from Madurai the 2026 NCAA Outdoor triple jump champion.

It is a result that travels a long way beyond Eugene, Oregon. Prabhu's gold is India's first NCAA outdoor athletics title in four years, since Tejaswin Shankar won the high jump in 2022. For a country whose athletes have historically had nowhere to develop between the junior ranks and the senior international circuit, the American collegiate system has quietly become one of the most important finishing schools Indian track and field has ever had access to.

## The Jump

Prabhu, a sophomore at Kansas State, did it the hard way. "He just competed like the champion and the warrior that he is," head coach Travis Geopfert said afterward. "He went out there early, executed early, and won a national title for K-State." The winning mark of 16.92m \u2014 some reports list it at 16.94m \u2014 edged Kevin Kemboi's 16.84m for the title. It was not even Prabhu's best of the season; in May he had jumped 17.19m to win the Big 12 Championship, though with a wind reading well over the legal limit.

For Kansas State, the achievement was historic in its own right. Prabhu became the first men's outdoor triple jump champion for the school since Kenny Harrison \u2014 a future Olympic gold medallist \u2014 won it in 1986. Alongside long jump champion Tafadzwa Chikomba, the Wildcats crowned two field-event national champions in the same season for the first time in program history, and finished eighth in the team standings, their highest placing since 1998.

## A Pathway, Not a One-Off

What makes Prabhu's win resonate with the diaspora is that he is not an isolated case. He is one node in a fast-growing network of Indian athletes who have chosen the NCAA route \u2014 trading the patchy domestic competition calendar back home for world-class coaching, sports science, modern facilities, and the relentless week-in, week-out competition that the American college system provides.

This season alone, Indian names dotted the NCAA meet sheets: Lokesh Sathyanathan cleared 8.01m in the long jump, Krishna Jayasankar threw 17.09m in the shot put and broke 55m in the discus, and Sharvari Parulekar made her NCAA outdoor debut in the women's triple jump for Louisville. The template was set by Shankar, who used a Kansas State scholarship to become a two-time NCAA high jump champion before going on to win Commonwealth Games bronze for India in 2022.

For Indian-origin families across the United States \u2014 many of whom send their own children into the same college athletics system for very different, academic-first reasons \u2014 the sight of a Madurai teenager standing atop an NCAA podium is a particular kind of validation. It says the pipeline they have invested in works in both directions: it can take an American-raised second-generation kid to a Division I roster, and it can take a kid straight out of Tamil Nadu to a national title.

## What It Means for India

Prabhu's personal best of 17.05m, set at the NCAA Indoor Championships in March, is the Indian indoor national record in the event. The senior outdoor national record, 17.37m, belongs to Praveen Chithravel, and that gap is the one Prabhu will now spend the next two years of college eligibility trying to close. His jumps have already cleared the Athletics Federation of India's qualifying standard for the 2026 Asian Games, though selection there also requires a minimum number of domestic appearances \u2014 a bureaucratic wrinkle that has long complicated life for India's overseas-based athletes.

That tension \u2014 between an athlete developing abroad and a federation that wants to see him at home \u2014 is itself a diaspora story, and a recurring one across Indian sport this month, from footballers carrying foreign flags to the debate over passports and overseas-based players. Prabhu sits squarely inside it: an Indian athlete being made into a champion by an American system, now expected to come home to prove himself.

For now, the result speaks plainly enough. On a June evening at Hayward Field, with the silver and purple of Kansas State on his chest and the tricolour in his story, a 21-year-old from Madurai jumped further than anyone else in American college athletics. The next stop, the Asian Games in Aichi-Nagoya later this year, will test whether the pipeline that produced him can carry him onto a senior international podium too."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Hayward Field in Eugene, Oregon, where Selva Prabhu won the 2026 NCAA Outdoor triple jump title for Kansas State"
img_attribution = "Wikimedia Commons"
img_final = None

# No Wikipedia/Commons photo of Selva Prabhu exists; use a specific photo of the
# actual venue (Hayward Field) rather than a generic stock image.
cand = fetch_wikipedia_person_image("Selva Prabhu")
if not cand:
    cand = "https://upload.wikimedia.org/wikipedia/commons/b/b6/Hayward_Field_%28Eugene%2C_USA%29_2021.jpg"

if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "athletics",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "The Bridge \u2014 Selva Prabhu clinches the 2026 NCAA Outdoor Triple Jump title", "url": "https://thebridge.in/athletics/selva-prabhu-2026-ncaa-outdoor-triple-jump-title"},
        {"name": "Kansas State Athletics \u2014 Prabhu Crowned Triple Jump Champion", "url": "https://www.kstatesports.com"},
        {"name": "NCAA.com \u2014 2026 NCAA outdoor track and field championships results", "url": "https://www.ncaa.com/news/trackfield-outdoor-men/article/2026-06-10/2026-ncaa-outdoor-track-and-field-championships-schedule-location-how-watch-results"},
        {"name": "World Athletics \u2014 Selva Prabhu Thirumaran profile", "url": "https://worldathletics.org"},
    ]),
    "diaspora_angle": "Selva Prabhu's NCAA title shows how the American college system has become a real development pathway for Indian track-and-field talent \u2014 a pipeline diaspora families already know intimately, now producing national champions.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
