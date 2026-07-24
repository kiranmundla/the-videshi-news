#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-10 06:00 UTC run"""

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


# ─── ARTICLE 1: Air India Easy Connect Hub-and-Spoke ───

art1_body = """Air India will begin flying passengers from Varanasi to 18 international destinations — London, Frankfurt, Singapore, Dubai, and 14 others — without making them endure the chaos of a Delhi transit. Starting June 25, the airline's new "Easy Connect" service will let travelers from India's spiritual capital check in their bags, clear immigration, and board a flight to Delhi where they'll walk straight to their international gate as transit passengers. No re-screening. No second check-in. No dragging suitcases across Terminal 3.

The first flight, AI1111, departs Varanasi daily at 9:50 AM and lands at Delhi's Indira Gandhi International Airport by 11:00 AM. From there, passengers connect within four hours to any of 18 long-haul destinations: London Heathrow, Frankfurt, Rome, Milan, Zurich, Vienna, Copenhagen, Manila, Singapore, Phuket, Kuala Lumpur, Riyadh, Bangkok, Dubai, Colombo, Ho Chi Minh City, and Kathmandu.

## Why This Changes the Game

For decades, international air travel in India has been a big-city privilege. If you lived in Lucknow, Varanasi, Patna, or Bhubaneswar and wanted to fly to London, you booked a domestic flight to Delhi or Mumbai, collected your bags, hauled them to the international terminal, stood in another immigration line, and hoped your connection held. The process turned a 9-hour London flight into a 16-hour ordeal.

Air India's hub-and-spoke model eliminates the worst of it. Passengers complete all immigration and customs formalities at the spoke airport — Varanasi, for now — and transit through Delhi as if they were connecting at any global hub. The concept is standard at Heathrow, Changi, and Dubai. In India, it's a first.

The airline has flagged future spoke cities under the AI11XX flight series, though it hasn't named them yet. Aviation analysts expect Lucknow, Jaipur, Ahmedabad, and Amritsar — cities with large outbound diaspora populations — to be early additions.

## What NRIs Should Know

This matters enormously for the estimated 4.5 million Indian Americans whose families still live in Tier-2 and Tier-3 cities. Until now, picking up aging parents or grandparents from smaller cities for a visit abroad meant either driving them to Delhi or booking a separate domestic flight and coaching them through a complicated terminal transfer.

Under Easy Connect, a parent in Varanasi flying to visit family in London or Singapore checks one bag, clears one immigration counter, and lands at their destination without ever navigating Delhi's sprawling terminals alone. For families sending unaccompanied elderly travelers, the reduction in friction is significant.

The timing is deliberate. India's government released the standard operating procedures for hub-and-spoke operations earlier this year, covering passenger processing, baggage handling, and immigration at spoke airports. Air India, now firmly under Tata Group management, moved fast to operationalize the framework.

## The Bigger Picture

This isn't just an Air India story. IndiGo, which operates more than 2,700 daily flights to 137 destinations, has been expanding internationally at pace — adding Manchester, Amsterdam, Istanbul, and London to its network in 2025-26. If the hub-and-spoke model proves operationally sound at Varanasi, pressure will mount on IndiGo and other carriers to adopt it at their own hub airports.

For NRIs, the bottom line is straightforward: flying your family internationally from smaller Indian cities is about to get dramatically easier. If your parents live in Varanasi, June 25 is worth circling on the calendar."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Just Made It Possible to Fly International From Varanasi — and Dozens of Indian Cities Could Be Next",
    "subheadline": "The airline's new 'Easy Connect' hub-and-spoke model lets passengers from Tier-2 cities clear immigration locally and transit through Delhi to 18 global destinations. NRIs with family in smaller cities should pay attention.",
    "slug": make_slug("air-india-easy-connect-varanasi-hub-spoke-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs with family in Tier-2 and Tier-3 Indian cities have long struggled with the logistical nightmare of getting elderly parents or relatives to international flights. Air India's Easy Connect model eliminates terminal transfers and double immigration at Delhi, making it dramatically easier for families in places like Varanasi to fly abroad.",
    "tags": ["travel", "airlines", "air-india", "hub-and-spoke", "varanasi", "nri-families"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-launch-hub-and-spoke-international-connectivity-flights-from-june-25/article71081684.ece"},
        {"name": "IndiGo International Network (Wego)", "url": "https://blog.wego.com/indigo-international-flights/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
    "image_caption": "An Air India Boeing 777 on the tarmac at JFK Airport",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ─── ARTICLE 2: Ebola Screening at Indian Airports ───

art2_body = """If you're flying to India this summer, expect a new piece of paperwork at 35,000 feet. India's aviation regulator has ordered airlines to collect mandatory Self-Declaration Forms from all passengers arriving from or transiting through Uganda and the Democratic Republic of Congo — and given that most NRIs fly through Gulf hubs like Dubai, Doha, and Abu Dhabi, the ripple effects reach far beyond Africa.

