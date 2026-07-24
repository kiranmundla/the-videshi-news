#!/usr/bin/env python3
"""Food Writer — 2026-06-25 — 3 articles to p2_articles (status=review)."""
import os, re, requests
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
                'limit': '30', 'select': 'headline'}, headers=HEADERS)
    out = []
    for a in resp.json():
        h = re.sub(r'[^a-z0-9 ]', '', a['headline'].lower())
        out.append(h[:40])
    return out

def validate_image(url):
    try:
        resp = requests.get(url, timeout=20, stream=True,
                            headers={'User-Agent': 'TheVideshi/1.0'}, allow_redirects=True)
        ct = resp.headers.get('Content-Type', '')
        cl = int(resp.headers.get('Content-Length', '0'))
        if resp.status_code == 200 and 'image' in ct:
            if cl > 5000:
                return True
            chunk = resp.raw.read(6000)
            return len(chunk) > 5000
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
    if article.get('image_url') and not validate_image(article['image_url']):
        print(f"  Image validation failed: {article['image_url'][:70]}")
        article['image_url'] = None
        article['image_caption'] = None
        article['image_attribution'] = None
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    payload = {
        'headline': article['headline'], 'subheadline': article['subheadline'],
        'body': article['body'], 'slug': make_slug(article['headline']),
        'category': 'food', 'vertical': 'food', 'status': 'review',
        'published_at': now, 'image_url': article.get('image_url'),
        'image_caption': article.get('image_caption'),
        'image_attribution': article.get('image_attribution'),
        'is_editorial': False,
    }
    resp = requests.post(f'{SB_URL}/rest/v1/p2_articles', headers=HEADERS, json=payload)
    if resp.status_code in (200, 201):
        result = resp.json()
        art_id = result[0]['id'] if isinstance(result, list) else result.get('id', '?')
        print(f"  PUBLISHED ({wc(article['body'])}w): {article['headline'][:55]}... id={art_id}")
        return True
    print(f"  FAILED ({resp.status_code}): {resp.text[:200]}")
    return False

articles = []

