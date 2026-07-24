#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

parks_body = """America's national parks are doing something this summer that they have not done in years: getting easier to visit. After several seasons of timed-entry reservations that forced families to set phone alarms for the moment booking windows opened, the National Park Service has dialed back the gatekeeping at some of its most popular parks for 2026 — a quiet but consequential shift for the NRI families who treat a great American road trip as the centerpiece of a summer vacation.

## The big change: fewer reservations to chase

The headline is access. The Park Service announced visitor-access plans for summer 2026 that lean on parking and traffic management rather than advance reservations at several marquee parks. Arches National Park in Utah, which spent recent summers behind a timed-entry system, will not require advance reservations this year — you can drive up during operating hours, with the caveat that staff may temporarily pause entry when lots fill. Yellowstone confirms no reservation is needed to enter; you just need an entrance pass. Mount Rainier, which trialed timed entry, is also skipping it for 2026 in favor of parking-management strategies.

For a family coordinating cousins flying in from two coasts — or grandparents visiting from India who want to see the landscapes they have only watched in films — removing the reservation lottery takes a real planning headache off the table. You can build the trip around the people, not around a booking server.

## The other gift: free-entry days

The Park Service also publishes a handful of fee-free days each year, and several fall right in the prime travel window. The remaining 2026 free-entry dates are the Independence Day weekend of July 3–5, the Park Service's 110th birthday on August 25, Constitution Day on September 17, Theodore Roosevelt's birthday on October 27, and Veterans Day on November 11. On those days, the standard $20–$35 per-vehicle entrance fee is waived. (Note that the agency dropped Juneteenth and Martin Luther King Jr. Day from this year's free-entry lineup, so don't plan around those.)

A word of realism: free days are popular days. If you are chasing the savings, arrive early, and treat the waived fee as a bonus rather than a reason to visit at peak crush.

## Why this lands for NRI families

Indian American families over-index on exactly the kind of trip national parks reward: multi-generational, road-trip-based, and built around shared experience rather than nightlife. The great Southwest loop — Grand Canyon, Zion, Bryce, Arches, Monument Valley — is a rite of passage that maps neatly onto a one- or two-week summer break, and it photographs like nothing back home. With airfares up sharply this summer and many travelers swapping pricey international trips for drives closer to home, a parks road trip is also simply better value than a long-haul holiday this year.

There is a practical immigration angle too. Visiting relatives on a B-2 visa can absolutely join a national-parks trip; the parks ask for an entrance pass, not a passport. For green-card holders and citizens who travel often, the $80 America the Beautiful annual pass pays for itself in about three park visits and covers everyone in the vehicle.

## How to do it well in 2026

- **Book lodging and campgrounds early.** This is the one place reservations still bite. In-park lodges and campgrounds at Yellowstone, Yosemite and the Grand Canyon book out months ahead, even though entry itself is walk-up.
- **Go early or late in the day.** Where parks use parking management instead of timed entry, arriving before 8 a.m. or after 4 p.m. is the difference between a smooth visit and a closed parking lot. Long summer daylight makes evening visits genuinely pleasant.
- **Buy the annual pass if you'll hit three or more parks.** A single Southwest loop alone usually clears that bar.
- **Check the specific park's page before you drive.** A few high-demand spots and individual attractions (Yosemite's peak-period access, Rocky Mountain, and certain trailheads) still use targeted tools, so confirm the rules for your exact dates rather than assuming.
- **Pack patience for the free days.** July 3–5 and August 25 will be busy. Midweek visits remain the quietest.

## The bottom line

Summer 2026 is one of the friendlier years in recent memory to plan a US national-parks trip: fewer reservation hoops, a clutch of fee-free dates, and a domestic-travel surge that makes the parks both a smart-value and crowd-tested choice. For diaspora families looking to give visiting relatives an unforgettable slice of America — or simply to get the kids off screens and under a big Western sky — the gate is, this year, a little more open."""

