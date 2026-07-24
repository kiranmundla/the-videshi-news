#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-30 02:00 UTC run"""
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
    # ── Article 1: India Luxury Hotel Boom ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Luxury Hotel Boom Is Rewriting the NRI Homecoming",
        "subheadline": "From a Leela in the Thar Desert to India's largest DoubleTree at Bengaluru airport, the country is adding premium rooms faster than any market in Asia Pacific — and NRIs are the target guest.",
        "slug": make_slug("india-luxury-hotel-boom-nri-homecoming"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India now have a tier of accommodation that rivals anything in the Gulf or Southeast Asia. The new properties are clustered around airports, pilgrimage towns, and wedding-destination corridors — precisely the itinerary of a typical homecoming trip.",
        "tags": ["travel", "hotels", "india", "luxury", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel+Leisure Asia", "url": "https://www.travelandleisureasia.com/"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com/"},
            {"name": "TravelPlusStyle", "url": "https://www.travelplusstyle.com/"},
            {"name": "Glance Trends", "url": "https://trends.glance.com/"},
            {"name": "Journal des Palaces", "url": "https://www.journaldespalaces.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/47/Jaisalmer_forteresse.jpg",
        "body": """Something has shifted in Indian hospitality, and NRIs planning their next trip home should pay attention.

India added more hotel rooms in the first half of 2026 than any other country in Asia Pacific excluding China. The pipeline now stands at over 610 projects and 75,000 keys, according to Lodging Econometrics — a record that reflects a hospitality sector finally catching up to the country's economic weight. For the diaspora, this matters in a very specific way: the India you fly home to now has hotels that match or exceed what you find in Dubai, Singapore, or Bangkok.

## The Leela Jaisalmer: Destination Weddings in the Desert

The most talked-about opening is The Leela Jaisalmer, a 30-acre property in the Thar Desert within reach of the UNESCO-listed fort. The 80-room resort breaks from the ornate Rajasthani heritage style that dominates the region, opting for a cleaner, contemporary look with a mix of masonry rooms and tented villas spread across the dunes. The centrepiece is a massive pillarless ballroom and open-air courtyards engineered for large-scale weddings — precisely the market that NRI families are driving. Rajasthan destination weddings have become a rite of passage for Indian American families willing to spend, and The Leela is built to capture that demand.

## India's Largest DoubleTree: Built for the Bengaluru Corridor

At Bengaluru's Kempegowda International Airport, Hilton has opened India's largest DoubleTree — 304 rooms in the Aerospace Park, fifteen minutes from the terminal. The property is designed for the corporate traveller, with an outdoor pool, poolside cabanas, and conference rooms. For the tens of thousands of NRIs who fly the SFO–BLR and SEA–BLR corridors for work, this fills a genuine gap: a reliable international-brand hotel close enough to the airport for a red-eye recovery before heading into the city.

Rates start at roughly $116 per night — a fraction of what the same brand charges at comparable US airport hotels.

## InterContinental Chennai Mahabalipuram: A Coastal Icon Returns

IHG has completed a multi-million-dollar renovation of the InterContinental Chennai Mahabalipuram Resort, a 15-acre beachfront property on the scenic East Coast Road inspired by the iconic Shore Temple. The redesign blends contemporary luxury with South Indian cultural references. Sudeep Jain, IHG's managing director for South West Asia, called it "a new benchmark for mindful luxury on the Coromandel Coast."

For NRIs from Tamil Nadu — one of the largest state-level diaspora groups in the US — this is notable. Chennai has long lagged behind Goa and Rajasthan in the luxury resort category, and the InterContinental reopening signals that the coast south of Chennai is finally getting serious attention.

## The Leela Moves Into Coorg

The Leela group has also acquired a luxury resort in Coorg, Karnataka — the coffee-plantation hill station known as the "Scotland of India." The acquisition adds 4,160 keys to a 15-property portfolio and is expected to welcome guests before year-end 2026. Coorg has been an open secret among Bengaluru weekenders for years, but international-grade luxury accommodation has been scarce. The Leela's entry changes the math for NRIs looking to extend a Bengaluru work trip into a few days of hill-country quiet.

## The Spiritual Hospitality Play

In Vrindavan, Vivanta (a Tata brand) opened a 135-room property in late March, positioned squarely at the intersection of luxury and pilgrimage. The hotel serves pure vegetarian food, has a rooftop infinity pool, and sits close to the town's major temples. It is a bet on a growing NRI travel pattern: combining a spiritual visit with creature comforts that previous generations of pilgrimage hotels never offered.

## What This Means for NRIs

India's hotel investment hit $401 million last year, a fourfold increase from 2022. Radisson is building a 300-room property in Hyderabad's Financial District. Minor Hotels plans 50 properties in India over the next decade. The message is clear: international hospitality chains see India's domestic and diaspora travellers as a growth market worth billions.

For NRIs who last visited when "luxury" meant a mid-range Taj with intermittent Wi-Fi, the shift is worth noting. The next trip home might feel less like an obligation and more like a holiday."""
    },

    # ── Article 2: Route 66 Centennial ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Route 66 Turns 100 — and NRI Families Have a Summer Road Trip Worth Taking",
        "subheadline": "America's Mother Road celebrates its centennial on June 6 with events across eight states. For Indian American families who have never done the classic cross-country drive, this is the year.",
        "slug": make_slug("route-66-centennial-nri-family-road-trip"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRI families travel to India for holidays but rarely explore the American interior. Route 66's centennial — with its roadside diners, national parks, and small-town festivals — offers a distinctly American experience that first-generation immigrants and their American-born kids can share.",
        "tags": ["travel", "road-trip", "route-66", "usa", "family"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN Travel", "url": "https://www.cnn.com/travel/article/route-66-centennial-essential-stops"},
            {"name": "Expedia", "url": "https://www.parade.com/"},
            {"name": "Visit Santa Monica", "url": "https://www.santamonica.com/"},
            {"name": "The Oklahoman", "url": "https://www.oklahoman.com/"},
            {"name": "Route 66 News", "url": "https://route66news.com/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/210112/pexels-photo-210112.jpeg",
        "body": """On June 6, 1926, the American Association of State Highway Officials designated a road stretching 2,448 miles from Chicago to Santa Monica. They numbered it 66. A century later, it remains the most storied highway in the country — and this summer, it is throwing a birthday party across eight states that NRI families should seriously consider crashing.

## A Centennial Worth the Drive

Route 66 is having a moment. Expedia reports a 302% increase in mentions of the highway this year, making it one of the most searched road trip destinations in America. The centennial has triggered a wave of celebrations: Santa Monica launches a caravan from the pier on June 6 that will traverse the full length of the Mother Road. Oklahoma City hosts "Kickin' It On Route 66" at Scissortail Park on May 30. Tulsa is staging the largest classic car parade the highway has ever seen. Albuquerque's museum opens a centennial exhibition on June 6. Even the US Postal Service has issued commemorative stamps.

For Indian American families — particularly those in the Midwest and on the coasts who fly to India for every vacation but have never driven through their own country's interior — this is an invitation to a different kind of trip.

## The Route, in Brief

The classic alignment runs Chicago to Santa Monica through Illinois, Missouri, Kansas, Oklahoma, Texas, New Mexico, Arizona, and California. You do not need to drive all 2,448 miles. The most rewarding segments can be done in a long weekend:

**Oklahoma's "100 Greatest Miles"** — the 11-town corridor from Sapulpa to Edmond, passing through the Rock Cafe in Stroud (the inspiration for Sally's café in Pixar's *Cars*), the iconic Round Barn in Arcadia, and the Route 66 Bowl in Chandler. A road rally on June 6 costs $25 per vehicle and covers 26 checkpoints.

**Albuquerque's Central Avenue** — the original Route 66 path through the city, lined with "Pueblo Deco" architecture from the 1930s. The KiMo Theater, El Vado Motel, and repurposed gas stations turned into restaurants (the Andy Johnston Service Station is now an Asian fusion spot called Fan Tang) make for a walkable afternoon.

**Arizona's Oatman to Kingman stretch** — twisting mountain roads that inspired the landscape in *Cars*, complete with wild burros in Oatman and the original Cool Springs Station.

## Why This Works for NRI Families

The Indian American family road trip is an underexplored genre. Most first-generation NRIs grew up in a culture where long-distance travel meant trains, and vacations meant going home. Their American-born kids, meanwhile, associate travel with airports and resorts. Route 66 is neither — it is diners and motels and empty desert highway and the kind of unscripted American experience that does not exist on a cruise ship or at a theme park.

The timing helps. Summer airfares to India are brutally expensive this year — up 30% or more on key diaspora routes thanks to the fuel crisis. A domestic road trip with a minivan, a cooler of snacks, and a loose itinerary is the budget-friendly alternative that also happens to be genuinely memorable.

## Practical Notes

Expedia's trending summer destinations list favours gateway towns near national parks — St. George, Utah (+125% in bookings) for Zion and Bryce Canyon, Bozeman, Montana (+30%) for Yellowstone. Several of these sit near Route 66 or connect easily to it.

Hotels along the route are booking fast for the centennial. If you are planning a June or July drive, book accommodation now, especially in smaller towns like Williams and Kingman in Arizona.

The "Pacific Coast Highway" leg from Santa Monica to San Francisco (+75% in mentions) makes a natural extension. End your Route 66 drive at the Santa Monica Pier, pick up your free Certificate of Completion from the Visitor Information Center, and head north along the coast.

Pack the car. Call the kids. The Mother Road is turning 100, and it has never been more worth the drive."""
    },

    # ── Article 3: IndiGo's Quarterly Loss ──
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Just Lost $280 Million in a Single Quarter — What NRIs Need to Know",
        "subheadline": "India's largest airline posted its worst quarterly result in years, is considering fuel hedging for the first time, and has slowed capacity growth to a crawl. For NRIs who rely on IndiGo for domestic connections, the ripple effects are real.",
        "slug": make_slug("indigo-quarterly-loss-fuel-hedging-nri-impact"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "IndiGo carries more domestic passengers than any airline in India. NRIs use it for the DEL-BLR, BOM-HYD, and MAA-BLR hops that connect international arrivals to final destinations. Fewer flights, higher fares, and a financially stressed carrier directly affect the NRI travel experience.",
        "tags": ["travel", "airlines", "indigo", "india", "fares"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-mulls-hedging-fuel-costs-after-quarterly-loss-crude-surge-hits-margins-2026-05-29/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-domestic-flights-high-jet-fuel-prices-2026-05-27/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/energy/baton-rouge-melbourne-iran-war-rising-prices-upend-jet-fuel-trade-2026-05-28/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14694761/pexels-photo-14694761.jpeg",
        "body": """IndiGo, the airline that moves more people inside India than any other, just reported a net loss of ₹26.62 billion ($280 million) for the quarter ended March 31. A year ago, the same quarter delivered a profit of ₹30.73 billion. The swing — nearly $600 million from profit to loss — is the starkest measure yet of what the Iran war and its oil-price shock have done to Indian aviation.

For the four million NRIs who fly to India each year and rely on IndiGo for the domestic legs of their journey, the numbers matter more than they might appear.

## What Happened

Three forces collided. First, jet fuel prices surged after Iran's effective closure of the Strait of Hormuz disrupted global oil supply. Fuel accounts for 30% to 40% of an airline's operating costs, and IndiGo — unlike many Western carriers — has historically never hedged its fuel exposure. When crude spiked, IndiGo absorbed the full hit.

Second, the rupee weakened sharply against the dollar. More than 60% of IndiGo's costs are dollar-denominated — aircraft leases, maintenance contracts, spare parts. The currency swing added ₹48.82 billion in foreign-exchange losses in a single quarter, compared with a ₹1.38 billion gain a year earlier.

Third, regulatory capacity cuts imposed after December's aviation crisis — one of India's worst — forced IndiGo to fly 10% fewer domestic flights than it otherwise would have. Revenue rose just 1.3%.

## The Hedging Shift

The most significant signal from IndiGo's earnings call was not the loss itself but a four-word phrase from CFO Gaurav Negi: "whether fuel hedging is another option." IndiGo has never hedged fuel. The company's founding philosophy was that hedging added complexity and cost without reliably improving outcomes. That orthodoxy is now under review.

"We will be putting our minds to start looking at whether fuel hedging is another option, given what we've experienced in the last three months now," Negi told analysts.

If IndiGo does begin hedging, it would mark a fundamental change in how India's dominant carrier manages risk — and potentially, a floor under future fare volatility. Hedged airlines can keep ticket prices more stable during oil shocks because their fuel costs are partially locked in. Unhedged airlines pass every spike directly to passengers.

## Capacity Growth Is Slowing to a Crawl

IndiGo expects capacity growth of just 3% to 4% in the current quarter, down from 16.4% growth a year earlier. That is not a rounding error — it is the difference between an airline expanding aggressively and one that is treading water.

Combined with the flight cuts already announced — IndiGo is trimming 7% to 10% of domestic flights and 17% of international capacity through August — the practical effect is fewer seats on the routes NRIs care about. Delhi-Hyderabad, Mumbai-Bengaluru, Chennai-Kolkata: these are the connections that turn a 16-hour international journey into a 20-hour one when the domestic leg is delayed, full, or cancelled.

## What NRIs Should Do

Book domestic connections early. The combination of fewer flights and steady demand means the last-minute IndiGo ticket that used to cost ₹3,000 may now cost ₹8,000 or more on popular routes.

Consider alternatives. Air India, despite its own 22% domestic cut, still operates on many NRI-relevant corridors. Akasa Air and other newer carriers are picking up some of the slack, though their networks are thinner.

Watch the fuel hedging decision. If IndiGo commits to hedging, it could stabilize domestic fare volatility over the next 12 to 18 months. If it does not, expect continued turbulence — in the financial and literal senses — every time oil prices move.

The airline's managing director, Rahul Bhatia, struck a reassuring tone: "While the near term remains volatile, we remain firmly focused on disciplined execution, cost efficiency, and long-term value creation." That is corporate for "we will get through this." He is probably right. IndiGo controls 60% of India's domestic market and has outlasted every competitor that has tried to challenge it. But the next two quarters will be the roughest it has faced since the pandemic — and NRIs flying home this summer will feel it at the booking screen."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
