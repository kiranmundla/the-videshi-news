#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-02 batch."""

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

# Validate image before inserting
def validate_image(url):
    """Check that the URL returns an actual image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            print(f"  ✓ Image validated: {ct}, {cl} bytes")
            return True
        elif "image" in ct and cl == 0:
            # Some servers don't send Content-Length on HEAD, try GET
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            size = len(r2.content)
            if size > 5000:
                print(f"  ✓ Image validated via GET: {ct}, {size} bytes")
                return True
        print(f"  ✗ Image rejected: {ct}, {cl} bytes")
        return False
    except Exception as e:
        print(f"  ✗ Image validation error: {e}")
        return False

articles = [
    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 1: US Airports Visitor Pass Programs
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "21 US Airports Now Let Your Family Walk You to the Gate — Here's How NRIs Can Use It",
        "subheadline": "A growing number of American airports are reviving pre-9/11 gate access with free visitor passes, and for Indian families who treat airport drop-offs as ceremonial occasions, this changes everything.",
        "slug": make_slug("us-airports-visitor-pass-nri-family-gate-access"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian families are known for their elaborate airport rituals — entire clans showing up for departures, elders blessing grandchildren at the curb, tears flowing freely at Terminal 1. For two decades, post-9/11 security rules forced all of that emotion into a curbside goodbye. Now, 21 US airports — including SFO, a hub for the Bay Area's massive Indian community — let non-ticketed guests apply for free passes to go through security and accompany travelers all the way to the gate.",
        "tags": ["travel", "airports", "usa", "family", "nri-life"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNN Travel", "url": "https://www.cnn.com/2026/06/01/travel/visitor-pass-us-airports"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/guide/airports-no-ticket-past-security/"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/these-airports-allow-unticketed-visitors-through-security"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/2767767/pexels-photo-2767767.jpeg",
        "body": """If you grew up in an Indian household, you know what an airport drop-off looks like. The entire family piles into the car — sometimes two cars. Your mother has packed a steel dabba of food "for the flight." Your father is triple-checking the passport. An uncle who wasn't even invited shows up because he "was in the area." Everyone accompanies you to the terminal entrance, and then comes the hard part: the security line, where non-travelers must stop and wave goodbye through the glass.

For 25 years, that's where the ritual ended. Post-9/11 security rules meant only ticketed passengers could pass through TSA checkpoints. The gate-side farewell — the kind you see in old Bollywood films and '90s Hollywood — was dead.

Now it's coming back.

## Twenty-One Airports and Counting

As of June 2026, twenty-one US airports offer free visitor pass programs that allow non-ticketed guests to go through security and spend time in the terminal. They can shop, eat, watch planes — and, yes, walk a loved one all the way to the gate.

The list includes several airports that matter deeply to NRIs: **San Francisco International Airport (SFO)**, which lets you apply up to 30 days in advance; **Seattle-Tacoma (SEA)**, which has run the longest continuous program since 2018; **Tampa International (TPA)**, which allows unlimited visit time; and **Philadelphia International (PHL)**, **Kansas City (MCI)**, **New Orleans (MSY)**, and **San Antonio (SAT)**, among others.

Pittsburgh International Airport pioneered the concept in 2017 with its myPITpass program, though it paused during COVID and terminal construction. The idea spread. Rosa Johnson, who manages the SEA visitor pass program, told CNN that it has evolved from a revenue initiative — airports wanted more customers in post-security shops and restaurants — into a genuine customer experience tool.

"Nine times out of 10, our SEA visitor pass is the solution," Johnson said, describing how families with elderly travelers, non-English speakers, or passengers with disabilities use the program to provide in-person support all the way to the boarding gate.

## How It Works

The process is straightforward. You apply online — or at a kiosk at some airports — providing your full legal name as it appears on your Real ID or passport, plus the day you want to visit. Most airports process applications within 24 hours. SFO accepts applications up to 30 days out. At airports with same-day kiosks, approval is instant.

Once approved, you go through regular TSA screening with your visitor pass and ID. You cannot use TSA PreCheck or any expedited lane. Some airports restrict you to specific terminals. Capacity limits apply — it's first-come, first-served — so early applications win.

Visit windows vary. Kansas City and Philadelphia cap visits at six hours. Tampa and San Antonio impose no time limit during operating hours. All airports except Albuquerque International Sunport allow minors to apply, provided an adult accompanies them.

## Why This Matters for the Diaspora

