#!/usr/bin/env python3
"""Travel writer — 2026-06-30 07:00 PT run. Three articles."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# ─────────────────────────────────────────────
# ARTICLE 1: India's Wealthy Travellers Reshaping Luxury Hospitality
# ─────────────────────────────────────────────

art1_body = """When a Mumbai business family recently booked all 14 villas at Soneva Secret in the Maldives — where nightly rates run from $3,300 to north of $15,000 — the resort's staff didn't blink. They chartered a seaplane timed to the family's arrival, arranged personal butlers for every villa, hired private chefs, and cleared the entire property for an exclusive multi-generational holiday. Grandparents, parents, children and great-grandchildren had the island to themselves.

That kind of booking, luxury hospitality executives say, is no longer exceptional. It is becoming a pattern.

## The Numbers Behind the Shift

India's outbound luxury travel market has grown sharply in the past two years. Across the Maldives, Sri Lanka, Thailand and Southern Europe, affluent Indian families are travelling in larger groups, spending more per trip, and demanding a level of personalisation that is quietly reshaping how the world's most expensive hotels design their products.

"I don't think there's any business in luxury that doesn't have India in its priority list," Joanna Flint, chief executive of one Maldives-based ultra-luxury operator, told Mint.

The trend is not confined to industrialist families flying out of Mumbai or Delhi. Indian Americans — particularly those in finance, tech and medicine on the East and West Coasts — are driving a parallel wave. Multi-generational travel, where NRI couples fly their parents and in-laws to a third-country resort, has become a staple of the Indian diaspora holiday calendar. The Maldives, Bali and increasingly Southern Europe are the favoured staging grounds.

## What's Different About the Indian Luxury Traveller

Several things set Indian luxury demand apart from established high-net-worth markets in Europe or East Asia. First is the group size. Where a European couple might book a two-bedroom overwater villa, an Indian family routinely needs five to eight rooms — and often prefers a full buyout. Second is the emphasis on food. Requests for private chefs who can prepare both Jain-friendly thalis and continental fare are now standard at properties from Soneva to Aman.

Third, and most commercially significant, is the willingness to spend on experiences rather than branded goods. Bespoke beach dinners, private yacht excursions, guided snorkelling trips, daily spa treatments and on-call wellness practitioners are being bundled into what resorts now call "immersive family programmes" — packages that can run into hundreds of thousands of dollars for a single week.

## Why NRIs Are at the Centre

For Indian Americans, the calculus is straightforward. A family reunion at a Maldives resort eliminates the logistical headache of hosting across time zones and dietary preferences in someone's suburban home. It also sidesteps the increasingly painful process of flying elderly parents into the United States on visitor visas — a wait that now stretches past ten months in Mumbai.

The economics work, too. A seven-night buyout at a mid-tier Maldives resort can cost less than renting a large vacation home in the Hamptons or Napa for the same period, with the added benefit of all-inclusive service and direct flights from both India and the US Gulf hubs.

## Hotels Are Redesigning for India

The commercial impact is tangible. Several luxury operators have begun redesigning villas to accommodate larger family groups, adding interconnected rooms, dedicated children's areas and multi-cuisine kitchen facilities. Soneva, Aman and One&Only have all expanded their Indian-market sales teams. Even European luxury chains like Belmond are reportedly studying the Indian family-travel segment.

India accounted for the largest share of tourist arrivals in the Maldives for most of 2025 and continues to dominate in 2026, supported by high-frequency air connectivity from Mumbai, Delhi, Bengaluru, Chennai and Kochi.

