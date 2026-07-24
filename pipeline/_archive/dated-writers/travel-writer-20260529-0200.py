#!/usr/bin/env python3
"""Travel writer – 2026-05-29 02:00 UTC run. Publishes 2 travel articles."""

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
        "headline": "India's Monsoon Arrived Five Days Early — Why Smart NRIs Are Booking Home Trips Now",
        "subheadline": "With hotel rates down 30-50% and domestic flights cheaper than they've been all year, the early monsoon is turning June into the NRI traveler's sweet spot.",
        "slug": make_slug("india-monsoon-early-arrival-nri-travel-opportunity"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who usually visit India in December or summer peak can save hundreds per person by shifting their trip to June-August monsoon season, when fewer tourists mean better availability and dramatically lower prices on flights and hotels.",
        "tags": ["travel", "monsoon", "india", "budget-travel", "kerala", "meghalaya"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "India Meteorological Department", "url": "https://srkanalytics.com/monsoon-2026-imd-predicts-early-arrival-in-kerala/"},
            {"name": "Wego Travel Blog", "url": "https://blog.wego.com/best-monsoon-destinations-in-india/"},
            {"name": "SOTC India", "url": "https://sotc.in/blog/best-places-to-visit-in-july-in-india"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/air-india-indigo-cut-domestic-capacity-new-indian-express-reports-2026-05-27/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ee/House_Boat_DSW.jpg",
        "image_caption": "A houseboat on Kerala's backwaters — monsoon transforms the landscape into its most photogenic version.",
        "body": """The India Meteorological Department confirmed on May 26 that the southwest monsoon has officially arrived in Kerala — five days ahead of its traditional June 1 schedule. For the roughly 4.5 million Indian Americans planning trips home this year, the early onset isn't just a weather footnote. It's a pricing signal.

## The Math That Matters

Airfares on key NRI corridors — SFO-DEL, JFK-BOM, ORD-HYD, LAX-BLR — typically crater between mid-June and August. The monsoon window is India's aviation off-season, and with Air India and IndiGo both slashing domestic capacity by 7-25% this summer due to Iran war-driven fuel costs, airlines are aggressively discounting the seats they do fly. Round-trip fares from the US to India are running $600-$900 on major carriers right now, compared to $1,200-$1,800 during Diwali and December peak.

Hotels follow the same curve. Properties across Rajasthan, Kerala, and Karnataka drop rates by 30-50% during monsoon months. That Taj property in Udaipur that runs $400 a night in November? It's $180 in July. The ITC Grand Chola in Chennai? Down 40%. For NRI families booking multiple rooms for extended stays — and most do — the savings compound fast.

## Where to Go (and Where to Skip)

Not every Indian destination works in the monsoon. Here's what does:

**Kerala's backwaters** hit their visual peak during monsoon. The canals swell, the vegetation turns electric green, and Ayurvedic resorts run their best promotions of the year. Alleppey houseboats that cost ₹15,000 a night in January drop below ₹8,000.

**Meghalaya and the Northeast** transform into something otherworldly. Cherrapunji and Mawsynram — the wettest places on Earth — deliver waterfalls, living root bridges, and cloud forests that don't exist in any other season. It rains hard, but between the downpours the landscape is staggering.

**Ladakh and Kashmir** operate on a different weather clock. The monsoon largely bypasses them, making June through August the actual peak season in the high Himalayas. Dal Lake houseboats, Pangong Tso, and the Zanskar Valley are at their most accessible. Book early — these are the destinations where NRI demand has already pushed prices up.

**Rajasthan** splits the difference. The desert gets dramatic — Jaisalmer's dunes after rain, Udaipur's lakes full for the first time in months — but the humidity can be punishing. The Aravallis and southern Rajasthan (Kumbhalgarh, Mount Abu) handle it better than Jaipur.

**Skip**: Mumbai during peak monsoon (July-August) unless you're visiting family. The city floods regularly and transportation becomes unreliable. Goa's beaches are closed to swimming in June-July. The Andamans are technically accessible but rough seas limit island-hopping.

## The NRI Advantage

Indian Americans have a structural edge that most monsoon travel guides ignore: you're visiting family, not checking into a tourist bubble. That means you have a home base, local knowledge of which roads flood and which don't, and someone to pick you up from the airport when your connecting flight gets delayed by weather.

The early monsoon also means kharif crop season starts sooner, and with it the festivals. Small-town India during monsoon has a texture that the winter tourist circuit never shows — temple festivals, regional food seasons (hello, alphonso mangoes in June, jackfruit in July), and communities that are genuinely glad to see visitors because almost nobody else is coming.

## Practical Moves

**Book domestic flights now.** With Air India cutting 22% of domestic capacity and IndiGo trimming 7-10%, the seats that remain on popular NRI routes (DEL-LKO, BOM-GOI, BLR-CCU) will fill early. Akasa Air and SpiceJet have been expanding into routes the big two abandoned — check them for backup options.

**Pack for the rain, not against it.** Quick-dry clothing, waterproof phone cases, and a compact umbrella matter more than rain jackets (which are unbearably hot in Indian humidity). Leave the heavy luggage — monsoon travel rewards those who move light.

**Travel insurance is non-negotiable.** Flight cancellations due to weather are more common June through September. Make sure your policy covers trip interruption, not just medical emergencies.

The monsoon isn't India's ugly season. It's India's secret season — the one that most of the diaspora has been conditioned to avoid. This year, with the early arrival and rock-bottom pricing, the case for going against the grain has never been stronger."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's e-Arrival Card Is Now Mandatory — The Two-Minute Fix That Could Save Your Trip",
        "subheadline": "Delhi Airport stopped accepting paper arrival forms in April. If you haven't heard about the switch, you're not alone — and you could face delays at immigration.",
        "slug": make_slug("india-earrival-card-mandatory-nri-guide"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Most NRIs visit India once or twice a year. The switch from paper to mandatory digital arrival cards happened quietly, and many diaspora travelers — especially OCI cardholders who haven't visited since 2024 — risk arriving unprepared.",
        "tags": ["travel", "india", "immigration", "oci", "visa", "airport", "e-arrival-card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Travel Noire", "url": "https://travelnoire.com/india-issues-new-e-arrival-card-required-for-all-international-travelers"},
            {"name": "Travelobiz", "url": "https://travelobiz.com/travelling-to-india-e-arrival-card-becomes-mandatory-from-april-2026/"},
            {"name": "Consulate General of India, St. Petersburg", "url": "https://cgispburg.gov.in/"},
            {"name": "Live From A Lounge", "url": "https://livefromalounge.com/india-abolishes-physical-arrival-cards-for-foreign-visitors-from-october-1-2025/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4606721/pexels-photo-4606721.jpeg",
        "image_caption": "India's new e-Arrival Card must be submitted online before you land — paper forms are gone for good.",
        "body": """If you're flying to India this summer and your last visit was before October 2025, there's a small but consequential change waiting for you at immigration: the paper disembarkation card is gone. India has replaced it with a mandatory digital form called the e-Arrival Card, and as of April 2026, Delhi's Indira Gandhi International Airport no longer accepts the old paper version at all. Other major airports are following.

The change happened in stages. India's Bureau of Immigration launched the e-Arrival Card system on October 1, 2025, initially as an option alongside paper forms. By early 2026, the government pushed harder — physical forms were phased out at Delhi first, with Mumbai, Bengaluru, Hyderabad, and Chennai transitioning on rolling timelines. The goal is a fully paperless arrival experience at every international airport in India by the end of the year.

## What You Need to Do

The process takes about two minutes, but you need to do it before you board.

**Step 1:** Visit [boi.gov.in](https://boi.gov.in/) or download the **Indian Visa Su-Swagatam** app (available on iOS and Android). The website works fine on mobile browsers if you'd rather not install anything.

**Step 2:** Fill in your details — passport number, flight information, Indian address (your family's home address works), purpose of visit, and basic personal information. OCI cardholders select "OCI" as their visa type. The form asks for your OCI card number, so have it handy.

**Step 3:** Submit the form **within 72 hours of your scheduled arrival**. You can submit it up to four days before landing, but if you submit more than 72 hours out, the system generates a QR code that you'll need to screenshot or print. If you submit within the 72-hour window, immigration officers can pull your record automatically using your passport.

**Step 4:** Save the confirmation. The system sends an email with a reference number and QR code. Screenshot it, print it, or save the PDF — whatever ensures you can access it when your phone has no signal at the immigration counter.

## What Happens If You Don't Fill It Out

You won't be denied entry, but you will be delayed. Immigration officers at Delhi are directing passengers without a completed e-Arrival Card to kiosks set up in the arrival hall, where they fill out the digital form on the spot. During peak arrival windows — which for NRI routes means 1-4 AM, when the Dubai, Doha, and Singapore connections all land within an hour of each other — the kiosk lines can stretch to 30 minutes or more.

For OCI cardholders, this is particularly frustrating. The whole point of the OCI card is frictionless entry. Showing up without the e-Arrival Card adds exactly the kind of bureaucratic delay the card was supposed to eliminate.

## The OCI Wrinkle

OCI holders face a specific confusion point: many assume the e-Arrival Card is only for visa holders and foreign nationals. It's not. Every international traveler entering India must complete it, regardless of citizenship or residency status. Indian passport holders are currently exempt, but OCI cardholders — who hold foreign passports — are not.

This matters for mixed-passport families, which describes most NRI households. If one parent holds an Indian passport and the other has an OCI, only the OCI holder needs to fill out the form. Children traveling on foreign passports with OCI cards need their own submissions. One form per person, no family filing.

## Why India Made the Switch

The move is part of a broader push toward digital border management that the Bureau of Immigration has been building toward for years. Paper disembarkation cards were error-prone — handwritten entries created mismatches in immigration databases — and the physical forms generated tonnes of paper waste annually. The digital system feeds directly into India's Immigration, Visa, and Foreigners Registration & Tracking (IVFRT) platform, giving authorities real-time data on passenger flows.

For NRIs, the practical upside is real: once the system matures, it should mean faster immigration processing. The Bureau of Immigration claims that airports with full e-Arrival Card adoption are clearing passengers 35-40% faster than those still running parallel paper systems.

## The Two-Minute Drill

Set a reminder for 48 hours before your departure. Pull up boi.gov.in, fill in the form, save the QR code. That's it. The form doesn't ask for anything you don't already have on your ticket and passport.

The cost of forgetting? At best, 10 extra minutes at a kiosk while jet-lagged. At worst, the back of a long line at 3 AM in Terminal 3, watching families who did their homework sail through the e-gates while you wait. For a two-minute task, the return on investment is hard to beat."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
