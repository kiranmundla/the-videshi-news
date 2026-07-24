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


# ─────────────────────────────────────────────────────
# ARTICLE 1: Air India Maharaja Lounge at SFO
# ─────────────────────────────────────────────────────
article1_body = """Air India has opened its first branded lounge outside India — and it chose San Francisco, the airport that arguably matters most to the Indian American diaspora.

The Maharaja Lounge, a 3,300-square-foot space near Gate A1 in SFO's International Terminal, marks a deliberate signal that the Tata-owned carrier is investing in the ground experience, not just the seats above the clouds. For the hundreds of thousands of Indian Americans who fly through SFO each year, this is the first time an Indian airline has offered anything resembling a flagship lounge on US soil.

## Who Gets In

Access is limited to Air India First and Business Class passengers, Maharaja Club Gold and Platinum members, and eligible Star Alliance premium guests. Economy flyers are out of luck, but the lounge's existence raises the competitive bar for every airline operating the transpacific India corridor.

The space seats 80 guests and includes a dedicated First Class zone, a tarmac-view seating area, and what Air India calls the Aviator's Bar — a speakeasy-style cocktail space with curated whiskies and a signature drink called the Maharaja Manhattan, made with black pepper as a nod to India's spice trade history.

## The Food Is the Point

Live cooking stations serve Indian and international dishes, with a hot buffet and cold counter rounding out the options. For anyone who has endured a sad United Polaris pretzel basket before a 16-hour flight to Delhi, the promise of freshly prepared Indian food at the gate is a tangible upgrade.

The lounge was designed by Hirsch Bedner Associates (HBA), the firm behind many of the world's top hotel interiors. The aesthetic blends champagne and ivory tones with deep red accents, upcycled aircraft parts turned into art installations, and work by local Bay Area artists — a subtle but deliberate move to root the space in its host city rather than defaulting to generic luxury.

## Why SFO, and Why Now

The timing is not accidental. Air India has expanded its SFO operations from nine to seventeen weekly flights, now serving Delhi, Bengaluru, and Mumbai. Seat capacity has more than doubled compared to pre-pandemic levels — a 186 percent increase, according to the airline. SFO is now one of Air India's most important North American gateways, and the lounge exists to match that volume with a premium ground experience.

The broader context matters too. Air India's Tata-era transformation has been heavy on fleet orders and route expansion, but the lounge game has lagged. The Maharaja Lounge is the first step in fixing that gap, with future locations planned for New York and other key international cities.

## What This Means for NRIs

For the estimated 700,000-plus Indian Americans in the Bay Area, this is a practical upgrade. SFO-Delhi and SFO-Bengaluru are among the most heavily traveled diaspora routes in the world. A branded lounge at the departure gate means NRIs flying premium cabins — or those who have accumulated enough loyalty points — now have a reason to prefer Air India over Emirates, Singapore Airlines, or Cathay Pacific for the first leg of their journey home.

It also sends a message about what kind of airline Air India is trying to become. The lounge market at international airports is crowded and competitive. Planting a flag at SFO, in the heart of the tech diaspora, is a statement of intent that goes beyond a cocktail menu."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Just Opened Its First International Lounge — and It Picked the Heart of NRI Country",
    "subheadline": "The new Maharaja Lounge at San Francisco's International Terminal seats 80, pours signature cocktails, and serves freshly cooked Indian food at the gate. SFO now has 17 weekly Air India flights.",
    "slug": make_slug("air-india-maharaja-lounge-sfo-nri-bay-area"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The Bay Area is home to 700,000+ Indian Americans who fly the SFO-India corridor regularly — this is the first branded Indian airline lounge on US soil, giving NRIs a premium alternative to Gulf carrier lounges.",
    "tags": ["travel", "airlines", "air-india", "sfo", "lounge", "bay-area"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/etcf8jzloqy5/"},
        {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/air-india-easy-connect-flights/"},
        {"name": "Air India Official", "url": "https://www.airindia.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/San_Francisco_International_Airport_-_aerial_photo.jpg",
    "image_caption": "Aerial view of San Francisco International Airport, Air India's newest premium lounge location",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────────────
# ARTICLE 2: Thailand 15-Day Visa-Free for Indians
# ─────────────────────────────────────────────────────
article2_body = """Thailand has dropped the visa barrier for Indian travelers, introducing a 15-day visa-free entry that makes it the latest Southeast Asian country to bet heavily on the Indian outbound market. For NRIs in the US planning a monsoon-season escape or a family reunion in a neutral third country, the timing could not be better.

