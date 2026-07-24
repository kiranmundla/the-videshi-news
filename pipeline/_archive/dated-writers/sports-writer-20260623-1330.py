#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (13:30 UTC slot / videshi-writer-sports)

Article: Nitish Kumar Reddy ruled OUT of India's T20I tours of Ireland & England
with a left-quadriceps injury (reported by BCCI on Tuesday, June 23). Mumbai
all-rounder Suryansh Shedge handed a MAIDEN India call-up as replacement after
147 runs in the India A tri-series in Sri Lanka.

Distinct from the recent feed:
- 2026-06-22 feed = SKY sacked as T20I captain, Shreyas Iyer named captain;
  ODI squad for England (Kohli included). This is a NEW, same-day BCCI release:
  Reddy injured OUT + Shedge's first senior call-up. Different event.

Key facts (Cricbuzz / Reuters / ANI-ESPNcricinfo / Sportskeeda, June 23):
- BCCI on Tue June 23 ruled Reddy (23) out of BOTH T20I series (2 vs Ireland,
  5 vs England) after he reported left-quad discomfort following the 3rd ODI
  vs Afghanistan in Chennai on June 20.
- Reddy first felt it bowling in the 1st ODI (Dharamsala), was rested for the
  2nd (Lucknow), returned in Chennai for 6 wicketless overs (42), then flagged
  discomfort. Medical team prescribed rehab at the CoE, Bengaluru (~a month).
- Suryansh Shedge (Mumbai all-rounder, 23) drafted in — maiden India call-up.
  Scored 147 runs in 5 India A tri-series games in Sri Lanka, incl. unbeaten 72
  vs Sri Lanka A; bowls handy off-spin. Played under Shreyas Iyer at Punjab
  Kings in IPL 2026, so already familiar with the new T20I captain.
- Context: India already without Hardik Pandya (leg injury) for the tour, so
  Reddy's absence leaves the side thin on frontline seam-bowling all-rounders.
  Backup names floated: Shivam Dube, Harshit Rana.
- Fixtures: 2 T20Is in Belfast (June 26 & 28) — India's first T20Is since the
  World Cup win — then 5 T20Is in England, with Shreyas Iyer captaining; ODIs
  from July 14 (Birmingham).

DIASPORA ANGLE: The Ireland/England white-ball summer is the most accessible
India tour for UK and Ireland NRIs in years; the all-rounder shuffle — Reddy
out, Pandya out, an uncapped Mumbai name in — reshapes the XI diaspora crowds
will actually see at Belfast and English grounds.

Hero: Wikipedia REST API portrait — Nitish Kumar Reddy. Person-led -> Wikipedia first.
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
print("ARTICLE: Reddy ruled out, Shedge handed maiden India call-up")
print("="*60)

art_slug = "nitish-kumar-reddy-ruled-out-india-t20i-ireland-england-quadriceps-injury-suryansh-shedge-maiden-call-up-shreyas-iyer-belfast-diaspora-nri"
art_headline = "India Lose Another All-Rounder Before England \u2014 and Hand a Mumbai Newcomer His First Cap"
art_subheadline = "Nitish Kumar Reddy has been ruled out of India's T20I tours of Ireland and England with a quadriceps injury, and the selectors have responded by drafting in the uncapped Mumbai all-rounder Suryansh Shedge for his maiden call-up."

