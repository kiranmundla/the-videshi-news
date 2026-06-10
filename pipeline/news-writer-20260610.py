#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-06-10 batch)
Writes 3 news articles, sources images from Wikipedia/Commons/Pexels,
inserts into Supabase with status="review".
"""

import os, json, re, time, uuid, urllib.parse, subprocess
import requests
from datetime import datetime, timezone

# Load env
def load_env(path):
    env = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip()
    return env

supabase_env = load_env(os.path.expanduser('~/.env.supabase'))
pexels_env = load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = supabase_env['SUPABASE_URL']
SUPABASE_KEY = supabase_env['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = pexels_env['PEXELS_API_KEY']

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- Image sourcing functions ---

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
    """Search Wikimedia Commons for CC-licensed images. Returns list of {url, title}."""
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
            for page_id, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                url = ii.get("thumburl") or ii.get("url")
                mime = ii.get("mime", "")
                width = ii.get("width", 0)
                if url and "image" in mime and width > 200:
                    results.append({"url": url, "title": page.get("title", "")})
            if results:
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []


def fetch_pexels_image(query):
    """Search Pexels for a relevant image. Returns URL or None. Uses curl to avoid 403."""
    try:
        result = subprocess.run(
            ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
             f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            if photos:
                url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{query}': {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


def validate_image_url(url):
    """Validate that image URL returns HTTP 200 with image content-type and >5KB."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ✗ Banned source: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            print(f"  ✓ Image validated: {cl} bytes, {ct}")
            return True
        # Try GET if HEAD doesn't work well
        r2 = requests.get(url, timeout=10, stream=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get('Content-Type', '')
        cl2 = int(r2.headers.get('Content-Length', 0))
        r2.close()
        if r2.status_code == 200 and 'image' in ct2:
            print(f"  ✓ Image validated (GET): {cl2} bytes, {ct2}")
            return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False


def source_image(person_name=None, wiki_search=None, pexels_query=None):
    """Multi-source image search. Returns (url, caption, attribution) or (None, None, None)."""
    # 1. Try Wikipedia for person
    if person_name:
        img = fetch_wikipedia_person_image(person_name)
        if img and validate_image_url(img):
            return img, f"{person_name}", "Wikimedia Commons"

    # 2. Try Wikimedia Commons
    if wiki_search:
        results = fetch_wikimedia_commons_images(wiki_search)
        for r in results:
            if validate_image_url(r["url"]):
                title = r["title"].replace("File:", "").replace(".jpg", "").replace(".png", "").replace("_", " ")
                return r["url"], title[:80], "Wikimedia Commons"

    # 3. Try Pexels (only for non-person topics)
    if pexels_query and not person_name:
        img = fetch_pexels_image(pexels_query)
        if img and validate_image_url(img):
            return img, pexels_query.title(), "Pexels"

    return None, None, None


def insert_article(article):
    """Insert article into Supabase p2_articles table."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return data[0]
        print(f"  ✓ Inserted (no return data)")
        return data
    else:
        print(f"  ✗ Insert failed ({r.status_code}): {r.text[:300]}")
        return None


# ============================================================
# ARTICLE 1: Iran Retaliates Against US Bases
# ============================================================

def write_article_1():
    print("\n=== ARTICLE 1: Iran Retaliates Against US Bases ===")

    headline = "Iran Just Hit US Bases in Jordan, Kuwait and Bahrain. India Has 8 Million Reasons to Worry."
    subheadline = "The biggest military escalation since the April ceasefire puts India's Gulf diaspora, oil supply chain and economic recovery on a razor's edge."
    slug = "iran-attacks-us-bases-jordan-kuwait-bahrain-india-gulf-diaspora-oil-crisis-20260610"
    category = "news"
    vertical = "news"

    body = """Iran's Revolutionary Guards launched long-range missiles at the US al-Azraq base in Jordan and sent drones at American installations in Kuwait and Bahrain on Wednesday, in the most violent exchange between Washington and Tehran since the two sides agreed to a tenuous ceasefire in April.

The attacks — targeting F-35 jet hangars, a command-and-control centre in Jordan, the Ali Al Salem base in Kuwait and the US Fifth Fleet headquarters in Bahrain — came hours after the United States struck nearly 20 Iranian air defence and radar sites near the Strait of Hormuz.

Jordan said it intercepted five Iranian missiles. Bahrain sounded air raid sirens. Kuwait's army engaged hostile aerial targets and urged the public to follow safety instructions. A US official said initial assessments showed nearly all incoming missiles and drones were intercepted, with no immediate reports of harm to American personnel.

## How It Started

The spiral began on Monday when an Iranian one-way attack drone brought down a US Apache helicopter near Oman's coast while it patrolled the Strait of Hormuz. The two American pilots were rescued uninjured by a US Navy surface drone after two hours in the water.

President Trump, who initially told The Wall Street Journal the incident "wasn't a big deal," then ordered retaliatory strikes. "I believe the response should be very strong, very powerful, and that's what this one is," he told ABC News.

US Central Command described the four-hour operation as "a proportional response to unjustified Iranian aggression," targeting air defence, ground control stations and surveillance radar sites near Qeshm island and the port city of Sirik.

Iran hit back within hours, warning it was ready to deliver a "crushing and decisive" response to any further American attack.

## India's Stakes in the Crossfire

India has roughly 8.7 million citizens living and working across the Gulf states — the largest expatriate workforce in the region. Kuwait, Bahrain and the UAE host the densest concentrations of Indian labourers, nurses, engineers and professionals.

Every escalation in this theatre directly threatens their safety. Just days ago, seven Indian workers were killed when a truck struck their minibus on Dubai's Emirates Road. The Indian embassy in each Gulf state has activated helpline numbers, but with missiles flying over civilian airspace, the calculus has changed.

Then there is oil. India ships in about 90% of its crude and sourced more than 40% of those imports through the Strait of Hormuz before the February conflict. Oil prices climbed about 1% in early Asian trade on Wednesday, with Brent crude at $92.29 a barrel. Fitch expects Brent to stay at $100-110 per barrel through July if the strait remains closed.

Oil Minister Hardeep Singh Puri said on Monday that India has reserves to last 76-80 days and expects prices to drop in the coming months. But he also warned the situation could become "worrying" if the crisis expands to other theatres — which is precisely what happened hours later.

## The Economic Blow

India's oil-and-gas import bill jumped 53% in April from March. HSBC expects the country's balance of payments deficit to balloon to about $65 billion in 2026-27. The rupee has fallen to a record low of 95 against the dollar. State retailers have raised petrol and diesel prices four times since mid-May — a cumulative hike of nearly 8%.

"India is set for a series of supply shocks," said Michael Langham, emerging markets economist at Aberdeen Investments. Apart from oil, India faces fertiliser supply disruptions from the war, just as farmers brace for an El Niño season that the IMD says could push monsoon rainfall to 90% of the long-period average — its lowest forecast in three years.

The RBI, which held rates steady last week, is now navigating a treacherous path. Inflation is expected to breach 4% in May for the first time in 15 months. Rate hike bets are rising. The "rare Goldilocks" phase that RBI Governor Sanjay Malhotra celebrated at the end of last year now looks like a distant memory.

## What Comes Next

The escalation shatters any remaining illusion that a US-Iran deal is imminent. Trump has repeatedly said the two sides are close to an agreement, but the ceasefire that took hold in April has now collapsed in all but name. Iran demands the lifting of sanctions, the release of frozen assets and recognition of its control over the strait. Washington wants a deal that prevents Iran from developing a nuclear weapon.

For the 8.7 million Indians across the Gulf, for the truck drivers fuelling at newly expensive pumps, for the housewives paying more for cooking gas — the war just got closer. And there is no diplomatic off-ramp in sight.

*Sources: Reuters, USA Today, Fitch Ratings, India Ministry of External Affairs*"""

    # Image sourcing — try Commons for Strait of Hormuz / Gulf military
    print("  Sourcing image...")
    img_url, img_caption, img_attr = source_image(
        wiki_search="Strait of Hormuz military",
        pexels_query="oil tanker strait"
    )
    if not img_url:
        img_url, img_caption, img_attr = source_image(
            wiki_search="US military base Persian Gulf",
            pexels_query="military aircraft carrier"
        )
    if not img_url:
        img_url, img_caption, img_attr = source_image(
            wiki_search="USS aircraft carrier Persian Gulf"
        )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": vertical,
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption or "Military vessels near the Strait of Hormuz",
        "image_attribution": img_attr or "Wikimedia Commons",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Reuters", "USA Today", "Fitch Ratings", "India Ministry of External Affairs"]),
    }

    return insert_article(article)


# ============================================================
# ARTICLE 2: India Inflation Breaches 4%
# ============================================================

def write_article_2():
    print("\n=== ARTICLE 2: India Inflation Breaches 4% ===")

    headline = "India's Inflation Is About to Breach 4% for the First Time in 15 Months. The War Bill Has Arrived."
    subheadline = "Four fuel price hikes in May, a heatwave that crushed vegetable supply and a weakening rupee are ending India's longest low-inflation streak in years."
    slug = "india-inflation-breaches-4-percent-15-months-fuel-hikes-vegetables-war-20260610"
    category = "news"
    vertical = "news"

    body = """India's consumer price inflation is expected to have hit the Reserve Bank of India's medium-term target of 4% in May, ending a 15-month streak of below-target readings that had given the economy rare breathing room.

A Reuters poll of 38 economists forecasts the annual change in the consumer price index rose to 4.0% in May from 3.48% in April. The official number is due on June 12. Nobody expects a pleasant surprise.

## The Double Squeeze: Fuel and Food

The culprits are painfully visible to anyone who buys groceries or fills a tank in India.

State-owned fuel retailers raised petrol and diesel prices four times in May alone — the first increases in over a year, after the government held the line through state elections. Petrol is now roughly 7.8% more expensive than it was in mid-April. Diesel is up 8.6%.

The hikes reflect the pass-through of surging crude oil costs. Global oil prices have climbed 40% since the US-Israeli war on Iran restricted shipments through the Strait of Hormuz in February. India imports about 90% of its crude, making it one of the most exposed economies in the world.

Union Bank of India estimates transport inflation jumped to 4.15% in May from negative 0.01% in April — a swing that alone lifted its contribution to headline inflation by 36 basis points.

On the food side, a brutal heatwave across northern and central India crushed vegetable supply. Tomato, onion and potato prices — the politically sensitive trio that has toppled Indian governments in the past — rebounded sharply after months of deflation. Elevated temperatures disrupted cold chains and accelerated spoilage.

"Persistence of elevated temperatures across several regions and war-led constraints have adversely impacted the supply of commodities," said Kanika Pasricha, chief economic adviser at Union Bank of India. "All segments of food inflation likely clocked positive month-on-month momentum."

## The End of the Goldilocks Phase

At the end of last year, RBI Governor Sanjay Malhotra spoke of a "rare Goldilocks" moment for India — inflation falling, growth holding steady, the economy humming along. That window is now closing.

The central bank held rates steady at its June meeting, as expected, but the commentary was more cautious. Malhotra said underlying inflation pressures remained benign but warned that "second-round effects warranted vigilance."

Interest rate swap markets tell a different story. They are now pricing in at least 25 basis points of rate hikes over the next three months and more than 75 basis points over the next year. For homebuyers with floating-rate loans and businesses dependent on cheap credit, this is the early tremor before the quake.

## Compounding Shocks

The inflation breach does not arrive in isolation. It lands alongside a cascade of supply-side pressures that are all connected to the same geopolitical crisis.

India's oil-and-gas import bill jumped 53% in April. The rupee hit a record low of 95 against the dollar. Foreign portfolio investors have pulled billions out of Indian equities. HSBC expects India's balance of payments deficit to swell to roughly $65 billion in the current fiscal year.

And looming over all of it is El Niño. The Nino 3.4 index crossed the drought threshold of +0.80°C as of June 7. The IMD has already downgraded its monsoon forecast to 90% of the long-period average — the weakest outlook in three years. A poor monsoon would push food prices higher still, precisely when the economy can least afford it.

"India is set for a series of supply shocks," said Michael Langham of Aberdeen Investments. "The ability of the RBI to look through the energy price shock will be increasingly difficult given the overlapping nature of these supply shocks."

## What It Means for NRIs

For the Indian diaspora sending money home, the calculus is shifting. The rupee's weakness means remittances buy more — NRI remittances hit a record $43.5 billion in the January-March quarter. But the purchasing power of those rupees is eroding as prices rise across the board.

For families in India, the squeeze is immediate. Cooking gas subsidies have been cut. Fuel is more expensive. Vegetables cost more at the mandi. And the monsoon may not bring relief.

The 15-month respite was real. It is now over. The question is not whether inflation will rise, but how high and for how long.

*Sources: Reuters, Reserve Bank of India, Union Bank of India, India Meteorological Department, HSBC, Aberdeen Investments*"""

    # Image sourcing — try for RBI or Indian market/economy
    print("  Sourcing image...")
    img_url, img_caption, img_attr = source_image(
        wiki_search="Reserve Bank of India building Mumbai",
        pexels_query="india market vegetables prices"
    )
    if not img_url:
        img_url, img_caption, img_attr = source_image(
            person_name="Sanjay Malhotra RBI Governor",
            wiki_search="Indian rupee currency",
            pexels_query="india fuel petrol pump"
        )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": vertical,
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption or "Reserve Bank of India headquarters in Mumbai",
        "image_attribution": img_attr or "Wikimedia Commons",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Reuters", "Reserve Bank of India", "Union Bank of India", "India Meteorological Department", "HSBC", "Aberdeen Investments"]),
    }

    return insert_article(article)


# ============================================================
# ARTICLE 3: India Inc Shrinkflation
# ============================================================

def write_article_3():
    print("\n=== ARTICLE 3: India Inc Shrinkflation ===")

    headline = "India's Consumer Giants Are Shrinking Your Packet of Chips. The War Made Them Do It."
    subheadline = "From Dabur to Maruti, Indian companies are raising prices or quietly reducing pack sizes as surging oil, freight costs and a weak rupee squeeze margins."
    slug = "india-shrinkflation-price-hikes-dabur-maruti-hindustan-unilever-iran-war-20260610"
    category = "news"
    vertical = "news"

    body = """The pack of biscuits looks the same on the shelf. The price tag has not changed. But pick it up and something feels off. It is lighter.

Welcome to shrinkflation, India's quiet corporate response to a war that has sent input costs spiralling and left consumer demand too fragile to absorb a straightforward price increase.

## The Squeeze on India Inc

Consumer goods makers Hindustan Unilever, Godrej Consumer Products and Dabur India have rolled out low- to mid-single-digit price hikes across categories. Britannia Industries is preparing similar moves. But in the mass-market segments — the 10-rupee and 20-rupee packs that account for the bulk of rural and semi-urban sales — companies are doing something different: keeping the price and shrinking the product.

"We are reducing grammage because we can't breach those price points," said Mohit Malhotra, global CEO at Dabur, in comments to Reuters.

It is a familiar playbook in India, where decades of experience have taught FMCG companies that the 10-rupee price barrier is nearly sacred. Cross it, and a significant chunk of your customer base simply switches to a cheaper brand or stops buying.

The trigger this time is the US-Israeli war on Iran. The conflict, now in its fourth month, has disrupted trade routes through the Strait of Hormuz, pushed crude oil prices up 40%, sent freight and insurance costs soaring and weakened the rupee to a record low of 95 against the dollar. India imports nearly 90% of its oil, and the cost ripples through every supply chain in the country — from the palm oil in soap to the diesel in delivery trucks.

## Cars, Flights and Cooking Gas

The squeeze is not limited to grocery aisles.

Automakers Maruti Suzuki, Mahindra & Mahindra, Tata Motors and Hyundai Motor India have all hiked vehicle prices. "We were left with no choice," said Partho Banerjee, Maruti's senior executive officer for marketing and sales, adding that raising prices was "not good for customers, especially first-time buyers."

Airlines IndiGo and Air India are trimming capacity, particularly on fuel-heavy international routes, and raising fares to offset higher aviation turbine fuel costs. State-owned fuel retailers have raised petrol and diesel prices four times since mid-May — a cumulative 8% increase.

Even cooking gas, the lifeline of Indian kitchens, has not been spared. The government cut subsidies on LPG cylinders for households, pushing the effective price higher just as the summer heat drives up demand.

## The Consumer Is Already Stretched

The price hikes land on consumers whose budgets are already strained. India's retail inflation is expected to breach the 4% threshold in May for the first time in 15 months. Food prices are rising because of heatwave-driven supply disruptions. The rupee's record weakness makes everything imported — from electronics to edible oil — more expensive.

"We are among the world's most vulnerable countries," said economist Jayati Ghosh, warning that higher oil and fertiliser costs, weaker Gulf demand, softer remittances and potential capital outflows could simultaneously stoke inflation and slow growth.

India's opposition Congress party released a 76-page report this week accusing the Modi government of benefiting from years of low oil prices by raising taxes and collecting windfall gains, rather than passing relief to consumers. "Please don't do that. Swallow that bitter pill for a little while because you have been enjoying the fruits," said Rajeev Gowda, a senior Congress leader.

## The Diaspora Dimension

For NRI families visiting India this summer, the sticker shock will be real. Flight tickets are more expensive. Hotel rates in metros have climbed. The 10-rupee samosa might still cost 10 rupees, but it is smaller than it was in January.

For those sending money home, the math is more complicated. The weak rupee means more purchasing power per dollar — NRI remittances hit a record $43.5 billion in a single quarter recently. But the value of those rupees is being steadily eroded by the price hikes on everything from milk to motorcycle fuel.

Indian companies have navigated input cost cycles before. The oil shock of 2022, the commodity spike during COVID — each produced a round of grammage cuts and selective price increases that eventually unwound as costs normalised.

But this time the shock has a geopolitical ceiling. Oil prices cannot fall meaningfully until the Strait of Hormuz reopens, and there is no timeline for that. The El Niño weather pattern is expected to suppress monsoon rainfall, keeping food inflation elevated. And the rupee has no obvious floor until foreign portfolio flows stabilise.

For now, the pack gets lighter. The bill gets heavier. And the war that started 12,000 kilometres away in the Persian Gulf continues to tax every Indian household, one reduced grammage at a time.

*Sources: Reuters, Dabur India, Maruti Suzuki, Hindustan Unilever, India Ministry of External Affairs, Congress Party*"""

    # Image sourcing — Pexels for grocery/consumer goods (no named person)
    print("  Sourcing image...")
    img_url, img_caption, img_attr = source_image(
        wiki_search="Indian grocery store FMCG",
        pexels_query="india grocery store shopping"
    )
    if not img_url:
        img_url, img_caption, img_attr = source_image(
            pexels_query="supermarket shelves products"
        )

    article = {
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body": body,
        "category": category,
        "vertical": vertical,
        "status": "review",
        "is_editorial": False,
        "image_url": img_url,
        "image_caption": img_caption or "Grocery products on shelves in an Indian store",
        "image_attribution": img_attr or "Pexels",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "sources": json.dumps(["Reuters", "Dabur India", "Maruti Suzuki", "Hindustan Unilever", "Congress Party"]),
    }

    return insert_article(article)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("The Videshi — News Writer (2026-06-10)")
    print("=" * 60)

    results = []
    for writer_fn in [write_article_1, write_article_2, write_article_3]:
        try:
            result = writer_fn()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(None)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for i, r in enumerate(results, 1):
        if r:
            slug = r.get('slug', 'unknown') if isinstance(r, dict) else 'inserted'
            print(f"  Article {i}: ✓ {slug}")
        else:
            print(f"  Article {i}: ✗ FAILED")
    print("=" * 60)
