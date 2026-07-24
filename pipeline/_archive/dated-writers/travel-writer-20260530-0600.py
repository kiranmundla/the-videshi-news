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
        "headline": "India Finally Has a Cruise Route to Singapore — and It Starts at ₹12,994",
        "subheadline": "Cordelia Cruises returns to Chennai for its fifth season with sailings to Sri Lanka, Phuket, Langkawi, and Singapore — offering NRIs visiting South India a genuine alternative to flying this summer.",
        "slug": make_slug("cordelia-cruises-chennai-singapore-sri-lanka-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs visiting family in Tamil Nadu, Kerala, or Karnataka this summer, Cordelia's Chennai sailings offer a way to bolt on a multi-country vacation without booking separate flights. A 10-night Singapore cruise from Chennai costs less than a round-trip SFO-SIN economy ticket.",
        "tags": ["travel", "cruise", "india", "chennai", "singapore", "sri-lanka", "cordelia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/cordelia-cruises-to-call-on-chennai-for-5th-season-on-june-20/"},
            {"name": "India Outbound", "url": "https://www.indiaoutbound.info/cordelia-cruises-announces-voyages-to-sri-lanka-south-east-asia/"},
            {"name": "CruiseBay", "url": "https://www.cruisebay.com/cordelia-cruise-from-india"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/813036/pexels-photo-813036.jpeg",
        "body": """India's domestic cruise industry has spent years making promises about becoming "the next big thing." With Cordelia Cruises announcing its fifth consecutive season out of Chennai — launching June 20, running through August — the promises are starting to look like an actual business.

The Cordelia Empress will sail itineraries ranging from 2-night coastal getaways to a 10-night international voyage reaching Phuket, Langkawi, Kuala Lumpur, and Singapore. Fares start at ₹12,994 per person for a 2-night sailing — roughly $155 at current exchange rates.

## The Itineraries That Matter

The headline route is the **10-night Southeast Asia cruise departing July 18**: Chennai to Phuket, Langkawi, Kuala Lumpur, and Singapore. For context, a round-trip economy flight from Chennai to Singapore runs ₹25,000–40,000 depending on the carrier. The cruise hits four countries for a single boarding pass.

For families who want something shorter, the **5-night Sri Lanka circuit** departs August 10 and 17, covering Hambantota, Trincomalee, and Jaffna — three cities that are difficult to stitch together by land without burning vacation days on intercity buses.

The bread-and-butter offerings are **5-night domestic sailings** to Visakhapatnam and Puducherry (departing weekly from June 22 through July 13) and **2-night weekend cruises** that leave Chennai on Fridays and return Sunday mornings.

A **5-night westbound sailing on August 24** — Chennai to Kochi to Mumbai — is essentially a floating repositioning trip that doubles as a way to move between India's coasts without the hassle of domestic airport security lines.

## Why NRIs Should Care

If you are flying into Chennai this summer to visit family — and statistically, a significant share of the 4.5 million Indian Americans trace roots to Tamil Nadu, Kerala, and Karnataka — Cordelia's sailings let you tack on an international side trip without booking separate flights, hotels, or transfers.

The math is straightforward. A 5-night Mumbai-Goa-Lakshadweep cruise runs ₹32,485 per person including meals, entertainment, and accommodation. A comparable 5-night Goa hotel stay with meals and activities at a mid-range resort would run ₹8,000–12,000 per night, totaling ₹40,000–60,000 before flights.

The ship itself is no Maldives overwater villa — the Cordelia Empress is a repurposed 1992-built vessel with a central atrium, gaming arcade, rock climbing wall, and multiple dining venues. But it is the only game in town for Indian-flagged cruising, and the itineraries are genuinely useful for covering ground in a region where visa logistics and flight connections eat into vacation time.

## The Fine Print

A few caveats worth noting. The **3-night Sri Lanka cruise** (August 7, Chennai–Trincomalee–Chennai) is the shortest international option, but three nights means one full day at sea each way, leaving only a few hours in port. The 5-night option is the smarter buy.

Cordelia's on-board experience skews family-friendly and vegetarian-accessible — a meaningful distinction for NRI families traveling with parents or children. Alcohol is available but not all-inclusive; spa and premium dining carry surcharges.

For the 10-night Southeast Asia cruise, NRIs holding US passports will need to check visa requirements for each port. Thailand, Malaysia, and Singapore all offer visa-free or visa-on-arrival for US passport holders, so the logistics are minimal. Indian passport holders with valid US visas can also transit visa-free through Singapore and Malaysia.

## Booking and Availability

Bookings are live through Cordelia's website and authorized agents like CruiseBay and Mercury Travels. The Chennai season runs June 20 through August 24. Given that the 10-night Singapore sailing is a single departure (July 18), cabins on that route will likely sell out first.

Chennai port's passenger terminal has been modernized over the past two seasons, with streamlined embarkation that now takes about 90 minutes — a far cry from the chaotic early seasons. The port is about 15 minutes from Chennai Central railway station and 45 minutes from Chennai International Airport.

For a country with 7,500 kilometers of coastline and a diaspora that regularly flies 16-hour routes to visit family, it's taken remarkably long for someone to put a proper cruise ship in the water. Cordelia's fifth season suggests the model works. Whether it scales beyond one ship and two homeports remains the bigger question — but for this summer, the tickets are real and the prices are hard to argue with."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's Pakistan Airspace Bill Hits ₹4,000 Crore — Delhi-Chicago Is Gone",
        "subheadline": "The airline has asked the government for compensation after the Pakistan airspace closure since April 2025 crippled its international network. Delhi-Chicago is discontinued, Delhi-Singapore is halved, and London and New York frequencies are down 30 percent.",
        "slug": make_slug("air-india-pakistan-airspace-4000-crore-delhi-chicago-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs on key corridors — especially Chicago's 400K+ Indian American community — are losing direct Air India options. The cascading cuts from Pakistan and Middle East airspace closures are reshaping which routes remain viable and pushing travelers toward Gulf and European carriers with longer layovers.",
        "tags": ["travel", "airlines", "air-india", "pakistan", "airspace", "chicago", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Whispers in the Corridors", "url": "https://www.whispersinthecorridors.com/detail/147584-Air+India+demands+%E2%82%B94000+Cr+compensation+from+GOI+due+to+closure+of+Pakistani+airspace.+Proposed+opening+China+sector%5E.html"},
            {"name": "MySandesh", "url": "https://mysandesh.in/air-india-reduces-flights-on-many-routes-till-august-2026/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-domestic-flights-amid-high-jet-fuel-prices-sources-say-2026-05-28/"},
            {"name": "IndUS Business Journal", "url": "https://www.indusbusinessjournal.com/air-india-reduces-domestic-flights-as-fuel-costs-rise/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32037884/pexels-photo-32037884.jpeg",
        "body": """Air India has submitted a ₹4,000 crore compensation demand to the Government of India, quantifying for the first time the financial toll of the Pakistan airspace closure that has been bleeding the national carrier since April 2025.

The number — roughly $475 million — covers losses from rerouted flights, additional fuel burn, extended crew hours, and cancelled services across hundreds of affected international routes. It arrives alongside the airline's recent disclosure of a record annual loss exceeding $2 billion, making this the worst financial period in Air India's post-privatization history under Tata Group and Singapore Airlines ownership.

## The Route-by-Route Damage

The airspace closure, imposed mutually by India and Pakistan following the Pahalgam terror attack and Operation Sindoor, forced Air India to reroute every westbound flight. Each affected service now runs 60 to 90 minutes longer than its pre-closure schedule, burning fuel on detours that were never part of the route economics.

The international cuts announced for June through August 2026 read like a systematic dismantling of the NRI travel network:

- **Delhi–Chicago**: completely discontinued
- **Delhi–Shanghai**: fully suspended
- **Delhi–Singapore**: slashed from 24 to 14 weekly flights
- **Mumbai–Singapore**: halved from 14 to 7 weekly
- **Delhi–Bangkok**: cut from 28 to 21 weekly
- **Delhi–Kuala Lumpur**: reduced from 10 to 5 weekly
- **Delhi–Paris**: reduced from two daily flights to one
- **London, Frankfurt, New York**: frequencies down 15 to 30 percent

Air India says it will still operate over 1,200 international flights monthly across five continents. But the trajectory is unmistakable — the airline is retreating from routes it cannot profitably serve while burning extra fuel on every remaining flight.

## Why Chicago Hurts the Most

The Delhi–Chicago discontinuation is not just another schedule tweak. Chicago's metropolitan area is home to one of the largest Indian American communities in the United States — over 400,000 people, many of whom relied on AI-127/AI-128 as the only nonstop option between Delhi and O'Hare.

Air India had previously operated both Delhi–Chicago and Hyderabad–Chicago nonstop services, building O'Hare into a genuine hub for Midwestern NRIs. The route's loss pushes those travelers onto connecting itineraries through JFK, Newark, or San Francisco — adding 4 to 8 hours of total travel time — or onto Gulf carriers routing through Dubai, Doha, or Abu Dhabi.

United Airlines still operates its own Delhi–Chicago service, but Air India's exit reduces competition on a corridor where fares were already climbing. One-way economy tickets on the route have been running $900–1,400 in recent weeks, compared to $600–800 before the airspace disruptions began.

## The Compounding Problem

The Pakistan airspace closure is not the only factor. The Iran conflict has restricted airspace across the Middle East, forcing airlines to avoid Iranian, Iraqi, and Israeli airspace on many routes. For Air India's westbound flights, this means the two most direct corridors to Europe and North America — through Pakistan and through the Middle East — are both compromised.

Jet fuel prices have surged from around ₹80,000 per kiloliter to over ₹1 lakh, a 25 percent increase that turns already-marginal routes into guaranteed money-losers. The strong US dollar compounds the problem: Air India earns revenue in rupees on many domestic legs but pays for fuel and international airport charges in dollars and euros.

IndiGo, India's largest carrier by market share, has also cut domestic and some international flights for the same reasons, though its long-haul exposure is smaller. The domestic reductions by both airlines — Air India is trimming roughly 20 percent of its domestic schedule — are partly a knock-on effect: fewer international flights mean fewer passengers needing domestic connections through Delhi and Mumbai.

## What NRIs Can Do

For travelers on affected routes, the practical options are limited but worth understanding:

**Chicago corridor**: United Airlines remains the only nonstop Delhi–O'Hare option. Emirates (via Dubai), Qatar Airways (via Doha), and Turkish Airlines (via Istanbul) offer one-stop alternatives with competitive business class products, though total travel times run 18 to 22 hours versus 15.5 for nonstop.

**Singapore and Southeast Asia**: Singapore Airlines, Vistara (now merged into Air India's network but operating separately), and IndiGo still serve the corridor. Emirates and Qatar offer Gulf-routed alternatives.

**Europe**: Lufthansa, British Airways, and Air France maintain robust India schedules. Turkish Airlines via Istanbul has emerged as a price-competitive alternative that avoids both the Pakistan and Iran airspace problems entirely.

Air India says affected passengers will be offered rebooking on alternative flights, complimentary date changes, or full refunds. The airline advises checking booking status regularly through its app, as "more schedule changes may happen in the coming weeks."

## The Bigger Picture

The ₹4,000 crore compensation demand is as much a political signal as a financial one. Air India is telling the government that strategic decisions — closing airspace, maintaining military postures — have direct costs for the national carrier. Whether the government pays is an open question, but the demand puts a dollar figure on what was previously an abstract geopolitical consequence.

For the 4.5 million Indian Americans who fly these routes, the message is simpler: the direct connection between India and the United States is getting thinner, more expensive, and less reliable. The summer of 2026 is shaping up to be the most difficult travel season in recent memory for the diaspora, and relief depends on geopolitical developments that show no sign of resolving soon."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
