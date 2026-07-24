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

# ---------------------------------------------------------------------------
# ARTICLE 1 — National parks $100 nonresident surcharge + reservation drops
# ---------------------------------------------------------------------------
body1 = """When the cousins fly in from Bengaluru this summer and the family piles into a rented SUV for the great American road trip, the math at the park gate just changed. The Department of the Interior's pricing overhaul, in effect for the 2026 season, adds a surcharge of up to **$100 for non-U.S. residents** at the most heavily visited national parks — and rewrites the calendar of free-entry days that families have long planned around.

For the Indian diaspora, where summer almost always means visiting parents, in-laws, or relatives on a B-2 visitor visa, the distinction between resident and non-resident is no longer academic. It now shows up as a line item at the entrance booth.

## What actually changed

The Interior Department's "America-first pricing" policy keeps entrance fees flat for U.S. residents — still the familiar $20 to $35 per vehicle at most parks — but layers a **$100 surcharge for international visitors** at marquee parks. The annual America the Beautiful pass, the workhorse of any multi-park trip, also splits: residents pay the usual rate, while a **non-resident annual pass now runs $250**.

The free-entry calendar was reshuffled too. Flag Day (June 14, which doubles as the President's birthday), the National Park Service's 110th anniversary on August 25, Constitution Day on September 17, and Theodore Roosevelt's birthday on October 27 are now fee-free. Martin Luther King Jr. Day and Juneteenth, both previously free, have been dropped. Independence Day weekend (July 3–5) and Veterans Day (November 11) remain free.

## The reservation rollback

The bigger practical shift for trip-planners is that several of the country's most photographed parks have **scrapped their timed-entry reservation systems** for 2026. Yosemite confirmed in February it will not require advance vehicle reservations at any point this year — including the peak summer months and the February firefall window. Arches in Utah dropped its system too, and Glacier in Montana will run only targeted congestion management on Going-to-the-Sun Road rather than a park-wide booking requirement.

That is a double-edged update. It removes the 7 a.m. scramble for reservation slots that tripped up so many first-time visitors. But conservation groups warn it also means the parking lots at Yosemite Valley and Arches' Delicate Arch trailhead will fill early and stay full, with rangers diverting traffic when capacity is hit. Rocky Mountain National Park, notably, is keeping its timed-entry system from late May through mid-October.

## Why this matters for NRIs

Indian American families are among the most enthusiastic national-park road-trippers in the country — the parks are a fixture of the itinerary when relatives visit, and the photos are a diaspora WhatsApp staple. The new rules change the calculus in three concrete ways.

First, **budget for the visa status of every person in the car.** A green-card holder and a U.S. citizen are residents; a parent visiting on a B-2 is not. At a park with the surcharge, that visiting parent could add $100 to the gate cost. For a family hosting two visiting grandparents, that is a real number worth knowing before you arrive, not after.

Second, **rethink the annual pass.** If the trip is built around one or two parks, the per-visit resident fee is cheap. The $250 non-resident annual pass only makes sense for a relative planning a genuinely park-heavy, multi-week tour.

Third, **arrive early or go midweek.** With reservations gone at Yosemite, Arches, and Glacier, the crowd-control valve is now the parking lot. Families used to a guaranteed timed slot should treat a pre-8 a.m. arrival as the new reservation. Tuolumne Meadows, Wawona, and Hetch Hetchy absorb overflow when Yosemite Valley is jammed.

## The bottom line

For a community that treats the summer road trip as a rite of passage, 2026 rewards planning. Confirm each traveler's residency status against the surcharge, check the new free-day calendar before locking dates, and — at the reservation-free parks — beat the parking-lot rush rather than the booking window. The gates are more open than they have been in years; they are also, for some of your passengers, more expensive."""

