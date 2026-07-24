#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (22:30 UTC slot / videshi-writer-sports)

Article: IPL confirms the Rishabh Pant <-> Kuldeep Yadav trade between Delhi
Capitals and Lucknow Super Giants ahead of IPL 2027.

Distinct from the recent feed:
- Recent sports feed = England Test (Headingley), MLC, India white-ball squad
  churn (SKY sacked, Reddy injured/Shedge in, ODI squad, Kohli recall),
  women's T20 WC, hockey, Wimbledon doubles, para-badminton youth haul, FIFA WC
  recaps. NONE cover the IPL trade window or the Pant-Kuldeep swap. New, fresh
  (IPL media advisory Tue June 23), high-profile.

Key facts (Cricbuzz, Reuters, Wisden, Khel Now — June 23, 2026):
- IPL confirmed via media advisory on Tuesday (June 23) the completed trade.
- Rishabh Pant returns to Delhi Capitals for INR 15 crore (down from the
  record INR 27 crore LSG paid at the 2025 mega auction). Pant took a ~INR 12
  crore pay cut to enable the move.
- Kuldeep Yadav moves the other way to Lucknow Super Giants on his existing
  INR 13.5 crore contract (DC retained him for ~INR 13.25 cr pre-2025).
- Pant spent nine seasons / first eight years of his IPL career at Delhi
  (2016-2024): 111 matches (most by any DC player), 3,284 runs (franchise
  leading run-scorer), captained DC in 43 matches (2021-2024). Released ahead
  of the 2025 mega auction after differences with the GMR Group ownership.
- LSG stint underwhelming: 269 runs (2025) and 312 runs (2026); finished 7th
  and 10th; stepped down as captain after IPL 2026.
- Kuldeep: joined DC in 2022, 72 wickets in 65 matches at economy 8.24 over
  five seasons; below-par 2026 (10 wickets, economy 10.30 — worst of his
  10-season career). LSG becomes his third IPL franchise after KKR and DC.
  Move is a partial homecoming — he plays domestic cricket for Uttar Pradesh.
- Deal first reported by Cricbuzz on May 29, now formalised. Takes effect IPL
  2027 (season ~March-May 2027).

DIASPORA ANGLE: The IPL is the diaspora's loudest shared spring ritual — watch
parties from Edison to Wembley. Pant (a Test hero whose 2026 Headingley century
the diaspora just celebrated) returning "home" to Delhi, and the economics of a
record contract unwound by a voluntary pay cut, is the kind of franchise drama
NRIs follow as closely as any match.

Hero: Wikipedia REST API photo of Rishabh Pant (person-led source rule:
Wikipedia/Commons first). upload.wikimedia.org permanent URL, re-uploaded to
Supabase storage.
"""

import os, sys, json, io
from datetime import datetime, timezone

import requests
from PIL import Image

# -- ENV --
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


def fetch_wikipedia_person_image(name):
    """Wikipedia REST summary -> originalimage/thumbnail source URL."""
    import urllib.parse
    enc = urllib.parse.quote(name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc}",
            headers={"User-Agent": UA}, timeout=20,
        )
        if r.status_code == 200:
            d = r.json()
            orig = d.get("originalimage", {}).get("source")
            thumb = d.get("thumbnail", {}).get("source")
            return orig or thumb
    except Exception as e:
        print(f"  wiki fetch error: {e}")
    return None


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
print("ARTICLE: Pant <-> Kuldeep IPL trade confirmed (DC <-> LSG)")
print("="*60)

art_slug = "ipl-2027-rishabh-pant-kuldeep-yadav-trade-confirmed-delhi-capitals-lucknow-super-giants-15-crore-pay-cut-homecoming-diaspora-nri"
art_headline = "Rishabh Pant Is Going Home to Delhi \u2014 and He Took a 12-Crore Pay Cut to Get There"
art_subheadline = "The IPL has confirmed the season's biggest trade: Pant returns to Delhi Capitals for INR 15 crore while Kuldeep Yadav heads to Lucknow, unwinding the record deal that made Pant the most expensive cricketer in the league's history."

art_body = """When Lucknow Super Giants paid INR 27 crore for Rishabh Pant at the 2025 mega auction, it was the largest winning bid the Indian Premier League had ever seen \u2014 a statement that the franchise was building its future around India's most electric wicketkeeper-batter. Eighteen months later, that future has been quietly dismantled. The IPL confirmed through a media advisory on Tuesday that Pant will return to Delhi Capitals for INR 15 crore, with left-arm wrist-spinner Kuldeep Yadav moving the other way to Lucknow for INR 13.5 crore. It is the most significant player trade in recent IPL memory, and it formalises a deal first reported in late May.

