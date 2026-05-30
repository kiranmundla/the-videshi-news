#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 06:00 UTC"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# ─── ARTICLE 1 ─────────────────────────────────────────────────────────
art1_body = """Wipro's American Depositary Receipt surged 18.5 per cent on the New York Stock Exchange on Wednesday — its largest single-day gain since October 2008 — after the Bengaluru-based IT services company announced an expanded partnership with ServiceNow to deploy agentic AI workflows across enterprise operations.

The stock followed through on the National Stock Exchange on Friday, jumping 4.6 per cent to ₹211 in early trade before settling at ₹205.53. For a company that has spent most of 2026 getting battered alongside the broader Indian IT sector, the move was seismic.

## What the Deal Actually Does

Under the expanded partnership, Wipro will integrate its Wipro Intelligence platform — a suite of AI-powered tools — with the ServiceNow AI Platform. Three specific solutions sit at the core of the arrangement:

**SmartProcure** handles procurement workflows through standardised intake, approvals and execution. **Telco Autonomous Networks** targets service operations in the telecom sector by combining AI workflows with industry-specific context. **Cyber Transform** addresses security operations, focusing on vulnerability management and incident response governance.

"This is not about standalone pilots or isolated proofs of concept," Amit Zavery, President and COO at ServiceNow, said in a statement. "When agentic AI runs inside secure workflows, ideas start delivering real results."

Malay Joshi, CEO of Wipro's Americas 1 Strategic Market Unit, described the partnership as solving "a practical problem many large organisations face — not a lack of AI ambition, but difficulty scaling AI implementation."

## Why Wipro's Stock Needed This

Indian IT services companies have been under relentless pressure since OpenAI announced its services-led venture earlier this month, sending shockwaves through the $315 billion sector. TCS shed 25,000 jobs in nine months. Infosys CEO Salil Parekh's compensation — ₹826 million — drew scrutiny precisely because it came as the industry faces existential questions about its future.

Against that backdrop, Wipro's deal represents something the market has been craving: evidence that traditional Indian IT companies can transform from body-shopping operations into AI-native solution providers. The 18.5 per cent ADR jump wasn't about a single contract — it was about narrative shift.

## The Buyback Factor

The timing also benefits from Wipro's board-approved buyback at ₹250 per share, a 21 per cent premium over its previous closing price. The record date is June 5, which means investors are now positioning ahead of the eligibility cutoff.

Wipro plans to repurchase up to 60 crore equity shares through a tender offer route, representing over 5 per cent of total equity share capital.

## What This Means for NRIs

For the roughly 30,000 Indian tech professionals who work at or with Wipro in the United States, this deal signals something important: their employer is pivoting from being a cost-arbitrage play to an AI-implementation partner.

For NRI investors holding Indian IT stocks — many of whom watched TCS, Infosys and Wipro collectively shed billions in market capitalisation over the past quarter — the question is whether this is a genuine inflection point or a temporary reprieve. The agentic AI partnership with ServiceNow is real and specific. But whether Wipro can replicate this model across its $10 billion revenue base remains the harder question.

Market analysts at Bonanza noted the stock is "showing signs of base formation near the long-term support zone around ₹200-202" but cautioned that a sustained uptrend requires a decisive move above ₹212-218. For Wipro, the ServiceNow deal at least gives bulls something concrete to point to."""

