#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-05 batch)
Publishes 3 news articles:
1. Trump confirms India-US trade deal is coming
2. Delhi hotel fire kills 21 including 17 foreign nationals
3. India's free trade blitz — 6-7 new FTAs expected next year
"""

import json, os, sys, time, uuid, re
from datetime import datetime, timezone
import requests
import urllib.parse

# Load environment
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

load_env(os.path.expanduser('~/.env.supabase'))
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

# ====== IMAGE SOURCING ======

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
            data = r.json()
            photos = data.get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error for '{query}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and > 5KB."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {r.status_code}, {ct}, {cl} bytes")
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated via GET: {size} bytes")
                return True
        print(f"  ✗ Image validation failed: {r.status_code}, {ct}, {cl} bytes")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


# ====== ARTICLE PUBLISHING ======

def publish_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', 'unknown')[:60]}...")
            return result[0]
        print(f"  ✓ Published (raw response)")
        return result
    else:
        print(f"  ✗ Publish failed: {r.status_code} — {r.text[:300]}")
        return None


# ====== ARTICLES ======

def build_articles():
    articles = []
    now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    # ---- ARTICLE 1: Trump-India Trade Deal ----
    print("\n=== Article 1: Trump-India Trade Deal ===")

    # Image: Trump — try Wikipedia
    img1 = fetch_wikipedia_person_image("Donald Trump")
    img1_caption = "US President Donald Trump speaks to reporters in the Oval Office"
    img1_attr = "Wikimedia Commons"

    # Also try Wikimedia Commons for Trump+Modi
    commons1 = fetch_wikimedia_commons_images("Trump Modi bilateral meeting", limit=3)
    # Prefer a Trump-Modi image if available and valid
    if commons1:
        for c in commons1:
            if validate_image(c["url"]):
                img1 = c["url"]
                img1_caption = "US President Donald Trump and Indian Prime Minister Narendra Modi at a bilateral meeting"
                break

    if not img1 or not validate_image(img1):
        img1 = fetch_pexels_image("US India trade diplomacy")
        img1_attr = "Pexels"
        img1_caption = "US and India flags symbolizing bilateral trade negotiations"
        if img1 and not validate_image(img1):
            img1 = None

    body1 = """The India-US trade deal that has eluded negotiators for the better part of two decades may finally be within reach. US President Donald Trump confirmed on Thursday that he expects the two countries to strike an agreement, calling Prime Minister Narendra Modi "a good friend" and expressing confidence that a deal is imminent.

"We will get to a deal because I like your prime minister a lot. He is a good friend of mine. We get along great, and we are gonna make a deal," Trump told reporters at the Oval Office on June 4.

The president's remarks came hours after a three-day round of face-to-face negotiations in New Delhi wrapped up between US Chief Negotiator Brendan Lynch and India's Additional Secretary of Commerce Darpan Jain. The talks, held from June 1 to 4, focused on giving final legal shape to an interim trade agreement whose framework was agreed upon in February.

## The Ambassador Says 99%

Trump's comments reinforced what US Ambassador to India Sergio Gor had said earlier in the week at CITI's 2026 India Conference in Mumbai. Gor revealed that the trade deal is "99% there," with only technical legal phrasing and implementation timelines left to resolve.

"We are 99% there, the last 1% we are working on. We are very optimistic that this will get done. It will be a win-win situation for both the US and India," Gor said, noting that the negotiations had progressed faster in 18 months than India's trade pact with the European Union, which took nearly 19 years.

Gor praised India's "incredible negotiators" and emphasized that the strong personal rapport between Trump and Modi has been the primary driver behind the deal's rapid advancement.

## What the Deal Covers

The interim agreement spans six critical areas: market access, non-tariff measures, customs and trade facilitation, investment promotion, economic security alignment, and broader bilateral trade framework issues. India's Commerce Ministry described the discussions as positive, with both sides committed to a mutually beneficial outcome.

Union Commerce Minister Piyush Goyal confirmed that the US delegation met with him on June 4 to review progress. India and the US are targeting bilateral trade of $500 billion by 2030, roughly double the current levels.

## The Shadow of New Tariffs

Yet even as the deal nears completion, a fresh challenge has surfaced. The US has proposed a 12.5% tariff on imports from countries it believes are not doing enough to address forced labour concerns. India has been included in the proposed list of 60 countries, a move that could make Indian exports more expensive in the American market if implemented.

