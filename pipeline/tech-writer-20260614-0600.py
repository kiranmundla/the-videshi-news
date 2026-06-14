#!/usr/bin/env python3
"""Tech writer — 2026-06-14 06:00 UTC run. Three articles across beats A, D."""

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
    # ── Article 1: Jayshree Ullal / Arista 7060XE7 ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Jayshree Ullal's Arista Launches 1.6-Terabit Switches. AI's Bandwidth Bottleneck Just Got an Upgrade.",
        "subheadline": "The 7060XE7 Series delivers 100 terabits per second of switching capacity, backed by Meta, Microsoft, and Oracle — and Ullal is positioning Arista at the dead centre of the AI infrastructure buildout.",
        "slug": make_slug("jayshree-ullal-arista-7060xe7-ai-networking-data-center"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-origin CEO Jayshree Ullal leads the company building the networking backbone for every major AI data centre — a story of diaspora leadership in the invisible layer that makes AI work.",
        "tags": ["arista-networks", "jayshree-ullal", "ai-infrastructure", "data-centers", "indian-ceo"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2421107/can-aristas-advanced-networking-platform-meet-the-growing-ai-demand"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NYSE/ANET/"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/goldman-sachs-rethinks-cybersecurity-stocks-palo-alto-outlook"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Jayshree_Ullal_Arista_CEO.jpg/330px-Jayshree_Ullal_Arista_CEO.jpg",
        "image_caption": "Jayshree Ullal, CEO of Arista Networks",
        "image_attribution": "Wikimedia Commons",
        "body": """Everyone knows who builds AI models. Far fewer know who builds the wiring.

Arista Networks, led by India-born CEO Jayshree Ullal, has just launched the 7060XE7 Series — a suite of 1.6-terabit Ethernet platforms engineered for the crushing bandwidth demands of AI training and inference workloads. The product line delivers up to 100 terabits per second of switching capacity and ships with endorsements from three of the world's largest cloud operators: Meta, Microsoft, and Oracle.

It is, by any measure, an aggressive play for the physical layer of the AI boom. And it is being run by a woman who arrived in the United States from New Delhi at age sixteen.

## What the 7060XE7 actually does

The series includes four configurations: the air-cooled 7060XE7-64PS and 7060XE7-64PRS rack switches, a liquid-cooled variant (the 7060XE7-64PRS-RV3-L) for high-density GPU clusters, and the 7060XE7-128PE, which packs 128 ports of 800-gigabit connectivity into a four-rack-unit chassis. Together, they are designed to handle the data volumes generated when thousands of GPUs train models simultaneously — the kind of workload that breaks conventional networking gear.

The platform supports Linear Pluggable Optics (LPO), which reduces interconnect power consumption by roughly 60 per cent — a significant detail when electricity is becoming the binding constraint on AI expansion. The switches run on Broadcom's Tomahawk 6 silicon and support both Arista's Extensible Operating System and open network operating systems, with built-in load balancing, congestion management, and telemetry.

## The Ullal factor

Jayshree Ullal has led Arista since 2008, transforming it from an Ethernet startup into a $228 billion company. Born in New Delhi and raised in India before moving to the US, she holds a degree in electrical engineering from San Francisco State University and an MBA from Santa Clara. Under her leadership, Arista went public in 2014 and has since become the de facto networking vendor for hyperscale cloud providers.

Wall Street has noticed the AI tailwind. Bank of America recently raised its price target on Arista to $200, Deutsche Bank upgraded the stock to a "buy" rating, and Susquehanna moved to "strong-buy." Analysts at Erste Group raised FY2027 earnings estimates, signalling confidence that the AI infrastructure buildout has years of runway left.

The company's balance sheet is entirely debt-free, with rising cash reserves and strong operating cash flow — a rarity among technology companies at this scale.

## Why NRIs should care

For Indian professionals working in AI infrastructure at companies like Meta, Google, and Microsoft, Arista's switches are likely already underfoot — literally connecting the GPU clusters they train models on. Ullal's trajectory from Delhi to the helm of a quarter-trillion-dollar networking giant is one of the more understated diaspora success stories in Silicon Valley.

For NRI investors, the stock has traded between $140 and $303 over the past year. The 7060XE7 launch and the broader AI infrastructure spending wave give Arista a plausible multi-year growth story — though the stock's current P/E ratio of around 40 demands that the growth materialise, not merely be promised.

There is also a deeper structural story here. The AI revolution is typically narrated through model breakthroughs and consumer products. But it runs on physical infrastructure — switches, optics, cooling systems — and that layer is disproportionately built and led by Indian-origin engineers and executives. Ullal at Arista, Jensen Huang at NVIDIA, and the sprawling Indian engineering teams at Broadcom and Cisco form the backbone of a supply chain that the rest of the industry depends on but rarely acknowledges."""
    },

    # ── Article 2: Nikesh Arora / Palo Alto Networks + Goldman thesis ─────
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora's Palo Alto Networks Posts $3 Billion Quarter. Goldman Says the Real AI Security Boom Hasn't Started.",
        "subheadline": "Revenue up 31 per cent, next-gen security ARR surging 60 per cent — and Goldman Sachs argues the agentic AI era will force enterprise security spending into an inflection that mirrors the cloud security lag of 2015.",
        "slug": make_slug("nikesh-arora-palo-alto-networks-q3-goldman-ai-security"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Former Google executive Nikesh Arora has turned Palo Alto Networks into the most valuable pure-play cybersecurity company on earth — a story that matters to every NRI investor tracking the AI spending chain.",
        "tags": ["palo-alto-networks", "nikesh-arora", "cybersecurity", "ai-security", "indian-ceo", "goldman-sachs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/goldman-sachs-rethinks-cybersecurity-stocks-palo-alto-outlook"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/PANW/earnings/"},
            {"name": "Palo Alto Networks Q3 2026 Results", "url": "https://investors.paloaltonetworks.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg/330px-Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Nikesh Arora, Chairman and CEO of Palo Alto Networks",
        "image_attribution": "Wikimedia Commons",
        "body": """Palo Alto Networks just posted the kind of quarter that makes a thesis look inevitable.

The cybersecurity giant, led by Chairman and CEO Nikesh Arora, reported fiscal Q3 2026 revenue of $3.0 billion — up 31 per cent year over year — beating analyst expectations of $2.94 billion. Non-GAAP earnings came in at $0.85 per share, topping the Street consensus of $0.79. Next-Generation Security annual recurring revenue hit $8.1 billion, growing 60 per cent. Adjusted free cash flow surged to $910 million, up from $578 million in the year-ago quarter.

Those are not incremental gains. They are the numbers of a company riding a structural wave.

## Goldman's thesis: we've seen this before

The results landed alongside a note from Goldman Sachs that reframed the entire cybersecurity sector through a historical lens. Goldman's analysts drew a direct parallel between the current moment and the cloud security lag that played out from 2015 to 2020.

During the cloud era, enterprise security spending took roughly two years to move from below 1 per cent of infrastructure spend to above 3 per cent. Goldman argues that a similar pattern — but faster — is about to unfold with AI. As agentic AI moves from proof-of-concept to production, the security requirements become non-negotiable. AI agents that run persistently, access internal systems, and execute actions autonomously create attack surfaces that did not exist twelve months ago.

Goldman expects this shift to accelerate in the second half of 2026, with full momentum into 2027. The firm pointed to Palo Alto's Prisma AIRS product as a key beneficiary — a platform purpose-built to secure AI agents and workloads in enterprise environments.

Arora himself was blunt on the earnings call: "The latest advancements at the AI frontier have increased the level of urgency around cybersecurity, and redefined the shape of the industry for the coming years." He added that Q3's events "have increased the terminal value of the entire cybersecurity industry."

## The Arora story

Nikesh Arora's journey to the helm of Palo Alto Networks is an unlikely one. Born in Ghaziabad, Uttar Pradesh, he studied at IIT Varanasi (then BHU) and later at Northeastern and Boston College. He spent a decade at Google, rising to Chief Business Officer and the highest-paid executive in the company's history, before a stint as president and COO of SoftBank under Masayoshi Son.

He took over Palo Alto Networks in 2018 and has since steered the company through a platformisation strategy that consolidated dozens of point security products into a unified platform — a bet that initially spooked investors but has now delivered consistent outperformance. Palo Alto's market cap sits at roughly $228 billion, making it the most valuable pure-play cybersecurity company in the world.

For Q4 fiscal 2026, Arora guided for NGS ARR of $8.90 to $8.95 billion (59-60 per cent growth) and revenue of $3.345 to $3.355 billion (32 per cent growth). Scotiabank raised its price target to $320 with a bullish rating. Multiple other firms reiterated buy ratings with price targets north of $300.

## What this means for Indian tech professionals

For the tens of thousands of Indians working in enterprise IT and cybersecurity across the United States, Arora's platform play is reshaping the tools they use daily. Palo Alto's consolidation strategy means fewer vendors, fewer integration headaches, and — Goldman's thesis suggests — a growing budget to hire the people who can secure AI systems.

For NRI investors, the stock has run from a 52-week low of $140 to a recent close of $280, nearly doubling. The P/E ratio of 229 prices in enormous expectations. But if Goldman's AI security inflection thesis is right, the company's current run rate may be the floor, not the ceiling.

The deeper signal is cultural. An IIT alumnus now leads the most valuable cybersecurity company on earth, at precisely the moment when the global economy is betting that AI agents will handle everything from customer service to code deployment to financial transactions. Someone has to secure all of that. It helps when the person doing it understands both the technology and the stakes."""
    },

    # ── Article 3: India Semiconductor Mission ₹31,299 Cr ──────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chip Factories Start Spending Real Money. ₹31,299 Crore Hits the Shop Floor by FY27.",
        "subheadline": "Five companies — including Tata Electronics, Micron, and CG Power — have already deployed ₹15,799 crore in FY26, with another ₹15,500 crore queued for equipment procurement as India's semiconductor mission moves from announcements to assembly lines.",
        "slug": make_slug("india-semiconductor-mission-31299-crore-fy27-tata-micron"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's semiconductor buildout is creating a new category of return-to-India career opportunities for NRI chip engineers — and an investment thesis that didn't exist three years ago.",
        "tags": ["india-semiconductor", "tata-electronics", "micron", "asml", "chip-manufacturing", "nri-careers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/indian-semiconductor-mission-attract-31299-crore-investment-fy27/"},
            {"name": "Livemint", "url": "https://www.livemint.com/technology/tech-news/where-does-india-stand-in-chip-ambitions-tata-electronics-asml-intel-semiconductor-mission-mint-explainer-11718010260547.html"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/tata-electronics-partners-asml-to-boost-indias-semiconductor-manufacturing-push/article69589210.ece"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Inside a semiconductor fabrication cleanroom facility",
        "image_attribution": "Pexels",
        "body": """For years, India's semiconductor ambitions lived in press releases and MoUs. Now they are living on construction sites.

Companies operating under the India Semiconductor Mission (ISM) are projected to invest ₹31,299 crore ($3.8 billion) by fiscal year 2027 — roughly 19 per cent of the total committed investment of ₹1.65 trillion across India's chip ecosystem. Of that, ₹15,799 crore has already been deployed in FY26 by five anchor participants: Tata Electronics, Micron Technology, CG Power (with Japan's Renesas), and two others. Another ₹15,500 crore is earmarked for FY27, focused primarily on procuring and installing the precision equipment that turns a building into a fab.

The numbers represent a phase shift. Buying lithography systems, deposition tools, and wafer-handling robots is the point at which a semiconductor project stops being an aspiration and starts being a factory.

## Tata's ASML deal changes the equation

The most consequential recent development is Tata Electronics' partnership with ASML, the Dutch company that holds a near-monopoly on advanced lithography equipment. Signed during Prime Minister Modi's visit to the Netherlands in May, the deal ensures that ASML will deploy its full suite of lithography tools at Tata's upcoming 300mm semiconductor fab in Dholera, Gujarat — India's first commercial wafer fabrication plant.

The Dholera facility carries a planned investment of ₹91,000 crore ($11 billion) and aims to produce 50,000 wafers per month for automotive, mobile, AI, and industrial applications. Tata Electronics CEO Randhir Thakur — a former Intel executive who led Intel Foundry Services — has been explicit about the ambition: the Dholera fab is not a pilot project. It is designed to serve global customers and compete with established facilities in Taiwan, South Korea, and the United States.

Intel is already on board as a customer, having signed an MoU with Tata in late 2025 to explore manufacturing and packaging of Intel products for the Indian market. The Assam OSAT (Outsourced Semiconductor Assembly and Test) facility is expected to begin operations this year, with the Gujarat fab targeting production in 2027.

## The broader ecosystem

Beyond Tata, the ISM now encompasses twelve approved semiconductor projects across multiple states. CG Power, partnering with Renesas Electronics and Thailand's Stars Microelectronics, is building a chip packaging unit in Sanand, Gujarat, with capacity for 15 million units per day. Micron's ATMP facility in Sanand — the company led by Lucknow-born CEO Sanjay Mehrotra — continues rapid construction.

The Union Budget 2026-27 allocated ₹1,000 crore specifically for India Semiconductor Mission 2.0, with support for industry-led research centres and training programmes. The government now offers up to 50 per cent of project costs on a pari-passu basis for fab, compound semiconductor, and ATMP facilities.

Gujarat has emerged as the nucleus. Dholera and Sanand host the majority of large-scale projects, though Assam, Uttar Pradesh, and Odisha are developing their own semiconductor clusters with tailored state-level incentives.

## Why this matters for NRIs

For the thousands of Indian engineers working in semiconductor design and manufacturing at Intel, Micron, Qualcomm, TSMC, and Samsung in the United States, India's fab buildout is creating a new category of career opportunity. Tata's partnership with ASML and Intel means the Dholera facility will need lithography specialists, process engineers, and yield managers — roles that currently exist almost exclusively in Taiwan, South Korea, and the American Southwest.

For NRI investors, the publicly listed participants offer direct exposure. CG Power trades on the NSE. Tata Electronics' parent companies — Tata Sons and its listed affiliates — provide indirect access. And the broader supply chain, from equipment vendors to chemicals and gases suppliers, is generating a cluster of investable companies that barely existed in India five years ago.

The scepticism is earned. India has announced semiconductor ambitions before, only to watch them stall. But the current cycle is different in one measurable way: the money is actually being spent. ₹15,799 crore deployed in a single fiscal year, with equipment orders placed and construction timelines being met, is not a press release. It is a fab taking shape."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
