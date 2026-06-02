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
        "headline": "Air India Express Just Launched Bengaluru–Phuket Nonstops — Starting at ₹13,745",
        "subheadline": "Four weekly flights on the Boeing 737 MAX connect India's tech capital to Thailand's most popular island, and the timing is perfect for monsoon-escape planners.",
        "slug": make_slug("air-india-express-bengaluru-phuket-nonstop-thailand"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru is home to over 200,000 NRIs and returning diaspora professionals in its tech corridor. Direct Phuket access means a 3.5-hour weekend beach escape without transiting through Bangkok or Kuala Lumpur — a genuine game-changer for short-break travelers.",
        "tags": ["travel", "airlines", "air-india-express", "phuket", "thailand", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AviationA2Z", "url": "https://www.aviationa2z.com/index.php/2026/06/01/air-india-express-bengaluru-phuket/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/starting-at-rs-13745-bengaluru-gets-direct-flights-to-phuket-thanks-to-air-india-express/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/news/air-india-express-launches-direct-flights-between-bengaluru-and-phuket/"}
        ]),
        "score_total": 76,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/14659909/pexels-photo-14659909.jpeg",
        "body": """Air India Express inaugurated direct service between Bengaluru and Phuket on June 1, adding Thailand's most visited island to a network that now spans eight international destinations from Kempegowda International Airport. Fares start at ₹13,745 one way — roughly $160 — on a Boeing 737-8 MAX, with four weekly frequencies covering Monday, Friday, Saturday, and Sunday departures.

## The Schedule

The timetable is built for leisure travel. Monday and Saturday flights leave Bengaluru at 10:35 AM and touch down in Phuket at 3:50 PM local time, giving passengers a full afternoon to reach their hotel. Friday departures are slightly later at 11:25 AM, arriving at 4:40 PM. Sunday flights depart at 11:15 AM. Return legs all depart in the late afternoon — between 4:45 and 5:40 PM — and land back in Bengaluru by early evening, making it possible to squeeze a long weekend out of three calendar days.

The flight time is roughly three hours and forty-five minutes, comparable to Bengaluru–Colombo or Bengaluru–Male.

## Why This Route Matters

Phuket has long been one of the top three international beach destinations for Indian travelers, alongside Bali and the Maldives. But until now, getting there from South India meant either transiting through Bangkok's Suvarnabhumi or connecting in Kuala Lumpur — adding four to eight hours and considerable cost to the journey.

Air India Express already flies Bengaluru–Bangkok (launched October 2025) and Hyderabad–Phuket. The new Bengaluru link closes the last major gap for South Indian outbound leisure traffic to Thailand.

For the estimated 200,000-plus NRI professionals and returning diaspora workers in Bengaluru's tech corridor, the calculus is simple: a Friday departure and Monday return means a three-night Phuket trip without burning a single vacation day. That is the kind of math that fills planes.

## Thailand Visa Update

One wrinkle: India is no longer on Thailand's visa-free list. As of early 2026, Indian passport holders must obtain a Visa on Arrival (VOA) at Phuket International Airport, which costs 2,000 Thai baht (approximately ₹5,000 or $58). The process typically takes 30 to 60 minutes at the immigration counter. Travelers need a passport valid for at least six months, a confirmed return ticket, proof of accommodation, and 10,000 baht in cash or equivalent.

This is a downgrade from the visa-free arrangement that was briefly in place during 2024, and it adds friction — but not enough to dent demand on a leisure-heavy route.

## The Bigger Picture

Air India Express now operates close to 500 weekly flights from Bengaluru alone, connecting 31 domestic and eight international destinations. The carrier was named Airline of the Year in both domestic and international categories at Bengaluru Airport's Pinnacle Awards earlier this year and received the Domestic Connectivity Award at Wings India 2026.

Under Tata Group ownership, the airline is executing a clear strategy: dominate India's budget international market before IndiGo's own Airbus A350 widebodies arrive. Phuket is a textbook move — a proven demand market with limited direct competition from Bengaluru.

For NRIs toggling between Bengaluru's tech campuses and Southeast Asia's beaches, the message is straightforward: the nonstop era from South India's biggest city just got a little wider."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Monsoon Is Forecast to Be the Weakest in 11 Years — What NRIs Planning Summer Trips Need to Know",
        "subheadline": "A Super El Niño is suppressing rainfall to 90% of normal, raising heatwave risks across the subcontinent and scrambling the usual monsoon travel playbook.",
        "slug": make_slug("super-el-nino-india-monsoon-weak-nri-summer-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of NRIs travel to India between June and September for family visits, weddings, and monsoon tourism. A weaker monsoon means hotter cities, potential water shortages at popular destinations, and disrupted monsoon-centric experiences — from Kerala's Ayurveda season to Meghalaya's waterfalls.",
        "tags": ["travel", "monsoon", "el-nino", "weather", "india", "summer-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-29/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/monsoon-2026-forecast-driest-in-11-years-el-nino-imd-rainfall-prediction-11748604218556.html"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/agri-business/el-nino-knocking-on-the-door-as-oceans-warm-rapidly-says-un-weather-body/article69640802.ece"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/26202090/pexels-photo-26202090.jpeg",
        "body": """The India Meteorological Department has issued its starkest monsoon forecast in over a decade: the 2026 southwest monsoon is expected to deliver only about 92 percent of the long-period average rainfall, which would make it the driest season since 2015. The culprit is a rapidly developing Super El Niño in the Pacific, which the World Meteorological Organization confirmed on June 2 is among the strongest warming events in recorded history.

