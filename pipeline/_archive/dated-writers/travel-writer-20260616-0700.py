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
        "headline": "Air India's 'Easy Connect' Lets You Clear Immigration in Varanasi and Fly Through Delhi to the World",
        "subheadline": "The new hub-and-spoke model means Tier 2 and Tier 3 cities can check baggage through to a final international destination — a quiet but real upgrade for NRIs visiting family upcountry.",
        "slug": make_slug("air-india-easy-connect-hub-spoke-varanasi-tier2-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "NRIs whose families live beyond the big metros — Varanasi, and dozens of Tier 2 cities to follow — can finally start and finish an international trip from their hometown airport without re-checking bags or queueing for immigration at Delhi.",
        "tags": ["travel", "airlines", "air india", "varanasi", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Voice of Chandigarh — Air India Easy Connect", "url": "https://thevoiceofchandigarh.com/from-your-home-city-to-the-world-air-india-introduces-easy-connect-flights-leads-rollout-from-varanasi-on-25-june/"},
            {"name": "Air India newsroom", "url": "https://www.airindia.com/in/en/about-airindia/press-release.html"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg/1280px-%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg",
        "image_caption": "An Air India Airbus A350-900 (VT-JRB) at London Heathrow, the type now flying the carrier's marquee long-haul routes from Delhi.",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India has opened bookings for the first flights under the Indian government's new hub-and-spoke aviation model, branding them "Easy Connect." The first one lifts off on 25 June from Varanasi, and for any NRI who has ever lugged two suitcases off a domestic belt in Delhi and queued again to re-check them, the mechanics are worth understanding.

## What actually changes

Until now, a passenger flying from a smaller Indian city to, say, London almost always did it in two disconnected legs. You flew Varanasi–Delhi as a domestic passenger, collected your bags at Terminal 1, took the inter-terminal transfer to Terminal 3, re-checked everything, and cleared international immigration there — often with a tight, stressful connection.

Easy Connect collapses that into a single coordinated journey. Under the new model, travellers from "spoke" cities like Varanasi can:

- **Check baggage straight through** to the final international destination, with no collect-and-recheck at Delhi.
- **Complete international immigration at the origin airport**, so they arrive at the hub already cleared and simply walk to the onward gate.
- **Transit Delhi as international passengers**, inside a familiar Indian airport rather than a foreign one.

The inaugural flight, AI1111, departs Varanasi at 09:50 and lands in Delhi at 11:00. Within four hours, it is timed to feed 17 international departures — London Heathrow, Frankfurt, Zurich, Rome, Milan, Vienna, Copenhagen, Singapore, Kuala Lumpur, Bangkok, Manila, Phuket, Ho Chi Minh City, Riyadh, Dubai, Colombo and Kathmandu among them. Subsequent spoke flights will carry "AI11XX" numbers, so the network identity stays recognisable.

## Why this matters to the diaspora

The Indian American map does not stop at Delhi, Mumbai and Bengaluru. A large share of the diaspora traces home to Uttar Pradesh, Bihar, Punjab, Gujarat and the smaller cities that the metros overshadow. For decades, "going home" meant an international flight plus a separate, anxious domestic hop — and the connection at Delhi was the single most common place to miss a bag or a gate.

Varanasi is the proof of concept. The city is both a spiritual magnet and the constituency that anchors enormous diaspora sentiment. Letting a traveller from Kashi clear immigration at home and step off in Delhi already "international" removes the part of the trip NRIs complain about most: the messy, baggage-reclaim scramble in the middle.

Air India says the rollout will expand to more Tier 2 and Tier 3 cities in phases over the coming months. If the next wave includes places like Lucknow, Amritsar, Ahmedabad and Coimbatore — all cities with deep diaspora ties — the practical effect is that more NRIs can book a true through-fare from their family's nearest airport rather than routing everything through a metro.

## The fine print to watch

A few things are still unproven. The model depends on tight coordination between the airline, the spoke and hub airports, immigration officials and security — and on the four-hour connection window holding up in practice during monsoon delays and peak-season congestion. Through-checked baggage is only as reliable as the transfer system behind it, and Delhi's T3 has had its share of bottlenecks.

There is also the question of fares. Through-fares on hub-and-spoke itineraries are often priced as a single ticket, which is good for protection if a leg is delayed, but they are not automatically cheaper than booking the legs separately. NRIs comparing options should price both ways before assuming Easy Connect is the better deal.

## The bottom line

For now, Easy Connect is a single daily flight from one city. But the direction is the point: India is trying to make its smaller airports behave like real international gateways, and Air India is the carrier leading it. For a diaspora whose roots run well past the metros, that is the kind of unglamorous, logistics-level change that actually makes the trip home easier.

Bookings are open across Air India's website, app, contact centre and travel agents."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Mega-Airport Near Agra Is Almost Ready — and It Could Reshape How NRIs Fly Into North India",
        "subheadline": "Noida International Airport at Jewar is built to handle 120 million passengers a year and sits two hours from the Taj Mahal. For the diaspora in the NCR belt, a second Delhi-region gateway changes the math.",
        "slug": make_slug("noida-international-airport-jewar-nri-north-india-gateway"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The huge Indian American population with family across western Uttar Pradesh, the NCR suburbs and the Agra–Mathura belt gets a second major gateway that is closer to home than congested IGI Delhi — and a far shorter drive to the Taj Mahal.",
        "tags": ["travel", "airports", "noida", "jewar", "nri", "delhi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Sun — Noida International Airport", "url": "https://www.thesun.co.uk/travel/"},
            {"name": "Noida International Airport (official)", "url": "https://www.nia.co.in/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "Prime Minister Narendra Modi at the inauguration ceremony of Noida International Airport at Jewar.",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, flying into the Delhi region has meant one airport: Indira Gandhi International (IGI), one of the busiest in the world and, at peak hours, one of the most clogged. That near-monopoly is about to end. Noida International Airport at Jewar — a greenfield mega-hub spread across roughly 5,000 hectares — is in its final stretch before opening, and it is built on a scale that few airports anywhere can match.

## The numbers

When fully built, Jewar is designed to handle up to 120 million passengers a year, which would put it among Asia's largest airports. By land area it rivals Hyderabad's Rajiv Gandhi International, currently India's biggest. Both IndiGo and Akasa Air have confirmed operations there, though the early schedule is expected to lean heavily domestic, with international routes — names like Zurich and Dubai have been floated — still being firmed up.

The original target was September 2024; construction overran, and reporting now points to an opening in the near term rather than a confirmed date. NRIs should treat any specific launch claim with caution until the airport and airlines publish schedules.

## Why a second gateway matters to the diaspora

Two things make Jewar genuinely useful for Indian Americans, not just an aviation-trivia headline.

First, **proximity for the NCR belt.** A large share of the diaspora has family in Noida, Greater Noida, Ghaziabad and the fast-growing western UP suburbs. For them, IGI on the far side of Delhi can mean a long, traffic-choked haul across the capital after a 15-hour flight. Jewar sits on the other side — closer to home for that whole eastern arc of the NCR, and far less congested in its early years.

Second, **the Taj Mahal.** Agra draws up to eight million visitors a year, and most international tourists still fly into Delhi and drive nearly four hours south. Jewar cuts that to roughly two hours. For NRI families bringing American-born kids or visiting relatives to see the Taj, Mathura and Vrindavan, a gateway that halves the drive is a real quality-of-life upgrade on a tight holiday itinerary.

## What to watch before you book through it

The honest caveats matter here. A brand-new airport's international network takes time to mature; in the first phase, an NRI flying from the US will almost certainly still connect through Delhi, Mumbai or a Gulf hub rather than landing directly at Jewar. Direct long-haul service to North America is not on the near-term horizon.

Ground connectivity is the other variable. The airport is being tied into expressways and a planned rapid-transit link, but until those are fully operational, the "closer to home" advantage depends on which part of the NCR you are actually headed to. For someone going into central or south Delhi, IGI may still win on total door-to-door time.

## The bigger picture

Jewar is part of a broader Indian push to add gateway capacity rather than keep funnelling everything through a handful of saturated metros — the same logic behind Navi Mumbai's new airport and Air India's hub-and-spoke "Easy Connect" flights from smaller cities. For the diaspora, the payoff is gradual but clear: more entry points, shorter drives, and less dependence on a single overloaded airport every time you fly home.

For now, NRIs planning North India trips should keep Jewar on the radar but book against confirmed schedules. Once it opens and the route map fills in, it has a real shot at becoming the default arrival point for a big slice of the diaspora's family map."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Akasa Air Bets on Hanoi as the Gulf Stays Frozen — and Vietnam Is Quietly Becoming an NRI Favorite",
        "subheadline": "With Middle East routes suspended by the conflict, India's youngest airline is pivoting to Southeast Asia. A new Mumbai–Hanoi nonstop from 4 September gives the diaspora another visa-easy short-haul escape.",
        "slug": make_slug("akasa-air-mumbai-hanoi-vietnam-southeast-asia-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs who use India as a base for regional holidays — or who plan trips around visiting family in Mumbai — a new low-cost nonstop to Vietnam adds an affordable, visa-easy destination just as the Gulf transit corridor stays unreliable.",
        "tags": ["travel", "airlines", "akasa air", "vietnam", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Skift — Akasa Heads to Hanoi", "url": "https://skift.com/"},
            {"name": "Asian Aviation — Akasa Air adds Hanoi route", "url": "https://asianaviation.com/akasa-air-adds-hanoi-route/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Akasa_Air_737_max_8-200.jpg/1280px-Akasa_Air_737_max_8-200.jpg",
        "image_caption": "An Akasa Air Boeing 737 MAX 8-200, the workhorse of the carrier's expanding domestic and international network.",
        "image_attribution": "Wikimedia Commons",
        "body": """Akasa Air, the youngest entrant in India's crowded skies, is rerouting its international ambitions. Starting 4 September, the carrier will fly four weekly nonstops between Mumbai and Hanoi — its seventh international destination and a clear signal that, with the Gulf in turmoil, Southeast Asia has become its growth corridor.

## Why the pivot

Akasa built five of its first six overseas routes into the Middle East — Doha, Jeddah, Riyadh, Abu Dhabi and Kuwait City — with plans to deepen that footprint as bilateral rights opened up. The Iran-linked conflict and the resulting airspace closures upended that strategy. Several of those Gulf routes have been suspended, leaving Jeddah as the airline's lone reliably operating Middle East destination. Westward expansion stalled; the obvious alternative was to fly east.

Phuket was Akasa's first Southeast Asian foray. Hanoi is the bolder follow-up — a full-service capital city, not just a beach resort — and it slots into a region where Indian outbound travel is booming.

## Vietnam's quiet rise with Indian travelers

Vietnam has become one of the most talked-about short-haul destinations for Indians, and the diaspora angle is real. Three things drive it:

- **Visa ease.** Vietnam's e-visa process is straightforward for Indian passport holders, sparing the paperwork that makes Schengen or even some Gulf transit trips a chore.
- **Value.** Hanoi, Ha Long Bay, Da Nang and Hoi An deliver a big-trip feel at a fraction of European prices — a strong pitch for NRI families combining a India visit with a regional getaway.
- **Vegetarian-friendly, family-friendly.** Vietnamese cuisine and the country's compact, scenic geography make it an easy sell for multi-generational groups, the kind of trip diaspora families often plan around an India visit.

Travel-industry chatter has increasingly framed Vietnam as "stealing Thailand's crown" with Indian tourists — helped along by Thailand's recent move to cut Indians' visa-free stay to 15 days, which nudged some travellers to look elsewhere.

## What it means for NRIs specifically

Most Indian Americans will not fly Akasa across the Pacific — it is a narrowbody, short-to-medium-haul carrier. The value is in how the diaspora actually travels: many NRIs base a trip in Mumbai to see family, then tack on a regional holiday. A direct, low-cost Mumbai–Hanoi link makes Vietnam an easy add-on rather than a separate, expensive expedition.

It also reflects a healthier competitive map. As Akasa, IndiGo and Air India all push into Southeast Asia, fares on these India–ASEAN corridors should stay keen, and frequencies should grow — good news for anyone building a two-country itinerary around a home visit.

## The caveats

Four weekly flights is a modest start, and Akasa's near-term international story is still hostage to when — and whether — its Gulf routes come back. Schedules on a new route can shift, and a single narrowbody frequency offers limited rebooking flexibility if a flight is disrupted. NRIs booking the inaugural season should keep an eye on Akasa's updates and avoid stacking tight onward connections in the first weeks of operation.

Still, the direction of travel is encouraging. India's newest airline is finding room to grow despite a frozen Gulf, and the diaspora gets one more affordable, visa-easy door into a region that is fast becoming a favorite."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\nTotal inserted: {len(inserted)}")
for h in inserted:
    print(" -", h)