The new policy allows Indian passport holders to enter Thailand for up to 15 days without applying for a visa in advance — no embassy appointment, no e-visa form, no fee. It joins a growing list of countries that have simplified or eliminated visa requirements for Indians, including Malaysia, Singapore, Vietnam, and Sri Lanka, which waived its own tourist visa fees just last month.

## What Changed

Previously, Indian nationals needed either a visa-on-arrival (which cost roughly $15 and required paperwork at the airport) or a pre-arranged tourist visa from a Thai consulate. The new visa-free arrangement removes both steps entirely for stays of 15 days or fewer. Travelers simply show up with a valid Indian passport and proof of onward travel.

Thailand's tourism authority has framed the move as a response to India becoming one of its top three source markets. The Indian traveler demographic skews younger and higher-spending than the regional average, with particular strength in luxury resorts, destination weddings, wellness retreats, and food tourism — categories where Thailand has built a global reputation.

## The NRI Angle

For Indian Americans, Thailand has always been on the short list of affordable, visa-friendly destinations for family gatherings that do not require dragging aging parents through a US visa interview or an expensive European Schengen application. The 15-day window is generous enough for a proper vacation — Bangkok, Chiang Mai, Phuket, and the islands can all fit into a two-week itinerary.

It also helps that Thailand is one of the few countries where an Indian passport and a US green card or visa are not required for entry. Indian nationals — whether NRIs, OCI holders, or India-based relatives — all qualify equally. That makes it a practical meeting point for diaspora families scattered across multiple countries.

## The Competitive Landscape

Thailand's move intensifies a quiet visa war across Southeast Asia for Indian tourist dollars. Malaysia already offers Indians visa-free entry for up to 30 days. Singapore has streamlined its approval process. Vietnam has expanded its e-visa scheme. Sri Lanka dropped its tourist visa fee entirely on May 25, covering 40 countries including India.

The pattern is clear: countries across Asia are recognizing that India's outbound travel market — projected to hit 50 million trips annually by 2030 — is too large to gate behind consulate appointments and processing fees. Thailand, with its established tourism infrastructure, proximity to India (flights from Delhi or Mumbai take under five hours), and reputation for hospitality, is well positioned to capture a disproportionate share.

## Practical Details

The 15-day visa-free entry applies to Indian passport holders arriving by air. Key requirements include a passport valid for at least six months, proof of onward or return travel, and evidence of accommodation. The policy is designed for tourism — working or studying requires separate authorization. Travelers who want to stay longer than 15 days will still need to arrange a tourist visa through standard channels.

