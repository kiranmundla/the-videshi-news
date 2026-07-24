#!/usr/bin/env python3
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

# Verify images
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        return r.status_code == 200 and 'image' in ct and cl > 5000
    except Exception:
        return False

img1 = "https://images.pexels.com/photos/4461192/pexels-photo-4461192.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img2 = "https://images.pexels.com/photos/32649171/pexels-photo-32649171.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

for url in [img1, img2]:
    ok = verify_image(url)
    print(f"Image verify {'✅' if ok else '❌'}: {url[:80]}")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Indian Airports Crack the Skytrax World Top 100 — and NRIs Should Notice",
        "subheadline": "Delhi jumps four places to 28th globally, Bengaluru and Hyderabad climb double digits, and Goa's brand-new Manohar Airport debuts at 64th — a signal that flying into India is getting measurably better.",
        "slug": make_slug("skytrax-2026-indian-airports-top-100-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 4.4 million Indian Americans who fly into DEL, BLR, HYD, GOA, and BOM every year, these rankings translate directly into shorter immigration queues, better lounges, and less chaotic terminals.",
        "tags": ["travel", "airports", "india", "skytrax", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/worlds-top-airports-for-2026-announced-five-indian-hubs-earn-global-recognition"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/asian-airports-sweep-top-3-rankings-in-worlds-top-10-airports-2026-list-here-is-where-delhis-igi-mumbais-csmia-stand-11743333178485.html"},
            {"name": "Skytrax World Airport Awards", "url": "https://www.worldairportawards.com/worlds-top-100-airports-2026/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/mumbai-delhi-goa-airports-among-worlds-top-100-in-2026-1748572480216"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img1,
        "body": """The Skytrax World Airport Awards for 2026 are out, and India has its strongest showing yet. Five Indian airports have been ranked in the world's top 100, led by Delhi's Indira Gandhi International Airport at number 28 — a four-place climb from 32nd in 2025.

For the millions of NRIs who transit through these terminals every year, these are not abstract numbers. They represent real differences: faster immigration processing, cleaner restrooms, better food courts, and lounges that do not make you question your life choices during a four-hour layover.

## Delhi Leads the Pack

Delhi's IGI Airport did not just climb in the global rankings. It swept the regional awards, winning Best Airport in India and South Asia and picking up recognition for Best Airport Dining. The airport has invested heavily in Terminal 3 enhancements over the past two years, including expanded duty-free retail, improved signage in multiple Indian languages, and a significant upgrade to its immigration processing lanes.

For NRIs landing at DEL after a 16-hour flight from Newark or San Francisco, the difference is tangible. Immigration wait times at T3 have dropped from an average of 45 minutes to under 20 minutes during off-peak hours, partly thanks to the expanded e-gate system and DigiYatra facial recognition integration that went live across the terminal earlier this year.

## Bengaluru and Hyderabad: The Tech Corridor's Quiet Upgrades

Bengaluru's Kempegowda International Airport climbed seven places to 41st, winning Best Regional Airport in India and South Asia for the third consecutive year. The airport's Terminal 2, which opened in 2022, has matured into one of the most aesthetically distinctive terminals in Asia, with its garden-themed design and emphasis on natural light.

Hyderabad's Rajiv Gandhi International Airport made the biggest leap among Indian entries, jumping 13 places from 56th to 43rd. It won Best Airport Staff Service in India and South Asia — a recognition that matters more than it sounds. When your elderly parents are navigating an unfamiliar terminal with heavy luggage and limited English, staff who actually help make the difference between a smooth arrival and a stressful one.

For the estimated 800,000 Indian Americans with roots in Andhra Pradesh and Telangana, Hyderabad's rise in the rankings reflects a broader improvement in the travel experience on the increasingly popular SFO-HYD and ORD-HYD corridors.

## Goa Debuts, Mumbai Holds Steady

Goa's Manohar International Airport, which opened in late 2022 as a greenfield project, entered the Skytrax top 100 for the first time at 64th place. The airport serves India's most popular leisure destination and has been designed with international traffic in mind — wider taxiways, modern baggage handling, and a terminal that feels more like a resort lobby than an aviation facility.

Mumbai's Chhatrapati Shivaji Maharaj International Airport held at 66th. Given that it operates in one of the most space-constrained aviation environments in the world — two runways handling over 900 movements a day at peak — maintaining a top-100 spot is an achievement in itself. The Navi Mumbai airport, expected to begin operations later this year, should eventually relieve some of that pressure.

## What This Means for NRI Travel

The global top 10 remains dominated by Asian airports. Singapore Changi claimed the number-one spot for the 14th time, followed by Seoul Incheon, Tokyo Haneda, Hong Kong, and Tokyo Narita. No US airport made the top 10, though Vancouver (10th) and Houston George Bush (29th) represented North America.

For NRIs, the practical takeaway is this: the airports on both ends of the India corridor are improving. Delhi and Bengaluru are now ranked higher than Dallas-Fort Worth (48th), Los Angeles (49th), and San Francisco (which did not make the top 50). The gap between flying into an Indian airport and flying into an American one has narrowed considerably.

The next frontier is consistency. A gleaming new terminal means little if the taxi queue outside is chaotic or if the airport metro shuts down at midnight. But on the metric that Skytrax measures — the experience inside the terminal — India's airports are climbing, and NRIs who have not visited in a couple of years may be surprised by the difference."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Air Traffic Fell Off a Cliff in April — and NRIs Booking Summer Flights Should Brace",
        "subheadline": "Domestic passengers dropped 3%, international flights by Indian carriers plunged 37%, and the lean months have not even started yet. Here is what is driving the slump and what it means for diaspora travel this summer.",
        "slug": make_slug("india-air-traffic-decline-april-2026-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs booking summer flights to India face a paradox: fewer flights mean less competition on routes, but volatile fuel costs and a weakening rupee could push fares higher — especially on diaspora-heavy corridors like SFO-DEL and JFK-BOM.",
        "tags": ["travel", "airlines", "india", "aviation", "airfares"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/industry/why-indias-domestic-air-passenger-traffic-is-falling-despite-summer-travel-11780297376934.html"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/ireland-and-germany-joins-france-canada-spain-china-india-sweden-turkey-and-more-countries-in-declining-us-tourism/"},
            {"name": "DGCA India", "url": "https://www.dgca.gov.in"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": img2,
        "body": """Indian aviation just posted its worst April in years. Domestic carriers flew 13.8 million passengers last month, down over 3% from April 2025 — and the international numbers were far uglier. Indian airlines operated 37.2% fewer international flights compared to the same month last year, carrying 39.3% fewer passengers across borders.

For NRIs planning summer visits to India, this is not just an industry statistic. It is a signal that the flight options, pricing, and reliability you have come to expect on key diaspora routes may look different this year.

## What Is Behind the Slump

Three forces collided in April to ground Indian aviation's growth story.

**The West Asia war.** The ongoing conflict has disrupted airspace over the Persian Gulf and driven jet fuel prices sharply higher. Global oil prices have roughly doubled, and while India's government has capped Aviation Turbine Fuel increases at around 25% for domestic flights, airlines are absorbing massive losses. IndiGo alone lost over ₹2,500 crore last year, with a significant portion tied to foreign exchange losses as the rupee weakened.

**The AI job chill.** This is the less obvious factor, but it is real. India's information technology sector — historically one of the highest-spending segments in domestic and international air travel — is pulling back. As artificial intelligence reshapes service industry jobs, IT professionals are becoming more cautious about discretionary spending, including travel. The psychological effect extends beyond actual layoffs: the uncertainty itself is enough to make families postpone non-essential trips.

**The heatwave.** India recorded one of its most severe heatwaves in recent memory through April and May, with temperatures crossing 48°C in parts of Rajasthan and central India. Extreme heat suppresses travel demand — people simply stay indoors rather than heading to airports.

## The Market Share Shake-Up

IndiGo tightened its grip on Indian aviation, climbing to a 65% domestic market share in April — up 1.7 percentage points from March. The Air India Group, still deep in its Tata-led transformation and absorbing heavy restructuring costs, slipped below 25% for the first time in months, ending April at 24.7%.

Akasa Air, the Rakesh Jhunjhunwala-founded carrier that launched in 2022, has now firmly established itself as India's third-largest airline with a 5.8% share. SpiceJet, meanwhile, continued its slide to just 3.4%, posting an abysmal 31.2% on-time performance across major airports — meaning roughly seven out of ten SpiceJet flights were late.

For NRIs, the practical implication is straightforward: if you are connecting through a domestic flight to reach your hometown after landing in Delhi or Mumbai, IndiGo remains the most reliable option. Booking SpiceJet to save a few thousand rupees on the Delhi-Lucknow or Mumbai-Pune leg could cost you far more in missed connections and stress.

## What This Means for Summer Fares

The NRI summer travel window — June through August — typically sees strong demand on routes like SFO-DEL, JFK-BOM, ORD-HYD, and LAX-BLR. But this year, the supply-demand equation is shifting.

Airlines have already begun curtailing capacity for the lean months. Fewer flights on India routes means fewer seats, which normally pushes fares up. But the 39% drop in international passengers suggests demand is also weakening — potentially offsetting some of the fare pressure.

The wildcard is fuel. The Indian government's ATF price cap has shielded domestic passengers so far, but that subsidy may not be sustainable indefinitely. If global oil prices spike further due to an escalation in West Asia, airlines will have no choice but to pass costs to consumers through higher base fares and fuel surcharges — including on international routes that are not subject to the domestic price cap.

## The Silver Lining

India's aviation industry has a track record of resilience. Even when Jet Airways collapsed in 2019, total passenger numbers that year still exceeded the previous year's. The post-COVID recovery was faster than any industry body predicted. Every year since 2023 had recorded higher traffic than the one before — until now.

The industry is betting on the Diwali travel season and the winter wedding surge to make up lost ground. For NRIs, that means the best time to lock in summer fares may be now, before airlines recalibrate pricing for the back half of the year.

If you are flexible on dates, consider flying in September or early October instead of peak summer. Load factors are expected to be lower, airlines will be hungry for bookings, and the monsoon — which keeps many domestic tourists grounded — actually makes destinations like Kerala, Coorg, and the Western Ghats spectacularly beautiful."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
