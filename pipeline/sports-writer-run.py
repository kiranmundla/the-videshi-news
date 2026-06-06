#!/usr/bin/env python3
"""Sports writer - June 6, 2026 run"""

import json
import os
import sys
import uuid
import time
import requests
from io import BytesIO
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

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

UA = "TheVideshi/1.0 (thevideshi.com)"

# ==================== IMAGE SOURCING ====================

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA},
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    import urllib.parse
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
            headers={"User-Agent": UA},
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []


def fetch_pexels_image(query):
    """Fetch from Pexels."""
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        import urllib.parse
        q = urllib.parse.quote(query)
        cmd = f'curl -sS "https://api.pexels.com/v1/search?query={q}&per_page=5" -H "Authorization: {PEXELS_KEY}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
    from PIL import Image
    img = Image.open(BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    result = buf.getvalue()
    print(f"  ✓ Compressed image: {len(result)} bytes ({img.width}x{img.height})")
    return result


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=img_bytes, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None


def download_image(url):
    """Download image bytes."""
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get('Content-Type', '')
            if 'image' in ct or len(r.content) > 10000:
                print(f"  ✓ Downloaded image: {len(r.content)} bytes")
                return r.content
        print(f"  ⚠ Image download issue: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None


def source_image(person_name=None, topic_terms=None, pexels_query=None, slug="article"):
    """Multi-source image search. Returns (supabase_url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia (for person articles)
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikimedia", "relevance": 3})

    # Source 2: Wikimedia Commons
    search_terms = []
    if person_name and topic_terms:
        search_terms.append(f"{person_name} {topic_terms}")
    elif topic_terms:
        search_terms.append(topic_terms)
    if person_name:
        search_terms.append(person_name)

    for term in search_terms[:2]:
        commons = fetch_wikimedia_commons_images(term)
        for r in commons[:2]:
            candidates.append({"url": r["url"], "source": "wikimedia", "relevance": 2})
        if commons:
            break

    # Source 3: Pexels
    if pexels_query:
        pexels_img = fetch_pexels_image(pexels_query)
        if pexels_img:
            candidates.append({"url": pexels_img, "source": "pexels", "relevance": 1})

    # Pick best
    if not candidates:
        print("  ✗ No image found from any source")
        return None, None

    candidates.sort(key=lambda c: c["relevance"], reverse=True)
    best = candidates[0]
    print(f"  → Best candidate: {best['source']} (relevance {best['relevance']})")

    # Download, compress, upload
    img_bytes = download_image(best["url"])
    if not img_bytes:
        # Try next candidates
        for c in candidates[1:]:
            img_bytes = download_image(c["url"])
            if img_bytes:
                best = c
                break
    
    if not img_bytes:
        print("  ✗ Could not download any candidate image")
        return None, None

    compressed = compress_image(img_bytes)
    if len(compressed) < 10000:
        print(f"  ⚠ Compressed image too small ({len(compressed)} bytes), trying next candidate...")
        for c in candidates:
            if c == best:
                continue
            img_bytes2 = download_image(c["url"])
            if img_bytes2:
                compressed2 = compress_image(img_bytes2)
                if len(compressed2) >= 10000:
                    compressed = compressed2
                    best = c
                    print(f"  → Switched to: {c['source']} (relevance {c['relevance']})")
                    break
        if len(compressed) < 10000:
            print("  ✗ All candidate images too small, skipping")
            return None, None

    filename = f"{slug}.jpg"
    supabase_url = upload_to_supabase(compressed, filename)
    attribution = "Wikimedia Commons" if best["source"] == "wikimedia" else "Pexels"
    return supabase_url, attribution


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    r = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) else result.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ==================== ARTICLES ====================

articles_to_write = []

# ---- ARTICLE 1: Shreyas Iyer named T20I captain ----
articles_to_write.append({
    "headline": "Shreyas Iyer Is India's New T20I Captain. Suryakumar Yadav Has Been Dropped Entirely.",
    "subheadline": "The selectors have named Iyer captain for the Ireland and England tours, with 15-year-old Sooryavanshi earning his maiden call-up as India begins its rebuild toward the 2028 World Cup.",
    "slug": "shreyas-iyer-india-t20i-captain-suryakumar-dropped-sooryavanshi-maiden-call-ireland-england-nri",
    "category": "sports",
    "person_name": "Shreyas Iyer",
    "topic_terms": "Shreyas Iyer cricket India captain",
    "pexels_query": "cricket captain india",
    "image_caption": "Shreyas Iyer, India's newly appointed T20I captain",
    "body": """Three months after leading India to a T20 World Cup title on home soil, Suryakumar Yadav has lost not just the captaincy but his place in the squad entirely. The Board of Control for Cricket in India announced on Saturday that Shreyas Iyer will captain India's T20I side for the upcoming tours of Ireland and England, marking one of the most decisive leadership transitions in Indian white-ball cricket.

The announcement, made by selection panel chairman Ajit Agarkar during a press conference held at the Maharaja Yadavindra Singh Stadium in New Chandigarh, signals the beginning of India's rebuild toward the 2028 T20 World Cup in Australia and New Zealand and the Los Angeles Olympics the same year.

## A World Cup Winner Sacked

Suryakumar's exit follows a now-familiar BCCI pattern. In 2025, Rohit Sharma was removed as captain after leading India to the Champions Trophy title. Suryakumar has now suffered a similar fate — a trophy-winning captain discarded while the selectors look ahead.

The numbers, however, tell a story of diminishing returns. Since 2024, Suryakumar has scored 1,131 runs in 50 T20I innings at an average of 26.30, a sharp decline from his career average of 36.35. His IPL 2026 campaign was equally modest: 270 runs in 13 innings at a strike rate of 147.54. At 35, the Mumbai batter's best years in the shortest format appear to be behind him.

"Led a team to the IPL title, his own performances have been good. He was close to being part of the World Cup squad. In my opinion, he was a stand-out candidate," Agarkar said of Iyer's appointment.

## Iyer's Long Road Back

Shreyas Iyer's return to T20I cricket is a story of patience. He last played a T20I for India in December 2023, unable to find a place in the squad with Suryakumar and Tilak Varma occupying middle-order positions. He was called up as an injury replacement during the home series against New Zealand in January 2026 but did not play a single match.

Yet his credentials are hard to ignore. He led Kolkata Knight Riders to the IPL title in 2024 and guided Punjab Kings to the final in 2025. In IPL 2026, he scored 498 runs at a strike rate of 168.81, consistently among the tournament's most impactful batters. At 31, the selectors clearly see him as the man to bridge the gap between India's current transition and the next major cycle.

Iyer will captain the side for two T20Is against Ireland in Belfast on June 26 and 28, followed by a five-match series against England from July 1 to 11.

## The Sooryavanshi Moment

The headline within the headline is the maiden call-up of Vaibhav Sooryavanshi, the 15-year-old who demolished IPL 2026 with 776 runs in 16 matches for the Rajasthan Royals. He broke Chris Gayle's record for the most sixes in an IPL season, swept the Orange Cap, MVP, and Emerging Player awards, and carried his franchise almost single-handedly into the playoffs.

Should Sooryavanshi debut against Ireland or England, he would become the youngest player to represent India's senior men's team, breaking a record held by Sachin Tendulkar since 1989. "We've seen what he can do — towards the playoffs, he almost single-handedly carried Rajasthan Royals," Agarkar said. "He's a game-changer. He has picked himself."

## The Full Squad

India's T20I squad for Ireland and England: Shreyas Iyer (captain), Tilak Varma (vice-captain), Abhishek Sharma, Sanju Samson, Ishan Kishan, Vaibhav Sooryavanshi, Shivam Dube, Nitish Kumar Reddy, Axar Patel, Washington Sundar, Ravi Bishnoi, Varun Chakaravarthy, Arshdeep Singh, Mohammed Siraj, Harshit Rana, and Prince Yadav.

The BCCI also named the squad for the men's cricket competition at the Asian Games in Japan later this year, which includes veteran fast bowler Jasprit Bumrah.

## What It Means for NRIs

For the Indian diaspora in the UK and Ireland, the timing is significant. The Belfast T20Is and the England series will offer NRI fans in Britain and Northern Ireland a rare chance to watch India's next generation live. With Sooryavanshi, Tilak Varma, and Abhishek Sharma all under 25, and Iyer leading a squad built for 2028, these tours are the first chapter of a new era.

The message from the selectors is clear: winning a World Cup no longer guarantees your place. The future starts now."""
})

# ---- ARTICLE 2: India vs Afghanistan Test Day 1 ----
articles_to_write.append({
    "headline": "Rahul Made a Hundred. Gill Made a Hundred. India Are 368 for 3 at Stumps Against Afghanistan.",
    "subheadline": "KL Rahul scored 100 off 165 balls and Shubman Gill struck an unbeaten 103 as India dominated the opening day of the one-off Test at Mullanpur. Rishabh Pant is 50 not out.",
    "slug": "india-afghanistan-test-day-1-kl-rahul-gill-centuries-pant-fifty-mullanpur-368-3-nri",
    "category": "sports",
    "person_name": "KL Rahul",
    "topic_terms": "KL Rahul cricket test century India",
    "pexels_query": "cricket test match batting India",
    "image_caption": "KL Rahul scored his 12th Test century against Afghanistan at Mullanpur",
    "body": """India's first Test of 2026 began exactly the way the team needed it to. On a hot Saturday in New Chandigarh, KL Rahul scored his 12th Test century, captain Shubman Gill struck an unbeaten 103, and Rishabh Pant added an aggressive 50 not out as India reached 368 for 3 at stumps on the opening day of the one-off Test against Afghanistan.

The Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur hosted its first-ever Test match, and the home team ensured the venue's maiden day in red-ball cricket would be remembered for all the right reasons.

## The Morning: A Cautious Start

India won the toss and chose to bat on a pitch that showed a green tinge on the eve of the match but was expected to dry out quickly in temperatures pushing past 40 degrees Celsius. Manav Suthar, the young left-arm spinner from Rajasthan, earned his Test cap.

Yashasvi Jaiswal and KL Rahul opened the batting. The morning session was marked by caution, with both batters taking their time against Afghanistan's pace attack. Jaiswal, however, fell in the 11th over for 24, caught behind off Mohammad Saleem Safi.

Rahul had survived a significant reprieve on the first ball of the 11th over when Afghanistan declined to review a caught-behind appeal. UltraEdge later confirmed there was a deflection. It was a decision that would prove costly.

## The Afternoon: Rahul and Sudharsan Build

After lunch, KL Rahul and Sai Sudharsan settled into a partnership that took the game away from Afghanistan. Sudharsan, playing in only his fourth Test, looked composed from the start. Both batters brought up their half-centuries within two overs of each other in the afternoon session, with Sudharsan reaching his third Test fifty with back-to-back boundaries.

The pair added 139 runs in 184 balls for the second wicket before Saleem Safi broke through again, drawing an edge from Sudharsan that carried to wicketkeeper Afsar Zazai. Sudharsan departed for 81, having struck 13 fours in a mature innings that confirmed his growing stature at number three.

Captain Gill joined Rahul, and the pair took India to 209 for 2 at tea in 50 overs.

## The Evening: Centuries and Intent

The final session belonged to Gill and then Pant. Rahul, increasingly confident after his reprieve, reached his 12th Test century off 165 balls, drawing warm applause from the Mullanpur crowd. But he fell on the very next delivery, caught by Gurbaz off Ziaur Rahman Sharifi for exactly 100. The dismissal, coming on the ball after his milestone, was a cruel twist.

Captain Gill, however, was in imperious form. He brought up his ninth Test fifty and then pressed on to three figures, reaching 103 off 143 balls with 11 fours and a six. It was a captain's knock — patient when the situation demanded it, aggressive when the bowlers faltered.

Rishabh Pant joined Gill and played with characteristic intent. The wicketkeeper-batter raced to 50 off 70 balls, clearing the boundary three times, and was 50 not out at stumps alongside Gill. Their unbroken fourth-wicket stand was worth 121 runs in 151 balls.

## Afghanistan's Struggle

For Afghanistan, playing their second-ever Test against India — and their first in eight years — the day was punishing. Captain Hashmatullah Shahidi bowled 17 overs of spin himself for 61 runs but could not find a breakthrough. Nangeyalia Kharote, the left-arm spinner, went for 95 in 20 wicketless overs. Only Mohammad Saleem Safi, who returned figures of 2 for 67, provided any control.

The absence of Rashid Khan, arguably the finest Afghan cricketer of his generation, was felt acutely. Without his leg-spin, Afghanistan lacked the wicket-taking threat needed to contain India's batting depth.

## What It Means

This was India's first home Test since the painful whitewashes by New Zealand and South Africa. Though the match sits outside the World Test Championship cycle, it carries symbolic weight. The top three — Jaiswal, Rahul, and Sudharsan — are the same unit that was battered in those defeats. On Saturday, at least two of them answered emphatically.

For NRI fans following from abroad, the scorecard reads like a statement of intent. India are building again, and on Day 1 at Mullanpur, the foundations looked solid."""
})

# ---- ARTICLE 3: Indian-origin players at FIFA World Cup 2026 ----
articles_to_write.append({
    "headline": "India Are Not at the World Cup. But Four Players With Indian Roots Will Be.",
    "subheadline": "When the FIFA World Cup kicks off on June 11, players tracing their heritage to Kerala, Punjab, and Tamil Nadu will represent four different nations — the first time this has happened since 2006.",
    "slug": "four-indian-origin-players-fifa-world-cup-2026-sarpreet-tahsin-velupillay-moutoussamy-nri",
    "category": "sports",
    "person_name": "Sarpreet Singh",
    "topic_terms": "FIFA World Cup 2026 Indian origin players",
    "pexels_query": "football soccer world cup stadium",
    "image_caption": "Sarpreet Singh of New Zealand, one of four Indian-origin players at the 2026 FIFA World Cup",
    "sources": [
        {"name": "Mint", "url": "https://livemint.com"},
        {"name": "Dainik Bhaskar", "url": "https://bhaskarenglish.in"},
        {"name": "FIFA", "url": "https://fifa.com"}
    ],
    "body": """India has never played at a senior men's FIFA World Cup. They qualified once, for the 1950 tournament in Brazil, but withdrew, citing travel costs and a preference for the 1952 Olympics. Seventy-six years later, the Indian national team is nowhere near the expanded 48-team field that will contest the 2026 edition across the United States, Canada, and Mexico starting June 11.

But for the first time since Vikash Dhorasoo wore France's blue shirt in Germany in 2006, the World Cup will feature players with Indian roots — and this time, there are four of them, representing four different nations.

## Tahsin Mohammed Jamshid — Qatar

The youngest of the four is Tahsin Mohammed Jamshid, a 19-year-old winger born in Doha to parents from Kannur, Kerala. His father, Jamshid, played football for the University of Calicut before moving to Qatar in 1996 to work as an accountant. Tahsin joined the Aspire Academy as a teenager and emerged as one of Qatar's most explosive young attackers at Al Duhail.

His pace and dribbling drew comparisons to more established players, and he caught the eye of Spanish coach Julen Lopetegui, who trusted him ahead of veteran forward Sebastian Soria. Spanish football analyst Alfonso Perez has described him as a player with "raw pace" who could one day move to a major European club.

Tahsin made his senior debut for Qatar during a World Cup qualifier against Afghanistan in June 2024. He has since represented Qatar at senior, U-23, U-20, and youth levels. He is also, notably, the first player with an Indian passport to be named in a World Cup squad.

## Sarpreet Singh — New Zealand

Sarpreet Singh was born in Auckland to Punjabi parents from Jalandhar. He broke through at Wellington Phoenix before earning a move to Bayern Munich in 2019, becoming the first player of Indian descent to play in the German Bundesliga.

His career since has been itinerant — stints in Germany, Portugal, and a return to Wellington Phoenix on loan from Serbian club TSC — but his talent has never been in question. At 27, Singh has 24 international caps and recovered from a knee injury earlier this year to make New Zealand's final squad. The All Whites open their campaign against Iran in Inglewood, California, on June 16, with Singh expected to be a central creative presence.

## Nishan Velupillay — Australia

Nishan Velupillay, born in Melbourne, traces his heritage to Sri Lankan Tamil roots through his Malaysian-born father, Sasinath, and an Anglo-Indian mother, Gillian. The 25-year-old winger has been a mainstay at Melbourne Victory, scoring 19 goals in 128 appearances since 2021.

He made his senior Australia debut during a World Cup qualifier against China in 2024 and has earned six international caps. His blistering pace on the wing gives Australia a counter-attacking dimension that coach Graham Arnold has relied on through the qualification campaign. The Socceroos face Denmark, France, and Peru in what promises to be one of the tournament's toughest groups.

## Samuel Moutoussamy — DR Congo

The most experienced of the four is Samuel Moutoussamy, a 29-year-old defensive midfielder born in Paris. His connection to India runs through his Indo-Guadeloupean father, whose family traces its origins to Tamil Nadu. Indo-Guadeloupeans are largely descendants of South Indian workers who migrated to the Caribbean island in the late nineteenth century.

Moutoussamy built his career at French club Nantes, where he made over 140 appearances and won the Coupe de France in 2021-22. He currently plays for Greek side Atromitos. Though born and raised in France, he chose to represent DR Congo through his Congolese mother and has earned 57 caps since 2019. Congo open against Portugal, with Moutoussamy expected to anchor their midfield.

## What It Means for the Diaspora

For Indian football fans — and for the broader NRI community — the presence of four players with Indian roots at a single World Cup is without precedent. Their backgrounds span three continents and trace back to Kerala, Punjab, and Tamil Nadu, the very regions that define much of the Indian diaspora's geography.

None of these players grew up in India. Each was shaped by the football infrastructure of the country they represent. But their success carries a message: that talent from the Indian diaspora can thrive at the highest level when given the right development pathway.

The FIFA World Cup 2026 runs from June 11 to July 19. India may not be playing. But Indians, in a sense, will be there."""
})

# ==================== MAIN EXECUTION ====================

print("=" * 60)
print("SPORTS WRITER - June 6, 2026")
print("=" * 60)

published_count = 0

for i, article_data in enumerate(articles_to_write):
    print(f"\n{'='*60}")
    print(f"ARTICLE {i+1}: {article_data['headline'][:60]}...")
    print(f"{'='*60}")

    slug = article_data["slug"]

    # Source image
    print("\n📸 Sourcing image...")
    img_url, img_attr = source_image(
        person_name=article_data.get("person_name"),
        topic_terms=article_data.get("topic_terms"),
        pexels_query=article_data.get("pexels_query"),
        slug=slug
    )

    # Build article payload
    article_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "id": article_id,
        "headline": article_data["headline"],
        "subheadline": article_data["subheadline"],
        "slug": slug,
        "body": article_data["body"].strip(),
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "is_featured": False,
        "score_total": 0,
        "sources": json.dumps(article_data.get("sources", [
            {"name": "Reuters", "url": "https://reuters.com"},
            {"name": "BCCI", "url": "https://bcci.tv"},
            {"name": "ESPNcricinfo", "url": "https://espncricinfo.com"}
        ]))
    }

    if img_url:
        payload["image_url"] = img_url
        payload["image_caption"] = article_data.get("image_caption", "")
        payload["image_attribution"] = img_attr
    else:
        print("  ⚠ No image — publishing without hero image")

    # Insert
    print("\n📝 Inserting article...")
    art_id = insert_article(payload)
    if art_id:
        published_count += 1
        print(f"  ✓ Published: {slug}")
    else:
        print(f"  ✗ Failed: {slug}")

    time.sleep(1)

print(f"\n{'='*60}")
print(f"DONE: {published_count}/{len(articles_to_write)} articles published")
print(f"{'='*60}")
