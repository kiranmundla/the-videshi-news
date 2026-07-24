#!/usr/bin/env python3
"""Tech writer – 2026-06-08 18:00 UTC run. 3 articles."""

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


# ─────────────────────────────────────────────────────────────
# Article 1: Wipro crash + Indian IT market selloff
# ─────────────────────────────────────────────────────────────

art1_body = """Wipro shares cratered 8.4 per cent on Monday to ₹181.80 — their lowest level in three years — as a violent convergence of geopolitical risk, commodity shock, and an AI-trade unwind swept through Indian markets. The stock now sits 33 per cent below its 52-week high of ₹273.15, set barely six months ago.

It was not alone. The Nifty IT index opened nearly 600 points lower before clawing back some losses by midday. TCS shed 2.2 per cent, HCL Technologies dipped 0.3 per cent, and Infosys fell close to a per cent. Of the top-tier Indian IT names, only Tech Mahindra managed to hold green by late morning.

## Three shocks in 72 hours

The rout had three distinct catalysts, each amplifying the others.

First, the Nasdaq crashed roughly 5 per cent on June 5 — its worst session in months — led by steep declines in semiconductor and AI-linked stocks. Nvidia, Broadcom, and Micron all saw sharp drops as investors rotated out of the AI trade that had driven a year-long rally. Indian IT stocks, which derive a significant share of revenue from the same American tech clients, absorbed the shock when Mumbai opened on Monday.

Second, oil surged. Brent crude jumped 4.3 per cent to $97 a barrel after fresh Israeli strikes on Iran and Lebanon reignited fears of a wider Middle Eastern conflict and supply disruptions. India, the world's third-largest oil importer, is acutely vulnerable. On Friday, New Delhi had already unveiled emergency measures to support the battered rupee, which has been under sustained pressure from record foreign outflows triggered by the Iran war.

Third, a stronger-than-expected May jobs report in the United States revived expectations that the Federal Reserve could raise interest rates by year-end rather than cut them. Higher US rates typically strengthen the dollar, pull capital out of emerging markets, and squeeze the valuations of growth and technology stocks globally.

## Why Wipro took the hardest hit

Wipro's decline was deeper than its peers for company-specific reasons. Monday was the stock's buyback record date, triggering heavy institutional selling as funds repositioned around the event. But the structural overhang is more troubling: Wipro has reported flat or declining revenue growth for several consecutive quarters, and Wall Street's consensus rating on the stock has slipped to "sell," with two downgrades in the past 90 days alone.

Trading volume on Monday hit 2.5 million shares — nearly double the 50-day average — suggesting the move was driven by conviction, not merely a thin-market panic.

## The bigger picture for Indian tech workers

For the roughly 300,000 employees at Wipro and the hundreds of thousands more at TCS, Infosys, and HCL, the selloff is more than a ticker symbol. A sustained stock decline erodes the value of ESOPs and retention bonuses, the invisible compensation that keeps senior engineers from jumping to product companies or startups.

For NRI investors, the double hit — stock losses denominated in rupees, compounded by a weakening currency — is especially painful. The rupee's decline, however, has one silver lining: it makes Indian IT services cheaper for American and European clients, potentially supporting outsourcing demand through fiscal 2027.

The question now is whether this is a sharp but temporary correction or the start of a longer repricing. If oil stays above $90 and the Fed signals rate hikes, the answer will not be kind to Dalal Street's technology corridor."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Wipro Sinks to a Three-Year Low as Oil at $97, AI Selloff, and Middle East Turmoil Converge",
    "subheadline": "The IT bellwether fell 8.4 per cent in a single session, dragging the Nifty IT index down as three simultaneous shocks rattled Indian markets.",
    "slug": make_slug("wipro-three-year-low-oil-ai-selloff-nifty-it"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT workers face eroding ESOP values and retention bonuses. NRI investors suffer a double hit — falling stock prices in a weakening currency — though the rupee's slide makes Indian outsourcing cheaper for US clients.",
    "tags": ["wipro", "indian-it", "nifty-it", "stock-market", "oil-prices", "ai-selloff", "middle-east"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/asia/indian-shares-decline-two-month-lows-oil-spike-asia-selloff-2026-06-08/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/wipro-tcs-drag-nifty-it-2-lower-after-nasdaq-crash-ai-selloff/article69670123.ece"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/data-news/wipro-falls-monday-underperforms-competitors-50717a0a-7b9ae8dde98d"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Wipro_EC_4%2C_Bangalore%2C_India_%282015%29.jpg/1280px-Wipro_EC_4%2C_Bangalore%2C_India_%282015%29.jpg",
    "image_caption": "Wipro's Electronic City campus in Bangalore, India",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}


# ─────────────────────────────────────────────────────────────
# Article 2: OpenAI ChatGPT superapp overhaul
# ─────────────────────────────────────────────────────────────

art2_body = """Sam Altman's company is done letting ChatGPT be a chatbot. According to the Financial Times, citing more than a dozen current and former employees, OpenAI is planning the biggest overhaul in ChatGPT's history — transforming it from a question-and-answer tool into a unified "superapp" built around coding agents, task automation, and enterprise workflows. The changes are expected to roll out within weeks.

