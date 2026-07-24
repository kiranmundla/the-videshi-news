#!/usr/bin/env python3
"""Travel writer — 2026-06-06 22:00 UTC run."""
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

# ── Article 1 ────────────────────────────────────────────────────────────────

art1_body = """The Pushpabanta Palace sits on a quiet hillock in Agartala's Kunjaban neighbourhood, a white-walled structure built in 1917 by Maharaja Birendra Kishore Manikya Debbarman Bahadur as a royal retreat for guests and visiting dignitaries. For over a century, it has been one of Tripura's most recognisable landmarks — and one of its most underused.

That changed on June 5, when Union Home Minister Amit Shah laid the foundation stone for the Taj Pushpabanta Palace Heritage Hotel, a joint venture between the Tripura state government and Indian Hotels Company Limited (IHCL), the Tata Group subsidiary that operates the Taj brand. The ceremony, attended by Chief Minister Manik Saha and IHCL CEO Puneet Chhatwal, formalised a lease agreement signed in May 2025 and marked the beginning of what will be one of Northeast India's most significant hospitality projects.

## What's Being Built

The property will feature approximately 100 rooms — 89 standard guest rooms, six executive rooms, five executive suites, and a presidential villa — alongside a banquet block, ballroom, meeting halls, a restaurant, and a swimming pool. The palace itself will house select public areas and royal suites inspired by the legacy of the Manikya dynasty, while new construction will complement the original architecture. IHCL has committed to preserving the building's historic character while meeting modern five-star standards.

The project is expected to take three years to complete. When it opens, it will be the first Taj-branded property in Tripura and one of the most prominent luxury hotels anywhere in India's seven northeastern states.

## Why Northeast India Matters Now

IHCL has been quietly building a Northeast portfolio for years. Under its Accelerate 2030 roadmap, the company aims for 30 hotels across the region by the end of the decade, backed by a planned investment of ₹2,500 crore. The Pushpabanta project extends a footprint that has already reached 14 properties in the Northeast, including a Vivanta in Guwahati and a Taj in Gangtok.

The push reflects broader infrastructure improvements. New airports, expanded rail connectivity, and improved roads have begun to shrink the perceived remoteness that kept tourist numbers low. The Indian government's Act East Policy and Look North-East initiative have channelled significant funding into the region, with tourism positioned as a key economic driver.

India's spiritual tourism economy alone is projected to reach $135 billion by 2034, and the Northeast — home to monasteries, indigenous tribal cultures, and some of the subcontinent's most dramatic landscapes — stands to capture a growing share.

## The NRI Angle

For the estimated 400,000-plus Americans of Northeastern Indian origin, including significant Tripuri, Manipuri, and Assamese communities concentrated in cities like Houston, the Bay Area, and the New York metro, the hospitality gap has long been a practical barrier to visiting home. Decent accommodation in Agartala has been scarce, and family trips often meant staying with relatives or settling for bare-bones guesthouses.

A Taj property changes the calculation. It gives NRIs a base for exploring a region most Indian Americans have never visited — the living root bridges of Meghalaya, Kaziranga's one-horned rhinos, Tawang's Buddhist monastery, and now, a restored royal palace with room service.

It also signals something broader: that the Tata Group — India's most trusted conglomerate — sees the Northeast as commercially viable, not just politically symbolic. That credibility matters when families are deciding whether to add Agartala or Shillong to a trip that might otherwise stop at Delhi and Jaipur.

## What Comes Next

The project still faces the realities of building luxury hospitality infrastructure in a region with limited contractor capacity, monsoon-heavy construction windows, and the logistical challenges of remoteness. IHCL's track record with heritage conversions — the Taj Lake Palace in Udaipur, the Rambagh Palace in Jaipur — suggests it knows how to navigate this, but timelines in the Northeast tend to stretch.

For now, the foundation stone is in the ground, and the blueprint calls for a property that does something rare: take a piece of Tripura's royal past and make it useful again, without turning it into a museum exhibit. The first guests are expected by 2029."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "A 1917 Royal Palace in Tripura Is Becoming a Taj Hotel — and Northeast India Just Got Its Most Ambitious Luxury Bet",
    "subheadline": "IHCL breaks ground on a 100-room heritage property inside Agartala's Pushpabanta Palace, doubling down on a region most NRIs have never considered visiting.",
    "slug": make_slug("taj-pushpabanta-palace-tripura-heritage-hotel-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The 400K+ Americans of Northeastern Indian origin finally get a luxury base for visiting home — a Taj-branded heritage hotel that could put Tripura on the NRI travel map alongside Rajasthan and Kerala.",
    "tags": ["travel", "hotels", "northeast-india", "taj", "ihcl", "tripura", "heritage"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Tripura Star News", "url": "https://tripurastarnews.com"},
        {"name": "LatestLY / ANI", "url": "https://www.latestly.com"},
        {"name": "Tripura Net", "url": "https://www.tripuranet.com"},
        {"name": "IHCL Official", "url": "https://www.ihcltata.com"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Pushpabanta_Palace_at_Agartala%2C_Tripura.jpg/3840px-Pushpabanta_Palace_at_Agartala%2C_Tripura.jpg",
    "image_caption": "Pushpabanta Palace in Agartala, Tripura — the 1917 royal retreat being converted into a Taj heritage hotel",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
    "is_editorial": False,
}

# ── Article 2 ────────────────────────────────────────────────────────────────

art2_body = """If you last visited India five years ago and booked a hotel through a family recommendation or a quick search on MakeMyTrip, your next trip will look nothing like that one. India's hospitality industry is in the middle of its strongest run in at least a decade, and the numbers tell a story that goes well beyond a post-pandemic bounce.

