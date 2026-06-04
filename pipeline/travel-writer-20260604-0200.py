#!/usr/bin/env python3
"""Videshi Travel Writer — June 4, 2026 batch"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
# ARTICLE 1: ITC Hotels Acquires Zuri Kumarakom
# ─────────────────────────────────────────────

art1_body = """ITC Hotels Limited has signed definitive agreements to acquire The Zuri Kumarakom, Kerala Resort & Spa — a move that gives India's most profitable hotel company its first owned property in a state that draws more NRI visitors per capita than almost any other.

The deal values Zuri Hotels & Resorts Private Limited at an enterprise value of Rs 205 crore on a debt-free, cash-free basis. ITC will take a 100 percent stake, with the transaction expected to close within days.

## The Property

Kumarakom sits on the eastern bank of Vembanad Lake, roughly 70 km from Cochin International Airport — the gateway for the vast majority of Keralite diaspora returning from the Gulf, the UK, and North America. The resort itself spreads across 18 acres and holds 72 keys, including 38 villas and cottages arranged around a five-acre man-made lagoon. There are multiple dining venues, event facilities, and nearly 20,000 square feet of spa and wellness infrastructure.

It is, in other words, the kind of backwater retreat that Keralite NRIs have been booking for family reunions and post-wedding celebrations for years — only now it will carry ITC's standards for food, service, and Ayurvedic wellness programming.

## Why ITC Wants Kerala

ITC Hotels has long been the premium player in business destinations — its marquee properties sit in Delhi, Mumbai, Kolkata, Bengaluru, and Chennai. But its leisure portfolio has been thinner, concentrated in Rajasthan (ITC Rajputana) and a handful of hill and temple destinations. Kerala, India's most established leisure corridor, was a conspicuous gap.

"Kerala's rich cultural heritage and breathtaking landscapes have always resonated with tourists," said Anil Chadha, Managing Director of ITC Hotels. "We aim to elevate the guest experience through our globally recognized culinary excellence and world-class Ayurvedic wellness offerings."

The timing is strategic. ITC Hotels was demerged from the parent ITC Limited in early 2025 and listed separately, putting pressure on the hotel division to demonstrate independent growth. Acquiring an operating asset with immediate revenue — rather than a greenfield build — accelerates that narrative.

## What NRIs Should Know

For the Keralite diaspora, the practical implications are straightforward. ITC properties command premium pricing but deliver consistent standards that few independent resorts in Kerala match. Expect upgraded F&B (ITC's kitchens are arguably India's best hotel dining operations), a properly curated Ayurvedic spa programme, and integration with ITC's loyalty ecosystem.

The Kumarakom backwaters remain one of the most photogenic and culturally immersive destinations in India. A houseboat cruise on Vembanad Lake, the Kumarakom Bird Sanctuary next door, and the Kottayam heritage churches nearby make it a natural anchor for multi-generational family trips — exactly the kind of travel that NRIs plan around December holidays and summer breaks.

