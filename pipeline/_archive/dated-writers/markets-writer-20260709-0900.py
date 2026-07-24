#!/usr/bin/env python3
"""Markets & Finance writer — July 9, 2026 morning run."""
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


# ──────────────────────────────────────────────
# ARTICLE 1: FPI Flows Return to Indian Banks
# ──────────────────────────────────────────────

article1_body = """Foreign portfolio investors have staged their most significant return to Indian banking stocks in over a year, buying ₹146.34 billion ($1.54 billion) worth of shares in the second half of June — the largest fortnightly inflow into the sector since April 2025.

The buying spree marks a decisive shift in sentiment after 18 months of relentless foreign selling that saw $48 billion exit Indian equities, much of it redirected toward AI and semiconductor plays in Taiwan and South Korea.

## What Changed

Three policy interventions converged to bring foreign money back.

In June, the Reserve Bank of India extended a subsidised forex swap facility for banks' overseas borrowings and allowed lenders to offer loans to non-residents against foreign currency deposits — a move Citi Research said could help banks narrow loan-to-deposit gaps, reduce deposit costs, and improve margins.

The government, meanwhile, scrapped capital gains tax for foreign portfolio investors and eliminated the 20% withholding tax on interest income from such investments, both effective April 1, 2026. Together, these measures substantially improved the after-tax return on Indian financial assets for overseas investors.

The Nifty Bank index responded with a 6.1% gain in June, leading the Nifty 50's 1.4% rise. HDFC Bank, India's largest private lender, climbed 7.2% after an independent review related to former chairman Atanu Chakraborty's resignation found no evidence supporting the concerns raised.

## The Bigger Picture

FPIs turned net buyers of Indian equities overall in the second half of June, with total inflows of ₹141.09 billion after four consecutive months of selling. In the first five trading sessions of July, another $401 million flowed in.

Perhaps more telling than the equity flows is the bond market signal. Foreign investors have been aggressively unwinding bets on Indian rate hikes, pushing turnover in the five-year overnight index swap market to a record ₹253 billion ($2.65 billion) on July 8. The five-year OIS rate, a key gauge of policy expectations, fell to a four-month low of 6.1% — just 10 basis points above where it stood before the Iran war began — after climbing as high as 6.9% in April when investors were pricing in up to 125 basis points of tightening.

"My sense is that the worst of the FPI selling is over and outflows will reduce significantly," said Abhay Laijawala, chief investment officer for India at Lighthouse Canton. "Meaningful FPI buying in large banks aided by steady earnings outlook could be enough to power Nifty higher after the 2026 underperformance so far."

## What It Means for NRI Investors

The flow reversal carries direct implications for the millions of Indian Americans with exposure to Indian financial markets.

For NRI investors holding Indian bank stocks or banking ETFs — including popular vehicles like the Nifty Bank ETF and HDFC Bank ADRs — the return of institutional foreign buying provides a meaningful tailwind. Banking stocks had become significantly cheaper relative to their own history after the prolonged selloff, and the combination of strong Q1 FY27 earnings, policy support, and renewed FPI interest suggests valuations may have found a floor.

The elimination of capital gains tax and withholding tax on interest also directly benefits NRIs investing through FPI channels. NRE fixed deposit holders, meanwhile, benefit indirectly — as banks' funding costs ease and competition for deposits softens, the premium rates on NRE deposits seen during the tight-liquidity period may gradually moderate.

The one risk that could derail the recovery sits in the Middle East. The rupee slid to 95.55 per dollar on July 8 — a one-month low — after Trump declared the Iran ceasefire "over" and Brent crude surged 6.1% to $79. India imports over 80% of its oil, and a sustained price above $80 would pressure inflation, the current account deficit, and the very policy environment that attracted foreign investors back.

For now, though, the RBI's dollar-selling intervention and a slight pullback in crude to $77.50 on July 9 have steadied nerves. The question is whether diplomacy can hold — because the macro case for Indian banks, stripped of geopolitical noise, is the strongest it has been in over a year."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Foreign Investors Pour $1.5 Billion Into Indian Banks in Biggest Buying Spree Since 2025",
    "subheadline": "Policy support, cheaper valuations, and easing rate-hike fears are drawing FPIs back to Indian financials after 18 months of record outflows — but oil prices threaten the recovery.",
    "slug": make_slug("foreign-investors-pour-1-5-billion-indian-banks-buying-spree-fpi-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI investors with Indian bank ETFs, HDFC ADRs, and NRE deposits benefit directly from the FPI flow reversal and elimination of capital gains and withholding taxes on foreign investments.",
    "tags": ["markets", "finance", "nri-investing", "fpi", "indian-banks", "rbi", "hdfc-bank"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/policy-support-lifts-foreign-inflows-into-indian-banks-14-month-high-2026-07-07/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/worst-global-money-exodus-barely-bruises-india-2026-07-08/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/foreign-investors-pare-india-rate-hike-bets-fuel-record-5-year-swaps-trading-2026-07-08/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange building in Mumbai, India's financial capital",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ──────────────────────────────────────────────
# ARTICLE 2: India's IPO Super-Cycle
# ──────────────────────────────────────────────

article2_body = """India's capital markets are gearing up for a listing bonanza that could reshape the country's equity landscape. Some 251 companies are waiting to raise a combined ₹4.93 trillion ($51.7 billion) through initial public offerings, and the marquee names — the National Stock Exchange, Razorpay, and Reliance Jio — read like a who's who of India's economic ambitions.

## The Headline Act: NSE Goes Public

The National Stock Exchange of India, operator of the world's largest derivatives exchange by trading volume, is set to begin formal IPO marketing next week. Investor roadshows are planned across the United States, London, Singapore, Hong Kong, the Middle East, and India ahead of a targeted September listing.

