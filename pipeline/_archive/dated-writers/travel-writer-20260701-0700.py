#!/usr/bin/env python3
"""Travel writer — July 1, 2026 morning run.

Two articles:
1. IndiGo Lite fare launch + ATF price cut (fare unbundling trend)
2. Navi Mumbai Airport's first international flights on July 15
"""
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


# ──────────────────────────────────────────────────────────
# Article 1: IndiGo Lite + ATF price cut
# ──────────────────────────────────────────────────────────

article1_body = """India's largest airline just made it cheaper to fly light. IndiGo launched "IndiGo Lite" on July 1 — a stripped-down economy fare for passengers who carry only cabin baggage. Bookings opened today on IndiGo's website, app and call centre, with the first Lite-fare flights departing from July 15 across domestic and international routes.

The pitch is straightforward: if you don't check a bag, you shouldn't pay for the privilege. IndiGo Lite passengers get a lower base price, an auto-assigned seat at no extra cost, and a cabin baggage allowance of 7 kg. Checked luggage, seat selection and meals can be added à la carte. The fare covers one-way, round-trip and multi-city itineraries on nonstop flights. Passengers still earn and redeem BluChip loyalty points.

## The unbundling wave hits Indian aviation

IndiGo isn't operating in a vacuum. Last month, Air India quietly introduced a basic economy fare that drops complimentary meals for "price-conscious travellers." Between the two carriers, India's domestic aviation market — the world's third-largest — is embracing the low-cost model that Ryanair and Spirit Airlines normalised in Western markets years ago.

The timing is not coincidental. Indian airlines have been squeezed from every direction this year. The Iran-Israel conflict drove jet fuel prices to record highs, airspace closures over West Asia forced expensive rerouting on European and North American routes, and the rupee's slide against the dollar has amplified fuel procurement costs.

But July 1 also brought a small reprieve. Oil marketing companies cut aviation turbine fuel (ATF) prices by ₹5 per litre, bringing the Delhi benchmark to roughly ₹110 per litre. It is the first reduction since the West Asia crisis began pushing fuel costs higher. The government's ₹10,000-crore ATF price-stabilisation scheme — offering airlines a fixed rate of ₹115 per litre for up to three years — remains on the table, though no carrier has opted in so far.

## What this means if you're flying home

For NRIs planning summer or Diwali trips to India, the convergence of unbundled fares and falling fuel costs could meaningfully shrink domestic travel budgets. The average NRI visiting family in India takes two to three internal flights — a Delhi-to-Lucknow hop to see parents, a connecting leg to a wedding in Jaipur, perhaps a weekend in Goa. On a typical four-day trip where you're living out of a carry-on, IndiGo Lite could shave a few thousand rupees off each leg.

On international routes, the savings calculus is different. IndiGo operates nonstop to the Gulf, Southeast Asia and southern Europe (its A321XLR-operated Athens service launched in January). A Lite fare on a Delhi-Dubai sector or a Mumbai-Singapore run could offer meaningful savings for the diaspora passenger who travels lean — visiting for a long weekend with a backpack rather than hauling two checked bags of gifts.

The catch: Lite fares are available only through IndiGo's own channels — its website, app and call centre. Third-party booking sites like MakeMyTrip and Cleartrip are excluded, at least for now. That's a deliberate push to recapture the booking funnel and cut out aggregator commissions.

## The bigger picture

India now has over 800 aircraft in service and more than 1,700 on order. Airlines need to fill seats. Unbundled pricing isn't charity — it's a yield management tool. IndiGo is betting that the passenger who pays less for a base fare will spend more on add-ons: extra legroom, priority boarding, meals, checked bags. The airline's ancillary revenue has been growing faster than ticket revenue for three consecutive quarters.

For the Indian traveller — especially the cost-conscious NRI navigating war-inflated international fares — any downward pressure on the base ticket price is welcome. Whether airlines pass along the full benefit of falling fuel costs remains the watch item for the rest of the summer."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Lite Is Here — India's Biggest Airline Wants You to Pay Only for What You Carry",
    "subheadline": "A new cabin-bag-only fare launches today alongside the first jet fuel price cut since the Gulf crisis began. For NRIs flying domestic legs during India trips, the math just changed.",
    "slug": make_slug("indigo-lite-cabin-bag-fare-atf-cut-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "NRIs taking 2-3 domestic flights during India visits can save thousands of rupees per leg with IndiGo Lite, and the first ATF price cut since the Gulf war signals further fare relief on diaspora routes.",
    "tags": ["travel", "airlines", "IndiGo", "fares", "aviation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-launches-cheaper-tickets-passengers-with-cabin-baggage-only-2026-07-01/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/indigo-rolls-out-lite-fare-bookings-for-july-15-travel-begin-today"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-launches-cheaper-tickets-for-passengers-with-cabin-baggage-only/article69748123.ece"},
        {"name": "Bharat Horizon", "url": "https://bharathorizon.com/indigo-lite-cabin-baggage-fares/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo — the workhorse of India's largest domestic and international carrier",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ──────────────────────────────────────────────────────────
# Article 2: Navi Mumbai Airport goes international July 15
# ──────────────────────────────────────────────────────────

article2_body = """On July 15, an Air India Express flight to Abu Dhabi will lift off from Navi Mumbai International Airport — and India's youngest commercial airport will become an international gateway. It is a milestone that was supposed to happen in March, but was delayed by the West Asia conflict. Now, with Gulf airspace reopening and customs clearances in their final stages, the launch is on track.

