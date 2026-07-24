#!/usr/bin/env python3
"""Travel writer — July 7, 2026 batch (3 articles)."""

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


articles = [
    # ── ARTICLE 1: Air India Express Xplore More Sale ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Express Is Running a Flash Sale on International Flights — Here's What NRIs Need to Know",
        "subheadline": "The Tata-owned carrier's 'Xplore More' sale offers up to 15 percent off fares to the Gulf and Southeast Asia, with a new Navi Mumbai–Abu Dhabi route launching July 15.",
        "slug": make_slug("air-india-express-xplore-more-sale-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "NRIs booking Diwali, Christmas, or winter trips to India can lock in discounted fares now — the sale covers travel through March 2027, hitting every major holiday window.",
        "tags": ["travel", "airlines", "air-india-express", "deals", "navi-mumbai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/air-india-express-unveils-xplore-more-mega-sale/"},
            {"name": "UAE News 4U", "url": "https://uaenews4u.com/air-india-express-launches-xplore-more-sale/"},
            {"name": "Daily Guardian UAE", "url": "https://dailyguardian.ae/air-india-express-launches-navi-mumbai-to-abu-dhabi-flights/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "The new Navi Mumbai International Airport, which will welcome its first Air India Express international flight on July 15",
        "image_attribution": "Wikimedia Commons",
        "body": """If you've been meaning to book your Diwali trip home — or that winter getaway through Dubai — this week is worth paying attention to.

Air India Express has launched its **"Xplore More" sale**, running from July 5 through July 9, with discounts of up to 15 percent on Lite and Value fares across the airline's entire international network. The travel window stretches all the way to March 27, 2027, which means it covers Onam, Navratri, Diwali, Christmas, New Year, and the spring break travel rush in one booking window.

## What's Actually on Offer

The headline discount is 15 percent off base fares, but the real value stacks up in the fine print. Bookings made directly on the Air India Express website or app carry zero convenience fees — a saving that adds up quickly on international itineraries. Every sale booking also comes with a complimentary date change option, a genuine perk for NRIs juggling visa timelines, work schedules, and family obligations across time zones.

Tata NeuPass members get an additional discount of up to ₹500 and can earn up to 8 percent in NeuCoins on international bookings, effectively layering a loyalty rebate on top of the sale price.

## The Network Is Bigger Than You Think

Air India Express now operates roughly **820 weekly international flights**, connecting dozens of Indian cities with destinations across West Asia and Southeast Asia. That includes 13 destinations across Bahrain, Kuwait, Oman, Qatar, Saudi Arabia, and the UAE, plus Bangkok, Phuket, and Singapore in Southeast Asia.

For NRIs routing through the Gulf — whether visiting family in Kerala, connecting through Dubai, or transiting Abu Dhabi — the frequency alone makes it a viable alternative to the legacy Gulf carriers.

## Navi Mumbai Gets Its First International Flights

Perhaps the most interesting development buried in the sale buzz is Air India Express becoming the **first airline to launch international flights from Navi Mumbai International Airport**, Maharashtra's newest aviation gateway. Direct flights to Abu Dhabi begin July 15, initially twice a week (Wednesdays and Fridays), scaling to three weekly flights from July 29.

For the millions of NRIs with roots in the Mumbai metropolitan region, this is a second international gateway — no more battling the traffic and congestion of Mumbai's Chhatrapati Shivaji Maharaj International Airport for every Gulf trip. Navi Mumbai also draws from Pune, and its catchment area stretches deep into western Maharashtra.

The airline has simultaneously launched Guwahati–Abu Dhabi and Guwahati–Dubai routes, opening direct Gulf connectivity for Northeast India — a region with a substantial diaspora working in the Gulf states but historically underserved by direct flights.

## The Booking Window Is Narrow

The sale ends July 9. Direct bookings on the airline's website and app got early access from July 5, with third-party platforms opening from July 6 onward. If you're planning a trip to India or through the Gulf anytime between now and next March, locking in fares this week makes straightforward financial sense — especially with the complimentary date change as insurance.""",
    },

    # ── ARTICLE 2: IndiGo Lite Fares ──
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Just Launched a Bare-Bones 'Lite' Fare — and Air India Followed Suit",
        "subheadline": "India's two largest airlines are unbundling their fares, offering stripped-down tickets without checked bags or meals. For NRIs who travel light, it could mean meaningfully cheaper flights.",
        "slug": make_slug("indigo-lite-air-india-basic-economy-fares-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "NRIs making quick trips to India — a weekend wedding, a document run, a short family visit — can now book genuinely cheaper tickets by skipping checked bags and meals they didn't need anyway.",
        "tags": ["travel", "airlines", "indigo", "air-india", "fares", "budget-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-indigo-launches-cheaper-tickets-passengers-with-cabin-baggage-only-2026-07-01/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/atf-price-cut-aviation-impact/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo — the airline's workhorse on both domestic and international routes",
        "image_attribution": "Wikimedia Commons",
        "body": """Indian airlines are taking a page from the American and European low-cost playbook, and it could save NRIs real money on the right kind of trip.

IndiGo, India's largest carrier by market share, launched **"IndiGo Lite"** on July 1 — a new entry-level fare available across both domestic and international flights. The concept is simple: you get a seat (auto-assigned) and a cabin bag allowance of up to 7 kilograms. No checked luggage, no meal, no seat selection. Just the flight, at a lower price.

The fare went live for bookings on IndiGo's direct channels starting July 1, with travel eligible from July 15 onward.

## Air India Made the Same Move Last Month

IndiGo isn't acting alone. Last month, Air India introduced its own **basic economy fare** — a stripped-down ticket that drops complimentary meals for "price-conscious travellers." It's the Tata Group carrier's first serious attempt at unbundling, following its premium cabin overhaul with A350 suites on US routes.

Together, India's two largest airlines — which between them carry well over half the country's domestic passengers and an expanding share of international traffic — are signaling that fare segmentation is now standard practice in Indian aviation.

## Why This Is Happening Now

The shift isn't purely customer-friendly altruism. Indian airlines are under **simultaneous cost pressure** from multiple directions. The Iran war drove jet fuel prices sharply higher earlier this year, squeezing margins on every flight. Airspace closures over parts of West Asia have forced longer routing on many international flights, burning more fuel per trip. And competition is intensifying, with new routes and carriers entering the market every month.

Unbundling lets airlines lower the advertised fare — the number that wins price-comparison searches — while recouping revenue from passengers who want add-ons. It's the model that made Ryanair and Spirit viable, and it's been standard on US domestic carriers for years.

## What NRIs Should Know

For diaspora travelers, the practical question is straightforward: **do you actually need a checked bag and a meal on every flight?**

If you're making a quick trip to India for a wedding, a visa appointment, or a short family visit — the kind of trip where you pack a carry-on and eat at the airport — IndiGo Lite or Air India's basic economy could shave a meaningful amount off your ticket. On domestic connections within India (say, Delhi to Hyderabad after arriving from SFO on a separate ticket), the savings add up even faster.

The catch, as always, is in the add-on pricing. If you end up buying a checked bag, a meal, and a seat selection separately, you may pay more than the standard fare. The value proposition is real only if you genuinely travel light.

## The Bigger Picture

India's aviation market is maturing. A decade ago, IndiGo's innovation was offering a reliable, on-time, no-frills flight at one price. Now, the market has segmented further: Air India chases the premium long-haul traveler with private suites and flat beds, while IndiGo and Air India Express compete on price with bare-bones fares.

For the NRI who books four to six India flights a year — a mix of long-haul international and short domestic hops — this means more options, more price points, and a reason to actually compare before clicking "book." The era of one-size-fits-all Indian airfares is over.""",
    },

    # ── ARTICLE 3: Jet Fuel Prices Drop ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Jet Fuel Just Got Cheaper — So Why Aren't Airfares Falling?",
        "subheadline": "Aviation turbine fuel prices dropped ₹5 per litre from July 1, and the government pledged a ₹100 billion support package. But for NRIs booking flights to India, the savings haven't shown up in ticket prices yet.",
        "slug": make_slug("india-jet-fuel-atf-price-cut-airfares-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "Fuel costs account for up to 60 percent of airline operating expenses on India routes — but despite a historic fuel price correction, NRIs are still seeing stubbornly high fares on key corridors like SFO-DEL and JFK-BOM.",
        "tags": ["travel", "airlines", "fuel-prices", "airfares", "aviation", "economy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CurrentIndia.com", "url": "https://www.currentindia.com/flight-fuel-gets-cheaper-atf-prices-cut"},
            {"name": "TTG India", "url": "https://www.ttgindia.travel/india-offers-fuel-price-relief-for-airlines-amid-cost-pressures"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-indigo-launches-cheaper-tickets-passengers-with-cabin-baggage-only-2026-07-01/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33300361/pexels-photo-33300361.jpeg",
        "image_caption": "A commercial aircraft being refueled on the airport tarmac — fuel accounts for up to 60 percent of airline operating costs",
        "image_attribution": "Pexels",
        "body": """India's state-run oil marketing companies quietly delivered what should have been excellent news for air travelers on July 1: a **₹5 per litre cut in Aviation Turbine Fuel (ATF) prices**, bringing the domestic rate down to roughly ₹110 per litre. The reduction came as international crude oil and jet fuel prices softened following the easing of tensions in West Asia and the resumption of shipping through the Strait of Hormuz.

On top of that, the Indian government last month approved a **₹100 billion (US$1.17 billion) interest-free advance** to oil marketing companies specifically to help stabilize ATF prices for airlines. It was the clearest signal yet that Delhi considers affordable aviation a policy priority.

And yet, if you've priced a flight from Newark to Delhi or San Francisco to Mumbai lately, you've probably noticed: the fares haven't budged much.

## The Math That Should Work — But Doesn't

Fuel is the single largest operating cost for airlines, typically accounting for **40 to 60 percent of total expenditure** depending on the route and the price environment. When crude oil spiked during the West Asia crisis earlier this year, airlines passed the cost on immediately — fares climbed, fuel surcharges appeared, and some routes saw double-digit price increases within weeks.

The reverse doesn't seem to apply with the same urgency. Jet fuel prices have fallen roughly **40 percent from their April peak** globally, according to industry data. Indian ATF has tracked that decline. But the gap between falling fuel costs and sticky ticket prices is widening.

## Three Reasons Fares Aren't Falling

**First, airlines are still absorbing losses from earlier this year.** The months of elevated fuel prices, combined with the depreciation of the rupee against the dollar (which makes fuel procurement more expensive since jet fuel trades in USD), left carriers with significant balance sheet damage. Lower fuel prices are being used to rebuild margins, not fund lower fares.

**Second, airspace restrictions continue to inflate operating costs.** The closure of Pakistani airspace during the height of the West Asia tensions forced international flights to reroute — adding flight time, fuel burn, and crew costs that don't disappear just because the base price of fuel dropped. Even with the Hormuz corridor reopening, some of these diversions remain in effect.

**Third, demand on India routes remains exceptionally strong.** India recorded 19.07 million international passenger movements in early 2026, according to DGCA data. With 9.77 million outbound passengers, the market is structurally tight — and airlines have little incentive to cut prices when planes are already flying full.

## What the Government Package Actually Does

The ₹100 billion support package is not a direct subsidy to passengers. It's an interest-free advance to oil marketing companies — essentially a mechanism to prevent OMCs from hiking ATF prices further, rather than a tool for bringing them down.

Subhash Goyal, chairman of the aviation committee at the Indian Chamber of Commerce, put it plainly: "The budgetary support will help airlines avoid steep increases in airfares. While this initiative may not eliminate the challenges, it is a positive step that can provide short-term stability."

In other words: the package is about preventing things from getting worse, not making them better for ticket buyers.

## What NRIs Can Actually Do

The practical takeaway for diaspora travelers is to treat the current fare environment as the new normal for the near term — and plan accordingly.

**Book early for peak periods.** Diwali (October), Christmas, and spring break are already showing elevated fares on popular NRI corridors. Promotional sales like Air India Express's current "Xplore More" offer (up to 15 percent off, through July 9) are worth watching.

**Consider the new unbundled fares.** Both IndiGo and Air India now offer stripped-down ticket options that drop checked bags and meals in exchange for lower base prices. For quick trips, the savings are real.

**Watch for fuel surcharge adjustments.** Some carriers adjust fuel surcharges with a lag of 30 to 60 days. If ATF prices hold at current levels, surcharges on India-US routes may ease later this summer — but it's not guaranteed.

The gap between fuel costs and ticket prices will narrow eventually. But in a market where demand outstrips supply and airlines are nursing losses from a volatile year, "eventually" isn't the same as "soon." """,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