# ─── ARTICLE 2 ─────────────────────────────────────────────────────────
art2_body = """On Tuesday afternoon, a 390-foot superyacht named "Launchpad" glided through Seattle's Ballard Locks and into Lake Union. Bystanders booed. One screamed that its owner should "pay some f---ing taxes."

The yacht belongs to Mark Zuckerberg. The same week, Meta filed WARN notices confirming 1,395 layoffs across Washington state — about 20 per cent of its local workforce. Separately, state filings in California revealed 671 job cuts in the Bay Area: 338 in Burlingame, 252 in San Francisco, and 81 in Fremont.

In total, Meta is eliminating roughly 8,000 positions globally while reassigning another 7,000 workers to AI-focused roles. The company projects $145 billion in capital expenditures this year, almost entirely directed at AI infrastructure.

## The Numbers Keep Getting Worse

Meta is not alone. According to TrueUp's tracking data, 144,355 tech workers have been laid off in 2026 — running 47 per cent ahead of last year's pace. The largest cuts come from the very companies that employ the most H-1B visa holders: Oracle has shed 30,000 positions, Amazon 16,000, and Meta 9,500.

Goldman Sachs economist Elise Peng estimated in April that AI has reduced monthly job growth by roughly 16,000 to 25,000 over the past year, with lower postings for occupations most exposed to AI risk.

"AI-driven jobs disruption isn't primarily via layoffs, but through a steady narrowing of opportunities at the entry level," wrote Jeffrey Sonnenfeld, a professor at the Yale School of Management, in a May 4 commentary. New York Federal Reserve data shows the unemployment rate for recent college graduates averaged 5.7 per cent in Q1 2026 — up from 4 per cent when ChatGPT launched in late 2022.

## The H-1B Dimension

For Indian tech workers on H-1B visas, these numbers carry an additional weight that their American colleagues do not bear. Under current rules, laid-off H-1B holders have a 60-day grace period to find another sponsoring employer or leave the country.

A Reddit post this week from an H-1B Data Engineer in Ohio — who claimed to have applied to over 1,500 jobs without a single recruiter callback — went viral, generating hundreds of responses from visa holders describing similar experiences.

"I honestly never thought I would be in this situation," the user wrote.

The post resonated because it captured a shift that many Indian tech workers have been absorbing quietly: companies that once aggressively hired international talent are now slowing recruitment, cutting teams, or avoiding visa sponsorship altogether. For Indians specifically, per-country caps mean green card wait times stretch to decades, making every job loss potentially existential.

## The Optics Problem

Meta's layoffs have been proceeding in waves since April, when Zuckerberg acknowledged the cuts were tied to AI spending. "We're doing this as part of our continued effort to run the company more efficiently and to allow us to offset the other investments we're making," Chief People Officer Janelle Gale said in an internal memo.

But the yacht's arrival in Seattle — on the same day the Washington layoffs were confirmed — generated the kind of headlines that no corporate communications strategy can absorb. "Just another Tech Bro who can't read the room," one X user wrote. A lock operator at the Ballard Locks told GeekWire the vessel was "the biggest one I've had in 14 years."

## What NRIs Should Watch

Three things matter for the Indian diaspora in tech. First, the layoff pace is accelerating, not decelerating. Meta's Washington cuts affect departments that historically employed significant numbers of Indian engineers: software engineering, data science, and IT infrastructure.

Second, the 60-day clock creates a liquidity crisis that American workers simply do not face. Indian tech workers in Seattle and the Bay Area — where rents routinely exceed $3,000 per month — cannot afford to wait out a slow job market. The market for H-1B transfers has tightened considerably as companies reduce sponsorship.

Third, the broader trend of AI replacing headcount is structural, not cyclical. Companies like Meta, Snap, PayPal, and Cloudflare have explicitly said that smaller teams can now accomplish what larger teams used to do. For an industry where Indian professionals constitute roughly 70 per cent of H-1B holders, this is the defining employment challenge of the decade."""

