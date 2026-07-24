#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-09 batch"""

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

# Validate images
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Wikimedia thumbs sometimes return 429 for HEAD but work for real browsers
        if "upload.wikimedia.org" in url:
            return True
    except:
        if "upload.wikimedia.org" in url:
            return True
    return False


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Made Facial Recognition Mandatory at Its Busiest Airports — and Every NRI Needs to Download This App Before Flying",
        "subheadline": "DigiYatra's biometric transit system is now compulsory for international passengers at Delhi, Mumbai, Bengaluru, and Hyderabad. The era of shuffling through documents at every checkpoint is officially over — but so is the option to skip it.",
        "slug": make_slug("digiyatra-biometric-mandatory-airports-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every NRI flying through India's four biggest airports must now use DigiYatra. No opt-out. If you haven't set up the app with Aadhaar verification before your trip, expect friction at the gate.",
        "tags": ["travel", "airports", "digiyatra", "biometric", "india-airports", "nri-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://travelandleisureasia.com/india/news/india-digiyatra-mandatory-airports/"},
            {"name": "TravTalk India", "url": "https://travtalkindia.com/digiyatra-mandatory-for-international-travellers/"},
            {"name": "The Mainstream", "url": "https://themainstream.co.in/digiyatra-biometric-transit-system-mandatory/"},
            {"name": "Gallivant", "url": "https://gallivant.co.in/digiyatra-mandatory-at-4-indian-airports/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Delhi_Airport_T3_Dep_Terminal_Entrance.jpg/1280px-Delhi_Airport_T3_Dep_Terminal_Entrance.jpg",
        "image_caption": "Terminal 3 departure entrance at Indira Gandhi International Airport, Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": """If you flew through Delhi, Mumbai, Bengaluru, or Hyderabad any time before June 2026, you know the routine: boarding pass out, passport out, boarding pass again, passport again, one more time at the gate. Repetitive, slow, and universally loathed.

That ritual is now dead. As of June 1, India's Ministry of Civil Aviation has made the DigiYatra biometric transit system **mandatory** for all international passengers at these four airports. Your face is now your boarding pass, your ID, and your security clearance — all in one scan.

## How It Actually Works

DigiYatra uses facial recognition to create a "digital identity token" tied to your travel profile. Passengers upload an Aadhaar-verified selfie and their boarding pass details through the DigiYatra app at least 48 hours before departure. At the airport, biometric e-gates scan your face at entry, security, and boarding — no documents required at any checkpoint.

The system has already processed over 10 crore domestic journeys since its initial rollout. Airlines including Air India and IndiGo have integrated their systems with the platform. The government plans to expand mandatory DigiYatra to 27 airports by 2027.

## What NRIs Need to Know — Right Now

Here's where it gets complicated for the diaspora. DigiYatra requires **Aadhaar verification**, which means you need a valid Aadhaar number linked to a working Indian mobile number. For NRIs who've let their Indian SIM lapse or never enrolled in Aadhaar, this creates a genuine logistical hurdle.

The process isn't difficult if you're prepared. Download the DigiYatra app (available on iOS and Android), complete the Aadhaar-selfie verification, and link your boarding pass. Do this before you leave for the airport — the system is designed for pre-registration, not last-minute setup at the terminal.

For those holding OCI cards or foreign passports, the implementation details remain somewhat murky. The current rollout is built around Aadhaar as the identity backbone, and the government hasn't published clear guidance for travelers who don't have one. If you're flying through these four airports on a foreign passport without Aadhaar, expect to encounter the older manual processing lanes — but expect those lanes to get longer as the biometric gates become the default.

## The Privacy Question Nobody's Asking

India's data protection advocates have raised concerns about DigiYatra since its inception. The Digi Yatra Foundation — the non-profit body running the system — has claimed that facial biometrics are stored only on the passenger's device and deleted from airport servers within 24 hours of departure. But the system has been exempted from Right to Information Act requests, making independent verification difficult.

For NRIs accustomed to the TSA PreCheck or Global Entry model in the US, DigiYatra operates on a fundamentally different principle. Those programs are voluntary conveniences. DigiYatra, at these four airports, is now the default — and the only way through the international transit corridor.

## Practical Steps Before Your Next India Trip

The window for gradual adoption is closed. If you're flying through Delhi, Mumbai, Bengaluru, or Hyderabad this summer — and millions of NRIs will be — treat DigiYatra setup as a pre-trip essential, alongside visa checks and travel insurance.

Ensure your Aadhaar is active and linked to a reachable phone number. Download the app well before your departure date. And if you're traveling with elderly parents who've never touched a smartphone app, budget time to set them up before they reach the airport.

The age of paper-shuffling at Indian airports is ending. Whether that's progress or overreach depends on who you ask. But it's no longer optional."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Modi Told Indians to Stop Traveling Abroad — and Global Hotel Chains Are Betting Billions That They'll Listen",
        "subheadline": "Hotel investments in India surged 67% last year to $567 million. Room rates are up 25%. The country's domestic tourism market is heading for $216 billion. For NRIs visiting home, the hotel experience is transforming — but the bill is too.",
        "slug": make_slug("modi-domestic-travel-push-hotel-boom-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "India's hotel boom means NRIs visiting home will find dramatically better accommodation — but at prices that increasingly rival Western destinations. With Modi urging domestic travel and the Iran war pushing up international fares, the economics of flying home are shifting fast.",
        "tags": ["travel", "hotels", "india-tourism", "modi", "hospitality", "nri-travel", "domestic-tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine / Bloomberg", "url": "https://www.thehindubusinessline.com/economy/hotel-giants-bet-indias-local-travel-boom-can-defy-slowdown/article69670456.ece"},
            {"name": "JLL India", "url": "https://www.jll.co.in/"},
            {"name": "World Travel & Tourism Council", "url": "https://wttc.org/"},
            {"name": "Kotak Securities", "url": "https://www.thehindubusinessline.com/markets/hospitality-demand-to-rebound/article69657879.ece"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Shot_of_The_Taj_Mahal_Palace_Hotel.jpg/1280px-Shot_of_The_Taj_Mahal_Palace_Hotel.jpg",
        "image_caption": "The Taj Mahal Palace Hotel in Mumbai, an icon of India's luxury hospitality sector",
        "image_attribution": "Wikimedia Commons",
        "body": """Last month, Prime Minister Narendra Modi made a request that sounded more like a directive: Indians should limit non-essential overseas travel for at least a year and vacation within the country instead. He framed it as economic patriotism — a way to keep rupees from flowing into foreign currencies at a time when the currency is under pressure.

The hotel industry heard him loud and clear. Not as a patriotic plea, but as a profit signal.

## The Numbers Behind the Boom

Hotel investments in India surged **67% to $567 million** in 2025, according to JLL. The country's domestic travel and tourism market is projected to hit **$216 billion** this year, up nearly 8% from 2025, per World Travel & Tourism Council data. Demand for hotel rooms is forecast to rise about 11% annually over the next several years, comfortably outpacing supply.

The gap between supply and demand is staggering. India has roughly **one hotel room for every 3,000 people**, compared with one for every 60 in the United States, according to Hilton's own calculations. That ratio explains why global chains — Hilton, Marriott, ITC, IHCL — are rushing to plant flags across the country, from Goa's beaches to Kashmir's mountains to pilgrimage circuits that draw millions annually.

Room rates have already responded. Hotel rates have risen as much as **25% in popular destinations** across the country this summer, according to the Indian Association of Tour Operators. Airfares, local transportation, and restaurant prices have all climbed in tandem.

## The Iran War Factor

Modi's domestic travel push coincides with a geopolitical squeeze that's making international travel more expensive anyway. The ongoing Iran conflict has pushed up oil prices, forced airlines to reroute around closed Middle Eastern airspace, and sent jet fuel costs spiraling. IATA has slashed its 2026 airline profit forecast nearly in half — from $41 billion to $23 billion — and those costs are landing squarely on passengers.

For Indians who traditionally routed through Dubai, Abu Dhabi, or Doha to reach Europe or Southeast Asia, the Gulf hub model is under unprecedented strain. Emirates, Qatar Airways, and Etihad face the greatest operational uncertainty, and reduced Gulf connectivity is pushing international fares higher across the board.

The practical result: a family trip to Thailand or Europe from India costs significantly more than it did 18 months ago. A domestic trip to Rajasthan or Kerala, by contrast, is suddenly the path of least resistance — exactly as the government intended.

## What This Means for NRIs

For the 14 million-plus overseas Indians who visit home regularly, this hotel transformation cuts both ways.

The good news is genuine. India's hotel stock is undergoing its most significant upgrade in a generation. New properties from international chains are raising the baseline of what a mid-range hotel experience looks like. The days of settling for tired business hotels with unreliable Wi-Fi and mystery breakfast buffets are receding — at least in major metros and popular tourist destinations.

The bad news is the price tag. NRIs who remember ₹3,000-a-night hotels in Goa or Jaipur are encountering ₹8,000-12,000 rates at comparable properties during peak season. The combination of rising demand, limited supply, and a weaker rupee (which makes dollar-denominated travelers feel richer but doesn't offset the rate hikes) means the "India is cheap" assumption needs recalibrating.

## Where the Smart Money Is Going

The biggest bets are being placed on three segments: **religious and spiritual tourism**, which has emerged as the fastest-growing category; **premium leisure destinations** like Goa, Kashmir, and wildlife reserves, where demand has climbed 20% for summer 2026; and **tier-two cities** that are benefiting from new airports, better highways, and Modi's infrastructure push.

EaseMyTrip founder Nishant Pitti argues that Modi's appeal will "further encourage travelers to rediscover domestic tourism, which is already witnessing sustained growth backed by strong infrastructure development." The India hotel story isn't a bubble — it's a structural correction of decades of underinvestment meeting a population that's finally wealthy enough to travel domestically in serious numbers.

## The Bottom Line for Your Next Trip Home

If you're planning a summer or fall trip to India, book accommodation early. The combination of Modi's domestic travel push, Gulf route disruptions making international trips expensive for Indians, and a genuine hotel supply shortage means popular destinations will be tighter than usual.

The upside: when you do book, you'll likely find a noticeably better room than the last time you visited. The Indian hotel experience is finally catching up to the country's ambitions. Just don't expect the prices to stay where they were."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
