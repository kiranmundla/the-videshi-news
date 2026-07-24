#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

vande_body = """India's railways crossed a quiet milestone this week. With Prime Minister Narendra Modi due to flag off five more Vande Bharat Express trains on June 27, the country's semi-high-speed fleet pushes past 160 services — and the latest additions are aimed squarely at the temple towns and heritage circuits that draw the diaspora home.

The four trains launched from Varanasi earlier this month set the template. The headline service, Banaras–Khajuraho, links Varanasi, Prayagraj, Chitrakoot and the UNESCO World Heritage temples of Khajuraho, cutting roughly **2 hours 40 minutes** off the existing run. Lucknow–Saharanpur shaves nearly an hour and opens up Haridwar via Roorkee. Firozpur–Delhi, at 6 hours 40 minutes, becomes the fastest train on a route threading Bathinda and Patiala. In the south, Ernakulam–Bengaluru drops the Kerala–Karnataka hop to 8 hours 40 minutes, connecting two of India's busiest IT corridors.

## What the new trains actually change

The Vande Bharat pitch is not just speed. These are fully air-conditioned, automatic-door trainsets with reserved chair-car seating, on-board catering and a punctuality record that conventional long-distance trains rarely match. For a family arriving jet-lagged into Delhi or Varanasi, the difference between a lurching overnight express and a clean, predictable day train is the difference between a wasted day and a usable one.

The routing tells you who the trains are for. India's railway ministry has leaned hard into the pilgrimage-and-heritage map: Varanasi, Khajuraho, Haridwar, Katra, Ajmer, Dehradun. These are precisely the stops on a typical NRI itinerary — the temple visit slotted between a wedding in one city and ageing parents in another.

## Why this matters to the diaspora

For Indian-American families, the hardest part of a trip home is rarely the transatlantic leg. It is the last 300–500 kilometres — the connection from a metro arrival airport to the ancestral town or the pilgrimage site, historically done by an overnight train booked months ahead or a long, tiring car ride. The Vande Bharat network is steadily collapsing those segments into daytime, same-day journeys you can book around a jet-lagged body clock.

The Banaras–Khajuraho service is the clearest example. Khajuraho's temples are a bucket-list stop, but the town has long been awkward to reach without a domestic flight or a punishing road transfer. A direct, modern train from Varanasi — itself a major NRI arrival and pilgrimage hub — folds a second heritage destination into a trip that previously had room for only one.

There are practical limits worth flagging. Vande Bharat trains sell out fast on pilgrimage corridors, and IRCTC's booking window opens 60 days ahead — so for a November or December trip, the smart move is to lock seats the moment the window opens, not after landing. Foreign-passport holders and OCI card-holders can book through IRCTC's international payment gateway or via an agent; there is no separate tourist quota on most Vande Bharat services, so early booking is the only real edge.

## What's next

The network's most-watched extension — a full Vande Bharat into the Kashmir Valley over the Chenab rail bridge — remains on a phased rollout, with the upgraded Jammu–Srinagar service still awaiting a revised schedule while the existing Katra–Srinagar train carries the load. Officials have signalled that more heritage-circuit routes are in the pipeline as trainset production scales.

For the diaspora, the takeaway is simple: the India you fly home to is getting easier to move around in, one corridor at a time. The trick is to treat Vande Bharat seats like festival-season flights — book early, book specific, and build the itinerary around the train rather than hoping to catch one on arrival.

**Sources:** Prime Minister's Office (pmindia.gov.in); The Indian Eye; Travel And Tour World."""

