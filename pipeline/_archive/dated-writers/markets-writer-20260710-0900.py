#!/usr/bin/env python3
"""Markets & Finance writer — July 10, 2026 morning run."""
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

# ─────────────────────────────────────────────
# ARTICLE 1: SP Group's Debut Dollar Bond
# ─────────────────────────────────────────────
art1_body = """India's Shapoorji Pallonji Group finally opened its first-ever U.S. dollar bond issue on Friday, looking to raise $650 million in what has become one of the most closely watched corporate debt deals in Indian markets this year.

The bond issue, delayed multiple times since the start of 2026, is part of the conglomerate's planned ₹255 billion ($2.68 billion) fundraise — the bulk of which will go toward refinancing existing high-yield debt. Mercury Finance, an SP Group entity, is selling three-year securities at a yield of 14.50%, with a right to redeem them at the end of one year, according to three sources familiar with the matter cited by Reuters.

## Why This Deal Matters

Deutsche Bank is the sole arranger for the issue and has underwritten part of it. More significantly, BlackRock — the world's largest asset manager with over $11 trillion under management — is expected to invest $100 million to $200 million through an Asia-focused fund, a move likely to reassure other institutional investors eyeing the deal.

The SP Group's debt saga is inseparable from its relationship with Tata Sons. The group is a major shareholder in the unlisted Tata holding company, and uncertainty over whether it can unlock that investment has been the primary reason for repeated delays. Markets had been watching whether SP Group could monetise its Tata Sons stake to service its debt — a question that has persisted since the group's acrimonious split with the Tata family in 2020.

## The Numbers Tell a Story

Alongside the dollar bond, another SP Group entity — Eqyizen Investment — will sell three-year zero-coupon bonds at a yield of 18.95% for the remaining amount. For context, these yields are eye-wateringly high by global standards but reflect the group's credit profile: CareEdge Ratings recently downgraded bonds of Goswami Infratech, another SP Group company, to B+ from BB-, citing delays in group-level fundraising.

The group previously raised ₹143 billion through zero-coupon bonds in June 2023, selling them to foreign private credit funds at a yield of 18.75%. It has since extended the maturity of those notes twice, most recently to July 31 from June 30.

## What Changed Now

Sources told Reuters that easing hedging costs — a direct result of the Reserve Bank of India's measures to encourage dollar inflows — helped turn the tide. The RBI's subsidised forex swap facility and other liquidity measures announced in June have materially reduced the cost of hedging rupee exposure, making Indian corporate dollar bonds more attractive to foreign investors.

## The NRI Investor Angle

For NRI investors watching India's corporate bond market, this deal is a bellwether. A 14.5% dollar-denominated yield from an Indian conglomerate with a legitimate (if complicated) Tata Sons connection represents the kind of risk-reward that India's private credit market is increasingly offering. BlackRock's participation signals that the world's biggest money managers see value in Indian high-yield credit despite the elevated risk.

The deal also highlights a broader trend: Indian corporates are tapping global debt markets more aggressively, encouraged by RBI policies that have lowered hedging costs. For NRIs who typically park money in NRE fixed deposits yielding 7-8%, the emergence of a deeper Indian corporate bond market — accessible through global funds — opens new avenues for portfolio diversification.

The SP Group deal is expected to close in the coming days. If successful, it could pave the way for more Indian conglomerates to access dollar debt markets in the second half of 2026."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Shapoorji Pallonji Launches $650 Million Dollar Bond With BlackRock Backing — What NRI Investors Should Know About India's Hottest Debt Deal",
    "subheadline": "The Tata Sons-linked conglomerate's debut dollar bond at 14.5% yield has drawn Deutsche Bank as arranger and BlackRock as a likely investor, signalling growing global appetite for Indian high-yield corporate credit.",
    "slug": make_slug("shapoorji-pallonji-650-million-dollar-bond-blackrock-nri-india-debt"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "The deal signals maturing Indian corporate debt markets with yields far above NRE deposits — NRI investors can access this via global credit funds like BlackRock's Asia-focused vehicle, diversifying beyond traditional FD and equity exposure.",
    "tags": ["markets", "finance", "bonds", "shapoorji-pallonji", "blackrock", "tata-sons", "nri-investing", "corporate-debt"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-sp-group-opens-debut-dollar-debt-issue-after-multiple-delays-sources-say-2026-07-10/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/blackrock-invest-indias-shapoorji-pallonji-unit-dollar-debt-sources-say-2026-05-07/"},
        {"name": "CareEdge Ratings", "url": "https://www.careratings.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5476028/pexels-photo-5476028.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Indian currency notes representing the corporate debt market",
    "image_attribution": "Ravi Roshan / Pexels",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: Rate-Hike Bets Collapse / Record OIS Swap Day
# ─────────────────────────────────────────────
art2_body = """Foreign investors are aggressively unwinding bets on interest rate hikes in India, pushing turnover in the country's five-year overnight index swap (OIS) market to an all-time record and sending a powerful signal: the worst fears about monetary tightening are fading.

