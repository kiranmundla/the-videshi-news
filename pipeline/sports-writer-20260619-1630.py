#!/usr/bin/env python3
"""
Sports Writer — June 19, 2026 (16:30 UTC run)
Article: Samuel Moutoussamy — the fourth and least-known of the Indian-origin
players at the 2026 World Cup. DR Congo's defensive midfielder (#8, Atromitos),
born in Paris, with a Tamil-Guadeloupean paternal lineage and a Congolese
mother. He played all 90 minutes of DR Congo's 1-1 draw with Portugal in
Houston on June 17.

ANGLE: A solo profile. The Videshi has already run group roundups of the four
Indian-origin players and standalone pieces on Sarpreet Singh, Nishan
Velupillay and Tahsin Jamshid — but NOT on Moutoussamy. He has the deepest and
least-told diaspora thread of the four: 19th-century Tamil indentured migration
to the French Caribbean (Guadeloupe), a chapter of the Indian diaspora most
NRIs have never heard of. He follows Vikash Dhorasoo (France 2006), the first
player of Indian descent at a World Cup.

Hero: Samuel Moutoussamy has a Wikipedia/Commons portrait (verified). Fall back
to on-topic Commons imagery, then skip.
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
print("ARTICLE: Samuel Moutoussamy — the fourth Indian-origin player")
print("="*60)

art_slug = "samuel-moutoussamy-dr-congo-tamil-guadeloupe-fourth-indian-origin-player-world-cup-2026-portugal-houston-nri"
art_headline = "He Was Born in Paris, His Mother Is Congolese, and His Tamil Roots Run Through a Caribbean Island. Meet the Fourth Indian at This World Cup."
art_subheadline = "Samuel Moutoussamy played all 90 minutes of DR Congo's 1-1 draw with Portugal in Houston \u2014 the least-known of the four players carrying Indian heritage onto the 2026 World Cup stage, and the one with the longest, strangest journey home to it."

art_body = """HOUSTON \u2014 When DR Congo walked out at NRG Stadium on June 17 to hold European giants Portugal to a 1-1 draw, the No. 8 anchoring their midfield played the full ninety minutes without fuss \u2014 two tackles, an 84 percent pass-completion rate, a couple of efforts that forced corners. To most of the 71,000 watching, Samuel Moutoussamy was simply a disciplined Congolese holding midfielder doing a hard, unglamorous job against one of the best teams on earth. To a smaller audience scattered across the world, he was something else: the fourth player of Indian descent at this World Cup, and the one whose roots travel the furthest to get here.

India's men did not qualify for the 2026 World Cup, as they never have. Yet this tournament features an unprecedented four players who trace their ancestry to the subcontinent \u2014 New Zealand's Sarpreet Singh, Australia's Nishan Velupillay, Qatar's Tahsin Mohammed Jamshid, and Moutoussamy. The first three have stories that map neatly onto the modern diaspora: Punjabi parents in Auckland, a Tamil father in Melbourne, a Keralite family in Doha. Moutoussamy's thread is older and stranger, and it runs through a French Caribbean island most Indians have never thought to look for themselves on.

## A Tamil Line Through Guadeloupe

Born in Paris on August 12, 1996, Moutoussamy is the son of a Congolese mother and an Indo-Guadeloupean father. That paternal surname \u2014 Moutoussamy, an unmistakable Tamil name \u2014 is the clue. His father's ancestors were among the tens of thousands of Tamils shipped from southern India to Guadeloupe in the second half of the 19th century, indentured labourers brought in to cut sugarcane after the abolition of slavery in the French colonies. They came on multi-year contracts, many never to return, and their descendants built a community that endures on the island today, complete with Hindu temples and Tamil festivals folded into Caribbean life.

It is a chapter of the Indian diaspora that rarely makes it into the NRI conversation, which tends to orbit Silicon Valley, the Gulf, and the old Commonwealth. Guadeloupe sits outside all of it. And so when Moutoussamy lines up for the Democratic Republic of the Congo, he carries three continents at once \u2014 an African nation on his shirt, a European city on his birth certificate, and a Tamil name handed down through the Caribbean.

## A Footballer in His Own Right

