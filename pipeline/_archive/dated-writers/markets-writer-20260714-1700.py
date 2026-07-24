#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-14 17:00 PT run."""

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

# ── ARTICLE 1 ────────────────────────────────────────────────────────────────

art1_headline = "Goldman Sachs Declares Foreign Selling 'Likely Over' — FPIs Pump ₹15,157 Crore Into Indian Equities as the Tide Turns"
art1_subheadline = "After record outflows of $30 billion in just three months, Goldman targets Nifty at 26,500 by mid-2027 and names banks as the top sector pick. For NRI investors who rode out the worst H1 in three decades, the calculus is shifting."

art1_body = """Foreign portfolio investors have turned net buyers of Indian equities in July for the first time since February, pouring in ₹15,157 crore in the first ten days of the month and ending a punishing four-month selling streak that extracted ₹2.6 lakh crore from the market in 2026 alone.

The reversal, confirmed by data from the Central Depository Services (India) Ltd, comes alongside a Goldman Sachs research note that declared foreign selling "likely over" and set a Nifty 50 target of 26,500 by June 2027 — implying roughly 10% upside from current levels around 24,100.

## The Numbers Behind the Exodus

The scale of the exit was historic. In H1 2026, the Nifty posted its worst first-half performance in three decades, falling 9%. India was used as what Goldman described as a "funding market," with global investors liquidating Indian positions to finance bets elsewhere — primarily in U.S. AI stocks and semiconductor plays.

The outflows were staggering: ₹1.17 lakh crore in March, ₹60,847 crore in April, ₹32,963 crore in May, and ₹49,340 crore in June. Total foreign withdrawals in 2026 have already exceeded ₹2.6 lakh crore, surpassing the ₹1.66 lakh crore pulled out in the same period of 2025.

But the tide has turned. Since mid-June, foreign investors have pumped in approximately $2 billion, with most of the buying concentrated in financial stocks. Goldman noted that with foreign positioning now "ultra-light," global funds have substantial room to rebuild Indian exposure.

## Why Goldman Is Turning Constructive

Goldman's thesis rests on three pillars. First, the domestic recovery is becoming visible — inflation remains within the RBI's comfort zone, the rupee has stabilized after touching 94 per dollar post-RBI measures, and corporate earnings are expected to reaccelerate in H2.

Second, valuations have compressed. After months of selling, large-cap Indian stocks are trading at more reasonable multiples relative to their own history and to other emerging markets. Goldman expects investors to rotate from growth to value and from mid-caps (which it considers still expensive) to large-caps.

Third, the brokerage sees banks as the standout opportunity. Having absorbed the heaviest foreign selling, bank valuations have reset to attractive levels. Goldman cited stronger credit growth, healthier asset quality, and improving liquidity conditions as reasons to prefer banks over non-banking financial companies.

J.P. Morgan echoed a similar tone, maintaining a year-end Nifty target of 27,000 — implying 11.5% upside — and pointing to healthy demand, rising GST collections, and resilient nominal GDP as upside risks through the earnings season.

## The Risks That Remain

The optimism comes with caveats. Renewed hostilities between the U.S. and Iran have pushed Brent crude past $87 per barrel, reviving concerns about India's current account deficit and the rupee, which slid past 96 per dollar on Tuesday — less than 1% from its all-time low of 96.96.

Retail inflation ticked up to 4.38% in June, crossing the 4% mark for the first time since January 2025, and raising the prospect of a more cautious RBI. Meanwhile, India's IT sector — where many NRIs hold concentrated positions — continues to face structural headwinds despite a tactical 10.3% July rally.

Goldman itself acknowledged that the earnings downgrade cycle has not fully run its course, and that India's growth-valuation mix remains "less attractive" relative to some markets.

## What This Means for NRI Investors

For the Indian American investor watching from a dual-economy vantage point, the Goldman report carries several actionable signals.

The most immediate: if you stayed invested through the H1 selloff, the worst of the foreign-driven drawdown may be behind you. The ₹15,157 crore July inflow, while modest against the ₹2.6 lakh crore exodus, represents a directional shift that typically accelerates once positioning normalizes.

Banking stocks — HDFC Bank, ICICI Bank, SBI, Axis Bank — are Goldman's highest-conviction play. For NRIs already allocated to Indian financials through mutual funds or direct equity, the current dip in these names may offer an entry point ahead of a potential foreign-flow recovery.

The rotation call — large-cap over mid-cap, value over growth — also deserves attention. Many NRI portfolios are tilted toward mid-cap IT and consumer names that rallied hard in 2023-24 but now trade at stretched valuations. A rebalancing toward large-cap financials and domestic-oriented industrials aligns with where the smart money appears headed.

The rupee remains the wildcard. At 96+ to the dollar, remittance conversions are historically attractive for NRIs sending money home. But the oil-driven pressure means further depreciation is possible, making the timing of any INR-denominated investment a genuine tactical decision.

*Sources: Goldman Sachs Research Note (July 14, 2026), CDSL FPI data, Outlook Business, Reuters, J.P. Morgan India Equity Strategy*"""

