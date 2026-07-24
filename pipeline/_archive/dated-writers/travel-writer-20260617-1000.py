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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Quietly Making Its Tourist Visa a Year-Long, Multi-Entry Pass — A Win for OCI Families' Friends and Guests",
        "subheadline": "New e-Tourist Visa rules stretch validity to a full year with unlimited entries, and the e-Business visa now allows 180-day stays — a practical upgrade for anyone the diaspora invites to India.",
        "slug": make_slug("india-etourist-visa-one-year-multiple-entry-relaxation-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Most NRIs already hold an OCI card and skip visas entirely, but the friends, in-laws, and foreign-citizen spouses they invite to India do not — and the new year-long, multi-entry e-Tourist Visa makes repeat family visits far cheaper and less bureaucratic.",
        "tags": ["travel", "visa", "india", "e-visa", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — Electronic Visa Rules to be Relaxed", "url": "https://www.fragomen.com/insights/electronic-visa-rules-for-tourists-and-business-visitors-to-be-relaxed.html"},
            {"name": "Wego Travel — India e-Tourist Visa 2026", "url": "https://blog.wego.com/india-e-tourist-visa/"},
            {"name": "Fragomen — E-Visa Program to be Expanded", "url": "https://www.fragomen.com/insights/e-visa-program-to-be-expanded.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11948442/pexels-photo-11948442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Taj Mahal in Agra, India's most-visited landmark for inbound tourists",
        "image_attribution": "Pexels",
        "body": """India is rewriting the rulebook for who can come visit — and how often. The Ministry of Tourism and the Ministry of Home Affairs have released a set of relaxed guidelines for the country's electronic visa program, the most consequential of which stretches the e-Tourist Visa to a full year of validity with multiple entries, up from a 60-day window that allowed just two visits.

The changes have not yet gone live in the application portal, and the government has not given a firm switch-on date. But the direction is unambiguous: India wants more foreign visitors, and it is removing the friction that has long made repeat trips a paperwork chore.

## What Actually Changed

Under the relaxed framework, the e-Tourist Visa will be granted for up to one year and permit multiple entries — a sharp upgrade from the current short-window, double-entry structure. Travelers still cannot exceed their per-visit consecutive-stay limit: 180 days for U.S., U.K., Japanese, and Canadian nationals, and 90 days for most other eligible nationalities.

The e-Business Visa is getting a parallel loosening. Its consecutive-stay period jumps to 180 days, and it can now be used multiple times in a calendar year rather than the previous cap of three. For someone flying in for technical reviews, board meetings, or vendor visits, that erases a recurring scramble for fresh paperwork.

Both visas remain fast to obtain — processed within 24 to 72 hours, with applications accepted online at least four days before travel.

## Why This Matters to the Diaspora

Here is the nuance most coverage misses. The typical Indian American does not use any of this. If you hold an Overseas Citizen of India card, you walk into India visa-free for life. The people this change actually serves are the ones orbiting the diaspora: the American-citizen spouse, the foreign-born grandchildren traveling on a U.S. passport, the college roommate who wants to tag along for a Goa wedding, the in-laws from a non-Indian background.

For those travelers, the old 60-day, two-entry visa was a genuine constraint. A family that visits India over Christmas and again for a summer wedding previously needed two separate visa applications, each with its own fee. A year-long multi-entry permit collapses that into one. For mixed-status families who shuttle between continents, the savings in time, money, and consular anxiety are real.

The e-Business expansion lands squarely on the diaspora's professional class. Bay Area and tri-state tech workers who run India delivery centers, founders raising from Indian funds, and consultants on rolling engagements can now structure a year of travel around a single visa rather than reapplying every quarter.

## The Bigger Picture

This is not a one-off. New Delhi has been steadily digitizing and widening its visa machinery — expanding the list of ports of entry under the e-visa scheme and adding new subcategories, including an E-Conference Visa for government-sponsored events and an E-Medical Attendant Visa for those accompanying patients on medical trips. The government has also signaled it will open e-visa eligibility to nationals of additional countries, though the updated list has not been published.

The throughline is a country trying to make itself easier to reach as inbound tourism and medical travel climb. For a diaspora that constantly brokers visits between its adopted home and its ancestral one, fewer forms and longer validity is exactly the kind of quiet, practical win that adds up.

## What to Do Now

If you have guests or relatives planning India trips on foreign passports, hold off on locking in a short-validity visa if the timeline allows — the year-long version could deliver far better value once the portal updates. Watch the official Indian Visa Online portal for the rollout, and remember that OCI holders never needed any of this in the first place. The smart move is to make sure the people you travel with know the rules are about to get friendlier."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Vande Bharat Sleeper Is Finally Rolling Out — Overnight Trains Are About to Feel Like Flying",
        "subheadline": "The long-promised sleeper version of India's flagship semi-high-speed train is launching its prototype this month, with 120 trainsets planned by 2032 to replace the aging Rajdhani and Duronto fleet.",
        "slug": make_slug("vande-bharat-sleeper-prototype-launch-overnight-train-nri"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "NRIs who return to India for weeks each year and dread the cramped, hours-long overnight Rajdhani journeys between family cities will soon have a modern, airline-grade alternative — quiet, fast, and bookable from abroad.",
        "tags": ["travel", "india", "railways", "vande-bharat", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Metro Rail Today — RVNL targets June 2026 Vande Bharat Sleeper launch", "url": "https://www.metrorailtoday.com/news"},
            {"name": "Travel + Leisure Asia — Mumbai-Bengaluru Vande Bharat Sleeper Approved", "url": "https://www.travelandleisureasia.com/in/news/mumbai-bengaluru-vande-bharat-sleeper-train/"},
            {"name": "Metro Rail Today — ICF to roll out 24-coach Vande Bharat Sleeper", "url": "https://www.metrorailtoday.com/news"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Howrah%E2%80%93Puri_Vande_Bharat_Express_at_Balasore_railway_station_1.jpg/1280px-Howrah%E2%80%93Puri_Vande_Bharat_Express_at_Balasore_railway_station_1.jpg",
        "image_caption": "A Vande Bharat Express trainset at Balasore railway station; the sleeper variant is now entering service",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the Vande Bharat Express has been India's showpiece train — sleek, fast, and built entirely at home — but it had one glaring limitation: no beds. Confined to daytime, chair-car runs, it could not touch the overnight market dominated by the decades-old Rajdhani and Duronto expresses. That is about to change.

Rail Vikas Nigam Limited has confirmed that the first prototype of the Vande Bharat Sleeper train is set to launch this month, the opening move in an ambitious plan to deliver 120 sleeper trainsets by 2032. India's first AC sleeper semi-high-speed service, the Howrah–Kamakhya Vande Bharat Sleeper, was inaugurated in January, and a steady pipeline of new routes is now lining up behind it.

## What the Sleeper Offers

These are not your parents' overnight coaches. The sleeper variant is engineered for journeys at up to 160 kmph, with berths spread across AC First Class, AC 2-Tier, and AC 3-Tier. Each coach comes with automatic doors, CCTV, bio-vacuum toilets, sensor-based taps, reading lights, individual power outlets, ergonomic berths, modern lighting, and serious noise insulation.

The Integral Coach Factory in Chennai is preparing to roll out the country's first 24-coach Vande Bharat Sleeper by the end of 2026 — a configuration explicitly designed to phase out premium long-haul trains like the Rajdhani and Duronto. Manufacturing is being handled under the "Make in India" banner, with RVNL's joint venture Kinet Railway Solutions overseeing design and production.

## The Routes Taking Shape

Several corridors are already approved or in planning. A Mumbai CSMT–Bengaluru KSR sleeper is expected to begin operations around mid-2026, cutting the trip well below the 18-to-19 hours that existing trains like the Udyan and Coimbatore Expresses take. A Delhi–Amritsar sleeper linking Chandigarh, Ludhiana, and Jalandhar is slated for the 2026 winter season. The broader plan calls for a dozen sleeper services with six rakes on each side rolling out through the end of the year.

## Why It Matters to the Diaspora

Here is the diaspora reality. NRIs who fly home for two or three weeks a year are time-rich on arrival but constantly criss-crossing the country — Bengaluru to see one set of parents, Mumbai for in-laws, Delhi for a cousin's wedding. Domestic flights are quick but pricey at peak season and dump you at congested metro airports. The old overnight trains are cheap but cramped, noisy, and slow.

A modern, quiet, airline-grade sleeper changes that calculus. An overnight Mumbai–Bengaluru run that gets you a real night's sleep and deposits you downtown at breakfast is exactly the kind of civilized travel returning families have been missing. For grandparents traveling with young grandchildren born abroad, the upgrade in comfort and hygiene — bio-vacuum toilets, sealed automatic doors, climate control throughout — is not a luxury, it is the difference between a trip they will repeat and one they will not.

Crucially, Vande Bharat tickets are bookable online through IRCTC from anywhere in the world, so diaspora travelers can lock in berths before they even land.

## The Catch

Timelines on Indian rail projects move. The 2032 full-rollout target is aggressive, and prototype testing, safety approvals, and supply-chain readiness all stand between the first trainset and a nationwide network. Early services will cluster on marquee corridors before reaching second-tier routes.

Still, the direction is set. The train that became a symbol of new India is finally getting beds — and for a diaspora that measures its trips home in overnight journeys between loved ones, that is news worth tracking."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Gulf Is Reopening Its Skies — and the Flight Home to India May Finally Get Cheaper",
        "subheadline": "A US-Iran framework set to be signed in Switzerland this week would reopen the Strait of Hormuz and Middle East air corridors, easing the fuel costs and reroutes that have inflated NRI fares for months.",
        "slug": make_slug("gulf-airspace-reopening-us-iran-deal-cheaper-india-fares-nri"),
        "category": "travel",
        "vertical": "geopolitics",
        "diaspora_angle": "The vast majority of NRIs fly home through Dubai, Doha, or Abu Dhabi, and the Gulf conflict that closed corridors and spiked jet fuel has been a hidden tax on every ticket — a signed peace framework could finally bring fares and reliable layovers back.",
        "tags": ["travel", "airlines", "india", "airfares", "middle-east"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — US and Iran sign ceasefire agreement", "url": "https://www.reuters.com/world/middle-east/us-iran-sign-ceasefire-agreement-2026/"},
            {"name": "Reuters — Major Gulf markets mixed as investors assess US-Iran peace deal", "url": "https://www.reuters.com/markets/gulf-markets-us-iran-peace-deal-2026/"},
            {"name": "Travel And Tour World — Middle East Airspace Reopening, Fare Crash Expectations", "url": "https://www.travelandtourworld.com/news/article/uae-qatar-saudi-arabia-peace-deal-airspace-reopening/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A digital flight information board displaying international departures",
        "image_attribution": "Pexels",
        "body": """For months, the cheapest, most familiar way for the Indian diaspora to get home — a one-stop hop through a Gulf megahub — has been quietly broken. The conflict that began when the U.S. and Israel struck Iran in February shut the Strait of Hormuz, closed swaths of Middle Eastern airspace, and sent jet fuel costs soaring as airlines flew long, expensive detours around active combat zones. Every one of those costs landed, eventually, on the ticket prices NRIs pay.

That may be about to ease. A U.S.-Iran framework, which President Trump said has been signed and which is due for a formal ceremony in Switzerland on Friday, would extend a fragile April ceasefire by 60 days and — critically for travelers — reopen the Strait of Hormuz and lift the U.S. naval blockade. Oil prices fell to their lowest level since March on the news, with Brent crude sliding toward the high $70s and West Texas Intermediate dropping toward $80 a barrel.

## Why Gulf Skies Decide NRI Fares

Most Indian Americans do not fly nonstop. They connect — through Dubai on Emirates, Doha on Qatar Airways, Abu Dhabi on Etihad. Those three carriers alone handle a massive share of long-haul one-stop traffic between continents, and their hubs are the diaspora's default gateway to Kochi, Hyderabad, Ahmedabad, and dozens of cities Air India does not serve nonstop from the U.S.

When Gulf airspace is constrained, three things happen at once. Flights reroute around closed corridors, adding hours and burning more fuel. Jet fuel itself gets pricier as oil markets price in the risk. And schedules wobble, raising the odds that the layover you booked turns into a missed connection. The result has been higher fares, longer journeys, and shakier reliability on precisely the routes the diaspora leans on most.

## What Reopening Could Unlock

If the framework holds, analysts expect a gradual return to normal at Dubai, Doha, and Abu Dhabi — the connecting backbone for travel between Europe, Asia, Africa, and Australia. Travel-industry observers are openly discussing fare relief and a recovery boom as corridors reopen and carriers retire their costly detours. Airline and travel stocks rallied on the prospect, a market vote of confidence that cheaper fuel and stabler operations are coming.

For diaspora travelers, the practical upside is threefold: lower fuel surcharges feeding into ticket prices, shorter and more direct routings that shave hours off the journey, and more dependable layovers that make tight Gulf connections feel less like a gamble.

## The Caveats Are Real

This is a framework, not a finished peace. Vice President Vance described the signed memorandum as roughly a page and a half and "a very general document," and Iran's president called it an important step while cautioning that a lasting truce "has yet to take shape." The blockade and Strait are slated to reopen within 30 days "under Iranian arrangements" — a phrase doing a lot of work. Gulf markets traded mixed rather than euphoric, signaling that investors, too, are waiting to see the details.

Fares also do not fall overnight. Airlines hedge fuel months ahead, and peak summer pricing is already baked in. The realistic window for relief is the back half of 2026, not next week.

## The Bottom Line

If you are booking a fall or winter trip home and your dates are flexible, it may pay to wait a beat before locking in a Gulf-routed fare — the pricing landscape could look meaningfully better once the deal is signed and corridors reopen. For a diaspora that has absorbed an invisible conflict premium on every flight home this year, a calmer Gulf is the most consequential travel story on the board."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
