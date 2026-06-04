#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-04 22:00 UTC run
Three articles:
1. India-Oman CEPA enters force — trade, energy, mobility for 700K NRIs
2. Global aviation's worst crisis since COVID — IATA summit, fare outlook
3. IndiGo Manchester exit — first-ever European routes die at 13 months
"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ───────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
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
IMG_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


def compress_image(img_bytes, max_width=1200, quality=80):
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase article-images bucket."""
    print(f"  Downloading {img_url[:80]}...")
    r = requests.get(img_url, headers=UA, timeout=30)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return None
    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    up_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
    if resp.status_code not in (200, 201):
        # Try PUT for upsert
        resp = requests.put(upload_url, headers=up_headers, data=compressed, timeout=30)
    resp.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✅ Uploaded: {public_url}")
    return public_url


def validate_image(url):
    """Quick HEAD check that URL returns a real image."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        return ct.startswith('image/') and cl > 5000
    except:
        return False


# ── Image sourcing ─────────────────────────────────────────────────
print("\n🖼️  Sourcing images...\n")

# Article 1: India-Oman CEPA — Al Alam Palace, Muscat
img1_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Al_Alam_Palace.jpg/1280px-Al_Alam_Palace.jpg"
art1_id = str(uuid.uuid4())
art1_slug = make_slug("india-oman-cepa-trade-pact-nri-gulf-mobility")
img1_url = upload_to_supabase(img1_source, f"{art1_slug}.jpg")

# Article 2: IATA / aviation crisis — aviation fuel truck (Commons)
img2_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Shell_aviation_fuel_truck_at_V%C3%A6rnes.jpg/1280px-Shell_aviation_fuel_truck_at_V%C3%A6rnes.jpg"
art2_id = str(uuid.uuid4())
art2_slug = make_slug("iata-global-aviation-crisis-iran-war-nri-fares")
img2_url = upload_to_supabase(img2_source, f"{art2_slug}.jpg")

# Article 3: IndiGo Manchester — IndiGo aircraft (Wikipedia)
img3_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1280px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg"
art3_id = str(uuid.uuid4())
art3_slug = make_slug("indigo-manchester-flights-axed-uk-nri-diaspora")
img3_url = upload_to_supabase(img3_source, f"{art3_slug}.jpg")


# ── Articles ───────────────────────────────────────────────────────
print("\n📝 Preparing articles...\n")

