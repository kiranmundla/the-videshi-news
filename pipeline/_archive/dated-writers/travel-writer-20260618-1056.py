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
        "headline": "Air India Is Wiring Up the Smaller Cities — and Varanasi Is the First Door to 17 Global Hubs",
        "subheadline": "A new hub-and-spoke service starting June 25 lets travelers from India's secondary cities connect to London, Frankfurt and Singapore on one ticket, transiting Delhi as domestic flyers.",
        "slug": make_slug("air-india-easy-connect-varanasi-hub-spoke-secondary-cities-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "For the millions of NRIs whose families live beyond the big metros, one-ticket connectivity from cities like Varanasi means parents and relatives can finally reach Western hubs without booking risky separate domestic legs or hauling bags through Delhi's international transfer maze.",
        "tags": ["travel", "airlines", "air india", "airports"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "eGlobal Travel Media — Air India Easy Connect Flights Launch from Varanasi", "url": "https://www.eglobaltravelmedia.com.au/2026/06/air-india-easy-connect-flights-launch-from-varanasi-june-25/"},
            {"name": "Air India Newsroom — Network Expansion", "url": "https://www.airindia.com/in/en/about-us/press-release.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20848212/pexels-photo-20848212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Passengers wait at an airport boarding gate ahead of an international departure",
        "image_attribution": "Pexels",
        "body": """Air India is quietly rewriting the map for travelers who don't live next door to a big international airport. Starting June 25, the airline launches what it calls **Easy Connect**, a hub-and-spoke service that lets passengers from secondary Indian cities buy a single ticket to global destinations and transit Delhi as domestic flyers rather than wrestling with international transfers.

Varanasi is the first spoke. The designated Easy Connect flight, numbered AI1111, will fly daily from Varanasi to Delhi, timed so that within four hours of landing, passengers can connect onward to 17 international destinations — among them London Heathrow, Frankfurt, Milan, Rome, Zurich, Manila, Singapore, Phuket, Kuala Lumpur, Riyadh and Dubai. Subsequent spoke flights will carry the AI11XX numbering, building a distinct network identity for the model.

## Why the small-city angle matters

For decades, the friction in flying home wasn't the long-haul leg — it was the last mile inside India. A family member in a Tier-2 city who wanted to reach Newark or London usually had two bad options: book a domestic ticket separately and pray the connection held, or route through Mumbai or Delhi as an international transfer, re-checking bags and clearing immigration twice. A missed domestic connection on a separate ticket meant eating the cost of the international leg.

Easy Connect collapses that risk. Because the whole itinerary sits on one Air India ticket, baggage is checked through to the final destination, and a delay on the feeder flight becomes Air India's problem to re-accommodate, not the passenger's. Travelers transit Delhi within a familiar domestic environment before stepping into the international terminal.

## The NRI calculation

This is squarely aimed at the diaspora's reality. The Indian American community is not concentrated in Delhi and Mumbai alone — it has deep roots in Uttar Pradesh, Bihar, Gujarat and the south, and those roots stretch into smaller cities that have never had reliable global connectivity. Varanasi alone is both a spiritual magnet and the home district for thousands of families whose children now live in New Jersey, Houston and the Bay Area.

A daughter in Edison who wants to bring her parents over for a grandchild's birth, or a son in London visiting an ailing relative, no longer has to coordinate a fragile multi-airline puzzle. One booking, one fare, bags checked through.

P. Balaji, Air India's Group Head for Governance, Risk, Compliance and Corporate Affairs, framed the rollout as the product of heavy coordination across airlines, airports and government agencies, and said the model would expand to several additional cities in phases over the coming months.

## What to watch

The first thing to confirm is the connection buffer. Air India is promising onward links within four hours of arrival at Delhi — generous enough to absorb a modest delay, but travelers should still build in margin for international check-in and security at Terminal 3, especially during peak diaspora travel windows around Diwali and the summer holidays.

The second is fare competitiveness. Single-ticket convenience is only a win if the bundled price stays close to what a savvy traveler could assemble independently. Air India's pitch is that the seamless transit and protected connection justify booking the whole journey as one product.

Bookings for Easy Connect are open across Air India's website, mobile app, contact center and travel agents. For NRIs who have spent years apologizing to relatives about the ordeal of getting to and from a small Indian city, the more interesting question is which spoke comes next — and whether Patna, Lucknow, Coimbatore or Indore makes the list.

For now, Varanasi is the proof of concept. If it holds up through a full festival season, the hub-and-spoke model could finally make "flying home" mean flying all the way home, not just to the nearest metro."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Oman Is Quietly Becoming the Gulf's Smartest Stop for Indian Travelers — and Your US Visa Is the Key",
        "subheadline": "Indian arrivals to Oman have jumped 70% as the sultanate leans into visa-on-arrival for US and Schengen visa holders, positioning itself as a calmer, cheaper alternative to Dubai.",
        "slug": make_slug("oman-top-destination-indian-tourists-visa-on-arrival-us-visa-nri"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "Indian Americans holding a valid US visa or green card can land in Oman on a visa-on-arrival, turning a layover on the way to India into a low-friction beach-and-mountain detour without a consulate run.",
        "tags": ["travel", "visa", "middle east", "oman"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Oman Emerges as Top Destination for Indian Tourists", "url": "https://theindianeye.com/oman-emerges-as-top-destination-for-indian-tourists-in-the-middle-east/"},
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 71,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/38014529/pexels-photo-38014529.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The rugged mountain landscape of Oman, a growing draw for Indian travelers",
        "image_attribution": "Pexels",
        "body": """While the diaspora's attention stays fixed on Dubai, a quieter Gulf destination is pulling ahead in the affections of Indian travelers. Oman welcomed more than 600,000 Indian tourists last year, a roughly 70% jump over 2023, making India the sultanate's largest tourism market outside the Gulf Cooperation Council.

For Indian Americans, the most useful detail is buried in the fine print of Oman's entry rules: the country offers a visa-on-arrival for Indian passport holders who already hold a valid US or Schengen visa or residence permit. That single provision turns Oman from a place requiring advance paperwork into an easy add-on.

## The US-visa shortcut

The logic is the same one that makes Mexico and a clutch of other countries accessible to Indians who carry a US visa: a wealthy, vetted destination decides that a traveler good enough for Washington's screening is good enough for theirs. For an NRI flying between, say, San Francisco and Kochi, Oman becomes a viable stopover or standalone trip with no consulate appointment, no waiting on processing, and no risk of a rejected application derailing plans.

Muscat sits conveniently on Gulf routings, and the practical upshot is that a green-card holder or US-visa-carrying Indian can break a long journey home with a few days of mountains, wadis and coastline instead of another sterile airport layover.

## What Oman is selling

Oman's pitch leans on contrast. Where Dubai sells superlatives and spectacle, Oman sells landscape and quiet — dramatic mountain ranges, the fjord-like khors of Musandam, pristine coastline, and a culture that has not been bulldozed for tourism. Azzan Qassim Al Busaidi, Undersecretary at Oman's Ministry of Heritage and Tourism, attributed the surge to the "closeness and proximity between Oman and India" and the minimal travel restrictions between the two countries.

The ministry has made tourism one of five focus areas under its Vision 2040 plan and has been courting the Indian market directly, including a recent road show in Mumbai aimed at travel agents and a planned slate of consumer promotions and luxury campaigns.

## Why it lands with the diaspora

The appeal to NRI families is straightforward. Multi-generational travel — grandparents, parents, kids — does badly in destinations built around nightlife and shopping malls, and does well in places with nature, space and a slower pace. Oman's adventure-sports growth (trekking, diving, dune drives) gives teenagers something to do, while the heritage forts, souks and coastline suit older travelers who find Dubai overwhelming.

Cost is the other quiet advantage. Oman generally undercuts Dubai on hotels and dining, which matters for a family of five stretching a vacation budget that also has to cover the onward leg to India. A few days in Muscat or the Musandam peninsula can be folded into an India trip for far less than an equivalent stop in the UAE, and the shorter crowds mean more of the budget goes toward experiences rather than queueing.

## The practical checklist

A few things to confirm before booking. The visa-on-arrival concession is tied to holding a valid US, UK, Canadian, Japanese or Schengen visa or residence permit, plus, in some cases, a 14-day stay window — so travelers should verify current terms on Oman's official portal before flying, as Gulf entry rules shift with little notice. Carry the physical or digital proof of the qualifying visa, since the concession is worthless without it at the counter.

For the diaspora, Oman is shaping up to be the kind of destination that rewards the traveler who reads the fine print: a calmer, cheaper, more scenic Gulf stop that a US visa unlocks almost as an afterthought. As Dubai grows more crowded and expensive, expect more Indian American families to discover that the better Gulf holiday was one emirate's neighbor away all along."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "As India's Cities Bake, the Diaspora's Summer Trip Is Moving to the Mountains",
        "subheadline": "Rishikesh, Manali, Leh and Spiti are absorbing the season's travelers fleeing the heat — and an early, below-normal monsoon is making the high-altitude circuit unusually easy to plan this year.",
        "slug": make_slug("india-summer-high-altitude-escape-leh-spiti-manali-monsoon-nri"),
        "category": "travel",
        "vertical": "destinations",
        "diaspora_angle": "NRI families timing a summer India trip around school holidays can skip the furnace-like plains entirely — the Himalayan circuit offers cooler weather, lower monsoon-season airfares and activities that actually work for kids and grandparents traveling together.",
        "tags": ["travel", "india", "monsoon", "himalaya"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — High-Altitude Adventure Zones in India's Peak Summer", "url": "https://www.travelandtourworld.com/news/article/rishikesh-manali-leh-spiti-valley-and-bir-billing/"},
            {"name": "Wego Travel Blog — Best Monsoon Destinations in India 2026", "url": "https://blog.wego.com/monsoon-destinations-india/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37839625/pexels-photo-37839625.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "High-altitude Himalayan landscape in the Ladakh region of northern India",
        "image_attribution": "Pexels",
        "body": """Every summer, the same calculation faces the NRI family planning a trip back to India: the school holidays line up perfectly, and the destination is an oven. This year, a growing number of travelers are answering the heat the same way Indians increasingly are — by heading straight for the mountains.

A clear seasonal shift is underway across northern India, with Rishikesh, Manali, Leh, Spiti Valley and Bir Billing absorbing the travelers fleeing city and lowland temperatures. These aren't just cooler postcards; they form a connected high-altitude circuit built around rafting, trekking, paragliding and long-distance road travel, with each town serving as a distinct entry point into the mountains.

## Why this year is easier to plan

Two weather facts make 2026 unusually friendly for the mountain route. India's southwest monsoon arrived in Kerala on May 24 — the earliest onset since 2009 — and the India Meteorological Department has forecast rainfall at 92% of the long-period average, the first below-normal forecast since 2023.

For travelers, a slightly drier monsoon is largely good news: fewer landslide closures in the Western Ghats, drier mornings at hill stations, and more predictable road conditions across the Himalayas. The trade-off most relevant to a budget-conscious diaspora family is the pricing. Domestic flight fares drop 30–50% versus peak winter rates on popular routes during the monsoon months, and hotel rates across India dip significantly from July through early September.

## Matching the destination to the family

The circuit's strength is that it spreads across very different travel styles.

**Rishikesh** is the most structured river-adventure base, with white-water rafting on the Ganges at a range of difficulty levels, plus kayaking, cliff jumps and riverside camping run through guided operators — ideal for families with active teenagers but also reachable as a gentler spiritual-and-yoga stop for elders.

**Manali** remains the accessible gateway, well connected by road and rich in day trips, suiting multi-generational groups who want mountain air without a punishing journey.

**Leh and Spiti** sit at the demanding end — trans-Himalayan high desert, dramatic monasteries and serious altitude. They reward travelers who can spend the days acclimatizing and don't mind basic infrastructure, and they are best left off the itinerary for very young children or relatives with heart or breathing conditions.

**Bir Billing** is India's paragliding capital, a specialist draw for the adventurous.

## The NRI angle

For Indian Americans, the high-altitude shift solves the perennial summer problem. A trip timed to US school holidays no longer means subjecting kids raised on temperate summers — and grandparents who tire in the heat — to 43°C afternoons in the plains. The mountains offer comfortable daytime temperatures, genuine activities, and the kind of shared-experience travel that makes a long-haul trip worth the jet lag.

There's also a practical sequencing trick. Many diaspora itineraries already require a stop in a metro to see family before any leisure leg. Routing the leisure portion north — flying into Delhi, then on to Dehradun, Bhuntar (for Manali) or Leh — keeps the heat exposure to a minimum and takes advantage of the monsoon-season fare dip on those domestic hops.

## Plan around the altitude, not just the calendar

The one caution is altitude itself. Leh sits above 3,500 meters, and Spiti higher still; acute mountain sickness does not care how fit the traveler is. Build in acclimatization days, avoid flying straight to the highest points and then immediately exerting, and consult a doctor before taking elderly relatives to the extreme-altitude stops.

Handled with that respect, the mountain circuit is shaping up as the smart diaspora play for summer 2026 — cooler, cheaper, and far more memorable than another sweltering fortnight in the plains."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
