#!/usr/bin/env python3
"""
Food writer for The Videshi - 2026-06-04 evening run
Topics:
1. Chaiiwala UK chain launching in US
2. Progressive Indian restaurants redefining American dining
3. Viral dosa student and dosa's global rise
"""

import json, os, sys, re, time
from datetime import datetime, timezone

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip().strip('"').strip("'")
                os.environ[k] = v

load_env(os.path.expanduser('~/workspace/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/.env.supabase'))

import requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS_SB = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

def slug_from_headline(headline, max_len=80):
    s = headline.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s.strip())
    s = re.sub(r'-+', '-', s)
    if len(s) > max_len:
        s = s[:max_len].rsplit('-', 1)[0]
    return s

def search_pexels(query):
    if not PEXELS_KEY:
        return None, None, None
    try:
        r = requests.get(
            'https://api.pexels.com/v1/search',
            headers={'Authorization': PEXELS_KEY},
            params={'query': query, 'per_page': 5, 'orientation': 'landscape'},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if data.get('photos'):
                photo = data['photos'][0]
                url = photo['src']['large2x']
                alt = photo.get('alt', query)
                return url, alt, 'Pexels'
    except Exception as e:
        print(f"  Pexels error: {e}")
    return None, None, None

def search_wikimedia(query):
    try:
        r = requests.get(
            'https://commons.wikimedia.org/w/api.php',
            params={
                'action': 'query',
                'generator': 'search',
                'gsrsearch': query,
                'gsrnamespace': 6,
                'gsrlimit': 5,
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime',
                'iiurlwidth': 1200,
                'format': 'json'
            },
            headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            pages = data.get('query', {}).get('pages', {})
            for pid, page in pages.items():
                info = page.get('imageinfo', [{}])[0]
                mime = info.get('mime', '')
                if mime.startswith('image/') and 'svg' not in mime:
                    url = info.get('thumburl') or info.get('url')
                    if url:
                        return url, page.get('title', query).replace('File:', ''), 'Wikimedia Commons'
    except Exception as e:
        print(f"  Wikimedia error: {e}")
    return None, None, None

def find_image(queries):
    """Try multiple search queries across Pexels and Wikimedia"""
    for q in queries:
        print(f"  Searching Pexels: '{q}'")
        url, alt, attr = search_pexels(q)
        if url:
            return url, alt, attr
    for q in queries:
        print(f"  Searching Wikimedia: '{q}'")
        url, alt, attr = search_wikimedia(q)
        if url:
            return url, alt, attr
    return None, None, None

def dedup_check(headline, existing_headlines):
    norm = re.sub(r'[^a-z0-9 ]', '', headline.lower())[:40]
    for eh in existing_headlines:
        en = re.sub(r'[^a-z0-9 ]', '', eh.lower())[:40]
        if norm == en:
            return True
    return False

def publish_article(headline, subheadline, content, image_url, image_caption, image_attribution, existing_headlines):
    if dedup_check(headline, existing_headlines):
        print(f"  SKIP (dedup): {headline[:60]}")
        return False
    
    now = datetime.now(timezone.utc).isoformat()
    slug = slug_from_headline(headline)
    
    payload = {
        'headline': headline,
        'subheadline': subheadline,
        'body': content,
        'category': 'food',
        'vertical': 'food',
        'status': 'published',
        'published_at': now,
        'slug': slug,
        'image_url': image_url,
        'image_caption': image_caption,
        'image_attribution': image_attribution,
        'is_editorial': False
    }
    
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=HEADERS_SB,
        json=payload,
        timeout=30
    )
    
    if r.status_code in (200, 201):
        result = r.json()
        aid = result[0]['id'] if isinstance(result, list) else result.get('id', '?')
        print(f"  PUBLISHED: {headline[:60]}... (id={aid})")
        return True
    else:
        print(f"  FAILED ({r.status_code}): {r.text[:200]}")
        return False

# Fetch existing headlines for dedup
print("Fetching existing food articles for dedup...")
r = requests.get(
    f'{SUPABASE_URL}/rest/v1/p2_articles',
    headers=HEADERS_SB,
    params={
        'category': 'eq.food',
        'order': 'published_at.desc',
        'limit': 30,
        'select': 'headline'
    },
    timeout=15
)
existing = [a['headline'] for a in r.json()] if r.status_code == 200 else []
print(f"Found {len(existing)} existing food articles")

# ============================================================
# ARTICLE 1: Chaiiwala crossing the Atlantic
# ============================================================
print("\n--- Article 1: Chaiiwala US Expansion ---")

a1_headline = "From Leicester to Houston: Chaiiwala, Britain's Indian Street Food Giant, Bets Big on America"
a1_subheadline = "With 115 UK stores, 23 Canadian outlets, and £89 million in annual sales, the karak chai and roti wrap chain is preparing to open its first permanent US location — and sees room for 900 more."

a1_content = """The first time most Houstonians tasted Chaiiwala's karak chai and Bombay bowls, it was from a pop-up stall in a strip-mall parking lot. The cups were paper, the tables folding, and the queues — to the surprise of even the organisers — stretched around the block.

That was earlier this year. By 2027, if all goes to plan, those paper cups will be permanent fixtures in restaurants from Texas to New York, as Britain's fastest-growing Indian street food chain mounts its most ambitious expansion yet: a full-scale launch into the United States.

## From a Leicester Market Stall to a Global Empire

Chaiiwala was founded in 2015 by Sohail Ali, Muhummed Ibrahim, and Mustafa Ismail in Leicester, a city in England's East Midlands with one of Britain's largest South Asian communities. The concept was disarmingly simple: authentic karak chai brewed the way it's made on Indian and Pakistani street corners, paired with street food staples like roti wraps, samosas, and Bombay bowls.

A decade later, Chaiiwala operates approximately 115 locations across the United Kingdom, including high streets, travel hubs, university campuses, and — most recently — Britain's first 24-hour Indian food drive-thru in Blackburn, Lancashire. Add 23 stores in Canada and a handful in Dubai, and the brand's global sales hit £89.4 million in 2024, a 35 percent jump from the previous year.

The numbers tell only part of the story. What Chaiiwala has done, quietly and methodically, is prove that Indian street food can work as a fast-casual format at scale — the same way Chipotle proved it for Mexican food and Panda Express for Chinese.

## Houston, We Have a Karak Chai

The choice of Houston as Chaiiwala's US beachhead was deliberate. The city is home to one of America's largest and fastest-growing South Asian populations, with an established appetite for authentic flavours. The pop-up series gave the brand a chance to test consumer response and court potential franchisees simultaneously.

"Our recent pop-up was a first taste for consumers in Houston — a city that we believe has great potential for Chaiiwala in the short-term — and a total success," said Nazibur Rahman, Chaiiwala's country manager for the US and Canada. "Now, we are focused on continuing our conversations with local partners and franchisees and bringing our high-quality, authentic menu to the market with a permanent fixture."

The brand's ambitions extend far beyond a single storefront. According to CFO Abdul Piranie, the company has scoped out potential for up to 900 store opportunities across the United States — a staggering figure that would make Chaiiwala one of the largest Indian food chains in North America if even a fraction of that target is met.

## The Fast-Casual Indian Opportunity

Chaiiwala's US push arrives at a moment when Indian cuisine is experiencing an unprecedented surge in American mainstream consciousness. Turmeric lattes are Starbucks staples, biryani bowls appear on Sweetgreen-style menus, and Michelin stars are landing on Indian restaurants from Chicago to San Francisco.

Yet the fast-casual Indian category remains remarkably underdeveloped. While Mexican, Chinese, Thai, and Japanese cuisines each have multiple nationwide chains, Indian food has no equivalent — no household name that serves millions of Americans daily.

The gap represents both the challenge and the opportunity. "Everyone loves Indian food, but Indian street food is becoming a more and more credible option for people, whether it's breakfast, lunch, or potentially in the evening," Piranie told The Grocer.

## What This Means for the Diaspora

For the estimated 4.8 million Indian Americans, Chaiiwala's arrival carries a different weight. It is the promise of accessible, affordable, everyday Indian food that doesn't require a sit-down restaurant or a trip to the ethnic grocery aisle. It is chai that tastes like home, served in three minutes through a drive-thru window.

Chaiiwala's high-protein breakfast wraps — which sold over a million units in their first 12 weeks in the UK — hint at the kind of menu innovation that bridges desi comfort with American convenience culture.

The brand's global target of 500 stores over the next decade may sound ambitious. But then again, so did the idea of selling karak chai from a market stall in Leicester."""

img1_url, img1_cap, img1_attr = find_image([
    "Indian street food chai tea",
    "karak chai masala tea preparation",
    "Indian chai street food stall"
])
if img1_cap and img1_attr:
    img1_caption = "A steaming cup of karak chai served alongside Indian street food snacks"
else:
    img1_caption = None

print(f"  Image: {img1_url}")
publish_article(a1_headline, a1_subheadline, a1_content, img1_url, img1_caption, img1_attr, existing)
existing.append(a1_headline)

# ============================================================
# ARTICLE 2: Progressive Indian restaurants redefining US dining
# ============================================================
print("\n--- Article 2: Progressive Indian Restaurants ---")

a2_headline = "Parle-G Ice Cream and Goat Brain Masala: The Restaurants Blowing Up America's Idea of Indian Food"
a2_subheadline = "From Badmaash's Punjabi steak frites in LA to Dishoom's £400 million arrival in New York, a new generation of Indian restaurants is tearing up the curry-house playbook."

a2_content = """At Badmaash in Los Angeles, dessert is an ice cream sandwich made with Parle-G biscuits — the iconic Indian cookie that practically every desi kid grew up dunking in chai. At Dhamaka in New York, the menu features Gurda Kapoora: goat kidney and testicles. At Indienne in Chicago, Michelin-starred chef Sujan Sarkar turns pani puri into éclairs.

None of these places look, feel, or taste like the Indian restaurant most Americans picture — the one with burgundy carpet, a $6.99 lunch buffet, and a rotating selection of creamy curries. And that is precisely the point.

## The Year the Rules Broke

2026 is shaping up to be the year progressive Indian cuisine goes from a niche dining movement to a nationwide phenomenon. The evidence is arriving from both sides of the Atlantic.

From London comes Dishoom, one of Britain's most beloved restaurant brands, which is preparing to open its first US location in New York City. The 12-unit chain, inspired by the Irani cafés of 1960s Bombay, reportedly attracted investment from private-equity firm L Catterton in a deal that valued the company at nearly $400 million.

Also crossing the pond is JKS Restaurants, which brought its acclaimed Gymkhana concept — named after the British-Indian members' clubs of the Raj era — to the Aria Resort & Casino in Las Vegas. The group also recently opened Ambassadors Clubhouse, a Punjabi-focused concept in Manhattan.

Meanwhile, US-based operators are expanding aggressively. Chef Sarkar is bringing Indienne from Chicago to Henry Hall in Hudson Yards this spring, with a cocktail bar called Apas and a British-Indian chophouse called Elder to follow. In Phoenix, Indibar is adding a 10-course tasting menu restaurant-within-a-restaurant called Lehr.

## "We Wanted to Blow It Up"

No one embodies the rebellion quite like Nakul Mahendro, co-founder of Badmaash, which means "scoundrel" in Hindi. When Nakul, his brother Arjun, and their father Pawan opened the first location in downtown LA in 2013, their hashtag was #fuckyourfavoriteIndianrestaurant.

"Your idea of an Indian restaurant is horrible," Mahendro told Restaurant Business Online. "Don't put me in that box."

The newest Badmaash location opened in Venice Beach recently with a full cocktail bar and a menu that includes Punjabi-spiced steak frites, lamb burgers, and bourbon cocktails with housemade date jam. A separate concept — Secret Indian Food Window by Badmaash — serves Indian tacos (butter chicken, short rib curry, Indian beef chorizo) from a window at the Pacific Electric music venue in Chinatown.

The old-school rap playlist, Bollywood classics projected on the wall, and servers trained to Hillstone Group standards are all part of a deliberate strategy. "We were the ones that kicked the door open," Mahendro said. "We literally jumped off the cliff thinking, 'Is this umbrella going to open so we can land safely?'"

## Unapologetic and Unflinching

In New York, Unapologetic Foods takes a different approach — not fusion, but fearless authenticity. At Adda, the "full Butter Chicken experience" features tableside presentation with locally sourced chicken, house-churned butters, charcoal-smoked tomatoes, and signature black daal. But the menu also includes Bheja Masala — goat brain with steamed egg, lamb butter, and pao — daring American diners to go beyond their comfort zones.

In San Francisco, Rivaaz Hospitality's Rooh has pioneered the "progressive Indian" label since its founding, and last month launched a national luxury catering division for modern Indian weddings and corporate events — a sign that the movement is spilling beyond restaurant walls.

## Why It Took So Long

Mahendro traces the progressive Indian movement back to 1998, when the late Floyd Cardoz opened Tabla with Danny Meyer's Union Square Hospitality Group. It earned three stars from the New York Times but closed in 2010. "That restaurant was 20 years before its time," Mahendro said.

The gap between then and now reflects a deeper problem: the perception of Indian chefs in the West. "The Indian chef is not as respected as the Italian chef or the French chef," he said. "When I say 'three-star Michelin chef,' you still picture a French dude in chef whites."

That image is changing. Sarkar sees it in his dining rooms, where the clientele has shifted from predominantly South Asian to a diverse cross-section. "Something good is happening," he said. "You'll see it evolve and get better."

## What It Means for NRIs

For Indian Americans who grew up eating extraordinary food at home but settling for mediocrity at restaurants, this moment is personal. These concepts are not dumbing Indian cuisine down for Western palates — they are turning the volume up, insisting that desi food belongs in the same conversation as French, Japanese, and Italian.

The day an Indian chef becomes as recognizable as Nobu Matsuhisa or Michael Chow will be the day the revolution is complete. That day, Mahendro suggests, is closer than most people think."""

img2_url, img2_cap, img2_attr = find_image([
    "modern Indian restaurant plating fine dining",
    "progressive Indian cuisine elegant",
    "Indian fine dining restaurant"
])
if img2_url:
    img2_caption = "Modern Indian fine dining with contemporary plating and vibrant spices"
else:
    img2_caption = None

print(f"  Image: {img2_url}")
publish_article(a2_headline, a2_subheadline, a2_content, img2_url, img2_caption, img2_attr, existing)
existing.append(a2_headline)

# ============================================================
# ARTICLE 3: Viral dosa student and dosa's global rise
# ============================================================
print("\n--- Article 3: Viral Dosa Student ---")

a3_headline = "The Dosa Missionary: How a College Musician's Classroom Cooking Reel Became a Global Sensation"
a3_subheadline = "Indian-origin musician Pranva Pannal founded the 'Dosa Student Organisation' and cooked fresh dosas for his classmates during a lecture — and nearly a million people watched."

a3_content = """The classroom is mid-lecture. Students are hunched over laptops. The professor is explaining something about credit allocation or cash flow — the details hardly matter, because in the back row, a young man is heating a griddle, spreading batter, and filling the room with the unmistakable aroma of a crispy dosa.

This is Pranva Pannal — known on Instagram as Pedda P — an Indian-origin musician studying at a US college who has turned his classroom into an impromptu South Indian kitchen. His viral video, in which he cooks fresh dosas with coconut chutney and potato masala and serves them to bemused classmates and a remarkably unfazed professor, has racked up 9.9 lakh views and 52,000 likes on Instagram.

"Not all heroes wear capes," one commenter wrote. "Some give food to hungry college kids."

## Spreading Dosa Awareness, One Griddle at a Time

What makes Pannal's stunt more than a one-off joke is what lies behind it: the Dosa Student Organisation, which he founded with a mission statement that reads like a manifesto for fermented-batter diplomacy. The organisation's goal is to "spread dosa awareness and best practices regarding making crispy dosas."

Its recruitment form makes clear that membership is open to all — "Brown, white, small, tall, round, square, whatever" — with a zero-discrimination policy. "It's no easy task," Pannal wrote, "but we are looking to recruit members across the globe, so we can make dosas and save lives."

The tongue-in-cheek earnestness is part of the charm. But beneath the humour lies something real: dosa, once a regional South Indian breakfast staple unknown outside Indian households, is rapidly becoming one of the world's most recognisable and beloved foods.

## From Chennai to Kyoto

The dosa's global journey extends far beyond American college campuses. In Kyoto, Japan, a restaurant called Tadka has become a viral sensation in its own right — not because of an Indian chef, but because it is run by two Japanese men who visit Chennai every six months, learn new recipes, practise until they achieve perfection, and add them to their menu.

"They visit Chennai once every six months, learn new dishes, practise it to perfection and add it to their menu," wrote Prasanna Karthik, a Fulbright Program Fellow, in a widely shared thread on X. The dedication of these Japanese dosa-makers to achieving authentic South Indian flavour — from the crispiness of the batter to the exact coconut-to-green-chilli ratio in the chutney — has resonated with food lovers worldwide.

In the United States, dosa has evolved from a dish found only at dedicated South Indian restaurants to a street food staple. Worcester's Indian Bites, which opened recently at the Worcester Public Market in Massachusetts, calls itself an "authentic Indian fast food" restaurant and features dosas alongside samosas, naan, and curry bowls. It's part of a broader trend of Indian street food concepts entering mainstream food halls and public markets.

## Why Dosa Travels So Well

The dosa's global rise is not accidental. It is naturally gluten-free, can be made vegan, requires no oven, and can be customised infinitely — from the classic masala dosa stuffed with spiced potatoes to cheese dosa, paneer dosa, and the controversial but Instagram-famous aam ras cheese dosa that divided the Indian internet last year.

The fermentation process gives the batter a complex, slightly sour flavour profile that food scientists describe as umami-adjacent — a quality that appeals across cultures. The cooking process itself is theatrical: the sizzle of batter hitting a hot tawa, the satisfying scrape as the dosa is spread thin, the golden crispness that forms in seconds.

It is, in short, the perfect food for the Instagram age — which is exactly how a musician from India ended up cooking one in an American lecture hall and launching a global conversation about fermented rice batter.

## The Diaspora Connection

For millions of Indian Americans, watching Pannal's classroom dosa video triggers a specific kind of nostalgia — the memory of weekend mornings when the sound of a dosa sizzling on a tawa was as reliable as an alarm clock. It's the smell of home, served with sambar and a side of cultural pride.

"Watch out, Saravana Bhavan! We have a new competitor," one commenter joked, referencing the legendary South Indian restaurant chain that has expanded to over 80 locations worldwide.

Whether Pannal's Dosa Student Organisation will achieve its stated goal of global dosa domination remains to be seen. But if one musician with a griddle and a dream can get nearly a million people to watch a dosa being made in a college classroom, the batter is clearly ready to spread."""

img3_url, img3_cap, img3_attr = find_image([
    "dosa Indian crispy crepe",
    "masala dosa South Indian food",
    "dosa preparation Indian street food"
])
if img3_url:
    img3_caption = "A golden masala dosa served with coconut chutney and sambar on a traditional plate"
else:
    img3_caption = None

print(f"  Image: {img3_url}")
publish_article(a3_headline, a3_subheadline, a3_content, img3_url, img3_caption, img3_attr, existing)

print("\n=== Food writer run complete ===")
