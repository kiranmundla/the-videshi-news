#!/usr/bin/env python3
"""
Food Writer — June 18, 2026
3 food articles for The Videshi
1. Vikas Khanna's Bungalow wins Michelin Bib Gourmand (named chef → Wikipedia)
2. Keralan cuisine is America's "Cuisine to Know for 2026" — Kidilum, Chatti
3. High-protein desi food: how India's fitness culture is rewriting the dosa
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
# ARTICLE 1 — Vikas Khanna / Bungalow Bib Gourmand
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 1: Vikas Khanna Bungalow Bib Gourmand")
a1_body = """For a chef who has held eight Michelin stars across a career that began in the roofless kitchens of Amritsar, an award for value-for-money cooking might seem like a step down. Vikas Khanna does not see it that way. When his New York restaurant Bungalow received the Michelin Guide's Bib Gourmand distinction, the chef wept on Instagram.

"While I've previously received the Michelin Star 8 times, today felt different," Khanna wrote. "I felt that it was for some higher purpose, it was like a tribute, it was like a promise to my land and to my people. To my sister."

## Context & Background

Bungalow opened on March 23, 2024 — the birthday of Khanna's late sister Radhika, who died in 2022 — in partnership with restaurateur Jimmy Rizvi of the Bombay House hospitality group. Set in a space styled after a British Raj-era club, with pale pink walls, colorful murals and a crafted bar, the restaurant was conceived as a love letter to India's bygone club culture and, more personally, to the family Khanna lost.

The chef's journey is the stuff of diaspora legend. From a boy in Amritsar bullied for choosing cooking over cricket, to a stint in a New York homeless shelter, to cooking for Barack Obama, Narendra Modi and the Dalai Lama — Khanna has spent four decades arguing for the seriousness of Indian food on the world's most demanding stages. His earlier Manhattan restaurant, Junoon, held a Michelin star for eight consecutive years.

## Current Developments

The Bib Gourmand — Michelin's nod to restaurants offering exceptional cooking at moderate prices — arrives as Bungalow consolidates a remarkable run. Earlier this year the restaurant was named to the New York Times' list of the 50 best restaurants in America, and it has drawn a steady stream of A-list patrons: Priyanka Chopra and Nick Jonas dined there, with Chopra thanking the chef for "a taste of home," and New York City Mayor Zohran Mamdani broke his Ramadan fast at Bungalow over a meal Khanna cooked personally.

The Michelin Guide singled out Bungalow's contemporary Indian cooking, which draws across the culinary traditions of India's 28 states. Standout dishes include an indulgent five-cheese kulcha and yogurt kebabs wrapped in crisp kataifi pastry, served with pickled cabbage puree and spicy mango coulis. The bar leans into the theme with turmeric-infused tequila and chili-infused mezcal.

## Diaspora Impact

For Indian-Americans, Bungalow has come to function as more than a restaurant. Khanna has framed it explicitly as a bridge — "the central force of connecting the diaspora and connecting the Western world to India." The Bib Gourmand recognition matters in that context because it certifies not a rarefied tasting menu but the kind of food a diaspora family might actually eat: generous, regional, rooted in memory rather than spectacle.

"I have never seen this level of patronage for Indian culture and cuisine in four decades," Khanna told Robb Report India of Bungalow's first year. The restaurant's success has become a point of pride for NRIs who grew up watching the West dismiss their food as cheap takeaway, and who now watch global icons fly into New York specifically to eat it.

In an emotional post following the award, Khanna addressed a younger generation directly: "To all those kids who are watching this moment, this is for you. I chose a profession that was completely against the norms in the 1980s. I continued to be bullied and shamed... The only thing that kept me going was a mission and vision to create a community around Indian cuisine."

## What's Next

Bungalow's recognition lands in what the restaurant industry is calling the year of redefining Indian food in America, with Michelin stars, James Beard nods and high-profile openings clustering across New York, Chicago and beyond. For Khanna, the trajectory points toward further cementing Indian cuisine as fine dining's equal rather than its bargain alternative.

