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
        "headline": "Air India Is Bleeding $2.8 Billion a Year — and NRIs Flying Home This Summer Will Feel It",
        "subheadline": "Tata Group has ordered its flagship carrier to slash losses. That means fewer flights to North America, deferred jet deliveries, and thinner service on the routes Indian Americans depend on most.",
        "slug": make_slug("air-india-losses-flight-cuts-north-america-nri-summer"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Air India's deep cuts to North America routes — down 69% from January levels — directly squeeze the SFO-DEL, JFK-BOM, and ORD-HYD corridors that millions of NRIs rely on for summer family visits.",
        "tags": ["travel", "airlines", "air-india", "flights", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/air-india-seeks-defer-hundreds-jet-deliveries-sources-say-2026-06-12/"},
            {"name": "Livemint", "url": "https://www.livemint.com/industry/infrastructure/why-airlines-are-cutting-capacity-across-india-s-busiest-airports-and-routes-11718193827456.html"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/air-india-plans-flight-cuts-and-delivery-deferrals-amid-financial-pressure"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-plans-to-defer-delivery-of-hundreds-of-airbus-and-boeing-jets-amid-cost-cuts/article69679123.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Air_India_aircraft_at_Rajiv_Gandhi_International_Airport_01.jpg/1280px-Air_India_aircraft_at_Rajiv_Gandhi_International_Airport_01.jpg",
        "image_caption": "An Air India aircraft on the tarmac at Rajiv Gandhi International Airport in Hyderabad",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers are stark. Air India posted a record loss of roughly $2.8 billion in fiscal year 2025-26 — its worst financial performance since Tata Group acquired the carrier from the Indian government in January 2022. And Tata's response has been equally blunt: stop the bleeding, now.

That directive, first reported by Bloomberg and confirmed by Reuters this week, has triggered a cascade of cutbacks that will ripple directly through the diaspora travel corridors Indian Americans use most.

## Fewer Planes, Fewer Flights

Air India is now in discussions with Airbus and Boeing to defer delivery of as many as 500 aircraft. In 2023, flush with post-privatization ambition, the airline placed a landmark order for 470 jets — the largest in commercial aviation history at the time — with additional orders following in 2024. Most were scheduled for delivery in 2027 and 2028. Those plans are now on ice.

The immediate impact is already visible. According to OAG data reviewed by Mint, Air India operated 27% fewer flights in June compared to the same month last year. Air India Express, its low-cost subsidiary, cut 17% of flights over the same period.

The sharpest reductions have hit long-haul routes. North America-bound flights dropped from 177 in January to just 54 — a staggering 69% decline. Services to London, Paris, Frankfurt, New York, and San Francisco have all seen reduced frequencies. Flights to Australia and the Southwest Pacific fell 35%.

## A Perfect Storm

The financial crisis didn't arrive overnight. Air India has been navigating a brutal combination of headwinds: the ongoing Iran conflict has pushed Brent crude above $96 a barrel, driving jet fuel costs to record highs. Pakistan's continued airspace ban forces India-bound flights from Europe and North America onto longer, costlier routing through the Arabian Sea or Central Asia. And the shadow of a fatal Boeing 787 crash a year ago still lingers over passenger confidence.

Meanwhile, rival IndiGo — India's largest carrier by market share — posted its own loss of ₹2,394 crore and has signalled only single-digit capacity growth for the year. IndiGo has trimmed some international operations but maintained most European frequencies, restoring about two-thirds of its West Asia and Europe services by May.

## What NRIs Should Expect This Summer

For the 4.4 million Indian Americans who make the SFO-DEL, JFK-BOM, ORD-HYD, and LAX-BLR run each year, the math is simple: fewer seats plus steady demand equals higher fares. Analysts estimate international fares on India routes are already 20-40% above year-ago levels — and the peak summer travel window from July through September will only tighten supply further.

The reduction in nonstop options pushes more travelers onto connecting itineraries through Gulf hubs like Dubai, Doha, and Abu Dhabi. But even that fallback is complicated: Gulf routing has been disrupted by the West Asia conflict, with several carriers adjusting schedules around the Strait of Hormuz.

## How to Navigate It

Diaspora travelers still have options, but they require planning. Emirates, Qatar Airways, and Etihad continue to operate robust schedules through their Gulf hubs, though connection times have lengthened. United Airlines and American Airlines maintain codeshare arrangements on select India routes. IndiGo's growing long-haul network — including its Delhi-London Heathrow service with 12 weekly flights — offers a budget-carrier alternative that didn't exist two years ago.

The practical advice: book early, stay flexible on dates, and consider off-peak departures in mid-week slots. For NRIs with flexibility on their India end, secondary airports like Kochi, Ahmedabad, and Hyderabad sometimes offer better availability than the saturated Delhi and Mumbai gates.

Air India's transformation under Tata was always going to be a multi-year project. But for the diaspora travelers who form the backbone of India-US aviation demand, the turbulence is happening right now — and it's hitting their wallets first."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Monsoon Just Hit India — and It's the Best-Kept Secret for NRIs Planning a Trip Home",
        "subheadline": "Off-peak prices, thinner crowds, and some of the most dramatic landscapes on earth. Here's why smart diaspora travelers are booking July through September.",
        "slug": make_slug("india-monsoon-travel-guide-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs default to December or Diwali for India trips, but the monsoon window — when US kids are on summer break — offers dramatically lower prices, fewer crowds, and experiences you simply cannot get any other time of year.",
        "tags": ["travel", "india", "monsoon", "nri", "summer-travel", "budget"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Thomas Cook India / SOTC Travel", "url": "https://www.businessnewsthisweek.com/tune-in-to-magical-monsoon-holidays-10-destinations-that-shine-during-the-rains/"},
            {"name": "TripAdvisor India Forum", "url": "https://www.tripadvisor.co.uk/ShowTopic-g293860-i511-k14583372-Travelling_in_monsoon_season-India.html"},
            {"name": "Travel+Leisure Asia", "url": "https://www.travelandleisureasia.com/in/destinations/india/summer-holiday-destinations-2026/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/India_-_Udaipur_-_016_-_Monsoon_rains_on_Pichola_Lake_%281037769207%29.jpg/1280px-India_-_Udaipur_-_016_-_Monsoon_rains_on_Pichola_Lake_%281037769207%29.jpg",
        "image_caption": "Monsoon rains sweep across Lake Pichola in Udaipur, Rajasthan",
        "image_attribution": "Wikimedia Commons",
        "body": """Every year, millions of NRIs book their India trips for the same narrow windows: Diwali in October, Christmas in December, maybe a spring wedding in March. The monsoon — June through September — barely registers. Too wet, too unpredictable, too inconvenient.

That's a mistake. And the numbers prove it.

## The Price Gap Is Real

Hotel rates across India's top destinations drop 30-50% during monsoon season compared to the October-March peak. A heritage property in Udaipur that runs $400 a night during Diwali week can be had for $180 in August. Business-class award availability on India routes, bone-dry during the holidays, opens up considerably in July and September.

For NRI families with school-age children, the timing is ideal. American kids are on summer break from June through August — perfectly aligned with monsoon season. Instead of competing with every other diaspora family for overpriced December flights, you're traveling when the routes are quieter and the fares are gentler.

## Six Destinations That Peak in the Rain

**Udaipur, Rajasthan.** The so-called City of Lakes earns its name only during the monsoon, when Lake Pichola and Fateh Sagar actually fill to the brim. The Monsoon Palace — Sajjangarh — was built specifically for watching the rains roll in across the Aravallis. Rajasthan gets minimal rainfall overall, so you're not fighting waterlogged streets. You're watching a desert turn green.

**Kerala Backwaters.** Cruising Alleppey's canals on a kettuvallam houseboat in the rain is an experience that borders on spiritual. If you time it right, August brings the Nehru Trophy Snake Boat Race in Alappuzha — one of the world's most spectacular team sporting events, with long-keeled chundan vallams cutting through the backwaters at speed. Thomas Cook India and SOTC Travel rank it among their top monsoon picks for 2026.

**Mandu, Madhya Pradesh.** This medieval Afghan fortress city undergoes the most dramatic monsoon transformation in India. The Jahaz Mahal — Ship Palace — sits between two rain-fed reservoirs that fill to the point where the 15th-century structure appears to float. Misty ruins, empty pathways, zero crowds. It's India's best-kept heritage secret.

**Ladakh.** The ultimate monsoon hack. Sitting in the rain shadow of the Himalayas, Ladakh stays bone-dry while the rest of India soaks. June through September is actually peak season here — the only time the mountain passes are reliably open. Pangong Tso, Nubra Valley, and the monasteries of Leh are at their most accessible.

**Kashmir.** Srinagar, Gulmarg, and Pahalgam in August offer mild rainfall, temperatures in the low 20s Celsius, and green scenery that makes the Valley look like a postcard. Travel advisors on TripAdvisor's India forum specifically recommend Kashmir as one of the best August destinations — more peaceful than peak tourist months, fully accessible, and stunningly beautiful.

**Meghalaya.** Cherrapunji and Mawsynram hold the world record for rainfall, and visiting during monsoon is like stepping into a nature documentary. The living root bridges of Nongriat, waterfalls at full thunder, and clouds drifting through village streets create a landscape unlike anything else on the planet.

## Practical Notes for NRI Travelers

The Golden Triangle — Delhi, Agra, Jaipur — remains fully functional during monsoon. Infrastructure is solid, rainfall is manageable, and the Taj Mahal without 10,000 tourists in the frame is worth the trip alone.

Flights within India stay reliable. IndiGo and Air India's domestic networks operate normally through monsoon, though occasional delays are possible during heavy downpours in Mumbai and Chennai.

Pack accordingly: a solid waterproof jacket beats an umbrella, quick-dry clothing is essential, and waterproof bags for electronics are non-negotiable. Mosquito repellent is mandatory outside the dry zones.

One genuine caution: avoid monsoon trekking in the Western Ghats and Northeast unless you're experienced. Landslides are a real risk in Himachal Pradesh, Uttarakhand, and parts of Kerala during peak rainfall weeks. Stick to established routes and check state advisories before heading into hill country.

## The Bottom Line

The monsoon isn't a bug in India's travel calendar — it's a feature. Lower prices, thinner crowds, greener landscapes, and experiences you literally cannot have any other time of year. For NRIs who've been defaulting to December flights their entire lives, this summer might be the year to try something different."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
