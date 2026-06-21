#!/usr/bin/env python3
"""
Food Writer — June 20, 2026 (evening run)
3 food articles for The Videshi:
1. Patel Brothers / Indian grocery chain expansion across US suburbs
2. Kati Roll Company & NYC Indian street-food brands franchising into NJ
3. Indian tiffin / home-style meal subscription boom in the US
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

def validate_image(url):
    if not url:
        return False
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']
    for b in banned:
        if b in url:
            print(f"  BANNED source: {b}")
            return False
    try:
        result = subprocess.run(
            ['curl', '-sS', '-A', 'TheVideshi/1.0 (thevideshi.com)', '-o', '/dev/null',
             '-w', '%{http_code} %{content_type} %{size_download}', '-L', url],
            capture_output=True, text=True, timeout=25)
        parts = result.stdout.strip().split()
        if len(parts) >= 3:
            code = parts[0]; ctype = parts[1]; size = int(parts[-1])
            print(f"    Validate: {code} {ctype} {size}b")
            if code == '200' and 'image' in ctype and size > 5000:
                return True
    except Exception as e:
        print(f"    Validation failed: {e}")
    return False

def publish_article(article, existing):
    headline = article['headline']
    if is_duplicate(headline, existing):
        print(f"  SKIP duplicate: {headline}")
        return False
    if not validate_image(article.get('image_url')):
        print(f"  IMAGE failed validation, setting null: {headline}")
        article['image_url'] = None
        article['image_attribution'] = None
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
        print(f"  PUBLISHED ({wc}w): {headline}")
        print(f"     slug: {slug}")
        return True
    else:
        print(f"  FAILED {resp.status_code}: {resp.text[:300]}")
        return False


ARTICLES = [
    {
        "headline": "From Baymeadows to Main Street: How Patel Brothers Became the Anchor of Suburban Desi America",
        "subheadline": "As the largest Indian grocery chain crosses 50 stores and pushes into Florida, New Jersey and beyond, the desi supermarket is becoming the new town square for a scattered diaspora.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Perry_Hall_Grocery_Store_Nepalese_%26_Indian_03.jpg/1280px-Perry_Hall_Grocery_Store_Nepalese_%26_Indian_03.jpg",
        "image_caption": "Shelves of South Asian groceries and spices at an Indian and Nepalese grocery store in the United States",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Beacon Journal / Florida Times-Union — Patel Brothers to expand Indian market to St. Johns County (Jan 2026)",
            "Township of East Windsor, NJ — Patel Brothers to open 50th store, May 28 (2026)",
            "WhatNow — Patel Brothers Plans New Indian Market in St. Johns (2026)"
        ],
        "body": """For millions of Indian Americans, the route home runs through a strip-mall parking lot. Past the dry cleaner and the nail salon sits the store that smells of cumin and fresh coriander, where the rice comes in twenty-pound sacks and the frozen aisle holds the parathas your mother would recognize. Increasingly, that store carries one name: Patel Brothers.

In late May, the chain cut the ribbon on its 50th store, in East Windsor, New Jersey, taking over a former Genuardi's supermarket on the Route 130 corridor. It was a milestone dressed as routine — a mayor, a council, twenty new full-time jobs — but it marked something larger. The desi grocery store, once a cramped specialty shop tucked into immigrant enclaves, has become an anchor tenant in suburban America.

## Context & Background

Patel Brothers was founded in 1974 in Chicago by two brothers who imported the spices and staples their community could not find. Half a century later it operates more than 50 stores across the country, partnering with wholesaler Raja Foods to bring rice, lentils, spices and snacks from India, Pakistan and beyond to American shelves. Its mission statement is unabashedly emotional: to "reconnect people with the familiar flavors of India."

That sentiment is the engine behind a national footprint. The chain's expansion mirrors the diaspora's own — following H-1B engineers to tech suburbs, families to good school districts, and retirees to the Sun Belt. Where Indian Americans settle in numbers, a Patel Brothers tends to follow, and where one opens, it signals to the wider neighborhood that a community has arrived to stay.

## Current Developments

The pace of expansion has quickened. In Florida, Patel Brothers is preparing a second Jacksonville-area location in St. Johns County, having purchased 4.25 acres for a 20,000-square-foot store in a retail center still under construction. Company executives say three Florida locations are in the works, with more they cannot yet announce.

