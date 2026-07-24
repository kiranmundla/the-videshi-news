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
        "headline": "Air India and Saudia Just Linked Their Networks — Why Gulf-Based NRIs Get the Biggest Win",
        "subheadline": "A reciprocal codeshare starting June 21 puts dozens of India and Saudi cities on a single ticket, cutting the separate-booking gamble for millions of workers and pilgrims.",
        "slug": make_slug("air-india-saudia-codeshare-gulf-nri-single-ticket"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "For the roughly 2.5 million Indians working in Saudi Arabia, a single through-ticket means checked-through bags, one PNR, and protected connections instead of the risky self-transfer between two separate bookings.",
        "tags": ["travel", "airlines", "air india", "saudia", "gulf", "codeshare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AeroRoutes — Air India / Saudia Codeshare", "url": "https://aeroroutes.com"},
            {"name": "VisaHQ — Saudia and Air India sign codeshare", "url": "https://www.visahq.com/india/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG/1280px-Boeing_777-337ER_-_Air_India_%28VT-ALK%29.JPG",
        "image_caption": "An Air India Boeing 777-300ER, the widebody type used on the carrier's long-haul Gulf and US routes",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India and Saudia begin a reciprocal codeshare on June 21, and for the Indian community spread across the Gulf it is a quietly important change. The agreement lets each airline sell seats on the other's flights under its own code, which in plain terms means a passenger can book Jeddah to Lucknow, or Riyadh to Kochi, on one ticket with one set of rules — instead of stitching together two separate bookings and hoping the bags and the timings cooperate.

## What the deal actually covers

Under the pact, Saudia places its "SV" code on Air India flights connecting Jeddah and Riyadh to a string of Indian cities, while Air India puts its code on Saudia services into Saudi Arabia and onward to several domestic Indian destinations. The published route list is wide: from the Saudi side, Jeddah and Riyadh link to Delhi, Mumbai, Madinah, Dammam, Abha, Gassim, Gizan and Taif; from the Air India side, the network fans out to Bangalore, Chennai, Hyderabad, Kochi and Lucknow via Delhi and Mumbai.

The headline benefit is not a new airplane in the sky — both carriers already fly these corridors — but a new way to buy the journey. Through-ticketing means one reservation, through-checked baggage to the final destination, and recognised frequent-flyer accrual. Crucially, it also means the airline owns the connection: if the first leg runs late, the passenger is rebooked rather than left stranded with a missed self-transfer and no recourse.

## Why this lands hardest for Gulf NRIs

Saudi Arabia is home to roughly 2.5 million Indian nationals, the single largest expatriate group in the Kingdom. Most are not flying Delhi-to-New-York glamour routes; they are construction workers, nurses, drivers, engineers and shopkeepers flying home to tier-two cities — Lucknow, Kochi, Hyderabad — where direct Gulf service is thin or seasonal. For them, the old reality was two tickets: a Gulf carrier to Mumbai or Delhi, then a separate domestic hop, with the connection entirely at their own risk.

That self-transfer is exactly where things go wrong. A delayed inbound flight can mean a forfeited domestic ticket, an unplanned overnight, and bags that have to be collected and re-checked. The codeshare collapses that gamble into a single contract of carriage. For a worker sending money home on a tight budget, the difference between a protected connection and a lost ticket is real money.

There is a pilgrimage dimension too. The route map deliberately includes Madinah and ties into Jeddah, the gateway for Hajj and Umrah. Indian Muslims — who make up one of the largest national contingents at the annual pilgrimage — gain smoother one-ticket routing from Indian metros through to the holy cities, with baggage handled end to end.

## The competitive backdrop

The tie-up fits Air India's post-privatisation playbook under the Tata Group: rather than chase every bilateral route on its own metal, the carrier is leaning on alliances and codeshares to widen its map cheaply. Saudia, for its part, already carries heavy volumes of visiting-friends-and-relatives traffic and pilgrims, and the deal deepens its Indian reach without adding frequencies.

For the diaspora, the practical takeaway is to check the new combined itineraries when booking. Codeshare fares sometimes unlock lower booking classes in global distribution systems when both airlines appear on one ticket, and the single-PNR structure is worth more than a marginal price difference when a tight connection is on the line.

## What to watch next

Both airlines have signalled that international codeshare destinations beyond the initial India-Saudi pairs could follow later in the year, which would extend the single-ticket convenience to onward points in Europe and beyond. For now, the advice is simple: if your trip home routes through Jeddah or Riyadh, look for the joint itinerary before booking two separate legs. Starting June 21, the safer ticket and the cheaper ticket may finally be the same one."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "British Airways Is Quietly Reopening US Cities to India — and It's a Win for NRIs Far From the Big Hubs",
        "subheadline": "St. Louis, Dallas and Miami are back on BA's map this summer, giving Indians in mid-tier American cities a one-stop route home with a family-friendly baggage allowance.",
        "slug": make_slug("british-airways-us-cities-india-one-stop-nri-secondary-hubs"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "For Indian families in Missouri, North Texas and South Florida, a BA one-stop via London beats the usual two-stop slog — and the two free checked bags matter when you're hauling a household home for the summer.",
        "tags": ["travel", "airlines", "british airways", "us-india", "routes"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Indian Eagle — Airlines Starting New USA to India Flight Routes in 2026", "url": "https://www.indianeagle.com/travelbeats/airlines-starting-new-flights-usa-to-india/"},
            {"name": "British Airways route network", "url": "https://www.britishairways.com"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/04/British_Airways%2C_G-ZBJH%2C_Boeing_787-8_Dreamliner.jpg",
        "image_caption": "A British Airways Boeing 787 Dreamliner, the type operating BA's restored US secondary-city routes via London Heathrow",
        "image_attribution": "Wikimedia Commons",
        "body": """The flashiest India aviation news always involves a new nonstop. But for the large slice of the diaspora that does not live in New York, the Bay Area or Chicago, the more useful story this summer is a quieter one: British Airways is reopening a clutch of US secondary cities and wiring them back into India via London Heathrow.

## The routes coming back

Since April 19, BA has flown to St. Louis, Missouri four times a week with a Boeing 787 Dreamliner, connecting onward to Delhi and Mumbai through Heathrow. Dallas-Fort Worth, which BA had pulled back, is restored to a daily service, and Miami has been bumped up to a double-daily operation. The airline is also pushing frequencies on the southern coast, ramping toward 14 weekly services to San Diego and Austin.

None of this is a nonstop to India, and that is the point. These are one-stop itineraries — a single transatlantic hop to London, then a connection to an Indian metro on one ticket — aimed at travellers for whom the nearest nonstop gateway is a domestic flight away to begin with.

## Why a one-stop via London still matters

For an Indian family in St. Louis, the practical options to reach Delhi have long been two-stop ordeals: a domestic feeder to a coastal hub, then a long-haul, then sometimes another connection. United and American offer one-stop routings, but, as travel agents serving the community point out, their basic transatlantic and US-India fares often allow just one free checked bag — a genuine headache for families travelling with children and the inevitable summer haul of gifts and supplies.

British Airways, by contrast, runs three cabins on the 787 — World Traveller (economy), World Traveller Plus (premium economy) and Club World (business) — and its India itineraries typically come with a more generous checked-baggage allowance. When you are moving a household across the planet for two months, the bag policy is not a footnote; it can be the deciding factor between airlines.

## The bigger pattern

BA's moves are part of a broader 2026 reshuffle in the US-India corridor, as one-stop European and Gulf carriers compete hard for diaspora traffic that does not originate at a major hub. SWISS is adding Bengaluru from Zurich in October, wired into a wide US network. Qatar Airways is returning to Philadelphia from August 1. Etihad has opened Charlotte. Cathay Pacific is back in Seattle. The common thread: airlines are chasing the Indian-American traveller in mid-tier cities — Charlotte, Philadelphia, St. Louis, San Diego — who has historically been underserved by nonstops.

For the diaspora, that competition is good news. More one-stop options through more hubs means more fare choice and less reliance on a single carrier's schedule.

## How to play it

If you live within reach of St. Louis, Dallas, Miami, San Diego or Austin, it is worth pricing a BA one-stop against the usual two-stop routings before booking the summer trip home. Compare not just the headline fare but the baggage allowance and the total elapsed time — a single connection at Heathrow can shave hours off an itinerary that would otherwise route through two airports.

The era of every NRI needing to drive or fly to a coastal mega-hub to begin a journey to India is slowly fading. The nonstops still grab the headlines, but for families away from the big gateways, a well-timed one-stop is quietly becoming the smarter way home."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Scandinavia Has a Nonstop to India Again — and It Doubles as a New Backdoor Route Home for US NRIs",
        "subheadline": "SAS's Copenhagen-Mumbai service, its first to India in 17 years, is timed to feed travelers from New York, Boston and other US cities onward to Mumbai.",
        "slug": make_slug("sas-copenhagen-mumbai-nonstop-us-nri-backdoor-route"),
        "category": "travel",
        "vertical": "airlines",
        "diaspora_angle": "SAS deliberately timed its Copenhagen-Mumbai flights to connect with its US gateways, giving East Coast NRIs a new one-stop path to Mumbai via Scandinavia just as Gulf airspace stays unreliable.",
        "tags": ["travel", "airlines", "sas", "mumbai", "europe", "us-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SAS Group — SAS launches new route between Copenhagen and Mumbai", "url": "https://www.sasgroup.net"},
            {"name": "The Hindu BusinessLine — SAS launch flight turns back due to approval delays", "url": "https://www.thehindubusinessline.com"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/SAS_Scandinavian_Airbus_A330-300_SE-REH_at_Washington_Dulles_August_2022.jpg/1280px-SAS_Scandinavian_Airbus_A330-300_SE-REH_at_Washington_Dulles_August_2022.jpg",
        "image_caption": "A Scandinavian Airlines Airbus A330-300, the aircraft operating the new Copenhagen-Mumbai route",
        "image_attribution": "Wikimedia Commons",
        "body": """Scandinavian Airlines is back in India for the first time in 17 years, and while the headline is about Copenhagen and Mumbai, the more interesting angle for the American diaspora is what the new route plugs into on the other side of the Atlantic.

## A long-awaited return

SAS launched its Copenhagen-Mumbai service this month, operating five times a week with an Airbus A330-300. The flights — SK969 outbound, SK970 back — run on a roughly eight-and-a-half-hour block, and they mark the carrier's return to India after exiting in 2009. It is the first nonstop link between Copenhagen and Mumbai, complementing Air India's existing Delhi-Copenhagen flight, until now the only direct line between India and Scandinavia.

The relaunch was not entirely smooth. The inaugural attempt had to turn back to Copenhagen mid-flight after the airline did not receive final regulatory approval from Indian authorities while the aircraft was already en route over Azerbaijan. SAS said it completed all operational preparations and expected the remaining formal clearance within days — a reminder that even well-planned route launches can stumble on paperwork.

## The US connection hiding in the schedule

Here is where it gets relevant for NRIs in America. SAS did not design these flight times for Danes alone. The carrier explicitly built the Copenhagen-Mumbai timings to feed smooth transfers to and from its North American gateways — New York, Boston and Toronto get specific mention, and SAS serves a deep US map including Newark, Washington, Atlanta, Chicago, Seattle, Los Angeles and San Francisco.

In practice, that gives an East Coast traveller a fresh one-stop option to Mumbai: a transatlantic hop to Copenhagen, a short connection, and onward to India's financial capital — all within one airline's network, with through-checked bags and a single itinerary. For anyone who has spent the last few years watching Gulf hub connections wobble amid airspace disruptions, a stable Northern European routing is a welcome alternative to add to the comparison.

## Who should care

The natural audience is the Mumbai-rooted diaspora on the US East Coast and in the Midwest who would rather not route through the Gulf or through congested Western European mega-hubs. SAS joined SkyTeam in 2024, and its Copenhagen base is one of the more efficient transfer airports in Europe — compact, punctual, and far less of a maze than Heathrow or Frankfurt at peak. SAS has also been named among the world's most punctual carriers in recent months, which counts for something when a tight connection is involved.

There is a frequent-flyer wrinkle worth noting too: the route has been bookable on partner award charts, with redemption pricing published through Virgin Flying Club at the launch — economy from around 20,500 miles, premium economy at 37,500, and business at 60,000. For points-savvy travellers, that opens a non-obvious way to reach Mumbai.

## The practical advice

If Mumbai is your final destination and you are starting from the Northeast or a SAS-served US city, it is worth pricing the Copenhagen routing against the usual Gulf and Air India options for your summer or holiday travel. Compare the total journey time, the connection comfort at CPH, and the baggage terms. A 17-year absence has just ended, and with it, NRIs heading to Mumbai have one more — and notably calmer — way to get home."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
