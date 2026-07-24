#!/usr/bin/env python3
"""Travel writer - 2026-05-29 03:00 PDT run. Two articles on summer travel crunch."""

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

# Verify image URLs return 200 with image content-type and >5KB
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✅ Image verified: {url[:80]}... ({cl} bytes)")
            return True
        print(f"  ❌ Image failed: status={r.status_code}, ct={ct}, cl={cl}")
    except Exception as e:
        print(f"  ❌ Image error: {e}")
    return False


# ──────────────────────────────────────────────────────────────────
# Article 1: Air India & IndiGo slash summer flights
# ──────────────────────────────────────────────────────────────────

art1_image = "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png"
if not verify_image(art1_image):
    art1_image = "https://images.pexels.com/photos/27550030/pexels-photo-27550030.jpeg"

art1_body = """India's two largest airlines just cut the summer travel plans of millions — and NRIs headed home between June and August are squarely in the blast radius.

Air India will slash 22 per cent of its domestic flights from June 1 through August 31, eliminating more than 790 weekly services from its 3,600-flight domestic network. IndiGo, which carries more passengers than any other Indian airline, is trimming 7 to 10 per cent of domestic capacity over the same period and has already cut 17 per cent of its international operations.

Between them, the two carriers control roughly 90 per cent of India's domestic air passenger market. When they both pull back at once, it is effectively the whole market contracting.

## The Routes That Hurt Most

The domestic cuts are concentrated on corridors NRIs rely on to reach their hometowns after landing in Delhi or Mumbai. Out of Mumbai, frequencies to Ahmedabad, Nagpur, Patna, and Bhopal are being reduced. Out of Delhi, services to Hyderabad, Bengaluru, and Kolkata are losing frequency. Return legs on several southern routes are being axed too.

No route is being dropped entirely — the airlines are reducing how often they fly, not whether they fly. But if the remaining frequency does not align with your connecting flight, that is a problem money alone cannot solve.

## The US Routes Go Dark

More consequentially for the diaspora, Air India has already suspended or will suspend seven international routes from June 1: Delhi–Chicago, Delhi–Newark, Mumbai–New York JFK, Delhi–Shanghai, Chennai–Singapore, Mumbai–Dhaka, and Delhi–Malé.

The Delhi–Chicago and Delhi–Newark suspensions hit the heart of the NRI corridor. Chicago's O'Hare is the primary gateway for roughly 250,000 Indian Americans across Illinois, Wisconsin, and the broader Midwest. Newark serves the 700,000-strong Indian community in New Jersey and the tri-state area. With Mumbai–New York also gone, the entire Air India US network shrinks to Delhi–San Francisco and Bengaluru–San Francisco for the summer.

Passengers with existing bookings will be offered alternative flights, complimentary date changes, or full refunds. But "alternative flights" on a suspended route means codeshare partners or connections through the Gulf — the very layovers that Air India's nonstops were supposed to eliminate.

## Why Now

The culprit is jet fuel, which accounts for up to 40 per cent of an airline's operating expenses. The US–Israeli war with Iran, now entering its fourth month, has effectively closed the Strait of Hormuz to commercial shipping. Brent crude surged more than 50 per cent between March and May. Aviation turbine fuel in India hit record prices in April, and the market has not come back down.

Air India, which just reported a record annual loss exceeding $2.4 billion, is particularly exposed. The Tata-owned carrier is simultaneously absorbing Pakistan's ban on Indian overflights — which adds fuel-burning detours to every westbound flight — and a strong US dollar that inflates its dollar-denominated costs.

## What NRIs Should Do Now

**Book domestic connections immediately.** With 790 fewer weekly flights, seat availability on surviving Delhi–Hyderabad or Mumbai–Bengaluru services will tighten fast. Do not wait for last-minute deals — they are not coming this summer.

**Check your US–India itinerary.** If you are booked on Delhi–Chicago or Delhi–Newark through August, contact Air India now. The airline's rebooking options may include routing through San Francisco or connecting via partner airlines, but availability is limited.

**Consider foreign carriers.** Emirates, Qatar Airways, Singapore Airlines, Cathay Pacific, and British Airways are all adding India capacity as Indian carriers pull back. The connections add time, but they add certainty too.

**Watch for the Hormuz deal.** Iran's state television reported a draft framework this week that would restore shipping through the Strait within a month. If it holds, fuel prices could ease and some suspended routes might return early. But the ceasefire is fragile — renewed attacks were reported as recently as May 28 — so do not book around optimism."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India and IndiGo Just Gutted the Summer Flight Schedule — Here's What NRIs Lose",
    "subheadline": "A 22 per cent domestic cut by Air India, 7–10 per cent by IndiGo, and the suspension of Delhi–Chicago, Delhi–Newark, and Mumbai–New York routes leave the diaspora scrambling for summer connections.",
    "slug": make_slug("air-india-indigo-summer-flight-cuts-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Delhi-Chicago and Delhi-Newark suspensions directly impact the Midwest and tri-state NRI communities. Domestic cuts to tier-2 cities make onward connections from Delhi/Mumbai harder for diaspora visitors.",
    "tags": ["travel", "airlines", "air-india", "indigo", "flight-cuts", "iran-war", "fuel-prices"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-air-india-cut-domestic-flights-high-fuel-prices-sources-say-2026-05-28/"},
        {"name": "Daily Jagran", "url": "https://www.thedailyjagran.com/trending/air-india-to-cut-22-indigo-to-slash-7-domestic-flights-amid-high-fuel-prices"},
        {"name": "Daily Prabhat", "url": "https://dailyprabhat.com/high-fuel-prices-air-india-cuts-22-domestic-flights-indigo-trims-5-7-domestic-17-international/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": art1_image,
    "image_caption": "An Air India Boeing 777 at New York JFK — one of the US routes suspended for summer 2026.",
    "body": art1_body.strip()
}


# ──────────────────────────────────────────────────────────────────
# Article 2: US airfares hit record highs at NRI gateway airports
# ──────────────────────────────────────────────────────────────────

art2_image = "https://images.pexels.com/photos/27550030/pexels-photo-27550030.jpeg"
if not verify_image(art2_image):
    art2_image = None

art2_body = """San Francisco, Dulles, JFK, Newark — the airports that connect Indian Americans to the world are now among the most expensive in the country, and summer 2026 is shaping up to be the priciest flying season in memory.

