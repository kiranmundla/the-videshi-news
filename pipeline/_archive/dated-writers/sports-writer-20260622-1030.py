#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (10:30 UTC slot / videshi-writer-sports)

Article: Harmanpreet Kaur became the FIRST cricketer across genders to play
200 T20 Internationals, reaching the milestone on Sun June 21, 2026 as she
walked out for the toss in India's Women's T20 World Cup 2026 group match vs
South Africa at Old Trafford, Manchester. Poignant symmetry: she made her
T20I debut in June 2009 in England (vs England at Taunton, inaugural WT20WC),
so the landmark came in the same country, in the same tournament, 17 years on.

KEY FACTS (verified across The Bridge, Female Cricket, Cricbuzz, Yardbarker,
CricketAddictor):
- 200th T20I = first cricketer male or female. NZ's Suzie Bates next on 184,
  Danni Wyatt-Hodge (Eng) 183, Ellyse Perry (Aus) 177, Smriti Mandhana 169.
  Men's most-capped: Ireland's Paul Stirling 163, Rohit Sharma 159.
- Career to milestone: 4,123 T20I runs in 178 innings @ 30.09, 17 fifties,
  one century — the iconic 103 off 51 (7x4, 8x6) vs NZ, 2018 WT20WC opener.
- Debut: ODI 7 Mar 2009 vs Pakistan (Bowral); T20I 11 Jun 2009 vs England
  (Taunton). Age 37 (b. 8 Mar 1989).
- Special '200' jersey presented by coach Amol Mazumdar before the toss.
- Quote (at toss): "It's been an amazing journey. I never thought I'll come
  this far, but God has been really kind and I'm really thankful to him, my
  family, friends, and all my teammates."
- Bowling coach Aavishkar Salvi: called her a "top-level athlete" and "role
  model for almost all cricketers globally."
- Context: led India to its maiden ODI World Cup title 8 months ago in Navi
  Mumbai, beating South Africa in the final.
- The milestone match itself: India 158/7, SA chased 161/4 in 19.1 (India
  lost). Harmanpreet made 24 off 22. (The defeat was covered separately; THIS
  piece is the career/milestone story, not a match report.)

DEDUP: Checked last 3 days of sports — covered: women's hockey Nations Cup,
Manika Batra Asian Games row, ETPL launch, Glasgow CWG contingent, India
women's T20 WC LOSS to SA (Kapp 81 — match report), Kohli ODI recall, MLC
run-fests, India-England Test Day 1, Afghanistan ODI sweep, Sarpreet Singh
WC, US Open golf, FIFA WC recaps. Harmanpreet's 200-T20I milestone / career
retrospective is FRESH and UNCOVERED (the SA match report is a different
article and a different angle).

ANGLE: A landmark for the most enduring figure in women's cricket, and a
clean diaspora hook — Harmanpreet's 17-year arc mirrors the rise of the
women's game in India that NRIs have followed with growing pride, and the
milestone landing in England (where she debuted) gives it a story-book frame.

Hero: Wikipedia REST API portrait of Harmanpreet Kaur. Person article →
Wikipedia first.
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
            thumb = data.get("thumbnail", {}).get("source")
            orig = data.get("originalimage", {}).get("source")
            img = thumb or orig
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=82):
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
print("ARTICLE: Harmanpreet Kaur — first to 200 T20Is")
print("="*60)

art_slug = "harmanpreet-kaur-first-cricketer-200-t20i-milestone-women-t20-world-cup-2026-old-trafford-south-africa-debut-2009-england-diaspora-nri"
art_headline = "Seventeen Years After Her First Match in England, Harmanpreet Kaur Walked Out for Her 200th — a Number No Cricketer Had Ever Reached"
art_subheadline = "India's captain became the first player, man or woman, to appear in 200 T20 Internationals. That it happened at a World Cup in the same country where she debuted as a teenager in 2009 made the milestone read like a story written in advance."

