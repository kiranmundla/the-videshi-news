#!/usr/bin/env python3
"""Travel writer: 2-3 fresh travel articles for The Videshi (2026-06-29 19:00 PT run)."""

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
    # ─── Article 1: Air India Express eyes Georgia / Europe ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Express Is Plotting Its First European Route — and Georgia Is the Target",
        "subheadline": "The Tata-owned budget carrier is evaluating nonstop flights to Tbilisi for the winter schedule, part of a broader push that has already taken it past the 100-aircraft mark and into 4-star Skytrax territory.",
        "slug": make_slug("air-india-express-georgia-europe-budget-carrier-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "A low-cost nonstop to Georgia opens a visa-free European gateway for Indian passport holders with a US visa — and could pressure fares on competing Gulf-hub routings that NRIs currently depend on.",
        "tags": ["travel", "airlines", "air-india-express", "georgia", "europe", "budget-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-express-eyes-europe-expansion-plans-georgia-entry/article71162011.ece"},
            {"name": "AeroRoutes", "url": "https://aeroroutes.com"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/VT-BXY_Air_India_Express.jpg/1280px-VT-BXY_Air_India_Express.jpg",
        "image_caption": "An Air India Express Boeing 737 in the carrier's current livery",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India Express has never flown to Europe. That is about to change.

The Tata Group's budget arm is actively evaluating nonstop services to Georgia — specifically Tbilisi — for the upcoming winter schedule, according to sources cited by *The Hindu BusinessLine*. If the route launches, it would mark the carrier's first foray into Europe and a significant expansion of India's low-cost international network.

## From Kochi upstart to 100-aircraft carrier

The ambition is not a one-off bet. Air India Express recently crossed the 100-aircraft milestone, with nearly two-thirds of its fleet now comprising new-generation Boeing 737 MAX 8 jets. Since the Tata Group took over in 2022, the airline has nearly doubled its capacity, tripled its market share, and secured a 4-star Skytrax rating in its first-ever audit — a transformation that has repositioned what was once a small Kochi-based operator into a pan-India and international carrier with 43 domestic and 16 international destinations.

The airline currently serves 13 destinations across the Gulf and has restored roughly 80 per cent of its West Asia network following disruptions caused by regional geopolitical tensions earlier this year. Southeast Asia is the other growth vector: Bangkok and Phuket already feature on its route map, and sources say it is now evaluating entry into Malaysia.

At home, at least five new domestic stations are expected before the end of 2026.

## Why Georgia, and why it matters for NRIs

Georgia is not an obvious choice for a budget airline, but the economics make more sense than they first appear. Tbilisi is roughly six hours from Delhi — well within the 737 MAX's range — and Georgia offers visa-free or visa-on-arrival entry for Indian passport holders who carry a valid US, Canadian, or Schengen visa. For NRIs shuttling between the US and India, that makes it a cheap, painless stopover in the Caucasus without the bureaucratic overhead of a Schengen application.

The country has also become a quiet favourite among Indian travellers. Georgia's tourism board reported a sharp increase in Indian visitor numbers over the past two years, driven partly by its wine country, Orthodox monasteries, and the snow-capped Greater Caucasus — all at a fraction of Western European prices. A budget nonstop from India would turbocharge that trend.

For IndiGo, which launched Athens nonstops from Delhi and Mumbai earlier this year using its new A321XLR fleet, an Air India Express entry into Eastern Europe would signal that India's low-cost carriers are now competing not just in the Gulf and Southeast Asia, but on the continent's fringes — territory long dominated by Gulf network carriers offering sixth-freedom connections through Dubai and Doha.

## The bigger picture: a value carrier, not just a budget airline

Air India Express is positioning itself as something that sits between a traditional low-cost carrier and a full-service airline — a "value carrier," in the language of its strategy documents. The 4-star Skytrax rating is part of that pitch. So is the fleet composition: the 737 MAX 8 offers better fuel economics and a longer range than its predecessor, enabling routes that were previously uneconomical for a budget operator.

The airline has outlined plans to reach a 25 per cent domestic market share by FY31, supported by a fleet of 300 aircraft — a threefold expansion from where it stands today. International network growth, particularly into underserved short-to-medium-haul markets, is central to that ambition.

For NRIs, the practical upshot is more direct, affordable options on routes that currently require either a full-service ticket or an awkward connection through a Gulf hub. If Georgia works, the template — visa-friendly, mid-range distance, underserved by Indian carriers — could easily extend to other destinations in Eastern Europe, the Balkans, or Central Asia.

The winter schedule, when these routes would launch, typically begins in late October. Air India Express has not officially confirmed the Georgia plan, and the airline did not respond to queries from *BusinessLine*. But with the fleet, the range, and the ratings now in place, the question is less *whether* it will enter Europe than *which route comes first*."""
    },

    # ─── Article 2: Air India first class to Melbourne ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Brings First Class to Melbourne Starting July 1 — Using Borrowed Etihad Suites",
        "subheadline": "The Delhi-Melbourne route swaps its Boeing 787 for a three-class 777 with eight enclosed first-class suites, making it the first time Air India has offered a premium-tier cabin on the India-Australia corridor.",
        "slug": make_slug("air-india-first-class-melbourne-etihad-suites-july"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "Australia's Indian-origin population has topped one million, with Melbourne's Victorian corridor among the fastest-growing — first class on a nonstop from Delhi gives high-yield diaspora travellers an option that previously required routing through Singapore or the Gulf.",
        "tags": ["travel", "airlines", "air-india", "australia", "melbourne", "first-class", "boeing-777"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Executive Traveller", "url": "https://www.executivetraveller.com/air-india-brings-first-class-to-melbourne"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com"},
            {"name": "Fleet Wire", "url": "https://fleet-wire.com/air-india-adds-777-first-class-suites-on-melbourne-route/"},
            {"name": "AeroRoutes", "url": "https://aeroroutes.com"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG/1280px-Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG",
        "image_caption": "An Air India Boeing 777-300ER, the aircraft type now deployed on the Delhi-Melbourne route",
        "image_attribution": "Wikimedia Commons",
        "body": """Starting tomorrow, the daily Air India flight between Delhi and Melbourne will feel like a different airline.

The carrier is swapping its Boeing 787-8 Dreamliner — a capable but two-class workhorse — for a Boeing 777-300ER fitted with eight enclosed first-class suites, 40 lie-flat business seats, and a larger economy cabin. It is the first time Air India has offered first class on the India-Australia corridor, and the timing is not accidental.

## The suites: familiar, if you've flown Abu Dhabi

The 777 being deployed is one of six aircraft previously operated by Etihad Airways, leased by Air India in 2023 and purchased outright in 2025. The first-class product, therefore, is Etihad's Diamond First — suites framed by walls up to 1.6 metres high, with a sliding door for privacy and a seat that converts into a fully flat bed roughly two metres long. Each passenger gets direct aisle access, a large personal screen, and substantial storage.

It is not Air India's forthcoming next-generation first-class product (that will arrive with the A350-1000, which the airline has configured with a custom Airbus suite). But for a route that previously offered no first class at all, the leap is significant.

Behind the eight suites, 40 Pearl Business seats sit in a 1-2-1 layout — again, an Etihad inheritance. The product is older than what the market's best carriers now offer, but the 1-2-1 configuration guarantees direct aisle access for every passenger, a clear improvement over the 2-2-2 business layout on the departing 787.

Flight AI308 departs Delhi at 01:15 and arrives Melbourne at 17:55; AI309 returns at 19:35, landing in Delhi at 03:50 the next morning.

## Why Melbourne, and why now

Australia's Indian-born population has crossed one million, making it one of the largest diaspora communities in the Asia-Pacific. Victoria — and Melbourne specifically — has been the epicentre of that growth, fuelled by students, tech workers, and family reunification. The Delhi-Melbourne corridor has seen double-digit passenger growth in recent years, and Air India is the only carrier offering a nonstop service on it.

Deploying a bigger aircraft with a premium cabin is a capacity play and a revenue play simultaneously. The 777-300ER carries more passengers than the 787-8, so Air India adds seats without needing additional airport slots. And the first-class cabin targets high-yield traffic — business travellers, affluent leisure passengers, and members of the Indian diaspora willing to pay for a direct, comfortable flight rather than routing through Singapore, Kuala Lumpur, or the Gulf.

## Part of a broader July reset

The Melbourne upgrade is one piece of a larger fleet reshuffle taking effect this week. Mumbai-London Heathrow is moving to new and retrofitted Boeing 787-9s with all-new cabin interiors, replacing the older 777-300ER that previously served the route. Bengaluru-London Heathrow will introduce premium economy for the first time, again using retrofitted Dreamliners. Across its US network, over 50 per cent of flights now feature new or upgraded interiors.

Air India's CEO, Campbell Wilson, has described the transformation as a multi-year process built on "continuous improvement" — a phrase that would ring hollow at many airlines but is backed, in Air India's case, by measurable changes. The carrier's domestic on-time performance hit a record 90 per cent in June. Its Net Promoter Scores have climbed. And the opening of the Maharaja Lounge at San Francisco's international terminal in March — a 3,400-square-foot space with spice-inspired artwork and an Indian-focused dining programme — showed that the ground product is keeping pace with the inflight overhaul.

## The NRI calculus

For Indian Americans flying to Australia — whether visiting family, attending conferences, or connecting through Delhi on a broader itinerary — the calculus just shifted. A nonstop Delhi-Melbourne flight with enclosed first-class suites and a modern business cabin is no longer something you get only by routing through Emirates or Singapore Airlines. Air India now offers it directly, on a 12-hour sector, with Star Alliance connectivity at both ends.

The seats are already bookable on Air India's website. Given the route's traffic patterns and the limited number of first-class suites, early booking is advisable — particularly for the Melbourne-to-Delhi return, which tends to fill faster during the Australian winter break."""
    },

    # ─── Article 3: India's expressway revolution ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Expressway Boom Has Quietly Halved Your Road Trip — an NRI Summer Guide",
        "subheadline": "The Delhi-Dehradun drive now takes 2.5 hours instead of six. Delhi-Jaipur is under three and a half. If you haven't driven in India since your last pre-pandemic visit, the highway network has changed beneath you.",
        "slug": make_slug("india-expressway-road-trip-nri-summer-guide"),
        "category": "travel",
        "vertical": "infrastructure",
        "diaspora_angle": "NRIs visiting India this summer will find that once-punishing road trips to hill stations, heritage cities, and family hometowns are now dramatically faster thanks to new expressways opened in 2025-2026 — the driving experience has fundamentally changed.",
        "tags": ["travel", "india", "road-trip", "expressways", "infrastructure", "nri-guide"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "StayVista Journal", "url": "https://stayvista.com/journal/india-new-2026-expressways-road-trips"},
            {"name": "Press Information Bureau, Government of India", "url": "https://pib.gov.in"},
            {"name": "Wikipedia - Delhi Dehradun Expressway", "url": "https://en.wikipedia.org/wiki/Delhi%E2%80%93Dehradun_Expressway"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/India_highway_gurgaon.jpg/1280px-India_highway_gurgaon.jpg",
        "image_caption": "A modern divided highway near Gurgaon, part of India's expanding national expressway network",
        "image_attribution": "Wikimedia Commons",
        "body": """If your last road trip in India involved a white-knuckle crawl through single-lane towns and unmarked detours, you are operating on outdated intelligence. Over the past 18 months, India has opened a series of expressways that have cut driving times between major cities by 40 to 60 per cent. For NRIs visiting this summer, that changes the maths on what counts as a weekend getaway — and what is worth driving to instead of flying.

## The new map

Here is what has actually opened and is driveable today, stripped of the aspirational timelines that litter most Indian infrastructure coverage:

**Delhi to Dehradun: 2.5 hours.** The Delhi-Dehradun Expressway opened on April 14, 2026, slicing a miserable 5-6 hour slog through Meerut and Muzaffarnagar into a smooth 210-kilometre run. If your family has a place in Mussoorie or Rishikesh, this single road changes the trip from a gruelling day of travel into a morning drive. Dehradun is now closer in time to NCR than Jaipur was five years ago.

**Delhi to Jaipur: 3 to 3.5 hours.** The Delhi-Mumbai Expressway's Jaipur spur, open since mid-2025, has turned what was a five-to-six-hour ordeal into a fast, well-signed cruise. For NRI families doing the Golden Triangle circuit, this means Jaipur is genuinely a day trip from Delhi — not an overnight commitment.

**Mumbai to Nashik: about 3 hours.** The Samruddhi Mahamarg (Maharashtra's flagship expressway) reached full operational status in June 2025, connecting Mumbai to Nagpur across 701 kilometres. The Nashik stretch, roughly three hours from Mumbai, has turned Maharashtra's wine country and Trimbakeshwar temple into a feasible weekend escape.

**Bengaluru to Mysuru: 75 to 90 minutes.** This one opened in March 2023, but many NRIs who visit Bengaluru still do not know it exists. The 119-kilometre expressway has halved the drive to Mysore Palace, Chamundi Hills, and the Ranganathittu bird sanctuary. A Sunday drive, not a two-day excursion.

**Meerut to Prayagraj (Ganga Expressway, Phase 1): open.** At 594 kilometres, the Ganga Expressway is one of India's longest, cutting through the heart of Uttar Pradesh. Phase 1 is operational, and the full Delhi-to-Prayagraj drive — once an 11-hour marathon — is now closer to six or seven hours. For NRIs whose families are from UP's eastern belt, this is the road that makes an Allahabad visit practical without a flight.

## What this means in practice

The practical effect for NRI visitors is threefold.

First, **short domestic flights become optional.** A Delhi-Jaipur flight costs ₹4,000-8,000 one way, takes an hour in the air, and requires two hours of airport overhead on each end. The expressway drive costs a fraction in tolls and fuel, and the door-to-door time is comparable — particularly if you are staying outside the city centre.

Second, **family visits to smaller towns are far less painful.** The expressways do not just connect metros to metros. They pass through — or connect to upgraded national highways serving — tier-2 and tier-3 towns that are home to millions of NRI families. Getting from Delhi to a town in western UP that once required six hours of nerve-shredding NH traffic can now be done in three.

Third, **self-drive holidays become viable.** India's car rental market has matured considerably, with Zoomcar, Revv, and Avis all operating in major cities. An NRI comfortable driving in the US will find the new expressways — divided, well-lit, with electronic tolling — a world apart from the India highway experience of a decade ago. That said, exercise caution: expressway speeds are higher, wrong-way driving remains a hazard on some stretches, and the transition from expressway to state highway can be abrupt.

## What is not yet open

The Bengaluru-Chennai Expressway is partially driveable but not complete — the full 262-kilometre corridor is expected around mid-2026. The Delhi-Mumbai Expressway's full alignment is operational in sections but not yet a continuous drive from capital to capital. Do not plan either trip as a through-drive just yet.

## The bottom line

If you are an NRI planning a summer trip to India and debating whether to squeeze in a side trip to a hill station, a heritage city, or a relative's hometown, check the expressway map before you book a domestic flight. The road trip that used to be impractical may now be the better option — faster, cheaper, and considerably more scenic than the inside of another Airbus A320."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
