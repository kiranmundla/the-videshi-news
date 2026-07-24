#!/usr/bin/env python3
"""
Sports Writer — June 25, 2026 (07:30 UTC slot / videshi-writer-sports)

Article: Edgbaston preview — India go to Birmingham 0-1 down for the second
Test (July 2-6), carrying the recurring "Bumrah question" (he is contracted to
play only three of five Tests; a week's gap but Lord's looming) and the weight
of a venue at which India have NEVER won in eight attempts. Pitch report: green
top, seam-friendly day one, spin only late. Story is a forward-looking preview /
analysis, distinct from the feed's Headingley result piece.

DEDUP CHECK (vs recent ~3 days sports feed, category=sports):
- Feed HAS: Headingley 1st Test RESULT (England chase 371, India lose); India's
  ODI squad; England's T20I squad; Suryakumar sacking; Sooryavanshi
  safeguarding + fastest List-A fifty; Nitish Reddy injury; Pant-Kuldeep IPL
  trade; women's T20 WC qualification scenarios; Wimbledon; athletics.
- Feed does NOT have: an EDGBASTON 2ND TEST PREVIEW — the Bumrah selection
  call, India's winless Edgbaston record (0 from 8), the green pitch, and what
  India must change to level the series. This is a distinct forward-looking
  analysis piece. CLEAR TO WRITE.

Key facts (CricTracker pitch/weather report; ICC; PTI via LatestLY; Cricbuzz;
Mint; Sky Sports via CricTracker):
- 2nd Test at Edgbaston, Birmingham, July 2-6, 2026. India trail 0-1 after the
  Headingley defeat (England chased 371).
- India have played 8 Tests at Edgbaston and won NONE (seven losses, one draw);
  England's overall Edgbaston record is excellent (~30 wins from 56).
- Edgbaston pitch: ~11mm grass two days out, seam and swing on day one under
  overcast skies; flattens days 2-3; spinners average 40+ here — least
  spin-friendly English venue this decade; teams bowling first historically
  favoured (23 wins of 56 by side bowling first).
- Bumrah question: management has stated he will play only THREE of the five
  Tests to manage a back that cost him ~3 months after the 2025 Sydney injury.
  He bowled 44.4 overs and took a first-innings five-for at Headingley. With a
  full week's gap but Lord's (3rd Test) offering more for him, selectors (Ajit
  Agarkar / Gautam Gambhir / Shubman Gill) face a tough call with the series
  alive — likely assessed a day before the Test.
- Pundits split: Stuart Broad and Irfan Pathan say resting your best bowler at
  0-1 down is hard to justify; "if you are selected, you cannot pick and choose
  which match to play" (Pathan). MSK Prasad: "He should ideally play when the
  series is alive, but the management knows best."
- Other likely changes debated: Kuldeep Yadav's wrist-spin vs lower-order
  batting depth (Washington Sundar) — a recurring selection tension.
- Captain Shubman Gill leads in the post-Rohit/Kohli Test era; this is an early
  test of his leadership with the series on the line.
- UK & Ireland broadcast: Sky Sports / TNT Sports; India on Star Sports /
  JioHotstar.

Hero: Wikipedia/Commons photo of Jasprit Bumrah (the central figure of the
selection debate). Permanent Wikimedia URL, downloaded + re-uploaded to Supabase.
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
print("ARTICLE: Edgbaston 2nd Test preview — the Bumrah question")
print("=" * 60)

art_slug = "india-england-2nd-test-edgbaston-2026-preview-bumrah-question-workload-winless-record-shubman-gill-0-1-down-diaspora-nri"
art_headline = "India Have Never Won at Edgbaston. Now They Must \u2014 and Decide Whether to Risk Bumrah to Do It"
art_subheadline = "Trailing England 0-1, Shubman Gill's young side arrives in Birmingham for the second Test on July 2 facing a green pitch, a venue that has beaten India eight times out of eight, and the recurring question of whether to spend their best bowler now or save him for Lord's."

art_body = """India have toured England for generations, won famous Tests at Lord's and The Oval, and built whole legends at Headingley. But there is one English ground that has never yielded: Edgbaston. In eight Tests in Birmingham, India have lost seven and drawn one. When Shubman Gill's side walks out there on July 2, already a match down in this five-Test series, history and arithmetic will both be working against them.

The series opener at Headingley got away from India in the cruellest fashion \u2014 a commanding position surrendered as England chased down 371 on the final day. For a team rebuilding its Test identity after the departures that ended the Rohit Sharma and Virat Kohli era, a 0-2 hole would be close to fatal. Level the series in Birmingham and the tour is alive; lose, and the remaining three Tests become an exercise in damage control.

