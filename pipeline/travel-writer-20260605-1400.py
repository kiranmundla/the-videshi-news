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

# Verify images before publishing
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        print(f"  ⚠️ Image failed: status={r.status_code}, type={ct}, size={cl}")
        return False
    except Exception as e:
        print(f"  ⚠️ Image verify error: {e}")
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Lufthansa Group Bets Big on India at 100 — New Routes, Premium Cabins, and the A380 Returns to Mumbai",
        "subheadline": "SWISS will launch its first-ever Bengaluru–Zurich nonstop this winter, while Lufthansa deploys its newest cabin product on Delhi and Hyderabad routes. For NRIs connecting through Europe, the options just got significantly better.",
        "slug": make_slug("lufthansa-group-india-expansion-swiss-bengaluru-zurich"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Bengaluru's estimated 200,000 tech professionals with European work ties gain their first direct link to Switzerland. Combined with Germany's new transit visa waiver, NRIs connecting through Frankfurt and Munich face fewer bureaucratic hurdles and shorter journeys across the continent.",
        "tags": ["travel", "airlines", "lufthansa", "swiss", "bengaluru", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/04/lufthansa-boosts-india-connectivity-after-germany-removes-transit-visa-rule/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3319712-germany-eases-transit-for-indian-flyers-boosting-air-links"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Frankfurt_Airport_Lufthansa_Boeing_787-9_Dreamliner_D-ABPC_%28DSC02632%29.jpg/1280px-Frankfurt_Airport_Lufthansa_Boeing_787-9_Dreamliner_D-ABPC_%28DSC02632%29.jpg",
        "image_caption": "A Lufthansa Boeing 787-9 Dreamliner at Frankfurt Airport, the aircraft type getting new Allegris cabins on India routes",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """As Lufthansa Group celebrates its centenary in 2026, the airline conglomerate is channelling a disproportionate share of its expansion budget into India — a market it calls its largest intercontinental play in Asia-Pacific. The moves announced this week span new routes, premium cabin upgrades, and added capacity on existing services, collectively amounting to the most aggressive India push by a European carrier group in years.

## SWISS Finally Gives Bengaluru a Direct European Link

The headline announcement: SWISS, Lufthansa's Swiss subsidiary, will launch the first-ever nonstop service between Bengaluru (BLR) and Zurich (ZRH) in the Winter 2026 schedule. The route fills a conspicuous gap. Bengaluru is India's third-largest international gateway by passenger volume and home to the country's densest concentration of tech multinationals — yet it has had no direct link to Switzerland, a country whose pharma, banking, and technology sectors employ thousands of Indian-origin professionals.

SWISS will also add Airbus A330 frequencies between Delhi and Zurich, expanding capacity on a route that has historically run at high load factors during the summer and December travel peaks.

For Bay Area NRIs with family in Karnataka, the new BLR–ZRH service means a one-stop option to the West Coast through Zurich that avoids the Gulf hubs entirely. Star Alliance connections through Zurich to San Francisco, Los Angeles, and Chicago are well-timed and competitively priced — a serious alternative to the Emirates and Qatar Airways routings that dominate the Bengaluru–US corridor.

## Allegris Cabins Come to Delhi and Hyderabad

Lufthansa is deploying its Allegris cabin product — the carrier's most significant hardware upgrade in a decade — on Boeing 787-9 services from Delhi (DEL) and Hyderabad (HYD). Allegris features redesigned business-class suites with doors, a new premium economy product with more recline and storage, and economy seats with broader armrests and improved entertainment screens.

The Hyderabad deployment is particularly notable. HYD has grown rapidly as an international hub, driven by the city's IT corridor and the large Telugu diaspora in North America. Lufthansa's decision to put its best product on this route signals confidence in the premium end of the market — business travelers and NRIs willing to pay for a flat bed on the 10-hour hop to Frankfurt.

## The A380 Returns to Mumbai–Munich

Lufthansa is expanding Airbus A380 operations between Mumbai (BOM) and Munich (MUC), responding to what the airline describes as "strong demand from both business and leisure travelers." The superjumbo, which carries over 500 passengers in Lufthansa's four-class configuration, replaces smaller-gauge equipment on what has become one of the airline's best-performing Indian routes.

Munich serves as Lufthansa's second hub and the primary gateway to Southern Europe, the Alps, and Eastern European destinations. For NRIs traveling to Italy, Austria, Croatia, or Greece — popular summer and wedding destinations — the A380 frequency adds seats at a time when capacity across the India–Europe corridor is under severe strain from the Iran conflict's airspace closures.

## The Bigger Picture: Europe Gets Easier

Lufthansa Group now operates more than 70 weekly flights between India and Europe. The expansion comes days after Germany abolished its airport transit visa requirement for Indian nationals, effective June 3. That policy change — long sought by India and the airline industry — means Indian passport holders can now transit through Frankfurt, Munich, and other German airports without a separate visa, provided they hold valid documentation for their final destination.

The combined effect is substantial. An NRI in Chicago flying to Hyderabad via Frankfurt no longer needs a transit visa for the connection. A Bengaluru-based consultant traveling to Zurich for a client meeting can now fly direct. A family in New Jersey visiting relatives in Mumbai gets A380 widebody comfort on the Mumbai–Munich leg.

Lufthansa Group carried more than 135 million passengers globally in 2025, generating €39.6 billion in revenue. India, the airline says, is central to its next phase of growth. At 100 years old, the group appears to be treating the subcontinent not as an emerging market, but as a cornerstone of its global network — and NRIs stand to benefit directly from that bet."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "InterContinental Reopens Its Mahabalipuram Resort After a Multi-Million-Dollar Overhaul — and Tamil Nadu's Coast Has a New Luxury Anchor",
        "subheadline": "Set across 15 acres of beachfront near the UNESCO-listed Shore Temple, the reimagined 110-room resort targets NRI families and destination weddings along the Coromandel Coast.",
        "slug": make_slug("intercontinental-chennai-mahabalipuram-resort-reopens-luxury"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Tamil Nadu's diaspora — concentrated in the US, UK, Singapore, and the Gulf — has long lacked a marquee luxury option near Chennai that combines heritage, beach, and modern facilities. The relaunch positions Mahabalipuram as a viable destination wedding and family reunion venue for NRIs visiting home.",
        "tags": ["travel", "hotels", "luxury", "chennai", "mahabalipuram", "tamil-nadu"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hotel Magazine", "url": "https://hotelmagazine.co.nz/2026/06/05/opening-for-intercontinental-chennai-mahabalipuram-resort/"},
            {"name": "IHG Hotels & Resorts", "url": "https://www.ihg.com/intercontinental/hotels/gb/en/mamallapuram/maaha/hoteldetail"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Shore_Temple_-Mamallapuram_-Tamil_Nadu_-N-TN-C55.jpg/1280px-Shore_Temple_-Mamallapuram_-Tamil_Nadu_-N-TN-C55.jpg",
        "image_caption": "The UNESCO-listed Shore Temple at Mahabalipuram, steps from the newly reopened InterContinental resort",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """InterContinental Chennai Mahabalipuram Resort has reopened after a comprehensive, multi-million-dollar transformation that the brand calls the final chapter of a years-long reinvention. The 110-room property, spread across 15 acres of landscaped beachfront along Tamil Nadu's East Coast Road, is now positioned as the Coromandel Coast's most ambitious luxury play — and a credible destination for NRI families who have historically bypassed Chennai's southern coast for Goa, Kerala, or Rajasthan.

## What Changed

The overhaul touches nearly every surface. The resort now features an ocean-facing ballroom — a first for the property — along with expansive beach lawns designed for large-scale events. New restaurants and bars replace the previous F&B lineup. A sports pavilion, scenic walking trails, and a meditation garden add programming that didn't exist before.

The 110 guestrooms and suites have been redesigned with a contemporary South Indian sensibility: spacious layouts, standalone bathtubs, rain showers, and views spanning the Bay of Bengal, the gardens, or the resort's central pool. At the top end, the Grand Presidential Suite offers a jacuzzi and steam room with ocean views, while the Presidential Suite includes a private pool and dedicated spa room. The Rathi Suite, a newer addition, features a plunge pool and greenery views.

"This multi-million-dollar transformation reflects our commitment to delivering destination-led, experience-rich stays that combine world-class hospitality with a strong sense of place," said Sudeep Jain, IHG's Managing Director for South West Asia.

## The Mahabalipuram Draw

The resort's location is its strongest card. Mahabalipuram — also known as Mamallapuram — is home to the UNESCO-listed Group of Monuments, including the seventh-century Shore Temple, one of the oldest structural stone temples in South India. The town's rock-cut caves, monolithic rathas, and bas-relief panels draw historians and tourists alike, but it has never had a luxury resort capable of anchoring multi-day stays.

That changes now. The InterContinental sits along the scenic East Coast Road, roughly 55 kilometres south of Chennai — close enough for an airport transfer but far enough to feel like a genuine coastal retreat. The resort's design draws directly from the Shore Temple's architectural vocabulary, blending contemporary interiors with local cultural motifs.

For NRIs visiting family in Chennai — one of the largest source cities for Indian immigration to the US, UK, and Singapore — Mahabalipuram has always been a half-day excursion tacked onto a trip to see relatives in T. Nagar or Adyar. The InterContinental's relaunch reframes it as a two-or-three-night destination in its own right: a place to decompress after the family obligations, host a sangeet or reception, or simply sit on a beach that isn't in Goa.

## The Wedding and Events Play

The ocean-facing ballroom and beach lawns signal IHG's real ambition here: capturing the NRI destination wedding market that has historically flowed to Udaipur, Jaipur, and Goa. Tamil Nadu's coast has been underrepresented in this segment despite Chennai being well-connected by international flights from Singapore, Dubai, London, and the US.

A beachfront wedding venue within an hour of Chennai International Airport, adjacent to UNESCO heritage monuments, and priced below Rajasthan's palace hotels is a proposition that didn't exist six months ago. The resort's ballroom and lawn infrastructure suggest IHG is betting on exactly this market.

## Broader Context

The reopening fits a pattern. India's luxury hotel sector is in the middle of its most aggressive expansion cycle in a decade, driven by rising domestic demand and a surging NRI travel market. ITC Hotels recently acquired a premium Kerala property. The Leela is expanding to Jaisalmer, Srinagar, and Dubai. Sanjay Dutt's Evren just launched in Goa under the Small Luxury Hotels banner.

InterContinental's Mahabalipuram play stands out because it bets on a location with genuine heritage and natural beauty that has been underserved by the hospitality industry. Whether the bet pays off depends on whether NRIs — and the domestic elite — are willing to view Tamil Nadu's coast as a luxury destination rather than a temple trail. The product, at least, is now ready for that conversation.

General Manager Anand Nair put it directly: "Our ambition is to position the resort not merely as a place to stay, but as a destination in its own right." For the lakhs of Tamil NRIs who fly into Chennai every year, that destination just became a lot harder to skip."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Maldives Luxury Chain Is Quietly Building 20 Resorts Across India — From Goa's Beaches to Meghalaya's Hills",
        "subheadline": "Atmosphere Core, the hospitality group behind some of the Maldives' most popular resorts, is deploying a villa-first model across India's emerging leisure destinations. NRIs who fly to Malé for a villa holiday may soon find the same product in Coorg, Kannur, and Mussoorie.",
        "slug": make_slug("atmosphere-core-maldives-chain-india-expansion-luxury-villas"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans spend an estimated $2-3 billion annually on Maldives holidays. Atmosphere Core's India expansion means NRIs visiting home can now add a villa-style beach or hill-station stay to their India trip — no separate international flight to Malé required.",
        "tags": ["travel", "hotels", "luxury", "maldives", "northeast-india", "goa", "coorg"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/maldives-hotel-chain-atmosphere-core-india-leisure-travel-11780544902525.html"},
            {"name": "TravelPlusStyle", "url": "https://www.travelplusstyle.com/new-luxury-hotels/best-luxury-hotel-openings-2026"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16744884/pexels-photo-16744884.jpeg",
        "image_caption": "A luxury resort villa with private pool in India — the kind of product Atmosphere Core plans to replicate across 20 Indian properties",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """For years, the Maldives has been the default luxury getaway for India's affluent travellers and its diaspora. Direct flights from Delhi, Mumbai, and Bengaluru made the island nation an easy sell: overwater villas, private pools, all-inclusive packages, and the kind of curated seclusion that Indian resorts rarely matched. Now, the company behind some of the Maldives' best-known properties wants to build that same product on Indian soil.

Atmosphere Core, the hospitality group that operates resorts across the Maldives, is in the advanced stages of an India expansion that will span at least 20 properties across leisure destinations from Goa's coastline to the hills of Meghalaya. The strategy, detailed in a recent Mint report, marks one of the most ambitious entries into India's luxury hospitality market by an international operator focused exclusively on the leisure segment.

## The Portfolio Taking Shape

The numbers are striking. Atmosphere Core has signed seven to eight projects in India's Northeast — primarily across Assam and Meghalaya — alongside developments in Rajasthan, Goa, and Maharashtra. A 235-room property in Kolkata has been completed and awaits operating approvals. A 51-villa resort in Goa, a 56-villa property in Coorg, and a 70-villa resort in Kannur are in various stages of development. In Gurugram, a 46-villa property positions the brand in the luxury segment within the National Capital Region.

The company is also directly investing in three properties — in Mussoorie, Puri, and Kannur — through partnerships with high-net-worth investors, with a combined outlay of approximately ₹1,000 crore ($105 million). The remaining properties will follow an asset-light management contract model, allowing faster expansion without the capital intensity of ownership.

"The Northeast has good potential. We will see development in states like Manipur, Arunachal Pradesh, Meghalaya, and Assam," said Subhash Panigrahi, the company's head of India operations, pointing to new airports, roads, and connectivity improvements that are making the region accessible for the first time to premium travellers.

## Why This Matters for NRIs

The Maldives has become almost synonymous with Indian luxury travel. Indian tourists were the largest nationality group visiting the Maldives in 2025, and the Indian American diaspora accounts for a significant share of that traffic. A week at a Maldives resort — flights, transfers, and the resort package — typically runs $3,000 to $8,000 per person, and for NRI families of four visiting from the US, the total bill can exceed $25,000.

Atmosphere Core's India play changes the calculus. An NRI family flying to Bengaluru to visit parents in Karnataka can now tack on a four-night villa stay in Coorg — coffee plantations, private plunge pool, curated dining — at a fraction of the Maldives price. A family visiting relatives in Kolkata can drive two hours to a property in the Bengal hills. A Diwali trip to Delhi can include a weekend at a Mussoorie hillside villa that matches Maldives standards.

The villa-first model is key. Indian hotels have traditionally centred on rooms — even luxury properties like Oberoi, Taj, and Leela default to room configurations with shared pool and dining facilities. The Maldives model, built around standalone villas with private pools and personalised service, is what Indian affluent travellers have been flying abroad to experience. Atmosphere Core's bet is that this product, transplanted to Indian landscapes, will capture demand that currently leaks overseas.

## The Northeast Frontier

The most intriguing element of the expansion is the Northeast push. Seven to eight signed projects across Assam and Meghalaya represent a serious commitment to a region that India's established hotel chains have largely ignored. The infrastructure thesis is real: new airports in Itanagar, expanded terminals in Guwahati, and improved highway connectivity are making destinations like Shillong, Kaziranga, and Meghalaya's living root bridges accessible within a day's travel from Delhi or Kolkata.

For NRIs seeking an India beyond the Delhi–Agra–Jaipur triangle, the Northeast has enormous appeal: spectacular biodiversity, distinct indigenous cultures, and landscapes that range from tropical river valleys to cloud-wrapped hills. What it has lacked is hospitality infrastructure. A villa resort in Meghalaya operated by a group with Maldives-level service standards could be the product that finally converts NRI curiosity about the Northeast into actual bookings.

## The Competitive Landscape

Atmosphere Core enters an Indian luxury market that is simultaneously booming and undersupplied. ITC Hotels just acquired a Kerala backwater resort. The Leela is building in Jaisalmer. Marriott, Hyatt, and Accor are all expanding their Indian portfolios aggressively. But few of these players are building villa-format properties at scale outside of Goa.

The Maldives group's advantage is that it knows exactly how to operate the villa model — the staffing ratios, the all-inclusive packaging, the privacy architecture, the curated experiences that justify premium pricing. Whether that expertise translates to the operational realities of Indian real estate, staffing markets, and infrastructure remains the open question. But for NRIs who have been subsidising the Maldives tourism industry for years, the prospect of getting that experience during their India trip, rather than instead of it, is the most compelling travel development of the year."""
    }
]

for art in articles:
    img_url = art.get("image_url", "")
    print(f"\n🔍 Verifying image for: {art['slug']}")
    if not verify_image(img_url):
        print(f"  ❌ Skipping article due to bad image")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
