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
        "headline": "Swiss Air Lines Will Fly Nonstop to Bengaluru From October — and South India's Tech Corridor Finally Gets a Direct European Link",
        "subheadline": "The Lufthansa Group subsidiary will operate five weekly Zurich-Bengaluru flights on the A350, its first route to southern India — opening a direct Schengen gateway for 300,000+ Indian-origin residents in the DACH region.",
        "slug": make_slug("swiss-air-zurich-bengaluru-nonstop-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Swiss Air's new Zurich-Bengaluru nonstop creates a direct connection between India's tech capital and Europe's financial center, benefiting the 300K+ Indian-origin residents in Switzerland, Germany, and Austria who currently rely on Gulf carrier connections through Dubai or Doha.",
        "tags": ["travel", "airlines", "bengaluru", "europe", "swiss-air", "lufthansa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/lufthansa-group-winter-expansion-new-long-haul-routes/"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/05/29/lufthansa-to-fly-allegris-cabin-on-11-new-long-haul-destinations/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/africa-and-asia-await-new-direct-european-flights/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17166882/pexels-photo-17166882.jpeg",
        "body": """Swiss International Air Lines will launch nonstop flights between Zurich and Bengaluru beginning in October 2026, marking the carrier's first-ever route to southern India and giving the country's technology capital a direct link to the heart of Europe.

The new service, announced as part of the Lufthansa Group's winter 2026/27 schedule expansion, will operate five times weekly on the Airbus A350 — the wide-body workhorse that Swiss has been deploying across its most premium long-haul routes. Flights will connect Zurich Airport, Switzerland's primary international hub, with Kempegowda International Airport in Bengaluru.

## Why Bengaluru, Why Now

The choice of Bengaluru is not arbitrary. The city has emerged as India's most important international aviation market after Delhi and Mumbai, handling 44.5 million passengers in the fiscal year ending March 2026 — a 6.2% increase year-on-year. In April 2026, Bengaluru overtook Mumbai to become India's second-busiest airport for domestic traffic, a milestone driven by the city's booming tech economy and expanding infrastructure.

For Swiss, the route plugs a conspicuous gap. Lufthansa Group already serves Delhi and Mumbai through its Frankfurt and Munich hubs, but southern India — home to the country's largest IT clusters and a growing base of corporate travel demand — has been underserved by direct European connections.

The A350's range and economics make the route viable in a way that older wide-bodies could not. At roughly 7,800 kilometres, the Zurich-Bengaluru sector sits comfortably within the aircraft's capabilities while offering the fuel efficiency that justifies five weekly frequencies on a route that is not yet high-volume.

## What It Means for NRIs in Europe

For the estimated 300,000 Indian-origin residents in Switzerland, Germany, and Austria — the so-called DACH region — the new route eliminates what has long been a frustrating detour. Flying from Zurich to Bengaluru currently requires a connection, typically through Dubai, Doha, or Mumbai. That adds four to six hours to what will become an approximately nine-hour nonstop flight.

The NRI population in Switzerland alone has grown steadily, driven by the country's financial sector, pharmaceutical industry, and a string of multinational headquarters that actively recruit from India's tech talent pipeline. Many of these professionals are from Bengaluru, Hyderabad, and Chennai — cities in southern India that have historically been poorly connected to Europe.

The route also opens up Zurich as a Schengen gateway. Passengers connecting through Zurich can reach virtually any European city without a second immigration check, making it a natural hub for NRIs who need to travel across the continent for work or leisure.

## The Broader Lufthansa Group Push Into India

Swiss's Bengaluru launch is part of a wider Lufthansa Group strategy to deepen its India footprint. The group's winter schedule also includes increased frequencies from Frankfurt to Hyderabad, along with Lufthansa's premium Allegris cabin product rolling out on several intercontinental routes.

The timing is notable. Indian carriers — particularly IndiGo and the Tata-owned Air India — have been aggressively expanding their own international networks, eating into market share that Gulf and European airlines once dominated. Lufthansa Group's response has been to compete on product quality and connectivity rather than price, betting that the Zurich hub's efficiency and the A350's cabin experience can justify premium fares.

Air India, for its part, is already planning to launch London Heathrow to Bengaluru service using the A350-900 from August 2026 — meaning Bengaluru will gain two major new European connections within weeks of each other.

## Practical Details

Schedules and fares have not been published yet, but Swiss's A350 configuration includes business, premium economy, and economy cabins. The airline has been rolling out its new "SWISS Senses" long-haul experience, which it plans to bring to the Bengaluru route.

For NRIs planning trips to Bengaluru or southern India this winter, the key window to watch is mid-August, when Swiss typically opens winter schedule bookings. Given pent-up demand and limited frequencies, early booking is advisable — five weekly flights on a single-aisle-equivalent capacity aircraft means seats will be scarce during peak December-January travel season."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bengaluru Just Overtook Mumbai as India's Second-Busiest Airport — and the Shift Is Not Temporary",
        "subheadline": "Kempegowda International Airport handled 3.18 million domestic passengers in April 2026, surpassing Mumbai's 2.89 million for the first time outside pandemic conditions — a milestone fuelled by tech-driven travel demand and infrastructure that Mumbai cannot match.",
        "slug": make_slug("bengaluru-overtakes-mumbai-second-busiest-airport-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the millions of NRIs with roots in Karnataka, Andhra Pradesh, Tamil Nadu, and Kerala, Bengaluru's rise as an aviation hub means better connections, more flight options, and lower fares when flying home — a structural improvement that could reshape how diaspora families plan India trips.",
        "tags": ["travel", "airports", "bengaluru", "mumbai", "india-aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/05/29/bengaluru-overtakes-this-airport-to-become-2nd-busiest-airport-in-india/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/bengaluru-airport-surpasses-mumbai-in-domestic-traffic/article69625125.ece"},
            {"name": "Network Thoughts", "url": "https://networkthoughts.com/2026/05/29/bengaluru-overtakes-mumbai-new-rankings-in-indian-aviation/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19528200/pexels-photo-19528200.jpeg",
        "body": """Bengaluru's Kempegowda International Airport has overtaken Mumbai's Chhatrapati Shivaji Maharaj International Airport in domestic passenger traffic for the first time under normal operating conditions, according to Airports Authority of India data for April 2026.

The numbers are unambiguous: Bengaluru handled 3.18 million domestic passengers in April, compared to Mumbai's 2.89 million. Delhi's Indira Gandhi International Airport remains India's busiest, with 4.93 million domestic passengers during the same period.

This is not a statistical anomaly. While Bengaluru briefly edged ahead during the pandemic — when city-specific lockdown rules distorted traffic — April 2026 marks the first time the overtaking has occurred in a fully open market. And the gap is widening for structural reasons that suggest Mumbai may not reclaim the position anytime soon.

## Mumbai's Traffic Is Splitting, Not Shrinking

The immediate trigger for Mumbai's decline is the opening of Navi Mumbai International Airport, which began commercial operations in December 2025. IndiGo and other carriers have shifted routes to the new airport — destinations like Ayodhya, Agra, Tirupati, and Jabalpur that were once served from Mumbai are now exclusively operated from Navi Mumbai.

In April, Navi Mumbai handled 524,000 passengers, a 2.3x increase over March. Combined, the two Mumbai airports still handle more traffic than Bengaluru. But at the individual airport level — which determines ranking, slot allocation, and airline investment decisions — Mumbai's flagship airport is losing ground.

The deeper problem is capacity. Mumbai operates on a single primary runway with severe congestion during peak hours. Expansion options are limited by the airport's urban location. Bengaluru, by contrast, has two parallel runways, two terminals, and room to grow.

## Why Bengaluru Is Growing

Bengaluru's rise mirrors the city's economic trajectory. India's technology capital generates enormous corporate travel demand — IT services alone employ millions of professionals who fly frequently between Bengaluru and Delhi, Mumbai, Hyderabad, and Chennai.

Airlines have responded by adding capacity aggressively. Air India Express has been consolidating its southern India operations at Bengaluru, shifting flights from Hyderabad and Chennai to use BLR as a hub. IndiGo, which controls roughly 62% of India's domestic market, has steadily increased its Bengaluru schedule.

International operations are growing even faster. Bengaluru's international passenger traffic surged 28.7% year-on-year in calendar year 2025, with daily international departures increasing from 38 to 51. The airport now serves 34 international destinations, including Dubai, Singapore, London, and — starting October 2026 — Zurich via Swiss Air Lines.

## What This Means for NRIs

For the large South Indian diaspora in the United States, the shift has practical implications. Bengaluru is the primary gateway for NRIs from Karnataka, and an increasingly viable option for those heading to Andhra Pradesh, Tamil Nadu, and Kerala.

More domestic traffic at BLR means more connecting flights. An NRI landing at Bengaluru from San Francisco or London now has significantly better onward options to Tier-2 cities like Mangalore, Hubli, Coimbatore, Vijayawada, and Thiruvananthapuram than even five years ago. The airline competition that comes with being a top-three airport also tends to push fares down — a welcome development for families booking expensive peak-season tickets.

For NRIs who have traditionally connected through Mumbai to reach southern India, the calculus is changing. Direct international flights to Bengaluru — from carriers including Air India, Emirates, Singapore Airlines, and soon Swiss — eliminate the need for the chaotic domestic connection at Mumbai's congested Terminal 2.

## The Road Ahead

Bengaluru's airport operator has outlined plans for Terminal 2 Phase 2 construction to handle rising demand, with a Terminal 3 and automated people mover in the long-term master plan. The airport handled 44.5 million total passengers in FY 2025-26, up 6.2% from the previous year.

Whether Bengaluru can close the gap with Delhi — which handles nearly 79 million passengers annually — remains to be seen. But the overtaking of Mumbai is a landmark that reflects something larger: India's economic and demographic centre of gravity is shifting south, and the aviation map is following."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Carriers Now Own More International Market Share Than Emirates — and NRIs Are the Reason",
        "subheadline": "IndiGo holds 17.6% of India's international aviation market while Emirates has fallen to 8.3%, a dramatic reversal driven by new routes, competitive pricing, and a diaspora that increasingly prefers flying Indian.",
        "slug": make_slug("indigo-air-india-international-market-share-gulf-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who once defaulted to Emirates or Qatar Airways for the Dubai/Doha connection now have viable direct options on Indian carriers — IndiGo's aggressive international expansion and Air India's Tata-led revival are reshaping how the diaspora flies home.",
        "tags": ["travel", "airlines", "indigo", "air-india", "emirates", "market-share"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indigo-and-air-india-surges-ahead-middle-eastern-carriers-decline/"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/articles/indigo-overtakes-air-india-in-international-market-97197"},
            {"name": "Fleet Wire", "url": "https://fleet-wire.com/2026/05/29/air-india-indigo-cut-flights-fuel/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17259764/pexels-photo-17259764.jpeg",
        "body": """For years, the default booking for an NRI flying from JFK to Hyderabad or SFO to Chennai was straightforward: Emirates via Dubai, Qatar Airways via Doha, or Etihad via Abu Dhabi. The Gulf carriers owned the India corridor, offering reliable connections, modern aircraft, and a mid-journey break that softened the 20-hour slog.

That era is ending. Recent market data shows IndiGo now commands approximately 17.6% of India's international aviation market — making it the single largest carrier for international flights in and out of the country. Emirates, once the undisputed king of the India corridor, has fallen to around 8.3%.

Air India, under the Tata Group since January 2022, has also been clawing back share. Together with Air India Express, the Tata aviation portfolio controls a significant chunk of international capacity. When you add IndiGo's numbers, Indian carriers collectively now handle more international passengers than any single Gulf airline.

## How the Shift Happened

Three forces converged to reshape the market.

**Route expansion.** IndiGo has been adding international destinations at a pace that would have seemed implausible five years ago, when it was purely a domestic low-cost carrier flying Airbus narrowbodies. The airline now operates to Istanbul, Central Asia, Southeast Asia, and the Middle East, and many of its newer routes are monopolistic or duopolistic — meaning IndiGo is the only carrier, or one of two, on those sectors.

**Air India's revival.** The Tata acquisition brought fleet renewal, new routes, and a credible premium product for the first time in decades. Air India has added Mumbai-Tokyo, Delhi-Rome, and is launching London-Bengaluru this August. The airline's interline agreement with Alaska Airlines gives it reach into 32 US destinations — a direct play for NRI traffic.

**Gulf carrier constraints.** Emirates and Qatar Airways face their own challenges. Airspace restrictions related to the Iran conflict have forced rerouting on some sectors, adding flight time and cost. The Gulf hub model — which requires passengers to connect through Dubai or Doha — also faces competition from nonstop routes that Indian carriers are increasingly able to offer as they acquire wide-body aircraft.

## What NRIs Actually Experience

The market share numbers matter because they translate into real differences at the booking stage.

**More direct options.** Air India now flies nonstop from San Francisco, Newark, JFK, Chicago, Washington, and other US cities to Delhi and Mumbai. IndiGo's international network feeds into these trunk routes via domestic connections. An NRI flying SFO-DEL-HYD on Air India can now do the entire journey on Indian carriers without touching a Gulf hub.

**Competitive pricing.** IndiGo's entry into international markets has forced fare discipline across the board. On sectors like Delhi-Dubai or Mumbai-Singapore, IndiGo's presence has pushed average fares down by an estimated 10-15%, benefiting all passengers regardless of which airline they ultimately choose.

**Cultural familiarity.** This is harder to quantify but repeatedly cited by frequent NRI travellers. Indian carriers serve Indian meals as standard, cabin crew speak Hindi and regional languages, and the boarding experience at Indian airports — while chaotic — is at least a familiar chaos.

## The Caveats

Indian carriers are not without problems. IndiGo reported a $280 million quarterly loss recently, driven by fuel costs and Pratt & Whitney engine issues that have grounded parts of its fleet. Air India and IndiGo are cutting roughly 250 domestic flights daily from June to manage rising operational costs.

On long-haul routes, Emirates and Qatar Airways still offer a meaningfully superior business-class product. For NRIs willing to pay for lie-flat seats and lounge access, the Gulf carriers remain hard to beat. Air India's cabin refurbishment is ongoing but incomplete — some aircraft still fly with interiors that date to the airline's pre-privatisation era.

And the Gulf hub model retains one advantage that Indian carriers cannot easily replicate: timing. Emirates operates multiple daily frequencies on the Dubai-India corridor, meaning NRIs can connect to virtually any Indian city at convenient hours. IndiGo's narrowbody fleet limits its range, and Air India's wide-body fleet is still smaller than what a true global carrier needs.

## The Trajectory Is Clear

Despite these caveats, the direction of travel is unmistakable. Indian carriers will continue gaining international market share as fleet deliveries accelerate, new routes launch, and the domestic network feeds more connecting passengers into international departures.

For the 4.5 million Indian-origin residents in the United States alone, this means more choices, better prices, and — eventually — a flying experience that matches or exceeds what the Gulf carriers offer. The days when Emirates owned the India corridor are not quite over. But the monopoly is broken, and it is not coming back."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
