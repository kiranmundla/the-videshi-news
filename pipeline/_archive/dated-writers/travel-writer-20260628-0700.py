#!/usr/bin/env python3
"""Travel writer — June 28, 2026 batch"""
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


# ── Article 1: July 4th Road Trip Guide ──────────────────────────────

article1_body = """America turns 250 this Friday, and 72.2 million people are expected to celebrate the only way the country truly knows how: by getting in the car and going somewhere. For NRI families weighing whether to brave the holiday traffic or stay home with a pot of biryani and Netflix, here is the case for hitting the road — and how to do it without spending a fortune.

## The national parks are free — all weekend

The National Park Service has waived entry fees from July 3 through July 5, covering every one of its 400-plus sites. That includes the heavy-hitters — Yellowstone, Yosemite, the Grand Canyon, Great Smoky Mountains — and dozens of lesser-known gems that rarely charge admission anyway. For a family of four, saving the $35-per-vehicle fee is a small win. The real payoff is the excuse to visit a place you have been meaning to see since you moved here.

## Five gateway towns trending this summer

Budget-conscious travellers are skipping the big cities and heading for gateway towns near national parks. According to Expedia, searches using budget filters have surged 1,265 per cent year over year for the July 4 window. The top five trending destinations tell the story:

**Moab, Utah** — gateway to Arches and Canyonlands national parks. The sandstone landscape looks like it belongs on Mars, and the iconic Delicate Arch at sunset is worth every minute of the 3-mile round-trip hike. Kid-friendly, but bring plenty of water.

**Gatlinburg, Tennessee** — the front door to Great Smoky Mountains National Park, the most visited park in the system. The Smokies offer dense hardwood forests, black bear sightings, and trails that range from stroller-friendly to serious backcountry. Temperatures will be in the high 80s; shade breaks are mandatory.

**Flagstaff, Arizona** — a cooler, pine-forested base for Grand Canyon day trips. The South Rim is 80 miles away, and the altitude keeps Flagstaff 20 degrees cooler than Phoenix.

**Mariposa, California** — the small-town gateway to Yosemite, offering lodges and rentals at a fraction of Yosemite Valley prices. The Merced River corridor is ideal for families with younger children.

**Bozeman, Montana** — a college town turned outdoor hub, about 90 minutes from Yellowstone's north entrance. Old Faithful, the Grand Prismatic Spring, and bison herds await.

## Timing your drive

AAA projects 61.4 million drivers on the road over the extended weekend. The traffic data firm Inrix has mapped the best and worst windows. The short version: leave before 11 a.m. on most days, and avoid Thursday and Friday afternoons entirely. Saturday, July 4, clears up after 3 p.m. when most people are already parked at their barbecue. Sunday is best before 11 a.m.

Gas prices have dipped slightly in recent weeks, though they are still more than 80 cents per gallon above last year's levels. The silver lining: airfares are trending down too, so if you would rather fly to a gateway city and rent a car, this is a reasonable window to book.

## The NRI calculation

For first-generation Indian Americans, the July 4 weekend sometimes feels like borrowed nostalgia — someone else's Independence Day, someone else's fireworks. But the national parks belong to everyone, and a weekend spent scrambling over red rock in Moab or watching elk graze in Yellowstone has a way of making the place feel more like home.

It is also the rare American holiday that does not revolve around a specific cuisine. Pack your own — a cooler of parathas, achaar, and chai fixings works better at a picnic site than any overpriced rest-stop burger.

For families with kids, the Junior Ranger programme at most parks hands children a workbook, sends them on a scavenger hunt, and badges them as official Junior Rangers at the end. It costs nothing and buys you two hours of uninterrupted hiking silence.

## What to pack

Sunscreen, reusable water bottles (refill stations are common), layers for elevation changes, a first-aid kit, and a healthy respect for wildlife. The Smokies are reminding visitors that bear encounters are real and that food left in an unlocked car can get a bear killed. Store everything in a hard-sided, locked vehicle with windows up.

America's semiquincentennial only happens once. The parks are free, the roads are open, and the biryani travels well in a cooler. Go."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "America Turns 250 This Weekend — Here's the NRI Family's Guide to a National Park Road Trip",
    "subheadline": "National parks waive fees July 3–5, gateway towns are trending over big cities, and 72 million Americans are hitting the road. A practical guide for Indian American families joining the caravan.",
    "slug": make_slug("july-4-national-parks-road-trip-nri-family-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "For NRI families, the July 4 weekend and free national park entry is the most accessible American road trip window of the year — no special cuisine required, just a cooler and curiosity.",
    "tags": ["travel", "july 4", "national parks", "road trip", "family travel", "usa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "USA Today", "url": "https://www.usatoday.com/story/travel/2026/06/24/july-4-travel-priciest-day-fly/77052018007/"},
        {"name": "Fast Company", "url": "https://www.fastcompany.com/91349215/july-4-2026-travel-data-trending-destinations"},
        {"name": "AAA / NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/06/27/millions-driving-july-4-what-to-expect/"},
        {"name": "National Park Service", "url": "https://www.nps.gov/planyourvisit/fee-free-parks.htm"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Delicate_arch_sunset.jpg",
    "image_caption": "Delicate Arch at sunset in Arches National Park near Moab, Utah",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ── Article 2: Sri Lanka direct flight from Ahmedabad ────────────────

article2_body = """If you are an NRI flying to Gujarat this summer, there is a new three-hour detour worth knowing about. On June 19, Sri Lanka's FitsAir became the only airline operating direct flights between Ahmedabad and Colombo — a route that previously required a nine-to-ten-hour crawl via Mumbai or Chennai. For NRIs visiting family in Ahmedabad, Baroda, or Surat, Colombo just became the easiest international add-on to a homecoming trip.