vande = {
    "id": str(uuid.uuid4()),
    "headline": "India's Vande Bharat Fleet Tops 160 Trains — and the New Routes Run Straight Through the Diaspora's Pilgrimage Map",
    "subheadline": "Five more semi-high-speed trains launch June 27, linking Varanasi, Khajuraho, Haridwar and Bengaluru. For NRI families, the hardest leg of the trip home just got shorter.",
    "slug": make_slug("vande-bharat-160-trains-new-heritage-routes-khajuraho-nri-pilgrimage"),
    "category": "travel",
    "vertical": "tourism",
    "diaspora_angle": "The new Vande Bharat heritage-circuit trains collapse the hardest part of an NRI trip home — the last-mile connection from arrival metros to temple towns and ancestral cities — into clean, same-day daytime journeys.",
    "tags": ["travel", "india", "rail", "vande-bharat", "tourism", "heritage"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Prime Minister's Office", "url": "https://www.pmindia.gov.in/en/news_updates/pm-to-visit-varanasi-and-flag-off-4-new-vande-bharat-trains/"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Howrah%E2%80%93Puri_Vande_Bharat_Express_at_Balasore_railway_station_1.jpg/1280px-Howrah%E2%80%93Puri_Vande_Bharat_Express_at_Balasore_railway_station_1.jpg",
    "image_caption": "A Vande Bharat Express trainset at an Indian railway station; the semi-high-speed fleet has crossed 160 services.",
    "image_attribution": "Wikimedia Commons",
    "body": vande_body
}

uae_body = """If you are an Indian national in the UAE and your passport, visa paperwork or document attestation is anywhere near a deadline, the calendar just tightened. The Embassy of India in Abu Dhabi has confirmed that routine passport, visa and attestation services across the Emirates will be **suspended for five days, from June 26 to June 30**, as consular work shifts to a new outsourced provider.

The transition is a big one. From **July 1**, Al Hind Tours and Travel LLC takes over passport, visa and attestation services across the UAE, replacing the two incumbents — BLS International, which handled passport and visa work, and SGIVS Global, which handled attestation. Both stop accepting new applications after the close of business on **June 25**.

## What is actually closing, and when

Between June 26 and June 30, no routine appointments will be available for passport renewal, visa services or document attestation. Applications already submitted before the cut-off will continue to be processed through the existing centres. From July 1, all new applications route through Al Hind, which plans to open a fresh online appointment portal and is reportedly building out 16 dedicated centres across all seven emirates, including hubs in Abu Dhabi, Dubai and Fujairah.

Emergency services do not stop. The Embassy of India in Abu Dhabi and the Consulate General of India in Dubai will directly handle urgent passport, visa and attestation cases throughout the five-day window. Anyone in a genuine emergency can reach the missions via the toll-free line **800 46342 (800 INDIA)**, WhatsApp at **+971 54 309 0571**, or email **pbsk.dubai@mea.gov.in**.

## Why this matters to the diaspora

This is not an abstract administrative reshuffle. The UAE is home to roughly **3.5 million Indians** — close to 40% of the country's population — and it functions as one of the busiest connective tissues of the entire global diaspora. Indians in the Gulf shuttle constantly between Dubai, Abu Dhabi and Sharjah and cities like Mumbai, Delhi, Hyderabad, Chennai and Kochi, and a huge share of family travel, job changes and document legalisation runs through exactly the services that are pausing.

The practical risk is timing. A child's passport expiring before a summer trip home, a work-visa stamping tied to a new contract, a degree certificate that needs attestation before a job offer clears — any of these can slip if the paperwork is not lodged before June 25. Five days does not sound like much, but stacked onto an already busy summer travel season and the lead time a new provider needs to find its feet, it can cascade into weeks of delay for anyone who waits.

There is a second-order angle for the wider NRI community. Document attestation handled in the UAE frequently feeds onward processes in the US, Canada and UK — degree and marriage certificates attested in the Gulf are used for green-card, spousal-visa and professional-licensing files abroad. A hiccup in Abu Dhabi can ripple into a delayed filing in New Jersey or Toronto.

## What to do before June 25

The guidance from the missions is blunt: if you have anything in the pipeline, submit it before June 25, or wait for the new system on July 1. A few concrete steps:

- **Check expiry dates now** on every family passport and residence visa, especially for travel planned in July and August.
- **Lodge attestation requests early** if any document is tied to an overseas filing deadline.
- **Save the emergency channels** — the toll-free number, WhatsApp line and email — in case a genuine urgency lands during the closure.
- **Expect a learning curve** in early July as Al Hind's portal and centres come online; build buffer time into any deadline that falls in the first half of the month.

## What's next

The embassy says arrangements are being made for a smooth handover, and Al Hind's larger centre network could eventually mean shorter queues than the two-provider system it replaces. But the immediate story for the diaspora is one of a narrow window: act before June 25, or plan around a five-day gap that lands right at the start of peak summer travel.

**Sources:** Embassy of India, Abu Dhabi (via Khaleej Times / The Gulf Gazette); What's On UAE; AInvest."""

uae = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Passport and Visa Services in the UAE Go Dark for Five Days — Here's the Window Before June 25",
    "subheadline": "Consular work shifts to a new provider, Al Hind, from July 1. Routine passport, visa and attestation services pause June 26–30, with only emergencies handled in between.",
    "slug": make_slug("indian-passport-visa-services-uae-suspended-june-al-hind-takeover-nri"),
    "category": "travel",
    "vertical": "immigration",
    "diaspora_angle": "With 3.5 million Indians in the UAE and the Gulf acting as a hub for the wider diaspora, a five-day pause in passport, visa and attestation services at the start of peak summer travel can cascade into missed trips and delayed filings abroad.",
    "tags": ["travel", "visa", "passport", "uae", "diaspora", "consular"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "What's On UAE", "url": "https://whatson.ae/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/"},
        {"name": "The Gulf Gazette", "url": "https://thegulfgazette.com/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Indian_Passport_01.jpg/1280px-Indian_Passport_01.jpg",
    "image_caption": "An Indian passport; consular services in the UAE pause June 26–30 during a provider transition.",
    "image_attribution": "Wikimedia Commons",
    "body": uae_body
}

swiss_body = """Bengaluru is about to get its first nonstop link to Switzerland. From **October 28**, Swiss International Air Lines will fly five times a week between Kempegowda International Airport (BLR) and Zurich — the carrier's third gateway into India after Mumbai and Delhi, and a notable bet on southern India's premium travel demand.

The schedule is built for the business traveller. The westbound LX 141 leaves Bengaluru at **04:50** and lands in Zurich at **10:50** the same morning; the return LX 140 departs Zurich at **13:20** and arrives in Bengaluru at **02:55** the next day. Both run five days a week, with First, Business and Economy cabins — and, unusually, First Class on every flight.

## A Lufthansa Group play, not just a SWISS route

This is one piece of a much larger Lufthansa Group push into India, now the group's biggest intercontinental market in Asia-Pacific. Alongside the new Bengaluru service, the group is adding summer frequencies — two extra weekly Frankfurt–Chennai flights, more to Delhi and Hyderabad, an additional Munich–Bangalore rotation, and seven extra weekly SWISS flights to Delhi. Lufthansa is also rolling out its new Allegris cabins on Boeing 787-9 services from Delhi and Hyderabad, and bigger A380s on Mumbai–Munich.

The timing dovetails with a quieter but consequential change: as of **June 3**, Germany scrapped the airport transit visa requirement for Indian passport holders, following France in April. For an Indian traveller connecting through Frankfurt, Munich or Zurich to a non-Schengen destination, that removes a paperwork hurdle that used to make European hubs a hassle.

## Why this matters to the diaspora

For the Indian-American who started life in Bengaluru — or whose parents still live there — the route quietly reshapes the trip home. Until now, a Bay Area or East Coast techie heading to Bengaluru typically routed through a Gulf hub or through Frankfurt/Munich with a connection. A nonstop BLR–ZRH leg plugs Bengaluru directly into the Star Alliance and Lufthansa Group network, opening one-connection itineraries to dozens of US and European cities via Zurich.

The logic is explicitly diaspora-aware. SWISS and Lufthansa cite the "growing Indian diaspora across Europe and beyond" as a core driver, and Bengaluru's pull is unmistakable: it is India's tech capital, the source of a disproportionate share of H-1B and L-visa workers in the US, and a city whose families travel constantly for work, education and weddings. Bengaluru airport's own network — 78 domestic destinations — means single-ticket transfers from Tier 2 and Tier 3 southern cities feed straight into the Zurich flight.

There is a premium-cabin angle too. South India has long been underserved for genuine First and Business product on European carriers compared with Mumbai and Delhi. SWISS putting First Class on every BLR rotation, plus Lufthansa's Allegris rollout from Delhi and Hyderabad, signals that carriers now see southern India as a market worth their best hardware — which over time tends to pull fares and award availability in travellers' favour.

## The practical read

A few things to keep in mind:

- **Winter schedule launch:** the route starts late October, so it is a play for holiday-season and 2027 travel, not this summer.
- **Connection quality:** Zurich is a compact, efficient hub — good for tight transfers to onward Europe and North America, with First and Business lounge access for premium cabins.
- **Watch the fare war:** more Lufthansa Group capacity into India, plus Gulf carriers and a recovering Air India, means the India–Europe and India–US premium market is getting more competitive. That is good news for anyone booking business class home.

## What's next

The Bengaluru launch caps a year in which European carriers have steadily re-weighted toward India. With transit-visa friction easing and capacity climbing across Frankfurt, Munich, Zurich and beyond, the southern Indian diaspora — long routed through someone else's home city — is finally getting nonstop options of its own.

**Sources:** Swiss International Air Lines (swiss.com); Lufthansa Group Newsroom; Travel Trade Journal / ANI."""

swiss = {
    "id": str(uuid.uuid4()),
    "headline": "Bengaluru Finally Gets a Nonstop to Europe — SWISS Launches a Five-a-Week Zurich Link in October",
    "subheadline": "It's the Lufthansa Group's third India gateway, with First Class on every flight. For southern India's diaspora, the trip home no longer has to route through someone else's city.",
    "slug": make_slug("swiss-bengaluru-zurich-nonstop-lufthansa-group-india-nri-tech-capital"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "A nonstop Bengaluru–Zurich service plugs India's tech capital — and the H-1B-heavy southern diaspora — directly into the Lufthansa Group and Star Alliance network, opening one-connection routes to US and European cities that previously required routing through Mumbai, Delhi or a Gulf hub.",
    "tags": ["travel", "airlines", "swiss", "lufthansa", "bengaluru", "aviation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Swiss International Air Lines", "url": "https://www.swiss.com/"},
        {"name": "Lufthansa Group Newsroom", "url": "https://newsroom.lufthansagroup.com/"},
        {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Swiss_Airbus_A330-300_HB-JHM_IAD_VA1.jpg/1280px-Swiss_Airbus_A330-300_HB-JHM_IAD_VA1.jpg",
    "image_caption": "A Swiss International Air Lines Airbus A330-300; the carrier launches nonstop Bengaluru–Zurich flights on October 28.",
    "image_attribution": "Wikimedia Commons",
    "body": swiss_body
}

articles = [vande, uae, swiss]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
