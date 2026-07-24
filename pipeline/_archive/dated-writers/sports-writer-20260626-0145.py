#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (21:30 PT slot / videshi-writer-sports)

Article: Jyothi Yarraji's sub-13 comeback at the 65th National Inter-State
Senior Athletics Championships in Bhubaneswar — one year after a knee injury
that cost her a season, she runs 12.99s to win the 100m hurdles, with the
Kalinga Stadium meet doubling as the Asian Games qualification window. Built
out with Gulveer Singh's 5000m and Lasha Ilango's triple-jump meet record.

DEDUP CHECK (vs recent ~3-4 days sports feed, category=sports):
- Feed HAS Bhubaneswar championship pieces on Dev Meena (pole vault NR) and
  Anushka Yadav (hammer NR) — BOTH are single-event/single-athlete records.
- Jyothi Yarraji has only ever been NAME-DROPPED in those pieces; she has never
  been the subject. Her 12-month injury comeback + sub-13 run is an untold
  story and a different event (100m hurdles). Gulveer Singh (5000m) and Lasha
  Ilango (triple jump) are also previously uncovered.
- This is framed as the comeback narrative, not a record-chase duplicate.
  CLEAR TO WRITE.

IMAGE: No Wikipedia/Commons photo exists for Jyothi Yarraji OR Gulveer Singh
(verified: REST summary = NO IMAGE; Commons search = no results for either).
Per IMAGE-SOURCING-RULES "no image is better than a wrong image" — use the
actual VENUE: "Aerial view of Kalinga Stadium" (Commons, CC BY 4.0, Government
of Odisha, 1280x720). Honest scene imagery of the stadium hosting the meet,
not a generic stock substitute or a wrong-person photo.

Key facts (RevSportz; The Bridge; AFI; Olympics.com profiles):
- 65th National Inter-State Senior Athletics Championships, Kalinga Stadium,
  Bhubaneswar, June 24-28 2026. Doubles as an Asian Games qualification window.
- Jyothi Yarraji: 12.99s gold in the 100m hurdles. Andhra Pradesh. Asian Games
  silver medallist (Hangzhou 2022, awarded after a protest/lane controversy),
  two-time Asian champion, national record holder (12.78s), first Indian woman
  to run the 100m hurdles at the Olympics (Paris 2024). Suffered a knee/leg
  injury in 2025 that cost her much of a season; this is her comeback run, and
  going back under 13 seconds is the marker she wanted.
- Gulveer Singh: won the 5000m. Army runner from Uttar Pradesh, Asian Games
  bronze medallist; set an outdoor national record 13:03.93 on the US circuit
  earlier in the season. Now the dominant force in Indian men's distance running.
