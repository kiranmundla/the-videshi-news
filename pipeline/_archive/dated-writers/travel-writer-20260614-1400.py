#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-06-14 14:00 UTC run."""

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

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: Air India Easy Connect
# ──────────────────────────────────────────────────────────────────────

art1_body = """Air India will launch its first "Easy Connect" flights from Varanasi on June 25, inaugurating a hub-and-spoke model that could fundamentally change how millions of Indians in smaller cities reach the rest of the world. For the Indian American diaspora — many of whom trace their roots to Uttar Pradesh, Bihar, and other states far from Mumbai or Delhi — this is the most significant shift in homeward travel logistics in years.

## How It Works

Under the Easy Connect framework, passengers departing from Varanasi's Lal Bahadur Shastri International Airport can complete their international immigration and customs clearance right at the origin airport. Baggage is checked through to the final international destination. Upon landing at Delhi's Indira Gandhi International Airport — the hub — travellers are routed through a secured international transit corridor, bypassing the notoriously congested domestic-to-international transfer queues.

The daily feeder flight, designated AI1111, is timed to connect with 17 international destinations from Delhi, including London, Frankfurt, Dubai, Singapore, and key North American gateways. The transit window at Delhi is optimised to under four hours.

India's Civil Aviation Minister Ram Mohan Naidu Kinjarapu confirmed the launch on social media: "India's hub and spoke aviation vision begins with Varanasi. International travellers can now complete immigration and baggage formalities before reaching Delhi and connect seamlessly onwards."

## Why NRIs Should Care

Anyone who has flown into Delhi from the US only to catch a connecting domestic flight to a Tier 2 city knows the drill: clear immigration in Delhi's heaving Terminal 3, collect luggage from the international carousel, haul it to the domestic terminal, re-check, re-screen, and hope the connection holds. The return journey is equally painful — especially for elderly parents travelling alone.

Easy Connect eliminates that friction on the outbound side from India. A grandmother in Varanasi heading to visit family in Chicago clears immigration at her local airport and walks straight through a transit corridor in Delhi. No second check-in. No second immigration queue. No hauling suitcases between terminals.

The implications extend beyond convenience. Varanasi's airport handled 3.6 million passengers last year, and the city sits at the centre of a vast catchment area stretching across eastern UP and Bihar — states that collectively account for over 300 million people and a significant share of the American desi community. Cities like Lucknow, Patna, Bhopal, and Rajkot are next in the phased rollout.

## What's Still Missing

The Easy Connect model currently works only on outbound international journeys from India. Arriving NRIs will still clear immigration and customs at Delhi before catching a domestic connection — though Air India says the reverse flow is being planned. The programme also launches exclusively with Air India; IndiGo and other carriers may join later pending regulatory approval.

For the diaspora, the real test will be reliability. Connecting flights through a single hub work brilliantly when schedules hold, but a delayed feeder flight from Varanasi could mean a missed London departure. Air India's on-time performance — still a sore point despite the Tata makeover — will determine whether Easy Connect becomes transformative or merely aspirational.

Still, the structural shift is real. For the first time, India's aviation system is acknowledging that international travel shouldn't require a mandatory layover in a mega-city. For NRIs who grew up in towns that never had a direct flight to anywhere, that recognition is overdue."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Air India's Easy Connect Lets You Clear Immigration in Varanasi — and Skip the Delhi Chaos",
    "subheadline": "Starting June 25, passengers from India's Tier 2 cities can complete international formalities at their home airport and transit seamlessly through Delhi to 17 global destinations.",
    "slug": make_slug("air-india-easy-connect-varanasi-hub-spoke-nri"),
    "category": "travel",
    "vertical": "aviation",
    "diaspora_angle": "NRIs from UP, Bihar, and eastern India — and their visiting parents — can finally skip Delhi's brutal terminal transfer when flying internationally from their home cities.",
    "tags": ["travel", "airlines", "air-india", "airports", "varanasi", "hub-and-spoke"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/air-india-easy-connect-flights/"},
        {"name": "Air India (via PNI News)", "url": "https://pninews.com/from-your-home-city-to-the-world-air-india-introduces-easy-connect-flights/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/new-air-india-varanasi-flights-simplify-global-travel/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/hub-and-spoke-operations-to-debut-from-delhi-varanasi-route/article69505392.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/14694761/pexels-photo-14694761.jpeg",
    "image_caption": "Air India aircraft lined up on the runway at an Indian airport",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: DigiYatra Biometrics
# ──────────────────────────────────────────────────────────────────────

art2_body = """If you're flying through Delhi, Mumbai, Bengaluru, or Hyderabad this summer, your face is now your boarding pass — at least in theory. India's DigiYatra biometric system, which uses facial recognition to replace repeated document checks at airport touchpoints, has been rolled out for international transit passengers at the country's four busiest airports. And for the millions of NRIs planning summer trips home, it's worth understanding what's changed before you land.

