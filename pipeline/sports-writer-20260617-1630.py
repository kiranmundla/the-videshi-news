#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (16:30 UTC run)
Article: India Women's 209/5 vs Netherlands at Headingley — their highest total of
the 2026 Women's T20 World Cup — built on a 115-run opening stand between Smriti
Mandhana (74) and Shafali Verma (55). India cruised to a dominant win and went top
of Group A. Distinct from the June 15 PREVIEW piece (this is the RESULT/report).
Diaspora angle: India's women are building toward a maiden T20 World Cup title;
NRIs in the UK packed Headingley and follow this side as closely as the men's team.
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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
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
print("ARTICLE: India Women 209/5 \u2014 highest WC total vs Netherlands")
print("="*60)

art_slug = "india-women-209-5-highest-t20-world-cup-total-mandhana-74-shafali-55-netherlands-headingley-2026-nri"
art_headline = "India's Women Just Posted Their Highest-Ever World Cup Total. Mandhana and Shafali Took 11 Overs to Bury the Netherlands."
art_subheadline = "Smriti Mandhana (74 off 47) and Shafali Verma (55 off 38) shared a 115-run opening stand and brought up India's joint-fastest team fifty in Women's T20 World Cup history. India's 209 for 5 at Headingley was the most they have ever made at a World Cup \u2014 and a debutant Netherlands side never stood a chance."

art_body = """LEEDS \u2014 Put in to bat under overcast Yorkshire skies that were supposed to help the bowlers, India's women instead produced the most destructive batting display of the 2026 Women's T20 World Cup. Their 209 for 5 against the Netherlands at Headingley on Wednesday was the highest total India have ever posted at a World Cup, and it set up a win so comprehensive that the result was effectively settled inside the first hour.

At the heart of it was an opening partnership that the Dutch debutants simply could not contain. Smriti Mandhana, in imperious touch, top-scored with 74 off 47 balls, striking 11 fours and a six. Shafali Verma matched her stroke for stroke at the other end, reaching her maiden World Cup fifty off 34 balls before falling for 55 off 38. Together they put on 115 for the first wicket \u2014 a stand that took India past the point of no return before the Netherlands had taken a single wicket.

## A Powerplay That Broke the Game Open

The tone was set immediately. Shafali opened the face of the bat to steer Iris Zwilling for four, then rocked back to cut Heather Siegers through extra cover. Mandhana joined the assault with crisp drives, and when she lofted Zwilling over extra cover and punched through the same region, India brought up their team fifty inside 5.1 overs \u2014 the joint-fastest in Women's T20 World Cup history.

The Netherlands, playing in their first-ever Women's T20 World Cup and meeting India for the first time in any T20 international, compounded their problems with wayward bowling. Debutant Myrthe van den Raad's nervy first over leaked six wides, and India surged to 59 without loss at the end of the powerplay. Dropped catches and missed run-outs only deepened the sense that the Dutch were chasing shadows.

https://www.instagram.com/p/DZhv0OQDW1r/

## The Finishers Twist the Knife

Even after the openers fell \u2014 Shafali for 55, Mandhana holing out to cover for 74 \u2014 India did not relent. Richa Ghosh walked in and wasted no time, blazing an unbeaten 20 off just eight balls, while Deepti Sharma chipped in with a rapid 10 not out off two deliveries. Jemimah Rodrigues (19) and Harmanpreet Kaur (12) kept the scoreboard ticking through the middle. The late surge carried India to 209 for 5, comfortably their best at any World Cup and a statement of the depth this batting order now carries from top to bottom.

In reply, the Netherlands were always playing for pride rather than the result. Babette de Leede top-scored with a busy knock before being stumped by Ghosh off Nandni Sharma, but with a required rate hovering near 18 an over, the Dutch never threatened the target. India's spinners and the disciplined Nandni Sharma kept chipping away to seal a thumping win.

## Two from Two, and a Net Run Rate Statement

The victory leaves Harmanpreet Kaur's side unbeaten after two matches in Group A, following their 64-run demolition of arch-rivals Pakistan in Birmingham. Just as importantly in a tight group that also features Australia, South Africa and Bangladesh, the margin gave India's net run rate a hefty boost \u2014 a number that could prove decisive when semi-final qualification is settled. After a rusty if convincing start against Pakistan, India will be delighted that the "perfect game" their management had been hunting arrived against the tournament's weakest side.

For the Indian diaspora, this campaign carries a particular charge. India's women have never won a senior global title, falling agonisingly short in the 2017 ODI World Cup final and the 2020 T20 World Cup final, and a generation of NRI families in Britain has watched them grow into genuine contenders. Headingley, in the heart of Yorkshire's large South Asian community, drew a vocal, flag-waving crowd that treated Mandhana's boundaries like home fixtures. With Mandhana now in the form of her life and a batting order that produced its highest World Cup total against opposition it had never faced before, the question following India around England is no longer whether they can compete \u2014 it is whether this is finally the year they go all the way."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Smriti Mandhana, who top-scored with 74 off 47 balls as India posted their highest-ever Women's T20 World Cup total"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Smriti Mandhana")
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
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "IANS \u2014 Women's T20 WC: Smriti and Shafali fifties carry India to 209/5 against Netherlands", "url": "https://ianslive.in/"},
        {"name": "Cricbuzz \u2014 India Women vs Netherlands Women, 10th Match, Group A, ICC Women's T20 World Cup 2026", "url": "https://www.cricbuzz.com/live-cricket-scores/121846/10th-match-group-a-icc-womens-t20-world-cup-2026"},
        {"name": "Cricketaddictor \u2014 India Women vs Netherlands Women Full Scorecard, Match 10, 17 June 2026", "url": "https://cricketaddictor.com/"},
        {"name": "ICC \u2014 ICC Women's T20 World Cup 2026", "url": "https://www.icc-cricket.com/"},
    ]),
    "diaspora_angle": "India's women have never won a senior global title, and a generation of NRI families in Britain has watched them grow into genuine contenders \u2014 Headingley, in the heart of Yorkshire's South Asian community, drew a vocal, flag-waving diaspora crowd.",
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
