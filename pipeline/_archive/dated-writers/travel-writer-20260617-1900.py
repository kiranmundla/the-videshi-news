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
        "headline": "Air India and Thai Airways Are Joining Codes — Why the Bangkok Layover Just Got Smarter for NRIs",
        "subheadline": "A new codeshare between the two Star Alliance carriers will let US-based Indians thread Bangkok onto a single ticket to India, with one bag tag and one set of connection guarantees.",
        "slug": make_slug("air-india-thai-airways-codeshare-bangkok-nri-single-ticket"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the hundreds of thousands of NRIs who route through Bangkok to reach Indian cities Air India does not serve nonstop, a single AI-TG ticket means protected connections, through-checked bags, and no separate budget-carrier gamble if the first leg runs late.",
        "tags": ["travel", "airlines", "air india", "thailand", "codeshare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-and-thai-join-forces-through-mou/"},
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/air-india-and-thai-airways-sign-mou-to-strengthen-connectivity-between-india-and-thailand/"},
            {"name": "Aviation World", "url": "https://aviationworld.in/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30540817/pexels-photo-30540817.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Buddhist temple complex in Bangkok, Thailand, a key transit hub for India-bound travelers",
        "image_attribution": "Pexels",
        "body": """Air India and Thai Airways International have signed a memorandum of understanding to build a codeshare partnership between the two carriers, a deal that on paper reads like dry airline housekeeping but in practice reshapes one of the most heavily used connecting routes for the Indian diaspora.

The agreement, signed on June 7 on the sidelines of the IATA annual general meeting in Rio de Janeiro, commits the two Star Alliance members to place each other's codes — "AI" for Air India and "TG" for Thai — on flights between India and Thailand, and on select onward international routes. The carriers say a full codeshare will follow later in 2026, subject to regulatory clearance in both countries.

### Why Bangkok matters to NRIs

Bangkok is not a vacation footnote for the Indian community abroad. It is one of the busiest one-stop gateways between the United States and India, especially for travelers headed to cities Air India does not reach nonstop from North America. A passenger flying from the West Coast often connects through an East Asian or Gulf hub, and Bangkok has long been a natural midpoint for onward travel to southern and eastern India.

Until now, stitching a Bangkok connection onto an India trip frequently meant buying two separate tickets — one long-haul, one regional, often on a low-cost carrier. That arrangement carries a quiet risk most travelers learn the hard way: if the first flight is delayed and the second is on an unrelated ticket, the airline owes you nothing. You eat the missed connection, rebook at the gate, and pay again.

A codeshare changes the math. When both legs sit on a single itinerary, the operating airlines are responsible for protecting the connection. Bags are checked through to the final destination. And if weather or a mechanical delay breaks the chain, rebooking is the airline's problem, not the passenger's.

### What the deal actually delivers

The two carriers already have an interline agreement, which allows tickets to be issued across both networks. The codeshare deepens that into coordinated scheduling and shared inventory, meaning the airlines time their flights to connect and sell the combined journey as one product.

Campbell Wilson, Air India's chief executive, framed the partnership around "longstanding cultural ties" and "strong flows of tourism and business travel" between the two countries. Thai Airways chief executive Chai Eamsiri called it a milestone in strengthening regional connectivity. The corporate language is predictable; the practical upshot is not. Both airlines belong to Star Alliance, so frequent flyers can expect mileage earning and, eventually, lounge and priority benefits to extend across the combined network.

The deal also opens onward routes beyond the two home markets. Thai's network reaches deep into Australia, Japan, and Southeast Asia, while Air India's post-merger map now stretches across North America and Europe. For an NRI in the tri-state area visiting family in Chennai with a side trip to relatives in Australia, the prospect of doing it all on linked tickets is genuinely new.

### The fine print to watch

A memorandum of understanding is not a binding commercial contract, and the specific terms — which routes, which fare classes, how loyalty benefits map across — have not been published. Regulatory approval in both India and Thailand is still pending, and codeshares of this scale typically roll out in phases rather than all at once. Travelers should not expect to book an AI-coded Thai flight tomorrow.

What is worth doing now is watching how the route maps fill in over the coming months. If the codeshare extends to Air India's US gateways, the Bangkok connection could become one of the more reliable and competitively priced ways to reach second-tier Indian cities from America — particularly as Gulf hubs face periodic airspace disruptions that have made some NRIs wary of routing through the Middle East.

For a community that plans trips home around school holidays, weddings, and aging parents, fewer points of failure on a long journey is not a small thing. It is the difference between arriving for the function and missing it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Direct India-China Flights Are Quietly Coming Back — and a New Daily Guangzhou Service Widens the Door",
        "subheadline": "After a five-year freeze, four nonstop routes now link India and China, with China Southern set to add daily Delhi-Guangzhou flights from September. For NRIs with business or study ties across Asia, the one-stop detour through Hong Kong may finally be optional.",
        "slug": make_slug("india-china-direct-flights-revival-guangzhou-nri-asia"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Indian American professionals and students with work, manufacturing, or academic links spanning India and China have spent five years routing through Hong Kong, Singapore, or Bangkok; the return of nonstop service cuts both travel time and cost on a corridor that once carried over a million passengers a year.",
        "tags": ["travel", "airlines", "china", "india", "indigo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-and-china-travel-connectivity-china-southern-delhi-guangzhou/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airports-networks/indigo-adds-guangzhou-first-step-india-china-resumption"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/india-china-resume-direct-flights-after-five-year-freeze/"}
        ]),
        "score_total": 73,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14230236/pexels-photo-14230236.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The skyline of Guangzhou, China, a growing direct-flight destination from Indian cities",
        "image_attribution": "Pexels",
        "body": """The air corridor between India and China, frozen since the pandemic and a deadly 2020 border clash brought it to a standstill, is reopening one route at a time. The latest signal: China Southern Airlines plans to launch daily nonstop flights between Delhi and Guangzhou from September 2026, adding capacity to a market that until recently had none.

It joins a small but growing roster. As of mid-2026, four nonstop routes now connect the two countries — a sharp turn from a year ago, when the only way across was a one-stop itinerary through Hong Kong, Singapore, or Bangkok.

### What is flying now

The revival began in February, when Air India launched Delhi to Shanghai Pudong, stepping the route up to five times weekly by late March. IndiGo followed with a daily Kolkata-Shanghai service and resumed Delhi-Guangzhou flights in late April. Air China restarted Beijing-Delhi service three times a week, and China Eastern brought back Kunming-Kolkata six times weekly. Together these routes now generate roughly 40 nonstop flight movements between the two countries each week.

The diplomatic backdrop matters here. The freeze followed the 2020 Galwan Valley clash, after which no direct flights operated for more than five years. The thaw traces to a series of quiet steps since 2024 — a border agreement, a bilateral deal to restart air services, and India reopening tourist visas to Chinese nationals — culminating in Prime Minister Narendra Modi's visit to the Shanghai Cooperation Organisation summit, his first trip to China in years.

### Why the diaspora should pay attention

For most Indian Americans, China is not the destination — but it is increasingly part of the journey and the work. The Indian diaspora in the US is heavily concentrated in technology, manufacturing supply chains, pharmaceuticals, and academia, all sectors with deep operational links to Chinese cities. Guangzhou in particular is the trading and manufacturing gateway of southern China, the city where countless small importers, electronics buyers, and textile traders of Indian origin do business.

Before the shutdown, nine nonstop routes connected India and China, carrying more than 1.25 million two-way passengers in 2019, according to Sabre data. By 2024 that traffic had halved, with most travelers forced onto expensive, time-consuming one-stop routings. New Delhi-Guangzhou alone carried about 40,500 passengers in 2024 even without a nonstop option — demand that a daily direct service is now positioned to capture.

For an NRI managing a sourcing operation between, say, a warehouse in New Jersey and suppliers in Guangzhou, with family in Delhi, the difference between a nonstop and a Hong Kong connection is hours of travel time and often hundreds of dollars per ticket. The same logic applies to the growing number of Indian students and researchers moving between the two countries.

### The caveats

This is a recovery, not a full restoration. Forty weekly movements is a fraction of the pre-2020 network, and routes remain concentrated on Delhi, Kolkata, Mumbai, and a handful of Chinese megacities. Schedules are still building, fares on thin routes can be high — Air China's Beijing-Delhi economy fares start around $523 — and the political relationship, while improved, remains sensitive enough that travelers should not assume the trajectory is permanent.

There is also a practical visa dimension. India reopened tourist visas to Chinese nationals in 2025, and travel in both directions has eased, but NRIs holding Indian passports should confirm current Chinese visa requirements well ahead of travel, as processing timelines on this corridor have been unpredictable during the reopening.

Still, the direction is unmistakable. A market that went to zero is rebuilding, and for the slice of the diaspora whose lives straddle both economies, the nonstop is back on the table for the first time since 2020."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Etihad Is Opening Up Central Asia — and These Visa-Light Stopovers Are a Quiet Win for Indian Travelers",
        "subheadline": "Abu Dhabi's flag carrier is adding Almaty, Tashkent, Baku, and more to its 2026 map. For NRIs already routing through the Gulf, these emerging destinations pair easy entry rules with a natural break in the long haul home.",
        "slug": make_slug("etihad-central-asia-expansion-visa-light-stopovers-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Indian passport holders face onerous visa hurdles for most of Europe, but several Central Asian and Caucasus nations now offer e-visas or visa-free entry — and Etihad's new routes through Abu Dhabi make them an easy, low-friction stopover on the way to or from India.",
        "tags": ["travel", "airlines", "etihad", "central asia", "visa"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/united-kingdom-joins-global-airlines-expand-new-direct-flight-routes/"},
            {"name": "Etihad Airways", "url": "https://www.etihad.com/en/about-us/newsroom"}
        ]),
        "score_total": 64,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15196986/pexels-photo-15196986.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The mountain-ringed cityscape of Almaty, Kazakhstan, a new addition to Etihad's 2026 network",
        "image_attribution": "Pexels",
        "body": """Etihad Airways is in the middle of one of the larger network expansions in its history, and tucked inside the 2026 route announcements is a list that should interest the Indian diaspora more than the headline UAE-Europe additions: a clutch of new Central Asian and Caucasus destinations including Almaty, Tashkent, Baku, Tbilisi, Yerevan, and Bucharest.

On the surface this is Abu Dhabi reinforcing its role as a global transit hub. Look closer and it is something more useful for Indian passport holders — a set of genuinely easy-to-enter destinations now hanging off a route most NRIs already fly.

### The visa problem these routes solve

For Indian citizens, the single biggest friction in international travel is the visa. Schengen Europe means appointments, bank statements, and weeks of waiting. The United Kingdom and the United States are worse. Against that backdrop, the appeal of Central Asia and the Caucasus is straightforward: many of these countries offer e-visas or visa-free entry to Indian nationals, with approvals measured in days rather than weeks.

Kazakhstan and Uzbekistan have built e-visa systems specifically courting Indian tourists. Azerbaijan offers an e-visa that processes quickly online. These are not bucket-list-famous destinations, which is precisely the point — they are uncrowded, affordable, visually spectacular, and reachable without the bureaucratic ordeal that defines so much of an Indian traveler's planning.

### Why the Etihad map makes it work

The NRI travel pattern through the Gulf is well established. A huge share of US-to-India traffic already connects through Abu Dhabi, Dubai, or Doha. What Etihad's expansion does is turn that obligatory layover into an optional adventure.

Instead of a dead two-hour connection in Abu Dhabi, a traveler can break the journey for a few days in Almaty — a city ringed by snow-capped mountains with world-class skiing an hour away — or Tashkent, with its Silk Road architecture and Soviet-era grandeur. On the way back from visiting family in India, a stopover costs little more than the price of the segment and turns a grueling long-haul into two manageable hops with a holiday in the middle.

This is the same logic that has made Gulf carriers' free or cheap stopover programs popular. Etihad's expansion simply widens the menu of where you can stop, and it points it at exactly the destinations Indian travelers can enter with minimal paperwork.

### Who this suits

The new routes are best for a few kinds of diaspora traveler. There is the family that flies to India every couple of years and is tired of the same Dubai layover — a few days in Baku or Tbilisi adds a real trip without a real visa headache. There is the younger NRI looking for an offbeat, photogenic, budget-friendly destination that does not require a Schengen application. And there is the multi-generational group for whom Central Asia's halal-friendly food culture and relaxed pace are an easier sell than a fast-moving European itinerary.

### The practical notes

A few things to keep in mind. Etihad's Central Asian routes are still being phased in through 2026, so schedules and frequencies will firm up over the year — check availability before building a trip around a specific city. Visa rules change, so confirm the current e-visa or visa-free terms for your destination and your specific passport before booking; the easy-entry status of these countries is a policy choice, not a permanent guarantee. And summer in Central Asia can be punishingly hot, while winter brings serious cold and snow — Almaty's ski season is a feature, not a warning, but pack accordingly.

For a community that has learned to treat the Gulf layover as a necessary evil, Etihad has quietly turned it into a doorway. The visa-light corner of the map just got a lot more reachable."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
