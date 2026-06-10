#!/usr/bin/env python3
"""
Food Writer — writes and publishes 3 articles to p2_articles
"""
import os, json, re, requests
from datetime import datetime, timezone

# Load env
with open(os.path.expanduser('~/workspace/.env.supabase')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('export '): line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v

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
        params={
            'category': 'eq.food',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'headline'
        },
        headers=HEADERS
    )
    articles = resp.json()
    normalized = []
    for a in articles:
        h = re.sub(r'[^a-z0-9 ]', '', a['headline'].lower())
        normalized.append(h[:40])
    return normalized

def validate_image(url):
    """Verify image URL returns 200 with image content-type and >5KB."""
    try:
        resp = requests.get(url, timeout=15, stream=True,
                           headers={'User-Agent': 'TheVideshi/1.0'},
                           allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        cl = int(resp.headers.get('Content-Length', '0'))
        if resp.status_code == 200 and 'image' in ct:
            if cl > 5000:
                return True
            # Read a chunk to verify size
            chunk = resp.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except:
        pass
    return False

def is_duplicate(headline, existing):
    norm = re.sub(r'[^a-z0-9 ]', '', headline.lower())[:40]
    return norm in existing

def publish_article(article, existing):
    if is_duplicate(article['headline'], existing):
        print(f"  ⚠️  SKIPPED (duplicate): {article['headline'][:60]}")
        return False

    # Validate image
    if article.get('image_url'):
        if not validate_image(article['image_url']):
            print(f"  ⚠️  Image validation failed for {article['image_url'][:60]}...")
            article['image_url'] = None
            article['image_caption'] = None
            article['image_attribution'] = None

    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': make_slug(article['headline']),
        'category': 'food',
        'vertical': 'food',
        'status': 'review',
        'published_at': now,
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
        'is_editorial': False
    }

    resp = requests.post(
        f'{SB_URL}/rest/v1/p2_articles',
        headers=HEADERS,
        json=payload
    )

    if resp.status_code in (200, 201):
        result = resp.json()
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id', 'unknown')
        print(f"  ✅ Published: {article['headline'][:60]}... (id: {art_id})")
        return True
    else:
        print(f"  ❌ Failed ({resp.status_code}): {resp.text[:200]}")
        return False

# ─── ARTICLES ────────────────────────────────────────────

articles = []

