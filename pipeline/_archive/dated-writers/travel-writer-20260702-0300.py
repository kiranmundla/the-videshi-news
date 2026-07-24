#!/usr/bin/env python3
"""Travel writer — July 2, 2026 batch. Two articles for The Videshi travel section."""

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


# ── Article 1: Bhogapuram Airport ──────────────────────────────────────

article1_body = """All commercial flights serving Visakhapatnam will shift to the brand-new Alluri Sitarama Raju International Airport at Bhogapuram on July 8 — and for the roughly 800,000 Telugu-speaking Americans who still call coastal Andhra Pradesh home, the move changes how they'll fly back.

The old Visakhapatnam Airport has served the region since the 1960s, but it was never really a civilian airport. It operates as a civil enclave inside INS Dega, the Indian Navy's Eastern Command air station. Commercial flights shared a single 3,050-metre runway with military aircraft, terminal expansion was locked by defence boundaries, and airspace windows were negotiated around naval operations.

That compromise has now ended. The Navy wants full control of the airfield to expand its maritime air operations, and civil aviation gets a purpose-built replacement 45 kilometres north, in Vizianagaram district.

## What the New Airport Looks Like

Bhogapuram is a greenfield facility developed by GMR Visakhapatnam International Airport Limited, with an initial capacity of six million passengers a year — more than double the old terminal's 2.74 million. The single 3,700-metre runway is longer than Vizag's existing one, equipped with Category II instrument landing systems that allow operations in visibility as low as 300 metres.

The terminal layout is designed around the lotus motif that GMR has used across its airport portfolio. Unlike the cramped Vizag terminal — 20 check-in counters, three baggage belts — the new facility is built for contemporary throughput, with room for a second parallel runway and a planned eventual capacity of 90 million passengers across three interconnected terminal phases.

## The NRI Catch: It's Farther from the City

Here's the practical issue. Bhogapuram sits approximately 45 kilometres from Visakhapatnam's city centre, compared to the current airport's convenient location within the city limits. For NRIs whose parents live in Vizag's Waltair, MVP Colony, or Madhurawada neighbourhoods, the ride to the airport just got significantly longer.

Road connectivity is the immediate bottleneck. The Vizianagaram highway serves as the primary corridor, but dedicated airport expressway infrastructure is still under development. Travellers arriving on late-night international connections should plan for longer transfers and potentially limited cab availability during the early months of operation.

## What It Costs

The Airports Economic Regulatory Authority of India has approved ad hoc tariffs for the new airport. Domestic departures will carry a User Development Fee of ₹835 per passenger, with arrivals at ₹355. International travellers pay ₹1,255 on departure and ₹545 on arrival. Children under two, diplomats, transit passengers, and airline crew on duty are exempt.

These rates are higher than what passengers paid at the old Vizag airport, reflecting the cost of a brand-new facility. The final tariff structure will be determined once AERA completes its first regulatory control period review.

## Which Airlines and Where

IndiGo and Air India Express currently dominate Vizag's route network. IndiGo operates domestic services to major metros plus two surviving international routes to Singapore and Abu Dhabi. Air India Express connects the city to Gulf destinations. Singapore's Scoot, which launched Vizag service in recent years, has confirmed it will shift operations to Bhogapuram from July 8.

For NRIs, the critical question is international connectivity. The old airport's constrained infrastructure limited growth on international routes — services to Bangkok, Kuala Lumpur, and Dubai were launched and withdrawn over the years as demand fluctuated against operational limitations. Bhogapuram's larger capacity and dedicated international terminal should, in theory, support more stable international services.

## The Navy Backdrop

The handover isn't just an infrastructure story. The Navy's decision to take full control of Visakhapatnam's airspace — effective July 9, with the service designated as the "Controlling Authority" under new Aeronautical Information Publication supplements — reflects India's broader military modernisation along the eastern seaboard. INS Dega is home to naval reconnaissance and maritime patrol aircraft that will benefit from unrestricted airfield operations.

For NRIs who grew up watching Navy jets share the tarmac with IndiGo A320s, that era ends next week.

## What to Do Now

If you're flying into Vizag after July 8, update your ground transport plans. The airport code remains VTZ for now, but the physical destination is Bhogapuram. Book cabs or arrange family pickups accounting for the 45-kilometre distance from the city. International passengers should check airline communications for any schedule changes during the transition window.

The new airport is a long-overdue upgrade for a coastline that stretches from Srikakulam to Kakinada. Whether it lives up to its promise depends on what comes next — the road connectivity, the international routes, and whether airlines see Bhogapuram as a gateway worth betting on."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Vizag's Airport Is Moving Next Week — What NRIs Flying Home to Andhra Pradesh Need to Know",
    "subheadline": "All commercial flights shift from the Navy-shared Visakhapatnam Airport to a brand-new facility at Bhogapuram on July 8. The upgrade is overdue, but the 45-kilometre commute from the city is not.",
    "slug": make_slug("vizag-airport-bhogapuram-shift-nri-andhra-pradesh"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Roughly 800,000 Telugu Americans fly back to coastal Andhra Pradesh regularly — their airport is physically relocating 45km north, changing ground transport logistics for every trip home.",
    "tags": ["travel", "airports", "andhra-pradesh", "vizag", "infrastructure", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/commercial-flight-operations-to-end-at-visakhapatnam-international-airport-on-july-8/"},
        {"name": "Aviation India", "url": "https://indianaviationnews.net/2026/06/23/aera-approves-tariffs-bhogapuram-airport/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-express-eyes-europe-expansion-plans-georgia-entry/article71166517.ece"},
        {"name": "SSBCrack News", "url": "https://news.ssbcrack.com/indian-navy-visakhapatnam-airspace-control-july-2026/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Aerial_view_of_runway_of_Alluri_Sitarama_Raju_International_Airport_07.jpg/1280px-Aerial_view_of_runway_of_Alluri_Sitarama_Raju_International_Airport_07.jpg",
    "image_caption": "Aerial view of the runway at the new Alluri Sitarama Raju International Airport at Bhogapuram",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}


# ── Article 2: Delhi Hub-and-Spoke ─────────────────────────────────────

article2_body = """Delhi's Indira Gandhi International Airport handled 7.5 million domestic-to-international transfer passengers in FY26 — up 83 per cent from 4.1 million the previous year. One in four passengers passing through the airport is now in transit. And if the government's new hub-and-spoke model works as designed, those numbers are headed much higher.

