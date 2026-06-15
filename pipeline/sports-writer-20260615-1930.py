#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (19:30 UTC run)
Article: India's women head to Headingley to face the Netherlands on June 17,
fresh off a 64-run demolition of Pakistan at Edgbaston. A look ahead at the
fixture, the in-form Women in Blue, and why Yorkshire's huge South Asian
community makes Leeds a home away from home.
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
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        content = None
        if r.status_code != 200:
            import subprocess
            tmp = f"/tmp/{filename}"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                content = open(tmp, "rb").read()
            else:
                print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
                return None
        else:
            ct = r.headers.get("Content-Type", "")
            if not ct.startswith("image/"):
                print(f"  \u2717 Not an image: {ct}")
                return None
            if len(r.content) < 5000:
                print(f"  \u2717 Image too small: {len(r.content)} bytes")
                return None
            content = r.content

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
print("ARTICLE: India Women vs Netherlands, Headingley preview")
print("="*60)

art_slug = "india-women-netherlands-t20-world-cup-2026-headingley-leeds-preview-harmanpreet-deepti-mandhana-nri"
art_headline = "They Crushed Pakistan by 64 Runs. Now India's Women Take Their Show to Yorkshire's Desi Heartland."
art_subheadline = "Fresh off Deepti Sharma's record 5 for 10 and Smriti Mandhana's defiant 68, Harmanpreet Kaur's side meet the Netherlands at Headingley on Wednesday \u2014 a near-formality on paper, but a chance to keep building toward the T20 title that has always eluded them."

art_body = """India's women could hardly have asked for a more emphatic start to their Women's T20 World Cup campaign. At a sold-out Edgbaston on Saturday, Harmanpreet Kaur's side dismantled Pakistan by 64 runs in a contest that was effectively over by the midpoint. On Wednesday they travel north to Headingley in Leeds for their second Group 1 fixture, against a Netherlands side that, on paper, should offer little resistance. But for the Women in Blue \u2014 World Cup semi-finalists five times over without ever lifting this particular trophy \u2014 every match is now a brick in a structure they have been trying to build for a decade.

## A Statement at Edgbaston

The win over Pakistan was a near-perfect performance. Smriti Mandhana, dropped twice early, made the fielders pay with a composed 68 off 44 balls, anchoring an Indian total of 170 for 6 alongside a typically belligerent cameo from wicketkeeper Richa Ghosh. It was a score that always looked beyond Pakistan on a true Birmingham surface.

Then came the demolition. Off-spinning all-rounder Deepti Sharma produced the best bowling figures in the history of women's T20 internationals, taking 5 for 10 as Pakistan folded for 106. The spell carried Deepti past the milestone of leading wicket-taker in women's T20I history \u2014 a reminder that India's strength in this format lies not only in its celebrated top order but in a deep, varied bowling attack built for English conditions.

## The Netherlands Test

The Netherlands arrive at Headingley as the group's clear underdogs. Cricket in the country remains semi-professional, and the gulf in resources, exposure and depth between the Dutch and a fully professionalised Indian set-up is stark. India will start as overwhelming favourites, and a comfortable win would all but secure their passage toward the semi-finals from a group that also contains Australia, South Africa, Bangladesh and Pakistan.

The danger, as ever in these games, is complacency. India's management will likely use the fixture to fine-tune combinations and give batters such as Jemimah Rodrigues and Shafali Verma valuable time in the middle ahead of sterner tests. Harmanpreet has spoken repeatedly about the team treating the tournament one game at a time after the heartbreak of past near-misses, and the captain will be wary of any drop in intensity against lesser opposition.

## Why Headingley Matters

There is a reason this fixture feels like more than a routine group game for the diaspora. Leeds and the wider West Yorkshire region \u2014 Bradford in particular \u2014 are home to one of the largest South Asian communities in Britain, with deep roots in Punjab, Gujarat, Kashmir and beyond. Headingley has long been one of English cricket's most raucous venues when India or Pakistan come to town, the stands a sea of blue shirts and tricolour flags.

For families who came to Yorkshire's mill towns generations ago, an Indian women's team playing a World Cup match a short drive away is a genuine occasion \u2014 a chance to take children and grandchildren to see Mandhana, Harmanpreet and Deepti in the flesh, the kind of access to the national side that simply did not exist for the women's game even a few years ago.

## The Bigger Picture

India won the 50-over World Cup on home soil in 2025, a watershed moment that transformed the profile of the women's game across the country and its diaspora. The T20 crown remains the conspicuous gap on the mantelpiece. With a top order in form, a bowling unit setting records, and a captain determined not to let history repeat itself, this is arguably India's strongest-ever chance to complete the set.

Wednesday at Headingley is unlikely to be the match that defines the campaign. But for the thousands of British Indians who will fill the ground, it is a date that was circled on the calendar the moment the fixtures were released \u2014 a World Cup, a in-form team, and a corner of England where the desi roar is as loud as anywhere on earth.
"""

print("\nSourcing image...")
img_url = fetch_wikipedia_person_image("Harmanpreet Kaur")
img_caption = "India captain Harmanpreet Kaur with the 2025 Women's Cricket World Cup trophy"
img_attribution = "Wikimedia Commons"

img_final = None
if img_url:
    img_final = upload_to_supabase(img_url, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "The Sporting News", "url": "https://www.sportingnews.com"},
        {"name": "SportsCafe", "url": "https://sportscafe.in"},
        {"name": "ICC / ESPNcricinfo", "url": "https://www.espncricinfo.com"},
        {"name": "Mint", "url": "https://www.livemint.com"},
    ]),
    "diaspora_angle": "India's women play their June 17 World Cup match at Headingley in Leeds, the heart of one of Britain's largest South Asian communities, giving British Indian families across West Yorkshire a rare chance to watch Harmanpreet Kaur's in-form side in person.",
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
