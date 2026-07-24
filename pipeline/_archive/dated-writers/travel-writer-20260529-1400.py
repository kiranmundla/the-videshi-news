#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-29 14:00 UTC run. Publishes 2 fresh travel articles."""

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
        "headline": "India's Summer Flight Crunch Just Got Real — and NRIs With Homebound Trips Should Act Now",
        "subheadline": "Air India and IndiGo are slashing domestic capacity by up to 22 percent from June through August, threatening fare spikes on the very routes NRIs depend on to reach their hometowns.",
        "slug": make_slug("india-domestic-flight-cuts-nri-summer-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India this summer face dramatically fewer domestic flight options and spiking fares on the connecting routes that get them from international gateways to their hometowns — Delhi-Hyderabad, Mumbai-Ahmedabad, Delhi-Bengaluru and more.",
        "tags": ["travel", "airlines", "air india", "indigo", "domestic flights", "fares", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indigo-air-india-cut-june-july-domestic-flights-amid-high-jet-fuel-prices-sources-2026-05-27/"},
            {"name": "Hindustan Herald", "url": "https://hindustanherald.in/shocking-domestic-flight-cuts-fares-spiking-june-2026/"},
            {"name": "Live From A Lounge", "url": "https://livefromalounge.com/indian-carriers-prepare-for-13-domestic-flight-cuts/"},
            {"name": "Nation Press", "url": "https://nationpress.com/indigo-slash-domestic-capacity-june-august-2026/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17259764/pexels-photo-17259764.jpeg",
        "image_caption": "Indian airport terminal — domestic flight options are shrinking sharply this summer",
        "body": """The two airlines that carry nine out of every ten domestic passengers in India are simultaneously pulling back this summer. Air India is cutting up to 22 percent of its domestic flights between June and August. IndiGo, the country's largest carrier, is trimming 7 to 10 percent. Together, that amounts to well over a thousand fewer weekly flights across India's busiest corridors.

For the roughly 4.5 million Indian Americans who fly home each year, the headline number is troubling enough. But the real pain lies in the details: the routes being cut are precisely the ones NRIs use most when visiting family.

## The Routes Getting Hit

The cuts are concentrated, not random. Out of Mumbai, flights to Ahmedabad, Nagpur, Patna, and Bhopal are losing frequency. Out of Delhi, services to Hyderabad, Bengaluru, and Kolkata are being reduced. Return legs on several southern routes are being axed too.

No route is being dropped entirely — the airlines are reducing how often they fly, not whether they fly at all. Cold comfort if the remaining frequency doesn't align with when you need to travel.

Air India operates about 3,600 domestic flights per week. A 22 percent reduction means roughly 790 fewer weekly services. The airline called it a "temporary rationalisation" driven by "the sustained impact of high fuel prices on overall operations."

IndiGo's cuts are smaller in percentage terms but significant given the airline's scale. With over 2,200 daily flights, even a 7 percent reduction removes hundreds of departures from the system each week. The airline has attributed its pullback partly to softer post-summer demand, though the 17 percent cut to its international capacity suggests fuel costs are driving the math.

## Why This Is Happening

The root cause is the same crisis rippling through global aviation since March: the Iran conflict. Brent crude has surged more than 50 percent in three months as tensions around the Strait of Hormuz show no sign of easing. Aviation turbine fuel now accounts for nearly 40 percent of Indian airlines' operating costs, up from the mid-20s in more stable years.

Air India, still carrying the weight of a record $2.4 billion annual loss, has taken the deepest cuts. It has already suspended several international routes — Delhi-Chicago, Delhi-Newark, Mumbai-New York — from June through August. The domestic reductions follow the same logic: stop flying routes that bleed money at current fuel prices.

## What NRIs Will Actually Feel

If you've booked flights to India this summer but haven't locked in domestic connections, you're exposed. Dynamic pricing will compound the capacity crunch. The cheapest fare buckets on any flight sell first, typically 40 to 45 days before departure. By the time most NRIs search for domestic connections — usually two to three weeks out, after confirming their international itinerary — those seats are gone. Remaining fares can spike 40 to 200 percent.

## Four Things to Do Right Now

**Book domestic legs immediately**, even before your international flights are finalized. Most Indian carriers allow free date changes for advance bookings.

**Consider Akasa Air**, which has been adding routes while the giants retreat. Its network is still limited, but it covers several key corridors at competitive fares.

**Look at trains.** India's Vande Bharat network now covers over 40 routes, and new sleeper variants on trunk routes like Mumbai-Bengaluru offer overnight connections that bypass the airport chaos entirely.

**Check Tier-2 direct flights.** The government's UDAN scheme has opened dozens of regional routes that didn't exist five years ago. If your hometown is near a smaller airport, you may find a direct option from Delhi or Mumbai that avoids the crowded main corridors.

Air India says it will "monitor demand and operating conditions closely, with a view to restoring frequencies as conditions stabilise." But with oil prices showing no sign of retreat and the Iran situation unresolved, that stabilisation could be months away. Plan accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Fuel Crisis That Rewrote Every NRI Airfare — and When Relief Might Come",
        "subheadline": "Brent crude is up 50 percent since March, the Strait of Hormuz remains a flashpoint, and Indian airlines are hemorrhaging cash. Here is what it means for every diaspora traveler booking a trip home.",
        "slug": make_slug("nri-airfare-fuel-crisis-iran-oil-prices-relief"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs are paying 30-50% more for India-bound flights due to the Iran conflict's cascading effects on oil prices, Gulf transit hubs, and airline capacity — with direct routes like Delhi-Chicago and Mumbai-New York suspended entirely.",
        "tags": ["travel", "airlines", "fuel prices", "iran", "oil", "airfares", "nri", "gulf"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/airline-shares-selloff-eases-some-flights-leave-gulf-amid-iran-conflict-2026-03-04/"},
            {"name": "The News (Pakistan)", "url": "https://www.thenews.pk/latest/thousands-stranded-as-iran-conflict-shuts-mideast-hubs"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/ceasefire-risks-disrupt-aviation-tourism/"},
            {"name": "Live From A Lounge", "url": "https://livefromalounge.com/indian-carriers-prepare-for-13-domestic-flight-cuts/"},
            {"name": "Hindustan Herald", "url": "https://hindustanherald.in/shocking-domestic-flight-cuts-fares-spiking-june-2026/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/1678617/pexels-photo-1678617.jpeg",
        "image_caption": "Airfares to India have climbed sharply as oil prices and geopolitical disruptions squeeze airlines",
        "body": """If your flight to India this summer costs 30 to 50 percent more than it did a year ago, you are not imagining things. The explanation runs deeper than seasonal demand or airline pricing tactics. Three separate crises have collided to produce the most expensive NRI travel season in recent memory.

## The Chain Reaction

When the United States and Israel launched strikes against Iran in early March, the immediate impact was felt at the world's busiest airports. Dubai International — the single most important transit hub for NRI traffic to India — shut down for five days. Doha and Abu Dhabi followed. For roughly a week, the three Gulf hubs that together handle nearly 300,000 passengers daily went dark.

Emirates, which operates 22 daily flights to India alone, crawled back to 60 percent of its network. Some routes still have not fully recovered three months later. The disruption stranded tens of thousands of passengers worldwide, with repatriation flights organized by multiple governments.

But the airport closures were only the first shock. The deeper damage came from oil markets. Brent crude has surged more than 50 percent since March, driven by fears of prolonged supply disruptions around the Strait of Hormuz — the narrow waterway through which roughly 20 percent of the world's crude supply passes. Aviation turbine fuel, which India imports heavily, has followed crude upward. For Indian carriers, fuel now consumes nearly 40 percent of operating costs, up from the mid-20s a year ago.

## The Pakistan Factor

Layer on a second complication that predates the Iran war: Pakistan's continued ban on Indian carriers using its airspace. For westbound flights from India to Europe and the United States, this forces planes onto longer southern routing over the Arabian Sea — adding 60 to 90 minutes of flight time and burning thousands of dollars in extra fuel per departure.

Air India's Delhi-London service, for instance, now swings south and loops through the Middle East corridor, adding an estimated $8,000 to $12,000 in fuel costs per roundtrip. Those costs land directly on your ticket, either as explicit surcharges or baked into the base fare.

## Where the Money Goes

A rough breakdown for a typical NRI summer roundtrip — say, San Francisco to Delhi — illustrates the scale. Base fares are up 15 to 20 percent year-over-year. Fuel surcharges add $200 to $400 per ticket. The Pakistan rerouting penalty contributes another $50 to $100 per direction. And reduced competition — Air India has suspended Delhi-Chicago, Delhi-Newark, and Mumbai-New York through August — means fewer seats chasing the same diaspora demand.

For economy passengers booking late, the combination of fewer flights and dynamic pricing can push a $1,200 roundtrip past $1,800 or more. Premium economy and business class increases are steeper in absolute terms.

## When Relief Might Come

The honest answer: not this summer. Oil analysts expect Brent to remain above $100 per barrel as long as the Iran situation is unresolved. The Pakistan airspace ban shows no sign of lifting. Airlines have signaled their capacity cuts will run through at least August.

The first meaningful inflection point may arrive in September, when post-monsoon demand typically softens and airlines have indicated they may restore some frequencies. If oil retreats below $90 — possible if a ceasefire holds — fuel surcharges could ease by Diwali season. But a return to 2024-level fares is unlikely before 2027 at the earliest.

## What NRIs Can Do Now

**Book early.** The sweet spot for the cheapest fares is 40 to 45 days before departure — a window that is closing fast for June and July travel.

**Fly midweek.** Tuesday and Wednesday departures are consistently $100 to $200 cheaper than weekend flights on the same route.

**Rethink your transit hub.** Singapore Airlines via Changi, Cathay Pacific via Hong Kong, and Korean Air via Incheon have all reported strong India route performance and competitive pricing as they absorb traffic displaced from Gulf hubs. These carriers avoided the worst of the March disruptions and offer reliable alternatives.

**Shift your dates if possible.** October and November fares historically drop 20 to 30 percent from peak summer levels, and the post-monsoon weather across most of India is at its best.

The crisis is real, but it is not permanent. Airlines will rebuild capacity. Gulf hubs will stabilize. In the meantime, the NRIs who plan early and route creatively will save hundreds — possibly thousands — on their next trip home."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
