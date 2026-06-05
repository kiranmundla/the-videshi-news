#!/usr/bin/env python3
"""Sports writer for The Videshi - June 5, 2026 batch"""

import json, os, sys, time, re, uuid, urllib.parse
import requests
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

# Image sourcing functions
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


def fetch_wikimedia_commons_images(search_query, limit=5):
    """Search Wikimedia Commons for CC-licensed images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
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
    """Search Pexels for a relevant image. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None


def validate_image(url):
    """Verify image URL returns HTTP 200 with image content > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't give content-length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >5KB")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url", ""),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
        "sources": json.dumps(article.get("sources", [])),
        "is_editorial": False
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✓ Published: '{article['headline']}' (id: {aid})")
        return True
    else:
        print(f"  ✗ Failed to publish: {r.status_code} — {r.text[:300]}")
        return False


# ============================================================
# ARTICLE 1: BCCI Five-Year Cooling-Off Period
# ============================================================
def write_article_1():
    print("\n=== Article 1: BCCI Five-Year Cooling-Off Period ===")
    
    # Image: Vijay Shankar from Wikipedia (triggered the story)
    print("Sourcing image...")
    image_url = fetch_wikipedia_person_image("Vijay Shankar (cricketer)")
    if not image_url:
        image_url = fetch_wikipedia_person_image("Vijay Shankar cricketer")
    
    image_caption = "Vijay Shankar, whose retirement and signing with Lanka Premier League's Kandy Royals triggered the BCCI's cooling-off discussion"
    image_attribution = "Wikimedia Commons"
    
    # Try Wikimedia Commons if Wikipedia fails
    if not image_url:
        commons = fetch_wikimedia_commons_images("Vijay Shankar cricketer India")
        if commons:
            image_url = commons[0]["url"]
    
    # Pexels fallback: BCCI cricket board
    if not image_url or not validate_image(image_url):
        print("  Trying BCCI/cricket fallback...")
        commons2 = fetch_wikimedia_commons_images("BCCI cricket India board")
        if commons2:
            image_url = commons2[0]["url"]
            image_caption = "The BCCI headquarters in Mumbai, where the Apex Council met to discuss the proposed cooling-off policy"
        else:
            image_url = fetch_pexels_image("cricket stadium India")
            image_caption = "A cricket stadium in India"
            image_attribution = "Pexels"
    
    if image_url and not validate_image(image_url):
        print("  Image validation failed, trying Pexels...")
        image_url = fetch_pexels_image("cricket bat ball")
        image_caption = "The BCCI is proposing new rules to discourage early retirement from Indian cricket"
        image_attribution = "Pexels"
    
    body = """The Board of Control for Cricket in India is considering a five-year cooling-off period for cricketers who retire from domestic or international cricket and then seek a return. The proposal, discussed at an online Apex Council meeting on Thursday, is the board's most direct response yet to a growing trend: Indian players retiring early to become eligible for overseas T20 franchise leagues.

"The idea is to send a message to the players to be sure of their decision," a BCCI official told Hindustan Times. "Modalities will be worked out before rules are framed, looking at all parameters."

The BCCI has authorised its president and secretary to finalise the policy before sending it back to the Apex Council for formal approval.

## What Triggered the Proposal

The immediate trigger is Vijay Shankar. The 35-year-old all-rounder, who represented India in the 2019 World Cup and played 12 internationals, recently announced his retirement from domestic cricket and the Indian Premier League. Days later, he signed with the Kandy Royals in the Lanka Premier League. He has indicated interest in other overseas competitions as well, including the Bangladesh Premier League, Canada's Global T20, and Major League Cricket in the United States.

Shankar went unsold in the IPL 2026 auction. His retirement note was gracious — "Cricket is my life. I started playing when I was 10, and 25 years later, I am grateful and blessed to have played at every level, and to the highest level." But the BCCI sees his decision as part of a larger pattern it wants to discourage.

## The Exodus That Worries the BCCI

