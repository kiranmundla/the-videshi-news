#!/usr/bin/env python3
"""
Sports Writer — June 18, 2026 (22:30 UTC run)
Article: Anahat Singh — at 18, the Delhi squash player has cracked the world's
top 20, won the Squash on Fire Open in Washington (beating World No. 10
Georgina Kennedy) and defended her JSW Indian Open title in Mumbai. India's
biggest hope for squash's Olympic debut at LA 2028.

SQUASH is an untouched vertical on the dashboard (cricket, chess, tennis,
golf, football, hockey, athletics, shooting, WNBA, badminton are all covered).
Strong diaspora angle: huge South Asian squash following in US/UK/Canada and
LA 2028 Olympic inclusion.

Hero image: Anahat Singh has a Wikipedia page but NO portrait. Try her page
first, then Commons squash imagery.
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
print("ARTICLE: Anahat Singh — India's squash teenager, top 20, LA 2028")
print("="*60)

art_slug = "anahat-singh-squash-top-20-indian-open-squash-on-fire-open-la-2028-olympics-india-diaspora-2026"
art_headline = "She Is 18, She Beat the World No. 10 in Washington, and She Is India's Best Shot at an Olympic Squash Medal"
art_subheadline = "Anahat Singh has cracked the world's top 20, defended her Indian Open title in Mumbai and become the youngest Asian woman ever to climb that high. With squash entering the Olympics for the first time at LA 2028, the teenager from Delhi is carrying a sport \u2014 and a diaspora \u2014 on her shoulders."

art_body = """NEW DELHI \u2014 For most of squash's long history, the sport has lived in the shadows: played on glass courts tucked inside clubs and gymnasiums, beloved by those who play it and largely invisible to everyone else. India has had its champions \u2014 Saurav Ghosal, Joshna Chinappa, Dipika Pallikal \u2014 but they competed for medals at the Asian Games and Commonwealth Games, never the one stage that turns athletes into household names. That is about to change. And when squash makes its Olympic debut at Los Angeles 2028, India's brightest hope will be an 18-year-old from Delhi who has spent this season quietly dismantling the established order.

Her name is Anahat Singh, and the numbers around her have started to feel implausible. This winter, at the Squash on Fire Open in Washington, she beat England's Georgina Kennedy \u2014 the world No. 10 and a reigning Commonwealth Games champion \u2014 12-10, 11-5, 11-7 in the final. The win pushed her inside the world's top 20 and made her the youngest Asian woman ever to reach that ranking. A few weeks later, on a glass court set up on the outfield of the Cricket Club of India in Mumbai, she defended her JSW Indian Open title in front of a roaring home crowd, beating Egypt's Hana Moataz 11-5, 11-6, 9-11, 11-6.

## A Prodigy, On Schedule

Anahat is not a surprise. She is a prodigy arriving exactly when the people who have tracked her always said she would. Born in Delhi in 2008 to parents who both played field hockey, she first picked up a badminton racket because she idolised P. V. Sindhu and dreamed of the Olympics. She drifted to squash following her older sister Amira to tournaments, fell for the sport, and never looked back.

The junior record reads like a travel itinerary: the British Junior Open at under-11 in 2019, then a flood of European, Dutch, Scottish, German and American junior titles. At 14, she became the youngest Indian ever to compete at the Commonwealth Games. At the 2022 Asian Games she won two bronze medals and became the youngest Indian to ever medal at the event. By late 2023 she was the country's senior national champion \u2014 again, the youngest ever.

Then came the season that announced her to the professional tour. In 2024, Anahat won nine PSA Tour titles in a single year \u2014 the first woman to do so since the legendary Nicol David in 2010 \u2014 winning 38 of 40 matches, 31 of them in straight games. In 2025 she added two Asian Championship golds, a World Junior Championship bronze (becoming the first Indian woman to reach that semi-final in 15 years), and was part of the India team that won the country's first-ever Squash World Cup. The PSA named her both Young Player of the Year and Challenger Player of the Year.

