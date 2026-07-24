#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-13 14:00 UTC run."""
import json, os, uuid, re, io, requests
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

def upload_image_to_supabase(img_url, filename):
    """Download image, compress, upload to Supabase storage."""
    from PIL import Image
    r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    img_bytes = r.content
    if len(img_bytes) < 5000:
        print(f"  ⚠ Image too small ({len(img_bytes)} bytes), skipping upload")
        return img_url

    # Compress
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > 1200:
        ratio = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=80, optimize=True)
    compressed = buf.getvalue()
    print(f"  📦 Compressed: {len(img_bytes)} -> {len(compressed)} bytes ({img.width}x{img.height})")

    # Upload to Supabase storage
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    ur = requests.post(upload_url, headers=upload_headers, data=compressed, timeout=30)
    if ur.status_code in (200, 201):
        public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        print(f"  ✅ Uploaded: {public_url}")
        return public_url
    else:
        print(f"  ⚠ Upload failed ({ur.status_code}): {ur.text[:200]}")
        return img_url

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ============================================================
# IMAGE SOURCING
# ============================================================

print("🖼️ Sourcing images...")

# Article 1: China Southern Airlines — Pexels commercial airplane in flight
img1_source = "https://images.pexels.com/photos/1493756/pexels-photo-1493756.jpeg?auto=compress&cs=tinysrgb&w=1200"
print("\n--- Article 1: China Southern Airlines ---")
img1_url = upload_image_to_supabase(img1_source, "china-southern-guangzhou-delhi-nri-20260613.jpg")

# Article 2: Japan Airlines A350 — Pexels airport terminal departure
img2_source = "https://images.pexels.com/photos/4401167/pexels-photo-4401167.jpeg?auto=compress&cs=tinysrgb&w=1200"
print("\n--- Article 2: Japan Airlines ---")
img2_url = upload_image_to_supabase(img2_source, "japan-airlines-daily-bengaluru-nri-20260613.jpg")

# Article 3: World Cup visa challenges — Pexels soccer stadium crowd
img3_source = "https://images.pexels.com/photos/34649361/pexels-photo-34649361.jpeg?auto=compress&cs=tinysrgb&w=1200"
print("\n--- Article 3: World Cup ---")
img3_url = upload_image_to_supabase(img3_source, "world-cup-2026-visa-nri-fans-guide-20260613.jpg")

# ============================================================
# ARTICLES
# ============================================================

