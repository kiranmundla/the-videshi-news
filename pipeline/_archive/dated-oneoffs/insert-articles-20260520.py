#!/usr/bin/env python3
"""Insert 3 articles into p2_articles using stdin pipe for body content."""
import json, os, uuid, subprocess, sys
from datetime import datetime, timezone

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REST = f"{SB_URL}/rest/v1"
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sb_post_stdin(table, data):
    """POST using stdin to avoid shell escaping issues."""
    payload = json.dumps(data)
    cmd = [
        "curl", "-s", "-X", "POST", f"{REST}/{table}",
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", "@-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, input=payload)
    try:
        return json.loads(result.stdout)
    except:
        return {"raw": result.stdout[:500], "err": result.stderr[:200]}

def sb_patch(table, filt, data):
    cmd = [
        "curl", "-s", "-X", "PATCH", f"{REST}/{table}?{filt}",
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", json.dumps(data)
    ]
    subprocess.run(cmd, capture_output=True, text=True)


# ── Article 1: Amazon H-1B (nri-world) ──

a1_body = """Amazon.com Services LLC filed 33,181 Labor Condition Applications — the federal prerequisite for H-1B, H-1B1, and E-3 visas — in the second quarter of fiscal year 2026, according to newly released Department of Labor data. Over the same period, the company eliminated roughly 30,000 corporate roles across two layoff waves.

The juxtaposition is not unique to Amazon. The same DOL dataset shows Qualcomm Technologies leading with 59,379 certified positions, followed by Goldman Sachs entities combining for over 42,000, Cisco at 11,879, Apple at 9,218, and NVIDIA at 7,663. Across all employers, software developers accounted for 151,458 certified positions — 32.1 per cent of the total — followed by electronics engineers, IT project managers, and data scientists.

## The Paradox That Defines an Era

An LCA certification is not the same as a visa being issued. It is, however, the official starting gate: without it, an employer cannot proceed through the H-1B lottery or file an extension. When companies are simultaneously downsizing domestic workforces and building massive foreign-labour pipelines, the disconnect raises questions that neither corporate HR departments nor Congressional offices have been eager to answer.

For the roughly 600,000 Indian nationals currently in the H-1B system — many of whom have waited a decade or more for permanent residency — the numbers carry a double edge. On one hand, the sheer volume of certifications signals that employer demand for skilled foreign talent has not collapsed, despite the layoff headlines. On the other, it underscores a system where their labour is valued as fungible input, requested in bulk and discarded in batches, with little regard for the human beings caught in between.

## What the Critics Are Saying

The backlash has been fierce. Legislative proposals including the 'End H-1B Visa Abuse Act' and the 'EXILE Act' are gaining bipartisan attention, and a new $100,000 employer fee on certain H-1B filings — designed to make bulk applications more expensive — has already taken effect. Critics argue the data reveals a "coordinated labour replacement machine" using "immigration, offshoring, layoffs, and AI" in concert.

Microsoft's $17.5 billion investment in Indian AI and cloud infrastructure, announced alongside domestic headcount reductions, adds fuel to the argument that American corporations are not facing a talent shortage so much as executing a global wage-arbitrage strategy.

## The Diaspora Squeeze

For Indian tech professionals in the United States, the landscape has never been more contradictory. Those on H-1B visas face a 35 per cent approval rate under tightened adjudication, six-figure employer fees that make some companies think twice about sponsorship, and a green-card backlog that stretches past 2060 for Indian-born applicants under current allocations.

Yet the FY2026 LCA data proves that demand for their skills remains robust — just not necessarily for them as individuals. Companies want the talent profile. They are less committed to the specific people already here, already building lives, already enrolled in American schools and mortgages.

The Indian-American community — which contributes an estimated $1 trillion annually to the US economy and accounts for the highest median household income of any ethnic group — finds itself in a paradox: simultaneously the most recruited immigrant workforce and the most vulnerable to policy whiplash.

## What Comes Next

As the H-1B lottery season concludes and layoff tallies for 2026 approach 175,000 in tech alone, the conversation is shifting from whether the system is broken to what replaces it. Some employers are pivoting to global hiring through Employer of Record (EOR) arrangements that bypass the visa system entirely. Others are expanding India-based delivery centres, effectively moving the jobs rather than the workers.

For the Indian engineer in Sunnyvale or the QA analyst in Bellevue, the message from corporate America is increasingly clear: we need what you know, but we are no longer sure we need you here.

That is not just an immigration story. It is a labour story, a dignity story, and — for 1.5 million Indian-origin professionals in the United States — an existential one."""

