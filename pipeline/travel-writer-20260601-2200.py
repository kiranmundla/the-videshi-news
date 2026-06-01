#!/usr/bin/env python3
"""Travel writer — 2026-06-01 22:00 UTC batch"""

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


# ─────────────────────────────────────────
# ARTICLE 1: FIFA World Cup 2026 NRI Guide
# ─────────────────────────────────────────

article1_body = """The FIFA World Cup kicks off on June 11 at Estadio Azteca in Mexico City, and for the first time, the tournament sprawls across three countries — the United States, Mexico, and Canada — with 48 teams, 104 matches, and 39 days of football spread across 16 host cities. For the estimated 4.4 million Indian Americans living in the US, this is the most accessible World Cup in history. No transatlantic flights. No visa gymnastics. Just drive, fly domestic, or hop a short cross-border trip to catch the biggest sporting event on the planet.

## Where the Games Are — and Where NRIs Live

Eleven US cities host the bulk of the fixtures: Atlanta, Boston, Dallas, Houston, Kansas City, Los Angeles, Miami, New York/New Jersey, Philadelphia, San Francisco Bay Area, and Seattle. Every knockout match from the quarterfinals onward is on American soil, with the final at MetLife Stadium in East Rutherford, New Jersey on July 19.

The overlap with major Indian American population centres is not a coincidence — it is an opportunity. The Bay Area alone is home to roughly 770,000 Indian Americans. Houston, Dallas-Fort Worth, the NYC metro area, and Atlanta each have communities exceeding 200,000. Levi's Stadium in Santa Clara, where group stage and Round of 32 matches will be played, sits less than 15 minutes from the heart of Cupertino and Sunnyvale.

Tickets for group stage matches have ranged from $35 to $300 on FIFA's official portal, though resale prices for high-demand matches in metros like LA, Miami, and NYC are already running three to five times face value.

## The Mexico Games — and Why Your US Visa Is Your Ticket In

Mexico hosts 10 matches across three cities: Mexico City (Estadio Azteca, capacity 87,523), Guadalajara (Estadio Akron, 46,355), and Monterrey (Estadio BBVA, 51,000). The opening match — Mexico vs South Africa on June 11 — makes Azteca the first stadium in World Cup history to host matches in three different tournaments (1970, 1986, 2026).

For Indian passport holders with a valid, multiple-entry US visa, Mexico allows visa-free entry for up to 180 days. No separate application, no embassy visit. You land, show your Indian passport and US visa, and you are in. This makes the Mexico leg of the World Cup remarkably accessible for NRIs who might want a long weekend of football and tacos without the paperwork.

**One caveat**: The US State Department currently rates the state of Jalisco — where Guadalajara is located — at Level 3 ("Reconsider Travel") due to violent crime. Guadalajara's metropolitan area itself has no specific restrictions for tourists, but the advisory urges caution, particularly when driving at night. Monterrey's Guadalupe suburb, where Estadio BBVA sits, carries a Level 2 advisory. Mexico City is Level 2.

## Canada — Toronto and Vancouver

Canada hosts 10 matches in Toronto (BMO Field, 30,000 capacity) and Vancouver (BC Place, 54,500). Indian passport holders need a Canadian visa or eTA to attend — there is no visa-free shortcut here. Those already holding a valid Canadian visa or who are Canadian residents are set; everyone else should apply now, as processing times can stretch to several weeks during peak summer.

## Practical Tips for NRI Fans

**Book accommodation now.** Hotel rates in host cities are already elevated. In the NYC metro, expect rates to double around the July 19 final. Airbnbs in Houston, Dallas, and the Bay Area for June group-stage weekends are still available but filling fast.

**Domestic flights will be squeezed.** The 250 daily domestic flight cuts by Air India and IndiGo from June do not directly affect US domestic routes, but jet fuel prices — still elevated from the Iran crisis — have pushed average US domestic fares up 25% year-over-year. Book early, consider Southwest or budget carriers, and look into Amtrak for the Boston-New York-Philadelphia corridor, where three host cities are connected by rail.

**Get FIFA's official app.** Tickets, schedules, real-time match updates, and stadium maps are all centralised there. Fan Fest locations — free outdoor screenings — will be announced for each host city closer to kickoff.

**If you are heading to Mexico, bring cash.** Card acceptance is widespread in Cancún and Mexico City tourist zones, but around stadiums and street vendors, pesos are king. ATMs at Mexican airports offer competitive exchange rates.

India is not in the tournament — the country's FIFA ranking sits outside the top 100 — but that has never stopped Indian fans from adopting teams. Brazil, Argentina, Germany, and Portugal jerseys will likely outnumber any other nation's at NRI watch parties from Jersey City to Fremont."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Cup Starts in 10 Days — Here Is the NRI's Complete Guide to Attending",
    "subheadline": "Forty-eight teams, 16 host cities across the US, Mexico, and Canada, and the most accessible World Cup Indian Americans have ever had. What you need to know about tickets, travel, visas, and the Mexico games.",
    "slug": make_slug("world-cup-2026-nri-travel-guide-us-mexico"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "11 of the 16 host cities overlap with major Indian American population centres. Mexico is visa-free for Indians with a valid US visa. This is the most geographically convenient World Cup NRIs have ever had access to.",
    "tags": ["travel", "world-cup", "fifa", "sports", "mexico", "visa"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "FIFA", "url": "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026"},
        {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/soccer/worldcup/2026/05/27/when-does-the-world-cup-start-dates-schedule/84016972007/"},
        {"name": "People", "url": "https://people.com/everything-to-know-about-the-2026-world-cup-11736992"},
        {"name": "US State Department", "url": "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories/mexico-travel-advisory.html"},
        {"name": "Voye Global", "url": "https://www.voyeglobal.com/countries-indians-can-visit-with-us-visa/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Metlife_stadium_%28Aerial_view%29.jpg",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article1_body.strip()
}


# ─────────────────────────────────────────
# ARTICLE 2: Vande Bharat Fleet at 164
# ─────────────────────────────────────────

article2_body = """Indian Railways now operates 164 Vande Bharat services, a number that would have been unthinkable five years ago when the programme had exactly two trains. Add 68 Amrit Bharat services — three of which were inaugurated in May alone — and the picture is of a national railway system in the middle of a wholesale fleet transformation. For NRIs heading home this summer, the train their parents talk about is no longer a single showcase route. It is the system.

