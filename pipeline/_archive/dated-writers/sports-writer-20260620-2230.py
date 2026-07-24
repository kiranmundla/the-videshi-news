#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (22:30 UTC slot)
Article: MLC 2026 Match 3 — Seattle Orcas chase 217 to beat Washington Freedom
by 5 wickets at Grand Prairie Stadium, Dallas. Tim Seifert 78(33) and Matthew
Breetzke 66(36) power the chase home with 14 balls to spare; Dasun Shanaka 36*
finishes it and earlier took 3 wickets. Washington Freedom 216 (Mitchell Owen
61, Mark Chapman 57; Ottneil Baartman 4-33).

ANGLE: Dedup-checked — recent sports articles covered the MLC opener (du Plessis
113) and the SF Unicorns collapse, but NOT today's Orcas-Freedom run-fest. Fresh
result (~hours old). Diaspora angle: America's franchise T20 league, built in
the suburbs the Indian diaspora calls home, with Indian-American Saurabh
Netravalkar (2-35) in the Freedom attack.

Hero: Wikipedia portrait of Saurabh Netravalkar (Indian-American, USA & Freedom);
fallback to Glenn Maxwell / Commons MLC / US cricket imagery.
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
print("ARTICLE: Orcas chase 217, beat Washington Freedom by 5 wkts")
print("="*60)

art_slug = "seattle-orcas-beat-washington-freedom-mlc-2026-chase-217-tim-seifert-78-breetzke-66-shanaka-grand-prairie-netravalkar-diaspora-nri"
art_headline = "Seattle Chased 217 in Texas and Barely Broke Stride. America's T20 League Is Producing Run-Fests the Diaspora Built It For."
art_subheadline = "Tim Seifert's 78 off 33 and Matthew Breetzke's 66 powered the Orcas past Washington Freedom by five wickets with 14 balls to spare, the latest blockbuster in a Major League Cricket season the NRI suburbs made possible."

art_body = """The Seattle Orcas needed 217 to win on Saturday in Grand Prairie, Texas, and treated the target as a formality. Chasing what should have been a match-winning Washington Freedom total, the Orcas reached 219 for five in just 17.4 overs, sealing a five-wicket victory with 14 balls to spare and confirming that the fourth season of Major League Cricket has begun the way the league likes it best: with the bat in charge and the scoreboard barely able to keep up.

It was the second run-soaked thriller in as many days at Grand Prairie Stadium, the purpose-built ground at the heart of America's cricket experiment. And once again the man at the centre of it was Tim Seifert, the New Zealand wicketkeeper who had struck a hundred in a losing cause 24 hours earlier and was in no mood to slow down.

## A Chase That Was Over by the Ninth Over

Washington Freedom had every reason to feel safe. Asked to bat first, they came out swinging through Mitchell Owen, whose 61 off 25 balls — ten fours and two sixes — set a brutal early tempo, and Mark Chapman, who matched him with a 24-ball 57. For a while a total north of 230 looked likely. Then the South African seamer Ottneil Baartman ripped through the lower order with figures of four for 33, supported by three wickets from Sri Lanka's Dasun Shanaka, and the Freedom were bowled out for 216 off the final ball.

It still should have been enough. It was not close to enough. Seifert hammered three fours and a six off Marco Jansen in the opening over and never relented; with opening partner Shayan Jahangir, he raced the Orcas to 52 inside 3.1 overs. After Jahangir fell, Matthew Breetzke joined the assault, and when Seifert took 28 off a single Mitchell Owen over — four, six, six, six — the chase was effectively done. Seattle were 123 for one after nine overs. Seifert fell for 78 from 33 balls just short of back-to-back hundreds, Breetzke made 66 from 36, and though three quick wickets briefly threatened a wobble, Shanaka settled it with an unbeaten 36 off 12, clubbing Lockie Ferguson for successive sixes to finish the job.

## The League the Diaspora Built

For all the southern-hemisphere star power on the field, the story of Major League Cricket has always been an American one — and, more specifically, a diaspora one. The grounds in Grand Prairie and the Bay Area sit in the very suburbs where Indian and South Asian families have settled in their hundreds of thousands, and it is their season-ticket money, their weekend crowds and their streaming subscriptions that have turned a speculative idea into a viable professional league now in its fourth year.

That connection runs onto the pitch, too. Washington Freedom's attack on Saturday included Saurabh Netravalkar, the Oracle software engineer turned United States international who has become the unofficial face of American cricket's immigrant generation; he claimed two for 35. The league's rosters are dotted with USA-eligible players of Indian origin who learned the game in driveways and on matting pitches from New Jersey to California, and for whom MLC is the first genuine domestic stage.

## Why It Matters for NRIs

For the diaspora watching from Edison, Dallas and Fremont, these are not exhibition matches to be half-followed between IPL seasons. They are the proof of concept for a sport trying to plant permanent roots in North America ahead of cricket's return to the Olympic Games at Los Angeles 2028, where the T20 format will be on show. Every 217 chased down in front of a packed suburban crowd strengthens the case that there is a paying, passionate audience for cricket on this continent — an audience the diaspora has effectively underwritten.

The season is barely a week old and already the batting has been relentless. Seattle's win lifts them early in a six-team table that will be decided over a month of double round-robin cricket before the playoffs and a final in Oakland on July 18. The Orcas, beaten in their opener, have answered with a statement chase. On this evidence, the bowlers across Major League Cricket should brace for a long, hot, high-scoring summer."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Saurabh Netravalkar, the Indian-American USA international who featured for Washington Freedom in Major League Cricket"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured diaspora / recognizable player Wikipedia portrait
for name, cap in [
    ("Saurabh Netravalkar", "Saurabh Netravalkar, the Indian-American USA international who took 2-35 for Washington Freedom in MLC 2026"),
    ("Glenn Maxwell", "Glenn Maxwell of Washington Freedom during the 2026 Major League Cricket season"),
    ("Marco Jansen", "Marco Jansen of Washington Freedom during the 2026 Major League Cricket season"),
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
    for q in ["Major League Cricket", "Grand Prairie Stadium cricket",
              "cricket United States", "Twenty20 cricket match"]:
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
                img_caption = "A Major League Cricket scene; Seattle Orcas chased down 217 to beat Washington Freedom in Texas"
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
        {"name": "Cricbuzz \u2014 MLC 2026: Washington Freedom vs Seattle Orcas, Match Report", "url": "https://www.cricbuzz.com/"},
        {"name": "Khel Now \u2014 Seattle Orcas won by 5 wickets vs Washington Freedom, SEO vs WF 2026", "url": "https://khelnow.com/cricket"},
        {"name": "Cricket World \u2014 Major League Cricket 2026 Fixtures & Match Reports", "url": "https://www.cricketworld.com/"},
        {"name": "Bharat Horizon \u2014 Seattle Orcas pull off stunning chase to beat Washington Freedom in MLC 2026", "url": "https://bharathorizon.com/"},
    ]),
    "diaspora_angle": "Major League Cricket is played in the very North American suburbs the Indian and South Asian diaspora calls home, and features USA internationals of Indian origin like Saurabh Netravalkar \u2014 making the league's run-fests a proof of concept for cricket's permanent roots in America ahead of the LA 2028 Olympics.",
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
