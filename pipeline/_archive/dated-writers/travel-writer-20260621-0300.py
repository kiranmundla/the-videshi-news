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

JAPAN_BODY = """Japan has quietly become the diaspora's favourite mid-haul escape — close enough to fold into an India trip, cheap enough on a weak yen to feel like a steal, and visually unlike anywhere an NRI family from New Jersey or the Bay Area normally vacations. Starting **July 1, 2026**, two of the numbers behind that trip are going up at once.

## What changed

Japan is raising the fee for a single-entry tourist visa from ¥3,000 to ¥15,000 — a fivefold jump and the first revision since 1978. A multiple-entry visa climbs from ¥6,000 to ¥30,000. Separately, the country's International Tourist Tax — the "sayonara tax" baked into your departure ticket — rises from ¥1,000 to ¥3,000 from the same month.

There is an important wrinkle for Indian passport holders specifically. The Embassy of Japan in India charges Indian nationals a concessional consular fee — currently 500 INR for a single or multiple visa applied through VFS, far below the standard rate other nationalities pay. How the July overhaul filters down to that special Indian rate is the detail to confirm with VFS before you apply, because the embassy's India fee schedule and the headline yen figure are not the same line item. What is not in doubt is the departure tax: at roughly $20, it now applies to anyone flying out of Japan after July, children under two and pure transit passengers excepted.

## Why this matters to NRIs

Indian travel to Japan has been on a tear. Over 300,000 Indians visited in 2025 — a record, and a roughly 35% jump on the prior year. That surge is exactly why Japan is changing the rules: visa centres in Chennai, Hyderabad, Kochi and Puducherry already moved off walk-in submissions to an appointment system in March to cope with the crowds.

For an Indian American family, the calculus is slightly different from a traveller flying out of Delhi. If you hold a US, UK or Schengen visa, you may qualify for relaxed documentation on a Japan tourist visa — but India is *not* on Japan's visa-free list, and your US green card or H-1B does not change that. Every Indian passport holder still needs a sticker visa before boarding, regardless of where they live. The fee increase lands on top of an application process that already takes 8–10 working days and, post-March, an appointment you must book in advance.

## The math on a weak yen

Here is the counterintuitive part: even with both increases, Japan in 2026 is cheaper for Indian and dollar-earning travellers than it has been in years. The yen remains historically soft against both the rupee and the dollar, which is why Indian agencies are reporting record package bookings for spring and autumn. A $100 visa fee and a $20 departure tax are real, but they are rounding errors against a fare and a week of hotels — and the currency advantage swamps both.

The practical takeaway for a US-based family planning a Tokyo-and-Kyoto leg, perhaps bolted onto a winter India trip: there is no urgency to rush in before July to dodge the fee — the sums are too small to drive the decision. The thing to actually plan around is the appointment system and the 8–10 day processing window. Apply early, build in buffer, and treat the new fees as a line in the budget rather than a reason to change your dates.

## What's next

Discussions about a Japan e-visa for Indians have been "ongoing" for two years without landing; for now, assume a VFS sticker visa and a biometrics appointment. Watch for VFS to publish exactly how the July fee schedule maps to the concessional Indian rate — that notice, not the yen headline, is what will tell an NRI applicant what they will actually pay at the counter."""

