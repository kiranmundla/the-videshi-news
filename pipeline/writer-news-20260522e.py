#!/usr/bin/env python3
"""Videshi Writer — 3 fresh NEWS articles for 2026-05-22 (evening batch #2)
Topics: Iran peace talks + Hormuz, FIFA World Cup hotel bust, RBI rupee crisis
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Iran Peace Talks — Rubio, Hormuz, Pakistan Mediation
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Iran Peace Talks Show 'Slight Progress' as Pakistan's Army Chief Lands in Tehran. But the Strait of Hormuz Remains Closed — and India's Oil Bill Keeps Climbing.",
    "subheadline": "Secretary of State Rubio says the U.S. is 'not there yet' on a deal while rejecting Iran's proposed tolling system for the world's most important oil chokepoint. France has drafted its own UN resolution. For India, every day without a deal costs $200 million in extra crude imports.",
    "slug": make_slug("iran-peace-talks-hormuz-rubio-pakistan-india-oil"),
    "category": "news",
    "vertical": "politics",
    "diaspora_angle": "For Indian Americans watching oil prices drive up everything from airfare to India to the cost of shipping Diwali gifts home, the Hormuz stalemate is not geopolitics — it is personal finance. The rupee has already lost 6% since the war began, and every week without a deal erodes the value of every dollar remitted.",
    "tags": ["Iran", "Strait of Hormuz", "Marco Rubio", "Asim Munir", "Pakistan", "oil prices", "India", "RBI", "peace talks", "NATO"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Reuters — US Secretary of State Rubio sees progress in Iran talks, says more work to be done", "url": "https://www.reuters.com/world/asia-pacific/pakistan-seeks-breakthrough-us-iran-peace-talks-2026-05-22/"},
        {"name": "New York Post — Rubio warns Iran against 'unacceptable' tolling system with Oman for Strait of Hormuz passage", "url": "https://nypost.com/2026/05/22/us-news/marco-rubio-warns-iran-against-tolling-system-with-oman-for-strait-of-hormuz-passage-it-cant-happen/"},
        {"name": "Reuters — France readies UN resolution on Hormuz as vote on US text stalls", "url": "https://www.reuters.com/world/europe/france-readies-un-resolution-hormuz-vote-us-text-stalls-2026-05-22/"},
        {"name": "FXStreet — US Secretary of State Rubio on Iran deal: We are not there yet", "url": "https://www.fxstreet.com/news/us-secretary-of-state-rubio-on-iran-deal-we-are-not-there-yet-202605221442"},
        {"name": "Barron's — India's Battle on Two Fronts: Iran War and Rupee Slide", "url": "https://www.barrons.com/articles/india-iran-war-rupee-economy-9c1b8f45"}
    ]),
    "score_total": 92,
    "status": "published",
    "published_at": now,
    "body": """The fragile machinery of diplomacy ground forward on Friday as Pakistan's military chief landed in Tehran, Qatar dispatched a negotiating team, and the United States acknowledged — in carefully measured language — that there had been "slight progress" in the effort to end the three-month-old Iran war. But Secretary of State Marco Rubio made clear that the distance between "some progress" and an actual deal remains vast, and for India, every day of that distance has a price tag.

"There's been some progress. I wouldn't exaggerate it. I wouldn't diminish it," Rubio told reporters after a NATO foreign ministers' meeting in Helsingborg, Sweden. "There's more work to be done. We're not there yet. I hope we get there."

The diplomatic maneuvering is intensifying. Pakistani Field Marshal Asim Munir — who has become the unlikely linchpin of the negotiations after facilitating face-to-face talks between Washington and Tehran in Islamabad last month — arrived in the Iranian capital on Friday for his second visit. He was joined by Pakistan's interior minister, Syed Mohsin Naqvi, who has already met with Iranian Foreign Minister Abbas Araqchi twice this week. A Qatari negotiating team, working in coordination with Washington, also arrived in Tehran.

## The Hormuz Stalemate

