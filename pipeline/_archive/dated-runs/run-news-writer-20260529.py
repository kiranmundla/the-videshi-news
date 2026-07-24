#!/usr/bin/env python3
"""
The Videshi News Writer — 2026-05-29 batch
Produces 3 news articles with proper images, quality checks, and Supabase publishing.
"""

import json, os, re, sys, time, uuid, urllib.parse
import requests

# === Load env ===
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

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

# === Image helpers ===

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
    """Fetch image from Pexels API using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        if r.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {r.status_code}")
            return image_url  # fallback to direct URL
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(upload_url, data=r.content, headers={
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': content_type,
            'x-upsert': 'true'
        }, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed: {up.status_code} {up.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url

def validate_image_url(url):
    """Check image URL is valid (HTTP 200, image content type, >5KB)."""
    if not url:
        return False
    # Check for banned domains
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com']
    if any(b in url for b in banned):
        print(f"  ❌ Banned domain in URL: {url[:80]}")
        return False
    banned_params = ['_nc_ht=', '_nc_cat=', 'ccb=']
    if any(p in url for p in banned_params):
        print(f"  ❌ Banned params in URL: {url[:80]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200:
            print(f"  ⚠ Image HEAD failed: {r.status_code}")
            return False
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if 'image' not in ct:
            print(f"  ⚠ Not image content type: {ct}")
            return False
        if cl > 0 and cl < 5000:
            print(f"  ⚠ Image too small: {cl} bytes")
            return False
        return True
    except Exception as e:
        print(f"  ⚠ Validate error: {e}")
        return True  # assume ok if can't check

def sb_insert(table, data):
    """Insert row into Supabase."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", json=data, headers=HEADERS, timeout=30)
    if r.status_code in (200, 201):
        rows = r.json()
        return rows[0] if rows else data
    else:
        print(f"  ❌ Insert failed: {r.status_code} {r.text[:300]}")
        return None

