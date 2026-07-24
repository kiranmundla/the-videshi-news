#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-13 01:00 PDT run."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / "workspace" / ".env.supabase"
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

# ---------------------------------------------------------------------------
# ARTICLE 1: NSE IPO Roadshow
# ---------------------------------------------------------------------------
art1_body = """India's National Stock Exchange — the country's largest bourse and the world's most active derivatives exchange — is about to pitch itself to more than 30 global institutional investors as it prepares for what could be one of the largest initial public offerings in Indian corporate history.

## A Decade in the Making

NSE filed its draft IPO papers with SEBI last month after nearly a decade of regulatory delays linked to a settlement over fair market access. The exchange has since agreed to pay approximately $158 million to resolve the remaining proceedings, clearing the path for a listing that investors and analysts have long anticipated.

The IPO will be a pure offer-for-sale, with existing shareholders divesting about 6% of the exchange's equity. No fresh capital will be raised. At an estimated valuation of around ₹1,900 per share — roughly where NSE trades in the unlisted market — the offering would be worth approximately $3.3 billion, valuing the entire exchange at some $57 billion.

That would make NSE the world's fifth most valuable exchange, trailing only the London Stock Exchange Group, CME Group, ICE, and Nasdaq.

## Roadshow Begins This Week

According to Reuters, NSE's senior management will begin meeting key institutional investors in India this week, before traveling to Singapore, Malaysia, and Hong Kong later in July. A final leg of roadshows is planned for August in the United States, UAE, and London.

The exchange is pitching itself as a direct play on India's deepening capital markets. In its investor presentation, NSE projects annual turnover growth of 12% in cash equities and equity futures, and 10% in equity options over the next five years. It currently commands 100% market share in equity futures, 93% in cash markets, and 75% in equity options.

The IPO has already drawn significant interest from sovereign wealth funds, including Abu Dhabi Investment Authority and Singapore's GIC, who are also investing in the SBI Funds Management IPO opening this week.

## The BSE Precedent — And Why NRIs Should Pay Attention

For NRI investors weighing whether an exchange listing is worth the hype, BSE offers a compelling precedent. Since its own 2017 listing, BSE shares have surged more than 30 times — even as its revenue base is a fraction of NSE's.

BSE's revenue grew 88% in its latest fiscal year. NSE's revenue, though nearly six times larger, actually fell 3% due to SEBI's regulatory curbs on derivatives trading. That regulatory overhang is a risk investors will weigh carefully, but NSE's sheer dominance of India's market infrastructure gives it a moat that few listed companies can match.

"India's capital markets penetration is still very low across segments compared to other major economies and has room to grow," NSE said in its investor presentation.

For NRI investors, an NSE IPO represents something rare: a chance to own a piece of the infrastructure through which every rupee of Indian equity trading flows. It is not a bet on a single sector or company — it is a bet on the financialization of India itself.

## Two Mega IPOs, One Defining Half-Year

NSE is one of two blockbuster listings expected in the second half of 2026. Reliance Jio, which filed its DRHP with SEBI on June 19, is the other. Jio is targeting approximately $3 billion in fresh capital at a potential valuation of $180 billion or more.

Together, these two IPOs will test the depth of India's capital markets at a time when 251 companies are waiting in the pipeline to raise a staggering ₹4.93 trillion ($51.7 billion), according to PRIME Database.

The listing is expected around October. For NRIs who invest through India-focused funds or direct brokerage accounts, the next three months could define the shape of their portfolios for years to come."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Stock Exchange Is Going Public — NSE Kicks Off $3.3 Billion IPO Roadshow With 30 Global Investors This Week",
    "subheadline": "The world's most active derivatives exchange, valued at $57 billion, begins pitching institutional investors ahead of an October listing that could make it the fifth most valuable exchange on earth.",
    "slug": make_slug("nse-ipo-roadshow-57-billion-exchange-global-investors-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NSE's IPO gives NRI investors a rare chance to own a piece of India's capital market infrastructure — not a single company or sector, but the exchange through which every rupee of equity trading flows. BSE's 30x return since its 2017 listing offers a precedent.",
    "tags": ["markets", "ipo", "nse", "nri-investing", "capital-markets", "india-exchange"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indias-nse-pitch-ipo-30-global-investors-play-deepening-capital-markets-sources-2026-07-10/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/stock-markets/nse-to-pitch-ipo-to-30-global-investors-betting-big-on-indias-deepening-capital-markets/article69793215.ece"},
        {"name": "Reuters - NSE IPO Windfall", "url": "https://www.reuters.com/markets/deals/long-delayed-nse-ipo-sets-up-26-billion-windfall-top-investors-2026-06-18/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/IT7A2275_copy_%28cropped%29.jpg/3840px-IT7A2275_copy_%28cropped%29.jpg",
    "image_caption": "The National Stock Exchange of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ---------------------------------------------------------------------------
# ARTICLE 2: Bloomberg Bond Index Decision
# ---------------------------------------------------------------------------
art2_body = """India's government bond market is on the verge of a milestone that could redirect tens of billions of dollars in global capital: inclusion in the Bloomberg Global Aggregate Index, the world's flagship fixed-income benchmark.

