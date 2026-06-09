#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 03:00 UTC run"""
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
    # ── Article 1: Oracle 30K Layoffs, India Hit Hardest ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Oracle Is Cutting 30,000 Jobs by June 15. India Lost 12,000 of Them.",
        "subheadline": "The largest layoff in Oracle's 48-year history is completing this week — and India, where 12,000 employees were terminated by email at 6 AM, bore the heaviest blow. Campus offers at IITs and NITs were revoked overnight.",
        "slug": make_slug("oracle-30000-layoffs-india-12000-iit-nit-revoked"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Oracle employs tens of thousands of Indian engineers in the US on H-1B visas and is one of India's largest tech employers. The 12,000 India job cuts affect families on both sides of the ocean — NRI employees worry about team restructuring and visa exposure, while relatives back home face a suddenly hostile job market. The IIT/NIT campus offer revocations hit incoming graduates hardest.",
        "tags": ["oracle", "layoffs", "india-tech", "h-1b", "enterprise-software", "ai-restructuring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Salesforce Ben", "url": "https://www.salesforceben.com/oracle-layoffs-30000-employees/"},
            {"name": "IndMoney", "url": "https://www.indmoney.com/articles/stocks/oracle-layoffs-2026"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/oracle-layoffs-30000-job-cuts-by-june-15"},
            {"name": "LatestLY", "url": "https://www.latestly.com/latest/news/oracle-layoffs-30000/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Oracle-October2011.JPG",
        "image_caption": "Oracle Corporation headquarters in Redwood City, California",
        "image_attribution": "Wikimedia Commons",
        "body": """On March 31, 2026, tens of thousands of Oracle employees across the United States, India, Canada, and Mexico opened their inboxes to a five-line email from "Oracle Leadership." No warning. No call from HR. No conversation with their manager. Just a flat statement: your role has been eliminated, today is your last day.

System access was cut within the hour.

By mid-June, Oracle will have completed the departure of approximately 30,000 employees — roughly 18 percent of its global workforce and the largest layoff in the company's 48-year history. And India, where Oracle runs sprawling engineering centres in Bengaluru, Hyderabad, and Pune, bore the single heaviest share: an estimated 12,000 jobs wiped out in one morning.

## The Paradox That Defines This Moment

What makes Oracle's restructuring so disorienting is the context. This is not a company in decline. In fiscal Q3 2026, Oracle reported revenue of $17.2 billion, up 22 percent year over year. Cloud revenue surged 44 percent to $8.9 billion, now accounting for more than half of total sales. The AI segment of Oracle Cloud Infrastructure grew 243 percent. Multicloud database revenue soared 531 percent.

Larry Ellison's company is printing money faster than at any point in its history. It is also firing people faster than at any point in its history.

The contrast is deliberate. Oracle's leadership has signalled that these cuts are designed to free up capital and engineering bandwidth for AI infrastructure — data centre buildouts, GPU procurement, and the headcount needed to run a hyper-scale cloud business. Legacy hardware divisions, consulting verticals, and sales territories outside the company's fastest-growing cloud regions were hit hardest.

## India Took the Biggest Hit

The 12,000 Indian layoffs sliced through multiple divisions: Oracle Health (where 8,000 to 10,000 cuts were concentrated globally), Revenue and Health Sciences, SaaS and Virtual Operations Services, and — most painfully for India's tech ecosystem — NetSuite's India Development Centre.

Employees reported receiving termination emails at approximately 6 AM local time, a detail that has become a grim symbol of the restructuring. Separation packages offered four weeks of base pay for the first year of service, plus one additional week per year worked, capped at 26 weeks. Unvested restricted stock units were forfeited immediately.

But the collateral damage extended beyond current employees. Oracle revoked campus placement offers at IITs and NITs — India's most competitive engineering institutions. For graduates who had signed offer letters and turned down alternatives, the news was devastating.

## What This Means for Indian Americans

For NRIs working at Oracle's Austin headquarters or its offices across the Bay Area, the restructuring raises immediate visa concerns. H-1B holders who lose their positions have a 60-day grace period to find new employment or change status. In a market where Oracle, Meta, Amazon, and Intuit have collectively shed over 50,000 jobs in the first half of 2026, that window is alarmingly tight.

The broader pattern is clear: Big Tech is restructuring around AI, and the transition cost is falling disproportionately on workers who built the previous generation of products. Oracle's cloud AI business grew 243 percent. Its workforce shrank 18 percent. The math is not subtle.

For Indian IT services companies — TCS, Infosys, Wipro — who count Oracle among their major platform partners, the restructuring also reshuffles competitive dynamics. Fewer Oracle employees means more consulting demand for implementation partners, but also signals that Oracle is automating functions these firms traditionally staffed.

## The Numbers in Perspective

Oracle joins a grim leaderboard. According to layoff trackers, more than 150,000 tech workers have been cut globally in 2026. Amazon leads the count with approximately 16,000 corporate layoffs in January. Meta notified 8,000 employees in May, with more planned for the second half. Intuit cut 3,000 — 17 percent of its workforce — on May 20.

The through-line connecting all of these: AI is both the justification for the cuts and the destination for the freed capital. Oracle's executives have been explicit about this. The company is not downsizing. It is re-allocating — from people who maintained legacy systems to infrastructure that serves the next era.

For the 12,000 Oracle employees in India who opened that email at six in the morning, the distinction is academic."""
    },

    # ── Article 2: NVIDIA Vera CPU — First Chip for AI Agents ──
    {
        "id": str(uuid.uuid4()),
        "headline": "NVIDIA Just Built a CPU for AI Agents, Not Humans. The Data Centre Will Never Be the Same.",
        "subheadline": "The Vera processor is NVIDIA's first standalone data centre CPU — designed specifically for agentic AI workloads, with 1.8x the performance of x86 silicon. Jensen Huang's message: agents are the new customers.",
        "slug": make_slug("nvidia-vera-cpu-agentic-ai-data-centre-intel-amd"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers dominate NVIDIA's design and architecture teams. The Vera CPU also deepens NVIDIA's partnership with Micron, whose Indian-origin CEO Sanjay Mehrotra is building a major semiconductor fab in Gujarat. For NRI engineers at Intel, AMD, and cloud companies, Vera reshuffles the competitive landscape they work in daily.",
        "tags": ["nvidia", "vera-cpu", "agentic-ai", "jensen-huang", "semiconductor", "data-center"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-ai-pc-push-2026-06-08/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/nvidia-vera-cpu-sk-hynix-ai/"},
            {"name": "CNN", "url": "https://www.cnn.com/business/intel-ai-agentic-race-nvidia/"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/nvidia-sk-hynix-vera-cpu"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang, who unveiled the Vera CPU at GTC Taipei during Computex 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """For two years, the artificial intelligence infrastructure story has been about GPUs — who makes them, who can buy them, and how many racks Jensen Huang can ship before demand outruns supply. That chapter is not over. But at GTC Taipei during Computex 2026, Huang opened a new one.

NVIDIA has built a CPU. Not for laptops. Not for gaming PCs. A data centre processor designed explicitly for a customer that does not exist yet in meaningful numbers: the AI agent.

The Vera CPU is NVIDIA's first standalone central processing unit for servers, putting it in direct competition with Intel's Xeon and AMD's EPYC — and with custom silicon from cloud giants like Amazon's Graviton. But Vera is not positioned as a general-purpose server chip. It is engineered specifically for the orchestration layer underneath agentic AI: the code execution, database queries, tool calls, and multistep reasoning loops that autonomous software performs thousands of times per second.

## Why a CPU for Agents Matters

NVIDIA claims Vera delivers roughly 1.8 times the agentic performance of incumbent x86 processors and approximately three times faster data processing on common workloads. The phrasing that stuck from Huang's two-hour keynote: "Agents are impatient."

The insight is architectural. Today's AI workflows follow a predictable pattern: a human sends a prompt, a GPU-heavy model generates a response, and the cycle pauses until the next prompt. Agentic AI does not pause. An autonomous agent tasked with auditing supply chain data or debugging a codebase will plan, search databases, call external APIs, backtrack when it hits an error, rewrite its approach, and synthesize results — all without human intervention. Each cycle can trigger 50 to 100 sequential model calls.

In that world, the CPU becomes a bottleneck. GPUs handle the raw thinking, but agents also need to execute code, manage memory, coordinate tool calls, and maintain state across long-running loops. Legacy CPUs crumble under that coordination workload, leaving expensive GPUs idling. Vera is designed to eliminate that mismatch.

"The CPU is now the conductor, and the GPU is the orchestra," Huang said.

## The Platform Play

Vera does not exist in isolation. NVIDIA confirmed that its Vera Rubin platform — a five-rack system spanning Vera Rubin NVL72 GPU systems, the Vera CPU, new networking silicon, and storage — is now in full production. Rack assembly times have been compressed to minutes. Samsung, SK Hynix, and Micron have all passed qualification for HBM4, the next-generation high-bandwidth memory that Vera Rubin requires.

The partnership with SK Hynix, announced after Huang flew to Seoul for a fried chicken dinner with SK Group's chairman, confirms that Vera will use SK Hynix DRAM. Huang told reporters he expects NVIDIA's business with SK Hynix to grow substantially through the second half of 2026 and into 2027, adding that the memory shortage will persist for "quite a few years" due to insatiable AI demand.

## What Indian Engineers Should Watch

Vera reshuffles the competitive map for tens of thousands of Indian-origin engineers in Silicon Valley and beyond. At Intel, where CEO Lip-Bu Tan is mounting an aggressive comeback, every CPU it sells to data centres now faces a new competitor with the NVIDIA software ecosystem behind it. At AMD, Lisa Su's EPYC line must contend with a rival that integrates tightly with the GPUs already dominating AI infrastructure.

For Indian engineers working at cloud companies — AWS, Azure, Google Cloud — the question is whether Vera can displace the custom silicon these platforms have spent billions developing internally.

And there is a supply chain angle that lands closer to home. Micron, whose Indian-origin CEO Sanjay Mehrotra is building a major semiconductor packaging and testing facility in Gujarat under India's semiconductor mission, is now a qualified HBM4 supplier for the Vera Rubin platform. That Gujarat fab represents one of the most significant bets on India's semiconductor future — and NVIDIA's stamp of approval gives it strategic weight.

## The Bigger Shift

Huang's keynote repeated a single phrase like a mantra: "Compute is revenue. Compute is profit." The subtext is that NVIDIA no longer sees itself as a chip company selling hardware to tech firms. It sees itself as the infrastructure layer for a new economy where software agents, not humans, are the primary consumers of computing power.

There will be more agents than people, Huang claimed. The market they require will be larger than the one NVIDIA already dominates. It sounds like marketing until you map it against the agentic roadmaps of every major enterprise software company — Microsoft's Autopilots, Google's Gemini agents, Oracle's autonomous database — and realise it is probably conservative.

For the Indian tech professionals who design, deploy, and maintain the infrastructure underneath all of it, the Vera CPU is not just a product announcement. It is a signal that the job description is changing — again."""
    },

    # ── Article 3: Micron's Gujarat Fab Gets NVIDIA Validation ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron's Gujarat Fab Just Got Its Biggest Validation. NVIDIA Needs Its Chips.",
        "subheadline": "Sanjay Mehrotra's Micron cleared HBM4 qualification for NVIDIA's Vera Rubin platform — placing India's first major semiconductor facility squarely in the AI supply chain. Micron stock surged nearly 10 percent.",
        "slug": make_slug("micron-gujarat-fab-nvidia-hbm4-sanjay-mehrotra-india-semiconductor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Micron CEO Sanjay Mehrotra is Indian-born, from Kanpur. His company's Gujarat fab is India's most tangible entry into the global semiconductor supply chain. For NRI investors, Micron's 10% stock surge and HBM4 qualification signal that India's chip ambitions are finally hitting commercial milestones — not just government press releases.",
        "tags": ["micron", "sanjay-mehrotra", "semiconductor", "india-fab", "nvidia", "hbm4", "gujarat"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/nvidia-sk-hynix-vera-cpu"},
            {"name": "CoinCentral", "url": "https://coincentral.com/sk-hynix-nvidia-vera-cpu/"},
            {"name": "Bloomberg (via WebProNews)", "url": "https://www.webpronews.com/nvidia-vera-cpu-sk-hynix-ai/"},
            {"name": "CNN Business", "url": "https://www.cnn.com/business/intel-ai-agentic-race-nvidia/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron CEO Sanjay Mehrotra, whose company's Gujarat facility is India's most significant semiconductor investment",
        "image_attribution": "Wikimedia Commons",
        "body": """For two years, India's semiconductor ambitions have lived mostly in the realm of government announcements, MoU signings, and PowerPoint timelines. The Modi government's India Semiconductor Mission committed over $10 billion. Tata Electronics broke ground on a fab in Dholera. CG Semi and ISMC sketched out roadmaps. But the question that hung over all of it was: would anyone in the global chip supply chain actually need what India produces?

Last week, Micron Technology got an answer.

At Computex 2026 in Taipei, NVIDIA CEO Jensen Huang confirmed that Samsung, SK Hynix, and Micron have all passed qualification for HBM4 — the next-generation high-bandwidth memory critical to NVIDIA's Vera Rubin AI platform. Vera Rubin is now in full production. It is the infrastructure that will power the next wave of AI factories worldwide. And Micron — whose Indian-born CEO Sanjay Mehrotra is building a major semiconductor assembly and testing facility in Sanand, Gujarat — is a qualified supplier.

Micron stock surged nearly 10 percent on the news, closing at roughly $949 a share.

## What Gujarat Actually Builds

It is worth being precise about what the Gujarat facility does and does not do. This is not a front-end wafer fabrication plant. Micron is not manufacturing silicon in India — yet. The Sanand facility, backed by approximately $2.75 billion in investment with significant subsidies from both the central and Gujarat state governments, focuses on semiconductor assembly and testing (OSAT): the back-end process of packaging bare dies into finished chips and running quality checks.

That distinction matters, but it should not be dismissed. Assembly and testing is where HBM chips are stacked, bonded, and validated — and HBM is the single hottest product category in the semiconductor industry. Each Vera Rubin rack requires enormous quantities of high-bandwidth memory. If Gujarat can process even a fraction of that volume, it places India in the critical path of AI infrastructure supply chains for the first time.

## Sanjay Mehrotra's Quiet Bet

Mehrotra, born in Kanpur and raised in Delhi, co-founded SanDisk before leading Micron since 2017. He has been characteristically understated about the Gujarat project in public, framing it as a long-term investment aligned with both India's strategic priorities and Micron's need to diversify its manufacturing footprint beyond Southeast Asia.

But the commercial logic has sharpened dramatically. AI infrastructure demand is consuming memory at a rate that has created what Huang described as a shortage lasting "quite a few years." HBM4 specifically is a premium product with limited global supply. SK Hynix leads production, Samsung is ramping, and Micron — the only American-headquartered HBM supplier — is now fighting for share in a market projected to exceed $30 billion by 2027.

Gujarat gives Mehrotra an additional packaging node in a geography that is actively courting semiconductor investment. Labour costs are lower. The Indian government is eager to demonstrate a success story. And the strategic symbolism — an Indian-origin CEO helping India enter the global chip supply chain — is powerful, even if neither Mehrotra nor Modi would frame it that way in public.

## The NRI Investor Angle

Micron's stock has been on a remarkable run. From a 52-week low near $103, shares have climbed to nearly $950 — a ninefold increase driven almost entirely by AI-related memory demand. For NRI investors who track the Indian semiconductor story, the HBM4 qualification is the first concrete evidence that India's chip infrastructure is not merely aspirational.

The comparison with Tata Electronics' Dholera fab is instructive. Tata's project is larger in ambition — a full front-end fabrication facility — but is still under construction and years from commercial production. Micron's Gujarat plant is operational now and is already part of a supply chain that NVIDIA has validated.

That is a meaningful distinction for investors weighing India's semiconductor thesis. Government commitments and ground-breaking ceremonies generate headlines. HBM4 qualification generates purchase orders.

## What Comes Next

India's semiconductor journey is still in its early chapters. The country does not fabricate advanced logic chips. Its packaging capabilities, while growing, remain modest compared to TSMC's facilities in Taiwan or ASE's operations across Asia. The skills gap is real — India produces exceptional software engineers but has limited depth in semiconductor process engineering.

But the trajectory is unmistakable. Micron's Gujarat facility is expanding. Tata's Dholera project is progressing. And the global chip supply chain, under pressure from US-China tensions and concentrated geographic risk, is actively looking for new nodes.

For Sanjay Mehrotra, the NVIDIA qualification is validation of a bet he placed years ago. For India, it is something rarer: proof that the semiconductor mission is producing commercial outcomes, not just policy documents.

Micron shares reflected that distinction — up nearly 10 percent in a single session. The Gujarat fab did not build NVIDIA's next GPU. But it may have earned a seat at the table where AI infrastructure gets assembled. In the semiconductor business, that is how empires begin."""
    },
]

# ── Insert articles ──
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