# ─── Article 1: Sanjeev Kapoor / celebrity-chef chains ───
articles.append({
    'headline': "The Celebrity Chef Lands: Sanjeev Kapoor's Yellow Chilli Stakes a Claim in Silicon Valley",
    'subheadline': "As India's most televised chef opens his first U.S. restaurant in Santa Clara, a new wave of branded, celebrity-backed Indian chains is betting the diaspora is ready to trade the corner curry house for the franchise.",
    'image_url': "https://upload.wikimedia.org/wikipedia/commons/e/ea/Sanjeev_kapoor_at_the_Launch_of_new_restaurant_%27Arola%27_at_J_W_Marriott.jpg",
    'image_caption': "Celebrity chef Sanjeev Kapoor, whose Yellow Chilli chain has opened its first U.S. location in Santa Clara",
    'image_attribution': "Wikimedia Commons",
    'body': """For a generation of Indians who grew up in the 1990s and 2000s, the face of home cooking was not a grandmother but a man on television in a chef's whites, gently coaxing viewers through a recipe with the patience of a favourite uncle. Sanjeev Kapoor's *Khana Khazana* ran for over two decades and became the longest-running cookery show in Asia, turning its host into a household name across the subcontinent and the diaspora alike. Now, that name has arrived in the heart of Silicon Valley.

Kapoor's casual-dining chain, **The Yellow Chilli**, has opened its first United States location at Monticello Apartment Homes in Santa Clara, California — the dense, prosperous, overwhelmingly desi corridor that stretches from Sunnyvale to Fremont. Billed as "Northern California's first ever Indian celebrity-chef restaurant," it is a deliberate bet that the Bay Area's Indian-American community will pay for a brand it already trusts.

## Context & Background

The Yellow Chilli is no startup. Overseen by Mumbai-based SK Restaurants, the chain runs roughly 30 outlets across India alongside branches in the United Arab Emirates and Oman. Its menu reads like a greatest-hits reel of Kapoor's televised career: Lalla Mussa Dal, black and green lentils simmered overnight with cream, ghee and butter; Shaam Savera, spinach koftas stuffed with cottage cheese floating in a velvety tomato gravy — the very dish Kapoor says he cooked when his television journey began; and Gulab-e-Gulkand, milk dumplings stuffed with candied rose petals.

The Santa Clara opening, developed in partnership with local operator Yogesh Gupta and landlord Irvine Company, slots the restaurant into a planned residential community rather than a strip mall — a tell about its target customer. This is not a lunch-buffet operation chasing office workers. It is a polished, family-friendly, full-bar concept aimed squarely at the affluent NRI household that wants celebration food without the formality of fine dining.

## Current Developments

Yellow Chilli is part of a broader invasion. India's best-known restaurant brands and chefs are crossing the Pacific in numbers not seen before. From the United Kingdom, JKS Restaurants has brought Gymkhana to Las Vegas and the Punjabi-focused Ambassadors Clubhouse to New York; the beloved Dishoom is on deck for a Manhattan opening valued, in a recent private-equity deal, at nearly $400 million. Michelin-starred chef Sujan Sarkar is expanding his Indienne concept from Chicago to Hudson Yards.

What sets Yellow Chilli apart is the celebrity-chef model itself. Where most Indian restaurants in America are independent, family-run affairs, Kapoor offers a franchise-ready package: name recognition, a standardised menu, and the implicit promise that what you eat in Santa Clara tastes like what you would eat in Mumbai. Early signs are encouraging — the restaurant has been booked dozens of times a day on OpenTable, carrying a 4.6 rating across hundreds of reviews, with diners singling out the Shaam Savera and the rose-stuffed gulab jamun.

## Diaspora Impact

For Bay Area NRIs, the arrival of a familiar name carries an emotional charge that goes beyond convenience. Sanjeev Kapoor is not an abstraction; he is the voice that played in the background of countless immigrant kitchens, a comforting constant for families rebuilding their food traditions thousands of miles from home. To eat at his restaurant is, in a small way, to close the distance.

It also signals a maturing market. Silicon Valley's Indian population — swollen by waves of H-1B engineers and second-generation professionals — now commands the spending power to sustain branded, premium-priced concepts. The corner curry house with the worn vinyl menu is no longer the only option, nor the aspirational one. The diaspora is being courted, and the brands know it.

## What's Next

The real question is whether the celebrity-chef chain model scales in America the way it has across the Gulf. SK Restaurants has signalled appetite for further U.S. growth, and rivals are watching closely. If Santa Clara succeeds, expect a rush of recognisable Indian names — chefs, regional chains, sweet-shop brands — to follow the diaspora into the suburbs of Texas, New Jersey and the Pacific Northwest.

For now, the test is simpler and more personal. Can a dish that millions first watched being made on a flickering television screen taste, in a Santa Clara dining room, exactly the way memory insists it should? On that question, the diaspora will be the toughest critic of all.

*Sources: Restaurant Business Online, The Mercury News, Irvine Company Retail, OpenTable*"""
})

