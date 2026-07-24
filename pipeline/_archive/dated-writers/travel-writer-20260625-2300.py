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

body_lounge = """Air India now has a signature lounge on American soil, and it sits exactly where the Bay Area's enormous Indian community boards its flights home. The carrier opened its first overseas Maharaja Lounge at San Francisco International Airport on May 23, a 3,300-square-foot space near the A Gates in the International Terminal. It is the airline's second flagship lounge after the one at Delhi's Terminal 3, and the first outside India since the Tata Group took the carrier over in January 2022.

For the hundreds of thousands of Indian-Americans clustered around San Jose, Fremont and the wider Bay Area, this is not an abstract upgrade. SFO is the single most important West Coast gateway to India, and Air India runs nonstop service from here to Delhi and Bengaluru. Until now, premium passengers on those long hauls cleared security and waited in a generic shared lounge or none at all. The Maharaja Lounge changes the pre-flight ritual for the leg that matters most.

## What's inside

The lounge was designed by the global hospitality firm Hirsch Bedner Associates, and it leans into Indian craft and culture rather than generic airport luxury. The food program centers on a buffet of Indian cooking — dal Bukhara, chicken tikka masala, vegetable biryani, paneer, and a beet-and-fig kofta called sham savera — alongside live cooking stations turning out uttapam and other made-to-order items. There are international options too, including grilled salmon and roasted vegetables, plus a self-serve station for coffee, chai, juices and soft drinks throughout the day.

The centerpiece for many will be the Aviator's Bar, a moody, speakeasy-style cocktail space stocked with curated wines and whiskeys. Two signature drinks nod to India: the Limitless, a gin cocktail infused with saffron, rose and hibiscus, and the Maharaja Manhattan, a black-pepper riff on the classic that references India's centuries-long role in the global spice trade.

## Who gets in

Access is restricted to Air India's First and Business Class passengers, plus Platinum and Gold members of the carrier's Maharaja Club loyalty program. The lounge is expected to operate daily from roughly 6:30 a.m. to 10 p.m., with hours flexing around flight schedules. Travelers should turn left after clearing security, walk past the Air France lounge, take the escalators up one level, and follow the signage.

## Why it matters for the diaspora

This lounge is the most visible sign yet that Air India's expensive, slow transformation is finally reaching the routes Indian-Americans actually fly. North America is one of the carrier's most important markets — it operates around 65 weekly flights between the region and India — and CEO Campbell Wilson has called the continent a critical pillar of the airline's global network strategy.

That matters because the diaspora's loyalty to Air India has been tested. The carrier logged a record annual loss of more than $2 billion, and Pakistan's closure of its airspace to Indian carriers has forced longer, costlier routings on exactly these long hauls. Gulf carriers like Emirates, Etihad and Qatar Airways have spent years winning over NRI travelers with superior hard products and hub lounges in Dubai, Abu Dhabi and Doha. A genuinely good lounge at SFO is Air India's bid to claw back the premium flier who has options.

There is a practical calculation here too. If you are weighing a one-stop Gulf itinerary against an Air India nonstop from SFO, the lounge tips the math slightly. A nonstop already saves you a connection and the missed-flight risk that comes with it; now the pre-flight wait comes with proper Indian food and a real bar rather than a sad sandwich at the gate. For families traveling with elderly parents or young children — a common NRI scenario on the India run — a comfortable, familiar space before a 15-hour flight is worth more than the price of the Business Class seat alone.

The lounge also signals where Air India is headed. Wilson has framed SFO as the start of a broader global lounge network, with a new domestic lounge planned for Delhi's T3 in the second half of 2026 and the premium overhaul rolling out across the fleet's retrofitted cabins. For the diaspora, the test will be consistency: whether the SFO standard holds at JFK, and whether the cabin product on the aircraft finally matches the lounge on the ground.

Sources: The Points Guy, AFAR, TravelBiz Monitor, The Economic Times."""

