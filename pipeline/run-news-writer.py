#!/usr/bin/env python3
"""News writer for The Videshi — publishes 3 articles to Supabase."""

import os, json, sys, time, re, urllib.parse, subprocess
import requests
from datetime import datetime, timezone

# ── Load env ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            v = v.strip().strip('"').strip("'")
            os.environ[k.strip()] = v

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image sourcing ──
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
    """Fetch image from Pexels. Use curl internally (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None

    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for p in photos:
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('large')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns 200 with image content-type and >5KB."""
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
        # Try GET if HEAD didn't return content-length
        if r.status_code == 200 and 'image' in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True,
                            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated (GET): {size} bytes")
                return True
        print(f"  ✗ Image validation failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
    return False


def get_image(person_name=None, pexels_query=None, pexels_fallback=None):
    """Get image following hierarchy: Wikipedia person → Pexels → None."""
    url = None
    attribution = None

    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image(url):
            return url, "Wikimedia Commons"

    if pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url and validate_image(url):
            return url, "Pexels"

    return None, None


def publish_article(article):
    """Publish article to Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article
    )
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ Published: {result[0].get('headline', '')[:60]}")
            return True
        print(f"  ✓ Published (no body returned)")
        return True
    else:
        print(f"  ✗ Publish failed ({r.status_code}): {r.text[:200]}")
        return False


# ── Articles ──

articles = []

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: India's Weakest Monsoon in 11 Years
# ──────────────────────────────────────────────────────────────────────
print("\n=== Article 1: Monsoon Forecast ===")

img1, attr1 = get_image(pexels_query="india monsoon rain farmer field", pexels_fallback="monsoon rain india agriculture")

monsoon_body = """India is bracing for its weakest monsoon season in over a decade, and the timing could not be worse.

The India Meteorological Department on Friday downgraded its forecast for the June-to-September southwest monsoon to 90 percent of the long-period average — below its earlier April estimate of 92 percent and the lowest projection since 2015. The monsoon delivers roughly 70 percent of India's annual rainfall, replenishing the reservoirs, rivers, and groundwater systems that sustain nearly half the country's farmland.

The culprit is a developing El Niño in the equatorial Pacific Ocean, which is expected to strengthen to moderate or strong intensity during the second half of the monsoon season, suppressing the rain-bearing systems that the subcontinent depends on.

**What the numbers mean for food and prices**

M. Ravichandran, secretary of India's earth sciences ministry, told reporters that June alone is expected to bring below-normal rainfall across most of the country — less than 92 percent of the long-period average. Central India, South Peninsular India, Northwest India, and the critical monsoon core zone, which covers the heartland of rain-fed agriculture, are all projected to receive deficient rains. Only the Northeast is expected to see normal rainfall.

For an economy where nearly half of all farmland lacks irrigation, the forecast is a direct threat to crop output and food prices. Gaura Sengupta, chief economist at IDFC First Bank, warned that a deficient monsoon "particularly in the crucial July-August months, can add to the pressure and push up inflation closer to an average of 5.5 percent if food inflation spikes." India's retail inflation stood at 3.48 percent in April, but the outlook is now clouded by a convergence of forces: elevated global energy prices from the Iran war, a depreciating rupee, and the prospect of crop failures.

The finance ministry's own monthly economic report, released the same day, acknowledged that the confluence of fuel price hikes, a below-normal monsoon, and the ongoing Strait of Hormuz disruption "calls for sustained policy vigilance." It described the Hormuz closure as the "single most consequential variable" for India's price and external outlook.

**Heatwave conditions intensify**

The monsoon delay is compounding a brutal summer. Several Indian states are enduring temperatures above 45 degrees Celsius, with the IMD warning of above-normal heatwave days in June across Uttar Pradesh, Haryana, Punjab, Bihar, Odisha, Chhattisgarh, Gujarat, and Andhra Pradesh. Parts of Maharashtra, Telangana, and Tamil Nadu are also expected to see increased heatwave activity.

The IMD said both maximum and minimum temperatures will remain above normal for most of the country during June, offering little overnight relief in regions already under severe heat stress.

**What it means for the diaspora**

For NRIs with family in rural India, the forecast raises immediate concerns about agricultural income and food security. Remittance flows to rural households could come under pressure if crop losses materialize, particularly in kharif-season staples like rice, pulses, and oilseeds that depend heavily on monsoon timing.

India's $4 trillion economy is already navigating the headwinds of an energy shock. A failed monsoon would add food inflation to the mix, potentially forcing the Reserve Bank of India to rethink the rate cuts that markets have been counting on. The next few weeks of rainfall data will determine whether this remains a forecast or becomes a crisis.

*Sources: Reuters, India Meteorological Department press conference (May 29), India Finance Ministry monthly economic report (May 30), The Hindu Business Line*"""

articles.append({
    "headline": "India Just Forecast Its Weakest Monsoon in 11 Years. El Niño Is Only Part of the Problem.",
    "subheadline": "The IMD downgraded its rainfall forecast to 90% of normal as food inflation fears collide with the Iran war's energy shock.",
    "body": monsoon_body,
    "slug": "india-weakest-monsoon-11-years-el-nino-inflation-food-prices-20260531",
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "For NRIs with family in rural India, a failed monsoon threatens agricultural income and food security. Remittance flows to rural households could come under pressure if crop losses hit kharif staples. A weaker rupee and higher food inflation would squeeze household budgets across the country.",
    "tags": ["monsoon", "el-nino", "inflation", "imd", "agriculture", "food-prices"],
    "urgency": "high",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img1,
    "image_attribution": attr1,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"},
        {"name": "India Finance Ministry", "url": "https://finmin.nic.in/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/"}
    ])
})

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: Delhi HC Fines Google Over Hindware Trademark
# ──────────────────────────────────────────────────────────────────────
print("\n=== Article 2: Delhi HC Google Ruling ===")

img2, attr2 = get_image(pexels_query="google search engine laptop india", pexels_fallback="online advertising digital marketing")

google_body = """A Delhi High Court ruling has rattled India's digital advertising market by declaring that Google's practice of auctioning trademarked brand names as advertising keywords amounts to trademark infringement — and ordering the tech giant to pay ₹30 lakh ($31,600) in damages to sanitaryware maker Hindware.

The judgment, delivered on May 22 by Justice Mini Pushkarna, permanently restrains Google LLC and Google India from using Hindware's registered trademarks as advertising keywords. It rejected Google's defense that it is merely an intermediary entitled to safe-harbor protection, ruling instead that Google's keyword auction system constitutes an "unfair practice" that exploits the "distinctive character or repute" of a well-known trademark.

**What Google was doing**

The case, which dates back to 2013, centered on Google's AdWords platform. Hindware alleged that competitors Grohe and Cera — assisted by digital agency Omkara Infoweb — had purchased "Hindware" and variations like "Hindware Sanitary" as keywords on Google Ads. When users searched for Hindware, competitors' sponsored links appeared as the first results, above Hindware's own website.

While Grohe, Cera, and Omkara settled with Hindware during the trial, Google contested the case to the end. The court found that Google actively sold, suggested, and auctioned the use of Hindware's trademark "without any authorisation from the proprietor" — going beyond the role of a passive intermediary.

"The manner in which Google operates its AdWords Policy makes it clear that Google sells or auctions the use of the trademark," the judgment states.

**Why Indian business leaders are celebrating**

The ruling has drawn vocal support from some of India's most prominent entrepreneurs. Nithin Kamath, founder of brokerage firm Zerodha, said his brand had suffered from the same practice for years and that the ruling "now opens up a route for legal recourse."

Anupam Mittal, founder of matchmaking platform Shaadi.com, was blunter: "You create the brand. Someone else bids on it. Google takes the fee." He said the ruling "could change the economics of online advertising for millions of businesses."

Legal experts say the decision could trigger a wave of similar cases across India, where Google counts more users than in any other market except for the United States. If other brand owners follow Hindware's lead, Google may be forced to build trademark-verification systems at scale before allowing keyword bidding — a significant compliance burden that could slow its ad-auction machinery in one of its most critical growth markets.

**The bigger picture**

The case has implications beyond India. Courts in the European Union have previously ruled that keyword advertising on trademarked terms does not automatically constitute infringement, placing the Delhi High Court's decision at odds with international precedent. Google's statement said it operates in accordance "with all local laws" and works to explain its position in cases where orders are "overbroad or inconsistent" with its policies — a signal that an appeal is likely.

For now, the ruling gives Indian brand owners a powerful new legal weapon in the fight over search-engine real estate. The ₹30 lakh fine is nominal by Google's standards, but the precedent it sets is not. If upheld, it could fundamentally alter how keyword advertising works in India's $8 billion digital ad market.

**The diaspora angle**

For NRI entrepreneurs running businesses in India or targeting Indian consumers through Google Ads, the ruling introduces new uncertainty. Companies that have been bidding on competitors' brand names as keywords may need to rethink their search advertising strategies. At the same time, Indian-origin brands sold globally — from spice companies to fashion labels — now have a legal framework to challenge trademark misuse on Google's platform.

*Sources: Reuters, Inc42, Bar and Bench, The Hindu Business Line, Storyboard18*"""

articles.append({
    "headline": "A Delhi Court Just Ruled Google's Keyword Ads Violate Trademark Law. India's Founders Are Cheering.",
    "subheadline": "The Delhi HC fined Google ₹30 lakh for letting rivals bid on Hindware's brand name. Zerodha and Shaadi.com founders say it could reshape online advertising.",
    "body": google_body,
    "slug": "delhi-hc-google-hindware-trademark-keyword-ads-ruling-zerodha-shaadi-20260531",
    "category": "news",
    "vertical": "business",
    "diaspora_angle": "For NRI entrepreneurs running businesses in India or targeting Indian consumers through Google Ads, the ruling introduces new uncertainty. Companies bidding on competitors' brand names may need to rethink strategies. Indian-origin brands sold globally now have a legal framework to challenge trademark misuse on Google's platform.",
    "tags": ["google", "trademark", "delhi-high-court", "hindware", "digital-advertising", "zerodha"],
    "urgency": "medium",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img2,
    "image_attribution": attr2,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/delhi-hc-fines-google-for-infringing-hindwares-trademark/"},
        {"name": "Bar and Bench", "url": "https://www.barandbench.com/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Storyboard18", "url": "https://storyboard18.com/"}
    ])
})

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 3: India Cuts Fuel Export Duties
# ──────────────────────────────────────────────────────────────────────
print("\n=== Article 3: Fuel Export Duty Cut ===")

img3, attr3 = get_image(pexels_query="oil refinery India industrial", pexels_fallback="petroleum refinery fuel export")

fuel_body = """India will cut export duties on petrol, diesel, and aviation turbine fuel starting June 1, the finance ministry announced on Saturday, in the latest adjustment to the emergency levies it imposed in March to keep fuel available at home during the Iran war.

The new rates: ₹1.5 per litre on petrol exports (down sharply from previous levels), ₹13.5 per litre on diesel, and ₹9.5 per litre on aviation turbine fuel. There is no change to excise duties on fuel sold for domestic consumption.

The cuts, described as a routine fortnightly revision based on average international prices since the last review on May 16, come at a moment when the global oil market is flashing some of its most alarming signals since the war began.

**The backstory**

India introduced the export levies — formally called Special Additional Excise Duty and Road and Infrastructure Cess — on March 27, 2026, weeks after the U.S.-Iran conflict began disrupting shipping through the Strait of Hormuz. The explicit goal was to "ensure domestic availability of petroleum products by disincentivising exports in the backdrop of the West Asia crises."

The mechanism is simple: every two weeks, the government recalculates duties based on global crude, petrol, diesel, and ATF prices. When international prices soften relative to Indian refinery costs, the levies come down to let refiners export more competitively. When prices spike, the levies go up to keep fuel at home.

The sharp reduction in petrol export duties this round reflects softening international gasoline prices relative to crude, according to The Hindu Business Line. Diesel and ATF levies remain elevated because global demand for those fuels — driven by shipping, aviation, and industrial use during the conflict — has not eased.

**But the calm may not last**

The timing of the duty cut is ironic. Just two days before the announcement, ExxonMobil senior vice president Neil Chapman warned at the Bernstein Conference in New York that global oil inventories are approaching "unheard of" lows and that physical Brent crude could spike to $150–$160 per barrel within weeks.

"We're approaching unheard of inventory levels. I mean, really, really low levels," Chapman said. "Once you get to that point, then you'll see prices shoot up."

Chevron CEO Mike Wirth echoed the warning, saying the "buffers and shock absorbers" that have kept prices manageable — strategic petroleum reserve releases, commercial inventory drawdowns — are steadily being exhausted. The International Energy Agency has flagged that stockpiles are being consumed at an unprecedented rate, with member countries releasing 400 million barrels in March alone.

The Strait of Hormuz closure has removed roughly 14 million barrels per day from global supply. Dated Brent dropped from a monthly average of $117 in April to near $103 in May, partly on news of progress in U.S.-Iran ceasefire talks. But if those talks falter, or if inventories hit the floor that Chapman described, India's carefully calibrated export levies could swing sharply upward again.

**What it means for Indians at home and abroad**

For consumers in India, the immediate news is neutral: domestic fuel prices are unchanged. But the finance ministry's own economic report, released the same day, warned that "a sharp rise in upstream price pressures, along with recent increases in fuel prices, suggests a gradual pass-through to retail inflation." The rupee has been under pressure, and pump prices were last raised in mid-May.

For NRIs, the story is the fragility underneath. India imports over 85 percent of its crude oil. A sustained move to $150-plus Brent would widen the current account deficit, weaken the rupee further, and squeeze household budgets across the country. The fortnightly export levy adjustment is a tool, not a shield. If global stockpiles run out, the tool runs out too.

*Sources: Reuters, India Finance Ministry notification (May 31), The Hindu Business Line, Fox Business, Seeking Alpha*"""

articles.append({
    "headline": "India Just Cut Fuel Export Duties. Exxon Says Oil Could Hit $160 Anyway.",
    "subheadline": "The government eased levies on petrol, diesel, and ATF exports starting June 1. But global inventories are running out — and industry leaders say the worst is ahead.",
    "body": fuel_body,
    "slug": "india-cuts-fuel-export-duties-exxon-oil-160-warning-hormuz-20260531",
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "India imports over 85% of its crude oil. A sustained move to $150+ Brent would widen the current account deficit, weaken the rupee, and squeeze household budgets. NRIs sending remittances would see exchange rate pressure, while family members in India face higher transport and cooking fuel costs.",
    "tags": ["fuel-export-duty", "oil-prices", "exxon", "chevron", "hormuz", "iran-war", "windfall-tax"],
    "urgency": "high",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "image_url": img3,
    "image_attribution": attr3,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/"},
        {"name": "India Finance Ministry", "url": "https://finmin.nic.in/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/"}
    ])
})

# ── Publish all ──
print("\n=== Publishing ===")
success = 0
for i, article in enumerate(articles):
    print(f"\nArticle {i+1}: {article['headline'][:60]}...")

    # Validate article quality
    body_words = len(article['body'].split())
    if body_words < 400:
        print(f"  ✗ REJECTED: Body too short ({body_words} words, minimum 400)")
        continue
    if len(article['headline']) < 20 or len(article['headline']) > 200:
        print(f"  ✗ REJECTED: Headline length issue ({len(article['headline'])} chars)")
        continue
    if len(article.get('subheadline', '')) < 15:
        print(f"  ✗ REJECTED: Subheadline too short")
        continue
    if not article.get('image_url'):
        print(f"  ⚠ No image found — publishing without image")
        article.pop('image_url', None)
        article.pop('image_attribution', None)

    print(f"  Body: {body_words} words")
    print(f"  Headline: {len(article['headline'])} chars")
    print(f"  Slug: {article['slug']}")
    print(f"  Image: {'Yes' if article.get('image_url') else 'No'}")

    if publish_article(article):
        success += 1

print(f"\n=== Done: {success}/{len(articles)} articles published ===")
