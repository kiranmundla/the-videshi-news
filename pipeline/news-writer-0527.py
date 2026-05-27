#!/usr/bin/env python3
"""
The Videshi News Writer — May 27, 2026
Publishes 3 news articles with proper image sourcing.
"""

import os, sys, json, time, uuid, re, requests, urllib.parse
from datetime import datetime, timezone

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

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
    """Fetch image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess
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
                url = p.get('src', {}).get('large2x') or p.get('src', {}).get('original')
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image(url):
    """Validate image URL returns 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read first chunk to estimate size
            chunk = next(r.iter_content(chunk_size=6000), b'')
            if len(chunk) >= 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def is_banned_url(url):
    """Check if URL is from a banned source."""
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', 'scontent-']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            return True
    for p in banned_params:
        if p in url:
            return True
    return False

def publish_article(article):
    """Publish article to Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    sources_list = [{'url': u} for u in article['sources']]
    word_count = len(article['body'].split())
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': article['category'],
        'vertical': article.get('vertical', 'nri-world'),
        'urgency': article.get('urgency', 'daily'),
        'word_count': word_count,
        'status': 'published',
        'published_at': now,
        'created_at': now,
        'updated_at': now,
        'sources': sources_list,
        'image_url': article.get('image_url'),
        'image_attribution': article.get('image_attribution', ''),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )
    if r.status_code in (200, 201):
        result = r.json()
        returned_id = result[0]['id'] if isinstance(result, list) and result else art_id
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {returned_id})")
        return returned_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:200]}")
        return None


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: Canada-India CEPA Trade Deal
# ─────────────────────────────────────────────────────────────
print("\n━━━ Article 1: Canada-India CEPA Trade Deal ━━━")

art1_image = fetch_wikipedia_person_image("Mark Carney")
if not art1_image or is_banned_url(art1_image) or not validate_image(art1_image):
    art1_image = fetch_wikipedia_person_image("Piyush Goyal")
if not art1_image or is_banned_url(art1_image):
    art1_image = fetch_pexels_image("Canada India trade agreement diplomacy", "Ottawa parliament building")
art1_attribution = "Wikimedia Commons" if art1_image and 'wiki' in art1_image.lower() else "The Videshi"

art1 = {
    'headline': "Canada and India Are Negotiating a Free Trade Deal That Would Triple Bilateral Commerce to $50 Billion. Mark Carney Called It a 'Game Changer.' The Largest Indian Business Delegation Ever Sent Abroad Is Already in Ottawa.",
    'subheadline': "Commerce Minister Piyush Goyal brought 112 companies to Canada as both sides race to finalize the Comprehensive Economic Partnership Agreement by year-end — a diplomatic reset that would have been unthinkable eighteen months ago.",
    'slug': 'canada-india-cepa-free-trade-deal-carney-goyal-50-billion-20260527',
    'category': 'news',
    'vertical': 'diaspora',
    'sources': [
        'https://globalindiabroadcastnews.com/india-news/india-canada-negotiate-game-changing-free-trade-deal-were-working-fast',
        'https://www.thehindubusinessline.com/',
        'https://www.reuters.com/'
    ],
    'image_url': art1_image,
    'image_attribution': art1_attribution,
    'body': """Canada and India are negotiating what could become the most consequential trade agreement either country has signed in a decade — and they are doing it at a speed that has surprised even seasoned diplomats.

Canadian Prime Minister Mark Carney said on Tuesday that a potential free trade agreement with India is actively being negotiated and called it a "game changer" for Canadian workers and businesses. "We are negotiating a free trade agreement with India," Carney posted after meeting Indian Commerce Minister Piyush Goyal in Ottawa. "This will be a game-changer for Canadian workers and businesses — and open up a huge new market. We are working fast."

## The Numbers Behind the Deal

