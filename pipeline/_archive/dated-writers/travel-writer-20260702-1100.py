#!/usr/bin/env python3
"""Videshi Travel Writer — July 2, 2026 11:00 AM run"""
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
    # ─── Article 1: Vande Bharat Sleeper Bengaluru-Mumbai ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Second Vande Bharat Sleeper Has Reached Bengaluru — and Mumbai Is 13 Hours Away",
        "subheadline": "The overnight train that could reshape how NRIs travel between India's two biggest tech cities has entered final testing at SMVT Bengaluru station.",
        "slug": make_slug("vande-bharat-sleeper-bengaluru-mumbai-final-testing-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting family split between Bengaluru and Mumbai finally get a premium overnight option — no dawn flights, no 18-hour Udyan Express ordeals.",
        "tags": ["travel", "railways", "vande-bharat", "bengaluru", "mumbai", "infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CurlyTales", "url": "https://curlytales.com/india/trending/bengaluru-mumbai-vande-bharat-sleeper-reaches-final-testing-stage-heres-all-you-need-to-know/"},
            {"name": "The Indian Express", "url": "https://indianexpress.com/"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/bengaluru-mumbai-vande-bharat-sleeper-planned/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/trains/new-vande-bharat-sleeper-train-to-connect-bengaluru-and-mumbai-soon/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Vande_Bharat_Sleeper_Express.jpg/1280px-Vande_Bharat_Sleeper_Express.jpg",
        "image_caption": "A Vande Bharat Sleeper Express trainset at a station platform in India",
        "image_attribution": "Wikimedia Commons",
        "body": """The orange-and-grey rake sitting at SMVT Bengaluru station this week is not there for display. It is the Bengaluru–Mumbai Vande Bharat Sleeper, India's second sleeper-class semi-high-speed train, and it is undergoing the final round of operational checks before its commercial launch.

Railway officials parked the 16-coach train at Bengaluru for testing because the station offers convenient access to the route's operational corridor. Once the trials wrap — no firm date yet, but the Railway Ministry had targeted late July — it will begin overnight service between KSR Bengaluru and Mumbai's Chhatrapati Shivaji Maharaj Terminus (CSMT).

## What the numbers look like

The train accommodates 823 passengers across three classes: 611 berths in AC 3-tier, 188 in AC 2-tier and 24 in First AC. The coaches are built by Chennai's Integral Coach Factory (ICF), the same facility that produced the first Vande Bharat Sleeper, which has been running between Howrah and Kamakhya in the Northeast since January.

The route threads through Karnataka's Hubballi-Dharwad belt and Belagavi before crossing into Maharashtra via Pune and Solapur. Expected travel time: roughly 13 hours, slicing about six hours off the 19-hour Udyan Express, the current workhorse on this corridor.

Each coach features automatic doors, CCTV, bio-vacuum toilets, sensor-based taps, individual reading lights and power outlets — upgrades that bring the overnight rail experience meaningfully closer to what Indians encounter on premium trains abroad.

## Why NRIs should care

Bengaluru and Mumbai are India's two largest professional cities, and the NRI connection between them runs deep. Thousands of diaspora families are split across the two — parents in one, siblings or in-laws in the other. Until now, the choices were an early-morning flight (expensive and inconvenient during peak season) or the grinding Udyan Express overnight.

A 13-hour sleeper that departs in the evening and arrives by morning changes the arithmetic. It is cheaper than a flight, more comfortable than any existing train on the route, and eliminates the airport-transfer time that eats into a short India visit. For NRIs routing a family trip through both cities, it is a genuine alternative.

## The bigger picture

Indian Railways plans to roll out 12 Vande Bharat Sleeper services by the end of 2026, covering major overnight corridors including Delhi–Chennai, Delhi–Kolkata and Mumbai–Delhi. The 24-coach version — capable of replacing the iconic Rajdhani Express on longer routes — is expected to enter prototype testing by year-end, with a potential top speed of 160 km/h.

The Bengaluru–Mumbai service, once operational, will also improve access to smaller cities along the route. Hubballi-Dharwad, Belagavi and Solapur have large Kannada and Marathi diaspora populations in the US and Gulf, and a modern train passing through at reasonable hours opens up those towns to visitors who might otherwise skip them.

For now, the train sits in Bengaluru, waiting for the green light. But the tracks are laid and the coaches are ready. The overnight trip between India's two tech capitals is about to get a long-overdue upgrade."""
    },

    # ─── Article 2: Marriott's 10,000th Property in Ranthambore ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Marriott Chose India for Its 10,000th Hotel — and It's a Tiger Safari Resort in Rajasthan",
        "subheadline": "The JW Marriott Ranthambore Resort & Spa, with 127 rooms near one of India's most famous national parks, marks a global milestone and a bet on Indian luxury tourism.",
        "slug": make_slug("marriott-10000th-hotel-ranthambore-rajasthan-nri-luxury"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs who plan India trips around wildlife and heritage, Ranthambore just got a Marriott Bonvoy property — meaning points, upgrades and a familiar loyalty ecosystem in the middle of tiger country.",
        "tags": ["travel", "hotels", "luxury", "rajasthan", "ranthambore", "marriott"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "TravelPulse Canada", "url": "https://www.travelpulse.ca/news/hotels-and-resorts/marriott-unveils-10000th-property-with-opening-of-jw-marriott-in-india"},
            {"name": "HOTELS Magazine", "url": "https://www.hotelsmag.com/news/marriott-just-opened-its-10000th-hotel-here/"},
            {"name": "Hotelier Middle East", "url": "https://www.hoteliermiddleeast.com/from-root-beer-to-10-000-hotels-marriott-marks-global-milestone"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ranthambore_National_Park.JPG/1280px-Ranthambore_National_Park.JPG",
        "image_caption": "Ranthambore National Park in Rajasthan, home to India's most photographed Bengal tigers",
        "image_attribution": "Wikimedia Commons",
        "body": """When Marriott International wanted a stage for its 10,000th property — a number that took 99 years to reach — it did not pick Manhattan, Dubai or Tokyo. It picked Ranthambore, a small town in Rajasthan where the main attraction has four legs and stripes.

The JW Marriott Ranthambore Resort & Spa opened recently near the boundary of Ranthambore National Park, one of India's premier tiger reserves. It features 127 accommodations spanning private villas, suites and guestrooms, each designed to face the scrubby Aravalli landscape. Dining options lean into the regional: modern Indian cuisine, Rajasthani specialties and botanical cocktails made from locally sourced ingredients.

"Marriott was founded 99 years ago as a nine-seat root beer stand, and as of today, has grown into a global portfolio of 10,000 properties spanning 146 countries and territories," said CEO Anthony Capuano at the opening, joined by chairman David Marriott and Asia Pacific president Rajeev Menon.

## Why Ranthambore, why now

The choice is not accidental. India's luxury hospitality market has been on a tear. Domestic travellers are spending more on premium stays, international tourist arrivals are climbing back toward pre-pandemic peaks, and Rajasthan — with its forts, palaces and wildlife — consistently ranks among India's top-visited states.

Ranthambore specifically benefits from its proximity to Delhi (about five hours by road, or a short hop to Jaipur followed by a two-hour drive) and its reputation as the most accessible tiger safari in the country. The park's tigers are famously unafraid of vehicles, making it easier to spot them here than in more remote reserves like Corbett or Bandhavgarh.

The resort sits within the broader JW Marriott portfolio, which now includes more than 130 properties globally. Marriott's luxury segment — seven brands, nearly 700 properties across 74 countries — has been growing faster than its economy tiers, a bet that travellers are willing to pay more for curated experiences.

## What this means for NRIs

For the Indian American family planning a heritage trip to Rajasthan, this is practical news. Ranthambore has long had boutique lodges and heritage properties, but no major international chain with a global loyalty programme. A JW Marriott in the mix means Bonvoy points earned from business travel in the US can now cover a tiger safari weekend — and the reverse. Elite members get the familiar suite of upgrades, late checkouts and lounge access.

It also signals a broader shift. Global hotel brands are no longer treating India as an afterthought. Hilton opened six properties in India this quarter alone, including its first lifestyle hotel in Bengaluru and a Lucknow property aimed at the MICE market. IHG has a Crowne Plaza coming to Pushkar, the Rajasthani town famous for its annual camel fair and Brahma temple.

## The luxury arms race continues

India added more five-star hotel rooms in 2025 than in any year since 2019, and 2026 is tracking even higher. The demand is being driven partly by wealthy Indian families (some of whom are booking out entire Maldives resorts, as recent reports have noted), partly by the rising NRI travel market, and partly by India's growing status as a wedding, MICE and incentive-travel destination.

For NRIs, the net effect is simple: the next India trip will have better hotels, more loyalty options and fewer compromises than any visit in the last decade. Marriott just made that point with 10,000 hotels' worth of emphasis."""
    },

    # ─── Article 3: Malaysia Visa-Free for Indians ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Malaysia's Visa-Free Window for Indians Expires in Six Months — Here's Why NRIs Should Use It",
        "subheadline": "Indian passport holders can enter Malaysia without a visa until December 31, 2026. With monsoon fares dropping and Visit Malaysia 2026 in full swing, the timing has never been better.",
        "slug": make_slug("malaysia-visa-free-indians-expires-december-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs holding Indian passports can skip the visa hassle entirely for a 30-day Malaysian holiday — a rare perk that makes Malaysia one of the easiest international getaways from India right now.",
        "tags": ["travel", "visa", "malaysia", "southeast-asia", "visa-free", "monsoon"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/malaysia-visa-exemption-implemented-for-chinese-and-indian-nationals.html"},
            {"name": "Business Traveller", "url": "https://www.businesstraveller.com/business-travel/2025/03/13/malaysia-unveils-visit-malaysia-year-2026-campaign-extends-visa-free-entry-for-indians/"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/visa-free/malaysia-visa-free-entry-for-indians-through-2026/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/henley-passport-index-2026-indian-passport-rank/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Kuala_Lumpur_Malaysia_Petronas-Twin-Towers-01.jpg/1280px-Kuala_Lumpur_Malaysia_Petronas-Twin-Towers-01.jpg",
        "image_caption": "The Petronas Twin Towers dominate the Kuala Lumpur skyline in Malaysia",
        "image_attribution": "Wikimedia Commons",
        "body": """Since December 2023, Indian passport holders have been able to walk into Malaysia without a visa. No embassy appointments, no biometrics queues, no weeks of waiting. Just a valid passport, a return ticket and up to 30 days of visa-free entry for tourism, business meetings, conferences or transit.

That window closes on December 31, 2026. Six months from now, unless Kuala Lumpur extends the programme again, Indians will be back to applying for e-visas. For NRIs still holding Indian passports — and that includes a significant share of the diaspora on H-1B, L-1 or green card tracks in the US — this is a perk worth using while it lasts.

## The numbers behind the policy

Malaysia's gamble has paid off handsomely. In 2024, 1.13 million Indian visitors entered the country, a 47 per cent jump from 2019 and a 72 per cent increase over 2023. India is now Malaysia's second-largest inbound market after China.

The Malaysian government is doubling down with its Visit Malaysia Year 2026 campaign, launched under the tagline "Surreal Experiences." The target: between 43 and 47 million international visitors this year, backed by RM500 million (roughly $115 million) in promotional spending. Tourism Minister Datuk Seri Tiong King Sing has not been subtle about the ambition.

The visa exemption is the centrepiece. Without it, Indian arrivals would likely fall by half, based on what happened during the pre-exemption years.

## Why it makes sense for NRIs right now

Timing matters. July through September is monsoon season across much of India, which means two things for NRIs: flights to India get cheaper (less demand), and flights from Indian cities to Kuala Lumpur, Langkawi or Penang drop correspondingly.

A return ticket from Delhi or Mumbai to KL currently runs between ₹12,000 and ₹18,000 on IndiGo, AirAsia or Malaysia Airlines — roughly the cost of a domestic flight within India. The flight time is under five hours from most major Indian cities.

What you get for that fare is considerable. Malaysia offers the best value-for-money in Southeast Asia for Indian travellers: the food is familiar (Indian-Malaysian cuisine is its own category), the infrastructure is first-world, the beaches in Langkawi and the Perhentian Islands rival anything in Thailand, and Kuala Lumpur's shopping and street food scene needs no introduction to the Indian palate.

For families, the Genting Highlands theme park complex, Penang's George Town (a UNESCO World Heritage Site) and the Batu Caves provide a mix of entertainment, culture and religion that is hard to match elsewhere at this price point.

## The fine print

The visa-free entry is not unlimited. You get 30 days per visit, and the Social Visit Pass you receive on arrival cannot be extended — you must leave and re-enter for a fresh stamp. The exemption covers tourism, business, social visits and transit, but not employment or study.

You will need to fill out the Malaysia Digital Arrival Card (MDAC) before flying. It is a straightforward online form, but skipping it can cause delays at immigration. Malaysian border officers also retain the right to refuse entry (a "Not To Land" decision) if they are not satisfied with your travel documents or stated purpose.

## The bigger picture

Malaysia's visa-free experiment is part of a broader trend in Southeast Asia. Thailand offered Indian passport holders visa-free entry for several months before recently switching to a 15-day visa-on-arrival. Indonesia still requires a visa-on-arrival fee. Singapore requires a visa for Indian nationals (though it is processing times have improved).

In that landscape, Malaysia stands out. A 30-day visa-free stay, direct flights under five hours, a significant Tamil and Indian Muslim community (about 7 per cent of Malaysia's population is of Indian descent), and a tourism infrastructure that is genuinely world-class — it is hard to find a better short-haul international option for Indian passport holders right now.

The clock is ticking on December 31. If you have been meaning to go, the monsoon season fare dip is your cue."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
