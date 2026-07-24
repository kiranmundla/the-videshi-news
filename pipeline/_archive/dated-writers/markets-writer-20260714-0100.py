#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-14 01:00 PDT run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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


# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 1: India's CPI inflation surges to 4.38%
# ═══════════════════════════════════════════════════════════════════════

art1_body = """India's consumer price index rose 4.38% year-on-year in June, the government confirmed on Monday — breaching the Reserve Bank of India's 4% medium-term target for the first time in 17 months and landing above the 4.30% that economists in a Reuters poll had forecast.

The number marks the highest reading since India overhauled its CPI basket in January, and it arrives at an awkward moment: crude oil is climbing again after renewed U.S.-Iran strikes in the Gulf, the monsoon has been erratic enough to push vegetable prices higher, and state-owned fuel retailers have already hiked pump prices four times since May.

## What Drove the Jump

Food inflation accelerated to 5.32% in June from 4.78% the previous month. Vegetable and cereal prices led the charge, partly because rainfall in June — the first critical month of the kharif sowing season — arrived unevenly across key growing states. Transport costs surged to 4.31% from 1.75% in May, reflecting the cumulative impact of those fuel-price revisions.

Core inflation, which strips out food and fuel, remained relatively contained, suggesting the headline spike is supply-driven rather than a sign of overheating demand. But that distinction may not matter much to the RBI if the supply shocks prove persistent.

## The Rate Hike Calculus

The central bank held its repo rate steady at 5.25% at its June meeting but raised its full-year inflation forecast to 5.1% from 4.6%, a clear signal that the Monetary Policy Committee is watching the data closely.

Markets are now pricing in rate hikes before year-end. Goldman Sachs expects 25-basis-point increases in both October and December. Kotak Mahindra Bank's chief economist Upasna Bhardwaj sees 50 basis points of cumulative tightening in the second half of FY27. OCBC Bank projects a "shallow hiking cycle" of 50 basis points total, likely in late 2026 and early 2027.

"Inflation inched up by close to 45 basis points in June to 4.4%, mainly driven by some increase in food and fuel inflation as the impact of a revision in petrol and diesel prices played out," said Sakshi Gupta, principal economist at HDFC Bank. She estimates inflation will average 5.2% for FY27, assuming oil stays around $80 per barrel.

## What NRI Investors Should Watch

**NRE and NRO deposits.** Rate hikes are straightforwardly good news for NRI depositors. Indian banks have already started nudging up term-deposit rates, and a 50-basis-point hike cycle would push one-year NRE fixed-deposit rates above 7% at several major banks — a meaningful yield pickup for dollar earners, especially with the rupee near 95.60 per dollar.

**Bond portfolios.** The 10-year benchmark government bond yield ended last week at 6.71%, recovering from an intraweek high of 6.77%. Traders expect the yield to oscillate between 6.65% and 6.77% this week. If rate hikes materialise, existing bondholders face mark-to-market losses, but new allocations at higher yields become more attractive. Foreign investors have net purchased over $4.1 billion of Indian bonds since June 1 through the Fully Accessible Route — a vote of confidence in India's fiscal trajectory even as inflation ticks up.

**Equities.** Rate-sensitive sectors — real estate, auto, and consumer durables — typically underperform in a tightening cycle. Banking stocks, by contrast, can benefit from wider net interest margins, which partly explains why Bank Nifty jumped 1.15% last Friday even as pharma and healthcare fell more than 1%.

**The rupee.** The Indian currency slipped to a one-month low of 95.85 per dollar on Monday before settling at 95.62, pressured by rising oil prices. Options markets are signalling a bearish bias, with the 1-month risk reversal drifting to 0.3 from near zero at the start of July. For NRIs timing remittances, the combination of a weaker rupee and higher deposit rates creates an attractive entry window — though the direction of crude oil remains the dominant wild card.

## The Bigger Picture

India's wholesale price index data for June, due Tuesday, is expected to show WPI inflation at around 9.15% — adding to the producer-side pressure. The widening gap between wholesale and retail inflation suggests that companies are absorbing margin compression rather than passing costs to consumers, but that cushion has limits.

The Iran conflict remains the elephant in the room. Brent crude rose 3% to $78 per barrel on Monday after Tehran said it had closed the Strait of Hormuz. India imports roughly 4.93 million barrels per day — a record — and more than half now comes from Russia. Any sustained disruption to Gulf shipping lanes would push inflation well above current forecasts and accelerate the RBI's tightening timeline.

For NRI investors with exposure to Indian markets, the message is clear: the era of ultra-cheap money in India is over, and portfolio positioning should reflect it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's CPI Inflation Surges to 4.38% — The Rate Hike Cycle Is Coming, and NRI Portfolios Need to Adjust",
    "subheadline": "June's reading blew past the RBI's 4% target for the first time in 17 months. Goldman expects two rate hikes by December. Here's what it means for NRE deposits, bonds, and equities.",
    "slug": make_slug("india-cpi-inflation-4-38-rate-hike-nri-deposits-bonds"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "Rate hikes boost NRE/NRO deposit yields above 7%, creating an attractive remittance window for dollar earners even as bond portfolios face mark-to-market risk and rate-sensitive equities come under pressure.",
    "tags": ["inflation", "rbi", "interest-rates", "nri-investing", "nre-deposits", "bonds"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-retail-inflation-accelerates-438-raising-rate-hike-expectations-2026-07-13/"},
        {"name": "Reuters Instant View", "url": "https://www.reuters.com/world/india/instant-view-indias-retail-inflation-accelerates-438-raising-rate-hike-expectations-2026-07-13/"},
        {"name": "Reuters — Rupee & Bonds Outlook", "url": "https://www.reuters.com/world/india/indian-rupee-bonds-likely-track-mideast-developments-inflation-data-2026-07-13/"},
        {"name": "Dainik Bhaskar English", "url": "https://bhaskarenglish.in/rbi-inflation-data-july-2026/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Stock market data display reflecting market volatility amid rising inflation",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}

# ═══════════════════════════════════════════════════════════════════════
# ARTICLE 2: India's gold ETF boom meets reality check
# ═══════════════════════════════════════════════════════════════════════

art2_body = """India's gold exchange-traded funds are sitting on a mountain of money that would have been unthinkable two years ago. Assets under management surged to ₹1.85 lakh crore ($21.8 billion) by May 2026 — up roughly 195% from the year before — and the first quarter of 2026 was the strongest on record for Indian gold ETF inflows, with net purchases of about 20 tonnes accounting for a remarkable 32% of all global gold ETF demand.

