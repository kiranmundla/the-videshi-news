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

thailand_body = """Thailand has quietly ended one of the most generous travel arrangements it ever offered Indian passport holders. On May 19, 2026, the Thai cabinet abolished the 60-day visa-free scheme — known internally as "Phor 60" — for more than 90 countries, India among them. Once the change is published in the Royal Gazette, Indians no longer slide through Bangkok or Phuket immigration on a two-month stamp. Instead, India has been moved to the Visa on Arrival category, capped at 15 days.

That is a steep drop. As recently as February 2026, Thailand had *doubled* the visa-free window for Indians from 30 to 60 days, and the Tourism Authority of Thailand was openly courting Indian families, honeymooners, and digital nomads. The reversal, Bangkok says, is about security — a string of cases involving foreigners overstaying, working illegally, or running unlicensed businesses pushed the government toward what it now calls "one country, one Thai visa exemption privilege."

## What actually changed

Under the old rules, an Indian traveler could land in Bangkok and stay up to 60 days, with the option to extend another 30 at a local immigration office — effectively three months with minimal paperwork. Under the new structure, Indians fall into Visa on Arrival, which permits a maximum 15-day stay and requires paying a fee at the airport counter. The Visa on Arrival list itself was slashed from 31 countries to just four, with India placed on it.

For anyone planning a longer trip — say, a multi-week temple circuit through Chiang Mai, or a remote-work stint in Phuket — the path now runs through Thailand's eVisa portal before departure, not a free stamp on arrival.

## Why this stings for the diaspora

Thailand is one of the most popular international getaways for Indians, drawing more than two million arrivals in 2025 and ranking as India's fourth-largest outbound destination. For NRI families in the US, Thailand has long been the convenient "meet in the middle" destination — relatives flying out from Mumbai or Delhi and cousins from California or New Jersey converging on Phuket or Krabi for a week of beaches without the visa hassle of Europe or the long-haul cost of a full India trip.

The 15-day cap and the reinstated fee change that calculus. A fee that looks trivial for a solo traveler adds up quickly for a family of five, and the shorter window squeezes the kind of relaxed, two-week multigenerational holiday that made Thailand a diaspora favorite in the first place.

## The Vietnam effect

The timing has handed a gift to Thailand's neighbors. Vietnam, with its streamlined e-visa system and lower costs, is already absorbing Indian travelers who feel nudged out. Destinations like Da Nang, Hoi An, and Ha Long Bay are seeing rising Indian interest, and 2026 may be remembered as the year a chunk of India's outbound leisure traffic began shifting east. For NRIs weighing a Southeast Asia reunion, Vietnam — along with visa-on-arrival-friendly options like Sri Lanka and the Maldives — now deserves a serious look.

## What to do before you book

If Thailand is still on your list, the practical advice is straightforward. For trips of 15 days or less, the Visa on Arrival route works, but budget for the fee and the airport queue, and carry proof of onward travel and accommodation. For anything longer, apply through the official Thai eVisa portal well ahead of departure — do not assume you can sort it out at the gate. And if you are coordinating a family reunion across continents, build in a buffer: immigration processing for the larger Indian contingent will now take longer than the breezy arrivals of the past two years.

The broader lesson for diaspora travelers is that visa-free arrangements are reversible, and 2026 has been a year of whiplash — Thailand giveth in February, taketh in May. Lock in your entry requirements at the moment of booking, not the week of departure."""

