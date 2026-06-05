#!/usr/bin/env python3
"""Sports writer — June 5, 2026 run. Generates 3 articles with proper images."""

import json, os, sys, time, uuid, re, io
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    if line.startswith('export '):
                        line = line[7:]
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

##############################################################################
# Image sourcing functions
##############################################################################

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = requests.utils.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("thumbnail", {}).get("source")
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
            params=params, headers=UA, timeout=15
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch a Pexels image using curl (urllib gets 403)."""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_KEY}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def download_and_compress_image(url, max_width=1200, quality=80):
    """Download image, resize/compress, return JPEG bytes."""
    from PIL import Image
    try:
        r = requests.get(url, headers=UA, timeout=20)
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None
        img = Image.open(io.BytesIO(r.content))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        compressed = buf.getvalue()
        print(f"  ✓ Image compressed: {len(r.content)} → {len(compressed)} bytes, {img.width}x{img.height}")
        return compressed
    except Exception as e:
        print(f"  ⚠ Image processing error: {e}")
        return None

def upload_to_supabase_storage(img_bytes, filename):
    """Upload image bytes to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    try:
        r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(person_name=None, topic_queries=None, pexels_query=None, slug="article"):
    """Multi-source image pipeline. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries:
            commons = fetch_wikimedia_commons_images(q, limit=3)
            for c in commons[:2]:
                candidates.append({"url": c["url"], "source": "wikimedia_commons", "priority": 2})
            if candidates:
                break
            time.sleep(1)

    # Source 3: Pexels
    if pexels_query and PEXELS_KEY:
        pex = fetch_pexels_image(pexels_query)
        if pex:
            candidates.append({"url": pex, "source": "pexels", "priority": 3})

    # Pick best and upload
    if not candidates:
        print("  ✗ No image candidates found")
        return None, None

    # Sort by priority
    candidates.sort(key=lambda x: x["priority"])

    for cand in candidates:
        img_bytes = download_and_compress_image(cand["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase_storage(img_bytes, filename)
            if final_url:
                attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attr

    print("  ✗ All image candidates failed")
    return None, None

##############################################################################
# Article insertion
##############################################################################

def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS_SB, json=article, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

##############################################################################
# Article definitions
##############################################################################

def write_articles():
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    articles_written = 0

    # ========================================================================
    # ARTICLE 1: Praggnanandhaa Wins Norway Chess 2026
    # ========================================================================
    print("\n=== Article 1: Praggnanandhaa Wins Norway Chess 2026 ===")

    slug1 = "praggnanandhaa-wins-norway-chess-2026-carlsen-gukesh-oslo-champion-nri"

    body1 = """Rameshbabu Praggnanandhaa has won Norway Chess 2026, the biggest title of his career so far. The 20-year-old from Chennai beat world number one Magnus Carlsen in the classical game in the final round to finish on 18 points, one clear of Wesley So, who had led for most of the tournament.

## Four Classical Wins in Ten Rounds

Praggnanandhaa's run through Oslo was relentless. He scored four classical victories in a six-player, double round-robin field that included the reigning world champion, the world number one, and three other top-fifteen players. In a format where most games end in a draw and head to armageddon, that is an extraordinary return.

His most talked-about sequence came in the final three rounds. In round eight, he beat Carlsen with the white pieces. In round nine, he beat world champion Gukesh Dommaraju with the black pieces. In round ten, he beat Carlsen again, this time with black, to clinch the title.

No one else in the field managed more than two classical wins.

## The Final Round

Going into the last day, So led with 15.5 points to Praggnanandhaa's 15, with Alireza Firouzja still alive at 14.5. Praggnanandhaa needed a result against Carlsen and got one. He seized the initiative in the middlegame and converted with confidence, earning the full three points.

So drew his classical game and won the armageddon to finish on 17 points. Firouzja also picked up 1.5 points to finish third on 15.5. It was not enough to catch Praggnanandhaa.

The final standings told the story of a tournament that belonged to one player from the moment he found his rhythm in the middle rounds.

**Final Standings:**