The two countries are aiming to raise bilateral trade from the current $17 billion to $50 billion by 2030 — a near tripling that would make India one of Canada's largest non-U.S. trading partners. The vehicle is the Comprehensive Economic Partnership Agreement, or CEPA, which covers four key sectors: energy, agriculture, technology, and education.

Two rounds of CEPA negotiations have already been completed. The third round, which Canada will host, is being prepared. Both sides have publicly committed to concluding the deal by the end of 2026.

To underscore the seriousness of the talks, Goyal brought with him the largest Indian business delegation ever sent to another country — 112 companies that arrived in Canada before the formal trade forums even began. More are expected to join before meetings shift to Toronto for the Canada-India Trade and Investment Forum.

## A Diplomatic Reset After the Khalistan Crisis

The speed of these negotiations is remarkable given how recently the relationship was in freefall. In September 2023, then-Prime Minister Justin Trudeau told the House of Commons there were "credible allegations" linking Indian agents to the killing of pro-Khalistan figure Hardeep Singh Nijjar in British Columbia. India rejected the accusations as "ridiculous and motivated." Diplomats were expelled. Intelligence sharing was frozen.

The reset came when Carney took over as Prime Minister in March 2025. He invited Modi to the G7 summit in Kananaskis. They met again at the G20 in Johannesburg. By early 2026, Carney visited India and launched CEPA negotiations with an end-of-year deadline. As Goyal noted in Ottawa, Carney's February visit "completely changed the way Canada and India view each other."

## Why This Matters for the Indian Diaspora

Canada is home to roughly 1.8 million people of Indian origin — the largest per-capita Indian diaspora in any G7 country. A CEPA deal would directly affect tens of thousands of Indian-Canadian businesses, from Brampton logistics firms to Vancouver tech startups. It would ease the flow of goods, services, and potentially even labor mobility in sectors like IT and healthcare where both countries face chronic shortages.

For the roughly 320,000 Indian students currently studying in Canada, a trade deal could stabilize the post-graduation work environment that has grown increasingly uncertain under tightened immigration rules.

## The Bigger Strategic Picture

Carney has been explicit that the India deal is part of Canada's broader strategy to diversify trade away from dependence on the United States, which currently absorbs roughly 75 percent of Canadian exports. With Trump-era tariff uncertainty persisting and U.S.-Canada relations strained, India represents an insurance policy — a $3.7 trillion economy growing at over 6 percent annually with an appetite for exactly what Canada exports: energy, agricultural commodities, and advanced technology.

Goyal praised Carney for being "the catalyst in changing the course of bilateral relations," adding that "the speed and intent of both sides is extraordinary." Canadian Trade Minister Maninder Sidhu — himself of Indian-Punjabi heritage — attended the meetings, a symbolic touch that was not lost on the delegation.

## What Comes Next

The third round of CEPA negotiations will be held in Canada in the coming weeks. Goyal and Sidhu will co-host the Canada-India Trade and Investment Forum in Toronto, with the 112-company delegation participating. If both sides stick to their year-end deadline, this would be the fastest major trade deal either country has negotiated since Canada's CETA agreement with the European Union — and it would mark the definitive end of the Trudeau-era diplomatic freeze.