articles = [
    # ─── Article 1: India-Oman CEPA ─────────────────────────────────
    {
        "id": art1_id,
        "headline": "India-Oman Trade Pact Enters Force — and It's About More Than Tariffs for 700,000 Gulf NRIs",
        "subheadline": "The Comprehensive Economic Partnership Agreement, effective June 1, gives India a secure energy route past the Hormuz chokepoint and opens professional mobility lanes for the Indian diaspora in Oman.",
        "slug": art1_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "700,000 Indians in Oman gain enhanced professional mobility, social security protections, and Ayurveda licensing pathways. NRIs with US visas can already enter Oman visa-free for 14 days — the CEPA now makes Oman a stronger business and transit hub for the diaspora.",
        "tags": ["travel", "oman", "india-oman", "trade", "nri", "gulf", "mobility"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters via OilPrice.com", "url": "https://oilprice.com/Energy/Energy-General/Indias-Oman-Bet-Looks-Timely-As-Hormuz-Crisis-Deepens.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/india-oman-energise-new-economic-corridor/article69651234.ece"},
            {"name": "Capital Market", "url": "https://www.capitalmarket.com/news/general-news/indiaaoman-cepa-comes-into-force-opens-dutyfree-access-for-over-99-of-indian-exports/1473234"},
            {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/national/india-oman-fta-modi-secures-oil-deal-from-gulf-country/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img1_url,
        "image_caption": "Al Alam Palace in Muscat, the seat of Oman's monarchy and a symbol of India-Oman diplomatic ties",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India and Oman's Comprehensive Economic Partnership Agreement quietly came into force on June 1, and its timing could not have been sharper. Signed in Muscat last December, the pact was ratified by Sultan Haitham in February — months before the Strait of Hormuz became functionally uninsurable for most tanker traffic. What was negotiated as a trade deal now doubles as a strategic energy corridor.

## The Hormuz problem

The numbers are stark. Nearly 45 percent of India's crude oil imports, 55 percent of its LNG shipments, and 90 percent of its LPG flow through the Strait of Hormuz. The Iran conflict has turned that chokepoint into a liability: insurance premiums have spiked, tanker operators are rerouting, and Iran has repeatedly threatened to seal the waterway entirely.

Oman's geography offers India a workaround. Its primary commercial ports — Duqm, Sohar, and Salalah — sit outside the Strait, directly on the Arabian Sea. Under the CEPA, Oman will eliminate customs duties on 98 percent of its tariff lines, giving Indian exporters immediate preferential access. For energy imports flowing the other direction, Oman's ports now provide a secure route that avoids Hormuz entirely.

## What NRIs gain

The CEPA is not just a commodity play. Buried in its services chapters are provisions that directly affect the roughly 700,000 Indians living and working in Oman — one of the largest Indian communities in the Gulf.

**Professional mobility.** For the first time in any Indian free trade agreement, Oman has established a dedicated mobility regime for independent professionals. The deal liberalises entry and stay rules for Indian workers in accountancy, taxation, architecture, and healthcare. The Intra-Corporate Transferee ceiling rises to 50 percent, meaning Indian firms can deploy specialised staff to Oman far more flexibly than before.

**Healthcare integration.** A dedicated annex facilitates the recognition of traditional Indian medical systems — including Ayurveda — within Oman's mainstream healthcare framework. Licensing procedures for Indian medical professionals get streamlined.

**Social security.** The agreement mandates negotiation of a Social Security Agreement, which would protect Indian workers in Oman from the burden of paying into two national systems simultaneously. For the thousands of Indian engineers, IT professionals, and construction workers who cycle between Muscat and home, that is real money.

## The travel angle

For NRIs visiting or transiting through the Gulf, Oman was already accessible. Indian passport holders with a valid US, UK, Canada, Australia, Schengen, or Japan visa can enter Oman visa-free for up to 14 days. That policy predates the CEPA, but the trade pact reinforces Oman's positioning as a convenient Gulf stopover — particularly now that Dubai and Doha face higher transit risk due to Hormuz proximity.

Bilateral trade between India and Oman stood at $11.18 billion in FY26. More than 6,000 Indian enterprises already operate in the country. Annual remittances from Indian workers in Oman are estimated at roughly $2 billion.

## The bigger picture

India has been on a trade-pact sprint. The Oman CEPA follows agreements with the UAE, Australia, and EFTA. But the Hormuz dimension gives this one an urgency the others lacked. As one OilPrice.com analysis put it, the deal "is turning out to be more fortuitous than initially expected."

For Indian Americans with family or business ties to the Gulf — and that is a substantial share of the NRI population — the practical effect is a more resilient corridor between India and its second-largest trade region. Flights, goods, and professionals all move a little easier when the infrastructure does not depend on a single contested waterway."""
    },

    # ─── Article 2: IATA / Global Aviation Crisis ──────────────────
    {
        "id": art2_id,
        "headline": "Airlines Face Their Worst Crisis Since COVID — and NRI Summer Fares Will Show It",
        "subheadline": "Moody's has downgraded the global airline sector to negative. Profits may fall 35 percent this year. And the industry's biggest summit opens Friday in Rio with no clear answers.",
        "slug": art2_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying India-US routes this summer face higher fares, fewer flight options, and longer travel times as airlines cut unprofitable routes and pass fuel costs to passengers. Air India's outgoing CEO has said some routes are now 'harder to justify.'",
        "tags": ["travel", "airlines", "iata", "fuel-crisis", "iran-war", "fares", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/global-airline-chiefs-confront-iran-war-fuel-shock-industry-summit-2026-06-04/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3370001-global-airlines-grapple-with-crisis"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/india-jet-fuel-prices-unchanged-june-2026/"},
            {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/national/airlines-aid-fund-jet-fuel-price-cap-iran-war-impact/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": img2_url,
        "image_caption": "An aviation fuel truck on an airport tarmac — jet fuel costs have more than doubled since the Iran war began",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When 370 airline CEOs gather in Rio de Janeiro this Friday for the International Air Transport Association's annual summit, the mood will be nothing like last year's. In 2025, IATA projected a record $41 billion in global airline profits for 2026. That number is now heading for a 35 percent haircut, courtesy of a war that has rewritten the economics of flying.

## The damage so far

The Iran conflict has hit aviation on three fronts simultaneously. Jet fuel prices have more than doubled as fighting near the Strait of Hormuz disrupts oil flows. Middle Eastern airspace closures — compounded by Pakistan's ban on Indian overflights — have forced airlines to reroute long-haul flights, adding hours and fuel burn. And global passenger traffic contracted in April for the first time since the post-pandemic recovery, led by a sharp drop at Middle Eastern carriers.

Moody's Ratings cut its global airline sector outlook from stable to negative last week, warning that fuel costs and Hormuz disruptions would "materially reduce" operating profit this year. The agency expects profits to recover in 2027 — but only if the conflict does not escalate further.

## What Indian carriers are doing

India's airlines are responding with a mix of route cuts, government support, and fleet reshuffling.

IndiGo, India's largest carrier, has suspended eight international routes effective July 1, including Hong Kong, Shanghai, and four Southeast Asian leisure destinations. It has also cut planned domestic flights for June and July by 7 to 10 percent. The airline reported a fourth-quarter loss driven largely by higher fuel costs.

Air India has been more aggressive, slashing 22 percent of domestic flights for the same period and reducing services on several international routes. Outgoing CEO Campbell Wilson said publicly that higher fuel prices and airspace closures are making some routes "harder to justify."

The Indian government stepped in this week with a ₹10,000 crore ($1.04 billion) price stabilisation fund for aviation turbine fuel, capping the domestic rate at ₹75.60 per litre. State-owned refiners have also held jet fuel prices unchanged for June. The relief is welcome but comes with strings — participating airlines must buy fuel exclusively from government oil marketing companies for up to three years.

## What NRI travelers should expect

The ripple effects for Indian Americans booking summer travel are already visible.

**Higher fares.** Airlines globally are passing fuel costs to passengers. On competitive India-US trunk routes like SFO-DEL and JFK-BOM, fare increases have been somewhat contained by competition. On thinner routes — particularly those routed over the Middle East — the increases are steeper.

**Fewer options.** IndiGo's Southeast Asian cuts reduce connection options for NRIs who used Bangkok, Kuala Lumpur, or Ho Chi Minh City as transit points to reach southern and eastern India. Air India's domestic cuts mean onward connections within India are also thinner.

**Longer flights.** The combined effect of Iranian and Pakistani airspace closures adds 60 to 90 minutes on many westbound routes from India to Europe and the Americas. Airlines absorb some of that cost; passengers absorb the rest in cabin time.

**Gulf hub pressure.** Emirates and Qatar Airways — the two carriers that built their businesses on connecting Asia with the West through Gulf hubs — are under particular strain. Emirates' international market share from India has dropped to about 8.3 percent, down sharply from its peak. If the Gulf carriers pull back further, NRIs lose some of their most popular one-stop options.

## The outlook

IATA's summit runs June 6 through 8. The big number to watch is the association's updated profit forecast, expected on the opening day. Discussions will also cover deepening aircraft delivery delays from Boeing and Airbus, sustainable aviation fuel mandates that look increasingly unrealistic under current fuel economics, and whether airlines should start hedging fuel more aggressively.

For NRI families planning India trips this summer, the practical advice is straightforward: book early, be flexible on dates, and brace for fares that reflect an industry in genuine distress."""
    },

    # ─── Article 3: IndiGo Manchester ──────────────────────────────
    {
        "id": art3_id,
        "headline": "IndiGo's Manchester Experiment Dies at 13 Months — and the UK's Indian Diaspora Loses Its Cheapest Link Home",
        "subheadline": "India's largest airline will stop flying its only European routes on August 31, returning its leased Dreamliners to Norse Atlantic as fuel costs and airspace restrictions make the maths impossible.",
        "slug": art3_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "The UK is home to roughly 1.8 million people of Indian origin. Manchester and the North of England had their first direct budget flights to India from July 2025 — IndiGo's Delhi and Mumbai services starting at £290 one-way. Those routes are now dying, leaving London as the only UK city with direct India connections and pushing Northern NRIs back to expensive Air India and Virgin Atlantic options through Heathrow.",
        "tags": ["travel", "indigo", "manchester", "uk", "airlines", "nri", "europe"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/indias-indigo-cuts-six-international-routes-amid-rising-costs-airspace-restrictions-2026-06-04/"},
            {"name": "The Sun", "url": "https://www.thesun.co.uk/travel/35145679/budget-airline-axe-flights-uk-year-launching/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indigo-to-suspend-manchester-flights-from-august-31-amid-rising-costs-and-airspace-constraints/article69628342.ece"},
            {"name": "LiveMint", "url": "https://www.livemint.com/industry/aviation/indigo-pips-air-india-again-on-overseas-routes-as-west-asia-crisis-weighs-11717458234567.html"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": img3_url,
        "image_caption": "An IndiGo Airbus A320neo — the airline's long-haul ambitions used leased Boeing 787-9 Dreamliners from Norse Atlantic",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """IndiGo launched its Manchester services in July 2025 with the swagger of an airline that had just become India's largest international carrier. Three weekly flights to Delhi, four to Mumbai, all on Boeing 787-9 Dreamliners leased from Norse Atlantic Airways. One-way fares started at £290 — roughly half of what Air India charged from Heathrow. For the hundreds of thousands of Indian-origin families across Northern England, the Midlands, and Scotland, it was the first time they could fly home without routing through London.

Thirteen months later, IndiGo is pulling the plug. Both Manchester routes end on August 31.

## What went wrong

The short answer is the Iran War. The longer answer involves three compounding pressures that turned promising economics into an impossible equation.

**Airspace closures.** IndiGo's Manchester flights were routed over the Middle East. Iranian airspace has been closed to most commercial traffic since the conflict began, and Pakistan's reciprocal ban on Indian carriers — imposed during last year's military tensions — remains in force. The result is a dramatic increase in flight time: what should be a 9-hour journey now takes significantly longer on circuitous southern or northern routes.

**Fuel costs.** Aviation turbine fuel prices have more than doubled since mid-2025. Longer routes burn more fuel. IndiGo SVP Abhijit Dasgupta put it bluntly: "Longer flying times due to airspace constraints combined with dramatically escalating costs compelled us to take the decision."

**Leased aircraft.** IndiGo does not own wide-body aircraft. The six Boeing 787-9 Dreamliners operating the Manchester routes were damp-leased from Norse Atlantic, a strategy designed to "fast-track connectivity to high-potential long-haul destinations" while IndiGo waited for its own Airbus A350 deliveries. Leasing costs are fixed; when revenues cannot cover the fuel penalty, the maths collapse.

Norse Atlantic has confirmed it will redeploy the returned aircraft on winter Europe-to-Thailand routes.

## What it means for UK NRIs

The loss is real and specific. Manchester Airport serves a massive catchment area — roughly 22 million people across the North of England, the Midlands, and Scotland. For Indian families in Birmingham, Leeds, Manchester, Glasgow, and Liverpool, IndiGo was the only affordable direct option.

With the routes gone, the alternatives are familiar and expensive:

- **Air India** from Heathrow to Delhi and Mumbai — higher fares, and a train or domestic flight to London first
- **Virgin Atlantic** from Heathrow to Delhi and Mumbai — premium product, premium price
- **Emirates, Qatar, Etihad** via Gulf hubs — one-stop, but the Gulf transit itself now carries schedule and security risk

No other carrier has announced plans to serve Manchester-India. The city loses its only direct link to the subcontinent.

## IndiGo's long-haul ambitions are not dead

Despite the retreat, IndiGo insists it has not given up on Europe. Dasgupta called the Manchester decision "temporary" and expressed confidence the airline would return "at the earliest viable opportunity."

The airline has its own Airbus A350s on order, which would replace the expensive leasing arrangement. And IndiGo's broader international performance is strong: it carried 0.87 million international passengers in April alone, edging out the Air India group and claiming the top spot among Indian carriers on international routes for the third time in four months.

But the A350 deliveries are still some way off, and the conditions that killed Manchester — fuel costs, airspace closures, currency volatility — show no sign of easing. The Iran War is not ending. Pakistan's airspace ban is not lifting. And IndiGo's ambition to offer low-cost long-haul from India to Europe will have to wait for a world that, right now, does not exist.

## The pattern

IndiGo is not alone in retreating from international routes. This week the airline also suspended flights to Hong Kong, Shanghai, and four Southeast Asian destinations effective July 1. Air India has cut 22 percent of domestic flights and reduced international services. The entire Indian aviation sector is in retrenchment mode.

For the 1.8 million people of Indian origin in the UK — many of whom booked IndiGo precisely because it was cheap and direct — the message is uncomfortable: the budget link to India was a product of a world where fuel was affordable and airspace was open. That world may not come back soon."""
    },
]


# ── Insert ─────────────────────────────────────────────────────────
print("\n🚀 Inserting articles...\n")

for art in articles:
    try:
        # Verify image URL exists
        if art["image_url"]:
            sb_post("p2_articles", art)
            print(f"✅ {art['slug']}")
        else:
            print(f"⚠️  {art['slug']}: No image, inserting without image")
            art.pop("image_url", None)
            art.pop("image_caption", None)
            art.pop("image_attribution", None)
            sb_post("p2_articles", art)
            print(f"✅ {art['slug']} (no image)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n✅ Travel writer run complete.")
