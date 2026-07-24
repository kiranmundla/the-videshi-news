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

ETIHAD_BODY = """Etihad Airways has opened a three-day flash sale on business-class fares out of India, and for once the diaspora math is worth doing before the window slams shut. The Abu Dhabi carrier is selling lie-flat seats to more than 45 destinations across Europe, North America, Africa and Central Asia, with India-origin fares starting at ₹153,800 (roughly $1,840) round trip. Booking is open only from June 23 to June 25, 2026, for travel between July 1 and October 31 — which means the cheapest way to fly the family home in business class this autumn is decided this week, not in September.

## The numbers that matter

A long-haul business-class ticket from India to the US routinely runs ₹400,000–650,000 ($4,800–7,800) at peak. Etihad's promotional floor of ₹153,800 is an India-origin fare, so it rewards the traveller flying out of Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kochi or Ahmedabad first — not the NRI starting in New York. That distinction is the whole game for diaspora families.

The practical play: a parent or relative in India books the outbound-first itinerary to a US gateway, or an NRI times a round trip that originates in India during a visit home. Everything routes through Abu Dhabi's Zayed International, where Etihad has tightened its connection bank and rebuilt its lounge. For a 14-plus-hour journey broken by a single Gulf stop, a flat bed at a third of the usual business price is a genuinely different trip — especially for older parents the diaspora flies back and forth.

## Why this lands for NRIs

Indian Americans are among the heaviest premium-cabin buyers on the India–US corridor, disproportionately flying parents who can't easily manage 16 hours upright in economy. Etihad knows it: India is one of its fastest-growing outbound markets, and the one-stop-via-Abu-Dhabi model competes directly with Emirates via Dubai and Qatar via Doha. When one Gulf carrier blinks on business-class price, it usually drags the others toward matching deals within days — so even travellers who miss this specific sale should watch Emirates and Qatar fares through early July.

The catch worth reading twice: the ₹153,800 headline is a starting fare, not a US-route fare. North American destinations sit higher in the band, and seat availability at the lowest fare is capacity-controlled. Award-style scarcity applies — the cheapest buckets on the most popular dates (Diwali-season returns in October) will clear first.

## What to check before you book

- **Origin matters.** Price the trip starting from an Indian city; India-origin promo fares are the discounted ones.
- **Travel window.** Outbound and return must fall between July 1 and October 31, 2026.
- **Date flexibility pays.** The lowest fares are concentrated on off-peak departure dates; shifting a day or two can save five figures in rupees.
- **Compare the Gulf trio.** Run the same dates on Emirates and Qatar before committing — a flash sale from one often forces a quiet match from the others.
- **Mind the connection.** Build at least 2–3 hours at Abu Dhabi for the long-haul leg, more if you're travelling with elderly parents.

Flash sales are blunt instruments — they exist to fill seats on a fixed schedule, not to reward loyalty. But for the NRI who already planned an autumn trip home, this is the rare week where booking early and booking smart converge. The window closes June 25.
"""

