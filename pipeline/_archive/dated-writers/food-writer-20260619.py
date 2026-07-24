#!/usr/bin/env python3
"""
Food Writer — June 19, 2026
3 food articles for The Videshi
1. Indibar (Scottsdale) — USA TODAY Restaurant of the Year 2026, Indian + Sonoran desert
2. Indian frozen/ready-meals go mainstream — Truly Indian NEXTY finalist + Quicklly at Costco/ALDI
3. Mango season — diaspora's viral summer recipe wave (pani puri, sago, malai toast)
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
            print("  \u2713 Wikipedia")
            return img, "Wikimedia Commons"
    for t in topics_commons:
        print(f"  Commons: {t}")
        img = search_wikimedia_commons(t)
        if img and validate_image(img):
            print("  \u2713 Commons")
            return img, "Wikimedia Commons"
    for t in topics_pexels:
        print(f"  Pexels: {t}")
        img = search_pexels(t)
        if img and validate_image(img):
            print("  \u2713 Pexels")
            return img, "Pexels"
    return None, None

def publish_article(article, existing):
    headline = article['headline']
    if is_duplicate(headline, existing):
        print(f"  \u26a0 SKIP duplicate: {headline}")
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
        print(f"  \u2713 Published: {headline}\n    slug: {slug}  id: {aid}  words: {wc}")
        return True
    print(f"  \u2717 Failed: {resp.status_code} - {resp.text[:200]}")
    return False

articles = []

# ─────────────────────────────────────────────────────────────
# ARTICLE 1 — Indibar / USA TODAY Restaurant of the Year
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 1: Indibar USA TODAY Restaurant of the Year")
a1_body = """In the strip-mall sprawl of Paradise Valley, Arizona, between a desert highway and a public parking lot, two chefs who met cooking fine dining at The Taj in Dubai have built one of the most decorated Indian restaurants in America. Indibar, the contemporary Indian craft-cocktail bar led by chefs Nigel Lobo and Ajay Singh, has been named one of USA Today's Restaurants of the Year for 2026 — the latest in a run of national honors that has turned a Scottsdale-area room into a case study for where Indian food in America is heading.

The recognition cites Indibar's "unique menu of Indian dishes presented with fine dining precision," along with its Indian-inspired cocktail program. It arrives alongside a James Beard Foundation semifinalist nod for Best New Restaurant and a place on Phoenix New Times' 50 Best Restaurants list.

## Context & Background

Lobo and Singh's partnership began far from the Sonoran Desert. The two met while working as fine-dining chefs at The Taj in Dubai, forming a friendship rooted in a shared culinary vision. When Lobo relocated to Arizona, drawn to the distinct landscapes and native ingredients of the desert Southwest, he invited Singh to join him. The result was a restaurant that does something few Indian kitchens in America attempt: it weds the regional cooking of their upbringing to indigenous Sonoran ingredients.

That fusion is not a gimmick. The chefs have built dishes around the tepary bean — a drought-hardy legume cultivated by the region's Native communities for millennia — treating it with the same reverence an Indian kitchen gives to its dals. The approach reframes the question of what "Indian food" can mean once it puts down roots in American soil.

## Current Developments

Indibar's 2026 has been a procession of validations. The James Beard semifinalist listing in the national Best New Restaurant category placed it among the most-watched openings in the country. USA Today's Restaurant of the Year designation extended that reach to a mainstream national audience. Locally, the restaurant landed on Phoenix New Times' 50 Best and was a finalist for the Arizona Foodist Awards' most creative cocktail program — a category that pits it against the state's top bars rather than its top Indian restaurants.

The menu leans on vibrant spices, seasonal ingredients and a cocktail list built to match — turning what could have been a neighborhood curry house into a destination booked dozens of times a day on reservation platforms. Priced in the $31-to-$50 range, it occupies the elevated-but-accessible tier that a generation of ambitious Indian restaurants in America is racing to claim.

## Diaspora Impact

For Indian-Americans, Indibar's recognition lands as part of a larger correction. For decades, "Indian restaurant" in the United States signified a buffet, a lunch special, a value proposition. The current wave — Vikas Khanna's Bungalow in New York, Sujan Sarkar's NADU in Chicago and now Phoenix, Tamba in Las Vegas, and Indibar in the desert — insists on something else: that Indian cooking belongs in the same conversation as any other fine-dining cuisine, judged on technique and creativity rather than price.