The Directorate General of Civil Aviation issued the detailed standard operating procedure on May 22, after the World Health Organization declared the Ebola outbreak in Congo and Uganda a Public Health Emergency of International Concern on May 17. India's government has separately advised citizens to avoid all non-essential travel to Congo, Uganda, and South Sudan.

## What Changes on Your Flight

Airlines serving routes connected to the affected countries — Air India, IndiGo, Emirates, Qatar Airways, Ethiopian Airlines, Kenya Airways, Turkish Airlines, Etihad, Akasa Air, EgyptAir, Flydubai, and KLM among them — must now follow a strict in-flight protocol:

- **Health announcements** during the flight asking passengers to self-report symptoms including fever, weakness, muscle pain, headache, vomiting, diarrhea, rash, or bleeding
- **Self-Declaration Forms** collected from all passengers before de-boarding in India
- **On-board isolation**: symptomatic passengers relocated to the rear of the aircraft with three surrounding rows kept vacant
- **PPE, masks, gloves, and biohazard bags** stocked on all affected flights
- **Aircraft disinfection** after every landing
- **Isolated parking bays** for planes carrying suspected cases, coordinated with air traffic control

The protocol primarily targets passengers originating from or transiting through Uganda and Congo. But for NRIs routing through Dubai, Doha, Abu Dhabi, Istanbul, Nairobi, or Addis Ababa — which describes the majority of India-bound flights from the Americas — the screening net is wide. Delhi, Mumbai, Bengaluru, Hyderabad, and Chennai airports are the most likely to see these checks first.

## What the US Is Doing

The screening isn't one-sided. The US Centers for Disease Control and Prevention last month barred non-citizens who have been in Congo, Uganda, or South Sudan within the previous 21 days from entering the United States. American citizens returning from those countries are being rerouted to Washington Dulles International Airport for mandatory enhanced screening.

On June 1, the Trump administration issued a formal diplomatic demarche urging European nations to impose similar travel restrictions, explicitly citing the FIFA World Cup — which kicks off this week across the US, Canada, and Mexico — as a vector for potential spread. European nations have not yet responded.

## Why NRIs Should Care

For the vast majority of Indian Americans, none of this means canceling summer travel plans. The risk to travelers on standard US-India routes is low. But there are practical implications worth noting:

**If you transit through a Gulf hub**, your airline may distribute a Self-Declaration Form during the flight. Fill it out honestly. The form asks about travel history and symptoms — refusing or providing false information can trigger additional screening at the Indian airport.

**If you have business in East Africa**, the 21-day window is critical. Under current US rules, if you visit Uganda or Congo and return to the US within 21 days, you'll be rerouted to Dulles regardless of your booked itinerary. Indian passport holders face the additional constraint of India's non-essential travel advisory.

**If you develop symptoms within 21 days of arriving in India** from an affected region, the DGCA directive asks you to seek immediate medical attention and inform airport health authorities.

Andhra Pradesh has already deployed screening teams at Gannavaram Airport, checking all international arrivals from Singapore three times a week and conducting special screenings for returning Hajj pilgrims. No Ebola-related symptoms have been detected among any screened passengers so far.

## The Bottom Line

