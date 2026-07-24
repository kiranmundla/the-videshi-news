#!/usr/bin/env python3
"""
News writer batch — 2026-06-12 00:30 UTC
Three articles:
1. US inflation hits 4.2% three-year high + PPI surges — impact on India and NRIs
2. India rejects US Section 301 overcapacity charges on textiles and steel
3. India scraps bond taxes for foreigners — $1B+ inflows in a week
"""

import os, json, sys, uuid, requests, io, time, re
from datetime import datetime, timezone
from urllib.parse import quote, quote_plus

# Load env
def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

UA = "TheVideshi/1.0 (thevideshi.com)"

# ── Image sourcing functions ──

def fetch_wikipedia_person_image(person_name):
    encoded = quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": UA}, timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None

def fetch_wikimedia_commons_images(search_query, limit=5):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": search_query, "gsrnamespace": "6",
        "gsrlimit": str(limit), "prop": "imageinfo",
        "iiprop": "url|size|mime", "iiurlwidth": "1200", "format": "json"
    }
    try:
        r = requests.get("https://commons.wikimedia.org/w/api.php",
                         params=params, headers={"User-Agent": UA}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                w = ii.get("width", 0)
                if w < 300:
                    continue
                results.append({
                    "url": ii.get("thumburl") or ii.get("url", ""),
                    "original_url": ii.get("url", ""),
                    "title": page.get("title", ""),
                    "width": w, "height": ii.get("height", 0)
                })
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{search_query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels_image(query):
    if not PEXELS_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY, "User-Agent": UA},
            timeout=10
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                url = photos[0]["src"]["large2x"]
                print(f"  ✓ Pexels image for '{query}': {url[:80]}...")
                return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if r.status_code == 200 and r.headers.get('content-type', '').startswith('image'):
            data = r.content
            if len(data) > 5000:
                return data
            print(f"  ⚠ Image too small: {len(data)} bytes")
    except Exception as e:
        print(f"  ⚠ Download error: {e}")
    return None

def upload_to_supabase(img_bytes, filename):
    compressed = compress_image(img_bytes)
    size_kb = len(compressed) / 1024
    print(f"  📦 Compressed to {size_kb:.0f} KB")
    if size_kb < 10:
        print(f"  ⚠ Too small after compression, skipping")
        return None

    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true"
    }
    r = requests.post(url, headers=headers, data=compressed, timeout=30)
    if r.status_code in (200, 201):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✓ Uploaded: {public_url[:80]}...")
        return public_url
    else:
        print(f"  ⚠ Upload failed: {r.status_code} {r.text[:200]}")
        return None

def source_image(slug, person_name=None, topic_queries=None, pexels_query=None):
    """Multi-source image search. Returns (url, attribution) or (None, None)."""
    candidates = []

    # Source 1: Wikipedia person image
    if person_name:
        wiki_url = fetch_wikipedia_person_image(person_name)
        if wiki_url:
            candidates.append({"url": wiki_url, "source": "wikipedia", "priority": 1})

    # Source 2: Wikimedia Commons
    if topic_queries:
        for q in topic_queries[:3]:
            results = fetch_wikimedia_commons_images(q, limit=3)
            for r in results[:2]:
                candidates.append({"url": r["url"], "source": "wikimedia_commons", "priority": 2})

    # Source 3: Pexels (last resort)
    if pexels_query:
        pexels_url = fetch_pexels_image(pexels_query)
        if pexels_url:
            candidates.append({"url": pexels_url, "source": "pexels", "priority": 3})

    # Sort by priority and try to download + upload
    candidates.sort(key=lambda x: x["priority"])
    for c in candidates:
        print(f"  Trying {c['source']}: {c['url'][:80]}...")
        img_data = download_image(c["url"])
        if img_data:
            filename = f"{slug}.jpg"
            final_url = upload_to_supabase(img_data, filename)
            if final_url:
                attr = "Wikimedia Commons" if c["source"] in ("wikipedia", "wikimedia_commons") else "Pexels"
                return final_url, attr

    print(f"  ⚠ No image found for {slug}")
    return None, None

