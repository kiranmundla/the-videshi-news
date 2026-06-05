#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-05 06:00 UTC run"""
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

# ─────────────────────────────────────────
# ARTICLE 1: Noida International Airport
# ─────────────────────────────────────────
article1_body = """India's newest airport has everything it needs to start flying — a 3,900-meter runway rated for the world's largest widebodies, an aerodrome licence from the DGCA, a gleaming terminal built to handle 12 million passengers a year, and airlines lined up to operate. What it does not have is a CEO who qualifies under a 15-year-old security rule. And until that changes, no commercial flight will leave Noida International Airport.

Two months after Prime Minister Narendra Modi inaugurated the ₹11,200 crore facility at Jewar, the airport remains silent. The reason is as bureaucratic as it is avoidable.

## The clearance that won't come

Christoph Schnellmann, the airport's chief executive, is a Swiss national. He has run the project since 2020 — through planning, construction, and inauguration — and brings decades of aviation experience at Swissport and Zurich Airport across Europe, Central Asia, and Africa.

But a 2011 BCAS aviation security order designates the CEO of every greenfield airport as its security coordinator and requires that role be held by an Indian citizen. Without BCAS issuing the Aerodrome Security Programme (ASP) approval — which flows through the CEO — no commercial operations can begin.

The Bureau of Civil Aviation Security asked the Ministry of Home Affairs to relax the rule. The MHA refused. According to Forbes India, Uttar Pradesh officials were aware of this restriction for three years but did not act to resolve it. The airport operator, Yamuna International Airport Private Limited (a subsidiary of Zurich Airport International AG), may now need to appoint an Indian national as CEO before the final clearance can be issued.

## A project defined by delays

The security clearance is only the latest chapter. The concession was awarded in 2020, with operations expected by 2024. That slipped to April 2025, then early 2026. The March 28 inauguration — complete with a presidential walkthrough and a live aerodrome licence grant — suggested the end was in sight.

IndiGo signed on as the launch carrier, with Akasa Air and Air India Express queuing behind it. UPSRTC began running shuttle buses from Noida, Greater Noida, and Delhi. A 750-meter link road to the Yamuna Expressway was completed. Everything converged — except the one approval that requires an Indian passport holder to sign for it.

## What this means for NRIs

For the estimated 2.5 million Indian Americans with roots in Uttar Pradesh and the Delhi-NCR corridor, Jewar was supposed to change the arithmetic of flying home. Delhi's Indira Gandhi International Airport — the country's busiest — has been buckling under capacity pressure for years. NRIs arriving on 14-hour flights from Newark, San Francisco, or Chicago face congested terminals, long immigration queues, and unreliable ground connections to Noida, Greater Noida, and western UP.

Jewar sits 72 km from IGI and 40 km from Noida, with a direct Yamuna Expressway connection and eventual links to the Delhi-Mumbai Expressway. It was designed as the pressure valve — and a practical one, cutting road travel to Agra from three hours to under 90 minutes.

Instead, NRIs planning summer visits will continue funnelling through IGI, which is simultaneously absorbing reduced capacity from Air India (22% domestic cuts) and IndiGo (7-10% reductions) as the Iran-driven fuel crisis bites.

## What happens next

Two paths exist. The operator restructures its leadership and appoints an Indian national to the CEO role, unblocking the BCAS approval. Or the MHA reconsiders — an outcome that, by all reporting, is not on the table.

YIAPL has said it is "working closely with BCAS to secure ASP approval." Neither BCAS nor Zurich Airport has commented publicly on the timeline. The airport's Wikipedia entry still lists commercial operations as "expected within 45 to 60 days of inauguration." That window closed in mid-May.

A world-class facility, fully built and technically cleared, grounded by a question of passports. For an airport named after the country's aspirations, it is a particularly Indian kind of irony."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Newest Airport Has Been Inaugurated, Applauded — and Grounded by a Rule Nobody Fixed",
    "subheadline": "Noida International Airport at Jewar was built for ₹11,200 crore, inaugurated by the PM, and holds all its technical clearances — except one. Its CEO is Swiss, and Indian law says that's a problem.",
    "slug": make_slug("noida-jewar-airport-grounded-swiss-ceo-security-clearance"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Delhi-NCR NRIs from UP were counting on Jewar as an alternative to IGI's overcrowded terminals — the delay means another summer routing through India's most congested airport while capacity is being cut due to the fuel crisis",
    "tags": ["travel", "airports", "infrastructure", "noida", "delhi-ncr"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/news/deep-dive/noida-international-airport-ceo-christoph-schnellmann-faces-security-hurdle/2993424/1"},
        {"name": "WhispersInTheCorridors", "url": "https://whispersinthecorridors.in"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Noida_International_Airport"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
    "image_caption": "PM Narendra Modi at the inauguration of Noida International Airport at Jewar on March 28, 2026",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}

# ─────────────────────────────────────────
# ARTICLE 2: South Korea Visa-Free Transit
# ─────────────────────────────────────────
article2_body = """The next time you price out an SFO-DEL ticket with a Seoul layover, do not sleep in the transit lounge. Stay for a week.

