#!/usr/bin/env python3
"""Travel writer — 2026-06-01 18:00 UTC batch. Three articles."""
import json, os, uuid, re, requests
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

def verify_image(url):
    """Check that an image URL returns 200 with image content-type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Image OK: {url[:80]}... ({cl} bytes)")
            return url
        # Some servers don't return Content-Length on HEAD, try GET with stream
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        chunk = r2.raw.read(6000)
        r2.close()
        if r2.status_code == 200 and "image" in ct2 and len(chunk) > 5000:
            print(f"  ✓ Image OK (GET verify): {url[:80]}...")
            return url
    except Exception as e:
        print(f"  ⚠ Image check failed for {url[:60]}: {e}")
    return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── Images ──────────────────────────────────────────────────────────────
img_kovalam = verify_image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Kovalam_beach_trivandrum_kerala.jpg/1200px-Kovalam_beach_trivandrum_kerala.jpg")
img_hampi = verify_image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Wide_angle_of_Galigopuram_of_Virupaksha_Temple%2C_Hampi_%2804%29_%28cropped%29.jpg/1200px-Wide_angle_of_Galigopuram_of_Virupaksha_Temple%2C_Hampi_%2804%29_%28cropped%29.jpg")
img_jaipur = verify_image("https://upload.wikimedia.org/wikipedia/commons/4/41/East_facade_Hawa_Mahal_Jaipur_from_ground_level_%28July_2022%29_-_img_01.jpg")

# Pexels fallbacks
if not img_kovalam:
    img_kovalam = "https://images.pexels.com/photos/17928231/pexels-photo-17928231.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
if not img_hampi:
    img_hampi = "https://images.pexels.com/photos/31143502/pexels-photo-31143502.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
if not img_jaipur:
    img_jaipur = "https://images.pexels.com/photos/3581364/pexels-photo-3581364.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# ── Articles ────────────────────────────────────────────────────────────

articles = [
    # ── 1. Kerala GTM 2026 ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Kerala Launches Its Biggest Travel Expo Yet — and the Ayurveda Pitch Is Aimed Squarely at NRIs",
        "subheadline": "The second edition of the Global Travel Market opens June 3 in Kovalam, assembling 1,000-plus operators and 300 corporate buyers to sell the world on Kerala's wellness credentials.",
        "slug": make_slug("kerala-global-travel-market-2026-ayurveda-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Kerala's 3.5 million-strong diaspora in the Gulf, US, and UK is the state's most reliable tourism pipeline. GTM 2026 is expected to produce new wellness packages priced at $2,000-$4,000 for 10-14 day stays — specifically designed for NRIs combining family visits with Ayurveda retreats.",
        "tags": ["travel", "kerala", "ayurveda", "wellness-tourism", "gtm-2026"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3360941-kerala-to-host-global-travel-market-2026-in-june"},
            {"name": "AIR News", "url": "https://airnews.in/2026/05/30/kerala-cm-vd-satheesan-opens-gtm-2026/"},
            {"name": "BizzBuzz", "url": "https://www.bizzbuzz.news/nation/kerala-gears-up-to-host-global-travel-market-from-june-3-1393199"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": img_kovalam,
        "image_attribution": "Wikimedia Commons",
        "body": """The state that gave the world Ayurveda is doubling down on its biggest export. Kerala's Global Travel Market (GTM) 2026 opens on Tuesday, June 3, at the Uday Samudra Leisure Beach Hotel in Kovalam, Thiruvananthapuram, with Chief Minister V.D. Satheesan presiding over what organisers describe as South India's premier B2B tourism platform.

The numbers suggest they are not exaggerating. More than 1,000 domestic and international tour operators, over 300 corporate buyers, and representatives from Sri Lanka, Andhra Pradesh, and Tamil Nadu will converge over three days of networking sessions, matchmaking meetings, and a 200-stall expo at the Golden Palace Convention Centre in Amaravila. The inaugural edition in 2022 recorded 650 exhibitors and generated ₹1.2 billion in export-linked bookings. This year's targets are considerably more ambitious.

## The Ayurveda play

A dedicated Ayurveda pavilion will pitch Indian wellness packages to global operators — a deliberate escalation of Kerala's strategy to position itself not merely as a beach-and-backwaters destination, but as Asia's answer to Switzerland's medical tourism circuit. The state has been steadily upgrading its wellness infrastructure, with certified Ayurveda resorts now numbering in the hundreds and government-backed quality standards that foreign insurers are beginning to recognise.

