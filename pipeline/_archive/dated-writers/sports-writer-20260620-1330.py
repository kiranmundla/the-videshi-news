#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (13:30 UTC slot)
Article: Two Indian-American golfers — Sahith Theegala and Akshay Bhatia —
made the weekend cut at the 2026 U.S. Open at Shinnecock Hills, with Theegala
sitting T7 (-1) inside the top 10 heading into Moving Day, while recent major
champions Bryson DeChambeau, Jon Rahm, Brooks Koepka and defending champ
J.J. Spaun all went home after missing the brutal +4 cut.

ANGLE: A genuine diaspora-in-American-sport story — two golfers of Indian
descent in contention at the toughest major in the game, on a weekend when
former champions were eliminated. Distinct from the June 18 Manav Shah
US Open preview (who himself missed the cut here).

Hero: Wikipedia portrait of Sahith Theegala first, then Akshay Bhatia,
then Commons Shinnecock Hills / US Open golf imagery.
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
print("ARTICLE: Indian-American golfers make US Open weekend")
print("="*60)

art_slug = "sahith-theegala-akshay-bhatia-indian-american-golfers-us-open-2026-weekend-shinnecock-hills-cut-diaspora-nri"
art_headline = "Two Indian-Americans Made the U.S. Open Weekend. Three Recent Champions Did Not."
art_subheadline = "As Bryson DeChambeau, Jon Rahm and Brooks Koepka were sent home from Shinnecock Hills, Sahith Theegala and Akshay Bhatia survived the brutal cut \u2014 with Theegala sitting inside the top 10 heading into Moving Day."

art_body = """When the cut fell at the 2026 U.S. Open on Friday evening, the list of names heading home read like a roll call of recent major champions. Bryson DeChambeau, the 2024 winner. Jon Rahm, who lifted the trophy in 2021. Brooks Koepka, a back-to-back U.S. Open champion in 2017 and 2018. Even J.J. Spaun, the man who won this very title a year ago, packed his bags after missing the +4 cut line at a wind-scoured Shinnecock Hills.

Among the 72 players who survived to play the weekend were two golfers the Indian diaspora has quietly come to claim as its own: Sahith Theegala and Akshay Bhatia. And one of them is doing rather more than just surviving.

## Theegala in the Mix

Theegala, the 28-year-old Telugu-American who grew up in Southern California, sits tied for seventh at one under par heading into Saturday's third round \u2014 squarely inside the top 10 at the most demanding test in golf. Rounds of 72 and 67 on a course that has humbled the game's biggest names left him just six off the runaway leader, Wyndham Clark, and very much in the conversation as the tournament turns toward the weekend.

It is the kind of position Theegala has earned a reputation for reaching. Since breaking through on the PGA Tour, he has become one of the most popular players in the American game \u2014 known as much for his sportsmanship and visible emotion as for a silky short game. For the South Asian families who follow him, his presence near the top of a U.S. Open leaderboard carries an extra charge.

## Bhatia Battles Through

Bhatia, 24, born in North Carolina to parents of Indian origin, also did the hard part by making it to the weekend. A left-hander with one of the more unorthodox grips in the professional game, he has already won multiple times on the PGA Tour and represented the United States in international team competition. Grinding out a place in the final two rounds at Shinnecock \u2014 where par is a genuinely good score and bogeys arrive in clusters \u2014 is no small feat, especially on a week when so many higher-ranked players faltered.

That both men are still standing while DeChambeau, Rahm, Koepka and Spaun are not speaks to how punishing this championship has been. The wind off the Atlantic has turned Shinnecock's fast, sloping greens into a survival test, and the leaderboard has rewarded patience and precision over raw power.

## A Quiet Milestone for the Diaspora

For a community that has long dominated the conversation in cricket, chess and, increasingly, American business and technology, golf has been a slower burn. The sight of two players of Indian descent making the weekend at a U.S. Open \u2014 with one of them in the top 10 \u2014 is the kind of marker that registers far beyond the galleries at Southampton.

Manav Shah, the Bay Area amateur-turned-professional whose debut in this field had been one of the week's feel-good storylines, missed the cut on his first appearance at a major. But the broader trend is unmistakable: the pipeline of Indian-American talent in golf is deepening, and the names at the top of it are no longer novelties.

## What's Next at Shinnecock

Clark heads into Moving Day at seven under, four clear of a chasing pack that includes Matt Fitzpatrick, Xander Schauffele, Sam Stevens and Tom Kim. Theegala will need a clean weekend on a course that punishes the smallest error, but a top-10 finish \u2014 or better \u2014 at a U.S. Open would stand among the biggest results of his career.

For the diaspora watching from living rooms in Edison, Fremont, Houston and beyond, the math is simple and the stakes are real. Two of their own are still in it at golf's hardest test, and a generation of recent champions is already watching from home. Whatever the leaderboard says by Sunday evening, that is a weekend worth tuning in for."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Shinnecock Hills Golf Club, host of the 2026 U.S. Open"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured-player Wikipedia portraits (Theegala first as the lead figure)
for person, cap in [
    ("Sahith Theegala", "Sahith Theegala, who sits tied for seventh at the 2026 U.S. Open heading into the weekend at Shinnecock Hills"),
    ("Akshay Bhatia", "Akshay Bhatia, who made the cut at the 2026 U.S. Open at Shinnecock Hills"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if got:
            img_final = got
            img_caption = cap
            break

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["Shinnecock Hills Golf Club", "US Open golf championship", "golf course United States", "professional golfer tee"]:
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
                img_caption = "A U.S. Open golf scene; the 2026 championship is being played at Shinnecock Hills"
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
    "vertical": "golf",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "USA Today \u2014 Moving day at US Open: Leaderboard, tee times, live updates, Round 3", "url": "https://www.usatoday.com/"},
        {"name": "Palm Beach Post \u2014 Live updates from 2026 US Open third round, tee times, TV schedule", "url": "https://www.palmbeachpost.com/"},
        {"name": "TalkSport \u2014 US Open 2026 LIVE: Adjusted tee times, leaderboard, course info", "url": "https://talksport.com/"},
    ]),
    "diaspora_angle": "Sahith Theegala and Akshay Bhatia, both American golfers of Indian descent, made the weekend cut at the 2026 U.S. Open while recent major champions were eliminated \u2014 a marker of the deepening Indian-American presence in a sport where the diaspora has historically had little visibility.",
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