def insert_article(article):
    """Insert article into Supabase."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        art_id = data[0]["id"] if isinstance(data, list) else data.get("id")
        print(f"  ✓ Inserted: {article['slug']} (id={art_id})")
        return art_id
    else:
        print(f"  ✗ Insert failed: {r.status_code} {r.text[:300]}")
        return None

# ── Articles ──

now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

ARTICLES = [
    {
        "headline": "US Inflation Just Hit a Three-Year High. The Fed May Hike Rates. Here Is What That Means for India.",
        "subheadline": "Consumer prices rose 4.2 per cent in May as the Iran oil shock ripples through the American economy. Producer prices surged even faster. For NRIs with mortgages, investments and families back home, the math just changed.",
        "slug": "us-inflation-4-2-percent-three-year-high-fed-rate-hike-india-nri-impact-20260612",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "sources": json.dumps([
            "Reuters", "CNN", "Wall Street Journal", "MarketWatch", "The Motley Fool"
        ]),
        "diaspora_angle": "Rising US inflation and potential Fed rate hikes directly affect NRI mortgage costs, dollar-rupee remittance rates, and the trajectory of FPI flows into Indian markets.",
        "body": """America's inflation problem just got materially worse, and for the roughly five million Indians living in the United States, the consequences are no longer abstract.

The Bureau of Labor Statistics reported on Wednesday that the Consumer Price Index rose 4.2 per cent year-on-year in May, the fastest pace in three years. The headline number was driven by elevated fuel prices — a direct casualty of the Iran war that has disrupted roughly 20 million barrels of daily oil flow through the Strait of Hormuz since late February.

On Thursday, the picture darkened further. The Producer Price Index, which tracks wholesale costs, surged even more sharply, with core PPI (excluding food and energy) holding at 4.9 per cent annually. A stripped-down measure that also excludes trade services jumped 0.8 per cent in May alone — a four-year high.

## The Fed's Dilemma

The data has reshaped expectations for the Federal Reserve. Markets now price a 38.7 per cent chance of a rate hike by September, up from 35.2 per cent before the PPI release. By December, the odds of higher rates have climbed to 69 per cent.

"The key concern is not whether inflation is too high — it clearly is — but whether it has become self-reinforcing," said Oliver Allen, senior US economist at Pantheon Macroeconomics. The initial shock was fuel. But wholesalers and retailers are now passing costs through to consumers across goods categories, and tariff-driven price increases from 2025 show no sign of abating.

Federal Reserve Chair Kevin Warsh has expressed a preference for "trimmed average" inflation measures that strip out extreme price swings, including the oil shock. By that metric, inflation looks more contained — the Dallas Fed's trimmed mean PCE clocked 2.35 per cent annualised in April. But critics argue this approach risks repeating the Fed's 2021 mistake of dismissing inflation as transitory.

## What It Means for NRIs

The implications cascade in several directions at once.

**Mortgages and housing.** The 30-year fixed mortgage rate is hovering near its highest level of the year. For NRIs who bought homes in the US during the low-rate era of 2020-21, refinancing is off the table. For those looking to buy, every quarter-point increase adds roughly $40 to the monthly payment on a $400,000 loan.

**Remittances.** A stronger dollar, which typically accompanies rate hikes, is a double-edged sword. NRIs sending money home get more rupees per dollar — the rupee is already at 95.27 per dollar. But if rate hikes trigger a US recession, the income that funds those remittances could shrink.

**Indian markets.** Foreign portfolio investors have already pulled roughly $29 billion out of Indian equities in 2026. Higher US rates make American assets more attractive, accelerating that outflow. Indian IT stocks, which derive the bulk of their revenue from the US, have fallen 10.6 per cent in seven straight sessions.

**The RBI's response.** India's central bank has already cut its growth forecast for FY27 to 6.6-6.9 per cent. It announced a concessional forex swap facility this week to attract NRI deposits and support the rupee. The question is whether monetary easing at home can offset the gravitational pull of rising American rates.

## The Oil Connection

The throughline remains the Iran war. The conflict has produced the most severe energy supply disruption in modern history. Brent crude, after swinging between $89 and $98 per barrel earlier this week, settled at $90.38 on Thursday after President Trump said a peace deal could be signed as soon as this weekend.