For Kerala's tourism ministry, the timing is strategic. Tourism accounts for roughly 13 percent of the state's GDP and employs over 1.2 million workers. The GTM is the first major tourism convergence since the current government took office, and the presence of Union Minister of State for Tourism Suresh Gopi signals Delhi's buy-in.

## Why NRIs should care

Kerala's diaspora — estimated at 3.5 million worldwide, with significant concentrations in the Gulf states, the United States, and the United Kingdom — has always been the state's most reliable tourism pipeline. Malayali families in Houston, Chicago, and the Bay Area routinely plan annual trips home that blend family visits with temple pilgrimages and, increasingly, Ayurveda wellness retreats.

The GTM's B2B sessions are expected to produce new tour packages specifically designed for this segment: multi-week itineraries combining Ayurveda treatment courses with cultural circuits through Kochi's Fort area, Munnar's tea plantations, and Alleppey's backwaters. Several operators previewing their GTM offerings have confirmed packages priced between $2,000 and $4,000 for 10-to-14-day stays — competitive with wellness retreats in Bali or Thailand, but with the added pull of family proximity.

Direct flight connectivity is also improving. Air India Express and IndiGo both operate regular services between the Gulf and Kochi/Trivandrum, and Air India's expanding long-haul network now includes a nonstop Kochi–London service. For US-based NRIs, the most common routing — through Dubai or Doha to Kochi — remains efficient, though the Iran conflict has added uncertainty to some Gulf transit options.

## The broader Kerala bet

Kerala's tourism push extends beyond the GTM. France recently joined the United States, United Kingdom, Australia, and Japan as a key source market that Kerala's tourism board is actively courting, with French operators showing particular interest in sustainable and experience-driven travel. The state is also investing in its houseboat fleet's sustainability credentials, phasing in solar-powered boats on the Vembanad Lake circuit and expanding responsible tourism initiatives that let visitors stay in village homestays rather than resort complexes.

## What to watch

The GTM Metro Expedition Award Night on June 4 at The Leela Kovalam will recognise operators who have driven the most significant tourism flows into the state. The expo opens to the public on June 5, offering locals and visitors a direct window into the tourism products being pitched to global buyers.

For NRIs planning a trip to Kerala this monsoon season — which, despite the IMD's forecast of below-normal rainfall, still delivers the lush green landscapes and cooled temperatures that make the state's hospitality sector hum — the new package announcements in the coming weeks will be worth watching. The wellness retreats are getting better. The flights are getting more direct. And Kerala knows exactly who it is selling to."""
    },

    # ── 2. India's 100M arrivals target ─────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants 100 Million Tourists a Year by 2047 — and the Strategy Begins Where the Golden Triangle Ends",
        "subheadline": "The Union Tourism Ministry's decentralized eco-tourism push aims to lift tourism's share of GDP above 7 percent by 2030, steering visitors — and their wallets — beyond Delhi, Agra, and Jaipur.",
        "slug": make_slug("india-100-million-tourists-2047-eco-tourism-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the 4.7 million-strong Indian diaspora in the US, the government's infrastructure push means ancestral towns are becoming easier to reach — better domestic flights, branded hotels in pilgrimage cities, and IRCTC luxury trains connecting temple towns that once required overnight bus rides.",
        "tags": ["travel", "india-tourism", "eco-tourism", "heritage", "infrastructure"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/india-dominates-global-trends-witness-the-sensational-expansion-of-decentralized-eco-tourism-destinations/"},
            {"name": "Outlook Business (DigiYatra)", "url": "https://www.outlookbusiness.com/news/govt-says-27-more-airports-to-have-digiyatra-by-next-year"},
            {"name": "Travel And Tour World (Delhi IGI)", "url": "https://www.travelandtourworld.com/news/article/asias-leading-nations-airports-expand-routes/"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": img_hampi,
        "image_attribution": "Wikimedia Commons",
        "body": """India receives roughly 10 million foreign tourist arrivals a year. The government wants that number to hit 100 million by 2047, the centenary of independence. To get there, the Union Tourism Ministry is betting on a strategy that sounds deceptively simple: send people places they have never considered going.

