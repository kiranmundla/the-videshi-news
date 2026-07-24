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
        "headline": "Five Indian Airports Just Made the World's Top 100 — Here's What NRIs Will Actually Notice",
        "subheadline": "Skytrax's 2026 rankings put Delhi at 28th globally, with Bengaluru, Hyderabad, Goa, and Mumbai also on the list. The real story isn't the numbers — it's whether the experience matches them.",
        "slug": make_slug("skytrax-2026-five-indian-airports-top-100-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs landing in India 2-3 times a year are the most frequent stress-testers of these airports. Skytrax rankings reflect improvements in lounges, immigration speed, signage, and terminal design that directly affect the diaspora landing experience — from the 5-second DigiYatra entry to the new T3 restaurants at Delhi.",
        "tags": ["travel", "airports", "skytrax", "india", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Skytrax World Airport Awards 2026", "url": "https://www.worldairportawards.com/worlds-top-100-airports-2026/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/travel-news/worlds-best-airports-2026/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/world/worlds-top-10-airports-2026-full-list-delhi-igi-mumbai-csmia-skytrax-awards-asian-airports-changi-incheon-haneda-11743243027022.html"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4318372/pexels-photo-4318372.jpeg",
        "body": """India placed five airports in Skytrax's World's Top 100 for 2026 — the most it has ever managed in a single year. Delhi leads at 28th, up from 32nd in 2025. Bengaluru jumped seven spots to 41st. Hyderabad climbed thirteen places to 43rd. Goa's Manohar International arrived at 64th, and Mumbai sits at 66th.

The rankings, based on a global passenger survey covering 550 airports, also handed India three regional trophies. Delhi won Best Airport in India and South Asia. Hyderabad took Best Airport Staff Service. Bengaluru earned Best Regional Airport in the subregion for the third consecutive year.

For Changi obsessives: Singapore held its top slot for the 14th time since 2000. Asia swept the top five, with Seoul Incheon, Tokyo Haneda, Hong Kong, and Narita filling out the rest. Paris CDG was the highest-ranked non-Asian airport at sixth.

## What's Actually Changed on the Ground

The numbers tell a story that any NRI who flew home in 2024 versus 2026 can confirm with their own feet. Delhi's Terminal 3 has undergone a quiet revolution: expanded retail, vastly improved food courts that no longer rely exclusively on overpriced sandwiches, and immigration processing that now averages under 90 seconds for Indian passport holders using e-gates. The DigiYatra facial recognition system — which hit 100 million journeys this month — has cut domestic boarding entry time from 15 seconds to 5.

Bengaluru's Kempegowda airport has benefited from its Terminal 2, which opened in late 2024 and brought the kind of spacious, well-lit design that Changi made famous. The terminal's Namaste lounge and expanded duty-free section have made the layover experience substantially less grim. Hyderabad's rise is partly attributable to consistently high staff courtesy scores — the kind of thing that matters enormously at 2 AM when your connection is delayed and the help desk is your only friend.

Goa's Manohar International, which replaced the cramped Dabolim Airport as the state's primary hub, debuted on the list this year. Its modern design and spacious layout are a genuine upgrade for the lakhs of NRIs who fly into Goa for weddings, holidays, and family reunions every winter.

Mumbai at 66th is the most sobering data point. Chhatrapati Shivaji Maharaj International remains one of the busiest single-runway commercial airports on Earth — 219 flights per runway per day, the highest density globally according to AeroCorner. The terminal experience, while improved, simply cannot keep up with the passenger volumes it handles. Navi Mumbai International, which opened in December 2025, is designed to relieve that pressure, but full ramp-up will take years.

## The NRI Perspective

For the 4.7 million Indian Americans who fly to India at least once a year, these rankings translate into real quality-of-life changes. The immigration hall at Delhi is no longer the purgatorial queue it was a decade ago. Bengaluru's arrivals area now has functioning taxi apps and metro connectivity. Hyderabad's staff will actually help you find your connecting gate.

But the improvements are uneven. Wi-Fi remains unreliable at most Indian airports. Signage in regional languages is still inconsistent. And while the premium lounge experience has improved dramatically — especially at Delhi and Bengaluru — the economy-class departure experience at Mumbai during peak hours remains genuinely stressful.

The broader trajectory matters more than any single ranking. In 2019, India had two airports in the top 100. In 2025, it had four. Now it has five, and all moved upward. Delhi's 28th-place finish puts it ahead of LaGuardia (38th), Houston Hobby (39th), Dallas/Fort Worth (48th), and Los Angeles (49th) — airports that NRIs know intimately from the other end of their journeys.

## What Comes Next

India's civil aviation ministry projects annual passenger traffic hitting 500 million by 2030 and nearly a billion by 2040. If the airports already in operation can maintain their trajectory — and Navi Mumbai plus Noida International (opening June 15) deliver on their design ambitions — India could plausibly have six or seven airports in the top 100 by 2028.

For NRIs, the practical takeaway is straightforward: the landing experience in India is getting measurably better, year by year. Whether it's getting good enough, fast enough, is a debate best held at the arrivals pickup area — which, at most Indian airports, still needs work."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The NRI Family's Summer National Parks Playbook — Five Parks, Zero Excuses",
        "subheadline": "Yellowstone's geysers, Glacier's alpine lakes, Yosemite's granite cathedrals. America's best scenery costs less than a weekend at Great Wolf Lodge, and the kids will actually remember it.",
        "slug": make_slug("nri-family-summer-national-parks-guide-2026"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian American families often default to India trips or Disney vacations. National parks offer a radically different — and far cheaper — summer option that most NRI families underutilize. Vegetarian-friendly camping, kid-appropriate trails, and genuine wilderness within driving distance of most major Indian American metros.",
        "tags": ["travel", "national-parks", "road-trip", "family", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Frommers - Best National Parks for Summer", "url": "https://www.frommers.com/slideshows/848380/the-best-u-s-national-parks-to-visit-in-summer"},
            {"name": "GetYourGuide - US National Parks Summer", "url": "https://www.getyourguide.com/magazine/best-us-national-parks-summer/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/united-states-to-unlock-budget-family-magic/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17187982/pexels-photo-17187982.jpeg",
        "body": """June through August is when Indian American families face the annual question: India trip, beach resort, or Disney? There is a fourth option that costs a fraction of any of those, and your children will talk about it long after they've forgotten which waterslide was at which hotel.

America's national parks are the most underutilized family resource in the NRI playbook. Entry fees are $35 per vehicle. Campsite fees run $20-35 per night. Ranger-led programs — geology talks, stargazing sessions, wildlife walks — are free. And the scenery makes every Instagram filter redundant.

Here are five parks worth building your summer around.

## Yellowstone — The One Everyone Should Do First

Wyoming's crown jewel is the gateway drug to national parks. Old Faithful erupts every 90 minutes with Swiss-watch reliability, giving even toddler-burdened families a guaranteed spectacle. The Grand Prismatic Spring is the most photographed natural feature in America for a reason — its colours genuinely look AI-generated.

**The NRI edge:** Yellowstone's general stores carry decent vegetarian options, and the park's cafeterias serve pasta, salads, and grilled cheese alongside the standard burgers. Book the Mammoth Hot Springs Hotel or Canyon Lodge by April — summer rooms vanish fast. Driving from Salt Lake City (5 hours) is the most common approach from the West Coast.

**Don't miss:** Lamar Valley at dawn for bison herds. Bring binoculars.

## Glacier National Park — The One That Won't Last

Montana's Glacier is best visited in July and August when the Going-to-the-Sun Road is fully open and the high-elevation snow has mostly cleared. The park's namesake glaciers are retreating — scientists estimate most will be gone by 2030 — making this a genuinely now-or-never destination.

**The NRI edge:** The Many Glacier area has shorter, family-friendly trails with alpine lake payoffs that rival anything in the Swiss Alps. Grinnell Glacier Trail is the signature hike — strenuous but doable for fit teenagers. Vehicle reservations are required for Going-to-the-Sun Road; book at recreation.gov the moment the window opens (usually early March).

**Don't miss:** Hidden Lake Overlook from Logan Pass. One-and-a-half miles, moderate, and the views will wreck every other hike for you.

## Yosemite — The One You Have to Plan

Yosemite Valley is breathtaking and brutally crowded in summer. The solution: split your time. Spend one day in the valley for El Capitan, Half Dome views, and Bridalveil Fall. Then drive up Tioga Road to Tuolumne Meadows, where the crowds evaporate and the wildflowers take over.

**The NRI edge:** The park is a 4-hour drive from the Bay Area, making it the most accessible marquee park for the largest NRI concentration in America. Book Curry Village or Housekeeping Camp for the valley; for Tuolumne, the campground is first-come-first-served and fills by noon on weekends.

**Don't miss:** Mirror Lake Loop — flat, easy, stunning, perfect for young kids.

## Great Smoky Mountains — The Free One

The most visited national park in America charges zero entrance fee. Straddling Tennessee and North Carolina, the Smokies offer firefly displays in June (Elkmont synchronous fireflies are genuinely magical), waterfalls accessible by short trails, and cabin rentals in Gatlinburg and Pigeon Forge that are cheaper than most highway motels.

**The NRI edge:** Closest major park for the East Coast desi corridor (4 hours from Atlanta, 6 from the DC-Virginia belt). Indian restaurants in Pigeon Forge are nonexistent, but Gatlinburg has enough variety to keep vegetarians alive. Pack a cooler with home-cooked parathas and achaar — trail snacks from home taste better than any granola bar.

**Don't miss:** Clingmans Dome at sunset. Highest point in Tennessee, 360-degree views.

## Grand Canyon — The One That Changes Perspective

No photo prepares you. The South Rim is the accessible side, open year-round, with paved rim trails suitable for strollers and wheelchairs. Summer temperatures on the rim hover around 80°F — hot but manageable. Do not hike to the bottom and back in a single day unless you are seriously fit and carrying serious water.

**The NRI edge:** A 4.5-hour drive from Las Vegas, making it a natural addition to any Vegas trip. Phantom Ranch — the only lodge at the bottom — requires a lottery reservation 15 months in advance. El Tovar Lodge on the rim is the classic stay.

**Don't miss:** Desert View Watchtower on the East Rim Drive. Sunrise from Mather Point.

## Practical Tips

**America the Beautiful Pass** ($80/year) covers entrance to all 63 national parks and 2,000+ federal recreation sites. One pass per vehicle, unlimited visits. It pays for itself in two parks.

**Camping with kids:** REI rents family tents, sleeping bags, and camp stoves. You do not need to own gear to camp.

**Food:** Most park lodges serve vegetarian pasta, salads, and breakfast items. Pack dal-chawal in a thermos for trail lunches — it travels better than sandwiches and tastes better too.

**Timing:** Weekdays are dramatically less crowded than weekends. If you can pull kids out of camp for a Tuesday-Thursday window, do it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Seven Caribbean Islands Where Your Indian Passport Gets You In Without a Visa",
        "subheadline": "Barbados, Jamaica, Dominica, Trinidad — the beach vacation you didn't know you could take without a single embassy visit. Some offer stays of up to 180 days.",
        "slug": make_slug("caribbean-islands-visa-free-indian-passport-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs assume Caribbean vacations require visa hassle. In fact, seven Caribbean nations offer visa-free entry to Indian passport holders — no consulate visits, no visa fees, no waiting. For NRIs in the US on H-1B, green cards, or US citizenship, these islands are weekend-trip accessible from the East Coast.",
        "tags": ["travel", "visa-free", "caribbean", "indian-passport", "beach"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Henley Passport Index 2026 - India", "url": "https://www.henleyglobal.com/passport/india"},
            {"name": "Wikipedia - Visa Requirements for Indian Citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Platinumlist Guide", "url": "https://platinumlist.net/guide/india-henley-passport-index-2026-list-visa-free-countries"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/10490903/pexels-photo-10490903.jpeg",
        "body": """Ask most Indian Americans about Caribbean vacations and the response is predictable: "Don't you need a visa?" The answer, for seven island nations, is no. Indian passport holders can walk off the plane in Barbados, Jamaica, Dominica, Grenada, Trinidad and Tobago, Haiti, and St. Vincent and the Grenadines without a visa, a consulate appointment, or a single form submitted in advance.

This is not new — most of these arrangements have been in place for years. But awareness among NRIs remains remarkably low, and the result is that Indian Americans are systematically overlooking some of the most accessible, affordable, and beautiful beach destinations within a few hours' flight of the East Coast.

## The Seven Islands

**Barbados — 90 days, visa-free**
The most polished of the group. Barbados has direct flights from Miami and JFK, a well-developed tourist infrastructure, and some of the best beaches in the Western Hemisphere. The south coast (Oistins, St. Lawrence Gap) is affordable and lively; the west coast (Holetown) is quieter and more upscale. Cricket fans: the Kensington Oval is here, and the island's cricketing culture runs deep — a natural conversation starter for any desi traveller.

**Jamaica — 90 days, visa-free**
Montego Bay and Ocho Rios are the resort hubs; Negril has the best beach (Seven Mile Beach lives up to its reputation). Kingston is rougher but culturally rich — the Bob Marley Museum alone justifies a day trip. All-inclusive resorts from Sandals and Hyatt make budgeting predictable. Direct flights from New York, Miami, Atlanta, and Fort Lauderdale. A 3-hour flight from JFK.

**Dominica — 180 days, visa-free**
Not to be confused with the Dominican Republic (which requires a visa). Dominica is the "Nature Island" — volcanic hot springs, rainforest hikes, snorkelling in Champagne Reef where underwater volcanic vents create a natural jacuzzi. It is emphatically not a beach resort island; it is an adventure destination. The 180-day visa-free stay is the longest any Caribbean nation offers Indian passport holders.

**Trinidad and Tobago — 90 days, visa-free**
Trinidad has the largest Indian diaspora in the Caribbean — roughly 35% of the population traces ancestry to indentured labourers who arrived from Bihar and eastern UP in the 19th century. The cultural overlap is startling: roti shops on every corner, Divali Nagar celebrations that rival parts of India, Hindu temples alongside mosques and churches. Tobago, the smaller island, has the beaches. Carnival (February/March) is the main event — plan a year ahead.

**Grenada — 90 days, visa-free**
The "Spice Island" produces nutmeg, cinnamon, and cocoa. Grand Anse Beach is regularly ranked among the world's best. Grenada is small, quiet, and spectacularly green. St. George's, the capital, has a picturesque harbour ringed by colourful colonial buildings. It is an excellent choice for families who want to slow down.

**St. Vincent and the Grenadines — visa-free**
An archipelago of 32 islands. The Grenadines (Bequia, Mustique, Canouan) are where the sailing and luxury crowd goes. St. Vincent itself is volcanic and lush. The Tobago Cays Marine Park — a cluster of uninhabited islands with crystal water — is a day trip that belongs in a David Attenborough documentary.

**Haiti — 3 months, visa-free**
The most complex destination on this list. Haiti's tourism infrastructure is minimal, safety requires careful planning, and independent travel is not recommended without local guidance. The Citadelle Laferrière, a mountaintop fortress and UNESCO World Heritage Site, is extraordinary. For experienced travellers willing to do the research, Haiti offers something no other Caribbean island can: a raw, unvarnished encounter with a singular culture.

## Practical Notes for NRIs

**Flights:** Most Caribbean islands are 3-5 hours from the US East Coast. JetBlue, American, Delta, and Caribbean Airlines cover the major routes. Prices from JFK to Barbados or Montego Bay in summer run $350-500 round-trip.

**Trinidad for the culturally curious:** If you have never experienced the Indian diaspora outside of the US, UK, and India, Trinidad will rewrite your understanding. Doubles (a street food of curried chickpeas in fried bread) is the national snack. Chutney-soca music is a genre. The Hanuman murti in Carapichaima is the largest outside India. Plan around Divali (October/November) or Phagwa (March) for the full experience.

**Entry requirements:** Visa-free does not mean document-free. Carry your passport (valid for at least 6 months), return ticket, and proof of accommodation. Immigration officers may ask for evidence of funds — a credit card and a hotel booking typically suffice.

**US visa holders get more options:** If you hold a valid US visa (H-1B, B1/B2, green card), several additional Caribbean and Central American countries open up — including Mexico (180 days), Costa Rica, Honduras, Guatemala, and Panama. Your US visa or green card effectively functions as a travel pass across much of the Western Hemisphere.

**Health:** Check CDC travel advisories for each island. Mosquito-borne diseases (dengue, Zika) are present in some Caribbean nations, particularly during rainy season (June-November). Pack DEET-based repellent.

The Caribbean is closer, cheaper, and easier to visit than most NRIs assume. Seven islands, no visa, and a flight shorter than San Francisco to Honolulu. The only remaining excuse is inertia."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
