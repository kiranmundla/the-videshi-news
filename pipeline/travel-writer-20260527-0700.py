#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-27 07:00 PDT batch"""

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

# ──────────────────────────────────────────────
# ARTICLE 1: Sri Lanka Free Tourist ETA
# ──────────────────────────────────────────────

article1_body = """As of May 25, Sri Lanka's free tourist ETA is live. Citizens of 40 countries — India, the United States, the United Kingdom, Canada, Australia, the UAE, Germany, France, Japan, China, and 30 others — can now apply for an Electronic Travel Authorization at zero cost. The scheme grants a 30-day stay with double entry, and it represents the most significant easing of Sri Lanka's border policy in years.

## What Changed

Sri Lanka's Cabinet approved the draft regulation on March 30. Parliament signed off on May 7 under the Immigration and Emigration Act. The Department of Immigration confirmed the operational start date in a circular dated May 19. The fee waiver runs for one year, with a six-month review to decide whether to continue.

The ETA itself isn't new — travelers to Sri Lanka have needed one for years. What's new is that the $50 processing fee has been eliminated for tourist visits. The application process remains the same: submit through [eta.gov.lk](https://eta.gov.lk) before departure, receive approval electronically, and present it at immigration on arrival.

Three countries that previously skipped the ETA entirely — the Maldives, Seychelles, and Singapore — now must use the system too, though their ETAs are also free. Maldivian travelers get a 90-day visa through the system under a bilateral reciprocity deal.

## Why NRIs Should Care

Indian passport holders were already receiving free ETA issuance under an existing arrangement, so the direct financial impact for Indian nationals is limited. The bigger shift is for NRI families with mixed-nationality households.

An Indian American couple planning a two-week South Asian circuit — say, a week in Kerala followed by a week on Sri Lanka's southern coast — previously faced different visa cost structures depending on which passport each person held. A US passport holder paid $50 for the Sri Lanka ETA; an Indian passport holder paid nothing. That gap is now closed. Both walk through immigration on the same terms.

The timing also matters. Sri Lanka's monsoon coast (the southwest) enters its dry season in November, but the east coast — Trincomalee, Passikudah, Arugam Bay — is at its best right now through September. For NRIs visiting family in South India this summer, a three-day detour to Sri Lanka's east coast just became cheaper and simpler for everyone in the travel party.

## The Numbers Behind the Policy

Sri Lanka's government estimates the free ETA could attract roughly 247,000 additional tourists and generate about $317 million in revenue, against a projected cost of $75 million in waived fees. The math is straightforward: every dollar not collected at the border is expected to return four dollars in hotel stays, meals, transport, and tours.

Tourism is Sri Lanka's most important foreign exchange earner after remittances, and the country's recovery from its 2022 economic crisis remains fragile. Arrival numbers have improved but haven't reached pre-pandemic levels. Officials believe the visa fee — small in absolute terms — still influenced destination choice for price-sensitive travelers comparing Sri Lanka against Thailand, Vietnam, or Bali.

## What to Know Before You Go

The free ETA covers tourist travel only. Business visas and other categories still carry fees. Extensions beyond 30 days are available but also cost extra. And one important detail: ETA fees paid before May 25 will not be refunded — the government has confirmed this explicitly.

For NRIs planning summer trips to South Asia, the practical takeaway is simple: if Sri Lanka wasn't on the itinerary because of paperwork friction, that excuse is gone. Colombo is a 90-minute flight from Chennai, two hours from Bangalore. The free ETA, combined with competitive hotel rates during the shoulder season, makes it one of the easiest add-ons to any India homecoming trip this summer.

*The official ETA portal is [eta.gov.lk](https://eta.gov.lk). Apply before departure — the fee is waived, but the authorization is not.*"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sri Lanka Just Dropped Its Visa Fee for 40 Countries — and NRI Families Stand to Gain the Most",
    "subheadline": "The free tourist ETA, live since May 25, eliminates a cost gap that made mixed-passport NRI households plan around two different border regimes.",
    "slug": make_slug("sri-lanka-free-eta-nri-families-mixed-passport"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families with US/UK/Canadian passport holders no longer face a cost split at Sri Lanka immigration — everyone enters free, making multi-country South Asia trips simpler to plan and budget.",
    "tags": ["travel", "sri-lanka", "visa", "eta", "nri", "south-asia"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "BudgetBro Blog", "url": "https://budgetbro.app/blog/sri-lanka-free-visa-scheme"},
        {"name": "Sri Lanka ETA Portal", "url": "https://eta.gov.lk"},
        {"name": "Lanka Websites Immigration Guide", "url": "https://lankawebsites.com"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Sigiriya_%28141688197%29.jpeg",
    "image_caption": "Sigiriya, Sri Lanka's ancient rock fortress — now accessible under a free tourist ETA for citizens of 40 countries including India and the United States.",
    "body": article1_body
}

# ──────────────────────────────────────────────
# ARTICLE 2: Akasa Air Expanding While Giants Cut
# ──────────────────────────────────────────────

article2_body = """While Air India slashes 22% of its domestic flights and IndiGo trims 7-10%, one Indian carrier is doing the opposite. Akasa Air — the three-year-old budget airline backed by late investor Rakesh Jhunjhunwala's estate — grew its flight operations by 13.2% in March and April 2026, adding routes and frequencies even as fuel costs forced its larger rivals into retreat.