What makes Indibar's story resonate for the diaspora is its location. This is not New York or the Bay Area, where a critical mass of Indian diners can sustain ambitious cooking. It is suburban Arizona, where the chefs are introducing regional Indian flavors to an audience that may have known only tikka masala — and winning over critics in the process. For NRI families scattered across America's less-dense metros, that is proof their food can thrive anywhere.

## What's Next

The Sonoran-Indian experiment points toward a broader trend: chefs of Indian origin treating their adopted American landscapes as part of the pantry, not a constraint on it. Lobo and Singh have spoken of bringing India closer through the lens of local ingredients, and their success will encourage others to do the same in their own regions.

For now, Indibar's calendar tells the story — booked solid, happy hours full, a former Taj duo's desert gamble vindicated on a national stage. The desert, it turns out, was always a good place to grow something new."""

articles.append({
    'headline': "From Dubai to the Desert: How Indibar Became One of America's Restaurants of the Year",
    'subheadline': "The Scottsdale-area Indian craft-cocktail bar, built by two former Taj chefs around Sonoran ingredients, lands a USA Today honor and a James Beard nod.",
    'body': a1_body,
    'sources': [
        "USA TODAY / azcentral — Over a dozen Arizona restaurants named best in US this year (Indibar, Restaurant of the Year 2026)",
        "OpenTable — INDIBAR Restaurant, Paradise Valley AZ (Chefs Nigel Lobo and Ajay Singh; James Beard semifinalist; Phoenix New Times 50 Best)",
        "Phoenix Magazine — 12 in Arizona Named James Beard Award Semifinalists in 2026 (INDIBAR, Best New Restaurant)",
        "Visit Phoenix — Sonoran Food Guide: tepary bean, Chefs Nigel Lobo and Ajay Negi, Indibar origin"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=[],
        topics_commons=["Indian fine dining plated dish", "modern Indian cuisine restaurant plate"],
        topics_pexels=["Indian fine dining restaurant plated", "Indian curry restaurant elegant plating"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 2 — Indian frozen/ready-meals go mainstream
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 2: Indian ready-meals go mainstream")
a2_body = """The frozen-food aisle has become an unlikely front line in Indian cuisine's American conquest. Once the preserve of a few dusty bags of samosas at the local desi grocery, the freezer case at Costco, ALDI and Whole Foods now carries butter chicken, lamb vindaloo and tandoori naan made at industrial scale and aimed squarely at mainstream shoppers. The signal that the shift has gone fully legitimate came this spring, when Truly Indian, a brand of the 94-year-old Mumbai house ADF Foods, was named a finalist in two categories at the 2026 NEXTY Awards — the natural-products industry's most closely watched honor.

Truly Indian's Tikka Masala Naan and Crispy Chili Mango Chutney both made the NEXTY finalist list, a recognition that certifies not just sales but innovation. For a diaspora that once had to drive across town for a freezer bag of parathas, the mainstreaming of Indian convenience food is a quiet revolution.

## Context & Background

Indian food is now the second-fastest-growing global cuisine in America, according to data firm Datassential, and the U.S. ethnic-food market is estimated at $24.5 billion by Ken Research. That demand has pulled a wave of brands off the desi-grocery shelf and into national retail.

ADF Foods, founded as a single Mumbai storefront in 1932 and now a fourth-generation family business, launched Truly Indian in May 2024. Within roughly a year it expanded to more than 1,300 stores nationwide, including 509 Whole Foods locations for its frozen naan alone. The brand's pitch threads a careful needle: hand-stretched naans — about 150,000 produced daily in India — baked in traditional clay ovens, but formulated to be vegan, Non-GMO Project Verified, low-glycemic, kosher and halal. It is heritage craftsmanship sold to a label-reading American shopper.

## Current Developments

The retail land grab has accelerated. In January, Quicklly — the largest Indian online marketplace in the U.S. — launched its "Just by Quicklly" ready-to-heat line at Costco and ALDI, one of the category's biggest national rollouts to date. Butter chicken, among the most-consumed Indian dishes in America, anchors a Costco run across 81 Southeast warehouses, while ALDI carries butter chicken and chicken tikka masala across 2,500 stores. The lineup also reaches for regional specificity with dishes like Goan lamb vindaloo, made with grass-fed lamb and long-grain Himalayan basmati.

Older players are thriving too. Sukhi's Gourmet, the Hayward, California brand founded by Sukhi Singh, has built its Costco business on refrigerated entrées — its chicken tikka masala remains the top seller — while developing compostable trays that cut packaging plastic by 70 percent. And at Costco, the humble block of Gopi paneer has become a viral value find, with 2.5-pound bricks selling for about $10.49.