PILOT_BODY = """India is about to change how it makes pilots — and the diaspora that depends on Indian carriers to fly home should pay attention to why. A government panel has proposed adopting the Multi-Crew Pilot Licence (MCPL), a simulator-heavy training route that would cut the hours cadets spend in real aircraft from at least 200 to as few as 100–120, with much of the rest logged in commercial-jet simulators. The draft report, reviewed by Reuters and prepared by a committee that included the aviation regulator, IndiGo and Air India, is a direct response to a pilot shortage that is throttling the fastest-growing aviation market on earth.

## What's actually being proposed

The MCPL was introduced by the UN's International Civil Aviation Organization in 2006 and is already used across Europe, Asia and the Middle East alongside traditional licensing. Instead of building hours flying small training aircraft, cadets train from early on for a specific airline's jets in high-fidelity simulators. Under the Indian draft, cadets would complete 100–120 hours in training aircraft, including at least 20 solo, then move much of their practical training into simulators — a route the report says "may shorten timeline for cadets."

The committee's logic is supply-side: India's airlines have ordered well over 1,000 aircraft between them, and there simply aren't enough pilots in the pipeline to crew them. A more predictable, carrier-specific training track is meant to turn out junior first officers faster and on schedule.

## Why this matters to NRIs

Every NRI who flies Air India or IndiGo home has a stake in whether those airlines can staff their flight decks. Pilot shortages are the quiet reason routes get delayed, frequencies get cut, or promised nonstops slip a season — the kind of disruption that turns a Diwali trip into a connection nightmare. A healthier pilot pipeline is, indirectly, a more reliable schedule on the SFO–BLR, JFK–BOM and ORD–DEL routes the diaspora actually books.

But the proposal cuts both ways, and the diaspora is right to ask hard questions. Reducing real-aircraft hours in favour of simulator time is precisely the kind of safety-versus-throughput trade-off that draws scrutiny — especially in a country where public confidence in aviation safety is sensitive. The draft itself hedges: the new route "can reduce manpower shortages" only "if implemented with strong regulatory oversight and industry collaboration." That conditional is doing a lot of work.

## The bigger picture

India's regulator, the DGCA, will collect airline responses before a final report goes to its head. IndiGo, Air India and the DGCA declined to comment on the draft. Globally, MCPL-trained pilots fly safely every day, so the model is not untested — the question is execution, oversight and whether Indian flight schools and simulators can scale quality alongside quantity.

For the diaspora, the takeaway is not alarm but awareness. The pilots crewing your next flight home are increasingly likely to have trained on a screen before they trained in the sky — a global norm India is now formalising. Whether that produces more reliable schedules without cutting corners on safety depends entirely on the oversight India builds around it. This is one aviation story worth following past the headline, because it shapes the dependability of the routes the diaspora lives by.
"""

