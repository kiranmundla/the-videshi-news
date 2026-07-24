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

bali_body = """India's largest airline is about to do something it has never done before: fly a single-aisle jet nearly eight hours nonstop to a beach.

IndiGo confirmed on June 19 that it will launch direct service from both Delhi (DEL) and Mumbai (BOM) to Bali's Ngurah Rai International Airport (DPS) using the new Airbus A321XLR, replacing the one-stop routings it currently flies with smaller A320neo aircraft. Westbound sectors back to India are expected to run as long as seven hours and 55 minutes — among the longest narrowbody flights the carrier has ever scheduled.

## Why a Narrowbody Goes Long-Haul

For years, a nonstop to Bali required a widebody, and the economics rarely worked for a low-cost carrier. The A321XLR changes that math. The aircraft can fly roughly 8,700 km — about 4,700 nautical miles — which is enough to open thinner long-haul markets that never justified a 250-seat Boeing or Airbus widebody. IndiGo, which says it operates 2,200 daily flights to 141 destinations and controls the largest share of India's domestic market, is using the jet to push into leisure routes it could only serve with a connection before.

This is the strategic shift worth watching: India's biggest airline, historically built on high-frequency short hops, is now flying long and thin on a single aisle. Bali is the proof of concept.

## What It Means for the Diaspora

For the 4.5 million-strong Indian American community, a nonstop Delhi or Mumbai-Bali flight is not directly a route home. But it reshapes the most popular add-on trip the diaspora takes. Bali has quietly become the destination of choice for NRI destination weddings, multi-generational family holidays, and the "stop somewhere on the way" leg that breaks up a long India trip. Until now, getting there from India meant a connection through Singapore, Kuala Lumpur, or Bangkok — and a half-day of airport time.

A direct flight collapses that. An NRI family flying SFO or JFK to Delhi for a wedding can now tack on Bali as a clean two-flight extension rather than a three-flight ordeal with bags to re-check. For the Gujarati and Punjabi wedding circuits that increasingly book Bali resorts, the nonstop also makes it realistic to fly elderly relatives who can manage one long flight but not a midnight layover.

There is a catch worth flagging. A narrowbody on an eight-hour run is a different experience from a widebody: narrower aisles, no crew rest, and a single-aisle cabin for the duration. Travelers used to a Dreamliner or A350 on long-haul should set expectations accordingly, and families with small children may want to weigh seat selection carefully.

## What's Next

IndiGo has not published fares or a firm start date for the Bali nonstops, and the A321XLR rollout is being staged across the network as deliveries arrive. The carrier has signaled this is part of a broader long-and-thin strategy, which means more leisure markets in Southeast Asia and Central Asia could follow the same template. For NRIs planning a 2026-27 India trip with a beach week attached, the advice is simple: watch IndiGo's schedule loads in the coming weeks, and book the India leg and the Bali leg on a single itinerary so a delay on one doesn't strand you on the other.

For now, the headline is the strategy, not the schedule. India's dominant carrier has decided a beach in Indonesia is worth eight hours on a single aisle — and the diaspora's favorite wedding-and-honeymoon island just got materially closer to home."""

