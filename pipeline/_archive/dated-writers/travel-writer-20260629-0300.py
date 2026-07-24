#!/usr/bin/env python3
"""Travel writer — 2026-06-29 03:00 PDT run. Two articles."""

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

# ── Article 1 ─────────────────────────────────────────────────

art1_body = """\
The peak summer travel season is here, and Air India has just shrunk its map. The Tata-owned carrier announced a sweeping rationalisation of international routes from June through August 2026, driven by record-high jet fuel prices and the airspace restrictions that have dogged the airline since the Iran conflict erupted earlier this year. For the hundreds of thousands of Indian Americans who rely on Air India as their primary carrier to India, the cuts land squarely on the routes that matter most.

## What got cut — and what survived

The headline casualty is Delhi-Chicago: completely suspended through August. For the roughly 250,000 people of Indian origin in the Chicagoland metro — one of the largest NRI concentrations in the Midwest — there is, as of now, no direct Air India option. Delhi-Newark and Mumbai-New York JFK have also been pulled.

San Francisco fares only slightly better. Delhi-SFO has been trimmed from ten weekly flights to seven, a 30 per cent reduction that effectively eliminates the ability to fly any day of the week. Given that the Bay Area is home to one of the densest Indian populations in the United States, the capacity squeeze will be felt acutely during the summer homeward rush.

The Canadian corridors are similarly dented. Delhi-Toronto drops from ten weekly flights to just five through July (it returns to daily in August), and Delhi-Vancouver falls from seven to five.

There is a partial silver lining: Mumbai-Newark has been boosted from three weekly flights to seven, effectively absorbing some of the displaced Delhi-Newark traffic. And Delhi-JFK continues to operate daily — the only US route that emerges unscathed.

## Why it happened

Air India pointed to "continued airspace restrictions over certain regions and record high jet fuel prices" — diplomatic shorthand for the cascading effects of the West Asia conflict. Fuel now accounts for roughly 40 per cent of operating costs, and the closure of Iranian and parts of Iraqi airspace has forced longer, more expensive routing on westbound flights. The airline has been routing some New York-bound services through Rome as a technical fuel stop since early 2026 — a costly workaround that added hours to an already gruelling journey.

The cuts are not limited to Air India. Reuters reported that IndiGo has trimmed 7-10 per cent of its planned domestic flights for June and July, while Air India slashed 22 per cent of its domestic schedule. Together, the two carriers control about 90 per cent of India's domestic air market — meaning NRIs flying within India during their summer trips will also encounter thinner schedules and higher fares.

## A rebound on the horizon?

There is cautious optimism. Campbell Wilson, Air India's CEO, said late last week that the easing of Gulf tensions has opened the door to restoring some of the suspended routes. June, he noted, was the airline's strongest operational month — on-time performance hit 86 per cent overall and a record 90 per cent on domestic services. Air India Express, meanwhile, is pushing ahead with new international routes: it launches the first-ever international flight from Navi Mumbai airport on July 15, to Abu Dhabi, and will add direct Guwahati-Dubai and Guwahati-Abu Dhabi services.

The broader Tata strategy has not changed. Air India still has 34 Airbus A350s on order (including 20 of the longer-range A350-1000), and 60 per cent of all US flights now feature new or upgraded cabins. The route cuts are presented as a temporary holding pattern, not a retreat.

## What NRIs can do right now

For those with bookings on suspended routes, Air India is offering re-accommodation on alternative flights, free date changes, or full refunds. The practical alternatives: fly Delhi-JFK (daily, A350 with new cabins), or Mumbai-Newark (now daily on the 777-300ER). For Chicago, United's nonstop from Newark to Delhi via code-share, or Emirates/Qatar routing through their Gulf hubs, are the most viable workarounds.

Booking early matters more than usual this summer. With fewer seats in the market and fuel surcharges baked into fares, the price gap between advance and last-minute tickets is wider than it has been in years.

Air India has said it will "restore full capacity as soon as conditions permit." For NRIs scanning departure boards from O'Hare, SFO, or Newark this summer, that day cannot come soon enough.
"""

