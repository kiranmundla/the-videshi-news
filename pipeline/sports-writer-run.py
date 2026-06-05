#!/usr/bin/env python3
"""Sports writer for The Videshi — produces 2 articles."""

import requests
import urllib.parse
import json
import os
import sys
import time
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
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
            # Try thumbnail first (330px, always works), then originalimage
            img = data.get("thumbnail", {}).get("source") or data.get("originalimage", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/"):
                    continue
                if mime == "image/svg+xml" or ii.get("width", 0) < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": ii.get("width", 0),
                    "height": ii.get("height", 0),
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image. Uses curl internally to avoid 403."""
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('original')
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Check that URL returns a valid image > 5KB."""
    try:
        # Use GET with stream to handle redirects and check actual content
        r = requests.get(url, timeout=15, allow_redirects=True, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com; editorial)"})
        content_type = r.headers.get('Content-Type', '')
        # Read first chunk to check size
        content = r.content
        size = len(content)
        if 'image' in content_type and size > 5000:
            print(f"  ✓ Image validated: {size} bytes, {content_type}")
            return True
        print(f"  ✗ Image failed validation: {size} bytes, {content_type}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Article inserted: {result[0].get('id', 'unknown')}")
            return True
        print(f"  ✓ Article inserted")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: Norway Chess Round 9 — Praggnanandhaa hat-trick
# ============================================================
def write_article_1():
    print("\n=== ARTICLE 1: Norway Chess Round 9 ===")

    # Image sourcing: Try Praggnanandhaa Wikipedia first
    print("Sourcing image...")
    img_url = fetch_wikipedia_person_image("Rameshbabu Praggnanandhaa")
    if not img_url:
        img_url = fetch_wikipedia_person_image("R. Praggnanandhaa")
    img_attribution = "Wikimedia Commons"
    img_caption = "R. Praggnanandhaa at a chess tournament"

    if not img_url:
        # Try Wikimedia Commons
        commons = fetch_wikimedia_commons_images("Praggnanandhaa chess")
        if commons:
            img_url = commons[0]["url"]

    if not img_url:
        # Fallback to Pexels chess
        img_url = fetch_pexels_image("chess grandmaster tournament")
        img_attribution = "Pexels"
        img_caption = "A chess board at an elite tournament"

    if img_url and not validate_image(img_url):
        print("  Primary image failed validation, trying alternatives...")
        img_url = fetch_pexels_image("chess competition professional")
        img_attribution = "Pexels"
        img_caption = "A chess board at an elite tournament"

    headline = "Praggnanandhaa Beats Gukesh for the Third Time in Oslo. He Is Half a Point Behind Wesley So With One Round Left."
    subheadline = "The 20-year-old Indian grandmaster completed a hat-trick of classical wins over the reigning World Champion at Norway Chess 2026, while Bibisara Assaubayeva clinched the women's title with a round to spare."
    slug = "praggnanandhaa-hat-trick-gukesh-norway-chess-2026-round-9-so-leads-final-round-nri"

    body = """R. Praggnanandhaa is running out of ways to say he does not think too much about the names on the other side of the board. At Norway Chess 2026 in Stavanger, the 20-year-old from Chennai has done something only Viswanathan Anand had managed before — he has beaten Magnus Carlsen twice in classical chess in the same tournament. And now, after Round 9, he has added a third scalp of equal weight: World Champion D. Gukesh, defeated in classical play for the third consecutive time in this event.

The victory on Wednesday pushed Praggnanandhaa to within half a point of tournament leader Wesley So, who drew his classical game against Carlsen before winning the Armageddon tiebreaker to collect an extra half-point and retain his lead.

## A Hat-Trick Against the World Champion

Gukesh arrived in Stavanger as the reigning World Champion but has endured a miserable campaign. His Round 9 loss to Praggnanandhaa was his latest setback in what has become a tournament to forget, dropping him further down the standings. Praggnanandhaa, meanwhile, has treated his compatriot's world title with the same clinical detachment he has shown Carlsen — identifying weaknesses, converting chances, and walking away with the full point.

"It's more important for the tournament that I get this win than thinking about who it's against," Praggnanandhaa said after his Round 8 victory over Carlsen, a sentiment he has applied with equal discipline to Gukesh.

## The Three-Horse Race

After nine of ten rounds, the standings tell the story of a tournament that could still go in three directions:

- **Wesley So** leads with 15.5 points, having won every Armageddon tiebreak he has needed this tournament
- **Praggnanandhaa** sits on 15 points, the only player to have won three classical games
- **Alireza Firouzja** is on 14 points, having beaten Gukesh in Round 8 and won his Armageddon against Vincent Keymer in Round 9

Carlsen, the five-time world champion and seven-time Norway Chess winner, sits on 10.5 points — too far back to contend for the title. It has been an uncharacteristically poor event for the Norwegian, who has now lost three classical games in a single tournament.

## Assaubayeva Clinches the Women's Title

In the women's event, Bibisara Assaubayeva sealed the title with a round to spare. The Kazakh grandmaster made a quick draw against Anna Muzychuk in the classical game, a result that was enough to put the championship beyond reach. Zhu Jiner overtook Muzychuk for second place with a classical win over India's Divya Deshmukh.

For Deshmukh, the 19-year-old from Nagpur, it has been a difficult event. She entered as one of India's brightest young talents but struggled against the elite field.

## What It Means for Indian Chess

The contrast between Praggnanandhaa's form and Gukesh's struggles tells a broader story about Indian chess's depth. Two of the world's strongest players are Indian, and in Stavanger, they have been on opposite trajectories. Gukesh, 20, won the World Championship in 2024 but has seen his rating drop by 22 points since. Praggnanandhaa, also 20, has climbed steadily, and a Norway Chess title — should he overhaul So in the final round on Friday — would be the biggest tournament victory of his career.

For the Indian diaspora, the final round offers a rare appointment. It begins at 8:30 PM IST on Friday, June 6, and for NRI fans in the US, that translates to 11 AM Eastern — a convenient time to watch what could be a historic result.

**The final round of Norway Chess 2026 starts Friday, June 5, at 5:00 PM CEST (8:30 PM IST / 11:00 AM ET).** It is broadcast live on chess.com and Norway Chess's official channels.

*Sources: chess.com, The Bridge, Yardbarker*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps(["chess.com", "The Bridge", "Yardbarker", "Bhaskar English"]),
    }

    if not img_url:
        print("  ⚠ No valid image found — skipping article")
        return False

    return insert_article(article)


# ============================================================
# ARTICLE 2: Women's T20 World Cup 2026 Preview
# ============================================================
def write_article_2():
    print("\n=== ARTICLE 2: Women's T20 World Cup 2026 ===")

    # Image sourcing: Try Harmanpreet Kaur Wikipedia
    print("Sourcing image...")
    img_url = fetch_wikipedia_person_image("Harmanpreet Kaur")
    img_attribution = "Wikimedia Commons"
    img_caption = "Harmanpreet Kaur, captain of India's Women's T20 World Cup squad"

    if not img_url:
        commons = fetch_wikimedia_commons_images("Harmanpreet Kaur cricket")
        if commons:
            img_url = commons[0]["url"]

    if not img_url:
        img_url = fetch_wikipedia_person_image("Smriti Mandhana")
        img_caption = "Smriti Mandhana, India's vice-captain for the Women's T20 World Cup"

    if not img_url:
        img_url = fetch_pexels_image("women cricket players India")
        img_attribution = "Pexels"
        img_caption = "Women cricketers in action during an international match"

    if img_url and not validate_image(img_url):
        print("  Primary image failed validation, trying alternatives...")
        img_url = fetch_pexels_image("cricket women sport")
        img_attribution = "Pexels"
        img_caption = "Women cricketers competing in an international match"

    headline = "Harmanpreet Will Lead India at a Fifth T20 World Cup. This Time, She Has Nandni Sharma and a Point to Prove."
    subheadline = "India's 15-player squad for the Women's T20 World Cup in England features a maiden call-up for Chandigarh pacer Nandni Sharma, the return of Yastika Bhatia and Radha Yadav, and a team that has won just three of its last eight T20Is."
    slug = "india-women-t20-world-cup-2026-squad-harmanpreet-kaur-nandni-sharma-england-preview-nri"

    body = """The ICC Women's T20 World Cup begins on June 12 in England, and India will arrive with a complicated record and a new face. Nandni Sharma, a 24-year-old pacer from Chandigarh, has earned her first international call-up after finishing as the joint-highest wicket-taker in her debut WPL season, picking up 17 wickets for Delhi Capitals. She is the one uncapped player in Harmanpreet Kaur's squad, and her inclusion signals what the selectors are thinking: India's pace attack needed reinforcement.

## A Squad Built for English Conditions

The 15-player squad, announced by the BCCI on May 2, blends experience with tactical adjustments:

**Batters:** Harmanpreet Kaur (c), Smriti Mandhana (vc), Shafali Verma, Jemimah Rodrigues, Yastika Bhatia, Bharti Fulmali

**All-rounders:** Deepti Sharma, Shreyanka Patil, Radha Yadav, Kranti Gaud

**Wicketkeeper:** Richa Ghosh

**Bowlers:** Arundhati Reddy, Renuka Thakur, Shree Charani, Nandni Sharma

The return of Yastika Bhatia gives India a left-handed middle-order option they lacked in the South Africa series. Radha Yadav's recall bolsters the spin department alongside Deepti Sharma, Shree Charani, and Shreyanka Patil — a four-pronged slow-bowling attack designed for pitches in Birmingham and London that should offer grip.

Kashvee Gautam, the exciting young all-rounder, missed out due to a right knee injury. Anushka Sharma and Uma Chetry were the other notable omissions.

## The Form Problem

India have won just three of their last eight T20Is. Four defeats came in the recently concluded five-match series against South Africa, a sequence that exposed vulnerabilities in the batting order's ability to chase under pressure and in the death bowling.

Since the 2024 T20 World Cup, where India exited in the group stage, Harmanpreet's team has won 13 of 21 T20Is — a win rate that does not inspire the confidence expected of a side that holds the 50-over World Cup title. The question in England will be whether the team can convert the talent on the roster into results under tournament conditions.

## India vs Pakistan on June 14

India open their Group 1 campaign against Pakistan on June 14 at Edgbaston in Birmingham — a ground with deep significance for Indian cricket fans, and one where the diaspora regularly fills the stands. The match starts at 7:00 PM BST (11:30 PM IST), and for NRI fans in the UK, it will be the most accessible fixture of the tournament.

India's full Group 1 schedule:

- **June 14** — India vs Pakistan, Edgbaston, Birmingham
- **June 17** — India vs Netherlands, Edgbaston, Birmingham
- **June 21** — India vs South Africa, The Oval, London
- **June 24** — India vs Bangladesh, The Oval, London
- **June 27** — India vs Australia, Lord's, London

The group is loaded. Australia, South Africa, and Pakistan all have realistic ambitions, and only four of the six teams advance to the Super 8s. India cannot afford a slow start.

## What NRI Fans Should Know

For the Indian diaspora in England, this is the most accessible women's cricket tournament in years. All of India's group matches are at Edgbaston or the London grounds — The Oval and Lord's — with tickets starting at £10 for group-stage fixtures. The tournament runs until July 5, with the final at Lord's.

For diaspora fans in North America, all matches will be available on Willow TV and the ICC's digital platforms. The India-Pakistan match falls on a Saturday afternoon in UK time, which translates to early evening IST and late morning across US time zones.

Harmanpreet has led India in every T20 World Cup since the format began expanding. This will be her fifth time captaining the side in the tournament. At 37, it could well be her last. She will want it to count.

*Sources: Cricbuzz, ICC, SuperSport, BCCI*"""

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "is_editorial": False,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url or "",
        "image_caption": img_caption,
        "image_attribution": img_attribution,
        "sources": json.dumps(["Cricbuzz", "ICC", "SuperSport", "BCCI"]),
    }

    if not img_url:
        print("  ⚠ No valid image found — skipping article")
        return False

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=== The Videshi Sports Writer ===")
    print(f"Run time: {datetime.now(timezone.utc).isoformat()}")

    success_count = 0
    if write_article_1():
        success_count += 1
    if write_article_2():
        success_count += 1

    print(f"\n=== Done: {success_count}/2 articles published ===")
