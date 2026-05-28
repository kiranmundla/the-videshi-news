#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-28 18:00 UTC run
Publishes 3 travel articles targeting the Indian American diaspora.
"""
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
    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 1: India's New Baggage Rules — NRI Duty-Free Allowance
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Rewrote Its Baggage Rules — and Every NRI Going Home This Summer Should Know",
        "subheadline": "The duty-free allowance jumped 50% to ₹75,000, laptops are now explicitly free, and customs duty on excess goods dropped to 10%. Here's what changed and what it means for your next trip.",
        "slug": make_slug("india-baggage-rules-2026-nri-duty-free-laptop"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Every NRI returning home can now bring more gifts, electronics, and personal goods without customs hassles — the first update in a decade directly benefits the 4.5 million Indian Americans who fly home regularly.",
        "tags": ["travel", "customs", "baggage rules", "duty-free", "NRI"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TripZilla India", "url": "https://www.tripzilla.in/travel/india/indias-new-baggage-rules-2026-higher-duty-free-limits-and-digital-declarations-explained/26037"},
            {"name": "CBIC / Tax Guru", "url": "https://taxguru.in/custom-duty/cbic-notifies-baggage-rules-2026.html"},
            {"name": "FlapOne Aviation News", "url": "https://flapone.com/budget-2026-duty-free-baggage-limits/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3693017/pexels-photo-3693017.jpeg",
        "image_caption": "Airport baggage claim area — India's new customs rules make the experience smoother for returning NRIs",
        "body": """For years, the ritual of packing for India involved a mental spreadsheet: How much can I bring? Will they stop me at customs? Is the laptop going to be a problem again?

India's Central Board of Indirect Taxes and Customs has finally rewritten the rules — the first overhaul in a decade — and the changes are unambiguously good for NRIs.

## The headline number: ₹75,000 duty-free

The general duty-free allowance for Indian residents and people of Indian origin returning from abroad has jumped from ₹50,000 to ₹75,000. That's a 50% increase, and while it still won't cover the latest iPhone and a MacBook together, it accounts for a decade of inflation that the 2016 rules had quietly ignored.

The breakdown is straightforward. Indian residents, NRIs, OCI cardholders, and foreign nationals on long-term visas (work permits, student visas) all get the ₹75,000 ceiling. Foreign tourists get ₹25,000, up from ₹15,000. If you're entering India by land — say, from Nepal or Bangladesh — the general allowance doesn't apply. Air and sea arrivals only.

## Your laptop is finally, officially free

This one matters. One laptop or notebook per passenger aged 18 or older is now explicitly exempt from duty, and it does not count toward your ₹75,000 limit. Previously, whether your laptop attracted customs attention depended on the officer's mood and your gate assignment. That ambiguity is gone.

For students, remote workers, and the large number of NRIs who carry a work laptop plus personal devices, this removes a genuine pain point. Your laptop is your laptop — customs has no business with it.

## Jewelry rules: weight, not value

The old jewelry rules were a thicket of weight-and-value combinations that confused everyone, including customs officers. The new rules simplify radically: it's weight only.

Indian residents and OCIs returning after more than a year abroad can bring gold jewelry duty-free — up to 40 grams for women, 20 grams for others. No more arguments about market valuation at the counter.

## Excess goods? The duty rate dropped too

If you bring more than your allowance covers, the customs duty on excess personal goods has been cut from 20% to a flat 10%. So if you're carrying goods worth ₹1 lakh, you pay duty only on the ₹25,000 above the limit — that's ₹2,500 plus a small social welfare surcharge. The math is friendlier than it's ever been.

The flat rate doesn't apply to alcohol, tobacco, automobiles, or goods requiring special import licenses. Those remain on their own schedules.

## Moving back to India? The transfer-of-residence rules improved

NRIs relocating permanently to India can now bring household goods worth up to ₹7.5 lakh duty-free, depending on time spent abroad. The allowed items list has been modernized — air fryers, robot vacuum cleaners, and microwave ovens are now explicitly included. The 2016 list was written when half these appliances didn't exist.

