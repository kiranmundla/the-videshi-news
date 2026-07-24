#!/usr/bin/env python3
"""Travel writer — 2026-06-27 07:00 PT batch. Three articles."""

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


# ── Article 1: GMR Nagpur Airport ──────────────────────────────────────────────

art1_body = """
Nagpur's Dr. Babasaheb Ambedkar International Airport changed hands on June 25 when GMR Group formally took over operations under a 30-year concession. The handover — attended by Civil Aviation Minister K. Rammohan Naidu, Maharashtra Chief Minister Devendra Fadnavis, and Union Minister Nitin Gadkari — marks the start of what could become Central India's most consequential infrastructure upgrade in a generation.

## What GMR Plans to Build

The concession covers a phased modernisation programme: a new integrated terminal, expanded airside infrastructure, enhanced cargo facilities, and sustainability-led digital systems. The long-term target is capacity for 30 million passengers annually — roughly ten times the airport's current throughput. GMR, which already runs Delhi, Hyderabad, and Goa (Mopa), now operates nine airports across India and abroad, including Medan in Indonesia.

Gadkari described Nagpur as "one of India's most strategically located cities" — it sits near the country's geographical centre — and argued that the upgraded airport would catalyse growth in tourism, mining, agriculture, and export-oriented industries across the wider Vidarbha region. Fadnavis called it "the biggest engine of economic growth" for Central India.

## Why This Matters for the Diaspora

For the estimated 200,000-plus Vidarbha-origin Indians scattered across the US, UK, and Gulf states, Nagpur has long been the airport you tolerate rather than enjoy. Most international journeys meant a connection through Mumbai or Delhi, adding hours and a domestic booking to every trip. The hub-and-spoke model India launched this week — Air India's Easy Connect service already links Varanasi to 18 international destinations via Delhi with single-ticket immigration — is designed to change that calculus. If Nagpur joins that network as planned, a traveller from Chicago could eventually book a single itinerary to Nagpur via Delhi without touching their bags at the hub.

GMR's track record is relevant here. Hyderabad's Rajiv Gandhi International Airport was a regional facility when GMR took it over; today it handles 25 million passengers and serves as a genuine international gateway. Nagpur's supporters hope for the same arc — and the five-year plan for the airport includes Nagpur joining GMR's cargo hub strategy, which matters for the region's orange, textile, and pharmaceutical exports.

## The Competitive Landscape

The handover lands amid India's busiest season of airport development. Adani Group announced $2.12 billion in airport-city investments across six locations the same week. Navi Mumbai's Adani-run airport begins international flights on July 15. And Bhogapuram, GMR's other greenfield project near Visakhapatnam, opens on July 8. The common thread: private operators are betting that India's airport infrastructure gap is large enough — and demand persistent enough — to justify multi-billion-dollar wagers.

For NRIs from Nagpur, Wardha, Amravati, or Chandrapur, the bet translates to something simpler: a direct international connection within a few years, and a terminal that doesn't feel like a bus station in the meantime.
""".strip()

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nagpur Airport Gets a New Owner — and Central India Gets a Shot at the World",
    "subheadline": "GMR Group has taken over Nagpur's Dr. Babasaheb Ambedkar International Airport under a 30-year concession. For the Vidarbha diaspora, it could mean the end of routing every trip home through Delhi or Mumbai.",
    "slug": make_slug("nagpur-airport-gmr-takeover-central-india-vidarbha-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Vidarbha-origin NRIs in the US, UK, and Gulf may eventually get direct international connectivity to Nagpur instead of routing through Mumbai or Delhi.",
    "tags": ["travel", "airports", "infrastructure", "nagpur", "gmr", "vidarbha"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/03/NagpurAirport.JPG",
    "image_caption": "Aerial view of Dr. Babasaheb Ambedkar International Airport in Nagpur",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ── Article 2: India Hotel Investment Boom ─────────────────────────────────────

art2_body = """
In the span of seven days, three of India's biggest hospitality moves landed on the same theme: build where the diaspora wants to stay.

Marriott International signed a ₹350 crore deal with Manglam Group to bring a 220-key Sheraton to Jaipur's Ajmer Highway — their third collaboration and part of a ₹1,000 crore hospitality push by the Rajasthan developer. The Indian Hotels Company (IHCL, parent of Taj) planted its Tree of Life brand on the banks of Chilika Lake in Odisha, marking its first resort in the state. And The Leela confirmed that its first Rajasthan desert property — 80 rooms and tented villas on 30 acres near Jaisalmer Fort — will open later this year.

## The Pattern Behind the Projects

Each of these signings targets a different slice of the Indian travel market, but they share an underlying logic: India's domestic and inbound luxury demand is growing faster than supply, and the gap is widest in exactly the kinds of places the diaspora visits.

Jaipur is already India's wedding capital. The new Sheraton aims to absorb overflow from peak wedding and festival seasons, when the city's existing luxury stock fills up months in advance. NRI families who fly in for a week-long wedding — and there are tens of thousands every winter — currently scramble for rooms. A purpose-built 220-key convention-ready property on the highway changes that math.

Chilika Lake is a different bet entirely. Asia's largest brackish water lagoon, a UNESCO World Heritage candidate, home to 160 bird species and the endangered Irrawaddy dolphin — yet it has virtually zero branded accommodation. IHCL's 30-key Tree of Life resort is modest in scale but signals something larger: Odisha is being positioned as India's next eco-luxury frontier, alongside Kerala and the Northeast. For NRIs with roots in Odisha — or those looking for destinations beyond the Goa-Rajasthan-Kerala circuit — this is worth watching.

## The Leela's Desert Play

The Leela Jaisalmer is perhaps the boldest move. A full luxury resort near a UNESCO fort in the Thar Desert, it will offer tented villas, a ballroom, a spa, and a man-made lake — designed explicitly to anchor multi-city Rajasthan itineraries alongside The Leela's existing properties in Udaipur and Jaipur. The play is clear: make Rajasthan's "golden triangle" a self-contained luxury corridor where guests never leave the Leela ecosystem.

For NRI travellers, this kind of curated itinerary removes the friction that still plagues Indian travel — inconsistent quality between cities, unreliable bookings, and the gap between what a travel brochure promises and what the hotel delivers.

## Why Brands Are Moving Now

India added 20 million domestic air passengers in the last two years. International tourist arrivals are at their highest since 2019. And the wedding industry — worth an estimated $130 billion annually — is increasingly anchoring itself around branded venues rather than convention centres.

Hilton is preparing to open The Den Bengaluru, its first LXR Hotels & Resorts property in India. IHG has signed five hotels with Adani Airports for upcoming airport-city developments. Marriott alone now has over 160 properties across the country. The race for India's premium hospitality dollar is no longer coming; it's here.

For the diaspora, the practical upshot is tangible: the next trip to Jaipur, Odisha, or the Thar might finally come with a hotel that matches the expectation.
""".strip()

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "From Jaisalmer's Desert to Odisha's Lagoon, India's Hotel Builders Are Chasing the Diaspora Dollar",
    "subheadline": "In one week, Marriott signed a ₹350 crore Sheraton in Jaipur, IHCL planted its Tree of Life brand on Chilika Lake, and The Leela confirmed a desert resort near Jaisalmer Fort. The common bet: NRIs will pay for places worth flying home for.",
    "slug": make_slug("india-luxury-hotel-boom-sheraton-jaipur-leela-jaisalmer-ihcl-chilika-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India for weddings, festivals, and family trips now have significantly more branded luxury hotel options in Jaipur, Odisha, and Rajasthan's desert circuit.",
    "tags": ["travel", "hotels", "luxury", "jaipur", "jaisalmer", "odisha", "ihcl", "marriott", "leela"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Restaurant India", "url": "https://www.restaurantindia.in"},
        {"name": "Hotelier India", "url": "https://www.hotelierindia.com"},
        {"name": "HOTELS Magazine", "url": "https://www.hotelsmag.com"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com"},
    ]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33726144/pexels-photo-33726144.jpeg",
    "image_caption": "Sandstone courtyard of a heritage hotel in Jaisalmer, Rajasthan",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── Article 3: Bhogapuram Airport ──────────────────────────────────────────────

art3_body = """
India's newest greenfield international airport has a date: July 8. The Alluri Sitarama Raju International Airport at Bhogapuram, about 45 kilometres from Visakhapatnam on NH-16, will begin operations after a ₹4,592 crore build by GMR Visakhapatnam International Airport Limited. It is the first major new airport on India's eastern coast in over a decade.

## Built for the Big Planes

The numbers are deliberately ambitious. A 3,800-metre runway — long enough for fully loaded Airbus A350s and Boeing 787s — signals that Bhogapuram isn't settling for regional hops. Phase one is sized for six million passengers annually, with a master plan that can scale as demand grows. A 5,000-square-metre cargo terminal, equipped with temperature-controlled rooms for pharma and seafood exports, follows in August or September.

The terminal itself draws on Andhra Pradesh's visual language: Mogulu folk paintings and hand-crafted local art line the interiors, while automated baggage systems and crowd-flow sensors are designed to keep processing times down from day one.

## The Telugu American Angle

There are an estimated 600,000 Telugu-speaking Americans in the United States — concentrated in New Jersey, Texas, the Bay Area, and the Washington-Baltimore corridor. For most of them, getting to Visakhapatnam has meant flying into Hyderabad and then catching a short domestic hop or enduring an overnight train. Bhogapuram's runway was built to handle nonstop international services eventually, which could mean direct Gulf connections within months and, if demand warrants, long-haul routes to the US down the line.

Even before the nonstops materialise, Bhogapuram improves the equation. Air India's new Easy Connect hub-and-spoke model — which lets passengers clear immigration at their origin airport and check bags through to the final destination — is tailor-made for an airport like this. A traveller from Dallas could book a single ticket through Delhi to Bhogapuram, clear immigration in Bhogapuram's brand-new terminal rather than fighting the Delhi scrum, and step out into Vizag's sea air without touching a bag in transit.

## What It Means for the Region

Vizag already ranks as India's eighth-largest city and has attracted IT parks, a steel plant, and a submarine-building shipyard. But its existing airport — a repurposed naval facility — has long constrained connectivity. Commercial flights squeezed between military operations, and international capacity was essentially nil.

Bhogapuram changes the equation for several constituencies. The pharma corridor around Visakhapatnam gets a temperature-controlled cargo terminal for direct exports. The tourism sector — Araku Valley's coffee plantations, Borra Caves, the beaches of Rushikonda and Yarada — gets an airport that can actually bring international visitors. And the north Andhra hinterland, from Vizianagaram to Srikakulam, gets the kind of connectivity that once required a train to Hyderabad.

GMR, which just took over Nagpur Airport the same week, is betting that India's secondary cities are ready for the infrastructure that primary metros took decades to build. For Telugu Americans who have watched the Hyderabad airport transform from a regional facility into an international gateway, Bhogapuram represents the hope that their ancestral coast might follow the same arc.
""".strip()

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Vizag's New Greenfield Airport Opens on July 8 — and the Telugu Diaspora Finally Gets a Shorter Route Home",
    "subheadline": "The ₹4,592-crore Bhogapuram airport near Visakhapatnam has a 3,800-metre runway built for long-haul jets. For the estimated 600,000 Telugu Americans, it could eventually mean skipping the Hyderabad layover entirely.",
    "slug": make_slug("bhogapuram-airport-vizag-july-opening-telugu-diaspora-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Telugu Americans in the US (estimated 600,000+) may get direct international flights to Visakhapatnam via Bhogapuram, eliminating the Hyderabad layover for visits to north Andhra and coastal AP.",
    "tags": ["travel", "airports", "infrastructure", "visakhapatnam", "vizag", "andhra-pradesh", "telugu-diaspora"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "MagicBricks", "url": "https://www.magicbricks.com"},
        {"name": "GMR Airports", "url": "https://www.gmrgroup.in"},
        {"name": "CNBC-TV18", "url": "https://www.cnbctv18.com"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/View_of_Vizag_city_from_RK_Beach.jpg/1280px-View_of_Vizag_city_from_RK_Beach.jpg",
    "image_caption": "View of Visakhapatnam's skyline from RK Beach on the Bay of Bengal coast",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}


# ── Insert ─────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
