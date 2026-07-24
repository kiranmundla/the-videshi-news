#!/usr/bin/env python3
"""Travel writer — 28 June 2026, 7 PM PT run."""

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
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── ARTICLE 1: IndiGo's Africa & Central Asia Push ──
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Planting Flags in Africa and Central Asia — and Budget-Minded NRIs Should Pay Attention",
        "subheadline": "India's largest carrier is adding six new international destinations across three continents by September, with 174 fresh weekly flights that open corridors NRIs have never had on a low-cost ticket.",
        "slug": make_slug("indigo-africa-central-asia-expansion-nairobi-tbilisi-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family in India can now tag on affordable side trips to Nairobi, Baku, or Tbilisi on the same IndiGo booking — routes that previously required a Gulf carrier or a separate itinerary.",
        "tags": ["travel", "airlines", "indigo", "africa", "central-asia", "international-flights"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Airways Magazine", "url": "https://www.airwaysmag.com/legacy-posts/indigo-international-expansion-plans"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/indigo-international-flights/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-start-operations-from-noida-international-airport-in-june-2026/article69540697.ece"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/IndiGo_Airlines.jpg/1280px-IndiGo_Airlines.jpg",
        "image_caption": "An IndiGo Airbus aircraft on the tarmac at an Indian airport",
        "image_attribution": "Wikimedia Commons",
        "body": """India's largest airline by passengers carried is about to become its most geographically adventurous. IndiGo has announced six new international destinations spanning Africa, Southeast Asia, the Caucasus, and Central Asia — the airline's first foray into three of those four regions — with 174 additional weekly flights rolling out between June and September.

## The new map

Starting in late July, IndiGo will fly nonstop from Mumbai to **Nairobi, Kenya** and **Jakarta, Indonesia**, marking the carrier's debut on the African continent and its second gateway in Indonesia after Bali. In August, Delhi picks up direct connections to **Tbilisi, Georgia** (three times per week) and **Baku, Azerbaijan** (four times per week). September adds **Tashkent, Uzbekistan** (four weekly) and **Almaty, Kazakhstan** (three weekly).

Add it up and IndiGo's international destination count jumps from 26 to 32. The airline is also resuming daily Delhi–Hong Kong service, suspended three years ago during the pandemic, which gives it a fresh gateway to southern China and Macau.

## Why NRIs should care

For Indian Americans accustomed to booking Gulf carriers for anything beyond India and Southeast Asia, IndiGo's expansion is a quiet disruption. A round-trip from the US to India on a full-service airline already runs $1,200–$1,800 in economy. Adding a side trip to Nairobi or Baku from Delhi on IndiGo could cost a fraction of what a separate itinerary on Emirates or Turkish Airlines would.

The Caucasus and Central Asian routes are particularly intriguing. Georgia has become a visa-free destination for Indian passport holders (14-day stay), and Tbilisi's old-town charm and wine country have turned it into a word-of-mouth hit among younger Indian travellers. Azerbaijan requires a simple e-visa. Tashkent and Almaty tap into the Silk Road tourism boom — historic madrasas, mountain treks, and food scenes that South Asian palates take to instantly.

For the roughly 200,000 Indian Americans with roots in East Africa — many of them Gujarati families with generational ties to Kenya, Uganda, and Tanzania — a direct Mumbai–Nairobi flight on a familiar Indian carrier removes the Gulf-stopover friction that has defined the corridor for decades.

## The bigger play

CEO Pieter Elbers, who joined IndiGo in 2022 after leading KLM, has been methodical about pushing the airline beyond its low-cost domestic roots. The strategy has two prongs: direct new routes and a deepening codeshare with Turkish Airlines that already connects IndiGo passengers to 33 European cities via Istanbul. A North American codeshare extension is pending regulatory approval — meaning an IndiGo booking from Delhi could eventually ticket through to JFK or Chicago on a Turkish metal leg.

IndiGo has also deployed the Airbus A321XLR on its Delhi–Istanbul route since April, cutting nearly two hours from the journey and eliminating the previous one-stop routing. The narrowbody workhorse lets IndiGo serve routes up to eight hours without the capital burden of widebody fleets — though the airline has already wet-leased Boeing 787 Dreamliners from Norse Atlantic Airways for its London, Manchester, and Amsterdam services.

## What to watch

Fares on the new routes have not been announced, and schedules remain subject to regulatory approvals. If IndiGo prices Nairobi and the Central Asian routes the way it has priced Istanbul — aggressively, with promotional fares well below legacy carriers — the move could reshape how budget-conscious NRIs plan multi-stop trips around an India visit.

For diaspora families used to the Emirates-or-nothing paradigm, IndiGo's expansion is a reminder that India's aviation market is no longer just about getting from Tier-2 towns to Delhi. It is about getting from Delhi to the world — and doing it on a ticket that does not require a second mortgage.""",
    },

    # ── ARTICLE 2: JW Marriott Ranthambore ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Marriott Just Opened Its 10,000th Hotel — and It Is a Tiger Lodge in Rajasthan",
        "subheadline": "The JW Marriott Ranthambore Resort & Spa marks a global milestone for the hospitality giant and signals that India's wildlife-luxury corridor is ready for the diaspora dollar.",
        "slug": make_slug("jw-marriott-ranthambore-10000th-hotel-tiger-safari-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who collect Marriott Bonvoy points on US credit cards, the new Ranthambore resort means they can redeem loyalty rewards on a luxury tiger safari without leaving the Marriott ecosystem.",
        "tags": ["travel", "hotels", "marriott", "ranthambore", "rajasthan", "wildlife", "luxury"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelPulse Canada", "url": "https://www.travelpulse.ca/news/hotels-resorts/marriott-unveils-10000th-property-with-opening-of-jw-marriott-in-india"},
            {"name": "Hospitality Biz India", "url": "https://www.hospitalitybizindia.com/story/marriott-reaches-10000-hotel-milestone-with-opening-of-jw-marriott-ranthambore-resort-spa/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/marriott-international-opens-10000th-property-globally-with-jw-marriott-ranthambore-resort-and-spa/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/080_Bengal_tiger_in_Ranthambore_National_Park_Photo_by_Giles_Laurent.jpg/1280px-080_Bengal_tiger_in_Ranthambore_National_Park_Photo_by_Giles_Laurent.jpg",
        "image_caption": "A Bengal tiger in Ranthambore National Park, Rajasthan",
        "image_attribution": "Wikimedia Commons / Giles Laurent",
        "body": """When Marriott International picked the location for its 10,000th property worldwide, it did not choose Manhattan or Monaco. It chose Sawai Madhopur, a dusty Rajasthani town best known as the gateway to Ranthambore National Park — India's most famous tiger reserve. The choice says something about where the global hospitality industry thinks the next wave of high-spending guests will come from.

## The resort

The JW Marriott Ranthambore Resort & Spa opened earlier this month with 127 accommodations — a mix of guestrooms, suites, and private villas — spread across a landscaped property a short drive from the national park's entrance. The dining programme leans into regional Rajasthani flavours alongside modern Indian cuisine, with botanical-inspired cocktails that nod to the surrounding Aravalli scrubland.

It is the 11th JW Marriott in India, and Marriott's leadership made sure the milestone landed with ceremony. CEO Anthony Capuano, board chairman David Marriott, and Asia-Pacific president Rajeev Menon all flew in for the ribbon-cutting alongside owner Nilesh Gadhiya.

"Marriott was founded 99 years ago as a nine-seat root beer stand, and as of today has grown into a global portfolio of 10,000 properties spanning 146 countries," Capuano said. That the 10,000th happens to sit within earshot of Bengal tigers is, by any measure, a flex.

## Why Ranthambore

Ranthambore is not new to luxury. The park has attracted high-end safari lodges for years — Aman, Oberoi, and Taj all operate properties nearby. But Marriott's entry at this scale signals a shift: the market for Indian wildlife tourism has grown large enough to support a 127-key international-branded resort, not just boutique lodges with 30 tents.

The park itself is one of the best places on earth to see wild Bengal tigers. Spread across 1,334 square kilometres of dry deciduous forest, scrub, and the ruins of a 10th-century fort (itself a UNESCO World Heritage Site), Ranthambore offers open-canopy jeep safaris where sightings are common enough to plan around. The park is home to roughly 80 tigers, along with leopards, sloth bears, marsh crocodiles, and over 300 bird species.

For wildlife photography enthusiasts — a surprisingly large community among Indian American professionals — Ranthambore has long been the aspirational trip. The difference now is that the infrastructure matches the ambition.

## The NRI math

Here is where it gets interesting for diaspora travellers. Marriott Bonvoy is the dominant hotel loyalty programme among Indian Americans, partly because US credit cards like the Chase Sapphire Reserve and Amex Platinum transfer points directly into Bonvoy. A Category 7 redemption at a JW Marriott property costs 50,000–70,000 points per night — roughly the equivalent of one to two months of regular US credit card spending.

That means NRIs can now book a luxury tiger-safari resort using the same points they accumulate at Courtyard by Marriotts in suburban New Jersey. For families planning a winter India trip — Ranthambore's prime safari season runs October to April — the JW Marriott slots neatly into a Rajasthan circuit that could include the Leela Palace Udaipur, the Leela Jaisalmer (opening later this year), and Jaipur's growing roster of heritage stays.

## The pipeline

Marriott is not stopping at Ranthambore. The company has confirmed two more marquee Indian openings: The Ritz-Carlton Mumbai and The St. Regis New Delhi, both expected in 2027. India's luxury hospitality market is expanding at roughly 12–15 per cent annually, driven by domestic demand and an NRI segment that increasingly wants five-star comfort at ancestral destinations rather than Delhi airport hotels and mid-range Jaipur guesthouses.

The broader trend is unmistakable. International hotel brands are no longer treating India as an emerging market to hedge on — they are treating it as a core growth engine. Marriott alone now operates across the country with brands from Fairfield Inn to JW Marriott, and the 10,000th-hotel milestone landing in Rajasthan rather than Dubai or Bangkok is the clearest signal yet of where the company sees its next decade of returns.

For NRIs planning a wildlife trip to India, the arrival of JW Marriott at Ranthambore means one less reason to default to the familiar beach-resort circuit of Goa and Kerala. The tigers, it turns out, are now a loyalty-point redemption away.""",
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   Slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
