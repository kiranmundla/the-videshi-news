#!/usr/bin/env python3
"""Sports writer for The Videshi — 2026-05-29 evening batch"""

import json, os, re, sys, time, uuid, subprocess
from datetime import datetime, timezone

import requests, urllib.parse

# ── env ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:]
        k, _, v = line.partition("=")
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k.strip(), v)

load_env(os.path.expanduser("~/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.pexels"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── helpers ──────────────────────────────────────────────────────────────
def sb_insert(table, payload):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 201):
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None
    data = r.json()
    return data[0] if isinstance(data, list) else data

def sb_patch(table, match, payload):
    params = "&".join(f"{k}={v}" for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", headers=HEADERS, json=payload, timeout=30)
    if r.status_code not in (200, 204):
        print(f"  ✗ Patch failed ({r.status_code}): {r.text[:300]}")
    return r

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_API_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
                 f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ✗ Image download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return img_url  # fall back to direct link for wiki/pexels
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ✗ Not an image: {content_type}")
            return img_url

        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        up = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}",
            headers=upload_headers,
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return img_url

def validate_image(url):
    """Quick check that URL returns a valid image."""
    if not url:
        return False
    try:
        r = requests.head(url, timeout=10, headers={"User-Agent": "TheVideshi/1.0"}, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        return "image" in ct and cl > 5000
    except:
        return True  # assume OK if HEAD fails (some CDNs block HEAD)


# ── articles ─────────────────────────────────────────────────────────────
articles = []

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 1: GT Storm Into IPL 2026 Final
# ══════════════════════════════════════════════════════════════════════════

article1 = {
    "headline": "Gill and Sudharsan Smashed a Record 167-Run Stand. Gujarat Titans Are in the IPL 2026 Final.",
    "subheadline": "Shubman Gill's blazing 95 off 45 balls and Sai Sudharsan's 58 powered GT past Rajasthan's 214 in Mullanpur. They face RCB on Sunday in Ahmedabad.",
    "slug": "gt-beat-rr-qualifier-2-gill-sudharsan-167-run-record-ipl-2026-final-vs-rcb-20260529",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "sources": json.dumps([
        {"name": "Sportradar", "url": "https://sportradar.com"},
        {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
        {"name": "Yardbarker", "url": "https://www.yardbarker.com"},
        {"name": "Sports Yaari", "url": "https://sportsyaari.com"},
    ]),
    "image_attribution": "Wikimedia Commons",
    "body": """Shubman Gill has been threatening a statement innings in the playoffs all week. On Friday evening in Mullanpur, he delivered one that ended the IPL 2026 season for Rajasthan Royals and booked Gujarat Titans a place in Sunday's final against Royal Challengers Bengaluru in Ahmedabad.

Gujarat chased down 215 with seven wickets in hand and eight balls to spare. The scorecard reads GT 219/3 in 18.4 overs. The story, though, was written in the opening partnership.

## Gill and Sudharsan Rewrote the Playoff Record Books

Gill and Sai Sudharsan put on 167 runs for the first wicket, the highest partnership in IPL playoff history. The previous record — 159 by Michael Hussey and Murali Vijay in the 2011 final — had stood for fifteen years. Remarkably, Gill and Sudharsan also held the fourth spot on that list, having put on 138 against Mumbai Indians in the 2023 Qualifier 2.

Gill was devastating from the first ball. He scored 19 runs off the opening over from Jofra Archer, smashing back-to-back boundaries in the third over to set the tone. His fifty came off just 30 balls; he was on 95 off 45 when Sudharsan was dismissed.

Sudharsan's dismissal was one of the strangest moments of the tournament. The left-hander, playing fluently on 58 off 32 balls with eight fours and a six, suffered a freak hit-wicket when his bat crashed into the stumps during a shot. It was the kind of dismissal that leaves everyone on the ground momentarily confused.

By then, the damage was done. Jos Buttler walked in with 46 needed off 42 balls. There was never any doubt.

## Sooryavanshi Scored 96 in a Losing Cause

For Rajasthan, the evening began badly and improved spectacularly before collapsing again. Yashasvi Jaiswal fell in the first over to Mohammed Siraj for just one run. Dhruv Jurel followed in the second over, caught by Gill off Kagiso Rabada for seven. At 9/2, the tournament looked over.

It was not. Vaibhav Sooryavanshi, the fifteen-year-old who has redefined what is possible in this format, walked out at number three and counterattacked with stunning violence. He and Ravindra Jadeja added 82 runs in a blitz that took Rajasthan to 70/2 at the end of the powerplay.

Jadeja retired hurt at 34 after a physical setback. Captain Riyan Parag contributed a quickfire 11 off six balls before falling to Jason Holder. But Sooryavanshi kept going. His fifty came off 31 balls; he was eventually out for 96, agonisingly close to a hundred that would have crowned the most remarkable playoff campaign by a teenager in IPL history.

Rajasthan finished at 214/6, a total that looked competitive but was swallowed by the Gujarat openers.

## Rabada and Holder Contained the Damage

Kagiso Rabada (1/21 from four overs) and Jason Holder (2 wickets) did their jobs. Siraj struck early. Prasidh Krishna picked up a wicket. But the RR middle-and-lower order — Dasun Shanaka and Jadeja returning to bat — pushed the total past 210, which on most nights would have been enough.

This was not most nights.

## What It Means for Sunday's Final

Gujarat Titans now face a Royal Challengers Bengaluru side that demolished them by 92 runs in Qualifier 1 just three days earlier. In that match, Rajat Patidar's unbeaten 93 off 33 balls powered RCB to 254, and GT's batters crumbled.

The rematch in Ahmedabad is a different proposition. The Narendra Modi Stadium is GT's fortress. Gill has already shown his intent. And the Titans have the bowling depth — Rabada, Siraj, Rashid Khan, Holder — to trouble any lineup.

For NRIs tracking the biggest domestic cricket season in the world, the final between GT and RCB on Sunday promises to be a blockbuster. It is a clash between defending champions Gujarat and an RCB side chasing back-to-back titles — a prospect that would have been unthinkable for most of RCB's history.

## The Toss Controversy

A footnote: the toss itself became a talking point. The coin was flipped twice after match referee Prakash Bhatt said he could not hear Riyan Parag's call. Replays on the broadcast suggested the call was audible. Parag won the retake and elected to bat. In the end, the toss was a footnote to a match that Gill and Sudharsan decided in the first ten overs.

*The IPL 2026 final takes place on Sunday, June 1, at the Narendra Modi Stadium in Ahmedabad. GT face RCB. First ball: 7:30 PM IST.*""",
}
articles.append(article1)

# ══════════════════════════════════════════════════════════════════════════
# ARTICLE 2: Nishesh Basavareddy Stuns Taylor Fritz at French Open
# ══════════════════════════════════════════════════════════════════════════

article2 = {
    "headline": "An Indian-American Wildcard From Andhra Pradesh Roots Just Knocked Out the Seventh Seed at Roland Garros.",
    "subheadline": "Nishesh Basavareddy, whose parents emigrated from Nellore in 1999, beat Taylor Fritz 7-6, 7-6, 6-7, 6-1 for the biggest win of his career at the French Open.",
    "slug": "nishesh-basavareddy-beats-taylor-fritz-french-open-2026-indian-american-nellore-nri-20260529",
    "category": "sports",
    "vertical": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "sources": json.dumps([
        {"name": "Mykhel", "url": "https://www.mykhel.com"},
        {"name": "Sporting News", "url": "https://www.sportingnews.com"},
        {"name": "ATP Tour", "url": "https://www.atptour.com"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Nishesh_Basavareddy"},
    ]),
    "image_attribution": "Wikimedia Commons",
    "body": """On the opening day of the 2026 French Open, a twenty-one-year-old wildcard from Carmel, Indiana walked onto Court Suzanne-Lenglen and beat the seventh seed in four sets. His name is Nishesh Basavareddy. His parents are from Nellore, Andhra Pradesh. And his victory over Taylor Fritz — 7-6(5), 7-6(5), 6-7(9), 6-1 — was the kind of result that makes the Indian diaspora sit up and take notice.

## From Nellore to Newport Beach to Roland Garros

Basavareddy's story is a quintessentially NRI arc. His father, Muralikrishna Basavareddy, and mother, Sai Prasanna, emigrated from Nellore to the United States in 1999. They settled first in the San Francisco Bay Area, then moved to Irvine in Southern California, where Muralikrishna worked at Toyota. When Nishesh was eight, the family relocated again — this time to Carmel, Indiana, a quiet suburb of Indianapolis surrounded by corn and soybean fields.

It is not the obvious place to produce a tennis player who would one day take down a top-ten opponent at Roland Garros. But Carmel has an unlikely tennis pedigree: it is also the hometown of Rajeev Ram, the former doubles world number one, who became a mentor to the young Basavareddy.

"My coach was like, 'I think I have a pretty special one here. He's only eight, but it's incredible what he can do,'" Ram has recalled of their first meeting at a local tennis camp.

## The Match: Composure Under Pressure

Fritz, seeded seventh and ranked among the best hard-court players in the world, was expected to handle a wildcard ranked 148th without serious difficulty. The first two sets told a different story.

Basavareddy won both tiebreaks 7-5, displaying the kind of nerve that is difficult to teach. His groundstrokes — a right-handed game built on a solid two-handed backhand — were deep and well-directed. He converted three of four break points across the match, a remarkable statistic for a player with only one previous main-draw singles win on the ATP Tour.

Fritz fought back to take the third set in a tense tiebreak, 11-9, and for a moment the upset looked like it might slip away. But Basavareddy regrouped and dominated the fourth set 6-1, closing out the biggest win of his career with authority.

It was the first time an American man had beaten a top-ten opponent at Roland Garros since the year 2000. For a player who only turned professional in late 2024, it was a seismic result.

## The Stanford Dropout Who Took a Set Off Djokovic

Basavareddy's path to this moment has been anything but straightforward. He attended Stanford University for two years and was a standout on the Cardinals' tennis team before deciding to turn professional. Knee surgeries in 2016 and 2018 interrupted his junior career. He climbed to number three in the ITF junior rankings and won the boys' doubles title at the 2022 US Open alongside Ozan Baris.

The breakthrough came in late 2024, when he won 28 of 34 Challenger-level matches between September and November. That run earned him a spot at the Next Gen ATP Finals, where he beat Shang Juncheng for his first top-fifty victory.

A few weeks later, he entered the 2025 Australian Open as a wildcard and took a set off his idol, Novak Djokovic, in the first round. His ranking peaked at world number 99 in June 2025 before sliding back. He arrived at Roland Garros ranked 148th, with a wildcard and something to prove.

## What This Means for Indian-Origin Tennis

India's relationship with professional tennis has always been complicated. The country has produced excellent doubles players — Leander Paes, Mahesh Bhupathi, Rohan Bopanna, and Ram himself — but no Indian-born man has threatened the top of the singles rankings in the Open Era.

Basavareddy is American, born and raised. But his heritage matters. For the estimated five million Indian Americans watching from living rooms in Edison, Fremont, Sugar Land, and Naperville, seeing someone with their surname and their roots competing at a Grand Slam is powerful. It is the same energy that surrounds Shrey Parikh winning the Scripps Spelling Bee or Usha Vance standing on a political stage — the quiet thrill of recognition.

"My dad used to play for fun in Irvine, and my brother started playing a little bit then," Basavareddy has said. "I started playing at the local club." From a local club in Orange County to Centre Court in Paris. The distance is vast. The twenty-one-year-old from Nellore roots is only beginning to travel it.

## What's Next

Basavareddy advances to the second round, where he will face a potentially difficult opponent on the clay he is still learning to master. His current ranking makes every win at this level significant. Whether this French Open becomes a deep run or a one-match wonder, the Fritz upset has announced Basavareddy to a global tennis audience.

For the Indian diaspora, that announcement alone is worth celebrating.

*The 2026 French Open continues through June 7 at Roland Garros in Paris.*""",
}
articles.append(article2)


# ── image sourcing & publishing ──────────────────────────────────────────
def source_image_for_article(article, person_names, pexels_query=None, pexels_fallback=None):
    """Try Wikipedia for person images, then Pexels. Upload to Supabase."""
    img_url = None

    # Try Wikipedia for each person
    for name in person_names:
        img_url = fetch_wikipedia_person_image(name)
        if img_url:
            break

    # Fallback to Pexels
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)

    if img_url:
        # Upload to Supabase storage
        ext = "jpg"
        filename = f"{article['slug']}.{ext}"
        final_url = upload_image_to_supabase(img_url, filename)
        article["image_url"] = final_url
    else:
        print(f"  ⚠ No image found for: {article['headline'][:60]}")
        article["image_url"] = None


# Source images
print("\n=== Sourcing images ===")

print("\n[1] GT vs RR — trying Shubman Gill")
source_image_for_article(
    article1,
    ["Shubman Gill"],
    pexels_query="cricket match IPL stadium",
    pexels_fallback="cricket batsman celebration",
)

print("\n[2] Nishesh Basavareddy — trying Wikipedia")
source_image_for_article(
    article2,
    ["Nishesh Basavareddy"],
    pexels_query="tennis Roland Garros clay court",
    pexels_fallback="tennis French Open",
)

# ── publish ──────────────────────────────────────────────────────────────
print("\n=== Publishing articles ===")

for i, art in enumerate(articles, 1):
    print(f"\n[{i}] {art['headline'][:70]}...")

    # Remove None image_url
    if art.get("image_url") is None:
        art.pop("image_url", None)

    result = sb_insert("p2_articles", art)
    if result:
        art_id = result.get("id", "unknown")
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")

        # If we had an image, also update with the article ID-based filename
        if "image_url" in art and art_id != "unknown":
            new_filename = f"{art_id}.jpg"
            new_url = upload_image_to_supabase(art["image_url"], new_filename)
            if new_url != art["image_url"]:
                sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": new_url})
                print(f"  ✓ Image re-uploaded as {new_filename}")
    else:
        print(f"  ✗ FAILED to publish: {art['slug']}")

print("\n=== Sports writer complete ===")
