#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

swiss_body = """Southern India's tech capital is about to get its first nonstop link to Switzerland. Swiss International Air Lines confirmed it will begin flying between Bengaluru and Zurich on 28 October 2026, five times a week, making Bengaluru the carrier's newest Indian gateway alongside its long-running Delhi and Mumbai services.

For the Kannadiga and South Indian diaspora scattered across Europe and North America, this is the kind of route that quietly removes a connection from the itinerary — and a connection removed is usually a missed-bag risk avoided.

## The schedule, and why the timings matter

SWISS will operate the route with a westbound morning departure and an eastbound afternoon one. The LX 141 leaves Bengaluru at 04:50 and lands in Zurich at 10:50 the same morning, running Monday, Wednesday, Friday, Saturday and Sunday. The return LX 140 departs Zurich at 13:20 and arrives in Bengaluru at 02:55 the next day, operating Tuesday, Thursday, Friday, Saturday and Sunday.

The late-morning Zurich arrival is the useful part. It feeds straight into Zurich's bank of midday onward departures across Europe and to North America, so a passenger from Bengaluru can reach a wide swath of Lufthansa Group destinations on a single ticket without an overnight layover. Zurich Airport is also one of Europe's more compact major hubs, which makes a tight connection less of a gamble than it would be at a sprawling gateway.

## Why this lands differently for the diaspora

Bengaluru sits at the center of India's IT industry, and the engineers, founders and consultants who work there are precisely the people who move between India, Europe and the US most often. Until now, that crowd flew Bengaluru's existing Lufthansa Group options through Frankfurt and Munich, or routed through the Gulf. A nonstop to Zurich adds a third Lufthansa Group gateway from the city and, crucially, opens SWISS's premium product — First Class is offered on every flight on this route — to travelers who previously had to connect to reach it.

For families visiting relatives in Switzerland, Germany, France or Italy, the open-jaw possibilities are real: fly into Zurich, tour the continent, and fly home from a different European city, all stitched together through one alliance. And for the growing number of Indian students and young professionals in Swiss and German university towns, a direct hop home for Diwali or a family emergency just got materially shorter.

## The bigger Lufthansa Group push into India

The Bengaluru launch is one piece of a broader European bet on Indian traffic. The Lufthansa Group — which spans Lufthansa, SWISS, Austrian, Brussels and ITA Airways — runs more than 70 weekly flights between India and Europe and has signaled it intends to keep adding capacity. The group is rolling out Lufthansa's new Allegris cabins on additional Boeing 787-9 services from Delhi and Hyderabad, and adding SWISS A330 frequencies between Delhi and Zurich.

That expansion rides on top of a deepening tie-up with Air India. The two sides have been building toward a joint business arrangement that already places codeshare flights across scores of India–Europe routes, knitting Air India's long-haul network into the European carriers' hubs. For NRIs, the practical upshot is more single-ticket itineraries, better-coordinated schedules, and frequent-flyer reciprocity that makes miles earned on one carrier more useful on the other.

## What to do about it

If Bengaluru is your home airport, it is worth pricing the new SWISS nonstop against your usual Gulf or Frankfurt routing — introductory fares on a launch route are often sharper than the schedule's premium positioning suggests, and the time saved by skipping a connection has its own value. Award seats on a brand-new route also tend to be more available in the first few months before the route fills out.

Bookings are open now through SWISS and Lufthansa Group channels for travel from late October. For the southern Indian diaspora that has long watched Delhi and Mumbai get the direct European links first, Bengaluru's turn has finally come."""