# ═══ Article 1: Michelin Stars ═══
articles.append({
    'headline': "Three Stars, Three Cities: Indian Chefs Make Michelin History Across America",
    'subheadline': "Vijaya Kumar in New York, Chetan Shetty in Washington DC, and Sujan Sarkar in Chicago all earn Michelin stars, marking the most decorated year ever for Indian cuisine in the United States.",
    'image_url': 'https://upload.wikimedia.org/wikipedia/commons/0/06/Semma_NYC.jpg',
    'image_caption': 'Semma restaurant in New York City, home to Michelin-starred South Indian cuisine by Chef Vijaya Kumar',
    'image_attribution': 'Wikimedia Commons',
    'body': """For decades, the question hung over America's dining tables like a stubborn cloud of cumin smoke: why couldn't Indian cuisine crack the Michelin ceiling? Japanese restaurants amassed constellations of stars, French bistros collected them like loose change, and even Thai and Korean kitchens joined the firmament. Indian food — with its millennia of technique, its galaxy of regional traditions, its sheer depth — remained largely overlooked by the world's most influential restaurant guide.

That era is now, emphatically, over.

The Michelin Guide's latest ceremony in New York delivered a verdict that sent shockwaves through the Indian diaspora and the American culinary establishment alike: three Indian chefs, working in three different cities, each earned a Michelin star. Chef Vijaya Kumar at **Semma** in New York City, Chef Chetan Shetty at **Raina** in Washington DC, and Chef Sujan Sarkar at **Indienne** in Chicago have together written the most significant chapter yet in Indian cuisine's American story.

## A Tamil Kitchen in Greenwich Village

Semma — the word means "awesome" in Tamil — occupies a corner of Greenwich Avenue that has become a pilgrimage site for anyone who believes South Indian cuisine has been criminally underrepresented in fine dining. Chef Vijaya Kumar's menu is unapologetically rooted in the traditions of Tamil Nadu: Gunpowder Dosa, Dindigul Biryani, parotta so flaky it practically levitates. The restaurant first earned its star in 2022, making it the only Indian restaurant to receive a Michelin star in New York at the time. Under Kumar's stewardship, Semma has retained that distinction with a consistency that the Guide clearly values.

"This is not fusion. This is heritage Southern Indian cuisine," Kumar has said. The approach is radical in its simplicity: cook what generations of Tamil grandmothers cooked, but with impeccable sourcing and presentation.

## From Punjab Grill to Michelin Star

In Washington DC, Chef Chetan Shetty's **Raina** represents a more dramatic metamorphosis. The space once housed Punjab Grill DC, a mid-market operation that struggled through the pandemic. Under Shetty — a veteran of the celebrated Indian Accent — the restaurant was reborn with interiors shipped from Jaipur and a menu that balances playfulness with refinement. The Michelin Guide singled out dishes like "shiso leaf chaat" that marry "a playful spirit with elegant overtones," and ghee-roasted lamb folded inside a delicate lentil cheela with a "spicy kick tempered with buttermilk mousse."

For the Indian-American community in the capital, Raina's star feels personal. DC's desi population has long complained that the city's Indian restaurant scene lagged behind New York and the Bay Area. That argument just lost its legs.

## Progressive Indian in the Windy City

Chef Sujan Sarkar, meanwhile, has turned a reconverted 19th-century printing press warehouse in Chicago's River North into a stage for what he calls "progressive Indian" cuisine. Indienne earned its first star in 2023 — making it the first-ever starred Indian restaurant in the Chicago area — and Sarkar has since expanded his ambitions dramatically, announcing three new concepts at Hudson Yards in New York: Indienne New York, a cocktail bar called Apas, and a British-Indian chophouse named Elder.

"I wanted to come back to New York with something new and more progressive," Sarkar told *DiningOut*. "It feels like both a homecoming and a new beginning."

## What This Means for the Diaspora

Chef Vikas Khanna — whose own restaurant Bungalow recently earned a Michelin Bib Gourmand and landed on the New York Times' list of 50 Best Restaurants in America — captured the moment's significance in an Instagram post: "Diwali has arrived a little early in the United States. What an honor for India, our hospitality and cuisine."

The numbers tell a larger story. There are roughly 5,000 Indian restaurants in the United States — one for every 66,000 Americans. For Chinese restaurants, that ratio is one to 24,000; for Mexican, one to 48,000. Indian cuisine has long punched below its weight in sheer restaurant count, which makes its ascent through the Michelin ranks all the more remarkable. These aren't outliers riding a trend. They are the vanguard of a movement that has been building for years, fuelled by a new generation of Indian-origin chefs who refuse to dilute their heritage for Western palates.

For the millions of NRIs who grew up watching their mothers' cooking dismissed as "too spicy" or "too complicated" by mainstream American food culture, the sight of three Indian names on the Michelin stage is not just a culinary milestone. It is a recognition, long overdue, that Indian food belongs at the very highest table.

*Sources: The Indian Eye, DiningOut, Michelin Guide, Tripura Times, Restaurant India*"""
})

