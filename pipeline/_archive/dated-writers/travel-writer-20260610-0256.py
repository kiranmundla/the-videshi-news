#!/usr/bin/env python3
"""Travel writer — 2026-06-10 02:56 PDT run. Three articles."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ──────────────────────────────────────────
# Article 1: World Cup Travel Logistics
# ──────────────────────────────────────────
art1_body = """The FIFA World Cup kicks off this Thursday across the United States, Mexico, and Canada — the first time three countries have co-hosted the tournament. For the estimated 4.5 million Indian Americans scattered across US metro areas, many of which double as host cities, the logistics of actually getting to a match have turned out to be a bigger story than the group-stage draw.

## The Hotel Paradox

Here is the headline that no one expected: hotel bookings in American host cities are *lagging behind* Mexico and Canada. According to CoStar data, Vancouver and Guadalajara lead the pack at 48 percent occupancy for match weeks. San Francisco is the only US city above 40 percent, at 44. New York and New Jersey — home to MetLife Stadium, which will host the final — sit at a paltry 39 percent.

The culprit is a toxic cocktail of eye-watering hotel rates (averaging $300 a night in Miami, Boston, and Kansas City), record-high ticket prices (some final-match resale tickets are clearing $20,000), and transit costs that have shocked even seasoned American sports fans.

In Kansas City, which will host six matches, the situation borders on absurd. FIFA had reserved up to 5,000 rooms per night for officials and partners — tens of thousands of room-nights across the tournament. Then it cancelled 75 percent of them. Visit KC confirmed the cancellations were "abnormally large," leaving the Crowne Plaza and other downtown hotels scrambling to fill rooms with weeks to go.

Meanwhile, hotels in Monterrey saw a 40-fold increase in reservations, and Mexico City bookings rose over 150 percent. Short-term rentals across Mexico are moving at roughly $100 a night — one-third of what US cities are charging.

## Transit Sticker Shock

Getting to the stadiums without a car is possible, but it will cost you. Round-trip trains from Manhattan to MetLife Stadium in East Rutherford, New Jersey, were initially priced at $150 — more than ten times the standard $12.90 game-day rate for NFL matches. After public backlash, officials dropped the price to $98. In Boston, round-trip service from downtown to Gillette Stadium runs $80.

Los Angeles, at least, offers a bargain. The LA Metro will run direct buses to SoFi Stadium from 15 locations across the county — Union Station, LAX, North Hollywood, Anaheim, Long Beach, and more — all for $1.75 each way. Metro also partnered with Uber for $10-discount rides through temporary Micro zones in Hollywood and East LA on match days.

For NRI families in the Bay Area planning a trek to Levi's Stadium in Santa Clara, the story is simpler: BART to Milpitas, then the free VTA shuttle. But for those flying to East Coast matches, the calculus shifts. A family of four looking at $400 in transit, $1,200 in hotel costs for two nights, and $600-plus in tickets could easily spend $2,200 before food and merchandise. That is an India trip.

## The Mexico Play

Here is where it gets interesting for NRI fans with US visas: Mexico offers visa-free entry for Indian passport holders with valid US visas. With hotel rates a fraction of American prices, direct flights from most US hubs to Mexico City and Guadalajara, and a football-mad atmosphere that puts American stadiums to shame, watching group-stage matches south of the border is looking increasingly rational.

Dallas is a different story — hotel bookings there surged 1,400 percent during group-stage dates, driven largely by Japanese and South Korean travellers. But even in Dallas, the host committee has set up robust shuttle systems from downtown Fort Worth and key transit hubs, including a route to the local Buc-ee's.

## What NRIs Should Actually Do

For those committed to attending, the practical playbook is straightforward: book transit early, use public transportation where possible, consider mid-range hotels 20 to 30 miles from the stadiums and Uber in, and monitor FIFA's official fan zones — free entry, big screens, and the actual atmosphere without the ticket price. LA's fan festival at the Coliseum and similar setups in each host city are built for this.

