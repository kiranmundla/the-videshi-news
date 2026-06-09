#!/usr/bin/env python3
"""
News writer for The Videshi — June 9, 2026
Generates 3 news articles, sources images, uploads to Supabase.
"""

import requests, json, os, io, re, time, uuid, urllib.parse
from datetime import datetime, timezone
from PIL import Image

# Load environment
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ.setdefault(key.strip(), val.strip())

load_env('~/.env.supabase')
load_env('~/workspace/.env.pexels')

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_API_KEY = os.environ['PEXELS_API_KEY']
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

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

def fetch_wikipedia_person_image(person_name):
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
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
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
                print(f"  ✓ Wikimedia Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
    return []

def fetch_pexels_image(query):
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            for p in photos:
                url = p.get("src", {}).get("large2x") or p.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image: {url[:80]}...")
                    return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and len(r.content) > 5000:
            ct = r.headers.get("Content-Type", "")
            if "image" in ct or url.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                return r.content
        print(f"  ⚠ Image download failed: status={r.status_code}, size={len(r.content)}")
    except Exception as e:
        print(f"  ⚠ Image download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase storage bucket 'article-images'"""
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    print(f"  Compressed image: {size_kb:.0f} KB")
    
    upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    r = requests.post(
        upload_url,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        },
        data=compressed,
        timeout=30
    )
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def insert_article(article):
    """Insert article into p2_articles"""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Article inserted: {art_id}")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def source_image(person_name=None, wiki_queries=None, pexels_query=None, slug="article"):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []
    
    # Wikipedia person image
    if person_name:
        wiki_img = fetch_wikipedia_person_image(person_name)
        if wiki_img:
            candidates.append({"url": wiki_img, "source": "wikipedia", "priority": 1})
    
    # Wikimedia Commons
    if wiki_queries:
        for q in wiki_queries:
            results = fetch_wikimedia_commons_images(q)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})
    
    # Pexels
    if pexels_query:
        px = fetch_pexels_image(pexels_query)
        if px:
            candidates.append({"url": px, "source": "pexels", "priority": 3})
    
    # Try candidates in priority order
    for c in sorted(candidates, key=lambda x: x["priority"]):
        img_bytes = download_image(c["url"])
        if img_bytes and len(img_bytes) > 5000:
            filename = f"{slug}.jpg"
            public_url = upload_to_supabase(img_bytes, filename)
            if public_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return public_url, attr
    
    return None, None


# ============================================================
# ARTICLE 1: EB-2 India Visa Retrogression
# ============================================================
print("\n" + "="*60)
print("ARTICLE 1: EB-2 India Visa Retrogression")
print("="*60)

art1_slug = "eb2-india-retrogression-june-2026-green-card-10-months-backward"
art1_headline = "The US Just Moved the EB-2 India Green Card Line Backward by 10 Months. Thousands Are Stuck Again."
art1_subheadline = "The June 2026 visa bulletin pushed the EB-2 India final action date to September 2013 — erasing nearly a year of progress for Indian professionals waiting for permanent residency."

