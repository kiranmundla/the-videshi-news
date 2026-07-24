#!/usr/bin/env python3
"""Videshi Travel Writer — 2026-05-25 15:00 PDT batch"""

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
        "headline": "American Airlines Just Opened Four New Doors to Europe — and NRIs in Philly and Dallas Should Pay Attention",
        "subheadline": "Nonstop flights from Philadelphia to Budapest and Prague, and from Dallas to Athens and Zurich, give Indian Americans direct access to four European cities that previously required layovers.",
        "slug": make_slug("american-airlines-europe-routes-phl-dfw-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "NRIs in the Philadelphia and Dallas-Fort Worth metros — two corridors with significant Indian American populations — now have nonstop options to Central and Southern Europe. The PHL-Budapest route is the only direct US-Hungary service from any carrier, and the Prague route restores a connection that had lapsed. For tech workers in DFW's rapidly growing Indian community, direct Zurich access opens a corridor to Switzerland's banking and pharma hubs without the Frankfurt or Amsterdam layover.",
        "tags": ["travel", "airlines", "american-airlines", "europe", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Simple Flying", "url": "https://simpleflying.com/american-airlines-4-new-european-routes/"},
            {"name": "Aviation A2Z", "url": "https://aviationa2z.com/american-airlines-launches-4-new-europe-routes-for-summer-2026/"},
            {"name": "Travel and Tour World", "url": "https://travelandtourworld.com/american-airlines-summer-2026-route-surge/"},
            {"name": "AFAR", "url": "https://afar.com/magazine/american-adds-5-new-europe-routes-for-2026"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16922415/pexels-photo-16922415.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Prague's red rooftops — now a nonstop flight from Philadelphia.",
        "body": """American Airlines launched four new nonstop transatlantic routes on May 21, quietly reshaping how Indian Americans in two major metro areas can reach parts of Europe that have historically required awkward connections. The additions — Philadelphia to Budapest and Prague, Dallas-Fort Worth to Athens and Zurich — bring American's daily US-Europe flight count to 70, the highest in the airline's century-long history.

## What's new, specifically

The Philadelphia–Budapest route is the only direct service between the United States and Hungary offered by any airline. The Philadelphia–Prague route restores a seasonal connection that had lapsed, putting the Czech capital within a single 9-hour flight of the East Coast. Both run on Boeing 787-8 Dreamliners.

From Dallas-Fort Worth, the new Athens route competes directly with Delta's existing JFK–Athens service but offers a mid-continent departure point for the first time. The DFW–Zurich route, operated on a Boeing 777-300ER, gives Texas-based travelers nonstop access to Switzerland without routing through United's Newark or Lufthansa's Frankfurt hubs.

All four are seasonal summer services, running through early fall.

## Why NRIs should care

The Philadelphia metro area is home to roughly 130,000 Indian Americans, with dense clusters in the western suburbs along the Main Line and in South Jersey. For this community, the new Budapest route opens a gateway to Central Europe that previously required connections at London, Frankfurt, or Istanbul. Budapest has become an increasingly popular destination for Indian American travelers — affordable by European standards, architecturally stunning, and connected by rail to Vienna and Prague.

The DFW-Zurich connection matters for a different reason. The Dallas-Fort Worth Indian community has grown rapidly alongside the region's tech expansion, with companies like Texas Instruments, Infosys, and Wipro all running significant operations. Direct Zurich access eliminates a connection that typically added three to five hours to the trip, making business day-trips to Switzerland's pharma and banking corridor meaningfully more practical.

American is calling this its biggest summer schedule ever, with plans to fly 75 million passengers across 750,000 flights this season. The airline has also restructured its Philadelphia hub with new "bank" schedules that improve connection times for domestic-to-international transfers — relevant for NRIs flying in from other US cities through PHL.

## The competitive picture

American still trails Delta and United in total transatlantic capacity. Delta dominates the premium New York–Europe market, while United has built a massive hub-and-spoke operation at Newark. But American is playing a niche game — targeting city pairs that Delta and United have left uncovered. Budapest and Prague are exactly the kind of underserved destinations where a single nonstop route can capture disproportionate demand.

For Indian Americans planning summer Europe trips, the practical calculus is straightforward: check whether American's new routes serve your destination before defaulting to the usual Delta/United options through JFK or EWR. A nonstop from PHL to Prague at $600-800 round-trip will beat a one-stop through Frankfurt at $900+ every time — especially when the connection risk during a chaotic summer travel season is factored in.

## The fine print

These are seasonal routes, so they will disappear in the fall. American has not committed to year-round service on any of the four. If the routes perform well this summer — measured by both load factors and revenue per seat mile — expect them to return in 2027, potentially with expanded frequency. If they don't, they'll go the way of dozens of other aspirational transatlantic routes that airlines launch and quietly retire.

Book early. American's widebody fleet is limited, and these routes will fill quickly as the summer travel season peaks."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Spirit Airlines Is Dead, and It's Not Alone — The Airline Bankruptcy Wave That Should Worry Every NRI Flyer",
        "subheadline": "Spirit's final shutdown, three more carrier collapses, and Polymarket giving JetBlue a 13% chance of filing by year-end add up to a summer where booking the wrong airline could leave you stranded.",
        "slug": make_slug("spirit-airlines-dead-bankruptcy-wave-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Spirit was the cheapest way for many NRIs to fly domestically — connecting through Fort Lauderdale or Detroit to reach smaller US cities. Its death removes budget seat capacity from the domestic market, pushing fares up on the carriers NRIs rely on for connections after landing on international flights. JetBlue, popular for JFK connections, faces its own financial pressure. Every NRI with a multi-carrier itinerary this summer should stress-test their bookings.",
        "tags": ["travel", "airlines", "spirit-airlines", "bankruptcy", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/travel/one-more-airline-files-for-bankruptcy-and-cancels-all-flights"},
            {"name": "Polymarket", "url": "https://polymarket.com/event/airline-bankruptcy-2026"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/travel/another-airline-files-for-bankruptcy-and-cancels-all-flights"},
            {"name": "Simple Flying", "url": "https://simpleflying.com/jetblue-fort-lauderdale-a220-base/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36376791/pexels-photo-36376791.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Empty terminals are becoming more common as airlines fold under fuel pressure.",
        "body": """On May 2, Spirit Airlines canceled its last flight. The airline that pioneered ultra-low-cost flying in America — the one where you paid $49 for the seat and $45 for the carry-on — is finished. Two prior bankruptcy filings couldn't save it. A jet fuel crisis that has doubled the cost of keeping planes in the air delivered the final blow.

Spirit is the biggest name to fall, but it is not alone. The count of airline shutdowns and bankruptcy filings in 2026 is growing at a pace not seen since the post-9/11 era.

## The body count so far

Spirit Airlines shut down all remaining operations on May 2 after failing to emerge from its second Chapter 11 filing. The proximate cause was jet fuel prices that surged from $831 per tonne in late February to $1,838 by early April — a cost structure that made Spirit's thin-margin, high-frequency model mathematically impossible to sustain.

In Mexico, low-cost holiday carrier Magnicharters filed for bankruptcy protection after suspending all flights, stranding thousands of passengers who had booked vacation packages. In China, regional carrier Joy Air entered restructuring after canceling all flights in April. In the UK, charter operator Zenith Aviation went into administration over "cashflow issues and unpaid debtors," and its 41 employees are now out of work.

Earlier in the year, Houston-based Starflite Aviation had its operating certificate revoked after the FAA found that owners had falsified pilot training records. Slovenian charter airline AlpAvia shut down in March. Swedish carrier H-Bird was declared bankrupt by a judge after losing its operating license.

## Why NRIs should be paying attention

Spirit's death is not an abstraction for Indian Americans. The airline operated 600+ daily flights across the US, and its ultra-low fares acted as a price anchor across the domestic market. When Spirit offered a $79 fare from Fort Lauderdale to Detroit, Delta and United had to keep their competing fares within striking distance. That competitive pressure is now gone on dozens of routes.

For NRIs, the practical impact is twofold. First, domestic connection fares are likely to rise. If you fly Air India or Emirates into JFK and then need to get to, say, Nashville or Raleigh, the cheapest connecting options just got more expensive. Spirit was often the airline filling that gap.

Second — and more concerning — the financial stress is not limited to Spirit. Prediction markets on Polymarket currently give Frontier Airlines an 18% probability of filing for bankruptcy by December 31, and JetBlue a 13% probability. JetBlue is particularly relevant to NRIs: it operates a massive JFK network and has been a go-to carrier for domestic connections after international arrivals. The airline is cutting 11 routes elsewhere in its network to fund an expansion at Fort Lauderdale, a strategy that signals financial triage more than confident growth.

## How to protect yourself

If you have bookings on any carrier that feels financially precarious, here is the playbook:

**Pay with a credit card, not a debit card or bank transfer.** Credit card chargebacks are your strongest protection if an airline collapses before your flight. Debit card disputes are harder to win, and airline vouchers become worthless in a bankruptcy.

**Book refundable fares when the cost difference is modest.** A $30 premium for a refundable ticket is cheap insurance when the carrier might not exist in three months.

**Avoid booking separate tickets for domestic connections.** If your Air India JFK arrival and your JetBlue JFK-to-wherever departure are on separate tickets, a delay on one means you eat the cost of the other. Book through-fares or same-alliance connections whenever possible.

**Check your airline's financial health before booking.** This sounds paranoid, but it wasn't long ago that people booked Spirit flights for June and discovered the airline was gone by May. A quick search for "[airline name] bankruptcy risk" takes 30 seconds and can save hundreds.

## The bigger picture

The Iran-driven oil crisis has doubled jet fuel costs in three months, and airlines operating on thin margins have no cushion. The larger carriers — Delta, United, American — will survive by cutting routes, raising fares, and shrinking capacity. But the budget airlines that Indian Americans have used for years to stretch their travel budgets are the ones most exposed to this shakeout.

The summer of 2026 is not the time to book the cheapest possible fare from the most financially fragile carrier. Book smart, book protected, and assume that the airline landscape you see today may not be the one that exists in September."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Asiana Airlines Disappears in December — What Every NRI Using Star Alliance Miles Needs to Do Before Then",
        "subheadline": "Korean Air's absorption of Asiana on December 17 will pull the airline out of Star Alliance and into SkyTeam, eliminating a key Asian connection for Indian Americans who earn miles on Air India or United.",
        "slug": make_slug("asiana-korean-air-merger-star-alliance-nri"),
        "category": "travel",
        "vertical": "travel",
        "diaspora_angle": "Air India — the default carrier for millions of NRIs — is a Star Alliance member. So is United, the most popular US carrier for India routes. NRIs who pool miles across these Star Alliance partners have long used Asiana as a connecting airline for Seoul, Southeast Asia, and Australia. That option vanishes December 17. Every NRI sitting on Star Alliance miles earmarked for Asiana flights has until December 1 to book or lose the redemption path entirely.",
        "tags": ["travel", "airlines", "star-alliance", "korean-air", "asiana", "nri"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AirPro News", "url": "https://airpronews.com/2026/05/20/lufthansa-issues-euro-bond-amid-rising-fuel-costs-and-operational-cuts/"},
            {"name": "Korea JoongAng Daily", "url": "https://koreajoongangdaily.joins.com/news/industry/korean-air-asiana-merger-december-2026"}
        ]),
        "score_total": 68,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32211620/pexels-photo-32211620.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Incheon International Airport — soon to be a single-carrier Korean Air hub.",
        "body": """On December 17, 2026, Asiana Airlines will cease to exist. Every Asiana aircraft will be repainted in Korean Air livery. Every Asiana route will operate under the Korean Air code. And every Asiana frequent flyer mile will be converted into Korean Air SKYPASS points at a ratio that has not yet been finalized.

For most travelers, this is background noise — another airline merger in a consolidating industry. For Indian Americans who fly Star Alliance, it is a quiet but consequential shift that could affect how they book flights across Asia for years to come.

## What's actually happening

Korean Air and Asiana Airlines announced their merger in November 2020 as part of a South Korean government rescue package during the pandemic. After six years of antitrust review across 13 countries — including the US, EU, Japan, and China — the deal was formally approved. The boards of both airlines signed the merger contract on May 14, 2026.

The mechanics are straightforward: Korean Air absorbs all of Asiana's assets, liabilities, routes, and personnel. Asiana's brand disappears entirely. The merged airline will operate exclusively under the Korean Air name from one of Asia's most efficient hub airports — Incheon International, outside Seoul.

The alliance shift is where it gets complicated. Asiana is currently a member of Star Alliance, alongside Air India, United Airlines, Lufthansa, Singapore Airlines, and others. Korean Air is a member of SkyTeam, alongside Delta, Air France-KLM, and China Eastern. When the merger closes, the combined carrier stays in SkyTeam. Asiana leaves Star Alliance permanently.

## Why this matters for NRIs

The Indian American travel ecosystem runs heavily through Star Alliance. Air India — the carrier that operates more US-India nonstops than anyone else — joined Star Alliance in 2014. United Airlines, which serves Delhi from Newark and San Francisco, is a founding Star Alliance member. Most NRIs who accumulate airline miles do so across these two carriers.

Asiana has been a valuable Star Alliance partner for NRIs traveling beyond India. Want to fly from San Francisco to Seoul on United, then connect to Ho Chi Minh City on Asiana using miles? That has been a standard Star Alliance redemption for years. Want to route through Incheon to reach Sydney or Melbourne on a Star Alliance itinerary? Asiana was often the connecting carrier that made the pricing work.

After December 17, those itineraries break. Korean Air will be a SkyTeam carrier, which means Star Alliance miles — whether earned on Air India, United, or any other member — cannot be used to book seats on the merged airline. The connecting options through Seoul will still exist, but they will only be accessible through Delta SkyMiles, Air France-KLM Flying Blue, or other SkyTeam programs.

## The December 1 deadline

Star Alliance has set December 1, 2026, as the strict cutoff for booking award flights on Asiana using partner miles. After that date, no new Asiana award bookings will be accepted through programs like Air Canada Aeroplan, United MileagePlus, or Singapore Airlines KrisFlyer.

If you are sitting on Star Alliance miles and have been considering a Seoul routing — or any itinerary that uses Asiana as a connecting carrier — the window to book is narrowing. Award availability on popular routes tends to dry up 3-4 months before travel, which means the practical booking window for fall travel through Asiana is essentially now through mid-June.

## What replaces the lost connectivity

Star Alliance will not be without Asian coverage after Asiana exits. Singapore Airlines, ANA (All Nippon Airways), EVA Air, Thai Airways, and Asiana's own former codeshare partners will remain in the alliance. But none of them hub in Seoul, which means Incheon — one of Asia's best-connected airports — effectively becomes a SkyTeam-only hub for alliance-based travel.

For NRIs who want to keep using Incheon as a transit point, the practical move is to build some Delta SkyMiles balance alongside their Star Alliance portfolio. Delta's partnership with Korean Air is deep, and the merged carrier's enhanced Incheon hub will likely offer better SkyTeam redemption options than Asiana ever did as a Star Alliance member.

Alternatively, NRIs can shift their Asia transit strategy to Singapore (via Singapore Airlines), Tokyo Narita (via ANA), or Bangkok (via Thai Airways) — all Star Alliance hubs that remain unaffected by the merger.

## The bottom line

This is not an emergency, but it is a deadline. Indian Americans who fly Star Alliance and have ever used Asiana as part of their routing need to audit their miles balances, check whether any planned itineraries route through Korean Air or Asiana metal, and book any remaining Asiana award flights before December 1. After that, the alliance math changes permanently."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