Over the past several years, a steady stream of Indian cricketers has retired from domestic cricket specifically to play in overseas franchise leagues. BCCI regulations bar active Indian cricketers — at any level — from participating in foreign leagues without board clearance, which is almost never granted.

The workaround is simple: retire from Indian cricket, and you are no longer bound by BCCI rules.

Dinesh Karthik retired from all forms of Indian cricket in 2024 and moved to commentary and overseas leagues. Yuvraj Singh, after his international career ended, played in the Global T20 Canada and other exhibitions. Unmukt Chand, the former India U-19 World Cup-winning captain, retired from Indian cricket entirely to play in the United States, eventually representing the USA in international cricket. Pravin Tambe, the leg-spinner who made his IPL debut at 41, retired from Indian cricket to play in the Caribbean Premier League. Irfan Pathan played in the Lanka Premier League after retirement.

For NRI fans who follow cricket across multiple leagues and time zones, these players have been familiar faces in tournaments from Durban to Dallas. But for the BCCI, the trend represents a leakage of talent and, more critically, a diversion of the commercial surplus generated by the IPL into rival ecosystems.

## The Broader Context: An IPL Ecosystem Under Pressure

The BCCI's concern is not purely about player loyalty. Many of the T20 leagues that attract retired Indian cricketers — the SA20 in South Africa, the ILT20 in the UAE, the Lanka Premier League, Major League Cricket — are owned or funded by the same Indian investors who own IPL franchises.

"The surplus from the IPL is being diverted towards other leagues, thus swelling the coffers of other boards," a BCCI source told Cricbuzz during a previous discussion on the same issue in 2023. That concern has only intensified as more leagues have launched and more Indian players have found their way there.

A five-year cooling-off period would effectively end the retire-and-play-abroad pipeline for most cricketers. A player who retires at 32 would not be eligible to return to Indian cricket until 37, by which point a competitive comeback is nearly impossible for most athletes.

## What It Means for the Diaspora

For NRIs in the US, UK, Canada, and the Gulf, the presence of Indian cricketers in local or regional leagues has been a significant draw. Unmukt Chand playing for the Silicon Valley Strikers in Major League Cricket, or Irfan Pathan turning up in Colombo, adds a layer of connection for fans who may not travel to India for domestic cricket but can watch these leagues locally or on streaming platforms.

If the cooling-off policy is implemented, the flow of Indian talent into these leagues could slow dramatically. Players who might have retired at 30 or 31 to chase opportunities abroad may instead stay in the Indian system longer, knowing that a return would require a five-year wait.

