#!/usr/bin/env python3
"""Videshi Travel News Writer — June 10, 2026 evening run"""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

# Load env
env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

pexels_env = Path.home() / "workspace/.env.pexels"
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
    if Image is None:
        return img_bytes  # fallback if PIL not available
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(image_url, filename):
    """Download image, compress, upload to Supabase storage bucket."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"  ⚠ Not an image: {content_type}")
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
        up = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
        if up.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded: {public_url}")
            return public_url
        else:
            print(f"  ❌ Upload failed ({up.status_code}): {up.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Image processing error: {e}")
        return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── IMAGE SOURCING ────────────────────────────────────────────────────

print("=" * 60)
print("IMAGE SOURCING")
print("=" * 60)

# Article 1: US Fast-Pass Visa — Pexels passport close-up
print("\n📸 Article 1: US passport image...")
art1_img_url = "https://images.pexels.com/photos/32642491/pexels-photo-32642491.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_id = str(uuid.uuid4())
art1_slug = make_slug("us-fast-pass-visa-750-nri-parents-family")
art1_final_img = upload_to_supabase(art1_img_url, f"{art1_slug}.jpg")

# Article 2: Air India Maharaja Club — Wikipedia Air India aircraft
print("\n📸 Article 2: Air India aircraft image...")
art2_img_url = "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png"
art2_id = str(uuid.uuid4())
art2_slug = make_slug("air-india-maharaja-club-express-loyalty-nri")
art2_final_img = upload_to_supabase(art2_img_url, f"{art2_slug}.jpg")

# Article 3: World Cup visa chaos — Pexels stadium crowd
print("\n📸 Article 3: World Cup stadium image...")
art3_img_url = "https://images.pexels.com/photos/34649361/pexels-photo-34649361.jpeg?auto=compress&cs=tinysrgb&w=1200"
art3_id = str(uuid.uuid4())
art3_slug = make_slug("fifa-world-cup-2026-visa-chaos-nri-visitors")
art3_final_img = upload_to_supabase(art3_img_url, f"{art3_slug}.jpg")


# ── ARTICLES ──────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("WRITING ARTICLES")
print("=" * 60)

articles = [
    # ── ARTICLE 1: US Fast-Pass Visa ──
    {
        "id": art1_id,
        "headline": "The US Just Launched a $750 Fast-Pass for Tourist Visas — and NRIs With Visiting Parents Should Read the Fine Print",
        "subheadline": "A new pilot program lets B1/B2 applicants pay a premium to cut months-long appointment queues to ten days. For the millions of Indian Americans who sponsor family visits every year, it could change everything — or deepen an already unequal system.",
        "slug": art1_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs routinely wait months for parent/family B1/B2 visa appointments at US embassies in India. The $750 fast-pass pilot (July–December 2026) could eliminate the agonizing wait — but the price tag raises equity concerns for middle-class families in India.",
        "tags": ["travel", "visa", "us-visa", "nri", "b1b2", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/fe8l14enb3pd/"},
            {"name": "US Department of State", "url": "https://travel.state.gov/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_final_img or art1_img_url,
        "image_caption": "A US passport alongside travel documents and a boarding pass",
        "image_attribution": "Pexels",
        "body": """Every summer, the same ritual plays out across Indian American households: someone opens the US embassy appointment portal in Delhi or Mumbai, scrolls through months of unavailable dates, and calls their parents to deliver the bad news. The visit will have to wait.

That calculus may have just shifted. The US State Department has launched a fast-pass pilot program for B1/B2 tourist visa applicants, allowing them to pay a $750 premium fee — on top of the standard $185 application charge — to secure a consular interview within ten business days. The pilot runs from July 1 through December 31, 2026, and applies across all US embassies and consulates worldwide.

## How It Works

The mechanics are straightforward. Applicants select the fast-pass option during the standard DS-160 process and pay the additional fee. Once processed, they receive a priority interview slot within roughly two weeks rather than the months-long wait typical at high-volume posts like New Delhi, Mumbai, Chennai, and Hyderabad.

The State Department has emphasized that the premium fee expedites scheduling only — not the visa decision itself. Applicants still undergo the same background checks, document review, and in-person interview. Paying $750 does not guarantee approval. It guarantees speed.

The pilot was introduced in response to what officials described as record-breaking global travel demand and persistent backlogs at major consulates. India, which generates the highest volume of B1/B2 applications among non-waiver countries, stands to feel the impact most acutely.

## Why NRIs Should Pay Attention

For Indian Americans, the B1/B2 tourist visa is the single most common mechanism for bringing parents, siblings, and extended family to the US. Unlike green card sponsorship, which involves years-long queues, the tourist visa is meant to be temporary and accessible. But in practice, appointment backlogs have made even this process painfully slow.

The fast-pass changes the equation for families planning around specific events — a grandchild's graduation, a new baby, Diwali celebrations, or the summer school break. Previously, these visits required booking appointments six to eight months ahead. Now, a family willing to spend $750 per applicant can compress that to days.