"This is just the beginning," he wrote. "We will work harder & harder everyday to give our guests an experience that will be a testament to Indian hospitality." For a chef who has spent his life insisting the world take Indian food seriously, the tears were not for the award itself — but for how far the cuisine, and its diaspora, have come."""

articles.append({
    'headline': "Vikas Khanna's Bungalow Wins a Michelin Bib Gourmand — and the Chef Wept",
    'subheadline': "The eight-time Michelin-starred chef calls the value-dining honour for his New York restaurant a tribute to his late sister and a promise to the diaspora.",
    'body': a1_body,
    'sources': [
        "Indian Food Times — Chef Vikas Khanna's Restaurant Bungalow Earns Michelin Bib Gourmand Award (June 2026)",
        "The Indian Eye — Chef Vikas Khanna's restaurant Bungalow wins Michelin Bib Gourmand (Vikas Khanna Instagram statements)",
        "Robb Report India — Vikas Khanna's NYC Bungalow Celebrates Indian Culinary Art",
        "LatestLY / ANI — Vikas Khanna Hosts NYC Mayor Zohran Mamdani for Iftar at Bungalow"
    ],
    'embeds': ["https://www.instagram.com/p/DV5JQkHD2Hj/?utm_source=ig_web_copy_link"],
    'img': dict(
        topics_wiki=["Vikas_Khanna"],
        topics_commons=["Vikas Khanna chef"],
        topics_pexels=[])  # named person — Wikipedia/Commons only
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 2 — Keralan cuisine, Cuisine to Know 2026
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 2: Keralan cuisine wave")
a2_body = """For decades, "Indian food" in America meant a flattened compromise — a menu of butter chicken, naan and tikka masala that owed more to Punjab and the British curry house than to the subcontinent's staggering regional range. That map is being redrawn, and the newest territory comes from the country's southwestern tip. Kerala, the slim coastal state of backwaters, coconut groves and toddy shops, is having its American moment.

The food intelligence platform Datassential named Keralan food its "Cuisine to Know for 2026," reporting that 39 percent of U.S. consumers are now interested in trying it — a striking number for a regional cuisine most Americans could not have placed on a map five years ago.

## Context & Background

Keralan cooking is built on ingredients that read like a wellness manifesto written centuries early: seafood, rice, coconut in every form, and a pantry of curry leaves, turmeric, black pepper and the pungent, savory funk of asafoetida. It is veggie-forward, often lighter than the cream-heavy North Indian dishes Americans know, and deeply tied to place — the Malabar Coast's spice trade made this corner of India a global crossroads long before "fusion" was a menu word.

For the Malayali diaspora, the cuisine has always meant home. What has changed is that the rest of America is now lining up for it. The shift is part of a broader appetite for regional Indian specificity, with analysts also flagging Goan, Naga and Himalayan cuisines as the next flavors to watch.

## Current Developments

New York has become the proving ground. In late February, chef Vinu Raveendran opened Kidilum — "beyond awesome" in Malayalam — in Flatiron, fulfilling what he calls a lifelong dream of bringing his home-state dishes to the city with rigorous attention to traditional spice blends. The menu runs to podi idli, paper podi dosa, vella lamb korma, Thalassery biryani and black Calicut halwa, with a cocktail program built on South Indian filter coffee and tamarind.

"When I crave Indian food, I always crave South Indian food because it's where I'm from," Raveendran told Resy. "This is my dream come true."

He is not alone. Chef Regi Mathew, whose Kappa Chakka Kandhari became a blockbuster in Chennai and Bengaluru, has brought Kerala's toddy-shop cuisine to New York with Chatti. Mathew and his team spent three years researching the project — visiting 300 homes and 100 toddy shops, testing 800 recipes — to capture the state's micro-cuisines. His signature Malabar Mutton, dry-fried with black pepper and curry leaves, has become the dish critics cite as the truest ambassador of the genre, with mains priced comparably to Michelin-starred peers like Semma.

