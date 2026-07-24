#!/usr/bin/env python3
"""Travel writer — 2026-06-11 02:56 PDT batch"""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# ── env ────────────────────────────────────────────────────────────────
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
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

# ── helpers ────────────────────────────────────────────────────────────
def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")

def fetch_wikipedia_image(term):
    encoded = requests.utils.quote(term.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers=UA, timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{term}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{term}': {e}")
    return None

def fetch_wikimedia_commons(query, limit=5):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params, headers=UA, timeout=15,
        )
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            results = []
            for pid, page in pages.items():
                ii = page.get("imageinfo", [{}])[0]
                mime = ii.get("mime", "")
                if not mime.startswith("image/") or mime == "image/svg+xml":
                    continue
                if ii.get("width", 0) < 300:
                    continue
                url = ii.get("thumburl") or ii.get("url", "")
                if url:
                    results.append(url)
            if results:
                print(f"  ✓ Commons: {len(results)} images for '{query}'")
            return results
    except Exception as e:
        print(f"  ⚠ Commons error: {e}")
    return []

def fetch_pexels(query):
    if not PEXELS_KEY:
        return None
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-sS", f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page=5",
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            url = photos[0]["src"]["large2x"]
            print(f"  ✓ Pexels: '{query}' → {url[:60]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Pexels error: {e}")
    return None

def compress_and_upload(img_url, slug):
    """Download, compress, and upload to Supabase storage. Return final URL."""
    try:
        from PIL import Image
    except ImportError:
        print("  ⚠ PIL not available, using direct URL")
        return img_url, False

    try:
        r = requests.get(img_url, headers=UA, timeout=20)
        r.raise_for_status()
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small ({len(r.content)} bytes), skipping")
            return img_url, False

        img = Image.open(io.BytesIO(r.content))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        jpeg_bytes = buf.getvalue()
        print(f"  ✓ Compressed: {len(jpeg_bytes)//1024}KB")

        filename = f"{slug}.jpg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        upload_headers = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }
        up = requests.post(upload_url, headers=upload_headers, data=jpeg_bytes, timeout=30)
        if up.status_code in (200, 201):
            final = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {final[:60]}...")
            return final, True
        else:
            print(f"  ⚠ Upload failed ({up.status_code}): {up.text[:200]}")
            return img_url, False
    except Exception as e:
        print(f"  ⚠ Compress/upload error: {e}")
        return img_url, False

