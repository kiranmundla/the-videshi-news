#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-05-30 10:00 UTC run."""

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

# ============================================================
# ARTICLE 1: Air India's 2026 Route Explosion
# ============================================================

article1_body = """Air India is in the middle of the most aggressive route expansion in its history, and the timing could not be better for the four million Indian Americans who fly the India corridor every year.

## Mumbai to Tokyo, Nonstop

The headline route lands on June 15: four weekly nonstop flights from Mumbai to Tokyo Haneda, operated as AI 356 on an Airbus A350. Departing at 4:50 PM from Chhatrapati Shivaji, arriving 4:55 AM at Haneda — which is 18 kilometres from central Tokyo, compared to Narita's 60. Through Air India's expanded codeshare with Star Alliance partner All Nippon Airways, passengers can connect onward to Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka, and Sapporo on a single ticket with bags checked through.

For the 200,000-plus Indian Americans in the tristate area and Bay Area who've been routing through Singapore or Bangkok to reach Tokyo, this is a direct improvement. Mumbai-Haneda also opens a practical option for NRIs visiting family in western India who want to tack on a Japan side-trip without backtracking through Delhi.

## London to Bengaluru on the A350

Starting August 1, Air India will fly London Heathrow to Bengaluru on the A350-900 — a route that fills a genuine gap. Until now, the 350,000 Indians in the UK with roots in Karnataka have relied on connections through Mumbai or Delhi, or on carriers like Emirates routing through Dubai. The nonstop link between Britain's capital and India's technology hub is overdue.

## The Routes Already Running

Several other new routes have already gone live this year with little fanfare:

- **Delhi–Rome**: Four weekly nonstops since March 25, reconnecting India to one of its largest European trade partners after a long hiatus. Italy hosts roughly 180,000 Indians, mostly in the northern industrial belt.
- **Delhi–Hanoi**: Five weekly nonstops since May 1, complementing existing daily service to Ho Chi Minh City. Vietnam has become an increasingly popular destination for Indian tourists, with visa-on-arrival simplifying the process.
- **Delhi–Shanghai**: Four weekly nonstops resumed in February — the first return to mainland China in nearly six years. Business travel between the countries had been limping along on connections through Hong Kong and Singapore.
- **India–Singapore**: 52 flights per week, the densest frequency Air India has ever operated on the corridor. Singapore's 750,000-strong Indian community is the target.

## Domestic Heritage Circuits

Air India is not ignoring internal connectivity. From October 25, daily flights will link Delhi, Khajuraho, and Varanasi in a tri-city heritage circuit — a route designed explicitly for the tourism corridor between Madhya Pradesh's temples and the Varanasi ghats. A new Mumbai–Jaisalmer nonstop opens up Rajasthan's desert fort city without the usual connection through Delhi.

## What This Means for NRI Summer Planning

The net effect is that Air India now serves eight destinations in mainland Europe, three in the UK, and has meaningfully expanded its Asian network — all while Indian carriers collectively are cutting domestic capacity by 10–22 percent due to fuel costs. The international expansion and domestic contraction are not contradictory: long-haul routes are where margins survive even at elevated fuel prices, while short-haul metro-to-metro routes are the first to be trimmed.

For NRIs booking summer and fall travel, the practical takeaway is to check Air India's network before defaulting to Gulf connections. The airline also picked up the APEX Award for Best Entertainment in Central and Southern Asia — a small but telling sign that the Tata Group's post-privatisation overhaul is reaching the cabin experience, not just the route map.

Sources: [Cleartrip](https://www.cleartrip.com), [BrightSun Travel](https://brightsun.co.in), [TravTalk India](https://travtalkindia.com), [Travel Daily Media](https://traveldailymedia.com)"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's 2026 Route Blitz — Mumbai-Tokyo, London-Bengaluru, and Nine Other New Flights NRIs Should Know About",
    "subheadline": "The Tata-owned carrier is adding more international routes in a single year than it has in the past decade, from Haneda to Heathrow to Shanghai.",
    "slug": make_slug("air-india-2026-route-expansion-mumbai-tokyo-london-bengaluru-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Four million Indian Americans fly the India corridor annually; Air India's new routes to Tokyo Haneda, London-Bengaluru, Delhi-Rome, and resumed Delhi-Shanghai service give NRIs more nonstop options that bypass Gulf hubs.",
    "tags": ["travel", "airlines", "air india", "routes", "nri travel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Cleartrip", "url": "https://www.cleartrip.com/offers/domestic/mumbai-to-tokyo-haneda-with-air-india"},
        {"name": "BrightSun Travel", "url": "https://brightsun.co.in/blog/air-india-expands-connectivity-with-new-routes-for-2026"},
        {"name": "TravTalk India", "url": "https://travtalkindia.com/air-india-to-resume-non-stop-delhi-rome-flights-from-march-2026/"},
        {"name": "Travel Daily Media", "url": "https://traveldailymedia.com/air-india-to-operate-daily-flights-to-tokyo-haneda/"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "body": article1_body
}

# ============================================================
# ARTICLE 2: India's Fast Track Immigration for NRIs
# ============================================================

article2_body = """If you have been landing at Delhi or Mumbai after a 16-hour flight and then standing in a 90-minute immigration queue, you have been doing it wrong. India has quietly rolled out a system that can get you through passport control in 30 seconds — and most NRIs do not know it exists.

