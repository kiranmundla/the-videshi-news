#!/usr/bin/env python3
"""
Food Writer — June 22, 2026
3 food articles for The Videshi:
1. Chai Pani's DC flagship — James Beard winner Vish Bhatt brings non-Westernized Indian street food to the capital
2. The mithai renaissance — Indian sweets going upscale/artisanal in America (Tagmo/Surbhi Sahni, Xari Foods)
3. The desi pantry gold rush — Anveshan's Rs 121cr Series A and the new-age clean-label Indian food startups eyeing America
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
        "headline": "Chai Pani Comes to the Capital: A Two-Time Beard Winner Brings Unapologetic Street Food to Washington",
        "subheadline": "With chef Vishwesh Bhatt at the helm, the James Beard-honored Asheville chaat house opens its first location outside the South in DC's Union Market District, betting the capital is ready for sev puri over saag paneer.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Sev_puri_chaat%2C_an_Indian_Street_food.jpg/1280px-Sev_puri_chaat%2C_an_Indian_Street_food.jpg",
        "image_caption": "A plate of sev puri, the crunchy Mumbai street snack of the kind Chai Pani built its reputation on",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Washingtonian — A James Beard-Winning Indian Restaurant From Asheville Is Opening in DC (2026)",
            "What Now DC — Chai Pani Nearing DC Debut (2026)",
            "The Adventurist Magazine — 'We Belong': How Chef Vishwesh Bhatt Is Defining the Future of Southern Food (2026)",
            "PoPville — Asheville's Chai Pani Now Open in Union Market Area (2026)"
        ],
        "body": """For most of the cuisine's American life, the unspoken rule of the Indian restaurant was reassurance. Soften the spice, dim the lights, lean on a familiar trio of creamy gravies, and never make the diner work too hard. Chai Pani built a James Beard Award on doing the opposite — and now it is bringing that defiance to Washington, D.C.

The celebrated Asheville chaat house, named the country's most Outstanding Restaurant by the James Beard Foundation in 2022, has opened its first location outside the South in DC's bustling Union Market District. The 4,000-square-foot room at 1325 Fifth Street NE seats up to 150 and is helmed by Vishwesh "Vish" Bhatt, the two-time James Beard Award-winning chef and Gujarat native who spent decades defining a new Southern-Indian idiom in Oxford, Mississippi.

## Context & Background

Chai Pani is the work of Meherwan and Molly Irani, who launched it in Asheville in 2009 with a deceptively simple mission: to showcase "everyday Indian culture and its underestimated street food." Where most American Indian restaurants chased white-tablecloth respectability, Chai Pani served the loud, snackable food of Indian railway platforms and city corners — sev potato dahi puri, bhel puri, vada pav, kale pakoras — with hand-painted signage and a palette of kaleidoscopic color. Thirteen years later, that bet on the street over the banquet hall earned the country's highest restaurant honor.

The DC kitchen pairs the Iranis with Bhatt, whose own story runs parallel. He arrived in Oxford in the late 1990s not knowing how to work a professional line, took a prep job at John Currence's City Grocery, and rose to run Snackbar, where he discovered the South through its foodways — and rediscovered Indian food in the process. The fried okra of Mississippi met the bhindi of his mother's Ahmedabad kitchen. He boils his philosophy down to two words: we belong.

## Current Developments

Chai Pani DC stays "firmly in our street food lane," as the team puts it, but lets Bhatt leave his fingerprints on it. Alongside the Asheville greatest hits — the okra fries, the SPDP, the Sloppy Jai, the homestyle thalis — the menu leans into Gujarati snacks and small plates, American South-meets-Western India dishes reminiscent of his Snackbar years, and an expanded sigri (grill) section. Bhatt has said he is relishing the four seasons after years in the Deep South, and plans to fold Chesapeake seafood into the street-food model, pulling Mid-Atlantic ingredients into a distinctly Indian frame.

