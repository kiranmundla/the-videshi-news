#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (16:30 UTC slot / videshi-writer-sports)

Article: India open a new T20 era under Shreyas Iyer in the 1st T20I vs Ireland
in Belfast (Fri June 26, Civil Service Cricket Club). Iyer's captaincy debut
after Suryakumar Yadav was sacked; the central selection riddle is whether to
hand 15-year-old Vaibhav Sooryavanshi his international debut at the cost of a
settled, World-Cup-winning top three (Samson, Abhishek, Kishan).

DEDUP CHECK (vs recent ~4 days sports feed, category=sports):
- Feed HAS: SKY sacked as T20I captain + Iyer named (June 22, the announcement);
  Edgbaston 2nd Test preview; Vaibhav safeguarding dressing-room piece; Vaibhav
  11-ball fifty record; Nitish Reddy ruled out / Suryansh Shedge call-up;
  England T20I squad named; pole vault / hammer / athletics; hockey; relay.
- Feed does NOT have: a MATCH-EVE PREVIEW of the 1st T20I vs Ireland — Iyer's
  actual captaincy debut, the playing-XI dilemma over Sooryavanshi, Ireland's
  injury-hit side. The June 22 piece was the squad/captaincy ANNOUNCEMENT, not
  the on-field debut. Distinct, time-pegged event. CLEAR TO WRITE.

Key facts (Yardbarker preview; Cricbuzz preview; Cricketaddictor squad):
- 1st T20I, Ireland vs India, Friday June 26, 2026, Civil Service Cricket Club,
  Belfast. Two-match series (2nd T20I June 28, same venue).
- Shreyas Iyer = new India T20I captain (replacing Suryakumar Yadav), Tilak
  Varma vice-captain. Marks start of a new cycle toward the 2028 T20 World Cup.
- India T20I squad: Shreyas Iyer (C), Tilak Varma (VC), Abhishek Sharma, Sanju
  Samson (WK), Ishan Kishan (WK), Shivam Dube, Axar Patel, Washington Sundar,
  Varun Chakravarthy, Vaibhav Sooryavanshi, Ravi Bishnoi, Harshit Rana,
  Arshdeep Singh, Prince Yadav, Suryansh Shedge (Nitish Kumar Reddy ruled out,
  quad injury). Bumrah/Siraj rested from T20Is.
- Selection riddle: top three Samson, Abhishek, Kishan all made fifties in the
  March T20 World Cup final win over NZ. Fitting opener Sooryavanshi in means
  dropping/shuffling one of them — a harsh move post-title. Samson has elite
  numbers opening (926 runs, 28 inns, 3 hundreds, 4 fifties, SR 181.93) but
  weaker at 3/4/5; No.6 traditionally an all-rounder slot (Dube/Sundar/Axar/
  Shedge), and playing Samson at 6 would leave just five bowlers.
- Heightened interest in Sooryavanshi after IPL run + 29-ball 94 for India A vs
  Sri Lanka A at Dambulla; would be a 15-year-old international debut.
- Ireland: skipper Andrew Balbirnie the batting mainstay; missing Paul
  Stirling/Josh Little/Mark Adair to injury per one report (squads list Lorcan
  Tucker keeping; Harry Tector, Gareth Delany, Curtis Campher provide depth).
  Ireland's barren run in T20s (only a Zimbabwe series win of note in 3 years).

Hero: Wikipedia/Commons photo of Shreyas Iyer. Permanent Wikimedia URL,
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
print("ARTICLE: India open Iyer era vs Ireland — the Sooryavanshi riddle")
print("=" * 60)

art_slug = "india-ireland-1st-t20i-belfast-2026-preview-shreyas-iyer-captaincy-debut-vaibhav-sooryavanshi-selection-dilemma-new-t20-era-diaspora-nri"
art_headline = "A New Captain, and a 15-Year-Old Knocking: India Begin the Iyer Era in Belfast"
art_subheadline = "Shreyas Iyer leads India for the first time in Friday's opening T20I against Ireland, and the toughest call of his debut is whether to break up a World Cup-winning top three to fit teenage sensation Vaibhav Sooryavanshi."

