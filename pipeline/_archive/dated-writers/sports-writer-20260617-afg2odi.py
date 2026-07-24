#!/usr/bin/env python3
"""
Sports Writer — June 17, 2026 (India-Afghanistan 2nd ODI match report)
Article: India beat Afghanistan by 15 runs in the 2nd ODI at Lucknow to clinch the
series 2-0 with a match to spare — and notch the country's 500th ODI win. Twin
centuries from Shubman Gill (his 9th ODI ton) and Ishan Kishan (maiden ODI hundred,
also his 1000th ODI run) built a 224-run stand; debutant Prince Yadav got ODI Cap 263.
Distinct from the June 15 PREVIEW piece — this is the actual match report.
Diaspora angle: India's white-ball rebuild under captain Gill is appointment viewing
for NRIs, and a milestone 500th win plus two centuries is exactly the storyline that
travels across the cricket-following diaspora.
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
print("ARTICLE: India beat Afghanistan, 2nd ODI \u2014 500th ODI win")
print("="*60)

art_slug = "gill-kishan-centuries-india-beat-afghanistan-2nd-odi-lucknow-500th-win-series-clinched-2026-nri"
art_headline = "Two Centuries, a 224-Run Stand, and India's 500th ODI Win: Gill and Kishan Sink Afghanistan in Lucknow"
art_subheadline = "Shubman Gill's ninth ODI hundred and Ishan Kishan's maiden century carried India to a 15-run victory at Lucknow, sealing the three-match series 2-0 with a game to spare \u2014 and handing the country a landmark 500th win in one-day internationals."

art_body = """India turned the second one-day international against Afghanistan into a celebration on Wednesday, riding centuries from captain Shubman Gill and Ishan Kishan to a 15-run win at the Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium in Lucknow. The result clinched the three-match series 2-0 with a game still to play \u2014 and, fittingly, marked India's 500th victory in the history of men's one-day internationals.

Afghanistan captain Hashmatullah Shahidi won the toss and chose to bowl, hoping the Lucknow surface might offer something early. It did not. Gill and Kishan made sure of that with a partnership that, more than the scoreline, will be what India remember from this match.

## A 224-Run Stand That Settled the Match

Rohit Sharma set the tone at the top with a brisk 48 off 39 balls before falling, but the innings belonged to the pair who followed. Gill, batting with the calm authority that has come to define his captaincy, brought up his ninth ODI hundred \u2014 a century laced with 12 fours and a couple of towering sixes. At the other end, Kishan produced the defining knock of his white-ball career: a maiden ODI century in his comeback to the side, an innings that also took him past 1,000 runs in the format.

Together they added 224 runs, an alliance that broke Afghanistan's spirit on a flat pitch and pushed India to a total their opponents would ultimately fall short of by 15 runs. For Kishan in particular, returning to the national setup after a turbulent stretch out of favour, the hundred read like vindication \u2014 the kind of innings that resets a career.

## A Moment of Sportsmanship

The afternoon also produced one of those images cricket cherishes. As Gill battled cramps in the closing overs of his innings, it was Afghanistan opener Rahmanullah Gurbaz who stepped in to help the India captain stretch and recover between deliveries \u2014 a quiet act of sportsmanship from an opponent in the thick of a contest. It was the sort of gesture that travels well beyond the boundary, and it drew warm applause from the Lucknow crowd.

## Afghanistan Fight, but Fall Short

Afghanistan, never a side to be dismissed in the 50-over format, did not surrender the chase. They kept India honest deep into the innings, and the margin \u2014 15 runs \u2014 tells of a contest that stayed alive longer than the gulf in resources might suggest. But India's bowlers held their nerve at the death. Arshdeep Singh and Washington Sundar struck at crucial junctures, while Gurnoor Brar and debutant Prince Yadav chipped in to choke the chase.

Prince Yadav's evening carried its own significance: the young quick was handed India ODI Cap No. 263 before play, marking his arrival in the one-day side. Kuldeep Yadav, ever the showman with the ball and occasionally with the bat, added to the entertainment in a match India controlled from the Gill-Kishan stand onward.

## The 500th Win, in Context

India became only the second nation to reach 500 ODI wins, a milestone that stretches back to the format's earliest years and threads through the country's two World Cup triumphs, the Sachin Tendulkar era, the Dhoni years, and now a side being rebuilt in Gill's image. Reaching the mark on home soil, in a series India have dominated, gave the achievement a celebratory frame rather than a nervy one.

With the series already secured, the third and final ODI becomes a chance for India to experiment \u2014 to look at the fringe players knocking on the door and to give the likes of Prince Yadav a longer rope. For Gill, captaining a transitioning side through the post-2025 cycle, a 2-0 result with a century of his own is exactly the kind of statement he would have wanted to make.

## Why It Matters to the Diaspora

For the cricket-following Indian diaspora \u2014 from the high-rises of Jersey City to the suburbs of Toronto, London and Sydney \u2014 India's white-ball rebuild under Gill is appointment viewing. A milestone 500th win, twin centuries from a young captain and a redeemed wicketkeeper-batter, and a touch of old-fashioned sportsmanship make for the kind of evening NRIs forward to family group chats within minutes. It is a reminder that even in a so-called bilateral filler series, Indian cricket rarely fails to produce a story worth carrying across an ocean."""

print(f"\nWord count: ~{len(art_body.split())} words")

print("\nSourcing image...")
img_caption = "Shubman Gill scored his ninth ODI century to lead India past Afghanistan in the second ODI at Lucknow"
img_attribution = "Wikimedia Commons"
img_final = None

cand = fetch_wikipedia_person_image("Shubman Gill")
if cand:
    img_final = upload_to_supabase(cand, f"{art_slug}.jpg")

if not img_final:
    # fallback to Ishan Kishan
    cand2 = fetch_wikipedia_person_image("Ishan Kishan")
    if cand2:
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
        {"name": "BCCI.tv \u2014 Resilient India seal 500th win | 2nd ODI highlights", "url": "https://www.bcci.tv/"},
        {"name": "Sportskeeda \u2014 IND vs AFG 2nd ODI: Gill, Kishan centuries", "url": "https://www.sportskeeda.com/"},
        {"name": "ESPNcricinfo \u2014 India vs Afghanistan 2nd ODI, Lucknow", "url": "https://www.espncricinfo.com/"},
        {"name": "Hindustan Times \u2014 India clinch series 2-0 vs Afghanistan", "url": "https://www.hindustantimes.com/"},
    ]),
    "diaspora_angle": "India's white-ball rebuild under captain Shubman Gill is appointment viewing for the cricket-following Indian diaspora, and a milestone 500th ODI win, twin centuries, and a touch of old-fashioned sportsmanship make for exactly the kind of storyline NRIs forward to family group chats within minutes.",
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
