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

oci_body = """India has quietly rewritten the rulebook for the document that ties roughly 5.5 million people of Indian origin to their ancestral country — and most of them have not read the fine print. The Overseas Citizen of India card, the lifelong visa that lets the diaspora live, work, study and own property in India without a separate visa each trip, moved to an all-digital "e-OCI" system this spring, with a new fee schedule, a hard passport-update deadline, and a rule that will force some families to make a choice they have been avoiding for years.

For the Indian American community — the largest single block of OCI holders outside India — the changes are less about cost than about compliance. Miss a step and you risk a fine, a flagged record, or a re-entry problem at Delhi or Bengaluru that you only discover at the immigration counter.

## What actually changed

The Ministry of Home Affairs notified the revised framework through the Gazette of India, with the fee structure taking effect April 1 and the system going digital-first from May 1. Four shifts matter most.

**It is now digital-only.** Every application — fresh registration, passport update, re-issue, renunciation — runs end to end through the official portal. Postal submission of documents to Indian missions abroad has been discontinued, and the paper card is now optional rather than mandatory. The e-credential is the record of truth, and the government says approvals should drop from the old six-to-eight-week wait to roughly 15 working days.

**A fresh OCI now costs USD 275** plus a USD 3 welfare surcharge for applications filed abroad, with debit-card payments adding about 1 percent. Re-issue for a change of personal details and renunciation are listed at USD 25; a lost or damaged card replacement is USD 100; a PIO-to-OCI conversion is USD 100.

**The three-month passport rule has teeth.** OCI holders must update their record within three months of receiving a new foreign passport. Miss the window and a USD 25 late penalty applies. Because the new system links the OCI record to passport-data and biometric matching, an out-of-date entry is no longer a paperwork footnote — it is something the system can flag.

**Minors can no longer hold two passports.** Under the amended rules, a child cannot simultaneously hold an Indian passport and a foreign one. Parents applying for an Indian passport for a child must now declare that no foreign passport is held, and surrender any foreign passport first.

There is one piece of genuine relief buried in the overhaul: adults no longer need to re-issue the card every time they renew a passport. A card issued before age 20 needs re-issue only once, on the first passport obtained after turning 20; cards issued after age 20 need no re-issue at all; and the old requirement to re-issue after age 50 is gone.

## Why this lands hard on Indian Americans

The math is unforgiving for the family that has been quietly ignoring its OCI paperwork. Consider the common Bay Area or New Jersey household: two adults who renew US passports on staggered cycles, a teenager who just got a fresh US passport, and a grandparent visiting on a years-old OCI card. Each new US passport now starts a 90-day clock. A family juggling three or four passports on different renewal dates can easily blow a deadline without realizing one exists.

The minor-passport rule is the thornier one. Tens of thousands of US-born children of Indian parents have, over the years, ended up holding both a US passport and a lingering Indian one. India's position is now explicit: pick one. Holding both is a violation the digital system is built to catch in real time — and US naturalization forms, separately, now ask for fuller disclosure of foreign documents including OCI status, which means a sloppy record on one side can surface on the other.

## What to do before your next trip home

Pull up your OCI record and check the passport number on file against the passport you actually travel on. If they do not match and you have renewed within the last three months, update now and avoid the penalty; if it has been longer, update anyway and budget for the USD 25 fee. Families with a child holding two passports should sort the conflict before booking a ticket, not at the airport. And anyone planning a fresh application should know the queue is shorter now — 15 working days is realistic — but the USD 275 entry fee is not coming back down.

The OCI was always pitched as the diaspora's frictionless bridge to India. It still is. It just now comes with a clock, a portal, and a system that remembers."""

