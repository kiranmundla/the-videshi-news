#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (22:30 UTC run)
Article: India lead Afghanistan 1-0 and can seal the three-match ODI series at
Lucknow on June 17 — in Shubman Gill's first ODI series as full-time captain.
A preview/analysis pegged to the Jaiswal-vs-Kishan No.3 debate, the selection
continuity criticism from K Srikkanth, and what a series win would mean for a
young captain chasing his first piece of ODI silverware before the 2027 WC.
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
print("ARTICLE: India vs Afghanistan 2nd ODI, Lucknow — Gill's series test")
print("="*60)

art_slug = "india-afghanistan-2nd-odi-lucknow-shubman-gill-first-series-win-jaiswal-kishan-no3-debate-2026-nri"
art_headline = "One More Win and Shubman Gill Lifts His First Trophy as India's ODI Captain. In Lucknow, the Real Question Is Who Bats at No. 3."
art_subheadline = "India lead Afghanistan 1-0 and can seal the three-match series at the Ekana Stadium on Wednesday. But with Virat Kohli injured, the contest within the contest \u2014 Yashasvi Jaiswal versus Ishan Kishan for the most coveted spot in Indian batting \u2014 is the story that will outlast the result."

art_body = """India return to Lucknow on Wednesday holding a 1-0 lead and a chance to do something Shubman Gill has not yet managed in his young tenure: win an ODI series as the full-time captain of the Men in Blue. A victory over Afghanistan at the Bharat Ratna Shri Atal Bihari Vajpayee Ekana Stadium would seal the three-match contest with a game to spare and hand the 26-year-old his first piece of silverware in a role that, for all his batting pedigree, still carries the weight of expectation.

## A Captain Still Proving Himself

Gill's elevation to the ODI captaincy was meant to signal the start of a new era. His first assignment, a three-match series in Australia in October 2025, ended in a 1-2 defeat \u2014 a chastening introduction to leadership at the highest level. With the ODI World Cup in 2027 now firmly on the horizon and India still chasing the 50-over crown that has eluded them since 2011, every series has become a referendum on whether Gill is the man to end that wait.

The first ODI in Dharamsala offered reassurance. In a rain-truncated, 25-overs-a-side affair that played out almost like a T20, Gill brought his prolific IPL form straight into international colours, anchoring the chase with an unbeaten 84 at better than a run a ball as India cruised home by seven wickets. Two debutants, Gurnoor Brar and Harsh Dubey, took three wickets apiece, while Afghanistan's Rahmanullah Gurbaz lit up the contest with a 51-ball 102 that ultimately counted for little.

## The No. 3 Question

The intrigue heading into Lucknow is not whether India will win \u2014 they remain heavy favourites \u2014 but who will occupy the most storied position in their batting order. Virat Kohli, who has made the No. 3 slot his own across two decades, was ruled out of the series with a hamstring injury sustained during the IPL 2026 final, where he struck an unbeaten 75 to seal Royal Challengers Bengaluru's title defence.

His designated replacement, Yashasvi Jaiswal, has yet to feature. In the opener, India instead handed the role to Ishan Kishan, the wicketkeeper-batter enjoying a striking career resurgence. Six months ago Kishan did not hold a BCCI central contract; since leading Jharkhand to their first Syed Mushtaq Ali Trophy and starring in India's successful T20 World Cup defence, he has become, in Aakash Chopra's memorable phrase, "God's favourite child." His IPL numbers \u2014 602 runs at a strike rate above 182 \u2014 dwarf Jaiswal's returns from the same tournament.

Jaiswal, for his part, can point to an unbeaten 116 in his most recent ODI innings, against South Africa last December. That a player capable of that remains on the bench speaks to the riches India can currently call upon, and to the selectorial logjam that has frustrated observers.

## The Continuity Critique

Former India opener Kris Srikkanth captured the unease bluntly, arguing that the team management has mishandled in-form batters. "Ruturaj and Jaiswal must be wondering why they aren't there despite scoring centuries in their last ODI innings," he said, referring also to Ruturaj Gaikwad, currently with India A in Sri Lanka. "You score a century three to four months back and still get forgotten. The lack of continuity is what's hurting them."

It is a debate that cuts to the heart of Indian cricket's enviable problem: an embarrassment of batting talent and only so many places. If India seal the series on Wednesday, the management may well use the dead-rubber third ODI in Chennai on June 20 to test its bench \u2014 and finally give Jaiswal a run.

## Why It Matters to the Diaspora

For the millions of NRIs who follow every ball from living rooms in New Jersey, Toronto, London and Sydney, this series is more than a routine home assignment against a developing side. It is the first real look at the Gill-led ODI project in subcontinental conditions, a dress rehearsal for the build-up to a World Cup that diaspora fans will once again organise their lives around. Afghanistan, who have won five of their six ODI series this cycle, are no pushovers \u2014 and a clinical India performance in Lucknow would send a quiet message about the direction of travel.

For Gill, the equation is simple. Win, and he has his first trophy as captain, a marker laid down on the long road to 2027. The selection puzzles can wait for Chennai.
"""

print("\nSourcing image...")
img_url = fetch_wikipedia_person_image("Shubman Gill")
img_caption = "India ODI captain Shubman Gill, who leads the side against Afghanistan"
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
        {"name": "CricTracker", "url": "https://www.crictracker.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Sportskeeda", "url": "https://www.sportskeeda.com"},
        {"name": "Yardbarker", "url": "https://www.yardbarker.com"},
    ]),
    "diaspora_angle": "The Afghanistan ODI series is the first real test of Shubman Gill's leadership in subcontinental conditions ahead of the 2027 World Cup, the tournament diaspora cricket fans across the US, UK and Canada will once again rally around.",
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
