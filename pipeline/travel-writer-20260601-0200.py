#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-01 02:00 UTC run."""

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
    # ─── ARTICLE 1: Airport Lounge Crackdown ───
    {
        "id": str(uuid.uuid4()),
        "headline": "The Great Airport Lounge Crackdown Is Here — and NRIs Flying to India Will Feel It Most",
        "subheadline": "American Airlines, Delta, Capital One, and Amex are all tightening lounge access at once. If you rely on a premium credit card to survive those 18-hour India runs, here is what just changed.",
        "slug": make_slug("airport-lounge-crackdown-nri-india-flights"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who fly SFO-DEL, JFK-BOM, or ORD-HYD two to three times a year have built their entire travel routine around lounge access — hot showers at Centurion, Priority Pass meals during layovers, a quiet seat before boarding a 15-hour red-eye. These credit card perks are now being gutted across the board, and the India corridor is disproportionately affected because of its long-haul layover-heavy structure.",
        "tags": ["travel", "airlines", "airport lounges", "credit cards", "NRI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/american-airlines-joins-delta-air-lines-united-emirates-qatar-airways-to-restrict-airport-lounge-access-in-2026/"},
            {"name": "Inc.com", "url": "https://www.inc.com/business-travel/how-1-decision-at-american-airlines-changed-the-entire-industry/91156858"},
            {"name": "Your Mileage May Vary", "url": "https://yourmileagemayvary.com/major-airport-lounge-access-changes-coming-in-early-2026/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/35026875/pexels-photo-35026875.jpeg",
        "body": """For a generation of Indian Americans who fly to India two or three times a year, the airport lounge has become as essential to the journey as the boarding pass itself. A hot shower at the Amex Centurion Lounge in SFO before a 16-hour red-eye to Delhi. A Priority Pass meal during a four-hour layover at Doha or Dubai. A quiet corner at the Delta Sky Club to charge devices and avoid the terminal chaos at JFK.

That ecosystem is unravelling — fast.

## What Changed, and Why It Matters

In the span of a few months, nearly every major credit card issuer and airline has tightened lounge access rules:

**Capital One Venture X** — Since February 2026, cardholders can no longer bring guests to Capital One or Priority Pass lounges for free. Guests now pay standard entry fees, typically $27–$50 per person.

**Chase Ritz-Carlton Card** — As of January 15, Priority Pass access is capped at two free guests per visit. Additional guests pay $27 each. Previously, the card offered unlimited guest access — a favourite of NRI families travelling together.

**American Express Platinum** — The biggest blow: Amex is ending access to Lufthansa lounges for Platinum cardholders from October 2026. For NRIs transiting through Frankfurt or Munich on Lufthansa-operated flights — one of the most common European routing options to India — this eliminates a key layover comfort.

**Delta Sky Club** — Visit limits of 10–15 per year for Amex and Reserve cardholders remain in effect. For NRIs who fly Delta domestically in addition to their international trips, the cap can be exhausted before December.

**United Club** — Star Alliance Gold access is now restricted unless cardholders hit $50,000 in annual spending, a threshold that excludes the vast majority of NRI travellers.

## Why the India Corridor Gets Hit Hardest

The typical SFO-DEL or JFK-BOM routing involves at least one layover — often at a Gulf hub (Dubai, Doha, Abu Dhabi) or a European one (Frankfurt, London Heathrow, Amsterdam). These 20–30 hour door-to-door journeys made lounge access not a luxury but a sanity tool: a shower after the first 10-hour leg, a meal that is not a $22 airport sandwich, a seat that is not a plastic bench.

The new restrictions specifically erode this corridor's value proposition. Capital One's guest fee change means a family of four now pays $81 extra at a Priority Pass lounge during a Doha layover. Amex's Lufthansa lounge exit removes the only decent pre-departure option at Frankfurt for many NRIs routing through Europe.

And the overcrowding problem is not going away. Delhi IGI's Terminal 3 has seen record traffic in 2026, with lounge capacity failing to keep pace. Priority Pass lounges at Heathrow and Dubai are routinely at capacity during peak India departure hours — late evening and overnight.

## What NRIs Can Do

**Audit your card benefits now.** Do not wait until you are at the airport to discover your lounge access has changed. Check whether your specific card and issuer combination still covers guests, and at which lounges.

**Consider the Chase Sapphire Reserve.** It still offers Priority Pass Select with two free guests — one of the last standing generous guest policies. The annual fee ($550) is steep, but the $300 travel credit and lounge access together justify it for anyone flying to India twice a year.

**Look at airline-specific lounges.** Air India's new Maharaja Lounge at SFO (opened May 2026) offers business-class passengers and Star Alliance Gold members a dedicated space. For economy travellers, day passes are sometimes available at airline lounges for $40–$60, which may now be cheaper than relying on card-based access.

**Download the LoungeBuddy app.** It provides real-time availability and lets you purchase day passes at lounges worldwide. Not ideal for frequent travellers, but useful as backup when card access fails.

The era of the all-access lounge pass is ending. For NRIs whose travel life revolves around long-haul India routes, the adjustment is not trivial — it changes how you plan layovers, which cards you carry, and which routing you choose. The sooner you recalibrate, the less painful the next SFO-DEL red-eye will be."""
    },

    # ─── ARTICLE 2: Western Ghats Monsoon Travel ───
    {
        "id": str(uuid.uuid4()),
        "headline": "The Western Ghats' Four-Month Monsoon Window Just Opened — Five Experiences NRIs Won't Find in Winter",
        "subheadline": "From June through September, India's most biodiverse mountain range transforms into a landscape of waterfalls, endemic amphibians, and spice-scented mist. Here is what makes monsoon travel in the Ghats unlike anything else.",
        "slug": make_slug("western-ghats-monsoon-window-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs visit India during winter — Diwali, Christmas, or January wedding season. They experience the Ghats dry, brown, and relatively dormant. The monsoon Ghats are a completely different landscape, and NRIs who can time a June–September trip around their India visits will see a side of the country that most diaspora travellers have never experienced.",
        "tags": ["travel", "India", "Western Ghats", "monsoon", "nature", "NRI"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Better India", "url": "https://www.thebetterindia.com/"},
            {"name": "Ease India Trip - Coorg Guide", "url": "https://easeindiatrip.com/"},
            {"name": "Agoda Travel Data 2026", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/33649970/pexels-photo-33649970.jpeg",
        "body": """The Western Ghats run 1,600 kilometres down India's western coast, from Gujarat to the tip of Kerala. For eight months of the year, they are a pleasant backdrop — green hills, coffee plantations, the occasional waterfall reduced to a trickle. Then the monsoon arrives, usually in early June, and the entire range wakes up.

Waterfalls that were dry rock faces in March become thundering curtains of water. Streams that were ankle-deep turn into rivers. The forest floor, silent in winter, erupts with the calls of endemic frogs — species found nowhere else on earth. For NRIs who have only visited India during the Diwali-to-January window, the monsoon Ghats are an entirely different country.

## 1. Frog Walks in Agumbe, Amboli, and Wayanad

This is not a metaphor. After sunset in places like Agumbe (Karnataka), Amboli (Maharashtra), and Wayanad (Kerala), trained naturalists lead small groups through wet forest trails, identifying frogs by their calls. The Western Ghats harbour over 200 amphibian species, many endemic and visible only during the monsoon breeding season.

Visitors crouch beside leaf litter and waterlogged rocks. Torches are kept dim. The Malabar Gliding Frog — bright green, with oversized webbed feet it uses to glide between trees — is the star. The Dancing Frog, which waves its hind legs to attract mates near rushing streams, is another monsoon-exclusive sighting.

For NRI families with kids studying biology, this is field research disguised as a holiday. Most walks cost ₹500–1,500 per person and run 2–3 hours.

## 2. Coorg in the Rain

Coorg (Kodagu) in Karnataka is India's coffee country, and June transforms it. Daytime temperatures hover around 20–25°C, the humidity sits at 85–95 per cent, and the entire district is wrapped in mist. Coffee plantations drip. Waterfalls like Abbey Falls run at full force. The air smells of wet earth, cardamom, and pepper.

The practical trade-off: 18–25 rainy days in June mean outdoor activities require flexibility. But hotel rates drop 30–50 per cent from peak-season prices, and the crowds vanish. A plantation homestay that costs ₹8,000 per night in December runs ₹4,000–5,000 in June.

For NRIs, the value proposition is clear: luxury stays in India's most atmospheric landscape at half the price, with the only cost being a willingness to get wet.

## 3. Dudhsagar Falls at Full Volume

The 310-metre Dudhsagar Falls on the Goa-Karnataka border is one of India's tallest. In winter, it is a thin white line against brown rock. In monsoon, it becomes what its name promises — a "sea of milk" roaring down four tiers of cliff face, visible from the railway bridge that crosses its gorge.

The classic approach is by train from Margao or Castle Rock — a journey through tunnels and bridges that is itself a monsoon spectacle. Jeep safaris from Mollem operate when the roads are passable. The falls are typically at peak flow from late June through August.

NRIs visiting family in Goa during summer should treat this as a mandatory day trip. It is 60 kilometres from Panaji and a world away from the beach-bar Goa most diaspora travellers know.

## 4. Spice Plantation Stays in Wayanad and Munnar

Kerala's spice country comes alive during monsoon. Pepper vines flower, cardamom pods swell, and the tea estates of Munnar turn an almost artificial shade of green. Several plantations offer monsoon-season stays where guests walk through working spice gardens, learn to identify pepper, clove, nutmeg, and cinnamon growing on the vine, and eat meals cooked with ingredients picked that morning.

Wayanad has seen a 40 per cent jump in family accommodation searches for summer 2026, according to Agoda data — driven by families seeking cooler, greener getaways from the plains. Prices during monsoon run 25–40 per cent below October-to-March rates.

## 5. The Netravati Peak Trek

For NRIs who want something more demanding, the Netravati Peak trek in Chikmagalur district offers a two-day forest and ridge walk inside Kudremukh National Park. The trail passes through tea estates, river crossings, and shola-grassland ridges with panoramic views of the rain-soaked Ghats.

Forest permits are required (₹505, limited slots — book at least a month in advance). The trek is rated moderate, doable for reasonably fit adults and teenagers, and runs roughly 7 hours from Bengaluru by road.

## The Practical Case for Monsoon Travel

The monsoon Ghats are not a compromise destination. They are a different experience — one that requires waterproof bags, flexible plans, and a tolerance for being damp. In return, you get India's most biodiverse landscape at its most dramatic, at prices 30–50 per cent below peak season, with a fraction of the crowds.

For NRIs who have seen India only in winter, a monsoon trip to the Ghats is the single biggest upgrade to their understanding of the country."""
    },

    # ─── ARTICLE 3: Puri, Wayanad Lead Family Travel Surge ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Puri and Wayanad Are Where Indian Families Are Heading This Summer — and NRIs Should Pay Attention",
        "subheadline": "Agoda data shows a 68 per cent surge in Puri bookings and 40 per cent in Wayanad. The old Goa-Shimla circuit is giving way to a new generation of family destinations — and they are better value for visiting diaspora families.",
        "slug": make_slug("puri-wayanad-family-travel-surge-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs bringing children to India for summer break tend to default to the same circuit — Delhi, then maybe Agra, then Goa or a hill station. The emerging family travel trends in India point to destinations that are richer, cheaper, and better suited to multi-generational NRI families visiting relatives while squeezing in a short vacation.",
        "tags": ["travel", "India", "Puri", "Wayanad", "family travel", "NRI", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Agoda via Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/puri-wayanad-and-goa-lead-indian-families-summer-2026-getaways-shows-agoda-data/"},
            {"name": "Kerala Tourism - Global Travel Market 2026", "url": "https://www.devdiscourse.com/article/business/3413062-kerala-to-host-global-travel-market-2026-in-june"},
            {"name": "The Better India - Monsoon Travel", "url": "https://www.thebetterindia.com/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/33573923/pexels-photo-33573923.jpeg",
        "body": """Every summer, a familiar pattern plays out in NRI households across America. The kids finish school. Flights to India get booked, usually to Delhi, Mumbai, or Hyderabad to visit family. And then someone asks: should we go somewhere for a few days? The default answers — Goa, Shimla, maybe Jaipur — have not changed in a decade.

India's domestic travel market, however, has moved on. New data from Agoda shows that the summer 2026 family travel map looks substantially different from what most NRIs expect.

## Puri: 68 Per Cent Surge in Family Bookings

Odisha's coastal temple town has recorded a 68 per cent year-on-year jump in family accommodation searches for May–June 2026. The number is not a statistical fluke — it reflects a genuine shift in how Indian families think about summer holidays.

The appeal is specific: Puri offers something almost no other Indian destination does at this price point. The Jagannath Temple — one of the four sacred dhams — gives grandparents a reason to come. The broad Bay of Bengal shoreline gives children a beach. The town's food culture, centred on the temple's Ananda Bazaar (one of the world's largest community kitchens), gives everyone something to talk about at dinner.

For NRI families with elderly parents in Odisha or Bengal, Puri is a two-to-three-hour drive from Bhubaneswar — close enough for a weekend side trip, substantial enough for a three-night stay. Hotels in the ₹3,000–6,000 per night range deliver clean, air-conditioned rooms within walking distance of the beach.

The Rath Yatra, typically in June or July, adds another reason to time a visit. Watching three massive wooden chariots pulled through the streets by thousands of devotees is an experience that is difficult to replicate — and one that NRI children studying Indian culture from textbooks will remember.

## Wayanad: 40 Per Cent Jump — and Falling Prices

Kerala's hill district has seen a 40 per cent rise in family searches, driven by a straightforward value proposition: cooler temperatures, dense forests, and monsoon-season rates that are 25–40 per cent below winter prices.

Wayanad's wildlife sanctuaries, plantation retreats, and mist-covered forests cater to a different kind of family holiday — one where the itinerary involves jeep safaris, farm stays, and nature walks rather than pool time and buffets. For NRI families with children aged 8 and above, this is India as a nature destination, not just a family obligation.

The practical infrastructure is in place. Wayanad is three hours from Kozhikode (Calicut) airport, which has direct flights from the Gulf and connecting flights from all major Indian cities. Bengaluru is a six-hour drive — manageable for NRIs visiting family in Karnataka's tech capital.

## Goa: Still There, but Changing

Goa remains on the list — it would be strange if it did not — but the nature of Goa family travel is shifting. The beach-shack, party-circuit Goa that dominated the diaspora imagination for decades is being replaced by a quieter, more residential version. Families are booking villas in South Goa over hotels in North Goa. Boutique stays in Assagao and Aldona are replacing the Calangute strip.

Monsoon Goa, once considered off-season, has its own growing audience. Green rice paddies, empty beaches, and rain-washed Portuguese architecture create a visual contrast to the December-January crowds. Hotel rates drop accordingly.

## What This Means for NRI Families

The old NRI travel formula — fly into a metro, visit relatives for two weeks, maybe squeeze in one tourist stop — is increasingly inadequate. India's domestic travel infrastructure has improved enough that short side trips are no longer logistical nightmares. Trains run on time more often than not. Budget airlines connect tier-two cities. Hotel standards outside the metros have risen sharply.

For NRI families visiting India this summer, the practical advice is simple: add two to three days to your trip and book a destination your Indian relatives are already talking about. Puri if your family is in the east. Wayanad if they are in the south. Monsoon Goa if they are on the west coast.

Kerala is leaning into this shift. The state is hosting the second edition of the Global Travel Market on June 3–5 in Thiruvananthapuram, with over 1,000 tour operators and 300 corporate buyers — a B2B event, but a signal of how seriously India's states now take domestic tourism infrastructure.

The destinations have changed. The prices have dropped. The only thing that has not changed is the NRI default to Goa and Shimla. This might be the summer to update the playbook."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