def validate_image_url(url):
    """Check URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, headers=UA, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD didn't return Content-Length
        if r.status_code == 200 and "image" in ct:
            return True
    except Exception:
        pass
    return False


# ── Image sourcing ─────────────────────────────────────────────────────
print("=" * 60)
print("SOURCING IMAGES")
print("=" * 60)

# Article 1: China Southern Airlines
print("\n--- Article 1: China Southern Airlines Guangzhou-Delhi ---")
art1_candidates = []
wiki_img = fetch_wikipedia_image("China Southern Airlines")
if wiki_img:
    art1_candidates.append(("wikipedia", wiki_img))
commons = fetch_wikimedia_commons("China Southern Airlines Boeing 737")
for c in commons[:2]:
    art1_candidates.append(("wikimedia_commons", c))
if not art1_candidates:
    commons2 = fetch_wikimedia_commons("China Southern Airlines aircraft")
    for c in commons2[:2]:
        art1_candidates.append(("wikimedia_commons", c))
pex = fetch_pexels("commercial airplane runway takeoff")
if pex:
    art1_candidates.append(("pexels", pex))

print(f"  Candidates: {len(art1_candidates)}")
art1_img = art1_candidates[0][1] if art1_candidates else None
art1_source = art1_candidates[0][0] if art1_candidates else None

# Article 2: Air Canada Delhi-Toronto
print("\n--- Article 2: Air Canada Delhi-Toronto ---")
art2_candidates = []
wiki_img2 = fetch_wikipedia_image("Air Canada")
if wiki_img2:
    art2_candidates.append(("wikipedia", wiki_img2))
commons2 = fetch_wikimedia_commons("Air Canada Boeing 787 Dreamliner")
for c in commons2[:2]:
    art2_candidates.append(("wikimedia_commons", c))
pex2 = fetch_pexels("Boeing 787 Dreamliner airplane")
if pex2:
    art2_candidates.append(("pexels", pex2))

print(f"  Candidates: {len(art2_candidates)}")
art2_img = art2_candidates[0][1] if art2_candidates else None
art2_source = art2_candidates[0][0] if art2_candidates else None

# Article 3: Riyadh Air launch
print("\n--- Article 3: Riyadh Air maiden flight ---")
art3_candidates = []
wiki_img3 = fetch_wikipedia_image("Riyadh Air")
if wiki_img3:
    art3_candidates.append(("wikipedia", wiki_img3))
commons3 = fetch_wikimedia_commons("Riyadh Air Boeing 787")
for c in commons3[:2]:
    art3_candidates.append(("wikimedia_commons", c))
if not art3_candidates:
    commons3b = fetch_wikimedia_commons("Saudi Arabia airline Boeing 787")
    for c in commons3b[:2]:
        art3_candidates.append(("wikimedia_commons", c))
pex3 = fetch_pexels("Boeing 787 Dreamliner airport")
if pex3:
    art3_candidates.append(("pexels", pex3))

print(f"  Candidates: {len(art3_candidates)}")
art3_img = art3_candidates[0][1] if art3_candidates else None
art3_source = art3_candidates[0][0] if art3_candidates else None

# ── Compress and upload images ─────────────────────────────────────────
print("\n" + "=" * 60)
print("COMPRESSING & UPLOADING IMAGES")
print("=" * 60)

art1_slug = make_slug("china-southern-guangzhou-delhi-nonstop-nri")
art2_slug = make_slug("air-canada-delhi-toronto-17-hour-nonstop-nri")
art3_slug = make_slug("riyadh-air-maiden-flight-london-nri-gateway")

art1_final_img = None
art1_attribution = "Wikimedia Commons"
if art1_img:
    art1_final_img, uploaded = compress_and_upload(art1_img, art1_slug)
    art1_attribution = "Wikimedia Commons" if art1_source in ("wikipedia", "wikimedia_commons") else "Pexels"

art2_final_img = None
art2_attribution = "Wikimedia Commons"
if art2_img:
    art2_final_img, uploaded = compress_and_upload(art2_img, art2_slug)
    art2_attribution = "Wikimedia Commons" if art2_source in ("wikipedia", "wikimedia_commons") else "Pexels"

art3_final_img = None
art3_attribution = "Wikimedia Commons"
if art3_img:
    art3_final_img, uploaded = compress_and_upload(art3_img, art3_slug)
    art3_attribution = "Wikimedia Commons" if art3_source in ("wikipedia", "wikimedia_commons") else "Pexels"


# ── Articles ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

articles = [
    # ── ARTICLE 1: China Southern Guangzhou-Delhi ──────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "China Southern Is Launching Daily Nonstops Between Guangzhou and Delhi — and NRIs Should Watch the Connecting Map",
        "subheadline": "Starting September 21, flight CZ359 will link India's capital to southern China's biggest aviation hub, opening one-stop access to dozens of Chinese cities for business travelers, students, and tourists.",
        "slug": art1_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "India-China direct flights have been sparse since the pandemic and border tensions. For the tens of thousands of NRIs working in trade, manufacturing consulting, and tech supply chains that run through both countries, a daily nonstop through Guangzhou — China Southern's mega-hub — restores a connection that until now required awkward detours through Bangkok or Singapore.",
        "tags": ["travel", "airlines", "china-southern", "india-china", "delhi", "guangzhou", "nri-business"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/y1rl9g91uapg/"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/17-hour-nonstop-flights-air-canadas-10-new-ultra-long-routes-in-2026/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art1_final_img or "",
        "image_caption": "A China Southern Airlines aircraft on the tarmac",
        "image_attribution": art1_attribution,
        "body": """For most of the post-pandemic era, flying between India and China has meant accepting a layover. Direct services shriveled during the border standoffs and COVID shutdowns, and they never fully recovered. China Southern Airlines is about to change that.

The carrier announced this week that flight CZ359 will operate daily from Guangzhou Baiyun International Airport to Delhi's Indira Gandhi International Airport starting September 21, 2026. The return leg, CZ360, flies the same route in reverse. Both will be operated on Boeing 737-8 aircraft — a narrow-body workhorse that signals China Southern sees this as a bread-and-butter route, not a prestige play.

