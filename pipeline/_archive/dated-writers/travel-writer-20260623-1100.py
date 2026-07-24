#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env (prefer ~/.env.supabase)
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Air India's New Maharaja Lounge at SFO Is the First Real Sign Its US Overhaul Has Crossed the Pacific",
        "subheadline": "The carrier's first 'signature' lounge outside India opens at San Francisco's International Terminal — but with SFO nonstops gone, who actually gets to use it is the catch.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-overhaul-bay-area-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The Bay Area holds one of the largest concentrations of Indian Americans in the US, and SFO is their primary gateway home — a flagship Air India lounge here is a direct upgrade to how the Silicon Valley diaspora flies to India.",
        "tags": ["travel", "airlines", "air india", "sfo", "lounge", "bay area"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AFAR — Air India Opens Maharaja Lounge at San Francisco Airport", "url": "https://www.afar.com/magazine/air-india-opens-maharaja-lounge-at-san-francisco-airport"},
            {"name": "The Points Guy — Inside Air India's new Maharaja Lounge at SFO", "url": "https://thepointsguy.com/news/air-india-maharaja-lounge-sfo/"},
            {"name": "Air India Newsroom — Maharaja Lounge", "url": "https://www.airindia.com/in/en/about-us/press-release.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/San_Francisco_International_Airport_International_Terminal.jpg/1280px-San_Francisco_International_Airport_International_Terminal.jpg",
        "image_caption": "The International Terminal at San Francisco International Airport, home to Air India's new Maharaja Lounge near the A gates.",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India has opened its first "signature" Maharaja Lounge outside India — and it picked San Francisco to do it. The 3,300-square-foot space sits past security in SFO's International Terminal, a short walk past the Air France lounge and up one level near Gate A1. It is a small room with an outsized message: the most visible piece of Air India's makeover has now landed in the Bay Area, the single densest pocket of Indian tech talent in the United States.

## What's actually inside

The new lounge is a deliberate step up from the airline's older US offerings. There are live cooking stations, a speakeasy-style cocktail bar, and decor built partly from upcycled aircraft parts — the same design language Air India rolled out at its flagship Maharaja Lounge in Delhi's Terminal 3 earlier this year. There is even a "first-class lounge-within-a-lounge" for the airline's top cabin. Operating hours run roughly 6:30 a.m. to 10 p.m., flexing with flight schedules.

This is not Air India's first lounge on US soil. It has long run a Maharaja Lounge at New York's JFK, but that outpost is now closed for renovation, and when it reopens the airline says it will be an "upgraded space" rather than a true signature flagship. For now, SFO is the showcase.

## Why San Francisco, and why it matters to the diaspora

The choice of SFO is not sentimental. The Bay Area's Indian American population — heavily concentrated in Santa Clara, Alameda and surrounding counties — flies to India in large, predictable waves around summer, Diwali and the winter holidays. A premium lounge here is a direct quality-of-life upgrade for tens of thousands of frequent flyers who have spent years making do with crowded contract lounges or none at all.

It also fits a larger pattern. Since the Tata Group regained control of Air India in 2022, the carrier has poured money into new Airbus A350s with upgraded business-class suites, cabin refurbishments on older jets, and a steadily expanding lounge network now spanning Bengaluru, Delhi, New York and San Francisco. The airline says its Net Promoter Score — its passenger-satisfaction yardstick — hit an all-time high of 37 last September. The SFO lounge is the physical proof of that turnaround reaching American shores.

## The catch every Bay Area flyer should know

Here is the awkward part. Air India suspended its Bengaluru–San Francisco and Mumbai–San Francisco nonstops from March 2026, rerouting North America traffic through Delhi as it grappled with fuel costs, crew strain and airspace curbs. That means the diaspora's most convenient direct links from SFO to South India and West India are, for now, gone. The lounge opens just as the routes that would fill it have thinned.

So who gets in? The Maharaja Lounge is open to passengers flying First and Business Class on Air India, plus Maharaja Club Platinum and Gold members and eligible Star Alliance Gold members. With Air India's own SFO nonstops paused, the most reliable way for a Bay Area traveler to use it is via the Delhi nonstop (10 weekly) or by holding Star Alliance Gold status and flying a partner carrier like United on a qualifying international itinerary. Economy passengers without status remain on the outside looking in.

## The practical read

For the Silicon Valley diaspora, the lounge is best understood as a statement of intent rather than an everyday perk — at least until Air India restores meaningful SFO nonstop capacity. If you fly business class to Delhi, or you hold Star Alliance Gold, it is a genuine upgrade to a long travel day: a proper meal, a cocktail, and a quiet corner before a 15-hour flight.

If you are an economy flyer, the smarter near-term play is a premium credit card with Priority Pass or a Star Alliance lounge benefit, which still gets you into a comfortable space at SFO's International Terminal. And keep an eye on Air India's schedule: the lounge is a strong signal the airline wants the Bay Area back. The day the SFO nonstops return, this small room near Gate A1 will suddenly be one of the most useful addresses in the terminal for anyone flying home to India.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Samarkand Is the Silk Road Trip Indians Can Do on a $20 Visa and a Three-Hour Flight — and 2026 Is the Year It Booms",
        "subheadline": "Uzbekistan is riding a record tourism surge, and for Indian travelers the math is unusually friendly: a quick e-visa, daily nonstops from Delhi, Mumbai and Hyderabad, and a high-speed train to the Registan.",
        "slug": make_slug("uzbekistan-samarkand-silk-road-india-evisa-nonstop-nri-trip"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "For NRIs planning a family trip that's exotic but low-friction, Uzbekistan offers a rare combination — a $20 online visa, sub-three-hour nonstops from India, and Mughal-era Islamic architecture that resonates deeply with South Asian heritage.",
        "tags": ["travel", "uzbekistan", "samarkand", "visa", "destinations", "silk road"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Uzbekistan Silk Road Travel Boom 2026", "url": "https://www.travelandtourworld.com/news/article/south-korea-joins-qatar-china-russia-kazakhstan-uzbekistan-silk-road-travel-boom/"},
            {"name": "Wego Travel Blog — Uzbekistan Visa for Indians 2026", "url": "https://blog.wego.com/uzbekistan-visa-for-indians/"},
            {"name": "Femina — Why Samarkand Is The New Favourite", "url": "https://www.femina.in/travel/uzbekistan-2026-samarkand"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Registan_01.jpg/1280px-Registan_01.jpg",
        "image_caption": "The Registan in Samarkand, Uzbekistan — three madrasahs framing the heart of the ancient Silk Road city.",
        "image_attribution": "Wikimedia Commons",
        "body": """Uzbekistan is having a moment. The Central Asian nation is posting record tourist arrivals for a third straight year, fueled by visa liberalization, new flight routes and a wave of hotel investment in its Silk Road cities. Chinese arrivals alone have surged past 278,000, and the country is now actively courting travelers from India, the Gulf and beyond. For Indian families weighing where to go in 2026, the case for Samarkand has quietly become one of the strongest in Asia.

## The visa math actually works

Uzbekistan is not visa-free for Indian passport holders — but the alternative is almost as painless. India is one of 76 countries eligible for the Uzbekistan e-Visa: a single or multiple-entry visa valid for 30 days, costing about US$20, applied for online at least three days before travel. There is no embassy queue, no invitation letter, no bank-balance certificate for a standard tourist trip.

There is also a 5-day visa-free transit window for Indians passing through Uzbek airports — but read the fine print. It applies only if you hold a confirmed onward ticket to a third country and your outbound flight is on Uzbekistan Airways. For a straightforward there-and-back holiday, the $20 e-visa is the cleaner route; the transit waiver is a niche hack for travelers already routing through Tashkent to somewhere else.

## Getting there is easier than getting to Goa in season

This is the part that surprises people. Daily direct flights operate from Delhi, Mumbai and Hyderabad to Tashkent, with flight times of just under three hours — shorter than many domestic Indian sectors. Once on the ground, the high-speed Afrosiab train links Tashkent to Samarkand in about two hours, gliding past the steppe to drop you near the city's monumental core. You can land in Tashkent in the morning and be standing in front of the Registan by mid-afternoon.

## Why the architecture hits differently for South Asians

Samarkand's draw is its Silk Road heritage, and for Indian travelers the resonance runs deeper than postcard appeal. The turquoise-domed madrasahs of the Registan, the soaring portals, the intricate tilework — this is the same Timurid and Persianate tradition that shaped Mughal architecture from the Taj Mahal to Humayun's Tomb. Babur, who founded the Mughal Empire, came from this region. Walking Samarkand, Bukhara and Khiva feels less like visiting a foreign country and more like meeting the ancestor of a familiar architectural language.

Beyond the monuments, the appeal is authenticity: family-run restaurants serving plov, bustling bazaars, ancient madrasahs sitting beside modern cultural spaces, and a high-speed rail network that makes the UNESCO triangle of Samarkand–Bukhara–Khiva genuinely doable in a week.

## Practical planning notes

Timing matters. Spring (March–May) and autumn (September–November) offer the most comfortable weather, with mild days and clear skies. Summer in Samarkand can push past 40°C, while winter brings unpredictable cold snaps and thinner crowds. Most travelers find two to three days in Samarkand ideal — enough to see the Registan at sunset (its best light), wander the Shah-i-Zinda necropolis, and absorb the bazaars without rushing.

Book accommodation early. Hotel rooms in Samarkand and Bukhara fill quickly during peak season as the tourism boom widens, and international operators like Hilton have already planted flags in the city. Lock in flights and the Afrosiab train in advance during festival and long-weekend windows, when Indian outbound demand spikes.

## The bottom line for NRI families

For a diaspora family that wants a trip that feels genuinely off the usual Dubai-Singapore-Bali circuit but doesn't demand the visa gymnastics of Europe or the US, Uzbekistan is close to ideal in 2026. A $20 online visa, a sub-three-hour nonstop, English increasingly spoken in tourist hubs, and a destination steeped in a heritage that South Asians recognize in their bones. The Silk Road boom means more flights and more hotel choice — but it also means the quiet, uncrowded version of Samarkand has a shelf life. As one local tourism line puts it: some places demand to be seen before they change.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Diwali Flights Home Go on Sale Now — and the DGCA Is Adding 1,700 Extra Flights to Stop the Usual Fare Gouge",
        "subheadline": "With festival demand set to surge and fuel surcharges already biting, India's regulator has ordered carriers to inject capacity. For NRIs, the booking window is open — and waiting is the expensive move.",
        "slug": make_slug("diwali-2026-flights-india-dgca-extra-flights-nri-booking-window"),
        "category": "travel",
        "vertical": "airfare",
        "diaspora_angle": "Diwali is the single biggest travel-home occasion for the Indian diaspora, and US-India fares historically spike 50-80% on peak festival dates — knowing the booking window and the regulator's capacity injection can save an NRI family thousands.",
        "tags": ["travel", "diwali", "airfare", "flights", "dgca", "festival"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "AgentBazar — DGCA Curbs Diwali Airfare Surge, Adds 1,700+ Flights", "url": "https://blog.agentbazar.in/dgca-curbs-diwali-airfare-surge/"},
            {"name": "Mint — How to plan summer holidays amid soaring airfares", "url": "https://www.livemint.com/money/personal-finance/how-to-plan-summer-holidays-amid-soaring-airfares-west-asia-war.html"},
            {"name": "Wego Travel Blog — Air India Fuel Surcharge 2026", "url": "https://blog.wego.com/air-india-fuel-surcharge-2026/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12940608/pexels-photo-12940608.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Digital screens display international flight information at an airport departure hall.",
        "image_attribution": "Pexels",
        "body": """Diwali falls on November 8 this year, and for the Indian diaspora that means the most predictable, most expensive booking decision of the calendar is already live. India's aviation regulator, the DGCA, has stepped in early — ordering the major carriers to add more than 1,700 extra flights and to keep fares from running away. For NRIs flying in from the US, UK and Canada, the message is simple: the booking window is open, and the longer you wait, the more you pay.

## What the regulator is doing

Indian airfares are deregulated, but the DGCA retains the power to intervene when increases turn "excessive" — and festival season is exactly when that happens. Historically, fares on high-demand domestic routes have jumped 50–80% around Diwali. To blunt that, the Ministry of Civil Aviation has directed carriers to inject capacity across the busiest sectors:

- **IndiGo**: roughly 730 additional flights across 42 sectors
- **Air India and Air India Express**: about 486 extra flights across 20 routes
- **SpiceJet**: around 546 extra flights on 38 sectors

The intervention is aimed primarily at domestic fares — the connecting legs that get NRIs from their international gateway (Delhi, Mumbai, Bengaluru) onward to hometowns in Tier-2 and Tier-3 India. That is precisely where festival pricing has historically been most brutal, so the extra seats matter most for the final hop home.

## The headwind: this isn't a normal year

Capacity is only half the story. The bigger pressure on 2026 fares is cost. Conflict-driven airspace closures over parts of West Asia have forced westbound flights from India onto longer, fuel-hungry reroutes, and Air India has layered on fuel surcharges of up to ₹18,600 per ticket on long-haul international flights — its first carrier-imposed fuel levies in years, rolled out in phases since March.

The result, by industry estimates: nonstop international fares running about 22% above pre-conflict levels, with Delhi/Mumbai-to-US routes up 25–30% year-on-year for the peak season. The DGCA's domestic capacity push helps with the India-side connection, but it does nothing for the trans-Pacific or trans-Atlantic leg that dominates an NRI ticket's cost. That part is supply-and-demand, and demand around Diwali only goes one way.

## How NRIs should play it

The practical playbook for this year:

**Book the international leg now, not later.** Diwali peak dates (roughly the first half of November) are the most contested of the year. With fuel surcharges already baked into fares and capacity on some West Asia hubs still recovering, there is little reason to expect prices to fall as the date approaches — and every reason to expect them to climb.

**Shift your dates if you can.** Flying in a week before Diwali or returning a week after the peak can cut hundreds off the fare. The most expensive window is the cluster of dates immediately around the festival itself.

**Lock the domestic connection early.** The DGCA's 1,700 extra flights mean more availability on the Delhi/Mumbai-to-hometown legs — but on popular festival sectors those added seats sell through. Booking the connection at the same time as the international ticket avoids a painful last-minute domestic fare.

**Consider the Gulf hubs.** Carriers routing through Abu Dhabi, Doha and Dubai have been rebuilding capacity and competing hard on India fares. A one-stop itinerary via a Gulf hub can undercut a nonstop by a meaningful margin, especially out of secondary US cities.

**Watch for award space.** If you hold miles, Star Alliance and oneworld partner space to India tends to open in waves. Festival dates go fast, so set alerts now.

## The bottom line

The regulator's capacity injection is real relief on the India side, and it should keep the worst domestic gouging in check. But the trans-Pacific math is unforgiving this year, and the cheapest Diwali ticket is almost always the one booked early. For diaspora families set on being home for the festival of lights, the smart move is to treat the booking like the fixed appointment it is — and make it now.
"""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\nInserted {len(inserted)}/{len(articles)} articles.")
for h in inserted:
    print(" -", h)
