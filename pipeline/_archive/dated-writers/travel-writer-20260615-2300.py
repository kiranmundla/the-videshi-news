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

uae_body = """If you live in the UAE and your Indian passport is up for renewal this summer, mark July 1 on your calendar — the office you walk into is about to change hands.

The Embassy of India in Abu Dhabi has confirmed that **Al Hind Tours and Travels LLC** will take over all outsourced Indian passport, visa, and consular services across the United Arab Emirates from **July 1, 2026**. The new provider replaces **BLS International Services** and **SGIVS Global**, which have handled these applications for years. The two outgoing operators will keep accepting and processing applications through **June 30**; anything filed before that date stays with them.

## What Al Hind will handle

The handover covers the full menu of services the roughly 3.5 million Indians in the UAE rely on:

- Passport renewals and re-issues
- Visa applications
- Overseas Citizen of India (OCI) cards
- Police Clearance Certificates (PCC)
- Surrender certificates (for those who took foreign citizenship)
- Global Entry Programme verification
- Document attestation

Al Hind has indicated it plans to operate **16 centres across the UAE**, with appointments and applications routed through a dedicated online platform. The embassy says service procedures will stay largely unchanged — the same forms, the same documents — so the disruption for most applicants should be procedural rather than substantive.

## Why an NRI in Dubai or Abu Dhabi should care

This is not an abstract bureaucratic reshuffle. The UAE is home to the largest Indian expatriate community anywhere in the world, and consular paperwork is a recurring fact of life: a child's first passport, a renewal before it lapses, an OCI card for a spouse, a PCC for a job or a green-card application back in the US. For NRIs who hold UAE residency as a stepping stone — and for the many Gulf-based Indians whose families have since spread to North America — getting these documents right and on time matters.

The practical advice for the next two weeks is simple. If your application is ready, **file before June 30** through the existing BLS or SGIVS centres and let the current system see it through. If you can wait, hold until Al Hind publishes its centre locations, operating hours, appointment procedures, and fee schedule — details the embassy says will come "in the coming weeks," before the transition takes effect. Starting a fresh application in the final days of June, only to have it caught mid-handover, is the one scenario worth avoiding.

## The backstory

The change did not come out of nowhere. India's Ministry of External Affairs **barred BLS International from bidding for new contracts for two years in October 2025**, following court cases and applicant complaints. When the UAE consular contract went out to tender, four firms — Al Hind, DU Digital Global, SGIVS Global, and VFS Global — submitted financial bids, opened on March 30, 2026. Al Hind came in as the lowest bidder and won the award, confirmed by the embassy in an official notice dated April 20.

## What to watch

A few open questions remain. Al Hind has said procedures will be "largely unchanged," but a new operator means new appointment portals, new centre addresses, and potentially new wait times as the system beds in. Fee structures have not yet been published. And the embassy has been emphatic on one point: rely only on **official embassy and consulate channels** for information. Transitions like this are fertile ground for scam websites and fake "appointment booking" services that harvest fees and personal data.

The bottom line for the diaspora: the service itself isn't going anywhere, but the front door is moving. Plan your paperwork around July 1, verify every link against the embassy's official site, and don't leave a time-sensitive renewal to the last week of June."""

