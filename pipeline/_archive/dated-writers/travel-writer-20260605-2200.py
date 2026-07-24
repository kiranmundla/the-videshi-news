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
        "headline": "Air India Express Opens Bengaluru–Phuket Nonstop — and South India's Tech Workers Get a Beach Escape Under Four Hours",
        "subheadline": "Four weekly flights on a Boeing 737 MAX 8 connect India's IT capital to Thailand's most popular island, giving Bengaluru's diaspora-linked professionals a weekend getaway that doesn't require a connection in Bangkok.",
        "slug": make_slug("air-india-express-bengaluru-phuket-nonstop-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru is home to hundreds of thousands of IT workers with NRI ties — many of whom travel frequently between India and the US. A direct Phuket link means families visiting from America can tack on a Thai beach weekend without backtracking through Bangkok or Chennai.",
        "tags": ["travel", "airlines", "air-india-express", "phuket", "bengaluru", "thailand", "southeast-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/air-india-express-bengaluru-phuket-direct-flights/"},
            {"name": "TTR Weekly", "url": "https://www.ttrweekly.com/site/2026/06/air-india-express-links-bengaluru-and-phuket/"},
            {"name": "Travel Trade Journal", "url": "https://www.traveltradejournal.com/air-india-express-launches-direct-flights-between-bengaluru-and-phuket/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Banana_beach_Phuket_2017_-_02.jpg/1280px-Banana_beach_Phuket_2017_-_02.jpg",
        "image_caption": "Banana Beach on Phuket's western coast, now a direct flight from Bengaluru",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The first Air India Express flight from Bengaluru to Phuket touched down on June 1, opening a route that had been conspicuously absent from South India's international network. The service operates four times a week — Monday, Friday, Saturday, and Sunday — on a Boeing 737 MAX 8 with 176 seats. Flight time is three hours and 45 minutes, roughly the same as Bengaluru to Goa by train.

## The Schedule

Departure times vary by day. Monday and Saturday flights leave Kempegowda International Airport at 10:35 AM and land in Phuket at 3:50 PM local time. The return departs Phuket at 4:45 PM and reaches Bengaluru by 6:55 PM. Friday services leave a bit later — 11:25 AM outbound, 5:40 PM return from Phuket. Sunday timings split the difference, departing Bengaluru at 11:15 AM.

The schedule is designed for long-weekend getaways. A Friday-to-Monday window gives travelers three nights in Phuket without burning a single weekday of leave — a calculation that Air India Express clearly made with Bengaluru's IT workforce in mind.

## Why Phuket, Why Now

Thailand already receives more Indian tourists than any other Southeast Asian country, and the numbers have climbed sharply since Bangkok introduced visa-free entry for Indian nationals. But most of that traffic has funnelled through Bangkok, with Phuket requiring a domestic connection or a flight from Delhi or Mumbai.

Air India Express launched Bengaluru–Bangkok last October. The Phuket addition is a natural extension, targeting the leisure segment that Bangkok's city-break appeal doesn't fully capture. Phuket offers beaches, diving, and island-hopping — the kind of trip that Bengaluru's young professionals and dual-income families book for a quick reset.

From Bengaluru, the airline now operates nearly 500 weekly flights covering 31 domestic and eight international destinations. The carrier recently won "Airline of the Year" in both domestic and international categories at Bengaluru Airport's Pinnacle Awards, a recognition of its aggressive network expansion from the city.

## The NRI Angle

For Indian Americans with family in Bengaluru — and there are a lot of them, given the city's status as India's tech capital — this route changes the math on India visits. Instead of spending two full weeks in Bengaluru visiting relatives, families can now carve out a four-day Phuket detour without the hassle of repositioning to Mumbai or Delhi for an international connection.

The pricing is competitive. Air India Express positions itself below full-service carriers, and introductory fares on the route are expected to undercut the typical Bengaluru–Bangkok–Phuket itinerary by eliminating the domestic Thai leg. For NRI families visiting India with children during summer or winter breaks, it adds a beach option that doesn't require a visa (Thailand offers visa-free stays of up to 60 days for Indian passport holders) or a long-haul detour.

## What to Know Before Booking

Air India Express is a low-cost carrier with a full-service veneer. Hot meals — branded as "Gourmair" — are included on international flights, a differentiator from competitors like IndiGo. The 737 MAX 8 is a single-aisle aircraft, so don't expect lie-flat seats, but the sub-four-hour flight time makes that irrelevant.

Phuket International Airport is on the island's north end, about 45 minutes from the popular Patong Beach area. Grab and local taxis are the standard transfer options. NRIs holding US passports don't need a Thai visa for stays under 60 days. Indian passport holders also enjoy visa-free entry for up to 60 days.

The route's four-day-a-week frequency means it won't suit every schedule, but it fills a genuine gap. For years, Bengaluru's international network has been heavy on Gulf destinations and light on Southeast Asian leisure routes. Air India Express is betting that the city's travelers — and the diaspora families who visit them — want the opposite."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Kills the 14-Day Grace Period for Long-Stay Visitors — and NRIs' Foreign-Born Spouses Will Feel It First",
        "subheadline": "New immigration rules require foreign nationals to register before their 180-day stay expires, not after. Visa extensions are now restricted to emergencies only.",
        "slug": make_slug("india-180-day-stay-rules-tightened-nri-spouses"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Millions of NRIs have foreign-born spouses, parents-in-law, or children with non-Indian passports who visit India for extended stays. The eliminated grace period and emergency-only extensions mean these families must now plan registrations proactively rather than treating the 180-day limit as a soft deadline.",
        "tags": ["travel", "visa", "immigration", "india", "oci", "nri", "mha"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/news/government-notifies-changes-in-immigration-rules-for-foreigners-travelling-to-india"},
            {"name": "PTI via Nagaland Post", "url": "https://www.nagalandpost.com/index.php/government-notifies-changes-in-immigration-and-foreigners-rules-2025/"},
            {"name": "Travelobiz", "url": "https://www.travelobiz.com/india-tightens-180-day-stay-rules-for-foreign-visitors-makes-visa-extensions-harder/"},
            {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national/india-foreign-national-registration-rules-revised-immigration-changes-2026/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922085/pexels-photo-4922085.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passports and boarding documents at an airport immigration counter",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """India's Ministry of Home Affairs quietly amended the country's immigration rules on June 1, 2026, tightening the framework that governs how long foreign nationals can stay in the country and what happens when they overstay. The changes are technical in nature but carry real consequences for a specific group: NRIs whose non-Indian family members visit India for extended periods.

## What Changed

Under the previous Immigration and Foreigners Rules, foreign nationals holding visas that permitted stays of 180 days or longer were required to register with authorities within 14 days *after* completing their 180th day in India. That two-week buffer effectively gave visitors a grace period — time to sort out paperwork, book an extension appointment, or simply wrap up their stay.

That buffer is gone. The amended rules, formally titled the Immigration and Foreigners (Amendment) Rules, 2026, now require registration to be completed "any time before the expiry of the said period of 180 days." The shift from "14 days after" to "before the deadline" is not cosmetic. It moves the compliance burden forward, requiring visitors to plan proactively rather than reactively.

The same logic applies to holders of longer-validity visas that cap each individual stay at 180 days. These visitors — common among OCI cardholders' foreign-born family members — must now register before reaching 180 days of continuous stay or before crossing the cumulative stay limit in a calendar year.

## Extensions Are Now Emergency-Only

The second major change concerns visa extensions. Previously, extending a stay beyond 180 days was an administrative process — not always smooth, but generally achievable with the right paperwork and a visit to the Foreigners Regional Registration Office. The amended framework narrows this considerably. Extensions will now be granted "only in emergent circumstances," a phrase the government has not defined in detail but which clearly signals that routine extensions are no longer on the table.

For foreign nationals who previously treated India's registration system as flexible — and many did — this is a material shift. India is moving toward the kind of compliance-first immigration regime that countries like the US, UK, and Australia have operated for years.

## The NRI Impact

The people most directly affected are not tourists on two-week holidays. They are the foreign-born spouses, parents, and children of Indian-origin families who spend months in India at a time — caring for aging relatives, attending weddings that stretch across weeks, or simply spending an extended summer with family.

Consider the typical scenario: An American-born spouse of an NRI visits India on a tourist or OCI-linked visa, planning a three-month stay that gradually extends to five months as family obligations pile up. Under the old rules, they could register after the 180-day mark and negotiate an extension. Under the new rules, they must register before day 180 and should not count on getting an extension at all unless there is a genuine emergency — a medical crisis, a natural disaster, or a comparable situation.

For NRI families, this means calendar discipline. If your spouse holds a US passport and plans to stay in India for more than a few months, the registration clock starts the day they arrive, and the paperwork needs to happen well before the six-month mark.

## A Small Relief for Mixed-Citizenship Families

One positive change buried in the amendment concerns children born in India to foreign nationals. Previously, parents were required to notify immigration authorities within 30 days of the child's birth to access visa services, including exit permits. The new rules exempt families where one parent is an Indian citizen and wishes the child to retain Indian citizenship. This removes a layer of bureaucratic anxiety for mixed-citizenship couples who have children during an India visit.

## What NRIs Should Do Now

First, know the rules. If a non-Indian family member is planning a stay in India that could approach 180 days, build the FRRO registration into the trip plan from the start — not as an afterthought.

Second, don't assume extensions. The "emergent circumstances" language is deliberately narrow. Plan return tickets within the 180-day window unless you have a documented reason to stay longer.

Third, use the new online appeal system. For the first time, India has introduced an online mechanism to appeal immigration orders. Appeals must be filed with the Commissioner of the Bureau of Immigration within 30 days, and decisions are expected within 60 days. It is a small but meaningful improvement in procedural fairness.

The broader signal is clear: India wants tighter control over who stays long-term and how. For the millions of NRIs whose family lives straddle two countries, the days of treating India's immigration system as forgiving are over."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "El Niño Is Set to Deliver India's Weakest Monsoon in 11 Years — and NRIs Heading Home This Summer Should Pack for Heat, Not Rain",
        "subheadline": "The IMD forecasts just 90% of average rainfall this monsoon season, with an 84% probability of below-normal precipitation. Heatwaves, water shortages, and rising food prices will define the summer travel experience.",
        "slug": make_slug("el-nino-india-weakest-monsoon-11-years-nri-summer-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Summer is the peak season for NRI visits to India. Families planning trips home between June and September should expect persistent heat even during what's supposed to be the rainy season, along with water rationing in some cities, higher food prices, and potential flight disruptions from extreme weather events.",
        "tags": ["travel", "monsoon", "el-nino", "india", "weather", "heatwave", "nri", "summer-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-monsoon-reaches-kerala-three-days-later-than-usual-2026-06-04/"},
            {"name": "ET Edge Insights", "url": "https://etedge-insights.com/industry/agriculture/el-nino-impact-on-indian-agriculture/"},
            {"name": "World Meteorological Organization", "url": "https://wmo.int/"},
            {"name": "Reuters - El Nino crops", "url": "https://www.reuters.com/world/asia-pacific/hot-weather-hurts-asian-crops-powerful-el-nino-takes-shape-2026-06-05/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12932180/pexels-photo-12932180.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Parched, cracked earth during a dry spell — a scene that may become more common across India this monsoon season",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The monsoon reached Kerala on June 4, three days later than the traditional June 1 onset. In most years, that would be a footnote. This year, it is the opening act of what the India Meteorological Department says will be the country's weakest monsoon season in over a decade.

## The Forecast

IMD's updated long-range outlook projects total monsoon rainfall at just 90% of the Long Period Average, with a model error margin of plus or minus 4%. The LPA for the June-September season, calculated from 1971-2020 data, is 87 centimeters. In plain terms, India is expected to receive roughly 10% less rain than normal — and possibly much less in specific regions.

The probability breakdown is stark. IMD assigns a 60% chance of deficient rainfall and a 24% chance of below-normal rainfall. Combined, that is an 84% probability that the 2026 monsoon will underperform. Northwest India, Central India, and the South Peninsula face the highest risk of shortfalls. The Monsoon Core Zone — the agricultural heartland that feeds much of the country — is "most likely" to see below-normal precipitation.

The culprit is El Niño. The World Meteorological Organization says there is an 80% chance that an El Niño event develops between June and August, and a 90% chance it persists through November. Early indicators suggest this could be one of the strongest El Niños on record, with sea surface temperatures in the eastern Pacific already trending well above the threshold.

## What This Means on the Ground

El Niño's effect on India is straightforward: less rain, more heat. The grueling heatwave that preceded the monsoon's late arrival pushed power demand to record highs across northern India. Normally, the monsoon's advance brings rapid cooling — temperatures in Delhi can drop 10 degrees Celsius within a week of the first sustained rains. This year, meteorologists expect the relief to be patchy and inconsistent.

For NRIs visiting India between June and September — and millions do, since summer aligns with school breaks in the US — the practical implications are significant.

**Heat will persist.** North Indian cities like Delhi, Jaipur, Lucknow, and Varanasi, which normally cool down by late June, may stay hot well into July. Temperatures above 40°C (104°F) could be common in the Indo-Gangetic Plain through the early monsoon period. Pack accordingly — lightweight clothing, electrolyte supplements, and realistic expectations about outdoor activities with elderly relatives.

**Water may be rationed.** Several Indian cities already face seasonal water stress. A deficit monsoon will worsen the picture. Bengaluru, Chennai, and parts of Maharashtra have experienced water restrictions in recent years during weak monsoon seasons. NRIs staying with family should not be surprised by reduced municipal supply or reliance on tanker water.

**Food prices are climbing.** Wheat prices globally have risen about 20% since the start of 2026, driven partly by drought concerns in key growing regions. Rice prices at Southeast Asian export hubs have surged roughly 15% in the past month. Within India, the combination of El Niño-driven crop stress and diesel shortages from the Iran war is pushing food inflation higher. Restaurant meals and catered family events will cost more than last summer.

**Flights could get bumpy.** Extreme heat disrupts flight operations — hot air reduces aircraft lift, forcing weight restrictions and occasional cancellations, particularly at airports with shorter runways. Thunderstorms, when they do arrive, tend to be more intense during El Niño years, leading to sudden delays. Delhi, Mumbai, and Hyderabad airports are most exposed.

## The Regional Picture

Not every part of India will be equally affected. IMD's regional forecast suggests that Northeast India — Assam, Meghalaya, Arunachal Pradesh — is most likely to see normal rainfall. The Western Ghats will still receive monsoon precipitation, keeping Kerala and coastal Karnataka relatively green. But the heartland — Uttar Pradesh, Madhya Pradesh, Rajasthan, Maharashtra's interior — faces the steepest deficit risk.

For NRIs planning hill station retreats, the monsoon's weakness creates a paradox. Places like Shimla, Mussoorie, and Ooty typically become misty, rain-soaked retreats in July. This year, they may be pleasantly dry — but also more crowded, as domestic tourists who would normally avoid the monsoon head for the hills to escape heat that the rains aren't breaking.

## How to Plan Around It

NRIs booking India trips for the summer should build flexibility into their plans. Consider travel insurance that covers weather-related disruptions. Book refundable or changeable airline tickets where possible — the combination of monsoon uncertainty and Iran war-driven fuel volatility means schedule changes are more likely than usual.

If visiting North India, front-load outdoor activities to early morning hours and plan indoor alternatives for afternoons. Check municipal water advisories for your destination city before packing — a portable water purifier is worth the suitcase space.

And recalibrate expectations. The romantic monsoon that NRIs remember from childhood — sheets of rain transforming dusty streets into rushing streams, the smell of wet earth, evening chai on the balcony watching clouds roll in — may arrive late, arrive light, or arrive in bursts that flood rather than soothe. El Niño does not cancel the monsoon, but it makes it unreliable. Plan for the weather India is getting, not the weather it usually gets."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
