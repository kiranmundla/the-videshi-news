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

NZ_BODY = """New Zealand and India do not have a single nonstop flight between them. To get from Auckland to Delhi today, you route through Singapore, Sydney, or one of the Gulf hubs, and you budget the better part of a day — the cheapest itineraries clock in around 20 hours, and the convenient ones still ask for a stopover. That gap is finally on a clock.

Air New Zealand and Air India, both Star Alliance carriers, have firmed up the next stage of a partnership aimed squarely at closing it. The two airlines now run a codeshare across 16 routes linking India, Singapore, Australia, and New Zealand, and they have signed a memorandum of understanding to launch a direct India–New Zealand service by the end of 2028. The target city pair is Auckland to either Delhi or Mumbai.

### What is actually changing now

The direct flight is still years away, but the codeshare is live, and that is the part travelers can use this year. Passengers can book a single ticket on Air India from Delhi, Mumbai, Bengaluru, or Chennai, connect at Sydney, Melbourne, or Singapore, and continue on Air New Zealand metal to Auckland, Christchurch, Wellington, or Queenstown. One booking, one baggage check, coordinated connections — the practical wins of an alliance tie-up before any new aircraft arrives.

A nonstop Auckland–Delhi sector would run roughly 12,500 kilometers and 15 to 16 hours, putting it among the longest scheduled flights in the world. That distance is exactly why the route has waited this long: it needs the right ultra-long-haul aircraft, and both carriers are caught in the same Boeing and Airbus delivery backlog slowing widebody plans across the industry. The end-2028 date is a target, not a timetable, and it hinges on jets landing and regulators signing off.

### Why the math finally works

The demand case has hardened. Tourism New Zealand estimates around 18 million people across Delhi, Mumbai, and Bengaluru are actively weighing the country as a destination, and Indian arrivals have already climbed past 80,000 a year — up roughly 23% on pre-pandemic 2019. A recently concluded India–New Zealand free trade agreement adds cargo volume and corporate travel to the leisure pull. For an airline planner, that is the combination that turns a 16-hour route from a vanity project into a business.

### Why it matters to the diaspora

For Indian Americans, New Zealand is the long-haul trip that never quite gets easier. Families with relatives in Auckland — home to one of the fastest-growing Indian-origin communities in the Pacific — and the steady stream of Indian students heading to New Zealand universities currently face the same double-hop the rest of the world does: a transpacific or transcontinental leg to the US West Coast, then a second long sector down to Auckland, usually with a Gulf or Asian connection layered in.

A direct India–New Zealand link reshapes that map. An NRI in California visiting parents in Delhi and a sibling in Auckland could, by 2028, build a clean triangle — US to India, India nonstop to New Zealand, New Zealand home — instead of backtracking through a third continent. And the codeshare already simplifies the booking today: a single Star Alliance itinerary that also feeds United's transpacific network, the carrier most West Coast NRIs already fly. For the Indian diaspora that increasingly spans three countries rather than two, a Delhi–Auckland nonstop is less a tourist convenience than a family-logistics upgrade.

### What's next

Watch three signals. First, aircraft: the route depends on the A350-1000 or 777-class deliveries both airlines are awaiting, so any acceleration in those orders pulls the date forward. Second, bilateral air-rights talks, which have to expand before nonstops can be scheduled. Third, the codeshare's own performance — strong loads on the one-stop connections through Sydney and Singapore are the clearest proof the nonstop will fill. Until then, the cheapest move for an NRI planning a New Zealand trip is to price the new through-fares on Air India rather than booking the two legs separately."""

