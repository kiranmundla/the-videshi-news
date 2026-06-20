#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (19:30 UTC slot)
Article: India complete a 3-0 ODI clean sweep of Afghanistan with a nine-wicket
win in Chennai. Yashasvi Jaiswal's unbeaten 110 and Prasidh Krishna's 5/23
seal it. The bigger story is the post-Kohli transition under new ODI captain
Shubman Gill, with the 2027 World Cup the horizon.

ANGLE: Dedup-checked — recent sports articles covered the Lucknow 2nd ODI
(Gill/Kishan centuries, 500th win) but NOT today's series-sealing 3rd ODI
sweep in Chennai. Fresh, live result (~hours old). Diaspora angle: Gill's
new-era India, Jaiswal as opener-in-the-making, building toward 2027 WC.

Hero: Wikipedia portrait of Yashasvi Jaiswal (POTM, unbeaten 110); fallback to
Commons India cricket / Chepauk imagery.
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
print("ARTICLE: India sweep Afghanistan 3-0, Jaiswal 110*")
print("="*60)

art_slug = "india-sweep-afghanistan-3-0-odi-series-chennai-jaiswal-110-prasidh-krishna-5-23-nine-wickets-gill-new-era-2027-world-cup-nri"
art_headline = "Jaiswal's Unbeaten 110 Seals a 3-0 Sweep \u2014 and the First Clean Verdict on India's Post-Kohli ODI Team"
art_subheadline = "India brushed Afghanistan aside by nine wickets in Chennai to complete a whitewash, but the real story is a new-look side under Shubman Gill building quietly toward the 2027 World Cup."

art_body = """India finished the job in Chennai on Saturday, completing a 3-0 sweep of their one-day series against Afghanistan with a nine-wicket win at the MA Chidambaram Stadium. The margin flattered no one. After Afghanistan were dismissed for 218, Yashasvi Jaiswal made an unbeaten 110 and Rohit Sharma 79 to chase down 219 inside 29 overs, and a series that had threatened to be competitive ended as a procession.

For a tournament played in sweltering June heat at half-empty grounds, the cricket itself mattered less than what it revealed. This was the first home white-ball assignment of a transition India have been bracing for since Virat Kohli and Rohit Sharma stepped away from the Test arena, and the first full look at an ODI side now captained by Shubman Gill. On the evidence of three lopsided matches, the rebuild is further along than the doubters feared.

## A Bowler's Morning, a Batter's Afternoon

Afghanistan won the toss and chose to bat on a Chepauk surface expected to help the seamers, and Prasidh Krishna made the decision look generous. The tall Karnataka quick tore through the top order to finish with five for 23 from 8.2 overs, his best ODI figures, reducing the innings to rubble before captain Hashmatullah Shahidi's defiant century and a half-century from Azmatullah Omarzai lent the total a respectability it scarcely deserved. Afghanistan were all out for 218 in 44.2 overs.

The reply was effectively over before tea. Jaiswal and Rohit put on 170 for the first wicket, the kind of opening stand that turns a chase into an exhibition. Rohit, still searching for the fluency of old, made a brisk 79 before falling to Mohammad Nabi. Jaiswal simply carried on, striking 14 fours and three sixes in an unbeaten 110 off 86 balls \u2014 his second ODI hundred, and a statement from a 24-year-old being groomed as a long-term opener in the format. It was India's 18th clean sweep in a bilateral ODI series.

## The Gill Project

The headline number belongs to Gill. Across the series the new captain amassed runs at will from No. 3, picking up multiple player-of-the-match awards and demoting himself a place in the order to give Jaiswal a run at the top \u2014 a small act of selflessness that doubled as a selectorial message. India are no longer building around a single batting colossus; they are building a system, and Gill, calm and unhurried, looks the part of the man to run it.

That clarity extends through the side. Ishan Kishan, handed the gloves with KL Rahul rested, hammered a century in Lucknow and added dynamism to a middle order that no longer leans on Kohli's chase-mastery. Washington Sundar and Harsh Dubey offer all-round balance; Prasidh Krishna has emerged as a genuine new-ball threat. None of this is finished, but the outline of India's 2027 World Cup squad is beginning to harden.

## Why the Diaspora Should Watch

For Indian fans in Edison, Surrey and the Bay Area, the Afghanistan series was easy to dismiss as a mismatch against a side missing rhythm and ranked far below their hosts. That would be a mistake. These are the matches in which the next generation is auditioned, and the names that dominated Chennai \u2014 Jaiswal, Gill, Kishan, Prasidh \u2014 are the ones who will headline the white-ball tours that bring India to grounds across North America and England in the coming years.

The schedule now quickens. India travel to Ireland for two T20Is before a five-match T20I and three-match ODI series in England in July, the first real test of this remade unit against opposition that will not roll over. A whitewash of Afghanistan settles little on its own. But it has given India something they have not had since the retirements began to land in succession: a captain who looks settled, an opening partnership that scores in clusters, and the quiet confidence of a team that has stopped mourning what it lost and started counting what it has."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Yashasvi Jaiswal, whose unbeaten 110 sealed India's 3-0 ODI series sweep of Afghanistan in Chennai"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured-player Wikipedia portrait
for name in ["Yashasvi Jaiswal", "Shubman Gill", "Prasidh Krishna"]:
    wiki_img = fetch_wikipedia_person_image(name)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            if name != "Yashasvi Jaiswal":
                img_caption = f"India during the ODI series against Afghanistan; {name} featured in the 3-0 sweep"
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["India national cricket team", "MA Chidambaram Stadium cricket",
              "Yashasvi Jaiswal cricketer", "One Day International cricket India"]:
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
                img_caption = "An India ODI scene; India completed a 3-0 series sweep of Afghanistan in Chennai"
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
        {"name": "Reuters \u2014 Jaiswal slams ton as India sweep ODI series 3-0 against Afghanistan", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Cricbuzz \u2014 India tour news digest, June 2026", "url": "https://www.cricbuzz.com/"},
        {"name": "Sportskeeda \u2014 Indian men's cricket team schedule after IPL 2026", "url": "https://www.sportskeeda.com/cricket"},
        {"name": "Khel Now \u2014 India's predicted XI for 3rd IND vs AFG ODI in Chennai", "url": "https://khelnow.com/cricket"},
    ]),
    "diaspora_angle": "The Afghanistan sweep is the first full look at India's post-Kohli ODI side under new captain Shubman Gill, whose names \u2014 Jaiswal, Kishan, Prasidh Krishna \u2014 will headline the white-ball tours bringing India to grounds across North America and England in the years ahead.",
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
