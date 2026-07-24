#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (01:30 UTC slot / videshi-writer-sports)

Article: India vs England, 1st Test at Headingley, Leeds — DAY TWO.
The feed already carries Day 1 (Gill & Jaiswal centuries, India 359/3 at stumps).
Day 2 is genuinely new and eventful:
- India bowled out for 471 — THREE individual centuries (Yashasvi Jaiswal 101,
  Shubman Gill 147, Rishabh Pant 134) yet from 430/3 they lost their last 7
  wickets for 41. Cricbuzz: the lowest a team has been bowled out in Test
  history while carrying THREE hundreds.
- Rishabh Pant: stylish 134, somersault celebration, sixes off Bashir.
- England replied strongly: Ollie Pope 100* (his second Test century in
  succession), Ben Duckett 62; England 209/3 at stumps, trailing by 262.
- Jasprit Bumrah 3-48 — got Crawley, Duckett, and Root (10th Test dismissal of
  Root); had Brook caught off a no-ball in the last over.
- Ben Stokes 4-66, Josh Tongue 4-86 for England in India's innings.

ANGLE: The post-Kohli/Rohit India is a side that scores in waterfalls and then
forgets to turn the tap off. Three diaspora-beloved batters all reached three
figures, Pant gave the SW19-of-the-north crowd its highlight reel, and yet the
match is alive because of a familiar Indian frailty — the lower-order
collapse — and an English captain's knack for clawing back. Pant is the
emotional centre for the diaspora: the keeper-batter whose comeback from a
near-fatal 2022 car crash makes every six feel like a gift.

DEDUP: Last 30 sports articles checked. Feed has Headingley DAY ONE
(india-england-first-test-headingley-day-one-gill-jaiswal-centuries-359-3...),
plus women's T20 WC, squads, MLC, hockey, Wimbledon, Commonwealth Games.
NO Day 2 piece exists. This is distinct and timely.

Hero: Wikipedia REST API portrait — Rishabh Pant (the day's showman), then
Shubman Gill (captain, top score 147), then Jasprit Bumrah. Person-led →
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
print("ARTICLE: India vs England, Headingley Test — Day Two")
print("="*60)

art_slug = "india-england-first-test-headingley-day-two-pant-134-three-centuries-471-all-out-collapse-pope-100-bumrah-diaspora-nri"
art_headline = "Three Centuries, One Collapse: India Pile Up 471 at Headingley, Then Watch England Punch Straight Back"
art_subheadline = "Yashasvi Jaiswal, Shubman Gill and Rishabh Pant all reached three figures on a sun-soaked Leeds morning \u2014 yet India lost their last seven wickets for 41, and by stumps Ollie Pope's unbeaten hundred had England right back in the contest."

art_body = """For most of two days at Headingley, India looked like a side rediscovering how good it can be. Then, in the space of a single afternoon session, they remembered the oldest lesson in their own history: a batting line-up that can fill a scorecard with hundreds can still find a way to give a Test back.

India were bowled out for 471 on the second day of the first Test against England, a total built on three individual centuries \u2014 Yashasvi Jaiswal's 101, captain Shubman Gill's commanding 147, and Rishabh Pant's stylish 134. According to Cricbuzz, no team in Test history has ever been dismissed for so few while carrying three separate hundreds. The reason is the part that will sting in dressing rooms from Leeds to Edison: from a position of total command at 430 for 3, India lost their last seven wickets for just 41 runs.

## Pant Gives the Crowd Its Morning

The morning, at least, belonged to the diaspora's favourite showman. Resuming overnight alongside Gill, Pant played the kind of innings that has made him the most watchable cricketer of his generation \u2014 paddles, reverse-dabs and outright assaults on England's young off-spinner Shoaib Bashir, who was twice deposited into the stands. His hundred, raised with a swept six and celebrated with a full somersault, was both an act of joy and a statement of intent in the first series of India's post-Rohit, post-Kohli era.

For the millions of NRIs who have followed Pant's road back from a near-fatal car crash in late 2022, every one of those sixes carries a weight that a scorecard cannot show. He fell for 134, trapped lbw shouldering arms to Josh Tongue, but not before he had given a packed Headingley its highlight reel.

## The Familiar Wobble

Gill, meanwhile, was three short of 150 when he miscued a slog-sweep to deep square leg, ending a 209-run fourth-wicket stand with Pant. That dismissal was the first pebble of an avalanche. Karun Nair, recalled to the side, departed for a duck. Shardul Thakur fell at the stroke of lunch to Ben Stokes, who finished with 4 for 66, and Tongue mopped up the tail soon after the interval to end with 4 for 86. A total that had threatened to sail past 500 closed, almost embarrassingly, at 471.

It is the kind of collapse Indian fans know intimately \u2014 the lower-order subsidence on a foreign pitch, the inability to convert dominance into the truly daunting score. On a surface still good for batting, 471 was par at best.

## England Reply in Kind

England, true to the aggressive identity they have worn for four years now, did not blink. Ben Duckett (62) and Pope set off at a gallop, racing to a 122-run stand that belied increasingly bowler-friendly skies. Mohammed Siraj and Prasidh Krishna were carted; only Jasprit Bumrah held his length, and he was magnificent for figures that flattered him little \u2014 3 for 48, including the prized wicket of Joe Root for the tenth time in Test cricket.

Pope, dropped behind the stumps earlier in his innings and reprieved by a grassed chance off Bumrah, went on to his second hundred in successive Tests, an unbeaten 100 that dragged England to 209 for 3 by the close, trailing by 262. Bumrah might have struck a heavier blow in the final over, having Harry Brook caught at midwicket, only for the celebration to die on a no-ball call.

## What's Next

India, despite the day's wobble, retain the upper hand: a 262-run cushion with seven England wickets still to fall. But the match is alive in a way it had no right to be at 430 for 3, and that is the story of this young Indian side under Gill \u2014 thrilling, prolific, and still learning where the brakes are.

Day three at Headingley will test that lead and that temperament. If India's bowlers, led by Bumrah, can prise out Pope and the England middle order early, the visitors will be in sight of a statement win to open the Anderson-Tendulkar Trophy. If Pope and Brook bat on, the most entertaining Test India have played in months could yet slip the other way."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Rishabh Pant, whose stylish 134 was the highlight of India's first innings at Headingley"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Rishabh Pant", "Rishabh Pant, whose stylish 134 was the highlight of India's first innings at Headingley"),
    ("Shubman Gill", "India captain Shubman Gill, who top-scored with 147 at Headingley"),
    ("Jasprit Bumrah", "Jasprit Bumrah, who took 3 for 48 to keep India ahead at Headingley"),
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
        {"name": "Cricbuzz \u2014 England vs India, 1st Test, Leeds: Day 2 report", "url": "https://www.cricbuzz.com/cricket-news/134724/england-vs-india-1st-test-leeds-day-2-report-ollie-pope-ton-leads-englands-strong-reply-cricbuzzcom"},
        {"name": "Wisden \u2014 England vs India, Headingley Test Scorecard", "url": "https://www.wisden.com"},
        {"name": "ESPNcricinfo \u2014 India tour of England 2026", "url": "https://www.espncricinfo.com"},
    ]),
    "diaspora_angle": "The first Test of India's post-Kohli, post-Rohit era is captivating the diaspora: three hometown heroes \u2014 Jaiswal, captain Gill and the inspirational comeback man Rishabh Pant \u2014 all scored hundreds at Headingley, yet a classic lower-order collapse kept England in the game, a drama NRIs across the US, UK and Canada are following ball by ball.",
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