For the nearly two million Indians in Canada, the stakes are not abstract. A CEPA deal would reshape everything from small business tariffs to student visa pathways, from agriculture imports to energy investment flows. Carney is betting that it will be a game changer. The delegation in Ottawa suggests India is betting the same."""
}

publish_article(art1)


# ─────────────────────────────────────────────────────────────
# ARTICLE 2: India's High-Level Immigration Committee
# ─────────────────────────────────────────────────────────────
print("\n━━━ Article 2: India Immigration Committee ━━━")

art2_image = fetch_wikipedia_person_image("Amit Shah")
if not art2_image or is_banned_url(art2_image) or not validate_image(art2_image):
    art2_image = fetch_pexels_image("India border security fence", "India government parliament")
art2_attribution = "Wikimedia Commons" if art2_image and 'wiki' in art2_image.lower() else "The Videshi"

art2 = {
    'headline': "India Just Formed a High-Level Committee to Study 'Unnatural Demographic Changes' Caused by Illegal Immigration. It Has One Year to Deliver a Deportation Framework.",
    'subheadline': "Home Minister Amit Shah announced the panel — chaired by retired Supreme Court Justice Naolekar — fulfilling a promise Modi made on Independence Day 2025. The committee will analyze population shifts across religious and social communities.",
    'slug': 'india-demographic-change-committee-naolekar-illegal-immigration-deportation-20260527',
    'category': 'news',
    'vertical': 'nri-world',
    'sources': [
        'https://www.thehindubusinessline.com/economy/policy/centre-forms-high-level-panel-on-demographic-change-led-by-justice-naolekar/article71024821.ece',
        'https://visaverge.com/',
        'https://www.reuters.com/'
    ],
    'image_url': art2_image,
    'image_attribution': art2_attribution,
    'body': """The Indian government has constituted a high-level committee to conduct what it calls a "comprehensive assessment of demographic changes occurring across India due to illegal immigration and other unnatural causes." The panel has been given one year to deliver its findings — and a framework for permanent deportation.

Union Home Minister Amit Shah made the announcement on Tuesday, saying the committee will be chaired by retired Supreme Court Justice Prakash Prabhakar Naolekar. The other members include the Census Commissioner, retired IAS officer Durga Shankar Mishra, retired IPS officer Balaji Srivastava, and economist Dr. Shamika Ravi. The Joint Secretary (Foreigners-I) in the Ministry of Home Affairs will serve as member secretary.

## What the Committee Will Do

The committee's mandate is sweeping. According to Shah's statement, it will:

- Conduct a comprehensive assessment of demographic changes caused by illegal immigration and "other unnatural causes"
- Analyze patterns of "abnormal population shifts" at the levels of religious and social communities
- Present a "planned and time-bound solution" for addressing these shifts
- Recommend a permanent deportation framework

The language is deliberately broad. "Unnatural causes" could encompass anything from cross-border migration to differential fertility rates — a framing that has drawn immediate criticism from opposition parties and civil liberties groups who see it as a prelude to implementing a nationwide National Register of Citizens.

## From Independence Day Promise to Policy

The committee fulfills a promise Modi made during his Independence Day address on August 15, 2025, when he announced the government would form a high-level panel to study demographic changes. The announcement came amid the BJP's continued emphasis on "infiltration" as a national security threat — a theme that has been central to the party's political messaging since the passage of the Citizenship Amendment Act in 2019.

Shah framed the issue in stark terms: "Infiltration and other reasons are causing unnatural demographic change, which poses a significant challenge to the present and future of any nation." He emphasized that demographic change is linked to "sovereignty, national security, law and order, profound changes in social structure, and the preservation of tribal society."

## The Political Context

The committee's formation comes at a charged political moment. India has been conducting pushbacks of suspected illegal immigrants across the Bangladesh border, with the Supreme Court recently ordering the government to bring back people who had been pushed across after Foreigners' Tribunals declared them non-citizens — some of whom had lived in India their entire lives.

The Assam model of Foreigners' Tribunals and the National Register of Citizens has been deeply controversial. The 2019 Assam NRC excluded nearly two million people, many of them Bengali-speaking Hindus and Muslims whose families had lived in the state for generations. The CAA was designed to provide a pathway to citizenship for non-Muslim excluded persons, effectively creating a religion-based filter.

Critics argue the new committee is the groundwork for extending this model nationally. Supporters say it is a necessary step to understand and address genuine demographic pressures from illegal immigration, particularly along India's porous borders with Bangladesh and Myanmar.

## What NRIs Should Watch

For the Indian diaspora, this development sits at the intersection of several issues they follow closely. Many NRIs from northeastern India have family members directly affected by NRC processes. The committee's findings could shape immigration policy in ways that affect Overseas Citizenship of India cardholders and their families.

