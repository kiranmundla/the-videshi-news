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
        "headline": "India's Newest Mega Airport Opens Tomorrow — and NRIs Finally Get a Faster Route to the Taj Mahal",
        "subheadline": "Noida International Airport launches commercial flights on June 15 with 140 weekly departures, a redBus intercity partnership, and a plan to become Delhi's pressure valve. International routes are expected by year-end.",
        "slug": make_slug("noida-international-airport-jewar-launch-nri-taj-mahal"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting the Delhi-NCR region now have a third airport option that halves travel time to Agra and the Taj Mahal, relieves Delhi IGI congestion, and will add international routes later in 2026 — a direct upgrade for anyone flying home to UP or Rajasthan.",
        "tags": ["travel", "airports", "noida", "infrastructure", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/noida-airport-to-handle-40-daily-flights-by-july-international-services-to-start-later-this-year/article69680123.ece"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/11/noida-international-airport-aircraft-turnaround-trial/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/noida-airport-partners-with-redbus-for-intercity-connectivity"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/crc-group-maiden-lucknow-noida-flight/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19190599/pexels-photo-19190599.jpeg",
        "image_caption": "Exterior view of a modern airport terminal with a curved roof design",
        "image_attribution": "Pexels",
        "body": """India's third airport in the National Capital Region opens for commercial flights on June 15, and the timing could not be better for the millions of NRIs who dread the Delhi IGI experience every summer.

Noida International Airport — located at Jewar along the Yamuna Expressway in Uttar Pradesh — will welcome its maiden arrival at 8:05 AM on Sunday: an IndiGo flight from Lucknow carrying 75 of Noida's most prominent business families. By July, the airport expects to handle 40 to 42 daily flights connecting 15 domestic destinations.

## What launches on day one

IndiGo will be the airport's anchor carrier, operating 126 weekly flights from the start. Akasa Air adds another 14 weekly departures. Together, that is 140 weekly flights connecting Noida to metros like Bengaluru, Hyderabad, and Mumbai, along with tier-2 cities including Amritsar, Chandigarh, Dharamshala, Jaipur, Lucknow, and Srinagar.

Air India Express, which had been expected at launch, pulled out in a cost-cutting move — leaving it as the notable absence. Air India's mainline operations are also not part of the initial rollout, though the airport says discussions with additional carriers continue.

## The numbers behind the ambition

Phase 1 opens with a single runway and passenger terminal built at a cost of ₹11,200 crore, with capacity for 12 million passengers a year. The full buildout envisions 70 million passengers annually — enough to rival the busiest airports in Asia.

The airport is operated by Yamuna International Airport Private Limited, a subsidiary of Zurich Airport International. It has been marketed as India's first net-zero greenfield airport, a claim that will face scrutiny as operations scale, but signals the kind of infrastructure India is betting on.

International flights are expected to begin later in 2026. Foreign carriers have reportedly expressed interest, with Zurich and Dubai mentioned as possible early international destinations.

## Why NRIs should pay attention

For the Indian American diaspora, Noida International Airport solves two persistent headaches.

First, Delhi's Indira Gandhi International Airport is chronically congested. At peak summer travel season, immigration queues at IGI can stretch past two hours. A third NCR airport — after IGI and the much smaller Hindon — distributes that pressure.

Second, Jewar's location along the Yamuna Expressway puts the Taj Mahal roughly two hours away by car, compared to nearly four hours from Delhi. For NRIs planning family trips to Agra — one of the most common itineraries for visiting relatives from the US — this is a meaningful upgrade.

## The redBus connection

In a first-of-its-kind partnership for an Indian airport, Noida International has tied up with redBus to offer direct intercity bus connections to more than 20 destinations across North India. Passengers can book buses to Agra, Mathura, Lucknow, Dehradun, and Chandigarh through the redBus platform, with GPS-tracked, air-conditioned coaches departing from a dedicated staging area at the terminal.

For NRIs landing from the US who need to reach family in Uttar Pradesh, Uttarakhand, or Rajasthan, this integrated bus network fills a gap that no Indian airport has addressed before. It is the kind of last-mile thinking that makes an airport useful beyond its runway.

## The cost question

There is a catch. The Airport Economic Regulatory Authority has approved a ₹490 user development fee for domestic departing passengers — higher than what travelers pay at Delhi IGI. Airport CEO Nitu Samra has defended the fee as reasonable for a greenfield facility, arguing that passengers will choose between the two airports based on convenience and timing rather than fee alone.

Whether that holds depends on how quickly the airport builds its route network and whether international carriers follow through on their interest. For now, Noida International Airport is a promising addition to India's aviation map — and for NRIs flying into the Delhi region, it is worth watching the route announcements closely.

The first flight lands Sunday morning. The real test begins the Monday after."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's Maharaja Lounge at SFO Is Its First Overseas Lounge Since the Tata Takeover",
        "subheadline": "The 3,300-square-foot lounge near Gate A features speakeasy-style cocktails, live Indian cooking stations, and a private first-class zone — a direct pitch to the Bay Area's 400,000-strong Indian diaspora.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-bay-area-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO is the primary international gateway for the Bay Area's massive Indian American population. The Maharaja Lounge is Air India's clearest signal yet that it is investing in the NRI travel corridor, not just the route — and it matters for anyone flying business or first class between California and India.",
        "tags": ["travel", "airlines", "air-india", "san-francisco", "lounges"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Points Guy", "url": "https://thepointsguy.com/airline/air-india-maharaja-lounge-sfo-opening/"},
            {"name": "Global Traveler", "url": "https://www.globaltravelerusa.com/air-india-opens-first-international-signature-lounge-at-sfo/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-opens-first-overseas-maharaja-lounge-at-san-francisco-airport/article69611234.ece"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/05/23/air-india-maharaja-lounge-sfo/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17083402/pexels-photo-17083402.jpeg",
        "image_caption": "San Francisco International Airport terminal illuminated at night",
        "image_attribution": "Pexels",
        "body": """For years, flying Air India out of San Francisco meant the same uninspiring routine: a cramped gate area, maybe a third-party lounge if you had the right credit card, and the lingering sense that India's flag carrier had given up trying to compete on experience. That is starting to change.

Air India opened its Maharaja Lounge at SFO's International Terminal on May 23 — the airline's first signature lounge outside India since the Tata Group acquired the carrier in January 2022. It is small at 3,300 square feet, but it is deliberate, and for Bay Area NRIs flying home on Air India, it represents a tangible upgrade to a corridor that handles roughly 65 weekly flights between North America and India.

https://www.instagram.com/p/DYoMlN9DeRB/

## Inside the lounge

Located near the A Gates in SFO's International Terminal, the Maharaja Lounge seats about 75 guests in the main area plus eight in a private first-class zone. The design, by hospitality firm Hirsch Bedner Associates, blends contemporary luxury with Indian heritage — champagne tones, ivory accents, deep red furniture, and art installations made from upcycled aircraft components.

The standout detail is the artwork: several pieces were created using pigments derived from Indian spices and botanicals, including turmeric, rose, and cinnamon, rather than traditional paint. It is the kind of touch that separates a lounge designed with intention from one furnished by committee.

## The food and drink

The dining program leans into Indian cuisine with rotating menus. On a recent visit, the buffet included dal Bukhara, chicken tikka masala, vegetable biryani, paneer moringa, and beet-and-fig sham savera kofta alongside grilled salmon. A cold spread featured fresh fruit, specialty dips — tikka achari and mango habanero — and a modernized gajar ka halwa served in bite-sized tart form.

The Aviator's Bar is the lounge's centerpiece: a separate speakeasy-style space with bar stools modeled after seating from Air India's 1930s-era aircraft. The cocktail list includes the Maharaja Manhattan (with black pepper) and the Limitless (gin, rose, hibiscus, saffron). Archival imagery, vintage postcards, and model aircraft line the walls.

## Who gets in

Access is limited to Air India first and business class passengers, eligible Star Alliance premium travelers, and Maharaja Club Gold and Platinum members. The private first-class zone offers a la carte dining and a reserved selection of cognac and whiskey.

What the lounge does not have: showers — a notable omission for a long-haul international lounge. But the fast Wi-Fi, USB-C charging throughout, and natural light from tarmac-facing windows make it a comfortable preflight space.

## What it signals for NRIs

The Maharaja Lounge is not just a lounge; it is a statement about where Air India is investing. San Francisco was chosen deliberately — it is the airline's most important North American gateway, serving the Bay Area's estimated 400,000-strong Indian community and the tech corridor that generates enormous premium demand on the SFO-Delhi and SFO-Mumbai routes.

The lounge follows the flagship Maharaja Lounge that opened at Delhi in February. Campbell Wilson, Air India's CEO, has said the carrier plans a series of signature lounges across its network, with North America as a key pillar.

For the NRI traveler who has watched Air India's decline over the past decade with a mix of nostalgia and frustration, this is the first physical evidence at an American airport that the Tata transformation is real. It is not enough on its own — Air India still needs to fix on-time performance, aging aircraft on some routes, and inconsistent service — but a lounge this considered, at this airport, is a start.

The next time you fly out of SFO to Delhi or Mumbai, walk past the Air France lounge, take the escalators up, and see for yourself."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Gulf Airlines Are Offering Free Insurance and Repatriation — Here's What NRIs Need to Know",
        "subheadline": "Etihad is giving every passenger 15 days of free medical coverage. Emirates has pledged to fly you home if things go sideways. The reason: Gulf travel confidence has cratered, and India is the most exposed market.",
        "slug": make_slug("gulf-airlines-free-insurance-repatriation-nri-dubai-transit"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The majority of NRIs flying between the US and India transit through Dubai or Abu Dhabi. With the Gulf crisis reshaping insurance coverage and airspace access, understanding these new airline protections — and their limits — is essential for anyone with summer travel booked through the region.",
        "tags": ["travel", "airlines", "dubai", "insurance", "gulf-crisis"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/pih7ddujykwo/"},
            {"name": "LinkedIn / Manoj Keshwar", "url": "https://www.linkedin.com/pulse/foreign-air-travel-risk-what-do-manoj-keshwar-d0vyf/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/american-travelers-are-trading-tuscany-for-tacoma-this-summer-thanks-to-soaring-airfares-eb3b2e0b"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/middle-east-tourism-collapse-aviation-crises-2026/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20594766/pexels-photo-20594766.jpeg",
        "image_caption": "Emirates airplane on the tarmac at Dubai International Airport",
        "image_attribution": "Pexels",
        "body": """If you are an NRI with summer flights booked through Dubai, Abu Dhabi, or Doha, the airlines want you to know they have your back. Whether you believe them is another matter.

Etihad Airways has rolled out free 15-day medical travel insurance for all passengers — automatic, no opt-in required. Emirates has gone further with a "Fly You Home" repatriation guarantee, pledging to get passengers back to their origin if regional disruptions strand them. Qatar Airways has maintained flexible rerouting policies.

These are not random acts of generosity. They are emergency responses to a crisis that has cratered Gulf tourism and shaken the confidence of millions of travelers who depend on Dubai and Abu Dhabi as transit hubs.

## What is actually happening

The Hormuz Strait crisis that began escalating in early 2026 has disrupted airspace across Iran, Iraq, Kuwait, Bahrain, and Syria. Over 46,000 flights were cancelled within a two-week stretch. Dubai International Airport — normally the world's busiest for international passengers — has been operating at roughly 53 percent capacity. Doha's Hamad International dropped to 35 percent.

UAE hotel occupancy has fallen to approximately 33 percent, down from the historic highs that Dubai typically enjoys during its peak tourism cycles. Multiple governments, including Australia, have issued Level 3 or Level 4 travel advisories for parts of the region. The US State Department has warned that "Do Not Travel" advisories apply to transits and layovers, not just final destinations.

For India — the single largest passenger volume market transiting through Gulf hubs — the impact is enormous.

## Why NRIs are most exposed

The geography of the India-US air corridor makes Gulf transit almost unavoidable for millions of NRIs. While nonstop flights exist on routes like SFO-Delhi, JFK-Mumbai, and ORD-Bengaluru, they are expensive and limited in capacity. The majority of Indian Americans flying home — especially those headed to tier-2 cities — route through Emirates via Dubai, Etihad via Abu Dhabi, or Qatar Airways via Doha.

That means NRIs are disproportionately affected by three converging problems:

**Insurance gaps.** Standard travel insurance policies are increasingly excluding the Gulf region from coverage. If your flight is disrupted during a layover in Dubai, your US-purchased travel insurance may not cover rebooking, accommodation, or medical expenses incurred in the transit country. Etihad's free insurance is a patch, not a solution — 15 days of medical coverage does not address trip disruption or cancellation.

**Airfare inflation.** Flights between the US and India are up 27 percent year-over-year. Rerouting around Gulf airspace adds fuel costs and flight time. Airlines are passing those costs directly to passengers, and the cheapest routes — which invariably go through the Gulf — are now the ones with the most uncertainty.

**Rebooking chaos.** When airspace closures hit, they hit fast. Passengers have reported being stranded in Dubai for 48 to 72 hours with minimal airline support, especially on budget carriers that lack the operational depth to reroute quickly.

## What to do before you fly

For NRIs with summer travel through the Gulf, the practical steps are straightforward:

**Read your insurance policy now** — not at the gate. Check whether your travel insurance explicitly excludes the Gulf region, conflict-related disruptions, or transit country coverage. If it does, consider supplemental coverage or a policy upgrade.

**Ask your airline about waiver windows.** Most Gulf carriers are currently offering flexible rebooking. Get the terms in writing. Know the deadline before the flexibility expires.

**Have an alternate routing in mind.** Direct flights from the US to India exist on Air India, United, and American Airlines. They cost more, but they bypass the Gulf entirely. If your risk tolerance is low, this is the moment to pay the premium.

**Monitor advisories actively.** The State Department, MEA, and individual airline policy pages are updating every 48 to 72 hours. Set alerts rather than checking passively.

**Avoid non-refundable bookings.** This is not the summer to lock in a non-refundable fare through Dubai to save a few hundred dollars. The savings evaporate the moment your flight is cancelled.

## The bigger picture

Gulf airlines offering free insurance and repatriation guarantees is unprecedented — and it tells you exactly how serious the demand collapse is. These carriers built their business models on being the world's most efficient transit hubs. When they start giving away insurance to get people on planes, the confidence problem is real.

For NRIs, the practical takeaway is simple: the Gulf route is still operational, but it carries more uncertainty than it has in years. Price your risk accordingly, carry the right insurance, and know your alternatives. The airlines are trying to reassure you. Whether they can deliver on those promises during a genuine disruption remains the open question."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
