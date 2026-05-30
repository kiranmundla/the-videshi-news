#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-30 batch"""

import json, os, sys, uuid, re, time
import requests, urllib.parse
from datetime import datetime, timezone

# ── Supabase config ──
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/.env.supabase'))
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

# ── Image helpers ──
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
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                headers={"Authorization": PEXELS_KEY},
                timeout=10
            )
            if r.status_code == 200:
                results = r.json().get("photos", [])
                for photo in results:
                    src = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                    if src:
                        print(f"  ✓ Pexels image found for '{q}': {src[:80]}...")
                        return src
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate image URL returns proper image with decent size."""
    if not url:
        return False
    # Block banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    for b in banned:
        if b in url:
            print(f"  ✗ Blocked banned domain: {b}")
            return False
    for p in banned_params:
        if p in url:
            print(f"  ✗ Blocked banned param: {p}")
            return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' not in ct:
            print(f"  ✗ Not an image: {ct}")
            return False
        if cl > 0 and cl < 5000:
            print(f"  ✗ Image too small: {cl} bytes")
            return False
        return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        return False

def source_image(person_name=None, pexels_query=None, pexels_fallback=None):
    """Try Wikipedia first for people, then Pexels. Returns (url, attribution)."""
    if person_name:
        url = fetch_wikipedia_person_image(person_name)
        if url and validate_image_url(url):
            return url, "Wikimedia Commons"
    if pexels_query:
        url = fetch_pexels_image(pexels_query, pexels_fallback)
        if url and validate_image_url(url):
            return url, "The Videshi"
    return None, None

# ── Article publishing ──
def publish_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': now,
        'sources': json.dumps(article['sources']),
        'image_url': article.get('image_url'),
        'image_attribution': article.get('image_attribution', 'The Videshi'),
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload
    )

    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}... (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Failed to publish: {r.status_code} {r.text[:200]}")
        return None

# ── Articles ──
articles = []

# ── ARTICLE 1: India Monsoon Weakest in 11 Years ──
print("\n📰 Article 1: India monsoon weakest in 11 years...")
img_url_1, img_attr_1 = source_image(
    pexels_query="India monsoon rain farmland",
    pexels_fallback="dry cracked earth drought India"
)

articles.append({
    'headline': "India Just Forecast Its Weakest Monsoon in 11 Years. El Niño Is Coming.",
    'subheadline': "The IMD now projects rainfall at just 90% of the long-period average — the lowest since 2015. With oil prices already elevated and inflation creeping up, a failed monsoon could push food prices into crisis territory.",
    'slug': 'india-weakest-monsoon-11-years-el-nino-inflation-food-prices-20260530',
    'body': """India's monsoon season — the single most consequential weather event for the world's most populous country — is about to underperform in a way it hasn't in over a decade.

The India Meteorological Department announced on Friday that the 2026 southwest monsoon is expected to deliver just 90% of the long-period average rainfall, revised down from an already cautious April forecast of 92%. If that holds, it would be the weakest monsoon since 2015, when El Niño slashed rainfall to 87% and sent food prices spiralling across the country.

## The El Niño Factor

The culprit is familiar: El Niño, the periodic warming of Pacific Ocean surface temperatures that disrupts weather patterns across Asia. The IMD says there is an 84% probability that rainfall will be below normal or worse during the June-to-September monsoon window.

M. Ravichandran, secretary in the Ministry of Earth Sciences, told reporters that an El Niño is "likely to develop soon" and could range from moderate to strong intensity during the critical July-August months — the period that typically delivers the bulk of India's annual rainfall.

The timing could not be worse. Several Indian states are already reeling under severe heatwave conditions, with temperatures exceeding 45°C (113°F). These are temperatures that ordinarily ease only with the monsoon's arrival.

## Why This Matters for the Economy

The monsoon is not just a weather event in India. It is an economic event. Roughly 70% of India's annual rainfall arrives during these four months, replenishing reservoirs, rivers, and groundwater that sustain a nearly $4-trillion economy. Almost half of India's farmland lacks irrigation. About half the population still earns its livelihood from agriculture.

"A deficient monsoon, particularly in the crucial July-August months, can add to the pressure and push up inflation closer to an average of 5.5% if food inflation spikes," said Gaura Sengupta, chief economist at IDFC First Bank.

India's retail inflation stood at 3.48% in April — comfortably below the Reserve Bank of India's 4% medium-term target. But that number is deceptive. It masks a food inflation component that is already elevated, and an energy cost structure that has been blown apart by the Iran war and the closure of the Strait of Hormuz.

## The Double Squeeze

