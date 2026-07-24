#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-26 15:00 PDT batch"""
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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Air India Maharaja Lounge at SFO
# ─────────────────────────────────────────────────────────

art1_body = """Air India's first international Maharaja Lounge opened at San Francisco International Airport on May 23, and for the roughly 700,000 Indian Americans in the Bay Area, it changes what departure day feels like.

The lounge sits near Gate A1 in SFO's International Terminal — 3,300 square feet designed by Hirsch Bedner Associates, the hospitality firm behind some of Asia's best hotel interiors. It seats about 80 guests in the main area and eight in a private first-class zone with its own à la carte menu and a reserved selection of cognac and whiskey.

## Why SFO First

Air India flies two daily nonstops from SFO to India — one to Delhi, one to Mumbai — making it the carrier's busiest US gateway by seat count. San Francisco was the obvious place to plant the flag outside India. The airline's flagship Maharaja Lounge at Delhi's T3 opened earlier this year; SFO is the second in a planned global series.

For the hundreds of thousands of tech workers, families, and students flying SFO–DEL or SFO–BOM every year, the pre-flight experience has historically been a contract lounge shared with a dozen other carriers. Now there's a dedicated space that feels deliberate.

## The Aviator's Bar

The lounge's centerpiece is a speakeasy-inspired cocktail bar separated from the main dining area. Bar stools reference seating patterns from Air India's original 1930s aircraft. Ceiling fixtures are modeled after propeller shafts from the pre-jet age. Archival imagery, vintage postcards, and model aircraft line the walls.

The cocktail menu bridges India and the West: a Maharaja Manhattan with black pepper, a Limitless with rose, hibiscus, and saffron, and a Maharaja Mule — an Indian twist on the Moscow Mule with muddled mint and ginger. The bar overlooks the tarmac, which makes it a strong pre-flight spot for anyone who likes watching 777s taxi past with a drink in hand.

## The Food

The buffet rotates by mealtime and cycle — designed to stay interesting for frequent flyers on the SFO–India corridor. On opening day, the spread included dal Bukhara, chicken tikka masala, vegetable biryani, paneer moringa, and a beet-and-fig sham savera kofta alongside grilled salmon. Cold options featured crackers, cheese, and dips including tikka achari and mango habanero. Smaller bites: fish croquettes, Szechuan paneer, and a miniature gajar ka halwa tart.

Art installations throughout the dining area were sourced from India — one piece uses pigments derived from turmeric, roses, and cinnamon instead of paint.

## What's Missing

No showers. For a 16-hour flight to Delhi, that's a notable gap. Most competing premium lounges on long-haul international routes — the Polaris Lounge at SFO, the Qantas First lounge at LAX — include shower suites. Air India may add them later, but for now, plan accordingly.

## Who Gets In

Access is open to Air India first and business class passengers, Maharaja Club Gold and Platinum members, and eligible Star Alliance premium travelers. If you're flying Air India economy — which is most NRIs — you're out of luck unless you hold Star Alliance Gold status through United MileagePlus or another program.

The lounge operates daily from roughly 6:30 a.m. to 10 p.m., though hours flex with the flight schedule.

## The Bigger Picture

The Maharaja Lounge is part of a $400 million premium overhaul that the Tata-owned Air India has been executing since 2023. New cabins, new uniforms, new in-flight dining, and now, dedicated lounges at key international airports. For a carrier that spent years as a punchline, the turnaround is real — and Bay Area NRIs flying home this summer will notice."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Just Opened Its First International Lounge — and It's at SFO, Right in the Bay Area's Backyard",
    "subheadline": "The 3,300-square-foot Maharaja Lounge near Gate A1 brings speakeasy cocktails, dal Bukhara, and spice-pigment art to the airline's busiest US gateway.",
    "slug": make_slug("air-india-maharaja-lounge-sfo-bay-area-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "SFO is Air India's busiest US gateway, serving the Bay Area's 700K+ Indian Americans. The Maharaja Lounge replaces shared contract lounges with a dedicated pre-flight space for NRIs flying home — though economy passengers still need Star Alliance Gold status to access it.",
    "tags": ["travel", "airlines", "air india", "san francisco", "sfo", "lounge"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Points Guy", "url": "https://thepointsguy.com/airline/air-india-maharaja-lounge-sfo-opening/"},
        {"name": "Air India Official", "url": "https://www.airindia.com/"},
        {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/"},
        {"name": "One Mile at a Time", "url": "https://onemileatatime.com/"},
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2612117/pexels-photo-2612117.jpeg",
    "body": art1_body,
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: India Monsoon 2026 — NRI Travel Playbook
# ─────────────────────────────────────────────────────────

art2_body = """The southwest monsoon hit Kerala today — May 26, right on the IMD's predicted date — and within two weeks it will reach Mumbai, Goa, and Bangalore. For NRIs planning a summer India trip, the next six weeks are the window that matters most.

