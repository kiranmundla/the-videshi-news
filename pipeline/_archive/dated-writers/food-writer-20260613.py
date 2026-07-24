#!/usr/bin/env python3
"""
Food Writer — June 13, 2026
Writes 3 food articles for The Videshi
Topics:
1. James Beard Awards 2026 - Indian restaurants/chefs dominating (ceremony June 15!)
2. Dishoom's NYC debut - London's cult Indian restaurant crosses the Atlantic
3. 2026 Global Indian Restaurant Awards - Sanjeev Kapoor, Tresind, Cinnamon Club
"""
import os, json, re, requests, sys, subprocess
from datetime import datetime, timezone

# ── Load env ──
with open(os.path.expanduser('~/workspace/.env.supabase')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('export '): line = line[7:]
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ[k] = v.strip('"')

with open(os.path.expanduser('~/workspace/.env.pexels')) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k] = v.strip('"')

SB_URL = os.environ['SUPABASE_URL']
PEXELS_KEY = os.environ['PEXELS_API_KEY']

# ── Get service role key ──
with open('/tmp/sb_service_key.txt') as f:
    SB_KEY = f.read().strip()
print(f"Service role key loaded (length={len(SB_KEY)}, jwt={SB_KEY.startswith('eyJ')})")

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
            'limit': 25,
            'select': 'headline,slug'
        },
        headers=HEADERS
    )
    if resp.status_code == 200:
        return [a['headline'].lower() for a in resp.json()]
    print(f"Warning: Could not fetch existing articles: {resp.status_code}")
    return []

def is_duplicate(headline, existing):
    norm = re.sub(r'[^a-z0-9 ]', '', headline.lower()).strip()[:40]
    for ex in existing:
        ex_norm = re.sub(r'[^a-z0-9 ]', '', ex).strip()[:40]
        if norm == ex_norm:
            return True
    return False

def search_wikimedia_commons(query):
    """Search Wikimedia Commons for CC images."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': query,
        'gsrnamespace': '6',
        'gsrlimit': '5',
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': '1200',
        'format': 'json'
    }
    headers = {'User-Agent': 'TheVideshi/1.0 (contact@thevideshi.com)'}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get('query', {}).get('pages', {})
            for pid, page in pages.items():
                ii = page.get('imageinfo', [{}])[0]
                img_url = ii.get('thumburl') or ii.get('url', '')
                mime = ii.get('mime', '')
                size = ii.get('size', 0)
                if 'image' in mime and size > 5000 and 'upload.wikimedia.org' in img_url:
                    return img_url
    except Exception as e:
        print(f"  Commons search failed: {e}")
    return None

def search_wikipedia_image(topic):
    """Get image from Wikipedia REST API."""
    topic_clean = topic.replace(' ', '_')
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic_clean}"
    headers = {'User-Agent': 'TheVideshi/1.0'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            img = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
            if img and 'upload.wikimedia.org' in img:
                return img
    except Exception as e:
        print(f"  Wikipedia image search failed for {topic}: {e}")
    return None

def search_pexels(query):
    """Search Pexels for food images."""
    from urllib.parse import quote_plus
    encoded_query = quote_plus(query)
    try:
        result = subprocess.run(
            ['curl', '-sS', f'https://api.pexels.com/v1/search?query={encoded_query}&per_page=5',
             '-H', f'Authorization: {PEXELS_KEY}'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for photo in data.get('photos', []):
                img_url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                if img_url and 'images.pexels.com' in img_url:
                    print(f"    Pexels found: {img_url[:80]}")
                    return img_url
            print(f"    Pexels: {len(data.get('photos', []))} results but none valid")
        else:
            print(f"    Pexels curl failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"  Pexels search failed: {e}")
    return None

def validate_image(url):
    """Verify image URL returns valid image with sufficient size."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']
    for b in banned:
        if b in url:
            print(f"  BANNED source detected: {b}")
            return False
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True, headers={'User-Agent': 'TheVideshi/1.0'})
        content_type = resp.headers.get('Content-Type', '')
        content_length = int(resp.headers.get('Content-Length', 0))
        print(f"    Validate: status={resp.status_code} type={content_type[:20]} len={content_length}")
        if resp.status_code == 200 and 'image' in content_type and content_length > 5000:
            return True
        # Some servers don't support HEAD properly, try GET with stream
        if resp.status_code != 200 or content_length == 0:
            resp = requests.get(url, timeout=10, stream=True, allow_redirects=True, headers={'User-Agent': 'TheVideshi/1.0'})
            ct = resp.headers.get('Content-Type', '')
            cl = int(resp.headers.get('Content-Length', 0))
            print(f"    Validate GET: status={resp.status_code} type={ct[:20]} len={cl}")
            if resp.status_code == 200 and 'image' in ct:
                return True
    except Exception as e:
        print(f"    Image validation failed: {e}")
    return False

