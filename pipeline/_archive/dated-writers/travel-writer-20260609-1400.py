#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-09 14:00 UTC run"""

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
# ARTICLE 1: FIFA World Cup 2026 NRI Guide
# ─────────────────────────────────────────────
article1_body = """The FIFA World Cup kicks off on Thursday in a tournament spread across 16 cities in the United States, Canada, and Mexico. India isn't on the pitch — the men's team hasn't qualified since their one and only appearance in 1950, and that's unlikely to change anytime soon. But for the roughly 4.4 million Indian Americans living within driving distance of at least one host venue, this is a once-in-a-generation opportunity to experience the world's biggest sporting event without booking a single international flight.

## NRIs Have a Structural Advantage

While international fans wrestle with US visa uncertainties, record-high ticket prices, and hotel rates that have pushed some toward Canada and Mexico instead, NRIs already in the country face none of those barriers. No visa interview. No ESTA. No anxious wait at immigration. Just buy a ticket and drive.

That matters more this year than it normally would. According to the Wall Street Journal, hotel bookings in US host cities are trailing expectations, with Vancouver and Guadalajara leading at 48% occupancy. San Francisco — home to a massive Indian American population — is the only US city cracking 40%, at 44%. Several other American host cities are underperforming. The reason? A combination of record ticket prices, travel costs, and what the WSJ delicately calls "the U.S. political climate that many foreigners perceive as unwelcoming."

For NRIs, that soft demand could translate into deals. Last-minute hotel rooms in host cities may be more available than expected, and resale ticket prices for group-stage matches are already softening on secondary markets.

## Where to Watch

The 16 host cities span the continent, but several have especially large Indian American communities. MetLife Stadium in New Jersey — venue for the final on July 19 — sits in the heart of the tri-state area's massive desi population. The Bay Area has matches at Levi's Stadium in Santa Clara. Dallas, Houston, Atlanta, and Seattle all host games and all have significant Indian populations.

If you're in the Bay Area, the group stage runs from June 11 through July 2, with knockout rounds following. India's cricket-first culture means most NRIs haven't traditionally followed football closely, but the World Cup is different — it's a cultural event that transcends sport, and the stadium experience alone is worth the trip.

## The Visa Question for Friends and Family

For family members planning to fly in from India specifically for the World Cup, the situation is more complex. Indian passport holders need a B1/B2 tourist visa — there's no visa waiver for Indians. The US State Department has launched a FIFA PASS (Priority Appointment Scheduling System) that gives confirmed ticket holders priority consular appointments, but that doesn't guarantee approval.

Current wait times for US visa interviews vary wildly by consulate — Mumbai and Delhi can run several weeks to months. If relatives haven't already started the process, group-stage matches are likely out of reach, though knockout-round and semifinal timing might still work.

A concierge service owner in Ivory Coast told the Washington Post that clients are asking him, "Are you sure I can get in?" His answer: "I'm not sure because I'm not working at the airport." That uncertainty is real, and it's keeping some international fans away entirely. The financial stakes are steep: between flights ($800–$1,800), hotels ($614–$2,052 for two nights near a stadium), and tickets ($250–$9,000 depending on the match), a denied entry could mean thousands lost.

## The Smart NRI Move

For Indian Americans already stateside, the calculus is simple. Group-stage tickets for less prominent matchups are the most accessible entry point — think Costa Rica vs. New Zealand, not Argentina vs. Brazil. Pair that with a road trip to a host city you haven't visited, and it's a sporting weekend that doubles as a family trip.

The World Cup hasn't been in the US since 1994. The next time it comes back is anyone's guess. If you're already here, the hardest part of attending is already done."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Cup Starts Thursday — and NRIs in America Have the Easiest Ticket in the Building",
    "subheadline": "While international fans face visa fears and record hotel prices, Indian Americans already in the US can simply buy a ticket and drive. Here's how to make the most of a once-in-a-generation sporting event on your doorstep.",
    "slug": make_slug("fifa-world-cup-2026-nri-america-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "4.4 million Indian Americans live within driving distance of at least one of the 16 host cities. While international fans deal with visa uncertainty, NRIs face zero immigration barriers. Soft hotel demand in US cities could mean last-minute deals.",
    "tags": ["travel", "fifa", "world-cup", "nri", "sports", "events"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/real-estate/america-is-already-losing-the-world-cup-for-hotel-bookings-c8c79f75"},
        {"name": "Travel And Tour World", "url": "https://travelandtourworld.com/news/article/mexico-canada-and-united-states-see-diverging-fifa-world-cup-2026-tourism-trends/"},
        {"name": "Fragomen", "url": "https://www.fragomen.com/insights/us-visitor-visa-rules-for-the-2026-fifa-world-cup.html"},
        {"name": "StadiumDB", "url": "https://stadiumdb.com/tournaments/world-cup-2026/fan-guide"},
        {"name": "The Travel", "url": "https://www.thetravel.com/fifa-world-cup-fans-hesitant-travel-usa/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Metlife_stadium_%28Aerial_view%29.jpg",
    "image_caption": "Aerial view of MetLife Stadium in New Jersey, venue for the 2026 FIFA World Cup final",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: Hotel Chains Bet on India's Temple Towns
# ─────────────────────────────────────────────
article2_body = """Marriott International plans to add 180 properties in India over the next few years, making it the company's fastest-growing market in Asia-Pacific after China. Hilton has 94 hotels operating or in the pipeline. And a boutique chain called Tamara just launched a dedicated pilgrimage brand — Raé by Tamara — with plans for 25 properties across India's temple circuit by 2030.

