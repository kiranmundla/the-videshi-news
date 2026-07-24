#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 07:00 PDT batch."""
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

# ── Article 1: H-1B Green Card Rule ──────────────────────────────

art1_body = """The US Citizenship and Immigration Services dropped a policy memo last week that amounts to the most disruptive change to employment-based immigration in a generation: most people on temporary visas who want a green card must now leave the country and process through a US consulate abroad. Adjustment of status inside the United States — the mechanism that has allowed hundreds of thousands of H-1B holders to transition to permanent residency without boarding a plane — will henceforth be granted only in "extraordinary" cases.

For the roughly 1.2 million Indian-origin families currently in the employment-based green card backlog, this is not an abstract policy shift. It is a logistics problem with an airline ticket attached.

## What Changed, Precisely

Until last week, an H-1B worker whose priority date became current could file Form I-485 and adjust status domestically — continuing to work, keeping their children in school, maintaining health insurance. The new USCIS memo reverses that default. Applicants are now expected to return to their home country and appear at a US embassy for consular processing.

USCIS spokesperson Zach Kahler framed the change as restoring "the original intent of immigration law," arguing that in-country adjustment was being treated as a right rather than a discretionary exception. Immigration attorneys see it differently. Shev Dalal-Dheini of the American Immigration Lawyers Association called it an attempt to "upend decades of processing."

## Why the Diaspora Should Pay Attention

Indians hold approximately 71% of all approved H-1B applications. The EB-2 and EB-3 backlogs for India-born applicants stretch beyond a decade. Many of these workers have American-born children, US mortgages, and entire professional lives built around the assumption that they would not have to uproot for a consular interview.

Now they may need to. That means booking a flight to Delhi, Mumbai, Hyderabad, or Chennai — cities where US consulate appointment wait times already run months long. Former White House advisor Ajay Bhutoria put it bluntly: "This puts 1.2 million Indian Americans and their families in limbo after they followed every law, paid taxes, and waited legally for decades."

## The Travel Fallout

The practical implications are immediate. If even a fraction of the backlog begins consular processing in the coming year, demand for India-bound flights on key corridors — SFO–DEL, JFK–BOM, ORD–HYD, EWR–BLR — will spike. Summer 2026 fares are already elevated, with round-trips on Air India and United running $1,100–$1,500 on popular routes. A wave of forced consular trips could push peak-season pricing higher still.

There is also the question of timing. Consular appointments are notoriously difficult to schedule. The Chennai consulate, which handles a disproportionate share of H-1B-related cases, has historically had wait times exceeding six months for immigrant visa interviews. Workers who must travel for processing face not just airfare costs but potential gaps in employment authorization, disrupted schooling for children, and the logistical burden of maintaining two households.

## What NRIs Should Do Now

Immigration attorneys are advising H-1B holders to consult legal counsel immediately, particularly those with pending I-485 applications. For those whose priority dates are approaching, the calculus has changed: locking in consular interview slots early may be more important than waiting for domestic processing windows that may not reopen.

From a travel standpoint, the smart move is to monitor fare trends on diaspora-heavy routes and consider booking flexible tickets for late 2026 or early 2027. Airlines with robust India networks — Air India, United, Emirates, and Qatar Airways — are likely to add capacity if demand materializes, but the adjustment will not be instant.

The policy is expected to face legal challenges. But until a court intervenes, the new reality for Indian H-1B holders is straightforward: the path to a green card now runs through an airport."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The New Green Card Rule Means 1.2 Million Indians May Need to Fly Home — Here Is What That Looks Like",
    "subheadline": "USCIS now requires most H-1B holders to leave the US for consular processing, turning an immigration policy into a travel logistics crisis for the diaspora.",
    "slug": make_slug("h1b-green-card-fly-home-consular-processing-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "71% of H-1B holders are Indian-origin. 1.2 million families face potential forced travel to India for consular green card processing, spiking demand on key US-India flight corridors.",
    "tags": ["travel", "immigration", "h1b", "green card", "airlines", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/international/news/us-h1b-green-card-rules-tightened-indian-professionals-concerns-138007222.html"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/1-2-mn-indian-american-families-affected--ex-wh-aide-on-new-green-card-rule-1779541952012"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/trump-administration-ends-us-based-green-cards-for-temporary-visa-holders"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/politics/policy/trump-administration-to-make-green-card-applicants-file-overseas"},
        {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/uscis-limits-adjustment-of-status-new-2026-policy-impact/"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922085/pexels-photo-4922085.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Passport and boarding pass at an airport gate — a scene that may become mandatory for 1.2 million Indian green card applicants.",
    "body": art1_body,
}

# ── Article 2: Emirates A380 Premium Economy Retrofit ─────────────

art2_body = """Emirates is halfway through a $5 billion project to retrofit 219 aircraft — 110 Airbus A380s and 109 Boeing 777s — and the first tangible results are now in the air. The airline's densest A380 variant, a 615-seat two-class behemoth that crammed 557 economy seats onto a single airframe, is being reconfigured into a 569-seat three-class layout that introduces premium economy for the first time.

