#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-27 03:00 PDT batch"""

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


# ── ARTICLE 1 ────────────────────────────────────────────────────────

article1_body = """Your Indian passport ranks among the weakest in the world for visa-free access — 144th on the Henley Index as of early 2026, behind Iraq and barely ahead of Pakistan. But if you hold a valid US visa — an H-1B, an L-1, a B1/B2, even an F-1 — you are carrying a second passport that most NRIs never think to use.

As of this summer, a valid US visa unlocks entry to **55 countries** without applying for a separate visa. That list spans Latin America, the Caribbean, parts of Europe, the Middle East, and Southeast Asia. For Indian Americans planning summer travel, it is the single most underused perk sitting in your passport.

## The Headline Destinations

**Mexico** leads the list. A valid, *used* multiple-entry US visa gets you 180 days — six full months — on arrival. No appointment, no application, no fee beyond a modest immigration card charge. Cancún, Mexico City, Oaxaca, Tulum: all open. One critical caveat Indian travelers should note: Mexico has started enforcing a requirement that your US visa must have been previously **used** to enter the United States. An unused visa stamp will get you turned away. This is being enforced specifically for Indian, South Asian, and African passport holders.

**Costa Rica** grants 30 days, making it ideal for a quick summer rainforest trip. **Colombia** offers 90 days — Bogotá, Cartagena, and Medellín are all accessible. **Panama**, gateway to the Canal and some of Central America's best beaches, allows 30 days. **Turkey** offers 90 days with an e-visa that processes in minutes for US visa holders, opening up Istanbul and Cappadocia without the usual Turkish visa bureaucracy.

**Georgia** is the quiet star of the list. The former Soviet republic in the Caucasus grants Indian US-visa holders **one full year** of visa-free stay. Tbilisi's wine country, Black Sea coast, and mountain villages have turned it into a growing digital nomad hub — and increasingly, a weekend-trip option for NRIs based in Europe.

## The Caribbean and Beyond

Several Caribbean islands welcome Indians with US visas: **Aruba** (30 days), **Curaçao** (30 days), and **Bonaire** — all Dutch territories that accept a valid US visa in lieu of a separate Schengen or Caribbean visa. The **Dominican Republic** issues a tourist card on arrival. **Jamaica** grants 30 days. For NRI families eyeing a beach holiday that does not require another round of visa paperwork, the Caribbean is wide open.

In the Balkans, **Albania** offers 90 days visa-free, and **North Macedonia** grants 15 days with a valid US visa. **Serbia** allows 90 days within a 180-day period without any visa.

## What You Need to Know Before Boarding

The rules vary by country, but a few patterns hold across most destinations:

- Your US visa must be **multiple-entry** and **valid** for the duration of your stay. Single-entry or expired US visas will not work in most countries.
- Some countries — Mexico and Colombia in particular — now require that the US visa has been **used at least once** to enter the US.
- Carry proof of onward travel, hotel reservations, and sufficient funds. Immigration officers in developing countries occasionally ask for documentation even when none is technically required.
- An expired US visa in an old passport may still work in some countries (Mexico and Canada accept this) but will not in others. Check before you fly.

## Why This Matters Now

Summer 2026 is shaping up to be one of the most expensive in years for India-bound flights. Jet fuel prices have surged 70% since the Strait of Hormuz closure in February, and Air India and IndiGo have cut domestic schedules by up to 22%. For NRIs who planned a summer India trip but are sticker-shocked by $1,800 round-trip fares to Delhi, the US visa opens a Plan B that is cheaper, closer, and requires zero additional paperwork.

A round-trip to Cancún from any major US city runs $250–$400 in June. Costa Rica is under $500 from most hubs. Colombia sits around $350 from Miami or Houston. Against the backdrop of the most disrupted India corridor in a decade, these alternatives are not consolation prizes — they are legitimate summer options that your passport, on its own, would never allow.

The 55-country list keeps growing. France removed its transit visa requirement for Indian citizens earlier this year. The trend is clear: more countries are choosing to honor the screening that a US visa already represents. For 4.8 million Indian Americans, that is a travel unlock hiding in plain sight."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Your US Visa Unlocks 55 Countries — The NRI's Secret Weapon for Summer Travel",
    "subheadline": "Mexico for 180 days, Georgia for a full year, and the Caribbean without a single extra application — how Indian Americans can turn one visa stamp into a passport multiplier.",
    "slug": make_slug("us-visa-55-countries-nri-summer-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian passport holders rank 144th globally for visa-free access, but a valid US visa — held by millions of NRIs on H-1B, L-1, B1/B2, and F-1 — opens 55 additional countries. With India flights at record highs this summer, these alternatives offer cheaper, paperwork-free vacations.",
    "tags": ["travel", "visa", "nri", "summer", "mexico", "caribbean", "us-visa"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Visa Traveler", "url": "https://www.visatraveler.com/blog/travel-20-countries-visa-free-with-us-visa/"},
        {"name": "Atlys", "url": "https://atlys.com/post/countries-you-can-visit-with-us-visa-on-indian-passport"},
        {"name": "Passport Guide", "url": "https://www.passportguide.co/mexico-visa-for-indian-passport-holders/"},
        {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
    "body": article1_body
}


# ── ARTICLE 2 ────────────────────────────────────────────────────────

article2_body = """On February 28, the United States and Israel launched airstrikes on Iran. Within days, Tehran retaliated by effectively sealing the Strait of Hormuz — the 21-mile chokepoint between Oman and Iran through which one-fifth of the world's oil and gas had been flowing. Three months later, the strait remains functionally closed. And an NRI in New Jersey trying to book a July flight to Hyderabad is paying $400 more than last summer for the privilege.

