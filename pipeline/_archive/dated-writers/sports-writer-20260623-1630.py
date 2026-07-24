#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (16:30 UTC slot / videshi-writer-sports)

Article: Rishabh Pant returns to Delhi Capitals in a blockbuster IPL trade with
Lucknow Super Giants; Kuldeep Yadav moves the other way. BCCI officially
confirmed the swap on Tuesday, June 23, ahead of IPL 2027.

Distinct from the recent feed:
- The recent sports feed = England Test (Headingley), MLC, India white-ball
  squad churn (SKY sacked, Shedge maiden call-up), women's T20 WC, hockey,
  Wimbledon. NONE cover the IPL Pant/Kuldeep trade. This is a NEW, same-day
  BCCI release (June 23) about a marquee franchise swap. Different event.

Key facts (Reuters / Wisden / Cricket Times / Dainik Bhaskar, June 23):
- BCCI on Tue June 23 officially confirmed a direct trade between Delhi
  Capitals (DC) and Lucknow Super Giants (LSG), effective IPL 2027.
- Rishabh Pant (28) returns to DC — the franchise where he spent nine seasons
  (2016-2024), 111 appearances (most by any player for DC), 3,284 runs (DC's
  leading run-scorer), captain in 43 matches across four seasons (2021-2024).
- Pant takes a major pay cut: from the record INR 27 crore LSG paid at the
  2025 mega auction (highest winning bid in IPL history) down to INR 15 crore.
  ~INR 12 crore reduction; compared to Ravindra Jadeja's similar step joining
  Rajasthan Royals last season.
- Kuldeep Yadav moves to LSG on his existing INR 13.5 crore contract. Left-arm
  wrist-spinner; 5 seasons at DC (joined 2022), 72 wickets in 65 matches,
  10 wickets in 12 games in IPL 2026. LSG is his 3rd franchise (after KKR, DC).
  Homecoming feel — he played domestic cricket for Uttar Pradesh (Lucknow).
- Pant's LSG stint: 2 seasons, both missed playoffs (2025, 2026). 269 runs @
  24.45 SR 133.16 in 2025 (lowest aggregate since debut); 312 runs @ 28.36 in
  2026. Stepped down as captain after LSG's 2026 elimination.
- Parth Jindal (DC co-owner, JSW Group reassuming full operational control)
  posted a heartfelt X note thanking Kuldeep and welcoming Pant: "Dear Kuldeep
  thank you for your service over the last 5 years @DelhiCapitals... Rishabh –
  Kiran and I are both happy to have you back at DC."

DIASPORA ANGLE: The IPL is the diaspora's most-watched cricket property, and
Pant — India's Test talisman and a wicketkeeper-batter NRIs follow obsessively
— returning to his "home" franchise resets the most-followed storyline of the
2027 season for fans in the US, UK and Gulf who plan their nights around it.

Hero: Wikipedia REST API portrait — Rishabh Pant. Person-led -> Wikipedia first.
Inline embed: official @delhicapitals Instagram welcome-back reel (June 23).
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
            img = orig or thumb
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
print("ARTICLE: Pant returns to Delhi Capitals; Kuldeep to LSG")
print("="*60)

art_slug = "rishabh-pant-returns-delhi-capitals-kuldeep-yadav-lucknow-super-giants-ipl-2027-trade-pay-cut-27-crore-15-crore-diaspora-nri"
art_headline = "Pant Goes Home: Delhi Capitals Bring Back Their Talisman, and Send Kuldeep the Other Way"
art_subheadline = "In the biggest IPL trade in years, Rishabh Pant has returned to Delhi Capitals on a steep pay cut while spinner Kuldeep Yadav moves to Lucknow Super Giants, ending the league's most expensive experiment after just two seasons."

