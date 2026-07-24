#!/usr/bin/env python3
"""Travel writer for The Videshi — 2026-07-01 15:00 PT run."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ── Article 1: Navi Mumbai Airport Goes International ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Navi Mumbai Airport Opens for International Flights on July 15 — and NRIs Get a Second Gateway Home",
        "subheadline": "India's newest greenfield airport will launch Gulf routes with Air India Express and IndiGo, giving the Mumbai metro region its first real alternative to the congested Chhatrapati Shivaji terminal.",
        "slug": make_slug("navi-mumbai-airport-international-flights-july-nri"),
        "category": "travel",
        "vertical": "aviation",
        "is_editorial": False,
        "diaspora_angle": "NRIs flying to Mumbai and Pune now have a second, less chaotic airport option — with international departures starting just two weeks from now.",
        "tags": ["travel", "airlines", "airports", "mumbai", "navi-mumbai", "adani", "aviation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/navi-mumbai-airport-to-launch-international-operations-on-july-15"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/economy/logistics/navi-mumbai-airport-launch-international-flights-from-july-15/article69107842.ece"},
            {"name": "ANI via LatestLY", "url": "https://www.latestly.com/agency-news/business-news-navi-mumbai-international-airport-to-launch-international-flights-from-july-15-says-nmia-chairman-6788109.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Navi_Mumbai_Airport_%2896252%29.jpg/1280px-Navi_Mumbai_Airport_%2896252%29.jpg",
        "image_caption": "The Navi Mumbai International Airport terminal, which began domestic operations in December 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Mumbai's airport problem has been an open secret for decades. Chhatrapati Shivaji Maharaj International Airport — wedged between slums, a golf course, and a national park — processes over 50 million passengers a year through facilities that were never designed for that volume. For NRIs arriving on a red-eye from JFK or SFO, the experience is familiar: crawling immigration queues, luggage carousels that test your patience, and a taxi line that stretches into the humid night.

That bottleneck is about to get some relief.

## The Launch

Navi Mumbai International Airport (NMIA) will commence international passenger flights on July 15, according to NMIA Chairman Captain BVJK Sharma. The Adani Group-owned airport — India's largest greenfield aviation project — launched domestic operations last Christmas and now handles roughly 20,000 passengers daily across 149 flights to 46 Indian cities.

The international debut will start with short-haul Gulf routes. Air India Express and IndiGo have both filed route plans, with Abu Dhabi and Dubai expected among the first destinations. International cargo freighter operations will begin simultaneously, with a target of 18 weekly freight flights.

The launch was originally planned for late March, timed to the 2026 summer schedule. But the West Asia conflict and resulting airspace disruptions pushed the date back by nearly four months.

## Why It Matters for NRIs

The real significance here isn't the Gulf routes themselves — it's the precedent. Navi Mumbai's terminal is being positioned as a future international hub for the entire Mumbai Metropolitan Region, which is home to more than 25 million people.

For the Indian American diaspora, the airport offers three immediate advantages:

**Less congestion.** CSMIA is India's second-busiest airport and regularly ranks among the most delayed internationally. Having a second option — especially one built from scratch with modern infrastructure — means fewer missed connections and shorter ground times.

**Better access to Pune and south Mumbai suburbs.** Navi Mumbai sits closer to Pune (India's IT hub) and the fast-growing suburbs of Panvel, Kharghar, and Vashi. NRIs with family in Pune or Navi Mumbai currently face a 2-3 hour transfer from CSMIA. The new airport cuts that to under 30 minutes.

**Expansion is already baked in.** The current terminal handles 20 million passengers annually. But NMIA has scrapped its original Phase 2 plan for a 30-million-passenger terminal and is instead designing one for 50 million — a signal that the Adani Group sees international traffic scaling fast. By year-end, daily passenger volume is expected to hit 50,000 with 380 flight movements.

## The Bigger Picture

NMIA joins a small but growing club of Indian greenfield airports — alongside Hyderabad's Rajiv Gandhi and Bengaluru's Kempegowda — that were purpose-built for the scale modern Indian aviation demands. Unlike CSMIA, it has room to expand without the political and geographic constraints that have stunted Mumbai's primary airport for years.

Customs clearance for international operations is being fast-tracked. The Central Board of Indirect Taxes and Customs reviewed the airport's readiness on June 16, and the final trade notice was expected around July 5. Both Air India Express and IndiGo have confirmed international route filings with the airport.

For NRIs who have watched Mumbai's infrastructure promises come and go, the airport's trajectory so far has been unusually disciplined: domestic operations launched on schedule in December 2025, daily flight counts ramped from 46 to 149 within six months, and the international timeline — despite a geopolitical delay — is being met within the same calendar year.

## What to Watch

The initial Gulf routes are a starting point, not the destination. Long-haul nonstop service to North America or Europe from Navi Mumbai would require larger aircraft and bilateral slot agreements that are still years away. But for NRIs transiting through Dubai or Abu Dhabi — as many do — having a second Mumbai airport on the itinerary means more routing options and, eventually, more competitive fares.

If you're booking a trip home this summer, CSMIA remains the primary gateway. But keep an eye on July 15. Navi Mumbai is no longer a construction site. It's an airport — and soon, an international one."""
    },

    # ── Article 2: TSA PreCheck Touchless ID + Google Wallet ──
    {
        "id": str(uuid.uuid4()),
        "headline": "TSA PreCheck Goes Touchless at 65 Airports — and NRIs with Global Entry Should Set It Up Now",
        "subheadline": "A new Google Wallet integration lets TSA PreCheck members breeze through security with a facial scan and no physical ID. Indian citizens already enrolled in Global Entry get the perk automatically.",
        "slug": make_slug("tsa-precheck-touchless-google-wallet-nri-global-entry"),
        "category": "travel",
        "vertical": "aviation",
        "is_editorial": False,
        "diaspora_angle": "Indian citizens have been eligible for Global Entry since 2017, which includes TSA PreCheck — this upgrade makes the airport experience even faster for enrolled NRIs.",
        "tags": ["travel", "tsa", "global-entry", "airports", "google", "nri", "security"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TSA Official Announcement", "url": "https://www.tsa.gov/news/press/releases/2026/06/24/tsa-google-wallet-launch-new-tsa-precheck-touchless-id-opt"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/tsa-precheck-touchless-id-expansion-google-wallet/"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/news/tsa-precheck-touchless-id-google-wallet/"},
            {"name": "CBP Global Entry for Indian Citizens", "url": "https://www.cbp.gov/travel/trusted-traveler-programs/global-entry/international-arrangements/india"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/15068317/pexels-photo-15068317.jpeg",
        "image_caption": "A traveler using a smartphone at an airport terminal",
        "image_attribution": "Pexels",
        "body": """If you fly frequently between the US and India, you've probably memorised the drill: passport out, boarding pass ready, shoes off if you're in the wrong line, laptop out, jacket off, belt off. It's a ritual that hasn't fundamentally changed in two decades.

That just changed — at least for TSA PreCheck members.

## What Happened

On June 24, the Transportation Security Administration announced a partnership with Google Wallet to launch TSA PreCheck Touchless ID at 65 airports and across more than 100 airlines. The system uses facial comparison technology to verify your identity in dedicated security lanes — no physical passport, no boarding pass printout, no wallet fumble. You walk up, look into a camera, and walk through.

The Google Wallet integration is the key upgrade. Previously, setting up Touchless ID required manually adding your Known Traveler Number and passport details into each airline's app separately — a tedious process that kept adoption low. Now, Google Wallet handles the opt-in automatically once you check in for your flight and add your boarding pass to your wallet.

## How It Works

The setup takes about two minutes:

1. Check in for your flight with a participating airline and add your boarding pass to Google Wallet.
2. If you have an eligible digital ID in Google Wallet, you'll see a "Get Started" button that redirects to TSA's consent page.
3. Authorize sharing your digital ID and boarding pass with TSA.
4. TSA confirms enrollment and sends a confirmation code to Google Wallet.
5. At the airport, walk into the dedicated Touchless ID lane — the system matches your face to your records and you're through.

TSA says the system does not retain facial images after identity verification. The comparison happens at the checkpoint and the data is deleted afterward. TSA also emphasizes that participation is entirely voluntary — you can always use the standard PreCheck lane with physical documents.

## The NRI Angle: Global Entry = Automatic Access

Here's why this matters specifically to the Indian American community: India has been a Global Entry-eligible country since 2017. Indian citizens with valid US visas can apply for Global Entry, which costs $100 for five years and includes TSA PreCheck as a built-in benefit.

For NRIs who already have Global Entry — and many frequent India-US flyers do — this upgrade is free and automatic. Your Global Entry membership number doubles as your Known Traveler Number, and adding it to your airline profile is all that's needed to unlock Touchless ID through Google Wallet.

The practical impact is significant. Major NRI travel hubs like SFO, JFK, Newark, LAX, Chicago O'Hare, Dallas-Fort Worth, and Houston are all Touchless ID airports. If you're connecting through any of these on your way to or from India, the new system means one less bottleneck.

## For Those Without Global Entry

If you haven't enrolled yet, the process for Indian citizens involves three steps: applying through the CBP Trusted Traveler Program website, submitting a background verification request through India's Passport Seva Portal (with an in-person visit to a PSK in India), and completing an interview at a US Global Entry Enrollment Center — typically at a major airport.

The total cost is $100 (CBP) plus ₹500 (India-side verification). Enrollment centers at airports like SFO, JFK, and O'Hare often have walk-in availability during international arrivals, making it possible to complete the interview on your next trip.

## The Bigger Shift

TSA's push toward biometric verification isn't happening in isolation. India's own airports are increasingly adopting DigiYatra, a facial recognition system for domestic travel that lets you move from check-in to boarding without showing documents. The US system works on a similar principle — verify once, move freely.

For NRIs toggling between Indian and American airports, the convergence is convenient: facial verification at departure in Delhi, touchless screening at arrival in San Francisco. The paper-and-plastic airport experience is quietly becoming optional.

The Google Wallet partnership currently supports Android devices. Apple Wallet integration has not been announced, though TSA says additional digital wallet partners are "being explored." For now, iPhone users can still opt in through individual airline apps.

If you fly through US airports more than a couple of times a year, this is worth the two minutes it takes to set up. The dedicated Touchless ID lanes are consistently shorter than even the standard PreCheck lines — and for anyone who has stood in the regular security queue at JFK Terminal 4 during peak hours, that alone justifies the effort."""
    },

    # ── Article 3: Air India Maharaja Lounge at SFO ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India's New Maharaja Lounge at SFO Is Its First International Signature Lounge — and Bay Area NRIs Can Walk In",
        "subheadline": "The 3,300-square-foot lounge near SFO's A Gates features a speakeasy-style bar, live Indian cooking stations, and art made from upcycled aircraft parts — and it's open to all Star Alliance Gold members.",
        "slug": make_slug("air-india-maharaja-lounge-sfo-bay-area-nri"),
        "category": "travel",
        "vertical": "aviation",
        "is_editorial": False,
        "diaspora_angle": "The Bay Area is home to one of the largest Indian diaspora communities in the US, and SFO is a primary gateway for flights to India — the lounge directly serves this corridor.",
        "tags": ["travel", "airlines", "air-india", "sfo", "lounge", "bay-area", "nri", "star-alliance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NerdWallet", "url": "https://www.nerdwallet.com/article/travel/air-india-maharaja-lounge-sfo-review"},
            {"name": "The Points Guy", "url": "https://thepointsguy.com/reviews/air-india-maharaja-lounge-sfo/"},
            {"name": "AFAR", "url": "https://www.afar.com/magazine/air-india-opens-maharaja-lounge-at-san-francisco-airport"},
            {"name": "Air India Newsroom", "url": "https://www.airindia.com/in/en/air-india-newsroom/air-india-maharaja-lounge-san-francisco.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/San_Francisco_International_Airport_International_Terminal.jpg/1280px-San_Francisco_International_Airport_International_Terminal.jpg",
        "image_caption": "San Francisco International Airport's International Terminal, home to Air India's new Maharaja Lounge",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the pre-flight experience for Air India passengers at SFO was a study in managed expectations. You cleared security, walked to the gate, and waited. If you held business class, you could use one of the generic contract lounges near the A gates — functional, but forgettable.

That changed on May 23 when Air India opened the Maharaja Lounge at SFO's International Terminal, its first signature lounge outside India and only the second in its new generation of premium spaces after the flagship Delhi lounge launched earlier this year.

## What's Inside

The lounge sits near Gate A1 in the international terminal's lounge complex, on the upper level past the security checkpoint. At 3,300 square feet and 80 seats, it's compact — roughly a third of the size of a United Polaris Lounge — but the design makes it feel deliberate rather than cramped.

The interior, designed by global hospitality firm Hirsch Bedner Associates (the same firm behind luxury hotel interiors worldwide), is divided into distinct zones. The front section centers on the Aviator's Bar, a speakeasy-style cocktail space with a custom architectural ceiling, premium whiskies, and curated wines. Art installations throughout the lounge were constructed from upcycled aircraft components — turbine blades, fuselage panels — giving the space an aviation-heritage feel that's more thoughtful than the usual lounge aesthetics.

The rear section is the dining area, with live cooking stations serving Indian cuisine alongside international options. Multiple reviewers have called the food the lounge's strongest asset — freshly prepared dishes rather than the buffet trays that define most airport lounges in the US.

For first-class passengers, the lounge has a "Private Zone" — essentially a lounge within a lounge — with separate seating, enhanced beverages, and a quieter atmosphere.

## Who Gets In

The access policy is broader than you might expect, and this is what matters most for Bay Area NRIs:

**Air India passengers** in first or business class, and Maharaja Club Platinum and Gold loyalty members, get automatic access. But the Maharaja Lounge is also an official Star Alliance lounge — the only one in SFO's A Gates area.

That means any **Star Alliance Gold member** flying on a Star Alliance carrier can walk in. If you hold United MileagePlus Premier Gold, Premier Platinum, or Premier 1K status — or equivalent status on Singapore Airlines, EVA Air, ANA, or any Star Alliance carrier — you're eligible. One reviewer confirmed entry using United Star Alliance Gold status on a domestic itinerary, since the lounge is airside in the international terminal.

This is a significant detail. When United removed Polaris Lounge access for most Star Alliance partners' premium cabin passengers, it left a gap in the A Gates area. Air India's lounge fills it.

## The Transformation in Context

The Maharaja Lounge is a piece of Air India's larger reinvention under Tata Group ownership. Since the acquisition in January 2022, the airline has ordered new Airbus A350s and Boeing 787s, launched cabin refurbishments across its existing fleet, and expanded its route network to over 65 weekly flights between North America and India.

The lounge strategy is part of that premium push. The Delhi Maharaja Lounge opened in February with sleep suites for first-class passengers and a Crystal Bar serving Champagne. The SFO lounge is the first international outpost, with JFK's existing Maharaja Lounge currently closed for renovations to bring it closer to the new standard.

CEO Campbell Wilson has signalled that more international signature lounges are planned. For the Bay Area's Indian diaspora — one of the densest NRI populations in the country, with direct Air India service to Delhi and Bengaluru — the SFO lounge is the most visible proof that the airline's transformation is reaching the ground experience, not just the inflight product.

## The Verdict

The lounge won't compete with the largest premium lounges at SFO — it can't match the square footage of United's Polaris Lounge or the sheer scale of the international terminal's other offerings. But reviewers have consistently noted that what it lacks in size, it compensates for in design cohesion, food quality, and a sense of place that most US airport lounges simply don't have.

The lounge is open approximately 6:30 a.m. to 10 p.m. daily, though hours may shift with the flight schedule. For NRIs heading home from the Bay Area, it's worth arriving early enough to spend time there — especially if you want to eat well before a 16-hour flight to Delhi.

The Maharaja Lounge is what Air India wants to become: a carrier that doesn't just get you to India, but makes you feel like you've already arrived."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
