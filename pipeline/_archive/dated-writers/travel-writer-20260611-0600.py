#!/usr/bin/env python3
"""Travel writer run — 2026-06-11 06:00 UTC"""
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

# --- ARTICLE 1: Air India + Thai Airways Codeshare ---

art1_body = """Air India and Thai Airways International signed a memorandum of understanding on June 7 at the IATA Annual General Meeting in Rio de Janeiro, setting the stage for a codeshare agreement that could reshape how Indian travellers move between South and Southeast Asia.

The deal, when finalised later this year pending regulatory approvals, will let both Star Alliance carriers place their flight codes on each other's services between India and Thailand — and, critically, on select international routes beyond both countries. An Air India passenger booking a Delhi-to-Bangkok flight could seamlessly connect onward to Chiang Mai, Phuket, or Ho Chi Minh City on a Thai Airways code. A Thai traveller heading to London or New York could route through Delhi on an Air India long-haul service without a separate ticket.

## What the Numbers Say

India-Thailand air traffic has been climbing steadily. Thailand welcomed roughly 2 million Indian visitors in 2024, making Indians the fourth-largest tourist group in the kingdom. From the other direction, Thailand is consistently among the top five international destinations booked by Indians on Cleartrip and MakeMyTrip. The route pair is served by both carriers plus IndiGo, SpiceJet, and several Gulf airlines — but coordinated schedules and single-ticket pricing between Air India and Thai Airways would give both an edge in capturing connecting traffic that currently leaks to Emirates and Singapore Airlines via their respective hubs.

"This MoU with Thai Airways brings together two carriers with complementary strengths and a shared commitment to service excellence," said Campbell Wilson, Air India's CEO. "It also supports Air India's broader ambition to strengthen India's connectivity with the world."

Chai Eamsiri, Thai Airways' CEO, framed the deal in diplomatic terms: the partnership would "support economic growth, promote people-to-people exchanges, while contributing to broader cooperation between the two countries."

## Why NRIs Should Care

For the estimated 4.8 million Indian Americans, Thailand occupies a unique sweet spot. It is visa-free for Indian passport holders arriving by air (up to 60 days), making it the easiest international trip outside of Nepal and Bhutan. It is also one of the few countries where an Indian passport combined with a valid US visa unlocks additional privileges — including visa-on-arrival for family members visiting from India who hold B1/B2 stamps.

The codeshare matters because it smooths the two trips NRIs make most often to Thailand. The first is the family vacation: parents visiting from India who currently need to book separate tickets from, say, Varanasi to Delhi and then Delhi to Bangkok can now potentially get a single itinerary with coordinated baggage handling. The second is the stopover: NRIs flying between the US and India increasingly route through Bangkok on Thai Airways' excellent long-haul product, and a codeshare with Air India means earning and burning frequent-flyer miles across both carriers on a single reservation.

## The Bigger Picture

The MoU is part of Air India's aggressive alliance-building under Tata Group ownership. In the past six months alone, the carrier has signed partnerships with Riyadh Air (Saudi Arabia's new airline), expanded its Star Alliance commitments, and launched the Easy Connect hub-and-spoke model from Varanasi. Thai Airways, meanwhile, is recovering from a bruising restructuring and looking to rebuild its network by piggybacking on India's booming outbound travel market.

Neither airline disclosed specific routes or a launch date, saying only that terms would be announced "in due course." But with both carriers operating multiple daily flights between Delhi, Mumbai, Kolkata, and Bangkok — plus Thai Airways' dense domestic network feeding Chiang Mai, Krabi, and Phuket — the integration surface is large.

For NRIs planning a Thailand trip this monsoon or winter, the practical advice is simple: wait for the codeshare to go live before booking, because single-ticket pricing on connecting routes almost always beats two separate bookings. And if you hold Air India Maharaja Club status, the Star Alliance tie-up means your lounge access and priority boarding should extend seamlessly onto Thai Airways metal."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India and Thai Airways Are Merging Their Networks — and NRIs Get the Best of Both",
    "subheadline": "A new codeshare deal signed in Rio de Janeiro will let passengers book single-ticket itineraries across both Star Alliance carriers, smoothing the India-Thailand corridor that millions of diaspora travellers use every year.",
    "slug": make_slug("air-india-thai-airways-codeshare-nri-thailand"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Thailand is visa-free for Indian passport holders and a top vacation destination for NRIs. The codeshare means single-ticket pricing, coordinated baggage, and frequent-flyer reciprocity on the India-Thailand corridor — plus smoother connections for parents visiting from India.",
    "tags": ["travel", "airlines", "air india", "thai airways", "codeshare", "thailand", "nri"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Asian Aviation", "url": "https://asianaviation.com/posts/air-india-thai-airways-deepen-cooperation"},
        {"name": "BW Travel", "url": "https://bwtravel.com"},
        {"name": "The Hindu Business Line", "url": "https://thehindubusinessline.com"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png/1280px-VT-JRF_%40_JFK%2C_2024-11-04.png",
    "image_caption": "An Air India Boeing 777 at JFK Airport in New York",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# --- ARTICLE 2: Ayodhya Tourism Boom ---

art2_body = """Four years ago, Ayodhya received six million visitors a year. In 2024, that number hit 164 million. The transformation — a 27-fold increase driven by the Ram Mandir inauguration in January 2024, a new international airport, and a rebuilt railway station — has turned a sleepy Uttar Pradesh temple town into India's fastest-growing pilgrimage destination. And for the Indian American diaspora, the city that once required a punishing detour through Lucknow is now a direct flight away.