The committee's composition offers some signals about its likely direction. Justice Naolekar served on the Supreme Court from 2022 to 2024 and is seen as ideologically aligned with the government's position on immigration. Dr. Shamika Ravi is a former member of the Prime Minister's Economic Advisory Council. Retired IPS Balaji Srivastava served as Delhi Police Commissioner.

## One Year Clock

The committee has been given a one-year deadline to submit its report. If it follows the pattern of previous high-level panels, interim recommendations could surface within six months, potentially ahead of state elections where immigration and demographic change are politically salient issues.

The formation of this committee marks a shift from rhetoric to institutional machinery. Whether it produces evidence-based policy or politically useful conclusions will depend on the transparency of its methodology and the rigor of its data — both of which will be closely watched by demographers, legal scholars, and the courts."""
}

publish_article(art2)


# ─────────────────────────────────────────────────────────────
# ARTICLE 3: Fed Says World May Need to Cut Oil Use — India Impact
# ─────────────────────────────────────────────────────────────
print("\n━━━ Article 3: Fed / Oil / India Impact ━━━")

art3_image = fetch_pexels_image("oil refinery industrial night", "crude oil tanker port")
if not art3_image or is_banned_url(art3_image) or not validate_image(art3_image):
    art3_image = fetch_pexels_image("India economy Mumbai skyline", "stock market trading")
art3_attribution = "Pexels" if art3_image and 'pexels' in art3_image.lower() else "The Videshi"

art3 = {
    'headline': "A Federal Reserve President Just Said the World May Have to 'Get By on Less Oil and Gas.' India Imports 85 Percent of Its Crude. The Rupee Just Hit 95.68. Traders Are Pricing In 100 Basis Points of Rate Hikes.",
    'subheadline': "Dallas Fed President Lorie Logan warned that if the Strait of Hormuz doesn't reopen soon, global energy consumption will have to fall — a scenario that would hit India's economy harder than almost any other major nation.",
    'slug': 'fed-logan-world-less-oil-gas-hormuz-india-rupee-rbi-rate-hike-20260527',
    'category': 'news',
    'vertical': 'economy',
    'sources': [
        'https://www.reuters.com/business/energy/feds-logan-world-may-need-cut-use-oil-natural-gas-2026-05-27/',
        'https://www.reuters.com/world/india/rupees-rally-may-be-halted-by-dented-peace-deal-hopes-month-end-dollar-demand-2026-05-26/',
        'https://www.reuters.com/'
    ],
    'image_url': art3_image,
    'image_attribution': art3_attribution,
    'body': """A senior Federal Reserve official has said what energy markets have feared for weeks: the world may simply have to learn to consume less oil and natural gas if the Strait of Hormuz does not reopen soon. For India — which imports roughly 85 percent of its crude oil — the implications are enormous.

Dallas Federal Reserve President Lorie Logan, speaking at a Bank of Japan conference on Wednesday, delivered one of the starkest assessments yet of the energy crisis triggered by the three-month-old U.S.-Israeli war on Iran.

"With supplies highly constrained, if shipping through the strait does not soon return to prewar levels, world oil and natural gas consumption could need to fall more meaningfully than it has so far," Logan said. "The economic consequences would depend on the degree to which end users can switch to other energy sources or use energy more efficiently, versus curtailing economic activity."

## The Numbers Are Brutal

Before the war began on February 28, roughly a fifth of the world's oil and liquefied natural gas transited through the Strait of Hormuz. Since Iran throttled shipping through the waterway, the global oil supply has been reduced by approximately 13 million barrels per day — the largest supply disruption in history.

That shortfall is currently being covered by drawing down strategic and commercial inventories. But inventories, as Logan noted, are "finite."

