#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Just Added Bengaluru to Its Nonstop Map — and India's Tech Corridor Finally Has a European Shortcut",
        "subheadline": "Starting October 25, Switzerland's flag carrier will fly Zurich–Bengaluru five days a week on an Airbus A350, making it the third Indian city with a direct SWISS link after Delhi and Mumbai.",
        "slug": make_slug("swiss-airlines-zurich-bengaluru-direct-nri-tech"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the roughly 150,000 Indian-origin professionals and students in Switzerland, Germany, and Austria, the new route eliminates the Gulf layover that has defined Bengaluru travel for years. It also creates a viable one-stop option for US-based Kannadigas connecting through Zurich.",
        "tags": ["travel", "airlines", "swiss", "bengaluru", "europe", "tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "iamexpat.ch", "url": "https://www.iamexpat.ch/lifestyle/lifestyle-news/new-swiss-route-connects-switzerland-indias-tech-capital"},
            {"name": "Nomad Lawyer", "url": "https://nomadlawyer.org/swiss-international-air-lines-deploys-direct-bengaluru-route/"},
            {"name": "SWISS Newsroom", "url": "https://newsroom.swiss.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20848202/pexels-photo-20848202.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Swiss International Air Lines aircraft at Zurich Airport",
        "body": """Bengaluru has spent decades calling itself India's Silicon Valley. Now it finally has a direct air link to match. Swiss International Air Lines announced that it will launch nonstop flights between Zurich and Bengaluru starting October 25, 2026 — making India's tech capital the airline's third direct Indian destination alongside Delhi and Mumbai.

## The Route

The new service will operate five days a week (daily except Mondays and Wednesdays) using an Airbus A350-900, SWISS's newest widebody equipped with its "SWISS Senses" redesigned cabin. Flight time clocks in at roughly nine hours — competitive with the Gulf-hub alternatives that currently dominate the corridor but involve a connection and an extra three to five hours of total travel.

SWISS CEO Jens Fehlinger framed the move squarely around business demand. "There is growing demand from business travellers for direct flights to this important tech metropolis," he said in the airline's announcement. That demand has a name: Bengaluru is headquarters to the Indian operations of Google, Amazon, Microsoft, SAP, Bosch, and dozens of European firms — many of which route executives through Zurich, Frankfurt, or Munich today.

The route fits into a broader winter 2026/27 schedule that runs through March 27, 2027, covering 88 destinations from Zurich and Geneva.

## Why NRIs Should Pay Attention

For Indian Americans, the SWISS Bengaluru route solves a specific problem. Today, flying from the US to Bengaluru almost always means transiting through a Gulf hub — Dubai, Abu Dhabi, Doha — or connecting domestically through Delhi or Mumbai on Air India. That second leg is where things tend to fall apart: delayed connections, missed bags, and a three-hour domestic hop after an already exhausting 14-hour transatlantic flight.

Zurich offers a different geometry. SWISS's parent company, Lufthansa Group, operates extensive transatlantic service from hubs in Zurich, Frankfurt, and Munich. That means an NRI in San Francisco, New York, or Chicago can now book a single-alliance itinerary to Bengaluru via Zurich — one connection, both legs on a premium European carrier, bags checked through. Star Alliance frequent flyers earn and burn miles across the whole trip.

For the estimated 150,000 Indian-origin professionals and students scattered across Switzerland, Germany, and Austria, the route is even more direct. Many currently fly via Dubai or Istanbul to reach Bengaluru. A nine-hour nonstop from Zurich cuts that to a single flight.

## The Bigger Picture

SWISS's entry into Bengaluru reflects a broader shift. India's aviation market has been dominated by Gulf carriers on international long-haul and by Air India and IndiGo domestically. But European carriers are beginning to carve out direct corridors to India's Tier 1 cities. Lufthansa already flies Munich–Bengaluru. British Airways serves Heathrow–Bengaluru. Now SWISS completes the trilogy of major European flag carriers with a direct Bengaluru link.

The timing is also notable. Air India has been cutting international routes amid soaring fuel costs from the Iran conflict, reducing its own long-haul capacity by an estimated 17% this summer. That retreat has created openings. Foreign carriers — Cathay Pacific, Singapore Airlines, and now SWISS — are filling the gaps, particularly on high-yield business corridors.

SWISS is also expanding its A350 fleet to five aircraft by year-end, enabling it to add capacity on premium routes like Johannesburg, Shanghai, and Boston alongside Bengaluru.

## What to Know Before Booking

Bookings for the winter 2026/27 schedule will open through SWISS.com and travel agents in the coming weeks. Fares from Zurich to Bengaluru on competitor routes currently start around CHF 700 (roughly $780) round-trip in economy. SWISS is likely to price competitively at launch.

For US-based travelers: look for connecting fares on Lufthansa Group's transatlantic routes. A ZRH connection adds roughly two hours compared to a Gulf hub but eliminates the domestic Indian leg — a trade-off many Bengaluru-bound NRIs will happily take.

*The winter schedule runs October 25, 2026 through March 27, 2027. Whether the route continues into summer 2027 will depend on load factors and demand.*"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Golden Chariot Is Back — and It Might Be the Best Way for NRIs to See the South",
        "subheadline": "IRCTC has relaunched its luxury train through Karnataka, Goa, Tamil Nadu, and Kerala with upgraded cabins, an onboard Ayurvedic spa, and early-bird discounts of up to 20% through June 30.",
        "slug": make_slug("golden-chariot-luxury-train-relaunch-south-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who visit India every year or two but rarely venture beyond their hometown, the Golden Chariot offers a curated, hassle-free way to cover four South Indian states in under a week — without the logistics headache of booking drivers, hotels, and guides separately.",
        "tags": ["travel", "luxury-train", "golden-chariot", "south-india", "karnataka", "irctc"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/india/irctc-resumes-golden-chariot-luxury-train-for-2026-2027-season/"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/irctc-launches-upgraded-golden-chariot-luxury-train-for-2026-27/"},
            {"name": "LatestLY", "url": "https://www.latestly.com/agency-news/india-news-irctc-launches-upgraded-golden-chariot-luxury-train-for-2026-27-season.html"},
            {"name": "PNI News", "url": "https://pninews.com/irctc-announces-launch-of-upgraded-golden-chariot-luxury-train-for-2026-27-tourist-season/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35866185/pexels-photo-35866185.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A train passes through lush Indian countryside — the Golden Chariot route covers Karnataka, Goa, Tamil Nadu, and Kerala",
        "body": """Most NRIs know exactly two things about Indian trains: the Rajdhani is always late, and the Palace on Wheels exists but costs a fortune. The Golden Chariot — India's luxury train through the south — has operated in relative obscurity for years, overshadowed by its Rajasthan counterpart. IRCTC is betting that a major relaunch will change that.

## What Changed

The Indian Railway Catering and Tourism Corporation has upgraded the Golden Chariot for the 2026–27 season with refreshed cabins, modern amenities, and a sharper focus on wellness. The train now carries 40 cabins accommodating up to 80 guests, each outfitted with smart TVs, improved climate control, and redesigned interiors that lean into South Indian aesthetic motifs.

The headline addition is the Arogya Spa & Fitness Centre — an onboard wellness facility offering Ayurvedic therapies and contemporary fitness equipment. It is a calculated move: India's wellness tourism sector has been growing at roughly 20% annually, and IRCTC is positioning the Golden Chariot as a moving Ayurvedic retreat rather than just a heritage rail experience.

Wi-Fi connectivity, enhanced safety features, and improved accessibility for differently-abled passengers round out the upgrades.

## Three Routes, Four States

The 2026–27 season offers three curated itineraries, all departing from Bengaluru:

**Pride of Karnataka** (6 days/5 nights): Bengaluru → Mysuru → Halebidu → Hampi → Badami → Goa → Bengaluru. This is the flagship route, threading through the Hoysala temples, the Vijayanagara ruins at Hampi, and the Badami cave temples before ending with Goa's beaches.

**Jewels of the South** (6 days/5 nights): Bengaluru → Mysuru → Kochi → Alleppey → Chettinad → Pondicherry → Mahabalipuram → Bengaluru. The wider southern sweep, covering Kerala's backwaters, Tamil Nadu's temple towns, and the French Quarter of Pondicherry.

**Glimpses of Karnataka** (4 days/3 nights): A shorter circuit through Karnataka for travelers with less time — details to be finalized, but expected to focus on Mysuru, Hampi, and one or two other Karnataka highlights.

## The NRI Calculus

Here is the pitch for Indian Americans who visit India regularly but rarely explore beyond their home city: the Golden Chariot removes every logistical headache of South Indian travel.

Booking a multi-city trip through Karnataka, Goa, Tamil Nadu, and Kerala on your own means coordinating drivers, vetting hotels, navigating unfamiliar bus stations, and managing the sheer distances involved. For a family of four visiting from the US, the planning overhead alone can consume weeks. The Golden Chariot packages all of it — transport, accommodation, meals, guided excursions — into a single ticket. You sleep on the train, wake up at the next destination, and walk out to a curated experience.

This is particularly relevant for second-generation NRIs who want to see India beyond their grandparents' village but lack the local knowledge to plan a complex itinerary. It is also a smart option for NRI parents bringing American-born children to India for the first time. The controlled environment of a luxury train softens the culture shock while delivering the highlights.

## The Price Question

IRCTC has not published rack rates for the 2026–27 season, but the Golden Chariot has historically ranged from roughly ₹2.5 lakh to ₹5 lakh per person for the 6-day itineraries (approximately $3,000 to $6,000), depending on cabin class — broadly comparable to the Palace on Wheels and Maharajas' Express.

The promotional offer is significant: 20% off for early bookings and an additional 5% discount on select departures through June 30, 2026. For a couple, that could shave ₹1–2 lakh off the total — enough to justify booking now rather than waiting.

## Worth It?

Luxury train travel in India is not cheap, and the Golden Chariot is no exception. But measured against the alternative — booking five separate hotels, three flights, two car services, and a dozen entry tickets across four states — the all-inclusive economics start to make sense. Add the spa, the curated guides, and the absence of Indian traffic, and the value proposition sharpens further.

The first departures of the 2026–27 season begin in October. Bookings are open through IRCTC's website and authorized agents. Early-bird pricing runs through June 30.

*For NRIs planning a winter India trip, this might be the most painless way to see the South — and arrive back in Bengaluru with your sanity intact.*"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India and Maldivian Just Made Island-Hopping a One-Ticket Affair — and NRIs Should Notice",
        "subheadline": "A new interline agreement lets passengers book a single ticket from Delhi or Mumbai to 16 Maldivian islands, while the archipelago prepares to open its most exclusive resort yet.",
        "slug": make_slug("air-india-maldivian-codeshare-nri-island-hopping"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans have been swapping Goa for the Maldives in growing numbers, but the logistics of reaching anything beyond Malé have been a friction point. The Air India-Maldivian codeshare, combined with visa-free entry for Indian passport holders, makes the Maldives a significantly easier add-on to an India trip.",
        "tags": ["travel", "maldives", "air-india", "luxury", "island", "resort"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Angel One / Market Updates", "url": "https://www.angelone.in/news/market-updates/air-india-and-maldivian-partner-for-seamless-island-travel-across-maldives"},
            {"name": "Visit Maldives Corporation", "url": "https://corporate.visitmaldives.com/maldives-emerges-as-key-travel-hub-as-private-jet-arrivals-surge/"},
            {"name": "Islands Magazine", "url": "https://www.islands.com/the-maldives-new-little-gold-island-resort-is-opening-in-2026/"},
            {"name": "Maldives Magazine", "url": "https://maldives-magazine.com/luxury-maldives-travel-2026-top-trends/"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9394274/pexels-photo-9394274.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Overwater bungalows in the Maldives — the new Air India-Maldivian interline agreement opens up 16 domestic island destinations",
        "body": """The Maldives has a logistics problem. Everyone flies into Malé, checks into an overwater villa, posts the obligatory turquoise-water photo, and goes home. The archipelago stretches across 26 atolls and nearly 1,200 islands, but for most visitors, the experience begins and ends within speedboat range of Velana International Airport.

Air India and Maldivian — the Maldives' national carrier — have signed an interline agreement designed to change that equation. The arrangement allows passengers to book a single ticket covering Air India's international flights and Maldivian's domestic network, with coordinated connections and baggage transfers.

## What the Deal Covers

Air India passengers flying into Malé from Delhi (the only current direct route, operating daily with over 55,000 one-way seats annually) can now connect onward to 16 domestic Maldivian destinations on a single itinerary. The domestic network includes Hanimaadhoo, Gan, Kooddoo, Maafaru, Kulhudhuffushi, Dharavandhoo, and Kaadedhdhoo — names that mean nothing to most tourists but represent access to the quieter, less developed atolls where the Maldives' newest luxury resorts are concentrated.

The agreement also covers Maldivian-operated flights from Kochi and Thiruvananthapuram to Malé and Hanimaadhoo, creating a southern India gateway that bypasses Delhi entirely.

For Indian Americans, the practical impact is straightforward: you can book Delhi → Malé → Dharavandhoo (for the Baa Atoll resorts) as a single ticket through Air India's booking system, rather than purchasing a separate Maldivian domestic flight and hoping the connections line up.

## The Maldives' India Bet

India has become the Maldives' largest source market, and the interline deal reflects that reality. Indian passport holders receive a 30-day visa on arrival — no pre-arrangement required, just a valid passport, return ticket, and proof of accommodation. The IMUGA traveller declaration must be completed within 96 hours of arrival, but it is a simple online form.

The numbers tell the story. India sent roughly 210,000 tourists to the Maldives in the most recent full year of data, outpacing China and Russia. The Gulf corridor disruptions from the Iran war have further shifted travel patterns: private jet arrivals to the Maldives surged 166% as affluent travelers from India and the Gulf rerouted around conflict zones. Maafaru Airport alone handled 804 private jet movements in 2025, up 38% from the prior year.

For NRIs, the Maldives occupies an interesting niche. It is close enough to India to add as a four-day extension to a family visit (Delhi to Malé is roughly four hours), luxurious enough to satisfy anniversary or milestone trip expectations, and visa-free for Indian passport holders — a rarity in a world where Indian passports unlock relatively few destinations without paperwork.

## Bvlgari Enters the Chat

The timing of the Air India-Maldivian deal coincides with the Maldives' most anticipated luxury opening of the year. Bvlgari Resort Ranfushi, located in Raa Atoll, is set to open in 2026 after a one-year delay. The property — Bvlgari Hotels' tenth globally — will feature 54 villas, including overwater and beach configurations, plus a private-island Bulgari Villa for those operating at a different economic stratum.

Designed by ACPV Architects (the firm behind Bvlgari's Milan and Paris hotels), Ranfushi will include four signature dining venues, an extensive spa, and what the brand describes as the highest sustainability standards in its portfolio. A nesting bird habitat integrated into the resort design signals the kind of regenerative-luxury positioning that high-end Maldivian properties are increasingly adopting.

Raa Atoll is precisely the kind of destination the new interline agreement is designed to unlock. It is not reachable by speedboat from Malé. You need a domestic flight or seaplane — and now, that domestic flight can be part of your Air India ticket.

## The 2026 Maldives Playbook for NRIs

The most efficient approach for Indian Americans: fly into India for your family visit, then tag on a Maldives extension using Air India's daily Delhi–Malé service. Book through to your final island destination on a single ticket via the new Maldivian interline. Total additional travel time from Delhi: four to six hours depending on the domestic connection.

Peak season runs November through April. Shoulder season (May through July) offers lower rates and smaller crowds, though monsoon rain is a factor. Budget around $400–800 per night for a mid-range overwater villa; the Bvlgari and comparable ultra-luxury properties will start north of $2,000.

The visa-on-arrival process is genuinely painless — have your IMUGA form filled out, carry your hotel confirmation, and you are through immigration in minutes.

*For NRIs who have been meaning to do the Maldives but never quite worked out the logistics, the friction just dropped considerably.*"""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
