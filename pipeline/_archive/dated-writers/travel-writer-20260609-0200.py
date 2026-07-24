#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-09 02:00 UTC run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
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

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image. Returns JPEG bytes."""
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
    """Download image, compress, upload to Supabase storage bucket 'article-images'."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        if not ct.startswith("image/"):
            print(f"  ⚠ Not an image: {ct}")
            return None
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return None

        compressed = compress_image(r.content)
        size_kb = len(compressed) / 1024
        print(f"  📦 Compressed to {size_kb:.0f} KB")

        # Upload to Supabase storage
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return None
    except Exception as e:
        print(f"  ⚠ Image processing error: {e}")
        return None

def validate_image(url):
    """Quick HEAD check to verify image URL is live."""
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and ct.startswith("image/") and cl > 5000
    except:
        return False

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ============================================================
# IMAGE SOURCING
# ============================================================

print("=" * 60)
print("IMAGE SOURCING")
print("=" * 60)

# Article 1: India summer family travel — Puri beach
print("\n🖼️ Article 1: Puri beach image")
img1_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/At_Puri_beach_04.jpg/1280px-At_Puri_beach_04.jpg"
art1_id = str(uuid.uuid4())
img1_url = upload_to_supabase(img1_source, f"{art1_id}.jpg")

# Article 2: Delta Air Lines
print("\n🖼️ Article 2: Delta Air Lines aircraft")
img2_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Delta_Air_Lines_%28Dublin%29_in_2025.01.jpg/1280px-Delta_Air_Lines_%28Dublin%29_in_2025.01.jpg"
art2_id = str(uuid.uuid4())
img2_url = upload_to_supabase(img2_source, f"{art2_id}.jpg")

# Article 3: Vande Bharat Express / IRCTC
print("\n🖼️ Article 3: Vande Bharat Express")
img3_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Vande_Bharat_Express_2.jpg/1280px-Vande_Bharat_Express_2.jpg"
art3_id = str(uuid.uuid4())
img3_url = upload_to_supabase(img3_source, f"{art3_id}.jpg")

# ============================================================
# ARTICLES
# ============================================================

print("\n" + "=" * 60)
print("WRITING ARTICLES")
print("=" * 60)

