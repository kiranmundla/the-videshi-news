#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-31 02:00 UTC run. Two fresh articles."""

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

# ─────────────────────────────────────────────
# ARTICLE 1: 250 Daily Flights Cut
# ─────────────────────────────────────────────
article1_body = """Air India, IndiGo, and Air India Express will collectively pull roughly 250 domestic flights per day from India's skies starting in June — a cut that will run through August and reshape summer travel for anyone trying to move around the country.

The numbers are stark. Air India plans to axe about 22 per cent of its domestic schedule, roughly 110 flights a day from a base of 500. The airline, which posted a record loss of approximately ₹25,000 crore (over $2 billion) in the 2025-26 fiscal year, described the move as "temporary network rationalisation" driven by the sustained impact of high fuel prices. It had already suspended 145 weekly international flights earlier this year.

IndiGo, which operates some 2,200 domestic flights daily and controls 62 per cent of the domestic market, is trimming capacity by 5 to 7 per cent — another 110 or so services per day. Air India Express, the low-cost arm, will cut close to 10 per cent of its 340 daily domestic flights.

Together, the three carriers account for roughly 90 per cent of India's domestic air traffic. When they sneeze, the entire system catches cold.

## Why Now

Three forces converged. Aviation turbine fuel (ATF) prices have surged, in part because of the US-Israel conflict with Iran and the sustained closure of Pakistani airspace to Indian carriers. Air India alone has spent an estimated ₹4,000 crore rerouting international flights around Pakistan. The Indian rupee has weakened against major currencies, compounding fuel costs denominated in dollars. And domestic travel demand typically softens after the summer holiday surge, making overstretched schedules harder to justify financially.

The result is that operating thin Indian margins on expensive fuel, with longer routing and weaker demand, simply does not compute — so the airlines are pulling back.

## What It Means on the Ground

The impact is already showing up at booking portals. Delhi, the country's busiest aviation hub, is seeing last-minute fares spike by 20 to 30 per cent compared to a week earlier.

Delhi-Mumbai economy tickets that would normally hover around ₹6,000-8,000 are now touching ₹12,000 to ₹16,000 for last-minute bookings. Delhi-Bengaluru and Delhi-Chennai economy fares have climbed to ₹14,000-15,000, with business class crossing ₹50,000. Even shorter regional hops — Delhi-Lucknow, Delhi-Patna — are breaching ₹7,500 to ₹9,000 during peak hours.

Mumbai, Delhi, and Bengaluru are expected to see the biggest disruptions, precisely the routes that carry the heaviest NRI connecting traffic.

## The NRI Calculus

For Indian Americans planning summer trips home, the domestic leg just became the most unpredictable part of the itinerary. Most NRIs fly into Delhi or Mumbai on international carriers and then connect onward to Hyderabad, Bengaluru, Chennai, Ahmedabad, or smaller cities. Fewer flights mean fewer connection options and higher prices — and rebooking becomes a nightmare when half the schedule has been cut.

Here is what to do. First, book domestic connecting flights immediately if you have not already. Availability will only tighten through July. Second, consider flying direct to your destination city. Air India, Emirates, and United all serve Bengaluru, Hyderabad, and Chennai with nonstop or one-stop flights from US gateways — skip Delhi entirely if your family is in the south.

Third, look at trains. The Vande Bharat Express network has expanded significantly and covers routes like Delhi-Varanasi, Delhi-Jaipur, and Mumbai-Goa with comfortable, high-speed service. For distances under 600 kilometres, a four-hour train may now be faster than the airport-to-airport ordeal of a cancelled domestic flight.

Air India has said passengers affected by cancellations will be offered re-accommodation on alternative flights, complimentary date changes, or full refunds. IndiGo has characterised its cuts as "seasonal adjustments." Neither statement will be much comfort when you are standing in a Delhi terminal with a toddler and a ₹16,000 last-minute ticket to Bengaluru.

Plan accordingly."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Cutting 250 Domestic Flights a Day This Summer — and Fares Are Already Surging",
    "subheadline": "Air India slashes 22 per cent of operations, IndiGo trims capacity by up to 7 per cent, and Delhi ticket prices jump 30 per cent. NRIs heading home need to rethink their connecting flights.",
    "slug": make_slug("india-250-flights-cut-summer-fares-surge-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Most NRIs connect through Delhi or Mumbai for domestic onward travel. With 250 daily flights cut June-August and fares spiking 20-30%, the domestic leg of summer India trips just became the most expensive and unreliable part of the itinerary. Book connecting flights now, consider flying direct to destination cities, or use Vande Bharat trains.",
    "tags": ["travel", "airlines", "air-india", "indigo", "flights", "fares", "nri-travel"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/travel-news/air-india-indigo-to-cut-250-daily-domestic-flights-from-june"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/air-india-indigo-to-cut-250-daily-domestic-flights-from-june-amid-fuel-cost-surge"},
        {"name": "The Daily Jagran", "url": "https://www.thedailyjagran.com/trending/delhi-flight-fares-soar-30-percent-air-india-indigo-250-daily-domestic-flights-cut-june"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/air-india-indigo-to-cut-250-domestic-flights-daily-to-reduce-fuel-costs"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2833379/pexels-photo-2833379.png",
    "body": article1_body,
}

# ─────────────────────────────────────────────
# ARTICLE 2: DigiYatra Expansion
# ─────────────────────────────────────────────
article2_body = """India's facial recognition airport system DigiYatra just crossed a milestone that would have seemed absurd five years ago: 100 million seamless passenger journeys, processed without a single paper document check at the gate.

