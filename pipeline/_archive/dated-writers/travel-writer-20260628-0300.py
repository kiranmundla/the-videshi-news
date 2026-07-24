#!/usr/bin/env python3
"""Travel writer — 2026-06-28 03:00 PDT run. Two articles."""

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
    return slug[:70].rstrip('-') + "-20260628"


# ────────────────────────────────────────────────
# ARTICLE 1: Etihad Business Class Sale
# ────────────────────────────────────────────────

etihad_body = """Etihad Airways has opened a limited-period business class sale for travellers departing from India, with fares starting at INR 153,800 — roughly $1,830 — to more than 45 destinations across its network. The booking window runs from June 23 to June 29, 2026, covering travel between July 1 and October 31.

The sale routes passengers through Abu Dhabi, Etihad's home base, and covers destinations across Europe, North America, the Middle East, Africa, and Central Asia. Featured cities include Paris, Zurich, Munich, Dublin, Kraków, and Charlotte. For the diaspora, Charlotte stands out: it is Etihad's newest US gateway, and the only one south of Washington, D.C., putting the airline's business class within reach of the fast-growing Indian community across the Carolinas and the broader Southeast.

## Why NRIs Should Pay Attention — Even From the US Side

The sale is priced for India-originating tickets, but it matters on both sides of the ocean. Etihad's competitive positioning on the US-India corridor has been quietly aggressive this summer. Economy round-trips from JFK to Delhi are currently listed at $916, Atlanta to Mumbai at $848, Boston to Mumbai at $940, and Chicago to Delhi at $1,069 — all via Abu Dhabi. These are well below the $1,100-to-$1,400 range that Air India nonstops and Delta one-stops have been quoting for peak-season July departures.

The Abu Dhabi routing adds three to five hours compared to a nonstop, but the Gulf carrier's pricing fills a genuine gap. With Air India having suspended its Delhi-Chicago service and cut Delhi-San Francisco from ten weekly flights to seven through August — moves driven by elevated jet fuel costs from the ongoing West Asia conflict — available nonstop seats on the most popular NRI routes have tightened considerably. Etihad's one-stop alternative keeps options open for families trying to book summer or early-fall trips home.

## The Business Class Product

Etihad's long-haul business class has been a consistent award-winner, and the sale's INR 153,800 starting fare undercuts what most carriers charge for the same cabin on India-Europe routes. The experience includes flat-bed seats, priority boarding, lounge access in Abu Dhabi (the airline's flagship First & Business Class Lounge was renovated in 2025), and a dine-on-demand menu with regionally inspired options.

For NRI professionals making the India run for work — consulting engagements, family business, or simply the annual July-August visit — the math is worth running. A business class return from Delhi to Zurich via Abu Dhabi at INR 153,800 is roughly $1,830, a fraction of the ₹3-4 lakh that Lufthansa and Air India typically quote for the same cabin in peak season.

## The Catch — and the Opportunity

The booking window closes on June 29, which means procrastinators have hours, not days. Travel must occur between July 1 and October 31, which conveniently spans the shoulder season when many NRIs plan India visits — after the US school year ends but before the Diwali rush drives fares back up.

The broader signal is harder to ignore. Gulf carriers are making a concerted play for Indian premium traffic. Emirates and Qatar Airways have been running similar tactical sales in recent months, and Etihad's move is the latest in a pattern: use competitive business class pricing to pull traffic through Abu Dhabi at a time when direct India-US and India-Europe capacity is constrained by airspace closures and fuel costs.

For NRIs weighing a summer or early-fall trip, the combination of Etihad's economy fares from the US and its business class sale from India creates a genuinely attractive two-way corridor. The routing is longer, but the wallet is lighter — and in a season where nonstop options are shrinking, that trade-off looks better by the week."""


# ────────────────────────────────────────────────
# ARTICLE 2: SWISS Bengaluru-Zurich nonstop
# ────────────────────────────────────────────────

