#!/usr/bin/env python3
"""Travel article writer for The Videshi — July 3, 2026 run."""

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


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: IndiGo Lite Fare
# ─────────────────────────────────────────────────────────────

indigo_lite_body = """IndiGo, India's largest carrier by market share, has launched a new entry-level fare that strips air travel down to its essentials: a seat and a cabin bag. Called "IndiGo Lite," the ticket went on sale July 1 for travel from July 15 onward, available across every non-stop domestic and international route the airline operates.

The mechanics are straightforward. Passengers booking a Lite fare get an auto-assigned seat at no extra charge and can carry one cabin bag weighing up to 7 kg. Check-in baggage, meal pre-bookings, and seat selection are excluded from the base price but can be purchased separately. Bookings are restricted to IndiGo's own channels — its website, mobile app, and contact centre — which means third-party platforms and travel agents are cut out, at least for now.

## Why airlines are unbundling

The move follows a broader unbundling trend sweeping Indian aviation. Last month, Air India introduced a basic economy fare that drops complimentary meals for price-sensitive flyers. The trigger is familiar to anyone who has watched Indian airline earnings: jet fuel prices have surged since the Iran conflict began, and fuel accounts for roughly 40 percent of an airline's operating costs. Both IndiGo and Air India have already cut domestic and international capacity for the summer — IndiGo by 7–10 percent, Air India by a steeper 22 percent on domestic routes.

Unbundled fares are the industry's pressure valve. They let carriers advertise lower headline prices while recovering revenue from passengers who still want the extras. European budget carriers like Ryanair and EasyJet pioneered this model years ago; in the US, even full-service carriers like Delta and United now sell basic economy tickets with baggage restrictions. IndiGo is adapting that playbook for a market where 60 percent of domestic seats are already its own.

"This has been designed for customers who travel with less luggage and only want to pay for the services they need," said Alok Singh, IndiGo's Chief Strategy Officer.

## What it means for NRIs

For Indian Americans flying IndiGo's international network — which now spans roughly 50 destinations — the Lite fare could shave meaningful dollars off short hops within India or to regional destinations like Bangkok, Singapore, and Dubai. If you are visiting family in India and taking a quick Bangalore-to-Goa weekend trip, or a Delhi-to-Jaipur day run, you probably don't need 15 kg of check-in luggage.

The catch: IndiGo's long-haul routes, including the Delhi–London Heathrow service launched earlier this year on wet-leased Boeing 787-9s, are technically eligible for the Lite fare. But flying a 9-hour international leg with nothing but 7 kg of cabin baggage is a niche play — more realistic for business travellers on a quick turnaround than for families heading home with suitcases of gifts and groceries.

The bigger picture is competitive pressure. Air India's new basic economy fare and IndiGo Lite are the opening salvos of a fare war fought not on price alone but on how granularly carriers can slice their product. For NRIs comparing options on the key India–US trunk routes — where Air India, United, and Emirates dominate — the lesson is to compare total cost, not just the headline fare, before booking.

IndiGo Lite fares are available now at [indigo.com](https://www.indigo6e.com) for travel beginning July 15."""

indigo_lite_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-launches-cheaper-tickets-passengers-with-cabin-baggage-only-2026-07-01/"},
    {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-launches-cheaper-tickets-for-passengers-with-cabin-baggage-only/article69746532.ece"},
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/indigo-rolls-out-lite-fare-bookings-for-july-15-travel-begin-today"},
])

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: InterContinental Chennai Mahabalipuram Resort
# ─────────────────────────────────────────────────────────────