malaysia_body = """For two decades, Thailand was the default first stamp in many an Indian passport — cheap, close, beach-laden and, for a stretch, visa-free. That era is quietly ending. As Thailand tightens its entry rules and brings back fees for Indian visitors, Malaysia is emerging as the Southeast Asian destination Indian travelers are switching to, and the shift carries real implications for NRI families planning the next big group trip.

## What changed in Thailand

Thailand's temporary visa-free arrangement for Indian passport holders has been wound back, with the country reinstating visa charges and introducing stricter tourism controls in certain areas. For a solo traveler the fee is modest, but for a family of four or a multi-generational group — the way many NRIs actually travel — it stacks up fast and reshuffles the math on a budget holiday. Reports of shortened visa-free windows have added uncertainty, and uncertainty is exactly what makes travelers shop around.

## Why Malaysia is winning the switch

Malaysia has kept its door open. Indian passport holders can enter visa-free for tourism for up to 30 days, an arrangement currently extended through the end of 2026. The one piece of homework is the Malaysia Digital Arrival Card (MDAC), a free online form that must be submitted within three days of arrival — a few minutes of typing rather than a visa application.

Beyond the paperwork, Malaysia ticks the boxes Indian families care about. Kuala Lumpur pairs big-city shopping and the Petronas Towers skyline with easy day trips; Langkawi and Penang deliver beaches and some of the best street food in the region; and the country's deep Indian-origin community means Tamil is widely spoken, vegetarian and halal food is everywhere, and temples sit alongside mosques and churches. For grandparents traveling with the family, that familiarity matters as much as the price.

## The connectivity angle

Air links are thickening at the right moment. Low-cost and full-service carriers serve Kuala Lumpur from a long list of Indian cities, and KL's position as an AirAsia hub makes it a natural springboard for onward hops to Bali, Cambodia and the rest of Southeast Asia on a single low-cost itinerary. For NRIs routing home through Asia, that turns a Malaysia stop into a flexible hub rather than a dead-end beach week.

Vietnam is the other beneficiary of the same realignment, drawing Indian travelers with a seamless e-visa system and lower costs to Hanoi, Da Nang and Ha Long Bay. Between Malaysia's visa-free window and Vietnam's digital visa, the center of gravity for Indian leisure travel in the region is visibly moving away from its old Thai anchor.

## Why this matters to the diaspora

For Indian Americans, the destination calculus is different from that of travelers flying out of India, but the trend still matters. Many NRI families plan reunion trips on neutral ground — a place where relatives flying from India and relatives flying from the US can meet halfway. Southeast Asia is a favored compromise, and the easiest-entry, best-value option in that region is now Malaysia rather than Thailand.

There is also the US-visa perk to weigh: while it does not apply to Malaysia, NRIs holding a US green card or visa already enjoy simplified entry to a growing list of countries, and the broader lesson is to check entry rules close to departure rather than assuming last year's policy still holds. Visa regimes across Southeast Asia have been unusually fluid in 2026.

## The practical takeaway

If a Southeast Asia trip is on the calendar, Malaysia is the low-friction pick for now: book before the end-2026 visa-free window's status is reviewed, fill the MDAC within three days of arrival, and consider pairing KL with a cheap onward hop to stretch the itinerary. Thailand is not off the table — but it is no longer the automatic answer it was, and Indian travelers are voting with their bookings."""