art1_body = """The June 2026 US Visa Bulletin delivered a gut punch to hundreds of thousands of Indian professionals waiting for employment-based green cards. The EB-2 India final action date — the cutoff that determines who can file for permanent residency — moved backward by more than 10 months, landing at September 1, 2013.

The retrogression effectively erases a year's worth of forward movement. Applicants who had been tracking their priority dates, gathering documents, and preparing I-485 filings now face an indefinite wait all over again.

## What Changed

The US State Department's June bulletin pushed the EB-2 India date back from roughly July 2014 to September 2013. The EB-1 India category also slipped about three and a half months, to December 15, 2022. Both shifts were driven by the same problem: demand from India-chargeable applicants overwhelmed the fiscal year's remaining visa numbers.

For now, USCIS will continue accepting employment-based adjustment filings using the more generous Dates for Filing chart. But the bulletin carried a stark warning: further retrogression, or even an "unavailable" designation, may follow before the fiscal year ends in September if India's pro-rated limits run out.

## Why It Keeps Happening

The structural problem has not changed in decades. The US caps employment-based green cards at 140,000 per year, with a 7% per-country limit. India and China consistently exceed their allocations, creating backlogs that stretch over a decade for EB-2 applicants. A software engineer who filed a labor certification in 2014 is still waiting. A physician who filed in 2015 has no visibility on when approval might come.

The per-country cap — originally designed to ensure diversity in immigration — has become the single biggest bottleneck for skilled Indian workers. With roughly 1 million Indians in the EB-2 and EB-3 queues combined, the math is unforgiving: at current processing rates, some applicants face wait times exceeding 50 years.

## The Human Cost

The retrogression lands at a particularly difficult time. Indian professionals on H-1B visas cannot change employers freely while waiting in the green card queue. They cannot start companies. Their spouses on H-4 visas face their own employment restrictions. Children who age out at 21 lose their place in line entirely — a cruel provision that has separated families.

"Every retrogression announcement sends a wave of anxiety through Indian tech workers," said one immigration attorney who advises Fortune 500 companies on visa strategy. "These are people who have been in the US for 10, 15, sometimes 20 years. They pay taxes, buy homes, raise children here. And every few months, the line moves backward."

The National Interest Waiver route — which bypasses the labor certification requirement — offers no relief either. NIW applicants share the same EB-2 India queue, so the retrogression hits them equally.

## What NRIs Can Do Now

Immigration experts recommend several steps for those caught in the retrogression. Applicants with pending I-485 filings retain their employment authorization and advance parole benefits. Those who haven't filed should monitor the Dates for Filing chart, which may still allow new filings even as the Final Action Date moves backward.

Some are exploring the EB-1 route, which requires demonstrating extraordinary ability or being a multinational manager. Others are considering EB-5 investor visas, though the $800,000 minimum investment puts that option out of reach for most.

The only systemic fix — raising or eliminating the per-country cap — requires Congressional action. Bills like the Eagle Act have stalled repeatedly, most recently in 2024. With Congress focused on the Iran conflict and midterm elections, immigration reform is nowhere near the legislative agenda.

For now, the wait continues. The October 2026 bulletin, which opens a new fiscal year, may bring some forward movement. But after a decade of broken promises and incremental progress followed by sharp retreats, few in the Indian professional community are holding their breath."""

print("Sourcing image for Article 1...")
art1_img_url, art1_img_attr = source_image(
    wiki_queries=["United States visa immigration office", "USCIS immigration"],
    pexels_query="US immigration visa passport office",
    slug=art1_slug
)

art1_data = {
    "headline": art1_headline,
    "subheadline": art1_subheadline,
    "body": art1_body,
    "slug": art1_slug,
    "category": "news",
    "vertical": "news",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "US Department of State Visa Bulletin June 2026",
        "WR Immigration analysis",
        "Fragomen immigration advisory",
        "Asanify EOR & Compliance Digest June 6 2026"
    ]),
    "image_url": art1_img_url or "",
    "image_caption": "A US Citizenship and Immigration Services facility processes visa applications",
    "image_attribution": art1_img_attr or "Wikimedia Commons",
    "published_at": datetime.now(timezone.utc).isoformat()
}

art1_id = insert_article(art1_data)

# ============================================================
# ARTICLE 2: India Inc Shrinkflation
# ============================================================
print("\n" + "="*60)
print("ARTICLE 2: India Inc Shrinkflation")
print("="*60)

art2_slug = "india-inc-shrinkflation-price-hikes-iran-war-consumer-squeeze-20260609"
art2_headline = "Your Biscuit Packet Is Smaller. Your Petrol Bill Is Higher. India Inc Is Passing the War to You."
art2_subheadline = "From Hindustan Unilever to Maruti Suzuki, Indian companies are hiking prices and shrinking product sizes as the Iran war drives up oil, freight, and raw material costs across the board."

