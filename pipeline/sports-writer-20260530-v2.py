#!/usr/bin/env python3
"""Sports writer for The Videshi – 2026-05-30 batch (fixed)"""

import json, os, sys, time, uuid, re, urllib.parse
import requests

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    key, val = line.split('=', 1)
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_wikipedia_person_image(person_name):
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
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
    import subprocess
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            cmd = [
                'curl', '-sS',
                f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape',
                '-H', f'Authorization: {PEXELS_KEY}'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                alt = (photo.get('alt') or '').lower()
                bad_alts = ['aerial', 'satellite', 'map', 'flag', 'icon', 'logo']
                if any(b in alt for b in bad_alts):
                    continue
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return image_url if 'wikimedia' in image_url or 'pexels' in image_url else None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            return image_url if 'wikimedia' in image_url or 'pexels' in image_url else None
        
        if len(r.content) < 5000:
            return image_url if 'wikimedia' in image_url or 'pexels' in image_url else None
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true"
        }
        ur = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if ur.status_code in [200, 201]:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {ur.status_code}, using direct URL")
            if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
                return image_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in image_url or 'images.pexels.com' in image_url:
            return image_url
        return None

def validate_image_url(url):
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            if cl == 0 or cl > 5000:
                return True
        return False
    except:
        return False

def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    if r.status_code in [200, 201]:
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:400]}")
        return None

def sb_patch(table, filters, data):
    params = "&".join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers=HEADERS,
        json=data,
        timeout=30
    )
    return r.status_code in [200, 204]

# Create topics first
def create_topic(title, category="sports"):
    topic = {
        "canonical_title": title,
        "category": category,
        "vertical": "sport",
        "urgency": "daily",
        "score_diaspora": 7,
        "score_significance": 7,
        "score_recency": 9,
        "score_source_avail": 8,
        "score_total": 31,
        "signal_count": 3,
        "status": "approved",
        "keywords": json.dumps([])
    }
    result = sb_insert("p2_topics", topic)
    if result:
        return result.get("id")
    return None

# ============================================================
# ARTICLES
# ============================================================

articles_data = []

# ---------------------------------------------------------------
# ARTICLE 1: England Women beat India Women in 2nd T20I Bristol
# ---------------------------------------------------------------
print("\n" + "="*60)
print("ARTICLE 1: England Women level T20I series vs India")
print("="*60)

topic1_id = create_topic("England Women Level T20I Series Against India at Bristol 2026")
print(f"  Topic ID: {topic1_id}")

body1 = """India's bid to wrap up the T20I series a game early came undone in the space of twelve deliveries at Bristol's County Ground on Saturday.

England won the toss, chose to bat, and spent eighteen overs looking ordinary. At 129 for 5, India's bowlers had the hosts under control. The asking rate was manageable. The pitch was true. Shree Charani had taken three wickets for 25 runs off her four overs. Every indicator suggested a target between 145 and 155 — comfortably within India's range.

**Then Freya Kemp walked in.**

## Two Overs That Changed Everything

What followed was one of the most destructive cameos in recent women's T20I cricket. Kemp smashed 39 runs off just 13 balls — not a single one of them defensive. India's death bowlers, who had been metronomic all afternoon, suddenly had no answers. The 19th and 20th overs together leaked 39 runs, an extraordinary collapse in discipline that turned England's total from chaseable to commanding.

England finished on 168 for 5 from their 20 overs. The last two overs alone had added more than a quarter of the total.

## India's Chase Never Found Rhythm

Shafali Verma gave India the start they needed — aggressive, intent-driven — but her dismissal for 22 off 14 in the third over set a pattern the middle order could never break. Smriti Mandhana compiled a composed 32 off 25, looking settled until Charlotte Dean had her caught in the ninth over. When Mandhana went, India were 62 for 2 and the required rate was already climbing.

Yastika Bhatia batted the longest for India — 33 off 36 — but the knock struggled for urgency. Her eventual retirement out in the fourteenth over came too late to change the momentum. Harmanpreet Kaur made 28 off 22, but the wickets kept falling at precisely the wrong moments. Four wickets tumbled in the final two overs as India finished on 142 for 9 — 26 runs short.

Dean was outstanding with the ball: 2 for 20 off four overs. Kemp, already the match-winner with the bat, took 2 for 15 from her two overs to claim Player of the Match.

## The Series Is Alive

The result levels the three-match series at 1-1 after India's dominant 38-run win in the first T20I at Chelmsford, where Jemimah Rodrigues's 69 off 40 had been the decisive innings. The decider moves to Cooper Associates County Ground in Taunton on Tuesday, June 2.

For India, the concern is not the defeat itself but where it came from. The team had controlled ninety percent of England's innings. The final ten percent — twelve balls — undid all of it. In T20 cricket, that is the margin. One unchecked over changes everything.

## What This Means for the World Cup

The T20 World Cup begins on English soil on June 12, less than two weeks away. India and England could meet again in the group stage. For both sides, this series is the last meaningful competitive cricket before the tournament begins.

India's bowling unit has questions to answer at the death. England now have genuine momentum heading into the decider. For NRIs across the UK, Tuesday's match at Taunton is the last chance to watch India's women live before the World Cup — and it now carries a series on the line.

**Where to Watch**: The third T20I at Taunton on Tuesday, June 2, starts at 6:30 PM BST (11:00 PM IST). Available on Sky Sports in the UK and FanCode in India.

*Sources: ESPN Cricinfo, Sky Sports, Heavy.com, CREX*"""