But the boom has hit a wall. Six of India's largest fund houses — HDFC, ICICI Prudential, Nippon India, Tata Asset Management, Axis, and Aditya Birla Sun Life — moved in rapid succession during June to cap direct gold ETF subscriptions at ₹25 crore and limit lump-sum purchases in their gold funds-of-funds to ₹10 lakh per PAN per calendar month.

The restrictions are a signal: the gold trade in India has gotten so crowded that the infrastructure is straining under the weight.

## Why the Caps?

Every rupee flowing into a gold ETF through a large direct subscription must eventually be backed by physical gold that the fund house sources and holds. When gold ETF demand was estimated to account for roughly 16% of India's entire gold imports in January alone, the scale of creation-unit activity began to test the operational limits of custodians and authorised participants.

Fund houses publicly cited "operational and regulatory considerations," but the underlying concern is straightforward: sourcing, vaulting, and insuring this much physical gold — while managing the tracking error that investors pay a premium to avoid — becomes exponentially harder when inflows arrive in ₹25-crore-plus blocks from institutional and ultra-high-net-worth buyers.

## The Physical Market Tells a Different Story

While paper gold surges, the physical market is cooling fast. Dealers in Mumbai offered gold at discounts of up to $19 per ounce over official domestic prices this past week — a dramatic swing from premiums of up to $5 just a week earlier.

"Retail buying has slowed, and most transactions are now exchanges of old jewellery for new. As a result, jewellers have little need to replenish inventories by buying gold from banks," a Mumbai-based bullion dealer told Reuters.

Domestic gold prices are hovering around ₹143,000–144,000 per 10 grams, well off the January highs near ₹176,000 but still elevated by historical standards. The 2026 average so far is roughly ₹157,600 — nearly double the 2025 average of ₹82,450 — making India one of the most expensive gold markets in the world relative to purchasing power.

The World Gold Council's assessment is blunt: India's physical gold demand is likely to fall in 2026, following an 11% drop in 2025. Price volatility, rather than price levels alone, is the demand killer. Buyers are waiting for a bigger correction before committing, and jewellers are running down inventory rather than restocking at current levels.

