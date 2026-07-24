#!/usr/bin/env python3
"""Travel writer — July 6, 2026, 10:00 AM PT"""
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


# ─────────────────────────────────────────────────────────
# ARTICLE 1: India's Passport Ranking Falls
# ─────────────────────────────────────────────────────────

article1_body = """India's passport has slipped one place to 125th in the Global Passport Index 2026, released on July 5 by Global Citizen Solutions. The ranking puts India outside the world's top 100 passports for the fifth consecutive year — and behind countries such as Namibia, the Philippines, Morocco and Uzbekistan.

For the roughly 4.5 million Indian-born residents of the United States, the ranking is a reminder of a stubborn asymmetry: the American passport they may hold (or aspire to hold) sits comfortably in 11th place. The Indian passport in their other pocket opens just 26 doors without a visa.

## The Numbers

The Global Passport Index differs from the more commonly cited Henley Passport Index, which ranks India 77th based solely on visa-free access. The GPI uses three pillars: Enhanced Mobility (50% weight), Investment Potential (25%) and Quality of Living (25%). India's composite score reached a five-year high of 45.1, but that still wasn't enough to prevent the one-spot slide from 124th in 2025.

Indian citizens currently need visas to enter 88 countries, including every major Western economy — the United States, the United Kingdom, Germany, France, Canada, Australia and the UAE. By contrast, holders of Swedish passports (ranked first) can travel to nearly every country on earth without prior paperwork.

The top ten is dominated by European nations: Sweden, Switzerland, Finland, Germany, the Netherlands, Denmark, Ireland, the United Kingdom, Norway and Singapore.

## Why NRIs Should Care

The ranking matters to the diaspora in two specific ways.

**OCI holders still carry an Indian passport.** Overseas Citizens of India enjoy lifetime visa-free travel to India but still need their Indian passport (or the passport of their adopted country) for everywhere else. For dual-nationality families planning a summer in Europe or a gap-year in South America, the Indian passport is the weaker link. Argentina now allows entry without a visa for Indians holding a US B2, J, H-1B or Green Card — but that concession is pegged to the American document, not the Indian one.

**Family visitors face a visa gauntlet.** Elderly parents visiting their NRI children in the US, UK or Canada must still navigate consulate appointments, financial documentation and processing delays. The Indian passport's limited visa-free reach means even a short trip to see grandchildren requires weeks of planning.

## Small Gains, Long Road

There have been bright spots. Germany abolished its airport transit visa requirement for Indian nationals in June 2026, and France did the same in April. Malaysia extended its visa-free arrangement through December 2026. Argentina's new US-visa-linked exemption is another door ajar.

But the broader trajectory is slow. India added just two new visa-free destinations in 2025 (the Philippines and Sri Lanka). Neighbours China, ranked 104th, is pulling ahead. Pakistan, at 188th, remains one of the weakest passports globally.

Diplomats in New Delhi have signalled that reciprocal visa-relaxation talks with several countries are ongoing. But for now, NRIs planning multi-country trips with family from India should budget extra time — and patience — for the paperwork that a 125th-ranked passport demands."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Passport Slips to 125th in Global Ranking — and NRIs Feel the Pinch",
    "subheadline": "The Global Passport Index 2026 puts India behind Namibia and Morocco, with visa-free access to just 26 countries. For diaspora families juggling two passports, the gap keeps widening.",
    "slug": make_slug("india-passport-ranking-125-global-index-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs with OCI cards still rely on India's weak passport for non-US travel, and family visitors face visa hurdles to reach the US, UK and Canada.",
    "tags": ["travel", "visa", "passport", "india", "nri", "global-passport-index"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Global Citizen Solutions", "url": "https://www.globalcitizensolutions.com/global-passport-index/"},
        {"name": "Curly Tales", "url": "https://curlytales.com/indian-passport-rank-slips-in-global-passport-index-2026/"},
        {"name": "7Globe", "url": "https://7globe.in/news/indias-passport-ranking-slips-remains-outside-top-100-which-nations-are-in-top-10/"},
        {"name": "The India Moves", "url": "https://theindiamoves.com/india-ranks-125th-in-global-passport-index-2026/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Indian_Passport_%28e-Passport%2C_2024%29.svg/500px-Indian_Passport_%28e-Passport%2C_2024%29.svg.png",
    "image_caption": "India's e-passport, introduced in 2024, ranked 125th globally in the 2026 index",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────────────────
# ARTICLE 2: SWISS Bengaluru–Zurich Nonstop
# ─────────────────────────────────────────────────────────

article2_body = """Swiss International Air Lines will launch nonstop flights between Bengaluru and Zurich from October 28, operating five times a week on its Airbus A330-300. The route marks SWISS's first-ever service to India's technology capital — and the latest move in a broader European push into the Indian aviation market.

