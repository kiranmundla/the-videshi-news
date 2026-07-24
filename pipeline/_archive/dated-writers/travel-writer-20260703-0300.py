#!/usr/bin/env python3
"""Travel writer — 2026-07-03 03:00 PDT run. 3 articles."""
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
    return slug[:70].rstrip('-') + "-20260703"

# ──────────────────────────────────────────────
# ARTICLE 1: India Passport Fee Hike
# ──────────────────────────────────────────────

art1_body = """India's Ministry of External Affairs hiked passport fees on July 1 — the first revision in 14 years — and the new rates land squarely on the millions of Indian nationals who renew, replace, or apply for a fresh booklet every year. For the diaspora, the timing stings: it arrives just as summer travel season peaks, when consulate appointment slots in the US are already stretched thin.

## What changed

A standard 36-page adult passport now costs ₹2,500, up from ₹1,500 — a 67 per cent jump. The 60-page version, popular with frequent flyers who burn through visa pages, rose from ₹2,000 to ₹3,500. Tatkaal (urgent) processing shot up to ₹5,000 for a 36-page booklet, compared with ₹3,500 before. If you've lost your passport or it was damaged, the replacement fee nearly doubled: ₹5,000, up from ₹3,000.

Minors aren't spared. A child's 36-page passport now costs ₹1,750 (was ₹1,000), and the Tatkaal rate for a minor jumped to ₹4,250 from ₹3,000. The 10 per cent discount for children under eight and seniors over 60 still applies — but only on fresh applications, not reissues.

## The overseas price tag

Indian citizens renewing from abroad face a separate schedule. At US consulates, a fresh 36-page passport costs $125 (roughly ₹10,500 at current rates); Tatkaal runs $250. The 60-page booklet is $175 normal, $300 Tatkaal. Lost or stolen replacements cost $250 for a 36-page and $300 for a 60-page booklet.

These rates apply at all Indian missions and consulates worldwide, from Houston to San Francisco. Miscellaneous services such as Police Clearance Certificates — often needed for immigration applications — have gone from ₹500 to ₹750 domestically.

## Why it matters for NRIs

About 3.6 million Indian passports were issued or renewed in the US alone over the past five years, according to consular data. For a family of four — two adults and two children — the domestic cost of fresh passports just went from ₹5,000 to ₹8,500. From a US consulate, the same family is looking at $430, roughly ₹36,000.

The hike also comes as India's passport infrastructure evolves. The new e-passport, launched in late 2024 with an embedded chip, is now the standard issue. The MEA has been expanding Passport Seva Kendras and streamlining online appointments, but walk-in availability remains patchy at Indian consulates in the US.

OCI (Overseas Citizen of India) cardholders who still maintain an Indian passport — a common arrangement for NRIs shuttling between countries — will feel the pinch on renewals. So will parents applying for first-time passports for US-born children ahead of summer trips to India.

## The bigger picture

The revision, notified through the Passports (Amendment) Rules, 2026, replaces Schedule IV of the Passports Rules, 1980. The government has not changed passport validity: adult passports remain valid for 10 years, and minors get five years or until they turn 18, whichever comes first.

India issued over 14 million passports in 2025-26, a record. The MEA argues the fee hike will fund upgraded infrastructure and faster processing. Whether that materialises at overburdened overseas consulates remains to be seen.

**What to do now:** If your passport expires within the next year, file your renewal application before the next potential revision cycle. The online portal at passportindia.gov.in lets you schedule an appointment at your nearest Passport Seva Kendra or Indian consulate. Tatkaal slots, while expensive, typically cut processing to three to five working days domestically."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Hiked Passport Fees for the First Time in 14 Years — Here's What NRIs Pay Now",
    "subheadline": "A standard 36-page booklet now costs ₹2,500, Tatkaal runs ₹5,000, and overseas renewals start at $125. For a family of four, the maths has changed.",
    "slug": make_slug("india-passport-fee-hike-nri-overseas-renewal-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Millions of NRIs renew Indian passports at US consulates every year — the first fee hike since 2012 adds real costs for families maintaining dual documentation.",
    "tags": ["travel", "passport", "visa", "NRI", "MEA", "India"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Ministry of External Affairs — Passports (Amendment) Rules, 2026", "url": "https://www.passportindia.gov.in"},
        {"name": "Madhyamam Online — MEA hikes passport fees", "url": "https://madhyamamonline.com"},
        {"name": "Digit.in — New rules from July 1", "url": "https://www.digit.in"},
        {"name": "Asian News 18 — Centre raises passport fees", "url": "https://asiannews18.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "An open passport displaying various travel stamps at an airport check-in counter",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 2: India's Pilgrimage Hotel Boom
# ──────────────────────────────────────────────

art2_body = """The companies building India's next generation of hotels have something unusual in common: none of them have ever run a hotel.

