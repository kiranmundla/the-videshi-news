#!/usr/bin/env python3
"""NRI World Writer — 2026-06-09 18:00 UTC run"""
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

articles = [
    # ── Article 1 ──────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "The Rupee Crossed 95. For NRIs Wiring Money Home, Every Dollar Now Buys a Small Fortune.",
        "subheadline": "India's currency has shed 12 per cent against the dollar in a year — a gut punch for importers, but an unexpected windfall for the diaspora sending money back.",
        "slug": make_slug("rupee-95-nri-remittance-windfall-exchange-rate"),
        "category": "nri-world",
        "vertical": "nri-world",
        "is_editorial": False,
        "diaspora_angle": "NRIs sending remittances to India are getting significantly more rupees per dollar, affecting family support, property purchases, and retirement planning for millions abroad.",
        "tags": ["nri", "diaspora", "remittance", "rupee", "currency", "personal-finance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-rbi-offers-concessional-swaps-allows-leverage-nri-deposits-drive-forex-2026-06-09/"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/fpis-pull-out-43000-crore-in-first-week-of-jun-as-ai-trade-rupee-weakness-weigh-on-indian-equities/article69668845.ece"},
            {"name": "Goldman Sachs via Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/forex/goldman-sees-rupee-weakness-capped-after-steps-to-boost-inflows/article69672380.ece"},
            {"name": "Livemint", "url": "https://www.livemint.com/money/personal-finance/rupee-hits-96-against-usd-how-can-falling-currency-impact-your-investments-and-how-to-protect-them-11747752291925.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Indian rupee banknotes; the currency has lost over 12 per cent against the US dollar in the past year",
        "image_attribution": "Pexels",
        "body": """On 20 May, the Indian rupee touched 96.96 against the US dollar — a figure that would have seemed absurd two years ago, when it hovered around 83. In the twelve months since June 2025, the currency has shed more than 12 per cent of its value, driven by a toxic cocktail of surging oil prices from the Iran conflict, record equity outflows by foreign portfolio investors, and a global capital rotation toward American AI stocks. For the Reserve Bank of India, now burning through forex reserves and cobbling together emergency deposit schemes, it is the worst depreciation episode in a decade.

For the 35 million Indians living abroad, however, the maths works in reverse.

## The remittance dividend

An NRI in Houston or Dubai who wired $1,000 home in June 2025 delivered roughly ₹85,000 to a parent's bank account in Bengaluru. The same transfer today lands as ₹95,500 — an effective raise of more than 12 per cent without a single change in salary. Scale that across India's $135 billion annual remittance haul — the largest of any country on earth — and the aggregate windfall for recipient families is staggering.

Remittance corridors from the Gulf, where dirham-denominated salaries are pegged to the dollar, are seeing the sharpest gains. A construction supervisor in Abu Dhabi earning AED 5,000 a month now converts to ₹130,000, up from ₹115,000 a year ago. For blue-collar workers whose families in Kerala or Uttar Pradesh depend entirely on that wire, the difference is a second child's school fees, a hospital bill settled, a chunk of a dowry fund.

In the United States, where the Indian diaspora's median household income runs north of $150,000, the calculus shifts toward larger plays. Property buyers have noticed: a $200,000 flat in Pune now costs the equivalent of fewer dollars than it did last summer, even if rupee-denominated prices haven't fallen. Anecdotally, NRI real estate brokers report a 15-20 per cent uptick in enquiries from the US and UK since April.

## The other side of the ledger

The windfall is not without its complications. NRIs who hold Indian equities — whether through PMS accounts, mutual funds, or direct stock holdings — are watching their dollar-denominated returns erode. The Nifty 50 is down roughly 8 per cent in rupee terms from its September 2024 peak; factor in currency depreciation and the loss in dollar terms stretches past 20 per cent. Foreign portfolio investors have pulled ₹2.67 lakh crore ($31 billion) from Indian stocks in 2026 alone, surpassing the full-year outflow of 2025.

For the NRI contemplating retirement in India, the weak rupee is a double-edged sword. Savings accumulated in dollars stretch further on arrival — but if a large part of the nest egg is already invested in Indian markets, its purchasing power has actually shrunk.

Goldman Sachs, in a note published on 8 June, forecast the dollar-rupee cross settling around 96 over the next three months, suggesting the worst may be over. The RBI's recent blitz — absorbing hedging costs on FCNR deposits, exempting banks from CRR and SLR on fresh foreign-currency deposits, and scrapping capital-gains tax on government bonds for foreign investors — is designed to pull $40 billion to $50 billion back into the system. Analysts at IDFC First Bank expect the FCNR window alone to draw $40 billion.

## What the diaspora should watch

Three things matter in the near term. First, the interest rate differential: with the RBI widely expected to hold rates at its June meeting and the US Federal Reserve signalling no cuts until September, the carry trade favouring Indian deposits remains attractive. Second, oil: Brent crude at $99 a barrel is the single largest drag on the rupee, and any de-escalation in the Gulf could trigger a sharp snap-back. Third, the AI trade: a sustained correction in Nasdaq — which fell sharply on 5 June — could redirect capital toward emerging markets, including India.

For most NRIs, though, the practical question is simpler: wire now or wait? The consensus among forex analysts is that the rupee's floor is close, making the current window an unusually good moment to move dollars into rupee assets — property, fixed deposits, or family obligations. Those who waited for 100 may never get there.

The rupee's slide is India's problem. For the diaspora, it is, perversely, a reason to send more money home."""
    },

    # ── Article 2 ──────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Gulf NRIs Are Buying Indian Stocks While Wall Street Runs for the Door. The Numbers Explain Why.",
        "subheadline": "Foreign institutional investors have yanked $31 billion from Indian equities this year. GCC-based NRIs, meanwhile, are doing the opposite — and SEBI just made it easier.",
        "slug": make_slug("gulf-nri-indian-equities-fpi-outflows-sebi"),
        "category": "nri-world",
        "vertical": "nri-world",
        "is_editorial": False,
        "diaspora_angle": "Gulf NRIs are taking a contrarian long-term bet on Indian equities even as global institutional money flees, reshaping how diaspora wealth flows into India's capital markets.",
        "tags": ["nri", "diaspora", "equities", "investment", "sebi", "gulf", "fpi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TodayTelugu", "url": "https://todaytelugu.net/en/business/why-gulf-nris-are-turning-to-indian-equities-as-real-estate-sees-an-exit-mou3sufh"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/fpis-withdraw-43000-crore-from-indian-equities-in-june-amid-global-ai-investments-2506076c8aeb/"},
            {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/money-and-banking/fpis-pull-out-43000-crore-in-first-week-of-jun-as-ai-trade-rupee-weakness-weigh-on-indian-equities/article69668845.ece"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-banks-could-raise-35-40-bln-via-rbis-foreign-currency-deposit-scheme-pnb-2026-06-09/"},
            {"name": "Ainvest (RBI measures)", "url": "https://www.ainvest.com/news/rbi-introduces-concessional-swaps-leverage-nri-deposits-boost-forex-inflows-2506093c3c57/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange in Mumbai; foreign investors have withdrawn a record ₹2.67 lakh crore from Indian equities in 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """The headline numbers are brutal. Foreign portfolio investors pulled ₹43,000 crore from Indian equities in the first week of June alone, bringing 2026's total outflow to ₹2.67 lakh crore — already dwarfing the ₹1.66 lakh crore withdrawn in all of 2025. The Nifty IT index has cratered 22 per cent this year. The rupee, pummelled by $99 oil and a global stampede toward American AI stocks, touched a record low of 96.96 against the dollar last month. By any conventional measure, Indian markets are in a buyer's strike.

Unless you happen to be an NRI in the Gulf.

## The contrarian bet

A recent survey of GCC-based Indians found that 73 per cent have increased their exposure to Indian equities over the past year, with many deploying fresh capital rather than merely riding existing positions. The shift represents something more structural than opportunistic bargain-hunting: Gulf NRIs are rotating out of their traditional favourite — Indian real estate — and into the stock market.

The reasons are partly mathematical. A Dubai-based software engineer earning in dirhams (pegged to the dollar) has watched her Indian stock portfolio decline 20 per cent in dollar terms. But she has also watched Indian property yields flatten at 2-4 per cent while Dubai apartments return 7-11 per cent. The calculation is straightforward: keep the apartment in JLT, sell the Pune flat, and funnel the proceeds into a diversified Indian equity portfolio trading at a significant discount to its September 2024 peak.

## SEBI opens the door wider

The timing is not coincidental. The Securities and Exchange Board of India has quietly expanded the welcome mat. Under the RBI's new guidelines, published on 9 June, investment limits for NRIs and overseas citizens of India in equity instruments have been raised without requiring SEBI registration. The facility has been extended to all individual Persons Resident Outside India — a category that captures a far wider pool than the traditional NRI definition.

This matters because the single biggest friction point for diaspora equity investors has been the KYC labyrinth. Opening a Portfolio Investment Scheme (PIS) account as an NRI typically requires weeks of paperwork, notarised documents from an Indian consulate, and a designated bank that may have no branch within 200 miles of the investor. SEBI's liberalisation doesn't eliminate the process, but it significantly reduces the barriers for smaller, non-institutional investors who want to buy into India without setting up a formal FPI structure.

## Why NRIs see it differently

The divergence between institutional and diaspora money tells a story about time horizons. FPIs are benchmarked quarterly. Their mandate is global allocation: when Nvidia is up 140 per cent in 18 months and the Nasdaq offers AI-fuelled returns unavailable in Mumbai, the capital goes where the momentum is. The Iran war, which has pushed Brent crude to $99, compounds the pain — India imports 85 per cent of its oil, and every dollar increase per barrel widens the current account deficit.

NRIs, by contrast, are playing a 20-year game. They know India's GDP growth story. They know that the Sensex, despite this year's foreign exodus, has compounded at roughly 12 per cent annually over two decades. Many have family wealth, property, and retirement plans rooted in India. Their equity allocation is not a tactical trade — it is an expression of conviction that India's underlying economy will outgrow its current turbulence.

The Goldman Sachs note published on 8 June reinforced this view, projecting the rupee's slide will stabilise around 96 as recent policy measures — including tax exemptions on government bonds, expanded FCNR deposit incentives, and broader foreign access to the Fully Accessible Route for sovereign debt — draw between $40 billion and $50 billion in fresh inflows.

## The risk NRIs are underpricing

Conviction is not the same as clairvoyance. The structural risks that drove FPIs out — weak corporate earnings growth, a depreciating currency, and India's limited exposure to AI-era technologies — are real, and NRI retail investors are not immune to them. Currency risk, in particular, is a blind spot: a further slide to 100 per dollar would wipe out another 4-5 per cent of any equity gain in dollar terms. The IT sector, once the diaspora's favourite proxy for Indian innovation, has been among the worst performers this year.

Still, for the Gulf NRI watching institutional money flee, there is a certain cold comfort in the contrarian position. The smart money, after all, has been wrong about India before — and the diaspora has a longer memory than most hedge funds.

Markets rotate. Capital flows reverse. But the NRI bet on India is as much emotional as it is financial. That is both its greatest strength and its most obvious vulnerability."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
