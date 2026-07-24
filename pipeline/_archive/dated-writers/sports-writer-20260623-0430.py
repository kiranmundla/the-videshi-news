#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (04:30 UTC slot / videshi-writer-sports)

Article: Major League Cricket 2026 — MI New York thrash Texas Super Kings by 8
wickets at Grand Prairie (Mon June 22), their first win of the season.

Why it's distinct from the recent feed:
- Recent MLC pieces: Washington Freedom run-fest (Jun 21), SF Unicorns x2,
  Seattle Orcas chase 217 (Jun 20). NO MI New York vs Texas Super Kings piece.
- Today's earlier sports slot already covered the Headingley Test Day Two.
  This is a clean, separate US-based diaspora cricket story.

Key facts (Cricbuzz/TimesOfSports/Sportradar scorecard, June 22, Grand Prairie):
- Texas Super Kings 158 all out in 19.2 ov (Shubham Ranjane 49, Milind Kumar 39;
  Corbin Bosch 4-29, Trent Boult 3-18).
- MI New York 162/2 in 17.4 ov. Won by 8 wickets.
- Monank Patel (USA national-team captain, Indian-American) 46 off 34 opening.
- Nicholas Pooran (capt) 68* off 46; Quinton de Kock 26.
- Player of the Match: Corbin Bosch (4-29).
- MI New York's FIRST win of MLC 2026 after a loss the previous night.

DIASPORA ANGLE: MLC is the league the Indian-American community built — Monank
Patel, the Edison-raised USA captain, anchored the chase; the franchise is the
US arm of the Mumbai Indians. For NRIs in Texas and the tri-state area, this is
hometown cricket on home soil.

Hero: Wikipedia REST API portrait — Monank Patel (the diaspora hook) first,
then Nicholas Pooran, then Trent Boult. Person-led -> Wikipedia first.
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
print("ARTICLE: MLC 2026 — MI New York beat Texas Super Kings by 8 wkts")
print("="*60)

art_slug = "mi-new-york-beat-texas-super-kings-8-wickets-mlc-2026-monank-patel-46-pooran-68-bosch-4-29-grand-prairie-diaspora-nri"
art_headline = "MI New York Found Their Feet in Texas, and an Edison-Raised Captain Led the Way Home"
art_subheadline = "A night after their season opened with a stumble, the Mumbai Indians' American franchise dismantled the Texas Super Kings for 158 and chased it down with eight wickets to spare \u2014 USA captain Monank Patel anchoring, Nicholas Pooran finishing unbeaten on 68."

art_body = """Twenty-four hours can be a long time in a Twenty20 league. On Sunday night, MI New York opened their Major League Cricket campaign looking rusty and second-best. On Monday at Grand Prairie, just outside Dallas, they were a different side altogether \u2014 sharp in the field, ruthless with the ball, and unhurried in the chase as they beat the Texas Super Kings by eight wickets for their first win of the 2026 season.

It was, in the end, a comfortable evening. The Super Kings were bowled out for 158 in 19.2 overs, and MI New York knocked off the runs for the loss of two wickets with 14 balls to spare. But the scoreline flatters neither the discipline of the bowling that set it up nor the calm of the chase that closed it out.

## Bosch and Boult Squeeze the Life Out of Texas

Put in to bat after losing the toss, the Super Kings never built the platform a 20-over total demands. Trent Boult, the New Zealand left-armer, struck twice in the powerplay \u2014 removing Smit Patel and Rilee Rossouw \u2014 to leave the innings reaching for momentum it would not find. Milind Kumar, the India-born batter who has become a fixture of American franchise cricket, made a busy 39, and Shubham Ranjane top-scored with 49, but neither could push on.

The damage was done by Corbin Bosch, named Player of the Match for figures of 4 for 29, and by Boult, who finished with 3 for 18. Between them they accounted for seven wickets and choked the Super Kings' middle order, so that what might have been a 180-plus total folded for 158. "We showed we were quite rusty yesterday," Bosch said afterwards, "so it was nice to put a really good performance in, especially from a bowling perspective."

## Monank Patel Sets the Tone

For The Videshi's readers, the heart of the night was at the top of the MI New York reply. Monank Patel \u2014 the Gujarat-born, New Jersey-raised wicketkeeper-batter who captains the United States national team \u2014 opened the innings and made 46 off 34 balls, the kind of controlled, intent-laden knock that takes the nerves out of a chase before they can settle in.

Patel's story is the league's story in miniature: a young man who moved to Edison, New Jersey, worked his way up through American club cricket, and now leads both his country and one of the marquee MLC franchises. Every time he walks out at Grand Prairie, the stands hold a sizeable contingent of Indian-Americans for whom his rise is a point of genuine pride. His 46 ended only when Hardus Viljoen trapped him lbw, but by then the result was barely in doubt.

## Pooran Finishes It in Style

What Patel started, the captain finished. Nicholas Pooran, the West Indian left-hander, was unbeaten on 68 from 46 balls, peppering the Grand Prairie boundary with six fours and three sixes, with Quinton de Kock chipping in 26 at the other end. By the time Pooran cut and pulled MI New York to the line, the Super Kings' bowlers \u2014 a varied attack including Akeal Hosein and Adam Milne \u2014 had simply run out of answers.

It was the sort of all-round display that the franchise, backed by the Mumbai Indians ownership group, had been built to produce: international names blending with American-qualified players in a league that, three seasons in, is fast becoming a genuine fixture of the US summer.

## What's Next

The win lifts MI New York off the bottom and back into a tightly packed table, with the Super Kings left to regroup after a chastening night at their home venue. For the diaspora that has adopted this competition \u2014 in Texas, in the tri-state area, and in front of streams across the country \u2014 it was an evening that delivered exactly what MLC promised: top-tier T20 cricket, played on American soil, with familiar heroes in the middle. The league rolls on through July, and on this evidence MI New York will be a side nobody wants to face once they hit their stride."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Monank Patel, the USA captain who made 46 to anchor MI New York's chase"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Monank Patel", "Monank Patel, the USA captain who made 46 to anchor MI New York's chase"),
    ("Nicholas Pooran", "Nicholas Pooran, whose unbeaten 68 sealed MI New York's win at Grand Prairie"),
    ("Trent Boult", "Trent Boult, who took 3 for 18 to help bowl out the Texas Super Kings for 158"),
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
        {"name": "Cricbuzz \u2014 Major League Cricket 2026 coverage", "url": "https://www.cricbuzz.com/cricket-series/major-league-cricket-2026"},
        {"name": "Times of Sports \u2014 MLC 2026 TSK vs MINY scorecard", "url": "https://www.timesofsports.com/cricket/major-league-cricket/mlc-2026-tsk-vs-miny-highlights/"},
        {"name": "Sportradar \u2014 MLC 2026 match data", "url": "https://www.sportradar.com"},
    ]),
    "diaspora_angle": "Major League Cricket is the competition the Indian-American community helped build, and MI New York's first win of 2026 was anchored by Monank Patel \u2014 the New Jersey-raised USA captain \u2014 a hometown hero for NRIs following top-tier T20 cricket on American soil.",
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