The interiors complete the transport: garlands of bougainvillea and marigolds, museum-worthy murals by District artists, the visual grammar of a Mumbai street rendered in a corner of the American capital. The DC debut is the first move in a broader expansion — the group has signaled plans for a Botiwalla location in Tenleytown and a presence at Raleigh Iron Works, extending a footprint that began in a single Asheville storefront.

## Diaspora Impact

For the diaspora, Chai Pani's arrival in Washington lands as more than another opening. It is a public argument about whose food gets to be celebrated and on what terms. A generation of NRIs grew up watching the cooking of their grandmothers — the tangy, messy, hand-eaten snacks of home — dismissed as too pungent, too unfamiliar, too far from the buffet's safe middle. To see that exact food honored by the Beard Foundation and planted in the capital's most-watched food district is a quiet correction of the record.

The Bhatt-Irani partnership also models something the diaspora knows intimately: belonging built sideways, through friendship and food, in places where, as Bhatt puts it, "there aren't many people like us." Their cult Brown in the South dinner series, their shared spice blends, their travels through India — all of it feeds a kitchen that insists Indian street food deserves a marquee, not an apology.

## What's Next

The opening arrives amid what the trade press has called a year of redefining Indian food in America, with British imports like Dishoom and JKS's Gymkhana landing in New York and Las Vegas, and homegrown chefs scaling fast. Chai Pani's wager is distinct: not fine dining, but street food taken seriously, in a city of power lunches and policy dinners.

If it works, the ripple is cultural. Each room that treats chaat as worthy of a destination restaurant nudges the baseline, until the next generation of diaspora cooks no longer has to choose between authenticity and acclaim. In Washington, at least, the marigolds are up and the sev puri is on the menu — no reassurance required."""
    },
    {
        "headline": "Mithai Goes Couture: How Indian Sweets Are Trading the Syrup Tin for the Gallery Case",
        "subheadline": "From French-trained pastry chefs in New York to Bay Area experimentalists, a new wave of artisanal mithai is reframing the diaspora's most nostalgic food as fine confection — clean, less sweet, and built for a modern palate.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Burfi_and_Peda%2C_Indian_Sweets_Mithai_Chennai_India.jpg/1280px-Burfi_and_Peda%2C_Indian_Sweets_Mithai_Chennai_India.jpg",
        "image_caption": "An assortment of burfi and peda, milk-based Indian sweets at the heart of the mithai tradition",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Khabar — Food & Dining: This Diwali, Elevate Your Mithai Game (2026)",
            "Korea JoongAng Daily — In India, the sweet spot hits differently with local confectionary mithai (2026)",
            "The Hindu BusinessLine — Mithai flavoured with artisanal chic (2026)"
        ],
        "body": """Every diaspora kitchen has a box of it somewhere — the dusty tin of kaju katli, the sweating laddoos in their pleated paper cups, the burfi cut into squares that someone's auntie pressed on you at a wedding. Mithai has always been the diaspora's most loaded food: sacred at festivals, ubiquitous at gatherings, and quietly embarrassing in a culture that filed it under "too sweet." A new generation of chefs is dragging it out of the tin and into the gallery case.

The shift is unmistakable. Across the United States and India alike, Indian sweets are being reimagined the way fine chocolate and pâtisserie once were — with restrained sugar, clean presentation, and an inventive borrowing of regional and global flavors. Blueberry motichoor from the Bay Area, filter-coffee burfi nodding to South India, fig-and-amaranth rolls drawn from Ayurvedic tradition: mithai, long viewed as rustic and nostalgic, is being positioned alongside high-end confectionery.

## Context & Background

The old mithai was a product of its constraints — heavy syrups, intense sweetness, short shelf lives, and family recipes guarded behind the counters of hyperlocal sweet shops. It was food made to be given, in volume, at peak festival demand. For the diaspora, it carried enormous emotional weight precisely because it was so unchanged: a bite of pista burfi tasted exactly like Diwali in Delhi or Mumbai, decades and oceans removed.

