#!/usr/bin/env python3
"""
News writer for The Videshi — June 1, 2026 run.
Three articles:
1. Forex reserves / Rupee crisis
2. Solar ALMM mandate June 1
3. Record stock market foreign sell-off (MSCI rebalancing)
"""

import json, os, uuid, requests, subprocess, sys, re
from datetime import datetime, timezone

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                key, _, val = line.partition('=')
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

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

# ─── Image sourcing ───

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch image from Pexels using curl (Python urllib gets 403)."""
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get('Content-Type', '')
                    cl = int(head.headers.get('Content-Length', '0'))
                    if head.status_code == 200 and 'image' in ct and cl > 5000:
                        print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None
        
        ct = r.headers.get('Content-Type', 'image/jpeg')
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': ct,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None


def source_image(article_slug, person_name=None, pexels_query=None, pexels_fallback=None):
    """Source image following the hierarchy: Wikipedia > Pexels > None."""
    img_url = None
    attribution = None
    
    if person_name:
        img_url = fetch_wikipedia_person_image(person_name)
        if img_url:
            attribution = "Wikimedia Commons"
    
    if not img_url and pexels_query:
        img_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if img_url:
            attribution = "Pexels"
    
    if img_url:
        # Upload to Supabase for permanence (unless already Pexels permanent URL)
        if 'images.pexels.com' in img_url or 'upload.wikimedia.org' in img_url:
            return img_url, attribution
        else:
            uploaded = upload_to_supabase_storage(img_url, f"{article_slug}.jpg")
            if uploaded:
                return uploaded, attribution
            return img_url, attribution
    
    return None, None


def insert_article(article):
    """Insert article into Supabase p2_articles."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    resp = requests.post(url, headers=HEADERS, json=article, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else data.get('id', 'unknown')
        print(f"  ✓ Inserted article: {article['slug']} (id: {art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {resp.status_code} {resp.text[:300]}")
        return None


# ─── Articles ───

articles = []

# ── Article 1: Forex Reserves / Rupee Crisis ──
print("\n=== Article 1: India's Forex Reserves Plunge ===")

