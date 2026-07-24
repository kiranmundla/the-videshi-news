#!/usr/bin/env python3
"""Travel writer — 3 July 2026, 07:00 PDT run."""
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
# ARTICLE 1: Air India Express Restores Full Gulf Network
# ─────────────────────────────────────────────────────────────

art1_body = """Air India Express has restored connectivity to every destination in its West Asia network. The Tata Group carrier announced on July 2 that flights to Salalah in Oman and Kuwait — the last two holdouts from the disruptions that followed the US-Iran conflict earlier this year — are back on schedule. With 780 weekly flights now connecting 18 Indian cities to 13 Gulf destinations across six countries, the airline's regional network is whole again.

## What Resumed and When

The Kozhikode–Salalah route restarted on July 2 with twice-weekly service. Kozhikode–Kuwait followed on July 3 with one weekly flight, expanding to three per week from July 5. Bengaluru–Kuwait begins July 4, also scaling to three weekly flights by July 7. All Kuwait services will operate from Terminal 4 at Kuwait International Airport.

The restoration also includes the Muscat–Mangaluru route, which resumed on July 3. Air India Express now serves two airports in Oman — Muscat International and Salalah International — and operates around 40 weekly flights from Muscat alone to seven Indian cities.

## The Gulf Network by the Numbers

Air India Express currently flies more than 500 daily flights with a fleet of over 100 Boeing 737 and Airbus A320 aircraft, connecting 43 domestic and 16 international destinations. Its West Asia footprint spans Bahrain, Kuwait, Oman, Qatar, Saudi Arabia, and the UAE.

The restoration follows a phased approach. Services to Qatar and Bahrain resumed in late April. UAE, Oman, and Saudi Arabian frequencies were boosted around the same time. Kuwait and Salalah were the final pieces, held back while the airline assessed demand and operational feasibility in a region still emerging from months of airspace uncertainty.

## Why NRIs Should Pay Attention

For the estimated 8.5 million Indians living in the Gulf states — many of whom hold OCI cards or maintain strong ties to the US — the full restoration of Air India Express's network has practical consequences. The carrier is often the cheapest option between Kerala, Karnataka, and the Gulf, a corridor that sees enormous volume from the blue-collar and white-collar diaspora alike.

The resumption also matters for NRIs in the US who transit through the Gulf on carriers like Emirates, Etihad, and Qatar Airways. With Indian carriers restoring full frequency to Gulf hubs, connecting options on the India side multiply. A traveller flying Emirates from JFK to Dubai, for instance, now has more onward connections to Kozhikode, Mangaluru, or Bengaluru on Air India Express than at any point since February.

The airline has not announced any new routes as part of this restoration, but it continues to evaluate expansion in Southeast Asia and, separately, is exploring Tbilisi, Georgia, as a potential first entry into the European market. For now, the priority is rebuilding load factors on the Gulf routes that were disrupted for nearly four months."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Express Restores Its Full Gulf Network — 780 Weekly Flights Across Six Countries",
    "subheadline": "The last holdout routes to Kuwait and Salalah are back, completing a four-month recovery from the Gulf conflict disruptions that grounded services across West Asia.",
    "slug": make_slug("air-india-express-full-gulf-network-restored-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "Restores the cheapest India-Gulf corridor used by millions of Indian workers and NRIs transiting through Dubai and Doha on US-bound routes.",
    "tags": ["travel", "airlines", "air-india-express", "gulf", "kuwait", "oman"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/VT-BXY_Air_India_Express.jpg/1280px-VT-BXY_Air_India_Express.jpg",
    "image_caption": "An Air India Express Boeing 737 on the tarmac",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: Noida International Airport Scales to 40 Flights
# ─────────────────────────────────────────────────────────────

art2_body = """India's newest commercial airport is growing fast. Noida International Airport at Jewar, which received its first passenger flight on June 15, is on track to handle 40 to 42 daily flights by mid-July — more than tripling the 12 daily services it started with. For the 46 million residents of the National Capital Region, it is no longer a ribbon-cutting curiosity but a functioning second gateway.