mahabalipuram_body = """IHG Hotels & Resorts has reopened the InterContinental Chennai Mahabalipuram Resort after a multi-million-dollar gut renovation — and the result is India's most ambitious beachfront luxury property on the Coromandel Coast. Set across 15 acres along the East Coast Road, within striking distance of the UNESCO-listed Shore Temple, the reimagined resort is positioning itself squarely at the destination-wedding and high-end-leisure market that NRIs increasingly dominate.

## What's new

The transformation goes well beyond a fresh coat of paint. The resort's 110 rooms and suites have been completely redesigned with views of the Bay of Bengal, landscaped gardens, and pool areas. The standout is the Grand Presidential Suite, which offers an ocean-facing living space, a jacuzzi, and a steam room. The Presidential Suite comes with a private pool and a dedicated spa room overlooking the sea. The Rathi Suite adds a plunge pool and steam room with garden views.

On the dining front, The Melting Pot offers Indian, Western, and Pan-Asian cuisine across three open kitchens. Tao of Peng serves Hunan and Cantonese fare. And for the sunset-cocktail crowd, there's KoKoMMo Tiki Shack on the beach, Viora Sky Lounge on the rooftop, and The Gatsby Lounge for nightcaps. A new sports pavilion, walking trails, and a meditation garden round out the wellness infrastructure.

The centrepiece for events is the Vaibhava Ballroom — an ocean-facing venue spanning over 12,000 square feet — complemented by the Vaibhava and Beach Lawns, which together can host over 5,000 guests. That last number matters: the destination-wedding market in India is booming, and the combination of beachfront setting, UNESCO heritage next door, and international-chain service standards makes Mahabalipuram a serious contender against Goa and Udaipur.

## The NRI play

For the Tamil diaspora in particular — an estimated 300,000-strong community concentrated in the US, UK, Singapore, and the Gulf — Mahabalipuram has always held cultural weight. The Shore Temple, the Arjuna's Penance bas-relief, and the Five Rathas are landmarks that many grew up hearing about from parents and grandparents. A world-class resort next to these sites means NRIs no longer have to choose between a heritage trip and a comfortable holiday.

"The reopening of InterContinental Chennai Mahabalipuram Resort marks an important milestone for our luxury portfolio in India," said Sudeep Jain, Managing Director for South West Asia at IHG Hotels & Resorts. "This multi-million-dollar transformation reflects our commitment to delivering destination-led, experience-rich stays that combine world-class hospitality with a strong sense of place."

## The bigger picture

The resort's relaunch is part of a wave of international hotel investment pouring into India's leisure corridors. Marriott opened its 10,000th property globally — the JW Marriott Ranthambore Resort & Spa — in Rajasthan last month. Hilton is opening four properties in Bengaluru this summer. The Leela is building a desert resort near Jaisalmer Fort. The common thread: global chains are betting that Indian domestic tourism and the NRI homecoming market can sustain premium rates year-round, not just during wedding season.

For NRIs planning a trip to Chennai or Tamil Nadu, InterContinental Mahabalipuram is now bookable on IHG's loyalty programme, which means points-based stays and status benefits apply. The resort is roughly 90 minutes from Chennai Airport (MAA) via the East Coast Road — close enough for a weekend, far enough to feel like an escape."""

mahabalipuram_sources = json.dumps([
    {"name": "IHG Hotels & Resorts", "url": "https://www.ihgplc.com/en/news-and-media/news-releases/2026/a-new-chapter-by-the-sea-unfolds-at-intercontinental-chennai-mahabalipuram-resort"},
    {"name": "The Hotel Spotter", "url": "https://thehotelspotter.com/intercontinental-chennai-mahabalipuram-resort-reopens/"},
    {"name": "Hospitality News India", "url": "https://www.hospitalitynews.in/intercontinental-chennai-unveils-transformed-resort/"},
])

# ─────────────────────────────────────────────────────────────
# Build article list
# ─────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Launches 'Lite' Fares — and NRIs Flying Within India Should Pay Attention",
        "subheadline": "India's largest airline now sells cabin-bag-only tickets at lower prices on every domestic and international route, part of a broader unbundling trend driven by soaring fuel costs.",
        "slug": make_slug("indigo-lite-fare-cabin-bag-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs taking short domestic trips within India — weekend getaways, family visits, business hops — can save on flights where they don't need check-in luggage, though long-haul routes remain impractical with a 7 kg limit.",
        "tags": ["travel", "airlines", "indigo", "fares", "nri"],
        "urgency": "medium",
        "sources": indigo_lite_sources,
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg/1280px-Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg",
        "image_caption": "An IndiGo Airbus A320 on the runway",
        "image_attribution": "Wikimedia Commons",
        "body": indigo_lite_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "InterContinental Mahabalipuram Reopens After a Multi-Million-Dollar Makeover — and Tamil NRIs Have a New Reason to Visit",
        "subheadline": "The 110-room beachfront resort near Chennai's UNESCO-listed Shore Temple has been completely rebuilt with ocean-facing suites, five restaurants, and event lawns for 5,000 guests.",
        "slug": make_slug("intercontinental-mahabalipuram-reopens-luxury-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the estimated 300,000 Tamil NRIs in the US, UK, Singapore, and the Gulf, a world-class resort next to Mahabalipuram's heritage sites means heritage trips and luxury holidays are no longer mutually exclusive.",
        "tags": ["travel", "hotels", "chennai", "mahabalipuram", "luxury", "nri"],
        "urgency": "low",
        "sources": mahabalipuram_sources,
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Shore_Temple_-Mamallapuram_-Tamil_Nadu_-N-TN-C55.jpg/1280px-Shore_Temple_-Mamallapuram_-Tamil_Nadu_-N-TN-C55.jpg",
        "image_caption": "The Shore Temple at Mahabalipuram, a UNESCO World Heritage Site near the resort",
        "image_attribution": "Wikimedia Commons",
        "body": mahabalipuram_body,
    },
]

# ─────────────────────────────────────────────────────────────
# Insert into Supabase
# ─────────────────────────────────────────────────────────────

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