## The Infrastructure That Changed Everything

The catalyst was the consecration of the Ram Mandir on January 22, 2024, a moment watched by an estimated 150 million Indians on live television. But the physical transformation began earlier. The Maharishi Valmiki International Airport now connects Ayodhya directly to Delhi, Mumbai, Bengaluru, Chennai, and Kolkata — eliminating the three-hour road transfer from Lucknow that previously made the trip impractical for time-pressed NRI families visiting India for two or three weeks.

The Ayodhya Dham railway station has been redeveloped into a modern transit hub. Road widening, new bypass corridors, and a river cruise on the Saryu have added layers to what was once a one-temple, one-day visit.

State tourism data tells the story: Uttar Pradesh recorded 23.75 crore tourists in 2017. By the first quarter of 2025 alone, that figure crossed 109.65 crore, with Ayodhya accounting for roughly one in five visitors to the state.

## The Economic Ripple

A study by IIM Lucknow published in February quantified the impact on the ground. Shopkeeper earnings in Ayodhya have risen from Rs 400–500 per day before the temple inauguration to around Rs 2,500 — a fivefold jump. Citywide real estate values have appreciated 25–40%, with plots near the Ram Mandir seeing price increases of five to ten times.

The city generated approximately Rs 400 crore in GST revenue, a figure that reflects not just pilgrim spending on lodging and prasad but a growing commercial ecosystem of restaurants, tour operators, souvenir shops, and transport services.

Hotels are the clearest barometer. Budget guesthouses that once charged Rs 500 a night now list at Rs 2,000–3,000. Branded hospitality is arriving too: Marriott and Hilton have both flagged temple towns as a strategic growth category, with 11% and 15% of their respective Indian portfolios now serving pilgrim destinations.

## Why the Diaspora Is Paying Attention

Ayodhya's visitor data increasingly includes international passport holders — particularly from the United States, United Kingdom, Canada, Australia, and the UAE. While official international tourist breakdowns are limited, airport data and hotel booking patterns confirm growing NRI interest.

The reason is straightforward. For the 4.8 million Indian Americans, a trip to India almost always includes a family or religious dimension. Ayodhya had long been on the list but was logistically painful to reach — especially for older parents who struggle with long road journeys. The new airport changes that calculus entirely. A Delhi-Ayodhya flight takes about 90 minutes. An NRI family spending two weeks in India can now add Ayodhya without losing an entire day to ground transport.

The timing matters too. Ayodhya is becoming a multi-day destination rather than a quick darshan stop. Pilgrims are extending stays to two to four nights, combining the temple visit with river ceremonies, the Ramayan circuit heritage walk, and trips to nearby Prayagraj (the Kumbh Mela site) and Varanasi. For diaspora families introducing American-born children to their roots, that depth of experience is the difference between a checkbox visit and a meaningful trip.

## What Comes Next

The Uttar Pradesh government has announced plans for an Ayodhya cultural zone, a Ramayan theme park, and expanded river tourism infrastructure. The pace of hotel construction suggests the market expects the surge to be structural, not cyclical.

For NRIs planning a trip home in the next six months, the practical takeaway is this: book Ayodhya flights early, because capacity on the Delhi-Ayodhya corridor is still catching up to demand. And if you are planning a multi-city pilgrimage — Ayodhya, Varanasi, Prayagraj — Air India's new Easy Connect hub-and-spoke model from Varanasi now offers single-ticket international connections that did not exist a year ago."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Ayodhya Went From 6 Million Visitors to 164 Million in Four Years — and NRIs Are Finally Booking",
    "subheadline": "A new airport, a rebuilt railway station, and the Ram Mandir have turned an Uttar Pradesh temple town into India's fastest-growing pilgrimage destination. For the diaspora, the city that once required a punishing detour through Lucknow is now a direct flight away.",
    "slug": make_slug("ayodhya-tourism-boom-ram-mandir-nri-pilgrimage"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Ayodhya's new international airport eliminates the difficult Lucknow-to-Ayodhya road journey, making it practical for time-pressed NRI families to add the Ram Mandir to their India trips. Growing numbers of US, UK, and Canadian passport holders are showing up in visitor data.",
    "tags": ["travel", "ayodhya", "ram mandir", "pilgrimage", "religious tourism", "nri", "uttar pradesh"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/yqa2sqc2vq26/"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in"},
        {"name": "IIM Lucknow (via Bloomberg)", "url": "https://thehindubusinessline.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Shri_Ram_Janambhoomi_Mandir%2C_Ayodhya_Dham.jpg",
    "image_caption": "The Ram Mandir in Ayodhya, inaugurated in January 2024",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