The Abu Dhabi service starts twice a week — Wednesdays and Fridays — stepping up to three weekly flights from July 29 with the addition of a Sunday departure. Flights depart Navi Mumbai at 02:55 and arrive in Abu Dhabi at 04:35 local time. The return leg leaves Abu Dhabi at 05:45 and lands at 10:20.

Cargo freighters will begin the same day, with plans to ramp to 18 freight movements per week. IndiGo is also expected to file international routes from the airport shortly.

## A second Mumbai — finally

Mumbai has needed a second airport for decades. Chhatrapati Shivaji Maharaj International Airport handles more than 50 million passengers a year on a site hemmed in by the city on all sides, with no room for a parallel runway. Delhi overtook Mumbai in passenger traffic back in 2008-09 and never looked back.

Navi Mumbai International Airport, operated by Adani Airports, opened for domestic traffic on Christmas Day 2025. Since then it has scaled rapidly: from 22 daily departures at launch to 149 daily flights today, connecting 46 domestic destinations. The airport now handles roughly 20,000 passengers daily and has crossed the two-million passenger mark in barely six months of operations.

The initial international focus will be short-haul Gulf routes — a logical starting point given the massive VFR (visiting friends and relatives) traffic between western India and the UAE. But the airport's ambitions are larger. Its management has begun redesigning the planned second terminal: the original 30-million-passenger facility has been scrapped in favour of a 50-million-passenger international terminal, to be built in phases based on demand.

## Why NRIs should care

For the estimated 3.5 million Indians in the Gulf and millions more across the NRI diaspora who fly into Mumbai, Navi Mumbai airport changes the ground game. The airport sits in Ulwe, Raigad district — significantly closer to Navi Mumbai, Thane, Panvel and the eastern suburbs than the existing airport across the harbour in Andheri.

If your parents live in Vashi, Kharghar or Belapur, you no longer need to budget two hours each way for the cross-city airport run through Mumbai's traffic. If you're visiting family in Pune, the Navi Mumbai airport is more accessible via the Mumbai-Pune Expressway than the existing airport on the western side of the city.

For now, the international network is limited to one Gulf route. But the playbook is familiar — budget carriers like Air India Express use a single route to establish customs and immigration operations, then layer on more destinations once the infrastructure is proven. Given Mumbai's position as India's busiest international aviation market, Navi Mumbai will likely add Gulf, Southeast Asian and eventually long-haul connections over the next 12-18 months.

## The infrastructure bet

Navi Mumbai airport is the eighth airport in the Adani Airports portfolio, which spans Ahmedabad, Lucknow, Mangaluru, Jaipur, Guwahati, Thiruvananthapuram and Mumbai's existing airport. The airport business contributed 10% of Adani Enterprises' consolidated income and 21% of its EBITDA in FY25.

The push to 50 million passengers in the second phase — up from the original 20 million capacity of the first terminal — signals that Adani is betting heavily on Mumbai's aviation demand. Customs authorities completed their inspection of international readiness last week, with the final Section 45 approval and trade notice expected by July 5.

For NRIs who have watched Mumbai's airport constraints with frustration — the queues, the single runway delays, the two-hour taxi rides — Navi Mumbai's international launch is the beginning of a structural fix, not just another route announcement."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Navi Mumbai Airport Goes International on July 15 — and NRIs on the Eastern Side Finally Have a Gateway",
    "subheadline": "Air India Express will fly the first international service from India's newest airport to Abu Dhabi, turning a six-month-old domestic hub into an international one. The airport has already crossed two million passengers.",
    "slug": make_slug("navi-mumbai-airport-international-july-abu-dhabi-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "NRIs with family in Navi Mumbai, Thane, Panvel and Pune get a second Mumbai airport option — closer, faster and without the cross-city traffic run to Andheri that has defined India trips for decades.",
    "tags": ["travel", "airports", "Navi Mumbai", "Air India Express", "infrastructure"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/navi-mumbai-airport-launch-international-flights-from-july-15/article69702321.ece"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/air-india-express-navi-mumbai-abu-dhabi/"},
        {"name": "ANI via Southeast Asia News", "url": "https://southeastasianews.net/navi-mumbai-international-airport-to-launch-international-flights-from-july-15-says-nmia-chairman/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
    "image_caption": "Navi Mumbai International Airport terminal — India's newest commercial airport opened in December 2025",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ──────────────────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