body_1 = """India's foreign exchange reserves have dropped to their lowest level in more than a year, falling to $681.4 billion in the week ending May 22 — a decline of nearly $47 billion from the record high of $728.49 billion reached in February.

The sharp drawdown reflects the Reserve Bank of India's aggressive intervention in currency markets to prevent a disorderly fall in the rupee, which has lost roughly 6 percent of its value against the dollar in 2026. At its weakest point in May, the currency touched a record low of 96.96 per dollar before recovering to 95 on the back of heavy central bank selling.

## The Numbers Tell a Stark Story

In a single week ending May 22, reserves fell by $7.5 billion. Of that, approximately $4.5 billion came from a decline in the value of the RBI's gold holdings, while foreign currency assets — the largest component of reserves — dropped by nearly $3 billion to $543 billion.

Market participants estimate the RBI has been selling between $800 million and $2 billion a day in recent weeks to slow the rupee's slide. The central bank's short forward dollar commitments fell to $95.3 billion at the end of April from over $100 billion in March, according to data released after market hours on Friday.

The RBI has maintained that it does not target any specific exchange rate but intervenes to prevent "disorderly market movements and excessive speculation." The distinction, economists say, is increasingly academic.

## Why the Rupee Is Under Siege

Three forces are converging on the Indian currency.

**The oil shock.** The Strait of Hormuz, which handles roughly a fifth of global oil and liquefied natural gas flows, has remained largely shut since February 28 due to the US-Iran conflict. Brent crude, while easing 11 percent last week, still trades at around $92-93 per barrel — 30 percent above pre-war levels. India imports nearly 90 percent of its crude oil, making it acutely vulnerable to sustained energy price increases.

**Capital flight.** Foreign portfolio investors have been pulling money out of Indian equities for months. On Friday alone, they dumped $2.22 billion worth of shares — a record single-day outflow — as MSCI's index rebalancing triggered massive position adjustments. The outflows have been amplified by an AI-driven rally in markets like South Korea and Taiwan, which has diverted foreign capital away from India.

**The dollar's strength.** US Treasury yields remain elevated, making dollar-denominated assets more attractive relative to emerging market investments. The rupee has weakened from the mid-80s to 95 against the dollar, a slide that directly erodes the dollar-denominated returns foreign investors earn in India.

## What This Means for the Diaspora

For the estimated 18 million Indians living abroad, the weaker rupee has a direct and tangible impact. Every dollar, pound, or dirham sent home now converts to significantly more rupees — a family sending $1,000 home gets roughly ₹95,000 today compared to ₹85,000 at the start of the year.

But the benefit comes with uncertainty. NRIs with India-denominated investments — property, fixed deposits, mutual funds — are seeing the value of those holdings shrink in dollar terms. Those planning to repatriate funds face the question of whether to wait for a recovery or lock in current rates.

India received $129 billion in remittances in the fiscal year ending March 2026, the largest in the world. The weaker rupee makes those flows more valuable in local currency terms, providing a modest cushion to the economy's external accounts.

## The Week Ahead

All eyes now turn to the RBI's Monetary Policy Committee meeting from June 3-5, where Governor Sanjay Malhotra will announce the rate decision on June 5. A Reuters poll of economists shows nearly 80 percent expect the repo rate to be held at 5.25 percent, with analysts at Goldman Sachs forecasting a "hawkish pause alongside possible measures to attract dollar inflows."

The SBI Research team has projected GDP growth at 6.6 percent for FY27 and inflation at 5 percent, with risks tilted to the upside. The RBI is also expected to update its inflation and growth forecasts, which currently assume crude oil at $85 per barrel — well below current market prices.

India's reserves, despite the decline, still cover approximately 11 months of imports and remain among the largest in the world. But the pace of depletion — nearly $50 billion in three months — has raised questions about how long the central bank can sustain this level of intervention without triggering a confidence crisis of its own.

*Sources: Reserve Bank of India data, Reuters, Outlook Money, SBI Research, Goldman Sachs*"""

img_1, attr_1 = source_image(
    "india-forex-reserves-681-billion-rbi-rupee-defence-47-billion-decline-20260601",
    pexels_query="Indian rupee currency notes",
    pexels_fallback="reserve bank India"
)

articles.append({
    "headline": "India\u2019s Forex Reserves Have Fallen $47 Billion in Three Months. The RBI Is Spending Billions to Defend the Rupee.",
    "subheadline": "From a record $728 billion in February to $681 billion in May \u2014 the central bank is burning through dollars as the Hormuz crisis, oil shock, and capital flight batter the currency.",
    "slug": "india-forex-reserves-681-billion-rbi-rupee-defence-47-billion-decline-20260601",
    "body": body_1,
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reserve Bank of India", "url": "https://www.rbi.org.in/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/"},
        {"name": "SBI Research", "url": "https://sbi.co.in/"},
        {"name": "Goldman Sachs", "url": "https://www.goldmansachs.com/"}
    ]),
    "image_url": img_1,
    "image_attribution": attr_1 or "Pexels",
    "is_editorial": False
})


# ── Article 2: Solar ALMM Mandate ──
print("\n=== Article 2: India Solar ALMM Mandate ===")

