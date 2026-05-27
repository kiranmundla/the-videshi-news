#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-27 06:00 UTC batch"""

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
        "headline": "Saudi Arabia's Budget Airline Just Picked Hyderabad as Its First Indian City — and a Million Gulf NRIs Stand to Benefit",
        "subheadline": "Flyadeal launches daily nonstop Riyadh-Hyderabad flights from July 1, marking the Saudia Group's low-cost push into India's busiest expat corridor.",
        "slug": make_slug("flyadeal-riyadh-hyderabad-daily-flights-nri-gulf"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Over a million Indians work in Saudi Arabia, with Hyderabadis forming one of the largest communities. Flyadeal's budget fares on the Riyadh-HYD route directly undercut full-service carriers that have long charged premium prices on this corridor, giving Gulf-based NRIs a cheaper way to visit family.",
        "tags": ["travel", "airlines", "saudi-arabia", "hyderabad", "gulf-nri", "flyadeal"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelObiz", "url": "https://travelobiz.com/flyadeal-daily-riyadh-hyderabad-flights-from-july-2026/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/0ltwi3nu8xcp/"},
            {"name": "Connecting Travel", "url": "https://connectingtravel.com/news/flyadeal-to-launch-flights-to-hyderabad-india"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1098745/pexels-photo-1098745.jpeg",
        "body": """Saudi Arabia's low-cost carrier flyadeal will begin daily nonstop service between Riyadh and Hyderabad on July 1, making it the airline's first scheduled route to India — and the latest signal that the Kingdom's aviation ambitions under Vision 2030 are accelerating faster than most NRIs realize.

## The Route

Flight F3 665 departs Riyadh at 11:20 PM and lands at Rajiv Gandhi International Airport at 6:50 AM the next morning. The return, F3 666, leaves Hyderabad at 7:55 AM and arrives back in Riyadh by 11:05 AM local time. The timing is deliberate: a red-eye out, a morning return, minimal workdays lost. For the hundreds of thousands of Hyderabadi expats scattered across Riyadh, Jeddah, and Dammam, the schedule is built around how they actually travel — quick trips home, often around festivals or family emergencies, where every hour of leave counts.

The aircraft is an Airbus A320neo in a 186-seat all-economy layout. No business class, no frills, no pretense. USB charging at every seat and Airbus's Airspace cabin interiors are the extent of the upgrades. What matters is the fare: flyadeal's model is aggressive discounting, and early bookings on the route are already listed well below what Air India Express and Saudia charge on the same corridor.

## Why Hyderabad First

Hyderabad was not a random pick. The city sits at the intersection of two powerful migration streams that flow into Saudi Arabia: technology workers and religious pilgrims. Hyderabad's IT corridor — home to Microsoft, Google, Amazon, and hundreds of Indian services firms — generates a steady churn of business travelers to the Gulf. Meanwhile, the city's deep Islamic heritage and large Muslim population make it one of India's biggest sources of Hajj and Umrah traffic.

Until now, flyadeal's India presence was limited to seasonal Hajj charters. This move puts it on the year-round schedule, competing directly with Saudia (its own parent company's full-service arm), Air India Express, IndiGo, and flynas on the India-Saudi corridor. The Saudia Group's strategy is transparent: use flyadeal to capture price-sensitive passengers while Saudia retains the premium market. It mirrors the Emirates-flydubai playbook that reshaped Gulf aviation a decade ago.

## What It Means for NRIs

The India-Saudi corridor is one of the most price-gouged in Asian aviation. Indian workers in the Gulf — many earning modest salaries in construction, retail, and services — have long paid disproportionately high fares relative to the route distance. A five-hour flight from Riyadh to Hyderabad often costs more than a transatlantic budget fare.

Flyadeal's entry injects genuine low-cost competition into a market that has been dominated by full-service carriers charging full-service prices. For the estimated 2.6 million Indians in Saudi Arabia — the single largest expatriate community in the Kingdom — even a 15-20% fare reduction on this corridor translates to meaningful savings, particularly for workers who fly home two or three times a year.

The airline has confirmed a second Indian city will be announced soon. Industry watchers expect either Mumbai or Kochi, both heavy Gulf-traffic generators. Tickets are already on sale through flyadeal's website, app, and travel agencies.

## The Bigger Picture

Saudi Arabia is spending billions to transform itself into a global transit hub. Riyadh's new King Salman International Airport, designed to handle 120 million passengers annually, is under construction. The Kingdom wants airlines — its own and others — to route through Saudi Arabia the way they currently route through Dubai or Doha. Flyadeal's India push is a piece of that puzzle: build volume on India routes, feed passengers into the Riyadh hub, and connect them onward to Africa and Europe.

For Hyderabadis in the Gulf, the strategic ambitions matter less than the practical reality: starting July 1, there is one more daily option to get home, and it will probably be the cheapest seat on the route."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's National Parks Now Charge Foreign Visitors $100 Extra — and NRIs on Work Visas Are Caught in the Middle",
        "subheadline": "The Trump administration's surcharge on non-U.S. residents at 11 marquee parks has already driven a 42% drop in international bookings. Here's what every H-1B holder, OCI cardholder, and green card applicant needs to know before planning a summer road trip.",
        "slug": make_slug("national-parks-100-surcharge-nri-h1b-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of Indian Americans on H-1B, L-1, and other work visas may technically be classified as non-U.S. residents under this policy. Green card holders are residents and likely exempt, but the verification process at park gates — showing a driver's license — creates ambiguity for anyone whose status falls between tourist and citizen.",
        "tags": ["travel", "national-parks", "h1b", "nri", "road-trip", "usa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Travel", "url": "https://www.thetravel.com/acadia-national-park-gateway-center-overshadowed-100-international-tourist-fee/"},
            {"name": "Marketplace (NPR)", "url": "https://www.marketplace.org/story/2026/01/16/international-visitors-to-pay-100-fee-for-some-national-parks"},
            {"name": "Visit Utah", "url": "https://www.visitutah.com/plan-your-trip/national-park-fee-changes"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/videos/4576662/national-parks-waive-entrance-fees-memorial-day/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6982828/pexels-photo-6982828.jpeg",
        "body": """If you are an Indian American on an H-1B visa and you drove your family to Yellowstone this Memorial Day weekend, you may have encountered a surprise at the gate: a $100-per-person surcharge for non-U.S. residents, on top of the standard $35 vehicle entrance fee. For a family of four, that is $400 extra before you have parked the car.

The policy, implemented on January 1, 2026, applies to 11 of America's most visited national parks. Five months in, it has already triggered a 42% drop in international bookings at some parks and sparked a lawsuit challenging its legality. For the roughly 4.5 million Indian-born residents of the United States — many on temporary work visas — the surcharge raises an uncomfortable question: does America consider you a resident or a visitor?

## The 11 Parks

The surcharge applies at Yellowstone, Yosemite, Grand Canyon, Zion, Bryce Canyon, Rocky Mountain, Glacier, Acadia, Grand Teton, Sequoia, and Arches. These are not obscure backcountry sites. They are the crown jewels of the National Park System, and for NRI families — particularly those in the West — they are the backbone of summer road trip planning.

The fee structure: U.S. residents pay the standard entrance fee ($15-$35 per vehicle depending on the park). Non-U.S. residents aged 16 and older pay the standard fee plus a $100 per-person surcharge. The America the Beautiful annual pass costs $80 for residents and $250 for non-residents; the non-resident pass covers the surcharge for the holder and all passengers in one vehicle.

## The Residency Question

Here is where it gets complicated for NRIs. The NPS verifies residency by checking a U.S. driver's license or state ID. If you have one, you are treated as a resident. If you do not, you pay the surcharge.

For most Indian Americans who have lived in the U.S. for years on H-1B or L-1 visas, a state driver's license is standard. In practice, showing your California or Texas license at the gate should exempt you from the surcharge. But the policy is designed around a blunt instrument — ID checks at park entrances — and the implementation has been uneven. Rangers at some parks have asked additional questions about citizenship status, creating confusion and delays.

Green card holders are unambiguously U.S. residents and are exempt. OCI cardholders visiting from India are not U.S. residents and will pay the surcharge. The gray zone sits with H-1B and L-1 holders who may not carry a U.S. driver's license — new arrivals, dependents on H-4 visas in states with restrictive licensing, or anyone whose license recently expired during a visa renewal.

## The Fallout

The surcharge has already dented park-adjacent economies. Lance Syrett, who manages Ruby's Inn outside Bryce Canyon, reported a 10-15% drop in international visitors and a 5% overall business decline. Intrepid Travel, a major adventure tour operator, reported 42% fewer bookings for U.S. national park itineraries. Some tour companies have absorbed the fee themselves rather than pass it to customers, eating into already thin margins.

Maine's governor, Janet Mills, was blunt at the opening of Acadia's new $30 million Gateway Center last week: "It is wrong to penalize people for coming from another nation. It does not make any sense. It is not going to raise any money because they just won't come."

Supporters point to the NPS's $22 billion maintenance backlog and early revenue numbers: Grand Teton alone has already collected $73,000 in extra revenue from non-resident passes and surcharges. A research estimate from the Property and Environment Research Center (PERC) projects the surcharge could generate $55 million annually across all 11 parks.

## The NRI Playbook

For Indian Americans planning summer road trips to any of the 11 parks, here is what to do:

**Carry your U.S. driver's license.** This is your primary proof of residency. A state ID works too. Do not rely on your passport alone — an Indian passport without a U.S. ID will trigger the surcharge.

**Consider the $250 non-resident annual pass** if you are visiting parents or relatives from India and plan to hit multiple parks. It covers the surcharge for the passholder and everyone in the vehicle, making it cost-effective for families visiting two or more parks.

**Know the fee-free days.** The NPS waives entrance fees on several holidays — Memorial Day, July 3-5, August 25 (NPS birthday), and others. However, in 2026, fee-free days apply only to U.S. citizens and residents. Non-residents still pay the surcharge even on fee-free days.

**Skip the Big 11 if you want to avoid the fee entirely.** The surcharge applies only to those 11 parks. America has 63 national parks and hundreds of national monuments, forests, and recreation areas with no surcharge. Crater Lake, Olympic, Shenandoah, Big Bend, and dozens of others remain surcharge-free and far less crowded.

The national parks surcharge is unlikely to go away soon — the administration has framed it as an "America First" revenue measure, and early collection numbers give it political cover. For NRIs with U.S. driver's licenses, the practical impact is minimal. For visiting family and friends from India, it is a $100-per-person tax on experiencing America's most iconic landscapes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Eleven Schengen Countries Just Brought Back Border Checks — and NRIs Planning a Europe Summer Trip Need to Adjust",
        "subheadline": "Germany, France, Italy, and eight other EU nations have reintroduced temporary passport controls at internal borders through late 2026. The free-flowing European road trip is no longer guaranteed.",
        "slug": make_slug("schengen-border-checks-europe-summer-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families frequently plan multi-country European vacations — Paris to Amsterdam by train, Rome to Switzerland by car. These internal border checks mean Indian passport holders may face additional scrutiny at crossings that were previously seamless, and must carry passports at all times even within the Schengen zone.",
        "tags": ["travel", "europe", "schengen", "visa", "nri", "border-checks"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TravelObiz", "url": "https://travelobiz.com/schengen-border-checks-list-european-countries-2026/"},
            {"name": "European Union Official Data", "url": "https://home-affairs.ec.europa.eu/policies/schengen-borders-and-visa/schengen-area/temporary-reintroduction-border-control_en"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29485309/pexels-photo-29485309.jpeg",
        "body": """The Schengen Area — Europe's passport-free travel zone spanning 29 countries — is supposed to let you drive from Paris to Berlin without stopping for a single document check. This summer, that promise has a large asterisk next to it. Eleven countries have reintroduced temporary border controls, citing terrorism threats, migration pressure, and geopolitical instability tied to the wars in Ukraine and the Middle East.

For NRI families planning the classic European summer holiday — a train from Paris to Amsterdam, a drive from Munich to the Italian lakes, a ferry across the Øresund from Denmark to Sweden — these controls mean checkpoints where there were none, queues where there was open road, and a passport that needs to be within arm's reach at every border crossing.

## Where the Checks Are

The eleven countries and their control periods:

**France** (May 1 – October 31): All land, air, and sea borders. Extra controls near Calais and Dunkirk. Security will tighten further during the G7 Summit in Evian in mid-June.

**Germany** (March 16 – September 15): Nearly all neighboring borders. This is the big one — Germany shares borders with nine countries, and checks affect both road and rail travel across Central Europe.

**The Netherlands** (June 9 – September 30): Land borders with Belgium and Germany, plus some intra-Schengen flights. If you are flying Amsterdam to Paris, expect ID checks.

**Italy** (December 19, 2025 – June 18): Controls at the Slovenian border, linked to migration routes and security for the Catholic Jubilee and the upcoming Winter Olympics.

**Sweden** (May 12 – November 11): Land, sea, and air borders, focused on Danish routes.

**Norway** (May 12 – November 11): Ferry ports connected to Schengen countries.

**Denmark** (May 12 – July 11): German border, citing terrorism and organized crime.

**Poland** (April 5 – October 1): Borders with Germany and Lithuania.

**Austria** (through June 15): Borders with Slovakia, Hungary, Slovenia, and Czech Republic.

**Slovenia** (through June 21): Croatian and Hungarian borders.

**Switzerland** (June 10 – 19): Lake Geneva region only, for the G7 Summit.

## What This Means for Indian Passport Holders

If you are an NRI traveling on an Indian passport with a valid Schengen visa, these controls do not change your legal right to move between countries. Your visa remains valid across the entire Schengen zone. But the practical experience changes significantly.

At temporary checkpoints, border police may ask to see your passport, your Schengen visa, proof of accommodation, and proof of onward travel. For Indian passport holders — who are already subject to more scrutiny at European borders than EU nationals or Americans — this adds another layer of friction. Random checks on trains between Germany and the Netherlands, or at highway crossings between France and Switzerland, are now routine.

The processing is generally quick — a few minutes at most — but during peak summer travel, those minutes compound. The Paris-Amsterdam Thalys, the Munich-Innsbruck Eurocity, the Copenhagen-Malmö Øresund trains: all are now subject to potential document inspections that can add 15-30 minutes to journey times.

## The NRI Summer Trip Playbook

**Carry your passport everywhere.** Not a photocopy, not a photo on your phone — the physical document. Even for a day trip from Strasbourg to Kehl, which is literally crossing a bridge from France to Germany, you may be asked for it.

**Print your documents.** Hotel confirmations, return flight itineraries, travel insurance. European border police tend to trust paper over screens, particularly at temporary checkpoints staffed by officers who may not have seen an Indian passport in months.

**Add buffer time to every cross-border leg.** The 3-hour Paris-to-Amsterdam train is still 3 hours of rail time, but plan for an extra 30 minutes of potential delay. For road trips, add 15-20 minutes at each border crossing. Multi-country itineraries that pack five cities into seven days were already aggressive — they are now fragile.

**Consider single-country depth over multi-country breadth.** A week exploring Provence, or a deep dive into the Italian lakes, sidesteps most of these controls entirely. The checks affect borders, not internal travel within a country.

**Watch the June 10-19 window carefully.** The G7 Summit in Evian means both France and Switzerland will have heightened security simultaneously around Lake Geneva. If your itinerary includes Geneva, Lausanne, or Annecy during this period, expect significant disruption.

## Why This Matters Beyond the Inconvenience

These temporary controls are a symptom of something larger: the slow erosion of Schengen's foundational promise. What started as emergency measures during the 2015 migration crisis have become semi-permanent fixtures, renewed every few months by governments that find political utility in visible border enforcement. For NRI travelers, who already navigate a world of visa applications, biometric enrollments, and immigration queues, it is one more reminder that the frictionless global travel experience marketed in airline advertisements rarely matches the reality of holding an Indian passport.

The practical advice is straightforward: prepare more, pack your patience, and keep your documents close. Europe is still worth the trip. It just takes a bit more planning than the brochure suggests."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
