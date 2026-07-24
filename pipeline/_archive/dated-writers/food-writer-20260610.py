#!/usr/bin/env python3
"""
Food Writer — June 10, 2026
Writes 3 food articles for The Videshi
"""
import os, json, re, requests, sys
from datetime import datetime, timezone

# ── Load env ──
with open(os.path.expanduser('~/workspace/.env.supabase')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('export '): line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v

with open(os.path.expanduser('~/workspace/.env.pexels')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k] = v

SB_URL = os.environ['SUPABASE_URL']
PEXELS_KEY = os.environ['PEXELS_API_KEY']

# ── Get service role key ──
with open('/tmp/sb_service_key.txt') as f:
    SB_KEY = f.read().strip()
print(f"Service role key loaded (length={len(SB_KEY)}, jwt={SB_KEY.startswith('eyJ')})")

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
        params={
            'category': 'eq.food',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'headline'
        },
        headers={'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
    )
    return [a['headline'].lower().strip() for a in resp.json()]

def is_duplicate(headline, existing):
    normalized = re.sub(r'[^a-z0-9]', '', headline.lower())[:40]
    for ex in existing:
        ex_norm = re.sub(r'[^a-z0-9]', '', ex)[:40]
        if normalized == ex_norm:
            return True
    return False

def search_wikimedia_commons(query):
    """Search Wikimedia Commons for CC images"""
    try:
        resp = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params={
                'action': 'query',
                'generator': 'search',
                'gsrsearch': query,
                'gsrnamespace': '6',
                'gsrlimit': '5',
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime',
                'iiurlwidth': '1200',
                'format': 'json'
            },
            headers={'User-Agent': 'TheVideshi/1.0'},
            timeout=10
        )
        data = resp.json()
        pages = data.get('query', {}).get('pages', {})
        for pid, page in sorted(pages.items(), key=lambda x: x[0]):
            info = page.get('imageinfo', [{}])[0]
            url = info.get('thumburl') or info.get('url', '')
            mime = info.get('mime', '')
            size = info.get('size', 0)
            if url and 'image' in mime and size > 5000:
                return url
    except Exception as e:
        print(f"  Commons search error: {e}")
    return None