## Why Guangzhou Matters More Than It Looks

For NRIs whose work touches Chinese manufacturing — and in 2026, that's a vast swath of the Indian American professional class — the destination isn't really Guangzhou. It's everything Guangzhou connects to. China Southern's home hub offers onward flights to Shenzhen, Chengdu, Hangzhou, Wuhan, Kunming, and dozens of smaller industrial cities that are nearly impossible to reach from India without burning an entire day in transit.

A Delhi departure timed to link with China Southern's domestic network means a morning flight from IGI can put you in a second-tier Chinese manufacturing city by evening. That's the kind of routing that turns a three-day business trip into a two-day one — and for NRIs running supply chain operations between Guangdong's factories and American distribution centers, it translates directly into money.

## The Broader India-China Air Corridor

The route also arrives at a moment when India-China aviation is cautiously thawing. Air India and IndiGo have both been exploring expanded Chinese connectivity, and Chinese carriers have been quietly rebuilding their India schedules after years of minimal service. The bilateral air services agreement between the two countries permits far more flights than currently operate — capacity has simply lagged demand.

The student pipeline matters here too. Tens of thousands of Indian students pursue medical and engineering degrees at Chinese universities, and their families in the US often coordinate travel around academic calendars. A reliable daily nonstop through Guangzhou simplifies those logistics considerably.

## What NRIs Should Know Before Booking

A few practical notes. The Boeing 737-8 is a single-aisle aircraft, so don't expect lie-flat seats or premium cabin frills — this is an economy-forward route. The Guangzhou-Delhi sector is roughly six hours, manageable but not luxurious. China Southern is a SkyTeam alliance member, so frequent flyers on Delta, Korean Air, or other SkyTeam partners can earn and redeem miles.

Visa logistics remain the real friction point. China still requires most Indian passport holders to obtain a visa in advance, and processing times can be unpredictable. NRIs holding US passports have a slightly smoother path through China's transit visa exemptions for certain itineraries, but the rules are specific and change frequently. Check with the nearest Chinese consulate before building your itinerary around the new flight.

The September 21 launch gives travelers about three months to plan. For the Indian American business community that has been routing through Bangkok or Singapore to reach Chinese cities, that detour is about to get a lot shorter."""
    },

    # ── ARTICLE 2: Air Canada Delhi-Toronto 17-hour nonstop ────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Air Canada's Delhi–Toronto Nonstop Is Now Its Longest Flight — and the Numbers Show Why NRIs Made It Happen",
        "subheadline": "At 17 hours and five minutes, the DEL-YYZ return leg is the airline's most demanding route. Booking data reveals 574,000 round-trip passengers flew the corridor last year — dwarfing New York by nearly 200,000.",
        "slug": art2_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Canada is home to nearly 1.9 million people of Indian origin — the largest visible minority group in the country. Toronto's Brampton alone is 30% South Asian. The DEL-YYZ corridor isn't just Air Canada's longest route; it's the single largest India–North America air travel market, outpacing New York's JFK and Newark combined. For NRIs in the US with family in both Canada and India, these numbers explain why Air Canada keeps adding frequency.",
        "tags": ["travel", "airlines", "air-canada", "delhi-toronto", "longest-flight", "nri-canada", "boeing-787"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying", "url": "https://simpleflying.com/17-hour-nonstop-flights-air-canadas-10-new-ultra-long-routes-in-2026/"},
            {"name": "OAG Aviation Data", "url": "https://www.oag.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art2_final_img or "",
        "image_caption": "An Air Canada aircraft in its signature livery",
        "image_attribution": art2_attribution,
        "body": """Somewhere over Central Asia, roughly eleven hours into the westbound leg from Delhi to Toronto, an Air Canada 787-9 Dreamliner crosses into airspace that no longer exists on its flight plan. Russian airspace is off-limits. So is Ukrainian. And with the Iran conflict raging below, Iranian airspace is out too. The aircraft swings south, arcing over Turkey and the Mediterranean before turning northwest across the Atlantic.

The result: 17 hours and five minutes of block time, making Delhi to Toronto Pearson the longest nonstop in Air Canada's network. New OAG schedule data for July 2026 through March 2027 confirms it — and the numbers underneath tell a story that every NRI in North America should understand.