The practical applications are obvious: an aging parent arriving from India who needs help navigating a US airport can now have family waiting past security. A first-time international student can be walked to the gate by parents who want every last minute. A family sending their child off to college across the country can make the farewell feel less abrupt.

But there's a cultural dimension too. In Indian families, airport goodbyes are not perfunctory. They are emotional, communal, and often loud. The curb-side checkpoint has been a poor substitute for two decades. These programs restore something that feels both mundane and significant: the right to accompany someone you love to the place where they leave.

Johnson, the SEA airport official, put it simply: "Don't be afraid to pick somebody up that you love from the airport, park there, meet them at their gate. Make it a more leisurely time for human connection."

## What's Not on the List

The program is limited to 21 airports and does not yet include some of the busiest NRI-relevant hubs. **JFK, Newark, LAX, Chicago O'Hare, Dallas-Fort Worth, and Houston IAH** — all major international gateways for India routes — do not currently offer visitor passes. Given that these are also the airports with the most security infrastructure and the highest traffic volumes, adding them would be operationally complex.

Still, the trend is moving in one direction. Two years ago, there were fewer than a dozen. The next airport to launch a program could be any of the ones Indian families care about most."""
    },
    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 2: Indian Carriers Overtaking Gulf Airlines
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Now Flies More International Passengers Than Emirates From India — and the Gap Is Widening",
        "subheadline": "India's largest airline holds 17.6% of the country's international market share while Emirates has slipped to 8.3%, marking a structural shift in how the diaspora gets home.",
        "slug": make_slug("indigo-air-india-overtake-emirates-international-market"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For two decades, Gulf carriers were the default choice for NRIs flying between the US and India — the Dubai or Doha layover was practically a rite of passage. That era is ending. IndiGo and Air India together now command a larger share of India's international traffic than all three Gulf mega-carriers combined, and the Iran crisis has only accelerated the shift. For NRIs, this means more direct options, more competitive fares on Indian carriers, and less dependence on a Middle Eastern hub that has twice been disrupted by geopolitical crises in the past four years.",
        "tags": ["travel", "airlines", "indigo", "air-india", "emirates", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2024/09/19/indigo-and-air-india-surges-ahead-middle-eastern-carriers-decline/"},
            {"name": "AGBI", "url": "https://www.agbi.com/articles/indias-airlines-face-fight-for-market-gains-from-the-gulf/"},
            {"name": "Kotak Securities - InterGlobe Aviation Report", "url": "https://www.kotaksecurities.com"},
            {"name": "Travel Extra Ireland - EASA Bulletin", "url": "https://travelextra.ie/easa-extends-prohibition-on-european-airlines-flying-through-gulf-until-june-10/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "body": """For the better part of two decades, the travel arithmetic for Indian Americans was simple. You booked Emirates, Qatar Airways, or Etihad. You endured a three-hour layover in Dubai, Doha, or Abu Dhabi. You arrived in India having spent roughly 20 hours in transit. The Gulf hub model worked — it was affordable, the service was excellent, and for most US-India city pairs, there were no direct alternatives.

That equation has quietly but decisively changed.

## The Numbers Tell a Clear Story

Recent aviation data shows IndiGo now commands approximately 17.6% of India's international market share, making it the single largest carrier for international flights from Indian airports. Emirates, once the dominant foreign airline in India, has slipped to around 8.3%. Air India, under Tata Group ownership since early 2022, holds 14.3% of the domestic market and is steadily rebuilding its international network with new routes to London, Tokyo, and a dozen other destinations announced this year.

Combined, IndiGo and the Tata aviation portfolio — Air India and Air India Express — now carry a larger share of India's international passengers than Emirates, Qatar Airways, and Etihad put together. This is not a blip. It's a structural realignment.

## What Changed

