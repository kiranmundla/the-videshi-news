#!/usr/bin/env python3
"""
Sports Writer — June 16, 2026 (10:30 UTC run)
Article: The 2026 Canada Tri-Nation Series (ICC Cricket World Cup League 2)
concludes today in King City, Ontario — Canada vs Netherlands, the finale of
a six-match ODI round contested by Canada, the USA and the Netherlands. The
diaspora angle: the two North American national sides are built almost
entirely of South Asian (largely Indian and Pakistani) migrant talent, all
fighting for points on the road to 2027 World Cup qualification.
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
            img = data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php", params=params,
            headers={"User-Agent": UA}, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 400:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "title": page.get("title", ""),
                })
            if results:
                print(f"  \u2713 Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  \u26a0 Wikimedia Commons error for '{search_query}': {e}")
    return []


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
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        content = None
        if r.status_code != 200:
            import subprocess
            tmp = f"/tmp/{filename}"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                content = open(tmp, "rb").read()
            else:
                print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
                return None
        else:
            ct = r.headers.get("Content-Type", "")
            if not ct.startswith("image/"):
                print(f"  \u2717 Not an image: {ct}")
                return None
            if len(r.content) < 5000:
                print(f"  \u2717 Image too small: {len(r.content)} bytes")
                return None
            content = r.content

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
print("ARTICLE: Canada Tri-Nation Series — diaspora-built cricket in Ontario")
print("="*60)

art_slug = "canada-tri-nation-series-2026-cwc-league-2-usa-netherlands-south-asian-diaspora-cricket-king-city-nri"
art_headline = "Two North American Teams, One Ontario Ground, and a Squad List That Reads Like a Punjab Phone Book."
art_subheadline = "Canada close out a six-match ODI tri-series against the Netherlands and the USA on Tuesday in King City. The cricket is about 2027 World Cup points. The story is who is playing it \u2014 sides built almost entirely of South Asian migrants."

art_body = """On Tuesday at the Maple Leaf Cricket Club in King City, Ontario, Canada play the Netherlands in the sixth and final match of a tri-nation one-day series. It is the nineteenth round of the ICC Cricket World Cup League 2, the unglamorous qualifying ladder that decides which Associate nations reach the 2027 World Cup in South Africa, Zimbabwe and Namibia. There is no television fanfare, no packed house. But for a particular slice of the Indian and South Asian diaspora, this small tournament on a suburban Toronto ground is one of the most quietly resonant cricket stories of the summer.

Look at the team sheets and you understand why. Canada took the field under Saad Bin Zafar, with Harsh Thaker, Nicholas Kirton, Shreyas Movva, Yuvraj Samra, Kaleem Sana, Pargat Singh, Sukhjinder Singh and Dilpreet Bajwa among the names. The United States, the third side in the series, are captained by Monank Patel and feature Milind Kumar, Saurabh Netravalkar, Harmeet Singh, Saiteja Mukkamalla, Shubham Ranjane and Sanjay Krishnamurthi. Two national teams of North America, and the overwhelming majority of both rosters trace directly back to India, Pakistan and the wider subcontinent.

## A Series Decided By Migrants

The cricket itself has been absorbing. The USA opened with an eight-wicket win over Canada on June 6, powered by Shehan Jayasuriya's unbeaten 113. The Netherlands then edged the Americans by 21 runs, Harmeet Singh \u2014 a Mumbai-born left-arm spinner who once played age-group cricket alongside future India stars \u2014 taking 4 for 26. Canada hit back to beat the Dutch by two wickets, Shreyas Movva's 83 not out seeing them home. Then on June 12 came the highlight: Milind Kumar, born in Delhi and a former Sikkim and Services batsman in India's domestic system, struck an unbeaten 111 to chase down 276 against Canada.

The fifth match, between the Netherlands and the USA, was washed out by Ontario rain. That left Tuesday's Canada-Netherlands finale to settle the round, with World Cup qualifying points \u2014 not pride alone \u2014 on the line.

## The Indian Domestic System's Export Market