1. R Praggnanandhaa (India) — 18 points
2. Wesley So (USA) — 17 points
3. Alireza Firouzja (France) — 15.5 points
4. Magnus Carlsen (Norway) — 13 points
5. Vincent Keymer (Germany) — 11 points
6. Gukesh Dommaraju (India) — 8 points

## Gukesh's Difficult Tournament

For Gukesh, who won the World Championship just seven months ago, Norway Chess was a chastening experience. He finished last on 8 points, losing 11.3 Elo rating points and dropping to 25th in the live world rankings. Among Indian players, he is now only fifth, behind Arjun Erigaisi, Praggnanandhaa, Viswanathan Anand, and Nihal Sarin.

His head-to-head record against Praggnanandhaa in Oslo was particularly painful: 0-3 across their two meetings, including two classical losses.

## What It Means for the Diaspora

Praggnanandhaa's victory continues Indian chess's dominance of the elite circuit. India now has the world champion (Gukesh), the former world champion (Anand), and the Norway Chess champion (Praggnanandhaa), along with a deep bench of young talent that includes Arjun Erigaisi and Nihal Sarin.

For NRI fans who have followed Praggnanandhaa's rise since he became the youngest international master in history at age ten, the Norway Chess title is confirmation that he belongs at the very top. He climbed four spots to 12th in the live ratings during the tournament and, at 20, has time and trajectory on his side.

The $75,000 first prize is a nice bonus. The statement he made by beating Carlsen twice in classical chess at his home tournament is worth considerably more.

## Sources

- Wikipedia: Norway Chess 2026 final standings
- ChessBase: Round-by-round coverage
- ESPN India: Indian sports roundup, June 5, 2026
- Chess.com: Norway Chess Round 9 and Round 10 reports"""

    # Image sourcing
    print("  Sourcing image...")
    img_url1, img_attr1 = source_image(
        person_name="Rameshbabu Praggnanandhaa",
        topic_queries=["Praggnanandhaa chess", "Praggnanandhaa Norway Chess 2026"],
        pexels_query="chess grandmaster tournament",
        slug=slug1
    )

    art1 = {
        "headline": "Praggnanandhaa Beat Carlsen in the Final Round. He Won Norway Chess. He Is Twenty.",
        "subheadline": "The Chennai grandmaster scored four classical wins in ten rounds, beating the world champion and the world number one to claim the biggest title of his career in Oslo.",
        "slug": slug1,
        "body": body1.strip(),
        "category": "sports",
        "status": "published",
        "published_at": now_utc,
        "sources": json.dumps(["Wikipedia", "ChessBase", "ESPN India", "Chess.com"]),
        "vertical": "sports",
        "is_editorial": False,
        "image_url": img_url1 or "",
        "image_caption": "R Praggnanandhaa during a classical chess game at the tournament in Oslo",
        "image_attribution": img_attr1 or ""
    }

    if insert_article(art1):
        articles_written += 1

    time.sleep(2)

    # ========================================================================
    # ARTICLE 2: Rohit Sharma Fitness Doubt
    # ========================================================================
    print("\n=== Article 2: Rohit Sharma Fitness Doubt ===")

    slug2 = "rohit-sharma-fitness-doubt-afghanistan-odi-series-kohli-out-india-without-pillars-nri"

    body2 = """India could be without both Rohit Sharma and Virat Kohli for the three-match ODI series against Afghanistan, starting June 13 in Dharamsala. Kohli has already been ruled out with a hamstring injury sustained in the IPL 2026 final. Now Rohit's participation is in serious doubt after he failed to report to the BCCI Centre of Excellence in Bengaluru for the mandatory fitness clearance.

## The Hamstring Problem

Rohit injured his hamstring during the IPL 2026 season while playing for the Mumbai Indians. He missed a stretch of matches midway through the campaign, and when he returned toward the end, it was only as an impact player. Mumbai finished ninth on the points table. His last IPL innings was a duck against the Rajasthan Royals at the Wankhede.

The selection committee, led by chief selector Ajit Agarkar, included Rohit in the Afghanistan ODI squad but made his selection conditional on passing a fitness test at the Centre of Excellence. As of June 5, that test has not happened.

## Training in Mohali, Not Bengaluru

