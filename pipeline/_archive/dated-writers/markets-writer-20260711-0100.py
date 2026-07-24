#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-11 01:00 PDT run."""
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


# ── ARTICLE 1: SBI Funds Management IPO ──────────────────────────────────

art1_body = """India's largest mutual fund house is about to go public — and the smart money is already piling in.

SBI Funds Management, the joint venture between State Bank of India and France's Amundi that oversees ₹12.5 trillion ($131 billion) in assets, has set a price band of ₹545–574 per share for its initial public offering opening July 14. At the upper end, the company would command a valuation of roughly $12.3 billion, making it one of India's largest IPOs of 2026.

## Sovereign Wealth Funds Lead the Charge

The offering has already attracted cornerstone commitments from two of the world's most prominent sovereign wealth funds — Abu Dhabi Investment Authority (ADIA) and Singapore's GIC — according to Reuters, citing sources with direct knowledge. Anchor investors will place their bids on July 13, a day before the public subscription opens.

Institutional demand is running hot. Commitments are reportedly worth nearly five times the amount reserved for institutional buyers. Despite that demand, SBI Funds Management is keeping 50% of the offer reserved for individual investors — a deliberate nod to the retail participation that has transformed India's capital markets over the past five years.

Neither SBI nor Amundi is injecting fresh capital. SBI will sell up to 128.3 million shares and Amundi India Holding will divest up to 75.4 million shares, together offloading roughly 10% of the company's paid-up equity.

## What NRI Investors Should Know

For diaspora investors, the SBI Funds Management IPO sits at the intersection of several important trends. The company manages more money than any other fund house in India — more than HDFC AMC ($12.5 billion market cap) and close to ICICI Prudential AMC ($17.2 billion). Its distribution network, anchored by SBI's 22,000-plus branch network, gives it unmatched retail reach.

NRIs holding NRE or NRO demat accounts with Indian brokers can participate directly through the ASBA (Application Supported by Blocked Amount) process. The 50% retail reservation means individual allotment odds may be more favourable than in recent oversubscribed issues.

The valuation, however, is not cheap. At ₹574 per share, SBI Funds Management would trade at roughly 28 times its trailing earnings — a premium justified by its market-leading position but one that leaves limited room for listing-day fireworks.

## The Bigger Picture: H2 IPO Pipeline

SBI Funds Management is the opening act for what investment bankers expect to be a transformative second half. Also lined up for July: Manipal Health Enterprises ($1.2 billion) and Indo-MIM ($471 million). Later in the year, the mega-listings of the National Stock Exchange of India ($3.3 billion) and Reliance Jio ($3.8 billion) could redefine India's public markets.

According to PRIME Database, 251 companies are waiting to raise a collective ₹4.93 trillion ($51.7 billion). In 2025, Indian firms raised $21.8 billion from IPOs; so far in 2026, the figure stands at just $3.8 billion, depressed by the Iran conflict and oil-price volatility.

"We remain optimistic about the $20 billion IPO fundraise this year despite a subdued first half," said Bhavesh Shah, managing director and head of investment banking at Equirus. "A lot of heavy lifting — $8 billion to $9 billion — will be done by three to four large IPOs in the pipeline."

For NRI investors who have watched India's IPO market from the sidelines during a turbulent first half, the second half could offer a re-entry window — starting Monday."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "SBI Funds Management Prices $1.2 Billion IPO at ₹545–574 — ADIA and GIC Already In, Retail Gets Half the Pie",
    "subheadline": "India's largest asset manager opens its blockbuster public offering on July 14, kicking off a $20 billion H2 IPO pipeline that includes the NSE and Reliance Jio.",
    "slug": make_slug("sbi-funds-management-ipo-adia-gic-nri-retail"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs with NRE/NRO demat accounts can apply for the IPO through ASBA, with 50% reserved for retail investors — a rare chance to get into India's largest fund house at listing.",
    "tags": ["markets", "finance", "ipo", "sbi", "mutual-funds", "nri-investing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-largest-asset-manager-draws-top-sovereign-funds-12-billion-ipo-sources-2026-07-07/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/sbi-funds-management-seeks-1224-billion-valuation-india-ipo-2026-07-09/"},
        {"name": "IPO Watch", "url": "https://ipowatch.in/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange building in Mumbai, home to India's capital markets",
    "image_attribution": "Wikimedia Commons, CC BY-SA",
    "body": art1_body.strip(),
}


# ── ARTICLE 2: India Forex Reserves Jump ──────────────────────────────────

art2_body = """India's foreign exchange reserves posted their sharpest weekly gain in over a month, climbing $7.26 billion to $674.19 billion for the week ending July 3, the Reserve Bank of India reported on Friday.