mexico_body = """For Indian passport holders, Mexico has always carried an asterisk. There is no visa-on-arrival, and applying through a consulate in India is a paperwork slog. But there is a workaround that most NRIs already qualify for and many still don't realize they can use: if you hold a valid US visa, you can enter Mexico without a separate Mexican visa. With the FIFA World Cup 2026 turning Mexico into a magnet this summer, it is worth knowing exactly how the rule works.

## The rule, in plain terms

An Indian citizen who holds a valid, multiple-entry US visa — of any category, including a B-1/B-2 tourist visa — can enter Mexico visa-free for tourism or business for up to 180 days. The same exemption extends to those holding valid visas or permanent residence from Canada, the United Kingdom, Japan, or any Schengen Area country. The key conditions: the visa must be valid for the duration of your Mexico stay, and the underlying passport must have at least six months' validity.

There is one important nuance buried in the fine print. The exemption is built for visitors, not residents. If your US status is a temporary or work-style category in some jurisdictions' reading, check the specific requirement before you book — but for the typical NRI on a B-1/B-2, H-1B with a valid visa stamp, or a US green card, the visa-free entry path is straightforward.

## The one form you still need

Visa-free does not mean paperwork-free. Travelers arriving by air should complete Mexico's electronic authorization system (the online entry form) before departure and carry a printed copy to show at check-in and on arrival. It takes a few minutes online — a world away from a consular visa appointment. Airlines will ask to see proof of your US visa at check-in, so keep the physical visa and passport accessible, not buried in checked baggage.

## Why the timing matters: World Cup 2026

Mexico is co-hosting the FIFA World Cup with the United States and Canada this summer, and it has leaned into one of the most visitor-friendly entry postures of the three host nations — visa-free access for citizens of dozens of countries and simplified entry for holders of US, Canadian, UK, Japanese and Schengen visas. For the cricket-and-football-loving diaspora, that opens an obvious combination: catch matches in the US, then hop south to Mexico City, Guadalajara or Monterrey for more football and a genuinely different holiday, all on the strength of the US visa already in the passport.

Even for NRIs who could not care less about football, the World Cup summer is a reminder that Mexico is a far easier add-on to a US trip than most assume. Cancún and the Riviera Maya are a short flight from Texas and the East Coast, and the beaches, Mayan ruins and food make it a strong choice for a family week.

## Why this matters to the diaspora

This is the quiet superpower of the US visa or green card for Indian travelers: it unlocks a string of destinations that would otherwise require their own visa runs. Mexico is the headline example, but the same US-visa perk smooths entry into several Caribbean and Latin American destinations, and most recently Argentina opened visa-free access for Indians holding a valid US visa or green card. For a community that knows the pain of the Indian passport's limited reach, stacking these perks is how you turn one hard-won US visa into a far wider map.

## Practical checklist before you fly

- **Confirm your US visa is multiple-entry and valid** through your entire Mexico stay. A single-entry visa already used to enter the US will not qualify.
- **Complete the online entry authorization** before departure and print it.
- **Carry the physical passport and US visa** — airlines verify both at check-in.
- **Check six-month passport validity.** Mexico, like most destinations, can deny boarding on a passport too close to expiry.
- **Verify rules close to departure.** Entry policies have been unusually fluid in 2026; a quick check of the Mexican consulate's current guidance before booking is cheap insurance.

For the millions of Indians already living in or regularly visiting the US, Mexico is not the bureaucratic ordeal the passport ranking suggests. The visa you already have is, in effect, the key."""

