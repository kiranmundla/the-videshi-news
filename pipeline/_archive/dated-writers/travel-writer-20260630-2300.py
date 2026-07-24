#!/usr/bin/env python3
"""Travel writer — 2026-06-30 23:00 PT batch."""

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


# ── Article 1: Air Suvidha 2.0 ──────────────────────────────────────────────

article1_body = """\
India has quietly re-activated one of the pandemic era's most recognisable travel tools — and this time, Ebola is the trigger.

On June 25, the Ministry of Civil Aviation and Delhi International Airport Limited launched **Air Suvidha 2.0**, a mandatory digital health self-declaration portal for every international passenger arriving in India. The form went live five weeks after the World Health Organization declared the Bundibugyo virus disease outbreak in the Democratic Republic of the Congo and Uganda a Public Health Emergency of International Concern. No exceptions, no exemptions: whether you are flying in from Dubai, San Francisco or London, you must submit the form before clearing immigration.

## What the form asks

Air Suvidha 2.0 collects three categories of data: your travel history over the previous 21 days, any exposure to Ebola-affected regions, and current symptoms such as fever, body aches or unexplained bleeding. The portal — available at **airsuvidha.civilaviation.gov.in** — is free, takes roughly five minutes to fill out, and requires no app download. You complete it from any browser on your phone or laptop.

The system shares your submission in real time with the Airport Health Officer, the Bureau of Immigration, the Integrated Disease Surveillance Programme and State Surveillance Officers. The idea is that by the time you land, authorities already have your data — so screening at the health desk is faster, not slower. Passengers who fill it out in advance simply show the downloaded form at the International Travel Health Desk or the immigration counter.

## The timing matters for NRIs

The portal's launch coincides with peak summer travel season on the India–US corridor. Hundreds of thousands of Indian Americans fly home between June and August, many with elderly parents, young children and multi-city itineraries. Adding a mandatory form to the pre-departure checklist — on top of existing visa documentation, OCI card renewals and the digital arrival card — is one more task in an already dense sequence.

For **OCI cardholders**, the burden doubles: you must now fill out **both** the Air Suvidha 2.0 form and the separate Digital Disembarkation Form (e-Arrival Card). Missing either could mean additional screening or delays at the immigration counter.

The practical advice from seasoned travellers and consular officials: complete Air Suvidha during your airline's web check-in window, ideally 24 hours before your scheduled arrival in India. Airport Wi-Fi in transit hubs like Dubai, Doha or Frankfurt can be unreliable, and the form's submission portal occasionally needs multiple attempts on a weak signal. Do it from your couch, not the gate.

## Not a COVID replay — but a sign of things to come

India's original Air Suvidha portal was a pandemic-era creation — paper-based, slow, and plagued by airport queues. Version 2.0 is entirely digital, contactless and designed to avoid the bottlenecks that frustrated millions of arrivals during COVID. The authorities stress this is a targeted Ebola screening measure, not a blanket border restriction. India has not banned any flights or imposed quarantine requirements. The outbreak itself remains geographically limited to Central and East Africa.

But the broader pattern is clear: digital health declarations are becoming a permanent fixture of international travel infrastructure. India is not alone — several countries have introduced or maintained similar portals since COVID, calibrating them to each new public health threat. For NRIs who fly home regularly, building the Air Suvidha step into pre-departure routine is likely a permanent adjustment, not a temporary inconvenience.

## What you need to know

- **Who**: All international passengers arriving in India, regardless of nationality
- **When**: Within 24 hours before your scheduled arrival
- **Where**: [airsuvidha.civilaviation.gov.in](https://airsuvidha.civilaviation.gov.in)
- **What it asks**: 21-day travel history, exposure to Ebola-affected areas, symptoms
- **OCI holders**: Must also complete the separate e-Arrival Card
- **Cost**: Free — ignore any third-party sites charging a fee
- **Pro tip**: Fill it during web check-in, download the confirmation, keep it on your phone
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Flying Home This Summer? India's Mandatory Air Suvidha 2.0 Form Is Now Live for Every International Arrival",
    "subheadline": "Triggered by the Ebola outbreak in Central Africa, the digital health declaration must be completed within 24 hours of landing — and OCI holders have double the paperwork.",
    "slug": make_slug("air-suvidha-health-form-india-ebola-nri-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Every NRI flying home this summer must now complete Air Suvidha 2.0 before landing — OCI holders face a double form requirement that adds a new mandatory step to an already paperwork-heavy journey.",
    "tags": ["travel", "air-suvidha", "ebola", "health", "immigration", "nri", "oci"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
        {"name": "TravelManToday", "url": "https://travelmantoday.com/"},
        {"name": "News89", "url": "https://news89.com/"},
        {"name": "Just Dubai", "url": "https://just-dubai.com/"},
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Terminal_3_Interior_-_Indira_Gandhi_International_Airport_-_New_Delhi_2016-08-08_9230.JPG/1280px-Terminal_3_Interior_-_Indira_Gandhi_International_Airport_-_New_Delhi_2016-08-08_9230.JPG",
    "image_caption": "Interior of Terminal 3 at Indira Gandhi International Airport in New Delhi, the hub where Air Suvidha 2.0 was developed",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ── Article 2: Adani Airport Cities ──────────────────────────────────────────

article2_body = """\
If you have landed at Mumbai, Ahmedabad or Jaipur in recent years, you know the routine: step off the plane into a gleaming terminal, then exit into a tangle of construction dust, auto-rickshaws and half-built flyovers. Adani Airport Holdings wants to change the second part.