A decision is expected later this month, and the stakes for NRI investors are considerable.

## $4.1 Billion in Six Weeks — And Counting

Foreign investors have net purchased over $4.1 billion of Indian government bonds in just the last six weeks under the Fully Accessible Route, according to Reuters. These bonds are already part of three emerging market debt indexes, including J.P. Morgan's Government Bond Index-Emerging Markets, which India joined in 2024 to significant fanfare.

But the Bloomberg Global Aggregate Index is a different beast entirely. It tracks approximately $68 trillion in investment-grade debt worldwide, and inclusion would bring India into the portfolios of passive fixed-income funds that currently have zero allocation to Indian government securities.

Analysts estimate that Bloomberg inclusion could trigger $20 to $25 billion in additional foreign inflows into Indian government debt — a transformative amount for a market where foreign ownership still represents a small fraction of outstanding issuance.

## Tax Reforms Tipped the Scales

India's candidacy got a major boost in June when the government scrapped capital gains tax for foreign portfolio investors and eliminated the 20% tax on interest income from government bond investments, effective April 1, 2026.

Bloomberg Index Services had previously deferred inclusion in January, citing operational concerns from investors around automated trading workflows, settlement timelines, and fund registration procedures. The tax reforms directly addressed several of these barriers.

"The steps taken would broaden opportunities for overseas investors, redirect flows to the onshore market and provide a constructive boost to India's bid for inclusion," said Niel Clement, portfolio manager for emerging market fixed income at BNP Paribas Asset Management.

India's finance minister reportedly met with RBI officials before the tax changes to push specifically for Bloomberg index entry — a sign of how seriously New Delhi is treating this as a policy priority.

## What It Means for NRI Bond Investors

For NRIs who hold Indian fixed deposits, government bonds, or debt mutual funds, Bloomberg inclusion would have several tangible effects.

**Lower yields, higher prices.** The influx of passive foreign capital would compress yields on Indian government securities. The 10-year benchmark, currently at 6.71%, has already fallen 34 basis points over the past six weeks. Further demand could push it lower, translating to capital gains for existing bondholders.

**A stronger rupee floor.** Sustained foreign bond inflows provide a natural buffer against rupee depreciation, counterbalancing the pressure from elevated oil import costs. Goldman Sachs recently upgraded its rupee forecast to 94 per dollar — a move partly predicated on rising fixed-income flows.

**RBI's rate path stays shallow.** OCBC Bank expects a cumulative 50 basis points in rate hikes over FY27, likely in late 2026 and early 2027. Robust foreign demand for bonds gives the RBI more room to keep hikes measured, which supports both bond prices and equity valuations.

## The Risk: Oil and Hormuz

The complicating factor is crude oil. Brent surged over 3% on Monday to roughly $79 per barrel after renewed U.S.-Iran strikes and Iran's claim to have again closed the Strait of Hormuz. India imports over 80% of its crude, and every $10 per barrel increase in oil prices widens the current account deficit by approximately 0.4% of GDP.

If oil sustains above $80, the RBI may need to intervene more aggressively to defend the rupee, potentially tightening domestic liquidity and offsetting some of the benefits of foreign bond inflows.