For a couple — say, parents flying from Hyderabad to visit their son in the Bay Area — the premium adds $1,500 to an already expensive trip. That's on top of approximately $370 in standard visa fees for two, plus flights that routinely run $1,200–$1,800 per person on peak summer routes.

## The Equity Question

Not everyone is thrilled. Critics have pointed out that a $750 fast-pass creates a two-tier system where wealthier applicants move to the front of the line. For middle-class Indian families — a retired couple on a government pension, for instance — the fee may be prohibitive, effectively pricing them out of timely access.

Travel industry groups, on the other hand, have largely welcomed the program. Airlines, hotel chains, and tourism boards see it as a practical tool to unlock pent-up travel demand, particularly ahead of peak events like the FIFA World Cup 2026, which is already driving a surge in US-bound travel.

## What Happens Next

The State Department has said it will review the pilot's results at the end of 2026 before deciding on expansion. If successful, the fast-pass could extend to other visa categories or become a permanent feature of the consular appointment system.

For now, NRIs planning to bring family over this summer or fall have a new — if expensive — option on the table. The visa queue just got a shortcut, but only for those who can afford it."""
    },

    # ── ARTICLE 2: Air India Maharaja Club + Express ──
    {
        "id": art2_id,
        "headline": "Air India's Loyalty Program Now Covers Express Flights — and NRIs Can Finally Earn Points on Every Leg Home",
        "subheadline": "The Maharaja Club's expansion to Air India Express connects 55+ cities across India and Southeast Asia, letting frequent flyers earn and burn points on the budget carrier for the first time. Award flights start at just 1,500 points.",
        "slug": art2_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying Air India internationally often connect on Air India Express for domestic legs — Delhi to Amritsar, Mumbai to Goa, Bengaluru to Kochi. Until now, those connecting flights were loyalty dead zones. The Maharaja Club integration means every segment of the journey home now earns points.",
        "tags": ["travel", "airlines", "air-india", "loyalty", "nri", "air-india-express"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/yef2ix78anrv/"},
            {"name": "Air India", "url": "https://www.airindia.com/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_final_img or art2_img_url,
        "image_caption": "An Air India Boeing 777 on the tarmac at John F. Kennedy International Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """If you have ever landed at Delhi on a 16-hour Air India flight from Newark, cleared immigration, collected your bags, re-checked them, walked to the domestic terminal, and boarded an Air India Express connection to Amritsar — only to realize that last leg earned you exactly zero loyalty points — the frustration is familiar.

That gap just closed. Air India has extended its Maharaja Club loyalty program to cover all Air India Express flights, spanning more than 55 cities across India, Southeast Asia, and the Gulf. Members can now earn Maharaja Points and Tier Points on Express flights booked through Air India's website, its mobile app, or major travel agents. More importantly, those domestic and regional segments now count toward tier qualification, meaning the Kochi-to-Bengaluru hop after a long-haul flight from Chicago finally contributes to your status.

## The Numbers

The earning structure follows Air India's existing framework, calculated on base fare plus fuel surcharge. At the Red (entry) tier, members earn 8 points per ₹100 spent when booking directly through Air India Express's own channels, and 6 points when booking through OTAs and third-party agents. Platinum members earn up to 12 points per ₹100 on direct bookings.

Redemption starts low. A Bengaluru-to-Chennai award flight costs just 1,500 Maharaja Points. Domestic sectors like Delhi-to-Bengaluru run 7,000 points, while international routes — Amritsar to Dubai, Mumbai to Abu Dhabi, Kochi to Bahrain, Bengaluru to Bangkok — come in at 12,000 points each.

For NRIs who fly the US-India corridor regularly, the math is attractive. A single round-trip on Air India from San Francisco to Delhi in economy can generate enough base points that, combined with a few domestic Express connections during a two-week India trip, the accumulation becomes meaningful over a year or two of visits.

## Why This Matters for Diaspora Travelers

Air India Express operates a network that disproportionately serves exactly the routes NRIs need after landing at a hub airport. Think Ahmedabad, Kozhikode, Amritsar, Goa, Dimapur — cities that are major origin points for the Indian diaspora but don't have nonstop international service from the US. The typical NRI itinerary involves a long-haul flight to Delhi or Mumbai followed by one or two domestic connections on Express.

Until now, those connections existed in a loyalty vacuum. Competitors like IndiGo don't have a comparable points program, and third-party frequent flyer programs (Star Alliance, oneworld) don't cover Air India Express. The Maharaja Club integration fills a niche that no other Indian carrier currently offers: a single loyalty ecosystem that covers both the international trunk route and the last-mile connection to your hometown.

## Coming Attractions

Air India has signaled that later phases will bring additional Maharaja Club benefits to Express flights, including priority check-in and boarding, seat selection perks, flexible cancellation options, and fee waivers on changes. These enhancements aim to align the budget carrier's experience with Air India's full-service standards.

The broader strategic play is clear. As Air India Group consolidates its brands under Tata ownership — Air India, Air India Express, and the recently merged Vistara network — the Maharaja Club is becoming the connective tissue that binds the entire ecosystem. For the diaspora traveler who flies internationally twice a year and domestically several times during each visit, having a single loyalty program that rewards every segment is a meaningful upgrade.

