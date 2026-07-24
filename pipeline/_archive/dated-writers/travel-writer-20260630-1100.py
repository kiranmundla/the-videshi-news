#!/usr/bin/env python3
"""Travel writer — 2026-06-30 11:00 PDT run. Two articles for The Videshi travel section."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Mumbai cruise tourism boom ────────────────────────────────────

article1_body = """Mumbai is quietly becoming a global cruise port — and the numbers are starting to look serious.

In the financial year ending March 2026, Mumbai Port handled 240,000 cruise passengers across 95 vessel calls. For a country that barely registered on the cruise map five years ago, that is a remarkable transformation. And the next twelve months will push it further: Celebrity Cruises, Oceania, Crystal, Silversea and Regent Seven Seas have all confirmed voyages through Mumbai in the FY27 season, marking the first time five luxury international operators have committed to the port in a single year.

"The participation of luxury and premium cruise lines reflects growing international confidence in Mumbai as a world-class cruise destination," M. Angamuthu, Chairperson of the Mumbai Port Authority, told *BusinessLine* last week.

## A fourth ship, and a familiar name

The domestic side of the boom is equally telling. Cordelia Cruises, which established Mumbai as India's primary cruise hub with its flagship MV Empress, will induct a second vessel in October: the MV Cordelia Sky, formerly the Norwegian Sky from Norwegian Cruise Line's fleet. That makes four ships homeported at Mumbai — after the Angriya, Jalesh Cruises' Karnika, and the Empress — the densest homeporting concentration India has ever seen.

The Empress already operates regular itineraries connecting Mumbai with Goa, Lakshadweep, Kochi and Chennai. The Cordelia Sky's induction will likely expand that network and increase sailing frequency, especially during the October-to-April peak season that coincides with the best weather along India's western coast.

## Red Sea rerouting is Mumbai's gain

There is a geopolitical tailwind at work, too. The ongoing Red Sea shipping crisis has forced several cruise operators to reroute vessels away from the Suez Canal corridor. Mumbai, positioned as a natural turnaround point in the Indian Ocean, is picking up repositioned luxury ships that might otherwise have docked in Dubai or Muscat. The Mumbai Port Authority is actively courting these displaced vessels, working with the Ministry of Ports on the broader Cruise Bharat Mission to develop a national cruise terminal network.

The Marina project — a dedicated waterfront facility — is under construction and expected to add berthing capacity specifically designed for large international cruise ships.

## Why NRIs should pay attention

For the Indian American diaspora, Mumbai's cruise moment creates an option that barely existed a few years ago: fly into Mumbai, spend a day in the city, and board a five-night cruise to Goa and Lakshadweep before the family scatters to hometowns across India.

Cordelia's Mumbai-Goa-Lakshadweep itinerary starts around $960 per person for a five-night sailing — a fraction of what Caribbean cruises cost from US ports. The Kadmat Island stop in Lakshadweep, with its turquoise lagoons and virtually empty beaches, is drawing comparisons to the Maldives at a tenth of the price. For NRI families juggling a two-week India trip between wedding functions, temple visits and relatives' houses, a domestic cruise carves out a contained holiday-within-a-holiday that requires zero planning once you board.

The international luxury sailings add another dimension. A 15-day multi-country voyage departing Mumbai in December 2028 — covering Goa, Kochi, Colombo, Phuket, Langkawi, Penang and Singapore — is already on the books, reflecting how operators see Mumbai as a credible embarkation point for extended Indian Ocean itineraries.

## The infrastructure gap remains

Not everything is smooth sailing. Mumbai's existing cruise terminal at Ballard Pier, while functional, lacks the scale and passenger flow design of ports like Singapore or Barcelona. Immigration processing for international voyages can be slow, and ground transportation between the terminal and the city's airports remains uncoordinated. The Marina project should address some of these gaps, but timelines for Indian port infrastructure tend to slip.