art1_sources = json.dumps([
    {"name": "Goldman Sachs Research Note via Outlook Business", "url": "https://www.outlookbusiness.com/markets/fii-flows-to-return-gradually-nifty-to-jump-10-pc-to-26500-pts-by-june-2027-report"},
    {"name": "Outlook Business — FPIs Reverse 4-Month Selling Trend", "url": "https://www.outlookbusiness.com/markets/fpis-reverse-4-month-selling-trend-with-rs-15157-cr-inflow-in-jul"},
    {"name": "Reuters — Indian shares recoup losses on IT stocks", "url": "https://www.reuters.com/markets/asia/indian-shares-fall-middle-east-tensions-flare-again-2026-07-14/"},
    {"name": "Analytics Insight — FPIs Reverse Selling Streak", "url": "https://www.analyticsinsight.net/stock-market/stock-market-update-fpis-reverse-4-month-selling-streak-in-july"}
])

# ── ARTICLE 2 ────────────────────────────────────────────────────────────────

art2_headline = "HCLTech Beats Every Estimate, Then Loses $1.54 Billion in Market Cap — The Guidance Trap Haunting India's IT Sector"
art2_subheadline = "A 20% profit surge, record bookings, and 62% AI revenue growth weren't enough. By holding its FY27 outlook steady, HCLTech handed analysts the one thing they wanted least: uncertainty. The stock fell 4.5%, dragging the entire Nifty with it."

art2_body = """HCL Technologies delivered a textbook earnings beat on Monday — net profit up 20.3% year-on-year to ₹4,624 crore, revenue at ₹34,579 crore (13.9% higher), and net new bookings at a record $2.4 billion. Its advanced AI revenue hit $171 million for the quarter, up 62.1% year-on-year in constant currency.

None of it mattered.

On Tuesday, the stock cratered 4.5%, wiping out ₹14,789 crore ($1.54 billion) in market capitalization. It was the worst performer on the Nifty 50 and the top drag on the benchmark index. The culprit was a single line in the earnings release: HCLTech maintained its FY27 constant-currency revenue growth guidance at 1%–4% and its EBIT margin forecast at 17.5%–18.5%.

## The Market Wanted More — And Didn't Get It

"The expectation was that the management should have increased the guidance with this strong TCV and doubling growth numbers," said Piyush Pandey, senior vice president at Centrum Broking. "Since they have maintained the guidance, it roughly indicates that they do see some sort of muted growth performance in the next few quarters."

J.P. Morgan retained its "underweight" rating on HCLTech, calling the unchanged outlook a reflection of "continued weakness in discretionary technology spending" and pressure in telecom and manufacturing accounts. Jefferies was blunter, calling the steady guidance "the key disappointment" and maintaining its "underperform" rating.

The paradox is striking. HCLTech posted its highest-ever first-quarter bookings. Financial services revenue grew 5.3% year-on-year in constant currency. The U.S. market, which contributes 56% of revenue, expanded 2.9%. And the company's AI practice is growing at triple the pace of its core business.

Yet the market's verdict was unambiguous: growth isn't accelerating fast enough.

## The $315 Billion Question

HCLTech's predicament is not unique — it's a compressed version of the existential challenge facing India's entire $315 billion IT services industry.

AI revenue is growing, but from a small base. HCLTech's $171 million in advanced AI revenue represents roughly 4.7% of its quarterly total. Even at 62% annual growth, AI will not offset the structural deceleration in traditional outsourcing for years. Meanwhile, fears that AI tools will automate the very coding and testing work that built India's IT empire continue to weigh on valuations. Indian IT stocks are collectively down 23% in 2026, even after a tactical 10.3% rally in July.

Chief Executive C. Vijayakumar acknowledged on Monday that the West Asia conflict had created "some impact" and that "softness in discretionary spend persists." Those two words — discretionary spend — have become the sector's defining constraint. As global enterprises tighten budgets and redirect capital toward AI infrastructure, the gap between AI ambition and revenue reality keeps widening.

## The Partnership Play

One bright spot is HCLTech's growing roster of AI partnerships. Last week, LTIMindtree announced a collaboration with Anthropic to deploy Claude AI across enterprises, following similar deals that Anthropic struck with TCS in June and Infosys earlier this year. HCLTech itself partnered with OpenAI in 2025.

The pattern is clear: frontier AI labs are treating India's IT majors as distribution channels for enterprise adoption. Anthropic has called India its "second-largest market" and has opened offices, hired leadership, and expanded partnerships across TCS, Infosys, HCLTech, and now LTIMindtree.

For these firms, the AI partnerships are a lifeline — a way to remain relevant as the technology reshapes their industry. But the market is pricing in a slower transition than bulls hoped for.

## What NRI Investors Should Know

Indian IT stocks sit in a peculiar spot for NRI portfolios. Many Indian Americans work in the same sector — at TCS, Infosys, HCLTech, or their U.S. competitors — and hold these stocks as part of their India allocation. The double exposure (career + portfolio) to a single sector is worth examining.

The HCLTech sell-off, despite objectively strong numbers, illustrates a market that is pricing Indian IT for the AI transition's difficulty, not its promise. The ₹12 per share interim dividend (record date July 17, payable July 27) offers some cushion, but the dividend yield at current prices is modest.

Morgan Stanley described HCLTech's data centre strategy as "bold but time-consuming." Kotak Securities called it "strong execution despite a weak environment" but maintained a "reduce" rating with a ₹1,200 target. The consensus view is that Indian IT is a hold-and-wait story, not a buy-the-dip one.

For NRIs considering fresh exposure, the entry may come later — when guidance actually rises, not when earnings beat lowered bars. The AI revenue trajectory is encouraging, but $171 million per quarter against $3.65 billion in total revenue means the pivot is still in its early chapters.

*Sources: Reuters, HCLTech BSE Filing, J.P. Morgan Research, Jefferies Research, Capital Market, The Hindu BusinessLine*"""

