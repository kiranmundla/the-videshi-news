#!/usr/bin/env python3
"""Technology writer – 3 articles for The Videshi, 2026-06-12 03:00 UTC."""

import json, os, uuid, requests
from datetime import datetime, timezone

# ── env ──
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/.env.supabase"))
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

now_iso = datetime.now(timezone.utc).isoformat()

articles = []

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1 — TCS-Anthropic Partnership
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "TCS Partners With Anthropic to Put Claude in the Hands of 50,000 Employees — and the Real Story Is Bigger Than a Software Deal",
    "subheadline": "India's largest IT services firm creates a dedicated AI business unit as Anthropic calls India its second-largest market, reshaping the $315 billion outsourcing industry's survival playbook",
    "slug": "tcs-anthropic-claude-partnership-ai-business-unit-20260612",
    "body": """Tata Consultancy Services announced on Wednesday that it has entered a Global Premier Partnership with Anthropic, the San Francisco-based AI safety company behind the Claude family of large language models. The deal is more than a licensing agreement. TCS is creating an entirely new business unit dedicated to building enterprise AI solutions on Anthropic's platform, and it plans to equip 50,000 of its employees with Claude for internal operations and client delivery.

The partnership makes TCS Anthropic's most prominent services ally in Asia. Dario Amodei, Anthropic's chief executive, described India as the company's "second-largest market" during the announcement — a statement that would have been unthinkable even eighteen months ago, when the AI race was framed almost entirely as a contest between Silicon Valley labs chasing consumer products.

## The Business Unit Nobody Expected

What distinguishes this deal from the typical technology partnership press release is the structural commitment. TCS is not simply reselling Claude licences. It is building a dedicated practice — staffed with engineers, solution architects, and domain specialists — that will develop custom AI applications for clients in regulated sectors including banking, insurance, healthcare, and government. The new unit will operate alongside TCS's existing consulting and digital transformation divisions but with a singular focus on Anthropic's models.

N. Chandrasekaran, chairman of Tata Sons, has been vocal about his vision for a future in which TCS deploys as many AI agents as it does human consultants. "We want equal numbers of employees and AI agents," he said at a Tata Group strategy session earlier this year. The Anthropic partnership is the most concrete step toward that goal.

The timing is pointed. TCS reported a net reduction of approximately 23,000 employees in fiscal year 2026, its steepest workforce contraction in over a decade. Revenue remained above $30 billion, but growth has slowed as clients increasingly demand AI-augmented services rather than the labour-intensive delivery model that built India's IT industry. TCS shares have fallen roughly 34 percent year-to-date. Infosys, which signed its own partnership with Anthropic in February, has declined 31 percent.

## Anthropic's India Bet

For Anthropic, the partnership is a distribution play. The company's direct enterprise sales team is small relative to OpenAI's, and it has historically relied on Amazon Web Services — its primary cloud partner and investor — for go-to-market reach. Adding TCS, which serves clients across 46 countries with over 600,000 employees, gives Anthropic a consultancy-led channel into thousands of enterprises that would never engage directly with a Silicon Valley AI lab.

Anthropic's valuation has surged past $965 billion following its IPO filing last month, making it the most valuable AI company in the world by market capitalisation. But valuation without enterprise adoption is just speculation. TCS offers Anthropic something critical: proof that its models can be deployed at scale in the complex, compliance-heavy environments where most corporate revenue actually lives.

The Indian market itself is substantial. India's enterprise IT spending is projected to reach $138 billion in 2026, according to Gartner, with AI-related services growing at more than 35 percent annually. Wipro, HCLTech, and Tech Mahindra are all pursuing similar AI platform partnerships — Wipro with Google Cloud's Gemini, HCL with Microsoft's Copilot ecosystem — creating a new competitive axis in an industry that has traditionally competed on headcount and hourly rates.

## What This Means for Indian Tech Workers

The 50,000 employees who will receive Claude access represent roughly eight percent of TCS's global workforce. The company says these workers will use the AI for code generation, documentation, testing, and client communication — tasks that currently consume significant junior-engineer time. The implicit message is difficult to miss: the value of routine technical work is declining, and TCS is investing in tools that can perform it faster and cheaper.

For the Indian diaspora in technology, this shift has immediate professional implications. NRI engineers and managers at US-based companies increasingly work with Indian IT services firms as delivery partners. The quality and capability of those partners is changing rapidly. A TCS team augmented with Claude can iterate on code reviews, generate compliance documentation, and prototype solutions in hours rather than days. Diaspora professionals who manage these relationships will need to recalibrate their expectations — and their own skill development.

The deeper question is whether partnerships like this one accelerate or slow the workforce contraction. TCS's argument is that AI augmentation will create higher-value roles that require fewer but more skilled workers. The counterargument is simpler arithmetic: if Claude can do the work of three junior developers, you need fewer junior developers.

India's $315 billion IT services sector is being rebuilt in real time. The TCS-Anthropic deal is not the beginning of that reconstruction — it has been under way for two years — but it may be the moment when the industry's largest player committed publicly to the new architecture.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg",
    "image_caption": "N. Chandrasekaran, chairman of Tata Sons, at the India Economic Summit",
    "image_attribution": "World Economic Forum / Wikimedia Commons (CC BY-SA 2.0)",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/tcs-anthropic-partnership-ai-agents-2026-06-11"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/11/tcs-anthropic-claude-enterprise-ai"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/news/tcs-anthropic-claude-50000-employees-ai-business-unit"}
    ]),
    "diaspora_angle": "NRI tech professionals managing TCS delivery partnerships will encounter AI-augmented teams; Indian IT workforce contraction reshapes career pipelines for fresh engineering graduates considering services industry",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2 — AI Price War
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "The Great AI Price War Has Begun — and It Looks a Lot Like the Dot-Com Playbook",
    "subheadline": "Google slashes subscription prices, OpenAI weighs drastic token cuts, and short-seller Jim Chanos warns the whole boom is a giant capital-misallocation bubble",
    "slug": "ai-price-war-google-openai-anthropic-token-costs-20260612",
    "body": """Google quietly dropped the price of its AI Plus subscription from $7.99 to $4.99 per month this week, a 37 percent cut that received less attention than it deserved. The reduction is not a promotional offer. It is a permanent repricing that signals Google's willingness to sacrifice margin in exchange for market share at a moment when the AI industry's economics are under more scrutiny than at any point since the boom began.

