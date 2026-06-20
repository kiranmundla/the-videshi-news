#!/usr/bin/env python3
"""
Sports Writer — June 20, 2026 (16:30 UTC slot)
Article: Sarpreet Singh, the Auckland-born midfielder with roots in Jalandhar,
Punjab, has become the first Sikh footballer to play at a FIFA World Cup. After
New Zealand's 2-2 draw with Iran, he spoke about paving the way for South Asian
players, ahead of NZ's crucial Group G clash with Egypt in Vancouver on Sunday.

ANGLE: A distinct diaspora football story. The Videshi has already covered the
other three Indian-origin players at WC 2026 (Velupillay, Jamshid, Moutoussamy)
but NOT Sarpreet Singh, whose Sikh-Punjabi heritage and trailblazer comments
make him the standout fresh angle, tied to a live, must-win match Sunday.

Hero: Wikipedia portrait of Sarpreet Singh; fallback to Commons NZ football /
World Cup 2026 imagery.
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
print("ARTICLE: Sarpreet Singh, first Sikh at a World Cup")
print("="*60)

art_slug = "sarpreet-singh-first-sikh-footballer-world-cup-2026-new-zealand-egypt-vancouver-jalandhar-punjab-diaspora-nri"
art_headline = "India Has Never Played a World Cup. On Sunday in Vancouver, a Punjabi From Auckland Carries Its Hopes Anyway."
art_subheadline = "Sarpreet Singh, whose parents left Jalandhar for New Zealand, has become the first Sikh footballer to play at a World Cup \u2014 and the Kiwis' must-win clash with Egypt is now appointment viewing for the diaspora."

art_body = """India have never played at a men's football World Cup. They came closest in 1950, qualifying for the tournament in Brazil after rival Asian nations withdrew, only to pull out themselves over cost and travel. Seventy-six years later, with the 2026 World Cup spread across the United States, Canada and Mexico, the country is still on the outside looking in. And yet, for the Indian diaspora, this tournament has produced a player to adopt as its own \u2014 a 27-year-old midfielder from Auckland with roots in Jalandhar, Punjab.

Sarpreet Singh did not simply make New Zealand's squad. When he took the field in the All Whites' 2-2 draw with Iran in Los Angeles on June 16, he became, by widespread reckoning, the first Sikh footballer to play at a World Cup. India-West reported he was named in the starting XI wearing the No. 10 shirt, a number that carries its own weight in football. For a community that has long watched the sport's biggest stage from a distance, the image landed with unexpected force.

## A Trailblazer Who Knows It

Singh is acutely aware of what the moment means beyond the result. "It means a lot to me, it means a lot to my people, my family, my community," he told reporters at New Zealand's team hotel in San Diego. "I'm very happy to be the first, and pave the way for the rest of them coming through. I hope to see many more Singhs and Sikhs and Punjabi footballers coming through, and Indian heritage footballers."

It is not the first barrier he has broken. In 2019, Singh became the first player of Indian descent to appear in Germany's Bundesliga when he turned out for Bayern Munich, before spells in Germany, Portugal and Serbia. He now plays for A-League club Wellington Phoenix, on loan from Serbian side TSC. His parents emigrated from Punjab to New Zealand, and Singh has spoken often of carrying their journey onto the pitch.

## Not the Only One

Singh is part of a quartet of Indian-origin players scattered across different national teams at this World Cup, each a story in itself. Australia forward Nishan Velupillay, who has Tamil and Anglo-Indian heritage, made his debut in the Socceroos' win over Turkey. Qatar's teenage winger Tahsin Jamshid was born in Doha to parents from Kerala. And DR Congo midfielder Samuel Moutoussamy traces Tamil roots through his Indo-Guadeloupean father.

Together they represent something new: for the first time, multiple players of Indian descent are competing simultaneously at football's global showpiece, even as the nation of their heritage remains absent. For fans in Edison, Fremont, Surrey and Southall, the tournament has become a treasure hunt for the next familiar surname on a team sheet.

## Sunday's Stakes in Vancouver

The romance now meets a hard deadline. Group G is the tightest at the tournament: after the opening round, New Zealand, Iran, Belgium and Egypt are all locked on a single point. The All Whites face Egypt at BC Place in Vancouver on Sunday, June 21, in a match both sides know could decide their fate. New Zealand drew all three of their games at their last World Cup, in 2010, without ever winning one \u2014 a record they are desperate to shed.

Coach Darren Bazeley's side were twice ahead against Iran before being pegged back, and the frustration was evident. "When you're leading twice in a game you come away with that 'what if?'," he said. New Zealand will lean on the physical presence of striker Chris Wood, but Egypt arrive with their own talisman in Mohamed Salah, who scored nine goals in qualifying, and a defence that conceded just twice across ten qualifiers.

## Why It Matters Here

For the diaspora, the maths is simple. A New Zealand win, with Singh in the side, would push the All Whites to the brink of a historic first knockout appearance \u2014 and put a Punjabi-heritage footballer one step deeper into a World Cup than any before him. Indian football may not have arrived on the world stage in its own colours. But on Sunday night in Vancouver, a son of Jalandhar will be wearing someone's, and a great many people watching from living rooms across North America will be counting themselves among his people."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Sarpreet Singh, the New Zealand midfielder of Punjabi heritage who has become the first Sikh footballer to play at a World Cup"
img_attribution = "Wikimedia Commons"
img_final = None

# 1) Featured-player Wikipedia portrait
wiki_img = fetch_wikipedia_person_image("Sarpreet Singh")
if wiki_img:
    got = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
    if got:
        img_final = got

# 2) Fallback: on-topic Commons imagery
if not img_final:
    for q in ["New Zealand national football team", "Wellington Phoenix footballer",
              "FIFA World Cup 2026", "association football match"]:
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
                img_caption = "A World Cup 2026 football scene; New Zealand face Egypt in Group G in Vancouver"
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
        {"name": "Reuters \u2014 New Zealand's Singh proud to blaze a trail for Sikh community at World Cup", "url": "https://www.reuters.com/sports/soccer/"},
        {"name": "RevSportz \u2014 Sarpreet Singh Hopes World Cup Breakthrough Opens Doors for South Asian Footballers", "url": "https://revsportz.in/"},
        {"name": "India-West \u2014 Players With Indian Heritage Feature At FIFA World Cup 2026", "url": "https://www.indiawest.com/"},
        {"name": "Reuters \u2014 New Zealand, Egypt searching for elusive first World Cup win in key Group G clash", "url": "https://www.reuters.com/sports/soccer/"},
    ]),
    "diaspora_angle": "India have never played a men's World Cup, but Sarpreet Singh \u2014 an Auckland-born midfielder whose parents emigrated from Jalandhar, Punjab \u2014 has become the first Sikh footballer to play at one, and his New Zealand side's must-win clash with Egypt makes the tournament personal for South Asian fans across North America.",
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