ETIHAD_BODY = """For years the conventional wisdom on the diaspora's route home was simple: fly the Gulf carriers in economy, suffer the layover, save the money. The premium cabin was for someone else's expense account. This summer, the math has shifted in a way worth a second look — and Etihad's Abu Dhabi hub, which already funnels a large share of US–India traffic, is at the centre of it.

## The number that changed

Industry fare trackers heading into summer 2026 found something unusual. While international economy fares are up sharply year over year — roughly 6% to 12% depending on route — premium cabins rose far more modestly. Business and first-class cash fares are up only about 7%. In a market where coach prices have spiked, the gap between economy and the front of the plane has narrowed rather than widened. For travellers who have eyed an upgrade for years, this is the rare summer where the premium feels less punishing relative to the back.

Etihad's India routes illustrate it concretely. Business-class fares on Abu Dhabi–Delhi currently range from around $1,000 to over $2,000, and the Mumbai route can dip *under* $1,000 one-way — genuinely close to what a peak-summer economy ticket on a US–India routing costs this year. The carrier deploys its newest A350-1000 on both Delhi and Mumbai, the shortest routes in its network to see that aircraft, which means a strong chance of the latest seat without paying long-haul-flagship prices.

## The miles angle NRIs miss

The bigger value is hiding in Etihad Guest, the airline's loyalty programme — and it works differently from the American programs most NRIs default to. Etihad Guest is **distance-based, not revenue-based**, and award pricing is not dynamic. That combination is gold for a savvy diaspora flyer: on Delhi and Mumbai, business-class award flights run from roughly 29,700 to 78,375 miles one-way, and an economy-to-business upgrade costs as little as 21,711 miles. Those are strikingly low numbers next to the 100,000-plus miles a US program wants for a comparable transatlantic or transpacific business seat.

For an Indian American who collects points on a US credit card, Etihad Guest is a transfer partner of several major American programs — meaning miles parked in a flexible US currency can become a sub-30,000-mile business seat to Mumbai. That is the kind of arbitrage that turns a once-a-year trip home into a front-cabin one.

## Why this matters to NRIs

The diaspora's flying habits are being quietly rerouted. With Air India pulling back on some capacity and the Gulf carriers expanding aggressively into US cities — Etihad has been adding frequencies and new American gateways — Abu Dhabi is absorbing more of the family-visit traffic that once went through other hubs. For the large NRI populations in the tri-state area, Chicago and the West Coast, that means more seats, more competition, and this summer, a premium cabin that is unusually within reach.

## What's next

The fare window is seasonal. Premium pricing tends to firm up as peak summer demand builds, and the cheapest dates this year cluster in mid-to-late August — international fares run roughly 13% lower then than in July. The play for a diaspora traveller eyeing a comfortable trip home: price the Etihad business fare and the Etihad Guest award side by side now, target August dates, and book the one that is cheaper before the gap closes."""

