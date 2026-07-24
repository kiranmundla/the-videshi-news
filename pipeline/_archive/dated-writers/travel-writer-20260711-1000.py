#!/usr/bin/env python3
"""Travel writer - 2026-07-11 10:00 PT run. Three articles."""

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
    # ── Article 1: Emirates A380 to Delhi ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Emirates Sends Its A380 to Delhi — and Premium Economy to Half of India",
        "subheadline": "From October 25, the double-decker superjumbo joins Emirates' four daily Delhi services. Premium Economy will cover six Indian cities and nearly half the airline's India flights.",
        "slug": make_slug("emirates-a380-delhi-premium-economy-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Emirates is the go-to connecting airline for NRIs travelling between the US, UK, Canada, and India via Dubai. The A380 on Delhi and expanded Premium Economy across six cities means a materially better mid-cabin option on one of the most-flown diaspora corridors.",
        "tags": ["travel", "airlines", "emirates", "delhi", "premium-economy", "a380", "dubai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/07/09/emirates-will-deploy-a380-for-first-time-to-this-popular-indian-city/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/routes-networks-latest-rolling-daily-updates-wc-july-6-2026"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Emirates_Airbus_A380-861_A6-EER_MUC_2015_01.jpg/1280px-Emirates_Airbus_A380-861_A6-EER_MUC_2015_01.jpg",
        "image_caption": "An Emirates Airbus A380-861 on the tarmac — the superjumbo will begin Delhi service from October 25",
        "image_attribution": "Wikimedia Commons",
        "body": """Delhi is about to get the full Emirates treatment.

From October 25, the airline will deploy its flagship Airbus A380 on flight EK512/513 between Dubai and Delhi's Indira Gandhi International Airport. Delhi becomes the third Indian gateway to receive the double-decker superjumbo, joining Mumbai and Bengaluru — a trio that now covers the three busiest NRI corridors in the country.

The A380 will operate in a four-class configuration: First Class suites, Business Class lie-flat seats, Premium Economy, and Economy. It joins three other daily Delhi services operated by retrofitted Boeing 777 aircraft, all of which also carry the four-class layout. That means every single Emirates flight between Delhi and Dubai will now offer Premium Economy — a cabin that has become the airline's fastest-growing product.

## Premium Economy reaches six Indian cities

The Delhi rollout is part of a wider push. By late October, Premium Economy will be available across six Indian gateways: Delhi (four daily flights), Mumbai (22 weekly), Kolkata (12 weekly), Bengaluru (seven weekly), Ahmedabad (nine weekly), and Kochi (two weekly). That covers nearly half of Emirates' scheduled weekly flights to and from India.

Kolkata gets an upgrade of its own. The daily EK570/571 service will switch from a Boeing 777 to Emirates' next-generation Airbus A350, bringing the newer cabin product — including Premium Economy — to eastern India for the first time on the route.

The cabin itself features cream leather seats with extra legroom and recline, chinaware dining, and a full amenity kit. It sits in a distinct section between Business and Economy, pitched at travellers who want more comfort without the jump to a full-flat bed.

## Why this matters for NRIs

Emirates isn't just an India-to-Dubai airline. For the Indian American diaspora, it's one of the most popular connecting carriers on the India-US corridor. Hundreds of thousands of NRIs route through Dubai each year to reach JFK, SFO, LAX, ORD, IAH, and DFW — and the quality of that stopover experience matters.

Until now, the Premium Economy option on Indian routes was inconsistent. A family of four flying Economy from Chicago to Hyderabad via Dubai might have Premium Economy available on the US leg but not on the India leg. The October rollout fixes that asymmetry for a significant chunk of India traffic.

The A380 specifically brings Emirates' onboard lounge and shower spa (in First Class) to Delhi — a draw for the growing segment of Indian travellers willing to pay for top-tier service. The airline has also opened retail travel stores in Delhi and Mumbai, with Hyderabad and Bengaluru locations in the pipeline.

## The competitive picture

Emirates now operates 167 weekly flights across nine Indian gateways: Ahmedabad, Bengaluru, Chennai, Delhi, Hyderabad, Kochi, Kolkata, Mumbai, and Thiruvananthapuram. That's among the densest international networks serving India.

The A380 deployment comes as Air India accelerates its own fleet refresh — deploying A350s on US routes — and Gulf rivals like Qatar Airways and Etihad compete aggressively for India-to-world transfer traffic. Adnan Kazim, Emirates' deputy president and chief commercial officer, framed the move as a response to "strong demand for travel to and from India" and signalled further service enhancements in the pipeline.

For NRIs planning fall and winter travel to India, the October upgrades mean a tangibly better experience on one of the corridor's most reliable connecting options. The question now is whether the fares will follow the product upmarket — or whether competition keeps Premium Economy pricing accessible."""
    },

    # ── Article 2: LOT Polish Airlines Delhi–SFO via Warsaw ────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "LOT Polish Airlines Opens a New Delhi-to-Bay Area Route via Warsaw",
        "subheadline": "A Boeing 787 Dreamliner connection through Warsaw Chopin Airport gives Indian travellers — and the Bay Area's large diaspora — another option on the India-US corridor.",
        "slug": make_slug("lot-polish-airlines-delhi-san-francisco-warsaw-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The San Francisco Bay Area is home to one of the largest Indian diaspora communities in the US. A new Delhi-SFO routing via Warsaw adds competition to a corridor dominated by nonstops (Air India, United) and Middle Eastern hub connections, potentially pushing fares lower for NRI families making the trip home.",
        "tags": ["travel", "airlines", "lot-polish", "delhi", "san-francisco", "bay-area", "warsaw"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/n3nimwrbfd38/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/routes-networks-latest-rolling-daily-updates-wc-july-6-2026"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/LOT_-_Polish_Airlines_Boeing_787-8_Dreamliner_SP-LRA_%2814389157362%29.jpg/1280px-LOT_-_Polish_Airlines_Boeing_787-8_Dreamliner_SP-LRA_%2814389157362%29.jpg",
        "image_caption": "A LOT Polish Airlines Boeing 787-8 Dreamliner — the aircraft type expected to serve the Delhi-Warsaw-San Francisco route",
        "image_attribution": "Wikimedia Commons",
        "body": """There's a new way to fly from Delhi to the Bay Area — and it runs through an unexpected hub.

LOT Polish Airlines has announced connectivity between Delhi's Indira Gandhi International Airport and San Francisco International Airport through its Warsaw Chopin Airport hub. The routing, operated on Boeing 787 Dreamliner aircraft, links three aviation markets on a single airline network and adds a European-hub alternative to the India-California corridor.

It's not a nonstop. But for price-sensitive travellers, especially NRI families booking four or five seats, a one-stop connection through Warsaw with competitive fares could undercut the $1,200-plus roundtrips that nonstops on Air India and United routinely command during peak season.

## The Bay Area connection

San Francisco and the wider Bay Area are home to one of the most concentrated Indian diaspora populations in the United States. Santa Clara County alone has more than 200,000 residents of Indian origin, and the tech corridor from San Jose to San Francisco employs tens of thousands of Indian-born professionals at Apple, Google, Meta, and the region's startup ecosystem.

That population drives enormous demand on the India-SFO corridor. Air India operates nonstop service from both Delhi and Mumbai to SFO. United runs its own Delhi-SFO nonstop. Emirates, Qatar Airways, and Etihad all compete through their respective Gulf hubs. Turkish Airlines connects through Istanbul.

LOT's entry via Warsaw adds another card to the deck. Poland's flag carrier has been steadily expanding its long-haul network, using Warsaw's geographical position — roughly equidistant between India and North America on a great-circle path — as a connecting advantage.

## What travellers should expect

The 787 Dreamliner is a solid long-haul aircraft, known for its pressurised cabin (equivalent to 6,000 feet altitude versus the 8,000-foot standard), larger windows, and improved humidity. LOT operates both the 787-8 and 787-9 variants.

The key variable is connection time at Warsaw. Passengers will need to clear transit at Chopin Airport, which has a dedicated transfer area and has invested in improving processing times for connecting passengers. Indian passport holders transiting through Warsaw to the US generally do not need a Schengen visa if they remain in the international transit zone, though travellers should verify requirements based on their specific routing.

Total travel time from Delhi to SFO via Warsaw will likely run 18 to 20 hours depending on the connection, compared with roughly 15.5 hours for a nonstop. For travellers coming from smaller Indian cities connecting through Delhi, the total door-to-door difference may be negligible.

## Fare competition matters

The real impact of LOT's entry may be felt not in its own load factors but in what it does to pricing across the corridor. Every additional carrier on a route creates fare pressure. Airlines monitor competitor bookings closely, and the mere existence of a Warsaw option at, say, $850 roundtrip could force Air India and United to sharpen their own Economy pricing.

This matters most during peak NRI travel windows — Diwali (October-November), Christmas-New Year, and the summer break — when fares on Delhi-SFO routinely spike above $1,500 and families weigh whether the trip home is financially viable.

LOT's network also opens routing flexibility. Passengers could combine the India leg with a Warsaw stopover — Poland has become an increasingly popular European destination — or connect onward to other European cities before continuing to SFO.

## The bigger picture

LOT's Delhi-SFO connection fits a broader trend: European secondary hubs competing with the Gulf mega-carriers for India-US transfer traffic. Turkish Airlines through Istanbul, Lufthansa through Frankfurt, and now LOT through Warsaw are all chipping away at the Dubai-Doha-Abu Dhabi dominance.

For the Bay Area's Indian community, more options means more leverage. And in a market where a family of four can easily spend $5,000 on roundtrip tickets to India, every new competitor that shaves a few hundred dollars off the fare makes a real difference."""
    },

    # ── Article 3: Akasa Air Kochi–Kuwait ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Akasa Air Launches Direct Kochi-Kuwait Flights, Reopening Kerala's Gulf Lifeline",
        "subheadline": "Starting August 1, the budget carrier will connect Cochin International Airport with Kuwait City, restoring a direct link that serves millions of Keralite expatriates in the Gulf.",
        "slug": make_slug("akasa-air-kochi-kuwait-direct-flights-kerala-gulf-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Kerala's Gulf diaspora — estimated at over 2 million Malayalis across the GCC — depends on affordable direct flights between Kochi and Gulf capitals. The Akasa route fills a critical gap, particularly for blue-collar workers and middle-class families who can't afford premium carriers or long layovers.",
        "tags": ["travel", "airlines", "akasa-air", "kochi", "kuwait", "kerala", "gulf", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/akasa-air-launches-direct-kochi-kuwait-flights/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/akasa-air-flight-status/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Kochi_airport_terminal_1.jpg/1280px-Kochi_airport_terminal_1.jpg",
        "image_caption": "Terminal 1 at Cochin International Airport, the departure point for Akasa Air's new Kuwait service",
        "image_attribution": "Wikimedia Commons",
        "body": """For millions of Keralites living and working in the Gulf, a direct flight between Kochi and Kuwait isn't a convenience — it's a lifeline.

Akasa Air will launch direct service between Cochin International Airport (COK) and Kuwait International Airport (KWI) starting August 1, the carrier announced this week. The route adds another spoke to Akasa's growing Gulf network and restores direct connectivity on a corridor that has been disrupted by the broader Middle East conflict.

The timing is significant. Akasa's earlier Kuwait flights were among the international services suspended as airlines rerouted and pulled capacity amid airspace closures tied to the West Asia conflict. The August relaunch signals the carrier's confidence that operating conditions have stabilised enough to bring the route back.

## Kerala's Gulf corridor

The Kerala-Gulf connection is one of the most culturally and economically significant migration corridors in the world. An estimated 2.1 million Malayalis live across the six GCC states — Saudi Arabia, UAE, Kuwait, Qatar, Bahrain, and Oman — with Kuwait hosting one of the largest communities. Remittances from Gulf-based Keralites account for a substantial share of Kerala's state GDP, and the traffic between Kochi and Gulf capitals is year-round, not seasonal.

That traffic is also price-sensitive. Unlike the tech professionals flying Business Class between Bengaluru and San Francisco, the Kochi-Kuwait corridor serves a broader economic cross-section — construction workers, nurses, hospitality staff, teachers, and small-business owners whose ticket purchases represent a meaningful share of their monthly income. Budget carrier pricing matters here in a way it doesn't on premium routes.

Akasa Air, backed by late investor Rakesh Jhunjhunwala's vision of a low-cost international carrier, has positioned itself squarely in this segment. The airline already operates from Kochi to Jeddah and has been building out its Gulf network from multiple Indian cities.

## What Akasa is competing against

The Kochi-Kuwait corridor isn't empty. Kuwait Airways, Jazeera Airways, and Air India Express have all operated the route at various points. IndiGo, India's largest carrier, has been expanding aggressively into Gulf markets as well.

But Akasa's entry still matters for two reasons. First, additional capacity on a route generally pushes fares down — and current one-way prices on Kochi-Kuwait hover around ₹14,000 to ₹22,000, a range where even a ₹1,000-2,000 reduction is meaningful for a worker sending the bulk of their salary home. Second, Akasa's schedule flexibility — the carrier has been adding frequencies quickly on routes that perform — means the August launch could scale to daily or even twice-daily service if demand warrants it.

## The conflict shadow

The caveat is obvious. Akasa suspended its Kuwait, Qatar, Riyadh, and Abu Dhabi services earlier this year due to the West Asia conflict. Jeddah remained the only Gulf destination that kept operating, largely because its western Saudi Arabian location kept it further from affected airspace.

The August 1 relaunch suggests the airline believes the worst of the disruption has passed — or at least that it can operate safely around it. But travellers should note that conflict-related schedule changes remain possible, and Akasa has offered crisis waivers (free cancellation and rescheduling) on affected Middle East routes before. Passengers booking for August and beyond would be wise to check the airline's waiver policy and buy flexible tickets where available.

## What NRIs in the US should know

For Indian Americans, the Kochi-Kuwait route might seem like someone else's story. But it isn't, entirely. Many NRIs in the US have family members working in the Gulf — a brother in Kuwait, a cousin in Dubai, parents who retired back to Kerala after decades in Bahrain. The health of Gulf-India connectivity directly affects the extended family's ability to gather, especially during Onam (August-September) and Christmas-New Year, when Keralite families converge from three continents.

More broadly, the restoration of budget carrier service on Gulf routes is a signal that India's international aviation market is normalising after months of conflict-driven disruption. If Akasa's Kuwait relaunch holds, expect similar resumptions across other suspended Gulf routes in the coming weeks."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