## Diaspora Impact

For NRIs, the change is practical and emotional at once. The practical part: a graduate student in Ohio or a young family in Texas can now buy a credible butter chicken or a stack of clay-oven naan on a normal grocery run, no special trip required. The emotional part runs deeper. For years, the diaspora watched American "Indian food" mean a single beige curry, while the real range of the cuisine stayed locked inside home kitchens and immigrant-run shops.

Seeing ADF Foods, Quicklly and Sukhi's win national distribution — and industry awards — is a form of recognition. It says the food of home is good enough, and wanted enough, to sit on the same shelf as every other cuisine America has embraced. The vegan, halal and gluten-free formulations also reflect a diaspora that has fused its inherited palate with American dietary norms.

## What's Next

The trajectory points toward more shelf space and more specificity. Brands are betting that American shoppers, having mastered tikka masala, are ready for vindaloo, dosa batters and regional chutneys. Tariff pressures on imported ingredients remain a wildcard for pricing, but retailers report demand strong enough to keep expanding distribution across natural, conventional and club channels.

The freezer aisle, in other words, is no longer a compromise. For the diaspora, it is becoming a mirror — proof that Indian food has gone from the back of the store to the center of the American cart."""

articles.append({
    'headline': "Butter Chicken in the Costco Cart: Indian Ready-Meals Storm the American Freezer Aisle",
    'subheadline': "Truly Indian's NEXTY Award finalist nods and Quicklly's Costco and ALDI rollout show how desi convenience food is moving from the ethnic shelf to the national mainstream.",
    'body': a2_body,
    'sources': [
        "Food Dive — Truly Indian Named 2026 NEXTY Finalist in Two Categories (ADF Foods, Tikka Masala Naan, Crispy Chili Mango Chutney)",
        "Retail Dive — Truly Indian Expands in U.S. Grocery Aisles (1,300+ stores; Datassential second-fastest-growing cuisine; $24.5B ethnic-food market)",
        "Morningstar / ACCESS Newswire — Quicklly Achieves a Major Nationwide Milestone with Costco and ALDI launch (butter chicken, lamb vindaloo)",
        "Costco Connection — Sukhi's Gourmet supplier profile (chicken tikka masala, compostable trays); The Kitchn — Gopi paneer Costco find"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=[],
        topics_commons=["butter chicken Indian dish", "frozen naan bread Indian", "chicken tikka masala"],
        topics_pexels=["butter chicken Indian curry bowl", "Indian frozen meal naan"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 3 — Mango season viral recipes / diaspora nostalgia
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 3: Mango season viral recipes")
a3_body = """Every June, something happens in the diaspora kitchen that no marketing department engineered. The mangoes arrive — boxed Alphonso and Kesar at the desi grocery, ripening on apartment windowsills from New Jersey to the Bay Area — and the internet fills with the sound of Indian home cooks turning the fruit into everything but a plain sliced snack. This summer, mango season has gone fully viral, and the recipes racing through Instagram reels and WhatsApp forwards are doing more than feeding a craving. They are carrying a generation's nostalgia across an ocean.

The breakout dishes read like a fever dream of summer: Double Mango Pani Puri, which fills the classic street snack with a chilled raw-mango aampanna and a ripe-mango masala; mango sago laced with aam papad and coconut; mango malai toast; and a viral mango-wafer cheesecake that MasterChef India alum Aruna Vijay sent ricocheting around the foodie internet within hours of posting.

## Context & Background

Mango occupies a place in the Indian imagination that no other fruit approaches. It is the "king of fruits," the taste of school holidays, the centerpiece of summer rituals from pickling raw green mangoes to ending a meal with chilled aamras. For the diaspora, the fruit is freighted with memory — of grandmothers, of monsoon afternoons, of a homeland measured out in seasons that the American calendar does not quite share.

That emotional charge is exactly why mango recipes travel so well online. A 30-second reel of someone assembling mango pani puri is not just a cooking tutorial; it is a hit of homesickness, instantly legible to anyone who grew up with the fruit. Food creators have learned that the surest way to virality in summer is to take a beloved classic — pani puri, puran poli, kheer — and run it through the mango.

## Current Developments