The BCCI has not set a timeline for finalising the rules, but the authorisation given to its office-bearers suggests the policy could be ready before the next domestic season begins."""

    article = {
        "headline": "Retire From Indian Cricket and You Wait Five Years to Come Back. The BCCI Wants to Make That the Rule.",
        "subheadline": "The board's Apex Council discussed a cooling-off period for players who leave domestic cricket to chase overseas franchise leagues. Vijay Shankar's Lanka Premier League move is the latest trigger.",
        "slug": "bcci-five-year-cooling-off-period-retired-players-overseas-leagues-vijay-shankar-lpl-nri",
        "body": body,
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": [
            {"name": "Cricbuzz", "url": "https://www.cricbuzz.com"},
            {"name": "Hindustan Times", "url": "https://www.hindustantimes.com"},
            {"name": "Cricket Addictor", "url": "https://cricketaddictor.com"},
            {"name": "Crex", "url": "https://crex.com"}
        ]
    }
    
    wc = len(body.split())
    print(f"  Word count: {wc}")
    if wc < 400:
        print(f"  ✗ Article too short ({wc} words), skipping")
        return False
    
    return publish_article(article)


# ============================================================
# ARTICLE 2: Afghanistan Without Rashid Khan for India Test
# ============================================================
def write_article_2():
    print("\n=== Article 2: Afghanistan Without Rashid Khan for India Test ===")
    
    # Image: Rashid Khan from Wikipedia
    print("Sourcing image...")
    image_url = fetch_wikipedia_person_image("Rashid Khan (cricketer)")
    if not image_url:
        image_url = fetch_wikipedia_person_image("Rashid Khan cricketer")
    
    image_caption = "Rashid Khan will miss Afghanistan's Test against India due to workload management"
    image_attribution = "Wikimedia Commons"
    
    # Try Wikimedia Commons for Rashid Khan
    if not image_url:
        commons = fetch_wikimedia_commons_images("Rashid Khan Afghanistan cricket")
        if commons:
            image_url = commons[0]["url"]
    
    if image_url and not validate_image(image_url):
        print("  Image validation failed, trying alternatives...")
        # Try Hashmatullah Shahidi (Afghanistan captain)
        image_url = fetch_wikipedia_person_image("Hashmatullah Shahidi")
        if image_url and validate_image(image_url):
            image_caption = "Hashmatullah Shahidi will captain Afghanistan in the one-off Test against India at Mohali"
        else:
            commons2 = fetch_wikimedia_commons_images("Afghanistan cricket team")
            if commons2:
                image_url = commons2[0]["url"]
                image_caption = "The Afghanistan cricket team faces India in only their second Test encounter"
                image_attribution = "Wikimedia Commons"
            else:
                image_url = fetch_pexels_image("cricket test match")
                image_caption = "Afghanistan will play their second-ever Test against India starting June 6 at Mohali"
                image_attribution = "Pexels"
    
    body = """Rashid Khan will not play the one-off Test against India starting Saturday at the Maharaja Yadavindra Singh International Cricket Stadium in Mohali. Afghanistan's most recognisable cricketer has been advised to limit his red-ball workload to protect his body for the T20 franchise circuit and ODI commitments that define his year.

It is a notable absence. Afghanistan have played India in Tests exactly once before — in Bengaluru in 2018 — and lost by an innings in two days. Eight years later, they return without their best player.

## Who Leads Afghanistan in Mohali

Hashmatullah Shahidi, the 29-year-old left-hander and Afghanistan's Test captain, will lead a squad that mixes experience with new faces. Rahmanullah Gurbaz, the explosive wicketkeeper-batter who has become one of the most sought-after players on the T20 circuit, is in the squad. So is the experienced Rahmat Shah and all-rounder Azmatullah Omarzai, whose ability to bowl fast and bat in the middle order makes him Afghanistan's most complete player in any format.

Three uncapped players have been selected: fast bowler Bilal Sami, leg-spinner Nangyal Kharoti, and middle-order batter Rahmanullah Zadran. Qais Ahmad, the young leg-spinner, also returns to the Test setup.

Without Rashid, Afghanistan's spin attack will lean on the unorthodox left-arm spin of Sharafuddin Ashraf and whatever Kharoti and Qais Ahmad can produce on a Mohali pitch that has historically assisted both pace and spin.

**Afghanistan Test squad:** Hashmatullah Shahidi (c), Abdul Malik, Sediqullah Atal, Rahmat Shah, Rahmanullah Gurbaz, Rahmanullah Zadran, Afsar Zazai (wk), Ikram Alikhil (wk), Azmatullah Omarzai, Sharafuddin Ashraf, Nangyal Kharoti, Qais Ahmad, Bilal Sami, Zia Ur Rahman Sharifi, Saleem Safi.

## India's New-Look Test Side

India's squad carries its own storylines. Shubman Gill captains the Test side with KL Rahul as his vice-captain. Virat Kohli is out, recovering from the hamstring strain he played through in the IPL final. Rishabh Pant is in the squad but no longer the vice-captain, a quiet demotion that followed questions about his shot selection under pressure. Jasprit Bumrah is rested entirely.