## The Sleeper Variant Changes the Equation

The biggest shift for long-distance travellers came on January 17, when Prime Minister Modi flagged off the first Vande Bharat Sleeper Express between Howrah and Kamakhya (Guwahati). The 968-kilometre overnight run takes 14 hours, connecting eastern India with the northeast through 13 stops including Malda Town, New Jalpaiguri, and New Cooch Behar.

The train carries 16 coaches: 11 AC three-tier, four AC two-tier, and one AC first class. Fares start at ₹2,300 for third AC, ₹3,000 for second AC, and ₹3,600 for first AC. Crucially, Indian Railways has confirmed that the Sleeper Vande Bharat does not issue waitlist or RAC tickets — every berth sold is a confirmed berth, a policy aimed at predictable occupancy and a smoother experience.

For NRIs accustomed to the Rajdhani's uncertain waitlists and the unpredictable cleanliness of older rolling stock, this is significant. The interiors feature ergonomic berths with improved cushioning, larger windows, automatic doors, and modern air conditioning. Indian Railways plans to roll out 12 Sleeper Vande Bharat routes by March 2027, targeting corridors of 1,200 to 1,500 kilometres.

## 18,262 Summer Special Trips

Running alongside the regular fleet, Indian Railways has deployed 18,262 summer special train trips between April 15 and July 15, 2026 — the largest seasonal surge capacity in recent years. The services target high-traffic corridors connecting metros with hinterland destinations: New Delhi to Mumbai, Pune, Surat, Ahmedabad, and Bengaluru feature heavily.

Over 11,800 of these trips had been notified by late May, with the remainder being announced in phases. Union Railway Minister Ashwini Vaishnaw personally reviewed summer operations, underscoring the political visibility of getting this right during peak travel season.

For NRIs with family in smaller cities — the Kanpurs, Patnās, and Bhubaneswars that once required two connections and a prayer — the special services offer direct or semi-direct routes that did not exist a decade ago. Bookings for these trains go through IRCTC in the standard way, but availability is tighter than regular services, so booking windows matter.

## What NRIs Will Actually Notice