India is now facing what economists are calling a "double squeeze" — energy-driven inflation from the geopolitical crisis in the Middle East, compounded by potential food price shocks from a weak monsoon.

Crude oil prices have averaged roughly 30% above pre-war levels. The rupee has fallen more than 5% in 2026. Foreign investors have pulled over $24 billion from Indian debt and equities between March and May. And now, the monsoon forecast adds agricultural risk to an already stressed picture.

The Wall Street Journal reported this week that El Niño's return is "the next risk hanging over the global economy," noting that the last major El Niño episode triggered India's rice export ban, disrupted the Panama Canal, and caused devastating floods in Brazil.

## What the Diaspora Should Watch

For NRIs with family in India, the monsoon forecast has direct implications. Rural incomes, which drive consumption in smaller cities and towns, could take a hit. Families dependent on agriculture — still a significant portion of India's population — face potential income losses.

Food prices, particularly for vegetables, pulses, and rice, are the most sensitive to monsoon performance. A weak monsoon in 2015 pushed food inflation above 6% for several months, squeezing household budgets across the country.

The RBI's monetary policy decision on June 5 will now carry even more weight. Most economists expect the central bank to hold rates at 5.25%, but a growing minority — 11 out of 56 in the latest Reuters poll — are now forecasting a rate hike to counter the combined threat of energy inflation and a failing monsoon.

## What Comes Next

June rainfall is expected to be particularly weak — below 92% of the long-period average. If El Niño develops as projected, the July-August window will determine whether this is a manageable shortfall or a full-blown agricultural crisis.

India has been here before. In 2015, the weak monsoon reduced kharif crop output significantly, but the government's buffer stocks and targeted interventions prevented a food security emergency. The question in 2026 is whether the government has the fiscal space to intervene effectively while simultaneously managing energy subsidies and a weakening currency.

The monsoon has always been India's most important economic variable. This year, it may also be its most dangerous.""",
    'sources': [
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-29/"},
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/"},
        {"name": "The Business Standard", "url": "https://www.tbsnews.net/"},
        {"name": "IDFC First Bank (Gaura Sengupta)", "url": ""}
    ],
    'image_url': img_url_1,
    'image_attribution': img_attr_1 or 'The Videshi'
})

# ── ARTICLE 2: Piyush Goyal's North America Charm Offensive ──
print("\n📰 Article 2: Piyush Goyal's North America economic diplomacy...")
img_url_2, img_attr_2 = source_image(
    person_name="Piyush Goyal",
    pexels_query="India US trade diplomacy meeting"
)