body_goa = """Goa in July is the version of Goa almost no NRI ever sees. The shacks are shuttered, the sea is rough and roped off, the charter crowds are gone — and that is precisely the point. For diaspora visitors who only know Goa as a December beach destination jammed with tourists, the monsoon offers a quieter, greener, far cheaper state that rewards a different kind of trip.

This is timely for a specific reason. Many Indian-American families travel to India during the US summer break, June through August, when kids are off school. That window lands squarely in the monsoon, which most guidebooks treat as the season to avoid. For Goa, the conventional wisdom is wrong.

## What the rain unlocks

Dudhsagar Falls, the four-tiered cascade on the Goa-Karnataka border, is at its thundering best only during and just after the monsoon. In the dry season it shrinks to a trickle; in July it is a wall of white water, which is exactly when it earns its name, "sea of milk." Access is via jeep safari through the Bhagwan Mahaveer sanctuary, and the train-track viewpoint is one of the most photographed spots in the state.

The rains also empty Old Goa's UNESCO-listed churches. The Basilica of Bom Jesus, which holds the relics of St. Francis Xavier, and the Se Cathedral draw heavy tour-group traffic from October to March. In July and August you may have these 400-year-old interiors — the azulejo tilework, the vast courtyards — almost to yourself. Entry to both is free.

Then there are the experiences that only exist in the wet season. Operators in Panjim run guided kayak tours through flooded rice-paddy channels and the backwaters around Divar Island and the Cumbarjua canal, roughly ₹800–1,200 for a two-to-three-hour session. The paddies flood in July and August into a maze of shallow waterways flanked by green fields and coconut palms — a landscape that simply does not exist the rest of the year. South Goa's hinterland trails, run by outfits like Soul Travelling, pair plantation walks with hands-on Goan cooking and river dips, and consistently draw rave reviews from monsoon visitors.

The monsoon also overlaps with two of Goa's most local festivals. Sao Joao, in late June, sees revelers leap into wells and water tanks to celebrate the feast of St. John the Baptist; Bonderam, on Divar Island in August, is a mock-battle flag festival rooted in old Portuguese boundary disputes. Neither is staged for tourists, which is the appeal.

## The honest caveats

This is not a beach-and-party trip, and pretending otherwise sets families up for disappointment. The Arabian Sea turns dangerous in the monsoon — swimming is risky and often officially banned, and water sports shut down entirely. Most beach shacks, especially in North Goa, close for the season. The nightlife that defines high-season Goa is dialed way down. Rain can be heavy and unpredictable, bringing muddy roads, occasional power cuts and travel delays.

So the monsoon trip works for a specific traveler: someone who wants greenery, waterfalls, heritage, food and quiet over sunbathing and clubs. For NRI families, it pairs especially well with a multi-generational visit where the goal is to show kids a side of India that is lush and unhurried rather than to chase a beach holiday.

## The diaspora math

The savings are real. Monsoon is Goa's deepest off-season, and room rates at properties that would be booked solid in December fall sharply — luxury resorts that run well above ₹20,000 a night in peak season can be had for a fraction of that, and mid-range stays drop accordingly. Flights into Goa's Mopa and Dabolim airports are cheaper too, and the connecting legs from Delhi, Mumbai or Bengaluru — where most diaspora travelers land first — are far less crowded.

For a family already flying to India over the summer, a few days in monsoon Goa is one of the lowest-cost, lowest-crowd add-ons available, and it delivers a version of the state that the December crowds never get to see. Pack quick-dry clothes and real footwear, keep the itinerary loose enough to dodge the heaviest downpours, and skip the beach plans. The rest of Goa is wide open.

Sources: Tripoto, Tripadvisor, StayVista Journal."""