But that very stasis made mithai feel out of step with younger eaters fluent in the language of macros, clean labels, and Instagrammable plating. The new wave answers that tension not by abandoning tradition but by refining it. The essence of home stays; the sugar bomb goes.

## Current Developments

Few embody the change more vividly than Chef Surbhi Sahni of Tagmo in New York. A veteran pastry chef, Sahni applies the discipline of French technique to the artistry of mithai — almond-orange katli cut into clean geometric diamonds, rose-coconut burfi finished with a restrained drizzle of saffron, laddoos hand-rolled to a silken finish, each piece composed for a gallery case. Crucially, she pairs the precision with less sugar, more flavor, and a roster of vegan and gluten-free options for contemporary diets, without sacrificing the familiar soul of the sweet.

She is not alone. The Bay Area's Xari Foods has built a "Boutique Mithai Collection" around playful fusions — Valrhona chocolate-stuffed besan laddu, tiramisu burfi, Biscoff burfi, lemongrass-guava-coconut laddu. In India, brands like Bombay Sweet Shop (from the team behind The Bombay Canteen) have turned heritage sweets into design objects, with a chocolate box inspired by sohan halwa and "Katli Bites" topped with dark-chocolate ganache. The category is no longer a backwater; market intelligence platform Tracxn reports India's new-age sweets startups secured over $43 million in funding between 2020 and 2025, with the packaged-sweets segment projected to more than quadruple to roughly ₹26,000 crore by 2030.

## Diaspora Impact

For NRIs, the rise of couture mithai resolves a small, persistent ache. The food that anchored childhood celebrations had quietly become something to explain or apologize for — too sugary for a health-conscious table, too unfamiliar to share at the office. The new artisanal versions, with their balanced sweetness and gallery-grade presentation, hand the diaspora a way to carry the tradition forward without flinching.

It also reframes mithai as a gift worth giving outside the community. A box of jewel-like, French-influenced burfi reads, to a non-Indian colleague, as a luxury confection rather than an ethnic curiosity. That repositioning matters: it lets the diaspora present a piece of home on its own elevated terms, the same courtesy long extended to macarons and pralines.

## What's Next

The trajectory points toward a global moment for Indian sweets. As Korea, Europe, and the United States chase the next imported indulgence — Dubai's pistachio-kataifi chocolate, Turkey's brick cake — mithai's distinctive toolkit of chickpea flour, milk solids, jaggery, and ghee offers something genuinely unfamiliar to Western dessert culture, and largely egg-free to boot.

The likely path is the one fine chocolate already walked: a premium tier of artisanal makers building national brands, festival demand anchoring the calendar, and social media turning clean-label mithai into an aspirational object. For a diaspora that spent years quietly explaining the contents of that dusty tin, the gallery case is its own kind of vindication — proof that the sweetest part of home was always worthy of the spotlight."""
    },
    {
        "headline": "The Desi Pantry Gold Rush: How Clean-Label Indian Food Brands Raised Millions and Set Their Sights on America",
        "subheadline": "D2C brand Anveshan's ₹121 crore Series B, backed by boAt and Swiggy founders, is the loudest signal yet that wood-pressed oils, A2 ghee, and heritage Indian staples are becoming a venture-funded category aimed squarely at the diaspora shopper.",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Pure_Ghee.jpg/1280px-Pure_Ghee.jpg",
        "image_caption": "A bowl of pure ghee, the kind of heritage Indian pantry staple now drawing venture funding and US ambitions",
        "image_attribution": "Wikimedia Commons",
        "sources": [
            "Indian Retailer — Anveshan Raises Rs 121 Cr in Series B Round Led by Vertex Ventures (May 2026)",
            "Indian Retailer — D2C Brand Moi Soi Raises Funds Amid Growing Demand for Asian Foods (2026)",
            "Specialty Food Association — Quicklly expands South Asian grocery marketplace with new investment (2026)"
        ],
        "body": """For decades, the Indian-American pantry was a study in compromise. The good stuff — cold-pressed oils, real ghee, single-origin spices — came from a parent's suitcase or a once-a-month pilgrimage to the desi grocery. Everything else was a substitute, bought from the mainstream aisle and quietly tolerated. A wave of venture-funded Indian food brands is now betting it can close that gap, and the money pouring in suggests investors agree.

