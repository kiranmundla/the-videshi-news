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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Express Is Rebuilding the Gulf Run From the South — and Bengaluru Is the Engine",
        "subheadline": "After months of Iran-Israel airspace cuts, the Tata low-cost carrier has restored Abu Dhabi, Jeddah, Riyadh and Kuwait from Bengaluru and added first-ever Dubai and Doha flights — a quiet win for the Gulf's huge South Indian workforce.",
        "slug": make_slug("air-india-express-gulf-restoration-bengaluru-south-india"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Millions of Keralite, Kannadiga, Tamil and Telugu families split between South India and the Gulf depend on these low-cost VFR routes; their return means cheaper, more frequent seats home after a season of cancellations.",
        "tags": ["travel", "airlines", "air-india-express", "gulf", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/17/air-india-express-restores-more-middle-east-flights/"},
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/about-us/press-release.html"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Air_India_Express_Boeing_737_2078.JPG/1280px-Air_India_Express_Boeing_737_2078.JPG",
        "image_caption": "An Air India Express Boeing 737, the workhorse of the carrier's short- and medium-haul Gulf network.",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India Express has finished rebuilding the Middle East network it was forced to gut earlier this year, and the recovery has been led not from Delhi or Mumbai but from Bengaluru. For the South Indian families who keep the Gulf's offices, hospitals and construction sites staffed, the restoration of these low-cost routes is the difference between an affordable flight home and a months-long scramble for seats.

The Iran-Israel conflict that flared earlier in 2026 closed swathes of West Asian airspace, forcing carriers to reroute, thin out or suspend services across the region. Air India Express — the Tata Group's low-cost arm — pulled back hard, cancelling and pausing flights to several Gulf cities as overflight restrictions made schedules unworkable and fuel costs spiked. Muscat was among the first destinations to come back online; the rest of the Gulf followed in phases as authorities eased the restrictions.

## Bengaluru Leads the Recovery

The carrier's largest base, Kempegowda International Airport, has been the centre of the rebuild. According to the airline's latest network update, Air India Express has resumed service from Bengaluru to Abu Dhabi, Jeddah, Riyadh and Kuwait. More notably, it launched its first-ever flights from Bengaluru to Dubai and Doha in early June — new routes rather than mere restorations, signalling that the airline sees structural demand in the South, not just a temporary bounce-back.

The expansion does not stop at Bengaluru. Air India Express has also restored Gulf links from a long list of southern cities — Kochi, Kozhikode, Kannur, Mangaluru, Tiruchirappalli and Thiruvananthapuram — the airports that feed Kerala's and coastal Karnataka's vast expatriate workforce. Northern hubs including Delhi, Amritsar, Jaipur, Lucknow, Hyderabad, Mumbai and Varanasi have regained their Gulf services as well.

https://x.com/AirIndiaX

## Why the South Matters Most

The geography of this recovery is not an accident. The Gulf is home to one of the largest concentrations of overseas Indians anywhere, and a disproportionate share of that population traces back to Kerala, coastal Karnataka, Tamil Nadu and the Telugu states. These are the workers who send home the remittances that prop up entire local economies, and they fly on exactly the kind of point-to-point, no-frills routes that Air India Express specialises in.

That traffic is what the industry calls VFR — visiting friends and relatives — supplemented by labour migration. It is steady, year-round and relatively price-sensitive, which makes it both lucrative and fragile. When fares spike or flights vanish, families ration trips home, miss weddings and funerals, and pay through the nose for one-stop alternatives via Dubai or Sharjah on full-service carriers.

## What It Means for NRIs

For the Indian American reading this from afar, the relevance is indirect but real. Many US-based NRIs have extended family working in the Gulf, and Gulf hubs like Dubai, Abu Dhabi and Doha are also major one-stop gateways between India and North America. A healthier, denser Air India Express network across the Gulf strengthens the broader connective tissue of the diaspora — and signals that the Tata-owned group is willing to invest in secondary Indian cities rather than concentrating everything in the metros.

There is a note of caution. Air India Group has signalled it is re-evaluating its fleet and growth plans, with reports of deferred aircraft deliveries amid supply-chain constraints. Against that backdrop, the decision to pour capacity back into the Gulf is telling: it is the airline's most established and dependable international market, and the one it trusts to recover fastest.

## What's Next

Air India Express currently serves 17 international destinations and operates more than 500 flights a day with a fleet of Boeing 737 and Airbus A320-family jets. As regional stability holds, expect the carrier to add frequencies on the busiest Gulf sectors before opening genuinely new city pairs. For families watching fares from Kochi to Doha or Bengaluru to Dubai, the trend line — for now — finally points down."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The India Fare Math for This Summer: Why September Beats July by Hundreds of Dollars",
        "subheadline": "Peak-summer roundtrips from the US to India are running $1,300-$2,000, but the same routes drop toward $850-$1,050 once the calendar flips to September and October — here is the booking window NRIs should be watching.",
        "slug": make_slug("us-india-summer-airfare-guide-september-savings-nri"),
        "category": "travel",
        "vertical": "travel-deals",
        "diaspora_angle": "For the millions of Indian Americans planning a trip home, shifting departure dates by a few weeks into the shoulder season can cut a family of four's airfare by thousands of dollars.",
        "tags": ["travel", "flight-deals", "airfare", "us-india", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "momondo — India to US fares", "url": "https://www.momondo.com/flights/india/united-states"},
            {"name": "United Airlines — India to US fares", "url": "https://www.united.com/en/us/fly/deals/flights-from-india-to-united-states.html"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12940608/pexels-photo-12940608.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An airport departure board — timing, more than luck, drives the price of a US-India ticket.",
        "image_attribution": "Pexels",
        "body": """If you are pricing a trip home to India this summer and recoiling at the numbers, the problem may be the dates more than the destination. Current fare data across the major US-India corridors tells a consistent story: travel in late June and July, and you will pay a heavy peak-season premium; push the same trip into September and October, and the price can fall by hundreds — sometimes more than a thousand — dollars per ticket.

## The Peak-Summer Tax

The numbers are stark. Roundtrips departing in the back half of June and through July are sitting well above $1,300 on the marquee West Coast routes. San Francisco to Mumbai and San Francisco to Delhi have both been quoted around $1,375-$1,380 for late-June departures, and JFK to Mumbai near $1,540. Onward connections to the southern metros run higher still — SFO to Bengaluru in the $1,790 range, SFO to Chennai past $2,000, and Hyderabad and Ahmedabad routinely north of $2,000 for peak-summer dates.

This is the predictable consequence of demand. School is out, families travel together, and the entire diaspora tries to fly in the same eight-week window. Airlines price accordingly.

## The September Cliff

Wait a few weeks and the market changes character entirely. For September and October departures, momondo and the airlines themselves are showing SFO-Delhi roundtrips around $850, SFO-Mumbai near $870, and JFK-Delhi in the $710-$850 band. Nonstop Delhi-New York fares on a leading Gulf-free routing have shown up as low as the rupee equivalent of roughly $900 for mid-September. October is, on the data, typically the cheapest month of the year to fly between India and North America.

The reason is the shoulder season: summer crowds have gone home, the festival rush has not yet begun, and airlines discount to fill seats. For a family of four, the gap between a July departure and a late-September one can run to several thousand dollars — enough to fund the entire trip's in-country costs.

## Routes and Carriers Worth Watching

A few practical patterns stand out in the current data:

- **Newark and New York are the value gateways from the East Coast.** United has shown Delhi-Newark roundtrips from around $976 even for summer dates, and Mumbai-Newark near $1,170 — well below comparable West Coast pricing.
- **One-stop European and Gulf carriers undercut nonstops.** ITA Airways, Qatar Airways, Emirates and Scandinavian Airlines have all surfaced sub-$1,100 fares on West Coast-India routings for shoulder-season dates, the trade-off being a longer journey with a connection.
- **The South Indian metros carry a premium.** Bengaluru, Chennai, Hyderabad and Kochi consistently price above Delhi and Mumbai. If your family can route through a major metro and take a cheap domestic hop, the savings can be substantial.

## What's Next for NRIs

The takeaway is not "never fly in summer" — for families tied to the school calendar, that is not a choice. But for retirees, remote workers, and anyone with flexibility, the message from the data is unambiguous: every week you can shift a trip past Labor Day works in your favour, and the stretch from mid-September through October is the sweet spot.

One caveat looms over the autumn calendar. Diwali falls on November 8 this year, and fares to India spike sharply in the two to three weeks before it as the diaspora books festival travel. The cheap shoulder-season window effectively closes in late October. If you are chasing the low fares, the move is to book the September-to-mid-October band now, before the Diwali surge pulls the whole market back up.

Fares move daily and the figures here are snapshots, not guarantees. But the structure of the year — expensive summer, cheap autumn, a Diwali spike, then a winter-holiday climb — is reliable enough to plan around."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Great American Road Trip, Desi Edition: A Summer National Parks Plan for NRI Families",
        "subheadline": "With India's metros baking and US schools out, the country's national parks offer the diaspora a cooler, cheaper alternative to flying home — and a way to give kids the wide-open America their parents came for.",
        "slug": make_slug("us-national-parks-summer-road-trip-nri-families-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRI families who cannot make the expensive summer trip to India, a national-parks road trip is an affordable, multi-generational alternative that works for visiting grandparents and US-raised kids alike.",
        "tags": ["travel", "road-trip", "national-parks", "usa", "family"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "National Park Service — Plan Your Visit", "url": "https://www.nps.gov/planyourvisit/index.htm"},
            {"name": "NPS — Reservations and timed entry", "url": "https://www.nps.gov/subjects/reservations/index.htm"}
        ]),
        "score_total": 62,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Grand_Canyon_Hopi_Point_with_rainbow_2013.jpg/1280px-Grand_Canyon_Hopi_Point_with_rainbow_2013.jpg",
        "image_caption": "Hopi Point on the South Rim of Grand Canyon National Park, one of the most accessible parks for first-time visitors.",
        "image_attribution": "Wikimedia Commons",
        "body": """Not every NRI family is flying home this summer. With US-India airfares at their seasonal peak and India's metros under a brutal pre-monsoon heat, a growing number of diaspora families are doing what generations of Americans have always done in June and July: loading the car and pointing it at a national park. Done right, it is cheaper than the trip to India, easier on jet-lagged grandparents, and a way to show US-raised kids the version of America that drew their parents here in the first place.

## Why It Works for Desi Families

The national-parks road trip solves several problems at once. It is multi-generational — a visiting grandparent can sit at a scenic overlook while teenagers hike — and it scales to any budget, from tent camping to lodge stays. It avoids the 16-hour flight and the week of jet lag on both ends. And for families who keep a vegetarian kitchen, a road trip with a cooler and a rented condo or cabin gives far more control over food than a packaged tour ever will.

## The Beginner Loops

For a first big trip, three regions stand out:

- **The Southwest Grand Circle.** Anchored by the Grand Canyon, this loop strings together Zion, Bryce Canyon, Arches and Monument Valley across Arizona and Utah. The driving distances are manageable, the scenery is staggering, and Las Vegas or Phoenix make easy, well-connected starting points with plentiful Indian groceries and restaurants to stock up before you head into the parks.
- **California's giants.** Yosemite, Sequoia and Kings Canyon are within a few hours of the Bay Area's enormous NRI population — a long weekend rather than a full expedition. Yosemite Valley in particular is a gentle introduction: shuttle buses, paved trails and grand views without serious hiking.
- **The Northern Rockies.** Yellowstone and Grand Teton, usually paired, are the splurge option — farther to reach but unmatched for wildlife. Salt Lake City and Bozeman are the practical gateways.

## The Catch Nobody Mentions: Reservations

Here is the single most important thing for a first-time park visitor to understand: many of the marquee parks now require timed-entry or vehicle reservations during the summer peak, booked weeks in advance through the National Park Service's reservation system. Show up at the gate of a park under a timed-entry rule without a booking, and you may simply be turned away during peak hours.

Lodging is the other bottleneck. In-park lodges at Yosemite, the Grand Canyon and Yellowstone book out months ahead for summer. If those are gone, gateway towns just outside the boundary are the fallback, and a vacation rental with a kitchen is often both cheaper and more practical for a large family than two hotel rooms.

A few practical notes that matter for diaspora families specifically: the America the Beautiful annual pass, at $80, covers entry to every federal park and pays for itself in three or four visits — worth it if you will do more than one park. Summer temperatures in the Southwest parks routinely top 100°F, so the hiking is best done early; carry far more water than you think you need. And cell coverage inside most parks is effectively nonexistent, so download maps offline before you lose signal.

## What's Next

If the full road trip feels ambitious this year, treat a single nearby park as a trial run — a weekend at Yosemite from the Bay Area, Shenandoah from the DC corridor, or the Great Smoky Mountains from Atlanta or Nashville. The Smokies, notably, charge no entrance fee at all. Start small, learn the rhythm of early starts and packed coolers, and build toward the big Southwest loop next summer. The parks are not going anywhere — but the summer reservation windows fill fast, so the planning, at least, should start now."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
