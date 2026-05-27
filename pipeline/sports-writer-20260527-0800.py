#!/usr/bin/env python3
"""
Sports writer for The Videshi — 2026-05-27 08:00 PDT run
Articles:
1. Vaibhav Sooryavanshi's record-breaking IPL 2026 season (583 runs, 53 sixes, age 15)
2. French Open: Yuki Bhambri & Sriram Balaji advance in men's doubles
3. Neeraj Chopra's CWG spot depends on June comeback after back injury
"""

import json, os, re, sys, time, uuid, urllib.parse
import requests
from datetime import datetime, timezone

# ── ENV ──────────────────────────────────────────────────────────────────
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

# ── WIKIPEDIA IMAGE ──────────────────────────────────────────────────────
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

# ── PEXELS IMAGE ─────────────────────────────────────────────────────────
def fetch_pexels_image(query, fallback_query=None):
    """Fetch from Pexels using curl (requests gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15,
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

# ── SUPABASE IMAGE UPLOAD ────────────────────────────────────────────────
def upload_image_to_supabase(img_url, filename):
    """Download an image and upload to Supabase storage. Return public URL."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                print(f"  → Using permanent source URL directly")
                return img_url
            return None
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if not content_type.startswith('image/'):
            print(f"  ⚠ Not an image: {content_type}")
            return img_url if ('upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url) else None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return img_url if ('upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url) else None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true',
            },
            data=r.content,
            timeout=30,
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
                return img_url
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        if 'upload.wikimedia.org' in img_url or 'images.pexels.com' in img_url:
            return img_url
        return None

# ── VALIDATE IMAGE ───────────────────────────────────────────────────────
def validate_image_url(url):
    """Check that a URL returns a real image > 5KB."""
    if not url:
        return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' in ct and cl > 5000:
            return True
        if 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            r2.close()
            return len(chunk) > 5000
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

