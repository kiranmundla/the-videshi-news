#!/usr/bin/env python3
"""NRI World writer — 2026-07-15 01:00 PDT run."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Indian Cuisine CPG Invasion ───────────────────────────

article1_body = """Indian cuisine's American conquest has reached a new front: the grocery aisle.

Gymkhana Fine Foods, an offshoot of the Michelin-starred London restaurant, has launched a line of simmer sauces and marinades in Whole Foods Markets nationwide. The move arrives alongside an $8.5 million Series A funding round led by CAVU Consumer Partners — the firm co-founded by Rohan Oza, better known as the "Shark Tank" investor who helped build Vitaminwater and Popchips into household names.

The deal marks a telling shift. For decades, Indian flavours in American supermarkets meant a dusty jar of tikka masala paste tucked between the soy sauce and sriracha. Now the money flowing into the category is the kind usually reserved for plant-based protein or premium pet food.

## From White Tablecloth to Whole Foods

Gymkhana is no newcomer. Operated by London-based JKS Restaurants — founded by siblings Jyotin, Karam, and Sunaina Sethi — the group runs more than thirty Indian restaurant concepts and holds eight Michelin stars and six Bib Gourmand mentions across its portfolio. The restaurant made its American debut last year at the Aria Resort & Casino in Las Vegas.

The consumer-packaged-goods line, co-founded with Gulrez Arora, who helped build the brand's retail presence in the United Kingdom, is designed to bring the same flavour profile into home kitchens. "Each sauce, marinade, and chutney has been created to deliver the same bold, authentic flavours found in our restaurants," said Karam Sethi, culinary and creative director for JKS. "Our aim remains the same: to offer Indian cuisine in its purest form, whether you're cooking in your own kitchen or dining with us."

The bet is that Indian food has crossed the threshold from "ethnic aisle curiosity" to mainstream weeknight staple — and that American home cooks are ready to pay a premium for restaurant-quality shortcuts.

## A Wider Landing

Gymkhana is not alone on the runway. Farzi Café, the popular bistro chain run by Zorawar Kalra — son of the legendary Jiggs Kalra, once called the "czar of Indian cuisine" — has opened its first American outlet in Bellevue, Washington. Kalra, who oversees more than two dozen restaurants across eleven countries, described the launch as the first step in a coast-to-coast expansion aimed at making "Indian cuisine a mainstream cuisine across the US."

Meanwhile, Dishoom, the Bombay-inspired café chain that has become something of a cult brand in Britain, secured investment from L Catterton, the LVMH-linked private-equity firm, for its own American entry. And celebrity chef Sanjeev Kapoor's Yellow Chilli chain is planning its first US branch in Santa Clara, California.

## Why Now?

The timing is not accidental. Indian Americans are the second-largest immigrant group in the United States, with over 5.4 million people according to Ministry of External Affairs data. A generation that grew up eating dal and roti at home and explaining it to college roommates is now old enough to run venture funds — and hungry enough to back the food they actually want to eat.

Investors see the arithmetic. Indian cuisine is the fastest-growing segment within the broader "ethnic foods" category in US retail, according to industry analysts. The global Indian food market is projected to surpass $80 billion by 2028. And unlike, say, Japanese or Thai cuisine — both of which went mainstream in American kitchens a decade ago — Indian food is still dramatically underrepresented on American grocery shelves relative to the size of its diaspora and the American appetite for it.

## The Diaspora Dividend

For the Indian diaspora, the commercial buzz carries a quieter satisfaction. Every jar of Gymkhana butter chicken sauce on a Whole Foods shelf, every Farzi Café reservation in Bellevue, is a small correction to a long-standing asymmetry: Indian professionals have run some of America's largest corporations for years, but the cuisine they grew up on has been slow to get the same respect.

That is changing — one funding round, one franchise deal, and one grocery aisle at a time."""


# ── Article 2: Natya Darpan 2026 ────────────────────────────────────

article2_body = """On a Friday afternoon in early July, while most of suburban New Jersey was making weekend plans, five theatre companies were warming up backstage at the New Brunswick Performing Arts Center for something quietly remarkable: a festival of short plays performed in four languages, none of them requiring a passport to attend.

The 11th annual Natya Darpan — literally "mirror to society through theatre" — wrapped its 2026 edition on July 11 with five productions in Marathi, Hindi, English, and a multilingual format, drawing audiences from across the northeastern United States. The festival, organised by the Indian Heritage & Cultural Association of New Jersey (IHCA-NJ), has become one of the most distinctive cultural events in the Indian American calendar — a space where diaspora identity is explored not through Bollywood spectacle or classical recital, but through the unfashionable, unforgiving intimacy of live theatre.

## Five Plays, Four Languages, One Stage

This year's lineup tackled subjects that ranged from the algorithmic to the existential. *Human in the Loop*, directed by Atul Athavale, was performed entirely in Marathi and explored the tension between human judgment and machine logic — a theme that resonated with an audience that, statistically speaking, is disproportionately employed in technology. *The Calculus of Guilt*, directed by Dr. Manoj Shahane, used English to examine moral arithmetic. *Daldal* (Hindi, directed by Seema Shahane) and *Seen Under the Weight* (English, directed by Yona Downes) rounded out the dramatic fare, while *Dhaaga* — directed simply by Amita — wove multiple languages into a single narrative thread.