# ─── ARTICLE 3 ─────────────────────────────────────────────────────────
art3_body = """Corporate America discovered something uncomfortable this quarter: artificial intelligence is expensive to use, not just to build.

According to a Wall Street Journal report this week, large companies are beginning to ration AI token usage after months of encouraging employees to embrace the technology. At one major financial institution, executives discovered employees were burning hundreds of thousands of dollars per month on AI tokens — some using powerful premium-tier models for the simplest of questions, or just small talk.

"If your daughter needs tutoring in algebra, you can probably find someone cheaper than Albert Einstein," said Matan Grinberg, CEO of coding automator Factory.

The phenomenon even has a name: tokenmaxxing — using as much computing power as possible in order to be seen as "AI-forward." It persisted even after model providers shifted from all-you-can-eat subscriptions to usage-based pricing.

## The Scale Is Staggering

Google said at a recent event that it now processes over 3.2 quadrillion tokens per month — seven times its volume a year ago. The company and others are seeking to reduce AI costs through improved computing efficiency, but the growth curve is relentless.

The cost problem is compounding because enterprises adopted AI tools before building the governance frameworks to manage them. ChatGPT Plus costs $20 per month per user. ChatGPT Pro — with essentially unlimited agent usage — runs $200 per month. For API-level access, web search queries alone cost $25 to $30 per 1,000 calls. Scale that across a 50,000-person enterprise and the annual bill can reach tens of millions of dollars.

Some companies are exploring cheaper models, but several of the most affordable options were developed in China, creating a security and compliance reluctance. Anthropic, OpenAI, and Google all offer lighter versions of their flagship models, and firms like Factory have developed routing systems to triage queries — sending simple questions to cheaper models and reserving premium capacity for complex tasks.

## Where Indian IT Comes In

This is precisely the kind of problem that Indian IT services companies were built to solve. Wipro, TCS, Infosys, and HCLTech have spent three decades optimising enterprise technology costs. The shift from "implement AI everywhere" to "implement AI efficiently" plays directly to their consulting-led strengths.

Wipro's expanded partnership with ServiceNow this week — which sent its ADR up 18.5 per cent — is one example. The deal specifically targets enterprise AI governance: standardised workflows, policy-aligned execution, and measurable outcomes. It is not about building AI models. It is about making AI deployments cost-effective and auditable.

TCS, despite shedding 25,000 jobs in nine months, has doubled its fresher intake — a signal that it is reshaping its workforce pyramid around AI implementation rather than traditional service delivery. Infosys has been investing in its AI-native platform Topaz. HCLTech has been building out its AI Force portfolio.

For these companies, the enterprise AI cost crisis is not a threat — it is a market expansion opportunity. Research firm Gartner estimates that AI spending optimisation will become a $10 billion consulting category by 2028.

## The Diaspora Angle

For Indian tech professionals at American companies, the AI cost reckoning cuts both ways. On one hand, their expertise in enterprise systems integration makes them valuable as organisations seek to rationalise AI spending. On the other, the broader push for "efficiency" has historically meant layoffs — and this cycle is no different.

The deeper issue is structural. Indian engineers at Google, Microsoft, Amazon, and Meta are simultaneously being asked to build AI systems, implement them across business units, AND reduce the cost of using them. The employees who built the internal AI tools that are now being rationed face an uncomfortable irony: their success in driving adoption has created the very cost problem their employers now want solved.

For NRI investors, the token bill story offers a counterintuitive signal. While the initial AI investment wave favoured model builders — Nvidia, OpenAI, Anthropic — the next phase will favour AI optimisers. Indian IT services companies, trading at depressed valuations after the OpenAI services venture scare, may be better positioned for the "Phase Two" AI economy than the market currently recognises.

Google's 3.2 quadrillion tokens per month is not a ceiling — it is a floor. Someone will have to manage the bill. The Indian IT industry has been managing technology bills for Fortune 500 companies since 1991. This is, in many ways, what they trained for."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Wipro's ADR Posts Biggest Single-Day Jump Since 2008 After ServiceNow Agentic AI Deal",
        "subheadline": "The IT services company's American depositary receipt surged 18.5 per cent — its largest one-day gain in nearly two decades — as an expanded partnership to deploy agentic AI across enterprises signals a potential pivot for India's battered IT sector.",
        "slug": make_slug("wipro-adr-18-percent-surge-servicenow-agentic-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Wipro employs tens of thousands of Indian tech professionals in the US. The ServiceNow partnership signals a shift from traditional IT outsourcing to AI-native enterprise solutions, directly affecting the career trajectories and value proposition of Indian H-1B workers in the American IT services sector.",
        "tags": ["wipro", "servicenow", "agentic-ai", "indian-it", "stock-market"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-rises-after-expanded-partnership-scale-ai-adoption-2026-05-29/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/wipro-and-servicenow-deepen-ai-partnership-to-automate-enterprise-workflows/article69631234.ece"},
            {"name": "TradingView", "url": "https://www.tradingview.com/news/reuters.com,2026:newsml_L1N3PB028:0-wipro-shares-rise-up-to-4-5-after-it-firm-s-ai-partnership-with-servicenow/"},
            {"name": "DQ India", "url": "https://www.dqindia.com/news/wipro-servicenow-deepen-alliance-to-drive-enterprise-adoption-of-agentic-ai-12978261"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17483873/pexels-photo-17483873.png",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Zuckerberg's $300 Million Yacht Drew Boos in Seattle. Meta Just Fired 2,100 Workers on the West Coast.",
        "subheadline": "Meta has confirmed 1,395 layoffs in Washington state and 671 in the Bay Area as part of an 8,000-person global restructuring. With 144,000 tech layoffs in 2026 running 47 per cent ahead of last year, Indian H-1B holders face the sharpest edge of the downturn.",
        "slug": make_slug("meta-layoffs-seattle-bay-area-zuckerberg-yacht"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta is one of the largest H-1B employers in the US. Indian engineers constitute roughly 70% of H-1B holders in tech, and the 60-day grace period after layoff creates an existential urgency that American workers don't face. The structural shift toward smaller AI-powered teams threatens the employment model that brought hundreds of thousands of Indian professionals to Silicon Valley.",
        "tags": ["meta", "layoffs", "h1b", "silicon-valley", "zuckerberg", "ai-restructuring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/technology/meta-lays-off-nearly-1400-washington-employees-latest-tech-workforce-cut"},
            {"name": "KTVU", "url": "https://www.ktvu.com/news/nearly-700-meta-layoffs-bay-area"},
            {"name": "New York Post", "url": "https://nypost.com/2026/05/27/business/mark-zuckerbergs-300m-superyacht-draws-boos-cruising-into-seattle-as-meta-slashes-jobs-there/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/ai-tax-openai-anthropic/"},
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/05/28/h-1b-worker-shares-harsh-reality-of-us-tech-job-market/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Corporate America Has an AI Token Problem. It Looks a Lot Like India's Next Consulting Goldmine.",
        "subheadline": "Enterprises are burning hundreds of thousands of dollars monthly on AI tokens as 'tokenmaxxing' runs rampant. Google alone processes 3.2 quadrillion tokens per month. Indian IT services companies, battered by OpenAI's services push, may have found their comeback story.",
        "slug": make_slug("corporate-america-ai-token-bill-indian-it"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian tech professionals at American companies are simultaneously building AI systems, deploying them, and being asked to reduce their cost. Indian IT services companies — Wipro, TCS, Infosys, HCLTech — are positioning AI cost optimisation as their next major revenue line, directly relevant to NRI investors and employees in the sector.",
        "tags": ["ai-costs", "tokenmaxxing", "indian-it", "enterprise-ai", "consulting"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/corporate-america-ai-costs-rationing-2026"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-rises-after-expanded-partnership-scale-ai-adoption-2026-05-29/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/ai-tax-openai-anthropic/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
        "body": art3_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