print("\n📝 Preparing articles...")

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "China Southern Launches Daily Guangzhou–Delhi Nonstop — and NRIs Get a New Asia Gateway",
        "subheadline": "The September launch of Boeing 737-8 service on the CZ359/360 pair adds daily frequency to a corridor that Indian business travelers and students have long booked through Middle Eastern hubs.",
        "slug": make_slug("china-southern-guangzhou-delhi-daily-nonstop-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian tech workers, traders, and students who regularly shuttle between India and China gain a direct daily option that eliminates Gulf-state layovers and cuts travel time by up to eight hours.",
        "tags": ["travel", "airlines", "china-southern", "india-china", "nonstop-flight"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/c5ehqhdm53lb/"},
            {"name": "Travel And Tour World (route details)", "url": "https://www.travelandtourworld.com/news/article/dqy8j6lzlnqf/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url,
        "image_caption": "A commercial airplane flies high above the clouds on an international route",
        "image_attribution": "Pexels",
        "body": """China Southern Airlines will launch daily nonstop service between Guangzhou Baiyun International Airport and Delhi's Indira Gandhi International Airport on September 21, 2026. Flight CZ359 will depart Guangzhou daily, with the return leg CZ360 operating the same frequency. The airline will deploy its Boeing 737-8, a fuel-efficient narrowbody that seats roughly 160 passengers in a two-class configuration.

The route fills a gap that has frustrated Indian business travelers for years. Guangzhou — the manufacturing and export capital of southern China — sits at the center of the Pearl River Delta, home to thousands of Indian traders who source electronics, textiles, and industrial components. Until now, most flew through Dubai, Doha, or Bangkok, adding six to ten hours to what should be a five-hour flight.

## Why This Matters to NRIs

For the estimated 50,000 Indian nationals living and working in mainland China — plus tens of thousands of NRI entrepreneurs who make quarterly sourcing trips — the new daily service is overdue. The India-China trade corridor hit $118 billion in 2025, yet direct air connectivity has lagged far behind the commerce it supports. Before the pandemic, only Air India operated a spotty Delhi-Shanghai service. The post-COVID rebuild has been slow, with most Indian carriers steering clear of Chinese routes.

China Southern's move is strategic. Guangzhou is the airline's home hub and a Star Alliance gateway, meaning NRIs in the U.S. can book through-tickets on United or Air India (also Star Alliance) with a single baggage check from, say, San Francisco to Delhi via Guangzhou. That routing may not be the fastest, but it unlocks competitive fares for budget-conscious travelers willing to stop in southern China.

## The Student Angle

The route also targets the growing number of Indian medical and engineering students in Chinese universities. Roughly 23,000 Indian students were enrolled across China as of early 2026, concentrated in Guangdong, Hubei, and Sichuan provinces. A daily Delhi service means cheaper, more reliable connections home during semester breaks — especially when compared to the erratic scheduling of charter-style services that have served this market.

## What to Watch

The Boeing 737-8 is a narrowbody, which means no lie-flat seats and limited cargo capacity. Business travelers accustomed to the Gulf carriers' wide-body comfort may find the five-hour hop tolerable but unspectacular. If load factors justify it, China Southern could upgrade to an A330 — the airline already flies A330s on its Guangzhou-Mumbai route.

For NRIs planning ahead, the September 21 start date falls right before the Golden Week holiday in China (October 1–7), when fares on China-linked routes spike. Booking early on the new service could yield introductory pricing before the holiday rush hits."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Japan Airlines Goes Daily on Tokyo–Bengaluru — and Indian Tech Workers Get a Premium Alternative",
        "subheadline": "JAL upgrades its Narita-BLR route from limited weekly service to daily A350 flights starting September 1, creating a new high-end corridor between India's tech capital and the Oneworld network.",
        "slug": make_slug("japan-airlines-daily-tokyo-bengaluru-a350-nri-tech"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian tech professionals shuttling between Bengaluru and the U.S. or Japan gain a premium daily option via Tokyo, with Oneworld connections to American Airlines hubs across the U.S.",
        "tags": ["travel", "airlines", "japan-airlines", "bengaluru", "tech-travel", "a350"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/epuzpsbszlpx/"},
            {"name": "Japan Airlines Official Schedule", "url": "https://www.jal.co.jp/en/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url,
        "image_caption": "An airplane visible through airport terminal windows at a departure gate",
        "image_attribution": "Pexels",
        "body": """Japan Airlines has confirmed that its Tokyo Narita to Bengaluru service will move to daily operations from September 1, 2026, running through at least March 27, 2027. The route, previously limited to a handful of weekly frequencies, will now operate seven days a week on JAL's Airbus A350 fleet — giving Indian travelers one of the most comfortable long-haul products available on any India-Japan corridor.

The upgrade is part of JAL's broader A350 network expansion, which also brings daily service to San Diego, increased frequencies to Melbourne and Helsinki, and more A350-1000 deployments on premium routes to New York JFK, London Heathrow, and Paris CDG.

## The Bengaluru Connection

Bengaluru is not just India's IT capital — it is the city where Japan's corporate presence in India is most concentrated. Toyota, Sony, Hitachi, NTT, and dozens of Japanese mid-caps operate R&D and engineering centers in the city's Outer Ring Road corridor. The move to daily frequencies directly reflects the volume of business travel between these two tech ecosystems.

For NRIs in the United States, the Tokyo routing offers a compelling alternative to the Gulf carrier trifecta of Emirates, Qatar, and Etihad. JAL's Oneworld membership means American Airlines frequent flyers can earn and burn miles on the Tokyo-Bengaluru leg. A hypothetical itinerary like Dallas–Tokyo–Bengaluru books on a single Oneworld ticket, with JAL's premium economy and business class cabins consistently rated among the world's best by Skytrax.

## Why This Beats the Gulf Route for Some Travelers

The Dubai/Doha routing to Bengaluru is well-established, but it comes with tradeoffs: long layovers, crowded transfer terminals, and time-zone math that lands you at 3 AM. The Tokyo-Bengaluru leg is a roughly eight-hour flight that, combined with JAL's efficient Narita connections, can deliver passengers from the U.S. West Coast to Bengaluru in under 20 hours with a single stop.

JAL's A350-1000 cabins feature herringbone business-class suites with direct aisle access, a step up from the 2-3-2 configurations still common on some Gulf carrier wide-bodies. Economy is no afterthought either — the A350's wider cabin and lower pressurization altitude mean noticeably less fatigue on arrival.

## The Student and Family Market

The daily frequency also opens the route to leisure and family travelers. Bengaluru is a gateway to Karnataka's temple towns, Coorg's hill stations, and Hampi's UNESCO ruins — destinations that Japanese tourists are increasingly discovering. In reverse, the strong yen and Japan's near-universal English signage make Tokyo, Kyoto, and Osaka attractive for NRI families seeking an Asia holiday that does not default to Southeast Asia.

JAL's pricing on new daily routes typically starts competitive before settling into market rates. NRIs eyeing a fall trip to India — or a cherry blossom detour through Japan on the way back — should watch for introductory fares when bookings open."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The World Cup Is Here — and NRIs Have an Edge Most Global Fans Don't",
        "subheadline": "While visa denials and ICE fears keep fans from Europe and Africa away, Indian Americans with valid U.S. residency can walk into any of the 11 American host cities without a single extra form. Here's how to make the most of it.",
        "slug": make_slug("world-cup-2026-nri-travel-advantage-visa-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian Americans already in the U.S. face zero visa barriers to attending World Cup matches — a significant advantage over fans flying in from Europe, Africa, and Asia who face B1/B2 delays, ICE concerns, and record-high ticket prices.",
        "tags": ["travel", "world-cup-2026", "fifa", "visa", "nri-guide", "sports-travel"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/sports/soccer/trump-world-cup-border-security-crackdown-69e6f3e0"},
            {"name": "Reuters", "url": "https://www.reuters.com/sports/soccer/pricey-world-cup-keeps-fans-away-hits-us-hotels-airlines-2026-06-12/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/sb12gmyrqk5t/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3_url,
        "image_caption": "A packed soccer stadium filled with enthusiastic fans during a match",
        "image_attribution": "Pexels",
        "body": """The first FIFA World Cup ever spread across three countries kicked off on June 11, and within 48 hours, the tournament's biggest off-field story is not a goal or a red card — it is the chaos at the border. A Somali referee detained for ten hours at Miami airport. Visa denials hitting ticketholders from Germany, Nigeria, and Egypt. European governments updating travel advisories for the United States. The Wall Street Journal reported that international arrivals to the U.S. fell 5.5% in 2025, making America the only major destination to lose visitors — and the World Cup has not reversed the slide.

For the roughly 4.8 million Indian Americans living across the United States, this dysfunction is someone else's problem. Green card holders, H-1B workers, U.S. citizens of Indian origin — none of them need a single additional document to buy a ticket and walk into Levi's Stadium in Santa Clara or MetLife Stadium in New Jersey. In a tournament defined by border friction, NRIs are the fans with the smoothest path to the pitch.

## The Numbers Are Stark

Fans from more than half the 48 qualified nations need B1/B2 visas to enter the United States. FIFA's much-publicized PASS program — a priority appointment system for ticketholders — only accelerates the interview scheduling, not the approval. Embassy wait times in parts of Africa and Asia stretch past 90 days. Meanwhile, dynamic pricing has pushed the cheapest tickets in New York and Miami past $1,000 on resale platforms, according to TicketData.

Reuters reported that hotel bookings in several host cities are running below expectations, while Airbnb is positioning the event as its largest ever — a sign that fans who do make it are trading hotels for vacation rentals to split costs.

## The NRI Playbook

Indian Americans sitting in Dallas, Houston, the Bay Area, Los Angeles, or the New York metro area are within driving distance or a short flight from a World Cup venue. Here is the practical calculus:

**Bay Area residents**: Qatar vs. Switzerland plays at Levi's Stadium in Santa Clara today (June 13). Jordan vs. Algeria comes to the same venue later this month. These are not marquee matchups for most American fans, which means tickets are among the tournament's most affordable — often under $100 for upper-deck seats on the secondary market.

**Tri-state NRIs**: MetLife Stadium in East Rutherford hosts some of the tournament's biggest draws, including Brazil vs. Morocco tonight. The stadium is a 30-minute train ride from Penn Station.

**Texas corridor**: AT&T Stadium in Dallas and NRG Stadium in Houston both host group-stage matches. NRIs in the DFW-Houston-Austin triangle can attend multiple matches without boarding a flight.

**Mexico as a bonus**: Indian passport holders with a valid U.S. visa can enter Mexico without a separate Mexican visa. Guadalajara, Mexico City, and Monterrey host matches, and flights from U.S. border cities are cheap. A weekend trip to catch a match in Mexico City is entirely feasible for NRIs willing to cross the border.

## Hosting Fans From India

The trickier question is for NRIs whose family or friends want to fly in from India. The B1/B2 tourist visa remains the bottleneck. Current wait times for U.S. visa appointments in Mumbai and Delhi hover around 30 to 60 days — better than some regions but tight for anyone who has not already applied. FIFA PASS priority appointments help, but only if you hold a confirmed match ticket.

For family members already holding valid U.S. tourist visas from previous trips, the path is clear. For those without, the window to attend group-stage matches has effectively closed. Knockout rounds in July remain possible if applications are filed immediately.

## The Bottom Line

The 2026 World Cup is a once-in-a-generation spectacle happening in NRIs' backyard. While the world debates America's border policies, Indian Americans have the rare advantage of being inside the fence already. The smart move: pick a match in your nearest host city, grab secondary-market tickets before knockout-round demand spikes, and show up. India may not be on the pitch, but 4.8 million Indian Americans are in the stands — if they choose to be."""
    }
]

# ============================================================
# INSERT
# ============================================================

print("\n🚀 Inserting articles...")
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline']}\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n✅ Done.")