The Strait of Hormuz — through which a fifth of the world's oil and liquefied natural gas normally flows — remains the single biggest obstacle to any deal. The waterway has been effectively closed since the war began on February 28, when U.S.-Israeli airstrikes triggered Iranian retaliation against Gulf states hosting American military bases. The closure has sent oil prices spiralling and triggered a global energy crisis.

Rubio on Friday rejected what he described as Iran's attempt to create a "tolling system" for the strait, accusing Tehran of trying to enlist Oman as a partner in charging fees for passage through international waters. "There is not a country in the world that should accept that," he said. "It's an international waterway. It can't happen."

He also signalled that Washington is preparing contingency plans. "There needs to be a Plan B if Iran refuses to reopen the Strait of Hormuz," Rubio said, adding that NATO countries had discussed the matter. France, meanwhile, has drafted its own UN Security Council resolution to establish an international mission to restore navigation in the strait — a parallel track that reflects European frustration with both the stalled U.S.-Bahraini resolution and Washington's unilateral approach to the crisis.

The U.S.-Bahraini draft, which demands Iran halt attacks and mining in the strait, has been under discussion for over two weeks but remains blocked by the threat of Chinese and Russian vetoes. Washington has secured nearly 140 co-sponsors in an effort to avoid a veto, but France — itself a veto-wielding power — has refused to back the text.

## Iran's Position: No Movement on Uranium

Iran's latest offer to Washington, submitted earlier this week, appears to largely repeat terms that Trump previously rejected: demands for control of the Strait of Hormuz, compensation for war damage, lifting of sanctions, release of frozen assets, and the withdrawal of U.S. troops. Iran's foreign ministry spokesman, Esmaeil Baghaei, said Friday that "diplomacy takes time" and suggested the sides were nowhere near agreement.

Most critically, Iran's Supreme Leader Ayatollah Mojtaba Khamenei has reportedly issued a directive that Iran's stockpile of near-weapons-grade enriched uranium should not be sent abroad — a direct rejection of one of Washington's core demands. Trump has said the U.S. will "eventually recover" the uranium, but the path from rhetoric to reality remains unclear.

## What This Means for India — and Every NRI Who Sends Money Home

India imports approximately 85 per cent of its crude oil, and the Hormuz closure has been catastrophic. Crude prices have spiked, the rupee has depreciated roughly 6 per cent since the war began — hitting a record low of 96.96 against the dollar this week — and the Reserve Bank of India has burned through an estimated $100 billion in reserves trying to stabilise the currency.

The arithmetic is brutal. At current prices, India's annual oil import bill has swelled by an estimated $70-80 billion compared to pre-war levels. That cost ripples through the entire economy — from the price of petrol at Delhi pumps to the airfare for an NRI flying home for a wedding. The Kearney consultancy estimated this week that the war could shave 1 to 1.5 percentage points off India's GDP growth.

For the Indian diaspora, the rupee's slide is a direct hit. A dollar bought approximately 87 rupees before the war; it now buys nearly 97. For someone sending $1,000 home every month, that is an extra ₹10,000 per remittance — a windfall in rupee terms, but a symptom of an economy under siege. And if the rupee breaches 100 — a level that Barron's reports could "spur speculative panic" — the consequences for India's financial system would be severe.

## What's Next

The next 72 hours are critical. Munir's presence in Tehran, combined with the Qatari team's arrival, suggests a push for a framework agreement before Rubio lands in India on Saturday for his four-day visit. A deal — or its absence — would dominate his meetings with Prime Minister Modi and External Affairs Minister Jaishankar, and would set the tone for Monday's Quad Foreign Ministers' Meeting in New Delhi.

