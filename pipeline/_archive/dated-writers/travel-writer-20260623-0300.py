#!/usr/bin/env python3
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

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

GUW_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Lokpriya_Gopinath_Bordoloi_International_Airport.jpg/1280px-Lokpriya_Gopinath_Bordoloi_International_Airport.jpg"
THAI_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/%E0%B9%80%E0%B8%88%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B9%8C%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%87%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%87%E0%B8%84%E0%B9%8C%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B8%AD%E0%B8%A3%E0%B8%B8%E0%B8%932.jpg/1280px-%E0%B9%80%E0%B8%88%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B9%8C%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%87%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%87%E0%B8%84%E0%B9%8C%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B8%AD%E0%B8%A3%E0%B8%B8%E0%B8%932.jpg"

guwahati_body = """Northeast India's diaspora has spent a generation flying the long way home. From Dubai or Abu Dhabi, the trip to Guwahati has always meant a stop in Delhi or Kolkata — a domestic transfer, an overnight, a re-check of bags, and the particular dread of a missed connection during monsoon. From August 4, that detour disappears.

Air India will begin nonstop flights from Guwahati's Lokpriya Gopinath Bordoloi International Airport to both Dubai and Abu Dhabi, Assam Chief Minister Himanta Biswa Sarma announced on June 22. The two routes give the Northeast its first direct link to the Gulf, and they hand the region's large worker-and-family diaspora in the Emirates something they have never had: a single boarding pass from the UAE straight into Assam.

## Why the Northeast diaspora has waited so long

Guwahati is the gateway to all of Northeast India — Assam, Meghalaya, Nagaland, Manipur, Arunachal and the rest. Hundreds of thousands from the region work across the Gulf, concentrated in construction, hospitality and healthcare in the UAE. Until now, none could fly home without routing through a major mainland hub. With the new services, Bordoloi International will be directly connected to four countries — the UAE, Thailand, Singapore and Bhutan — turning a regional airport into a genuine international gateway.

The timing is not coincidental. Sarma noted the routes come "just days after European Union member states lifted their travel advisory for Assam," a diplomatic signal he tied directly to the commercial opening. The state government has made international air links a centerpiece of its plan to position Guwahati as the gateway to Southeast Asia, and the CM said his next target is a direct Guwahati–Vietnam service.

## What it means for NRIs

For the Assamese and Northeastern diaspora in the US, UK and Canada, the change is indirect but real. A family in New Jersey or Toronto flying to visit relatives in Jorhat or Dibrugarh has long faced the same multi-leg ordeal — a transatlantic or transpacific haul, a Gulf or Delhi connection, and then the final domestic hop into Guwahati with its own re-check and weather risk. A nonstop Gulf–Guwahati leg removes one of the most fragile links in that chain. Routing through Dubai or Abu Dhabi — both of which the major US and Canadian gateways already serve heavily — now puts the Northeast within one connection of North America rather than two or three.

It also matters for the growing number of NRIs with roots in the region who have avoided bringing aging parents on the journey precisely because of the connection burden. A single transfer in the Gulf is a different proposition from a two-stop itinerary with an overnight in Delhi.

## The bigger picture: India's regional airports go global

The Guwahati announcement lands in the middle of a broader shift. On July 15, Air India Express will begin the first international service from the new Navi Mumbai International Airport, a twice-weekly Abu Dhabi link scaling to three flights a week from July 29. Both moves point the same direction: India's aviation map is no longer drawn only through Delhi and Mumbai's saturated mega-hubs. Tier-two and regional airports are being wired straight into the Gulf, the diaspora's most-used transfer point.

For NRIs, the practical upshot is more choice and fewer pinch points. The Gulf carriers and Air India's own widebody network already move the bulk of India-bound diaspora traffic through Dubai, Abu Dhabi and Doha; feeding regional Indian cities directly off those hubs means the last leg home stops being the weakest part of the trip.

## What's next

Air India has not yet published the full weekly frequency or aircraft type for the Guwahati routes, and fares on the related Air India Express Gulf services from the Northeast are currently listed from around ₹14,000–₹20,000 one-way. Bookings are expected to open in the run-up to the August 4 launch. Travelers should watch for whether the carrier runs the routes daily or a few times a week, since frequency will determine how useful the connection is for tight onward itineraries from North America.

For now, the headline is simple: after years of flying home the long way, the Northeast diaspora finally gets a straight line back to Assam."""