The divergence is the most striking split in Indian aviation since the Jet Airways collapse of 2019. And for the 4.4 million NRIs who fly to India each year, the shakeout could reshape how the last leg of the homecoming works.

## The Numbers

Data from the Directorate General of Civil Aviation shows that in March-April 2026, India's major domestic airlines collectively reduced flights by nearly 6%. Air India Group — which includes Air India, Air India Express, and Vistara — cut capacity by up to 17.1%. IndiGo, which operates over 2,200 daily flights and controls roughly 60% of India's domestic market, trimmed 4.5-7% of planned services.

Akasa, by contrast, operated 10,109 flights during the same period, capturing 4.7% of domestic passenger traffic. For an airline that didn't exist before August 2022, that's a meaningful footprint — roughly the size that SpiceJet held before its financial spiral.

The cuts at the top aren't voluntary strategy; they're arithmetic. The Iran-driven disruption to the Strait of Hormuz has pushed jet fuel costs up by an estimated 50-60%, and fuel now accounts for up to 45% of Indian airlines' operating expenses. Air India, which just logged a record annual loss exceeding $2 billion, told Reuters it had "temporarily rationalised operations on certain domestic routes" and would restore frequencies "as conditions stabilise."

## Why Akasa Can Grow When Others Can't

The answer is fleet homogeneity. Akasa flies a single aircraft type: the Boeing 737 MAX. All 38 planes in its current fleet are identical, which means pilots, crews, maintenance teams, and spare parts are fully interchangeable. When one plane goes down for servicing, any other slot in the network can absorb the flight.

IndiGo and Air India, by contrast, manage fleets spanning Airbus A320s, A321neos, A350s, Boeing 777s, and 787 Dreamliners. That complexity introduces scheduling rigidity — you can't swap a widebody for a narrowbody on a tier-2 city route. When fuel costs force cuts, the big carriers have to trim entire route clusters rather than redistribute capacity.

Akasa also has 226 additional planes on order, a pipeline that signals confidence in long-term domestic growth even if the medium-term outlook is turbulent.

## What This Means for NRIs

For most NRIs, the India trip goes like this: a 16-18 hour long-haul flight to Delhi or Mumbai, followed by a 2-3 hour domestic connection to the actual hometown — Lucknow, Ahmedabad, Coimbatore, Vizag, Bhubaneswar. That second flight is where the domestic capacity cuts bite hardest.

When Air India pulls 22% of its domestic flights, it's not pulling the Delhi-Mumbai shuttle (too many business travelers). It's pulling the Delhi-Patna, Mumbai-Nagpur, Bangalore-Bhopal frequencies that NRIs depend on to reach tier-2 and tier-3 cities. Seats on remaining flights get scarce, fares spike, and the two-hour connection turns into a six-hour wait for the next departure.

Akasa's expansion into exactly these mid-market routes — it now serves 31 domestic destinations — creates an alternative. It won't replace Air India or IndiGo on the trunk routes, but on the spoke connections where NRIs feel the pinch most, more Akasa flights mean more options.

## The Risks

Akasa is growing into a headwind. The airline reported net losses of ₹1,983 crore (roughly $235 million) in the 2024-25 financial year. It's privately held, which limits scrutiny of its balance sheet but also limits access to public market capital. A prolonged fuel crisis could drain its cash reserves faster than growth fills them.

There's also the question of whether Akasa can sustain its load factors — the percentage of seats actually filled — as it adds flights. Expanding into a weak demand environment is a bet that competitors' cuts will redirect passengers your way. If demand softens further, those extra flights fly half-empty.

For now, though, the bet is working. In a season where India's two dominant carriers are shrinking, Akasa is the only airline with both the will and the fleet structure to grow. NRIs booking domestic connections this summer would do well to check Akasa's route map before defaulting to IndiGo — the scrappy upstart might have the seat the giants just gave up."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Akasa Air Is Growing While India's Aviation Giants Retreat — and NRIs Might Benefit Most",
    "subheadline": "As Air India cuts 22% of domestic flights and IndiGo trims 7-10%, the three-year-old budget carrier is expanding into exactly the mid-market routes NRIs depend on to reach home.",
    "slug": make_slug("akasa-air-growing-aviation-giants-retreat-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs connecting through Delhi or Mumbai to tier-2 cities are most exposed to domestic flight cuts — Akasa's expansion into 31 destinations offers an alternative on exactly those spoke routes.",
    "tags": ["travel", "airlines", "akasa-air", "air-india", "indigo", "nri", "domestic-flights"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"},
        {"name": "WhalesBook", "url": "https://www.whalesbook.com/news/English/transportation/Akasa-Air-Gains-Market-Share-as-Rivals-Cut-Flights-Amid-Geopolitical-Turmoil/6a143e2eb979113840ca0b93"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/aviation/atf-pinch-air-india-indigo-set-to-trim-domestic-operations-from-june"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Akasa_Air_737_max_8-200.jpg/3840px-Akasa_Air_737_max_8-200.jpg",
    "image_caption": "An Akasa Air Boeing 737 MAX — the airline's uniform fleet of 38 identical aircraft gives it scheduling flexibility that larger, mixed-fleet rivals can't match.",
    "body": article2_body
}

# ──────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted at {now}")
