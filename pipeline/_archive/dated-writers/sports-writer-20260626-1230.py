#!/usr/bin/env python3
"""
Sports Writer — June 26, 2026 (videshi-writer-sports, 12:30 PDT slot)

STORY: San Francisco Unicorns beat Texas Super Kings by 1 RUN in Major League
Cricket 2026, defending 148 in a last-ball thriller at Central Broward Regional
Park, Lauderhill, Florida (June 25, 2026). Unicorns 148/6 (Matthew Short 80 off
63, Hassan Khan 40 off 25; Marcus Stoinis 3-32). Texas 147/7 (Donovan Ferreira
39 off 20; Brody Couch 2-26, Romario Shepherd 2-26). Came down to 3 needed off
the last ball; Calvin Savage run out at the keeper's end going for a second.
This AVENGES the Unicorns' earlier 22-run loss to Texas (their Oakland debut)
and lifts their top-two hopes.

DEDUP CHECK (sports feed last 3 days): there IS an article on the Unicorns'
EARLIER 22-run LOSS to Texas at the Oakland Coliseum debut
("major-league-cricket-2026-oakland-coliseum-debut-san-francisco-unicorns-lose-
texas-super-kings-22-runs"), and one on MI New York beating Texas. There is NO
article on this 1-run WIN / Lauderhill thriller. This match is uncovered. CLEAR.

FACTS (Cricbuzz match report; SportsCafe MLC results/standings; Wikipedia 2026
MLC season):
- SF Unicorns 148/6 beat Texas Super Kings 147/7 by 1 run, MLC 2026.
- Matthew Short 80 (63) anchored from 25/3; Hassan Khan 40 (25). Stoinis 3-32.
- Texas chase: Ferreira 39 (20) kept them alive; Shepherd struck twice in the
  19th over (Ferreira, Ranjane). 13 needed off the last over (Xavier Bartlett);
  Mohammad Mohsin hit two fours; 3 needed off the last ball; Calvin Savage run
  out at keeper's end attempting a second.
- Result returns Unicorns to winning ways, strengthens top-two hopes.
- Context: SF Unicorns signed R Ashwin for this MLC season; captain/Bay Area
  ties; this is the marquee US franchise T20 league.

IMAGE: Person-led — Matthew Short (Australian all-rounder, Player-of-the-Match
80). Cascade: Wikipedia (Matthew Short cricketer) -> Wikimedia Commons
(Major League Cricket / cricket USA) -> abort if nothing. Caption matches what
lands.
"""

import os, io, json, subprocess, urllib.parse
from datetime import datetime, timezone

import requests
from PIL import Image

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
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=15,
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


def fetch_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            out = []
            for _, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 500:
                    continue
                out.append({"url": ii.get("thumburl") or ii.get("url", ""),
                            "title": page.get("title", "")})
            return out
    except Exception as e:
        print(f"  \u26a0 Commons error '{search_query}': {e}")
    return []


def compress_image(img_bytes, max_width=1200, quality=85):
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
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                     "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS,
                      json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


print("\n" + "=" * 60)
print("ARTICLE: SF Unicorns beat Texas Super Kings by 1 run — MLC 2026")
print("=" * 60)

art_slug = "san-francisco-unicorns-beat-texas-super-kings-1-run-mlc-2026-lauderhill-thriller-matthew-short-80-revenge-top-two-diaspora-nri"
art_headline = "San Francisco Get Their Revenge on Texas \u2014 by the Width of a Single Run"
art_subheadline = "Defending just 148, the Bay Area's Major League Cricket franchise held its nerve to the final ball in Lauderhill, where a run-out off the last delivery sealed a one-run win over the Texas Super Kings \u2014 and turned an early defeat into a statement."