For the millions of NRIs who travel to India between June and September — for weddings, family visits, or the monsoon tourism season — this is not abstract climate science. It will shape what your trip looks like on the ground.

## What the Numbers Mean

Normal monsoon rainfall for India is roughly 87 centimeters spread across the June-to-September season. At 92 percent, the country would receive around 80 cm — a deficit of 7 cm that sounds modest until you consider how unevenly it distributes. The IMD expects central and northwestern India to bear the worst shortfalls, while some pockets in the northeast and far south may see near-normal or above-normal rain.

The last time India experienced back-to-back weak monsoons was 2014-2015, when rainfall fell to 88 and 86 percent of normal respectively. Those years saw reservoir levels plummet, crop failures in rain-fed regions, and water rationing in cities as large as Bangalore and Chennai.

## The Heatwave Factor

El Niño is not just about rain. The IMD has warned that maximum and minimum temperatures in June will stay above average across southern, western, central, and northern India, with more heatwave days than usual. As of early June, 97 of the 100 warmest cities globally are in India, according to recent analysis.

For NRIs arriving from air-conditioned American cities, the heat will be the first thing you notice. Delhi, Lucknow, Jaipur, and Nagpur are recording temperatures above 45°C (113°F). Even hill stations like Dehradun and Shimla are running 3-4 degrees above their seasonal averages.

## What This Means for Your Trip

**Kerala Ayurveda season**: Traditionally, the monsoon months are considered the most effective for Ayurvedic treatments — the humidity opens pores and enhances oil absorption. A weaker monsoon does not cancel this, but resorts may face water supply constraints. Book properties with their own wells or rainwater harvesting.

**Western Ghats waterfalls and treks**: The iconic monsoon experiences — Dudhsagar Falls, Valley of Flowers, Coorg's coffee estates in the rain — all depend on heavy rainfall. A 10 percent deficit means some cascades may be underwhelming in June and early July. Late August and September, when IMD expects the monsoon to recover somewhat, are safer bets.

**Rajasthan and Gujarat**: These already arid states will be drier than usual. Heritage tourism (Jaipur, Jodhpur, Udaipur) is still feasible, but plan outdoor sightseeing for early morning or evening. Midday temperatures will be punishing.

**Ladakh and the Himalayas**: Here, El Niño may actually help. Ladakh is a rain-shadow desert — its appeal lies in dry, clear skies. A weaker monsoon means fewer landslides on the Manali-Leh highway and more reliable road access. This could be an unusually good summer for high-altitude road trips.

**Wedding travel**: June weddings in North India under these conditions will test everyone's patience. Outdoor mandaps are risky not because of rain but because of extreme heat. Ensure venues have backup cooling arrangements.

## The Practical Checklist

Travel insurance that covers trip disruption due to extreme weather is worth the premium this year. Carry oral rehydration salts and sunscreen rated for Indian UV levels. Confirm water availability at your accommodation before booking — smaller heritage hotels and homestays are the most vulnerable. Domestic flights may face more turbulence and delays as atmospheric instability increases, so build buffer days into tight itineraries.