The stakes are enormous. ChatGPT now serves over 900 million weekly active users and 50 million paying subscribers. Two million businesses account for about 40 per cent of OpenAI's revenue, a share the company expects to push to 50 per cent by year-end. The superapp strategy is designed to lock in those enterprise dollars ahead of a confidential IPO filing that Reuters reported OpenAI is preparing.

## What changes

The overhaul has three pillars.

First, OpenAI's coding product Codex — a cloud-based software engineering agent that can autonomously write, debug, and deploy code — moves from a side offering to a flagship feature, deeply integrated into ChatGPT's main interface. Rather than asking users to navigate to a separate tool, the redesigned app will steer them toward coding, image generation, and partner services like Canva and Booking.com through new prompts and UI elements.

Second, the platform will emphasise "agentic workflows" — multi-step tasks where the AI does work on the user's behalf rather than merely answering questions. Think less "tell me about this bug" and more "fix this bug, write the tests, and open a pull request." The shift from conversational AI to task-executing AI reflects a broader industry trend, though OpenAI's move is the most aggressive consumer-facing bet on agents to date.

Third, OpenAI plans to eventually phase out the traditional text prompt altogether. The long-term vision, per the FT, is for the underlying models to intuitively understand user intent without needing explicit instructions — a goal that remains technically ambitious and, for now, aspirational.

## The enterprise pivot

Fidji Simo, OpenAI's CEO of Applications, has been leading the reorganisation, which has included deprioritising some consumer-focused initiatives to redirect engineering resources toward enterprise tooling and infrastructure scaling. The company's recent $40 billion funding round from SoftBank provides the capital to sustain this pivot.

The enterprise emphasis is partly competitive. Anthropic — which recently filed for what could be a trillion-dollar IPO — has been steadily gaining ground in the corporate market with its Claude models. Google's Gemini, now embedded in Apple's Siri at roughly $1 billion per year, is expanding its cloud footprint. OpenAI's superapp strategy is an attempt to make ChatGPT the default operating environment for knowledge work, not just the default chatbot.

## Why Indian engineers should pay attention

The implications for India's technology workforce are layered. Indian developers are among the heaviest users of AI coding tools; a 2025 GitHub survey found that Indian engineers adopted Copilot faster than any other national group. A more capable, more integrated Codex will likely accelerate that adoption — and sharpen the divide between engineers who use AI to multiply their output and those who do not.

For Indian IT services companies — TCS, Infosys, Wipro, HCL — the agentic turn is a strategic threat. If ChatGPT can autonomously handle the kind of routine code generation and testing that constitutes a significant portion of offshore IT services contracts, the labour arbitrage model that built Bangalore's tech corridor faces a slow-motion disruption.

At the same time, the superapp creates opportunity. Every enterprise deploying agentic AI needs prompt engineering, workflow design, integration, and governance — precisely the kind of high-value consulting that India's IT majors have been trying to move toward. The question is whether they can make that transition before the lower rungs of the services ladder get automated away.

