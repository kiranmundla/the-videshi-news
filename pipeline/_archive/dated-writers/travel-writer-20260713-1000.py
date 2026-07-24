#!/usr/bin/env python3
"""Travel writer for The Videshi — July 13, 2026 batch."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # -------------------------------------------------------------------
    # ARTICLE 1: India-to-US Travel Falls 4%
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "India-to-US Travel Falls 4% — and Indian Globetrotters Are Finding New Favorites",
        "subheadline": "As US arrivals from India record the steepest decline among major source markets, travelers are shifting budgets to the UK, Japan, South Korea, and a string of visa-friendly surprises.",
        "slug": make_slug("india-us-travel-decline-alternative-destinations-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs may notice fewer visiting relatives this summer — and the reasons go beyond airfare, from stricter US border scrutiny to a weakening rupee making America the priciest option on the board.",
        "tags": ["travel", "india-us", "tourism", "visa", "nri", "uk-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/4xowb5pu4jo7/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "US National Travel and Tourism Office", "url": "https://www.trade.gov/national-travel-and-tourism-office"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png?auto=compress&cs=tinysrgb&w=1260",
        "image_caption": "Digital flight information board displaying arrivals and departures at an international airport terminal",
        "image_attribution": "Pexels",
        "body": """For years, the United States sat comfortably atop the wish list for Indian international travelers. That hold is slipping.

Official data from the US National Travel and Tourism Office confirms that India has recorded the largest decline in US-bound visitors among the country's leading source markets in 2026, with arrivals falling more than 4%. The drop is not a blip — it reflects a convergence of financial pressure, tighter border policies, and a growing sense among Indian travelers that the world has better deals on offer.

## The math has changed

The Indian rupee's slide against the dollar has made every American hotel bill, restaurant tab, and Uber ride measurably more expensive. Add to that surging international airfares — carriers have hiked fuel surcharges sharply since the Strait of Hormuz disruption pushed crude above $100 — and a family trip to the US that once cost ₹8 lakh now easily runs past ₹12 lakh.

For the NRI community, this has a visible consequence: fewer relatives boarding flights to visit. The annual summer pilgrimage of parents and in-laws — a ritual for hundreds of thousands of Indian American households — is being deferred, rerouted, or replaced with video calls.

## Border anxiety adds to the chill

Financial pressure is only part of the story. Expanded social media vetting at US ports of entry, including for travelers from visa-waiver countries, has generated headlines and unease. While most visitors clear immigration without incident, the cumulative effect on public perception has been measurable.

A travel ban affecting nationals from 39 countries, introduced in January and overlapping with the 2026 FIFA World Cup, has further clouded America's image as a welcoming destination. The tourism industry — worth more than $1.1 trillion to the US economy — is watching nervously.

## Where the money is going instead

Indian travelers have not stopped traveling. They have redirected. Skyscanner India reports surging search and booking activity for Japan, South Korea, Georgia (Tbilisi), and Azerbaijan (Baku) — destinations that combine accessible visa policies, lower costs, and strong cultural appeal.

The UK-India travel corridor, meanwhile, has proven remarkably resilient. During the first quarter of 2026, more than 1.1 million passengers flew directly between the two countries — 577,380 from India to the UK and 559,601 the other way — supported by over 170 weekly direct flights. Indian tourist spending in the UK is projected to cross £1 billion by year-end.

Brazil has been another surprise winner, recording 2.6 million international tourists in just January and February 2026 — a 52.9% leap over the same period in 2024.

## What this means for NRIs

The shift has practical implications for the diaspora. Families coordinating multi-generational reunions may find it easier to meet in a third country — Dubai, London, even Bangkok — than to fly everyone to the US. NRIs planning their own India trips, meanwhile, are competing for seats on routes where airlines have cut capacity (Air India recently trimmed flights to Chicago, San Francisco, and Toronto).

Prime Minister Modi's public appeal in May for Indians to curb unnecessary foreign travel, aimed at trimming India's import bill during the Gulf crisis, added another headwind. Travel stocks including EaseMyTrip, Yatra, and Ixigo sold off on the news.

