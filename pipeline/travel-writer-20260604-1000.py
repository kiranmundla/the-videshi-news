#!/usr/bin/env python3
"""Travel writer — 2026-06-04 10:00 UTC run. Two articles."""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Env ──────────────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace/.env.supabase"]:
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
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage bucket article-images."""
    print(f"  Downloading: {img_url[:80]}...")
    r = requests.get(img_url, headers=UA, timeout=30)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return None
    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r2 = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    r2.raise_for_status()
    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✅ Uploaded: {public_url}")
    return public_url


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 1: Kedarnath Helicopter Char Dham
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

art1_id = str(uuid.uuid4())
art1_slug = make_slug("kedarnath-helicopter-char-dham-fuel-crisis-nri-pilgrimage")

art1_body = """It is peak Char Dham season, and the helicopters that ferry pilgrims to Kedarnath are caught between surging demand and economics that no longer add up.

Eight operators run shuttle services from Guptakashi, Phata, and Sersi to the Kedarnath helipad — a five-minute flight that replaces a brutal 16-kilometre trek at 3,583 metres. Ticket prices, locked in by tender months ago, range from ₹6,300 to ₹12,700 per seat depending on the route. But after an April spike in aviation turbine fuel (ATF) prices, the Business Aircraft Operators Association is now asking the Uttarakhand government for a fuel surcharge, warning that "continued fare caps are making operations commercially unsustainable on a day-to-day basis."

The government has capped ATF price hikes at 25 per cent for scheduled airlines. Helicopter companies — classified as non-scheduled operators — get no such relief. Oil companies rolled back ATF prices by 25 per cent from June 1, but operators say the damage was already done across April and May, the busiest weeks of the season.

## Why NRIs should care

The Char Dham helicopter yatra has quietly become the default pilgrimage format for the Indian American diaspora. The full circuit — Yamunotri, Gangotri, Kedarnath, Badrinath — takes 10 to 12 days by road, with two serious treks and unpredictable mountain weather. By helicopter, it collapses to five or six days out of Dehradun's Sahastradhara helipad.

For NRI families flying in for two or three weeks, that arithmetic is decisive. So is the physical reality: many book the helicopter specifically for elderly parents who cannot manage the Kedarnath trek. Packages from UCADA-approved operators like Heritage Aviation, Aryan Aviation, and Himalayan Heli run ₹1.95 lakh to ₹2.5 lakh per person for the full Char Dham circuit, inclusive of VIP darshan, premium hotels, all meals, and ground transfers.

The Do Dham option — Kedarnath and Badrinath only — starts around ₹75,000 to ₹95,000 per person. The Kedarnath shuttle alone, booked through IRCTC's heliyatra portal, costs ₹7,500 to ₹10,000 for a round trip.

## What the fuel fight means for prices

Charter flights — the full Char Dham packages — have already absorbed partial cost increases. Operators told The Hindu BusinessLine that they have raised prices for roughly 25 per cent of charter passengers, though many bookings made months earlier could not be revised. Shuttle services, whose rates are government-approved and pre-set, have no such flexibility.

If the Uttarakhand government approves a fuel surcharge, shuttle fares could rise by ₹500 to ₹1,500 per seat — not catastrophic, but enough to add up for a family of four. NRIs booking through travel agents for later in the season should confirm whether the quoted price includes any surcharge, and whether cancellation terms have changed.

## Booking tips for NRIs planning this season

The 2026 Char Dham temples opened between April 19 and 24. Peak helicopter season runs through mid-June, then resumes in September and October after the monsoon. For NRIs who have not yet booked:

- **Book the IRCTC shuttle** at heliyatra.irctc.co.in — this is the only authorised portal for Kedarnath helicopter shuttles. Fraudulent lookalike sites are a documented problem; always verify the URL.
- **Weight limits matter.** Each passenger is capped at 75 kilograms including 5 kg of baggage. This is strictly enforced.
- **September and October** offer better value: fewer crowds, clearer mountain views, and potentially lower charter prices as operators try to fill seats before the November closures.
- **Register first.** All Char Dham pilgrims must obtain a Yatra Registration Number at registrationandtouristcare.uk.gov.in before booking helicopter tickets.

