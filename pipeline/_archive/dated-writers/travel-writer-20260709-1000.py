#!/usr/bin/env python3
"""Travel writer – July 9, 2026 batch (3 articles)."""

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


# ─────────────────────────────────────────────────────────────────
# ARTICLE 1: Riyadh Air launches Mumbai flights
# ─────────────────────────────────────────────────────────────────

art1_body = """Saudi Arabia's newest carrier has picked Mumbai as its beachhead into India — and NRIs now have a premium alternative on one of the busiest corridors in global aviation.

Riyadh Air, the kingdom's second national airline backed by the Public Investment Fund (PIF), will operate daily nonstop flights between Riyadh's King Khalid International Airport and Mumbai's Chhatrapati Shivaji Maharaj International Airport starting August 4. Bookings opened on July 6, with economy fares starting at SAR 585 (roughly $156) one-way and business class from SAR 2,537 ($676).

## A Premium Offering on a Massive Route

The service will be flown on brand-new Boeing 787-9 Dreamliners configured in four classes — Business Elite (four private suites), Business (24 seats), Premium Economy (39 seats), and Economy (223 seats). That four-cabin layout is a deliberate play for high-yield traffic: Indian executives, Gulf-based professionals, and NRIs visiting family who want something better than the budget options that dominate this corridor today.

"With India emerging as one of the fastest-growing aviation markets globally, we are delighted to offer travellers a new premium choice and enhanced global connectivity from Mumbai to Riyadh, and onwards to Europe," said CEO Tony Douglas.

The timing makes sense. Flight RX0697 departs Riyadh at 14:05 and lands in Mumbai at 20:35 local time. The return, RX0698, leaves Mumbai at 22:05 and arrives in Riyadh at 23:50 — timed for convenient onward connections to London, Madrid, Manchester, Cairo, and Jeddah through the Riyadh hub.

## Why NRIs Should Pay Attention

Around 3.4 million Indians travelled to Saudi Arabia in 2025 alone, according to India's tourism ministry. That includes a vast expatriate workforce, families visiting relatives in the Gulf, and a growing segment of leisure and business travellers routing through Saudi hubs to reach Europe.

Until now, that traffic has been served primarily by IndiGo, Air India Express, and Saudia — airlines that skew toward economy-class configurations. Riyadh Air's entry gives NRIs a genuinely premium alternative, with codeshare agreements already in place with Air India, Delta, Singapore Airlines, Virgin Atlantic, and Turkish Airlines. That means frequent flyers can earn and burn miles across a wide alliance network.

The carrier has also announced plans for services to Delhi, Bengaluru, Hyderabad, and Chennai as more aircraft arrive — a signal that India is central to Riyadh Air's global buildout, not just a flag-planting exercise.

## The Bigger Picture

Riyadh Air is part of Saudi Arabia's Vision 2030 push to position Riyadh as a global transit hub rivalling Dubai and Doha. The airline launched London flights in June, followed by Dubai and Cairo, with Madrid, Manchester, Kuala Lumpur, and Dhaka starting this month. Mumbai is destination number ten.

For Indian Americans who regularly route through the Gulf on their way to India, this adds genuine competition on price and quality. And for the roughly 2.7 million Indian nationals working in Saudi Arabia, it is simply a better way to get home."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Riyadh Air Enters India with Daily Mumbai Flights Starting August 4",
    "subheadline": "Saudi Arabia's newest premium carrier will fly Boeing 787-9 Dreamliners in four classes on the Mumbai–Riyadh route, with economy fares from $156 and onward connections to Europe.",
    "slug": make_slug("riyadh-air-mumbai-flights-launch-august-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "The 3.4 million Indians who travel to Saudi Arabia annually — plus NRIs routing through Riyadh to Europe — now have a premium four-class alternative with codeshare partners including Air India and Delta.",
    "tags": ["travel", "airlines", "saudi-arabia", "aviation", "riyadh-air", "mumbai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/riyadh-air-to-begin-mumbai-flights-from-aug-4-improving-india-saudi-arabia-connectivity/article69770162.ece"},
        {"name": "Connecting Travel", "url": "https://www.connectingtravel.com/news/riyadh-air-opens-bookings-for-mumbai-flights"},
        {"name": "DJ's Aviation", "url": "https://www.djsaviation.net/2026/07/riyadh-air-launches-flights-to-mumbai.html"},
        {"name": "HDFC Sky", "url": "https://www.hdfcsky.com/blog/riyadh-air-announces-india-foray-with-daily-mumbai-riyadh-flights-from-august-4"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/HZ-RXX_-_Boeing_787-9_Dreamliner_-_Riyadh_Air_LHR_010426.jpg/1280px-HZ-RXX_-_Boeing_787-9_Dreamliner_-_Riyadh_Air_LHR_010426.jpg",
    "image_caption": "A Riyadh Air Boeing 787-9 Dreamliner at London Heathrow Airport",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ─────────────────────────────────────────────────────────────────
# ARTICLE 2: Viksit UDAN + Jodhpur Airport
# ─────────────────────────────────────────────────────────────────

art2_body = """India just made its biggest bet yet on regional aviation — and the payoff could reshape how NRIs travel to their hometowns.