The heritage is the hook, but Moutoussamy has earned his place on merit. A graduate of the French youth system, he made his name at FC Nantes, where he spent seven seasons and played more than 140 matches in Ligue 1. Spells in the Netherlands and Turkey followed before he settled at Atromitos in the Greek Super League. Internationally he chose DR Congo, his mother's country, and has since won more than 50 caps \u2014 including a run to the semi-finals of the 2023 Africa Cup of Nations, the Leopards' best showing in a generation.

At 29, he is the elder statesman among the four Indian-origin players in North America, and the only one already established as a senior international fixture rather than a breakout name. Against Portugal he did the quiet work of a defensive midfielder facing Cristiano Ronaldo's heirs \u2014 screening the back line, snuffing out transitions, keeping the ball moving \u2014 and DR Congo's point felt like a minor triumph for a side ranked among the tournament's underdogs.

## The Dhorasoo Lineage

Moutoussamy is not the first footballer of Indian descent to grace a World Cup. That distinction belongs to Vikash Dhorasoo, the France midfielder of Mauritian-Indian heritage who featured at the 2006 finals. But two decades on, the sight of four such players at a single World Cup marks how widely the diaspora has spread \u2014 and how many routes there now are from an Indian bloodline to football's biggest stage.

## What Comes Next

DR Congo sit second in Group K with a point, level with Portugal and behind only Colombia. Their next test is a meeting with Colombia in Guadalajara on June 23, before a final group game against Uzbekistan in Atlanta on June 27 \u2014 a fixture on US soil that will be within reach of the country's large South Asian community, should they choose to adopt the Leopards' No. 8 as one of their own. For a diaspora that has waited in vain for India to reach a World Cup, Samuel Moutoussamy offers an unlikely, roundabout way in \u2014 by way of Paris, Kinshasa, and a sugarcane island in the Caribbean Sea."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "DR Congo midfielder Samuel Moutoussamy, who traces his paternal roots to Tamil indentured migrants in Guadeloupe"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Subject athlete (Wikipedia portrait)
for person, cap in [
    ("Samuel Moutoussamy", "DR Congo midfielder Samuel Moutoussamy, of Tamil-Guadeloupean and Congolese descent, one of four players of Indian origin at the 2026 World Cup"),
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
    for q in ["Samuel Moutoussamy", "DR Congo national football team", "Congo football"]:
        cands = fetch_wikimedia_commons_images(q)
        for c in cands:
            low = c["title"].lower()
            print(f"   candidate: {c['title']} ({c['w']}x{c['h']})")
            if any(bad in low for bad in ["logo", ".svg", ".pdf", "map", "seating",
                                           "letters", "diagram", "chart", "flag", "icon"]):
                continue
            if not any(g in low for g in ["moutoussamy", "congo", "leopards", "football"]):
                continue
            got = upload_to_supabase(c["url"], f"{art_slug}.jpg")
            if got:
                img_final = got
                img_caption = "DR Congo's national football team at the 2026 World Cup"
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
    "vertical": "football",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Sporting News \u2014 Is Samuel Moutoussamy of Indian origin? Meet DR Congo player set for FIFA World Cup debut", "url": "https://www.sportingnews.com/"},
        {"name": "Sporting News \u2014 Did Samuel Moutoussamy play yesterday? Performance in Portugal vs DR Congo", "url": "https://www.sportingnews.com/"},
        {"name": "Khel Now \u2014 Who is Samuel Moutoussamy? Indian-origin player who starred for DR Congo vs Portugal", "url": "https://www.khelnow.com/"},
        {"name": "India-West \u2014 Players With Indian Heritage Feature At FIFA World Cup 2026", "url": "https://www.indiawest.com/"},
        {"name": "Sky Sports \u2014 World Cup 2026 fixture schedule", "url": "https://www.skysports.com/"},
    ]),
    "diaspora_angle": "Samuel Moutoussamy is the fourth and least-known player of Indian descent at the 2026 World Cup \u2014 and the one with the deepest diaspora thread, tracing his Tamil roots to 19th-century indentured migrants in the French Caribbean island of Guadeloupe. For a diaspora that has never seen India reach a World Cup, he is an unlikely point of connection, and his June 27 group game against Uzbekistan in Atlanta will be within reach of America's South Asian community.",
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
