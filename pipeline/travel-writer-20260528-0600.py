#!/usr/bin/env python3
"""Travel writer — 2026-05-28 06:00 UTC run. Publishes 2 articles."""

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

# --------------------------------------------------------------------------
# ARTICLE 1: Hong Kong Terminal 2
# --------------------------------------------------------------------------

hk_body = """Hong Kong International Airport's brand-new Terminal 2 opened its doors to passengers on May 27, marking the first phase of a HK$141.5 billion ($14.5 billion) expansion that the city hopes will claw back ground lost to Singapore Changi and Dubai International during the pandemic years. For the millions of Indian Americans who route through Hong Kong on their way to the subcontinent, the timing is significant — and so is the airline list.

## IndiGo Moves to T2 on June 2

Fifteen airlines are migrating from Terminal 1 to the new facility over the next two weeks. Among them: IndiGo, India's largest carrier by market share, which shifts its check-in operations to T2 on June 2. HK Express, Hong Kong Airlines, AirAsia, Greater Bay Airlines, Cebu Pacific, Hainan Airlines, Jeju Air, Bangkok Airways, Batik Air, Thai Lion Air, Air Cambodia, VietJet Air, and Thai AirAsia round out the roster.

For NRIs, IndiGo's presence in T2 matters because the airline operates direct Hong Kong–India routes connecting to Delhi, Mumbai, and Bengaluru. Passengers on these flights will now check in at the new terminal's self-service kiosks and biometric e-Security Gates before taking the Automated People Mover (APM) to their boarding gate in Terminal 1 — arrival facilities at T2 won't open until 2027.

## What's Actually Different

The numbers: 300,000 square metres of floor space, 230 check-in counters across eight aisles, and e-Security Gates that use facial recognition to replace manual passport stamping. Hong Kong's Airport Authority claims a 25 per cent reduction in processing time compared to T1's existing security lanes. Passengers can keep laptops and sub-100ml liquids in their bags through the new CT scanners — a small mercy for anyone who's sprinted through a Hong Kong connection with 55 minutes on the clock.

Dining runs from local cha chaan teng chain Milk Cafe and TamJai SamGor noodles to Luckin Coffee and Jollibee. It's decidedly mid-range rather than luxury, reflecting T2's design brief as a leisure and budget-carrier terminal.

The MTR Airport Express has added a new T2 platform — exit right from the city, left from AsiaWorld-Expo. 'A' buses now stop at T2 directly. Car Park 3 connects to the terminal for those driving.

## Why NRIs Should Pay Attention

Hong Kong has quietly become one of the most important transit hubs for Indian travellers. Cathay Pacific, which remains in T1, operates some of the most competitive one-stop fares between the US West Coast and India. Singapore Airlines and Emirates dominate the conversation, but Cathay's SFO–HKG–DEL and LAX–HKG–BOM routings consistently undercut rivals by $200–400 on premium economy.

The T2 expansion is Hong Kong's answer to Changi's Terminal 5 (under construction) and Dubai's Al Maktoum expansion. For the airport authority, the bet is that better infrastructure will attract more low-cost and regional carriers to feed into Cathay's long-haul network — which means more connection options and lower fares for price-sensitive NRI families booking summer trips to India.

The practical impact won't be immediate. Until 2027, T2 passengers still board at T1 gates, adding an APM ride to the journey. And the terminal's focus on budget carriers means Cathay Pacific and Singapore Airlines passengers won't notice a difference yet. But the 100-million-passenger annual capacity target signals that Hong Kong is playing the long game — and NRIs who've been routing through Dubai or Doha might want to watch the fare screens more carefully.

**One caveat**: The APM doesn't run between 12:31 AM and 5:59 AM. Red-eye passengers checking in during those hours should head to T1 security directly via the pedestrian link bridge."""

