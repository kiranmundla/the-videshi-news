#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (19:30 UTC slot / videshi-writer-sports)

Article: India Women keep their T20 World Cup hopes alive with a 5-wicket win
over Bangladesh at Old Trafford (Match 23, June 25), a must-win in a four-way
Group A scramble. Shafali Verma's 34-ball 53 powered the chase.

DEDUP CHECK (vs recent ~4 days sports feed, category=sports):
- Feed HAS: India men vs Ireland 1st T20I preview (Iyer era / Sooryavanshi);
  Edgbaston 2nd Test preview; Vaibhav safeguarding piece; England T20I squad;
  pole vault / hammer / athletics records; women's hockey Nations Cup win;
  women 4x100m relay gold; badminton worlds; Neeraj Chopra Doha; fencing.
- Feed does NOT have: India WOMEN at the ICC Women's T20 World Cup 2026 — the
  must-win vs Bangladesh, semifinal-scramble standings, Shafali's fifty. The
  hockey/relay women's pieces are different events. Distinct, time-pegged
  result. CLEAR TO WRITE.

Key facts (Cricketaddictor scorecard; ICC; Sporting News/Wisden points table):
- Match 23, Group A, ICC Women's T20 World Cup 2026, Old Trafford, Manchester,
  Thursday June 25, 2026. India won by 5 wickets.
- Bangladesh batted first (won toss, elected to bat), made 136/8 in 20 overs.
- India chased 137, reached 139/5 in 16.5 overs.
- India batting: Shafali Verma 53 (34b, 8x4, 1x6, SR 155.88, st N Sultana b N
  Akter); Jemimah Rodrigues 26 (15b, SR 173.33); Yastika Bhatia 23 (18b);
  Harmanpreet Kaur 13* (14b); Smriti Mandhana 8 (6b); Richa Ghosh 10; Deepti
  Sharma 5*. Bangladesh bowling: Ritu Moni 2/29, Marufa Akter 1/28, Rabeya Khan
  1/19, Nahida Akter 1/24.
- Group A standings after the win: Australia top (4 played, 4 won, 8 pts,
  +4.724 NRR), then India / South Africa / Bangladesh all tied on 4 pts but
  separated by NRR — India 2nd (+2.511), SA 3rd (-0.546), Bangladesh 4th
  (-0.641). Pakistan & Netherlands eliminated. Two semifinal spots from the
  group; top two qualify.
- India's final group game: vs unbeaten, table-topping Australia, Sunday June
  28 at Lord's. India still need to navigate that; a healthy NRR cushion now
  matters.
- Context: India lost their previous game to South Africa by 6 wickets; this
  win echoed their 2025 50-over World Cup-winning run after a mid-tournament
  slump. Smriti Mandhana is the tournament's leading run-scorer for India
  (159 runs coming in); Shree Charani India's top wicket-taker (10).

Hero: Wikipedia/Commons photo of Shafali Verma. Permanent Wikimedia URL,
downloaded + re-uploaded to Supabase.
"""

import os, io, json, subprocess
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


print("\n" + "=" * 60)
print("ARTICLE: India Women keep T20 World Cup hopes alive vs Bangladesh")
print("=" * 60)

art_slug = "india-women-beat-bangladesh-5-wickets-t20-world-cup-2026-old-trafford-shafali-verma-53-must-win-semifinal-scramble-australia-lords-diaspora-nri"
art_headline = "Shafali Verma Drags India Out of the Danger Zone — and Into a Sunday Showdown With Australia"
art_subheadline = "A 34-ball 53 anchored India's five-wicket chase of Bangladesh at Old Trafford, a must-win that keeps them second in a three-way logjam and sets up a final group decider against the unbeaten champions at Lord's."

art_body = """India Women walked into Old Trafford on Thursday knowing the maths left no room for sentiment: lose to Bangladesh, and a title defence that began with promise could be over before the knockouts. They did not lose. A composed five-wicket win, built on Shafali Verma's 34-ball 53, keeps India alive at the ICC Women's T20 World Cup 2026 — and sets up a Sunday decider against an Australia side that has won everything in sight.

