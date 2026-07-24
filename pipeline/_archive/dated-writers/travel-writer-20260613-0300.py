#!/usr/bin/env python3
"""Travel writer - 2026-06-13 03:00 PDT batch"""

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
        "headline": "Air India and Thai Airways Ink a Codeshare Deal — and NRIs Flying Through Bangkok Just Got More Options",
        "subheadline": "The Star Alliance partners signed an MoU at the IATA AGM in Rio, planning to place their codes on each other's flights across Asia, Europe, and North America.",
        "slug": make_slug("air-india-thai-airways-codeshare-mou-nri-bangkok"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs routing through Bangkok on trips between the US and India gain single-ticket itineraries and better connections across Southeast Asia under the planned codeshare.",
        "tags": ["travel", "airlines", "air india", "thai airways", "codeshare", "star alliance", "bangkok"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/air-india-and-thai-airways-sign-mou-to-strengthen-connectivity-between-india-and-thailand"},
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/air-india-and-thai-airways-deepen-partnership/"},
            {"name": "Asian Aviation", "url": "https://asianaviation.com/air-india-thai-airways-deepen-cooperation/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16562841/pexels-photo-16562841.jpeg",
        "image_caption": "A commercial aircraft on the tarmac before departure",
        "image_attribution": "Pexels",
        "body": """Air India and Thai Airways International have signed a Memorandum of Understanding to build a codeshare partnership, a deal that quietly reshapes how millions of Indian passport holders — and the NRI diaspora — connect to the world through Southeast Asia's busiest hub.

The MoU was signed on June 7 at the International Air Transport Association's Annual General Meeting in Rio de Janeiro. Under the planned arrangement, both Star Alliance carriers intend to place their respective designator codes — AI for Air India and TG for Thai Airways — on each other's flights between India and Thailand. The codeshare is also expected to extend to select international routes from both countries, opening single-ticket access to destinations across Asia, North America, and Europe.

## What the deal actually means

At its core, the partnership turns Bangkok's Suvarnabhumi Airport into a more powerful transit node for Indian travelers. Today, Air India and Thai Airways already have an interline agreement — passengers can book connecting flights, but each leg is essentially a separate ticket with separate baggage handling. A codeshare changes that calculus. Passengers book one itinerary, check bags through to the final destination, and benefit from coordinated schedules that minimize layover dead time.

"India and Thailand are connected by longstanding cultural ties, growing economic engagement, and strong flows of tourism and business travel," Air India CEO Campbell Wilson said in the announcement. "This MoU brings together two carriers with complementary strengths and a shared commitment to service excellence."

Thai Airways CEO Chai Eamsiri described the agreement as "a meaningful milestone" in the airline's strategy to strengthen regional connectivity.

## The NRI calculus

For Indian Americans, the deal matters in two practical ways.

First, Bangkok is already one of the most popular layover cities for NRIs flying between the US and India, particularly on Star Alliance itineraries that route through major Asian hubs. The codeshare would let passengers book multi-leg trips — say, San Francisco to Bangkok to Chennai — on a single ticket under either Air India or Thai Airways branding. That means fewer booking headaches, through-checked bags, and coordinated rebooking if a connection goes sideways.

Second, the partnership makes Southeast Asia significantly easier to reach from India. Thai Airways operates an extensive regional network from Bangkok to destinations across Thailand, Vietnam, Cambodia, Laos, Myanmar, and Indonesia. For NRIs planning a family vacation to Phuket, Chiang Mai, or Bali alongside a trip to India, this codeshare could eliminate the need for a separate ticket on a separate airline.

The timing matters too. Thailand recently shifted from its 60-day visa-free policy for Indians to a Visa on Arrival system at 2,000 Thai Baht. Despite that added friction, India remains one of Thailand's fastest-growing tourist markets, driven by cultural affinity, affordable packages, and the sheer variety of experiences — from Bangkok's street food to northern hill-tribe treks.

## The Star Alliance factor

Both airlines are Star Alliance members, which means the codeshare amplifies an already dense network. Air India's growing long-haul fleet — including A350s on its Delhi-New York route and expanded US frequencies — connects directly into Thai Airways' Southeast Asian web. The reverse is equally significant: Thai Airways' European network, which includes flights to London, Frankfurt, Paris, Zurich, and Munich, offers NRIs routing through Bangkok an alternative to Middle Eastern carriers on the India-Europe corridor.

Specific terms of the codeshare agreement, including which routes will carry dual codes and when ticket sales begin, will be announced after regulatory approvals are secured. Given both airlines' Star Alliance membership and existing interline framework, industry observers expect the transition to be relatively straightforward.

## What comes next

The MoU is part of Air India's broader strategy under the Tata Group to rebuild its international network through partnerships rather than going it alone. In recent months, Air India has also deepened ties with Singapore Airlines, Lufthansa, and United — building a web of codeshares that gives Indian travelers access to global destinations without the legacy carrier needing to fly every route itself.

For the 4.4 million Indian Americans who collectively spend billions on airfare each year, every new partnership that simplifies the journey between their two homes is worth watching. The Air India-Thai Airways codeshare may not be a headline-grabbing fleet order, but it is the kind of behind-the-scenes plumbing that makes the actual experience of flying better."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Vande Bharat Now Connects Vaishno Devi to the Golden Temple — and NRIs Can Do Both in a Single Day",
        "subheadline": "Starting June 16, the rerouted Katra-Amritsar express adds stops at Gurdaspur and Batala, stitching together Punjab's most sacred pilgrimage corridor by high-speed rail.",
        "slug": make_slug("vande-bharat-katra-amritsar-gurdaspur-golden-temple-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the millions of Punjabi Americans who plan pilgrimages to Vaishno Devi and the Golden Temple on every India trip, a single high-speed rail journey now connects both sacred sites in under six hours.",
        "tags": ["travel", "india", "railways", "vande bharat", "golden temple", "vaishno devi", "pilgrimage", "punjab"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/2026/06/12/vande-bharat-express-route-diverted-via-gurdaspur-batala-weekly-off-changed-to-saturday/"},
            {"name": "Metro Rail News", "url": "https://metrorailnews.in/centre-approves-jammu-srinagar-vande-bharat-express-to-halt-at-anantnag/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/air-india-easy-connect-flights-to-ease-immigration-for-tier-2-cities/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "image_caption": "The Golden Temple in Amritsar, the terminus of the rerouted Vande Bharat Express",
        "image_attribution": "Wikimedia Commons",
        "body": """Indian Railways has rerouted the Vande Bharat Express between Shri Mata Vaishno Devi Katra and Amritsar to run through Gurdaspur and Batala, creating what amounts to Punjab's first high-speed pilgrimage corridor. For NRIs who squeeze both Vaishno Devi and the Golden Temple into every India trip — often enduring a brutal overnight bus or a multi-car relay — this is the itinerary upgrade they have been waiting for.

The revised schedule takes effect on June 16 for services originating from Amritsar and June 17 from Katra. The train will run six days a week, with Saturday replacing Tuesday as the weekly off day.

## The new route

Under the old alignment, the Vande Bharat ran from Katra to Amritsar via Pathankot Cantt. The rerouted service instead passes through Pathankot, then continues to Gurdaspur (arriving at 10:15 AM), Chhina (10:45 AM), and Batala Junction (10:54 AM) before reaching Amritsar at 12:20 PM. The return leg departs Amritsar at 4:25 PM, following the same route in reverse and arriving at Katra by 10:00 PM.

The change is more than a scheduling tweak. Gurdaspur and Batala are significant population centers in Punjab's border belt — home to hundreds of thousands of people who previously had to travel to Jammu or Pathankot Cantt to board the Vande Bharat. The diversion gives them direct access to India's fastest train class and, crucially, connects them to both ends of the pilgrimage circuit.

## Why NRIs should care

Every year, millions of diaspora Indians — particularly those with roots in Punjab, Jammu, and the broader North Indian belt — make the dual pilgrimage to Vaishno Devi's mountain shrine and the Golden Temple in Amritsar. Historically, this meant cobbling together a miserable multi-day logistics chain: fly into either Delhi or Amritsar, take a taxi or bus to Katra, climb to the shrine, come back down, then somehow get to Amritsar (or vice versa) before flying out.

The rerouted Vande Bharat compresses that into a manageable single-day rail journey. Leave Katra at 6:40 AM after an early darshan, settle into air-conditioned comfort, and arrive at Amritsar by 12:20 PM — in time for the afternoon prayer at the Golden Temple. Or reverse it: morning langar at the Harmandir Sahib, the 4:25 PM Vande Bharat to Katra, and you are at the base of Vaishno Devi by 10 PM, ready for the next morning's climb.

For NRI families traveling with elderly parents — which describes a large share of pilgrimage trips — the difference between a Vande Bharat seat and an overnight bus is not a luxury. It is the difference between the trip happening at all.

## The broader picture

The Katra-Amritsar reroute is part of a larger expansion of the Vande Bharat network across India's pilgrimage and heritage circuits. The Jammu-Srinagar Vande Bharat, which launched last year and was extended to Jammu Tawi in April 2026, recently added an Anantnag halt on the recommendation of Kashmir Chief Minister Omar Abdullah. That service now operates with 20 coaches to handle surging demand.

Meanwhile, existing Vande Bharat services already connect Varanasi to Khajuraho, Delhi to Agra, and Ahmedabad to Mumbai — corridors that see heavy NRI traffic. The pattern is clear: Indian Railways is systematically linking the destinations that matter most to religious and heritage tourism, and doing it with trains that offer Western-standard comfort at Indian prices.

## Practical details for NRI visitors

The Vande Bharat runs with eight coaches on the Katra-Amritsar route. Tickets are available through the IRCTC website and app, and NRIs can book using foreign credit cards through IRCTC's international payment gateway. Fares on the Vande Bharat are typically 15-20% higher than Shatabdi Express equivalents, but the time savings and comfort — reclining seats, onboard catering, bio-vacuum toilets — make it a clear upgrade.

One practical note: the weekly off has shifted from Tuesday to Saturday, which may affect weekend travel plans. NRIs building an itinerary around these trains should check the IRCTC schedule before booking flights.

The rerouted service also opens up Gurdaspur as a convenient stopover. The historic border town is home to several gurudwaras, the Ranjit Sagar Dam, and Dalhousie — a hill station that remains underexplored by NRI tourists but offers cooler temperatures and colonial-era charm.

For a diaspora that has long endured punishing ground transport to complete its most meaningful journeys, a Vande Bharat seat between Vaishno Devi and the Golden Temple is not just a rail upgrade. It is a small revolution in how NRIs experience the India they return to."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Americans Are Trading Tuscany for Tacoma This Summer — and NRIs Should Join the Domestic Surge",
        "subheadline": "Booking.com data shows US domestic travel searches up 21%, with Austin exploding 423%. With India-bound fares up 45%, exploring your own backyard has never made more sense.",
        "slug": make_slug("us-domestic-city-break-boom-nri-summer-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With India-bound airfares up 45% and the World Cup driving domestic interest, NRIs who default to annual India trips may find better value — and new experiences — in an American city break this summer.",
        "tags": ["travel", "united states", "city break", "summer travel", "world cup", "nri", "domestic travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/american-travelers-are-trading-tuscany-for-tacoma-this-summer-thanks-to-soaring-airfares"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/austin-joins-atlanta-houston-san-diego-chicago-washington-san-francisco/"},
            {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/06/12/soaring-airfares-reshape-summer-travel-plans-as-fuel-costs-drive-domestic-vacation-surge/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20185085/pexels-photo-20185085.jpeg",
        "image_caption": "The Austin, Texas skyline — the city leading America's summer travel surge with a 423% jump in accommodation searches",
        "image_attribution": "Pexels",
        "body": """Every summer, millions of Indian American families face the same question: fly to India, or do something else? This year, the math is tilting decisively toward "something else" — and the data suggests NRIs should pay attention to a trend reshaping American travel.

According to Booking.com's latest search figures, accommodation searches for US domestic destinations are up 21% year-over-year, while domestic flight searches have surged 29%. The numbers for individual cities are even more striking: Austin, Texas, saw accommodation searches jump 423%. San Francisco is up 81% in flight searches. Boston, Washington D.C., and San Diego are all posting double-digit gains.

The catalyst is a collision of forces that hits NRI wallets especially hard.

## The airfare wall

Geopolitical volatility in the Strait of Hormuz has disrupted roughly 20% of global oil supply, sending jet fuel prices — and ticket prices — sharply higher. According to Kayak, round-trip economy fares to London are up over 45% from last summer, with average tickets jumping from $786 to over $1,100. Domestic round-trips have also risen, from $307 to $388 on average — but that is still a fraction of what India-bound travelers are facing.

For NRIs on the SFO-DEL corridor, summer fares that once ran $900-1,100 round-trip are now regularly crossing $1,600. Multiply that by a family of four, add checked baggage fees that every airline has raised in 2026, and the annual India trip becomes a $8,000-10,000 proposition before you have even landed.

Expedia's data confirms the behavioral shift: 63% of US travelers are prioritizing domestic trips this summer, driven by rising international costs and enthusiasm for regional events, including FIFA World Cup matches and America 250 celebrations.

## The cities worth visiting

For NRI families conditioned to think of summer as "India or bust," here is what the domestic surge actually looks like on the ground.

**Austin** is leading the pack for a reason. The Texas capital has evolved from a music-and-barbecue stopover into a genuine cultural destination, with a booming food scene that includes standout Indian and South Asian restaurants, a thriving tech community (many NRIs already have colleagues there), and outdoor recreation that ranges from Barton Springs to the Hill Country. A family of four can fly roundtrip from most major cities for under $1,200 and eat like royalty for a week.

**San Francisco** is surging in flight searches despite being home to one of the largest Indian American populations in the country. The irony is not lost: many Bay Area NRIs have never properly explored their own city as tourists. This is the summer to fix that — Alcatraz, the Ferry Building, Golden Gate Park, and the wine country are all within a day trip, and World Cup matches at Levi's Stadium add a once-in-a-generation event to the mix.

**Washington D.C.** offers free Smithsonian museums, the National Mall, and a food scene that has quietly become one of America's best. For NRI families with school-age kids, it is arguably the most educational city break in the country — and flights from the East Coast are cheap enough to justify a long weekend.

**Boston** combines colonial history with a world-class restaurant scene and some of the best universities in the world — a particular draw for NRI families with college-bound teenagers. The city's North End, Fenway Park, and harbor cruises make for a compact, walkable vacation.

## The World Cup bonus

The FIFA World Cup is being hosted across the US, Canada, and Mexico through July, and several host cities overlap with the domestic travel surge. Seattle, Houston, Dallas, and the Bay Area are all hosting matches, and the atmosphere in these cities — large screens, fan zones, international food festivals — is unlike anything most American cities have experienced.

For NRI families, the World Cup adds a unique layer: watching India's neighbors and cricketing rivals compete on a global stage, attending a live match as an event within a broader city break, and soaking in the kind of multicultural energy that NRIs navigate daily but rarely get to celebrate in public spaces.

## Making the case

None of this means NRIs should abandon the India trip permanently. The family obligations, the festivals, the food — nothing replaces going home. But in a summer when going home costs 45% more than it did last year, a domestic city break is not settling. It is a strategic choice.

A four-night Austin trip for a family of four — flights, hotel, food, activities — can come in under $3,000. The same family flying to Delhi is looking at $8,000 minimum, before gifts, weddings, and the inevitable "just one more suitcase" of shopping.

This summer, trading Tuscany for Tacoma is not just an American trend. It might be the smartest NRI travel move of the year."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