GOA_BODY = """Goa has spent decades selling the same two stories to the same two markets: sunburned package tourists from Britain and charter loads from Russia. Now the state wants new customers, and it is going looking for them in unusual places — Poland, Kazakhstan, and Uzbekistan.

State tourism officials have laid out a plan to chase direct international air links with those three countries, part of a deliberate push to diversify away from Goa's traditional reliance on the UK and Russian source markets. Talks with the central government are underway to expand international access through Goa's two airports — the older Dabolim field and the new greenfield Mopa airport in the north — with the aim of turning the destination from a winter beach stop into a year-round hub.

### The logic behind the new map

The strategy is a recognition of how the tourism business now works: destinations compete on accessibility as much as on attractions. A direct flight does not just shorten a journey — it changes whether a traveler considers the destination at all. By courting Central and Eastern European markets that currently have no easy path to Goa, the state is betting it can manufacture demand that does not exist today, rather than fighting for a bigger slice of the saturated UK charter market.

Goa is also repositioning what it sells. The pitch now leans on cultural festivals, luxury hospitality, MICE (meetings, incentives, conferences, exhibitions), the booming destination-wedding business, and experiential travel — all of it aimed at longer stays and higher per-visitor spending rather than cheap, high-volume beach packages. Officials argue that better connectivity encourages visitors to stay longer and spend more across local businesses, spreading the economic benefit beyond the shacks and into hospitality, events, and retail.

### Why it matters to the diaspora

On its face, a Poland–Goa flight has nothing to do with an NRI in New Jersey. Look closer and it does. Goa is one of the diaspora's most-used domestic destinations — the default winter-wedding venue, the family reunion spot, the place an NRI flies the US-born kids to for a week of beach before the obligatory rounds of relatives. Anything that thickens Goa's international air network changes the calculus for that traveler too.

Here is the mechanism. New international routes justify airport expansion, upgraded terminals, and more slots — infrastructure that every carrier serving Goa benefits from, not just the new entrants. They also strengthen the case for Gulf hubs to add Goa frequencies, and the Gulf is precisely how most NRIs already reach the state: a US–Dubai or US–Doha leg, then a short hop into Goa. More international demand at Mopa means more reason for Emirates, Qatar, and Etihad to thicken those connections, which in turn means more seats and better fares for the diaspora flying in from America. A Goa that is busy year-round is also a Goa where hotels, villas, and wedding venues invest — the supply NRI families lean on for big-event travel.

There is a second-order benefit. Goa's move to chase higher-spending, longer-staying visitors aligns with how the diaspora actually travels: not a weekend, but a one-to-three-week anchor trip built around a wedding or a family milestone. A destination optimizing for that profile is a destination optimizing for them.

### What's next

The Poland, Kazakhstan, and Uzbekistan routes are aspirational for now — no carrier has been confirmed, and direct service depends on bilateral agreements and an airline willing to take the risk. The nearer-term tell is capacity at Mopa: watch for new international slots, additional Gulf frequencies, and charter announcements ahead of the winter season. For an NRI planning a Goa wedding or a family trip in late 2026, the practical advice is unchanged — book the Gulf connection early — but the medium-term outlook is a better-connected, busier Goa with more ways in."""

