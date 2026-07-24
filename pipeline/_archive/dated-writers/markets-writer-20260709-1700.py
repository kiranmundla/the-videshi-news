#!/usr/bin/env python3
"""Markets & Finance writer — July 9, 2026 5:00 PM PT run"""
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
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# ── ARTICLE 1: TCS Q1 FY27 Results ──────────────────────────────────

art1_body = """TCS kicked off India's Q1 FY27 earnings season with a beat on Wednesday evening, reporting consolidated revenue of ₹72,275 crore — a 14% year-on-year jump that topped the Street's consensus estimate of ₹72,030 crore. For the roughly 1.4 million Indian IT workers whose career prospects hinge on how the Big Four perform each quarter, and for the tens of thousands of NRI shareholders who hold TCS ADRs on American exchanges, the results offered a dose of cautious optimism in an otherwise nervous market.

Net profit rose 4.6% to ₹13,349 crore, despite a one-time charge tied to the settlement of a long-running IP-theft dispute with DXC Technology. The company declared a dividend of ₹12 per share, with a record date of July 15 and payment scheduled for July 31 — a tangible payout for NRI investors watching their rupee-denominated returns closely as the currency hovers near 95.4 to the dollar.

## AI Revenue Crosses $2.6 Billion

The headline that will matter most to the tech industry: TCS's annualised AI revenue run rate hit $2.6 billion in Q1, a 13.6% sequential increase from $2.3 billion the previous quarter. The company attributed the acceleration to demand for AI-led services across IT operations, software engineering, enterprise modernisation, and what it calls "autonomous business services."

During the quarter, TCS announced strategic partnerships with Anthropic — establishing a dedicated business unit and deploying Claude across 50,000 associates — and with Mistral, becoming the first global systems integrator partner for Mistral Forge. These moves position TCS at the intersection of enterprise AI adoption and the open-vs-proprietary model debate that is reshaping how companies buy and deploy intelligence.

## Banking Drives Growth, But the Order Book Shrank

Revenue growth was led by the banking, financial services, and insurance vertical, where two mega-deal wins from the previous fiscal year began contributing. Sales from this key segment rose 2.4% sequentially. Other notable wins during the quarter included an $800 million enterprise transformation programme with SKF, a multi-million-dollar strategic partnership with ServiceNow, and a contract with a Europe-based Fortune Global 50 company.

But the order pipeline narrowed: total contract value for the quarter came in at $9.5 billion, down from $12 billion in the preceding three months. Analysts at LKP Securities flagged this as a point to watch, noting the results were "marginally better than expected" but cautioning that it remained to be seen "if this is a turnaround or one-off case amid the geopolitical roller-coaster."

## Hiring Restarts After Three Years of Caution

In a signal that may ease anxieties across India's engineering campuses, TCS added roughly 9,300 employees during the quarter — its highest net addition in more than three years. The workforce stood at 593,798 at quarter's end, with trailing twelve-month IT services attrition at 13.6%.

CEO K. Krithivasan told analysts he was "optimistic" about a turnaround in technology spending among manufacturing and life sciences clients in Q2, while noting that recovery in consumer businesses still hinged on geopolitical stability.

## What It Means for NRI Investors

For diaspora investors holding Indian IT stocks — whether directly on the BSE/NSE or through US-listed ADRs — TCS's results set the tone for earnings season. The sector has shed roughly $100 billion in market capitalisation since February, as fears about AI-driven disruption to traditional outsourcing models spooked institutional investors. TCS's demonstration that AI is additive (not substitutive) to revenue could begin to reverse that narrative.

The earnings calendar is stacked: HCLTech reports on July 13, HDFC Bank and ICICI Bank on July 18, and Infosys on July 23. NRI investors with concentrated IT exposure — common among the diaspora, given where many of them work or worked — should watch operating margins closely, as annual salary hikes implemented in April will pressure the bottom line across the sector.

At ₹2,047 per share, TCS closed 0.4% lower ahead of the results announcement. The stock trades at roughly 18.9x forward earnings — below its five-year long-term average — suggesting that if the AI-driven revenue acceleration proves sustainable, there may be a value case for patient capital."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Beats Revenue Estimates as AI Business Crosses $2.6 Billion — What NRI Investors Should Know",
    "subheadline": "India's largest IT exporter posted 14% revenue growth, restarted hiring after three years, and expanded partnerships with Anthropic and Mistral. The dividend cheque lands July 31.",
    "slug": make_slug("tcs-q1-fy27-results-ai-revenue-nri-investors"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "TCS is one of the largest H-1B employers and a cornerstone holding for NRI investors. The $2.6B AI revenue run rate, dividend declaration, and hiring restart all directly impact diaspora portfolios and career prospects.",
    "tags": ["tcs", "q1-results", "indian-it", "ai-revenue", "nri-investing", "earnings-season", "tata-group"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tcs-beats-first-quarter-revenue-view-2026-07-09/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/tcs-q1-results-profit-rises-to-rs-13349-cr-rs-12-per-share-dividend-declared"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/stock-markets/tata-consultancy-service-earnings-tcs-q1-results-today-live-news-updates-09-july-2026/article71200856.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TCS_Gitanjali_Park%2C_Newtown.jpg/1280px-TCS_Gitanjali_Park%2C_Newtown.jpg",
    "image_caption": "TCS Gitanjali Park campus in Kolkata, one of the company's major technology hubs",
    "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
    "body": art1_body,
}

# ── ARTICLE 2: India Real Estate Institutional Investment ────────────

art2_body = """India's real estate sector pulled in $2.68 billion in institutional investment during the second quarter of 2026 — a 90% leap from Q1 and a 49% increase from the same period last year, according to data released this week by Vestian, the Chicago-headquartered workplace solutions firm. More striking than the headline figure was the composition: foreign investors, who had virtually disappeared from the market in Q1, came roaring back with over $1 billion in capital, a staggering 454% quarter-on-quarter surge.

