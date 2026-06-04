#!/usr/bin/env python3
"""
Sports writer — June 4, 2026 run
Two articles:
1. Ashwin backs Dubey for India debut — the spin battle for the Afghanistan Test
2. Sooryavanshi effect — Sony broadcasts A-team tri-series live for the first time
"""

import json, os, sys, time, uuid, re, subprocess
import requests
import urllib.parse
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

UA = "TheVideshi/1.0 (thevideshi.com)"

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns (url, attribution) or (None, None)."""
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
                return img, "Wikimedia Commons"
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None, None

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
            headers={"User-Agent": UA},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                if url and "image" in mime:
                    results.append({
                        "url": url,
                        "title": page.get("title", ""),
                        "width": ii.get("width", 0),
                        "height": ii.get("height", 0)
                    })
            if results:
                print(f"  ✓ Wikimedia Commons found {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error for '{search_query}': {e}")
    return []

def fetch_pexels_image(query):
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                best = photos[0]
                url = best.get("src", {}).get("large2x") or best.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url, "Pexels"
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None, None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": UA}, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        content_length = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in content_type and content_length > 5000:
            print(f"  ✓ Image validated: {content_length} bytes, {content_type}")
            return True
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and "image" in content_type and content_length == 0:
            r2 = requests.get(url, headers={"User-Agent": UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >5KB")
                return True
        print(f"  ✗ Image failed validation: status={r.status_code}, type={content_type}, size={content_length}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def get_best_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search. Returns (url, caption_hint, attribution)."""
    candidates = []
    
    # Source 1: Wikipedia person image
    if person_name:
        url, attr = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            candidates.append(("wikipedia", url, attr))
    
    # Source 2: Wikimedia Commons
    if wiki_search:
        commons = fetch_wikimedia_commons_images(wiki_search)
        for img in commons[:3]:
            if validate_image(img["url"]):
                candidates.append(("commons", img["url"], "Wikimedia Commons"))
                break
    
    # Source 3: Pexels
    if pexels_query:
        url, attr = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            candidates.append(("pexels", url, attr))
    
    # Prefer: wikipedia > commons > pexels
    for source_type in ["wikipedia", "commons", "pexels"]:
        for c in candidates:
            if c[0] == source_type:
                return c[1], c[2]
    
    return None, None

def publish_article(article):
    """Insert article into Supabase."""
    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": "sports",
        "vertical": "sports",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption"),
        "image_attribution": article.get("image_attribution"),
        "sources": json.dumps(article.get("sources", [])),
        "is_editorial": False,
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=15
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('id', 'unknown')} — {article['headline'][:60]}...")
            return True
        print(f"  ✓ Published (no ID returned)")
        return True
    else:
        print(f"  ✗ Publish failed: {r.status_code} — {r.text[:200]}")
        return False


###############################################################################
# ARTICLE 1: Ashwin backs Dubey for Test debut
###############################################################################
print("\n=== ARTICLE 1: Ashwin backs Dubey for Afghanistan Test ===")

# Image: Try Harsh Dubey (likely no Wikipedia page), then R Ashwin
img1_url, img1_attr = get_best_image(
    person_name="Ravichandran Ashwin",
    wiki_search="Ravichandran Ashwin cricket India",
    pexels_query="cricket bowling India"
)

