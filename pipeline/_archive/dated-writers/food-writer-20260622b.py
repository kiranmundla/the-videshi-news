#!/usr/bin/env python3
"""
Food Writer — June 22, 2026 (evening run)
3 food articles for The Videshi:
1. Drāvida NYC — Aarthi Sampath's East Village restaurant of the "double diaspora" (Indo-Caribbean/Indo-African)
2. Masala chai goes mainstream in America — the $5bn+ chai latte economy and the diaspora's reclaiming of it
3. Dosa Belt expands — South Indian regional cuisine (Dakshin, NADU) breaking out beyond butter chicken in US metros
"""
import os, re, requests, subprocess
from datetime import datetime, timezone

# Load env
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
                'limit': 30, 'select': 'headline,slug'},
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
        "headline": "The Double Diaspora Plates Up: A Chopped Champion Brings Trinidad, Durban and Guyana to the East Village",
        "subheadline": "At Drāvida, chef Aarthi Sampath traces Indian food along the indenture routes that carried it to the Caribbean, Africa and Southeast Asia — arguing that the diaspora's table is far bigger than butter chicken.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Doubles_%28Food%29%2C_Trinidad_%26_Tobago.jpg/1280px-Doubles_%28Food%29%2C_Trinidad_%26_Tobago.jpg",
        "image_caption": "Doubles, the Trinidadian street snack of curried chickpeas in fried bara bread, born of the Indo-Caribbean indenture diaspora",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "PR Newswire / lifestyle.side.cr — Drāvida Debuts in NYC's East Village with a Fresh Take on Indian and South Asian Diaspora Cuisine (2026)",
            "Drāvida — dravidanyc.com restaurant information (2026)",
            "Food Network — Aarthi Sampath, Chopped Champion and Beat Bobby Flay winner, profile",
            "CookUnity — Chef Aarthi Sampath chef partner page (2026)"
        ],
        "body": """The most familiar story of Indian food abroad is the one the diaspora itself tells: a family boards a plane, opens a restaurant, and teaches a new country to love butter chicken. But there is an older, rougher migration buried beneath that one — the nineteenth-century indenture ships that carried Indian laborers to Trinidad, Guyana, Fiji, South Africa and Malaya. A new East Village restaurant has built its entire menu on that forgotten journey.

Drāvida, which opened this spring at 211 First Avenue in Manhattan, is the first restaurant from chef Aarthi Sampath — a Mumbai-born, New York-trained cook who became a national name through Food Network wins on *Chopped* and *Beat Bobby Flay*. Its premise is deceptively simple and quietly radical: trace Indian flavor not through the kitchens of the homeland, but along the routes its people were scattered across, and plate the result for a New York audience.

## Context & Background

The menu reads like a map of indenture. There are Doubles, the curried-chickpea street snack of Trinidad. There is Oxtail Bunny Chow, the hollowed-bread curry of Durban's Indian South Africans. There is Idli paired with shrimp, nodding to the Indonesia-South India crossing, and Nasi Kandar from the Indo-Malay world. These are dishes that emerged when Indian cooks, far from home and often barred from their old ingredients, improvised with what the new land offered — and in doing so created entirely new cuisines that are neither fully Indian nor fully local.

Sampath wrote the concept in 2019, long before it found a building. "This restaurant is for New Yorkers who haven't seen their food represented — for the communities that built this city and whose cuisines haven't always had a place at the table," she has said. The name Drāvida points south, to the Dravidian linguistic and cultural world of the subcontinent, the wellspring from which much of the indenture-era migration flowed.

## Current Developments

The restaurant occupies two floors of a restored century-old building, complete with original brick ovens, and is paired with a 20-seat downstairs speakeasy named Jam and Jaggery. The cooking, Sampath insists, is the food "more commonly found in homes than restaurants" — adapted for a broader New York audience without being sanded down into the reassuring, cream-heavy template that long defined Indian dining in America.

Sampath's own path lends the project credibility. After moving to the United States from Mumbai in 2013, she trained in serious kitchens — Junoon, The Breslin, the Rainbow Room — before her television breakthrough. Today she also reaches a mass audience through CookUnity, the chef-driven meal service, where she sells roughly 50,000 meals a week across U.S. markets. Drāvida is the bricks-and-mortar argument behind all of it.

## Diaspora Impact

For the Indian diaspora in America, a place like Drāvida lands differently than the latest fine-dining tasting menu. It widens the very definition of who counts as the diaspora. The Indo-Trinidadian whose ancestors left Bihar in the 1880s, the Indo-Guyanese family, the South African of Tamil descent — these are communities often invisible in the dominant NRI narrative of doctors and engineers who arrived after 1965. Seeing their food on a celebrated Manhattan menu is a form of recognition that has been a long time coming.

It also reframes what "authentic" means. Doubles and bunny chow are not corruptions of Indian food; they are Indian food, evolved across a century in another hemisphere. For second-generation kids raised to think the cuisine begins and ends with North Indian gravies, Drāvida is a lesson in just how far the spices traveled — and how much they changed on the way.

## What's Next

Drāvida arrives in what the trade press has called the year of redefining Indian food in America, a moment crowded with British imports and Michelin-chasing regional concepts. Its distinct wager is historical rather than geographic: that the most untold story in Indian cuisine is the one written by the people who never chose to leave.

If the bet pays off, expect the indenture diaspora to become a richer seam for chefs to mine — Fijian-Indian, Mauritian, Surinamese kitchens that have been cooking this fusion for generations without a marquee. For now, in a brick-oven room on First Avenue, a Chopped champion is quietly insisting that the diaspora's table was always bigger than anyone let on."""
    },
    {
        "headline": "Chai's American Hour: How a Roadside Ritual Became a Billion-Dollar Cafe Staple",
        "subheadline": "Masala chai is surging through American cafes and supermarket aisles on a wave of wellness marketing and TikTok virality — and the diaspora is watching its grandmother's drink get rebranded, repriced, and reclaimed.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Masala_Tea_2.jpg/1280px-Masala_Tea_2.jpg",
        "image_caption": "A glass of masala chai, the spiced milk tea now surging through American cafes and grocery shelves",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Verified Market Research — Masala Chai Market size and forecast (cited via VegNews, 2025-2026)",
            "VegNews — More Than Just a Latte, Chai Spice Is a Fall Must for Cooking and Baking (2025)",
            "FoodNavigator — Flavour trends 2026 (matcha and spiced-beverage growth, 2026)",
            "Adventure.com — Why you should think twice about your next matcha latte. And all viral food trends (April 2026)"
        ],
        "body": """Ask anyone who grew up in an Indian household and the image is automatic: a battered steel pot on the stove, milk and water coming to a rolling boil, a fistful of black tea, and the bruised cardamom, ginger and clove that turn it into chai. It was never a luxury. It was the cheapest, most constant punctuation of the day — the cup pressed into your hands at every visit, the drink sold for a few rupees at every railway platform. In America in 2026, that same drink is having a designer moment.

Masala chai — confusingly marketed simply as "chai" in the United States, where the word that just means "tea" has been turned into the name of a single recipe — has become one of the fastest-rising beverages in the American cafe economy. Market researchers peg the global masala chai market well above $5 billion, with projections approaching $10 billion by the early 2030s. The drivers are familiar to anyone tracking the matcha boom: cafe culture, social media virality, and a relentless wellness narrative built around antioxidants, anti-inflammatory spices, and "functional" comfort.

## Context & Background

Chai's American journey has been long and uneven. For years the word evoked the syrupy, over-sweetened "chai tea latte" of mall coffee chains — a powdered or concentrate-based drink that bore only a distant relationship to a stovetop pot in Lucknow or Lahore. The diaspora learned to wince at the redundant phrase "chai tea" and the sugar-bomb version that came with it.

But the broader food culture has shifted. The same forces that turned matcha into a meme-able, ceremonial-grade obsession — its popularity up a reported 87 percent globally — have created an appetite for spiced, photogenic, wellness-coded drinks with a story. Chai fits the brief almost too neatly: warm, aromatic, rooted in centuries of tradition, and naturally loaded with the turmeric, ginger and cinnamon that the West has spent a decade rediscovering as superfoods.

## Current Developments

The result is a chai renaissance that runs from independent cafes to grocery shelves. Tea influencers rack up hundreds of thousands of views demonstrating the proper stovetop method; one widely cited creator's masala chai tutorial passed half a million views. Specialty roasters now treat chai the way they once treated single-origin espresso, fussing over leaf grade and spice ratios rather than reaching for a sugary concentrate. Brands are folding chai spice into everything — lattes, baked goods, ice cream, ready-to-drink cans — as the flavor migrates from the cup into the broader pantry.

It is, in other words, following the exact arc that matcha walked: from niche ethnic ingredient to wellness symbol to mainstream flavor platform. And as with matcha, the boom carries a warning. Reporting on viral food trends has noted how the rush to commodify a traditional drink can strain supply chains and, more subtly, erode the cultural history behind it — reducing a centuries-old ritual to a neon-hued, hashtag-ready product.

## Diaspora Impact

For NRIs, chai's American hour is a bundle of contradictions. There is genuine pride in watching a humble, intimate ritual celebrated on its own terms — and a flicker of irritation at paying six dollars for a smaller, sweeter version of what simmered for free in a childhood kitchen. The drink that once marked the diaspora as different is now, briefly, fashionable.

But the trend has also handed the community a chance to reclaim the narrative. A generation of diaspora founders is launching chai brands that lead with authenticity — real spices, proper brewing, honest labeling that drops the redundant "tea" — and positioning themselves explicitly against the powdered mall version. For them, the wellness wave is not an appropriation to resent but a market to lead, armed with the one thing no trend cycle can manufacture: the actual recipe, passed down rather than reverse-engineered.

## What's Next

Expect chai to consolidate its place as a permanent fixture rather than a passing fad, much as matcha has matured from spectacle into a stable specialty category. The likely next phase is a flight to quality: unsweetened, properly spiced, single-estate offerings that mirror the specialty-coffee playbook, and a premium tier of diaspora-led brands competing on heritage.

The deeper question is who gets to define the drink as it scales. If the answer is the cooks who grew up with the pot on the stove, then chai's American moment will be more than a rebrand — it will be a homecoming, served hot."""
    },
    {
        "headline": "Beyond Butter Chicken: The Dosa Belt Pushes Into America's Second Cities",
        "subheadline": "From a new South Indian flagship in Rochester to a regional-kebab concept landing in Phoenix, chefs are betting Americans are finally ready for the coconut-and-rice cooking of the subcontinent's south — not just the creamy gravies of the north.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Masala_Dosa_with_sambhar.jpg/1280px-Masala_Dosa_with_sambhar.jpg",
        "image_caption": "A masala dosa served with sambar and chutney, the South Indian staple driving a new wave of US restaurant openings",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Democrat and Chronicle — South Indian restaurant opening in Rochester space (Dakshin Indian Cuisine, June 2026)",
            "Arizona Republic / azcentral.com — Michelin-recognized Chicago Indian restaurant to make Phoenix debut (NADU, June 2026)",
            "Restaurant Business — The year of redefining Indian food in America (2026)"
        ],
        "body": """For most Americans, the mental image of "Indian food" still defaults north: butter chicken, garlic naan, the orange-hued tikka masala that British colonialism and post-war immigration carried west. But a quieter culinary front is opening in America's mid-sized cities, where chefs are wagering that diners are finally ready for the other India — the coconut, rice, seafood and fermented batters of the south.

The signal this month came from two very different places. In Rochester, New York, a full-service South Indian restaurant called Dakshin Indian Cuisine is preparing to open in the former Cub Room space on South Clinton Avenue — the second outpost of a concept that debuted in Syracuse last year. And in Phoenix, the Michelin-recognized Chicago restaurant NADU is making its second U.S. appearance with a regional menu designed to push guests well past the familiar.

## Context & Background

What unites the openings is a deliberate rejection of the standard playbook. Dakshin's owner, Vimala Mohanraj, ran North Indian restaurants in Albany and New Jersey before pivoting to the cuisine of her native Tamil Nadu, the subcontinent's southernmost state, which shares a border and a coconut-rich culinary sensibility with neighboring Kerala. "I want to let people know that it is different than butter chicken and garlic naan," she said. Her Rochester menu will showcase dosas — the crisp, fermented-rice crepes of the south — alongside curries built on coconut rather than butter and cream, plus the flaky, griddled Kerala parotta that has become a customer obsession in Syracuse.

NADU, opened in Chicago in spring 2025 by chef Sujan Sarkar, took a different route to the same destination, earning an Eater Best New Restaurant nod, a James Beard semifinalist nomination and a Michelin Bib Gourmand within its first year by championing regional Indian cooking. Its Phoenix location, led by Sarkar's brother Pujan, leans into a pan-regional kebab program — a Galouti from Lucknow, a Chapli from the northwest frontier, a Bihari kebab — explicitly to "help guests understand that Indian food can be different from what they're used to."

## Current Developments

The economics increasingly favor the bet. Mohanraj discovered that a striking share of her Syracuse customers were driving an hour and a half from Rochester for her food — proof of a hungry, underserved market in cities long stuck with a single, Americanized template. Her Rochester space will be larger, with an event room, an Indian bakery corner and a full bar leaning into Indian beers and spirits, and it sits deliberately close to the international student populations of the local universities.

These openings are a grassroots counterpart to the headline-grabbing arrivals reshaping Indian dining at the top end — the British imports and Michelin-starred fine-dining concepts landing in New York and Las Vegas. The second-city dosa houses are doing the same cultural work one strip mall at a time, broadening the American palate in Rochester and Phoenix rather than only in Manhattan.

## Diaspora Impact

For South Indian NRIs in particular, the trend corrects a long-standing imbalance. The diaspora's restaurant scene has skewed Punjabi and Mughlai for decades, leaving Tamil, Telugu, Kannada and Malayali families to recreate sambar, rasam and avial at home or drive hours to the nearest dedicated spot. A proper dosa counter in a mid-sized American city is, for them, both a convenience and a quiet validation that their regional food deserves a storefront of its own.

It also reshapes how the next generation eats. Children raised on the idea that Indian food means a creamy gravy and a basket of naan are growing up with crisp dosas, idli and coconut chutney as everyday options — a fuller, truer picture of a cuisine that was never a monolith.

## What's Next

Expect the regional wave to keep spreading outward from the coasts into the country's second and third cities, following the diaspora's own settlement patterns into the Sun Belt and the Rust Belt alike. The likely winners are operators who, like Mohanraj, treat skepticism as an opportunity — "trust me and give it a try," as she tells wary first-timers — and convert it into loyalty one dosa at a time.

The deeper shift is definitional. Each coconut curry and fermented crepe that lands in a new American city chips away at the notion that Indian food is one thing. In Rochester and Phoenix this summer, the south is making its case — and, increasingly, winning it."""
    }
]


def main():
    print("=== Food Writer 20260622b (evening) ===")
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
