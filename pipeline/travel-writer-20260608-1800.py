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
        "headline": "IndiGo Just Pulled Six Asian Destinations Off the Board for Summer — Here's What NRIs Planning a Layover Trip Need to Know",
        "subheadline": "India's largest airline is suspending flights to Hong Kong, Shanghai, and four Southeast Asian destinations from July through September, citing fuel costs and airspace disruptions. If you were planning a side trip during your India visit, your options just narrowed.",
        "slug": make_slug("indigo-suspends-six-asian-routes-summer-nri-impact"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who route through India often tack on a quick Bangkok, Langkawi, or Hong Kong trip. IndiGo's summer pullback eliminates the cheapest options on six popular Asian routes, forcing travelers onto pricier carriers or longer connections.",
        "tags": ["travel", "airlines", "indigo", "southeast asia", "hong kong", "route suspensions"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/hong-kong-joins-shanghai-krabi-ho-chi-minh-city-langkawi-siem-reap-flights-suspended-as-indigo-is-pulling-back-from-six-international-routes-until-september/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/flights/why-indigo-is-temporarily-pulling-out-of-six-international-markets-this-summer"},
            {"name": "Reuters via Hindu Business Line", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg/1280px-Airbus_A320-232_VT-IEZ_IndiGo_Airlines.jpg",
        "image_caption": "An IndiGo Airbus A320 on the tarmac — the airline is pulling back from six Asian routes this summer",
        "image_attribution": "Wikimedia Commons",
        "body": """IndiGo has confirmed what aviation watchers suspected was coming: India's largest airline is temporarily suspending flights to six international destinations across Asia this summer. The pullback, effective July 1 through September 30, eliminates direct service from Indian cities to Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap.

The timing is notable. These are precisely the routes that budget-conscious Indian American families have used to bolt a quick beach holiday or city break onto a summer visit home. A five-day Langkawi detour after two weeks in Kerala, or a long weekend in Hong Kong before flying back to SFO — these itineraries worked because IndiGo made them cheap. That arithmetic no longer holds.

## What's Getting Cut

The suspensions affect multiple gateway cities in India:

- **Hong Kong**: Flights from Delhi, Bengaluru, and Chennai — all paused
- **Shanghai**: The Kolkata connection, barely a year old, goes dark
- **Ho Chi Minh City**: Kolkata service suspended
- **Krabi**: Delhi and Bengaluru routes shelved
- **Langkawi**: Bengaluru link dropped
- **Siem Reap**: Kolkata flights paused from July 3

IndiGo has also announced frequency reductions on routes to Singapore, Bangkok, Phuket, Penang, and Reunion Island from several Indian cities. The airline says bookings should reopen from October, "subject to market conditions and demand trends" — language that leaves the door open for some routes to not come back at all.

## Why Now

Three forces are converging. Jet fuel prices have spiked nearly 70% year-on-year to an average of $152 per barrel, according to IATA data released this week. Airspace restrictions linked to the Middle East conflict are forcing longer flight paths and higher fuel burn on westbound routes. And monsoon-season demand on these leisure-heavy Asian routes simply doesn't justify the operating costs.

IndiGo's CEO Pieter Elbers has framed the move as "capacity optimization" — pulling aircraft off underperforming routes and redeploying them on corridors with better yields. The airline is simultaneously adding widebody orders for A321XLR and A350 aircraft, signaling that the international retreat is tactical, not strategic. The long-haul push toward Athens, Istanbul, Bali, and Seoul remains on track for FY27.

But the timing also reflects a broader industry reckoning. Spirit Airlines shuttered last month — the first airline casualty directly attributed to the Iran-linked fuel price shock. Smaller carriers globally are under existential pressure.

## What NRIs Should Do

If you've already booked an IndiGo flight on any of these routes for July through September, the airline is offering rerouting and refund options. But the practical reality is that alternatives are more expensive. Singapore Airlines, Cathay Pacific, and Thai Airways still serve these destinations from Indian cities, but at multiples of what IndiGo was charging.

A few strategies worth considering:

**Reroute through Singapore or Bangkok.** Both remain well-served from major Indian cities, and connecting flights to Langkawi, Krabi, or Siem Reap are plentiful — just not on IndiGo's dime.

**Book the side trip separately from the US.** Depending on timing, a positioning flight from the US to Hong Kong or Ho Chi Minh City may be cheaper than routing through India, especially if you're using miles on Cathay or United.

**Wait for October.** If the trip is flexible, IndiGo's own messaging suggests most routes will resume. Monsoon season ends, fuel hedges kick in, and demand picks up.

https://x.com/IndiGo6E/status/2063220585854058855

## The Bigger Picture

IndiGo isn't retreating from international flying — quite the opposite. The airline now holds 17.6% of India's international market share, overtaking every Gulf carrier. Its Delta Air Lines codeshare, announced this week, will eventually let IndiGo passengers book through to dozens of US destinations on a single ticket. The long game is clear: India's largest domestic carrier wants to become a global airline.

But getting there means surviving 2026's fuel crisis first. For NRIs who've grown used to IndiGo's cheap Asia connections during India trips, this summer is a reminder that budget aviation runs on margins thin enough to evaporate when jet fuel does the wrong thing."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Global Airlines Just Lost Half Their Expected Profits — and Your Flight Home Is Paying for It",
        "subheadline": "IATA slashed its 2026 industry profit forecast from $41 billion to $23 billion. Jet fuel at $152 a barrel, Gulf hub shutdowns, and Spirit Airlines' collapse tell the story of an industry under pressure — and NRIs are absorbing the cost.",
        "slug": make_slug("iata-airline-profit-forecast-halved-nri-fares"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans flying the US-India corridor are paying 20-30% more than a year ago. Gulf carriers that served as the cheapest transit option are cutting routes, and Spirit Airlines — a go-to for domestic US legs — is gone. The industry's pain is showing up in every NRI family's travel budget.",
        "tags": ["travel", "airlines", "IATA", "jet fuel", "fares", "gulf airlines", "spirit airlines"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/global-airlines-slash-2026-profit-forecast-fuel-shock-iran-war-2026-06-07/"},
            {"name": "IATA via Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/iata-cuts-2026-airline-profit-forecast-amid-rising-fuel-costs/article69662781.ece"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/delta-airline-stocks-iata-profit-warning-1a4f6e8c"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/outbound-travel-plummets-over-20-as-west-asia-conflict-disrupts-tourism/article69664011.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16108906/pexels-photo-16108906.jpeg",
        "image_caption": "Ground crew servicing a commercial aircraft — airlines face a $350 billion fuel bill in 2026",
        "image_attribution": "Pexels",
        "body": """The numbers landed like a gut punch at IATA's annual meeting in Rio de Janeiro this weekend. The International Air Transport Association — the trade body representing 370-plus airlines that carry 85% of the world's passengers — cut its 2026 net profit forecast from $41 billion to $23 billion. That's a 44% reduction, and it's roughly half the $45 billion the industry earned last year.

The immediate cause is jet fuel, which has surged to an average of $152 per barrel — nearly 70% higher than 2025 levels. The industry's total fuel bill is expected to hit $350 billion this year, up from $252 billion last year, making fuel about a third of total operating costs. Even as revenues rise 9.4% to $1.16 trillion, the cost squeeze is relentless.

For the estimated 4.5 million Indian Americans who fly the US-India corridor at least once a year, the forecast isn't abstract economics. It's the $1,800 roundtrip fare that used to be $1,400. It's the Emirates routing through Dubai that now takes four extra hours because of Middle Eastern airspace closures. It's the Spirit Airlines fare from San Francisco to Los Angeles that doesn't exist anymore because Spirit is gone.

## The Gulf Problem

The Middle East conflict — triggered by US and Israeli strikes on Iran — has reshaped the airways that NRIs depend on most. Gulf carriers like Emirates, Qatar Airways, and Etihad run some of the most popular US-to-India transit routes, funneling passengers through Dubai, Doha, and Abu Dhabi. At the start of the conflict, regional airspace shut down almost completely. It's partially reopened, but carriers are still rerouting flights around restricted zones, burning more fuel and adding hours to journeys.

IATA Director General Willie Walsh was blunt: Middle East airlines are "likely to slip into the red" this year. For NRIs, that translates to fewer flights, higher fares, and less schedule reliability on Gulf-routed itineraries — exactly the routes that millions of diaspora families have used for decades because they were the cheapest way home.

India's own outbound travel data confirms the shift. Provisional numbers from the tourism ministry show a 22.5% year-on-year decline in Indian nationals traveling overseas in April — 22.34 lakh travelers, down sharply from the year before. The UAE, India's single largest outbound destination at 25% of all traffic, saw steep declines. Saudi Arabia dropped out of the top two. Thailand and Vietnam picked up some of the slack, but the aggregate picture is clear: geopolitical disruption is rerouting money and passengers.

## Who's Getting Hurt

The pain isn't evenly distributed. North American airlines — where most US-India flights originate or terminate — are expected to earn $9.4 billion of the global $23 billion in profits, down from $12.4 billion last year. US carriers have largely abandoned fuel hedging, which means they're absorbing the full price shock and passing it to passengers through higher fares.

Walsh expects some smaller airlines to go bankrupt or be absorbed by larger carriers this year. Spirit Airlines' collapse last month was the first domino — a low-cost carrier that couldn't survive the fuel spike. Walsh predicted more would follow: "In an environment where demand remains pretty robust but capacity comes down, fares will remain elevated."

That dynamic — steady demand, constrained supply, higher costs — is the textbook recipe for sustained fare inflation. And the US-India corridor, where load factors routinely exceed 90%, is exactly the market where airlines have the pricing power to push through increases.

## What NRIs Can Do

The honest answer: not much in the short term. But there are edges to find.

**Book early and lock fares.** Airlines are adjusting prices upward as fuel costs hit. A ticket bought in June for a December trip will almost certainly be cheaper than one bought in October.

**Consider direct flights.** Air India's expanding nonstop network — Delhi and Mumbai to New York, Newark, SFO, Chicago, and now London-Bengaluru on the A350 — bypasses Gulf hubs entirely. The fares are higher than one-stop options, but the time savings and schedule reliability are worth the premium in a disrupted year.

**Watch for off-peak windows.** September through mid-November, after monsoon season but before the winter holiday rush, historically offers the best fares on the US-India corridor. With capacity constrained, those windows may be narrower this year — but they'll still exist.

**Stack loyalty programs.** If you're split across Star Alliance (United/Air India), SkyTeam (Delta), and Oneworld (American/Qatar), 2026 is the year to consolidate. Status gets you rebooking priority when flights get cut or rerouted — and that's happening more often.

The airline industry will recover. It always does. But the NRI community's particular dependence on Gulf transit routes and low-cost carriers means this turbulence hits closer to home than most. Budget accordingly."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