The ambition is straightforward: make Delhi a global transfer hub on par with Dubai, Doha, and Singapore, so that Indian passengers from Varanasi, Lucknow, or Bhubaneswar no longer need to route through a foreign airport to reach London or New York.

Air India put that ambition into practice on June 25, when it launched "Easy Connect" — a hub-and-spoke product that treats Varanasi as a spoke and Delhi as the hub. Passengers boarding flight AI1111 in Varanasi at 9:50 AM complete immigration at Varanasi itself, land in Delhi as international transit passengers, and connect within four hours to any of 17 international destinations including London Heathrow, Frankfurt, Rome, Milan, Zurich, Singapore, Dubai, and Manila.

## Why This Matters to NRIs

For years, the standard NRI trip home to a non-metro Indian city involved a painful sequence: fly SFO or JFK to Dubai or Doha, clear immigration in a foreign hub, then catch a domestic connection to Varanasi or Lucknow or Bhubaneswar. The return was worse — a 3 AM departure from a Tier 2 city to catch a Gulf connection at dawn.

Delhi's hub-and-spoke model flips this. Your parents in Varanasi can now check in internationally at their home airport, transit through Delhi with a sub-one-hour connection (no immigration queues, no baggage retrieval), and board a nonstop to London or Frankfurt. The reverse works too: NRIs landing at Delhi from overseas can connect to a smaller city without leaving the international transit zone, with baggage transferred airside.

This is especially powerful for elderly parents travelling alone. Navigating a transit through Dubai International — with its sprawling concourses, Arabic signage, and multi-hour layovers — is daunting for someone who speaks Hindi and Telugu. Delhi's Terminal 3, whatever its flaws, is familiar territory.

## The Infrastructure Behind It

DIAL, the airport operator, has invested in making this work at scale. The upgrades include dedicated international-contact gates, an expanded international-to-international transfer area (capacity tripled under the Phase 3A expansion), DigiYatra biometric e-gates for seamless identity verification, and segregated corridors that keep domestic and international passengers on the same aircraft operationally separated.

Pier C of Terminal 3, which previously handled domestic flights, has been converted to international operations — adding nearly 10 million passengers of annual international capacity without constructing a single new building. Delhi's international handling at T3 now approaches 30–32 million passengers per year.

The hub-and-spoke standard operating procedures, issued by the Ministry of Civil Aviation in April, lay out the mechanics: two boarding passes (marked "D" and "I"), immigration at the spoke airport, airside baggage transfer at Delhi, and mandatory DigiYatra enrolment for Indian nationals on the international leg.

## Where It Goes Next

Varanasi is the pilot. Air India plans to expand Easy Connect to "several additional cities in a phased manner," with future spoke-to-hub flights numbered in the AI11XX series. The obvious candidates are high-traffic Tier 2 airports with large diaspora connections: Lucknow, Patna, Jaipur, Ahmedabad, and Chandigarh.

DIAL CEO Pradeep Panicker framed the goal in competitive terms: "Our overarching goal is not about hitting any specific number, but about ensuring Delhi offers a world-class hub experience competitive with the best in the world." Translation: they want to pull transfer traffic away from Gulf hubs — and the 83 per cent year-over-year growth in transit numbers suggests it's already happening.

## The Limits

Delhi still has significant constraints. The airport handled 78.7 million total passengers in FY26, down slightly from 79.2 million the prior year, suggesting capacity pressure. The single-terminal international setup (even with Pier C's conversion) will face strain as transfer traffic scales. And the hub model only works if spoke flights are timed tightly with international departures — miss the four-hour connection window, and you're stuck at Delhi with no advantage over a Gulf transit.

For NRIs, the practical upside is real but conditional. If your hometown has an Easy Connect flight, this changes your travel calculus. If it doesn't yet, you're still routing through Dubai. Watch the AI11XX series for your city's name."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Delhi Wants to Be the New Dubai — and the Numbers Say It Might Be Working",
    "subheadline": "Transfer passengers at Delhi Airport surged 83 per cent last year. Air India's new hub-and-spoke flights mean your parents in Varanasi can now clear immigration at home and connect to London through Delhi — no Gulf layover required.",
    "slug": make_slug("delhi-airport-hub-spoke-air-india-easy-connect-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs from Tier 2 cities have long depended on Gulf hubs to reach home. Delhi's hub-and-spoke model lets passengers from Varanasi (and soon other cities) transit through Delhi instead, with immigration completed at their home airport.",
    "tags": ["travel", "airports", "delhi", "air-india", "hub-and-spoke", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/delhi-airport-handled-75-mn-domestic-to-international-transfer-passengers-in-fy26/article71166517.ece"},
        {"name": "Air India", "url": "https://www.airindia.com/in/en/announcements/air-india-easy-connect-flights.html"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2255045"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Delhi_Airport_Terminal_3.jpeg/1280px-Delhi_Airport_Terminal_3.jpeg",
    "image_caption": "Terminal 3 at Delhi's Indira Gandhi International Airport, the hub of India's new spoke-and-connect model",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}


# ── Insert ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
