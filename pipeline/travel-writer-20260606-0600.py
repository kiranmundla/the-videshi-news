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
        "headline": "The World Cup Starts Next Week — Here's an NRI's Guide to Catching It Live",
        "subheadline": "Forty-eight teams, 16 cities, 104 matches across the US, Mexico, and Canada. India isn't playing — but millions of Indian Americans live within driving distance of a venue, and the tournament may never be this close again.",
        "slug": make_slug("fifa-world-cup-2026-nri-guide-us-venues-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The 2026 FIFA World Cup is being played across 16 cities in North America — many of them major NRI population centers including the Bay Area, Houston, Dallas, and New York/New Jersey. For Indian Americans who follow football or want a once-in-a-generation live sports experience, this is the most accessible World Cup in history.",
        "tags": ["travel", "fifa", "world-cup-2026", "sports", "road-trip", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "People Magazine", "url": "https://people.com/everything-to-know-about-the-2026-world-cup-11739032"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/sports/soccer/worldcup/2026/06/02/world-cup-live-updates/84002191007/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/8-iconic-road-trips-to-pair-with-the-fifa-world-cup-2026"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/SoFi_Stadium_2023.jpg/3840px-SoFi_Stadium_2023.jpg",
        "image_caption": "SoFi Stadium in Inglewood, California — one of 16 World Cup venues across North America",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The FIFA World Cup kicks off on June 11 in Mexico City, and for the first time since 1994, matches will be played on American soil. The tournament sprawls across three countries — the United States, Mexico, and Canada — with 16 host cities, 48 national teams, and 104 matches stretching through July 19.

India didn't qualify. That part stings. But here's the thing most Indian Americans haven't processed yet: this is the most logistically accessible World Cup in the history of the tournament, and it may never be this close to home again.

## The Cities That Matter to NRIs

Of the 16 host cities, at least eight sit in or near major Indian American population centers. The San Francisco Bay Area — home to roughly 300,000 Indian Americans — hosts matches at Levi's Stadium in Santa Clara. Houston, with the largest Indian population in the South, has NRG Stadium. The New York-New Jersey metro, where MetLife Stadium will host the final on July 19, is home to more than 700,000 people of Indian origin.

Dallas, Atlanta, Seattle, Boston, and Philadelphia round out the US venues — all cities with substantial desi communities, established Indian grocery networks, and direct or one-stop flights to India.

The full group schedule runs June 11 through June 27. The knockout rounds begin June 28, with the Round of 16 running July 4-7 — landing squarely on the long Independence Day weekend, a natural travel window for NRI families.

## Which Matches to Target

India's absence doesn't mean Indian Americans have no rooting interests. Several diaspora-relevant matchups stand out:

**Brazil vs Morocco** (June 13, MetLife Stadium, NJ) — two of the most popular football nations among South Asian fans, and it's in the New York metro. Expect the 50,000+ Moroccan and Brazilian diaspora communities to make this electric.

**England vs Croatia** (Group L, dates TBD) — the Premier League is the most-watched football league among Indian sports fans, and England's matches consistently draw South Asian crowds.

**Mexico vs South Africa** (June 11, Mexico City) — the opening match. If you're in SoCal or Texas, Mexico City is a short flight away, and the atmosphere will be unforgettable.

**USA vs Paraguay** (June 12, SoFi Stadium, LA) — the host nation's first match. SoFi is arguably the most spectacular venue in the tournament, and seats in the upper bowl were still available in the $150-200 range on FIFA's resale platform as of early June.

## The Road Trip Angle

The World Cup practically begs for an American road trip. Several venue pairings sit within reasonable driving distance:

**Bay Area → LA** (5.5 hours): Catch a match at Levi's Stadium in Santa Clara, then drive down the Pacific Coast Highway to SoFi Stadium in Inglewood. Stop in Big Sur and Santa Barbara. Time it with a June match weekend and you've got a trip your family will remember.

**Dallas → Houston** (3.5 hours): Both are group-stage venues, and the I-45 corridor between them is lined with some of Texas's best Indian restaurants — particularly the Hillcroft area in Houston, nicknamed the "Mahatma Gandhi District."

**Philadelphia → New York/New Jersey** (1.5 hours): Two venues, one Amtrak ticket. MetLife hosts the final. Philadelphia's Lincoln Financial Field hosts group matches. Devon Avenue-quality desi food is available in Edison and Jackson Heights between matches.

**Boston → New York** (3.5 hours): Gillette Stadium in Foxborough hosts group-stage matches. Combine with a New Jersey match for a Northeast football weekend.

## Tickets and Logistics

FIFA's official ticket platform at FIFA.com remains the primary source. Last-chance individual match tickets went on sale in late May, with prices ranging from $35 for Group Stage Category 3 seats to $600+ for knockout rounds. The resale market is active but pricey — expect premiums of 2-4x for high-demand matches.

For NRIs planning to bring family visiting from India, remember: visitors on B1/B2 tourist visas can attend sporting events without any special authorization. Canada and Mexico matches require separate entry requirements — Indian passport holders need a valid Canadian or Mexican visa (or a valid US visa for Mexico transit).

## Why This Matters

The 2026 World Cup is the first expanded tournament with 48 teams, and the first held across three countries. It's a scale of sporting event that North America hasn't seen since the 1994 World Cup in the US — which, despite American indifference to football at the time, still set attendance records that stood for decades.

For the Indian American diaspora — many of whom grew up watching World Cups on grainy Star Sports broadcasts in India and now live minutes from a stadium — this is a rare convergence of proximity and spectacle. India may not be on the pitch, but its diaspora is in the stands, in the fan zones, and on the road between venues."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Lufthansa Is Rolling Out Its Best Cabin to India — and Frankfurt Just Got Easier to Transit",
        "subheadline": "The Allegris premium cabin is coming to Delhi, Hyderabad, and Chennai routes. SWISS launches Bengaluru-Zurich nonstop. And Germany has killed the transit visa for Indian passport holders. For NRIs flying to India via Europe, the experience is about to change.",
        "slug": make_slug("lufthansa-allegris-india-routes-premium-cabin-transit"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Lufthansa Group is deploying its flagship Allegris cabin on multiple India routes — Delhi, Hyderabad, Chennai — and launching SWISS Bengaluru-Zurich nonstop. Combined with Germany's new transit visa waiver for Indians (effective June 3), Frankfurt and Munich are now the most friction-free European gateways for NRIs flying between the US and India.",
        "tags": ["travel", "airlines", "lufthansa", "allegris", "india-flights", "premium-cabin", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/international/3388371-germany-eases-transit-for-indian-flyers-boosting-air-links"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/05/lufthansa-boosts-india-connectivity/"},
            {"name": "Hospitality Career Profile", "url": "https://hospitalitycareerprofile.com/lufthansa-expands-allegris-cabins-to-11-new-long-haul-routes/"},
            {"name": "Europe Says", "url": "https://europesays.com/1766508/lufthansa-to-significantly-expand-allegris-this-winter/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/D-AIXO_Lufthansa_A359_MUC_%22Ulm%22_%2849033191421%29.jpg/3840px-D-AIXO_Lufthansa_A359_MUC_%22Ulm%22_%2849033191421%29.jpg",
        "image_caption": "A Lufthansa Airbus A350 at Munich Airport — the aircraft type carrying the new Allegris cabin to India",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Lufthansa Group has spent two years telling the world about Allegris, its answer to the cabin arms race that Gulf carriers have been winning for over a decade. Privacy doors in business class. Suites with lockable doors in first. A complete redesign across all four travel classes. More than half a million passengers have flown it since its 2024 debut.

Now, in its centenary year, the German aviation giant is finally bringing Allegris to India — and the timing couldn't be sharper for NRIs.

## What's Coming

Starting with the winter 2026-27 schedule, Lufthansa will deploy Allegris-equipped Boeing 787-9 aircraft on routes from Frankfurt to Delhi, Hyderabad, and — launching in March 2027 — Chennai. The 787-9 configuration carries 38 business class seats, 24 premium economy, and 201 economy, all in the new Allegris fitout.

From Munich, the Allegris rollout expands to Singapore, Washington, and Cape Town. In total, 11 new long-haul destinations get the cabin this winter, the largest single expansion since the product launched.

Meanwhile, Lufthansa's subsidiary SWISS will launch its first-ever nonstop service between Bengaluru and Zurich during the winter schedule. SWISS is also adding capacity between Delhi and Zurich with additional Airbus A330 flights. Both routes will eventually receive the SWISS Senses cabin — essentially Allegris with Swiss branding.

And the A380, the double-decker giant, is getting more frequency on the Mumbai-Munich route, responding to what Lufthansa calls "strong demand from both business and leisure travelers."

## The Transit Visa Game-Changer

This hardware upgrade coincides with a policy shift that makes the entire Lufthansa network dramatically more accessible for Indian passport holders.

On June 3, 2026, Germany officially eliminated the Airport Transit Visa requirement for Indian nationals. Previously, Indians connecting through Frankfurt or Munich to a non-Schengen destination — say, flying San Francisco to Frankfurt to Delhi — needed a separate transit visa just to change planes. That meant a consulate visit, paperwork, and a fee, for the privilege of walking between two gates.

That requirement is now gone. The change, announced after discussions between Prime Minister Modi and German Chancellor Friedrich Merz during a January 2026 meeting, was published in Germany's Federal Law Gazette on June 2 and took effect the next day.

France had already removed its transit visa for Indians earlier. But Germany's airports — particularly Frankfurt, Europe's fourth-busiest hub — handle far more India-to-Americas routing than Charles de Gaulle.

## What This Means for NRIs

The practical impact is significant for the estimated 4.5 million Indian Americans who fly to India regularly.

**Better cabin, more routes.** An NRI in Houston connecting through Frankfurt to Hyderabad will now fly the Allegris cabin on the transatlantic leg and potentially on the Hyderabad leg too — both in business class with privacy doors, if booked in that cabin. The current Lufthansa product on India routes has been a mixed bag, with older cabins on some 747 and A340 services. Allegris standardizes the experience.

**No visa friction.** The same Houston traveler no longer needs a transit visa to connect in Frankfurt. Book the ticket, show up, walk to your gate. That's how it already works in Dubai, Doha, and Istanbul — the Gulf hubs that have been eating Lufthansa's India-US connecting traffic for years.

**Price competition.** Lufthansa Group operates more than 70 weekly flights between India and Europe. With a better cabin product and no transit visa headache, Frankfurt and Munich become genuinely competitive with the Gulf carriers on the US-India corridor. Emirates, Qatar Airways, and Etihad have dominated premium connecting traffic between the US and India precisely because their hubs required no transit visa. That advantage just evaporated for German routes.

**Chennai gets direct Europe access.** The planned Frankfurt-Chennai service, launching March 2027 on the 787-9, gives South India's fourth-largest metro a direct Lufthansa link. For the large Tamil diaspora in the US and UK, this adds a connecting option that doesn't route through Delhi or Mumbai.

## The Bigger Picture

Lufthansa's India push is not charity — it's commerce. India is the airline group's largest intercontinental market in Asia-Pacific, and the Indian American diaspora generates high-yield traffic on the US-Europe-India triangle. The combination of Allegris hardware, transit visa removal, and new routes to Bengaluru, Chennai, and Hyderabad represents a coordinated bet on capturing a larger share of that traffic from Gulf carriers.

For NRIs who have spent years routing through Dubai or Doha, the European alternative just got meaningfully better. Whether it's enough to shift booking habits remains to be seen — but at minimum, the next time you price out flights home, Frankfurt deserves a second look."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Monsoon Just Hit Kerala — Seven Indian Destinations That Are About to Turn Spectacular",
        "subheadline": "India's southwest monsoon arrived on June 4, three days late and forecast to be the weakest in 11 years. For NRIs planning summer trips home, that's actually good news — milder rains mean easier travel and the same breathtaking landscapes.",
        "slug": make_slug("india-monsoon-destinations-nri-summer-travel-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Summer is peak NRI-visits-India season, and many diaspora travelers avoid the monsoon months out of habit or parental warnings. But a weak El Niño-influenced monsoon in 2026 means milder conditions — an ideal window for monsoon tourism. These seven destinations are at their most beautiful right now, with lower hotel rates and fewer crowds than winter season.",
        "tags": ["travel", "india", "monsoon", "kerala", "western-ghats", "nri", "summer-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-monsoon-reaches-kerala-three-days-later-than-usual-2026-06-04/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/india-braces-for-torrential-monsoon-rains/"},
            {"name": "BW Retail World", "url": "https://www.bwretailworld.com/article/offbeat-wet-monsoon-travel-finds-its-moment/"},
            {"name": "Booking.com Travel Trends 2026", "url": "https://www.outlooktraveller.com/experiences/skip-the-international-flight-visit-these-indian-destinations-instead"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17141643/pexels-photo-17141643.jpeg",
        "image_caption": "A houseboat on Kerala's backwaters — the monsoon transforms the state's waterways into lush green corridors",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The southwest monsoon hit the coast of Kerala on June 4 — three days behind schedule, arriving to a country baking under a heatwave that had pushed power demand to record highs. The India Meteorological Department has forecast this will be the weakest monsoon in 11 years, dampened by El Niño conditions that suppress rainfall across the subcontinent.

For farmers, that's worrying. For NRIs planning summer trips to India, it's quietly excellent news.

A weaker monsoon doesn't mean no rain — it means less extreme rainfall, fewer flood alerts, and milder conditions in destinations that normally get battered between June and September. The landscapes still turn impossibly green. The waterfalls still roar. But the roads stay passable, the flights stay on schedule more often, and the hotel rates drop to a fraction of winter-season prices.

Here are seven destinations that are at their best right now.

## 1. Munnar, Kerala

The tea capital of South India becomes a misty dreamscape during the monsoon. Rolling plantations disappear into fog, waterfalls swell to their most dramatic, and temperatures hover around 15-20°C — a world away from the 40-degree furnace of the plains. The Eravikulam National Park reopens after its annual breeding-season closure, and the roads through the Western Ghats are lined with wild orchids and cardamom.

**NRI tip:** Munnar is a 4-hour drive from Kochi airport. Combine it with a houseboat night in Alleppey for a two-destination trip that covers hill and water.

## 2. Coorg (Kodagu), Karnataka

Karnataka's coffee country is at its most fragrant during the monsoon. The region receives sustained rainfall that feeds the Abbey Falls and Iruppu Falls, both of which are underwhelming in dry months but spectacular in July and August. The mist-covered estates, plantation homestays, and the smell of wet earth mixed with coffee blossoms make this the most atmospheric stay in South India.

**NRI tip:** Fly into Mangalore or Mysuru. Most plantation homestays offer monsoon-season rates 30-40% below peak season, and many include estate tours and home-cooked Kodava cuisine.

## 3. Goa — the Off-Season Version

Monsoon Goa is nothing like December Goa, and that's the point. The party crowds vanish. The beaches empty. The fields behind the coastline turn neon green, and the Portuguese-era churches and colonial homes look their most photogenic against grey skies and wet laterite stone. Dudhsagar Falls, accessible only by train or jeep, is at full force and worth the trip alone.

According to Booking.com's Travel Trends 2026, 65% of Indian travelers now prefer domestic travel — and monsoon Goa is the sharpest example of why.

**NRI tip:** Monsoon hotel rates in South Goa can be 50-60% lower than December. Book a heritage property in Fontainhas or Assagao and spend your time on food, architecture, and waterfalls instead of beaches.

## 4. Meghalaya — India's Wettest State

Cherrapunji and Mawsynram are the wettest places on earth, and the monsoon is when they earn that title. But the rain here isn't a deterrent — it's the attraction. The living root bridges of Nongriat are best visited during the monsoon, when the streams below them are at their fullest. Mawlynnong, Asia's cleanest village, is emerald-green and nearly tourist-free.

**NRI tip:** Guwahati is the gateway airport. The roads to Shillong and beyond are winding but well-maintained. Budget 4-5 days for the full circuit: Shillong → Cherrapunji → Nongriat → Mawlynnong → Dawki.

## 5. Udaipur, Rajasthan

Rajasthan's lake city transforms during the monsoon from a dusty postcard into a living painting. Lake Pichola and Fateh Sagar fill to capacity, the Aravalli hills behind the City Palace turn green, and the Monsoon Palace — originally built as a retreat to watch the approaching rains — finally justifies its name.

**NRI tip:** Udaipur receives moderate monsoon rainfall compared to western Rajasthan, making it one of the safer bets in the state. The Taj Lake Palace and Oberoi Udaivilas both offer monsoon-season packages that include boat rides, cooking classes, and palace tours at reduced rates.

## 6. Valley of Flowers, Uttarakhand

This UNESCO World Heritage Site is open only from June to October, and July-August is peak bloom. More than 600 species of wildflowers carpet the alpine meadow at 3,600 meters, creating a landscape that doesn't exist anywhere else in India. The trek from Govindghat is moderate — about 17 km each way — and can be combined with a visit to the Sikh pilgrimage site of Hemkund Sahib.

**NRI tip:** The IMD has issued monsoon alerts for Uttarakhand, including potential hailstorms in early June. Check conditions before trekking and register with the forest department. This is a destination that rewards planning and punishes improvisation.

## 7. Agumbe, Karnataka

Known as the "Cherrapunji of the South," this tiny settlement in the Western Ghats receives some of the heaviest rainfall in peninsular India. The surrounding rainforest — home to king cobras, Malabar pit vipers, and the lion-tailed macaque — is at its most alive during the monsoon. The sunset point overlooking the Arabian Sea, when clouds part long enough to reveal it, is among the most dramatic views in India.

**NRI tip:** Agumbe is 6 hours from Bengaluru and best accessed by car. The Agumbe Rainforest Research Station offers guided walks for visitors. Pair it with a stop at Jog Falls — India's second-highest waterfall — which is 2 hours away and absolutely thunderous in monsoon.

## The Bottom Line

Indian monsoon tourism is no longer a niche idea. Hotel aggregators report a 30% year-over-year increase in monsoon bookings for Western Ghats and Northeast destinations. For NRIs visiting India this summer, the weak 2026 monsoon is a rare alignment: the landscapes are monsoon-spectacular, the crowds are winter-low, the prices are off-season, and the rainfall is milder than usual. The parents who warned you never to travel during monsoon were right about 2019. They're wrong about 2026."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