sl_body = """India remains, by a wide margin, Sri Lanka's biggest source of tourists — and the island has just made the math even more inviting. For NRIs already flying home to India this year, a short hop across the Palk Strait now costs nothing at the visa counter.

Sri Lanka has scrapped the **Electronic Travel Authorisation (ETA) fee** for citizens of **40 countries**, including India, the United States, the United Kingdom, Canada, and the UAE. Under the scheme, which took effect on **May 25, 2026**, eligible travellers receive a **free 30-day tourist visa with double-entry access**. The change extends and broadens a pilot that originally waived fees for just seven countries — India, China, Russia, Japan, Thailand, Indonesia, and Malaysia.

## What's actually free, and what isn't

The important nuance: the **fee is gone, but the ETA is not**. Travellers still must apply online and secure approval before they fly. There is no turning up at Bandaranaike International and sorting it out on arrival — the authorisation has to be in hand first. The good news is that the application itself now carries no charge, and the double-entry feature means you can pop into Sri Lanka, slip over to the Maldives or back to India, and return within the same 30-day window without a fresh visa.

For NRIs, the double-entry detail is quietly useful. A common itinerary — fly into India for a family visit, take a week in Sri Lanka, dart to the Maldives, then circle back through Colombo — now works on a single free authorisation.

## Why this matters to the diaspora

Two reasons stand out.

First, **proximity and pairing**. Most NRIs visiting India already absorb the cost and jet lag of a long-haul flight. Sri Lanka sits a short flight from Chennai, Bengaluru, Mumbai, or Delhi, which makes it the natural add-on for a diaspora traveller who wants a beach-and-culture week without a second intercontinental ticket. Removing the visa fee — and the friction of paying it — lowers the bar for that side trip.

Second, **value**. Sri Lanka is in active recovery mode after its 2022 economic crisis and a softer-than-hoped 2026, when arrivals between March 1 and 25 fell 22% year-on-year amid regional tensions and disrupted air travel. A country courting tourists tends to be a country where the rupee — or the dollar — stretches further. Hotels, drivers, and guides are competing for visitors, and the free-visa push is a deliberate signal that Sri Lanka wants you there.

## What's on offer

For first-timers, the classic loop is hard to beat. The **Nine Arch Bridge at Ella**, a colonial-era railway viaduct framed by tea country, has become the island's most photographed landmark. **Sigiriya**, the fifth-century rock fortress, is a UNESCO World Heritage Site and a genuine wonder. Add the **Galle Fort** on the southern coast, the hill-country tea estates around **Nuwara Eliya**, and the beaches of the south and east, and a 10-day trip fills itself.

A practical note: Cyclone Ditwah disrupted hill-country access in late November 2025, but tourism officials say roads to Nuwara Eliya and Kandy have since reopened and resorts elsewhere were largely unaffected.

## The fine print

- The free ETA covers **30 days** with **double entry**.
- You **must apply online before departure** — the fee waiver does not remove the requirement to obtain authorisation.
- ETA fees **paid before May 25, 2026 are non-refundable**.
- The scheme has been described as a pilot running through **March 31**, so treat the window as time-limited and confirm current terms on Sri Lanka's official immigration portal before booking.

For an NRI weighing where to spend a week of an India trip, the calculus just shifted. Sri Lanka is close, it's cheap right now, and the one piece of paperwork it still demands no longer costs a thing."""

