#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-28 11:00 PT run."""

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

# ─────────────────────────────────────────────────
# ARTICLE 1: Noida International Airport
# ─────────────────────────────────────────────────

article1_body = """India's newest mega airport is about to shift gears. Noida International Airport — code DXN, located in Jewar, Uttar Pradesh — opened for commercial flights on June 15 with just 12 daily services to five cities. Starting July 1, the airport will triple that to roughly 40–45 daily flights across 16 to 17 destinations, according to the Noida International Airport Limited (NIAL) board.

That is an unusually steep ramp for an airport barely two weeks old. But DXN was built for speed: it is the NCR's second full-service airport, designed to relieve congestion at Delhi's Indira Gandhi International, which handled over 72 million passengers last year and is bursting at the seams.

## What flies now, and what's coming

IndiGo and Akasa Air currently operate daily non-stops from DXN to Bengaluru, Hyderabad, Amritsar, Jammu, and Navi Mumbai. From July 1, IndiGo will add direct flights to Mumbai, Srinagar, Chandigarh, Jaipur, Jodhpur, Dehradun, Dharamshala, Bhopal, Bareilly, Kishangarh, Lucknow, and Pantnagar — a route map that covers business travellers, hill-station holidaymakers, and families visiting hometowns across North India.

The bigger milestone sits a few months further out. The international terminal is in its final construction phase, expected to be complete by September or October. Officials say international flights could begin before the end of 2026. That timeline, if it holds, means Gulf routes first — which would give diaspora passengers a second gateway into Delhi-NCR that bypasses IGI entirely.

## The numbers behind the build

DXN's Phase I is designed for 12 million passengers a year, with a master plan that scales to 70 million across four phases — matching the busiest airports in Asia. The terminal, designed by a Grimshaw-led international consortium (including Nordic, Haptic, and STUP), draws from the architecture of Indian ghats and havelis, with landscaped courtyards, natural ventilation, and a carbon-net-zero design target.

A second runway is planned for Phase III, along with a Ground Transportation Centre that could eventually integrate high-speed rail.

## The gap that still needs closing

There is a catch, and it is not small. DXN sits 70–75 kilometres from central Delhi, and there is no metro or rail link yet. The Regional Rapid Transit System (RRTS) extension and Delhi Metro Phase 4 will eventually connect Jewar to the city, but neither is operational. For now, passengers rely on a six-lane expressway, YEIDA-operated electric buses, and cabs — and local taxi fares have already drawn complaints.

Airport vice chairman Christoph Schnellmann has acknowledged the ground-transport gap but calls it a government responsibility, not the operator's. His team's focus, he says, is on getting flight operations right.

## Why this matters if you fly home to India

For the 2 million-plus NRIs who visit Delhi-NCR every year, a second airport is not a luxury — it is relief. IGI's terminals are chronically crowded, especially during Diwali and summer holiday surges. If DXN's international terminal opens on schedule, it could absorb a meaningful share of that traffic, particularly for passengers whose families live in Noida, Greater Noida, Agra, or anywhere in western UP.

The access problem is real — an extra 45-minute cab ride from South Delhi is a hard sell. But for NRIs whose in-laws live in Noida or whose connecting flight heads to Lucknow or Jaipur, DXN will save hours. And once the RRTS line opens, the calculus changes entirely.

India opened three new airports in June alone — DXN, Navi Mumbai's partial launch, and Bhogapuram near Vizag. DXN is the largest, the most ambitious, and the one most likely to reshape how the diaspora gets home."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Noida's New Airport Triples Its Flights on July 1 — and International Routes Could Follow by Christmas",
    "subheadline": "Asia's newest mega airport in Jewar goes from 12 daily flights to 45 in its third week of operation, with the international terminal now months away from completion.",
    "slug": make_slug("noida-airport-dxn-triples-flights-july-international-terminal"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting Delhi-NCR get a second airport option that could bypass IGI congestion entirely — and international flights to the Gulf and beyond may start before year-end.",
    "tags": ["travel", "airports", "infrastructure", "Noida", "Delhi-NCR", "aviation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/27/asias-largest-airport-opens/"},
        {"name": "Livemint", "url": "https://www.livemint.com/news/india/noida-airport-to-triple-flights-from-july-eyes-international-operations-by-year-end-11750935069458.html"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/national/noida-airport-flight-services-to-triple-from-july-1-nial-to-connect-with-chandigarh-jaipur-and-15-other-cities/"},
        {"name": "Skift", "url": "https://skift.com/2026/06/16/india-has-a-new-airport-getting-people-there-is-the-bigger-test/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7508565/pexels-photo-7508565.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Airport runway at sunrise with clear sky and distant terminal buildings",
    "image_attribution": "Pexels",
    "body": article1_body.strip(),
}

# ─────────────────────────────────────────────────
# ARTICLE 2: Varanasi Airport New Terminal
# ─────────────────────────────────────────────────

article2_body = """India's aviation minister wants the new terminal at Varanasi's Lal Bahadur Shastri International Airport finished within six months — ahead of schedule. Ram Mohan Naidu reviewed the ₹2,870 crore project on June 24 and told the Airports Authority of India and its contractors to accelerate. The message was unambiguous: this is a priority, and the Centre will remove whatever obstacles remain.

