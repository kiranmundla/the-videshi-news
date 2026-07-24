#!/usr/bin/env python3
"""Travel writer — 27 June 2026, 11:00 PT run."""
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


# ──────────────────────────────────────────────────────────────
# ARTICLE 1: El Niño's Dry Monsoon
# ──────────────────────────────────────────────────────────────

article1_body = """\
India's monsoon has arrived — technically. But so far it is behaving less like the dramatic downpour that defines the subcontinent's summer and more like an intermittent drizzle with a scheduling problem. Through the first three weeks of June, rainfall has run roughly 43 per cent below the long-period average, and the India Meteorological Department (IMD) projects the full season at just 90 per cent of normal — the weakest since 2015. The culprit is a strengthening El Niño, which some European forecasting models suggest could become one of the most intense on record by autumn.

For the roughly 4.4 million Indian Americans planning summer visits home, the dry spell is reshaping the trip in ways both welcome and cautionary.

## Clearer Skies at the Hill Stations

The typical July complaint for NRI visitors — cancelled treks, landslide-closed highways, rain-soaked temple circuits — may be markedly less severe this year. Destinations across the Western Ghats, the Nilgiris, and the northeast usually receive their heaviest rainfall between late June and mid-August. A 40-plus per cent deficit means drier approach roads, better visibility, and fewer flight diversions at airports like Cochin, Mangalore, and Bagdogra.

Himachal Pradesh and Uttarakhand, which saw devastating flood events in previous monsoon years, are so far reporting lighter-than-expected rainfall. For families planning the classic Shimla–Manali circuit or the Kedarnath pilgrimage, conditions are — for now — more forgiving than usual.

## But the Heat Isn't Backing Off

The flip side is that temperatures have lingered above 40°C across the Gangetic plain longer than normal, with heatwave conditions extending well into June. Delhi recorded 46°C earlier this month. Without steady rain to cool the land surface, cities like Varanasi, Lucknow, and Jaipur remain significantly hotter than their seasonal norms.

For diaspora visitors accustomed to American air conditioning, this means stricter hydration discipline, earlier sightseeing windows (before 10 a.m., after 5 p.m.), and a reason to favour South India or the coasts over North India's inland cities through mid-July.

## Water Stress Is Real — and It Affects Hotels

The government has classified 111 districts as high priority for drought contingency, with another 76 at medium risk. In parts of Maharashtra, Karnataka, and Rajasthan, local authorities have already restricted water supply for irrigation and are promoting less water-intensive crops.

This has a knock-on effect for hospitality. Several Rajasthan resorts have quietly reduced laundry turnaround and limited pool hours. In rural Maharashtra, homestay operators report lower water table levels than any recent June. Travellers staying at large urban hotels will barely notice, but those choosing the agrarian-chic farmstay experience — increasingly popular among second-generation NRIs — should check ahead.

## What Farmers Are Doing Matters for Food Prices

The monsoon deficit is pushing farmers from sugarcane and rice toward drought-resistant pulses, millets, and soybeans. The agricultural ministry is monitoring over 300 vulnerable districts. Vegetable prices are expected to climb as rain-fed cultivation contracts, which means the produce markets and street food stalls that draw food-loving visitors could see noticeable price hikes by August.

Wholesale inflation has already ticked up. Economists at IDFC First Bank project retail inflation could push toward 5.5 per cent if the monsoon's July–August performance remains weak — a reality that will show up in restaurant bills and market visits alike.

## The Silver Lining: Off-Season Pricing Still Holds

Despite the drier weather making travel conditions more pleasant than a typical monsoon, hotels and domestic airlines have not adjusted their monsoon-season pricing upward. Domestic airfares remain 30 to 50 per cent below winter peaks on popular routes. Hotel aggregators report deep discounts across Goa, Kerala, and Karnataka — places where the monsoon's reduced severity this year makes the value proposition unusually strong.

The advice for NRIs: book the monsoon trip, but swap the usual rain gear for sunscreen. Carry a reusable water bottle, check district-level advisories for flash-flood-prone zones in the northeast, and be prepared for a version of India that is, paradoxically, sunnier and dustier in what should be its wettest weeks. El Niño has rewritten the seasonal script — and for once, the diaspora visitor might be the accidental beneficiary.
"""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "El Niño Has Turned India's Monsoon Into a Drizzle — and NRI Summer Plans Should Adjust",
    "subheadline": "Rainfall is 43 per cent below average, hill stations are drier than usual, and hotel deals are holding. But the heat isn't going anywhere.",
    "slug": make_slug("el-nino-weak-monsoon-india-nri-summer-travel-heat"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The weakest monsoon in 11 years is reshaping summer travel to India for the 4.4 million Indian Americans who visit during these months — drier treks and cheaper hotels, but extended heatwaves and water stress in key tourism districts.",
    "tags": ["travel", "monsoon", "el-nino", "india", "weather", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-makes-contingency-plans-weak-monsoon-threatens-some-farm-areas-2026-06-24/"},
        {"name": "India Meteorological Department via Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-30/"},
        {"name": "Livemint", "url": "https://www.livemint.com/market/stock-market-news/el-nino-risk-looms-how-to-monsoon-proof-your-portfolio-11750785127082.html"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33545425/pexels-photo-33545425.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A man walks through lush green Indian countryside during a monsoon shower",
    "image_attribution": "Pexels",
    "body": article1_body.strip(),
}


# ──────────────────────────────────────────────────────────────
# ARTICLE 2: Vande Bharat Sleeper Trains
# ──────────────────────────────────────────────────────────────

article2_body = """\
For decades, an overnight train in India meant the same ritual: a vinyl-covered berth on a Rajdhani Express, a thermos of railway chai, and the rhythmic percussion of wheels on 1970s-era track joints. The experience was beloved by some and endured by most — particularly NRIs returning to find that the coach they were in might be older than they were.

That era is ending faster than most people realise. India's Vande Bharat Sleeper Express, a domestically designed and manufactured overnight train, has been in commercial service since January 2026. The first route — Howrah to Kamakhya (Guwahati), covering 968 kilometres in about 14 hours — now runs six days a week. And it is the opening salvo in what the railways ministry says will be a fleet of 200-plus sleeper trainsets deployed by 2032.

## What's Actually Different

The basics: air-conditioned coaches across three classes (First AC, AC 2-Tier, and AC 3-Tier), automatic doors, bio-vacuum toilets, infotainment screens, Wi-Fi, noise insulation, and a suspension system designed for a smoother ride at speeds up to 160 km/h. The 16-coach rakes carry 11 Third AC coaches, four Second AC, and one First AC — a capacity mix that tilts toward the mass market while preserving a premium tier.

The less obvious upgrade is operational. Unlike Rajdhani services, which share track priority with freight and slower passenger trains, Vande Bharat Sleeper schedules are being designed around tighter turnaround windows and dedicated path allocation on electrified corridors. The result is faster end-to-end times and fewer unexplained halts.

## The Routes That Matter for NRIs

The Howrah–Kamakhya route serves the Bengali and Assamese diaspora corridor — one of the busiest long-distance segments in the eastern network. A Mumbai CSMT–Bengaluru KSR service has been approved and is expected to begin operations soon, connecting two cities whose combined diaspora presence in the US runs into the hundreds of thousands.

The railways minister has confirmed that 12 Vande Bharat Sleeper trains will deploy on long-distance routes in the current fiscal year (2026-27). Two are already running. Future corridors reportedly under consideration include Delhi–Kolkata, Chennai–Hyderabad, and Delhi–Mumbai — the trunk routes that carry the heaviest NRI traffic during festival seasons.

A 24-coach version, being developed by the Integral Coach Factory in Chennai, is expected to roll out by end-2026. It will add capacity and, critically, offer a viable alternative to overcrowded Rajdhani and Duronto services on 1,000-to-1,500-kilometre corridors.

## The Price Argument

This is where it gets compelling. Third AC fares on the Howrah–Kamakhya Vande Bharat Sleeper are set at around ₹2,300 — roughly $27 at current exchange rates. A flight on the same route typically costs ₹6,000 to ₹10,000, plus airport transfers at both ends. For an NRI family of four visiting relatives in Guwahati from Kolkata, the train saves ₹15,000 to ₹30,000 each way — money that goes further in a country where a solid hotel room outside metro cities costs ₹3,000 a night.

The value proposition extends beyond fares. Indian domestic airports are crowded, security queues can stretch past an hour at peak times, and flight delays during monsoon season are endemic. The Vande Bharat Sleeper's overnight schedule — board at 8 p.m., arrive at 10 a.m. — saves a hotel night and delivers you rested, not frazzled by a 4 a.m. airport alarm.

## What Still Needs Work

The service is not without rough edges. Early passengers on the Howrah–Kamakhya route have noted that onboard catering remains uneven — the pantry car system is still being refined, and meal variety lags behind what the Rajdhani once offered at its best. Wi-Fi connectivity drops in stretches of West Bengal and Assam where infrastructure hasn't caught up with the train's technology.

Platform boarding at Indian stations remains the familiar scramble, and the trains themselves are not immune to delays caused by track-sharing with freight corridors. Indian Railways is working on dedicated high-speed corridors for the long term — seven new corridors were recently approved — but that infrastructure is years away.

## Why the Diaspora Should Track This

Every NRI who has organised a family trip to India knows the logistical headache of internal travel. Domestic flights are expensive during peak periods, unreliable during monsoon, and exhausting with elderly parents or young children. The Vande Bharat Sleeper is not a luxury product — it is a practical one, built for the kind of 800-to-1,200-kilometre overnight journey that defines travel within the subcontinent.

As the network expands through 2026 and 2027, the trains will gradually cover the corridors the diaspora uses most: Delhi to ancestral towns in UP and Bihar, Mumbai to family in Karnataka and Goa, Chennai to Hyderabad for long-weekend visits. For NRIs conditioned to assume that Indian trains are a downgrade, the Vande Bharat Sleeper is an invitation to reconsider.
"""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Vande Bharat Sleeper Is Quietly Replacing the Rajdhani — and It Costs Less Than a Domestic Flight",
    "subheadline": "The first overnight Vande Bharat trains are running, with 12 more deploying this year. Fares start at ₹2,300. The Rajdhani generation should pay attention.",
    "slug": make_slug("vande-bharat-sleeper-trains-nri-travel-india-overnight"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs organising family travel within India face expensive monsoon-season flights and ageing overnight trains — the Vande Bharat Sleeper offers AC comfort at a third of the airfare on the corridors the diaspora uses most.",
    "tags": ["travel", "indian-railways", "vande-bharat", "trains", "nri", "infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wikipedia — Vande Bharat Sleeper Express", "url": "https://en.wikipedia.org/wiki/Vande_Bharat_Sleeper_Express"},
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/mumbai-bengaluru-vande-bharat-sleeper-train/"},
        {"name": "Metro Rail Today", "url": "https://www.metrorailtoday.com/article/icf-to-roll-out-first-24-coach-vande-bharat-sleeper-train-by-end-of-2026"},
        {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/national/indian-railways-2026-27-hydrogen-train-vande-bharat-new-rules-10260412"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Vande_Bharat_Sleeper_Express.jpg/1280px-Vande_Bharat_Sleeper_Express.jpg",
    "image_caption": "A Vande Bharat Sleeper Express on standby at an Indian railway platform",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}

# ──────────────────────────────────────────────────────────────
# INSERT
# ──────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