# ── SUPABASE HELPERS ─────────────────────────────────────────────────────
def sb_insert(table, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS_SB, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        return result[0] if isinstance(result, list) and result else result
    else:
        print(f"  ✗ Insert into {table} failed: {r.status_code} {r.text[:300]}")
        return None

def check_duplicate(slug):
    """Check if an article with this slug already exists."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id&limit=1"
    r = requests.get(url, headers=HEADERS_SB, timeout=10)
    if r.status_code == 200:
        data = r.json()
        return len(data) > 0
    return False


# ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 1: Vaibhav Sooryavanshi's Record-Breaking IPL 2026 Season
# ══════════════════════════════════════════════════════════════════════════

article1 = {
    "headline": "He Is Fifteen Years Old. He Has 583 Runs, 53 Sixes, and a Strike Rate of 232. The IPL Has Never Seen Anything Like Vaibhav Sooryavanshi.",
    "subheadline": "The Rajasthan Royals opener has broken records that belonged to Chris Gayle, Sachin Tendulkar, and Travis Head. He turns sixteen in October.",
    "slug": "vaibhav-sooryavanshi-ipl-2026-season-583-runs-53-sixes-youngest-500-record-20260527",
    "category": "sports",
    "body": """When Sachin Tendulkar was fifteen, he was batting in the nets at the Cricket Club of India, already famous but still years away from his Test debut. When Chris Gayle was fifteen, he was playing club cricket in Kingston, Jamaica, undiscovered and unheralded. When Vaibhav Sooryavanshi turned fifteen last October, he had already played in the IPL. By May 2026, he had done something neither of them managed at any age: 583 runs in a single IPL season at a strike rate of 232.27.

The numbers are absurd. They read like a video game save file, not a professional cricket stat line.

## The Season in Numbers

Sooryavanshi has played 14 matches for Rajasthan Royals in IPL 2026. He has scored 583 runs at an average of 41.64. He has hit 53 sixes — the most ever by an Indian in a single IPL season, and the second-most in IPL history behind Chris Gayle's 59 in 2012. He is seven sixes away from matching that record, with at least one match still to play.

His strike rate of 232.27 is the highest ever recorded by a batter who has scored more than 500 runs in a T20 league season. Anywhere in the world. At any level. By anyone.

He hit his fastest IPL century — 103 off 36 balls — against Sunrisers Hyderabad, an innings so violent that Pat Cummins, the Australian captain and SRH skipper, told reporters afterward: "I think he's my new favourite player."

Against Lucknow Super Giants, he smashed 93 off 38 balls, including ten sixes, to chase down 221 with five balls to spare. Justin Langer, the LSG head coach and former Australia opener, could only marvel: "He'll adapt, he'll keep getting better and better, which is scary for world cricket."

## The Records He Has Broken

The list is almost comically long. Sooryavanshi is the youngest player to score 500 runs in a single IPL season. He is the fastest to 400 runs and the fastest to 500 runs in IPL history. He has hit more sixes than any Indian batter in a single IPL campaign. He holds the highest powerplay tally by a batter this season, surpassing Travis Head's record. He has the highest strike rate in T20 league history for any batter crossing 500 runs.

He has done all of this at fifteen.

## What His Teammates Say

Jos Buttler, the Rajasthan Royals captain, has watched from the other end: "He's one step ahead of everyone. He's now hit the most sixes for sure by an Indian player in an IPL. And I think it's only Gayle who's just ahead of him with maybe one or two more sixes for the all-time record for most sixes in a season."

Devdutt Padikkal, the RCB batter whose own teenage IPL breakout in 2020 now seems modest by comparison, was blunt about Sooryavanshi: "It would be foolish to copy him."

Kiran More, the former India wicketkeeper and national selector, reached for the only comparison that felt adequate: "Vaibhav Sooryavanshi has been made by God for this sport." More drew a direct parallel to Tendulkar — the highest praise anyone in Indian cricket can bestow.

## The Diaspora Angle

For the Indian diaspora watching from living rooms in Edison, Fremont, Brampton, and Hounslow, Sooryavanshi has become appointment television. He bats in the powerplay, which means his innings begin within the first thirty minutes of the match — perfect timing for NRIs waking up early or staying up late to catch the IPL.

His appeal transcends the usual boundaries of cricket fandom. He is not a product of a big-city academy or an IPL franchise's youth system. He is from Bhopal, the son of Rajkumar Sooryavanshi, a club-level cricketer who coached his son on basic pitches in Madhya Pradesh. The story resonates with every Indian parent who has watched their child practise in a park and wondered if the dream was possible.

## What Comes Next

Sooryavanshi is playing in the IPL Eliminator on Wednesday — Rajasthan Royals against Sunrisers Hyderabad at Mullanpur. If Rajasthan win, he gets at least one more match, and possibly two, to chase Gayle's record.

Beyond the IPL, the conversation has already begun. Multiple former cricketers and commentators have named him as a candidate for India's T20I squad for the upcoming series against Ireland and England. He is fifteen. He would be the youngest Indian to play international cricket since Tendulkar himself debuted at sixteen in 1989.

The IPL has produced prodigies before. It has never produced this.

*Sources: Sporting News, CricTracker, Fox Sports Australia, Reuters*""",
    "sources": ["Sporting News", "CricTracker", "Fox Sports Australia", "Reuters"],
    "person_image": "Vaibhav Sooryavanshi",
    "pexels_query": "cricket batsman hitting six stadium",
}

# ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 2: French Open Doubles — Bhambri & Balaji Advance
# ══════════════════════════════════════════════════════════════════════════

article2 = {
    "headline": "India's Last Two Men Standing at Roland Garros Are Doubles Partners. Both Won on Day Three.",
    "subheadline": "Yuki Bhambri and N Sriram Balaji are the only Indians left at the French Open after Karman Kaur Thandi's singles qualifier exit. Next up: the fifth seeds.",
    "slug": "yuki-bhambri-sriram-balaji-french-open-2026-doubles-second-round-india-20260527",
    "category": "sports",
    "body": """India does not have a singles player in the main draw of the 2026 French Open. The last hope, Karman Kaur Thandi, was eliminated in the qualifying rounds. Maaya Rajaeswaran Revathi is competing in the girls' singles and Arnav Paparkar in the boys', but in the senior draw, India's representation comes down to two men playing doubles.

Both of them won on Day Three. Both of them will be back for more.

## Bhambri and Venus Cruise Through

Yuki Bhambri, partnering New Zealand's Michael Venus, beat Argentina's Francisco Cerundolo and Mariano Kestelboim 7-5, 6-2 in the men's doubles first round. It was a controlled performance from a pair that arrived in Paris with momentum — Bhambri and Venus reached the ATP 250 final in Geneva just days before Roland Garros began.

Bhambri, now 34 years old, has quietly built one of India's most successful doubles careers. His ATP career-high doubles ranking of 18, achieved in 2026, makes him the highest-ranked Indian men's doubles player in the current generation. He was the first Indian to win the junior Australian Open, and his transition to a doubles specialist in his late twenties has extended a career that many wrote off after repeated injury setbacks in singles.

The second round draws fifth seeds Andrea Vavassori and Simone Bolelli of Italy — a serious step up in quality, but Bhambri and Venus have the form and the clay-court rhythm to compete.

## Balaji Fights Through in Three Sets

N Sriram Balaji, playing alongside Brazil's Marcelo Demoliner, had a tougher afternoon. The Indian-Brazilian pair beat Germany's Constantin Frantzen and Robin Haase in three sets. Unlike Bhambri's relatively serene passage, Balaji had to work through a tight opening set before the pair found their rhythm.

Balaji, 34, from Chennai, has been a fixture on the doubles circuit for the past decade. He represented India at the 2024 Paris Olympics in doubles and has been a reliable Davis Cup doubles player for years. His partnership with Demoliner is relatively new but has shown enough quality to advance at a Grand Slam.

## A Tournament Missing Its Champion

The 2026 French Open is being played without its defending men's singles champion. Carlos Alcaraz, who won back-to-back titles at Roland Garros in 2024 and 2025, withdrew with a serious right wrist injury sustained at the Barcelona Open. The injury has also ruled him out of Wimbledon.

Alcaraz's absence has cleared a path for Jannik Sinner, the world number one, who arrived in Paris unbeaten on clay in 2026 and carrying a 17-0 record on the surface this season. The Italian is the overwhelming favourite, with Polymarket putting his probability at 73 percent. Alexander Zverev and Novak Djokovic — the 38-year-old Serbian chasing a record-extending 25th Grand Slam title — are the only other realistic contenders.

## What It Means for Indian Tennis

India's Grand Slam presence in singles has been effectively absent since Sania Mirza's retirement. The country's best current singles player, Sumit Nagal, is ranked outside the top 100 and did not qualify for Roland Garros. The doubles pathway — through Bhambri, Balaji, and the retired Rohan Bopanna — remains India's most viable route to Grand Slam success.

For NRIs following the French Open from North American time zones, the men's doubles schedule offers a practical advantage: doubles matches often begin earlier in the day in Paris, making them more accessible for morning viewing on the US East Coast and late evening in India.

Bhambri and Balaji play their second-round matches on Wednesday or Thursday. One more win each, and India will have two pairs in the third round of a Grand Slam for the first time in recent memory.

*Sources: Sporting News, LatestLY, SSI Fanzine, SwapUpdate*""",
    "sources": ["Sporting News", "LatestLY", "SSI Fanzine", "SwapUpdate"],
    "person_image": "Yuki Bhambri",
    "pexels_query": "tennis clay court doubles Roland Garros",
}

# ══════════════════════════════════════════════════════════════════════════
#  ARTICLE 3: Neeraj Chopra — CWG Spot Depends on June Comeback
# ══════════════════════════════════════════════════════════════════════════

article3 = {
    "headline": "Neeraj Chopra Is in Switzerland Rehabbing a Back Injury. His Commonwealth Games Spot Depends on What Happens in June.",
    "subheadline": "India's Olympic javelin champion missed the Federation Cup. He might miss Glasgow. His coach says the selectors are watching.",
    "slug": "neeraj-chopra-back-injury-commonwealth-games-2026-switzerland-rehab-june-comeback-20260527",
    "category": "sports",
    "body": """Neeraj Chopra left India on May 25 for a 47-day off-season training camp in Bienne, Switzerland. He did not compete at the Federation Cup in Ranchi last week. He will not be throwing a javelin competitively for at least several more weeks. And his place at the 2026 Commonwealth Games in Glasgow — an event that every Indian sports fan has circled on the calendar — is no longer a certainty.

The reason is a back injury that has lingered through the early months of 2026, forcing India's most decorated track and field athlete to prioritise rehabilitation over competition.

## The Timeline

Chopra last competed at the 2025 World Athletics Championships in Tokyo, where he finished eighth — his first time outside the top two in a major competition since 2021. That result, combined with a chronic back issue that has troubled him intermittently since his teenage years, prompted a longer-than-usual off-season.

He skipped the Federation Cup entirely. His coach, Radhakrishnan Nair, told reporters that the decision was straightforward: "We can't risk his long-term career for one national event. The Commonwealth Games and the Asian Games are the priority, but only if his body is ready."

The Commonwealth Games in Glasgow begin in late July. Chopra's participation depends on how his body responds to the Swiss training camp and whether he can compete in a tune-up event in June — most likely a Diamond League meeting in Europe.

## What the Selectors Are Saying

Nair has indicated that the selectors will evaluate Chopra's fitness based on his June performances. If he can throw competitively and show no recurrence of the back issue, he will be selected for Glasgow. If he cannot, India will send a team without its biggest name.

"His spot is not automatic," Nair said. "He has to prove his fitness. But we are optimistic. The injury is manageable, and the Swiss camp is designed to build him back to full capacity."

## The Federation Cup Happened Without Him — and It Was Historic

The irony of Chopra's absence from the Federation Cup is that the event produced some of the most extraordinary performances in Indian athletics history. Over four days in Ranchi, three national records fell.

Gurindervir Singh ran 10.09 seconds in the 100 metres — the fastest time ever recorded by an Indian man. Vishal TK ran 44.97 seconds in the 400 metres, becoming the first Indian to break 45 seconds in the event. Tejaswin Shankar scored 8,057 points in the decathlon, becoming the first Indian to cross 8,000 points.

None of these men are household names in India. That distinction belongs almost exclusively to Chopra, whose Olympic gold in Tokyo and silver in Paris made him the most recognisable Indian athlete of his generation. His absence from Ranchi was felt, but the performances that emerged in his shadow suggest Indian athletics is developing depth it has never had before.

## Avinash Sable Is Also Missing

Chopra is not the only Indian star in rehabilitation. Avinash Sable, the national record holder in the 3000-metre steeplechase, is recovering from ACL surgery following an injury sustained during the Monaco Diamond League in 2025. Sable's return timeline is uncertain, and he is unlikely to be fit for the Commonwealth Games.

## The NRI Watch

For the Indian diaspora — particularly in the UK, where the Commonwealth Games will be held — Chopra's participation is the single biggest draw. His Olympic performances turned him into a crossover star, recognised by Indians who have never watched a javelin competition. NRIs in London, Birmingham, Edinburgh, and Glasgow have already begun planning trips to the Games, many of them specifically to watch Chopra throw.

If he is not there, the disappointment will be palpable. But the athletes who filled the void at the Federation Cup — Gurindervir, Vishal, Tejaswin — represent a new generation that deserves the same attention. They just need the stage.

June will tell us whether India's golden arm is ready. Until then, the javelin waits.

*Sources: Devdiscourse, Bharat Affairs, MyKhel, IndiaSportsHub*""",
    "sources": ["Devdiscourse", "Bharat Affairs", "MyKhel", "IndiaSportsHub"],
    "person_image": "Neeraj Chopra",
    "pexels_query": "javelin throw athletics stadium",
}


# ══════════════════════════════════════════════════════════════════════════
#  PUBLISH ALL ARTICLES
# ══════════════════════════════════════════════════════════════════════════

articles = [article1, article2, article3]
published = 0

for i, article in enumerate(articles, 1):
    print(f"\n{'='*60}")
    print(f"  ARTICLE {i}: {article['headline'][:60]}...")
    print(f"{'='*60}")

    # Check for duplicate
    if check_duplicate(article['slug']):
        print(f"  ⚠ SKIP: Slug '{article['slug']}' already exists")
        continue

    # Source image — Wikipedia first for person articles
    image_url = None
    image_attribution = None

    if article.get('person_image'):
        print(f"  → Trying Wikipedia for '{article['person_image']}'...")
        wiki_img = fetch_wikipedia_person_image(article['person_image'])
        if wiki_img:
            # Upload to Supabase for permanence
            safe_name = re.sub(r'[^a-z0-9]+', '-', article['slug'][:60]) + '.jpg'
            uploaded = upload_image_to_supabase(wiki_img, safe_name)
            if uploaded and validate_image_url(uploaded):
                image_url = uploaded
                image_attribution = "Wikimedia Commons"
                print(f"  ✓ Using Wikipedia image")

    if not image_url and article.get('pexels_query'):
        print(f"  → Trying Pexels for '{article['pexels_query']}'...")
        pexels_img = fetch_pexels_image(article['pexels_query'])
        if pexels_img:
            safe_name = re.sub(r'[^a-z0-9]+', '-', article['slug'][:60]) + '-pexels.jpg'
            uploaded = upload_image_to_supabase(pexels_img, safe_name)
            if uploaded and validate_image_url(uploaded):
                image_url = uploaded
                image_attribution = "Pexels"
                print(f"  ✓ Using Pexels image")

    if not image_url:
        print(f"  ⚠ No image found — publishing without image (no image > wrong image)")

    # Build article record
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    record = {
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "slug": article['slug'],
        "category": article['category'],  # MUST be lowercase "sports"
        "body": article['body'].strip(),
        "sources": json.dumps(article['sources']),
        "image_url": image_url,
        "image_attribution": image_attribution,
        "vertical": article['category'],
        "status": "published",
        "published_at": now,
        "created_at": now,
        "updated_at": now,
        # "author" column does not exist in p2_articles
    }

    # Validate before inserting
    assert record['category'] == 'sports', f"Category must be 'sports', got '{record['category']}'"
    assert 20 <= len(record['headline']) <= 200, f"Headline length {len(record['headline'])} out of range"
    assert len(record['subheadline']) >= 15, f"Subheadline too short: {len(record['subheadline'])}"
    body_words = len(record['body'].split())
    assert body_words >= 400, f"Body too short: {body_words} words (min 400)"
    assert record['slug'] == record['slug'].lower(), "Slug must be lowercase"
    assert not any(c in record['slug'] for c in ' _'), "Slug must be hyphenated, no spaces/underscores"

    print(f"  → Body: {body_words} words")
    print(f"  → Image: {'yes' if image_url else 'no'}")
    print(f"  → Inserting into p2_articles...")

    result = sb_insert('p2_articles', record)
    if result:
        print(f"  ✓ Published: {article['slug']}")
        published += 1
    else:
        print(f"  ✗ Failed to publish: {article['slug']}")

print(f"\n{'='*60}")
print(f"  DONE: {published}/{len(articles)} articles published")
print(f"{'='*60}")
