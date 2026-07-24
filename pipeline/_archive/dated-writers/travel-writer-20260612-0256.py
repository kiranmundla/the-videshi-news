#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-12 batch (3 articles)."""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── ENV ──────────────────────────────────────────────────────────────
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
UPLOAD_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG."""
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def download_and_upload(image_url, slug):
    """Download image via curl, compress, upload to Supabase storage."""
    import subprocess, time
    print(f"  Downloading: {image_url[:80]}...")
    tmp_path = f"/tmp/img_{slug}.tmp"
    result = subprocess.run(
        ["curl", "-sS", "-o", tmp_path, "-w", "%{http_code}",
         "-H", "User-Agent: TheVideshi/1.0 (thevideshi.com)", image_url],
        capture_output=True, text=True, timeout=60
    )
    code = result.stdout.strip()
    if code != "200":
        print(f"  ❌ Download failed: HTTP {code}")
        return None

    raw = open(tmp_path, "rb").read()
    os.unlink(tmp_path)
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return None

    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    filename = f"{slug}.jpg"
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"

    # Try upsert
    up_headers = {**UPLOAD_HEADERS, "Content-Type": "image/jpeg", "x-upsert": "true"}
    resp = requests.post(upload_url, headers=up_headers, data=compressed, timeout=30)
    if resp.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✅ Uploaded: {public_url}")
        return public_url
    else:
        print(f"  ❌ Upload failed: {resp.status_code} {resp.text[:200]}")
        return None


# ── IMAGE SOURCING ───────────────────────────────────────────────────
print("=" * 60)
print("IMAGE SOURCING")
print("=" * 60)

# Article 1: Varanasi Airport
slug1 = make_slug("air-india-easy-connect-varanasi-hub-spoke-nri")
img1_url = "https://upload.wikimedia.org/wikipedia/commons/9/95/The_facade_of_Varanasi_Airport%2C_Varanasi.jpg"
print(f"\n[Article 1] Varanasi Airport image:")
final_img1 = download_and_upload(img1_url, slug1)

import time; time.sleep(3)

# Article 2: Air India A350
slug2 = make_slug("air-india-a350-delhi-new-york-newark-premium-nri")
img2_url = "https://upload.wikimedia.org/wikipedia/commons/5/56/Air_India_A350.png"
print(f"\n[Article 2] Air India A350 image:")
final_img2 = download_and_upload(img2_url, slug2)

time.sleep(3)

# Article 3: Kashmir Rail (Srinagar Railway Station — Kashmir-specific)
slug3 = make_slug("kashmir-vande-bharat-rail-tourism-srinagar-nri")
img3_url = "https://upload.wikimedia.org/wikipedia/commons/4/4f/Srinagar_railway_station.jpg"
print(f"\n[Article 3] Srinagar railway station image:")
final_img3 = download_and_upload(img3_url, slug3)


# ── ARTICLES ─────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

articles = [
    # ── ARTICLE 1 ────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's Easy Connect Launches From Varanasi — and NRIs From Tier-2 Cities Get a Direct Line to the World",
        "subheadline": "Starting June 25, passengers from Varanasi can clear immigration and check bags at home before connecting through Delhi to 17 international destinations. More cities are next.",
        "slug": slug1,
        "category": "travel",
        "vertical": "aviation",
        "is_editorial": False,
        "diaspora_angle": "Millions of NRIs trace their roots to tier-2 cities like Varanasi, Lucknow, and Patna — Easy Connect eliminates the chaotic Delhi transit that has long been the worst part of flying home.",
        "tags": ["travel", "airlines", "air-india", "aviation", "tier-2-cities"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel + Leisure Asia", "url": "https://www.travelandleisureasia.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "AviationA2Z", "url": "https://www.aviationa2z.com/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": final_img1 or "",
        "image_caption": "The terminal at Lal Bahadur Shastri International Airport in Varanasi, now India's first Easy Connect city",
        "image_attribution": "Wikimedia Commons",
        "body": """Anyone who has flown from a smaller Indian city to the US, UK, or the Gulf knows the drill. You land in Delhi, collect your bags, drag them across terminals, stand in a two-hour immigration queue, re-check everything, and sprint to your international gate. It is the worst stretch of any NRI's journey home — and Air India just eliminated it.

