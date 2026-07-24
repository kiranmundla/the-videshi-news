#!/usr/bin/env python3
"""Markets & Finance Writer — 2026-07-11 09:00 PT"""

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

# ────────────────────────────────────────────
# ARTICLE 1: UPI's Global Expansion
# ────────────────────────────────────────────

upi_body = """India's Unified Payments Interface is no longer just an Indian phenomenon. Over the past year, the payment rail that processes over 21 billion monthly transactions domestically has been aggressively expanding its footprint abroad — and the latest push could reshape how NRIs move money across borders.

## Indonesia Deal Marks a Southeast Asian Breakthrough

Speaking during a bilateral meeting in early July, Prime Minister Narendra Modi announced that India's UPI would be integrated with Indonesia's national payment system. The move targets the world's fourth-most-populous nation and the largest economy in Southeast Asia, opening a corridor that could serve both India's growing trade relationship with Jakarta and the roughly 120,000 Indians living and working in Indonesia.

The Indonesia integration follows a proven playbook. UPI is already operational in eight countries — Singapore, Bhutan, Nepal, Qatar, Mauritius, the UAE, Sri Lanka, and France — with live QR-code-based merchant payments enabling Indian travellers to pay at shops and restaurants using familiar apps like PhonePe and Google Pay. Singapore remains the most advanced corridor, with peer-to-peer transfers now functional.

## Europe Is the Prize

The most consequential linkage under negotiation is with the European Central Bank. The Reserve Bank of India and the ECB have entered what NPCI International Payments describes as the "realisation phase" of connecting UPI with TIPS, Europe's instant payments settlement system. If completed, this would give Indian students in Germany, tourists in Italy, and business travellers across the eurozone the ability to pay via UPI — and, crucially, it would open a direct remittance corridor that bypasses the expensive SWIFT-based wire transfer system that most NRIs currently rely on.

The India-Europe corridor handles an estimated $8–10 billion in annual remittances. Even a partial shift to UPI rails could compress costs from the current 3–5% per transaction to under 1%, a meaningful saving for NRIs remitting monthly.

## Central Asia and Malaysia Expanding the Map

Beyond the headline deals, quieter expansions are underway. PayU's partnership with 8B is integrating UPI, net banking, and card payments into merchant networks across Kazakhstan, Uzbekistan, and Kyrgyzstan — driven by the surge in Indian tourists to Central Asia, which has benefited from visa-free access and improved air connectivity.

In Malaysia, Razorpay's Curlec unit is enabling UPI acceptance for Indian visitors, tapping into the RM 6.11 billion ($1.3 billion) that Indian tourists spend annually in the country. The linkage with Malaysia's PayNet network will eventually be bidirectional, allowing Malaysian visitors to pay at Indian merchant points using DuitNow QR.

## The 20-Country Roadmap

According to the RBI's annual report, the central bank and NPCI International are working to extend UPI to 20 countries by FY29. Beyond the corridors already live or in negotiation, discussions are underway with central banks across SAARC nations, East Asia, and additional Gulf states.

The global UPI push dovetails with India's diplomatic fintech strategy. At the India AI Impact Summit earlier this year, NPCI launched its "One World" digital wallet — a prepaid instrument that allows foreign visitors to load international cards and make UPI payments across India. The wallet signals an ambition to make UPI not just an export product but a two-way platform.

## What NRIs Should Watch

For the diaspora, UPI's international expansion matters in three ways. First, remittance costs: direct UPI-to-local-payment linkages could dramatically undercut the fees charged by Western Union, Wise, and traditional bank wires on high-volume corridors like US-India and UK-India. Second, travel convenience: NRIs visiting India already use UPI extensively; the reverse — using it abroad — eliminates the need for foreign currency exchange and international card swipes. Third, competition: as UPI enters corridors dominated by Visa and Mastercard, merchant discount rates in those markets could decline, benefiting Indian businesses and consumers on both sides.

The infrastructure is moving faster than the regulatory harmonisation. FX conversion rules, transaction limits, and anti-money-laundering compliance still vary country by country. But the direction is clear: India is building a payments rail that could, by the end of the decade, function as a de facto global standard for real-time, low-cost, mobile-first transactions — with NRIs as its most natural early adopters."""