The monsoon will still arrive. It will still rain. But for the first time in 11 years, it will rain meaningfully less — and the India you land in this summer will feel hotter, drier, and more stressed than the one your family remembers."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Zoji La Tunnel Is About to Punch Through — and Ladakh Will Never Be Inaccessible Again",
        "subheadline": "At 13 kilometers and 11,500 feet, the world's highest bi-directional road tunnel is over 80 percent complete, promising year-round access to a region that was cut off for half the year.",
        "slug": make_slug("zoji-la-tunnel-ladakh-all-weather-connectivity-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Ladakh is one of the top bucket-list destinations for diaspora Indians, but the narrow June-September road window has always forced NRIs into peak-season pricing and crowded permits. All-weather connectivity via the Zoji La tunnel will open winter Ladakh for the first time, enable flexible trip planning, and dramatically lower costs for the growing NRI adventure tourism segment.",
        "tags": ["travel", "infrastructure", "ladakh", "tunnel", "kashmir", "road-trip"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Zoji-la_Tunnel"},
            {"name": "TunnelBuilder", "url": "https://tunnelbuilder.com/News/Zoji-La-Tunnel-Engineering-an-All-Weather-Lifeline-to-Ladakh.php"},
            {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/research/developing-all-weather-strategic-connectivity-to-kashmir-and-ladakh"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Zojila_Road.jpg",
        "body": """Somewhere beneath 11,500 feet of Himalayan rock, between Sonamarg in Kashmir and Dras in Ladakh, two excavation teams are closing in on each other. The Zoji La Tunnel — 13.15 kilometers long, horseshoe-shaped, and bored through some of the most geologically unstable terrain on earth — crossed the 80 percent physical completion mark earlier this year. The breakthrough, when the two headings meet, is targeted for mid-2026.

When it opens, it will be the world's highest bi-directional road tunnel and the longest single-tube tunnel at such altitude. More importantly, it will end Ladakh's centuries-old isolation from the Indian mainland during winter.

## The Problem It Solves

The Zoji La Pass sits at 11,578 feet on National Highway 1 between Srinagar and Leh. For roughly seven months every year, from October through April, heavy snowfall and avalanches render the pass impassable. During this window, Ladakh's 300,000-plus residents rely entirely on airlifts and pre-winter stockpiling for everything from food to fuel to medicine.

For tourists, the closure compresses Ladakh's entire tourism season into a frantic five-month window — June through October — during which permit queues are long, hotels are overpriced, and the Manali-Leh and Srinagar-Leh highways are clogged with convoys. The adventure-tourism experience that draws visitors from around the world is, paradoxically, undermined by the very crowds that come during the only months when access is possible.

The tunnel will cut the journey between Sonamarg and Dras from three to four hours in good weather to approximately 15 minutes. Combined with the adjacent Z-Morh tunnel (6.5 km, already completed), the entire Srinagar-Leh corridor will become all-weather for the first time in history.

## Engineering at the Edge

Building a tunnel at this altitude, through the young and fractured Himalayan geology, has been an extraordinary engineering challenge. The project uses the New Austrian Tunnelling Method — controlled drilling and blasting in short cycles, followed by immediate stabilization with sprayed concrete, rock anchors, and steel supports. Continuous tunnel boring machines were ruled out because the rock is too unpredictable: water ingress, fault zones, and squeezing ground conditions change every few meters.

The project is being executed by Megha Engineering and Infrastructures Limited (MEIL) under the National Highways and Infrastructure Development Corporation. As of March 2025, 12 of the 13.15 kilometers of excavation had been completed. The budget stands at ₹6,809 crore (approximately $815 million), including 17 kilometers of approach roads.

The original completion target was September 2026, but COVID-era delays, security incidents, and extreme weather have pushed the revised timeline to February 2028 for full commissioning. The breakthrough itself, however, is expected much sooner.

## What Changes for NRI Travelers

The implications for diaspora tourists are significant. Ladakh consistently ranks among the top five dream destinations in surveys of Indian Americans, alongside Rajasthan, Kerala, Goa, and the Himalayas broadly. But the logistics have always been daunting: flights to Leh are expensive and limited, the road approaches are seasonal, and altitude sickness hits harder when you rush in during a narrow window.

Year-round road access changes the equation. Winter Ladakh — with its frozen Zanskar River treks (the Chadar Trek), snow leopard safaris in Hemis, and empty monasteries — has been accessible only to the most determined travelers willing to fly into Leh's unpredictable airport. A reliable all-weather highway from Srinagar opens this world to anyone with a rented SUV and a week to spare.

It also spreads tourism load across 12 months instead of five, which should moderate peak-season hotel rates and reduce the environmental pressure on fragile high-altitude ecosystems that are already showing signs of over-tourism.

## The Bigger Connectivity Story

The Zoji La tunnel does not exist in isolation. It is one of 31 road tunnels under construction across Jammu & Kashmir and Ladakh at a combined cost of ₹1,400 billion ($17.5 billion). The Chenab Rail Bridge — the world's highest railway arch bridge, taller than the Eiffel Tower — recently carried its first Vande Bharat Express, making the Jammu-Srinagar rail journey possible in three hours instead of seven. The Shinkun La tunnel on the Manali-Leh highway will add a second all-weather road corridor from Himachal Pradesh.

Together, these projects are rewriting the accessibility map of India's most dramatic landscape. For NRIs who have been putting off the Ladakh trip because the logistics felt too uncertain, the window of possibility is about to become a permanent open door."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