The common thread: all three are betting that India's domestic travel boom, particularly the explosive growth in religious tourism, isn't a post-pandemic blip. It's a structural shift, and it's being turbocharged by something unusual — pilgrims with money.

## The Numbers Behind the Prayer

Five-star hotel bookings in India more than doubled in April compared to the previous year, according to Cleartrip data shared with Bloomberg News. Family hotel bookings surged 125%. A Westin wellness retreat in the Himalayan foothills near Rishikesh — about as spiritual as a luxury chain gets — runs nearly $1,900 per night for a garden suite with a private plunge pool.

Roughly 11% of Marriott's approximately 220 hotels in India now cater specifically to temple visitors. For Hilton, that figure is about 15%. And these aren't dharamshalas with better plumbing. They're full-service properties with spas, multiple restaurants, and event spaces designed for the social occasions that increasingly accompany pilgrimages.

"Now people are staying two to four nights because they're doing social events there, they're doing a little birthday party and sightseeing," Rajeev Menon, Marriott's president for Asia Pacific excluding China, told Bloomberg. The pilgrimage weekend has become the pilgrimage mini-vacation.

Hilton's Clarence Tan put it more bluntly: "The religious tourism alone fills the season, and the rates alone are astronomical."

## Where the Hotels Are Going

Tamara's new Raé brand tells the story most clearly. Its first properties open this summer in Guruvayur, Kerala (36 rooms, July) and Kumbakonam, Tamil Nadu (45 rooms, August) — both converted from existing Tamara properties. An 80-room new build in Velankanni, home to one of India's most important Christian pilgrimage sites, follows later this fiscal year. After that: Tirupati, Palani, and Tiruvannamalai, three of South India's most visited spiritual destinations, expected in FY27.

Marriott and CG Hospitality Global just signed a deal to bring a JW Marriott to Siliguri — the gateway city to Northeast India and the starting point for trips to Darjeeling, Gangtok, and the Himalayan foothills. A Ritz-Carlton is headed to Kathmandu. These aren't random pins on a map. They're calculated bets on the routes that affluent Indian travelers — including returning NRIs — actually take.

## The NRI Angle

For the diaspora, this changes the calculus of the India trip. The traditional NRI visit — fly into Delhi or Mumbai, spend a week at relatives' homes, squeeze in one temple visit, fly back — is giving way to something more intentional. When there's a JW Marriott in Siliguri and a luxury option in Tirupati, the temple visit becomes the trip, not an afterthought bolted onto family obligations.