jal_body = """Japan Airlines has put Bengaluru on its long-haul map, announcing a new daily service to the southern Indian city as part of a fiscal-2026 expansion that also adds daily flights to San Diego and pushes more of the carrier's Airbus A350 fleet onto international routes. For the Indian American traveler — especially the large Kannada- and Telugu-speaking tech diaspora on the US West Coast — the announcement reshapes one of the more awkward journeys in the network: getting between Northern California's tech corridor and India's.

## A second front door to South India

Until now, the nonstop story from the US to Bengaluru has been thin. Air India flies San Francisco–Bengaluru, but options have been limited and pricey, and most travelers from Seattle, San Diego, Los Angeles or the smaller West Coast tech hubs route through Delhi, Dubai or a European hub, eating a connection and several hours. Japan Airlines' move creates a clean alternative: fly to Tokyo — where JAL's Haneda and Narita hubs already connect deeply into the US West Coast — and pick up a daily nonstop down to Bengaluru.

The carrier framed the route as a bet on Bengaluru's pull as one of India's fastest-growing technology and business centers, deepening corporate ties between Japanese industry and India's innovation economy. The same logic runs in reverse for the diaspora: Bengaluru is the home airport for a huge share of the Indian engineers, founders and families clustered around the Bay Area, Seattle and San Diego.

## The A350 is the quiet headline

The aircraft matters as much as the route. JAL is steadily shifting its long-haul flying to the Airbus A350, prized for quieter cabins, better cabin-air pressurization and humidity, and lower fuel burn. The airline is pairing the fleet move with onboard upgrades — enhanced seating, improved dining and JAL's signature service in premium cabins, with better seats and entertainment in economy too.

For a 20-plus-hour door-to-door journey broken in Tokyo, that combination — a modern jet on the long Pacific leg and a fresh nonstop into Bengaluru — is a materially more comfortable trip than a Gulf or European double-connection.

## Why San Diego is in the same announcement

JAL's decision to add daily San Diego service alongside Bengaluru is not a coincidence for the diaspora reader. San Diego's biotech, defense and tech cluster has a sizable Indian-origin workforce that has historically had no easy path home — the city is a connection-heavy origin for India travel. A daily JAL flight to Tokyo turns San Diego into a one-stop origin for Bengaluru via Haneda, opening a route that effectively did not exist as a clean itinerary before.

That makes the two new routes a single corridor when you read them together: San Diego (and the broader West Coast) to Tokyo to Bengaluru, on one airline, with one baggage check and a familiar hub in the middle.

## The practical read for NRIs

A few things to weigh before this changes your booking habits. First, schedule alignment is everything on a connecting itinerary — the value of the Bengaluru nonstop depends on how tightly JAL times it against its US West Coast arrivals into Tokyo, so check the through-fares rather than assuming a smooth same-day connection. Second, JAL is a Oneworld carrier, which matters for travelers banking miles with American Airlines or British Airways and for those who value Oneworld lounge access on a long layover. Third, a Tokyo connection is one of the more pleasant places to break a trans-Pacific haul, with strong onward options if you want to tack on a Japan stopover.

For years the West Coast-to-South-India journey has been the diaspora's least-loved long haul — too far for a comfortable single connection, too important to skip. A daily Bengaluru nonstop from Tokyo, fed by JAL's West Coast network and flown on its newest jets, is the most credible fix the market has offered in a while. The question now is price and timing; the geography, at last, finally works."""