The headline is not just the swap, but the economics. To make the move possible, Pant accepted a pay cut of roughly INR 12 crore, slashing his fee from the record 27 crore to 15. A contract that size had become an anchor; no franchise could realistically absorb it in a trade, and so the player himself agreed to take less to engineer his way home. It is a move reminiscent of Ravindra Jadeja's fee reduction to join Rajasthan Royals a season earlier \u2014 a sign of how the league's biggest names are increasingly willing to bend the math to control where they play.

## A Homecoming Nine Seasons in the Making

For Pant, Delhi is not a new badge but an old one. He spent the first eight years of his IPL career with the franchise between 2016 and 2024, turning out 111 times \u2014 more than any other player in Delhi Capitals history \u2014 and scoring 3,284 runs, which still leaves him the club's leading run-scorer. He captained the side in 43 matches between 2021 and 2024 before differences with the GMR Group ownership saw him released ahead of the 2025 mega auction. His return closes a loop that few expected to be reopened so soon.

The Lucknow chapter, by contrast, never caught fire. Pant managed 269 runs in 2025 and 312 in 2026, modest returns for a player of his ceiling, and LSG finished seventh and then tenth across his two seasons in charge. Shortly after this year's elimination, the franchise announced that Pant had asked to step down as captain, with the decision effective immediately. The trade is, in that sense, a clean break for both sides.

## Kuldeep's Quiet Move the Other Way

Kuldeep Yadav's journey to Lucknow has been overshadowed by the bigger name leaving it, but it matters too. The spinner enjoyed a productive five seasons at Delhi after joining in 2022, taking 72 wickets in 65 matches at an economy of 8.24 and reinventing himself as a white-ball force. His 2026 was a rare dip \u2014 just 10 wickets at an economy of 10.30, the worst of his ten IPL campaigns \u2014 and the trade gives him a fresh start at his third franchise after Kolkata Knight Riders and Delhi.

There is a homecoming flavour to his move as well. Kuldeep has long played his domestic cricket for Uttar Pradesh, the state Lucknow represents, and joining the Super Giants brings him closer to that base. On the same INR 13.5 crore contract under which Delhi retained him, he becomes a marquee bowling addition for a franchise that has badly needed one.

## Why the Diaspora Will Be Watching

For Indians abroad, the IPL is the spring ritual that binds living rooms from Edison to Wembley to the Bay Area \u2014 the one tournament that turns a weeknight into a watch party. Pant carries a particular charge with that audience right now: it was only days ago that the diaspora was celebrating his century at Headingley in India's new-look Test side. To see him return to Delhi, the franchise where he grew up as a cricketer, adds a layer of sentiment to a deal that is, on paper, about salary-cap arithmetic.

It is also a reminder of how the IPL's player market has matured into something the diaspora follows like a sport of its own \u2014 the auctions, the retentions, the trades dissected in WhatsApp groups across three continents. A record contract unwound by a voluntary pay cut, two India internationals swapping cities, and a homecoming a decade in the making: the 2027 season is still months away, but its first big story has already been written."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia REST API \u2014 Rishabh Pant)...")
img_caption = "Rishabh Pant, who returns to Delhi Capitals in the IPL 2027 trade window after two seasons with Lucknow Super Giants"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_url = fetch_wikipedia_person_image("Rishabh Pant")
if wiki_url:
    print(f"  Wikipedia image: {wiki_url}")
    img_final = upload_to_supabase(wiki_url, f"{art_slug}.jpg")

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
        {"name": "Cricbuzz \u2014 DC and LSG complete Pant-Kuldeep trade ahead of IPL 2027", "url": "https://www.cricbuzz.com/cricket-news/"},
        {"name": "Reuters \u2014 Pant returns to Delhi in IPL swap with Kuldeep", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Wisden \u2014 Rishabh Pant Takes Pay Cut To Return To DC, Kuldeep Yadav Joins LSG In IPL Trade Deal", "url": "https://wisden.com/"},
    ]),
    "diaspora_angle": "The IPL is the diaspora's loudest shared spring ritual, and Pant's pay-cut homecoming to Delhi \u2014 days after NRIs celebrated his Headingley century \u2014 is exactly the kind of franchise drama Indians abroad follow as closely as any match.",
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
