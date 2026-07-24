#!/usr/bin/env python3
"""
Food Writer — June 21, 2026
3 food articles for The Videshi:
1. Sujan Sarkar's regional-Indian expansion (NADU Phoenix + Indienne NYC) — Michelin-recognized fine dining
2. Suresh Sundas, first Nepalese-American James Beard finalist — modern Indian street food in DC
3. A2 ghee + the 2025-2030 US Dietary Guidelines vindicating traditional Indian fats
"""
import os, json, re, requests, subprocess
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
        "headline": "Regional India, Plated for Critics: How Chef Sujan Sarkar Is Spreading Michelin-Grade Indian Across America",
        "subheadline": "With NADU debuting in Phoenix and his Michelin-starred Indienne crossing into New York's Hudson Yards, the Chicago chef is betting that America is finally ready to judge Indian food by technique, not price.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Non_Veg_Thali_-_Gandhi_Nagar_Jammu_-_Jammu_%26_Kashmir_-_01.jpg/1280px-Non_Veg_Thali_-_Gandhi_Nagar_Jammu_-_Jammu_%26_Kashmir_-_01.jpg",
        "image_caption": "A regional Indian thali of curries, rice and breads, the kind of homestyle cooking chefs are now plating for fine-dining audiences",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "AZ Central — Michelin-recognized Chicago Indian restaurant to make Phoenix debut (June 2026)",
            "WhatNow — Michelin-Starred Indian Restaurant From Chicago Is Opening in Hudson Yards (2026)",
            "Resy — Nadu Brings Regional Homestyle Indian Cooking to Lincoln Park (2026)"
        ],
        "body": """For decades, the surest way to insult an ambitious Indian chef in America was to praise the value. The lunch buffet, the $12 tikka masala, the all-you-can-eat naan — these were the terms on which the cuisine was allowed to compete, and they capped its ceiling. A new generation of chefs is dismantling that ceiling one tasting menu at a time, and few are doing it on more fronts than Sujan Sarkar.

This June, Sarkar's team opened NADU at Desert Ridge Marketplace in north Phoenix, the second American location of a restaurant that earned an Eater Best New Restaurant nod, a James Beard semifinalist nomination and a Michelin Bib Gourmand within a year of opening in Chicago. The Phoenix kitchen will be led by executive chef Pujan Sarkar — Sujan's brother and longtime mentee — extending a family project that treats regional Indian cooking as something to be discovered, not dumbed down.

## Context & Background

Sarkar's rise tracks a broader shift in how Indian food is consumed in America. His Chicago restaurant Indienne, opened in River North in 2022, won a Michelin star within its first year on the strength of a multi-course tasting format that begins with chaat-inspired bites and moves through layered, regionally specific courses. NADU, by contrast, is the approachable sibling — a celebration of "the type of cuisine traditionally enjoyed in my home country," as Sarkar put it, "simple, bold, and full of flavor."

That two-track strategy — fine dining at the top, elevated-casual just beneath it — is the template the most decorated Indian chefs in America are now following. It is a deliberate rejection of the buffet economics that defined the cuisine's first few decades in the United States, and a bet that diners will pay fine-dining prices for cooking they once considered cheap takeout.

## Current Developments

The expansion is accelerating on both coasts. In late May, Sarkar's Michelin-starred Indienne opened a New York outpost inside Henry Hall at Hudson Yards, a 34-seat room continuing its signature nine-course tasting experience, with menus priced at $175 for vegetarian and vegan diners and $195 for the non-vegetarian progression. The interiors lean on the work of Chicago artist Ken Andjulis, whose Holi-inspired paintings signal that this is Indian food presented as art, not afterthought.

The detail work is where the ambition shows. At NADU's original Lincoln Park location, the beverage program runs on Indian gins, whiskeys and regional spirits like cashew feni, while cocktails are built around curry leaf, palm jaggery, turmeric and saffron. The dining room's centerpiece is an 11-by-10-foot oil painting blending Chicago iconography with Indian motifs. None of this is incidental. It is the architecture of a category trying to be taken seriously, course by course and cocktail by cocktail.

## Diaspora Impact

For the Indian diaspora, Sarkar's multiplying footprint lands as a quiet vindication. A generation of NRIs grew up watching their food filed under "ethnic" and "cheap eats," its complexity flattened into a handful of creamy gravies. To see regional Indian cooking — the dishes of specific states, seasons and households — earn Michelin recognition and command tasting-menu prices is to see a part of one's heritage finally granted the prestige long reserved for French and Japanese kitchens.

Geography matters, too. Phoenix is not New York or the Bay Area, where a dense Indian population can sustain ambitious cooking on its own. By planting an accoladed restaurant in suburban Arizona, the Sarkars are wagering that the audience for serious Indian food now extends well beyond the diaspora's traditional strongholds — and that NRI families scattered across America's less-dense metros no longer have to drive to a coastal city to eat the food of home done well.

## What's Next

Sarkar has signaled that the New York project is more than a single restaurant; Indienne arrives at Hudson Yards alongside two additional concepts he is planning, suggesting a cluster strategy rather than a one-off. With NADU now in two cities and Indienne in two more, the question is no longer whether elevated Indian cooking can survive in America, but how fast it can scale without losing the regional specificity that makes it worth the price.

For the diaspora, the answer will be written one opening at a time. Each new room that treats Indian food as fine dining shifts the baseline a little further — until, perhaps, the buffet ceiling is something the next generation of chefs will read about rather than fight against."""
    },
    {
        "headline": "From a 7-Eleven Counter to the Beard Awards: A Self-Taught Chef Rewrites the Indian-American Kitchen Story",
        "subheadline": "Suresh Sundas, who learned to cook in a southeastern Nepal home kitchen and never attended culinary school, becomes the first Nepalese-American James Beard finalist — a milestone for Himalayan and South Asian food in America.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Buff_Momos.jpg/1280px-Buff_Momos.jpg",
        "image_caption": "A plate of steamed momos, the Himalayan dumplings central to the Nepali and modern Indian cooking now winning national acclaim",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "American Bazaar — Chef Sundas makes history as first Nepalese American JB finalist (2026)",
            "USA Today — Several Washington DC restaurants are finalists for James Beard Awards (2026)",
            "Washingtonian — DC Chef and Restaurant Nominees for the 2026 James Beard Awards (2026)"
        ],
        "body": """The most American of culinary stories is also, increasingly, a South Asian one: the immigrant who arrives with nothing, works a job no one wants, and turns a home-cooked dish into a destination. This year that story belongs to Suresh Sundas, the Washington, D.C. chef who became the first Nepalese-American to be named a finalist for a James Beard Award — the honor often called the Oscars of the food world.

Sundas was a finalist in the fiercely competitive Best Chef: Mid-Atlantic category for his H Street restaurant Tapori, which Eater named one of the 15 best new restaurants in America. The award ultimately went to Philadelphia's Jesse Ito of Royal Sushi & Izakaya, but the recognition itself was the milestone: a self-taught cook who never set foot in a culinary school, standing among the region's most celebrated chefs.

## Context & Background

Sundas learned to cook at age 11 in southeastern Nepal, taking over family meals when his mother went to work. "She taught me how to cook lentil rice, fried rice, even momo," he has recalled — the Nepalese dumpling that would become a signature of his cooking. He moved to the United States at 24 and took a job behind the counter of a 7-Eleven in Northern Virginia.

The turn came over a plate of chicken curry. A roommate's guest tasted it and told him plainly that he belonged in a restaurant, not a convenience store. He found the nearest restaurant in Virginia, got the job, and began climbing — eventually landing at the acclaimed Rasika West End, where he mastered the tandoor and met mixologist Dante Datta. In 2021 the two opened Daru, a modern Indian restaurant and cocktail bar that became a D.C. favorite, and Sundas later launched Tapori.

## Current Developments

The Beard finalist nod is the latest in a run of recognition. At the 43rd annual RAMMY Awards, hosted by the Restaurant Association of Metropolitan Washington, Sundas won Rising Culinary Star of the Year, beating out some of the city's most talked-about new chefs. Tapori's Eater listing put it on a national stage, and the restaurant framed his rise in deliberately generational terms.

"We are proud of him in a way that is hard to put into words," the Tapori team wrote on Instagram. "What he carries from his mother's kitchen, what he has built here, what he is building for the next generation of cooks who come from somewhere people didn't expect them to come from — that is the work. The nomination is just proof that other people see it too."

That framing — heritage as credential, the home kitchen as culinary school — runs against the grain of an industry that has long gatekept prestige behind formal training and European technique. Sundas's cooking insists that the food of a Himalayan household, made by a boy filling in for his working mother, can stand at the summit of American fine dining.

## Diaspora Impact

For the Nepali and broader South Asian diaspora, Sundas's recognition carries outsized weight. The James Beard Foundation has slowly broadened its lens in recent years, but a Nepalese-American finalist is a first — a marker that Himalayan flavors, often folded loosely into the "Indian" category on American menus, are being seen and named on their own terms.

His story also reframes the diaspora's relationship with menial first jobs. The 7-Eleven counter, the restaurant dish room, the line cook's station — these are way stations in countless immigrant biographies, rarely celebrated and seldom seen as the start of an artist's career. Sundas's arc insists otherwise, offering a template to thousands of NRIs and their children: that the food carried from home is not a limitation to overcome but the very thing worth building on.

## What's Next

With Daru and Tapori both drawing national attention, Sundas now occupies the rare position of a chef whose backstory and cooking are equally compelling to critics. Industry watchers expect the Beard recognition to bring a "Beard bump" — the surge in bookings and attention that has launched past finalists toward household-name status.

The deeper significance may be cumulative. Each South Asian chef who breaks into the awards conversation widens the path for the next, and chips away at the idea that Indian, Nepali and Himalayan food belong only in the value aisle of American dining. For a diaspora long accustomed to explaining its food, Sundas offers something simpler and more powerful: proof that the world is finally ready to give it a standing ovation."""
    },
    {
        "headline": "Ghee Was Right All Along: America's New Dietary Guidelines Vindicate the Indian Kitchen",
        "subheadline": "As the 2025-2030 federal guidelines soften decades of warnings against animal fats, the diaspora's grandmothers — and a booming market for premium A2 ghee — are having a quiet vindication.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Ghee_2.jpg/1280px-Ghee_2.jpg",
        "image_caption": "A jar of golden ghee, the clarified butter long central to Indian cooking and Ayurvedic tradition",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Medium / Dr. Barman — Ancient Wisdom, Modern Science: What India Can Teach the New Global Diet (2026)",
            "Medium / Preetimohar — Why A2 Ghee is Trending Among Fitness Enthusiasts (May 2026)",
            "Dainik Jagran English — Ghee on Empty Stomach: The Morning Miracle Taking Over Indian Wellness Circles in 2026"
        ],
        "body": """For most of the diaspora's time in America, ghee lived a double life. At home it was sacred — drizzled over dal, smeared on the first roti, lit in lamps at the altar. Outside, it was contraband: a saturated fat, the kind nutritionists warned would clog your arteries, the reason a doctor might frown at your cholesterol. A generation of NRI parents quietly swapped their danedar ghee for "heart-healthy" vegetable oils, hedging against the science of the day. That science is now changing its mind.

The newly released 2025-2030 Dietary Guidelines for Americans have softened decades of blanket warnings against animal fats, moving toward an emphasis on whole, minimally processed "real food" over refined substitutes. For Indian families, the reversal reads less like news than like an apology — modern nutrition catching up to what their grandmothers never doubted.

## Context & Background

The case against saturated fat hardened in the late twentieth century, when public-health campaigns pushed Americans toward seed and vegetable oils and away from butter, lard and ghee. Indian cooking, built around ghee for millennia and praised in Ayurveda as amrit — nectar, a rasayana that aids digestion and nourishes the body — suddenly found one of its foundational ingredients on the wrong side of dietary orthodoxy.

The intervening decades have complicated that story. Researchers now point to ghee's content of butyrate, a short-chain fatty acid associated with gut health and reduced inflammation, and to its fat-soluble vitamins A, D, E and K, which the body needs dietary fat to absorb. Its high smoke point makes it more stable for high-heat cooking than many of the polyunsaturated oils that replaced it. None of this makes ghee a health food to be eaten by the spoonful, but it has dismantled the simple villain narrative that pushed it out of so many diaspora kitchens.

## Current Developments

The vindication is showing up in the market. A premium category has exploded around A2 ghee — clarified butter from the milk of indigenous, humped Indian cow breeds, whose protein structure many find easier to digest than that of conventional dairy. Once a niche product, A2 ghee has become a fixture in fitness and wellness circles, promoted by creators who frame it as the meeting point of ancient food wisdom and modern clean-eating, and prized for its traceability to traditional Bilona churning methods.

The trend has even produced its own rituals. In urban India, nutritionists report a surge of clients taking a teaspoon of ghee on an empty stomach each morning — a practice pitched, only half-jokingly, as a desi answer to bulletproof coffee, promising steady energy without the caffeine crash. Whether or not the more extravagant claims hold up, the cultural signal is unmistakable: ghee has gone from dietary liability to aspirational wellness product.

## Diaspora Impact

For NRIs, the rehabilitation of ghee touches something deeper than nutrition science. Food is one of the diaspora's strongest threads back to home, and ghee sits at the center of that web — the smell of it in a hot pan is the smell of a parent's kitchen. To have been told for years that this ingredient was quietly harmful was to absorb a small, persistent message that the food of home was somehow backward. The guidelines' shift loosens that knot.

It also reframes a familiar tension between generations. The aunties who never stopped cooking with ghee, dismissing the seed-oil orthodoxy as a fad, are now positioned as having been ahead of the curve. Younger diaspora cooks, raised on the language of macros and gut health, are rediscovering ghee not as a guilty inheritance but as a functional food they can defend in the gym and at the dinner table alike. The result is a rare convergence: tradition and trend pointing the same direction.

## What's Next

The likely trajectory is more, not less, of this. As Western nutrition continues its pivot toward whole foods, traditional fasting practices and minimally processed ingredients, more staples of the Indian kitchen — millets, makhana, amla, turmeric — are poised for the same arc from suspicion to celebration. Premium A2 ghee brands are already chasing the American wellness shopper, and the diaspora's pantry is increasingly being mined for the next functional superfood.

The caution worth keeping is the one Ayurveda itself counsels: moderation. A teaspoon on the dal is wisdom; a wholesale embrace of any single ingredient as a miracle is the same mistake the seed-oil era made in reverse. But for a diaspora that spent years apologizing for the contents of its kitchen, the deeper message of the new guidelines is its own kind of nourishment — that the food of home was never the problem."""
    }
]


def main():
    print("=== Food Writer 20260621 ===")
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