The clearest signal came in late May, when Delhi-based D2C food brand Anveshan secured ₹121 crore — roughly $12.7 million — in a Series B round led by Vertex Ventures, with participation from the International Finance Corporation, Titan Capital, and Wipro Enterprises. The cap table read like a who's who of Indian consumer success: boAt co-founders Aman Gupta and Sameer Mehta, and Swiggy co-founder Sri Harsha Majety, all wrote checks. It was Anveshan's second big raise in a year, following a ₹48 crore Series A.

## Context & Background

Anveshan's pitch is the heart of the trend: heritage Indian staples, made the traditional way, sold with modern transparency. Its catalog centers on wood-pressed (kachi ghani) cooking oils, A2 ghee from indigenous cow breeds, raw honey, and stone-ground flours — the exact ingredients the diaspora has long associated with a grandmother's kitchen and struggled to source reliably abroad. The brand's pitch fuses two currents at once: cultural nostalgia and the global clean-label movement that prizes minimally processed, traceable food.

The category is broader than any single company. Bengaluru's India Sweet House has scaled to 50 stores and ₹80 crore in revenue on the back of natural-ingredient mithai, and has experimented with US distribution. Asian-foods brand Moi Soi recently raised funds on rising American demand for South Asian flavors. Investors increasingly see "desi pantry" not as a niche but as a packaged-goods opportunity sized to a diaspora of tens of millions plus a curious mainstream.

## Current Developments

The infrastructure to reach American kitchens is maturing alongside the brands. Chicago-based Quicklly, an online marketplace for South Asian and Indian groceries, has raised fresh capital to expand same-day delivery beyond its Chicago, Bay Area, and New York footprints into Austin, Seattle, and Los Angeles, offering more than 250,000 products and a "shop by recipe" feature. Roughly 80% of its customers are of South Asian descent — a base these new brands can plug straight into.

There are headwinds. India Sweet House recently paused US shipments after new American rules requiring inspection of every package valued around $100 made small-parcel exports unworkable — a reminder that trade friction can stall even hot brands at the border. The likely workaround is the path Gymkhana Fine Foods and others have taken: build domestic US distribution through retailers rather than shipping from India, landing products on shelves at Whole Foods and in the desi-grocery channel instead of relying on cross-border parcels.

## Diaspora Impact

For NRIs, the gold rush is personal before it is financial. The brands being funded are, in effect, productizing the diaspora's own preferences — the conviction that wood-pressed oil tastes cleaner, that A2 ghee sits easier, that honey should be raw and flour stone-ground. To have that quiet domestic knowledge validated by Vertex Ventures and the founders of boAt and Swiggy is to see the diaspora's pantry instincts treated as a market thesis.

It also promises a concrete convenience. If these brands succeed in building US distribution, the suitcase runs and monthly grocery pilgrimages give way to a same-day delivery or a Whole Foods endcap. The ingredients that once marked the boundary between "real" home cooking and American compromise become simply available — a small but meaningful easing of the immigrant tax on eating the way one grew up.

## What's Next

Expect consolidation and a US land grab. With nine-figure rupee rounds now routine, the leading desi-pantry brands have the capital to chase American shelf space, and the clean-label positioning travels well to a mainstream shopper already primed by the wellness movement. The open questions are trade policy, which can choke the export route overnight, and whether these brands localize manufacturing fast enough to sidestep it.

What seems settled is the direction. The Indian pantry — long the diaspora's improvised, compromise-laden corner of the kitchen — is becoming a funded, branded, and increasingly available category. For a community that spent years making do, the next grocery list may finally read like home."""
    }
]


def main():
    print("=== Food Writer 20260622 ===")
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