# ---------------------------------------------------------------------------
# ARTICLE 2 — International airfares plunge below $1,000 + India-route deals
# ---------------------------------------------------------------------------
body2 = """For the first time since mid-March, the average international airfare from the United States has dipped below $1,000 — a window that lands right as diaspora families finalize summer plans to India. The catch, as every veteran NRI flyer knows, is that these windows close fast.

The average international round-trip ticket fell to **$980 last week**, the lowest since the week of March 23, according to fare-tracker Kayak. It is a meaningful break in a year that has otherwise punished anyone trying to fly transatlantic or transpacific.

## What's driving the dip

The softening is less a gift than a symptom. Carriers are easing prices to win back cash-strapped travelers amid weaker-than-expected demand, especially on U.S.–Europe routes. The 2026 FIFA World Cup, spread across 11 U.S. cities, was supposed to flood the market with inbound visitors; those numbers have underwhelmed, leaving airlines with seats to fill.

The steepest drops were on Asia and Europe routes: Seoul fell 15% to $1,207, Shanghai 15% to $1,378, and a clutch of European cities — Barcelona, Athens, Paris, Naples — slid into the low $1,000s. The shadow over all of it is the war involving Iran, which keeps jet-fuel costs elevated and, experts caution, could snap fares back up with little warning.

## The India-route picture

India-bound fares have not collapsed the way some European routes have, but the deals are real for travelers willing to accept a one-stop itinerary. Fare aggregators are currently surfacing round-trips well under the psychological $1,000 line on the corridors NRIs use most:

- **Boston–Mumbai** around $776 (one stop, Etihad)
- **Atlanta–Delhi** around $792 (one stop, Etihad)
- **Boston–Bengaluru** around $807, **Boston–Delhi** around $813
- **Chicago–Bengaluru** around $823

These are seasonal snapshots, not guarantees, and they cluster on dates in July, August, and the shoulder weeks. Nonstop fares — Air India and United's flagship India service — remain pricier, a premium that has only grown as Pakistani airspace closures force longer, costlier routings.

## The timing game

The data points to a clear strategy. Kayak and Expedia both flag **August 10 to September 6** as the cheapest international booking-and-travel window of the summer, with fares running roughly 40% below peak weeks. For families with school-age children that window is tight, but those traveling with retired parents or on flexible schedules can exploit it.

A few tactics specific to the India route:

- **Watch the Gulf carriers.** If the airspace situation around Iran stabilizes — and there are early diplomatic signals it might — Emirates, Qatar Airways, and Etihad capacity returns, and one-stop Gulf fares are historically the cheapest way to reach India. Qatar Airways already expanded to over 150 destinations from June 16.
- **Friday beats Tuesday.** Expedia's latest data overturns the old "Travel Tuesday" wisdom: the cheapest day to both book and depart is now Friday.
- **Book the dip, don't wait it out.** As The Points Guy's Brian Kelly put it, "Waiting around in 2026 has not been a great strategy." When a fare looks good, lock it.

## Why this matters for NRIs

For Indian Americans, the annual or biennial trip home is rarely optional — it is weddings, ailing grandparents, a child meeting cousins. That makes the diaspora unusually exposed to fare swings, and unusually rewarded by timing them well. A family of four shaving $200 off each ticket on a Boston–Bengaluru run keeps $800 in the trip budget — the difference between economy and a premium-economy upgrade, or a few extra days on the ground.

The honest read: this is a genuine softening, but a fragile one. The same fuel pressures that experts say will push fares back up are one headline away from doing exactly that. If the dates work and the fare is under four figures on your corridor, this is the week to book — not the week to keep a tab open."""