art1 = {
    "topic_id": topic1_id,
    "headline": "Freya Kemp Smashed 39 Off 13 Balls in the Final Two Overs. England Beat India by 26 Runs to Level the T20I Series.",
    "subheadline": "India had England at 129 for 5 after 18 overs in Bristol. Then Kemp arrived. The series decider is at Taunton on Tuesday, ten days before the T20 World Cup begins on English soil.",
    "category": "sports",
    "vertical": "sport",
    "urgency": "daily",
    "tags": json.dumps(["India Women Cricket", "England Women Cricket", "T20I", "Freya Kemp", "Smriti Mandhana", "T20 World Cup 2026", "Bristol"]),
    "diaspora_angle": "The T20 World Cup starts on English soil on June 12, making the India-England bilateral series a direct preview for NRIs in the UK. Tuesday's decider at Taunton is the last chance for diaspora cricket fans to watch India's women live before the tournament begins.",
    "slug": "england-beat-india-women-2nd-t20i-bristol-kemp-39-off-13-series-1-1-taunton-decider-20260530",
    "sources": json.dumps(["ESPN Cricinfo", "Sky Sports", "Heavy.com", "CREX"]),
    "status": "published",
    "published_at": "2026-05-30T18:00:00Z",
    "body": body1,
    "word_count": len(body1.split()),
    "score_total": 31,
    "is_featured": False
}

# Image sourcing
img_url = fetch_wikipedia_person_image("Smriti Mandhana")
if not img_url:
    img_url = fetch_pexels_image("women cricket match batting", "cricket stadium England")

if img_url:
    filename = f"{art1['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    if final_url:
        art1["image_url"] = final_url
        art1["image_attribution"] = "Wikimedia Commons" if "wikimedia" in img_url.lower() else "The Videshi"

articles_data.append(art1)

# ---------------------------------------------------------------
# ARTICLE 2: India's Unity Cup ends without a goal
# ---------------------------------------------------------------
print("\n" + "="*60)
print("ARTICLE 2: India's Unity Cup ends without a goal")
print("="*60)

topic2_id = create_topic("India Finish Last at Unity Cup 2026 in London")
print(f"  Topic ID: {topic2_id}")

body2 = """India's first match on English soil in twenty-four years ended in defeat. So did the second.

The Blue Tigers lost 1-0 to Zimbabwe in the third-place playoff of the 2026 Unity Cup at The Valley in London on Saturday. A 33rd-minute penalty from Prince Dube was the only goal of the game, and it was enough. India finished last in a four-team tournament that also included Nigeria and Jamaica.

Across two matches in London — a 2-0 semifinal loss to Jamaica and Saturday's defeat to Zimbabwe — India failed to score a single goal.

## How It Unfolded

Head coach Khalid Jamil made four changes from the Jamaica loss, handing starts to Vikram Partap Singh, Rahim Ali, Macarton Nickson, and Ricky Shabong, the last of whom had made his international debut as a substitute just days earlier.

India were not overwhelmed. The opening half-hour was evenly contested, with Sandesh Jhingan producing two crucial interventions — a stretched-leg clearance in the fourth minute and a towering header to deal with Shane Maroodza's cross in the fifteenth.

India's best chance arrived in the 29th minute. Shabong floated a perfectly weighted ball over the Zimbabwe defence for Vikram Partap Singh, who looked certain to go through on goal. But Zimbabwe captain John Takwara produced a sliding challenge at the last moment to deny him.

Four minutes later, India conceded the penalty. Dube stepped up and converted. The Blue Tigers spent the remaining fifty-seven minutes chasing an equaliser that never came.

## Two Matches, Zero Goals

The numbers from London tell a blunt story. India played 180 minutes across two matches against Jamaica (ranked 71st) and Zimbabwe (ranked 130th). They managed zero goals. The last time India played in England was 2002. A twenty-four-year gap, and this was the return.

It would be unfair to read too much into a four-team invitational tournament outside the FIFA calendar window. But the Unity Cup still carried Tier 1 status, meaning the results count for ranking points. India, ranked 136th in the world, now have those two losses on their record.

## The Bigger Picture for Indian Football

The timing makes the results harder to ignore. The 2026 FIFA World Cup kicks off in America on June 11 — twelve days from now. India are not in it. They have never qualified for it, except for a withdrawn entry in 1950. But the proximity of the tournament, held across cities with massive Indian diaspora populations, makes Indian football's standing more visible than usual.

For NRIs in the United States, the World Cup will be impossible to avoid. It will be in their stadiums, on their screens, in their neighbourhoods. And Indian football will not be part of it.

The gap between India and the teams that matter is not about one bad week in London. Jamaica and Zimbabwe are not powerhouses, but they are both competitive sides. Zimbabwe recently stunned Asian champions Qatar in Doha — a result that underlines their quality, but also reveals where India stands relative to teams ranked in the same neighbourhood.

## Silver Linings and What Comes Next

The Unity Cup was not meant to be a trophy hunt. It was a developmental exercise — a chance to blood young players, test combinations, and build confidence against non-Asian opposition in unfamiliar conditions. On the first two counts, it delivered. Ricky Shabong and Noufal PN earned their senior international debuts. Edmund Lalrindika got his first start. These minutes in London, against physical opposition on English turf, have value that does not show up in scorelines.

India return to more familiar territory for the SAFF Championship in Goa and will prepare for the 2027 AFC Asian Cup qualifiers. The domestic Indian Super League remains the primary competitive environment for most of these players.

But at 136th in the world, with zero goals across two matches in a four-team invitational, Indian football needs more than developmental silver linings. It needs a plan to close the gap — and evidence that the plan is working.

*Sources: Sportslightmedia, Latestly, Wikipedia, IANS*"""