The connection between a naval blockade in the Persian Gulf and the price of your Delhi ticket is not metaphorical. It is a supply chain, and it has broken.

## Twenty Percent of the World's Jet Fuel, Gone

Before the crisis, roughly 20% of the global jet fuel supply passed through or originated near the Strait of Hormuz. When the strait closed, that fuel did not simply reroute — it vanished from the accessible market. Kerosene refined from oil is now **70% more expensive** than it was before February 28, according to Le Monde's analysis of aviation fuel markets. The International Energy Agency has revised its global oil demand forecast downward by 1.3 million barrels per day from its pre-conflict projection, forecasting an outright contraction of 420,000 barrels per day for 2026.

For airlines, fuel typically accounts for 25–30% of operating costs. When that input doubles, the math gets ugly fast.

## The Cascade Hits India Hardest

India's aviation sector sits at the worst possible intersection of this crisis. Pakistani airspace remains closed to Indian carriers — a restriction that predates the Iran war but compounds it. Gulf hubs that NRIs have relied on for decades — Dubai, Abu Dhabi, Doha — saw traffic plunge by as much as **65%** as the conflict intensified. Emirates, the largest Gulf carrier, has clawed back to 96% of its pre-disruption network, but capacity remains below normal.

Air India, still absorbing its Tata Group restructuring, recorded an annual loss exceeding **$2 billion**. In response, it is cutting domestic flights by 22% for June and July. IndiGo, India's largest carrier, is scaling back domestic operations by up to 7%. Both have introduced fuel surcharges: IndiGo's international surcharge has climbed by up to ₹10,000 per ticket.

The cuts to domestic flights create a secondary problem for NRIs. Even if your international leg is on time, the connecting flight from Mumbai or Delhi to your hometown may not exist anymore — or may cost three times what it did last year.

## The Rerouting Has Begun

The global fuel supply chain is slowly adapting. In a milestone reported by Reuters in late May, Northeast Asian refiners shipped the first jet fuel cargo to Europe since the crisis began — a sign that alternative supply routes are forming, even if they are longer and more expensive.

Delhi and Maharashtra have cut their state-level Value Added Tax on aviation turbine fuel to 7%, an attempt to cushion airlines operating from India's two busiest airport regions. The relief is modest — ATF taxes have long been a sore point for Indian carriers — but it signals that state governments recognize the crisis is structural, not seasonal.

Travelers, meanwhile, are rerouting themselves. Cathay Pacific, Singapore Airlines, and Korean Air have all reported surging demand on routes that bypass the Middle East entirely. The Asia-to-Europe corridor through Southeast Asian hubs is seeing some of its strongest booking numbers in years.

## What NRIs Should Expect This Summer

The honest answer: elevated fares through at least September. Even if Iran and the US reach a deal — and talks are reportedly progressing — analysts expect months of lag before oil flows normalize, damaged infrastructure is repaired, and fuel prices recede.