# ---------------------------------------------------------------------------
# ARTICLE 3 — Noida International Airport goes live
# ---------------------------------------------------------------------------
body3 = """The Delhi region's long-promised second major gateway is finally real. On June 15, the first scheduled commercial flight — an IndiGo service from Lucknow — touched down at **Noida International Airport in Jewar**, ending years of construction delays and opening a new front door to North India that NRIs flying home will soon find hard to ignore.

The inaugural 6E-2278 arrived from Lucknow before continuing to Bengaluru, a modest first schedule that belies the airport's ambitions. IndiGo plans to connect Jewar to more than **16 domestic destinations** — Hyderabad, Jaipur, Chandigarh, Amritsar, Srinagar, Bhopal, Dehradun, Dharamshala and others — building toward 40 daily flights by July.

## A relief valve for Delhi

Noida International was conceived to take pressure off Indira Gandhi International Airport (IGI), which has spent years operating near saturation. Phase 1, built at roughly ₹11,582 crore, is designed to handle **12 million passengers a year**, with a single runway, an integrated terminal, and a modern air traffic control tower. Expansion phases will scale it well beyond that as demand grows.

Strategically placed along the Yamuna Expressway, the airport gives the National Capital Region a third commercial field, alongside IGI and Ghaziabad's Hindon. IndiGo, the launch carrier, now serves all three. Akasa Air and Air India Express are expected to follow, giving the airport a multi-airline footprint from its earliest weeks.

## The international piece is coming

For now the schedule is domestic, but the name is not aspirational — international operations are part of the plan, and that is where the diaspora calculus gets interesting. The Jewar location sits closer to the satellite cities of Noida, Greater Noida, and the western Uttar Pradesh belt than IGI does, and it is positioned to draw traffic from Agra and the wider region to its south.

The airport's backers project it will eventually anchor a logistics, warehousing, and hospitality corridor expected to generate over 100,000 jobs — the kind of economic gravity that tends to pull airline route planners along with it.

## Why this matters for NRIs

A large share of the Indian American community traces its roots to Delhi-NCR and western Uttar Pradesh, and for them the practical question on every trip home is the same: how long is the drive from the airport to the family home, and how brutal is the traffic? For relatives in Noida, Greater Noida, or the Yamuna Expressway corridor, Jewar promises a materially shorter, less congested run than the cross-city slog to IGI — especially painful after a 15-hour flight with jet-lagged kids.

There is a second, subtler benefit. IGI's congestion has long meant tight connections and frequent delays on the domestic legs that NRIs use to reach Lucknow, Varanasi, or Amritsar after landing from the U.S. A second high-capacity hub eases that bottleneck across the whole region, even for travelers who never set foot in Jewar.

The honest caveat: until international carriers actually schedule long-haul service into Noida, diaspora flyers from the U.S. will still route through IGI or a Gulf hub. But infrastructure shapes airline behavior, and a 12-million-passenger airport on the Yamuna Expressway is not built to stay domestic. For families with roots in the region, Jewar is one to watch — and, before long, one to fly into.

## What's next

IndiGo's network from Noida expands through July, with Akasa and Air India Express slated to add capacity. The real milestone to watch is the first international route announcement, which would transform Jewar from a domestic relief valve into a genuine diaspora gateway."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "America's National Parks Just Got Pricier for Visiting Family — and the Reservation Rules Quietly Vanished",
        "subheadline": "A 2026 pricing overhaul adds a $100 surcharge for non-resident visitors while Yosemite, Arches and Glacier drop timed-entry reservations. For NRI families hosting relatives this summer, the road-trip math has changed.",
        "slug": make_slug("national-parks-2026-nonresident-surcharge-reservation-changes-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families hosting visiting parents and relatives on B-2 visas now face a $100 non-resident surcharge at major parks, while the end of timed-entry reservations at Yosemite, Arches and Glacier changes how to plan the classic summer road trip.",
        "tags": ["travel", "national parks", "road trip", "summer", "visa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Sun — National parks holiday calendar and fee changes", "url": "https://www.the-sun.com/travel/"},
            {"name": "AFAR — Reservations Dropped for Yosemite and Arches National Parks", "url": "https://www.afar.com/magazine/yosemite-arches-national-parks-drop-reservations"},
            {"name": "National Park Service — Yosemite 2026 reservations", "url": "https://www.nps.gov/yose/planyourvisit/reservations.htm"},
            {"name": "Detroit Free Press — National park free entry days 2026", "url": "https://www.freep.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Tunnel_View%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg/1280px-Tunnel_View%2C_Yosemite_Valley%2C_Yosemite_NP_-_Diliff.jpg",
        "image_caption": "Tunnel View overlooking Yosemite Valley, one of the parks dropping timed-entry reservations for the 2026 season",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body1
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "International Airfares Just Dropped Below $1,000 — Here's the India-Route Window NRIs Should Grab",
        "subheadline": "Average overseas fares fell to their lowest since March, and one-stop deals to Mumbai, Delhi and Bengaluru are surfacing under four figures. Experts warn the dip is fragile — book it, don't wait it out.",
        "slug": make_slug("international-airfares-drop-below-1000-india-route-deals-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With the near-mandatory annual trip home, Indian Americans are unusually exposed to fare swings — and one-stop India fares now dipping under $1,000 plus the August booking window offer real savings for families timing it right.",
        "tags": ["travel", "airfare", "flight deals", "airlines", "India"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post — International airfares plunge below $1,000", "url": "https://nypost.com/"},
            {"name": "KAYAK — Summer 2026 Savings Report", "url": "https://www.kayak.com/news/summer-travel-2026/"},
            {"name": "Mint — Planning summer holidays amid soaring airfares", "url": "https://www.livemint.com/"},
            {"name": "Travel Noire — 2026 summer airfare window", "url": "https://travelnoire.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36681344/pexels-photo-36681344.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A busy airport departures hall during the summer travel season",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Delhi's Second Big Airport Is Finally Flying — Why NRIs With Roots in North India Should Care",
        "subheadline": "Noida International Airport at Jewar took its first commercial flight on June 15, opening a new gateway designed for 12 million passengers a year. International service is part of the plan.",
        "slug": make_slug("noida-international-airport-jewar-first-flight-nri-north-india"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "A large slice of the Indian American community traces its roots to Delhi-NCR and western Uttar Pradesh — and the new Jewar airport promises shorter drives home and relief from IGI's congestion once international routes arrive.",
        "tags": ["travel", "airports", "India", "Delhi", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia — Commercial flights begin at Noida International Airport", "url": "https://www.travelandleisureasia.com/in/"},
            {"name": "Hotelier India — IndiGo first airline at Noida International Airport", "url": "https://www.hotelierindia.com/"},
            {"name": "Travel And Tour World — Noida International Airport unlocks new routes", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "image_caption": "The inauguration ceremony of Noida International Airport at Jewar in the Delhi-NCR region",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": body3
    }
]

# Word-count sanity check
for art in articles:
    wc = len(art["body"].split())
    print(f"  • {art['slug']}: {wc} words")
print()

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