Indian officials have clarified that no final decision has been taken on the forced-labour tariffs, and the US is expected to seek public feedback before acting. The proposal sits awkwardly alongside the trade deal's stated goal of reducing barriers between the two economies.

## A Broader Trade Blitz

The India-US talks are part of a larger trade push by New Delhi. The India-Oman Comprehensive Economic Partnership Agreement entered into force on June 1, offering duty-free access to nearly 98% of Indian exports. India has signed nine free trade agreements in the last three and a half years, covering 38 developed economies, and plans to roll out another six to seven FTAs in the coming year.

For the millions of Indians in the US — tech workers, entrepreneurs, students, and business owners — the trade deal carries direct implications. Lower tariffs, smoother customs procedures, and aligned investment frameworks could reshape how Indian businesses access the American market and how American companies invest in India.

The signing could come within weeks. The 99% may not be the hardest part — but in trade negotiations, the last 1% often is.

*Sources: Reuters, The Hindu BusinessLine, The Indian Eye, Dainik Bhaskar English, Bloomberg Law*"""

    articles.append({
        "headline": "Trump Says a Trade Deal With India Is Coming. The US Ambassador Says It Is 99% Done.",
        "subheadline": "Three days of face-to-face talks in New Delhi wrapped up on June 4. Both sides say only technical legal language remains before the interim pact can be signed.",
        "body": body1,
        "slug": "trump-india-us-trade-deal-99-percent-sergio-gor-brendan-lynch-20260605",
        "category": "news",
        "vertical": "news",
        "image_url": img1,
        "image_caption": img1_caption,
        "image_attribution": img1_attr,
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "The Hindu BusinessLine", "The Indian Eye", "Dainik Bhaskar English", "Bloomberg Law"])
    })

    # ---- ARTICLE 2: Delhi Hotel Fire ----
    print("\n=== Article 2: Delhi Hotel Fire ===")

    # Image: Search Wikimedia Commons for Delhi fire / Malviya Nagar
    img2 = None
    commons2 = fetch_wikimedia_commons_images("Delhi fire building rescue 2026", limit=5)
    if not commons2:
        commons2 = fetch_wikimedia_commons_images("Delhi fire rescue", limit=5)
    
    for c in commons2:
        if validate_image(c["url"]):
            img2 = c["url"]
            break

    img2_caption = "Rescue operations at a fire scene in Delhi"
    img2_attr = "Wikimedia Commons"
    
    if not img2:
        # Try Pexels for Delhi fire rescue
        img2 = fetch_pexels_image("fire rescue building smoke")
        img2_attr = "Pexels"
        img2_caption = "Firefighters battling a building fire during rescue operations"
        if img2 and not validate_image(img2):
            img2 = None

    body2 = """A fire at a budget hotel in south Delhi's Malviya Nagar neighbourhood on June 3 killed 21 people, including 17 foreign nationals who had come to India for medical treatment. It was the deadliest blaze the capital had seen since 2022, and it has renewed a familiar reckoning with the city's building safety failures.

The fire broke out around 8:48 in the morning at Flourish Stay B&B, a five-storey structure that housed a restaurant called Lemon Green on its ground floor and hotel rooms on the upper levels. Delhi Fire Services dispatched eight trucks and multiple rescue units after receiving the distress call. By the time the search-and-rescue operation was declared complete at 12:12 p.m., 47 people had been pulled from the building. Twenty-one were dead.

## Victims From Four Countries

The foreign nationals killed in the fire came from Liberia, Nigeria, Mozambique, and Bangladesh, according to police. Most had been staying at the hotel because of its proximity to a nearby private hospital where they or their relatives were receiving treatment. The hotel's listing as an affordable option near medical facilities had made it popular among international patients — a grim detail that now defines the scale of the tragedy.

Max Healthcare Group Medical Director Dr Sandeep Budhiraja said eight patients remained on ventilator support in critical condition. Most suffered severe asphyxiation from smoke inhalation rather than burns. Several sustained fractures after jumping from upper floors in desperation as the fire engulfed the building.

Video footage from the scene showed two women leaping from upper storeys as flames and thick black smoke billowed behind them. Bystanders rushed to catch them and carry survivors to safety as rescue teams worked their way through the structure.

## A Single Staircase and Sealed Windows