NSE filed its Draft Red Herring Prospectus with SEBI last month for a pure offer-for-sale of approximately 148.9 million shares — about 6% of its equity. At a grey market valuation of ₹5.25 trillion ($55.1 billion), the sale could raise around ₹30,600 crore ($3.2 billion), surpassing Hyundai Motor India's ₹27,870 crore listing in 2024 as the country's largest IPO on record.

The numbers underline why the exchange is attractive: NSE reported total income of ₹18,713 crore and net profit of ₹10,302 crore for FY26, powered by surging retail participation in derivatives trading. Twenty banks, including Kotak Mahindra Capital, Morgan Stanley, HSBC, and Citigroup, have been appointed to manage the offering.

SEBI approval is expected by August, with a September launch the target — assuming geopolitical conditions cooperate.

## Razorpay's Reverse Flip to Dalal Street

While NSE represents old-guard infrastructure, Razorpay's impending IPO captures the new India story. The Bengaluru-based fintech giant filed a confidential DRHP with SEBI on June 12, seeking to raise $500–700 million at a valuation of $5–6 billion.

That valuation represents a roughly 25% haircut from Razorpay's last private-market valuation of $7.5 billion — a reality check that reflects the broader repricing of fintech globally. But the fundamentals tell a growth story: operating revenue surged 65% year-on-year to ₹3,783 crore in FY25, and the company processes an annualised total payment volume exceeding $180 billion, serving a majority of India's unicorns.

The IPO caps a multi-year journey back to Indian shores. Founded by IIT Roorkee alumni Harshil Mathur and Shashank Kumar in 2014, Razorpay was incorporated in the United States — like many Indian startups chasing Silicon Valley venture capital. It reverse-flipped to India in May 2025, absorbing a $150 million tax bill in the process.

Axis Capital, Kotak Mahindra Capital, JP Morgan, and Citi are managing the offering.

## The Pipeline Behind Them

The NSE and Razorpay listings are just the tip of a formidable pipeline. SBI Funds Management, India's largest mutual fund house managing ₹12.5 trillion in assets, opens its ₹11,700 crore ($1.22 billion) IPO on July 14, with sovereign wealth funds ADIA and GIC already committed as anchor investors.

Reliance Jio Platforms, the telecom and digital services arm of Reliance Industries, is expected to raise $3.8 billion in what would be another record-breaking offering later this year.

Other July listings include Manipal Health Enterprises ($1.2 billion) and Indo-MIM ($471 million). Fitness platform Cult.fit has filed for a ₹950 crore IPO. And Sachin Bansal's Navi, the full-stack fintech he built after exiting Flipkart, is preparing a ₹3,000 crore listing with SEBI filing expected soon.

Yet the first half of 2026 was subdued. Indian firms raised just $3.8 billion through IPOs — a fraction of the $21.8 billion raised in all of 2025 — as the Iran war, surging oil prices, and foreign investor exodus dampened appetite. Bankers remain optimistic about catching up.

"We remain optimistic about the $20 billion IPO fundraise this year despite a subdued first half. Although, a lot of heavy lifting — $8 billion to $9 billion — will be done by three to four large IPOs," said Bhavesh Shah, managing director and head of investment banking at Equirus.

## What NRI Investors Should Know

For the Indian American diaspora, this IPO cycle is unusually relevant.

Razorpay's reverse flip is part of a broader trend of Indian-origin companies returning from US incorporation to list domestically — a structural shift that gives NRI investors access to companies they may have used or funded in their Silicon Valley lives, but now on Indian exchanges. NRIs with demat accounts can participate in IPO allotments through their NRE or NRO accounts, subject to SEBI's NRI participation rules.

The NSE IPO offers a rare chance to own a piece of India's market infrastructure — the exchange itself, not just the companies traded on it. For context, exchanges globally tend to trade at premium valuations given their quasi-monopoly positions and operating leverage.

The SBI Funds Management listing provides exposure to India's mutual fund boom. With systematic investment plan (SIP) inflows consistently exceeding ₹25,000 crore per month, the asset management industry has become one of the most resilient segments of Indian financial services.

Timing, though, is everything. The geopolitical overhang from Iran-US tensions and elevated crude prices could delay some offerings or compress valuations. NRI investors would be wise to watch the IPO pipeline as a barometer of broader confidence in India's economic trajectory — and position accordingly."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "From Razorpay to the NSE: Inside India's $51 Billion IPO Pipeline That Could Rewrite Market History",
    "subheadline": "With 251 companies in the queue and mega listings from the National Stock Exchange, Razorpay, and Reliance Jio on the horizon, India's second-half IPO wave promises to be its most consequential yet.",
    "slug": make_slug("razorpay-nse-india-51-billion-ipo-pipeline-nri-investor"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI investors can participate in Indian IPOs through demat accounts linked to NRE/NRO accounts. Razorpay's reverse flip from US to India represents a structural trend bringing diaspora-connected companies to Indian exchanges.",
    "tags": ["markets", "finance", "nri-investing", "ipo", "nse", "razorpay", "reliance-jio", "fintech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-largest-asset-manager-draws-top-sovereign-funds-12-billion-ipo-sources-say-2026-07-07/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/nse-gears-up-to-market-3-billion-ipo-next-week/article69758432.ece"},
        {"name": "Inc42", "url": "https://inc42.com/features/indian-startup-ipo-tracker/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/sbi-funds-management-seeks-1224-billion-valuation-india-ipo-2026-07-09/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/National_Stock_Exchange.jpg/1280px-National_Stock_Exchange.jpg",
    "image_caption": "The National Stock Exchange of India building in Mumbai's Bandra Kurla Complex",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ──────────────────────────────────────────────
# Publish
# ──────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