# ─── Article 2: Paneer's protein moment ───
articles.append({
    'headline': "Paneer's American Moment: How India's Cottage Cheese Became a Protein Darling",
    'subheadline': "Amid a national cottage-cheese shortage and an insatiable hunger for protein, India's 500-year-old fresh cheese is being reinvented by startups and embraced by mainstream shoppers far beyond the saag.",
    'image_url': "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Paneer_Butter_Masala_3.jpg/1280px-Paneer_Butter_Masala_3.jpg",
    'image_caption': "Paneer butter masala, featuring cubes of India's firm fresh cheese in a rich tomato gravy",
    'image_attribution': "Wikimedia Commons",
    'body': """America is in the grip of a protein obsession. Walk any supermarket aisle and the evidence is everywhere: protein cereals, protein chips, protein water, and above all the once-humble cottage cheese, resurrected by TikTok into a creamy, scoopable status symbol. Demand has run so hot that shelves have periodically gone bare, with dairy manufacturers scrambling to shift capacity from yogurt back to curds. Into this frenzy steps an unlikely contender that India perfected five centuries ago: paneer.

## Context & Background

Paneer — the firm, unaged fresh cheese that anchors vegetarian Indian cooking from saag paneer to paneer tikka — is, on paper, almost engineered for the moment. It is high in protein, clean-label by nature (typically just milk and an acid like lemon juice or vinegar), and, crucially, it does not melt. That last property makes it a rare thing: a centre-of-the-plate vegetarian protein that holds its shape on the grill, in the curry, or seared in a pan. For a country full of people trying to eat less meat without surrendering texture, paneer answers a question Western food technologists have spent fortunes trying to solve.

The groundswell is not new, but it is accelerating. U.S. curd consumption has climbed nearly a fifth over the past decade, and paneer has ridden that wave from the back of the international aisle toward the mainstream dairy case. Whole Foods product developers have publicly noted sustained category growth, crediting both the keto crowd — for whom paneer's protein-and-fat profile is ideal — and a broad surge of interest in cooking Indian food at home. Online searches for "paneer maker" have spiked, a small but telling sign of a cheese moving from restaurant order to home project.

## Current Developments

The clearest signal that paneer has arrived is that American food entrepreneurs are now building businesses around it. This year's Midwest Dairy Accelerator — a competitive cohort backed by the regional dairy industry to spotlight the most promising startups — selected **MOOJ Foods**, a Chicago venture founded by Ritu Sreenivasan that is "modernizing traditional paneer with a high-protein, lower-fat dairy product designed for everyday cooking across a wide range of cuisines." That a paneer startup now sits alongside whipped cottage-cheese dips and high-protein cheese snacks in a mainstream dairy accelerator is a milestone in itself: paneer is no longer being pitched as ethnic specialty food, but as a versatile, protein-forward American pantry staple.

Researchers, too, are racing to reinvent it. Food scientists from India to the University of Copenhagen have been formulating hybrid paneers — blending dairy casein with pea, peanut, millet or mung-bean protein — to cut fat, add fibre and shrink the climate footprint while preserving the springy bite that makes paneer paneer. One Copenhagen team found it could replace a quarter of the milk protein with pea protein and still produce a cheese with near-identical texture and taste. The subtext is unmistakable: a 500-year-old Indian staple has become a serious object of global food innovation.

## Diaspora Impact

For Indian-Americans, paneer's mainstreaming is a quietly vindicating spectacle. For decades, the cheese that NRIs hauled home from Patel Brothers or pressed themselves on weekend afternoons was invisible to the wider culture — a curiosity, if it was noticed at all. Now non-Indian shoppers are tossing it into their carts as a protein hack, and a national accelerator is funding its reinvention.

There is a flicker of irony in watching a food long dismissed as niche get rebranded as cutting-edge wellness. But there is also opportunity. Diaspora food brands that have quietly supplied paneer to Indian grocery shelves for years are suddenly positioned at the centre of one of the fastest-growing categories in American dairy. The familiar block of cheese in the home fridge is, improbably, a growth market.

## What's Next

Expect paneer to keep climbing — into more conventional grocery chains, into protein-marketing language ("X grams per serving" splashed across the package), and into formats Indian grandmothers would barely recognise: pre-cubed, pre-marinated, air-fryer-ready, even blended into spreads and snacks. The hybrid versions emerging from research labs may reach shelves within a few years, pitched as lighter and greener.

Whether any of it tastes as good as paneer made fresh that morning is, of course, the eternal question. But for a cheese that has fed the subcontinent since the time of the Mughals, a belated American spotlight is sweet validation — high in protein, and richer still in meaning.

*Sources: AARP, The Hindu BusinessLine, Protein Production Technology News, AdvFN / Midwest Dairy Accelerator*"""
})

