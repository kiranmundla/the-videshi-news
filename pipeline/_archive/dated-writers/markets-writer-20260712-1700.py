#!/usr/bin/env python3
"""Markets & Finance Writer — 2026-07-12 17:00 PT"""
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


# ─── ARTICLE 1: HCLTech $1.1B AI Deal + Earnings Week ───
art1_body = """HCLTech, India's third-largest IT services company, walks into its Q1 FY27 earnings announcement on July 13 carrying an unusual tailwind: a $1.14 billion artificial intelligence-led transformation deal with a Europe-headquartered Fortune Global 50 company, announced just ten days earlier. The contract, running from July 2026 through December 2031 with an optional five-year extension, sent HCLTech shares surging 5.7% in a single session — recovering 10% from a fresh 52-week low of ₹1,030 hit just two days prior.

For NRI investors holding Indian IT exposure through direct equity or mutual funds, the timing creates a rare convergence: a mega deal announcement landing right before a results cycle that will set the tone for the entire sector.

## What the $1.14 Billion Deal Actually Means

HCLTech will build and manage an AI-driven operating model covering the client's global digital workplace and enterprise networks. This is not a one-off consulting engagement — it is a multi-year infrastructure takeover where HCLTech deploys automation, predictive analytics, and AI agents to run the client's technology backbone.

At roughly $200 million in annualized revenue, the contract represents about 1.4% of HCLTech's $14.66 billion FY26 top line. That sounds modest, but the strategic significance runs deeper. Large outsourcing deals provide multi-year revenue visibility during a period when discretionary IT spending remains frozen across the industry.

HCLTech's Advanced AI revenue already hit $620 million on an annualized basis in Q4 FY26, growing 6.1% sequentially. The new deal embeds AI inside a long-duration enterprise programme rather than selling it as a standalone product — exactly the kind of commercial model Wall Street and Dalal Street have been looking for.

The catch: Q1 results will not reflect any material revenue contribution from the deal, which starts in July. Investors will instead scrutinize constant-currency growth, HCLSoftware performance (which declined 14.1% year-on-year last quarter), and whether management narrows its cautious 1%–4% FY27 revenue growth guidance.

## The Mega Earnings Week Ahead

HCLTech is just the opening act. The week of July 13–18 is the most consequential earnings stretch NRI investors will see this quarter:

- **July 13**: HCLTech, ICICI AMC
- **July 15**: Angel One, HDB Financial Services, HDFC AMC
- **July 18**: Axis Bank, HDFC Bank, ICICI Bank, India Cements

The July 18 trio — HDFC Bank, ICICI Bank, and Axis Bank — matters enormously. These three private-sector lenders collectively dominate NRI investment portfolios, whether through NRE-linked SIPs, direct stock holdings, or banking ETFs.

Motilal Oswal Financial Services projects private banks will deliver earnings growth of around 20% CAGR through FY28, outpacing public sector banks at roughly 15%. But the near-term picture is less rosy: net interest margins face pressure in Q1 as lending rates have held steady while earlier rate cuts compress yields. The CASA ratio is declining across the industry, pushing up deposit costs.

## What NRI Investors Should Watch

**TCS set the bar.** Its Q1 revenue beat with AI-linked sales crossing $2.6 billion lifted the entire IT index 2% on Friday. If HCLTech delivers a similar narrative — deal momentum, AI commercialization, stable margins — the sector could sustain its July rebound.

**Banking earnings will drive the Nifty.** J.P. Morgan has reiterated its year-end Nifty target of 27,000, implying 11.5% upside from the July 11 close of 24,207. That target rests heavily on earnings acceleration from India's banking heavyweights.

**Infosys on July 23 completes the IT picture.** Along with Dr. Reddy's and Nestlé India, the last week of July will reveal whether the Q1 earnings season validates the market's constructive stance or forces a correction.

The Nifty snapped a four-week winning streak last week with a 0.3% loss, rattled by the U.S.-Iran flare-up and a spike in crude prices. But the recovery on Friday — Sensex up 827 points to 77,569 — suggests buyers remain willing to step in on dips. For NRI investors with rupee-denominated portfolios, this earnings season is the moment that determines whether J.P. Morgan's optimism holds or the 24,500 resistance becomes a ceiling."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "HCLTech's $1.1 Billion AI Deal Sets the Stage for a Mega Earnings Week — Here's What NRI Investors Should Watch",
    "subheadline": "India's third-largest IT firm reports Monday with a Fortune 50 mega-contract in hand, kicking off a week that includes HDFC Bank, ICICI Bank, and Axis Bank results — and could define Q1 for NRI portfolios.",
    "slug": make_slug("hcltech-1-billion-ai-deal-mega-earnings-week-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI investors hold significant IT and banking exposure through direct equity, mutual funds, and NRE-linked SIPs — this earnings week will determine near-term returns on rupee-denominated portfolios and signal whether the Nifty's bullish thesis holds.",
    "tags": ["markets", "finance", "hcltech", "earnings", "nri-investing", "indian-it", "banking", "nifty", "ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Business News Today", "url": "https://business-news-today.com/hcltech-nse-hcltech-jumps-5-7-on-1-1bn-ai-deal-before-q1-results/"},
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-shares-rise-tcs-boost-snap-weekly-winning-run-mideast-worries-2026-07-10/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/stock-market-highlights-markets-end-in-green-sensex-gains-827-pts-nifty-closes-at-24207/article69789123.ece"},
        {"name": "Motilal Oswal Financial Services (via DevDiscourse)", "url": "https://www.devdiscourse.com/article/business/3394523-private-banks-to-outperform-psu-banks-in-earnings-growth-during-fy26-28-mofs"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/67/HCL_Tech_Noida_SEZ_Campus.png",
    "image_caption": "HCLTech's SEZ campus in Noida, the company's headquarters",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ─── ARTICLE 2: India Millionaire Migration ───
art2_body = """One in five ultra-high-net-worth Indians is either actively migrating abroad or planning to do so — and most intend to settle permanently while retaining their Indian citizenship. That is the headline finding from a new Kotak Bank report on India's ultra-rich, released alongside updated Henley & Partners data showing India now ranks third globally in millionaire outflows, behind China and the United Kingdom.

