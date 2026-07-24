#!/usr/bin/env python3
"""Travel writer for The Videshi — July 2, 2026 run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
# ARTICLE 1: Dubai Airport July Rush
# ──────────────────────────────────────────────────────────────

art1_body = """Dubai International Airport is bracing for one of its most intense fortnights of the year. Around three million passengers are expected to move through DXB in the first half of July, with a departure surge beginning July 2 and the busiest day forecast for July 12, when more than 225,000 travellers will pass through the terminals in a single day.

For the roughly 1.8 million Indian Americans who fly through Dubai every year — many of them connecting to Delhi, Mumbai, Hyderabad, Bengaluru and Chennai — this is more than a headline about a foreign airport. It is the chokepoint between your home in the US and your family's home in India.

## India is DXB's biggest market — by a wide margin

India remained Dubai International's largest source country in 2025, contributing 11.9 million passengers out of DXB's record 95.2 million total. Saudi Arabia followed at 7.5 million; the UK at 6.3 million. Mumbai, Delhi and Kochi are consistently among the most-served routes from DXB, and Emirates alone operates more than 170 weekly flights to Indian cities.

In 2026, DXB is forecast to handle 99.5 million passengers — pushing the airport to the edge of its physical capacity. The $35 billion expansion of Al Maktoum International Airport, Dubai's second hub, is designed to eventually absorb DXB's overflow, but that full transition isn't expected until 2032.

## Why this July is different

Two factors are compounding the usual summer rush. First, Gulf airspace has fully reopened after months of disruptions tied to the Iran conflict earlier this year. The US-Iran memorandum of understanding signed on June 17 and the Doha peace discussions on June 30 have stabilised regional aviation. Airlines that had suspended or rerouted Gulf services are restoring capacity — which means more passengers flowing through the hub.

Second, jet fuel prices have fallen sharply. The global Baltic Air Freight Index dropped 5% in the last week of June, and airlines are beginning to pass some of that relief through to fares. For NRIs booking late-summer trips home, the pricing environment is more favourable than it has been in months.

## What NRI transit passengers should know

DXB's summer-readiness plan includes several measures worth noting if you're connecting through Dubai in the coming weeks:

**Arrive early, but not too early.** Dubai Airports recommends arriving no earlier than three hours before departure. Terminal 3 — the Emirates hub where most India-bound flights depart — will see the heaviest traffic.

**Use Smart Gates.** Children over 12 can now use automated passport gates, which significantly cuts immigration queues for families. If you're travelling with teenagers, this alone can save 30–40 minutes.

**Skip the airport check-in line.** DXB's DUBZ service allows passengers to complete check-in and baggage drop from their hotel or home before heading to the airport — a useful option during peak days.

**Transfer traffic is half the load.** Around 50% of DXB's July traffic is connecting passengers, not origin/destination. If you're transiting, your main bottleneck is the transfer security screening between concourses, not immigration.

## The bigger picture

Dubai's dominance as a connecting hub for India-US travel isn't going away. Emirates and flydubai together serve more Indian cities than any other foreign airline group, and for NRIs in cities without nonstop India flights — think Houston, Dallas, Boston, Atlanta — a Dubai connection remains the default option.

The July rush is a stress test, but DXB has consistently delivered: 98.8% of arriving passengers cleared passport control within 15 minutes in 2025, and 98.9% cleared security in under five. The airport works. It just works best when you plan for the crowd."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Million Travellers Will Pass Through Dubai This Fortnight — and Most of Them Are Indian",
    "subheadline": "DXB is entering its most intense July on record. India remains the airport's largest market, and NRIs connecting through Dubai need a plan.",
    "slug": make_slug("dubai-airport-july-rush-india-nri-transit-guide"),
    "category": "travel",
    "vertical": "travel",
    "is_editorial": False,
    "diaspora_angle": "Most NRI flights to India route through Dubai, and the July rush directly affects connection times, queues, and fares for Indian Americans flying home.",
    "tags": ["travel", "dubai", "airports", "nri", "emirates", "transit"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Dubai Airports / WAM", "url": "https://www.gulftime.ae/dxb-set-for-busy-start-to-summer-as-daily-guest-numbers-top-200000/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/dubais-dxb-airport-forecast-handle-nearly-100-million-passengers-this-year-2026-02-11/"},
        {"name": "Time Out Dubai", "url": "https://www.timeoutdubai.com/news/dubai-international-airport-dxb-reveals-busiest-summer-2026-travel-day"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/uae-aviation-spotlight-turns-to-dubai-international-airport/"}
    ]),
    "score_total": 80,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg/1280px-Dubai_International_Airport_interior_of_Terminal_3%2C_2019%2C_04.jpg",
    "image_caption": "Interior of Dubai International Airport Terminal 3, the Emirates hub serving most India-bound flights",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 2: Rath Yatra 2026 — NRI Travel Guide
