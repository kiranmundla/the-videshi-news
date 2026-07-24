#!/usr/bin/env python3
"""
Videshi Travel News Writer — 2026-06-30 03:00 PDT
Writes 2 fresh travel articles for The Videshi.
"""
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


# ── Article 1 ──────────────────────────────────────────────────────────────
article1_body = """Southern Railway has just doubled the Bengaluru–Ernakulam Vande Bharat Express from eight coaches to sixteen, effective the first week of July. Seating jumps from roughly 530 passengers per trip to 1,128 — nearly 600 extra seats on one of South India's most in-demand intercity routes. The timing is deliberate: Onam bookings were already selling out weeks in advance, and the expanded rake is meant to absorb the festive surge before it overwhelms the waiting lists.

For NRIs planning a summer trip home, the upgrade is a small but meaningful signal. India's premium rail network is no longer the same cramped, uncertain experience it was even two years ago — and the changes coming over the next twelve months will be far bigger than an extra eight coaches on a single route.

## The bigger story: Vande Bharat goes sleeper

The Integral Coach Factory in Chennai is building a 24-coach Vande Bharat Sleeper prototype scheduled to roll out by the end of 2026. Unlike the current chair-car sets — designed for daytime intercity runs of four to eight hours — the sleeper version is built for overnight journeys. It will feature berths across AC First Class, AC 2-Tier, and AC 3-Tier, running at up to 160 km/h.

If the testing goes to plan, the sleeper Vande Bharat will eventually replace the ageing Rajdhani and Duronto Express trains on routes like Delhi–Mumbai, Delhi–Kolkata, and Bengaluru–Chennai. For NRIs accustomed to booking domestic flights for these corridors, an overnight train that departs at 10 pm and arrives by 7 am — in a modern, air-conditioned coach with bio-vacuum toilets, GPS-based displays, and automatic doors — could genuinely compete on convenience.

## What NRIs need to know for this summer

The network already has more than 40 operational Vande Bharat sets across India's busiest intercity routes. Several are directly useful for NRI visitors:

**Bengaluru–Ernakulam**: Now 16 coaches. Covers the Bengaluru–Kerala corridor in under 9 hours — faster and more comfortable than driving, cheaper than flying if you book early. Ideal for NRIs with family across both states.

**Delhi–Varanasi**: The Vande Bharat on this route takes about 8 hours, versus 12+ on conventional trains. For NRIs visiting family in eastern UP or heading to Kashi, the time saving is material.

**Jammu–Srinagar**: Launched in 2026 on the newly completed Udhampur–Srinagar–Baramulla rail link. The scenic journey through the Pir Panjal range takes under 4 hours, replacing an unpredictable 10-hour road drive. The train has been running at full capacity since launch and was recently upgraded to 20 coaches.

**Secunderabad–Visakhapatnam**: Cuts the journey from 12.5 hours to 8.5 hours. Useful for NRIs with roots in both Telugu-speaking states.

## The booking reality

Seats fill fast, especially on new routes and during festival season. IRCTC's booking window opens 120 days in advance. If you are flying into India in July or August, book your Vande Bharat legs as soon as your travel dates are confirmed. Tatkal (last-minute) booking opens one day before departure, but availability is a coin toss on popular routes.

Fares remain reasonable by international standards — the Bengaluru–Ernakulam chair car costs roughly ₹1,400 (about $17) in second class. But Vande Bharat trains do not have a general unreserved section, so every passenger needs a confirmed ticket.

## The bigger picture

India is spending heavily on rail. The government launched more than 40 Vande Bharat sets in under three years, with another 200+ on order. RVNL, the rail infrastructure arm, is targeting full production-scale delivery of the sleeper variant by 2032. The Jammu–Srinagar route alone required years of tunnelling and bridge-building through some of the most difficult terrain on the subcontinent.

For NRIs who have not taken an Indian train in a decade, the gap between memory and reality is widening fast. The next time you visit, the smartest move might not be another ₹8,000 domestic flight — it might be a ₹1,400 train ticket booked four months in advance."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Vande Bharat Trains Just Doubled Capacity on a Key South India Route — and the Sleeper Version Is Next",
    "subheadline": "Southern Railway has expanded the Bengaluru–Ernakulam express to 16 coaches ahead of Onam. Meanwhile, a 24-coach overnight sleeper prototype is on track to roll out by year-end, eventually replacing the Rajdhani on routes NRIs actually fly.",
    "slug": make_slug("vande-bharat-bengaluru-ernakulam-doubles-sleeper-train-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India this summer will find a dramatically upgraded intercity rail network — with 40+ Vande Bharat sets already running, the Bengaluru–Kerala corridor just doubled, and an overnight sleeper version that could replace Rajdhani trains coming by year-end.",
    "tags": ["travel", "vande-bharat", "indian-railways", "trains", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/p4t9ayvshhph/"},
        {"name": "Metro Rail Today", "url": "https://metrorailtoday.com/news/icf-to-roll-out-first-24-coach-vande-bharat-sleeper-train-by-end-of-2026"},
        {"name": "Metro Rail Today", "url": "https://metrorailtoday.com/news/rvnl-targets-june-2026-launch-for-vande-bharat-sleeper-train-prototype-full-rollout-by-2032"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
    "image_caption": "A Vande Bharat Express train near Mumbai, part of India's rapidly expanding semi-high-speed rail network",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}

# ── Article 2 ──────────────────────────────────────────────────────────────
article2_body = """India has received 42 per cent less rainfall than normal since the monsoon season officially began on June 1, according to data compiled by the India Meteorological Department. In some regions, the deficit runs as high as 92 per cent. The monsoon reached Kerala three days late, then stalled across western India for nearly two weeks. As of the last week of June, the seasonal rains have yet to hit Delhi, most of Rajasthan, and large parts of northern India.