The rebound follows a $5.65 billion drop in the prior week and signals that the central bank's campaign to rebuild the country's FX buffer is gaining traction — even as geopolitical uncertainty and oil-price swings continue to test the rupee.

## Where the Money Came From

Foreign currency assets — the largest component of the reserves — rose $4.51 billion to $545.58 billion, reflecting both valuation gains from the weakening US dollar against other reserve currencies (euro, pound, yen) and what analysts believe were fresh inflows from foreign portfolio investors returning to Indian equities.

Gold reserves surged $2.67 billion to $105.21 billion, underscoring the RBI's aggressive diversification into bullion. India's central bank has been one of the world's largest gold buyers over the past two years, a strategy that has paid off as gold prices hit record highs above ₹1.44 lakh per 10 grams domestically.

Special Drawing Rights edged up $65 million to $18.62 billion, and India's reserve position with the IMF rose $15 million to $4.79 billion.

## The Long Road Back From $728 Billion

The reserves hit an all-time high of $728.49 billion in late February, before the Iran-US conflict sent oil prices spiralling and forced the RBI into heavy dollar sales to defend the rupee. At their recent trough, reserves had shed over $60 billion in roughly three months — a pace not seen since the 2013 taper tantrum.

The recovery has been supported by three factors: the RBI's measures to attract foreign inflows (including relaxing overseas borrowing limits for corporates), a partial cooling of crude prices from their May highs, and the return of portfolio flows after the ceasefire-that-wasn't between the US and Iran.

Prime Minister Narendra Modi has also made repeated public appeals since May 11, urging citizens to conserve foreign exchange by cutting foreign travel, reducing fuel consumption, and abstaining from gold purchases for a year — a campaign that has drawn comparisons to the 1991 balance-of-payments crisis.

## What This Means for NRI Remittances

For the Indian diaspora, reserve levels are more than an abstract macro indicator. Higher reserves give the RBI more firepower to intervene against sharp rupee depreciation, which directly affects the dollar-to-rupee conversion rate on remittances.

The rupee ended the week at 95.33 per dollar, down 0.1% on the week but well above its record low of 96.96 hit on May 20. Goldman Sachs recently upgraded its rupee forecast to 94 per dollar, suggesting the worst of the depreciation may be behind.

For NRIs sending money home through services like Wise, Remitly, or bank wire transfers, the current rate still offers more rupees per dollar than at any point before March 2026. But the window may narrow if reserves continue rebuilding and the RBI gains enough confidence to let the rupee appreciate.

