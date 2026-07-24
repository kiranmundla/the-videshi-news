#!/usr/bin/env python3
"""Markets & Finance Writer — July 12, 2026 01:00 PT run"""

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

# ─────────────────────────────────────────────────────────────
# ARTICLE 1: India CPI Inflation Expected to Breach 4%
# ─────────────────────────────────────────────────────────────
article1_body = """India's consumer price inflation data, due for release on Monday, July 13, is expected to show that price pressures have breached the Reserve Bank of India's medium-term target of 4% for the first time in 16 months — a development that could reshape the interest-rate calculus for millions of NRI investors with exposure to Indian bonds, fixed deposits, and real estate.

A Reuters poll of 37 economists conducted between July 3 and 9 pegs June's annual CPI inflation at 4.3%, up sharply from 3.93% in May. Estimates range from 3.65% to 5.50%, reflecting deep uncertainty over how multiple inflationary forces will interact. If confirmed, this would be the highest reading since India introduced its revised consumer price index series with a new base year and updated consumption basket earlier this year.

## What's Driving the Spike

Three forces are converging. First, food prices have been firming steadily, with the delayed southwest monsoon raising fears of crop disruption. The India Meteorological Department has flagged El Niño conditions that historically weaken monsoon rainfall and push agricultural prices higher — a pattern that hits vegetable, pulse, and cereal prices hardest.

Second, retail fuel prices remain elevated after state-owned oil marketing companies raised pump prices four times in May, adding roughly ₹3 per litre. With Brent crude still trading near $76 per barrel — and the fragile U.S.-Iran ceasefire leaving energy markets exposed to renewed spikes — transportation and logistics costs continue to feed through to consumer goods.

Third, core inflation, while expected to ease marginally to 3.8% according to Citi Research, remains sticky. "The expected increase is less a reflection of broad-based inflationary pressures and more a consequence of a gradual firming in food, fuel, and select services categories over recent months," noted Kunal Kundu, India economist at Société Générale.

## The RBI's Dilemma

The Reserve Bank held its key policy rate unchanged at 5.25% at its June meeting, but the monetary policy committee faces an increasingly uncomfortable balancing act. The central bank had been expected by many to cut rates further after slashing them by 125 basis points since February 2025. A breach of the 4% target complicates that narrative.

ING economists Deepali Bhargava and Lynn Song project CPI at 4.2% and warned that "persistent retail fuel costs, gradually firming food inflation, and sticky core pressures point to a mild uptick in consumer inflation," with risks "tilted to the upside" over the coming months.

Yet bond markets tell a different story. The 10-year government bond yield has fallen for six consecutive weeks to 6.71%, shedding 34 basis points as foreign investors have piled in — betting that Indian bonds may soon be added to the Bloomberg Global Aggregate Index. Five-year overnight index swap rates have plunged to 6.1%, just 10 basis points above pre-Iran-war levels, after a record $2.65 billion day of swap trading as investors aggressively unwound rate-hike bets.

## What This Means for NRI Investors

For NRIs with money parked in Indian fixed deposits, the inflation print matters directly. Banks have been competing fiercely for NRI deposits — AU Small Finance Bank recently hiked its FCNR (USD) deposit rate from 5.15% to 7.10%, and major banks have followed with their own increases. If inflation stays above 4%, the RBI is unlikely to cut rates further, keeping deposit rates attractive.

For those invested in Indian bonds or bond mutual funds, the tension between inflation and foreign inflows creates a complex picture. ANZ Research's Dhiraj Nim noted that second-quarter inflation is "tracking below the Reserve Bank of India's forecast from its June meeting, supporting a patient approach to monetary policy." But a surprise above 4.5% could trigger a sharp repricing.

The rupee, currently at 95.32 per dollar after recovering from its record low of 96.96 in May, adds another variable. Goldman Sachs recently upgraded its rupee forecast to 94, but renewed Middle East tensions and an upside inflation surprise could reverse that trajectory — affecting remittance values in both directions.

Investors with dual-economy exposure should watch Monday's number closely. A print at or below 4.2% would reinforce the "patient RBI" narrative and keep bond rally hopes alive. Anything above 4.5% reopens the rate-hike debate that markets had just begun to put behind them."""