VANDE_BODY = """For the NRI who flies into Delhi or Mumbai and then dreads the second leg — the overnight train to the home town, the one with the lurching old sleeper coaches — India's railways are quietly building the upgrade. The Vande Bharat Sleeper, the first long-distance overnight version of India's flagship semi-high-speed train, is moving from trials toward service, and it is poised to change the part of the India trip that the diaspora complains about most: getting from the metro to the mofussil.

## What the sleeper actually is

India has more than 160 Vande Bharat trains running, but until now they were all day trains — chair-car services for daytime city-to-city hops. The Sleeper variant, developed by BEML using Integral Coach Factory technology, is built for the overnight long-haul that defines real Indian travel. It offers fully air-conditioned AC 3-tier, AC 2-tier and First Class AC coaches, completed high-speed trials up to 180 km/h, and is certified for passenger service. The first route announced is Howrah (Kolkata) to Kamakhya (Guwahati) — a roughly 968 km, 14-hour run — with more corridors to follow as rakes roll off the line.

The pitch is simple: the comfort and cleanliness of a modern train, on the routes where Indians have historically had to choose between a cramped flight to a small airport or a tired old sleeper. For families connecting from an international arrival to a Tier-2 or Tier-3 home town, that middle leg is exactly where the journey used to fall apart.

## Why it lands for the diaspora

Most NRIs land at a metro — Delhi, Mumbai, Kolkata, Bengaluru, Chennai — but home is often somewhere the nonstop doesn't reach. The choice has been a connecting domestic flight (expensive, baggage-fee-laden, weather-prone) or an overnight train that, for returning diaspora used to Western rail, can be a jolt. A clean, quiet, AC sleeper that departs after an evening arrival and delivers you near home by morning is a genuinely better answer — and often cheaper than a same-day domestic connection with checked bags.

It also reframes the India trip itself. The Howrah–Guwahati route opens the Northeast — Assam, Meghalaya, the tea estates and Kaziranga — to diaspora families who'd written it off as too hard to reach. As the network expands, expect sleeper routes to knit the pilgrimage and heritage circuits (Varanasi, the Himalayan foothills, Rajasthan) into itineraries that no longer require a domestic flight for every hop.

## What to watch and how to plan

- **Routes are rolling out gradually.** Howrah–Kamakhya is first; check which corridors are live before building a train leg into your itinerary.
- **Book early.** Vande Bharat services run heavy demand; AC 2-tier and First Class AC sell out fastest, especially around festivals.
- **Use it as the connector.** Time an evening Vande Bharat Sleeper after an international arrival to reach a Tier-2 town by morning, skipping a pricey domestic flight.
- **Mind the season.** Northeast and hill routes are spectacular but weather-sensitive; the monsoon reshapes both scenery and reliability.

India's airports get the diaspora headlines, but the train is where the trip is won or lost. For the NRI tired of the metro-to-home-town scramble, the Vande Bharat Sleeper is the most quietly useful travel development of the year — not a flight, not a fare, but the missing middle leg finally getting an upgrade.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Etihad Is Selling Business Class to the US From India at a Third of the Usual Price — but the Window Shuts June 25",
        "subheadline": "A three-day flash sale puts lie-flat seats to 45-plus destinations within reach for diaspora families flying parents home this autumn — if you book from India and book now.",
        "slug": make_slug("etihad-business-class-flash-sale-india-origin-us-nri-autumn"),
        "category": "travel",
        "vertical": "airfare",
        "diaspora_angle": "Indian Americans are among the heaviest premium-cabin buyers on the India-US corridor, often flying elderly parents who can't manage 16 hours in economy; this India-origin sale puts a flat bed within reach for autumn trips home.",
        "tags": ["travel", "airlines", "etihad", "business class", "flight deals", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/etihad-airways-unveils-exclusive-india-origin-business-class-promotion/"},
            {"name": "Etihad Airways", "url": "https://www.etihad.com/en-us/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Boeing_787-9_-_Etihad_Airways_-_E-BOX.jpg/1280px-Boeing_787-9_-_Etihad_Airways_-_E-BOX.jpg",
        "image_caption": "An Etihad Airways Boeing 787-9 Dreamliner, the type that anchors its India long-haul network via Abu Dhabi",
        "image_attribution": "Wikimedia Commons",
        "body": ETIHAD_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants to Train Pilots on Simulators to Fix Its Crew Shortage — Here's What It Means for Your Flight Home",
        "subheadline": "A government panel has proposed a simulator-heavy licence that cuts real-aircraft hours nearly in half, a trade-off the diaspora that flies Air India and IndiGo should watch closely.",
        "slug": make_slug("india-multi-crew-pilot-licence-simulator-training-shortage-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Pilot shortages are the quiet reason diaspora routes get delayed or cut; a faster pilot pipeline could mean more reliable SFO-BLR, JFK-BOM and ORD-DEL schedules, but the safety trade-off deserves scrutiny.",
        "tags": ["travel", "aviation", "air india", "indigo", "pilots", "dgca", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-panel-proposes-simulator-heavy-pilot-licence-ease-crew-shortage-document-2026-06-24/"},
            {"name": "ICAO (Multi-Crew Pilot Licence)", "url": "https://www.icao.int/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Boeing_777-200LR_Flightdeck.jpg/1280px-Boeing_777-200LR_Flightdeck.jpg",
        "image_caption": "The flight deck of a Boeing 777-200LR, the wide-body type Air India flies on US nonstops",
        "image_attribution": "Wikimedia Commons",
        "body": PILOT_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Overnight Vande Bharat Is Coming — and It Fixes the Worst Leg of the Diaspora's India Trip",
        "subheadline": "The Vande Bharat Sleeper moves from trials toward service on the Kolkata-Guwahati route, finally upgrading the metro-to-home-town connection NRIs dread.",
        "slug": make_slug("vande-bharat-sleeper-overnight-train-nri-metro-hometown-connector"),
        "category": "travel",
        "vertical": "rail-tourism",
        "diaspora_angle": "Most NRIs land at a metro but home is a Tier-2 town the nonstop doesn't reach; a clean AC overnight sleeper is a cheaper, better alternative to a same-day domestic connection with checked bags.",
        "tags": ["travel", "india tourism", "vande bharat", "trains", "railways", "northeast india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia (Kamakhya-Howrah Vande Bharat Sleeper)", "url": "https://en.wikipedia.org/wiki/Kamakhya%E2%80%93Howrah_Vande_Bharat_Sleeper_Express"},
            {"name": "Wikipedia (Vande Bharat Express)", "url": "https://en.wikipedia.org/wiki/Vande_Bharat_Express"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Vande_Bharat_Sleeper_Express.jpg/1280px-Vande_Bharat_Sleeper_Express.jpg",
        "image_caption": "A Vande Bharat Sleeper Express trainset, India's first long-distance overnight semi-high-speed train",
        "image_attribution": "Wikimedia Commons",
        "body": VANDE_BODY
    }
]

# Word count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  [{wc} words] {art['headline'][:60]}")

print("---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
