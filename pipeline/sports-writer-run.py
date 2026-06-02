#!/usr/bin/env python3
"""Sports writer — generates 2 articles for The Videshi (June 2, 2026 run)."""

import json, os, sys, uuid, re, time
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key] = val

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests, urllib.parse

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_API_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(img_url, filename):
    """Download image and upload to Supabase storage."""
    try:
        r = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code == 429:
            print(f"  ⚠ Rate limited, waiting 3s and retrying...")
            time.sleep(3)
            r = requests.get(img_url, timeout=15, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return None
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }
        up = requests.post(upload_url, data=r.content, headers=upload_headers, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            # Try PUT instead
            up = requests.put(upload_url, data=r.content, headers=upload_headers, timeout=30)
            if up.status_code in (200, 201):
                public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
                print(f"  ✓ Uploaded to Supabase (PUT): {public_url[:80]}...")
                return public_url
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return None

def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def patch_article(art_id, updates):
    """Patch an article by ID."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{art_id}"
    r = requests.patch(url, headers=HEADERS, json=updates, timeout=15)
    if r.status_code in (200, 204):
        print(f"  ✓ Article patched: {art_id}")
    else:
        print(f"  ⚠ Patch failed: {r.status_code} {r.text[:200]}")

# ─────────────────────────────────────────────
# ARTICLE 1: India's ODI Squad for Afghanistan
# ─────────────────────────────────────────────
def write_article_1():
    print("\n=== Article 1: India's ODI Squad for Afghanistan ===")

    headline = "Rohit and Kohli Are Back. Ishan Kishan Returns After Three Years. India's ODI Squad for Afghanistan Is a Statement."
    subheadline = "Hardik Pandya's inclusion is subject to fitness clearance. Prince Yadav earns a maiden call-up. The three-match series starts June 13 in Dharamsala."
    slug = "india-odi-squad-afghanistan-2026-rohit-kohli-ishan-kishan-prince-yadav-hardik-fitness-nri"

    body = """The selectors have spoken. India's ODI squad for the three-match series against Afghanistan, starting June 13 in Dharamsala, is a blend of returning stars, surprise recalls, and fresh faces that signals the BCCI's intent heading into a packed 50-over calendar.

## The Headline Returns

**Rohit Sharma** and **Virat Kohli** are back in the ODI setup after sitting out the England Test tour. Both are named in the 15-member squad, though Rohit's inclusion carries an asterisk — his selection is subject to fitness clearance after the hamstring injury that limited his involvement in IPL 2026. Mumbai Indians head coach Mahela Jayawardene recently said Rohit was "at 100 per cent," but the BCCI's medical team wants its own assessment before committing him to three ODIs in eight days.

If Rohit is cleared, he and Shubman Gill — who captains the squad — will form a formidable opening partnership. If not, Yashasvi Jaiswal or Ishan Kishan could slot in at the top.

Kohli, who has been India's most prolific ODI batter since the format's restart in late 2025 with 616 runs at an average of 88.00, needs no fitness test. His presence alone makes this squad a serious unit.

## The Three-Year Comeback

The most emotionally resonant selection is **Ishan Kishan**'s. The wicketkeeper-batter last played an ODI during the 2023 World Cup — coincidentally against Afghanistan, the same opposition he now returns to face. A prolonged absence from international cricket, fuelled by a fallout with the selectors over his refusal to play domestic cricket, seemed to have ended his career at 25.

But Kishan rebuilt his reputation the hard way. Consistent domestic performances across the 2025-26 season earned him a recall to the setup, and the selectors have picked him as a versatile option who can bat anywhere from one to seven. At 27, he gets a second chance that most players never receive.

## The Debutant in Waiting

**Prince Yadav**, the tall right-arm pacer from Lucknow Super Giants, earns a maiden call-up to the Indian squad. The 22-year-old finished IPL 2026 with 16 wickets in 14 matches despite his franchise's torrid season. His pace, bounce, and ability to hit hard lengths consistently caught the selectors' attention.

Prince is part of the ODI squad only — he is not in the Test squad for the one-off match starting June 6. With Mohammed Siraj named exclusively in the Test pool, Prince could make his debut as early as the first ODI in Dharamsala.

## Hardik Pandya's Fitness Question

**Hardik Pandya** is in the squad, but his selection is subject to fitness clearance at the BCCI's Centre of Excellence. The all-rounder was due to report on June 2 and will spend over a week proving his fitness before the ODI camp assembles around June 10-11.

Pandya's body has been a recurring concern throughout his career, and the BCCI is taking no chances ahead of a stretch that includes not just the Afghanistan series but the subsequent England white-ball tour. If he passes, India get their premium all-rounder back. If he doesn't, Nitish Kumar Reddy — already in the squad — becomes the primary pace-bowling all-rounder.

## The Full Squad

**Captain:** Shubman Gill. **Vice-Captain:** Shreyas Iyer.

**Batters:** Rohit Sharma*, Virat Kohli, Shreyas Iyer, KL Rahul (wk).

**Wicketkeeper:** Ishan Kishan.

**All-rounders:** Hardik Pandya*, Nitish Kumar Reddy, Washington Sundar.

**Spinners:** Kuldeep Yadav, Harsh Dubey, Gurnoor Brar.

**Pacers:** Arshdeep Singh, Prasidh Krishna, Prince Yadav.

*Subject to fitness clearance.

## The Schedule

The series covers three venues across India: Dharamsala (June 13), Lucknow (June 17), and Chennai (June 20). For the diaspora, the timing works — all three matches start at 1:30 PM IST, which translates to early morning in the US and mid-morning in the UK.

## What It Means for NRIs

This squad is the first time since the Champions Trophy that Rohit, Kohli, and Gill are in the same ODI eleven. For NRI fans who watched the 50-over resurgence from October 2025 onward — India's ODI record in that stretch has been exceptional — this series is a chance to see the full-strength batting lineup in action before the bigger assignments later in the year.

The Afghanistan ODIs also serve as a dry run for the selectors. With England's white-ball tour looming and the Champions Trophy defence not far behind in the planning horizon, every spot in this squad is under evaluation.

*Sources: CricTracker, InsideSport India, BCCI*"""

    # Image sourcing — try Ishan Kishan (the comeback story)
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Ishan Kishan")
    img_attribution = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_wikipedia_person_image("India national cricket team")
        if not img_url:
            img_url = fetch_pexels_image("cricket stadium India", "cricket match India")
            img_attribution = "The Videshi"

    art_id = str(uuid.uuid4())
    final_img = None
    if img_url:
        final_img = upload_image_to_supabase(img_url, f"{art_id}.jpg")

    article = {
        "id": art_id,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["CricTracker", "InsideSport India", "BCCI"]),
        "is_editorial": False,
        "image_url": final_img,
        "image_attribution": img_attribution if final_img else None
    }

    result = insert_article(article)
    if result:
        print(f"  ✓ Article 1 published: {headline[:60]}...")
    return result


# ─────────────────────────────────────────────
# ARTICLE 2: Norway Chess Women R8 — Assaubayeva beats Divya
# ─────────────────────────────────────────────
def write_article_2():
    print("\n=== Article 2: Norway Chess Women R8 ===")

    headline = "Assaubayeva Beat Divya Deshmukh in the Decisive Round. The Norway Chess Women's Title Is All but Settled."
    subheadline = "The Kazakh star leads by 5.5 points with two rounds left. Divya drops to joint third. Humpy finishes last among six."
    slug = "norway-chess-women-2026-round-8-assaubayeva-beats-divya-deshmukh-title-decided-nri"

    body = """The match that was supposed to decide Norway Chess Women ended up deciding it — just not the way Indian fans hoped.

In the most anticipated game of Round 8, **Bibisara Assaubayeva** of Kazakhstan defeated **Divya Deshmukh** in classical play with the black pieces, earning the full three points and stretching her lead at the top of the standings to a virtually insurmountable 5.5 points with only two rounds remaining.

## The Decisive Game

Divya had White — the advantage of the first move, the initiative, and the knowledge that a classical win would bring her back to within striking distance. The buildup had been framed as a title-defining showdown. Our own preview described it as "now or never" for the 20-year-old from Nagpur.

But Assaubayeva, 21, is playing the tournament of her life. She absorbed Divya's opening pressure, found counterplay in the middlegame, and gradually seized control. The Kazakh player's technique in converting advantages has been the story of this event — she now has four classical wins, more than any other player in either the Open or Women's sections.

Divya's loss drops her from sole second to joint third alongside China's Zhu Jiner, both on 10 points.

## The Standings After Round 8

| Player | Country | Points |
|--------|---------|--------|
| Bibisara Assaubayeva | Kazakhstan | **15.5** |
| Anna Muzychuk | Ukraine | 10.5 |
| Divya Deshmukh | India | 10 |
| Zhu Jiner | China | 10 |
| Ju Wenjun | China | 9 |
| Koneru Humpy | India | 8 |

With a maximum of 6 points available across the final two rounds, Assaubayeva needs just half a point from her remaining games to mathematically clinch the title. Even if she loses both — an unlikely scenario given her form — she would need all three of her nearest rivals to win their classical games to be overtaken. The title is hers to lose, and she has shown no inclination to lose anything in Oslo.

## Divya's Tournament in Context

This is not a failure for Divya Deshmukh. She is 20 years old, playing in her first Norway Chess, competing against a field that includes a reigning World Champion (Ju Wenjun), a former World Championship finalist (Anna Muzychuk), and a veteran of decades of elite chess (Koneru Humpy). She came into Round 8 in second place and pushed for the title until the penultimate stage.

But the gap between second and first in women's chess has a name right now, and it is Bibisara Assaubayeva. The Kazakh player has been the most dominant force in the women's game this season, and her Norway Chess performance — likely a title-winning one — cements her status as the player everyone else is chasing.

## Humpy's Difficult Event

For Indian fans, the more sobering story is **Koneru Humpy**'s position at the bottom of the standings with 8 points after eight rounds. The 39-year-old, who remains one of the most decorated players in women's chess history, has struggled to find her form in Oslo. She drew her classical game in Round 8 but has not won a single classical game in the tournament.

Humpy's participation in Norway Chess was itself a statement of ambition — she was not content to wind down her career quietly. But the results suggest that the gap between her current form and the level required at super-tournaments has widened. Whether this event marks a turning point or a temporary dip is a question only the coming months will answer.

## The Open Section: So Still Leads

In the Open tournament, **Wesley So** maintained his lead with 14 points after drawing with Vincent Keymer and winning the Armageddon tiebreak. The American grandmaster has been the most consistent player in the event, but the field is closing in.

**Alireza Firouzja** bounced back from two consecutive classical losses with a win over World Champion **Gukesh Dommaraju**, climbing to 13 points. And **R Praggnanandhaa** — whose classical victory over Magnus Carlsen in this same round was the headline result in the Open section — sits on 12 points, within striking distance of the top two.

Carlsen, who lost to Pragg in classical, drops to 9 points and fifth place. The final two rounds will determine whether So can hold off Firouzja's late surge and Pragg's momentum.

## What Comes Next

The tournament resumes after a rest day. In Round 9, the pairings will be crucial — the final stretch of a double round-robin often produces the most dramatic results as players who need points take risks.

For Divya, the remaining rounds are about pride and rating points. For Assaubayeva, they are a coronation. And for Indian chess fans watching from abroad, the lesson is clear: India's women are at the table, even if the trophy goes elsewhere this time.

*Norway Chess 2026 runs May 25–June 5 in Oslo. Sources: Chess.com, ChessBase, Wikipedia*"""

    # Image sourcing — try Bibisara Assaubayeva from Wikipedia
    print("  Sourcing image...")
    img_url = fetch_wikipedia_person_image("Bibisara Assaubayeva")
    img_attribution = "Wikimedia Commons"
    if not img_url:
        img_url = fetch_wikipedia_person_image("Divya Deshmukh")
        if not img_url:
            img_url = fetch_pexels_image("chess tournament", "chess grandmaster")
            img_attribution = "The Videshi"

    art_id = str(uuid.uuid4())
    final_img = None
    if img_url:
        final_img = upload_image_to_supabase(img_url, f"{art_id}.jpg")

    article = {
        "id": art_id,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Chess.com", "ChessBase", "Wikipedia"]),
        "is_editorial": False,
        "image_url": final_img,
        "image_attribution": img_attribution if final_img else None
    }

    result = insert_article(article)
    if result:
        print(f"  ✓ Article 2 published: {headline[:60]}...")
    return result


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Sports writer run: {datetime.now(timezone.utc).isoformat()}")
    
    results = []
    r1 = write_article_1()
    results.append(r1)
    
    r2 = write_article_2()
    results.append(r2)
    
    success = sum(1 for r in results if r)
    print(f"\n{'='*50}")
    print(f"Published {success}/{len(results)} articles")
    if success < len(results):
        print("⚠ Some articles failed to publish")
        sys.exit(1)
    print("✓ All articles published successfully")
