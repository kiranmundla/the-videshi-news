#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-13 22:00 UTC run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

# ── Load env ──
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
STORAGE_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}

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
    """Resize and compress image. Returns JPEG bytes."""
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def upload_to_supabase(image_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL."""
    print(f"  Downloading: {image_url[:100]}...")
    r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    raw = r.content
    if len(raw) < 5000:
        print(f"  ⚠ Image too small ({len(raw)} bytes), skipping upload")
        return None

    compressed = compress_image(raw)
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    # Upload to Supabase storage
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        **STORAGE_HEADERS,
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    resp = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if resp.status_code not in (200, 201):
        # Try PUT if POST fails
        resp = requests.put(upload_url, headers=upload_headers, data=compressed, timeout=30)
    resp.raise_for_status()

    public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
    print(f"  ✅ Uploaded: {public_url}")
    return public_url


# ═══════════════════════════════════════════════════════════════
# ARTICLE 1: America's 250th Birthday — What NRIs Need to Know
# ═══════════════════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_slug = make_slug("america-250th-birthday-july-4-nri-guide")

art1_body = """America turns 250 on July 4 — and this is not your average Independence Day weekend.

The semiquincentennial (that's the official term, though nobody outside Washington uses it) has triggered the biggest civic celebration the country has seen since the Bicentennial in 1976. For the roughly 4.4 million Indian Americans who call this country home, it is an unusually loaded moment: a chance to celebrate belonging in a nation that has shaped their families' trajectories, even as questions about immigration, identity, and inclusion remain very much alive.

## What's Actually Happening

The centerpiece is the **National Mall in Washington, D.C.**, which is being transformed into a weeks-long festival zone. The Great American State Fair runs from June 25 through July 10, featuring exhibits from all 50 states and territories — think World's Fair meets county fair, stretched across two miles of prime federal real estate. The July 4 "Salute to America" celebration will cap the evening with what organizers are calling the largest fireworks display in the Mall's history.

The FIFA World Cup Fan Zone, already operational on the Mall since June 11, adds a layer of international flavor that previous milestone celebrations lacked. Tickets for all signature events are free through Freedom 250's website, though registration is required and slots are filling fast.

## Beyond D.C.

Cities and historic sites across the country are marking the occasion with their own programming. **Graceland** in Memphis is hosting an "All-American Weekend" from July 3 to 5, with Elvis tribute concerts, exclusive mansion tours, and fireworks. **Valley Forge National Historic Park** in Pennsylvania celebrates its 50th anniversary as a national park on the country's 250th birthday weekend. Savannah, Jacksonville, Augusta, and dozens of smaller cities are staging parades, drone shows, and historical reenactments.

For NRI families already planning summer road trips, the 250th provides a ready-made itinerary hook. Philadelphia's Independence Hall, Boston's Freedom Trail, and Williamsburg's colonial district are all running expanded programming through July.

## Why NRIs Should Care

Indian Americans are the highest-earning and one of the fastest-growing ethnic groups in the United States. The community's contributions — from Silicon Valley boardrooms to Capitol Hill to NASA — are woven into the story of modern America. Yet milestone national celebrations have historically felt like someone else's party.

This year is different. The America 250 Commission has made inclusivity a stated priority, emphasizing immigrant contributions alongside founding-era history. Several state exhibits at the Great American State Fair will highlight immigration stories, and community organizations across the country are hosting "My American Story" events through the summer.

For families with children born in the US, the semiquincentennial offers a tangible way to engage with civic history — and to claim a place in it.

## Practical Tips

**Getting there**: Hotels in D.C. are booking up fast for the June 25–July 10 window. Amtrak's Northeast Regional from New York and Philadelphia remains one of the best options for avoiding Beltway traffic. If you're flying, Reagan National (DCA) puts you closest to the Mall.

**Crowds**: Expect Inauguration-level foot traffic on July 4. The National Park Service recommends arriving before noon for the evening fireworks. Metro will run extended hours.

**For kids**: The Smithsonian museums along the Mall are free and air-conditioned — a crucial combination in D.C.'s July heat. The National Museum of American History is running a special 250th exhibit through September.

**Budget move**: Pack a cooler. Food vendors on the Mall during events charge festival prices, and the heat makes hydration non-negotiable."""

art1 = {
    "id": art1_id,
    "headline": "America Turns 250 — and Indian Americans Have Every Reason to Show Up",
    "subheadline": "The semiquincentennial brings the biggest civic celebration since 1976. Here's what NRI families should know about the events, the history, and why it matters.",
    "slug": art1_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian Americans are the highest-earning ethnic group in the US, yet national milestone celebrations have historically felt like someone else's party — the 250th is making inclusivity a priority.",
    "tags": ["travel", "july-4", "america-250", "nri-families", "washington-dc"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Freedom 250 / America 250 Commission", "url": "https://www.freedom250.com/"},
        {"name": "Delaware Online", "url": "https://www.delawareonline.com/"},
        {"name": "Graceland", "url": "https://www.graceland.com/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "body": art1_body,
    "image_caption": "Fourth of July fireworks illuminate the Washington Monument on the National Mall",
    "image_attribution": "Wikimedia Commons",
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE 2: India's Wellness Tourism Renaissance
# ═══════════════════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_slug = make_slug("india-wellness-tourism-ayurveda-retreats-nri")

art2_body = """The pitch used to be simple: come home for the wedding, stay for the food, endure the traffic. But a growing number of Indian Americans are adding a new line to their India itineraries — a wellness retreat that costs less than a week of therapy in Manhattan.

India's wellness tourism sector is on a tear, and NRIs are fueling a disproportionate share of the demand. According to Booking.com's Travel Trends 2026 report, 87 percent of Indian travelers now say personal wellness motivates their travel decisions. One in four plans to book a wellness-focused holiday this year. Hotels are responding by moving far beyond the spa menu.

## The New Landscape

**Ananda in the Himalayas**, set in a restored viceregal palace above Rishikesh, has become the gold standard. A 21-day Panchakarma programme here runs upward of $10,000 — steep by Indian standards, competitive with comparable offerings in Switzerland or Bali. The resort combines clinical Ayurvedic medicine with yoga, meditation, and Vedantic philosophy, attracting a clientele that skews heavily toward NRIs and international visitors.

In Kerala, **Taj Bekal Resort & Spa** occupies a quiet stretch where the backwaters meet the Arabian Sea. The setting does most of the work: coconut groves, narrow canals, and a coastline that feels empty even in peak season. It is not trying to be a wellness clinic — it is a hotel that understands that slowing down is its own therapy.

**Six Senses Vana** in Dehradun, nestled in sal forests, has carved a niche with specialized programmes — including "Embrace Your Cycle," designed for women dealing with hormonal imbalances or PCOS. The combination of Ayurvedic therapies, Tibetan healing practices, and breathwork reflects a broader industry shift toward personalized, outcome-driven wellness rather than generic pampering.

**Six Senses Fort Barwara** in Rajasthan offers a different register: a 700-year-old warrior fort converted into a wellness destination where guests sleep in rooms once occupied by Rajput nobility. The juxtaposition of ancient architecture and modern wellness science is precisely the kind of thing that pulls NRIs away from their usual Delhi-Mumbai-hometown triangle.

## Why NRIs Are Driving This

The economics are straightforward. A week-long Ayurvedic retreat in Kerala costs $2,000 to $5,000 — roughly what a single therapy session per week costs over a year in most American cities. For NRIs already budgeting an annual trip home, tacking on a wellness detour is an easy decision, particularly when the alternative is a third cousin's engagement party in Lucknow.

But there is something deeper at work. KB Kachru, president of the Hotel Association of India and chairman of Radisson Hotel Group's South Asia operations, told Outlook Traveller that wellness has shifted from "a niche offering into a strategic business imperative." Hotels are building entire ecosystems around Ayurveda, yoga, meditation, nutrition, fitness, and mental wellbeing — integrating them into the core brand proposition rather than treating them as add-ons.

For second-generation Indian Americans who grew up watching their parents' skepticism about yoga studios in strip malls, experiencing these practices in their original cultural context can be revelatory. The yoga in Rishikesh is not the same as the yoga in a Santa Monica studio, and the Ayurveda in Kerala is not the turmeric latte at Whole Foods.

## What to Know Before Booking

**Timing matters**: Northern retreats (Rishikesh, Dehradun) are best from October to March. Kerala works year-round but is driest from December to February. Avoid monsoon season unless you specifically want a traditional Karkidaka Ayurveda treatment, which uses the monsoon's humid conditions as part of the protocol.

**Minimum stays**: Serious Ayurvedic programmes require at least 7 days, with 14 to 21 days recommended for Panchakarma. A weekend spa visit is pleasant but not transformative.

**Credentials check**: Look for resorts with in-house Ayurvedic physicians (vaidyas), not just massage therapists. The best programmes begin with a detailed consultation, including pulse diagnosis, before designing a treatment plan.

**Insurance note**: Most US health insurance plans do not cover Ayurvedic treatments, even at accredited facilities. Some NRIs use HSA or FSA funds for qualifying wellness expenses — check with your provider before assuming coverage."""

art2 = {
    "id": art2_id,
    "headline": "India's Wellness Retreats Are Booming — and NRIs Are the Biggest Converts",
    "subheadline": "From Panchakarma in Rishikesh to Ayurvedic detox in Kerala, Indian Americans are discovering that the best wellness vacation costs less than a year of therapy in the US.",
    "slug": art2_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs are fueling disproportionate demand at India's luxury wellness resorts, where a 21-day Panchakarma costs less than a year of weekly therapy sessions in most US cities.",
    "tags": ["travel", "wellness", "ayurveda", "kerala", "rishikesh", "retreats"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
        {"name": "Booking.com Travel Trends 2026", "url": "https://www.booking.com/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
        {"name": "Hotel Association of India", "url": "https://www.hotelassociationofindia.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "body": art2_body,
    "image_caption": "A traditional houseboat glides through the Kerala backwaters, one of India's most sought-after wellness destinations",
    "image_attribution": "Wikimedia Commons",
}


# ═══════════════════════════════════════════════════════════════
# ARTICLE 3: Gaya Airport's Big Push
# ═══════════════════════════════════════════════════════════════

art3_id = str(uuid.uuid4())
art3_slug = make_slug("gaya-airport-bodh-gaya-flights-bihar-nri-connectivity")

art3_body = """Bihar has never been an easy place to fly into, and Biharis in America know this better than anyone. But the state is making its most aggressive push yet to change that — and Gaya, home to the UNESCO-recognized Mahabodhi Temple, is at the center of the effort.

The Union Civil Aviation Ministry has forwarded a request for new direct flights from Gaya International Airport to Bengaluru, Mumbai, and Ahmedabad — three cities with significant Bihari migrant populations — to Air India and IndiGo for assessment. While the government was careful to note that airlines independently determine route viability, the move signals that Gaya's connectivity gaps have reached the highest levels of aviation policy.

## The Bangkok Breakthrough

The bigger headline, for now, is the Gaya-Bangkok direct service. Bihar's cabinet approved IndiGo to operate twice-weekly flights between Gaya and Bangkok, backed by ₹10.40 crore in viability gap funding — roughly ₹5 lakh per round trip. The route directly targets Buddhist pilgrimage traffic: Thailand has a large Buddhist population, and Bodh Gaya receives hundreds of thousands of Thai, Cambodian, Burmese, and Sri Lankan pilgrims annually.

The Bangkok connection is a template that could reshape Gaya's identity. Until now, the airport has functioned as a seasonal facility, busy during the winter pilgrimage season and quiet for the rest of the year. A regular international service — even twice weekly — gives it the baseline traffic to justify infrastructure investment and attract other carriers.

IndiGo is already connecting Bihar to Shanghai via Kolkata, with through check-in baggage eliminating the traditional hassle of rebooking at intermediate hubs. One-way fares from Patna to Shanghai start at approximately ₹15,999, with total travel time dropping from 30 hours to around 15.

## Why NRIs Should Watch This

Bihar has one of the largest diaspora populations in the United States, concentrated in cities like Chicago, Dallas, and the New York tri-state area. Yet flying home to Bihar has always required routing through Delhi or Kolkata, adding hours and connections to an already grueling journey.

Direct flights from Gaya to Mumbai and Bengaluru would not eliminate the US-India leg, but they would transform the domestic connection. An NRI flying into Delhi or Mumbai could catch a direct flight to Gaya rather than enduring a 12-hour train ride or a 90-minute flight that only operates three days a week.

For the Bihari diaspora, Bodh Gaya is more than a pilgrimage site — it is a cultural anchor. Many NRI families from the Magadh region visit the Mahabodhi Temple during trips home, combining religious observance with family visits in nearby towns. Better connectivity makes these trips logistically feasible rather than aspirational.

## The Buddhist Circuit Play

India's Buddhist circuit — spanning Bodh Gaya, Sarnath, Kushinagar, and Lumbini (just across the Nepal border) — has long been identified as an under-exploited tourism asset. The Mahabodhi Temple alone draws visitors from across Southeast and East Asia, but poor connectivity has capped growth.

The Gaya Citizen Forum recently submitted a detailed tourism development memorandum proposing expanded infrastructure at the Mahavihara complex, riverfront access improvements along the Phalgu River, and better road and rail connectivity. These are not pie-in-the-sky proposals — they address specific capacity constraints that limit visitor access during peak seasons.

If the proposed domestic routes materialize and the Bangkok service proves sustainable, Gaya could evolve from a seasonal pilgrimage airport into a year-round aviation hub. That transformation would ripple through Bihar's tourism, hospitality, and handicrafts sectors — and give the state's diaspora a reason to rethink how often they visit.

## What's Still Missing

The route proposals remain just that — proposals. Airlines will assess commercial viability before committing, and Bihar's aviation market has historically been thin enough to make carriers cautious. The viability gap funding model used for the Bangkok route could be replicated for domestic connections, but that requires sustained state government commitment.

For NRIs planning a trip home through Bihar, the practical advice has not changed yet: book through Delhi or Kolkata, and leave buffer time for connections. But if IndiGo and Air India green-light even two of the proposed routes, that calculus could shift within the year."""

art3 = {
    "id": art3_id,
    "headline": "Gaya Airport Is Finally Getting the Flights Bihar's Diaspora Has Waited For",
    "subheadline": "New routes to Bangkok, Bengaluru, Mumbai, and Ahmedabad could transform Bodh Gaya from a seasonal pilgrimage stop into a year-round hub — and make NRI trips home far less painful.",
    "slug": art3_slug,
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Bihar has one of the largest diaspora populations in the US, but flying home has always required painful routing through Delhi or Kolkata — these new routes could transform the domestic connection.",
    "tags": ["travel", "bihar", "gaya-airport", "bodh-gaya", "indigo", "air-india", "buddhist-tourism"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
        {"name": "GK Today", "url": "https://www.gktoday.in/"},
        {"name": "Patna Press", "url": "https://www.patnapress.com/"},
        {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "body": art3_body,
    "image_caption": "The Mahabodhi Temple complex in Bodh Gaya, Bihar — a UNESCO World Heritage Site and the spiritual anchor of India's Buddhist circuit",
    "image_attribution": "Wikimedia Commons",
}


# ═══════════════════════════════════════════════════════════════
# IMAGE SOURCING & UPLOAD
# ═══════════════════════════════════════════════════════════════

image_sources = {
    art1_slug: "https://upload.wikimedia.org/wikipedia/commons/c/cd/Fourth_of_July_Washington_D.C._Washington_Monument_National_Mall_%2852196286195%29.jpg",
    art2_slug: "https://upload.wikimedia.org/wikipedia/commons/e/ee/House_Boat_DSW.jpg",
    art3_slug: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Mahabodhi_temple_at_Bodhgaya_in_Bihar_21.jpg/1200px-Mahabodhi_temple_at_Bodhgaya_in_Bihar_21.jpg",
}

articles = [art1, art2, art3]

for art in articles:
    slug = art["slug"]
    img_src = image_sources.get(slug)
    if img_src:
        try:
            filename = f"{slug}.jpg"
            public_url = upload_to_supabase(img_src, filename)
            if public_url:
                art["image_url"] = public_url
            else:
                print(f"  ⚠ Upload failed for {slug}, using original URL")
                art["image_url"] = img_src
        except Exception as e:
            print(f"  ❌ Image upload error for {slug}: {e}")
            art["image_url"] = img_src
    else:
        art["image_url"] = ""


# ═══════════════════════════════════════════════════════════════
# INSERT INTO SUPABASE
# ═══════════════════════════════════════════════════════════════

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
