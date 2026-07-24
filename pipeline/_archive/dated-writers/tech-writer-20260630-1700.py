#!/usr/bin/env python3
"""Videshi Technology Writer — 30 June 2026, 5:00 PM PT run."""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1 ──────────────────────────────────────────────────────────
art1_body = """Google has a problem that most companies would envy — and one that no amount of money has yet solved. Demand for its Gemini AI models has outstripped the computing capacity Sundar Pichai's company can physically deliver.

The scale of the shortfall became public over the past week through two disclosures. First, a Financial Times report revealed that Google informed Meta around March that it could not fulfil Meta's full Gemini compute request, disrupting and delaying several of Meta's internal AI projects. Then, in a separate SEC filing tied to SpaceX's IPO, it emerged that Google has agreed to pay Elon Musk's company $920 million per month — roughly $11 billion a year — just for bridge access to approximately 110,000 NVIDIA GPUs at SpaceX's data centres.

## The company that sold cloud can't buy enough for itself

Google Cloud reported $20 billion in first-quarter revenue, but Pichai acknowledged on the earnings call that capacity constraints had prevented even stronger growth. The cloud unit's order backlog nearly doubled quarter on quarter. The SpaceX deal, which runs from October 2026 through June 2029, is explicitly described as "bridge capacity" to handle "surging customer demand for Gemini Enterprise."

Meta, for its part, has been using Gemini for customer service chatbots, advertiser tools, coding assistance, and content moderation — tasks where Google's model outperformed Meta's own open-source Llama. Forced to ration, Meta has instructed employees to use AI tokens more efficiently and is accelerating development of Muse Spark, an internal model designed to reduce its dependence on external AI providers.

## What this signals for the industry

The episode exposes a structural bottleneck in the AI supply chain that transcends any single company. Even as hyperscalers pour hundreds of billions into new data centres, the lag between ordering chips and bringing facilities online means demand continues to outrun supply. NVIDIA's latest Blackwell and Rubin GPUs remain allocation-constrained worldwide. Firmus Technologies, an Australian firm, separately signed a deal this week for up to 170,000 NVIDIA GPUs across facilities in Indonesia, projecting $25 to $30 billion in committed revenue.

For Google, the irony is sharp: the company that invented the Transformer architecture underpinning most modern AI is now leasing compute from a rocket company to keep its own enterprise product running.

## Why this matters to Indian tech workers

Pichai's compute crunch has a direct bearing on the tens of thousands of Indian engineers employed across Google and Meta. At Google, Cloud is one of the fastest-growing divisions and a major employer of Indian talent in both the Bay Area and Bengaluru. Capacity constraints that slow Cloud's growth ultimately constrain headcount expansion and the AI projects those engineers work on.

At Meta, the forced migration away from Gemini toward internal models means a pivot in engineering priorities — and potentially in the teams that are staffed up or wound down. For NRI investors, the compute shortage is a reminder that even the mightiest AI stocks face physical-world bottlenecks that no software update can fix.

The broader signal is equally important for Indian IT services companies like TCS, Infosys, and HCLTech, which are building agentic AI practices on Google Cloud's Gemini Enterprise platform. If Google itself cannot secure enough capacity, its enterprise customers — and their Indian IT partners — will feel the squeeze downstream."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Pichai's Google Ran Out of GPUs. So It's Paying a Rocket Company $920 Million a Month.",
    "subheadline": "Google capped Meta's Gemini access, leased compute from SpaceX, and still can't keep up with demand. The AI infrastructure crisis is no longer hypothetical.",
    "slug": make_slug("pichai-google-gpu-shortage-spacex-meta-gemini-compute"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Sundar Pichai's compute crunch directly affects Indian engineers at Google Cloud and Meta, and downstream capacity for Indian IT firms building on Gemini Enterprise.",
    "tags": ["google", "sundar-pichai", "ai-infrastructure", "meta", "spacex", "gemini", "gpu-shortage"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Financial Times (via Reuters)", "url": "https://www.reuters.com/technology/google-limits-metas-use-its-gemini-ai-models-ft-reports-2026-06-28/"},
        {"name": "Engadget", "url": "https://www.engadget.com/ai/google-reportedly-capped-metas-use-of-gemini-ai-for-coding-and-chatbots-131552712.html"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/05/google-will-pay-spacex-920m-per-month-for-compute/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-stock-ai-chip-demand-firmus-deal-c6c3bc56"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, at a 2023 event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── Article 2 ──────────────────────────────────────────────────────────
art2_body = """In a cavernous facility in Austin, Texas, fleets of humanoid robots are learning to pick, pack, stack, and sort — not from human programmers writing line-by-line instructions, but from doing the work themselves, over and over, while AI models watch and learn.