For NRIs looking at summer and monsoon-season travel, the math works out well. Round-trip fares from US West Coast cities to Bangkok typically run $600–900 in economy, and Thailand's cost of living makes it one of the most budget-friendly destinations in Asia once you land. The elimination of the visa fee and paperwork removes one more friction point from an already compelling proposition."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Thailand Drops the Visa Barrier for Indian Travelers — and NRIs Get the Easiest Family Reunion Destination Yet",
    "subheadline": "A new 15-day visa-free policy means Indian passport holders can now enter Thailand without any advance paperwork, joining a growing list of Asian countries competing for India's booming outbound travel market.",
    "slug": make_slug("thailand-visa-free-indians-nri-family-travel"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Thailand's visa-free entry applies equally to Indian passport holders, NRIs, and OCI holders — making it a practical meeting point for diaspora families scattered across countries without the hassle of Schengen or US visa interviews for relatives.",
    "tags": ["travel", "visa", "thailand", "visa-free", "family-travel", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/2hrxcv4nq571/"},
        {"name": "Travel and Tour World - Sri Lanka visa waiver", "url": "https://www.travelandtourworld.com/news/article/sri-lanka-free-tourist-eta/"},
        {"name": "Visament - Visa Free Countries for Indians", "url": "https://visament.com/visa-free-countries-for-indian-passport-holders/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/30540817/pexels-photo-30540817.jpeg",
    "image_caption": "Skyline view of Bangkok with traditional Thai architecture and modern cityscape",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ─────────────────────────────────────────────────────
# ARTICLE 3: India Domestic Flight Crunch
# ─────────────────────────────────────────────────────
article3_body = """If you are planning a summer trip to India and expecting to fly cheaply between cities once you land, recalibrate now. Air India has slashed its domestic schedule by 20 to 22 percent, IndiGo is pulling back capacity, and aviation turbine fuel prices show no sign of dropping. The cheap domestic flight era in India is over, at least for this summer.

The cuts began on May 27, when Air India trimmed roughly one in five of its domestic flights. The carrier had already scaled back select international routes on May 13, but the financial pressure from ATF prices — which were hiked by 10 percent under a new government stabilization scheme — proved too severe to absorb through international adjustments alone. The domestic network took the hit.

## The Ripple Effect

IndiGo, which controls the largest share of India's domestic market, has also reduced seat capacity. The airline has characterized the pullback as a seasonal monsoon-quarter adjustment, but the timing — concurrent with Air India's deeper cuts — means the two carriers that together dominate Indian domestic aviation are both offering fewer seats at the same time.

SpiceJet and Akasa Air have followed with their own reductions and surge pricing on high-demand routes. The result is a market where fewer seats are available, fares are climbing, and alternatives are thin. Indian Railways, the usual fallback, is itself fully booked on most popular routes during peak summer.

The numbers tell the story. According to travel industry sources, baseline domestic fares on popular corridors like Delhi-Mumbai, Delhi-Bengaluru, and Mumbai-Hyderabad have already risen 15 to 25 percent compared to the same period last year. Further increases are expected as the monsoon season progresses and capacity remains constrained.

## Why This Hits NRIs Hardest

For Indian Americans visiting family during summer break, the domestic leg of the trip is often the most logistically fragile part of the itinerary. You book a transpacific flight to Delhi or Mumbai months in advance. Then you need a connecting domestic flight to Varanasi, Hyderabad, Lucknow, Ahmedabad, or wherever your family actually lives. Those domestic connections are exactly the flights being cut.

The financial impact compounds quickly. A family of four flying Delhi to Hyderabad round-trip might now pay ₹50,000 to ₹70,000 ($590–$830) for tickets that would have cost ₹30,000 ($355) a year ago. And unlike transpacific fares, which NRIs typically lock in months ahead, domestic India flights are often booked closer to travel dates — precisely when the remaining seats carry the steepest premiums.

There is also the rebooking risk. Airlines that cancel flights are required to offer alternatives or refunds, but in a constrained market, the "alternative" may be a flight the next day or a routing through a different hub entirely. For NRIs coordinating tight family visit schedules, a one-day delay on a domestic leg can cascade through an entire trip.

## What to Do

Book domestic India flights as early as possible — ideally at the same time you book your international ticket. Do not wait until you arrive to figure out the internal routing. Consider indirect options: the new Vande Bharat express trains now cover several popular corridors at speeds that make them competitive with short-haul flights once you factor in airport wait times and the risk of cancellation.

For trips to Tier-2 cities, Air India's new Easy Connect hub-and-spoke model — launching June 25 from Varanasi — may eventually help by routing international passengers through Delhi with a single immigration stop. But for this summer, the program is limited to one city, and the broader capacity crunch remains the dominant reality.

The structural issue is not going away. Global energy markets remain elevated, the Iran conflict continues to push Brent crude above $93 a barrel, and Indian ATF prices are indexed to global benchmarks. Airlines will not restore cut capacity until the economics justify it, and nothing in the current fuel price trajectory suggests that happens before autumn at the earliest."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Airlines Just Cut One in Five Domestic Flights — and NRIs Flying Home This Summer Will Feel It",
    "subheadline": "Air India has slashed 20-22% of its domestic schedule as jet fuel costs surge. IndiGo and SpiceJet are pulling back too. Fares on key corridors are up 15-25% and climbing.",
    "slug": make_slug("india-domestic-flights-cut-atf-fuel-nri-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting India this summer face sharply higher domestic airfares and cancellation risk on the connecting flights they rely on to reach family beyond Delhi and Mumbai — the domestic leg is now the most fragile part of the trip.",
    "tags": ["travel", "airlines", "air-india", "indigo", "domestic-flights", "fuel-prices", "summer-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/chsjyjx5dcrb/"},
        {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/air-india-easy-connect-flights/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/air-india-to-launch-hub-and-spoke-international-connectivity-flights-from-june-25/article69658614.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/392265/pexels-photo-392265.jpeg",
    "image_caption": "Airport departure terminal with passengers — domestic flight options in India are shrinking this summer",
    "image_attribution": "Pexels",
    "body": article3_body
}


# ─────────────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────────────
articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
