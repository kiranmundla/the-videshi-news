#!/usr/bin/env python3
"""
Food Writer — June 23, 2026 (evening run)
3 food articles for The Videshi:
1. Millet's American breakout — ragi/jowar from forgotten grain to snack-aisle superfood
2. "Don't put me in that box" — the progressive Indian fusion wave (Badmaash, Pataaka, NADU)
3. The all-vegetarian bet — Simply South's 450-item meatless Indian expansion into Houston
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
        "headline": "The Forgotten Grain's Comeback: How Ragi and Jowar Are Storming America's Snack Aisle",
        "subheadline": "Once dismissed as poverty food, India's millets are being reborn in the United States as gluten-free, climate-smart superfoods — and the diaspora is rediscovering the grains its grandparents grew up on.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Ragi_Idli_%28Finger_Millet%29_with_Sambar.jpg/1280px-Ragi_Idli_%28Finger_Millet%29_with_Sambar.jpg",
        "image_caption": "Ragi idli made with finger millet, served with sambar — one of the millet dishes finding a new audience in America",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Bonafide Research — United States Millets Market Overview, 2031 (2026)",
            "Fortune Business Insights — Millet Snacks Market Size, Share, Forecast 2026-2034 (2026)",
            "GlobeNewswire — Millet Based Packaged Food Market Report 2026 (Global)",
            "Agro Spectrum India — Can the Americas turn millets from forgotten grains into future staples? (2026)"
        ],
        "body": """For generations, ragi was the grain Indian families ate when they could afford nothing else. Finger millet, jowar and bajra were the staples of the village and the famine year — dense, drought-proof grains that the rising middle class quietly left behind as soon as polished white rice and refined wheat flour became affordable. Now those same grains are arriving in American supermarkets wrapped in the language of wellness, and the diaspora is being asked to pay a premium for what its grandparents once grew in the back field.

The American millet market is in the middle of a sharp, deliberate reinvention. Analysts tracking the category describe finger and pearl millet moving steadily off the health-store fringe and into mainstream breakfast, bakery and snacking aisles, with the broader millet-based snacks market valued near $2.95 billion in 2026 and projected to climb past $4 billion by the early 2030s. The growth is being driven by the same forces reshaping the rest of the American pantry: a hunt for gluten-free grains, high-fiber and high-protein labels, and a story diners can feel good about.

## Context & Background

Millets are not new to America so much as newly fashionable. Brands like Bob's Red Mill and Great River Organic Milling have milled sorghum and finger-millet flour for years, while Nature's Path and Purely Elizabeth have folded pearl and foxtail millet into granola and muesli. What has changed is the framing. India's government spent 2023, the International Year of Millets, aggressively rebranding the grains as "Shree Anna" — nutritious cereals fit for a climate-stressed future rather than a poor man's substitute. That campaign has rippled outward, and millet now arrives in the West pre-loaded with a narrative about sustainability, gut health and low-glycemic eating.

The technology has caught up too. Manufacturers are using extrusion and popping to turn dense, slightly bitter grains like ragi and jowar into puffs, flakes and savory crispies that sit comfortably next to corn and rice snacks on the impulse shelf. That has cracked the old palatability barrier that long kept millets out of the convenience aisle.

## Current Developments

The clearest sign of the shift is in snacking. Ragi crisps, jowar puffs and millet-based namkeen mixes are multiplying across direct-to-consumer storefronts and specialty retailers, with industry reports flagging "Ragi Bites"-style products and kid-friendly millet snacks as fast risers. Bakeries are quietly swapping finger-millet flour into cookies, muffins and pizza crusts, and a wave of California and New York startups is building millet into smoothies, fermented drinks and plant-based protein shakes.

Yet the category still faces real friction. Industry voices, including the founders of millet-focused startups and the North American Millets Alliance, warn that the grains remain boxed in as a narrow gluten-free substitute rather than a mainstream staple. Processing infrastructure is thin, supply can be inconsistent, and much of the available seed was bred for animal feed rather than flavor — leaving texture and taste uneven. Repositioning, infrastructure and consumer education, they argue, are the three shifts millets still need.

## Diaspora Impact

For Indian Americans, the millet revival lands as a strange kind of homecoming. The grains carry deep regional memory — ragi mudde in Karnataka, bajra rotla in Gujarat, jowar bhakri across the Deccan — foods many second-generation kids never tasted because their parents associated them with hardship and left them behind on the journey up. Watching ragi sold as a $9 superfood snack is both validating and faintly absurd.

But it is also an opening. A generation of diaspora founders is uniquely placed to lead the category honestly, with recipes and processing know-how that legacy American brands simply do not have. For families, the trend is a nudge to reach back: to put nutty, mineral-rich millets back on the weeknight table not as a wellness purchase but as a recovered inheritance.

