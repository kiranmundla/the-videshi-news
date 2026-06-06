#!/usr/bin/env python3
"""Sports writer for The Videshi — June 6, 2026 batch."""

import json, os, sys, time, uuid, re, io
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

import requests
from PIL import Image

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase storage bucket 'article-images'."""
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    print(f"  Compressed image: {size_kb:.0f} KB")
    if size_kb < 10:
        print("  ⚠ Image too small after compression, skipping")
        return None

    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
        return None

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
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
                    "mime": mime
                })
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images found for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image."""
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={query}&per_page=3',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        if r.status_code == 200 and r.headers.get('Content-Type', '').startswith('image'):
            if len(r.content) > 5000:
                return r.content
            else:
                print(f"  ⚠ Image too small: {len(r.content)} bytes")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def source_image(person_name, topic_terms, slug):
    """Multi-source image sourcing. Returns (supabase_url, attribution, caption) or Nones."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "person": person_name})

    # Source 2: Wikimedia Commons
    for term in topic_terms:
        commons = fetch_wikimedia_commons_images(term)
        for c in commons[:2]:
            candidates.append({"url": c["url"], "source": "wikimedia_commons", "title": c.get("title", "")})
        if commons:
            break

    # Source 3: Pexels fallback
    if not candidates:
        for term in topic_terms:
            pex = fetch_pexels_image(term)
            if pex:
                candidates.append({"url": pex, "source": "pexels"})
                break

    # Download and upload best candidate
    for cand in candidates:
        print(f"  Trying {cand['source']}: {cand['url'][:80]}...")
        img_bytes = download_image(cand["url"])
        if img_bytes:
            filename = f"{slug}.jpg"
            sb_url = upload_to_supabase(img_bytes, filename)
            if sb_url:
                attr = "Wikimedia Commons" if cand["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return sb_url, attr
    
    print("  ⚠ No image sourced")
    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) and data else "unknown"
        print(f"  ✓ Article inserted: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLES
# ============================================================

articles = []

# -------- ARTICLE 1: Kohli ruled out of Afghanistan ODIs --------
print("\n=== Article 1: Kohli Out of Afghanistan ODIs ===")

art1_slug = "virat-kohli-ruled-out-afghanistan-odi-series-hamstring-injury-gaikwad-replacement-nri"
art1_headline = "Kohli Is Out. He Tore His Hamstring in the IPL Final He Refused to Leave. Now Gaikwad Gets His Chance."
art1_subheadline = "India will be without both Kohli and possibly Rohit Sharma for the first-ever bilateral ODI series against Afghanistan, starting June 13 in Dharamsala."

art1_body = """Virat Kohli has been ruled out of India's three-match ODI series against Afghanistan with a hamstring injury sustained during the IPL 2026 final on May 31. The confirmation, first reported by PTI citing a BCCI source, ends weeks of speculation about the severity of the injury he carried through the final overs of Royal Challengers Bengaluru's title-clinching chase against Gujarat Titans.

## The Injury He Played Through

Those who watched the final at the Narendra Modi Stadium in Ahmedabad saw Kohli receive on-field treatment at least twice. He was visibly limping between runs. None of it stopped him from hitting an unbeaten 75 off 42 deliveries — including the winning six — to hand RCB their second consecutive IPL title. The 25-ball fifty was the fastest of his IPL career.

But the price was steep. The hamstring tear, initially downplayed by the franchise, has now been confirmed as serious enough to rule him out of international duty for at least the Afghanistan series. The BCCI is yet to announce a formal replacement, though Ruturaj Gaikwad is widely expected to slot in at No. 3.

## Gaikwad's Opportunity

Gaikwad has been knocking on the door of India's ODI middle order for over a year. The Maharashtra batter captained Chennai Super Kings through IPL 2026 and ended the season with 487 runs at a strike rate above 140. His ability to anchor an innings while accelerating through the middle overs makes him the most natural replacement for Kohli's role in the batting order.

If selected, it will be Gaikwad's chance to stake a permanent claim ahead of the all-important England tour in July and the 2027 ODI World Cup cycle.

## Rohit's Fitness Still Unclear

