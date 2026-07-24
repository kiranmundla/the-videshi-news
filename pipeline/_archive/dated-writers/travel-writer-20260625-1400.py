#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

indigo_body = """India's largest airline is doing something it has not done in years: shrinking its map. IndiGo, the budget giant that spent the past decade racing to plant its flag on every reachable foreign runway, is temporarily pulling out of six international destinations this summer — a retreat that says more about the state of Indian aviation than any expansion announcement could.

## What is being cut

From July 1, IndiGo suspends flights to Langkawi, Krabi, Ho Chi Minh City, Hong Kong and Shanghai, with Siem Reap following on July 3. All six routes are scheduled to stay dark until September 30, with bookings reopening from October 1 — earlier, the airline says, if conditions improve. These come on top of services already paused to Almaty, Tashkent, Baku, Tbilisi, Kuwait and Fujairah.

The carrier is also dropping its Manchester route from August 31 and handing back one of the wet-leased Boeing 787-9 Dreamliners it had taken from Norway's Norse Atlantic — aircraft that were meant to be IndiGo's bridge into long-haul Europe until its own Airbus A350s arrive. IndiGo frames it all as "network optimisation" to match capacity with "softer demand" and "an incredibly challenging cost environment," and stresses it still flies more than 1,800 international flights a week.

## Why now

The blunt reason is money. IndiGo posted a loss of ₹2,536 crore in the fourth quarter of FY26, dragged down by a weak rupee and thin yields. Behind that loss sits a geography problem the airline cannot fly around.

Pakistan's airspace remains closed to Indian carriers, and the Iran conflict has forced wide detours across West Asia. Routes that once ran in a straight line now arc the long way around, burning more fuel and more crew hours for the same ticket revenue. On thin leisure routes to Central Asia and Southeast Asia, that extra cost is enough to tip a marginally profitable flight into a money-loser. Rather than fly them at a loss through a traditionally weak quarter, IndiGo is parking them.

## The diaspora angle

For Indian Americans, the immediate sting is small but real. The cuts hit holiday and short-haul leisure routes — Krabi, Langkawi, Siem Reap — that NRIs often bolt onto a longer India trip, turning a family visit into a regional vacation. Anyone who had penciled in a Southeast Asian leg between July and September on IndiGo metal will need to rebook on another carrier or wait for October.

The Manchester withdrawal is the more telling signal. It marks IndiGo's first stumble in its long-haul ambitions, the very ambitions that promised diaspora flyers more India-direct options to Europe and, eventually, North America. That timeline has now slipped. The Dreamliner going back to Norse Atlantic is a concrete reminder that the airspace crisis is not a background headline — it is actively reshaping which homeland-bound routes get built and which get shelved.

There is a quieter takeaway too. With both IndiGo and Air India trimming and re-routing, fares on the surviving nonstop and one-stop services to India are unlikely to soften this year. Diaspora families planning autumn and Diwali travel should book early and watch for schedule changes, because the network they remember from 2024 is being redrawn in real time.

## What is next

IndiGo insists the retreat is temporary and that it stands ready to relaunch routes "earlier than scheduled" if the operating environment eases. The trigger it is watching for is obvious: a reopening of Pakistani airspace, a calming of the West Asian conflict, or a meaningful drop in jet fuel prices. Any one of those would shorten flight times and rescue the economics of the parked routes overnight.

Until then, the era of IndiGo's relentless international land-grab is on pause. The airline is signaling discipline over growth — keeping the bulk of its 1,800-plus weekly overseas flights while quietly conceding that, for now, geopolitics has a veto over the route map. For a carrier that built its brand on always adding, learning to subtract may be the harder skill — and the more important one in a year when the skies over India have rarely been more complicated."""

