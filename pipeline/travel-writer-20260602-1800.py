#!/usr/bin/env python3
"""Travel writer — 2 June 2026, 18:00 UTC run."""

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

# ── ARTICLE 1 ─────────────────────────────────────────────────────────
art1_body = """IndiGo's experiment with wide-body transatlantic flying just took its first casualty. The airline will "temporarily discontinue" all services between India and Manchester from 31 August 2026, returning one of the six Boeing 787-9 Dreamliners it had leased — crew included — from Norway's Norse Atlantic Airways.

The decision strips Northern England's only direct link to India, a route that served roughly half a million people of Indian heritage in the Manchester Airport catchment area. For British Indians who had grown accustomed to bypassing London Heathrow on their way to Mumbai and Delhi, the loss is immediate and practical.

## What happened

IndiGo damp-leased the six Dreamliners from Norse Atlantic in early 2025 as a bridging strategy: fly wide-body European routes now, wait for its own Airbus A350-900 fleet to arrive later. Manchester was the flagship, IndiGo's first-ever European destination, followed quickly by Amsterdam.

The economics worked — until they didn't. Three factors converged. First, the US-Iran war closed Iranian airspace, forcing India-Europe flights onto longer, costlier routing. Second, global jet fuel prices spiked roughly 25 percent, driven by Strait of Hormuz disruptions. Third, the Indian rupee weakened against the dollar, inflating lease and fuel payments denominated in foreign currency.

"It is unfortunate that longer flying times due to airspace constraints coupled with dramatically escalating costs compelled us to take the decision," said Abhijit Dasgupta, IndiGo's senior vice-president for network planning and revenue management. He stressed the suspension is "temporary in nature."

## The bigger picture

IndiGo is not alone. Air India is making even deeper cuts to its wide-body programme for the same reasons, trimming roughly 22 percent of its domestic operations and scaling back long-haul frequencies. Between the two carriers — which together command over 90 percent of India's domestic aviation market — the Indian flying public is entering its most constrained summer in years.

For IndiGo specifically, Manchester was always a calculated bet. The airline had no wide-body aircraft of its own and relied entirely on Norse Atlantic's planes and operating crew. That arrangement gave IndiGo quick access to the lucrative UK-India corridor but left it exposed to exactly the kind of cost shock the Iran war delivered.

The remaining five Dreamliners continue to operate IndiGo's other European services "as planned," the airline says. But the precedent is set: if costs do not ease, more routes could follow.

## What this means for NRIs

For the estimated 1.8 million people of Indian origin in the UK, Manchester was more than a convenience — it was a statement that Indian carriers finally understood the diaspora extends beyond London. The route cut forces British Indians in the Midlands and North back onto connecting flights through Heathrow, or onto Gulf carriers routing through Dubai or Doha, adding hours and cost to every trip home.

The timing is particularly poor. Summer is peak season for family visits to India, and fares on the remaining London-India services are already elevated. NRIs who had booked IndiGo Manchester flights beyond 31 August will need to rebook, and the alternatives will not be cheap.

IndiGo says it plans to resume the route once its own A350-900s enter service, but no date has been given. Until then, Manchester's half-million-strong Indian community will have to take the long way round."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo Pulls Its Manchester Dreamliners — Half a Million British Indians Lose Their Direct Link to India",
    "subheadline": "Rising fuel costs and Iran war airspace closures have killed IndiGo's first European route. Northern England's Indian diaspora is back to connecting through London or the Gulf.",
    "slug": make_slug("indigo-manchester-dreamliner-route-cut-uk-india-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Half a million people of Indian heritage in the Manchester Airport catchment area lose their only direct route to India. British Indians in Northern England must revert to connecting through London Heathrow or Gulf hubs, adding hours and cost during peak summer travel season.",
    "tags": ["travel", "airlines", "IndiGo", "UK", "Manchester", "wide-body", "Iran war"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CurrentIndia.com", "url": "https://currentindia.com/news/after-air-india-indigo-to-cut-wide-body-flights-too"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-indigo-and-air-india-express-cut-250-domestic-flights-daily/"},
        {"name": "Hospitality News India", "url": "https://hospitalitynews.in/aviation/indigo-and-air-india-reduce-domestic-flights/"},
        {"name": "Greater Manchester Business Board", "url": "https://gmbusinessboard.com/manchester-airport-and-indigo-announce-the-only-flights-between-the-north-and-indias-financial-capital-mumbai/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── ARTICLE 2 ─────────────────────────────────────────────────────────
art2_body = """India's state-owned oil refiners have frozen domestic jet fuel prices for June, handing airlines a rare reprieve in a season of cascading costs. But the gesture, while welcome, does little to reverse the damage already done: roughly 250 domestic flights are disappearing from Indian skies every day this summer, and fares for NRIs heading home show no sign of retreating.