The ministry's recently articulated vision centres on what officials call "decentralized eco-tourism destinations" — a bureaucratic phrase for a genuinely ambitious idea. Instead of concentrating visitor flows on the Golden Triangle and a handful of beach destinations in Goa and Kerala, the plan aims to distribute tourism across India's 28 states and 8 union territories by developing heritage circuits, spiritual corridors, and eco-tourism clusters in regions that currently attract minimal foreign footfall.

## The numbers behind the ambition

Tourism currently contributes roughly 5 percent of India's GDP, according to the World Travel and Tourism Council. The government's target of 7 percent by 2030 would require adding tens of billions of dollars in tourism revenue — a leap that cannot come from Agra's existing Taj Mahal turnstile alone.

The infrastructure push is real. India has opened or upgraded dozens of airports in the past five years, and the latest Skytrax rankings placed five Indian airports in the global top 100 — a first. DigiYatra's facial recognition system, now live at 38 airports with 27 more being added by next year, is cutting passenger processing times from 15 seconds to five. Annual passenger traffic across Indian airports is projected to reach 500 million by 2030 and nearly one billion by 2040, according to Civil Aviation Minister K. Rammohan Naidu.

## Where the new tourism corridors lead

The destinations the government is developing read like a bucket list for NRIs who have exhausted the standard circuit. Hampi, the ruins of the Vijayanagara Empire in Karnataka, is getting improved road access and a new visitor centre. Odisha's Konark Sun Temple complex is being expanded with upgraded facilities. The Buddhist circuit — Bodh Gaya, Sarnath, Kushinagar, Rajgir — is receiving railway upgrades aimed at Japanese and Southeast Asian pilgrims. Meghalaya's living root bridges and Arunachal Pradesh's tribal homestays are being positioned as premium eco-tourism experiences.

The spiritual tourism corridor is perhaps the most NRI-relevant. IRCTC's luxury trains — including the recently relaunched Golden Chariot for South India — now connect temple towns that diaspora families have traditionally reached only by gruelling overnight bus rides. The Varanasi–Ayodhya–Prayagraj circuit, energised by the Ram Mandir's inauguration, is drawing domestic visitors in numbers that strain existing hotel capacity.

## What this means for NRIs

For the 4.7 million-strong Indian diaspora in the United States, India visits have historically followed a predictable pattern: fly into Delhi or Mumbai, attend a family wedding or festival, squeeze in a Taj Mahal visit if time permits, fly home. The government's decentralization strategy aims to break that pattern by making it genuinely easier — better flights, better roads, better hotels — to explore regions that NRIs often know only from their parents' stories.

The hotel supply is responding. India's branded hotel pipeline now exceeds 70,000 rooms under construction, with the fastest growth in tier-two cities like Varanasi, Jaipur, Lucknow, and Kochi. International chains including Marriott, Hilton, and ITC are expanding aggressively beyond the metros, a bet that business and leisure demand in these cities will justify the investment.

## The catch

Getting from 10 million to 100 million annual arrivals is a tenfold increase in roughly two decades. No major country has achieved that pace, and India's challenges — visa processing delays, inconsistent hygiene standards, and safety perceptions among solo female travellers — remain formidable. The hardware is improving faster than the soft skills, and the gap between a polished airport lounge and the experience of navigating an Indian city on arrival remains wide.

But the direction of travel is unmistakable. India is building the infrastructure for a tourism economy that matches its cultural pull. For NRIs who have not visited in a few years, the India that greets them next may already look substantially different from the one they remember."""
    },

    # ── 3. Asia's Tier-Two Cities Boom ──────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Asia's Tier-Two Cities Are Having a Tourism Moment — and India's Jaipur, Kochi, and Ahmedabad Are Leading the Pack",
        "subheadline": "Flight rerouting, rising hub-city costs, and a growing appetite for authentic experiences are channelling travelers to secondary cities across the continent — and India's smaller airports are finally ready for them.",
        "slug": make_slug("asia-tier-two-cities-tourism-boom-india-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For NRIs, the secondary city boom means ancestral towns are easier and cheaper to reach than ever. A round-trip Delhi-to-Jaipur or Mumbai-to-Kochi domestic hop costs under $50 on IndiGo or Akasa, and branded hotels are now available even in pilgrimage towns.",
        "tags": ["travel", "tier-two-cities", "india-tourism", "domestic-flights", "hotels"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/iran-war-middle-east-disruptions-fuel-tourism-boom-asia-secondary-cities/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-warns-weakest-monsoon-11-years-inflation-risks-rise-2026-05-29/"},
            {"name": "Travel And Tour World (Asia Airports)", "url": "https://www.travelandtourworld.com/news/article/asias-leading-nations-airports-expand-routes/"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": img_jaipur,
        "image_attribution": "Wikimedia Commons",
        "body": """The tourism map of Asia is being redrawn in real time, and the beneficiaries are not the capitals. Across the continent, secondary cities — places that rarely featured on mainstream travel itineraries a decade ago — are posting record visitor numbers in 2026, driven by a convergence of higher hub-city costs, Middle East flight disruptions, and a generational shift toward destinations that offer authenticity over Instagram backdrops.