The festival was inaugurated by Consul Upendra Singh Negi from the Consulate General of India in New York. Video messages arrived from New Jersey Governor Mikie Sherrill and Padma Shri awardee Dr. Mohan Agashe, the renowned actor and psychiatrist whose endorsement carries particular weight in the Marathi theatre world. Ambassador Binaya Srikanta Pradhan, Consul General of India in New York, also sent greetings.

## Why Theatre, Why Here

IHCA-NJ was founded in 2013 as a volunteer-driven nonprofit with a simple premise: Indian classical and contemporary performing arts deserve a home in America that is not someone's living room or a rented community hall. Over eleven years, Natya Darpan has staged more than sixty-six short plays featuring over 650 artists, with performers travelling from as far as California to appear on the New Brunswick stage.

Dr. Ashok Chaudhary, the organisation's founder and president, has said that the festival deliberately avoids the competition format. There are no prizes, no rankings, no "best play" announcement. Directors are given complete creative freedom, and the selection committee — comprising accomplished actors, directors, and writers from both the United States and India — prioritises "out-of-the-box concepts and thought-provoking messages" over elaborate staging.

The approach has produced a distinctive curatorial identity. Where many diaspora cultural events lean toward nostalgia — a greatest-hits reel of the homeland — Natya Darpan consistently programmes work that interrogates the present. A Marathi play about pandemic-era unemployment. A Kannada adaptation exploring caste and privilege. An English play about teenage substance abuse. The subjects are global; the languages are specific; the audiences are both.

## The Performing Arts Ecosystem

Natya Darpan is not IHCA-NJ's only production. The organisation also runs Nritya Darpan, a classical and contemporary dance festival that sold out its 2026 edition in April, featuring everything from a Bharatanatyam interpretation of Moby-Dick to a hip-hop-Chhau fusion exploring desert mythology. Together, the two festivals have turned New Brunswick — a mid-sized New Jersey city better known for Rutgers University and a Johnson & Johnson campus — into an unlikely but genuine hub for Indian performing arts in America.

## A Mirror Worth Holding Up

For a community that is often reduced to its economic statistics — highest median income, most advanced degrees, most CEOs per capita — Natya Darpan offers a different kind of representation. Not the diaspora as model minority, but the diaspora as audience, as artist, as someone willing to sit in the dark for six hours on a Friday and watch five plays in four languages about what it means to be human.

That is a contribution worth measuring, even if no census captures it."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Eight Michelin Stars, One Grocery Aisle: How Indian Cuisine Conquered America's Supermarket Shelves",
        "subheadline": "Gymkhana Fine Foods launches nationwide in Whole Foods with $8.5 million in backing, as a wave of Indian restaurant brands — from Farzi Café to Dishoom — bet that American home cooks are finally ready.",
        "slug": make_slug("gymkhana-whole-foods-indian-cuisine-american-grocery"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian diaspora entrepreneurs and chefs are driving the mainstreaming of Indian cuisine in American retail and dining — a cultural and commercial milestone that reflects the community's growing economic influence and culinary confidence.",
        "tags": ["nri", "diaspora", "food", "business", "indian-cuisine", "retail"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com/operations/uk-based-indian-concept-gymkhana-brings-its-cpg-line-us"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/farzi-cafe-opens-first-outlet-in-us/"},
            {"name": "Restaurant Business Online", "url": "https://www.restaurantbusinessonline.com/emerging-brands/3-restaurant-concepts-set-invade-us"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9792458/pexels-photo-9792458.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Vibrant Indian dishes featuring tandoori chicken and aromatic curries, representative of the bold flavours now reaching American grocery shelves",
        "image_attribution": "Pexels",
        "body": article1_body.strip()
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Plays, Four Languages, Six Hours, One Stage: Inside New Jersey's Quietly Radical Indian Theatre Festival",
        "subheadline": "Natya Darpan's 11th edition in New Brunswick featured Marathi, Hindi, English, and multilingual drama — a diaspora cultural event that refuses to be a nostalgia act.",
        "slug": make_slug("natya-darpan-2026-new-jersey-multilingual-theater"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The festival represents a maturing Indian American cultural ecosystem that goes beyond Bollywood and classical dance to engage with contemporary issues through multilingual theatre — a form of diaspora identity-building that receives little mainstream attention.",
        "tags": ["nri", "diaspora", "culture", "theater", "new-jersey", "performing-arts"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/natya-darpan-2026-celebrates-11-years/"},
            {"name": "New Brunswick Performing Arts Center", "url": "https://secure.nbpac.org/overview/4992"},
            {"name": "IHCA-NJ", "url": "https://www.ihca-nj.com/natya-darpan-nj"}
        ]),
        "score_total": 65,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12165875/pexels-photo-12165875.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Actors performing a theatrical play on stage, representing the multilingual drama celebrated at Natya Darpan",
        "image_attribution": "Pexels",
        "body": article2_body.strip()
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