## The Bumrah question, again

Every India tour of England now comes with the same recurring headline, and this one has arrived early. Jasprit Bumrah, the spearhead who took a first-innings five-wicket haul and sent down nearly 45 overs at Headingley, is contracted to play only three of the five Tests on this tour \u2014 a plan agreed before the series to protect a back that kept him out for almost three months after he broke down in Sydney in early 2025.

The maths is unforgiving. If Bumrah plays Edgbaston, the management must then ration his last two appearances across Lord's, Old Trafford and The Oval. There is a full week between the first and second Tests \u2014 ample recovery for a fast bowler \u2014 but Lord's, with its slope and movement through the air, is the venue where Bumrah is most lethal, and the temptation to hold him back is real.

Not everyone agrees with the caution. "A week is a very good time off for a fast bowler," former England seamer Stuart Broad said. "[Resting him] does surprise me." India's Irfan Pathan was blunter: "If you are selected in the Indian team, you cannot pick and choose which match to play to manage your workload. There is no other bowler like him." Former chief selector MSK Prasad split the difference: "He should ideally play when the series is alive, but the management knows best." The final call is expected to rest with chief selector Ajit Agarkar, head coach Gautam Gambhir and Gill, likely after assessing Bumrah a day out.

## A pitch that rewards seam, not spin

The conditions will shape the team sheet as much as the Bumrah debate. Reports two days out described an Edgbaston surface carrying around 11mm of grass over a dry base \u2014 a classic recipe for seam and swing on day one, especially under the overcast skies Birmingham so often serves up. Historically the team bowling first has had the edge here.

That tilts the balance toward pace. It also reopens the question of Kuldeep Yadav: India's wrist-spinner offers a genuine wicket-taking threat, yet Edgbaston has been the least spin-friendly Test venue in England this decade, with spinners averaging over 40 per wicket. The management's recurring instinct \u2014 to deepen the lower-order batting with an all-rounder such as Washington Sundar rather than play a frontline spinner \u2014 will be tested against the desperate need to take twenty wickets and finally break the Edgbaston curse.

## A young captain's defining week

Beyond the personnel, this is an early referendum on Gill's captaincy. Leading a side shorn of its modern greats, he must marshal a bowling attack whose best member may not be available, on a ground that has never been kind, while a defeat away. How he balances the conservative long game \u2014 protecting Bumrah for the matches the data says suit him \u2014 against the immediate imperative of saving the series will say a great deal about the kind of captain he intends to be.

## Why the diaspora should care

For Indian families across Britain, Edgbaston is the closest thing to a home Test, and Birmingham's enormous South Asian community turns the ground into a sea of blue every time India visit. This is a rare chance for diaspora fans to watch Gill's new-look side in person \u2014 and to witness whether India can finally win at the one English venue that has always defeated them. With the series on the line and the Bumrah call hanging over everything, the second Test from July 2 \u2014 live on Sky Sports and TNT Sports in the UK and Ireland, and on Star Sports and JioHotstar in India \u2014 may be the day this young team either steadies itself or starts to slip."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing hero image (Wikipedia/Commons \u2014 Jasprit Bumrah)...")
img_caption = "India pace spearhead Jasprit Bumrah, whose availability for the Edgbaston Test is the central selection question of the tour."
img_attribution = "Wikimedia Commons"

wiki_img = "https://upload.wikimedia.org/wikipedia/commons/0/02/Jasprit_Bumrah_in_PMO_New_Delhi.jpg"
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
        {"name": "CricTracker \u2014 England vs India 2nd Test: Edgbaston weather forecast and pitch report", "url": "https://www.crictracker.com/"},
        {"name": "LatestLY/PTI \u2014 0-1 Down, India Face the Bumrah Question Ahead of Edgbaston Test", "url": "https://www.latestly.com/"},
        {"name": "ICC \u2014 India make Bumrah call among other changes for Edgbaston", "url": "https://www.icc-cricket.com/"},
        {"name": "Cricbuzz \u2014 Ten Doeschate on managing Bumrah's workload", "url": "https://www.cricbuzz.com/"},
    ]),
    "diaspora_angle": "Edgbaston sits in the heart of Britain's largest South Asian community, making the second Test the closest thing to a home game for UK-based Indian fans \u2014 a rare in-person chance to watch Shubman Gill's new-look side try to level the series and finally win at the one English ground that has always beaten India.",
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
