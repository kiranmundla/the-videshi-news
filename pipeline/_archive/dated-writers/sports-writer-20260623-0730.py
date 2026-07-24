#!/usr/bin/env python3
"""
Sports Writer — June 23, 2026 (07:30 UTC slot / videshi-writer-sports)

Article: England chase 371 to beat India by five wickets in the first Test at
Headingley — and India become the first team in Test history to LOSE a match
in which it scored five individual hundreds.

Why it's distinct from the recent feed:
- Day 1 piece: Gill/Jaiswal centuries (359/3), "post-Kohli era" framing.
- Day 2 piece: India 471 all out (Pant 134), England reply, Pope 100.
- This is the MATCH RESULT — England's run chase on Day 5 — not yet covered.
- Earlier 04:30 slot today = MLC (MI New York). This is the marquee Test story.

Key facts (theScore / Sky Sports / Cricbuzz Day 5 reports, June 23):
- Target 371; England finished 373-5, won by FIVE wickets.
- Ben Duckett 149 off 170, Player of the Match; 188-run opening stand w/ Crawley.
- Zak Crawley 65; Joe Root 53 not out; Jamie Smith sealed it with a six.
- Prasidh Krishna 2-92 (removed Crawley & Pope back-to-back); Shardul Thakur
  2-51 (Duckett caught at cover, then Brook 0 next ball).
- India scored 835 runs across the match with FIVE individual hundreds —
  Gill 147, Jaiswal 101, Pant 134 & 118 — and still lost. First team in Test
  history (>60,000 first-class matches) to lose despite five tons.
- Pant: only the second wicketkeeper to make hundreds in both innings of a Test.
- India's tail-end collapses: last 7 for 41 (1st inns), last 6 for 31 (2nd).
- Multiple dropped catches; Jaiswal dropped Duckett on 97, equalling the record
  for most drops by an Indian fielder in a Test (4).
- England's joint-highest chases in Tests both vs India under Stokes/McCullum
  (378-3 Edgbaston 2022; 373-5 Headingley now).
- Gill's first Test as captain ends in defeat. 2nd Test July 2 at Edgbaston.

DIASPORA ANGLE: A new India era under captain Shubman Gill opened with a
heartbreak that will sting wherever NRIs gathered to watch — five hundreds and
a defeat. For the large British-Indian crowd at Headingley, it was an
unforgettable Test for all the wrong reasons; for the wider diaspora, a sobering
start to the post-Kohli, post-Rohit transition.

Hero: Wikipedia REST API portrait — Ben Duckett (POM) first, then Shubman Gill
(captaincy-debut story), then Rishabh Pant. Person-led -> Wikipedia first.
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
print("ARTICLE: England chase 371 to beat India at Headingley")
print("="*60)

art_slug = "england-chase-371-beat-india-five-wickets-headingley-first-test-duckett-149-gill-captaincy-debut-defeat-five-centuries-diaspora-nri"
art_headline = "Five Hundreds Were Not Enough: England Chase 371 at Headingley, and India's New Era Opens With a Defeat"
art_subheadline = "Ben Duckett's brilliant 149 carried England to 373 for 5 and a five-wicket win on the final day, leaving India the first team in Test history to lose a match in which it scored five individual centuries \u2014 a chastening start to Shubman Gill's captaincy."

art_body = """There is something about Headingley that keeps delivering Test matches like this one. On a tense, drizzle-interrupted final day in Leeds, England chased down 371 to beat India by five wickets, completing the second-highest successful run chase in their history and sending the new-look tourists to a defeat that will be picked over for a long time to come.

The numbers tell a story almost too strange to credit. Across the five days India scored 835 runs and produced five individual hundreds \u2014 and still lost. No side in the recorded history of the first-class game, a sample of more than 60,000 matches, had ever lost a Test in which its batters made five centuries. India have now managed it, and the manner of it \u2014 promising positions surrendered, catches grassed, an attack that could not close the game out \u2014 made the result feel less like misfortune than self-inflicted.

## Duckett's Masterpiece

