#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (19:30 UTC slot / videshi-writer-sports)

Article: The BWF World Championships return to India for the first time in 17
years — New Delhi, Indira Gandhi Indoor Stadium, Aug 17–23, 2026 — and ticket
sales (via BookMyShow, from June 22) have just gone live. India's home stars
(Sindhu, Lakshya Sen, Satwik–Chirag) will play a Worlds on home soil for the
first time in their careers.

DEDUP CHECK (vs recent ~4 days of sports feed):
- Feed is cricket-heavy (England/India squads, Headingley Test, women's T20 WC,
  Pant trade, MLC, Vaibhav Sooryavanshi) plus one-off athletics/other:
  Neeraj/AFI awards (Jun 24), Animesh Kujur sprinter (Jun 24), women's 4x100m
  relay gold (Jun 24), Jagmeet Singh basketball (Jun 24), Asian fencing/Bhavani
  Devi (Jun 24), para-badminton youth games Mersin (Jun 23), Manika Batra TT
  (Jun 22), CWG smaller contingent (Jun 21).
- The BWF WORLD CHAMPIONSHIPS 2026 coming to New Delhi + ticket launch appears
  NOWHERE in the feed. Wholly uncovered. (The para-badminton youth-games piece
  is a separate event; this is the senior BWF Worlds.)

Key facts (BAI press release via MediaBrief, RevSportz, SportsMint,
PassionateInMarketing; Wikipedia 2026 BWF World Championships; BookMyShow —
June 20–23, 2026):
- 30th edition of the BWF World Championships, the sport's flagship individual
  event, held at the Indira Gandhi Indoor Stadium (Indira Gandhi Arena),
  New Delhi, from Monday Aug 17 to Sunday Aug 23, 2026 (7 days, 5 disciplines).
- First time India has hosted the Worlds since Hyderabad 2009 — a 17-year gap.
  Only India's second time ever hosting (Hyderabad 2009 the first).
- Badminton Association of India (BAI) named BookMyShow the official ticketing
  partner; tickets went on sale June 22. Over 6,000 seats for the general
  public, six price categories, Early Bird from INR 499, premium up to
  INR 5,500, plus a 15% Early Bird discount on the other five categories.
  Sales released in phases (opening four days first); pricing consistent
  through to the Finals.
- Home field: Lakshya Sen, PV Sindhu, and men's doubles pair Satwiksairaj
  Rankireddy & Chirag Shetty will play a BWF Worlds on home soil for the FIRST
  TIME in their careers.
- Global field: world No. 1 women's singles An Se-young; Chinese men Shi Yu Qi
  and Li Shi Feng; Indonesian doubles Fajar Alfian & Muhammad Shohibul Fikri;
  strong contingents from Malaysia, Thailand, Indonesia.
- Quote — Sanjay Mishra, General Secretary, BAI: "The BWF World Championships
  coming to New Delhi is a landmark moment for Indian badminton and for the
  fans who have fuelled the sport's rise over the years. Our ambition is not
  just to host a world-class tournament, but to deliver a fan experience that
  matches the occasion — accessible, seamless and worthy of an event of this
  stature."
- India's Worlds record: 15 medals since 1983 (1 gold, 4 silver, 10 bronze);
  PV Sindhu leads with five, including the historic 2019 gold (Basel). India
  has won at least one medal at every edition since 2011 — 15 straight years.
- Context: the Indira Gandhi Indoor Stadium hosted the Yonex-Sunrise India Open
  2026 in January as the official test event. Note: badminton was EXCLUDED from
  the reduced Glasgow 2026 Commonwealth Games programme, so the home Worlds is
  the marquee badminton occasion of India's 2026.

DIASPORA ANGLE: Badminton is, after cricket, the sport the Indian diaspora most
closely follows — and Sindhu, Sen and Satwik–Chirag are household names in NRI
homes from New Jersey to Surrey. A home Worlds is a rare, fixed date on the
calendar that diaspora families plan India trips around; with global ticketing
on BookMyShow and an August window that overlaps the NRI summer-travel season,
this is an event many will literally fly back for. It also lands as badminton
booms in diaspora communities abroad, where weekend club leagues in the US, UK,
Canada and the Gulf are increasingly Indian-run.

Hero: Wikipedia/Wikimedia Commons photo of PV Sindhu (real photo of a named
athlete in the field). Pexels/generic stock NOT used (rules forbid generic
stock for a named athlete).
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


def fetch_wikipedia_person_image(name):
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
print("ARTICLE: BWF World Championships return to New Delhi 2026")
print("="*60)

art_slug = "bwf-world-championships-2026-new-delhi-india-host-first-time-17-years-tickets-bookmyshow-indira-gandhi-stadium-sindhu-lakshya-sen-satwik-chirag-diaspora-nri"
art_headline = "Badminton's Biggest Stage Comes Home: India Hosts the World Championships for the First Time in 17 Years"
art_subheadline = "Tickets are live for the BWF World Championships in New Delhi this August \u2014 and PV Sindhu, Lakshya Sen and Satwik\u2013Chirag will play a Worlds on home soil for the first time in their careers."

