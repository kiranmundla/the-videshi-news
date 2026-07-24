#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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
        "headline": "Air New Zealand Is Finally Studying a Nonstop to India — but the Diaspora Shouldn't Hold Its Breath Until 2028",
        "subheadline": "A Bengaluru-born CEO, a fresh free-trade deal and 80,000 Indian visitors a year are pushing Auckland toward a Delhi or Mumbai nonstop — yet the aircraft to fly it don't arrive until the end of the decade.",
        "slug": make_slug("air-new-zealand-india-nonstop-flight-evaluation-auckland-delhi-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the growing Indian community in New Zealand and the NRIs who shuttle between the two countries for family, study and business, a nonstop would finally cut out the Singapore or Sydney layover that adds a half-day to every trip home.",
        "tags": ["travel", "airlines", "air new zealand", "air india", "new zealand"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/india-new-zealand-direct-flights-could-soon-take-off"},
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/air-new-zealand-evaluating-direct-flights-to-india-says-ceo-nikhil-ravishankar/"},
            {"name": "FlightGlobal", "url": "https://www.flightglobal.com/airlines/direct-new-zealand-india-flights-on-the-cards-under-air-nz-air-india-partnership/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Auckland_Skyline_from_Mission_Bay.jpg/1280px-Auckland_Skyline_from_Mission_Bay.jpg",
        "image_caption": "Auckland's skyline seen from Mission Bay; the city would be the New Zealand hub for any future nonstop to India.",
        "image_attribution": "Wikimedia Commons",
        "body": """Air New Zealand has confirmed it is actively studying nonstop flights to India, a route the carrier has flirted with for years but never flown. Chief executive Nikhil Ravishankar — himself born in Bengaluru and raised in New Zealand from age 14 — told reporters the airline is evaluating the feasibility of direct service to a major Indian city, with an operational target of late 2028.

For now, that is a study, not a schedule. But it is the most concrete the plan has ever been, and it sits on top of three forces that are unlikely to reverse: a fast-growing Indian diaspora, deepening business ties, and a recently concluded free-trade agreement between the two countries.

## What is actually on the table

The groundwork was laid in March 2025, when Air New Zealand and Air India — both Star Alliance members — signed a memorandum of understanding and extended their codeshare to 16 routes spanning India, Singapore, Australia and New Zealand. Under that arrangement, travellers can already book a single Air India ticket from Delhi, Mumbai, Bengaluru or Chennai and connect onto Air New Zealand metal at Singapore, Sydney or Melbourne for the final leg to Auckland, Christchurch, Wellington or Queenstown.

The MoU also committed both carriers to "explore the introduction of a direct service" by the end of 2028 — explicitly conditional on new aircraft deliveries and regulatory approvals. That conditionality is the catch. A nonstop Auckland–Delhi flight runs roughly 15 to 16 hours, ultra-long-haul territory that demands the right widebody. Air New Zealand's incoming Boeing 787-9s are the obvious candidate, but the delivery timeline is exactly what pins the target to 2028 rather than next summer.

## Why the math is starting to work

New Zealand tourism data shows more than 80,000 travellers arrived from India in the most recent count — a 23 percent jump over pre-pandemic 2019. Auckland is the presumed New Zealand hub, with the Indian end most likely Delhi or Mumbai. Ravishankar has been blunt that India is "a key growth market," and the airline has already been quietly building toward it: in May it added a Singapore–Christchurch service three days a week, opening up the South Island for Indian travellers routing through Singapore and adding more than 34,000 seats over the peak season.

That incremental capacity is the tell. Carriers rarely jump straight to a 16-hour nonstop; they thicken the connecting flows first, watch the load factors, and only then commit metal to a direct route. The codeshare is functioning as a live market test.

## What it means for the diaspora

For the roughly quarter-million people of Indian origin in New Zealand — and the students, who form one of the fastest-growing visitor categories — the current reality is a one-stop journey via Singapore, Sydney or Melbourne that adds the better part of a day in each direction. A nonstop would collapse that into a single 16-hour hop, the difference between landing in Auckland tired and landing wrecked after a midnight connection.

It also matters for the NRIs in Australia, the US and the Gulf who tack a New Zealand leg onto a trip home. Better Auckland connectivity through Singapore — already live — makes a Christchurch-and-Queenstown add-on far less painful than it was a year ago, even before any nonstop materialises.

A word of realism: there is a difference between an MoU clause and a confirmed launch. The 2028 target has been restated several times without ever firming into a sale date, and "subject to aircraft availability and regulatory approval" is doing a lot of work. The India–New Zealand FTA and the diaspora numbers make the route more plausible than it has ever been, but anyone planning a trip in the next two years should still budget for a connection.

## What's next

Watch three signals. First, aircraft: confirmed 787-9 delivery slots are the precondition for everything else. Second, capacity creep on the connecting routes — if the Singapore and Australian flows keep growing, a nonstop becomes easier to justify. Third, regulatory and bilateral air-services approvals, which tend to move quietly until they don't. If all three line up, the diaspora's "someday" nonstop to India could become a booking by the end of the decade — but not, on current evidence, before it.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Rewrote Its Permit Rules for Western Rajasthan — and Wrote OCI Cardholders Into the Law for the First Time",
        "subheadline": "The Immigration and Foreigners (Amendment) Order, 2026 redraws the protected-area map across six border districts, but carves out the tourist circuit NRIs actually visit — and finally defines where OCI holders stand.",
        "slug": make_slug("india-immigration-foreigners-amendment-order-2026-oci-rajasthan-protected-areas-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Millions of OCI cardholders now have a legal definition inside India's immigration code for the first time, and NRI families planning a Jaisalmer desert trip need to know which corners of the Thar still require a permit and which are explicitly open.",
        "tags": ["travel", "visa", "OCI", "rajasthan", "permits", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SCC Times", "url": "https://www.scconline.com/blog/post/2026/06/20/immigration-foreigners-amendment-order-2026-explained/"},
            {"name": "Ministry of Home Affairs (notification, 18 June 2026)", "url": "https://www.mha.gov.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Jaisalmer_Fort%2C_India.jpg/1280px-Jaisalmer_Fort%2C_India.jpg",
        "image_caption": "Jaisalmer Fort in western Rajasthan; the city's municipal area is explicitly exempt from the redrawn protected-area restrictions.",
        "image_attribution": "Wikimedia Commons",
        "body": """On 18 June 2026, India's Ministry of Home Affairs notified the Immigration and Foreigners (Amendment) Order, 2026 — a dry-sounding document with two changes that matter to the diaspora. It writes "Overseas Citizen of India (OCI) Cardholder" into the immigration code for the first time, and it completely redraws the protected-area map across western Rajasthan, the heart of the Thar Desert tourist circuit.

The amendment modifies the Immigration and Foreigners Order, 2025, India's overhauled framework for foreign nationals. For NRIs, the headline is less about new restrictions than about clarity — and a permit map that has long confused families planning a desert trip just got redrawn.

## OCI holders, finally, in the text

Until now, OCI cardholders occupied an awkward space in immigration law: a category everyone used but the code never properly defined. The amendment formally inserts the term and aligns its definition with the Citizenship Act, 1955. That sounds technical, but it removes ambiguity at exactly the points where it bites — at FRRO offices, at protected-area checkpoints, and in the fine print of who needs what permit.

It is not a loosening of OCI privileges, and it does not touch the separate, already-tightened OCI rules on passport re-issue and the activities (journalism, missionary work, research) that still need prior FRRO permission. What it does is give OCI holders a fixed legal identity inside the immigration order, so the rules that reference them now have a clear subject.

The amendment also adds procedural flexibility: authorities can now permit movement either with or without a permit depending on the situation, rather than applying a single blanket rule. That discretion cuts both ways, but in tourism-friendly zones it is designed to ease access.

## The Rajasthan redraw

The most significant change is a complete revision of the Third Schedule covering Rajasthan. The order identifies protected areas across six border districts — Jaisalmer, Bikaner, Sriganganagar, Barmer, Phalodi and Jalore — defined either as entire tehsils (sub-districts) or as specific regions lying west of major highways such as NH-11, NH-62 and NH-68.

That is the restriction. The exemptions are what travellers should memorise:

- **National highway corridors** along NH-11, NH-62 and NH-68 are excluded from the restrictions.
- **The municipal areas of major towns are open**, including Jaisalmer, Bikaner, Barmer, Sriganganagar, Phalodi and Pokaran.
- **The marquee tourist sites stay open** — Sam dunes, Kuldhara, Amarsagar, Khuri, and the desert safari and camping zones around them.
- A **500-metre corridor** along the roads leading to those tourist spots is also carved out of the protected zone.

In plain terms: the classic NRI itinerary — fly or train into Jaisalmer, tour the fort, drive out to the Sam dunes for a sunset camel safari and a night in a desert camp — sits squarely inside the exempt areas. The restrictions bite only if you venture off the highway corridors into the genuine border interior, which most family trips never do.

## What it means for the diaspora

For OCI families, the practical effect is reassurance rather than disruption. The desert circuit you came for is explicitly protected as open, and your legal status as an OCI holder is now spelled out rather than inferred. The catch is geography: if your plans include remote border villages west of the named highways, you may still need a permit, and the safest move is to route any off-road desert excursion through a registered local operator who knows exactly where the protected line falls.

It is also a reminder that foreign passport holders without OCI status face a different regime. Standard foreign nationals continue to deal with Protected Area Permit and Restricted Area Permit rules elsewhere in the country, and those have not been relaxed by this order.

## What's next

The amendment is in force now. NRIs with a Rajasthan trip on the calendar should carry their OCI card and passport, stick to the highway-and-tourist corridors that the order names as exempt, and confirm permit needs with a registered Jaisalmer operator before heading anywhere near the border interior. For the vast majority of diaspora desert trips, the answer is simpler than it sounds: the Thar you came to see is open.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air Canada Just Made Vancouver–Delhi a Year-Round Nonstop — and the West Coast Diaspora Gets a Third Canadian Gateway Home",
        "subheadline": "The Dreamliner route that started as a seasonal experiment in 2016 now flies all twelve months, part of a $1.5 billion bet on Canada–India traffic that already includes year-round Toronto nonstops to both Delhi and Mumbai.",
        "slug": make_slug("air-canada-vancouver-delhi-year-round-nonstop-west-coast-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the large Punjabi and South Asian community across British Columbia and the US Pacific Northwest, a year-round Vancouver nonstop means no more winter detours through Toronto or a Gulf hub just to reach Delhi for a family wedding or a December trip home.",
        "tags": ["travel", "airlines", "air canada", "vancouver", "delhi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "PAX News", "url": "https://www.paxnews.com/news/airlines/air-canada-vancouver-delhi-service-becomes-year-round-june-8"},
            {"name": "TTR Weekly", "url": "https://www.ttrweekly.com/site/2026/03/air-canada-adds-flights-to-india/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Vancouver_Skyline_and_Mountains.jpg/1280px-Vancouver_Skyline_and_Mountains.jpg",
        "image_caption": "Vancouver's skyline and the North Shore mountains; Air Canada's Vancouver–Delhi Dreamliner route now operates year-round.",
        "image_attribution": "Wikimedia Commons",
        "body": """Air Canada has turned its Vancouver–Delhi nonstop into a year-round route, ending the route's run as a seasonal-only service and giving the West Coast diaspora a third permanent Canadian gateway to India.

The flight, operated with Boeing 787-9 Dreamliners, first launched in October 2016 as a seasonal experiment. It became year-round on June 8, with flights now on sale for travel across all twelve months. Benjamin Smith, Air Canada's president of passenger airlines, called the response to the route "extremely positive."

## Three year-round routes, $1.5 billion

The Vancouver upgrade is the third piece of a deliberate build-out. Air Canada now runs year-round nonstops to India from both Toronto — to Delhi and to Mumbai — and Vancouver, three permanent routes launched within the last two and a half years. The carrier says it is committing close to $1.5 billion worth of aircraft between Canada and India, a figure that signals this is a structural bet on the market rather than opportunistic capacity.

That bet has been tested under stress. Earlier this year, disruption from the conflict in the Middle East and the resulting airspace closures pushed Air Canada to temporarily double its Toronto–Delhi service to two flights a day in March, deploying ultra-long-haul Boeing 777-200LRs to absorb passengers displaced by other carriers' cancellations. The Vancouver move is the opposite kind of decision — not a crisis response, but a permanent commitment based on demand that held up year after year.

## Why Vancouver matters

Vancouver is the natural gateway for the South Asian community of British Columbia, one of the densest concentrations of people of Indian origin anywhere in North America, and for travellers across the US Pacific Northwest — Seattle, Portland — who would otherwise backtrack east to Toronto or route through a Gulf hub to reach Delhi.

Until now, the seasonal nature of the route created a recurring headache: the nonstop was there for summer travel but vanished for the winter holidays, exactly when families fly to India for weddings and December trips home. Travellers who missed the seasonal window were pushed onto one-stop itineraries via Toronto, a European hub, or the Gulf, adding hours and a connection to an already long journey. A year-round schedule removes that gap entirely.

The Dreamliner cabin helps the case. The 787-9 offers a three-class layout with lie-flat business seats and premium economy, and the type's higher cabin humidity and lower cabin altitude make the roughly 15-hour Pacific-and-polar routing more bearable than older widebodies. For families travelling with elderly parents or young children, the difference between a nonstop and a one-stop is not just time — it is one less set of security lines, gate changes and the risk of a missed connection with checked bags.

## The connecting picture

Air Canada has also been thickening the feed around its India routes. The carrier recently expanded an interline and partnership framework with WestJet that lets Air India and Air Canada passengers connect onward to more than 30 cities across North America, including 14 in the US. For a diaspora traveller landing at Vancouver or Toronto, that web of onward connections matters as much as the long-haul leg itself.

A note of caution familiar to any frequent flyer: schedules and frequencies can shift, and award availability on these routes — particularly in business class over the December peak — disappears fast. Aeroplan redemptions on India routes exist but are priced steeply, so travellers chasing points should book early.

## What's next

The immediate takeaway is simple: Vancouver–Delhi is now a booking you can make for any month of the year, including the winter holiday window that used to force a detour. West Coast NRIs planning a December trip home should lock in fares early, watch for the premium-economy sweet spot on the Dreamliner, and weigh the WestJet connections if the journey starts beyond Vancouver. With three year-round routes and a billion-and-a-half-dollar fleet commitment behind them, Air Canada has made clear it intends to keep flying the diaspora home.
"""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