And if you are flexible on which matches you attend, the knockout-round bookings are still soft. Once matchups are set and fans know where their team is playing, hotels expect a surge. Getting ahead of that wave — particularly in cities like Atlanta and Philadelphia, where public-transit prices remain normal — could save hundreds.

The World Cup is here. The football will be spectacular. The travel experience? Plan early, or plan to pay."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Cup Starts Thursday — and Getting There May Cost More Than Your Ticket",
    "subheadline": "FIFA cancelled 75 percent of its Kansas City hotel blocks, Manhattan-to-stadium trains cost $98, and US bookings lag behind Mexico. Here is the NRI fan's survival guide.",
    "slug": make_slug("world-cup-2026-nri-hotels-transit-survival-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Millions of Indian Americans live in World Cup host cities. With US hotels at $300/night and transit at 10x NFL rates, NRI fans need a practical game plan — including the Mexico visa-free option for Indian passport holders with US visas.",
    "tags": ["travel", "world cup", "hotels", "transit", "nri", "fifa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/soccer/worldcup/2026/06/09/how-to-get-to-sofi-stadium-world-cup-public-transit/84070281007/"},
        {"name": "Front Office Sports", "url": "https://frontofficesports.com/world-cup-fans-face-significant-sticker-shock-for-hotels/"},
        {"name": "The Sun", "url": "https://www.the-sun.com/sport/16476242/fifa-kansas-city-world-cup-hotel-rooms-lack-interest/"},
        {"name": "LinkedIn / CoStar Data", "url": "https://www.linkedin.com/posts/activity-7206962984783872000"},
        {"name": "MyNewsLA", "url": "https://mynewsla.com/transportation/2026/06/09/world-cup-fans-offered-expanded-transit-options/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SoFi_Stadium_2023.jpg/3840px-SoFi_Stadium_2023.jpg",
    "image_caption": "SoFi Stadium in Inglewood, California, a FIFA World Cup 2026 host venue",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ──────────────────────────────────────────
# Article 2: Oberoi Rajgarh Palace
# ──────────────────────────────────────────
art2_body = """A 350-year-old palace near Khajuraho in Madhya Pradesh has just been named one of the 16 most beautiful hotels in the world — and it is the only property in India on the list.

The Oberoi Rajgarh Palace was selected for the 2026 Prix Versailles, an international architecture and design award program associated with UNESCO that celebrates properties blending aesthetic excellence, cultural identity, and environmental responsibility. The palace joins hotels in Italy, France, Croatia, Georgia, Saudi Arabia, Morocco, Mexico, Thailand, and China on the shortlist. It is the kind of recognition that typically drives a property from "insider knowledge" to "fully booked through December."

## From Royal Residence to Luxury Hotel

The Rajgarh Palace was not built for tourists. It was a functioning royal court for roughly three and a half centuries, overlooking landscaped gardens and a lake in the Bundelkhand region of central India. The Oberoi Group's restoration preserved the original architectural bones — the carved stone facades, the courtyards, the regional design vocabulary — while adding the discreet luxuries that differentiate a heritage stay from a heritage museum: climate control, modern plumbing, a spa, and the kind of service that Oberoi properties are known for.

The restoration follows a model that India's luxury hospitality sector has been perfecting for two decades: take a building with genuine historical weight, invest in careful adaptive reuse rather than demolition and rebuild, and charge rates that reflect both the quality and the irreplicability of the experience. The Taj Lake Palace in Udaipur, Sujan Rajmahal in Jaipur, and Alila Fort Bishangarh established the template. The Rajgarh Palace extends it deeper into India's cultural heartland.

## The Khajuraho Advantage

For NRIs planning a trip to India, the Rajgarh Palace solves a problem that heritage travellers know well: Khajuraho is a UNESCO World Heritage Site with some of the finest temple sculpture on the planet, but it has historically lacked a luxury hotel that matches the destination's significance. Visitors would fly in from Delhi or Varanasi, spend a few hours at the temples, and leave the same day.

The Oberoi changes that calculation. With a palace hotel a short drive from the temple complex, Khajuraho becomes a multi-day destination. Add in Panna National Park — one of India's most successful tiger conservation stories, less than an hour away — and you have a three-day itinerary that combines heritage, wildlife, and luxury without the crowds and touts of Rajasthan's golden triangle.

Direct flights connect Khajuraho to Delhi and Varanasi. From Delhi, the flight is roughly 75 minutes. For NRI families accustomed to the Jaipur-Udaipur circuit, this is genuinely new territory — central India's less-trafficked cultural corridor, anchored by a property that just earned global validation.

## Why Heritage Hotels Matter for the Diaspora

India's palace-hotel renaissance is not just a hospitality story. It is a preservation story. Many of these buildings would have crumbled without private investment. The economics only work because there is a market willing to pay premium rates for the experience — and the Indian diaspora, with its combination of cultural connection and international travel budgets, is a core part of that market.

The Prix Versailles recognition matters because it tells a global audience what India's heritage travellers already know: the best hotel experiences in the country are not in glass towers. They are in restored forts, converted palaces, and reimagined havelis where the building itself is the experience. The Oberoi Rajgarh Palace is simply the latest — and perhaps the most striking — example."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Oberoi Rajgarh Palace Just Made the World's 16 Most Beautiful Hotels — and NRIs Should Take Note",
    "subheadline": "A 350-year-old palace near Khajuraho wins Prix Versailles recognition, anchoring a new luxury itinerary that pairs UNESCO temples with tiger country.",
    "slug": make_slug("oberoi-rajgarh-palace-worlds-most-beautiful-hotel-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "India's palace-hotel renaissance depends on the diaspora: NRI families with cultural connection and international travel budgets are a core market for heritage luxury properties that might otherwise crumble. The Rajgarh Palace opens a new central India itinerary beyond the usual Rajasthan circuit.",
    "tags": ["travel", "luxury", "heritage", "hotel", "khajuraho", "oberoi", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/62gk6l0x7h5w/"},
        {"name": "Prix Versailles", "url": "https://www.prix-versailles.com/"},
        {"name": "Wikipedia — Khajuraho Group of Monuments", "url": "https://en.wikipedia.org/wiki/Khajuraho_Group_of_Monuments"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/1_Khajuraho.jpg",
    "image_caption": "The Khajuraho temple complex in Madhya Pradesh, a UNESCO World Heritage Site near the Oberoi Rajgarh Palace",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ──────────────────────────────────────────
# Article 3: Sri Lanka Free Visa for Indians
# ──────────────────────────────────────────
art3_body = """Sri Lanka just made it free for Indian citizens to visit — and the numbers suggest the timing is no accident.

Effective May 25, the Sri Lankan government began offering free 30-day Electronic Travel Authorizations to citizens of 40 countries, India among them. The double-entry ETA eliminates the processing fee that previously applied, removing one of the last friction points for what has always been one of the subcontinent's most accessible international getaways. And the results are already visible: Sri Lanka recorded 145,745 international tourists in May 2026, the highest May figure in the country's history, up 9.6 percent from the same month last year.

India is Sri Lanka's single largest source market. That is not new. What is new is the pace of recovery and the deliberate policy machinery behind it.

## What Changed — and What It Means

The free ETA is straightforward: Indian passport holders apply online, receive a 30-day tourist authorization at no cost, and get double-entry flexibility within the validity period. Extensions beyond 30 days require a separate application and fee. The system replaces the old paid ETA process, which charged $35 to $50 depending on the application method.

The 40-country list reads like a tourism marketing wish list: India, China, the US, the UK, Germany, Australia, Japan, South Korea, France, the UAE, Saudi Arabia, and more. By removing the visa fee for its highest-volume markets simultaneously, Sri Lanka is betting that reduced friction at the front door translates to higher spending once visitors are inside.

For NRI families, the math is particularly compelling. An Indian American family of four previously paid $140 to $200 in ETA fees alone before setting foot on the island. That cost is now zero.

## The NRI Case for Sri Lanka

Sri Lanka occupies a peculiar sweet spot in the NRI travel universe. It is close enough to India that a visit home can easily include a four- or five-day Sri Lanka extension — Colombo is a two-hour flight from Chennai, 90 minutes from Trivandrum. It is far enough from the Indian tourist mainstream to feel like a distinct international trip. And it offers a density of experiences — ancient ruins, wildlife, beaches, hill country, and some of South Asia's best boutique hotels — that few destinations its size can match.

Sigiriya, the fifth-century rock fortress that is Sri Lanka's most visited site, remains one of the subcontinent's most dramatic heritage experiences. The cultural triangle connecting Sigiriya, Polonnaruwa, and Anuradhapura rivals anything on India's temple circuit. Yala National Park's leopard population draws serious wildlife enthusiasts. And the southern coast — Galle, Unawatuna, Mirissa — has developed a boutique hospitality scene that caters to precisely the kind of design-conscious, experience-driven traveller that many NRI families have become.

## Monsoon Timing Works in Your Favour

Here is the practical angle that travel agents will not tell you for free: Sri Lanka's southwest monsoon runs roughly from May through September, which means the popular southern and western coasts see rain during these months. But the east coast — Trincomalee, Pasikuda, Arugam Bay — is bone-dry and stunning from June through September. Hotel rates on the east coast during monsoon season can be 40 to 60 percent lower than the south coast in peak winter season.

For NRI families visiting India during the summer months, a quick side trip to Sri Lanka's east coast delivers beach-resort quality at monsoon-discount prices, with no visa fee and flights from Chennai or Bangalore costing under $100 each way on budget carriers.

## What to Know Before Booking

The free ETA must be applied for before travel — it is not visa-on-arrival. Processing is typically 24 to 48 hours through Sri Lanka's official ETA portal. Carry a printout or digital copy. The double-entry feature means you can leave and return within the 30-day window, useful if combining Sri Lanka with a side trip to the Maldives (which also offers visa-on-arrival for Indians).

Currency: the Sri Lankan rupee has stabilised significantly since the 2022 economic crisis, and USD and Indian rupee acceptance is widespread in tourist areas. Infrastructure has improved markedly — the Southern Expressway from Colombo to Galle cuts what was once a four-hour drive to under two.

Sri Lanka has been quietly rebuilding its tourism proposition for four years. The free ETA is the clearest signal yet that the rebuilding is complete — and that India, as always, is the market that matters most."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Sri Lanka Just Dropped Visa Fees for Indians — and Record Tourist Numbers Show the Bet Is Working",
    "subheadline": "Free 30-day ETAs for 40 countries including India, a record 145,745 visitors in May, and monsoon-season east-coast deals make Sri Lanka the smartest NRI side trip of the summer.",
    "slug": make_slug("sri-lanka-free-visa-indians-record-tourism-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "India is Sri Lanka's largest source market, and NRI families visiting India this summer can add a 4-5 day Sri Lanka extension with zero visa fees, $100 flights from Chennai, and east-coast monsoon-season hotel discounts of 40-60 percent.",
    "tags": ["travel", "sri lanka", "visa", "nri", "tourism", "monsoon"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World — Sri Lanka Free ETA", "url": "https://www.travelandtourworld.com/news/article/india-joins-china-pakistan-indonesia-us-uk-sri-lanka-free-30-day-etas/"},
        {"name": "Travel And Tour World — Sri Lanka May 2026 Tourism", "url": "https://www.travelandtourworld.com/news/article/sri-lanka-records-145745-international-visitors-may-2026/"},
        {"name": "Travel And Tour World — Sri Lanka Oman Connectivity", "url": "https://www.travelandtourworld.com/news/article/sri-lanka-oman-strengthening-travel-connectivity/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Sigiriya_%28141688197%29.jpeg",
    "image_caption": "Sigiriya rock fortress in central Sri Lanka, a UNESCO World Heritage Site and the island's most visited landmark",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ──────────────────────────────────────────
# Insert all articles
# ──────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
