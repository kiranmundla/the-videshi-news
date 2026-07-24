#!/usr/bin/env python3
"""Travel writer — 2026-06-11 02:00 UTC run. Two articles."""

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

# ─────────────────────────────────────────────
# ARTICLE 1: IndiGo route retreat
# ─────────────────────────────────────────────

article1_body = """India's largest airline is pulling back from eight international markets this summer — and the ripple effects will hit NRI travel plans from London to Saigon.

IndiGo confirmed in early June that flights to six Asian destinations — Hong Kong, Shanghai, Krabi, Langkawi, Ho Chi Minh City, and Siem Reap — will be suspended from July 1 through September 30, with Siem Reap services ceasing two days later on July 3. The airline simultaneously announced the permanent discontinuation of its Manchester routes from Delhi and Mumbai, effective August 31, barely a year after those services launched as IndiGo's first foray into Europe. On top of the full suspensions, frequencies on routes to Singapore, Phuket, Bangkok, Penang, and Réunion Island from multiple Indian cities are being cut.

## The Cost Squeeze

The proximate cause is money. Aviation turbine fuel prices have surged through 2026, driven partly by airspace restrictions stemming from the Iran conflict, which force longer routing on westbound flights. IndiGo cited an "incredibly challenging cost environment" in its announcement, pointing to rising fuel costs, rupee depreciation against the dollar, and ballooning expenses on aircraft leases and maintenance — all denominated in foreign currency.

The Manchester route was a particular casualty. IndiGo had wet-leased a Boeing 787-9 Dreamliner from Norse Atlantic Airways to serve the route, offering one-way fares from £290 — substantially cheaper than Air India or Virgin Atlantic from London. But longer flight paths around restricted Iranian airspace erased the economics. The aircraft is being returned to Norse Atlantic, which plans to redeploy it on Europe-Thailand services this winter.

"The response and support for these services have reinforced our belief in the opportunity for IndiGo's long-haul ambitions," said Abhijit Dasgupta, IndiGo's Senior VP of Network Planning. "We are convinced that this discontinuation is temporary."

## What It Means for NRIs

For the estimated 1.8 million people of Indian origin in the UK, the Manchester axing removes the only budget nonstop option between northern England and India. NRIs in Manchester, Leeds, and Birmingham who had shifted away from pricier London connections will now need to reroute through Heathrow — or pay premium fares on Air India and Virgin Atlantic from Gatwick.

The Asian suspensions matter less for US-based NRIs flying home, but they complicate summer vacation plans for the India-resident leg. Families visiting relatives in India who planned side trips to Southeast Asia — Vietnam's beaches, Cambodia's temples, Hong Kong's shopping districts — will find fewer direct options from Indian cities. Alternative routing through Singapore, Bangkok, or Kuala Lumpur hubs remains available, but at higher cost and longer transit times.

## The Contradiction

The retreat is paradoxical. IndiGo currently operates more than 2,700 daily flights across 137 destinations and has flagged plans to hit 3,000 daily departures by FY30. The airline is simultaneously preparing to introduce a dedicated business-class cabin on its incoming Airbus A350-900 widebody fleet, expected in 2027, with Europe as the primary deployment theater. It plans to expand to over 50 international destinations in FY26, with London, Copenhagen, and Athens among the targets.

In other words, IndiGo is retreating from eight markets in order to advance on a dozen others. The suspensions are a tactical reallocation, not a strategic withdrawal — the airline will continue to operate more than 1,800 international flights weekly even during the cut period. Bookings on all six suspended Asian routes are expected to reopen from October 1.

For NRIs, the practical takeaway is straightforward: if you are flying to or through any of the affected destinations between July and September, rebook now. IndiGo is not the only game in town — Air India's new hub-and-spoke Easy Connect model, which just launched from Varanasi with connections to 17 international cities through Delhi, offers an expanding alternative. But budget fares on these routes are gone until at least October, and possibly longer if fuel costs do not ease."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Just Axed Eight International Routes in One Week — and NRI Summer Plans Are Collateral Damage",
    "subheadline": "India's largest airline is suspending six Asian destinations and killing its only UK budget route, blaming fuel costs and the Iran conflict. Here's what it means for diaspora travel this summer.",
    "slug": make_slug("indigo-suspends-routes-manchester-asia-nri-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "UK NRIs lose the only budget nonstop between northern England and India. US-based NRIs visiting family face fewer cheap side-trip options in Southeast Asia. The retreat reshapes summer travel planning for diaspora families across multiple corridors.",
    "tags": ["travel", "airlines", "indigo", "manchester", "hong-kong", "southeast-asia", "flight-routes"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/hong-kong-joins-thailand-malaysia-vietnam-cambodia-and-china-as-indigo-suspends-multiple-international-routes/"},
        {"name": "The Sun UK", "url": "https://www.thesun.co.uk/travel/34780001/budget-airline-flights-axed-uk-year-after-launch/"},
        {"name": "Business Standard (via LinkedIn)", "url": "https://www.linkedin.com/posts/nakulghai_indigo-suspends-flights-to-six-international-activity-ugcPost-7336300000000000000"},
        {"name": "Curly Tales", "url": "https://www.curlytales.com/after-domestic-flight-cuts-indigo-suspends-services-to-hong-kong-shanghai-more-till-sept/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/IndiGo_VT-IJB_A320neo_Mumbai_Apr22_R16_05934.jpg/1280px-IndiGo_VT-IJB_A320neo_Mumbai_Apr22_R16_05934.jpg",
    "image_caption": "An IndiGo Airbus A320neo at Mumbai airport",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: Hotel boom in India
# ─────────────────────────────────────────────

article2_body = """Every major global hotel chain is racing to plant flags across India — and the rooms they are building tell you exactly who they expect to fill them.