Occupancy across premium hotels has hit 68 percent — the highest in recent memory, according to industry data compiled by SOH Magazine and corroborated by ICRA's latest sectoral report. Average daily rates have risen 8.6 percent year-on-year to ₹8,624 (roughly $103). Revenue per available room (RevPAR), the metric that matters most to hotel operators, has climbed 10.8 percent to ₹5,522. And the pipeline of branded rooms under construction or in planning has swelled to 144,000 keys, which could push India's total branded inventory toward 360,000 rooms by 2030.

## The Supply-Demand Gap

The headline numbers are impressive, but the structural story underneath them is what makes this cycle different. Demand for hotel rooms, measured as room nights sold, is growing at roughly nine percent annually. Supply is growing at about five to six percent. That gap — expected to persist for at least two to three more years — is what gives hotels pricing power and keeps occupancy elevated even as rates climb.

A fresh Kotak Securities report published June 6 projects a 16 percent compound annual growth rate in EBITDA for India's listed hotel companies over FY2026-28, with occupancy gradually pushing toward 72 percent. ICRA's parallel assessment sees premium hotel margins holding at 34 to 36 percent, well above the 20 to 22 percent range that was normal before the pandemic permanently reset the industry's cost structure.

## What's Driving It

Several forces are converging. Domestic leisure travel has become a mass-market habit, not a luxury. Weddings, which were always big in India, have industrialised: destination weddings in Udaipur, Jaipur, and Goa now routinely fill 300-room properties for three-day stretches. Corporate travel has recovered. And two newer demand segments — spiritual tourism and Tier-2 city leisure — are growing fast enough to matter.

Spiritual tourism alone is projected to become a $135 billion market by 2034. Cities like Ayodhya, Varanasi, and Tirupati are seeing hotel construction booms driven by both government investment and private capital. Summit Hotels launched an entire brand — The Mandir Collection — dedicated to pilgrimage hospitality, with its first property planned for Salasar in Rajasthan.

The hotel industry is also benefiting from infrastructure that didn't exist a decade ago. New airports, expanded highway networks, and the Vande Bharat semi-high-speed train network have made previously difficult-to-reach destinations accessible for weekend trips. That means hotels in Rishikesh, Coorg, and Hampi can now fill midweek, not just on long weekends.