OpenAI has not commented publicly on the superapp plans. Reuters could not independently verify all details of the Financial Times report."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Is Turning ChatGPT Into a Superapp. Its 900 Million Users Are About to Find Out What That Means.",
    "subheadline": "Coding agents, task automation, and an enterprise pivot signal the biggest overhaul in ChatGPT's history — just as OpenAI prepares a confidential IPO filing.",
    "slug": make_slug("openai-chatgpt-superapp-codex-enterprise-ipo"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian developers are the world's fastest adopters of AI coding tools. The superapp's agentic capabilities could accelerate that trend — while threatening the offshore services model that employs hundreds of thousands.",
    "tags": ["openai", "chatgpt", "ai-agents", "enterprise-ai", "ipo", "indian-it", "codex"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-plans-chatgpt-superapp-overhaul-ahead-listing-ft-reports-2026-06-07/"},
        {"name": "Financial Times (via TBS News)", "url": "https://www.tbsnews.net/tech/openai-plans-chatgpt-superapp-overhaul-ahead-listing-203125"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/openai-to-revamp-chatgpt-into-comprehensive-superapp-ahead-of-planned-ipo-2506080431/"}
    ]),
    "score_total": 76,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman at a meeting in February 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ─────────────────────────────────────────────────────────────
# Article 3: BFSI revenue concentration in Indian IT FY26
# ─────────────────────────────────────────────────────────────

art3_body = """Indian IT's annual results are in, and they tell a story the industry would rather not advertise: banks and financial institutions are now the only growth engine that matters. Four of the five largest Indian IT services companies saw their revenue share from Banking, Financial Services, and Insurance climb in fiscal 2026, even as technology, telecom, manufacturing, and retail verticals shrank.

The numbers, compiled from annual reports and reported by The Hindu BusinessLine on Monday, are stark.

TCS, India's largest IT exporter, drew 32 per cent of its revenue from BFSI in FY26, up from 30.9 per cent a year earlier. HCL Technologies saw the vertical's share jump from 20.7 per cent to 21.5 per cent. Infosys edged up from 27.7 per cent to 28 per cent. Tech Mahindra rose modestly from 16.1 per cent to 16.3 per cent.

Only Wipro bucked the trend, with BFSI dropping fractionally from 34.3 per cent to 34.1 per cent — though even at that lower share, banking remains by far Wipro's largest vertical.

In absolute terms, BFSI revenue grew between 1 and 7.5 per cent year-over-year for most of these companies. Wipro, again, was the outlier with a 0.7 per cent decline.

## AI is the demand driver

The growth is not accidental. Global banks have emerged as the most aggressive enterprise buyers of artificial intelligence, and they are channelling those investments through their existing IT services partners. Unlike the experimental AI spend in Silicon Valley — where projects are started, paused, and pivoted with startup-like frequency — BFSI clients are deploying AI for core productivity: fraud detection, risk modelling, compliance automation, and customer service transformation.

"Unlike other verticals, banks and financial institutions are using AI and technology investments for core productivity gains rather than discretionary innovation spending," said Vivek Iyer, partner and financial services risk leader at Grant Thornton Bharat. "That makes the segment relatively resilient even during periods of macro stress."

There is also a currency tailwind. The rupee's depreciation against the dollar — accelerated by oil-price spikes and foreign capital outflows — is making Indian IT vendors cheaper for global BFSI clients. Iyer noted that this cost competitiveness could support outsourcing demand from global banking clients through FY27.

## The concentration risk

The flipside is uncomfortable. When one-third of your revenue comes from a single vertical, you are not diversified — you are dependent. And that dependency is growing precisely because other verticals are contracting.

Technology and telecom clients — historically strong spenders with Indian IT firms — have pulled back amid post-pandemic cost rationalisation and their own AI-driven workforce reductions. Manufacturing is cautious. Retail has been hammered by consumer spending uncertainty in the US and Europe.

The result is a revenue mix that looks increasingly lopsided. If banks tighten their own IT budgets — whether from a credit cycle downturn, regulatory pressure, or the kind of sudden risk aversion that a Fed rate hike could trigger — Indian IT firms would have no offsetting vertical to absorb the impact.

This matters deeply for the Indian diaspora workforce. TCS employs over 600,000 people. Infosys has more than 300,000. HCL, Wipro, and Tech Mahindra add several hundred thousand more. A significant share of these employees work on BFSI projects, and many are deployed in the United States on H-1B and L-1 visas.

## A familiar pattern

India's IT industry has seen this movie before. In the years before the 2008 financial crisis, BFSI was the dominant revenue driver for every major services company. When Lehman Brothers collapsed, the shock wave hit Bangalore before it hit most of Wall Street. Hiring froze. Projects were cancelled. Visa applications stalled.

The industry eventually diversified — into healthcare, retail, energy, and manufacturing. But the FY26 data suggests that diversification has quietly reversed. AI modernisation pulled banks back to the top of the spending stack, and the other verticals did not keep pace.

For now, the banking sector's appetite for AI-driven transformation is keeping the lights on. The question is what happens when — not if — that appetite slows."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Banks Are the Only Vertical Keeping Indian IT Alive. The FY26 Numbers Prove It.",
    "subheadline": "BFSI now accounts for nearly a third of revenue at TCS, Infosys, and HCL — and it is the only segment growing while tech, telecom, and retail shrink.",
    "slug": make_slug("indian-it-bfsi-revenue-concentration-fy26-risk"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Over a million Indian IT workers — many on H-1B and L-1 visas in the US — are employed by these companies. Heavy BFSI concentration means a banking downturn would ripple through India's largest white-collar workforce.",
    "tags": ["indian-it", "bfsi", "tcs", "infosys", "hcl", "wipro", "ai-modernization", "h1b"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-sees-rising-share-of-revenue-from-bfsi-in-fy26/article69672345.ece"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/explainers/tcs-infosys-q4-earnings-bfsi-ai/95621/1"},
        {"name": "TechCircle", "url": "https://www.techcircle.in/2025/07/24/indian-it-firms-deepen-ai-reliance-amid-modest-q1-fy26-growth/"}
    ]),
    "score_total": 73,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/35118208/pexels-photo-35118208.jpeg",
    "image_caption": "Candlestick chart showing a downward trend in stock market analysis",
    "image_attribution": "Pexels",
    "body": art3_body
}


# ─────────────────────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