For now, though, the trajectory is clear. Mumbai handled more cruise passengers last year than at any point in its history, and the arrival of five global luxury operators signals that the city is no longer a curiosity stop for repositioning ships. It is becoming a destination port — and for NRIs planning their next India trip, a cruise out of Mumbai might be the smartest addition to the itinerary."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Mumbai Is Now a Four-Ship Cruise Hub — and Five Global Luxury Lines Are Booking It for Next Season",
    "subheadline": "Celebrity, Oceania, Crystal, Silversea and Regent have all confirmed FY27 voyages through Mumbai Port, which handled 240,000 passengers last year. Cordelia's ex-Norwegian Sky joins in October.",
    "slug": make_slug("mumbai-cruise-hub-cordelia-sky-luxury-lines-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRI families can now add a five-night Mumbai-Goa-Lakshadweep cruise to their India trip for under $1,000 — a contained holiday that requires zero planning once aboard.",
    "tags": ["travel", "cruise", "mumbai", "goa", "lakshadweep", "cordelia", "luxury"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/mumbai-port-charts-course-as-global-cruise-operators-set-sail-for-india/article71157782.ece"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/india-aligns-sri-lanka-thailand-malaysia-singapore-cruise/"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Mumbai_03-2016_30_Gateway_of_India.jpg/1280px-Mumbai_03-2016_30_Gateway_of_India.jpg",
    "image_caption": "The Gateway of India on Mumbai's waterfront, adjacent to the city's cruise terminal at Ballard Pier",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip(),
}

# ── Article 2: IRCTC Bharat Gaurav Divine East Temple Tour ───────────────────

article2_body = """Indian Railways has a new pitch for the spiritually inclined: an eleven-day, all-inclusive train journey through eastern India's holiest sites, departing Delhi on September 25 and returning on October 5. Bookings are open now.

The Divine East Temple Tour, operated by IRCTC under the Bharat Gaurav banner, stitches together eight destinations across Uttar Pradesh, Odisha, West Bengal and Jharkhand into a single rail-based pilgrimage. It is the latest in a growing catalogue of Bharat Gaurav circuits — purpose-built tourist trains that bundle temples, heritage sites and cultural landmarks into curated, hotel-backed packages that eliminate the logistics of independent travel.

## The route

The train departs from Delhi's Safdarjung Railway Station and heads first to Varanasi for darshan at the Kashi Vishwanath Temple and the evening Ganga Aarti. From there, the journey moves east to Puri — the Jagannath Temple, a mandatory stop for any Odia or pan-Hindu pilgrimage — before branching into Odisha's heritage corridor: the UNESCO-listed Konark Sun Temple, Dhauli Shanti Stupa, the rock-cut Udayagiri and Khandagiri Caves in Bhubaneswar, and the brackish waters of Chilika Lake, Asia's largest coastal lagoon and a birdwatcher's paradise.

The circuit then swings north to Kolkata, covering Victoria Memorial, Dakshineswar Kali Mandir, Kalighat Mandir and Belur Math. A day excursion to Gangasagar — the point where the Ganges meets the Bay of Bengal — includes a holy dip at Sagar Sangam and darshan at Kapil Muni Temple. The final stop before the return to Delhi is Baidyanath Dham in Deoghar, Jharkhand, one of the twelve Jyotirlingas of Lord Shiva.

## What is included

The package covers the train journey, three-star hotel accommodation at each stop, all meals (vegetarian), transfers and sightseeing in AC vehicles, travel insurance, and the services of IRCTC tour managers at every destination. Passengers do not need to arrange anything beyond getting to Safdarjung station on September 25.

Pricing is tiered by train class:

- **AC First Class**: ₹1,13,530 per person
- **AC Second Class**: ₹1,06,145 per person
- **AC Third Class**: ₹91,370 per person

The 3AC option works out to roughly ₹8,300 per day for eleven days of travel, lodging, food, transport and guided sightseeing — competitive with what independent travellers would spend cobbling together this route on their own, minus the coordination headaches.

## Why the Bharat Gaurav model is working

The Bharat Gaurav programme, launched to promote pilgrimage and cultural tourism on Indian Railways' infrastructure, has quietly scaled from a handful of routes to a national network covering south India temple circuits, Jyotirlinga tours across Maharashtra and Gujarat, and now this eastern corridor. The model is simple: IRCTC handles the entire chain — rail berths, hotels, meals, ground transport — so that pilgrims, especially elderly ones, face none of the booking complexity that makes multi-city Indian travel daunting.

The September 25 departure date is well-timed. It falls during the Navratri and Durga Puja window, when eastern India's temples are at their most vibrant and Kolkata transforms into an open-air art gallery of pandals. Travellers on this circuit will experience Odisha and Bengal at their devotional peak.

## The NRI opportunity

For Indian Americans, the Divine East Temple Tour solves a recurring dilemma: how to give parents or in-laws a meaningful spiritual experience in India without personally managing logistics across four states.

The all-inclusive structure — from Delhi departure to Delhi return, with no independent bookings required — makes it an ideal gift for elderly family members who want to visit Varanasi, Puri and the Jyotirlinga circuit but find the multi-city planning overwhelming. NRIs visiting India in late September or early October can time their own trip to overlap with the tour's Delhi departure, see parents off at Safdarjung, and collect them eleven days later with a phone full of temple photos and a suitcase of Odia sweets.

Bookings are available through IRCTC's tourism portal and authorized IRCTC tourism offices. Given that previous Bharat Gaurav departures have sold out weeks in advance, early booking is advisable — especially for the 1AC and 2AC classes, which have limited berths."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "IRCTC's New Temple Train Covers Eight Holy Sites Across Eastern India in Eleven Days — Starting at ₹91,370",
    "subheadline": "The Bharat Gaurav Divine East Temple Tour departs Delhi on September 25, connecting Varanasi, Puri, Konark, Kolkata and Baidyanath Dham in an all-inclusive rail pilgrimage.",
    "slug": make_slug("irctc-bharat-gaurav-divine-east-temple-tour-nri"),
    "category": "travel",
    "vertical": "travel",
    "diaspora_angle": "NRIs can gift this all-inclusive pilgrimage to parents or in-laws — no independent bookings required, Delhi departure and return, timed perfectly with Navratri and Durga Puja.",
    "tags": ["travel", "irctc", "bharat-gaurav", "pilgrimage", "temples", "varanasi", "puri", "konark", "kolkata"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Awaaz", "url": "https://theindianawaaz.com/irctc-introduces-new-tourism-circuit-titled-divine-east-temple-tour-on-its-bharat-gaurav-deluxe-tourist-train/"},
        {"name": "Travel Trade Journal", "url": "https://traveltradejournal.com/irctc-launches-divine-east-temple-tour-on-bharat-gaurav-deluxe-tourist-train/"},
        {"name": "Travel and Tour World", "url": "https://www.travelandtourworld.com/news/article/a-guide-to-the-irctc-bharat-gaurav-temple-circuit/"},
    ]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Konarka_Temple.jpg/1280px-Konarka_Temple.jpg",
    "image_caption": "The 13th-century Konark Sun Temple in Odisha, a UNESCO World Heritage Site and one of eight stops on the Divine East Temple Tour",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip(),
}

# ── Insert ────────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
