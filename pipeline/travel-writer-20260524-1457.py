#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-24 batch"""
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


# ── ARTICLE 1 ─────────────────────────────────────────────
art1_body = """India opened two brand-new airports in the span of a week — and for the millions of NRIs who dread the annual Mumbai and Delhi gauntlet, the implications are immediate.

## Navi Mumbai Is Finally Real

Navi Mumbai International Airport (NMIA), inaugurated by Prime Minister Modi and developed by the Adani Group in coordination with CIDCO, launched commercial operations on May 22 with IndiGo as its first carrier. The maiden arrival — an Airbus A320 from Bengaluru — touched down to a water-cannon salute at 8 AM, followed by the first departure to Hyderabad.

Phase one delivers a single runway and terminal handling 20 million passengers annually. The long-term plan: two runways and 90 million capacity, making it one of India's largest aviation hubs. IndiGo is already connecting NMIA to Delhi, Bengaluru, Hyderabad, Ahmedabad, Goa (Mopa), Jaipur, Nagpur, Kochi, and Mangalore, with more routes coming as demand builds.

For anyone who has ever spent two hours in a taxi crawling from Navi Mumbai or Panvel to Chhatrapati Shivaji Maharaj International, this changes the calculus entirely. The new airport sits close to key highways and planned metro links, cutting ground transit to under 30 minutes for most of the eastern Mumbai Metropolitan Region.

## Noida Airport Opens Next Month

Less than 200 kilometres north, Noida International Airport near Delhi NCR begins operations on June 15 with IndiGo as the launch carrier. Akasa Air follows one day later with daily nonstop flights to Bengaluru and Navi Mumbai.

The airport is designed to absorb the pressure on Delhi's Indira Gandhi International, which has been operating near capacity during peak hours. For NRIs flying into the NCR to visit family in Noida, Greater Noida, or western Uttar Pradesh, this eliminates the gruelling cross-Delhi airport transfer that can take three hours in traffic.

## What This Means for NRIs

These openings are not incremental improvements — they represent the first genuinely new commercial airports serving India's two biggest metro regions in decades.

**Mumbai-bound NRIs** from the Bay Area, New Jersey, and Chicago can expect international carriers to add NMIA to their networks within the year as the airport ramps up. Until then, connecting via domestic flights from Delhi or Bengaluru to NMIA is already live.

**Delhi-NCR NRIs** flying home to UP, Haryana, or Rajasthan gain a second entry point that avoids the congestion of IGI entirely.

Both airports also signal a broader trend: India processed over 376 million domestic passengers in 2025, and the government is aggressively building capacity to match. For the diaspora, more airports means more route options, more competition, and eventually, lower fares on the routes that matter most."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Two New Airports in One Week: India Opens Navi Mumbai and Noida, Reshaping Travel for the Diaspora",
    "subheadline": "Navi Mumbai International launched commercial flights on May 22; Noida International follows on June 15. Both promise to cut hours off the ground-transit nightmare NRIs know too well.",
    "slug": make_slug("india-navi-mumbai-noida-airports-open-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs flying to Mumbai and Delhi NCR gain two entirely new entry points, eliminating the cross-city airport transfers that can add 2-3 hours to every India trip. International carriers are expected to add both airports to their networks within a year.",
    "tags": ["travel", "airports", "india", "mumbai", "delhi", "infrastructure"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/vr6b1qt8am77/"},
        {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/1zzvmdz7ozbp/"},
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/19528200/pexels-photo-19528200.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Modern airport architecture in Mumbai. Photo: Keith Lobo / Pexels",
    "body": art1_body,
}


# ── ARTICLE 2 ─────────────────────────────────────────────
art2_body = """If you are an OCI cardholder who has not visited India since April, there is a new step at the border — and skipping it could cost you an hour in the immigration queue.

## Paper Forms Are Gone

As of April 1, 2026, India's Bureau of Immigration discontinued the paper disembarkation card that has been handed out on flights since the 1960s. In its place: a mandatory digital e-Arrival Card that every foreign national — including OCI and PIO cardholders — must complete online within 72 hours of arrival.

