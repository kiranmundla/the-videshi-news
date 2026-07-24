#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-09 22:00 UTC run."""

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


# ─────────────────────────────────────────────────────────────
# Article 1: Noida International Airport Opens June 15
# ─────────────────────────────────────────────────────────────

article1_body = """India's newest commercial airport is six days from takeoff. Noida International Airport at Jewar — the country's largest greenfield airport, built from scratch on the plains of Gautam Buddha Nagar — will begin commercial operations on June 15, with IndiGo operating the inaugural flight. Air India Express and Akasa Air will follow within days.

## What's Opening

Phase 1 delivers a single 3,900-metre runway capable of handling the world's largest widebody jets, a 12-million-passenger terminal, and a multimodal cargo hub engineered for 100,000 tonnes a year. The airport operates under IATA code DXN and ICAO code VIND, run by Yamuna International Airport Private Limited, a subsidiary of Zurich Airport International AG. PM Modi inaugurated the facility on March 28; the DGCA granted its aerodrome licence earlier that month.

Initial domestic routes will connect Jewar to Bengaluru, Hyderabad, Kolkata, and Mumbai — four cities that collectively house the largest pockets of the NRI diaspora when it comes to onward connections to the US, UK, and Gulf.

## The NCR Bottleneck It's Meant to Fix

Indira Gandhi International Airport handled roughly 73 million passengers in FY25, straining against its design capacity. For the 4.5 million NRIs who route through Delhi-NCR each year — arriving on Air India from Newark, United from San Francisco, or Emirates via Dubai — IGI's congestion has been a perennial pain point. Noida International is designed as the pressure valve: a second airport within the National Capital Region, 75 kilometres southeast of IGI, positioned to absorb domestic feeder traffic and eventually international services.

The Yamuna Expressway already connects the terminal to Greater Noida and Agra. A 750-metre link road from the terminal to the expressway is complete. And for the longer term, the government has started a feasibility study for an underground tunnel connecting Jewar directly to IGI Airport and Gurugram — a project that, if built, would allow passengers to transfer between the two airports without navigating Delhi's surface roads.

## The CEO Clearance Drama

There is, however, a hitch. The airport's operating company is headed by Christopher Schnellmann, a Swiss national. India's Ministry of Home Affairs has reportedly refused to grant security clearance to a foreign CEO for a greenfield airport — and rejected Uttar Pradesh's request to waive the requirement. The Bureau of Civil Aviation Security certification, which depends on that clearance, remains pending. State officials are banking on Chief Minister Yogi Adityanath to escalate the matter to Home Minister Amit Shah. Whether this gets resolved before June 15 will determine if the launch date holds or slips.

## What NRIs Should Watch

For diaspora travellers, Noida International matters in two ways. First, it immediately improves domestic connectivity for anyone visiting family in western UP, Agra, or the NCR corridor — no more fighting IGI's traffic to catch an internal flight to Hyderabad or Bengaluru. Second, international routes are coming. IndiGo has publicly stated it will use Jewar for its expanding long-haul network, including A321XLR services to destinations like Bali, Athens, and Istanbul. Once international operations begin — likely in Phase 2, targeted for 2028 — NRIs flying into Delhi will have a genuine choice between two airports for the first time.

The terminal architecture is designed around a net-zero emissions framework, with natural light, energy-efficient systems, and provisions for a future high-speed rail link to Delhi and Varanasi that would cut transit time to 21 minutes. The full build-out envisions 70 million annual passengers by 2040 and, at completion, the fourth-largest airport in the world by area.

Six days out, the runway is ready. The terminal is ready. The airlines are ready. The only question is whether Delhi's bureaucracy can clear a Swiss passport faster than Zurich Airport can clear a boarding gate."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Newest Airport Opens Next Week — and It Could Change How NRIs Get Home",
    "subheadline": "Noida International at Jewar launches commercial flights on June 15, giving Delhi-NCR its first dual-airport system and a second gateway for the diaspora.",
    "slug": make_slug("noida-jewar-airport-opens-june-15-nri-gateway"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs routing through Delhi-NCR gain a second airport option with less congestion, better domestic connections, and future international routes — plus a planned tunnel link to IGI for seamless transfers.",
    "tags": ["travel", "airports", "infrastructure", "delhi", "noida", "indigo"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wikipedia — Noida International Airport", "url": "https://en.wikipedia.org/wiki/Noida_International_Airport"},
        {"name": "Curly Tales", "url": "https://curlytales.com/india/trending/delhi-noida-airports-may-soon-be-connected-by-a-tunnel-heres-what-we-know/"},
        {"name": "Magicbricks — Jewar Airport", "url": "https://www.magicbricks.com/blog/jewar-airport-noida/128218.html"},
        {"name": "Whispers in the Corridors", "url": "https://whispersinthecorridors.in/up-government-not-able-to-start-the-noida-international-airport/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
    "image_caption": "PM Modi at the inauguration of Noida International Airport at Jewar in March 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ─────────────────────────────────────────────────────────────
# Article 2: National Parks Road Trip Guide for NRI Families
# ─────────────────────────────────────────────────────────────

article2_body = """America's national parks just posted their 2025 report card: 323 million recreation visits, more than 13 million overnight stays, and a top-ten list dominated by the kind of open-road, pine-scented destinations that no resort can replicate. Summer 2026 is shaping up to be even bigger. And for NRI families based in California, Texas, or the Eastern Seaboard, a national park road trip is the most rewarding vacation you can plan this month without booking a single flight.

