#!/usr/bin/env python3
"""
Travel writer — July 4, 2026
Articles:
  1. Valley of Flowers peak bloom season guide for NRIs
  2. Indian summer travelers shifting to cooler European destinations
"""
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
    # ── Article 1: Valley of Flowers ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Valley of Flowers Just Entered Peak Bloom — and Most NRIs Have Never Heard of It",
        "subheadline": "The UNESCO World Heritage site in Uttarakhand explodes with 600 species of wildflowers between mid-July and mid-August. It caps visitors at 300 a day, costs under $10 to enter, and pairs perfectly with a summer trip home.",
        "slug": make_slug("valley-of-flowers-peak-bloom-nri-monsoon-trek-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families visiting India during the US summer break are already in the right window — the Valley of Flowers' peak bloom aligns perfectly with July-August school holidays, offering a once-a-year trekking experience most diaspora travelers never plan for.",
        "tags": ["travel", "trekking", "uttarakhand", "monsoon", "valley of flowers", "india", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/destinations/valley-of-flowers-uttarakhand-2026/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/adventure/valley-of-flowers-national-park-opens-for-2026-season"},
            {"name": "StayVista Journal", "url": "https://stayvista.com/journal/valley-of-flowers-trek-2026/"},
            {"name": "Discover with Dheeraj", "url": "https://discoverwithdheeraj.com/valley-of-flowers-2026/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Valley_of_flowers_national_park%2C_Uttarakhand%2C_India_03_%28edit%29.jpg/1280px-Valley_of_flowers_national_park%2C_Uttarakhand%2C_India_03_%28edit%29.jpg",
        "image_caption": "Alpine wildflowers in full bloom across the Valley of Flowers National Park in Uttarakhand's Garhwal Himalayas",
        "image_attribution": "Wikimedia Commons",
        "body": """There is a place in India where, for about four weeks every year, the ground itself turns into something improbable — a carpet of pink, yellow, blue, and white stretching across an alpine meadow at 3,600 metres, framed by glaciers on three sides. It is called the Valley of Flowers, and most people who grew up hearing about it have never actually been.

The park, a UNESCO World Heritage Site since 2005, reopened for its 2026 season on June 1 and will stay open until October 31. But the window that matters is narrower: peak bloom runs from mid-July to mid-August, when over 600 species of alpine wildflowers — including the elusive Himalayan Blue Poppy and the sacred Brahma Kamal — erupt across the valley floor simultaneously. By September, the colours are already fading.

## Why This Matters Right Now

For NRI families visiting India during the American summer break, the timing is almost too convenient. July and August are precisely when most diaspora families are back home — attending weddings, catching up with relatives, complaining about the humidity in Delhi. The Valley of Flowers sits just off this calendar, offering a dramatic detour that most visitors never consider.

The park is in Chamoli district, deep in Uttarakhand's Garhwal Himalayas. Getting there requires a trek — about 13 to 14 kilometres from Govindghat (the last motorable point) to Ghangaria, the base village, and another 4 kilometres from Ghangaria into the valley itself. It is not Everest. The trail is well-marked, relatively gentle by Himalayan standards, and classified as moderate difficulty. Plenty of first-time trekkers complete it every year.

## The Practicalities

Entry is capped at 300 visitors per day — a rule enforced since 2017 to protect the fragile ecosystem. During peak bloom, permits can sell out, so booking ahead through the official Uttarakhand forest portal (valleyofflower.uk.gov.in) is strongly recommended rather than hoping for a walk-in.

The costs are minimal. Indian nationals pay ₹200 (roughly $2.50) for a three-day entry permit, plus ₹20 per day in wildlife protection fees. Foreign nationals — which includes NRIs on US, UK, or Canadian passports — pay ₹800 (about $10) for the same three-day window.

Overnight stays inside the valley are not permitted. Visitors must enter after 7:00 AM, explore the meadows, and exit before the gates close. Ghangaria serves as the base, with a modest range of guesthouses and lodges. It is not luxurious, but it is functional, and the alternative — camping near the trailhead — is part of the charm.

## Pair It With Hemkund Sahib

One of the valley's lesser-known advantages is its proximity to Hemkund Sahib, the highest Sikh gurudwara in the world, perched at 4,329 metres on the shores of a glacial lake. The trek to Hemkund departs from the same base village, Ghangaria, and most itineraries combine both — the valley one day, the gurudwara the next. For the large Sikh diaspora in North America, the combination is particularly compelling.

Badrinath, one of Hinduism's holiest shrines, is only about 25 kilometres from Govindghat. A Valley of Flowers trip can easily extend into a Char Dham circuit for families combining trekking with pilgrimage.

## What NRIs Should Know Before Booking

**Fitness**: You do not need to be an athlete, but you do need to be able to walk 14 kilometres uphill at altitude. The trek from Govindghat to Ghangaria gains about 1,000 metres of elevation over 9 to 10 kilometres (after a 4-kilometre road stretch to Pulna). Acclimatise in Joshimath or Govindghat for a day if you are flying in from sea level.

**Monsoon gear**: It will rain. Waterproof jackets, trekking shoes with good grip, and dry bags for electronics are non-negotiable. The monsoon is not a bug here — it is the entire reason the flowers bloom.

**Getting there**: Fly into Dehradun (Jolly Grant Airport), then drive roughly 300 kilometres to Govindghat — a full day on mountain roads. Alternatively, Rishikesh is the nearest major railhead. Helicopter services to Ghangaria exist but operate weather-permitting and book up fast.

**When to go**: If you are reading this in early July, you are in the ideal booking window. Mid-July to mid-August is peak bloom. Late June offers fewer crowds but thinner floral coverage. After August, the flowers begin to thin, though the mountain scenery remains stunning.

The Valley of Flowers is one of those rare Indian destinations that rewards the diaspora traveller willing to step outside the wedding-and-relatives circuit. It is cheap, it is seasonal, and it is the kind of place that makes you understand why people trek in the first place."""
    },

    # ── Article 2: Indian travelers shifting to cooler European destinations ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Travellers Are Ditching the Mediterranean This Summer — and Heading for Scandinavia Instead",
        "subheadline": "Record heatwaves across Southern Europe are quietly reshaping where Indians spend their summer holidays. Switzerland, Norway, and Finland are the new hot picks — because they are not hot.",
        "slug": make_slug("indian-travelers-europe-heatwave-scandinavia-alps-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs in the US and UK planning European summer trips should note the shift — the same heatwaves pushing India-based travelers toward Scandinavia also affect diaspora families flying from New York or London to the continent.",
        "tags": ["travel", "europe", "scandinavia", "switzerland", "heatwave", "summer", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/indian-tourists-stay-committed-to-europe-summer-travel-despite-heatwaves-shift-bookings-towards-cooler-destinations/"},
            {"name": "Tata AIG / Dainik Bhaskar English", "url": "https://www.bhaskarenglish.in/national/travel/rich-indians-travel-shift-japan-maldives-top-new-holiday-picks-153225428.html"},
            {"name": "Morningstar / Marriott APEC Report", "url": "https://www.morningstar.com/news/pr-newswire/20260701ph29948/beyond-the-gen-z-myth-four-distinct-luxury-mindsets-reshaping-travel-in-asia-pacific"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17804518/pexels-photo-17804518.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The Swiss Alps in summer — increasingly preferred by Indian travellers seeking cooler European destinations",
        "image_attribution": "Pexels",
        "body": """Something has shifted in the way Indians plan their European summer holidays, and the numbers are making it hard to ignore.

Industry data released this week shows that Indian outbound travellers are increasingly bypassing the traditional Mediterranean circuit — Paris, Rome, Barcelona — in favour of cooler Northern European destinations. Switzerland, Norway, Sweden, Finland, and Denmark are all recording significant increases in Indian visitor interest for summer 2026, driven by a simple calculation: Southern Europe is too hot, and getting hotter.

## The Heatwave Effect

Europe's summers have been brutal in recent years, and 2026 is tracking no differently. Temperatures across Spain, Italy, and Greece have already crossed 40°C in early July, with forecasts pointing to sustained heatwaves through August. For Indian travellers accustomed to extreme heat at home, the appeal of escaping it — only to land in another furnace — is diminishing.

Travel operators say the shift is measurable. Bookings for Alpine regions, including Switzerland and Austria, have climbed sharply as families and long-stay holidaymakers seek destinations where summer means pleasant 20-degree days, not 42-degree afternoons. Coastal Northern France, the Netherlands, and the Baltic states are also picking up as alternatives to the Côte d'Azur and the Amalfi Coast.

"These destinations are now being actively promoted in India as 'summer-safe' European options, particularly for families," said one Mumbai-based travel operator cited in industry reports.

## The Numbers Behind the Shift

India's outbound travel market has matured rapidly. Over 40 per cent of Indian international travellers in FY 2025-26 chose destinations they had not visited before — places like South Korea, Egypt, Japan, and the Maldives — according to data from Tata AIG General Insurance Company. Southeast Asia alone accounted for 26 per cent of all Indian international travellers purchasing insurance, with year-on-year growth exceeding 10 per cent.

The average Indian international holiday now lasts about 24 days. For Europe and North America, the figure stretches to 32 days — nearly a full month — reflecting a willingness to invest in longer, more immersive trips rather than the five-country-in-ten-days bus tours that once dominated the market.

Switzerland, already India's top Schengen destination with over 1.15 million visa applications, is the clearest beneficiary. But the Nordic countries are where the growth is steepest. Norway's fjords, Finland's midnight sun, and Sweden's archipelago coast offer dramatic summer landscapes with none of the overcrowding that plagues Mediterranean hotspots in July.

## What This Means for NRIs

The heatwave-driven shift is not just an India story. NRIs in the United States and the United Kingdom planning European summer side-trips face the same calculus. A family flying from New York to Rome in late July will encounter the same 40-degree heat that is pushing India-based travellers northward.

The practical advantages compound. Scandinavian countries are among the most English-friendly in Europe — far more so than Spain or Italy — which removes a friction point for families travelling with children or elderly parents. Public transport is reliable, cities are walkable, and the infrastructure is designed for tourists who prefer to move independently rather than in guided groups.

For NRIs already flying through European hubs, the logistics work out neatly. SAS reopened its Copenhagen-Mumbai route in June after a 17-year absence, with connections timed for onward travel to New York, Boston, and Toronto. Lufthansa is adding extra summer frequencies from Frankfurt and Munich to Chennai, Delhi, Hyderabad, and Bengaluru. The connective tissue between India, Northern Europe, and North America has never been denser.

## The Flexibility Factor

Another trend emerging alongside the destination shift is a growing emphasis on flexible booking. Indian travellers are increasingly opting for adjustable itineraries rather than locked-in schedules, allowing them to shift travel dates based on weather forecasts or personal convenience.

Travel insurers and platforms have responded with flexible cancellation policies, rescheduling options, and weather-related protections. The result is a drop in outright cancellation rates, even among travellers concerned about conditions at their destination.

The underlying message is clear: Indian travellers are not abandoning Europe. They are recalibrating where in Europe they go. The days of Paris-and-Rome being the default are giving way to a more informed, more weather-conscious generation of travellers who check the forecast before they check the Eiffel Tower ticket price.

For the diaspora, the takeaway is practical. If you are planning a European leg during your India trip — or a standalone summer holiday from the US or UK — the Nordics and the Alps are having their moment. The fjords are 18 degrees, the trains run on time, and nobody is queueing for two hours to get into the Louvre in 39-degree heat."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