The 10-year benchmark yield traded in a 6.65%–6.77% range last week, and traders expect that band to hold unless oil breaks significantly higher or the Bloomberg announcement surprises.

## A Pivotal Month

M&G Investments, which manages approximately $503 billion in assets, called the tax reforms "a restoration of policy control" that differentiates India from other emerging bond markets.

For NRI investors, the calculus is straightforward: if Bloomberg says yes, Indian bonds become a core holding for the world's largest fixed-income allocators. The resulting demand compression in yields would benefit anyone already positioned in Indian debt — whether through direct government bond holdings, gilt mutual funds, or NRE/NRO fixed deposits whose pricing benchmarks against sovereign yields.

The announcement could come any day this month. Investors who wait for confirmation may find that the market has already priced in the good news."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Bond Market Awaits a $25 Billion Catalyst — Bloomberg Global Index Decision Expected This Month",
    "subheadline": "Foreign investors have poured $4.1 billion into Indian bonds in six weeks. If Bloomberg adds India to its flagship Global Aggregate Index, the floodgates could open — reshaping yields, the rupee, and NRI fixed-income portfolios.",
    "slug": make_slug("bloomberg-global-bond-index-india-inclusion-nri-fixed-income"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "Bloomberg inclusion would compress Indian bond yields, strengthen the rupee, and benefit NRIs holding government bonds, gilt funds, and NRE/NRO fixed deposits. The resulting passive foreign demand could add $20-25 billion to India's debt market.",
    "tags": ["markets", "bonds", "bloomberg-index", "rbi", "nri-investing", "fixed-income", "rupee"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/rates-bonds/indian-rupee-bonds-likely-track-mideast-developments-inflation-data-2026-07-13/"},
        {"name": "Reuters - Bond Tax Reforms", "url": "https://www.reuters.com/markets/rates-bonds/india-bond-tax-moves-catalyse-foreign-debt-inflows-bolster-bid-global-index-2026-06-10/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/stock-markets/indias-10-year-bond-logs-best-day-in-over-a-week-on-oil-relief/article69794912.ece"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Mumbai%2C_reserve_bank_of_india_01.jpg/1280px-Mumbai%2C_reserve_bank_of_india_01.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai, central to India's bond market policy",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ---------------------------------------------------------------------------
# ARTICLE 3: Foreign Fund Exodus
# ---------------------------------------------------------------------------
art3_body = """Nearly 60% of the foreign money that flowed into India-focused equity funds during the 2023–24 investment rally has now been pulled out, according to a new research report from Elara Capital — and the culprit is not India's economy. It is the global AI trade.

The numbers are stark: India-focused funds attracted nearly $20 billion between March 2023 and October 2024. Since then, almost $12 billion has been redeemed. In calendar year 2026 alone, investors have withdrawn $9 billion — $7 billion from long-only funds and $2 billion from exchange-traded funds.

For NRI investors who access Indian equities through U.S.-listed India ETFs or Luxembourg-domiciled funds, this is not an abstract statistic. It is happening inside the very vehicles they own.

## Where the Money Is Going

The rotation is straightforward. Since April 2025, global capital has flowed toward South Korea and Taiwan to ride the AI semiconductor wave, and toward Brazil on the back of a commodity rally — largely at India's expense.

Luxembourg-domiciled funds have seen the largest share of redemptions at $3.5 billion, followed by the United States at $2.4 billion and Japan at $2.1 billion. Ireland is the only major fund domicile that has largely avoided the selling.

"Almost 60% of inflows that India-focused funds saw in the 2023-24 period has been pulled out," Elara Capital wrote. "Redemptions have accelerated since January 2026 to fund the AI trade, and momentum continues to remain weak."

But there are early signs the rotation cycle itself is losing steam. South Korea saw a record $1.3 billion in outflows three weeks ago. Taiwan flows are slowing. Brazil recorded its largest redemption since December 2024. The AI and commodity trades that powered the rotation are, as Elara puts it, "showing early signs of exhaustion."

## India's Domestic Investors Are Not Flinching

While foreign passive vehicles bleed, India's domestic investor base is doing something remarkable: accelerating its commitments.

Equity mutual fund inflows surged 26% month-on-month in June to ₹28,973 crore ($3.04 billion), rebounding from a one-year low in May. This marks five years and four months of consecutive net inflows into equity mutual funds — the longest streak on record.

Midcap funds led inflows at ₹6,090 crore, followed by small-cap funds at ₹5,602 crore and flexi-cap at ₹5,231 crore. Even gold ETFs saw a dramatic reversal, recording ₹3,443 crore in inflows after net outflows in May.

The industry's total assets under management rose to ₹82.22 lakh crore — roughly $863 billion — at the end of June.

"Rising equity inflows show investors are willing to look past near-term global shocks from the Iran conflict and stay focused on the underlying strength of the Indian economy," said Aishvarya Dadheech, founder and chief investment officer at Fident Asset Management.

## The NRI Dilemma: Follow the Funds or Follow the Fundamentals?

This divergence creates a genuine dilemma for NRI investors, many of whom straddle both worlds.

If you hold an iShares MSCI India ETF or a Luxembourg-domiciled India fund, your vehicle has likely seen redemption-driven selling pressure that has nothing to do with India's earnings outlook. The fund is lighter, the NAV may have lagged the underlying market, and tracking error has widened — all because other investors in the same fund are rotating into Nvidia proxies.

Meanwhile, the Indian market's fundamentals are improving. J.P. Morgan recently reiterated its year-end Nifty target of 27,000, implying 11.5% upside from Friday's close. TCS delivered a revenue beat and flagged surging AI-linked sales. Credit growth, GST collections, and nominal GDP all point to potential earnings upgrades in the second half.

Foreign portfolio investors themselves are beginning to return at the direct level. They turned net buyers in the second half of June for the first time in months, with banking stocks alone drawing $1.54 billion in fortnightly inflows — the highest in 14 months.

## What to Watch

The key risk remains oil. Brent crude jumped over 3% on Monday to roughly $79 per barrel on renewed U.S.-Iran strikes, and every oil spike pressures the rupee and the current account. If Hormuz risks escalate further, even the domestic investor base may pause.

But for NRIs evaluating their India allocation, the question is less about timing and more about structure. The Elara data suggests that passive India-focused funds are subject to redemption flows driven by entirely non-India factors — the AI rotation, commodity positioning, and global risk appetite.

Direct exposure through Indian brokerage accounts, India-listed mutual funds, or the upcoming IPO pipeline (NSE, Reliance Jio, SBI Funds Management) may offer a cleaner way to ride India's growth without being whipsawed by a Silicon Valley narrative that has nothing to do with Mumbai."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "60% of Foreign Money Has Fled India-Focused Funds — But Domestic Investors Are Pouring In at Record Pace",
    "subheadline": "Elara Capital says $12 billion of $20 billion in India fund inflows have been redeemed since the 2024 peak, mostly to chase the AI trade. Yet India's SIP machine just hit its longest-ever streak. Here's what NRIs caught in between should know.",
    "slug": make_slug("foreign-fund-exodus-india-ai-rotation-domestic-sip-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs who hold US-listed India ETFs or Luxembourg-domiciled funds are directly exposed to redemption-driven selling from the AI rotation — even as India's fundamentals improve. Direct India exposure through IPOs and domestic funds may offer a cleaner ride.",
    "tags": ["markets", "fpi", "foreign-funds", "sip", "ai-rotation", "nri-investing", "etf"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Elara Capital via ChiniMandi/ANI", "url": "https://chinimandi.com/nearly-60-of-foreign-inflows-into-india-focused-funds-withdrawn-since-2024-peak-report/"},
        {"name": "Reuters - MF Inflows Rebound", "url": "https://www.reuters.com/markets/funds/india-equity-mutual-fund-inflows-rebound-one-year-low-2026-07-11/"},
        {"name": "Reuters - Worst Exodus Barely Bruises India", "url": "https://www.reuters.com/breakingviews/worst-global-money-exodus-barely-bruises-india-2026-07-08/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16594725/pexels-photo-16594725.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Financial trading screens displaying market data and charts",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. Published {len(articles)} articles at {now}")
