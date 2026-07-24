#!/usr/bin/env python3
"""Travel writer — 3 articles for 2026-06-15 batch."""

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
# Article 1: US Summer Flight Chaos
# ─────────────────────────────────────────────

art1_body = """Summer 2026 is barely two weeks old, and America's airports are already buckling. Between June 12 and June 15, a succession of violent thunderstorms, tornado warnings, and oppressive heat has triggered more than 10,000 flight delays and over 2,000 cancellations across the United States — and the worst-hit hubs are the exact ones most NRIs depend on to get home.

## The Numbers Are Staggering

On June 12, severe storms raked the Midwest. Chicago O'Hare — the primary connecting hub for dozens of Air India, United, and American routes — saw more than 500 flights cancelled in a single evening as tornado watches extended across Illinois, Iowa, and Missouri. Nearly 390,000 homes lost power across the region.

The next day, disruptions spread east and south. Across the country, 236 flights were grounded and 795 delayed, with Dallas-Fort Worth, JFK, Boston Logan, and Newark all reporting cascading schedule failures. By June 15, Dallas alone clocked 940 delays and 182 cancellations — the worst single-airport day of the summer so far. American Airlines and its regional partners bore the heaviest load, but United, Delta, Air Canada, Qatar Airways, and Lufthansa all took hits.

International services to the UK, South Korea, Japan, Australia, and across Latin America were affected. For NRIs routing through Chicago, Dallas, or Newark on their way to Delhi, Mumbai, or Hyderabad, the ripple effects have been brutal.

## Why NRIs Are Disproportionately Exposed

Most India-bound flights from the US depart late evening and connect through one of three mega-hubs: O'Hare, DFW, or Newark. A cancelled afternoon domestic leg means a missed international connection — and in peak summer, rebooking onto the next available India flight can mean a 48-to-72-hour wait.

Add to that the fact that June through August is the single busiest corridor for NRI travel to India: wedding season, school holidays, family reunions, and monsoon homecomings all converge. Load factors on US–India routes routinely exceed 90 percent in summer. There is no slack in the system.

## What You Can Do Right Now

**Book direct where possible.** Air India's nonstops from SFO, JFK, Newark, and Washington Dulles eliminate the domestic-connection vulnerability entirely. United's Newark–Delhi and Newark–Mumbai nonstops serve the same purpose. Yes, they cost more. This summer, that premium is insurance.

**Avoid single-hub itineraries.** If you must connect, choose an airline that can reroute you through an alternate hub. United can swing you through San Francisco or Houston if Newark goes down. American has options through Charlotte or Miami if Dallas fails. A codeshare ticket on a single carrier gives you more rebooking leverage than a self-booked two-ticket itinerary.

**Monitor proactively.** Download FlightAware and set alerts for your specific flights 48 hours before departure. The FAA's real-time airport status page (fly.faa.gov) shows ground stops, delays, and weather holds before airlines update their apps.

**Know your rights.** Under the Department of Transportation's 2024 rules, airlines owe you a full cash refund — not a voucher — if they cancel your flight or delay it by more than three hours for domestic flights or six hours for international. If the disruption is within the airline's control, they must also cover meals and hotel stays.

**Get travel insurance that covers weather delays.** Most basic credit-card travel protections exclude "acts of God." A standalone policy from providers like Allianz or World Nomads typically covers weather-related delays above a six-hour threshold, including meals, accommodation, and rebooking costs.

## The Forecast Is Not Encouraging

The National Weather Service has flagged the entire June-through-September window for above-average storm activity across the central United States, elevated wildfire risk in the West, and a stronger-than-usual Atlantic hurricane season. Florida, Texas, and California — three states NRIs transit through constantly — are all under summer weather warnings.

None of this means you should cancel your India trip. But it does mean building a buffer into your itinerary, carrying essentials in your cabin bag, and treating every connection through a weather-vulnerable hub as a point of failure worth planning around."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "America's Airports Are Melting Down — and NRIs Flying Home Are Caught in the Middle",
    "subheadline": "More than 10,000 delays and 2,000 cancellations in four days. Here's how to protect your summer India trip.",
    "slug": make_slug("us-summer-flight-chaos-nri-india-travel-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Peak NRI summer travel to India coincides with the worst US airport disruptions in years, hitting the exact hubs — O'Hare, DFW, Newark — that most India-bound passengers connect through.",
    "tags": ["travel", "flights", "airports", "weather", "nri-guide", "summer-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/t9m527bwv1su/"},
        {"name": "Travel And Tour World — Chicago Disruptions", "url": "https://www.travelandtourworld.com/news/article/c3ar16oxywc7/"},
        {"name": "FlightAware", "url": "https://www.flightaware.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Airport departure board showing flight information at an international terminal",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# Article 2: Tirupati Luxury Pilgrimage Hotel
# ─────────────────────────────────────────────

art2_body = """For decades, visiting Tirupati meant accepting a tradeoff. The darshan at Tirumala Venkateswara Temple — one of the richest and most visited religious sites on the planet — was transcendent. The accommodation options within reach of it were, to put it gently, not.