monsoon_body = """The conventional wisdom says skip India in the monsoon. The conventional wisdom is wrong — and for the diaspora, the rainy season may be the smartest time to go.

With the southwest monsoon now sweeping north across the subcontinent — the India Meteorological Department flagged heavy rain over the Northeast, Kerala, and the Western Ghats this week — July and August are written off by most NRI families as a washout. But for travelers who can't always pick their dates, monsoon travel offers emptier sites, dramatically lower hotel rates, and a version of India that peak-season tourists never see. The key is knowing where the rain is a feature and where it's a hazard.

## Where the Rain Is the Point

**Kerala** is India's original monsoon destination, and its tourism board actively promotes June through August as the best window for Ayurvedic treatment — the humid climate is considered ideal for therapies like Panchakarma. Kochi and Alleppey are the gateways to houseboat cruises through rain-swollen backwaters, while the tea plantations of **Munnar** turn an almost electric green. Further north, **Wayanad** has reopened to visitors with misty forests and far smaller crowds than Munnar, though the Chooralmala-Mundakkai area remains restricted after the 2024 landslides.

**Coorg** in Karnataka — the "Scotland of India" — delivers coffee-plantation walks and waterfalls at full force, and **Ooty** and **Kodaikanal** in Tamil Nadu offer cool hill-station air. For families based in or visiting Mumbai and Pune, Maharashtra's Western Ghats are unbeatable for a weekend: Lonavala and Mahabaleshwar for waterfalls and valley views, Malshej Ghat for cloud-level drives, and Matheran, India's only car-free hill station.

## Where to Be Careful

Not every green photo is a safe bet. Sikkim and parts of Kerala see heavy rainfall that triggers landslides and road closures, and hill roads can shut with little warning. If your itinerary is fixed and you need reliability, the smarter monsoon picks are the rain-shadow regions: **Ladakh**, a high-altitude desert largely untouched by the monsoon; **Rajasthan's** Udaipur, where the rains fill the lakes and cool the heat without flooding the city; and **Kashmir**, which sees only mild August rain and stays green and accessible.

## Why This Matters for NRIs

Most diaspora families travel to India on a school-calendar clock, and summer break lands squarely in monsoon season. That's usually treated as bad luck. It doesn't have to be. Monsoon is when domestic hotel rates fall hardest — premium properties in Kerala, Coorg, and Goa discount steeply — and when the queues at heritage sites thin out. An NRI family flying in for July weddings or family obligations can build a genuinely good holiday around the rain instead of enduring it.

The practical playbook: pack quick-dry clothes and a compact rain shell, build buffer days into hill-station legs in case roads close, avoid red-alert zones flagged by the IMD, and lean toward rain-shadow destinations if your dates are immovable. Travel insurance that covers weather disruption is worth the small premium on a monsoon itinerary.

Goa in the monsoon is its own argument — empty beaches, lush interiors, deeply discounted rooms, and the Sao Joao festival in late June — provided you accept afternoon downpours and some shuttered beach shacks.

The diaspora has spent years treating the monsoon as the season to avoid. For families who travel when the calendar allows rather than when the brochures recommend, it may be the season that rewards them most."""