# ─── Article 3: Chutney / condiment flights ───
articles.append({
    'headline': "The Chutney Awakening: How America Discovered the Sauce India Never Lost",
    'subheadline': "As 'condiment flights' go viral in American restaurants and one in five diners admits to smuggling their own sauces to the table, Indian chefs are pointing out, politely, that they have been doing this for generations.",
    'image_url': "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Coconut_Chutney_%28Indian_Cuisine%29.jpg/1280px-Coconut_Chutney_%28Indian_Cuisine%29.jpg",
    'image_caption': "Fresh coconut chutney, a staple South Indian accompaniment served alongside dosa and idli",
    'image_attribution': "Wikimedia Commons",
    'body': """A peculiar trend has swept American dining rooms: the "condiment flight." Restaurants from Texas to the coasts now present diners with little trios of dips and sauces — guacamole, queso, hummus; or beer cheese, French onion, mustard — arranged like a tasting menu of accompaniments. A recent survey found that one in five Americans now admits to sneaking their own sauces into restaurants, so deep is the national craving for something to dunk, drizzle and dab. To Indian chefs watching this unfold, the reaction has been a knowing smile. America, they note gently, has just rediscovered the chutney.

## Context & Background

In Indian cooking, the sauce was never an afterthought. Chutneys, raitas and pickles are not garnishes bolted onto a plate; they are structural, designed to balance and complete a meal. "Mango chutney, tamarind sauce, mint-coriander chutney and yogurt-based sauces are all designed to balance spice, acidity, sweetness and freshness," explained Sanwar Mal Khokhar, a bar manager at Sanjh, a high-end Indian restaurant in Texas. "Each creates a different flavor experience." Put a dosa in front of any South Indian and it arrives with a flight of its own: coconut chutney, tomato chutney, a fiery gunpowder, a bowl of sambar. The "flight" is not an innovation there. It is the default.

"In many ways, what American restaurants call condiment flights has existed in Indian food culture for generations," Khokhar observed — a remark that lands somewhere between pride and gentle exasperation. The chutney is, in this telling, one of the original modular flavour systems: a way to let every diner tune a dish to their own palate, sweet to searing, in a single meal.

## Current Developments

The mainstreaming of the chutney is happening on two fronts at once. In restaurants, sauces have become a cheap, high-margin route to personality — "they don't cost much to produce, but they add personality to a dish and make it more memorable," as one operator put it. That logic plays directly to Indian cuisine's strengths, and modern Indian restaurants across America are leaning in, building entire chutney bars and elevating the humble accompaniment into a marquee feature.

On grocery shelves, Indian condiments are quietly conquering the American pantry. Mango chutney, tamarind concentrate, mint-coriander pastes and the now-ubiquitous chili crisp variants have moved from the international aisle into mainstream sets at Whole Foods, Trader Joe's and Costco. Diaspora-founded brands have raised serious capital on the bet that the American appetite for bold, dunkable, shelf-stable flavour is just getting started — and that the chutney, perfected over centuries, is ready-made for it.

## Diaspora Impact

For Indian-Americans, the chutney's moment carries a familiar bittersweetness. The same condiments that drew wrinkled noses in school cafeterias — the "smelly" pickle, the green chutney that stained the lunchbox — are now being repackaged as adventurous, premium, even aspirational. A jar of achaar that an aunty once apologised for is now a $9 artisanal product with a minimalist label and a waitlist.

But beneath the irony lies genuine affirmation. Chutney-making is intimate knowledge, passed mother to daughter, each household guarding its own ratio of tamarind to jaggery, its own grind of coconut and chana dal. To see that knowledge validated — to watch non-Indian diners chase the precise balance of sweet, sour, salt and heat that Indian cooks have engineered for generations — is to see a piece of culinary heritage finally recognised as the sophistication it always was.

## What's Next

Expect the chutney to keep climbing the prestige ladder: chef-driven chutney pairings on tasting menus, regional chutneys (Bengali, Tamil, Maharashtrian) marketed with the same specificity Americans once reserved for olive oils, and a continued grocery-aisle land grab by diaspora brands. The condiment flight, in other words, is not a fad India needs to catch up to. It is a homecoming for a tradition that never left — and the rest of the table is finally pulling up a chair.

*Sources: Fox News Digital, Southern Living, Restaurant Business Online, The Videshi reporting*"""
})

if __name__ == '__main__':
    existing = get_existing_headlines()
    print(f"Loaded {len(existing)} existing food headlines for dedup.\n")
    published = 0
    for art in articles:
        if publish_article(art, existing):
            published += 1
    print(f"\nDone. Published {published}/{len(articles)} articles.")