# ──────────────────────────────────────────────────────────────

art2_body = """The chariots are built. The ropes are coiled. And on July 16, the three towering wooden rathas of Lord Jagannath, Lord Balabhadra and Goddess Subhadra will roll down Bada Danda — Puri's Grand Road — in the most spectacular religious procession on Earth.

Rath Yatra 2026 runs from July 16 to approximately July 25, and if you're an NRI who has never witnessed it in person, this is the year to seriously consider it. Here is everything you need to plan the trip.

## The schedule you need to know

The festival is not a single day — it's a ten-day ritual sequence, and several days are worth attending beyond the main procession:

- **July 16 (Thursday) — Rath Yatra:** The main event. The three chariots are pulled from Singhadwara (the Lion Gate of Jagannath Temple) to Gundicha Mandir, roughly 3.5 kilometres away. The procession typically starts around 7 AM.
- **July 19 — Hera Panchami:** Goddess Lakshmi visits Gundicha Mandir, upset that Lord Jagannath left without her. A beautifully human drama.
- **July 22 — Bahuda Yatra:** The return journey. Chariots are pulled back to the main temple.
- **July 23 — Suna Besha:** The deities are adorned with 208 kilograms of gold ornaments. This is the single most photographed darshan of the year.
- **July 25 — Niladri Bije:** Lord Jagannath re-enters the sanctum, persuaded by Lakshmi. The festival's emotional finale.

**Important:** Exact dates for Bahuda Yatra and Suna Besha are determined by the tithi (lunar calendar) and confirmed by the Shri Jagannath Temple Administration closer to the date. Check shrimandir.gov.in before booking.

## Getting there

**By air:** Biju Patnaik International Airport in Bhubaneswar (BBI) is the nearest major airport, roughly 60 kilometres from Puri. IndiGo, Air India and Vistara operate daily flights from Delhi, Mumbai, Bengaluru, Hyderabad and Kolkata. From the US, your best routing is through Delhi or Mumbai with a domestic connection — Air India's nonstop SFO-DEL and JFK-DEL services connect well.

**By train:** Puri has its own railway station with direct trains from Delhi (Purushottam Express, ~30 hours), Kolkata (~8 hours), and Bengaluru (~28 hours). During Rath Yatra, Indian Railways typically runs special trains — check IRCTC closer to the date.

**Ground transport:** From Bhubaneswar, the NH316 highway to Puri takes about 90 minutes by car. Ola and Uber operate in Bhubaneswar; pre-arranged cabs are the safer bet during the festival.

## Where to stay

Hotels on and near Grand Road in Puri book out months ahead for Rath Yatra. Your realistic options:

- **Puri:** If you haven't booked yet, check Mayfair Heritage, Hotel Nilachal Ashok or the Toshali Sands resort (slightly outside town). Budget guesthouses along Chakratirtha Road still have availability in early July.
- **Bhubaneswar (backup):** Trident Bhubaneswar, Mayfair Lagoon or any of the business hotels near the airport. The 60-kilometre drive is manageable if you leave early.
- **Konark (scenic option):** The Sun Temple town is just 35 kilometres from Puri and typically has rooms available. A quieter base.

## What NRIs get wrong

**Arriving too late.** The procession starts at dawn. If you reach Bada Danda at 8 AM, you're behind a wall of humanity. Be there by 5:30 AM.

**Skipping July 15.** Nava Jauban Darshan happens the day before the main procession. Crowds are 30–40% lighter, and you get a closer darshan.

**Missing Mahaprasad.** Anand Bazaar inside the temple compound serves sacred food — but only until noon on festival days. It's one of Puri's most meaningful experiences, and most tourists don't know about it.

**Over-packing.** The crowd is dense, the heat is real, and you'll be standing for hours. Carry water (at least two litres per person), a phone, and nothing else. Leave valuables at the hotel.

## The NRI perspective

For second-generation Indian Americans, Rath Yatra is often the first encounter with Hindu India at its most raw and communal. There are no velvet ropes, no VIP lines, no curated experience. You're standing in a crowd of a million people, pulling a rope attached to a 14-metre chariot, sweating in the Odisha sun. It's overwhelming and unforgettable.

Non-Hindus can fully participate in the street procession — only the temple sanctum is restricted to Hindus. The festival on the street is for everyone.

**Pro tip:** Walk toward the Gundicha Temple end of Grand Road, away from the starting point where most spectators cluster. The chariots slow down near Gundicha, and you can actually grab the rope and pull."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Puri's Rath Yatra Begins July 16 — an NRI's Guide to India's Greatest Chariot Festival",
    "subheadline": "The ten-day festival draws a million devotees to Odisha's coast. Here's how to plan the trip from the US, where to stay, and what most tourists get wrong.",
    "slug": make_slug("puri-rath-yatra-2026-nri-travel-guide"),
    "category": "travel",
    "vertical": "travel",
    "is_editorial": False,
    "diaspora_angle": "Rath Yatra is one of the few Indian festivals that second-generation NRIs consistently name as a bucket-list experience — and it's accessible even to non-Hindus on the street.",
    "tags": ["travel", "rath-yatra", "puri", "odisha", "festivals", "pilgrimage", "nri"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/entertainment/3381002-epic-rath-yatra-and-digital-initiative-elevate-jagannatha-culture-to-global-stage"},
        {"name": "HinduTone", "url": "https://hindutone.com/jagannath-rath-yatra/"},
        {"name": "Heritage Tours Orissa", "url": "https://heritagetoursorissa.com/rath-yatra/"},
        {"name": "TripAdvisor Puri Forum", "url": "https://www.tripadvisor.co.uk/ShowTopic-g297662-i9237-k15117411-Jagannath_Rath_Yatra_2026-Puri_Puri_District_Odisha.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Shri_Jagannath_temple.jpg/1280px-Shri_Jagannath_temple.jpg",
    "image_caption": "The Shri Jagannath Temple in Puri, starting point of the annual Rath Yatra chariot procession",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────────────────────
# ARTICLE 3: Kerala Monsoon Ayurveda + Travel
# ──────────────────────────────────────────────────────────────

art3_body = """Most NRIs plan their India trips for December or January — peak wedding season, school holidays, comfortable weather. Kerala's tourism industry has spent years trying to convince them that they're timing it exactly wrong.