The new stores are not the fluorescent-lit warehouses of old. The St. Johns design — the template rolled out over the past four to five years — includes Patel's Fresh Kitchen, an in-house counter selling samosas, breads, pizzas and ready-to-eat meals. Swetal Patel, who oversees day-to-day operations, describes the location as a hub, with a restaurant, a jewelry store and a beauty store planned alongside the grocery. The supermarket, in other words, is becoming a desi mini-mall.

The model reflects a shift in how the chain sees itself. It is no longer competing only with other Indian grocers, but with the prepared-foods sections of Whole Foods and Wegmans, and with the convenience of delivery apps. The Fresh Kitchen counter is a hedge against both, offering the time-pressed second-generation shopper a hot meal that still tastes like home.

## Diaspora Impact

For NRIs, the rise of Patel Brothers and its peers is more than a shopping convenience — it is an erasure of one of immigration's quiet hardships. A generation ago, stocking a desi pantry meant a once-a-month pilgrimage to the nearest big-city enclave, an ice chest in the trunk and careful rationing of curry leaves. Today, in dozens of suburbs, the trip is fifteen minutes each way.

The stores have also become social infrastructure. On weekends, the aisles fill with aunties comparing mango varieties, students stocking up on instant dal, and toddlers angling for a packet of Parle-G. Community flyers paper the entrances: garba nights, tutoring services, temple events. In a diaspora spread thin across exurban America, the grocery store is one of the few places the community reliably gathers in person.

There is an economic ripple, too. Each new store creates jobs, anchors a retail center, and draws other desi businesses — restaurants, salons, sweet shops — into its orbit, knitting together the commercial fabric of a community that might otherwise exist only online.

## What's Next

Patel Brothers' suburban march is unlikely to slow. With construction underway in Florida and a New Jersey cluster expanding around East Windsor, the chain is betting that the next decade of Indian American growth lies not in the established gateways of Edison and Fremont but in the fast-growing exurbs of the South and Southwest.

The bigger question is what the format becomes. As Fresh Kitchen counters expand and the hub model takes hold, the line between grocery store, restaurant and community center is blurring. For a diaspora that has long improvised its sense of place, the desi supermarket — humble, fluorescent, smelling of home — may turn out to be the town square it never knew it was building."""
    },
    {
        "headline": "Kati Rolls Cross the Hudson: How New York's Indian Street Food Is Franchising the American Suburb",
        "subheadline": "The Kati Roll Company's first New Jersey outpost, opening near Jersey City's historic India Square, signals a new phase in which desi street food scales through franchising rather than fine dining.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Making_Kati_Rolls_-_Millennium_Park_-_Central_Kolkata_-_India_%2812268604906%29.jpg/1280px-Making_Kati_Rolls_-_Millennium_Park_-_Central_Kolkata_-_India_%2812268604906%29.jpg",
        "image_caption": "A vendor making kati rolls on a griddle, the Kolkata street snack now spreading across American cities",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "NorthJersey.com — Popular NYC-based Indian restaurant opens first NJ location in July (2026)",
            "RestaurantNews.com — Chaatwala Launches Franchise Program to Bring Indian Street Food to the U.S.",
            "OpenTable — The Chaat Explainer: 6 South Asian Street Snacks and Where to Try Them"
        ],
        "body": """When the Kati Roll Company opens its doors in Jersey City this July, it will be a short walk from India Square — the Newark Avenue stretch where kati rolls and kebabs have been sold for decades. To an outsider it might look like coals-to-Newcastle. To the company, it is a homecoming, and a sign of how India's most democratic food is finally scaling on American soil.

The Jersey City site, a franchise run in partnership with local owner Jay Sorathiya, joins four locations in New York City, two in Texas and two in London. The brand has plans for Hoboken, Metuchen and New Brunswick before year's end. "We do good food, we have been doing it for a while," founder Payal Saha's team told NorthJersey.com, brushing aside the proximity to the city's longtime desi enclave. "I think the customers will be happy."

## Context & Background