a1 = {
    "id": str(uuid.uuid4()),
    "headline": "Amazon Certified 33,181 H-1B Positions While Cutting 30,000 Jobs. For Indian Tech Workers, the Math Does Not Add Up.",
    "subheadline": "New Department of Labor data reveals a staggering gap between Big Tech layoff announcements and foreign-worker hiring pipelines — and Indians, who hold the vast majority of H-1B visas, are caught squarely in the middle.",
    "slug": "amazon-h1b-certifications-layoffs-indian-tech-workers-20260520",
    "body": a1_body,
    "category": "nri-world",
    "sources": [
        {"name": "U.S. Department of Labor FY2026 Q2 LCA Data", "url": "https://www.dol.gov/agencies/eta/foreign-labor/performance"},
        {"name": "LinkedIn Analysis — H-1B Certification Data", "url": "https://www.linkedin.com"},
        {"name": "NBOT AI — 2026 Tech Layoff Tracker", "url": "https://nbot.ai"},
        {"name": "American Bazaar — H-1B Landscape 2026", "url": "https://americanbazaaronline.com"}
    ],
    "status": "published",
    "published_at": now,
    "score_total": 95,
    "diaspora_angle": "Indians hold the vast majority of H-1B visas; 600,000 Indian nationals in the system with decade-long green card waits. Simultaneous layoffs and mass certifications directly threaten NRI tech workers.",
    "urgency": "breaking",
    "vertical": "immigration",
}

# ── Article 2: Rupee Record Low + RBI $5B Swap (markets-finance) ──

a2_body = """The Indian rupee slid to 96.96 against the US dollar on Wednesday — breaching its previous record low of 96.6150 set just a day earlier — before settling at 96.82 on the interbank market. It was the fifth consecutive session of record lows for what has become Asia's worst-performing currency of 2026, having depreciated more than 7 per cent since January and 5.5 per cent since the Iran conflict erupted on February 28.

The immediate trigger was a convergence of three forces: stalled US-Iran peace talks that kept Brent crude above $111 a barrel, a global bond-yield surge that pushed US 10-year Treasuries to levels last seen in 2023, and persistent foreign institutional investor (FII) outflows from Indian equities.

## The RBI Steps In — With Its Biggest Tool

Hours after the rupee's latest rout, the Reserve Bank of India announced a USD 5 billion buy/sell swap auction scheduled for May 26. Under the mechanism, banks will sell dollars to the RBI and agree to repurchase them at the end of a three-year tenor, with bids submitted as a premium in paisa terms. The minimum bid size is $10 million.

The move is designed to inject rupee liquidity into a banking system that has been squeezed by the RBI's own forex interventions. Over the past three months, the central bank has sold tens of billions of dollars from its reserves to defend the rupee — a strategy that keeps the currency from falling faster but drains domestic liquidity in the process.

The swap is essentially the RBI trying to solve two problems at once: it needs to keep liquidity surplus to support growth and keep lending rates stable, but every dollar it sells to defend the rupee pulls rupees out of the system. The swap gives those rupees back without appearing to abandon the currency.

## What Is Driving the Collapse

The rupee's 2026 decline is inseparable from the geopolitical shock that began in late February. The Iran conflict and its disruption of shipping through the Strait of Hormuz sent oil prices surging past $110 — a devastating blow for India, which imports roughly 85 per cent of its crude requirements. Every $10 increase in Brent adds approximately $15 billion to India's annual import bill and widens the current account deficit by 0.4 per cent of GDP.

Compounding the oil shock, rising US Treasury yields have made dollar-denominated assets more attractive, drawing capital away from emerging markets. FIIs have been net sellers of Indian equities for much of 2026, with outflows accelerating in May.

The BSE Sensex declined 114 points to 75,200 on Tuesday amid late profit-booking, while the Nifty 50 slipped to 23,618 — both indices struggling to hold gains in the face of the currency headwind.

## What It Means for NRIs

For the estimated 18 million Indians living abroad, the rupee's slide creates an unusual — and potentially lucrative — window. At 97 to the dollar, remittances sent today buy approximately 12 per cent more in rupee terms than they did at the start of the year. For NRIs with property payments, family support obligations, or investment plans in India, the exchange rate has rarely been more favourable.

But the opportunity comes wrapped in a warning. A weaker rupee means higher import costs that eventually feed into domestic inflation, squeezing the purchasing power of families back home. The RBI's aggressive rate defence has already tightened financial conditions, and if the rupee continues its slide, the central bank may be forced to choose between defending the currency and supporting economic growth — a choice with consequences for everyone from Mumbai bond traders to Lucknow shopkeepers.

India's forex reserves, while substantial at approximately $620 billion, have declined noticeably since February. The $5 billion swap auction signals that the RBI is conserving reserves while still trying to keep markets liquid — a balancing act that gets harder with every leg down.

## The Bigger Picture

The rupee's record weakness is not just a currency story. It is a barometer of India's exposure to a world where oil supply disruptions, geopolitical conflicts, and rising US interest rates converge. The Iran conflict shows no sign of resolution. OPEC dynamics are shifting — the UAE's recent departure after 60 years adds another variable. And the Federal Reserve has signalled that rate cuts remain distant.

For NRIs, the pragmatic play is clear: lock in favourable exchange rates for necessary transfers while they last. For India's policymakers, the challenge is more existential — finding a path to macroeconomic stability in a world that keeps throwing new shocks at the one thing India cannot control: the price of oil."""