## From Farmland to Flight Operations

The airport's journey from groundbreaking to passenger service took just over four years. Phase I, built at a cost of ₹11,200 crore ($1.35 billion), includes a single runway and a terminal designed by Grimshaw Architects with sustainability targets including LEED Gold certification and carbon net-zero operations. The terminal's design draws from traditional Indian ghats and havelis, with landscaped courtyards built into the plan to improve natural light and ventilation.

IndiGo was the launch carrier, operating the first arrival from Lucknow and the first departure to Bengaluru. The airline plans to connect Jewar with more than 16 domestic destinations, including Hyderabad, Jammu, Chandigarh, Jaipur, Amritsar, Dehradun, Dharamshala, and smaller cities like Pantnagar, Bareilly, and Kishangarh. Akasa Air followed on day two with flights to Bengaluru and Navi Mumbai. Air India Express, originally slated to launch alongside them, has indefinitely deferred its Jewar plans as part of a broader cost-cutting exercise.

## International Flights on the Horizon

Airport CEO Nitu Samra told Business Line that international services are expected to begin later this year, with foreign carriers already expressing interest. The airport projects five million passengers in its first full year of operations — a target it has not revised despite the aviation turbine fuel (ATF) cost pressures that have led other airports to see schedule cuts.

The phased expansion plan is ambitious: Phase I handles 12 million passengers annually, with an eventual six-runway configuration capable of 70 million passengers per year. Phase III will introduce a second 4,150-metre runway and a second terminal.

## What This Means for NRIs Visiting NCR

For Indian Americans flying into Delhi-NCR, the practical question is when Jewar becomes a realistic alternative to Indira Gandhi International Airport. Not yet — but soon.

The airport sits on the Yamuna Expressway, roughly 72 kilometres from central Delhi but far more accessible for anyone heading to Noida, Greater Noida, western Uttar Pradesh, or the industrial corridors east of the capital. For the estimated 100,000-plus NRI families with roots in western UP — Agra, Aligarh, Mathura, Meerut — Jewar will eventually be the closer airport by a significant margin.

Domestic connections are the immediate draw. An NRI landing at Delhi IGI and needing to reach Lucknow, Chandigarh, or a tier-2 city can now consider routing through Jewar instead of battling IGI's congestion for a connecting flight. Once international services begin, likely on Gulf or Southeast Asian routes first, the airport could become a genuine second gateway for diaspora travellers.

The user development fee has been set at ₹490 ($5.90) for domestic departing passengers — roughly comparable to other greenfield airports. Samra acknowledged that travellers will choose between IGI and Jewar based on convenience, time of day, and destination, rather than being funnelled to one or the other.