## The Branded Revolution

Perhaps the most significant shift for visiting NRIs is the explosion of branded, quality-controlled options in cities and towns that previously had nothing between a five-star and a roadside lodge. Tata's IHCL alone is targeting 700 hotels by 2030 across its Taj, Vivanta, SeleQtions, and Ginger brands. ITC, Oberoi, Marriott, Hyatt, and Accor are all expanding aggressively. The online accommodation market, valued at close to $9 billion in 2025, is projected to hit $16 billion by 2031.

For NRIs used to the consistency of a Marriott or Hilton in the US, this means something practical: you can now find a clean, well-managed, internationally branded hotel in Bhubaneswar, Indore, Kochi, or Chandigarh — not just in Mumbai and Delhi. Loyalty programmes are starting to work across borders, too. IHCL's Tata Neu integration has pushed its membership from 2.2 million in 2021 to 11 million today, with app revenue growing 46 percent year-on-year.

## What NRIs Should Know

The boom also means prices are rising. If you're planning a December trip — peak season for diaspora travel — expect to pay 15 to 25 percent more than you did in 2023 for equivalent properties. Booking early matters more than it used to. The days of walking into a decent hotel in Jaipur during Christmas week and finding a room are over.

The upside is that what you get for that money has improved dramatically. India's hotel industry is projected to support nearly 64 million jobs by 2035. The service standards, the food and beverage quality, and the wellness offerings at India's better properties now rival Southeast Asian competitors. Your relatives might still insist you stay at their place. But the hotels are finally good enough to make that a harder argument."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Hotels Are Having Their Best Run in a Decade — and Your Next Trip Home Won't Look Like the Last One",
    "subheadline": "Occupancy at record highs, 144,000 branded rooms in the pipeline, and rates climbing fast — the country's hospitality transformation is rewriting what it means to visit home.",
    "slug": make_slug("india-hotel-industry-boom-revpar-nri-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India will encounter a transformed hospitality landscape — branded hotels in Tier-2 cities, higher prices during peak diaspora season, and service standards rivalling Southeast Asia.",
    "tags": ["travel", "hotels", "india", "hospitality", "nri", "tourism"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "SOH Magazine / LinkedIn", "url": "https://www.linkedin.com"},
        {"name": "Kotak Securities via The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "ICRA", "url": "https://www.icra.in"},
        {"name": "DevDiscourse", "url": "https://www.devdiscourse.com"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33803739/pexels-photo-33803739.jpeg",
    "image_caption": "A heritage hotel lobby in Bikaner, Rajasthan — India's branded hospitality pipeline is its largest ever",
    "image_attribution": "Pexels",
    "body": art2_body,
    "is_editorial": False,
}

# ── Article 3 ────────────────────────────────────────────────────────────────

art3_body = """IndiGo launched its Manchester routes with ceremony and ambition. On July 1, 2025, the airline's first-ever European service — a Boeing 787-9 Dreamliner from Mumbai to Manchester — touched down to genuine excitement. A Delhi-Manchester route followed weeks later. For the half-million people of Indian heritage living within Manchester Airport's catchment area, IndiGo's arrival meant something specific: a direct, affordable link home that didn't require a connection through London or a layover in the Gulf.

Thirteen months later, both routes are dead. IndiGo confirmed this week that it will axe all Manchester services by August 31, 2026, returning the leased Dreamliner to Norse Atlantic Airways and effectively abandoning its European footprint. The decision, the airline says, was driven by a toxic combination of factors that have made long-haul economics from India increasingly unworkable.

## What Went Wrong

The proximate cause is the Iran War. The conflict has closed or restricted airspace across western Iran and parts of the Persian Gulf, forcing flights between India and Europe onto longer, fuel-heavier routing over Central Asia or the Arabian Sea. For IndiGo, which leased its 787s precisely because their fuel efficiency made thin-margin long-haul routes viable, the maths no longer work.

"Longer flying times due to airspace constraints combined with dramatically escalating costs compelled us to take the decision to discontinue India-Manchester services," said Abhijit Dasgupta, IndiGo's Senior Vice President for Network Planning. He called the suspension "temporary" and expressed hope to resume "at the earliest viable opportunity." But IndiGo is returning one of its six leased Boeing 787-9s to Norse Atlantic — a move that suggests this isn't a seasonal pause.

The Manchester exit is part of a broader retreat. IndiGo has also suspended routes to Hong Kong, Shanghai, Ho Chi Minh City, Langkawi, Krabi, and Siem Reap through at least September 2026. The airline, which dominates Indian domestic aviation with a 62 percent market share, has found that its low-cost model — built on short-haul A320 turnarounds — doesn't translate cleanly to intercontinental operations where fuel costs, crew scheduling, and competitive dynamics are fundamentally different.

## What It Means for NRIs in the UK

For the UK's 1.5 million-strong Indian diaspora, the practical impact depends on where you live. Londoners still have options: Air India and Virgin Atlantic fly direct from Heathrow, and British Airways codeshares with Air India on some routes. But for the hundreds of thousands of British Indians in Manchester, Birmingham, Leeds, and across northern England, IndiGo's departure means a return to connecting through London or flying via Dubai and Doha — adding hours, cost, and complexity to every trip.

IndiGo's Manchester fares started at £290 one-way, significantly undercutting legacy carriers. That price point made impromptu trips home more feasible — a long weekend for a family wedding, a quick visit to ageing parents. Without it, the northern Indian community is back to the pre-2025 reality of expensive, time-consuming journeys that require more planning and more money.

## The Bigger Picture

IndiGo's retreat underscores a structural problem in India-Europe aviation. The Iran War has compressed the margin on every route that would normally overfly the Persian Gulf. Emirates and Qatar Airways, which use Dubai and Doha as connecting hubs for India-Europe traffic, have also scaled back. Indian carriers like IndiGo and Air India, which were betting on direct routes to bypass the Gulf hubs, now face the same airspace constraints without the deep pockets or fleet flexibility of the Gulf carriers.

Air India, backed by the Tata Group's resources, is better positioned to absorb the higher costs. It has ordered 470 new aircraft and is integrating Vistara's operations into a single full-service carrier. But even Air India hasn't announced plans to serve Manchester — the market may simply be too small for the current cost environment.

For IndiGo, the lesson is expensive but clarifying. The airline's core strength remains domestic and short-haul international — markets where its A320 fleet, low-cost operations, and frequency advantage are unmatched. It now holds 17.6 percent of India's international market share, ahead of the Air India group, and carried 870,000 international passengers in April alone.

But the long-haul dream will wait. And for the British Indian family in Manchester who briefly had a direct, cheap flight to Mumbai, the wait starts again on September 1."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "IndiGo's European Experiment Dies After 13 Months — and the UK's Indian Diaspora Loses Its Cheapest Route Home",
    "subheadline": "The airline will axe Manchester–Mumbai and Manchester–Delhi by August 31, returning leased Boeing 787s as Iran War–driven costs make long-haul economics unworkable.",
    "slug": make_slug("indigo-manchester-uk-routes-axed-nri-diaspora"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The UK's 1.5 million Indian diaspora — especially in northern England — loses its only direct budget connection to India, pushing families back to expensive Gulf hub connections or London departures.",
    "tags": ["travel", "airlines", "indigo", "uk", "manchester", "nri", "iran-war"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Sun", "url": "https://www.thesun.co.uk"},
        {"name": "AviationA2Z", "url": "https://www.aviationa2z.com"},
        {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
        {"name": "Manchester Airport Media Centre", "url": "https://mediacentre.manchesterairport.co.uk"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
    "image_caption": "An IndiGo Airbus A320neo — the airline's long-haul 787 Dreamliner fleet is being downsized after the Manchester exit",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
    "is_editorial": False,
}

# ── Publish ──────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