That equation just changed. Royal Orchid Hotels, through its subsidiary Regenta Hotels, has opened Regenta Devarayah Tirupati, a 56-room four-star property positioned as the closest branded upscale hotel to the temple complex. For the millions of NRIs who make the Tirupati pilgrimage a cornerstone of their India visits, this is the kind of infrastructure upgrade that has been years overdue.

## What You Get

The hotel sits on DBR Hospital Road in Kothapalli, roughly two kilometres from Tirupati Railway Station and 15 kilometres from the recently upgraded Tirupati International Airport. From the upper floors and rooftop, guests look out at the Seshachalam Hills — the sacred seven hills that cradle the Tirumala temple above.

Rooms come in four tiers: Deluxe, Club, Suite, and two Presidential Suites at the top. All feature high-speed Wi-Fi, air conditioning, ergonomic workstations, and the kind of bedding you'd expect from a property competing with Marriott Courtyards and Lemon Tree Premiers already in the market. The difference is positioning: Regenta Devarayah is explicitly designed around the pilgrim's schedule, not just the business traveller's.

The rooftop infinity pool — with its panoramic hill views — is the signature amenity. A sixth-floor spa, a fitness centre, and banquet facilities for up to 200 guests round out the offering. The all-day restaurant, Pinxx, leans heavily into vegetarian cuisine, with South Indian staples alongside North Indian and selected international options.

## The Solar Story

Here's the detail that elevates this from a standard hotel opening. Regenta Devarayah runs on 80 percent solar power, using a 220 kW vertical solar installation. The hotel claims it is the first property in Andhra Pradesh and only the ninth in India to adopt this technology. For a pilgrimage destination that processes tens of millions of visitors annually, the sustainability angle matters — and it signals where India's hospitality industry is heading.

## Why NRIs Should Care

Tirupati is not a discretionary destination for many Indian American families. It is a duty, a tradition, a promise kept across generations. The Telugu diaspora in the United States — concentrated in the Bay Area, Dallas-Fort Worth, New Jersey, and the greater DC area — numbers well over a million. Add Tamil, Kannada, and other South Indian communities for whom Tirupati is a central pilgrimage, and you're looking at one of the largest faith-based travel flows between the US and India.

Yet hotel quality has historically lagged far behind the spiritual significance of the destination. Families flying 20 hours from Newark or San Francisco, often with elderly parents and young children, have had to choose between generic business hotels in the city centre and basic dharamshalas closer to the temple. A four-star branded option with a travel desk offering guided temple tours, EV charging for rental cars, and rooms designed for post-darshan recovery fills a genuine gap.