body_2 = """Starting today, every solar power project in India must use domestically manufactured solar cells. No extensions. No exceptions.

The Ministry of New and Renewable Energy has enforced its Approved List of Models and Manufacturers (ALMM) List-II mandate for solar photovoltaic cells, effective June 1, 2026. The policy, announced 18 months ago to give the industry time to prepare, is designed to cut India's dependence on Chinese solar imports and build a self-sustaining domestic manufacturing ecosystem.

The numbers suggest the industry was listening. India's cumulative solar PV cell manufacturing capacity reached 40 gigawatts at the end of March 2026, with 5 GW added in the January-March quarter alone — the third-highest quarterly addition in six years, according to JMK Research & Analytics. Of the total capacity, approximately 27.23 GW is already listed under the ALMM framework.

## Why This Matters

India has been the world's third-largest solar market for several years, but its manufacturing base has lagged far behind its installation ambitions. Until recently, the country imported the vast majority of its solar cells and modules from China, creating a strategic vulnerability that became painfully visible during the supply chain disruptions of the pandemic era.

The ALMM mandate flips the equation. Developers building solar projects — whether utility-scale farms in Rajasthan or rooftop installations in Bengaluru — must now source cells from manufacturers on the approved domestic list. The policy effectively creates a guaranteed market for Indian manufacturers, incentivizing further investment in production capacity.

"There are two things," a senior government official told The Hindu BusinessLine. "First, whatever investments have been made in cell manufacturing to make India self-reliant, please go ahead and we will support you. There is demand creation. Second, this also gives a clear window for fresh investments."

## The Scale of Ambition

India's solar targets are staggering. The country aims to reach 500 GW of renewable energy capacity by 2030, of which solar is expected to contribute the largest share. Meeting that target requires not just installation capacity but a robust domestic supply chain — from polysilicon and wafers to cells and modules.

The 40 GW of cell manufacturing capacity is a significant milestone, but it is still not enough. India installed approximately 18 GW of solar capacity in FY26, and installation rates are expected to accelerate sharply over the next four years. The government's Production-Linked Incentive (PLI) scheme for solar manufacturing, with an allocation of ₹19,500 crore ($2.3 billion), is designed to bridge the remaining gap.

Several major players have announced or are building gigawatt-scale cell manufacturing facilities, including Adani Solar, Tata Power Solar, Waaree Energies, and Vikram Solar. The combination of the ALMM mandate and PLI incentives has created what industry analysts describe as the most favorable policy environment for domestic solar manufacturing in India's history.

## The Diaspora Connection

For NRI investors tracking India's green energy transition, the ALMM mandate represents a structural shift. Indian solar manufacturers listed on domestic exchanges have seen significant interest from institutional investors anticipating the captive market the policy creates. The mandate also reduces currency risk for solar projects by localizing the supply chain — a relevant consideration as the rupee faces pressure from elevated oil prices.

India's broader energy security calculus is also shifting. The country imports nearly 90 percent of its crude oil, a vulnerability starkly exposed by the ongoing Hormuz crisis. Every gigawatt of solar capacity installed reduces that dependency, making the ALMM mandate as much an energy security policy as an industrial one.

## What Could Go Wrong

Critics of the ALMM mandate argue that restricting cell sourcing to domestic manufacturers could temporarily increase costs for solar developers, potentially slowing installation rates in the short term. Some developers have lobbied for extensions, arguing that domestic manufacturing capacity, while growing, is not yet sufficient to meet all demand at competitive prices.

The Ministry's response has been unequivocal. "No blanket extension of the deadline for applicability of ALMM List-II for solar PV cells will be given beyond June 1, 2026," MNRE clarified in a statement.

The message to the industry is clear: the era of unlimited Chinese solar imports is over.

*Sources: Ministry of New and Renewable Energy, JMK Research & Analytics, The Hindu BusinessLine*"""

img_2, attr_2 = source_image(
    "india-almm-solar-cell-mandate-june-2026-40gw-manufacturing-20260601",
    pexels_query="solar panel manufacturing factory",
    pexels_fallback="solar panels India"
)