art2 = {
    "topic_id": topic2_id,
    "headline": "India's Unity Cup in London Ended Without a Single Goal. They Lost 1-0 to Zimbabwe in the Third-Place Match.",
    "subheadline": "The Blue Tigers went to England for the first time in twenty-four years. They came back with two defeats, zero goals, and hard questions twelve days before the FIFA World Cup kicks off in America.",
    "category": "sports",
    "vertical": "sport",
    "urgency": "daily",
    "tags": json.dumps(["India Football", "Unity Cup 2026", "Zimbabwe", "Blue Tigers", "Khalid Jamil", "FIFA World Cup 2026", "London", "Sandesh Jhingan"]),
    "diaspora_angle": "The FIFA World Cup starts in America in twelve days, across cities with massive Indian diaspora populations. Indian football's absence from the tournament, combined with this goalless showing against lower-ranked opposition in London, sharpens the contrast between the sport's aspirations and its current standing for NRIs who will be surrounded by World Cup fever.",
    "slug": "india-unity-cup-london-2026-zero-goals-two-defeats-zimbabwe-third-place-world-cup-20260530",
    "sources": json.dumps(["Sportslightmedia", "Latestly", "Wikipedia - Unity Cup", "IANS"]),
    "status": "published",
    "published_at": "2026-05-30T18:05:00Z",
    "body": body2,
    "word_count": len(body2.split()),
    "score_total": 30,
    "is_featured": False
}

# Image sourcing
img_url = fetch_wikipedia_person_image("India national football team")
if not img_url:
    img_url = fetch_wikipedia_person_image("Sandesh Jhingan")
if not img_url:
    img_url = fetch_pexels_image("football match London stadium", "soccer pitch evening")

if img_url:
    filename = f"{art2['slug']}.jpg"
    final_url = upload_image_to_supabase(img_url, filename)
    if final_url:
        art2["image_url"] = final_url
        art2["image_attribution"] = "Wikimedia Commons" if "wikimedia" in img_url.lower() else "The Videshi"

articles_data.append(art2)

# ============================================================
# PUBLISH
# ============================================================
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

published = 0
for i, art in enumerate(articles_data):
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")
    
    # Validate word count
    print(f"  Word count: {art['word_count']}")
    if art['word_count'] < 400:
        print("  ✗ REJECTED: Under 400 words")
        continue
    
    # Validate headline length
    if len(art['headline']) > 200:
        print(f"  ⚠ Headline too long ({len(art['headline'])} chars)")
    
    # Validate subheadline
    if len(art.get('subheadline', '')) < 15:
        print("  ✗ REJECTED: Subheadline too short")
        continue
    
    # Validate image
    img = art.get('image_url', '')
    if img:
        if any(bad in img for bad in ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']):
            print("  ✗ BANNED image source, removing")
            del art['image_url']
        elif not validate_image_url(img):
            print("  ⚠ Image validation failed, removing")
            del art['image_url']
    
    if not art.get('topic_id'):
        print("  ✗ REJECTED: No topic_id")
        continue
    
    result = sb_insert("p2_articles", art)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {art['slug']} (id: {art_id})")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {art['slug']}")

print(f"\n{'='*60}")
print(f"DONE — {published}/{len(articles_data)} articles published")
print("="*60)