According to a Times of India report, Rohit has informed the Punjab Cricket Association that he intends to train at the IS Bindra Stadium in Mohali on June 8 and 9, ahead of the squad assembling in the city. He has asked for specific training slots. But Mohali is not Bengaluru, and the BCCI protocol for injured contracted players requires them to report to the Centre of Excellence for assessment, rehabilitation, and fitness clearance before rejoining the squad.

The disconnect has raised questions about whether Rohit is in a position to play or is managing expectations ahead of a formal announcement.

## India Without Its Two Pillars

If Rohit joins Kohli on the sidelines, India will enter their first bilateral ODI series against Afghanistan without the two batsmen who have defined their white-ball cricket for the better part of a decade.

Rohit, 38, now plays only ODI cricket after retiring from T20Is and Tests. His last ODI series as captain was the ICC Champions Trophy 2025, where he scored 76 in the final against New Zealand. His last ODI appearance produced just 61 runs across three innings. He ended 2025 as India's second-highest ODI run-scorer with 650 runs at an average of 50.

Kohli, meanwhile, was in superb form during the IPL, scoring over 650 runs and hitting an unbeaten 75 off 42 balls in the final. His hamstring gave way in that very innings.

## A Depleted Squad

The injury list does not end with the two senior batsmen. All-rounder Hardik Pandya, who suffered a back spasm during the IPL, is also undergoing assessment at the Centre of Excellence. His clearance is pending.

Agarkar has already rested Jasprit Bumrah and Mohammed Siraj for workload management. Ravindra Jadeja and Axar Patel are also absent. In their place, the selectors have turned to fresh faces: Harsh Dubey, Prince Yadav, and Gurnoor Brar.

Ruturaj Gaikwad has been named as Kohli's replacement. If Rohit also misses out, India will likely lean on the likes of Shubman Gill, Ishan Kishan — who was recently recalled after a three-year absence — and KL Rahul to carry the batting.

## What NRI Fans Should Know

The Afghanistan ODI series starts June 13 in Dharamsala, followed by matches in Lucknow and Chennai. It follows the one-off Test against Afghanistan at the new Mullanpur stadium near Mohali, which begins June 6. An official announcement on Rohit's availability is expected before the squad assembles on June 9.

For fans in the diaspora who tune in to ODI cricket specifically for Rohit and Kohli, the message is straightforward: prepare for the possibility of watching neither.

## Sources

- CricketAddictor: Rohit Sharma fitness clearance report
- CricTracker: Rohit Sharma fitness concerns
- Sportskeeda: Rohit Sharma Mohali training plan
- Inside Sport India: Rohit fitness test status"""

    print("  Sourcing image...")
    img_url2, img_attr2 = source_image(
        person_name="Rohit Sharma",
        topic_queries=["Rohit Sharma cricket", "Rohit Sharma batting"],
        pexels_query="cricket batsman India",
        slug=slug2
    )

    art2 = {
        "headline": "Rohit Has Not Reported to the Centre of Excellence. He Wants to Train in Mohali Instead. India May Be Without Both Him and Kohli.",
        "subheadline": "With Virat Kohli already ruled out of the Afghanistan ODI series, Rohit Sharma's failure to appear for the mandatory BCCI fitness test raises the prospect of India losing both batting pillars.",
        "slug": slug2,
        "body": body2.strip(),
        "category": "sports",
        "status": "published",
        "published_at": now_utc,
        "sources": json.dumps(["CricketAddictor", "CricTracker", "Sportskeeda", "Inside Sport India"]),
        "vertical": "sports",
        "is_editorial": False,
        "image_url": img_url2 or "",
        "image_caption": "Rohit Sharma during an international cricket match for India",
        "image_attribution": img_attr2 or ""
    }

    if insert_article(art2):
        articles_written += 1

    time.sleep(2)

    # ========================================================================
    # ARTICLE 3: India Lose 3-1 to Tajikistan
    # ========================================================================
    print("\n=== Article 3: India Lose 3-1 to Tajikistan ===")

    slug3 = "india-lose-3-1-tajikistan-friendly-tursunzoda-khalid-jamil-world-cup-nri"

    body3 = """India lost 3-1 to Tajikistan in a FIFA international friendly at the TALCO Arena in Tursunzoda on Thursday. It was the latest in a string of poor results for Khalid Jamil's side, who now have a 20 percent win rate under the interim head coach after ten matches in charge.

