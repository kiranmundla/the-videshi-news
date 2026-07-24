#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-13 batch."""
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
        "headline": "India Dominates Skytrax's Best Regional Airports — and NRIs Flying Home Will Notice the Difference",
        "subheadline": "Bengaluru takes the top spot, nine of the ten best regional airports in South Asia are Indian, and the upgrades matter most to diaspora travelers navigating connections beyond Delhi and Mumbai.",
        "slug": make_slug("india-skytrax-best-regional-airports-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying home increasingly connect through regional airports like Bengaluru, Hyderabad, and Amritsar — knowing which ones offer the best experience saves hours of stress on already exhausting 20-hour journeys.",
        "tags": ["travel", "airports", "india", "skytrax", "bengaluru", "hyderabad"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/index.php/2026/06/12/top-10-best-regional-airports-in-india-south-asia-in-2026/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/"},
            {"name": "Skytrax World Airport Awards", "url": "https://www.worldairportawards.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37540293/pexels-photo-37540293.jpeg",
        "image_caption": "Airplanes on the tarmac at Delhi airport with terminal buildings in the background",
        "image_attribution": "Pexels",
        "body": """India's regional airports aren't what they used to be. The 2026 Skytrax rankings for best regional airports in India and South Asia confirm what frequent flyers already suspect: the country's non-metro gateways have quietly become some of the best-run airports in Asia.

Nine of the top ten slots belong to Indian airports. Bengaluru's Kempegowda International takes the crown, followed by Hyderabad's Rajiv Gandhi International and Goa's gleaming new Manohar International. The list rounds out with Chennai, Goa's older Dabolim, Chittagong (the sole non-Indian entry, from Bangladesh), Amritsar, Kozhikode, Nagpur, and Kolkata.

## Bengaluru sets the standard

Kempegowda's Terminal 2, which opened in 2022, has become a case study in what Indian airport design can look like when the ambition matches the investment. Its garden-inspired interiors, natural light wells, and green spaces feel closer to Singapore's Changi than to the fluorescent-lit chaos that defined Indian air travel a decade ago. Passenger flow is smooth, lounges are spacious, and the terminal handles rising traffic volumes without the bottlenecks that plague older hubs.

For NRIs arriving on red-eye flights from San Francisco or Newark, that matters. A calm, well-organized arrival at 4 AM — rather than the sensory assault of Delhi's T3 — can set the tone for the entire trip home.

## Hyderabad and Goa hold strong

Hyderabad's Rajiv Gandhi International, ranked second, has long been a quiet overachiever. Quick processing times and a manageable layout make it one of the easiest Indian airports to navigate, a particular advantage for the large Telugu diaspora flying in from the US on connecting legs through Dubai or Doha.

Goa's Manohar International, at third, represents the next generation. Opened specifically to relieve pressure on the aging Dabolim facility, it has quickly won praise for its modern infrastructure and reduced congestion. Both airports made the list, a testament to Goa's exploding tourism traffic and the state's decision to build capacity rather than patch the old.

## Amritsar and Kozhikode: diaspora lifelines

Two airports on the list carry outsized significance for the Indian diaspora. Amritsar's Sri Guru Ram Dass Jee International, ranked seventh, serves as the primary gateway for the Punjabi diaspora — handling heavy traffic from direct flights to Birmingham, Rome, Milan, and several Gulf cities. Its growing international profile has attracted infrastructure upgrades that its passenger numbers long demanded.

Kozhikode's Calicut International, at eighth, is the aviation backbone of Kerala's Gulf migration. Millions of Malayali expats cycle through its terminals on their way to and from jobs in the UAE, Saudi Arabia, and Qatar. Despite challenging terrain — the tabletop runway requires special approach procedures — the airport scores well on efficiency and handling of international arrivals.

## What this means for NRIs

The broader trend matters more than any single ranking. A decade ago, an NRI flying into a regional Indian airport could expect dim terminals, confusing signage, and long waits for luggage. That experience is rapidly changing. Government modernization programs, private investment, and sheer passenger growth have pushed standards upward across the board.

For diaspora travelers, the practical takeaway is straightforward: if your final destination is Bengaluru, Hyderabad, or even Nagpur, flying through these regional airports — rather than defaulting to a Delhi or Mumbai connection — may actually offer a smoother, faster, and less stressful experience. With Air India's new Easy Connect hub-and-spoke model starting June 25, the calculus shifts further in favor of routing through India's improved regional gateways.

The old assumption that smaller Indian airports mean worse experiences is officially outdated. The data says the opposite."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IndiGo Launches Direct Bangkok–Varanasi Flights — and the Internet Can't Stop Laughing",
        "subheadline": "The budget carrier's new route connecting Southeast Asia's party capital to India's holiest city has gone viral for all the right reasons, but the real story is the strategic corridor it opens for Thai-Indian tourism.",
        "slug": make_slug("indigo-bangkok-varanasi-direct-flight-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs planning a Thailand trip before heading to family functions in UP or Bihar, this route eliminates a painful Delhi connection and links two destinations they were already visiting separately.",
        "tags": ["travel", "indigo", "airlines", "bangkok", "varanasi", "thailand"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/u2esbuh4p5l7/"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17869831/pexels-photo-17869831.jpeg",
        "image_caption": "Colorful riverside buildings and boats along the ghats of Varanasi on the Ganges",
        "image_attribution": "Pexels",
        "body": """IndiGo's newest route connects Bangkok to Varanasi, and the internet did exactly what the internet does. Within hours of the announcement, social media was flooded with memes about flying from Thailand's nightlife capital straight to the ghats of the Ganges. "Do paap in Bangkok, fly to Varanasi for prayaschit" became the dominant punchline, and the route trended across Indian Twitter and Instagram.

The jokes write themselves. But underneath the viral moment lies a genuinely smart piece of network strategy from India's largest airline.

## Why this route makes sense

Varanasi has been at the center of India's aviation expansion. The city's Lal Bahadur Shastri International Airport is the first to join Air India's Easy Connect hub-and-spoke system, which launches June 25 and enables passengers from tier-2 cities to complete immigration before reaching Delhi. IndiGo's Bangkok route adds an international spoke to Varanasi from the other direction.

Thailand is already among the top source countries for tourists visiting India's spiritual and heritage circuits. Varanasi, with its 3,000-year-old temples, nightly Ganga Aarti ceremonies, and labyrinthine old city, ranks among the most visited Indian destinations for Southeast Asian visitors. The direct flight eliminates the Delhi connection that previously made this trip a two-flight affair.

From IndiGo's side, the route fills a niche that full-service carriers haven't addressed. Bangkok–Delhi and Bangkok–Mumbai are well-served, but Southeast Asia's connectivity to India's cultural heartland has been limited to indirect routings. A direct budget option changes that equation.

## The NRI calculation

For the Indian American diaspora, this route solves a different problem. Thailand is one of the easiest international trips an NRI can take — visa-free with a US visa, cheap flights, world-class food, and beaches that compete with anything in the Caribbean. Many NRIs combine a Bangkok stopover with a trip to India, especially when visiting family in Uttar Pradesh, Bihar, or Jharkhand.

Until now, that meant flying Bangkok to Delhi, then Delhi to Varanasi (or a grueling 12-hour train ride). IndiGo's direct service cuts that to a single flight. For a family of four hauling suitcases of gifts and NRI-grade shopping, the elimination of one connection is worth more than the fare difference.

## Thailand's open door

Thailand's decision to grant visa-free entry to Indian passport holders, announced earlier this year, has turbocharged Indian arrivals. Direct flights to tier-2 Indian cities are the next logical step for both Thai tourism authorities and Indian carriers looking to capture that demand.

IndiGo is positioning itself to own this corridor. The airline already operates routes from multiple Indian cities to Bangkok, and adding Varanasi deepens its network in a way that's hard for competitors to replicate quickly. The route also feeds IndiGo's broader Southeast Asian ambitions — the carrier has been steadily expanding to Vietnam, Malaysia, and Indonesia over the past two years.

## Spiritual tourism meets budget travel

Tourism experts have noted a growing category they call "spiritual-leisure" travel — itineraries that combine sacred sites with recreational destinations. The Bangkok–Varanasi corridor is a textbook example. Curated packages combining temple visits, Ganga boat rides, and Thai beach time are already being assembled by Indian tour operators.

The memes got the attention, but the underlying trend is serious. India's spiritual tourism market generates over $30 billion annually, and Varanasi is its beating heart. Connecting it directly to Southeast Asia's most popular leisure hub isn't just funny — it's good business.

Whether travelers are seeking redemption, relaxation, or both, IndiGo has built the bridge."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five-Star Hotel Bookings in India Surge 108% — and NRIs Are Part of the Reason",
        "subheadline": "Cleartrip's summer travel data reveals a dramatic shift toward luxury, driven by geopolitical uncertainty, domestic tourism confidence, and a generation of Indians who now expect global-standard hospitality at home.",
        "slug": make_slug("india-luxury-hotel-bookings-surge-nri-summer"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs returning for weddings and family visits are increasingly booking luxury stays rather than staying with relatives — and India's hotel industry is finally delivering the quality they expect.",
        "tags": ["travel", "hotels", "luxury", "india", "summer", "cleartrip"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/News/luxury-leads-the-boom-as-indian-summer-travel-enters-an-experience-first-era"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Cleartrip NoVac Report", "url": "https://www.cleartrip.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36563720/pexels-photo-36563720.jpeg",
        "image_caption": "Ornate poolside area at a luxury hotel in Jaipur, India",
        "image_attribution": "Pexels",
        "body": """Something has shifted in how Indians travel domestically. Five-star hotel bookings rose 108.2% year-on-year this summer, according to new data from Cleartrip's annual "Nation on Vacation" tracker. Overall hotel bookings surged over 80%, flights grew 20%, and family hotel stays — the multigenerational kind that India does better than almost anyone — jumped 124.9%.

These aren't pandemic-recovery numbers anymore. India's domestic luxury travel market is maturing into something structural, and the forces driving it affect NRIs as much as resident Indians.

## Geopolitics is reshaping where Indians vacation

The West Asia conflict and the Hormuz corridor tensions have made international travel uncertain and expensive. Flights through the Gulf — the most common routing for Indian travelers to Europe and Africa — are rerouting, fares are climbing, and travel insurance policies are riddled with conflict-zone exclusions. The result: Indian families who would normally fly to Portugal or Switzerland are staying domestic and upgrading their accommodations instead.

ITC Hotels, The Leela, and Oberoi are all reporting strong demand for their premium properties. The Leela is running "stay three nights, pay for two" packages at its Rajasthan properties — not discounts, but value propositions aimed at travelers who already decided to spend but redirected their budgets inward. Postcard Hotels, the uber-luxury chain, is seeing demand for flexible long-stay itineraries from guests who would previously have booked European vacations.

## The NRI luxury upgrade

For NRIs, the story is more personal. The traditional diaspora trip to India — crash at the family home, endure the broken AC, negotiate bathroom schedules with twelve relatives — is giving way to a hybrid model. Many NRIs now book a nearby luxury hotel for at least part of their visit, especially during wedding season or extended family gatherings.

India's hotel industry has made this easier. A decade ago, the gap between a Marriott in Houston and a Marriott in Jaipur was jarring. Today, properties like the JW Marriott Ranthambore (Marriott's 10,000th hotel globally, which opened this year), the new Oberoi at Khajuraho, and the upcoming Leela Jaisalmer in the Thar Desert compete on global standards. The service was always there; the infrastructure has finally caught up.

## Where the money is flowing

Cleartrip's data reveals the new geography of Indian travel. Bengaluru emerged as the most popular domestic destination for Gen Z and Millennials, functioning less as a final destination and more as a gateway for road trips and regional exploration across Karnataka and Kerala.

Northeast India is the breakout story. Dibrugarh, Dimapur, Imphal, and Agartala are seeing meaningful booking growth, driven partly by solo women travelers — whose bookings to the region rose 31.9%. The northeast has always been India's best-kept travel secret. It may not stay secret much longer.

For international destinations, Bali leads among younger Indian travelers, followed by Phuket, Kuala Lumpur, Dubai, and Singapore. But the domestic numbers tell the clearer story: when the world gets uncertain, Indians explore their own country — and they're doing it at a higher price point than ever before.

## The family-hotel connection

The 124.9% surge in family hotel bookings is the most revealing number in the data. Indian families are not just traveling more — they're choosing to stay in proper hotels rather than at relatives' homes, family guesthouses, or budget lodges. Group bookings rose 24%, and family travel overall climbed 68.6%.

This mirrors a pattern NRIs know well. The generation that grew up staying in crowded joint-family homes during summer vacations is now earning enough to book the Taj or the Oberoi for their own kids. It's not a rejection of family — it's an upgrade that lets you enjoy family time without sharing a bathroom.

## What comes next

India's luxury hospitality sector is betting that this isn't a blip. New properties opening in 2026 include a Dusit International resort in Rishikesh, a Courtyard by Marriott in Kochi's tech hub, Hilton's first LXR collection property in Bengaluru, and The Leela's desert debut in Jaisalmer. Each targets a different segment — wellness, business, tech-adjacent, destination weddings — but all share one assumption: Indian travelers, domestic and diaspora alike, will keep trading up.

The data suggests they're right. When five-star bookings double in a single year, the market isn't fluctuating. It's transforming."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
