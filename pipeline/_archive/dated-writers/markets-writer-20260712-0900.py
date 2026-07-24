#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-12 09:00 PT"""
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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: TCS Forward-Deployed AI Engineers
# ─────────────────────────────────────────────────────────
art1_body = """TCS CEO K Krithivasan has revealed that India's largest IT services company is building a dedicated team of up to 8,900 forward-deployed engineers — specialists who embed directly with clients to accelerate AI adoption — while simultaneously hunting for acquisitions in artificial intelligence, data security, and cybersecurity.

The strategic pivot, disclosed in an exclusive Reuters interview published Saturday, positions TCS against an unusual set of competitors: not rival outsourcers like Infosys or Wipro, but the AI labs themselves — OpenAI, Anthropic, and Microsoft — all of which have expanded hiring for forward-deployed engineers (FDEs) to help enterprises operationalise AI tools.

## The Numbers Behind the Bet

Krithivasan's target of 1% to 1.5% of TCS's 593,000-strong workforce translates to roughly 5,900 to 8,900 dedicated FDEs. The CEO did not specify whether these would be external hires or retraining of existing staff, but the company's $1 billion annual spend on talent development — with a heavy focus on AI-native technologies — suggests a significant internal retraining pipeline.

The FDE push comes on the heels of TCS's strongest quarterly hiring in four years. The company added 9,279 employees on a net basis during the June quarter, its highest quarterly net addition since Q2 of fiscal 2023, even as concerns about AI-driven job losses continue to roil the sector.

TCS's annualised AI services revenue crossed $2.6 billion in Q1 FY27, up 13% quarter-on-quarter, though the pace of growth slowed from the 28% recorded in the previous quarter. Krithivasan said he would like the business to grow roughly 25% quarter-on-quarter over the long term but did not expect a linear trajectory.

## Why This Matters: AI as a Creator, Not a Destroyer

The broader context is a $315 billion Indian IT industry grappling with an existential question: will AI disrupt the traditional labour-intensive outsourcing model, or create new revenue streams?

Krithivasan dismissed the disruption thesis. "What you need is a deep knowledge of the customer environment to make it work. That is where we differentiate ourselves. This has nothing to do with cost arbitrage. It's essentially because of the talent pool that we have built," he told Reuters.

Companies increasingly use multiple AI models and require partners like TCS to integrate those models with existing systems and manage data flows, he argued. CFO Samir Seksaria confirmed TCS is evaluating acquisitions to "enhance our strategic positioning" — a departure from the company's decades-long preference for organic growth.

## The NRI Investor Angle

For NRI investors who own TCS shares — it remains one of the most widely held Indian stocks in overseas portfolios — the signals are mixed. The FDE strategy and acquisition appetite suggest management sees AI as a growth driver, not a threat. TCS's $2.6 billion AI revenue already exceeds the total revenue of many standalone AI startups.

But the deceleration in AI revenue growth (13% vs. 28% the prior quarter) and a 20% drop in total contract value to $9.5 billion in Q1 warrant caution. TCS shares have fallen more than 32% in 2026, compared with a 25% decline in the Nifty IT index, reflecting the sector's broader valuation compression.

Rivals Infosys, HCL Tech, and Wipro report their quarterly results later this month. Their commentary on AI-led demand — and whether they are pursuing similar FDE strategies — will determine whether TCS's playbook is an industry template or a solo bet.

The key question for the coming quarters: can TCS convert its FDE and acquisition strategy into accelerating AI revenue growth, or will the 13% Q-on-Q pace prove to be the new normal?"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Plans Up to 8,900 Forward-Deployed AI Engineers and Hunts for Acquisitions — What NRI Tech Investors Should Know",
    "subheadline": "India's largest IT firm is building an army of specialists who embed with clients to deploy AI, while eyeing its first major acquisitions in years. The strategy pits TCS against OpenAI and Anthropic, not just Infosys.",
    "slug": make_slug("tcs-8900-forward-deployed-ai-engineers-acquisitions-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRI tech investors holding TCS — one of the most widely held Indian stocks in overseas portfolios — get mixed signals: the FDE strategy and acquisition appetite suggest AI as a growth engine, but decelerating AI revenue growth and a 32% share price decline in 2026 demand careful portfolio review.",
    "tags": ["tcs", "artificial-intelligence", "it-sector", "nri-investing", "forward-deployed-engineers", "tech-strategy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tata-consultancy-services-plans-up-8900-ai-deployment-engineers-seeks-ai-2026-07-12/"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/corporate/tcs-ceo-says-ai-wont-kill-white-collar-jobs-as-tech-giant-adds-9279-employees"},
        {"name": "Reuters - TCS AI Momentum", "url": "https://www.reuters.com/world/india/indias-tcs-up-ai-momentum-fuels-revenue-beat-sector-recovery-gradual-analysts-say-2026-07-10/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Stock market data on a financial trading screen",
    "image_attribution": "Pexels",
    "body": art1_body,
}

# ─────────────────────────────────────────────────────────
# ARTICLE 2: 1% Remittance Tax — One Year Later
# ─────────────────────────────────────────────────────────
art2_body = """One year ago this week, President Donald Trump signed the One Big Beautiful Bill Act into law at a July Fourth ceremony at the White House. Buried within the sweeping tax and spending package was a provision that sent shockwaves through the Indian diaspora: an excise tax on international remittances sent by non-US citizens.