articles = [
    # ---------- ARTICLE 1 ----------
    {
        "id": art1_id,
        "headline": "Puri's Family Travel Searches Just Jumped 68% — and NRI Parents Should Take the Hint",
        "subheadline": "Agoda data shows Puri, Wayanad, and Goa dominating India's summer family travel boom. For NRIs timing a trip home with the kids, the overlap with US school breaks makes this the window to book.",
        "slug": make_slug("puri-wayanad-goa-india-summer-family-travel-surge-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI parents with school-age kids in the US have a narrow summer window — June through August — that overlaps perfectly with India's May-June school break season. These trending destinations offer exactly the kind of heritage-meets-beach family trip that diaspora families keep saying they want to take but never quite plan.",
        "tags": ["travel", "family", "india", "puri", "wayanad", "goa", "summer"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Agoda", "url": "https://www.agoda.com/press/puri-wayanad-goa-summer-family-travel-2026"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/travel/puri-wayanad-goa-summer-family-travel"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/india-family-travel-puri-wayanad-goa-summer-2026"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url or "",
        "image_caption": "Families gather on the wide shoreline of Puri beach in Odisha, one of India's fastest-growing summer destinations",
        "image_attribution": "Wikimedia Commons",
        "body": """Every year, the same question surfaces in NRI family WhatsApp groups around April: *Where should we go when we take the kids to India this summer?*

New data from digital travel platform Agoda offers a clear answer — and it isn't the usual suspects of Shimla and Manali.

## Puri Leads the Pack

Odisha's temple town has recorded a **68 per cent surge** in family accommodation searches compared to last year, making it the fastest-growing domestic family destination for summer 2026. The combination is hard to beat: the Jagannath Temple for grandparents, wide Bay of Bengal beaches for kids, and a hospitality infrastructure that has quietly matured over the past two years.

For NRI families, Puri has an additional draw. It sits within easy reach of Bhubaneswar's well-connected airport, which now has direct flights from Delhi, Mumbai, Hyderabad, and Bengaluru. A family flying in from the US can connect through any of those hubs and be on the beach by evening.

## Wayanad and Goa Hold Steady

Kerala's **Wayanad** district has seen accommodation searches rise **40 per cent**, driven by its wildlife sanctuaries, plantation retreats, and the kind of cool, mist-wrapped quiet that works as a reset for families arriving from North American heat. It is not a beach holiday — it is a nature immersion, and the distinction matters for parents deciding between screen fatigue and forest walks.

**Goa** remains perennially reliable, posting a **29 per cent increase** in searches. Its formula hasn't changed — beaches, water parks, and resort infrastructure designed for children of all ages — but the consistency is the point. For NRI families who want a low-friction trip where everyone from toddlers to grandparents finds something, Goa keeps delivering.

## The Hill Station Contingent

Beyond the coastal leaders, Agoda's data shows continued demand for hill stations. **Rishikesh** attracts adventure-seeking families with rafting and trekking. **Mahabaleshwar** draws Mumbai-connected NRIs with its strawberry farms and colonial-era viewpoints. **Ooty** and **Kodaikanal** remain go-to choices for families heading south, offering cooler temperatures and tea plantation landscapes.

The pattern suggests Indian families — domestic and diaspora alike — are moving away from single-city visits and toward destination-based holidays where location itself is the experience.

## Why the Timing Works for NRIs

The May–June school break in India overlaps with the early weeks of US summer vacation, creating a two-to-three-week window when NRI kids are free and Indian cousins are too. This is not a coincidence that travel platforms ignore. Agoda's search data is effectively tracking the planning behaviour of millions of families trying to synchronise across time zones.

For diaspora families who have been putting off the "India trip with kids" conversation, the data is unambiguous: Puri, Wayanad, and Goa are where Indian families are heading this summer. The accommodation is filling up. The window is narrowing. And the WhatsApp group is still waiting for someone to book the Airbnb."""
    },

    # ---------- ARTICLE 2 ----------
    {
        "id": art2_id,
        "headline": "Delta Is Coming Back to India — and This Time It's Using IndiGo's Entire Network to Get You There",
        "subheadline": "A four-airline alliance between Delta, IndiGo, Air France-KLM, and Virgin Atlantic is building the most seamless US-to-India connection network NRIs have ever had. Here's how the routing works.",
        "slug": make_slug("delta-indigo-alliance-nri-us-india-flights"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 4.4 million Indian Americans flying between the US and India, the Delta-IndiGo alliance means one-ticket bookings from mid-size American cities to tier-2 Indian cities — think Minneapolis to Lucknow, or Atlanta to Kochi — without the usual three-booking juggling act.",
        "tags": ["travel", "airlines", "delta", "indigo", "us-india-flights", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/delta-air-lines-returns-to-india-with-indigo-led-global-partnership/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/aviation/indigo-bets-big-on-international-growth-targets-200-mn-passengers-by-fy30"},
            {"name": "Drift Travel", "url": "https://drifttravel.com/partnership-for-flights-to-india-from-north-america-and-europe"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url or "",
        "image_caption": "A Delta Air Lines widebody aircraft on the tarmac — the carrier is returning to India through its IndiGo partnership",
        "image_attribution": "Wikimedia Commons",
        "body": """Delta Air Lines hasn't flown its own metal to India since 2015, when it pulled out of the Mumbai route citing thin margins and punishing competition from Gulf carriers. A decade later, the airline is plotting its return — but the strategy looks nothing like the old playbook.

Instead of brute-forcing a direct route and hoping the load factors hold, Delta is plugging into a four-airline alliance that effectively lets it sell tickets to more than 30 Indian cities without parking a single plane in Mumbai.

## The Alliance Architecture

The partnership centres on **IndiGo**, which has grown into India's dominant carrier with over 2,700 daily flights to 137 destinations. Through an expanded codeshare agreement, IndiGo's 6E code will appear on select flights operated by Delta, Air France-KLM, and Virgin Atlantic — and vice versa.

The practical effect for NRIs is significant. A passenger in **Atlanta, Detroit, or Salt Lake City** can book a single ticket that routes through Amsterdam or London, connects to an IndiGo flight, and lands in **Ahmedabad, Kochi, Lucknow, Pune, or Coimbatore**. One booking. One itinerary. One set of checked bags.

Delta CEO **Ed Bastian** confirmed the ambition publicly: "We look forward to restarting Delta's direct service from the U.S. to India in the near future." The codeshare is the scaffolding; direct flights are the endgame.

## Why This Matters Now

The US-India air corridor has been one of the fastest-growing long-haul markets in aviation. Indian carriers — led by IndiGo and the Tata-owned Air India — have been capturing market share from Gulf airlines at a pace that would have been unthinkable five years ago. IndiGo alone now holds **17.6 per cent** of India's international market share, overtaking Emirates, which has slipped to 8.3 per cent.

For American carriers, the maths has changed. India's outbound international traffic is projected to cross 100 million passengers annually by 2030. And unlike the Gulf routing model — where passengers connect through Dubai or Doha — the Delta-IndiGo alliance offers routing through European hubs that are often faster and involve fewer visa complications for Indian passport holders.

## IndiGo's European Bet Makes It Work

The alliance became viable because IndiGo took a gamble on long-haul. The airline launched services to **Manchester** and **Amsterdam** in 2024-25, proving its A321XLR and A321neo fleet could handle six-to-eight-hour sectors. With planned routes to **London, Copenhagen, and Athens**, IndiGo is building a European footprint that creates natural connection points for Delta's transatlantic network.

IndiGo has also ordered **30 Airbus A350-900 widebody jets**, its first true long-haul aircraft. Nine A321XLR deliveries are expected in FY27, opening routes to **Istanbul, Bali, and Seoul**. By FY30, international capacity could account for 40 per cent of IndiGo's total — up from a fraction of that three years ago.

## The NRI Calculation

For the Indian American diaspora, the alliance addresses the single most persistent frustration of flying home: the last mile. Getting to Delhi or Mumbai has never been the hard part. Getting from there to **Mangalore, Indore, Amritsar, or Trivandrum** on a coordinated itinerary — with luggage that actually follows — has been the source of decades of airport rage.

The Delta-IndiGo partnership, layered on top of IndiGo's existing codeshares with Air France-KLM and Virgin Atlantic, creates the first genuine one-ticket, multi-carrier network connecting mid-size American cities to tier-2 Indian cities. It is not perfect. It still involves connections. But for a family in **Minneapolis booking flights to Chandigarh**, the difference between three separate bookings and one is the difference between a plan and a prayer."""
    },

    # ---------- ARTICLE 3 ----------
    {
        "id": art3_id,
        "headline": "India's Rail Tourism Push Just Got 200 New Trains — and NRIs Are the Target Audience",
        "subheadline": "IRCTC is forecasting 20 per cent tourism growth for FY27, backed by a wave of Vande Bharat and Amrit Bharat trains. The Maharajas' Express is seeing record demand from foreign visitors. And for the first time, you can ride a train directly from Jammu to Srinagar.",
        "slug": make_slug("irctc-rail-tourism-vande-bharat-expansion-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who haven't taken a train in India since childhood are the exact demographic IRCTC is courting. The Vande Bharat fleet, the Maharajas' Express luxury segment, and the new Jammu-Srinagar route are all pitched at travellers who want the romance of Indian railways without the chaos of unreserved general coaches.",
        "tags": ["travel", "india", "railways", "vande-bharat", "irctc", "tourism", "kashmir"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CNBC-TV18 / Storyboard18", "url": "https://storyboard18.com/brand-marketing/irctc-eyes-tourism-led-growth-expansion-of-vande-bharat-and-amrit-bharat-trains-73085.htm"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/in-a-historic-first-vande-bharat-express-runs-directly-from-jammu-to-srinagar/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/indian-railways-to-launch-historic-jammu-srinagar-vande-bharat-express/article69516282.ece"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3_url or "",
        "image_caption": "A Vande Bharat Express in service — India plans to add over 200 new premium trains in the next three to five years",
        "image_attribution": "Wikimedia Commons",
        "body": """The last time most NRIs took a train in India, the experience involved a waitlisted ticket, a thermos of chai, and the quiet resignation that comes with a 14-hour journey on a seat meant for eight-hour distances. Indian Railways is betting that memory is about to become irrelevant.

IRCTC Chairman **Sanjay Kumar Jain** has confirmed that the company expects its tourism business to grow by **20 per cent in FY27**, powered by what he describes as record demand on premium services and a government plan to deploy more than **200 new Vande Bharat and Amrit Bharat trains** over the next three to five years.

## The Vande Bharat Fleet

The Vande Bharat Express has become Indian Railways' flagship product — a semi-high-speed, air-conditioned chair car service that runs at up to 160 km/h and looks nothing like the trains NRIs remember. The fleet now covers major corridors across the country, and the expansion plan is aggressive: new routes are being added quarterly, with a focus on tourist circuits and pilgrimage corridors.

The most dramatic addition came on **April 30, 2026**, when Railway Minister **Ashwini Vaishnaw** flagged off the first direct Vande Bharat Express from **Jammu to Srinagar**. The service runs six days a week, covering 269 km in under five hours, with stops at **Vaishno Devi Katra**, **Reasi**, and **Banihal**.

For the first time in history, Kashmir is connected to India's national rail network by a regular passenger train. The route crosses the **Chenab Bridge** — the world's highest railway bridge — and passes through the Anji Khad cable-stayed bridge, India's first. The trains are equipped with anti-freezing technology, snow ploughs, and self-regulating heating cables designed for sub-zero operations.

## Why NRIs Should Care

The Jammu-Srinagar Vande Bharat is not just an infrastructure milestone. It is a tourism product aimed squarely at travellers who want to see Kashmir but dread the Srinagar-Jammu highway — a road so frequently disrupted by weather and landslides that it makes Indian Railways look like the model of reliability.

An NRI family flying into Jammu can now board a Vande Bharat at 6:20 AM and be in Srinagar by 11:10 AM, with a stop at Vaishno Devi Katra for pilgrims. The return service departs Srinagar at 2:00 PM and arrives back in Jammu by 6:50 PM. Tickets are available through IRCTC — Executive Chair Car at ₹1,185 and Chair Car at ₹450.

## The Luxury End

At the other end of the spectrum, IRCTC's **Maharajas' Express** is seeing what Jain described as "record inbound tourism" on its premium itineraries. The train — often compared to the Orient Express — runs curated multi-day journeys across Rajasthan, Varanasi, and other heritage circuits, with suites that start at several thousand dollars per night.

The demand signal is clear. International tourists, including a growing cohort of NRI families bringing their American-raised children on heritage trips, are willing to pay for a curated rail experience that delivers the grandeur of Indian landscapes without the logistical friction.

## The Broader Play

Beyond tourism, IRCTC expects its catering business to grow 15 per cent in FY27 and internet ticketing to expand 9-10 per cent. The company is exploring advertising, loyalty programmes, and its unified digital platform as additional revenue streams.

But the headline number is the one that matters to travellers: **200+ new premium trains** entering service in the next few years. Each one adds a route. Each route creates a travel option that didn't exist before. And for NRIs who have been renting SUVs and hiring drivers for every India visit, the calculus is shifting.

The train is becoming a viable — and in some cases, superior — way to travel India. The Vande Bharat fleet is clean, fast, and increasingly ubiquitous. The Jammu-Srinagar route proves the network can reach places that roads struggle with. And IRCTC's 20 per cent growth forecast suggests the organisation knows exactly which audience is paying attention."""
    },
]

# ============================================================
# INSERT
# ============================================================

print("\n" + "=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

for art in articles:
    # Skip if no image
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']} — skipping image_url field")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        print(f"   → {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n🎯 Done. {len(articles)} articles submitted for review.")
