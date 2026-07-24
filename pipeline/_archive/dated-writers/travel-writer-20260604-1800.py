#!/usr/bin/env python3
"""Travel writer — 2026-06-04 18:00 UTC run. Three articles."""

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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────────────

art1_body = """IndiGo, India's largest airline by market share, announced Thursday that it will suspend services to six international destinations starting July 1 — barely a week after reporting a quarterly loss driven by skyrocketing jet fuel prices. The cuts to Hong Kong, Shanghai, Langkawi, Krabi, Ho Chi Minh City, and Siem Reap follow last week's confirmation that both Manchester routes will end on August 31. Together, the airline is pulling out of eight international markets in under two months.

The scale of the retreat is striking for a carrier that only months ago was celebrating its emergence as India's largest international operator. IndiGo still runs more than 1,800 international flights per week, but the cuts signal that the economics of long-haul and mid-haul flying have deteriorated sharply since the Iran conflict began disrupting airspace across West Asia.

## The Iran War Tax on Indian Aviation

The root cause is straightforward: closed airspace means longer routes, longer routes burn more fuel, and fuel prices have roughly doubled since the conflict escalated. Pakistan's airspace ban on Indian carriers — imposed during military tensions last year — compounds the problem, adding hours to flights that once took direct paths over the subcontinent's western flank.

IndiGo's Manchester operation was a particular casualty. Launched in July 2025 with leased Boeing 787-9 Dreamliners from Norse Atlantic Airways, the Mumbai and Delhi services were the airline's first-ever European routes. One-way fares started at £290 — undercutting Air India and Virgin Atlantic by a wide margin.

"We inducted these wide-body aircraft to fast-track our connectivity to high-potential long-haul destinations such as Manchester, and witnessed very encouraging demand response," said Abhijit Dasgupta, IndiGo's Senior Vice President for Network Planning. "It is unfortunate that longer flying times due to airspace constraints coupled with dramatically escalating costs compelled us to take the decision to temporarily discontinue."

IndiGo will return one of its six leased 787-9s to Norse Atlantic. The remaining five will continue serving other long-haul routes — for now.

## The Domestic Squeeze

The international cuts are only part of the picture. Reuters reported last week that IndiGo had already trimmed domestic flights for June and July by 7-10 percent. Rival Air India has cut deeper, slashing 22 percent of domestic services over the same period.

IndiGo's CFO Gaurav Negi has said the airline may consider fuel hedging to manage the ongoing volatility — a tool IndiGo has historically avoided. The carrier's Q4 loss, reported just days before the route cuts, underscored why hedging is now on the table.

## What This Means for NRIs

For the approximately 1.2 million Indians living in the UK, the Manchester cuts remove the only budget direct option from the North of England. Travelers from Manchester, Leeds, Liverpool, and surrounding cities now face a choice: fly via London on Air India or Virgin Atlantic at higher fares, or route through Gulf hubs — exactly the connections that are themselves under pressure from airspace disruptions.

The Southeast Asian route cuts hit a different segment. Destinations like Langkawi, Krabi, and Siem Reap had become popular visa-friendly holiday options for NRIs visiting from the US and Canada, often tacked onto India trips. Ho Chi Minh City and Shanghai served business corridors where India-based professionals and diaspora entrepreneurs increasingly operate.

IndiGo says it plans to reopen bookings from October 1, or earlier if conditions improve. But the airline's hedging against optimism is telling — Dasgupta called the Manchester suspension "temporary in nature" while Norse Atlantic confirmed the returned aircraft would be redeployed on Europe-Thailand routes instead.

The broader message is clear: Indian aviation is repricing around a new geopolitical reality. Every route that crosses or skirts West Asian airspace now carries a cost penalty that budget carriers cannot absorb. For NRIs who built travel habits around IndiGo's aggressive pricing, the summer of 2026 demands a rethink."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Axes Eight International Routes as the Iran War Burns Through Indian Aviation",
    "subheadline": "Manchester, Hong Kong, Shanghai, and five more destinations fall off the map as airspace closures and fuel costs force India's largest airline into its biggest route retreat yet.",
    "slug": make_slug("indigo-axes-eight-international-routes-iran-war"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "UK-based NRIs lose the only budget direct option from Northern England; SE Asian holiday routes popular with US/Canada diaspora vanish right as summer starts; fare pressure across all India routes intensifies.",
    "tags": ["travel", "airlines", "indigo", "iran-war", "routes", "uk-nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-2026-06-04/"},
        {"name": "The Sun", "url": "https://www.thesun.co.uk/travel/35649218/budget-airline-axe-flights-uk/"},
        {"name": "Hotelier India", "url": "https://www.hotelierindia.com/operations/indigo-to-suspend-manchester-flights-from-august-31"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-suspend-manchester-flights-from-august-31-amid-rising-costs-and-airspace-constraints/article69644123.ece"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo in the airline's signature blue livery",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────────────

art2_body = """Air India and Riyadh Air signed a memorandum of understanding on Wednesday to establish codeshare and interline arrangements connecting their networks through Delhi, Mumbai, and Riyadh. The deal — pending regulatory approvals in both countries — positions Saudi Arabia's brand-new national carrier as a transit partner for Indian travelers headed to Europe and beyond.