The monsoon, which arrived in Kerala on May 24 this year — eight days ahead of schedule — transforms the state into something visitors in winter never see. Rivers swell, waterfalls thunder, tea plantations glow an electric green, and hotel rates drop 30–50% from their December peaks. More importantly, this is Karkkadakam — the traditional Ayurvedic rejuvenation season, when practitioners say the humid monsoon air opens the body's pores and makes it most receptive to therapeutic oils and herbal treatments.

## Why Ayurveda works best in monsoon

This isn't marketing. Kerala's government-backed monsoon tourism campaign explicitly promotes June through August as the ideal window for Panchakarma and other traditional treatments. The science is straightforward: monsoon humidity softens the skin and tissues, allowing medicated oils to penetrate more effectively. The cooler temperatures (23–29°C, compared to 33–36°C in April) mean patients tolerate the intensive oil-based therapies more comfortably.

Resorts and wellness centres across Kerala are leaning into this. Kerala Business News reported this week that hotels, resorts and tour operators are introducing discounted monsoon packages combining Ayurveda therapies, cultural activities and sightseeing experiences. Many are bundling 7-day and 14-day Panchakarma programmes with accommodation and vegetarian meals — the traditional dietary requirement during treatment.

For NRIs dealing with the accumulated stress of American work culture, a two-week Ayurveda retreat in Kerala during monsoon is both more authentic and dramatically cheaper than trying to squeeze one into a December holiday trip.