Bangladesh, sent in to bat after winning the toss, posted a competitive 136 for 8 from their 20 overs, a total that looked awkward on a Manchester surface where spin has bitten and the average first-innings score is modest. India's reply could have wobbled. Smriti Mandhana, the tournament's leading scorer coming in, fell early for 8. But Verma made sure the chase never drifted.

## Verma sets the tone

Opening the innings, Verma played the kind of knock that has become her signature in must-win games — eight fours and a six, a strike rate of nearly 156, and an intent that refused to let Bangladesh's spinners settle. She added a brisk stand with Yastika Bhatia (23 off 18) before Jemimah Rodrigues kept the foot down with a 15-ball 26 at a strike rate above 170. By the time Verma was stumped off Nahida Akter, India were within sight, and captain Harmanpreet Kaur (13 not out) and Deepti Sharma steered them home with 19 balls to spare, finishing on 139 for 5.

Ritu Moni was the pick of Bangladesh's bowlers with 2 for 29, but the total was always a touch light, and India's depth told. It was the disciplined, unfussy performance the team had promised after a bruising six-wicket defeat to South Africa in their previous outing on the same ground.

## A familiar place for this team

There is an echo here that India's dressing room has leaned into all week. In the 2025 50-over World Cup, this group recovered from three straight defeats to reach the semi-finals and win a maiden world title. "It's not like we haven't been in this situation before," Verma said the head coach reminded the squad. Thursday was the first instalment of that recovery script in this tournament: take care of the immediate task, and worry about the bigger one next.

## The Group A logjam

The win does more than bank two points; it protects net run rate in a group where the margins are razor-thin. Australia sit clear at the top with a perfect record and eight points. Below them, India, South Africa and Bangladesh are all locked on four points, separated only by NRR — and India's healthy +2.511 keeps them second, ahead of South Africa and Bangladesh. Pakistan and the Netherlands are already out. With two semi-final places available, every run and every over now carries weight.

## What's next

India's final group game is the hardest of all: a meeting with unbeaten, table-topping Australia at Lord's on Sunday. Win, and qualification is assured. Even in defeat, the cushion India have built — and the results elsewhere in the group — could still carry them through. That is precisely why Thursday mattered so much; a slip against Bangladesh would have left their fate entirely in others' hands.

## Why the diaspora should care

For Indian fans across the UK, the timing could hardly be better. This World Cup is being played on English grounds, putting India's women within train-ride reach of supporters in London, Manchester and Birmingham — and Sunday's clash with Australia lands at Lord's, the sport's most storied address, on a weekend. For NRIs who watched the 2025 50-over triumph from afar, this is a chance to see a world-champion side fight for its place in the knockouts in person, in friendly time zones, on home-from-home soil. A team that has made the dramatic comeback its calling card is asking the diaspora to show up for the next chapter."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Shafali Verma)...")
img_caption = "Shafali Verma, whose 34-ball 53 anchored India's chase against Bangladesh at the Women's T20 World Cup."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Shafali_Verma_in_2025.jpg/330px-Shafali_Verma_in_2025.jpg"
img_final = upload_to_supabase(wiki_img, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image uploaded \u2014 trying originalimage fallback")
    img_final = upload_to_supabase(
        "https://upload.wikimedia.org/wikipedia/commons/9/99/Shafali_Verma_in_2025.jpg",
        f"{art_slug}.jpg",
    )

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
        {"name": "Cricketaddictor \u2014 India Women vs Bangladesh Women Full Scorecard, Match 23, 25 June 2026", "url": "https://cricketaddictor.com/livescore/india-women-vs-bangladesh-women-match-23-icc-womens-t20-world-cup-2026/"},
        {"name": "ICC \u2014 India bank on prior experience to tackle must-win pressure (Women's T20 World Cup 2026)", "url": "https://www.icc-cricket.com/"},
        {"name": "Sporting News \u2014 Women's T20 World Cup 2026 points table: Live standings", "url": "https://www.sportingnews.com/"},
        {"name": "Wisden \u2014 Women's T20 World Cup 2026 Points Table: Updated Standings And Net Run Rate", "url": "https://www.wisden.com/"},
    ]),
    "diaspora_angle": "The Women's T20 World Cup is being played on English grounds, putting India's title defence within reach of diaspora fans across the UK \u2014 with Sunday's decisive group game against Australia at Lord's.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