## What's Next

Expect millets to follow the well-worn arc of turmeric and chai — from ethnic-aisle curiosity to functional-food buzzword to permanent pantry fixture — with snacking leading the charge and bakery close behind. The open question is who tells the story as it scales. If the answer includes the cooks who grew up eating these grains, America's millet moment will be more than a rebrand. It will be a long-overdue correction, one puffed ragi crisp at a time."""
    },
    {
        "headline": "Don't Call It a Curry House: The Rule-Breaking Chefs Blowing Up Indian Dining in America",
        "subheadline": "From Punjabi-spiced steak frites in Los Angeles to a reimagined dosa in Midtown Atlanta, a new wave of Indian-American chefs is rejecting the old template — and the diaspora is split between delight and discomfort.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Chicken_Tandoor_Mix_Platter.jpg/1280px-Chicken_Tandoor_Mix_Platter.jpg",
        "image_caption": "A mixed tandoori platter — the kind of familiar Indian dish that a new wave of progressive American chefs is deliberately reinventing",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Restaurant Business Online — The year of redefining Indian food in America (June 2026)",
            "Business Debut — Pataaka Aiming for Late May / Early June Opening in Midtown Atlanta (2026)",
            "Arizona Republic / azcentral.com — Michelin-recognized Chicago Indian restaurant NADU to make Phoenix debut (June 2026)"
        ],
        "body": """For half a century, the American "Indian restaurant" has been a remarkably stable institution: dim lighting, a buffet steam table, a menu anchored by butter chicken, chicken tikka masala and a basket of garlic naan. A growing cohort of Indian-American chefs now wants to take that institution out back and, in the words of one of them, "blow it up with TNT."

That chef is Nakul Mahendro, co-founder of the Los Angeles restaurant Badmaash, which opened its third LA location this month. The name means scoundrel — a term of endearment — and the menu lives up to it: Punjabi-spiced steak frites with paprika-dusted fries, a lamb burger, a bourbon cocktail spiked with Madeira and housemade date jam, and ice cream sandwiches built from Parle-G biscuits, the tea-time staple of every Indian childhood. "Your idea of an Indian restaurant is horrible," Mahendro says of American diners. "Don't put me in that box."

## Context & Background

Badmaash is the loudest voice in what the trade press has dubbed the year of redefining Indian food in America. The movement has been building for years, but 2026 has become its breakout, as a stunning variety of "progressive" Indian concepts move into the spotlight — places that treat the cuisine not as a fixed canon to be reproduced but as a living grammar to be played with.

The shift is generational. The first wave of Indian restaurateurs, often immigrants building a business in an unfamiliar country, leaned into a reassuring, Americanized template because it sold. Their children — raised in two cultures, trained in serious kitchens, fluent in both biryani and the language of fine dining — feel no such obligation. They are mixing regional Indian technique with American formats and ingredients precisely because, for them, that fusion is not a gimmick. It is autobiography.

## Current Developments

The examples are multiplying across the map. In Midtown Atlanta, chef Anish Nair has opened Pataaka, a 113-seat upscale room with a mezzanine and a 14-seat bar, built around small plates and what he calls a "progressive interpretation" rather than fusion — reimagining the dosa, seafood and regional classics with an emphasis on technique and seasonality. In Phoenix, the Michelin Bib Gourmand-winning NADU has opened a second outpost built around a pan-regional kebab program — Galouti from Lucknow, Chapli from the northwest frontier, a signature Bihari kebab — explicitly designed, as chef Pujan Sarkar puts it, to "help guests understand that Indian food can be different from what they're used to."

What unites them is a refusal of the single-template past and a confidence that American diners are finally ready to follow. The cocktail programs lean on turmeric, saffron, curry leaf and tamarind; the dessert menus raid the Indian childhood pantry; the plating borrows from the modern fine-dining playbook. Critics and award juries are rewarding the ambition, with James Beard recognition, Michelin nods and Eater best-new-restaurant lists increasingly going to kitchens that would once have been too unconventional to register.

## Diaspora Impact

For the Indian diaspora, this wave is a source of pride laced with unease. There is genuine joy in watching Indian chefs win on their own terms, free of the apology that once hung over the cuisine. But the boldest experiments also touch a nerve. To some NRIs, a Parle-G ice cream sandwich or a poutine-adjacent Punjabi plate is a clever, loving wink. To others, it edges toward novelty — a worry that the food of their grandmothers is being remixed for a clientele that never knew the original.

The deeper effect is permission. Each rule-breaking restaurant widens the space for the next, and for diaspora kids it models a way of being Indian-American that refuses to choose between heritage and reinvention.

## What's Next

Expect the progressive wave to keep cresting through 2026 and beyond, spreading from coastal flagships into second cities, and expect the debate over authenticity to follow it everywhere. The chefs leading it would say that is the point. Indian food, they insist, was never one thing — and the most faithful tribute to a living cuisine is to keep it moving."""
    },
    {
        "headline": "No Meat, No Compromise: The All-Vegetarian Indian Chains Betting on America's Appetite",
        "subheadline": "As Simply South plans a 450-dish, entirely meatless menu for Greater Houston, India's vegetarian restaurant tradition is quietly proving it can scale in a country obsessed with plant-based eating.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/South_Indian_thali-Saravana_bhawan-New_Delhi-6.jpg/1280px-South_Indian_thali-Saravana_bhawan-New_Delhi-6.jpg",
        "image_caption": "A South Indian vegetarian thali with rice, sambar, rasam and an array of vegetable preparations",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "What Now Houston / Community Impact — Simply South to Debut in Greater Houston (June 2026)",
            "Simply South — restaurant concept and menu information, simplysouthusa.com (2026)",
            "Restaurant Business Online — The year of redefining Indian food in America (June 2026)"
        ],
        "body": """In a country where the burger is a birthright and the steakhouse a civic institution, one of the more counterintuitive bets in Indian dining is the one that leaves meat off the menu entirely. This summer, the all-vegetarian chain Simply South will test that bet in one of America's great meat-eating metros, with plans to open its first Greater Houston location in suburban Katy.

The restaurant, confirmed by owner Sree Bharat Gummadi for a summer debut at 24600 Katy Freeway, is the latest outpost of a concept founded in Dallas in 2024 that has grown to a handful of locations across Texas and Illinois. Its pitch is audacious in its breadth: a 100 percent vegetarian menu of more than 450 items celebrating the culinary traditions of five South Indian states, from crisp dosas and rich biryanis to vegetarian meat alternatives and decadent desserts.

## Context & Background

Vegetarianism is not a marketing trend in Indian cuisine; it is a foundation. Large swaths of the subcontinent have eaten meat-free for religious and cultural reasons for centuries, and India sustains a vast ecosystem of pure-vegetarian restaurants — from temple-town messes to national institutions like Saravana Bhavan — that never treat the absence of meat as a limitation. The South Indian repertoire in particular is built to be satisfying without it: fermented rice-and-lentil batters, coconut-rich curries, tangy rasams, and protein-dense legumes that anchor a meal.

What is new is the wager that this tradition can scale in the American mainstream rather than serving only a captive diaspora audience. For decades, vegetarian Indian restaurants in the U.S. clustered near temples and Indian enclaves, run as community fixtures rather than expansion-minded brands. Simply South's multi-state, suburban-strip-mall growth represents a more confident commercial thesis: that an entirely meatless Indian menu can compete for the general American diner, not just the homesick NRI.

## Current Developments

The timing is shrewd. The all-vegetarian Indian model dovetails neatly with the American plant-based moment — the flexitarian shopper, the Meatless Monday household, the diner chasing high-fiber, high-protein eating without processed fake meat. A South Indian thali offers exactly that: a naturally plant-forward plate that needs no reformulation to fit the wellness brief. Simply South leans into the breadth of its offering, promising vegetarian "meat alternatives" alongside traditional preparations, and stresses fresh ingredients and from-scratch spicing.

It is part of a broader redefinition of Indian food in America, in which regional specificity is the selling point. Just as South Indian dosa houses and modern fusion kitchens are pushing past the butter-chicken template, the pure-vegetarian segment is asserting that meat-free need not mean compromised. The choice of Katy is itself a statement — a fast-growing, diverse Houston suburb with a large and rising Indian population, but also a thoroughly American market that will test whether the concept travels beyond the community.

## Diaspora Impact

For vegetarian NRIs, the spread of restaurants like Simply South is a practical liberation. Families who once drove long distances to find a fully vegetarian kitchen — one where there is no anxiety about shared fryers or hidden meat stock, and where Jain or no-onion-no-garlic preferences are understood without explanation — increasingly have a dependable option closer to home. For elders, it is a taste of the temple-town meals of their youth; for kids, it normalizes the idea that a feast can be entirely plant-based.

It also reframes vegetarianism itself for the American diner who wanders in. Encountering a 450-item meatless menu reframes the cuisine from a single "veggie option" buried on a card to a complete, celebrated world of its own.

## What's Next

Expect the all-vegetarian Indian segment to keep expanding into the Sun Belt suburbs where the diaspora is settling, following the same playbook of larger spaces, broader menus and full bars that is reshaping Indian dining at large. The deeper significance is cultural: in a country reconsidering how much meat it eats, India's centuries-old vegetarian tradition arrives not as a niche accommodation but as a ready-made answer — and Houston this summer is the next place to find out if America is hungry for it."""
    }
]


def main():
    print("=== Food Writer 20260623 (evening) ===")
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