article1_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-consumer-inflation-likely-topped-rbis-4-target-june-2026-07-09/"},
    {"name": "ING Economics", "url": "https://www.fxstreet.com/news/india-inflation-risks-stay-skewed-higher-ing-202607110400"},
    {"name": "ANZ Research / Wall Street Journal", "url": "https://www.wsj.com/livecoverage/stock-market-today-dow-sp500-nasdaq-live-07-10-2026"},
    {"name": "Société Générale", "url": "https://www.reuters.com/world/india/india-consumer-inflation-likely-topped-rbis-4-target-june-2026-07-09/"}
])

# ─────────────────────────────────────────────────────────────
# ARTICLE 2: SK Hynix Nasdaq Debut & India AI Angle
# ─────────────────────────────────────────────────────────────
article2_body = """South Korean memory chipmaker SK Hynix made its debut on the Nasdaq on Friday in the largest-ever U.S. stock listing by a foreign company, raising $26.5 billion in a sale that was oversubscribed seven to eight times over. American depositary shares priced at $149 opened at $170 and surged as much as 15% in early trading, sending a clear signal: institutional investors believe the AI memory supercycle is far from exhausted.

For NRI tech investors, the listing opens a direct pathway to the AI hardware boom that has, until now, been dominated by a handful of U.S. names — Nvidia, Broadcom, and Micron. SK Hynix commands roughly 32% of the global DRAM market and an estimated 57% of the high-bandwidth memory (HBM) market, the specialized chips that power Nvidia's AI training accelerators. If you own Nvidia, you are already betting on SK Hynix's supply chain. Now you can own both sides of the trade.

## Why This Matters Beyond Korea

The sheer scale of the offering — third-largest IPO in history behind Saudi Aramco and SpaceX — validates the thesis that AI infrastructure spending is structural, not cyclical. SK Hynix plans to use the proceeds to build two new fabrication plants in South Korea, expand HBM production capacity, and invest in next-generation packaging technology.

This is the same thesis playing out across India's technology ecosystem. TCS reported just days ago that its annualised AI revenue run rate had crossed $2.6 billion, a 13.6% sequential increase, with CEO K. Krithivasan noting that enterprises are accelerating investments in AI modernization, cybersecurity, and sovereign cloud. The company added 9,279 employees in the June quarter — its strongest quarterly hiring in three years — suggesting that AI is creating jobs faster than it eliminates them, at least in the services layer.

The demand chain extends further. At least 10 fund managers, including ProShares and Direxion, have already filed to list single-stock leveraged and inverse ETFs tracking SK Hynix's ADRs, a sign of the derivative infrastructure that will build around this listing. For NRI investors accustomed to accessing AI through U.S.-listed tech ETFs, SK Hynix adds a new dimension: pure-play exposure to the memory layer of the AI stack, which analysts at Jupiter Asset Management say should trade at least on par with Micron's valuation — implying significant upside from current levels.

## India's Semiconductor Ambitions in Context

The timing of SK Hynix's debut coincides with an acceleration in India's own semiconductor push. Tata Electronics broke ground on its $11 billion fabrication plant in Gujarat with Taiwan's PSMC as technology partner. Adani Group signed a partnership with American engineering firm Jabil to build AI infrastructure domestically. Meta and Reliance Industries are expanding their partnership with plans for AI-enabled data centers.

These projects are years from producing chips at scale, but they represent a strategic bet that India can capture a piece of the semiconductor supply chain that has historically been monopolised by Taiwan, South Korea, and increasingly the United States. For diaspora investors watching the AI buildout from both sides of the Pacific, the question is no longer whether to have semiconductor exposure, but how much and through which vehicles.

## The Valuation Puzzle

SK Hynix shares have risen 630% over the past year on the Korea Exchange, driven by insatiable demand for HBM chips. Yet the stock still trades at a forward price-to-earnings discount to Micron, its closest U.S. peer. Sam Konrad, investment manager for Asia equity income at Jupiter Asset Management, told Reuters that the ADR listing "could help re-rate the Korean-listed SK Hynix shares."

However, the semiconductor cycle has historically been brutal. Memory prices are notoriously volatile, and the massive capital expenditure plans announced by both SK Hynix and Samsung have fuelled concerns about future oversupply. The stock has already dropped from a recent high — falling 6% on Tuesday and another 6% on Wednesday before recovering — tracking a broader technology selloff driven by worries about the sustainability of AI spending.

## NRI Portfolio Implications

For NRI tech investors, the listing creates a clear decision framework. If you believe AI infrastructure spending will remain elevated for three to five years — driven by enterprise adoption, sovereign AI initiatives, and the proliferation of AI agents across industries — SK Hynix offers direct exposure to the physical layer that makes it all possible, at a valuation discount to U.S. peers.

India's IT services sector — TCS, Infosys, Wipro, HCLTech — captures the services and integration layer of the same cycle. Owning both gives NRI portfolios exposure across the AI value chain: from the silicon that trains the models to the consultants who deploy them.

The risk is that AI spending decelerates faster than expected, memory prices crater, and the capex cycle turns into a glut. For investors who lived through the 2022 semiconductor downturn, that scenario is not academic. But with SK Hynix's Nasdaq debut drawing the kind of institutional demand that hasn't been seen since Alibaba's 2014 listing, the market is pricing in a very different outcome."""

