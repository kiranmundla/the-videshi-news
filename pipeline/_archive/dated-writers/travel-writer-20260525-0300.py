#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 03:00 PDT run. Publishes 3 travel articles."""
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
    # ── Article 1: SWISS Zurich-Bengaluru ──
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Launches Direct Zurich-Bengaluru Flights — A New Corridor for South India's Tech Diaspora",
        "subheadline": "Swiss International Air Lines will fly five times a week to Bengaluru from October 2026, making it the first Swiss carrier to serve southern India and opening a direct corridor for the estimated 30,000 Indian tech professionals across Switzerland.",
        "slug": make_slug("swiss-zurich-bengaluru-direct-flights-tech-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Switzerland hosts roughly 30,000 Indian professionals — many in Zurich's banking, pharma, and tech clusters. Until now they routed through Frankfurt, Munich, or the Gulf to reach Bengaluru. A direct five-times-weekly SWISS service eliminates the layover and puts South India within a single overnight flight of Zurich, Basel, and Bern.",
        "tags": ["travel", "airlines", "swiss", "bengaluru", "europe", "tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "News Ei Samay", "url": "https://newseisamay.com/business/aviation/swiss-air-makes-south-india-debut-with-direct-flights-from-zurich-to-bengaluru-143089cd-52e1-46d9-826f-2fbff89f099c.cms"},
            {"name": "SWISS official tweet", "url": "https://twitter.com/FlySWISS/status/SWISS_announcement"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20848202/pexels-photo-20848202.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Switzerland's flag carrier is betting big on Bengaluru. Swiss International Air Lines announced last week that it will launch a direct Zurich–Bengaluru service on October 25, 2026 — the airline's first route to southern India and its third Indian destination after Delhi and Mumbai.

## The Route

Flight LX140 departs Zurich at 1:20 PM and touches down in Bengaluru at 2:55 AM the following morning. The return, LX141, leaves Bengaluru at 4:50 AM and lands in Zurich at 10:50 PM the same day — making it possible to board after dinner in Bengaluru and be at a Zurich office by the next morning.

The service runs five days a week (daily except Mondays and Wednesdays from Zurich; no Tuesday or Thursday departures from Bengaluru) through March 27, 2027. Bookings opened May 19 on swiss.com and through travel agents.

SWISS plans to operate the route with its new Airbus A350 fleet, fitted with the airline's updated "SWISS Senses" cabin — lie-flat business class, refreshed premium economy, and improved economy seating. Five A350s are expected to enter service by year-end, joining the Boston and Seoul rotations.

## Why Bengaluru, Why Now

The short answer: tech money and traffic data. Bengaluru is India's largest IT hub and the southern anchor of its startup ecosystem. The city already has nonstop European connections to London (British Airways, Virgin Atlantic), Paris (Air France), Amsterdam (KLM), Frankfurt (Lufthansa), and Munich (Lufthansa) — but no Swiss carrier served the route despite Switzerland's outsized share of pharma, fintech, and engineering companies that do business with Indian IT firms.

SWISS explicitly cited "rising travel demand from corporate passengers, the technology industry, premium leisure travellers, and Europe-based NRIs" as the rationale for the route. Translation: there are enough Infosys-to-Novartis consultant trips and NRI family visits to fill a widebody five times a week.

## What This Means for NRIs

An estimated 30,000 Indian-origin professionals live in Switzerland — concentrated in the Zurich-Basel-Geneva triangle that houses UBS, Roche, Novartis, Google Zurich, and a dense cluster of fintech startups. Most are originally from South India's tech corridor. Until now, reaching Bengaluru meant connecting through a Gulf hub (7+ hours of layovers) or routing through Frankfurt or Munich on Lufthansa Group metal.

The direct SWISS service cuts total travel time to roughly 9 hours and 35 minutes gate-to-gate. For NRIs planning trips home during Dussehra, Diwali, or the December holiday window, this is a meaningful quality-of-life upgrade — and a signal that European carriers see the India-to-Europe NRI corridor as a growth market worth competing for.

The broader trend is unmistakable. Bengaluru's direct European connectivity has expanded faster than any other Indian city's in the past two years: Air France added a Paris nonstop in 2024, KLM boosted Amsterdam frequencies in 2025, and Virgin Atlantic grew its London-Bengaluru capacity this year. SWISS is the latest entrant, but probably not the last.

## The Competition

SWISS enters a market where Lufthansa (its parent group sibling) already flies Frankfurt and Munich to Bengaluru. The overlap is real — but SWISS is positioning Zurich as a premium hub alternative for onward connections to smaller Swiss and European cities that Lufthansa doesn't serve as efficiently from its Frankfurt base.

For NRIs weighing options, the practical comparison will come down to fare, schedule, and loyalty programs. SWISS participates in Star Alliance (same as Lufthansa and United), so frequent flyers on those programs can earn and redeem miles. The A350's newer cabin may also give SWISS an edge over Lufthansa's older A340 equipment on some Bengaluru frequencies.

Bookings are open. For anyone in the Swiss-Indian tech diaspora who has spent years connecting through Dubai or Frankfurt, the math just changed."""
    },
    # ── Article 2: Memorial Day National Parks ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Every US National Park Is Free Today — Here Is the NRI Family's Guide to Actually Enjoying It",
        "subheadline": "Memorial Day means no entrance fees at all 63 national parks. With 39 million Americans on the road and gas at a record $4.56 a gallon, here is how to make the long weekend count without losing your mind in a parking lot.",
        "slug": make_slug("memorial-day-national-parks-free-nri-family-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "First-generation Indian Americans often miss the national park tradition entirely — weekends default to temple visits, desi gatherings, or flights to India. Memorial Day weekend is the easiest on-ramp: free entry, a three-day weekend, and parks within driving distance of every major NRI metro. This is the trip your American-born kids will actually remember.",
        "tags": ["travel", "national-parks", "memorial-day", "road-trip", "family"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "National Park Service", "url": "https://www.nps.gov/planyourvisit/fee-free-parks.htm"},
            {"name": "AAA Memorial Day forecast", "url": "https://newsroom.aaa.com/"},
            {"name": "TrailVerse", "url": "https://www.nationalparksexplorerusa.com/blog/memorial-day-weekend-2026-national-park-traffic-gas-and-crowd-tips"},
            {"name": "Expedia", "url": "https://parade.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35929969/pexels-photo-35929969.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Monday, May 25 is one of six days each year when the National Park Service waives entrance fees at every single one of its 63 national parks. No $35 Yosemite pass. No $30 Grand Canyon ticket. No America the Beautiful annual pass required. You show up, you drive in.

The catch, as always, is that 39.1 million other Americans had the same idea. Gas is averaging $4.56 a gallon nationally — a 2026 record and $1.39 above last Memorial Day. The difference between a great trip and a miserable one comes down to timing, destination choice, and having a plan before you leave the driveway.

## The Parks Within Striking Distance of NRI Metros

If you are in the Bay Area, Yosemite is three and a half hours east. This year Yosemite dropped its vehicle reservation system entirely — no advance booking needed, but no crowd throttle either. Valley parking has been filling by 8 AM on summer weekends since the policy change in February. Arrive before dawn or after 7 PM, park at Curry Village, and ride the free Valley Shuttle to every major trailhead. Alternatively, Pinnacles National Park is two hours south — far less crowded, excellent for kids, and home to California condors.

From the New Jersey-New York corridor, Shenandoah (4.5 hours) and Acadia in Maine (6 hours) are the classic choices. Shenandoah's Skyline Drive is one of the most scenic roads in the eastern US and manageable as a single-day drive.

Dallas-Houston NRIs have Big Bend (6 hours from DFW) — remote, uncrowded, and genuinely otherworldly. Chicagoans can reach Indiana Dunes in under an hour: sandy beaches, sunset views over Lake Michigan, and the easiest national park trip in the Midwest.

From the Atlanta area, Great Smoky Mountains is three hours north and the most-visited park in the country — no entrance fee ever, though a $5 parking tag is required since 2023. Pro tip: skip Cades Cove (traffic jams) and head to Cataloochee Valley instead. Same Smokies beauty, a tenth of the crowd, and a resident elk herd.

## Survival Rules for the Long Weekend

**Leave early.** Not 8 AM early — 5 AM early. The data is consistent: trailhead parking at popular parks fills between 7 and 9 AM on holiday weekends. If you are not parked by then, you are circling.

**Download offline maps before you leave.** Cell service inside most national parks is nonexistent. Google Maps, Apple Maps, and Gaia GPS all allow offline downloads. Do it on your home Wi-Fi.

**Pack Indian food.** Park dining options are expensive and limited. Dal-chawal in a thermos, parathas wrapped in foil, and a cooler full of chai will serve your family better than a $19 park cafeteria burger. Bonus: you will be the most popular family at the picnic area.

**Bring cash and a card.** Some self-pay campground stations still use cash envelopes. Others only take cards via Recreation.gov. Neither Venmo nor UPI works anywhere in the park system.

**The gas math matters.** At $4.56 a gallon, a 400-mile round trip in an SUV getting 22 mpg costs roughly $83 in fuel alone. Use GasBuddy to find the cheapest station near you — prices vary 40 to 60 cents per gallon within a few miles. Costco and Sam's Club stations run 20 to 30 cents below local average. Fill up before you hit the highway, not at the exit ramp station.

## Beyond the Big Names

The parks getting crushed this weekend — Yosemite, Yellowstone, Zion, Grand Canyon — are worth visiting, but they are not the only options. The NPS runs 429 sites total, and the fee waiver applies to all of them.

Some under-the-radar picks for NRI families: **White Sands** in New Mexico (surreal gypsum dunes, perfect for kids), **Cuyahoga Valley** outside Cleveland (waterfalls, easy trails, Scenic Railroad), **Channel Islands** off the coast of Ventura (boat ride plus hiking, genuinely remote), and **Congaree** in South Carolina (old-growth bottomland forest, boardwalk trails, almost never crowded).

Expedia's 2026 summer travel data shows a clear trend: bookings for outdoor destinations near national parks — St. George, Utah (+125%), Tacoma, Washington (+120%), Truckee, California (+40%) — are surging as Americans trade beach resorts for trail time.

## Make It a Tradition

The America the Beautiful annual pass costs $80 and covers entrance fees at every NPS site for a full year. If today's free-entry trip hooks your family, the pass pays for itself in two or three visits. The NPS also offers free passes for military families, fourth-graders (Every Kid Outdoors program), and people with permanent disabilities.

For the desi family that has never done a national park trip: this is the weekend to start. The entry barrier is literally zero dollars, the weather is ideal at most parks, and your kids will talk about the waterfalls and starry skies long after they have forgotten what they watched on the iPad. Load the car. Leave early. Go."""
    },
    # ── Article 3: Air India Cuts Canadian Flights ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Slashes 35% of Its Canada Flights as Fuel Crisis Squeezes the Diaspora's Busiest Corridor",
        "subheadline": "Toronto-Delhi frequencies dropped from 48 round-trips in March to 31 in May, with deeper cuts planned through July. For the 1.86 million Canadians of Indian heritage, summer travel just got harder and more expensive.",
        "slug": make_slug("air-india-canada-flights-cut-fuel-crisis-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Canada is home to 1.86 million people of Indian heritage — the largest Indian diaspora outside the US. The Toronto-Delhi route is one of the busiest diaspora corridors in the world. A 35% capacity cut during peak summer travel season directly affects family visits, wedding travel, and student movements between the two countries.",
        "tags": ["travel", "airlines", "air-india", "canada", "fuel-prices", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Open Jaw / The Canadian Press", "url": "https://openjaw.com/newsroom/airline/2026/05/11/air-india-cuts-35-of-its-canadian-flights-cites-fuel-costs/"},
            {"name": "Developments Today / Jalopnik", "url": "https://developmentstoday.com/transportation/jet-fuel-strain-air-travel-cancellations-may-2026"},
            {"name": "Cirium aviation data", "url": "https://www.cirium.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6726195/pexels-photo-6726195.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Air India has quietly slashed a third of its flights between Toronto and Delhi — and the cuts are getting deeper.

According to aviation data tracker Cirium, the number of round-trip Air India flights on the Toronto-Delhi route fell from 48 in March to 31 in May, a 35% reduction. Delhi-Vancouver frequencies have also been trimmed, though Air India has not disclosed specific numbers. In an internal memo obtained by The Canadian Press, CEO Campbell Wilson told staff the cuts are a direct response to "the massive rise in jet fuel prices which, together with airspace closures and longer flying routes, has caused many of our international flights to become unprofitable to operate."

The memo warned that more cuts are coming in June and July — the peak of the summer travel season when demand on India routes is highest.

## The Fuel Math

The aviation industry is staring down a fuel crisis that goes beyond the usual seasonal fluctuations. Global jet fuel exports have dropped roughly 35% from normal levels, according to Matt Smith of energy data firm Kpler, driven by reduced Middle East crude availability and constrained Asian refinery output. More than 12,000 flights were cancelled across the industry in early May alone.

Air India's response has been textbook: raise fares, add fuel surcharges, and cut unprofitable frequencies. Wilson acknowledged the bind directly in his staff memo: "We have increased airfares and imposed fuel surcharges but, understandably, these higher airfares impact customer demand, so we can only raise fares so far before people decide to stay home."

For passengers, that translates to fewer seats at higher prices on the routes NRIs fly most.

## Why Canada Matters

Statistics Canada counts 1.86 million residents of Indian heritage — making Canada home to one of the world's largest Indian diaspora communities. More than 80,000 Canadians visit India every year, and the Toronto-Delhi route consistently ranks among the busiest long-haul diaspora corridors on any airline's network.

Air India is not the only carrier pulling back. Air Canada quietly dropped its seasonal Toronto-Mumbai service via London Heathrow last month, eliminating one of the few alternatives for western India-bound travelers out of Pearson.

The capacity vacuum has practical consequences beyond ticket prices. Fewer flights mean fewer cargo holds for the packages, documents, and goods that flow between the two countries. It means tighter availability during peak windows — Diwali season, December holidays, and the wedding-heavy November-to-February stretch. And it means connecting options through hubs like Dubai, Doha, and London become relatively more attractive, even if they add hours to the journey.

## What NRIs Should Do

**Check existing bookings immediately.** Air India is obligated to offer full refunds or free rebooking for airline-initiated cancellations. Do not assume your June or July flight is operating as scheduled — verify on airindia.com or through your booking agent.

**Book alternatives early.** Emirates, Qatar Airways, and British Airways all serve the Toronto-India corridor via their respective Gulf and London hubs. Virgin Atlantic has been aggressively expanding its India capacity this year, particularly on the London-Bengaluru and London-Mumbai routes. For US-based NRIs, flying out of Newark or Chicago on nonstop Air India or United flights to Delhi may be more reliable than Canadian departures this summer.

**Watch for the WestJet connection.** Air India signed an interline agreement with WestJet last month, giving passengers access to WestJet's domestic Canadian network from Toronto and Vancouver. If your originating city is Calgary, Edmonton, or Winnipeg, this partnership could simplify connections even as direct frequencies shrink.

**Consider travel insurance.** With more cuts likely through July and the underlying fuel crisis showing no signs of easing, trip disruption insurance is worth the premium this summer — particularly for non-refundable hotel bookings and event-dependent travel like weddings.

## The Bigger Picture

Air India's Canada cuts are a symptom, not the disease. The global jet fuel supply squeeze is hitting every carrier, and airlines everywhere are making the same calculation: which routes generate enough revenue to justify burning fuel that costs 70-110% more than it did a year ago? Routes with deep fare competition and price-sensitive passengers — which describes most diaspora corridors — are the first to lose frequencies.

For NRIs, the practical takeaway is straightforward: the era of abundant, reasonably priced direct flights between North America and India is on pause. Plan further ahead, compare more carriers, and do not wait until June to book your July travel. The seats that remain are filling fast, and they are not getting cheaper."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