What makes these names land for the diaspora is their backstory. Milind Kumar piled up runs for years in the Ranji Trophy before concluding that the queue in front of him in Indian cricket was simply too long, and moving to the United States. Harmeet Singh was once a India Under-19 World Cup winner. Saurabh Netravalkar, the USA's new-ball spearhead, is the software engineer whose spell against Pakistan at the 2024 T20 World Cup became a sensation across diaspora WhatsApp groups. Canada's ranks are thick with Punjab-born and Punjabi-Canadian cricketers who grew up on the same maidans as the men now wearing India blue.

These are, in other words, the players the Indian system could not absorb \u2014 and who found, in the cricket clubs of Brampton, the Bay Area and Texas, a second sporting life and eventually a national cap. It is the same migration story that defines so many diaspora families, transposed onto a cricket field: talent that left, rebuilt, and now competes on the world stage under a different flag.

## Why It Matters in Brampton and Beyond

For the roughly two million people of Indian origin in Canada \u2014 and the heavy South Asian concentration in Greater Toronto specifically \u2014 a Canadian national team that looks like the neighbourhood is a source of genuine pride. King City sits less than an hour from Brampton, sometimes called the most South Asian city in North America. Cricket there is not an exotic import; it is the weekend default, played on park grounds and watched on phones.

The bigger prize is 2027. League 2 is the grind that keeps the World Cup dream alive for both Canada and the USA, and every point in a tri-series like this one nudges them closer to or further from the global stage. The USA already tasted that stage as co-hosts in 2024. Canada, twice a World Cup participant, want back in.

So when Canada and the Netherlands walk out in King City on Tuesday, the scoreline will matter to the qualification table. But for diaspora families watching from Mississauga to Edison to Surrey, the deeper meaning is simpler and older: this is their game, their kids, their migration written in runs and wickets \u2014 finally being played at a level the world has to count."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
# Hero: try a recognizable diaspora player from the series, in priority order.
img_caption = ""
img_attribution = "Wikimedia Commons"
img_final = None

candidates = [
    ("Saurabh Netravalkar", "Saurabh Netravalkar, the USA's Indian-origin new-ball bowler, part of the tri-series in King City, Ontario"),
    ("Monank Patel", "USA captain Monank Patel, one of many Indian-origin players in the Canada tri-nation series"),
    ("Milind Kumar", "Milind Kumar, the Delhi-born batsman now with the USA, who scored an unbeaten 111 in the series"),
    ("Harmeet Singh (cricketer, born 1992)", "Harmeet Singh, the Mumbai-born spinner now representing the USA"),
]

for name, cap in candidates:
    cand = fetch_wikipedia_person_image(name)
    if cand:
        up = upload_to_supabase(cand, f"{art_slug}.jpg")
        if up:
            img_final = up
            img_caption = cap
            break

if not img_final:
    # Commons fallback: a generic but specific cricket-at-Maple-Leaf / ODI scene
    for q in ["Maple Leaf Cricket Club King City", "Canada national cricket team", "cricket match ODI"]:
        results = fetch_wikimedia_commons_images(q)
        for res in results:
            up = upload_to_supabase(res["url"], f"{art_slug}.jpg")
            if up:
                img_final = up
                img_caption = "Cricket in Canada, where the national side is built largely of South Asian diaspora players"
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
    "image_caption": img_caption or "Cricket in Canada, built largely of South Asian diaspora players",
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Wikipedia \u2014 2026 Canada Tri-Nation Series", "url": "https://en.wikipedia.org/wiki/2026_Canada_Tri-Nation_Series"},
        {"name": "ESPNcricinfo \u2014 ICC Cricket World Cup League 2", "url": "https://www.espncricinfo.com"},
        {"name": "International Cricket Council \u2014 Eight-team CWC League 2 on the road to 2027", "url": "https://www.icc-cricket.com"},
        {"name": "DreamCricket \u2014 Jayasuriya's maiden ODI century takes USA past Canada", "url": "https://www.dreamcricket.com"},
    ]),
    "diaspora_angle": "Two North American national cricket teams \u2014 Canada and the USA \u2014 are built almost entirely of Indian, Pakistani and South Asian migrants, and this Ontario tri-series is where the diaspora's lost cricketing talent now competes for a 2027 World Cup berth.",
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