The bigger worry for Indian cricket may not be Kohli's absence but the uncertainty around Rohit Sharma. The former all-format captain also sustained a hamstring injury during IPL 2026, missed several matches for Mumbai Indians, and has not yet reported to the BCCI Centre of Excellence in Bengaluru for his mandatory fitness assessment.

Reports suggest Rohit is expected at the CoE on June 8 and will undergo batting sessions under lights before a decision on his availability for the opening ODI on June 13 in Dharamsala. If cleared, he could join the squad in Dharamsala on June 11, just two days before the first match.

If Rohit also misses out, India would face Afghanistan without both pillars of their batting lineup for the first time in a bilateral series. Shubman Gill would likely lead the side, with Yashasvi Jaiswal expected to open alongside him.

## What It Means for NRI Fans

For diaspora fans who planned their viewing around India's marquee names, the series has lost some star power. The Afghanistan series — the first-ever bilateral ODI contest between the two sides — will be played across Dharamsala (June 13), Lucknow (June 15), and Chennai (June 18), with most matches falling in late-night or early-morning windows for viewers in North America.

But there is a silver lining. A Kohli-less, possibly Rohit-less India means younger players get the stage. Gaikwad, Jaiswal, Sudharsan — the next generation will have to carry the batting against an Afghan side that includes Rashid Khan's leg-spin and Fazalhaq Farooqi's left-arm pace.

India's preparation for the 2027 ODI World Cup, to be hosted by South Africa, Zimbabwe, and Namibia, requires exactly this kind of stress-testing. The question is whether the selectors see it that way, or whether they would rather preserve their veterans for England.

**Sources:** PTI, Times of India, CricTracker, InsideSport"""

# Source image for Kohli
img1_url, img1_attr = source_image(
    "Virat Kohli",
    ["Virat Kohli cricket", "Virat Kohli batting IPL"],
    art1_slug
)

articles.append({
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1_url,
    "image_caption": "Virat Kohli during the IPL 2026 season for Royal Challengers Bengaluru",
    "image_attribution": img1_attr or "Wikimedia Commons",
    "sources": json.dumps(["PTI", "Times of India", "CricTracker", "InsideSport"]),
    "is_editorial": False
})

# -------- ARTICLE 2: Sindhu's losing streak to An Se Young --------
print("\n=== Article 2: Sindhu 10-Match Losing Streak ===")

art2_slug = "pv-sindhu-an-se-young-10-match-losing-streak-indonesia-open-2026-exit-nri"
art2_headline = "Sindhu Has Now Lost Ten Straight to An Se Young. The Gap Between Them Is No Longer Closing."
art2_subheadline = "The double Olympic medallist fell 21-17, 21-15 in the Indonesia Open Round of 16 — her second consecutive loss to the world No. 1 in as many weeks."

art2_body = """PV Sindhu's campaign at the 2026 Indonesia Open ended in familiar fashion on Thursday. An Se Young, the world No. 1 and reigning Olympic champion from South Korea, defeated the Indian 21-17, 21-15 in the Round of 16 at Istora Senayan in Jakarta — extending her perfect record against Sindhu to ten consecutive victories.

## A Contest That Keeps Slipping Away

The opening game offered hope. Sindhu matched An Se Young point for point through the early exchanges, the score locked at 10-10. She briefly moved ahead at 15-14, and the Jakarta crowd — which has long had a soft spot for the Indian — sensed an upset. But An Se Young found another gear. A brutal 41-shot rally went the Korean's way, and from there, the first game slipped to 21-17.

The second game was less competitive. An built a 13-6 lead that Sindhu never threatened to recover from. The world No. 1 closed it out 21-15, advancing to the quarterfinals where she would meet China's Chen Yufei in the latest installment of their own rivalry.

For Sindhu, the defeat mirrored her quarterfinal loss to An at the Singapore Open the previous week. The pattern has become uncomfortable: competitive stretches followed by a decisive Korean surge that the Indian cannot match.

## What the Numbers Say