## The freeze

Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum kept aviation turbine fuel at ₹1,04,927 per kilolitre in Delhi for June — unchanged from May, which was itself held flat after an 8.6 percent hike in April. The decision followed a direct appeal from India's airlines, which asked refiners to hold prices until the Iran war ends.

In a partial concession, refiners also reduced jet fuel prices for international flight operations, though the exact quantum has not been disclosed. The split pricing — frozen domestic, cut international — reflects the government's dual priority: shield domestic passengers from further fare hikes while easing margins on the long-haul routes where Indian carriers are haemorrhaging money.

## Why it matters

The freeze is part of a broader, quietly assembled rescue package for Indian aviation. Over the past two months, the government has:

- **Capped domestic ATF price increases** at 25 percent (imposed in April, still in effect)
- **Cut value-added tax on jet fuel** in Delhi and Maharashtra, India's two biggest aviation markets
- **Offered rebates on aircraft parking charges** at major airports
- **Removed airfare caps** and suspended the 60 percent free-seat allocation rule, giving airlines full pricing flexibility
- **Relaxed pilot flight-duty time limitations** for long-haul flights, responding to global aviation disruptions

Each measure, taken alone, is incremental. Together, they amount to the most interventionist aviation policy India has pursued since the pandemic. The implicit message: the government views the current crisis as existential for an industry projected to carry 50 crore passengers annually by 2030.

## The 250-flight gap

Despite this support, the arithmetic has not improved enough to keep planes in the air. Air India has announced the steepest reduction, cutting 22 percent of domestic operations during June and July — roughly 110 flights daily from a schedule of 500. IndiGo, India's largest carrier, is trimming 5 to 7 percent of domestic capacity, another 110 or so flights. Air India Express is cutting 10 percent of its 340 daily services.

The routes most affected connect India's major hubs — Delhi, Mumbai, Bengaluru, Hyderabad — with the tier-two and tier-three cities that NRI families actually fly to: Goa, Kochi, Lucknow, Jaipur, Ahmedabad, Kolkata, and Chennai. With over 90 percent of India's domestic market controlled by the Air India group and IndiGo, there are few alternatives.

## What NRIs should know

For the millions of Indian Americans planning summer visits home, the practical impact is straightforward: fewer domestic connections, fuller flights, and higher fares on the legs that get you from Delhi or Mumbai to your hometown.

International fares on the US-India trunk routes are already at their highest levels in a decade, driven by the same fuel costs and airspace detours. The domestic squeeze adds a second layer of pain. An NRI flying San Francisco to Kochi, for instance, now faces not just an expensive transoceanic ticket but a reduced, pricier domestic connection at the other end.

The fuel price freeze helps airlines' balance sheets but is unlikely to translate into lower consumer fares this summer. Airlines have been explicitly given pricing flexibility by the regulator, and with fewer seats chasing the same demand, the incentive to discount is nil.

**The realistic advice:** Book domestic Indian legs early, consider alternate routing through less congested airports, and budget for fares 15 to 25 percent above last summer's levels. The government's relief measures are keeping airlines solvent — but they are not keeping tickets cheap."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Freezes Jet Fuel Prices — but 250 Flights a Day Are Still Vanishing This Summer",
    "subheadline": "Refiners have frozen domestic aviation fuel prices and the government is quietly assembling a rescue package. For NRIs heading home, it may not be enough.",
    "slug": make_slug("india-jet-fuel-freeze-250-flights-cut-summer-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying home this summer face a double squeeze: record-high international fares on US-India routes plus fewer, costlier domestic connections to tier-2 cities. The government's fuel freeze helps airlines survive but won't lower ticket prices for travelers.",
    "tags": ["travel", "airlines", "jet fuel", "India aviation", "Iran war", "summer travel", "NRI"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/domestic-jet-fuel-prices-unchanged-for-june-as-international-rates-fall/article69643122.ece"},
        {"name": "OilPrice.com", "url": "https://oilprice.com/Energy/Energy-General/Indian-Refiners-Freeze-Domestic-Jet-Fuel-Prices.html"},
        {"name": "Madhyamam Online", "url": "https://www.madhyamamonline.com/en/business/airlines-slash-250-flights-fuel-shock-fare-surge"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-indigo-and-air-india-express-cut-250-domestic-flights-daily/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Aircraft_being_fueled_by_tanker.jpg",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ── PUBLISH ───────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
