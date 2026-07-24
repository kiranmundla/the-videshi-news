#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (10:30 UTC slot)
Article: The Bay Area's San Francisco Unicorns opened their MLC 2026 campaign
with a 7-wicket defeat (DLS) to the Los Angeles Knight Riders in a rain-hit
clash at Grand Prairie. SFU posted 150/7 in 14 overs (Lhuan-dre Pretorius 58,
Matthew Short 30) after a collapse — 5 for 33 in the last five overs — then
Colin Munro's unbeaten 64 off 40 chased it down inside 14 overs.

ANGLE: This is the Bay Area's home franchise, owned by Indian-American tech
entrepreneurs, starting its season. Distinct from recent MLC coverage (season
opener, du Plessis Texas chase). Local resonance for the huge South Asian
tech diaspora in the Bay Area who pack SFU's games.

Hero: Wikipedia portrait of a featured player (Matthew Short / Colin Munro),
then Commons MLC/cricket imagery.
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
print("ARTICLE: SF Unicorns open MLC 2026 with rain-hit defeat")
print("="*60)

art_slug = "san-francisco-unicorns-lose-mlc-2026-opener-la-knight-riders-7-wickets-dls-colin-munro-pretorius-grand-prairie-bay-area-diaspora-nri"
art_headline = "The Bay Area's Team Began Its Season 117 for 2 \u2014 and Still Lost. The Unicorns' Collapse Handed LA the Opener."
art_subheadline = "San Francisco Unicorns slipped from a commanding position to 150 for 7 in a rain-shortened game, and Colin Munro's unbeaten 64 made the Knight Riders' chase look routine as Major League Cricket's fourth season began at Grand Prairie."

art_body = """For 11 overs on Friday night in Grand Prairie, the San Francisco Unicorns looked every bit the title contenders the Bay Area's cricket-mad diaspora had been promised. Then, in the space of five overs, the season opener slipped through their fingers \u2014 and the Los Angeles Knight Riders pounced.

Reduced to 14 overs a side by rain, the Unicorns were cruising at 117 for 2 before a startling collapse \u2014 five wickets for 33 runs \u2014 left them stranded on 150 for 7. The Knight Riders, set an adjusted target under the Duckworth-Lewis-Stern method, knocked it off with two balls to spare, Colin Munro unbeaten on 64 from 40 balls, to win by seven wickets and spoil San Francisco's first night of Major League Cricket 2026.

## A Strong Start Squandered

The Unicorns' innings was built by Lhuan-dre Pretorius, the young South African wicketkeeper-batter, whose 58 anchored the powerplay and beyond. He found early support from Finn Allen, who flayed 24 from just 12 balls, and a composed 30 from 20 by the Australian all-rounder Matthew Short. A 20-run over off Jason Holder pushed San Francisco to that commanding 117 for 2, and a total of 175-plus looked well within reach.

It never came. Sunil Narine, the Knight Riders' evergreen mystery spinner, applied the brakes through the middle with 2 for 33, and once the death overs arrived the Unicorns lost their way completely. Wickets tumbled, the boundaries dried up, and a innings that had promised so much finished a good 25 runs short of par on a fast outfield.

## Munro Makes the Chase Look Easy

Whatever total San Francisco defended, Munro had other ideas. The left-hander came out swinging, racing to his fifty with a mix of pulls and lofted drives, and was scarcely troubled as he carried the Knight Riders home. Andre Fletcher's brisk 34 from 17 balls gave the chase its early momentum, and Holder's 28 from 12 \u2014 at a strike rate north of 230 \u2014 ensured the required rate never became a problem.

Peter Siddle was the pick of the San Francisco attack with 2 for 27, removing both Rovman Powell and Holder, but the Unicorns' bowlers were left defending too little. By the time Munro clipped the winning runs in the 14th over, the result had long felt inevitable.

## What It Means for the Bay Area's Franchise

For the Unicorns, this is a familiar early-season stumble rather than a crisis. The franchise reached the playoffs in each of the league's first three seasons and boasts one of the deepest squads in the competition, with Allen, Short, Pretorius and the experienced Siddle all capable of turning a game on its own. A 14-over shootout decided by one bad five-over stretch is the kind of result that gets filed away quickly in a long round-robin.

But the timing stings a little. The Unicorns are the Bay Area's team in a region that is home to one of the densest South Asian populations in the United States, and a franchise backed by Indian-American technology entrepreneurs who built it precisely to give that community a side to call its own. Their home games at Oakland have become a fixture of the diaspora's summer, and an opening-night defeat is not how anyone in the stands wanted the season to begin.

## Why the Diaspora Is Watching

Major League Cricket has, in four short seasons, become the most tangible sign that the sport is putting down real roots in America \u2014 and nowhere is that more keenly felt than in the Bay Area, where weekend cricket grounds fill with families who grew up on the game in India, Pakistan and Sri Lanka. The Unicorns are their stake in that story.

The good news is that the schedule turns quickly. San Francisco return to action against the Texas Super Kings, and with the bulk of the league still to play, Friday's collapse is a wobble rather than a verdict. The diaspora that adopted this franchise will be back in the stands soon enough \u2014 hoping that next time, 117 for 2 finishes the job."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Major League Cricket action; the San Francisco Unicorns opened their 2026 season at Grand Prairie"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured-player Wikipedia portraits (SFU player first, then match-winner)
for person, cap in [
    ("Matthew Short (cricketer)", "Australia all-rounder Matthew Short, who made 30 for the San Francisco Unicorns in their MLC opener"),
    ("Colin Munro", "Colin Munro, whose unbeaten 64 carried the LA Knight Riders past the San Francisco Unicorns"),
    ("Sunil Narine", "LA Knight Riders spinner Sunil Narine, who took 2 for 33 against the San Francisco Unicorns"),
    ("Peter Siddle", "San Francisco Unicorns seamer Peter Siddle, the pick of the bowlers with 2 for 27"),
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
    for q in ["Major League Cricket", "Grand Prairie Stadium cricket", "cricket Texas United States", "T20 cricket batsman"]:
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
                img_caption = "Major League Cricket action in the United States"
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
        {"name": "Cricbuzz \u2014 MLC 2026: Munro, Fletcher, Holder power LA Knight Riders in rain-hit clash", "url": "https://www.cricbuzz.com/"},
        {"name": "Khel Now \u2014 LAKR 154/3 beat SFU 150/7, LA Knight Riders won by 7 wickets", "url": "https://khelnow.com/"},
        {"name": "Cricket World \u2014 Major League Cricket 2026: Teams, Squads, Fixtures & Schedule", "url": "https://www.cricketworld.com/"},
    ]),
    "diaspora_angle": "The San Francisco Unicorns are the Bay Area's home franchise \u2014 backed by Indian-American tech entrepreneurs and embraced by one of the densest South Asian communities in the US \u2014 making their MLC season opener a marquee event for a diaspora watching cricket take root in America.",
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
