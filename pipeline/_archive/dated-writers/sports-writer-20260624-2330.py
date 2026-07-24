#!/usr/bin/env python3
"""
Sports Writer — June 24, 2026 (23:30 UTC slot / videshi-writer-sports)

Article: Day one of the 65th National Inter-State Senior Athletics
Championships at Bhubaneswar's Kalinga Stadium (June 24-28, 2026) — a record-
breaking opening night. 18-year-old Anushka Yadav broke the women's hammer
throw national record TWICE in 40 minutes (65.64m then 67.02m, erasing Sarita
Singh's 65.25m mark from 2017), becoming India's youngest national record
holder and sealing an Asian Games berth. Dev Meena raised his own pole vault
NR to 5.46m, and Jyothi Yarraji returned from 383 days out to win the 100m
hurdles heat in 13.14s — all three booking Aichi-Nagoya 2026 Asian Games spots.

DEDUP CHECK (vs recent ~3 days sports feed, category=sports):
- Feed is cricket-heavy (England/India squads, Headingley Test, women's T20 WC,
  Pant trade, MLC) plus athletics one-offs: Neeraj Chopra Doha comeback (Jun 24),
  the INAUGURAL INDIAN ATHLETICS AWARDS (Jun 24), Animesh Kujur sprinter (Jun 24),
  women's 4x100m relay gold at Asian Relays (Jun 24).
- This article is the 65th NATIONAL INTER-STATE CHAMPIONSHIPS at Bhubaneswar —
  a brand-new domestic meet (opened Jun 24) with fresh national records. It is
  NOT the Awards ceremony (a black-tie honours night) and NOT the Asian Relays
  (a separate continental event in China). The Inter-State meet, Anushka Yadav,
  Dev Meena's 5.46m, and Jyothi Yarraji's comeback appear NOWHERE in the feed.
  Wholly uncovered. Animesh Kujur is a different athlete/story.

Key facts (Indian Express; ANI via webindia123; Inshorts; News Dive/IE;
Yardbarker/IANS; saartaj/PTI — June 24, 2026):
- 65th National Inter-State Senior Athletics Championships, Kalinga Stadium,
  Bhubaneswar, Odisha. June 24-28, 2026. A key Asian Games qualification meet.
- Anushka Yadav (Uttar Pradesh, Baleni village, Baghpat district), 18:
  - Opened with 62.07m (already over the AFI's 61.72m Asian Games qual mark).
  - 2nd round 65.64m — broke Sarita A Singh's national record of 65.25m (2017).
  - Final attempt 67.02m — broke her own brand-new record again. Two NRs in
    ~40 minutes. Also erased the meet record (65.03m, Rachna, 2023).
  - Becomes India's YOUNGEST national record holder.
  - Huge leap from her previous official PB of 62.89m (National Games 2025).
  - Father Sushil Yadav: a thrower who quit at 18 for "family duties and
    marriage"; pushed his children into hammer throw — son (16) first, then
    Anushka. Trains at Sri Krishna Inter College Ground near her village (also
    home to Rachna and Tanya Chaudhary, who finished 2nd to Anushka here).
    Coached by Sushil + Chirag Yadav + Gagan Yadav.
  - Quote: "I can't express my happiness of booking a berth to board a flight
    to the Japan Asian Games." / "thankful to my family... I was on the injured
    list earlier in March."
- Dev Kumar Meena (Madhya Pradesh): cleared 5.46m in men's pole vault — new
  national record, over the 5.45m Asian Games qual mark. Second straight NR-
  breaking outing; a month earlier he'd SHARED the 5.45m NR with training
  partner Kuldeep Kumar at the Federation Cup, Ranchi — now holds it alone.
  Men's pole vault NR has improved five times in under two years. Quote: "It is
  good to improve the national record before going to the Glasgow Commonwealth
  Games." Top 3 vaulters all beat the old 5.20m meet record (M Gowtham, 2025).
- Jyothi Yarraji: returned after 383 days off the track, winning the women's
  100m hurdles heat in 13.14s and booking her Asian Games spot.
- Mohammed Afsal: met the men's 800m Asian Games qual mark in 1:47.69.
- 2026 Asian Games: Aichi-Nagoya, Japan, Sept 19 - Oct 4, 2026.
- VERIFIED X EMBEDS (both @afiindia, official AFI handle, verified VALID with
  photos via verify-tweet.sh):
  - Anushka: https://x.com/afiindia/status/2069792533849444578
  - Dev Meena: https://x.com/afiindia/status/2069788586887741847

DIASPORA ANGLE: For NRIs who only see Indian sport through the cricket lens,
the country's Olympic-sport pipeline is quietly deepening — and it is being
built by teenagers from small-town and farming families (Anushka from a Baghpat
village, daughter of a thrower who gave up the sport himself). The Asian Games
in Japan this September is the next global stage where the diaspora can follow,
and increasingly cheer for, names beyond the cricket XI.

Hero: Wikimedia Commons photo of Kalinga Stadium (the actual venue of the meet
— permanent, on-topic, factual). Anushka has no Wikipedia/Commons photo; the
verified AFI tweet of her record throw is embedded inline so readers see the
athlete. Pexels/generic stock NOT used.
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
print("ARTICLE: Anushka Yadav NR + Inter-State Championships Day 1")
print("="*60)

art_slug = "anushka-yadav-18-hammer-throw-national-record-twice-67-02m-inter-state-athletics-bhubaneswar-2026-dev-meena-pole-vault-jyothi-yarraji-asian-games-qualify-diaspora-nri"
art_headline = "Eighteen, and a National Record Twice in Forty Minutes: Anushka Yadav Announces Herself"
art_subheadline = "On the opening night of the National Inter-State Championships in Bhubaneswar, an 18-year-old hammer thrower from a Baghpat village broke India's record twice \u2014 part of a record-laden evening that also sent Dev Meena and a returning Jyothi Yarraji to the Asian Games."

art_body = """For nine years, the women's hammer throw national record sat untouched at 65.25 metres. On Wednesday night at Bhubaneswar's Kalinga Stadium, an 18-year-old broke it twice in the space of forty minutes.