The era of the US as the default international destination for Indian travelers is not over. But in 2026, it is competing harder — and often losing — against a world that has learned to roll out a smoother, cheaper welcome mat."""
    },

    # -------------------------------------------------------------------
    # ARTICLE 2: Air New Zealand–Air India Direct Flights
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Air New Zealand and Air India Are Building a Bridge to Auckland — Direct Flights Targeted by 2028",
        "subheadline": "A 16-route codeshare is live, marketing teams are deploying to Indian cities, and both carriers say direct India-New Zealand flights will follow once demand and aircraft deliveries align.",
        "slug": make_slug("air-new-zealand-air-india-direct-flights-codeshare-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Over 80,000 Indians visited New Zealand last year, a 23% jump from pre-pandemic levels — and for the fast-growing Indian community across Australasia, a nonstop route would transform an 18-hour two-stop journey into a single overnight flight.",
        "tags": ["travel", "airlines", "air-india", "air-new-zealand", "nri", "codeshare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/"},
            {"name": "FlightGlobal", "url": "https://www.flightglobal.com/airlines/direct-new-zealand-india-flights-on-the-cards-under-air-nz-air-india-partnership/162200.article"},
            {"name": "Air India Newsroom", "url": "https://newsroom.airindia.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Air_New_Zealand%2C_Boeing_787-9%2C_ZK-NZF_NRT_%2818139364859%29.jpg/1280px-Air_New_Zealand%2C_Boeing_787-9%2C_ZK-NZF_NRT_%2818139364859%29.jpg",
        "image_caption": "An Air New Zealand Boeing 787-9 Dreamliner — the long-range aircraft type that could eventually serve a nonstop India route",
        "image_attribution": "Wikimedia Commons",
        "body": """There has never been a nonstop passenger flight between India and New Zealand. If Air New Zealand's latest signals are any guide, that will change before the decade is out.

Air New Zealand CEO Sanjiv Ravishankar told Aviation A2Z this week that the airline is actively working with Air India on a proposed joint venture that would coordinate schedules, share revenue, and lay the groundwork for direct services between the two countries. The carriers have set a target of launching nonstop flights by the end of 2028, subject to new aircraft deliveries and regulatory approvals in both countries.

## The codeshare is already flying

The partnership is not starting from scratch. Air New Zealand and Air India — both Star Alliance members — signed a codeshare agreement and memorandum of understanding in March 2025, witnessed by New Zealand Prime Minister Christopher Luxon at a ceremony in Mumbai.

That codeshare now covers 16 routes linking India, Singapore, Australia, and New Zealand. Indian travelers can fly Air India from Delhi, Mumbai, Bengaluru, or Chennai, then connect at Sydney, Melbourne, or Singapore onto Air New Zealand services to Auckland, Christchurch, Wellington, and Queenstown — all on a single itinerary.

## The numbers behind the push

Around 350,000 passengers flew between India and New Zealand in 2024, according to industry data. Singapore Airlines dominates the market with roughly 30% share; its joint venture with Air New Zealand gives the pair a combined 50%. Malaysia Airlines carries another 25%.

But the traffic has been growing fast. More than 80,000 Indian nationals visited New Zealand last year, a 23% increase over pre-pandemic 2019 figures. Air New Zealand has reported over 90% growth in passenger volumes originating from India onto its network since 2019.

Ravishankar said the airline wants to confirm demand across three segments before committing aircraft to a nonstop route: travelers visiting friends and relatives, corporate passengers, and premium leisure travelers. Rather than waiting for launch day, Air New Zealand plans to stimulate demand through targeted marketing campaigns, deploying senior staff to key Indian cities.

## What a direct flight would look like

The most likely route would connect Delhi or Mumbai with Auckland — a distance of roughly 12,500 kilometers that falls comfortably within the range of Air New Zealand's Boeing 787-9 Dreamliners. Flight time would be approximately 13–14 hours, turning what is currently an 18–20 hour two-stop journey into a single overnight flight.

The timing also depends on Air India's fleet refresh. The Tata-owned carrier has Boeing 787s and Airbus A350s in its long-haul fleet and is in the middle of a massive order book — 470 aircraft from Airbus and Boeing — that will reshape its network through the end of the decade.

## Why NRIs should care

New Zealand is home to one of the fastest-growing Indian communities in the Pacific. The 2023 census recorded over 280,000 people of Indian ethnicity in New Zealand, making Indians the country's third-largest ethnic group. For this community, direct flights would slash travel time for family visits, business trips, and the growing flow of Indian students to New Zealand's universities.

The broader Australasian corridor matters too. Indian Australians number over 900,000, and many have family and business ties stretching from Auckland to Sydney to Bengaluru. A direct Air India–Air New Zealand service would plug a gap that the Star Alliance partnership has only partially bridged.