The hotel chains understand this. International brands that might normally insist on alcohol sales are making exceptions for properties in holy cities, where liquor permits are often restricted. The demand, executives say, more than offsets the revenue they forgo at the bar.

India's domestic travel market was worth $234 billion last year, according to the World Travel & Tourism Council. Modi's persistent "explore India" messaging may be part of it, but so is something simpler: a growing Indian middle class that can finally afford to travel the way they want to, and an NRI community that's ready to reconnect with their roots in five-star comfort.

The chains are betting billions that both groups will keep coming. Based on the booking data, they're probably right."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Global Hotel Chains Are Betting Billions on India's Temple Towns — and the Returns Are Already Biblical",
    "subheadline": "Marriott is adding 180 properties. Hilton has 94 in the pipeline. A new luxury pilgrimage brand just launched. The bet: India's religious tourism boom is structural, not seasonal — and NRIs are the premium upgrade.",
    "slug": make_slug("marriott-hilton-india-pilgrimage-hotel-boom-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI visits to India are shifting from obligation-driven family stays to intentional luxury pilgrimages. JW Marriotts in temple gateway cities and five-star options at Tirupati and Varanasi mean the temple visit can now be the trip, not an afterthought. International chains are forgoing alcohol revenue in holy cities because pilgrimage demand alone is astronomical.",
    "tags": ["travel", "hotels", "india", "pilgrimage", "marriott", "hilton", "nri", "luxury"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Bloomberg / Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/hotel-giants-bet-indias-local-travel-boom-can-defy-slowdown/article69668721.ece"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/stay/rae-by-tamara-plans-25-properties-across-indias-pilgrimage-circuit-by-2030"},
        {"name": "Tripura Star News", "url": "https://tripurastarnews.com/marriott-international-and-cg-hospitality-global-sign-multi-unit-agreement/"},
        {"name": "Cleartrip / Bloomberg", "url": "https://www.thehindubusinessline.com/economy/hotel-giants-bet-indias-local-travel-boom-can-defy-slowdown/article69668721.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Tirumala_090615.jpg/3840px-Tirumala_090615.jpg",
    "image_caption": "Tirumala Venkateswara Temple, one of India's most visited pilgrimage sites now attracting luxury hotel investment",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}

# ─────────────────────────────────────────────
# ARTICLE 3: India's Mountain Treks Go Mainstream
# ─────────────────────────────────────────────
article3_body = """Accommodation searches for Leh have surged 143% year-over-year. Kasol is up 127%. McLeod Ganj, the Himalayan seat of the Dalai Lama and the starting point for the Triund trek, is seeing similar spikes. According to data from travel platform Agoda, India's mountain trekking destinations are pulling travelers away from crowded beaches and city breaks at a pace that's hard to ignore.

The numbers are being driven overwhelmingly by metro-city residents. Delhi searches for Leh are up 140%. Mumbai is up 158%. Hyderabad is showing a 106% rise. The pattern is consistent: urban Indians with disposable income are choosing altitude over attitude, trading resort pools for ridge lines.

## Why the Surge Matters to NRIs

For Indian Americans planning summer trips to India, this data carries a practical signal. The destinations seeing the sharpest growth — Kasol in Himachal Pradesh's Parvati Valley, McLeod Ganj near Dharamsala, Leh in Ladakh — are exactly the kinds of places that make a monsoon-season India trip worth the flight.

June through September is traditionally the cheapest window for US-to-India airfares. It's also when most of peninsular India is soaked in monsoon rain, making beach destinations and plains cities unappealing. But the trans-Himalayan regions — particularly Ladakh and parts of Himachal — sit in a rain shadow. Leh gets almost no monsoon rainfall. Spiti Valley is bone-dry. Even Kasol and McLeod Ganj, while wetter than Leh, offer dramatically better conditions than Kerala or Goa in July.

This is the window that savvy NRI travelers have been exploiting for years. What's changed is that the infrastructure has caught up.

## The Infrastructure Catch-Up

Kasol, once a backpacker-only destination known mainly for its Israeli cafes and proximity to Kheerganga hot springs, now has boutique properties and organized trek operators catering to a more affluent demographic. The Parvati Valley's appeal has broadened from gap-year wanderers to weekend professionals willing to pay for a guided Sar Pass or Pin Parvati trek with gear provided.

McLeod Ganj has seen a similar upgrade. Dharamsala's airport now handles more flights, and the town's hotel stock has expanded beyond the prayer-flag-draped guesthouses that defined it for decades. The Triund trek — a relatively accessible overnight climb with panoramic Dhauladhar views — has become one of India's most popular short treks, and the trail now has designated camping spots and better-marked routes.

Leh, meanwhile, has benefited from improved road connectivity and increased flight frequency. The Manali-Leh highway and the newer Atal Tunnel have cut travel times, making overland access more practical for visitors who want to acclimatize gradually rather than fly directly into high altitude.

## The Trek Portfolio

For NRIs who've done the Golden Triangle and ticked off the Taj Mahal, India's mountain destinations offer something genuinely different:

**Beginner-friendly:** Triund (McLeod Ganj, 1-day), Kheerganga (Kasol, 2-day), Chandrashila (Uttarakhand, 2-day)

**Intermediate:** Hampta Pass (Manali to Spiti, 4-5 days), Markha Valley (Ladakh, 6-7 days), Rupin Pass (Shimla to Uttarakhand, 7 days)

**Advanced:** Pin Parvati Pass (Kullu to Spiti, 10 days), Stok Kangri (Ladakh, 6-8 days, peaks at 20,182 feet)

Organized operators like Indiahikes, Trek The Himalayas, and Bikat Adventures now offer fixed-departure treks with all logistics handled — a format that works well for NRIs with limited vacation days who want the mountain experience without the planning overhead.

## Booking Window

The optimal booking window for monsoon-season Himalayan treks is now through mid-July. Leh's peak season runs June through September, with July and August offering the warmest temperatures and clearest skies. Kasol and McLeod Ganj are best in June and September, when rainfall is lighter. Flight prices from major US cities to Delhi typically bottom out in June — the sweet spot where monsoon discounts overlap with the Himalayan trekking season.

Domestic India searches suggest the secret is already out. For NRIs who've been putting off a "real" India trip that goes beyond family weddings and temple visits, the mountains are calling with better infrastructure, better access, and — for now — better prices than they'll likely see again."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Forget Goa — India's Himalayan Treks Are the Hottest Travel Trend of 2026, and NRIs Should Book Now",
    "subheadline": "Leh searches are up 143%, Kasol 127%, McLeod Ganj surging. India's monsoon season is the cheapest time to fly from the US — and the Himalayas are the one place it barely rains.",
    "slug": make_slug("himalayan-treks-monsoon-season-nri-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "June-September is the cheapest window for US-India flights and coincides with the Himalayan trekking season. Leh, Kasol, and McLeod Ganj sit in the monsoon rain shadow. Organized trek operators now offer fixed-departure packages ideal for NRIs with limited vacation days.",
    "tags": ["travel", "trekking", "himalayas", "leh", "kasol", "monsoon", "nri", "india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World / Agoda", "url": "https://travelandtourworld.com/news/article/indian-travellers-abandon-crowded-cities-and-beaches-to-discover-leh-kasol-and-mcleod-ganj/"},
        {"name": "Travel And Tour World / Agoda", "url": "https://travelandtourworld.com/news/article/india-family-travel-soars-as-puri-wayanad-and-goa-dominate-summer-holiday-searches-2026/"},
        {"name": "Wikipedia - Kasol", "url": "https://en.wikipedia.org/wiki/Kasol"},
        {"name": "Wikipedia - Parvati Valley", "url": "https://en.wikipedia.org/wiki/Parvati_Valley"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/14114690/pexels-photo-14114690.jpeg",
    "image_caption": "Trekkers on a foggy mountain trail in Tungnath, Uttarakhand, India",
    "image_attribution": "Pexels",
    "body": article3_body
}

# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