The chase belonged to Ben Duckett. Set 371 on a fifth-day pitch, England needed someone to take the game by the scruff, and the left-hander did exactly that with a magnificent 149 off 170 balls. He and Zak Crawley put on 188 for the first wicket, reverse-sweeping the spinners and driving the seamers with a freedom that drained the menace from India's bowling. By the time Duckett fell, England were within sight of the line, and Joe Root \u2014 unbeaten on 53 at his county home ground \u2014 and the debutant Jamie Smith, who sealed it with a six, completed the job. England finished on 373 for 5, and Duckett was the obvious choice as Player of the Match.

It was the kind of chase that has become a signature of the Ben Stokes and Brendon McCullum era. England's two highest successful run chases in men's Tests have now both come against India and both under this regime: 378 for 3 at Edgbaston in 2022, and now 373 for 5 at Headingley.

## India's Costly Afternoon

India did not go quietly. Prasidh Krishna, who finished with 2 for 92, struck twice in quick succession after lunch, having Crawley caught at first slip for 65 and then bowling Ollie Pope for 8. Just as Duckett and Root appeared to have settled matters, Shardul Thakur \u2014 2 for 51 \u2014 had Duckett caught at cover and then dismissed Harry Brook first ball, and for a few overs either side of tea the chase wobbled. But India had given England too much road. Duckett alone was dropped on 97 by Yashasvi Jaiswal, one of a clutch of missed chances; Jaiswal's tally of drops for the match equalled the unwanted record for an Indian fielder in a Test.

The seeds of defeat had been sown earlier, in two collapses that wasted a mountain of runs. Having reached commanding positions in both innings, India lost their last seven first-innings wickets for 41 and their last six second-innings wickets for 31. Rishabh Pant was magnificent, scoring 134 and 118 to become only the second wicketkeeper in history to make hundreds in both innings of a Test; Shubman Gill made 147 and Jaiswal a century of his own. Yet the lower order's repeated failure to wag, and the bowlers' inability to defend 371, undid all of it.

## A Sobering Start to the Gill Era

For India, this was meant to be the dawn of something. With Virat Kohli and Rohit Sharma no longer in the Test side, Shubman Gill walked out at Headingley as captain for the first time, leading a young team into a new cycle. A first-innings 147 announced his batting credentials; the result announced how steep the climb will be. India have now lost seven of their last nine Tests, and the questions about their bowling depth and their slip cordon will only grow louder before the second Test begins on July 2 at Edgbaston.

For the diaspora, the timing cuts deep. A large British-Indian contingent had made the trip to Leeds to witness the first chapter of the post-Kohli era in person, and across living rooms in the United States, Canada and the Gulf, NRIs had set alarms for a Test that promised a fresh beginning. Instead they watched five hundreds dissolve into a defeat \u2014 a reminder that transitions are rarely tidy, and that this England side, on this ground, simply refuses to lose. India will regroup at Edgbaston. They will need to learn quickly."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image (Wikipedia first — person-led article)...")
img_caption = "Ben Duckett, whose 149 powered England's chase of 371 at Headingley"
img_attribution = "Wikimedia Commons"
img_final = None

for person, cap in [
    ("Ben Duckett", "Ben Duckett, whose 149 powered England's chase of 371 at Headingley"),
    ("Shubman Gill", "Shubman Gill, who made 147 but saw his first Test as India captain end in defeat"),
    ("Rishabh Pant", "Rishabh Pant, who made 134 and 118 \u2014 hundreds in both innings \u2014 in a losing cause"),
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
        {"name": "theScore \u2014 England beats India by 5 wickets in 1st Test after historic chase", "url": "https://www.thescore.com/cricket/news"},
        {"name": "Sky Sports \u2014 Ben Duckett hits 149 as England chase 371 at Headingley", "url": "https://www.skysports.com/cricket"},
        {"name": "Cricbuzz \u2014 1st Test, Headingley, Day 5 report", "url": "https://www.cricbuzz.com"},
    ]),
    "diaspora_angle": "A new India era under captain Shubman Gill \u2014 the first Test of the post-Kohli, post-Rohit transition \u2014 opened with a wrenching defeat despite five individual centuries. For the large British-Indian crowd at Headingley and NRIs watching across the US, Canada and the Gulf, it was a sobering, unforgettable start to a new chapter of the team they follow most closely.",
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
