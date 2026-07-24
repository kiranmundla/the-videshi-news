#!/usr/bin/env python3
"""Travel writer — 2026-06-07 22:00 UTC run."""

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

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    # ── Article 1: Air India Mumbai–Tokyo Haneda Nonstop ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Launches Mumbai–Tokyo Nonstop Next Week — and Western India Finally Gets a Direct Line to Japan",
        "subheadline": "Four weekly flights from June 15 give Mumbaikars and NRIs a direct path to Haneda, just 18 km from central Tokyo — no more routing through Delhi or connecting through Southeast Asia.",
        "slug": make_slug("air-india-mumbai-tokyo-haneda-nonstop-june"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs in western India and the Gulf no longer need to route through Delhi for Japan trips. The Mumbai-Tokyo nonstop slashes transit for the large Maharashtrian and Gujarati diaspora who travel via Mumbai, and opens a direct corridor for the growing India-Japan business community.",
        "tags": ["travel", "airlines", "air-india", "japan", "mumbai", "tokyo"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "BrightSun Travel", "url": "https://www.brightsun.co.in/travelblog/air-india-expands-connectivity-with-new-routes-for-2026"},
            {"name": "Travel Daily Media", "url": "https://www.traveldailymedia.com/air-india-to-operate-daily-flights-to-tokyo-haneda/"},
            {"name": "Air India Official", "url": "https://www.airindia.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/55/Air_India%2C_VT-ANP%2C_Boeing_787-8_Dreamliner.jpg",
        "image_caption": "An Air India Boeing 787-8 Dreamliner on the tarmac",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India will begin nonstop service between Mumbai and Tokyo Haneda on June 15, operating four flights per week on its widebody fleet. It is the airline's first direct connection between western India and Japan — and for the tens of thousands of NRIs who route their India trips through Mumbai, it removes a connection that has long made Japan feel further away than it actually is.

## What's on Offer

The new route supplements Air India's existing Delhi–Tokyo Haneda service, which moved from Narita to the city-centre airport in March 2025 and went daily last June. Mumbai–Haneda will operate four times weekly, putting Japan's capital within a single flight of India's financial hub.

Haneda sits just 18 kilometres from central Tokyo, with a monorail link to Tokyo Station that takes roughly 30 minutes. For travellers accustomed to the hour-long journey from Narita, that alone changes the calculus of a Japan trip.

Through Air India's deepened codeshare with Star Alliance partner All Nippon Airways, passengers booking through Mumbai can connect onward from Tokyo to six Japanese cities — Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka, and Sapporo — on a single ticket with baggage checked through.

## Why NRIs Should Pay Attention

Until now, flying Mumbai to Tokyo meant routing through Delhi, Singapore, Bangkok, or a Gulf hub — each adding five to ten hours and a layover. For the large Maharashtrian and Gujarati diaspora in the US who fly home through Mumbai, a Japan side trip meant backtracking through Delhi or booking a separate itinerary entirely.

The direct link matters beyond leisure. India-Japan bilateral trade crossed $22 billion in 2025, and Mumbai is home to the country's largest concentration of Japanese corporate offices outside Delhi. Japanese investment in India's infrastructure — from the Mumbai-Ahmedabad bullet train to Suzuki's manufacturing corridor — has deepened the business travel corridor between the two countries.

For NRI families planning summer travel, the timing is deliberate. Japan's tourism infrastructure has expanded aggressively since it lifted Covid-era entry restrictions, and the weak yen continues to make it one of Asia's best-value luxury destinations. A family of four can eat world-class ramen for under $30 and stay in a ryokan for less than a midrange hotel in Goa.

## The Bigger Air India Picture

The Mumbai–Tokyo route is part of a broader 2026 expansion. Air India launched Delhi–Rome with four weekly flights in March, will extend London Heathrow–Bengaluru service on the Airbus A350-900 from August 1, and already operates 52 weekly flights between India and Singapore. The airline added Delhi–Shanghai service in February after a six-year hiatus, and now connects to Hanoi five times a week alongside daily Ho Chi Minh City flights.

The Maharaja Lounge at Delhi's Terminal 3 — a 16,000-square-foot premium facility with sleep suites, a runway-view bar, and dedicated first-class sections — is part of the airline's broader rebrand under Tata Group ownership.

## What It Costs

Current one-way fares on the Mumbai–Tokyo Haneda route are listed from approximately ₹35,000 ($415) in economy, though introductory pricing may shift as bookings fill. Round-trip fares from Mumbai via Air India's codeshare with ANA to secondary Japanese cities like Osaka start around ₹75,000 ($890).

NRIs in the US considering a Japan stopover en route to Mumbai should compare this against routing through a Gulf carrier. Emirates and Qatar still offer competitive Mumbai connections via Dubai and Doha, but neither offers the one-ticket, checked-bag convenience of the Air India–ANA codeshare from Haneda to Japanese cities.

Bookings are live on airindia.com and through major OTAs. Flights begin June 15."""
    },
    # ── Article 2: Delhi–Siliguri Bullet Train Corridor ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Second Bullet Train Will Link Delhi to Siliguri in Six Hours — Opening a High-Speed Gateway to the Northeast",
        "subheadline": "Railway Minister Ashwini Vaishnaw's announcement of a new corridor through Lucknow, Varanasi, and Patna cuts a 20-hour journey to six and signals serious investment in a region the diaspora has long found hard to reach.",
        "slug": make_slug("delhi-siliguri-bullet-train-corridor-northeast"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of NRIs with roots in UP, Bihar, and Bengal — three of the largest source states for the US Indian diaspora — could see their journey home cut from 20+ hours to 6 hours from Delhi. The corridor also unlocks Darjeeling, Sikkim, and the Northeast as practical destinations for NRI family trips.",
        "tags": ["travel", "india", "railways", "bullet-train", "infrastructure", "northeast-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indulge Express", "url": "https://www.indulgexpress.com/travel/2026/Jun/07/west-bengals-first-bullet-train-to-link-delhi-to-siliguri-via-lucknow-varanasi-and-patna"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/in-a-historic-first-vande-bharat-express-runs-directly-from-jammu-to-srinagar/"},
            {"name": "Indian Railways", "url": "https://indianrailways.gov.in"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
        "image_caption": "A Vande Bharat Express on India's modernising rail network",
        "image_attribution": "Wikimedia Commons",
        "body": """Railway Minister Ashwini Vaishnaw has announced a Delhi–Siliguri high-speed rail corridor — India's second bullet train project after the Mumbai-Ahmedabad line. The proposed route would cut travel time between the national capital and North Bengal's gateway city from roughly 20 hours to just six, with stops at Lucknow, Varanasi, and Patna.

The announcement, made during a high-level railway review on June 6, signals a decisive tilt in India's rail infrastructure strategy toward the north and east — regions that have historically been underserved by premium connectivity and are home to some of the largest source communities of the Indian American diaspora.

## The Route and What It Changes

The corridor follows a path through four of India's most consequential cities for the diaspora. Lucknow, the capital of Uttar Pradesh, is the administrative heart of India's most populous state. Varanasi is its spiritual epicentre. Patna anchors Bihar, which sends more students to US universities than most Indian states. And Siliguri is the funnel through which all traffic to Darjeeling, Sikkim, and India's northeastern states passes.

Today, the fastest train from Delhi to New Jalpaiguri (Siliguri's main station) takes 19-21 hours. Most NRIs with roots in this belt either fly — limited options, often with connections through Kolkata or Guwahati — or endure the overnight rail journey that their parents took decades ago. A six-hour bullet train changes the arithmetic entirely.

The corridor also connects to the Jammu-Srinagar Vande Bharat service that launched in April 2026, the first direct rail link to the Kashmir Valley. Together, these projects represent a shift from India's historical rail investment pattern, which favoured the western and southern corridors that carried freight and business traffic, toward the northern and eastern routes that carry people.

## Why This Matters to the Diaspora

Uttar Pradesh, Bihar, and West Bengal collectively account for an estimated 1.5 to 2 million Indian Americans. For this community, trips home typically mean flying into Delhi or Kolkata and then facing a domestic connection or an overnight train to their family's town. The Delhi-Varanasi leg alone — one of the busiest rail corridors in India — currently takes 8-12 hours by conventional train.

A bullet train that covers Delhi to Varanasi in roughly two hours and Delhi to Patna in about three would fundamentally reshape how NRIs plan their India trips. A visit to the ancestral village in eastern UP or north Bihar could become a day trip from Delhi rather than a logistical ordeal requiring a separate flight booking and an overnight stay.

Siliguri, at the corridor's eastern end, is the gateway to destinations that NRI families have historically found difficult to access: Darjeeling's tea estates, Sikkim's monasteries, and the wildlife reserves of Dooars. With a six-hour train from Delhi, these become viable additions to a two-week India trip rather than standalone expeditions.

## The Investment Behind It

West Bengal's railway allocation has risen from ₹4,000 crore to ₹14,205 crore, a more than threefold increase that reflects the state's growing weight in India's infrastructure plans. Kolkata now has 45 km of operational metro rail, with 60 new metro trains on order.

The Delhi-Siliguri corridor follows the completion of the Mumbai-Ahmedabad bullet train — India's first, built with Japanese Shinkansen technology and operational since late 2025. That project's success appears to have accelerated the government's appetite for high-speed rail, with the northern corridor being the first to receive an explicit ministerial endorsement since Mumbai-Ahmedabad.

No timeline or budget has been announced for the Delhi-Siliguri project, and infrastructure observers caution that Indian mega-projects often face land acquisition delays and cost overruns. The Mumbai-Ahmedabad bullet train itself took years longer than originally projected. But the political signalling is unmistakable: the government is betting that high-speed rail can do for India's north and east what the expressway and airport expansion programme did for the west and south.

## What to Watch

For NRIs planning trips home through Delhi, the practical takeaway is forward-looking but significant. The corridor won't be operational for years, but the announcement shifts the long-term calculus of where in India premium connectivity is headed. In the near term, the existing Vande Bharat services — running at 160 km/h on conventional track — continue to expand. Thirteen routes are now operational, with the Bengaluru-Mangaluru and Jammu-Srinagar services among the most recent additions.

For those with roots along the Delhi-Patna-Siliguri belt, this is worth watching. India's rail network is being rebuilt around speed, and for the first time, the north-east corridor is near the front of the queue."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