Apptronik, a Google-backed robotics company, on Tuesday unveiled Robot Park, a nearly 90,000-square-foot training facility purpose-built to generate the real-world data that will teach humanoid robots to function reliably in factories, warehouses, and retail floors. Alongside it, the company introduced Apollo 2, its latest humanoid platform, available in both bipedal and wheeled configurations.

## The data factory behind the robot factory

The premise is deceptively simple. The hardest problem in robotics is not building a machine that can walk — it is building one that can handle the messy, unpredictable reality of a warehouse floor without falling over or crushing something. That requires enormous volumes of training data collected in physical environments, not simulations.

Robot Park is designed to produce that data at scale. Apollo 2 robots perform logistics, manufacturing, and retail tasks across the facility, generating training data that feeds directly into Gemini Robotics, Google DeepMind's foundational AI model for robotics.

"We have a factory that produces robots, we also have a factory that produces data," CEO Jeff Cardenas said. The company has built "hundreds" of Apollo 2 robots, though it declined to disclose deployment numbers.

Apptronik raised $520 million in February at a roughly $5 billion valuation, with investors including Google, Mercedes-Benz, John Deere, AT&T Ventures, and the Qatar Investment Authority. It plans to expand Robot Park to customer and partner sites globally, with production-grade deployments expected from 2027.

## Where Indian talent fits

Google DeepMind's robotics division, which is consuming the data Robot Park generates, is one of the most research-intensive AI teams in the world — and one that draws heavily on Indian engineering talent. The Gemini Robotics models being trained on this data are built by researchers across DeepMind's offices in London, Mountain View, and Bengaluru.

The implications extend well beyond the lab. Indian workers make up a significant share of the US logistics and warehousing workforce, particularly in metropolitan areas with large distribution centres. As humanoid robots move from pilots to production deployments in 2027 and beyond, the automation trajectory will reshape job categories that many Indian immigrants currently occupy.

## The competitive landscape is heating up

Apptronik is not alone. Tesla's Optimus, Figure AI (backed by NVIDIA and Jeff Bezos), and China's Unitree are all racing toward commercially viable humanoid robots. But Apptronik's Google DeepMind partnership gives it a distinctive edge: access to arguably the most advanced robotics AI models in the world, trained on proprietary physical-world data that competitors cannot easily replicate.