art_body = """India's white-ball tour of Ireland and England was supposed to mark a clean reset \u2014 a new T20I captain in Shreyas Iyer, the first matches since the World Cup triumph, a fresh look at the next generation. Instead, the squad has lost another all-rounder before a ball has been bowled. The Board of Control for Cricket in India confirmed on Tuesday that Nitish Kumar Reddy has been ruled out of both T20I series with a left-quadriceps injury, and named the uncapped Mumbai all-rounder Suryansh Shedge as his replacement.

For Reddy, 23, it is a familiar and frustrating story. He first felt the quad while bowling in the opening one-day international against Afghanistan in Dharamsala, was rested for the second match in Lucknow, then returned for the final ODI in Chennai, where he sent down six wicketless overs for 42 runs before reporting discomfort again. "Nitish reported left quadriceps discomfort after the third ODI against Afghanistan on June 20," the BCCI's statement read. "Following a subsequent medical assessment, the BCCI Medical Team has recommended a period of rehabilitation, ruling him out of both T20I series."

## A Body That Keeps Letting Him Down

The injury is the latest in a string of fitness setbacks that have shadowed Reddy's rise. A wrist injury and recurring niggles limited his bowling sharply during IPL 2025, when he managed just five overs across 13 matches, and he was forced out midway through India's Test tour of England last year with a knee problem. His Sunrisers Hyderabad bowling coach had spoken hopefully during IPL 2026 about Reddy increasing both his workload and his pace, which makes the timing especially cruel: the breakdown comes just as he looked to be building momentum. He is expected to spend at least a month rehabilitating at the BCCI's Centre of Excellence in Bengaluru, with an eye on the two-Test tour of Sri Lanka in August.

His absence matters more than a single name suggests. India are already without Hardik Pandya, ruled out of the tour earlier while recovering from a leg injury picked up in a conditioning session after the IPL. Lose Reddy on top of that and the side is suddenly short of frontline seam-bowling all-rounders \u2014 the very balance that lets a captain squeeze a sixth bowling option out of a batting line-up. Names like Shivam Dube and Harshit Rana have been floated as cover, though each offers a more one-dimensional skill set.

## The Newcomer From Mumbai

Into that gap steps Suryansh Shedge, also 23, earning his first India call-up of any kind. The Mumbai all-rounder forced his way into the conversation with a strong showing for India A in the recently concluded tri-series in Sri Lanka, where he made 147 runs in five matches, including an unbeaten 72 against Sri Lanka A that demonstrated his temperament under pressure, and chipped in with his off-spin. He arrives with one useful piece of familiarity already in place: he played under Shreyas Iyer at Punjab Kings during IPL 2026, so the new T20I captain knows exactly what he is getting.

Shedge is the second India A graduate from that same Sri Lanka tri-series to be fast-tracked into the senior set-up, alongside the 15-year-old phenomenon Vaibhav Sooryavanshi, underlining how directly the selectors are now using the A-team pipeline as an audition for international cricket. For a player who has spent years in the grind of Mumbai's domestic system, the leap is a reminder that a single breakout series can change everything.

## Why the Diaspora Is Watching This One

For Indian cricket followers in Britain and Ireland, this tour is the rare one that comes within reach. India play two T20Is in Belfast on June 26 and 28 \u2014 their first matches in the format since lifting the World Cup \u2014 before a five-match series across English grounds, with the ODIs beginning in Birmingham on July 14. Tickets are gettable, the grounds are a train ride away, and the stands will be heavy with the kind of travelling support that turns a neutral venue into a home one.

What those crowds see, though, will be shaped by exactly this churn. With Pandya and Reddy both absent, the all-rounder slots are wide open, and an uncapped Mumbai cricketer could find himself making his India debut in front of a diaspora audience hungry for a first glimpse of the post-World Cup team. The headline is an injury, but the story underneath is opportunity \u2014 the kind that has launched more than one Indian career on English soil."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first \u2014 person-led article)...")
img_caption = "India all-rounder Nitish Kumar Reddy, ruled out of the Ireland and England T20Is"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Nitish Kumar Reddy", "India all-rounder Nitish Kumar Reddy, ruled out of the Ireland and England T20Is with a quadriceps injury"),
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
        {"name": "Cricbuzz \u2014 Nitish Reddy ruled out of Ireland T20Is with quadriceps injury", "url": "https://www.cricbuzz.com"},
        {"name": "Reuters \u2014 Injured Reddy to miss India's T20I series against England, Ireland", "url": "https://www.reuters.com/sports/cricket/"},
        {"name": "ANI / ESPNcricinfo \u2014 Reddy ruled out, Shedge named replacement", "url": "https://www.aninews.in"},
    ]),
    "diaspora_angle": "India's Ireland and England white-ball summer is the most accessible tour for UK and Irish NRIs in years, and the all-rounder reshuffle \u2014 Reddy out, Pandya out, an uncapped Mumbai name in \u2014 will directly shape the XI diaspora crowds see at Belfast and English grounds.",
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