art_body = """A fortnight ago, the San Francisco Unicorns walked off the Oakland Coliseum having lost their Major League Cricket opener to the Texas Super Kings by 22 runs, the Bay Area's first taste of big-league franchise cricket ending in disappointment. On Thursday in Lauderhill, Florida, the same two sides met again \u2014 and this time the Unicorns found a way to win that no scriptwriter would have dared invent. They beat Texas by one run, defending a modest 148 in a contest that swung from over to over and was settled only by a run-out off the very last ball.

## Short drags them to a total

For most of the Unicorns' innings, a winning total looked a long way off. Reduced to 25 for 3 inside the powerplay on a sticky, two-paced surface, San Francisco needed someone to dig in, and Matthew Short did exactly that. The Australian all-rounder anchored the innings with a gutsy 80 from 63 balls, refusing to chase the game and instead nudging, running and picking his moments to clear the rope. He found a willing partner in Hassan Khan, whose brisk 40 off 25 balls injected the late momentum that lifted the Unicorns to 148 for 6.

It was, by the standards of a league built on towering scores, a below-par total. Texas's Akeal Hosein had been the pick of the bowlers early, and on another night the Super Kings' chase would have been a formality. The Unicorns simply had to bowl, and field, better than they had any right to.

## A chase that would not die

Texas never settled at the top. Brody Couch removed both openers cheaply, and although Marcus Stoinis \u2014 earlier a three-wicket destroyer with the ball \u2014 and Saiteja Mukkamalla steadied things briefly, the required rate kept climbing. The turning point came when Donovan Ferreira walked in and counter-attacked, his 39 from 20 balls hauling the equation down to 23 needed off the last 12 deliveries and reviving a chase that had looked dead.

Then Romario Shepherd struck twice in the 19th over, removing both Ferreira and Shubham Ranjane in quick succession to swing the game back toward the Unicorns. It left Texas needing 13 from the final six balls, and the ball in the hands of Xavier Bartlett.

## Three off the last ball

What followed was the kind of finish that wins new fans for a young league. Mohammad Mohsin found two boundaries to keep Texas alive, but Bartlett held his nerve, varying his angles and refusing to offer width. It came down to three runs required off the final delivery. Going hard for a second run that would have at least tied the scores, Calvin Savage was run out at the keeper's end, and the Unicorns had their one-run win. Brief scores: San Francisco Unicorns 148/6 (Short 80; Stoinis 3-32) beat Texas Super Kings 147/7 (Ferreira 39; Couch 2-26, Shepherd 2-26) by one run.

## What it means for the Unicorns

Beyond the drama, the result matters in the table. The win returned the Unicorns to winning ways and strengthened their push for a top-two finish and the playoff advantages that come with it. Having signed India's veteran off-spinner Ravichandran Ashwin for the season, San Francisco arrived in 2026 with genuine ambition; a tight loss followed by a nerveless win over the same opponent is exactly the kind of resilience a franchise needs to build a following.

## Why the diaspora is watching

Major League Cricket is the most serious attempt yet to plant the professional game in American soil, and no franchise carries more weight with the Indian diaspora than the Bay Area's own Unicorns. The region is home to one of the largest concentrations of Indian-origin tech workers and families anywhere in the United States \u2014 a community that grew up on the sport and now, for the first time, has a top-tier team to call local. Ashwin's presence gives that connection a familiar face, and matches like this one, decided off the last ball, are precisely how a league earns the loyalty of fans who can finally drive to a stadium rather than stay up for a feed from halfway around the world. For NRIs from Edison to Fremont, the Unicorns winning a thriller is no longer a novelty. It is starting to feel like a home team."""

print(f"\nWord count: ~{len(art_body.split())} words")

# ---- IMAGE CASCADE ----
print("\nSourcing hero image...")
img_final = None
img_caption = None
img_attribution = "Wikimedia Commons"

short = fetch_wikipedia_person_image("Matthew Short (cricketer)")
if short:
    img_final = upload_to_supabase(short, f"{art_slug}.jpg")
    if img_final:
        img_caption = "Matthew Short, whose 80 anchored the San Francisco Unicorns to a defendable total in their one-run win over the Texas Super Kings."

if not img_final:
    for q in ["Major League Cricket 2026", "Major League Cricket United States",
              "Grand Prairie Stadium cricket", "Cricket United States stadium"]:
        cands = fetch_commons_images(q)
        if cands:
            img_final = upload_to_supabase(cands[0]["url"], f"{art_slug}.jpg")
            if img_final:
                img_caption = "Major League Cricket, the United States' marquee T20 franchise league, where the San Francisco Unicorns edged the Texas Super Kings by a single run."
                img_attribution = "Wikimedia Commons"
                break

if not img_final:
    print("  \u2717 No image sourced — aborting to avoid wrong/blank hero.")
    raise SystemExit(1)

print(f"\nHero: {img_final}\nCaption: {img_caption}")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final,
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Cricbuzz \u2014 Major League Cricket: San Francisco Unicorns beat Texas Super Kings by one run (match report, Lauderhill)", "url": "https://www.cricbuzz.com/cricket-news/134896/major-league-cricket-cricbuzzcom"},
        {"name": "SportsCafe \u2014 Major League Cricket 2026 results, scorecards and points table", "url": "https://www.sportscafe.in/"},
        {"name": "Wikipedia \u2014 2026 Major League Cricket season", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
    ]),
    "diaspora_angle": "The San Francisco Unicorns are the Bay Area's own Major League Cricket franchise, and the region's huge Indian-origin tech community \u2014 with R Ashwin now in the squad \u2014 finally has a top-tier team to follow in person, making a last-ball thriller like this a milestone in cricket's American growth.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