Investigators have identified a catalogue of safety violations that turned the building into a death trap. The hotel had only one staircase serving all five floors — no secondary exit, no fire escape. Some windows were found sealed shut, trapping occupants who might otherwise have reached safety. There was no internal fire protection system in place. The building's fire No Objection Certificate is now under scrutiny.

Police have lodged a criminal case and arrested the building's owner. The Sub-Divisional Magistrate of South Delhi confirmed that 26 of the 47 people rescued were still undergoing hospital treatment as investigations continued.

## Crackdown Promised, Again

Delhi's Chief Minister announced a city-wide crackdown against guest houses and commercial establishments operating in violation of fire safety norms and building by-laws. Non-compliant premises will be sealed and those responsible prosecuted, the Chief Minister's Office said in a post on X.

Prime Minister Narendra Modi offered condolences and announced financial assistance of ₹2 lakh to the families of the deceased. Home Minister Amit Shah said local authorities were engaged in relief operations. Foreign Minister S. Jaishankar confirmed that the Ministry of External Affairs was in contact with the embassies of the countries whose citizens were killed.

The Delhi fire follows a drearily familiar pattern. A 2019 fire at a factory in Anaj Mandi killed 43 people in a building with similarly illegal partitions and a single exit. In 2022, a fire at a commercial building near Mundka metro station killed 27. Each tragedy has been followed by promises of enforcement, inspections, and prosecutions. Each time, the enforcement has proven temporary and the violations have returned.

AIIMS Delhi received 13 patients from the fire, including 10 police personnel who were among the first to enter the building. Three bodies were transferred to the Burns and Plastic Surgery Department.

The fire at Flourish Stay B&B is not just a story about a building that burned. It is a story about a system that knew the building was unsafe and allowed it to operate anyway — because that is what the system does, until the next time.

*Sources: Reuters, Livemint, People, Latestly, NDTV, NewKerala*"""

    articles.append({
        "headline": "A Delhi Hotel Fire Killed 21 People. Seventeen Were Foreign Nationals Who Came for Medical Care.",
        "subheadline": "Flourish Stay B&B in Malviya Nagar had one staircase, sealed windows, and no fire protection. Victims came from Liberia, Nigeria, Mozambique, and Bangladesh.",
        "body": body2,
        "slug": "delhi-malviya-nagar-hotel-fire-21-dead-17-foreign-nationals-20260605",
        "category": "news",
        "vertical": "news",
        "image_url": img2,
        "image_caption": img2_caption,
        "image_attribution": img2_attr,
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "Livemint", "People", "Latestly", "NDTV", "NewKerala"])
    })

    # ---- ARTICLE 3: India's FTA Blitz ----
    print("\n=== Article 3: India FTA Blitz ===")

    # Image: India trade / commerce
    commons3 = fetch_wikimedia_commons_images("India trade commerce port", limit=5)
    img3 = None
    for c in commons3:
        if validate_image(c["url"]):
            img3 = c["url"]
            break
    
    img3_caption = "Indian commercial port handling international trade cargo"
    img3_attr = "Wikimedia Commons"

    if not img3:
        commons3b = fetch_wikimedia_commons_images("India commerce ministry New Delhi", limit=5)
        for c in commons3b:
            if validate_image(c["url"]):
                img3 = c["url"]
                img3_caption = "India's Commerce Ministry building in New Delhi"
                break

    if not img3:
        img3 = fetch_pexels_image("India shipping port trade containers")
        img3_attr = "Pexels"
        img3_caption = "A commercial port handling trade cargo"
        if img3 and not validate_image(img3):
            img3 = None

    body3 = """India is in the middle of the most aggressive trade diplomacy push in its history. Nine free trade agreements signed in three and a half years. The India-Oman deal that went live on June 1. A US trade pact that the American ambassador says is 99% done. And now, six to seven more FTAs expected to come into force in the next twelve months.

The numbers mark a sharp departure from a country that spent decades treating trade liberalisation with deep suspicion. India's previous record was the India-EU Free Trade Agreement signed in January 2026 — a deal that took 19 years of negotiations to close. The current pace is unrecognisable.

## The Oman Deal Sets the Template

The India-Oman Comprehensive Economic Partnership Agreement, which entered into force on June 1, 2026, offers duty-free access to nearly 98% of Indian exports. In return, India has reduced tariffs on Omani petrochemicals, minerals, and select industrial goods. The agreement is expected to benefit Indian exporters in textiles, gems and jewellery, food processing, and pharmaceuticals — sectors that employ millions of workers and anchor the export economy of several Indian states.