swiss_body = """Swiss International Air Lines will launch its first-ever nonstop service between Bengaluru and Zurich on October 28, 2026, operating five times a week on a wide-body aircraft configured with First, Business, and Economy cabins. Bengaluru becomes SWISS's third Indian destination after Delhi and Mumbai — and the first in southern India.

The route will operate as LX 141 departing Bengaluru at 04:50 and arriving in Zurich at 10:50 the same day, with the return LX 140 leaving Zurich at 13:20 and landing in Bengaluru at 02:55 the next morning. Flights run on Mondays, Wednesdays, Fridays, Saturdays, and Sundays — a schedule that covers both the weekend and mid-week business travel windows.

## The Diaspora Math

India's Silicon Valley sends more tech professionals to Europe than any other Indian city. Bengaluru is home to the India headquarters of SAP, Bosch, ABB, and Novartis — all Swiss or Swiss-adjacent companies — and the flow of engineers, product managers, and consultants between BLR and ZRH has historically been served by one-stop routings through Delhi, Mumbai, or the Gulf.

A direct flight changes the equation. The roughly nine-hour nonstop eliminates a three-to-five-hour layover and cuts total travel time to under ten hours door-to-airport. For the estimated 80,000 Indians living in Switzerland and thousands more in the German-speaking tech corridors of Munich and Frankfurt, Bengaluru is often the final domestic connection from parents' homes in Hyderabad, Chennai, or Kochi. SWISS's through-ticketing with Bengaluru's domestic network of 78 destinations means a single booking can now cover Coimbatore to Zurich.

## The Lufthansa Group Strategy

The launch is not an isolated move. It arrives weeks after Germany abolished transit visa requirements for Indian passport holders at German airports, effective June 3, 2026. That policy change made connections through Frankfurt and Munich frictionless for the first time — no more queuing for a transit visa before boarding a connecting flight to Paris, Amsterdam, or Stockholm.

Bengaluru now becomes the third Lufthansa Group gateway from the city, joining Lufthansa's own Frankfurt and Munich services. The group plans to operate over 70 weekly flights between India and Europe in its Winter 2026 schedule, and the SWISS addition plugs the one gap that mattered most to southern India's tech workforce: a premium direct link to the heart of continental Europe.

Kevin Markette, Lufthansa Group Senior Director for Regional Sales in South Asia, called the launch a response to "surging corporate and leisure demand, connecting India's Silicon Valley with a premier global financial capital."

## What to Expect on Board

SWISS is deploying its full premium product, including its recently upgraded "SWISS Senses" cabin on select long-haul aircraft. Business class features lie-flat seats with direct aisle access, noise-cancelling headphones, and a menu sourced from Swiss culinary partners. First class — a rarity on India routes outside Air India and Lufthansa — is available on every flight, with eight private suites.

For economy passengers, the SWISS long-haul experience includes complimentary meals, a personal entertainment screen, and the option to pre-select seats. Luggage allowances follow Lufthansa Group standards: 23 kg checked bag in economy, 2×32 kg in business, with Star Alliance Gold members getting an extra piece.

## Booking and Fares

Tickets are already on sale at swiss.com and through travel agents. Early indications show round-trip economy fares from Bengaluru to Zurich starting around INR 55,000 to INR 65,000 for October-November travel, competitive with Lufthansa's one-stop offerings through Frankfurt. Business class fares start at approximately INR 2,50,000 — a premium, but one that buys a direct flight and the time savings that come with it.

For the Kannadiga and broader South Indian diaspora in Europe, SWISS's Bengaluru bet is a recognition of a corridor that carriers have underserved for years. The October launch means the winter holiday season — when NRIs flood Indian airports — will have a premium nonstop option that did not exist before."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Etihad's Business Class Sale Starts at ₹1.54 Lakh — and the Abu Dhabi Routing Is Quietly Winning the India-US Fare War",
        "subheadline": "A limited-window sale from India and aggressive economy fares from the US make Etihad's one-stop corridor hard to ignore as Air India cuts nonstop capacity on key diaspora routes.",
        "slug": make_slug("etihad-business-class-sale-india-abu-dhabi-us-fares-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With Air India suspending Delhi-Chicago and cutting Delhi-SFO to seven weekly flights, Etihad's Abu Dhabi routing offers NRIs an affordable alternative on the US-India corridor — economy from $848 and business class from ₹1.54 lakh.",
        "tags": ["travel", "airlines", "etihad", "fares", "business-class", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/travel-news/etihad-airways-opens-business-class-sale-for-travellers-from-india"},
            {"name": "TravelMedia.in", "url": "https://www.travelmedia.in/fly-beyond-borders-in-style-etihad-airways-launches-exclusive-business-class-sale-for-indian-flyers/"},
            {"name": "Etihad Airways", "url": "https://www.etihad.com/en-in/flights-from/india"},
            {"name": "Air India", "url": "https://www.airindia.com/en/air-india-rationalises-international-route-network"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/A6-BLL_-_Boeing_787-9_Dreamliner_-_Etihad_Airways_-_MSN_39656_-_VGHS.jpg/1280px-A6-BLL_-_Boeing_787-9_Dreamliner_-_Etihad_Airways_-_MSN_39656_-_VGHS.jpg",
        "image_caption": "An Etihad Airways Boeing 787-9 Dreamliner, the aircraft type that serves many of the airline's India routes",
        "image_attribution": "Wikimedia Commons",
        "body": etihad_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Will Fly Bengaluru to Zurich Nonstop Starting October — the First Direct Link Between South India and Switzerland",
        "subheadline": "Five weekly flights with First, Business, and Economy cabins plug a gap the tech diaspora has waited years for, weeks after Germany dropped transit visa requirements for Indians.",
        "slug": make_slug("swiss-bengaluru-zurich-nonstop-south-india-europe-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 80,000-strong Indian community in Switzerland and tech professionals commuting between Bengaluru and Europe, SWISS's direct flight eliminates the Gulf or Delhi layover that added hours to every trip home.",
        "tags": ["travel", "airlines", "swiss", "bengaluru", "zurich", "europe", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SWISS Newsroom", "url": "https://newsroom.swiss.com/en/swiss-to-offer-its-first-ever-service-to-bengaluru-india"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/swiss-expands-india-network-with-new-nonstop-bengaluru-zurich-service/"},
            {"name": "TravelWires", "url": "https://www.travelwires.com/swiss-launches-nonstop-flights-between-zurich-and-bengaluru/"},
            {"name": "Hospitality News India", "url": "https://hospitalitynews.in/swiss-adds-first-bengaluru-service-from-zurich/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg/1280px-HB-JNB_Boeing_777-300_Swissair_LHR_4.11.20.jpg",
        "image_caption": "A SWISS Boeing 777-300 at London Heathrow; the airline will deploy a wide-body aircraft on its new Bengaluru-Zurich route",
        "image_attribution": "Wikimedia Commons",
        "body": swiss_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
