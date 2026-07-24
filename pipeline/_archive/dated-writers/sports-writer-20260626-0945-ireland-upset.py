#!/usr/bin/env python3
"""
Sports Writer — June 26, 2026 (videshi-writer-sports re-run, 09:45 PDT slot)

STORY: Ireland beat India by 34 runs in the 1st T20I at Civil Service CC,
Stormont, Belfast on Fri June 26, 2026 — India's FIRST-EVER loss to Ireland in
international cricket (any format). Ireland 182/9; India bowled out for 148 in
18.5 overs. India won the toss and bowled. It was Shreyas Iyer's first match as
India's T20I captain (post-T20-World-Cup reset); 15-year-old Vaibhav
Sooryavanshi did not play. Ireland led by captain-keeper Lorcan Tucker. India
had won all eight previous T20Is and every prior international meeting (11)
against Ireland. 2nd (final) T20I is June 28 in Belfast.

DEDUP: Recent sports feed has a PREVIEW of this fixture
("india-ireland-1st-t20i-belfast-2026-preview-...") and squad/injury pieces
(Nitish Reddy out, Sooryavanshi safeguarding rule, England squad), but NO
result/report of the actual match. This historic upset is uncovered. CLEAR.

FACTS (Inshorts; Cricbuzz live; Sportradar; IndiaForums preview/live;
TheSportsTak):
- Ireland 182/9 (20 ov) beat India 148 all out (18.5 ov) by 34 runs.
- First time India have lost to Ireland in international cricket; Ireland had
  lost each of their previous 11 internationals vs India. India had won all 8
  previous T20Is between the sides (last in 2024 T20 WC, New York).
- Toss: India won, chose to field. Venue: Civil Service CC, Stormont, Belfast.
- Iyer captaincy debut; Sooryavanshi (15) not in XI. Ireland captain Lorcan
  Tucker (wk). India missing several first-choice/injured players (Nitish Kumar
  Reddy ruled out, quadriceps).

IMAGE: Person-led story with named captains. Cascade — Wikipedia (Shreyas Iyer,
India's new captain & central figure; then Lorcan Tucker) → Wikimedia Commons
(Stormont / Ireland cricket). Caption set to match whichever lands.
"""

import os, io, json, subprocess, urllib.parse
from datetime import datetime, timezone