Starting June 25, Air India will operate daily "Easy Connect" flight AI1111 from Varanasi to Delhi under the Indian government's new hub-and-spoke aviation model. The key change: passengers clear immigration and check their bags through to their final international destination at Varanasi's Lal Bahadur Shastri Airport. When they land in Delhi, they transit as international passengers — no second check-in, no immigration queue, no baggage carousel.

## What Easy Connect Actually Means

Under the old system, a family flying Varanasi to London would book two separate tickets: a domestic leg to Delhi and an international leg onward. At Delhi's Terminal 3, they would collect luggage, cross to international departures, and start the process from scratch. For elderly parents traveling alone — a scenario every NRI knows well — this was a genuine ordeal.

Easy Connect collapses that into a single itinerary. The model mirrors how major hubs like Singapore Changi and Dubai International have operated for decades, but applies it domestically for the first time in India. Civil Aviation Minister Ram Mohan Naidu called it "a significant step towards making India a global aviation hub."

The schedule has been designed so that onward connections from Delhi depart within four hours of the Varanasi arrival. From Delhi, passengers can reach 17 international destinations including London Heathrow, Frankfurt, Milan, Rome, Zurich, Singapore, Kuala Lumpur, Phuket, Manila, Riyadh, and Dubai.

## Why NRIs Should Care

India has roughly 4.5 million citizens living in the US alone, and a large share of them — particularly from Uttar Pradesh, Bihar, and Jharkhand — route through Delhi on every trip home. Varanasi is the first spoke city, but Air India has confirmed a phased rollout to more tier-2 and tier-3 cities in the coming months. The structure is designed to eventually connect dozens of smaller airports to Delhi and Mumbai hubs.

For the estimated 800,000-plus NRIs with roots in eastern Uttar Pradesh, the immediate benefit is obvious. But the broader signal matters more: India's aviation infrastructure is finally catching up to its diaspora's travel patterns. Destinations like Lucknow, Patna, Jaipur, and Ahmedabad could follow, each one removing a pain point that has frustrated NRI travelers for years.

## The Competitive Picture

Air India's move also sharpens its fight against Gulf carriers. Emirates, Qatar Airways, and Etihad have dominated the India-US corridor partly because their hubs offer smoother connections than Delhi or Mumbai. If Easy Connect works as designed — single check-in, fast transit, no re-screening — it neutralizes one of the Gulf carriers' biggest advantages for passengers originating from smaller Indian cities.

The timing aligns with Air India's broader Tata-era transformation. The airline recently deployed A350 widebodies on US routes, opened its first international lounge at SFO, and merged loyalty programs across Air India Express. Easy Connect is the infrastructure layer that ties all of it together.

## What to Watch

The model's success hinges on execution. Immigration facilities at Varanasi's airport need to be staffed and equipped for international processing. Baggage systems must handle through-checked luggage without losing it in transit. And the four-hour connection window at Delhi needs to hold even when domestic flights run late.