art_body = """When Harmanpreet Kaur walked out for the toss at Old Trafford on Sunday, she was handed a jersey with a single number stitched across the back: 200. It marked her 200th T20 International — a figure no cricketer, in the men's game or the women's, has ever reached. India's captain now stands alone at the top of the most-capped list in the format, and she got there in the place where it all began.

The symmetry was almost too neat. Harmanpreet made her T20I debut in June 2009, against England at Taunton, at the inaugural Women's T20 World Cup. Seventeen years later, the milestone arrived in the same country, at the same tournament, against South Africa at Emirates Old Trafford in the 2026 edition. "It's been an amazing journey," she said at the toss. "I never thought I'll come this far, but God has been really kind and I'm really thankful to him, my family, friends, and all my teammates."

## A Number That Stands Alone

The gap behind her tells its own story. New Zealand's Suzie Bates, the next most-capped T20I cricketer across both games, sits on 184 appearances. England's Danni Wyatt-Hodge has 183, Australia's Ellyse Perry 177, and India's own vice-captain Smriti Mandhana 169. In men's cricket, the leader is Ireland's Paul Stirling on 163, with Rohit Sharma next on 159 — which means Harmanpreet has now played a full season's worth of internationals more than any man has managed in the shortest format.

It is a record built on rare longevity. The 37-year-old has been a fixture in India's side through nearly the entire modern history of women's T20 cricket, a span in which the game went from an afterthought to a professionalised, broadcast, IPL-backed sport. Her career has tracked that transformation almost match for match.

## More Than Endurance

The 200 is not a monument to mere survival. Across 199 T20Is before Sunday, Harmanpreet had compiled 4,123 runs in 178 innings at an average of 30.09, with 17 half-centuries and one unforgettable hundred. That century — 103 off 51 balls against New Zealand in the opening game of the 2018 T20 World Cup, laced with seven fours and eight sixes — remains one of the format's defining individual innings, the night she dragged India to 194 and announced that the women's game had a genuine superstar.

Her influence has only deepened as captain. Eight months ago she lifted India's first senior World Cup of any kind, leading the side to the 2025 ODI World Cup title in Navi Mumbai — beating, as it happens, the same South Africa she faced in her milestone match. India's bowling coach Aavishkar Salvi did not reach for understatement when asked about her. "She's a role model for almost all cricketers globally," he said. "The way she has conducted herself over the years... she's been a performer in any format."

The match itself did not go India's way — they posted 158 for 7 and South Africa chased it down with five balls to spare, Harmanpreet falling for 24. But the result, on this particular afternoon, was a footnote to the occasion.

## Why It Resonates Abroad

For the Indian diaspora, Harmanpreet is one of the faces through which the women's game crossed over. NRIs who grew up watching only the men's team have, over the last decade, found a second side to follow — and her 2017 World Cup semi-final 171 not out against Australia, and that 2018 century, were the kind of performances that travelled, shared across WhatsApp groups from Sydney to San Jose. Her steady climb mirrors a larger pride: a women's team that now sells out grounds, commands a professional league, and wins world titles.

There is also something in the shape of the story that lands with a community built on long journeys far from home. A teenager who debuted in near-anonymity in 2009, who kept showing up for 17 years as the structures around her were slowly built, and who now holds a record no one in the sport's history can claim — it is a narrative of persistence rewarded, and it reads the same in Ludhiana as it does in London.

## What Comes Next

The retirement questions that surface around any 37-year-old captain were raised again before this tournament, and Harmanpreet brushed them aside. Her appetite, by every account inside the camp, remains undimmed. India still have a World Cup to chase, and their skipper — now 200 caps deep and counting — intends to be there at the business end of it. The number on her back will keep climbing. For now, it is one that belongs to her alone."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person article)...")
img_caption = "Harmanpreet Kaur, India's captain and the first cricketer to play 200 T20 Internationals"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Harmanpreet Kaur")
if wiki_img:
    img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

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
        {"name": "The Bridge \u2014 Harmanpreet Kaur becomes first cricketer to play 200 T20Is", "url": "https://thebridge.in/cricket"},
        {"name": "Female Cricket \u2014 Harmanpreet Kaur Creates History, Becomes First Cricketer to Play 200 T20Is", "url": "https://femalecricket.com"},
        {"name": "Cricbuzz \u2014 Seventeen years on, Harmanpreet stands alone at 200 T20Is", "url": "https://www.cricbuzz.com"},
        {"name": "Yardbarker \u2014 Harmanpreet Kaur pulls off a cricket first even Rohit Sharma and Virat Kohli haven't", "url": "https://www.yardbarker.com"},
    ]),
    "diaspora_angle": "Harmanpreet Kaur is one of the players through whom the Indian diaspora embraced the women's game, and her 17-year climb to a record 200 T20Is mirrors the rise of women's cricket in India that NRIs have followed with growing pride \u2014 a story of persistence rewarded that resonates across a community built on long journeys far from home.",
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
