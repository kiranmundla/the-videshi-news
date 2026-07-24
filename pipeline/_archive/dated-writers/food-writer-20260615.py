#!/usr/bin/env python3
"""
Food Writer — June 15, 2026
3 food articles for The Videshi
1. Freeze-dried Indian meals startups (DryM, Bowlful) targeting NRIs abroad
2. Sanjeev Kapoor's Yellow Chilli opening first US branch in Santa Clara
3. Tariffs raising Indian grocery prices for diaspora in the US
"""
import os, json, re, requests, subprocess
from datetime import datetime, timezone

# ── Load env ──
for envf in ['~/workspace/.env.supabase', '~/workspace/.env.pexels']:
    with open(os.path.expanduser(envf)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if line.startswith('export '): line = line[7:]
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k] = v.strip('"')

SB_URL = os.environ['SUPABASE_URL']
SB_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
PEXELS_KEY = os.environ['PEXELS_API_KEY']

HEADERS = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def make_slug(headline, max_len=80):
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:max_len].rstrip('-')

def get_existing_headlines():
    resp = requests.get(
        f'{SB_URL}/rest/v1/p2_articles',
        params={'category': 'eq.food', 'order': 'published_at.desc',
                'limit': 25, 'select': 'headline,slug'},
        headers=HEADERS)
    if resp.status_code == 200:
        return [a['headline'].lower() for a in resp.json()]
    print(f"Warning: could not fetch existing: {resp.status_code}")
    return []

def is_duplicate(headline, existing):
    norm = re.sub(r'[^a-z0-9 ]', '', headline.lower()).strip()[:40]
    for ex in existing:
        ex_norm = re.sub(r'[^a-z0-9 ]', '', ex).strip()[:40]
        if norm == ex_norm:
            return True
    return False

def search_wikimedia_commons(query):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {'action': 'query', 'generator': 'search', 'gsrsearch': query,
              'gsrnamespace': '6', 'gsrlimit': '5', 'prop': 'imageinfo',
              'iiprop': 'url|size|mime', 'iiurlwidth': '1200', 'format': 'json'}
    headers = {'User-Agent': 'TheVideshi/1.0 (contact@thevideshi.com)'}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=12)
        if resp.status_code == 200:
            pages = resp.json().get('query', {}).get('pages', {})
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                img_url = ii.get('thumburl') or ii.get('url', '')
                mime = ii.get('mime', ''); size = ii.get('size', 0)
                if 'image' in mime and size > 5000 and 'upload.wikimedia.org' in img_url:
                    return img_url
    except Exception as e:
        print(f"  Commons search failed: {e}")
    return None

def search_wikipedia_image(topic):
    topic_clean = topic.replace(' ', '_')
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic_clean}"
    headers = {'User-Agent': 'TheVideshi/1.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img and 'upload.wikimedia.org' in img:
                return img
    except Exception as e:
        print(f"  Wikipedia image failed for {topic}: {e}")
    return None

def search_pexels(query):
    from urllib.parse import quote_plus
    encoded = quote_plus(query)
    try:
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={encoded}&per_page=5',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for photo in data.get('photos', []):
                img_url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if img_url and 'images.pexels.com' in img_url:
                    print(f"    Pexels found: {img_url[:70]}")
                    return img_url
    except Exception as e:
        print(f"  Pexels failed: {e}")
    return None

def validate_image(url):
    """GET-based validation (HEAD blocked for wikimedia from this env)."""
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']
    for b in banned:
        if b in url:
            print(f"  BANNED source: {b}")
            return False
    try:
        # Use curl GET to dodge wikimedia 429 on python requests
        result = subprocess.run(
            ['curl', '-sS', '-A', 'TheVideshi/1.0 (thevideshi.com)', '-o', '/dev/null',
             '-w', '%{http_code} %{content_type} %{size_download}', '-L', url],
            capture_output=True, text=True, timeout=20)
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]; ctype = parts[1]; size = int(parts[-1])
            print(f"    Validate: {code} {ctype} {size}b")
            if code == '200' and 'image' in ctype and size > 5000:
                return True
    except Exception as e:
        print(f"    Validation failed: {e}")
    return False

