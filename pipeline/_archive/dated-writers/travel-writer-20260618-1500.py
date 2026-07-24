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
        "headline": "Air India's US Flights Have Quietly Collapsed — and Swiss, KLM and Cathay Are Taking the Diaspora's Seats",
        "subheadline": "Scheduled Air India flights to the US fell 77% this spring as Pakistani airspace and the Gulf war reroute the map. For NRIs, the smartest path home now often runs through Zurich, Amsterdam or Hong Kong.",
        "slug": make_slug("air-india-us-flights-collapse-swiss-klm-cathay-reroute-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Air India has long been the default nonstop for Indian Americans flying home; with its US schedule down 77% this spring, NRIs need to know which one-stop carriers now offer the most reliable and affordable route to India.",
        "tags": ["travel", "airlines", "air-india", "us-india", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — As Iran war jolts Air India, Lufthansa and Cathay pounce", "url": "https://www.reuters.com/business/aerospace-defense/iran-war-jolts-air-india-lufthansa-cathay-pounce-fast-growing-market-2026/"},
            {"name": "Skift — IndiGo Suspends 7 International Routes", "url": "https://skift.com/2026/06/indigo-suspends-international-routes/"},
            {"name": "Airways Magazine — Air India Resumes Mumbai-New York Nonstop", "url": "https://airwaysmag.com/air-india-mumbai-new-york/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Boeing_777_VT-ALO_Air_India_%287315805402%29.jpg/1280px-Boeing_777_VT-ALO_Air_India_%287315805402%29.jpg",
        "image_caption": "An Air India Boeing 777, the workhorse of its long-haul US network now reduced to a fraction of its former schedule",
        "image_attribution": "Wikimedia Commons",
        "body": """For a decade, the booking math for Indian Americans heading home was simple: find the Air India nonstop, swallow the fare, skip the connection. That math has broken.

Air India's scheduled flights from India to the United States plunged 77.4% year-on-year over March to May, according to route-level Cirium data cited by Reuters — by far the steepest cut in its network. Flights to Europe slipped a comparatively gentle 5.1%. The collapse is not a strategy; it is a squeeze. Pakistan has banned Indian carriers from its airspace since April 2025, forcing long, fuel-burning detours. The US-Israel war on Iran this spring closed more of the map. In a May staff memo, outgoing CEO Campbell Wilson wrote bluntly that the "massive rise" in jet fuel prices, "together with airspace closures and longer flying routes, has caused many of our international flights to become unprofitable."

## Foreign carriers are cashing in

The seats Air India is vacating are not going unsold. They are being absorbed by European and Asian airlines that don't have to fly around Pakistan and can route through their own hubs.

Swiss, owned by Lufthansa, scheduled 247 flights from India during March-May, up 39% on the year, with the Delhi-Zurich route alone rising 76% to 155 flights after the airline added a second daily service. Amsterdam-based KLM scheduled 294 flights, up 19.5%, and said it had seen more Indian passengers amid the Middle East crisis. Cathay Pacific scheduled 588 flights from India to Hong Kong, up 19%; CEO Ronald Lam told Reuters that many Indians who once connected through the Gulf were now reaching the US via Hong Kong.

The pattern matters for the diaspora. The classic Gulf one-stop — Emirates through Dubai, Qatar through Doha, Etihad through Abu Dhabi — held roughly steady but did not expand, and Gulf carriers remain boxed in by bilateral seat caps with India. The growth is in the European and Hong Kong corridors.

## What this means for your next trip home

For NRIs on the coasts and in the Midwest, the practical takeaways are concrete:

- **East Coast (JFK, EWR, IAD, BOS):** Zurich (Swiss) and Amsterdam (KLM) are now among the most reliable one-stops to Delhi, Mumbai, Bengaluru and beyond, often with better on-time performance than rerouted nonstops. Lufthansa through Frankfurt and Munich remains deep.
- **West Coast (SFO, LAX, SEA):** Cathay through Hong Kong has quietly become a strong option to South India, and avoids the Atlantic-then-Gulf zigzag entirely.
- **Air India still flies — but check the routing.** Where nonstops survive (Delhi and Mumbai to JFK, Newark, San Francisco, Chicago and Washington), block times have lengthened because of the airspace detours. A "nonstop" that now takes 17-plus hours eastbound may be less comfortable than a well-timed one-stop.

Booking behaviour should adjust too. With capacity thinner and reroutings adding cost, fares on surviving Air India nonstops have firmed even as the airline shrinks frequency. Comparison shopping across the European and Hong Kong hubs — rather than defaulting to the national carrier — is now the move that saves both money and missed-connection stress.

## The bigger picture

India remains one of the fastest-growing international air markets in the world; that has not changed. What has changed is who carries the traffic. With Pakistani airspace closed indefinitely and the Gulf only now stabilising after the Iran conflict, the airlines structurally best placed to serve US-India demand are the ones with unobstructed great-circle routes over Europe and East Asia.

Air India insists the retreat is temporary, tied to fuel and geopolitics rather than a permanent surrender of its flagship market. Its newest Airbus A350s, being deployed on premium US routes, are meant to claw back share once conditions ease. But for the family booking a December trip to India today, the reliable answer increasingly does not have "AI" in the flight number — and knowing that before the fares spike is the difference between a smooth journey and a scramble at the gate."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is in Full Retreat Abroad — Seven International Routes Cut Just as Summer Travel Peaks",
        "subheadline": "India's largest airline is suspending six Asian destinations from July and dropping Manchester in August, blaming fuel costs, airspace closures and a rare quarterly loss. NRIs with multi-city Asia plans should rebook now.",
        "slug": make_slug("indigo-international-route-cuts-asia-manchester-nri-summer"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "IndiGo's suspended routes through Hong Kong, Bangkok-adjacent Krabi and Southeast Asia are popular layover and side-trip options for diaspora families combining an India visit with a regional holiday — those itineraries now need rebuilding before October.",
        "tags": ["travel", "airlines", "indigo", "asia", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — India's IndiGo cuts six international routes", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-cuts-six-international-routes-2026/"},
            {"name": "Skift — IndiGo Suspends 7 International Routes: What's Behind the Cutbacks", "url": "https://skift.com/2026/06/indigo-suspends-7-international-routes/"},
            {"name": "The Hindu BusinessLine — IndiGo suspends flights to six Asian destinations", "url": "https://www.thehindubusinessline.com/companies/indigo-suspends-flights-six-asian-destinations/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg/1280px-Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg",
        "image_caption": "An IndiGo Airbus A320; the carrier is pulling back from long-haul and Southeast Asian flying after a quarterly loss",
        "image_attribution": "Wikimedia Commons",
        "body": """IndiGo spent the past two years trying to become something more than India's domestic workhorse — leasing wide-bodies for the first time, opening European long-haul, pushing into China and Southeast Asia. This month it started undoing much of that, fast.

The carrier announced it will temporarily suspend flights to Langkawi, Krabi, Ho Chi Minh City, Hong Kong and Shanghai from July 1, and Siem Reap from July 3, with all six routes shut until at least September 30. Days earlier it confirmed it would stop flying to Manchester from August 31 — the seventh international route to fall. IndiGo framed the moves as matching capacity to "softer demand" in a "challenging cost environment," and says it will reopen bookings on October 1, or sooner if conditions improve.

## Why a growing airline is shrinking abroad

The retreat follows a rare stumble: IndiGo posted a loss of ₹2,536 crore in the fourth quarter of FY26, dragged down by a weak rupee and low yields. The same forces battering Air India are at work — jet fuel prices elevated by the Iran conflict, and Pakistan's continuing ban on Indian carriers using its airspace, which lengthens routes and burns more fuel.

Manchester is the clearest casualty of overreach. That route relied on six Boeing 787-9 Dreamliners taken on a damp lease from Norway's Norse Atlantic in early 2025 — a stopgap meant to bridge the gap until IndiGo's own Airbus A350s arrive. Longer flight times from airspace closures made the economics untenable. The airline is returning one of the wet-leased jets to Norse.

Even after the cuts, IndiGo stresses it will keep operating more than 1,800 weekly international flights, so the core Gulf, Singapore and short-haul network stays intact. But the symbolism is hard to miss: India's two biggest airlines, IndiGo and Air India, are both in retreat from international ambitions they were trumpeting barely a year ago.

## What NRIs should do about it

The suspended routes are not random — several are exactly the destinations diaspora families fold into a trip home:

- **Hong Kong and Shanghai:** popular East Asia connections and standalone visits. If you booked IndiGo through either after July 1, expect a cancellation; rebook on Cathay, Singapore Airlines or a Gulf carrier now while seats last.
- **Krabi and Langkawi:** beach add-ons that NRIs often tack onto a December India holiday. With IndiGo out until October, AirAsia, Malaysia Airlines and Thai carriers are the fallback, generally via Kuala Lumpur or Bangkok.
- **Ho Chi Minh City and Siem Reap:** Vietnam and Cambodia trips will now require a connection rather than IndiGo's nonstop; Vietnam Airlines and regional carriers fill the gap.

The practical risk is not just rebooking hassle. As IndiGo pulls capacity out of these markets at the start of the school-holiday and wedding-travel window, the remaining seats on rival carriers will get more expensive. Travellers holding affected tickets should expect proactive notification from IndiGo, but should not wait passively — the earlier you rebook onto another airline, the better the fare.

## The takeaway

IndiGo insists this is a pause, not a permanent withdrawal, and that it stands ready to relaunch the routes ahead of schedule if fuel and airspace conditions ease. Its A350s, due over the next couple of years, are still meant to anchor a genuine long-haul network. For now, though, the airline that promised to connect India to the world is connecting it to rather less of it — and diaspora travellers planning anything beyond a straight India round-trip this summer should build their itineraries on the assumption that the IndiGo option simply isn't there until autumn."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Launched Its Longest Vande Bharat Yet — Nagpur to Pune in About 12 Hours",
        "subheadline": "The new semi-high-speed service stitches together Vidarbha and western Maharashtra, and for NRIs it is one more reason to leave the rental car behind and ride the rails on a visit home.",
        "slug": make_slug("nagpur-pune-vande-bharat-longest-route-india-nri-rail"),
        "category": "travel",
        "vertical": "rail",
        "diaspora_angle": "For Indian Americans visiting family across Maharashtra, India's expanding Vande Bharat network offers a comfortable, predictable alternative to chaotic highways and sold-out flights — and the new Nagpur-Pune route opens up a region many NRIs only ever drove through.",
        "tags": ["travel", "rail", "vande-bharat", "india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Current Affairs Adda247 — India's Longest-Route Vande Bharat Express Launched", "url": "https://currentaffairs.adda247.com/indias-longest-route-vande-bharat-express/"},
            {"name": "Dainik Jagran English — Indian Railways 2026-27: Hydrogen Train, Vande Bharat & New Rules", "url": "https://english.dainikjagranmpcg.com/indian-railways-2026-27/"},
            {"name": "Wikipedia — Vande Bharat Sleeper Express", "url": "https://en.wikipedia.org/wiki/Vande_Bharat_Sleeper_Express"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express on the move near Mumbai, part of India's fast-growing semi-high-speed network",
        "image_attribution": "Wikimedia Commons",
        "body": """India's semi-high-speed train network just stretched further than it ever has. Prime Minister Narendra Modi this week flagged off the Nagpur-Pune Vande Bharat Express — now the longest-route Vande Bharat in the country — covering the better part of Maharashtra in roughly 12 hours.

The route is a workhorse, not a showpiece: Nagpur (Ajni) to Pune via Wardha, Badnera, Akola, Bhusawal, Jalgaon, Manmad, Kopargaon, Ahilyanagar and Daund. It answers a long-standing demand from travellers in Vidarbha, who have leaned on private cars and pricey alternatives for the lack of a direct, comfortable, time-efficient link to Pune. The Maharashtra government had pressed the Railway Ministry to close the gap.

## A network that keeps growing

The Nagpur-Pune launch lands amid a broader railway push that should interest anyone who travels India regularly. Indian Railways is rolling out 12 Vande Bharat Sleeper trains for long-distance routes in 2026-27, two of which already run on the Howrah-Kamakhya corridor. Each sleeper rake carries 16 coaches built to cover 1,000 to 1,500 kilometres overnight — and the fares undercut flying sharply. The ministry has pegged the third-AC Guwahati-Howrah sleeper fare at about ₹2,300, against ₹6,000 to ₹10,000 for air travel on the same stretch.

The chair-car Vande Bharats, like Nagpur-Pune, offer airline-style rotatable seats, large windows, onboard Wi-Fi, infotainment, electric outlets and onboard catering. The newer sets run 20-coach configurations to handle demand. Add the recently launched Katra-Srinagar service crossing the world's highest rail bridge over the Chenab, and the network now reaches places that were genuinely hard to get to a few years ago.

## Why this matters to NRIs

For the diaspora, the appeal is practical. Anyone who has visited family in India knows the two usual options for intercity travel — a long, white-knuckle highway drive or a domestic flight that may be delayed, overbooked or eye-wateringly priced during festival season. The Vande Bharat network is quietly becoming a third path: predictable departure times, reserved comfortable seating, and a journey you can actually relax through.

For Maharashtra specifically, the Nagpur-Pune line opens up a swathe of central India — Vidarbha towns, the Nashik-Manmad belt — that many NRIs have only ever driven past on the way somewhere else. Booking is straightforward through IRCTC, which now handles foreign-issued cards more reliably than it once did, and confirmed reservations mean none of the platform scrum associated with older trains.

A few tips for diaspora travellers planning to use these trains on a trip home:

- **Book early through IRCTC.** Vande Bharat seats on popular corridors sell out, especially around Diwali and the winter wedding season.
- **Mind the long-haul timing.** A 12-hour daytime run like Nagpur-Pune is comfortable but full-day; for overnight intercity hops, watch for the new sleeper services as they expand.
- **Treat it as part of the itinerary, not just transit.** The large windows and smooth ride through the Maharashtra interior make the journey itself worth something — a slower, ground-level look at the country between the cities where family lives.

India's aviation map may be in turmoil this summer, with carriers cutting routes and reroutings stretching flight times. The railways, by contrast, are having a quietly good year — and for NRIs, the growing Vande Bharat network is becoming one of the easiest, least stressful ways to move around the country once you have landed."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
