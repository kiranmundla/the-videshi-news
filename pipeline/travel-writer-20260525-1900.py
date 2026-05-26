#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 19:00 PDT batch"""

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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Hong Kong Airport Terminal 2
# ─────────────────────────────────────────────────────────

art1_body = """Hong Kong International Airport opens its rebuilt Terminal 2 for departures on Tuesday, and if you are an NRI who routes through HKG on Cathay Pacific, HK Express, or any of 13 other regional carriers, your next trip to India just got more complicated — at least temporarily.

## What Is Happening

Starting 27 May 2026, fifteen airlines will relocate their check-in operations from Terminal 1 to the brand-new Terminal 2 in a phased rollout running through mid-June. Hong Kong Airlines moves first on 27 May, Greater Bay Airlines follows on 3 June, and HK Express — Cathay Pacific's low-cost arm — shifts on 10 June. Selected Cathay Pacific regional flights complete the migration by mid-June.

These fifteen carriers collectively handled 18 per cent of HKG's total seat capacity in February 2026. That is not a minor reshuffling — it is roughly one in five seats at Asia's busiest cargo hub redirected through an entirely new building.

The new terminal spans 300,000 square metres, features 160 check-in counters across eight aisles, self-service bag-drop facilities, and biometric e-Security Gates. The Airport Authority projects it will handle eight million passenger journeys in its first year of operation.

## The Catch That Matters

Here is the part that will trip up distracted travelers: if you check in at Terminal 2, you still board from Terminal 1.

The new T2 airside concourse — which will eventually house 27 additional boarding gates — is not scheduled to open until 2027. In the meantime, passengers who check in and clear security at T2 must ride the underground Automated People Mover (APM) to reach their gates in T1. The ride takes only a few minutes, but the additional transfer step adds friction that most connection calculators do not yet reflect.

## Why NRIs Should Care

Hong Kong has been a critical transit point for the Indian diaspora in North America for decades. Cathay Pacific's one-stop flights from SFO, LAX, JFK, and YVR through HKG to Delhi, Mumbai, Bangalore, and Chennai remain among the most popular premium routings for NRI families — particularly those who value the airline's lounges and connection efficiency.

The split-terminal flow disrupts that efficiency. If your inbound transpacific flight arrives at T1 and your connecting regional carrier now checks in at T2, the standard 60-minute minimum connection time is suddenly tight. If your outbound flight departs from a T2 carrier and you have lounge access, note that Cathay's flagship lounges — The Wing, The Pier, The Bridge, and The Deck — all remain in T1. You will need to factor in the APM ride before settling in.

## What to Do Before Your Next HKG Booking

**Verify your check-in terminal now.** If you are booked on any regional carrier departing HKG after 27 May, confirm your check-in location through the official HKIA relocation notice before heading to the airport. Do not rely on printed itineraries issued before mid-May.

**Add 30 minutes to your connection buffer.** The published airside minimum was set before the T2/T1 split existed. Build in extra time and pre-select seats near the front of the aircraft on your inbound leg.

**Use the APM, not the footbridge.** The Automated People Mover handles the post-security T2-to-T1 transfer. The air-conditioned footbridge is landside only — useful for ground transport, useless for reaching gates.

**Monitor gate assignments on travel day.** During the phased relocation, gate assignments may shift as the airport calibrates passenger flows. Check the official HKIA flight status page in real time.

The HK$141 billion Three-Runway System project — the largest infrastructure programme in HKG's history — aims to push total airport capacity to 120 million passengers once all phases are commissioned. The T2 opening is the most visible step yet. For the next twelve months, though, it means a little more homework for anyone connecting through Hong Kong to the subcontinent."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Hong Kong Airport's New Terminal Opens Tuesday — and NRIs Connecting to India Need to Rethink Their Layover",
    "subheadline": "Fifteen airlines are relocating to Terminal 2 starting 27 May, but boarding still happens at Terminal 1. If you transit through HKG on Cathay Pacific or HK Express, your connection math just changed.",
    "slug": make_slug("hong-kong-airport-terminal-2-nri-india-transit"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "HKG is a critical transit hub for NRIs flying Cathay Pacific from SFO, LAX, JFK, and YVR to India. The T2/T1 split-terminal flow disrupts connection timing, affects lounge access, and requires NRI families to rebuild their layover buffers for the next 12 months.",
    "tags": ["travel", "airports", "hong kong", "cathay pacific", "transit"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Air Traveler Club", "url": "https://www.airtraveler.club/news/hong-kong-airport-terminal-2-opening/"},
        {"name": "Airport Authority Hong Kong", "url": "https://www.hongkongairport.com"},
        {"name": "The HK HUB", "url": "https://thehkhub.com"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6544051/pexels-photo-6544051.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Inside Hong Kong International Airport — NRIs transiting to India face a new terminal split starting 27 May.",
    "body": art1_body
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: Europe's EES + ETIAS
# ─────────────────────────────────────────────────────────

art2_body = """If you are an NRI planning a European vacation this summer, the border experience you remember from your last trip no longer exists. Europe's new biometric Entry/Exit System went fully operational on 10 April 2026, and the numbers tell the story: 66 million crossings logged and 32,000 travelers refused entry — all within the system's first three weeks.