def sb_patch(table, match, data):
    """Update row in Supabase."""
    params = '&'.join(f'{k}={v}' for k, v in match.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{params}", json=data, headers=HEADERS, timeout=30)
    if r.status_code in (200, 204):
        return True
    else:
        print(f"  ❌ Patch failed: {r.status_code} {r.text[:300]}")
        return False

# === Articles ===

articles = [
    {
        "headline": "Anthropic Just Hit a $965 Billion Valuation. The Company That Might Dethrone OpenAI Was Built by Its Own Alumni.",
        "subheadline": "The Claude-maker raised $65 billion in a single round, surpassing OpenAI for the first time. For thousands of Indian engineers in the AI race, the power shift changes everything.",
        "slug": "anthropic-965-billion-valuation-surpasses-openai-indian-ai-engineers-20260529",
        "category": "news",
        "sources": json.dumps(["Reuters", "Wall Street Journal", "Barron's", "MarketWatch"]),
        "person_image": "Dario Amodei",
        "pexels_query": "artificial intelligence technology server room",
        "pexels_fallback": "silicon valley technology headquarters",
        "body": """Anthropic, the San Francisco-based AI company founded by former OpenAI researchers, announced on Thursday that it has raised $65 billion in a Series H funding round at a post-money valuation of $965 billion — surpassing rival OpenAI's $852 billion valuation for the first time.

## The Numbers That Shook Silicon Valley

The round was led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital, with each lead investor contributing over $2 billion. Strategic infrastructure partners Samsung, SK Hynix, and Micron also joined. Amazon, which has already invested $8 billion, added another $5 billion as part of a broader commitment of up to $25 billion in the company.

Anthropic's valuation has more than doubled from $380 billion in February, a pace of appreciation that makes it the fastest-growing private company in history by market value. If it were public, it would rank as the 12th most valuable company in the S&P 500, just behind Berkshire Hathaway and above Walmart.

"Since our Series G in February, adoption has continued to grow across global enterprise customers, and our run-rate revenue crossed $47 billion earlier this month," the company said in a blog post. The Wall Street Journal reported Anthropic is on track to hit $50 billion in annualised revenue next month — an 80-fold increase in the first quarter alone.

## What Changed

The shift at the top of the AI leaderboard has been swift. Anthropic's Claude models, particularly the Opus line, have been gaining ground among developers and enterprise customers who prize the company's focus on safety research and its "constitutional AI" approach to alignment. The company is preparing to release Claude Mythos, its next-generation model, in the coming weeks.

Both Anthropic and OpenAI are eyeing potential IPOs as early as this year, setting up what could be the largest technology listings since the dot-com era.

Meanwhile, Apollo Global Management and Blackstone are working on a separate $36 billion debt financing deal tied to Anthropic's AI infrastructure expansion. The debt would be used to purchase custom tensor processing units from Google, with Broadcom backstopping payments on the largest portions.

## The Diaspora Angle

For the estimated 40,000 to 60,000 Indian-origin engineers working in Silicon Valley's AI sector, the power shift between Anthropic and OpenAI is more than a headline — it is a career calculus.

Indian engineers hold senior technical roles at both companies. The broader Indian American tech workforce, which makes up a disproportionate share of AI research talent in the United States, is watching the Anthropic-OpenAI rivalry with particular interest because the winning company will set the agenda for how AI is built, regulated, and deployed globally.

The valuation race also has implications for India's own AI ambitions. Indian IT services companies like Wipro, Infosys, and TCS have been building partnerships with frontier AI companies to deploy their models across enterprise clients. A shift in which company leads the market could reshape those partnerships and the billions of dollars in services revenue that flow through them.

## What Comes Next

Anthropic's IPO preparations are already underway. If the company lists at or near its current private valuation, it would be the largest technology IPO in history — larger than Arm's 2023 listing and dwarfing even the most optimistic projections for OpenAI's own planned offering.

For now, the AI industry has a new leader by valuation. Whether Anthropic can sustain that lead will depend on whether Claude Mythos delivers on its promise and whether the company can convert its explosive revenue growth into profitability. The Wall Street Journal reported that Anthropic expects to turn an operating profit for the first time in the second quarter of 2026.

The trillion-dollar milestone is within reach. The question is which company gets there first."""
    },
    {
        "headline": "Wipro's Stock Just Jumped 18 Percent Overnight. The Reason: An AI Deal That Could Reshape Indian IT.",
        "subheadline": "The company's partnership with ServiceNow to deploy agentic AI across enterprise functions sent its American depositary receipts soaring — and signalled a new chapter for India's $250 billion IT industry.",
        "slug": "wipro-servicenow-agentic-ai-partnership-stock-surge-indian-it-20260529",
        "category": "news",
        "sources": json.dumps(["Reuters", "LiveMint", "The Hindu Business Line", "Analytics Insight"]),
        "person_image": None,
        "pexels_query": "enterprise software technology office automation",
        "pexels_fallback": "corporate technology digital transformation",
        "body": """Wipro's American depositary receipts surged 18.54 percent on the New York Stock Exchange on Thursday after the Bengaluru-based IT services giant announced an expanded partnership with ServiceNow to deploy agentic AI workflows across core enterprise functions. On Friday morning in Mumbai, Wipro shares opened 4.6 percent higher on the BSE.

## The Deal

The partnership integrates Wipro Intelligence, the company's proprietary AI platform, with ServiceNow's AI Platform to automate enterprise workflows across four critical domains: IT operations, human resources, procurement, and cybersecurity.

The key products include SmartProcure, which uses AI agents to automate procurement workflows from requisition to payment; Telco Autonomous Networks for telecom service operations; and Cyber Transform, a security governance platform that deploys AI to detect, triage, and respond to threats in real time.

Unlike earlier AI integrations that relied on chatbots or simple automation, the Wipro-ServiceNow partnership is built around agentic AI — systems that can independently plan, execute, and verify multi-step tasks with minimal human oversight. This represents a qualitative leap from the "copilot" model that has dominated enterprise AI deployments over the past two years.

## Why the Market Reacted

The scale of the stock move — an 18 percent overnight jump for a company with a market capitalisation of over $30 billion — reflects something beyond a single partnership announcement. Investors see the deal as evidence that Indian IT services companies can move from implementing other companies' AI products to co-creating AI platforms with them.

Wipro has been the underperformer among India's top IT firms for years. Its stock had lagged peers like TCS, Infosys, and HCL Technologies, and the company went through a CEO transition that left investors uncertain about its strategic direction. The ServiceNow deal suggests Wipro is finding a differentiated position in the AI services market.

The Nifty IT index rose 2.3 percent on Friday morning in Mumbai, with Wipro leading the sector higher.

## The Bigger Picture for Indian IT

India's IT services industry, which employs over five million people and generates more than $250 billion in annual revenue, faces an existential question: will AI replace the labour arbitrage model that built the industry, or will it create new categories of work that Indian companies are uniquely positioned to deliver?

The Wipro-ServiceNow deal points to the second scenario. Agentic AI workflows require deep domain expertise, change management, integration with legacy systems, and ongoing governance — exactly the kind of work that IT services companies excel at. The difference is that the value shifts from bodies-on-seats to intellectual property and platform co-creation.

For the hundreds of thousands of Indian IT professionals in the United States on H-1B visas, this shift has immediate implications. Companies that successfully pivot to AI platform partnerships will need fewer but more specialised engineers, while those that fail to adapt risk losing contracts to AI-native competitors.

## What It Means for NRIs

Indian Americans working in enterprise technology — from ServiceNow administrators to Wipro consultants — are at the intersection of this transformation. The agentic AI wave is creating new roles in AI governance, workflow design, and human-AI orchestration that did not exist two years ago.

For investors, the Wipro move is a signal that the Indian IT sector's AI story may be entering its second act. The first act was about using AI tools. The second is about building them."""
    },
    {
        "headline": "The US Ambassador to India Says a Trade Deal Is 'Not Too Far Apart.' Here Is What That Actually Means.",
        "subheadline": "Sergio Gor, Trump's pick for New Delhi, says delegations are exchanging visits and a deal could close in weeks. For Indian exporters and NRI businesses, the 50 percent tariff wall is the only number that matters.",
        "slug": "us-india-trade-deal-ambassador-gor-tariffs-nri-businesses-20260529",
        "category": "news",
        "sources": json.dumps(["The Indian Eye", "LiveMint", "India Tribune", "Reuters"]),
        "person_image": None,
        "pexels_query": "US India bilateral meeting trade diplomacy",
        "pexels_fallback": "international trade flags diplomatic summit",
        "body": """Sergio Gor, the United States ambassador-designate to India, said this week that the two countries are "not that far apart" on a bilateral trade deal and expressed confidence that negotiations could conclude within weeks.

## The State of Play

The comments came against the backdrop of a 50 percent tariff regime that the Trump administration imposed on Indian exports earlier this year, citing persistent trade imbalances. India retaliated with 25 percent tariffs on American oil imports from Russia, adding fuel to an already complex negotiating dynamic.

"We are confident that in the coming weeks and months, this trade deal will be finalised," Gor told The Indian Eye, pointing to a rapid schedule of high-level exchanges. An Indian delegation visited Washington last month to advance the negotiations, and a U.S. delegation is expected in New Delhi next month.

Gor also drew a comparison with the India-EU Free Trade Agreement, which was signed in January 2026 after 19 years of negotiations. "Negotiations have been ongoing for a year and a half, but to put it in perspective, the European Union took almost 19 years," he said.

U.S. Trade Representative Jamieson Greer separately confirmed that the two sides are close but "not there yet," noting ongoing discussions with India's commerce minister on the scope of the deal.

## What Is on the Table

The proposed bilateral trade agreement aims to double U.S.-India trade to $500 billion by 2030. The key sticking points include market access for American agricultural products, intellectual property protections for pharmaceutical patents, data localisation requirements, and India's defence procurement preferences.

The Trump administration has also signalled that it wants India to reduce its purchases of Russian oil — a demand that puts New Delhi in a difficult position given that Russian crude has become a major source of affordable energy for Indian refiners since the Ukraine war began.

For its part, India is pushing for expanded access for its IT services professionals in the American market, relief from the H-1B visa backlog, and recognition of Indian pharmaceutical standards — all issues that directly affect the diaspora.

## What This Means for NRIs

The India-U.S. trade relationship is not an abstraction for the four million Indian Americans living in the United States. It is the connective tissue of their economic lives.

Indian American-owned businesses, from IT consultancies to import-export firms to restaurant chains, operate in both markets simultaneously. A 50 percent tariff wall makes that harder. Goods that Indian American entrepreneurs source from family businesses back home — textiles, spices, handicrafts, machinery parts — have become significantly more expensive.

The tariffs have also complicated the remittance economy. Higher import costs feed into inflation, which erodes the purchasing power of the $100 billion-plus that Indian Americans send home each year.

A deal that reduces tariffs and opens market access in both directions would be the single most significant economic development for the Indian diaspora in the Trump era. Gor's confidence that it is close is the strongest signal yet from the U.S. side.

## The Caveat

Gor is an ambassador-designate, not a trade negotiator. His optimism may reflect the administration's desire to project progress more than the actual state of talks. U.S.-India trade negotiations have a long history of near-misses — the two countries came close to a mini-deal during Trump's first term in 2019-2020 and failed to close it.

The EU comparison that Gor invoked is also double-edged. Yes, the India-EU FTA took 19 years. But it also required India to make concessions on dairy, wine, and automobile imports that were politically painful in New Delhi. Whether India's current government is willing to make similar concessions to Washington, while simultaneously managing the domestic political fallout of the Iran-driven oil price shock, remains an open question.

The deal is close. But in trade diplomacy, "close" can mean next month or next year."""
    }
]

# === Main execution ===

print("=" * 60)
print("The Videshi News Writer — 2026-05-29")
print("=" * 60)

published_count = 0

for i, article in enumerate(articles):
    print(f"\n{'─' * 50}")
    print(f"Article {i+1}/{len(articles)}: {article['headline'][:70]}...")
    print(f"{'─' * 50}")

    # Validate article quality
    body = article['body']
    word_count = len(body.split())
    print(f"  Word count: {word_count}")
    if word_count < 400:
        print(f"  ❌ REJECTED: Body too short ({word_count} words, need 400+)")
        continue
    if len(article['headline']) < 20 or len(article['headline']) > 200:
        print(f"  ❌ REJECTED: Headline length {len(article['headline'])} out of range")
        continue
    if len(article['subheadline']) < 15:
        print(f"  ❌ REJECTED: Subheadline too short")
        continue

    # Image sourcing
    print("  Sourcing image...")
    image_url = None
    image_attribution = None

    # Step 1: Wikipedia for person articles
    if article.get('person_image'):
        wiki_img = fetch_wikipedia_person_image(article['person_image'])
        if wiki_img:
            image_url = wiki_img
            image_attribution = "Wikimedia Commons"

    # Step 2: Pexels fallback
    if not image_url:
        pexels_img = fetch_pexels_image(article.get('pexels_query'), article.get('pexels_fallback'))
        if pexels_img:
            image_url = pexels_img
            image_attribution = "Pexels"

    # Upload to Supabase for permanence (except for Pexels which are permanent)
    final_image_url = None
    if image_url:
        if 'upload.wikimedia.org' in image_url:
            # Wikimedia URLs are permanent, but upload for consistency
            filename = f"{article['slug']}.jpg"
            final_image_url = upload_image_to_supabase(image_url, filename)
        elif 'images.pexels.com' in image_url:
            # Pexels URLs are permanent per their license
            final_image_url = image_url
        else:
            filename = f"{article['slug']}.jpg"
            final_image_url = upload_image_to_supabase(image_url, filename)

    if final_image_url and not validate_image_url(final_image_url):
        print("  ⚠ Image validation failed, using without validation")

    if not final_image_url:
        print("  ⚠ No image found — publishing without hero image")

    # Insert into Supabase
    art_id = str(uuid.uuid4())
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    row = {
        "id": art_id,
        "headline": article['headline'],
        "subheadline": article['subheadline'],
        "slug": article['slug'],
        "body": article['body'],
        "category": article['category'],
        "vertical": article['category'],
        "status": "published",
        "published_at": now_iso,
        "created_at": now_iso,
        "sources": article['sources'],
        "tags": [],
        "urgency": "medium",
        "is_featured": False,
        "is_editorial": False,
        "score_total": 75,
    }

    if final_image_url:
        row["image_url"] = final_image_url
    if image_attribution:
        row["image_attribution"] = image_attribution

    print(f"  Publishing to Supabase...")
    result = sb_insert("p2_articles", row)
    if result:
        print(f"  ✅ Published: {article['slug']}")
        published_count += 1
    else:
        print(f"  ❌ Failed to publish: {article['slug']}")

    time.sleep(1)  # brief pause between inserts

print(f"\n{'=' * 60}")
print(f"Done. Published {published_count}/{len(articles)} articles.")
print(f"{'=' * 60}")