In India, the shift is particularly visible. Jaipur, long the least-visited leg of the Golden Triangle for international travelers, has seen hotel bookings surge this spring. Kochi is posting its strongest tourism numbers since the pandemic. Ahmedabad — India's first UNESCO World Heritage City — is appearing in Western travel publications as a serious food-and-architecture destination. And Lucknow, the Nawabi capital of Uttar Pradesh, is attracting a growing stream of domestic and diaspora travelers drawn by its Mughal-era cuisine and newly improved air connectivity.

## What changed

Three forces are converging. First, the Iran war and broader Middle East disruptions have forced airlines to reroute and raised the cost of long-haul flights transiting through Gulf hubs — the primary corridor for India-bound traffic from Europe and North America. With Dubai and Doha connections getting more expensive and less predictable, some travelers are opting for direct flights into secondary Indian airports or rerouting through Southeast Asian hubs entirely.

Second, India's airport infrastructure buildout is reaching beyond the metros. Noida International Airport opens on June 15, giving Delhi-NCR a second gateway. Bengaluru has overtaken Mumbai as India's second-busiest airport. Smaller airports in Jaipur, Lucknow, Varanasi, and Coimbatore have received terminal upgrades and new carrier allocations from IndiGo, Air India Express, and Akasa Air, making domestic connections cheaper and more frequent than they have ever been.

Third, the travel preferences of younger Indian Americans are shifting. The generation that grew up visiting grandparents in Delhi or Mumbai is now old enough to plan their own trips, and they are gravitating toward cities that feel less like tourist circuits and more like living cultures. A weekend in Jaipur's walled city, with its dyers' quarter and stepwells, offers something that five-star Delhi increasingly does not.

## The numbers tell the story

Across Asia, the pattern is consistent. Thailand's secondary cities — Chiang Rai, Khon Kaen, Udon Thani — are seeing stronger hotel demand than Bangkok. Japan's Kanazawa, Takayama, and Kumamoto are drawing visitors away from Tokyo and Osaka. Vietnam's Da Nang and Hue are growing faster than Ho Chi Minh City.

In India, routes connecting tier-two cities — Jaipur to Kochi, Lucknow to Bengaluru, Ahmedabad to Hyderabad — have posted double-digit growth in passenger loads this quarter, even as overall domestic capacity has been constrained by the government's decision to cut 250 flights daily to manage summer congestion.

The hotel industry is responding in kind. Branded hotel rooms under construction in Indian tier-two cities outnumber those in the top six metros for the first time. Marriott, ITC, and Taj are all building properties in cities that would have seemed commercially questionable five years ago.

## What NRIs should know

For diaspora travelers, the secondary city boom is an opportunity disguised as a disruption. Direct domestic flights from hub airports to ancestral towns are more plentiful and affordable than they have been in years. A round-trip Delhi-to-Jaipur or Mumbai-to-Kochi domestic hop costs under $50 on IndiGo or Akasa. Hotel quality in tier-two cities has improved dramatically, with branded options now available in pilgrimage towns and district headquarters alike.

The cultural payoff is real. NRIs who have not visited their parents' hometown in a few years will find cities that have changed faster than the metros in some respects — better roads, more restaurants, functional public transport — while retaining the neighbourhood textures that make them feel distinctly different from anywhere in the West.

## The bottom line

Asia's tourism geography is flattening. The era when a trip to India meant Delhi-Agra-Jaipur-Goa is giving way to something more distributed, more personal, and — for the diaspora — potentially more meaningful. The flights are there. The hotels are there. The only question is whether NRIs will look beyond the familiar."""
    },
]

# ── Insert ──────────────────────────────────────────────────────────────
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