Twelve months later, confusion persists about what NRIs actually owe — and what they don't. Here is a clear-eyed breakdown of how the remittance tax works, who it hits, and the critical exemptions that most H-1B workers, green card holders, and NRI families need to understand.

## What the Law Actually Says

The final version of the remittance tax is significantly narrower than the proposals that generated headlines last year. The House of Representatives originally passed a 3.5% excise tax on remittance transfers by non-citizens. The Senate reduced the rate to 1%. The final signed law adopted the Senate's 1% rate.

That is a crucial distinction. Early reporting — and some trade body analyses — referenced the 3.5% or even 5% rate, projecting catastrophic impacts on India's $120 billion annual remittance inflows. The enacted rate of 1% is materially lower.

## The Exemptions That Change Everything

More important than the rate itself are the exemptions baked into the final law. The 1% excise tax applies only to remittance transfers funded by:

- Cash
- Money orders
- Cashier's checks
- Similar instruments, as determined by the Treasury Department

Transfers made from accounts held at US banks, credit unions, or broker-dealers — or funded with a US-issued debit or credit card — are **explicitly exempt** from the tax.

This means the overwhelming majority of NRI remittances are untouched. Most Indian professionals in the US send money home via bank wire transfers (through services like Wise, Remitly, or direct bank-to-bank transfers funded from a US checking account). These transactions fall squarely within the exemption.

The 1% tax primarily targets cash-based remittance services — walk-in money transfer operators where senders pay in cash — which account for a smaller and declining share of total US-to-India flows.

## The Real-World Impact

India received approximately $120 billion in remittances during 2023-24, with roughly 28% — about $33.6 billion — originating from the United States, according to the Global Trade Research Initiative (GTRI).

GTRI warned in a recent report that a 10-15% drop in remittance flows could result in a $12-18 billion annual shortfall for India. However, that analysis was based on the originally proposed 5% rate and did not account for the bank-transfer exemption in the final law.

With the enacted 1% rate applying only to cash-based transfers, the actual impact on total flows is likely a fraction of GTRI's estimate. Industry analysts suggest the effect on overall US-to-India remittances could be under 2%, as the vast majority of high-value transfers between NRI professionals and their families already flow through exempt banking channels.

## What NRIs Should Do Now

**Check your transfer method.** If you send money to India via bank wire, ACH transfer, or through a service funded by your US bank account or debit card, you are exempt. No action needed.

**Switch from cash-based services if applicable.** If you currently use a walk-in remittance service where you pay in cash, consider switching to a bank-funded digital service to avoid the 1% levy. Most digital remittance platforms (Wise, Remitly, Xoom) fund from bank accounts and qualify for the exemption.

**Factor it into property and education transfers.** For large one-time transfers — buying property in India, paying university fees, or sending lump sums for family — ensure the transfer originates from a US bank account. A $100,000 property transfer via a non-exempt channel would incur a $1,000 tax; via a bank wire, zero.

**Monitor for Treasury guidance.** The Treasury Department has authority to designate additional "similar instruments" subject to the tax. Future rulemaking could narrow or expand the exemption boundaries.

## The Rupee Effect

The Reserve Bank of India had flagged the remittance tax as a potential source of pressure on the rupee. BMI, a Fitch Group company, estimated that the Middle East conflict combined with reduced remittance flows could widen India's current account deficit by 0.4 percentage points to 1.3% of GDP.