The season runs until the temples close — typically late October or early November, depending on snowfall. The fuel surcharge question should be resolved within weeks. In the meantime, the helicopters keep flying, the queues keep forming, and Kedarnath remains one of the most logistically complex — and spiritually resonant — pilgrimages an NRI family can plan."""

print("=" * 60)
print("ARTICLE 1: Kedarnath Helicopter")
print("=" * 60)

# Image: Kedarnath Temple at Dawn from Commons (beautiful, specific)
art1_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Kedarnath_Temple_at_Dawn_-_OCT_2014.jpg/1200px-Kedarnath_Temple_at_Dawn_-_OCT_2014.jpg",
    f"{art1_slug}.jpg",
)

art1 = {
    "id": art1_id,
    "headline": "Kedarnath's Helicopters Are Flying Into a Fuel Crisis — and NRI Pilgrims Will Feel It",
    "subheadline": "Shuttle operators want a surcharge, charter prices are already creeping up, and the peak Char Dham season is half over. Here's what NRIs booking the helicopter yatra need to know.",
    "slug": art1_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The Char Dham helicopter yatra has become the default pilgrimage for NRI families — especially those with elderly parents who cannot trek. Fuel surcharges and price uncertainty hit this demographic directly.",
    "tags": ["travel", "pilgrimage", "char-dham", "kedarnath", "helicopter", "uttarakhand"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/national/helicopter-operators-seek-fuel-surcharge-for-shuttle-service/article69641234.ece"},
        {"name": "IRCTC Heli Yatra Portal", "url": "https://heliyatra.irctc.co.in"},
        {"name": "Pilgrim Packages", "url": "https://www.pilgrimpackages.com/upload/blog/image-5CD2ZPSWMJZW5DO2.jpg"},
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": art1_img_url or "",
    "image_caption": "Kedarnath Temple at dawn, nestled in the Himalayan peaks of Uttarakhand",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body,
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ARTICLE 2: India's Cruise Revolution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

art2_id = str(uuid.uuid4())
art2_slug = make_slug("india-cruise-revolution-cordelia-vizag-southeast-asia-nri")

art2_body = """India had one cruise ship operating commercially from its ports at the start of 2025. By the end of 2027, it will have three — and the routes they are opening will matter more to NRI families than any new airline seat.

Cordelia Cruises, the country's only domestic cruise operator, confirmed plans to triple its fleet within two years. Its flagship Empress already runs the Mumbai–Goa–Lakshadweep circuit that has become a staple for Indian families. This year, two expansions change the map entirely.

## Vizag goes international

On July 15, Cordelia will launch India's first international cruise departure from the east coast. A 14-day itinerary will sail from Visakhapatnam to Chennai (two-day stopover), then onwards to Phuket, Langkawi, Kuala Lumpur, and Singapore. The route is designed around visa simplicity: Indian passport holders need no visa for Thailand or Malaysia, and Singapore offers visa-on-arrival.

For NRIs visiting family in Andhra Pradesh, Telangana, or Tamil Nadu, this is a genuine option. Fly into Hyderabad or Chennai, spend a week with family, then board a cruise that doubles as a Southeast Asian holiday — all without a single visa application.

From Kochi, Cordelia is introducing five-night cruises to Malé and Colombo, alongside shorter weekend high-seas departures. From Chennai, five-night itineraries to Sri Lanka and Visakhapatnam round out the new domestic network.

## The fleet is growing fast

Cordelia Sky, a vessel transferring from Norwegian Cruise Line, enters service from Mumbai in October 2026. It will take over the high-demand Mumbai routes — Goa, Lakshadweep, high-seas weekends — while Empress pivots to the new international itineraries. A third ship is expected to join by late 2027.

Meanwhile, Resorts World Cruises has repeatedly signalled an India entry with Resorts World One (the 75,000-gross-ton former SuperStar Virgo), originally planned for March 2025, now pushed to 2026 as the company integrates a third vessel into its global operations. When it arrives, it will bring a second operator and a capacity surge to Mumbai's International Cruise Terminal.

