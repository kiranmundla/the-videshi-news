#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-03 06:00 UTC run."""

import json, os, re, uuid, requests
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
        "headline": "Your US Visa Unlocks 16 Countries Visa-Free — The NRI's Summer 2026 Playbook",
        "subheadline": "From 180 days in Mexico to 90 in Colombia, your American visa stamp opens doors across Latin America, the Caribbean, and Southeast Asia. Here's exactly how to use it.",
        "slug": make_slug("us-visa-unlocks-16-countries-visa-free-nri-playbook"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans with valid US visas can skip the visa application process for 16+ countries — turning a weekend trip or a World Cup detour into a passport-stamp-free breeze. Most NRIs don't realize this perk exists.",
        "tags": ["travel", "visa", "NRI", "Mexico", "Caribbean", "Colombia", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Voye Global", "url": "https://voyeglobal.com/countries-indians-can-visit-with-us-visa/"},
            {"name": "Visa2Fly", "url": "https://www.visa2fly.com/blog/visa-free-countries-for-indian-passport-holders-with-us-visa/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/3anp5xofqz6z/"},
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/506810/pexels-photo-506810.jpeg",
        "body": """Most Indian Americans know their US visa gets them into the United States. Far fewer realize it also functions as a skeleton key to more than a dozen other countries — no separate visa application, no consulate appointment, no weeks of waiting.

With the FIFA World Cup kicking off in Mexico, the United States, and Canada on June 11, and summer travel season in full swing, there has never been a better time for NRIs to understand exactly what their visa stamp unlocks.

## The Big List

Here are the countries Indian passport holders can enter visa-free or with drastically simplified entry, provided they carry a valid US visa:

**Mexico** — Up to 180 days. No separate visa, no fee beyond the standard FMM visitor form (often included in your airfare). Mexico is the crown jewel of this list. Cancún, Mexico City, Tulum, Oaxaca — all accessible with just your passport and US visa. With the World Cup hosting matches across Mexico, the timing could not be better.

**Colombia** — Up to 90 days. A valid US visa (excluding C-1 transit) grants visa-free entry. Cartagena's old walled city, Medellín's transformation, and the coffee region are all within reach.

**Panama** — Up to 30 days. Requires a valid multiple-entry US visa that has been used at least once. The Panama Canal, Bocas del Toro, and Panama City's skyline rival any Central American destination.

**Philippines** — 30 days. Your US visa waives the standard visa requirement. Manila, Palawan, and Cebu offer some of the cheapest luxury travel in Southeast Asia.

**Turkey** — 30 days via e-Visa. Not technically visa-free, but if you hold a valid US visa, the Turkish e-Visa takes minutes online (USD 43). Istanbul alone is worth the detour.

**Additional countries** include Costa Rica, Belize, Guatemala, Honduras, El Salvador, Peru, Albania, Georgia, Serbia, Montenegro, Bosnia and Herzegovina, and North Macedonia. Some require a Schengen visa instead of (or in addition to) a US visa, so always verify the specific entry requirement for your visa type.

## The Caribbean Angle

For NRIs in the Northeast or Southeast US, Caribbean destinations are a short flight away. Several islands accept Indian passport holders with valid US visas:

- **Aruba** — Visa-free, up to 30 days
- **Curaçao** — Visa-free with valid US multiple-entry visa
- **Sint Maarten** — Same deal
- **Cayman Islands** — Visa-free transit/entry with US visa
- **Bahamas** — Visa-free with valid US visa

Direct flights from Miami, Fort Lauderdale, New York, and Houston make these weekend-trip realistic, not just aspirational.

## Mexico and the World Cup

Mexico is leading Caribbean and Latin American tourism growth in 2026, according to a Travel And Tour World analysis published this week. Reduced entry barriers, budget-friendly flights from US cities, and a diversified tourism offering — from the beaches of the Yucatán to the street food capital of Oaxaca — are driving record arrivals.

With the World Cup hosting group-stage matches in Mexico City (Estadio Azteca) and Guadalajara, Indian American fans with valid US visas can cross the border without the weeks-long visa process that would otherwise apply. Flights from Los Angeles to Mexico City start under $200 round trip. From Dallas, it is even cheaper.

## Practical Tips for NRIs

**Check your visa type.** Most benefits require a valid, unexpired B1/B2 multiple-entry visa. Some countries require it to have been used at least once.

**Carry printed proof.** Even though entry is visa-free, airline staff at boarding may ask to see your US visa. Keep a printed copy or ensure it is clearly visible on your passport.

**Watch for fine print.** "Visa-free" does not mean "documentation-free." You still need a valid passport (often with six months' remaining validity), proof of return travel, and sometimes proof of accommodation.

**Do not overstay.** Visa-free entry limits vary from 14 to 180 days. Overstaying in one country can jeopardize your US visa status on return.

**Travel insurance is not optional.** Countries like Colombia and Costa Rica may ask for proof of travel insurance at immigration. Even where it is not required, a hospital visit abroad without coverage can be financially devastating.

## Why This Matters

The Indian passport ranks 80th on the 2026 Henley Passport Index, with visa-free or visa-on-arrival access to 55 destinations. That is a fraction of what a US, UK, or EU passport unlocks. But for the roughly 4.4 million Indian Americans holding valid US visas, the effective access list is significantly longer. Understanding and using this perk turns an administrative stamp into a genuine travel advantage — one that most NRIs leave entirely on the table."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "US National Parks Are Heading for a Record Summer — The NRI Family Road Trip Starter Kit",
        "subheadline": "Active travel bookings are up 10 percent for summer 2026, and parks like Yellowstone, Yosemite, and Acadia are filling fast. A practical guide for Indian American families planning their first — or fifth — national park road trip.",
        "slug": make_slug("us-national-parks-record-summer-nri-family-road-trip"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "National park road trips are the quintessential American family vacation — and one that NRI families are increasingly embracing. The combination of low per-person cost, vegetarian-friendly campsite cooking, and jaw-dropping landscapes makes parks the ideal alternative to Disney fatigue.",
        "tags": ["travel", "national parks", "road trip", "NRI", "family", "summer", "USA"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Backroads Summer 2026", "url": "https://www.travelandtourworld.com/news/article/united-states-national-parks-on-track-for-record-breaking-growth-backroads-reports-10-boost-in-active-travel-for-summer-2026/"},
            {"name": "National Park Service", "url": "https://www.nps.gov/"},
            {"name": "Recreation.gov", "url": "https://www.recreation.gov/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/220032/pexels-photo-220032.jpeg",
        "body": """Every summer, millions of American families load up an SUV and drive toward a national park. Increasingly, Indian American families are joining them — and discovering that a week in Yellowstone or Yosemite costs a fraction of a theme park vacation while delivering experiences their kids will remember far longer than another roller coaster.

Backroads, one of the largest active travel operators in the US, reports a 10 percent increase in national park bookings for summer 2026. Crater Lake, Great Smoky Mountains, Joshua Tree, Acadia, Yellowstone, and Yosemite are all trending. If you have not booked yet, the window is narrowing.

## The Six Parks Every NRI Family Should Consider

**Yellowstone (Wyoming/Montana/Idaho)** — The original national park. Geysers, bison herds, and the Grand Prismatic Spring make it otherworldly. Old Faithful erupts roughly every 90 minutes, and the park's network of boardwalks makes it manageable for all ages. Book lodges inside the park at least three months ahead; campsite reservations open in March and sell out fast.

**Yosemite (California)** — Half Dome, El Capitan, and Bridalveil Fall are iconic for a reason. Summer is peak season, and the park now uses a reservation system for day visitors driving in between 5 AM and 4 PM. Reserve at Recreation.gov. For Bay Area NRIs, it is a four-hour drive from the South Bay.

**Great Smoky Mountains (Tennessee/North Carolina)** — The most visited national park in the country, and one of the few with no entrance fee. The Smokies offer easy hikes, wildflower meadows, and black bear sightings. Gatlinburg and Pigeon Forge on the Tennessee side are family-friendly gateway towns with abundant vegetarian dining options.

**Acadia (Maine)** — A coastal park with rocky beaches, forests, and mountain views. Cadillac Mountain is one of the first places in the US to see sunrise from October through March. Summer brings warm days and cool nights — perfect for families escaping the heat of Texas or the South.

**Crater Lake (Oregon)** — The deepest lake in the United States, formed in the caldera of a collapsed volcano. The blue is so vivid it does not look real. The 33-mile Rim Drive is a stunning scenic loop, and boat tours to Wizard Island run from late June through September.

**Joshua Tree (California)** — A desert park where two ecosystems meet. Ideal for stargazing — the park is an International Dark Sky Park. For SoCal NRIs, it is a two-hour drive from Los Angeles. Spring and fall are the best seasons, but early summer mornings are magical before the heat builds.

## The Practical NRI Playbook

**The America the Beautiful Pass** costs $80 and covers entrance fees at all 63 national parks plus hundreds of other federal sites for a full year. If you plan to visit more than one park, the pass pays for itself immediately. Buy it at any park entrance or at Recreation.gov.

**Food planning matters.** Most parks have limited dining inside — a general store and maybe one lodge restaurant. NRI families who cook at their campsite or cabin save money and eat better. A portable gas stove, a cooler, and a Costco run before departure covers most needs. Rice, dal, and sabzi cook just as well on a camp stove as they do on your kitchen range.

**Book campgrounds or lodges early.** Popular sites like Yellowstone's Canyon Village and Yosemite's Curry Village open reservations months in advance and sell out within hours. If you miss the window, check for cancellations weekly — they appear regularly as plans change.

**Layer your clothing.** Mountain parks can swing 30-plus degrees Fahrenheit between morning and afternoon, even in summer. A light down jacket, rain shell, and sun hat are non-negotiable.

**Wildlife distance is law.** Stay at least 100 yards from bears and wolves, and 25 yards from all other wildlife. This is not a suggestion — it is a federal regulation, and rangers enforce it. Use binoculars and zoom lenses rather than approaching.

## The Road Trip Format

The beauty of national parks for NRI families is the road trip itself. A typical two-week itinerary might look like this:

- **Days 1–4:** Fly into Salt Lake City. Drive to Yellowstone (five hours). Spend three days exploring geysers, Lamar Valley, and Grand Canyon of the Yellowstone.
- **Days 5–7:** Drive south to Grand Teton (one hour from Yellowstone's south entrance). Hike to Taggart Lake, float the Snake River.
- **Days 8–10:** Continue to Arches and Canyonlands in Utah (six hours). Delicate Arch at sunset is a bucket-list moment.
- **Days 11–13:** Drive to Zion National Park (five hours). Hike the Narrows or Angels Landing. Fly home from Las Vegas (two and a half hours from Zion).

Total driving: roughly 1,500 miles across four states. Cost for a family of four, including gas, park passes, camping or budget lodges, and groceries: approximately $2,500 to $4,000 — less than a single week at Disney World.

## Why Now

National Park visitation hit 312 million in 2023 and has continued climbing. Infrastructure improvements across the system — new shuttle routes, expanded campgrounds, improved trail surfaces — mean the experience is better than ever. But popularity also means crowding. The NRI families who plan and book now will get the sites, the dates, and the experiences they want. Those who wait until July will be checking cancellation calendars and settling for overflow parking lots.

The parks are not going anywhere. Your kids' summers are."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Typhoon Jangmi Grounds 3,000 Flights Across Asia — NRIs Transiting Through Tokyo Should Rebook Now",
        "subheadline": "Over 3,000 flights were disrupted on June 2 as the storm tore through Okinawa and southern Japan. Tokyo's Narita and Haneda airports sit directly in its path for June 3, threatening onward connections to India.",
        "slug": make_slug("typhoon-jangmi-asia-flights-disrupted-nri-tokyo-transit"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Tokyo Narita and Haneda are critical transit hubs for NRIs flying between the US West Coast and India on carriers like ANA, JAL, and connecting flights. A multi-day disruption at both Tokyo airports could cascade into missed connections and rebooking chaos for Indian Americans mid-journey.",
        "tags": ["travel", "typhoon", "flights", "Japan", "Tokyo", "NRI", "Asia", "airlines"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel Tourister — Asia Flight Chaos June 2", "url": "https://www.traveltourister.com/asia-flight-chaos-june-2-typhoon-jangmi/"},
            {"name": "Japan Meteorological Agency", "url": "https://www.jma.go.jp/"},
            {"name": "Reuters — JetBlue fuel costs", "url": "https://www.reuters.com/business/aerospace-defense/jetblue-flags-higher-fuel-costs-disruptions-iran-conflict-linger-2026-06-01/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png",
        "body": """Typhoon Jangmi, the sixth named storm of the 2026 Western Pacific season, ground more than 3,000 flights to a halt across Asia on Tuesday, June 2 — and the worst is not over. The storm is now tracking northeast toward Tokyo, placing the Japanese capital's two major international airports, Narita and Haneda, directly in its projected path for Wednesday, June 3.

For Indian Americans transiting through Tokyo on their way to or from India, this is an active disruption that demands immediate attention.

## What Happened on June 2

As of Tuesday morning, Asia recorded 3,034 flight disruptions: 586 outright cancellations and 2,448 delays. Japan bore the brunt, with Okinawa's Naha Airport effectively shut down and services from Kagoshima, Amami, and southern Kyushu suspended or severely delayed.

Japan Airlines, Japan Air Commuter, and Japan Transocean Air alone cancelled 173 flights. HK Express cancelled all Hong Kong–Okinawa services for both June 1 and June 2. ANA and EVA Air were also affected.

A separate severe weather event in China added another 166 cancellations and 2,183 delays on June 1, compounding the regional disruption.

## Why Tokyo Matters for NRIs

Tokyo Narita (NRT) and Haneda (HND) are two of Asia's most critical connecting airports for passengers flying between North America and India. ANA operates nonstop services from San Francisco, Los Angeles, Houston, and New York to Tokyo, with onward connections to Delhi and Mumbai. JAL offers similar routing. Singapore Airlines, Cathay Pacific, and other carriers also route through the broader Asia-Pacific corridor that is now under typhoon threat.

The Japan Meteorological Agency has issued warnings for Kanto-Koshin — the region containing Tokyo — through Wednesday. Storm conditions include sustained winds of 30 meters per second (67 mph) with gusts up to 40 meters per second (89 mph) and a central pressure of 975 hPa. That is strong enough to force runway closures, ground departures, and strand thousands of transit passengers.

If you are an NRI currently booked on a US-to-India itinerary routing through Tokyo on June 3 or 4, your connection is at risk.

## What to Do Right Now

**Check your airline's app or website.** ANA, JAL, and most major carriers have already begun issuing fee-free rebooking waivers for flights transiting through affected Japanese airports. Look for travel advisories on your carrier's homepage — they typically allow one free date change or rerouting.

**Consider alternate routing.** If your airline offers connections through Singapore, Hong Kong, or Seoul (Incheon), those hubs are currently operational. Cathay Pacific via Hong Kong and Singapore Airlines via Changi are alternatives worth checking — both airports are outside the storm's path as of Tuesday evening.

**Do not wait for a cancellation notification.** Airlines typically send cancellation alerts 6 to 12 hours before departure. By that point, alternate seats on other routings may already be gone. Proactive rebooking — calling the airline or using the app — gives you the best chance at a smooth reroute.

**If you are already in transit at a Japanese airport,** locate the airline's service counter or lounge immediately. Japan's airport staff are well-practiced at typhoon disruptions and will provide hotel vouchers, meal credits, and rebooking priority for stranded passengers. Airport Wi-Fi is free and reliable at both Narita and Haneda.

**Travel insurance claims.** If you purchased travel insurance, document everything: screenshots of flight status changes, boarding pass scans, receipts for any meals or accommodation. Most policies cover weather-related delays and cancellations, but claims require documentation submitted within 30 days.

## The Bigger Picture

This is the second major Asian aviation disruption of 2026, following a comparable event on May 13 that produced 3,390 total disruptions. The Western Pacific typhoon season runs from May through November, with peak activity in August and September. NRIs planning summer travel through Asian hubs should build at least one buffer day into their itineraries — a 90-minute connection through Narita during typhoon season is a gamble, not a plan.

The broader context makes it worse. The Iran conflict has already pushed US-India airfares to their highest levels in a decade, with carriers rerouting around Middle Eastern airspace. IndiGo just suspended its Manchester Dreamliner services due to similar airspace constraints and cost pressures. Disruptions in the Pacific corridor pile on top of disruptions in the western route, leaving NRIs with fewer alternatives and higher rebooking costs.

## What Comes Next

The Japan Meteorological Agency projects Jangmi to weaken as it crosses Honshu and moves out over the Pacific by Thursday, June 4. If that forecast holds, Tokyo operations should begin normalizing by Thursday afternoon local time. But typhoon recovery at major airports typically takes 24 to 48 hours to clear the backlog of delayed flights and stranded passengers.

The practical advice is blunt: if you can avoid transiting Tokyo between now and Friday, do so. If you cannot, build in contingency time and rebook proactively. The NRIs who act today will fly this week. The ones who wait for push notifications may not."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