Turnover in the five-year OIS — the closest gauge of where markets think the Reserve Bank of India's policy rate is headed — surged to a record ₹253 billion ($2.65 billion) on Wednesday, smashing through the previous day's ₹236 billion record. The volume was nearly three times the average daily turnover so far this year, according to Reuters.

## From Panic to Pivot

The reversal has been dramatic. In April, as the Iran conflict drove oil above $100 a barrel and the rupee tumbled to a record low of 96.96 per dollar on May 20, swap markets had priced in up to 125 basis points of rate increases — essentially betting that the RBI would be forced into an aggressive tightening cycle to defend the currency and contain inflation.

Those bets have since collapsed. The five-year OIS rate fell to a four-month low of 6.1% this week, just 10 basis points above where it stood before the Iran conflict began. The swing from 6.9% to 6.1% represents a fundamental reassessment of India's monetary outlook.

"Some market participants had accumulated sizeable positions for a series of front-loaded rate hikes in quick succession on concerns over inflation and rupee weakness," Mandar Pitale, head of treasury at SBM Bank (India), told Reuters. "Those positions are being unwound aggressively."

## What Changed

The RBI's June policy package was the catalyst. The central bank unveiled a series of measures to boost dollar inflows and support the rupee, including a subsidised forex swap facility for banks' overseas borrowings and permission for banks to lend to non-residents against foreign currency deposits.

These measures had two effects: they directly attracted dollar flows into India, and they signalled that the RBI had tools beyond rate hikes to manage currency pressure. Markets took the hint. If the RBI can stabilise the rupee through liquidity management rather than rate increases, the case for monetary tightening weakens considerably.

The rupee has responded, climbing 1.5% from its May 20 record low — though it came under fresh pressure this week after U.S. President Donald Trump declared the Iran ceasefire "over."

"Expectations of sizeable foreign-exchange inflows have improved sentiment toward the rupee, limiting the risk that currency volatility could push offshore OIS rates higher," Duncan Tan, APAC rates strategist at HSBC, said in a note on Wednesday.

## What This Means for NRI Investors

The collapse in rate-hike expectations carries direct implications for NRI portfolios across multiple asset classes.

**Indian bonds become more attractive.** If the RBI holds rates steady — or even resumes cutting later this year — bond prices will rise. Foreign investors have already responded, buying a net ₹346 billion ($3.6 billion) in Fully Accessible Route government bonds in just five weeks since June 1. A potential inclusion in the Bloomberg Global Aggregate Index could supercharge these flows.

**NRE/NRO deposit rates may not rise further.** NRIs hoping for higher fixed deposit rates on their India accounts are unlikely to see them if the RBI stays pat. Current NRE FD rates of 7-7.5% may represent the cycle peak.

**Equity sentiment improves.** Lower rate-hike fears reduce the discount rate for Indian equities and signal that the RBI prioritises growth support over aggressive inflation fighting. Bank stocks, which are sensitive to the rate outlook, have already led the recent rebound.

