#!/usr/bin/env python3
"""Travel writer — 2026-07-14 10:01 PT"""

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
    # ── Article 1: United Airlines SFO-DEL / SFO-BLR rumored nonstops ──
    {
        "id": str(uuid.uuid4()),
        "headline": "United Airlines Eyes Nonstop Flights From San Francisco to Delhi and Bangalore",
        "subheadline": "The rumored ultra-long-haul routes would give Bay Area's half-million Indian Americans their first US carrier option to India's tech capital — and could become among the most profitable flights in aviation.",
        "slug": make_slug("united-airlines-sfo-delhi-bangalore-nonstop-flights-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "Bay Area is home to over 400,000 Indian Americans — many of them tech professionals who shuttle between Silicon Valley and Bangalore. A United nonstop on SFO-BLR would end decades of inconvenient one-stop itineraries via the Gulf or Europe for this corridor.",
        "tags": ["travel", "airlines", "aviation", "united-airlines", "silicon-valley", "bangalore"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying", "url": "https://simpleflying.com/why-rumored-united-airlines-ultra-long-haul-flight-among-most-profitable-routes-aviation/"},
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/07/12/emirates-set-to-launch-airbus-a380-flights-to-hyderabad/"},
            {"name": "United Airlines", "url": "https://www.united.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/N2749U%40PEK_%2820211130144100%29.jpg/1280px-N2749U%40PEK_%2820211130144100%29.jpg",
        "image_caption": "A United Airlines Boeing 787 Dreamliner, the aircraft type expected to operate the rumored India routes",
        "image_attribution": "Wikimedia Commons",
        "body": """Industry chatter about United Airlines launching nonstop service between San Francisco and two major Indian cities — Delhi and Bangalore — has moved from idle speculation to serious analysis. Aviation economists now believe the routes could become among the most profitable in the carrier's long-haul network, driven by an unusual convergence of corporate travel demand, diaspora spending power, and a widening gap in direct connectivity.

## The Routes on the Table

The proposed flights would cover staggering distances. San Francisco to Delhi spans roughly 7,700 miles, while San Francisco to Bangalore stretches to about 8,700 miles — placing it within striking distance of Qantas's famously grueling Perth-to-London service. Both would rank among the longest routes in United's global network and push the Boeing 787 Dreamliner's range capabilities close to their limit.

Currently, United operates just one US-India route: Newark to Delhi, a service running since 2005. The airline briefly flew Chicago O'Hare to Delhi between 2020 and 2023 before pulling the plug. A San Francisco hub would open the airline's third US gateway to India — and its first on the West Coast.

## Why Bangalore Is the Real Prize

Delhi is the obvious candidate: India's busiest airport, the largest Star Alliance hub in the country, and geographically closer than most Indian cities. But the sharper commercial opportunity may be Bangalore.

Booking data for the twelve months through October 2025 show that approximately 156,000 round-trip passengers flew between San Francisco and Bangalore, paying an average one-way fare of $1,600 across all cabin classes. Only about a quarter of those travelers used Air India's direct service, which was suspended in February 2026 due to aircraft availability constraints. The rest routed through Dubai, Singapore, London, or Frankfurt — adding six to ten hours of travel time and padding the pockets of Gulf and European carriers.

The demand is structural, not seasonal. Silicon Valley and Bangalore are the twin poles of the global technology industry, linked by AI research, venture capital pipelines, and thousands of corporate contracts that generate predictable, year-round business travel. United is strategically positioning for this with its new "Elevated" Polaris cabin, featuring 64 lie-flat business class seats on the 787-9 — a configuration that tilts heavily toward the premium revenue that makes ultra-long-haul economics work.

## The Competition Is Circling

United is hardly alone in spotting the opportunity. American Airlines resumed JFK-Delhi service in 2021 and had planned a Seattle-Bangalore route before shelving it indefinitely due to airspace closures from geopolitical conflicts. Delta, which pulled out of India entirely in 2020, has signed a memorandum of understanding with IndiGo and announced plans for an Atlanta-Delhi service, though no launch date has been set.

From the Indian side, Air India's San Francisco services — once covering Delhi, Mumbai, and Bangalore — have contracted sharply. The Delhi flight now stops in Kolkata due to airspace restrictions. IndiGo, India's largest carrier, has 60 Airbus A350-900s on order from 2027, but as a low-cost airline it may lack the premium cabin infrastructure to make these distances profitable.

## What It Means for NRIs

For the estimated 400,000-plus Indian Americans in the Bay Area, a United nonstop to Bangalore would be transformative. The current options — connecting through Middle Eastern or European hubs, or relying on Air India's inconsistent schedule — add complexity, jet lag, and expense to what is already a 15-plus-hour journey.

A direct SFO-BLR flight would cut total travel time by six to eight hours for the vast majority of passengers currently connecting. It would also give tech workers a Star Alliance alternative to Air India, with United's MileagePlus loyalty program and corporate contracts providing seamless integration with domestic US travel.

The Delhi route matters too. Northern India's diaspora — Punjabis, UP communities, Delhiites — are concentrated in the Bay Area and Central Valley in large numbers. Combined, the two routes would make SFO the most connected US airport to India by a significant margin.

No official launch date has been announced, and airspace restrictions over parts of Central Asia remain a complicating factor. But with demand data this strong and competitors positioning aggressively, the question for United may be less *whether* and more *when*.""",
    },

    # ── Article 2: Phu Quoc boat tragedy ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Fifteen Indian Tourists Killed in Vietnam Speedboat Capsize — What NRIs Need to Know",
        "subheadline": "A corporate incentive trip to Phu Quoc Island turned fatal when a packed speedboat overturned in rough seas, exposing dangerous gaps in Southeast Asia's maritime safety enforcement.",
        "slug": make_slug("phu-quoc-vietnam-boat-capsize-indian-tourists-killed-travel-safety"),
        "category": "travel",
        "vertical": "travel-safety",
        "diaspora_angle": "Southeast Asia has become the fastest-growing vacation destination for Indian travelers, with Vietnam alone seeing Indian tourist arrivals surge in recent years. This tragedy is a direct safety warning for the millions of NRIs and India-based travelers booking island-hopping excursions across the region.",
        "tags": ["travel", "safety", "vietnam", "southeast-asia", "phu-quoc", "travel-advisory"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/boat-carrying-tourists-capsizes-off-vietnams-phu-quoc-island-killing-15-2026-07-12/"},
            {"name": "CNN", "url": "https://www.cnn.com/2026/07/12/asia/vietnam-phu-quoc-boat-capsizes-intl/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/0knv4akekiba/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/adventure/phu-quoc-island-boat-tragedy-essential-safety-tips-before-boarding-tourist-boat"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12198347/pexels-photo-12198347.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Tourist boats off the coast of Phu Quoc Island, Vietnam — a destination increasingly popular with Indian travelers",
        "image_attribution": "Pexels",
        "body": """At least fifteen Indian tourists died on Saturday when a speedboat capsized in rough waters off Vietnam's Phu Quoc Island, turning what was meant to be a corporate rewards trip into one of the deadliest tourist boat accidents involving Indian nationals in recent years.

## What Happened

The speedboat, registered as AG 26751 and operated by the Ocean Pearl Island Company, was carrying 32 Indian tourists and four Vietnamese crew members on a return trip from Hon May Rut Island to An Thoi Port. The vessel overturned approximately 400 meters from the shoreline of Hon May Rut Ngoai Island at around 1 PM local time on Saturday.

The passengers were employees of the Indian smartphone brand Lava, traveling on a corporate incentive trip. Most of the group hailed from Tamil Nadu, Andhra Pradesh, Telangana, and Kerala — states with significant overseas populations. Of the 36 people on board, 21 survived, including all four crew members. Fifteen Indian nationals — 13 men and two women — were confirmed dead. Two survivors remain in critical condition.

Witnesses described choppy seas and large waves at the time of the accident. The speedboat was a closed-hull vessel, meaning several passengers became trapped inside after the boat flipped. Rescue boats arriving within minutes found that "only a few people were brought out conscious," according to a nearby boat operator who joined the effort.

## The Emergency Response

The Vietnamese government deployed a large-scale rescue operation involving border guards, the navy, the coast guard, and civilian boats. The Vietnamese Prime Minister ordered criminal investigations into the operating company, a nationwide inspection of all tourist speedboats and safety equipment, and direct coordination with India's diplomatic mission.

On the Indian side, Prime Minister Narendra Modi issued a statement of condolence. The Indian Ambassador traveled to Phu Quoc to oversee consular assistance. The Embassy of India in Hanoi established emergency control rooms in both Ho Chi Minh City and Hanoi:

- Ho Chi Minh City: +84 36 281 7930, +84 91 552 3714, +84 33 452 0414
- Hanoi: +84 91 308 9165

State governments in Tamil Nadu, Andhra Pradesh, Telangana, and Kerala have set up dedicated desks to assist with repatriation paperwork and family logistics. The remains of the 15 victims have been transported to Ho Chi Minh City for repatriation to India.

## A Pattern Across Southeast Asia

The Phu Quoc disaster is not an isolated incident. Across Southeast Asia's booming maritime tourism corridors — from Thailand's Phuket and Koh Samui to Indonesia's Bali and Lombok — speedboat and ferry accidents involving tourists have been a recurring problem. The common thread: soaring international visitor numbers outpacing local safety enforcement.

Vietnam maintains a Level 1 travel advisory from the US State Department ("Exercise Normal Precautions"), but the department's own safety assessment notes that "ground and water transportation lack safety regulations" and standards "vary greatly from company to company and province to province." The UK's Foreign Office specifically warns travelers to "check with your tour guide about the safety record and registration of boats."

## What Indian Travelers Should Do

For the millions of Indians — both NRIs and India-based — booking Southeast Asian holidays each year, the tragedy underscores a set of precautions that are easy to overlook in the excitement of an island vacation:

**Before booking:** Research the tour operator's safety record. Licensed, established operators with online reviews are preferable to unnamed outfits arranged through hotel desks. Ask specifically about vessel maintenance schedules and crew certifications.

**Before boarding:** Check weather conditions independently. Rough seas and high winds are grounds to postpone, regardless of what the operator says. Refuse to board overcrowded vessels — if every seat is full and luggage is piled high, the boat is likely at or over capacity.

**On the boat:** Wear the life jacket for the entire journey, not just during the safety briefing. On closed-hull speedboats, note where emergency exits are. Keep your phone in a waterproof pouch with emergency numbers saved offline.

**Insurance:** Verify that your travel insurance explicitly covers recreational boat excursions, emergency medical evacuation, and repatriation. Many standard policies exclude water activities unless specifically added.

Vietnam remains a stunning and generally safe destination. Phu Quoc's beaches, its night markets, and its snorkeling reefs draw visitors for good reason. But the waters around any island destination deserve the same caution you would give to any other adventure activity — because when things go wrong on the open sea, help is measured in minutes, not seconds.""",
    },

    # ── Article 3: Emirates A380 to Hyderabad ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Emirates Plans to Deploy Its A380 Superjumbo on Hyderabad Route After 25 Years in the City",
        "subheadline": "Telangana's chief minister pitched MRO investments and expanded frequencies as the Dubai carrier proposes its flagship double-decker for one of India's fastest-growing tech corridors.",
        "slug": make_slug("emirates-a380-hyderabad-telangana-aviation-hub-nri"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "Hyderabad is the fourth-largest source of Indian immigrants to the US, with a massive Telugu-speaking community concentrated in the tech corridors of New Jersey, Texas, and the Bay Area. An A380 on the Hyderabad-Dubai route would dramatically increase seat capacity on a key NRI travel corridor, particularly for connecting flights onward to the US.",
        "tags": ["travel", "airlines", "emirates", "hyderabad", "telangana", "a380"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/07/12/emirates-set-to-launch-airbus-a380-flights-to-hyderabad/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/09/A6-EDY_A380_Emirates_31_jan_2013_jfk_%288442269364%29_%28cropped%29.jpg",
        "image_caption": "An Emirates Airbus A380 — the world's largest passenger aircraft that could soon fly the Hyderabad-Dubai route",
        "image_attribution": "Wikimedia Commons",
        "body": """Emirates has proposed deploying its flagship Airbus A380 — the world's largest passenger aircraft — on flights to Hyderabad, a move that would significantly expand capacity on one of India's most important Gulf corridors and mark a milestone in the airline's quarter-century relationship with the city.

## The Proposal

The plan was floated during a meeting between Mohammed Sarhan, Emirates' Vice-President for India, and Telangana Chief Minister A. Revanth Reddy on Saturday. The discussions covered not just the A380 deployment but also increased flight frequencies from Rajiv Gandhi International Airport, MRO (Maintenance, Repair, and Overhaul) investments in Telangana, and broader cooperation extending beyond aviation.

Emirates currently operates Boeing 777 aircraft on its Hyderabad services. Upgrading to the A380 — a double-decker with up to 615 seats in a two-class configuration, or around 489 in Emirates' standard three-class layout — would roughly double the number of passengers the airline can carry on each departure.

## Why Hyderabad Matters

The timing is deliberate. Hyderabad has emerged as India's second tech city after Bangalore, home to major campuses for Microsoft, Google, Amazon, and dozens of Indian IT firms. Its airport has seen international passenger traffic grow steadily, driven by both business travel and the enormous Gulf-bound labor and diaspora traffic that has defined Hyderabad's aviation market for decades.

For Emirates, Hyderabad has been a consistent performer. The airline has served the city for 25 years — a tenure that predates the current Rajiv Gandhi International Airport, which opened in 2008. The anniversary provides a natural occasion to upgrade the service, and the A380 is Emirates' calling card: a visible statement of route importance that the airline has deployed to Delhi and Mumbai but not yet to India's southern tech capitals.

Chief Minister Revanth Reddy welcomed the proposal and pushed for more. He invited Emirates to establish MRO facilities at two proposed airports in Warangal and Adilabad, part of Telangana's broader strategy to position itself as an aviation hub. MRO is a high-value segment of the aviation industry — airlines worldwide spend billions annually on aircraft maintenance — and attracting a player like Emirates would bring jobs, technical expertise, and international credibility.

Sarhan also indicated the airline's willingness to sponsor training programs for athletes at Hyderabad's Gachibowli Sports University, a small but notable gesture that signals Emirates' interest in deepening its presence in the state beyond flying routes.

## The NRI Connection

For the Telugu diaspora — one of the largest and fastest-growing Indian-origin communities in the United States — the A380 upgrade would be more than symbolic. Hyderabad-to-Dubai is not just a point-to-point market. It is one of the most important connecting corridors for NRIs traveling between the US and South India.

Emirates' Dubai hub serves as the primary transit point for travelers connecting from US cities like Houston, Dallas, New York JFK, San Francisco, and Chicago to Hyderabad. The airline's extensive US network — currently covering 12 American gateways — funnels through Dubai, making the Hyderabad-Dubai leg a critical bottleneck in the journey.

More A380 seats on this leg means fewer sold-out flights during peak travel windows: Diwali, Christmas, Sankranti, and the summer holidays when NRI families flood homebound routes. It also means more premium cabin availability. The Emirates A380 features its signature first-class suites, a dedicated onboard lounge, and a shower spa — amenities that the 777, while comfortable, does not match.

The deployment would also come with improved cargo capacity. The A380's belly hold can carry significantly more freight than the 777, benefiting Hyderabad's pharmaceutical export industry — the city is India's bulk drug capital — and the steady flow of NRI-bound packages that move through Dubai.

## When Could It Happen?

No specific timeline has been announced. Emirates typically conducts extensive route analysis before committing an A380, evaluating not just passenger demand but also airport infrastructure — the A380 requires specific gate and runway configurations. Rajiv Gandhi International Airport already handles A380 operations (it has received the aircraft on special occasions), so the infrastructure bar is likely already cleared.

If the deployment moves forward, Hyderabad would join Delhi and Mumbai as the third Indian city with regular A380 service — a recognition of the city's growing importance in India's aviation landscape and a tangible benefit for the hundreds of thousands of Telugu NRIs who consider the Hyderabad-Dubai leg a familiar, if often frustrating, part of every trip home.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline'][:80]}...")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