In their ten meetings since An Se Young's rise to the top of the rankings, Sindhu has failed to take a single match. More tellingly, she has won just four games across those ten encounters — an average of fewer than one game won per match. The head-to-head is now so lopsided that their matchup barely registers as a contest in pre-tournament brackets.

For context, Sindhu is still ranked inside the world's top 15 and remains India's highest-profile women's singles player. But the gap between her and the sport's current elite — An Se Young, Chen Yufei, Akane Yamaguchi — has widened with each passing season.

## India's Singles Crisis in Jakarta

Sindhu was not the only Indian to exit early. Ayush Shetty, the 21-year-old who has emerged as India's most promising men's singles player, fell to Hong Kong's Lee Cheuk Yiu 21-16, 13-21, 14-21 after winning the opening game comfortably. The defeat marked Shetty's third consecutive tournament without reaching a quarterfinal, raising questions about whether his rapid rise has plateaued.

Lakshya Sen, HS Prannoy, Kidambi Srikanth, Malvika Bansod, and Unnati Hooda had all exited in earlier rounds. India's entire singles contingent — six players across men's and women's draws — was eliminated before the quarterfinal stage of a Super 1000 event.

## The Doubles Bright Spot

The one Indian pair still alive in Jakarta was Hariharan Amsakarunan and MR Arjun, who reached their maiden Super 1000 quarterfinal by beating Malaysia's Aaron Tai and Kang Khai Xing 16-21, 21-15, 21-19. Ranked 30th in the world, the young pair has quietly become India's most reliable men's doubles combination after Satwiksairaj Rankireddy and Chirag Shetty were upset earlier in the draw.

## The Bigger Question for NRI Fans

Sindhu remains one of the most recognizable Indian athletes globally, and her struggles resonate deeply with diaspora fans who followed her Olympic journeys in Rio and Tokyo. The question now is not whether she can beat An Se Young — the evidence suggests she cannot — but whether she can remain competitive enough at the highest level to justify her place in the Indian team heading into the 2028 Los Angeles Olympics.

At 31, time is not on her side. But Sindhu has defied expectations before. The Indonesia Open exit, painful as it is, may sharpen the urgency of her off-court preparation rather than signal the end.

**Sources:** Badminton World Federation, MyKhel, RevSportz, The Bridge"""

# Source image for Sindhu
img2_url, img2_attr = source_image(
    "P. V. Sindhu",
    ["PV Sindhu badminton", "Sindhu badminton India"],
    art2_slug
)

articles.append({
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2_url,
    "image_caption": "PV Sindhu during a BWF World Tour event",
    "image_attribution": img2_attr or "Wikimedia Commons",
    "sources": json.dumps(["BWF", "MyKhel", "RevSportz", "The Bridge"]),
    "is_editorial": False
})

# -------- ARTICLE 3: Women's T20 World Cup — India vs Pakistan preview --------
print("\n=== Article 3: India vs Pakistan Women's T20 World Cup ===")

art3_slug = "india-pakistan-women-t20-world-cup-2026-birmingham-edgbaston-june-14-preview-nri"
art3_headline = "India Play Pakistan at Edgbaston on June 14. Harmanpreet Has Done This Before. This Time She Has Shafali Back."
art3_subheadline = "The ICC Women's T20 World Cup begins June 12 in England. India, the reigning ODI world champions, open their campaign against their fiercest rivals in Birmingham."

art3_body = """The ICC Women's T20 World Cup 2026 starts on June 12 in England, and India will begin their campaign two days later against Pakistan at Edgbaston, Birmingham. It is the kind of fixture that writes its own script — high-stakes, high-pressure, and watched by millions across the subcontinent and the diaspora.

## India's Squad and Form

India enter the tournament as the reigning ODI World Cup champions, having lifted the trophy on home soil in 2025 with Shafali Verma's blazing 87 in the final. The T20 squad carries familiar names: Harmanpreet Kaur leads, Smriti Mandhana is vice-captain, and Shafali returns at the top of the order after a period of being dropped and recalled.

