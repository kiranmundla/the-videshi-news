#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-06-05 02:00 UTC run"""
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
    # ── Article 1: Germany Transit Visa ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Germany Scraps Transit Visa for Indians — and Europe Just Got Easier to Reach",
        "subheadline": "Indian passport holders can now transit through Frankfurt and Munich without a separate visa, removing a decades-old hurdle for millions of travellers connecting through Europe's busiest hubs.",
        "slug": make_slug("germany-scraps-transit-visa-indians-europe-easier"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs booking connecting flights through Frankfurt or Munich to European destinations — or routing family visitors through Germany — no longer need to factor in transit visa costs, processing times, or appointment slots. For the estimated 250,000 Indian students in Germany and the broader diaspora across Europe, this also simplifies visits from relatives back home.",
        "tags": ["travel", "visa", "germany", "europe", "lufthansa", "transit"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/news/india-welcomes-germanys-visa-free-transit-for-indian-travellers-20260602230055"},
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/international/germany-removes-airport-transit-visa-rule-for-indians-from-june-2026"},
            {"name": "Aviation A2Z", "url": "https://www.aviationa2z.com/lufthansa-boosts-india-connectivity-after-germany-removes-transit-visa-rule/"},
            {"name": "German Embassy New Delhi", "url": "https://india.diplo.de/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/202201_Atrium_and_Transit_Re-Security_Area_at_Frankfurt_Airport_Terminal_1_Concourse_AZ.jpg/1280px-202201_Atrium_and_Transit_Re-Security_Area_at_Frankfurt_Airport_Terminal_1_Concourse_AZ.jpg",
        "image_caption": "The transit re-security area at Frankfurt Airport Terminal 1",
        "image_attribution": "Wikimedia Commons",
        "body": """Germany has officially eliminated the airport transit visa requirement for Indian nationals, effective June 3, 2026. The change, published in the Bundesgesetzblatt (Federal Law Gazette) on June 2, means Indian passport holders transiting through German airports en route to a third country no longer need a separate transit visa — a procedural relic that had persisted for decades.

The Ministry of External Affairs confirmed the move in a statement, noting that India "welcomes the operationalisation by Germany of the announcement waiving requirement of transit visa for Indian nationals transiting through Germany, exclusively by air." MEA spokesperson Randhir Jaiswal traced the decision to discussions between Prime Minister Narendra Modi and German Chancellor Friedrich Merz during Merz's visit to India in January 2026.

## What actually changes

Until now, an Indian traveller connecting through Frankfurt or Munich to, say, Barcelona or Athens needed to secure an airport transit visa even if they never left the terminal. The process required an appointment at a German consulate, supporting documents, and a fee — all for the privilege of sitting in an airside lounge for two hours.

That barrier is now gone. Indians holding a valid ticket onward to a non-German destination can transit through any German airport without additional paperwork, provided they meet the entry requirements of their final destination. The change applies to air transit only and does not affect entry visa requirements for those planning to leave the airport or stay in Germany.

## Why this matters for NRIs

For Indian Americans and the broader diaspora, Germany's two main hubs — Frankfurt and Munich — are among the most common connecting points for flights between the US and the Indian subcontinent. Lufthansa Group alone operates more than 70 weekly flights between India and Europe, and Frankfurt Airport handled over 4.5 million Indian-origin passengers in connecting traffic last year.

The timing is deliberate. Lufthansa is simultaneously expanding its India operations: deploying its new Allegris premium cabin on Boeing 787-9 services from Delhi and Hyderabad, boosting A380 operations between Mumbai and Munich, and its subsidiary SWISS is launching a first-ever nonstop between Bengaluru and Zurich for Winter 2026. Germany is clearly betting that removing friction at its airports will capture more of the India-Europe connecting traffic that currently flows through Dubai, Doha, and Istanbul.

For NRIs routing parents or in-laws through Europe, the practical impact is immediate. Booking a connecting itinerary through Frankfurt no longer triggers a transit visa scramble — a relief for elderly travellers who found the consulate process especially burdensome.

## The bigger picture

Germany's move follows a broader pattern of countries reducing visa barriers for Indian travellers. Malaysia extended its visa-free arrangement through December 2026, Sri Lanka recently dropped visa fees for 40 countries including India, and the Philippines now offers a two-tier visa-free scheme for Indian passport holders with valid Western visas.

India filed 1.15 million Schengen visa applications in 2025, making it one of the largest source markets for European travel. Germany's transit visa waiver, while narrower than a full Schengen exemption, addresses one of the most common friction points in that pipeline. For a country that has positioned India as its largest intercontinental aviation market in Asia-Pacific, the calculus is straightforward: fewer barriers mean more bookings.

The waiver also strengthens Germany's hand against Gulf carriers that have long offered visa-free transits as a competitive advantage. When connecting through Dubai or Doha required zero additional paperwork while Frankfurt demanded a consulate visit, the choice was obvious. That asymmetry has now been partially corrected.

NRIs planning summer travel through Europe should note that the change is effective immediately and requires no application or registration — just a valid passport, a confirmed onward ticket, and compliance with the destination country's entry rules."""
    },

    # ── Article 2: Srinagar Airport Disruptions ──────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Srinagar Airport Will Shut Two Days a Week Starting July — and a Full Fortnight in October",
        "subheadline": "Runway maintenance by the Indian Air Force will close Kashmir's only major airport every Monday and Tuesday through September, with a complete 16-day shutdown planned for early October — right when NRI families typically book autumn trips to the Valley.",
        "slug": make_slug("srinagar-airport-shutdown-july-october-kashmir-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs who book Kashmir trips around Durga Puja, Dussehra, or the autumn foliage season face a near-total air blackout in early October. Those planning summer visits need to avoid Monday-Tuesday arrivals or build in road alternatives via Jammu. Flight prices on remaining days will likely spike as capacity drops by roughly 30%.",
        "tags": ["travel", "kashmir", "srinagar", "airport", "flights", "disruption"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Traveller", "url": "https://www.outlooktraveller.com/destinations/india/srinagar-airport-to-remain-shut-twice-a-week-from-july-2026-amid-runway-works"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/logistics/srinagar-airport-announces-partial-runway-closure-from-july-2026-full-shutdown-from-october-1/article69644127.ece"},
            {"name": "The Kashmir Horizon", "url": "https://thekashmirhorizon.com/srinagar-airport-to-shut-for-15-days-from-oct-1/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/headlines/3364818-srinagar-airport-runway-maintenance-set-to-affect-flight-operations"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Srinagar_%28SXR%29_airport_-_vrvvkbjk2k23pxl_%281%29.jpg/1280px-Srinagar_%28SXR%29_airport_-_vrvvkbjk2k23pxl_%281%29.jpg",
        "image_caption": "Srinagar International Airport terminal building in Kashmir",
        "image_attribution": "Wikimedia Commons",
        "body": """Srinagar International Airport, the sole major air gateway to the Kashmir Valley, is heading into its most disruptive period in years. The Indian Air Force has laid out a phased runway maintenance plan that will shut the airport two days every week from July through September and close it entirely for 16 days in early October — squarely overlapping with one of Kashmir's peak tourism windows.

The airport authority confirmed the schedule in an advisory posted on X, though it noted the plan is still awaiting formal approval. The details are specific enough to warrant immediate attention from anyone booking Kashmir travel this summer or autumn.

## The maintenance schedule

**July 1 to September 30**: The runway will be unavailable every Monday and Tuesday, effectively cutting the operating week to five days. Airlines will need to compress their schedules into Wednesday through Sunday, which means fewer total flights and higher load factors on remaining days.

**Until July 31**: A NOTAM (Notice to Airmen) restricts operations to a fixed window between 8 AM and 5 PM. No early morning departures, no late evening arrivals. This is already in effect due to ongoing runway length restrictions that have imposed payload limitations on aircraft.

**October 1 to October 16**: A proposed complete shutdown of all runway operations for 16 days. This is the most consequential phase — it coincides with Durga Puja, one of the heaviest domestic travel periods of the year, and the start of Kashmir's spectacular autumn foliage season.

## Why NRIs should pay attention now

Kashmir has become one of the most popular homecoming destinations for the Indian diaspora, particularly families who combine a Delhi visit with a short hop up to Srinagar for houseboats on Dal Lake, Gulmarg's meadows, or the Mughal gardens. The autumn window — late September through mid-October — is considered the best time to visit, with the chinar trees turning gold and red against the Himalayan backdrop.

The October shutdown demolishes that window entirely. An NRI family planning an October 5 arrival in Srinagar will need to rethink from scratch. The alternatives are limited: a 300-kilometre road journey from Jammu (8-10 hours through the mountains on the Jammu-Srinagar highway, itself prone to landslides during the monsoon tail), or rescheduling to late October at the earliest.

Even the summer months are affected. Monday and Tuesday closures mean that the typical long-weekend pattern — fly in Thursday or Friday, fly out Monday or Tuesday — breaks down. Travellers will need to depart by Sunday or extend through Wednesday.

## What this means for fares and availability

When you remove two operating days from a week, you don't just lose 28% of flights. You compress demand into fewer slots, which drives both fares and load factors sharply higher. Airlines serving Srinagar — primarily IndiGo, Air India, SpiceJet, and GoFirst — have not yet announced schedule adjustments, but fare spikes on remaining operating days are all but certain.

Hoteliers and tour operators in the Valley are already bracing for impact. The Kashmir Horizon reported that tourism stakeholders fear cancellations and financial losses, particularly from the lucrative Bengali tourist segment that books heavily around Durga Puja.

## Practical advice

Book early and book flexible. If you're set on a summer Kashmir trip, anchor your flights on Wednesday through Saturday arrivals and avoid building an itinerary that depends on Monday or Tuesday operations. For autumn travel, treat the October 1-16 window as a hard blackout and plan accordingly — either arrive before September 28 or after October 17.

Consider the road. The Jammu-Srinagar highway, despite its reputation, has improved significantly with the completion of several tunnel projects. For travellers who can handle the drive, flying into Jammu and driving up offers a reliable backup.

Stay connected to official channels. The airport authority has emphasised that the schedule is still in the planning phase, and formal approval with detailed timelines will follow. Follow Srinagar Airport's official X account and monitor airline schedule updates directly rather than relying on aggregator apps that may lag behind changes."""
    },

    # ── Article 3: The Evren, Goa — Bollywood-Backed Luxury ─────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sanjay Dutt's New Goa Hotel Joins the World's Most Exclusive Club — and NRIs Are the Target Market",
        "subheadline": "The Evren in Vagator has been inducted into Small Luxury Hotels of the World before even fully opening, with a chef who cooked at Eleven Madison Park and rooms starting at $250 a night. Goa's boutique hotel scene is growing up.",
        "slug": make_slug("sanjay-dutt-evren-goa-slh-luxury-hotel-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Goa is the default holiday destination for NRIs visiting India, but the accommodation options have long lagged behind the international standards diaspora travellers are used to. The Evren represents a new wave of globally benchmarked boutique properties that give NRI families a reason to extend their Goa stays beyond the usual three-night stopover.",
        "tags": ["travel", "goa", "hotel", "luxury", "sanjay-dutt", "boutique"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Restaurant India", "url": "https://www.restaurantindia.in/news/sanjay-dutt-and-anant-hospitality-launch-luxury-hotel-the-evren-in-goa.nid-24652.html"},
            {"name": "Small Luxury Hotels of the World", "url": "https://www.slh.com/hotels/the-evren/"},
            {"name": "TripAdvisor", "url": "https://www.tripadvisor.co.uk/Hotel_Review-g303877-d26553131-Reviews-The_Evren-Vagator_Bardez_North_Goa_District_Goa.html"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Vagator_Beach%2C_Goa%2C_India%2C_Palms.jpg/1280px-Vagator_Beach%2C_Goa%2C_India%2C_Palms.jpg",
        "image_caption": "Vagator Beach in North Goa, walking distance from The Evren hotel",
        "image_attribution": "Wikimedia Commons",
        "body": """A new luxury hotel in North Goa has managed something unusual: it earned a spot in the Small Luxury Hotels of the World (SLH) collection before it even fully opened. The Evren, located on Ozran Beach Road in Vagator, is backed by a group that includes actor-entrepreneur Sanjay Dutt and a team of hospitality entrepreneurs who have spent years building some of India's most recognizable nightlife and dining brands.

The property represents a broader shift in Goa's hospitality landscape — from the backpacker-and-beach-shack economy that defined the state for decades to a tier of boutique luxury that can genuinely compete with Bali, Tulum, or the Amalfi Coast.

## What The Evren actually is

Developed by Anant Hospitality — co-founded by Harkaran Chawla, Angad Singh, Kunal Patel, and Suved Lohia alongside Dutt — The Evren sits a short walk from Ozran Beach, the quieter, cliff-backed stretch south of Vagator's main beach. The property features suites with canopied wooden beds and wrought-iron balconies, a central courtyard pool with a swim-up bar, and a spa rooted in traditional Kansa rituals with views over Salagaon Hill.

The food programme is the headline act. Chef Prachi Mehta, appointed as culinary consultant, brings a resume that spans London's The Wolseley, Copenhagen's Michelin-starred 108, and a pop-up stint at New York's Eleven Madison Park. Her menu at Nines, the hotel's flagship restaurant, applies European technique to Indian flavours — a deliberate pitch to well-travelled diners who want global standards without losing the Goan context.

The food and beverage strategy is led by Suved Lohia, whose portfolio includes One8 Commune (Virat Kohli's restaurant chain), Neuma, Milagro, and Palacio. The Evren also houses Mila, an all-day dining space, and Suenos de Café, a specialty coffee and cocktail lounge. A speakeasy-style bar rounds out the nightlife offering.

## The SLH stamp matters

Small Luxury Hotels of the World is a curated collection of about 520 independent hotels across 90 countries. Membership requires meeting detailed quality standards across service, design, dining, and guest experience. For a newly launched Indian property to earn admission before its formal opening suggests either exceptional execution or exceptional connections — probably both.

For the NRI traveller, SLH membership carries practical weight. It integrates with Hyatt's loyalty programme (World of Hyatt), meaning points earned at any Hyatt property worldwide can be redeemed at The Evren. For diaspora families who accumulate hotel points through US business travel, this creates a direct pipeline between their American loyalty accounts and a Goa beach holiday.

Rooms start at approximately $250 per night — expensive by Goa standards, where a perfectly decent beachfront resort can be had for $80, but competitive with comparable boutique properties in Southeast Asia and well below the $400-600 range that SLH hotels typically command in Europe.

## Goa's quiet luxury transformation

The Evren is not an isolated play. Goa has seen a steady influx of premium hospitality investment over the past two years. The Atmosphere Core group, a Maldives-based operator known for its overwater villa resorts, recently announced a 51-villa property in Goa as part of an aggressive India expansion that includes properties in Coorg, Kannur, and Kolkata. ITC Hotels completed its acquisition of the Zuri Kumarakom resort, and The Leela has announced expansion plans that include new properties in Srinagar, Ayodhya, and Dubai.

What's driving the shift is partly demand-side: India's domestic luxury travel market has exploded post-pandemic, and NRIs who previously dismissed Goa accommodation as underwhelming are finding properties that match what they experience in Phuket or Positano. It's also supply-side: developers and operators have recognised that the margins on a 30-suite boutique hotel with a celebrity chef far exceed those on a 200-room package-tour property.

## For NRI travellers

If Goa has been a two-or-three-night stopover on your India trip — sandwiched between Delhi obligations and a Rajasthan circuit — properties like The Evren are designed to change that calculus. The combination of international culinary talent, design-forward spaces, and a location that actually feels like a destination rather than a transit point makes a compelling case for extending the stay.

The Evren is located at 246/2, Ozran Beach Road, Vagator, Goa 403509. It is bookable directly through the SLH website, through Hyatt's platform using World of Hyatt points, or through standard OTAs. The property is a 90-minute drive from Goa's Dabolim Airport or 45 minutes from the newer Manohar International Airport at Mopa."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
