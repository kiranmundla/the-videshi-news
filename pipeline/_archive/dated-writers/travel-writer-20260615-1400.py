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
        "headline": "India-US Airfares Are Up 30% This Summer — Here's How NRIs Can Beat the Squeeze",
        "subheadline": "A Gulf war, a closed Strait of Hormuz, and fuel surcharges have pushed Delhi-to-California fares to painful highs. Smart routing and timing still leave room to save.",
        "slug": make_slug("india-us-airfares-up-30-percent-summer-nri-booking-guide"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "For the Indian diaspora flying home over summer break, fares on the key US-India corridors have jumped 25-30%, and knowing how surcharges and rerouting work is the difference between a $900 ticket and a $1,600 one.",
        "tags": ["travel", "airlines", "airfare", "air india", "fuel surcharge"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint — Planning summer holidays amid soaring airfares", "url": "https://www.livemint.com/news/how-to-plan-summer-holidays-amid-soaring-airfares-due-to-west-asia-war.html"},
            {"name": "Wego — Air India Fuel Surcharge 2026", "url": "https://blog.wego.com/air-india-fuel-surcharge-2026/"},
            {"name": "NBC Palm Springs — Soaring Airfares Reshape Summer Travel", "url": "https://nbcpalmsprings.com/2026/06/15/soaring-airfares-reshape-summer-travel-plans/"},
            {"name": "Travel And Tour World — Global airfare shockwave", "url": "https://www.travelandtourworld.com/news/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A busy airport departure board listing international flights during peak summer travel season",
        "image_attribution": "Pexels",
        "body": """If you have been refreshing fare trackers for a July trip to Hyderabad or Bengaluru, you already know the bad news: the numbers are ugly. What you may not know is exactly why — and where the discounts are hiding.

US government data tells the broad story. The Bureau of Labor Statistics recorded airline fares rising 26.7% year-on-year in May 2026, the steepest jump in years. On the India corridors specifically, travel agency Yatra Online pegs increases from Delhi and Mumbai to the United States at 25-30% over the same May-July window last year, with Europe close behind at 20-25%.

## What's actually driving the spike

Three forces are stacking on top of each other, and all three trace back to the Gulf.

First, jet fuel. After Iran moved to close the Strait of Hormuz following US strikes in mid-June, roughly 20% of the world's seaborne oil — and nearly all of Qatar's LNG — was suddenly in question. Jet fuel, which already makes up about 40% of Air India's operating costs, spiked. The airline has rolled out a phased fuel surcharge that now adds up to ₹18,600 (roughly $220) on long-haul tickets. IndiGo layered on two rounds of its own, adding as much as ₹10,000 on India-Gulf sectors.

Second, airspace. With parts of West Asian airspace closed or risky, carriers are flying longer routes around the conflict zone. Longer routes burn more fuel and, crucially, kill the cheap one-stop itineraries that NRIs have leaned on for decades. A Delhi-London one-stop via the Gulf with a short layover is being quietly retired in favor of pricier nonstops; a direct Delhi-London round trip is now ₹1.1-1.3 lakh, nearly double the old connecting fare.

Third, capacity. Air India is bleeding nearly $3 billion a year and has cut services on several North America, Europe and Australia routes between June and August. Fewer seats on the routes diaspora families actually use means less competition and firmer prices.

## Where NRIs can still save

The squeeze is real, but it is not uniform. A few moves still work:

**Split the ticket.** Instead of one through-fare to a Tier-2 Indian city, book a competitive long-haul into Delhi, Mumbai or Bengaluru and add a separate domestic leg on IndiGo or Akasa. With Air India trimming its own connections, the all-in through-fare premium has widened, so unbundling often wins.

**Watch the Gulf carriers' insurance sweeteners.** Etihad is offering free 15-day travel medical insurance and Emirates a "Fly You Home" repatriation guarantee — a meaningful hedge if your routing transits Abu Dhabi or Dubai during an unstable summer.

**Lock in early, but check the change rules.** Air India's surcharges do not apply retroactively to tickets already issued — unless you change the date or route, which triggers a recalculation at current rates. If your plans are firm, booked-and-paid beats wait-and-see right now.

**Consider the shoulder weeks.** Demand peaks around school break and the late-August return crush. Flying out in the first half of June or pushing the return into September can shave hundreds off economy fares.

## The bottom line for the diaspora

This is the most expensive India summer in recent memory, and the reasons — a shooting war near the Gulf, a contested shipping strait, an airline cutting to survive — are not the kind that resolve on a predictable timeline. For the 5-million-strong Indian American community, that argues for booking decisively when a fair fare appears rather than gambling on a dip that the fundamentals do not support. The era of the cheap one-stop to India via Dubai is, at least for this summer, on pause."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Just Launched Mumbai-Tokyo Nonstops — and Japan Is Having an NRI Moment",
        "subheadline": "The new four-times-weekly Haneda service opens a second Japan gateway as Indian visits to the country surge 35% in a year.",
        "slug": make_slug("air-india-mumbai-tokyo-haneda-nonstop-japan-nri-travel"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "For NRIs in Japan and Indian American families eyeing a less-crowded Asia trip, a Mumbai-Haneda nonstop plus codeshare access to six Japanese cities makes Japan dramatically easier to reach without backtracking through Delhi or a Gulf hub.",
        "tags": ["travel", "air india", "japan", "tokyo", "new routes"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Air India Newsroom — Asia expansion to Vietnam and Japan", "url": "https://www.airindia.com/en-in/newsroom/"},
            {"name": "TravelMedia.in — Air India expands Asia footprint", "url": "https://travelmedia.in/air-india-expands-asia-footprint-with-new-routes-to-vietnam-and-japan/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31048512/pexels-photo-31048512.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Tokyo skyline at dusk, a growing draw for Indian travelers in 2026",
        "image_attribution": "Pexels",
        "body": """Air India's newest international route quietly went live this week, and it deserves more attention than it has gotten. Starting June 15, the airline is flying nonstop between Mumbai and Tokyo's Haneda airport four times a week on a Boeing 787-8 Dreamliner — its second gateway into Japan alongside the daily Delhi-Haneda service.

For a route map that has been shrinking elsewhere, this is a notable add. And the timing is not an accident.

## Japan is booming with Indian travelers

The numbers behind the decision are striking. More than 315,000 Indians visited Japan in 2025 — a 35% jump from 2024, and nearly 80% above pre-pandemic levels. Japan has gone from a once-in-a-lifetime bucket-list trip to a repeat destination for Indian families, drawn by the cherry blossoms and autumn foliage, the famously clean and punctual rail network, and a yen that has stayed weak enough to make a traditionally expensive country feel affordable.

The Mumbai launch matters because, until now, western and southern India effectively had to route through Delhi to reach Japan on Air India metal. A Mumbai nonstop removes a backtrack for the enormous Gujarati, Maharashtrian and South Indian populations clustered around the city and its catchment.

## The codeshare is the real unlock

The headline is the nonstop, but the quieter story is connectivity. Air India's deepened codeshare with All Nippon Airways (ANA) gives passengers onward access to six Japanese cities beyond Tokyo: Fukuoka, Hiroshima, Nagoya, Okinawa, Osaka and Sapporo.

That turns a single Tokyo flight into a gateway for the whole country. An NRI in Mumbai can now book a single itinerary to Osaka for the food, Sapporo for the snow, or Okinawa for the beaches — without stitching together separate tickets or risking a self-transfer.

## Why this matters to the diaspora

Two groups should take note. The first is the growing Indian community in Japan itself — students, IT professionals and engineers concentrated around Tokyo and Osaka — for whom a direct Mumbai link means easier family visits in both directions and smoother baggage handling than a Gulf or Southeast Asian connection.

The second is the Indian American traveler weighing an Asia trip. As Thailand reinstates visa fees and gets more crowded, and as the Gulf becomes a less appealing transit point amid regional conflict, Japan is emerging as the polished, orderly alternative. For an NRI flying from the US to India this summer, tacking on a Japan leg via Mumbai is now a genuinely practical add-on rather than a logistical headache.

## The bigger picture

The Mumbai-Haneda launch lands the same week Air India opened its Delhi-Hanoi route and amid news that the carrier is cutting capacity to North America and Europe to stem losses. The contrast is telling: Air India is pulling back on the expensive, fuel-hungry long-haul Western routes while leaning into nearer Asian markets where demand is exploding and the economics work.

For diaspora travelers, the lesson is that the airline's network is being reshaped around where Indians are actually flying — and right now, in record numbers, that is Japan. If a Tokyo trip has been on the family list, the routing has never been simpler from India's commercial capital."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Global Entry Is Open to Indian Citizens — Why Every Frequent-Flyer NRI Should Apply Now",
        "subheadline": "The $100 trusted-traveler program skips the customs line at 53 US airports and bundles in TSA PreCheck. The catch: Indian vetting can take up to two years.",
        "slug": make_slug("global-entry-indian-citizens-trusted-traveler-nri-guide"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "For green-card-holding and Indian-passport NRIs who fly the US-India corridor several times a year, Global Entry turns a 90-minute customs ordeal at JFK or SFO into a 30-second kiosk scan — and the long Indian background-check timeline means the smart move is to apply before the next India trip, not after.",
        "tags": ["travel", "global entry", "visa", "tsa precheck", "airports"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "US Customs and Border Protection — Global Entry for Indian Citizens", "url": "https://www.cbp.gov/travel/trusted-traveler-programs/global-entry/international-arrangements/global-entry-indian-citizens"},
            {"name": "Fragomen — Global Entry Opens to All Eligible Citizens of India", "url": "https://www.fragomen.com/insights/global-entry-opens-to-all-eligible-citizens-of-india.html"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32176062/pexels-photo-32176062.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passport control and immigration kiosks at an international airport arrivals hall",
        "image_attribution": "Pexels",
        "body": """Anyone who has landed at Newark or San Francisco on a packed evening bank of India flights knows the feeling: a wall of people, snaking lines, and an hour-plus shuffle to a customs officer before you even reach baggage claim. For Indian passport holders, there is now a way around it — and it is worth understanding before your next trip.

US Customs and Border Protection has opened its flagship Global Entry trusted-traveler program to citizens of India, making India the eleventh country whose nationals can enroll. For the millions of Indians and NRIs who cross the US border each year, it is one of the more useful immigration developments in recent memory.

## What you actually get

Global Entry lets pre-approved, low-risk travelers skip the regular customs and immigration line. Instead of queueing for an officer, members walk to an automated kiosk, scan their passport, get fingerprinted and photographed, complete an on-screen declaration, and walk out with a receipt toward baggage claim. The whole thing takes seconds.

The membership lasts five years and, critically, includes TSA PreCheck — the expedited domestic security screening that lets you keep your shoes, belt and laptop in place. For a family that flies domestically within the US between international trips, that benefit alone often justifies the cost.

The fee is $100, non-refundable, for the five-year term.

## The catch every Indian applicant needs to know

Here is the part that trips people up. Unlike US citizens, who can be approved in weeks, Indian citizens face an extra layer: vetting by the Government of India. CBP warns that this background check can take anywhere from six months to two years, and Global Entry approval can be delayed accordingly.

There is also an India-specific step. After applying through CBP's Trusted Traveler Program (TTP) website and paying the $100, Indian applicants must submit additional information and pay a ₹500 local fee through the Passport Seva Portal, then schedule an in-person interview at a designated PSK or PSLK passport office in India.

The practical implication: if you are an NRI who only visits India occasionally, apply for Global Entry before your next trip home so you can knock out the interview while you are there. CBP explicitly recommends that Indian citizens not currently living in India time their application to a planned visit.

## Two paths to the interview

Once conditionally approved, you have options. You can schedule an interview at a Global Entry Enrollment Center, or use Enrollment on Arrival — completing the interview with a CBP officer when you next land in the US, with no separate appointment needed. For busy travelers, Enrollment on Arrival is often the path of least resistance: you are already at the airport.

Bring your passport and an official photo ID showing your current address to whichever interview you choose.

## Why it is worth it for the diaspora

For the frequent-flyer NRI — the consultant shuttling between Bengaluru and the Bay Area, the parent doing two India trips a year, the student flying home each summer — the math is simple. Spread over five years and dozens of border crossings, $100 buys back hours of standing in line at exactly the moment you are most jet-lagged and least patient. The only real cost is planning ahead around India's slow vetting clock. Start the application now, and your future self stuck behind 300 people at the JFK arrivals hall will thank you."""
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

print(f"\n{len(inserted)}/{len(articles)} articles inserted.")
