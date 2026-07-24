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
        "headline": "Ayodhya's Largest Resort Opens Walking Distance from Ram Mandir — and NRIs Are the Target Guest",
        "subheadline": "Evoke Rambagh brings 156 cottages, satvik dining, and Ayurvedic wellness to a city that until recently had almost nowhere decent to stay.",
        "slug": make_slug("evoke-rambagh-ayodhya-resort-ram-mandir-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs planning darshan trips to Ram Mandir now have a premium resort option with 156 cottages, wellness facilities, and destination wedding infrastructure — eliminating the accommodation bottleneck that has kept many diaspora families from making the trip.",
        "tags": ["travel", "ayodhya", "ram-mandir", "hotels", "pilgrimage", "india-tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Safari India", "url": "https://safariindia.com/evoke-unveils-rambagh-ayodhya-near-ram-mandir/"},
            {"name": "HospeMag", "url": "https://hospemag.me/evoke-rambagh-ayodhya-opens/"},
            {"name": "NomadLawyer", "url": "https://nomadlawyer.org/evoke-experiences-opens-156-cottage-resort-near-ayodhya-ram-mandir/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Shri_Ram_Janambhoomi_Mandir%2C_Ayodhya_Dham.jpg",
        "image_caption": "The Ram Janmabhoomi Mandir in Ayodhya, now flanked by premium hospitality developments",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Ayodhya has been a pilgrimage destination for centuries. A comfortable place to sleep there, however, has been a far more recent development. Evoke Experiences, the hospitality arm of Eyak Ventures, has opened Evoke Rambagh — a 25-acre, 156-cottage resort on Parikrama Marg, within walking distance of the Ram Janmabhoomi Mandir. It is, by any measure, the city's largest organized accommodation property, and its timing is not accidental.

## A City That Outgrew Its Hotels

Since the Ram Mandir's consecration in January 2024, Ayodhya has experienced a visitor surge that its hospitality infrastructure was never designed to handle. Pilgrim numbers have climbed from a few thousand daily to tens of thousands, and the city's existing stock of dharamshalas, guesthouses, and budget hotels has been overwhelmed during peak seasons. For NRI families accustomed to organized travel — families who can afford the ₹1.5 lakh round-trip airfare from the US but struggle to find a clean room with air conditioning in Ayodhya — the accommodation gap has been a genuine deterrent.

Evoke Rambagh is pitched squarely at this gap. The property's 156 cottages are spread across landscaped grounds with multiple water bodies, designed to feel more leisure resort than pilgrim hostel. The positioning is deliberate: close enough to walk to the temple, far enough to decompress after darshan.

## What the Property Offers

The resort's facilities reflect a bet on the convergence of pilgrimage and premium leisure travel. Dining is entirely vegetarian, anchored by a satvik cuisine restaurant alongside Indian, Oriental, and Continental options — a nod to the religious sensibilities of the primary visitor base without restricting it to austerity. A lobby restaurant and in-room dining round out the food options.

Wellness facilities include a swimming pool, yoga sessions, meditation programs, and naturopathy-based activities. For NRIs who pair temple visits with broader wellness-oriented travel — a growing segment — these are practical draws rather than luxury additions.

The property also includes a banquet hall, landscaped gardens, a clubhouse, and dedicated event spaces. Ayodhya is emerging as a destination wedding market, and Evoke is positioning itself to capture that demand, with capacity for 500-plus guests.

Operational details suggest the resort is targeting the well-organized NRI visitor: concierge assistance, valet parking, golf cart transportation within the property, multilingual support, and wheelchair accessibility. It is accessible via both Ayodhya Junction railway station and Maharishi Valmiki International Airport, the relatively new airport that has dramatically improved the city's air connectivity.

## Why NRIs Should Pay Attention

The Ayodhya accommodation landscape is changing quickly. Ramada by Wyndham has signed a 70-room property in nearby Faizabad, expected to open by mid-2026. Summit Hotels recently announced The Mandir Collection, a new brand focused on pilgrimage destinations, with its first property also in Rajasthan's spiritual circuit. ITC, Taj, and Lemon Tree have all signaled interest in the region.

For the roughly 4.5 million Indian Americans in the United States, Ayodhya sits in a category of destinations that are emotionally essential but logistically difficult. The temple itself now rivals Varanasi and Tirupati in symbolic importance. But unlike those cities, which have decades of hospitality infrastructure, Ayodhya is building its hotel stock in real time.

Evoke Rambagh matters because it signals that the build-out is reaching a quality threshold that organized NRI travelers expect. A family flying SFO-DEL-Ayodhya for a long weekend of darshan no longer needs to reconcile spiritual aspiration with accommodation anxiety.

## The Broader Picture

India's spiritual tourism economy is projected to reach $135 billion by 2034, according to Summit Hotels CEO Sumit Mitruka. The sector's growth is being driven by infrastructure improvements — airports, highways, dedicated train services like the Vande Bharat — that make previously remote pilgrimage sites accessible within a day's journey from major metros.

Ayodhya is the sharpest example of this convergence. A city that had one functioning airport and limited rail connectivity five years ago now has an international airport, expanded rail service, and an emerging hospitality sector targeting premium travelers.

For NRIs planning a Ram Mandir visit, the practical advice is straightforward: the accommodation problem is being solved, but demand still outstrips supply during peak periods like Navratri, Diwali, and Ram Navami. Book early, and expect pricing to reflect the premium positioning that properties like Evoke Rambagh represent."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Amtrak Will Take You Through 12 National Parks in 25 Days for $8,000 — Here's Why NRI Families Should Consider It",
        "subheadline": "The Grand National Parks of America itinerary covers Yellowstone, Yosemite, Grand Canyon, and nine more parks by rail — with hotels, car rentals, and guided tours included.",
        "slug": make_slug("amtrak-grand-national-parks-25-day-trip-nri-families"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRI families who have lived in the US for years but never explored beyond coastal metros, Amtrak's 25-day national parks itinerary offers a structured, no-driving-stress way to see the country — at roughly $300 per day all-in, competitive with self-planned road trips once hotels and car rentals are factored in.",
        "tags": ["travel", "usa", "national-parks", "amtrak", "road-trip", "family-travel"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Travel", "url": "https://www.thetravel.com/amtrak-grand-national-parks-america-trip-cost/"},
            {"name": "Amtrak Vacations", "url": "https://amtrakvacations.co.uk/trips/grand-national-parks-of-america/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5164440/pexels-photo-5164440.jpeg",
        "image_caption": "Yosemite Valley, one of 12 national parks on Amtrak's Grand National Parks of America itinerary",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """There is a particular species of NRI travel regret that surfaces at dinner parties across the Bay Area, the tri-state area, and the Dallas-Fort Worth sprawl: the realization that after a decade or more of living in the United States, you have seen Delhi, Mumbai, Goa, and Bali more recently than Yellowstone or the Grand Canyon. The flights to India get booked. The national parks do not.

Amtrak's Grand National Parks of America itinerary is designed, perhaps inadvertently, for exactly this demographic. A 25-day, pre-packaged train journey through 12 of the country's most celebrated parks, it eliminates the two things that most reliably kill NRI domestic travel plans: the need to drive hundreds of miles between remote destinations, and the logistical burden of booking hotels, car rentals, and park tours across multiple states.

## What $8,000 Buys You

The headline price of $7,929 per person covers 26 days of travel, 20 hotel nights and five nights onboard Amtrak, six meals, a nine-day mid-size car rental, guided sightseeing tours at all 12 parks, and several city-specific perks — a boat cruise on Glacier National Park's Two Medicine Lake, a hop-on-hop-off bus tour of Los Angeles, admission to Chicago's Skydeck, a ride on the historic Grand Canyon Railway, and a trip up Seattle's Space Needle.

The parks themselves span the greatest hits of American landscape: Rocky Mountain, Arches, Canyonlands, Zion, Bryce Canyon, Capitol Reef, Grand Teton, Yellowstone, Yosemite, Grand Canyon, Glacier, and Mount Rainier. The itinerary threads them together using four major Amtrak routes — the California Zephyr, Coast Starlight, Southwest Chief, and Empire Builder — with overnight train rides replacing red-eye flights and long highway stretches.

## The NRI Calculus

For a family of four, the math looks steep at first: roughly $32,000 before optional upgrades to private sleeper compartments. But the comparison point is not a week in Cancun. It is the self-planned alternative: renting an SUV, booking 20 hotel nights across remote Western states during peak summer, purchasing park passes, arranging guided tours, and navigating the logistics of covering Denver to San Francisco to Los Angeles to Chicago to Seattle — with children — over 25 days.

Done independently, that trip would cost a comparable amount, take weeks of planning, and require someone to drive thousands of miles through unfamiliar mountain roads. Amtrak handles the logistics; you handle the camera.

The train itself is part of the value proposition. The California Zephyr's route through the Colorado Rockies and Sierra Nevada is regularly cited as one of the most scenic rail journeys in the world. Amtrak's observation cars — with panoramic windows and no assigned seating — offer views that no highway windshield can match. For families with children old enough to appreciate landscape but young enough to get restless in a car seat, the freedom to walk between carriages, eat in a dining car, and watch the scenery change from desert to mountain to coastline is a genuine upgrade over road-tripping.

## What to Know Before Booking

Amtrak trains in the US are not European rail. They share tracks with freight trains, which have priority, and delays are common. The itinerary builds in buffer time, but travelers should approach the schedule with flexibility rather than precision. Multiple travelers on Reddit have described delays of several hours on cross-country routes.

Accommodation onboard ranges from standard coach seats to private Roomettes (compact two-berth compartments with a window) and Bedrooms (larger compartments with a private toilet and shower). The upgrade cost varies by route and season but can add $1,000-$3,000 to the total fare. For overnight legs, the upgrade is worth serious consideration — sleeping upright in coach for five nights is an experience best left to college backpackers.

The itinerary runs during summer months, which means peak season at the parks. Crowds at Yellowstone, Yosemite, and the Grand Canyon will be substantial. The guided tours help navigate this — guides know the timing and access points that avoid the worst congestion.

## The Case for Going

Indian American families tend to travel internationally with enthusiasm and domestically with reluctance. The US national parks system — 63 parks spanning every major American biome — is arguably the country's single greatest cultural asset, and it costs almost nothing to enter compared to international travel. An America the Beautiful pass covers all 63 parks for $80 per vehicle per year.

Amtrak's package removes the planning friction that keeps NRI families defaulting to another Cancun trip or another Christmas in India. It is not cheap, but it is comprehensive, scenic, and — critically — it does not require anyone to drive through Utah in July.

The journey starts in Denver and ends in Seattle. Book through Amtrak Vacations. Summer 2026 departures are filling up."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bihar Is Building Five Airports at Once — and the State's Massive US Diaspora Stands to Benefit",
        "subheadline": "Muzaffarpur, Saharsa, Munger, Valmikinagar, and a Patna expansion are all under way, transforming a state that NRIs have long found difficult to reach.",
        "slug": make_slug("bihar-five-new-airports-nri-diaspora-connectivity"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bihar's US diaspora — concentrated in the Midwest and Northeast — has long faced a grueling multi-leg journey home via Delhi or Kolkata. Five simultaneous airport projects will dramatically reduce last-mile travel times to cities like Muzaffarpur, Saharsa, and Munger, making trips home more practical for NRI families.",
        "tags": ["travel", "bihar", "airports", "india-infrastructure", "aviation", "nri-connectivity"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Patna Press", "url": "https://patnapress.com/five-new-airports-faster-travel-and-cheaper-flights-bihars-big-aviation-plan-explained/"},
            {"name": "ScanX Trade", "url": "https://scanx.trade/india-adding-new-airports-every-50-days/"},
            {"name": "Urban Acres", "url": "https://urbanacres.in/kolkata-airport-pushes-passenger-capacity-upgrade/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Patna_Airport_JNPI_New_Terminal.jpg",
        "image_caption": "The new terminal at Jay Prakash Narayan International Airport in Patna, Bihar's aviation gateway",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Getting to Bihar from the United States has always been an exercise in patience. The typical journey — SFO or JFK to Delhi, Delhi to Patna, then a four-to-seven-hour drive to wherever your family actually lives — can stretch past 30 hours door to door. For NRIs from Muzaffarpur, Darbhanga, or the Kosi belt, the last leg is often the worst: overnight buses, unreliable trains, and roads that test both vehicle and vertebrae.

Five airport projects are now under way simultaneously across Bihar, representing the most concentrated push to improve air connectivity the state has ever seen. Taken together, they promise to shorten the homeward journey for a diaspora that has long been underserved by India's aviation infrastructure.

## The Five Projects

**Muzaffarpur Airport** is receiving the most substantial upgrade. The Airports Authority of India has allocated ₹72 crore for runway and airside infrastructure, with an 11-month completion deadline. The upgraded airport will serve not just Muzaffarpur city but the broader litchi belt — Sitamarhi, Sheohar, East Champaran, Vaishali, and Samastipur. For NRIs from these districts, it eliminates the three-to-four-hour drive from Patna that currently bookends every trip home.

**Saharsa Airport** is a new build. AAI issued the construction tender in April 2026, with Phase 1 estimated at ₹35.14 crore. Technical bids open on June 16, and the contractor will have 15 months to deliver. The airport will serve nearly two million residents of the Kosi and Seemanchal regions — Saharsa, Madhepura, and Supaul districts — an area that has historically been among the most isolated in northern India. The airport will also function as a critical logistics node during the annual Kosi flood season, when road connectivity is routinely severed.

**Munger Airport** (Safiabad) is being upgraded for night landing capability. The existing runway — 758 metres long and 25 metres wide — will be expanded to at least 1,200 metres by 70 metres, sufficient for 19-seater regional aircraft under the UDAN scheme. Chief Minister Samrat Choudhary has directed officials to develop it into a modern facility. The district administration has proposed acquiring an additional 20 acres, with an estimated investment of ₹300 crore.

**Valmikinagar Airport** in West Champaran is the most architecturally distinctive of the lot: a tiger-themed terminal inspired by the adjacent Valmiki Tiger Reserve. It is being developed as both a tourism gateway and a strategic connectivity asset in a border district.

**Patna Airport** (Jay Prakash Narayan International) is the anchor of the entire system. Already Bihar's only airport with international connectivity — Air India Express flies to Dubai and Sharjah — Patna is undergoing terminal modernization and capacity expansion to handle the increased feeder traffic that the new regional airports will generate.

## Why This Matters to the Diaspora

Bihar has one of the largest diaspora populations of any Indian state. Bihari Americans are concentrated in metropolitan areas across the US — Chicago, New Jersey, Houston, the Bay Area — and their connection to home remains strong. Weddings, Chhath Puja, family emergencies, and property matters generate a steady stream of return visits.

But the logistics of getting beyond Patna have been a persistent friction. Darbhanga Airport, which began commercial operations in 2020, demonstrated the demand: flights to Delhi and Mumbai filled quickly, and the airport now handles several daily departures. Muzaffarpur, Saharsa, and Munger represent the next tier of cities where demand exists but infrastructure does not — yet.

The UDAN regional connectivity scheme is the policy mechanism making these smaller airports viable. By offering subsidized fares and viability gap funding to airlines, UDAN has enabled commercial service to airports that would otherwise be uneconomical. The model has already connected cities like Darbhanga, Deoghar, and Dumka in the broader region.

## The Connectivity Math

Consider the current journey for an NRI from Saharsa. Today: fly into Delhi (15-17 hours from the US), connect to Patna (2 hours), then drive or take a train to Saharsa (5-7 hours depending on road conditions and season). Total transit time: 24 to 30 hours.

With Saharsa Airport operational: fly into Delhi, connect via a UDAN flight to Saharsa (roughly 90 minutes). Total transit time: 18 to 20 hours. The savings are not dramatic in absolute terms, but the elimination of the ground leg — which is invariably the most exhausting, unpredictable, and uncomfortable portion — changes the calculus of whether to make the trip at all.

For elderly parents traveling in the opposite direction — Bihar to the US to visit children — the improvement is even more significant. A five-hour car ride to Patna can be a serious health consideration for older travelers.

## What Remains to Be Seen

Airport construction in India has a mixed track record on timelines. The 11-month deadline for Muzaffarpur is ambitious; the 15-month window for Saharsa even more so. Land acquisition for Munger's expansion has not yet been completed. And operational airports need airlines willing to fly there — something that depends on sustained passenger demand and the continuation of UDAN subsidies.

But the direction is unmistakable. Bihar's aviation map is being redrawn, and the beneficiaries include not just the state's residents but the millions of Biharis abroad who have long accepted a punishing journey home as the price of diaspora life. That price is about to drop."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
