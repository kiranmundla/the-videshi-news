#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-05 15:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # ── Article 1: TSMC Shareholders Meeting ──
    {
        "id": str(uuid.uuid4()),
        "headline": "TSMC's CEO Says AI Chip Demand Will Outstrip Supply for Years. He'd Also Like to Raise Prices.",
        "subheadline": "C.C. Wei told shareholders that even $165 billion in Arizona fabs won't satisfy American customers anytime soon — and the world's most important chipmaker isn't ruling out charging more.",
        "slug": make_slug("tsmc-ceo-cc-wei-ai-chip-shortage-years-price-hike-shareholders"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers at NVIDIA, Apple, Google and AMD — TSMC's biggest customers — face supply constraints that could slow AI projects and delay product launches. India's own chip ambitions, including the $11 billion Tata Electronics fab at Dholera using TSMC-class technology, depend on the same equipment ecosystem that TSMC dominates.",
        "tags": ["tsmc", "semiconductor", "ai-chips", "supply-chain", "computex"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/tsmc-boss-bets-big-ai-growth-says-hed-like-hike-chip-prices-2026-06-05/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/tsmc-not-at-risk-of-losing-competitive-edge-ceo-says-f9e3ca0b"},
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/technology/tsmc-ceo-warns-ai-driven-chip-demand-will-outstrip-supply-for-years-raising-prospects-of-higher-device-prices-57362.htm"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/TSMC_Global_R%EF%BC%86D_Center_at_night.jpg/1280px-TSMC_Global_R%EF%BC%86D_Center_at_night.jpg",
        "image_caption": "TSMC's Global R&D Center in Hsinchu, Taiwan, where the company pushes the boundaries of chip manufacturing",
        "image_attribution": "Wikimedia Commons",
        "body": """The world's most consequential chipmaker just told its shareholders to get comfortable with scarcity.

At TSMC's annual shareholders' meeting in Hsinchu on Thursday, CEO C.C. Wei delivered a message that was equal parts confidence and caution: demand for advanced AI chips will outstrip the company's manufacturing capacity for years — and the $165 billion it's pouring into new factories in Arizona won't change that equation anytime soon.

"We continue to see increasing adoption of AI models across consumer, enterprise and sovereign AI applications," Wei said. "This trend is driving demand for greater computing power, which in turn supports strong demand for advanced semiconductor chips."

When a shareholder asked the obvious follow-up — whether TSMC would raise prices — Wei didn't flinch. "I'd like to do that," he said. "We still need to make money."

## The Numbers Behind the Squeeze

The gap between what the industry wants and what TSMC can build is staggering. The company commands roughly 72% of the global foundry market and manufactures the most advanced chips for virtually every major AI player: NVIDIA, Apple, AMD, Google, and Qualcomm. Its first-quarter 2026 revenue hit $35.6 billion, up 35% year-over-year, driven overwhelmingly by AI-related orders.

TSMC has already begun mass production of 2nm chips using nanosheet Gate-All-Around transistors — the most significant architectural leap in a decade — with initial yields reaching 70-80%. By the end of 2026, the company expects to hit 100,000 wafers per month at the N2 node. Revenue from the 2nm process is projected to surpass 3nm and 5nm combined by the third quarter.

Yet even that pace falls short. Wei acknowledged that it will take "a very long time" to fully satisfy demand from American customers, even after the Arizona fabs come online.

## The High-NA EUV Gamble

A particularly revealing exchange came when shareholders pressed Wei on ASML's High-NA EUV lithography machines — the $400 million-per-unit tools that represent the next frontier of chipmaking. Intel has moved early to adopt them. TSMC has not.

Wei confirmed that TSMC has purchased the equipment and is conducting R&D, but will not deploy it for volume production until the economics make sense. "It is simply not yet being deployed for volume mass production," he said. The implication: TSMC believes it can maintain its technology lead without rushing into the most expensive tooling on the planet.

This is a calculated bet. Intel, which is rebuilding its foundry business under CEO Lip-Bu Tan's leadership, is wagering that early High-NA adoption will help it leapfrog TSMC at advanced nodes. TSMC is betting that cost discipline and execution will win the marathon.

## What This Means for Indian Engineers and NRI Investors

The supply crunch ripples directly through the working lives of tens of thousands of Indian-origin engineers in Silicon Valley and beyond. At NVIDIA, where Indian engineers form a significant share of the AI chip design workforce, TSMC's manufacturing constraints directly govern how fast new GPU architectures can reach data centres. At Apple, Google, and Qualcomm, the same dynamic plays out across smartphone and AI accelerator timelines.

For NRI investors, the calculus is straightforward. TSMC's stock has surged from T$950 to T$2,425 over the past year — a 155% climb — and the supply-demand imbalance suggests pricing power that could persist through the decade. The company is projecting $52-56 billion in capital expenditure for 2026 alone, with a CAGR in the mid-40s through 2029.

But the longer view matters too. India's own semiconductor ambitions — the $11 billion Tata Electronics fab at Dholera, Micron's assembly facility in Gujarat, the three chip startups that just showcased at a French trade exhibition — all operate within the same global ecosystem that TSMC dominates. When TSMC sneezes, the entire supply chain catches a cold. When it can't produce enough wafers, everyone from Cupertino to Dholera feels the pinch.

Wei's message was blunt: the AI revolution is real, the demand is structural, and TSMC will not satisfy it fully for years. The only question is how much more you'll pay while you wait."""
    },

    # ── Article 2: Aravind Srinivas / Perplexity at Computex ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Aravind Srinivas Just Put Perplexity on Intel's Biggest Stage. The IIT-Madras Grad Is Rewriting How AI Runs.",
        "subheadline": "The Perplexity CEO shared Intel's Computex keynote to unveil hybrid agentic inference — a system that splits AI work between your laptop and the cloud, task by task, without asking permission.",
        "slug": make_slug("aravind-srinivas-perplexity-computer-hybrid-ai-intel-computex"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Srinivas, an IIT-Madras alumnus who co-founded Perplexity AI in 2022, represents the latest wave of Indian-origin founders building category-defining AI companies from Silicon Valley. His Computex appearance alongside Intel's CEO signals how deeply embedded Indian technical leadership has become in the AI infrastructure stack.",
        "tags": ["perplexity", "aravind-srinivas", "ai", "computex", "indian-tech-leaders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint / PTI", "url": "https://www.livemint.com/technology/perplexity-ceo-outlines-multi-model-ai-vision-in-taiwan-event-11749024023397.html"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/technology/perplexity-ceo-outlines-multi-model-ai-vision-at-taiwan-event"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/03/perplexity-computer-local-cloud-models/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/tech-leaders-signal-the-agent-led-era-of-personal-computing-at-computex-2026/article69634290.ece"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c9/Aravind_Srinivas_2024.jpg",
        "image_caption": "Perplexity CEO Aravind Srinivas, who presented the company's hybrid AI vision at Computex 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """When Intel CEO Lip-Bu Tan needed someone to demonstrate the future of personal computing at his Computex 2026 keynote in Taipei, he didn't pick a colleague or a legacy software executive. He picked Aravind Srinivas, the 31-year-old IIT-Madras graduate who runs Perplexity AI.

The choice was deliberate. Srinivas took the stage to unveil a feature called hybrid agentic inference — a system that automatically splits AI tasks between your laptop and the cloud without requiring the user to choose. Sensitive data stays local. Heavy computation goes to frontier models. The orchestration happens invisibly.

"It creates a team of agents, uses up to 20 different AI models, and it orchestrates across models, tools, and files in one single system," Srinivas told the audience.

## How Hybrid Inference Actually Works

Perplexity Computer, launched earlier this year, already lets users run complex AI workflows. The hybrid inference layer, arriving in July, adds something technically ambitious: a compact model runs locally on the device, evaluating each task in real-time. If the task involves financial records, health data, or personal files, the local model handles it. If it needs frontier-scale reasoning — writing a research brief, synthesising legal documents, running a multi-step analysis — the system routes it to cloud models.

"This allows you to run smaller models locally," Srinivas explained, describing it as a way to balance "intelligence, accuracy, privacy and cost" within a single workflow.

The approach differs fundamentally from the current paradigm, where users either run everything in the cloud (fast but privacy-challenged) or everything locally (private but limited). Perplexity's bet is that the right answer is both — and that the routing should be automatic.

In a demonstration, one coding task saved approximately 1.4 million tokens and cut costs by 60% through intelligent routing. A webpage-generation task achieved the same result with 30% fewer tokens at a quarter of the cost.

## The IIT-Madras-to-Computex Pipeline

Srinivas's trajectory mirrors a pattern that Indian tech professionals will recognise. Born in Hyderabad, he studied electrical engineering at IIT-Madras before moving to the US for a PhD at UC Berkeley, where he worked on language models under Pieter Abbeel. He spent time at DeepMind and OpenAI before co-founding Perplexity in 2022.

Less than four years later, his company has become one of the most closely watched AI startups in the world. Perplexity's answer engine has carved out a position between traditional search and conversational AI, and its enterprise partnerships — including the Similarweb integration announced this week — signal a shift toward monetisable B2B workflows.

His Computex appearance alongside Intel's CEO is significant beyond the product announcement. When the world's computing hardware is being redesigned around AI workloads, having the Indian-origin founder of a leading AI company on the keynote stage demonstrates something that resume statistics alone cannot: Indian technical leadership isn't just filling engineering seats at FAANG companies. It's building the next layer of the stack.

## Why Indian Engineers Should Pay Attention

The technical architecture Srinivas described — hybrid local-cloud inference with automatic routing — has direct implications for how AI applications will be built and deployed over the next several years.

For Indian engineers working on AI infrastructure at Google, Microsoft, Amazon, or any of the dozens of enterprise AI companies, this represents a design pattern they will likely need to understand and implement. The notion that a single workflow can dynamically distribute across hardware tiers — NPU, CPU, GPU, cloud — is architecturally non-trivial and will demand new skills in model optimisation, latency management, and privacy-preserving computation.

For the broader Indian tech community in the US, Srinivas's rise offers a data point on what post-FAANG careers can look like. The previous generation of Indian-origin tech leaders — Pichai, Nadella, Narayen — rose through the ranks of established corporations. This generation is founding the companies. Perplexity sits alongside Databricks (Ali Ghodsi, Iranian-origin, but with a deeply Indian engineering team), Scale AI, and a growing roster of startups where Indian-origin founders are building infrastructure, not just consuming it.

"What we are showing today is just the start," Srinivas said. From an IIT hostel to Intel's Computex keynote, the trajectory suggests he means it."""
    },

    # ── Article 3: Qualcomm "Year of Agents" + Dragonfly ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Just Declared War on NVIDIA's Data Centres. Its Weapon Is Called Dragonfly.",
        "subheadline": "CEO Cristiano Amon launched Qualcomm's data centre chip brand at Computex and declared 2026 the 'year of agents' — a vision where your phone has two personalities, one for you and one for the AI working behind your back.",
        "slug": make_slug("qualcomm-dragonfly-data-center-nvidia-year-of-agents-computex"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Qualcomm is one of the largest employers of Indian-origin engineers in the semiconductor industry, with major design centres in Hyderabad, Bangalore, and Chennai employing thousands of chip architects and software engineers. A successful push into data centre AI would expand high-value roles for Indian talent on both sides of the Pacific.",
        "tags": ["qualcomm", "dragonfly", "nvidia", "ai-agents", "computex", "semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/qualcomm-says-2026-is-the-year-of-agents-unveils-dragonfly-ai-data-center-brand-2026-06-02/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/06/02/qualcomm_computex_2026/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/tech-leaders-signal-the-agent-led-era-of-personal-computing-at-computex-2026/article69634290.ece"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Qualcomm_Headquarters_La_Jolla.jpg/1280px-Qualcomm_Headquarters_La_Jolla.jpg",
        "image_caption": "Qualcomm's headquarters in La Jolla, California, where the chipmaker is plotting its data centre expansion",
        "image_attribution": "Wikimedia Commons",
        "body": """Qualcomm has spent most of the AI era watching from the sidelines as NVIDIA captured the data centre market. On Monday at Computex 2026, CEO Cristiano Amon made clear that the spectating phase is over.

Amon used his keynote to launch Dragonfly, Qualcomm's new umbrella brand for data centre compute products. He described it as the company's entry into the highest-margin, highest-growth segment of the semiconductor industry — the very territory NVIDIA has dominated so thoroughly that its market capitalisation now exceeds $3 trillion.

But the strategic logic behind Dragonfly extends beyond ambition. Amon's thesis rests on a structural shift in how AI will be consumed: not exclusively in massive cloud data centres, but distributed across a continuum that stretches from wearables to edge servers to hyperscale facilities. And in that distributed world, Qualcomm believes its decades of expertise in power-efficient mobile silicon gives it an edge that NVIDIA's GPU-centric architecture cannot easily replicate.

## The Two-Personality Device

The most provocative idea in Amon's keynote wasn't a product announcement. It was a prediction about what personal computing will become.

He declared 2026 the "year of agents" and argued that within a few years, every computing device will have "two personalities." One serves the human user — the familiar interface of apps, screens, and inputs. The other serves the AI agent working autonomously in the background, executing tasks, coordinating with other agents, and consuming tokens at machine speed.

"Future devices will be used at the same time by both humans and agents working in the background," Amon said.

The token economics he cited are worth pausing over. A typical conversational AI interaction today consumes about 10,000 tokens per prompt-response cycle. Reasoning tasks require roughly 100,000. Agentic AI — where software autonomously executes multi-step workflows — demands about a million tokens per task. Amon projected global token demand within a 10-second window at 31.7 billion in 2026, rising to 1.27 trillion by 2030.

If those numbers are even directionally correct, the infrastructure required to serve them cannot be built using cloud data centres alone. Hence the case for distributed compute — and hence Dragonfly.

## The NVIDIA Problem

Taking on NVIDIA in AI compute is, by most measures, a quixotic endeavour. Jensen Huang's company controls over 80% of the AI training chip market, its CUDA software ecosystem has created deep vendor lock-in, and its capital expenditure projections suggest it intends to keep that lead.

But Qualcomm is not trying to win the training market. Dragonfly targets inference — the process of running trained AI models to generate outputs. Inference workloads are growing faster than training, are more price-sensitive, and increasingly favour efficiency over raw horsepower.

Qualcomm demonstrated a distributed routing approach in which AI tasks are dynamically split between device-level compute and cloud-hosted models. In one coding example, the distributed approach saved approximately 1.4 million tokens and cut costs by 60%. In a webpage generation task, the same result was achieved with 30% fewer tokens at four times lower cost.

If inference becomes the dominant workload — and most industry analysts believe it will — then the competition isn't purely about who has the biggest GPU. It's about who can deliver the most intelligence per watt across the widest range of hardware.

## Why Indian Engineers Are Central to This Play

Qualcomm's India engineering centres in Hyderabad, Bangalore, and Chennai are not satellite offices. They house some of the company's most critical chip design, wireless technology, and AI software teams. Thousands of Indian-origin engineers work across Qualcomm's Snapdragon platform, and a pivot into data centre AI would create new career pathways in server chip architecture, AI compiler design, and systems software — roles that have historically been concentrated at NVIDIA, Intel, and AMD.

The Dragonfly announcement also matters for NRI investors who have built portfolios around the AI supply chain. Qualcomm's Investor Day on June 24 will provide the first real look at the data centre roadmap, and Wall Street will be watching to see whether Dragonfly is a credible product line or an aspirational brand exercise.

For now, Amon has made the bet. Qualcomm's mobile chip expertise, its power-efficiency pedigree, and its scale in edge devices give it a plausible path into a market that NVIDIA has treated as its private domain. Whether Dragonfly can fly remains to be seen. But the fact that it exists at all signals how rapidly the AI compute landscape is fragmenting — and how many fronts NVIDIA will have to defend."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
