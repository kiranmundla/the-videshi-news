#!/usr/bin/env python3
"""Travel writer — 2026-06-10 02:00 UTC run"""
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
    # ── ARTICLE 1: SWISS Zurich-Bengaluru ──
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Is Launching Nonstop Zurich-Bengaluru Flights — and NRIs in Europe Just Got a Direct Line Home",
        "subheadline": "Five-times-weekly A350 service starts in October, with First Class on every flight and onward connections across Europe and North America through the Lufthansa Group hub.",
        "slug": make_slug("swiss-zurich-bengaluru-nonstop-nri-europe-tech"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "Tens of thousands of Indian tech professionals across Switzerland, Germany, and wider Europe have long relied on Gulf-hub connections or Lufthansa via Frankfurt/Munich to reach southern India. SWISS's direct Zurich-Bengaluru link cuts that to a single nine-hour hop — and the Lufthansa Group's onward network means NRIs in Amsterdam, Vienna, or Copenhagen can now book a single-ticket itinerary home through Zurich without touching Dubai.",
        "tags": ["travel", "airlines", "europe", "bengaluru", "swiss", "lufthansa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Swiss International Air Lines", "url": "https://www.swiss.com"},
            {"name": "LatestLY / ANI", "url": "https://www.latestly.com/agency-news/india-news-swiss-international-airlines-to-launch-nonstop-bengaluru-zurich-flights-from-october-6800972.html"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/05/19/swiss-launching-new-a350-flights-bengaluru/"},
            {"name": "iamexpat.ch", "url": "https://www.iamexpat.ch/expat-info/swiss-news/new-swiss-route-connects-switzerland-indias-tech-capital"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Swiss.a321-112.hb-ioh.750pix.jpg",
        "image_caption": "A Swiss International Air Lines A321 on the tarmac",
        "image_attribution": "Wikimedia Commons",
        "body": """Swiss International Air Lines will begin flying nonstop between Zurich and Bengaluru five times a week from October 25, making India's technology capital the airline's third Indian destination after Delhi and Mumbai. The move plugs a gap that Indian professionals across Europe have felt for years: until now, reaching southern India on a premium European carrier meant either routing through a Gulf hub or connecting via Frankfurt or Munich on Lufthansa.

## What SWISS Is Offering

The eastbound LX 140 departs Zurich daily — except Mondays and Wednesdays — at 13:20, landing in Bengaluru around 02:55 the next morning. The return LX 141 leaves Bengaluru at 04:50 and touches down in Zurich by 10:50 the same day. Flight time is roughly nine hours each way.

SWISS will deploy its long-haul fleet on the route, and every flight will carry First Class, Business, and Economy cabins. That's a meaningful differentiator: the only other European carriers offering direct Bengaluru service are Lufthansa (Frankfurt and Munich) and a handful of seasonal charters.

SWISS CEO Jens Fehlinger framed the route as demand-driven, not aspirational. "India's technology capital appeals to both leisure and business travelers and serves as a strong gateway for exploring southern India," he said in the airline's announcement. Kevin Markette, Lufthansa Group's Senior Director for South Asia, added that the new service makes Zurich the group's third gateway from Bengaluru — joining Frankfurt and Munich — and "significantly enhances connectivity for travellers from southern India."

## Why This Matters for NRIs

Bengaluru is not just another pin on a route map. It is the administrative heart of Karnataka, home state to an estimated 400,000-plus Kannadigas in the United States alone and tens of thousands more across Switzerland, Germany, the Netherlands, and the UK. For this community, a direct European link to Kempegowda International Airport eliminates the Dubai or Doha layover that has been the default for decades.

The practical upside is significant. A single-ticket Zurich connection opens seamless routing from dozens of European cities — Amsterdam, Vienna, Copenhagen, Brussels, Geneva — without the passport-control detour of a Gulf transit. For families with children or elderly parents, that's one fewer airport, one fewer security line, and roughly four fewer hours in transit.

The timing matters too. SWISS's winter schedule runs October 25 through March 27 — peak season for NRI trips home, covering Diwali, Christmas, and the January wedding circuit. Bookings opened on May 19 through swiss.com and travel agency partners.

## The Bigger Picture: Europe's India Bet

SWISS isn't acting alone. The Lufthansa Group has been quietly building out its India network for two years. Frankfurt and Munich already serve Bengaluru, Delhi, and Mumbai. Air India, freshly recapitalized under Tata ownership, has been adding European capacity. And British Airways, Virgin Atlantic, and Air France-KLM have all expanded or announced India routes in 2025-26.

The driver is straightforward: India's outbound travel market is growing at roughly 15% annually, and the tech corridor between Bengaluru and Europe's financial and corporate centers — Zurich, Frankfurt, London, Amsterdam — is one of the highest-yield segments in the business. Bengaluru's airport handled over 37 million passengers last year, and Girish Nair, COO of Bangalore International Airport Limited, called the SWISS launch "a strong validation of the market maturity and long-term potential that Bengaluru continues to demonstrate."

For NRIs weighing their winter travel options, the calculus just shifted. A direct European flight with First Class service, single-ticket connections across the continent, and arrival times that sync with Indian business hours is no longer a Gulf-carrier monopoly. SWISS just gave southern India's diaspora a credible alternative — and the Lufthansa Group's network makes sure it connects to everywhere they actually live."""
    },

    # ── ARTICLE 2: flyadeal Riyadh-Hyderabad ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Saudi Arabia's Budget Airline Just Picked Hyderabad as Its Gateway to India — and Three Million Gulf NRIs Should Pay Attention",
        "subheadline": "flyadeal will fly daily nonstop between Riyadh and Hyderabad from July 1, its first scheduled Indian route, with a second Indian city planned soon.",
        "slug": make_slug("flyadeal-riyadh-hyderabad-gulf-nri-budget"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "Over three million Indians live and work in Saudi Arabia, the largest Indian diaspora community in the Gulf. Hyderabad is the most common origin city for this population. flyadeal's budget pricing on the Riyadh-Hyderabad route directly undercuts full-service Gulf carriers and gives working-class NRIs — construction workers, IT staff, nurses, retail employees — a cheaper path home.",
        "tags": ["travel", "airlines", "saudi-arabia", "hyderabad", "gulf", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/saudi-arabia-joins-india-uae-qatar-bahrain-travel-markets-flyadeal-riyadh-hyderabad-flights/"},
            {"name": "Channel I AM", "url": "https://en.channeliam.com/2026/06/02/flyadeal-starts-india-flights/"},
            {"name": "Pravasi Samwad", "url": "https://pravasisamwad.com/saudi-budget-airline-flyadeal-launches-first-scheduled-india-service-with-hyderabad-route/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/92/Flyadeal.jpg",
        "image_caption": "A flyadeal aircraft at a Saudi Arabian airport",
        "image_attribution": "Wikimedia Commons",
        "body": """Saudi Arabia's low-cost carrier flyadeal will begin daily nonstop flights between Riyadh and Hyderabad on July 1, marking its first scheduled passenger service to India. The airline, a subsidiary of the Saudia Group, has operated charter flights for Hajj and Umrah pilgrims before, but this is a different play: a permanent, year-round budget route aimed squarely at the millions of Indians who live, work, and transit through the Kingdom.

## The Route Details

flyadeal will deploy Airbus A320neo aircraft configured with 186 all-economy seats on the Riyadh–Hyderabad sector. The flight covers roughly 3,400 kilometers in about five hours eastbound. Service will be daily from day one — an aggressive frequency for a launch route, signaling that the airline expects the seats to fill.

Acting CEO Sanjiv Kapoor — a veteran of Indian aviation who previously led Vistara and SpiceJet — described Hyderabad as "the first step in the airline's planned expansion into India." He confirmed that a second Indian destination will be announced soon, though he did not name the city. Delhi and Mumbai are the obvious candidates, but Kochi and Chennai — both major Gulf labor corridors — are also in the frame.

## Why Hyderabad First

The choice is not accidental. Hyderabad has the deepest ties to Saudi Arabia of any Indian metro. The Telangana capital is the single largest source of Indian workers in the Kingdom, spanning IT professionals, healthcare workers, construction laborers, and hospitality staff. Rajiv Gandhi International Airport already handles heavy Gulf traffic, with Air India, IndiGo, and full-service Gulf carriers like Saudi Arabian Airlines, Emirates, and Qatar Airways all serving Middle Eastern routes from the city.

What flyadeal brings is price. As a low-cost carrier, its fares are expected to undercut the legacy airlines by a meaningful margin. For the working-class diaspora — the electricians, drivers, nurses, and shop assistants who make up the bulk of India's Gulf workforce — the difference between a ₹25,000 ticket and a ₹15,000 ticket is the difference between one trip home a year and two. That math matters to millions of families.

## The Saudi Aviation Push

flyadeal's India entry is part of a much larger Saudi strategy. The Kingdom is spending over $100 billion on aviation infrastructure as part of Vision 2030, including the construction of a new mega-airport in Riyadh — King Salman International Airport — designed to handle 120 million passengers annually by 2030. The Saudia Group itself is being restructured, with flyadeal positioned as the budget arm while Saudi Arabian Airlines goes premium.

India is the single largest source market for Saudi aviation. The two countries are connected by deep economic ties — bilateral trade exceeded $50 billion in FY25 — and by religious tourism that drives millions of Indian Muslims to Mecca and Medina each year. A budget carrier on this corridor is, in some ways, overdue.

## What NRIs in America Should Know

For Indian Americans, flyadeal's Hyderabad route matters less as a direct travel option and more as a signal. Saudi budget aviation to India means downward pressure on fares across the Gulf corridor — and that corridor is how most NRIs in the United States get home. Whether you route through Dubai, Doha, or Abu Dhabi, more competition on the India-Gulf leg means lower connection fares and better options.

It also matters for family. Many Indian American families have relatives who work in Saudi Arabia — brothers, cousins, uncles who took Gulf jobs and send remittances home. A cheaper Riyadh-Hyderabad flight makes it easier for those relatives to visit family in India, which in turn makes the annual NRI trip home more likely to overlap with a family reunion.

flyadeal is not going to replace Emirates or Qatar Airways on anyone's SFO-to-HYD itinerary. But it's adding capacity, competition, and price pressure to one of the world's busiest migration corridors. For the Indian diaspora on both sides of the ocean, that's worth watching."""
    },

    # ── ARTICLE 3: Emirates / Iran War / Gulf Hub Disruption ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Emirates Is Fighting to Win Back Passengers as the Iran War Reshapes How NRIs Fly Home",
        "subheadline": "Tim Clark says the airline will offer safety incentives and rebooking guarantees, but admits first-class cabins are half-empty and fares won't drop while oil stays above $90.",
        "slug": make_slug("emirates-iran-war-nri-flights-gulf-hub-disruption"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "Dubai is the single most common layover point for Indian Americans flying between the US and India. Emirates, Etihad, and Qatar Airways between them carry more NRI traffic than any US or Indian carrier. When Gulf airspace is restricted and fares spike, NRIs feel it directly — every Diwali trip, every family emergency, every wedding RSVP becomes more expensive and less predictable.",
        "tags": ["travel", "airlines", "emirates", "iran", "gulf", "airfares", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/middle-east/emirates-offer-incentives-safety-assurances-iran-war-hits-travel-2026-06-09/"},
            {"name": "IATA / TBS News", "url": "https://www.tbsnews.net/world/global-airlines-slash-2026-profit-forecast-fuel-shock-iran-war-1099201"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/iran-israel-uae-qatar-saudi-arabia-airline-profit-collapse-2026/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20594766/pexels-photo-20594766.jpeg",
        "image_caption": "An Emirates aircraft on the tarmac at Dubai International Airport",
        "image_attribution": "Pexels",
        "body": """Emirates President Tim Clark gave his first major interview since the Iran war began in late February, and the message was equal parts reassurance and realism. The airline will offer "all sorts of incentives other than price" to win back nervous passengers, he told Reuters on the sidelines of an aviation summit in Berlin. But he also conceded that first-class cabins are running about half-full, ticket prices cannot drop while oil fluctuates near $90 a barrel, and the airline is in active talks with governments to loosen airspace restrictions that have upended Gulf aviation.

For the millions of Indian Americans who route through Dubai on their way to Delhi, Mumbai, Hyderabad, and Bengaluru, this is not an abstract industry story. It is the reason their tickets cost more, their layovers feel riskier, and their travel plans have become harder to lock down.

## What the Iran War Has Done to Gulf Aviation

The conflict, which escalated from U.S.-Israeli strikes against Iranian nuclear and military targets in late February, has closed or restricted airspace across large swaths of the Persian Gulf and wider Middle East. The European Union Aviation Safety Agency (EASA) has issued conflict-zone warnings advising airlines against flying over parts of the Gulf. That means longer routes, higher fuel burns, and disrupted schedules for every carrier that uses Dubai, Abu Dhabi, Doha, or Riyadh as a hub.

The financial toll is staggering. IATA — the global airline industry body — slashed its 2026 profit forecast from $41 billion to $23 billion, nearly halving it. Jet fuel prices have surged past $150 per barrel at points, up from under $100 a year ago. Spirit Airlines, the U.S. budget carrier, shut down last month — the first airline casualty directly attributed to the war's cost pressures.

IATA Director General Willie Walsh said he expects more airline failures. "In an environment where demand remains pretty robust, but capacity comes down, that will likely lead to a situation where fares will remain elevated," he said at the group's annual meeting in Rio de Janeiro.

## What Emirates Is Doing About It

Clark's strategy is to hold the line on schedules and win passengers back with non-price incentives. He outlined three commitments: enhanced safety assurances backed by intelligence-sharing with regional governments, rebooking guarantees for passengers stranded by cancellations ("We'll take care of all of that, including flying them on other carriers if necessary to bring them home or get the kids into school"), and active lobbying to ease EASA's airspace restrictions.

What he did not promise was cheaper tickets. "The ticket price is very much conditional on what the oil price starts, and at the moment the oil price fluctuates," Clark said. He predicted oil would eventually fall from about $90 to $70, and "then we'll be back. But it's a question of how long it takes."

## The NRI Impact

For Indian Americans, the Gulf carriers are not a luxury — they are infrastructure. Emirates, Etihad, and Qatar Airways collectively carry more US-India traffic than any American or Indian airline. Their hub model — fly west from India to Dubai or Doha, then onward to JFK, SFO, ORD, IAH, DFW — has been the default routing for a generation of NRIs. When that model is disrupted, the ripple effects hit every family planning a trip home.

The practical consequences are already visible. Round-trip fares on key NRI corridors — SFO-DEL, JFK-BOM, ORD-HYD — have jumped 15-25% compared to the same period last year. Transit times are longer as carriers adjust routing to avoid restricted airspace. And the psychological cost is real: passengers are booking refundable fares, buying more travel insurance, and in some cases avoiding Gulf hubs altogether in favor of direct flights on Air India or United, even at higher base prices.

## What NRIs Can Do Now

Three practical moves for anyone planning India travel this summer or fall. First, book refundable or flexible fares — the premium is worth it in this environment. Second, compare Gulf-hub routings against nonstop options from Air India (SFO-DEL, SFO-BLR, JFK-DEL, JFK-BOM, ORD-DEL) and United (SFO-DEL, EWR-DEL, EWR-BOM). Nonstop flights avoid the Gulf entirely, and the fare gap has narrowed as Gulf carriers raise prices. Third, monitor EASA's conflict-zone bulletins and your airline's travel advisories — if airspace restrictions expand, schedule changes will follow fast.

Clark sounded cautiously optimistic that the worst may be passing. But the Iran war has exposed a structural vulnerability in how NRIs travel: too much of the US-India corridor runs through a single, geopolitically fragile region. Until that changes — or until the war ends — elevated fares and schedule uncertainty are the new normal."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