a2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Rupee Just Hit 97 to the Dollar — and the RBI's $5 Billion Emergency Swap Tells You How Worried They Really Are",
    "subheadline": "Asia's worst-performing currency of 2026 crashed through another record low on Wednesday as oil prices, the Iran conflict, and rising US bond yields created a perfect storm. For NRIs, the remittance window is wide open — but the macro picture is alarming.",
    "slug": "rupee-97-dollar-rbi-5-billion-swap-nri-remittances-20260520",
    "body": a2_body,
    "category": "markets-finance",
    "sources": [
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com"},
        {"name": "DevDiscourse — RBI $5B Swap Announcement", "url": "https://www.devdiscourse.com/article/headlines/3915543"},
        {"name": "Trade Brains — Rupee Crash Analysis", "url": "https://tradebrains.in"},
        {"name": "Capital Market News", "url": "https://www.capitalmarket.com"},
        {"name": "The Business Standard", "url": "https://tbsnews.net"}
    ],
    "status": "published",
    "published_at": now,
    "score_total": 96,
    "diaspora_angle": "At 97/dollar, NRI remittances buy 12% more rupees than in January. For 18 million overseas Indians, the exchange rate window is the most favourable in years — but the macro warning signs are serious.",
    "urgency": "breaking",
    "vertical": "markets-finance",
}

# ── Article 3: IT Industry AI Pricing Revolution (technology) ──