The first retrofitted aircraft, registration A6-EUX, returned to service on May 16 on the Dubai–Birmingham route. By summer's end, Emirates plans to have the new layout operating on nine routes, with all 15 of the affected A380s converted by November.

## The Numbers

The old configuration was blunt: 58 business class seats and 557 economy seats, nothing in between. The new version adds nuance. Business class grows to 76 seats (up 18), a new 56-seat premium economy cabin occupies the upper deck in a 2-3-2 layout with 40 inches of pitch, and economy shrinks to 437 seats. The premium cabin share jumps from 9% to 23%.

For passengers, the difference is material. Premium economy on the A380 offers 19.5-inch-wide seats with 8 inches of recline — not business class, but a meaningful step above economy's 17.9-inch width and 4-inch recline. For Emirates, the math is simple: a quarter of the aircraft now generates higher per-seat revenue.

## The Nine Routes (So Far)

According to aviation schedule tracker Aero Routes, the reconfigured A380s are planned for:

- **Bangkok** — from June 28
- **Birmingham** — ongoing (gap July 1–August 12)
- **Copenhagen** — from July 1
- **Denpasar (Bali)** — from September 15
- **Düsseldorf** — from July 11
- **London Gatwick** — from December 1
- **Manchester** — October 25 to November 30
- **Mauritius** — from August 1
- **Prague** — from July 1

These are leisure-heavy and visiting-friends-and-relatives markets — precisely the routes where diaspora travelers connect.

## Why This Matters for NRIs

Dubai is the single most important connecting hub for Indian Americans flying to India. Emirates, Etihad, and the broader Gulf carrier ecosystem handle a vast share of US–India traffic through their Middle Eastern hubs. Any cabin improvement on Emirates' largest aircraft ripples directly through the diaspora's travel experience.

Premium economy slots the gap that NRI families have long complained about: economy on a 14-hour Dubai connection is brutal, but business class at $4,000–$7,000 round-trip is out of reach for most. Premium economy, typically priced at 1.5 to 2 times economy, gives the Bay Area tech worker visiting Hyderabad or the New Jersey family heading to Kerala a genuine middle option.

Emirates has said premium economy will be available on 99 destinations by end of 2026. That covers virtually every route an NRI would book.

## The Bigger Picture

The retrofit is part of a broader industry shift. Airlines worldwide are investing heavily in premium economy as the fastest-growing long-haul cabin. Singapore Airlines, Cathay Pacific, and Air India have all expanded their premium economy offerings in the past year. The logic is uniform: passengers who would never buy business class will happily pay 50–80% more than economy for a wider seat, better food, and priority boarding.

For Emirates specifically, the retrofit also brings consistency. Until now, booking an A380 was a lottery — you might get the four-class flagship with first class suites, or you might get the stripped-down 615-seat variant with no premium economy at all. By November, every A380 in the fleet will offer at least three classes.