The days of dead-mileage domestic connections are over. Every leg home now counts."""
    },

    # ── ARTICLE 3: World Cup Visa Chaos ──
    {
        "id": art3_id,
        "headline": "The World Cup Kicks Off This Week — but Getting Into the US Has Become the Hardest Match of the Tournament",
        "subheadline": "Visa denials, travel bans, passport warnings, and a climate of uncertainty are overshadowing the biggest sporting event on American soil. For NRIs hosting visiting family and friends, the stakes are personal.",
        "slug": art3_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "India isn't playing in the World Cup, but the tournament is being hosted across 11 US cities where millions of NRIs live. Many are hosting family and friends from India who want to experience the atmosphere. The current visa and immigration climate adds a layer of anxiety that goes beyond the pitch.",
        "tags": ["travel", "world-cup", "fifa", "visa", "immigration", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Front Office Sports", "url": "https://frontofficesports.com/travel-visa-issues-hang-over-world-cup/"},
            {"name": "The Travel", "url": "https://www.thetravel.com/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_final_img or art3_img_url,
        "image_caption": "A packed football stadium during a major international match",
        "image_attribution": "Pexels",
        "body": """The 2026 FIFA World Cup opens this week across the United States, Mexico, and Canada — the largest sporting event ever held on American soil, with 78 matches in 11 US cities, over five million expected visitors, and an economic impact projected in the billions. But behind the highlight reels and bracket predictions, a quieter drama is playing out at airports, consulates, and border crossings.

Players have been held up. At least one referee was delayed. Coaches and federation officials have had visa applications rejected outright. Journalists from several participating nations are facing widespread denials or single-entry restrictions that make covering a month-long tournament across multiple cities logistically impossible. Iran's football federation reported that the US would only allow the national team to enter one day before each match — barely enough time to adjust to jet lag, let alone prepare.

## Governments Are Warning Their Own Citizens

The anxiety extends well beyond team delegations. Multiple foreign governments have issued explicit travel advisories for their nationals attending the World Cup in the US. The UK government has urged visitors to "always carry a passport showing you have permission to enter or remain in the US." Australia's Smartraveller website warned that "US authorities actively pursue, detain, and deport people who are in the country illegally" and that immigration officers have "broad powers to decide if you're eligible to enter."

For fans from visa-waiver countries, these warnings are unsettling. For visitors from countries that require a visa — including India — the message is starker: prepare thoroughly, carry all documentation, and understand that entry is never guaranteed, even with a valid visa in hand.

## The NRI Dimension

India is not competing in the World Cup. But the tournament is being hosted across cities that are home to the country's largest diaspora populations — New York/New Jersey, the Bay Area, Houston, Dallas, Los Angeles, Seattle. Millions of Indian Americans live in these metro areas, and many have invited family and friends from India to visit during the tournament — not necessarily to watch football, but to experience the atmosphere, the city, the moment.

Those visits now carry a layer of uncertainty that didn't exist a few years ago. Multiple reports over the past year of foreign tourists being detained by US immigration authorities have rattled confidence. A concierge service owner in the Ivory Coast, speaking to the Washington Post, captured the mood: "Even if you get a visa, you can get to the airport in the US and still get sent back to your country. They are asking me, 'Are you sure I can get in?' I say, 'I'm not sure because I'm not working at the airport.'"

For NRIs whose parents or siblings hold B1/B2 tourist visas, the question is no longer just "will they get the visa?" but "will they get through the border?" That distinction matters.

## The Financial Exposure

The potential losses for a denied entry are significant. Round-trip flights from India to a World Cup host city run $1,200 to $1,800. Hotels within 15 miles of a stadium average $300 to $1,000 per night. Match tickets range from $250 for group-stage seats to nearly $9,000 for premium final tickets. Add pre-booked tours, restaurants, and experiences, and a family of four could have $10,000 or more on the line — all of it at risk if someone is turned away at immigration.

## What NRIs Can Do

For Indian Americans hosting visitors during the tournament, a few practical steps can reduce risk. Ensure visitors carry printed copies of their return tickets, hotel reservations, and a letter of invitation with your contact details and address. Advise them to have evidence of ties to India — property documents, employment letters, bank statements — readily accessible, not buried in checked luggage. And set realistic expectations: even with proper documentation, entry is at the discretion of the Customs and Border Protection officer.

The State Department has said it is working with the White House, DHS, and FIFA to support team travel, but emphasized it "will not waver in upholding US law and the highest standards of national security." That language leaves little room for flexibility — and a lot of room for anxiety.

The world is coming to America for the World Cup. Whether America is ready to let them in is the match that matters most."""
    },
]


# ── INSERT ──────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"\n✅ {art['slug']}")
        print(f"   Headline: {art['headline'][:80]}...")
        print(f"   Image: {'Supabase' if art['image_url'] and 'supabase' in art['image_url'] else 'Original URL'}")
    except Exception as e:
        print(f"\n❌ {art['slug']}: {e}")

print("\n" + "=" * 60)
print(f"DONE — {len(articles)} articles submitted for review")
print("=" * 60)