## What NRIs should know about pricing

Cordelia's current rates set the baseline. A two-night Mumbai–Goa cruise starts at ₹35,000 per person for an interior cabin, rising to ₹90,000+ for a suite. The five-night Mumbai–Goa–Lakshadweep route — widely considered the best-value itinerary — runs ₹75,000 to ₹2.5 lakh depending on cabin class. Weekend sailings and school-holiday periods push prices up 15 to 40 per cent.

The all-inclusive label is misleading. Cabin, buffet meals, and onboard entertainment are included. Specialty restaurants, the spa, shore excursions, and the casino (which opens only in international waters) all cost extra. Budget an additional ₹10,000 to ₹25,000 per person for a realistic total.

For context: a comparable Maldives trip runs two to three times more. A Royal Caribbean or Norwegian cruise out of Singapore, which many NRIs book, costs roughly the same in dollars but involves international airfare from India.

## The Lakshadweep factor

Lakshadweep has emerged as Cordelia's marquee destination, and for good reason. The archipelago's turquoise lagoons and untouched beaches rival the Maldives, but access has historically been limited to flights to Agatti or permits for island stays. The cruise route — typically stopping at Kavaratti, Kalpeni, and Kadmat islands — bypasses most of that friction.

One caveat: monsoon weather (July through September) can cancel island stops. Passengers on shoulder-season sailings have reported two of three island visits scrubbed due to rough seas, with only partial refunds. The October-to-March window is safest.

## Why this matters for the diaspora

NRIs visiting India increasingly look for experiences to layer onto family trips — a few days in Goa, a Rajasthan circuit, a Kerala houseboat. A two-to-five-night cruise out of Mumbai, Kochi, or now Vizag fits that pattern at a price point that competes with domestic flights and hotel stays.

The infrastructure is catching up. Mumbai's International Cruise Terminal, which opened in 2024, can handle ships up to 300 metres long. Chennai and Visakhapatnam are investing in port-side passenger facilities. The government's Sagarmala programme has earmarked cruise tourism as a growth vertical.

India's cruise industry is still a fraction of what Southeast Asia or the Caribbean offers. But for the first time, NRIs visiting home can add a legitimate cruise holiday without leaving the country — or dealing with a single visa stamp."""

print()
print("=" * 60)
print("ARTICLE 2: India Cruise Revolution")
print("=" * 60)

# Image: Agatti Island, Lakshadweep from Wikimedia Commons
art2_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Agatti_Island%2C_Lakshadweep%2C_India_20160325-_DSC1718.jpg/1200px-Agatti_Island%2C_Lakshadweep%2C_India_20160325-_DSC1718.jpg",
    f"{art2_slug}.jpg",
)

art2 = {
    "id": art2_id,
    "headline": "India's Cruise Industry Is Tripling Its Fleet — and NRIs Visiting Home Can Finally Sail",
    "subheadline": "Cordelia Cruises is adding two ships, launching India's first east-coast international sailings to Southeast Asia, and turning Lakshadweep into a Maldives alternative. Here's what it costs and how to book.",
    "slug": art2_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs visiting family in India can now layer a 2-5 night cruise onto their trip — out of Mumbai, Kochi, or Vizag — at prices that compete with domestic flights and hotels, with no extra visa needed.",
    "tags": ["travel", "cruise", "cordelia", "lakshadweep", "southeast-asia", "vizag", "mumbai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Cruise Arabia", "url": "https://cruise-arabia.com/cordelia-cruises-expands-fleet/"},
        {"name": "Travel Weekly Asia", "url": "https://www.travelweekly-asia.com/Travel-News/Cruise-Travel/India-east-coast-international-cruise"},
        {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/cordelia-international-cruises-vizag-july/"},
        {"name": "Trip Cabinet", "url": "https://tripcabinet.com/cruise-from-india-2026-cost/"},
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "image_url": art2_img_url or "",
    "image_caption": "Agatti Island in Lakshadweep, one of Cordelia Cruises' marquee destinations",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body,
}


# ── Publish ──────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    if not art.get("image_url"):
        print(f"⚠ {art['slug']}: No image URL, publishing without image")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