For India, the race carries a dual significance. The country's own robotics ambitions — from IIT labs working on agricultural drones to ISRO's humanoid prototype Vyommitra — could benefit from the foundational AI models being developed through partnerships like this one. Whether India becomes a consumer of humanoid labour or a builder of it may depend on decisions being made in facilities like Robot Park right now."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Google Just Opened a Factory That Makes Data for Humanoid Robots. Production Workers Should Pay Attention.",
    "subheadline": "Apptronik's Robot Park in Austin is training fleets of Apollo 2 humanoids with Google DeepMind's AI. Real deployments start in 2027.",
    "slug": make_slug("apptronik-robot-park-google-deepmind-apollo-humanoid"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian AI researchers at Google DeepMind are driving the Gemini Robotics models, while Indian logistics workers in the US face the automation wave these robots will bring.",
    "tags": ["robotics", "google-deepmind", "apptronik", "humanoid-robot", "ai", "automation", "logistics"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/apptronik-launches-robot-training-hub-unveils-apollo-2-humanoid-robot-2026-06-30/"},
        {"name": "Apptronik (Press Release)", "url": "https://apptronik.com/news"},
        {"name": "SiliconAngle", "url": "https://siliconangle.com/2026/02/13/apptronik-raises-520m-produce-humanoid-apollo-robot-commercial-deployments/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8566470/pexels-photo-8566470.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A humanoid robot in a digital network setting, representing the new wave of AI-powered automation",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ── Article 3 ──────────────────────────────────────────────────────────
art3_body = """Sanoke Viswanathan has spent barely ten months as CEO of FactSet, and he is already rewriting the playbook. On Tuesday, the former JPMorgan executive announced a strategic partnership with Google Cloud to embed agentic AI across the financial data company's platform — a deal that could reshape how Wall Street's investment professionals access data, build portfolios, and close deals.

The partnership will weave Google Search and Gemini directly into the FactSet Workstation, used daily by thousands of analysts, portfolio managers, and dealmakers at the world's largest financial institutions. In the other direction, FactSet-powered AI agents will "deepen the financial intelligence in Gemini Enterprise," Google's corporate AI platform.

## What 'agentic' means on a trading floor

The buzzword requires unpacking. Agentic AI refers to software that can autonomously execute complex, multi-step workflows — not just answer a question, but go find the data, run the analysis, draft the memo, and flag the risks. In finance, that means an agent that can pull a company's latest filing, cross-reference it against consensus estimates, compare the result to peer performance, and surface a recommendation — all from a single conversational prompt.

"AI is fundamentally shifting how financial professionals access data, derive insights, and make decisions," Viswanathan said in a statement. "Together with Google Cloud, we are putting trusted financial data and advanced AI capabilities to work."

The specifics remain deliberately vague. The companies described their work as building "a new generation" of agents "designed to improve efficiency, execution, and decision-making across portfolio operations, deal advisory, and corporate finance." Google declined to share financial terms.

## The Indian-origin CEO leading the charge

Viswanathan's ascent is itself a diaspora story worth noting. A 15-year JPMorgan veteran, he served as CEO of International Consumer and Wealth, sat on JPMorgan's Operating Committee, and previously ran the Corporate and Investment Bank's strategy division. Before JPMorgan, he co-headed McKinsey's Global Corporate and Investment Banking Practice.

His appointment as FactSet CEO in September 2025 added another name to the growing roster of Indian-origin executives leading major American financial technology companies — a list that already includes Ajay Banga at the World Bank, Arvind Krishna at IBM, and Sriram Krishnan advising the White House on AI policy.

## Why NRIs on Wall Street should care

FactSet is not a household name, but it is ubiquitous infrastructure. Its terminals sit on desks at BlackRock, Goldman Sachs, and virtually every mid-to-large asset manager and investment bank. For the estimated 40,000-plus Indian-origin professionals working in US financial services — from quant developers at hedge funds to analysts at bulge-bracket banks — the tools they use daily are about to change fundamentally.

The partnership also has implications for Indian IT services firms. HCLTech, TCS, and Infosys all have significant financial services practices and are Google Cloud partners. Agentic AI deployed through platforms like FactSet could automate precisely the kind of data wrangling and report generation that these firms currently staff with thousands of engineers.

FactSet's stock slipped fractionally on the announcement, trading more than 48 per cent below its 52-week high. Investors, it seems, want specifics before they get excited. Viswanathan, whose career was built on transforming large organisations from the inside, will need to deliver them quickly."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "FactSet's Indian-Origin CEO Just Plugged Google's AI Directly Into Wall Street's Terminal.",
    "subheadline": "Sanoke Viswanathan, a former JPMorgan executive, is partnering with Google Cloud to build agentic AI for the financial industry. The tools 40,000 Indian-origin finance professionals use daily are about to change.",
    "slug": make_slug("factset-viswanathan-google-agentic-ai-wall-street"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CEO Sanoke Viswanathan leads FactSet's AI transformation, directly affecting tens of thousands of Indian finance professionals on Wall Street who use FactSet daily.",
    "tags": ["factset", "google-cloud", "agentic-ai", "fintech", "wall-street", "indian-ceo", "sanoke-viswanathan"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/factset-stock-google-agents-ai-deal/"},
        {"name": "Nasdaq / RTTNews", "url": "https://www.nasdaq.com/articles/factset-research-joins-hands-google-cloud-bring-advanced-ai-financial-intelligence"},
        {"name": "GlobeNewsWire (FactSet CEO Succession)", "url": "https://www.globenewswire.com/news-release/2025/06/03/3016019/0/en/FactSet-Announces-CEO-Succession-Plan.html"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16902140/pexels-photo-16902140.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Financial market data and analytics displayed on a trading screen",
    "image_attribution": "Pexels",
    "body": art3_body,
}

# ── Insert ─────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
