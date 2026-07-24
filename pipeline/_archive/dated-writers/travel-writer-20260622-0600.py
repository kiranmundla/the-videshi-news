#!/usr/bin/env python3
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

navi_body = """India's most-watched airport project is about to do the thing it was actually built for. Navi Mumbai International Airport (NMIA), the Adani-run greenfield field that opened to domestic flights on Christmas Day 2025, will begin international passenger and cargo operations on **July 15, 2026** — with Air India Express set to fly the inaugural overseas service to Abu Dhabi.

For the millions of Indians in the Gulf who treat Mumbai as the front door to the homeland, this is the most consequential airport news of the year so far.

## What's Actually Happening On July 15

The launch had originally been pencilled in for the start of the summer schedule in late March, but operators pushed it to mid-July after the West Asia conflict disrupted planning. A senior Central Board of Indirect Taxes and Customs official reviewed the airport's readiness for international operations on June 16, and trial runs are now in their final stretch. A formal trade notice clearing the airport for international launch is expected in early July.

Air India Express, the Air India Group's low-cost arm, is slated to be the first carrier to fly internationally from NMIA, opening bookings for its Abu Dhabi inaugural around June 27. IndiGo is expected to follow closely. Early international routes will concentrate on short-haul Gulf and Middle East destinations — exactly the corridors that carry the bulk of India's blue-collar and professional diaspora.

Freighters launch the same day, scaling toward roughly 18 cargo flights a week.

## Why The Gulf-First Rollout Matters To NRIs

The geography here is the whole story. NMIA sits across Mumbai's harbour from the chronically congested Chhatrapati Shivaji Maharaj International Airport (BOM), which has long run near its operational ceiling. For a Gulf resident flying home for Eid, a wedding, or a parent's medical procedure, the difference between landing at a saturated single-runway BOM and a brand-new field with room to breathe is measured in real minutes at immigration and baggage.

The United Arab Emirates alone hosts an estimated 3.5 million Indians, and the Mumbai–Gulf corridor is one of the densest air-travel markets on earth. Routing even a slice of that traffic through a second international gateway eases the squeeze on BOM that diaspora flyers have complained about for a decade.

There is also a quieter convenience: NMIA is closer to Pune, Navi Mumbai's growing tech and residential belt, and the southern and eastern suburbs than the old airport. NRIs with family in those areas may shave an hour off the white-knuckle cab ride that has always bookended the India trip.

## The Bigger Picture: Two Airports, One Megacity

NMIA's long-term design has already been revised upward on the strength of early demand projections. The planned Terminal 2 has been re-scoped to handle around 50 million passengers a year, up from an earlier 30 million, with the airport's overall ceiling now targeted at roughly 90 million annually. For context, that would make the Mumbai region one of a small club of global megacities served by two large international airports — the model that London, New York, and Tokyo have used for decades.

The project has also picked up a *Prix Versailles* nod as one of the world's most beautiful airports for 2026, a marketing win that matters for a field trying to lure foreign carriers away from the incumbent.

## What's Next

The first international weeks will be modest — a handful of Gulf services and freighters — before the network broadens through the back half of 2026. NMIA's operators expect daily passenger footfall to climb from around 20,000 today toward 50,000 by year-end. For now, diaspora flyers booking summer and Diwali-season trips home should watch which carriers add NMIA as an alternative to BOM; an Abu Dhabi or Dubai connection through the new airport could quickly become the smarter routing.

The takeaway for NRIs: after years of headlines, India's marquee new airport is finally about to do international arrivals — and the Gulf diaspora is first in line.
"""