A new study from Local Insider, using Bureau of Transportation Statistics data, ranks San Francisco International fourth among the costliest US airports with an average ticket price of $422 in 2026. Washington Dulles leads the nation at $439. JFK clocks in at $405, and Newark sits at $397. These four airports together handle the vast majority of direct India flights and are the primary departure points for the 4.4 million Indian Americans spread across the Bay Area, the DC metro, and the Northeast corridor.

## The $400 Ticket Is the New Normal

The numbers mark a sharp departure from even two years ago. Average domestic airfares across the US have risen 12 to 18 per cent year-on-year at major hubs, driven almost entirely by fuel costs. Brent crude has traded above $90 for most of 2026, and jet fuel hit a record $200 per barrel in April after the Strait of Hormuz was effectively closed by the US–Iran conflict.

Airlines are passing the pain straight through. Delta and United have raised ticket prices and baggage fees. American Airlines expects its fuel bill to rise by $4 to $5 billion this year. Southwest's CEO called the fare increases since February the steepest he has seen in 38 years in the industry.

For NRIs, the math is brutal. A round-trip economy ticket from SFO to Delhi that averaged $900 to $1,100 in 2024 now routinely clears $1,400 to $1,600 on Air India. Factor in the domestic connection from Delhi to a tier-2 hometown — itself more expensive and less available thanks to this week's Air India and IndiGo cuts — and a family of four is looking at $7,000 or more just to get home and back.

## The K-Shaped Summer

A Deloitte survey found that only 45 per cent of Americans made summer travel plans this year, the lowest in six years. The biggest drop came from the middle-income cohort — households earning $100,000 to $199,000 — where travel intent fell from 45 per cent to 37 per cent in a single year.

American Airlines CEO Robert Isom called the pattern "K-shaped": higher-income travellers are holding steady, while middle-income flyers are delaying, downgrading, or cancelling. This split matters for the Indian American community, which skews higher-income on average but includes hundreds of thousands of young professionals and H-1B families for whom a $7,000 summer trip home is a genuine financial stretch.

Some families are pivoting. Driving vacations and cruise packages — which bundle flights, hotels, and meals into a flat price — are seeing increased demand from cost-conscious travellers. Others are waiting longer to book, hoping fares will drop. Travel analysts say they probably will not — at least not before August, and not unless the Hormuz situation resolves.

## Where NRIs Can Find Relief

**Gulf carriers remain competitive.** Etihad, Emirates, and Qatar Airways are routing aggressively through Abu Dhabi, Dubai, and Doha to capture NRI demand that Indian carriers are shedding. Etihad fares from the US to India start around $380 one-way, well below Air India's nonstop pricing.

**Book midweek, fly off-peak.** Tuesday and Wednesday departures consistently show 15 to 20 per cent savings over weekend flights on India routes. If your schedule allows, departing in the first or last week of June — before peak summer demand — can save $200 to $300 per ticket.

**Use airline miles strategically.** With cash fares at record levels, the value of frequent flyer miles has never been higher. A United MileagePlus award ticket to India that cost 80,000 miles last year now represents $1,500 or more in avoided cash outlay. If you have been sitting on miles, this is the summer to spend them.

**Consider European stopovers.** SWISS just launched Zurich–Bengaluru nonstop, and British Airways is expanding India capacity. A London or Zurich stopover adds a few hours but can cut costs by $200 to $400, especially if booked as separate tickets on different carriers.

**Watch the Hormuz talks.** A draft framework for reopening the Strait surfaced this week. If shipping resumes, crude prices could drop 15 to 20 per cent within weeks, and airlines would face pressure to pull back fare increases. But the ceasefire is fragile, so plan around current prices, not future hopes."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "SFO, JFK, Dulles — Every Major NRI Gateway Is Now Among America's Priciest Airports",
    "subheadline": "Average airfares have surged past $400 at the airports Indian Americans rely on most, and the middle-income squeeze is forcing families to rethink their summer India trips.",
    "slug": make_slug("nri-gateway-airports-record-airfares-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "SFO, JFK, Dulles, and Newark are the primary departure points for 4.4 million Indian Americans. Record airfares at these hubs, combined with India route suspensions, are making summer trips home significantly more expensive.",
    "tags": ["travel", "airfares", "airports", "nri", "summer-travel", "iran-war", "fuel-prices"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/costlier-flights-hotels-divide-us-summer-travel-haves-have-nots-2026-05-29/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/05/28/business/jfk-is-one-of-nations-most-expensive-airports-as-flight-prices-surge/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/american-airlines-ceo-says-demand-resilient-enough-absorb-higher-fuel-costs-2026-05-28/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": art2_image,
    "image_caption": "Passengers wait at an airport terminal as summer airfares surge to record levels across the US.",
    "body": art2_body.strip()
}


articles = [art1, art2]

for art in articles:
    # Skip if image failed verification
    if art.get("image_url") is None:
        print(f"⚠️  {art['slug']}: No valid image, publishing without image")
        art.pop("image_url", None)
        art.pop("image_caption", None)
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
