#!/usr/bin/env python3
"""Markets & Finance writer — July 15, 2026 01:00 PT run."""

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


articles = [
    # ── Article 1: US CPI / Fed / NRI Impact ──
    {
        "id": str(uuid.uuid4()),
        "headline": "US Inflation Crashes to 3.5% and Fed Rate Hike Odds Collapse — But Oil at $86 Keeps NRI Investors on Edge",
        "subheadline": "June CPI came in far cooler than expected, slashing the probability of a July rate hike from 40% to 15%. For NRIs navigating a rupee at 96.20 and Brent crude at $86, the relief may be short-lived.",
        "slug": make_slug("us-cpi-inflation-3-5-percent-fed-rate-hike-collapse-nri-rupee-oil"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Cooler US inflation eases the dollar squeeze on India, but NRIs face a dual calculation — lower Fed hike risk supports the rupee and Indian asset flows, while $86 crude threatens to undo those gains through India's import bill and inflation trajectory.",
        "tags": ["us-inflation", "federal-reserve", "rupee", "nri-investing", "oil-prices", "interest-rates"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bureau of Labor Statistics", "url": "https://www.bls.gov/"},
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "The Times (UK)", "url": "https://www.thetimes.com/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Marriner_S._Eccles_Federal_Reserve_Board_Building.jpg/1280px-Marriner_S._Eccles_Federal_Reserve_Board_Building.jpg",
        "image_caption": "The Marriner S. Eccles Federal Reserve Board Building in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": """The numbers told a straightforward story on Tuesday. U.S. consumer prices fell 0.4% in June — the steepest monthly decline since the COVID crash of April 2020 — dragging the annual inflation rate down to 3.5% from May's three-year high of 4.2%. Wall Street had expected 3.8%. The gap between forecast and reality was wide enough to reshape the interest rate calculus overnight.

Core CPI, which strips out volatile food and energy costs, was flat for the month. The year-over-year core reading dropped to 2.6%, well below the 2.9% consensus. Shelter costs registered their smallest monthly increase since January 2021. Car insurance fell 2.0%. Apparel prices declined 0.6%. Even the politically sensitive egg index, up 4.3% on the month, couldn't dent the broader narrative.

"Headline inflation has tentatively peaked," said Bernard Yaros, lead U.S. economist at Oxford Economics. "The Federal Reserve is worried about a broadening out of inflationary pressures across goods and services, and that wasn't evident in the June inflation details."

## The Fed pivot that wasn't — but almost was

Before the data dropped, futures markets were pricing a close to 40% chance that Fed Chair Kevin Warsh would raise rates at the July 29-30 meeting. That probability collapsed to roughly 15% within hours. For September, the odds of a hike fell from 75% to about 60%.

The report arrived on the same day Warsh was testifying on Capitol Hill, giving Congress — and markets — an unusual real-time read on how the data might shape his thinking. U.S. stocks opened higher, with the S&P 500 gaining 0.2% and the Nasdaq rising 1%. Treasury yields fell sharply, with the 2-year yield dropping 7 basis points to 4.19% and the benchmark 10-year sliding 3 basis points to 4.575%. The dollar index fell 0.6% to 100.7.

## What it means for the rupee and Indian markets

The relief rippled straight through to Asia. Indian markets opened higher on Wednesday, with the Sensex adding 493 points (0.64%) and the Nifty 50 gaining 124 points to 24,176 by midday. Fifteen of sixteen sectors advanced. Financials, which had lost 1.1% on Tuesday's oil-driven sell-off, bounced back 0.9%.

The rupee, however, remains under siege. After breaching 96 per dollar on Tuesday — its weakest since May 22 — the currency opened little changed on Wednesday in the 96.18-96.22 range. The RBI intervened in both spot and non-deliverable forward markets to contain losses, but traders noted the underlying bias has turned "considerably weaker."

The reason is crude. Brent hit $87 per barrel on Tuesday after the U.S. reimposed a naval blockade on Iranian ports, and President Trump proposed a 20% fee on all cargo traversing the Strait of Hormuz. India imports roughly 90% of its crude oil, and every $10 per barrel increase in Brent adds approximately $15 billion to its annual import bill.

## The NRI calculation: two forces pulling in opposite directions

For the roughly 32 million Indians living abroad, the CPI report creates a moment of genuine cross-current.

**The bull case:** A Fed that holds rates — or delays hikes — eases dollar strength, supports emerging market currencies, and keeps the carry trade into Indian assets attractive. Foreign portfolio investors have already poured ₹15,157 crore ($1.58 billion) into Indian equities in July, with Goldman Sachs declaring the foreign selling cycle "likely over." The RBI's special FCNR(B) deposit program has attracted $10 billion, with bankers estimating $30-60 billion in total flows before the September 30 deadline. Lower U.S. yields make these Indian deposits comparatively more attractive.

**The bear case:** The CPI data is backward-looking. Gasoline prices in June reflected a brief Iran ceasefire that has since collapsed. Brent has surged over 20% from its recent lows. "The inflation data predates the latest rise in geopolitical tensions, higher oil prices, energy supply risks and Trump's threat of a 20% protection fee," warned Uto Shinohara, senior investment strategist at Mesirow Currency Management. July's CPI will almost certainly look worse.

For NRIs sending remittances, the rupee at 96.20 is already near its all-time low of 96.96. Those with flexibility might find value in locking in transfers now — but only if they believe oil prices will push the rupee even lower before the Fed eventually acts.

## The bigger picture: inflation is not defeated

There is a temptation to read the June report as an all-clear. It is not. Annual CPI at 3.5% remains well above the Fed's 2% target. Three-month annualized inflation is running at 2.8%, which looks encouraging until you consider that energy costs — the primary driver of June's decline — are reversing in real time.

Karl Schamotta, chief market strategist at Corpay, captured the conditional optimism: "Without a sustained rise in global energy prices over the coming weeks and months, the U.S. economy is now on a modestly-disinflationary trajectory that should keep U.S. yields and the dollar capped."

The operative word is "without." With Iranian oil flows disrupted, a 20% Hormuz fee floated, and Brent approaching $90, that condition looks increasingly fragile. For NRI investors with exposure to both economies, the prudent move is to hedge for volatility rather than bet on direction — because the data and the geopolitics are telling two very different stories."""
    },

    # ── Article 2: Groww Q1 Results / India Retail Investing ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Groww's Profit Nearly Doubles to ₹735 Crore as 22 Million Indians Trade Actively — Inside the Retail Boom That's Rewriting India's Market DNA",
        "subheadline": "India's largest online brokerage added clients even as the broader industry shrank. Revenue surged 66%, and the platform now manages assets from over 50 million customers — a fintech story NRI investors can't ignore.",
        "slug": make_slug("groww-q1-profit-doubles-735-crore-retail-investing-boom-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Groww's surge reflects a structural shift in how Indians invest — and it directly affects NRIs considering Indian brokerage accounts, mutual fund SIPs, and exposure to India's fintech sector. The retail investor base is also changing market dynamics for NRI-held stocks.",
        "tags": ["groww", "fintech", "retail-investing", "india-stock-market", "nri-investing", "brokerage"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/"},
            {"name": "Inc42", "url": "https://inc42.com/"},
            {"name": "Motilal Oswal Research", "url": "https://www.motilaloswal.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange building in Mumbai — home to the world's fastest-growing retail investor base.",
        "image_attribution": "Wikimedia Commons",
        "body": """Something unusual happened in India's brokerage industry during the April-June quarter. While the overall market saw a net decline of 257,000 active National Stock Exchange clients, Groww — the country's largest online investment platform — added 115,000. The numbers from the Bengaluru-headquartered fintech tell a story of an industry being reshaped from within.

Billionbrains Garage Ventures, Groww's parent company listed on the NSE as BILO, reported consolidated net profit of ₹735 crore ($76.5 million) for the quarter ended June 30, 2026 — nearly doubling from ₹378 crore a year earlier. Revenue from operations surged 66% to ₹1,501 crore. Expenses grew a more modest 25%, giving the company significant operating leverage.

Shares of Groww jumped nearly 8% on the results before settling 4.1% higher at ₹212.22 by early afternoon.

## The numbers behind the numbers

The headline profit figure, impressive as it is, understates the underlying momentum. Groww's transacting users — the people who actually bought or sold something during the quarter, not just those who opened accounts — reached 22 million, up 24% year-on-year and 4% sequentially. Total customer assets climbed 38% on-year and 22% quarter-on-quarter.

That last metric matters. In a quarter where the Nifty 50 rose roughly 4%, Groww's asset growth significantly outpaced the benchmark — meaning net new money is flowing in, not just riding market appreciation. Total assets under management across the platform's 50 million-plus customers now exceed ₹3 trillion ($31 billion).

The commodities derivatives segment, often overlooked in brokerage analysis, showed notable growth. Active users in commodities rose 10.7% sequentially to 435,000, diversifying Groww's revenue beyond its equity trading and mutual fund distribution core.

## Why the industry is contracting while Groww expands

The paradox of Groww gaining clients while the broader industry loses them has a regulatory backdrop. The Securities and Exchange Board of India tightened derivatives trading rules in late 2025 — larger lot sizes, fewer weekly expiry contracts, and "true-to-label" pricing that capped pass-through fees. The intent was to curb speculative activity by retail traders.

The regulation achieved its goal. Industry-wide, individual futures and options activity dropped 36% year-on-year. Many small brokers saw their client bases evaporate. But Groww, which had already diversified beyond pure derivatives into mutual funds, fixed income, and systematic investment plans (SIPs), absorbed the shock better than most.

The platform's mutual fund AUM has been growing steadily, benefiting from India's SIP phenomenon. Monthly SIP contributions across the industry crossed ₹25,000 crore in the June quarter — essentially, Indians are putting roughly $3 billion a month into automatic, recurring equity investments. Groww captures a meaningful share of this flow through its app, which has become one of India's most downloaded fintech platforms.

## What Groww's rise means for NRI investors

For the Indian diaspora, Groww's trajectory matters on two levels.

**As an investment opportunity:** Groww went public in November 2025 at ₹250 per share. After an initial post-IPO dip, the stock has ranged between ₹150 and ₹215 — currently near the upper end following the Q1 beat. Motilal Oswal has a "Buy" rating with a ₹235 target price, citing growing market share and new product lines. JM Financial, however, maintains a "Sell" at ₹150, arguing that valuations at 38x FY27 earnings are stretched for a company whose revenue mix is still heavily tied to volatile derivatives trading.

For NRIs evaluating whether to buy India's fintech growth story, the split opinion captures a real tension: Groww's market position is formidable, but SEBI's regulatory posture toward retail derivatives could tighten further, capping the upside.

**As a platform to invest through:** This is where it gets more interesting. India's brokerage platforms, including Groww, have been gradually improving NRI onboarding processes. Non-resident Indians can open Portfolio Investment Scheme (PIS) accounts to trade Indian equities, though the KYC process remains more cumbersome than it is for residents. The platforms that crack NRI ease-of-use at scale — particularly for mutual fund SIPs and IPO applications — will tap into a massive, underserved market.

## Context: India's retail investor base is now a market force

Five years ago, Indian retail investors were a footnote in market analysis. Foreign institutional investors dictated direction. That equation has flipped. Monthly SIP flows now regularly exceed net FPI buying. Domestic mutual funds have become the backstop when foreign money exits — something Goldman Sachs pointed to this week when it declared the foreign selling cycle "likely over," partly because domestic buyers had absorbed the selling pressure without the Nifty breaking key support levels.

Groww sits at the center of this structural shift. With State Street investing ₹580 crore into Groww's asset management arm earlier this fiscal year, the company is evolving from a pure-play brokerage into a diversified financial platform — one that mirrors the trajectory Zerodha pioneered but with a larger retail footprint.

For NRIs watching India's markets from afar, the takeaway is not just about one company's earnings beat. It is that the composition of who owns Indian equities is changing — becoming more domestic, more retail, and more sticky through SIPs. That makes India's market less vulnerable to FPI mood swings and potentially more attractive for long-term diaspora capital.

The question is whether platforms like Groww can turn that structural advantage into durable profitability — or whether the next round of SEBI tightening erases the margin gains that made this quarter look so good."""
    },
]


for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