art_body = """Eighteen months after one of the most expensive divorces in cricket, the Indian Premier League's biggest name is going home. The Board of Control for Cricket in India confirmed on Tuesday that Rishabh Pant will return to Delhi Capitals as part of a blockbuster trade, with left-arm wrist-spinner Kuldeep Yadav moving in the opposite direction to Lucknow Super Giants. The swap, finalised just weeks after IPL 2026 ended, takes effect ahead of the 2027 season and instantly reshapes the league's pecking order.

For Pant, it is a homecoming in the truest sense. Delhi is the franchise where he grew up in front of the cricketing world, spending nine seasons between 2016 and 2024, making a club-record 111 appearances and scoring 3,284 runs — more than any other player in the team's history. He captained the side in 43 matches across four seasons. "One of the defining faces of the franchise for nearly a decade," the BCCI said in its release. The reunion brings to a close a short and costly detour.

## The Most Expensive Experiment in IPL History

That detour began at the 2025 mega auction, when Lucknow Super Giants paid a tournament-record 27 crore rupees — the highest winning bid the IPL has ever seen — to make Pant the face of their franchise and their captain. It never came together. Lucknow missed the playoffs in both 2025 and 2026, and Pant's own form fell short of the billing: 269 runs at an average of 24.45 in his first season, his lowest aggregate since his 2016 debut, followed by 312 runs at 28.36 the next. Soon after this year's elimination, he asked to be relieved of the captaincy, and the franchise accepted with immediate effect — a clear signal that bigger changes were coming.

https://www.instagram.com/reel/DZ7YuYbNuZC/

The financial reset is almost as striking as the cricketing one. To make the trade work, Pant has accepted a sharp pay cut, with his contract value falling from 27 crore to roughly 15 crore rupees — a reduction of about 12 crore. It is a move reminiscent of Ravindra Jadeja's decision last season to trim his fee to enable a switch to Rajasthan Royals, and a reminder that even the league's marquee men now bend their salaries to engineer the moves they want.

## Kuldeep's Quiet Homecoming

The player heading the other way has his own reasons to feel at ease. Kuldeep Yadav joins Lucknow on his existing 13.5 crore rupee contract after five productive seasons at Delhi, where he arrived in 2022 and took 72 wickets in 65 matches, including 10 in 12 games during IPL 2026. Lucknow becomes the third franchise of his career, after Kolkata Knight Riders and Delhi, but the move carries a homecoming flavour of its own: Kuldeep is a product of Uttar Pradesh's domestic system, and Lucknow is, in effect, his home ground.

Delhi co-owner Parth Jindal, with the JSW Group reassuming full operational control of the franchise, marked the day with a heartfelt note on social media. "Dear Kuldeep, thank you for your service over the last five years," he wrote. "You have been a core part of our team and you will be sorely missed. Go well — you are a champion player. Rishabh, Kiran and I are both happy to have you back at DC. Hope you can find your best form back home in Delhi."

## Why the Diaspora Will Be Watching

For Indian fans abroad, the IPL is not just another tournament — it is the cricket property that organises their year, the one whose fixtures get screened in pubs in London, sports bars in New Jersey and living rooms across the Gulf at all hours. And no storyline travels further than Rishabh Pant's. He is India's Test talisman, a wicketkeeper-batter whose fearless, improbable innings have become diaspora folklore, and his survival and recovery from a near-fatal 2022 car crash made him a figure followed with something closer to affection than fandom.

Watching him return to the franchise that made him, in the blue of Delhi rather than the colours of a record contract that never delivered, gives the 2027 season a ready-made emotional centre. For the millions of NRIs who plan their evenings around the league, the trade does something simple but powerful: it puts one of their favourite players back where the story feels right. The cricket will be judged on runs and wins, as it always is. But the homecoming itself is the kind of moment the diaspora cricket calendar is built around."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first \u2014 person-led article)...")
img_caption = "Rishabh Pant, who returns to Delhi Capitals in an IPL trade with Lucknow Super Giants"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Rishabh Pant", "Rishabh Pant, who returns to Delhi Capitals after a blockbuster IPL trade with Lucknow Super Giants"),
]:
    wiki_img = fetch_wikipedia_person_image(person)
    if wiki_img:
        candidate = upload_to_supabase(wiki_img, f"{art_slug}.jpg")
        if candidate:
            img_final = candidate
            img_caption = cap
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
        {"name": "Reuters \u2014 Pant returns to Delhi in IPL swap with Kuldeep", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "Wisden \u2014 Rishabh Pant takes pay cut to return to DC, Kuldeep Yadav joins LSG", "url": "https://www.wisden.com"},
        {"name": "Cricket Times \u2014 Parth Jindal posts heartfelt note following Pant and Kuldeep trade", "url": "https://www.crickettimes.com"},
    ]),
    "diaspora_angle": "The IPL is the diaspora's most-watched cricket property, and Rishabh Pant \u2014 India's Test talisman and a wicketkeeper-batter NRIs follow obsessively \u2014 returning to his home franchise hands the 2027 season a ready-made emotional centre for fans in the US, UK and Gulf who organise their nights around the league.",
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