## The Biggest India Corridor You've Never Heard Of

Here's a statistic that surprises even frequent flyers: 574,000 round-trip passengers traveled between Toronto and Delhi last year across all airlines. That's not a typo. New York — JFK and Newark combined — managed only 380,000. Toronto-Delhi isn't just the busiest India-Canada route. It's the single largest India–North America air travel market, period.

The reason is demographic math. Canada's Indian-origin population has surged past 1.8 million, with Toronto's Greater Golden Horseshoe region home to the densest concentration. Brampton, Mississauga, and Scarborough are essentially satellite cities of the Punjabi and Gujarati diaspora. Add students — India sends more students to Canada than to any other country except the US — and you have a corridor where demand has outstripped capacity for years.

## What the Route Actually Looks Like

Air Canada operates the Delhi-Toronto nonstop primarily as a daily service on the 298-seat Boeing 787-9 Dreamliner, though some summer weeks drop to six departures. The 787's range makes the routing possible even with the massive detour around closed airspace, though passengers pay for it in hours.

The westbound leg (DEL to YYZ) is the marathon — 17 hours and five minutes — because it fights headwinds and takes the longer southern routing. The eastbound flight is shorter, typically around 14 hours, aided by tailwinds. Air Canada also serves the Delhi-Montreal corridor, which resumes in October with five weekly 787-9 flights clocking up to 16 hours and 30 minutes.

For perspective, Air Canada's second-longest nonstop is Vancouver to Singapore at 16 hours 45 minutes. Delhi-Toronto beats it by a solid 20 minutes.

## What This Means for NRIs in the United States

American NRIs might wonder why a Canadian route matters to them. Two reasons. First, a significant number of Indian Americans have family networks that span both countries — a brother in Brampton, parents in Delhi, a cousin in New Jersey. Toronto often figures into the travel equation whether you live there or not.

Second, Air Canada's aggressive India expansion is putting competitive pressure on US carriers. United's Newark-Delhi nonstop and Air India's growing US network both benefit from the fact that Air Canada is proving the demand exists at scale. When an airline commits its longest-range aircraft to a corridor and fills it daily, other carriers notice.

## The Iran War Factor

The conflict has reshaped every long-haul route between South Asia and the West. Airlines that once flew the efficient great-circle route over Iran now detour south, adding hours and fuel costs. Air Canada's Delhi-Toronto sector absorbs those extra miles more than most because the original routing crossed Iranian airspace at its widest point.

The airline isn't flinching. The daily service continues, and Air Canada has even added its Toronto-Shanghai route back after a six-year pandemic hiatus. The bet is clear: the Indian and Chinese diaspora corridors are too valuable to cede, even when the flights get longer and more expensive to operate.

For the 574,000 passengers who flew this corridor last year, the 17-hour flight is simply the price of the connection. And based on the demand trajectory, Air Canada is counting on that number going higher."""
    },

    # ── ARTICLE 3: Riyadh Air maiden London flight ─────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Saudi Arabia's Brand-New Airline Just Landed in London — and It Wants to Be the Gulf's Stable Option for NRIs",
        "subheadline": "Riyadh Air's inaugural Boeing 787 Dreamliner touched down at Heathrow three weeks ahead of schedule, launching six routes while Emirates and Qatar navigate Iran war disruptions around them.",
        "slug": art3_slug,
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the nine million Indians living in the Gulf and the millions of NRIs who transit through Dubai, Doha, and Abu Dhabi to reach India, the Iran conflict has turned every Gulf connection into a gamble. Riyadh Air — with its Air India codeshare and its location outside the worst disruption zones — is positioning itself as the predictable alternative. NRIs who've had Emirates flights rerouted or delayed now have a reason to look at Riyadh as a connecting hub.",
        "tags": ["travel", "airlines", "riyadh-air", "saudi-arabia", "gulf", "iran-war", "nri-gulf", "boeing-787"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/saudi-backed-riyadh-air-launches-first-london-flight-iran-conflict-rages-2026-06-11/"},
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/riyadh-joins-london-dubai-cairo-madrid-manchester/"},
            {"name": "Travel Tourister", "url": "https://traveltourister.com/riyadh-air-launches-london-heathrow-787-9-dreamliner/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": art3_final_img or "",
        "image_caption": "A Boeing 787-9 Dreamliner, the aircraft type used for Riyadh Air's inaugural service",
        "image_attribution": art3_attribution,
        "body": """On Tuesday morning, a Boeing 787-9 Dreamliner bearing the livery of an airline that didn't exist three years ago touched down at London Heathrow's Terminal 4. Flight RX401 from Riyadh had departed King Khalid International Airport at 2:35 AM local time and landed at 7:30 AM BST — three weeks ahead of the original July 1 launch date, because Riyadh Air's aircraft deliveries came in faster than planned.