The Vande Bharat experience on popular daytime routes — Delhi-Jaipur, Mumbai-Goa, Chennai-Mysuru, Bengaluru-Dharwad — is materially different from what most NRIs remember of Indian train travel. Reclining chairs, onboard catering from IRCTC's improved menu, Wi-Fi on select trains, and GPS-based announcements make the experience closer to European regional rail than the long-distance Indian trains of memory.

The stations are another matter. While select stations on the Amrit Bharat Station scheme have received facelifts (LED lighting, improved waiting areas, accessible ramps), most junction stations remain works in progress. NRIs arriving at Howrah or New Delhi will find pockets of renovation alongside the familiar chaos.

Booking remains IRCTC's domain. For NRIs, the IRCTC website and app accept international credit cards and offer a foreign tourist quota on select trains. The e-ticket process is straightforward, but requires an Indian mobile number for OTP verification — a hurdle that catches many returning NRIs off guard. A workaround: register with a family member's number before you fly.

## The Bigger Picture

India's rail modernisation is now visible at fleet scale, not just on showcase corridors. The Vande Bharat programme has moved from prestige project to operational backbone, and the Sleeper variant opens it to the overnight journeys that still define long-distance Indian travel. For NRIs planning summer trips home, the advice is simple: try the train. It is not the one you remember."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Vande Bharat Fleet Just Hit 164 Services — and NRIs Heading Home Will Find a Different Railway",
    "subheadline": "From a single showcase route to 164 services, a sleeper variant, and 18,000 summer specials, Indian Railways has transformed faster than most NRIs realise. A practical guide for the summer trip home.",
    "slug": make_slug("vande-bharat-164-services-nri-summer-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs heading home this summer will encounter a materially different Indian Railways — 164 Vande Bharat services, a new sleeper variant, and 18,262 summer specials. The IRCTC booking process still requires an Indian mobile number, catching many NRIs off guard.",
    "tags": ["travel", "indian-railways", "vande-bharat", "trains", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wikipedia - Vande Bharat Sleeper Express", "url": "https://en.wikipedia.org/wiki/Vande_Bharat_Sleeper_Express"},
        {"name": "Drivespark", "url": "https://www.drivespark.com/four-wheelers/2026/pm-modi-flags-off-india-first-vande-bharat-sleeper-train-055131.html"},
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national-news/indian-railways-summer-special-trains-2026/"},
        {"name": "NewKerala", "url": "https://www.newkerala.com/news/2026/73927.htm"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Vande_Bharat_Express_around_Mumbai.jpg",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article2_body.strip()
}


# ─────────────────────────────────────────
# ARTICLE 3: Pune Metro Line 3
# ─────────────────────────────────────────

article3_body = """Pune's Metro Line 3 — the 23-kilometre elevated corridor connecting the Hinjewadi IT hub to Shivajinagar in central Pune — is finally approaching its launch after years of delays, missed deadlines, and the kind of bureaucratic stop-start that has become a running joke among Punekars. The Commissioner of Metro Rail Safety inspection is expected in early June, with the first phase now targeted for a July opening. For the Indian diaspora, and particularly for the tens of thousands of NRIs with professional, familial, or real estate ties to Pune's booming tech corridor, this is infrastructure that changes the daily calculus of life in India's second-largest IT city.

## What Line 3 Actually Connects

The corridor runs from Maan-Hinjewadi (Phase III of Rajiv Gandhi Infotech Park) to Civil Court in Shivajinagar, with 23 stations along the route. The first phase will open 12 stations between Hinjewadi and Balewadi, covering the IT belt where companies like Infosys, Wipro, TCS, Cognizant, and dozens of mid-tier IT services firms employ hundreds of thousands.

The second phase — Balewadi to Civil Court — is expected by October, completing the connection to Shivajinagar, where commuters can interchange with the existing Pune Metro network (Line 1 running PCMC-Swargate, Line 2 running Vanaz-Ramwadi).

The project is a public-private partnership, with the Tata Group's Pune IT City Metro Rail as the special purpose vehicle and Alstom supplying the rolling stock — 22 trains of three coaches each. Maharashtra Metro Rail Corporation (Maha-Metro) is evaluating an upgrade to six-coach formations on existing lines to handle the expected ridership surge. Current daily passenger volumes across Pune Metro's two active lines average 1.87 lakh; projections suggest that could jump to 2.75–3 lakh once Line 3 opens, a nearly 50% increase.

## Why NRIs Should Care

Pune has quietly become the city that NRIs cannot avoid. It is India's second-largest IT employment centre after Bengaluru, and for many Indian Americans working in tech, Pune is where the offshore team sits, where the quarterly review happens in person, and where parents or siblings increasingly live. The Hinjewadi-Wakad-Baner corridor has seen explosive residential growth driven almost entirely by IT employment, and property prices have climbed steadily — a 23% increase in Wakad over the past three years, according to MagicBricks data.

Until now, reaching Hinjewadi from anywhere in Pune has meant enduring one of the city's worst traffic bottlenecks. The 18-kilometre drive from Shivajinagar to Hinjewadi routinely takes 60 to 90 minutes during peak hours, sometimes longer. For NRIs visiting on business — often shuttling between a hotel in central Pune and meetings in Hinjewadi — this commute eats into an already compressed schedule.

Line 3 is designed to cut that journey to under 40 minutes, with trains running at intervals of five to eight minutes during peak hours. For NRIs who visit Pune regularly on L-1 or B-1 assignments, this is the difference between a manageable day trip from a Koregaon Park hotel to Hinjewadi and a logistical ordeal.

## The Delays and What They Signal

The project has missed at least five deadlines. Originally slated for March 2025, it was pushed to April, then May, then June 15, and now July 2026. The Commissioner of Metro Rail Safety inspection — the mandatory safety clearance before commercial operations — has not yet been completed, and the approval process typically takes about a month after inspection.

More than 90% of civil works are complete, trial runs on the Hinjewadi-Balewadi section have been successful, and station finishing work is in its final stages. The delays have been driven by the usual suspects: land acquisition complications, coordination between multiple agencies (PMRDA, Maha-Metro, and the Tata Group SPV), and the layered approval process that governs Indian infrastructure projects.

For NRIs with Pune real estate investments, particularly in Wakad, Baner, and Hinjewadi — areas that have seen speculative buying driven partly by metro proximity — the delays have been frustrating but the trajectory is clear. The corridor will open, and when it does, the connectivity premium on properties near Line 3 stations will crystallise.

## What Comes Next

Pune's metro ambitions extend well beyond Line 3. Extensions to Line 1 (PCMC to Nigdi, Swargate to Katraj) are underway, and Maha-Metro has proposed additional corridors including routes to Wagholi, Hadapsar, and Khadakwasla. The Purandar greenfield international airport, roughly 40 kilometres southeast, is in the land acquisition phase with a target of 2028 for Phase 1.

Pune is building the transport infrastructure of a city that expects to be much larger and much more connected in a decade. For NRIs, that means the city they visit every year or two is changing faster than they realise — and this time, the train is actually coming."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Pune's Hinjewadi Metro Is Finally Coming — and NRIs with Tech Corridor Ties Should Take Notice",
    "subheadline": "After five missed deadlines, Pune Metro Line 3 connecting India's second-largest IT hub to the city centre is targeting a July launch. Here is what it means for NRIs who visit, invest in, or have family in Pune's booming Hinjewadi-Wakad belt.",
    "slug": make_slug("pune-metro-line-3-hinjewadi-nri-it-hub"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Pune's Hinjewadi-Wakad corridor is where many NRIs' offshore teams sit, where quarterly reviews happen, and where siblings or parents increasingly live. The metro cuts a 90-minute commute to under 40 minutes — a direct quality-of-life upgrade for NRIs on L-1 or B-1 business visits.",
    "tags": ["travel", "pune", "metro", "infrastructure", "real-estate", "IT"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Infra Post", "url": "https://theinfrapost.com/pune-metro-plans-six-coach-trains-depot-expansion-line-3/"},
        {"name": "Hinjewadi 360", "url": "https://hinjewadi360.com/punes-hinjawadi-metro-may-start-only-in-july-as-cmrs-approval-still-pending/"},
        {"name": "MagicBricks", "url": "https://www.magicbricks.com/blog/pune-metro-line-3/132454.html"},
        {"name": "Urban Acres", "url": "https://urbanacres.in/pune-metro-plans-six-coach-expansion-upgrade/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Titagarh_Wagon_Pune_Metro.jpg",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": article3_body.strip()
}


# ─────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