India's import cover — the number of months of imports that reserves can finance — now stands at roughly 9.5 months, comfortably above the standard benchmark of six months but still below the 12-month-plus cover India maintained before the conflict."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Forex Reserves Jump $7.26 Billion in a Week — Gold Reserves Cross $105 Billion as RBI Rebuilds Its War Chest",
    "subheadline": "The sharpest weekly gain in over a month lifts reserves to $674.19 billion, still $54 billion below their pre-conflict peak, as Modi's austerity appeals and RBI intervention reshape the FX landscape for NRI remittances.",
    "slug": make_slug("india-forex-reserves-jump-7-billion-gold-rbi-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "Reserve levels directly affect RBI's ability to defend the rupee, which determines how many rupees NRIs get per dollar on remittances — the current rate still favours senders, but the window may narrow.",
    "tags": ["markets", "finance", "forex-reserves", "rbi", "rupee", "gold", "nri-remittance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/indias-forex-kitty-jumps-726-bn-to-67419-bn"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/rupee-slips-on-week-iran-flare-up-spurs-caution-merchant-hedging-2026-07-11/"},
        {"name": "Reserve Bank of India", "url": "https://www.rbi.org.in/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
    "body": art2_body.strip(),
}


# ── ARTICLE 3: Mutual Fund SIP Inflows Near Record ──────────────────────

art3_body = """India's retail investors are voting with their wallets — and the verdict is emphatic.

Equity mutual fund inflows surged 26.5% month-on-month to ₹289.73 billion ($3.04 billion) in June, rebounding sharply from their lowest level in a year, according to data from the Association of Mutual Funds in India (AMFI) released Friday. The figure extends what is now the longest streak of net positive equity inflows on record: five years and four consecutive months.

Meanwhile, Systematic Investment Plan (SIP) contributions climbed 3% to ₹317.81 billion — just ₹3 billion shy of the all-time monthly record of ₹320.87 billion set in March.

## The Numbers Behind the Surge

The recovery was broad-based. Large-cap funds saw inflows jump 34% sequentially, mid-caps surged 39%, and small-caps rose 13%. The divergence suggests investors are rotating into broader markets where valuations have become more attractive after the April-May correction, while maintaining large-cap allocations as a defensive anchor.

India's benchmark Nifty 50 rose 1.4% in June, but the real action was in small-caps, which gained 4% — extending a pattern where broader indices have consistently outperformed blue chips since the March lows.

"Rising equity inflows show investors are willing to look past near-term global shocks from the Iran conflict and stay focused on the underlying strength of the Indian economy," said Aishvarya Dadheech, founder and CIO at Fident Asset Management. "Strong credit growth, healthy GST collections and resilient nominal GDP all point to the possibility of earnings upgrades."

## Gold ETFs Stage a Comeback

Perhaps the most striking reversal came in gold exchange-traded funds. After recording record outflows of ₹7.25 billion in May — triggered by India's shock decision to raise import tariffs on gold and silver to 15% from 6% — gold ETFs attracted ₹34.43 billion in June.

The pullback in domestic gold prices after their ₹1.44 lakh peak, combined with the tariff-driven premium that makes physical gold more expensive, has made paper gold a more attractive route for investors seeking bullion exposure without the import markup.

"The outlook for overall mutual fund inflows and SIPs remains strong, supported by improving market liquidity after the RBI's rupee-stabilising measures, softer oil prices and resilient domestic macro fundamentals," said AMFI Chief Executive Venkat Chalasani.

## What NRI Investors Should Watch

For Non-Resident Indians, the data carries several actionable signals.

**SIPs remain the smart entry point.** At nearly ₹318 billion per month, SIPs now represent roughly $3.3 billion in systematic buying power that provides a structural floor under Indian equities. NRIs with NRE or NRO accounts at banks like SBI, HDFC, or ICICI can set up SIPs through their fund house or demat platform — typically starting at ₹500 per month. The rupee-cost averaging benefit is amplified when the dollar is strong against the rupee, as it is now.

**Mid- and small-caps are where the alpha is.** The 39% jump in mid-cap inflows reflects growing institutional conviction that Indian mid-caps offer better risk-adjusted returns than large-caps at current valuations. NRI investors who have historically defaulted to large-cap index funds may want to consider diversifying into mid-cap funds that have track records through the 2024-2026 volatility.

**Gold ETFs over physical gold.** With the 15% import tariff making physical gold significantly more expensive in India, NRIs looking for gold exposure should consider gold ETFs or Sovereign Gold Bonds (though new SGB issuances have been paused). Gold ETFs trade on Indian exchanges and can be held in a demat account — no import duty, no making charges, no storage hassle.

The ₹317.81 billion SIP figure is more than just a data point. It represents a structural transformation in how India saves and invests — one that NRIs are increasingly participating in from abroad."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's SIP Machine Hits ₹317.81 Billion — Just ₹3 Billion Short of the All-Time Record as Mid-Cap Inflows Surge 39%",
    "subheadline": "Equity mutual fund inflows rebound 26.5% in June, extending the longest positive streak on record to five years, while gold ETFs stage a dramatic comeback after May's tariff shock.",
    "slug": make_slug("india-sip-317-billion-record-midcap-gold-etf-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs with NRE/NRO accounts can set up SIPs from abroad to ride the structural floor under Indian equities — and gold ETFs are now cheaper than physical gold after the 15% import tariff hike.",
    "tags": ["markets", "finance", "mutual-funds", "sip", "gold-etf", "nri-investing", "amfi"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-equity-mutual-fund-inflows-rebound-one-year-low-2026-07-10/"},
        {"name": "AMFI", "url": "https://www.amfiindia.com/"},
        {"name": "Fident Asset Management", "url": "https://www.reuters.com/world/india/india-equity-mutual-fund-inflows-rebound-one-year-low-2026-07-10/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/National_Stock_Exchange_NSE_India.jpg/1280px-National_Stock_Exchange_NSE_India.jpg",
    "image_caption": "The National Stock Exchange of India in Mumbai, the backbone of the country's equity markets",
    "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
    "body": art3_body.strip(),
}


# ── PUBLISH ───────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted to review.")