ai_body = """For the past three years, the story of Air India has been one of relentless expansion — new routes, new aircraft, refreshed cabins, a 470-jet order that was among the largest in aviation history. This summer, the story has changed. The Tata Group is pumping the brakes, and NRIs flying home between now and August will feel it.

Air India is **deferring aircraft deliveries, cutting flights, and postponing expansion** after Tata Group instructed the carrier to focus on stemming losses that have ballooned to roughly **$3 billion a year**. It is an abrupt reversal for an airline that, until recently, framed every quarter as another step in its post-privatisation "Vihaan.AI" transformation.

## What's being cut

Between **June and August 2026**, Air India is operating around **37% fewer international flights** than it did in April — roughly 1,240 international departures a month, down from 1,987 in April, according to aviation analytics firm OAG. Six international routes have been **temporarily suspended** outright:

- Delhi–Chicago
- Mumbai–New York
- Delhi–Shanghai
- Chennai–Singapore
- Mumbai–Dhaka
- Delhi–Malé

Frequencies to North America, Europe, and Australia are also being trimmed. Under the revised schedule, Air India is maintaining **33 weekly flights to North America**, 47 to Europe, 57 to the UK, and eight to Australia.

The airline blames a combination of factors: **airspace restrictions** tied to the Iran conflict and Pakistan's continuing ban on Indian carriers, which force longer reroutings, plus **record-high jet fuel prices** that, in May, ran 63% above pre-conflict levels. Together they have, in the airline's words, hurt "the commercial viability of certain planned services."

## Why this hits NRIs hardest

Two of the suspended routes — **Delhi–Chicago and Mumbai–New York** — sit squarely on the diaspora's most-travelled corridors. For the large Gujarati and Maharashtrian communities in the New York tri-state area, and for the Midwest's substantial Indian population around Chicago, these were marquee nonstops. Their suspension through August means more connecting itineraries, longer total travel times, and — in a peak summer travel season — fewer seats chasing the same demand, which tends to push fares up.

This compounds a squeeze NRIs are already feeling: India–US airfares have run sharply higher this summer, and Air India pulling capacity off exactly the routes the diaspora depends on removes a competitive anchor. When the national carrier thins its schedule, **foreign carriers** — Emirates, Qatar Airways, Etihad, and the European one-stops — gain pricing power on the India run.

## What affected passengers can do

Air India says it is offering travellers on cancelled flights **rebooking on alternative Air India services where possible, complimentary date changes, or full refunds**, depending on eligibility. If you are booked on one of the suspended routes this summer:

- Check your booking status directly and don't wait for the airline to reach you.
- If rebooking pushes you onto a long connection, ask about being re-accommodated on a partner carrier.
- Compare the refund option against rebooking — with fares elevated, a refund-and-rebook on another airline isn't always cheaper.

## The bigger picture

Behind the schedule changes is a structural reset. Air India is reportedly in talks with Airbus and Boeing to **defer hundreds of jet deliveries** — most scheduled for 2027 and 2028 — and is seeking at least 100 billion rupees in financial support. Singapore Airlines, which holds a 25.1% stake, has stayed in and continues to second senior operators to help run the airline. The carrier is also searching for a new chief executive after Campbell Wilson stepped down in April.

For the diaspora, the takeaway is pragmatic rather than alarmist. Air India isn't retreating from the US — it is still flying more than 1,200 international flights a month and says it will restore full operations "when circumstances allow." But for this summer specifically, the cushion is thinner. Book early, build in connection buffers, and keep an eye on your itinerary, because the carrier that spent three years adding seats to the India–US market has, for now, started taking some away."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Renewing Your Indian Passport in the UAE? The Office Changes Hands July 1",
        "subheadline": "Al Hind Tours and Travels takes over passport, visa, and OCI services from BLS and SGIVS across the Emirates — here's how the 3.5 million-strong Indian community should time their paperwork.",
        "slug": make_slug("indian-passport-uae-al-hind-replaces-bls-july-1-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "The UAE hosts the world's largest Indian expatriate community, and a switch in the outsourced provider for passports, visas, and OCI cards on July 1 affects every NRI in the Emirates with paperwork due this summer.",
        "tags": ["travel", "visa", "passport", "UAE", "OCI", "NRI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/india-new-visa-passport-service-provider-uae-al-hind/"},
            {"name": "Gulf Business", "url": "https://gulfbusiness.com/uae-alhind-replaces-bls-indian-consular-services/"},
            {"name": "Madhyamam Online", "url": "https://www.madhyamam.com/world/gulf/uae-al-hind-to-handle-indian-passport-visa-services-from-july-1"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19664340/pexels-photo-19664340.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Dubai's skyline, home to the world's largest Indian expatriate community",
        "image_attribution": "Pexels",
        "body": uae_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sri Lanka's Tourist Visa Is Now Free for Indians — and It's the Perfect NRI Side Trip",
        "subheadline": "A 30-day double-entry ETA at no cost makes the island the natural add-on to a family visit back home, though you still need to apply online before you fly.",
        "slug": make_slug("sri-lanka-free-eta-visa-indians-nri-side-trip"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "India is Sri Lanka's largest tourism market, and a free 30-day double-entry ETA turns the island into a low-cost, low-friction add-on for NRIs already flying home to India this year.",
        "tags": ["travel", "visa", "Sri Lanka", "ETA", "NRI", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/sri-lanka-free-30-day-tourist-eta-40-countries-india"},
            {"name": "Sri Lanka Department of Immigration and Emigration", "url": "https://www.immigration.gov.lk/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Nine_arch_bridge%2C_Ella%2C_Sri_lanka.jpg/1280px-Nine_arch_bridge%2C_Ella%2C_Sri_lanka.jpg",
        "image_caption": "The Nine Arch Bridge at Ella, Sri Lanka's most photographed landmark",
        "image_attribution": "Wikimedia Commons",
        "body": sl_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Is Cutting Summer Flights — and the Routes NRIs Use Most Are on the List",
        "subheadline": "Delhi-Chicago and Mumbai-New York are suspended through August as Tata forces loss control, thinning capacity on the diaspora's busiest corridors at peak season.",
        "slug": make_slug("air-india-summer-flight-cuts-suspended-routes-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Two of Air India's six suspended summer routes — Delhi-Chicago and Mumbai-New York — sit on the diaspora's most-travelled US corridors, meaning longer connections and higher fares for NRIs flying home through August.",
        "tags": ["travel", "airlines", "Air India", "flight cuts", "NRI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/air-india-seeks-defer-hundreds-jet-deliveries-sources-say-2026-06-12/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/air-india-cuts-june-august-international-flights-by-37-percent"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/air-india-cuts-planes-routes-tata-blocks-losses/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg/1280px-%28GBR-London%29_Air_India_Airbus_A350-941_VT-JRB_%40_EGLL_2025-06-18.jpg",
        "image_caption": "An Air India Airbus A350-900 at London Heathrow",
        "image_attribution": "Wikimedia Commons",
        "body": ai_body
    }
]

def wc(t):
    return len(t.split())

for art in articles:
    print(f"  [{art['slug']}] words={wc(art['body'])} headline_len={len(art['headline'])}")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