Trump, facing sinking approval ratings and midterm elections in November, has his own incentives to show progress. But Iran has shown no willingness to concede on uranium or Hormuz, and Rubio's invocation of "Plan B" and "other options" is a reminder that the alternative to diplomacy is escalation. For India, caught between its dependence on Gulf energy and its deepening strategic partnership with Washington, the stakes could not be higher."""
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: FIFA World Cup 2026 Hotel Bust
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The World Cup Starts in Three Weeks. Eighty Per Cent of U.S. Hotels in Host Cities Are Below Booking Targets — and Indian American Hotel Owners Are Caught in the Middle.",
    "subheadline": "FIFA cancelled up to 70 per cent of its room blocks in five major cities. Visa barriers and the Iran war are keeping international fans away. The Indian American families who own more than half of U.S. hotels had bet big on the tournament. The payoff is not coming.",
    "slug": make_slug("world-cup-2026-hotels-empty-indian-american-owners"),
    "category": "nri-world",
    "vertical": "diaspora",
    "diaspora_angle": "Indian Americans — predominantly Gujarati Patel families — own an estimated 60 per cent of all U.S. hotels. AAHOA, the industry's largest association with 20,000 members, represents billions in combined revenue. The World Cup hotel bust hits this community harder than any other demographic in American hospitality.",
    "tags": ["FIFA World Cup 2026", "hotels", "Indian Americans", "AAHOA", "hospitality", "Patel", "visa", "tourism", "Airbnb"],
    "urgency": "standard",
    "sources": json.dumps([
        {"name": "Dexerto — World Cup hotels are sitting empty after FIFA cancelled up to 70% of its reserved rooms", "url": "https://www.dexerto.com/entertainment/world-cup-hotels-are-sitting-empty-after-fifa-cancelled-up-to-70-of-its-reserved-rooms-3366608/"},
        {"name": "BBC — AHLA World Cup hotel survey findings", "url": "https://www.bbc.com/sport/football/articles/c0k5k5e0e58o"},
        {"name": "Sportsnet — 'The prices are crazy': Ticket, hotel costs skyrocket for World Cup in Vancouver", "url": "https://www.sportsnet.ca/soccer/article/the-prices-are-crazy-ticket-hotel-costs-skyrocket-for-world-cup-in-vancouver/"},
        {"name": "Newsy Today — World Cup 2026 Bookings Fall Short as High Costs and FIFA Policies Deter Fans", "url": "https://newsy-today.com/world-cup-2026-bookings-fall-short-as-high-costs-and-fifa-policies-deter-fans/"},
        {"name": "Expedia Group — Rise in 2026 summer domestic travel amid World Cup", "url": "https://stocktitan.net/press-releases/expedia-group-tracks-rise-in-2026-summer-domestic-travel/"}
    ]),
    "score_total": 84,
    "status": "published",
    "published_at": now,
    "body": """The 2026 FIFA World Cup kicks off on June 11, and the American hotel industry is staring at a disaster it did not see coming. A survey by the American Hotel & Lodging Association found that 80 per cent of hotels in the 11 U.S. host cities are tracking below booking expectations — a staggering shortfall for an event that was supposed to deliver the biggest hospitality windfall in a generation. For the Indian American families who own more than half of the country's hotels, the math is suddenly, painfully wrong.

The problem started at the top. FIFA had block-booked large volumes of hotel rooms across host cities in the years leading up to the tournament, creating what hoteliers say were artificial demand signals that shaped revenue forecasts, staffing decisions, and investment plans. Then FIFA cancelled. In Boston, Dallas, Los Angeles, Philadelphia, and Seattle, up to 70 per cent of FIFA-reserved rooms were released back to hotels — rooms that are now sitting empty with the tournament weeks away.

The AHLA surveyed more than 200 hoteliers across all 11 host cities and the picture is grim. Domestic travellers are outpacing international visitors, but the high-spending foreign fans that hotels had planned around have largely not materialised. In Boston, Philadelphia, and Seattle, booking pace is trailing a typical summer season — not a summer with the world's biggest sporting event.

## The Diaspora's Hospitality Empire

To understand why this matters so disproportionately to the Indian American community, you need to understand a single statistic: Indian Americans — predominantly Gujarati families, many with the surname Patel — own an estimated 60 per cent of all hotels in the United States. It is one of the most remarkable entrepreneurial achievements in American immigration history. The Asian American Hotel Owners Association, AAHOA, represents more than 20,000 members who collectively own properties worth over $150 billion.

These are not, for the most part, luxury chains with diversified revenue streams. Many are independent and economy-tier properties — the kinds of hotels that depend on events, conventions, and tourism spikes to hit their numbers. A World Cup in their own country was supposed to be a once-in-a-generation event. Hotel owners in host cities invested in renovations, hired additional staff, and adjusted pricing in anticipation of demand that is not arriving.

The impact is not evenly distributed. Miami and Atlanta are outperforming expectations, buoyed by confirmed team base camps, strong leisure appeal, and better air connectivity. But those markets represent only 25 to 30 per cent of total respondents in the AHLA survey. The rest — including major Indian American hotel markets like Dallas, Houston-adjacent areas, and the Northeast corridor — are underperforming.

## Why the Fans Aren't Coming

The reasons are a convergence of bad timing and bad policy. Between 65 and 70 per cent of surveyed hoteliers cited visa barriers and geopolitical concerns as the top constraint on international travel. The Iran war has made the United States a harder sell for international tourists — not because of any direct threat, but because of the global economic uncertainty, higher airfares driven by fuel costs, and the general mood of caution.

Ticket prices have not helped. World Cup tickets have reportedly hit $11,000 on the secondary market, and even face-value tickets for marquee matches are priced beyond what many international fans can justify when combined with flights and accommodation from Europe, South America, or Asia.

Then there is Airbnb. The platform said the World Cup is on course to be the biggest hosting event in its history, surpassing the 2024 Paris Olympics. New Jersey, adjacent to the MetLife Stadium host venue, has aggressively courted short-term rental hosts, while New York has maintained restrictions. The result is a fragmented accommodation market where hotels compete not just with each other but with a parallel economy of spare bedrooms and converted apartments.

## The India Cricket Comparison

For Indian Americans, the contrast with cricket is instructive. When India plays in an ICC tournament or a major bilateral series, the Indian diaspora turns out in force — filling stadiums, booking hotels, and spending generously. The World Cup, despite being the biggest event in global sport, does not activate the same economic engine in Indian American communities. Football is not cricket, and the diaspora's spending patterns reflect that.

This matters because the Indian American hotel owner in Dallas or Seattle is not losing money because of a sport they follow — they are losing money because of a sport they bet on, based on projections from the world's most powerful sporting body. When FIFA block-books rooms and then cancels, the hotel owner is left holding the downside risk.

## What Happens Next

The tournament itself may still generate a late booking surge — the AHLA notes that many fans buy tickets and accommodation closer to match dates, and the sheer scale of a 48-team World Cup means more matches and more fan bases than any previous edition. But the structural damage is done. Hotels that staffed up, renovated, and priced aggressively based on FIFA's original room blocks cannot easily recover those costs.

For Indian American hotel owners, the lesson is familiar: in the hospitality business, you are always one cancellation away from a bad quarter. But this cancellation came from FIFA, and the scale is national. As one hotelier in the AHLA survey put it, "We planned for a World Cup. What we got is a typical summer with a branding problem." """
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: RBI's Emergency Rupee Defence
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The Rupee Just Hit a Record Low. The RBI Is Throwing $5 Billion at It, Considering a Rate Hike, and Still Running Out of Options.",
    "subheadline": "India's central bank is deploying emergency measures — a $5 billion dollar-rupee swap, potential NRI bonds, and a possible interest rate reversal — as the currency slides toward the psychological barrier of 100 to the dollar. For the diaspora, every rupee of depreciation changes the math on remittances, property, and retirement plans.",
    "slug": make_slug("rbi-rupee-record-low-dollar-swap-rate-hike"),
    "category": "markets-finance",
    "vertical": "economy",
    "diaspora_angle": "For millions of NRIs who remit money to India, own Indian property, or plan to retire there, the rupee's collapse is a double-edged sword. Each dollar buys more rupees today — but if the RBI is forced to hike rates, Indian home loans become more expensive, stock markets may fall, and the broader economy that supports family back home comes under pressure.",
    "tags": ["RBI", "rupee", "dollar", "interest rate", "NRI bonds", "FCNR", "remittances", "oil prices", "Sanjay Malhotra", "India economy"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Devdiscourse — RBI announces USD 5 billion USD/INR swap auction on May 26 to inject liquidity", "url": "https://www.devdiscourse.com/article/business/3354631-rbi-announces-usd-5-billion-usd-inr-swap-auction-on-may-26-to-inject-liquidity"},
        {"name": "Madhyamam — RBI is evaluating multiple steps to check rupee decline: sources", "url": "https://madhyamamonline.com/business/rbi-is-evaluating-multiple-steps-to-check-rupee-decline-sources-1521781"},
        {"name": "Inshorts — RBI weighing rate hike to stabilise falling rupee: Report", "url": "https://inshorts.com/en/news/rbi-weighing-rate-hike-to-stabilise-falling-rupee-report-1747791960258"},
        {"name": "Barron's — India's Battle on Two Fronts: Iran War and Rupee Slide", "url": "https://www.barrons.com/articles/india-iran-war-rupee-economy-9c1b8f45"},
        {"name": "Livemint — Reserve Bank of India to hold $5 billion USD/INR forex swap auction on 26 May", "url": "https://www.livemint.com/market/stock-market-news/reserve-bank-of-india-to-hold-5-billion-usd-inr-forex-swap-auction-on-26-may-to-ease-banking-system-liquidity-11747751230966.html"}
    ]),
    "score_total": 88,
    "status": "published",
    "published_at": now,
    "body": """The Reserve Bank of India has entered emergency mode. After the rupee plunged to a record low of 96.96 against the U.S. dollar on Wednesday — losing 2.5 per cent in just nine trading sessions — Governor Sanjay Malhotra and senior officials have been holding a series of internal meetings that, according to Bloomberg, include discussion of the one tool the central bank has spent the past year trying to avoid: a rate hike.

The RBI has announced a $5 billion USD-INR buy-sell swap auction for May 26, a three-year operation designed to inject rupee liquidity into the banking system while absorbing dollars. It is the latest in a series of increasingly aggressive interventions that have already consumed an estimated $100 billion in foreign exchange reserves since the Iran war began in February. The rupee closed the week at 96.83, and traders say only the RBI's muscular intervention — including offshore and non-deliverable forwards — is preventing it from breaching 97.

But the swap is not a silver bullet. Sources told Madhyamam that the central bank is evaluating a wider arsenal: Foreign Currency Non-Resident deposits, NRI bonds, additional swap operations, and the removal of withholding taxes on overseas bonds to attract dollar inflows. All proposals are "still under discussion," the sources said, and no final decisions have been taken.

## The Rate Hike Dilemma

The most consequential measure under consideration is a reversal of the RBI's recent easing cycle. The central bank has cut rates twice this year — bringing the repo rate to 5.15 per cent — to support an economy buffeted by the global slowdown. A rate hike would be a dramatic about-face that would signal to markets that the RBI prioritises currency stability over growth.

The dilemma is acute. Higher rates would make the rupee more attractive to foreign investors and slow capital outflows. But they would also increase borrowing costs for Indian businesses and consumers, potentially tipping an already strained economy into sharper deceleration. India's GDP is still growing at nearly 7 per cent, but economists warn that the war's impact on trade, remittances, and energy costs is already shaving 1 to 1.5 percentage points off growth.

The next scheduled rate decision is June 5 — the first meeting under new Fed Chair Kevin Warsh in the United States, and a date that will force the RBI to show its hand. Markets are watching for any signal in the interim.

## The $100 Billion Question

The scale of the RBI's defence is staggering. An estimated $100 billion in foreign exchange reserves has been deployed since February to prevent the rupee from falling further. India's reserves, which stood at approximately $640 billion before the war, have been drawn down significantly, and the pace of depletion has accelerated as global conditions worsen.

The problem is structural. India imports 85 per cent of its crude oil, and the closure of the Strait of Hormuz has driven Brent crude to sustained levels above $90 a barrel. Every $10 increase in the oil price widens India's current account deficit by roughly $15 billion annually. At the same time, foreign institutional investors have been pulling money out of Indian equities and bonds, attracted by higher U.S. yields and unsettled by the geopolitical environment.

The result is a one-way bet against the rupee that the RBI is fighting with finite ammunition. Rajeev de Mello, a global macro portfolio manager at GAMA Asset Management, told Barron's that the "optical level of 100 could spur a speculative panic" — a warning that the currency's decline could become self-reinforcing if the psychological barrier is breached.

## What This Means for NRIs

For the Indian diaspora, the rupee's collapse is a complex equation.

**Remittances:** At 96.83 rupees to the dollar, each dollar remitted buys roughly 10 more rupees than it did six months ago. For the millions of Indian Americans who send money home monthly — India received $120 billion in remittances in 2025, the highest in the world — the weak rupee is a short-term windfall. Parents receive more, loan repayments go further, and Indian property becomes cheaper in dollar terms.

**Property and investments:** NRIs holding dollar savings and eyeing Indian real estate are in a favourable position — but only if the rupee stabilises. A further slide to 100 or beyond would signal deeper economic distress that could depress property values and stock markets, erasing any currency advantage.

**NRI bonds and FCNR deposits:** If the RBI launches a new NRI bond scheme — as it did successfully in 2013 when the rupee was under similar pressure — it could offer diaspora investors attractive dollar-denominated returns backed by India's central bank. The 2013 FCNR scheme raised $34 billion in just three months. A similar offering today could simultaneously strengthen reserves and give NRIs a high-yield investment.

**The rate hike trap:** If the RBI does hike rates, home loan EMIs in India will rise. For NRIs who own property in India financed by rupee-denominated loans, this is a direct cost increase. For Indian family members dependent on stable borrowing costs, it is a household budget hit.

## The Bigger Picture

India's currency crisis is not an isolated event. It is the domestic expression of a global energy shock, a regional war, and the tightening of U.S. monetary policy under a new Fed chair who has given few signals about his intentions. The RBI is fighting on multiple fronts simultaneously — defending the currency, maintaining liquidity, keeping rates supportive, and preserving reserves — and the limits of that defence are becoming visible.

The $5 billion swap on Monday will be closely watched, but it is the June 5 rate decision that will define the RBI's strategy for the months ahead. For India's economy, and for the millions of diaspora members whose financial lives straddle two currencies, the answer will be felt immediately — in the cost of a flight to Mumbai, the value of a wire transfer to Ahmedabad, and the EMI on a flat in Bengaluru."""
})


# ══════════════════════════════════════════════════════════════
# INSERT ARTICLES
# ══════════════════════════════════════════════════════════════
print(f"Inserting {len(articles)} articles...")
for a in articles:
    try:
        result = sb_post("p2_articles", a)
        print(f"  ✓ {a['headline'][:70]}...")
    except Exception as e:
        print(f"  ✗ {a['headline'][:50]}... — {e}")

# Mark the World Cup pending topic as published
wc_topic_id = None
r = requests.get(
    f"{SB_URL}/rest/v1/p2_topics?canonical_title=ilike.%25World%20Cup%25Hotel%25&status=eq.pending&limit=1",
    headers={
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
    },
    timeout=15,
)
topics = r.json()
if isinstance(topics, list) and topics:
    wc_topic_id = topics[0]["id"]
    code = sb_patch("p2_topics", f"id=eq.{wc_topic_id}", {"status": "published", "score_total": 84})
    print(f"  Topic {wc_topic_id[:8]} (World Cup) → published ({code})")

print("Done!")
