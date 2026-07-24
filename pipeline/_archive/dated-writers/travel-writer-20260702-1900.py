#!/usr/bin/env python3
"""Travel writer — 2 July 2026, 7 PM PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-20260702"


# ─────────────────────────────────────────────────
# ARTICLE 1: Air India Delhi-Melbourne First Class
# ─────────────────────────────────────────────────

article1_body = """Air India's daily Delhi–Melbourne service switched to a Boeing 777-300ER on 1 July, replacing the Boeing 787-8 Dreamliner that had served the route for years. The headline change: eight enclosed First Class suites are now available on a corridor that never had a First cabin before.

## What Changed on 1 July

The upgraded 777-300ER carries 8 First Class suites, 40 fully flat Business Class seats and 280 Economy seats — a net increase in both premium capacity and total seats compared to the outgoing 787-8, which offered only 28 Business and 241 Economy. The First suites, inherited from former Etihad Airways Diamond First cabins, feature sliding privacy doors, fully flat beds stretching roughly two metres, large personal screens and direct aisle access for every passenger.

Business Class moves to a 1-2-1 lie-flat layout with direct aisle access, a clear step up from the 2-2-2 configuration on some of Air India's older widebodies. Economy gets a refreshed cabin and, for the first time on this route, onboard Wi-Fi.

Dining has been overhauled too. Menus now blend Indian staples with international options, and First passengers receive a personalised service that includes premium wines and spirits — a deliberate play for the high-yield corporate and affluent leisure traffic that Gulf carriers have dominated on the India–Australia corridor.

Air India plans to increase the Delhi–Melbourne service from four weekly flights to daily operations from September 2026, adding nearly 4,000 seats a month between the two cities.

## The Bigger Picture: Eight Routes, One Summer

Melbourne is not an isolated upgrade. Air India outlined plans in February to deploy new or refreshed widebody cabins across eight international routes between July and August 2026:

- **Mumbai–London Heathrow** (from 1 July): switched from 777-300ER to the airline's brand-new Boeing 787-9 with factory-installed interiors, introducing Premium Economy on the route for the first time.
- **Bengaluru–London Heathrow** (from 1 August): retrofitted 787-8 with new cabins, adding Premium Economy.
- **Delhi–Toronto** (from 1 August): new 787-9 on seven of ten weekly flights, introducing Premium Economy.
- **Delhi–Birmingham, Amritsar–Birmingham, Ahmedabad–London Gatwick, Amritsar–London Gatwick** (all from 1 August): 777-300ER deployment, introducing First Class on all four routes.

When the August wave is complete, more than half of Air India's North America flights will operate with new or upgraded cabin interiors, and every single Air India flight to and from London Heathrow will feature redesigned cabins. That is a transformation no Indian airline has attempted at this scale or speed.

## Why This Matters to NRIs

Australia is home to more than 900,000 people of Indian origin, with Melbourne's Indian community — concentrated in suburbs like Tarneit, Truganina, Point Cook and Craigieburn — the fastest-growing in the country. The Delhi–Melbourne route is effectively a lifeline for visits home, weddings, festivals and business.

Until now, NRIs flying this corridor had to choose between Gulf carriers with premium cabins and lengthy layovers, or Air India's direct service with a comparatively dated product. A nonstop First Class option on a 12-hour sector changes that calculus. The lie-flat suites and Wi-Fi alone could pull corporate travellers who defaulted to Emirates or Singapore Airlines.

For NRIs in the UK and North America, the August upgrades are equally significant. First Class on all four UK routes — Delhi, Amritsar, Ahmedabad and Birmingham — means the diaspora corridors from Punjab and Gujarat finally get a premium nonstop product that was previously reserved for the Delhi–London trunk.