The timing is deliberate. Riyadh Air opens public sales for its inaugural London Heathrow service on July 1, giving the codeshare an immediate flagship route. Under the planned arrangement, a passenger in Delhi or Mumbai could book a single itinerary to London through Riyadh — a routing that sidesteps much of the airspace disrupted by the Iran conflict.

## Two Premium Carriers, One Network

The partnership pairs two airlines that share a premium positioning but serve very different markets. Air India, owned by the Tata Group since its 2022 privatization, operates 25 codeshare partnerships and more than 120 interline agreements. It carries the weight of India's largest international network. Riyadh Air, backed by Saudi Arabia's Public Investment Fund, is a startup with global ambitions and a fleet of new widebody aircraft.

Campbell Wilson, Air India's CEO, described India and Saudi Arabia as "two of the most important growth markets in global aviation" and called the scale and momentum in both countries a natural fit. Tony Douglas, Riyadh Air's CEO, called India "one of the most important and dynamic aviation markets in the world."

Beyond flights, the MoU covers reciprocal loyalty program benefits, cargo services, operational support, and shared digital initiatives. The loyalty piece matters: Air India's frequent flyer program, which feeds into the broader Tata Group ecosystem, could gain a Gulf-based earning and redemption partner that neither Emirates nor Qatar Airways currently provides in quite the same way.

## The Gulf Corridor Math for NRIs

Roughly 2.7 million Indians live in Saudi Arabia — the largest expatriate community in the kingdom. For this population, the codeshare simplifies what has historically been a booking headache: connecting from Indian domestic flights to Gulf-based international services often required separate tickets, separate check-ins, and no baggage protection if a connection was missed.

A working codeshare through Riyadh also creates a credible alternative to the established Gulf hubs. Dubai (Emirates), Doha (Qatar Airways), and Abu Dhabi (Etihad) have long dominated India-to-world connectivity, but the Iran war has exposed the vulnerability of routing through airspace that borders an active conflict zone. Riyadh sits further from the disruption, and its westward routes to Europe face fewer diversions.

For NRIs in the United States, the calculus is more indirect but still relevant. Air India's nonstop services from Newark, JFK, SFO, and Chicago to Delhi and Mumbai are the primary arteries. But when those flights are full — or when fare-hunters are looking for alternatives — a Gulf connection through Riyadh to secondary Indian cities could fill a gap that currently requires awkward itineraries through Dubai or Doha.

## What Comes Next

The MoU is a framework, not a finished product. Codeshare routes need regulatory clearance from both the Directorate General of Civil Aviation in India and the General Authority of Civil Aviation in Saudi Arabia. Air India's track record suggests this could take months. But the strategic logic is strong: Saudi Arabia is investing billions in tourism infrastructure under Vision 2030, and India is its largest source of both workers and potential visitors.