def find_image(topics_wiki, topics_commons, topics_pexels):
    """Multi-source image search: Wiki > Commons > Pexels. Returns (url, attribution)."""
    # Try Wikipedia first
    for topic in topics_wiki:
        print(f"  Trying Wikipedia: {topic}")
        img = search_wikipedia_image(topic)
        if img and validate_image(img):
            print(f"  ✓ Wikipedia image found")
            return img, "Wikimedia Commons"

    # Try Wikimedia Commons
    for topic in topics_commons:
        print(f"  Trying Commons: {topic}")
        img = search_wikimedia_commons(topic)
        if img and validate_image(img):
            print(f"  ✓ Commons image found")
            return img, "Wikimedia Commons"

    # Try Pexels (food/dish only, not people)
    for topic in topics_pexels:
        print(f"  Trying Pexels: {topic}")
        img = search_pexels(topic)
        if img and validate_image(img):
            print(f"  ✓ Pexels image found")
            return img, "Pexels"

    return None, None

def publish_article(article, existing_headlines):
    """Insert article into Supabase."""
    headline = article['headline']
    if is_duplicate(headline, existing_headlines):
        print(f"  ⚠ SKIPPING duplicate: {headline}")
        return False

    slug = make_slug(headline)
    now = datetime.now(timezone.utc).isoformat()

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
        'is_editorial': False
    }

    resp = requests.post(
        f'{SB_URL}/rest/v1/p2_articles',
        headers=HEADERS,
        json=payload
    )
    if resp.status_code in (200, 201):
        result = resp.json()
        article_id = result[0]['id'] if isinstance(result, list) else result.get('id', 'unknown')
        print(f"  ✓ Published: {headline}")
        print(f"    slug: {slug}")
        print(f"    id: {article_id}")
        return True
    else:
        print(f"  ✗ Failed to publish: {resp.status_code} - {resp.text[:200]}")
        return False


# ──────────────────────────────────────────────────────────────
# ARTICLES
# ──────────────────────────────────────────────────────────────

articles = []

# ── ARTICLE 1: James Beard Awards 2026 ──
print("\n📝 Writing Article 1: James Beard Awards 2026...")

