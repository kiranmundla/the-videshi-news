#!/usr/bin/env python3
"""Travel writer — 2026-06-08 02:56 PDT run. Two articles."""

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


# ── Article 1 ──────────────────────────────────────────────────────────────

art1_body = """The World Meteorological Organization has put the probability of El Niño developing through June and July at 80 to 90 percent, with conditions expected to peak between November and January. Sea-surface temperatures in the equatorial Pacific have already crossed the critical 0.5°C threshold that typically precedes the phenomenon's onset. For NRIs planning fall trips to India — Navratri, Diwali, wedding season, year-end family visits — the timing could not be worse.

## What El Niño Does to India Travel

El Niño and the Indian monsoon have a well-documented adversarial relationship. When El Niño strengthens, the monsoon weakens or turns erratic. The India Meteorological Department is already tracking a rapid transition from neutral conditions toward a clear El Niño pattern in the Pacific. While atmospheric responses typically lag the oceanic signals by weeks, the direction is unmistakable.

For India, this means the monsoon's second half — August through September — could deliver less rainfall than normal across central and peninsular India, or dump it unevenly. Either scenario creates problems. Drought conditions hit agriculture and water supply in popular travel regions. Erratic bursts trigger flash floods and landslides in the Western Ghats and Himalayan foothills, precisely where NRIs tend to take domestic side-trips.

The Hindu Business Line reported on June 6 that the equatorial Pacific has "transitioned rapidly from neutral conditions towards a clear El Niño pattern," with international agencies converging on an 80-90 percent likelihood through the summer months.

## The Southeast Asian Side-Trip Risk

El Niño does not stop at India's borders. Thailand, Vietnam, the Philippines, and Indonesia — popular stopovers and vacation add-ons for NRIs routing through Singapore, Bangkok, or Kuala Lumpur — face their own disruptions. The WMO's latest assessment flags intensified heatwaves and altered storm tracks across the region. Tour operators in Southeast Asia are already building flexible booking policies and contingency itineraries for the second half of 2026.

If you were planning a Bali extension after Diwali in India or a Vietnam detour on the way home, factor in the possibility of typhoon diversions, flash flooding in low-lying coastal areas, and extreme heat advisories that could shut down outdoor activities.

## What NRIs Should Do Now

**Book flexible fares.** If you haven't locked in Diwali-season tickets yet, prioritize airlines offering free changes or credits. Air India, United, and Emirates all have flexible fare classes for the peak October-November corridor. The extra $50-100 per ticket is insurance against a weather-disrupted itinerary.

**Avoid hill station drives during peak monsoon weeks.** Landslide risk on roads to Shimla, Manali, Ooty, Munnar, and Coorg spikes during erratic monsoon bursts. If your India visit includes September or early October, keep mountain excursions loose and cancellable.

**Check travel insurance fine print.** Standard policies rarely cover weather-related delays unless flights are formally cancelled. Look for policies that include "trip interruption" and "travel delay" benefits triggered by government-issued weather advisories, not just airline cancellations.

**Watch IMD bulletins, not just your weather app.** The India Meteorological Department issues region-specific monsoon forecasts that are far more granular than what shows up on Google Weather. Bookmark their website or follow their official channels in the weeks before travel.

**Consider January instead.** If your dates are flexible, pushing an India trip to January or February sidesteps monsoon tail risks and El Niño's peak disruption window entirely. Post-Makar Sankranti weather across most of India is consistently excellent for travel.

El Niño's last significant appearance in 2023-24 contributed to a deficient monsoon in parts of India and amplified heatwaves across South and Southeast Asia. The 2026 episode, if it develops as forecast, arrives against a backdrop of already-rising global temperatures — a combination that SBI's research team has flagged as a risk to food prices and energy availability in India. For NRI families planning the annual pilgrimage home, the smartest move right now is flexibility."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "El Niño Is Coming Back — and It Could Wreck Your Fall India Trip",
    "subheadline": "The World Meteorological Organization puts the odds at 80-90 percent. Here's what NRIs booking Diwali-season flights should know before it's too late to change plans.",
    "slug": make_slug("el-nino-2026-fall-india-trip-nri-travel-planning"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Fall is peak NRI travel season — Navratri, Diwali, weddings, year-end family visits. El Niño threatens monsoon disruptions, landslides, and erratic weather precisely when 2M+ Indian Americans are booking India flights.",
    "tags": ["travel", "el-nino", "monsoon", "weather", "diwali", "flight-planning"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "World Meteorological Organization", "url": "https://wmo.int"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/agri-business/monsoon-advances-even-as-el-ni%C3%B1o-signals-strengthen/article69653025.ece"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/india-joins-thailand-vietnam-china-philippines-indonesia-and-more-as-el-nino-2026-sparks-tourism-disruptions/"},
        {"name": "SBI Research Report", "url": "https://www.thehindubusinessline.com/economy/weather-risks-from-possible-el-nino-and-global-tensions-could-pressure-inflation-in-2026-sbi-report/article69230710.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/34140357/pexels-photo-34140357.jpeg",
    "image_caption": "Planes on a rain-soaked runway at Thiruvananthapuram airport during monsoon season",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────────

art2_body = """Summit Hotels & Resorts has launched The Mandir Collection, positioning it as India's first hospitality brand built entirely around temple-circuit travel. The debut property — Summit Salasar, in the Rajasthan town synonymous with the Salasar Balaji Temple — will feature 70 keys, including luxury villas with private pools, Satvik dining, dedicated temple visit assistance, curated wellness itineraries, and evening devotional gatherings. It is a deliberate bet on a market that has exploded in size but barely changed in hospitality quality.