Oman is a relatively small trading partner, but the deal matters for what it signals. India is now willing to offer deep market access in exchange for reciprocal concessions — a negotiating posture that would have been politically unthinkable a decade ago.

## The US Deal: Eighteen Months vs Nineteen Years

The India-US Bilateral Trade Agreement is the centrepiece of the current strategy. US Ambassador Sergio Gor confirmed this week that the deal is "99% there," with only technical legal phrasing left to resolve. A US delegation led by Chief Negotiator Brendan Lynch spent June 1 to 4 in New Delhi hammering out the details with India's chief negotiator, Additional Secretary Darpan Jain.

The interim agreement covers market access, non-tariff measures, customs and trade facilitation, investment promotion, and economic security alignment. India and the US are targeting bilateral trade of $500 billion by 2030, roughly double the current level.

President Trump confirmed on June 4 that he expects a deal, calling Prime Minister Modi "a good friend." Commerce Minister Piyush Goyal described the talks as productive.

## The Broader Picture: 38 Countries and Counting

India's nine recent FTAs cover 38 developed economies. The roster includes the UK Comprehensive Economic and Trade Agreement, the New Zealand FTA, and the EFTA Trade and Economic Partnership Agreement with Switzerland, Norway, Iceland, and Liechtenstein — the last of which includes a $100 billion investment commitment over 15 years.

Three to four more agreements are expected to be executed in the coming year. Another two to three are set to come into force within six months. Commerce Ministry officials have signalled that negotiations are underway with multiple partners across the Middle East, Southeast Asia, and Latin America.

## What It Means for the Diaspora

For the 18 million-strong Indian diaspora, the FTA blitz carries immediate consequences. Lower tariffs make Indian goods — from spices and textiles to pharmaceuticals and IT services — cheaper and more accessible in overseas markets. Investment frameworks aligned under bilateral agreements create smoother pathways for diaspora entrepreneurs to operate across borders.

The India-Oman CEPA, for instance, benefits the estimated 780,000 Indians living in Oman, many of whom work in construction, retail, and services. The US deal, once signed, could reshape the economics of Indian-American businesses that depend on cross-border trade in technology, manufacturing, and professional services.

India's trade strategy has shifted from cautious protectionism to something closer to strategic ambition. The next 12 months will test whether the ambition can hold — against domestic opposition to imported goods, against the complications of forced-labour tariff proposals from Washington, and against the geopolitical headwinds of a war that has reshaped global energy markets.

But the trajectory is clear. India is trading faster, wider, and deeper than at any point in its post-independence history.

*Sources: Reuters, The Indian Eye, AInvest, Dainik Bhaskar English, The Hindu BusinessLine*"""

    articles.append({
        "headline": "India Has Signed Nine Trade Deals in Three Years. Six More Are Coming.",
        "subheadline": "The India-Oman CEPA went live on June 1, the US deal is 99% done, and Commerce Ministry officials say three to four more agreements will be executed in the next twelve months.",
        "body": body3,
        "slug": "india-free-trade-agreements-fta-blitz-oman-us-uk-eu-20260605",
        "category": "news",
        "vertical": "news",
        "image_url": img3,
        "image_caption": img3_caption,
        "image_attribution": img3_attr,
        "status": "published",
        "published_at": now_iso,
        "is_editorial": False,
        "sources": json.dumps(["Reuters", "The Indian Eye", "AInvest", "Dainik Bhaskar English", "The Hindu BusinessLine"])
    })

    return articles


def main():
    print("=" * 60)
    print("The Videshi — News Writer Run")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    articles = build_articles()

    print(f"\n{'='*60}")
    print(f"Publishing {len(articles)} articles...")
    print(f"{'='*60}")

    published = 0
    for i, article in enumerate(articles):
        print(f"\n--- Publishing Article {i+1}/{len(articles)} ---")
        print(f"  Headline: {article['headline'][:80]}...")
        print(f"  Slug: {article['slug']}")
        print(f"  Category: {article['category']}")
        print(f"  Image URL: {str(article.get('image_url', 'None'))[:80]}...")

        if not article.get('image_url'):
            print("  ⚠ No image found — publishing without image")

        result = publish_article(article)
        if result:
            published += 1
        else:
            print(f"  ✗ FAILED to publish article {i+1}")

    print(f"\n{'='*60}")
    print(f"DONE: {published}/{len(articles)} articles published")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