But this is not a normal monsoon year. A developing El Niño in the Pacific is expected to weaken rainfall to 92 percent of the long-period average, according to the IMD's April forecast. Translation: some destinations will be drier and hotter than usual, others will get sudden cloudbursts, and the usual monsoon playbook needs adjusting.

## The Timing

Here's when the monsoon reaches the cities NRIs fly into:

- **Kerala (Thiruvananthapuram):** May 26 (today)
- **Goa:** June 3
- **Mumbai:** June 5–6
- **Bangalore:** June 5
- **Hyderabad:** June 12
- **Kolkata:** June 12
- **Delhi NCR:** June 30

The first two weeks after onset in any city are typically the heaviest. If you're flying into Mumbai in early June, expect airport delays and waterlogged roads from Sahar to Andheri. By mid-July, the rain settles into a rhythm — intermittent showers with dry spells between.

## The El Niño Complication

El Niño typically hits India's monsoon hardest in August and September. Central and western India — Rajasthan, Maharashtra, Madhya Pradesh — may see prolonged dry stretches. The Western Ghats waterfalls that draw monsoon tourists to Lonavala, Mahabaleshwar, and Coorg could be less dramatic this year.

On the flip side, coastal Tamil Nadu and parts of Andhra Pradesh may get intense short bursts of rain, raising flood risk in Chennai and Visakhapatnam. And the northeast — Meghalaya, Assam, Arunachal — remains relatively unaffected by El Niño, making it a safer bet for monsoon scenery.

## Where NRIs Should Go