Delhi-NCR now joins Mumbai (with Navi Mumbai's airport also opening this month), Bengaluru, and Hyderabad in the growing club of Indian metros served by multiple airports — a structural shift that could reshape how NRIs plan their trips home."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Noida's New Airport Hits 40 Daily Flights in Its First Month — and International Services Are Coming",
    "subheadline": "Jewar's greenfield airport tripled its daily flight count within weeks of opening, with IndiGo connecting it to 16 cities and foreign carriers circling for international routes later this year.",
    "slug": make_slug("noida-jewar-airport-40-daily-flights-nri"),
    "category": "travel",
    "vertical": "infrastructure",
    "diaspora_angle": "Gives NRIs with roots in western UP a closer airport than Delhi IGI, and will offer a second NCR gateway once international flights begin.",
    "tags": ["travel", "airports", "noida", "jewar", "infrastructure", "delhi-ncr"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/"},
        {"name": "Amar Ujala English", "url": "https://english.amarujaladigital.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg/1280px-Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
    "image_caption": "Inauguration of Noida International Airport at Jewar, which began commercial flights in June 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────────────────
# ARTICLE 3: Air India Reviews Restoring US/Europe Routes
# ─────────────────────────────────────────────────────────────

art3_body = """Air India is reviewing the restoration of international flights it curtailed during the Gulf crisis, CEO Campbell Wilson confirmed this week. The announcement signals potential relief for NRIs on some of the most popular corridors between India and the United States — routes that have been reduced or suspended since June.

## What Was Cut and What Might Come Back

The Tata Group airline made sweeping adjustments to its international schedule between June and August 2026, citing airspace restrictions over the Middle East and record-high aviation turbine fuel (ATF) prices. The cuts hit US-bound NRIs hardest:

- **Delhi–Chicago**: Temporarily suspended entirely
- **Delhi–San Francisco**: Reduced from 10 weekly flights to 7 through August
- **Delhi–Toronto**: Cut from 10 weekly to 5 through July, with daily service returning from August
- **Delhi–Vancouver**: Reduced from 7 weekly to 5

Mumbai–Newark, by contrast, actually increased from 3 to 7 weekly flights, while Delhi–JFK held steady at daily service. But Delhi–Newark and Mumbai–JFK were both suspended.

Across other regions, the reductions were equally steep. Delhi–Singapore dropped from 24 weekly to 14. Delhi–Melbourne went from daily to 4 per week. Delhi–Paris was halved from 14 weekly to 7. Despite all the cuts, Air India maintained more than 1,200 international flights per month across five continents.

## Why the Review Is Happening Now

Two factors are driving the reassessment. The first is airspace. Gulf tensions have eased enough for carriers to begin restoring overfly routes across the Middle East — Air India Express just completed its own full Gulf network restoration this week. The second is fuel. A decline in global crude prices has improved the economics of long-haul operations, reducing the cost penalty that made some routes commercially unviable in June.

Wilson said the decisions will hinge on "operational feasibility, passenger demand and continued stability in the region." Translation: routes with strong booking demand and reliable airspace access will come back first.

## The NRI Impact

The Delhi–Chicago suspension has been acutely felt. Chicago O'Hare is a hub for the 200,000-plus Indian Americans in the Chicagoland area, and Air India's nonstop was one of only two direct options on the corridor. Its absence has pushed passengers onto one-stop Gulf connections or rival carriers with higher fares.

The SFO reduction, from 10 weekly flights to 7, matters for the Bay Area's massive Indian population — estimated at over 300,000 in the broader metro. Losing three weekly flights reduces schedule flexibility, particularly for business travellers and families with elderly parents booking last-minute compassionate travel.

For NRIs planning late-summer or fall travel to India, the review offers cautious optimism. Delhi–Toronto's return to daily service from August is already confirmed. If Gulf airspace continues to stabilise and fuel prices hold, Chicago and the remaining SFO frequencies could follow by September.

Air India currently flies 51 weekly flights to five US cities — JFK, Newark, Washington Dulles, Chicago, and San Francisco — and operates upgraded A350-900 aircraft with 28 business-class suites on its flagship New York routes. The airline has also recently deployed its new Boeing 787-9 Dreamliner on the Mumbai–London route, introducing Premium Economy to that corridor for the first time.

The carrier is not commenting on specific restoration timelines, but NRIs tracking these routes should watch for schedule updates in mid-July, when airlines typically finalise autumn timetables."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Is Reviewing Restoration of US Routes Suspended During the Gulf Crisis",
    "subheadline": "Delhi–Chicago is still grounded and SFO is running fewer flights, but easing tensions and falling fuel prices have the airline reassessing its international cuts.",
    "slug": make_slug("air-india-us-routes-restoration-gulf-crisis-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "Directly affects NRIs in Chicago, San Francisco, Toronto, and Vancouver whose nonstop Air India options were cut or suspended during the Gulf disruptions.",
    "tags": ["travel", "airlines", "air-india", "us-routes", "gulf-crisis", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com/"},
        {"name": "Air India Newsroom", "url": "https://www.airindia.com/"},
        {"name": "Reuters", "url": "https://www.reuters.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "image_caption": "An Air India aircraft at New York JFK airport",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
