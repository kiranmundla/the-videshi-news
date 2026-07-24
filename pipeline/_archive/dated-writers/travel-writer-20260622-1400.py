#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env (try workspace first, then home)
for cand in [Path.home() / "workspace" / ".env.supabase", Path.home() / ".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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

qatar_body = """Qatar Airways has spent the spring quietly rebuilding the network that a Doha airspace shutdown nearly erased. From June 16, the carrier is flying to more than 150 destinations on a summer schedule that runs through September 15 — and several of the routes coming back online sit squarely on the map that matters to Indian Americans flying home through the Gulf.

For NRIs, Qatar Airways is rarely the destination. It is the connection. A San Francisco or Newark flyer headed to a second-tier Indian city almost never gets a nonstop; the trip is built on a long-haul leg to a Gulf hub and a shorter hop into India. When Doha's network collapsed to roughly 15 daily departures at the low point in early March, that one-stop math broke, and families scrambled onto pricier rerouting through Dubai, Abu Dhabi or Europe.

## What is actually back

The restored schedule leans heavily into the Indian routes that feed the diaspora. Kozhikode (CCJ) returned to daily service from May 1, reopening the Malabar Coast pipeline that carries a huge Kerala expatriate population. Goa (GOI) came back from May 16. Ahmedabad (AMD) was slated to return around June 16, restoring a key Gujarati gateway. On the western end of the journey, the US points that connect onward to Doha are also rebuilding: San Francisco came back June 11, with Atlanta, Boston and Los Angeles all on the June schedule, and Bangkok, London and San Francisco moving back to twice-daily A380 service for the summer.

That combination — US cities plus secondary Indian cities both back on the board — is what restores the seamless one-stop itinerary. A flyer from Atlanta to Kozhikode, or San Francisco to Ahmedabad, can once again do the whole trip on a single ticket through Doha rather than stitching together two carriers and hoping the bags follow.

## The fare and rebooking picture

The disruption is not fully behind travelers. Qatar Airways is still operating through dedicated corridors rather than normal airspace in parts of the region, and fuel costs spiked sharply during the crisis. Capacity is recovering faster than it is fully normal: the airline has been ramping daily departures from Doha steadily, but a return to the pre-crisis peak of roughly 150 daily flights is a summer-long project, not a switch that flips.

The practical upside is an unusually generous waiver. Any confirmed booking with travel between February 28 and September 15, 2026, is eligible for complimentary date changes to a new travel date up to October 31, subject to availability — and a full refund of unused ticket value if a flight is impacted. For a family that booked a summer India trip months ago and watched their Doha connection vanish, that flexibility is worth real money. Anyone holding an older ticket on a route that disappeared should check whether their itinerary has been reinstated before assuming they need to rebook elsewhere.

## Why this matters to NRIs

The Gulf carriers — Qatar Airways, Emirates and Etihad — are the workhorses of diaspora travel precisely because they reach the Indian cities US airlines do not. United and American concentrate on Delhi, Mumbai, Bengaluru and a handful of metros. If your family is in Kozhikode, Ahmedabad, Kochi or Thiruvananthapuram, the Gulf hub is how you get there without a domestic India connection tacked on at the end of a 15-hour flight.

That makes Qatar Airways' restoration more than an airline-recovery story. It is the reopening of the connecting architecture that a Kerala nurse in New Jersey or a Gujarati engineer in the Bay Area actually uses. The advice for summer is concrete: book the through-itinerary on a single ticket now that the legs exist again, keep the waiver terms handy in case the schedule shifts, and verify flight status 24 to 48 hours before departure, since the network is still firming up week to week.

## What's next

Watch the slot decisions at Doha. If Qatar Airways regains its peak Hamad International slots over the summer, expect frequencies on the India routes to climb back toward multi-daily and fares to ease as capacity catches up with the demand that never went away. Until then, the network is back — but it is back at a careful, rebuilding pace, and the smart diaspora traveler books early and reads the rebooking fine print."""

leela_body = """The Leela is planting a luxury flag in the middle of the Thar Desert. The Leela Jaisalmer — an 80-room desert resort and spa on 30 acres near the honey-colored ramparts of Jaisalmer Fort — is set to open in 2026, the brand's first property in Rajasthan's fabled Golden City. For diaspora families who have long treated Rajasthan as the centerpiece of the "show the kids real India" trip, it fills a conspicuous gap at the top of the market.

## A genuine luxury address in the desert

Jaisalmer has never lacked atmosphere. The living fort, a UNESCO World Heritage Site, is one of the few inhabited forts on earth, and the desert around it has drawn camel-safari tourists for decades. What it has lacked is a marquee luxury hotel to anchor the kind of multi-generational trip NRI families plan around weddings, milestone birthdays and once-in-a-few-years homecomings.

The Leela's plans read like a checklist for exactly that traveler: elegantly designed rooms and tented villas, an expansive spa and salon, a dedicated kids' club, a swimming pool, multiple dining venues, a man-made lake, a pillarless ballroom, and sprawling outdoor lawns and courtyards built for destination weddings and large family gatherings. The resort sits near Jaisalmer Fort and is reachable from Jaisalmer Airport, with Jodhpur as the larger air gateway.

It also slots into a circuit. The Leela operates The Leela Palace Udaipur and The Leela Palace Jaipur, and the brand is openly framing Jaisalmer as the third point in a Rajasthan itinerary — Jaipur, Udaipur, Jaisalmer — that a family can string together over ten days without dropping below five-star standards. For diaspora travelers who want their US-raised children to experience the desert without roughing it, that connected routing is the selling point.

## Part of a much bigger build-out

The Jaisalmer signing is one piece of an aggressive expansion. The Leela, India's largest institutionally owned pure-play luxury hospitality brand and backed by the Brookfield Group, runs 13 properties with around 3,544 keys across 11 cities. With roughly ten hotels in the pipeline, it is on track to reach 23 properties and more than 5,000 keys over the next three years, in markets including Agra, Ayodhya, Bandhavgarh, Mumbai, Ranthambore, Sikkim, Srinagar and Dubai.

Several of those targets are revealing. Ayodhya and Srinagar are pilgrimage and heritage destinations seeing a surge of domestic and diaspora interest; Bandhavgarh and Ranthambore are tiger country, increasingly on the wishlist of NRI families chasing a wildlife experience the kids will remember. The brand is building where the diaspora is already heading.

## Why this matters to NRIs

For Indian Americans, the supply of true luxury in India's heritage destinations has lagged demand. Plenty of mid-tier hotels exist, but the family that wants a single property capable of hosting a 200-guest wedding, a multi-generational reunion or simply a worry-free stay with elderly parents and small children has had limited choices outside a handful of palace hotels. New inventory at the top end eases that crunch and, over time, takes pressure off the peak-season scarcity that pushes wedding-season rates to eye-watering levels.

There is a practical booking angle, too. Opening-year properties often court guests with introductory rates and softer availability before they are fully discovered, which can make a newly opened Leela a relative value for a 2026 or early-2027 trip — provided travelers confirm the opening date directly, since luxury hotel launches in India routinely slip by a season.

## What's next

The wider signal is that India's hotel industry is betting on exactly the traveler The Videshi covers. Domestic chains are expanding hard on the thesis that geopolitical turbulence and a weak rupee are keeping more Indians — and more of the diaspora — traveling within India rather than abroad. Credit agencies expect Indian hotel demand and supply to grow 10 to 15 percent this financial year, with religious tourism, weddings and large events driving the boom.

For NRI families, the takeaway is simple. The luxury map of India is being redrawn in real time, and it is being redrawn around the desert forts, palace cities and pilgrimage towns that diaspora itineraries already favor. Jaisalmer just got a serious new reason to stay an extra night."""

domestic_body = """A counterintuitive thing is happening to Indian travel this year: the disruption pushing fares up and capacity down on international routes is quietly fueling a domestic-tourism boom — and the hotel industry is racing to build for it. For diaspora families weighing where to take elderly parents or US-raised kids on the next India trip, the shift reshapes the options on the ground.

## The build-out

Royal Orchid Hotels, the Bengaluru-based mid-scale chain, plans to open at least 50 hotels over the next 12 to 18 months, founder and chairman Chander Baljee said, lifting room inventory to roughly 11,000 from 8,000 by the end of 2027. The bet is explicit: geopolitical tension and a weak rupee are driving more Indians to vacation at home rather than abroad. "A lot of people who were planning to go for holidays to the Middle East and other places cancelled their trips and boosted domestic tourism demand," Baljee said.

He is not alone in reading the market that way. India Ratings and Research expects the country's hotel demand and supply to grow 10 to 15 percent in the current financial year. At the luxury end, The Leela is pushing toward 23 properties and more than 5,000 keys within three years, targeting heritage and pilgrimage towns. The common thread across price tiers is the same wager — that Indians, and the diaspora, will increasingly spend on travel within India.

## Why the math changed

Three forces are stacking. The Middle East conflict scrambled Gulf-hub connectivity and prompted airlines to raise fares and trim capacity, making overseas trips both pricier and less reliable. The rupee's weakness makes foreign holidays cost more in real terms while leaving domestic travel relatively cheap. And a broader cultural shift — more spending on experiences, a religious-tourism surge around sites like Ayodhya and Varanasi, and a booming wedding-and-events calendar — is filling rooms in cities that were tourism afterthoughts a few years ago.

Royal Orchid's footprint hints at where the growth is going. The chain runs 120 hotels across more than 65 locations, weighted toward Tier-2 and Tier-3 towns and pilgrimage destinations rather than just the big metros. Its asset-light model — management contracts and franchising — lets it expand fast with little capital, which is why "50 hotels in 18 months" is plausible rather than bluster.

## Why this matters to NRIs

For the diaspora, this is a planning story, not an abstract market trend. The good news: more rooms, especially in mid-scale and in the smaller cities where families actually have roots, eases the chronic scarcity that makes peak-season and wedding-season bookings so stressful. The new supply lands disproportionately in Tier-2 and Tier-3 India — exactly the places where an NRI's ancestral town finally gets a reliable, clean, predictable hotel instead of a gamble.

The caution: a domestic-travel boom means more competition for the same rooms during the windows NRIs cluster in — summer school holidays, Diwali, and the December-January wedding stretch. When more Indians stay home and travel internally, the diaspora is no longer competing mainly with other overseas families for festival-season inventory; it is competing with a surging domestic market too. The practical move is to book further ahead than felt necessary a few years ago, and to look at the newer mid-scale openings in second-tier cities, which often have availability and softer rates while the marquee properties sell out.

## What's next

The supply wave will take a year or more to fully land, and not every announced hotel will open on schedule. But the direction is clear, and it favors the diaspora traveler who plans around family geography rather than tourist hotspots. Watch the pilgrimage corridors — Ayodhya, Varanasi, the Char Dham routes — and the wildlife circuits, where both budget and luxury chains are converging.

For an NRI family mapping a 2027 trip, the message is to treat India's hotel landscape as a fast-moving target: the room that did not exist in your parents' town last year may be taking bookings by the time you fly home, and the festival-season scramble is only going to intensify as domestic demand climbs."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Qatar Airways Quietly Rebuilt Its Network — and the Diaspora's Connection Home Through Doha Is Back",
        "subheadline": "After an airspace shutdown gutted the schedule, Goa, Kozhikode and Ahmedabad are back on a 150-destination summer map that feeds the one-stop route NRIs actually use.",
        "slug": make_slug("qatar-airways-network-restoration-doha-india-routes-nri-summer"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Gulf carriers are how NRIs reach India's second-tier cities; Qatar Airways' restored Doha network reopens the seamless one-stop itinerary for families flying to Kozhikode, Goa and Ahmedabad this summer.",
        "tags": ["travel", "airlines", "qatar-airways", "gulf-hub", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Qatar Airways (official)", "url": "https://www.qatarairways.com/en/press-releases/2026/april/network-expansion.html"},
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/global/news/qatar-airways-resumes-flights-150-destinations/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/qatar-airways-delhi-flights-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/A7-ALG_Qatar_Airways_Airbus_A350-941_MSN-13.jpg/1280px-A7-ALG_Qatar_Airways_Airbus_A350-941_MSN-13.jpg",
        "image_caption": "A Qatar Airways Airbus A350-900, the aircraft anchoring the carrier's rebuilt long-haul network out of Doha",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": qatar_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Leela Is Opening a Luxury Resort in the Thar Desert — and Jaisalmer Just Joined the NRI Rajasthan Circuit",
        "subheadline": "An 80-room desert resort and spa near Jaisalmer Fort fills the missing five-star link between The Leela's Jaipur and Udaipur palaces, just as India's luxury hotel map is being redrawn.",
        "slug": make_slug("leela-jaisalmer-luxury-desert-resort-rajasthan-circuit-nri"),
        "category": "travel",
        "vertical": "hospitality",
        "diaspora_angle": "Diaspora families plan multi-generational Rajasthan trips around weddings and homecomings; a new Leela in Jaisalmer completes a connected Jaipur-Udaipur-Jaisalmer luxury circuit and eases peak-season scarcity at the top of the market.",
        "tags": ["travel", "hotels", "rajasthan", "luxury", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Leela Palaces, Hotels and Resorts (official)", "url": "https://www.theleela.com/en/press-releases/the-leela-jaisalmer"},
            {"name": "HOTELS Magazine", "url": "https://www.hotelsmag.com/the-leela-jaisalmer-to-open-in-2026/"},
            {"name": "Hotelier India", "url": "https://www.hotelierindia.com/jaisalmer-welcomes-the-leela"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/The_Golden_hue_of_Jaisalmer_Fort.jpg/1280px-The_Golden_hue_of_Jaisalmer_Fort.jpg",
        "image_caption": "The golden sandstone ramparts of Jaisalmer Fort, the UNESCO World Heritage Site beside which The Leela's new desert resort will open",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": leela_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Pricier Flights Are Fueling an India Hotel-Building Boom — and It's Landing in the Towns NRIs Actually Visit",
        "subheadline": "Royal Orchid plans 50 new hotels in 18 months and The Leela is racing to 23 properties, betting a weak rupee and Gulf turbulence keep travel inside India — with most of the new rooms in Tier-2 and pilgrimage cities.",
        "slug": make_slug("india-domestic-hotel-boom-2026-tier2-pilgrimage-nri-families"),
        "category": "travel",
        "vertical": "hospitality",
        "diaspora_angle": "The hotel boom is concentrated in the Tier-2 and pilgrimage towns where NRIs have family roots, easing room scarcity there but intensifying competition for festival- and wedding-season bookings the diaspora clusters in.",
        "tags": ["travel", "hotels", "domestic-tourism", "india", "nri"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/indias-royal-orchid-plans-add-50-hotels-betting-local-demand-boost/"},
            {"name": "India Ratings and Research", "url": "https://www.indiaratings.co.in/pressrelease"},
            {"name": "The Leela Palaces, Hotels and Resorts", "url": "https://www.theleela.com/en/press-releases"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Taj_Lake_Palace_Udaipur_from_City_Palace.jpg/1280px-Taj_Lake_Palace_Udaipur_from_City_Palace.jpg",
        "image_caption": "The Taj Lake Palace on Lake Pichola in Udaipur, an icon of the Indian heritage-hotel market now expanding into smaller cities",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": domestic_body
    }
]

def wc(s):
    return len(re.findall(r"\b\w+\b", s))

for art in articles:
    n = wc(art["body"])
    if n < 400:
        print(f"⚠ SKIP {art['slug']}: body only {n} words")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({n} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