## Passport Stamps Are Gone

The EU's Entry/Exit System — EES — replaces physical passport stamps with a digital biometric record for every non-EU national entering or exiting the Schengen area on a short stay. At the border, authorities now collect your name, travel document data, fingerprints, and a facial image, then log the exact date and place of your entry and exit.

The system is managed by eu-LISA, the EU's large-scale IT agency, and operates across all 29 Schengen member states plus four associated countries. Germany alone runs EES kiosks at 15 airports and 50 land crossings, handling roughly one-sixth of all transactions.

For Indian passport holders — who require Schengen visas — the practical change is mostly procedural: your border crossing is now digitally recorded rather than stamped. But the enforcement bite is real. Overstays that previously went undetected because an officer missed a faded stamp are now flagged automatically. The 90/180-day rule is digitally enforced, not manually counted.

## ETIAS Is Coming for US-Citizen NRIs

The bigger change lands later this year. The European Travel Information and Authorisation System — ETIAS — is confirmed for launch in Q4 2026. It will require visa-exempt travelers heading to 30 European countries to obtain pre-travel authorisation before departure.

This directly affects NRIs who hold US, Canadian, or Australian passports. Today, an American citizen can fly to Paris or Rome without any advance paperwork beyond a valid passport. Starting in late 2026, that same traveler will need an approved ETIAS authorisation — essentially an electronic permit — before boarding.

The standard fee is €7 (approximately $8). The authorisation is valid for three years or until the passport expires. It is not a visa, and the application process is designed to be quick and online. But it is one more step in what used to be a walk-up-and-go experience for US passport holders.

## What NRIs Need to Know Right Now

**If you hold an Indian passport and have a Schengen visa:** Your border experience has already changed. Expect fingerprint and facial image collection at every entry and exit. Your 90/180-day clock is now digitally tracked — no ambiguity, no grace period. If you are planning multiple Schengen trips in a rolling six-month window, count your days carefully.

**If you hold a US or Canadian passport:** ETIAS is not live yet, but Q4 2026 is months away. When it launches, you will not be able to board a flight to Europe without a valid ETIAS authorisation. The application is simple and online, but do not assume you can do it at the gate.

**If you travel on both passports:** Some NRIs hold both an Indian passport and a US or Canadian passport. The rules that apply depend on which passport you present at the Schengen border. An Indian passport requires a Schengen visa and triggers EES recording. A US passport triggers ETIAS (once live) and also triggers EES recording. Either way, your biometric data is now in the system.

## The Bigger Picture

The EU's 2026 State of Schengen report frames these changes as part of a broader digital border strategy. The Commission has also announced an EU Visa Strategy that promises a fully digital Schengen visa by 2031. Germany's consulates in India and the United States already accept end-to-end online visa filings for the Job-Seeker Opportunity Card and the EU Blue Card.

