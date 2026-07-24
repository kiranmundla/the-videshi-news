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
        "headline": "India Just Created a Billion-Dollar Shield Against Jet Fuel Chaos — and NRI Summer Fares Depend on It",
        "subheadline": "The Union Cabinet's ₹10,000 crore ATF stabilisation fund locks in fuel prices for Indian airlines for three years. Here's what it means for your next flight home.",
        "slug": make_slug("india-atf-fuel-stabilisation-fund-nri-summer-fares"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Indian carriers operate the bulk of India-US nonstop routes. If Air India and IndiGo can hold fares steady instead of passing through fuel spikes, NRIs booking summer and Diwali trips will see smaller sticker shocks — especially on premium cabins where fuel surcharges hit hardest.",
        "tags": ["travel", "airlines", "aviation", "fuel prices", "Air India", "IndiGo", "NRI fares"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ET Edge Insights", "url": "https://etedge-insights.com/industry/aviation/cabinet-approves-10000-crore-atf-price-stabilisation-fund-indian-airlines/"},
            {"name": "GKToday", "url": "https://www.gktoday.in/government-allocates-%E2%82%B910000-crore-for-aviation-fuel-prices/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/govt-fixes-jet-fuel-price-at-8632-perlitre-for-3-yrs-under-stabilisation-plan-1749045780349"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/see-how-much-pricier-summer-flights-are-this-year-2026-06-05/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/946841/pexels-photo-946841.jpeg",
        "image_caption": "Commercial aircraft on an airport runway at sunset",
        "image_attribution": "Pexels",
        "body": """Jet fuel prices have more than doubled since March. The Indian government just bet a billion dollars that its airlines won't have to pass the full pain on to passengers.

On June 3, the Union Cabinet approved a ₹10,000 crore ($1.05 billion) Aviation Turbine Fuel Price Stabilisation Fund — the most aggressive intervention India has ever made to shield its airline industry from fuel price shocks. The fund creates a fixed-price fuel mechanism for all scheduled Indian carriers, locking in ATF at benchmark rates for up to three years.

The numbers tell the story. International ATF prices surged from ₹60.50 per litre in March 2026 to ₹142 per litre by May — a 2.35x increase driven almost entirely by the Iran conflict and the resulting disruption to global energy markets. Fuel now accounts for nearly 40% of airline operating costs under normal conditions. During spikes like this one, it can consume 60%.

## How It Works

The fund operates through Oil Marketing Companies — Indian Oil, Bharat Petroleum, and Hindustan Petroleum — which supply ATF to domestic carriers. Under the new mechanism, these OMCs will sell fuel at a government-approved benchmark price regardless of where international crude sits on any given day. When the Import Parity Price exceeds the benchmark, the ₹10,000 crore corpus absorbs the difference. When prices moderate, the differential flows back to the Consolidated Fund of India.

It is, in effect, a revolving credit line with the taxpayer as guarantor.

The effective price works out to roughly ₹86.32 per litre for domestic operations — about ₹115 per litre in Delhi and ₹114.50 in Mumbai once port, freight, and marketing margins are added. That is still well above pre-crisis levels, but far below the ₹142 open-market rate that airlines were staring at in May.

Airlines that opt in commit to buying fuel exclusively from OMCs for the duration of the scheme. A Monitoring Committee with representatives from the Ministry of Civil Aviation, Ministry of Petroleum and Natural Gas, and the Department of Expenditure will oversee claims and reconciliation.

## Why NRIs Should Pay Attention

This is not an abstract fiscal manoeuvre. It directly shapes the fare environment on India routes.

Air India and IndiGo together operate the vast majority of nonstop services between India and the United States — SFO-DEL, JFK-BOM, ORD-DEL, EWR-BLR, and the recently launched Mumbai-Tokyo route, among others. These are the routes that 4.5 million Indian Americans rely on for summer trips home, wedding seasons, and Diwali travel.

Without the stabilisation fund, carriers faced two options: absorb the fuel cost and bleed margin, or raise fares and risk pricing out demand. IndiGo has already suspended six international routes and pulled out of Manchester. Air India has cut 22% of its domestic flights. American carriers are in similar trouble — US-origin flights are up 22% for international trips and 31% for domestic ones compared to the same period last year, according to KAYAK data published by Reuters.

The ATF fund gives Indian carriers a third option: hold fares closer to where they were, accept a slightly lower margin cushioned by the government backstop, and keep seats flying. For an NRI family of four booking economy round-trips from the Bay Area to Hyderabad, the difference between a fuel-surcharged fare and a stabilised one could easily be $300-$500 per ticket.

## The Bigger Picture

The fund is not without precedent. India earlier extended the Emergency Credit Line Guarantee Scheme 5.0 to airlines grappling with the same crisis. The Civil Aviation Ministry had also capped the April ATF price increase at 25% for domestic operations and cut landing and parking charges by 25% for three months.

But the ATF stabilisation fund is the most structural intervention yet — a three-year mechanism with a built-in recovery-and-true-up cycle, designed to outlast the current crisis rather than merely react to it.

Pakistan's airspace remains closed to Indian carriers, adding 60-90 minutes and significant fuel burn to every westbound flight from India. The Iran conflict shows no sign of de-escalation. Boeing and Airbus delivery delays have forced airlines to keep older, thirstier aircraft in service longer. These structural headwinds mean fuel volatility is not going away soon.

India's bet is that a billion-dollar buffer now prevents a far more expensive collapse of air connectivity later. For NRIs planning summer and fall travel, the bet translates into one practical reality: Indian carriers will be better positioned to hold fares than their unsubsidised competitors. Book accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Air India and Riyadh Air Just Signed a Deal — and Riyadh May Become Your Next Transit Hub to Europe",
        "subheadline": "A new MOU between India's flag carrier and Saudi Arabia's ambitious startup airline could reshape how NRIs connect to Europe, the Middle East, and beyond.",
        "slug": make_slug("air-india-riyadh-air-mou-nri-transit-europe"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "With Pakistan's airspace closed and fuel costs soaring, NRIs flying to Europe face longer routes and higher fares. A Riyadh transit hub — with codeshare flights and combined loyalty points — could offer a faster, cheaper alternative to the traditional Middle East hubs in Dubai and Doha.",
        "tags": ["travel", "airlines", "Air India", "Riyadh Air", "Saudi Arabia", "codeshare", "transit"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Travel And Tour World", "url": "https://www.travelandtourworld.com/news/article/lqzog2k7ku2b/"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/aerospace-defense/airline-chiefs-grapple-with-fuel-shock-fare-test-at-rio-summit-2026-06-06/"},
            {"name": "IATA", "url": "https://www.iata.org/en/pressroom/2026-releases/2026-06-06-01/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/VT-JRF_%40_JFK%2C_2024-11-04.png",
        "image_caption": "An Air India Boeing 777 at New York's JFK Airport",
        "image_attribution": "Wikimedia Commons",
        "body": """Air India and Riyadh Air signed a Memorandum of Understanding this week that could quietly redraw the transit map for millions of Indian travelers — including the NRIs who fly between the US and India more than almost anyone else.

The agreement, announced on June 6, covers the full spectrum of airline cooperation: codeshare flights, interline ticketing, reciprocal frequent-flyer benefits, cargo partnerships, and joint digital innovation. If executed, it would let passengers book a single itinerary from, say, San Francisco to Riyadh to London — with baggage transferring automatically and loyalty points accruing across both carriers.

On paper, it reads like a standard airline partnership announcement. In practice, it arrives at a moment when the geography of flying between India and the West is being fundamentally reshaped.

## Why Riyadh Matters Now

Two forces are converging. First, Pakistan's airspace remains closed to Indian carriers — a ban imposed during last year's military tensions that has not been lifted. Every Air India flight from Delhi to London, New York, or San Francisco now takes a longer southern routing, burning more fuel and eating into the margins that keep those routes viable. The closure adds 60 to 90 minutes to westbound journeys and has been a factor in both IndiGo's retreat from Manchester and the broader capacity cuts across Indian aviation.

Second, Saudi Arabia is spending aggressively to position Riyadh as a global aviation hub under its Vision 2030 strategy. Riyadh Air, which is wholly owned by the kingdom's Public Investment Fund, is scheduled to launch its first flights to London Heathrow on July 1. The airline has placed orders for dozens of Boeing 787 Dreamliners and plans a rapid buildout of routes connecting Riyadh to Europe, Asia, and eventually North America.

For Indian carriers locked out of the shortest path to the West, a partnership with a well-capitalised airline sitting at the geographic crossroads of Asia, Europe, and Africa is not a luxury. It is a strategic necessity.

## What NRIs Stand to Gain

The practical benefits depend on how deeply the two airlines integrate, but the potential upside is real.

**Routing options.** Today, NRIs flying from India to Europe typically transit through Dubai (Emirates), Doha (Qatar Airways), or Abu Dhabi (Etihad). Riyadh adds a fourth hub — one that could offer competitive connections to London, Paris, Frankfurt, and other European capitals once Riyadh Air's network matures. For travelers originating in the US, Air India's nonstop flights to Delhi and Mumbai connect directly to Riyadh Air's planned European network via a single stop in Riyadh.

**Pricing competition.** More hubs mean more competition on the India-Europe corridor. Emirates and Qatar Airways have had relatively free rein on premium pricing for years, partly because they face limited hub competition in the Gulf. A well-funded Riyadh Air, backed by codeshare deals with carriers like Air India, introduces pricing pressure that benefits passengers.

**Loyalty points.** If the airlines implement reciprocal frequent-flyer benefits — Air India's Maharaja Club and whatever loyalty scheme Riyadh Air launches — NRIs could earn and burn points across a wider network. For travelers who fly India routes regularly, that flexibility matters.

**Cargo connections.** This is less visible but significant for NRI businesses. Trade between India and Saudi Arabia continues to expand, and improved cargo connectivity supports supply chains for everything from pharmaceuticals to textiles.

## The Tata Group's Bigger Play

For Air India, the Riyadh Air MOU is one piece of a broader international transformation under the Tata Group. Since privatisation, the airline has pursued fleet modernisation, network expansion, and a series of strategic partnerships aimed at restoring its position as a credible global carrier.

The approach is deliberate. Rather than trying to build out every route with its own metal — expensive and slow — Air India is extending its reach through alliances and commercial cooperation. A partnership with Riyadh Air follows the same logic as Air India's existing codeshare agreements and its Star Alliance membership aspirations: use partners to fill the network gaps you cannot profitably serve on your own.

## What Comes Next

The MOU is not a done deal — it is a framework for future cooperation. The codeshare agreements, loyalty integrations, and cargo arrangements all need to be negotiated and implemented. Riyadh Air itself has yet to operate a single commercial flight, and the airline's trajectory will depend on execution, regulatory approvals, and the broader geopolitical environment.

But the direction of travel is clear. The old assumption that flying between India and the West means routing through Dubai or Doha is being challenged. Riyadh wants in on that market. Air India needs new partners. And NRIs — who collectively generate billions of dollars in annual travel spend — are the passengers both airlines are chasing.

Watch for codeshare routes to appear in booking systems by late 2026 or early 2027. If Riyadh Air's Heathrow launch goes well and the partnership moves from MOU to implementation, the next time you book a ticket from JFK to Delhi with a connection in the Gulf, Riyadh may be the stop that saves you the most time and money."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:80]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