## What NRI Gold Investors Should Consider

**Sovereign Gold Bonds remain the best vehicle.** SGBs offer a 2.5% annual interest coupon on top of gold price appreciation and are exempt from capital gains tax at maturity. For NRIs who can hold to maturity (typically eight years), they combine the gold hedge with a yield that no ETF can match. The catch: new issuance has been sporadic, and secondary-market SGBs often trade at premiums.

**Gold ETF caps hit large allocators hardest.** The ₹25-crore subscription limit is unlikely to affect retail NRI investors, but anyone managing a larger India allocation through gold ETFs will need to split across multiple AMCs or route through the fund-of-funds structure — adding a layer of expense ratio. The ₹10 lakh per PAN per month cap on gold funds-of-funds is more binding for systematic deployment.

**The dollar-rupee angle.** Gold in India is priced in rupees, and the rupee just hit a one-month low near 95.85 per dollar. For NRIs earning in dollars, a weaker rupee inflates the rupee-denominated gold price, making Indian gold more expensive relative to global benchmarks. Conversely, if the rupee stabilises or strengthens — Goldman Sachs recently upgraded its forecast to 94 — the rupee gold price could compress even as international gold holds steady.

**Physical gold discounts signal a buying window.** The $19 per ounce discount is the widest in months and suggests that anyone looking to buy physical gold in India — whether for investment or wedding season ahead — has unusual leverage over dealers right now. That window tends to close quickly when prices stabilise and retail confidence returns.

## The Bigger Pattern

Gold's record run in India is part of a global shift. Central banks bought over 1,180 tonnes of gold in 2025, and the People's Bank of China added 480,000 ounces in June alone, extending its buying streak to 20 months. The de-dollarisation narrative, geopolitical hedging, and the sheer scale of fiscal deficits worldwide have structurally lifted gold demand from institutional buyers.

For Indian retail and NRI investors, the question is no longer whether to hold gold — most already do, and the ETF boom proves the asset class has gone mainstream. The question is at what price and through which vehicle. With fund houses capping subscriptions, physical markets offering discounts, and SGBs providing a yield kicker, the optimal mix is shifting. The smart money isn't chasing the rally — it's positioning for the next correction."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Gold ETF Boom Hits a Wall — Fund Houses Cap Purchases as Physical Demand Cools and Discounts Widen",
    "subheadline": "Gold ETF assets nearly tripled to ₹1.85 lakh crore, but six major AMCs have capped subscriptions. Meanwhile, Mumbai dealers are offering $19-per-ounce discounts. Here's what NRI gold investors should know.",
    "slug": make_slug("india-gold-etf-boom-cap-physical-demand-nri-investors"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI gold investors face a shifting landscape: ETF subscription caps force larger allocators to split across AMCs, Sovereign Gold Bonds remain the best vehicle for tax-efficient exposure, and a weak rupee inflates India gold prices for dollar earners.",
    "tags": ["gold", "etf", "nri-investing", "sovereign-gold-bonds", "mutual-funds", "commodities"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters — Asia Gold", "url": "https://www.reuters.com/markets/commodities/asia-gold-gold-discounts-india-deepen-volatility-hurts-demand-purchases-china-steady-2026-07-10/"},
        {"name": "Equity Research India — Gold ETF AUM Trends", "url": "https://equityresearchindia.com/gold-fund-and-gold-etf-aum-trends/"},
        {"name": "ClearTax — Gold Price History India", "url": "https://cleartax.in/s/gold-price-history-india"},
        {"name": "Reuters — India Gold Premiums", "url": "https://www.reuters.com/markets/commodities/asia-gold-india-gold-premiums-decadal-high-china-demand-undeterred-price-rise-2026-01-24/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Bullion_Gold_bar_at_Swiss_Money_Museum_%28Ank_Kumar%2C_Infosys%29.jpg/1280px-Bullion_Gold_bar_at_Swiss_Money_Museum_%28Ank_Kumar%2C_Infosys%29.jpg",
    "image_caption": "Gold bullion bar at the Swiss Money Museum",
    "image_attribution": "Wikimedia Commons / Ank Kumar, CC BY-SA 4.0",
    "body": art2_body.strip(),
}

# ═══════════════════════════════════════════════════════════════════════
# PUBLISH
# ═══════════════════════════════════════════════════════════════════════

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