The full squad reads: Harmanpreet Kaur (c), Smriti Mandhana (vc), Shafali Verma, Jemimah Rodrigues, Bharti Fulmali, Deepti Sharma, Richa Ghosh (wk), Shree Charani, Yastika Bhatia (wk), Nandani Sharma, Arundhati Reddy, Renuka Singh, Kranti Gaud, Shreyanka Patil, Radha Yadav.

Jemimah Rodrigues, who has been in outstanding form through 2026, told CricTracker she believes India have the firepower to go all the way. Mandhana, meanwhile, acknowledged after the recent England T20I series that the team still has "a lot to learn" — particularly in its bowling plans, after a Knight-Capsey partnership of 137 chased down 180 in the decisive match.

## The England Warm-Up

India played a three-match T20I series against England before the World Cup. England won 2-1, with the hosts chasing down 181 in the decider. The series exposed India's bowling vulnerabilities — particularly the difficulty in containing established batters through the middle overs — but also showed encouraging signs from the batting unit. Yastika Bhatia's return to international cricket was a standout story, and Harmanpreet anchored the innings with an unbeaten 56 when early wickets fell.

## Pakistan's Challenge

Pakistan, led by Fatima Sana, arrive with less fanfare but carry genuine threats. Their spin options — Tuba Hassan, Nashra Sandhu, Sadia Iqbal — are suited to English conditions that often assist slow bowlers, and Gull Feroza's keeping has added solidity to the middle order. The rivalry adds its own intensity: no India-Pakistan match, in any format, is ever treated as routine by either side.

## The Group and What Comes Next

India are drawn in Group 1 alongside Australia, South Africa, Bangladesh, the Netherlands, and Pakistan. It is a formidable pool. Australia — led by Sophie Molineux after a generational transition — remain the benchmark. South Africa, with Laura Wolvaardt and Shabnim Ismail, are dangerous on any surface.

India's fixtures after Pakistan include the Netherlands (June 17, Edgbaston), Australia (June 20, The Oval), Bangladesh (June 23, Edgbaston), and South Africa (June 26, Lord's). The top three teams from each group advance to the Super Six stage.

## What NRI Fans Need to Know

For diaspora viewers in North America, the schedule is relatively kind. Matches at Edgbaston and Lord's start at 10:30 AM local time (5:30 AM ET, 2:30 AM PT) — early but watchable compared to the midnight starts of the men's ODI World Cup in Australia. The tournament runs until July 5, with the final at Lord's.

The ICC has confirmed broadcast partners across most territories, and the World Cup will be available on streaming platforms in the UK, Australia, and the subcontinent. Star Sports and JioCinema are expected to carry coverage in India, with Sky Sports in the UK.

This is Harmanpreet's fifth T20 World Cup as captain. At 37, it could be her last. She has never won it. The closest India came was in 2020, when they reached the final at the MCG before Australia overwhelmed them. Six years later, the squad is deeper, the experience is greater, and the hunger is sharper.

**Sources:** ICC, CricTracker, Female Cricket, ESPN Cricinfo"""

# Source image for Harmanpreet or India women cricket
img3_url, img3_attr = source_image(
    "Harmanpreet Kaur",
    ["Harmanpreet Kaur cricket India women", "India women cricket T20"],
    art3_slug
)

articles.append({
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "sports",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3_url,
    "image_caption": "India captain Harmanpreet Kaur during an international T20 match",
    "image_attribution": img3_attr or "Wikimedia Commons",
    "sources": json.dumps(["ICC", "CricTracker", "Female Cricket", "ESPN Cricinfo"]),
    "is_editorial": False
})

# ============================================================
# INSERT ALL ARTICLES
# ============================================================
print("\n=== Inserting articles ===")
for i, art in enumerate(articles, 1):
    print(f"\n--- Inserting article {i}: {art['slug']} ---")
    if not art.get("image_url"):
        print(f"  ⚠ No image for {art['slug']}, inserting without image")
        art.pop("image_url", None)
        art.pop("image_caption", None)
        art.pop("image_attribution", None)
    aid = insert_article(art)
    if aid:
        print(f"  ✓ Success: {art['headline'][:60]}...")
    else:
        print(f"  ✗ Failed: {art['headline'][:60]}...")
    time.sleep(1)

print("\n=== Sports writer complete ===")