## The Olympic Stakes

What makes this season different is the destination. In October 2023, the International Olympic Committee confirmed squash for the Los Angeles 2028 Games \u2014 the culmination of a campaign the sport had waged for decades. For a discipline long denied its biggest stage, it is everything. And for India, which has invested in squash academies and produced a steady stream of world-class talent without ever winning an Olympic medal in the sport, it is a once-in-a-generation opening.

Anahat will be 20 when those Games begin, deep into her physical prime, with a team around her built for exactly this moment: she is mentored by Ghosal, the finest male player India has produced, and coached by former world No. 1 Gr\u00e9gory Gaultier and Italy's St\u00e9phane Galifi. The trajectory is not subtle. The teenager who once won bronze in doubles alongside Joshna Chinappa is now the player India is building its Olympic hopes around.

## Why the Diaspora Should Watch

Squash is, quietly, one of the diaspora's sports. Walk into a racquet club in New Jersey, suburban London or the Greater Toronto Area and you will find South Asian families on the courts, kids in goggles drilling boasts and drops. It is a sport the community already plays and loves but rarely sees represented at the elite level on screens back home. Anahat Singh changes that calculus.

She loses, too \u2014 a first-round exit to Nardine Garas at the British Open in May, a tough loss to Egypt's Hania El Hammamy in El Gouna. The Egyptian dynasty that rules women's squash is not going to part easily. But she is 18, and the gap is closing match by match. For NRI parents looking for a role model who looks like their daughters \u2014 composed, fearless, and rewriting records on her way up \u2014 the wait is over. Her name is worth learning now, because by Los Angeles, everyone will know it."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Indian squash player Anahat Singh, who has climbed inside the world's top 20 at 18"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Try Anahat Singh's own Wikipedia portrait
wiki_img = fetch_wikipedia_person_image("Anahat Singh")
if wiki_img:
    got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
    if got:
        img_final = got
        img_caption = "Indian squash player Anahat Singh, the youngest Asian woman to break into the world's top 20"

# 2) Fallback: on-topic Commons squash imagery
if not img_final:
    commons_queries = [
        "Anahat Singh squash",
        "Anahat Singh",
        "India squash player",
        "squash glass court PSA",
        "squash player women",
    ]
    for q in commons_queries:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["squash", "singh", "anahat", "racquet", "court"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                if "anahat" in low or "singh" in low:
                    img_caption = "Indian squash player Anahat Singh, India's brightest hope for the sport's Olympic debut at LA 2028"
                else:
                    img_caption = "Professional squash \u2014 the sport set to make its Olympic debut at Los Angeles 2028, where Anahat Singh is India's biggest medal hope"
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
    "vertical": "diaspora-sport",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Squash Info \u2014 Top Seeds Abhay Singh & Anahat Singh Secure Home Double at Indian Open", "url": "https://www.squashinfo.com/"},
        {"name": "Female In Sports \u2014 Teen Sensation Anahat Singh Stuns World No. 10 to Win Squash On Fire Open 2026", "url": "https://femaleinsports.com/"},
        {"name": "Squash Info \u2014 Anahat Singh player profile and results", "url": "https://www.squashinfo.com/"},
        {"name": "Wikipedia \u2014 Anahat Singh", "url": "https://en.wikipedia.org/wiki/Anahat_Singh"},
        {"name": "IOC \u2014 Squash added to the Olympic programme for LA 2028", "url": "https://olympics.com/"},
    ]),
    "diaspora_angle": "Squash is quietly one of the diaspora's sports \u2014 South Asian families fill racquet clubs in New Jersey, suburban London and the Greater Toronto Area \u2014 yet the community rarely sees itself represented at the elite level. Anahat Singh, 18, of Delhi, has cracked the world's top 20 (the youngest Asian woman ever to do so), beaten the world No. 10, and become India's best hope for a medal when squash debuts at the LA 2028 Olympics. A composed, fearless role model for NRI families and their daughters.",
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