South Korea's 30-Day Transit Tourism Program allows travellers holding valid visas or permanent residency from the United States, Canada, Australia, New Zealand, the United Kingdom, and several European countries to enter the country without a separate tourist visa. The only requirement: a qualifying transit itinerary and a confirmed onward flight departing South Korea within 30 days.

For Indian Americans flying through Incheon on their way to Delhi, Mumbai, or Hyderabad, this effectively turns a layover into a vacation — without a single visa application.

## How the program works

The mechanics are simple. Present your passport, your US visa or green card, and your onward itinerary at Korean immigration. If you are transiting between two different countries — flying from the US to India via Seoul, for instance — you qualify for up to 30 days visa-free. There is no application, no fee, and no advance registration.

This is separate from the K-ETA (Korea Electronic Travel Authorization), which normally applies to citizens of visa-exempt countries. South Korea extended its K-ETA exemption through December 2026 for nationals of 67 countries, including the US. American citizens do not even need the K-ETA. Indian passport holders with US immigration documents use the transit tourism pathway instead.

The key requirement is a genuine transit itinerary. Your travel must include a connection through Korea between two different countries. A round trip starting and ending in the same country without a legitimate transit element may not qualify. In practice, any US-to-India routing through Incheon satisfies this condition.

## Why this matters for the diaspora

South Korea has shifted from a niche destination to a cultural force among Indian Americans. Korean dramas on Netflix, Korean beauty products in every Sephora, and Korean barbecue joints across the suburbs of Edison, Fremont, and Plano have built a genuine following — especially among younger diaspora travellers who grew up binge-watching *Crash Landing on You* and eating tteokbokki at H Mart.

Indian tourist arrivals to South Korea have tracked steadily upward since the pandemic recovery, driven partly by competitive airfares on Korean Air and Asiana Airlines and partly by Incheon's position as a natural transit hub on the India-US corridor. The 30-day window is generous enough for a proper trip, not just a forced stopover.

## What to do with 30 days in Korea

Seoul alone justifies a week. Gyeongbokgung Palace, the traditional hanok village of Bukchon, the electronics and street-food corridors of Myeongdong and Yongsan, and the N Seoul Tower viewpoint are all within a compact metro area served by one of the world's best subway systems.

A KTX bullet train to Busan takes under three hours and puts you on Haeundae Beach with a fresh plate of raw fish. Jeju Island — Korea's answer to Hawaii, complete with volcanic craters, tangerine orchards, and UNESCO heritage sites — is a one-hour flight from Seoul's Gimpo Airport.

Accommodation is surprisingly affordable by Asian capital standards. Budget hotels in Hongdae or Insadong run $40-60 per night. A proper bibimbap at a local restaurant costs $6-8, and Korean street food — hotteok, kimbap, tteokbokki — rarely exceeds $3.