article1_body = """The James Beard Foundation will announce its 2026 Restaurant and Chef Award winners in Chicago on Sunday, June 15 — and Indian cuisine has never had a stronger presence on the finalist ballot.

From a reimagined Las Vegas landmark to the street-food pioneers of Asheville, North Carolina, Indian-American chefs and restaurateurs occupy some of the most competitive categories in what the industry calls the Oscars of the food world. Their collective showing marks a turning point: this is no longer a breakout moment, but an arrival.

## The Finalists

**Tamba**, the modern Indian restaurant at Town Square in Las Vegas, is a finalist for Best New Restaurant — one of only ten concepts nationwide to earn the nod in its first year of existence. The restaurant's origin story spans three decades and two continents. Daljit and Jatinder Dhillon, Punjabi immigrants, opened India's Clay Oven in Monterey, California in 1989. Their son Sunny Dhillon grew up in those kitchens and revived the family name in late 2024, hiring Executive Chef Anand Singh — born in the Himalayan foothills of Uttarakhand, trained across six countries — to helm a menu that reimagines Indian regional specialties with Art Deco flourishes evoking 1930s Mumbai. The restaurant's name means "copper" in Hindi, a metal considered sacred in Indian tradition.

In the Outstanding Restaurateur category, two Indian-led hospitality groups are finalists. **Srijith Gopinathan and Ayesha Thapar** of the Cal-India Collective — the group behind Ettan in Palo Alto, Copra in San Francisco, and the Michelin-listed Eylan in Menlo Park — represent the Peninsula's contemporary Cal-Indian dining movement. And **Meherwan and Molly Irani** of the Chai Pani Restaurant Group are back after winning the Outstanding Restaurant award in 2022 for their flagship Asheville location. The couple recently expanded to Washington, D.C.'s Union Market, and Meherwan has just published a cookbook diving into why chai should be made with "substandard tea leaves" and why naan doesn't appear at every Indian meal.

In the Best Chef: Mid-Atlantic category, **Suresh Sundas**, chef and co-owner of modern Indian restaurants Tapori and Daru in Washington, D.C., is the sole non-Pennsylvania finalist — a significant achievement in one of the country's deepest culinary regions.

## A Broader Pattern

The James Beard nominations do not exist in isolation. Earlier this year, Indibar in Phoenix and Nadu — the regional Indian concept by Michelin-starred chef Sujan Sarkar — were both named James Beard semifinalists for Best New Restaurant. Sarkar has been on a tear: he brought his Chicago fine-dining concept Indienne to New York's Hudson Yards in May, with plans for a cocktail bar called Apas and a British-Indian chophouse called Elder to follow.

Globally, the validation is accelerating. Tresind Studio in Dubai became the first Indian restaurant to hold three Michelin stars. India's Masque climbed to No. 15 on Asia's 50 Best Restaurants list for 2026, winning the Art of Hospitality Award — the first time an Indian establishment has received the honour. And La Liste's 2026 edition featured fourteen Indian restaurants, up from six in 2022.

## What It Means for the Diaspora

For the 5.1 million Indians living in the United States, the James Beard recognition carries a personal weight that transcends culinary prestige. These are not celebrity chefs flown in for a pop-up — they are immigrants, their children, and their communities, building generational businesses that translate the memory of Indian kitchens into something the American establishment now recognises as world-class.

The Dhillon family's thirty-year journey from a small Monterey restaurant to a James Beard finalist in Las Vegas is a quintessentially NRI arc. So is Meherwan Irani's mission to change American perceptions of Indian food, one plate of okra fries at a time.

## What's Next

Winners will be announced at the ceremony in Chicago on Sunday. Regardless of who takes home the awards, the 2026 ballot has already made its statement: Indian cuisine in America is no longer emerging. It has emerged."""

article1 = {
    'headline': "Copper, Chai, and the Oscars of Food: Indian Restaurants Own the 2026 James Beard Ballot",
    'subheadline': "From a reimagined Las Vegas landmark to Asheville street food, Indian-American chefs and restaurateurs dominate the finalist list ahead of Sunday's ceremony.",
    'body': article1_body,
    'image_caption': None,
    'image_attribution': None,
    'image_url': None
}

# Find image for article 1
print("  Finding image for Article 1...")
img_url, img_attr = find_image(
    topics_wiki=["James_Beard_Award", "Chai_Pani"],
    topics_commons=["Indian restaurant fine dining", "modern Indian cuisine"],
    topics_pexels=["Indian fine dining restaurant elegant", "modern Indian cuisine plating"]
)
if img_url:
    article1['image_url'] = img_url
    article1['image_attribution'] = img_attr
    article1['image_caption'] = "A modern Indian fine dining presentation showcasing the elevated cuisine now earning America's top culinary honors"
articles.append(article1)


# ── ARTICLE 2: Dishoom NYC ──
print("\n📝 Writing Article 2: Dishoom NYC...")

