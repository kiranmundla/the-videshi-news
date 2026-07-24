#!/usr/bin/env python3
"""Travel writer — 30 June 2026 evening run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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

# ─────────────────────────────────────────────────────────────────
# ARTICLE 1: July 4th NRI Travel Guide
# ─────────────────────────────────────────────────────────────────

art1_body = """A record 72.2 million Americans are expected to travel over the July 4th weekend, according to AAA — and if you are one of the millions of Indian Americans planning a getaway, the numbers this year deserve a closer look before you book.

## The Big Picture

The Independence Day travel window (roughly July 1–7) is shaping up as one of the busiest in recent memory. About 85 per cent of those travellers — some 61 million — will drive, drawn by the flexibility of the open road even as gas prices sit more than 80 cents per gallon higher than last summer. Another 5.85 million will fly domestically, a small but record-setting number. And for the first time, bus, train and cruise travel will cross 4.93 million, a 5 per cent jump from 2025, with cruises leading the growth.

Airfares, however, are finally inching down after weeks of increases. KAYAK data shows that the cheapest day to fly is, counterintuitively, July 4th itself — domestic fares that day average around $286, roughly 25 per cent less than departures on July 1 or 2. Budget consciousness is the defining theme: Expedia reports a 1,265 per cent year-over-year surge in budget-filter usage and a 120 per cent jump in economy-fare searches.

## Where NRIs Are Heading

The trending destinations this July 4th are not the usual beach towns. National-park-adjacent locales dominate Expedia's list: Moab (Utah), Gatlinburg (Tennessee), Flagstaff (Arizona), Mariposa near Yosemite (California), and Bozeman (Montana). Flight-arrival data tells the same story — Alaska, Maine and Montana each recorded roughly 50 per cent year-over-year growth in incoming July 4th flights.

For Indian American families, national parks have long been a quiet favourite. The combination of affordable campgrounds, family-friendly trails, and the kind of landscape photography that fills WhatsApp groups makes them a natural fit. A long weekend at Yosemite, Yellowstone, or the Grand Canyon costs a fraction of a resort vacation, and with a $35 annual America the Beautiful pass covering all parks, the math works.

## The India-Bound Crowd

Not everyone is heading to Montana. For NRIs whose July 4th week doubles as the start of a summer India trip, the fare picture is mixed. Travelocity data shows SFO–Delhi roundtrips in early July starting around $1,522, while JFK–Delhi sits near $1,192. Those willing to push departure to August can find SFO–Delhi or SFO–Mumbai as low as $753 — a nearly 50 per cent drop.

The gap is significant, and it tracks with a broader pattern: peak-season fares on the key diaspora corridors (SFO–DEL, JFK–BOM, ORD–HYD, LAX–BLR) are at their most punishing in the first week of July, when school holidays, the long weekend, and summer wedding season in India all collide. Two to three weeks of flexibility in either direction can save $500 or more per ticket.

## Smart Moves for the Weekend

For those still finalising plans, a few practical notes. Departing on July 3 or 4 instead of July 1 or 2 saves on domestic airfare. If driving, AAA recommends filling up before Thursday — gas stations near highways and tourist corridors mark up prices over the holiday. KAYAK's data shows that sports-event cities (Kansas City, New York, San Antonio) are seeing a secondary search spike, so hotel availability in those markets may tighten.

Cruises, meanwhile, have emerged as a sleeper pick. Their all-inclusive pricing appeals to families watching every line item, and several three- to five-night sailings depart from Galveston, Miami, and Long Beach — all within driving distance of large Indian American communities in Texas, Florida, and California.

