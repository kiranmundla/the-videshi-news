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
        "headline": "Air France Is Flooding India Routes With Extra Summer Flights — and Its Best Cabin Is Coming to SFO",
        "subheadline": "Additional frequencies to Mumbai, Delhi, and Bengaluru in June and July, plus the La Première suite lands in San Francisco for the first time.",
        "slug": make_slug("air-france-extra-summer-flights-india-la-premiere-sfo-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs connecting through Paris CDG get more flexibility on India-bound summer trips, and Bay Area travelers finally get Air France's top cabin on the SFO route.",
        "tags": ["travel", "airlines", "air-france", "flights", "summer-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-france-and-klm-expand-big-global-network/"},
            {"name": "Air France Corporate", "url": "https://corporate.airfrance.com"},
            {"name": "Travel Market Report", "url": "https://www.travelmarketreport.com/articles/Air-France-Summer-2026-Schedule-Features-60-Weekly-Flights-from-Canada"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/12759005/pexels-photo-12759005.jpeg",
        "body": """Air France is deploying extra flights and bigger aircraft across its India network this summer, a move that hands NRIs connecting through Paris Charles de Gaulle some of the best scheduling flexibility they have had in years on the Europe-to-India corridor.

The French flag carrier will operate additional long-haul frequencies from CDG to Mumbai, Delhi, and Bengaluru during June and July. The specifics: extra Mumbai flights on June 30 and July 7, Delhi on July 1 and 5, and Bengaluru on July 3 and 10. These sit on top of the regular schedule, which already runs daily or near-daily on all three routes.

## Bigger Planes, More Seats

The extra frequencies are only half the story. Since March, Air France has quietly upgauged aircraft on existing services to Bangkok, Singapore, Delhi, Mumbai, Shanghai, Tokyo, and Osaka — swapping in higher-capacity widebodies that add hundreds of seats per week without requiring new airport slots. The airline confirmed the larger aircraft will continue through the summer season.

For NRIs flying out of the US East Coast or West Coast, the implications are concrete. CDG has long been a viable one-stop option to reach Indian cities, especially for those who prefer European carriers over Gulf airline routings. More seats and more flights mean better last-minute availability during peak summer travel — the window when fare prices on India routes historically spike 30-40% above shoulder-season averages.

## La Première Arrives in San Francisco

The real surprise for Bay Area NRIs: Air France is introducing its new La Première suite — the airline's top-of-the-line first-class cabin — on the Paris-San Francisco route this summer. The suite, which features a fully enclosed private space with a closing door, lie-flat bed, and dedicated dining service, was previously available only on routes to New York-JFK, Los Angeles, Miami, Singapore, and Tokyo-Haneda.

SFO is home to one of the largest Indian diaspora populations in the United States. The addition of La Première on this route gives premium travelers a genuine alternative to the business-class-only options that dominate US-India nonstops. A CDG connection adds two to three hours versus a direct SFO-DEL flight, but the cabin product is in a different league entirely.

## Free Wi-Fi Rollout Accelerating

Air France is also pushing hard on connectivity. By the end of March, 40% of its fleet was already equipped with free ultra-high-speed Wi-Fi, and the airline aims to cover virtually the entire fleet by year-end. For long-haul passengers — particularly business travelers splitting time between US and India offices — in-flight connectivity has shifted from a perk to a requirement.

## What NRIs Should Know

The practical takeaway: if you are booking summer travel to India through Europe, Air France's expanded India schedule makes CDG one of the strongest hub options available right now. The combination of extra flights, upgraded aircraft, and the transit visa exemption that France extended to Indian passport holders in April means fewer logistical headaches than in years past. Indian nationals transiting through French airports no longer need an Airport Transit Visa — a policy change that removes what was previously one of the biggest friction points of routing through Paris.

KLM, Air France's partner airline, is simultaneously adding 17 extra frequencies between Amsterdam and Nairobi, but the India-specific capacity boost is clearly where the group sees the strongest demand signal this summer."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Cut Visa-Free Stays in Half — What NRIs Need to Know Before Booking",
        "subheadline": "The visa-free window drops from 60 days to 30 for travelers from 93 countries, including India. Digital nomads and extended-stay visitors are hit hardest.",
        "slug": make_slug("thailand-visa-free-cut-60-to-30-days-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Thailand is one of the most popular short-haul destinations for NRIs — the halved visa-free window forces rethinking trip lengths, especially for retirees and remote workers who treated Bangkok as a base.",
        "tags": ["travel", "visa", "thailand", "nri-travel", "digital-nomads"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/5c890ltalem6/"},
            {"name": "Wikipedia - Visa Requirements for Indian Citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/20889615/pexels-photo-20889615.jpeg",
        "body": """Thailand has slashed its visa-free stay period from 60 days to 30 days for travelers from 93 countries — India included — in a policy shift that will reshape how NRIs plan trips to one of Southeast Asia's most visited destinations.

The change, which takes effect 15 days after publication in Thailand's Royal Gazette, does not eliminate visa-free entry. It simply halves the window. A two-week beach holiday in Phuket or a week exploring Chiang Mai temples remains entirely unaffected. But the reform lands squarely on a category of travelers that has grown sharply in the post-pandemic era: digital nomads, remote workers, retirees, and extended-stay holidaymakers who relied on the 60-day visa-free window as a de facto residence permit.

## Why Thailand Is Tightening

Thai authorities have been explicit about the reasoning. Reports of foreign nationals using visa-free entry to work, run businesses, or settle semi-permanently without proper documentation have increased pressure on immigration agencies. The 60-day window, originally introduced to boost tourism recovery, created what officials describe as "regulatory ambiguity" — blurring the line between a tourist visit and an informal residency arrangement.

The shorter stay period creates a clearer distinction. Tourists on standard holidays will barely notice. But anyone planning a longer stay will now need to apply for a formal visa — a Tourist Visa (TR), a Non-Immigrant visa, or Thailand's dedicated Digital Nomad Visa (DTV), which allows stays of up to 180 days.

## The NRI Angle

Thailand is consistently among the top five international destinations for Indian travelers. Affordable direct flights from Delhi, Mumbai, Bengaluru, and Kolkata — plus the country's deep familiarity with Indian food preferences and its well-established medical tourism infrastructure — have made it a default choice for NRI families, retirees visiting from the US, and young professionals taking extended breaks.

The 60-day window was particularly popular with NRIs who split time between the US and India. A common pattern: fly from the US to Bangkok, spend three to four weeks in Thailand, then continue to India for family visits. The 30-day cap makes that sequencing tighter but not impossible — most NRIs spending a month in Thailand were already cutting it close.

The bigger impact falls on a smaller but growing group: Indian-origin remote workers and early retirees who had established semi-permanent routines in Bangkok, Chiang Mai, or the islands. For this cohort, the math changes. A proper visa application — with documentation, processing time, and potentially a consulate visit — adds friction that the visa-free system was designed to eliminate.

## What Changes in Practice

For standard NRI vacation trips of 7-14 days, nothing changes. You still fly in without a visa.

For trips of 15-30 days, you are now using most or all of your visa-free allowance. Plan return flights carefully — overstaying even by a day triggers fines and potential immigration complications.

For trips exceeding 30 days, you now need a visa. The Tourist Visa (TR) allows 60-day stays and is available through Thai embassies and consulates. Processing times vary but typically run one to two weeks.

For digital nomads and remote workers, the 2024-vintage Destination Thailand Visa (DTV) remains an option. It costs 10,000 Thai baht (roughly $280), allows 180-day stays, and is explicitly designed for people working remotely. It requires proof of employment or freelance income.

## The Broader Pattern

Thailand is not alone. Across Southeast Asia, countries that relaxed entry requirements during the pandemic recovery phase are now recalibrating. Indonesia tightened its visa-on-arrival enforcement in 2025. Malaysia extended India's visa-free access through December 2026 but has signaled it may not renew. The Philippines introduced a two-tier system — 14 days for standard Indian passport holders, 30 days for those with valid US, UK, or Schengen visas.

For NRIs, the lesson is straightforward: the era of casual, open-ended visa-free travel in Southeast Asia is narrowing. Check entry requirements before booking, not after."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Golden Chariot Is Back — and IRCTC Wants NRIs to See South India by Luxury Train",
        "subheadline": "India's premier luxury rail experience relaunches with redesigned cabins, three curated heritage itineraries, and a price cut that makes it accessible beyond the five-star crowd.",
        "slug": make_slug("golden-chariot-luxury-train-relaunch-south-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs visiting South India, the Golden Chariot offers a curated Bengaluru-Mysuru-Hampi-Goa circuit that eliminates the logistics of multi-city road travel — a persistent pain point for diaspora families trying to cover ground during limited India trips.",
        "tags": ["travel", "luxury-train", "south-india", "irctc", "heritage-tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/u3cdq67z3yd5/"},
            {"name": "Urban Acres", "url": "https://urbanacres.in/bengaluru-tourism-push-aims-to-broaden-rail-access/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Mysore_Palace_Morning.jpg/3840px-Mysore_Palace_Morning.jpg",
        "body": """IRCTC has relaunched the Golden Chariot luxury train for the 2026-27 tourist season, and the timing is deliberate. South India's tourism infrastructure has been expanding rapidly — new Vande Bharat connections, upgraded airports in Bengaluru and Kochi, a string of luxury hotel openings across Karnataka and Kerala — and the Golden Chariot is positioning itself as the thread that ties these destinations together into a single, seamless journey.

The train, one of only a handful of luxury rail experiences in India alongside the Maharajas' Express and the Palace on Wheels, has undergone a full interior renovation. Forty redesigned cabins accommodate up to 80 guests, with double-bed, twin-bed, and accessible configurations. Wi-Fi-enabled entertainment systems, smart TVs, enhanced furnishings, CCTV surveillance, and advanced fire safety systems bring the experience closer to a moving five-star hotel than a traditional rail journey.

## Three Itineraries, One Region

IRCTC is offering three curated routes, each designed to showcase a different slice of South India:

**Pride of Karnataka** (6 days): Bengaluru → Mysuru → Hampi → Goa. This is the flagship itinerary — covering the palatial grandeur of Mysuru, the UNESCO World Heritage ruins of Hampi, and the coastal relaxation of Goa in a single sweep. For NRIs with limited time in India, it solves a persistent logistical headache: covering these four cities by road or domestic flights typically requires three separate bookings, multiple check-ins, and at least one predawn departure.

**Jewels of the South** (multi-day): Mysuru → Mahabalipuram → Thanjavur → Cochin. This route goes deeper into Tamil Nadu and Kerala — the Pallava shore temples, the Brihadeeswarar Temple, and the spice markets and backwaters of Cochin. It is the itinerary for NRIs with roots in Tamil Nadu or Kerala who want to revisit heritage sites without the grinding intercity bus transfers.

**Glimpses of Karnataka** (4 days): A shorter circuit covering key heritage sites in Karnataka. This is the practical option for NRIs who are combining a business trip to Bengaluru with a few days of tourism — common for the tech professionals who fly into Bengaluru regularly.

## The Price Cut That Matters

Karnataka's tourism authorities have simultaneously announced a pricing revision for the state's luxury rail tourism offerings, explicitly aimed at broadening access beyond the traditional five-star traveler demographic. The Golden Chariot has historically been positioned as an ultra-premium product — previous seasons saw per-person prices that put it out of reach for most domestic travelers. The revised pricing structure aims to improve occupancy rates while maintaining the quality of the experience.

For NRIs, the math is worth running. A six-day luxury rail journey that covers hotels, meals, sightseeing, and intercity transport in a single package can actually undercut the cost of booking the same cities independently — especially when you factor in the premium hotels, private cars, and English-speaking guides that independent travel in Karnataka typically requires.

## Why This Matters for the Diaspora

The Golden Chariot solves a problem that every NRI who has tried to show visiting parents or in-laws around South India knows well: the logistics of multi-city travel in India are exhausting. Domestic flights get delayed. Road journeys between Mysuru and Hampi take six hours on potholed highways. Hotel quality varies wildly outside major cities. The luxury train collapses all of that into a moving base — you sleep on the train, wake up at the next destination, and step off into a guided experience.

Bengaluru, the starting point for two of the three itineraries, is already the second-busiest airport in India and a natural gateway for NRIs flying in from the US West Coast. Air India, United, and now Swiss (launching Zurich-Bengaluru nonstops in October) all serve the city directly or with convenient connections.

IRCTC has not yet published the full 2026-27 schedule or revised pricing online. Bookings are expected to open through the IRCTC tourism portal and select luxury travel agents. NRIs planning winter or early 2027 trips to South India should monitor the portal — the Golden Chariot's limited capacity (80 guests per departure) means popular dates sell out quickly once the schedule drops."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