For NRIs who have been eyeing Indian property — whether as a hedge against rupee depreciation, a retirement plan, or simply a way to keep a financial footprint in the country they left — the data suggests that smart institutional money agrees with their instinct. India's real estate is no longer a punt. It's a conviction trade.

## The Numbers That Matter

Cumulative institutional investment in H1 2026 reached $4.1 billion, the highest first-half inflow recorded since the COVID-19 pandemic began reshaping global capital allocation. Domestic investors accounted for 58% of the Q2 total, deploying $1.55 billion — up 363% year-on-year. But the resurgence of foreign capital was the quarter's defining story: international investors contributed 38% of inflows, their highest share in three quarters.

Commercial real estate dominated, absorbing 70% of the total at roughly $1.88 billion. The driver was India's Global Capability Centre boom — multinational corporations expanding their back-office, technology, and analytics operations in Indian cities. GCC occupier demand pushed commercial investment up 67% quarter-on-quarter and 72% year-on-year.

Residential investment nearly doubled sequentially to $400 million, while diversified assets — mixed-use projects spanning commercial, residential, and industrial segments — surged 566% from a low base to $370 million.

## Geography Is Diversifying

The quarter marked a notable shift in where money is landing. Multi-city portfolio transactions accounted for nearly 60% of total inflows, a sign that institutional investors are building diversified exposure rather than concentrating bets. Among individual markets, Chennai led at 16.3%, followed by Bengaluru at 11.3% — a reversal from the historical dominance of Mumbai and Delhi-NCR, which drew just 2.3% and 3.1% respectively.

"India's position as a preferred global real estate investment destination" is strengthening, said Shrinivas Rao, CEO of Vestian. "While commercial assets continue to attract the lion's share of investments on the back of sustained GCC expansion, increased diversification across asset classes reflects growing investor confidence."

## What This Means for NRI Property Buyers

NRIs can purchase residential and commercial property in India under FEMA regulations, though agricultural land and farmhouses remain off-limits. The current data suggests several actionable takeaways:

**Chennai and Bengaluru are the new hotspots.** If you're an NRI who has been defaulting to Mumbai or Gurgaon for property purchases, the institutional capital flow data says reconsider. Chennai's share of investment has nearly quintupled from its historical average, driven by GCC-led office demand that tends to pull up surrounding residential values.