The 2026 crop of viral recipes shows how inventive the genre has become. Food influencer Aruna Vijay's Double Mango Pani Puri pairs a cooling aampanna-style pani made from pressure-cooked raw mango with a hearty filling of ripe mango and black chana — a single snack that delivers refreshing, fruity, spicy and tangy notes in one bite. Celebrity chef Saransh Goila's mango sago, built with coconut milk, condensed milk, aam papad and coco-de-nata jelly, became a fixture of summer feeds. Mango malai toast and mango poli — a seasonal twist on the Maharashtrian puran poli — have spread through short-form video, prized for being fuss-free enough to recreate in a small apartment kitchen.

What unites them is accessibility. The ingredients — ripe mangoes, semolina, ghee, cardamom, plain wafers — are available at any Indian grocery and most mainstream supermarkets in mango season, putting these dishes within reach of a homesick cook anywhere in America.

https://www.instagram.com/reel/DZKVnIcTeUE/

## Diaspora Impact

For NRIs, the mango-recipe wave solves a specific summer ache. The fruit that defined childhood summers is harder to come by abroad — pricier, more seasonal, sometimes hostage to import rules and tariffs. So when it does arrive, the impulse is not to ration it but to celebrate it, and the viral recipes offer a script. A reel watched in Sunnyvale can be recreated that same weekend with a box of Kesar mangoes from the local Patel Brothers.

The dishes also become a bridge across generations. Parents raising children abroad use mango season to pass on a sensory inheritance — teaching a kid to suck the seed clean, to recognize the smell of a ripe Alphonso, to understand why this fruit, of all fruits, makes the adults in the family go quiet with longing. The recipes, shared and reshared on family WhatsApp groups, knit scattered relatives back into a single seasonal ritual.

## What's Next

As mango season peaks, expect the genre to keep multiplying — fusion desserts, protein-spiked smoothies, mango-forward cocktails for the grown-ups. Food-trend watchers note that the appetite for "swavory" and seasonal, story-rich food is only growing, and few stories are richer than the diaspora's relationship with the king of fruits.

The deeper truth is simple. For a community that lives between two calendars, mango season is one of the few that survives the journey intact. The viral recipes are just the diaspora's way of saying: home is still here, and it tastes like summer."""

articles.append({
    'headline': "King of Fruits, Queen of the Feed: How Mango Season Conquered the Diaspora Internet",
    'subheadline': "From Double Mango Pani Puri to mango sago and malai toast, viral summer recipes are turning a fruit into a hit of homesickness for NRIs.",
    'body': a3_body,
    'sources': [
        "Whosthat360 — Double Mango Pani Puri Recipe: Summer Twist on Classic Chaat (food influencer Aruna Vijay)",
        "Whosthat360 — Saransh Goila's Mango Sago Recipe (aam papad, coco-de-nata jelly, coconut milk)",
        "Gree News — Viral Mango Wafers Cheesecake (Aruna Vijay, MasterChef India 2023)",
        "Glance Trends — Viral mango puran poli (mango poli) seasonal recipe"
    ],
    'embeds': [],  # embed placed inline in body above
    'img': dict(
        topics_wiki=["Mango", "Aamras"],
        topics_commons=["ripe mango Alphonso India", "mango slices summer", "Indian mango dessert"],
        topics_pexels=["ripe mango sliced summer", "mango dessert bowl"])
})

# ── Source images ──
for i, art in enumerate(articles, 1):
    print(f"\n\U0001f5bc  Image for Article {i}...")
    img = art.pop('img')
    url, attr = find_image(**img)
    if url:
        art['image_url'] = url
        art['image_attribution'] = attr
    else:
        art['image_url'] = None
        art['image_attribution'] = None
        print("  \u26a0 No image found")

# Captions (set after image found)
caps = [
    "Contemporary Indian fine dining, the style elevating restaurants like Indibar",
    "Butter chicken, one of the most-consumed Indian dishes now sold in US grocery chains",
    "Ripe Indian mangoes, the fruit at the centre of the diaspora's viral summer recipes"
]
for art, cap in zip(articles, caps):
    if art.get('image_url'):
        art['image_caption'] = cap

# ── Insert inline embeds into body (after the section before Diaspora Impact) ──
for art in articles:
    embeds = art.pop('embeds', [])
    if embeds:
        body = art['body']
        marker = "## Diaspora Impact"
        if marker in body:
            idx = body.index(marker)
            embed_block = "\n\n" + "\n".join(embeds) + "\n\n"
            art['body'] = body[:idx] + embed_block + body[idx:]
        else:
            art['body'] = body + "\n\n" + "\n".join(embeds)

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
