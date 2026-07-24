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
        "headline": "Lufthansa Is Betting Its 100th Year on India — and a First-Ever Zurich Flight Into the South",
        "subheadline": "The group's winter schedule adds a Bengaluru–Zurich nonstop, new Allegris cabins out of Delhi and Hyderabad, and extra A380 frequencies to Munich — a quiet but serious play for the diaspora's European connections.",
        "slug": make_slug("lufthansa-swiss-bengaluru-zurich-allegris-india-winter-expansion-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the roughly 4 million Indian Americans who route through Frankfurt, Munich or Zurich on the way home, more premium-cabin frequencies and a brand-new southern India gateway mean shorter layovers and fresher aircraft on the long leg.",
        "tags": ["travel", "airlines", "lufthansa", "swiss", "bengaluru", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via-germany/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/lufthansa-group-winter-expansion-new-long-haul-routes-to-kuala-lumpur-bengaluru-seoul-and-north-america/"},
            {"name": "Aviation India", "url": "https://www.aviationindia.net/lufthansa-group-welcomes-visa-free-airport-transit-for-indian-nationals-via-germany/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/14400667/pexels-photo-14400667.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A long-haul airliner's wing above the clouds, the workhorse of India-Europe connections.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The Lufthansa Group is marking its 100th year by quietly doing what no European carrier has managed before: putting Bengaluru on a nonstop map to Switzerland. As part of its winter 2026-27 schedule, Swiss International Air Lines will launch its first-ever direct service between Zurich and Bengaluru — the airline's debut route into southern India, and a notable vote of confidence in a city that has long sent more engineers to Europe than tourists.

For a group that already runs more than 70 weekly flights between India and Europe, this is not a one-off. India is now Lufthansa's largest intercontinental market in the Asia-Pacific region, and the carrier is spending accordingly.

## What's actually changing

The winter package has several moving parts that matter to anyone who flies the India-Europe corridor:

- **Swiss launches Zurich–Bengaluru**, its first route to southern India, opening a clean one-stop path from the Karnataka tech belt into Europe and onward to North America.
- **Lufthansa's Allegris cabins** — the airline's heavily marketed new business and premium-economy product — arrive on additional Boeing 787-9 services from **Delhi and Hyderabad**, replacing older interiors that frequent flyers have complained about for years.
- **Extra Swiss A330 frequencies** are being added between **Delhi and Zurich**.
- **Enhanced Airbus A380 service** runs between **Mumbai and Munich**, putting the group's largest aircraft on one of its densest Indian routes.
- A new onboard product called **FOX (Future Onboard Experience)** rolls out across all long-haul cabins.

The expansion lands alongside a regulatory tailwind. As of June 3, 2026, Germany abolished the airport transit visa requirement for Indian nationals connecting through German hubs to third countries — meaning a passenger flying, say, Hyderabad to Frankfurt to Toronto no longer needs a separate transit visa to change planes airside. France made the same move in April. For a traveler who has spent years budgeting an extra visa fee and the anxiety of a missed connection turning into an immigration problem, that is a real, money-and-stress saving.

## Why this matters to the diaspora

Indian Americans rarely fly Lufthansa or Swiss for the destination — they fly it for the connection. The group's Frankfurt, Munich and Zurich hubs are among the most efficient ways to reach second-tier Indian cities that Air India and United don't serve nonstop from the US. A San Jose engineer with family in Mysuru, for instance, has historically had to fly into Bengaluru via a Gulf hub or via Delhi, adding hours. A Zurich–Bengaluru nonstop, fed by Swiss's transatlantic network out of US cities like New York, Boston and Chicago, shortens that journey meaningfully.

The Allegris upgrade out of Hyderabad is equally pointed. Hyderabad is one of the fastest-growing diaspora source cities — the Telugu population in the US has roughly tripled in a decade — and yet its long-haul cabins have lagged. Putting the newest seats on that route signals where Lufthansa expects its premium revenue to come from.

There is a strategic subtext here, too. Air India's own US flying has been shaky in recent months, and Gulf carriers dominate the price-sensitive end of the market. Lufthansa is staking out the middle: better cabins, more frequencies, and the regulatory ease of visa-free transit, aimed squarely at the professional NRI who will pay for a smoother trip but won't fly 22 hours in an aging seat.

## What to watch

Swiss has not yet published exact start dates or frequencies for the Bengaluru route beyond the winter 2026-27 window, which typically begins in late October. Fares usually open for booking three to four months ahead, so travelers eyeing the inaugural season should set alerts now. The A380 Mumbai–Munich service and the expanded Delhi–Zurich frequencies are already loading into booking systems.

One caveat worth repeating: the German and French transit-visa waivers cover **airside transit only**. They do not let Indian passport holders leave the airport or enter the Schengen area — that still requires a full Schengen visa. The benefit is purely for travelers changing planes on the way to a non-Schengen destination such as the US, UK or Canada.

For the diaspora, the takeaway is simple. Europe's biggest airline group has decided India is where its next decade of growth lives, and it is putting its newest aircraft, its newest cabins and a brand-new southern gateway behind that bet. The flyer who plans ahead gets the upgrade."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Is About to Make the Bali Run Nonstop — and the A321XLR Is the Reason",
        "subheadline": "India's biggest airline is upgrading its Delhi and Mumbai flights to Denpasar to the long-range A321XLR, dropping the awkward fuel stop that has annoyed travelers to one of the diaspora's favorite getaways.",
        "slug": make_slug("indigo-a321xlr-bali-denpasar-nonstop-direct-nri-southeast-asia"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Bali is a top short-haul holiday and destination-wedding spot for NRIs who fly into India and want a nearby beach reset; a true nonstop from Delhi and Mumbai cuts hours off a trip that families often tack onto a longer India visit.",
        "tags": ["travel", "airlines", "indigo", "bali", "southeast-asia", "a321xlr"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/airbus-a321xlr-indigo-bali-denpasar-expansion/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-resumes-delhi-rome-flights-indigo-adds-delhi-london-route-in-2026/article.ece"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/27375306/pexels-photo-27375306.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A traditional Balinese temple, one of the diaspora's most-booked short-haul getaways from India.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """IndiGo, India's largest airline by a wide margin, is finally fixing one of the more irritating quirks of the Bali run. The carrier plans to deploy its new Airbus A321XLR on both the Delhi–Denpasar and Mumbai–Denpasar routes, replacing the A320neo aircraft that currently fly the journey with an awkward refueling stop in Bhubaneswar or Chennai. The upgrade turns a multi-leg slog into a clean nonstop.

The A321XLR is the aircraft making this possible. With a range of up to 8,700 km, it comfortably covers the Delhi-to-Bali distance that the A320neo cannot manage in one hop. IndiGo has ordered 40 of the type, with nine due for delivery by the end of 2026, and Denpasar is among the first destinations slated to get it after Athens and Istanbul.

## Why Bali, and why now

Bali has quietly become one of the most-booked international destinations for Indian travelers. It hits a sweet spot: visa-on-arrival access for Indian passport holders, a favorable exchange rate, the kind of beach-and-temple scenery that photographs well, and a thriving market for destination weddings. The current routing — with its fuel stop and aircraft change of pace — has been the main friction point. Removing it makes Bali a genuine long-weekend option rather than a full-day commitment.

The jet itself is configured for the premium-leaning leisure traveler IndiGo is chasing. The A321XLR carries 12 IndiGoStretch seats — the airline's business-style product with wider seats, deeper recline, priority boarding and complimentary meals — alongside 183 economy seats. That mix tells you who the airline expects to fill the front of the cabin: families and couples willing to pay a bit more for comfort on a five-hour-plus flight.

This is part of a broader IndiGo international push. The carrier has recently added Delhi service to Denpasar, Krabi, Hanoi, Guangzhou and Manchester, launched a Delhi–London Heathrow route, and is rolling IndiGoStretch onto longer routes such as Bengaluru–Mauritius. The A321XLR is the backbone of that medium-haul ambition.

## What it means for the diaspora

For NRIs, Bali is rarely the main event — it is the add-on. A family flying from the US to India for a wedding or a long summer visit often wants a few days of decompression somewhere nearby that isn't another round of relatives and humidity. Bali, Phuket and the Maldives are the usual shortlist. A nonstop from Delhi or Mumbai makes Bali the easiest of the three to slot into an existing India itinerary, because it shaves the connection time that previously made it a tough sell with kids or older parents in tow.

There is also a cost angle. IndiGo's low-cost model has historically undercut full-service carriers on Southeast Asia routes, and a more efficient nonstop aircraft tends to push fares down further by cutting the operational expense of an intermediate stop. For a diaspora family already spending heavily on US–India tickets, a cheaper, faster Bali leg is the difference between adding the side trip and skipping it.

## The fine print

IndiGo has confirmed the intent to deploy the A321XLR on the Bali routes but has not published a firm switchover date; the timing depends on the delivery schedule of the nine aircraft due by year-end. Travelers planning a Bali leg over the coming high season should check whether their specific flight has been upgraded to the nonstop before booking, since the stop-over A320neo service may continue on some frequencies in the interim.

Indonesia continues to offer Indian passport holders a visa on arrival for tourism, currently priced at around 500,000 rupiah (roughly $30), payable at the airport — a reminder that, unlike the European routes that dominate aviation headlines, Bali remains one of the genuinely low-friction destinations for the Indian traveler. Add a true nonstop, and IndiGo has removed just about the last reason to hesitate."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Monsoon Is Lighter This Year — and That Quietly Makes It the Best Summer to Visit in a Decade",
        "subheadline": "The IMD forecasts rainfall at 92% of normal, meaning fewer washed-out roads and clearer mornings. For diaspora families traveling in July and August, here's where the rain is a feature, not a bug.",
        "slug": make_slug("india-monsoon-2026-below-normal-travel-coorg-ladakh-meghalaya-nri-summer"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Summer is peak season for NRI families visiting India because US and UK school breaks line up with it; a below-normal monsoon means the off-season hill stations and waterfalls are at their lushest with lower landslide risk and a fraction of winter hotel prices.",
        "tags": ["travel", "india", "monsoon", "destinations", "hill-stations", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "StayVista Journal", "url": "https://www.stayvista.com/blog/pre-monsoon-2026-indian-hill-stations"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"},
            {"name": "Skymet Weather Services", "url": "https://www.skymetweather.com/content/weather-news-and-analysis/weather-forecast-june-26-monsoon-finally-reaches-mumbai-surat-and-indore/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36982207/pexels-photo-36982207.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A monsoon-fed waterfall in the lush green Western Ghats during India's rainy season.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For the diaspora family weighing a July or August trip to India, the weather forecast is doing something unusual this year: cooperating. The India Meteorological Department puts the 2026 southwest monsoon at roughly 92% of the long-period average — below normal — with Skymet pegging it at 94%. After 2024's catastrophic 108%-of-normal season that triggered the deadly Wayanad landslides, a lighter monsoon is genuinely good news for travelers. It means fewer road closures, more clear-view mornings, and the lush, green, photogenic India that the rains produce without as many of the dangers.

The timing is what makes this relevant to NRIs specifically. The Indian summer travel window — June through August — is when US, UK and Canadian school holidays line up, which is precisely why so many diaspora families schedule their India visits then. The conventional wisdom has long been to endure the heat in May or wait for the cool, dry winter. But the monsoon, handled correctly, is arguably the most beautiful time to see the country. And this year the risk-reward math tilts in the traveler's favor.

## Where the rain is the attraction

Not all monsoon destinations are created equal. The smart moves cluster in a few categories:

**The rain-shadow Himalayas.** Ladakh sits in a zone the monsoon barely reaches, delivering clear skies and 12–22°C temperatures while the rest of India floods. June through September is its peak season — ideal for Pangong Lake, Nubra Valley and Zanskar. The Valley of Flowers in Uttarakhand opens in June, with peak bloom from mid-July to mid-August when more than 500 wildflower species carpet the alpine meadow.

**The Western Ghats waterfalls.** Coorg's Abbey Falls, Kerala's Athirappilly, and Dudhsagar on the Goa-Karnataka border peak roughly 7–10 days after the Kerala monsoon onset. Coorg, Munnar, Lonavala and Mahabaleshwar are the classic, family-safe picks — close enough to Bengaluru, Mumbai and Hyderabad for a long weekend.

**Meghalaya, the wettest place on Earth.** Shillong is the base for Cherrapunji's living root bridges and Mawlynnong, billed as Asia's cleanest village. The waterfalls are at maximum volume; just pack waterproof shoes for the famously slippery descent to Nongriat's double-decker root bridge.

**Udaipur in the rain.** Rajasthan is an unexpected monsoon star. Lake Pichola fills, the Sajjangarh Monsoon Palace earns its name, and hotel rates fall to a fraction of their winter peak — Delhi–Udaipur fares can dip as low as ₹1,500 one-way.

## Where to be careful

A lighter monsoon does not mean a risk-free one. Family-travel specialists are still flagging the landslide-prone Wayanad valleys, parts of Uttarakhand, and high-altitude Sikkim as places to avoid with young children. The approach roads to Spiti from Manali remain risky in the rains — the safer way in is the Shimla–Kinnaur route via NH-5. And anyone driving in the Ghats should respect the "48-hour rule": wait two days after an official heavy-rain alert before attempting long hill drives.

## The festival bonus

The monsoon is also festival season, which is a draw in itself for diaspora travelers wanting their children to experience the culture. The 2026 calendar lines up several worth building a trip around: São João in Goa and the Hemis festival in Ladakh (both late June), the Puri Rath Yatra (July 16), Teej in Jaipur (August 15), and Onam in Kerala with the Nehru Trophy Boat Race (late August). These dates shift with the lunar calendar and sell out fast, so booking flights and stays early is the difference between attending and watching from afar.

## The practical takeaway

For NRIs, the monsoon trip has always been the contrarian play — cheaper, greener and far less crowded than the winter high season. This year's below-normal forecast strips out much of the downside that usually scares families off. The booking window matters: hill-station rates rise sharply the moment the Kerala onset is officially declared, so the travelers who lock in stays early get the lush scenery at off-season prices. Pack for rain, build flexibility into the itinerary, choose the rain-shadow and Western Ghats destinations over the landslide belt, and the much-maligned monsoon turns into the best-value season India offers."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
