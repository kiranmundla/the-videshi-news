#!/usr/bin/env python3
"""Travel writer — 2026-06-26 23:00 PT batch. Three articles."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────
# ARTICLE 1 — Adani Airport Cities
# ─────────────────────────────────────────────

article1_body = """Adani Airport Holdings Limited — India's largest private airport operator — has announced plans to invest more than ₹20,000 crore ($2.12 billion) in developing integrated airport cities at six airports across the country. The developments will span over 655 acres and roughly 22 million square feet across Mumbai, Navi Mumbai, Ahmedabad, Lucknow, Jaipur, and Guwahati.

Nearly 70 per cent of the planned investment will be concentrated in Mumbai and Navi Mumbai alone, a reflection of the metropolitan region's dominance as India's aviation gateway.

## What the airport cities will actually include

The developments are designed as walkable urban districts that combine hotels, offices, retail, dining, entertainment, and convention infrastructure — all connected to airport terminals, Metro stations, and city transport links. Think less "airport shopping mall" and more self-contained commercial ecosystem.

Adani Airport City Limited, the subsidiary leading the effort, has already signed agreements with IHG Hotels & Resorts for five properties across the network. Talks are underway with food and beverage and entertainment partners.

Jeet Adani, Director of Adani Airport Holdings, positioned the project as part of a broader global trend. "Around the world, the most successful airport districts have become centres of commerce, tourism and urban growth," he said, citing Changi in Singapore, Schiphol in Amsterdam, Incheon in Seoul, and Dubai International as models.

## Why this matters if you fly through India regularly

For NRIs who transit through Mumbai, Ahmedabad, or Jaipur — often on red-eye arrivals or with long layovers — the promise of brand-name hotels, proper dining, and entertainment within the airport precinct is a meaningful quality-of-life upgrade. Today, the experience at most Indian airports between arrivals and a connecting domestic flight is a combination of crowded lounges and limited food courts.

The Navi Mumbai airport, which recently began commercial operations and has its first international flights launching in July, is particularly significant. With 440 acres of the 655-acre land bank concentrated in the Mumbai–Navi Mumbai corridor, the Adani Group is betting that the twin airports will collectively function as an aerotropolis — a concept that's already proven at Dubai and Incheon.

## The bigger picture: airports as economic engines

The announcement arrives as India's aviation sector undergoes its most ambitious expansion in decades. Air India has just launched its hub-and-spoke "Easy Connect" service from Varanasi, the Noida International Airport (Jewar) opened for domestic flights this month, and Indian carriers are rebuilding capacity on Gulf and European routes.

Adani's airport city strategy is a bet that India's airports can capture the economic value that currently leaks to city-centre hotels and business districts. For the diaspora, it means the airport itself may no longer be the least pleasant part of the trip home.

