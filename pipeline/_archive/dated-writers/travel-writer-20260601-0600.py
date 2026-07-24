#!/usr/bin/env python3
"""Travel writer — 2026-06-01 06:00 UTC run. 2 articles."""
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Iran War Is Pushing US-India Airfares to Their Highest Levels in a Decade",
        "subheadline": "Gulf airspace closures, jet fuel above ₹1 lakh per kilolitre, and 250 fewer daily domestic flights are converging into the worst summer for NRI travel budgets since the pandemic.",
        "slug": make_slug("iran-war-us-india-airfares-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying home this summer face a triple hit: surging international fares from US gateways, fuel surcharges on every carrier touching the Gulf, and a domestic Indian flight shortage that makes onward connections harder to book and more expensive. The summer window — when most diaspora families visit — is being squeezed from every direction.",
        "tags": ["travel", "airlines", "airfares", "iran-war", "nri", "summer-2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/travel-news/air-india-indigo-to-cut-250-daily-domestic-flights-from-june"},
            {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/national/delhi-flight-fares-soar-up-to-30-percent-as-air-india-indigo-announce-to-slash-250-daily-domestic-flights-from-june"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/soaring-prices-during-the-iran-war-jeopardize-travel-to-tourism-dependent-countries-in-asia/article69638292.ece"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/the-fragile-sky-how-rising-inflation-and-the-middle-east-energy-crisis-jeopardize-asian-tourism/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36622441/pexels-photo-36622441.jpeg",
        "body": """The arithmetic of flying to India this summer is brutal. Aviation turbine fuel in India has crossed ₹1,00,000 per kilolitre — up roughly 25 per cent from ₹80,000 earlier this year — driven by crude oil volatility tied directly to the ongoing Iran conflict. Airlines are not absorbing the hit. They are passing it to you.

## The Numbers Are Not Abstract

Air India, Air India Express, and IndiGo — which together carry more than two-thirds of India's domestic passengers — are pulling roughly 250 flights a day from their June schedules. That is not a rounding error. That is a structural reduction in available seats across the country's busiest corridors.

The consequences showed up immediately. Last-minute fares out of Delhi have jumped 20 to 30 per cent in a single week. Delhi to Mumbai, once a ₹5,000-6,000 economy hop, now routinely crosses ₹12,000 to ₹16,000 for spot bookings. Delhi to Bengaluru and Chennai have climbed to ₹14,000-15,000 in economy. Even short regional hops — Delhi to Lucknow, Delhi to Patna — are touching ₹7,500-9,000 during peak hours.

Domestic fuel surcharges of ₹400 to ₹450 per passenger are now standard across carriers.

## Why the Gulf Matters to Your JFK-DEL Ticket

For NRIs, the pain is not limited to what happens after landing. The Iran war has intermittently closed airspace over the Persian Gulf and forced temporary shutdowns at some Gulf airports. That matters enormously because roughly half of all US-India traffic routes through Abu Dhabi, Dubai, or Doha.

When carriers cannot fly their usual Great Circle routes through the Gulf, they take longer detours — burning more fuel on every sector. Cathay Pacific, which connects many NRIs through Hong Kong, has doubled its fuel surcharge: medium-haul legs went from HK$264 to HK$633, and long-haul from HK$569 to HK$1,362. Air India has implemented its own sharp surcharge increases.

The result is a compounding effect. Your international fare from SFO or JFK is higher. Your fuel surcharge is higher. And when you land in India, your connecting domestic flight — if it has not been cancelled outright — costs more too.

## What NRIs Should Actually Do

**Book now, not later.** Fare trends are moving in one direction. Airlines are not adding summer capacity — they are cutting it. Waiting for a deal is a losing strategy this year.

**Consider European hubs over Gulf hubs.** Lufthansa, Air France, and SWISS are all expanding India services this summer and winter. European airspace is unaffected by the Gulf conflict, and their routing avoids the surcharge volatility hitting Gulf-hub carriers. A Frankfurt or Paris connection may cost the same as a Dubai one — and arrive more reliably.

**Be flexible on your India domestic legs.** If your connecting flight from Delhi to your hometown gets cancelled or repriced, rail is a real option on many corridors. Vande Bharat services now cover over 50 routes. Delhi to Lucknow by Vande Bharat takes about six hours and costs under ₹2,000 — less than a third of what the same flight costs at peak pricing.

**Watch for off-peak windows.** Late August and September, when the monsoon keeps leisure demand low, will likely see the first domestic fare corrections. If your travel dates have any flexibility, shifting even two weeks later can save thousands.

## The Bigger Picture

This is the first time since the pandemic that summer India travel — the single most important booking window for the diaspora — faces a simultaneous squeeze on both the international and domestic sides. The Iran conflict shows no signs of de-escalation. Fuel markets remain volatile. And airlines, already operating on thin margins, have made clear they will protect their balance sheets before they protect your fare.

Plan accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Lufthansa Is Betting Big on Asia This Winter — and NRIs Should Pay Attention",
        "subheadline": "Kuala Lumpur returns after a decade, the new Allegris cabin product lands on the Singapore route, and the group's India bet deepens with five weekly Zurich-Bengaluru flights.",
        "slug": make_slug("lufthansa-winter-expansion-asia-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With Gulf carriers facing fuel surcharges and airspace disruptions from the Iran conflict, Lufthansa Group's European hub expansion gives NRIs a compelling alternative routing — Frankfurt, Munich, and Zurich connections to India that avoid the Gulf entirely, with a new premium cabin product that rivals the Gulf carriers' business class.",
        "tags": ["travel", "airlines", "lufthansa", "europe", "business-class", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/lufthansa-group-winter-expansion-new-long-haul-routes-to-kuala-lumpur-bengaluru-seoul-and-north-america-boost-global-travel-connectivity/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/lufthansa-and-swiss-introduce-new-long-haul-routes-enhance-singapore-zurich-bengaluru-services/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/africa-and-asia-await-new-direct-european-flights-create-fresh-travel-opportunities/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/D-AIXO_Lufthansa_A359_MUC_%22Ulm%22_%2849033191421%29.jpg/3840px-D-AIXO_Lufthansa_A359_MUC_%22Ulm%22_%2849033191421%29.jpg",
        "body": """Lufthansa Group has announced the most aggressive long-haul expansion in its recent history, and the winter 2026-27 schedule reads like a deliberate play for exactly the kind of traveller NRIs are: frequent, premium-cabin-inclined, and increasingly looking for alternatives to Gulf-hub routing.

## What Is Actually Launching

The headline move is Lufthansa's return to Kuala Lumpur after a decade-long absence. Starting 25 October, Frankfurt to KL will operate five times weekly on Boeing 787-9 Dreamliners. For NRIs, KL is not a random Southeast Asian leisure destination — it is a major transit point for those visiting Malaysia's substantial Indian diaspora (roughly 2 million people of Indian origin) and a popular layover option for flights connecting to Singapore.

The second marquee announcement is the deployment of Lufthansa's new Allegris cabin product on the Munich-Singapore route from 26 October, operating on Airbus A350s. Allegris represents Lufthansa's complete cabin overhaul — new First Class suites, redesigned business class seats with direct aisle access, a genuine premium economy product, and a refreshed economy cabin. The airline has explicitly positioned it as a competitive answer to the Gulf carriers' premium products.

For US-based NRIs, the winter schedule also adds 11 new Allegris-equipped long-haul routes from Frankfurt alone — including Vancouver, Houston, Denver, Atlanta, Detroit, and Seoul. Munich picks up expanded services to Singapore, Washington, and Cape Town.

## The SWISS Bengaluru Play

Within the same group, SWISS International Air Lines will launch its first-ever route to southern India: Zurich to Bengaluru, five times weekly from October. SWISS already serves Delhi and Mumbai, but the Bengaluru addition is the piece that matters most for the tech diaspora — the Zurich-BLR route directly connects the Swiss financial centre with India's technology capital, serving the estimated 350,000-plus Indian tech workers who shuttle between Silicon Valley and Bengaluru's Outer Ring Road.

SWISS is also adding Zurich-Johannesburg and Zurich-Shanghai, extending its A350 network into corporate travel corridors where Gulf carriers have dominated.

## Why This Matters Now — Not Just in October

The timing is not accidental. The ongoing Iran conflict has made Gulf routing less predictable. Persian Gulf airspace closures have forced reroutings, Gulf hub airports have faced intermittent disruptions, and fuel surcharges on every carrier touching the region have spiked. For NRIs accustomed to booking Emirates or Etihad through Dubai and Abu Dhabi, the calculus has shifted.

European hub routing — through Frankfurt, Munich, or Zurich — sidesteps the Gulf entirely. The flights are marginally longer on the map, but when you factor in real-world delays from airspace restrictions, the total journey time difference shrinks. And the Allegris product is Lufthansa's clearest attempt to compete with Emirates business class on experience, not just price.

## The Practical NRI Routing Math

Consider a San Francisco-based NRI flying to Bengaluru for Diwali in October. The traditional route: SFO → Dubai → BLR on Emirates, roughly 22-24 hours with layover. The Lufthansa Group alternative: SFO → Frankfurt → BLR on Lufthansa + SWISS (or SFO → Zurich → BLR on SWISS codeshare), roughly 20-24 hours depending on connection.

With Allegris cabins on the SFO-Frankfurt leg and a new SWISS service on the Zurich-BLR leg, the European routing is no longer the compromise it once was. Add Miles & More status (Lufthansa Group's frequent flyer programme, which also covers United flights for Star Alliance members), and the loyalty math starts to favour the switch.

From the East Coast, the numbers look even better. Newark or JFK to Frankfurt is barely seven hours, putting BLR within striking distance of a 16-17 hour total journey with a decent Frankfurt connection.

## What to Watch

Lufthansa has not yet announced Allegris pricing on the India-relevant routes, and the Zurich-BLR fares have not appeared on booking engines. The winter schedule goes on sale in the coming weeks.

NRIs who currently route through Dubai should start watching Lufthansa Group fares to India for October-December travel. With the Gulf uncertainty unlikely to resolve before winter, and Lufthansa clearly building capacity to capture exactly this demand, the European hub option deserves serious consideration — especially for anyone flying premium cabins, where the Allegris product is the airline's best competitive weapon in years."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
