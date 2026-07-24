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
        "headline": "IndiGo Is Taking Bali Nonstop — and the New Jet Doing It Has a Premium Cabin",
        "subheadline": "From the winter 2026/27 season, Delhi and Mumbai travelers can reach Denpasar without a fuel stop, on the same long-range Airbus IndiGo is using to crack Europe.",
        "slug": make_slug("indigo-a321xlr-bali-nonstop-denpasar-premium-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Bali is the diaspora's go-to short-haul beach reunion spot between US-India visits, and a one-stop flight that becomes nonstop with a premium cabin reshapes how NRI families plan the India leg of a Southeast Asia trip.",
        "tags": ["travel", "airlines", "indigo", "bali", "southeast-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/15/indigo-to-deploy-airbus-a321xlr-to-this-popular-tourist-destination/"},
            {"name": "Aviation Week", "url": "https://aviationweek.com/air-transport/airlines-lessors/indigo-connects-europe-two-new-routes"},
            {"name": "IndiGo (goindigo.in)", "url": "https://www.goindigo.in/information/press-release.html"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8333127/pexels-photo-8333127.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Pura Ulun Danu Bratan, the lakeside temple that has become Bali's most photographed landmark for Indian travelers.",
        "image_attribution": "Pexels",
        "body": """IndiGo, India's largest airline, is about to do something it has never done before on one of the diaspora's favorite leisure routes: fly to Bali without stopping. From the Northern Winter 2026/27 season, the carrier will upgrade its Delhi–Denpasar and Mumbai–Denpasar services to the Airbus A321XLR, retiring the awkward fuel stops in Bhubaneswar and Chennai that have defined the route until now.

## Why the stopover existed in the first place

IndiGo's workhorse A320neo simply cannot make Bali in one hop. The current Delhi and Mumbai services to Denpasar route through an intermediate Indian city to refuel, adding an hour or more on the ground and turning a beach holiday into a test of patience. The A321XLR — "XLR" for extra-long range — changes the math. With a range of up to 8,700 km, it covers the India–Bali sector comfortably nonstop.

IndiGo became the first Indian carrier to induct the A321XLR in January 2026, and one of the earliest operators in the world. It has 40 on order, with nine due by the end of 2026. The airline first deployed the type on Mumbai–Athens and Delhi–Athens, then Delhi–Istanbul; Denpasar was always flagged as one of the next destinations in line.

## What changes in the cabin

The headline isn't just the missing stopover — it's the seat. The A321XLR flies in a two-class layout: 12 seats of "IndiGo Stretch," the airline's premium product, up front, and 183 economy seats behind. Stretch brings wider recline, power outlets, priority check-in and boarding, and complimentary hot meals — features a budget-carrier passenger to Bali has never had on this route.

Separately, IndiGo is rolling Stretch out on its daily Bengaluru–Mauritius service from July 18, giving South India another premium long-leisure option to an Indian Ocean favorite.

## Why this matters to NRIs

For the Indian American who flies home once or twice a year, Bali has quietly become the diaspora's preferred "neutral ground" — a short, visa-on-arrival beach reset that pairs naturally with a trip to India without eating another long-haul out of the US. Until now, building Bali into that itinerary meant accepting a domestic-style stopover and a no-frills cabin on the international leg.

A nonstop from Delhi or Mumbai with a real premium cabin tightens that calculus considerably. An NRI landing in Delhi can now connect onward to Denpasar in a single hop, and parents or in-laws joining from India face a far easier journey. For multigenerational family trips — where a 70-year-old grandparent and a toddler are on the same booking — removing a midpoint stop is not a luxury, it's the difference between a trip that happens and one that doesn't.

The A321XLR is also central to IndiGo's broader push into markets the diaspora cares about: Europe via Athens, Istanbul, Amsterdam and Manchester, with more to come. Every XLR that enters service expands the menu of affordable, India-originating long-haul options — and that competition is exactly what tends to pull fares down on the connecting flights NRIs actually book.

## What to know before you plan

The Bali upgrade lands in the Northern Winter 2026/27 schedule, which runs from late October 2026. That timing matters: winter is peak season for Bali, and it overlaps with the post-Diwali travel window when many NRIs are already in India visiting family. Travelers building a December trip should watch for IndiGo to open the nonstop inventory in the coming months, and compare the new Stretch fares against the widebody competition on the India–Bali corridor before booking.

For now, IndiGo's message is consistent: efficient, long-range narrowbodies plus a growing premium cabin, aimed squarely at higher-yield leisure traffic. Bali is simply the most diaspora-relevant proof of the strategy yet."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air New Zealand Is Studying Direct India Flights — and Its India-Born CEO Is Driving It",
        "subheadline": "A new free trade deal and a Bengaluru-born chief executive have put nonstop India–New Zealand routes on the table for one of the world's most remote diaspora corridors.",
        "slug": make_slug("air-new-zealand-direct-india-flights-fta-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Indians are New Zealand's third-largest ethnic group, yet there is still no nonstop flight between the two countries — a direct route would transform how NRI families split between India, the US and New Zealand stay connected.",
        "tags": ["travel", "airlines", "air-new-zealand", "india", "diaspora"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/air-new-zealand-evaluating-direct-flights-to-india-says-ceo-nikhil-ravishankarar/"},
            {"name": "Press Trust of India (via TTJ)", "url": "https://traveltradejournal.com/air-new-zealand-evaluating-direct-flights-to-india-says-ceo-nikhil-ravishankarar/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/724963/pexels-photo-724963.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Queenstown on Lake Wakatipu, one of the New Zealand destinations Air India passengers currently reach only via codeshare connections.",
        "image_attribution": "Pexels",
        "body": """Air New Zealand is seriously weighing direct flights to India for the first time, the airline's chief executive Nikhil Ravishankar has confirmed — a prospect with outsized meaning for one of the most stretched diaspora corridors in the world.

"Work is underway to assess the viability of those direct routes," Ravishankar told the Press Trust of India on the sidelines of the IATA annual general meeting. The carrier, he said, is "thinking about how to better connect the two countries," working closely with Singapore Airlines and Air India on servicing and connectivity.

## A CEO with a personal stake

The detail that gives this more weight than the usual airline-evaluation boilerplate: Ravishankar was born in Bengaluru. His family moved to New Zealand when he was around 14, and he took over as Air New Zealand's CEO in October 2025 after years as the airline's chief digital officer. In an industry where India route decisions are usually made by executives with no personal tie to the market, the man now running the national carrier of New Zealand grew up between the two countries.

There's symmetry on the other side, too. Air India's outgoing CEO and MD, Campbell Wilson, is himself a New Zealander — meaning both flag carriers in this conversation are led by people with feet in both nations.

## What's changed: the free trade agreement

The new urgency comes from policy. India and New Zealand recently concluded a Free Trade Agreement, and Ravishankar described it as "quite exciting for both countries" for trade and people-to-people connections alike. FTAs tend to be followed by surges in business travel, student flows and tourism — exactly the kind of demand that makes a thin, ultra-long-haul route start to pencil out.

The numbers already point one way. The Indian community is New Zealand's third-largest ethnic group, and the two countries share deep cultural ties, not least an obsession with cricket. Yet there is still no nonstop flight between India and New Zealand. Every traveler routes through Singapore, Australia or a Gulf hub.

## The connections that exist today

For now, the link runs through codeshares. Under a memorandum of understanding signed last year, Air India and Air New Zealand built a codeshare across 16 routes spanning India, Singapore, Australia and New Zealand. Passengers can fly Air India from Delhi, Mumbai, Bengaluru or Chennai, then connect at Sydney, Melbourne or Singapore onto Air New Zealand services to Auckland, Christchurch, Wellington and Queenstown.

That original MoU also flagged a possible direct India–New Zealand service by the end of 2028, subject to new aircraft deliveries and regulatory approvals. Ravishankar's latest comments suggest that timeline is now being actively pressure-tested rather than left on paper.

## Why this matters to NRIs

The Indian diaspora in New Zealand is large, young and increasingly mobile — and many of its members are part of a three-way family map that also includes relatives in India and cousins, siblings or children in the US. For these families, New Zealand is the hardest node to reach. A trip from Auckland to see family in India today means a connection and, often, an overnight; the same is true in reverse for US-based NRIs trying to visit relatives who settled in New Zealand.

A nonstop would not directly serve the US-India route most American NRIs fly. But it would knit the New Zealand branch of the global Indian family far more tightly into the network — shortening the journey for the grandparents in Bengaluru flying to meet a grandchild in Auckland, and making New Zealand a more realistic add-on for diaspora travelers already crossing the Pacific.

It remains, for now, an evaluation rather than a launch. But with an FTA freshly signed, two India-connected CEOs at the controls, and a 2028 marker already on the table, the prospect of finally flying Mumbai or Delhi to Auckland nonstop looks more concrete than it has in years."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Monsoon Is the NRI's Secret Travel Season — Here's Where to Go When India Floods",
        "subheadline": "Rain-shadow valleys, peak-volume waterfalls and half-price palace hotels: a practical guide to visiting India between June and September, when the crowds and the fares both drop.",
        "slug": make_slug("monsoon-travel-india-2026-nri-guide-rain-shadow-deals"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Summer break is when NRI families actually fly to India, and that overlaps with monsoon — knowing which regions reward the rains (and which to avoid) turns an off-season visit into the cheapest, least crowded trip of the year.",
        "tags": ["travel", "monsoon", "india", "destinations", "deals"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/india/best-places-to-visit-in-meghalaya-during-the-monsoon"},
            {"name": "India Meteorological Department (via The Indian Eye)", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36982207/pexels-photo-36982207.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Misty tea plantations at Munnar in Kerala, one of the green hill escapes that come alive during the southwest monsoon.",
        "image_attribution": "Pexels",
        "body": """For most NRI families, the trip to India is dictated by the American school calendar — which means flying home in June, July or August, squarely into the southwest monsoon. The conventional wisdom treats this as bad luck. It isn't. The monsoon is the cheapest, emptiest and, in the right places, the most beautiful time to travel in India. The trick is knowing where the rain is the attraction and where it's a problem.

## The rain-shadow play: Ladakh and the high Himalayas

The single most reliable monsoon strategy is to go where the rain doesn't reach. Ladakh sits in a Himalayan rain-shadow zone — while the plains flood, it stays clear and dry, with temperatures of 12–22°C. June through September is actually Ladakh's peak season, ideal for Pangong Lake, Nubra Valley and Zanskar.

Uttarakhand's Valley of Flowers National Park opens June 1, with peak bloom from mid-July to mid-August when more than 500 wildflower species carpet the alpine meadow. Spiti Valley is another rain-shadow gem, but a word of caution for families: approach roads from Manali turn risky in the rains, so take the Shimla–Kinnaur route instead.

## Where the monsoon is the whole point: Meghalaya and the Western Ghats

If you want the drama, head northeast. Meghalaya is the wettest place on Earth during the monsoon, and that's exactly the draw — Cherrapunji's waterfalls swell to full force, and the living root bridges around Nongriat are at their most cinematic. Shillong makes an easy base, with Mawlynnong, billed as Asia's cleanest village, a short drive away. Pack waterproof shoes; the famous 3,000-step descent to the Double Decker Root Bridge is no joke in the wet.

Down the Western Ghats, Kerala's Munnar and the hills of Coorg and Wayanad turn an electric green, and a clutch of wildlife parks stay open through the rains. Periyar in Kerala, Nagarhole's Kabini zone in Karnataka, and Maharashtra's Tadoba and Pench reserves all run monsoon safaris with thinner crowds and dramatic, mist-soaked forests.

## The value angle: Udaipur in the rain

Rajasthan isn't the obvious monsoon pick, but Udaipur transforms between July and September. Lake Pichola fills, the Sajjangarh "Monsoon Palace" finally earns its name amid the cloudbanks, and hotel rates fall to a fraction of their winter peak. Domestic fares follow — Delhi–Udaipur tickets can drop to as little as ₹1,500 one-way in the monsoon months.

## The practical NRI checklist

A few things turn a monsoon trip from gamble to bargain:

- **Book domestic legs flexibly.** Monsoon delays are real, especially in the northeast and the Ghats. Leave buffer days and avoid same-day tight connections back to your international flight.
- **Track the IMD.** The India Meteorological Department's onset and forecast updates are the single best planning tool; the southwest monsoon typically reaches Kerala in early June and sweeps north over the following weeks.
- **Lean into off-season pricing.** Heritage hotels, houseboats and hill resorts discount heavily from June to September. The same Kerala backwater cruise or Udaipur lake-palace stay that's fully booked in December is open and cheap now.
- **Skip the wrong beaches.** Goa's shacks shut and the sea turns rough; coastal Konkan is for atmosphere, not swimming. Save the beach holiday for the dry season.

## Why this matters to NRIs

The diaspora's travel window and India's discount season happen to coincide — and almost nobody plans around it. A family flying home for the summer can fold in a Ladakh leg with clear skies, a Meghalaya road trip at peak waterfall, or a half-price week in a Udaipur palace, all while the rest of the calendar's travelers stay home assuming the monsoon ruins everything.

For NRI parents trying to show US-raised kids an India beyond the family living room, the monsoon offers the version of the country that postcards rarely capture: green, dramatic, uncrowded and, for once, affordable. The rain isn't the obstacle. It's the itinerary."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