However, with the final law's narrow scope, the currency impact appears modest. Goldman Sachs recently revised its rupee forecast stronger, projecting USD/INR at 94 in three months — suggesting the remittance tax, in its enacted form, is not a dominant driver of exchange rate dynamics.

For NRI families in states like Kerala, Uttar Pradesh, and Bihar — where remittances fund education, healthcare, and housing — the exemption for bank-funded transfers is the critical relief valve. The feared scenario of a broad-based tax on all remittances did not materialise."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "America's 1% Remittance Tax Is Already Law — Here's What Every NRI Needs to Know About Sending Money Home",
    "subheadline": "The One Big Beautiful Bill Act signed a year ago imposed a remittance tax on non-citizens — but the final 1% rate and critical bank-transfer exemptions mean most H-1B workers and green card holders are untouched. A practical guide.",
    "slug": make_slug("us-1-percent-remittance-tax-law-nri-exemptions-guide"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "H-1B workers, green card holders, and NRI families sending money to India are the primary audience. The article clarifies that most bank-funded transfers are exempt from the 1% remittance tax, and provides actionable steps for those using cash-based services to switch and save.",
    "tags": ["remittance-tax", "nri-personal-finance", "us-india", "one-big-beautiful-bill", "h1b", "money-transfer"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mintz Law - OBBBA Tax Analysis", "url": "https://www.mintz.com/insights-center/viewpoints/2026-07-one-big-beautiful-bill-act-signed-law-tax-implications-glance"},
        {"name": "GTRI Report via The Indian Eye", "url": "https://theindianeye.com/2025/05/18/5-tax-on-remittances-by-us-could-reduce-indias-dollar-inflows-by-10-15/"},
        {"name": "CNN - One Year Later", "url": "https://www.cnn.com/2026/07/12/politics/one-big-beautiful-bill-act-democrats-republicans-midterms/index.html"},
        {"name": "Greenberg Traurig - Senate Proposal Analysis", "url": "https://www.gtlaw.com/en/insights/2025/6/one-big-beautiful-bill-act-senate-proposal-would-limit-applicability-of-house-remittance-tax"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7136068/pexels-photo-7136068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Indian rupee banknotes in various denominations",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ─────────────────────────────────────────────────────────
# ARTICLE 3: Indian Banks FCNR(B) Dollar Drive
# ─────────────────────────────────────────────────────────
art3_body = """Indian banks are scrambling for international credit ratings as the Reserve Bank of India's special dollar-deposit window creates what analysts call the most attractive FCNR(B) opportunity for NRI depositors in over a decade.

Federal Bank, YES Bank, and Bank of Baroda have all secured or upgraded their global ratings in recent weeks, positioning themselves to attract foreign-currency deposits from the Indian diaspora at a time when the RBI has effectively uncapped interest rates on these instruments.

## The RBI's Dollar Drive

The centrepiece of the opportunity is the RBI's special forex swap window for FCNR(B) deposits, which went live on June 8 and remains operative until September 30, 2026. The window covers 3-to-5-year maturities and comes with two critical sweeteners:

**Interest rate caps have been removed.** Banks can now offer rates up to 7.1% on dollar-denominated FCNR(B) deposits — well above the approximately 4.5-5% available on standard US savings accounts or CDs. Before the RBI's intervention, the ceiling was tied to the US Fed Funds rate plus a spread, typically capping payouts around 5.5%.

**CRR and SLR exemptions apply.** Banks are freed from mandatory cash reserve and statutory liquidity requirements on these deposits, making it economically viable for them to offer the elevated rates.

Indian Bank's managing director Binod Kumar told reporters the public-sector lender has already raised $140 million in fresh FCNR(B) deposits since the window opened and is targeting $2 billion by September. "My plan is to raise around $2 billion in FCNR(B) deposits till September. It may seem high, but I already have a pipeline of $1 billion visible," Kumar said.

## The Rating Race

The parallel scramble for international credit ratings underscores how seriously Indian banks are pursuing NRI dollars.

Federal Bank received its first-ever international issuer credit rating — BBB-/Stable from S&P Global, the lowest investment-grade rating. YES Bank secured a BB+/Stable rating, one notch below investment grade, with S&P citing improving asset quality and strategic backing from Japan's SMBC. Bank of Baroda is planning to raise up to $1 billion through senior unsecured notes, with CareEdge Global assigning a BBB+/Stable rating.

"Global ratings are increasingly becoming a prerequisite for accessing overseas investors, issuing foreign-currency bonds, and mobilising FCNR deposits from non-resident Indians," a senior industry official told The Hindu BusinessLine. "An international rating provides comfort to global investors and can help banks lower overseas borrowing costs."

Among India's major banks, SBI, HDFC Bank, ICICI Bank, Axis Bank, Kotak Mahindra Bank, and Bank of Baroda now carry investment-grade international ratings — covering the institutions where most NRIs already hold accounts.

## What NRIs Should Know

**FCNR(B) deposits are denominated in foreign currency** — US dollars, British pounds, euros, Canadian dollars, Australian dollars, or Japanese yen. The principal and interest are fully repatriable, and there is no currency conversion risk for the depositor: you deposit dollars, you withdraw dollars.

**The interest income is exempt from Indian income tax** under current rules, making the effective yield more attractive than most onshore Indian fixed deposits, which are taxed at the individual's slab rate.

**The 3-to-5-year lock-in is real.** Premature withdrawal penalties apply, and the attractive rates are specifically tied to the September 30 window. Deposits placed after the window closes will revert to the standard ceiling-linked rates.

**Compare rates across banks.** Indian Bank is offering 6% currently; some private-sector banks like Bandhan Bank and DCB Bank offer domestic FD rates above 7%, but their FCNR(B) rates may differ. Check the specific FCNR(B) rate, not the headline domestic FD rate.

## Why the RBI Is Doing This

The special window is part of the RBI's broader strategy to rebuild foreign-exchange reserves, which stood at $674.2 billion as of July 3 — down from a peak of $728.5 billion in late February, before the Middle East conflict triggered capital outflows and rupee depreciation pressure.

Prime Minister Narendra Modi has publicly urged citizens to conserve forex by limiting foreign travel and fuel consumption. The FCNR(B) window is the monetary policy equivalent: incentivise NRIs to park their overseas savings in Indian banks, boosting the supply of dollars available to the central bank.

The last time the RBI deployed a similar scheme was in 2013, during the "taper tantrum" that triggered an external sector crisis. Indian Bank's Kumar noted that the current rush mirrors that earlier episode in both urgency and scale.

## The Bottom Line for NRI Depositors

For NRIs holding surplus dollars in low-yielding US savings accounts, the FCNR(B) window offers a rare combination: 6-7% returns in dollar terms, no Indian income tax, full repatriation, and backing from internationally rated banks. The window closes September 30. After that, the rates revert — and this particular opportunity will not be available until the RBI faces another dollar crunch."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian Banks Race for Global Ratings as RBI's FCNR Dollar Drive Opens a Rare Window for NRI Depositors",
    "subheadline": "Federal Bank, YES Bank, and Bank of Baroda have secured international credit ratings to attract NRI deposits, while the RBI's special swap window offers up to 7.1% on dollar deposits — tax-free — until September 30.",
    "slug": make_slug("indian-banks-global-ratings-rbi-fcnr-nri-deposit-window"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "NRIs holding surplus dollars in low-yielding US savings accounts have a time-limited opportunity to earn 6-7% in dollar terms through FCNR(B) deposits at internationally rated Indian banks — tax-free under Indian law, fully repatriable. Window closes September 30, 2026.",
    "tags": ["fcnr-deposits", "rbi", "nri-banking", "indian-banks", "dollar-deposits", "forex-reserves"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine - Banks Global Ratings", "url": "https://www.thehindubusinessline.com/money-and-banking/banks-rush-for-global-ratings-as-fcnr-b-fund-raising-gains-momentum/article69774370.ece"},
        {"name": "The Hindu BusinessLine - Indian Bank FCNR Target", "url": "https://www.thehindubusinessline.com/money-and-banking/indian-bank-gets-140-million-in-fresh-fcnrb-deposits-after-rbi-rule-targets-2-billion-by-september/article69787073.ece"},
        {"name": "Outlook Business - Forex Reserves", "url": "https://business.outlookindia.com/news/indias-forex-kitty-jumps-726-bn-to-67419-bn"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_01.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ─────────────────────────────────────────────────────────
# Publish
# ─────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone — {len(articles)} articles submitted at {now}")