The numbers tell two stories at once. India is bleeding wealthy residents at scale, with approximately 4,300 millionaires projected to leave this year and 3,500 expected in 2025. But it is also minting new ones faster than any major economy, with wealth among India's high-net-worth population growing 85% over the past decade.

For the 32 million Non-Resident Indians and Persons of Indian Origin scattered across the globe, this trend is not an abstraction — it is reshaping the financial infrastructure, wealth management industry, and regulatory landscape that NRIs navigate daily.

## Who Is Leaving, and Where Are They Going?

The Kotak report reveals that professionals show a higher tendency to migrate than entrepreneurs or inheritors. Two age cohorts dominate: the 36-to-40 bracket, typically mid-career executives seeking better quality of life for young families, and those above 61, retirees looking for superior healthcare and lower tax burdens.

The UAE has cemented its position as the world's top wealth magnet, expecting a record net inflow of 6,700 millionaires this year — nearly double the United States' projected intake of 3,800. The pull factors are blunt: zero income tax, golden visa programmes, luxury infrastructure, and a strategic location between European and Asian time zones.

Dubai's rental yields of 7% to 11% dwarf the 2% to 5% returns typical in Indian metropolitan cities, making Gulf real estate a dual-purpose play for wealthy Indians — residency pathway and investment vehicle rolled into one.

Singapore, meanwhile, attracts the tech-oriented Ultra-HNI with its robust legal framework, family office ecosystem, and 17% top marginal tax rate — a fraction of India's 42%-plus effective rate for top earners.

## The Wealth Pipeline Is Not Shrinking

Here is what makes India's millionaire exodus different from China's or the UK's: the domestic wealth engine is accelerating faster than the outflow.

India's Ultra-HNI population is projected to reach 4.3 lakh by 2028, with aggregate wealth hitting ₹359 trillion. Nearly one-third of India's ultra-rich already hold global assets, with residential real estate abroad as the dominant allocation — a trend that will only intensify as migration plans crystallize into property purchases.

"While India loses thousands of millionaires each year, with many migrating to the UAE, concerns over the outflows may well be mitigated," the Henley report noted, pointing out that India "continues to produce far newer high-net-worth individuals than it loses to emigration."

The Ministry of External Affairs estimates over 2.5 million Indians migrate to other countries every year — a flow that feeds the NRI ecosystem with fresh capital, new compliance needs, and expanding demand for cross-border financial products.

## What This Means for NRI Investors

**Indian private banks are following the money.** Nuvama Private, LGT Wealth Management, and other platforms are expanding into the UAE to serve Indian families who want seamless advisory across jurisdictions. This trend will accelerate, creating both competition and better service for NRIs already managing money across India and their country of residence.

**FEMA compliance is getting more complex.** The intersection of golden visa residency, Indian citizenship retention, NRE/NRO account management, and cross-border tax obligations requires increasingly sophisticated planning. The new Form 145 and Form 146 remittance protocol, replacing the legacy Form 15CA and 15CB framework, adds another compliance layer for NRIs repatriating property sale proceeds or investment income.

**Real estate remains the anchor asset.** With one-third of India's ultra-rich holding global property and the pipeline of future NRIs skewing toward permanent overseas residency, NRI demand for both Indian real estate (as a homeland hedge) and foreign property (as a migration asset) will continue to grow. Mumbai, Dubai, London, and Singapore remain the top four markets.

**The NRI wealth management market is still early innings.** India's wealth growth trajectory means the diaspora will keep expanding — not just in population but in financial complexity. The Ultra-HNIs leaving today are becoming tomorrow's NRIs, carrying ₹359 trillion in projected wealth into a cross-border financial system that is only beginning to adapt."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "One in Five Ultra-Rich Indians Are Planning to Move Abroad — And It's Quietly Reshaping the NRI Financial Landscape",
    "subheadline": "A new Kotak Bank report reveals that 20% of India's ultra-high-net-worth individuals are migrating permanently while retaining citizenship, as India ranks third globally in millionaire outflows — behind China and the UK.",
    "slug": make_slug("ultra-rich-indians-migrating-abroad-nri-wealth-landscape"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "The Ultra-HNIs leaving India today are becoming tomorrow's NRIs — reshaping wealth management demand, FEMA compliance complexity, and cross-border financial infrastructure that all 32 million diaspora members navigate.",
    "tags": ["markets", "finance", "nri-investing", "wealth-management", "hni-migration", "uae", "real-estate", "fema"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian Eye (Kotak Report)", "url": "https://theindianeye.com/20-of-ultra-rich-indians-plans-to-settle-abroad-while-retaining-citizenship/"},
        {"name": "The Indian Eye (Henley Report)", "url": "https://theindianeye.com/millionaire-migration-india-is-expected-to-rank-third-globally-following-china-and-uk/"},
        {"name": "Henley & Partners", "url": "https://www.henleyglobal.com/publications/henley-private-wealth-migration-report-2024"},
        {"name": "Cbonds (Henley Migration 2025)", "url": "https://cbonds.com/news/3378041/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Dubai_Marina_At_Night_%28251388905%29.jpeg/1280px-Dubai_Marina_At_Night_%28251388905%29.jpeg",
    "image_caption": "Dubai Marina at night — the UAE has become the world's top destination for migrating millionaires",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