hotels_body = """India is in the middle of a hotel-building boom, and the timing is no accident. With airfares up, the rupee soft, and overseas trips pricier, a wave of Indians who might have holidayed in Dubai or Bangkok are staying home — and global hotel chains are racing to give them somewhere to stay. For NRIs planning a trip back, the upshot is a richer, more polished set of places to base a visit than even a couple of years ago.

## The headline opening: Marriott's 10,000th hotel is in India

Marriott chose India for a milestone. The company opened its 10,000th property worldwide with the JW Marriott Ranthambore Resort and Spa, set near Ranthambore National Park in Rajasthan — tiger country, and one of the most evocative settings in the Indian wildlife circuit. The resort offers 127 rooms, suites and private villas, and slots neatly into the kind of itinerary NRI families love: a few days of heritage and forts in Jaipur or Jodhpur, then a safari-and-spa wind-down within striking distance of a national park.

That a global chain marked its ten-thousandth hotel in India, rather than New York or Dubai, is its own signal about where the industry sees demand heading.

## The pipeline is deep — and it's leaning luxury

Marriott's flagship opening is one data point in a much larger surge. IHG has signed a 140-key voco hotel in Udaipur at the foothills of the Aravallis, targeting the city's booming wedding and leisure market. Accor is bringing a large convention hotel under the Novotel brand to Lucknow's fast-growing Golf City corridor. Hilton's first LXR property in India, The Den Bengaluru, is on the way for business and leisure travelers in the tech capital. And Marriott, with its partner CG Hospitality, has a multi-property South Asia expansion underway, including a JW Marriott in Siliguri — the gateway to Darjeeling, Sikkim and the Northeast.

The common thread is geographic spread. The new supply is not just in the metros; it is landing in Udaipur, Ranthambore, Siliguri and Lucknow — exactly the tier-two and leisure destinations that NRI itineraries increasingly favor over a predictable Delhi-Mumbai hotel stay.

## Why the boom is happening now

The driver is a reshuffling of where Indians are spending their holiday money. Geopolitical tension in the Middle East has curbed some outbound travel, airlines have raised fares and trimmed capacity, and a weak rupee has made overseas trips costlier. The result is a domestic-tourism surge that hotel groups are rushing to meet. India Ratings expects the country's hotel demand and supply to grow 10–15% this financial year, and mid-market chains are expanding aggressively — Royal Orchid alone plans to add 50 hotels in the next 12 to 18 months, betting squarely on Indians traveling at home.

Religious tourism, large-scale weddings and business travel are the engines. For travelers, more supply usually means more choice and, eventually, more competitive rates outside peak wedding and festival dates.

## What it means for NRIs

For diaspora travelers, three practical takeaways stand out.

- **Better bases in leisure destinations.** The trip back home no longer has to mean a business hotel in a metro. Branded resorts in Ranthambore, Udaipur and the Northeast make it easier to combine family visits with a genuine holiday, with the service standards and loyalty-point earning that frequent flyers value.
- **Loyalty points travel well.** NRIs who rack up Marriott, Hilton or IHG points on US and business travel can now spend them across a much wider Indian footprint — including these new leisure properties — which can meaningfully cut the cost of an extended trip home.
- **Book ahead for wedding and festival season.** The same demand surge that is driving construction also fills rooms. Diwali, the November–February wedding season, and major pilgrimage dates see the sharpest crunch; the new supply helps, but the best properties in places like Udaipur still sell out months ahead.

## The bottom line

India's hospitality map is being redrawn in real time, and it is being redrawn toward exactly the places diaspora families want to go. A boom born of Indians choosing to holiday at home has, as a side effect, handed NRIs a deeper, more polished menu of places to stay on the next trip back — from a tiger-country resort that happens to be a global chain's 10,000th hotel to lake-view luxury in Udaipur. For anyone planning a visit, it is a good year to aim a little higher than the usual."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "America's National Parks Just Got Easier to Visit This Summer — A Road-Trip Guide for NRI Families",
        "subheadline": "Several marquee parks are dropping timed-entry reservations for 2026, and a run of fee-free days falls right in the summer window. Here's how diaspora families can plan the great American road trip.",
        "slug": make_slug("us-national-parks-summer-2026-nri-family-road-trip-guide"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "Indian American families over-index on multi-generational road trips, and 2026's rollback of national-park reservations plus fee-free days makes the great American parks loop both cheaper and far easier to plan — including for visiting relatives on a B-2 visa, who need only an entrance pass, not a passport.",
        "tags": ["travel", "national-parks", "road-trip", "usa", "family"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "National Park Service — Summer 2026 access plans", "url": "https://www.nps.gov/orgs/1207/nps-expands-access-summer-2026.htm"},
            {"name": "USA Today — 2026 free entry days", "url": "https://www.usatoday.com/story/travel/news/2026/06/national-parks-free-entry-days/"},
            {"name": "NPS — Arches lifts entry reservation requirement for 2026", "url": "https://www.nps.gov/arch/learn/news/arches-2026-no-timed-entry.htm"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/33953347/pexels-photo-33953347.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A sweeping Yellowstone National Park landscape, one of the marquee US parks skipping timed-entry reservations in 2026.",
        "image_attribution": "Pexels",
        "body": parks_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Your US Visa Is the Key to Mexico — How Indian Travelers Can Skip the Visa and Catch the World Cup",
        "subheadline": "Indians with a valid US visa can enter Mexico visa-free for up to 180 days. With Mexico co-hosting the 2026 World Cup, here's exactly how the rule works and what paperwork you still need.",
        "slug": make_slug("mexico-visa-free-indians-us-visa-world-cup-2026-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Millions of Indians living in or visiting the US can enter Mexico visa-free on the strength of their existing US visa — turning a hard-won American visa into a far wider travel map, just as Mexico opens up for the 2026 World Cup.",
        "tags": ["travel", "visa", "mexico", "world-cup", "usa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Government of Mexico — visa exemption for US visa holders", "url": "https://consulmex.sre.gob.mx/reinounido/index.php/es/contenido/116-grupo-3"},
            {"name": "Travel And Tour World — World Cup 2026 host-nation entry policies", "url": "https://www.travelandtourworld.com/news/article/mexico-canada-united-states-fifa-world-cup-2026-streamlined-visa-policies/"},
            {"name": "BTW Visas — Mexico visa for Indians (updated 2026)", "url": "https://www.btwvisas.com/mexico-visa-for-indians/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20210498/pexels-photo-20210498.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A beach on Mexico's Caribbean coast near Cancún, an easy add-on for Indian travelers holding a valid US visa.",
        "image_attribution": "Pexels",
        "body": mexico_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Hotel Boom Is Reshaping Where NRIs Stay — Marriott's 10,000th Property Lands in Tiger Country",
        "subheadline": "A domestic-travel surge has global chains racing to open resorts in Udaipur, Ranthambore and the Northeast. For diaspora families, the trip home just got a richer set of places to stay.",
        "slug": make_slug("india-hotel-boom-2026-nri-marriott-ranthambore-udaipur"),
        "category": "travel",
        "vertical": "tourism",
        "diaspora_angle": "A boom born of Indians holidaying at home is handing NRIs a deeper, more polished menu of leisure-destination hotels for the trip back — and a far wider footprint to spend Marriott, Hilton and IHG loyalty points earned on US travel.",
        "tags": ["travel", "hotels", "india", "luxury", "tourism"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "Hotel Owner — Marriott opens 10,000th property in India", "url": "https://www.hotelowner.co.uk/marriott-international-opens-10000th-global-property-in-india/"},
            {"name": "Reuters — Royal Orchid plans 50 hotels on local demand", "url": "https://www.reuters.com/business/indias-royal-orchid-plans-add-50-hotels-betting-local-demand-boost/"},
            {"name": "Restaurant India — IHG signs voco Udaipur", "url": "https://www.restaurantindia.in/article/ihg-signs-voco-udaipur"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7195782/pexels-photo-7195782.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A lake palace in Udaipur, Rajasthan — one of the leisure markets at the center of India's 2026 hotel-building surge.",
        "image_attribution": "Pexels",
        "body": hotels_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