On Monday, real estate developer Omaxe announced a dedicated hospitality vertical backed by ₹6,200 crore ($656 million) in planned investment. The company intends to build 19 hotels across 13 cities over four to five years. A month earlier, Adani Airport Holdings signed a deal with IHG Hotels & Resorts to develop five Kimpton-branded properties at Indian airports. And Hilton just opened four new hotels in Bengaluru in a single week while launching Spark by Hilton, its budget brand, for the first time in Asia Pacific.

The pattern is unmistakable: India's hospitality sector is no longer the exclusive domain of legacy operators. Infrastructure conglomerates, airport builders, and township developers are piling in, drawn by a demand boom that shows no signs of slowing.

## Follow the pilgrims

What sets Omaxe's bet apart is where the hotels will go. Of the 19 planned properties, 12 are in Uttar Pradesh — including two each in Ayodhya and Vrindavan, three in Lucknow, and one each in Prayagraj and Gorakhpur. The company will also build in Ujjain, Amritsar, and Chandigarh.

These are not conventional business travel cities. They are pilgrimage destinations that saw visitor numbers explode after the Ram Mandir inauguration in Ayodhya in January 2024. Prayagraj hosted the Maha Kumbh Mela in early 2025, drawing an estimated 450 million visitors over 45 days. Vrindavan and Ujjain remain year-round pilgrimage magnets for Hindu devotees worldwide.

"With improving connectivity, growing religious tourism and increasing travel across emerging markets, there is a clear need for quality hospitality infrastructure in these locations," said Mohit Goel, Omaxe's managing director.

## Why NRIs should care

For decades, visiting a holy city in India meant choosing between a government rest house and a no-name lodge with unreliable plumbing. The diaspora — particularly older parents making their annual temple circuit — tolerated it because the alternatives didn't exist.