**Safest monsoon bets this year:** Coorg (Karnataka's coffee country), Munnar (Kerala's tea hills), Udaipur (Rajasthan's lake city, drier than usual means pleasant weather), and Goa (off-season rates are 40-60 percent cheaper, beaches are emptier, and the rain adds drama).

**Best for families with kids:** Lonavala (2 hours from Mumbai, Karla Caves are sheltered, Imagica is indoor), Nainital (lake boating, Eco Cave Gardens are covered), and Mussoorie (walkable Mall Road, Gun Hill ropeway).

**Skip with caution:** Wayanad's deep valleys (landslide-prone), Uttarakhand pilgrimage routes during red-alert days, and North Sikkim's Lachung-Lachen stretch. The IMD issues daily nowcasts — check 24 hours before any hill drive.

## Practical Tips for NRIs

**Flights:** Fares to India peak in June and July. If you haven't booked yet, mid-August through September offers the best monsoon experience at lower fares — and this year's El Niño means August could be drier than usual in many regions.

**Health:** Pack ORS sachets, a pediatric first-aid kit if traveling with kids, and DEET-free mosquito repellent. Dengue cases peak July through October across India. Drink only sealed bottled water — leptospirosis risk spikes in Kerala and the Konkan belt during monsoon.

**Insurance:** Buy travel insurance that covers weather cancellations. A single washed-out domestic connection can cascade into missed international flights.

**What to wear:** Leave the white sneakers at home. Waterproof sandals, quick-dry clothing, and a compact rain jacket beat umbrellas in Indian monsoon winds.

## The Bottom Line

The monsoon is India at its most alive — green hills, empty temples, street food in the rain. An El Niño year doesn't cancel any of that, but it does mean the usual destinations may not deliver on cue. Build flexibility into your dates, watch the IMD forecast, and book cancellable hotels. The payoff — experiencing India without the tourist crush — is worth the weather gamble."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Monsoon Just Arrived — and El Niño Means NRIs Need a Different Playbook This Summer",
    "subheadline": "The southwest monsoon hit Kerala today, but a developing El Niño could make this season drier in the west and wilder on the coasts. Here's where to go and what to watch.",
    "slug": make_slug("india-monsoon-2026-el-nino-nri-travel-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Millions of NRIs plan summer India trips around the monsoon window. This year's El Niño disruption means the usual playbook — Lonavala waterfalls, Kerala houseboats, Coorg coffee estates — needs adjusting. Timing, destination choice, and flexible bookings matter more than usual.",
    "tags": ["travel", "india", "monsoon", "el nino", "summer travel", "nri guide"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/planning-a-monsoon-trip-heres-how-el-ni%C3%B1o-could-affect-your-travel-plans"},
        {"name": "StayVista", "url": "https://www.stayvista.com/blog/monsoon-travel-with-kids-india/"},
        {"name": "PIB India", "url": "https://www.pib.gov.in/"},
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37013427/pexels-photo-37013427.jpeg",
    "body": art2_body,
}

# ─────────────────────────────────────────────────────────
# ARTICLE 3: France Drops Transit Visa for Indians
# ─────────────────────────────────────────────────────────

art3_body = """Since April 10, Indian passport holders no longer need a transit visa to connect through French airports. The change, announced during President Macron's February visit to India and formalized by decree on April 9, removes one of the most annoying friction points in the NRI travel toolkit — and it could reshape how you route your next flight home.

## What Changed

Previously, Indian nationals connecting through Paris-CDG, Lyon, or any other French airport needed an Airport Transit Visa (ATV) even if they never left the international transit zone. The requirement applied to airside connections — meaning you'd need a separate visa just to walk from one gate to another. The ATV cost €80, required a consulate appointment, and took days to process.

That's gone. As of April 10, 2026, Indians can transit through French airports without any visa, joining citizens of most other major nations who've had this privilege for years.

## Why This Matters to NRIs

Paris-Charles de Gaulle is one of the world's busiest connecting hubs. Air France, along with its SkyTeam partners, routes tens of thousands of India-bound passengers through CDG every month. For NRIs on the US East Coast, CDG has always been a natural connection point for flights to Delhi, Mumbai, Hyderabad, and Bangalore — but the ATV requirement pushed many toward Dubai, Doha, or Istanbul instead.

With the transit visa gone, Air France's Paris connections become viable again. This is especially relevant right now: the Iran-Strait of Hormuz conflict has disrupted Gulf corridors, forcing many Middle Eastern carriers to reroute. NRIs already pivoting toward European hubs will find the CDG connection smoother than ever.

The math is simple. A JFK–CDG–DEL routing on Air France takes roughly 16 hours with a 2-hour connection. The same trip via Dubai takes 18–20 hours. Remove the visa hassle, and Paris wins on time, convenience, and increasingly on price too.

## The Limits

This is a transit-only exemption. If you want to step outside the airport — even for a quick baguette at the arrivals hall — you still need a Schengen visa. The change applies strictly to the international transit zone at French airports.

Also worth noting: 11 European countries, including France itself, have reintroduced temporary Schengen border checks in 2026 due to security concerns. These don't affect airside transit, but if you're planning a multi-country European trip after your India visit, carry your passport at every border — even train crossings.

## How to Use This

**Rebooking window:** If you have a summer India trip booked through Dubai or Doha and the Gulf disruptions have you worried, check Air France and partner fares through CDG. One-stop connections through Paris are now friction-free for Indian passports.

**Connecting flights:** Air France operates daily nonstops from JFK, SFO, LAX, ORD, and other major US cities to CDG. From CDG, it flies to Delhi, Mumbai, Bangalore, Chennai, and Hyderabad. KLM (via Amsterdam, which never required an ATV) and other SkyTeam partners expand the options further.

**What to carry:** Even though the ATV requirement is gone, airlines are still updating their systems. Carry a printout of the French government's April 9 decree notice in case of confusion at check-in. The Indian Embassy in Washington has also posted guidance on their site.

## The Bigger Context

The transit visa removal is part of a broader India-France diplomatic push under the "Special Global Strategic Partnership" framework. Macron and Modi announced the change during their February summit alongside increased defense cooperation and student exchange programs. For everyday NRIs, though, the practical impact is this: one fewer visa to worry about, one more routing option to India, and a meaningful alternative to Gulf hubs that are under pressure."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "France Killed the Transit Visa for Indians — and NRIs Rerouting Through Paris Just Got an Easier Ride",
    "subheadline": "Since April 10, Indian passports can connect through CDG without an Airport Transit Visa. With Gulf corridors still disrupted, Paris just became the most practical European gateway.",
    "slug": make_slug("france-transit-visa-removed-indians-paris-cdg-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The €80 Airport Transit Visa used to push NRIs toward Dubai and Doha for connections. Now that France dropped it, Air France's CDG hub competes directly — especially with Gulf routes disrupted by the Strait of Hormuz conflict.",
    "tags": ["travel", "visa", "france", "paris", "transit", "nri guide", "air france"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "VisaHQ", "url": "https://www.visahq.com/"},
        {"name": "iVisa", "url": "https://www.ivisa.com/"},
        {"name": "Envoy Global", "url": "https://envoyglobal.com/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/"},
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37579178/pexels-photo-37579178.jpeg",
    "body": art3_body,
}

# ─────────────────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone — {len(articles)} articles submitted at {now}")
