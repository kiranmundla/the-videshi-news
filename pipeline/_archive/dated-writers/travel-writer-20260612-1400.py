#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-12 14:00 PDT run.
Two fresh travel articles:
  1. Soaring Airfares Hit NRI Summer Travel (Iran/Hormuz fuel crisis)
  2. El Niño Threatens India's Monsoon — What NRIs Planning Summer Trips Should Know
"""

import json, os, uuid, re, io, time, subprocess, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ---------- ENV ----------
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.pexels"]:
    if env_file.exists():
        for line in env_file.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

SB_URL  = os.environ["SUPABASE_URL"]
SB_KEY  = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS  = os.environ.get("PEXELS_API_KEY", "")
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
    return slug[:70].rstrip('-') + "-20260612"

# ---------- IMAGE HELPERS ----------

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

def download_and_upload(source_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL."""
    print(f"  Downloading: {source_url[:100]}...")
    for attempt in range(4):
        r = requests.get(source_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code == 429:
            wait = (attempt + 1) * 5
            print(f"  ⚠ Rate limited, waiting {wait}s (attempt {attempt+1}/4)...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        print(f"  ❌ Failed after 4 attempts (429)")
        return None
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping")
        return None

    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw):,} → {len(compressed):,} bytes")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if ur.status_code not in (200, 201):
        print(f"  ⚠ Upload failed: {ur.status_code} {ur.text[:200]}")
        return None

    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✅ Uploaded: {public_url}")
    return public_url


