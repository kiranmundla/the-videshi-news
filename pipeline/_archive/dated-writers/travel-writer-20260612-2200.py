#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-12 22:00 UTC run"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# --- Env ---
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

# --- Image helpers ---
from PIL import Image

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

import time

def upload_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase article-images bucket."""
    print(f"  Downloading: {img_url[:80]}...")
    for attempt in range(3):
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
        if r.status_code == 429:
            wait = 5 * (attempt + 1)
            print(f"  ⚠ Rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        break
    else:
        r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return img_url

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
    if r2.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✅ Uploaded: {public_url}")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({r2.status_code}): {r2.text[:200]}")
        return img_url

# --- Image sourcing ---
print("=== Sourcing images ===")

# Article 1: US National Parks — Yosemite Half Dome from Wikipedia
art1_id = str(uuid.uuid4())
art1_slug = make_slug("us-national-parks-drop-reservations-summer-nri-families")
art1_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Half_Dome_with_Eastern_Yosemite_Valley_%2850MP%29.jpg/1280px-Half_Dome_with_Eastern_Yosemite_Valley_%2850MP%29.jpg",
    f"{art1_id}.jpg"
)

# Article 2: Sri Lanka Free ETA — Sigiriya from Wikimedia Commons (thumbnail)
art2_id = str(uuid.uuid4())
art2_slug = make_slug("sri-lanka-free-visa-indians-nri-side-trip")
time.sleep(3)  # Avoid Wikimedia rate limit
art2_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Sigiriya_%28141688197%29.jpeg/1280px-Sigiriya_%28141688197%29.jpeg",
    f"{art2_id}.jpg"
)

# Article 3: South Africa ETA — Cape Town from Wikipedia
art3_id = str(uuid.uuid4())
art3_slug = make_slug("south-africa-digital-eta-indians-safari-nri")
time.sleep(3)  # Avoid Wikimedia rate limit
art3_img_url = upload_to_supabase(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Camps_bay_%2853460319478%29_%28cropped%29.jpg/1280px-Camps_bay_%2853460319478%29_%28cropped%29.jpg",
    f"{art3_id}.jpg"
)

print("\n=== Writing articles ===")

articles = [
    # ── Article 1: US National Parks ──
    {
        "id": art1_id,
        "headline": "America's Best National Parks Just Dropped Their Reservation Rules — and NRI Families Should Book Now",
        "subheadline": "Yosemite, Glacier, Arches, and Mount Rainier have all scrapped timed entry for summer 2026. Free entry this Saturday, June 14, sweetens the deal.",
        "slug": art1_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian American families make up one of the largest demographics visiting US national parks in summer — and the reservation headache was the top reason many skipped it.",
        "tags": ["travel", "national parks", "road trips", "family", "summer"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "National Park Service", "url": "https://www.nps.gov/orgs/1207/national-park-service-expands-access-for-summer-2026-while-maintaining-safety-at-high-visitation-parks.htm"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/news/national-park-reservation-requirements-2026/"},
            {"name": "Detroit Free Press", "url": "https://www.freep.com/story/news/local/michigan/2026/06/08/national-parks-free-entry-days-flag-day/84091345007/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_img_url,
        "image_caption": "Half Dome towers over eastern Yosemite Valley in California",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the biggest obstacle to a spontaneous national park road trip wasn't the drive — it was the reservation system. Families who didn't secure timed entry slots months in advance found themselves turned away at the gate at Yosemite, Glacier, Arches, and Mount Rainier, four of America's most iconic parks.

That era is over. The National Park Service has confirmed that all four parks have scrapped their timed entry reservation systems for summer 2026. And for Indian American families planning a summer road trip, the timing could not be better.

## What Changed

The NPS announced that **Yosemite**, **Arches**, and **Glacier** will not require advance reservations this summer, including during peak months. **Mount Rainier** followed weeks later, making it the fourth major park to drop the system. Only **Rocky Mountain National Park** in Colorado will retain timed entry, running from late May through mid-October.

The parks will instead rely on real-time traffic management — temporary diversions when parking fills up, extra seasonal staff at high-use trailheads, and shuttle systems at bottleneck corridors like Glacier's Logan Pass, where private vehicle parking is now capped at three hours starting July 1.

"Our national parks belong to the American people, and our priority is keeping them open and accessible," said Kevin Lilly, the Acting Assistant Secretary for Fish, Wildlife and Parks, in the NPS announcement.

## Why This Matters to Indian American Families

National park road trips are a rite of passage for NRI families, particularly during the June-August window when school is out and extended family visits often overlap. But the reservation system created a two-tier experience: those who planned months ahead got in, and those who decided on a whim — the way most family vacations actually happen — were shut out.

The old system was especially punishing for multigenerational trips, where coordinating dates across households often meant booking windows had already closed. With reservations gone at four of the five most popular parks, a family in the Bay Area can now drive to Yosemite on a Friday morning without checking an app first.

## Free Entry This Saturday

There is an immediate incentive to act. **Saturday, June 14**, is a free entry day across all 400+ National Park Service sites — no $35 vehicle fee at Yosemite, no $30 per car at Arches, no $25 at Mount Rainier. The NPS has designated Flag Day as a fee-free day for 2026.

The remaining free entry days this year: **July 3-5** (Independence Day weekend), **August 25** (NPS's 110th birthday), **September 17** (Constitution Day), and **October 27** (Theodore Roosevelt's birthday).

## Park-by-Park: What NRI Families Should Know

**Yosemite** (California): No reservations needed, including for the February-March firefall period. The park saw 4.28 million visitors in 2025. Arrive early on weekends — Yosemite Valley parking fills by 10 AM in July. The Mariposa Grove of giant sequoias and Glacier Point are best visited midweek.

**Glacier** (Montana): Vehicle reservations are gone park-wide, but Logan Pass parking is limited to three hours starting July 1. If you are planning the Highline Trail or Granite Park Chalet, take the shuttle. Glacier recorded 3.14 million visitors last year.

**Arches** (Utah): No timed entry at all. The park is also an International Dark Sky Park, so visiting after sunset for stargazing is encouraged. Pair it with nearby Canyonlands for a two-park weekend.

**Mount Rainier** (Washington): The timed entry system at select entrances, in place since 2024, is gone. Paradise and Sunrise areas are the main draws — both fill early on clear summer days.

## Planning Tips

The NPS recorded over 323 million recreation visits in 2025, with 26 parks setting records. Dropping reservations does not mean dropping crowds. Pack patience alongside the trail mix.

For NRI families combining a park visit with a trip to see relatives, the logistics have never been simpler: no booking windows to track, no slots to lose, and five chances this summer to skip the entrance fee entirely. The parks are open. The only reservation you need now is the hotel."""
    },

    # ── Article 2: Sri Lanka Free ETA ──
    {
        "id": art2_id,
        "headline": "Sri Lanka Just Made Its Tourist Visa Free for Indians — and NRIs Should Add a Side Trip",
        "subheadline": "A 30-day free ETA with double entry went live on May 25. For NRIs flying home this summer, Colombo is now a two-hour detour with zero visa cost.",
        "slug": art2_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying to Chennai, Kochi, or Bangalore this summer can add a Sri Lanka side trip for the cost of a short-haul flight — the visa is now free.",
        "tags": ["travel", "visa", "sri-lanka", "nri", "south-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/j4n61mthl2rh/"},
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_img_url,
        "image_caption": "The ancient rock fortress of Sigiriya rises above central Sri Lanka",
        "image_attribution": "Wikimedia Commons",
        "body": """Sri Lanka has quietly removed one of the last friction points for Indian travelers. Since May 25, 2026, citizens of India — along with 39 other countries — can obtain a free tourist Electronic Travel Authorization for stays of up to 30 days. The ETA is free. The fee is zero. And for NRIs planning a trip to southern India this summer, that changes the calculus on a Sri Lanka side trip entirely.

## What Exactly Changed

Previously, Indian tourists needed to apply for a tourist ETA and pay a processing fee before arriving in Sri Lanka. The fee was modest — around $20-50 depending on the visa type — but for families of four or five, it added up, and the paperwork felt like a hassle for what might be a three-day beach detour.

Under the new policy, eligible travelers from 40 countries still apply for an ETA before departure — this is not visa-free entry, it is fee-free entry — but the tourist visa charge has been waived entirely. The ETA grants a 30-day stay with **double entry**, meaning you can fly into Colombo, hop to the Maldives or back to India, and return to Sri Lanka on the same authorization.

The eligible countries include India, the United States, United Kingdom, Canada, Australia, China, Germany, France, and most of the Gulf states — covering virtually every country where NRIs live and work.

## The NRI Angle: A Two-Hour Detour from South India

The real value of this policy shift is geographic. Colombo is a 90-minute flight from Chennai, two hours from Bangalore, and barely longer from Kochi or Hyderabad. For NRIs who fly 16 hours to visit family in south India, tacking on a Sri Lanka trip used to require planning: visa applications, processing times, a separate cost. Now it requires a $60-100 one-way flight and an online form.

Sri Lanka's appeal for Indian diaspora families is specific and underrated. The cultural overlap runs deep — Tamil is widely spoken in the north and east, Hindu temples dot the island, and the food shares DNA with south Indian cuisine while tasting distinctly different. For NRI kids who have visited India many times, Sri Lanka offers a foreign-but-familiar experience that is hard to replicate elsewhere in the region.

## Where to Go: A Quick-Hit Guide

**Colombo** (1-2 days): The capital has evolved into a genuine food city. Try Ministry of Crab for its Sri Lankan mud crab, and Barefoot Café for a quieter pace. The Gangaramaya Temple and Pettah Market feel lively without being overwhelming.

**Galle** (1-2 days): The Dutch-era fort town on the southwest coast is Sri Lanka's most photogenic destination. Walk the ramparts at sunset, browse boutique shops inside the fort walls, and eat fresh seafood at any of the restaurants lining the harbor.

**Ella** (2-3 days): The hill country around Ella offers tea plantations, waterfalls, and the famous Nine Arches Bridge. The train from Kandy to Ella is routinely called one of the most scenic rail journeys in the world — and it costs less than $2 in second class.

**Sigiriya** (1 day): The ancient rock fortress, a UNESCO World Heritage site, is the country's most dramatic archaeological landmark. Climb the 1,200 steps for panoramic views of the surrounding jungle and the remnants of a 5th-century palace at the summit.

**Yala National Park** (1-2 days): Sri Lanka's premier wildlife park has one of the highest leopard densities in the world. Morning and evening safaris run year-round. For NRI families who have done Ranthambore and Corbett, Yala offers something genuinely different.

## Practical Details

The ETA application is online at [eta.gov.lk](https://eta.gov.lk). Processing is typically same-day. You will need a valid passport, a return or onward flight ticket, and proof of accommodation. The 30-day clock starts on your first entry.

Standard entry conditions still apply: immigration officers may ask for evidence of sufficient funds and a return ticket. The free ETA covers tourist activities only — not work, study, or business.

Fees paid before May 25, 2026 are not refundable. Extensions beyond 30 days are available but cost extra.

## The Bigger Picture

Sri Lanka's economy was devastated by the 2022 financial crisis, and tourism is central to its recovery. The country is betting that removing the visa fee will generate enough incremental visitors to more than offset the lost revenue. India, as Sri Lanka's nearest large market, is the biggest prize.

For NRIs, the proposition is simple. If your summer itinerary already includes a trip to India, Sri Lanka is now the easiest and cheapest international detour on the map. No visa fee, a 90-minute flight, and a country that feels simultaneously familiar and foreign. The only cost is the time you will wish you had spent longer."""
    },

    # ── Article 3: South Africa ETA ──
    {
        "id": art3_id,
        "headline": "South Africa's New Digital ETA Now Covers Indians — and NRIs Just Got Faster Access to Safari Country",
        "subheadline": "Phase 2 of South Africa's electronic travel authorization extends to Indian passport holders, with QR-based clearance and up to 90-day stays.",
        "slug": art3_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "South Africa is a bucket-list destination for Indian Americans, but visa friction has kept it behind Southeast Asia and Europe. The new ETA changes that equation.",
        "tags": ["travel", "visa", "south-africa", "safari", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/c3ar16oxywc7/"},
            {"name": "Wikipedia — Visa requirements for Indian citizens", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_img_url,
        "image_caption": "Camps Bay beach with Table Mountain and the Twelve Apostles in Cape Town",
        "image_attribution": "Wikimedia Commons",
        "body": """South Africa has expanded its Electronic Travel Authorization system to Indian passport holders, marking a significant step in digitizing entry for one of its fastest-growing tourist markets. Under Phase 2 of the rollout, Indian travelers can now apply online for an ETA before departure — a QR code-based clearance that replaces much of the traditional visa paperwork and promises faster processing at immigration.

The move positions South Africa alongside Thailand, Sri Lanka, and Malaysia in the growing list of countries simplifying entry for Indian nationals. For NRIs in the United States, Canada, and the UK — many of whom already hold powerful passports but travel on their Indian ones for homeland visits — South Africa just became meaningfully easier to reach.

## How the ETA Works

The system is straightforward. Eligible travelers holding ordinary Indian passports apply online through South Africa's ETA portal before departure. Once approved, they receive a digital authorization linked to a QR code. At immigration checkpoints in Johannesburg (OR Tambo), Cape Town International, or Lanseria, officers scan the QR code instead of processing a paper visa.

The ETA allows stays of up to **90 days** with multiple-entry flexibility — a significant improvement over the traditional eVisa process, which often involved longer wait times and less predictable outcomes. The multiple-entry feature is particularly useful for travelers combining South Africa with neighboring countries like Namibia, Botswana, or Mozambique on a single trip.

South African immigration authorities have encouraged travelers to use the ETA portal rather than the older eVisa system, which occasionally experiences downtime during maintenance.

## Why NRIs Should Pay Attention

South Africa has always been on the Indian diaspora's bucket list, but it has consistently lost out to easier destinations. Thailand, Bali, Dubai, and European capitals — all of which have progressively simplified or eliminated visa requirements for Indians — absorb the lion's share of NRI vacation budgets. South Africa's traditional visa process, which could take weeks and required embassy visits, was a deterrent even when the desire was there.

The ETA changes this. An online application, digital processing, and QR-based clearance at the airport mirror the kind of frictionless experience Indian travelers now expect. And the destination itself offers things no Southeast Asian beach resort can match.

## What Makes South Africa Worth the Flight

**Kruger National Park**: Africa's most famous game reserve, home to the Big Five — lion, leopard, elephant, rhino, and buffalo. Self-drive safaris are an option, and private lodges inside the park range from mid-range to ultra-luxury. For NRI families who have exhausted India's tiger reserves, Kruger is the natural next step.

**Cape Town**: Regularly ranked among the world's most beautiful cities. Table Mountain, the V&A Waterfront, Camps Bay, and the Cape Winelands are all within a 30-minute drive of each other. The food scene rivals any global capital — and Indian cuisine is deeply embedded in the local culture, thanks to South Africa's large Indian-origin population.

**The Garden Route**: A 300-kilometer coastal drive from Cape Town to Port Elizabeth, passing through Knysna, Plettenberg Bay, and Tsitsikamma National Park. Think of it as South Africa's answer to the Pacific Coast Highway — but with fewer crowds and more wildlife.

**Johannesburg and Soweto**: For history-minded travelers, the Apartheid Museum and Mandela House in Soweto offer a powerful, sobering experience. Johannesburg's Maboneng Precinct has emerged as a creative hub with galleries, restaurants, and street art.

## The Indian Connection

South Africa is home to roughly 1.6 million people of Indian descent, concentrated primarily in Durban and surrounding KwaZulu-Natal. The community traces its roots to indentured laborers brought by the British in the 19th century and to later waves of traders from Gujarat and Tamil Nadu. Mahatma Gandhi lived in South Africa for 21 years, and the house where he was attacked in Durban is now a museum.

For NRIs, visiting South Africa carries a dimension that pure leisure destinations do not. The Indian diaspora there is older, larger, and more established than in most Western countries. Temple architecture, street food, and community festivals in Durban feel distinctly Indian and distinctly not — the kind of cultural dislocation that diaspora travelers find endlessly fascinating.

## Practical Details

The ETA is currently available at three airports: OR Tambo International (Johannesburg), Cape Town International, and Lanseria International. Travelers should apply online before booking flights. Processing times are expected to be faster than the eVisa pathway, though South African immigration has not published specific turnaround benchmarks.

Flights from the US typically route through Dubai, Doha, or Addis Ababa, with Emirates, Qatar Airways, and Ethiopian Airlines offering the most convenient connections. From India, direct flights operate on SAA and Air India (seasonal). Budget approximately $800-1,200 round trip from major US cities during the off-peak months of May-September (South Africa's winter, which is mild and dry — ideal for safari).

The 90-day stay allowance and multiple-entry provision make South Africa viable for longer, more ambitious itineraries than the typical NRI week-long vacation. A two-week trip combining Cape Town, the Garden Route, and Kruger is now easier to plan than it has ever been."""
    },
]

# --- Insert ---
print("\n=== Inserting articles ===")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone.")