art_body = """When India walk out at the Civil Service Cricket Club in Belfast on Friday, they will do so under a new captain and into a new chapter. Shreyas Iyer takes charge of the T20I side for the first time, the start of a cycle pointed at the 2028 World Cup — and his first assignment comes wrapped in a selection puzzle that has dominated the build-up far more than the opponent has.

That puzzle has a name: Vaibhav Sooryavanshi. The 15-year-old, already a cult figure after a stunning IPL run and a 29-ball 94 for India A against Sri Lanka A in Dambulla, is in the squad and there is heightened public demand to see him debut. But accommodating him is anything but simple, and how Iyer resolves it will tell us a great deal about the team India is trying to become.

## The riddle at the top

India's current top three — Sanju Samson, Abhishek Sharma and Ishan Kishan — is not just settled, it is decorated. All three made fifties in the T20 World Cup final win over New Zealand in March, India's last assignment in the format. Dropping any of them weeks after a title triumph would be a harsh call.

Sooryavanshi is an opener, so fitting him in forces a domino effect. Samson, who has batted at No. 4 and No. 5 before, could in theory move down — but those slots now belong to skipper Iyer and vice-captain Tilak Varma, leaving only No. 6. That position traditionally belongs to an all-rounder, and India have a queue of them in Shivam Dube, Washington Sundar, Axar Patel and uncapped newcomer Suryansh Shedge. Push Samson to No. 6 and India risk taking the field with just five frontline bowlers, a thin look made thinner by the rested Jasprit Bumrah and Mohammed Siraj and the absence of Varun Chakravarthy from the likely XI.

The numbers explain the management's caution. Samson has 926 T20I runs from 28 innings at the top with three hundreds, four fifties and a strike rate of 181.93. At Nos. 3, 4 and 5 his strike rates fall to a far less commanding 121, 129 and 127. Moving a player that destructive away from the role he dominates is not a decision to take lightly, however bright the teenager waiting in the wings.

## A debut weighed against a World Cup win

This is the tension of the Iyer era in miniature: reward continuity, or accelerate the future. India's think tank, working alongside head coach Gautam Gambhir, must balance the pull of a generational talent against the loyalty owed to a group that just won a world title. Whichever way they lean on Friday, the choice sets a tone for the new captaincy.

There is also the matter of managing Sooryavanshi himself. India have already signalled how carefully they intend to handle a minor in a senior dressing room, and there is little appetite to rush him simply to satisfy the noise. A debut, when it comes, will be on India's terms.

## Ireland, and a chance to test the bench

Across the ropes, Ireland arrive in poor white-ball health. Beyond a series win over Zimbabwe last year, the shortest format has offered them little in three seasons. Captain Andrew Balbirnie remains the batting mainstay, with Harry Tector, Gareth Delany and Curtis Campher providing depth, but the hosts are missing several first-choice names to injury. For a full-strength India, the two matches are as much an audition for fringe players — Shedge, Prince Yadav, Harshit Rana — as they are a contest.

## Why the diaspora should care

For Indian fans in Dublin, London, Toronto and beyond, this short series is an accessible, time-zone-friendly window into a team in transition. It is the first look at India under a new captain, the possible international arrival of a 15-year-old whose every innings has gone viral, and a fixture played on diaspora doorsteps in the British Isles rather than half a world away. Belfast may be a modest stage, but the questions being answered on it — who leads, who opens, who gets left behind — are the ones that will shape India's white-ball side for years."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Shreyas Iyer)...")
img_caption = "Shreyas Iyer, who captains India in T20Is for the first time against Ireland in Belfast."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Shreyas_Iyer_snapped_at_the_airport_%28Cropped%29.jpg/330px-Shreyas_Iyer_snapped_at_the_airport_%28Cropped%29.jpg"
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
        {"name": "Yardbarker \u2014 India Vs Ireland Preview, 1st T20I: Sooryavanshi Or Settled Trio? Iyer-Gambhir Face Major Selection Dilemma", "url": "https://www.yardbarker.com/"},
        {"name": "Cricbuzz \u2014 Favourites India out to test bench strength against Ireland", "url": "https://www.cricbuzz.com/"},
        {"name": "Cricketaddictor \u2014 India T20I squad for Ireland, England Tour 2026: Full squad, captain, schedule", "url": "https://cricketaddictor.com/"},
        {"name": "Wikipedia \u2014 Shreyas Iyer", "url": "https://en.wikipedia.org/wiki/Shreyas_Iyer"},
    ]),
    "diaspora_angle": "The two-match series is played on diaspora doorsteps in the British Isles and offers NRIs a first look at India under new T20I captain Shreyas Iyer, plus the possible international debut of 15-year-old viral sensation Vaibhav Sooryavanshi.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print(f"Image: {img_final or '(none)'}")
print("Set to status='review'")