In the past month alone, IHG Hotels & Resorts signed a deal with the airports division of the Adani Group to build five hotels at key Indian aviation hubs, including the debut of its ultra-luxury Kimpton brand in the country. Accor announced plans to bring its eco-luxury Mantis label to a tiger reserve in Karnataka. Marriott International and CG Hospitality Global signed a multi-property agreement that includes a 150-room JW Marriott Hotel in Siliguri — the Himalayan gateway city near Bagdogra Airport — plus a Ritz-Carlton in Kathmandu and a Fairfield by Marriott in Bharatpur, Nepal. Hilton and Wyndham signed for properties in India's fast-growing Tier 2 and Tier 3 cities as recently as April.

And on the domestic front, the Ravi Surya Group just opened the Ananta Spa & Resort in Jaipur — a 351-room behemoth spread across 40 acres near the Aravali hills, designed explicitly for the Indian destination wedding market. It features a 19,000-square-foot ballroom, a 70,000-square-foot ceremonial lawn, 12 event venues, and presidential suites running to 3,600 square feet. Meanwhile, Thailand's Dusit International signed for a Dusit Princess property in Rishikesh, betting on India's booming wellness and spiritual tourism segment.

## Follow the Money

The scale of investment is striking. A Hindu Business Line report this week noted that the hotel building spree is happening against a backdrop of weakening consumer confidence — a Reserve Bank of India survey released June 5 showed that household spending sentiment "significantly weakened" in May. Yet the chains are not blinking.

The reason is data. A Kantar survey of 1,700 Indians published last week found that 60% plan a domestic holiday in the next 12 months, and 52% intend to travel internationally — even as they cut back on other spending. India's travel sector, in short, is the one category where consumers refuse to economize. EaseMyTrip, one of India's largest travel platforms, is reporting double-digit growth in domestic leisure bookings, with religious and spiritual journeys emerging as the fastest-growing segment.

## Why NRIs Should Care

If you haven't been to India in two years, the hotel landscape will be unrecognizable when you land. The five IHG-Adani airport hotels mean that transit accommodation at major Indian airports — historically a pain point for NRIs on red-eye connections — is about to get a significant upgrade. The Kimpton debut, in particular, signals that India's airport hospitality is being benchmarked against international standards for the first time.

The JW Marriott in Siliguri is equally significant. Siliguri is the staging point for trips to Darjeeling, Sikkim, and Northeast India — destinations that diaspora families have long avoided because of accommodation gaps. A 150-room JW Marriott with spa facilities and multiple dining venues, just 10 kilometers from Bagdogra Airport, changes the calculus. It becomes possible to fly into Bagdogra, recover in genuine luxury, and then head into the hills refreshed rather than exhausted.

For the NRI wedding circuit, the Ananta Jaipur is purpose-built. Rajasthan already hosts a disproportionate share of Indian diaspora weddings — the palace-hotel aesthetic, the winter climate, and the proximity to Delhi all make it the default choice. But inventory has been a constraint, particularly for large families flying in from multiple countries. A 351-room property with five accommodation categories and a dedicated wedding infrastructure removes that bottleneck.

## The Bigger Picture

What India is experiencing is a hospitality infrastructure boom that mirrors what Dubai and Bali went through a decade ago. The difference is scale: India's domestic tourism market is projected to reach $56 billion by 2030, fueled by a middle class that is larger than the entire population of Western Europe. The global chains understand that the Indian traveler — domestic or diaspora — is the growth engine of the next decade.

For NRIs planning trips home, the practical implication is simple: the India you remember staying in is being torn down and rebuilt. The new rooms are nicer, the airports are better, and the chains competing for your rupee are the same ones you book in Manhattan and Mayfair. Plan accordingly."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Marriott, IHG, and Hilton Are Racing to Build Hotels Across India — and NRIs Are the Prize",
    "subheadline": "From Adani airport hotels and Kimpton's India debut to a 351-room Rajasthan mega-resort built for NRI weddings, global chains are pouring billions into Indian hospitality. Here's what's opening.",
    "slug": make_slug("hotel-chains-india-boom-kimpton-adani-nri-weddings"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "IHG-Adani airport hotels improve NRI transit experience. JW Marriott Siliguri opens the Darjeeling/Sikkim corridor for diaspora families. Ananta Jaipur addresses the chronic room-shortage problem for NRI destination weddings in Rajasthan.",
    "tags": ["travel", "hotels", "marriott", "ihg", "adani", "kimpton", "india-tourism", "weddings"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/hotel-giants-bet-indias-local-travel-boom-can-defy-slowdown/article69667000.ece"},
        {"name": "Restaurant India", "url": "https://www.restaurantindia.in/news/ananta-spa-resort-jaipur-launches-with-351-rooms-across-40-acres.n21889"},
        {"name": "Hotelier India", "url": "https://www.hotelierindia.com/business/dusit-expands-its-india-footprint-with-a-new-project-near-rishikesh"},
        {"name": "Tripura Star News / Marriott", "url": "https://tripurastarnews.com/marriott-international-and-cg-hospitality-global-sign-multi-unit-agreement/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Rambagh_Palace_view_from_garden%2C_July_2016.jpg/1280px-Rambagh_Palace_view_from_garden%2C_July_2016.jpg",
    "image_caption": "The Rambagh Palace hotel in Jaipur, one of Rajasthan's iconic luxury properties",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
