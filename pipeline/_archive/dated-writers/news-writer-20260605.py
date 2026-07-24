#!/usr/bin/env python3
"""
News writer for The Videshi — 2026-06-05 batch
Writes 3 articles:
1. Georgia Indian American political wave (nri-world)
2. India's clean energy grid penalty crisis (news)
3. RBI's NRI-focused rupee defense playbook (news)
"""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone
import requests
import subprocess

# --- ENV ---
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                os.environ[key] = val.strip()

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}
WIKI_UA = 'TheVideshi/1.0 (thevideshi.com)'

# --- IMAGE FUNCTIONS ---
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": WIKI_UA},
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
    try:
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
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": WIKI_UA},
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
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    """Search Pexels for an image using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    try:
        result = subprocess.run(
            ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
             f'https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=3&orientation=landscape'],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        photos = data.get('photos', [])
        if photos:
            img_url = photos[0]['src']['large2x']
            print(f"  ✓ Pexels image found for '{query}': {img_url[:80]}...")
            return img_url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def validate_image(url):
    """Validate image URL returns HTTP 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": WIKI_UA}, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Sometimes HEAD doesn't return Content-Length; try GET
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": WIKI_UA}, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                print(f"  ✓ Image validated via GET: >{len(chunk)} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False

def source_image(person_name=None, wiki_searches=None, pexels_query=None):
    """Multi-source image search. Returns (url, caption, attribution) or (None,None,None)."""
    # 1. Wikipedia person image
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, None, "Wikimedia Commons"
    
    # 2. Wikimedia Commons
    if wiki_searches:
        for q in wiki_searches:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results:
                url = r.get('url') or r.get('original_url')
                if url and validate_image(url):
                    return url, r.get('title', ''), "Wikimedia Commons"
    
    # 3. Pexels fallback
    if pexels_query:
        url = fetch_pexels_image(pexels_query)
        if url and validate_image(url):
            return url, None, "Pexels"
    
    return None, None, None


def insert_article(article):
    """Insert article into Supabase p2_articles."""
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
        print(f"  ✓ Article inserted (response: {r.text[:100]})")
        return True
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return False


# =============================================================================
# ARTICLE 1: Georgia Indian American Political Wave
# =============================================================================
def write_georgia_article():
    print("\n=== ARTICLE 1: Georgia Indian American Political Wave ===")
    
    # Image sourcing: Try Georgia State Capitol from Wikimedia
    img_url, img_title, img_attr = source_image(
        wiki_searches=["Georgia State Capitol Atlanta", "Georgia state legislature"],
        pexels_query="Georgia State Capitol Atlanta"
    )
    
    img_caption = "The Georgia State Capitol in Atlanta, where a new generation of Indian American lawmakers is headed"
    if not img_url:
        print("  ⚠ No image found, skipping article")
        return False
    
    headline = "Five Indian Americans Just Won Primaries Across Georgia. One Could Become the State's First South Asian Lieutenant Governor."
    subheadline = "From a Sikh first-time candidate to the youngest state legislator in Georgia, South Asian Americans are reshaping the political map of a state that already has 600,000 Asian American residents."
    
    slug = "indian-americans-georgia-primaries-nabilah-parkes-jyot-singh-saira-draper-20260605"
    
    body = """Georgia's primary elections this week delivered a wave of historic results for Indian and South Asian American candidates, signaling a shift in political representation in a state where Asian Americans now number more than 600,000.

Five candidates endorsed by Indian American Impact, the largest political organization dedicated to South Asian American representation, either won outright or advanced to runoff elections. The breadth of their victories — spanning a lieutenant governor race, two state senate seats, and two state house districts — marks the most significant single-night haul for Indian American candidates in Georgia's history.

## The Lieutenant Governor Race

The most closely watched result was Nabilah Islam Parkes's advance to a runoff in the Democratic primary for lieutenant governor. If she wins the runoff and the general election, Parkes would become the first South Asian and Asian American to hold the office in Georgia — and one of only a handful of South Asian lieutenant governors in American history.

Parkes, a Bangladeshi American organizer who built her profile through voter registration drives in suburban Atlanta, ran on a platform of lowering costs for working families and defending immigrant communities. Her advance to the runoff reflects the growing electoral muscle of South Asian voters in metro Atlanta's rapidly diversifying suburbs.

## Georgia's First Sikh Elected Official

Jyot Singh's outright victory in State House District 97 puts him on track to become the first Sikh elected official in Georgia history. Singh's win is part of a broader pattern of Sikh Americans entering electoral politics across the country, from Sukh Kaur's city council seat in San Antonio to the growing Sikh caucus in state legislatures nationwide.

His district, in the suburban Atlanta corridor, has seen a significant influx of Indian American families over the past decade. Singh's campaign focused on education, infrastructure, and community engagement — issues that resonate in fast-growing suburban districts where many residents are first-generation immigrants or their children.

## Three More Victories

Saira Draper won the Democratic primary for State Senate District 44, securing her nomination in a competitive race. Rahul Garabadu advanced to a runoff in the State Senate District 7 race, one of the most contested seats in the state. And Akbar Ali secured the Democratic nomination for House District 106, where he will continue serving as the youngest state legislator in Georgia.

## What It Means for the Diaspora

The results in Georgia are not an anomaly. Indian American political engagement has been accelerating for years, driven by demographic growth, organizational infrastructure, and a generation of candidates who grew up in the communities they now seek to represent.

Indian American Impact, which has endorsed and supported more than 200 candidates since its founding in 2016, has channeled upwards of $20 million into campaigns and voter mobilization. The organization's executive director, Chintan Patel, called Tuesday's results evidence of "the growing political power and representation of our communities."

Georgia is a particularly significant battleground. The state's Asian American population has grown by more than 40 percent over the past decade, concentrated in the suburban counties ringing Atlanta — Gwinnett, Forsyth, Fulton, and DeKalb. These are the same counties that tipped Georgia to Democrats in 2020 and have remained fiercely competitive since.

For Indian American voters watching from California, New Jersey, Texas, or anywhere else in the diaspora, Georgia's primary results offer a template: invest in local races, build organizational capacity, and run candidates who reflect the communities they serve. The returns, as Tuesday showed, are already arriving.

*Sources: Indian American Impact, The Indian Eye, Georgia Secretary of State*"""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "sources": json.dumps(["Indian American Impact", "The Indian Eye", "Georgia Secretary of State"])
    }
    
    return insert_article(article)


