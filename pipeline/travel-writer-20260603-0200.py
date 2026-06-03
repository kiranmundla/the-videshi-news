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
        "headline": "Germany Drops Transit Visa for Indians — Two of Europe's Biggest Hubs Are Now Open",
        "subheadline": "Effective June 3, Indian passport holders no longer need a transit visa at German airports. France made the same move in April. For NRIs connecting through Frankfurt and Paris, the era of paying €80 to sit in a terminal lounge is over.",
        "slug": make_slug("germany-drops-transit-visa-indian-passport-europe"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans flying to destinations across Europe, Africa, and the Middle East routinely connect through Frankfurt and Paris — two of the world's busiest transit hubs. These back-to-back exemptions eliminate a costly, time-consuming bureaucratic step that uniquely penalized Indian passport holders among major-economy nationals.",
        "tags": ["travel", "visa", "germany", "france", "europe", "transit", "indian passport"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/big-relief-for-indian-flyers-after-france-germany-lifts-airport-transit-visa-requirement-11748839685015.html"},
            {"name": "IANS Live", "url": "https://ianslive.in/news/india-welcomes-germanys-visa-free-transit-for-indian-travellers-20260602205000"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-suspend-manchester-flights-from-august-31-amid-rising-costs-and-airspace-constraints/article69645319.ece"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/headlines/3354241-germany-scraps-airport-transit-visa-requirement-for-indian-travellers"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/32527327/pexels-photo-32527327.jpeg",
        "body": """Germany has formally scrapped the airport transit visa requirement for Indian nationals, effective June 3, 2026. The announcement, published in the Federal Law Gazette (*Bundesgesetzblatt*) on June 2, means Indian passport holders can now connect through Frankfurt, Munich, Düsseldorf, and every other German airport without obtaining the Schengen Type A transit visa that was previously mandatory — even for passengers who never left the secure airside zone.

The move follows France's identical decision, which took effect on April 10, 2026. In the space of eight weeks, two of Europe's three busiest transit hubs have eliminated a paperwork requirement that affected millions of Indian travellers annually.

## What Changed — and Why It Matters

Until now, Indian citizens ranked among a small group of nationalities — alongside Afghans, Somalis, and Syrians — who needed a dedicated transit visa simply to change planes at a European airport. The Schengen Type A visa cost around €80, required an appointment at a consulate, and could take two to four weeks to process. For families of four connecting through Frankfurt en route to, say, Nairobi or São Paulo, that meant €320 and a month of lead time for a layover in a terminal lounge.

The German Embassy in New Delhi traced the decision to Federal Chancellor Friedrich Merz's visit to India in January 2026, during which he and Prime Minister Narendra Modi agreed to "facilitate the movement of people" between the two countries. France had made its commitment during President Macron's visit in February, operationalising it by April.

India's Ministry of External Affairs welcomed the move. "This new arrangement would further enhance people-to-people ties between India and Germany," the MEA said in a statement.

## The European Transit Map for Indian Passports

With France and Germany now off the list, the transit visa landscape for Indian passport holders connecting through Europe has shifted meaningfully:

**No transit visa needed:** France (since April 10, 2026), Germany (since June 3, 2026), United Kingdom (if holding a valid US, Canadian, Australian, or New Zealand visa), Netherlands (with a valid Schengen visa for another purpose)

**Transit visa still required:** Spain, Italy, Belgium, Austria, Czech Republic, Portugal, Greece, and most other Schengen states

The practical impact is largest for connections through Frankfurt Airport — the third-busiest in Europe and the single most common European transit point for flights between India and the Americas, sub-Saharan Africa, and Northern Europe. Paris Charles de Gaulle, Europe's second-busiest, now offers the same frictionless transit.

## What NRIs Need to Know

For Indian Americans, the change has immediate implications:

**Booking flexibility widens.** Connecting through Frankfurt or Paris is now no different from connecting through Dubai, Doha, or Istanbul — no pre-arranged transit paperwork. This opens cheaper routing options on Lufthansa, Swiss, Austrian, Air France, and KLM that many Indian travellers previously avoided to dodge the transit visa hassle.

**Spontaneous rerouting becomes possible.** Flight disruptions that reroute passengers through a German airport no longer carry the risk of being denied boarding for lacking a transit visa — a scenario that has tripped up NRIs in the past.

**The exemption is airside only.** If you want to leave the airport during a long layover — to visit the city, check into a hotel, or catch a train — you still need a standard Schengen visa. The transit visa exemption applies exclusively to passengers remaining within the international transit zone.

**Carry proof of onward travel.** While no transit visa is needed, airport staff may still verify that you hold a valid ticket to a third country and aren't attempting to enter German or French territory through the transit area.

## A Diplomatic Pattern Takes Shape

The back-to-back exemptions from France and Germany aren't coincidental. Both followed state visits where Indian market access and people-to-people ties were explicitly on the agenda. Bilateral trade between India and Germany hit a record high in 2024, and both countries signed agreements spanning trade, technology, health, and renewable energy during Merz's January visit.

For India's outbound travellers — projected to exceed 50 million by 2030 — the transit visa was a symbolic irritant as much as a practical one. Indians holding valid US green cards or B1/B2 visas had long questioned why they needed additional paperwork to sit in a Frankfurt terminal for two hours.

Whether other Schengen states follow France and Germany's lead remains to be seen. Italy and Spain, which also handle significant Indian transit traffic, have not announced similar plans. But the diplomatic template is now clear: a state visit, a bilateral trade package, and a transit visa exemption as a goodwill gesture. For Indian Americans booking their next flight to Delhi or Bengaluru, the question is no longer *if* the transit visa regime will erode, but *how fast*."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Srinagar Airport Shuts Down Two Days a Week Starting July — Kashmir Travel Plans Need a Rewrite",
        "subheadline": "Runway maintenance will close Srinagar's only commercial airport every Monday and Tuesday from July through September, with a complete 15-day shutdown from October 1. The timing clashes with peak tourism season and the Durga Puja holidays.",
        "slug": make_slug("srinagar-airport-closure-july-october-kashmir-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs planning summer or early-autumn trips to Kashmir — among the most popular homeland destinations for the diaspora — face serious scheduling constraints. The October shutdown falls during Durga Puja and Navratri, when many NRI families plan their annual India visits.",
        "tags": ["travel", "kashmir", "srinagar", "airport", "infrastructure", "nri travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/destinations/india-destinations/srinagar-airport-closure/"},
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/why-srinagar-airport-will-remain-closed-two-days-a-week-all-you-need-to-know-11748871123614.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/srinagar-airport-announces-partial-runway-closure-from-july-2026-full-shutdown-from-october-1/article69645456.ece"},
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/srinagar-airport-to-shut-for-15-days-from-oct-1/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/22/Lapangan_terbang_Srinagar.jpg",
        "body": """Srinagar International Airport will suspend all flight operations every Monday and Tuesday from July 1 through September 30, 2026, and shut down completely for 15 days from October 1 to October 16. The closures, announced on June 2, are part of a runway repair and resurfacing programme coordinated with the Indian Air Force, which shares the airfield with commercial aviation.

For NRIs planning summer or autumn visits to Kashmir — consistently one of the most sought-after homeland destinations for the Indian diaspora — the disruption demands immediate attention. Flights already booked on affected days will need to be rescheduled, and the October shutdown collides directly with the Durga Puja and Navratri holiday window when many families time their annual India trips.

## The Closure Schedule

The maintenance programme unfolds in two phases:

**Phase 1 (July 1 – September 30):** The runway will be unavailable every Monday and Tuesday. Srinagar Airport currently handles 35 to 40 arrivals and departures daily; on closure days, that number drops to zero. Wednesday through Sunday operations continue, though the airport's existing restricted operating window — flights are already limited to 8 AM to 5 PM under a NOTAM issued in April — remains in effect.

**Phase 2 (October 1 – October 16):** A complete, uninterrupted shutdown of all runway operations. No commercial flights in or out of Srinagar for two full weeks. The runway work is expected to be completed by late November, restoring full operations before winter.

Airport Director Javed Anjum confirmed the revised schedule, which replaces an earlier plan that would have closed the airport on weekends between August and mid-October. The shift to Monday-Tuesday closures was designed to preserve weekend capacity, when tourist traffic peaks.

## Why This Hits NRI Travel Plans Hard

Kashmir's tourism calendar doesn't have an off-season anymore, but July through October is the spine of it. The summer months draw visitors to Gulmarg, Pahalgam, and the Mughal Gardens; September brings the famous *chinar* autumn colour; and October is festival season.

The October 1–16 shutdown is particularly brutal in its timing. Durga Puja begins October 1 this year, and Navratri follows shortly after — a period when domestic tourism to Kashmir surges, driven heavily by visitors from West Bengal, Maharashtra, and Gujarat. Travel operators in Srinagar are already warning of widespread trip cancellations and financial losses.

For NRIs, the calculus is different but equally challenging. Many diaspora families book India trips around October school breaks in the US, UK, and Canada. A two-week airport shutdown means the only way into Kashmir during that window is by road — the Jammu-Srinagar National Highway, a 10-hour drive on a good day, prone to landslides and military convoys.

## What NRIs Should Do Now

**Check existing bookings.** If you have flights to Srinagar on any Monday or Tuesday between July and September, contact your airline immediately. IndiGo, Air India, Air India Express, and Akasa Air are all expected to adjust their timetables, but proactive rebooking is safer than waiting for schedule changes to cascade.

**Avoid October 1–16 entirely** for Kashmir travel unless you're willing to drive from Jammu. There are no indications that charter or military-facilitated civilian flights will operate during the full shutdown.

**Consider alternative timing.** Late June — before the closures begin — or late October through mid-November, after the runway work wraps up, are the cleanest windows. November's early snowfall in Gulmarg also makes it a compelling shoulder-season option for skiers.

**Book flexible fares.** Given that the maintenance schedule is described as "currently in the planning phase" and subject to formal approval, there's a non-zero chance the dates shift. Refundable or easily changeable tickets are worth the premium.

**Explore Jammu as an entry point.** Jammu Airport (IXJ) operates normally and is the default alternative when Srinagar is disrupted. From Jammu, you can drive to Srinagar (approximately 300 km, 8–10 hours via the Jammu-Srinagar Highway) or take a helicopter if commercial heli-services are available. Several NRIs with family homes in the Valley have used Jammu as a staging point during past disruptions.

## The Bigger Picture

The runway work is genuinely necessary. Srinagar's runway has been under partial restrictions since April 2026, with payload limitations imposed on aircraft for safety reasons. Once completed, the upgraded surface will improve operational efficiency, reduce weather-related disruptions — frequent in Kashmir — and allow the airport to handle larger aircraft and higher passenger volumes.

Officials emphasize that the temporary pain will yield decades of reliable operations. The airport's role as Kashmir's primary commercial link to the rest of India and, increasingly, to international destinations makes the investment hard to argue against.

But the timing — smack in the middle of peak season, overlapping with India's most important autumn festivals — will test the patience of travellers, tour operators, and the roughly 200,000 passengers estimated to be affected over the three-month partial closure period. For NRIs who plan their Kashmir trips a year in advance, the message is simple: check the calendar, call the airline, and have a backup plan."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