art2_body = """The war is no longer just on television. It is in your grocery bill, at the petrol pump, and in the subtly smaller packet of biscuits that costs the same as it did three months ago.

Indian companies — from consumer giants to automakers to airlines — are scrambling to protect their margins as the Iran war sends oil prices, freight costs, and insurance premiums spiralling. The playbook is familiar: raise prices where consumers will tolerate it, and quietly shrink the product where they will not.

## The Shrinkflation Playbook

Hindustan Unilever, Godrej Consumer Products, and Dabur India have already rolled out low- to mid-single-digit price hikes across their product portfolios. Britannia is preparing similar moves. But in mass-market segments — where the price-sensitive Indian consumer watches every rupee — the strategy is different.

"We are reducing grammage because we can't breach those price points," said Mohit Malhotra, global CEO at Dabur, describing the dilemma facing companies selling at ₹10 to ₹20 price points. A ₹10 packet of chips that weighed 30 grams last quarter might now weigh 25 grams. The consumer pays the same. The company survives another quarter.

This is shrinkflation — the practice of reducing product size or quantity while keeping the price unchanged. It is economically identical to a price hike, but psychologically invisible. And it is spreading across India's consumer economy faster than the official inflation numbers suggest.

## Beyond FMCG

The squeeze is not limited to biscuits and shampoo. Automakers Maruti Suzuki, Mahindra & Mahindra, Tata Motors, and Hyundai Motor India have all announced price hikes in recent weeks. "We were left with no choice," said Partho Banerjee, Maruti's senior executive officer for marketing and sales. "Raising prices is not good for customers, especially first-time buyers."

Airlines IndiGo and Air India are trimming capacity on fuel-heavy international routes and increasing fares. Aviation turbine fuel costs have risen sharply with Brent crude hovering near $97 a barrel — up roughly 40% since the conflict began in February.

Even India's massive food delivery and restaurant sector is feeling it. Cooking oil prices are up. Packaging costs are up. Delivery fuel surcharges have appeared on platforms that spent years conditioning consumers to expect free delivery.

## Why India Gets Hit Harder

India imports roughly 90% of its crude oil. When global oil prices rise, the impact cascades through the economy — not just at the petrol pump, but through freight charges, packaging costs, and the price of every petrochemical-derived input from plastics to fertilisers.

"We are among the world's most vulnerable countries," economist Jayati Ghosh warned, pointing to the triple threat of higher oil costs, weaker Gulf demand reducing remittances, and potential capital outflows as global investors seek safer markets.

The rupee's decline has compounded the problem. A weaker currency means imports cost more in rupee terms, creating a vicious cycle: higher oil prices weaken the rupee, which makes oil even more expensive, which drives more inflation.

## The Consumer Squeeze

For Indian households, the arithmetic is brutal. Fuel prices have been raised four times in three weeks. Food inflation — driven by heatwaves, delayed monsoons, and rising input costs — was already a concern before the war. The Consumer Price Index crossed the RBI's 4% target in May for the first time since late 2025.

Salaried workers and gig economy participants are feeling the squeeze most acutely. Wages have not kept pace with the cost increases. Rural consumers, who drive a significant share of FMCG demand, are pulling back on discretionary purchases.

## What Comes Next

Analysts expect another round of price hikes by July if Brent crude stays above $90. Companies that have so far absorbed cost increases to protect market share will reach the limits of their balance sheets.

The RBI faces an impossible choice: raise interest rates to fight inflation, which would slow an already-pressured economy, or hold rates and risk letting inflation spiral. Friday's $50 billion forex defense measures bought time, but did not address the underlying cost problem.

For consumers, the message is clear: the Iran war's economic impact is no longer abstract. It is measured in smaller packets, higher EMIs, and a monthly budget that no longer stretches as far as it used to."""

