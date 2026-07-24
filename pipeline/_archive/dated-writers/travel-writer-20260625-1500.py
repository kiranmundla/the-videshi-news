#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is Adding Six New International Routes — and Two Whole Continents — Just as Its Rivals Retreat",
        "subheadline": "Nairobi, Jakarta and four Central Asian capitals join the map between July and September, IndiGo's first reach into Africa and the post-Soviet east. For the diaspora, it is the clearest sign yet that India's biggest airline is going global on its own terms.",
        "slug": make_slug("indigo-six-new-international-routes-africa-central-asia-nairobi-jakarta-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "IndiGo's new low-cost links to Africa and Central Asia open cheaper, more direct paths for NRIs visiting family, doing business, or routing home through India rather than ceding the traffic to Gulf carriers.",
        "tags": ["travel", "airlines", "indigo", "international-routes", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Airways Magazine — IndiGo Moves Forward with International Expansion", "url": "https://www.airwaysmag.com/legacy-posts/indigo-international-expansion-plans"},
            {"name": "Livemint — IndiGo plans to add overseas, domestic destinations", "url": "https://www.livemint.com/companies/news/indigo-plans-to-add-overseas-domestic-destinations-in-fy26-as-it-expands-network-11718000000000.html"},
            {"name": "The Hindu BusinessLine — IndiGo Noida International Airport", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-start-operations-from-noida-international-airport-in-june-2026/article69536000.ece"}
        ]),
        "score_total": 80,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/16562841/pexels-photo-16562841.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A widebody jet docked at an international terminal gate, the kind of long-haul flying IndiGo is now expanding into",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India's largest airline spent much of this summer in the headlines for routes it was *cutting*. Pakistani airspace remains shut, the Gulf and West Asia are in turmoil, and both Air India and IndiGo have quietly converted a string of long-haul services to one-stop operations. So the news that IndiGo is adding six entirely new international destinations between July and September — and entering two continents for the first time — is a useful corrective to the gloom.

## Two new continents on the map

IndiGo will connect Mumbai with **Nairobi, Kenya**, and **Jakarta, Indonesia**, in late July or early August. Out of Delhi, the airline adds **Tbilisi, Georgia** (three times weekly) and **Baku, Azerbaijan** (four times weekly) in August, followed by **Tashkent, Uzbekistan** (four times weekly) and **Almaty, Kazakhstan** (three times weekly) in September. Delhi–Hong Kong, suspended during the pandemic, returns daily in August as well.

The headline is the geography. Nairobi is IndiGo's first dot in Africa; the Central Asian capitals mark its debut in the post-Soviet east. Taken together, the carrier says the additions amount to 174 new weekly international flights between June and September, pushing its international network past 30 destinations across four continents.

## Why a low-cost carrier is flying this far

For years the long-haul game out of India belonged to full-service giants — Air India, Emirates, Qatar Airways, British Airways. IndiGo, built on a single-aisle A320 fleet and ruthless turnaround times, was a domestic and short-haul machine. That is changing fast.

The airline has wet-leased Boeing 787-9 Dreamliners from Norse Atlantic Airways to fly its first true long-haul routes — Mumbai–Manchester launched in July 2025, with Amsterdam and London Heathrow following. Airbus A321XLRs are arriving to open thinner European city pairs, and A350-900s are due from 2027. The Africa and Central Asia routes are flyable on the narrowbody and leased-widebody fleet IndiGo already has, which is precisely why they can launch on this timeline.

## The diaspora angle

Most NRIs will not personally board a Delhi–Almaty flight. The reason this matters runs deeper. Every route IndiGo adds out of India is a route that does not have to connect through Dubai, Doha or Istanbul — and connecting traffic is exactly what foreign hubs have feasted on for two decades.

For the Indian American who flies home and then onward — to a wedding in Tashkent's growing Indian business community, a safari out of Nairobi, or a Caucasus holiday from Baku — a single-carrier itinerary on IndiGo through Delhi or Mumbai is cheaper and simpler than stitching together a Gulf connection. For families in East Africa with deep Gujarati and Punjabi roots, a direct Mumbai–Nairobi link restores a corridor that has thinned over the years.

There is a strategic dimension too. India has spent the past few years trying to position Delhi and Mumbai as genuine global hubs rather than feeder airports for the Gulf. Air India's new "Easy Connect" hub-and-spoke model and IndiGo's continent-spanning expansion are two sides of the same bet: that outbound and connecting Indian traffic should be routed *through India*, by Indian carriers.

## The fine print

IndiGo's releases note that ticket sales and final schedules will be confirmed "as soon as all approvals are in place" — bilateral rights and slot clearances can shift launch dates by weeks. Several of these routes are seasonal-strength markets, so frequencies may flex with demand. And the airspace constraints that forced this summer's cuts have not gone away; an airline can add Almaty while still trimming a Gulf sector in the same schedule.

Still, the direction of travel is unmistakable. A carrier that did not fly a single intercontinental route eighteen months ago is now planting flags in Africa and Central Asia. For a diaspora that has long had to choose between expensive nonstops and cheap-but-circuitous foreign connections, more Indian metal in the sky — flying to more of the world — is unambiguously good news.

For travelers planning autumn trips, the practical takeaway is to watch IndiGo's booking channels through July and August as fares for these routes open, and to compare the new direct options against the Gulf one-stops that have dominated these markets for years."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Most Famous National Parks Just Dropped Reservations for Summer — but Not All of Them",
        "subheadline": "Yosemite, Glacier, Arches and Mount Rainier scrapped timed-entry permits for 2026, while Rocky Mountain and Zion kept theirs. For NRI families planning the great American summer road trip, knowing which is which is the difference between a smooth arrival and a locked gate.",
        "slug": make_slug("us-national-parks-2026-reservations-dropped-yosemite-glacier-nri-family-road-trip"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The summer road trip to a national park is a rite of passage for Indian American families; the 2026 reservation rollback changes how and when they should plan a visit to avoid crowds and closures.",
        "tags": ["travel", "national-parks", "road-trip", "usa", "family-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "U.S. National Park Service — Yosemite reservation announcement", "url": "https://www.nps.gov/yose/learn/news/yosemite-national-park-will-not-require-vehicle-reservations-in-2026.htm"},
            {"name": "USA Today — 3 major national parks remove timed-entry requirements", "url": "https://www.usatoday.com/story/travel/experience/national-parks/2026/02/18/arches-glacier-yosemite-national-parks-reservation-requirements-summer/88744302007/"},
            {"name": "The Points Guy — National park reservation requirements are changing in 2026", "url": "https://thepointsguy.com/news/national-parks-reservation-requirement-2026/"}
        ]),
        "score_total": 72,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/19977696/pexels-photo-19977696.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Yosemite Valley with El Capitan rising over the meadow, one of the parks dropping timed-entry reservations for summer 2026",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For a generation of Indian American families, the summer pilgrimage to a national park — Yosemite's granite walls, Glacier's alpine road, the red arches of Utah — is as much a part of the calendar as the trip back to India. This year, getting in is both easier and trickier than it has been in years, and the difference comes down to which park you pick.

## What changed for 2026

In February, the Department of the Interior announced it was scrapping the seasonal timed-entry reservation systems that several marquee parks adopted during the pandemic. **Yosemite** (California), **Arches** (Utah) and **Glacier** (Montana) all dropped their advance-reservation requirements for 2026. **Mount Rainier** (Washington) followed in March, becoming the fourth.

The National Park Service framed it as expanding access. "We're expanding access where conditions allow and using targeted tools only where necessary," said Kevin Lilly, the acting assistant secretary for fish, wildlife and parks. Yosemite's superintendent said a season-wide reservation requirement was simply "not the most effective approach" after analysis of 2025 traffic showed most weekdays had available parking.

The catch: dropping reservations does not mean dropping crowd management. Yosemite will use real-time traffic monitoring and temporary diversions when its valley lots fill. Glacier will keep parking limits at Logan Pass and may divert vehicles on the famed Going-to-the-Sun Road if safety thresholds are hit. Arrive late on a July Saturday and you can still find yourself parked out — just without a permit to blame.

## Where you still need a reservation

Not every park loosened up. **Rocky Mountain National Park** in Colorado is keeping its timed-entry system from late May through mid-October. Entries are released first-come, first-served on the first of each month for the following 30 days, with a small processing fee; one permit tier adds access to the popular Bear Lake Road corridor. **Zion National Park** in Utah maintains both its shuttle system and a lottery for the famous Angels Landing hike.

So the 2026 map splits cleanly:

- **No advance reservation needed:** Yosemite, Glacier, Arches, Mount Rainier
- **Still required:** Rocky Mountain (timed entry), Zion (shuttle + Angels Landing lottery)

Campground bookings and shuttle reservations remain in use across the system regardless of the entry rules — those you still lock in early.

## How NRI families should plan

The instinct, on hearing "no reservations needed," is to be spontaneous. Resist it for the headline parks. Conservation groups have warned that the rollback could send Yosemite and Arches back to the traffic jams of the pre-permit years, and early-summer data already shows Yosemite climbing back into the country's ten busiest destinations as crowds surge.

Three practical moves:

**Go mid-week.** The single most effective lever is timing. Parks that dropped reservations are explicitly steering visitors toward weekdays, when parking and traffic are manageable. A Tuesday-Wednesday at Yosemite is a different park from a Saturday.

**Arrive at dawn or late afternoon.** Without timed slots, the gates are open all day — but the lots are not infinite. Beat the 9 a.m.–2 p.m. crush, or come for the evening light.

**Don't skip the reservation parks — just respect the system.** Rocky Mountain and Zion kept their permits precisely because they work. Mark the first of the month on your calendar, set an alarm, and book the moment the window opens.

## The bigger picture

For multi-generational Indian American families — grandparents visiting from India, kids on summer break, a rented SUV and a cooler of theplas — the national parks remain the most accessible grand adventure in the country. Most are a half-day drive from major diaspora hubs: Yosemite from the Bay Area, Rocky Mountain from Denver, Zion and Arches on the classic Utah loop out of Las Vegas or Salt Lake City.

The 2026 changes reward the prepared over the lucky. Know which park needs a permit, go on the right day, and the country's most spectacular landscapes are wide open. Show up unplanned on a peak weekend, and even a "no reservation" park can turn you away at a full parking lot. Plan around the rules, and this is shaping up to be one of the easiest summers in years to get inside the gates."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's 'New Plane' Roulette Ends This Summer on the Routes the Diaspora Actually Flies",
        "subheadline": "From July and August, retrofitted Dreamliners and three-class jets land on Mumbai–London, Delhi–Toronto, Bengaluru–London and the Amritsar–Birmingham run — bringing lie-flat business, real premium economy and, on some, first class to routes that have long flown tired cabins.",
        "slug": make_slug("air-india-summer-2026-new-retrofit-cabins-london-toronto-premium-economy-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "NRIs flying the India–UK and India–Canada corridors have gambled for years on whether they'd get a refreshed or a worn-out cabin; Air India's summer 2026 deployments finally put new interiors on the specific routes the diaspora flies most.",
        "tags": ["travel", "airlines", "air-india", "premium-economy", "cabin-upgrade"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CAPA — Air India to adjust aircraft on eight international services from summer 2026", "url": "https://centreforaviation.com/news/air-india-to-adjust-aircraft-on-eight-international-services-from-summer-2026-1348794"},
            {"name": "The Hindu BusinessLine — Air India product reset 2026 (CEO Campbell Wilson)", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-has-readied-a-product-reset-in-2026-with-new-wide-bodies-retrofits-and-seat-upgrades-says-ceo-campbell-wilson/article70524815.ece/amp/"},
            {"name": "TTR Weekly — Air India upgrades cabin experience", "url": "https://www.ttrweekly.com/site/2026/02/air-india-upgrades-cabin-experience/"}
        ]),
        "score_total": 70,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/7044182/pexels-photo-7044182.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The aisle of a refreshed widebody cabin, the kind Air India is rolling out across its India–UK and India–Canada routes for summer 2026",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Anyone who flies Air India regularly knows the gamble. You book a long-haul ticket, and only at the gate do you learn whether you've drawn a gleaming new A350 or a Dreamliner with a decade-old cabin, a broken entertainment screen and a recliner that no longer reclines. For summer 2026, on a specific set of routes the diaspora flies most, that roulette is ending.

## What's being deployed, and where

Air India confirmed it will put new, retrofitted or upgraded aircraft on eight international services from the northern summer schedule. The list reads like a map of the diaspora's travel patterns:

- **Mumbai–London Heathrow:** new Boeing 787-9s and retrofitted 787-8s from July 1, replacing the older 777-300ER. All AI flights to and from Heathrow will now feature new cabins.
- **Delhi–Toronto:** 787-9s in a three-class layout on select frequencies from August 1, introducing **premium economy** on the route.
- **Bengaluru–London Heathrow:** retrofitted 787-8s from August 1, also adding **premium economy**.
- **Delhi–Melbourne:** 777-300ERs in three-class config from July 1, bringing **first class** to the route.
- **Delhi–Birmingham, Amritsar–Birmingham, Ahmedabad–London Gatwick, Amritsar–London Gatwick:** 777-300ERs from August 1, introducing **first class** on these Punjab- and Gujarat-heavy services.

## Why this matters to the diaspora specifically

These are not random routes. The UK corridor — Heathrow, Gatwick, Birmingham — and the Canada corridor to Toronto are the arteries of the Indian diaspora in those countries. The Amritsar and Ahmedabad services in particular carry enormous Punjabi and Gujarati VFR (visiting friends and relatives) traffic, communities that have historically been flown on whatever metal was spare.

The headline for value-conscious families is **premium economy**, now arriving on Delhi–Toronto and Bengaluru–London. For the NRI who finds full business class out of reach but dreads 9-plus hours in a cramped economy seat — often with elderly parents or young children — premium economy is the sweet spot: meaningfully more legroom, a wider seat, better service, at a fraction of the business fare. Its arrival on these exact routes is the single most practical upgrade in the schedule.

## The reset behind the schedule

The deployments are the visible tip of Air India's broader fleet overhaul under the Tata Group. CEO Campbell Wilson has called the transformation "irreversible," targeting more than 55% of the widebody fleet as new or refreshed by the end of 2026. Six new widebodies — Boeing 787-9s and Airbus A350-1000s — are joining this year, the first 787-9 already inducted in January.

In parallel, 26 legacy 787-8s are being retrofitted at Victorville, California, with new seats, redesigned galleys and lavatories, refreshed mood lighting and the airline's updated livery. The first two refitted Dreamliners are returning to service now, with two to three more sent for retrofit every month. The flagship A350s — 28 business suites with full-flat beds, a dedicated 24-seat premium economy cabin, Panasonic eX3 screens with content in 13 international and eight Indian regional languages — are already flying the marquee Delhi–London and Delhi–New York routes.

## The honest caveats

Two cautions before you book. First, "select frequencies" does the heavy lifting on Delhi–Toronto: only the majority of the ten weekly flights get the new 787-9, so the roulette is reduced, not eliminated — check the aircraft type at booking and again before departure. Second, supply-chain and certification snags have dogged the program; some new 787-9s initially flew with restrictions on business and a subset of economy seats pending full FAA certification. Schedules can slip.

But the trajectory is clear and, for once, pointed at the diaspora's own routes rather than just the showpiece flights to New York and London city-center business travelers. For an Indian American family planning a UK summer or a parent's visit to Toronto, the advice is concrete: check the aircraft type when you book, favor the dates that show the retrofitted or new equipment, and — if the budget allows — grab premium economy on the routes that now offer it. After years of hoping for a good plane, you can finally plan for one."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)} articles inserted.")
for h in inserted:
    print(f"  - {h}")