The kati roll is Kolkata's gift to the hurried — a paratha wrapped around spiced kebab, egg, onions and a squeeze of lime, eaten standing up on a train platform or street corner. It is street food in the truest sense: cheap, fast, and beloved across class and region. For the Indian diaspora, it is also a portal of memory, the taste of a college canteen or a late-night Park Street craving.

For years, Indian food in America scaled in two directions. At the top, ambitious chefs chased Michelin stars and James Beard nods with regional tasting menus. At the bottom, family-run restaurants served the familiar buffet of butter chicken and naan. The vast, profitable middle — the fast-casual lane that built Chipotle and Cava — sat largely empty for desi cuisine.

That gap is now closing, and street food is leading the charge.

## Current Developments

The Kati Roll Company's franchise push is one of several signs. Chaatwala, a Washington-based chaat concept, has launched a franchise program built explicitly for scale: a self-service setup, disposable tableware, a lean four-person team running a 40-to-50-seat location, and a standardized vegetarian menu that "doesn't need cooking skills or restaurant experience." Its founder, Jai Jaithirth, pitches it as "plug-and-play" — Indian street food engineered for the strip mall.

The data supports the bet. Yelp searches for "Indian food buffet near me" have jumped 459 percent, and interest in Indian street food has shown strong, sustained growth, according to trend analyses. Restaurant groups like Chai Pani — a James Beard winner that built its reputation on pani puri and okra fries rather than white tablecloths — have proven that chaat can anchor a beloved, expandable brand.

What unites these ventures is a recognition that street food travels better than fine dining. It is forgiving of suburban rents, friendly to vegetarians and vegans, and instantly legible to American diners who already understand the taco and the bao. A kati roll needs no explanation; it sells itself in one bite.

## Diaspora Impact

For NRIs, the franchising of street food lands somewhere between delight and unease. On one hand, it means the snacks of a Kolkata evening or a Mumbai monsoon are now a fifteen-minute drive away, in a clean, predictable storefront the kids will actually walk into. The second generation, raised on convenience and brand trust, may finally embrace the foods their parents missed most.

On the other hand, standardization carries a cost. Part of street food's soul is its irreproducibility — the specific char of one vendor's griddle, the secret ratio of one family's chutney. A franchise's promise of "the same authentic flavors, every time" is, by definition, a flattening. The worry, voiced quietly in diaspora kitchens, is that scaling the kati roll might smooth away the very imperfections that made it precious.

Yet placement matters. The Kati Roll Company chose to open beside India Square, not against it — a bet that a rising tide lifts the whole desi commercial corridor rather than draining the original mom-and-pop shops.

## What's Next

The fast-casual desi wave is only beginning. As franchise models prove out across New Jersey, Texas and the Mid-Atlantic, expect national investors — the same ones who scaled Mediterranean and Korean concepts — to start writing checks. The next few years will test whether Indian street food can become a category, the way poke and shawarma did, without losing the corner-stall charm that made it worth scaling in the first place.

For a diaspora that has spent decades explaining its food, the arrival of the standardized, suburban kati roll is a strange kind of arrival: proof that the snack no longer needs explaining at all."""
    },
    {
        "headline": "Ghar Ka Khana, Delivered: The Quiet Boom in America's Indian Tiffin Economy",
        "subheadline": "From Bay Area home kitchens to Toronto marketplaces, subscription tiffin services are feeding a diaspora that craves the one thing restaurants rarely offer — the taste of home cooking.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/%279%27_A_Thali%2C_meal_served_in_India.jpg/1280px-%279%27_A_Thali%2C_meal_served_in_India.jpg",
        "image_caption": "A traditional Indian thali of dal, vegetables, rice and bread, the model for home-style tiffin meals",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Global Indian — Sonu Kilam's mission to bring Ayurvedic Indian meals to the diaspora (2026)",
            "GlobeNewswire — Why Ready-to-Eat, Home-Cooked Meals Are the Next Big Thing (TiffinStash)",
            "The Food Institute — Regional Indian Cuisines: Yelp searches for Indian tiffin service up 153%"
        ],
        "body": """There is a hunger that no restaurant in America can satisfy. It is not for butter chicken or biryani, both available now in any decent-sized city. It is for the unglamorous daily plate — dal, a simple sabzi, soft rotis, a little rice and salad — cooked the way a mother or grandmother would make it, without the extra cream and salt that restaurants add to win over American palates. For a growing number of NRIs, that hunger is now being met by a tiffin.