OpenAI is reportedly exploring even more aggressive moves. According to people familiar with the company's internal planning, OpenAI has discussed drastic reductions to its token pricing — the per-unit cost that developers pay to use GPT models through its API. Anthropic, whose Claude models compete directly with GPT for enterprise clients, is expected to follow. The three companies are locked in a pricing dynamic that resembles nothing so much as the broadband wars of the early 2000s, when telecoms raced to undercut each other into unprofitability.

## The Numbers Behind the Squeeze

The Silicon Data LLM Token Expenditure Index, which tracks average per-token costs across major AI providers, peaked at $2.05 per million tokens in March and has since fallen to $1.80 — a decline of more than 10 percent in three months. The index measures what enterprises actually pay, not list prices, so the real competitive pressure is even steeper than headline cuts suggest.

ChatGPT now has more than 900 million weekly active users and over one billion monthly users. OpenAI's revenue is growing, but so is its cost base. The company's IPO filing last month revealed infrastructure spending that dwarfs its revenue, a pattern familiar to anyone who watched Amazon burn through capital in the late 1990s. Anthropic, valued at $965 billion after its own IPO filing, faces similar economics. Both companies are betting that scale will eventually produce margins. The price cuts are designed to build that scale.

The corporate market is responding with enthusiasm that borders on alarm. Uber disclosed this week that it has already exhausted its entire 2026 AI budget — money that was supposed to last through December — because usage across its engineering and operations teams scaled far faster than projected. The disclosure raised a term that has entered Silicon Valley's vocabulary: "tokenmaxxing," the tendency of organisations to consume AI tokens at exponentially growing rates once access barriers drop.

## The Bubble Question

Jim Chanos, the short-seller who famously predicted the collapse of Enron, has drawn explicit comparisons between the AI boom and the dot-com bubble. In a recent interview, Chanos argued that the AI sector exhibits the same pattern of massive capital expenditure chasing revenue that does not yet exist at profitable scale. He pointed to the gap between AI companies' combined infrastructure spending — now exceeding $400 billion annually across the industry — and their collective revenue, which remains a fraction of that figure.

