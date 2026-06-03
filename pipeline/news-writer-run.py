#!/usr/bin/env python3
"""
The Videshi News Writer — News Category
Generates articles for the 'news' category.
Run: python3 news-writer-run.py
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# Load env
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

# ─── Image helpers ───

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
    """Fetch image from Pexels using curl (urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    import subprocess, urllib.parse
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            encoded_q = urllib.parse.quote(q)
            result = subprocess.run(
                ['curl', '-sS', f'https://api.pexels.com/v1/search?query={encoded_q}&per_page=5',
                 '-H', f'Authorization: {PEXELS_KEY}'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    # Validate
                    head = requests.head(url, timeout=10)
                    ct = head.headers.get('Content-Type', '')
                    cl = int(head.headers.get('Content-Length', '0'))
                    if 'image' in ct and cl > 5000:
                        print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                        return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_to_supabase_storage(image_url, filename):
    """Download image and upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, timeout=20, headers={"User-Agent": "TheVideshi/1.0"})
        if r.status_code != 200 or len(r.content) < 5000:
            print(f"  ⚠ Image download failed or too small: {r.status_code}, {len(r.content)} bytes")
            return None
        
        content_type = r.headers.get('Content-Type', 'image/jpeg')
        if 'image' not in content_type:
            content_type = 'image/jpeg'
        
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        up = requests.post(
            upload_url,
            headers={
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': content_type,
                'x-upsert': 'true'
            },
            data=r.content,
            timeout=30
        )
        if up.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {up.status_code} {up.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return None

def source_image(article):
    """Source an image for an article following the hierarchy."""
    slug = article['slug']
    person = article.get('primary_person')
    
    # 1. Try Wikipedia for person articles
    if person:
        wiki_url = fetch_wikipedia_person_image(person)
        if wiki_url:
            filename = f"{slug}.jpg"
            final = upload_to_supabase_storage(wiki_url, filename)
            if final:
                return final, "Wikimedia Commons"
    
    # 2. Try Pexels with specific terms
    pexels_query = article.get('image_search_query')
    pexels_fallback = article.get('image_search_fallback')
    if pexels_query:
        pexels_url = fetch_pexels_image(pexels_query, pexels_fallback)
        if pexels_url:
            # Pexels URLs are permanent, can hotlink
            return pexels_url, "Pexels"
    
    return None, None

# ─── Article insertion ───

def insert_article(article):
    """Insert article into Supabase."""
    art_id = str(uuid.uuid4())
    
    # Source image
    img_url, img_attr = source_image(article)
    
    payload = {
        'id': art_id,
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': article['slug'],
        'category': 'news',
        'vertical': 'news',
        'status': 'published',
        'published_at': datetime.now(timezone.utc).isoformat(),
        'sources': json.dumps(article['sources']),
        'is_editorial': False,
        'image_url': img_url,
        'image_attribution': img_attr,
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    
    if r.status_code in (200, 201):
        print(f"  ✓ Published: {article['headline'][:60]}...")
        return art_id
    else:
        print(f"  ✗ Failed to insert: {r.status_code} {r.text[:300]}")
        return None


# ─── Articles ───

ARTICLES = [
    {
        "headline": "Zee Just Landed the FIFA World Cup. India's Biggest Sports Broadcaster Didn't Even Try.",
        "subheadline": "Zee Entertainment secures 39 FIFA events through 2034, including two World Cups, after JioStar's $20 million bid was rejected. The tournament kicks off on June 11.",
        "slug": "zee-entertainment-fifa-world-cup-2026-broadcast-rights-india-unite8-sports-20260603",
        "primary_person": None,
        "image_search_query": "FIFA World Cup football stadium",
        "image_search_fallback": "soccer football world cup",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "BestMediaInfo", "url": "https://www.bestmediainfo.com"},
            {"name": "Livemint", "url": "https://www.livemint.com"}
        ],
        "body": """The 2026 FIFA World Cup starts on June 11, and Indian football fans now know where to find it. Zee Entertainment announced on Monday that it has secured the broadcast rights for the tournament — along with 38 other FIFA events stretching through 2034 — in a deal that reshapes the country's sports media landscape.

The agreement ends months of uncertainty over whether Indian audiences would have access to the world's most-watched sporting event. FIFA had been locked in negotiations with multiple Indian broadcasters, but the talks kept falling through.

## JioStar walked away. Zee walked in.

JioStar, the Reliance-Disney joint venture that dominates Indian sports broadcasting with IPL, English Premier League, and Champions League rights, had offered approximately $20 million for the India package. FIFA rejected it. Sony, which broadcast the 2014 and 2018 tournaments, held discussions but did not submit a formal bid.

FIFA had originally sought about $100 million for a package covering the 2026 and 2030 World Cups. It later slashed the asking price to roughly $60 million. The final terms with Zee were not disclosed, but the deal clearly came at a price point that the market leader was not willing to match.

## Unite8 Sports: Zee's new play

The deal accelerates Zee's push into sports broadcasting through its new Unite8 Sports brand. The company has announced four dedicated channels — Unite8 Sports 1 and Unite8 Sports 1 HD in Hindi, alongside Unite8 Sports 2 and Unite8 Sports 2 HD in English — with distribution deals already underway. Airtel is scheduled to carry the channels from June 4.

The FIFA package includes the 2026 and 2030 men's World Cups, the 2027 Women's World Cup, multiple age-group tournaments across both genders, the FIFA Futsal World Cup, and the FIFA Intercontinental Cup. Zee will also air docu-series covering grassroots football and the cultural dimensions of participating nations.

## What the diaspora should know

For Indian fans in the United States, the World Cup's proximity makes this one of the most accessible editions ever. The tournament will be held across venues in the US, Canada, and Mexico, with most matches in American time zones. For those with friends and family back home, the question of whether they could watch together just got answered.

Zee's stock jumped roughly 7% on the announcement, reflecting investor enthusiasm for a deal that significantly expands the company's sports portfolio. But the real test comes on June 11 — whether Zee can build a compelling broadcast product around the world's biggest football event in a market where cricket has long dominated the conversation.

## The bigger picture

India is the world's most populous country and arguably FIFA's last major untapped broadcast market. That a deal this significant came down to the wire — just 10 days before kickoff — says less about India's appetite for football and more about the hardball economics of sports rights in a market where cricket commands 90% of sports viewership revenue.

For Zee, this is a bet that football's audience in India is ready to grow. For FIFA, it is an acknowledgement that the Indian market required flexibility on price. For fans, it is simply the answer they needed: yes, you can watch the World Cup."""
    },
    {
        "headline": "India Threatens to Roll Back Scotch Whisky Tariff Cuts Unless Britain Backs Down on Steel",
        "subheadline": "New Delhi signals it may withdraw concessions offered under the India-UK free trade deal as both sides meet to resolve a dispute over steel import quotas and carbon border levies.",
        "slug": "india-uk-fta-scotch-whisky-steel-tariff-dispute-goyal-kyle-june-2026-20260603",
        "primary_person": None,
        "image_search_query": "scotch whisky bottles trade",
        "image_search_fallback": "international trade deal negotiation",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com"}
        ],
        "body": """India's landmark free trade agreement with the United Kingdom — signed in May 2025 and expected to reshape bilateral commerce by $34 billion over 15 years — is running into trouble before it has even taken effect. The problem is steel, and the weapon India is reaching for is whisky.

An Indian trade official said on Monday that New Delhi could withdraw tariff concessions it offered Britain on products including Scotch whisky if London does not address concerns over new steel safeguard measures. "So now the ball is in their court," the official told reporters. "If they do not leverage their free trade agreement, we can always reconsider the concessions we offered."

## The steel trigger

From July 1, 2026, Britain will slash tariff-free quotas on steel imports by 60% and nearly double duties on shipments that exceed the reduced quota to 50%. The measures are designed to protect Britain's domestic steel industry, but they directly threaten Indian exporters who shipped roughly $900 million worth of iron and steel to the UK in the last fiscal year.

India is not alone in its objections. Brazil, Turkey, Japan, South Korea, Switzerland, and Australia have all raised concerns at the World Trade Organization over Britain's new restrictions.

## Whisky as leverage

Under the Comprehensive Economic and Trade Agreement (CETA), India had agreed to cut tariffs on Scotch whisky from 150% to 75% immediately, with a further reduction to 40% over 10 years. That was one of the deal's headline concessions — a symbolic market opening for one of Britain's most iconic exports.

Now India is threatening to take it back, characterising any rollback not as retaliation but as "rebalancing" — a recalibration of a deal whose terms, New Delhi argues, have been undercut by Britain's unilateral actions on steel.

## High-level talks in New Delhi

Britain's Trade Secretary Peter Kyle arrived in India on Tuesday for discussions with Commerce Minister Piyush Goyal. India's Commerce Secretary Rajesh Agarwal separately met with UK Permanent Secretary Amanda Brooks to work through what officials diplomatically called "sticking points" delaying the FTA's implementation.

A second concern looms behind the steel dispute: Britain's Carbon Border Adjustment Mechanism (CBAM), set to take effect in 2027. Under CBAM, carbon levies would apply to imports of steel, aluminium, and fertilisers — products in which India is a significant exporter. Indian officials want clarity on how CBAM will interact with the FTA before committing to full implementation.

## Why the diaspora should pay attention

The India-UK trade corridor matters enormously to the 1.6 million-strong Indian diaspora in Britain and the substantial British business community in India. The FTA was projected to boost bilateral trade by £25.5 billion by 2040, expanding access for Indian textiles, IT services, and pharmaceuticals into the UK while opening India's market to British luxury goods, financial services, and automobiles.

A breakdown in the FTA's implementation would not just be a trade story — it would be a signal that even concluded deals between allied democracies can unravel when domestic industrial politics collide with international commitments. For NRIs in the UK who were expecting cheaper whisky and better trade terms, the answer is: not yet."""
    },
    {
        "headline": "Indian Companies Had Their Best Quarter in Two Years. The Next One Could Undo It All.",
        "subheadline": "Nifty 50 profits grew 6.6% in Q4 FY26, beating estimates by a wide margin. But eight quarters of single-digit growth, a record foreign fund exit, and the Iran war's energy shock now cloud the outlook.",
        "slug": "india-q4-fy26-corporate-earnings-beat-iran-war-outlook-fpi-exit-20260603",
        "primary_person": None,
        "image_search_query": "Indian stock market Bombay Stock Exchange trading floor",
        "image_search_fallback": "stock market trading finance India",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Kotak Institutional Equities", "url": "https://www.kotaksecurities.com"},
            {"name": "Motilal Oswal Financial Services", "url": "https://www.motilaloswal.com"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"}
        ],
        "body": """India Inc just turned in its strongest quarterly performance since early 2024 — and almost nobody is celebrating. The numbers for January to March 2026 comfortably beat expectations across every major market segment, but the celebration lasts only as long as it takes to look at what comes next.

Nifty 50 companies posted net profit growth of 6.6% year-on-year in Q4 FY26, according to Kotak Institutional Equities. That does not sound dramatic until you consider that analysts had pencilled in just 2.2% growth. The broader universe told an even better story: Motilal Oswal's coverage of 359 companies showed 16% profit growth, nearly double its 8% estimate. Mid-cap earnings grew about 35%, small-caps advanced nearly 20%.

## Who delivered

Banks and financial companies drove the largest share of the earnings beat. Stable asset quality and improving credit growth helped lenders at a time when many expected the credit cycle to show strain. Metal producers benefited from rising global prices — a direct consequence of the supply disruptions the Iran war has caused. Oil marketing companies enjoyed favourable margins.

Automobile and telecom companies improved during the quarter. IT firms, however, stayed flat, as mounting concerns over AI-driven disruption and client spending caution kept revenue growth tepid. Pharmaceutical companies struggled with weakness in the US generics market. Cement, consumer staples, and durable goods makers began showing pressure from rising raw material and freight costs — an early preview of what the Iran war's energy shock will do to margins.

## Eight quarters and counting

The headline number obscures a troubling pattern. This was the eighth consecutive quarter of single-digit earnings growth for India's top-50 companies. The broader economy has been expanding, consumption tax cuts boosted demand, and the Reserve Bank of India cut rates by 125 basis points through last year. Yet corporate earnings have stubbornly refused to accelerate into double digits.

The reason is structural. India's largest companies are no longer growing fast enough to absorb rising input costs, while mid-caps and small-caps — which have been the real earnings story for two years — remain too small a share of index weight to move the headline numbers.

## The Iran shadow

Three months into the Iran war, the energy shock is now rippling across the economy. Brent crude has risen 50% since the conflict began. Base chemical prices have surged more than 60% — the fastest rate ever recorded. Goldman Sachs has labelled India the most vulnerable major economy, estimating a potential 3.6% GDP hit.

"Q4 may have marked a temporary relief, but does not yet signal improved momentum for quarters to come," Bernstein said in a note. Kotak was blunter: "A prolonged crisis could result in a deeper negative impact on both the economy and earnings."

Consensus FY27 earnings estimates have already been revised lower. Nomura's Saion Mukherjee noted that the downgrades reflect growing concerns over oil, commodities, and the broader fallout from the Iran conflict.

## The foreign exit

Foreign portfolio investors sold a record $2.22 billion of Indian shares in a single session last Friday as MSCI's May rebalancing took effect. Over the past four trading days, the Sensex has fallen 2.9% and the Nifty 2.7%. India has slipped to seventh in global market-cap rankings, overtaken by South Korea's AI-fuelled chip boom.

The interest rate outlook adds another layer of complexity. The RBI meets this week for what Reuters calls one of the toughest rate calls in recent memory. Nearly 80% of economists expect the central bank to hold at 5.25%, but the swap market is pricing in nearly 100 basis points of tightening over the next 12 months.

## What the diaspora should watch

For NRIs with Indian market exposure — whether through direct equity holdings, mutual funds, or property-linked investments — the next quarter will be the real test. The Q4 beat was earned on last year's momentum. The question is whether Indian companies can hold margins and growth targets as crude stays above $90, the rupee weakens, the monsoon disappoints, and foreign capital continues to exit. The earnings story that just delivered a pleasant surprise may not be in a position to repeat it."""
    },
]

# ─── Main ───

if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}\n")
    
    success = 0
    failed = 0
    
    for i, article in enumerate(ARTICLES, 1):
        print(f"\n[{i}/{len(ARTICLES)}] {article['headline'][:60]}...")
        
        # Validate article
        body_words = len(article['body'].split())
        if body_words < 400:
            print(f"  ✗ Body too short: {body_words} words (min 400)")
            failed += 1
            continue
        
        if len(article['headline']) > 200:
            print(f"  ✗ Headline too long: {len(article['headline'])} chars")
            failed += 1
            continue
            
        if len(article['subheadline']) < 15:
            print(f"  ✗ Subheadline too short: {len(article['subheadline'])} chars")
            failed += 1
            continue
        
        art_id = insert_article(article)
        if art_id:
            success += 1
        else:
            failed += 1
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"Done: {success} published, {failed} failed")
    print(f"{'='*60}\n")