Three forces converged. First, IndiGo stopped being "just a domestic airline." The carrier has been relentlessly adding international destinations — 32 and counting — including Athens (launched in January 2026 with India's first Airbus A321XLR), London, and Copenhagen. Its codeshare partnerships with Turkish Airlines, British Airways, American Airlines, Qantas, Air France, and KLM now extend its effective reach to hundreds of global destinations. For an NRI flying SFO to Hyderabad, an IndiGo codeshare through Istanbul or London is now a viable alternative to the Dubai connection.

Second, Tata's Air India is spending aggressively. The airline ordered 470 new aircraft — the largest order in commercial aviation history — and has been opening routes that directly serve the diaspora. London-Bengaluru, daily Tokyo service, and expanded US frequencies are designed to bring NRIs onto Indian metal rather than routing them through the Gulf.

Third, the Gulf hub model's vulnerability has been exposed. The Iran conflict that began in late February 2026 closed Gulf airspace for days, stranded hundreds of thousands of passengers, and pushed Emirates to operate at just 60% of its network even after partial recovery. As of late May, Emirates was running about 436 flights daily — better than the April low point but still below pre-crisis volumes. The European Aviation Safety Agency extended its prohibition on European carriers flying through the Gulf until June 10, meaning Lufthansa, Air France, and KLM still cannot route through Dubai or Doha.

## The NRI Calculation

For Indian Americans, the market share shift translates into three practical changes.

**More direct flights.** Air India now operates nonstop service from multiple US cities to Delhi, Mumbai, and Bengaluru, with daily frequencies that didn't exist five years ago. IndiGo's codeshare network connects to US carriers, making one-stop itineraries through non-Gulf hubs increasingly competitive.

**Competitive pricing.** When Indian carriers compete directly with Gulf airlines for the same passenger pool, fares come down. The days of Emirates setting the floor price on US-India routes are numbered. IndiGo's low-cost DNA means it will always undercut on price, even on international routes.

**Reduced geopolitical risk.** The Iran crisis demonstrated that routing all diaspora traffic through a single geographic chokepoint is risky. Indian carriers flying via European hubs, or nonstop, offer a hedge that simply didn't exist when Emirates was the default.

## What Has Not Changed

Gulf carriers still offer superior business class products, more extensive lounge networks, and better loyalty programs than any Indian airline. Emirates' first class remains in a different league. For premium travelers, the Gulf connection is still hard to beat on comfort.

And for NRIs flying to smaller Indian cities — Kochi, Lucknow, Thiruvananthapuram, Ahmedabad — Gulf carriers still offer more one-stop options than Indian airlines can match from the US. IndiGo's strength is in connecting from Indian metros; it cannot yet replicate the depth of Dubai's spoke network.

But the trajectory is unmistakable. Indian carriers are no longer playing catch-up. They are, for the first time, the market leaders on their own country's international routes. For the millions of NRIs who fly between two worlds every year, that is not just a statistic. It is the beginning of a different kind of journey home."""
    },
    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 3: European Airlines Banned From Gulf — NRI Plan B
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "European Airlines Still Cannot Fly to the Gulf — What NRIs Connecting Through Dubai Need to Know",
        "subheadline": "EASA has extended its prohibition on European carriers operating through Gulf airspace until at least June 10, leaving Lufthansa, Air France, and KLM unable to route through Dubai or Doha — and NRIs with summer bookings need alternatives.",
        "slug": make_slug("easa-gulf-flight-ban-european-airlines-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "A significant number of NRIs — particularly those on the East Coast and in the Midwest — book European carriers like Lufthansa, Air France, and KLM to fly to India via Frankfurt, Paris, or Amsterdam, sometimes connecting onward through the Gulf. The EASA ban means those carriers cannot operate to Dubai, Doha, or other Gulf destinations, forcing rebookings and rerouting. Meanwhile, Gulf carriers themselves are operating at reduced capacity. For NRIs planning summer trips to India, this is not an abstract geopolitical situation — it is a direct threat to their travel plans.",
        "tags": ["travel", "airlines", "europe", "gulf", "iran", "nri-advisory"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel Extra Ireland", "url": "https://travelextra.ie/easa-extends-prohibition-on-european-airlines-flying-through-gulf-until-june-10/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uae-and-middle-east-flight-disruption-creates-global-travel-uncertainty/"},
            {"name": "TravelPulse", "url": "https://www.travelpulse.com/news/airlines/several-international-airlines-resume-limited-flights-despite-iran-war"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36681344/pexels-photo-36681344.jpeg",
        "body": """If you booked a Lufthansa ticket from Chicago to Delhi via Frankfurt and Dubai, you may have a problem. If you're flying Air France from New York to Mumbai with a Paris-Doha connection, same story. And if your KLM itinerary routes through Amsterdam and then Abu Dhabi, you need to make a phone call.

The European Union Aviation Safety Agency has extended its Conflict Zone Information Bulletin — effectively a prohibition on European carriers operating through Gulf airspace — until at least June 10, 2026. The directive, originally issued following the US-Israeli military operations against Iran in late February, requires European airlines to avoid the airspace of Iran, Iraq, and Lebanon at all altitudes, and to exercise extreme caution over Bahrain, Israel, Jordan, Kuwait, Qatar, Oman, the UAE, and Saudi Arabia.

In practice, this means Lufthansa, Air France, KLM, and other European carriers cannot fly to Dubai, Doha, or any Gulf destination. War-risk insurance underwriters will not cover European airlines on Gulf routes regardless of what the UAE's own civil aviation authority says, so even if EASA's language stops short of an outright ban, the commercial effect is identical.

## What Is Actually Flying

Gulf-based carriers are operating — but not at full capacity. As of mid-May 2026, Emirates was running approximately 436 daily flights, Etihad 258, and Qatar Airways 341, for a combined total of about 1,035 flights per day. That is a recovery from the April lows but still well below pre-crisis volumes. Emirates announced it would operate at 60% of its network — 83 destinations, including 22 daily flights to India and seven US airports.

The UAE has officially reopened its airspace, and commercial flights are running. But the situation remains fragile. Sporadic missile and drone threats in the region, combined with the US naval presence in the Strait of Hormuz, mean schedules can change at short notice.

For NRIs who fly Gulf carriers directly — Emirates from JFK to Dubai to Delhi, or Qatar Airways from ORD to Doha to Hyderabad — flights are available but not guaranteed to remain stable through the summer.

## The European Carrier Problem

The more acute issue is for NRIs who use European airlines as their primary carriers to India. Lufthansa's Frankfurt hub, Air France's Charles de Gaulle hub, and KLM's Schiphol hub have long served as alternatives to the Gulf connection. These carriers offer competitive fares, strong loyalty programs (Miles & More, Flying Blue), and convenient connections for NRIs in cities like Chicago, Washington, Boston, and Toronto.

Many of these itineraries historically included an option to connect through the Gulf — Lufthansa to Frankfurt, then a partner flight to Dubai or Doha, then onward to India. That routing is now unavailable.

European carriers can still fly to India directly via their own hubs. Lufthansa still flies Frankfurt to Delhi and Mumbai. Air France still operates Paris to several Indian cities. KLM flies Amsterdam to Delhi. These direct European-hub-to-India routings remain unaffected because they overfly Turkey and Central Asia, bypassing the Gulf entirely.

The problem arises when itineraries were booked with Gulf segments, or when the European carrier planned to route through Gulf airspace. Those flights are cancelled, and passengers must rebook.

## What NRIs Should Do Now

**Check your routing.** Log into your airline account and look at the actual flight path, not just the city names. If any segment passes through Dubai, Doha, Abu Dhabi, Bahrain, or Kuwait on a European carrier, that segment is at risk.

**Book direct when possible.** For summer 2026, the safest India routings from the US are either nonstop (Air India from major US cities) or one-stop via European hubs that go directly to India without Gulf connectivity. Lufthansa to Frankfurt to Delhi. Air France to Paris to Mumbai. These work.

**Consider Indian carriers.** Air India's expanded US network and IndiGo's codeshare partnerships through Istanbul offer Gulf-bypass alternatives that did not exist a few years ago. Prices have risen across the board due to reduced capacity, but availability on Indian carriers has been more stable than on Gulf or European airlines.

**Watch the June 10 deadline.** EASA's current bulletin expires on June 10. If it is extended again — which analysts consider likely given that the underlying conflict has not been resolved — summer travel plans through the Gulf will remain complicated through July and August, the peak NRI travel season.

**Protect your booking.** If you have a European carrier ticket with Gulf segments booked before the crisis, you are entitled to rerouting or a refund under EU passenger rights regulation EC 261/2004. Contact the airline directly rather than waiting for automated rebooking, which may place you on suboptimal itineraries.

The situation is not permanent. Gulf airspace will eventually return to full operations, and European carriers will resume Gulf routes when insurance underwriters are satisfied with the risk profile. But "eventually" is not a useful word when your flight to India is booked for June 20.

Plan accordingly."""
    },
]

# Validate images and insert
for art in articles:
    print(f"\n📝 Processing: {art['headline'][:60]}...")
    
    # Validate image
    if art.get("image_url"):
        print(f"  Validating image: {art['image_url'][:80]}...")
        if not validate_image(art["image_url"]):
            print("  ⚠ Image failed validation, removing")
            art["image_url"] = None
    
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ Published: {art['slug']}")
    except Exception as e:
        print(f"  ❌ Error: {art['slug']}: {e}")