def find_image(topics_wiki, topics_commons, topics_pexels):
    for t in topics_wiki:
        print(f"  Wiki: {t}")
        img = search_wikipedia_image(t)
        if img and validate_image(img):
            print("  ✓ Wikipedia")
            return img, "Wikimedia Commons"
    for t in topics_commons:
        print(f"  Commons: {t}")
        img = search_wikimedia_commons(t)
        if img and validate_image(img):
            print("  ✓ Commons")
            return img, "Wikimedia Commons"
    for t in topics_pexels:
        print(f"  Pexels: {t}")
        img = search_pexels(t)
        if img and validate_image(img):
            print("  ✓ Pexels")
            return img, "Pexels"
    return None, None

def publish_article(article, existing):
    headline = article['headline']
    if is_duplicate(headline, existing):
        print(f"  ⚠ SKIP duplicate: {headline}")
        return False
    slug = make_slug(headline)
    now = datetime.now(timezone.utc).isoformat()
    wc = len(article['body'].split())
    payload = {
        'headline': headline,
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': slug,
        'category': 'food',
        'vertical': 'food',
        'status': 'review',
        'published_at': now,
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
        'sources': article.get('sources'),
        'word_count': wc,
        'is_editorial': False
    }
    resp = requests.post(f'{SB_URL}/rest/v1/p2_articles', headers=HEADERS, json=payload)
    if resp.status_code in (200, 201):
        result = resp.json()
        aid = result[0]['id'] if isinstance(result, list) else result.get('id', '?')
        print(f"  ✓ Published: {headline}\n    slug: {slug}  id: {aid}  words: {wc}")
        return True
    print(f"  ✗ Failed: {resp.status_code} - {resp.text[:200]}")
    return False

articles = []

# ─────────────────────────────────────────────────────────────
# ARTICLE 1 — Freeze-dried Indian meals
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 1: Freeze-dried Indian meals")
a1_body = """For generations, the Indian going abroad packed a suitcase that smelled faintly of home: theplas wrapped in foil, jars of homemade pickle, sachets of masala measured out by a mother who did not trust foreign kitchens. A new crop of Indian startups is betting that the next version of that tradition will fit into a lightweight freeze-dried pouch — and travel just as far.

For the 5.4 million-strong Indian diaspora in the United States, and the students and workers who join it every year, the appeal is immediate. Familiar food, dietary compliance, and the reassurance of trust, all rehydrated with hot water in minutes.

## Context & Background

The story that captures the shift is almost comically aspirational. Three school friends — Rahul Jain, Pranit Shah and Monish Agarwal — planned a reunion across the Swiss Alps, with suites in Bürgenstock, Gstaad and St. Moritz that can run from $8,700 to more than $46,000 a night. Yet the biggest question before departure was not flights or hotels. It was food. Rahul, a Jain, worried about meals made without onion, garlic or root vegetables. Pranit, a Gujarati vegetarian, feared the hidden lard, meat stock and gelatin that slip into dishes labelled "vegetarian" abroad.

The answer came not from a travel agent but from an Instagram feed: Sonipat-based DryM Foods and Surat-based Bowlful Foods, part of a generation of brands using freeze-drying to make shelf-stable Indian meals. Unlike the retort-processed ready-to-eat pouches from giants such as MTR, Haldiram's and ITC, freeze-drying removes moisture at sub-zero temperatures, preserving flavour and texture while slashing weight. A bulky curry pouch shrinks to a sachet, shelf-stable for six to nine months with no preservatives.

## Current Developments

The numbers suggest a niche maturing into a category. India's freeze-dried food market, estimated at $109 million in 2024, is projected to nearly triple to $315 million by 2033, while the broader ready-to-eat and frozen segment is expected to cross ₹593 billion.

DryM, founded in 2017 by the mother-daughter duo Mrinalini and Aayushi Jain, has grown from roughly ₹10 lakh in first-year revenue to ₹1.5 crore in FY25 and about ₹3 crore in FY26, with plans to triple this year. International markets — led by students and diaspora consumers in the US, UK and Canada — already contribute around 30 percent of revenue, and the company is aiming for a 50:50 domestic-to-export split within two years as it pushes into Europe and the Middle East.

"The common thread wasn't religion or geography, it was trust," co-founder Aayushi Jain told *businessline*. "What started as a travel use case has evolved into a much broader consumer segment — students, diaspora consumers and institutional channels."

The portfolio has swelled from five products to more than 80 recipes — parathas, biryanis, sambar, lemon rice, upma with coconut chutney, idli-based meals and Jain-friendly variants. Surat's Bowlful has taken a parallel path, focusing on vegetarian, Jain and no-onion-no-garlic meals sold largely through online channels and community referrals.

## Diaspora Impact

What makes this distinctly an NRI story is the distribution model. These brands rarely fight for supermarket shelf space. They reach customers through Instagram reels, Facebook travel groups, WhatsApp communities and word-of-mouth across diaspora networks — the same channels through which a homesick graduate student in Ohio or a new H-1B arrival in New Jersey already lives.

For the strictly observant, the value is not convenience but certainty. A Jain professional in San Jose cannot always verify that a restaurant's "vegetarian" thali was cooked without root vegetables or animal fat. A freeze-dried pouch carries the guarantee onto the plate. For South Indian families abroad, the arrival of shelf-stable sambar and idli meals answers a craving that frozen-aisle naan and butter chicken never quite did.

## What's Next

The opportunity is beginning to extend beyond community-led online sales. Alongside competitors such as Food On Tym, Dryfii and Bombay Tiffin Co., DryM is exploring institutional channels — it has already secured business with IRCTC for premium trains including Vande Bharat, and is evaluating airline catering and travel retail.

If those channels open, the freeze-dried pouch could move from suitcase hack to mainstream pantry staple — the moment a diaspora workaround becomes simply how Indian food travels. "People weren't just looking for convenience," Jain said. "They were looking for food they could trust, wherever they were in the world.\""""