articles.append({
    "headline": "India Just Made It Mandatory to Use Indian-Made Solar Cells. It Has 40 GW of Manufacturing Capacity to Back It Up.",
    "subheadline": "The ALMM mandate for solar PV cells takes effect today. No extensions, no exceptions — India's push to end dependence on Chinese solar imports enters its most consequential phase.",
    "slug": "india-almm-solar-cell-mandate-june-2026-40gw-manufacturing-20260601",
    "body": body_2,
    "category": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Ministry of New and Renewable Energy", "url": "https://mnre.gov.in/"},
        {"name": "JMK Research & Analytics", "url": "https://jmkresearch.com/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
    ]),
    "vertical": "news",
    "image_url": img_2,
    "image_attribution": attr_2 or "Pexels",
    "is_editorial": False
})


# ── Article 3: Record Stock Market Foreign Sell-Off ──
print("\n=== Article 3: Record Foreign Sell-Off ===")

body_3 = """Foreign investors pulled $2.22 billion out of Indian equities on Friday in a single trading session — the largest one-day outflow in the history of Indian stock markets.

The Nifty 50 index dropped 1.5 percent to close at 23,547.75, a two-week low, while turnover on the National Stock Exchange soared to a record ₹2.87 trillion ($30.21 billion). Nifty 50 turnover alone surpassed ₹1 trillion for the first time, according to data compiled by LSEG.

The immediate trigger was MSCI's May index rebalancing, which took effect at approximately 3:00 PM IST on Friday. Goldman Sachs had estimated the rebalancing would lead to about $870 million in outflows from Indian equities — but the actual selling far exceeded expectations as other portfolio adjustments piled on top of the index-driven flows.

## What Is MSCI Rebalancing?

MSCI Inc., the index provider whose benchmarks are tracked by an estimated $16.3 trillion in assets worldwide, periodically adjusts the weightings of individual countries and stocks in its global indices. When India's weight decreases — or when specific Indian stocks are removed or reduced — funds that track these indices are forced to sell Indian shares to stay aligned with the benchmark.

The May 2026 rebalancing was particularly significant because of changes to the weighting methodology that reduced India's share in the MSCI Emerging Markets Index. The result: a wave of forced selling that concentrated into the final hours of trading on Friday.

"A range of different flows, including those linked to equity index adjustments, maturities in the non-deliverable forward market and routine corporate demand, are likely to drive the rupee," a trader at a Mumbai-based private bank told Reuters.

## Beyond the Rebalancing: Structural Outflows

While the MSCI rebalancing explains Friday's extreme numbers, the broader trend of foreign portfolio investor (FPI) outflows has been building for months. Three factors are driving the pattern.

**The oil shock.** India imports nearly 90 percent of its crude oil, and the ongoing closure of the Strait of Hormuz has kept Brent crude prices elevated at around $92-93 per barrel — 30 percent above pre-war levels. Higher energy costs squeeze corporate margins, weaken the current account, and put downward pressure on the rupee, all of which reduce the attractiveness of Indian equities for foreign investors.

**Currency depreciation.** The rupee has fallen approximately 6 percent against the dollar in 2026. For foreign investors, this means their returns in Indian equities are eroded when converted back to dollars. A stock that gains 10 percent in rupee terms delivers only about 4 percent in dollar terms after accounting for the currency slide.

**The AI trade.** Markets in South Korea and Taiwan have surged on the back of the global artificial intelligence boom, drawing capital away from India. Samsung, TSMC, and other Asian chipmakers have delivered outsized returns, making India's consumption-driven market less attractive by comparison.

## Markets Expected to Recover Monday

Despite Friday's bloodbath, early indicators suggest Monday will bring relief. GIFT Nifty futures were trading at 23,726 as of 7:40 AM IST, indicating the benchmark Nifty 50 will open above Friday's close.

The recovery expectation rests on the fact that Friday's selling was largely technical and index-driven rather than reflecting a fundamental deterioration in India's economic outlook. Corporate earnings for the March quarter have been broadly in line with expectations, and India's GDP growth remains among the fastest of any major economy.

"As seen on Friday, those flows would matter little if the RBI decides to keep the currency anchored around a certain level," the Mumbai-based trader added.

## What NRI Investors Should Watch

For diaspora investors with exposure to Indian equities — whether through direct investments, mutual funds, or NRE/NRO-linked portfolios — the record sell-off raises legitimate questions about near-term volatility.

The key events this week include the RBI's monetary policy decision on June 5, where the central bank is widely expected to hold the repo rate at 5.25 percent but may signal a more hawkish posture. India's January-March GDP data, also due on June 5, will provide a clearer picture of whether the oil shock is beginning to dent economic growth. A Reuters poll expects 7.3 percent growth for the quarter.

The HSBC Manufacturing PMI for May, due today (Monday), will offer an early read on whether factory activity is holding up despite the energy headwinds.

Record one-day outflows make for alarming headlines, but they are rarely inflection points. The last time Indian markets experienced a comparable sell-off driven by index rebalancing — in November 2024 — the Nifty recovered within two weeks.

*Sources: Reuters, LSEG data, Goldman Sachs, National Stock Exchange of India, provisional exchange data*"""