Prime Minister Narendra Modi launched the next phase of the regional air connectivity scheme on July 4, rebranded as "Viksit UDAN," alongside the inauguration of a gleaming new terminal at Jodhpur Airport. The numbers are staggering: ₹29,000 crore ($3.4 billion) earmarked over the next decade to develop 100 new aerodromes from existing unserved airstrips, build 200 helipads, and fund regional airline operations across the country.

## Jodhpur Gets a Modern Gateway

The centrepiece of the launch was Jodhpur's new terminal building, built at a cost of ₹480 crore ($57 million). The 23,000-square-metre facility can handle 2 million passengers annually and 1,500 during peak hours. It features 20 check-in counters, six jet bridges, advanced baggage handling systems, and an apron accommodating 11 Airbus A321 aircraft.

For a city that serves as the gateway to western Rajasthan's fort-and-desert tourism circuit — Mehrangarh Fort, Umaid Bhawan Palace, the Thar Desert — this is a significant upgrade. NRI families planning heritage trips to Rajasthan no longer need to route through Delhi or Jaipur and take a five-hour drive; Jodhpur can now handle direct narrow-body jet service at scale.

## What 'Viksit UDAN' Actually Means

The original UDAN scheme, launched in 2016, operationalised 669 routes connecting 95 airports, heliports, and water aerodromes — benefiting over 16.6 million passengers. But sustainability has been a concern: of 923 routes originally awarded, 266 have been discontinued, and 15 of the 93 airports developed under the scheme are no longer operational.

The modified scheme attempts to fix that with a more structured approach:

- **₹12,159 crore** to develop 100 aerodromes from existing airstrips
- **₹3,661 crore** for 200 modern helipads
- **₹2,577 crore** for operations and maintenance of regional airports
- **₹10,043 crore** in viability gap funding to keep regional airlines running

The scheme will also encourage deployment of indigenous aircraft — HAL Dhruv helicopters and Dornier platforms — in remote regions, adding connectivity to places that are currently unreachable by commercial aviation.

## The NRI Angle: Getting Closer to Home

For the Indian American diaspora, the practical impact is straightforward. Today, visiting family in a tier-2 or tier-3 city often means a long-haul flight to Delhi or Mumbai, followed by a domestic connection or a punishing road trip. As regional airports come online and airlines commit capacity, that last-mile gap shrinks.

Akasa Air has already announced plans to evaluate UDAN routes, joining IndiGo, Air India Express, and Star Air on the regional circuit. The carrier currently serves 28 domestic destinations and seven international cities, and adding UDAN routes would extend its reach into towns that don't yet have reliable scheduled service.

Combined with Air India's new "Easy Connect" hub-and-spoke model — which lets passengers from tier-2 cities like Varanasi clear immigration at their origin airport and connect seamlessly to international flights through Delhi — the pieces of a genuinely decentralised Indian aviation network are falling into place.