In early May alone, more than **12,000 flights** were cancelled globally due to fuel supply disruptions. Long-haul routes are the most vulnerable because they burn more fuel and are more exposed to the international supply chain.

For NRIs planning summer India trips, a few practical realities: book early and lock in fares rather than waiting for drops that may not come; consider routing through Singapore, Hong Kong, or Tokyo rather than Dubai or Doha; watch for Delhi and Maharashtra's tax cuts to marginally reduce fares on domestic legs; and budget for the surcharges — they are not going away until crude drops below $80 a barrel, which no major forecaster currently expects before autumn.

The war in the Gulf is not a travel inconvenience. It is a structural repricing of the NRI's most important aviation corridor. Understanding the supply chain behind it is the first step toward navigating it."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "How a War in the Persian Gulf Raised Your India Ticket by $400",
    "subheadline": "The Strait of Hormuz closure wiped 20% of the world's jet fuel off the market. Three months later, the supply chain is still broken — and NRIs are paying the price on every leg home.",
    "slug": make_slug("gulf-war-jet-fuel-india-flight-prices-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs rely on Gulf carrier hubs and India's domestic network for the last-mile home. The Hormuz closure, Pakistan airspace ban, Air India's $2B loss, and IndiGo's ₹10,000 surcharges have structurally repriced the corridor that 4.8 million Indian Americans depend on.",
    "tags": ["travel", "airlines", "fuel-crisis", "nri", "air-india", "indigo", "hormuz"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Air India domestic cuts", "url": "https://www.reuters.com/business/aerospace-defense/air-india-cuts-june-july-domestic-flights-by-22-due-high-jet-fuel-prices-source-2026-05-26/"},
        {"name": "Le Monde — Aviation fuel crisis", "url": "https://www.lemonde.fr/en/economy/article/2026/05/22/french-airlines-are-finally-turning-to-sustainable-fuels-to-break-free-from-fossil-fuel-dependence_6771234_19.html"},
        {"name": "Reuters — Northeast Asia jet fuel shipment", "url": "https://www.reuters.com/business/energy/northeast-asia-ships-first-jet-fuel-europe-since-iran-war-sources-say-2026-05-23/"},
        {"name": "Streamline — Global aviation fuel crisis", "url": "https://streamlinefeed.co.ke/global-aviation-faces-turbulence-as-iran-crisis-reshapes-fuel-costs/"},
        {"name": "Outlook Business — ATF VAT cuts", "url": "https://www.outlookbusiness.com/amp/corporate/atf-pinch-air-india-indigo-set-to-trim-domestic-operations-from-june"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1036866/pexels-photo-1036866.jpeg",
    "body": article2_body
}


# ── ARTICLE 3 ────────────────────────────────────────────────────────

article3_body = """Every June, the same conversation plays out in NRI group chats across America: where do we go for summer? India is the default, but monsoon season, punishing domestic fares, and the 18-hour slog through a disrupted Gulf corridor are making the calculus harder this year. Goa is waterlogged by mid-June. Delhi is 45°C until the rains arrive. And a round-trip SFO-DEL ticket currently starts at $1,600.

Meanwhile, Cancún is a four-hour flight from Houston, the water is 28°C, and your US visa is all the paperwork you need. Indian Americans are discovering what Mexican immigration policy quietly made possible years ago — and the numbers are starting to show it.

## The Visa Hack That Changes Everything

India requires visas from citizens of most countries. Mexico does the opposite for anyone holding a US visa. With a valid, previously used, multiple-entry US visa — the standard H-1B or B1/B2 that millions of Indian Americans carry — Mexico grants **180 days** on arrival. No appointment. No application fee. No interview. You land, show your passport and US visa, get your immigration card stamped, and walk out into the Caribbean sun.

The same principle extends across Mexico's Caribbean coast. Riviera Maya, Tulum, Playa del Carmen, Cozumel — all accessible under the same entry. And because Mexico has no separate tourist visa application for US visa holders, you can book a flight tonight and leave tomorrow.

One caveat that catches Indian travelers: Mexico has begun enforcing a rule that the US visa must have been **used** to enter the United States at least once. An unused visa — even if valid — may result in denial at the Mexican border. This enforcement is specifically targeting Indian, South Asian, and African passport holders. If your visa is fresh, enter the US first before planning Mexico.

## What Cancún Offers That Goa Cannot (Right Now)

Goa in the monsoon is a particular experience — lush, dramatic, and increasingly marketed as an off-season draw. But for families with school-age children on a two-week summer break, the calculus favors Cancún on nearly every metric this year.

**Cost**: A round-trip flight from Dallas, Houston, Chicago, or the Bay Area to Cancún runs $250–$450 in June. All-inclusive resorts in the Hotel Zone start at $150/night for a family of four. A comparable Goa trip, once you add the international flight, domestic connector, and resort costs, runs three to four times as much this summer.

**Weather**: Cancún averages 31°C in June with afternoon thunderstorms that clear within an hour. Humidity is high but manageable with sea breeze. By contrast, much of India is either pre-monsoon furnace (Delhi, Rajasthan) or actively monsoon-drenched (Mumbai, Goa, Kerala) by mid-June.

**Food**: This is where skeptics raise an eyebrow, but Cancún's food scene has evolved. The Hotel Zone has a growing number of Indian restaurants catering to the rising flow of South Asian tourists. Supermarkets carry rice, lentils, and spices. And Mexican cuisine — rice-and-bean based, heavy on cilantro and lime, generous with chili — is closer to Indian palates than most NRIs expect.

## Safety: The Honest Assessment

Mexico's overall travel advisory sits at Level 2 — "exercise increased caution" — due to crime concerns. But Cancún and the wider Quintana Roo state operate under significantly enhanced security. The tourist corridor, particularly the Hotel Zone and Riviera Maya, maintains a visible military and police presence. The State Department does not advise against travel to these areas.

Common sense applies: stay in well-trafficked tourist zones, avoid isolated roads at night, use authorized taxis and hotel transport, keep valuables in the room safe. The risk profile is comparable to many popular NRI vacation destinations — arguably lower than parts of India that travelers navigate routinely.

## Beyond Cancún: The Wider Mexican Caribbean

Cancún is the entry point, but the Yucatán Peninsula offers weeks of travel without leaving the region. **Tulum** delivers boutique hotels and Mayan ruins overlooking the sea. **Playa del Carmen** is walkable, family-friendly, and cheaper than the Hotel Zone. **Cozumel**, a 45-minute ferry ride, has some of the best snorkeling in the Western Hemisphere. **Mérida**, the colonial capital of the Yucatán, offers food markets, hacienda tours, and cenote swimming with none of the resort-town markup.

For NRIs with more time, **Mexico City** is a five-hour bus ride or short flight — and it is one of the world's great food cities, with a cost of living that makes Mumbai look expensive.

## The Bottom Line

Nobody is arguing that Cancún replaces a trip home. The pull of family, festivals, and familiar streets is not something a beach resort replicates. But for NRI families looking at a summer window that does not align with an India trip — whether because of cost, weather, or the sheer exhaustion of a disrupted Gulf corridor — Mexico's Caribbean coast is an option that requires nothing more than the visa already in your passport.

Four hours from Texas. Six from New York. No forms, no fees, no appointment. Just blue water and 180 days of welcome."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Cancún for Desis: Why NRIs Are Trading Goa for Mexico's Caribbean This Summer",
    "subheadline": "A four-hour flight, 180 days visa-free on your US visa, and resorts at a third of what a monsoon-season Goa trip costs — the Mexican Caribbean is becoming the NRI's Plan B.",
    "slug": make_slug("cancun-desis-nri-mexico-caribbean-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "With India flights at record highs and monsoon season narrowing the domestic travel window, Indian Americans with US visas can enter Mexico for 180 days — making Cancún and the Riviera Maya a cheaper, closer, and paperwork-free summer alternative to Goa.",
    "tags": ["travel", "mexico", "cancun", "nri", "caribbean", "summer", "visa-free"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World — Mexico Travel Advisory", "url": "https://www.travelandtourworld.com/news/article/mexico-travel-alert-2026/"},
        {"name": "Visa Traveler — 55 countries with US visa", "url": "https://www.visatraveler.com/blog/travel-20-countries-visa-free-with-us-visa/"},
        {"name": "Passport Guide — Mexico visa for Indians", "url": "https://www.passportguide.co/mexico-visa-for-indian-passport-holders/"},
        {"name": "US State Department — Mexico Travel Advisory", "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/mexico-travel-advisory.html"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/506810/pexels-photo-506810.jpeg",
    "body": article3_body
}


# ── PUBLISH ──────────────────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted at {now}")