The most anticipated selections are the uncapped spinners. Harsh Dubey, the left-arm orthodox spinner who dismissed Kohli and Gill in IPL 2026, is in line for a Test debut. Manav Suthar, a 22-year-old left-arm spinner from Rajasthan who has torn through domestic cricket with 129 wickets at 25.76 in first-class cricket, is the other debutant candidate. Gurnoor Brar, the left-arm seamer from Punjab, adds a local flavour to a squad playing in his home state.

The big question is whether India will play Kuldeep Yadav alongside Dubey or Suthar, or whether they will opt for two new faces and Washington Sundar as the senior spin option. Ashwin's recent retirement has left a hole in the Test spin department that the BCCI is filling through exposure and opportunity.

**India Test squad:** Shubman Gill (c), Yashasvi Jaiswal, KL Rahul (vc), Sai Sudharsan, Rishabh Pant (wk), Devdutt Padikkal, Nitish Kumar Reddy, Washington Sundar, Kuldeep Yadav, Mohammed Siraj, Prasidh Krishna, Manav Suthar, Gurnoor Brar, Harsh Dubey, Dhruv Jurel (wk).

## The Last Time They Met

The 2018 Test in Bengaluru was Afghanistan's only previous Test against India, and it was brutal. India scored 474 in their only innings — Ajinkya Rahane made 110, Murali Vijay 105. Afghanistan were bowled out for 109 and 103. The match lasted less than two days. Ravindra Jadeja took seven wickets; Umesh Yadav took four.

Afghanistan cricket has matured significantly since then. The success of players like Rashid Khan, Gurbaz, and Omarzai in global T20 leagues has raised the country's profile and developed individual skills. But Test cricket remains their weakest format. They have played only nine Tests since gaining full-member status, winning three (against Zimbabwe, Ireland, and Bangladesh) and losing the rest.

## The Diaspora Angle

For NRI fans in North America, the UK, and the Gulf, the match arrives during a packed week of Indian sports. The T20 World Cup 2026 is under way in Sri Lanka, India A are in Dambulla for a tri-series, and the Norway Chess final round is being played simultaneously. The Test starts at 9:30 AM IST on Saturday — Friday evening for fans on the US East Coast, and early afternoon in London.

The match will be broadcast on Sony Sports Network in India and streamed on various platforms internationally. It is Afghanistan's chance to prove that eight years of growth has closed the gap. Without Rashid Khan, they will need someone unexpected to step up."""

    article = {
        "headline": "Afghanistan Will Play India at Mohali Without Rashid Khan. It Is Their First Test Against India in Eight Years.",
        "subheadline": "The star leg-spinner has been rested for workload management. Hashmatullah Shahidi leads a squad with three uncapped players into only Afghanistan's second Test against India.",
        "slug": "afghanistan-india-test-mohali-2026-rashid-khan-absent-shahidi-squad-debut-nri",
        "body": body,
        "image_url": image_url or "",
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": [
            {"name": "Fox Sports Australia", "url": "https://foxsports.com.au"},
            {"name": "CricTracker", "url": "https://crictracker.com"},
            {"name": "Sportskeeda", "url": "https://sportskeeda.com"},
            {"name": "Cricket World", "url": "https://cricketworld.com"}
        ]
    }
    
    wc = len(body.split())
    print(f"  Word count: {wc}")
    if wc < 400:
        print(f"  ✗ Article too short ({wc} words), skipping")
        return False
    
    return publish_article(article)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print(f"Sports Writer - {datetime.now(timezone.utc).isoformat()}")
    print(f"Supabase URL: {SUPABASE_URL[:30]}..." if SUPABASE_URL else "ERROR: No Supabase URL")
    print(f"Pexels key: {'set' if PEXELS_KEY else 'NOT SET'}")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("FATAL: Missing Supabase credentials")
        sys.exit(1)
    
    results = []
    results.append(("BCCI Cooling-Off Period", write_article_1()))
    results.append(("Afghanistan Without Rashid Khan", write_article_2()))
    
    print("\n=== Summary ===")
    for title, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {title}")
    
    published = sum(1 for _, s in results if s)
    print(f"\nTotal: {published}/{len(results)} articles published")
