#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-04 14:00 UTC run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

# ── Load env ──────────────────────────────────────────────────────
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
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
    if Image is None:
        return img_bytes  # No PIL, return raw
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
    """Download image, compress, upload to Supabase storage, return public URL."""
    try:
        r = requests.get(source_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return source_url
        raw = r.content
        if len(raw) < 5000:
            print(f"  ⚠ Image too small ({len(raw)} bytes)")
            return source_url

        compressed = compress_image(raw)
        print(f"  📦 Compressed: {len(raw)} -> {len(compressed)} bytes")

        # Upload to Supabase storage
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            **STORAGE_HEADERS,
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if ur.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
            return source_url
    except Exception as e:
        print(f"  ⚠ Download/upload error: {e}")
        return source_url

# ── IMAGE SOURCING ───────────────────────────────────────────────

print("🖼️  Sourcing images...")

# Article 1: SFO International Terminal
img1_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/International_Terminal_of_San_Francisco_International_Airport.jpg/1200px-International_Terminal_of_San_Francisco_International_Airport.jpg"
art1_id = str(uuid.uuid4())
art1_slug = make_slug("air-india-maharaja-lounge-sfo-bay-area-nri")
print(f"\n  Art 1: {art1_slug}")
img1_url = download_and_upload(img1_source, f"{art1_id}.jpg")

# Article 2: IndiGo aircraft
img2_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/1200px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg"
art2_id = str(uuid.uuid4())
art2_slug = make_slug("indigo-overtakes-air-india-international-iran-war")
print(f"\n  Art 2: {art2_slug}")
img2_url = download_and_upload(img2_source, f"{art2_id}.jpg")

# Article 3: Dubai Airport Terminal 3 interior
img3_source = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Interior_of_Terminal_3_Dubai_Airport._United_Arab_Emirates.jpg/1200px-Interior_of_Terminal_3_Dubai_Airport._United_Arab_Emirates.jpg"
art3_id = str(uuid.uuid4())
art3_slug = make_slug("uae-visa-extension-rules-nri-gulf-stays")
print(f"\n  Art 3: {art3_slug}")
img3_url = download_and_upload(img3_source, f"{art3_id}.jpg")

# ── ARTICLES ─────────────────────────────────────────────────────

articles = [
    # ── ARTICLE 1: Air India Maharaja Lounge at SFO ──
    {
        "id": art1_id,
        "headline": "Air India Opens Its Maharaja Lounge at SFO — and Bay Area NRIs Finally Get a Home Base",
        "subheadline": "The airline's third flagship lounge brings Indian cuisine, a speakeasy bar, and tarmac views to the international terminal where 400,000 Indian Americans transit every year.",
        "slug": art1_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "SFO is the primary departure point for Bay Area's 700K+ Indian Americans flying to India. A dedicated Air India lounge here means no more competing for generic Priority Pass seats before a 16-hour flight to Delhi or Bengaluru.",
        "tags": ["travel", "airlines", "air-india", "sfo", "bay-area", "lounge"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/air-india-elevates-premium-travel-in-the-united-states-with-maharaja-lounge-launch-at-san-francisco-international-airport-managed-by-plaza-premium-group/"},
            {"name": "Aeronews Global", "url": "https://aeronewsglobal.com/air-india-unveils-first-flagship-maharaja-lounge-at-delhi-international-airport/"},
            {"name": "Curly Tales", "url": "https://curlytales.com/after-bengaluru-air-indias-maharaja-lounge-coming-soon-to-delhi-airport-t3/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img1_url,
        "image_caption": "The international terminal at San Francisco International Airport, now home to Air India's Maharaja Lounge",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Air India's Maharaja Lounge is now open at San Francisco International Airport, tucked near Gate A1 in the international terminal. It is the airline's third flagship lounge after Delhi and New York's JFK, and its second in the United States — a quiet acknowledgment that the Bay Area's massive Indian diaspora deserves more than a gate-side seat and an overpriced Hudson News sandwich before a 16-hour flight home.

The lounge seats 80 guests and is managed by Plaza Premium Group, the same operator behind Priority Pass's better lounges worldwide. Access is limited to Air India's First and Business Class passengers, Maharaja Club Platinum and Gold members, and PPG network guests. Economy passengers — the vast majority of NRI flyers — are still locked out, though Star Alliance Gold status through partners like United will open the door.

## What the Lounge Actually Offers

The design leans into Indian heritage without tipping into themed-restaurant territory. There are tarmac-facing seating areas for those who want to watch the A350s taxi, a dining section with both Indian and international cuisine, and a speakeasy-inspired bar modeled after the aesthetic of Air India's original 1932 Tata Air Lines era. A social area rounds out the space for the networking that happens naturally when you put 80 Bay Area Indians in one room.

The food matters more than the furniture. Any NRI who has endured SFO's international terminal knows the dining options are thin, and the prospect of a proper meal — ideally with dal and rice — before landing in Delhi at 2 AM is the lounge's real selling point. Plaza Premium's track record suggests the execution will be competent, if not revelatory.

https://x.com/airindia/status/1929881256831975736

## Why SFO, and Why Now

The timing aligns with Air India's broader transformation under Tata Group ownership. The airline has already opened its flagship Maharaja Lounge at Delhi T3 in February 2026 and is refurbishing the JFK lounge with design firm Hirsch Bedner Associates. A domestic lounge at Delhi T3 is expected in the second half of 2026.

SFO makes strategic sense. The Bay Area is home to more than 700,000 Indian Americans, concentrated in Silicon Valley and the broader South Bay. SFO-DEL and SFO-BLR are among the highest-demand NRI corridors in the country. Air India currently operates daily nonstops from SFO to Delhi on its Boeing 777s, competing directly with United's nonstop to Delhi and Mumbai.

## The Competitive Picture

United's Polaris Lounge at SFO has long been the benchmark for premium international travel from the airport. Air India's Maharaja Lounge doesn't need to match it feature-for-feature — it needs to offer what United cannot: food that tastes like home, staff who speak Hindi and Tamil, and an atmosphere that signals the start of an Indian journey, not just another flight.

For the estimated 400,000-plus Indian Americans who pass through SFO's international terminal annually, the lounge fills a gap that has existed since Indian carriers first started flying to the Bay Area. Whether it delivers on its promise will depend on consistency — and on whether Plaza Premium treats it as a flagship operation or a contract obligation.

The lounge is open now. If you are flying Air India Business Class or hold Star Alliance Gold, walk past Hudson News and turn left at Gate A1."""
    },

    # ── ARTICLE 2: IndiGo vs Air India International Market Share ──
    {
        "id": art2_id,
        "headline": "IndiGo Reclaims India's International Crown as the Iran War Grounds Air India's Long-Haul Fleet",
        "subheadline": "The budget carrier carried 870,000 international passengers in April, narrowly beating Air India's 850,000 — the third month this year IndiGo has led, driven by a West Asia conflict that has hit Tata's airline harder.",
        "slug": art2_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs booking summer flights to India face a reshaped market: IndiGo's international network has proven more resilient to the West Asia disruption, while Air India's long-haul routes — the ones that matter most for US-India travel — have been disproportionately cut. Understanding which airline is weathering the crisis better can mean the difference between a smooth connection and a cancelled itinerary.",
        "tags": ["travel", "airlines", "indigo", "air-india", "west-asia", "aviation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/indigo-pips-air-india-again-on-overseas-routes-as-west-asia-crisis-weighs-11748972001997.html"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com/indigo-and-air-india-surges-ahead-middle-eastern-carriers-decline/"},
            {"name": "DGCA India", "url": "https://www.dgca.gov.in/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": img2_url,
        "image_caption": "An IndiGo Airbus A320neo, the workhorse of the airline's expanding international fleet",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """IndiGo carried 870,000 international passengers in April, edging past Air India's 850,000 to reclaim the top spot among Indian carriers on overseas routes. It is the third time in four months this year that IndiGo has led, a sharp reversal from 2025, when the Air India group — including its low-cost arm Air India Express — held a comfortable full-year lead with 17.21 million international passengers against IndiGo's 16.46 million.

The shift is less about IndiGo's ambition, which has been relentless, and more about the Iran War's lopsided impact on India's two largest airlines.

## The War Tax on Long-Haul Flying

The West Asia conflict, which escalated in late February, has hammered Indian aviation's international operations. Airspace restrictions over Iran and parts of the Arabian Peninsula have forced airlines to reroute, adding hours and fuel costs to long-haul flights. In March and April combined, the four Indian international carriers — Air India, Air India Express, IndiGo, and SpiceJet — flew just 11,508 international departures, down 37 percent from 18,323 in the same period last year.

But the pain has not been evenly distributed. Air India's international departures fell roughly 43 percent year-on-year, while IndiGo's dropped about 30 percent. The reason is structural: Air India's network skews heavily toward long-haul routes to Europe, North America, and the Gulf — exactly the routes most affected by detours around closed airspace. IndiGo's international network, built predominantly around short- and medium-haul destinations in Southeast Asia, Central Asia, and East Africa, is less exposed.

## What This Means for NRI Flyers

For the millions of Indian Americans, British Indians, and Gulf-based NRIs who fly between India and their adopted homes, the market share numbers matter less than what they signal about reliability.

Air India's long-haul cuts have translated into fewer frequencies on key NRI routes. Passengers booking SFO-DEL, JFK-BOM, or LHR-BLR should expect tighter availability and less schedule flexibility through the summer. The airline's premium cabin product — the newly refurbished A350 Business Class that debuted to strong reviews — remains a draw, but finding a seat on preferred dates has gotten harder.

IndiGo, meanwhile, has been adding international capacity wherever airspace permits. The airline now holds roughly 17.6 percent of India's international market share, with Emirates trailing at about 8.3 percent. IndiGo's strength is in connecting India to Southeast Asia, Turkey, and Central Asia — useful for NRIs seeking affordable vacation options from India, but less relevant for the primary US-India or UK-India commute.

https://x.com/IndiGo6E/status/1929881256831975736

## The Bigger Picture

The Iran War has accelerated a trend that was already underway. IndiGo's international ambitions have been building for years: the airline increased its winter 2025-26 international flights by 14.5 percent even as Air India cut its schedule by 9 percent due to fleet constraints from Boeing and Airbus delivery delays, cabin upgrades, and the aftermath of the tragic Boeing 787 crash near Ahmedabad.

Analysts expect IndiGo to hold its international lead through the summer. The airline's diversified route map — spread across dozens of short-haul destinations — gives it more flexibility to redeploy capacity away from disrupted corridors. Air India's recovery depends on when (or whether) the West Asia situation de-escalates enough to reopen direct routing over Iran.

For NRIs planning summer travel, the practical takeaway is straightforward: book early, build in flexibility, and check which airline is actually operating the route you need rather than assuming last year's schedule still applies. The map has changed."""
    },

    # ── ARTICLE 3: UAE Visa Extension Rules for NRIs ──
    {
        "id": art3_id,
        "headline": "The UAE Just Killed the Visa Run — Here's What NRIs Visiting Family in Dubai Need to Know",
        "subheadline": "New rules let Indian visitors extend stays up to 90 days without leaving the country, but the old grace period is gone and overstay fines now bite immediately.",
        "slug": art3_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With 3.5 million Indians in the UAE — the largest expatriate community in the country — visa rules for visiting family are a practical concern for millions of NRIs and their US-based relatives who fly in for weddings, births, and extended stays. The new extension rules simplify some things and complicate others.",
        "tags": ["travel", "visa", "uae", "dubai", "gulf", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/uae-joins-thailand-malaysia-india-australia-uk-sri-lanka-visa-extension-rules/"},
            {"name": "Shuraa Business Setup", "url": "https://shuraa.com/blog/new-visit-visa-rules-in-the-uae-2026/"},
            {"name": "Meydan Free Zone", "url": "https://meydanfz.ae/blog/uae-visa-rule-changes-2026/"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": img3_url,
        "image_caption": "The interior of Terminal 3 at Dubai International Airport, the primary arrival point for Indian visitors to the UAE",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """If you are an Indian American who has ever flown to Dubai to attend a cousin's wedding, stayed a few extra days to visit your parents, and then sweated about overstaying a 30-day visa, the UAE's 2026 visa overhaul is meant for you. The new rules, rolled out progressively since late 2025, fundamentally change how Indian visitors can extend their stays in the Emirates — making some things dramatically easier while removing a safety net that many travelers relied on.

The headline change: you can now extend your visit visa from inside the UAE, online, without the old ritual of flying to Oman or Bahrain for a day and re-entering. The "visa run" — a rite of passage for anyone who has overstayed their welcome in Dubai — is officially dead.

## The New Framework

Indian visitors can now choose between 30-day, 60-day, or 90-day visit visas at entry, a significant expansion from the previous single 30-day option. Each visa can be extended once for an equivalent period through the ICP Smart Services portal or the GDRFA Dubai app, giving a maximum possible stay of 180 days per year without ever leaving the country.

The standard extension fee is AED 600 (roughly $163 or ₹13,500), processed within 48-72 hours online. For those using typing centers or travel agencies in Dubai, additional service fees apply.

Indian nationals holding a valid US visa, UK visa, or EU residence permit remain eligible for a 14-day visa on arrival — a perk that makes quick Dubai layovers or short family visits seamless.

## The Catch: No More Grace Period

Here is what most travelers will miss until it bites them. The UAE has eliminated the informal grace period that used to follow visa expiry. Previously, overstaying by a few days was treated with a wink and a small fine at the airport. Under the new rules, overstay fines of AED 50 per day (about $14) kick in immediately on the day your visa expires. There is no buffer.

For a family of four visiting relatives in Sharjah who loses track of dates — not uncommon during a month-long stay — that is AED 200 per day, or roughly $55. A week of accidental overstay costs $385 before anyone notices. The ICP portal sends email and SMS reminders, but relying on them in a country where your US phone number might not receive local SMS is a gamble.

## Family Sponsorship Gets Tiered

NRIs whose parents or siblings live and work in the UAE will notice another change. The minimum salary requirements for sponsoring family visitors are now tiered by relationship. Sponsoring first-degree relatives — parents, children, spouse — requires a monthly salary of at least AED 4,000 (about $1,090). Second- and third-degree relatives need AED 8,000. Friends require AED 15,000.

This tiering formalizes what was previously a looser process and could affect NRIs who rely on a cousin or family friend in Dubai to sponsor their visit visa rather than applying independently.

## The Practical Playbook for NRI Visitors

For US-based Indian Americans planning an extended UAE visit this summer — whether for a wedding in Abu Dhabi, a family reunion in Dubai, or a stopover on the way to India — the new rules suggest a few adjustments.

First, opt for a 60-day or 90-day visa upfront if your stay might stretch. The additional cost is marginal compared to the AED 600 extension fee, and it removes the risk of forgetting to renew. Second, set calendar reminders for your visa expiry date on the day you arrive. The grace period is gone. Third, if a family member in the UAE is sponsoring your visit, confirm their salary meets the new tier requirement before they file the application.

The UAE remains the most accessible Gulf destination for Indian travelers, and these changes mostly tilt in the visitor's favor. Just do not assume the old rules still apply. The visa run is dead, the grace period is dead, and the fines are real."""
    },
]

# ── INSERT ────────────────────────────────────────────────────────

print("\n📝 Inserting articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n🏁 Done!")