The urgency makes sense when you look at the numbers. Varanasi's existing terminal was designed for 3.9 million passengers a year. It is already at capacity. Pilgrim traffic to the city has surged since the Kashi Vishwanath Corridor — the sweeping redevelopment around the temple complex — opened in 2021, turning Varanasi into one of India's fastest-growing aviation markets. Domestic and international arrivals have climbed steadily, and the current infrastructure is buckling under the weight.

## A terminal that looks like the temple

The new terminal spans 75,600 square metres and borrows its architectural language from the Kashi Vishwanath Temple itself — the same sacred complex that anchors the city's identity. The design translates the temple's arches, columns, and ornamental stonework into a modern aviation structure: 72 check-in counters, eight aerobridges, multi-level parking, and modern baggage handling, all wrapped in a facade that reads as unmistakably Banarasi.

When finished, the terminal will handle 6 million passengers annually on its own. Combined with the existing facility, the airport's total capacity rises to 9.9 million — a 2.5-fold increase over today. The runway is being extended to 4,075 metres (long enough for wide-body international flights), and a new apron will park 20 aircraft simultaneously.

The AAI is tracking progress through its Sangam digital monitoring platform, which provides daily construction updates on airport projects nationwide — a departure from the opacity that has historically plagued Indian infrastructure timelines.

## Green credentials

Varanasi's new terminal is being developed as a green airport: solar energy systems, natural daylighting, waste recycling, and carbon footprint reduction are baked into the design. The goal is LEED-level sustainability certification, which would make it one of a handful of Indian airports to achieve that standard alongside the new Noida and Navi Mumbai terminals.

## The Easy Connect puzzle piece

The timing aligns with another development that amplifies the new terminal's value. On June 25, Air India launched its Easy Connect service from Varanasi — a hub-and-spoke model that lets passengers clear immigration at their home airport before connecting through Delhi to international destinations. Varanasi was the first city in the programme, with Dubai, Colombo, Jeddah, Riyadh, Kathmandu, and Phuket accessible via single-ticket bookings.

When the extended runway is ready, Varanasi could graduate from a spoke to a hub in its own right — handling direct international charters or scheduled narrow-body flights to Gulf cities, where a large Banarasi migrant community lives and works.

## What NRIs should watch

Varanasi is the diaspora's most emotionally charged destination. It is where families perform last rites, where weddings happen in ancestral homes along the ghats, and where a growing number of NRI retirees are choosing to spend winters. The current airport experience — cramped, slow, with limited flight options — has long been a bottleneck.

The new terminal changes that equation. A 6 million-passenger facility with aerobridges and modern systems means more airlines can add frequency. IndiGo already operates heavily from Varanasi; Akasa, Air India Express, and SpiceJet have been building presence. If the runway extension enables direct Gulf flights, NRIs in the UAE and Saudi Arabia — among the largest Banarasi diaspora populations — will have a route that cuts out the Delhi connection entirely.

Naidu's six-month directive puts the completion target around early 2027. For the millions who navigate through this airport each year, and the millions more in the diaspora who plan their India trips around it, that cannot come soon enough."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Varanasi's ₹2,870 Crore Airport Terminal Will Mirror the Temple It's Named After — and the Minister Wants It Done in Six Months",
    "subheadline": "The Kashi Vishwanath-inspired terminal will handle 6 million passengers a year, extend the runway for wide-body jets, and pair with Air India's new hub-and-spoke service that already flies from the city.",
    "slug": make_slug("varanasi-airport-terminal-kashi-vishwanath-expansion-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Varanasi is the diaspora's most emotionally important destination — for weddings, pilgrimages, and last rites. The expanded airport, paired with Easy Connect, transforms the journey home.",
    "tags": ["travel", "airports", "Varanasi", "infrastructure", "pilgrimage", "aviation"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Impressive Times", "url": "https://impressivetimes.com/national/ram-mohan-naidu-pushes-for-early-completion-of-%E2%82%B92870-crore-varanasi-airport-terminal-project-varanasi-airport-new-terminal-expansion-ram-mohan-naidu/"},
        {"name": "Aviation Defence Universe", "url": "https://www.aviation-defence-universe.com/minister-naidu-reviews-new-varanasi-under-construction-terminal/"},
        {"name": "PMIndia.gov.in", "url": "https://www.pmindia.gov.in/en/news_updates/pm-lays-foundation-stone-and-inaugurates-multiple-development-projects-in-varanasi-uttar-pradesh/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-launches-easy-connect-service/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Shri_Kashi_Vishwanath_Temple_7.jpg/1280px-Shri_Kashi_Vishwanath_Temple_7.jpg",
    "image_caption": "The Kashi Vishwanath Temple in Varanasi, whose architecture inspires the new airport terminal design",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}

# ─────────────────────────────────────────────────
# Insert both articles
# ─────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