For now, the best option remains routing through Singapore — a well-oiled connection that both carriers have refined. But the clock is ticking toward 2028, and neither airline appears interested in waiting longer than it has to."""
    },

    # -------------------------------------------------------------------
    # ARTICLE 3: Five-Star Hotels Abroad 23% Cheaper
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Five-Star Hotels Abroad Cost 23% Less Than in America — Here's How NRIs Can Cash In",
        "subheadline": "The 2026 Hotels.com Price Index reveals that luxury travelers who book internationally save an average of $120 a night — and India's monsoon season makes the math even better.",
        "slug": make_slug("five-star-hotels-cheaper-abroad-nri-india-monsoon-deals"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs weighing a trip home or a summer getaway, the data is clear: a five-star week in India or Southeast Asia costs less than a three-star week in most US cities — and monsoon-season pricing in India sweetens the deal further.",
        "tags": ["travel", "hotels", "luxury", "india", "monsoon", "deals", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "USA Today", "url": "https://www.usatoday.com/"},
            {"name": "Hotels.com / Expedia 2026 Hotel Price Index", "url": "https://www.expedia.com/newsroom/"},
            {"name": "BusinessWire", "url": "https://www.businesswire.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/258154/pexels-photo-258154.jpeg?auto=compress&cs=tinysrgb&w=1260",
        "image_caption": "A luxury tropical resort with a swimming pool at dusk — the kind of stay that costs far less outside the US",
        "image_attribution": "Pexels",
        "body": """If you are an NRI budgeting a summer trip and wincing at hotel prices in New York, Las Vegas, or Seattle, here is a number worth absorbing: five-star hotels outside the United States cost 23% less, on average, than their American counterparts.

That finding comes from the 2026 Hotels.com Hotel Price Index, released this month, which analyzed global booking data and surveyed 11,000 travelers. The headline: an international five-star stay averages $250 a night, while a comparable US five-star averages $370. In some cities, the gap is even wider — you can book a five-star room for under $150 a night in Porto Alegre, Brazil, Nha Trang, Vietnam, or Phuket, Thailand.

This is the second consecutive year that international luxury has undercut domestic pricing, and it is changing how American travelers — including the Indian American diaspora — think about where their vacation dollars stretch furthest.

## India's monsoon math

For NRIs considering a trip home, the timing could not be better. India's monsoon season, which runs from June through September, brings flight fares down 30–50% compared with peak winter pricing on popular routes, according to travel platforms. Hotel rates across the country dip significantly.

The Taj Mahal Palace in Mumbai — arguably India's most iconic luxury hotel — is currently listing at around $254 a night. That is $116 less than the US five-star average and less than half the $427-a-night average for a luxury stay in Seattle. Even Delhi's premium properties near the airport, like the Novotel Aerocity, run as low as $77 a night.

Beyond pure pricing, the monsoon transforms India's landscapes. Kerala's backwaters swell with rain, Rajasthan's forts glow green, and Ranthambore's tigers are at their most active. The tradeoff — afternoon downpours and humidity — is well worth it for travelers who plan around it.

## How to book smarter

The Hotels.com data offers several tactical insights that NRI travelers can use:

**Book late.** The sweet spot for hotel booking is 8–14 days before travel. Last-minute bookings can save up to 30% across all star ratings. This runs counter to the instinct to lock in flights early and hotels later — but the data backs it up.

**Check in on Sunday.** Sunday is the cheapest day to start a hotel stay in the US, while Saturday is the most expensive internationally. If your India itinerary is flexible, shifting your arrival day can trim costs.

**January is king.** For those planning ahead, the cheapest month for hotel stays globally is January — right after the holiday rush clears. The most expensive domestic period falls during the second week of October, driven by fall breaks and business travel.

**Compare aggressively.** The price index shows that 4-star hotels are the most commonly booked category, and many travelers say they now associate luxury with a great view rather than a star rating. In India, a well-reviewed 4-star heritage property can outperform a formulaic 5-star chain hotel at a fraction of the cost.

## The bigger picture

The pricing gap reflects more than just exchange rates. Lower costs of goods, services, and labor in markets like India, Southeast Asia, and Latin America mean that a luxury experience — attentive service, fine dining, spa access, pool facilities — can be delivered at a structurally lower price point than in the US.

For NRIs, this creates an obvious playbook: when visiting family in India, build in a few days at a luxury property for a fraction of what a comparable stay would cost stateside. A week at a five-star resort in Kerala, Goa, or Rajasthan — including flights — can run less than a long weekend at a mid-range hotel in Manhattan.

As Melanie Fish, Hotels.com's vice president of global PR, put it: "This is a summer where how you book matters just as much as where you go." For Indian Americans with the flexibility to look beyond US borders, the data says the world is offering more for less — and India is one of the best deals on the board."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