The comparison is imperfect. Unlike the dot-com era, AI's largest customers are the world's most profitable companies — Google, Microsoft, Amazon, and Meta — not speculative startups. The technology produces measurable productivity gains in coding, customer service, and data analysis. But Chanos's core observation stands: the industry is spending far more to build AI infrastructure than it is earning from AI services, and the price war will widen that gap.

## What This Means for the Diaspora Tech Workforce

For the estimated 750,000 Indian-origin technology professionals working in the United States, the AI price war reshapes the economics of their industry in two ways. First, cheaper AI tools accelerate the automation of routine software development, data analysis, and quality assurance — tasks that employ hundreds of thousands of H-1B workers and their permanent-resident counterparts. The same price cuts that make AI accessible to startups also make it viable as a replacement for mid-level engineering work.

Second, the boom creates extraordinary demand for AI infrastructure talent. Engineers who understand distributed systems, GPU cluster management, and model optimisation are commanding salaries that rival partner-track compensation at top law firms. Indian-origin professionals are disproportionately represented in these roles at Google, Microsoft, and the AI labs themselves.

The price war will produce winners. The question, as Chanos suggests, is whether the winners will be the companies cutting prices today or the investors who bet against them. For diaspora engineers, the answer matters less than the imperative it creates: move up the value chain before the value chain moves past you.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
    "image_caption": "Server racks in a modern data centre — the infrastructure behind the AI price war",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Sherwood News", "url": "https://sherwood.news/tech/google-ai-plus-price-cut-ai-subscription-war"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/openai-anthropic-token-pricing-cuts-ai-cost-war"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/technology/ai-price-war-google-openai-anthropic-bubble-fears"}
    ]),
    "diaspora_angle": "750K Indian-origin tech professionals in the US face dual pressure — cheaper AI automates mid-level engineering work while creating extraordinary demand for infrastructure talent; H-1B workforce economics shifting rapidly",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 3 — Perplexity's Aravind Srinivas & Indian-Origin AI Founders
