#!/usr/bin/env python3
"""
Sports Writer — June 22, 2026 (13:30 UTC slot / videshi-writer-sports)

Article: India's ODI squad for the England tour (3 ODIs, July 14/16/19) was
announced Sun June 21, 2026 by the BCCI. The story is a generational handover:
Shubman Gill now captains India across ALL THREE formats; Jasprit Bumrah
returns to ODIs; Virat Kohli is named subject to a fitness test (June 22);
and Yashasvi Jaiswal is dropped despite an unbeaten 110 — his 2nd century in
his last 3 ODI innings — vs Afghanistan.

KEY FACTS (verified across CricTracker, Cricbuzz, Wisden, ICC, Inshorts):
- 15-man squad. 3 ODIs: 1st 14 Jul (Edgbaston), 2nd 16 Jul (Sophia Gardens,
  Cardiff), 3rd 19 Jul (Lord's). Precedes/follows a 5-match T20I series.
- Captain: Shubman Gill. Vice-captain: Shreyas Iyer.
- Full squad: Shubman Gill (c), Rohit Sharma, Virat Kohli* (subject to
  fitness), Shreyas Iyer (vc), KL Rahul (wk), Ishan Kishan (wk), Washington
  Sundar, Axar Patel, Nitish Kumar Reddy, Kuldeep Yadav, Jasprit Bumrah,
  Prasidh Krishna, Harshit Rana, Arshdeep Singh, Gurnoor Brar.
- Kohli: ruled out of Afghanistan ODIs with a hamstring injury picked up in
  the IPL 2026 final (RCB's title win). Fitness assessment at BCCI Centre of
  Excellence on June 22; clearance makes him available.
- Bumrah: returns to the ODI setup; last ODI appearance was the 2023 World
  Cup final. Was rested for the one-off Test and ODIs vs Afghanistan
  (workload management).
- Jaiswal: replaced Kohli for the Afghanistan series, finished with an
  unbeaten 110 (2nd hundred in last 3 ODI appearances) — and was DROPPED.
- Hardik Pandya: NOT included — quadriceps injury / rehab setback; had back
  spasms in the IPL. No national return yet.
- Harshit Rana: returns after right-knee lateral meniscus surgery that cost
  him the T20 WC and IPL season.
- Axar Patel: back in place of Harsh Dubey. No place for Ravindra Jadeja;
  Washington Sundar continues as the spin-bowling all-rounder.
- Gurnoor Brar: retained after 7 wickets on debut vs Afghanistan.
- Gill: opened his ODI captaincy with a 3-0 sweep of Afghanistan. Already
  Test captain (took over post-Rohit's Test retirement) and now leads across
  all formats. Series is a building block toward the 2027 ODI World Cup
  (South Africa, Namibia, Zimbabwe).

DEDUP: Checked last 4 days of sports. The existing piece "Kohli Is Coming
Back to England — This Time With a White Ball" (June 21, 10:33) was a
KOHLI-FOCUSED column on his white-ball return. THIS piece is a different
angle: the full squad as a generational baton-pass — Gill's all-format
captaincy, Jaiswal's harsh axing, Bumrah's ODI comeback, Hardik's absence —
i.e. the squad story, not the Kohli story. No squad-composition piece exists.

ANGLE: The squad sheet reads like a changing of the guard. The diaspora that
grew up on Tendulkar, then Kohli and Rohit, is watching the team formally
become Gill's — even as the two icons get one more England summer. And the
cruelty of selection (a man dropped after a match-winning century) is the
kind of debate that lights up NRI WhatsApp groups across three time zones.

Hero: Wikipedia REST API portrait of Shubman Gill. Person-led article →
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
print("ARTICLE: India ODI squad for England — the handover to Gill")
print("="*60)

art_slug = "india-odi-squad-england-tour-2026-shubman-gill-captain-all-formats-bumrah-returns-jaiswal-dropped-kohli-fitness-diaspora-nri"
art_headline = "India Picked Its England One-Day Squad, and the Team Sheet Read Like a Changing of the Guard"
art_subheadline = "Shubman Gill now captains India in all three formats, Jasprit Bumrah is back, and Yashasvi Jaiswal was left out despite a match-winning hundred. Virat Kohli is in too — if his hamstring lets him be."

art_body = """When the selectors released India's one-day squad for next month's tour of England on Sunday, the fifteen names told two stories at once. One was about who is coming back. The other, quieter and more consequential, was about who is now in charge.