def fetch_pexels_image(query):
    """Fetch a Pexels image URL using curl (urllib gets 403)."""
    if not PEXELS:
        print("  ⚠ No PEXELS_API_KEY")
        return None
    try:
        cmd = [
            "curl", "-sS", "-H", f"Authorization: {PEXELS}",
            f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5&orientation=landscape"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        # Pick the first photo with decent resolution
        for p in photos:
            src = p.get("src", {})
            w = p.get("width", 0)
            if w >= 1000:
                # Use the large2x version (~1200px) for good quality
                url = src.get("large2x") or src.get("large") or src.get("original")
                if url:
                    print(f"  Pexels hit: {p.get('alt', '')[:60]} ({w}px)")
                    return url
        print(f"  ⚠ Pexels: no suitable image for '{query}'")
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None


# ---------- SOURCE IMAGES ----------
print("=== Sourcing images ===")

# Article 1: Soaring airfares — airport/airplane image
print("\n--- Article 1: Airfares ---")
img1_url = None
# Try Pexels with specific travel-related query
pexels_src = fetch_pexels_image("airport departure board flights")
if pexels_src:
    img1_url = download_and_upload(pexels_src, "soaring-airfares-nri-summer-travel-hormuz-20260612.jpg")
if not img1_url:
    # Fallback: Wikimedia Commons airplane
    img1_url = download_and_upload(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Air_India_Boeing_787-8_Dreamliner_VT-ANQ_Heathrow.jpg/1280px-Air_India_Boeing_787-8_Dreamliner_VT-ANQ_Heathrow.jpg",
        "soaring-airfares-nri-summer-travel-hormuz-20260612.jpg"
    )

# Article 2: El Niño monsoon — monsoon rain India
print("\n--- Article 2: El Niño Monsoon ---")
img2_url = None
pexels_src2 = fetch_pexels_image("monsoon rain India")
if pexels_src2:
    img2_url = download_and_upload(pexels_src2, "el-nino-monsoon-nri-summer-india-travel-20260612.jpg")
if not img2_url:
    # Fallback: Wikimedia Commons monsoon image
    img2_url = download_and_upload(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/India_southwest_summer_monsoon_onset_map_en.svg/1200px-India_southwest_summer_monsoon_onset_map_en.svg.png",
        "el-nino-monsoon-nri-summer-india-travel-20260612.jpg"
    )


# ---------- ARTICLES ----------
print("\n=== Building articles ===")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Soaring Airfares Are Crushing NRI Summer Travel Plans — and the Hormuz Crisis Is Only Part of the Problem",
        "subheadline": "Jet fuel prices have doubled since the Strait of Hormuz closure, pushing US-India round trips past $1,800 and forcing Indian Americans to rethink summer visits home. Here is what is driving the surge and how to navigate it.",
        "slug": make_slug("soaring-airfares-nri-summer-travel-hormuz-crisis"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans face the steepest summer airfares in a decade as the Iran-US conflict disrupts Gulf carrier routes and pushes jet fuel costs to historic highs — directly impacting the annual trip home.",
        "tags": ["travel", "airfares", "airlines", "iran", "hormuz", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Kayak Travel Trends", "url": "https://www.kayak.com/news/travel-trends/"},
            {"name": "IATA", "url": "https://www.iata.org/en/pressroom/2026-releases/2026-06-03-01/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/"},
            {"name": "The Street", "url": "https://www.thestreet.com/travel/airfares-summer-2026"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/europe-airfares-cheaper-war-hormuz/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url or "",
        "image_caption": "Airport departure boards tell the story this summer — fewer flights, higher fares, longer detours",
        "image_attribution": "Pexels",
        "body": """Every June, millions of Indian Americans begin the annual ritual of booking summer flights to India. This year, the sticker shock is brutal.

Round-trip fares from the United States to Delhi and Mumbai have surged past $1,800 on most routes — a 30 to 45 percent jump from the same period last year. Flights through the Gulf, historically the cheapest and most popular corridor for NRI travel, have been hit hardest. The culprit is not seasonal demand or airline greed alone. It is a geopolitical crisis that has redrawn the economics of international aviation: the ongoing Iran-US conflict and the effective closure of the Strait of Hormuz.

## The Hormuz Effect on Jet Fuel

The Strait of Hormuz, the narrow waterway between Iran and Oman, carries roughly 20 percent of the world's oil supply. Since hostilities escalated in February, tanker traffic through the strait has slowed to a trickle. The impact on jet fuel — which accounts for 25 to 30 percent of an airline's operating costs — has been immediate and severe. Jet fuel prices have climbed from roughly $85 per barrel to between $160 and $230 per barrel in some markets, depending on the refinery and the route.

Airlines have responded in the only way they can: by passing costs to passengers. IATA, the global airline trade body, cut its 2026 industry profit forecast by half in early June, projecting just $23 billion in net profits against $40 billion forecast at the start of the year. American Airlines has already announced cancellations on select August and September routes, citing "unsustainable fuel economics." Delta has trimmed frequencies on several transatlantic routes. United is reportedly reviewing its fall schedule.

## How NRI Routes Are Specifically Hit

The US-India air corridor runs overwhelmingly through three hubs: Dubai (Emirates), Doha (Qatar Airways), and Abu Dhabi (Etihad). All three carriers operate in the immediate geographic shadow of the Hormuz conflict. While commercial aviation has not been directly targeted, the rerouting of tanker traffic, increased insurance premiums for Gulf-based operations, and the knock-on effects of regional instability have pushed operating costs for these carriers well above pre-crisis levels.

Direct flights on Air India and United — the two carriers offering nonstop US-India service — have seen fares rise as well, though less dramatically. The problem is capacity: there are simply not enough nonstop seats to absorb demand if Gulf carriers pull back further. Air India's new A350 fleet has added seats on Delhi-New York and Delhi-San Francisco, but the airline's total nonstop capacity between the US and India remains a fraction of what Emirates and Qatar Airways carry through their hubs.

Kayak's latest data tells the story in numbers. Average round-trip fares from US cities to London — a bellwether for transatlantic pricing — have jumped 45 percent year-over-year, from $786 to $1,100. Paris is up 30 percent. Domestic US fares have climbed from $293 to $383. The India corridor, which is longer and more fuel-intensive, has seen proportionally larger increases.

## The Behavioral Shift

The fare shock is not just a pricing inconvenience — it is changing travel behavior. An Expedia survey released this week found that 63 percent of American travelers are now prioritizing domestic trips over international ones, the highest share since the pandemic recovery. For NRIs, "domestic" often means a road trip to a national park rather than the annual flight to Hyderabad.

Families that typically book three or four tickets for a summer India visit are doing the math and finding that the total cost — airfare plus internal travel plus gifts plus the inevitable family wedding contribution — now comfortably exceeds $12,000. Some are postponing to Diwali in the hope that fares will ease. Others are shortening trips from three weeks to ten days. A few are splitting the family: one parent flies with the kids while the other stays home.

## Where the Deals Are (and Are Not)

Europe, counterintuitively, has become cheaper for NRIs who are flexible about their summer plans. Ryanair hedged its fuel costs at pre-crisis prices and is offering aggressive fares on European routes. Barron's reported this week that summer flights within Europe are actually down year-over-year, creating an unusual window for NRI families who might consider a European vacation as a substitute — or a stopover — for the India trip.

Within the US-India corridor, the cheapest options right now involve creative routing. Turkish Airlines through Istanbul, Ethiopian Airlines through Addis Ababa, and even Cathay Pacific through Hong Kong are pricing below the Gulf carriers on some routes. The trade-off is longer travel times and less convenient connections, but for a family of four, the savings can exceed $2,000.

## What Comes Next

The fuel crisis is unlikely to resolve quickly. Even if a Hormuz ceasefire materializes — and the diplomatic signals remain mixed — it will take months for tanker traffic to normalize and fuel prices to recede. Airlines typically hedge fuel purchases six to twelve months ahead, meaning that fares set for summer 2026 are already baked in.

IATA's chief economist Marie Owens Thomsen warned that the current environment is "the most challenging for airline economics since the pandemic." For NRIs, the practical translation is blunt: book early, be flexible on routing, consider off-peak travel windows like late August or early September, and watch for fare sales from carriers with strong fuel hedges.

The annual trip home has always been expensive. This year, it is a financial event that requires planning, compromise, and a willingness to endure a 22-hour itinerary through Addis Ababa if it saves $500 a seat. The Hormuz crisis did not create the NRI airfare problem — it exposed how fragile the economics of long-haul travel have always been."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "El Niño Is Back and India's Monsoon Is Already Behind — What NRIs Planning Summer Trips Should Know",
        "subheadline": "The India Meteorological Department confirms a moderate El Niño is forming during peak monsoon season. With rainfall already 27 percent below normal in June's first ten days, NRIs headed to India this summer face disrupted flights, flooded roads, and unpredictable weather across the subcontinent.",
        "slug": make_slug("el-nino-monsoon-nri-india-summer-travel-disruptions"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs planning summer India trips — especially to monsoon-heavy destinations like Kerala, Goa, or the Northeast — face heightened uncertainty as El Niño threatens erratic rainfall, flight cancellations, and landslide risks through September.",
        "tags": ["travel", "monsoon", "el-nino", "india", "weather", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-monsoon-rainfall-below-normal/"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/el-nino-iod-monsoon-2026/"},
            {"name": "US Climate Prediction Center (NOAA)", "url": "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url or "",
        "image_caption": "Monsoon rains in India — this year's season faces El Niño headwinds that could disrupt travel plans across the subcontinent",
        "image_attribution": "Pexels",
        "body": """The monsoon arrived in Kerala on June 4 — three days later than the statistical norm — and it has been underwhelming ever since. In the first ten days of June, rainfall across India has been 26.5 percent below the long-period average. Central and northern India, which depend on the monsoon's northward march for agriculture and water supply, have received even less. The reason is a phenomenon that NRIs planning summer India trips need to understand, because it will shape their travel experience from now through September: El Niño is back.

## What El Niño Means for the Monsoon

El Niño is a periodic warming of sea surface temperatures in the central and eastern Pacific Ocean. When it occurs during India's monsoon season (June to September), it typically suppresses rainfall by weakening the atmospheric pressure gradients that pull moisture-laden winds from the Indian Ocean onto the subcontinent.

The numbers are now official. The Niño 3.4 index — the key indicator — crossed the +0.80°C threshold on June 7, confirming that a moderate El Niño event is underway. The US Climate Prediction Center expects it to strengthen through the summer. The India Meteorological Department has adjusted its seasonal forecast to 90 percent of the long-period average, which in plain terms means India will likely receive noticeably less rain than a normal monsoon year.

This does not mean drought everywhere. El Niño's effects are uneven. Southern India and parts of the Northeast may still receive adequate rainfall, especially if a positive Indian Ocean Dipole (IOD) develops by August — the IOD currently sits at a neutral -0.34°C but forecasts suggest it could turn positive and partially offset El Niño's suppression. But for the vast swath of central and northern India — the Gangetic plain, Rajasthan, Madhya Pradesh, parts of Maharashtra — the outlook is drier and more erratic than usual.

## The NRI Travel Calculus

Every summer, roughly two to three million Indian Americans travel to India, with the peak falling between mid-June and August — directly overlapping with monsoon season. For most, the monsoon is a background inconvenience: a delayed flight here, a flooded road there. In an El Niño year, the inconvenience escalates.

**Flights.** Mumbai's Chhatrapati Shivaji International Airport is notorious for monsoon-season disruptions. In a normal year, heavy rains cause diversions and delays that cascade through domestic and international schedules. An El Niño monsoon is paradoxically worse for aviation — not because of more rain, but because of more unpredictable rain. Instead of steady, predictable precipitation that pilots and ground crews can plan around, El Niño tends to produce erratic bursts: sudden downpours followed by dry spells, with less warning and more severe individual storm events.

Delhi's Indira Gandhi Airport and Kolkata's Netaji Subhas Bose Airport face similar risks, though for different reasons. Reduced overall rainfall can mean that when storms do hit, urban drainage systems — designed for steady monsoon flow — are overwhelmed by concentrated bursts.

**Road travel.** NRIs who rent cars or take trains between cities face heightened landslide and flooding risk on mountain routes. The highways connecting Delhi to Shimla, Manali, and Rishikesh — popular NRI summer escapes — are particularly vulnerable during erratic monsoon years. Uttarakhand and Himachal Pradesh have already issued early advisories for the hill season.

**Destinations.** Kerala's backwaters, Goa's beaches, and the Northeast's forests are the monsoon-season destinations that NRIs most frequently build into their India trips. All three regions are monsoon-dependent, and their appeal during the rainy season — lush greenery, fewer crowds, lower hotel rates — depends on rain arriving in a predictable pattern. An El Niño year scrambles that pattern. Kerala could see delayed heavy rains in August and September rather than the gradual June-July onset that makes houseboat trips possible. Goa may experience dry spells that thin out the waterfalls and rivers that draw monsoon tourists.

## The Silver Lining: A Different Kind of Monsoon Trip

Not all El Niño effects are negative for travelers. Rajasthan, which becomes sweltering and largely unvisitable during a normal monsoon, may actually be more accessible this year if rainfall stays below average. The same applies to Gujarat and parts of Maharashtra's Deccan plateau. NRIs who typically avoid these regions in summer might find June through August surprisingly tolerable.

Ladakh, which sits in a rain shadow and depends on snowmelt rather than monsoon rain, is essentially El Niño-proof. The region has seen a surge in NRI visitors over the past three years, and this summer — with improved road access via the Atal Tunnel and expanded flight service to Leh — is expected to be its busiest yet.

## Crop Prices and the Kitchen Table

There is a second-order effect that NRIs visiting India will notice: food prices. India's agriculture depends on monsoon rainfall for roughly 50 percent of its irrigation. A below-normal monsoon typically drives up prices for rice, pulses, vegetables, and cooking oils — the staples of every Indian kitchen. If you are visiting family, expect to hear about dal and onion prices. If you are dining out, expect modest menu price increases at restaurants that source locally.

India's Finance Ministry flagged the inflation risk in a June report, noting that the combination of El Niño, elevated global crude prices from the Hormuz crisis, and reduced kharif (summer crop) sowing could push food inflation above the Reserve Bank of India's comfort zone by September.

## Practical Advice for NRI Travelers

**Book flexible tickets.** If your trip is between July and September, pay the extra for refundable or changeable bookings. Monsoon-season disruptions are a when, not an if.

**Carry travel insurance that covers weather delays.** Most basic policies do not. Look for policies that include trip interruption for weather events.

**Monitor IMD forecasts weekly.** The IMD's extended-range outlook, updated every Thursday, gives a 14-day rainfall forecast by region. It is freely available at mausam.imd.gov.in and is more granular than any international weather app.

**Build buffer days into your itinerary.** If you are connecting through Mumbai during monsoon season, do not schedule a tight same-day connection to a domestic flight. Allow at least one overnight buffer.

**Consider September.** If the IOD turns positive as forecast, late monsoon rainfall in August and September could be more reliable than June and July. NRIs with flexible schedules might find that the tail end of monsoon season offers better weather, lower fares, and the green landscapes they came for.

El Niño does not cancel summer travel to India. But it changes the risk profile in ways that NRIs — many of whom grew up with the monsoon and assume they know what to expect — should take seriously. This is not the monsoon you remember from childhood visits. It is a climate-disrupted version, and planning for it requires more attention than a decade ago."""
    },
]


# ---------- INSERT ----------
print("\n=== Inserting articles ===")
for art in articles:
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting anyway")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted: {art['slug']}")
        print(f"   ID: {art['id']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n=== Done! ===")
print(f"Articles inserted with status='review', is_editorial=false, category='travel', vertical='travel'")