Regenta Devarayah is now accepting reservations. Rates have not been publicly listed at launch, but Regenta's other four-star properties in India typically range between ₹5,000 and ₹9,000 per night — roughly $60 to $110 — making it competitive with the Courtyard by Marriott Tirupati and the Fortune Select Grand Ridge already in the market."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Tirupati Finally Gets the Luxury Pilgrimage Hotel It Deserves",
    "subheadline": "Regenta Devarayah opens with a rooftop infinity pool, 80% solar power, and the closest branded hotel to Tirumala temple.",
    "slug": make_slug("tirupati-regenta-devarayah-luxury-pilgrimage-hotel-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Over a million Telugu Americans make the Tirupati pilgrimage regularly — this is the first branded upscale hotel close enough to the temple to change the trip experience.",
    "tags": ["travel", "tirupati", "pilgrimage", "hotels", "south-india", "spiritual-tourism"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/zdl8rlvq2ppl/"},
        {"name": "Today's Traveller", "url": "https://todaystraveller.net/rohl-launches-regenta-devarayah-tirupati-for-spiritual-tourism-56-key/"},
        {"name": "Royal Orchid Hotels", "url": "https://www.royalorchidhotels.com"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Tirumala_090615.jpg/1280px-Tirumala_090615.jpg",
    "image_caption": "Tirumala Venkateswara Temple complex in the Seshachalam Hills, Andhra Pradesh",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────
# Article 3: South Africa ETA for Indians
# ─────────────────────────────────────────────

art3_body = """South Africa just made it significantly easier for Indian passport holders to visit — and for NRIs who have been eyeing Cape Town safaris, Kruger National Park, and the Garden Route, the timing could not be better.

The country has expanded Phase 2 of its Electronic Travel Authorisation (ETA) system to include India, alongside China, Indonesia, and Mexico. The new digital process replaces much of the paperwork and waiting that previously made South Africa one of the more cumbersome visa applications for Indian travellers. Approvals are faster, the process is online, and the authorization arrives as a QR code you present at immigration.

## How the ETA Works

The system is straightforward. Eligible Indian passport holders apply online before departure, submit required documentation digitally, and receive an electronic authorization linked to a QR code. On arrival at OR Tambo International Airport in Johannesburg, Cape Town International, or Lanseria International, travellers present the QR code at immigration for expedited processing.

The ETA allows multiple entries and stays of up to 90 days — far more flexibility than the previous single-entry visa arrangement that required weeks of processing through VFS Global centres. For travellers combining South Africa with neighbouring Botswana, Namibia, or Mozambique, the multiple-entry provision is particularly useful.

Authorities have also noted that the traditional eVisa portal occasionally experiences downtime during system upgrades, making the ETA the more reliable application pathway going forward.

## Why South Africa, Why Now

South Africa has been on the radar of Indian travellers for years, but visa friction kept it behind Southeast Asia and Europe as a holiday destination. The country offers a remarkable range for a single trip: wildlife safaris in Kruger and private game reserves, the cosmopolitan food and design scene of Cape Town, the Winelands of Stellenbosch and Franschhoek, and the dramatic coastline of the Western Cape.

For NRIs based in the US, there is an additional draw. South Africa sits in a time zone that splits the difference between American and Indian hours — making it a natural meeting point for multi-generational family reunions where one branch flies from New Jersey and another from Hyderabad. The country's well-developed tourism infrastructure, English as a primary language, and favourable exchange rate (the rand trades at roughly 18 to the dollar) make it considerably more accessible than many assume.

The Indian outbound travel market to Africa has been growing steadily. South African Tourism has actively courted Indian visitors, and the ETA expansion is the policy follow-through on that marketing effort.

## What NRIs Should Know Before Booking

**Passport validity matters.** Your Indian passport must be valid for at least 30 days beyond your intended departure from South Africa, with at least two blank pages for entry stamps.

**The ETA is not instant.** While faster than the traditional visa, processing can still take several business days. Apply at least two to three weeks before your travel date to avoid last-minute complications.

**Yellow fever vaccination may be required.** If you are transiting through or arriving from a yellow fever endemic country — which includes some common stopover points like Kenya, Ethiopia, and Nigeria — you will need proof of vaccination. This catches many Indian travellers off guard, particularly those routing through Addis Ababa on Ethiopian Airlines, one of the most popular carriers on the India–South Africa corridor.

**US visa holders get a separate perk.** Indian citizens with a valid US visa or green card were already eligible for a 90-day visa exemption when visiting South Africa for tourism. The ETA streamlines this further, but the underlying eligibility for US visa holders remains independently useful if the ETA system is temporarily unavailable.

**Peak season is reversed.** South Africa's summer runs from November to February, which is India's winter and a popular time for NRI travel. The safari high season (June to October) coincides with the dry season, when animals congregate around water sources and visibility is best. Right now — mid-June — is actually an excellent time to be there.

The ETA expansion removes one of the last meaningful barriers between India's growing outbound travel market and one of Africa's most compelling destinations. For NRIs who have done Thailand, Bali, and the Mediterranean, South Africa offers something fundamentally different — and now, getting in is no longer the hard part."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "South Africa Just Made It Much Easier for Indians to Visit — Here's What Changed",
    "subheadline": "A new electronic travel authorisation replaces the old visa slog with a QR code and faster processing. Multiple entries, 90-day stays.",
    "slug": make_slug("south-africa-eta-india-visa-safari-travel-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "South Africa's new ETA system removes the visa friction that kept it behind Southeast Asia for Indian travellers — and NRIs with US visas get an extra edge.",
    "tags": ["travel", "south-africa", "visa", "safari", "cape-town", "nri-guide"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/c3ar16oxywc7/"},
        {"name": "South African Department of Home Affairs", "url": "https://www.dha.gov.za"},
        {"name": "South African Tourism", "url": "https://www.southafrica.net"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Camps_bay_%2853460319478%29_%28cropped%29.jpg/1280px-Camps_bay_%2853460319478%29_%28cropped%29.jpg",
    "image_caption": "Camps Bay beach and the Twelve Apostles mountain range in Cape Town, South Africa",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
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