## Practical details for NRI travellers

Incheon International Airport is one of Asia's best-connected hubs. Korean Air and Asiana Airlines operate direct flights to Delhi, Mumbai, Chennai, and Bengaluru. From the US side, nonstop Seoul service is available from Los Angeles, San Francisco, New York, Seattle, Dallas, Chicago, and Atlanta.

India's passport ranks around 80th globally for visa-free access on the Henley Passport Index. Programs like South Korea's transit tourism pathway are exactly the kind of opportunity that NRIs — uniquely positioned with both Indian passports and US immigration documents — should be using. The infrastructure is there. The culture is calling. And for once, the bureaucracy is on your side.

Book the longer layover. Seoul is worth it."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "South Korea Will Let You Stay 30 Days Without a Visa — If You Hold a US Green Card",
    "subheadline": "Seoul's transit tourism program is one of Asia's best-kept travel secrets. For Indian Americans with a US visa or permanent residency, it turns a layover into a free 30-day pass to the world's K-drama, K-food, and K-beauty capital.",
    "slug": make_slug("south-korea-visa-free-transit-nri-us-green-card-seoul"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Indian Americans with US visas or green cards can enter South Korea visa-free for up to 30 days during transit — turning a routine Incheon layover on the India-US corridor into a Korean vacation without any visa application",
    "tags": ["travel", "visa", "south-korea", "nri", "transit"],
    "urgency": "low",
    "sources": json.dumps([
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/us-joins-canada-australia-new-zealand-uk-germany-south-korea-visa-free-transit-2026/"},
        {"name": "Pureum Law Office", "url": "https://pureumlawoffice.com/south-korea-k-eta/"},
        {"name": "Wikipedia — Visa policy of South Korea", "url": "https://en.wikipedia.org/wiki/Visa_policy_of_South_Korea"}
    ]),
    "score_total": 70,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/31743309/pexels-photo-31743309.jpeg",
    "image_caption": "Gyeongbokgung Palace in Seoul, South Korea's most iconic historical landmark",
    "image_attribution": "Pexels",
    "body": article2_body,
}