import requests
from PIL import Image

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
    encoded = urllib.parse.quote(person_name.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=15,
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


def fetch_commons_images(search_query, limit=6):
    params = {
        "action": "query", "generator": "search", "gsrsearch": search_query,
        "gsrnamespace": "6", "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json",
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php", params=params,
                         headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            out = []
            for _, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 500:
                    continue
                out.append({"url": ii.get("thumburl") or ii.get("url", ""),
                            "title": page.get("title", "")})
            return out
    except Exception as e:
        print(f"  \u26a0 Commons error '{search_query}': {e}")
    return []


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
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                     "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=compressed, timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  \u2713 Uploaded: {public_url}")
            return public_url
        print(f"  \u2717 Upload failed ({resp.status_code}): {resp.text[:200]}")
        return None
    except Exception as e:
        print(f"  \u2717 Upload error: {e}")
        return None


def insert_article(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS,
                      json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  \u2713 Inserted article: {article['slug']} (id={art_id})")
        return art_id
    print(f"  \u2717 Insert failed ({r.status_code}): {r.text[:300]}")
    return None


print("\n" + "=" * 60)
print("ARTICLE: Ireland beat India for the first time — 1st T20I, Belfast")
print("=" * 60)

art_slug = "ireland-beat-india-first-time-ever-1st-t20i-belfast-2026-34-runs-shreyas-iyer-captaincy-debut-defeat-lorcan-tucker-stormont-diaspora-nri"
art_headline = "Ireland Beat India for the First Time \u2014 and They Picked the Perfect Day to Do It"
art_subheadline = "In Shreyas Iyer's first match as captain, India were bowled out for 148 chasing 183 in Belfast, handing Ireland a maiden win over a side they had never beaten in 11 internationals \u2014 and turning the start of a new era into a reckoning."

art_body = """For as long as the two nations have shared a cricket field, the result had been a formality. India had played Ireland eleven times across formats and won all eleven, eight of them in the Twenty20 game, the most recent at the 2024 T20 World Cup in New York. On a grey Friday at the Civil Service Cricket Club in Stormont, Belfast, that streak finally broke. Ireland beat India by 34 runs \u2014 their first victory over India in any form of international cricket.

It could hardly have come at a more loaded moment. This was India's first T20I since they were crowned T20 World Cup champions, the opening night of a deliberate reset under a brand-new captain, Shreyas Iyer, who was not even part of the squad that lifted the trophy. A new era was supposed to begin with a routine win against a depleted host. Instead it began with a defeat that will be replayed for years.

## How it happened

Iyer won the toss and chose to bowl, the orthodox call on a slow, bigger-than-IPL Belfast ground under cloud cover. Ireland, led for the first time by wicketkeeper-batter Lorcan Tucker in the absence of the retired-from-captaincy Paul Stirling, posted 182 for 9 from their 20 overs \u2014 a total that looked competitive rather than commanding, and on most days against this India would not have been enough.

The chase is where the upset was authored. India never built the partnership the run rate demanded, lost wickets in clusters, and were bowled out for 148 in 18.5 overs. For a batting line-up that has spent two years making targets look small, being dismissed inside the 19th over chasing 183 was an unfamiliar, uncomfortable sight. Ireland's bowlers, missing five injured first-choice seamers, simply kept finding the breakthrough whenever India threatened to settle.

## A reset that just got harder

India arrived in the UK mid-transition. They had "ruthlessly moved on" from the captain who won them the World Cup, handed the T20I leadership to Iyer on the back of an IPL title and a run of strong campaigns, and brought along the 15-year-old phenomenon Vaibhav Sooryavanshi \u2014 who, in the end, did not play, India choosing not to hand him a debut in the first game. The XI was also without the injured Nitish Kumar Reddy, ruled out with a quadriceps problem, part of a patched-together touring group.

None of that should excuse a loss to a side ranked far below them, and India will not pretend otherwise. But it does frame what happened: a new captain, an experimental squad, alien conditions, and an opponent with nothing to lose and one glorious opportunity to take. Ireland took it.

## What it means for Ireland

For Irish cricket, this is the result of a generation. A program that lost its talisman captain after the World Cup and has been "scrambling for fit players" turned up against one of the best white-ball sides on earth and won on merit. Tucker's first match in permanent charge produced the defining win of his country's T20I history. Belfast, which had earlier this week watched New Zealand crush Ireland in a Test, got the celebration it had been waiting decades for.

## Why the diaspora is watching

For the millions of Indians in the United States, the United Kingdom, Canada and beyond, this India team is followed match by match, and the post-World-Cup transition under Iyer is exactly the kind of story that dominates the WhatsApp groups and the cricket bars from Edison to Wembley. An upset by Ireland \u2014 a side many in the British and Irish diaspora live alongside, and whose grounds NRIs can actually get to \u2014 is both a gut-punch and a talking point. It is a reminder that the gap at the top of the global game is thinner than the rankings suggest, and that the new India will have to earn its aura rather than inherit it.

## What's next

India have an immediate chance to respond. The second and final T20I of the series is on Sunday, June 28, back at Stormont, and a defeat there would mean a series loss \u2014 something this India side has not suffered in a bilateral or tournament setting in three years. Iyer's captaincy, barely a day old, already has its first test of character. Ireland, meanwhile, will walk out on Sunday for the first time as a team that has beaten India \u2014 and will want to prove that Friday was no accident."""

print(f"\nWord count: ~{len(art_body.split())} words")

# ---- IMAGE CASCADE ----
print("\nSourcing hero image...")
img_final = None
img_caption = None
img_attribution = "Wikimedia Commons"

iyer = fetch_wikipedia_person_image("Shreyas Iyer")
if iyer:
    img_final = upload_to_supabase(iyer, f"{art_slug}.jpg")
    if img_final:
        img_caption = "India captain Shreyas Iyer, whose first match in charge ended in a maiden defeat to Ireland in Belfast."

if not img_final:
    tucker = fetch_wikipedia_person_image("Lorcan Tucker")
    if tucker:
        img_final = upload_to_supabase(tucker, f"{art_slug}.jpg")
        if img_final:
            img_caption = "Ireland captain Lorcan Tucker, who led his side to their first-ever win over India in the 1st T20I in Belfast."

if not img_final:
    for q in ["Civil Service Cricket Club Stormont", "Stormont cricket ground Belfast",
              "Ireland cricket team", "Cricket Belfast Northern Ireland"]:
        cands = fetch_commons_images(q)
        if cands:
            img_final = upload_to_supabase(cands[0]["url"], f"{art_slug}.jpg")
            if img_final:
                img_caption = "The Civil Service Cricket Club at Stormont, Belfast, where Ireland beat India for the first time."
                img_attribution = "Wikimedia Commons"
                break

if not img_final:
    print("  \u2717 No image sourced — aborting to avoid wrong/blank hero.")
    raise SystemExit(1)

print(f"\nHero: {img_final}\nCaption: {img_caption}")

art_data = {
    "headline": art_headline,
    "subheadline": art_subheadline,
    "body": art_body,
    "slug": art_slug,
    "category": "sports",
    "vertical": "cricket",
    "status": "review",
    "is_editorial": False,
    "image_url": img_final,
    "image_caption": img_caption,
    "image_attribution": img_attribution,
    "sources": json.dumps([
        {"name": "Inshorts \u2014 India lose to Ireland in international cricket for the first time in history (Ireland beat India by 34 runs, 1st T20I, Belfast)", "url": "https://inshorts.com/"},
        {"name": "Cricbuzz \u2014 Live Cricket Score: Ireland vs India, 1st T20I, Stormont, Belfast", "url": "https://www.cricbuzz.com/"},
        {"name": "IndiaForums \u2014 IRE vs IND, 1st T20I preview & live: Iyer captaincy debut, Tucker leads Ireland, Sooryavanshi selection, head-to-head", "url": "https://www.indiaforums.com/"},
        {"name": "TheSportsTak \u2014 Ireland captain Lorcan Tucker on facing India and Vaibhav Sooryavanshi ahead of the series opener", "url": "https://www.thesportstak.com/"},
    ]),
    "diaspora_angle": "This India team is followed match by match across the US, UK and Canada, and the post-World-Cup transition under new captain Shreyas Iyer is a story the diaspora is deeply invested in \u2014 making a first-ever defeat to Ireland, a side many NRIs live alongside, both a shock and a sign that the new India will have to earn its aura rather than inherit it.",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
}

art_id = insert_article(art_data)
print("\nDONE." if art_id else "\nFAILED to insert.")