art2_sources = json.dumps([
    {"name": "Reuters — HCLTech wipes $1.54B in market cap", "url": "https://www.reuters.com/technology/indias-hcltech-wipes-154-billion-market-cap-unchanged-outlook-signals-demand-2026-07-15/"},
    {"name": "Reuters — HCLTech beats Q1 revenue estimates", "url": "https://www.reuters.com/technology/indias-hcltech-beats-first-quarter-revenue-estimates-financial-services-strength-2026-07-14/"},
    {"name": "Capital Market — HCL Technologies Q1 profit climbs 20%", "url": "https://www.capitalmarket.com/news/company-news/hcl-technologies-q1-profit-climbs-20-yoy-maintains-revenue-margin-guidance/1405660"},
    {"name": "The Hindu BusinessLine — HCL Tech shares decline on unchanged guidance", "url": "https://www.thehindubusinessline.com/markets/stock-markets/hcl-tech-shares-decline-as-unchanged-fy27-guidance-signals-slower-recovery/article71215823.ece"}
])

# ── BUILD ─────────────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": make_slug("goldman-sachs-fpi-reversal-nifty-26500-nri-banking"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Goldman's call that foreign selling is 'likely over' directly affects NRI equity portfolios tilted toward Indian markets. The banking sector pick, large-cap rotation advice, and rupee at 96+ are all actionable signals for Indian Americans managing dual-economy investments.",
        "tags": ["markets", "FPI", "Goldman Sachs", "Nifty", "banking", "nri-investing", "foreign-investors"],
        "urgency": "high",
        "sources": art1_sources,
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange in Mumbai, where foreign portfolio investors have turned net buyers after months of record selling",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": make_slug("hcltech-loses-market-cap-guidance-trap-nri-it-stocks"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Many Indian Americans work at or invest in India's IT majors. HCLTech's sell-off despite strong results illustrates the AI transition paradox facing the sector — and the double exposure risk for NRIs with career and portfolio concentration in Indian IT.",
        "tags": ["HCLTech", "IT-sector", "earnings", "AI", "nri-investing", "guidance"],
        "urgency": "medium",
        "sources": art2_sources,
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/67/HCL_Tech_Noida_SEZ_Campus.png",
        "image_caption": "HCL Technologies' Noida SEZ campus — the company's stock fell 4.5% despite beating every Q1 estimate",
        "image_attribution": "Wikimedia Commons",
        "body": art2_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
