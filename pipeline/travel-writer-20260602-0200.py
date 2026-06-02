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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Newest Airport Opens This Month — and It Could Change How NRIs Fly Into Delhi",
        "subheadline": "Noida International Airport begins commercial flights on June 15, with IndiGo and Akasa Air launching routes to Bengaluru and Navi Mumbai. For NRIs visiting family in UP and the NCR sprawl, the relief from IGI's chaos starts now.",
        "slug": make_slug("noida-international-airport-launch-nri-ncr"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying into Delhi to visit family in Noida, Greater Noida, Ghaziabad, Lucknow, and western UP have long endured the grind of IGI Airport — the overcrowded terminals, the hour-plus drive to east Delhi or UP. Noida International Airport, located off the Yamuna Expressway near Jewar, slashes that commute. Once international operations begin (West Asian and Southeast Asian carriers are already eyeing slots), NRIs could bypass IGI entirely for UP-bound trips. The airport is also just 130 km from Agra — meaning weekend Taj visits from the US could become a one-stop affair.",
        "tags": ["travel", "airports", "noida", "delhi-ncr", "infrastructure", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/noida-new-delhi-bengaluru-and-navi-mumbai-tourism-connectivity-expands-as-akasa-air-launches-operations-from-noida-international-airport/"},
            {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/national-news/noida-airport-launch-june-15-indigo-first-flight-aviation-upgrade/"},
            {"name": "Trak.in", "url": "https://trak.in/stories/commercial-flights-from-noida-airport-can-start-from-june-all-clearances-received/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Prime_Minister_of_Bharat%2C_Shri_Narendra_Damodardas_Modi_at_the_inauguration_ceremony_of_the_Noida_International_Airport%2C_Jewar.jpg",
        "body": """India will add its newest commercial airport to the map on June 15, when IndiGo operates the inaugural flight out of Noida International Airport (NIA) at Jewar, Uttar Pradesh. Akasa Air follows a day later, on June 16, with daily nonstop services to Bengaluru and Navi Mumbai. Air India Express is also confirmed as an early operator.

For anyone who has flown into Delhi's Indira Gandhi International Airport recently — and that includes the hundreds of thousands of NRIs who transit through IGI every summer — the opening of a second major airport in the National Capital Region is not just an infrastructure milestone. It is practical relief.

## What NIA Brings to the Table

The airport, developed through a public-private partnership with Zurich Airport International at an initial cost of ₹11,200 crore, sits along the Yamuna Expressway about 75 kilometres southeast of IGI. Phase 1 delivers a single terminal and one runway with capacity for 12 million passengers annually. At full build-out across four phases, NIA is designed to handle 70 million — which would make it one of Asia's largest airports.

Initial operations are domestic. But the timeline for international service is accelerating. According to Hindustan Times, carriers from West Asia and Southeast Asia are already negotiating slots. For NRIs, that means direct flights from Dubai, Abu Dhabi, or Singapore to Noida could arrive sooner than expected — potentially before the end of 2026.

The airport received its aerodrome licence from DGCA on March 6 and cleared its final security hurdle — the Aerodrome Security Programme approval from BCAS — in late April. A leadership compliance issue (Indian aviation rules require the airport CEO to be an Indian national) delayed the timeline by a few weeks, but that has been resolved.

## Why NRIs Should Care

The geography tells the story. IGI sits in southwest Delhi. Noida, Greater Noida, and Ghaziabad — home to millions of UP-based families that NRIs visit every summer — are in the east. Getting from IGI to Noida during peak hours can take 90 minutes or more, with the toll and traffic of the DND Flyway or the Eastern Peripheral Expressway.

NIA eliminates that entirely. The airport is a 30-minute drive from central Noida and sits on the Yamuna Expressway, which connects directly to Agra (130 km away). A planned high-speed rail link between Delhi and Varanasi will eventually cut the airport-to-Delhi commute to 21 minutes.

For the estimated 400,000-plus NRIs who travel to western UP, Agra, or the broader NCR belt each year, NIA represents the first real alternative to IGI since the Delhi airport opened Terminal 3 in 2010.

## The Bigger Picture

NIA's launch comes at a moment of extraordinary expansion in Indian aviation. Five Indian airports made the Skytrax World Top 100 this year, with Delhi leading at No. 28. DigiYatra facial recognition is live at 38 airports and expanding to 65. And despite the Iran War-driven airfare surge and domestic flight cuts, India's passenger traffic is projected to hit 500 million annually by 2030.

The Noida airport will not solve India's aviation capacity crunch overnight — Phase 1 handles 12 million in a country moving toward 500 million flyers. But for the NCR corridor specifically, it decompresses Delhi's most congested aviation bottleneck. And for NRIs, it offers something IGI never could: proximity to the places they are actually going.

Bookings for IndiGo's inaugural routes are expected to open shortly. Fares and schedules for the Bengaluru and Navi Mumbai routes will be listed on airline websites once final slot confirmations are complete."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Face-Scan Boarding System Is Expanding to 65 Airports — What NRIs Need to Know",
        "subheadline": "DigiYatra, which has already processed 100 million seamless journeys, will add 27 more airports by next year. The system cuts entry time from 15 seconds to five — but NRIs need to set it up before they land.",
        "slug": make_slug("digiyatra-expansion-65-airports-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs flying into India often face the longest lines at domestic connections — the security check at Mumbai T2, the boarding scrum at Delhi T1D, the interminable queue at Bengaluru. DigiYatra, India's facial recognition boarding system, lets you skip document checks entirely if you register in advance. With OCI cards now linked to the system and 27 more airports coming online, NRIs who set up DigiYatra before their next India trip will move through airports in a fraction of the usual time. The catch: you need to download the app and register before you arrive.",
        "tags": ["travel", "airports", "technology", "digiyatra", "india", "biometrics"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/govt-says-27-more-airports-to-have-digiyatra-by-next-year"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/27-new-airports-to-have-digiyatra-by-next-year-centre"},
            {"name": "Civil Aviation Ministry of India", "url": "https://www.civilaviation.gov.in/"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6544060/pexels-photo-6544060.jpeg",
        "body": """India's Civil Aviation Ministry announced last week that DigiYatra — the country's facial recognition-based contactless boarding system — will expand to 27 additional airports by next year, bringing the total to 65 from the current 38. The system, which has already facilitated over 100 million seamless journeys and crossed 24 million app downloads, is fast becoming the default way Indians move through airports. For NRIs who fly to India once or twice a year, the question is no longer whether DigiYatra matters — it is whether they will bother to set it up.

## How It Works

DigiYatra replaces the manual document-checking process at airport entry gates and boarding points with facial recognition technology (FRT). Passengers register through the DigiYatra app, linking their face scan to their boarding pass and identity document. At the airport, cameras at entry gates and security checkpoints verify the traveler's identity in seconds — no paper boarding pass, no ID card pulled out of a wallet, no frantic search for a printed itinerary.

The results are measurable. According to the ministry, the average entry processing time has dropped from 15 seconds per passenger to just 5 seconds. At airports like Delhi T3 and Bengaluru's Kempegowda, where peak-hour queues can stretch 30 minutes or more, that three-fold improvement translates to meaningfully shorter waits.

Civil Aviation Minister K. Rammohan Naidu said the expansion is part of a larger infrastructure push tied to India's aviation growth targets: 500 million annual airport passengers by 2030, doubling to nearly one billion by 2040. "Right now, DigiYatra is active at 38 airports, and by next year, 27 more airports will be enabled," he said.

## The NRI Angle

Here is where it gets practical. DigiYatra currently supports Indian passport holders and Aadhaar-linked travellers natively. For NRIs holding OCI (Overseas Citizen of India) cards, registration is possible through the app using OCI card details and a selfie scan. The system has been progressively adding support for foreign travel documents since late 2025.

The key step is pre-registration. DigiYatra is not something you sign up for at the airport counter — you download the app (available on iOS and Android, now supporting 11 languages with 11 more regional languages planned by year-end), complete the facial enrollment, and link your booking. The entire process takes under five minutes on a stable connection.

For NRIs catching domestic connections — say, landing at Mumbai on an international flight and connecting to Goa or Kochi — DigiYatra eliminates the re-verification bottleneck at security. That alone can save 20-30 minutes on a tight connection.

## Privacy and Data

The ministry emphasized that passenger data shared with DigiYatra remains encrypted and stored on the user's own device. Facial data is shared only for a limited duration with the departure airport for immediate verification and is not retained centrally. This is a notable distinction from facial recognition systems in other countries, where data is typically stored in government or corporate databases.

Whether that architecture survives the expansion to 65 airports and a billion annual travelers remains to be seen. But for now, the privacy model is device-first, not cloud-first.

## What Is Missing

DigiYatra does not yet cover international departure or arrival gates at most airports — it is primarily a domestic boarding facilitation tool. NRIs arriving on international flights still go through the standard immigration and customs process. The ministry has not announced a timeline for extending DigiYatra to international terminals, though integration with the e-gate system at select airports is reportedly under discussion.

The system also requires a smartphone with a working camera and internet connection for initial setup. For elderly NRI parents flying domestically within India, this could be a setup-once-and-forget situation — but someone tech-savvy needs to do the initial enrollment.

## The Bottom Line

At 38 airports and 100 million journeys, DigiYatra has passed the pilot phase. The expansion to 65 airports by next year — covering essentially every airport an NRI is likely to use for domestic connections — makes it worth the five-minute setup investment. Download the app before your next India trip, enroll your face, and skip the line. The technology is already there. The only missing piece is you."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