thailand_body = """For most of the past two years, Thailand was the easiest big trip an Indian passport could buy. Sixty days visa-free, extendable by thirty more, no paperwork, no fee — it turned Bangkok into something close to a domestic weekend for Indian travelers and made Thailand the single most-searched international destination from India. That era is over.

Under a sweeping immigration overhaul its Cabinet approved on May 19, Thailand has dropped India from its visa-free list entirely and moved Indian passport holders into the Visa on Arrival (VoA) category. The new rules are now in force, and they reset the math for one of the diaspora's favorite stopover and family-trip destinations.

## What actually changed

The old deal was generous: visa-free entry for up to 60 days, with a 30-day extension available on the ground. The new deal is narrower. Indian travelers now get visa on arrival only — a single-entry, 15-day permit, purchased at the immigration counter for 2,000 Thai baht (roughly ₹4,600–₹5,800), payable in Thai baht cash. India is one of only four countries placed in this VoA bracket, alongside Azerbaijan, Belarus and Serbia.

Bangkok's stated reason is misuse: authorities say the long visa-free window was being exploited for informal long-term residency and unofficial work rather than genuine tourism. The government has been explicit that short-stay tourists are not the target. "If you're visiting Thailand for a holiday, a honeymoon, or a family trip, you're still very welcome," its Ministry of Foreign Affairs said.

## Does it actually hurt the typical trip?

For most NRI itineraries, less than it sounds. A standard Thailand holiday — a 4-night or 6-night Bangkok–Pattaya–Phuket circuit — fits comfortably inside a 15-day window. The practical changes are three: you now pay a fee where there was none, you carry Thai baht in cash to the counter, and you lose the ability to linger for weeks or to bounce in and out on the old extendable terms.

Where it bites is the longer, looser trip. Diaspora families who used Thailand as a month-long base, digital nomads, and frequent in-and-out travelers lose the most. The single-entry limit also matters for anyone who planned to pair Thailand with a side trip — say, a hop to Cambodia or Vietnam and back — since re-entry now means a fresh VoA each time.

## Why this matters for the diaspora specifically

Thailand is not only a holiday destination for NRIs — it is a transit and gathering point. Bangkok is a common meeting ground for extended families split between India and the West, an easy mid-point where relatives flying from California and cousins flying from Chennai can converge without anyone needing a hard-to-get visa. The 15-day cap and the per-entry fee complicate the longer multi-generational reunions that made Thailand attractive in the first place.

It also lands amid a wider tightening of travel rules that NRIs are tracking closely — Japan raising its visa fee fivefold and hiking its departure tax, Europe pricing its forthcoming ETIAS authorization, and the US adding new fees of its own. Thailand's move fits the pattern: the frictionless-travel window that opened across much of Asia after the pandemic is quietly narrowing.

## How to plan around it

A few practical points for travelers booking now. Carry the VoA fee in Thai baht cash — card payment is not accepted at the counter. Keep your trip inside 15 days, or apply for a proper tourist visa in advance through a Thai mission if you need longer. Have return tickets and accommodation proof ready; immigration is leaning harder on onward-travel evidence. And if your itinerary involves leaving and re-entering Thailand, budget for a new VoA on each entry rather than assuming a single permit covers the whole trip.

For the weekend-in-Bangkok crowd, the change is a modest fee and a baht run at the airport. For the linger-a-month crowd, it is the end of an unusually good run."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India Just Gave the Northeast Diaspora a Straight Line Home — Nonstop Guwahati–Gulf Flights Start August 4",
        "subheadline": "For the first time, Assam and the wider Northeast get direct links to Dubai and Abu Dhabi, cutting the Delhi-or-Kolkata detour that has long made the trip home a gamble.",
        "slug": make_slug("air-india-guwahati-dubai-abu-dhabi-nonstop-northeast-diaspora-nri"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "Nonstop Guwahati-Gulf flights put the Northeast diaspora's home region one connection from North America instead of two or three, removing the most fragile leg of the journey to Assam.",
        "tags": ["travel", "airlines", "air india", "guwahati", "uae", "northeast india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Tribune / NewKerala (CM Sarma announcement)", "url": "https://www.newkerala.com/news/2026/"},
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/"},
            {"name": "Nation Press", "url": "https://www.nationpress.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": GUW_IMG,
        "image_caption": "Lokpriya Gopinath Bordoloi International Airport in Guwahati, the Northeast's gateway hub",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": guwahati_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Thailand Just Took Indians Off Its Visa-Free List — Bangkok Now Costs a Fee and a 15-Day Clock",
        "subheadline": "India has been moved from 60-day visa-free entry to a single-entry visa on arrival, reshaping the math for the diaspora's favorite stopover and family-reunion destination.",
        "slug": make_slug("thailand-india-visa-on-arrival-end-visa-free-nri-bangkok"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Thailand's switch from visa-free to a 15-day visa on arrival complicates the long, multi-generational reunions and Bangkok stopovers that NRIs lean on, while leaving short holidays largely intact.",
        "tags": ["travel", "visa", "thailand", "immigration", "bangkok"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Thailand Ministry of Foreign Affairs (via Medium explainer)", "url": "https://medium.com/"},
            {"name": "Visa requirements for Indian citizens - Wikipedia", "url": "https://en.wikipedia.org/wiki/Visa_requirements_for_Indian_citizens"},
            {"name": "Platinumlist Henley Passport Index 2026 guide", "url": "https://www.platinumlist.net/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": THAI_IMG,
        "image_caption": "Wat Arun on the Chao Phraya River in Bangkok, a centerpiece of Thailand's tourism draw",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": thailand_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"… {art['slug']} ({wc} words)")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
