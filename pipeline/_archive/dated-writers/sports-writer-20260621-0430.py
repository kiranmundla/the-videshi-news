#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (04:30 UTC slot)
Article: India vs England 1st Test, Headingley, Day 1 — India 359/3 at stumps.
New captain Shubman Gill 127* (175) on his captaincy debut; Yashasvi Jaiswal
101 (159) on his first innings in England; Rishabh Pant 65* (102), past 3,000
Test runs. KL Rahul 42, debutant Sai Sudharsan 0, Karun Nair recalled after 8
years. Stokes won toss and bowled; Stokes 2/43. Anderson-Tendulkar Trophy.

ANGLE: Dedup-checked — the 2026-06-20 01:45 sports article was the SERIES
PREVIEW ("India Begin in England Without Rohit and Kohli"). The Day 1 RESULT
(twin centuries, Gill's captaincy-debut ton, India 359/3) is fresh and
uncovered. Diaspora angle: the first day of the post-Kohli/Rohit India Test
era, led by a new captain who delivered.

Hero: Wikipedia portrait of Shubman Gill (captain, the story); fallback to
Yashasvi Jaiswal / Rishabh Pant, then Commons Headingley/cricket imagery.
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


def fetch_wikimedia_commons_images(search_query, limit=8):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    out = []
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for p in pages.values():
                ii = (p.get("imageinfo") or [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and mime.startswith("image/") and ii.get("width", 0) >= 800:
                    out.append({"url": url, "title": p.get("title", ""),
                                "w": ii.get("width"), "h": ii.get("height")})
    except Exception as e:
        print(f"  \u26a0 Commons error for '{search_query}': {e}")
    return out


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
            data=compressed, timeout=30,
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
print("ARTICLE: India 359/3 Day 1 Headingley — Gill & Jaiswal tons")
print("="*60)

art_slug = "india-england-first-test-headingley-day-one-gill-jaiswal-centuries-359-3-post-kohli-rohit-era-diaspora-nri"
art_headline = "On the First Day of the Post-Kohli Era, Two Centuries Said India Will Be Just Fine"
art_subheadline = "Shubman Gill marked his first Test as captain with an unbeaten 127, Yashasvi Jaiswal made 101 on his maiden innings in England, and India closed Headingley's opening day on 359 for three."

art_body = """For a generation of Indian cricket followers, the question hanging over this tour was less about runs than about identity. Virat Kohli and Rohit Sharma, the two men who defined India's red-ball cricket for more than a decade, had retired from the format within weeks of each other, and the team that walked out at Headingley on Friday was the first in living memory to take the field in a Test without either name on the sheet. By stumps on the opening day of the Anderson-Tendulkar Trophy, the anxiety had given way to something closer to relief: India 359 for three, two centuries on the board, and a new captain who looked very much like he belonged.

That captain is Shubman Gill, and his unbeaten 127 was the kind of innings that quiets a dressing room's nerves and a fanbase's doubts in a single afternoon. Reaching three figures in his first Test in charge, he joined an elite roll call of Indians — Vijay Hazare, Sunil Gavaskar, Dilip Vengsarkar and Kohli himself — to score a hundred in their maiden innings as captain. It was Gill's sixth Test century but his first outside Asia, the gap in his record that his critics always pointed to, now closed on the most demanding stage English cricket offers.

## A Toss Lost, an Advantage Squandered

England captain Ben Stokes won the toss under overcast skies and, true to the aggressive instincts of his side, chose to bowl. The Headingley pitch has historically rewarded that call — six of the last Tests here had been won by the team bowling first — but the heat, the quick outfield and a surface with no real demons turned Stokes's gamble into a long, draining day in the field.

India's openers made him pay. Yashasvi Jaiswal, playing his first Test innings on English soil, and KL Rahul put on 91 for the first wicket, blending caution with the kind of crisp driving that punishes anything overpitched. Nine boundaries came in the first hour alone, and for the first time in seven Tests at this venue there was no wicket inside the opening ten overs.

## Jaiswal Announces Himself in England

Jaiswal, who tormented England with 712 runs the last time the sides met in India, shelved his more explosive instincts and built. He survived a review, weathered a few short-ball examinations, and battled cramp in his right hand on the way to his fifth Test hundred — his third against England, and the first he has made in their conditions. He reached the milestone in 144 balls before Stokes, the pick of England's bowlers, finally bowled him for 101, ending a 129-run third-wicket stand with Gill.

The middle had wobbled briefly before that. Rahul fell for 42, edging Brydon Carse to slip, and debutant Sai Sudharsan — handed his cap as the man to fill the vacated No. 3 spot after a prolific IPL and domestic season — was caught behind for a duck off Stokes, two quick blows that gave England a flicker of hope just before lunch. It did not last.

## Gill and Pant Take Over

What followed was the day's defining passage. Gill came in standing outside his crease to counter the movement, found his rhythm immediately, and raced to a fifty off 56 balls, his quickest in Test cricket. Alongside him, vice-captain Rishabh Pant played the foil and then the aggressor, stepping out to loft Stokes for four to get going and later belting Chris Woakes for six in the final over of the day. Pant passed 3,000 Test runs along the way and finished unbeaten on 65 from 102 balls; the pair's stand was worth 138 and still growing at the close. India's run rate by stumps stood at a Bazball-shaming 4.22.

There was a nod to the past too: Karun Nair, recalled to the Test side after eight years in the wilderness, sat padded up as the new generation did the work. For England, Stokes's two wickets were the only return for a bowling attack that looked toothless once the new-ball threat passed.

## Why the Diaspora Should Watch

For the Indian diaspora scattered across England, the United States and Canada, this was never just a cricket match. It was the first real look at what Indian Test cricket becomes without Kohli's intensity and Rohit's authority — and the early verdict, written in two centuries on a Leeds afternoon, is reassuring. The faces are younger, the surnames less familiar to a passing fan, but the standard has not dropped. For NRI families who plan summers around the England tour, who fill the stands at Headingley and Edgbaston in replica shirts, and who measure home partly through the fortunes of this team, day one offered the most welcome message of all: the era has changed, and India are still very good.

There is a long way to go in this match and this series. England's batting is deep and their intent relentless, and a first-innings total, however large, guarantees nothing in a five-Test summer. But Gill's India have made their statement on the first morning they could. The post-Kohli age has a captain, and he scored a hundred to open it."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India captain Shubman Gill, who scored an unbeaten century on his Test captaincy debut at Headingley"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured player Wikipedia portraits (the story's protagonists)
for name, cap in [
    ("Shubman Gill", "India captain Shubman Gill, who made an unbeaten 127 on his Test captaincy debut at Headingley"),
    ("Yashasvi Jaiswal", "Yashasvi Jaiswal, who scored 101 on his first Test innings in England at Headingley"),
    ("Rishabh Pant", "Rishabh Pant, who finished Day 1 unbeaten on 65 and passed 3,000 Test runs at Headingley"),
]:
    wiki_img = fetch_wikipedia_person_image(name)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["Headingley cricket ground", "India cricket team Test",
              "Test cricket England", "cricket match Leeds"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Headingley, Leeds, where India closed Day 1 of the first Test on 359 for three"
                break
        if img_final:
            break

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
        {"name": "Cricbuzz \u2014 Shubman Gill, Yashasvi Jaiswal usher in new dawn with dazzling display", "url": "https://www.cricbuzz.com/"},
        {"name": "Sky Sports \u2014 England vs India, first Test, day one report", "url": "https://www.skysports.com/cricket"},
        {"name": "Livemint \u2014 IND vs ENG 1st Test Day 1: Gill, Jaiswal hundreds power India to 359/3", "url": "https://www.livemint.com/"},
    ]),
    "diaspora_angle": "Day 1 at Headingley was the first real look at Indian Test cricket without Virat Kohli and Rohit Sharma \u2014 and for NRI families who plan summers around the England tour and measure home through this team, twin centuries from a new captain and a young opener were the most reassuring start the post-Kohli era could have offered.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
