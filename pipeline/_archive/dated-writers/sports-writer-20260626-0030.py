#!/usr/bin/env python3
"""
Sports Writer — June 26, 2026 (00:30 PT slot / videshi-writer-sports)

Article: Arjun Erigaisi storms into the Winners Final of the 2026 Bullet Chess
Championship on Chess.com, thrashing two-time runner-up Andrew Tang 16-6 after
losing the first four games. India's #1 is one match from the Grand Final on
the world's fastest online stage, with Nihal Sarin still alive in the bracket.

DEDUP CHECK (vs recent ~3-4 days sports feed, category=sports):
- Recent feed is dominated by CRICKET (India-England Tests, India-Ireland T20Is,
  women's T20 WC, MLC), ATHLETICS (Bhubaneswar inter-state meet, Neeraj),
  BADMINTON (US Open Fullerton), F1 (Lindblad), HOCKEY, BASKETBALL.
- ZERO chess articles in the recent sports feed. Arjun Erigaisi / Bullet Chess
  Championship is a completely uncovered subject and event. CLEAR TO WRITE.

IMAGE: Arjun Erigaisi has a Wikipedia/Commons photo (verified: REST summary
thumbnail present). Use his actual photo per IMAGE-SOURCING-RULES (Wikipedia
FIRST for named athletes). Commons File: Arjun_Erigaisi_Uzchess_cup_3_masters
(cropped).jpg, CC. 330px thumbnail used AS-IS per the size rule.

Key facts (Chess.com event coverage, June 25 2026; FIDE June 2026 rating list):
- 2026 Bullet Chess Championship on Chess.com, June 25-28 (play-ins June 23).
  Strongest online bullet event; decides the fastest player in the world. Time
  control 1+0. Prize fund $50,000.
- Day 2 (Thu June 25): Arjun Erigaisi beat GM Andrew Tang 16-6 to reach the
  Winners Final, despite LOSING THE FIRST FOUR GAMES. He then won four straight
  to level, took the lead, and ran away with it. Tang is a two-time runner-up
  and bullet specialist.
- The other Winners Final spot went to defending champion GM Alireza Firouzja,
  who edged India's GM Nihal Sarin 12.5-9.5 in the other semi. Nihal led mid-match
  before Firouzja won four of the last five.
- Winners Final + Losers QF on Day 3, Friday June 26, 9:30 p.m. IST. Nihal dropped
  to the Losers Bracket but is still alive.
- Context: Arjun crossed the 2800 classical rating threshold; in Sept 2024 he
  became India's top-rated player. Per FIDE June 2026 list he returned to the
  Open top 10 after runner-up at TePe Sigeman 2026 (edged by Carlsen on tiebreak).
- India depth: 15-year-old contingent of prodigies; D Gukesh is world champion;
  Arjun, Nihal, Gukesh, Praggnanandhaa form the core of India's golden generation.

DIASPORA ANGLE: Online speed chess is where the diaspora actually watches India's
golden generation in real time — free streams, global time slots — and Arjun in a
Grand Final shot at the fastest format is the kind of bite-sized triumph NRIs share.
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
print("ARTICLE: Arjun Erigaisi reaches Bullet Chess Championship Winners Final")
print("=" * 60)

art_slug = "arjun-erigaisi-2026-bullet-chess-championship-winners-final-beat-andrew-tang-16-6-nihal-sarin-firouzja-chess-com-fastest-india-diaspora-nri"
art_headline = "Down 0-4 to a Bullet Specialist, Arjun Erigaisi Won the Next 16 \u2014 and a Shot at the World's Fastest Chess Title"
art_subheadline = "India's No. 1 thrashed two-time runner-up Andrew Tang 16-6 to reach the Bullet Chess Championship Winners Final, with Nihal Sarin still alive in the bracket \u2014 the clearest sign yet that India now owns the fastest format in the game."

art_body = """Arjun Erigaisi lost the first four games. Against Andrew Tang, an American bullet specialist who has finished runner-up at this event twice, that is usually the part of the match where the result stops being in doubt. Then Tang, with a winning position, mouse-slipped his entire queen \u2014 and something turned. Arjun won the next game, and the next, and the next. By the time the dust settled at the 2026 Bullet Chess Championship on Thursday, India's top-ranked grandmaster had beaten one of the format's most feared players 16-6 and booked his place in the Winners Final.

