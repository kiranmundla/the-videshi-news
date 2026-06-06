#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Google Is Building Its Own AI Chips. Broadcom's Record Quarter Can't Hide That.",
        "subheadline": "Broadcom posted $10.8 billion in AI chip revenue — up 143% — and the stock still cratered. The real story is Google's quiet move toward MediaTek and in-house silicon.",
        "slug": make_slug("broadcom-google-mediatek-tpu-chip-diversification"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Broadcom's Bengaluru R&D centre is one of the company's largest globally. Thousands of Indian engineers design the custom ASICs and networking silicon that powered this record quarter. If Google diversifies away from Broadcom for TPU production, the ripple effects will be felt in cubicles from San Jose to Sarjapur Road.",
        "tags": ["broadcom", "google", "tpu", "custom-chips", "ai-infrastructure", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/broadcom-set-shed-300-billion-value-ai-results-fail-impress-2026-06-05/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/broadcom-pays-big-for-playing-it-safe"},
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2458917/broadcom-q2-earnings-call-spotlights-ai-demand-surge"},
            {"name": "SDxCentral", "url": "https://www.sdxcentral.com/articles/news/broadcom-secures-deal-with-google-for-next-gen-ai-racks-and-custom-tpus/2026/05/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c5/Hock_Tan_2022.png",
        "image_caption": "Broadcom CEO Hock Tan, who steered the company to record AI chip revenue",
        "image_attribution": "Wikimedia Commons",
        "body": """Broadcom just delivered the kind of quarter most semiconductor companies would frame and hang on the wall. Revenue hit a record $22.2 billion, up 48% year over year. AI semiconductor sales reached $10.8 billion — a 143% surge that outpaced even the company's own guidance. Bookings for AI chips topped $30 billion in the quarter, nearly three times what it shipped. CEO Hock Tan called demand for custom AI accelerators and networking "simply insatiable."

The stock cratered anyway. Broadcom shed roughly $315 billion in market value over two trading sessions — one of the largest wipeouts in corporate history.

## The Google Problem

The numbers were fine. The narrative was not. Buried in the earnings call was an admission investors had been dreading: Google, Broadcom's single most important AI chip customer, is diversifying its supply chain.

Broadcom has been Google's primary partner for designing and manufacturing tensor processing units — the custom chips Google uses instead of buying Nvidia's GPUs. It is an enormously profitable relationship. But reports have been circulating for weeks that MediaTek, the Taiwanese chip designer better known for smartphone processors, is taking a growing role in Google's eighth-generation TPU programme.

Tan tried to frame it diplomatically. "We fully expect that there will be some diversity of sources for them," he told analysts. Morgan Stanley's Joe Moore estimates Broadcom will still capture at least 80% of Google's business. But the direction of travel is clear: Google wants optionality, and Broadcom's near-monopoly on TPU design is ending.

Macquarie downgraded Broadcom to neutral, explicitly citing Google's in-house chip ambitions and predicting Broadcom's market share will "decline meaningfully" by 2027.

## Anthropic's Quiet Shift

The Google story was not the only headache. Anthropic, the AI lab behind Claude and one of Broadcom's six core custom chip customers, recently shifted its procurement preference from full server racks to individual chips. Analysts flagged this as a likely contributor to the revenue miss relative to Wall Street's loftiest projections.

Broadcom did announce a new agreement for Anthropic to access five additional gigawatts of next-generation TPU-based compute starting in 2027. But the deal's fine print — "consumption is dependent on Anthropic's continued commercial success" — reads more like a handshake than a contract.

## Why Indian Engineers Should Watch This Closely

Broadcom's engineering footprint in India is vast. The company's Bengaluru office is one of its largest R&D centres globally, with teams working across custom ASIC design, networking silicon, and software-defined infrastructure. The Hyderabad and Pune offices add further depth. When Broadcom wins a multi-billion-dollar TPU contract, a significant portion of the design work happens in India.

If Google's diversification toward MediaTek and in-house alternatives accelerates, it does not just affect Broadcom's stock price. It affects project headcount, team allocations, and the career trajectories of chip designers who have spent years building expertise on Google's architecture.

For the roughly 200,000 Indian-origin engineers working across the semiconductor industry in the United States, Broadcom's predicament also illustrates a broader dynamic: the hyperscalers that drove the AI boom are increasingly determined to own more of the chip stack themselves. Amazon has Trainium. Google has TPUs and now MediaTek. Meta designs its own training chips. The custom silicon intermediary — Broadcom's core business model — is being squeezed from above.

## The Bull Case Survives, Barely

The bears are not wrong about the risks, but they may be premature about the timeline. Broadcom's AI backlog stands at $73 billion in contracted orders. Its fiscal 2027 target of $100 billion in AI revenue is underpinned by committed customer agreements across all six accounts. Q3 AI semiconductor revenue is guided at $16 billion — more than triple the year-ago figure.

The company is not shrinking. It is growing at a pace that would be considered extraordinary in any other context. The problem is that "extraordinary" was already priced in, and the market wanted "miraculous."

For NRI investors holding Broadcom in their portfolios — and many do, given the stock's eightfold rise since ChatGPT's 2022 launch — the question is no longer whether AI demand is real. It is whether the intermediaries that rode the first wave can survive the second one, when their biggest customers decide they would rather build the chips themselves."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Agentic AI Has a CPU Problem. It Could Reshape a $120 Billion Market.",
        "subheadline": "Everyone bet on GPUs. Now research shows CPUs account for 88% of agentic AI latency. AMD, Intel, Nvidia, and Arm are scrambling for a market that barely existed two years ago.",
        "slug": make_slug("agentic-ai-cpu-bottleneck-120-billion-market"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers design CPUs at every company in this race — AMD's EPYC team in Hyderabad, Intel's largest design centre outside the US in Bengaluru, Arm's growing India operation, and Nvidia's Grace CPU team. A $120 billion CPU market shift directly affects career opportunities and specialisation choices for tens of thousands of Indian chip designers.",
        "tags": ["agentic-ai", "cpu", "amd", "intel", "nvidia", "arm", "semiconductors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/cpu-demand-rapidly-rising-amid-expanding-agentic-ai-says-barclays-raises-pt-on-advanced-micro-amd-to-665-1519399/"},
            {"name": "StockTwits / IO Fund", "url": "https://stocktwits.com/news/article/2e8a5af5-forget-gpus-amd-nvda-intc-arm-are-chasing-ais-next-big-prize-the-120b-cpu-market"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/chip-selloff-erases-over-1-trillion-stock-market-value-2026-06-06/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/amp/corporate/intel-ceo-unveils-ai-innovations-and-partnerships-at-mega-tech-event-in-taiwan"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6636463/pexels-photo-6636463.jpeg",
        "image_caption": "A microprocessor on a motherboard — CPUs are emerging as the hidden bottleneck in agentic AI workloads",
        "image_attribution": "Pexels",
        "body": """For three years, the AI trade has had a simple thesis: buy GPU companies. Nvidia's stock went vertical. AMD rode the wave. The entire semiconductor conversation revolved around who could ship more graphics processors to power the insatiable demand for training and running large language models.

That thesis is developing a crack. Not because GPU demand is fading — it is not — but because the next phase of AI is exposing a bottleneck nobody planned for: the humble CPU.

## The 88% Problem

Research from Intel and Georgia Tech has quantified what AI infrastructure teams have been whispering about for months. In agentic AI workloads — systems where multiple AI agents coordinate tasks autonomously, calling APIs, querying databases, orchestrating multi-step workflows — CPUs account for up to 88% of end-to-end latency.

The finding upends the GPU-centric view of AI compute. In a chatbot, the GPU does the heavy lifting: it runs the model, generates tokens, handles inference. The CPU is a traffic cop. But in an agentic system, the CPU suddenly becomes the busiest component, managing orchestration logic, network calls, memory allocation, and the coordination layer between multiple agents working simultaneously.

IO Fund analyst Beth Kindig argues this dynamic could create a server CPU market worth $120 billion by 2030 — a figure that would dwarf the current market and fundamentally alter the competitive landscape.

## Wall Street Is Already Moving

The smart money noticed. On June 1, Barclays analyst Tom O'Malley raised AMD's price target from $500 to $665, maintaining an overweight rating. His thesis: CPU-to-GPU ratios are narrowing as agentic AI drives CPU demand to levels nobody modelled a year ago. AMD, with its EPYC server processors and growing data centre portfolio, is "among the best-positioned companies to benefit."

The same day, Mizuho raised AMD's target to $615 from $515, citing agentic AI demand across the CPU ecosystem and supply constraints extending into 2027.

These are not speculative bets. AMD's first-quarter 2026 data centre revenue hit $5.8 billion, up 57% year over year. Its EPYC processors are gaining share in cloud deployments where agentic workloads run. The company recently expanded its partnership with Dell to deploy MI350P GPUs alongside EPYC CPUs in PowerEdge servers — a pairing designed specifically for enterprises running multiple AI agents.

## The Four-Way Race

What makes this moment unusual is the number of credible contenders.

**AMD** has the most momentum. EPYC's server market share has climbed steadily from near-zero a decade ago to roughly 25% today, almost entirely at Intel's expense. Its integrated CPU-GPU roadmap gives it a natural play in agentic architectures.

**Intel** has the most to gain — and lose. Bengaluru is Intel's largest design centre outside the United States, with thousands of engineers working on Xeon processors and next-generation architectures. At Computex 2026, CEO Lip-Bu Tan showcased a Rack Scale AI platform combining Xeon CPUs with SambaNova's AI accelerators, explicitly targeting the agentic inference market. Intel needs this story to work. Its foundry business is still bleeding cash, and CPU relevance in the AI era is its lifeline.

**Nvidia** surprised everyone at Computex with RTX Spark — an Arm-based chip pairing a 20-core Grace CPU with Blackwell-class graphics. It is the company's first real consumer PC processor, and it signals that Nvidia sees the CPU as integral to the AI stack, not peripheral to it. Jensen Huang confirmed next-generation N2X and N3X chips are in development.

**Arm** is the architecture underlying it all. Its licensing model means it benefits regardless of which company wins. CEO Rene Haas appeared alongside Huang at Computex to mark the RTX Spark launch. Arm-based server designs from Ampere, Amazon (Graviton), and now Nvidia are gaining ground in data centres where power efficiency matters — which is everywhere agentic AI runs at scale.

## What This Means for Indian Engineers

India's role in CPU design is older and deeper than its role in GPU development. Intel Bengaluru has contributed to Xeon for over two decades. AMD's Hyderabad design centre works on EPYC core architecture. Arm's India engineering teams are expanding. Qualcomm's Nuvia-derived server CPUs were partly designed in Hyderabad before the division was wound down.

If the CPU market expands from its current size to $120 billion by 2030, the hiring implications are significant. CPU design talent — microarchitecture, verification, physical design — becomes dramatically more valuable. For Indian engineering graduates choosing between GPU-focused roles and CPU design, the calculus may be shifting.

For NRI investors, the agentic AI thesis offers a different portfolio construction than the pure-GPU play that dominated 2024 and 2025. AMD at 23 times forward earnings looks cheaper than Nvidia at 35 times. Intel at single-digit multiples is either a value trap or a turnaround story. Arm's premium valuation prices in its position as the Switzerland of chip architecture.

## The Bigger Picture

The GPU trade is not over. Nvidia will sell more than $200 billion worth of chips this fiscal year. But the agentic AI wave — where AI systems do not just answer questions but execute multi-step tasks autonomously — is creating demand for a part of the compute stack that was considered boring eighteen months ago.

CPUs are not glamorous. They do not generate breathless keynote applause or triple-digit stock rallies. But they might be the component that determines whether agentic AI works at enterprise scale or remains a demo. For the tens of thousands of Indian engineers designing them, that is not a bad place to be."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
