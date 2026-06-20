#!/usr/bin/env python3
"""
Food Writer — June 20, 2026
3 food articles for The Videshi
1. The British Invasion — UK Indian restaurants (Dishoom, JKS, Darjeeling Express) storm NYC
2. Beyond Butter Chicken — regional Indian fine dining lands in mid-tier US metros (NADU Phoenix, Dakshin Rochester, Rishtedar Miami)
3. Cuisine of the Year — "Next-Gen Indian" goes CPG (Lay's Masala, Miss Vickie's Tandoori, Bollygood)
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
# ARTICLE 1 — The British Invasion
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 1: British Indian restaurants storm NYC")
a1_body = """For half a century, the most ambitious Indian restaurants in the English-speaking world were not in Mumbai or Delhi but in London — a city where chicken tikka masala became an unofficial national dish and where curry houses evolved into Michelin-starred dining rooms. Now that culinary establishment is crossing the Atlantic. A wave of celebrated British-Indian restaurant groups is opening in New York, betting that America is finally sophisticated enough for the version of Indian food Britain has been perfecting for decades.

The clearest signal came when Dishoom, the cult Bombay-café mini-chain founded by cousins Shamil and Kavi Thakrar in London's Covent Garden in 2010, confirmed it will open its first overseas restaurant in lower Manhattan in 2026. It is not arriving alone.

## Context & Background

Dishoom's American debut is the product of years of courtship. The brand tested New York's appetite with a two-week breakfast pop-up at the French bistro Pastis in the summer of 2024 — reservations sold out in under five minutes, serving roughly 7,000 diners with another 20,000 on the waitlist. Today Dishoom operates more than ten restaurants across the U.K., serves over 100,000 guests a week, and employs around 2,000 people. To fund its international leap, it secured a reported £300 million investment from L Catterton, the private-equity firm backed by LVMH — a valuation that places a Bombay-café homage in the same financial league as luxury fashion houses.

Co-founder Kavi Thakrar, who told the New York Times he had eyed Manhattan since 2016, says "the time is right." His reasoning is demographic and cultural: the growth of South Asian communities, the rise of Indian-American chefs, and a wholesale shift in how Americans perceive Indian food. "There are so many young professionals, second-generation, third-generation people running businesses," he said. "Indian food is finally part of the city's fabric."

## Current Developments

Dishoom is one of several British names heading stateside. JKS Restaurants, the London group behind Michelin-starred Gymkhana, has signed a lease to launch its Punjabi-focused Ambassadors Clubhouse in Manhattan, while an outpost of Gymkhana itself opened at the Aria Resort in Las Vegas. Asma Khan's Darjeeling Express — the all-women kitchen made famous by Netflix's "Chef's Table" — is slated to open in New York following its own sold-out pop-up, and the small-plates favorite Kricket is reported to be eyeing a 2026 Manhattan launch.

The British arrivals join a homegrown American renaissance that paved the way: Dhamaka, Semma, and Vikas Khanna's Bungalow have already taught New York diners that Indian cooking can be regional, fine-dining, and unapologetically bold. Industry observers note the British groups bring something distinct — a polished hospitality model honed over decades in a market where Indian food never carried the "cheap ethnic" stigma it long bore in the United States.

## Diaspora Impact

For Indian-Americans, the British Invasion is bittersweet and validating at once. It is a reminder that Britain, for all its colonial baggage, built a culture that took Indian food seriously long before America did — the bacon naan roll exists because the U.K. wove Indian cooking into its everyday rhythms. Watching Dishoom and Darjeeling Express cross the ocean signals that New York has finally reached the same threshold.

There is also a question of authenticity that the diaspora is watching closely. Dishoom's romanticized Irani-café aesthetic and its anglicized comfort dishes are beloved, but some second-generation diners wonder whether New York wants a British interpretation of Bombay or the real regional cooking that operators like Semma and Dhamaka already deliver. The answer may be that there is now room for both — proof of how far the cuisine has traveled in American esteem.

## What's Next