def search_wikipedia_image(topic):
    """Get image from Wikipedia article"""
    try:
        topic_slug = topic.replace(' ', '_')
        resp = requests.get(
            f'https://en.wikipedia.org/api/rest_v1/page/summary/{topic_slug}',
            headers={'User-Agent': 'TheVideshi/1.0'},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img:
                return img
    except Exception as e:
        print(f"  Wikipedia search error: {e}")
    return None

def search_pexels(query):
    """Search Pexels for food images"""
    try:
        resp = requests.get(
            'https://api.pexels.com/v1/search',
            params={'query': query, 'per_page': 5, 'orientation': 'landscape'},
            headers={'Authorization': PEXELS_KEY},
            timeout=10
        )
        if resp.status_code == 200:
            photos = resp.json().get('photos', [])
            for photo in photos:
                url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('original')
                if url:
                    return url
    except Exception as e:
        print(f"  Pexels search error: {e}")
    return None

def validate_image(url):
    """Verify image URL returns valid image"""
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        cl = int(resp.headers.get('Content-Length', 0))
        if resp.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Some servers don't support HEAD, try GET
        if resp.status_code != 200:
            resp = requests.get(url, timeout=10, stream=True, allow_redirects=True)
            ct = resp.headers.get('Content-Type', '')
            cl = int(resp.headers.get('Content-Length', 0))
            if resp.status_code == 200 and 'image' in ct:
                return True
    except:
        pass
    return False

def find_image(topics, pexels_query):
    """Multi-source image search: Wikipedia → Commons → Pexels"""
    # Try Wikipedia first
    for topic in topics:
        print(f"  Trying Wikipedia: {topic}")
        url = search_wikipedia_image(topic)
        if url and validate_image(url):
            print(f"  ✓ Wikipedia image found")
            return url, "Wikimedia Commons"
    
    # Try Commons
    for topic in topics:
        print(f"  Trying Commons: {topic}")
        url = search_wikimedia_commons(topic)
        if url and validate_image(url):
            print(f"  ✓ Commons image found")
            return url, "Wikimedia Commons"
    
    # Try Pexels
    print(f"  Trying Pexels: {pexels_query}")
    url = search_pexels(pexels_query)
    if url and validate_image(url):
        print(f"  ✓ Pexels image found")
        return url, "Pexels"
    
    return None, None

def publish_article(article, existing_headlines):
    """Insert article into Supabase"""
    headline = article['headline']
    
    if is_duplicate(headline, existing_headlines):
        print(f"  ⚠ SKIPPED (duplicate): {headline}")
        return False
    
    slug = make_slug(headline)
    now = datetime.now(timezone.utc).isoformat()
    
    payload = {
        'headline': headline,
        'subheadline': article['subheadline'],
        'body': article['body'],
        'category': 'food',
        'vertical': 'food',
        'status': 'review',
        'is_editorial': False,
        'slug': slug,
        'published_at': now,
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
    }
    
    resp = requests.post(
        f'{SB_URL}/rest/v1/p2_articles',
        headers=HEADERS,
        json=payload
    )
    
    if resp.status_code in (200, 201):
        data = resp.json()
        art_id = data[0]['id'] if isinstance(data, list) and data else 'unknown'
        print(f"  ✓ PUBLISHED: {headline}")
        print(f"    slug: {slug}")
        print(f"    id: {art_id}")
        return True
    else:
        print(f"  ✗ FAILED: {resp.status_code} — {resp.text[:200]}")
        return False

# ══════════════════════════════════════════════════════════════
# ARTICLES
# ══════════════════════════════════════════════════════════════

articles = []

# ── Article 1: Curry Leaf trending on American menus ──
print("\n📝 Writing Article 1: Curry Leaf on American Menus")
img1_url, img1_attr = find_image(
    ["Curry tree", "Murraya koenigii", "Curry leaves"],
    "curry leaves Indian cooking"
)

article1_body = """India's most unassuming herb is having its most glamorous moment. The curry leaf — that fragrant, slightly bitter staple that your grandmother tossed by the fistful into tadkas and sambars — is turning up in some of America's most ambitious cocktail bars and fine-dining kitchens. And it's not just a garnish anymore.

## From Tadka to Tasting Menu

At The Pool in New York City, curry leaves steep alongside pomegranate and Scotch in the restaurant's Smoke Cocktail, a drink that sells for the price of an entire thali back in Mumbai. Down the block at Mace, bartenders are fat-washing Barbados rum with coconut oil and infusing it with curry leaf bitters alongside pandan. In San Jose, California, Straits serves crab croquettes seasoned with curry leaf and Indian spices, topped with mango salsa — a dish that feels as at home on the Pacific Rim as it does in a Mangalorean kitchen.

It's not just a coastal phenomenon. At MG Road Bar & Lounge in Asheville, North Carolina, chef-owner Meherwan Irani — who grew up near Mumbai — batters cauliflower with Kashmiri chile, garam masala, and curry leaves for his wildly popular Gobi 65. In Oxford, Mississippi, swordfish arrives with a curry leaf vinaigrette at Snackbar.

## Why Now?

The curry leaf's rise tracks a broader shift in how American restaurants engage with Indian ingredients. According to Restaurant Business, the leaves are "better known in India, where they literally grow on trees," but they're now "starting to show up on U.S. menus, flavoring a variety of dishes and drinks."

Part of the appeal is nutritional. Fresh curry leaves are believed to support heart health, fight infection, and aid digestion — credentials that play well in a wellness-obsessed dining culture. But the real driver is flavour: nothing else delivers that specific citrus-herbaceous punch that South Indian cooking relies on.

The trend also reflects a generation of Indian-American and Indian-born chefs who refuse to flatten their cuisine into butter chicken and naan. Curry leaf is an insider's ingredient — one that signals authenticity and regional specificity. When it shows up on a non-Indian menu, it means the chef has done their homework.

## The Diaspora Connection

For NRIs, the curry leaf trend produces a familiar mix of pride and mild exasperation. Many diaspora households have been growing curry leaf plants on kitchen windowsills for decades, shipping saplings in suitcases from India and nursing them through American winters. The idea that the humble kadi patta now commands a premium on cocktail menus in Manhattan is both vindicating and slightly absurd.

Indian grocery chains like Patel Brothers and Subzi Mandi have stocked fresh curry leaves for years. Now mainstream suppliers like Baldor are adding them to their catalogues as demand grows from non-Indian restaurants.

## What's Next

Expect curry leaf to follow the trajectory of lemongrass and kaffir lime leaf — ingredients that were once "exotic" imports and are now pantry staples in serious American kitchens. As more progressive Indian restaurants open across the US — Indienne in New York, Gymkhana in Las Vegas, Ambassadors Clubhouse on the East Side — the broader pantry of South Indian and coastal cooking is coming with them. The curry leaf is just the advance scout."""

articles.append({
    'headline': "Kadi Patta Goes Upscale: How India's Humblest Herb Conquered America's Cocktail Bars",
    'subheadline': "From Scotch-and-pomegranate drinks in Manhattan to cauliflower Gobi 65 in Asheville, the curry leaf is breaking out of the tadka and into fine dining.",
    'body': article1_body,
    'image_url': img1_url,
    'image_caption': "Fresh curry leaves, the aromatic South Indian herb now trending on American menus",
    'image_attribution': img1_attr,
})

# ── Article 2: Progressive Indian dining's biggest year ──
print("\n📝 Writing Article 2: Progressive Indian Dining in America")
img2_url, img2_attr = find_image(
    ["Dishoom", "Indian cuisine", "Biryani"],
    "upscale Indian restaurant dining"
)

article2_body = """Something remarkable is happening in American restaurants in 2026: Indian cuisine is shedding the buffet-and-naan straitjacket and arriving as one of the most exciting forces in fine dining. The evidence is everywhere — in Michelin-starred expansions, $400 million valuations, and a Yelp data point that would have seemed absurd five years ago: a 459% surge in searches for "Indian buffet."

## The British Invasion, Desi Edition

The most anticipated opening on the horizon is Dishoom, the beloved London chain that has turned Bombay-inspired comfort food into a cultural institution across the UK. The restaurant has secured 11 East 26th Street, right off Madison Square Park in New York, with a rep confirming a target opening. Backed by L Catterton in a deal reportedly valuing the 12-unit chain at nearly $400 million, Dishoom's New York debut represents the biggest bet yet that Americans are ready for sophisticated, emotionally resonant Indian dining.

Dishoom is just one front. JKS Restaurants brought its Gymkhana concept — a Michelin-starred colonial-era hunting lodge fantasy — to the Aria Resort & Casino in Las Vegas. Their Punjabi-focused Ambassadors Clubhouse in New York has become one of the hardest reservations in the city.

## Homegrown Ambitions

American-based chefs are matching the British imports move for move. Michelin-starred Sujan Sarkar is expanding his acclaimed Chicago restaurant Indienne to Henry Hall in Hudson Yards this year, to be followed by Apas, a cocktail bar, and Elder, a British-Indian chophouse. He's also opened Ayra in Chapel Hill, North Carolina, and plans Nadu — named for the Tamil word for "homeland" — in Phoenix.

In the same city, Indibar by Masti Hospitality is launching Lehr, a restaurant-within-a-restaurant featuring a 10-course tasting menu for up to 22 guests at a time — a journey through India's regional cuisines with the intimacy of a private dinner party.

## The Numbers Tell the Story

The data backs what diners already know. According to Technomic, 34% of American consumers say they've tried Indian food and consider it "unique and exciting." Yelp's 2026 trend report showed a 459% increase in searches for Indian buffets and a 49% spike in biryani chicken queries. Fast-casual concepts are riding this wave too: The Kati Roll Company, which started with a 300-square-foot shop in Manhattan, now operates six locations serving spice-packed kati rolls and date-palm-sugar lassis.

## The Diaspora Angle

For Indian Americans who grew up wincing when classmates called their lunchbox food "smelly," this moment lands differently. The cuisine that was once flattened into "curry" by the American palate is now being celebrated in its staggering regional diversity — from Chettinad pepper to Awadhi biryani to Goan vindaloo.

But the boom also raises questions. When a London chain valued at $400 million opens in New York serving Bombay street food, who benefits? The hope is that the rising tide lifts all boats — from fine-dining flagships to the family-run Woodlands and Temple Canteens in Queens that have quietly served extraordinary food for decades.

## What's Next

The pipeline is stacked. Dishoom's New York opening could be the Indian dining equivalent of Shake Shack's early days — a concept that redefines an entire category for American consumers. With multiple progressive Indian restaurants planned across the country, 2026 may be remembered as the year Indian food in America stopped being a niche and became a movement."""

articles.append({
    'headline': "From Gymkhana to Kati Rolls: 2026 Is Indian Dining's Breakout Year in America",
    'subheadline': "With Dishoom eyeing Manhattan, Indienne expanding to Hudson Yards, and Yelp searches for Indian buffets up 459%, the cuisine is having its biggest moment stateside.",
    'body': article2_body,
    'image_url': img2_url,
    'image_caption': "Indian fine dining is experiencing an unprecedented expansion across American cities",
    'image_attribution': img2_attr,
})

# ── Article 3: AIA Bay Area Indian Food Festival ──
print("\n📝 Writing Article 3: Indian Food Festivals in America")
img3_url, img3_attr = find_image(
    ["Indian festival food", "Indian street food", "Pani puri"],
    "Indian food festival street food colorful"
)

article3_body = """On a warm May weekend in San Ramon, California, more than 15,000 people showed up to eat samosas, shop for saris, and watch Bollywood dance performances at what has quietly become one of the largest Indian diaspora cultural events on the West Coast. The Great Indian Food & Shopping Fest, organized by the Association of Indo Americans, featured over 100 vendors and drew families from across the Bay Area — proof that desi food festivals have evolved from small community potlucks into major cultural productions.

## A Festival Ecosystem Takes Shape

The AIA festival is part of a growing ecosystem of Indian food events across the United States. From Houston's Diwali Mela to New Jersey's Navratri garba nights — which routinely draw 10,000-plus attendees — the Indian food festival circuit has become a serious economic and cultural force.

What makes these events different from, say, a Taste of Chicago is their community infrastructure. The AIA event in San Ramon featured not just food vendors but jewelry sellers, handicraft artisans, local Indian businesses, and a Mother's Day Saree Promenade. India's Consul General in San Francisco attended. Community leader Jayaram Komati was felicitated for his appointment as Andhra Pradesh's Special Representative for North America.

This is food as community architecture — and it's increasingly sophisticated.

## The Food Tells the Story

The menu at these festivals reads like a map of India's culinary geography. You'll find Hyderabadi biryani alongside Gujarati dhokla, Punjabi chole bhature next to Keralan fish molee. Chaat stalls do brisk business — the mix of tangy, spicy, and sweet that defines Indian street food translates perfectly to outdoor festival eating.

What has changed in recent years is the quality. Festival organizers report that vendors are moving beyond the basics. Fusion offerings — masala tacos, curry fries, chai lattes — sit alongside traditional favourites. Several festivals now feature live cooking demonstrations and chef competitions. The food truck revolution has intersected with the Indian festival circuit, producing mobile vendors who travel the summer festival route from California to Texas to the East Coast.

## Why It Matters for NRIs

For Indian Americans, these festivals serve a function that goes beyond nostalgia. They are where second-generation kids taste their grandmother's recipes made by strangers and discover that the food they ate growing up isn't just family tradition — it's culture. They are where new immigrants find the Maggi noodles and Parle-G biscuits that taste like home. And they are where non-Indian neighbours discover that Indian food extends far beyond the tikka masala they order on DoorDash.

The economic impact is real, too. Major festivals generate six-figure revenues for local vendors and bring foot traffic to Indian commercial corridors. In Edison, New Jersey, and Artesia, California — two cities with significant Indian commercial districts — festival seasons drive year-round business awareness.

## The Next Wave

The festival format is evolving. Some organizers are experimenting with ticketed tasting events modelled on wine and food festivals — smaller, curated experiences focused on regional cuisines. Others are incorporating wellness elements, with Ayurvedic cooking demonstrations and turmeric latte bars. A few have begun partnering with mainstream food festival brands, bringing Indian vendors into events like FoodieLand — the nation's largest food festival, which features 250-plus vendors with global flavours.

The trend line is clear: Indian food festivals in America are getting bigger, more professional, and more ambitious. For a diaspora community that has always used food as its primary language of belonging, these gatherings are becoming something larger — a public celebration of identity that's impossible to ignore."""

articles.append({
    'headline': "15,000 Samosas and a Saree Promenade: Inside America's Booming Indian Food Festival Circuit",
    'subheadline': "From San Ramon to Edison, desi food festivals have evolved from community potlucks into cultural productions drawing tens of thousands — and reshaping how America tastes India.",
    'body': article3_body,
    'image_url': img3_url,
    'image_caption': "Indian street food like pani puri draws thousands to diaspora food festivals across the US",
    'image_attribution': img3_attr,
})

# ══════════════════════════════════════════════════════════════
# PUBLISH
# ══════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

existing = get_existing_headlines()
print(f"Found {len(existing)} existing food articles for dedup check")

published = 0
for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i} ---")
    print(f"Headline: {article['headline']}")
    wc = len(article['body'].split())
    print(f"Word count: {wc}")
    print(f"Image: {'✓' if article.get('image_url') else '✗ None'}")
    
    if wc < 400:
        print(f"  ⚠ SKIPPED (word count {wc} below 400 minimum)")
        continue
    
    if publish_article(article, existing):
        published += 1
        existing.append(article['headline'].lower().strip())

print(f"\n{'='*60}")
print(f"DONE: {published}/{len(articles)} articles published to review queue")
print(f"{'='*60}")
