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
        "headline": "IndiGo Pulls the Plug on Six Southeast Asian Routes — and NRIs Planning Summer Side Trips Need a New Plan",
        "subheadline": "India's largest airline is suspending flights to Hong Kong, Shanghai, Ho Chi Minh City, and three other destinations from July through September, citing war-inflated fuel costs and Pakistan's airspace ban. For NRIs who pair India visits with beach-and-temple hops across the region, the alternatives are thinner and pricier.",
        "slug": make_slug("indigo-suspends-six-southeast-asia-routes-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Hundreds of thousands of NRIs combine annual summer India trips with quick side-hops to Thailand, Vietnam, and Cambodia. IndiGo's budget fares on these routes made the add-on affordable. With six routes dark until October, diaspora travelers face higher fares on Air India, Thai Airways, and VietJet — or need to rethink their itinerary entirely.",
        "tags": ["travel", "airlines", "indigo", "southeast-asia", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-2026-06-04/"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/05/indigo-cancels-flights-6-international-destinations/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-suspends-flights-to-six-asian-destinations/article69653241.ece"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1200px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo — the workhorse of India's largest airline's international fleet",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The list of destinations IndiGo has walked away from in 2026 keeps growing. On Thursday, India's largest carrier confirmed it would suspend flights to six international routes across Southeast Asia and China starting July 1, pausing service to Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap through the end of September. Bookings are expected to reopen October 1, though the airline hedged that services could resume earlier "if conditions improve."

The cuts follow last week's indefinite cancellation of IndiGo's Manchester routes — its first-ever European service — after just 13 months. Together, the moves represent a significant strategic retreat for an airline that has been aggressively building an international network.

## Why it is happening

Three forces are squeezing IndiGo simultaneously. The Iran conflict, now well into its second year, has closed swathes of Middle Eastern airspace and pushed jet fuel prices from roughly $85 per barrel to between $150 and $200. Pakistan's airspace ban on Indian carriers, imposed during last year's military standoff, forces longer flight paths across every westbound route. And the July-to-September quarter is traditionally the weakest for outbound international travel from India, as monsoon season dampens demand.

IndiGo posted a loss of Rs 2,536 crore in Q4 FY26, its first quarterly red ink in over a year. The airline had already trimmed domestic flights by seven to ten percent for June and July. Rival Air India has gone further, cutting 22 percent of its domestic schedule and reducing service on several international routes as well.

"These measured changes are designed to align capacity with current market conditions and demand trends, while ensuring the airline maintains reliability and network integrity," IndiGo said in a statement, adding that it still operates more than 1,800 weekly international flights.

## What NRIs lose

The suspended destinations read like a summer-holiday wish list for Indian Americans visiting family back home. Many NRIs pair their annual India trips with a short hop across the Bay of Bengal — a five-day beach holiday in Krabi, a food-and-temple run through Ho Chi Minh City, a weekend in Siem Reap to see Angkor Wat, or a family stopover in Hong Kong before heading back to the US.

IndiGo had turned these side trips into impulse purchases. Budget nonstop fares from Delhi or Mumbai to Bangkok, Langkawi, or Siem Reap started as low as Rs 8,000–12,000 one way, substantially undercutting Thai Airways, VietJet, and full-service carriers. With IndiGo dark on these routes until at least October, NRIs booking summer plans have fewer options and less pricing leverage.

Air India Express still flies several Southeast Asian routes, and carriers like Thai Airways, Vietnam Airlines, and Singapore Airlines (via Changi) remain available — but none match IndiGo's combination of frequency and price on these specific city pairs.

## The bigger picture

IndiGo's retreat is a symptom of a broader crisis gripping Indian aviation. The combination of geopolitical airspace closures, war-driven fuel inflation, and a weakening rupee has pushed operating costs to levels the industry hasn't seen since the early pandemic. IndiGo's CFO Gaurav Negi said in May that the airline may consider fuel hedging for the first time — a sign of how far the cost environment has deteriorated.

For now, IndiGo insists the suspensions are temporary. The airline retained its top position among Indian carriers in international passenger traffic in April, carrying 870,000 passengers to the Air India group's 850,000. Its core network to the Gulf, Singapore, and key ASEAN hubs remains intact.

But for the NRI family that had pencilled in a Krabi beach week between visiting nani in Delhi and catching a flight back to JFK, the message is plain: book around IndiGo this summer, and budget for the markup."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America Turns 250 Next Month — Eight Road Trips Every NRI Family Should Consider This Summer",
        "subheadline": "The United States marks its semiquincentennial on July 4 with a nationwide wave of festivals, fireworks, and historical celebrations. With summer airfares up 31 percent and gas still cheaper than a plane ticket, the open road has never made more sense — especially for Indian Americans looking to deepen their connection with the country they now call home.",
        "slug": make_slug("america-250-road-trips-nri-families-semiquincentennial"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For Indian Americans who have built lives in the US, the 250th anniversary is a singular chance to explore the country's founding stories alongside their children — many of whom are growing up straddling two cultures. Road trips are also the pragmatic choice this summer: flights are 31% pricier year-over-year, and NRI families already stretching budgets between India flights and domestic travel will find the car a kinder option.",
        "tags": ["travel", "road-trip", "usa", "america-250", "family", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fox News", "url": "https://www.foxnews.com/travel/great-american-road-trip-8-places-travel-stay-celebrate-america-250-summer"},
            {"name": "U.S. Department of the Interior", "url": "https://www.doi.gov/pressreleases/honor-americas-250th-department-interior-officially-launches-great-american-expedition"},
            {"name": "Reuters / KAYAK", "url": "https://www.reuters.com/markets/see-how-much-pricier-summer-flights-are-this-year-2026-06-05/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18514240/pexels-photo-18514240.jpeg",
        "image_caption": "A long, empty highway stretches through Monument Valley under a bright blue sky",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """On July 4, 2026, the United States turns 250. The semiquincentennial — try saying that at a Fourth of July barbecue — is being marked with a sprawling, coast-to-coast calendar of concerts, fireworks, reenactments, and museum reopenings that stretches from late June through the summer. The Department of the Interior has launched a Great American Expedition, sending an expedition flag to national parks and monuments across the country. Philadelphia is throwing a multi-week festival. Carnival Cruise Line is staging a coordinated fireworks show from seven ships.

For Indian American families, the timing collides with two realities: summer airfares from US airports are up 31 percent year-over-year for domestic flights, according to KAYAK data reported by Reuters, and only 45 percent of Americans plan to take a summer vacation with paid lodging this year — the lowest in six years, per Deloitte. The math increasingly favours the car over the plane.

Here are eight road trip destinations built around the 250th anniversary celebrations — each one reachable by car from a major NRI population centre, and each one worth the drive.

## Philadelphia: Where it all started

No destination owns America's 250th birthday like Philadelphia. The Wawa Welcome America Festival runs June 19 through July 4, with six consecutive nights of fireworks, a free concert on the Benjamin Franklin Parkway featuring Christina Aguilera, Jill Scott, and The Roots, and the reopening of the First Bank of the United States to the public for the first time in decades.

The city is a four-hour drive from the New Jersey-New York corridor — home to one of the largest Indian American populations in the country. Independence Hall, the Liberty Bell, and the National Constitution Center are all within walking distance of each other. Stay at the Penn's View Hotel, an Italian American family-owned boutique property in a building from 1828, or the Hotel Warner in nearby West Chester if you prefer something quieter.

## Mount Rushmore and the Black Hills

South Dakota's Black Hills are pure Americana, and the National Park Service is pulling out all the stops for the anniversary. Mount Rushmore hosts nightly lighting ceremonies through the summer with ranger-led programs, veteran recognition, and monument illumination after sunset. The Fourth of July brings presidential reenactors, Indigenous cultural demonstrations, and a performance by the US Air Force Academy Band.

Pair it with a visit to the Crazy Horse Memorial and a drive through Custer State Park, where bison roam alongside scenic roads. For NRI families in the Midwest — Chicago, Minneapolis, Denver — this is an eight-to-twelve-hour drive, or a weekend with one overnight stop.

## Yellowstone: America's first national park

The country's first national park, established in 1872, feels fitting for a 250th celebration. Old Faithful erupts with clockwork regularity, the Grand Prismatic Spring is the kind of geological spectacle that renders phones useless, and Hayden Valley offers some of the best bison-viewing in North America.

Yellowstone is a full day's drive from the Bay Area, Pacific Northwest, or Colorado Front Range, but families who make the trip find a landscape that exists nowhere else on Earth. Book early — park lodges fill months ahead, and the summer season is the most crowded.

## The Pacific Coast Highway

California's Highway 1 between Los Angeles and San Francisco delivers what may be the most photographed road in America: dramatic cliffs, Big Sur's redwoods, Monterey's aquarium, and the Santa Monica Pier. For NRI families in the Bay Area or Southern California — two of the three largest Indian American metros — this is the quintessential day-and-a-half road trip.

The drive is best done slowly. Stop in Carmel-by-the-Sea for lunch, pull over at Bixby Creek Bridge for the photograph, and arrive in San Francisco in time for the city's own Fourth of July fireworks over the Bay.

## The Grand Canyon

The South Rim of the Grand Canyon is a five-hour drive from Phoenix and roughly six from Las Vegas — both cities with substantial Indian American communities. Mather Point, Desert View Drive, and rim walks offer world-class views without requiring a backcountry permit or significant hiking.

Summer temperatures are brutal at lower elevations but manageable on the rim, which sits at 7,000 feet. Start before dawn, stay above the canyon, and check park alerts before leaving. The nearby Petrified Forest and Painted Desert make an excellent two-day extension.

## The National Mall, Washington DC

The capital is an obvious anchor for the anniversary, and the Smithsonian museums — all free — are reason enough. For NRI families on the East Coast, DC is an easy drive from anywhere between Boston and Atlanta. The Fourth of July celebration on the National Mall is among the largest in the country, with a concert on the West Lawn of the Capitol and fireworks over the Washington Monument.

DC also offers a particular resonance for Indian Americans: the Mahatma Gandhi statue in front of the Indian Embassy on Massachusetts Avenue, the growing collection of South Asian art at the Sackler Gallery, and the sheer scale of a democratic republic's institutional architecture — something many first-generation immigrants came here partly because of.

## The Yucatan Peninsula (for those with a US visa)

Technically not a road trip from the US, but close enough to count as a drive-from-Cancun itinerary. Indian passport holders with a valid US visa can enter Mexico visa-free for up to 180 days. The Yucatan loop — Cancun to Valladolid, Chichen Itza, and Merida — offers cenotes, Mayan ruins, and Caribbean coastline at a fraction of what a comparable US beach vacation costs.

Fly into Cancun, rent a car, and cover the peninsula in five to seven days. Hotel prices are a fraction of US rates, and the food — particularly the cochinita pibil and papadzules — is reason enough.

## Under Canvas: Glamping near the monuments

For families that want the national park experience without the tent-and-sleeping-bag commitment, Under Canvas operates safari-style glamping sites near Mount Rushmore, Yellowstone, the Grand Canyon, Zion, and Glacier National Park. Tents come with king-size beds, private bathrooms, and wood-burning stoves.

It is not cheap — rates run $300 to $600 per night in peak season — but for an NRI family introducing kids to the American outdoors for the first time, the comfort-to-adventure ratio is hard to beat.

## Making the road trip work

A few practical notes for NRI families hitting the road this summer. Gas prices remain elevated — national averages hover around $4 per gallon — but the total cost of a road trip for a family of four still undercuts four plane tickets by a wide margin. Pack snacks, download offline maps, and use GasBuddy or Costco membership to shave twenty cents per gallon.

The National Park Service annual pass costs $80 and covers entrance fees at all 63 national parks plus hundreds of other federal recreation sites. For a family planning two or more park visits this summer, it pays for itself immediately.

And one more thing: America's 250th happens once. The bicentennial in 1976 is the stuff of family legend for those who were there. For Indian Americans who arrived in the decades since, this is a chance to be present for the next one — and to give their children a story about the summer their family drove across the country their parents chose."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
