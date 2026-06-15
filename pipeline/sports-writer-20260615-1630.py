#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (16:30 UTC run)
Article: India A's chaotic Super Over loss to Sri Lanka A in Dambulla —
10-run penalty, last-ball run out, Super Over heartbreak, and post-match
altercations that have left their tri-series final hopes hanging by a thread.
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
        r = requests.get(img_url, headers={"User-Agent": UA}, timeout=30)
        content = None
        if r.status_code != 200:
            import subprocess
            tmp = f"/tmp/{filename}"
            subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
            if os.path.exists(tmp) and os.path.getsize(tmp) > 5000:
                content = open(tmp, "rb").read()
            else:
                print(f"  \u2717 Download failed ({r.status_code}) for {img_url[:80]}")
                return None
        else:
            ct = r.headers.get("Content-Type", "")
            if not ct.startswith("image/"):
                print(f"  \u2717 Not an image: {ct}")
                return None
            if len(r.content) < 5000:
                print(f"  \u2717 Image too small: {len(r.content)} bytes")
                return None
            content = r.content

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
print("ARTICLE: India A Super Over loss to Sri Lanka A, Dambulla")
print("="*60)

art_slug = "india-a-super-over-loss-sri-lanka-a-dambulla-tri-series-10-run-penalty-altercation-final-hopes-2026-nri"
art_headline = "A 10-Run Penalty, a Last-Ball Run Out, a Super Over. In Dambulla, India A Imploded Against Sri Lanka A."
art_subheadline = "Tilak Varma's side were docked 10 runs before a ball was bowled, clawed back into a tie, then froze in the Super Over \u2014 a chaotic, tempers-frayed defeat that leaves their tri-series final hopes hanging by a thread."

art_body = """Some cricket matches are lost. This one, India A managed to mislay, mishandle, and finally surrender in a Super Over, all in the space of a single sweltering afternoon in Dambulla. Their second straight defeat in the one-day tri-series \u2014 to a Sri Lanka A side they had beaten only days earlier \u2014 was not just a loss. It was a self-inflicted wound, and it has left Tilak Varma's team needing to win their last group game to stay alive.

The drama began before Sri Lanka A had even faced a legal delivery. India A were handed a 10-run penalty, the hosts effectively starting their chase at 10 for none, after Vipraj Nigam was caught running on the protected middle of the pitch twice despite explicit warnings from the umpires. It is the kind of avoidable, almost amateur lapse that turns a tight contest into an uphill one, and on Monday it proved the difference.

## A Total Rescued, Then Squandered

India A's batting offered little comfort. Bowled out for 265, they were rescued only by a 103-run stand between all-rounders Suryansh Shedge and Vipraj Nigam, who both reached fifties after the top order misfired. Captain Tilak Varma fell for 23, Ruturaj Gaikwad \u2014 the side's most reliable batter through the series \u2014 managed just 37, and the prodigious 15-year-old Vaibhav Sooryavanshi was dismissed for 21 off 14, extending a quiet run since his record-shattering IPL season. Nigam's eventual run out for 51, after a mix-up with Shedge, summed up an innings that never quite settled.

Chasing 266 (effectively 256 with the penalty cushion), Sri Lanka A leaned on a gritty 93 from Sadeera Samarawickrama, who batted through cramps and treatment stoppages to keep his side ahead for most of the chase. India A, as they had in the previous meeting, clawed back at the death. Arshad Khan castled Samarawickrama in the final over, and with two runs needed off the last ball, a run out off a single left the scores level. The match was tied. A Super Over would settle it.

## The Super Over That Got Away

Here the chaos peaked. Sri Lanka A, batting first, plundered 18 \u2014 a total inflated when Arshad Khan bowled a waist-high no-ball off what should have been the final delivery, forcing the batters, who had already left the crease, to be called back. Tilak Varma argued at length with the umpires before play resumed.

Set 19 to win, India A sent in Shedge and Sooryavanshi. The strike fell awkwardly: Shedge took three off the first three balls, leaving the teenager to find 16 off three. Kugathas Mathulan bowled a superb over, choking the boundaries, and Sooryavanshi could manage only six. India A fell short, and the frustration boiled over \u2014 Sooryavanshi was involved in a heated exchange with Sri Lanka A's Vishen Halambage, while Tilak Varma's earlier remonstrations with the officials added to the ill-tempered finish.

## Final Hopes on a Knife's Edge

The defeat \u2014 India A's second in a row after a four-run DLS loss to Afghanistan A \u2014 leaves the table delicately poised. Sri Lanka A sit top, having advanced to the final, while India A must beat Afghanistan A on June 17 to keep their own final hopes alive. For a side stacked with India's most exciting fringe talent \u2014 Sooryavanshi, Gaikwad, Tilak, Prabhsimran Singh \u2014 the campaign has become a lesson in how quickly fine margins and basic discipline can unravel a promising team.

## Why It Matters to the Diaspora

For NRIs who follow Indian cricket as a window into the next generation, the tri-series in Dambulla is a preview of the players who will soon fill the senior side. Several of these names \u2014 Sooryavanshi above all \u2014 are bound for the upcoming tours of Ireland and England, fixtures that diaspora families in Dublin, London, and across North America will turn out for in person. Monday's implosion is a useful corrective to the hype: these are gifted but still-raw cricketers, learning to win the hard, unglamorous moments. The temperament lessons of a chaotic afternoon in Sri Lanka may matter more, in the long run, than the runs and wickets. And for parents in the diaspora watching their own children chase the game, there is something oddly reassuring in seeing even prodigies stumble, argue, and have to come back stronger.
"""

print("\nSourcing image...")
img_url = fetch_wikipedia_person_image("Tilak Varma")
img_caption = "India A captain Tilak Varma, who led the side in the chaotic Super Over defeat in Dambulla"
img_attribution = "Wikimedia Commons"

img_final = None
if img_url:
    img_final = upload_to_supabase(img_url, f"{art_slug}.jpg")

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
        {"name": "Dainik Bhaskar (English)", "url": "https://www.bhaskarenglish.in"},
        {"name": "Khel Now", "url": "https://khelnow.com"},
        {"name": "Mint", "url": "https://www.livemint.com"},
        {"name": "ESPNcricinfo / Wikipedia", "url": "https://en.wikipedia.org/wiki/2026_Sri_Lanka_Tri-Nation_Series"},
    ]),
    "diaspora_angle": "Several of the India A players who imploded in Dambulla \u2014 led by 15-year-old Vaibhav Sooryavanshi \u2014 are bound for the upcoming tours of Ireland and England, fixtures that diaspora families across the UK and North America will attend in person, making this fringe side's growing pains a preview of the senior team NRIs will soon cheer.",
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