But even if a deal materialises, analysts warn the inflationary damage is already baked in. "The higher fuel prices appear to be starting to spill over into higher goods prices and may be starting to lift some services prices," Allen said. PPI data suggests that second-round effects — businesses adjusting prices to protect margins — are only beginning.

## What to Watch Next

The Fed's preferred inflation gauge, the core PCE index, is due later this month. Economists now expect it to rise to 3.4 per cent, the highest since late 2023. If that forecast holds, the case for a rate hike by September or October becomes considerably stronger.

For NRIs, the practical takeaway is straightforward: the cost of living in America is rising faster than wages, the cost of borrowing is likely to follow, and the ripple effects will reach every corner of the Indian economy that depends on dollar flows. The era of cheap money is not coming back anytime soon.""",
        "image_search": {
            "topic_queries": ["US Federal Reserve building Washington", "Federal Reserve interest rate inflation"],
            "pexels_query": "US Federal Reserve building",
            "image_caption": "The Federal Reserve building in Washington, D.C.",
            "person_name": None
        }
    },
    {
        "headline": "India Tells the US It Does Not Have Overcapacity in Anything. Washington Disagrees.",
        "subheadline": "As America's Section 301 probe targets 16 countries, India's top trade official fires back with a blunt defence: per capita consumption is too low for overcapacity to exist. A $42 billion trade surplus hangs in the balance.",
        "slug": "india-rejects-us-section-301-overcapacity-textiles-steel-trade-surplus-20260612",
        "category": "news",
        "vertical": "geopolitics",
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "sources": json.dumps([
            "Reuters", "Outlook Business", "The Hindu BusinessLine", "Swadesi"
        ]),
        "diaspora_angle": "Section 301 tariffs on Indian goods would directly affect NRI-linked businesses in textiles, steel and IT services, and could disrupt the broader India-US trade deal that both sides are negotiating.",
        "body": """India has rejected American allegations that it maintains surplus manufacturing capacity in textiles and steel, pushing back against a US trade investigation that could eventually lead to punitive tariffs on Indian exports.

"Overcapacity is a country's perspective. We don't think we have overcapacity in anything," Amitabh Kumar, India's Director General of Trade Remedies and Additional Secretary in the Commerce Ministry, told reporters on Wednesday.

The remarks are India's most direct public response yet to the US Trade Representative's Section 301 investigation, launched in March against 16 countries over policies that Washington says allow factories to keep producing even when market conditions do not support it. The probe covers a sweeping range of Indian industries — from solar modules and petrochemicals to steel and textiles.

## 'We Wear Cotton. How Do We Have Overcapacity?'

Kumar's defence rested on a simple but powerful argument: India's output should be measured against its population, not in absolute terms.

On textiles, he pointed out that India's per capita consumption of textile products — particularly man-made fibre and technical textiles — remains "abysmal" by global standards. "This country has a hot climate, tropical climate. We wear cotton. How do we have overcapacity?" he said. India remains a net importer of man-made fibres.

On steel, the case was similar. India is the world's second-largest producer of steel, but Kumar noted that per capita consumption is among the lowest globally. "Compared to our population, our economic and growth imperative, it's one of the lowest," he said.

Kumar also challenged the legal framework of the US probe itself, arguing that overcapacity "has not come under any of the trade remedial laws in the WTO framework" and calling it "a new narrative" — a pointed suggestion that Washington is inventing rules as it goes.

## The $42 Billion Question

The stakes are considerable. India ran a $42 billion goods trade surplus with the United States in 2025, a figure that has drawn repeated attention from the Trump administration. Trade analysts say Washington is using the Section 301 threat not primarily to address overcapacity, but as leverage to force India to open its markets for American agricultural products and to increase purchases of US energy and defence equipment.

India, for its part, is seeking a bilateral trade deal that would give it preferential tariffs compared to competitors like China and Vietnam. But the negotiations are clouded by the same investigations that India is now pushing back against.

The timing is particularly sensitive. Prime Minister Modi and President Trump are set to meet at the G7 summit in France next week, where trade is expected to feature prominently on the bilateral agenda. A resolution — or an escalation — could come quickly.