For farmers, this is bad news. For NRIs planning a July trip home, it is — counterintuitively — an opportunity.

## Why a weak monsoon matters for travel

A below-normal monsoon means fewer of the disruptions that typically make July travel in India miserable: waterlogged roads, cancelled domestic flights, landslides on hill routes, and the dreary indoor-only days that make sightseeing a write-off. The IMD has forecast 2026 monsoon rainfall at 92 per cent of the long-period average — the lowest since 2023 — driven by El Niño conditions in the Pacific.

The practical effects are already visible. Domestic flight fares have dropped 30 to 50 per cent compared with peak winter pricing. Hotel rates across North India are at their seasonal lows. And several regions that NRIs typically avoid in monsoon — Rajasthan, the Golden Triangle, Gujarat, and the northern plains — are experiencing drier, more predictable conditions than usual.

## Where to go

**Rajasthan**: Normally the monsoon's green season, but this year Rajasthan has received well below-average rain. Udaipur's lakes are calm, Jaisalmer's desert is accessible, and Jaipur's palace circuit is uncrowded. Hotel rates are 40-60 per cent below winter peaks. The newly opened JW Marriott Ranthambore and the upcoming Leela Jaisalmer are worth watching.

**Ladakh and Spiti**: These rain-shadow regions ignore the monsoon entirely. July is peak season here — dry, sunny, and cool — with the Manali–Leh highway and the Rohtang tunnel keeping access reliable. Book early; popular stays sell out by April.

**The Golden Triangle (Delhi–Agra–Jaipur)**: With the monsoon's late arrival, Delhi is hot but dry well into early July. The Taj Mahal is at its least crowded. Air-conditioned trains on the Vande Bharat network cover the triangle efficiently. The new Delhi–Mumbai Expressway also makes road trips to Rajasthan faster than ever.

**Goa**: The off-season delivers empty beaches, rock-bottom hotel rates, and monsoon-specific experiences like spice plantation tours, waterfall hikes, and Goan seafood at local prices rather than tourist markups. The rains that do arrive tend to come in sharp afternoon bursts, leaving mornings clear.

## Where to be cautious

The weak monsoon does not mean no rain. The Western Ghats — Maharashtra's hill stations, Kerala's backwaters, and Karnataka's coast — are still receiving moderate to heavy spells. If your itinerary includes Munnar, Coorg, or Mahabaleshwar, pack waterproof gear and keep plans flexible. Uttarakhand and Himachal are seeing scattered rain with landslide advisories on some mountain roads.

The IMD has also warned of heatwave conditions in Uttar Pradesh through early July, with temperatures exceeding 42°C in parts of the Gangetic plains. If you are visiting family in Lucknow, Varanasi, or Allahabad, midday hours will be brutal. Plan indoor activities or early-morning outings.

## The practical NRI checklist for July travel

**Flights**: Domestic fares are at annual lows. Book flexible tickets — monsoon disruptions are rarer this year but not impossible. IndiGo and Air India Express are adding summer capacity on key routes.

**Trains**: Vande Bharat services on the Delhi–Varanasi, Bengaluru–Ernakulam, and Secunderabad–Vizag corridors are running at full capacity. Book through IRCTC at least 60 days in advance.

**Hotels**: Negotiate directly with properties for stays longer than three nights. Many luxury hotels in Rajasthan and Goa are offering monsoon packages at 50 per cent or more off rack rates.

**Health**: The Air Suvidha 2.0 health declaration is now required for all international arrivals — fill it out before you fly. Carry mosquito repellent regardless of rainfall; dengue season does not need heavy rain.

**Roads**: India's expressway network has quietly expanded. The Delhi–Mumbai Expressway, the Samruddhi Mahamarg (Mumbai–Nagpur), and several upgraded national highways have halved driving times on popular NRI road-trip routes. If the monsoon holds off, July is one of the best months for a North India drive.

## The bottom line

The weak 2026 monsoon is creating an unusual window. Prices are low, crowds are thin, and the weather across much of North and West India is drier than any July in recent memory. For NRIs whose summer plans are not yet locked, this is the year to book that Rajasthan circuit, that Goa long weekend, or that Golden Triangle trip your parents have been asking about — before the monsoon finally catches up."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Weak Monsoon Is Quietly Making This July the Best Window for NRI Travel in Years",
    "subheadline": "Rainfall is 42 per cent below normal. Domestic fares have cratered. Hotel rates are at rock bottom. For once, the monsoon's bad news for farmers is unexpectedly good news for NRIs planning a summer trip home.",
    "slug": make_slug("india-weak-monsoon-july-nri-travel-window-2026"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The delayed, weak 2026 monsoon has created unusually dry and affordable travel conditions across North and West India in July — a rare window for NRIs to visit Rajasthan, the Golden Triangle, and Goa at off-season prices without the usual monsoon misery.",
    "tags": ["travel", "monsoon", "india", "nri-travel-guide", "summer"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/environment/indias-summer-crop-planting-lags-after-slow-monsoon-start-2026-06-29/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/environment/india-makes-contingency-plans-weak-monsoon-threatens-some-farm-areas-2026-06-23/"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/india-monsoon-travel/"},
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/19100110/pexels-photo-19100110.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
    "image_caption": "A traveller in monsoon rain gear amid the lush greenery of Lonavala, India",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ── Insert ─────────────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