a3_body = """For three decades, India's information technology services industry ran on a simple equation: more engineers multiplied by more hours equalled more revenue. The billable hour was the atom of a $250 billion industry, the unit that built Infosys campuses, funded Cognizant's Nasdaq listing, and sent a generation of Indian engineers to client sites from New Jersey to Nottingham.

That atom is splitting.

In a series of announcements over the past six months, India's largest IT outsourcers have begun replacing time-and-materials billing with AI-linked pricing models that treat machine intelligence as the primary unit of delivery. Cognizant, Coforge, LTIMindtree, Tech Mahindra, and EPAM Systems have each introduced — or begun piloting — pricing structures that decouple revenue from human headcount.

## Cognizant's Four-Tier Rate Card

Cognizant, which generated $21.1 billion in revenue last year, is the most explicit about how the new model works. CEO Ravi Kumar S described it on the company's April 2026 earnings call as "AI-infused rate cards where pricing reflects a blended model of human effort and digital effort."

The company now charges clients along four tiers: work done by AI and verified by a human, work done by a human and verified by AI, work that is fully automated, and work performed entirely by AI agents without human intervention. Each tier carries a different rate, linked to token consumption — the small units of text that large language models process with every query.

"We are exposing tokenized rate cards that price work along a continuum from fully human-led discovery to hybrid to increasingly autonomous agentic delivery," Kumar said.

## Coforge's AI Agent Buffet

Noida-based Coforge, the seventh-largest Indian IT services firm, has taken a different approach: monthly subscriptions. Its "AI Mod Squads" package gives clients access to over 130 pre-built AI agents — from code-writing bots to multi-task autonomous systems — bundled with senior human executives who oversee the agents' output. Clients pay a fixed monthly fee based on the number, complexity, and autonomy of agents deployed.

"We are giving clients something the market has not offered before: the freedom to compose their own AI-powered delivery team, backed by domain intelligence built over three decades," CEO Sudhir Singh said.

The model is already available for deployment, and Coforge — which grew 29 per cent to $1.87 billion in FY26 — is betting that the subscription model will attract clients who want cost predictability rather than variable AI bills.

## LTIMindtree's Arcade Credits

LTIMindtree (LTM), the sixth-largest IT firm, is rolling out "BlueVerse Credits" — a prepaid system where clients purchase a fixed pool of credits that get deducted each time an AI tool performs a task. The model is explicitly designed to "delink the effort-based pricing model from outcome or value of work delivered," according to CEO Venu Lambu.

Think of it as the arcade-token approach to enterprise software: buy credits upfront, spend them as AI agents handle cloud migration, code modernisation, or managed services. The rollout is expected to reach select clients by June 2026.

## Why This Matters for Indian Engineers

The industry employs roughly 5.4 million people in India directly and supports another 10 million indirectly. A pricing model built around AI tokens and agent subscriptions rather than engineer-hours creates an existential question: what happens to the humans when the billing unit is no longer human?

The optimistic answer — promoted vigorously by every company mentioned above — is that engineers move "up the stack." Instead of writing code, they supervise agents that write code. Instead of testing software, they validate AI-generated test suites. Instead of building dashboards, they design the prompts that build dashboards.

The realistic answer is more complicated. Cognizant itself is spending up to $320 million on an AI-led restructuring that includes $200-270 million in severance costs. The company frames this as "upskilling and rebalancing," but the scale of severance spending tells its own story.

For the Indian engineer — whether based in Bengaluru, Hyderabad, or on an H-1B in Dallas — the message is clear: the industry that built your career is rebuilding itself, and the new architecture has fewer floors for people who only know how to do what AI now does faster and cheaper.

## The NRI Dimension

For Indian-origin tech professionals abroad, the shift adds another layer of uncertainty to an already volatile landscape. Many built their careers precisely on the kind of mid-level technical work — application maintenance, QA testing, database administration — that AI agents are now absorbing. Those on temporary work visas face the additional risk that their employer may decide the role can be delivered from India by a team of three humans and fifteen AI agents, rather than by a team of thirty humans in North America.

The IT pricing revolution is not just a business-model story. It is a workforce story, a migration story, and — for millions of Indian families whose prosperity was built on the billable hour — a story about what comes after the model that made everything possible."""

a3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's IT Giants Are Killing the Billable Hour. The AI Pricing Revolution Has Begun — and It Will Change How Indian Engineers Get Paid.",
    "subheadline": "From Cognizant's tokenized rate cards to Coforge's AI agent subscriptions, India's IT outsourcers are abandoning the billing model that built a $250 billion industry. The shift will reshape careers, margins, and what 'value' means in tech services.",
    "slug": "india-it-ai-pricing-revolution-cognizant-coforge-billable-hour-20260520",
    "body": a3_body,
    "category": "technology",
    "sources": [
        {"name": "Livemint — IT Outsourcers Offering Subscriptions and Credits for AI Work", "url": "https://www.livemint.com/companies/it-services-outsource-subscriptions-tokens-credits-ai-work-11778561116677.html"},
        {"name": "Cognizant Q1 2026 Earnings Call", "url": "https://www.cognizant.com"},
        {"name": "Stock Titan — Cognizant Doubles Buyback", "url": "https://stocktitan.net"},
        {"name": "Expert Insights News — Cognizant $320M Restructuring", "url": "https://expertinsightsnews.com"},
        {"name": "Constellation Research — Cognizant Q1 AI Gains", "url": "https://constellationr.com"}
    ],
    "status": "published",
    "published_at": now,
    "score_total": 93,
    "diaspora_angle": "The billable hour built careers for millions of Indian engineers both in India and on H-1B visas abroad. AI-token pricing threatens mid-level technical roles that form the backbone of the diaspora tech workforce.",
    "urgency": "developing",
    "vertical": "business",
}

# ── Insert all articles ──
for art in [a1, a2, a3]:
    result = sb_post_stdin("p2_articles", art)
    if isinstance(result, list) and len(result) > 0:
        print(f"OK [{art['category']}] {art['headline'][:70]}...")
        print(f"   ID: {art['id']}, Slug: {art['slug']}")
    elif isinstance(result, dict) and result.get("message"):
        print(f"ERR [{art['category']}]: {result['message']}")
        print(f"   Details: {result.get('details','')}")
    else:
        print(f"??? [{art['category']}]: {str(result)[:200]}")

print("\nDone inserting articles!")