For the estimated 4.5 million Indian Americans who visit Europe regularly — whether for business, tourism, or family — the message is clear: Europe's borders are going digital, enforcement is automated, and the old system of ink stamps and manual day-counting is finished. Plan accordingly."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Europe's Borders Just Went Fully Digital — Here's What Changes for Every NRI Traveler",
    "subheadline": "The EU's biometric Entry/Exit System has logged 66 million crossings since April. ETIAS — a new pre-travel requirement for US passport holders — launches later this year. The era of passport stamps and manual day-counting is over.",
    "slug": make_slug("europe-ees-etias-digital-border-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian passport holders with Schengen visas now face biometric recording and automated overstay detection. US-citizen NRIs will soon need ETIAS pre-travel authorisation for Europe. Dual passport holders must understand which rules apply to which document.",
    "tags": ["travel", "visa", "europe", "schengen", "ETIAS", "biometrics"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/european-commission-reports-full-entryexit-system-rollout-ahead-of-etias-launch/"},
        {"name": "VisaHQ", "url": "https://www.visahq.com/news/2026-05-19/de/eu-state-of-schengen-report-reveals-first-entryexit-system-data-66-million-crossings-logged-32-000-refusals-what-this-means-for-travellers-to-and-from-germany/"},
        {"name": "VisaNews", "url": "https://visasnews.com"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3943947/pexels-photo-3943947.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Self-service airport kiosks — Europe's new biometric border system has replaced passport stamps entirely.",
    "body": art2_body
}

# ─────────────────────────────────────────────────────────
# ARTICLE 3: India's 100th Vande Bharat + Rail Reforms
# ─────────────────────────────────────────────────────────

art3_body = """Indian Railways just rolled out its 100th Vande Bharat trainset from the Raebareli manufacturing facility — a milestone that would have been unthinkable a decade ago, and one that most NRIs visiting India this year will benefit from whether they realise it or not.

## From Two to One Hundred

The first Vande Bharat Express launched in February 2019 on the Delhi-Varanasi route as a proof of concept: a semi-high-speed, fully air-conditioned, self-propelled train designed and built entirely in India. Seven years later, the programme has scaled to 100 trainsets, connecting cities across the country at speeds up to 160 km/h with onboard Wi-Fi, GPS-based passenger information, automatic doors, and bio-vacuum toilets.

The 100th trainset — a 16-coach configuration — will undergo trials before entering passenger service. Its rollout from the Integral Coach Factory ecosystem at Raebareli marks the point where Vande Bharat has moved from flagship project to industrial programme.

For NRIs who still associate Indian train travel with unreserved coaches and 12-hour delays, the transformation is worth paying attention to. Routes like Delhi-Jaipur (under 4 hours), Mumbai-Goa (under 7.5 hours), and the recently launched Jammu-Srinagar service — which crossed 100,000 passengers in its first 22 days — are increasingly competitive with flying once you factor in airport wait times and the door-to-door convenience of city-centre rail stations.

## 52 Reforms Are Coming

The 100th train is not the end of the story. Indian Railways has announced 52 major reforms planned for 2026, covering safety, fleet, and operations:

**Vande Bharat Sleeper trains** are being prepared to replace ageing Rajdhani Express services on overnight routes. These will offer the Vande Bharat experience — modern interiors, faster speeds, better ride quality — on the long-distance corridors that NRIs typically use when visiting family across states. Think Delhi-Kolkata, Mumbai-Chennai, Bangalore-Delhi.

**Kavach 4.0**, the indigenous automatic train protection system, is expanding to more routes. The technology automatically applies brakes if a train overshoots a signal, directly addressing the safety concern that keeps many NRI families from choosing rail over air for trips with children and elderly parents.

**Hydrogen-powered coaches** are in active development, with trials at ICF Chennai. While commercial deployment is still years away, the programme signals that Indian Railways is investing in next-generation traction technology — not just scaling what works today.

**Five more Vande Bharat trains** will begin service within the next two months, with routes to be finalised shortly. New timetables under the TAG 2026 framework will restructure scheduling across the network.

## Why This Matters for the Diaspora

Indian Railways carries 8.5 billion passenger trips per year — more than any other railway on earth. For the estimated 4.5 million NRIs who visit India annually, rail is often the most practical way to travel between their arrival city and their hometown, or between the relatives scattered across multiple states.

The Vande Bharat programme is changing the calculus. A Delhi-based NRI visiting family in Agra no longer needs to hire a car for the Yamuna Expressway — the Vande Bharat covers the route in under two hours. A Hyderabad family heading to Tirupati for a temple visit has a fast, comfortable rail option that did not exist three years ago.

The 100th trainset is a production milestone, but the real milestone is attitudinal: Indian rail is no longer the mode of last resort for domestic travel. For NRIs planning their next India trip, it is worth building rail segments into the itinerary — not as nostalgia, but as the genuinely better option on a growing number of routes.

Five more trains are coming within weeks. The network is still expanding. And for the first time in a generation, the phrase "taking the train in India" does not require an apologetic qualifier."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Rolled Out Its 100th Vande Bharat Train — and NRIs Who Haven't Taken Indian Rail Recently Are Missing Out",
    "subheadline": "From two trainsets in 2019 to a hundred in 2026, with sleeper versions, hydrogen coaches, and 52 reforms on the way. Indian rail travel is no longer what you remember.",
    "slug": make_slug("india-100th-vande-bharat-rail-reforms-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India increasingly have fast, comfortable rail options on popular diaspora routes. Vande Bharat Sleepers will replace Rajdhanis on overnight corridors. Kavach safety systems address the safety concern that kept NRI families on planes.",
    "tags": ["travel", "india", "railways", "vande bharat", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "NewsAre", "url": "https://newsare.net"},
        {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.in"},
        {"name": "SRIAS Institute", "url": "https://sriasedu.in"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37414662/pexels-photo-37414662.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A passenger train under electrified wires in India — the network that just produced its 100th Vande Bharat trainset.",
    "body": art3_body
}

# ─────────────────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