gulf_body = """The Gulf has long been the diaspora's great connecting machine — the place where a flight from San Francisco, Newark or Toronto meets a flight to Delhi, Mumbai, Hyderabad or Kochi. So when the region's biggest carriers start rolling out medical-insurance and repatriation safety nets for transit passengers, NRIs who route home through Dubai, Abu Dhabi or Doha should pay attention.

## What the carriers are offering

Two Gulf moves stand out. Etihad Airways has introduced complimentary medical travel insurance covering the first 15 days of a trip, and Emirates has rolled out a "Fly You Home" repatriation assurance designed to get travelers back to their home country if circumstances on the ground deteriorate. Both are responses to heightened regional safety concerns and to travel warnings that have begun to factor into how passengers book and transit through the Middle East.

The backdrop is uneasy. Airspace restrictions linked to regional conflict have already forced longer routings on several international services, and a wave of operational disruption — thousands of delays and hundreds of cancellations recorded across Asian and Gulf hubs in a single day this month — has rattled connection-dependent itineraries. Insurance and repatriation guarantees are, in part, the airlines' way of reassuring nervous travelers that a Gulf layover is still a safe bet.

## Why this matters to NRIs specifically

A huge share of US-, UK- and Canada-to-India traffic transits the Gulf, precisely because Emirates, Etihad and Qatar Airways built their hubs to funnel exactly this diaspora flow. That makes NRIs disproportionately exposed to anything that disrupts Gulf transit — and disproportionately served by anything that protects it.

The practical value is real. Travel medical coverage that activates automatically for the first stretch of a trip is genuinely useful for the many NRIs who travel with elderly parents, where a health scare abroad is a live worry. And a repatriation guarantee, while you hope never to use it, is reassurance for families weighing whether to route grandparents and young children through the region at all.

## The flip side: check your layover

The same turbulence that prompted these perks is a reason to scrutinize your itinerary. Longer reroutes mean some Gulf connections are tighter or schedules less reliable than the booking engine suggests. A few things worth doing before you fly home:

- **Build in buffer.** On a Gulf-transit ticket, a sub-two-hour connection is riskier than usual right now. Where you can, choose itineraries with a comfortable layover.
- **Read the fine print on the perks.** Airline-provided insurance and repatriation cover specific scenarios and time windows — they are not a substitute for a comprehensive travel policy, especially for trips longer than two weeks or for travelers with pre-existing conditions.
- **Keep your contacts handy.** Save the nearest Indian mission's details and your airline's rebooking line before departure, not after a cancellation.
- **Watch advisories.** State Department and Ministry of External Affairs alerts have moved more often than usual this year; check them close to your travel date rather than at booking.

## The bigger picture

Gulf carriers are not pulling back from the India market — far from it. Qatar Airways is rolling out its biggest-ever network this season, adding US gateways that matter directly to the diaspora, and the region's airlines continue to compete hard for NRI loyalty. The insurance and repatriation offers are best read as a sign that the Gulf hubs intend to remain the diaspora's connecting point of choice, and are willing to underwrite some of the risk to keep it that way.

For NRIs, the takeaway is balanced: the Gulf route home is still the most convenient and competitive option from much of North America, the new safety nets add genuine value, and a little extra attention to layover length and advisories goes a long way this summer."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "SWISS Is Flying Bengaluru to Zurich Nonstop From October — and It's Built for the Tech Diaspora",
        "subheadline": "India's Silicon Valley gets its first direct link to Switzerland, opening one-ticket access across Europe and North America through the Lufthansa Group's Zurich hub.",
        "slug": make_slug("swiss-bengaluru-zurich-nonstop-lufthansa-tech-diaspora"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "A nonstop Bengaluru–Zurich route removes a connection for the South Indian tech diaspora across Europe and North America, opening single-ticket itineraries and SWISS's premium cabins to travelers who previously had to route through Frankfurt, Munich or the Gulf.",
        "tags": ["travel", "airlines", "swiss", "bengaluru", "lufthansa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SWISS (swiss.com)", "url": "https://www.swiss.com/in/en/prepare/route-network/bengaluru-zurich"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/swiss-expands-india-network-with-new-nonstop-bengaluru-zurich-service/"},
            {"name": "LatestLY / ANI", "url": "https://www.latestly.com/agency-news/india-news-swiss-international-airlines-to-launch-nonstop-bengaluru-zurich-flights-from-october.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28445206/pexels-photo-28445206.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Aerial view of Zurich, the Lufthansa Group hub that will anchor SWISS's new nonstop service from Bengaluru.",
        "image_attribution": "Pexels",
        "body": swiss_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Malaysia Is Overtaking Thailand as Indian Travelers' Favorite — Here's What Changed",
        "subheadline": "As Thailand reinstates visa fees and tightens entry rules, Malaysia's visa-free window, familiar food and easy connections are pulling Indian families away from their old default beach holiday.",
        "slug": make_slug("malaysia-overtakes-thailand-indian-travelers-visa-free"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "Southeast Asia is a favored 'meet halfway' destination for NRI family reunions, and the easiest-entry, best-value option in the region is now Malaysia rather than Thailand — a shift that reshapes where diaspora families plan group trips.",
        "tags": ["travel", "visa", "malaysia", "thailand", "southeast-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/malaysia-overtakes-thailand-as-indian-travellers-seek-easier-visa-rules-affordable-luxury-and-hassle-free-southeast-asia-holidays-in-2026/"},
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Travel And Tour World — Vietnam shift", "url": "https://www.travelandtourworld.com/news/article/vietnam-joins-india-thailand-and-southeast-asia-in-witnessing-a-major-tourism-realignment/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11719269/pexels-photo-11719269.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Kuala Lumpur's Petronas Twin Towers, a centerpiece of the Malaysia itineraries drawing Indian travelers in 2026.",
        "image_attribution": "Pexels",
        "body": malaysia_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Gulf Airlines Are Adding Insurance and 'Fly You Home' Guarantees — What NRIs Routing Through Dubai Should Know",
        "subheadline": "Etihad's free 15-day medical cover and Emirates' repatriation pledge arrive as airspace turmoil snarls Gulf connections — here's how to read the perks and protect your trip home.",
        "slug": make_slug("gulf-airlines-insurance-repatriation-nri-dubai-transit"),
        "category": "travel",
        "vertical": "diaspora-safety",
        "diaspora_angle": "A huge share of US-, UK- and Canada-to-India traffic transits the Gulf, so new airline insurance and repatriation guarantees — and the airspace disruptions behind them — land squarely on NRIs flying home through Dubai, Abu Dhabi and Doha.",
        "tags": ["travel", "airlines", "gulf", "emirates", "etihad", "safety"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Gulf travel risk", "url": "https://www.travelandtourworld.com/news/article/united-kingdom-joins-australia-germany-france-etihad-airways-free-fifteen-day-insurance-emirates-fly-you-home-repatriation/"},
            {"name": "Travel And Tour World — Asia/Gulf disruptions", "url": "https://www.travelandtourworld.com/news/article/indonesia-joins-india-china-japan-saudi-arabia-russia-oman-flight-delays-cancellations/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33992401/pexels-photo-33992401.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An Emirates Airbus A380 departing — the Gulf carriers are the diaspora's main connecting point between North America and India.",
        "image_attribution": "Pexels",
        "body": gulf_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