## The destinations worth your time

**Kochi and Alleppey** are your entry points to the backwaters. Houseboat cruises run through the monsoon — operators adjust schedules for heavy rain, but the rain-swollen waterways are actually more scenic. A two-night houseboat cruise from Alleppey costs ₹8,000–15,000 ($95–180) per night in July, versus ₹20,000–35,000 in December.

**Munnar** is where the monsoon puts on its best show. The tea plantations that look pleasant in winter become luminous in the rain, and the mist rolling through the valleys is why photographers fly across the world to be here in July. Rooms at properties like Windermere Estate or Spice Tree start under $100 in monsoon — half their winter rates.

**Wayanad** has recovered from the 2024 landslide damage and is welcoming visitors again. Its northern Kerala location means dense tropical forest, wildlife (Wayanad Wildlife Sanctuary borders Bandipur and Mudumalai) and fewer crowds than Munnar, though the Chooralmala-Mundakkai area remains restricted.

**Thekkady and Periyar** offer monsoon wildlife viewing at its best. Tigers, elephants and bison are more active during the rains, and the Periyar Lake boat ride through morning mist is worth the early wake-up call.

## Practical advice for NRI families

**Flights:** From the US, Kochi (COK) and Thiruvananthapuram (TRV) are your best entry points. Air India flies nonstop from Delhi and Mumbai to both cities; from the US, connect through Delhi or Mumbai. August fares on the SFO-Delhi-Kochi routing have dropped below $800 round-trip on Etihad and Gulf Air via their Gulf hubs.

**What to pack:** Light cotton clothes, a good rain jacket (not an umbrella — you'll need both hands free), waterproof sandals, and insect repellent. The rain comes in intense afternoon bursts; mornings are often sunny.

**Leeches:** Yes, really. If you're trekking in Munnar or Wayanad during monsoon, leeches are part of the deal. Wear long socks tucked into your trousers, carry salt, and don't panic. They're harmless.

**Road conditions:** Landslides can close mountain roads temporarily, especially the Kochi-Munnar highway and Wayanad's ghat roads. Check Kerala State Disaster Management Authority advisories before driving mountain routes. The Kottayam-Kumily road to Thekkady is generally more reliable.

**The value proposition:** A 10-day Kerala monsoon trip — including flights, mid-range hotels, Ayurveda sessions and houseboat cruise — can realistically come in under $2,500 per person from the US West Coast. The same itinerary in December would cost $4,000–5,000. For a family of four, that's $6,000–10,000 in savings. The monsoon isn't a compromise. It's the better trip."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Kerala's Monsoon Is Peak Travel Season — and NRIs Are Paying Double to Visit at the Wrong Time",
    "subheadline": "Hotel rates drop by half, Ayurveda works best in the rain, and the landscape is at its most beautiful. Why monsoon Kerala deserves a spot on every NRI's calendar.",
    "slug": make_slug("kerala-monsoon-ayurveda-travel-nri-guide"),
    "category": "travel",
    "vertical": "travel",
    "is_editorial": False,
    "diaspora_angle": "Most NRIs visit Kerala in December at peak prices. Monsoon season offers better Ayurveda, better scenery and 30-50% lower costs — a $6,000-10,000 saving for a family of four.",
    "tags": ["travel", "kerala", "monsoon", "ayurveda", "wellness", "backwaters", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Kerala Business News", "url": "https://keralabusinessnews.com/monsoon-tourism-boosts-kerala-travel-industry/"},
        {"name": "Kerala Tourism (Official)", "url": "https://www.keralatourism.org/kerala-in-june/"},
        {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-india/"},
        {"name": "Travel Triangle", "url": "https://www.traveltriangle.com/blog/monsoon-in-kerala/"}
    ]),
    "score_total": 78,
    "status": "review",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Kerala_backwaters%2C_Houseboats%2C_India.jpg/1280px-Kerala_backwaters%2C_Houseboats%2C_India.jpg",
    "image_caption": "Traditional houseboats on the Kerala backwaters near Alleppey, a popular monsoon-season cruise destination",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ──────────────────────────────────────────────────────────────
# INSERT ALL
# ──────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