ayodhya_body = """For decades, the knock on India's great pilgrimage towns was the same: soaring devotion, dismal hotels. A diaspora family flying in from New Jersey or London to see Ram Mandir, the Golden Temple, or the ghats of Varanasi could find a world-class temple ringed by guesthouses that hadn't been renovated since the 1980s. That gap is now closing fast — and ITC Hotels just made its most pointed bet yet.

The Kolkata-based luxury group has signed a management agreement for a new **Welcomhotel by ITC Hotels in Ayodhya**, the latest in a deliberate string of signings along India's pilgrimage trail.

## A 143-Room Bet On Ayodhya

The property will span 143 rooms across four acres on the banks of the Saryu River, with interiors drawn from Ayodhya's layered history. Beyond well-appointed rooms and suites, it will offer an all-day dining restaurant and more than 11,000 square feet of indoor banqueting space — a clear signal that ITC expects destination weddings and milestone celebrations, not just temple visits. A swimming pool, fitness centre, and spa round out the wellness offering.

The timing is not subtle. Ayodhya now draws an average of 100,000 daily visitors to Ram Mandir, and the surrounding tourism and transport infrastructure has been overhauled — a new airport, widened roads, and a redeveloped riverfront. The pilgrims, as ITC's managing director Anil Chadha put it, keep coming. So do the curious. Premium hospitality, until very recently, had not kept pace.

## Part Of A Pilgrimage-Trail Strategy

The Ayodhya deal does not stand alone. ITC has been planting its Welcomhotel flag across India's holiest addresses — recent signings include Bodh Gaya, Shirdi, and Vrindavan, with a separate 140-key Welcomhotel just announced for Jaipur. Rival chains are racing the same map: Royal Orchid is targeting 50 new hotels in the next 12 to 18 months, betting that geopolitical tension and a weak rupee are pushing Indians — and visiting NRIs — toward domestic religious and heritage travel rather than overseas holidays.

The numbers back the thesis. India's branded hotel chains signed pacts to manage at least 550 new hotels nationwide last year, with pilgrimage towns, hill stations, and airport corridors leading the push. Religious tourism has quietly become one of the hospitality sector's biggest growth engines.

## Why This Matters For The Diaspora

For NRI families, the pilgrimage trip is often the emotional core of the India visit — the reason grandparents insist everyone come, the itinerary item that anchors the whole journey. Until now, the lodging math has frequently forced an uncomfortable choice: stay in a basic dharamshala-grade room near the temple, or book a proper hotel an hour's drive away and lose half a day to traffic each way.

A branded property with reliable air-conditioning, clean water, recognizable service standards, and rooms that can accommodate a multi-generational group changes that calculus. It also makes the increasingly popular "destination wedding at a sacred site" feasible for diaspora couples who want the spiritual setting without sacrificing the logistics their overseas guests expect.

There is a practical booking angle too: branded hotels in pilgrimage towns mean loyalty points, app-based reservations, and English-language customer service — small things that remove friction for a family coordinating a trip from 8,000 miles away.

## What's Next

The Ayodhya Welcomhotel is a signing, not a ribbon-cutting, so an opening date will follow once construction milestones are met — ITC's recent pilgrimage properties have typically run two to three years from agreement to launch. In the meantime, the broader signal is the useful one for NRIs planning ahead: the next time you map a temple-town itinerary, expect a real hotel to be part of it.

For a diaspora that has long endured the lodging lottery of India's holy cities, the room upgrade is finally arriving.
"""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Navi Mumbai's New Airport Goes International July 15 — and the Gulf Diaspora Is First in Line",
        "subheadline": "Air India Express will fly the inaugural overseas route to Abu Dhabi as India's marquee greenfield airport finally opens its international doors, easing the squeeze on chronically congested Mumbai.",
        "slug": make_slug("navi-mumbai-airport-international-launch-july-15-abu-dhabi-gulf-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Millions of Gulf-based Indians who route home through saturated Mumbai now get a second international gateway with room to breathe — and shorter cab rides for family in Pune and the southern suburbs.",
        "tags": ["travel", "airports", "navi mumbai", "air india express", "gulf", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/navi-mumbai-international-airport-to-take-off-internationally-from-july-15"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "The terminal at Navi Mumbai International Airport, which begins international operations on July 15, 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": navi_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Holy Cities Are Finally Getting Real Hotels — ITC Plants Its Flag in Ayodhya",
        "subheadline": "A new 143-room Welcomhotel on the banks of the Saryu is the latest sign that branded luxury is chasing the pilgrimage boom, ending the lodging lottery NRI families have long endured at sacred sites.",
        "slug": make_slug("itc-welcomhotel-ayodhya-pilgrimage-hotel-boom-nri-saryu"),
        "category": "travel",
        "vertical": "hospitality",
        "diaspora_angle": "For NRI families whose India trips revolve around a temple-town visit, branded hotels with reliable standards, app booking, and rooms big enough for a multi-generational group finally make the pilgrimage leg comfortable — and destination weddings at sacred sites feasible.",
        "tags": ["travel", "hotels", "ayodhya", "pilgrimage", "itc hotels", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/"},
            {"name": "Restaurant India", "url": "https://www.restaurantindia.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Shri_Ram_Janambhoomi_Mandir%2C_Ayodhya.jpg/1280px-Shri_Ram_Janambhoomi_Mandir%2C_Ayodhya.jpg",
        "image_caption": "Ram Mandir in Ayodhya, the pilgrimage hub now drawing branded luxury hotels like ITC's new Welcomhotel.",
        "image_attribution": "Wikimedia Commons",
        "body": ayodhya_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