Shubman Gill will captain the side for the three one-day internationals — at Edgbaston on July 14, Sophia Gardens in Cardiff on July 16, and Lord's on July 19. He already holds the Test captaincy, taken on after Rohit Sharma stepped away from the format, and he opened his white-ball reign with a 3-0 sweep of Afghanistan. With this squad, the handover becomes formal: at 26, Gill now leads India across all three formats. Shreyas Iyer was named his deputy.

## The Returns

The headline additions are two of the biggest names in the Indian game. Jasprit Bumrah is back in the one-day setup for the first time since the 2023 World Cup final, having been rested through the one-off Test and the Afghanistan series under the board's careful management of his workload. His re-entry instantly sharpens an attack that already includes Arshdeep Singh, Prasidh Krishna, the returning Harshit Rana, and the uncapped-turned-impressive Gurnoor Brar, who took seven wickets on debut against Afghanistan and kept his place.

Virat Kohli is named too, but with an asterisk. He missed the Afghanistan one-dayers after pulling up with a hamstring injury during Royal Challengers Bengaluru's victorious IPL 2026 final, and his selection is subject to a fitness clearance — a test he was due to take at the Board's Centre of Excellence on Monday. Pass it, and a 37-year-old who has made England his stage many times over gets one more white-ball summer there. Rohit Sharma, the other half of the era that is slowly closing, was also picked.

## The Casualty

The cruelest line on the sheet belongs to Yashasvi Jaiswal. Drafted in as Kohli's replacement against Afghanistan, he signed off with an unbeaten 110 — his second hundred in his last three one-day innings. It was the kind of form that usually buys a player a long run. Instead, with Kohli and Bumrah returning and the top order crowded, Jaiswal was the man squeezed out. It is the sort of selection call that does not so much settle an argument as start one, and across the diaspora's group chats it will be relitigated for days.

He is not the only notable absentee. Hardik Pandya, India's first-choice seam-bowling all-rounder, was left out again — troubled by back spasms during the IPL and then a setback in rehabilitation, he is yet to win his place back. There is still no return for Ravindra Jadeja in this format, with Washington Sundar continuing as the spin-bowling all-rounder, and Axar Patel comes back in place of Harsh Dubey. Kuldeep Yadav leads the wrist-spin, and KL Rahul and Ishan Kishan are the two wicketkeeping options.

## Why It Travels

For the Indian community abroad, a squad announcement is rarely just a list. This one captures a transition that overseas fans have been tracking with a particular tenderness — the slow passing of the team from the generation of Kohli and Rohit, the players many of them grew up timing their weekends around, to Gill's. That both icons are on the plane softens the moment; that the captaincy and the spine of the side are now built around younger men makes the direction unmistakable.

The series also matters beyond nostalgia. It is an early marker on India's road to the 2027 one-day World Cup, to be co-hosted by South Africa, Namibia, and Zimbabwe — the first full assignment of Gill's all-format leadership against quality opposition in tough conditions. England in July is where Indian touring sides have historically been examined most searchingly, and where reputations, new and old, get tested.

## What's Next

First, the fitness desk has the floor: Kohli's hamstring will decide whether the headline name is on the team bus or watching from afar. Then the cricket. A young captain, a returning spearhead, a dropped centurion with a point to prove from the sidelines, and two legends chasing one more good England summer — India's selectors have, intentionally or not, written a script the diaspora will not be able to look away from."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Shubman Gill, who now captains India across all three formats, will lead the ODI side in England"
img_attribution = "Wikimedia Commons"
img_final = None

wiki_img = fetch_wikipedia_person_image("Shubman Gill")
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
        {"name": "CricTracker \u2014 India announce ODI squad for England tour, Virat Kohli included subject to fitness clearance", "url": "https://www.crictracker.com"},
        {"name": "Cricbuzz \u2014 Jasprit Bumrah, Virat Kohli named in squad for England ODIs; No Hardik Pandya", "url": "https://www.cricbuzz.com"},
        {"name": "Wisden \u2014 India ODI Squad For England Tour: Kohli, Bumrah Return, Jaiswal Dropped Despite Second Ton In Three Matches", "url": "https://www.wisden.com"},
        {"name": "ICC \u2014 Veteran included as India name ODI squad for England tour", "url": "https://www.icc-cricket.com"},
    ]),
    "diaspora_angle": "A squad sheet that captures a generational handover the diaspora has followed with tenderness \u2014 the team passing from Kohli and Rohit to Shubman Gill, who now captains across all formats \u2014 while the dropping of a centurion (Jaiswal) is exactly the kind of selection debate that lights up NRI WhatsApp groups across time zones, all framed against India's build toward the 2027 ODI World Cup.",
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
