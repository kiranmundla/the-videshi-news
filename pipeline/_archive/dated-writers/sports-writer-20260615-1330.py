#!/usr/bin/env python3
"""
Sports Writer — June 15, 2026 (13:30 UTC run)
Article:
1. Vaibhav Sooryavanshi's lean India A tri-series form vs. his record IPL 2026,
   ahead of a historic senior India T20 debut on the Ireland/England tour.
"""

import os, sys, json, time, uuid, hashlib, io, re
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

env_pex = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(env_pex):
    for line in open(env_pex):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v.strip().strip('"').strip("'")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── HELPERS ──

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
        if r.status_code != 200:
            # Wikimedia 429 fallback via curl
            import subprocess
            tmp = f"/tmp/{filename}"
            res = subprocess.run(["curl", "-sS", "-A", UA, "-o", tmp, img_url], capture_output=True)
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
        size_kb = len(compressed) / 1024
        print(f"  \U0001f4e6 Compressed to {size_kb:.0f} KB")

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
        headers=HEADERS,
        json=article,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE: Vaibhav Sooryavanshi — IPL hype meets the grind
# ============================================================
print("\n" + "="*60)
print("ARTICLE: Vaibhav Sooryavanshi tri-series form vs IPL record")
print("="*60)

art_slug = "vaibhav-sooryavanshi-india-a-tri-series-lean-form-ipl-orange-cap-senior-india-debut-ireland-england-nri"
art_headline = "He Was the Most Feared Hitter in the IPL. In Dambulla, the 15-Year-Old Is Learning How Hard Cricket Can Be."
art_subheadline = "Vaibhav Sooryavanshi's 21 off 14 against Sri Lanka A continued a quiet run in the India A tri-series — a sobering interlude before the youngest debutant in Indian cricket history walks out for the senior team in Ireland and England."

art_body = """Two months ago, Vaibhav Sooryavanshi was rewriting the record books and reducing some of the world's best bowlers to spectators. In the middle of June, in the heat of Dambulla, he is doing something far more ordinary, and arguably far more useful: he is failing, just a little, and learning how to handle it.

The 15-year-old's recent outings for India A in the ongoing one-day tri-series against Sri Lanka A and Afghanistan A have been a long way from the standards he set during a once-in-a-generation IPL 2026. On Monday in Dambulla, he made 21 off 14 against Sri Lanka A. Across his last three innings he has gathered 79 runs at an average of 26.33 — flashes of the old menace, but no defining knock. For most teenagers, that is a perfectly respectable return. For Sooryavanshi, whose every dismissal is now news, it counts as a slump.

## A Season That Broke the Scale

To understand why a few modest scores make headlines, you have to remember what came before. In IPL 2026, Sooryavanshi finished as the tournament's leading run-scorer, claiming the Orange Cap with 776 runs in 16 innings at a strike rate of 237.31. He scored a century and five fifties, with a highest score of 103 off 37 balls. He hammered 72 sixes in a single season, obliterating Chris Gayle's long-standing record of 59. He became the first batter to score 600-plus runs in a major men's T20 tournament at a 200-plus strike rate.

The numbers were so absurd that the praise turned almost reverent. Pat Cummins, after watching the boy launch his very first delivery for six, called him "my new favourite player." Dale Steyn went further, predicting Sooryavanshi would end his career "bigger than Sachin and Virat put together." Graeme Swann admitted he would not want to bowl at him. For a left-hander who made his first-class debut at 13 and is the youngest player ever to appear in the IPL, the hyperbole has become the soundtrack to his teens.

## The Value of a Quiet Week

Which is precisely why the tri-series matters more than the scorecard suggests. The 50-over format is a different examination from the T20 blitz that made his name — it rewards patience, shot selection, and the discipline to build rather than detonate. India A, led by Tilak Varma, have had a mixed campaign, beating Sri Lanka A by eight runs before losing to Afghanistan A by four runs on DLS, and Sooryavanshi has had to find his rhythm in a setting where the bowling is sharper and the pitches less forgiving than the flat IPL decks.

A lean patch now, against second-string international attacks, is the gentlest possible reminder that the climb does not end with one golden season. The selectors clearly see the bigger picture. Despite the dip, the national selection committee has named Sooryavanshi in India's senior T20I squads for the upcoming tours of Ireland and England, and in the 15-member squad for the 2026 Asian Games. Barring a surprise, he is on course to debut for India at just 15 — the youngest in the country's history.

## Why It Matters to the Diaspora

For the Indian diaspora, Sooryavanshi is more than a prodigy; he is a story that travels. His father, a farmer from Samastipur in Bihar, reportedly sold part of his land and uprooted the family's routine to fund his son's cricket. It is the kind of sacrifice narrative that resonates deeply in NRI households, where the memory of a parent betting everything on a child's talent is rarely far from the surface. When Sooryavanshi walks out in Dublin or Chester-le-Street this summer, Indian families in Edison, Southall, and Brampton will be watching a teenager carry not just a bat but a whole community's sense of what is possible.

There is also a tenderness in this moment that the diaspora, perhaps better than anyone, understands. A 15-year-old is being asked to perform like a finished product while he is still, by every measure, a child — one who recently posted an emotional Instagram message celebrating his 10-year-old brother's first century at their local academy. Steyn, amid the praise, issued a warning to the BCCI: manage him carefully, "there's a risk you could lose him along the way if he isn't handled properly."

The runs will come; talent this rare does not stay quiet for long. But the most reassuring thing about Sooryavanshi's week in Dambulla may be that, for once, the cricket has been hard. Learning to grind through an ordinary patch is the one lesson the IPL never had the chance to teach him. He will be the better player for it when the senior cap finally arrives.
"""

# Image: Wikipedia for the player
print("\nSourcing image...")
img_url = fetch_wikipedia_person_image("Vaibhav Sooryavanshi")
img_caption = "India A and Rajasthan Royals batter Vaibhav Sooryavanshi"
if not img_url:
    img_url = fetch_wikipedia_person_image("Vaibhav Suryavanshi")

img_final = None
img_attribution = "Wikimedia Commons"
if img_url:
    img_final = upload_to_supabase(img_url, f"{art_slug}.jpg")

if not img_final:
    print("  \u26a0 No image found — inserting without image")

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
        {"name": "RevSportz", "url": "https://revsportz.in"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "CricketAddictor", "url": "https://cricketaddictor.com"},
        {"name": "CricTracker", "url": "https://www.crictracker.com"},
    ]),
    "diaspora_angle": "Vaibhav Sooryavanshi's rise from a Bihar farmer's son to the youngest player set to debut for India embodies the sacrifice-and-aspiration story that resonates deeply with NRI families, who will follow his summer tour of Ireland and England as a symbol of what their own children might achieve.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)

# ── SUMMARY ──
print("\n" + "="*60)
print("DONE")
print("="*60)
print(f"Article: {'\u2713' if art_id else '\u2717'} {art_slug}")
print(f"Word count: ~{len(art_body.split())} words")
print("Set to status='review'")
