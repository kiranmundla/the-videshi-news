#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-12 06:00 UTC run."""

import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# --- Image handling ---
from PIL import Image

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

import time

def download_and_upload(source_url, filename):
    """Download image, compress, upload to Supabase storage. Returns public URL."""
    print(f"  Downloading: {source_url[:80]}...")
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
    print(f"  Compressed: {len(raw)} → {len(compressed)} bytes")

    # Upload to Supabase storage bucket 'article-images'
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


# --- Source images ---
print("=== Sourcing images ===")

# Article 1: JW Marriott Ranthambore — Wikipedia image of Ranthambore National Park (1280px thumb)
img1_url = download_and_upload(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ranthambore_National_Park.JPG/1280px-Ranthambore_National_Park.JPG",
    "jw-marriott-ranthambore-luxury-wildlife-nri-20260612.jpg"
)

# Article 2: India's Second-City Tourism — Wikipedia image of Hampi Virupaksha Temple (1280px thumb)
img2_url = download_and_upload(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Wide_angle_of_Galigopuram_of_Virupaksha_Temple%2C_Hampi_%2804%29_%28cropped%29.jpg/1280px-Wide_angle_of_Galigopuram_of_Virupaksha_Temple%2C_Hampi_%2804%29_%28cropped%29.jpg",
    "india-second-city-tourism-hampi-nri-20260612.jpg"
)

# Article 3: Centrum Air Uzbekistan — Wikipedia image of the Registan in Samarkand (1280px thumb)
img3_url = download_and_upload(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Registan_square_Samarkand.jpg/1280px-Registan_square_Samarkand.jpg",
    "centrum-air-uzbekistan-silk-road-nri-20260612.jpg"
)


