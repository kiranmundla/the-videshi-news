#!/usr/bin/env python3
"""Travel writer – 2026-06-29 batch. Two articles for The Videshi travel section."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ──────────────────────────────────────────────────────────────────
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


# ── articles ─────────────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: Air India Easy Connect ─────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's 'Easy Connect' Lets Your Parents Fly Abroad from Varanasi Without Touching Delhi Immigration",
        "subheadline": "India's first hub-and-spoke service cleared immigration at the hometown airport on Day One — and eleven more cities are next.",
        "slug": make_slug("air-india-easy-connect-hub-spoke-varanasi-nri"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "NRIs whose families live in Tier-2 cities like Varanasi, Guwahati, or Kochi will no longer need to coach elderly parents through the chaos of a Delhi or Mumbai international terminal — immigration and baggage are handled at the hometown airport.",
        "tags": ["travel", "airlines", "air-india", "airports", "easy-connect", "hub-spoke"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/manage/easy-connect.html"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-launches-easy-connect-service/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-launch-hub-and-spoke-international-connectivity-flights-from-june-25/article69660447.ece"},
            {"name": "Madhyamam Online", "url": "https://english.madhyamamonline.com/india/2026/june/26/india-launches-hub-and-spoke-model-to-simplify-international-travel"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/95/The_facade_of_Varanasi_Airport%2C_Varanasi.jpg",
        "image_caption": "The facade of Lal Bahadur Shastri International Airport in Varanasi, where Air India's first Easy Connect flight departed",
        "image_attribution": "Wikimedia Commons",
        "body": """Anyone who has helped a parent or grandparent navigate an Indian hub airport for an international connection knows the drill: reclaim bags at Delhi, drag them to a different terminal, queue for immigration, queue again for security, and pray the connecting gate hasn't changed. Multiply the stress by jet lag and a wheelchair, and you have a recipe for cancelled trips.

Air India's new "Easy Connect" service, which took its maiden flight from Varanasi on June 25, is designed to end that ordeal. Under the government's hub-and-spoke framework, passengers departing from smaller cities now complete international immigration and check their bags through to their final overseas destination — all before they board the domestic leg to the hub.

## How It Works

The mechanics are straightforward. A traveller in Varanasi books a single itinerary — say, Varanasi to London via Delhi. At Lal Bahadur Shastri International Airport, they check in once, drop their bags (which are tagged straight through to Heathrow), and clear immigration at a dedicated counter. The domestic flight to Delhi operates as a normal Air India service, but on arrival the passenger is channelled through international transfer e-gates, skipping Delhi's immigration halls entirely. Checked baggage transfers automatically.

The first Easy Connect flight, AI 1111, carried 180 passengers and departed at 9:23 AM on June 25. From Delhi, onward connections currently reach Dubai, Colombo, Jeddah, Riyadh, Kathmandu, and Phuket — with London, Singapore, and other long-haul routes available through the same booking flow.

## Eleven Cities Are Next

Varanasi is only the beginning. Air India has confirmed that eleven more cities will be integrated into the Easy Connect network: Ahmedabad, Amritsar, Chennai, Goa, Guwahati, Hyderabad, Kochi, Mumbai, Patna, Vadodara, and Visakhapatnam. Civil Aviation Minister Ram Mohan Naidu said six of those will go live within six weeks. Each spoke will feed into hubs at Delhi, Mumbai, and Bengaluru, forming a multi-hub system rather than funnelling everything through a single chokepoint.

The expansion list reads like a map of diaspora roots. Hyderabad to San Francisco via Bengaluru. Kochi to London via Mumbai. Guwahati to Dubai via Delhi. For families in these cities, the difference between a single-booking journey with one immigration check and the current multi-booking, multi-queue gauntlet is enormous.

## Why NRIs Should Care

The practical impact is less about the traveller flying in from the US and more about the family flying out. The roughly 18 million members of the Indian diaspora in the US, UK, Canada, and the Gulf frequently arrange trips for parents, in-laws, and extended family — many of whom are elderly, travelling alone, and unfamiliar with the controlled chaos of Delhi T3 or Mumbai T2. Easy Connect turns a two-stage ordeal into a single, supervised journey from the hometown airport counter to the final destination.

There is a broader strategic play, too. India currently loses an estimated 60 to 70 per cent of its international connecting traffic to Gulf hubs like Dubai, Abu Dhabi, and Doha. Passengers from Varanasi or Guwahati headed to Europe would typically transit through the Middle East because Indian airports offered no seamless domestic-to-international transfer. Easy Connect is an attempt to claw that traffic back.

## Caveats Worth Noting

The system has a few gaps. There is no customs declaration facility at spoke airports — if a passenger is carrying high-value or dutiable goods, Air India recommends rebooking on an alternate (non-Easy Connect) flight. And while the single-booking system works end-to-end, travellers still need to collect a physical boarding pass at the origin counter; mobile boarding passes are not yet supported for Easy Connect itineraries.

The real test will come at scale. Processing immigration for Varanasi's relatively modest passenger volumes is one thing. Doing it at Hyderabad or Chennai, which handle millions of international passengers annually, will require significant infrastructure and staffing. But the concept is sound, the first flight has flown, and for any NRI who has spent a long-distance phone call talking a worried parent through Terminal 3, this cannot come soon enough.