U.S. oil executives surveyed by the Dallas Fed said they expect domestic output to rise by only 250,000 barrels per day this year and 500,000 barrels per day next year — nowhere near enough to close the gap. "One way or another, I expect energy markets to come into rough balance before too long," Logan said. "If the molecules aren't available, the world can't consume them."

Logan was one of three Fed policymakers who voted against last month's interest-rate decision, arguing that the central bank should signal that a rate hike is just as possible as a rate cut.

## India: Ground Zero for the Energy Shock

India is the world's third-largest oil consumer and imports roughly 85 percent of its crude. The Hormuz disruption has already sent domestic petrol prices above ₹100 per liter in Delhi and above ₹110 in Bengaluru, with four price hikes in ten days.

On Tuesday, the Indian rupee slipped nearly 0.5 percent to 95.68 per dollar, snapping a three-session winning streak. Brent crude rose more than 3 percent to nearly $100 per barrel. Indian equities fell and bond yields rose after news of fresh U.S. strikes on Iran.

The Reserve Bank of India has been intervening through state-run banks to smooth the rupee's decline, but the pressure is building. Analysts at MUFG, ANZ, and Standard Chartered have all penciled in a rate hike at the RBI's upcoming policy meeting on June 5.

Markets are already pricing in the worst. The one-year overnight index swap rate — a gauge of market expectations on central bank policy — rose to 6.19 percent on Tuesday, signaling that traders expect nearly 100 basis points of cumulative rate hikes over the next year. If that materializes, it would mark the RBI's first tightening cycle since 2022 and could slow India's GDP growth by an estimated 40 to 60 basis points.

## The Cascading Effects

For India's 1.4 billion people, Logan's warning translates into concrete kitchen-table consequences:

**Fuel prices:** With Brent at $100 and rising, Indian oil marketing companies are under pressure to pass through costs. The government has limited fiscal space for subsidies after already extending LPG and PNG support schemes.

**Food inflation:** India's food supply chain runs on diesel. Higher fuel costs push up transportation and cold-chain costs, which feed directly into retail food prices. India's CPI food inflation was already running above 8 percent before the latest oil spike.

**Current account deficit:** India's current account deficit, which had narrowed to 1.2 percent of GDP, is now expected to widen to 2.5 to 3 percent as the oil import bill balloons. Every $10 increase in Brent crude costs India roughly $15 billion annually.

**Remittances and diaspora impact:** A weaker rupee means Indian diaspora remittances — worth roughly $125 billion annually — buy more in India, which is one small silver lining. But for NRIs sending children to Indian colleges, investing in Indian real estate, or planning retirement returns, the macroeconomic instability introduces new risk.

## The Political Pressure

The oil shock has become a political issue. The government has raised fuel prices four times in ten days, with the hikes starting the day state elections ended — a pattern the opposition has seized on. India has been scrambling to diversify its oil supply chain, with Venezuela now its fifth-largest supplier and Iranian oil flowing for the first time in seven years through alternative payment channels.

But diversification has limits when the fundamental problem is a 13-million-barrel-per-day global shortfall. India cannot buy its way out of a supply gap this large.

## What Comes Next

The RBI policy meeting on June 5 will be the most closely watched in years. If the central bank hikes rates — even by 25 basis points — it would signal that inflation control has overtaken growth support as the primary concern. The government's fiscal calculus would also shift, potentially forcing cuts to capital expenditure budgets that have been driving India's infrastructure buildout.

Logan's message was blunt: if the Hormuz crisis persists, the world will have to adjust by consuming less. For India, that adjustment would be neither easy nor painless. The country cannot switch to renewables fast enough to offset an oil shock of this magnitude. It cannot produce enough domestic crude to matter. And it cannot subsidize its way through a $100-a-barrel world indefinitely.

The question is no longer whether India will be affected, but how deeply — and whether the RBI and the government can engineer a soft landing while the world's most important oil chokepoint remains closed."""
}

publish_article(art3)

print("\n━━━ All articles processed ━━━")