- Lasha Ilango: triple jump gold with a meet record ~13.89m (women's), Tamil Nadu.
- Scale: ~627 athletes from 26 states/units, including Olympians and Arjuna
  awardees, using the meet as the Asian Games qualification trial.
- Dev Meena (5.46m pole vault NR) and Anushka Yadav (67.02m hammer NR, twice)
  also set national records at this same meet — covered separately, mentioned
  here only as context for how loud the championships have been.

DIASPORA ANGLE: For NRIs who follow Neeraj Chopra and the Olympic athletics
story, Yarraji is the next name to know — and a comeback from injury is the
kind of arc the diaspora rallies behind ahead of the Asian Games.
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
print("ARTICLE: Jyothi Yarraji, sub-13 comeback in Bhubaneswar")
print("=" * 60)

art_slug = "jyothi-yarraji-100m-hurdles-12-99-comeback-injury-65th-national-inter-state-athletics-bhubaneswar-2026-gulveer-singh-5000m-lasha-ilango-asian-games-qualify-diaspora-nri"
art_headline = "One Year After the Injury That Cost Her a Season, Jyothi Yarraji Is Back Under 13 Seconds"
art_subheadline = "At the National Inter-State Championships in Bhubaneswar, India's first Olympic 100m hurdler ran 12.99 to win gold \u2014 the number she had been chasing since a knee injury wiped out much of her 2025."

art_body = """The clock read 12.99, and for the first time in a long time Jyothi Yarraji could exhale. A year ago, an injury had taken the thing she does better than any Indian woman in history \u2014 run over ten barriers faster than almost anyone on the continent \u2014 and left her watching from the sidelines. On Wednesday evening at the Kalinga Stadium in Bhubaneswar, she got it back, winning the 100m hurdles at the 65th National Inter-State Senior Athletics Championships and, more importantly to her, dipping back under 13 seconds for the first time since the comeback began.

For an athlete of Yarraji's standing, a national title is almost a formality. The number was the point. Sub-13 is the threshold that separates a good hurdler from a genuinely international one, and it was the marker she had quietly set herself as proof that the leg would hold and the speed had survived the long months of rehabilitation. It held. She got there.

## Why this name matters

Most of the Indian diaspora that has learned to follow track and field did so through one man, Neeraj Chopra, and his javelin. Yarraji is the athlete to learn next. She is from Visakhapatnam in Andhra Pradesh, she holds the national record at 12.78 seconds, and at the Paris Olympics in 2024 she became the first Indian woman ever to line up in the 100m hurdles at a Games. She is a two-time Asian champion and an Asian Games medallist. In an event where India had no presence at all a decade ago, she built one from scratch.

That is what made the past year so cruel. A leg injury in 2025 cost her the bulk of a season at exactly the age when a hurdler is meant to be peaking. Comebacks in sprint hurdling are unforgiving \u2014 the event is a precise, rhythmic thing, and time away erodes the split-second timing between strides and barriers faster than it does raw speed. To come back and run 12.99 is not just a result; it is evidence that the timing returned with the fitness.

## A championships that has not stopped producing

Yarraji's run was the headline act of an evening, but the Bhubaneswar meet has been generous with them all week. The championships, which run from June 24 to 28, are doubling this year as a qualification window for the Asian Games, and roughly 627 athletes from 26 states and units have arrived treating it as a trial rather than a domestic formality. The stakes have shown in the results.

Earlier in the week the teenager Anushka Yadav broke the national hammer-throw record twice inside forty minutes, and the pole vaulter Dev Meena cleared 5.46 metres to take the national record outright by a single centimetre. Both are 18. Both are now names the selectors cannot ignore. A championships that produces two national records from teenagers and a marquee comeback from its biggest star is doing exactly what a national meet is supposed to do.

## The distance man and the jumper

Two other winners deserve their own lines. Gulveer Singh, the Army runner from Uttar Pradesh, won the 5000m to underline a season in which he has become the undisputed leader of Indian men's distance running; earlier this year he set an outdoor national record of 13:03.93 on the American circuit, a time that would have been unthinkable for an Indian a generation ago. And in the women's triple jump, Lasha Ilango of Tamil Nadu took gold with a meet record of close to 13.89 metres, the kind of mark that turns a promising jumper into a qualification contender.

## What's next

The immediate prize is Asian Games selection, and the marks being posted in Bhubaneswar are making the selectors' job both easier and harder \u2014 easier because the standard is high, harder because there is suddenly genuine depth to choose from. For Yarraji, the road runs further than that: a national record to chase back down, a continental title to defend, and the quiet satisfaction of having answered the only question that matters after an injury like hers. She can still do this. The clock said so."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Commons \u2014 Kalinga Stadium venue)...")
img_caption = "The Kalinga Stadium in Bhubaneswar, host of the 65th National Inter-State Senior Athletics Championships, where Jyothi Yarraji ran 12.99 to win the 100m hurdles."
img_attribution = "Government of Odisha, via Wikimedia Commons (CC BY 4.0)"

# Verified: Commons File:Aerial view of Kalinga Stadium.jpg, 1280x720, CC BY 4.0
kalinga_url = "https://upload.wikimedia.org/wikipedia/commons/a/aa/Aerial_view_of_Kalinga_Stadium.jpg"
img_final = upload_to_supabase(kalinga_url, f"{art_slug}.jpg")

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
        {"name": "RevSportz \u2014 National Inter-State Athletics Championships 2026, Bhubaneswar (Yarraji 100m hurdles result, meet scale, Asian Games qualification)", "url": "https://revsportz.in/"},
        {"name": "The Bridge \u2014 Inter-State Athletics Championships day-by-day coverage (Gulveer Singh 5000m, Lasha Ilango triple jump, records)", "url": "https://thebridge.in/"},
        {"name": "Olympics.com \u2014 Jyothi Yarraji profile (national record 12.78s, Paris 2024 first Indian woman in 100m hurdles, Asian Games and Asian Championships medals)", "url": "https://www.olympics.com/en/athletes/jyothi-yarraji"},
        {"name": "Athletics Federation of India \u2014 65th National Inter-State Senior Athletics Championships, Kalinga Stadium, Bhubaneswar", "url": "https://indianathletics.in/"},
    ]),
    "diaspora_angle": "For an Indian diaspora that has learned to follow Olympic track and field through Neeraj Chopra, Jyothi Yarraji is the next name to know \u2014 the first Indian woman to run the 100m hurdles at a Games \u2014 and her comeback from a season-ending injury, capped by a sub-13 run in Bhubaneswar, is exactly the arc NRI sports fans rally behind ahead of the Asian Games.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
