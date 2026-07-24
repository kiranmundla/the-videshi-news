#!/usr/bin/env python3
"""Food Writer — 2026-06-25 (PM run) — 3 articles to p2_articles (status=review)."""
import os, re, requests, subprocess
from datetime import datetime, timezone

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
HEADERS = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}',
           'Content-Type': 'application/json', 'Prefer': 'return=representation'}

def make_slug(headline, max_len=80):
    slug = re.sub(r'[^a-z0-9\s-]', '', headline.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug[:max_len].rstrip('-')

def get_existing_headlines():
    resp = requests.get(f'{SB_URL}/rest/v1/p2_articles',
        params={'category': 'eq.food', 'order': 'published_at.desc',
                'limit': '40', 'select': 'headline'}, headers=HEADERS)
    out = []
    for a in resp.json():
        h = re.sub(r'[^a-z0-9 ]', '', a['headline'].lower())
        out.append(h[:40])
    return out

def validate_image(url):
    if not url:
        return False
    try:
        out = subprocess.run(
            ['curl', '-sS', '-o', '/dev/null', '-w', '%{http_code} %{content_type} %{size_download}',
             '-H', 'User-Agent: TheVideshi/1.0 (thevideshi.com)', '-L', url],
            capture_output=True, text=True, timeout=40).stdout.strip()
        parts = out.split()
        code = parts[0] if parts else ''
        ct = parts[1] if len(parts) > 1 else ''
        size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        return code == '200' and 'image' in ct and size > 5000
    except Exception as e:
        print("   img err:", e)
    return False

def is_duplicate(headline, existing):
    norm = re.sub(r'[^a-z0-9 ]', '', headline.lower())[:40]
    return norm in existing

def wc(body):
    return len(re.sub(r'[#*>\[\]()_`]', ' ', body).split())

def publish_article(article, existing):
    if is_duplicate(article['headline'], existing):
        print(f"  SKIPPED (dup): {article['headline'][:60]}")
        return False
    assert isinstance(article['sources'], list) and len(article['sources']) >= 2, "sources must be >=2"
    words = wc(article['body'])
    assert words >= 400, f"body too short: {words} words"
    if not validate_image(article.get('image_url')):
        print(f"  WARN image failed validation, setting null: {article['headline'][:50]}")
        article['image_url'] = None
        article['image_attribution'] = None
        article['image_caption'] = None
    now = datetime.now(timezone.utc).isoformat()
    payload = {
        'headline': article['headline'],
        'subheadline': article['subheadline'],
        'body': article['body'],
        'slug': make_slug(article['headline']),
        'category': 'food',
        'vertical': 'food',
        'status': 'review',
        'published_at': now,
        'sources': article['sources'],
        'diaspora_angle': article['diaspora_angle'],
        'score_total': article['score_total'],
        'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
        'is_editorial': False,
    }
    r = requests.post(f'{SB_URL}/rest/v1/p2_articles', headers=HEADERS, json=payload)
    if r.status_code in (200, 201):
        print(f"  PUBLISHED ({words}w): {article['headline'][:65]}")
        return True
    else:
        print(f"  FAILED {r.status_code}: {r.text[:300]}")
        return False

ARTICLES = [
    {
        "headline": "The British Are Coming, Bearing Black Dal",
        "subheadline": "A wave of London's most celebrated Indian restaurants is crossing the Atlantic to New York, betting that America is finally ready for the cuisine Britain has loved for decades.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Punjabi_style_Dal_Makhani.jpg/1280px-Punjabi_style_Dal_Makhani.jpg",
        "image_caption": "A bowl of Punjabi-style dal makhani, the slow-cooked black lentil dish that has become a signature of British-Indian dining.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "For NRIs in the US who once envied London's Indian dining scene, the arrival of Dishoom, Ambassadors Clubhouse and Darjeeling Express closes a decades-long gap across the Atlantic.",
        "score_total": 80,
        "sources": [
            {"name": "Foodservice Equipment Journal", "url": "https://www.foodserviceequipmentjournal.com/dishoom-aims-for-debut-us-site-in-2027/"},
            {"name": "Eater / Europe Says", "url": "https://europesays.com/us/dishoom-is-opening-new-york-city-indian-restaurant/"},
            {"name": "The Infatuation", "url": "https://www.theinfatuation.com/new-york/guides/most-anticipated-restaurant-openings-nyc"},
            {"name": "The Sun", "url": "https://www.the-sun.com/travel/dishoom-us-new-york-opening/"},
        ],
        "body": """For thirty years, Indians who moved to America carried a particular envy in their luggage. Friends and family in Britain could walk into a curry house on almost any high street, or queue for a bacon naan roll at a Bombay-themed cafe in Covent Garden. In the United States, Indian food too often meant a steam-table buffet or a strip-mall tikka masala. That gap is now closing — and it is closing fast, as a fleet of Britain's most beloved Indian restaurants prepares to land in New York.

The most anticipated arrival is **Dishoom**, the London group whose nostalgic homage to Bombay's old Irani cafes has built a near-religious following. Founded in 2010 by cousins Shamil and Kavi Thakrar, Dishoom now runs more than a dozen UK sites, serves over 100,000 diners a week, and has confirmed it will open its first overseas restaurant at 11 East 26th Street in Manhattan's NoMad neighborhood. The brand tested American appetite in 2024 with a two-week breakfast pop-up at the French brasserie Pastis, selling out 6,000 reservation slots in under five minutes, with a waitlist of 20,000 more.

## Context & Background

Dishoom is not crossing the Atlantic alone. The same firepower behind London's fine-dining scene is following. **JKS Restaurants**, the group that owns the Michelin-starred Gymkhana, has signed a lease for its Punjabi-leaning **Ambassadors Clubhouse** in the A24 building at 1245 Broadway, with a debut planned for this fall. Chef **Asma Khan**, whose Darjeeling Express became a symbol of female-led, home-style Indian cooking, has told reporters she plans a New York restaurant within roughly a year. The small-plates favorite **Kricket** is also tracking toward a Manhattan opening.

The financial muscle behind the migration is real. Dishoom received its first outside investment last summer from **L Catterton**, the global private-equity firm that is roughly 40% owned by LVMH — a deal reported in some accounts at around £300 million, designed specifically to de-risk an American expansion. Kavi Thakrar's co-founder has said the time is finally right because of the growth of South Asian communities and the rise of Indian-American chefs.

## Current Developments

What makes this moment different is the ground that has already been broken on American soil. A decade ago, Indian fine dining in New York was a hard sell. Today, restaurants like **Dhamaka**, **Semma** and **Bungalow** have turned regional Indian cooking into some of the hardest reservations in the city — Semma even holds a Michelin star for unapologetically South Indian food. As Asma Khan put it, ten years ago she would have spent her evenings explaining what prawn malai curry and kosha mangsho were. Now diners arrive already fluent.

The British imports carry a particular kind of credibility. Their cooking was forged in a country where Indian food is not exotic but woven into national life — where chicken tikka masala is half-jokingly called a national dish. The bacon naan roll, the 24-hour black dal, the gunpowder potatoes and vada pav that made Dishoom famous are comfort food refined over fifteen years of relentless iteration.

## Diaspora Impact

For the Indian diaspora in the United States, this is more than a restaurant story — it is a kind of validation. The food that NRIs grew up defending, simplifying or apologizing for is now the object of nine-figure investment and breathless press. Second- and third-generation Indian-Americans, many of them running the very businesses and neighborhoods these restaurants are targeting, no longer have to choose between authenticity and ambition.

There is also a quiet symmetry. Indian food traveled to Britain through one wave of migration, was elevated there over generations, and is now being carried onward to America — a diaspora cuisine making a second crossing. For families who have relatives on both sides of the Atlantic, the arrival of a Dishoom in Manhattan means the same chai, the same chili cheese toast, finally available on both coasts of their scattered lives.

## What's Next

Dishoom's New York debut is expected in 2026, with some reports pointing to early 2027 depending on the buildout. Ambassadors Clubhouse should arrive first, this fall, followed by Darjeeling Express and Kricket over the coming year. If they succeed, expect the wave to spread beyond Manhattan — to the dense South Asian corridors of New Jersey, the Bay Area and Texas, where the audience is already waiting with knife and fork in hand."""
    },
    {
        "headline": "Makhana's American Moment: The Lotus Seed Taking On Popcorn",
        "subheadline": "Once a humble fasting snack from the ponds of Bihar, roasted fox nuts are riding India's protein and clean-label boom into American pantries and Amazon best-seller lists.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Makhana_%28Foxnut%29_roasted_with_masala_and_ghee.jpg/1280px-Makhana_%28Foxnut%29_roasted_with_masala_and_ghee.jpg",
        "image_caption": "Makhana (fox nuts) roasted with masala and ghee, the traditional Indian preparation now being sold flavored and ready-to-eat in the West.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "For NRIs, makhana is the taste of grandmother's kitchen and fasting-day snacks — now it is showing up on American supermarket shelves as the latest health-food darling.",
        "score_total": 74,
        "sources": [
            {"name": "VegNews", "url": "https://vegnews.com/fox-nuts-makhana-popcorn-alternative"},
            {"name": "Future Market Insights", "url": "https://www.futuremarketinsights.com/reports/fox-nuts-market"},
            {"name": "Mordor Intelligence", "url": "https://www.mordorintelligence.com/industry-reports/fox-nuts-market"},
        ],
        "body": """For generations of Indians, makhana was the snack of restraint. Light, airy, faintly nutty fox nuts roasted in a little ghee and salt — the thing you ate on a fasting day, or that a grandmother pressed on you between meals. Few foods felt less like the future. Yet today those same puffed lotus seeds are stacking up on Amazon best-seller lists, appearing in flavored pouches labeled "high protein" and "guilt-free," and being talked about, in earnest, as the snack that might dethrone popcorn.

The numbers behind the hype are striking. The global fox nuts sector is projected to grow from about **USD 1.7 billion in 2026 to USD 4.7 billion by 2036**, an 11% compound annual rate, according to Future Market Insights. North America is the fastest-growing region — Mordor Intelligence pegs its growth at a 9.3% annual clip through 2031 — fueled almost entirely by consumer hunger for plant-based, gluten-free, protein-rich snacks.

## Context & Background

Makhana, also called fox nuts, phool makhana or water lily seeds, comes from the prickly water lily *Euryale ferox*. Roughly 80 to 90% of the world's supply is harvested in India, with the state of **Bihar** alone accounting for over 80% of global production. Traditionally, the seeds were gathered by hand from the muddy bottoms of deep ponds — backbreaking work — then popped over heat into the light kernels Indians have eaten for centuries, plain, spiced, or simmered into kheer and curries.

What changed is not the seed but the story around it. As Western consumers grew wary of fried, ultra-processed snacks, makhana arrived pre-loaded with everything a modern label wants: low calories, high protein and fiber, gluten-free, vegan, non-GMO. VegNews summed up the appeal bluntly, calling fox nuts "the new popcorn" — airy and crunchy when roasted, but with a nutritional profile popcorn cannot match.

## Current Developments

The Indian government has moved to formalize what was a fragmented cottage industry. In the 2025–26 Union Budget, the Centre sanctioned a **National Makhana Board in Bihar** with an initial allocation of around INR 100 crore, aimed at building mechanized popping clusters, cold storage and quality standards. Analysts expect the board to cut post-harvest losses from over 25% to below 10% by 2030 — effectively expanding marketable supply by 15 to 20% without a single new acre under cultivation.

On the demand side, the American shelf is filling up. Brands now sell roasted makhana in BBQ, peri-peri, salt-and-pepper and mint flavors, in ready-to-eat pouches pitched at office desks, movie nights and post-workout cravings. Updated FDA "healthy" labeling criteria, which reward minimally processed foods, are helping flavored fox nuts win better placement. California, New York, Texas and Illinois — states with both health-conscious shoppers and large Indian communities — are leading the early demand.

## Diaspora Impact

For the diaspora, makhana's rise is a small, satisfying vindication. The snack that immigrant parents packed in tiffins, that turned up at every Navratri fast and every winter evening, is suddenly being "discovered" by the same Whole Foods crowd that once found it unfamiliar. NRIs who used to stock up on makhana only at Indian grocery stores can now grab a flavored pouch at a mainstream retailer — and watch non-Indian colleagues become converts.

It also rebalances a familiar dynamic. So often, Indian ingredients reach Western fame stripped of their origins. Makhana is arriving with its Bihar roots and its fasting-day heritage still attached, carried in part by Indian-founded brands and by a government determined to keep the value chain — and the GI-tagged premium grades — anchored at home.

## What's Next

Expect more flavors, more brands, and more shelf space as makhana follows the path turmeric and ghee already blazed into the Western mainstream. The risk is the one that shadows every superfood boom: price volatility, supply concentrated in a single Indian state, and the temptation to over-process a snack whose whole appeal is its simplicity. But for now, the humble fox nut is having precisely the moment its growers — and the diaspora that never forgot it — could only have imagined."""
    },
    {
        "headline": "Aam, Sago and the Summer of the Viral Desi Dessert",
        "subheadline": "From mango sago to ragi lava cake, India's home cooks and chefs are turning peak mango season into a parade of internet-breaking sweets — and the diaspora is reaching for the blender.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Mango_Lassi_.jpg/1280px-Mango_Lassi_.jpg",
        "image_caption": "A chilled glass of mango lassi, the classic summer drink reinvented this season in viral panna cotta and sago forms.",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "For NRIs far from India's mango season, these viral recipes are a way to recreate the taste of an Indian summer in a Western kitchen, one blender batch at a time.",
        "score_total": 68,
        "sources": [
            {"name": "WhosThat360", "url": "https://www.whosthat360.com/food/saransh-goila-mango-sago-recipe"},
            {"name": "Daily Tips", "url": "https://dailytips.in/viral-indian-recipes-2026/"},
            {"name": "Beyond Chutney", "url": "https://beyondchutney.com/mango-lassi-panna-cotta/"},
        ],
        "body": """Every Indian summer has a flavor, and this one is unmistakably mango. As Alphonso and Kesar arrive at their fragrant peak, a season's worth of desi desserts has spilled out of home kitchens and onto the feeds of millions — chilled, creamy, fruit-laden and engineered, it sometimes seems, less to be eaten than to be filmed. For the diaspora scrolling from Jersey City or Toronto, these viral sweets are more than a trend. They are a taste of home, reverse-engineered for a Western pantry.

The breakout star is **mango sago**, given fresh momentum by celebrity chef **Saransh Goila**, whose version layers diced mango, overnight-soaked sago pearls, coconut malai, coconut milk, mango puree and a hit of condensed milk over ice. It is, as he describes it, "a perfect summer mood in a bowl" — and, crucially, it is Insta-worthy, rich and fruity in a way that travels well across a phone screen. The nostalgia is baked in too, with aam papad folded through as a wink to childhood.

## Context & Background

The viral desi dessert is not new, but its scale is. The internet has become, in the words of one Indian food writer, "the world's largest recipe book," and the home kitchen "a laboratory of delicious innovation." Each summer, a handful of recipes break out of that laboratory and become a shared national project — everyone making the same thing in the same week, comparing results in the comments.

Mango is the natural engine. India is the world's largest mango producer, and the fruit carries an emotional charge no other ingredient quite matches: the smell of a ripe Alphonso is, for many, the smell of summer itself. Layer that onto the visual logic of short-form video — bright color, glossy textures, a satisfying pour — and you have the perfect raw material for virality.

## Current Developments

This year's crop of recipes shows a cuisine confidently remixing itself. Alongside mango sago, home cooks are making **mango lassi panna cotta**, a set, sliceable take on the classic drink, finished with saffron and pistachio brittle. Lists of 2026's viral Indian recipes run from **baked oats chaat** to **tandoori paneer momos** to a **ragi chocolate lava cake**, in which finger-millet flour replaces part of the maida — adding nutty depth, a calcium-and-iron boost, and the "guilt-free" halo that Indian food culture increasingly prizes.

The through-line is fusion without apology. A lava cake meets a millet; a French panna cotta meets a roadside lassi; a Parisian-style pastry, as one recipe promises, delivers "the crackling sugar of a bistro" with "the aftertaste of an Indian chai stall." These are dishes that honor tradition and treat it as a starting point rather than a rulebook.

## Diaspora Impact

For NRIs, the viral dessert season solves a particular ache. India's mango glut and street-corner sago carts are an ocean away, but a blender, a can of Alphonso pulp and a bag of sago pearls are not. These recipes are deliberately forgiving — most are no-bake, weeknight-simple, built from ingredients an Indian grocery store stocks year-round. They let a parent recreate, for a child born abroad, the exact dessert they ate at that age.

There is a community dimension too. When a recipe goes viral, the diaspora makes it in the same window as everyone back home — a small act of synchrony across time zones. The WhatsApp forwards, the side-by-side reels, the inevitable debate over whether condensed milk belongs in mango sago: all of it knits a scattered family back into one kitchen.

## What's Next

Mango season will fade, and with it this particular wave, but the format is now permanent. Expect monsoon and festival sweets — modak, malpua, the jalebi-everything genre — to take their turns going viral as the calendar moves. For the diaspora, that is good news: a steady, year-round feed of recipes that double as homesickness cures, each one a reminder that the distance to an Indian summer is now only as far as the nearest blender."""
    },
]

def main():
    existing = get_existing_headlines()
    print(f"Loaded {len(existing)} existing food headlines for dedup.")
    published = 0
    for art in ARTICLES:
        if publish_article(art, existing):
            published += 1
            existing.append(re.sub(r'[^a-z0-9 ]', '', art['headline'].lower())[:40])
    print(f"\nDONE. Published {published}/{len(ARTICLES)} articles.")

if __name__ == '__main__':
    main()