## California: The Obvious Starting Point

If you live in the Bay Area, Los Angeles, or San Diego, you're within a day's drive of some of the most dramatic landscapes on the planet.

**Yosemite National Park** is the crown jewel — granite cliffs, waterfalls that run full into July, giant sequoias, and enough trails to keep both toddlers and teenagers engaged. The key tip: book your campsite or lodge months ahead. Yosemite Valley fills up fast, but Tuolumne Meadows and Wawona offer more space and fewer crowds. From San Francisco, it's roughly four hours to the valley floor.

**Sequoia and Kings Canyon**, two parks managed as one, sit just south of Yosemite and draw a fraction of the visitors. Stand under General Sherman — the largest tree on Earth by volume — and try explaining to your kids that it was already 1,000 years old when the Mughal Empire began. These parks are accessible for a two-day weekend from anywhere in the Central Valley or LA basin.

**Joshua Tree** pairs well with a Palm Springs stop for families who prefer desert stargazing to alpine meadows. The twisted Joshua trees and boulder formations are otherworldly, and nighttime temperatures in June are finally bearable. Pack plenty of water and arrive early; there's almost no shade.

## The East Coast Circuit

NRIs in the Northeast have their own riches. **Acadia National Park** in Maine is one of the most visited parks in the country — 4 million visitors in 2025. Cadillac Mountain offers panoramic ocean views, and this summer the park is running a clever conservation program: carry a bag of soil to the summit and get a free guided hike. The mountaintop vegetation is eroding under foot traffic, and park rangers are enlisting hikers to haul restoration material up trails that dump trucks can't reach.

**Shenandoah National Park** in Virginia, roughly two hours from Washington DC, is another strong pick for families in the tri-state area. Skyline Drive runs 105 miles along the Blue Ridge, and the park has more than 500 miles of hiking trails, including a stretch of the Appalachian Trail.

## The Southwest Detour

For families willing to fly into Phoenix or Las Vegas and rent a car, the Arizona-Utah corridor is peak road trip territory. **Antelope Canyon**, on Navajo land near Page, Arizona, is accessible only through Navajo-led guided tours that blend geology with cultural storytelling. Combine it with Horseshoe Bend and Lake Powell for a full-day itinerary. Summer temperatures regularly exceed 100°F, so book early-morning slots for the best light and the least heat.

## Practical Tips for NRI Families

**Reservations are non-negotiable.** Yosemite requires timed-entry reservations during peak summer. Many campgrounds across the NPS system fill months in advance on Recreation.gov. Don't assume you can show up.

**The RV option is real.** Platforms like RVezy now offer delivered RV rentals in California — the owner drops a fully equipped travel trailer at your campground, connects the hookups, and picks it up when you're done. No towing, no CDL-adjacent anxiety. For NRI families who've never camped in an RV, this removes the biggest barrier.

**Annual passes pay for themselves.** The America the Beautiful Pass costs $80 and covers entrance to every national park and federal recreation area for a full year. If you visit two parks, it's already paid for.

**Pack Indian trail food.** This is not in any guidebook, but it should be. Thepla, chikki, roasted makhana, and trail mix with cashews travel better than most American snack bars and won't melt in a hot car. Every NRI family that road-trips knows this; consider it inherited wisdom.

The parks aren't going anywhere, but your kids' summer is. Three hundred and twenty-three million Americans already know what's out there. The trailhead is waiting."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "323 Million Americans Visited a National Park Last Year — Here's Why NRI Families Should Join Them This Summer",
    "subheadline": "From Yosemite to Acadia, a practical road trip guide for Indian American families who'd rather chase waterfalls than sit in another airport lounge.",
    "slug": make_slug("national-parks-road-trip-nri-families-summer-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families in the US have world-class national parks within driving distance but often default to India trips or resort vacations. This guide maps out practical road trip options from major NRI metros — Bay Area, NYC, LA — with tips tailored to Indian families.",
    "tags": ["travel", "national parks", "road trips", "summer", "family", "usa"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World — NPS 2025 Data", "url": "https://www.travelandtourworld.com/news/article/national-park-travel-news-latest-2025-figures-reveal-record-crowds-scenic-adventures-and-hidden-gems/"},
        {"name": "USA Today — Acadia Summit Conservation", "url": "https://www.usatoday.com/story/travel/experience/america/national-parks/2026/06/08/acadia-national-park-carry-soil-up-mountain/84078467007/"},
        {"name": "The Travel — California Road Trips", "url": "https://www.thetravel.com/california-weekend-road-trips-summer/"},
        {"name": "Travel And Tour World — Antelope Canyon", "url": "https://www.travelandtourworld.com/news/article/summer-tourism-peaks-with-antelope-canyon-and-lake-powell-adventures/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2452244/pexels-photo-2452244.jpeg",
    "image_caption": "A scenic road through Yosemite Valley with views of El Capitan and surrounding Sierra Nevada peaks",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ─────────────────────────────────────────────────────────────
# Insert
# ─────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