art1_sources = json.dumps([
    {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/newsroom/press-release/Air-India-rationalises-international-route-network-through-August-2026.html"},
    {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airlines-lessors/air-india-suspends-routes-including-delhi-chicago-fuel-costs-bite"},
    {"name": "Skift", "url": "https://skift.com/2026/05/13/air-india-scales-back-international-flights-whats-cancelled-whats-reduced/"},
    {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-june-july-domestic-flights-amid-high-jet-fuel-prices-sources-2026-05-28/"},
    {"name": "Gulf Business", "url": "https://gulfbusiness.com/air-india-announces-route-cuts-through-august-debunks-viral-rumours/"}
])

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Has Suspended Chicago, Newark and Two Other NRI Corridors Through August — Here's What's Left",
    "subheadline": "Record jet fuel costs and West Asia airspace closures forced the airline to cut or thin out flights on nearly every major India-US and India-Canada route. A rebound may be near, but not before summer ends.",
    "slug": make_slug("air-india-summer-route-cuts-chicago-sfo-newark-nri"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "Chicago, San Francisco, Newark and Toronto — four of the five biggest NRI metro corridors — have lost direct Air India capacity this summer, forcing travellers onto costlier alternatives.",
    "tags": ["travel", "airlines", "air-india", "nri", "flights", "route-cuts"],
    "urgency": "high",
    "sources": art1_sources,
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Air_India_A350.png/1280px-Air_India_A350.png",
    "image_caption": "An Air India Airbus A350-900 in the carrier's current livery",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ── Article 2 ─────────────────────────────────────────────────

art2_body = """\
If you are an Indian expatriate in the Gulf scanning airfares for a July trip home, there is a sliver of good news — and a thick caveat. Ticket prices on key UAE-India routes have started to ease after weeks of relentless increases, with Kerala-bound sectors seeing the sharpest correction. But travel industry executives are unanimous: current fares are still 15 to 20 per cent above last summer's levels, and the reprieve could be fleeting.

## Kerala leads the fare correction

The biggest drops have landed on the routes that matter most to the Gulf's Malayali diaspora. Raheesh Babu, chief operating officer of Musafir.com, told Gulf News that one-way fares on some UAE-Kerala sectors had ballooned to Dh3,500-3,600 (roughly ₹80,000-82,000) earlier this month. They have since pulled back to around Dh2,600 (about ₹59,000) — a meaningful Dh1,000 decline, but still eye-watering by pre-conflict standards.

Kannur, the north Kerala airport that is a lifeline for the Malabar diaspora in the Gulf, has also seen some softening. Fares that had touched Dh1,500 have dropped by Dh400-500, according to TP Sudheesh of Deira Travels in Dubai. The catalyst: IndiGo has increased its Calicut and Kochi frequencies, adding seats to a market that had been operating at near-full capacity.

Kochi-bound fares, which had climbed to around INR 25,000 one-way from the Gulf, remain elevated despite the correction. And Sudheesh cautioned that the dip could be short-lived — fares may climb back to the Dh1,300-1,400 range from July 1 as schedules normalise and peak holiday demand kicks in.

## Why the correction, and why now

The easing is not a demand story. The UAE-India corridor remains one of the world's busiest international aviation markets, powered by the roughly 3.5 million Indian nationals in the UAE and the summer tradition of school-holiday family visits. What has changed is supply.

Airlines that had slashed capacity during the West Asia conflict are gradually restoring flights. Zaid Ameen of Go Kite Tours & Travels in Dubai said that during the conflict and its immediate aftermath, only Emirates and flydubai maintained full schedules; Indian carriers — IndiGo, SpiceJet, Air India, and Air India Express — operated reduced services. "Flights have now returned," Ameen said, crediting the capacity restoration and the addition of Salam Air's Muscat routing for easing the squeeze.

An industry source said Air India Express has restored about 80 per cent of its regional capacity, with additional services expected in the coming weeks. The airline also launched new frequencies from regional Indian airports, including expanded Calicut and Kochi services that directly address the Kerala fare pressure.

## The numbers to know before you book

Full-service carrier one-way fares (Emirates, Air India) are generally running Dh1,250-1,500 or higher. Budget airline one-way tickets (IndiGo, Air India Express, SpiceJet) range from Dh850 to Dh1,100, depending on route and date. But deals do surface: Sapna Aidasani, a Dubai-based travel consultant, recently secured Dh550 one-way fares for a family, and spotted Emirates tickets between Dh650 and Dh950 on selected flights.

Safeer Mahmood, general manager of Smart Travels in Dubai, said travellers may occasionally find lower fares before July 8 when cancellations free up seats. "Tracking fares closely would definitely help," he said, adding that travel agents sometimes have pre-blocked seats at lower rates.

## A practical checklist for Gulf NRIs

There are a few things that can shave hundreds of dirhams off a summer ticket. Book midweek departures (Tuesday, Wednesday) when demand is thinnest. Monitor fares daily — cancellation-driven inventory dumps are unpredictable but real. Consider flying into Calicut or Kannur instead of Kochi if your final destination is northern Kerala; the IndiGo capacity additions there have had the most impact on pricing.

Be aware that India's Air Suvidha 2.0 health self-declaration form is now mandatory for all inbound passengers. It can only be filled out within 24 hours of departure — a detail that catches first-time users off guard.

And do not wait for fares to fall further. Every agent Gulf News spoke to said the same thing: this is a window, not a trend. Once school holidays hit full stride and airlines sell through their budget inventory, the next fare move is likely upward, not down.
"""

art2_sources = json.dumps([
    {"name": "Dubai Standard / Gulf News", "url": "https://www.dubaistandard.com/uae-india-flights-airfares-ease-as-more-flights-return-before-the-summer-holiday-rush/"},
    {"name": "Times Now World", "url": "https://www.timesnowworld.com/business/economy/article/airfares-between-the-uae-and-india-decrease-in-anticipation-of-the-july-travel-surge-with-significant-reductions-noted-on-routes-to-kerala/3289847"},
    {"name": "USA Today", "url": "https://usatodaycom.com/uae-india-airfares-drop-ahead-of-july-travel-rush-kerala-routes-see-sharpest-dip-report/"},
    {"name": "Orbit Prime News", "url": "https://orbitprimenews.com/uae-india-airfares-drop-ahead-of-july-travel-rush-kerala-routes-see-sharpest-dip-report/"}
])

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "UAE-India Airfares Are Finally Easing — But Gulf NRIs Have a Narrow Window Before Prices Climb Again",
    "subheadline": "Kerala routes have seen the sharpest correction, with one-way fares from the Gulf dropping nearly Dh1,000 as airlines restore capacity. Agents warn the reprieve may last only until school holidays hit full stride.",
    "slug": make_slug("uae-india-airfares-ease-july-kerala-gulf-nri"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "The 3.5 million Indians in the UAE are the biggest buyers on this corridor — and the fare swings hit Malayali families headed to Kerala hardest, with one-way tickets still double pre-conflict norms.",
    "tags": ["travel", "airlines", "gulf", "nri", "uae", "kerala", "airfares"],
    "urgency": "high",
    "sources": art2_sources,
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg/1280px-Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg",
    "image_caption": "The departures hall at Dubai International Airport Terminal 3, one of the busiest hubs for UAE-India flights",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ── Insert ────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