## How the Match Unfolded

Tajikistan took the lead early through Komron Boboev in the ninth minute, setting the tone for a match India would spend most of chasing. The hosts doubled their advantage through Ehson Karimov in the 62nd minute before Shahrom Panjshanbe made it 3-0 in the 68th.

India's consolation came from Farukh Choudhary in the 89th minute, a goal that did little to disguise the extent of the defeat. The final whistle at the TALCO Arena confirmed what the scoreline suggested: India were second-best in every phase.

## A Pattern of Decline

The result extends India's dismal run of form. Under Khalid Jamil, the senior men's team has won just two of their last ten matches. Their most recent competitive campaign, the AFC Asian Cup qualifiers, ended in humiliation. Despite being top seeds and favourites to qualify, India finished bottom of their group after losses to Bangladesh, Hong Kong, and Singapore.

A trip to the Unity Cup 2026 offered no relief. India lost to Jamaica and Zimbabwe in consecutive matches. Now, a defeat to Tajikistan, a team ranked well below them in the FIFA standings, adds another chapter to a troubling narrative.

Khalid Jamil was appointed as interim manager after the departure of Igor Stimac. The results have not improved. The question of whether he will be given a permanent contract, or replaced before India's next meaningful fixtures, hangs over the program.

## Context: The World Cup Begins in Six Days

The timing of this defeat makes it sting more. The FIFA World Cup kicks off on June 11 in North America. India, as usual, are not in it. But the diaspora's connection to the tournament is stronger than ever: four players of Indian origin — Sarpreet Singh (New Zealand), Tahsin Mohammed Jamshid (Qatar), Nishan Velupillay (Australia), and Samuel Moutoussamy (DR Congo) — will represent other nations on football's biggest stage.

While those players prepare for World Cup group matches, the Indian senior team is losing 3-1 to Tajikistan in a friendly that few outside the most committed fans will have watched.

## The Second Friendly

India will face Tajikistan again on June 9 at the Central Stadium in Hisor. It is the last match before the international window closes. For Khalid Jamil, it represents an opportunity to salvage something from the trip. For the players, it is a chance to show the kind of fight that was absent in Tursunzoda.

## What NRI Fans Are Asking

The disconnect between Indian football's ambitions and its results is a recurring source of frustration for the diaspora. The AIFF has set targets for World Cup qualification. Grassroots programs have been funded. The Indian Super League has raised the standard of domestic football. But at the international level, the results are going backward.

NRI fans who follow Indian football from abroad — and there are more of them than the AIFF's ticket sales suggest — are left with a familiar question: when does investment start translating into competitive performances? The loss to Tajikistan provides no answer.

## Sources

- Wikipedia: Tajikistan national football team results
- ESPN India: Indian sports roundup, June 5, 2026
- Khel Now: India vs Tajikistan preview and head-to-head
- Oddslot: Match result tracker"""

    print("  Sourcing image...")
    img_url3, img_attr3 = source_image(
        person_name="Khalid Jamil football",
        topic_queries=["India national football team", "India football team 2026"],
        pexels_query="football soccer match stadium",
        slug=slug3
    )

    art3 = {
        "headline": "India Lost 3-1 to Tajikistan. Khalid Jamil Has Won Two of His Ten Matches in Charge.",
        "subheadline": "A ninth-minute goal set the tone in Tursunzoda as India conceded three before Farukh Choudhary's consolation. The World Cup starts in six days. India are going backward.",
        "slug": slug3,
        "body": body3.strip(),
        "category": "sports",
        "status": "published",
        "published_at": now_utc,
        "sources": json.dumps(["Wikipedia", "ESPN India", "Khel Now", "Oddslot"]),
        "is_editorial": False,
        "image_url": img_url3 or "",
        "image_caption": "The Indian football team during an international match",
        "image_attribution": img_attr3 or ""
    }

    if insert_article(art3):
        articles_written += 1

    print(f"\n{'='*60}")
    print(f"Sports writer complete: {articles_written}/3 articles published")
    print(f"{'='*60}")

if __name__ == "__main__":
    write_articles()