Temporary import provisions have also been formalized. Professional photographers, musicians, and business travelers with specialized equipment can get customs certificates for gear they plan to take back. No more improvising at the Red Channel.

## Digital declarations are here

The new rules lay the groundwork for electronic baggage declarations, replacing the paper forms that have been a fixture of Indian arrivals since the pre-internet era. The shift toward digital processing is designed to handle the sheer volume — India expects international passenger traffic to hit 350 million annually by 2028.

## What this means for NRIs this summer

The practical impact is immediate. If you're flying home for summer vacation, a wedding, or a family visit, you can carry more without stress. The laptop exemption alone eliminates one of the most common customs encounters. The lower duty rate on excess goods means even if you over-pack, the financial hit is manageable.

For NRIs who've been debating whether to ship household items or carry them, the higher transfer-of-residence limits tip the calculation further toward packing. And the weight-based jewelry rules mean one fewer argument at the airport.

The rules took effect on February 2, 2026. If you've flown to India since then and didn't know about the changes, you may have already benefited without realizing it. If you haven't flown yet this year, now you know the math before you start packing."""
    },

    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 2: Fairmont Udaipur + India's Luxury Hotel Boom
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Luxury Hotel Boom Is Rewriting the NRI Destination Wedding Playbook",
        "subheadline": "Fairmont just opened an 18-acre palace in Udaipur with 327 rooms and 1.4 lakh sq ft of event space. Meanwhile, Marriott and Fern have opened 50 hotels across 43 Indian cities in six months. The NRI homecoming stay is getting a serious upgrade.",
        "slug": make_slug("india-luxury-hotel-boom-fairmont-udaipur-marriott-nri-weddings"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI destination weddings are a $3B+ industry, and the hotel infrastructure finally matches the demand. Marriott Bonvoy points now work in 43 Indian cities, and Fairmont Udaipur is purpose-built for the diaspora celebration market.",
        "tags": ["travel", "hotels", "weddings", "luxury", "NRI", "Marriott", "Fairmont"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/stay/indias-newest-palace-hotel-is-a-lesson-in-crafty-opulence"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/marriott-international-and-the-fern-celebrate-major-series-by-marriott-growth/"},
            {"name": "Hospitality Net", "url": "https://www.hospitalitynet.org/news/4125123.html"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Evening_view%2C_City_Palace%2C_Udaipur.jpg",
        "image_caption": "Udaipur's City Palace at dusk — the city's newest luxury hotel, Fairmont Udaipur Palace, rises on 18 acres in the Aravalli hills",
        "body": """There's a certain audacity to building a palace from scratch in a city that already has several. But Fairmont — Accor's luxury arm — did exactly that in Udaipur, and the result is reshaping what NRI families can expect when they bring a wedding home to India.

## Fairmont Udaipur: Built for the big Indian wedding

Fairmont Udaipur Palace opened on 18 acres in the Aravalli hills, the quieter side of a city that most NRIs associate with Lake Pichola and the Oberoi Udaivilas. The scale is deliberate: 327 rooms and suites across three themed wings — Surya Mahal, Chandra Mahal, and Agni Mahal — with 1.4 lakh square feet of event space spread across seven venues.

The property isn't pretending to be a heritage conversion. It's a new-build palace designed specifically for large-format celebrations — the chandelier-lit Jewel ballroom, the column-lined Mehfil courtyard, the stepwell-inspired Chand Baori. Lawns and terraces extend the capacity outdoors. For NRI families who've spent months coordinating a 500-person wedding across three time zones, this is infrastructure that finally matches the ambition.

Rooms range from standard Fairmonts to suites with private plunge pools, marble dining tables, and bejewelled roll-top tubs. Eight dining concepts are already operational, with two more planned. The butler service is reported as genuinely attentive rather than performative — a distinction that matters when your extended family is scattered across three wings and someone's uncle needs a shawl at dinner.

## Marriott and Fern: 50 hotels in six months

While Fairmont targets the ultra-premium tier, Marriott International and The Fern Hotels & Resorts have been quietly executing the largest mid-to-upper-segment hotel expansion India has seen in years. Their "Series by Marriott" brand launched in India in November 2025. By May 2026 — less than six months — they had signed 75 hotels and opened 50, adding over 3,556 rooms across 43 Indian cities.

For NRIs, this matters more than any single palace opening. The 43 cities include not just Mumbai, Delhi, and Goa, but Chandrapur, Bhilwara, and other tier-2 towns that have historically offered exactly two hotel options: a decent one and a questionable one. If your hometown is a three-hour drive from the nearest international airport, the Marriott-Fern partnership means your parents' guests at a family function might actually have a comfortable place to stay.

Crucially, these properties are on Marriott Bonvoy. Points earned on business trips in Chicago or London now redeem in cities across India's heartland. For the NRI who racks up hotel nights in the US and has always been frustrated by the limited Bonvoy footprint in India, 43 cities is a material change.

## Accor's eco-luxury bet: Mantis near Nagarhole

On the other end of the spectrum, Accor has signed a property under its conservation-focused Mantis brand near Nagarhole Tiger Reserve in Karnataka. The 31-key eco-retreat, developed with Macs Max Private Limited, is scheduled to open in 2028 and will emphasize wildlife experiences and sustainable practices.

For NRIs interested in India beyond cities and palaces — the growing segment that wants a responsible wildlife experience rather than another beach resort — Mantis Nagarhole represents a category that barely existed in India five years ago. Eco-luxury with an international brand's operational standards, in a part of Karnataka that most Americans couldn't place on a map but that offers some of the best tiger and elephant sighting odds in the world.

## What's driving the boom

Three forces are converging. First, India's domestic leisure travel market has exploded, with rising incomes creating demand that existing hotel stock couldn't absorb. Second, NRI destination weddings have become a structural revenue stream — an estimated $3 billion annually — and hotel brands are building explicitly for that market. Third, the aviation disruptions from the Iran conflict have paradoxically boosted domestic tourism, as Indian families choose Rajasthan over Dubai when international flights are expensive and unreliable.

The result is an India where the gap between "international-standard hotel" and "local accommodation" is closing faster than it has in decades. For NRIs who remember the days when a Hyderabad visit meant choosing between a Taj and a three-star with intermittent hot water, the shift is tangible.

## The NRI calculus

Fairmont Udaipur Palace rooms start at approximately ₹25,000 per night (about $300), positioning it in the same range as established Udaipur luxury properties. Marriott-Fern Series properties target the ₹4,000-8,000 range ($50-100), which is the sweet spot for NRI families booking blocks of rooms for events.

Both segments are growing because NRI spending patterns in India have changed. The generation that once sent money home now flies home with a wedding planner, a photographer, and expectations shaped by American hospitality standards. India's hotel industry is finally building for that customer."""
    },

    # ─────────────────────────────────────────────────────────────────────
    # ARTICLE 3: British Airways India Expansion
    # ─────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "British Airways Is Doubling Down on India While Everyone Else Pulls Back — and the UK Diaspora Stands to Gain",
        "subheadline": "Twice-daily Bengaluru flights from June, up to three daily Delhis, and capacity shifted from the Gulf to South Asia. BA is making its biggest India bet in years, just as Air India retreats.",
        "slug": make_slug("british-airways-india-expansion-uk-diaspora-bengaluru-delhi"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With 1.5 million people of Indian origin in the UK and strong VFR traffic, BA's India expansion directly serves the UK-based diaspora. Twice-daily Bengaluru also opens one-stop US connections via Heathrow for NRIs routing through London.",
        "tags": ["travel", "airlines", "British Airways", "UK", "NRI", "Bengaluru", "Delhi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/british-airways-to-ramp-up-india-uk-summer-2026-flights-as-demand-soars/"},
            {"name": "British Airways Media Centre", "url": "https://mediacentre.britishairways.com/pressrelease/details/86/2025-338/13998"},
            {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/british-airways-plans-additional-london-delhi-flight-in-2026/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9015530/pexels-photo-9015530.jpeg",
        "image_caption": "A British Airways aircraft in flight — the airline is making its biggest India capacity push in years",
        "body": """While Air India slashes 22% of domestic flights and IndiGo trims international capacity, British Airways is moving in the opposite direction. The airline's summer 2026 schedule for India is its most aggressive in years — more frequencies, larger aircraft, and a deliberate reallocation of widebody jets from the Gulf to South Asian routes.

For the 1.5 million people of Indian origin living in the UK, and for US-based NRIs who route through London, the expansion is more than a scheduling footnote. It's a structural shift in how the India-UK corridor operates.

## Bengaluru goes twice-daily from June

The headline move is Bengaluru. From June 2026, British Airways will operate twice-daily flights between London Heathrow and Kempegowda International Airport, making BLR one of just three Indian cities — alongside Delhi and Mumbai — with that frequency. The route will use a mix of Boeing 787-8 and 787-9 aircraft, with BA's newer cabin products on selected services.

The doubling matters for specific reasons. Bengaluru's tech sector generates enormous corporate traffic to London, but the city's outbound leisure market has also matured. Families in Karnataka, Tamil Nadu, and Andhra Pradesh who previously flew via Mumbai or Delhi to reach Heathrow now have direct options at competitive times. The twice-daily schedule also creates same-day connections to major US and European cities — a practical improvement for anyone booking onward flights.

## Delhi: up to three daily flights

On the trunk Delhi-London route, BA is adding capacity to reach periods with three daily services during peak summer. Mumbai gets extra rotations around high-demand dates, though a brief frequency reduction is planned for May due to operational adjustments.

Three daily Delhis from a single carrier is unusual for the India-UK corridor. It gives travelers real schedule flexibility — overnight departures, daytime options, and enough seats to prevent the price spikes that typically accompany peak-season scarcity on the route.

## Hyderabad and South India reinforced

Beyond the metros, BA is strengthening Hyderabad, where demand from IT professionals, students, and family travelers has grown steadily. The airline currently operates 56 weekly flights to five Indian cities, and Hyderabad-specific frequency increases are being finalized for the summer timetable.

The South India emphasis is strategic. Telangana, Andhra Pradesh, Karnataka, and Tamil Nadu together represent one of India's fastest-growing outbound travel markets, and BA is positioning Bengaluru and Hyderabad as dual gateways to serve them. For UK-based NRIs with roots in the south — a substantial community in London, Birmingham, and Leicester — this means fewer three-leg journeys home.

## Gulf capacity redirected to India

The expansion isn't coming from new aircraft. BA is redeploying widebody capacity away from select Middle East routes, where the Iran conflict has disrupted operations and depressed demand. India and East Africa are the primary beneficiaries.

This is a calculated bet. The Gulf routes that BA is de-emphasizing served a different passenger mix — business travelers and Gulf-based expatriates. India's VFR traffic, by contrast, is structurally resilient. Families visit regardless of economic cycles, students fly twice a year, and the wedding-season spike is predictable. BA is trading volatility for reliability.

## Club Suite coming to India routes

For premium travelers, BA has confirmed that its latest Club Suite business class product — featuring direct aisle access, a door for privacy, and an 18.5-inch screen — will roll out on selected India routes by late 2026. The current Club World product on India flights is widely regarded as dated, so the upgrade addresses a competitive gap against Emirates, Qatar Airways, and Singapore Airlines.

Economy and premium economy cabins are also getting refreshed interiors, improved catering, and expanded digital services. The overall product positioning suggests BA sees the India-UK route not just as a volume play but as a market where premium demand justifies investment.

## What it means for NRIs

For UK-based Indians, the math is simple: more flights mean more choice, more competition, and eventually better prices. Twice-daily Bengaluru alone transforms the options for anyone in the Midlands or North who connects through Heathrow.

For US-based NRIs, the indirect benefit is real. London Heathrow is the world's busiest international hub, and BA's expanded India frequencies create tighter connections from US cities. If you're flying from JFK, Boston, or Chicago to Bengaluru, the BA one-stop via LHR is now a credible alternative to Gulf carrier routings — especially if you hold BA or Oneworld status.

The timing is pointed. Air India's summer cuts, driven by jet fuel costs that have nearly doubled, have created gaps in the India-UK schedule. BA is filling them with an aggression that suggests it views India not as a supplementary market but as a core long-haul priority. For the diaspora on both sides of the Atlantic, that's competition working exactly as it should."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