The company has announced a **₹20,000-crore ($2.3 billion) plan** to build integrated airport cities across six of the eight airports it manages — Mumbai, Navi Mumbai, Ahmedabad, Lucknow, Jaipur and Guwahati. The first phase will span roughly **22 million square feet across 655 acres**, with nearly 70 per cent of the investment concentrated in the Mumbai metropolitan region.

## The blueprint

The model is borrowed from Singapore's Changi, Dubai International, Amsterdam Schiphol and Seoul Incheon — airports that function as self-contained districts with hotels, retail, entertainment, convention centres and commercial offices, all connected to metro and city transport networks. The difference is scale: Adani is attempting it simultaneously across six cities instead of one, in a country where airport precincts have historically been afterthoughts.

"Around the world, the most successful airport districts have become centres of commerce, tourism and urban growth," said **Jeet Adani**, director of Adani Airport Holdings. "We are creating a network of integrated urban destinations where airports become catalysts for investment, employment, better passenger experiences and the long-term growth of the cities they serve."

The projects have already received **LEED Gold pre-certification** from the U.S. Green Building Council for sustainable design — a detail that signals the company is targeting international corporate tenants and global hotel chains, not just domestic retail.

## IHG, Kimpton and 1,500 hotel rooms

The hospitality piece is already moving. In May, Adani signed a managed hotel portfolio agreement with **IHG Hotels & Resorts** for five properties totalling roughly **1,500 rooms**. The deal introduces IHG's luxury lifestyle brand **Kimpton Hotels & Restaurants** to India for the first time, with a boutique property planned for Jaipur. The remaining hotels — Holiday Inn and Holiday Inn Express branded — will sit within the airport city developments at Navi Mumbai, Mangaluru and Thiruvananthapuram.

The architecture portfolio reads like a global shortlist: **Kohn Pedersen Fox** (Hudson Yards, One Vanderbilt), **Benoy** (Changi Airport's Jewel) and **Znera Space** are designing the precincts. Construction is being handled by **Larsen & Toubro**, **Tata Projects** and **PSP Projects**, with **CBRE, JLL and Cushman & Wakefield** advising on planning and commercial leasing.

## Why NRIs should pay attention

For the roughly 4.5 million Indian Americans who fly to India at least once every couple of years, airport cities would change the bookend of every trip. A Kimpton in Jaipur means a reliable layover hotel for families connecting through Rajasthan. A Holiday Inn Express at Navi Mumbai airport means NRIs arriving on the new NMIA flights — which go international on July 15 with an Abu Dhabi route — do not need to cross the harbour bridge to find a decent room.

More broadly, airport cities tend to anchor surrounding real estate development. NRIs with property investments in suburbs near Mumbai, Ahmedabad or Lucknow airports may see those areas appreciate faster as commercial districts materialise around the terminals. The IHG deal also signals that global hospitality brands now view Indian airports as viable premium destinations — a shift from the budget-hotel-and-dhaba model that has defined most airport peripheries for decades.

## The catch

Adani's airport city timeline is ambitious but unspecified. The company has not published a completion schedule for any of the six cities. India's record on large-scale airport infrastructure — Navi Mumbai's airport itself was first proposed in 1997 and is only now approaching its international debut — suggests that NRIs should plan for the airport city experience to arrive gradually, not all at once.

Still, the $2.3 billion commitment is real, the IHG contracts are signed, and the LEED certification process is under way. For a traveller who has spent the last twenty years navigating the chaos outside Indian airport doors, even incremental progress would be noticeable.
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Adani Is Spending $2.3 Billion to Build Airport Cities Across India — Here's What Changes for NRI Travellers",
    "subheadline": "Six airports. 655 acres. Hotels by IHG and Kimpton. The plan to turn Indian airport exits from construction zones into Singapore-style districts.",
    "slug": make_slug("adani-airport-cities-mumbai-ihg-kimpton-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs landing at Mumbai, Ahmedabad, Jaipur, Lucknow or Guwahati will eventually walk out of the terminal into integrated districts with global hotel brands, retail and transit connections — replacing the chaotic airport surrounds they have navigated for decades.",
    "tags": [
        "travel",
        "airports",
        "adani",
        "infrastructure",
        "ihg",
        "kimpton",
        "mumbai",
        "navi-mumbai",
        "nri",
    ],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/"},
        {"name": "TravelBiz", "url": "https://travelbiz.biz/"},
        {"name": "Adani Group", "url": "https://www.adani.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
    "image_caption": "Navi Mumbai International Airport, one of six airports in Adani's $2.3 billion airport city plan",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}

# ── Insert ───────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