lanka_body = """Sri Lanka has renewed its fee-free entry scheme for Indian passport holders, keeping one of the easiest international trips from India effectively free of visa charges. The island's Immigration Department confirmed the extension of the free Electronic Travel Authorisation for Indians and six other priority markets, locking in a policy that has helped make Sri Lanka the most accessible beach-and-heritage getaway in India's neighborhood. For the Indian American family planning a trip that pairs a visit home with a short regional escape, it is a quietly useful piece of news.

## What the policy actually is

Indians traveling to Sri Lanka still need to apply online for an ETA before departure through the official Sri Lankan immigration portal — but the application fee has been waived. The authorisation permits a 30-day stay with a double-entry facility inside that window, which is the part that matters for itinerary builders: you can enter, dip into a neighboring country or hop between Sri Lankan regions, and re-enter on the same authorisation.

The free-ETA framework, first launched as a six-month pilot in early 2023 for seven markets — India, China, Indonesia, Russia, Thailand, Malaysia and Japan — has been repeatedly extended and, since late May, widened to a 40-country list that now also covers the US, UK, Canada, Australia, the EU and the Gulf states. India remains the anchor: it was the single largest source market this year, accounting for roughly a quarter of all arrivals.

## Why this is an NRI story, not just a tourism story

For the diaspora, Sri Lanka's appeal is geographic and logistical. A trip home to India is long and expensive; bolting on a separate long-haul holiday is often not worth it. Sri Lanka solves that. It is a short hop from South India — Chennai, Bengaluru and Kochi all have quick connections to Colombo — which makes it the natural add-on to a trip that is already happening. A family flying in from New Jersey or the Bay Area for a wedding in Chennai can extend the trip with a few days in Galle or the hill country without a fresh visa run or a fee.

The double-entry feature is the underrated detail for these travelers. It means a diaspora visitor can use Colombo as a base, slot Sri Lanka between India legs, or split a trip across the island and the mainland without burning the authorisation.

## What is actually worth the detour

Sri Lanka packs an outsized variety into a small island. The cultural triangle anchored by Sigiriya — the fifth-century rock fortress that is the country's signature image — sits within a few hours of the ancient capitals of Anuradhapura and Polonnaruwa. The hill country around Kandy and Ella delivers tea estates and the much-photographed Nine Arch Bridge, reachable on one of the most scenic train rides in Asia. The southern coast — Galle's Dutch-era fort, the beaches of Mirissa and Unawatuna — is the easy beach payoff, and the national parks at Yala and Udawalawe put leopards and elephants within a day trip.

For NRI families traveling with elders or children, the low-friction entry, short flight times from South India, shared cultural touchpoints and English-friendly tourism infrastructure make it one of the gentlest international trips to organize.

## The fine print

A few practical notes. Apply through the official government portal, not a third-party site — the scheme's whole value is that the ETA is free, and unofficial sites layer on service charges that defeat the point. Carry a passport valid for at least six months, and keep return tickets and accommodation details handy for the entry counter. The waiver is being run as a defined-term program that the government reviews against tourism gains, so treat it as a window rather than a permanent fixture and confirm the rules close to your travel date.

The broader picture is a region competing hard for Indian travelers — and Sri Lanka, after a brutal economic stretch, has decided that the cheapest way to win them is to stop charging at the door. For the diaspora, that turns the island from a someday trip into an easy extension of the trip you are already taking."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Rewrote the OCI Rulebook — and Most of the Diaspora Hasn't Read the Fine Print",
        "subheadline": "An all-digital e-OCI system, a USD 275 fee, a three-month passport-update clock, and a new ban on minors holding two passports reshape the diaspora's lifelong link to India.",
        "slug": make_slug("oci-2026-overhaul-e-oci-digital-fee-passport-deadline-minor-nri"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "OCI is the document that lets 5.5 million people of Indian origin live, work and travel freely in India — and the 2026 overhaul adds deadlines and a minor-passport rule that can trip up Indian American families juggling multiple passports.",
        "tags": ["travel", "visa", "oci", "immigration", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wego Travel Blog — India Introduces e-OCI", "url": "https://blog.wego.com/e-oci-india/"},
            {"name": "VisaVerge — India OCI Rules 2026", "url": "https://www.visaverge.com/india/india-oci-rules-2026-new-fees-and-passport-update-deadlines/"},
            {"name": "Fragomen — OCI Cardholder Processes Streamlined", "url": "https://www.fragomen.com/insights/overseas-citizen-of-india-cardholders-processes-streamlined.html"},
            {"name": "VG Immigration Services — 6 New OCI Rules", "url": "https://vgis.ca/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Indian_Passport_01.jpg/1280px-Indian_Passport_01.jpg",
        "image_caption": "An Indian passport, the document that anchors Overseas Citizen of India status for the diaspora.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": oci_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Japan Airlines Is Putting Bengaluru on Its Map — and Fixing the West Coast's Worst Trip Home",
        "subheadline": "A new daily JAL service to Bengaluru, paired with a fresh San Diego route and a growing A350 fleet, turns Tokyo into a clean one-stop bridge between the US West Coast and South India.",
        "slug": make_slug("japan-airlines-bengaluru-san-diego-a350-west-coast-nri-route"),
        "category": "travel",
        "vertical": "aviation",
        "diaspora_angle": "The West-Coast-to-South-India journey has long been the diaspora's least-loved long haul; JAL's new daily Bengaluru nonstop from Tokyo, fed by its US West Coast network, finally gives Bay Area, Seattle and San Diego NRIs a comfortable one-stop route home.",
        "tags": ["travel", "airlines", "japan airlines", "bengaluru", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World — Japan Airlines New Daily Flights to Bengaluru and San Diego", "url": "https://www.travelandtourworld.com/news/article/iacitmg4evqt/"},
            {"name": "Air India / route context — Aviation Week", "url": "https://aviationweek.com/air-transport/air-india-further-expand-us-network"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/Japan_Airlines_A350-1000_JA01WJ.jpg/1280px-Japan_Airlines_A350-1000_JA01WJ.jpg",
        "image_caption": "A Japan Airlines Airbus A350, the aircraft type the carrier is shifting onto its long-haul network.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": jal_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sri Lanka Keeps the Door Free for Indians — and It's the Easiest Add-On to a Trip Home",
        "subheadline": "The island has renewed fee-free ETA entry for Indian passport holders, with a 30-day stay and double-entry facility that make it the simplest regional escape to bolt onto a visit to South India.",
        "slug": make_slug("sri-lanka-free-eta-visa-indians-renewed-double-entry-nri-add-on"),
        "category": "travel",
        "vertical": "visa-policy",
        "diaspora_angle": "Fee-free, 30-day, double-entry access from a short hop off South India turns Sri Lanka from a someday trip into an easy extension of the India trip NRI families are already taking.",
        "tags": ["travel", "visa", "sri lanka", "nri", "destinations"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Sri Lanka free visa entry for India and 6 countries", "url": "https://theindianeye.com/"},
            {"name": "Sri Lanka Immigration Department — Extending free visa", "url": "https://www.immigration.gov.lk/"},
            {"name": "Freaking Nomads — Sri Lanka fee-free visas for 40 countries 2026", "url": "https://freakingnomads.com/sri-lanka-free-visa/"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Sigiriya_Sri_Lanka_L%C3%B6wenfelsen.jpg/1280px-Sigiriya_Sri_Lanka_L%C3%B6wenfelsen.jpg",
        "image_caption": "Sigiriya, the fifth-century rock fortress at the heart of Sri Lanka's cultural triangle.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": lanka_body
    }
]

# word-count sanity
for art in articles:
    wc = len(art["body"].split())
    print(f"  {art['slug']}: {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