## What DigiYatra Actually Does

DigiYatra replaces the familiar cycle of flashing your boarding pass and passport at every checkpoint — airport entry, security hold, boarding gate — with a single biometric token: your face. Passengers register on the DigiYatra app using an Aadhaar-verified selfie and their boarding pass at least 48 hours before departure. At the airport, facial recognition cameras at dedicated e-gates match your live image against the encrypted biometric template.

The system has processed over 10 crore (100 million) passenger journeys domestically since its launch, and major airlines including Air India, IndiGo, Emirates, and Lufthansa have integrated it into their pre-departure workflows.

## Mandatory or Not? The Confusion

Reports in early June from Outlook Traveller, Lifestyle Asia, and several travel outlets stated that DigiYatra had become mandatory for international transit passengers at the four airports from June 1, 2026. The Ministry of Civil Aviation's own communications supported the rollout.

But a fact-check by TravTalk on June 12, citing sources close to the ministry, clarified that no official mandate has been issued. DigiYatra remains a "facilitation platform," and conventional document verification is still fully operational at all four airports.

The practical reality likely falls somewhere in between. Airports are clearly steering passengers toward the biometric lanes — dedicated e-gates are prominently placed, airlines are sending pre-departure emails about DigiYatra, and the infrastructure is built for the eventual shift. Whether it's technically mandatory today is less important than the fact that it's rapidly becoming the default pathway.

## What NRIs Need to Know

Here's the catch for diaspora travellers: DigiYatra requires Aadhaar verification. If you surrendered your Indian citizenship and hold an OCI card, you may not have a valid Aadhaar number linked to your current identity. The system was designed primarily for Indian citizens and residents, and the OCI edge case hasn't been fully addressed in public documentation.

If you do have Aadhaar (many NRIs retain theirs even after naturalisation), setting up DigiYatra before your trip is straightforward — download the app, verify your identity, and upload your boarding pass. The biometric lanes at Delhi's Terminal 3 and Bengaluru's Kempegowda International are notably faster than the manual queues, especially during peak summer travel.

For NRIs transiting through India — say, connecting in Delhi between a US flight and a domestic leg to Lucknow or Chennai — DigiYatra could meaningfully reduce transfer time. The system is designed to work across both international and domestic checkpoints within the same airport, making tight connections less stressful.

## Where It's Headed

India plans to expand DigiYatra to 27 additional airports by 2027. The government's stated goal is a fully paperless, contactless airport experience — a vision that puts India ahead of most Western countries in biometric airport infrastructure, even as privacy concerns remain underexplored in public debate.