## Diaspora Impact

For South Indian families abroad, the arrival of serious Keralan restaurants corrects a long imbalance. Generations of Malayali, Tamil and other South Indian immigrants watched American "Indian" menus default to the North, leaving them to cook appams and fish moilee at home or drive hours to a community joint. Now the food of their childhood is being plated with white-tablecloth ambition and reviewed in mainstream press.

There is also a quiet act of education embedded in these rooms. Chatti hands diners printed menu cards with visuals of each "touching" — the small dishes that anchor toddy-shop eating — and lists suggested pairings, deliberately working to dispel the notion that all Indian food is fiery. Mathew has made it his mission: "I'm proud of my culture, and I want to present it to the global market."

## What's Next

Beyond the flagship restaurants, the trend is spreading through pop-ups, supper clubs and casual spots far from the coasts — from a Kerala-focused lounge in Aurora, Illinois, to curated regional dinners across Europe. If Datassential's read is right, 2026 is the year Keralan dishes migrate from diaspora kitchens to mainstream menus, and the year "Indian food" in America finally starts to mean something more precise.

For NRIs who have spent years explaining that their food is not one thing but a hundred, the recognition is overdue — and delicious."""

articles.append({
    'headline': "Kerala's Moment: America Discovers the Malabar Coast on Its Plate",
    'subheadline': "Datassential named Keralan food its 'Cuisine to Know for 2026' as New York restaurants like Kidilum and Chatti bring toddy-shop cooking to the mainstream.",
    'body': a2_body,
    'sources': [
        "The Food Institute — Regional Indian Cuisines: The Next Big Global Flavor Trend (Datassential 'Cuisine to Know for 2026')",
        "Resy / Right This Way — Kidilum Brings the Malabar Coast to Manhattan (Feb. 27, 2026)",
        "The Nod Mag — Chatti is the newest Kerala-centric Indian restaurant in New York City (Chef Regi Mathew)",
        "The Indian Eye — Chatti Brings Kerala Cuisine to a Global Audience"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=["Kerala_cuisine", "Sadya"],
        topics_commons=["Kerala sadya banana leaf meal", "Kerala fish curry coconut", "Appam Kerala dish"],
        topics_pexels=["South Indian meal banana leaf", "coconut curry seafood Indian"])
})

# ─────────────────────────────────────────────────────────────
# ARTICLE 3 — High-protein desi food / fitness culture
# ─────────────────────────────────────────────────────────────
print("\n📝 Article 3: High-protein desi food")
a3_body = """The dosa, that lacy fermented crepe perfected over centuries in South India, delivers about seven or eight grams of protein. For a new generation of Indian home cooks and the diaspora that follows their reels, that is no longer enough. Across Instagram and YouTube, a wave of "high-protein" Indian cooking is remaking the country's most beloved staples — and reframing how desi food fits into a fitness-obsessed life abroad.

The breakout example is the Protein Dosa, a batter that folds moong dal, urad dal and a scoop of unflavored protein powder into the traditional rice-and-dal base, pushing a single serving to roughly 20 grams of protein. Paired with a paneer egg bhurji, the meal clears 35 grams — gym-bro territory, served on a banana leaf.

## Context & Background

The trend is the collision of two forces. India's urban fitness culture has exploded, with gym memberships, marathon participation and protein-tracking apps surging among young professionals. At the same time, the social-media food internet has industrialized recipe innovation: a clever twist on a classic can rack up millions of views in days, and creators are racing to "optimize" comfort food for macros.

The Protein Dosa was popularized by fitness influencer Ranveer Allahbadia, whose video on a high-protein Indian breakfast has been viewed more than 20 million times. He is one node in a sprawling network of creators reengineering Indian staples — the Baked Oats Chaat (a savory baked-oats square dressed with the full chaat arsenal of chutneys and sev) reportedly drew 12 million views in its first week for Bangalore creator Ananya Bhatt, who said she devised it to feed her kids more protein and fiber without deep-frying.