# ═══════════════════════════════════════════════════════════════════
articles.append({
    "id": str(uuid.uuid4()),
    "headline": "Aravind Srinivas Is Taking Perplexity Public in 2028 — and He's Not Waiting for OpenAI or Anthropic to Go First",
    "subheadline": "The Chennai-born founder's search startup has charted its own path to an IPO, part of a broader wave of Indian-origin entrepreneurs reshaping Silicon Valley's AI landscape",
    "slug": "perplexity-aravind-srinivas-ipo-2028-indian-origin-ai-founders-20260612",
    "body": """Aravind Srinivas does not appear to be in any hurry, which is unusual for the chief executive of a company valued in the tens of billions in the most competitive technology market in decades. In interviews this month, the co-founder and CEO of Perplexity AI confirmed that the company intends to go public in 2028 — a timeline he described as "agnostic" of whether OpenAI or Anthropic complete their own IPOs first.

The statement is quietly significant. OpenAI and Anthropic both filed for initial public offerings last month, setting up what could be the largest AI listings in history. The conventional wisdom in Silicon Valley is that smaller competitors should either rush to market before the giants absorb all the investor attention, or wait until the dust settles. Srinivas is doing neither. He is building on his own schedule.

## From Chennai to the Answer Engine

Srinivas grew up in Chennai, studied electrical engineering at IIT Madras, and completed a PhD in computer science at Berkeley, where he worked on language model research. Before founding Perplexity in 2022, he held research positions at both OpenAI and Google DeepMind — a pedigree that gave him front-row exposure to the capabilities and limitations of the models he would later build a company around.

Perplexity's product is deceptively simple: an AI-powered search engine that synthesises answers from across the web and cites its sources. In an industry obsessed with general-purpose chatbots and autonomous agents, Perplexity has carved out a distinctive position by focusing on a single task — answering questions accurately — and executing it exceptionally well. The company's revenue has grown from $100 million to $500 million on the strength of its Pro subscription and its Sonar API, which other companies use to add real-time search capabilities to their own products.

Earlier this month at COMPUTEX 2026 in Taipei, Srinivas unveiled Perplexity Computer, a system that can coordinate up to 20 AI models simultaneously. "It creates a team of agents, uses up to 20 different AI models, and it orchestrates across models, tools, and files in one single system," he said during Intel CEO Lip-Bu Tan's keynote session. The product represents Perplexity's evolution from a search tool to an AI operating system — a bet that the future of AI lies not in any single model but in the intelligent orchestration of many.

## The Indian-Origin AI Founder Wave

Srinivas is the most prominent member of a cohort of Indian-origin founders who have emerged as central figures in the AI industry. Mustafa Suleyman, born in London to a Syrian father and British mother but often grouped with the broader South Asian tech diaspora, leads Microsoft AI. Noam Shazeer, co-founder of Character.AI, built his company before returning to Google in a $2.7 billion acqui-hire. Daniela and Dario Amodei, Anthropic's co-founders, are of Italian-Iranian descent, but their company's Indian operations — with India as its "second-largest market" — increasingly anchor the firm's global strategy.

The pattern extends beyond founders. Sundar Pichai oversees Google's AI strategy as Alphabet CEO. Satya Nadella has positioned Microsoft as OpenAI's primary backer and cloud partner. Arvind Krishna steered IBM toward its Watsonx AI platform. The concentration of Indian-origin leadership in the AI sector is not incidental — it reflects three decades of Indian engineering talent flowing into American graduate programmes and technology companies, now reaching the C-suite at precisely the moment when AI is reshaping those companies' core businesses.

For Srinivas specifically, the 2028 IPO timeline suggests confidence that Perplexity's differentiated approach — search-first, model-agnostic, multi-model orchestration — will sustain growth independently of whatever happens to the ChatGPT and Claude ecosystems. He has cited SpaceX's approach to going public as a "leading indicator" for how AI companies should think about IPO timing: wait until the business is undeniably mature, then list from a position of strength.

## The Diaspora Dimension

Srinivas's trajectory — IIT Madras to Berkeley to DeepMind to founding a company now worth tens of billions — is a story that resonates with particular intensity in the Indian diaspora. It is, in broad strokes, the narrative that has driven generations of Indian students to American graduate programmes. What has changed is the scale of the outcome. Previous generations of Indian tech founders built companies worth hundreds of millions. Srinivas and his contemporaries are building companies worth hundreds of billions, in an industry that did not meaningfully exist five years ago.

Perplexity employs a growing team in India, primarily in engineering and research roles, contributing to the company's model development and infrastructure. The 2028 IPO, if it proceeds at the valuations the AI market currently supports, would make Srinivas one of the wealthiest Indian-origin entrepreneurs in history — and provide a data point that the next generation of IIT graduates will study carefully.

The AI IPO wave is coming. Srinivas just plans to arrive on his own terms.""",
    "category": "technology",
    "status": "review",
    "is_editorial": False,
    "vertical": "technology",
    "image_url": "https://images.pexels.com/photos/30530415/pexels-photo-30530415.jpeg",
    "image_caption": "An AI chat interface on a laptop — the kind of search experience Perplexity is redefining",
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/perplexity-ai-ipo-2028-srinivas"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/start-ups/perplexity-ai-aravind-srinivas-ipo-2028-openai-anthropic"},
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/10/perplexity-ai-ceo-ipo-timeline-agnostic-openai-anthropic.html"}
    ]),
    "diaspora_angle": "Srinivas's IIT Madras-to-AI-billionaire trajectory embodies the new scale of Indian diaspora entrepreneurship; Perplexity's growing India engineering team and the broader wave of Indian-origin AI leaders reshaping Silicon Valley",
    "published_at": now_iso,
    "created_at": now_iso,
    "updated_at": now_iso,
})

# ── Insert ──
url = f"{SUPABASE_URL}/rest/v1/p2_articles"
for a in articles:
    resp = requests.post(url, headers=HEADERS, json=a)
    if resp.status_code in (200, 201):
        row = resp.json()
        if isinstance(row, list):
            row = row[0]
        print(f"✓ Inserted: {row['slug']}  (id={row['id']})")
    else:
        print(f"✗ FAILED [{resp.status_code}]: {a['slug']}")
        print(f"  {resp.text[:300]}")

print(f"\nDone — {len(articles)} articles submitted at {now_iso}")