# --- Articles ---

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Marriott's 10,000th Hotel Just Opened in Rajasthan — and It Puts Ranthambore on the Global Luxury Map",
        "subheadline": "The JW Marriott Ranthambore Resort & Spa marks a historic milestone for the chain and signals India's arrival as a serious luxury wildlife destination for NRI families planning heritage trips home.",
        "slug": make_slug("jw-marriott-ranthambore-luxury-wildlife-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRI families visiting India now have a world-class luxury base for Rajasthan wildlife trips — no more choosing between a tiger safari and a five-star stay.",
        "tags": ["travel", "hotels", "rajasthan", "luxury", "wildlife"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/klmzhee2txat/"},
            {"name": "Marriott International Press Release", "url": "https://www.barchart.com/story/news/32916655/"},
            {"name": "Restaurant India", "url": "https://restaurantindia.in/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url or "",
        "image_caption": "Ranthambore National Park, Rajasthan — home to Marriott's milestone 10,000th property",
        "image_attribution": "Wikimedia Commons",
        "body": """When Marriott International chose the location for its 10,000th hotel worldwide, it did not pick Manhattan or Mayfair. It picked the scrubby, tiger-haunted forests outside a Rajasthani fort town that most global travelers cannot find on a map.

The JW Marriott Ranthambore Resort & Spa opened this week with 127 rooms, suites, and private villas just a short drive from Ranthambore National Park — India's most famous tiger reserve and a UNESCO tentative-list site. For Marriott, it is the capstone of a century-long run from a nine-seat root beer stand in Washington to a portfolio spanning 146 countries. For India, it is a signal that international luxury hospitality now sees the country's wildlife corridors as prime real estate.

## Why Ranthambore, and Why Now

Ranthambore has drawn serious wildlife photographers and monsoon-season adventurers for decades. Its Bengal tiger population is among the most reliably sighted in Asia, and the 10th-century Ranthambore Fort gives the park a historical layer that pure safari destinations lack. But accommodation has long lagged behind the experience. Most visitors have made do with a scattering of boutique lodges and heritage properties. The JW Marriott changes that equation.

The resort brings Marriott's full luxury playbook — modern Indian cuisine, botanical cocktails sourced from Rajasthani herbs, a destination spa, and the Bonvoy loyalty ecosystem that lets points-rich travelers redeem stays in the Indian wild rather than the usual beach-and-city circuit.

## What This Means for NRIs

For the 4.4 million Indian Americans planning trips home this year, Ranthambore has always been a tantalizing detour that rarely made the final itinerary. The problem was never desire — it was infrastructure. Families visiting grandparents in Jaipur or Delhi had few options that matched the hospitality standards they are accustomed to in the US. A JW Marriott changes the calculus. It is a brand NRI travelers already know, a loyalty program they already belong to, and a booking flow they can complete in the same app they use for domestic stays in New York or San Francisco.

The practical math also works. Ranthambore is roughly five hours by road from Jaipur and six from Delhi — a manageable day trip or an overnight that fits neatly into a broader Rajasthan circuit. With Air India's new Easy Connect hub-and-spoke flights linking smaller Indian cities to Delhi, even NRIs flying into non-metro airports can connect through without the old terminal-switching headache.

## A Broader Luxury Bet on India

Marriott is not alone in this wager. The JW Marriott brand now counts more than 130 properties globally, and India is one of its fastest-growing markets. IHG, Hilton, and Hyatt are all racing to plant flags in Indian leisure destinations that were previously underserved by international chains. Rajasthan — with its royal palaces, desert landscapes, and wildlife parks — is the obvious beachhead.

The Ananta Spa & Resort also launched in Jaipur this month with 351 rooms across 40 acres, targeting the destination-wedding market that has become a multi-billion-dollar industry driven in part by NRI families hosting celebrations in India. Dusit International announced a 300-key luxury wellness retreat near Rishikesh, slated for 2031.

## The Tiger Premium

Wildlife tourism is no longer a niche vertical. Globally, luxury safari-style experiences command premiums that outpace city hotels, and India's tiger reserves sit at the intersection of conservation success and rising demand. Ranthambore's tiger count has grown steadily under Project Tiger, and sightings are frequent enough that a two-day visit carries a reasonable chance of a face-to-face encounter with a Royal Bengal tiger — a prospect that safari operators in East Africa cannot always guarantee.

For NRIs, this is the selling point that competes with Kenya, South Africa, and Botswana. The wildlife is comparable, the cultural depth is personal, and — critically — the trip can be folded into a visit home rather than requiring a separate international itinerary.

Marriott's chairman David Marriott was on-site for the opening, alongside Rajeev Menon, who runs Marriott's Asia Pacific operations. "Marking this accomplishment with a property carrying the JW Marriott brand is especially meaningful given its naming after our co-founder, J. Willard Marriott," said CEO Anthony Capuano.

For the Indian traveler — and especially the NRI with Bonvoy points burning a hole in their digital wallet — the message is simpler: the world's biggest hotel company just told you that Ranthambore is worth the trip."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Hidden Destinations Are Having a Moment — and NRIs Should Stop Defaulting to Delhi and Mumbai",
        "subheadline": "A global shift toward 'second-city' tourism is reshaping Indian travel, with places like Hampi, Tawang, and Meghalaya pulling visitors away from overcrowded hubs. For the diaspora, these destinations offer the India their parents described but they have never actually seen.",
        "slug": make_slug("india-second-city-tourism-hampi-meghalaya-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs typically fly into Delhi or Mumbai and visit family — second-city destinations like Hampi, Coorg, and Ziro Valley offer the cultural immersion that a Connaught Place mall cannot.",
        "tags": ["travel", "india", "tourism", "heritage", "destinations"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-second-city-tourism/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Allianz Partners Global Travel Confidence Index 2026", "url": "https://www.outlooktraveller.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url or "",
        "image_caption": "The Virupaksha Temple at Hampi, Karnataka — one of India's emerging second-city destinations drawing global travelers",
        "image_attribution": "Wikimedia Commons",
        "body": """The annual NRI trip to India follows a familiar script. Fly into Delhi or Mumbai. Spend most of the visit at a relative's house. Maybe squeeze in a day at a mall and a meal at a restaurant that did not exist last time. Fly home having seen a lot of family and very little of the country.

A growing global trend is challenging that pattern. Travelers worldwide are abandoning overcrowded capital cities for lesser-known destinations that offer richer cultural experiences, cheaper prices, and fewer selfie sticks. India has joined this "second-city" movement alongside Portugal, Japan, Italy, and South Korea — and the destinations pulling travelers off the beaten path are precisely the places that NRIs have heard about for years but never bothered to visit.

## The Places Rewriting the Map

Hampi in Karnataka — a UNESCO World Heritage Site with 14th-century Vijayanagara ruins scattered across a surreal boulder landscape — is seeing visitor numbers climb steadily. Tawang in Arunachal Pradesh, home to the second-largest Buddhist monastery in the world after Lhasa's Potala Palace, is attracting trekkers and spiritual travelers who have grown tired of Rishikesh's yoga-tourist circuit. Ziro Valley in the same state draws music lovers to its annual outdoor festival set among rice paddies and pine forests.

Then there is Meghalaya, where the living root bridges of Cherrapunji have become one of India's most photographed natural wonders. Orchha in Madhya Pradesh — an entire medieval city of cenotaphs and palaces that receives a fraction of nearby Khajuraho's visitors. Gokarna on the Karnataka coast, where the beaches rival Goa without the nightclub infrastructure. And Coorg, the coffee-growing hill district in Karnataka that offers plantation stays, misty mornings, and Kodava cuisine that barely exists outside the region.

## Why NRIs Are the Perfect Audience

The Allianz Partners Global Travel Confidence Index, released this week, found that 86 percent of Indian respondents consider holidays a necessity rather than a luxury — and that travelers are not canceling trips in the face of rising costs but adjusting where and how they travel. For NRIs, the adjustment is overdue.

Most Indian Americans spend their India visits in the three or four cities where their families live. The idea of adding a four-day detour to Hampi or a weekend in Meghalaya barely registers because the logistics seem daunting and the destinations feel obscure. But improved regional connectivity — budget airlines now serve Guwahati, Bagdogra, Hubli, and Imphal with reasonable frequency — has quietly made these places accessible in ways they were not five years ago.

The cost differential is also significant. A night at a heritage guesthouse in Orchha runs a fraction of what a comparable hotel costs in Delhi. A week in Coorg, including a plantation stay and guided nature walks, can cost less than a single weekend in a Mumbai luxury hotel.

## The Infrastructure Is Catching Up

India's second-tier tourism destinations have historically suffered from a hotel gap — stunning landscapes with accommodation options that ranged from basic to alarming. That is changing. Boutique hotel operators, homestay platforms, and international chains are all moving into these markets. The Oberoi Rajgarh Palace near Khajuraho, which just made the Prix Versailles list of the world's 16 most beautiful hotels, is proof that luxury hospitality can thrive outside the metros.

Regional airports are expanding. Road infrastructure under the Bharatmala programme has improved access to destinations that once required bone-rattling drives. And digital booking platforms have removed the information barrier that kept these places invisible to international travelers.

## A Different Kind of Homecoming

For the 32 million-strong Indian diaspora, second-city travel offers something that Delhi and Mumbai cannot: a connection to the India that exists between the airports. The temple architecture of Hampi, the monasteries of Tawang, the living forests of Meghalaya — these are the stories that grandparents told, and they are still there, waiting for a generation that has the means to reach them but has never thought to try.

The global second-city trend is not about rejecting capital cities. It is about recognizing that the most interesting parts of any country are usually the parts that tourists have not yet overrun. India has more of those places than almost anywhere else on earth. NRIs who have been making the same Delhi-Mumbai-Bangalore triangle for twenty years might consider breaking the loop.

The flights are cheaper, the hotels are better, and the Instagram photos will be considerably more interesting."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Uzbekistan Just Became Five Flights a Week Closer to India — and NRIs Should Add the Silk Road to Their Next Trip Home",
        "subheadline": "Centrum Air's expanded India-Uzbekistan schedule reflects surging Indian demand for Central Asian travel. For NRIs visiting family, Samarkand and Bukhara are now a short side trip away from Delhi.",
        "slug": make_slug("centrum-air-uzbekistan-silk-road-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs visiting India can add a 3-4 day Silk Road detour to Samarkand or Bukhara — Uzbekistan offers visa-free entry for Indian passport holders, and the new flight frequency makes it a realistic side trip.",
        "tags": ["travel", "airlines", "uzbekistan", "silk-road", "central-asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "BW Travel", "url": "https://bwtravel.com/"},
            {"name": "Travel Mail India", "url": "https://travelmail.in/"},
            {"name": "India Outbound", "url": "https://indiaoutbound.info/"}
        ]),
        "score_total": 68,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3_url or "",
        "image_caption": "The Registan square in Samarkand, Uzbekistan — now five flights a week from India",
        "image_attribution": "Wikimedia Commons",
        "body": """Central Asia has spent decades as the blind spot on the Indian traveler's map — a region that appears in history textbooks (the Silk Road, Babur, Timur) but almost never on a boarding pass. That is changing fast, and the numbers are hard to ignore.

Centrum Air, Uzbekistan's fastest-growing private carrier, announced this week that it is increasing its India services to five flights per week, up from the three-weekly frequency it launched with. The expansion is a direct response to what the airline's founder Abdulaziz Abdurakhmanov called "growing passenger demand" on a route that barely existed a few years ago.

## Why Uzbekistan, and Why Now

Uzbekistan has quietly executed one of the most effective tourism pivots in recent memory. Under President Shavkat Mirziyoyev, the country dismantled its Soviet-era visa apparatus and opened its doors to visitors from dozens of countries — including India, whose passport holders now enjoy visa-free entry for stays up to 30 days. The result has been a tourism boom driven by three things: Silk Road heritage cities, competitive pricing, and a strategic location that makes it reachable from Delhi in roughly four hours.

Samarkand's Registan square — three madrasas arranged around a public plaza that has been called the most beautiful in Central Asia — is the obvious anchor. But the country offers far more. Bukhara's old town is a labyrinth of 9th-century mosques and trading domes. Khiva's walled inner city looks like a film set. And the Aral Sea region, while sobering, has become a draw for travelers interested in environmental tourism.

## The NRI Angle: A Side Trip That Actually Works

For the millions of Indian Americans who fly to Delhi or Mumbai every year, Uzbekistan has historically been invisible. It sits in a mental category alongside other "-stans" that sound vaguely complicated. The reality is different. A round trip from Delhi to Tashkent takes about the same time as Delhi to Goa. The visa is free. English signage across tourist areas has improved dramatically. And a four-day Silk Road circuit — Tashkent to Samarkand to Bukhara, all connected by high-speed rail — costs a fraction of a comparable European trip.

The cultural connections also run deep, though they are rarely discussed. Babur, the founder of the Mughal dynasty that built the Taj Mahal, was born in Andijan, Uzbekistan. The architectural DNA of Samarkand's tilework appears in Delhi's Humayun's Tomb and Agra's mosques. For NRIs interested in the full arc of Indian history, Uzbekistan is not a foreign destination — it is a prequel.

## The Bigger Picture: India-Central Asia Connectivity

Centrum Air is not operating in a vacuum. Air Astana connects India to Kazakhstan. Turkish Airlines and flydubai offer one-stop connections to Tashkent through their respective hubs. But direct service matters — it collapses a two-leg itinerary into a single flight and eliminates the transit-visa complications that have historically made Central Asia inconvenient for Indian passport holders.

The Indian government has also been pushing for deeper ties with Central Asia. Prime Minister Modi has visited the region multiple times, and the India-Central Asia Summit has established a framework for expanded connectivity, trade, and people-to-people exchange. Aviation routes are one of the most tangible outcomes of that diplomatic push.

## What Five Flights a Week Actually Means

Three weekly flights made Uzbekistan a possibility. Five make it a plan. The additional frequency means travelers can fly out on a Monday and return on a Thursday without burning an entire week waiting for the next departure. For NRIs who are already juggling limited vacation days between family obligations and personal travel, that scheduling flexibility is the difference between "interesting idea" and "booked."

Centrum Air's general sales agent in India, Aeroprime Group, reported that the response from both leisure and trade travelers has been "extremely encouraging." The airline is positioning Uzbekistan not just as a standalone destination but as a gateway to the broader Central Asian region — Kazakhstan, Kyrgyzstan, and Tajikistan are all within easy reach from Tashkent.

## The Practical Details

Round-trip fares on the India-Uzbekistan route currently hover around $300-400, though promotional deals have been lower. Uzbekistan's som-based economy means on-the-ground costs are remarkably low by Indian standards — a quality restaurant meal in Samarkand rarely exceeds $10, and guesthouse accommodations in Bukhara start around $25 per night.

The country's tourism infrastructure has improved markedly. The Afrosiyob high-speed train covers Tashkent to Samarkand in just over two hours. Hotels range from converted caravanserais to modern international chains. And the Uzbek hospitality tradition — centered on plov, green tea, and a warmth toward Indian visitors that borders on enthusiastic — makes the experience feel less foreign than many closer destinations.

For NRIs who have done Bali, done Dubai, and done Thailand, Uzbekistan is the next trip that nobody in their friend circle has taken yet. With five flights a week, the excuse list just got shorter."""
    },
]


# --- Insert articles ---
print("\n=== Inserting articles ===")
for art in articles:
    if not art["image_url"]:
        print(f"⚠ No image for {art['slug']}, inserting anyway")
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\nDone!")