# =============================================================================
# ARTICLE 2: India's Clean Energy Grid Penalty Crisis
# =============================================================================
def write_grid_article():
    print("\n=== ARTICLE 2: India Clean Energy Grid Penalty Crisis ===")
    
    # Image: solar panels in India from Wikimedia
    img_url, img_title, img_attr = source_image(
        wiki_searches=["solar power plant India", "India solar farm Rajasthan", "wind farm India"],
        pexels_query="solar panels India farm"
    )
    
    img_caption = "A solar power installation in India, where new grid rules threaten to slash developer revenues"
    if not img_url:
        print("  ⚠ No image found, trying harder...")
        img_url, img_title, img_attr = source_image(
            pexels_query="solar panels field"
        )
        if not img_url:
            print("  ⚠ Still no image, skipping")
            return False
    
    headline = "India's New Grid Rules Could Cut Wind Farm Revenue by 48 Percent. A Court Just Hit Pause."
    subheadline = "Tougher penalties for solar and wind producers who miss delivery targets have alarmed investors and forced a legal standoff — just as India needs billions to reach its 500 GW clean energy goal."
    
    slug = "india-grid-penalty-rules-solar-wind-500gw-cerc-karnataka-court-20260605"
    
    body = """India's push to tighten power grid discipline has collided with its clean energy ambitions. New regulations that sharply increase penalties for renewable energy producers who miss their delivery commitments have unsettled investors, drawn a legal challenge, and exposed the tension at the heart of the country's energy transition.

The rules, drafted by the Central Electricity Regulatory Commission and originally due to take effect in April 2026 before being pushed to April 2027, penalize solar and wind operators when the electricity they actually deliver to the grid deviates from what they scheduled. The penalties escalate with the size of the gap.

Industry groups estimate the tougher regime could cut revenue by roughly 11 percent for solar projects and as much as 48 percent for wind farms. For an industry where developers typically target an internal rate of return of 10 percent on solar and 12 to 13 percent on hybrid projects, those numbers are existential.

## The Problem the Rules Are Trying to Solve

India's power grid is changing faster than most people realize. Renewable energy's share of generation is projected to rise from 13.9 percent in the current fiscal year to 17.5 percent in the next. At those levels, weather-driven surges and shortfalls in solar and wind output create real-time balancing problems that the transmission system must manage far more tightly than before.

The CERC's position is straightforward: as renewables take up a larger share of the grid, they must behave more like conventional power plants. Predictability is not optional when a fifth of the grid depends on the weather.

As of March, India had 288 gigawatts of non-fossil fuel capacity, with wind and solar accounting for 73 percent of the total. The government's target is 500 GW by 2030 — a goal that requires sustained investment at a scale India has never achieved.

## The Investor Backlash

The developer community has pushed back hard. "Developers will face very high penalties even when deviations are small. This tightens margins, revenues will shrink and project viability will be affected," said Debabrat Ghosh, India head at Aurora Energy Research.

The backlash was strong enough to trigger a legal intervention. A Karnataka court temporarily blocked the tougher penalties, allowing developers to operate under the older, more lenient deviation-charging system until a hearing scheduled after June 10, when the government and regulator must file their response.

The injunction buys time, but it does not resolve the underlying conflict. Policymakers want grid reliability. Investors want stable returns. The two are currently on a collision course.

## A Deeper Constraint

The penalty debate may actually be obscuring a more fundamental problem: transmission bottlenecks. Before deviation fines become the primary concern, many renewable projects face the risk that they cannot move their generated power onto the grid at all.

Adani Green, one of India's largest renewable developers, has publicly acknowledged that it could add seven to eight gigawatts of capacity per year but is limiting annual additions to roughly 4.5 to 5 GW because of transmission constraints. If the country's largest developer is throttling itself, smaller operators face even steeper odds.

Solar curtailments — instances where generated power is wasted because the grid cannot absorb it — reached 300 gigawatt-hours in the first quarter of this year alone, according to climate think tank Ember. That represented two-thirds of all curtailments in the period.

## What Comes Next

The June 10 deadline will be the next signal. If the government softens the proposed penalties or phases them in more gradually, investor confidence could stabilize. If it holds firm, the clean energy financing pipeline — already strained by rising interest rates and geopolitical uncertainty — could face a material slowdown.

India's 500 GW target was always ambitious. It now faces a credibility test that has nothing to do with technology or willpower, and everything to do with whether regulation can keep pace with a grid that is being remade in real time.

*Sources: Reuters, OilPrice.com, Ember Climate, Aurora Energy Research, AInvest*"""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "OilPrice.com", "Ember Climate", "Aurora Energy Research"])
    }
    
    return insert_article(article)