DIWALI_BODY = """Diwali falls on November 8 this year, and the annual ritual is already underway in NRI households across America: someone in the family group chat asks when to book the India tickets, and someone else insists it is already too late. Both are usually wrong. The smarter question is not when to book but when to fly.

The structural problem is simple. Roughly five million Indian Americans, plus students and recent arrivals, all want to be in India for the same two-week window around Diwali — and increasingly around the long Thanksgiving weekend that often sits close to it. Airlines know this, and fares on the core diaspora routes — SFO and LAX to Delhi, Bengaluru, and Hyderabad; JFK and EWR to Mumbai and Ahmedabad; ORD to Hyderabad — climb steeply into the festival peak. The capacity has not kept pace either: Air India trimmed several US frequencies through the summer over airspace and fuel costs, and while seats are returning, the festival window stays tight.

### The fare math that actually saves money

The single biggest lever is date flexibility. Fares on US–India routes typically peak for departures in the seven to ten days before Diwali and for returns in the week after. Shifting either end by even a few days routinely moves the price by hundreds of dollars. Flying out in late October and returning in the first week of December — bracketing the peak rather than sitting inside it — is the classic NRI move, and it often pairs naturally with a longer trip that justifies the long-haul effort anyway.

A few concrete tactics worth pricing now:

- **Split the journey through the Gulf.** A US–Dubai/Doha/Abu Dhabi leg on Emirates, Qatar, or Etihad, then a separate hop into a smaller home city, frequently beats the nonstop or the single through-fare into second-tier airports like Ahmedabad, Kochi, or Coimbatore.
- **Fly mid-week.** Tuesday and Wednesday departures and returns are reliably cheaper than the Friday–Sunday crush, and the difference widens during the festival peak.
- **Watch the new gateways.** Capacity changes shift prices: more Gulf-carrier seats into India and new transit options through Europe and East Asia mean the cheapest routing this year may not be the one you flew last year. Price the one-stops, not just the nonstop.
- **Book the return first if it's the expensive half.** Post-Diwali returns into early November are often the pricier leg; lock that when you see a fair number rather than waiting for the outbound to drop.

### Why it matters to the diaspora

This is the diaspora's defining trip — the one non-negotiable journey on the calendar for millions of Indian American families. It is also one of the largest discretionary expenses many of them make all year, and the one where a little planning discipline returns the most. A family of four flying SFO–Delhi over the absolute peak can easily pay several thousand dollars more than the same family flying the same route ten days earlier. That gap is not a luxury-versus-economy choice; it is purely a function of which dates you pick.

There is a quieter benefit to flying the shoulder of the peak, too. Airports are calmer, the dreaded missed-connection risk at Gulf and European hubs drops, and you arrive before the family chaos of the festival rather than in the thick of it.

### What's next

Two things to monitor between now and the fall. First, US-carrier and Air India capacity on the transatlantic and transpacific legs — any restoration of trimmed frequencies eases prices, any further cuts tighten them. Second, Gulf-carrier promotions, which tend to surface in late summer and are the diaspora's most dependable source of a genuinely cheap festival-season fare. Set fare alerts on your specific city pair now, price the shoulder dates against the peak, and treat early November returns as the half of the trip most worth locking in early."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India and New Zealand Are Finally Planning a Nonstop — and the Codeshare to Use Until It Lands",
        "subheadline": "Air India and Air New Zealand are targeting a direct Auckland–Delhi or Mumbai flight by end-2028. A live 16-route codeshare already simplifies the trip today.",
        "slug": make_slug("air-india-air-new-zealand-direct-flight-2028-codeshare-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For NRIs whose families now span the US, India, and New Zealand, a Delhi–Auckland nonstop replaces a multi-continent backtrack with a clean triangle — and the new Star Alliance codeshare simplifies the booking today.",
        "tags": ["travel", "airlines", "air india", "new zealand", "star alliance", "codeshare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller — India-New Zealand Direct Flights Could Soon Take Off", "url": "https://www.outlooktraveller.com/destinations/international/india-new-zealand-direct-flights-could-soon-take-off"},
            {"name": "Air New Zealand Newsroom — Codeshare and MoU with Air India", "url": "https://www.airnewzealandnewsroom.com/media-releases"},
            {"name": "FlightGlobal — Direct New Zealand-India flights on the cards", "url": "https://www.flightglobal.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Auckland_Skyline_as_seen_from_Devonport_100128_2.jpg/1280px-Auckland_Skyline_as_seen_from_Devonport_100128_2.jpg",
        "image_caption": "The Auckland skyline seen from Devonport; Auckland is the likely New Zealand hub for a future India nonstop.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": NZ_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Goa Goes Hunting for New Tourists in Poland, Kazakhstan and Uzbekistan",
        "subheadline": "India's premier beach state wants direct flights from Central and Eastern Europe — and the airport expansion behind the push is good news for the diaspora flying in through the Gulf.",
        "slug": make_slug("goa-new-international-routes-poland-kazakhstan-uzbekistan-nri"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "Goa is the diaspora's default wedding and family-reunion destination; new international routes mean airport expansion and more Gulf-hub frequencies that translate into more seats and better fares for NRIs flying in from America.",
        "tags": ["travel", "goa", "tourism", "airports", "destination weddings"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Goa Targets Poland, Kazakhstan and Uzbekistan With New Direct Flight Plans", "url": "https://www.travelandtourworld.com/news/article/goa-india-targets-poland-kazakhstan-and-uzbekistan-with-new-direct-flight-plans/"},
            {"name": "Outlook Traveller — Goa international air connectivity", "url": "https://www.outlooktraveller.com/destinations/india/goa"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Palolem_Beach%2C_South_Goa.jpg/1280px-Palolem_Beach%2C_South_Goa.jpg",
        "image_caption": "Palolem Beach in South Goa, the kind of destination the state hopes to sell to new long-haul markets.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": GOA_BODY
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Diwali Is November 8 — Here's the Fare Math That Saves NRI Families Hundreds on the Trip Home",
        "subheadline": "The festival-season crush on US–India routes is predictable, and so are the ways around it. The smarter question isn't when to book, but when to fly.",
        "slug": make_slug("diwali-2026-us-india-airfare-guide-nri-booking-window"),
        "category": "travel",
        "vertical": "airfare",
        "diaspora_angle": "The trip home for Diwali is the diaspora's one non-negotiable journey and one of its biggest annual expenses; flying the shoulder of the peak instead of the peak itself routinely saves a family of four thousands of dollars.",
        "tags": ["travel", "airfare", "diwali", "flight deals", "air india", "gulf carriers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Air India — International network rationalisation through August 2026", "url": "https://www.airindia.com/en-us/about-airindia/press-release/"},
            {"name": "Air India Express — Fare data, US–India and Gulf routes", "url": "https://flights.airindiaexpress.com/"},
            {"name": "Fragomen — US visa appointment and travel context for Indian nationals", "url": "https://www.fragomen.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Air_India_787-8_%28VT-ANB%29.jpg/1280px-Air_India_787-8_%28VT-ANB%29.jpg",
        "image_caption": "An Air India Boeing 787-8 Dreamliner, a workhorse on the carrier's US–India routes.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": DIWALI_BODY
    }
]

# word-count sanity
for a in articles:
    wc = len(re.sub(r'[#*>\-]', ' ', a["body"]).split())
    print(f"  ~{wc} words | {a['headline'][:60]}")

print("---inserting---")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