The Heathrow launch on July 1 will be the first real test. If Riyadh Air can deliver competitive timings and fares on the India-London corridor — a route that carries enormous NRI traffic for work, education, and family — the partnership has a chance to reshape how Indian travelers think about Gulf transit. If the connection experience is clunky, it becomes another MoU that reads better in a press release than in a boarding pass."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India and Riyadh Air Ink Codeshare Deal — NRIs Get a New Gulf Gateway",
    "subheadline": "The partnership connects Delhi and Mumbai to Riyadh Air's network, including a London Heathrow launch on July 1, offering Indian travelers a transit alternative as Iran War airspace disruptions pressure Gulf hubs.",
    "slug": make_slug("air-india-riyadh-air-codeshare-nri-gulf-gateway"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "2.7 million Indians in Saudi Arabia gain simpler single-ticket bookings; NRIs in the US get an alternative Gulf connection to secondary Indian cities; London-bound diaspora travelers get a Riyadh routing that avoids Iran-adjacent airspace.",
    "tags": ["travel", "airlines", "air-india", "riyadh-air", "codeshare", "saudi-arabia", "gulf"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/04/air-india-and-riyadh-air-sign-mou-for-new-codeshare/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/global-airline-chiefs-confront-iran-war-fuel-shock-industry-summit-2026-06-04/"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "image_caption": "An Air India Boeing 777 at New York's JFK airport in the airline's new Tata-era livery",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ── ARTICLE 3 ──────────────────────────────────────────────────────────────────

art3_body = """India's Union Cabinet approved a ₹10,000 crore emergency fund on Wednesday to stabilize aviation turbine fuel prices for domestic airlines, capping ATF at ₹75.60 per litre for domestic operations. The move — the government's most direct intervention in airline economics since the pandemic — comes as jet fuel prices have roughly doubled since the Iran war began, pushing carriers into quarterly losses and triggering the deepest schedule cuts in years.

Union Minister Ashwini Vaishnav announced the fund as a one-time budgetary support package, structured as interest-free advances to oil marketing companies. The OMCs will use the money to subsidize ATF prices for scheduled Indian carriers on both domestic and international operations. When global prices moderate, the differential will be recovered — making this a revolving credit facility rather than a permanent subsidy.

## How the Fund Works

Participating airlines must sign an MoU committing to procure ATF exclusively from OMCs for up to three years, subject to annual review. The Ministry of Civil Aviation and the Ministry of Petroleum and Natural Gas will serve as signatories. The arrangement continues until global prices normalize and the full advance is recovered.

The ATF cap at ₹75.60 per litre is significant context. Before the Iran conflict, domestic ATF prices hovered around ₹65-70 per litre. The current market rate, driven by crude oil spikes and Strait of Hormuz supply fears, has pushed past ₹105 per litre in some markets. The cap effectively absorbs the top third of the price surge — enough to prevent further schedule cuts, but not enough to reverse the ones already made.

Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum — the three state-owned OMCs — will implement the pricing. Whether private retailers like Reliance and Nayara participate remains unclear.

## Airlines Are Already Bleeding

The fund arrives after weeks of cascading cuts. IndiGo, India's largest carrier, reported a fourth-quarter loss driven by fuel costs and has since suspended eight international routes and trimmed domestic capacity by 7-10 percent. Air India has cut 22 percent of domestic flights. Smaller carriers — Akasa Air, SpiceJet, and Alliance Air — have pulled back on marginal routes quietly, without the press releases.

This weekend's IATA annual general meeting in Rio de Janeiro, running June 6-8, is expected to deliver a sobering downgrade to the industry's global profit forecast. Before the Iran war, airlines were projected to earn a record $41 billion in 2026. Moody's Ratings last week cut the global airline sector outlook from stable to negative, forecasting a 35 percent profit decline this year.

Air India's outgoing CEO Campbell Wilson told Reuters that higher fuel prices and airspace closures were "making some routes harder to justify" — a diplomatic way of saying that several long-haul services are now losing money on every flight.

## What NRIs Should Expect This Summer

The ₹10,000 crore fund will help stabilize domestic fares, which matters for NRIs who fly within India after landing in Delhi, Mumbai, or Bengaluru. Without the cap, carriers would have passed the full fuel increase to passengers or cut more routes — both of which make the post-landing India experience worse.

But international fares are a different story. The fund covers ATF procurement for international operations, but the fuel consumed outside India — at foreign airports, on return legs — remains at global market prices. The India-US corridor, where round-trip fares have already climbed 15-25 percent since February, is unlikely to see relief from this subsidy alone.

Summer 2026 is shaping up as the most expensive flying season for the India-US corridor in a decade. Airlines are raising fares on seven out of seven attempts without seeing demand weaken, according to Southwest Airlines CEO Bob Jordan at the IATA pre-summit. For NRIs booking monsoon-season or Diwali travel, the advice is unambiguous: lock in fares now, because nothing in the current environment suggests they will drop before October.

The government's intervention buys Indian aviation time, not a cure. The cure requires either a ceasefire in the Iran conflict, a reopening of Pakistan's airspace to Indian carriers, or both. Until then, the ₹10,000 crore fund is a pressure valve — necessary, but nowhere near enough to restore the fares and frequencies NRIs had come to expect."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Throws Airlines a ₹10,000 Crore Lifeline — But NRIs Will Still Pay More This Summer",
    "subheadline": "The government caps jet fuel prices and opens an emergency fund for carriers. It will stabilize domestic fares, but the India-US corridor remains on track for its most expensive summer in a decade.",
    "slug": make_slug("india-10000-crore-airline-fuel-fund-nri-fares"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Fund stabilizes domestic Indian fares (post-landing travel for NRIs), but international routes — especially India-US — will keep climbing; summer and Diwali bookings should be locked in now.",
    "tags": ["travel", "airlines", "jet-fuel", "india-government", "fares", "iran-war"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national/airlines-aid-fund-jet-fuel-price-cap-iran-war-impact-133853834.html"},
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/india-jet-fuel-prices-june-2026/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/global-airline-chiefs-confront-iran-war-fuel-shock-industry-summit-2026-06-04/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/16108906/pexels-photo-16108906.jpeg",
    "image_caption": "Ground crew servicing a commercial aircraft on the tarmac",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ── INSERT ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