Bengaluru becomes SWISS's third Indian destination after Delhi and Mumbai, and the third Lufthansa Group gateway from the city alongside Lufthansa's own Frankfurt and Munich services. For the estimated 300,000-plus tech workers of Indian origin scattered across Switzerland, Germany and wider Europe, the route offers something that hasn't existed before: a direct, premium-cabin link between Kempegowda International Airport and Zurich's global hub.

## The Schedule

The westbound LX 141 departs Bengaluru at 04:50, arriving in Zurich at 10:50 the same morning — early enough to connect across Europe or catch an onward flight to North America. The eastbound LX 140 leaves Zurich at 13:20, touching down in Bengaluru at 02:55 the following day.

Flights operate daily except Tuesdays and Thursdays (westbound) and Mondays and Wednesdays (eastbound).

The A330-300 on the route carries a three-class configuration: First, Business and Economy. SWISS is one of a handful of airlines still offering a dedicated First Class cabin on India routes — a signal of how the carrier is positioning this as a premium corridor.

## Europe Is Going All-In on India

The SWISS route is not happening in a vacuum. The Lufthansa Group — SWISS's parent — has been aggressively expanding India capacity all year:

- **Lufthansa** added extra weekly flights from Frankfurt to Chennai, Delhi and Hyderabad, and from Munich to Bengaluru, for summer 2026.
- **SWISS** doubled its Delhi–Zurich service with a second daily flight in April and May.
- **Germany abolished its airport transit visa** for Indian nationals in June 2026, making connections through Frankfurt and Munich seamless for the first time.

Kevin Markette, the Lufthansa Group's Senior Director for South Asia, called India "the Group's largest intercontinental market in the Asia-Pacific region." With over 70 weekly flights between India and Europe now on the Lufthansa Group's schedule, the commitment is hard to miss.

## What This Means for Bengaluru's Diaspora

Bengaluru's international connectivity has been on a tear. The city's tech ecosystem — anchored by global firms like Infosys, Wipro, SAP and Bosch — drives persistent demand for premium long-haul seats. Kempegowda Airport has become one of India's fastest-growing international hubs, and the SWISS addition cements its position as a serious rival to Delhi and Mumbai for European traffic.

For NRIs in Switzerland and continental Europe, the Zurich hub opens single-connection access to cities such as Geneva, Basel, Vienna, Prague, Brussels and Barcelona. For tech professionals shuttling between Bengaluru campuses and European headquarters, the direct flight replaces what has typically been a two-stop journey through the Gulf or a connection in Delhi.

Girish Nair, Chief Operating Officer of Bangalore International Airport Limited, said the route "connects India's Silicon Valley with a premier global financial capital."

## Booking and Fares

Tickets are already available on swiss.com and through travel agents. SWISS has not announced introductory pricing, but one-stop Bengaluru–Europe fares on competitor airlines currently run between $700 and $1,100 round-trip in economy. The convenience premium of a nonstop — and SWISS's onboard product, including lounge access and Swiss cuisine — may justify a higher ticket price for many travellers.

With Air India simultaneously pulling back capacity on several international routes through August, the timing of SWISS's entry gives Bengaluru passengers an option that didn't exist six months ago. For India's southern tech corridor, Europe just got closer."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "SWISS Launches Bengaluru–Zurich Nonstop — Europe's Airlines Are All-In on India",
    "subheadline": "Swiss International Air Lines will fly its A330-300 to Bengaluru five times weekly from October, making it the Lufthansa Group's third gateway from the city and giving India's tech diaspora a direct European link.",
    "slug": make_slug("swiss-bengaluru-zurich-nonstop-europe-india"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs in Switzerland and Europe gain a direct premium link to Bengaluru, replacing two-stop Gulf connections and opening Zurich-hub access to dozens of European cities.",
    "tags": ["travel", "airlines", "swiss", "bengaluru", "zurich", "lufthansa-group", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Breaking Travel News", "url": "https://www.breakingtravelnews.com/news/article/swiss-expands-india-network-with-new-nonstop-bengaluruzurich-service/"},
        {"name": "Travel Wires", "url": "https://travelwires.com/swiss-launches-nonstop-flights-between-zurich-and-bengaluru/"},
        {"name": "SWISS", "url": "https://www.swiss.com/in/en/fly/bengaluru-to-zurich"},
        {"name": "Lufthansa Group", "url": "https://newsroom.lufthansagroup.com/en/summer-2026--lufthansa-group-airlines-expand-flight-offerings-to-numerous-holiday-destinations.html"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Swiss_Airbus_A330-300_HB-JHM_IAD_VA1.jpg/1280px-Swiss_Airbus_A330-300_HB-JHM_IAD_VA1.jpg",
    "image_caption": "A SWISS Airbus A330-300, the aircraft type that will operate the new Bengaluru–Zurich route",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body
}


# ─────────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