upi_sources = [
    {"name": "The Indian Eye", "url": "https://theindianeye.com/indias-upi-to-integrate-with-indonesias-payment-system-says-pm-modi/"},
    {"name": "Finextra", "url": "https://www.finextra.com/blogposting/27533/upi-is-plotting-something-big-9-countries-in-talks---whats-india-really-planning-for-2026"},
    {"name": "Reserve Bank of India Annual Report", "url": "https://www.livemint.com/news/india/rbi-and-npci-working-to-expand-upi-to-20-countries-by-2029-shows-central-bank-s-annual-report-11727088907747.html"},
    {"name": "Angel One", "url": "https://www.angelone.in/news/upi-goes-global-indian-travellers-to-pay-seamlessly-across-central-asia-soon"}
]

# ────────────────────────────────────────────
# ARTICLE 2: India Inc Revenue at 2-Year High
# ────────────────────────────────────────────

india_inc_body = """India's corporate sector is delivering its strongest revenue growth in two years — but the engine driving the numbers has quietly shifted, and the implications for NRI equity investors are worth parsing carefully.

## The Numbers: 11–11.5% Revenue Growth Across 400 Companies

A Crisil Intelligence analysis of 400 companies spanning 47 sectors (excluding banking, financial services, and oil and gas) projects aggregate revenue growth of 11–11.5% year-on-year in the June quarter of FY27. That would be the fastest clip since mid-2024, when post-pandemic pent-up demand was still fuelling topline expansion.

The headline is impressive given the backdrop. The West Asia conflict, which escalated sharply after the U.S.-Iran exchange of strikes in February, has disrupted supply chains, pushed up shipping costs, and sent Brent crude on a volatile ride between $68 and $79 a barrel. India imports 89% of its crude oil requirements, with 46% routed through the Strait of Hormuz — making it acutely vulnerable to the kind of disruptions that have played out over the past four months.

## The Catch: Pricing, Not Volume, Is Doing the Heavy Lifting

For much of the past two years, India Inc.'s revenue growth was powered primarily by volume — more cars sold, more cement poured, more telecom subscribers added. This quarter marks a structural shift.

"Pricing was the primary driver, contributing more to revenue growth than volume in sectors such as aluminium, steel, cement, airlines, fertilisers and gems and jewellery," said Sehul Bhatt, director of Crisil Intelligence. In plain terms, companies are charging more per unit rather than selling more units.

This distinction matters for investors. Volume-driven growth tends to be more durable because it reflects genuine demand expansion. Price-driven growth can evaporate quickly if input costs normalise or if consumers resist further hikes. It also compresses demand at the margin — the very dynamic that rating agency ICRA has flagged as a risk for the current quarter.

## Sector Leaders: Auto Is the Standout

The automobile sector is the strongest contributor, with revenue growth projected at 22–24% year-on-year. Passenger vehicle sales rose 25%, commercial vehicle sales climbed 15%, and automotive exports surged an estimated 19–21% on strong demand from Japan and Africa. The sector has benefited from GST rate reductions of 8–13% that boosted sales volumes.

White goods, telecom services, power generation, and parts of healthcare also drew support from healthy domestic demand, according to the Crisil report. But the growth has not been uniform — textiles and apparel exporters, unsecured retail lenders, commodity chemical makers, and generic drug manufacturers continued to report contraction, weighed down by weak global demand and Chinese dumping pressures.

## The Margin Warning

Revenue growth, however, is only half the picture. ICRA expects operating profit margins to contract by 100–150 basis points in Q1 FY27 as companies absorb higher fuel, logistics, packaging, and imported input costs that they cannot fully pass on to consumers. Interest coverage ratios — a key measure of a company's ability to service debt from operating earnings — are projected to decline to 4.8–5.0 times, down from 5.8 times in the March quarter.

Kotak Institutional Equities framed it bluntly: "Q4 FY26 results were decent, but Q1 FY27 could be bumpy." The brokerage warned that a prolonged West Asia crisis could result in a "deeper negative impact on both the economy and earnings," while a swift resolution would limit the damage.

## What This Means for NRI Portfolios

J.P. Morgan has reiterated its year-end Nifty target of 27,000 — implying 11.5% upside from Friday's close of 24,207 — arguing that the biggest upside risk comes from revenue growth supported by healthy demand, strong credit expansion, rising GST collections, and resilient nominal GDP.

But NRI investors should look beneath the headline. The price-over-volume dynamic means topline growth could decelerate sharply if input costs ease and companies can no longer justify premium pricing. Meanwhile, the sectors delivering genuine demand-led growth — autos, telecom, power — are already trading at elevated multiples.

The broadest mid-caps and small-caps rose 1.4% and 1.3% respectively on Friday, trimming weekly losses. But nine of 16 major sectors logged weekly declines, a reminder that the rally is narrow rather than broad-based.

For the NRI investor running a diversified India portfolio, the Q1 earnings season — with TCS already reporting a revenue beat and rising AI-linked sales — is the next catalyst. The sector-level divergence means stock selection matters far more than index-level allocation this quarter. Watch autos and IT for upside, and tread carefully in commodities and generic pharma, where the pricing tailwind could reverse before volume catches up."""

