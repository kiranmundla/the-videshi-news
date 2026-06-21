#!/usr/bin/env python3
"""
Sports Writer — June 21, 2026 (07:30 UTC slot)
Article: MLC 2026, Match 5 — Washington Freedom 245/5 beat MI New York 215/6
by 30 runs at Grand Prairie. Mitchell Owen 155 (68) and Kieron Pollard 100* (56)
both hit hundreds in the SAME match — Owen for Freedom, Pollard for MI New York.
460 combined runs. Glenn Maxwell 2/37. Saurabh Netravalkar in the Freedom XI.

ANGLE: Dedup-checked against the last 3 days of sports articles. Covered already:
Match 1 opener (Faf 113), Match 3 (Seattle chase 217), Match 4 (SFU beat TSK). This
Match 5 run-fest (TWO centuries in one game, Owen's monster 155, Pollard's ageless
ton) is FRESH and uncovered. Diaspora angle: America's T20 league, built in the
suburbs the NRI community calls home, producing some of the biggest hitting in
its short history — with US international Saurabh Netravalkar in the home XI.

Hero: Wikipedia portrait of Kieron Pollard (most reliable photo), then Glenn
Maxwell, then Commons Grand Prairie / MLC imagery. (Owen has weak Wikipedia photo.)
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
print("ARTICLE: MLC Match 5 — Owen 155 & Pollard 100, Freedom by 30")
print("="*60)

art_slug = "washington-freedom-beat-mi-new-york-mlc-2026-mitchell-owen-155-kieron-pollard-100-two-centuries-grand-prairie-diaspora-nri"
art_headline = "Two Hundreds, 460 Runs, One Game: America's Cricket League Just Staged Its Most Brutal Run-Fest Yet"
art_subheadline = "Mitchell Owen smashed 155 and Kieron Pollard answered with an unbeaten 100, but Washington Freedom's 245 was 30 too many for MI New York at Grand Prairie."

art_body = """There is a particular kind of cricket that Major League Cricket was built to produce — short, loud and merciless on the bowlers — and on Saturday night in Grand Prairie, Texas, the league delivered its purest expression of it yet. Washington Freedom piled up 245 for five, MI New York hit back with 215 for six, and between the two sides, two batters reached three figures in the same match. Freedom won by 30 runs. The scoreboard read like a misprint: 460 runs in 40 overs, and nobody who paid for a ticket went home feeling short-changed.

The architect of the carnage was Mitchell Owen, the Australian who has quietly become one of the most destructive openers in franchise cricket. Sent in after MI New York captain won the toss and chose to bowl, Owen treated the decision as a personal insult. He reached his fifty in a blur, kept going through the middle overs when most T20 innings pause for breath, and finished with 155 off just 68 balls — an innings of such sustained violence that it ranks among the biggest individual scores in the short history of American franchise cricket.

## A Total Built to Break Records

Owen did not do it alone, but he did most of it. By the time he was dismissed, Washington had already moved out of reach of a conventional chase, and the supporting cast — Mark Chapman and Andries Gous prominent among them — simply kept the run rate from sagging. The Freedom closed on 245 for five, a total that would have been unthinkable in the league's first season and now barely raises an eyebrow in a competition that has rewritten its own batting records almost weekly this June.

For the home crowd, much of it drawn from the Indian and South Asian diaspora that has made Grand Prairie the de facto capital of American cricket, there was a familiar face in the Freedom XI to cheer: Saurabh Netravalkar, the Mumbai-born software engineer turned United States international, whose journey from Silicon Valley cubicle to MLC star has become one of the diaspora's favourite sporting stories.

## Pollard Refuses to Let It Be a Procession

A target of 246 should, by every law of probability, produce a one-sided romp. MI New York very nearly turned it into a contest anyway, and the reason was a 38-year-old who has been winning T20 matches since before some of his teammates were teenagers. Kieron Pollard, the great West Indian finisher, walked in and produced a masterclass in controlled hitting, reaching an unbeaten 100 from 56 deliveries and dragging his side to within shouting distance of an absurd chase.

Pollard's hundred was the second of the night and, in its own way, the more remarkable. Owen's 155 came on a flat deck against a Freedom attack chasing the game; Pollard's came under the relentless pressure of a required rate that never dropped below double figures. That he got MI New York to 215 at all was a reminder that, even deep into his career, he remains one of the most reliable big-stage batters the format has produced. It was not enough. Glenn Maxwell, leading Washington, mixed his overs cleverly and finished with two for 37, and the 30-run gap that separated the sides at the end flattered nobody and disappointed no one.

## Why the Diaspora Should Watch

For the NRI families who fill the stands at Grand Prairie — and the many more who follow on streams from living rooms in New Jersey, the Bay Area and Toronto — this is the league they were promised. When MLC launched, the pitch to the diaspora was simple: world-class T20 cricket, played in your time zone, in your backyard, with the kind of star power that used to require a flight to Mumbai or a 3 a.m. alarm to watch. A match in which Owen and Pollard both score hundreds, and a side still needs 246 to win and falls short, is the proof of concept arriving in real time.

There is a longer game here too. Every run-fest like this one builds the case that American cricket is not a novelty but a genuine destination for the sport's best, and that the second-generation kids in the stands — many of them children of immigrants who grew up watching cricket as an act of homesickness — now have a major league of their own to belong to. Saturday night in Texas was a slugfest. It was also, quietly, a statement about where the game is heading."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Kieron Pollard, who hit an unbeaten 100 for MI New York at Grand Prairie"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured player Wikipedia portraits (the story's protagonists)
for name, cap in [
    ("Kieron Pollard", "Kieron Pollard, who struck an unbeaten 100 off 56 balls for MI New York at Grand Prairie"),
    ("Glenn Maxwell", "Glenn Maxwell, who captained Washington Freedom and took two wickets in the win over MI New York"),
    ("Mitchell Owen (cricketer)", "Mitchell Owen, whose 155 off 68 balls powered Washington Freedom to 245 for five"),
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
    for q in ["Grand Prairie Stadium cricket", "Major League Cricket",
              "cricket Texas USA", "T20 cricket match"]:
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
                img_caption = "Grand Prairie Stadium in Texas, the heart of American franchise cricket"
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
        {"name": "Major League Cricket \u2014 Washington Freedom vs MI New York, Match 5 scorecard", "url": "https://www.majorleaguecricket.com/"},
        {"name": "Wikipedia \u2014 2026 Major League Cricket season", "url": "https://en.wikipedia.org/wiki/2026_Major_League_Cricket_season"},
        {"name": "ESPNcricinfo \u2014 MLC 2026 results", "url": "https://www.espncricinfo.com/series/major-league-cricket-2026"},
    ]),
    "diaspora_angle": "MLC was sold to the NRI community as world-class T20 cricket in their own time zone and backyard \u2014 and a match where both Mitchell Owen and Kieron Pollard score hundreds, with US international Saurabh Netravalkar in the home XI, is that promise delivered for the diaspora that built American cricket's heartland in suburbs like Grand Prairie.",
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
