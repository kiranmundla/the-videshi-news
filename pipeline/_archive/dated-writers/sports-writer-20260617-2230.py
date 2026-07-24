#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (22:30 UTC run)
Article: India A beat Afghanistan A by 101 runs in Dambulla to storm into the
ODI tri-series final, days after a chaotic Super Over loss to Sri Lanka A.
Fresh, distinct angle (not the senior team, not women's WC, not hockey): India's
A-team production line — Tilak Varma's captaincy, three fifties (Varma 59,
Priyansh Arya 58, Kumar Kushagra 58), Nishant Sindhu's 4/31, and a glimpse of
15-year-old Vaibhav Sooryavanshi — as the shop window for the senior side.
Diaspora angle: NRIs follow the senior XI obsessively; the A-team is where the
next Gill/Jaiswal is forged, and these are the names that will define the team
the diaspora watches over the next decade.
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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  \u2713 Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  \u26a0 Wikipedia error for '{person_name}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
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
            data=compressed,
            timeout=30,
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
print("ARTICLE: India A into tri-series final, 101-run win over Afghanistan A")
print("="*60)

art_slug = "india-a-beat-afghanistan-a-101-runs-dambulla-tri-series-final-tilak-varma-priyansh-arya-kushagra-nishant-sindhu-2026-nri"
art_headline = "Four Days After a Super Over Meltdown, India A Answered With 319 and a 101-Run Rout to Reach the Final"
art_subheadline = "Three fifties — Tilak Varma's 59, plus 58 each from Priyansh Arya and Kumar Kushagra — and Nishant Sindhu's 4/31 carried India A into the tri-series final in Dambulla. It is the same A-team shop window that has been quietly minting India's senior internationals."

art_body = """DAMBULLA \u2014 Four days earlier, India A had walked off the Rangiri Dambulla International Stadium in near-darkness and disbelief, beaten in a Super Over by Sri Lanka A after a chaotic finish that ended with the 15-year-old Vaibhav Sooryavanshi being dragged into a melee. On Wednesday, the same ground gave them a cleaner ending. India A piled up 319 for nine, bowled Afghanistan A out for 218 in 36.5 overs, and won by 101 runs to storm into the final of the 50-over tri-nation series \u2014 a result that lifted Tilak Varma's side to the top of the table and put the chaos of Monday firmly behind them.

The win ended a two-match losing run at exactly the right moment. India A now have four points and the tournament's best net run rate at +0.597, comfortably ahead of Sri Lanka A's +0.494. Afghanistan A, marooned on two points with a net run rate of -1.602, would need a near-impossible thrashing of the hosts on Friday to overhaul India. For all practical purposes, India A are through, and they got there by doing the one thing they had failed to do in their two defeats: convert a strong position into a decisive scoreline.

## Three Fifties, One Message

Asked to bat first on a sluggish pitch, India A were given early impetus by Priyansh Arya, promoted to open in the absence of Prabhsimran Singh. Arya raced to 58 off 42 balls with nine fours and a six, sharing a 75-run stand inside eight overs with Sooryavanshi, who made a scratchy 38 off 28 after surviving a pair of early reprieves. Once Arya fell, captain Tilak Varma took charge with a measured 59 off 75 balls, anchoring a pivotal 104-run partnership with Kumar Kushagra, who struck 58 off 67. Ruturaj Gaikwad chipped in 30, and Vipraj Nigam's brisk 30 off 20 pushed India past 310 \u2014 a total that always looked beyond Afghanistan A on that surface.

## Nishant Sindhu Runs Through the Tail

If the batting set the platform, the bowling made it emphatic. Left-arm spinner Nishant Sindhu was named Player of the Match for figures of 4 for 31 in 6.5 overs, removing Afghanistan A captain Imran Mir early and returning to mop up the tail. Yash Thakur took 2 for 48, and Anukul Roy and Vipraj Nigam broke a threatening fourth-wicket stand between Bahir Shah, who top-scored with a fluent 57 off 52, and Faisal Shinozada, who made 46. From 70 for three inside ten overs, Afghanistan A never built the momentum a chase of 320 demanded, folding with more than 13 overs unused.

## The Production Line Nobody Watches \u2014 Until They Have To

For all the noise around the senior side, the A-team is where India's next decade is being assembled. Tilak Varma is already a fixture in the senior white-ball setup; here he is learning to captain. Gaikwad has captained the full side in T20Is. Arya, Kushagra, Sindhu and the dual-skilled all-rounders Suryansh Shedge and Vipraj Nigam are all on selectors' "targeted lists," the players being groomed to plug gaps before the gaps appear. And then there is Sooryavanshi, the 15-year-old who scored an IPL century this year and is being eased into the grind of representative cricket, scratchy days and all. This is the conveyor belt that produced Shubman Gill and Yashasvi Jaiswal; Wednesday was a reminder that it has not slowed down.

## Why the Diaspora Should Care

Indians abroad follow the senior XI obsessively, but the names on the team sheet a few years from now are being decided on grounds like Dambulla right now. For an NRI parent explaining to a US-born child why a 15-year-old opener matters, or for a fan in London tracking who might replace an ageing star, the A-team is the most reliable crystal ball Indian cricket offers. The depth on display \u2014 three different match-winners with the bat, a spinner who ran through a side, a teenager being handled with care \u2014 is precisely why India has been able to lose senior players to injury and rotation without the results collapsing. India A play their final over the weekend; the bigger story is that almost everyone in this XI is a senior cap waiting to happen."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "India A captain Tilak Varma, who top-scored with 59 as India A reached the tri-series final in Dambulla"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Tilak Varma")
if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    cand2 = fetch_wikipedia_person_image("Ruturaj Gaikwad")
    if cand2:
        img_caption = "India A batter Ruturaj Gaikwad, part of the side that beat Afghanistan A by 101 runs to reach the tri-series final"
        img_final = upload_to_supabase(cand2, f"{art_slug}.jpg")

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
        {"name": "myKhel \u2014 Priyansh Arya, Kumar Kushagra & Tilak Varma star as India A beat Afghanistan A by 101 runs", "url": "https://www.mykhel.com/cricket/"},
        {"name": "IANS \u2014 Batters, Sindhu help India A enter tri-series final after 101-run win", "url": "https://ianslive.in/"},
        {"name": "Cricbuzz \u2014 India A book spot in final with emphatic win over Afghanistan A", "url": "https://www.cricbuzz.com/"},
        {"name": "RevSportz \u2014 India A effectively qualify for final after 101-run win", "url": "https://revsportz.in/"},
        {"name": "CricTracker \u2014 India A suffer Super Over defeat to Sri Lanka A in Dambulla darkness", "url": "https://www.crictracker.com/"},
    ]),
    "diaspora_angle": "NRIs follow India's senior XI obsessively, but the A-team in Dambulla is where the next Gill or Jaiswal is being forged \u2014 the names on this team sheet are the players the diaspora will be watching for India over the next decade.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

print("\n" + "="*60)
print("DONE")
print("="*60)
mark = "\u2713" if art_id else "\u2717"
print(f"Article: {mark} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