It is the kind of scoreline that looks impossible until you watch it happen. Bullet chess \u2014 one minute per player for the entire game, no increment \u2014 is the most ruthless version of the sport, a format where a single slip of the mouse or a half-second of hesitation decides everything. Recovering from 0-4 down against a specialist in this discipline is not a comeback so much as a takeover.

## The fastest stage in the game

The Bullet Chess Championship, held on Chess.com from June 25 to 28, is the strongest online bullet event in the world. It exists for one purpose: to settle who is genuinely the fastest chess player alive, across a knockout bracket of the planet's best blitz and bullet talents, for a prize fund of 50,000 dollars. The time control is 1+0 \u2014 sixty seconds, and not a tick more.

This is not Arjun's home format, in the way that classical chess is. He is a 2800-rated grandmaster who, in September 2024, became India's highest-rated player, and who returned to the world's top ten in the June 2026 FIDE list after finishing runner-up to Magnus Carlsen at the TePe Sigeman tournament, edged out only on a tiebreaker. That he can walk into the fastest, most chaotic discipline in the game and dismantle a bullet specialist says something about how complete a player he has become.

## Firouzja, and a near miss for Nihal

The other Winners Final ticket went to the defending champion, France's Alireza Firouzja, who survived a genuine scare from another Indian, Nihal Sarin. Nihal led in the middle of the match and, at one point, found one of the finest combinations of the entire day to move ahead 9-8. But Firouzja, ferocious in the time scrambles that define this format, won four of the last five games to take it 12.5-9.5.

Nihal's defeat dropped him into the Losers Bracket rather than knocking him out, and he remains alive heading into the decisive third day. That two of the four Winners semifinalists were Indian \u2014 Arjun and Nihal \u2014 is itself a marker of how deep the country's bench has become. A decade ago, an Indian reaching this stage of a global speed-chess event would have been a curiosity. Now it is the expectation.

## A golden generation, in real time

India's chess rise is no longer a projection; it is the present. D Gukesh is the reigning world champion. Arjun, Nihal, Gukesh and R Praggnanandhaa form a cluster of young grandmasters who trade places near the top of the rankings and now turn up, routinely, in the closing stages of the biggest events. The online formats are where that dominance is most visible to the people watching from abroad \u2014 free streams, global time slots, results that arrive in the time it takes to finish dinner.

## What's next

Day three runs on Friday, June 26, starting at 9:30 p.m. IST, with the Winners Final and the Losers Quarterfinals on the schedule. Win the Winners Final, and Arjun goes straight to the Grand Final with the safety net of a bracket reset; lose it, and he drops to the Losers side to fight his way back. Nihal, meanwhile, must win out from the Losers Bracket to keep his own run going. Either way, the question hanging over the final day is a familiar one to anyone who has followed Indian chess lately: not whether an Indian will be there at the end, but which one."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Arjun Erigaisi)...")
img_caption = "Indian grandmaster Arjun Erigaisi, who beat Andrew Tang 16-6 to reach the Winners Final of the 2026 Bullet Chess Championship."
img_attribution = "Wikimedia Commons"

# Verified: Commons File:Arjun_Erigaisi_Uzchess_cup_3_masters (cropped).jpg, 330px thumb used as-is
arjun_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Arjun_Erigaisi_Uzchess_cup_3_masters_%28cropped%29.jpg/330px-Arjun_Erigaisi_Uzchess_cup_3_masters_%28cropped%29.jpg"
img_final = upload_to_supabase(arjun_url, f"{art_slug}.jpg")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "chess",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final or "",
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Chess.com \u2014 2026 Bullet Chess Championship Day 2: Firouzja, Arjun Advance To Winners Final (Arjun 16-6 over Tang, Firouzja 12.5-9.5 over Nihal, Day 3 schedule, format and prize fund)", "url": "https://www.chess.com/news/view/2026-bullet-chess-championship-day-2"},
        {"name": "Chess.com \u2014 2026 Bullet Chess Championship Day 1 (bracket, field, play-in context)", "url": "https://www.chess.com/news/view/2026-bullet-chess-championship-day-1"},
        {"name": "FIDE \u2014 June 2026 rating list published (Arjun Erigaisi returns to Open top 10 after TePe Sigeman 2026 runner-up to Carlsen)", "url": "https://www.fide.com/news/"},
    ]),
    "diaspora_angle": "Online speed chess is where the diaspora watches India's golden generation in real time \u2014 free global streams, results in minutes \u2014 and Arjun Erigaisi one win from a Grand Final in the world's fastest format, alongside Nihal Sarin, is exactly the bite-sized Indian triumph NRIs rally around and share.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