The first phase of construction timelines and specific hotel opening dates have not been disclosed. But with IHG already signed and architectural partners reportedly engaged, the ₹20,000-crore plan is past the concept stage."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Adani Bets ₹20,000 Crore on Turning Six Indian Airports Into Mini-Cities — and Mumbai Gets the Lion's Share",
    "subheadline": "Hotels, retail, entertainment, and convention centres across 655 acres at six airports. The Adani Group is borrowing from Changi and Schiphol to reimagine how India's airports function.",
    "slug": make_slug("adani-airport-cities-mumbai-navi-mumbai-ihg-hotels-nri"),
    "category": "travel",
    "vertical": "infrastructure",
    "diaspora_angle": "NRIs transiting through Mumbai, Ahmedabad, and Jaipur will see brand-name hotels and walkable commercial districts built around terminals — a meaningful upgrade over the current layover experience.",
    "tags": ["travel", "airports", "infrastructure", "adani", "mumbai", "hotels"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/indias-adani-airports-invest-over-2-billion-developing-airport-cities-2026-06-26/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/adani-airports-to-invest-20000-cr-in-airport-city-projects-across-6-airports/article69726849.ece"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/adani-airports-announces-20000-crore-airport-city-expansion-across-india"},
        {"name": "IndUS Business Journal", "url": "https://www.indusbusinessjournal.com/adani-airports-plans-2-4-billion-airport-city-development-across-five-states/"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Mumbai_03-2016_114_Airport_international_terminal_interior.jpg/1280px-Mumbai_03-2016_114_Airport_international_terminal_interior.jpg",
    "image_caption": "Interior of Mumbai's Chhatrapati Shivaji Maharaj International Airport terminal",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ─────────────────────────────────────────────
# ARTICLE 2 — Gulf flights restoration
# ─────────────────────────────────────────────

article2_body = """India's biggest airlines are racing to rebuild their West Asia schedules after the deepest capacity cuts in years — but the numbers tell a story of cautious recovery, not restoration.

By June, IndiGo, Air India Express, and Air India have collectively accelerated the return of flights to Dubai, Abu Dhabi, Doha, and Jeddah. Air India Express says it has restored roughly 80 per cent of its Gulf operations, with around 2,500 monthly flights (about 1,250 departures from India) now running. IndiGo says it has "progressively" restored India–West Asia capacity, with most expected to return by the end of June.

But the fine print matters. Air India Express is still operating about 1,244 departures in June against 1,784 last year — a 30 per cent shortfall. Air India is at 355 departures versus 607 a year ago, a 42 per cent gap. Full restoration, carriers warn, "could take longer" as some Gulf airports still face operational restrictions.

## How the crisis unfolded

The disruption traces back to late February, when conflict in West Asia triggered airspace restrictions that forced Indian airlines to cancel, reroute, or sharply cut Gulf-bound services. The closure of Pakistani airspace since April 2025 compounded the problem, adding flying time and fuel costs to virtually every westbound international route.

April marked the bottom. OAG data shows IndiGo operated just 623 West Asia departures that month — down 72 per cent year-on-year. Air India Express fell 68 per cent, and Air India dropped 77 per cent. Rising jet fuel prices layered further pressure on already thin margins.

By May, conditions began improving as restrictions eased. Airlines gradually rebuilt schedules, and by June the trend accelerated — though without reaching pre-crisis levels.

## The NRI connection: transit math and ticket prices

For the roughly 9 million Indian nationals living in the Gulf, the capacity shortfall directly shrinks their flight options. But the impact extends well beyond the Gulf itself. Dubai, Abu Dhabi, and Doha are the primary connecting hubs for NRIs flying between the US and India — particularly on itineraries like SFO–DXB–BOM or JFK–DOH–DEL that avoid the long nonstop.

Fewer seats on India–Gulf legs mean fewer connecting options, longer layovers, and higher fares on the very routes the diaspora uses most for summer and Diwali trips. The economics are simple: when IndiGo offers 72 per cent fewer Gulf departures, the connecting inventory available through codeshare and interline partners drops proportionally.

Air India Express is adding new routes, including Navi Mumbai–Abu Dhabi, to diversify its network. IndiGo has cautioned that "a full restoration could take longer as some airports in the region continue to face operational restrictions and infrastructure constraints."

## What to watch next

The key variable is airspace. Pakistan's closure remains the single biggest structural constraint on Indian carriers' ability to operate profitably on westbound routes. Each detour adds fuel cost and crew time that gets passed to passengers. Until that corridor reopens, full capacity restoration — and the fare relief that comes with it — will remain out of reach.

For NRIs planning autumn or Diwali travel through Gulf hubs, the practical advice is unchanged: book early, expect higher fares than 2024, and monitor whether capacity continues to inch upward through the summer."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Airlines Are Rebuilding Gulf Routes — but Seat Counts Still Lag Last Year by 30 to 40 Per Cent",
    "subheadline": "After months of airspace-driven capacity cuts, IndiGo, Air India Express, and Air India are restoring West Asia flights. The recovery is real but incomplete — and fares still bite.",
    "slug": make_slug("indian-airlines-gulf-west-asia-flights-capacity-recovery-nri"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "Dubai, Abu Dhabi, and Doha are the primary transit hubs for NRIs flying India–US routes. Fewer Gulf seats mean fewer connecting options, longer layovers, and higher fares for summer and Diwali trips.",
    "tags": ["travel", "airlines", "gulf", "west-asia", "indigo", "air-india-express", "fares"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mint", "url": "https://www.livemint.com/industry/indian-airlines-west-asia-flights-capacity-recovery-2026-11782355005689.html"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-launches-easy-connect-service-to-transform-international-travel/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-make-foreign-travel-more-accessible-to-bharat-ai-ceo/article69722438.ece"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Air_India_Express_aircraft_in_front_of_terminal_1C_at_Mumbai_airport_%281%29.JPG/1280px-Air_India_Express_aircraft_in_front_of_terminal_1C_at_Mumbai_airport_%281%29.JPG",
    "image_caption": "An Air India Express aircraft at Terminal 1C of Mumbai's Chhatrapati Shivaji Maharaj International Airport",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}


# ─────────────────────────────────────────────
# ARTICLE 3 — Outbound tourism pivot
# ─────────────────────────────────────────────

article3_body = """India's outbound tourism market is still growing in raw volume — but a structural shift is underway that NRIs in the US, UK, and Australia should pay attention to. Fewer Indian travellers are heading west. More are heading to Southeast Asia, the Middle East, and nearby visa-easy destinations. And the forces driving this aren't temporary.

Multiple long-haul destinations — including the United States, South Africa, Australia, China, and Egypt — are reporting a slowdown in Indian visitor arrivals in 2026. The numbers are softening not because Indians have stopped travelling, but because they're redirecting their spending toward shorter-haul, lower-cost, and visa-simplified alternatives like Thailand, Vietnam, Malaysia, Sri Lanka, and the UAE.

## Three forces bending the curve

**Rising airfares.** With crude oil above $100 a barrel following the Hormuz crisis, fuel surcharges on long-haul routes have climbed steadily. An economy round trip from Delhi to New York that cost ₹65,000 last summer now starts north of ₹85,000 on most carriers. The rupee's slide against the dollar compounds the pain.

**Visa friction.** India–US B1/B2 visa wait times at several consulates have stretched past 100 days for new applicants. Schengen appointments aren't much better. In contrast, Thailand now offers a 60-day visa-free entry (with a proposed 15-day exemption under discussion), Malaysia offers 30 days visa-free, and Indonesia provides visa-on-arrival at Bali.

**The Modi nudge.** On May 10, Prime Minister Modi publicly appealed to Indians to avoid unnecessary foreign travel for at least a year — framing it as a patriotic measure to conserve foreign exchange reserves during the Hormuz-driven energy crisis. RBI data shows overseas travel spending had already fallen 3 per cent to $15.3 billion in FY26 even before the appeal. Tour operators report a 10–15 per cent drop in summer inquiries.

## What this means for the diaspora

The most immediate impact for NRIs is personal: fewer visits from family. The annual summer trip to the US — a staple of Indian upper-middle-class family life — is being deferred, shortened, or redirected. Parents who would normally fly to San Francisco or New Jersey for three months are weighing the ₹1.7-lakh round-trip against a two-week holiday in Bali for a third of the price.

Travel stocks in India have felt the pressure. Shares in EaseMyTrip, Yatra Online, and Ixigo sold off after Modi's remarks. Airlines that depend heavily on outbound premium traffic are recalibrating summer schedules.

For NRIs considering a reverse trip to India, there's an upside: domestic tourism infrastructure is getting more attention and investment than ever. Hotel rates in monsoon season drop 30–50 per cent from winter peaks. And Modi's own messaging has nudged India's hospitality sector to raise its game for domestic visitors.

## The structural question

Whether this is a one-year correction or a longer trend depends on two variables: oil prices and airspace access. If the Hormuz corridor stabilises and Pakistani airspace reopens, fuel surcharges will ease and capacity will return. If they don't, India's outbound tourism — worth $18.8 billion in 2024 and projected to reach $55 billion by 2034 — will continue reshaping itself around shorter, cheaper, visa-free corridors.

For the Indian diaspora, the calculus is clear: if you want family to visit this year, expect to help with tickets. If you're visiting India instead, you'll find the monsoon airfares surprisingly reasonable — and the country increasingly eager to welcome you."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Fewer Indians Are Flying West This Summer — and the Diaspora Should Notice",
    "subheadline": "Rising airfares, a weaker rupee, the Hormuz crisis, and a prime ministerial nudge are steering India's outbound tourism toward Asia. Long-haul destinations — including the US — are feeling the pinch.",
    "slug": make_slug("india-outbound-tourism-pivot-west-asia-us-visits-fewer-nri"),
    "category": "travel",
    "vertical": "travel-trends",
    "diaspora_angle": "NRIs expecting family visits from India this summer are already seeing cancellations. Rising airfares, visa friction, and Modi's travel-domestic appeal are reshaping the economics of an India-to-US trip.",
    "tags": ["travel", "outbound-tourism", "airfares", "visa", "modi", "nri-families"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/south-africa-india-tourism-arrivals-2026/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-travel-industry-braces-hit-modis-appeal-avoid-foreign-trips-2026-05-13/"},
        {"name": "TradingView / Moneycontrol", "url": "https://www.tradingview.com/news/moneycontrol:7bdf20756094b:0-even-before-pm-s-appeal-overseas-travel-spend-fell-3-to-15-3-billion-in-fy26-rbi-data-shows/"},
        {"name": "Outlook Money", "url": "https://www.outlookmoney.com/personal-finance/overseas-travel-spend-fell-even-before-pm-modis-nation-first-appeal"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37540293/pexels-photo-37540293.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Airplanes on the tarmac at Delhi's Indira Gandhi International Airport",
    "image_attribution": "Pexels",
    "body": article3_body.strip(),
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