hk_sources = json.dumps([
    {"name": "Hong Kong Airport Authority", "url": "https://www.hongkongairport.com"},
    {"name": "Lifestyle Asia", "url": "https://www.lifestyleasia.com/hk/whats-on/news-whats-on/hong-kong-international-airport-terminal-2-t2/"},
    {"name": "Wego Travel Blog", "url": "https://blog.wego.com/hong-kong-airport-terminal-2/"},
    {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/05/27/hong-kong-opens-new-terminal-2/"}
])

# --------------------------------------------------------------------------
# ARTICLE 2: Vande Bharat Sleeper Mumbai–Bengaluru
# --------------------------------------------------------------------------

vb_body = """India's Railway Ministry has approved the launch of a Vande Bharat Sleeper service between Mumbai and Bengaluru, bringing semi-high-speed overnight rail to one of the country's busiest corridors. The approval, confirmed by Railway Minister Ashwini Vaishnaw in April 2026, makes it the second sleeper route after the Howrah–Kamakhya service that launched in January — and for the estimated 800,000 Kannadigas and Maharashtrians in the American diaspora, it changes the calculus of the India trip.

## The Route That Needed Fixing

The current workhorse on this corridor is the Udyan Express, a train that takes over 20 hours to cover roughly 800 kilometres and routinely runs late. Flights between Mumbai and Bengaluru are frequent but expensive during peak season — ₹8,000–15,000 one-way in summer and Diwali windows — and the fuel-price-driven domestic cuts announced this month by Air India (22 per cent) and IndiGo (5–7 per cent) will only tighten supply further.

The Vande Bharat Sleeper promises to split the difference: faster than the Udyan Express by several hours (exact timings are pending), air-conditioned berths designed for overnight comfort, onboard Wi-Fi, entertainment options, and catering that Indian Railways describes as "premium flight-equivalent." Fares haven't been announced, but the Howrah–Kamakhya sleeper launched at roughly 20–30 per cent above Rajdhani pricing — still a fraction of last-minute airfares.

## Twelve Sleeper Trains by December

The Mumbai–Bengaluru service is part of a broader push: Vaishnaw's office has committed to deploying 12 Vande Bharat Sleeper trains across the country by December 2026. The fleet is being manufactured by BEML, Kinet Railway Solutions, and Titagarh Rail Systems, all domestic producers — a deliberate move to build the industrial base for what Railways envisions as a nationwide semi-high-speed sleeper network by 2030.

The Howrah–Kamakhya launch in January offered the first real data point. Early reviews praised the berth spacing (wider than Rajdhani 3AC), the ride quality (less lateral sway at speed), and the charging infrastructure (every berth has USB-C and standard outlets). Complaints centred on catering quality and the lack of a pantry car — issues Railway officials say they're addressing for subsequent deployments.

## Why This Matters to NRIs

Every NRI who's visited India knows the two-city problem. You fly into Mumbai to see one set of relatives, then need to get to Bengaluru (or Hyderabad, or Chennai) for the other half of the family. Domestic flights during wedding season or Diwali are brutally priced and frequently disrupted. The Rajdhani and Shatabdi fleet, while adequate, is aging.

The Vande Bharat Sleeper directly addresses this gap. Board after dinner in Mumbai, sleep in a modern berth, arrive in Bengaluru by morning. No airport security theatre, no checked-bag anxiety, no 4 AM Uber to the domestic terminal. For families with elderly parents or young children, the overnight train is already the preferred mode — the Vande Bharat Sleeper simply makes it less of a compromise.

There's a broader infrastructure story too. The Indian government has poured money into rail modernisation since 2019 — the Vande Bharat fleet now exceeds 164 services carrying 75 million passengers since launch. The sleeper variant extends that investment to the overnight segment, which had been largely ignored in favour of daytime semi-high-speed runs.

## What to Watch

Launch dates, fare structures, and booking windows haven't been finalised. Given the pattern with earlier Vande Bharat rollouts, expect announcements 4–6 weeks before the first commercial run. NRIs planning winter trips to India — Diwali falls on October 20 this year — should keep an eye on the IRCTC portal for early booking access.

The bigger question is whether the sleeper network expands to the routes NRIs care about most: Delhi–Jaipur, Mumbai–Goa, Chennai–Bengaluru, and the golden triangle corridor. If the Mumbai–Bengaluru service performs well, those routes are likely next. Indian Railways is, for the first time in decades, building trains that people actually want to ride."""

vb_sources = json.dumps([
    {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/indias-new-vande-bharat-sleeper-train-set-to-revolutionize-overnight-travel-between-bengaluru-and-mumbai-faster-comfortable-and-affordable-rail-journey-approved/"},
    {"name": "Railway Supply", "url": "https://railway.supply/en/vande-bharat-express-network-upgrades-and-sleeper-launch/"},
    {"name": "The CSR Journal", "url": "https://thecsrjournal.in/indias-first-vande-bharat-sleeper-train-set-to-run-from-january/"}
])

# --------------------------------------------------------------------------
# Assemble articles
# --------------------------------------------------------------------------

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Hong Kong Just Opened a $14.5 Billion Terminal — and IndiGo Is Moving In",
        "subheadline": "Terminal 2 at HKIA launched May 27 with biometric gates and 25% faster processing. Fifteen airlines are shifting over, including India's largest carrier, reshaping a key NRI transit hub.",
        "slug": make_slug("hong-kong-terminal-2-indigo-nri-transit"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Hong Kong is a critical transit hub for NRIs flying between the US West Coast and India. IndiGo's move to T2 and the terminal's capacity expansion could bring more routing options and competitive fares on key diaspora corridors.",
        "tags": ["travel", "airlines", "airports", "hong-kong", "indigo"],
        "urgency": "medium",
        "sources": hk_sources,
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36860208/pexels-photo-36860208.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern airport terminal interior — Hong Kong's new T2 features biometric e-Security Gates and 230 check-in counters",
        "body": hk_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Vande Bharat Sleeper Is Coming to Mumbai–Bengaluru — and It Solves the NRI's Two-City Problem",
        "subheadline": "The Railway Ministry has approved overnight semi-high-speed rail between India's two biggest economic hubs. Twelve sleeper trains are slated for deployment by December 2026.",
        "slug": make_slug("vande-bharat-sleeper-mumbai-bengaluru-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India routinely need to travel between Mumbai and Bengaluru to see different branches of family. An overnight Vande Bharat Sleeper eliminates the need for expensive domestic flights or 20-hour legacy trains.",
        "tags": ["travel", "indian-railways", "vande-bharat", "infrastructure"],
        "urgency": "medium",
        "sources": vb_sources,
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express near Mumbai — the sleeper variant will bring overnight semi-high-speed rail to the Mumbai–Bengaluru corridor",
        "body": vb_body,
    },
]

# --------------------------------------------------------------------------
# Publish
# --------------------------------------------------------------------------

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