articles.append({
    'headline': "Piyush Goyal Just Finished a 10-Day Sprint Across North America. Here's What He Got Done.",
    'subheadline': "The Commerce Minister met CEOs at Morgan Stanley, Mastercard, and Warburg Pincus in New York, pushed a $50 billion trade target in Canada, and confirmed a US delegation is coming to Delhi next week for BTA talks.",
    'slug': 'piyush-goyal-north-america-us-canada-trade-bta-morgan-stanley-mastercard-20260530',
    'body': """India's Commerce and Industry Minister Piyush Goyal has just wrapped up one of the most intensive diplomatic tours of his tenure — a 10-day blitz through Ottawa, Toronto, and New York that covered trade deals, CEO meetings, diaspora engagement, and bilateral negotiations with two of India's most important economic partners.

## New York: 50 Business Leaders in One Room

On Friday, Goyal held a closed-door roundtable in New York City with more than 50 prominent global business and industry leaders. The session, hosted by the Indian Consulate in collaboration with the US-India Strategic Partnership Forum (USISPF), was designed to showcase India's investment story directly to the people who write the cheques.

The minister's calendar in New York read like a Wall Street speed-dating session. He held one-on-one meetings with Ted Pick, Chairman and CEO of Morgan Stanley; Miebach Michael, CEO of Mastercard; Chip Kaye, Chairman of Warburg Pincus; and Chintu Patel, Co-founder and Co-CEO of Amneal Pharmaceuticals.

With Morgan Stanley, discussions centred on "strengthening long-term investments and institutional partnerships in India." With Mastercard, the focus was on digital commerce, digital security, and next-generation payment solutions — areas where India's Unified Payments Interface (UPI) has already established a global lead. With Warburg Pincus, Goyal highlighted India's "scale, talent, rising domestic demand, and steady policy push" as reasons for continued investment.

## The BTA Countdown

The most consequential outcome may be the confirmation that a US trade delegation, led by the US Chief Negotiator, will arrive in New Delhi from June 1 to 4 for the next round of Bilateral Trade Agreement (BTA) negotiations.

This follows an Indian delegation's visit to Washington in April, where teams worked on finalising an interim agreement and advancing the broader BTA across five negotiation tracks: Market Access, Non-Tariff Measures, Customs and Trade Facilitation, Investment Promotion, and Economic Security Alignment.

US Ambassador to India Vinai Thummalapally — known informally as Ambassador Gor — has been publicly optimistic. "Negotiations have been ongoing for a year and a half, but to put it in perspective, the European Union took almost 19 years. We are confident that in the coming weeks and months, this trade deal will be finalised," he said this week.

The India-EU Free Trade Agreement, signed in January 2026 after negotiations that began in 2007, serves as both a benchmark and a motivational reference point. The US-India BTA, if completed, would reshape trade flows between the world's largest and fifth-largest economies.

## Canada: The $50 Billion Target

Before New York, Goyal spent three days in Canada — Ottawa on May 25, then Toronto from May 26 to 28 — focused on accelerating negotiations for the India-Canada Comprehensive Economic Partnership Agreement (CEPA).

The headline number: India-Canada bilateral trade currently stands at approximately $8.5 billion. Both governments have committed to expanding it to $50 billion by 2030 — an ambitious target that would require a near-sixfold increase in just four years.

Goyal's Toronto schedule was packed with engagements spanning academia, innovation, government, business councils, institutional investors, and the Indian diaspora. The outreach to the diaspora is strategic: Canada's Indian-origin population exceeds 1.8 million, making it one of the largest and most economically influential diaspora communities in the country.

## What This Means for NRIs

For the Indian diaspora in North America, the BTA and CEPA negotiations are not abstract policy exercises. They directly affect visa regimes, professional mobility, investment flows, and the regulatory environment for businesses that operate across borders.

A finalised US-India interim trade agreement could reduce tariffs on key goods, streamline customs procedures, and create more predictable investment frameworks — all of which benefit NRI entrepreneurs and businesses with operations in both countries.

The Canada-India CEPA, if it reaches its $50 billion target, would similarly expand opportunities for the diaspora community that serves as a natural bridge between the two economies.

## The Bigger Picture

Goyal's North America tour comes at a moment when India is aggressively diversifying its trade relationships. The EU free trade deal signed in January, the UK deal completed earlier this year, and ongoing negotiations with the US and Canada represent a coordinated effort to lock in market access across the developed world while global trade architecture is being rewritten.

The Iran war has only accelerated this urgency. With energy costs elevated, the rupee under pressure, and capital outflows mounting, securing stable trade agreements with major economies is no longer just good diplomacy — it is economic defence.""",
    'sources': [
        {"name": "IANS / India Post", "url": "https://www.indiapost.com/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
        {"name": "ANI / LatestLY", "url": "https://www.latestly.com/"},
        {"name": "The Freedom Press", "url": "https://thefreedompress.in/"}
    ],
    'image_url': img_url_2,
    'image_attribution': img_attr_2 or 'The Videshi'
})


# ── ARTICLE 3: RBI Annual Report FX Windfall ──
print("\n📰 Article 3: RBI annual report — $17.7B FX windfall...")
img_url_3, img_attr_3 = source_image(
    pexels_query="Reserve Bank India currency central bank",
    pexels_fallback="Indian rupee currency notes"
)

articles.append({
    'headline': "The RBI Made $17.7 Billion Selling Dollars to Defend the Rupee. Then It Gave a Record $30 Billion to the Government.",
    'subheadline': "The central bank's annual report shows foreign exchange gains rose 52%, its balance sheet topped $961 billion, and it transferred a record ₹2.87 trillion to the federal government — the largest such payout in RBI history.",
    'slug': 'rbi-annual-report-fy26-fx-gains-record-dividend-government-transfer-20260530',
    'body': """The Reserve Bank of India released its annual report on Friday, and buried in the numbers is a remarkable story about how the central bank turned a crisis into a cash windfall — and then handed that cash to the government.

## The Numbers

In the fiscal year ending March 2026, the RBI's gains from foreign exchange transactions rose 52% to ₹1.69 trillion ($17.7 billion). The mechanism is straightforward: when the RBI sells dollars from its reserves to defend the rupee — which it has been doing aggressively since the Iran war began — it books profits based on the difference between what it originally paid for those dollars and the current exchange rate.

Since the RBI accumulated much of its dollar reserves when the rupee was trading at ₹83-84 per dollar, and has been selling them at ₹95+, the profit margins on each intervention have been substantial.

Combined with interest income from foreign securities holdings (primarily US Treasuries), which rose to ₹1.07 trillion from ₹970 billion the previous year, the RBI's total foreign-currency income powered a record transfer to the government.

## The Record Dividend

Earlier this month, the RBI announced it would transfer a record ₹2.87 trillion ($29.99 billion) to the federal government for the fiscal year ended March 2026. This is the largest surplus transfer in the central bank's history, surpassing the previous record of ₹2.1 trillion in FY2025.

The government treats the RBI dividend as non-tax revenue, and it directly improves the fiscal balance. At ₹2.87 trillion, the transfer alone covers roughly 15% of the government's budgeted fiscal deficit for FY2027.

## The Balance Sheet

The RBI's balance sheet expanded by 20.61% to ₹91.97 trillion ($961.1 billion) as of March 31, 2026. This expansion reflects both the accumulation of domestic assets and the revaluation of foreign reserves in rupee terms — a natural consequence of the rupee's depreciation.

## The Paradox

There is an uncomfortable paradox in these numbers. The RBI's forex gains exist precisely because the rupee has weakened significantly. The central bank sells dollars to slow the rupee's decline, and because it bought those dollars when the rupee was stronger, it books a profit on each sale. The worse the rupee performs, the larger the paper profit on intervention.

This does not mean the RBI is profiting from economic distress — the central bank's primary objective in forex intervention is stability, not profit. But it does mean that the record dividend is, in part, a byproduct of the economic pain caused by the Iran war, capital outflows, and energy price shocks.

## What This Means for India

The record transfer to the government comes at a critical time. India is facing a fiscal squeeze from multiple directions: elevated energy subsidies, potential food price pressures from a weak monsoon, and lower-than-expected tax collections in some categories due to the economic slowdown.

The RBI dividend provides fiscal breathing room. It could help the government maintain capital expenditure on infrastructure — a key driver of economic growth — without breaching its fiscal deficit targets.

## What It Means for NRIs

For NRIs with investments in Indian markets or remittances to India, the RBI's massive forex reserves and active intervention provide a degree of comfort. The central bank has the firepower to prevent a disorderly rupee decline, even if it cannot reverse the underlying pressures.

The record transfer also signals that the government will have fiscal space to avoid the kind of austerity measures that could hurt growth — a positive signal for anyone invested in India's medium-term economic trajectory.

However, the rate decision on June 5 remains the more immediate concern. If the RBI decides to hike rates to defend the rupee and contain inflation, NRI deposit rates could rise (a positive for depositors) but corporate earnings and equity markets could take a hit.

## The Bigger Picture

The RBI's annual report paints a picture of a central bank that has been working overtime. The 52% surge in forex gains reflects the sheer volume of intervention required to manage the rupee through the most turbulent period since the 2013 taper tantrum.

The question now is whether the RBI's reserves are being depleted too quickly. India's foreign exchange reserves remain substantial — among the largest in the world — but they have declined from their peaks as the central bank has sold dollars to defend the currency. The pace of reserve depletion will determine how long the RBI can sustain this level of intervention without external support.""",
    'sources': [
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Reserve Bank of India Annual Report FY2025-26", "url": "https://m.rbi.org.in/"},
        {"name": "ChiniMandi / Front Wave Research", "url": "https://chinimandi.com/"}
    ],
    'image_url': img_url_3,
    'image_attribution': img_attr_3 or 'The Videshi'
})


# ── ARTICLE 4: Oil Forecasts Raised for Third Time ──
print("\n📰 Article 4: Oil forecasts hiked for third time...")
img_url_4, img_attr_4 = source_image(
    pexels_query="oil tanker crude ship sea",
    pexels_fallback="oil refinery energy industry"
)

articles.append({
    'headline': "Analysts Just Raised Oil Forecasts for the Third Time Since the Iran War Began. India Cannot Afford This.",
    'subheadline': "Brent crude is now forecast to average $90.44 per barrel in 2026 — up 40% from pre-war estimates. For India, the world's third-largest oil importer, every dollar of that increase bleeds into inflation, the trade deficit, and the rupee.",
    'slug': 'oil-price-forecasts-hiked-third-time-iran-war-india-imports-inflation-20260530',
    'body': """Three months into the Iran war, the world's energy forecasters have once again raised their estimates for how expensive oil will be this year — and the numbers are getting worse for India.

## The Forecast

A Reuters poll of 33 economists and analysts published Friday shows Brent crude is now expected to average $90.44 per barrel in 2026, up from $86.38 projected in April. US crude (WTI) is seen averaging $84.63, up from $80.07.

To understand how dramatically the landscape has shifted: these same forecasters projected Brent at $63.85 per barrel on February 27, 2026 — one day before the US and Israel struck Iran. The current forecast represents a 40% increase from that pre-war baseline.

## Why Prices Stay Elevated

The Strait of Hormuz — the narrow waterway through which roughly 20% of the world's oil supply passes — has been effectively closed since the war began. Data from Kpler shows that monthly crude oil exports from the Middle East have dropped from an average of 18.3 million barrels per day before the crisis to less than 8.8 million bpd since March.

That is more than half the region's export capacity taken offline.

Even with a potential 60-day ceasefire extension between the US and Iran reportedly close to approval, analysts warn that the recovery of energy flows will take months, not weeks. "The disruptions will last even longer than expected till the trade flows through the Strait of Hormuz may reach pre-crisis levels," said Thomas Wybierek, analyst at NORD/LB.

Brent and WTI have both hit four-year highs since the war began — over $126 and $119 per barrel respectively — though prices pulled back on Friday to around $91 as ceasefire extension hopes grew.

## India's Exposure

India is the world's third-largest oil importer, and its economy is structurally vulnerable to sustained high oil prices. Every $10 increase in crude prices adds roughly 0.3 to 0.4 percentage points to India's inflation and widens the current account deficit by approximately $15 billion annually.

The numbers are already showing the strain. The rupee has fallen more than 5% in 2026. Foreign investors have pulled over $24 billion from Indian equities and debt between March and May. Wholesale inflation has accelerated sharply. And the RBI has been burning through foreign exchange reserves to prevent a disorderly currency decline.

Capital Economics' Shilan Shah captured the outlook starkly: "Our base case is that the RBI lifts the repo rate to 6.00% before the end of the year, but that is contingent on the crisis coming to an end soon and energy prices dropping back."

## The Strategic Response

India has already moved to build resilience. The government recently ordered a 30-day strategic reserve of cooking gas (LPG) — a direct response to Hormuz-related supply risks. The RBI has been intervening aggressively in forex markets to stabilise the rupee, booking $17.7 billion in gains from dollar sales in the process.

But these are defensive measures. They buy time; they do not solve the fundamental problem of energy dependence.

## What the Diaspora Should Know

For NRIs, the oil price trajectory has several direct implications:

**Remittances**: A weaker rupee means NRI remittances stretch further in India — but it also signals economic stress that affects family members' cost of living.

**Investments**: High oil prices are a headwind for Indian equities, particularly in sectors like airlines, logistics, and consumer goods that are sensitive to input costs. Bank stocks, however, could benefit if the RBI raises rates.

**Real estate**: A rate hike, if it comes, would increase home loan costs in India — relevant for NRIs with property investments or plans to buy.

**Travel**: Fuel surcharges on India-bound flights have already increased. A sustained period of $90+ oil means travel costs will remain elevated through the year.

## What Comes Next

The ceasefire extension between the US and Iran, if approved, would be a temporary positive — but analysts are clear that even a ceasefire does not restore energy flows quickly. The physical infrastructure of Middle Eastern oil trade — tanker routes, insurance arrangements, port operations — takes time to normalise after a disruption of this magnitude.

EIU analyst Surabhi Menon projects prices to continue increasing through July before stabilising: "This is based on the assumption that the war in Iran will remain in its current state — with a ceasefire in place and the Strait of Hormuz closed — until at least end of July."

For India, there is no quick fix. The country imports roughly 85% of its crude oil, and no amount of strategic reserves or currency intervention can substitute for stable, affordable energy imports. The monsoon forecast — the weakest in 11 years — only compounds the problem, threatening food inflation on top of energy inflation.

India's economy has weathered oil shocks before. But rarely has it faced one of this magnitude while simultaneously dealing with a weak monsoon, capital flight, and currency pressure. The next few months will test the resilience of both the economy and its policymakers.""",
    'sources': [
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Capital Economics (Shilan Shah)", "url": ""},
        {"name": "EIU (Surabhi Menon)", "url": ""},
        {"name": "Kpler (shipping data)", "url": ""}
    ],
    'image_url': img_url_4,
    'image_attribution': img_attr_4 or 'The Videshi'
})

# ── Publish all articles ──
print("\n" + "="*60)
print("Publishing articles...")
print("="*60)

success_count = 0
for i, article in enumerate(articles, 1):
    print(f"\n[{i}/{len(articles)}] Publishing: {article['headline'][:70]}...")
    word_count = len(article['body'].split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ✗ SKIPPED — below 400-word floor")
        continue
    if not article.get('image_url'):
        print(f"  ⚠ No image — publishing without image")
    art_id = publish_article(article)
    if art_id:
        success_count += 1

print(f"\n{'='*60}")
print(f"Done. Published {success_count}/{len(articles)} articles.")
print(f"{'='*60}")