**Commercial may outperform residential.** With 70% of institutional capital targeting office and retail assets, commercial real estate linked to GCC expansion offers potentially stronger rental yields. NRIs looking for income-producing assets rather than speculative appreciation should explore fractional ownership platforms and REITs that provide commercial exposure without the management burden of owning property from abroad.

**The rupee factor matters.** With the dollar-rupee rate hovering near 95.4, every dollar buys roughly 8% more rupee-denominated real estate than it did a year ago. For NRIs earning in dollars, this window of rupee weakness effectively represents a discount on Indian property.

The institutional money is back, it's diversifying, and it's betting on India's structural growth story. For NRIs who have been on the fence, the question is no longer whether India's real estate market deserves a place in their portfolio — but where, and in what form."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Foreign Investors Pour $1 Billion Into Indian Real Estate in Q2 — A 454% Surge That NRIs Should Watch",
    "subheadline": "Institutional investment in Indian property hit $2.68 billion in the April-June quarter, with Chennai and Bengaluru overtaking Mumbai as the top targets. Here's what the data means for diaspora buyers.",
    "slug": make_slug("india-real-estate-q2-2026-foreign-investment-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs are significant property investors in India under FEMA rules. The surge in foreign institutional capital validates India's real estate thesis, while rupee weakness near 95.4/$ offers diaspora buyers an effective discount on INR-denominated assets.",
    "tags": ["real-estate", "nri-investment", "india-property", "foreign-investment", "gcc-expansion", "chennai", "bengaluru"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Vestian Research via Tripura Star News", "url": "https://www.tripurastarnews.com/investments-in-indian-real-estate-diversify-geographically-amid-global-headwinds-vestian/"},
        {"name": "PolicyBazaar", "url": "https://www.policybazaar.com/investment-plans/nri-investment-plans/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/stock-markets/stock-market-live-july-7-2026/article71182120.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/13143008/pexels-photo-13143008.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Mumbai's skyline — India's commercial real estate drew $1.88 billion in institutional investment in Q2 2026",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ── ARTICLE 3: Gold at ₹1.44 Lakh ──────────────────────────────────

art3_body = """Gold touched ₹1.44 lakh per 10 grams on Tuesday — up roughly ₹11,000 since the start of the year — and for NRIs who grew up watching their parents stack gold biscuits in bank lockers, the question is no longer sentimental. It's strategic: at these prices, does gold still make sense as an allocation in a diaspora portfolio, and if so, how should you hold it?

The short answer is that gold remains a core hedge, but the instruments available to NRIs have changed dramatically. The government has effectively closed the door on new Sovereign Gold Bond issuances, secondary-market SGBs are trading at a premium, and the global macro backdrop — with gold at $4,123 per troy ounce internationally — is being shaped by forces that range from central bank hoarding to the fallout from Trump's latest Iran escalation.

## The Price Picture

According to the India Bullion and Jewellers Association, 24-carat gold stood at ₹1,44,782 per 10 grams as of Wednesday, up ₹1,071 on the day. The metal has climbed steadily through 2026 after pulling back from its all-time high of ₹1.76 lakh hit on January 29, when geopolitical turmoil and tariff fears drove a global rush into safe-haven assets.

Silver, by contrast, has been a laggard. At ₹2.27 lakh per kilogram, it's actually down about ₹3,000 from its December 31, 2025 closing price, even as gold has added 8.3% over the same period. Internationally, gold settled at $4,145.30 on Comex on Monday before dipping slightly to $4,123 mid-week, while silver fell 1.6% to $60.93 per ounce.

The divergence matters for NRI investors who may be considering a broader precious metals allocation. Gold's strength is being driven by structural demand — central banks have purchased over 1,000 tonnes annually since 2020, absorbing roughly a quarter of annual mine supply — while silver's performance remains tied more closely to industrial demand cycles.

## The Sovereign Gold Bond Problem

For years, Sovereign Gold Bonds were the gold standard (no pun intended) for Indian gold investment: government-backed, tax-efficient at maturity, and paying 2.5% annual interest on top of any price appreciation. SGBs issued in 2016-17 and 2017-18 have delivered 190-200% returns at redemption.

But the government has stopped issuing new tranches, and the secondary market is now the only game in town. That creates a problem: SGBs on the NSE are trading at roughly ₹11,500 per gram, while MCX gold futures hover near ₹11,000. The premium effectively wipes out several years of the 2.5% coupon, making new purchases less attractive on a risk-adjusted basis.

"Buying SGBs from the secondary market at this juncture might not prove to be fruitful," advised Prathamesh Mallya of Angel One. "At present, SGBs are trading at a premium to gold prices; hence, buying them is not a good option."

## What NRIs Can Actually Do

NRIs looking for gold exposure in 2026 have four realistic options, each with trade-offs:

**Gold ETFs on Indian exchanges** — accessible through a Demat account linked to an NRE or NRO account, these track domestic gold prices without the premium problem plaguing secondary-market SGBs. Expense ratios range from 0.3% to 0.6%, and units can be bought and sold on the NSE/BSE during market hours.

**US-listed gold ETFs** — for NRIs earning in dollars, instruments like GLD or IAU provide gold exposure without currency risk. The tax treatment differs: US-based ETFs are taxed at the collectibles rate (28% for long-term gains), which may be less favourable than Indian capital gains treatment depending on individual circumstances and DTAA applicability.

**Physical gold in India** — still an option, but verify BIS hallmarking and be mindful of making charges, storage costs, and the difficulty of liquidating from abroad. Every gram should carry a Hallmark Unique Identification number.

**Digital gold platforms** — Paytm Gold, PhonePe, and Google Pay offer digital gold purchases in India, typically backed by MMTC-PAMP or Augmont. Minimum purchases can be as low as ₹1, making it accessible, but check platform fees and ensure the provider offers physical delivery or buy-back guarantees.

## The Macro Hedge Argument

The case for gold in a diaspora portfolio isn't about chasing the next ₹10,000 rally. It's about what happens when everything else goes wrong. With the US-Iran situation flaring again, oil prices elevated, and the rupee under pressure, gold serves as a portfolio shock absorber — uncorrelated to equity markets, unaffected by banking crises, and universally liquid.

At ₹1.44 lakh, gold is expensive relative to its own history but cheap relative to the risks it hedges. For NRIs splitting their financial lives between two currencies and two economies, that's a hedge worth having — in the right size, and through the right instrument."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Gold Hits ₹1.44 Lakh, SGBs Are at a Premium, and New Issuances Are Dead — Here's How NRIs Should Buy Gold Now",
    "subheadline": "With 24-carat gold up ₹11,000 in 2026 and Sovereign Gold Bonds no longer being issued, NRI investors need to rethink how they access India's favourite asset class.",
    "slug": make_slug("gold-144-lakh-sgb-premium-nri-investment-options"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "Gold remains culturally and financially significant for NRIs. With SGBs effectively closed to new buyers and secondary-market premiums eroding value, diaspora investors need updated strategies for gold allocation across India and the US.",
    "tags": ["gold", "sovereign-gold-bonds", "nri-investment", "precious-metals", "india-gold-price", "portfolio-strategy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Patna Press / IBJA", "url": "https://www.patnapress.com/gold-rises-to-rs-1-44-lakh-per-10-grams/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/livecoverage/stock-market-today-dow-sp500-nasdaq-live-07-07-2026/card/precious-metals-finish-lower-H9Rd8F2V5u6sQzHvkJTe"},
        {"name": "LiveMint", "url": "https://www.livemint.com/market/commodities/should-you-buy-sovereign-gold-bonds-from-secondary-market-gold-prices-sgb-11735724393367.html"},
        {"name": "Angel One", "url": "https://www.angelone.in/knowledge-center/sovereign-gold-bonds/sovereign-gold-bond-redemption-price"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/346547/pexels-photo-346547.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Gold bars — the metal has climbed ₹11,000 in 2026 to ₹1.44 lakh per 10 grams",
    "image_attribution": "Pexels",
    "body": art3_body,
}

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted to review.")