diwali_body = """If a trip to India for Diwali is on your 2026 calendar, the booking clock is already ticking. Diwali falls on Sunday, November 8 this year, with the five-day festival running November 6 through 10. For the millions of Indian Americans who fly home for the holiday, the single most important decision is not which airline — it is *when you buy the ticket*.

The consensus across fare-tracking data is blunt: for peak periods like Diwali, Christmas, and the summer holidays, you should book four to five months in advance. That puts the ideal Diwali booking window squarely in June and July. Wait until September, when fares spike on festival demand, and you will pay a premium that can run hundreds of dollars per seat.

## The price map right now

Current fares give a useful baseline. Round-trip economy from US hubs to major Indian metros for fall 2026 is clustering in a wide band depending on dates and how far out you book. New York to Delhi is showing around \\$820 for September departures, while San Francisco to Delhi and Mumbai is running closer to \\$970. Boston to Delhi for early December sits near \\$880, and Atlanta to Mumbai around \\$879. Those are the shoulder-season numbers — and they are exactly what disappears once Diwali demand kicks in.

The pattern matters: early October fares stay low *before* the festival rush, then climb sharply as November 8 approaches. If your travel dates fall in the week or two right around Diwali, you are in the most expensive window of the entire fall, which is why locking in now beats waiting for a deal that historically does not come.

## Fly the shoulder, save the most

Fare analysts repeatedly flag mid-September as the single cheapest month to fly to India, with post-monsoon fares hitting their annual lows before festival demand builds. Early October — the first two weeks — remains a sweet spot for travelers whose schedules are flexible. If you can celebrate Diwali a few days early with family or stay a little longer into mid-November, when post-festival fares settle back down, you can shave a meaningful amount off the ticket.

## Practical tactics for NRI families

A few moves consistently pay off. First, set fare alerts now on the specific city pair you need, so you can pounce the moment a fair price appears rather than checking obsessively. Second, consider splitting the itinerary — a separate transatlantic or transpacific leg paired with a regional connection can occasionally undercut a single through-fare, though it adds complexity if a bag goes missing. Third, build buffer days around the festival itself: airlines and analysts alike recommend flying a few days before Diwali rather than cutting it close, since delays during the festive crush are common.

For families traveling with elderly parents or young children, the nonstop premium is often worth it — Air India and United run direct service from several US gateways to Delhi, Mumbai, Bengaluru, and Hyderabad, sparing the connection chaos at intermediate hubs during the busiest travel weeks of the year.

## The bottom line

Diwali 2026 is November 8. The cheapest seats to India are being sold right now, in June and July, four to five months out. Every week of delay into the fall narrows your options and lifts the price. Set your alerts, pick your dates with a little flexibility, and book before the festival rush turns a \\$900 ticket into a \\$1,500 one. The diaspora ritual of flying home for the lamps and the laddoos is worth it — but only the early bookers get to do it without overpaying."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Slashed Indians' Visa-Free Stay to 15 Days — Here's What NRIs Need to Know",
        "subheadline": "Bangkok abolished its 60-day visa-free scheme and moved India to a 15-day visa-on-arrival category, upending one of the diaspora's favorite meet-in-the-middle getaways.",
        "slug": make_slug("thailand-ends-60-day-visa-free-indians-15-day-arrival-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Thailand has long been the convenient meet-in-the-middle destination for NRI families reuniting from the US and India, and the new 15-day cap plus reinstated fee squeezes the relaxed two-week multigenerational holiday that made it a diaspora favorite.",
        "tags": ["travel", "visa", "thailand", "southeast-asia", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Bharat Affairs", "url": "https://bharataffairs.com/thailand-ends-60-day-visa-free-entry-for-indians/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/thailand-cut-visa-free-stay-30-days-tourists-93-countries-2026/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/vietnam-joins-india-thailand-and-southeast-asia-tourism-realignment/"},
            {"name": "Wikipedia — Visa policy of Thailand", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_Thailand"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7494161/pexels-photo-7494161.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Kata Beach in Phuket, Thailand, a longtime favorite getaway for Indian travelers",
        "image_attribution": "Pexels",
        "body": thailand_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Flying Home for Diwali 2026? Book Now — Here's the NRI Guide to Beating the Festival Fare Spike",
        "subheadline": "Diwali falls on November 8, and fare data is clear: the cheapest seats to India are selling in June and July, four to five months out, before festival demand sends prices climbing.",
        "slug": make_slug("diwali-2026-flight-booking-window-nri-india-fare-guide"),
        "category": "travel",
        "vertical": "economy",
        "diaspora_angle": "Millions of Indian Americans fly home for Diwali, and timing the booking four to five months out can save hundreds of dollars per seat versus waiting for a festival-season deal that historically never comes.",
        "tags": ["travel", "airlines", "diwali", "flight-deals", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Medium — How to Find Cheap Flights to India 2026", "url": "https://medium.com/@cepkarthikeyachary/flights-to-india-starting-at-498-2026"},
            {"name": "Virgin Atlantic — Flights to India 2026/2027", "url": "https://flights.virginatlantic.com/en-us/flights-to-india"},
            {"name": "Alternative Airlines — Diwali 2026 dates", "url": "https://www.alternativeairlines.com/diwali-flights"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12940608/pexels-photo-12940608.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Digital flight information boards display departure schedules at an international airport terminal",
        "image_attribution": "Pexels",
        "body": diwali_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
