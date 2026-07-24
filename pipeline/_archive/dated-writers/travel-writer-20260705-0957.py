#!/usr/bin/env python3
"""Travel writer — July 5 2026 batch (3 articles)."""

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
    # ── ARTICLE 1: Riyadh Air Mumbai Launch ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Riyadh Air Picks Mumbai as Its First Indian Destination — Daily Flights Start August 4",
        "subheadline": "Saudi Arabia's newest full-service airline will fly Boeing 787-9 Dreamliners to India's financial capital, entering one of the world's most competitive aviation corridors.",
        "slug": make_slug("riyadh-air-mumbai-india-daily-flights-august"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "More than three million Indians live and work in Saudi Arabia, and Mumbai is the single busiest corridor between the two countries. A new daily nonstop option means better prices, better timing, and more upgrade inventory for NRIs flying between the Gulf and home.",
        "tags": ["travel", "airlines", "riyadh-air", "mumbai", "saudi-arabia", "gulf"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com"},
            {"name": "Live From A Lounge", "url": "https://livefromalounge.com"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg/1280px-HZ-RXX_Boeing_787-9_Dreamliner_Riyadh_Air_LHR_4.1.26_%2855027186633%29.jpg",
        "image_caption": "Riyadh Air Boeing 787-9 Dreamliner at London Heathrow Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """Mumbai will become Riyadh Air's first destination in India when the Saudi carrier launches daily nonstop flights on August 4. The airline — Saudi Arabia's newest full-service operation, barely a month into commercial flying — is deploying its flagship Boeing 787-9 Dreamliner on the route, a signal of how seriously it views the India market.

Flight RX697 will depart King Khalid International Airport at 14:05 and land at Mumbai's Chhatrapati Shivaji Maharaj International Airport at 20:35 local time, a roughly five-hour hop. The return, RX698, leaves Mumbai at 22:05 and touches down in Riyadh at 23:50. The timings are built around Riyadh Air's hub strategy: passengers arriving from India in the evening can connect onward to European and North African destinations the following morning.

## A corridor that keeps getting more crowded

The Mumbai–Riyadh sector is already one of the busiest international aviation corridors in the Gulf region. With Riyadh Air's entry, eight carriers will operate nonstop flights between India and Saudi Arabia: Air India, Air India Express, Akasa Air, flynas, flyadeal, IndiGo, Saudia, and now Riyadh Air. Mumbai alone will be served by six airlines on the Riyadh route, the highest concentration of any Indian city.

The competition should be welcome news for passengers. Fares on the route have historically spiked during Hajj and Umrah season, and around Indian holiday periods when workers travel home. More capacity means more price discipline — Air India currently lists one-way Mumbai–Riyadh fares as low as ₹13,189 ($157) for July dates, and the addition of daily Dreamliner capacity from a carrier eager to build market share could push shoulder-season fares lower still.

## What Riyadh Air actually is

Riyadh Air is not a legacy carrier. It was created from scratch as part of Saudi Arabia's Vision 2030 diversification plan, backed by the kingdom's sovereign wealth fund. The airline commenced commercial operations in June 2026 with flights to London Heathrow using factory-new Boeing 787-9s, and has since added Dubai, Jeddah, Cairo, and seasonal European routes including Malaga and Madrid. Kuala Lumpur starts July 30; Dhaka follows on August 7.

The product is squarely aimed at the premium end: lie-flat business class, a modern economy cabin, and IFE throughout — a clear attempt to compete with Gulf heavyweights Emirates, Qatar Airways, and Etihad on equipment quality while undercutting them on price and schedule through the Riyadh hub.

## Why NRIs should care

The India–Saudi Arabia aviation market is not driven primarily by tourists. It runs on the lives of roughly 2.6 million Indian nationals living and working in the kingdom — the largest expatriate community in Saudi Arabia. Mumbai is the natural gateway: it serves Maharashtra, Gujarat, and large parts of western and central India, regions that account for a disproportionate share of Gulf-bound Indian workers.

For Indian Americans, the route matters differently. Many NRI families maintain connections across the Gulf diaspora — siblings in Riyadh, parents in Mumbai, cousins in New Jersey. A daily nonstop on a new-generation widebody makes multi-stop family trips through the Gulf more practical. The evening departure from Mumbai also connects neatly to onward Riyadh Air flights to London and Southern Europe, creating a viable one-stop alternative to the traditional Gulf carrier routing.

Riyadh Air has confirmed plans to extend to Delhi, Bengaluru, Hyderabad, and Chennai by late 2026, though specific launch dates for those cities have not been announced. If those routes materialise on schedule, it would give the airline the widest India network of any Saudi carrier — and Indian travellers a genuinely new option on corridors that have long been dominated by the same half-dozen names."""
    },

    # ── ARTICLE 2: Cordelia Cruises Chennai to SE Asia ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's East Coast Just Got Its First International Cruise Season — and You Can Sail to Singapore Without a Visa",
        "subheadline": "Cordelia Cruises is running 10-night Southeast Asia sailings from Chennai to Phuket, Langkawi, Kuala Lumpur, and Singapore — a first for India's eastern seaboard.",
        "slug": make_slug("cordelia-cruise-chennai-southeast-asia-singapore-visa-free"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs visiting family in Tamil Nadu, Andhra Pradesh, or Karnataka, a cruise tagged onto a summer India trip is now genuinely practical — no extra visas needed, all departing from Chennai, with cabins starting around ₹50,000 per person.",
        "tags": ["travel", "cruise", "chennai", "southeast-asia", "cordelia", "singapore", "visa-free"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelBiz Monitor", "url": "https://travelbizmonitor.com"},
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com"},
            {"name": "Travel Weekly Asia", "url": "https://travelweekly-asia.com"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Cruise_in_Kochi_l_Kerala.jpg/1280px-Cruise_in_Kochi_l_Kerala.jpg",
        "image_caption": "A cruise ship docked at Kochi port in Kerala, India",
        "image_attribution": "Wikimedia Commons",
        "body": """Something quietly historic is happening at Chennai port this summer. For the first time, international cruise ships are departing from India's eastern coastline — and the itineraries read like a Southeast Asian greatest-hits tour.

Cordelia Cruises, India's only major domestic cruise line, returned to Chennai on June 20 for its fifth consecutive season. But 2026 is different. Previous years offered short domestic hops — weekend jaunts at sea, coastal runs to Puducherry or Visakhapatnam. This year, the Cordelia Empress is sailing international waters: a 10-night voyage from Chennai to Phuket, Langkawi, Kuala Lumpur, and Singapore, departing July 18.

## The itinerary

The flagship sailing covers four countries in 10 nights. After departing Chennai, the ship spends three days at sea before docking at Phuket — Thailand's beach-and-nightlife island — for a full day. From there it's Langkawi (Malaysia's duty-free resort island), Port Klang for Kuala Lumpur, and finally Singapore. Passengers disembark in Singapore and fly home, or can book the return separately.

For travellers who want more, Cordelia offers an extended 13-night version: a three-night Visakhapatnam–Puducherry–Chennai domestic leg starting July 15, followed seamlessly by the 10-night international sailing. One boarding pass, one cabin, India to Singapore.

The season also includes several Sri Lanka itineraries from Chennai: a five-night cruise covering Hambantota, Trincomalee, and Jaffna (departing August 10 and 17), and a shorter three-night Chennai–Trincomalee run on August 7. And Visakhapatnam — Andhra Pradesh's largest port — will see its first-ever international cruise departure when the Empress sails for Southeast Asia on July 15.

## The visa situation is the real story

Here is what makes these sailings unusually practical for Indian passport holders: you need almost no paperwork. Indian nationals do not require visas for Malaysia or Thailand. Singapore provides visa-on-arrival for cruise passengers. The only hard requirement is a passport valid for at least six months.

Compare that with the bureaucratic gauntlet of booking a multi-country Southeast Asian trip independently — hotel bookings, internal flights, transfer logistics, and in some cases multiple visa applications. The cruise collapses all of it into a single booking. Board in Chennai, disembark in Singapore, and the ship handles everything in between.

## What the ship is like

The Cordelia Empress is a mid-size cruise vessel — 692 feet, 11 decks, 796 cabins across five categories accommodating up to 1,950 guests. It is not the Queen Mary. But it offers four dining venues, nine bars and lounges, a casino, spa, rock-climbing wall, live stage performances, and dedicated kids' zones. For Indian travellers accustomed to the all-inclusive resort format, the proposition is familiar: one price, everything included, no nickel-and-diming for meals and entertainment.

Cabin prices for the Southeast Asia sailing start around ₹50,000 per person for interior rooms on a twin-share basis, scaling up for balcony and suite categories. Port charges and taxes are additional.

## Why this matters for NRIs

The Indian diaspora in the United States includes more than 1.5 million people with roots in Tamil Nadu, Andhra Pradesh, and Karnataka — the states that Chennai serves as a natural gateway. Many make an annual summer trip to visit family. Until now, the travel options after landing in Chennai were limited to the usual: temple circuit, beach town, or internal flight to another Indian city.

A 10-night cruise to Southeast Asia changes the calculus. An NRI family visiting grandparents in Chennai can tack on a cruise holiday departing from the same city, without needing to arrange additional visas or domestic flights to reach a departure port like Mumbai. The timing — mid-July through August — aligns perfectly with American school summer holidays.

India's cruise industry has been growing rapidly from a near-zero base. The government has identified 14 ports for cruise tourism development, and domestic passenger numbers have tripled since 2022. But international sailings from the east coast are genuinely new territory. If Chennai proves viable as a year-round international departure port, it could open up an entirely different kind of holiday for the millions of Indians — and Indian Americans — who call South India home."""
    },

    # ── ARTICLE 3: Monsoon Premium Villa Boom ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Monsoon Is Now a Luxury Season — and the Western Ghats Are Booked Solid",
        "subheadline": "Premium villa operators are expanding rapidly across Maharashtra and Karnataka as monsoon travel sheds its budget reputation and becomes the country's fastest-growing hospitality segment.",
        "slug": make_slug("india-monsoon-luxury-villa-western-ghats-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who only visit India in December or May, monsoon is the overlooked season: domestic flights cost 30-50% less, villa rates are a fraction of peak pricing, and the Western Ghats are at their most spectacular. Premium private stays now make it comfortable too.",
        "tags": ["travel", "monsoon", "western-ghats", "luxury", "villa", "india", "maharashtra", "karnataka"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"},
            {"name": "Outlook Traveller", "url": "https://outlooktraveller.com"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Kerala_Monsoon_clouds_over_Western_Ghats_India.jpg/1280px-Kerala_Monsoon_clouds_over_Western_Ghats_India.jpg",
        "image_caption": "Monsoon clouds rolling over the Western Ghats in Kerala, India",
        "image_attribution": "Wikimedia Commons",
        "body": """There was a time when the Indian monsoon was simply the season you avoided. Flights were cheap because nobody wanted them. Hotels dropped rates because occupancy cratered. The Western Ghats were stunning, but you got there on potholed roads and stayed in mildew-adjacent guesthouses. Not anymore.

India's monsoon travel market has undergone a quiet transformation. A new generation of premium villa operators — professionally managed, architecturally distinctive, Instagram-ready — has turned the rainy season into a luxury proposition. And the numbers are following: monsoon bookings at high-end private stays in Maharashtra and Karnataka have been growing at 25-30% year-on-year, according to industry estimates, outpacing every other travel season in the country.

## The villa boom

EkoStay, one of India's largest managed villa platforms, announced this week that it has expanded its portfolio to more than 160 properties across India, with the latest additions specifically timed for monsoon demand. The new properties — Vana Mora in Nashik, Wada Crest in Wada, Casa Elara in Igatpuri, Casa Bella in Lonavala, and Forest Cube Villa in Chikmagalur — are positioned around what the company calls different "travel moods": mountain-facing luxury, forest hideaway, celebration villa, slow-living retreat.

EkoStay is not alone. StayVista, SaffronStays, and Vista Rooms have all been expanding their monsoon-ready portfolios in the Sahyadri range and the Coorg-Chikmagalur coffee belt. The common thread: private pools (heated, because monsoon mornings are cool), fully equipped kitchens, dedicated caretakers, and enough distance from the nearest town that the only sound is rain on leaves.

Rates for a three-bedroom monsoon villa within driving distance of Mumbai or Pune start around ₹15,000-25,000 per night — roughly $180-300. A comparable property during Diwali or Christmas week would run two to three times that.

## The destinations NRIs are missing

Most Indian Americans plan their India trips around December holidays or May weddings. They miss the monsoon entirely, and with it some of the subcontinent's most dramatic landscapes.

The Western Ghats — a UNESCO World Heritage mountain chain running 1,600 kilometres down India's western edge — are at their absolute peak from July through September. Waterfalls that are trickles in winter become thundering cascades. Tea plantations in Munnar and coffee estates in Coorg turn an electric green that photographs cannot capture. Hill stations that are dusty and overcrowded in summer empty out and turn misty and cool.

Here is what the travel writers are recommending this season:

**Agumbe, Karnataka** — Called the "Cherrapunji of the South," this rainforest town receives among the highest rainfall in peninsular India. Dense jungle, rare reptile biodiversity, and Barkana Falls in full flow.

**Tirthan Valley, Himachal Pradesh** — A quieter alternative to Manali, with the Tirthan River running through apple orchards and pine forests. Great for families with older children who can handle moderate treks.

**Bhandardara, Maharashtra** — A lakeside destination in the Sahyadri range, roughly four hours from Mumbai. Waterfalls, historic forts, and camping under clouds that sit at eye level. The monsoon transforms it from a scrubby plateau into a green amphitheatre.

**Jawai, Rajasthan** — Not the Western Ghats, but worth the detour. Monsoon turns Jawai's granite hills green, and it remains one of India's best places for leopard sightings outside a national park.

## The practical case for monsoon travel

The economics are compelling. Domestic flight fares within India drop 30-50% between July and September compared to peak winter and wedding-season pricing, according to booking data from Wego. A round-trip Mumbai–Kochi fare that costs ₹12,000 in December can be had for ₹5,000-6,000 in July. Hotel rates across India dip significantly, and the premium villa market — while growing fast — still offers rates at a fraction of high-season pricing.

For NRI families on a summer visit, this means the internal India leg of the trip costs dramatically less. And with American school holidays running through August, the timing aligns naturally.

The legitimate concerns — road conditions, flight delays, unpredictable weather — are real but manageable. The monsoon in western India follows a predictable rhythm: mornings are often clear, heavy rain hits in the afternoon, and evenings turn cool and pleasant. The key is to book a villa rather than a hotel (so you are not stuck in a lobby during downpours), keep driving distances short (three to four hours maximum), and build flexibility into the itinerary rather than scheduling a sight per hour.

## The bigger picture

India's monsoon tourism push is not accidental. State governments in Kerala, Karnataka, and Maharashtra have all launched dedicated monsoon tourism campaigns in recent years. Kerala pioneered the concept with its Ayurveda-focused monsoon packages — the humid climate is believed to make the body more receptive to traditional Panchakarma treatments — and the model has spread.

What has changed is the supply side. Five years ago, a premium monsoon stay meant a five-star hotel in Munnar or Coorg with a spa package. Today, there are hundreds of independently operated luxury villas in locations that did not have a single bookable property a decade ago. The infrastructure has caught up with the landscape — and for NRIs who have never seen India in the rain, it might be the most underrated travel experience the country offers."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