## The Gap No One Was Filling

India's spiritual tourism sector has been growing at roughly 15-20 percent annually, fueled by the Ram Mandir opening in Ayodhya, record footfalls at Vaishno Devi and Tirumala, surging Char Dham yatra numbers, and the government's sustained investment in pilgrimage infrastructure. The IRCTC runs dedicated temple-circuit trains. State tourism boards market spiritual corridors aggressively. Airlines have added capacity to Varanasi, Tirupati, and Amritsar.

But the accommodation has not kept pace. At most major pilgrimage sites, the choice remains binary: spartan dharamshalas with shared facilities, or generic business hotels that happen to be located nearby. Neither is designed for the pilgrimage experience. A family completing the Char Dham circuit wants Satvik food, proximity to morning aarti schedules, and space for elderly members to rest — not a hotel bar and a buffet timed for corporate guests.

The Mandir Collection is designed to sit squarely in that gap. The Salasar property will feature dedicated assistance for temple visits and rituals, curated wellness itineraries that align with the spiritual rhythm of the destination, and large event spaces for community gatherings and ceremonies. It is positioned as a retreat, not just a hotel.

## Why NRIs Should Pay Attention

For the Indian American diaspora, the annual or biennial temple trip is a fixture. It is often multigenerational — grandparents, parents, and children traveling together — and the logistics of finding accommodation that works for everyone has always been the most painful part of the planning.

The elderly need accessible rooms, vegetarian kitchens, and quiet spaces for prayer. Children need air conditioning, clean water, and a pool. Working-age adults need Wi-Fi and a semblance of comfort after a long-haul flight. At most pilgrimage destinations, satisfying all three groups simultaneously has meant renting an entire guesthouse or staying uncomfortably far from the temple.

A branded, luxury temple-stay chain changes the calculus entirely. If The Mandir Collection executes on its promise — and expands beyond Salasar to the dozen-odd mega-pilgrimage sites that NRI families most frequently visit — it could become the default booking for diaspora temple trips the way Taj and Oberoi are defaults for wedding and leisure travel.

## The Business Case Is Obvious

India's domestic hotel market is on a tear. IHCL, the country's largest hotel company by room count, posted record revenue of ₹9,689 crore and profit of ₹2,247 crore in FY26. The Leela saw profit surge eightfold. ITC Hotels reported a 29 percent jump in profit after tax. Lemon Tree grew revenue 13 percent.

The spiritual tourism sub-segment, however, has been almost entirely served by unbranded, unorganized properties — dharamshalas, ashram guesthouses, and local hotels without standardized quality. That represents both an enormous greenfield opportunity and a category that branded chains have historically avoided because of the operational complexity: Satvik kitchens, temple-aligned scheduling, devotional programming, elder-friendly design.

Summit's willingness to build a dedicated brand around these requirements signals that the economics have shifted. Spiritual tourism is no longer a niche add-on to India's hospitality story — it is a standalone market large enough to support a branded chain.

## What Comes Next

The Mandir Collection's success will depend on expansion speed and site selection. Salasar is significant regionally, but the real prize is the tier-one pilgrimage circuit: Varanasi, Tirupati, Haridwar-Rishikesh, Amritsar, Puri, Shirdi, Somnath, Mathura-Vrindavan. If Summit can secure properties near even half of these destinations within the next three to four years, it will have built the first national hospitality network designed specifically for India's largest and most underserved travel segment.

For NRIs planning their next temple trip home, the arrival of luxury pilgrimage stays is overdue. The days of choosing between devotion and comfort may finally be numbered."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Temple Circuit Gets Its First Luxury Hotel Chain — and NRI Families Are the Target Market",
    "subheadline": "Summit Hotels launches The Mandir Collection with a 70-key retreat in Salasar, Rajasthan. Satvik dining, private pool villas, and temple visit concierges included.",
    "slug": make_slug("mandir-collection-luxury-temple-hotel-nri-pilgrimage"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Multigenerational temple trips are a staple of NRI family travel. The gap between dharamshalas and generic luxury hotels has forced diaspora families to compromise on comfort or proximity. A branded pilgrimage hospitality chain changes that calculus.",
    "tags": ["travel", "hotels", "spiritual-tourism", "pilgrimage", "rajasthan", "luxury"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/hotels/summit-hotels-resorts-enters-spiritual-tourism-with-launch-of-the-mandir-collection"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/india-hotel-companies-growth-fy26-travel-disruptions-ihcl-eih-itc-hotels-lemon-tree-leela-11749307685488.html"},
        {"name": "Travel+Leisure Asia", "url": "https://www.travelandleisureasia.com/in/hotels/new-hotels-in-india-2026/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/35394622/pexels-photo-35394622.jpeg",
    "image_caption": "A white marble temple in Rajasthan under a serene sky",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── Insert ─────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