The form is submitted through the Indian government's [e-Arrival Card portal](https://eac.gov.in) or the Su-Swagatam mobile app. It takes roughly five minutes, costs nothing, and requires no document uploads. Upon completion, the system generates a QR code that you present at immigration.

## The Catch That Trips Up NRIs

The process is straightforward, but there is one gotcha that has already caught travellers off guard: if you close the browser after submitting without downloading or screenshotting your QR code, you cannot retrieve it. Submitting a new form creates a duplicate record. And arriving at immigration without the QR code does not mean the officer can simply look you up — in many cases, they cannot, which means a long wait at a staffed kiosk.

The U.S. Embassy in India confirmed the requirement in an April 8 advisory. The UK updated its India travel advisory to reflect the same — paper forms will no longer be accepted under any circumstance.

## Step-by-Step for Your Next Trip

1. **72 hours before landing**: Visit [eac.gov.in](https://eac.gov.in) or download the Su-Swagatam app.
2. **Fill in details**: Passport info, flight number, Indian address, and basic travel purpose. No supporting documents needed.
3. **Submit and immediately save**: Download the PDF, screenshot the QR code, and email both to yourself.
4. **At immigration**: Show the QR code on your phone or a printout. Officers scan it and you proceed.

If you are travelling with family — especially elderly parents on OCI cards — fill out forms for everyone in advance. The system requires a separate submission per traveller.

## Why India Made the Switch

The shift is part of a broader digitisation push. India had already rolled out e-visas for 170+ nationalities and integrated biometric capture at major airports. The e-Arrival Card feeds into a centralised digital passenger database that the Bureau of Immigration says will speed up processing and reduce queues at the 32 immigration counters across India's international airports.

For NRIs, the practical effect is mixed. The form itself is simpler than the old paper card, and skipping the hunt for a pen at 3 AM in the Delhi arrivals hall is a genuine improvement. But the QR-code-or-bust system adds a point of failure that the paper card — for all its annoyances — never had.

## The Bottom Line

Save the QR code in at least two places before you board. Brief your parents. Do it 72 hours out, not at the gate. The immigration officer at Bengaluru or Mumbai at 2 AM will not have patience for "I forgot to download it." This is the new normal for every India trip."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's e-Arrival Card Is Now Mandatory: What Every OCI Holder Needs to Know Before Their Next Trip",
    "subheadline": "Paper disembarkation forms are gone. Since April 1, all foreign nationals — including OCI cardholders — must submit a digital arrival card with a QR code within 72 hours of landing. Here is the step-by-step.",
    "slug": make_slug("india-e-arrival-card-mandatory-oci-nri-guide"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Every NRI with an OCI card is directly affected. The new e-Arrival Card replaces the paper form used on India flights for decades. Failing to complete it means delays at immigration — a practical concern for the 4.5 million OCI holders worldwide.",
    "tags": ["travel", "visa", "oci", "india", "immigration", "e-arrival-card"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Envoy Global", "url": "https://www.envoyglobal.com/news-alert/india-e-arrival-card-for-all-foreign-nationals-within-72-hours-before-arrival/"},
        {"name": "U.S. Embassy in India", "url": "https://in.usembassy.gov/"},
        {"name": "UK High Commission India", "url": "https://www.hcilondon.gov.in"},
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922085/pexels-photo-4922085.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Passport at the gate. Photo: Ekaterina Belinskaya / Pexels",
    "body": art2_body,
}


# ── ARTICLE 3 ─────────────────────────────────────────────
art3_body = """The India Meteorological Department has confirmed that the southwest monsoon will hit Kerala on May 26 — right on schedule and right when summer vacation airfares to India start dropping. If you are an NRI planning a trip home between June and August, monsoon season is not a reason to postpone. It is, done right, the best time to go.

## Why Monsoon Is Underrated for NRI Trips

Most diaspora families default to December–January for India visits — and pay for the privilege. Round-trip fares from SFO or JFK to Indian metros run $1,100–$1,400 during the winter holiday rush. The same routes in July and August drop to $700–$900, with September bottoming out around $500–$600 on carriers like Qatar Airways and Emirates.

Beyond the savings: monsoon India is a different country. The heat breaks. The Ghats turn electric green. Tourist crowds vanish. Your uncle's farm in Karnataka looks like it belongs in a nature documentary. Hotels that charge ₹15,000 in peak season drop to ₹6,000–₹8,000.

The trade-off is rain — sometimes heavy, sometimes disruptive. But with the right planning, that trade-off is overwhelmingly in your favour.

## Best Monsoon Destinations for NRI Families

**Kerala** — The monsoon hits here first (May 26) and stays through September. Munnar's tea estates disappear into mist, Athirappilly Falls runs at full thunder, and Ayurvedic resorts offer monsoon-specific wellness packages. Flights to Kochi from the US connect easily through Dubai or Doha.

**Coorg (Kodagu), Karnataka** — The "Scotland of India" earns the nickname during monsoon. Waterfalls appear everywhere, coffee plantations shimmer, and the crowds that pack Coorg in winter are absent. Drive from Bengaluru in 5 hours, or fly into Mangalore.

**Goa** — Monsoon Goa is nothing like December Goa, and that is the point. Dudhsagar Falls is at peak flow, beaches are empty, and restaurants that cater to tourists in winter quietly serve their best food to locals. Fares to Goa's Mopa airport via domestic connections are at their cheapest.

**Udaipur, Rajasthan** — The lakes fill up, the Palace glows in diffused light, and the Aravalli hills turn green. Udaipur in monsoon is arguably the most photogenic city in India. Fly into the new Maharana Pratap Airport from Delhi or Mumbai.

**Darjeeling and Sikkim** — For NRI families from the eastern diaspora (Kolkata, Bengal, Odisha connections), the Northeast in monsoon offers rolling cloud forests, monastery visits, and temperatures in the teens. Fly to Bagdogra, drive up.

## Practical Tips

**Flights**: Book by early June for July–August travel. The cheapest fares sell out fast on Qatar Airways (DOH hub), Emirates (DXB hub), and Air India nonstops. Use Google Flights with flexible dates — shifting by two days can save $200.

**Health**: Carry a basic monsoon kit: oral rehydration salts, mosquito repellent (DEET-based), waterproof phone pouch, and a quick-dry rain jacket. Dengue peaks during monsoon; long sleeves in the evening are non-negotiable.

**Ground transport**: Roads in hilly regions get dicey. Avoid self-driving in the Ghats during heavy rain. Book a local driver who knows the routes. Landslide-prone areas (Wayanad, Himachal) require checking state advisories before travel.

**For kids**: Monsoon India is sensory overload in the best way — frogs, fireflies, chai in the rain, cousins splashing in puddles. Pack waterproof sandals, not sneakers.

## The Window Is Open

If you have been putting off the India trip because "monsoon is bad" — reconsider. The flights are cheap, the crowds are thin, and the country is at its most alive. Book the ticket. Save the QR code from your e-Arrival Card. And pack a good umbrella."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Monsoon India Is the NRI's Best-Kept Travel Secret — Here Is How to Plan Your Summer Trip",
    "subheadline": "The southwest monsoon hits Kerala on May 26. Flights to India drop to $500–$700. Tourist crowds vanish. Here is the practical guide to making monsoon season work for your family visit.",
    "slug": make_slug("india-monsoon-travel-guide-nri-summer"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "Summer is when NRI families have time off and kids are out of school — but most skip India because of monsoon fears. In reality, July–August fares are 30-40% cheaper than December, and monsoon destinations offer experiences unavailable the rest of the year.",
    "tags": ["travel", "monsoon", "india", "kerala", "goa", "flights", "budget"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "India Meteorological Department", "url": "https://mausam.imd.gov.in/"},
        {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/"},
        {"name": "StayVista Journal", "url": "https://stayvista.com/journal/"},
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29350151/pexels-photo-29350151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Monsoon mist over Munnar tea plantations. Photo: Salem Raju / Pexels",
    "body": art3_body,
}


# ── PUBLISH ───────────────────────────────────────────────
articles = [art1, art2, art3]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted.")