print("Sourcing image for Article 2...")
art2_img_url, art2_img_attr = source_image(
    wiki_queries=["Indian market shopping grocery", "India retail store consumer goods"],
    pexels_query="Indian grocery store market shopping",
    slug=art2_slug
)

art2_data = {
    "headline": art2_headline,
    "subheadline": art2_subheadline,
    "body": art2_body,
    "slug": art2_slug,
    "category": "news",
    "vertical": "news",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "Reuters - India Inc hikes prices shrinks packs as Iran war squeezes margins",
        "Reuters - Indian economy government finances see mounting costs from Iran war",
        "Dabur India CEO Mohit Malhotra comments",
        "Maruti Suzuki executive Partho Banerjee statement"
    ]),
    "image_url": art2_img_url or "",
    "image_caption": "An Indian consumer goods store stocked with household products and groceries",
    "image_attribution": art2_img_attr or "Pexels",
    "published_at": datetime.now(timezone.utc).isoformat()
}

art2_id = insert_article(art2_data)

# ============================================================
# ARTICLE 3: India Economy Mounting Costs from Iran War
# ============================================================
print("\n" + "="*60)
print("ARTICLE 3: India Economy Mounting Costs of Iran War")
print("="*60)

art3_slug = "india-economy-iran-war-cost-gdp-growth-slowdown-supply-shocks-20260609"
art3_headline = "India's Goldilocks Economy Is Over. The Iran War Broke It."
art3_subheadline = "GDP growth projected to slow to 6.7% in FY27 as oil at $97, a weak rupee, and fertiliser shortages create overlapping supply shocks that the RBI cannot simply cut its way out of."

art3_body = """Six months ago, RBI Governor Sanjay Malhotra described India's economy as being in a "rare Goldilocks phase" — growth was strong, inflation was falling, and the fiscal position was improving. That phrase has aged poorly.

The Iran war, now in its fourth month, has methodically dismantled every pillar of that optimism. Oil is at $97 a barrel. The rupee has weakened past its worst levels. Foreign institutional investors pulled $20 billion out of India in March and April alone. Forex reserves have shrunk by $27-28 billion since the conflict began. And the worst may not be over.

## The Growth Downgrade

Economists at CareEdge Ratings now project India's GDP growth will moderate to around 6.7% in the current financial year (FY27), down from 7.7% in FY26. The Asian Development Bank is even more bearish, forecasting a 0.7 percentage-point drag on growth across all of Asia if oil averages $96 a barrel this year. In a severe scenario of $200 oil, the ADB warns growth would fall by 1.2% and inflation would hit 7.4%.

India's current account deficit is expected to widen to 2.1% of GDP, more than doubling from around 1% in FY26. The widening is driven by higher oil import bills, disrupted trade routes, and weaker invisibles — the services exports and remittances that have traditionally cushioned India's external balance.

"The West Asia crisis is going to impact the Indian economy through various channels," said Rajani Sinha, Chief Economist at CareEdge Ratings. "Not just growth and inflation, but it's also going to adversely impact government finances and, very worryingly, India's balance of payments situation."

## The Overlapping Shocks

What makes this crisis different from past oil shocks is the number of fronts it is hitting simultaneously. The Strait of Hormuz closure has disrupted not just oil but fertiliser supplies. India sources 34% of its fertiliser imports from the Middle East. With the kharif sowing season approaching and an El Niño weather phenomenon threatening drought conditions, the fertiliser disruption could translate directly into lower agricultural output and higher food prices.

"India is set for a series of supply shocks," said Michael Langham, emerging markets economist at Aberdeen Investments. "The ability of the RBI to look through the energy price shock from the Strait of Hormuz will be increasingly difficult given the overlapping nature of these supply shocks."

Gulf demand for Indian goods and services has also weakened, adding pressure on exports. Remittances from the Gulf — a critical source of foreign exchange for states like Kerala, Andhra Pradesh, and Tamil Nadu — are expected to slow as construction and services activity in the region contracts.

## The RBI's Impossible Position

The central bank has been fighting on multiple fronts. Last Friday, it unveiled a $50 billion forex defense package, including concessional swap facilities for NRI deposits, expanded leverage allowances for foreign currency deposits, and separate swap facilities for public sector external commercial borrowings.

On investment policy, the RBI has doubled the individual investment limit for NRIs and OCI cardholders in listed Indian companies from 5% to 10%, and raised the aggregate foreign portfolio limit from 10% to 24%. The moves are designed to attract diaspora capital at a time when other sources of foreign exchange are drying up.

But these are defensive measures. They buy time without solving the underlying problem: India's economy is structurally exposed to a prolonged energy disruption, and the tools to address it — rate cuts, fiscal stimulus, diplomatic resolution — are all constrained.

Rate cuts would risk stoking inflation that has already crossed the RBI's 4% target. Fiscal stimulus would widen a deficit already strained by fuel subsidies and defence spending. And diplomatic resolution depends on Washington and Tehran, not New Delhi.

## What FY26 Tells Us

India's FY26 numbers were strong enough to provide a buffer. GDP grew 7.7% for the full year, with the January-March quarter coming in at 7.8% — beating most forecasts. Manufacturing expanded 10.7%. Private consumption rose 7.7%. Government infrastructure spending remained robust.

But those numbers were largely delivered before the Iran war's full economic impact hit. The March quarter benefited from policy tailwinds and domestic momentum that are now fading. The question is not whether the war will slow India's economy — it already has. The question is by how much, and for how long.

## The Diaspora Angle

For NRIs watching from abroad, the crisis creates both risk and opportunity. The RBI's new investment rules make it significantly easier to invest in Indian markets. The rupee's weakness means dollar-denominated remittances buy more in India. And the government's foreign asset disclosure scheme — offering immunity for undisclosed overseas assets up to ₹1 crore — suggests Delhi is actively courting diaspora capital.

But the investment case depends on the war ending. If Hormuz remains closed into the second half of 2026, the growth outlook deteriorates further, the rupee weakens further, and the stock market — already at two-month lows — has more room to fall.

India entered 2026 as the world's strongest major economy. It may not exit the year with that title intact."""