For luxury hospitality, the message is clear: India is no longer an emerging market. It is the market that is setting the terms."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Wealthy Families Are Buying Out Entire Maldives Resorts — and Luxury Hospitality Is Redesigning Itself Around Them",
    "subheadline": "From Soneva Secret to Aman, multi-generational Indian family buyouts are no longer exceptional — they are reshaping how the world's most expensive hotels build and sell their products.",
    "slug": make_slug("india-wealthy-families-luxury-maldives-resort-buyout-nri"),
    "category": "travel",
    "vertical": "luxury-travel",
    "diaspora_angle": "NRI families are driving a parallel luxury travel wave — multi-generational resort buyouts in the Maldives and Bali eliminate US visa hassles for elderly parents and offer all-inclusive family reunions at competitive costs.",
    "tags": ["travel", "luxury", "maldives", "nri", "hospitality", "resorts"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/industry/india-luxury-travel-boom-ultra-rich-reshaping-global-hotels-11782619104067.html"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/maldives-india-singapore-malaysia-srilankan-airlines-may-2026/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/9394274/pexels-photo-9394274.jpeg",
    "image_caption": "Overwater bungalows in the Maldives, the destination of choice for India's luxury family travellers",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ─────────────────────────────────────────────
# ARTICLE 2: Air India's Japan Push — Mumbai-Tokyo Haneda
# ─────────────────────────────────────────────

art2_body = """Two weeks into its new Mumbai–Tokyo Haneda nonstop, Air India has quietly completed one of the more significant route launches on its post-privatisation map. Flight AI 356 departs Mumbai at 4:50 pm every Monday, Wednesday, Friday and Sunday, landing at Haneda — Tokyo's city-centre airport — at 4:55 am the following morning. The return, AI 355, leaves Haneda at 8:50 am and reaches Mumbai by 2:20 pm.

The service, operated on Boeing 787-8 Dreamliners, complements Air India's existing daily Delhi–Haneda flights. Together, they give India 11 weekly nonstop frequencies to Tokyo — a capacity that would have seemed improbable even 18 months ago.

## Why Haneda Matters

The choice of Haneda over Narita is strategic. Haneda sits roughly 20 minutes from central Tokyo by monorail, compared with the 60- to 90-minute schlep from Narita. For business travellers landing before dawn on a red-eye, the difference between stepping into a Shinagawa hotel by 5:30 am and arriving by 7:00 am is the difference between a full working day and a lost morning.

For leisure passengers — particularly the growing cohort of Indian millennials and Gen-Z travellers drawn to Japan's food, culture and anime tourism — Haneda's proximity to Shibuya, Shinjuku and Ginza means the holiday starts immediately.

## The ANA Codeshare Unlocks Six More Cities

What makes the Mumbai route especially useful is Air India's codeshare agreement with All Nippon Airways (ANA), a fellow Star Alliance member. Passengers arriving at Haneda can connect seamlessly to six domestic Japanese cities: Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka and Sapporo. For NRIs planning a deeper Japan itinerary — cherry blossom season in Kyoto, ski trips to Hokkaido, Hiroshima's peace memorials — the codeshare eliminates the need to book separate domestic tickets.

Return fares from Mumbai start at ₹63,075 in economy and ₹2.1 lakh in business class. From the Tokyo end, economy returns begin at ¥108,704 (roughly $730 at current exchange rates).

## June Was Air India's Best Month

The Japan expansion comes against the backdrop of Air India's strongest operational performance since the Tata Group took over. In June 2026, the airline achieved 86 per cent on-time performance across its entire network, while domestic punctuality hit a record 90 per cent.

CEO Campbell Wilson attributed the improvement to investments in fleet modernisation, maintenance planning and operational coordination — though he noted that a temporarily shortened schedule and favourable weather helped. For NRIs who have long treated Air India as a carrier of last resort, the numbers suggest a genuine operational turnaround.

## What's Coming Next

Air India is not done expanding. In the coming weeks, it will launch:

- **Navi Mumbai–Abu Dhabi**: the first international passenger flight from Navi Mumbai International Airport, operated by Air India Express
- **Guwahati–Dubai and Guwahati–Abu Dhabi**: the first direct Gulf links from Northeast India
- **Pune–Amritsar**: a new domestic connection

The Guwahati routes are particularly significant. Northeast India has historically depended on connections through Delhi or Kolkata for international travel. Direct services to the UAE will cut travel time for the region's substantial VFR (visiting friends and relatives) traffic to the Gulf.

## The NRI Angle

For Indian Americans, Air India's Japan push addresses a gap that Emirates, Singapore Airlines and ANA themselves had long filled. A nonstop from Mumbai to central Tokyo — bookable on Star Alliance miles, with familiar food and Indian-language entertainment — removes the friction from what has become one of the fastest-growing outbound travel corridors for Indians.

The caveat: Air India recently suspended several NRI-heavy US routes, including Chicago, Newark and San Francisco services, through August. The Japan capacity suggests the airline is reallocating widebody aircraft to routes where it can compete more effectively — a strategy that trades short-term inconvenience on the US corridor for long-term network strength in Asia."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's Mumbai–Tokyo Haneda Nonstop Is Two Weeks Old — and Japan Is Now the Airline's Biggest Asia Bet",
    "subheadline": "Eleven weekly nonstops to Tokyo, a codeshare unlocking six Japanese cities, and the airline's best-ever operational month — Air India's Japan push is a signal of where the carrier sees its future.",
    "slug": make_slug("air-india-mumbai-tokyo-haneda-nonstop-japan-nri"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "NRIs can book Mumbai-Tokyo Haneda on Star Alliance miles with ANA connections to Osaka, Sapporo and four more Japanese cities — filling a gap long served only by Gulf and East Asian carriers.",
    "tags": ["travel", "airlines", "air-india", "japan", "tokyo", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-international-flight-growth-middle-east-airspace-japan/"},
        {"name": "Air India", "url": "https://www.airindia.com/in/en/fly-non-stop-mumbai-tokyo.html"},
        {"name": "Travel Span", "url": "https://www.travelspan.in/air-india-launches-non-stop-mumbai-tokyo-haneda-flights/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/15275312/pexels-photo-15275312.jpeg",
    "image_caption": "Tokyo skyline with Mount Fuji in the background — now a direct nonstop from Mumbai on Air India",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─────────────────────────────────────────────
# ARTICLE 3: Hilton, Leela and the Luxury Hotel Arms Race
# ─────────────────────────────────────────────

art3_body = """Hilton is opening six hotels in India this quarter alone — and the marquee property tells you exactly where the company thinks the money is. The Den Bengaluru, Hilton's first LXR Hotels & Resorts property in India, will debut as a 226-room luxury hotel aimed at the tech corridor crowd: business travellers attending conferences at the Embassy Tech Village who extend their stays for leisure, and the growing ranks of NRIs visiting family in India's startup capital.

The property offers three dining outlets — Layla (Indian-Mediterranean), The Creek (24/7 global fare), and The Nest (a cocktail lounge with pool tables) — plus nearly 9,000 square feet of meeting space, including a 700-capacity hall called The Forest.

It is also a statement of intent. Hilton plans to grow its India portfolio tenfold over the next decade.

## The Broader Land Grab

Hilton is not alone. Across India's second and third cities, a luxury hotel arms race is under way that will reshape the accommodation landscape for visiting NRIs within the next two to three years.

**The Leela Jaisalmer** is the most atmospheric of the newcomers. Spread across 30 acres of Thar Desert landscape near Jaisalmer Fort — a UNESCO World Heritage Site — the 80-room resort will feature tented villas, an expansive spa, a man-made lake, and a pillarless ballroom designed for destination weddings. The Leela already operates palaces in Udaipur and Jaipur; adding Jaisalmer creates a complete luxury circuit across Rajasthan, the state that draws the most heritage-tourism traffic from the Indian diaspora.

**Waldorf Astoria Jaipur**, Hilton's ultra-luxury flagship, is expected by 2027. The Pink City will also get a Conrad Hotels property, giving it three distinct Hilton luxury brands within a few years. For NRI families who have long defaulted to the Oberoi or Taj for Rajasthan weddings, the competition will bring both better rates and more options.

## Bengaluru Gets Five Hotels in One Quarter

The scale of Hilton's India push is most visible in Bengaluru, which is receiving five Hilton properties in Q3 2026 alone:

- **The Den, LXR Hotels & Resorts** — luxury (226 rooms)
- **Slohh by Roach Bengaluru, Curio Collection** — Hilton's first lifestyle hotel in India
- **Hilton Garden Inn Embassy Tech Village** — 211 rooms in the IT corridor
- **Spark by Hilton Bengaluru Marathahalli** — the Asia-Pacific debut of Hilton's premium-economy brand
- **Plus Spark by Hilton Goa Calangute** — 88 rooms near Calangute Beach

Spark by Hilton is Hilton's newest brand: a premium-economy concept pitched between budget and midscale. The company plans 150 Spark properties across India through a partnership with Olive by Embassy. Hampton by Hilton will debut separately in Gujarat, Rajasthan, Punjab and Bihar.

## Why This Matters to NRIs

For the 4.5 million Indian Americans who visit India regularly, the hotel landscape has long been bifurcated: five-star palaces at Taj and Oberoi prices, or unpredictable mid-range options. The entry of Hilton's full brand stack — from Spark (₹3,000–5,000/night) to LXR (₹15,000+) — fills the middle ground with properties that NRIs can book confidently using Hilton Honors points earned on their American Express or Chase credit cards.

The Leela's Rajasthan circuit, meanwhile, solves a specific NRI problem: the destination wedding. Jaisalmer's desert setting, combined with The Leela's event infrastructure (that pillarless ballroom seats hundreds), makes it a credible alternative to the overbooked Udaipur palace circuit that has priced out all but the wealthiest families.

## The India Hospitality Market

None of this is happening in a vacuum. India's hospitality market was valued at $29.3 billion in 2024 and is growing faster than any comparable market globally. Domestic air passenger traffic is rising sharply, international arrivals are recovering post-pandemic, and a government push to develop tourism infrastructure — from new airports in Noida and Navi Mumbai to the Vande Bharat train network — is opening up destinations that were previously inaccessible.

For global hotel chains, India is no longer a secondary market. It is the growth engine — and the race to plant flags in its second cities is well under way."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Hilton Is Opening Six Hotels in India This Quarter — and the Luxury Arms Race Is Just Starting",
    "subheadline": "From Hilton's first LXR in Bengaluru to The Leela's desert resort near Jaisalmer Fort, a wave of luxury hotel openings is about to reshape where NRIs stay when they visit India.",
    "slug": make_slug("hilton-leela-india-luxury-hotel-boom-bengaluru-jaisalmer-nri"),
    "category": "travel",
    "vertical": "hospitality",
    "diaspora_angle": "NRIs can now book India stays using Hilton Honors points from US credit cards, and The Leela's Rajasthan circuit offers a new destination-wedding alternative to overbooked Udaipur.",
    "tags": ["travel", "hotels", "hilton", "leela", "bengaluru", "jaisalmer", "luxury", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Asian Hospitality", "url": "https://www.asianhospitality.com/hilton-plans-9-hotels-in-us-and-india-in-q3/"},
        {"name": "Meetings Today", "url": "https://www.meetingstoday.com/articles/new-global-hotel-openings-india-portugal-shanghai/"},
        {"name": "Hotels Magazine", "url": "https://www.hotelsmag.com/news/the-leela-jaisalmer-to-open-in-2026/"}
    ]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Jaisalmer%2C_India%2C_Jaisalmer_Fort_2.jpg/1280px-Jaisalmer%2C_India%2C_Jaisalmer_Fort_2.jpg",
    "image_caption": "Jaisalmer Fort, a UNESCO World Heritage Site, near the site of The Leela's upcoming luxury desert resort",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}


# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