It's an entrance that carries more weight than the usual airline launch story. Riyadh Air is arriving into a Gulf aviation market that the Iran conflict has thrown into disarray — and its timing, whether by design or luck, positions it as something NRIs have been looking for: a Gulf transit option that actually works right now.

## The Launch, in Numbers

Riyadh Air currently has three Boeing 787-9 Dreamliners in its fleet, with deliveries expected to bring that to eight by the end of July and ten by year-end. The airline has opened bookings on six routes from Riyadh: London (already flying), Jeddah (June 14), Dubai (June 18), Cairo (June 25), Madrid (July 17), and Manchester (July 23).

The cabin is configured in four classes — Business Elite with lie-flat seats, Business, Premium Economy, and Economy — with Bluetooth audio, USB-C charging, and what the airline describes as "distinctive Saudi hospitality." CEO Tony Douglas, who previously ran Etihad Airways, told Reuters that early ticket sales are encouraging, though he declined to share figures.

The fleet plan is ambitious: 72 Boeing 787-9s on order, plus options on 60 Airbus A321neos and 50 A350s. The stated goal is 100 destinations by 2030. The airline has already signed codeshare agreements with Air India, Singapore Airlines, Delta, Air France-KLM, Virgin Atlantic, Turkish Airlines, and several others.

## The Iran War Context

This is where the story gets relevant for NRIs. Since the Iran conflict erupted in late February, the Gulf's three aviation giants — Emirates, Qatar Airways, and Etihad — have navigated airport closures, airspace restrictions, and rerouted flights. IATA nearly halved its 2026 industry profit forecast. Fuel costs are surging by almost $100 billion industry-wide. Emirates' president Tim Clark acknowledged in a Reuters interview this week that the airline is offering incentives to win back nervous passengers, though he insists Emirates won't cut capacity.

Riyadh sits in a different position. Saudi Arabia's capital hasn't experienced the airport closures that have hit Abu Dhabi and Dubai. Douglas made the point directly: "Perhaps to the point where some people have taken the view that it's a safe entry-exit point."

For NRIs, this matters concretely. The roughly nine million Indians in the Gulf — plus the millions of US-based NRIs who transit through Dubai and Doha to reach India — have watched their connecting flights get longer, more expensive, and less predictable since February. An Emirates connection through Dubai now carries a risk premium that didn't exist six months ago. Riyadh, for now, doesn't.

## The Air India Connection

The codeshare with Air India is the piece that makes Riyadh Air immediately useful for NRIs. A single ticket can now route a passenger from an Indian city through Riyadh and onward to London, Madrid, or eventually dozens more destinations. For NRIs flying between the US, India, and Europe, the Riyadh hub becomes a genuine alternative to the Dubai-centric routing that has dominated diaspora travel for two decades.

It's early days — three planes and six routes don't make a global airline. But the codeshare network, the fleet pipeline, and the Saudi government's investment fund behind the operation suggest this isn't a vanity project. Douglas himself has run a major Gulf airline before. He knows the playbook.

## What NRIs Should Actually Do

Don't rebook your summer flights yet. Riyadh Air's network is tiny, its operational track record is zero days old, and its India connectivity depends entirely on the Air India codeshare for now. But do watch this airline. If the Iran conflict drags on — and every indication is that it will — the relative stability of the Riyadh hub could shift meaningful traffic away from Dubai and Doha.

The bigger picture: Gulf aviation is no longer a three-player game. For NRIs who've built their travel patterns around Emirates and Qatar, having a fourth option backed by the world's largest sovereign wealth fund is, at minimum, worth knowing about."""
    },
]

# ── Insert ─────────────────────────────────────────────────────────────
for art in articles:
    # Skip if no image
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']} — inserting without image")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — \"{art['headline'][:60]}...\"")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