The Tata Group's multibillion-dollar bet on Air India is starting to show in the cabin. Whether it holds at altitude — in service consistency, catering quality and operational reliability — is the test that matters next."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Just Put First Class Suites on the Delhi–Melbourne Route — and Seven More Upgrades Are Coming",
    "subheadline": "Eight enclosed suites, lie-flat business beds and onboard Wi-Fi landed on the Australia corridor on 1 July. It's the opening move in an eight-route cabin overhaul that will reshape how NRIs fly home this summer.",
    "slug": make_slug("air-india-first-class-delhi-melbourne-summer-cabin-overhaul"),
    "category": "travel",
    "vertical": "airlines",
    "diaspora_angle": "Australia's 900K-strong Indian community gets a premium nonstop option on the Delhi-Melbourne lifeline, while UK and North America NRIs benefit from First Class and Premium Economy on eight upgraded routes by August.",
    "tags": ["travel", "airlines", "air-india", "australia", "first-class", "premium-economy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Air India (via ANI)", "url": "https://entertainment.industriesnews.net/air-india-begins-deploying-b777-300er-with-upgraded-cabin-interiors-on-flights-to-melbourne-from-july-1/"},
        {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/air-india-deploys-boeing-777-300er-with-upgraded-cabins-on-delhi-melbourne-route/"},
        {"name": "CAPA Centre for Aviation", "url": "https://centreforaviation.com/news/air-india-to-adjust-aircraft-on-eight-international-services-from-summer-2026"},
        {"name": "Outlook Traveller", "url": "https://outlooktraveller.com/air-indias-new-boeing-787-9-now-flies-mumbai-london-heathrow/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG/1280px-Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG",
    "image_caption": "An Air India Boeing 777-300ER, the aircraft type now deployed on the Delhi-Melbourne route with First Class suites",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}

# ─────────────────────────────────────────────────
# ARTICLE 2: Hilton's India Expansion
# ─────────────────────────────────────────────────

article2_body = """Hilton opened four hotels in Bengaluru this week and launched its mid-market Spark brand in Asia Pacific for the first time — through India. The moves land as international hotel groups rush to plant flags across a country where branded hotel rooms still account for a fraction of total supply, and where a growing middle class and returning diaspora are raising expectations for consistent, reliable stays.

## What Opened

The centrepiece is Hilton Garden Inn Bengaluru Embassy Tech Village, a 211-room property on Outer Ring Road developed with Embassy Group. It sits inside one of the city's densest tech corridors, surrounded by Embassy Tech Village, EcoWorld and Helios Tech Park — the kind of address where an NRI visiting their employer's India office will spend three nights running between meetings and a poolside dinner.

The hotel features flexible meeting spaces, a 24-hour fitness centre, a temperature-controlled pool and two restaurants: Merigo for all-day dining and Desi Quotient, which focuses on regional Indian cuisine. With this opening, Hilton now operates 13 properties in Bengaluru alone — its largest cluster anywhere in India.

In the same week, Spark by Hilton made its Asia-Pacific debut with two properties: an 82-key hotel in Bengaluru's Marathahalli area on Outer Ring Road and a 64-key resort in Calangute, Goa. The brand, launched globally in 2023 with more than 240 hotels already open in the US, UK and Canada, is designed as a stripped-back, value-driven proposition — complimentary breakfast, multi-functional communal spaces, a 24-hour retail market, and rooms that prioritise clean design over luxury frills.

Hilton's partnership with Olive Hospitality targets 150 Spark by Hilton hotels across India, with the first 10 signed for cities including Jaipur, Nashik, Mathura, Pune, Rajkot and Hyderabad. The pipeline is aimed squarely at tier-two and tier-three cities where infrastructure investment is accelerating and branded accommodation remains scarce.

Also opening this month: Slohh by Roach Bengaluru, Curio Collection by Hilton — the company's first lifestyle hotel in India, inspired by Malnad coffee estates. In August, The Den Bengaluru in Whitefield joins as an LXR Hotels & Resorts property near ITPB and Brigade Tech Park. Hilton Lucknow Gomti Nagar follows in September with 140 rooms and 17,000 square feet of event space.

## India's Hotel Boom, in Numbers

Hilton is not alone. Marriott celebrated 75 signings and 50 openings for its Series by Marriott brand in India — all in under six months. Indian Hotels Company (IHCL) pushed its Ginger brand to 15 hotels in Maharashtra alone. IHG signed a Crowne Plaza Resort in Pushkar, Rajasthan. Dusit International opened its first Indian property in Shimla.

The pattern is consistent: global chains are expanding beyond Mumbai, Delhi and Bengaluru into cities that international travellers — and NRIs — are increasingly visiting. Pushkar, Lucknow, Gadchiroli, Siwan and Agra are not afterthoughts; they reflect genuine demand in pilgrimage circuits, heritage corridors and emerging commercial hubs.

## Why NRIs Should Pay Attention

For the Indian diaspora, the branded-hotel deficit has long been a friction point. Visiting parents in a tier-two city often meant choosing between an unbranded lodge and an overpriced business hotel 90 minutes away. Spark by Hilton's pitch — clean, cheap, Hilton Honors points, breakfast included, in cities like Mathura and Nashik — directly addresses that gap.

The Bengaluru cluster matters too. The city draws more NRI business travellers than any Indian city except Mumbai, and most end up in the Outer Ring Road tech corridor. Having 13 Hilton properties to choose from, across price points from Spark to LXR, means Honors members can now match their stay to their trip — budget for a quick client visit, luxury for a family wedding weekend.

Hilton Honors points earned on US stays transfer directly. A few nights at a Hilton Garden Inn in the Bay Area can fund a Spark stay in Goa. For a diaspora that splits its time and spending between two countries, that portability is worth more than any single amenity."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Hilton Just Opened Four Hotels in Bengaluru and Launched Its Budget Brand in India — All in One Week",
    "subheadline": "Spark by Hilton enters Asia Pacific through India with a 150-hotel pipeline, while Bengaluru becomes Hilton's biggest Indian cluster at 13 properties. For NRIs splitting time between two countries, the loyalty-point portability may matter most.",
    "slug": make_slug("hilton-bengaluru-spark-india-expansion-nri-hotels"),
    "category": "travel",
    "vertical": "hotels",
    "diaspora_angle": "NRIs visiting tier-two Indian cities finally get branded, loyalty-point-earning hotel options as Hilton's Spark brand targets 150 properties in cities like Mathura, Nashik and Rajkot — and Honors points earned in the US transfer directly.",
    "tags": ["travel", "hotels", "hilton", "bengaluru", "hospitality", "india-tourism"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://outlooktraveller.com/hilton-expands-india-portfolio-launches-spark-by-hilton-in-asia-pacific/"},
        {"name": "The Hindu BusinessLine", "url": "https://thehindubusinessline.com/news/embassy-office-parks-reit-and-hilton-launch-hilton-garden-inn-in-bengaluru/"},
        {"name": "Indian Retailer / FranchiseTV", "url": "https://indianretailer.com/franchise-tv/hospitality-franchise-news-hilton-grows-bengaluru-hotel-network"},
        {"name": "Hilton Stories", "url": "https://stories.hilton.com/releases/hilton-olive-hospitality-spark-by-hilton-india"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Bengaluru_Skyline_from_Tata_Promont.jpg/1280px-Bengaluru_Skyline_from_Tata_Promont.jpg",
    "image_caption": "Bengaluru's skyline, where Hilton now operates 13 hotels across its tech corridors",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}

# ─────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