*Air India's Easy Connect flights can be booked on airindia.com, the Air India mobile app, and through authorised travel agents.*"""
    },

    # ── ARTICLE 2: Navi Mumbai goes international ────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Navi Mumbai's Airport Goes International on July 15 — and the Route Is Abu Dhabi",
        "subheadline": "Air India Express will operate the first overseas departure from Mumbai's second airport, giving the eastern suburbs and Thane a UAE gateway without the Chhatrapati Shivaji crawl.",
        "slug": make_slug("navi-mumbai-airport-international-abu-dhabi-air-india-express"),
        "category": "travel",
        "vertical": "travel",
        "is_editorial": False,
        "diaspora_angle": "NRIs from Navi Mumbai, Thane, and Panvel who connect through Abu Dhabi to reach the US or UK can now skip the often punishing drive to Mumbai's main airport — a second international gateway changes the math on every India trip.",
        "tags": ["travel", "airlines", "airports", "navi-mumbai", "air-india-express", "abu-dhabi", "uae"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Press Trust of India (via Nordot)", "url": "https://nordot.app/1306919085693739072"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-express-launches-navi-mumbai-abu-dhabi-flights-from-july-15/article69703063.ece"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/air-india-express-navi-mumbai-abu-dhabi/"},
            {"name": "AirlineStat", "url": "https://airlinestat.it/articles/navi-mumbai-air-india-express-abu-dhabi-international-debut"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "Navi Mumbai International Airport terminal, which will handle its first international departure on July 15",
        "image_attribution": "Wikimedia Commons",
        "body": """Six months after its first domestic flight rolled down the runway on Christmas Day 2025, Navi Mumbai International Airport is crossing a bigger threshold. On July 15, Air India Express flight IX 207 will depart at 2:55 AM for Abu Dhabi, making it the first international passenger service from Mumbai's greenfield second airport.

Bookings opened on June 21. The initial schedule is modest — two weekly flights on Wednesdays and Fridays — stepping up to three per week from July 29 with a Sunday addition. But the symbolism runs well ahead of the frequency count. International flights mean customs, immigration, and cargo infrastructure are live, and other carriers are expected to follow.

## What It Means for Mumbai's Eastern Half

Anyone who has taken a cab from Vashi, Panvel, or Thane to Chhatrapati Shivaji Maharaj International Airport during rush hour knows the journey can take ninety minutes on a good day. Navi Mumbai's airport, located in Jewar-adjacent Ulwe, flips the geography. For the roughly eight million residents of the eastern suburbs, Navi Mumbai, and the Konkan corridor, it cuts airport access time sharply.

The Abu Dhabi link matters because it is not just a point-to-point route. Etihad's Abu Dhabi hub offers connections to over 45 destinations, including multiple US gateways (New York JFK, Washington IAD, Chicago, Charlotte) and European cities. For NRIs routing through the Gulf to visit family in Navi Mumbai, Thane, or Pune, the new airport eliminates the worst part of the trip — the grind across Mumbai to reach the international terminal.

## The Numbers So Far

Navi Mumbai International Airport currently handles about 149 daily flights connecting 46 domestic destinations and processes around 20,000 passengers per day. The Adani Group, which operates the airport with a 74 per cent stake (CIDCO holds the remaining 26 per cent), has projected 300 daily flights by the winter schedule. IndiGo is the dominant domestic carrier with routes to over 40 cities, followed by Akasa Air serving eight destinations.

The airport's first phase can handle 12 million passengers annually. When fully built out — five runways, multiple terminals — capacity is projected at 225 million, which would make it one of the largest airports in the world. That is decades away, but the ambition explains why international clearance from Day One was a priority.

## Freight Comes Too

The July 15 milestone is not just about passengers. Navi Mumbai airport CEO BVJK Sharma confirmed that freighter operations will also launch on the same date, with a target of 18 weekly freight flights. For a metropolitan region whose economy runs on trade, finance, and manufacturing, cargo connectivity is arguably as important as passenger service. The airport's proximity to JNPT (Jawaharlal Nehru Port Trust), India's largest container port, adds a logistics dimension that Mumbai's main airport cannot easily replicate.

## What NRIs Should Watch

The immediate question is how quickly other international routes follow. Abu Dhabi is the opening act, but the routes that will matter most to the diaspora are direct Gulf connections to Dubai, Jeddah, and Muscat — the high-traffic corridors that serve millions of Indian expatriates. Beyond the Gulf, IndiGo and Akasa Air are both expanding at Navi Mumbai and could add international services once they secure the necessary bilateral slots.

For now, the practical advice is simple: if you are routing through Abu Dhabi on your next India trip and your family is anywhere east of the Thane Creek, check Navi Mumbai. The airport is new, the terminal is uncrowded, and the drive from Panvel is twenty minutes. Compared to the alternative, that alone might be worth the booking.

*Air India Express Navi Mumbai–Abu Dhabi flights are available on airindiaexpress.com and major OTA platforms. Fares start at approximately ₹12,000 one way.*"""
    },
]

# ── insert ───────────────────────────────────────────────────────────────
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