body_bali = """Bali remains one of the easiest international escapes for Indian travelers, and for the diaspora it is an obvious add-on to a summer trip home. But the island's entry rules have quietly tightened over the past two years, and the difference between a smooth arrival and a 90-minute immigration crawl now comes down to paperwork you sort before you fly. Here is what Indian passport holders need to know for 2026.

## The visa: e-VOA beats the airport counter

Indian citizens cannot enter Bali visa-free. The standard route is the Visa on Arrival (VOA), which costs IDR 500,000 — roughly ₹2,800 — and grants a 30-day stay, extendable once for another 30 days. You can pay it at a counter at Ngurah Rai International Airport, but during peak hours that counter feeds into queues of 30 to 90 minutes, and late-night arrivals from India routinely face the longest waits.

The smarter option is the e-VOA, applied for online at the official Indonesian immigration portal (molina.imigrasi.go.id) two to five working days before departure. It costs the same IDR 500,000 but is pre-approved, lets you skip the payment counter and walk straight to immigration, and dramatically cuts the risk of an entry hiccup. For the overwhelming majority of Indian travelers, the e-VOA is worth the small extra planning.

## The tourist levy everyone forgets

Separate from the visa, Bali charges every international arrival a one-time tourism levy of IDR 150,000 — about ₹850 or $10. It applies to everyone, including children, and it funds beach cleanups, cultural preservation and waste management on an island straining under overtourism.

The catch is that the levy is widely missed: surveys have found that fewer than half of arriving tourists actually pay it, mostly because they have never heard of it. Officials run random checks at the airport and at top sites like the Uluwatu temple, and a missing receipt can mean an awkward delay. Pay it before you fly through the official Love Bali website or app, save the QR-code voucher to your phone, and you are covered. Note that the levy is charged per entry — if you island-hop out of Bali and return during the same trip, you pay again.

## The new arrival card and the overstay trap

Indonesia now also requires the All Indonesia Arrival Card, a digital customs and health declaration submitted online before landing; you show its QR code at customs alongside your passport and visa. Combined with the e-VOA and the Love Bali levy receipt, that means three separate QR codes you should have saved offline on your phone before you reach the immigration hall.

Take the overstay rules seriously. Bali fines overstays at IDR 1,000,000 per day — roughly ₹5,300 — and serious overstays can trigger a deportation record and a future entry ban. If your plans stretch, extend the VOA once before it expires rather than gambling on the last day.

## Why this is a natural diaspora trip

For Indian-Americans, Bali sits in a sweet spot. It is a manageable connection from the major Indian metros — direct and one-stop options run from Delhi, Mumbai and Bengaluru — which makes it easy to bolt onto a summer visit home rather than flying all the way from the US. The rupee goes a long way on the island, accommodation spans backpacker guesthouses to world-class resorts, and the cultural texture — Hindu temples, elaborate offerings, festival processions — is familiar enough to feel welcoming yet distinct enough to feel like a real holiday.

There is also a vegetarian-friendliness that many Indian families appreciate: Bali's own Hindu-influenced cuisine and its long backpacker history mean meat-free and Indian food are easy to find in tourist hubs like Ubud, Seminyak and Canggu. For multi-generational trips, that lowers the friction that often complicates a family holiday abroad.

The bottom line for 2026: the trip itself is as appealing as ever, but the admin has grown. Budget around ₹3,650 per person in mandatory fees (the IDR 500,000 visa plus the IDR 150,000 levy), apply for the e-VOA and the arrival card online before you leave, pay the Love Bali levy in advance, and save all three QR codes offline. Do that, and you walk off the plane and into the holiday instead of into the queue.

Sources: Trip.com, Wise, VisaForTrip, The Points Guy."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Just Opened Its First US Lounge at SFO — the Bay Area's Gateway Home",
        "subheadline": "The 3,300-square-foot Maharaja Lounge near the A Gates is the carrier's first overseas signature lounge, landing exactly where the West Coast diaspora boards its nonstops to Delhi and Bengaluru.",
        "slug": make_slug("air-india-sfo-maharaja-lounge-first-us-bay-area-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "SFO is the West Coast's most important gateway to India, and Air India's first US lounge gives the Bay Area's huge Indian community a proper premium space before its nonstops home — a direct bid to win NRI fliers back from the Gulf carriers.",
        "tags": ["travel", "airlines", "air india", "sfo", "lounge", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Points Guy", "url": "https://thepointsguy.com/news/air-india-maharaja-lounge-sfo/"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/air-india-opens-maharaja-lounge-at-san-francisco-airport"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/"},
            {"name": "The Economic Times", "url": "https://economictimes.indiatimes.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/55/Air_India%2C_VT-ANP%2C_Boeing_787-8_Dreamliner.jpg",
        "image_caption": "An Air India Boeing 787-8 Dreamliner, the type that flies the carrier's SFO nonstops to India.",
        "image_attribution": "Wikimedia Commons",
        "body": body_lounge
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Goa Almost No NRI Sees: Why a Monsoon Trip Beats the December Crush",
        "subheadline": "Shuttered shacks, empty 400-year-old churches and Dudhsagar at full roar — for diaspora families traveling over the US summer break, monsoon Goa is the cheapest, quietest version of the state.",
        "slug": make_slug("goa-monsoon-travel-dudhsagar-old-goa-offbeat-nri-summer"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "NRI families who travel to India over the US summer break land right in the monsoon — the season guidebooks say to avoid — yet for Goa that is exactly when waterfalls, heritage and quiet peak and prices crash.",
        "tags": ["travel", "goa", "monsoon", "india", "nri", "destinations"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Tripoto", "url": "https://www.tripoto.com/goa"},
            {"name": "Tripadvisor", "url": "https://www.tripadvisor.com/"},
            {"name": "StayVista Journal", "url": "https://www.stayvista.com/journal"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Dudhsagar_Falls%2CGoa.jpg",
        "image_caption": "Dudhsagar Falls on the Goa-Karnataka border, at its fullest during and just after the monsoon.",
        "image_attribution": "Wikimedia Commons",
        "body": body_goa
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Bali's Entry Rules Quietly Tightened — Here's the 2026 Checklist for Indian Travelers",
        "subheadline": "An e-VOA, a tourist levy most arrivals forget, and a new arrival card mean three QR codes between you and the holiday. Sort them before you fly and skip the 90-minute queue.",
        "slug": make_slug("bali-entry-rules-2026-indians-evoa-tourist-levy-arrival-card-nri"),
        "category": "travel",
        "vertical": "visas",
        "diaspora_angle": "Bali is a natural bolt-on to an NRI summer trip home — an easy connection from the Indian metros — but the island's tightened 2026 entry admin can turn a smooth arrival into a long queue unless Indian passport holders prepare in advance.",
        "tags": ["travel", "bali", "visa", "indonesia", "nri", "southeast asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Trip.com", "url": "https://sg.trip.com/"},
            {"name": "Wise", "url": "https://wise.com/"},
            {"name": "VisaForTrip", "url": "https://visafortrip.com/"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Kuta_Bali_Indonesia_Pura-Luhur-Uluwatu-03.jpg/1280px-Kuta_Bali_Indonesia_Pura-Luhur-Uluwatu-03.jpg",
        "image_caption": "The Pura Luhur Uluwatu temple on Bali's cliffs, one of the island's most visited sites.",
        "image_attribution": "Wikimedia Commons",
        "body": body_bali
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