Dishoom has said it plans to open two or three U.S. sites a year if New York succeeds, with Boston, Chicago, and Washington, D.C. all scouted as future homes. The British wave, combined with the American fine-dining boom, is rapidly turning the United States into the next great frontier for Indian cuisine.

The larger story is one of reversal. For generations, Indians who emigrated to Britain and America adapted their food to survive in foreign markets. Now the most refined expressions of that adaptation are being exported back across borders — and a New Yorker's idea of Indian food is about to get a great deal more interesting."""

articles.append({
    'headline': "The British Are Coming: London's Indian Dining Empire Storms New York",
    'subheadline': "Dishoom, Darjeeling Express and JKS Restaurants are crossing the Atlantic, betting America is finally ready for the Indian food Britain perfected.",
    'body': a1_body,
    'sources': [
        "Robb Report India / The Caterer — L Catterton's £300m investment in Dishoom ahead of 2026 New York debut",
        "Secret NYC / New York Times — Dishoom confirms lower-Manhattan opening; Kavi Thakrar on Indian food as 'part of the city's fabric'",
        "The Caterer — JKS Ambassadors Clubhouse Manhattan lease, Gymkhana Las Vegas, Darjeeling Express and Kricket 2026 plans",
        "The Infatuation — NYC's Most Anticipated Restaurant Openings of 2026 (Ambassadors Clubhouse, Dishoom)"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=[],
        topics_commons=["Indian restaurant interior dining", "black dal Indian dish", "Indian restaurant table food"],
        topics_pexels=["Indian restaurant interior elegant", "Indian curry restaurant table"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 2 — Beyond Butter Chicken (regional Indian in mid-tier metros)
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 2: Regional Indian beyond the coasts")
a2_body = """The proof that Indian food has conquered America is no longer found only in New York or the Bay Area. It is in Rochester, New York, where a Tamil restaurateur is opening a South Indian dining room because customers were already driving ninety minutes for her dosas. It is in suburban Phoenix, where a Michelin-recognized Chicago chef is launching a restaurant built around regional kebabs from across India. And it is in Miami's Wynwood arts district, where an Indian restaurant born in Chile has planted its first American flag. The frontier of desi cuisine has moved inland — and it is going regional.

This new geography matters because it breaks Indian food out of the coastal enclaves where a critical mass of South Asian diners could always sustain it, and into the rest of the country, where the audience is curious but uninitiated.

## Context & Background

For decades, "Indian restaurant" in middle America meant a single template: a North Indian menu of butter chicken, tikka masala, and garlic naan, often served buffet-style at a value price. That template was a survival strategy — the safest possible introduction to an unfamiliar cuisine. The current wave of openings rejects it deliberately, wagering that American diners outside the big metros are now ready for specificity.

Vimala Mohanraj embodies the shift. Before opening her Dakshin Indian Cuisine in Syracuse last year, she ran North Indian restaurants in Albany and New Jersey, serving the fare Americans already knew. Now she is opening a second Dakshin in Rochester focused on the cooking of her native Tamil Nadu — coconut-based curries instead of butter and cream, a wide range of dosas, and Kerala parotta. "I want to let people know that it is different than butter chicken and garlic naan," she said. Her Syracuse success — and customers willing to drive an hour and a half — convinced her the appetite was real.

## Current Developments

In Phoenix, the celebrated chef Sujan Sarkar is bringing NADU — the word means "homeland" — to the Desert Ridge Marketplace, with his brother and longtime mentee Pujan at the helm. The Phoenix location will feature a regional kebab program spanning the subcontinent: a Galouti kebab from Lucknow, Bhatti ka Murgh from Punjab, a Chapli kebab from the northwest frontier, plus duck seekh and a signature Bihari kebab. "Indian food can be different from what they're used to," Pujan said, pairing the menu with a cocktail program built on turmeric, saffron, chili, ginger, and curry leaf.

Meanwhile in Miami, Rishtedar — a fine-dining institution from Santiago, Chile — has opened its first U.S. location in Wynwood. Founder Vikram Thadani, born to Indian parents in Chile, built the brand from an import business and now aims to introduce Miami to Indian culture the way he once introduced it to Chileans. "Rishtedar means 'family,'" he said, "and as soon as our diners step foot in here, we like to expose them to many traditions." The menu runs from tandoori shrimp served over blazing charcoal to lamb in onion-masala sauce.

## Diaspora Impact

For NRIs scattered across America's less-dense metros, these openings are a quiet homecoming. A Tamil family in upstate New York or a Punjabi household in Arizona has long had to choose between a generic curry house and cooking everything from scratch. A restaurant that serves the specific food of their region — and serves it with pride rather than apology — is a form of belonging.

The openings also reframe the diaspora's relationship with its own cuisine. When a chef in Phoenix builds a menu around Lucknowi and frontier kebabs, or a Chilean-Indian restaurateur brings his hybrid heritage to Miami, they signal that Indian food in America is no longer a monolith to be flattened for mainstream palates. It can be as plural and regionally proud abroad as it is at home.

## What's Next

The expansion into mid-tier metros points to a maturing market. As second- and third-generation Indian-Americans spread beyond traditional gateway cities, and as non-Indian diners grow more adventurous, the economics of regional Indian dining increasingly work outside the coasts. Expect more South Indian rooms in the Rust Belt, more regional concepts in the Sun Belt, and more chefs treating American cities as canvases for the full diversity of the subcontinent.

Butter chicken will not disappear — it remains a gateway and a comfort. But it is no longer the whole story. Across America's smaller cities, the menu is finally catching up to the map of India itself."""

articles.append({
    'headline': "Beyond Butter Chicken: Regional Indian Dining Lands in America's Heartland",
    'subheadline': "From a Tamil dosa house in Rochester to a regional kebab program in Phoenix, ambitious Indian restaurants are moving inland and going specific.",
    'body': a2_body,
    'sources': [
        "azcentral / Arizona Republic — Michelin-recognized Chicago Indian restaurant NADU to make Phoenix debut (Sujan and Pujan Sarkar, regional kebab program)",
        "Democrat and Chronicle — Dakshin Indian Cuisine to open in Rochester (Vimala Mohanraj, Tamil Nadu cuisine, dosas, Kerala parotta)",
        "The Indian EYE — 'Rishtedar' opens doors to Indian food and culture in Miami (Vikram Thadani, Chile origin, Wynwood)",
        "Restaurant Business — The year of redefining Indian food in America"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=["Dosa", "Kebab"],
        topics_commons=["masala dosa South Indian", "seekh kebab Indian", "South Indian thali"],
        topics_pexels=["dosa South Indian food", "Indian kebab platter"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 3 — Next-Gen Indian: Cuisine of the Year goes CPG
# ─────────────────────────────────────────────────────────────
print("\n\U0001f4dd Article 3: Next-Gen Indian named cuisine of the year")
a3_body = """When a food-trend agency crowns a "cuisine of the year," it is making a bet on the American grocery cart. For 2026, the creative insights firm Carbonate handed the title to "Next-Gen Indian" — and the evidence is no longer confined to restaurant menus. It is on the chip shelf, in the soda cooler, and across the center aisles of mainstream American supermarkets. Indian flavor has become a packaged-goods category, and the diaspora is watching its grandmother's spice box get reborn as a marketing strategy.

The shift is measurable. Indian food is now among the fastest-growing global cuisines in the United States, and the appetite has pulled Indian flavors out of restaurants and into the hands of America's biggest consumer brands.

## Context & Background

The logic behind Carbonate's pick is demographic. The Indian-American population has more than doubled over the past two decades, and that growth has been accompanied by a proliferation of Indian restaurants exposing mainstream consumers to far more than tikka masala. Leith Steel, the firm's head of insights, argues that global flavors are also becoming more specific — Americans increasingly want to know a dish is Indian, Malaysian, or Peruvian, not vaguely "Asian." Indian cuisine, with its enormous regional range and built-in story, is ideally suited to that hunger for specificity.

Crucially, the trend is arriving at a moment when American shoppers are primed for bold, functional, plant-forward food. Indian cooking — vegetable-heavy, spice-driven, and rich in legumes — fits the cultural mood almost perfectly, which is why packaged-goods companies are racing to bottle it.

## Current Developments

The roster of products tapping the trend reads like a tour of the modern American supermarket. PepsiCo's Lay's has rolled out Masala-flavored potato chips — a fusion of cumin, coriander, turmeric, and pepper — as part of its Global Flavors lineup, while its Miss Vickie's line has tested a Tandoori BBQ chip. The beverage start-up Bollygood is selling sparkling lemonades and limeades infused with unmistakably Indian flavor pairings: pomegranate cardamom, mango turmeric, basil cumin, and ginger mint.

The pattern extends well beyond snacks. Frozen and refrigerated Indian entrées from brands like Deep Indian Kitchen now sit in mainstream freezers, and private-label lines such as Target's Good & Gather carry chicken tikka masala, chana masala, and tikka masala simmer sauces at everyday prices. What was once sold only in the back corner of a desi grocery is now a category that buyers at PepsiCo and Target actively court.

## Diaspora Impact

For Indian-Americans, the CPG wave lands somewhere between pride and ambivalence. On one hand, seeing turmeric and masala normalized on a Lay's bag is a kind of cultural arrival — proof that the flavors of home are mainstream enough to move volume for a $14 billion snack division. The functional-food halo around Indian staples like turmeric, lentils, and ghee has only accelerated that acceptance.

On the other hand, the diaspora has watched this movie before, when "curry powder" flattened a thousand regional masalas into a single yellow tin. The worry is that "Next-Gen Indian," in the hands of marketers, becomes another beige approximation — a tikka-masala-flavored everything that bears little resemblance to the food families actually cook. The brands that win the diaspora's trust will be the ones that treat Indian flavor as a cuisine to be honored, not a trend to be strip-mined.

## What's Next

Expect the shelf to get more specific. Having proven that Americans will buy a masala chip, brands are likely to push toward regional flavors, dosa batters, chutneys, and spice blends that name their origins. The challenge — and the opportunity — is authenticity at scale: delivering genuine flavor through industrial production without losing the soul that made the cuisine worth copying.

For now, the verdict is in. Indian food's American moment is no longer a restaurant phenomenon or a diaspora secret. It is a line item in the strategy decks of the country's largest food companies — and a permanent fixture on the shelves where America actually shops."""

articles.append({
    'headline': "Masala on the Chip Aisle: Why 'Next-Gen Indian' Was Named America's Cuisine of the Year",
    'subheadline': "From Lay's Masala chips to Bollygood sodas, Indian flavor has jumped from restaurant menus to the center aisles of mainstream US supermarkets.",
    'body': a3_body,
    'sources': [
        "Food Processing — 2026 Flavor and Ingredient Trends (Carbonate names 'Next-Gen Indian' cuisine of the year; Lay's Masala, Miss Vickie's Tandoori BBQ, Bollygood)",
        "PepsiCo — Lay's brings global flavors including Masala to the US (cumin, coriander, turmeric, pepper)",
        "Target Good & Gather — chicken tikka masala, chana masala, tikka masala sauce private-label listings; Deep Indian Kitchen frozen entrées",
        "Retail Dive / Datassential — Indian among fastest-growing US cuisines; Indian-American population doubling"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=[],
        topics_commons=["Indian spices masala bowls", "potato chips snack", "Indian spice market colorful"],
        topics_pexels=["Indian spices colorful bowls", "assorted spices market"])
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
    "An elegant Indian restaurant dining room, the polished hospitality British groups bring to New York",
    "A South Indian masala dosa, the regional cooking spreading beyond America's coastal cities",
    "Colorful Indian spices, the flavors now reaching mainstream US supermarket shelves"
]
for art, cap in zip(articles, caps):
    if art.get('image_url'):
        art['image_caption'] = cap

# ── Insert inline embeds into body (before Diaspora Impact) ──
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