Across the United States, subscription tiffin services have quietly become one of the fastest-growing corners of the food economy. Yelp searches for "Indian tiffin service" have surged 153 percent, fueled in part by viral unboxing videos from creators showing off the daily dabba. What was once an informal arrangement among friends — a neighborhood aunty cooking for a handful of bachelors — is professionalizing into a genuine industry.

## Context & Background

In India, the tiffin is a humble institution: a stacked steel container of home-cooked food, carried to office or school, and in Mumbai delivered by the legendary dabbawalas with near-perfect logistics. Transplanted to America, the concept has been reborn as a meal subscription — fresh, home-style Indian food delivered daily or weekly, customizable for vegetarian, vegan, Jain or gluten-free diets, and priced by the week rather than the plate.

The appeal is precise. Restaurant Indian food, however good, is built for occasions and indulgence. Tiffin food is built for Tuesday. It targets the student who cannot cook, the engineer working twelve-hour days, the new mother with no time, and the elderly parent visiting on a dependent visa who simply wants the food of home. For all of them, the gap between takeout and home cooking has long been unbridgeable. The tiffin bridges it.

## Current Developments

The sector's growth is being driven by a wave of founder-operators, many of them women turning home recipes into businesses. In the Bay Area, Sonu Kilam's Healthy Tiffin began as a personal idea and grew, by word of mouth, into a community-focused service drawing interest from cities across the country. Kilam leans hard into Ayurvedic, traditional cooking, positioning her tiffins as a corrective to the "westernized" Indian restaurant food that pads recipes with fat and salt. She donates meals at cultural events and gives free tiffins to seniors, pregnant women and families in hardship — a reminder that the tiffin has always been as much about care as commerce.

The model is scaling structurally, too. In Toronto, TiffinStash became the first platform in Canada to help home-based chefs get licensed and to publicly list verified, hygiene-compliant home kitchens — solving the trust-and-safety problem that has kept the cottage tiffin economy informal and legally gray. Its founder frames the business in emotional terms: "We're bridging emotional gaps. People miss the comfort of familiar meals made with care."

The numbers behind the enthusiasm are real. North America's online food delivery market, worth roughly $38 billion in 2024, is projected to grow toward $110 billion within a decade, with ethnic and home-style meals named among the fastest-growing subcategories. The demand for "ghar ka khana" is no longer a niche; it is a market.

## Diaspora Impact

For the diaspora, the tiffin boom touches something deeper than convenience. It addresses the specific loneliness of eating far from home — the way a plate of plain dal-chawal can undo a hard day in a way no restaurant meal quite manages. Services report that orders spike during festivals, exam season and the arrival of visiting parents, the moments when the ache for home cooking is sharpest.

It is also quietly reshaping who cooks professionally. The tiffin economy has opened a path to income and dignity for immigrant women whose culinary skill had no formal outlet — running licensed home kitchens, building loyal customer bases, and, in cases like Kilam's, turning a household recipe into a regional movement. The dabbawala's discipline meets the startup's app, and a centuries-old institution finds new life in suburban America.

## What's Next

The next phase will test whether the tiffin can scale without losing its essence. Platforms are racing to formalize licensing, logistics and subscription management, and venture money is beginning to notice the home-style niche. The danger is the same one facing every desi food category: that industrialization sands away the very homeliness that is the product.

For now, though, the trend points in one direction. As the diaspora grows older, busier and more spread out, the demand for a hot, simple, home-cooked plate — delivered to the door, made by someone who understands why it matters — will only deepen. The restaurant boom gave Indian food in America its prestige. The tiffin boom is giving it back its heart."""
    }
]


def main():
    print("=== Food Writer 20260620b ===")
    existing = get_existing_headlines()
    print(f"Loaded {len(existing)} existing food headlines for dedup\n")
    published = 0
    for art in ARTICLES:
        print(f"-> {art['headline'][:60]}...")
        if publish_article(art, existing):
            published += 1
        print()
    print(f"=== Done. Published {published}/{len(ARTICLES)} articles ===")


if __name__ == '__main__':
    main()
