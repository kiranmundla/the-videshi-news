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
        "headline": "Nadella Is Building Microsoft's Own AI Brain. The OpenAI Divorce Gets Real.",
        "subheadline": "Microsoft will unveil homegrown coding, reasoning, and speech models at Build 2026 next week — its clearest signal yet that the $13 billion OpenAI partnership is becoming a backup plan, not the main one.",
        "slug": make_slug("microsoft-build-2026-homegrown-ai-models-openai-nadella"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Microsoft employs more Indian engineers on H-1B visas than almost any other company. If Nadella's in-house AI pivot reshapes product teams and hiring priorities, tens of thousands of Indian technologists in Redmond and the Bay Area will feel it first.",
        "tags": ["microsoft", "satya-nadella", "ai", "github-copilot", "build-2026", "openai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/microsoft-release-new-coding-model-next-week-information-reports-2026-05-28/"},
            {"name": "The Information", "url": "https://www.theinformation.com/"},
            {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/microsoft-visual-studio-2026/"},
            {"name": "CryptoBriefing", "url": "https://cryptobriefing.com/microsoft-new-coding-model/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Satya Nadella, CEO of Microsoft (Wikimedia Commons)",
        "body": """When Satya Nadella takes the stage at Microsoft's Build conference in San Francisco next week, he will do something that would have been unthinkable eighteen months ago: unveil a suite of AI models that Microsoft built itself, without OpenAI's help.

According to a Reuters report on Thursday, the centrepiece is a new coding model designed to supercharge GitHub Copilot, the AI-assisted programming tool that has become one of Microsoft's most visible AI products. But the coding model is only part of the story. Microsoft is also preparing homegrown models for transcription, reasoning, speech, and image tasks — a full-stack AI capability that directly competes with the models it currently licenses from OpenAI, Anthropic, and Google.

## The OpenAI Unbundling

The timing is deliberate. Microsoft and OpenAI have spent recent months renegotiating the terms of their $13 billion partnership, reducing mutual dependency. Microsoft has been quietly eyeing AI startup acquisitions, Reuters reported earlier in May, to diversify its talent base and deliver on Nadella's stated goal of building a cutting-edge foundation model by 2027.

The shift has been brewing since Anthropic's Claude Code overtook GitHub Copilot as the preferred AI coding assistant among developers. Microsoft's own tool, once the market leader, has been losing ground to competitors that iterate faster on newer model architectures. A homegrown coding model gives Microsoft direct control over the training data, update cadence, and integration depth that GitHub Copilot needs to compete.

Microsoft shares climbed nearly 3% on the Reuters report, suggesting investors are relieved rather than alarmed by the OpenAI decoupling. Market sentiment on the stock had soured this year as analysts questioned whether Microsoft's early AI lead was sustainable given the shifting partnership dynamics.

## Visual Studio 2026: AI Woven In

The model announcement coincides with the release of Visual Studio 2026, the first major update to Microsoft's flagship IDE in five years. The new version embeds GitHub Copilot as a native layer across every development workflow — from adaptive paste and AI-powered debugging to a new Profiler Agent that diagnoses performance bottlenecks using natural language.

For the estimated 50,000-plus Indian engineers working at Microsoft globally, the shift has immediate career implications. Teams that currently integrate third-party models may pivot to internal ones. New roles in model training, evaluation, and deployment are likely to open up. And the broader signal — that Microsoft views AI model development as a core competency, not an outsourced function — reshapes the kind of talent Redmond will recruit over the next hiring cycle.

## What NRIs Should Watch

The diaspora angle here is straightforward. Microsoft is the single largest H-1B employer among Big Tech companies. Indian engineers occupy critical roles across Azure, GitHub, Office 365, and the AI platform division. If Nadella's in-house AI ambitions accelerate, the demand for ML engineers, systems researchers, and infrastructure architects will shift from partner integration work to first-party model building.

For NRI investors, the stock's reaction to the news is instructive. The market is pricing in a Microsoft that can stand on its own AI feet — a Microsoft less dependent on a single, increasingly expensive, and unpredictable partner. Whether Build 2026 delivers on that promise will determine whether the 3% bump holds or evaporates.

The conference begins next week. Nadella, the Hyderabad-born engineer who turned Microsoft into a $3 trillion company, now has to prove he can build the AI that powers it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Chip Stocks Are Having Their Best Year Since the Dot-Com Boom. Sanjay Mehrotra's Micron Just Hit $1 Trillion.",
        "subheadline": "The Philadelphia Semiconductor Index has surged 81% in 2026 — its best first 100 trading days on record. At the centre of the rally: Micron Technology, led by Indian-American CEO Sanjay Mehrotra, which reached a $1 trillion valuation faster than any company in history.",
        "slug": make_slug("chip-rally-sox-micron-sanjay-mehrotra-trillion"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An Indian-origin CEO who was rejected for a US visa three times now leads the fastest company ever to reach $1 trillion. For NRI investors and the thousands of Indian semiconductor engineers at Micron, Intel, AMD, and Broadcom, this rally is both a portfolio event and a career validation.",
        "tags": ["semiconductors", "micron", "sanjay-mehrotra", "nvidia", "intel", "amd", "chip-rally", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/stocks/the-idaho-chip-maker-that-doubled-to-1-trillion-in-48-days"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/chip-stocks-rally-bubble-nvidia-amd-broadcom/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/the-surge-in-chip-stocks-this-year-is-putting-the-dot-com-rally-to-shame"},
            {"name": "Dow Jones Market Data", "url": "https://www.wsj.com/finance/stocks/chip-rally-5-7-trillion"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Sanjay Mehrotra, CEO of Micron Technology (Wikimedia Commons)",
        "body": """The numbers have crossed from impressive into surreal. The PHLX Semiconductor Index — the SOX, Wall Street's benchmark chip tracker — has surged 81% in the first 100 trading days of 2026, obliterating its previous record of 62% set in 1995, when the dot-com boom was still finding its footing.

At the epicentre of this rally sits an unlikely protagonist: Micron Technology, the Boise, Idaho memory-chip maker led by Sanjay Mehrotra, an Indian-American executive who was rejected for a US visa three times before eventually building one of the most consequential technology careers in Silicon Valley history.

## The Fastest Trillion Ever

On Tuesday, Micron shares surged 19% in a single session after UBS raised its price target from $535 to a staggering $1,625, arguing that long-term supply agreements justified a higher earnings multiple. The move pushed Micron past a $1 trillion market capitalisation — making it the 12th US company to reach that threshold, the first ever based in Idaho, and the fastest to double from $500 billion to $1 trillion in just 48 days. Nvidia, by comparison, took 490 days to cover the same ground.

Micron stock is up 830% from a year ago. Let that register. A company that makes memory chips — DRAM and NAND flash, the unsexy plumbing of the computing world — has outperformed virtually every AI darling on the market.

## Why Memory Is the New Oil

The explanation is deceptively simple: artificial intelligence is memory-hungry in ways that nobody fully anticipated. Training large language models requires massive GPU clusters, yes, but running those models — the inference stage that powers every ChatGPT response, every Gemini query, every enterprise copilot — demands extraordinary amounts of high-bandwidth memory (HBM). Micron's HBM3E chips are sold out through 2027. Every hyperscaler in the world is in a bidding war for supply.

The broader chip sector reflects this insatiable demand. Intel has more than tripled in 2026. SanDisk is up 570%. AMD now has a higher market capitalisation than JPMorgan Chase. Samsung, SK Hynix, and Micron have all joined the trillion-dollar club in a matter of months. The combined market value of SOX component companies has reached $5.7 trillion.

## The Bubble Question

Not everyone is comfortable. Barron's labelled chip stocks "the 2026 version of fiberoptic stocks" — the poster children of the dot-com bubble that eventually destroyed trillions in investor wealth. The gains have been indiscriminate: while Nvidia is up a relatively measured 30%, low-margin chip makers like ON Semiconductor and STMicroelectronics have each risen 122%, suggesting that some of this rally is momentum-driven rather than fundamentals-based.

Robert Pavlik, senior portfolio manager at Dakota Wealth Management, put it bluntly: investors are "holding their nose" and buying more AI and memory favourites because nothing else is working. "It's narrow," he told MarketWatch. "People want to say it's broadened out, but it hasn't."

## The Mehrotra Story

For the Indian diaspora, the Micron story carries a resonance beyond portfolio returns. Sanjay Mehrotra co-founded SanDisk in 1988, built it into a $19 billion company, and took the helm at Micron in 2017 — all after being turned away from America three times as a young student. His ascent to the trillion-dollar club alongside Satya Nadella, Sundar Pichai, and Arvind Krishna completes a quartet of Indian-born executives who now collectively oversee more than $8 trillion in market value.

For the thousands of Indian semiconductor engineers working at Micron's facilities in Boise, at Intel's design centres, at AMD's Austin and Bangalore offices, and at Broadcom's San Jose campus, the rally is also a career event. Chip companies are hiring aggressively. Micron is building a $15 billion fab in Gujarat. The semiconductor talent pipeline between India and the US has never been more valuable.

Whether this rally is the real thing or a prelude to a painful correction remains the central question of 2026. But for now, the man who was rejected three times at the US consulate is running the fastest-growing trillion-dollar company on earth."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jayshree Ullal's Arista Just Posted 35% Growth. The AI Networking Boom Is Only Getting Started.",
        "subheadline": "Arista Networks, led by Indian-origin CEO Jayshree Ullal, reported $2.71 billion in Q1 revenue and raised its AI networking target to $3.5 billion — but supply constraints in memory, optics, and wafers threaten to cap what could be an even bigger run.",
        "slug": make_slug("jayshree-ullal-arista-networks-q1-2026-ai-networking"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Jayshree Ullal, born in London to Indian parents and raised in New Delhi, has turned Arista into a $194 billion company. For Indian network engineers and infrastructure architects across Silicon Valley, her company's AI-driven growth is creating a new wave of high-paying roles.",
        "tags": ["arista-networks", "jayshree-ullal", "ai-networking", "data-center", "hyperscaler", "indian-ceo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Arista Networks Q1 2026 Press Release", "url": "https://www.businesswire.com/news/home/arista-q1-2026-results"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/arista-networks-q1-2026-earnings-call-transcript"},
            {"name": "Network World", "url": "https://www.networkworld.com/article/arista-q1-supply-constraints-optical-advances"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/ANET/earnings/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9b/Jayshree_Ullal_Arista_CEO.jpg",
        "image_caption": "Jayshree Ullal, CEO of Arista Networks (Wikimedia Commons)",
        "body": """There is a quiet war being fought inside every hyperscale data centre in the world, and Jayshree Ullal is winning it. Arista Networks, the company she has led since 2008, reported first-quarter 2026 revenue of $2.71 billion — a 35.1% jump from a year ago — beating Wall Street estimates on both the top and bottom lines.

The numbers are impressive on their own. But the real story is what they represent: a fundamental rewiring of how the world's largest AI systems communicate internally. Every GPU cluster, every training run, every inference request depends on the networking fabric that connects thousands of chips into a coherent system. Arista builds that fabric. And right now, every major cloud company on earth wants more of it than Ullal can supply.

## The AI Networking Thesis

Arista raised its full-year AI networking revenue target to $3.5 billion, up from earlier projections, driven by surging demand from hyperscalers like Meta, Microsoft, and Amazon. The company's high-speed switches — particularly its 800G and emerging 1.6T platforms — are the connective tissue of modern AI infrastructure. Without them, a room full of Nvidia GPUs is just expensive silicon generating heat.

Operating cash flow hit a record $1.69 billion in the quarter. Non-GAAP earnings per share came in at $0.87, beating consensus by nearly 8%. Full-year revenue guidance was raised to $11.5 billion, implying roughly 25% annual growth — a rate that most companies half Arista's size would envy.

And yet, the stock fell after earnings. The reason: supply constraints.

## The Bottleneck Problem

Ullal was unusually candid on the Q1 earnings call about what is holding Arista back. Memory chips, optical components, and semiconductor wafers are all in short supply, with shortages expected to persist well into 2027. The company has been building inventory aggressively — a strategy that pressures gross margins in the short term but ensures it can fulfil orders when components arrive.

Gross margin dipped to 62.4%, down from recent highs, largely because of the cost of securing scarce supply. It is a paradox familiar to anyone who has watched the AI infrastructure boom: demand is effectively unlimited, but the physical supply chain has hard ceilings that no amount of software can optimise away.

The optical component shortage is particularly acute. Arista introduced its XPO MSA optics platform — which Ullal described as a "10-year innovation" — designed to handle the extreme bandwidth requirements of next-generation AI clusters. But the optics supply chain, dominated by a handful of specialised manufacturers, cannot scale as fast as Arista's customer base is growing.

## The Ullal Factor

Jayshree Ullal's biography reads like a syllabus for the Indian diaspora's technology playbook. Born in London to Indian parents, raised in New Delhi, educated at San Francisco State and Santa Clara University, she spent 15 years at Cisco before joining Arista as CEO. Under her leadership, the company has grown from a niche data-centre switch maker into a $194 billion enterprise that sits alongside Broadcom and Palo Alto Networks in the upper echelon of tech infrastructure firms.

Her net worth has tracked the company's trajectory. Insider filings show Ullal executed plan-driven stock sales totalling $2.2 billion in April 2026 alone — not discretionary exits, but scheduled dispositions under 10b5-1 plans that reflect the sheer scale of Arista's appreciation.

For Indian network engineers — a substantial cohort in Silicon Valley and Bangalore — Arista's growth translates directly into career opportunity. The company is hiring across hardware engineering, software-defined networking, and AI infrastructure roles. Its customer list reads like a who's who of Big Tech, meaning that Arista experience is a transferable credential across the industry.

## What Comes Next

Arista's Q2 guidance points to revenue of approximately $2.8 billion, which would represent continued acceleration. The key variable is not demand — that is effectively inexhaustible — but whether the supply chain can keep pace.

For NRI investors, Arista trades at roughly 62 times forward earnings, a premium that reflects the market's confidence in Ullal's execution and the structural tailwinds behind AI networking. It is not cheap. But in a market where the infrastructure bottleneck has shifted from compute to connectivity, Ullal's company sits at exactly the right chokepoint.

The woman from New Delhi is building the nervous system of the AI age. The only constraint is physics."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