That is changing. A Gateway Hotel by IHCL (Tata's Taj Hotels brand) is part of Omaxe's 50-acre mixed-use development in Dwarka, New Delhi. Hilton Garden Inn just opened in Bengaluru's Embassy Tech Village with a temperature-controlled pool and two restaurants. Adani's five Kimpton hotels will sit inside airport complexes in Mumbai, Jaipur, Mangaluru, and Thiruvananthapuram — the first design-forward international brand hotels at these gateways.

For NRIs flying into Mumbai or Jaipur and connecting onward to Ayodhya, Varanasi, or Ujjain, the journey no longer requires a quality drop-off after the international terminal. Branded, bookable, loyalty-point-earning hotels are arriving at exactly the destinations where the diaspora goes but the five-stars historically didn't.

## The numbers behind the boom

India's hotel room inventory is growing at its fastest pace in a decade. The country added roughly 18,000 branded rooms in 2025-26, yet occupancy rates held above 65 per cent nationally — a sign that supply is still chasing demand. India now ranks among the top five hotel construction pipelines globally.

Omaxe alone plans nearly 5 million square feet of hospitality space. The Adani-IHG partnership will add approximately 1,500 rooms across five properties. Hilton's India pipeline now exceeds 60 properties. And these are just the headline deals — dozens of smaller branded projects are underway in tier-two and tier-three cities across North India.

"India's next hotel boom is being built by companies that don't run hotels," as Skift put it. The operators — Taj, Hilton, IHG, Marriott — supply the brand and management expertise. The capital and land come from infrastructure players who already own the sites.

## What to watch

The real test is execution. Omaxe's 19 hotels are "subject to regulatory approvals and market conditions," the company noted — standard caveats in Indian real estate. Construction timelines in pilgrimage cities can be unpredictable, and labour availability fluctuates with agricultural seasons.

But the direction is clear. If you're an NRI planning a family trip to Ayodhya, Vrindavan, or Amritsar in the next three to four years, expect the accommodation options to look nothing like what your parents settled for."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Real Estate Giants Are Betting $656 Million That NRIs Want Better Hotels at India's Holy Cities",
    "subheadline": "Omaxe plans 19 hotels — including two in Ayodhya and two in Vrindavan. Add Adani's airport Kimptons and Hilton's Bengaluru blitz, and India's pilgrimage belt is getting a hospitality overhaul.",
    "slug": make_slug("india-pilgrimage-hotel-boom-omaxe-ayodhya-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India's pilgrimage destinations have long settled for subpar accommodation — a wave of branded hotels at Ayodhya, Vrindavan, and Amritsar is about to change that.",
    "tags": ["travel", "hotels", "India", "pilgrimage", "Ayodhya", "NRI", "Omaxe", "Hilton", "Adani"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Skift — India's Next Hotel Boom Is Being Built by Companies That Don't Run Hotels", "url": "https://skift.com"},
        {"name": "First Construction Council — Omaxe to Invest Rs 62 Billion", "url": "https://firstconstructioncouncil.com"},
        {"name": "Asian Hospitality — Omaxe Adds Hospitality Business", "url": "https://asianhospitality.com"},
        {"name": "Outlook Traveller — Hilton Expands India Portfolio", "url": "https://outlooktraveller.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33803739/pexels-photo-33803739.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A hotel lobby in Bikaner, Rajasthan, showcasing the elegant Indian hospitality style now arriving at pilgrimage cities",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ──────────────────────────────────────────────
# ARTICLE 3: River Cruises on the Ganges
# ──────────────────────────────────────────────

art3_body = """The pitch is simple: skip the overnight train, the dodgy taxi, and the predawn queue at the ghat. See India from the river instead. A wave of international luxury cruise operators is betting that the Ganges, the Hooghly, and the Brahmaputra can draw the kind of traveller who currently books the Mekong or the Danube — and that the biggest untapped market for these voyages is the Indian diaspora itself.

## What's launching

Scenic Group, the Australian luxury cruise and touring company, announced last month that it will deploy its 44-passenger *Scenic Aura* on India's Hooghly River starting October 2027. The ship will sail all-inclusive itineraries through West Bengal, with land extensions spanning North India, South India, Rajasthan, and Sri Lanka. Trips range from 17 to 25 days. Land groups will be capped at 25 guests.

"These itineraries have been thoughtfully designed to provide unique and exclusive experiences that are culturally rich and showcase the best of India and Sri Lanka," said Adam Burke, Scenic's journey designer for Asia. The ship, previously deployed in Myanmar, will be refitted with private-balcony suites, up to four dining venues, and a resort-style pool.

Viking, the world's largest river cruise line, is also entering India — with plans to launch Brahmaputra River cruises in 2027, opening a corridor through Assam and the Northeast that has been virtually inaccessible to luxury travellers.

Meanwhile, Uniworld Boutique River Cruises already operates the *Ganges Voyager II* on India's most storied waterway. Its "Sacred Ganges & Maharajas' Express" package combines a river cruise with overland rail travel through Delhi, Agra, Jaipur, Jodhpur, and Mumbai — a 16-day odyssey that starts around $12,000 per person.

## Why the Ganges, and why now

India's Ministry of Tourism has identified river tourism as a strategic priority. The country's 20,000-plus kilometres of navigable waterways remain almost entirely untapped for tourism. Inland Waterways Authority of India has invested heavily in terminal infrastructure on the Ganga, and the Jal Marg Vikas Project has deepened the Varanasi-to-Haldia stretch to allow year-round commercial navigation.

The cruise industry sees India as the next Southeast Asia: spectacular cultural heritage, a government eager for tourism revenue, and a river system that threads through cities no road trip can match. The Hooghly alone passes Kolkata, Chandernagore (a former French colony), Murshidabad (the old Mughal provincial capital), and the battlefield of Plassey — all within a nine-night sailing.

## The NRI opportunity

Here's the quiet logic behind these launches: the average Indian American household earns about $150,000 a year. River cruises on the Danube or the Rhine run $5,000 to $10,000 per person — a price point the diaspora already spends on European and Alaskan cruises. But few have considered doing the same in India.

That's partly because the product didn't exist. Scenic Aura's 44-passenger capacity signals ultra-premium positioning: this isn't a crowded ferry from Varanasi to Patna. It's champagne at Kathgola Palace, a private tour of the Hooghly Imambara mosque, and a chef's table overlooking rice paddies at sunset.

For NRIs, these cruises solve a logistical headache that has plagued family trips to India for generations. Instead of coordinating trains, drivers, and hotels across five cities, a single booking covers transport, meals, accommodation, and guided experiences. Parents and in-laws who can't manage the pace of a traditional India road trip can cruise in comfort while still experiencing the cultural depth that made them want to visit in the first place.

## What it costs — and what to book

Uniworld's India itineraries for the 2026-27 season start around $8,000 per person for the 13-day "Golden Triangle & Sacred Ganges" package. The 16-day version with the Maharajas' Express train runs above $12,000. Scenic's 2027 India pricing hasn't been released, but its comparable Mekong cruises typically range from $6,000 to $9,000 for 11 to 14 days.

Viking's Brahmaputra pricing is expected later this year. APT, another Australian operator, is already selling its Kolkata-to-Varanasi Ganges itinerary for the 2026-27 season with departures from August 2026 through March 2027.

Booking tip: early-access pricing on inaugural seasons often includes complimentary upgrades or reduced single supplements. If you're considering a multigenerational family trip to India in late 2027, this is the moment to lock in a cabin.

India's rivers have carried civilisation for millennia. Now they're carrying cruise ships — and the diaspora might finally have a reason to see the country from the water."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Luxury River Cruises Are Coming to the Ganges — and the NRI Market Is the Prize",
    "subheadline": "Scenic, Viking, and Uniworld are launching all-inclusive voyages on the Hooghly and Brahmaputra from 2027. For NRIs tired of cobbling together India trips, a single booking now covers it all.",
    "slug": make_slug("ganges-hooghly-river-cruise-scenic-viking-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "International river cruise operators are targeting NRI spending power — offering a new way for the diaspora to show visiting family India's cultural depth without the logistics headache.",
    "tags": ["travel", "cruise", "Ganges", "Hooghly", "river cruise", "NRI", "luxury", "Scenic", "Viking", "Uniworld"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel Weekly — Scenic Group Hooghly River cruises launching 2027", "url": "https://www.travelweekly.com"},
        {"name": "Aspire Travel Club — Scenic Group unveils first India river cruise programme", "url": "https://aspiretravelclub.co.uk"},
        {"name": "Travel And Tour World — Global Cruise Tourism Enters a New Era", "url": "https://travelandtourworld.com"},
        {"name": "Uniworld River Cruises — India's Golden Triangle & the Sacred Ganges", "url": "https://www.uniworld.com"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b5/HooghlyRiverOverBally_gobeirne.jpg",
    "image_caption": "The Hooghly River flowing past Bally, West Bengal — the waterway where Scenic Group will launch luxury cruises in 2027",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ──────────────────────────────────────────────
# Insert all articles
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