articles.append({
    'headline': "From Lemon Rice to Rajma Chawal: How Freeze-Dried Indian Meals Are Feeding the Diaspora",
    'subheadline': "A new generation of Indian startups is turning the homemade travel hack into a packaged-food category, with NRIs in the US, UK and Canada driving a third of sales.",
    'body': a1_body,
    'sources': [
        "The Hindu BusinessLine — From Lemon rice to Rajma chawal: Why more Indians are carrying freeze-dried meals abroad (June 13, 2026)",
        "DryM Foods company statements via businessline",
        "India freeze-dried food market projections, businessline"
    ],
    'img': dict(
        topics_wiki=["Lemon_rice", "Rajma"],
        topics_commons=["lemon rice South Indian dish", "rajma chawal kidney bean curry rice"],
        topics_pexels=["Indian rice meal bowl home cooked", "Indian vegetarian thali meal"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 2 — Yellow Chilli / Sanjeev Kapoor
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 2: Yellow Chilli Santa Clara")
a2_body = """For NRIs of a certain generation, Sanjeev Kapoor is less a chef than a soundtrack — the voice of *Khana Khazana* drifting through living rooms on weekend afternoons, teaching a country, and its emigrants, how to cook. Now the most recognised Indian chef alive is bringing his restaurant brand to the heart of Silicon Valley.

The Yellow Chilli, the casual-dining concept fronted by Kapoor, is set to open its first U.S. branch in Santa Clara, California — a city where the Indian-American population is among the densest in the country.

## Context & Background

The restaurant is slated to open next summer at Monticello Apartment Homes, a planned community developed by Irvine Co., local operator Yogesh Gupta told *The Mercury News*. The location is no accident. Santa Clara sits at the centre of a Bay Area tech corridor where Indian engineers, founders and their families have built one of the most affluent diaspora communities in America — a population that has long outgrown the strip-mall curry house but still hungers for food that tastes like home.

The Yellow Chilli positions its menu as a "gastronomic tour of India," pairing several of Kapoor's signature dishes with classic comfort foods given a contemporary twist. Highlights include Lalla Mussa Dal — black and green lentils simmered overnight with spices, cream, ghee and butter — and Puran Singh da Tariwala Murgh, a chicken curry inspired by the roadside dhabas along the Ambala-Delhi highway.

## Current Developments

Central to the concept is Kapoor himself, whose name carries a measure of culinary authority and recognition that few independent operators can match. The brand leans on moderate prices and an ambience meant to be polished but casual and family-friendly — a deliberate position between the white-tablecloth fine dining of Michelin-chasing newcomers and the everyday neighbourhood Indian restaurant.

The chain is run by Mumbai-based multiconcept operator and franchisor SK Restaurants, which oversees six other brands. There are roughly 30 Yellow Chilli locations across India, plus five branches in the United Arab Emirates and Oman. Santa Clara marks the brand's first foray into the United States — and a notable bet that the American market is ready for a familiar, mid-priced Indian sit-down brand rather than another experimental tasting menu.

## Diaspora Impact

The Yellow Chilli's arrival lands in the middle of what the industry is calling the year of redefining Indian food in America. London imports like Dishoom, Gymkhana and Kricket are crossing the Atlantic; U.S.-based chefs such as Sujan Sarkar are opening fine-dining rooms in New York and Phoenix; and Indian restaurants are claiming James Beard nominations and Michelin stars across multiple cities.

But most of that energy has concentrated at the top of the market. The Yellow Chilli is aiming at a different and arguably larger appetite — the weeknight family dinner, the casual gathering of friends, the diner who wants Lalla Mussa Dal done properly without a reservation booked weeks out. For Bay Area families, the draw is partly nostalgia: a brand many ate at in Mumbai, Delhi or Dubai, now a short drive away.

There is also the comfort of consistency. A celebrity-backed franchise promises a standardised experience — the same dal, the same spice, the same service — in a market where Indian restaurant quality can swing wildly from one establishment to the next.

## What's Next

The Santa Clara opening is targeted for next summer, with no firm date yet announced. If it succeeds, it would give SK Restaurants a template for U.S. expansion in markets with dense Indian populations — the Bay Area, Dallas, New Jersey, the suburbs of Seattle and Atlanta.

For Kapoor, whose empire already spans television, cookbooks and packaged foods, an American restaurant footprint would close a long loop: the chef who taught the diaspora to cook at home, now setting a table for them a few miles from the office."""

articles.append({
    'headline': "Sanjeev Kapoor Comes to Silicon Valley: The Yellow Chilli Plans Its First US Restaurant",
    'subheadline': "India's most famous celebrity chef is bringing his casual-dining brand to Santa Clara next summer, betting on the Bay Area's dense and affluent diaspora.",
    'body': a2_body,
    'sources': [
        "Restaurant Business Online — 3 restaurant concepts set to invade the US (June 2026)",
        "The Mercury News, via Restaurant Business Online — local operator Yogesh Gupta",
        "The Yellow Chilli / SK Restaurants brand information"
    ],
    'img': dict(
        topics_wiki=["Sanjeev_Kapoor"],
        topics_commons=["Sanjeev Kapoor chef"],
        topics_pexels=[])  # named person — Wikipedia/Commons only
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 3 — Tariffs raise Indian grocery prices
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 3: Tariffs and Indian groceries")
a3_body = """The thali is getting pricier in Indian homes across America. As US tariffs on Indian goods climbed toward 50 percent, the cost of the pantry staples that anchor diaspora kitchens — rice, dal, coffee, spices — has jumped sharply, turning a geopolitical dispute into a line item on every NRI grocery receipt.

For the millions of Indians in the United States who measure home in the smell of basmati and the taste of toor dal, the squeeze is personal. And with trade talks still unresolved, relief remains uncertain.

## Context & Background

The pressure traces to Washington's decision to double tariffs on a wide range of Indian products to 50 percent, with the increase taking hold over recent months. While President Trump rolled back duties on more than 200 food products, importers and retailers say the gains will take time to trickle down — old, cheaper inventory has been exhausted, and fresh arrivals are landing at the higher cost.

The result shows up plainly on Indian grocery shelves. In New Jersey, residents describe Cothas Coffee (450g) rising to about $11 from $7, and a 20-pound bag of Sona Masoori rice climbing to $24 from $16. Prices across dal varieties have moved up in similar proportion. "We are witnessing a price escalation of 5 to 15 percent on different grocery items," one shopper, Priya, told *The Hindu BusinessLine*. "The cost of getting shipments from India has gone up by 100 percent."

## Current Developments

The knock-on effects reach beyond the grocery aisle. In California, one diner reported the price of a restaurant dosa jumping to $25 from $20 in a matter of weeks, as Indian restaurants pass rising ingredient costs to the table. Shoppers are adapting where they can — buying rice at Costco, where a comparable bag runs cheaper than at specialty stores, or rationing premium imports.

There is a competitive dimension, too. Neighbouring South Asian countries such as Pakistan, which face relatively lower tariff levels, are eating into the US market share of Indian retail exporters — meaning some diaspora staples may increasingly carry a different origin label even as the recipes stay the same.

The trade picture remains fluid. US Trade Representative Jamieson Greer is due to visit India on June 23–24 for further talks on an interim agreement, with New Delhi seeking preferential tariff access for its exports. Indian trade officials say discussions are aimed at "giving final touches" to an interim deal, while pressing for clarity on proposed new tariffs. Trade is also expected to feature in talks between Trump and Prime Minister Modi on the sidelines of this week's summit in France, though a final deal is not expected there.

## Diaspora Impact

For NRI families, the tariff squeeze is a reminder of how tightly diaspora life is bound to the supply chain from India. The weekly run to the Indian grocery store is not just shopping — it is the maintenance of identity, the act of keeping a kitchen recognisably Indian thousands of miles from home. When a bag of Sona Masoori jumps 50 percent, the cost is measured in more than dollars.

Some families are turning to alternatives: domestic rice brands, bulk-buying at warehouse clubs, or substituting ingredients sourced from countries facing lower duties. Others are simply absorbing the cost, unwilling to compromise on the specific varieties — a particular dal, a regional coffee, a brand of pickle — that carry the memory of a specific home.

The strain also lands on Indian-American grocers and restaurateurs, who must decide how much of the increase to pass on to a price-sensitive community and how much to absorb to keep loyal customers.

## What's Next

Much hinges on the June 23–24 trade talks and the broader push toward an interim US-India agreement. A deal that lowers duties on food products would ease the pressure, though the relief would still take weeks to reach store shelves as cheaper inventory works its way through the system.

Until then, the diaspora pantry stays expensive — and the weekly grocery trip remains a quiet barometer of a trade relationship that two governments call "75 years overdue" for a reset."""

articles.append({
    'headline': "The Pricier Thali: How US-India Tariffs Are Squeezing the Diaspora Grocery Cart",
    'subheadline': "Rice, dal and coffee have jumped 5 to 15 percent on Indian grocery shelves as tariffs bite, with relief hinging on US-India trade talks later this month.",
    'body': a3_body,
    'sources': [
        "The Hindu BusinessLine — Tariffs turn the thali pricier at Indian homes in the US",
        "The Hindu BusinessLine — Tariffs take a toll on desi comfort food of Indian diaspora in the US",
        "Reuters — India's May trade gap narrows; US trade talks in focus (June 2026)"
    ],
    'img': dict(
        topics_wiki=["Toor_dal", "Sona_Masoori"],
        topics_commons=["Indian grocery store lentils dal", "basmati rice sack grocery"],
        topics_pexels=["Indian grocery store spices lentils", "lentils dal pulses bowls"])
})

# ── Source images ──
for i, art in enumerate(articles, 1):
    print(f"\n🖼  Image for Article {i}...")
    img = art.pop('img')
    url, attr = find_image(**img)
    if url:
        art['image_url'] = url
        art['image_attribution'] = attr
    else:
        art['image_url'] = None
        art['image_attribution'] = None
        print("  ⚠ No image found")

# Captions (set after image found)
caps = [
    "A bowl of South Indian rice, the kind of comfort meal now sold freeze-dried to the diaspora",
    "Celebrity chef Sanjeev Kapoor, whose Yellow Chilli brand is heading to Santa Clara",
    "Lentils and rice on an Indian grocery shelf, staples hit hardest by rising tariffs"
]
for art, cap in zip(articles, caps):
    if art.get('image_url'):
        art['image_caption'] = cap

# ── Publish ──
print("\n" + "="*60 + "\nPUBLISHING\n" + "="*60)
existing = get_existing_headlines()
print(f"{len(existing)} existing food articles for dedup")
published = 0
for i, art in enumerate(articles, 1):
    print(f"\n--- Article {i} ---")
    print(f"  Headline: {art['headline']}  ({len(art['headline'])} chars)")
    print(f"  Words: {len(art['body'].split())}")
    print(f"  Image: {str(art.get('image_url'))[:70]}")
    if publish_article(art, existing):
        published += 1
        existing.append(art['headline'].lower())

print(f"\n{'='*60}\nDONE — published {published}/{len(articles)}\n{'='*60}")