Whether that ₹29,000 crore translates into airports that actually sustain traffic, or joins the list of infrastructure announcements that underdeliver, remains to be seen. But for NRIs dreaming of a direct flight to Jodhpur, Lucknow, or Coimbatore, the trajectory is finally pointing in the right direction."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Commits ₹29,000 Crore to Regional Aviation — and Opens a New Gateway to Rajasthan",
    "subheadline": "PM Modi launched the 'Viksit UDAN' scheme to develop 100 new aerodromes and 200 helipads over the next decade, while inaugurating a modern terminal at Jodhpur Airport.",
    "slug": make_slug("viksit-udan-jodhpur-airport-regional-aviation-nri"),
    "category": "travel",
    "vertical": "aviation-infrastructure",
    "diaspora_angle": "As 100 new aerodromes and upgraded regional airports come online, NRIs visiting family in tier-2 and tier-3 cities could see direct flights replacing the current Delhi-then-drive ordeal.",
    "tags": ["travel", "airports", "infrastructure", "udan", "jodhpur", "rajasthan"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Global Newswire", "url": "https://www.theglobalnewswire.com/pm-modi-launches-viksit-udan-inaugurates-new-terminal-at-jodhpur-airport/"},
        {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airports-networks/airport-updates-latest-news-global-market-wc-july-6-2026"},
        {"name": "Latestly (ANI)", "url": "https://www.latestly.com/agency-news/pm-narendra-modi-inaugurates-jodhpur-airport-terminal-building-launches-modified-udan-scheme-watch-video-6790183.html"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2131456"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/40/Jodhpur_Airport.png",
    "image_caption": "Jodhpur Airport, gateway to western Rajasthan's heritage tourism circuit",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────────────
# ARTICLE 3: Air India Easy Connect (tier-2 international)
# ─────────────────────────────────────────────────────────────────

art3_body = """If you have family in Varanasi, Lucknow, or any of India's mid-sized cities, you know the drill: they fly to Delhi, navigate the chaos of Terminal 3, re-check their bags, stand in another immigration line, and then — hours later — board an international flight. Air India wants to end that, and the early results suggest it might actually work.

On June 25, Air India launched "Easy Connect" — a hub-and-spoke model that lets passengers from tier-2 cities check their bags through to their final international destination, complete immigration at their origin airport, and transit through Delhi as international passengers. No baggage reclaim. No second immigration queue. No five-hour buffer "just in case."

## How It Works

Varanasi is the first spoke city. Flight AI1111 operates daily from Lal Bahadur Shastri International Airport to Delhi, with schedules coordinated so passengers can connect to any of 17 international destinations — London, Frankfurt, Dubai, Singapore, New York, and more — within a four-hour transit window.

The mechanics are simple but meaningful: passengers check in at Varanasi for, say, London Heathrow. Their bags are tagged through to LHR. They clear immigration in Varanasi — where lines are measured in minutes, not hours. In Delhi, they walk straight to their connecting gate as transit passengers.

"This is the first operational rollout of a framework that will expand to multiple cities in the months ahead," Air India said. The airline is positioning itself as the lead carrier for the government's hub-and-spoke initiative, which envisions a network where dozens of smaller airports serve as feeders into Delhi, Mumbai, and eventually other hubs.

## What It Means for NRIs

For the diaspora, this is less about their own travel — NRIs typically fly into Delhi or Mumbai directly — and more about the people they leave behind.

Parents in Varanasi visiting their children in the Bay Area currently face a gruelling journey: a domestic flight or train to Delhi, then the full international departure process at IGI Airport. Easy Connect eliminates the most stressful part of that trip. An elderly couple in Varanasi can now check in locally, clear immigration without the crush of Delhi, and arrive in San Francisco without touching their luggage until they reach the carousel.

The model also opens up reverse flows. NRIs flying into Delhi can now book onward connections to tier-2 cities on a single ticket with guaranteed baggage transfer — no more separate domestic bookings with white-knuckle connection times.

## The Bigger Vision

Air India's Easy Connect is part of a broader push by India's Civil Aviation Ministry to decentralise international air travel away from the metro giants. Union Aviation Minister Ram Mohan Naidu Kinjarapu has been championing the hub-and-spoke model as a way to make global travel accessible for millions of passengers who currently face long domestic journeys just to reach an international departure point.

The phased rollout will bring more cities online over the coming months. Cities likely in the queue include Lucknow, Ahmedabad, Jaipur, Chandigarh, and Amritsar — all with large diaspora populations and airports that can handle immigration infrastructure.

If the execution matches the ambition, this could be the most consequential change in Indian aviation for NRI families since the introduction of direct US-India nonstops. The difference: nonstops shaved hours off the journey for those flying from big cities. Easy Connect makes the journey humane for everyone else."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's 'Easy Connect' Lets Tier-2 India Skip the Delhi Airport Nightmare",
    "subheadline": "A new hub-and-spoke model launched from Varanasi lets passengers check bags through to their final international destination and clear immigration at home — no Delhi chaos required.",
    "slug": make_slug("air-india-easy-connect-varanasi-tier-2-international"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "NRI parents and relatives in tier-2 cities like Varanasi can now check through to the US or UK from their local airport — immigration, bags, and all — eliminating the most stressful leg of visiting family abroad.",
    "tags": ["travel", "airlines", "air-india", "varanasi", "hub-and-spoke", "tier-2-cities"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/about-us/news/press-releases/air-india-easy-connect.html"},
        {"name": "Travel & Leisure Asia", "url": "https://www.travelandleisureasia.com/in/air-travel/air-india-easy-connect-flights-tier-2/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-launch-hub-and-spoke-international-connectivity-flights-from-june-25/article69660012.ece"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/85/Varanasi_Airport.png",
    "image_caption": "Lal Bahadur Shastri International Airport in Varanasi, India's first Easy Connect spoke city",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ─────────────────────────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline']}: {e}")
