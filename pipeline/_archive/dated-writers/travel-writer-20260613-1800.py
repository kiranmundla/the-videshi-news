#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-13 18:00 UTC batch"""

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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Dubai's Visa Overhaul Means 48-Hour Approvals and Expanded Golden Visas — Here's What NRIs Need to Know",
        "subheadline": "From faster tourist visas to a wider Golden Visa net that now covers educators, content creators, and e-sports professionals, the UAE just made it significantly easier for Indians to visit, work, and invest in Dubai.",
        "slug": make_slug("dubai-visa-overhaul-48-hour-golden-visa-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With 3.5 million Indians forming the largest expatriate community in the UAE, every visa rule change in Dubai ripples directly through the Indian American diaspora — from family visits to property investments to career moves.",
        "tags": ["travel", "dubai", "visa", "golden visa", "uae", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Jagran Josh", "url": "https://www.jagranjosh.com/general-knowledge/dubai-visa-rules-2026-golden-visa-expansion-and-10-major-changes-1749731168-1"},
            {"name": "Time Out Dubai", "url": "https://www.timeoutdubai.com/news/9-important-dubai-visa-updates-to-know-in-2026"},
            {"name": "Dubai Standard", "url": "https://www.dubaistandard.com/dubai-tourist-visa-48-hours"},
            {"name": "Travel Man Today", "url": "https://www.travelmantoday.com/dubai-tourist-visa-2026"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19612315/pexels-photo-19612315.jpeg",
        "image_caption": "Dubai Marina waterfront with luxury yachts and skyscrapers in morning light",
        "image_attribution": "Pexels",
        "body": """Planning a Dubai trip used to mean waiting a week or more for visa approval, mentally budgeting for processing delays, and hoping your paperwork didn't get stuck in a queue. That calculus has changed.

Dubai's General Directorate of Residency and Foreigners Affairs (GDRFA) has confirmed that single-entry tourist visas — available for either 30 or 60 days — are now being processed within 48 working hours of document submission. Applications go through accredited tourism offices, UAE airlines like Emirates, Etihad, and flydubai, or approved visa portals. The requirements remain straightforward: a valid passport, a personal photograph, and for some nationalities, a national ID card.

For the millions of Indians who visit Dubai annually — whether for family reunions, shopping trips, or monsoon-season escapes — the faster turnaround eliminates what was often the most stressful part of trip planning. Travel agents in Dubai report that inquiries surged immediately after the announcement, particularly from the Indian subcontinent. "People have been asking about the process after reading the news," said Subair Thekepurathvalappil of Wisefox Tourism. "In many cases, travellers can expect to receive their visas within a day."

## The Golden Visa Gets Wider

The more consequential shift may be in the Golden Visa programme. The UAE's coveted 10-year self-sponsored residency — which previously catered mainly to investors and high-net-worth individuals — has been expanded to cover a significantly broader talent pool. New eligible categories include senior nurses, educators and teachers, content creators, digital artists, e-sports professionals, and prominent charity donors.

For Indian professionals in these fields, the implications are substantial. A teacher in Texas with a decade of experience or a digital content creator in the Bay Area can now secure long-term UAE residency without needing a local employer or corporate sponsor. The Golden Visa also remains exempt from the 180-day absence rule — holders can stay abroad for years without losing their residency status, unlike standard UAE visa holders whose residency lapses after six months away.

## Longer Safety Nets for Workers

Dubai has also tripled the grace period for job loss from 30 to 90 days. Under the old rules, losing a job in the UAE meant scrambling to find a new position or leave the country within a month. The expanded window gives workers — a disproportionate share of whom are Indian — three months to secure new employment, wrap up affairs, or negotiate transfers, without falling into legal limbo.

The zero-tolerance overstay policy, however, remains firmly in place: AED 50 per day for the first year, escalating to AED 100 per day thereafter, with automated absconding flags. The carrot is bigger, but the stick hasn't gotten softer.

## What This Means for Indian Americans

For NRIs who treat Dubai as a second home — and there are many — the changes are practical and immediate. Parents visiting children working in the Gulf can get visa approval in two days instead of a week. Professionals eyeing Dubai as a tax-free base can now qualify through the expanded Golden Visa without massive property investments. And the 90-day job-loss grace period provides a cushion that was badly needed in a region where employment law has historically favoured employers.

Dubai's summer season, often dismissed as too hot for tourists, is being actively repackaged with lower hotel rates, seasonal promotions, and fewer crowds. The faster visa processing is timed to capture exactly this demand — particularly from India, where monsoon season drives an annual exodus of travelers to drier, air-conditioned destinations.

The visa changes also arrive against the backdrop of regional instability, with Middle East airspace disruptions from the Iran-Israel conflict having rattled travel plans in recent months. Dubai's aggressive visa streamlining reads partly as a confidence signal: the emirate is betting that convenience and accessibility will outweigh geopolitical caution for most travelers. For the Indian diaspora, which has deep roots in the Gulf, that bet is probably right."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Drops Visa Requirements for Indian Travelers — and NRIs Should Book Before the Crowds Do",
        "subheadline": "A new 15-day visa-free entry for Indian passport holders puts Thailand alongside Malaysia, Singapore, and Vietnam in a growing list of countries actively courting Indian tourists with no-paperwork arrivals.",
        "slug": make_slug("thailand-visa-free-indian-travelers-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Thailand has long been the default getaway for Indian families — cheap flights, familiar food, and a culture that feels accessible. Visa-free entry removes the last friction point for NRIs planning a quick Southeast Asian trip between US visits home.",
        "tags": ["travel", "thailand", "visa-free", "indian passport", "southeast asia", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/thailand-joins-russia-malaysia-china-singapore-philippines-vietnam-taiwan-visa-free-indian-travellers/"},
            {"name": "Wikipedia - Visa Requirements for Indian Citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12390403/pexels-photo-12390403.jpeg",
        "image_caption": "Aerial view of a traditional Thai temple near the coastline with turquoise sea",
        "image_attribution": "Pexels",
        "body": """For years, the Thailand visa process for Indian passport holders was a minor but reliable annoyance — a trip to the embassy, a stack of documents, or at best a visa-on-arrival that still required paperwork and fees at Suvarnabhumi. That era is over.

Thailand has announced a 15-day visa-free entry for Indian nationals, effective immediately. Indian passport holders can now land in Bangkok, Phuket, Chiang Mai, or Krabi without any prior visa application, walk through immigration, and start their trip. The policy is for tourism purposes and covers stays of up to 15 days.

The move places Thailand alongside an expanding roster of countries that have eliminated visa requirements for Indians: Malaysia, Singapore, the Philippines, Vietnam, Taiwan, and Russia (which offers an eVisa with streamlined processing). It signals a clear strategic bet by Southeast Asian governments that the Indian outbound travel market — one of the world's fastest-growing — is worth competing for.

## Why Thailand Made the Move

The numbers tell a direct story. India has been one of Thailand's fastest-growing source markets for several years, driven by a large millennial and Gen Z population, rising disposable incomes, and a cultural appetite for the kind of experiences Thailand delivers — from street food crawls in Bangkok to beach weeks in the Andaman coast.

Thai authorities are counting on the visa-free policy to convert interest into action. The expected outcomes are longer stays, higher spending on premium experiences, repeat visits, and a surge in the destination wedding market, which has become a significant revenue stream. Indian couples have increasingly chosen Phuket, Krabi, and Koh Samui over traditional domestic options, drawn by the combination of stunning venues, affordable luxury, and easy logistics.

By removing the visa barrier, Thailand is essentially telling Indian travelers: stop overthinking and just book the flight.

## What NRIs Should Know

For Indian Americans holding Indian passports, the visa-free entry is particularly useful for the spontaneous side trip. Flying home to Delhi or Mumbai for a family visit? A 15-day Thailand detour now requires zero advance planning — no embassy visit, no e-visa application, no waiting period. Just a passport and a return ticket.

The timing is also significant. With Middle East airspace disruptions affecting routes through Dubai and Doha, many NRIs flying between the US and India are routing through Southeast Asian hubs like Bangkok and Singapore. A forced layover in Bangkok that previously required a visa headache is now just a layover — or an invitation to extend it into a few days on the beach.

## The Broader Visa-Free Trend

Thailand's move is part of a larger pattern. Over the past 18 months, the number of countries offering visa-free or simplified entry for Indian passport holders has grown substantially. Sri Lanka recently eliminated tourist visa fees for Indians entirely. South Africa introduced a streamlined digital ETA. The Philippines extended visa-free stays. And Russia has been aggressively expanding its eVisa programme with India as a priority market.

For Indian Americans who hold both a US passport and an Indian passport, the calculation is worth revisiting. Many NRIs default to traveling on their US passport, which offers visa-free access to more than 180 countries. But for countries like Thailand that now offer visa-free entry to Indian passport holders specifically, the distinction matters less — and using the Indian passport can sometimes simplify entry requirements for countries that have specific agreements with India.

## Practical Details

The 15-day visa-free window is strictly for tourism. Business travel, work, or extended stays still require the appropriate visa category. Travelers must have a confirmed return ticket and sufficient funds for their stay. The policy does not automatically extend to land border crossings — it applies at international airports.

For NRIs planning a summer trip, the window is wide open. Bangkok's monsoon season (June through October) brings brief afternoon downpours but also lower prices, fewer crowds, and a lush green landscape that photographers prize. A week in Chiang Mai's hill country followed by a few days on Koh Samui is now a trip that requires nothing more than a booking confirmation and a passport."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