article1 = {
    "headline": "Ashwin Has His Eyes on Dubey. Kumble Wants Kuldeep. The Afghanistan Test Has a Spin Selection Puzzle Nobody Agrees On.",
    "subheadline": "With four spinners in a fifteen-man squad, India's greatest modern spinner says the uncapped left-armer from Vidarbha is the one he wants to see bowl first.",
    "slug": "ashwin-backs-harsh-dubey-test-debut-kuldeep-kumble-afghanistan-india-spin-puzzle-nri",
    "image_url": img1_url,
    "image_caption": "R. Ashwin, India's all-time leading off-spinner, has backed Harsh Dubey for a Test debut",
    "image_attribution": img1_attr,
    "sources": [
        {"name": "Khel Ja", "url": "https://khelja.in"},
        {"name": "Fox Sports Australia", "url": "https://foxsports.com.au"},
        {"name": "Sportskeeda", "url": "https://sportskeeda.com"},
        {"name": "ICC Cricket", "url": "https://icc-cricket.com"}
    ],
    "body": """India have four frontline spinners in a fifteen-man squad for a single Test match. That is two too many for a playing eleven, and the debate over which pair gets the nod against Afghanistan in Mullanpur on Saturday has now pulled in the sharpest voice in Indian spin bowling: Ravichandran Ashwin.

## Ashwin's Pick Is Dubey

Speaking to JioStar ahead of the one-off Test, Ashwin made his preference clear. "My eyes will be on Harsh Dubey," the retired off-spinner said. "I am curious whether he will get a chance. We will have to wait and see if the team goes with Manav Suthar or Harsh Dubey. But I am particularly interested in Dubey because of his strong domestic season."

That domestic season was extraordinary. Dubey finished as the leading wicket-taker in the 2025-26 Ranji Trophy with 69 wickets at 16.98, bowling left-arm orthodox spin for Vidarbha. At twenty-three, he carried an entire state's red-ball campaign on his shoulders. He followed that with a strong IPL stint for Sunrisers Hyderabad, where Virat Kohli was among his white-ball victims. The combination of domestic dominance and franchise exposure has made him, in Ashwin's view, the more compelling debutant.

Manav Suthar, the other uncapped left-armer, brings a different resume. The Rajasthan spinner has 129 first-class wickets at 25.76 and took eight wickets in an unofficial India A Test against Australia A, dismissing Oliver Peake, Will Sutherland, Cooper Connolly, and Josh Philippe. He also showed batting ability, scoring 82 in a Duleep Trophy match. His case is built on consistency across formats rather than a single breakout season.

## The Kumble-Pathan Split

The disagreement goes beyond Ashwin. On Star Sports' *Follow the Blues*, Anil Kumble and Irfan Pathan offered directly opposing compositions.

Kumble picked Kuldeep Yadav and Harsh Dubey as his two specialist spinners, with Gurnoor Brar and Mohammed Siraj forming the seam attack. He went further, arguing that Nitish Kumar Reddy must be treated as a bowling option rather than a specialist batter. "If Gurnoor has been picked, there is a reason. Play him. If it means Prasidh misses out, he misses out, unfortunately."

Pathan agreed on three of four bowlers but replaced Kuldeep with Washington Sundar. His reasoning was structural: "The Indian team likes to bat till Number 8. That is how they play." Washington at Number 7, with Dhruv Jurel at 6 and Nitish Kumar Reddy at 8, gives India a deep batting tail that has served them well in home Tests. Dubey, in Pathan's eleven, bowls at Number 9.

## The Kuldeep Question

Kuldeep Yadav's place looked automatic until the IPL intervened. A forgettable season with Delhi Capitals has invited scrutiny, even though his Test record in India remains formidable — eight wickets at 28.63 in the most recent home series against South Africa. Ashwin acknowledged this directly: "Kuldeep Yadav will lead the spin attack against Afghanistan in the absence of Ravindra Jadeja. He has been bowling with great rhythm and confidence."

The implication is that Kuldeep plays, and the real battle is for the second spinner's slot. If captain Shubman Gill prefers batting depth, Washington Sundar at Number 7 is the safer pick. If the team wants two attacking spinners on a Mullanpur track that will turn, Dubey or Suthar comes in alongside Kuldeep.

## What the Pitch Says

The Maharaja Yadavindra Singh International Cricket Stadium in Mullanpur is new to Test cricket. Its IPL surface offered turn and variable bounce, conditions that favour spin bowling. Sairaj Bahutule, the newly appointed spin bowling coach, will have his first assignment mentoring two uncapped spinners through what could be their debut match.

Afghanistan, without Rashid Khan who has been rested from long-format cricket, will be led by Hashmatullah Shahidi. India have played one Test against Afghanistan previously — an innings defeat inside two days in Bengaluru in 2018. The match begins on June 6 at Mullanpur, with India's first red-ball assignment in five months.

## The Diaspora Angle

For NRI fans watching from abroad, this Test is available on FanCode in India and Fox Cricket in Australia. The match starts at 9:30 PM EDT on Friday night, a convenient time for East Coast viewers. With India resting Jasprit Bumrah and Ravindra Jadeja, the spotlight falls entirely on the next generation — and on which version of India's spin future the selectors and captain choose to put on the field first.

The answer arrives Saturday. Ashwin already knows who he wants to see."""
}

print(f"  Article 1 body word count: {len(article1['body'].split())}")
publish_article(article1)


###############################################################################
# ARTICLE 2: Sooryavanshi effect — Sony broadcasts A-team tri-series live
###############################################################################
print("\n=== ARTICLE 2: Sooryavanshi effect forces live broadcast ===")

# Image: Try Vaibhav Sooryavanshi on Wikipedia (may not exist), then generic cricket
img2_url, img2_attr = get_best_image(
    person_name="Vaibhav Sooryavanshi",
    wiki_search="Vaibhav Suryavanshi cricketer",
    pexels_query="cricket stadium broadcast television"
)

# If no Sooryavanshi image, try alternate name
if not img2_url:
    print("  Trying alternate name: Vaibhav Suryavanshi")
    img2_url, img2_attr = get_best_image(
        person_name="Vaibhav Suryavanshi",
        wiki_search="IPL 2026 cricket youngest",
        pexels_query="cricket bat young player"
    )

