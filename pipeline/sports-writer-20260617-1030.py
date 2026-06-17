#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (10:30 UTC run)
Article: Neeraj Chopra's confirmed comeback at the Doha Diamond League on June 19,
his first competition in 274 days after a back injury that kept him out all season.
Distinct from the June 14 piece on his conditional CWG selection — this is the
return-to-competition news hook, the field he faces, and what's at stake.
Diaspora angle: Neeraj is India's most globally followed track-and-field athlete;
NRIs treat his throws as appointment viewing, and Doha is where he first broke 90m.
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
print("ARTICLE: Neeraj Chopra \u2014 Doha Diamond League comeback")
print("="*60)

art_slug = "neeraj-chopra-doha-diamond-league-2026-comeback-274-days-back-injury-first-throw-arshad-nadeem-cwg-nri"
art_headline = "274 Days Without a Throw. On Friday, Neeraj Chopra Finally Returns \u2014 in the City Where He First Broke 90 Metres."
art_subheadline = "India's two-time Olympic javelin medallist will open his 2026 season at the Doha Diamond League on June 19, his first competition since a back injury wrecked his World Championships last September. He walks into a nine-man field led by a Sri Lankan who has already thrown 92.62m this year."

art_body = """For the first time in 274 days, Neeraj Chopra will pick up a javelin in front of a crowd that is keeping score. India's most decorated track-and-field athlete will return to competition at the Doha Diamond League on Friday, June 19, ending months of speculation about when \u2014 and whether \u2014 the two-time Olympic medallist would compete in 2026 at all.

The confirmation, announced by his management firm Vel Sports on Instagram with the line "The wait is over. First throw of 2026 lands in Doha," closes a chapter that has been unusually quiet by Chopra's standards. He has not thrown in anger since the World Athletics Championships in Tokyo on September 18, 2025, where a recurring back injury hampered him and he finished eighth with 84.03m. For a man who had not finished off a podium in 2,566 days before that night, the result was a jolt \u2014 and the long silence that followed only deepened the unease.

## A Comeback Built Quietly in Switzerland

Behind the scenes, the rebuild has been deliberate. After Tokyo, Chopra parted ways with his coach Jan \u017dern\u00fd \u2014 the javelin world record holder \u2014 and returned to his very first coach, Jai Chaudhary, at Switzerland's Bienne Olympic Training Centre as part of a 47-day training programme. The Athletics Federation of India struck an optimistic note in the days before the Doha announcement. "Neeraj is now training and getting ready to compete probably in the next 10 days or so. He is recovering well and recovering fast," AFI vice-president Adille Sumariwalla said.

Chopra was a late addition to the Doha field \u2014 his name was absent from the entry list organisers released on June 12, and appeared only after his fitness was confirmed. It is a sign of how carefully his team has managed expectations: no premature commitments, no comeback date until the back had been tested in training.

## The Field He Walks Into

Doha will not be a gentle re-entry. The nine-man javelin field is among the strongest of the early season, headlined by Sri Lanka's Rumesh Tharanga Pathirage, who stunned the event in Rome on June 4 with a 92.62m throw that makes him the season leader \u2014 a distance beyond anything Chopra has produced in competition. Also in the mix are reigning world champion Keshorn Walcott of Trinidad and Tobago, two-time world champion Anderson Peters of Grenada, Olympic and world silver medallist Jakub Vadlejch of Czechia, Pan American Games gold medallist Curtis Thompson of the USA, and the evergreen Julius Yego of Kenya.

Notably absent is Pakistan's Olympic champion Arshad Nadeem, whose participation had been floated on June 12 but who did not figure in the final list \u2014 denying fans an early renewal of South Asia's most compelling individual rivalry.

## Why Doha, of All Places

There is a neatness to the venue. It was at the 2025 Doha Diamond League, at the Khalifa International Stadium, that Chopra first breached the 90-metre barrier he had chased for years, recording a national record 90.23m \u2014 though even that monster throw left him second behind Germany's Julian Weber (91.06m). Returning to the scene of his personal best to relaunch his career is the kind of full-circle story Indian sport rarely scripts so cleanly.

The Doha meet is the seventh stop of the 2026 Diamond League season, which runs to its finals in Brussels in early September. For Chopra, though, it is less about Diamond League points than about answering a single question: is the back sound enough to carry him through a packed year?

## What's Still at Stake

That year includes the Commonwealth Games in Glasgow from July 23 to August 2, for which the AFI named Chopra in a 32-member contingent on June 14. But his selection is conditional \u2014 he must hit the federation's qualifying standard of 82.61m before the Games, the same bar cleared by fellow throwers Rohit Yadav and Yashvir Singh in Ludhiana. A clean, healthy outing in Doha would all but settle that question and clear his path to Glasgow as one of three Indian javelin throwers.

For the Indian diaspora, Chopra's return carries weight that transcends a single meet. He is the rare Indian athlete in an individual Olympic discipline who has become genuinely global \u2014 the man who ended India's 100-year wait for an Olympic athletics gold in Tokyo and backed it up with silver in Paris. NRIs across the United States, Britain, Canada and the Gulf treat his competitions as appointment viewing, often setting alarms for awkward hours to watch a single six-throw series. When he steps onto the runway in Doha on Friday, a diaspora that has waited nine months alongside him will be watching the first throw land \u2014 hoping it signals that the most reliable figure in Indian sport is, once again, back."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Neeraj Chopra, India's two-time Olympic javelin medallist, returns at the Doha Diamond League on June 19"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Neeraj Chopra")
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
        {"name": "PTI \u2014 Neeraj Chopra to return to action at Doha Diamond League", "url": "https://www.ptinews.com/"},
        {"name": "The Bridge \u2014 Neeraj Chopra set for season opener at Doha Diamond League", "url": "https://thebridge.in/"},
        {"name": "RevSportz \u2014 Neeraj Chopra set for return at Doha Diamond League after 274-day hiatus", "url": "https://revsportz.in/"},
        {"name": "IANS \u2014 After injury layoff, Neeraj Chopra set to start season in Doha Diamond League", "url": "https://ianslive.in/"},
    ]),
    "diaspora_angle": "Neeraj Chopra is India's most globally followed track-and-field athlete \u2014 the man who ended a 100-year wait for Olympic athletics gold \u2014 and NRIs across the US, UK, Canada and the Gulf treat his competitions as appointment viewing, often setting alarms for awkward hours to watch a single throw.",
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