rajasthan_body = """India has just redrawn the map of where foreigners can travel in the Thar Desert — and for diaspora families planning a Rajasthan trip, the fine print is unusually good news.

On June 18, the Ministry of Home Affairs notified the Immigration and Foreigners (Amendment) Order, 2026, which completely revises the list of "protected areas" across Rajasthan's border districts and, crucially, clarifies the legal status of Overseas Citizen of India (OCI) cardholders within India's immigration rules. The order modifies the broader Immigration and Foreigners framework introduced in 2025 and lands right as the desert tourism season planning begins.

## What Actually Changed

The headline for travelers is what stays open. The amendment names protected areas across the border districts of Jaisalmer, Bikaner, Sriganganagar, Barmer, Phalodi, and Jalore — but it carves out broad exemptions that cover almost everything a tourist actually wants to see.

The municipal areas of Jaisalmer, Bikaner, Barmer, Sriganganagar, Phalodi, and Pokaran are exempt. The national highway corridors along NH-11, NH-62, and NH-68 are excluded from restrictions. And the marquee desert experiences remain fully open: the **Sam sand dunes**, the abandoned village of **Kuldhara**, **Amarsagar**, **Khuri**, and the desert safari and camping sites that anchor a Jaisalmer itinerary. The order even excludes a 500-meter corridor along the roads leading to those tourist spots, so the drive in is covered too.

In plain terms: the camel safaris, the dune camps, the golden-sandstone fort city, and the routes connecting them are not affected. The restrictions apply to genuine border-sensitive zones, not the tourist trail.

## The OCI Clarification

The quieter but more consequential change for the diaspora is definitional. For the first time, the order formally writes the term "OCI Cardholder" into the immigration regulations, aligned with the Citizenship Act, 1955. It also gives authorities flexibility to permit movement with or without a permit depending on the situation.

For OCI families — the children and grandchildren of Indian emigrants who hold lifelong India travel and residency rights — this matters. Protected-area rules have historically been a gray zone for OCI holders, who are neither ordinary foreigners nor Indian citizens. Codifying their status reduces the risk of an OCI traveler being treated under blanket foreigner restrictions at a checkpoint, though families should still carry their OCI card and passport when traveling near border districts.

## Why It Matters for NRIs

Jaisalmer and the Thar are a fixture of the diaspora travel itinerary — the desert wedding, the multi-generational heritage tour, the bucket-list camel night under the stars. Uncertainty over what was "protected" and what wasn't has long made families nervous about booking dune camps near the Pakistan border. This order removes most of that ambiguity by spelling out, district by district, what stays open.

The practical takeaway: a Sam dunes safari, a night at a Jaisalmer desert camp, and a drive out along the exempt highways are all clearly permitted. Foreign-passport-holding travelers and OCI families should still travel with documents in hand and confirm with their tour operator on any offbeat route that strays from the named tourist zones. But the desert's greatest hits are open for business — and the rules just got clearer than they've been in years.

For NRI families who have circled a Rajasthan trip on the 2026-27 calendar, the message from New Delhi is reassuring: the romance of the Thar is firmly inside the lines."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is About to Fly a Single-Aisle Jet 8 Hours to Bali — and the Diaspora's Wedding Map Just Changed",
        "subheadline": "New Delhi and Mumbai nonstops on the Airbus A321XLR replace one-stop routings, turning the favorite NRI add-on island into a clean two-flight extension.",
        "slug": make_slug("indigo-a321xlr-bali-nonstop-delhi-mumbai-nri-wedding"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Bali is the diaspora's go-to destination wedding and family-holiday add-on to an India trip; IndiGo's nonstops from Delhi and Mumbai cut out the Singapore/KL connection that made it a three-flight ordeal.",
        "tags": ["travel", "airlines", "indigo", "bali", "a321xlr"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying", "url": "https://simpleflying.com/"},
            {"name": "AeroRoutes", "url": "https://www.aeroroutes.com/"},
            {"name": "Aviation Week — Routes & Networks", "url": "https://aviationweek.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Tanah-Lot_Bali_Indonesia_Pura-Tanah-Lot-01.jpg/1280px-Tanah-Lot_Bali_Indonesia_Pura-Tanah-Lot-01.jpg",
        "image_caption": "Pura Tanah Lot, the sea temple on Bali's southwest coast and an icon of the island IndiGo will soon serve nonstop",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": bali_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Everyone Says Skip India in the Monsoon. For NRI Families Who Travel on the School Calendar, That's a Mistake",
        "subheadline": "Emptier sites, the year's lowest hotel rates, and a greener country — a region-by-region guide to where July and August rain is a feature, not a hazard.",
        "slug": make_slug("india-monsoon-travel-guide-2026-nri-families-where-to-go"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Diaspora families travel to India on the summer school break, which lands in monsoon season; instead of writing it off, they can build a better, cheaper, less-crowded trip by choosing the right regions.",
        "tags": ["travel", "monsoon", "india", "kerala", "rajasthan"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/"},
            {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Munnar_-_Tea_Plantations.jpg/1280px-Munnar_-_Tea_Plantations.jpg",
        "image_caption": "Tea plantations turn electric green during the monsoon at Munnar in Kerala's Western Ghats",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": monsoon_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Redrew Its Desert Travel Map — and Jaisalmer's Camel Safaris Are Firmly Inside the Lines",
        "subheadline": "A new June 18 immigration order revises Rajasthan's protected areas and, for the first time, writes OCI cardholders into the rules — clearing up years of ambiguity for diaspora travelers.",
        "slug": make_slug("india-immigration-order-2026-rajasthan-desert-jaisalmer-oci-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Jaisalmer and the Thar are a diaspora travel staple, but uncertainty over border 'protected areas' made families nervous to book; the new order spells out what stays open and codifies OCI cardholders' status.",
        "tags": ["travel", "rajasthan", "oci", "immigration", "jaisalmer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SCC Times", "url": "https://www.scconline.com/blog/post/2026/06/20/immigration-foreigners-amendment-order-2026-explained/"},
            {"name": "Ministry of Home Affairs (Immigration and Foreigners Amendment Order, 2026)", "url": "https://www.mha.gov.in/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Camels_at_Sam_sand_dunes%2C_Jaisalmer_%2844753465845%29.jpg/1280px-Camels_at_Sam_sand_dunes%2C_Jaisalmer_%2844753465845%29.jpg",
        "image_caption": "Camels at the Sam sand dunes near Jaisalmer, a desert tourism site that remains exempt under the new order",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": rajasthan_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
