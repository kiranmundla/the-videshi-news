#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Opens Its First US Airport Lounge at SFO — and It's Built for the Bay Area Diaspora",
        "subheadline": "The new 3,300-square-foot Maharaja Lounge near Gate A1 features an Aviator's Bar, live cooking stations, and tarmac views — a signal that Air India is finally investing in ground experience on its busiest American corridor.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-opens"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO is Air India's biggest West Coast gateway, with daily nonstops to Delhi and onward connections to Bangalore, Mumbai, and Hyderabad. The 500,000-plus Indian Americans in the Bay Area — many of whom fly home at least once a year — have long endured SFO's generic international terminal with no dedicated lounge. This changes that equation for business and first class passengers, plus Star Alliance Gold members flying partners like United.",
        "tags": ["travel", "airlines", "air-india", "sfo", "bay-area", "lounge"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indian Eagle Travel Beats", "url": "https://www.indianeagle.com/travelbeats/air-india-lounge-san-francisco-sfo/"},
            {"name": "Air India (official)", "url": "https://www.airindia.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2612117/pexels-photo-2612117.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An elegant airport lounge — Air India's new Maharaja Lounge at SFO aims to bring this level of comfort to Bay Area flyers.",
        "body": """For years, flying Air India out of San Francisco International Airport meant an oddly spartan pre-departure ritual. You cleared TSA, wandered the international terminal, maybe grabbed a coffee, and boarded. No lounge, no ceremony — just a gate and a prayer that your 16-hour flight to Delhi would go smoothly.

That changed on May 23, when Air India opened the Maharaja Lounge at SFO — its first purpose-built lounge anywhere in the United States.

## What's Inside

The lounge occupies 3,300 square feet near Gate A1 on Level 4 of the International Terminal's Boarding A zone. It seats 80 guests and is divided into distinct areas that echo the airline's broader brand overhaul under Tata Group ownership.

The **Aviator's Bar** anchors the space with an curated selection of wines, whiskies, and a signature cocktail called the Maharaja Manhattan — described by the airline as "a regal twist on the classic Manhattan that honors black pepper as the Maharaja of spices." The warm-toned interiors lean into Indian luxury without the kitsch.

A **dedicated dining area** features live cooking stations, a hot buffet island, a cold counter, and a beverage station. Guests can request dishes customized to their preferences — a nod to the kind of personalized service that premium passengers on Gulf carriers have long expected.

The **Private Zone** is reserved for First Class passengers and offers an intimate, quiet environment for work or rest. The **Social Zone** arranges seating to encourage interaction while maintaining privacy, and several sections along the tarmac-facing windows offer views of aircraft on the apron.

## Who Gets In

Access is limited to Air India First and Business Class passengers, Maharaja Club Platinum and Gold members, and eligible Star Alliance Gold travelers flying on partner airlines. That last category is significant: Bay Area NRIs who hold United MileagePlus Gold status through credit card spend or domestic flying now have lounge access before their Air India connections — even if they booked the cheapest business fare.

## Why SFO First

Air India operates daily nonstop flights from SFO to New Delhi — seven per week on the summer 2026 schedule — plus connections onward to Mumbai, Bangalore, and Hyderabad. The SFO-DEL corridor is one of the airline's most commercially important routes globally, driven by the massive concentration of Indian tech workers and families across Silicon Valley, the Peninsula, and the East Bay.

The airline is renovating a second Maharaja Lounge at New York JFK, its other major US gateway. But SFO came first, and the reason is arithmetic: the Bay Area's Indian American population — estimated at over 500,000 — generates a disproportionate share of premium cabin demand on westbound India routes.

## The Bigger Picture

The lounge opening is one piece of a larger transformation at Air India under Tata ownership. The airline has been overhauling its fleet, cabin product, loyalty program, and ground services since the 2022 acquisition. For NRIs who grew up avoiding Air India in favor of Emirates, Singapore Airlines, or even United's Polaris, the Maharaja Lounge is a tangible signal that the airline is serious about competing for premium passengers on US-India routes.

Whether it works depends on consistency — a beautiful lounge means little if the onboard soft product doesn't match. But for now, Bay Area travelers headed to India have one less reason to connect through Dubai or Singapore, and one more reason to book direct."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Navi Mumbai Airport Opens for Commercial Flights — What It Means for NRIs Flying Into Maharashtra",
        "subheadline": "India's newest international-grade airport launched with IndiGo as its first carrier, connecting to 10 domestic cities. For the diaspora, it promises a second gateway into Mumbai that skips the infamous traffic crawl from Andheri.",
        "slug": make_slug("navi-mumbai-airport-nmia-opens-indigo"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying into Mumbai have long dreaded the post-landing ordeal: an hour or more crawling through Andheri and the Western Express Highway to reach Navi Mumbai, Pune, or anywhere south of the city. NMIA, located near Panvel with highway and future metro connectivity, fundamentally changes this. For the large Maharashtrian and Konkan diaspora in the US, it also means future international flights could land closer to hometowns in Raigad, Pune, and the Konkan belt.",
        "tags": ["travel", "airports", "navi-mumbai", "indigo", "infrastructure", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/vr6b1qt8am77/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19528200/pexels-photo-19528200.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Mumbai airport architecture at night — the new Navi Mumbai International Airport adds a second gateway to India's financial capital.",
        "body": """On May 22, an IndiGo Airbus A320 from Bangalore touched down at Navi Mumbai International Airport to a water-cannon salute and a crowd of officials, media, and genuinely excited passengers. Minutes later, a departure to Hyderabad completed the inaugural cycle. India's most anticipated airport project in a decade was officially open for business.

## The Basics

NMIA — developed by the Adani Group in coordination with CIDCO (City and Industrial Development Corporation of Maharashtra) — launched with a single runway and one terminal, built for an initial capacity of 20 million passengers annually. The long-term plan envisions two runways and capacity for 90 million passengers, which would make it one of the largest airports in South Asia. The project cost: roughly ₹19,650 crore.

IndiGo is the launch carrier, connecting NMIA in its first phase to Delhi, Bangalore, Hyderabad, Ahmedabad, Lucknow, Goa (Mopa), Jaipur, Nagpur, Kochi, and Mangalore. Akasa Air has announced a Delhi–Navi Mumbai service as well. Operations currently run on a 12-hour window, 8 AM to 8 PM, with expansion planned as airspace coordination with the existing Chhatrapati Shivaji Maharaj International Airport matures.

## Why This Matters to the Diaspora

For the roughly 700,000 Indian Americans with roots in Maharashtra, flying into Mumbai has always come with a catch: the airport is in Andheri, deep in the city's northern sprawl. If your family is in Navi Mumbai, Panvel, Kharghar, or anywhere along the Mumbai-Pune corridor, you've spent countless post-landing hours in traffic that makes the 405 look civilized.

NMIA sits near key highways south of Mumbai, and planned metro connectivity will link it to the broader Navi Mumbai transit network. For diaspora travelers headed to Pune — about 90 minutes by expressway from NMIA versus 3-4 hours from the existing airport in traffic — the math is transformative.

The airport also opens a second point of entry for the Konkan belt. NRIs from Ratnagiri, Sindhudurg, and coastal Maharashtra currently fly into Mumbai and then endure a 6-8 hour drive or take a connecting flight. NMIA's proximity to the Mumbai-Goa highway corridor makes that journey significantly shorter.

## International Flights: When?

The question every NRI is asking: when can I fly SFO-to-NMIA nonstop? Not yet. The airport launched with domestic routes only, and international operations depend on customs/immigration infrastructure buildout, airline demand assessments, and the resolution of shared airspace coordination with Mumbai's existing airport.

Realistically, international flights — likely starting with Gulf carriers connecting through Dubai and Doha — could begin within 12-18 months. Air India and IndiGo international services may follow. For now, the diaspora play is connecting through Delhi or Bangalore to reach NMIA domestically, skipping the Andheri transfer entirely.

## The Emotional Dimension

For families in Navi Mumbai and the satellite cities that have boomed over the past two decades — Kharghar, Ulwe, Panvel, Taloja — this airport is more than infrastructure. It's validation. These neighborhoods have absorbed millions of Mumbai's growth while being treated as the city's afterthought. An international-grade airport on their side of the creek changes the identity of the entire region.

NRI families who bought flats in Kharghar or Panvel a decade ago, partly on the promise of this airport, are finally seeing that bet pay off. Property values in the NMIA catchment area have already risen 15-25% in anticipation, according to local real estate trackers.

## What to Watch

The first phase is deliberately constrained — 12-hour operations, domestic routes only, one carrier dominating the schedule. The test will be whether NMIA can ramp up smoothly without the operational chaos that has plagued other Indian airport launches. For now, the runway is open, the salute has been given, and Mumbai finally has a second front door."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Summer India Flights Are Getting Expensive — Here's How NRIs Can Still Find Reasonable Fares",
        "subheadline": "Global airfare inflation, rising fuel costs, and surging demand on US-India routes are pushing summer round-trips past $1,500. A practical guide to booking smarter on the corridors that matter most to the diaspora.",
        "slug": make_slug("summer-india-flights-expensive-nri-booking-tips"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The 4.4 million Indian Americans collectively represent one of the largest long-haul travel markets in the world, with most families flying to India at least once a year — often in summer when kids are out of school. Rising fares on SFO-DEL, JFK-BOM, ORD-HYD, and LAX-BLR corridors directly impact household budgets, especially for families of four where a summer trip can easily exceed $6,000 in airfare alone.",
        "tags": ["travel", "flights", "airfare", "booking-tips", "summer-travel", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/v7lmod2vey86/"},
            {"name": "IATA Global Aviation Economics", "url": "https://www.iata.org"},
            {"name": "MyTicketsToIndia", "url": "https://myticketstoindia.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7310015/pexels-photo-7310015.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passport and boarding passes ready — planning ahead is key as summer India fares climb in 2026.",
        "body": """If you've been watching fares on your usual SFO-Delhi or JFK-Mumbai route this month, you already know: summer 2026 is not going to be cheap. Round-trip tickets on key diaspora corridors are running $1,200-$1,800 in economy — up 15-25% from the same period last year — and the trend is global.

## What's Driving the Surge

The International Air Transport Association (IATA) and multiple industry trackers point to a convergence of factors hitting simultaneously in 2026:

**Fuel costs remain elevated.** Aviation turbine fuel prices have stayed stubbornly high, driven by Red Sea shipping instability and broader geopolitical tensions affecting energy supply chains. Airlines have passed much of this cost through to passengers.

**Demand on US-India routes is at record levels.** The Indian American population continues to grow — now at 4.4 million — and summer remains the peak season for family visits, weddings, and festivals. Airlines have added capacity, but demand is outpacing supply on the busiest corridors.

**Hotel inflation compounds the pain.** It's not just flights. Hotel rates across India's major cities — Delhi, Mumbai, Bangalore, Hyderabad — are up 10-15% year-over-year. The total cost of a two-week India trip for a family of four has crossed $10,000 for the first time for many NRI families.

**The global picture is similar.** The US, Germany, UAE, France, Japan, and Australia are all seeing travelers delay holidays, shorten trips, and shift to regional travel due to rising costs. India is no exception — domestic airfares within India have also climbed.

## The Corridors That Matter

For Indian Americans, the routes that define summer travel are:

- **SFO → DEL**: Air India nonstop (daily), United via connections. Currently $1,300-$1,700 round-trip economy.
- **JFK → BOM**: Air India nonstop, Emirates/Qatar via Gulf. $1,100-$1,600.
- **ORD → HYD**: No nonstop — typically Emirates via Dubai or Qatar via Doha. $1,200-$1,500.
- **LAX → BLR**: Air India one-stop via Delhi, or Gulf carriers. $1,300-$1,800.
- **EWR → DEL**: United nonstop, Air India. $1,200-$1,600.

One-way fares from SFO to India are being listed as low as $500-600 on aggregators, but these are typically multi-stop itineraries on less premium carriers with long layovers.

## How to Book Smarter

None of this is revolutionary, but the basics matter more when fares are high:

**Book 8-12 weeks out for summer travel.** The sweet spot for US-India economy fares is roughly 2-3 months before departure. Last-minute bookings in June and July are running 30-40% premiums over advance purchases.

**Consider shoulder dates.** Departing in the last week of May or first week of August — just outside peak summer — can save $200-400 per ticket. If your schedule allows it, mid-week departures (Tuesday/Wednesday) consistently price lower than weekend flights.

**Watch the Gulf carriers.** Emirates, Qatar Airways, and Etihad often price competitively on US-India routes, especially to South Indian cities. The trade-off is a stop in Dubai, Doha, or Abu Dhabi, but their connection experiences are significantly better than most alternatives.

**Use Google Flights tracking.** Set fare alerts for your specific corridor. Prices fluctuate daily, and a $200-per-ticket drop on a family booking adds up fast.

**Don't ignore credit card travel portals.** Chase Sapphire, Amex Platinum, and Capital One Venture cardholders can often find 10-20% better effective rates through portal bookings, especially when combined with transfer partner programs to airline miles.

**Consider positioning flights.** If you're in a secondary market (Sacramento, San Jose, Portland), sometimes booking a separate cheap domestic flight to a major gateway like SFO or LAX and then booking the international leg separately yields a lower total cost than a single through-ticket.

## The Bigger Question

For NRI families who treat the annual India trip as non-negotiable — and most do — the question isn't whether to go but how to absorb the cost increase. Some families are shortening trips from three weeks to two. Others are shifting from summer to the Diwali window (October-November), where fares are typically 20-30% lower. A few are experimenting with flying into alternative Indian airports — Ahmedabad, Kochi, Amritsar — where demand is lower and connections can be cheaper.

The hard truth: summer India travel in 2026 requires more planning and flexibility than it has in years. The fares aren't coming down before September. Budget accordingly, book early, and set those Google Flights alerts."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