img_3, attr_3 = source_image(
    "india-record-foreign-sell-off-222-billion-msci-rebalancing-nse-turnover-20260601",
    pexels_query="stock market trading screen India",
    pexels_fallback="stock exchange trading floor"
)

articles.append({
    "headline": "Foreign Investors Just Dumped $2.22 Billion in Indian Stocks in a Single Day. It Was the Largest Sell-Off in History.",
    "subheadline": "MSCI's index rebalancing triggered record outflows and pushed NSE turnover past ₹2.87 trillion. Markets are expected to recover on Monday — but the structural headwinds remain.",
    "slug": "india-record-foreign-sell-off-222-billion-msci-rebalancing-nse-turnover-20260601",
    "body": body_3,
    "category": "news",
    "status": "published",
    "published_at": datetime.now(timezone.utc).isoformat(),
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "LSEG", "url": "https://www.lseg.com/"},
        {"name": "Goldman Sachs", "url": "https://www.goldmansachs.com/"},
        {"name": "National Stock Exchange of India", "url": "https://www.nseindia.com/"}
    ]),
    "vertical": "news",
    "image_url": img_3,
    "image_attribution": attr_3 or "Pexels",
    "is_editorial": False
})


# ─── Check skip list ───
skip_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/image-skip-list.json')
skip_list = []
if os.path.exists(skip_path):
    with open(skip_path) as f:
        skip_list = json.load(f)


# ─── Insert all articles ───
print("\n=== Inserting articles ===")
# Article 3 was already inserted in a prior run
already_inserted = {"india-record-foreign-sell-off-222-billion-msci-rebalancing-nse-turnover-20260601"}
for art in articles:
    slug = art['slug']
    
    if slug in already_inserted:
        print(f"  ⏭ Skipping {slug} (already inserted)")
        continue
    
    # Skip if in image skip list
    if slug in skip_list:
        print(f"  ⚠ Skipping {slug} (in image skip list)")
        art.pop('image_url', None)
        art.pop('image_attribution', None)
    
    # Validate image
    if art.get('image_url'):
        try:
            head = requests.head(art['image_url'], timeout=10, allow_redirects=True)
            ct = head.headers.get('Content-Type', '')
            cl = int(head.headers.get('Content-Length', '0'))
            if head.status_code != 200 or 'image' not in ct or cl < 5000:
                print(f"  ⚠ Image validation failed for {slug}: status={head.status_code}, ct={ct}, cl={cl}")
                art['image_url'] = None
                art['image_attribution'] = None
        except Exception as e:
            print(f"  ⚠ Image validation error for {slug}: {e}")
            art['image_url'] = None
            art['image_attribution'] = None
    
    # Clean up None values
    art = {k: v for k, v in art.items() if v is not None}
    
    art_id = insert_article(art)
    if art_id:
        print(f"  ✓ Published: {art['headline'][:60]}...")
    else:
        print(f"  ✗ Failed: {art['headline'][:60]}...")

print("\n=== Done ===")