**Rupee remittance window narrows.** The rupee's recovery from 96.96 means NRIs sending money home are getting fewer rupees per dollar than they were six weeks ago. The current rate of approximately 95.58 still represents a historically weak rupee, but the trend is moving against remitters.

The swap market's verdict is clear: India's monetary tightening scare is over. For NRI investors, the signal is to position for a stable-to-easing rate environment — not the emergency hiking cycle that markets feared just three months ago."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Rate-Hike Fears Collapse as Traders Dump Bets in Record $2.65 Billion Swap Day — What It Means for NRI Portfolios",
    "subheadline": "The five-year OIS rate has plunged from 6.9% to 6.1% since April as markets abandon expectations of aggressive RBI tightening, signalling a turning point for Indian bonds, bank stocks and NRE deposit rates.",
    "slug": make_slug("india-rate-hike-fears-collapse-record-swap-ois-rbi-nri-bonds"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "The rate-hike scare's end means NRE/NRO deposit rates may have peaked, Indian bonds are rallying, and the rupee remittance window is narrowing — NRIs should reassess fixed-income allocations and remittance timing.",
    "tags": ["markets", "finance", "rbi", "interest-rates", "ois-swap", "bonds", "nri-investing", "rupee", "monetary-policy"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/foreign-investors-pare-india-rate-hike-bets-fuel-record-5-year-swaps-trading-2026-07-08/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-rupee-track-merchant-flows-dollar-bonds-await-foreign-buying-cues-2026-07-06/"},
        {"name": "HSBC Research", "url": "https://www.hsbc.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_04.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 3: India Weathers $48B Capital Flight
# ─────────────────────────────────────────────
art3_body = """India has just survived the worst sustained foreign capital exodus in its market history — and emerged in better shape than almost anyone expected. Now, as foreign money tentatively returns, the dynamics underpinning India's resilience hold crucial lessons for NRI investors.

Over the past 18 months, foreign portfolio investors (FPIs) pulled a record $48 billion out of Indian equities, initially chasing artificial intelligence and chip-related stocks in Taiwan and South Korea, then fleeing emerging markets entirely as the Iran conflict roiled global risk appetite. By any historical measure, this should have been devastating.

It wasn't. And the reason is India's domestic investor base.

## The $3.5 Billion Monthly Floor

Indian retail investors — the "mom-and-pop" investors who have been pouring money into mutual funds through systematic investment plans (SIPs) — kept adding approximately $3.5 billion a month throughout the entire selloff, according to Reuters Breakingviews. This relentless domestic buying put a floor under valuations that foreign sellers couldn't break, keeping Indian markets from the kind of deep corrections that hit other emerging economies.

The result: despite $48 billion of outflows, Indian equity valuations remain elevated by global emerging-market standards. Bargain hunters arriving late are finding slim pickings — a testament to how fundamentally India's market structure has changed.

## The Turn Has Begun

Foreign investors are now cautiously returning. FPIs pumped a net $401 million into Indian equities during the first five trading sessions of July, according to National Securities Depository (NSDL) data. In the second half of June, they turned net buyers for the first time in four months, with overall inflows of ₹141 billion ($1.48 billion).

Banking stocks led the inflows. FPIs bought ₹146 billion ($1.54 billion) of banking stocks in the second half of June alone — the biggest fortnightly inflows into the sector in 14 months. Bank Nifty gained 6.1% in June, leading the Nifty 50's 1.4% rise.

"My sense is that the worst of the FPI selling is over and outflows will reduce significantly," Abhay Laijawala, chief investment officer for India at Lighthouse Canton, told Reuters. "Meaningful FPI buying in large banks, aided by a steady earnings outlook, could be enough to power Nifty higher after the 2026 underperformance so far."

## What's Drawing Foreign Money Back

Three policy shifts are pulling capital back to India:

**Tax overhaul for foreign investors.** The government scrapped capital gains tax for FPIs and removed the 20% tax on interest income from such investments, effective April 1, 2026. This materially improves after-tax returns for foreign portfolio allocators.

**RBI's liquidity toolkit.** The Reserve Bank of India extended a subsidised forex swap facility for banks' overseas borrowings and allowed banks to lend to non-residents against foreign currency deposits. Citi Research noted these measures could help banks narrow loan-to-deposit gaps, lower new deposit costs and improve margins.

**Bond market magnetism.** Foreign investors have bought a net ₹346 billion ($3.6 billion) in Fully Accessible Route (FAR) government bonds in just five weeks since June 1. A potential inclusion of Indian government bonds in the Bloomberg Global Aggregate Index — Bloomberg said in its January review that it would release its next update mid-2026 — could trigger billions more in passive inflows.

## Why NRIs Should Pay Close Attention

The turning of the FPI tide matters directly to NRI investors for several reasons.

**Your Indian equity holdings may be bottoming.** If you held Indian mutual funds or direct equity through the selloff, the worst of the foreign-driven pressure is likely behind. The combination of resumed FPI buying and continued domestic SIP flows creates a supportive backdrop for the second half of 2026.

**The tax changes benefit you too.** The scrapping of capital gains tax for FPIs and the removal of the 20% interest income tax also improve the tax environment for NRI investments, depending on your specific tax residency and treaty situation. Consult your cross-border tax advisor on whether these changes apply to your holdings.

**India's structural resilience is proven.** The 18-month stress test demonstrated that India's markets are no longer hostage to foreign capital flows. A domestic investor base adding $3.5 billion monthly through SIPs provides a structural cushion that didn't exist even five years ago. For NRIs making long-term allocation decisions, this resilience is a genuine differentiator versus other emerging markets.

**Bond allocation opportunity is growing.** With $3.6 billion of foreign money flowing into FAR bonds in five weeks and Bloomberg index inclusion potentially imminent, Indian government bonds are becoming a legitimate fixed-income allocation for global portfolios — including NRI portfolios managed through offshore accounts.

The message from global capital markets is simple: India's worst foreign exodus is over, and the country's domestic investor base has permanently altered the risk profile of Indian equities. For NRI investors, it's time to reassess India allocations with fresh eyes."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Survived a Record $48 Billion Foreign Exodus — And Came Out Stronger. Here's What NRI Investors Need to Know",
    "subheadline": "Domestic investors adding $3.5 billion a month cushioned the blow as foreign money fled. Now FPIs are returning, tax barriers are falling and Bloomberg bond index inclusion looms — a turning point for India allocations.",
    "slug": make_slug("india-48-billion-fpi-exodus-resilience-domestic-investors-nri"),
    "category": "markets-finance",
    "vertical": "markets-finance",
    "diaspora_angle": "India's structural market resilience — proven by $3.5B/month domestic SIP flows absorbing record FPI outflows — combined with new tax breaks and bond index inclusion, makes the case for NRIs to reassess India equity and fixed-income allocations.",
    "tags": ["markets", "finance", "fpi", "foreign-investors", "nri-investing", "mutual-funds", "sip", "bonds", "bloomberg-index", "indian-equities"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters Breakingviews", "url": "https://www.reuters.com/commentary/breakingviews/worst-global-money-exodus-barely-bruises-india-2026-07-08/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/policy-support-lifts-foreign-inflows-into-indian-banks-14-month-high-2026-07-07/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-rupee-track-merchant-flows-dollar-bonds-await-foreign-buying-cues-2026-07-06/"},
        {"name": "NSDL", "url": "https://www.nsdl.co.in"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/BSE_building_at_Dalal_Street.JPG/1280px-BSE_building_at_Dalal_Street.JPG",
    "image_caption": "The Bombay Stock Exchange building on Dalal Street in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────
# PUBLISH
# ─────────────────────────────────────────────
articles = [art1, art2, art3]
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted to review.")