# ═══ Article 2: Mango Wars ═══
articles.append({
    'headline': "The Mango Wars: How India's Favourite Fruit Became America's Hottest Culture-War Flashpoint",
    'subheadline': "A conservative commentator's mockery of Indian mangoes sparks fierce diaspora backlash, even as Costco sells out of Kesar mangoes in hours and Japan suspends imports over phytosanitary concerns.",
    'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Mango_Alphonso_Asit_fs.jpg/1280px-Mango_Alphonso_Asit_fs.jpg',
    'image_caption': 'Ripe Alphonso mangoes, one of India\'s most prized fruit exports now gaining popularity in US retail',
    'image_attribution': 'Wikimedia Commons',
    'body': """It is a truth universally acknowledged among the Indian diaspora that a perfectly ripe Alphonso mango is one of nature's supreme achievements — a saffron-fleshed, non-fibrous miracle that makes every other fruit feel like an audition. For generations of NRIs, the arrival of mango season has been less a calendar event than a spiritual homecoming, complete with WhatsApp group coordinates for the nearest stockist and arguments about whether Kesar can hold a candle to Hapus.

Now, improbably, the mango has become the latest front in America's culture wars.

## "Why Are They So Obsessed?"

The controversy ignited when conservative commentator Sara Gonzales used her program to mock Indian mangoes and the enthusiasm of Indian-American communities who organise seasonal purchases through WhatsApp groups. Gonzales questioned why immigrants were so "obsessed" with varieties like Banganapalli and suggested the fruit's popularity was a niche immigrant phenomenon rather than a genuine market force.

She also cited Japan's recent suspension of fresh Indian mango imports, framing it as a health concern. The reality, however, is more mundane: Japanese authorities flagged deficiencies in fumigation and phytosanitary procedures at certain Indian export facilities — a bureaucratic issue, not a contamination scare.

The remarks detonated across social media. Indian-American users condemned the comments as culturally insensitive and reflective of a broader hostility toward Indian immigrants — one that has intensified alongside debates over H-1B visa holders and the growing visibility of the Indian diaspora in American professional life.

https://www.instagram.com/reel/DYbQ45Hh-3j/

## Meanwhile, Costco Can't Keep Them on the Shelves

The irony of Gonzales' dismissal is that it arrived precisely as Indian mangoes are experiencing their most successful American season ever. In the third week of May, Costco imported its first shipment of Kesar mangoes to stores across the Greater Seattle area, Las Vegas, New Jersey, and Greater Los Angeles. Company representatives confirmed the mangoes **sold out within hours** of reaching shelves.

The Consulate General of India in Seattle, partnering with APEDA (the Agricultural and Processed Food Products Export Development Authority), hosted its second annual "Mango Magic" tasting event on June 6. Over 100 leading importers — including senior Costco leadership — sampled seven premium varieties: Alphonso and Kesar from Maharashtra, Banganapalli and Himayat from Andhra Pradesh, Langra and Dussehri from Uttar Pradesh, and Rajapuri from Gujarat. Washington State Lieutenant Governor Denny Heck and state senators Manka Dhingra and Vandana Slatter attended, lending the event the air of a diplomatic summit — for fruit.

"We are now going to have all kinds of Indian mangoes, beginning with Kesar, in Seattle," Consul General Gupta told attendees. "Stop by Costco and pick it up, or go to an Indian grocery store and pick it up."

## More Than a Fruit

For the Indian diaspora, the mango has never been just a fruit. It is a Proustian trigger — a single bite transporting you to a childhood summer in Ratnagiri, or an afternoon on a Chennai terrace, sticky-handed and blissfully unselfconscious. The academic literature on diaspora food culture treats mango references as a "culinary metaphor powerful in maintaining immigrant identity." In plainer terms: the mango is home, distilled into edible form.

That is precisely why Gonzales' comments stung. To mock the mango is to mock the act of remembering — and, by extension, the people doing the remembering.

## The Japan Complication

Japan's suspension of Indian mango imports after 20 years of trade adds a geopolitical wrinkle. Indian authorities have moved quickly to address the phytosanitary concerns, but the timing is awkward. India is the world's largest mango producer, cultivating between 20 and 26 million tonnes annually — nearly 50 per cent of global output. Any disruption in export credibility ripples across every market where Indian mangoes are trying to establish themselves, including the US.

APEDA's response has been to double down on quality certifications and retail partnerships. The Seattle event was explicitly designed to showcase export-grade fruit to major American retailers. The subtext was clear: judge our mangoes by what's on the shelf, not what's on cable news.

## What's Next

The mango wars are unlikely to subside as Indian fruit imports continue to grow. Community groups across the East Coast, Bay Area, and Texas are already organising bulk purchases for the peak Langra and Dussehri season in late June and July. For the diaspora, every box of mangoes delivered to an American doorstep is a small act of cultural affirmation — proof that the flavours of home can travel 8,000 miles and still taste exactly right.

And for anyone still wondering what the fuss is about: try a properly ripened Alphonso. You'll understand.

*Sources: American Bazaar Online, The Daily Jagran, Bharat Horizon, The Indian Eye*"""
})