This isn't 2020. There are no quarantine requirements, no travel bans on India routes, and no PCR tests at immigration. The DGCA's new protocols are precautionary, targeted, and — for most NRIs — will add no more than a few minutes of paperwork to an already long journey. But knowing the rules before you board is better than learning them at 35,000 feet."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Airports Just Got Ebola Screening Protocols — Here's What NRIs Flying Home This Summer Need to Know",
    "subheadline": "The DGCA has ordered airlines to collect health declaration forms and isolate symptomatic passengers on India-bound flights. Meanwhile, the US is barring travelers from Congo and Uganda and pushing Europe to follow suit ahead of the World Cup.",
    "slug": make_slug("india-ebola-airport-screening-dgca-nri-summer-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most NRIs fly to India through Gulf hubs like Dubai and Doha, which also serve as transit points for passengers from East Africa. The new DGCA screening protocols — including mandatory health forms, in-flight isolation procedures, and aircraft disinfection — will directly affect the travel experience of Indian Americans heading home this summer.",
    "tags": ["travel", "ebola", "dgca", "airports", "health-screening", "nri-travel-advisory"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "travelobiz", "url": "https://travelobiz.com/dgca-orders-airlines-to-screen-passengers-amid-ebola-outbreak-alert/"},
        {"name": "Times of India (via Currato)", "url": "https://currato.com/dgca-issues-ebola-preparedness-sop-for-airlines-operating-flights-linked-to-uganda-congo-india-news/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us-urges-europe-impose-ebola-travel-bans-ahead-world-cup-2026-06-09/"},
        {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/en/india/ebola-alert-prompts-andhra-pradesh-to-strengthen-airport-screening"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5955444/pexels-photo-5955444.jpeg",
    "image_caption": "A health worker conducting thermal screening at an airport checkpoint",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ─── ARTICLE 3: IEA Emergency Oil Release and NRI Flight Costs ───

art3_body = """Brent crude closed at $91.46 a barrel on Monday. Three months ago, when Iran and Israel's escalating strikes briefly shut the Strait of Hormuz, it was $114. The International Energy Agency responded with the largest emergency oil release in its history — 400 million barrels from the strategic reserves of 32 member nations — and prices have since retreated. But "retreated" is relative. At $91, oil is still expensive enough to keep airline fuel bills elevated, and the summer peak travel season is about to make it worse.

For the roughly 4.5 million Indian Americans who fly to India at least once a year, the math is uncomfortable. Jet fuel accounts for 30 to 35 percent of an airline's operating costs. When oil prices climb, airlines have two choices: absorb the hit or pass it to passengers through fuel surcharges and higher base fares. In 2026, they are choosing the latter.

## What Happened With Oil

The Iran-Israel conflict, which escalated significantly in early 2026, has been the primary driver. When Iranian forces targeted Israeli positions in March and Israel responded with strikes on Iranian oil infrastructure near the Strait of Hormuz — through which roughly 20 percent of the world's oil flows — Brent crude spiked above $114 a barrel. Tanker insurance rates surged, shipping routes were diverted, and India, which imports more than 85 percent of its crude oil, found itself scrambling to secure alternative supplies.

The IEA's 400-million-barrel release — announced with unusual urgency and described by Executive Director Fatih Birol as "unprecedented in scale" — helped stabilize markets. Member nations hold over 1.2 billion barrels in emergency stockpiles, with another 600 million in industry reserves. The release has pushed Brent back below $92, but analysts warn that any renewed escalation could send prices climbing again.

## How This Hits NRI Ticket Prices

The connection between crude oil and your SFO-DEL ticket isn't abstract. Airlines price jet fuel based on the Singapore Kerosene benchmark, which tracks closely with Brent. When Brent was below $70 in late 2024, round-trip economy fares on the San Francisco–Delhi route averaged roughly $900 to $1,100. With Brent above $90 for most of 2026, those same fares now regularly clear $1,400 to $1,800 for summer dates.

Business class is worse. Air India's nonstop Newark-Delhi, a favorite of East Coast NRIs, has seen business class fares climb above $6,000 round-trip — up from $4,500 a year ago. United's SFO-DEL nonstop isn't far behind.

The problem compounds during summer, when NRI demand for India flights peaks. Airlines know that July and August are high-yield months — families visiting during school breaks, festival preparations for Diwali and Navratri, and elderly parents flying for medical appointments all converge. Capacity cuts by carriers like IndiGo, which suspended six Asian routes this summer citing cost pressures, further tighten available seats on India routes.

## What NRIs Can Do

**Book early.** Fares on India routes typically bottom out 8 to 12 weeks before departure. If you're planning a September or October trip — when monsoon season ends and Diwali approaches — booking now locks in current prices before any further oil shocks.

**Watch the shoulder season.** Late September and early October sit between the summer rush and the Diwali surge. Fares often dip 15 to 25 percent during this window.

**Consider alternative routing.** Gulf carriers like Emirates and Qatar Airways, despite the Gulf region's proximity to the conflict zone, have been aggressively discounting to win back passengers worried about airspace disruptions. A Dubai or Doha stopover adds a few hours but can shave $200 to $400 off the fare.

**Track the IEA.** The 400-million-barrel release isn't permanent. If the release winds down without a ceasefire or production increase, oil prices could climb again, dragging fares up with them. The IEA has not yet set a timeline for how long the release will continue.

## The Bottom Line

Oil at $91 isn't a crisis, but it's not comfortable either. For NRIs who fly to India regularly, the era of sub-$1,000 economy fares appears to be on hold for the foreseeable future. The IEA's intervention bought time. Whether it bought enough depends on what happens next in the Strait of Hormuz."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The World Just Released 400 Million Barrels of Emergency Oil — and Your Flight to India Is Still Getting More Expensive",
    "subheadline": "Brent crude has retreated from $114 to $91 after the largest-ever IEA reserve release, but jet fuel costs remain elevated. Here's what that means for NRIs booking summer flights on the SFO-DEL and JFK-BOM routes.",
    "slug": make_slug("iea-oil-release-nri-india-flight-prices-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian Americans who fly to India at least once a year are seeing summer airfares climb $300 to $700 above 2024 levels as elevated oil prices push airlines to raise fuel surcharges. The IEA's 400-million-barrel emergency release has stabilized prices but not lowered them enough to bring relief on key diaspora routes like SFO-DEL, JFK-BOM, and EWR-DEL.",
    "tags": ["travel", "oil-prices", "airfares", "iea", "nri-flights", "fuel-costs"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TECHi Oil Price Data", "url": "https://techi.com/oil-price-today/"},
        {"name": "IEA Emergency Release (via ActiveBrainly)", "url": "https://activebrainly.netlify.app/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/iran-israel-strikes-oil-prices-airfares-airlines/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33914643/pexels-photo-33914643.jpeg",
    "image_caption": "An aircraft being refueled on the tarmac at a commercial airport",
    "image_attribution": "Pexels",
    "body": art3_body,
}


# ─── INSERT ───

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