The Civil Aviation Ministry announced on Saturday that the platform, which uses facial recognition to replace manual ID verification at airport entry, security, and boarding, is now live at 38 airports across India and will expand to 27 more by next year — bringing the total to 65. The app has been downloaded 24 million times and currently supports 11 languages, with 11 more regional languages planned by December.

The numbers matter less than the experience they represent. DigiYatra has cut the average airport entry processing time from 15 seconds per passenger to just five. For anyone who has stood in the scrum outside an Indian airport terminal at 4 AM, watching a security guard laboriously match a printout to a face to a boarding pass, that is not incremental improvement — it is a category shift.

## How It Works

The system is straightforward. Download the DigiYatra app, register with your Aadhaar or passport, and link your boarding pass. At participating airports, walk up to the DigiYatra e-gate, look at the camera, and go through. No printout. No ID card juggling. No "sir, please step aside."

The technology runs on facial recognition matched against the identity you registered, and the verification happens in real time. The ministry emphasises that passenger data remains encrypted and stored on the user's own device — it is shared only temporarily with the departure airport for immediate verification, then purged. Whether that privacy architecture survives contact with 100 crore annual passengers (projected by 2040) is a question worth watching, but for now the design is sound.

## The 65-Airport Map

DigiYatra started modestly — six airports in December 2022 — and has since rolled out across India's busiest hubs including Delhi, Mumbai, Bengaluru, Hyderabad, Kolkata, and Chennai. The next 27 airports will likely include a mix of growing regional airports and tier-two cities that have seen passenger traffic spike as domestic aviation boomed.

Civil Aviation Minister K. Rammohan Naidu framed the expansion in the context of India's aviation trajectory: annual passenger traffic is projected to hit 500 million by 2030 and approach a billion by 2040. At those volumes, the old paper-and-eyeball system would not just be slow — it would physically break.

## Why NRIs Should Care

For Indian Americans, this changes the texture of the India trip. The domestic airport experience — the part after you clear immigration and step into the connecting-flight chaos — has long been the most stressful segment. Long entry lines, aggressive queue-jumping, guards demanding documents you already showed twice. DigiYatra does not fix everything, but it removes the most friction-heavy touchpoint.

Here is the practical guide. Before your next trip to India, download the DigiYatra app (available on iOS and Android), register with your passport (Indian passport works best; OCI card support is being evaluated), and link your domestic boarding passes once you have them. At any of the 38 live airports — and soon 65 — you will walk through a dedicated lane in seconds.

The bigger development is on the horizon. The Digi Yatra Foundation has already completed an IATA-aligned contactless international travel proof of concept with IndiGo at Bengaluru's Kempegowda International Airport. The pilot tested how verifiable credentials and consent-based identity sharing could work across airlines and borders. If that model scales, NRIs could eventually clear both international and domestic checkpoints with nothing but their face.

That is still years away. But the domestic system works today, it is expanding fast, and it is the kind of upgrade that most NRIs do not know exists until they are standing in the wrong queue watching someone else breeze through.

Set it up before you fly."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "DigiYatra Just Hit 100 Million Journeys — and India Wants Your Face at 65 Airports by 2027",
    "subheadline": "The facial recognition system that cut airport entry time from 15 seconds to five is scaling to 27 more airports. For NRIs used to chaotic Indian terminal lines, the experience is quietly transforming.",
    "slug": make_slug("digiyatra-100-million-journeys-65-airports-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "The domestic airport experience has long been the most stressful part of NRI India trips. DigiYatra replaces the paper-and-eyeball entry check with facial recognition in 5 seconds, is live at 38 airports (65 by 2027), and an international pilot at Bengaluru hints at eventual cross-border expansion. Download the app before your next trip.",
    "tags": ["travel", "digiyatra", "airports", "india", "technology", "facial-recognition", "nri-travel"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/digiyatra-to-expand-to-27-more-airports/article69637988.ece"},
        {"name": "Economy India", "url": "https://economyindia.in/digiyatra-to-expand-to-27-more-airports-over-10-crore-seamless-journeys-recorded/"},
        {"name": "All India Radio News", "url": "https://airnews.in/2026/05/30/civil-aviation-minister-naidu-announces-digiyatra-expansion/"},
        {"name": "The Hindu Business Line (DigiYatra as identity layer)", "url": "https://www.thehindubusinessline.com/economy/logistics/beyond-aviation-digi-yatra-eyes-role-as-extensible-digital-identity-layer/article69622785.ece"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37094662/pexels-photo-37094662.jpeg",
    "body": article2_body,
}

# ─────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles processed.")