article2 = {
    "headline": "Sony Will Broadcast the Sri Lanka Tri-Series Live. They Are Doing It Because a Fifteen-Year-Old Is in the Squad.",
    "subheadline": "A-team cricket does not get televised. Vaibhav Sooryavanshi's inclusion in the India A squad for the Dambulla tri-series changed that overnight.",
    "slug": "vaibhav-sooryavanshi-sony-broadcast-india-a-tri-series-sri-lanka-dambulla-live-tv-nri",
    "image_url": img2_url,
    "image_caption": "The India A tri-series in Dambulla will be broadcast live on Sony Sports, driven by Sooryavanshi's star power",
    "image_attribution": img2_attr,
    "sources": [
        {"name": "Cricbuzz", "url": "https://cricbuzz.com"},
        {"name": "CricTracker", "url": "https://crictracker.com"},
        {"name": "Sports Yaari", "url": "https://sportsyaari.com"},
        {"name": "The Sports Tak", "url": "https://thesportstak.com"}
    ],
    "body": """There is no precedent for what just happened. Sony Sports Network has announced that it will broadcast the upcoming India A tri-series against Sri Lanka A and Afghanistan A live on television and its digital platform, SonyLIV. A-team tri-series in the subcontinent do not get televised. This one will, for a single reason: Vaibhav Sooryavanshi is in the squad.

## The Sooryavanshi Effect

The fifteen-year-old sensation, who lit up IPL 2026 with a staggering 776 runs to win the Orange Cap, has turned an otherwise routine developmental tournament into a commercial proposition that broadcasters cannot ignore. Sony, which holds the rights to cricket played in Sri Lanka, moved quickly once the BCCI announced the India A squad with Sooryavanshi's name in it.

"The Sooryavanshi Express is coming to light up the stage in a high-octane Tri-series," Sony's social media accounts announced, framing the tournament entirely around one player. The network has been looking for cricket content after rival Jio Hotstar secured the IPL and ICC World Cup properties, and Sooryavanshi's global appeal handed them an opportunity on a platter.

The tri-series, scheduled for June 9 to 21 at the Rangiri Dambulla International Stadium, will feature seven matches including a final. All matches start at 10:00 AM IST, which translates to 12:30 AM EDT and 9:30 PM PDT the previous night — a late evening slot for NRI fans on the West Coast of the United States.

## More Than One Star

While Sooryavanshi commands the headlines, the India A squad has genuine depth. Tilak Varma, fresh from a strong IPL campaign, leads the side. Ruturaj Gaikwad, who replaced Riyan Parag in a late squad change, brings the experience of leading Chennai Super Kings and scoring heavily in domestic cricket. Priyansh Arya, Ayush Badoni, and Suryansh Shedge represent a generation of batters pushing for senior team spots.

The bowling unit features Anshul Kamboj, Yash Thakur, and Arshad Khan — names that may mean little today but could feature prominently in India's 2027 ODI World Cup plans. Anukul Roy, who replaced Harsh Dubey after the latter was called up to the senior squad for the Afghanistan Test, adds left-arm spin options.

Sri Lanka A will be no pushovers. Their squad includes experienced internationals like Niroshan Dickwella, Avishka Fernando, and Chamika Karunaratne. Afghanistan A, led by Darwish Rasooli, bring quality spinners in Qais Ahmad and Sharafuddin Ashraf.

## Why This Matters for the Diaspora

For NRI cricket fans, this broadcast decision carries significance beyond one tournament. It establishes that Indian cricket's second tier can generate enough commercial interest to warrant live television coverage — something that was unthinkable even a year ago. The precedent is Sooryavanshi-specific for now, but it opens the door for more developmental cricket to reach screens in living rooms across the United States, the United Kingdom, Canada, and the Gulf.

The timing is deliberate. Between the conclusion of IPL 2026 and the India-Afghanistan senior series, there is a gap in marquee cricket. Sony saw a window, and Sooryavanshi gave them the justification to fill it.

## The IIM Connection

The Sooryavanshi phenomenon has already transcended cricket. IIM Indore announced it would study the "Vaibhav Model" as a management case study — examining how a fifteen-year-old prodigy navigated the pressures of a senior professional league while maintaining performance consistency. His five individual awards at IPL 2026 — Orange Cap (776 runs), MVP, Emerging Player, Super Striker (strike rate 237.30), and Most Sixes (72, breaking Chris Gayle's all-time record) — represent a dataset that business schools find genuinely worth analysing.

## What to Watch

The first match, India A versus Sri Lanka A, takes place on Tuesday, June 9. For NRI fans:

- **TV in India**: Sony Sports Network
- **Streaming**: SonyLIV app and website
- **Time**: 10:00 AM IST (12:30 AM EDT / 9:30 PM PDT the previous night)
- **Venue**: Rangiri Dambulla International Stadium, Sri Lanka

The full schedule runs across seven matches. India A play Sri Lanka A on June 9 and 15, Afghanistan A on June 11 and 17, with the final on June 21.

Sony is investing in production values typically reserved for senior international cricket. For a network looking to reclaim cricket relevance, and for fans looking to watch the most talked-about teenager in world cricket, the investment makes mutual sense. The question is no longer whether Sooryavanshi deserves the attention. It is whether the cricketing infrastructure around him can scale fast enough to keep up."""
}

print(f"  Article 2 body word count: {len(article2['body'].split())}")
publish_article(article2)

print("\n=== Sports writer run complete ===")