Rates at The Zuri currently range from Rs 12,000 to Rs 45,000 per night depending on season and villa category. ITC's repositioning will almost certainly push the higher end upward, so NRIs planning a Kerala trip later this year may want to book before the rebrand is complete."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "ITC Hotels Buys Its Way Into Kerala — and the Backwater Resort NRIs Already Love",
    "subheadline": "The Rs 205 crore acquisition of Zuri Kumarakom gives ITC its first owned property in Kerala, targeting the Keralite diaspora's favourite lakeside retreat.",
    "slug": make_slug("itc-hotels-acquires-zuri-kumarakom-kerala-resort-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Kerala has one of India's largest diaspora communities. Kumarakom is already a top destination for NRI family reunions and post-wedding trips. ITC's acquisition means upgraded standards at a property the diaspora already knows.",
    "tags": ["travel", "hotels", "kerala", "itc-hotels", "luxury", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Restaurant India", "url": "https://www.restaurantindia.in/news/itc-hotels-acquires-the-zuri-kumarakom-resort.html"},
        {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/domestic-hotels/"},
        {"name": "ITC Hotels Official", "url": "https://www.itchotels.com/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Kumarkom.jpg/3840px-Kumarkom.jpg",
    "body": art1_body,
}

# ─────────────────────────────────────────────
# ARTICLE 2: Air India Summer Cabin Makeover
# ─────────────────────────────────────────────

art2_body = """Air India is about to cross the most visible threshold in its three-year transformation. From August 1, 2026, the airline will deploy retrofitted Boeing 787-8s with brand-new cabin interiors on its London Heathrow–Bengaluru route, and simultaneously upgrade its Delhi–Toronto service to daily frequency using the factory-fresh Boeing 787-9 — the first Dreamliner built specifically for the post-privatisation Air India.

For the roughly 1.8 million Indian-origin residents in the UK and 1.6 million in Canada, these are not abstract fleet announcements. They are a direct upgrade to the two corridors that carry some of the heaviest NRI traffic in the world.

## What Changes on August 1

**London–Bengaluru**: The route shifts to Air India's retrofitted B787-8, which swaps the old 2-2-2 business class layout for a 1-2-1 herringbone configuration with direct aisle access and privacy doors. For the first time, premium economy will be available on this route. The retrofit took 12,825 man-hours over 45 days per aircraft — new seats, new IFE systems, new carpets, overhauled galleys, refreshed lavatories, and updated overhead bins.

This completes Air India's transition: every single Heathrow operation will now fly aircraft with new cabin interiors.

**Delhi–Toronto**: The route upgrades to daily service using VT-AWA, Air India's first "line-fit" 787-9 — delivered from Boeing's Everett factory in January 2026 with interiors designed and installed on the production line, not retrofitted later. The aircraft seats 296 across business, premium economy, and economy, and sets the standard Air India intends to replicate across its entire long-haul Boeing fleet.

## The Fine Print

There are caveats, and NRIs booking premium cabins should know them. The business class suite on the new 787-9 includes sliding privacy doors, but these will remain fixed in an open position until the FAA completes certification. The seats themselves are fully functional — you just won't get the door. Additionally, 18 economy seats have been blocked from sale due to a regulatory interpretation issue with the RECARO 3710 seat family, reducing economy capacity slightly.

## The Bigger Picture

These August changes are the leading edge of a US$400 million product investment that Air India announced as part of its Tata Group transformation. The airline is retrofitting its entire fleet of 26 B787-8s and six B787-9s inherited from Vistara, with upgrades expected to be complete by mid-2027. The Boeing 777-300ER fleet follows after that.

Air India has also taken delivery of Airbus A350-900s, which already operate on Delhi–London with the airline's flagship cabin product, and A350-1000 deliveries are expected later this year.

For NRIs who have spent years enduring Air India's ageing interiors on critical diaspora routes, the August 1 switchover is the moment the airline's promises start showing up where it matters — in the seat you actually sit in for 10 to 14 hours."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's August Upgrade Hits the Two Routes NRIs Fly Most",
    "subheadline": "From August 1, London–Bengaluru gets premium economy and new business class suites, while Toronto goes daily on Air India's first factory-fresh Dreamliner.",
    "slug": make_slug("air-india-august-upgrade-london-bengaluru-toronto-787-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "UK and Canada have the largest Indian diaspora populations outside the Gulf. The London-Bengaluru and Delhi-Toronto corridors are among the highest-demand NRI routes globally. New premium economy and upgraded business class directly affect diaspora travel quality.",
    "tags": ["travel", "airlines", "air-india", "boeing-787", "nri", "london", "toronto"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aerospace Global News", "url": "https://aerospaceglobalnews.com/news/air-india-gives-date-for-new-b787-9s-inaugural-heathrow-flight/"},
        {"name": "Travel Daily Media", "url": "https://www.traveldailymedia.com/air-india-welcomes-first-boeing-787-9/"},
        {"name": "Head for Points", "url": "https://www.headforpoints.com/2026/05/air-india-refurbished-boeing-787-8/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "body": art2_body,
}

# ─────────────────────────────────────────────
# ARTICLE 3: Vande Bharat Sleeper Mumbai-Bengaluru
# ─────────────────────────────────────────────

art3_body = """The Indian Railways has approved the launch of a Vande Bharat Sleeper service between Mumbai and Bengaluru — India's second overnight semi-high-speed train and arguably the one NRIs have been asking for since the concept was first floated.

Union Railway Minister Ashwini Vaishnaw confirmed the approval in April, following the successful launch of the inaugural Vande Bharat Sleeper on the Howrah–Kamakhya route in January. The Mumbai–Bengaluru service will cover approximately 800 km with projected journey times of 15 to 17 hours, compared to the 22 hours that conventional express trains typically take on this corridor.

## What Makes It Different

The Vande Bharat Sleeper is not your parents' Rajdhani. Built by BEML with technology from the Integral Coach Factory, each 16-coach trainset carries over 1,100 passengers in three classes: AC 3-Tier, AC 2-Tier, and AC First Class. The First Class cabins include hot-water showers — a first for Indian Railways sleeper services.

The onboard experience leans toward airline-style standards: automatic doors, bio-vacuum toilets, USB charging at every berth, reading lights, Wi-Fi, real-time information displays, and a pantry car serving hot meals and regional dishes through an app-based ordering system. The train operates at 160 to 180 kmph, with better suspension and noise insulation than anything currently running overnight on Indian tracks.

Safety upgrades include fire-retardant materials, GPS tracking, AI-supported monitoring, and emergency braking systems. Trial runs were completed in both Lucknow and Mumbai earlier this year.

## Why Mumbai–Bengaluru Matters to NRIs

These are India's two busiest corporate cities, connected by one of the most heavily travelled domestic air corridors. For NRIs visiting India on business or family trips, the Mumbai–Bengaluru shuttle is often unavoidable — and flights on this route are frequently delayed, overbooked, and priced aggressively during peak periods.

The Vande Bharat Sleeper offers something flights cannot: you board after dinner, sleep in a proper berth, and arrive ready for a morning meeting. No airport transfers, no security queues, no luggage drama. For families travelling with children or elderly parents — the demographic reality of most NRI India trips — the sleeper is vastly less stressful than a flight.

The economics work too. Current AC 2-Tier fares on the Mumbai–Bengaluru corridor run Rs 1,800 to Rs 2,500 depending on class and season. Even if the Vande Bharat Sleeper commands a modest premium over conventional trains, it will still undercut last-minute airfares on this route by a wide margin.

## When It Launches

Indian Railways has not announced an exact launch date, but the service is expected to begin operations later in 2026 as more Vande Bharat Sleeper trainsets are delivered. Over 50 trainsets are slated for production by mid-2026, with additional routes under evaluation including Delhi–Mumbai and Chennai–Bengaluru.

For NRIs planning India trips this winter, the Mumbai–Bengaluru Vande Bharat Sleeper may well be running by then — and it could change how you think about getting between India's two tech capitals."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Sleeper Train Revolution Reaches Mumbai–Bengaluru",
    "subheadline": "The Vande Bharat Sleeper will cut the overnight journey between India's two biggest tech cities from 22 hours to under 17 — with showers, Wi-Fi, and app-ordered meals.",
    "slug": make_slug("vande-bharat-sleeper-mumbai-bengaluru-nri-overnight-train"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Mumbai and Bengaluru are the two cities NRIs visit most for business and family. The Vande Bharat Sleeper offers a comfortable overnight alternative to expensive, delayed flights on one of India's busiest corridors.",
    "tags": ["travel", "railways", "vande-bharat", "mumbai", "bengaluru", "trains", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-vande-bharat-sleeper-train-mumbai-bengaluru/"},
        {"name": "EaseIndiaTrip", "url": "https://www.easeindiatrip.com/blog/vande-bharat-sleeper-trains/"},
        {"name": "Glance", "url": "https://trends.glance.com/en/railways/mumbai-bengaluru-vande-bharat-sleeper"}
    ]),
    "score_total": 70,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
    "body": art3_body,
}

# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