Anushka Yadav, from Baleni village in Uttar Pradesh's Baghpat district, opened her competition at the 65th National Inter-State Senior Athletics Championships with 62.07m \u2014 already past the Athletics Federation of India's 61.72m qualifying mark for the 2026 Asian Games. Then she found another gear. Her second-round throw of 65.64m erased Sarita Singh's mark from 2017. Her final attempt landed at 67.02m, breaking her own brand-new record and making her, by some distance, the youngest national record holder in Indian athletics.

x-official:https://x.com/afiindia/status/2069792533849444578

The leap is hard to overstate. Her previous official personal best was 62.89m, set while winning gold at last year's National Games. In one evening she added more than four metres to it and rewrote the record books in a discipline where India has rarely featured on the global stage.

## A Record Built at Home

Anushka's story is, in the way of so many Indian track-and-field tales, a family one. Her father, Sushil Yadav, was a thrower himself \u2014 one who walked away from the sport at 18 for, in his words, "family duties and marriage." The ambition he set aside he passed on to his children. His son, now 16, took up the hammer first; then Anushka, who admits she "initially preferred running," was talked into trying it.

"I can't express my happiness of booking a berth to board a flight to the Japan Asian Games," she said after the competition, having earlier this year spent time on the injured list. She trains at the Sri Krishna Inter College Ground near her village \u2014 a modest facility that has quietly produced a line of hammer throwers, including Tanya Chaudhary, who finished second to Anushka on Wednesday.

## A Night of Records

Anushka was the headline, but not the only one. Dev Meena of Madhya Pradesh cleared 5.46m in the men's pole vault to set a national record of his own \u2014 his second record-breaking outing in a month. In May he had shared the 5.45m national mark with training partner Kuldeep Kumar at the Federation Cup in Ranchi; by adding a single centimetre in Bhubaneswar, he now holds it alone. India's men's pole vault record has now improved five times in under two years.

x-official:https://x.com/afiindia/status/2069788586887741847

"It is good to improve the national record before going to the Glasgow Commonwealth Games," Meena said. He, too, cleared the Asian Games qualifying standard of 5.45m.

Then there was the comeback. Jyothi Yarraji, India's premier women's hurdler, returned after 383 days away from competition and won her 100m hurdles heat in 13.14 seconds \u2014 enough to book her own Asian Games place. Middle-distance runner Mohammed Afsal joined the qualifiers too, clocking 1:47.69 in the men's 800m. Four athletes, four tickets to Aichi-Nagoya, all on the meet's opening evening, with four more days of competition still to run.

## Why the Diaspora Should Look Beyond the Boundary

For a community that experiences Indian sport largely through the cricket scorecard, nights like this are a reminder that the country's Olympic-sport pipeline is deepening \u2014 and that it is being built, increasingly, by teenagers from farming and small-town families. Anushka is the daughter of a thrower who never got his own chance; Dev Meena is part of a pole-vault cohort rewriting records almost monthly.

The next global checkpoint is the Asian Games in Japan, from September 19 to October 4, a stage that runs in time zones friendly to viewers across North America, the UK and the Gulf. The cricket XI will always command the diaspora's attention. But the names that filled the Kalinga Stadium scoreboard on Wednesday \u2014 Yadav, Meena, Yarraji \u2014 are the ones worth learning now, before the rest of the world does."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikimedia Commons \u2014 Kalinga Stadium, the venue)...")
img_caption = "Bhubaneswar's Kalinga Stadium, host venue of the 65th National Inter-State Senior Athletics Championships, where multiple national records fell on the opening night."
img_attribution = "Wikimedia Commons"
img_final = None

commons_img = "https://upload.wikimedia.org/wikipedia/commons/5/5d/Aerial_view_of_Kalinga_Stadium_%28Night%29.jpg"
img_final = upload_to_supabase(commons_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 inserting without image")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "athletics",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "The Indian Express \u2014 Farmer's daughter Anushka Yadav becomes India's youngest national record holder", "url": "https://indianexpress.com/section/sports/"},
        {"name": "ANI via Webindia123 \u2014 Jyothi Yarraji, Anushka Yadav book Asian Games 2026 spots", "url": "https://news.webindia123.com/news/sports.asp"},
        {"name": "IANS via Yardbarker \u2014 National Inter-State Athletics: Dev Meena, Anushka, Jyothi brighten Day One", "url": "https://www.yardbarker.com/cricket/articles/inter_state_athletics_2026_dev_meena_anushka_yadav_break_national_records_secure_asian_games_tickets/s1_17725_43989762"},
        {"name": "Inshorts \u2014 18-yr-old Anushka Yadav sets new national record in hammer throw", "url": "https://inshorts.com/"},
    ]),
    "diaspora_angle": "For a diaspora that follows Indian sport mostly through cricket, the Inter-State Championships show an Olympic-sport pipeline deepening \u2014 led by teenagers from farming and small-town families \u2014 ahead of the Asian Games in Japan this September, a stage the diaspora abroad can watch and rally behind beyond the cricket XI.",
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