article2_sources = json.dumps([
    {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynixs-us-listing-sparks-rush-single-stock-etf-filings-2026-07-10/"},
    {"name": "Fast Company", "url": "https://www.fastcompany.com/91363850/sk-hynix-ipo-today-stock-price-skhyv"},
    {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/stocks/sk-hynix-to-debut-on-wall-street-after-biggest-share-sale-by-foreign-company-c9f8c62b"},
    {"name": "Reuters — TCS Q1 Results", "url": "https://www.reuters.com/technology/indias-tcs-up-ai-momentum-fuels-revenue-beat-2026-07-11/"}
])

# ─────────────────────────────────────────────────────────────
# Build articles array
# ─────────────────────────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's June Inflation Data Arrives Monday — CPI Expected to Breach 4% for the First Time in 16 Months, and NRI Portfolios Are in the Crosshairs",
        "subheadline": "A Reuters poll of 37 economists pegs June CPI at 4.3%, driven by food and fuel prices, El Niño fears, and Iran-war energy risks — with direct implications for RBI rate decisions, bond yields, and NRI deposit rates.",
        "slug": make_slug("india-june-cpi-inflation-breach-4-percent-rbi-nri-deposits-bonds"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI investors with Indian fixed deposits, bond funds, and real estate exposure face a direct impact from the inflation print. A breach of 4% keeps deposit rates elevated but could halt the bond rally that foreign investors have been riding. Remittance values hinge on whether the rupee, currently at 95.32, holds or weakens on an inflation surprise.",
        "tags": ["markets", "finance", "inflation", "rbi", "nri-investing", "bonds", "fixed-deposits", "rupee"],
        "urgency": "high",
        "sources": article1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg",
        "image_caption": "The Reserve Bank of India headquarters in Mumbai, where monetary policy decisions shape NRI investment returns",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SK Hynix's Record $26.5 Billion Nasdaq Debut Signals the AI Memory Supercycle Is Far From Over — Here's What NRI Tech Investors Should Know",
        "subheadline": "The South Korean chipmaker's largest-ever foreign listing on Wall Street — oversubscribed 7x, with shares surging 15% on day one — opens a new AI hardware play for diaspora investors already riding India's $2.6 billion TCS AI wave.",
        "slug": make_slug("sk-hynix-nasdaq-debut-ai-memory-nri-tech-india-semiconductor"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI tech investors now have direct Nasdaq access to the AI memory chip boom through SK Hynix ADRs, complementing their India IT services exposure via TCS and Infosys. India's own semiconductor ambitions — Tata's Gujarat fab, Adani-Jabil AI infrastructure — position the diaspora to invest across the entire AI value chain from both sides of the Pacific.",
        "tags": ["markets", "finance", "semiconductors", "ai", "sk-hynix", "nasdaq", "tcs", "nri-investing", "india-tech"],
        "urgency": "medium",
        "sources": article2_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Memory semiconductor chips like those made by SK Hynix are the physical foundation of the AI infrastructure boom",
        "image_attribution": "Pexels",
        "body": article2_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