article2_body = """London's most beloved Indian restaurant is finally crossing the Atlantic — and New York is already lining up.

Dishoom, the Bombay-café-inspired chain that has become a cultural institution in Britain, will open its first American outpost in lower Manhattan later this year. The restaurant's U.S. debut comes on the heels of a £300 million investment from L Catterton, the private equity firm backed by LVMH, valuing the brand at a level that puts it alongside some of Europe's most coveted consumer brands.

## A 7,000-Person Audition

The move to New York is not a leap of faith. In the summer of 2024, Dishoom staged a two-week breakfast pop-up at Pastis in the Meatpacking District. Reservations sold out in under five minutes. The pop-up served approximately 7,000 people, with another 20,000 on the waitlist. Co-founder Kavi Thakrar told the *New York Times* he had been eyeing Manhattan since 2016, but the cultural moment had not been right until now.

"There are so many young professionals, second-generation, third-generation people running businesses," Thakrar said. "Indian food is finally part of the city's fabric."

## The Dishoom Formula

For the uninitiated — and for NRIs who have been making Dishoom pilgrimages on London visits for years — the restaurant draws on the vanished Irani cafés of Bombay, establishments run by Zoroastrian immigrants from Iran that once numbered nearly 400 in the city and now survive as a handful. The aesthetic is retro glamour: ceiling fans, bentwood chairs, Art Deco tilework, and a warm, sepia-toned atmosphere that evokes a Bombay that existed before the city became Mumbai.

The menu is comfort-forward but precise. The house black daal, simmered for 24 hours, is the signature — rich, smoky, and impossible to replicate at home no matter how many YouTube tutorials you follow. Bacon naan rolls have become a cult breakfast item in Britain. The chicken ruby curry, the keema pau, and the lamb biryani complete a menu designed to feel like the best meal your coolest aunt might cook, if she had a professional kitchen and twenty prep cooks.

Since opening its first restaurant in Covent Garden in 2010, Dishoom has expanded to eleven locations across the U.K. and four Permit Room bars. It serves more than 100,000 diners per week and employs around 2,000 people.

## Part of a Larger Wave

Dishoom is not arriving alone. The past eighteen months have seen a procession of British Indian restaurants heading for American shores. JKS Restaurants brought its Michelin-starred Gymkhana to the Aria Resort & Casino in Las Vegas and launched Ambassadors Clubhouse, a Punjabi-focused concept, in Manhattan. Asma Khan's Darjeeling Express and the Indian small-plates restaurant Kricket are both eyeing 2026 Manhattan launches.

Combined with the surge of American-born Indian concepts — Indienne, Tamba, Semma, Nadu — the result is a landscape where Indian food in America is being defined simultaneously from multiple directions: regional authenticity, diasporic memory, fine-dining precision, and street-food accessibility.

## The Diaspora Angle

For Indian Americans, Dishoom's arrival carries a particular resonance. Many NRIs first experienced the restaurant on London trips and wondered when — not if — it would reach the United States. The pop-up waitlist of 20,000 suggests the demand has been building quietly for years.

Dishoom plans to open two to three U.S. locations per year following the New York launch, with Boston, Chicago, and Washington, D.C. all previously scouted. CEO Brian Trollip has said the company "doesn't grow for growth's sake," but the L Catterton investment and the scale of American demand suggest the pace could quicken.

## What's Next

An exact Manhattan address and opening date remain under wraps. What is known: the house black daal will make the crossing. For 20,000 people who could not get a seat at the Pastis pop-up, that is the only detail that matters."""

article2 = {
    'headline': "Dishoom Crosses the Atlantic: London's Cult Indian Restaurant Bets Big on New York",
    'subheadline': "Backed by £300 million from LVMH-linked investors, the beloved Bombay-café chain is opening in lower Manhattan after a pop-up that drew 20,000 to the waitlist.",
    'body': article2_body,
    'image_caption': None,
    'image_attribution': None,
    'image_url': None
}

print("  Finding image for Article 2...")
img_url, img_attr = find_image(
    topics_wiki=["Dishoom_(restaurant)", "Irani_café"],
    topics_commons=["Bombay Irani cafe interior", "black dal Indian"],
    topics_pexels=["Indian restaurant interior warm lighting", "black dal lentil Indian dish"]
)
if img_url:
    article2['image_url'] = img_url
    article2['image_attribution'] = img_attr
    article2['image_caption'] = "The warm retro ambiance of a Bombay-inspired café, the aesthetic that made Dishoom a British institution"
articles.append(article2)


# ── ARTICLE 3: 2026 Global Indian Restaurant Awards ──
print("\n📝 Writing Article 3: Global Indian Restaurant Awards...")

