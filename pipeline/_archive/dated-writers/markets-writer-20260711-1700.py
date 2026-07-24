#!/usr/bin/env python3
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
    {
        "id": str(uuid.uuid4()),
        "headline": "SEBI Wants to Double the Stocks You Can Short — And India's $5 Trillion Market Is About to Get a Lot More Interesting for NRIs",
        "subheadline": "India's market regulator is planning to nearly double stocks eligible for lending and borrowing from 176 to over 300, while cutting collateral from 130% to near-global levels — a move aimed at pulling retail investors away from the world's largest and riskiest derivatives market.",
        "slug": make_slug("sebi-double-shortable-stocks-collateral-cut-nri-derivatives"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI investors trading Indian equities through PIS accounts and GIFT City brokerages will benefit from deeper cash market liquidity and lower margin requirements, making hedging positions cheaper and more flexible",
        "tags": ["sebi", "stock-lending", "derivatives", "nri-investing", "nse", "cash-market", "shorting"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/government/india-aims-make-it-easier-short-by-nearly-doubling-stocks-eligible-borrowing-2026-07-06/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/markets/sebi-approves-nifty-fpi-150-index-derivatives"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange in Mumbai, India's oldest stock exchange",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "body": """India's securities regulator is quietly laying the groundwork for the most significant overhaul of its cash equities market in years — and NRI investors with portfolios in Indian stocks should pay attention.

The Securities and Exchange Board of India (SEBI) is planning to nearly double the number of stocks eligible for lending and borrowing, from the current 176 to over 300, according to people with direct knowledge of the plans. Simultaneously, the regulator intends to cut the collateral requirements from a punishing 130% — far above the roughly 100% standard in the United States and Europe — to a level closer to global norms.

## Why Only 176 Stocks?

The restriction is a legacy of India's history with stock market fraud. Scams in the early 2000s led regulators to impose strict rules on the cash equities market, tightened further between 2017 and 2020. The result: while the National Stock Exchange lists some 2,600 companies, only 176 currently qualify for borrowing and lending under criteria that include minimum monthly trading turnover of ₹1 billion ($10.5 million), sufficient derivatives exposure capacity, and adequate public shareholding.

The three main eligibility thresholds are under active review. "Deliberations are on relaxing the two thresholds," one source told Reuters, with details likely to be finalised by the end of 2026.

## The Derivatives Problem SEBI Is Trying to Solve

The expansion isn't happening in a vacuum. India operates the world's largest derivatives market — and the imbalance with its cash market has become a regulatory headache. Capital deployed in derivatives is roughly three times that of the cash market, while the gross contract value is nearly 500 times larger. That ratio is far higher than in any major global market.

The human cost is stark: SEBI's own data shows that nearly 90% of retail investors trading derivatives lose money. The government has spent the last 18 months raising the cost of derivative trading to discourage speculation. Expanding the cash market's borrowing and lending infrastructure is the carrot to complement that stick.

## The FPI 150 Play

In a parallel move, SEBI has also approved derivatives on the Nifty India FPI 150 Index — an index specifically designed for foreign portfolio investors, tracking 150 domestically listed stocks selected based on their accessibility to overseas funds. The new futures and options contracts will give foreign investors a dedicated hedging instrument that aligns with their regulatory and liquidity constraints.

The timing is strategic. Foreign investors have turned net buyers after four consecutive months of selling, pouring $401 million into Indian equities in the first five trading sessions of July. The FPI 150 derivatives give them another reason to stay.

## What This Means for NRI Investors

For NRIs trading Indian equities through Portfolio Investment Scheme (PIS) accounts or GIFT City-based brokerages, the reforms address two longstanding frustrations.

First, a larger universe of shortable stocks means better hedging. Currently, if an NRI holds a mid-cap stock outside the 176-name list, there's no exchange mechanism to borrow shares for hedging or income generation. Doubling that list to include the majority of liquid shares changes the calculus for portfolio construction.

Second, lower collateral requirements free up capital. At 130%, India's current margin rules lock up significantly more cash per position than equivalent trades in New York or London. Bringing that closer to 100% aligns India with global standards and makes the cash market more capital-efficient for cross-border investors.

One caveat: SEBI is unlikely to allow off-exchange stock lending and borrowing, despite lobbying from foreign investors. The regulator believes all trading activity should flow through exchanges to pool liquidity — a structural difference from Western markets that NRIs accustomed to broker-facilitated lending should note.

## The Bigger Picture

These reforms arrive as India's equity market reaches a milestone moment. NSE's market capitalisation has surged from $1 trillion a decade ago to over $5 trillion today, and the exchange itself is preparing for an IPO that would pitch India's capital market deepening as a global growth story.

For NRI investors, the message is clear: India's market infrastructure is being systematically upgraded to match its scale. The question isn't whether these reforms will happen, but whether the current crop of 176 eligible stocks will look quaintly restrictive by this time next year.

Details are expected by year-end. NRIs with active Indian portfolios should factor the expanded hedging universe into their 2027 investment planning."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Scraps Import Duties on Smartphone Parts and Lithium-Ion Cells — A $500 Billion Bet on Becoming the World's Electronics Factory",
        "subheadline": "New Delhi removes 5% and 7.5% levies on wireless charging modules, automotive displays, and battery cells in a move that benefits Apple and Xiaomi while targeting a 28-fold production growth encore by 2030.",
        "slug": make_slug("india-scraps-import-duty-smartphone-lithium-ion-electronics-manufacturing"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI investors with exposure to Apple, Foxconn, Tata Electronics, and Indian EV battery plays stand to benefit as duty-free lithium-ion cell imports accelerate domestic manufacturing scale and attract fresh FDI into India's electronics corridor",
        "tags": ["electronics-manufacturing", "apple-india", "lithium-ion", "import-duty", "nri-investing", "ev-battery", "make-in-india"],
        "urgency": "medium",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/india-removes-import-duty-some-electronics-smartphone-parts-2026-07-09/"},
            {"name": "Grant Thornton Bharat", "url": "https://www.grantthornton.in/"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4211136/pexels-photo-4211136.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Circuit board and electronics components in a manufacturing facility",
        "image_attribution": "Andrey Matveev / Pexels",
        "body": """India has eliminated import duties on a targeted set of electronics and smartphone components — a surgical policy move that signals New Delhi's determination to capture a larger share of the global electronics manufacturing chain, and one that carries direct implications for NRI investors watching the India manufacturing story.

The government scrapped the existing 5% and 7.5% levies on parts used to produce wireless charging modules for mobile phones, displays for medical devices and automobiles, and critically, lithium-ion cells used in batteries. The exemption is valid until March 31, 2029, giving manufacturers a nearly three-year runway to scale operations.

## The Numbers Behind the Ambition

India's smartphone production has already undergone a transformation that most NRI investors underestimate. Over the past decade, output has risen 28-fold to ₹5.45 trillion ($57 billion) in the 2024-25 fiscal year. The country now targets $500 billion in total electronics manufacturing by fiscal year 2030 — a goal that requires sustained policy support of exactly this kind.

"This should boost cost competitiveness, domestic value addition and localisation of high-value smartphone and electronics manufacturing," said Manoj Mishra, a partner at Grant Thornton Bharat.

The beneficiaries are obvious: Apple, which has aggressively expanded iPhone production in India through its contract manufacturers Foxconn and Tata Electronics, and Xiaomi, which dominates India's smartphone market by volume. Both companies source components globally and assemble in India, meaning every percentage point of duty reduction flows directly to their cost structures.

## The Lithium-Ion Play Is the Real Story

While the smartphone duty cuts grab headlines, the lithium-ion cell exemption may have a larger long-term impact. India's electric vehicle market is growing rapidly, but domestic battery manufacturing remains in its infancy. The country currently imports virtually all its lithium-ion cells, primarily from China, South Korea, and Japan.

By removing the 5% duty on cell imports, New Delhi is making a calculated trade-off: sacrifice near-term customs revenue to accelerate the development of a domestic battery assembly and pack manufacturing ecosystem. The logic is that companies will be more willing to invest in Indian gigafactories if they can import cells duty-free while building local capacity.

"Exemption for lithium-ion cell manufacturing may spur investment in domestic battery production for electronics and electric mobility," Mishra noted.

This connects to India's broader Production-Linked Incentive (PLI) schemes for advanced chemistry cell manufacturing, which have attracted commitments from players including Reliance New Energy, Ola Electric, and Amara Raja. NRI investors who have been tracking India's EV story through listed names like Tata Motors, Mahindra & Mahindra, and Exide Industries should factor in the improved economics that duty-free cell imports bring to the entire value chain.

## Where the India-China Rivalry Plays Out

The duty removal also has a geopolitical dimension. As the U.S.-China technology decoupling deepens, India is positioning itself as the alternative manufacturing destination for companies seeking to diversify away from Chinese supply chains. Apple's decision to manufacture its latest iPhone models in India — shipping them to global markets, not just selling domestically — is the most visible example.

But India needs to remain cost-competitive. Vietnam and Indonesia are competing aggressively for the same manufacturing investment, often with their own duty concessions and incentives. The component duty elimination keeps India in the race by ensuring that the "Make in India" cost advantage doesn't erode at the component-import stage.

## What NRI Investors Should Watch

For NRIs with portfolios spanning both U.S. tech stocks and Indian industrials, this policy creates a dual opportunity. On the U.S. side, Apple's India manufacturing expansion improves its supply chain resilience and margins — a positive for AAPL holders. On the Indian side, the companies building the manufacturing ecosystem — from Tata Electronics (still private, but Tata Group is publicly listed) to Dixon Technologies (the largest Indian contract electronics manufacturer) to battery plays like Amara Raja — are the direct beneficiaries.

The ₹5.45 trillion smartphone production figure is impressive, but it's the trajectory that matters. India went from near-zero to $57 billion in a decade. The next decade's target is nearly ten times that. For NRI investors, the question isn't whether Indian electronics manufacturing will grow, but which layer of the value chain will generate the best returns.

The duty exemption is valid until 2029, providing a clear policy certainty window — something investors can actually plan around."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Hits Record 4.93 Million Barrels Per Day in Crude Imports — And Russia Now Supplies More Than Half",
        "subheadline": "As the Strait of Hormuz flares up again, India's crude supply story is one of diversification and resilience. But LPG and LNG — the fuels that heat 335 million Indian kitchens — remain dangerously exposed.",
        "slug": make_slug("india-record-crude-imports-russia-half-hormuz-lpg-risk-nri"),
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI investors worried about their Indian portfolio exposure to oil shocks should note that crude supply is well-diversified, but rising LPG and LNG costs could squeeze consumer spending and FMCG earnings — a second-order hit to Indian equities",
        "tags": ["crude-oil", "russia-india", "hormuz", "lpg", "energy-security", "nri-investing", "oil-imports"],
        "urgency": "high",
        "is_editorial": False,
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/commodities/indias-crude-imports-remain-resilient-despite-strait-of-hormuz-tensions/article71202081.ece"},
            {"name": "Reuters", "url": "https://www.reuters.com/business/energy/"},
            {"name": "Kpler", "url": "https://www.kpler.com/"},
            {"name": "International Energy Agency", "url": "https://www.iea.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/11347815/pexels-photo-11347815.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An oil refinery complex at dusk, representing India's growing energy infrastructure",
        "image_attribution": "Picas Joe / Pexels",
        "body": """India's crude oil imports surged to a record 4.93 million barrels per day in June, a number that tells a story far more nuanced than the panic headlines about the Strait of Hormuz might suggest. For NRI investors watching their Indian portfolios through the lens of oil prices and macro stability, the latest data reveals a supply chain that has been quietly but fundamentally rewired.

The most striking shift: Russian crude now accounts for more than half of India's total imports. At approximately 2.7 million bpd in June, Russia has cemented its position as India's largest oil supplier by a wide margin — a geopolitical realignment that would have been unthinkable five years ago and one that has profound implications for how India weathers energy crises.

## The Hormuz Question

The latest exchange of fire between the U.S. and Iran has renewed concerns about the Strait of Hormuz, through which roughly one-fifth of the world's daily oil supply transits. Four oil and gas tankers turned back from the strait this week after attacks on vessels, including an Indian-flagged Very Large Crude Carrier carrying 2 million barrels of Kuwaiti crude that made a U-turn off the tip of Oman.

But for India specifically, the impact on crude supply is limited. According to Sumit Ritolia, lead research analyst for refining and modelling at data firm Kpler, Indian refiners have spent the past 100 days managing supply through a diversified import portfolio with minimal disruption.

"Crude flows through the Strait had not fully recovered before the latest escalation," Ritolia said. "For India, however, it has largely been business as usual."

The diversification runs deeper than Russia alone. Saudi Arabia and UAE supplies are increasingly routed through bypass infrastructure that provides an additional layer of security. West African and Latin American grades have filled gaps in refinery feedstock. Iranian crude, despite the theoretical availability, is unlikely to become meaningful for Indian refiners due to sanctions compliance risks.

## The Real Vulnerability: LPG and LNG

Here's where the reassuring narrative breaks down, and where NRI investors need to think more carefully about second-order effects.

While crude supply is well-diversified, liquefied petroleum gas (LPG) and liquefied natural gas (LNG) remain dangerously exposed to Gulf supply disruptions. These fuels have fewer short-term substitution options than crude oil, and India's dependence on them is enormous: LPG is the primary cooking fuel for over 335 million Indian households.

"A prolonged period of instability could tighten availability, increase freight costs, and add pressure to regional prices again, as we have seen over the last few months," Ritolia warned.

The International Energy Agency added to the concern in its latest monthly report, noting that while global oil supply jumped 4.1 million bpd in June as the Strait partially reopened, production remained 9.4 million bpd below pre-war levels. The IEA's forecast of a significant oil market surplus in 2027 is now contingent on improved Hormuz transits — and the latest escalation "could upend" that outlook entirely.

## What NRI Portfolios Should Prepare For

For NRI investors, the crude supply resilience is genuinely good news for India's macro stability. The current account deficit won't blow out the way it might have a decade ago, when India was far more dependent on Middle Eastern crude. The rupee, which fell to a record low of 96.96 per dollar on May 20 but has since recovered 1.5%, has enough macro cushion to absorb the current oil price levels.

But the LPG and LNG vulnerability creates a different kind of risk. If Hormuz disruptions persist and cooking fuel costs spike, the government faces a political choice: absorb the cost through subsidies (widening the fiscal deficit) or pass it to consumers (squeezing household spending). Either path has implications for Indian equities.

The subsidy route pressures government finances and could delay infrastructure spending — negative for construction, cement, and capital goods stocks. The pass-through route hits consumer spending, which is the primary growth engine for India Inc. — negative for FMCG, consumer durables, and auto companies.

Brent crude edged down to $76 on Friday, extending a 2.2% fall from Thursday, but remains set for a weekly gain. For now, the market is pricing in the Hormuz situation as a manageable disruption rather than a crisis. But as Ritolia put it: "The key variables to watch are how long regional tensions persist, the impact on shipping and insurance costs, and whether LPG and LNG markets begin to experience more meaningful disruptions."

For NRIs with Indian equity exposure, the crude import data is reassuring. The LPG data is the one to watch."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
