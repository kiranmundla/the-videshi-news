#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (01:30 UTC run)
Article: Manav Shah — born in California to a Gujarati family, raised on
Bakersfield municipal courses — tees up at the U.S. Open at Shinnecock Hills,
becoming the first Indian Golf Premier League (IGPL) player to reach a Major.
Distinct angle (NOT the June 16 "deepest diaspora field" overview): a single
personal profile of one debutant's improbable road — pre-med dropout, Latin
American mini-tours, a flight-disruption detour to India that rebuilt his game,
and golf's toughest qualifier.
Diaspora angle: a US-born, Gujarati-rooted golfer who chose the fairway over
medicine and now carries both an American childhood and an Indian league onto
the Major stage.
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


def fetch_wikimedia_commons_images(search_query, limit=6):
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
print("ARTICLE: Manav Shah, first IGPL golfer at a Major (U.S. Open)")
print("="*60)

art_slug = "manav-shah-first-igpl-golfer-us-open-2026-shinnecock-gujarat-california-bakersfield-diaspora-nri"
art_headline = "From a Bakersfield Muni to Shinnecock: The Gujarati-American Who Skipped Med School and Became the First IGPL Golfer at a Major"
art_subheadline = "Manav Shah was supposed to be a doctor. Instead, the California-born son of Gujarati immigrants ground his way through Latin American mini-tours, rebuilt his game on an Indian circuit during a chance detour, and survived golf's toughest qualifier to reach the U.S. Open."

art_body = """SOUTHAMPTON, N.Y. \u2014 When Manav Shah walks onto the first tee at Shinnecock Hills this week, he will be carrying more than a bag of clubs. He will be carrying a household full of doctors he chose not to join, a childhood spent on the public courses of Bakersfield, California, and an Indian golf league that, until now, had never sent one of its own to a Major. At one of the most punishing venues in championship golf, Shah becomes the first player associated with the Indian Golf Premier League to tee up at a Major \u2014 and one of five golfers of Indian origin in this year's U.S. Open field.

His road here was anything but conventional.

## The Doctor Who Wasn't

Born to parents who emigrated from India in the 1980s \u2014 his father from Gujarat, his mother from Mumbai \u2014 Shah grew up in a home where the path to success ran through a medical degree. "My extended family are in medicine," he said. "That was always kind of the Gujarati line of work in our household."

He enrolled at UCLA as a pre-med student. But the pull of the golf course gradually won out. He switched majors and graduated with a degree in Political Science and International Relations, fluent in English, Hindi, Gujarati and Spanish. After an accomplished college career \u2014 a season at UC San Diego, then four years with the UCLA Bruins after sitting out a year for NCAA transfer rules \u2014 he turned professional in 2015.

## The Grind Nobody Sees

What followed was the unglamorous reality of professional golf: PGA Tour Canada, PGA Tour Americas, the Korn Ferry Tour, the developmental circuits where dreams are quietly tested to destruction. He had learned the game on municipal courses in Bakersfield, and for years he played the kind of events that never make the highlight reels.

The breakthrough came in 2022, when he won a PGA Tour Latinoam\u00e9rica event in Quito, Ecuador. The victory, he says, validated everything \u2014 the years of persistence, the belief that he belonged at the top. He still counts Quito among the milestones that pointed him toward Shinnecock.

## A Detour That Changed Everything

After Quito, Shah began looking east, toward Asia and India, both for opportunity and for connection. He joined the Indian Golf Premier League, the circuit founded in 2025 to widen the pathway for Indian and Indian-origin golfers. Then chance intervened. Stranded in India earlier this year by flight disruptions tied to unrest in the Middle East, Shah simply stayed \u2014 and used the time to compete and sharpen his game across the IGPL, the Asian Development Tour and the Asian Tour.

"India is very much home to me, and it's amazing to be able to represent my culture at the U.S. Open," he said. The IGPL, he added, "brought me closer to my roots and closer to my culture."

That sharpened form carried him into the U.S. Open's brutal two-stage qualifying \u2014 "golf's toughest test." Shah opened with a 68 at Pasatiempo Golf Club, then fired a five-under 137 at Dallas Athletic Club to grab one of just nine qualifying spots for Shinnecock Hills. It was the first time an IGPL-linked player had ever reached a Major.

## Why It Matters Beyond One Man

Shah arrives in a field that suddenly looks like a generational turning point for diaspora golf. Indo-British Aaron Rai became the first Indian-origin golfer to win a Major just last month at the PGA Championship. PGA Tour winners Akshay Bhatia and Sahith Theegala are in the draw, as is Indo-Canadian Sudarshan Yellamaraju, fresh off a top-five at THE PLAYERS. Shah, who has played practice rounds alongside the likes of Tommy Fleetwood, is the newest name on that list.

"Manav is a prime example of dedication and perseverance," said Uttam Singh Mundy, the IGPL chief executive and a former Asian Tour pro. "The pathway we are creating will produce many more such stars in the years to come."

For the diaspora, Shah's story lands somewhere deeply familiar: the immigrant family that prized the safe profession, the American-born child who took the risky road, the heritage held close through a language spoken at home and summers spent in India. Whatever he shoots this week, the 33-year-old from Bakersfield has already made the point that mattered most \u2014 that a place in the Majors is within reach. "I want to stay calm," he said, "and give my best.\""""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Shinnecock Hills Golf Club in Southampton, New York, host of the 2026 U.S. Open"
img_attribution = "Wikimedia Commons"
img_final = None

# Person article: try Wikipedia first for Manav Shah
cand = fetch_wikipedia_person_image("Manav Shah (golfer)")
if not cand:
    cand = fetch_wikipedia_person_image("Manav Shah")
if cand:
    img_caption = "Manav Shah, the first IGPL-associated golfer to reach a Major, in the field at the 2026 U.S. Open"
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

# Fallback: Wikimedia Commons photo of the venue (topical, permanent)
if not img_final:
    for q in ["Shinnecock Hills Golf Club", "Shinnecock Hills", "U.S. Open golf Shinnecock"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "Shinnecock Hills Golf Club in Southampton, New York, host of the 2026 U.S. Open"
                break
        if img_final:
            break

# Last resort: Aaron Rai (named diaspora figure mentioned in the article)
if not img_final:
    cand3 = fetch_wikipedia_person_image("Aaron Rai")
    if cand3:
        img_caption = "Aaron Rai, who last month became the first Indian-origin golfer to win a Major, is among five diaspora players in the 2026 U.S. Open field"
        img_final = upload_to_supabase(cand3, f"{art_slug}.jpg")

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
        {"name": "IANS \u2014 Gujarat's Manav Shah makes history as first IGPL golfer to tee up at U.S. Open", "url": "https://ianslive.in/gujarats-manav-shah-makes-history-as-first-igpl-golfer-to-tee-up-at-us-open--20260616174827"},
        {"name": "Yardbarker \u2014 Gujarat's Manav Shah Makes History As First IGPL Golfer To Tee Up At U.S. Open", "url": "https://www.yardbarker.com/golf/"},
        {"name": "PGA Tour \u2014 Qualifiers for all 2026 majors", "url": "https://www.pgatour.com/"},
        {"name": "The Times \u2014 US Open 2026: tee times, guide and key holes at brutal Shinnecock Hills", "url": "https://www.thetimes.com/"},
    ]),
    "diaspora_angle": "Manav Shah is the immigrant-family story in miniature \u2014 a California-born son of Gujarati parents who chose golf over the expected path into medicine, kept his heritage alive through an Indian league, and now becomes the first IGPL golfer at a Major, a marker of how deep diaspora golf has grown.",
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