india_inc_sources = [
    {"name": "Outlook Business / PTI", "url": "https://www.outlookbusiness.com/news/india-inc-revenues-set-to-grow-at-two-year-high-in-q1-despite-west-asia-tensions-report"},
    {"name": "DevDiscourse / Crisil", "url": "https://www.devdiscourse.com/article/business/3406051-indias-auto-sector-drives-corporate-revenue-surge-in-q1-fy27"},
    {"name": "The Hindu BusinessLine / ICRA", "url": "https://www.thehindubusinessline.com/markets/west-asia-conflict-el-nio-threat-to-hit-india-inc-earnings-in-q1-says-icra/article69234142.ece"},
    {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-shares-set-rise-softer-crude-tcs-boost-2026-07-11/"}
]

# ────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India's UPI Goes Global — Indonesia Integration, ECB Linkage, and a 20-Country Roadmap That Could Reshape How NRIs Move Money",
        "subheadline": "From Southeast Asia to Europe, India's payment rail is building cross-border corridors that could slash remittance costs and challenge Visa-Mastercard dominance — and the diaspora stands to benefit most.",
        "slug": make_slug("india-upi-global-expansion-indonesia-ecb-nri-remittance"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "UPI's international expansion directly impacts NRIs through cheaper remittances, seamless travel payments, and new cross-border money corridors — potentially cutting transfer costs from 3-5% to under 1% on major diaspora corridors.",
        "tags": ["upi", "digital-payments", "fintech", "nri-remittance", "india-indonesia", "npci", "cross-border-payments"],
        "urgency": "medium",
        "sources": json.dumps(upi_sources),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935051/pexels-photo-12935051.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A contactless QR code payment transaction at a retail point of sale",
        "image_attribution": "Pexels",
        "body": upi_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Inc. Revenue Growth Hits a Two-Year High at 11.5% — But It's Pricing, Not Demand, Doing the Heavy Lifting",
        "subheadline": "A Crisil analysis of 400 companies shows the strongest quarterly topline growth since mid-2024, led by autos at 22-24%. The catch: margins are under pressure, and the price-over-volume dynamic could reverse quickly.",
        "slug": make_slug("india-inc-q1-revenue-two-year-high-pricing-volume-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI equity investors need to look beneath the headline revenue growth — the shift from volume to pricing-driven expansion means sector selection matters more than ever, with autos and IT leading genuine demand while commodity and pharma stocks face reversal risk.",
        "tags": ["india-inc", "q1-fy27", "earnings", "crisil", "auto-sector", "nri-investing", "equity-markets"],
        "urgency": "medium",
        "sources": json.dumps(india_inc_sources),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange building in Mumbai, India's oldest stock exchange",
        "image_attribution": "Wikimedia Commons",
        "body": india_inc_body
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