AIRFARE_BODY = """Every NRI who flies home knows the annual ritual: open the booking site in June, see a four-figure fare to Delhi, and wince. Summer 2026 is shaping up to be the most expensive in years — but the data also points to a specific, learnable window where the diaspora can claw a few hundred dollars back. The trick is knowing which month, which day, and which airport to target.

## The bad news first

US airlines collectively lost about $1 billion in the first quarter of 2026, and the squeeze shows up at the ticket counter. International fares are up 6% to 12% year over year. The Iran conflict and the closure of the Strait of Hormuz have pushed jet fuel to four-year highs, and that cost flows straight into long-haul tickets — including the US–India routes the diaspora depends on. Peak pricing runs late June through July, exactly when school is out and families most want to travel.

A scan of current fares shows the damage: round-trips from SFO and JFK to Delhi and Mumbai routinely clear $1,000, with peak summer departures pushing well past $1,500–$2,000 from the West Coast. American Airlines is showing JFK–Delhi from around $1,093 and ORD–Delhi from about $1,260 — and those are the *attractive* fares, mostly for later-summer dates.

## Where the deals actually are

Here is the pattern worth memorising. According to fare-trend data, three levers move the price more than anything else:

**Fly in August, not July.** International fares peak in June and are roughly 13% cheaper in August. The cheapest dates cluster in mid-to-late August — think the 14th, the 26th — as demand starts to taper after the July rush. For families who can flex around the school calendar, shifting a trip even two weeks deeper into August is the single biggest saving available.

**Fly on the right day.** Tuesdays are the cheapest day to fly internationally, followed by Wednesdays; Fridays and Saturdays are the most expensive. On a $1,400 ticket, the day-of-week swing is real money — by some measures Tuesdays run nearly 18% below Sundays.

**Widen the airport net.** Secondary cities and routes where airlines have added capacity consistently undercut the marquee hubs. A flyer willing to position to Dallas, where DFW–Delhi is showing around $1,200, or to drive to an alternate gateway, can beat the headline SFO and JFK fares. American's DFW–Bengaluru is appearing near $1,284 — competitive for a South Indian routing that often runs dearer.

## Why this matters to NRIs

For the Indian American family, the trip home is rarely optional — it is weddings, ageing parents, and the kids' one immersion in India each year. That makes the diaspora a price-taker on exactly the dates that cost the most. Understanding the August-Tuesday-secondary-airport formula is the difference between a $2,000 West Coast fare and something several hundred dollars lighter, multiplied across a family of four.

## What's next

One structural tip applies all summer: book a changeable fare now rather than waiting. Most major US carriers allow fee-free changes on anything above basic economy, and award tickets can be cancelled without forfeiting miles. Lock in a refundable-ish August itinerary today, keep watching, and rebook if the fare drops — the downside is minimal and the upside, in a rising market, is real. The one date to plan firmly around remains Diwali in November, when the booking window tightens far earlier than summer's."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Japan Just Raised Its Visa Fee Fivefold and Hiked the Departure Tax — but the Weak Yen Still Wins for NRIs",
        "subheadline": "From July 1, a Japan tourist visa costs five times more and the departure tax triples. Here's what Indian passport holders actually pay — and why it shouldn't change your plans.",
        "slug": make_slug("japan-visa-fee-fivefold-departure-tax-hike-july-nri-weak-yen"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Japan is the diaspora's fastest-growing mid-haul escape, but Indian passport holders still need a sticker visa regardless of US/UK residency — and the July fee changes plus appointment system mean NRI families must plan further ahead.",
        "tags": ["travel", "visa", "japan", "fees", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Curly Tales — Japan tourist visa fees hiked fivefold", "url": "https://curlytales.com/"},
            {"name": "Wego Travel Blog — Japan raising visa and travel fees 2026", "url": "https://blog.wego.com/"},
            {"name": "Embassy of Japan in India — Visa fees", "url": "https://www.in.emb-japan.go.jp/"},
            {"name": "Travel And Tour World — Japan ends walk-in visa submissions", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Shibuya_and_Mount_Fuji_seen_from_Roppongi_Hills.jpg/1280px-Shibuya_and_Mount_Fuji_seen_from_Roppongi_Hills.jpg",
        "image_caption": "Tokyo's Shibuya district with Mount Fuji in the distance, seen from Roppongi Hills",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": JAPAN_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "This Is the Summer Business Class to India Got Cheap — Etihad's Abu Dhabi Hub Shows Why",
        "subheadline": "Economy fares to India are up double digits, but premium cabins rose only about 7%. On Etihad's Delhi and Mumbai routes — and its distance-based miles program — the front of the plane is unusually within reach.",
        "slug": make_slug("etihad-business-class-india-cheap-summer-abu-dhabi-miles-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With Air India pulling back and Gulf carriers expanding into US cities, more diaspora traffic now flows through Abu Dhabi — and a narrowing economy-to-business fare gap plus Etihad's low distance-based award pricing make a front-cabin trip home rarely this affordable.",
        "tags": ["travel", "airlines", "etihad", "business-class", "miles", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying — Etihad A350 business class costs in 2026", "url": "https://simpleflying.com/"},
            {"name": "TravelPulse — Summer 2026 airfare trends", "url": "https://www.travelpulse.com/"},
            {"name": "The Points Guy — Finding the best summer fare deals", "url": "https://thepointsguy.com/"}
        ]),
        "score_total": 73,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Etihad_Airways_Airbus_A350_A6-XWB_at_Tokyo_Narita_Int%27l_Airport.jpg/1280px-Etihad_Airways_Airbus_A350_A6-XWB_at_Tokyo_Narita_Int%27l_Airport.jpg",
        "image_caption": "An Etihad Airways Airbus A350-1000, the aircraft type the carrier deploys on its Delhi and Mumbai routes",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": ETIHAD_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Summer Fares to India Are the Highest in Years — Here's the August-Tuesday Formula That Beats Them",
        "subheadline": "International fares are up as much as 12% and jet fuel is at a four-year high. But the data points to a specific month, day, and airport strategy that can save an NRI family hundreds on the trip home.",
        "slug": make_slug("us-india-summer-airfare-2026-august-tuesday-secondary-airport-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The trip home is rarely optional for NRI families — weddings, ageing parents, kids' summer in India — which makes the diaspora a price-taker on the most expensive dates; knowing the August/Tuesday/secondary-airport formula is worth several hundred dollars per family.",
        "tags": ["travel", "airfare", "deals", "us-india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Points Guy — Tips to find the best summer deals", "url": "https://thepointsguy.com/"},
            {"name": "TravelPulse — Summer 2026 most expensive in years", "url": "https://www.travelpulse.com/"},
            {"name": "Palm Beach Post — US airlines lost $1 billion in 2026", "url": "https://www.palmbeachpost.com/"},
            {"name": "Travelocity — Cheap flights to India", "url": "https://www.travelocity.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12940608/pexels-photo-12940608.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Travellers check an airport departure board ahead of summer flights",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": AIRFARE_BODY
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  [{art['slug']}] ~{wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