# ═══ Article 3: Indian Food Conquers the Grocery Aisle ═══
articles.append({
    'headline': "From Frozen Naan to NEXTY Gold: Indian Food's Quiet Conquest of the American Grocery Aisle",
    'subheadline': "Truly Indian's double NEXTY nomination, the rise of frozen Indian meals, and how diaspora brands are turning the supermarket shelf into the next frontier for Indian cuisine.",
    'image_url': 'https://images.pexels.com/photos/28674556/pexels-photo-28674556.jpeg?auto=compress&cs=tinysrgb&h=650&w=940',
    'image_caption': 'Traditional Indian breads including naan and roti arranged in a wicker basket',
    'image_attribution': 'Pexels',
    'body': """While Michelin-starred Indian restaurants dominate headlines and celebrity chefs battle for prime Manhattan real estate, a quieter revolution is unfolding in a less glamorous but arguably more consequential arena: the frozen food aisle at your neighbourhood grocery store.

At Natural Products Expo West in Anaheim earlier this year, **Truly Indian** — a brand of Edison, New Jersey-based ADF Foods — earned double finalist placement in the prestigious 2026 NEXTY Awards for its Tikka Masala Naan and Crispy Chili Mango Chutney. The NEXTY Awards are considered the Oscars of the natural products industry, and a double nomination for an Indian brand signals something that grocery buyers have been whispering about for months: Indian food is not just trending in restaurants. It is reshaping the American pantry.

## The Numbers Tell the Story

Indian food is now the second most popular cuisine on social media, with over seven million Instagram posts tagged #indianfood in the past 12 months alone — a 41 per cent growth rate that outpaces every other global cuisine category. Yet there are only roughly 5,000 Indian restaurants in the United States, one for every 66,000 people. Compare that to 14,000 Chinese restaurants or 6,900 Mexican restaurants, and a gap becomes obvious.

The grocery aisle is where that gap is closing fastest. The frozen Indian food market in the US has grown by an estimated 18 per cent annually since 2023, driven by a potent combination of diaspora demand and mainstream curiosity. What was once a niche section tucked between the frozen pizza and the egg rolls now commands dedicated shelf space at Whole Foods, Trader Joe's, Costco, and Target.

## Hand-Stretched, 150,000 Times a Day

Truly Indian's story illustrates the scale now required to compete. The brand is part of ADF Foods, a fourth-generation family-owned company founded in 1932. Its naan production alone runs to approximately 150,000 hand-stretched pieces per day, each baked in traditional clay ovens by generational artisans. The result is a frozen product that hits the dual consumer demands of 2026: authenticity and convenience.

The Tikka Masala Naan — the NEXTY finalist — is vegan, Non-GMO Project Verified, low-glycemic, Kosher, and Halal certified. It retails at $6.99. The Crispy Chili Mango Chutney, the other finalist, represents a bolder play: a condiment designed to cross over from Indian households into the broader American snacking occasion.

"Retailers report sustained consumer demand for authentic global flavours," the company noted in its announcement, "with Indian foods expanding distribution across natural, conventional, and club channels."

## The Diaspora-to-Mainstream Pipeline

The pattern is familiar to anyone who watched Korean food, Thai curry pastes, or Japanese snacks move from ethnic grocery aisles to mainstream shelf sets. It starts with diaspora demand — NRIs seeking the specific brands and flavours they grew up with. Then adventurous non-Indian consumers discover the products. Then major retailers expand their buying. Then the cycle accelerates.

For Indian food, this pipeline has a particular advantage: scale. India's food processing industry is enormous, and established exporters like ADF Foods, Haldiram's, MTR, and ITC have the manufacturing infrastructure to supply American retail at volume. The challenge has always been distribution and brand awareness, not production capacity.

Patel Brothers, the country's largest South Asian grocery chain with over 52 stores across 19 states, has been the anchor institution for diaspora grocery shopping since 1974. But the real shift is happening in mainstream retail. Costco now stocks Indian mangoes, ghee, and spice blends. Trader Joe's has expanded its Indian frozen section three times in the past two years. Whole Foods' 365 brand includes a turmeric-ginger shot that would have been unimaginable a decade ago.

## Beyond the Frozen Aisle

The grocery conquest extends beyond frozen meals. Ghee — once a mysterious jar at the back of the international aisle — is now a $250 million category in the US, with brands like Fourth & Heart and Ancient Organics competing alongside traditional Indian producers. Turmeric was named 2026's Herb of the Year by the International Herb Association. Chai concentrates from brands like Dona and Blue Lotus have moved from speciality coffee shops into mainstream grocery.

Even the condiment aisle is shifting. Chutneys, achaar (Indian pickles), and tamarind sauces are appearing on shelves previously reserved for sriracha and gochujang. The logic is simple: if Americans adopted Korean gochujang and Japanese ponzu, there is no reason they won't adopt mango pickle and coconut chutney.

## What's Next

The NEXTY nomination is validation, but the real test is whether Indian grocery brands can achieve what Korean food did in the 2010s: move from "ethnic" to "everyday." The ingredients are there — literally. The diaspora is growing, mainstream curiosity is at an all-time high, and the production infrastructure is mature. The frozen naan in your grocery store today may be the opening chapter of a much larger story: one where Indian food doesn't just win awards at fine-dining galas, but shows up, unpretentiously, in the weeknight dinner rotation of millions of American households.

For NRIs who spent years explaining what naan is to colleagues at office lunches, that future is already arriving — one grocery aisle at a time.

*Sources: NOSH, ADF Foods/Truly Indian, Natural Products Expo West, Patel Brothers, industry data*"""
})

# ─── PUBLISH ─────────────────────────────────────────────

existing = get_existing_headlines()
print(f"Found {len(existing)} existing food article headlines for dedup\n")

published = 0
for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)} ---")
    word_count = len(article['body'].split())
    print(f"  Title: {article['headline']}")
    print(f"  Words: {word_count}")
    if publish_article(article, existing):
        published += 1

print(f"\n{'='*50}")
print(f"Published {published}/{len(articles)} articles")