# ─────────────────────────────────────────
# ARTICLE 3: Air India Mumbai-Tokyo Nonstop
# ─────────────────────────────────────────
article3_body = """Starting June 15, Air India will fly four weekly nonstop flights between Mumbai and Tokyo Haneda — giving western India its first direct connection to Japan and eliminating the Delhi transfer that has defined the route for decades.

The flights will operate on Boeing 787-8 Dreamliner aircraft, the same widebody that currently serves Air India's Delhi-Tokyo Haneda daily service. The new Mumbai route complements rather than replaces the Delhi connection, effectively doubling Air India's Japan capacity and giving passengers from Gujarat, Maharashtra, Karnataka, and Kerala a more direct path to East Asia.

## The Delhi detour is over

For Mumbai-based travellers — and for NRIs connecting through Mumbai from the US — Tokyo has always required a workaround. Either you flew to Delhi first and connected to the Haneda flight, or you routed through a Gulf hub like Dubai or Singapore, adding hours and a second layover to an already gruelling journey.

The new nonstop changes that equation. Mumbai to Tokyo Haneda clocks in at roughly 9.5 hours eastbound, compared to the 13-15 hour journey through Dubai with Emirates or the two-flight combination of a domestic Mumbai-Delhi leg followed by the 8.5-hour Delhi-Haneda service.

Air India chose Haneda over Narita — the same switch it made for the Delhi route in March 2025. Haneda sits 18 km from central Tokyo, connected by monorail and Keikyu Line train in about 30 minutes to Tokyo Station. Narita, the legacy international airport, is 60 km out and requires a 90-minute Narita Express ride. For business travellers racing to a Shibuya meeting or tourists heading straight to Shinjuku, landing at Haneda saves an hour before you even leave the airport corridor.

## All of Japan on one ticket

The Mumbai-Tokyo flights feed into Air India's expanded codeshare with All Nippon Airways, its Star Alliance partner. Through the ANA agreement, passengers can book a single ticket from Mumbai to six Japanese cities beyond Tokyo: Osaka, Fukuoka, Hiroshima, Nagoya, Okinawa, and Sapporo. Baggage checks through to the final destination, no separate booking required.

In the reverse direction, ANA places its NH designator code on Air India flights into India, connecting Japanese travellers to Ahmedabad, Bengaluru, Chennai, Hyderabad, Kolkata, and Pune through Mumbai and Delhi. It is the deepest India-Japan airline partnership currently in operation.

## Why NRIs should pay attention

Japan has been climbing the Indian diaspora's travel wishlist for years. Anime tourism, cherry blossom season, tech pilgrimages to Akihabara, and a weakening yen that has made Tokyo, Kyoto, and Osaka dramatically more affordable since 2023 have all fuelled the trend. The Japan National Tourism Organisation recorded 233,000 Indian visitors in 2024, up 40% from the prior year — growth that accelerated further in 2025.

For NRIs, the route opens practical possibilities. Connecting through Mumbai from SFO, Newark, or Chicago is already standard for travellers headed to western and southern India. Now that same Mumbai connection can carry you to Tokyo on a single Star Alliance itinerary. Award redemption through United MileagePlus or Air Canada Aeroplan applies, making this a genuine option for frequent flyers sitting on points.

There is also a business dimension. India-Japan bilateral trade crossed $21 billion in 2024-25. Japanese companies — Toyota, Suzuki, Sony, SoftBank — maintain deep investments in India, and the technology corridor between Bengaluru-Pune and Tokyo has expanded steadily. A direct Mumbai-Tokyo link makes this commercial relationship easier to service from both ends.

## The details

Air India's Mumbai-Tokyo Haneda service launches June 15, 2026, with four weekly frequencies. The Boeing 787-8 Dreamliner is configured with 18 Business Class and 238 Economy Class seats.

Fares will track market conditions, but expect them to benchmark near the Delhi-Haneda pricing, which has been competitive with Gulf carrier alternatives since the Haneda switch. Round-trip economy fares on the Delhi route have recently hovered between $600 and $900, though the Iran-driven fuel surcharges affecting the entire industry could push Mumbai pricing higher.

Bookings are open on Air India's website, mobile app, and through travel agents. For NRIs who have been routing through Dubai or Delhi to reach Japan, June 15 is the date the detour ends."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India Launches Mumbai–Tokyo Nonstop on June 15 — and Western India Finally Gets Direct Access to Japan",
    "subheadline": "Four weekly Dreamliner flights connect India's financial capital to Tokyo Haneda, with onward codeshare access to Osaka, Fukuoka, and four more Japanese cities through ANA.",
    "slug": make_slug("air-india-mumbai-tokyo-haneda-nonstop-nri-japan"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs connecting through Mumbai from SFO, Newark, or Chicago can now reach Tokyo on a single Star Alliance itinerary — eliminating the Delhi detour and opening award redemption through United MileagePlus and Aeroplan",
    "tags": ["travel", "airlines", "air-india", "japan", "tokyo", "nonstop"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "BrightSun Travel", "url": "https://www.brightsun.co.in/travelblog/air-india-expands-connectivity-with-new-routes-for-2026"},
        {"name": "India Outbound", "url": "https://indiaoutbound.info/aviation/air-india-shifts-tokyo-flights-to-haneda-expands-codeshare-with-ana/"},
        {"name": "Travel Daily Media", "url": "https://www.traveldailymedia.com/air-india-daily-flights-tokyo-haneda/"}
    ]),
    "score_total": 75,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/15275312/pexels-photo-15275312.jpeg",
    "image_caption": "Tokyo skyline with Mount Fuji rising in the background",
    "image_attribution": "Pexels",
    "body": article3_body,
}

# ─────────────────────────────────────────
# Publish all
# ─────────────────────────────────────────
articles = [article1, article2, article3]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