The practical takeaway for diaspora travelers booking summer or fall trips through Dubai: check your aircraft type before you book. The 569-seat A380 routes now have premium economy available, and the early pricing on select routes has been competitive."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Emirates Is Spending $5 Billion to Make Its A380s Less Miserable — and NRIs Flying Through Dubai Will Notice First",
    "subheadline": "The airline's densest superjumbo is getting premium economy on nine routes this summer. For the diaspora, it fills the gap between economy agony and business class prices.",
    "slug": make_slug("emirates-a380-premium-economy-retrofit-nri-dubai"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Dubai is the top connecting hub for US-India flights. Emirates adding premium economy to its densest A380s gives NRI families a middle-tier option on the long-haul routes they fly most.",
    "tags": ["travel", "airlines", "emirates", "premium economy", "dubai", "a380"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Simple Flying", "url": "https://simpleflying.com/massive-569-seats-emirates-new-a380-9-routes/"},
        {"name": "Business Traveller", "url": "https://www.businesstraveller.com"},
        {"name": "Aero Routes", "url": "https://www.aeroroutes.com"},
        {"name": "Emirates", "url": "https://www.emirates.com"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/31878075/pexels-photo-31878075.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An Emirates Airbus A380 at the gate — the airline is retrofitting its densest superjumbos with a new premium economy cabin.",
    "body": art2_body,
}

# ── Article 3: Iran Conflict Reshaping India-US Flights ───────────

art3_body = """Three months into the Iran conflict, the consequences for anyone flying between the United States and India are no longer theoretical. Over 21,000 flights have been canceled globally since airspace closures began in late February. Gulf carriers — Emirates, Qatar Airways, Etihad — have restored roughly 96% of their networks, but "restored" does not mean "normal." Routes that once flew over Iranian airspace now detour south over Saudi Arabia or north over Central Asia, adding 45 minutes to two hours on key legs. Jet fuel costs have spiked. And the ripple effects are landing squarely on the diaspora's most-traveled corridors.

CNN reported this week that US visitor numbers from India are expected to drop more than 4% in 2026 compared to last year, driven in part by restricted airspace and elevated fares. For a community that generates one of the highest volumes of US–India round-trips annually — visiting family, attending weddings, managing property — a 4% dip is not a rounding error. It is tens of thousands of trips not taken.

## What Happened to the Gulf Route

Before the conflict, the standard routing for NRIs flying economy or business on Gulf carriers was straightforward: SFO or JFK to Dubai or Doha, then onward to Delhi, Mumbai, Hyderabad, Bengaluru, or Chennai. Iranian airspace sat in the middle of the most efficient path between the Gulf and South Asia, shaving time and fuel off every leg.

With that airspace closed or restricted, airlines have been forced to reroute. The detours add fuel burn, which airlines pass through as higher fares. British Airways has implemented "significant schedule cuts" across multiple Middle Eastern routes during its 2026 operational review. Air Arabia canceled five flights in a single day from Sharjah last week. Even FlyDubai — the budget workhorse that NRIs use for short Gulf–India hops — has been logging delays.

The Strait of Hormuz disruption adds another layer. India imports the majority of its crude oil through the strait, and the maritime crisis earlier this year drove aviation fuel prices higher across Indian domestic and international markets. Those costs flow directly into ticket prices.

## The Winners: Direct Flights and Asian Carriers

The conflict has made one thing clear: direct US–India flights have never been more valuable. Air India's nonstops from SFO, JFK, EWR, ORD, and IAD to Delhi and Mumbai bypass the Gulf entirely. United's nonstop Newark–Delhi and San Francisco–Delhi services do the same. These routes were already popular with the diaspora; now they carry a resilience premium.

Asian carriers are also benefiting. Cathay Pacific, Singapore Airlines, and Korean Air have all reported strong European route performance as travelers reroute away from Middle Eastern hubs. For NRIs flying to India, Singapore Airlines via Changi and Cathay via Hong Kong offer Gulf-free alternatives, though with longer total travel times on some itineraries.

## What the Fares Look Like

Summer 2026 fares on the US–India corridor are running 15–25% above the same period last year, depending on the route and carrier. Economy round-trips on Air India's SFO–DEL nonstop are hovering around $1,300–$1,500. Emirates via Dubai — still the highest-volume connecting option — is pricing economy at $1,100–$1,400 but with longer journey times due to rerouting.

The fare gap between direct and connecting itineraries has narrowed. A year ago, flying through Dubai or Doha saved $200–$400 over a nonstop. Today, the savings are often under $100, and the time penalty is steeper. For time-sensitive travelers — those with limited PTO, young children, or elderly parents to visit — nonstops have become the default.

## Planning Around Uncertainty

The conflict shows no signs of rapid resolution, and airlines are building their winter 2026 schedules around continued airspace restrictions. NRIs planning year-end trips to India should factor in several realities: fares will likely remain elevated through Diwali season, direct flights will sell out earlier than usual, and Gulf connections will be functional but slower.

Booking early, choosing flexible fare classes, and monitoring alternative routing through Singapore or Hong Kong are the practical moves. The era of cheap, fast Gulf connections to India is not over — but it is on pause, and the pause is costing the diaspora real money and real time."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Iran Conflict Has Quietly Reshaped How NRIs Fly to India — and the Costs Are Adding Up",
    "subheadline": "21,000 flights canceled, Gulf routes rerouted, fares up 15–25%. Direct US-India flights have never mattered more to the diaspora.",
    "slug": make_slug("iran-conflict-nri-india-flights-gulf-rerouting"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Gulf carriers handle the majority of US-India connecting traffic. Airspace closures and rerouting from the Iran conflict are driving up fares and travel times on the diaspora's most-flown corridors.",
    "tags": ["travel", "airlines", "iran conflict", "gulf carriers", "air india", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/23/travel/us-tourism-decline-perception"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com"},
        {"name": "The Traveler", "url": "https://thetraveler.org/21000-flights-axed-middle-east-conflict"},
        {"name": "GTM Business Travel", "url": "https://gtm.uk.com/middle-east-conflict-business-travel-disruption-update/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36713568/pexels-photo-36713568.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "An airplane silhouetted against a Dubai sunset — Gulf routes to India now take longer and cost more due to Iranian airspace closures.",
    "body": art3_body,
}

# ── Publish ───────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted at {now}")