The bottom line: it will be crowded out there. But with a bit of timing, flexibility, and the right destination, July 4th can be both affordable and worth the traffic."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "72 Million Americans Are Travelling This July 4th — Here's the NRI Playbook",
    "subheadline": "National parks are trending, airfares are finally dipping, and the cheapest day to fly is the holiday itself. A data-driven guide for Indian Americans planning the long weekend.",
    "slug": make_slug("july-4th-travel-guide-nri-national-parks"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian American families are among the millions travelling this July 4th; the article breaks down the best destinations, fare timing, and India-bound flight data specifically relevant to NRI travellers.",
    "tags": ["travel", "july 4th", "road trip", "national parks", "airfares", "NRI"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "AAA", "url": "https://newsroom.aaa.com"},
        {"name": "KAYAK Summer 2026 Savings Report", "url": "https://kayak.com"},
        {"name": "Expedia July 4th Report", "url": "https://expedia.com"},
        {"name": "Travelocity India Flights", "url": "https://travelocity.com"},
        {"name": "NBC Palm Springs / Travel And Tour World", "url": "https://travelandtourworld.com"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/18514240/pexels-photo-18514240.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An empty highway stretches through Monument Valley under a bright summer sky",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ─────────────────────────────────────────────────────────────────
# ARTICLE 2: Air India Route Restoration + Gulf Airspace
# ─────────────────────────────────────────────────────────────────

art2_body = """Air India may reinstate some of the international flights it cut earlier this summer after the Gulf airspace picture improved and jet fuel prices fell sharply, the airline's CEO Campbell Wilson said in an internal memo obtained by NDTV.

## What Changed

Between June and August, Air India had trimmed capacity on several long-haul routes — including key NRI corridors to Chicago, Newark, San Francisco and Toronto — citing Middle East airspace restrictions that forced longer, costlier detours to Europe and North America. For months, the conflict in the region had closed or constrained overflight routes across Iraq, Kuwait, Bahrain and parts of Iran, adding hours to westbound flights and burning through fuel budgets.

Now, with violence in the region subsiding, more of that airspace has reopened. Wilson's memo is candid: "The violence in the Middle East has subsided, and although there is no assurance that it won't worsen, the calmer climate has made more airspace available, and fuel prices have considerably decreased. We might be able to reverse some of the timetable cuts we made in recent months if this trend continues."

The airline stressed that it never stopped being a major international operator during the disruption. Air India continued running more than 1,200 international flights every month across five continents, even at reduced frequencies.

## Fleet Firepower

The potential restoration is backed by metal. Wilson confirmed that Air India expects to induct eight more new or refurbished wide-body aircraft before the end of the year. A Boeing 787-8 is currently being sent for a full cabin retrofit, and a brand-new Boeing 787-9 was scheduled to arrive in India over the weekend. Those additions matter: wide-body availability was one of the constraints that made it difficult to sustain high-frequency long-haul service during the crisis.

Separately, Air India reported that June was its best operational month yet, with 86 per cent of flights departing on time across the network and domestic on-time performance hitting a record 90 per cent. For passengers who suffered through years of delays and cancellations under the old Air India, the numbers represent a tangible shift under Tata Group management.

## New Routes Keep Coming

Even as it reviews restorations, Air India is not standing still on expansion. The airline launched four weekly nonstop flights between Mumbai and Tokyo Haneda earlier this month, adding to its existing daily Delhi–Haneda service. Japan is now the airline's biggest growth bet in Asia.

Its low-cost arm, Air India Express, is also pushing hard. Next month, it becomes the first airline to operate a direct international passenger flight from the brand-new Navi Mumbai International Airport — with Abu Dhabi as the inaugural destination. And in August, Air India Express will launch Guwahati's first-ever direct flights to Dubai and Abu Dhabi, ending decades of connecting-flight dependency for Northeast India's 50-million-plus population.

## What This Means for NRIs

The NRI corridors hit hardest by the summer cuts — O'Hare, Newark Liberty, SFO, and Toronto Pearson — carry some of the heaviest VFR (visiting friends and relatives) traffic of any routes in Air India's network. Their restoration, even partial, would relieve pressure on fares that spiked after capacity was pulled.

The timing matters. October through December is peak season for India-bound travel from North America — Diwali, wedding season, school breaks. If Air India can bring back even half the suspended frequencies before that window opens, NRI travellers on the East Coast and Midwest will have measurably more options and, critically, lower fares.

No firm timeline has been announced, and Wilson's memo makes clear the reversal depends on continued geopolitical stability and fuel-price trends. But for the first time since the crisis began, the signal from Air India's corner office is pointing in the right direction."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India May Reverse Its Summer Route Cuts as Gulf Airspace Reopens and Fuel Prices Fall",
    "subheadline": "CEO Campbell Wilson's internal memo signals that some of the international flights trimmed between June and August could return — backed by eight new wide-body aircraft arriving this year.",
    "slug": make_slug("air-india-route-restoration-gulf-airspace-fleet"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI corridors to Chicago, Newark, SFO, and Toronto were among the hardest-hit routes; restoration before Diwali season would directly benefit diaspora travellers with more options and lower fares.",
    "tags": ["travel", "airlines", "air india", "gulf crisis", "NRI corridors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "IANS / NDTV (Campbell Wilson memo)", "url": "https://ianslive.in"},
        {"name": "Travel And Tour World", "url": "https://travelandtourworld.com"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com"},
        {"name": "Inshorts", "url": "https://inshorts.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Air_India_Boeing_787-8_VT-ANB_NRT_%2815922475860%29_-_crop.jpg/1280px-Air_India_Boeing_787-8_VT-ANB_NRT_%2815922475860%29_-_crop.jpg",
    "image_caption": "An Air India Boeing 787-8 Dreamliner on the tarmac",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}

# ─────────────────────────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['headline']}: {e}")