## The route

FitsAir operates three weekly flights — Monday, Wednesday, and Friday. The westbound leg departs Colombo at 11.25 p.m. and lands in Ahmedabad at 2.35 a.m., giving passengers a full day ahead. The return options include a 3.40 a.m. red-eye or a 10.45 a.m. departure, arriving in Colombo by early afternoon. Flight time: roughly three hours and 10 minutes.

Curated travel packages — airfare, two nights at Cinnamon Life at City of Dreams, breakfast, and private airport transfers — start at ₹55,555 per person. That is not a misprint. For context, a comparable two-night package to Dubai from Ahmedabad runs closer to ₹80,000 during summer.

## Why Colombo, and why now

Sri Lanka has spent the last three years rebuilding its tourism infrastructure after a bruising economic crisis. The result is a country that is eager for visitors, competitively priced, and increasingly set up for Indian travellers specifically. UPI payments are now accepted at major hotels, restaurants, and retail outlets in Colombo, which means you can pay in rupees without fumbling with currency exchanges or carrying dollars.

City of Dreams Sri Lanka — South Asia's first integrated resort, opened inside the Cinnamon Life tower in central Colombo — is the headline attraction. It combines luxury hospitality, dining, entertainment, and nightlife under one roof, positioned squarely at the Indian wedding and family-celebration market.

But the real draw for a short trip is Colombo itself: a compact, walkable city with Dutch-colonial architecture in the Fort district, fresh seafood at the Pettah market, high tea at the Galle Face Hotel (a 160-year-old institution), and temple visits at the Gangaramaya and Kelaniya Raja Maha Vihara. A tuk-tuk ride from one end of the tourist belt to the other costs about 500 Sri Lankan rupees — roughly ₹125.

## The Ramayana trail and beyond

For NRI families with religious or cultural interests, Sri Lanka offers a Ramayana heritage circuit that connects sites traditionally associated with the epic across the island — from Sita Amman Temple near Nuwara Eliya to the Ashok Vatika garden and the Munneswaram Kovil near Chilaw. Several tour operators now run dedicated three-to-five-day Ramayana trail itineraries, and the cultural resonance is genuine: the sites are maintained, signposted, and visited by both Sri Lankan and Indian pilgrims.

Beyond Colombo, a three-day extension opens up Kandy (the Temple of the Tooth, tea plantations), Galle (the 17th-century Dutch fort, now a boutique-hotel strip), and the southern beaches — Unawatuna, Mirissa, and Tangalle — where whale-watching season runs through July.

## The NRI calculation

Gujarat currently sends 25,000 to 30,000 tourists to Sri Lanka annually, and tourism officials expect the direct flight to double that number within two years. But the math works even for NRIs based elsewhere in the US: if your homecoming trip routes through Ahmedabad anyway — and with Air India and IndiGo both serving Ahmedabad from the US via Delhi — tacking on a three-day Colombo side trip is now trivially easy.

Indian passport holders can get a Sri Lanka e-visa online in under 24 hours. There is no currency hassle if you carry UPI. The time difference from India is just 30 minutes. And if you are already jet-lagged from a San Francisco–to–Ahmedabad haul, a FitsAir red-eye to Colombo will feel like a nap.

## What to know before you book

Flights are bookable through FitsAir's website (fitsair.com) and authorised travel agents. Cinnamon Hotels runs the package deals. Colombo hotels are competitively priced — expect ₹5,000–₹8,000 per night for a solid four-star outside the package. The monsoon season brings intermittent rain to Colombo through September, but it is the kind of tropical downpour that clears in an hour, not the kind that cancels plans.

For NRIs who have flown halfway around the world to visit family in Gujarat, a three-hour hop to Colombo is the international side trip that finally makes geographic sense."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Colombo Is Now a Three-Hour Hop from Ahmedabad — Why NRIs Should Add Sri Lanka to Their India Trip",
    "subheadline": "FitsAir's new direct route cuts Ahmedabad-to-Colombo travel from ten hours to three. With UPI acceptance, packages from ₹55,555, and a Ramayana heritage trail, Sri Lanka is the easiest international add-on for NRIs visiting Gujarat.",
    "slug": make_slug("colombo-ahmedabad-fitsair-direct-flight-nri-sri-lanka"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting family in Gujarat can now add a three-day Colombo getaway for ₹55,555 — a three-hour direct flight that did not exist before June 19.",
    "tags": ["travel", "sri lanka", "colombo", "ahmedabad", "fitsair", "nri", "gujarat"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Lanka Business News", "url": "https://www.lankabusinessnews.com/city-of-dreams-sri-lanka-and-cinnamon-hotels-initiate-direct-ahmedabad-colombo-flights-in-partnership-with-fitsair/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/ahmedabad-colombo-direct-flights-may-15-travel-time-to-drop-3-hours"},
        {"name": "Suratha News", "url": "https://suratha.lk/fitsair-commences-only-direct-air-service-between-colombo-and-ahmedabad/"},
        {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/ahmedabad-colombo-new-flights-launched-to-boost-travel-to-city-of-dreams-sri-lanka/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Colombo_city_skyline_at_night.png",
    "image_caption": "Colombo city skyline at night, Sri Lanka",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ── Insert ────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