art_body = """For seven days this August, the biggest individual prize in world badminton will be decided not in Copenhagen, Tokyo or Paris, but at the Indira Gandhi Indoor Stadium in New Delhi. The Badminton Association of India (BAI) has thrown open ticket sales for the 2026 BWF World Championships, and with that the countdown has begun on a homecoming 17 years in the making.

India last hosted the Worlds in Hyderabad in 2009. The wait since has spanned an entire era of Indian badminton \u2014 the rise of Saina Nehwal, the breakthrough of PV Sindhu, the doubles revolution led by Satwiksairaj Rankireddy and Chirag Shetty. For all of them, a World Championships at home has remained the one box left unticked. From August 17 to 23, that finally changes.

## What Is on Sale, and for How Much

BAI has named BookMyShow the official ticketing partner, with sales opening on June 22. More than 6,000 seats will be released to the general public across six price categories, beginning as low as INR 499 under an Early Bird offer, with premium matchday seats at INR 5,500. Fans can claim a 15 per cent Early Bird discount across the other five categories for a limited window. Tickets are being released in phases \u2014 the opening four days first \u2014 with prices held consistent all the way through to the finals.

"The BWF World Championships coming to New Delhi is a landmark moment for Indian badminton and for the fans who have fuelled the sport's rise over the years," said Sanjay Mishra, General Secretary of the BAI. "Our ambition is not just to host a world-class tournament, but to deliver a fan experience that matches the occasion \u2014 accessible, seamless and worthy of an event of this stature."

## A Home Worlds for a Golden Generation

The draw will read like a who's who of the modern game. Sindhu, the most decorated Indian in the event's history, returns to a Worlds stage she has owned \u2014 five medals, including the historic 2019 gold in Basel that made her the first Indian world champion. Lakshya Sen brings the men's singles hopes, while Rankireddy and Shetty, the most successful men's doubles pair India has ever produced, will chase a title in front of a home crowd for the very first time.

https://www.instagram.com/p/DZ44vWcNSG1/

They will not have it easy. The field is stacked with the sport's global elite: women's singles world No. 1 An Se-young of South Korea, Chinese men's contenders Shi Yu Qi and Li Shi Feng, and Indonesian doubles specialists Fajar Alfian and Muhammad Shohibul Fikri. The traditional South-East Asian powers \u2014 Malaysia, Thailand and Indonesia \u2014 will all arrive in force. The Indira Gandhi Indoor Stadium is no stranger to this calibre of badminton; it staged the Yonex-Sunrise India Open in January as the official test event.

The timing also gives the Worlds added weight in India's 2026 calendar. Badminton was left out of the slimmed-down Glasgow Commonwealth Games programme this year, stripping the country's shuttlers of one of their most reliable medal stages. The home Worlds is, in effect, the marquee badminton occasion of the Indian sporting summer \u2014 a stage that cannot be cut from a budget.

## Why the Diaspora Should Care

After cricket, badminton may be the sport the Indian diaspora follows most closely. Sindhu, Sen and the Satwik\u2013Chirag pairing are household names in NRI living rooms from New Jersey to Surrey to Dubai, where weekend club leagues have become increasingly Indian-run as the sport booms abroad. For families who grew up watching these players win medals on foreign soil, the chance to see them compete for a world title in India carries a particular pull.

There is a practical dimension, too. A fixed, week-long event in mid-to-late August lands squarely in the NRI summer-travel window, and with global ticketing handled through BookMyShow, it is exactly the kind of occasion a diaspora family can plan an India trip around. Few sporting events offer that combination \u2014 a genuine world championship, on home soil, at a moment when so many are already heading back.

Seventeen years is a long time to wait for the world to come to you. This August, in a packed arena in the capital, India's badminton faithful \u2014 at home and abroad \u2014 finally get their turn to host it."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia \u2014 PV Sindhu)...")
img_caption = "India's PV Sindhu, the country's most decorated player at the BWF World Championships, headlines the home field in New Delhi this August."
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("P. V. Sindhu")
if not wiki_img:
    wiki_img = fetch_wikipedia_person_image("PV Sindhu")
if wiki_img:
    print(f"  Wikipedia image: {wiki_img}")
    img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "badminton",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "MediaBrief \u2014 BWF World Championships New Delhi 2026, BookMyShow ticketing", "url": "https://mediabrief.com/"},
        {"name": "RevSportz \u2014 BWF World Championships 2026 Tickets Go Live", "url": "https://revsportz.in/"},
        {"name": "SportsMint Media \u2014 BookMyShow to power ticket sales for BWF World Championships", "url": "https://sportsmintmedia.com/"},
        {"name": "Wikipedia \u2014 2026 BWF World Championships", "url": "https://en.wikipedia.org/wiki/2026_BWF_World_Championships"},
    ]),
    "diaspora_angle": "After cricket, badminton is the sport the Indian diaspora follows most closely \u2014 and PV Sindhu, Lakshya Sen and Satwik\u2013Chirag are household names in NRI homes abroad. A home World Championships in mid-August, with global ticketing on BookMyShow, lands in the NRI summer-travel window and is exactly the kind of fixed-date event diaspora families plan an India trip around.",
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
