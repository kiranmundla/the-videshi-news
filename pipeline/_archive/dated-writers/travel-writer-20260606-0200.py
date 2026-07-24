#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "India's Airports Now Scan Your Face Before You Fly — and NRIs Need to Prepare Before They Land",
        "subheadline": "DigiYatra's facial recognition system is now mandatory for international passengers at Delhi, Mumbai, Bengaluru, and Hyderabad. If you haven't enrolled, expect delays — or worse, missed connections.",
        "slug": make_slug("digiyatra-mandatory-international-nri-airports"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs transiting through India's four busiest airports must now enroll in DigiYatra before departure. The Aadhaar-linked requirement could create friction for OCI holders and long-term diaspora members whose Aadhaar credentials have lapsed, while tight 90-minute connections at Delhi T3 are at risk without pre-enrollment.",
        "tags": ["travel", "airports", "digiyatra", "biometric", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/experiences/india-expands-biometric-travel-push-with-mandatory-digiyatra-for-international-passengers"},
            {"name": "Travel and Leisure Asia", "url": "https://www.travelandleisureasia.com/in/news/digiyatra-mandatory-international-passengers-india/"},
            {"name": "VisaHQ", "url": "https://www.visahq.com/news/2026-06-01/in/digiyatra-biometric-transit-made-mandatory-at-delhi-mumbai-bengaluru-and-hyderabad-airports/"},
            {"name": "TravelBiz Monitor", "url": "https://www.travelbizmonitor.com/digiyatra-set-to-transform-international-transit-experience/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/a/a0/Delhi_airport_terminal_3_%28cropped%29.jpg",
        "image_caption": "Inside Terminal 3 at Delhi's Indira Gandhi International Airport",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India's airports have quietly crossed a threshold that will affect every NRI flying through the country this summer.

From June 1, 2026, all international passengers transiting through Delhi, Mumbai, Bengaluru, and Hyderabad are required to use DigiYatra — the government's facial recognition boarding system — to clear security. The mandate, announced by the Ministry of Civil Aviation as a "hub-and-spoke" pilot, marks the first time the biometric platform has moved from voluntary to obligatory.

## How it works

The process begins before you reach the airport. Passengers must download the DigiYatra app and upload an Aadhaar-verified selfie alongside their boarding pass at least 48 hours before departure. On arrival at one of the four hubs, cameras at dedicated e-gates match a live facial scan against the encrypted template stored in DigiYatra's cloud. If the match succeeds, the gate opens — no boarding pass scan, no passport flash, no queue.

The Airports Authority of India estimates the biometric lane trims 12 to 18 minutes from typical transit times at Delhi's Terminal 3, where international transfer corridors have historically been bottleneck-prone during peak evening departures.

Airlines have already adjusted. Air India, IndiGo, and Vistara have updated their pre-departure emails to flag the mandatory registration, while global carriers including Emirates and Lufthansa have issued operational bulletins to ground staff. Failure to enroll does not mean you cannot fly — but it triggers a manual exception flow involving secondary screening that can add 20 minutes or more to your transit, a meaningful risk for passengers on tight 90-minute domestic-to-international connections.

## The Aadhaar problem for NRIs

Here is where it gets complicated for the diaspora. DigiYatra enrollment is tied to Aadhaar, and many NRIs — particularly those who have lived abroad for a decade or more — either never enrolled or let their biometric data go stale. OCI cardholders who are not Indian citizens cannot obtain Aadhaar at all.

The Ministry has indicated that alternative verification pathways will be announced "in due course," but for now the system operates with Aadhaar as the sole identity anchor. Corporate travel managers at multinationals with India operations are already embedding DigiYatra registration into pre-trip approval workflows. Individual travelers should check their Aadhaar status before booking.

## Privacy concerns remain

The mandatory rollout has drawn pushback from digital rights advocates. The Internet Freedom Foundation has argued that requiring facial recognition for airport access lacks a proper statutory framework. The Ministry's response: facial templates are deleted within 24 hours of flight departure, and the programme falls under the 2025 Digital Personal Data Protection Act. A formal audit mechanism, including surprise penetration tests, will be published before the end of the year.

None of this will reassure passengers who object in principle to biometric surveillance. But the practical reality is that DigiYatra now has more than 10 crore recorded domestic journeys, and the roadmap targets nationwide coverage across 27 airports by 2027. Biometric identity is becoming the default gateway for air travel in India.

## What NRIs should do now

If you are flying through Delhi, Mumbai, Bengaluru, or Hyderabad this summer — whether on a stopover or starting your journey — download the DigiYatra app, verify your Aadhaar status, and complete registration before you leave. The alternative is a secondary screening queue that could turn a smooth connection into a scramble for your gate.

For the estimated 32 million members of the Indian diaspora who fly through these four hubs every year, this is no longer optional. India's airports have decided that your face is your boarding pass. The question is whether you will be ready when the camera turns on."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Taj Hotels Plants Its Flag in Frankfurt — and Indian Luxury Hospitality Arrives in Continental Europe",
        "subheadline": "IHCL's first property on the European mainland revives a Frankfurt landmark with Bombay Brasserie, Ayurvedic wellness, and a strategic location that pairs perfectly with Germany's new visa-free transit for Indians.",
        "slug": make_slug("taj-hessischer-hof-frankfurt-indian-luxury-europe"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "For the roughly 200,000 Indians living in Germany and the millions transiting through Frankfurt each year, the Taj Hessischer Hof offers a taste of home at a major European hub — arriving just as Germany eliminated transit visa requirements for Indian nationals on June 3.",
        "tags": ["travel", "hotels", "taj", "frankfurt", "luxury", "europe"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/cnier8618tk8/"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/cf/Eingangsbereich_Hessischer_Hof.jpg",
        "image_caption": "The entrance of the Hessischer Hof in Frankfurt, now operating as Taj Hessischer Hof",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """The Tata Group's hospitality arm has just pulled off something it has been circling for years: a permanent address on continental Europe.

Taj Hessischer Hof Frankfurt, a 126-room property opposite the Messe Frankfurt exhibition grounds, opened its doors in early June under Indian Hotels Company Limited (IHCL). It is the first Taj-branded hotel on the European mainland, extending a global portfolio that already includes properties in London, New York, Dubai, and Cape Town but had conspicuously skipped the continent between the English Channel and the Bosphorus.

## A landmark revived

The Hessischer Hof is not a new building. For decades it was one of Frankfurt's most recognizable luxury addresses, a favourite of trade fair delegates and corporate executives who needed proximity to Europe's largest exhibition complex. The hotel closed during the pandemic as the business-travel segment collapsed, and the property sat dark while Frankfurt's hotel market slowly rebuilt.

Its reopening under the Taj banner represents a bet by owner Peakside Capital and operator IHCL that Frankfurt's fundamentals remain sound. The city recorded approximately 11.02 million overnight stays in 2025, and Messe Frankfurt continues to host some of the world's largest exhibitions, drawing millions during major event cycles.

## What's inside

The property brings several signature Taj concepts to Germany for the first time. Bombay Brasserie, the fine-dining brand that has anchored Taj properties from Mumbai to London, introduces Indian cuisine to Frankfurt's competitive restaurant scene. The J Wellness Circle offers therapies rooted in Ayurveda — a distinctive pitch in a city saturated with Western spa brands. And The Chambers, Taj's members-only business club, targets the corporate networking market that Frankfurt practically runs on.

The 126 rooms have been renovated to blend the building's original German architectural character with IHCL's contemporary design language. For a hotel group that began with the Taj Mahal Palace in Mumbai in 1903 and now manages roughly 630 properties across 15 countries with 255 more in the pipeline, the Frankfurt opening is less an experiment than a statement: Indian luxury hospitality belongs at the top table in every major market.

## Why this matters for the diaspora

The timing is conspicuously good. On June 3 — days before the hotel's soft launch — Germany officially eliminated the airport transit visa requirement for Indian nationals. Indians flying through Frankfurt or Munich to third countries no longer need a separate Type A Schengen transit visa, a long-standing friction point that had pushed many NRI travelers toward connecting through Dubai, Doha, or Istanbul instead.

The combination of visa-free transit and a recognizable Indian luxury brand at Frankfurt Airport's doorstep could meaningfully shift routing choices for the diaspora. For the estimated 200,000 Indians living in Germany and the far larger number who pass through Frankfurt on their way between North America and South Asia, the Hessischer Hof offers something no European hotel previously did: the specific warmth, culinary vocabulary, and hospitality instincts that Taj has refined over 123 years.

## A bigger picture

IHCL's continental European entry follows a pattern visible across Indian hospitality. The Oberoi Group has expanded into Morocco and Indonesia. Lemon Tree is pushing into the Middle East. ITC Hotels, freshly demerged from its parent, is scouting international management contracts. What was once an industry content to dominate the domestic market is now systematically planting flags abroad, often targeting cities with large Indian business and diaspora populations.

Frankfurt — financial capital, aviation hub, trade fair powerhouse, home to the European Central Bank — checks every box. If the Hessischer Hof succeeds, expect Taj to move deeper into Europe. Paris, Milan, and Zurich are all on the radar.

For NRIs who have spent years choosing between soulless airport hotels and Western luxury brands that treat Indian food as an afterthought, the Taj's arrival in Frankfurt is a small but satisfying shift. The diaspora finally has one of its own in the heart of Europe."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Coromandel Coast Gets a Luxury Upgrade — and Chennai's Diaspora Has a New Reason to Stay Longer",
        "subheadline": "InterContinental Chennai Mahabalipuram Resort reopens after a multi-million-dollar overhaul, bringing plunge pools, a meditation garden, and ocean-facing suites to one of South India's most underrated stretches of coastline.",
        "slug": make_slug("intercontinental-mahabalipuram-resort-chennai-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Chennai is home to one of the largest South Indian diaspora feeder cities, yet NRIs visiting family rarely explore beyond the city. The reimagined resort, 50 km south near the UNESCO Shore Temple, gives the Tamil diaspora a luxury beach destination that can extend the typical family visit by two or three days.",
        "tags": ["travel", "hotels", "chennai", "mahabalipuram", "luxury", "resort"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hotel Magazine NZ", "url": "https://hotelmagazine.co.nz/2026/06/05/opening-for-intercontinental-chennai-mahabalipuram-resort/"},
            {"name": "IHG Hotels & Resorts", "url": "https://www.ihg.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37584854/pexels-photo-37584854.jpeg",
        "image_caption": "The Shore Temple at Mahabalipuram during sunset, a UNESCO World Heritage Site near the resort",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """Here is a pattern familiar to every NRI who grew up in Tamil Nadu: you fly into Chennai, spend a week shuttling between family homes in T. Nagar and Adyar, eat your body weight in filter coffee and dosa, and fly home without once leaving the city limits. The coast south of Chennai — one of India's most dramatic stretches of shoreline, dotted with 7th-century Pallava temples and fishing villages that look like they have not changed in centuries — barely registers.

InterContinental Hotels Group is betting that this is about to change.

## A resort reborn

InterContinental Chennai Mahabalipuram Resort has just completed a multi-million-dollar transformation and reopened along the East Coast Road, roughly 50 kilometres south of Chennai's international airport. Set across 15 acres of landscaped beachfront, the 110-room property takes design cues from the iconic Shore Temple — the UNESCO World Heritage Site that sits less than a 10-minute drive away — while delivering the kind of contemporary luxury that Chennai's hotel market has historically lacked outside the business district.

The overhaul is substantial. New ocean-facing suites come with private plunge pools. A Grand Presidential Suite offers a jacuzzi and steam room with Bay of Bengal views. The Presidential Suite has its own infinity pool and dedicated spa room. Beyond the rooms, the resort has added an ocean-facing ballroom, a sports pavilion, scenic walking trails, and a meditation garden designed for what IHG calls "mindful experiences" — a nod to the wellness tourism trend that is reshaping luxury hospitality globally.

"This relaunch marks a proud milestone for us," said Anand Nair, the resort's General Manager. "Our ambition is to position the resort not merely as a place to stay, but as a destination in its own right."

## The Coromandel Coast's moment

Mahabalipuram has always been one of South India's most compelling cultural destinations. The Shore Temple, the Pancha Rathas, and Arjuna's Penance are among the finest examples of Pallava architecture anywhere. The town hosted the Modi-Xi informal summit in 2019, briefly putting it on the global diplomatic map. But it has never had the resort infrastructure to match its heritage credentials.

That is changing. The Coromandel Coast — stretching from Chennai south through Mahabalipuram, Pondicherry, and Tranquebar to the Kaveri Delta — is attracting investment from multiple hotel groups. The InterContinental's reopening is the most high-profile addition, but it joins a growing collection of boutique properties and eco-resorts that are transforming a coastline once associated primarily with pilgrimage and fishing into a legitimate leisure destination.

The infrastructure supports it. Chennai's airport handles direct flights from 30 international destinations, including nonstops from San Francisco, Newark, Singapore, Dubai, and London. The East Coast Road itself has been steadily improved, and the drive from the airport to Mahabalipuram now takes around 75 minutes — less if you skip the city entirely.

## Why NRIs should pay attention

For the Tamil diaspora — concentrated in the Bay Area, New Jersey, greater Toronto, Singapore, and London — the resort addresses a gap that has persisted for years. Chennai has world-class hospitals, excellent restaurants, and deep cultural infrastructure. What it has lacked is a luxury beach destination close enough for a quick getaway during the annual family visit.

The InterContinental sits squarely in that gap. Two or three nights at the resort adds a beach and heritage dimension to a trip that might otherwise be entirely urban. The Shore Temple at sunrise, a morning swim in the Bay of Bengal, an afternoon exploring the rock-cut caves, and an evening at the resort's new restaurants — it is the kind of itinerary that turns a family obligation into something approaching a vacation.

IHG currently operates 52 hotels across seven brands in India, with a pipeline of 98 more expected over the next three to five years. The company's Managing Director for South West Asia, Sudeep Jain, called the Mahabalipuram reopening "an important milestone for our luxury portfolio in India" and a new benchmark for "mindful luxury on the Coromandel Coast."

For NRIs who have been visiting Chennai for decades without once staying overnight south of the city, the benchmark is simpler: there is finally a reason to."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
