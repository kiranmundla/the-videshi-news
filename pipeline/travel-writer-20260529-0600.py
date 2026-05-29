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
        "headline": "Canada Is Giving Away Free National Park Entry All Summer — and NRIs Should Pack the Minivan",
        "subheadline": "The Canada Strong Pass returns June 19 with free admission to 200-plus parks, 25 percent off camping, and free VIA Rail for kids. American residents — including NRIs — are eligible.",
        "slug": make_slug("canada-strong-pass-free-parks-nri-families-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "US-based NRI families near border cities like Detroit, Buffalo, and Seattle can drive across for world-class outdoor vacations at zero entry cost — while US park fees keep climbing to $35-plus per vehicle.",
        "tags": ["travel", "canada", "national parks", "family travel", "summer 2026", "budget travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Government of Canada", "url": "https://www.canada.ca/en/canadian-heritage/news/2026/05/canada-strong-pass-is-back-this-summer-to-help-canadians-save-on-vacation-plans.html"},
            {"name": "TravelPulse Canada", "url": "https://www.travelpulse.ca/news/destinations/canada-strong-pass-returns-for-summer-2026"},
            {"name": "Parade", "url": "https://parade.com/travel/best-canadian-national-parks-free-summer"},
            {"name": "The Weather Network", "url": "https://www.theweathernetwork.com/en/news/travel/destinations/the-canada-strong-pass-is-back-for-summer-2026"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/18292197/pexels-photo-18292197.jpeg",
        "image_caption": "Moraine Lake in Banff National Park — one of over 200 Parks Canada sites offering free entry this summer under the Canada Strong Pass.",
        "body": """Every June, the same question ricochets through NRI family WhatsApp groups: where do we go this summer that won't cost a fortune? This year, the answer is north.

## The Canada Strong Pass, Explained

Canada's federal government announced on May 21 that the Canada Strong Pass will return for a second summer season, running from **June 19 through September 7, 2026**. The programme — launched in 2025 as a post-pandemic tourism stimulus — offers something remarkable: **free admission to every Parks Canada site in the country**. That's more than 200 national parks, national historic sites, and national marine conservation areas, from Banff's turquoise lakes to the Bay of Fundy's tidal bores.

The fine print is almost nonexistent. There is no physical or virtual pass to obtain. No registration. No app to download. You simply show up.

And here's the detail that matters most: the programme is open to **all visitors, whether Canadian or international**. If you hold a US green card or any valid status, you're eligible.

## What's Included

The pass extends well beyond park gates:

- **Parks Canada**: Free entry to all sites, plus a 25 percent rebate on camping fees
- **National museums**: Free admission for children 17 and under; 50 percent off for young adults aged 18 to 24
- **Provincial and territorial museums**: Same age-based discounts at participating institutions
- **VIA Rail**: Free train travel for children 17 and under when accompanied by an adult; 25 percent off for young adults 18 to 24

For a family of four with two kids under 17, a week-long Canadian road trip could cost little more than gas and groceries. Last summer's programme drove a 13 percent increase in visits to Parks Canada sites and a 6.5 percent bump in VIA Rail ridership.

## Why This Hits Different for NRI Families

The timing is strategic for the Indian American diaspora. US national park fees have been climbing steadily — a standard vehicle pass at Yellowstone, Grand Canyon, or Yosemite now runs $35 to $40, and popular campgrounds book out months in advance. Meanwhile, the classic NRI summer vacation formula of Disney-plus-cruise has gotten brutally expensive, with a family of four now routinely spending $6,000 to $8,000 on a theme park week.

Canada offers a compelling alternative, especially for families in border-adjacent metros. **Detroit to Point Pelee National Park**: three hours. **Buffalo to Niagara Falls and the Niagara Escarpment**: under two hours. **Seattle to Pacific Rim National Park Reserve on Vancouver Island**: a day's journey that includes a spectacular ferry ride.

And for families willing to fly, **Banff and Jasper** — regularly ranked among the world's most beautiful mountain parks — are accessible via Calgary, with direct flights from most major US hubs.

## The Logistics NRIs Should Know

A few practical notes for US-based Indian families planning a cross-border park trip:

**Border crossing**: US citizens and green card holders can enter Canada with a passport (or a NEXUS card for expedited entry). H-1B and L-1 visa holders may need to check whether their visa permits re-entry from Canada — most do, but confirm before you drive.

**Camping reservations**: Free entry doesn't mean free camping, though the 25 percent discount helps. Parks Canada campgrounds — especially at Banff, Jasper, and Pacific Rim — fill fast. Book now at reservation.pc.gc.ca.

**Cell coverage**: Many Canadian parks have limited or no mobile coverage. Download offline maps and let family know your itinerary.

**Currency**: The Canadian dollar has been trading around 0.72 to the US dollar in 2026, making restaurants, fuel, and supplies meaningfully cheaper for American visitors.

## The Verdict

The Canada Strong Pass is the best-kept travel secret of summer 2026 for NRI families in the US. World-class wilderness, no entry fees, favourable exchange rate, and — for border-state families — a drive that's shorter than the one to the nearest Indian grocery store in some metros.

Banff's turquoise water doesn't care what passport you carry. This summer, it's free."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Opened Two New Mega-Airports — and the NRI Landing Experience Is About to Change",
        "subheadline": "Noida International Airport launches commercial flights June 15 while Navi Mumbai is already operational. For the first time, both Delhi-NCR and Mumbai have dual-airport systems.",
        "slug": make_slug("noida-navi-mumbai-airports-nri-dual-airport"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying home to Delhi and Mumbai — the two busiest arrival corridors for the diaspora — now have alternatives to the overcrowded IGI and CSIA terminals that have defined the India arrival experience for decades.",
        "tags": ["travel", "airports", "india", "noida", "navi mumbai", "infrastructure", "airlines"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/1zzvmdz7ozbp/"},
            {"name": "Pulse of Noida", "url": "https://pulseofnoida.com/noida-international-airport-to-begin-commercial-flights-from-june-15"},
            {"name": "CurlyTales", "url": "https://curlytales.com/delhi-to-noida-international-airport-in-just-21-mins/"},
            {"name": "Live From A Lounge", "url": "https://livefromalounge.com/indigo-to-become-the-first-airline-to-launch-flights-from-navi-mumbai-international-airport/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/3840px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "Navi Mumbai International Airport, now operational as Mumbai's second major aviation gateway.",
        "body": """For decades, the NRI arrival experience in India has been defined by two airports: Delhi's Indira Gandhi International and Mumbai's Chhatrapati Shivaji Maharaj International. The 2 AM landing, the serpentine immigration queue, the luggage carousel that tests your spiritual patience, the taxi ride through predawn traffic. It's a shared ritual, and most of the diaspora has war stories.

That's starting to change. India now has operational dual-airport systems in both its largest metros, and NRIs planning summer trips home should take note.

## Noida International Airport: June 15 Launch

Noida International Airport — inaugurated by Prime Minister Modi on March 28 — will begin commercial passenger operations on **June 15, 2026**. IndiGo is the launch carrier, with routes to Amritsar, Bengaluru, Hyderabad, Lucknow, and more destinations rolling out in phases through July.

Akasa Air follows one day later on June 16, launching daily nonstop flights to Bengaluru and Navi Mumbai.

The airport, located at Jewar in Uttar Pradesh, is the second to serve the Delhi-NCR region. Phase I capacity stands at 12 million passengers annually — roughly a quarter of what IGI handles — with plans to scale significantly. A proposed high-speed rail corridor could eventually connect Delhi to the airport in just 21 minutes.

For NRIs, the immediate relevance is geographic. If your family is in Greater Noida, Agra, Aligarh, or western UP, Noida International Airport eliminates the need to cross Delhi entirely. That alone could save two to three hours of transfer time on either end of a long-haul flight.

## Navi Mumbai: Already Up and Running

On the western coast, Navi Mumbai International Airport has quietly begun operations with IndiGo as its first carrier. The airline's inaugural Bengaluru-to-NMIA flight touched down to a water-cannon salute and a crowd of selfie-taking families — a fitting welcome for an airport the city had been waiting on for over a decade.

IndiGo started with 18 daily departures to 15 cities, including Delhi, Bengaluru, Hyderabad, Ahmedabad, Lucknow, Goa, Jaipur, and Kochi. The scale-up is aggressive: 100-plus daily departures by March 2026 timelines, reaching 140 daily (including 30 international flights) by November 2026. Air India and Akasa Air are also expected to begin NMIA operations.

Developed by Adani Airport Holdings in partnership with CIDCO, NMIA's Phase I can handle 20 million passengers annually. The long-term plan envisions 90 million — which would make it one of the busiest airports in South Asia.

## What This Means for the Diaspora

The practical impact for NRIs is substantial. Consider the two most common arrival scenarios:

**Delhi corridor**: An NRI flying into IGI who needs to reach family in Noida, Greater Noida, or western UP currently faces a 90-minute-to-two-hour cab ride through Delhi's traffic. Once domestic connections start at Noida Airport (and eventually international routes), that transit collapses to minutes.

**Mumbai corridor**: NRIs headed to Navi Mumbai, Pune, the Konkan coast, or south Mumbai suburbs currently land at CSIA in Andheri and face a grinding cross-city transfer. NMIA sits on the other side of the harbour, cutting that journey dramatically. For the large Maharashtrian diaspora in the US — and the substantial population headed to Pune's IT corridor — this is transformative.

## The Caveats

Neither airport is a full replacement yet. International long-haul flights remain concentrated at IGI and CSIA for now. Noida's connectivity will improve as the metro link and high-speed rail plans materialise. And NMIA's road access, while better than CSIA for eastern suburbs, still depends on the trans-harbour link completing its ramp-up.

But the direction is clear. India's two busiest aviation corridors now have relief valves, and the NRI experience of landing in India — that decades-old ritual of exhaustion and endurance — is finally getting an upgrade.

## Planning Ahead

NRIs booking summer 2026 India trips should monitor domestic routing options. If your final destination is in Noida Airport's catchment area, booking a domestic connecting flight from a southern hub like Bengaluru or Hyderabad through Noida could shave hours off your total door-to-door journey. The same logic applies to NMIA for Pune-bound or Konkan-bound travellers.

Check IndiGo and Akasa Air for the latest route maps. The airports are new, but the convenience is already real."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Killed Visa-Free Entry for Indian Passport Holders — Here's What NRIs Need to Know",
        "subheadline": "Bangkok's cabinet ended the 60-day visa exemption for 93 countries including India. Indian passport holders now face a 15-day visa-on-arrival limit. US citizens are unaffected.",
        "slug": make_slug("thailand-ends-visa-free-indian-passport-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs on Indian passports who routinely added a Bangkok layover or Thai beach week to their India trips now face tighter restrictions, while US-citizen NRIs retain 30-day visa-free access — creating a split experience within the same family.",
        "tags": ["travel", "visa", "thailand", "indian passport", "nri", "visa policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Mint / Livemint", "url": "https://www.livemint.com/news/trends/thailand-visa-news-tourist-visa-free-stay-for-indians-ends-11779550734027.html"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/thailand-south-korea-joins-china-india-indonesia-japan-visa-policy-2026/"},
            {"name": "Government of Thailand Department of Consular Affairs", "url": "https://www.mfa.go.th/en"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19041654/pexels-photo-19041654.jpeg",
        "image_caption": "Bangkok's Grand Palace — still a top destination for Indian travellers, but the visa rules just got tighter.",
        "body": """Thailand has been the default easy getaway for Indian travellers for the past two years. Cheap flights from every Indian metro, no visa paperwork, and 60 days to soak up islands and street food. That era just ended.

## What Happened

Thailand's Cabinet approved a sweeping overhaul of its visa framework on May 19, 2026. The centrepiece: the elimination of the **60-day visa-free entry scheme** (known as Phor 60) that had been available to travellers from 93 countries, including India.

The 60-day programme had been introduced in July 2024 as a post-pandemic tourism booster, and it worked — Indian arrivals surged, with Bangkok, Phuket, and Pattaya becoming almost as common as Goa on NRI vacation itineraries. But Thai authorities grew concerned about what came with the tourist boom: illegal employment, nominee businesses, and transnational crime.

The new policy follows a principle the government is calling **"one country, one Thai visa exemption privilege"** — a streamlined system that assigns each nationality exactly one entry category.

## Where India Lands

Under the revised framework, India has been moved from the visa-free tier to the **Visa on Arrival (VOA) category**. Here's what that means in practice:

- **No more visa-free entry**. Indian passport holders cannot simply show up at Suvarnabhumi and walk through immigration.
- **Visa on Arrival** is available at designated checkpoints, but the permitted stay drops to **15 days** — down from 60 under the old scheme.
- **Required documentation**: Return ticket, proof of accommodation, and sufficient funds (typically 10,000 baht or about $280 per person).

The 15-day limit makes Thailand viable for a short holiday but effectively kills the extended stays that had become popular — the month-long digital nomad stints, the two-week yoga retreats, the leisurely island-hopping circuits.

The VOA list itself has been dramatically cut from 31 countries to just four, though India is confirmed among them.

## The NRI Split

Here's where it gets complicated for diaspora families. The visa change applies to **passport holders**, not residents.

- **US citizens** (regardless of Indian origin) retain **30-day visa-free access** under Thailand's Phor 30 programme, which continues for 54 countries including the United States, Canada, the UK, Australia, and most of Europe.
- **Indian passport holders** — including H-1B workers, L-1 transferees, F-1 students, and green card applicants who haven't naturalised — now need a VOA and get only 15 days.

This creates an awkward split in mixed-passport NRI families. A naturalised US citizen parent can waltz through Thai immigration, while their Indian-passport-holding spouse or college-age child on an F-1 needs to queue at the VOA counter with documentation.

For the substantial population of NRIs who maintain Indian passports while living in the US on long-term visas, this is a meaningful downgrade. Thailand had been one of the easiest international trips to plan precisely because no embassy visit or advance application was required.

## Timing and Transition

The new rules take effect **15 days after publication in the Royal Gazette**, which hadn't happened as of this writing. Travellers already in Thailand under the existing scheme will be allowed to stay until their approved period expires.

If you have a Thailand trip booked for June or July on an Indian passport, check the gazette publication date. You may still enter under the old 60-day rule if you arrive before the cutoff — but don't count on it. Thailand's Tourism Minister Surasak Phancharoenworakul has signalled that the government wants to move quickly.

## Alternatives for NRIs

If your summer Asia plans just got complicated, a few options:

- **Apply for a Thai tourist visa** in advance through the Thai consulate. The standard tourist visa (TR) allows a 60-day stay with possible extension, but requires advance paperwork.
- **Consider Malaysia or Indonesia** — both still offer relatively generous visa-free entry for Indian passport holders (Malaysia: 30 days; Indonesia: 30 days visa-free).
- **Time the trip under VOA**: 15 days is still enough for Bangkok plus one island. Just plan tighter.

## The Bigger Picture

Thailand's move reflects a global tightening. The EU's new biometric border system, Japan's mandatory visa appointment system, and now Thailand's rollback — the post-pandemic golden age of easy travel for Indian passport holders is quietly ending. For NRIs who've been putting off naturalisation partly because "my Indian passport works fine," this is another data point in the other direction.

The beaches haven't moved. But the paperwork just got heavier."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