If Air India gets this right, Easy Connect could reshape how NRIs plan trips to India. Instead of routing through Delhi or Mumbai and adding a separate domestic booking, they could fly directly from their hometown — with their bags and paperwork already sorted. That is not a marginal improvement. For millions of diaspora travelers, it is the difference between a 24-hour journey and a tolerable one.""",
    },
    # ── ARTICLE 2 ────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Puts Its A350 on the Delhi–New York Route — and 60% of US Flights Now Have New Cabins",
        "subheadline": "The Tata-owned carrier is deploying its newest widebody on the busiest NRI corridor, with redesigned seats, new IFE systems, and upgraded soft products across all classes.",
        "slug": slug2,
        "category": "travel",
        "vertical": "aviation",
        "is_editorial": False,
        "diaspora_angle": "For the 4.5 million Indian Americans who fly the India-US corridor every year, Air India's cabin upgrade addresses the single biggest complaint about the national carrier: the inflight experience.",
        "tags": ["travel", "airlines", "air-india", "a350", "premium-travel"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/"},
            {"name": "Air India Press Release", "url": "https://www.airindia.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": final_img2 or "",
        "image_caption": "An Air India Airbus A350 in the carrier's new livery, now deployed on Delhi–New York and Newark routes",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the running joke among NRIs was that Air India's planes were older than their parents' marriage. The seats were threadbare, the entertainment screens flickered, and the food trays bore the scars of a thousand reheated curries. That was the price of nostalgia — you flew Air India because it was yours, not because it was good.

That calculus is changing. Air India has begun deploying its Airbus A350-900 fleet on the Delhi–New York JFK and Delhi–Newark routes, marking the most significant cabin upgrade on the airline's busiest US corridors. With this move, 60 percent of all Air India flights to the United States now feature either brand-new or fully refurbished cabin interiors.

## What's on the A350

The A350 is Airbus's newest widebody, and Air India's configuration reflects its ambitions. The aircraft features redesigned seats across all three classes, new inflight entertainment systems with larger screens and modern content libraries, and upgraded "soft products" — airline-speak for the blankets, amenity kits, cutlery, and meal presentation that shape how premium a flight actually feels.

Air India has positioned the A350 as its flagship international product. The aircraft's composite fuselage is quieter than older metal-bodied jets, its cabin pressure is equivalent to a lower altitude (reducing fatigue on long-haul flights), and its larger windows let in more natural light. For a 15-hour Delhi-to-Newark flight, these are not trivial details.

## The US Network Picture

Air India currently operates 51 weekly flights to five US cities: New York JFK, Newark, Washington DC, Chicago, and San Francisco. The A350 deployment on the New York and Newark routes addresses the two highest-volume corridors.

On Mumbai routes, the airline flies a three-class Boeing 777-300ER with eight first-class suites, 40 full-flat business-class beds, and 280 economy seats — all with updated IFE systems. Between the A350 and the refurbished 777s, Air India's US product is now materially different from what it was even 18 months ago.

The Delhi–Toronto corridor, which booking data shows carried 574,000 round-trip passengers last year (the largest India–North America market by volume), is served by Air Canada's 787-9 with a block time of up to 17 hours and five minutes. Air India doesn't fly Toronto yet, but the A350's range makes it a natural candidate for future expansion.

## Why NRIs Should Notice

The India-US air travel market is fiercely competitive. Emirates routes through Dubai. Qatar Airways routes through Doha. Singapore Airlines offers its trademark service via Changi. For years, these carriers pulled NRI travelers away from Air India not with lower fares but with a better experience — lie-flat beds, lounge access, and flights where the IFE actually worked.

Air India's A350 deployment is a direct response. The airline is betting that NRIs will return to the national carrier if the product matches the competition. Combined with the recently opened Maharaja Lounge at SFO (the airline's first international lounge), the expanded Maharaja Club loyalty program covering Air India Express, and the new Easy Connect hub-and-spoke model launching this month, the Tata Group is building a coherent premium proposition for the first time since acquiring the airline in January 2022.

## The Remaining Gap

Hardware alone does not fix an airline. Air India still struggles with punctuality, call-center responsiveness, and ground handling at Indian airports. The Delhi T3 experience remains chaotic compared to Doha's Hamad or Singapore's Changi. And the airline's premium fares are now closer to Gulf carrier pricing, which means NRIs will judge it on the same standard.

But for the millions of Indian Americans who fly this corridor annually — for weddings, festivals, family emergencies, and the simple pull of home — an Air India that feels modern is an Air India worth trying again. The A350 makes that argument in steel and carbon fiber. Whether the rest of the experience follows is the Tata Group's $400-billion question.""",
    },
    # ── ARTICLE 3 ────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Kashmir by Rail Is Finally Real — and NRIs Planning a Trip This Year Need to Know What's Changed",
        "subheadline": "The Jammu–Srinagar Vande Bharat now runs 20 coaches and four daily services. A new Anantnag stop opens South Kashmir. And when Srinagar Airport closes in October, trains will be the only way in.",
        "slug": slug3,
        "category": "travel",
        "vertical": "tourism",
        "is_editorial": False,
        "diaspora_angle": "Kashmir sits at the top of every NRI's India bucket list, but getting there has always been the hard part — limited flights, expensive peak-season fares, and weather cancellations. Rail changes that equation entirely.",
        "tags": ["travel", "kashmir", "vande-bharat", "indian-railways", "tourism"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Metro Rail News", "url": "https://metrorailnews.in/"},
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": final_img3 or "",
        "image_caption": "Srinagar Railway Station, now connected to Jammu by Vande Bharat Express in under five hours",
        "image_attribution": "Wikimedia Commons",
        "body": """Every NRI has said it at some family gathering: "Next trip, we're definitely going to Kashmir." And every time, the logistics kill the plan. Flights to Srinagar are expensive in peak season, frequently canceled in winter, and fully booked months ahead during summer. The only alternative was a grueling 10-hour drive from Jammu through mountain roads that test both your car's suspension and your family's patience.

That alternative just got dramatically better. The Jammu–Srinagar Vande Bharat Express, India's semi-high-speed train service, has expanded to 20 coaches and four daily services, cutting the journey to 4 hours and 50 minutes. And this week, Railway Minister Ashwini Vaishnaw approved a new halt at Anantnag, opening direct rail access to South Kashmir for the first time.

## What the Vande Bharat Offers

The train initially launched as an 8-coach service between Katra (the base for Vaishno Devi pilgrims) and Srinagar in June 2025. By April 2026, rising demand pushed the Railway Ministry to extend the route to Jammu Tawi and more than double capacity to 20 coaches. Commercial operations on the full Jammu–Srinagar route began May 2, 2026.

The Vande Bharat is not a regular Indian train. The semi-high-speed EMU (electric multiple unit) features reclining chairs, onboard Wi-Fi, GPS-based passenger information, automatic doors, and a ride quality that is closer to European regional rail than anything Indian Railways has offered before. For NRIs accustomed to Amtrak's Acela or the UK's Avanti, the Vande Bharat will feel familiar — and for a fraction of the price.

Four services now operate daily: two pairs running as trains 26401/26402 and 26404/26403. The schedule has been calibrated to work with morning arrivals in Srinagar and evening returns to Jammu, making day-trip patterns feasible for travelers based in either city.

## The Anantnag Stop Changes the Map

On June 10, Kashmir Chief Minister Omar Abdullah met Railway Minister Vaishnaw in New Delhi and requested a Vande Bharat halt at Anantnag. The approval came the same day. Anantnag is the gateway to South Kashmir — Pahalgam, Kokernag, Achabal gardens, and the Amarnath pilgrimage route all fan out from there.

Until now, travelers to South Kashmir had to reach Srinagar first, then backtrack by road. The Anantnag stop creates a direct rail entry point, saving two to three hours of road travel each way. For NRI families planning a Kashmir trip that covers both Srinagar's Dal Lake and Pahalgam's alpine meadows, this is a meaningful upgrade.

## The October Wildcard

Here is the detail most NRIs will miss: Srinagar International Airport is scheduled to close from October 1 to October 15 for essential runway maintenance. Chief Minister Abdullah flagged this during the same meeting, noting that the closure falls in peak tourist season — coinciding with Durga Puja holidays and early autumn, when the chinar trees turn Kashmir into a photographer's paradise.

During the closure, there will be no commercial flights in or out of Srinagar. The Vande Bharat and conventional rail services will be the only mechanized way into the Valley. The Railway Ministry has committed to increasing train frequency during this window, but details are still being worked out.

For NRIs planning an October trip to Kashmir — and many do, because fall colors in the Valley rival anything in New England — this means booking train tickets early. The 20-coach Vande Bharat has roughly 1,100 seats per service, and four daily services means around 4,400 seats per day in each direction. That will fill fast when the airport goes dark.

## The Bigger Picture

India has invested heavily in Kashmir's rail infrastructure over the past decade, including the engineering marvel of the Chenab Bridge (the world's highest rail bridge) and the ongoing extension of the rail line toward Baramulla. The Vande Bharat service is the most visible result of that investment, and the one most likely to change how tourists — including the diaspora — experience Kashmir.

For NRIs, the math is straightforward. A Delhi-to-Jammu flight takes 90 minutes and costs ₹4,000–8,000. The Jammu-to-Srinagar Vande Bharat adds under five hours for a few hundred rupees. Total door-to-door time from Delhi to Srinagar: about eight hours. That is competitive with a direct flight that costs three to four times more and cancels twice as often.

Kashmir by rail is no longer aspirational. It is operational, affordable, and expanding. The only question is whether NRIs will stop saying "next time" and actually book.""",
    },
]

for art in articles:
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting anyway")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline'][:60]}...\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