## Why NRIs Should Pay Attention

For the Indian diaspora, particularly those in the United States, the Section 301 probe touches multiple pressure points.

Indian-American entrepreneurs and importers who deal in Indian textiles, garments and steel products would face higher costs if tariffs are imposed. The IT and business services sector, while not directly named in the current probe, operates in the same diplomatic ecosystem — any deterioration in the broader trade relationship creates risk.

More broadly, the India-US trade relationship has been a cornerstone of the economic case for the diaspora's engagement with both countries. A sustained trade conflict would complicate the "bridge" role that NRI business leaders have played for decades.

India's submission to the USTR has stated that the investigation "has not provided cogent rationale or prima facie evidence" to support the overcapacity allegations. Whether Washington finds that argument persuasive will depend less on economics than on politics — and on what concessions India is prepared to make at the negotiating table.

## What Happens Next

The USTR is expected to hold hearings and issue findings over the coming months. If it concludes that India's industrial policies cause harm to American industries, it could recommend tariffs on specific Indian products — a move that would trigger retaliatory measures from New Delhi.

For now, India's strategy appears to be a combination of public pushback and quiet negotiation. The G7 meeting next week will be the first real test of whether that approach is working.""",
        "image_search": {
            "topic_queries": ["India US trade talks meeting", "USTR Section 301 investigation", "India textile industry factory"],
            "pexels_query": "international trade negotiation meeting",
            "image_caption": "India and the United States are locked in a trade dispute over alleged manufacturing overcapacity",
            "person_name": None
        }
    },
    {
        "headline": "India Scrapped Bond Taxes for Foreigners. A Billion Dollars Arrived in Three Days.",
        "subheadline": "The government's decision to exempt foreign investors from taxes on government bonds has triggered the fastest debt inflows this year, pushed yields down sharply and opened a path to global index inclusion worth tens of billions more.",
        "slug": "india-bond-tax-exemption-foreign-investors-billion-dollar-inflows-global-index-20260612",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "sources": json.dumps([
            "Reuters", "The Hindu BusinessLine", "PTI", "State Street Investment Management", "SBI Economic Research"
        ]),
        "diaspora_angle": "The package includes direct NRI incentives — concessional forex swaps and deposit schemes — while the bond market opening could stabilise the rupee and lower government borrowing costs that ultimately affect everything from home loans to infrastructure spending.",
        "body": """India just pulled off something that six months of diplomatic effort could not: it got foreign money to flow in.

On June 5, the government promulgated an ordinance scrapping withholding and capital gains taxes on foreign investments in Indian government bonds. The move was part of a broader package that included expanding the pool of securities available under the Fully Accessible Route, incentivising banks to raise foreign currency deposits from non-resident Indians, and encouraging companies to tap overseas borrowings.

The response was immediate. More than one billion dollars worth of government debt was purchased by foreign investors in just three trading sessions — more than half the total $1.6 billion that had trickled in during the entire year up to that point.

## The Numbers Tell the Story

The benchmark 10-year government bond yield fell from 7.024 per cent on June 3 to 6.911 per cent by Wednesday — a drop of over 10 basis points in four days. Shorter maturities saw even steeper declines, with yields falling 20 to 30 basis points across the curve.

Foreign portfolio investors poured Rs 11,026 crore into government securities through the Fully Accessible Route in the four days following the announcement, according to data compiled by PTI.

"We believe that these changes are a game-changer for debt flows," said Jennifer Taylor, head of emerging market debt and systematic fixed income at State Street Investment Management, which manages about $5.6 trillion in assets globally.

V. Ramachandra Reddy, head of treasury at Karur Vysya Bank, said the rally was driven by "strong foreign participation and increased flows into FAR securities" following the tax exemption.

## Why Now

The timing was not coincidental. India's external position has come under sustained pressure from the Iran war, which has pushed oil prices above $90 per barrel and triggered the largest energy supply disruption in modern history.

Foreign portfolio investors have withdrawn roughly $29 billion from Indian equities this year. The rupee has weakened to 95.27 per dollar. The current account deficit has widened as import costs have surged.

The bond tax exemption is part of a coordinated response by the government and the Reserve Bank of India to reverse the capital outflow. The RBI, in its June monetary policy review, expanded the universe of bonds available under FAR to include all new issuances of 15-year, 30-year and 40-year tenor securities — opening up the long end of the yield curve to foreign buyers for the first time.

An SBI Economic Research Department report estimated that the combined measures could attract $55-65 billion in inflows during the current fiscal year, stabilise the rupee, and push India's balance of payments into surplus.

## The Global Index Prize

The bigger game is global bond index inclusion. India has been lobbying for years to be added to major global bond benchmarks — indices that passive funds tracking hundreds of billions of dollars are obligated to follow.

The tax exemption removes one of the last significant barriers to inclusion. Foreign investors had long complained that India's withholding tax on bond income — previously as high as 20 per cent for some categories — made the market uncompetitive relative to peers like Indonesia and Brazil that offer tax-free access.

The exemption is retroactive to April 1, 2025, sending a signal that India is serious about permanence rather than offering a temporary sweetener.

If India is added to the JPMorgan Government Bond Index-Emerging Markets or the Bloomberg Global Aggregate Index, analysts estimate it could trigger $20-30 billion in automatic inflows from passive funds alone — dwarfing the current trickle.

## What It Means for NRIs

The package includes direct benefits for non-resident Indians. The RBI's concessional forex swap facility lowers the cost for banks to raise foreign currency deposits, making NRI deposit schemes more attractive. Private bank stocks have rallied on the back of these measures, with the Nifty Private Bank index rising for two consecutive sessions.

For NRIs with investments in Indian fixed income, the falling yields mean higher prices on existing bond holdings. For those considering fresh allocations, the window may be narrowing — if global index inclusion materialises, the flood of passive money could push yields lower still, compressing returns for latecomers.

More broadly, the measures represent a shift in India's approach to foreign capital. For years, New Delhi maintained a cautious stance, imposing taxes and limits that kept foreign participation in the debt market well below peers. The Iran-driven crisis has forced a rethink, and the results so far suggest the market was waiting for exactly this kind of signal.

## What to Watch

The sustainability of the inflows will depend on two factors: whether the tax exemption survives the next Union Budget (the retroactive application suggests it will) and whether a ceasefire in the Iran conflict reduces the urgency. If oil prices fall sharply on a peace deal, the pressure that prompted these measures could ease — but the structural benefits of a more open bond market would remain.

For now, the money is voting with its feet. A billion dollars in three days is a start. The question is whether India can turn a crisis response into a permanent advantage.""",
        "image_search": {
            "topic_queries": ["Reserve Bank of India building Mumbai", "Indian government bonds finance", "RBI monetary policy"],
            "pexels_query": "India financial district stock exchange",
            "image_caption": "The Reserve Bank of India headquarters in Mumbai",
            "person_name": None
        }
    }
]

# ── Main execution ──

print("=" * 60)
print(f"News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print("=" * 60)

results = []
for i, art in enumerate(ARTICLES):
    print(f"\n{'─' * 40}")
    print(f"Article {i+1}: {art['headline'][:60]}...")
    print(f"{'─' * 40}")

    # Source image
    img_cfg = art.pop("image_search")
    print("  🔍 Sourcing image...")
    img_url, img_attr = source_image(
        slug=art["slug"],
        person_name=img_cfg.get("person_name"),
        topic_queries=img_cfg.get("topic_queries"),
        pexels_query=img_cfg.get("pexels_query")
    )

    if img_url:
        art["image_url"] = img_url
        art["image_caption"] = img_cfg["image_caption"]
        art["image_attribution"] = img_attr
    else:
        print("  ⚠ No image — inserting without hero image")

    # Insert
    print("  📝 Inserting article...")
    art_id = insert_article(art)
    results.append({"slug": art["slug"], "id": art_id, "has_image": bool(img_url)})
    time.sleep(1)

print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
for r in results:
    status = "✓" if r["id"] else "✗"
    img_status = "🖼" if r["has_image"] else "⚠ no image"
    print(f"  {status} {r['slug']} [{img_status}]")
print(f"\nDone at {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
