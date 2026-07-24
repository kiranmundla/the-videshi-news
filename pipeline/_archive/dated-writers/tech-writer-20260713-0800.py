#!/usr/bin/env python3
"""Technology writer — 2026-07-13 08:00 PDT run"""

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
    # ── Article 1: Intel €5 Billion Ireland Investment ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Just Committed €5 Billion to Ireland. It Is a Bet on Keeping Europe's Most Advanced Chip Factory Ahead of the AI Curve.",
        "subheadline": "The chipmaker is upgrading its Leixlip campus outside Dublin to boost production of AI-optimised Xeon processors, adding several hundred jobs and spending roughly 30% of its entire 2026 capital budget in one country.",
        "slug": make_slug("intel-5-billion-ireland-ai-chip-leixlip-expansion"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Intel employs nearly 5,000 people in Ireland and runs one of Europe's most advanced fabs there. Many Indian engineers in Intel's global semiconductor division rotate through the Leixlip campus. The investment cements Ireland — already home to a significant Indian professional community — as a strategic node in the global chip supply chain.",
        "tags": ["intel", "semiconductors", "ireland", "ai-chips", "manufacturing", "lip-bu-tan"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/intel-announces-57-billion-ai-driven-capital-investment-ireland-2026-07-13/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/intel-to-invest-5-billion-for-expanded-manufacturing-in-ireland-f5bc26d4"},
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2521413/intels-operating-margins-are-improving-is-more-upside-ahead"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg",
        "image_caption": "Intel CEO Lip-Bu Tan, whose turnaround strategy has quadrupled the company's stock since March 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Intel has begun deploying €5 billion ($5.7 billion) into its Irish campus at Leixlip, west of Dublin, in what the company calls its most significant capacity upgrade in Europe since it doubled the site's footprint between 2019 and 2023. The investment, announced on Monday, will outfit existing cleanroom space with leading-edge manufacturing equipment to produce Intel 3 silicon wafers — the process node behind its latest Xeon 6 and next-generation Xeon server processors.

The scale is striking even by Intel's standards. The €5 billion represents roughly 30 percent of the chipmaker's entire $17 billion capital expenditure budget for 2026. Naga Chandrasekaran, Intel's executive vice president of foundry operations, told reporters that the majority of the spending would land before the end of 2027.

## Why Ireland, and Why Now

Ireland has been Intel's European manufacturing base since 1989, absorbing more than €30 billion in cumulative investment. The Leixlip campus already houses Fab 34 — which Intel reclaimed full ownership of in April after buying out Apollo Global Management's 49 percent stake for $14.2 billion — and is the most advanced semiconductor production facility of its kind in Europe.

The timing is not accidental. Global demand for server-grade silicon is surging as AI workloads proliferate. "The demand for servers, the demand for AI is driving a significant increase in the need for Intel 3 wafers," Chandrasekaran said. Intel's Data Center and AI Group posted $5.05 billion in first-quarter revenue, up from $4.13 billion a year ago, with operating margins leaping from 13.9 percent to 30.5 percent.

## The Turnaround Behind the Numbers

The Ireland expansion is a piece of a broader corporate resurgence under CEO Lip-Bu Tan, who took over in March 2025. Intel's shares have more than quadrupled since his arrival, and the company has landed landmark customer deals with Apple, Nvidia, and SpaceX — several of which were brokered with active encouragement from the Trump administration, which holds a 10 percent stake in the company.

A recent Wall Street Journal investigation detailed how Commerce Secretary Howard Lutnick and the administration's "chips czar" Bill Frauenhofer have taken an unusually hands-on role in Intel's business, receiving quarterly CFO briefings and regularly visiting headquarters. The arrangement has drawn comparisons to industrial policy models in East Asia — an ironic echo for a company whose Malaysian-born CEO initially faced White House scepticism over his ties to China.

Intel's non-GAAP operating margin has climbed to 12.3 percent from 5.4 percent a year ago. Disciplined cost management — R&D and SGA expenses fell 9 percent year over year — has combined with revenue growth to deliver the sharpest profitability swing in the company's recent history.

## What This Means for Indian Engineers

Intel's Irish operations will add "several hundred" new jobs to the existing 4,900-person workforce at Leixlip. For Indian semiconductor professionals, that matters in two ways.

First, Ireland is already a significant destination for Indian tech workers in Europe. The country's reliance on foreign multinationals — whose Irish workforces have nearly doubled in a decade to 11 percent of the entire labour market — has created a comparatively welcoming immigration environment for skilled engineers.

Second, Intel's manufacturing ambitions intersect directly with India's own semiconductor push. The company's foundry division is courting external customers with a pitch built on geographic diversification and US-allied supply chain security — the same logic driving Tata Electronics' fab in Dholera and Micron's Gujarat facility. Indian engineers with Intel foundry experience, whether gained in Ireland, Oregon, or Arizona, are increasingly valuable to both Intel's global operations and India's nascent chip manufacturing ecosystem.

## The Bigger Picture

The investment also underscores how the AI boom has entered a phase that favours Intel's traditional strengths. The explosion of AI agents — autonomous software systems that run continuously — has spiked demand for the general-purpose CPUs that Intel has manufactured for decades, even as GPU-makers like Nvidia push into Intel's territory with products like the Vera CPU. Intel's challenge is to ride this wave while simultaneously building a foundry business credible enough to win and keep external customers. Ireland, with its proven manufacturing record and $5.7 billion in fresh capital, is where that credibility gets tested."""
    },

    # ── Article 2: Accenture 35GB Data Breach ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Accenture Confirms a Hacker Stole Source Code and Cloud Credentials. For 300,000 Indian Employees, the Questions Are Just Starting.",
        "subheadline": "A threat actor calling themselves '888' is selling 35GB of alleged Accenture data — including RSA keys, SSH keys, and Azure access tokens — on a cybercrime forum. The company says the breach has been contained. Security researchers are not so sure.",
        "slug": make_slug("accenture-data-breach-35gb-source-code-indian-it-workers"),
        "category": "technology",
        "vertical": "cybersecurity",
        "diaspora_angle": "Accenture employs over 300,000 people in India — more than in any other country — and tens of thousands of Indian-origin professionals in its US, UK, and European offices. A breach involving source code and cloud credentials raises direct concerns about the security of systems those workers build and maintain daily.",
        "tags": ["accenture", "cybersecurity", "data-breach", "indian-it", "cloud-security", "azure"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Cybernews", "url": "https://cybernews.com/security/accenture-data-breach-35gb/"},
            {"name": "Help Net Security", "url": "https://www.helpnetsecurity.com/2026/07/08/accenture-data-breach/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/cyber-security/accenture-confirms-data-breach-after-hacker-claims-theft-of-35gb-internal-data"},
            {"name": "BleepingComputer (primary source)", "url": "https://www.bleepingcomputer.com/news/security/accenture-confirms-breach-after-hacker-offers-stolen-data-for-sale/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9951077/pexels-photo-9951077.jpeg",
        "image_caption": "Binary code and data streams on a computer screen — the kind of environment where cloud credentials live",
        "image_attribution": "Pexels",
        "body": """On July 6, a threat actor operating under the alias "888" posted a listing on PwnForums, a well-known cybercrime marketplace, offering what they described as "just over 35GB of source codes" stolen from Accenture. The price? Monero only. The proof? A screenshot showing what appeared to be a git clone operation against a private Azure DevOps repository hosted under an accenture.com production URL.

Accenture, the world's largest IT consulting firm with more than 700,000 employees globally, confirmed the breach to BleepingComputer with a statement remarkable for both its brevity and its gaps: "We are aware of this isolated matter, and we have remediated its source. There is no impact to Accenture operations and service delivery."

The company declined to specify the attack vector, confirm the volume of stolen data, or say whether any customer information was affected.

## What Was Allegedly Taken

According to the listing — which has not been independently verified in full — the exfiltrated data includes:

- Source code from internal repositories
- RSA and SSH private keys
- Azure Personal Access Tokens (PATs)
- Azure Storage access keys
- Configuration files, potentially including .env files containing secrets

Cybernews researchers noted that if the .env file claim is accurate, the data likely originated from a developer workstation rather than a centrally secured vault — a pattern that suggests a compromised individual endpoint rather than a sophisticated infrastructure breach.

The screenshot shared by "888" referenced a repository named "121123_AtriasTalentAcademy," which aligns with Accenture's known internal talent development platforms.

## A Familiar Adversary

This is not Accenture's first encounter with "888." In June 2024, the same actor attempted to sell data on 32,826 current and former Accenture employees, though the company later said only three legitimate names and email addresses were confirmed in the dataset.

The company has weathered larger incidents. In 2017, four unsecured AWS S3 buckets exposed sensitive data about Accenture's cloud platform and its clients. In 2021, the LockBit ransomware gang targeted the company and threatened to release stolen files. Each time, Accenture characterised the damage as limited. Each time, the incidents exposed patterns — over-permissioned cloud storage, under-monitored endpoints — that persist across the IT consulting industry.

## Why 300,000 Indian Workers Should Care

Accenture's India operations are the backbone of its global delivery model. More than 300,000 of its employees are based in India, making it the company's largest workforce by country. Tens of thousands of Indian-origin professionals staff its offices in the United States, the United Kingdom, and Europe. Many of them work directly with the Azure DevOps environments and cloud infrastructure that this breach allegedly compromised.

The immediate risk is reputational rather than operational. Accenture's clients — Microsoft, Google, AT&T, Verizon — entrust it with some of their most sensitive development and cloud migration work. If active access tokens or private keys were indeed exfiltrated, the window for secondary exploitation depends entirely on how quickly Accenture rotated its credentials after discovering the breach.

For Indian IT workers more broadly, the incident is a reminder that the consulting model's greatest strength — deep integration into client environments — is also its greatest vulnerability. A compromised Accenture endpoint does not just expose Accenture's code. It can expose the systems of every client whose infrastructure touches that developer's workspace.

## The Broader Cybersecurity Landscape

The breach lands in a year when cybersecurity has climbed to the top of India Inc.'s risk register. A FICCI-EY survey released earlier this year found that 51 percent of Indian senior executives now rank cybersecurity incidents as their single biggest business threat. PwC's 2026 Global Digital Trust Insights report noted that a quarter of Indian enterprises suffered breaches costing over $1 million in the past three years. India's CERT-In has issued emergency advisories on AI-driven cyberattacks, warning that frontier AI models can discover vulnerabilities and generate exploits with minimal human involvement.

For the $315 billion Indian IT services industry — already navigating AI disruption, client budget pressures, and visa uncertainties — a high-profile breach at its largest firm is the kind of headline that makes every contract renewal conversation a little harder."""
    },

    # ── Article 3: Nvidia Vera CPU ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia's New CPU Is Beating Intel and AMD in Its First Benchmarks. The $200 Billion Server Market Will Never Be the Same.",
        "subheadline": "The Vera processor — purpose-built for AI agents that never stop running — outperforms Intel Xeon by 55% and AMD EPYC by 10%. Perplexity, OpenAI, Anthropic, and SpaceX are already signed up. Jensen Huang is projecting $20 billion in sales this fiscal year.",
        "slug": make_slug("nvidia-vera-cpu-beats-intel-amd-ai-agents-server-market"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "Nvidia, Intel, and AMD collectively employ tens of thousands of Indian-origin engineers across their chip design centres in Santa Clara, Austin, Bengaluru, and Hyderabad. A market restructuring of this magnitude directly affects career trajectories, team priorities, and hiring patterns at all three companies.",
        "tags": ["nvidia", "vera-cpu", "intel", "amd", "ai-agents", "semiconductors", "jensen-huang"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/perplexity-says-it-plans-use-nvidias-new-cpu-2026-07-08/"},
            {"name": "Phoronix (benchmarks)", "url": "https://www.phoronix.com/review/nvidia-vera-cpu"},
            {"name": "TechSpot", "url": "https://www.techspot.com/news/107268-jensen-huang-says-nvidia-vera-cpu-challenge-xeon.html"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/cpu-competition-amd-stock-price-c1ade979"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia CEO Jensen Huang, who has positioned the Vera CPU as the company's first standalone server processor",
        "image_attribution": "Wikimedia Commons",
        "body": """For three decades, the server CPU market has been a two-horse race. Intel built it. AMD disrupted it. Everyone else watched. That era is ending.

Nvidia's Vera processor — the company's first standalone CPU, built around 88 custom ARM-based Olympus cores — has posted its initial independent benchmarks, and the numbers are difficult for Intel or AMD to dismiss. In comprehensive testing by Phoronix, the industry's most respected Linux hardware reviewer, Vera delivered a 55 percent performance advantage over Intel's 128-core Xeon 6980P and a 10 percent edge over AMD's EPYC 9575F, the latter a 5 GHz high-frequency part that represents AMD's best current silicon.

On a per-core basis, the gap widens further. Vera compiled a default Linux kernel in 20 seconds — the fastest result Phoronix has ever recorded in that test — and delivered twice the per-core compilation speed of the 128-core Intel chip. Phoronix's Michael Larabel called it "competitiveness to Intel/AMD x86_64 CPUs that I have never seen out of any other ARM or non-x86_64 processors."

## Why This CPU Exists

The answer is AI agents. Unlike traditional software — where a human sends a request, waits for a response, and takes a break — AI agents run continuously, executing complex sequences of code compilation, data processing, tool calling, memory management, and result verification with no downtime.

That pattern fundamentally changes what you need from a CPU. Intel's Xeon and AMD's EPYC were designed for workloads with idle intervals. Vera was designed for workloads that never pause. Its architecture prioritises sustained single-core throughput and deterministic memory latency under parallel load — qualities that Perplexity's Vice President of Infrastructure Nate Kupp described as "a dead-on fit" after the chip completed AI agent coding tasks 1.5 times faster than the traditional CPUs it replaced.

"AI agents do not take breaks between tasks," Kupp told Reuters. In separate testing, AI research firm Prime Intellect found that Vera maintained consistent bandwidth and low latency even as workloads scaled — the kind of predictable performance that agentic computing demands.

## The Customer List Tells the Story

Nvidia has disclosed that OpenAI, Anthropic, Oracle, and SpaceX will use Vera CPUs alongside Perplexity. These are not speculative design wins. The company hand-delivered the first Vera racks to major AI firms in recent weeks and expects to generate $20 billion in CPU revenue by the end of its fiscal year — an extraordinary figure for a product category Nvidia did not compete in 18 months ago.

The previous-generation Grace CPU was sold only as a companion to Nvidia's GPUs. Vera is different: it will be available as a standalone product from partners in dual- and single-socket configurations, directly competing for the same data centre sockets that Intel and AMD currently occupy.

## Intel and AMD Are Not Standing Still

AMD's stock has surged 280 percent in the past 12 months on the strength of its EPYC server CPUs and Instinct AI GPUs. William Blair analyst Sebastien Naji initiated coverage last week with a Market Perform rating, warning that "AMD's 146% surge since April has left the shares priced at a premium to peers with little room for error."

Naji specifically cited Nvidia's Vera, alongside ARM and Qualcomm, as competitive threats that could end AMD's "era of easy CPU share gains." Intel, meanwhile, is staging its own comeback — stock up more than 370 percent in a year — and is expected to regain manufacturing competitiveness by 2028 with its Coral Rapids architecture.

The three-way battle will play out in earnings season. TSMC, which manufactures chips for all three companies' customers, reports on Thursday. Its guidance will signal whether the hyperscaler spending spree that underpins every AI chip company's revenue forecast is holding or cracking.

## The Indian Engineering Calculus

Nvidia, Intel, and AMD all maintain large engineering operations in India. Nvidia's Bengaluru and Hyderabad offices are central to its GPU and software development. Intel employs thousands of chip designers across its Indian centres. AMD's Hyderabad campus is one of its largest outside the United States.

A market restructuring of this magnitude — where a GPU company suddenly competes for CPU sockets, and AI agents redefine what "good performance" means — reshuffles priorities, headcounts, and career trajectories at all three firms. Indian engineers with CPU architecture experience become more valuable across the board, whether they are optimising Vera cores at Nvidia, defending Xeon share at Intel, or scaling EPYC deployments at AMD.

For NRI investors tracking the semiconductor cycle, the picture is more nuanced. Global semiconductor sales hit a record $120.6 billion in May 2026, up 104 percent year over year. But forward P/E ratios for Intel, AMD, and Marvell stand well above their long-term averages, and earnings growth is expected to moderate from triple-digit percentages to 46 percent in 2027. The supercycle is real, but its pricing may already reflect that."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