akasa_body = """While IndiGo retreats, India's youngest major airline is leaning into the same storm — and choosing to grow through it. Akasa Air, the carrier that launched only in 2022, is targeting a 30 percent capacity increase in the year to March 2027 and pushing aggressively into Southeast Asia, even as the same airspace crisis squeezing its bigger rivals forces it to abandon its original game plan.

## A pivot, not a retreat

Akasa's strategy was supposed to point west. Five of its first six international routes ran into the Middle East — Doha, Jeddah, Riyadh, Abu Dhabi and Kuwait City — and the plan was to deepen that Gulf footprint as bilateral flying rights opened up. Then the Iran conflict froze West Asian expansion in place.

So the airline turned east. From September 4, Akasa begins four weekly nonstop flights between Mumbai and Hanoi, its seventh international destination and second in Southeast Asia after Phuket. Vietnam's capital — all centuries-old streets, French-colonial architecture and celebrated street food — has become a fast-rising favourite for Indian travellers, and Akasa is betting that short-haul, visa-friendly Southeast Asia is the growth corridor the Gulf can no longer be, at least for now.

## The numbers behind the ambition

This is expansion on a young airline's nerve. Akasa operates a fleet of 39 Boeing 737 MAX jets and says operating revenue rose 37 percent in the last fiscal year, with capacity up 30 percent. International flying now accounts for about 25 percent of its total capacity, a share chief executives say could climb toward 40 percent over the next few years. The airline has told reporters it aims to reach 226 aircraft by 2032.

It is not painless. Like every Indian carrier, Akasa is absorbing the cost of longer routings around closed airspace, and its finance chief has confirmed the airline is weighing whether to tap a government emergency credit-guarantee scheme — a ₹181 billion facility set up to help businesses ride out the liquidity squeeze from the war. Akasa says it has drawn nothing yet. It is also holding firm on identity: no premium cabins, no leasing of older jets, just a single-class, all-economy fleet. An IPO remains on the horizon, management says, but on a two-to-four-year timeline and as an "output" of building a good airline rather than the goal itself.

## The diaspora angle

For the Indian American community, Akasa's pivot is good news in an otherwise tightening market. While IndiGo and Air India trim overseas routes, here is a carrier still adding international capacity — and adding it in exactly the kind of short-haul leisure markets that pair naturally with a longer homeland trip. An NRI family flying into Mumbai can now tack on a Vietnam leg on a single Indian carrier, the sort of add-on that used to require a foreign airline and a separate ticket.

More broadly, Akasa's survival-by-expansion matters for diaspora travellers because competition is what keeps India's international fares honest. In a year when the two giants are pulling back, a hungry third player still chasing 30 percent growth is a useful counterweight. And as Akasa scales toward a fleet five times its current size, the long game points to more India-connected routes — and eventually, perhaps, the long-haul flying that would put it in direct service of the US-India corridor the diaspora depends on.

## What is next

The near-term test is whether Akasa can fund this growth through a brutal cost cycle without breaking its all-economy, no-frills discipline. Hanoi launches in September; more Southeast Asian additions are likely if the Gulf stays frozen. Watch, too, for whether the airline draws on that government credit line — a move that would signal the cash crunch is biting harder than the bullish capacity targets suggest.

For now, Akasa offers a striking counter-story to the summer's retreat. Same airspace, same fuel bills, same war next door — but a fundamentally different answer. Where the incumbents are subtracting, the upstart is still betting that the fastest way through a crisis is to keep flying into it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Pulls Out of Six International Routes This Summer as the Airspace Crisis Forces India's Biggest Airline to Shrink",
        "subheadline": "Flights to Hong Kong, Shanghai and four Southeast Asian cities go dark from July to September, the Manchester route is dropped, and a leased Dreamliner heads back to Norway.",
        "slug": make_slug("indigo-international-route-suspensions-airspace-southeast-asia-nri-2026"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The suspended routes are exactly the Southeast Asian leisure legs NRIs bolt onto a homeland trip, and IndiGo's stalled long-haul push means the extra India-direct options the diaspora was promised are now slipping further away.",
        "tags": ["travel", "airlines", "indigo", "airspace", "southeast asia"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-2026-06-04/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-suspends-flights-to-six-asian-destinations/article.ece"},
            {"name": "Skift", "url": "https://skift.com/2026/06/05/indigo-suspends-7-international-routes-whats-behind-the-cutbacks/"},
            {"name": "The Economic Times", "url": "https://economictimes.indiatimes.com/markets/stocks/news/indigo-shares-in-focus-as-airline-suspends-flights-to-6-countries/articleshow.cms"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/indigo-international-route-suspensions-airspace-southeast-asia-nri-2026.jpg",
        "image_caption": "An IndiGo Airbus A320neo on the tarmac; the carrier is suspending six international routes between July and September 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": indigo_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Akasa Air Bets on Southeast Asia and 30% Growth Even as the Same Airspace Crisis Freezes Its Gulf Plans",
        "subheadline": "India's youngest major carrier launches Mumbai-Hanoi on September 4 and pushes international flying toward 40% of capacity while its bigger rivals retreat.",
        "slug": make_slug("akasa-air-hanoi-southeast-asia-pivot-gulf-freeze-nri-2026"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "As IndiGo and Air India trim overseas routes, a hungry third carrier still chasing 30 percent growth keeps competition — and India fares — honest for NRI travellers, while opening single-airline add-on trips like a Vietnam leg off a Mumbai homeland visit.",
        "tags": ["travel", "airlines", "akasa air", "vietnam", "southeast asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indian-airline-akasa-targets-30-capacity-growth-weighs-government-credit-scheme-2026-06-23/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/akasa-air-eyes-30-capacity-growth-in-fy27-on-track-for-ipo-in-2-3-yrs/article.ece"},
            {"name": "Skift", "url": "https://skift.com/2026/04/18/akasa-heads-to-hanoi-as-iran-war-freezes-gulf-expansion-plans/"},
            {"name": "Asian Aviation", "url": "https://asianaviation.com/akasa-air-adds-hanoi-route/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/akasa-air-hanoi-southeast-asia-pivot-gulf-freeze-nri-2026.jpg",
        "image_caption": "An Akasa Air Boeing 737 MAX; the carrier launches nonstop Mumbai-Hanoi flights from September 4, 2026.",
        "image_attribution": "Wikimedia Commons",
        "body": akasa_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