article3_body = """The 2026 Global Indian Restaurant Awards have crowned their winners — and the roll call reads like a who's who of Indian culinary royalty, from a Michelin-star legend to a London institution that has been redefining Indian fine dining for two decades.

The inaugural awards, announced at a ceremony in London, honoured establishments and chefs whose work has elevated Indian cuisine's standing on the world stage. The winners were evaluated by a panel including former BBC journalist George Shaw, renowned food critic Andy Hayler, and celebrated TV host Rashmi Uday Singh.

## The Winners

**Sanjeev Kapoor**, the chef, restaurateur, and television personality who introduced millions of Indians to cooking through *Khana Khazana*, was named Global Indian Chef of the Year. For NRIs of a certain generation, Kapoor's show was the soundtrack to weekend afternoons — and his commercial empire, spanning restaurants, cookbooks, and packaged foods, has made him arguably the most recognised Indian chef alive.

**Atul Kochhar**, who in 2001 became one of the first Indian chefs to receive a Michelin star in Britain, received the Culinary Excellence Award. Kochhar has been a quiet but persistent force in proving that Indian cuisine deserves the same critical attention as French or Japanese — a battle that, two decades in, he appears to have won.

**The Cinnamon Club**, the Westminster institution that has served modern Indian cuisine to politicians, business leaders, and discerning diners for over twenty years, was named Global Indian Restaurant of the Year. The award recognised both its culinary consistency and its role in making Indian food a fixture of London's power-dining scene.

Other notable winners included **Jamavar** (Best Indian Restaurant Brand), **Benares Restaurant & Bar** (Best Chef-Led Restaurant), and the **Tresind** group (Restaurant Group of the Year) — the Dubai-based hospitality company that also operates the three-Michelin-starred Tresind Studio, the first Indian restaurant anywhere to achieve that distinction.

## What the Awards Reveal

The Global Indian Restaurant Awards arrive at a moment when Indian cuisine's international infrastructure is maturing rapidly. A decade ago, the conversation was about whether Indian food could compete at the highest levels of fine dining. Today, the question has shifted to how many different registers Indian cuisine can occupy simultaneously — from Tresind Studio's molecular gastronomy to Chai Pani's okra fries to Dishoom's comfort-forward Bombay café cooking.

The award for **Café Spice Namasté** (Culinary Heritage Award) is telling. The East London restaurant, opened by Cyrus Todiwala in 1995, represents a generation of Indian restaurants in Britain that laid the groundwork for the current renaissance — the establishments that fought to be taken seriously when Indian food was still largely associated with late-night curry houses and £5.99 all-you-can-eat buffets.

## The Diaspora Dimension

For NRIs watching from the United States, Canada, and the Gulf, the awards highlight both the progress and the geography of Indian fine dining's recognition. Britain and the UAE continue to lead — unsurprisingly, given the depth and affluence of their Indian diaspora communities. But the momentum is shifting. With Indian restaurants now claiming James Beard nominations in the United States and Michelin stars across multiple continents, the infrastructure of recognition is finally catching up with the quality of the food.

**Dastaan**, the winner of Best Indian Neighbourhood Restaurant, embodies this grassroots quality. Based in Epsom, Surrey, the restaurant has earned a devoted following by serving ambitious regional Indian food outside central London's spotlight — proving that excellence does not require a prime postcode.

## What's Next

The Global Indian Restaurant Awards plan to expand their scope in future years to include restaurants across North America and the Asia-Pacific region. For now, the inaugural winners have set a benchmark — and given NRIs everywhere a dining bucket list for their next London trip."""

article3 = {
    'headline': "Sanjeev Kapoor, The Cinnamon Club, and Tresind: The 2026 Global Indian Restaurant Awards",
    'subheadline': "The inaugural awards honour a generation of chefs and restaurants that elevated Indian cuisine from curry-house stereotype to global fine dining force.",
    'body': article3_body,
    'image_caption': None,
    'image_attribution': None,
    'image_url': None
}

print("  Finding image for Article 3...")
img_url, img_attr = find_image(
    topics_wiki=["Sanjeev_Kapoor", "The_Cinnamon_Club"],
    topics_commons=["Indian fine dining plating award", "Indian cuisine elegant presentation"],
    topics_pexels=["Indian fine dining elegant plating", "gourmet Indian food presentation award"]
)
if img_url:
    article3['image_url'] = img_url
    article3['image_attribution'] = img_attr
    article3['image_caption'] = "The elevated presentation of modern Indian fine dining, the style now earning global recognition"
articles.append(article3)


# ── PUBLISH ──
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)

existing = get_existing_headlines()
print(f"Found {len(existing)} existing food articles for dedup check")

published = 0
for i, article in enumerate(articles, 1):
    print(f"\n--- Article {i} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Subheadline: {article['subheadline']}")
    word_count = len(article['body'].split())
    print(f"  Word count: {word_count}")
    img_display = article.get('image_url') or 'None'
    print(f"  Image: {img_display[:80]}...")
    if publish_article(article, existing):
        published += 1
        existing.append(article['headline'].lower())

print(f"\n{'='*60}")
print(f"DONE — Published {published}/{len(articles)} articles")
print(f"{'='*60}")