## What Is FTI-TTP?

The Fast Track Immigration–Trusted Traveller Programme is India's answer to Global Entry. Launched as a pilot at Delhi's Indira Gandhi International Airport in 2024, it has since expanded to 31 international airports — from the obvious (Mumbai, Bengaluru, Hyderabad, Chennai) to the smaller gateways NRIs actually use when visiting family (Amritsar, Lucknow, Trichy, Calicut, Coimbatore, Mangalore, Varanasi, and even Gaya and Bagdogra).

The system uses automated e-gates with biometric verification: you scan your passport, the gate reads your fingerprints, and you walk through. No immigration officer, no forms, no queue.

## Who Qualifies

Two categories: **Indian passport holders** and **OCI cardholders**. That covers virtually every NRI. You do not need to be a frequent flyer or a diplomat. The programme is open to any eligible applicant who passes a background check.

## How to Register

1. Visit the FTI-TTP portal (search "FTI TTP India" — the official government site)
2. Fill in your personal details and passport information
3. Upload a scanned passport photo and passport pages
4. On your next trip through an enrolled airport, visit the FTI-TTP biometric enrolment counter to submit fingerprints and a facial scan
5. Once enrolled, you are cleared to use e-gates at any of the 31 participating airports

Registration is valid for the duration of your passport's validity or five years, whichever comes first. The fee is nominal — ₹500 (roughly $6).

## The 31 Airports

The full list: Delhi, Mumbai, Chennai, Kolkata, Bengaluru, Hyderabad, Cochin, Goa (Dabolim and Mopa), Ahmedabad, Amritsar, Gaya, Jaipur, Lucknow, Trichy, Varanasi, Calicut, Mangalore, Pune, Nagpur, Coimbatore, Bagdogra, Guwahati, Chandigarh, Visakhapatnam, Madurai, Bhubaneswar, Port Blair, Kannur, Indore, and Thiruvananthapuram.

If your hometown airport is on this list, there is no excuse not to enrol.

## Pairing It With Global Entry in the US

India is one of 11 countries whose citizens are eligible for the US Customs and Border Protection's Global Entry programme. The two programmes together create a genuine fast lane on both ends of the India-US corridor.

Global Entry costs $100 for five years and includes TSA PreCheck domestically. The application process for Indian citizens has an extra step: after applying online through the CBP Trusted Traveler Programs portal, you must also submit information through India's Passport Seva Portal with a ₹500 fee and schedule an in-person interview at your local Passport Seva Kendra for a background check.

The practical advice: apply for Global Entry before your next trip to India so you can complete the PSK interview during your visit. Then enrol in FTI-TTP at the airport on the same trip. One visit, both programmes done.

## Why This Matters for NRIs

The immigration experience at Indian airports has been a persistent irritant for the diaspora. Three lakh passengers have already registered for FTI-TTP, but that is a fraction of the roughly 15 million international passengers who move through Indian airports annually. The programme is expanding to foreign travellers in its next phase, but NRIs and OCI holders can use it right now.

Combined with Global Entry on the US side, an NRI can realistically go from aircraft door to baggage claim in under five minutes at both ends of the journey. For families travelling with elderly parents or young children — which describes most NRI homecoming trips — that is not a convenience. It is a necessity.

Sources: [VisaHQ](https://www.visahq.com/india/), [IndianEagle](https://www.indianeagle.com/travelbeats/), [Government FTI-TTP Portal](https://ftittp.gov.in), [US CBP Global Entry](https://www.cbp.gov/travel/trusted-traveler-programs/global-entry)"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Skip the Queue — India's Fast-Track Immigration Programme Is Live at 31 Airports, and Most NRIs Don't Know About It",
    "subheadline": "The FTI-TTP system uses biometric e-gates to clear immigration in 30 seconds. Combined with Global Entry in the US, it eliminates the worst part of flying the India corridor.",
    "slug": make_slug("india-fti-ttp-fast-track-immigration-nri-global-entry-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs and OCI cardholders can register for India's FTI-TTP to clear immigration via automated e-gates in 30 seconds at 31 airports. Paired with US Global Entry, it creates a fast lane on both ends of the India-US corridor.",
    "tags": ["travel", "airports", "immigration", "nri travel", "global entry"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "VisaHQ India", "url": "https://www.visahq.com/india/"},
        {"name": "Government FTI-TTP Portal", "url": "https://ftittp.gov.in"},
        {"name": "US CBP Global Entry", "url": "https://www.cbp.gov/travel/trusted-traveler-programs/global-entry"},
        {"name": "Testbook (Amit Shah Launch)", "url": "https://testbook.com/question-answer/amit-shah-launches-faster-immigration-clearance"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/32176062/pexels-photo-32176062.jpeg",
    "body": article2_body
}

# ============================================================
# Publish
# ============================================================

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