# =============================================================================
# ARTICLE 3: RBI's NRI-Focused Rupee Defense
# =============================================================================
def write_rbi_nri_article():
    print("\n=== ARTICLE 3: RBI NRI Rupee Defense Measures ===")
    
    # Image: RBI building or Sanjay Malhotra
    img_url, img_title, img_attr = source_image(
        person_name="Sanjay Malhotra (Reserve Bank of India)",
        wiki_searches=["Reserve Bank of India building Mumbai", "Reserve Bank of India headquarters"],
        pexels_query="Reserve Bank of India Mumbai"
    )
    
    img_caption = "The Reserve Bank of India headquarters in Mumbai, where policymakers unveiled measures targeting diaspora deposits"
    if not img_url:
        img_url, img_title, img_attr = source_image(
            wiki_searches=["Indian rupee currency", "Mumbai financial district"],
            pexels_query="Indian rupee currency notes"
        )
        if img_url:
            img_caption = "Indian rupee currency notes — the RBI's measures target diaspora deposits to shore up the weakened currency"
    
    if not img_url:
        print("  ⚠ No image found, skipping")
        return False
    
    headline = "The RBI Just Made It Cheaper for NRIs to Park Dollars in India. Here Is What Changed."
    subheadline = "India's central bank will cover the full hedging cost for banks raising diaspora deposits, raise NRI equity investment limits, and scrap capital gains tax on foreign-held government bonds — a package analysts say could pull in $40 billion."
    
    slug = "rbi-nri-deposits-fcnr-hedging-rupee-defense-diaspora-dollar-inflows-20260605"
    
    body = """The Reserve Bank of India on Friday rolled out a coordinated package of measures designed to attract dollar inflows from the Indian diaspora and foreign investors, marking the most aggressive currency defense since the rupee began its slide in February.

The rupee has lost nearly 5 percent this year, pushed to successive record lows by a surge in crude oil prices driven by the Middle East conflict, record foreign portfolio outflows from Indian equities, and a widening balance of payments gap that analysts estimate could reach $65 billion this fiscal year. On Friday, the currency gained 0.9 percent to close at 94.9450 per dollar — its best single-day performance in two months — as markets reacted to the measures.

## What Changes for NRIs

The most consequential measure for diaspora Indians is the RBI's decision to bear the full hedging cost for authorized dealer banks raising fresh three-to-five-year deposits under the Foreign Currency Non-Resident (Bank) scheme, known as FCNR(B). The facility runs until September 30, 2026.

FCNR(B) deposits allow NRIs to park foreign currency in Indian banks without exchange-rate risk — the deposit is denominated in dollars, pounds, euros, or other currencies and returned in the same currency at maturity. The catch has always been that the hedging cost for banks made these deposits expensive to offer at competitive rates. By absorbing that cost, the RBI is effectively subsidizing a channel for diaspora dollars to flow into India.

Banks will also be exempt from statutory fund requirements — the cash reserve ratio and statutory liquidity ratio — for these deposits, freeing up more of the inflow for productive lending.

## NRI Equity Limits Raised

The RBI also raised the limits for investment by NRIs and Overseas Citizens of India in equity instruments traded on Indian stock exchanges without requiring registration with the Securities and Exchange Board of India. The same facility is being extended to all individual Persons Resident Outside India at par with NRIs and OCIs — a significant expansion that opens Indian equity markets to a broader pool of overseas individual investors.

## Capital Gains Tax Scrapped on Government Bonds

In a parallel move announced by the Finance Ministry, India scrapped capital gains tax for foreign investors on interest or gains from the sale of government securities. Foreign investors were previously subject to a 12.5 percent long-term capital gains tax on listed bonds held for more than 12 months. The 20 percent tax on interest income has also been removed, effective from April 1, 2026.

The tax exemption applies to government bonds under the Fully Accessible Route, which the RBI expanded on Friday to include all new issuances of 15-year, 30-year, and 40-year government securities. These bonds are part of three global bond indexes, making them visible to institutional allocators worldwide.

## The Dollar Target

The RBI set no official dollar-inflow target, but Governor Sanjay Malhotra said the central bank expects "healthy" inflows. Analysts were more specific: Sachchidanand Shukla, group chief economist at Larsen & Toubro, estimated the measures could draw $40 to $60 billion. Kunal Sodhani, head of treasury at Shinhan Bank, called FCNR flows and the expanded bond access "the most likely to deliver the largest and fastest inflows," with a base-case estimate of $25 to $30 billion.

The combined effect matters because India's balance of payments is under unusual strain. Brent crude remains elevated near $96 a barrel, and foreign portfolio investors have pulled out record sums from Indian equities. The rupee's 5 percent decline this year follows a similar drop in 2025, making it one of the worst-performing emerging market currencies over the past 18 months.

## What It Means for the Diaspora

For NRIs weighing where to park savings, the calculus has shifted. FCNR(B) deposits now come with a central bank subsidy on hedging, no regulatory reserve requirements for banks, and a window that closes in September. The expanded equity access means NRIs can invest more in Indian markets without the friction of SEBI registration.

The question is whether these measures are sufficient or whether they are a down payment on more aggressive intervention later. RBI Governor Malhotra said curbs on capital outflows "are not under discussion," signaling that the central bank prefers to attract inflows rather than restrict them.

For now, the market has voted. The rupee posted its strongest session in two months, forward premiums plunged to the lowest level this fiscal year, and bank stocks rallied on expectations of cheaper funding.

*Sources: Reserve Bank of India, Reuters, The Hindu BusinessLine, HDFC Bank Research, Shinhan Bank*"""
    
    article = {
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "slug": slug,
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_url": img_url,
        "image_caption": img_caption,
        "image_attribution": img_attr,
        "is_editorial": False,
        "sources": json.dumps(["Reserve Bank of India", "Reuters", "The Hindu BusinessLine", "HDFC Bank Research"])
    }
    
    return insert_article(article)


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    results = []
    
    r1 = write_georgia_article()
    results.append(("Georgia Indian Americans", r1))
    
    r2 = write_grid_article()
    results.append(("Grid Penalty Crisis", r2))
    
    r3 = write_rbi_nri_article()
    results.append(("RBI NRI Rupee Defense", r3))
    
    print("\n=== SUMMARY ===")
    for name, success in results:
        status = "✓ Published" if success else "✗ Failed"
        print(f"  {status}: {name}")
    
    failed = sum(1 for _, s in results if not s)
    if failed:
        print(f"\n{failed} article(s) failed")
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} articles published successfully")