print("Sourcing image for Article 3...")
# Try RBI Governor or Indian economy imagery
art3_img_url, art3_img_attr = source_image(
    person_name="Sanjay Malhotra RBI",
    wiki_queries=["Reserve Bank of India Mumbai building", "Indian economy stock exchange Bombay"],
    pexels_query="Indian rupee currency economy finance",
    slug=art3_slug
)

art3_data = {
    "headline": art3_headline,
    "subheadline": art3_subheadline,
    "body": art3_body,
    "slug": art3_slug,
    "category": "news",
    "vertical": "news",
    "status": "review",
    "is_editorial": False,
    "sources": json.dumps([
        "Reuters - Indian economy government finances see mounting costs from Iran war",
        "Reuters - Indian shares decline to two-month lows on oil spike",
        "CareEdge Ratings - Rajani Sinha GDP and CAD projections",
        "Asian Development Bank growth forecast",
        "Brookings Institution - Iran war Asia economic security analysis",
        "Aberdeen Investments - Michael Langham supply shock analysis"
    ]),
    "image_url": art3_img_url or "",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, the nerve centre of India's monetary policy response",
    "image_attribution": art3_img_attr or "Wikimedia Commons",
    "published_at": datetime.now(timezone.utc).isoformat()
}

art3_id = insert_article(art3_data)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
results = [
    ("EB-2 India Retrogression", art1_slug, art1_id, art1_img_url),
    ("India Inc Shrinkflation", art2_slug, art2_id, art2_img_url),
    ("India Economy Iran War Cost", art3_slug, art3_id, art3_img_url),
]
for title, slug, aid, img in results:
    status = "✓" if aid else "✗"
    img_status = "✓ image" if img else "⚠ no image"
    print(f"  {status} {title}: {slug} ({img_status})")

print("\nDone.")