For now, the advice for NRIs is simple: set it up if you can, use it if it's available, and keep your physical documents handy regardless. India's airports are changing faster than the rulebooks can keep up."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Airports Are Scanning Your Face Now — What NRIs Flying Home Need to Know",
    "subheadline": "DigiYatra's biometric e-gates have rolled out for international passengers at Delhi, Mumbai, Bengaluru, and Hyderabad. The system promises faster transit — but NRIs with OCI cards face an Aadhaar catch.",
    "slug": make_slug("digiyatra-biometric-airports-india-nri-guide"),
    "category": "travel",
    "vertical": "airports",
    "diaspora_angle": "NRIs flying home this summer face a new biometric system at India's biggest airports — and those with OCI cards instead of Aadhaar may hit a registration wall.",
    "tags": ["travel", "airports", "digiyatra", "biometrics", "delhi-airport", "nri-guide"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/getting-there/digiyatra-biometric-transit-mandatory/"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/aviation/india-expands-biometric-travel-push-with-mandatory-digiyatra-for-international-passengers"},
        {"name": "TravTalk India (fact-check)", "url": "https://travtalkindia.com/fact-check-digiyatra-not-mandatory-for-international-travellers/"},
        {"name": "The Mainstream", "url": "https://themainstream.co.in/digiyatra-biometric-transit-system-becomes-mandatory-at-4-major-indian-airports/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/10640271/pexels-photo-10640271.jpeg",
    "image_caption": "Passengers passing through automated e-gates at an airport terminal",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ──────────────────────────────────────────────────────────────────────
# ARTICLE 3: Kyrgyzstan — Central Asia's Best-Kept Secret
# ──────────────────────────────────────────────────────────────────────

art3_body = """Most Indian Americans have never considered Kyrgyzstan for a summer trip. That's a mistake. This landlocked Central Asian republic — wedged between China and Kazakhstan, threaded with Silk Road history and ringed by snow-capped peaks that rival anything in the Swiss Alps — is one of the most affordable, visa-friendly, and visually stunning destinations available to NRIs right now. And almost nobody in the diaspora knows it exists as a travel option.

## The Visa Shortcut NRIs Already Have

Here's the detail that changes the calculus: Indian passport holders with a valid US, UK, or Schengen visa of at least three years' validity can enter Kyrgyzstan visa-free for up to seven days through Manas International Airport in Bishkek. No application. No fee. No advance paperwork. Just show your Indian passport and qualifying visa at the immigration counter.

For NRIs who hold US green cards or long-term B1/B2 visas, that means a week in Central Asia's most spectacular landscape with zero visa friction — the kind of spontaneous detour that's usually impossible on an Indian passport.

Those without a qualifying visa can apply for Kyrgyzstan's straightforward e-visa online, with processing in a few business days and fees starting around $40.

## What $50 a Day Gets You

Kyrgyzstan operates on a cost structure that makes even Southeast Asia look expensive. A comfortable guesthouse in Bishkek runs $15-25 a night. A full meal at a local restaurant costs $3-5. Hiring a driver with a 4x4 for a full day through mountain passes costs roughly $50-80, split among passengers. A week-long trip including internal transport, accommodation, meals, and activities can come in under $500 per person — before flights.

The country's star attraction is Issyk-Kul, the world's second-largest alpine lake, sitting at 1,607 metres in the Tian Shan mountains. It's warm enough to swim in during summer (June through August is peak season), ringed by yurt camps and beach resorts, and framed by peaks that top 4,000 metres. Think Lake Tahoe, but with nomadic culture and no crowds.

Beyond Issyk-Kul, the draws multiply: the Ala-Archa gorge an hour from Bishkek, the ancient caravanserai of Tash Rabat, horseback treks through the Song-Kul highlands where seminomadic herders still spend summers in yurt camps, and Osh — the country's second city and one of Central Asia's oldest settlements, with a 3,000-year-old bazaar that rivals anything in Rajasthan for sensory overload.

## The NRI Angle

Kyrgyzstan has a small but notable Indian connection. Several thousand Indian medical students study in Bishkek and Osh, and direct charter flights occasionally operate between Delhi and Bishkek during peak season. The food — heavy on lamb, flatbread, and dairy — has enough overlap with North Indian cuisine to feel familiar, and vegetarian options are improving at tourist-oriented guesthouses.

For NRIs with families, the country offers something rare: genuine adventure travel that's safe, affordable, and doesn't require extreme fitness. Children can ride horses on high-altitude pastures, stay in yurts, and swim in a lake surrounded by mountains. It's the kind of experiential travel that the Indian diaspora — increasingly bored by the Bangkok-Bali circuit — is starting to seek out.

## How to Get There

There are no direct flights from the US to Bishkek, but Turkish Airlines connects through Istanbul with a single stop, and several Gulf carriers route through Dubai or Abu Dhabi. From India, Air Manas and other carriers operate Delhi-Bishkek services. A round-trip from a US gateway to Bishkek typically runs $800-1,200, depending on the season and routing.

The sweet spot for NRIs is a Kyrgyzstan detour on the way back from India. A Delhi-Bishkek-Istanbul-US routing adds minimal cost to a standard India trip and turns a dreaded 20-hour return journey into a week-long Central Asian adventure.

Summer 2026 is the window. Kyrgyzstan's tourism infrastructure is growing but still modest — which is exactly what makes it worth going now, before the rest of the world catches on."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Kyrgyzstan on $50 a Day — the Central Asian Escape NRIs Don't Know About",
    "subheadline": "Alpine lakes, Silk Road history, nomadic yurt camps, and a visa-free entry for Indians with US visas. Kyrgyzstan is the summer detour the diaspora hasn't discovered yet.",
    "slug": make_slug("kyrgyzstan-budget-travel-nri-central-asia-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs with valid US visas can enter Kyrgyzstan visa-free for 7 days — making it one of the easiest and cheapest adventure detours available on an Indian passport.",
    "tags": ["travel", "kyrgyzstan", "central-asia", "budget-travel", "visa-free", "nri-guide"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/kyrgyzstan-joins-georgia-and-laos-as-indian-travellers-embrace-affordable-visa-friendly-summer-escapes/"},
        {"name": "Embassy of India, Bishkek", "url": "https://www.indembbishkek.gov.in/"},
        {"name": "Policybazaar Kyrgyzstan Visa Guide", "url": "https://www.policybazaar.com/travel-insurance/kyrgyz-republic-visa-for-indians/"}
    ]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/18156439/pexels-photo-18156439.jpeg",
    "image_caption": "Mountain range and alpine lake in rural Kyrgyzstan's Tian Shan highlands",
    "image_attribution": "Pexels",
    "body": art3_body
}

# ──────────────────────────────────────────────────────────────────────
# INSERT ALL ARTICLES
# ──────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
