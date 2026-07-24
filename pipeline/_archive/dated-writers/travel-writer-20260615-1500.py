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
        "headline": "Your US Visa Now Unlocks Argentina — No Separate Visa Needed for Indians",
        "subheadline": "Indian passport holders with a valid US visa or Green Card can now enter Argentina visa-free for up to 90 days. For the diaspora, Patagonia and Buenos Aires just got a lot more reachable.",
        "slug": make_slug("argentina-visa-free-indians-us-visa-green-card-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indian green-card holders and H-1B workers in the US can now add Argentina to their travel list without the cost, paperwork, and weeks-long wait of a separate consular visa.",
        "tags": ["travel", "visa", "argentina", "h1b", "green-card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "KPMG Immigration Alert", "url": "https://kpmg.com/xx/en/our-insights/gms-flash-alert/flash-alert-2025-167.html"},
            {"name": "Newland Chase", "url": "https://newlandchase.com/argentina-expands-visa-free-entry-using-u-s-visas-and-green-cards/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/indian-citizens-with-valid-us-visas-can-now-visit-argentina-without-a-separate-visa.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Buenos_Aires_%2820234294752%29.jpg",
        "image_caption": "Aerial view of Buenos Aires, Argentina's capital and the main gateway for travelers from North America",
        "image_attribution": "Wikimedia Commons",
        "body": """For the growing number of Indians settled in the United States, South America has long been the continent that got skipped. The flights are long, the connections awkward, and — until recently — the Argentine visa was one more bureaucratic hurdle stacked on top of an already demanding US immigration life. That last barrier is now gone.

Under a resolution published in Argentina's Official Gazette, Indian citizens who hold a valid US visa in a qualifying category — or a US permanent resident card — can enter Argentina without applying for a separate Argentine visa. The permitted stay runs up to 90 days for tourism, extendable once for an equivalent period at the discretion of the National Immigration office.

### Who qualifies

The exemption is not blanket. It applies to Indian nationals holding a valid US visa in the B1/B2, B2, B1, J, O, P (P1, P2, or P3), E, or H-1B categories, or a valid Green Card. Travelers on other US visa types — an F-1 student visa, for instance — still need to obtain a standard Argentine visa before flying. The recognized categories cover the bulk of the working diaspora: the H-1B engineer in the Bay Area, the L-1 manager transferred to Texas, the green-card-holding family in New Jersey.

One important caveat: entry under this framework is strictly for tourism. It does not permit a change of immigration status inside Argentina, and it cannot be converted into work authorization or longer-term residence. Anyone planning to stay must still go through the regular process.

### Why this matters to NRIs

There are well over four million people of Indian origin in the United States, and a sizeable share are constrained travelers — bound by H-1B renewal cycles, visa-stamping appointments, and the general anxiety of holding a non-immigrant status. Every additional visa application is not just a fee; it is paperwork, an appointment, and the small but real risk of a denial that complicates the US record.

Argentina recognizing the US visa as proof of bona fides removes that friction entirely. It also reflects a wider trend the diaspora has quietly benefited from: countries increasingly treating a US visa as a trusted credential in its own right. Mexico has long done it. Several Balkan and Gulf states do it. Argentina's move extends that logic to one of the world's great travel destinations.

For an Indian family in California weighing a December trip, the math is now simpler. Buenos Aires is a 13-to-14-hour haul from the US East Coast and longer from the West, but it opens onto Patagonia's glaciers, the Mendoza wine country, Iguazu Falls, and a capital city often described as the Paris of South America. None of it now requires a trip to the Argentine consulate.

### The practical details

Travelers should carry the physical US visa or Green Card alongside their Indian passport, since the entry credential is the US document itself. Immigration experts advise confirming that the US visa is valid through the intended travel dates — a visa expiring mid-trip is the most common avoidable problem. As with any policy resting on a bilateral arrangement, the rules can change, so checking the Argentine embassy's current guidance before booking is prudent.

China and the Dominican Republic are covered by parallel provisions, though Chinese nationals get a shorter 30-day window. For Indians, the 90-day allowance is generous enough to cover even an ambitious multi-week itinerary across the Southern Cone.

### What's next

The policy is part of Argentina's broader push to rebuild tourism numbers, and Indian visitors — among the fastest-growing outbound markets in the world — are squarely in its sights. Argentina's ambassador to India publicly welcomed the change as "wonderful news for both countries." For NRIs, it is one less form to fill out and one more continent within reach. The only thing standing between a Bay Area H-1B holder and a steak dinner in Palermo is now just the flight."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "China Southern Launches Daily Delhi–Guangzhou Nonstop — a New Door to East Asia for NRIs",
        "subheadline": "Starting September 2026, a daily nonstop between Delhi and Guangzhou reopens a direct India–China air corridor. For diaspora travelers, it is a faster gateway to East Asia and the Pacific.",
        "slug": make_slug("china-southern-delhi-guangzhou-daily-nonstop-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "A direct Delhi–Guangzhou route gives NRIs visiting family in India a faster onward connection to East Asia, Australia, and the Pacific without the long Gulf or Singapore detours.",
        "tags": ["travel", "airlines", "china-southern", "delhi", "routes"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/china-southern-airlines-launches-daily-non-stop-delhi-guangzhou-flight-in-september-2026/"},
            {"name": "China Southern Airlines", "url": "https://www.csair.com/en/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/B-309W%40PEK_%2820191029135846%29.jpg/1920px-B-309W%40PEK_%2820191029135846%29.jpg",
        "image_caption": "A China Southern Airlines aircraft, the carrier launching the new daily Delhi–Guangzhou nonstop",
        "image_attribution": "Wikimedia Commons",
        "body": """India–China direct flights all but vanished after 2020, leaving travelers between the two giants to route awkwardly through Hong Kong, Singapore, or the Gulf. That gap is beginning to close. China Southern Airlines will launch a daily nonstop service between Delhi and Guangzhou starting September 2026, restoring one of Asia's most logical — and long-dormant — air corridors.

### A hub-to-hub link

The route pairs two of Asia's busiest aviation hubs. Delhi's Indira Gandhi International is India's largest gateway and a launchpad for outbound business travelers, students, and tourists. Guangzhou Baiyun International, in the heart of the Pearl River Delta, is one of China's most important transport hubs and a connecting point onward into East Asia, Southeast Asia, Australia, and the Pacific.

For trade, the logic is obvious. India's corporate sector maintains deep ties to Chinese manufacturing, electronics, and supply-chain ecosystems, and Guangzhou sits at the center of that world. A daily nonstop shaves hours and a connection off what is currently a tedious journey, making same-week turnarounds realistic for business travelers.

### Why this matters to NRIs

At first glance, an India–China route might seem peripheral to the Indian American story. It is not. For the diaspora, the value lies in what Guangzhou connects to. NRIs visiting family in Delhi who then need to travel onward to East Asia, Australia, or the Pacific have long been forced into circuitous routings — backtracking through a Gulf hub or paying premium fares through Singapore.

A Guangzhou hub opens a cleaner path. China Southern operates an extensive network across the Asia-Pacific from its Guangzhou base, including strong connectivity to Australia and New Zealand, home to their own large and growing Indian communities. For a family splitting time between relatives in Delhi and Sydney, or a professional shuttling between India and Southeast Asia, the new nonstop is a meaningful piece of plumbing.

It also adds competitive pressure on the broader market. More capacity between India and East Asia tends to soften fares across the board — useful for diaspora travelers who watch every dollar on multi-leg family trips.

### The bigger picture

The route reflects a cautious thaw in India–China civil aviation after years of suspended direct links. Both governments have signaled interest in restoring connectivity, and carrier-level announcements like this one are the concrete result. Delhi continues to cement its status as a global hub, adding international partnerships and routes at a steady clip; this is one more strand in that web.

Travelers should note the practical realities. A Chinese visa is required for Indian passport holders entering China, even for short stays, and transit rules vary — anyone planning to merely connect through Guangzhou should confirm whether they qualify for a transit-without-visa allowance or need a full visa. NRIs holding US or other passports face different requirements and should check accordingly before booking.

### What's next

China Southern's move may prove to be a leading indicator. If the Delhi–Guangzhou service performs, expect other Chinese and Indian carriers to revisit suspended routes, and possibly additional city pairs — Mumbai, Bengaluru, and Hyderabad are obvious candidates given their business and student traffic. For now, the diaspora gains a single daily flight, but it is a flight that reopens a door that has been shut for the better part of six years.

The service begins in September 2026; schedules and fares will be loaded into booking systems closer to launch. Travelers building complex India-plus-Asia itineraries should keep it on their radar."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "World Cup 2026 Is Triggering an Airline Boom — and NRIs Have a Front-Row Seat",
        "subheadline": "Carriers are flooding North America's host cities with new routes and bigger jets ahead of the FIFA World Cup. For the Indian diaspora across the US, Canada, and Mexico, it means more seats, more competition, and a rare summer travel windfall.",
        "slug": make_slug("world-cup-2026-airline-boom-north-america-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The World Cup capacity surge across North American host cities gives NRIs more flight options and competitive fares for summer travel — even for trips that have nothing to do with football.",
        "tags": ["travel", "airlines", "world-cup", "routes", "north-america"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/new-york-joins-los-angeles-miami-toronto-vancouver-mexico-city-and-cancun-in-global-airline-route-boom/"},
            {"name": "FIFA", "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1657324/pexels-photo-1657324.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
        "image_caption": "A packed football stadium ahead of the FIFA World Cup 2026, hosted across the US, Canada, and Mexico",
        "image_attribution": "Pexels",
        "body": """The FIFA World Cup 2026, jointly hosted by the United States, Canada, and Mexico, is doing something for North American air travel that no ordinary summer could: it is pulling forward one of the largest route expansions in recent aviation history. Airlines from Europe, Asia, the Middle East, and South America are adding routes, raising frequencies, and swapping in wide-body jets to feed the host cities. The Indian diaspora, scattered across nearly every one of those cities, is positioned to benefit — whether or not anyone in the family follows football.

### The capacity surge

Carriers are concentrating new service on the tournament's gateway airports. New York joins Los Angeles, Miami, Toronto, Vancouver, Mexico City, and Cancun in seeing a wave of fresh international connections and beefed-up frequencies. The playbook is consistent: launch direct routes into host cities, add flights on existing high-demand transatlantic and transpacific corridors, and deploy larger aircraft during peak windows.

The tournament is projected to draw millions of international visitors, and airlines are not waiting to react — they are building capacity ahead of demand. That front-loading is what creates the opportunity for everyone else flying this summer.

### Why this matters to NRIs

The Indian community in North America is overwhelmingly concentrated in exactly the metros getting the capacity boost. The tri-state area around New York, the Bay Area and Greater Los Angeles, the Toronto and Vancouver corridors, and the Texas triangle are all home to large, dense diaspora populations. When airlines add seats and aircraft to these markets, two things tend to happen that help NRIs directly.

First, more seats mean more availability on the very routes families rely on — including the long-haul connections back to India that funnel through these hubs. A larger jet on a New York or Toronto leg can ease the bottleneck on award seats and last-minute bookings during the crunch of summer travel.

Second, added competition softens fares. Even travelers with no interest in the World Cup benefit from the spillover: a route launched to serve football fans still sells its empty seats to anyone, and carriers fighting for the same corridor tend to price more aggressively. For a diaspora family planning a summer India trip or a domestic North American holiday, the expanded schedule is a quiet windfall.

### The flip side — plan around the crowds

The same surge that adds seats also adds chaos. Host-city airports will see record passenger volumes during match windows, and security lines, immigration queues, and ground transport will all feel the strain. NRIs flying through New York, Los Angeles, Miami, Toronto, or Mexico City during the tournament should build in extra buffer time and, where possible, book early — the cheapest seats on these newly busy routes will go first.

Hotel pricing in host cities will spike around match dates, so families traveling for non-football reasons may want to time trips to avoid the peaks, or stay in suburbs with good transit links. Mexico's host cities, Mexico City and Cancun and Guadalajara, are particularly relevant for US-based NRIs, who can enter Mexico visa-free on a valid US visa — a combination that makes a World Cup-season escape unusually easy to arrange.

### What's next

Expect schedules to keep evolving as the tournament approaches and airlines fine-tune capacity to actual demand. The smart move for diaspora travelers is to watch the host-city routes now: the window where new capacity outruns booked demand is exactly when the best fares appear. Whether the goal is a match ticket or simply a well-timed family trip, 2026's football-fueled airline boom is a rare case of a global event making travel easier for people who never set foot in a stadium."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