## Current Developments

The genre keeps multiplying. There are paneer-stuffed parathas reframed as muscle food, besan (gram flour) cheelas marketed as the Indian protein pancake, and sprouted-moong chaats sold as post-workout fuel. Even indulgent fusions get the treatment: Tandoori Paneer Momos — a Delhi street mashup of paneer tikka and dumplings, amplified by vlogger Gaurav Wasan — trade partly on paneer's protein density, with a typical platter delivering well over 40 grams.

What unites them is a deliberate inversion of an old anxiety. For years, Indian food carried a reputation, fair or not, for being heavy, oily and carb-loaded — white rice, fried snacks, ghee-rich gravies. The new cohort of cooks is arguing the opposite: that with paneer, dal, sprouts, yogurt and besan, the Indian pantry is one of the world's richest sources of vegetarian protein, and always has been.

## Diaspora Impact

For NRIs, the movement solves a specific tension. Many in the diaspora juggle a cultural attachment to home cooking with the macro-counting, high-protein eating norms of American gym and wellness culture. The Protein Dosa and its cousins let them have both — a breakfast that tastes like Amma's kitchen and fits a lifting program, without defaulting to chicken breast and a Western protein shake.

The recipes also travel well through exactly the channels the diaspora already lives in: Instagram reels, YouTube Shorts and WhatsApp forwards. A graduate student in Texas or a software engineer in New Jersey can watch a 30-second clip, swap in ingredients available at the local Patel Brothers, and recreate the dish that week. For families raising kids abroad, the "sneak more protein and fiber into familiar food" framing offers a way to keep children eating Indian rather than drifting to nuggets and pasta.

## What's Next

Food-trend analysts already see the high-protein, functional angle migrating from home kitchens into packaged goods and restaurant menus — chai-spiced protein bars, ready-to-cook protein dosa batters, and "swavory" snacks that pair Indian spice with macro-friendly marketing. The broader narrative, that Indian food is healthy, plant-forward and protein-dense rather than indulgent, is becoming a selling point for the cuisine's mainstream ascent in America.

For the diaspora, the deeper appeal is identity. The high-protein dosa is not an abandonment of tradition but a negotiation with it — proof that the food of home can keep up with the life you are actually living, thousands of miles away."""

articles.append({
    'headline': "The 20-Gram Dosa: How India's Fitness Boom Is Rewriting Comfort Food",
    'subheadline': "Protein dosas, paneer egg bhurji and besan cheelas are going viral as a new generation reengineers Indian staples for a macro-counting, gym-going diaspora.",
    'body': a3_body,
    'sources': [
        "Daily Tips — Viral Indian Recipes of 2026: From Baked Oats Chaat to Tandoori Paneer Momos (Protein Dosa, Ranveer Allahbadia/BeerBiceps)",
        "Food Network — Experts Predict 6 Food Trends You'll See Everywhere in 2026 ('swavory' snacking)",
        "Agro Spectrum India — Indian food revolution in America: Street, fine dining and beyond"
    ],
    'embeds': [],
    'img': dict(
        topics_wiki=["Dosa", "Masala_dosa"],
        topics_commons=["Masala dosa South Indian", "paneer bhurji Indian dish", "dosa breakfast plate"],
        topics_pexels=["dosa South Indian breakfast", "Indian paneer healthy meal protein"])
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
    "Chef Vikas Khanna, whose New York restaurant Bungalow won a Michelin Bib Gourmand",
    "A traditional Kerala sadya feast served on a banana leaf, the cuisine America is discovering",
    "A South Indian dosa, the staple being reengineered into a high-protein meal"
]
for art, cap in zip(articles, caps):
    if art.get('image_url'):
        art['image_caption'] = cap

# ── Insert inline embeds into body (after first major section) ──
for art in articles:
    embeds = art.pop('embeds', [])
    if embeds:
        # place first embed after the "## Current Developments" section's first paragraph
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
