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
        "headline": "Two New Airports in Three Weeks — India's Aviation Blitz Is Rewriting the NRI's Homecoming Map",
        "subheadline": "Navi Mumbai's NMIA opened May 22 with IndiGo as launch carrier. Noida's Jewar airport starts commercial flights June 15. Together, they reshape how 6 million NRIs reach India's two biggest metro regions.",
        "slug": make_slug("navi-mumbai-noida-airport-nri-homecoming"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs flying into Mumbai or Delhi, these two airports mean shorter ground transfers, less congestion, and — eventually — more nonstop routes from the US. Navi Mumbai's proximity to Pune and the Konkan coast, and Noida's link to UP's tech corridor, directly serve diaspora families whose hometowns sit outside the old airport catchment areas.",
        "tags": ["travel", "airports", "india", "navi-mumbai", "noida", "infrastructure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/vr6b1qt8am77/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/india/trending/delhi-to-noida-international-airport-in-just-mins-up-plans-high-speed-rail-corridor/"},
            {"name": "Pulse of Noida", "url": "https://pulseofnoida.com/noida-international-airport-commercial-flights-june-15"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/3840px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "body": """India just opened its second airport for Mumbai and is about to open its second for Delhi — within three weeks of each other. For the 6 million–strong NRI population that funnels through these two metro regions on nearly every India trip, the implications are immediate.

## Navi Mumbai Is Live

On May 22, IndiGo's Airbus A320 from Bengaluru touched down at Navi Mumbai International Airport (NMIA) at 8 AM sharp, received a water-cannon salute, and became the first scheduled commercial arrival at the Adani-built greenfield airport. Minutes later, the first departure — to Hyderabad — completed the inaugural cycle. NMIA is now serving 10 domestic destinations: Delhi, Bengaluru, Hyderabad, Ahmedabad, Lucknow, Goa (Mopa), Jaipur, Nagpur, Kochi, and Mangalore.

Phase one runs a single runway and terminal rated for 20 million passengers annually, operating on a 12-hour window from 8 AM to 8 PM. The long-term blueprint envisions two runways and 90 million passengers — rivaling Mumbai's existing Chhatrapati Shivaji Maharaj International Airport (CSMIA), which has been bursting at its seams for years.

For NRIs, the real story is geography. CSMIA sits in Andheri, deep in Mumbai's western sprawl. NMIA sits near Panvel, off the Mumbai-Pune Expressway — a location that cuts ground travel time for anyone headed to Navi Mumbai, Thane, Pune, or the Konkan coast. If your parents retired to Kharghar or your cousin's wedding is in Lonavala, this airport just saved you two hours in a taxi.

## Noida Is Next — June 15

Three weeks after NMIA's debut, Noida International Airport at Jewar launches commercial flights on June 15. IndiGo is again the lead carrier, with initial routes to Amritsar, Bengaluru, Hyderabad, and Lucknow. Akasa Air follows the next day with daily nonstops to Bengaluru and Navi Mumbai.

The Jewar airport is the Delhi-NCR region's second airport, designed to relieve Indira Gandhi International Airport (DEL) — India's busiest, handling over 70 million passengers a year. A high-speed Regional Rapid Transit System (RRTS) is planned to connect central Delhi to Jewar in 21 minutes, though that corridor awaits final clearance from the housing ministry.

For the NRI calculus, Noida matters because of who lives nearby. Greater Noida, Ghaziabad, and the Yamuna Expressway corridor are home to a fast-growing tech and startup ecosystem. NRIs with family in UP — from Lucknow to Agra to Varanasi — will eventually bypass DEL's terminal chaos entirely.

## The Bigger Picture

India is in the middle of its most aggressive airport construction phase ever. Between NMIA, Jewar, the upcoming Bhogapuram airport in Andhra Pradesh, and major terminal expansions at Bengaluru (T2), Chennai, and Kolkata, the country is adding capacity for hundreds of millions of passengers before the decade ends.

For NRIs, more airports mean more competition among airlines, which means more nonstop routes from the US. Air India, IndiGo (now ordering wide-body A350s for long-haul), and foreign carriers will all eye these new hubs. A direct SFO-to-Navi Mumbai flight may sound ambitious today, but Mumbai's slot constraints at CSMIA were the bottleneck — not demand.

The immediate advice: if you're booking India trips for late 2026 or 2027, start checking whether NMIA or Noida serves your final destination better than the legacy airports. Domestic connections from these new hubs are thin right now, but they're adding routes monthly. The NRI homecoming just got a second door in each of India's two biggest cities."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Cut Its Visa-Free Stay for Indians to 15 Days — and It's Part of a Bigger Squeeze",
        "subheadline": "The 60-day visa-free window that made Bangkok the default NRI weekend escape is gone. Indians now get a 15-day visa on arrival, while 93 other countries — including the US — drop to 30 days.",
        "slug": make_slug("thailand-visa-cut-indians-nri-travel"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Thai beaches are the go-to decompression trip for NRIs visiting family in India — a quick Bangkok or Phuket leg tacked onto a two-week Delhi trip. The 60-day exemption made extended stays easy. Now, with Indians capped at 15 days via VOA and the US capped at 30 days, NRIs holding Indian passports face tighter windows than their American-citizen friends on the same group trip.",
        "tags": ["travel", "visa", "thailand", "india", "southeast-asia"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/news/india/thailand-ends-60-day-visa-free-stay-for-indians"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/big-change-for-thailand-travel-60-day-visa-free-stay-scrapped"},
            {"name": "People Magazine", "url": "https://people.com/thailand-visa-rules-change-93-countries-11746879"},
            {"name": "NY Post", "url": "https://nypost.com/2026/05/24/world-news/news-of-the-world-what-you-missed-this-week-internationally/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20889684/pexels-photo-20889684.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Thailand's cabinet has ended the 60-day visa-free entry program for tourists from 93 countries, and the fine print for Indian passport holders is worse than the headline suggests.

## What Actually Changed

Under the policy that's been in place since 2024, Indians could enter Thailand visa-free for up to 60 days — a generous window that turned Bangkok, Phuket, and Chiang Mai into extensions of the India trip for millions. That's over.

Indians will now need a Visa on Arrival (VOA) at Thai immigration checkpoints, with a hard cap of **15 days**. That's not a typo — while citizens of the US, UK, Australia, Japan, and most European countries drop from 60 to 30 days visa-free, Indian nationals are placed in a more restrictive VOA tier. The change takes effect 15 days after publication in Thailand's Royal Gazette, which is expected imminently.

Thailand's Foreign Minister Sihasak Phuangketkeow framed the move bluntly: "60 days may be too long." Officials cited rising security concerns — drug trafficking, illegal nominee businesses, and visa overstays — as the drivers. Tourism Minister Surasak Phancharoenworakul confirmed that the revised periods would vary by nationality.

## The NRI Double Standard

Here's where it stings for the Indian American traveler. An NRI couple — one holding a US passport, the other an Indian passport with OCI — planning a two-week Thailand trip after visiting family in Mumbai now faces two different entry rules. The US passport holder gets 30 days visa-free. The Indian passport holder needs to queue for a VOA and gets 15 days, with documentation requirements at the immigration counter.

For the enormous segment of NRIs who tack a Southeast Asian beach leg onto their India visits, this is a practical headache. Phuket and Krabi were the default "decompress after two weeks with the in-laws" destinations. The VOA process isn't onerous — it requires a passport, return ticket, proof of accommodation, and ฿10,000 in cash equivalents — but the 15-day ceiling kills any extended-stay plans.

## Who Else Got Hit

Thailand isn't acting alone. A broader visa tightening is sweeping through destinations popular with Indian travelers:

- **Maldives** has capped tourist visas on arrival at 30 days with stricter pre-approval for certain demographics
- **Serbia** and **Belarus** have shortened visa-free allowances and now require electronic registration
- **Seychelles** mandates pre-arrival authorization, ending spontaneous island-hopping
- **Azerbaijan, Georgia, Kazakhstan**, and **Uzbekistan** have tightened e-visa enforcement

The pattern is clear: countries that opened their doors wide to Indian tourists during the post-pandemic travel boom are now recalibrating, citing security and overstay concerns.

## What to Do Now

**If you're already booked for Thailand**: Check your travel dates against the Royal Gazette publication. If your trip starts after the 15-day grace period, you'll need to go through the VOA process. Budget an extra hour at Suvarnabhumi or Don Mueang for processing.

**If you're planning a long Thailand stay**: The 15-day VOA is essentially a short-holiday visa. For anything longer, apply for a proper tourist visa through the Thai Embassy or use the e-visa system. Processing takes 5-10 business days.

**If you hold both US and Indian passports**: Enter on your US passport for the 30-day visa-free window. This is obvious but worth stating — many dual-passport NRIs default to their Indian passport when traveling in Asia.

**Consider alternatives**: Vietnam offers Indians an e-visa for 90 days. Sri Lanka's free ETA for Indians remains in place. Malaysia offers 30-day visa-free entry. Cambodia issues 30-day visas on arrival with minimal friction.

The Thailand that NRIs treated as an easy, visa-free extension of their India trip just became a little less easy. Plan accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Leela Is Building a Forest Sanctuary in Coorg — and It Signals Where India's Luxury Hotel Boom Is Heading",
        "subheadline": "A 76-acre, all-villa wellness retreat in the Western Ghats marks The Leela's first 'Sanctuary' concept. For NRIs pricing out their next India trip, Coorg just became a serious alternative to Goa and Rajasthan.",
        "slug": make_slug("leela-coorg-forest-sanctuary-nri-luxury"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs have traditionally booked Goa beach resorts or Rajasthan palaces for their India vacations. Coorg — close to Bengaluru, cool-climate, coffee-country — is an emerging alternative that resonates with the South Indian tech diaspora in particular. A Leela-branded luxury property here gives NRIs a five-star option in a region they've only known through homestays.",
        "tags": ["travel", "hotels", "luxury", "india", "coorg", "wellness"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/stay/the-leelas-latest-address-in-coorg-is-built-around-wellness-and-wilderness"},
            {"name": "Luxebook India", "url": "https://luxebook.in/the-leela-debuts-in-coorg-with-a-forest-sanctuary/"},
            {"name": "Glance Trends", "url": "https://trends.glance.com/trending/leela-resort-coorg-luxury"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Tadiandamol_Valley%2C_Western_Ghats.jpg/3840px-Tadiandamol_Valley%2C_Western_Ghats.jpg",
        "body": """The Leela Palaces, Hotels and Resorts — the brand most NRIs associate with marble lobbies in Mumbai and Bengaluru — is going into the forest. Its next property is a 76-acre, all-villa wellness retreat buried in the coffee plantations of Coorg, Karnataka. It opens later this year, and it represents a bet on where Indian luxury hospitality is heading.

## What's Being Built

The Leela Coorg Forest Sanctuary sits near Madikeri, the hill town that serves as Coorg's administrative capital. The property introduces what The Leela is calling its first "Sanctuary" concept — a deliberate departure from the palace-style grandeur the brand built its reputation on.

The numbers: 71 villas at launch, expanding to 90 in phases. A 27,000-square-foot wellness center anchored by Ayurvedic therapies and The Leela's Aujasya wellness program. Four dining venues. A seven-acre lake. A private helipad for guests who want to skip the five-hour drive from Bengaluru. The flagship accommodation is a four-bedroom presidential villa with a private pool and integrated wellness facilities.

The property is IGBC Platinum-certified — India's green building standard — and sits within the Western Ghats, a UNESCO-recognized biodiversity hotspot. Architecture draws from local Kodava aesthetics while keeping things contemporary. The vibe is "forest first, luxury second," which is new language from a brand that has historically led with chandeliers.

## Why Coorg, Why Now

Coorg has been an open secret among Bengaluru weekenders for years — coffee estates, misty hills, Kodava cuisine, and a pleasantly cool climate even in summer. But its hotel scene has been dominated by boutique homestays and mid-range resorts, with no ultra-luxury anchor.

The Leela's entry changes that calculus. Coorg is now a destination where NRIs can book a world-class property and build a full week's itinerary around it — plantation walks, spice tours, Tibetan monastery visits in Bylakuppe, rafting on the Barapole River. That's the kind of experiential trip that's trending in the diaspora, especially among Bay Area and Seattle families with roots in Karnataka and Kerala.

The timing also tracks with India topping global wellness tourism rankings this year. Ayurveda, yoga retreats, and nature-led recovery stays are no longer niche — they're a $7 billion segment in India, growing at 15% annually. The Leela is betting that high-end NRI travelers will pay premium rates for a curated version of what their grandparents did for free in the village.

## The Leela's Bigger Play

Coorg is one piece of an aggressive pipeline. The Leela now operates 15 properties across 13 cities globally, with upcoming locations in Bandhavgarh, Ranthambore, Srinagar, Jaisalmer, and Sikkim — all nature-forward, experience-driven destinations rather than business-hotel markets. The brand's 40th anniversary, celebrated this year, marks a pivot point: from city palaces to forest sanctuaries.

For the competitive landscape, The Leela is chasing the same NRI dollar that Aman, Six Senses, and Taj's wildlife lodges target. The difference is accessibility: Coorg is a domestic flight plus a half-day drive from any South Indian city, and Bengaluru's Kempegowda International Airport is already the entry point for a massive chunk of the US-India tech corridor.

## The NRI Playbook

**When to go**: October through March for dry weather and cool mornings. Monsoon season (June-September) has its own dramatic beauty but makes outdoor activities unpredictable.

**How to get there**: Fly into Bengaluru (BLR) or Mangaluru (IXE). Drive to Madikeri takes 5-6 hours from Bengaluru, 3 hours from Mangaluru. The helipad at the resort will offer transfers for those who prefer to skip the winding ghats.

**What it'll cost**: The Leela hasn't published rates yet, but comparable luxury villa properties in South India (Evolve Back in Coorg, CGH Earth, Taj Bekal) run ₹30,000-80,000 per night ($350-950). Expect The Leela to price at the top of that range.

**Who it's for**: NRI families seeking a quieter alternative to Goa's beach scene. Wellness-focused travelers. Anyone who's done Rajasthan and wants something greener. South Indian diaspora visiting parents in Bengaluru or Mangaluru who want a luxury side trip that doesn't require another flight.

Coorg's always had the landscape. Now it has the hotel to match."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
