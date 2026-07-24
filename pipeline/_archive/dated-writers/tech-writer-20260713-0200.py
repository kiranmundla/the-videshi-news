#!/usr/bin/env python3
"""Technology writer – 2026-07-13 02:00 AM PT run"""
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
    # ── Article 1: TCS Leadership Reshuffle ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Just Split Its Biggest American Unit in Two. The Restructure Reveals Where Indian IT's Next Billion Will Come From.",
        "subheadline": "Five new business groups, a divided U.S. banking practice, and a fresh leadership slate — CEO Krithivasan is betting that specialisation, not scale, will protect TCS from the AI squeeze.",
        "slug": make_slug("tcs-reshuffle-us-banking-five-business-units-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "TCS employs tens of thousands of Indian professionals across the U.S. on H-1B and L-1 visas. A restructure that carves out a dedicated U.S. West Coast unit and splits the banking vertical — the company's single largest revenue stream — directly reshapes career paths, reporting lines, and visa sponsorship structures for Indian tech workers from Wall Street to the Bay Area.",
        "tags": ["tcs", "indian-it", "ai-disruption", "leadership", "us-banking"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tcs-rejigs-leadership-team-creates-new-business-units-2026-07-13/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tata_Consultancy_Services_Madhapur_Hyderabad.jpg/1280px-Tata_Consultancy_Services_Madhapur_Hyderabad.jpg",
        "image_caption": "Tata Consultancy Services campus in Madhapur, Hyderabad",
        "image_attribution": "Wikimedia Commons",
        "body": """India's largest IT services exporter just made its most consequential organisational move in years — and the timing is no accident.

On Sunday, Tata Consultancy Services announced a sweeping leadership reshuffle and the creation of five entirely new business groups, according to a series of internal memos from CEO K. Krithivasan and COO Aarthi Subramanian seen by Reuters. The restructure targets TCS's most lucrative market — the United States — at a moment when artificial intelligence threatens to compress the very project timelines and engineering headcounts that built India's $315 billion IT services industry.

## The Banking Split

The most significant move: TCS is cleaving its Americas banking and financial services unit — the company's single largest vertical, accounting for roughly a third of total revenue — into two separate divisions. Rakesh Kumar will lead U.S. West banking, while Mohan Veeturi takes the U.S. East operation. Susheel Vasudevan, the current U.S. banking head, moves to a strategic role reporting directly to Krithivasan.

The split is not merely administrative. North America accounts for nearly half of TCS's revenue, and the banking unit within it has been a battleground where AI-driven automation is already shortening engagement cycles and putting pressure on margins. By creating two focused units — one tracking Silicon Valley fintech innovation, the other serving Wall Street's legacy transformation needs — Krithivasan is making a bet that granular market intimacy will matter more than monolithic scale in the AI era.

Manmeet Chhabra, who currently leads the Canada banking unit, takes over as country head for all of TCS Canada.

## Five New Business Groups

Beyond the banking restructure, TCS unveiled five new business groups, each with dedicated leadership:

- **ServiceNow practice** — a direct play for the platform's fast-growing enterprise workflow market, where TCS competes against Accenture and Deloitte for implementation contracts
- **Travel and transport** — a vertical gaining urgency as airlines and logistics companies accelerate AI adoption
- **Energy and utilities** — positioned to capture spending from the global energy transition
- **U.S. West Coast** — a standalone unit acknowledging that the Bay Area and Pacific Northwest tech ecosystem demands its own dedicated leadership, rather than being lumped into a national structure
- **Global autonomous businesses** — a catch-all for AI, robotics, and emerging technology engagements

TCS also appointed new leaders for its cybersecurity practice and its UK and European life sciences and communications verticals.

## The AI Subtext

The reshuffle arrives days after TCS reported better-than-expected revenue for the April–June quarter, buoyed by strong spending from banking clients and a weaker rupee that flattered dollar-denominated earnings. But the earnings call subtext was less reassuring. AI is compressing project timelines, reducing the demand for large engineering teams, and enabling clients to negotiate lower prices by citing productivity gains from AI tools.

For the Indian IT sector broadly — TCS, Infosys, Wipro, HCL Tech — the question is existential: can these companies evolve from body-shop scale into AI-first consulting and platform businesses before the margin squeeze becomes irreversible?

## What This Means for Indian Professionals in the U.S.

For the tens of thousands of Indian tech professionals working for TCS across America — many on H-1B and L-1 visas — this restructure will ripple through in concrete ways. A dedicated U.S. West Coast unit signals more hiring and investment in the Bay Area, Seattle, and Portland. The banking split could mean new leadership, new project assignments, and new visa sponsorship decisions for those embedded in financial services clients from New York to Charlotte.

The creation of an autonomous businesses group also opens a new career track: one focused not on maintaining existing enterprise systems, but on building AI-native products and services. For Indian engineers debating whether to stay at a services giant or jump to a product company, that distinction may matter more than a title change.

TCS has not disclosed how many roles will be affected by the reshuffle. But when India's largest private-sector employer reorganises its most profitable market, the downstream effects on the Indian professional community in America are never small."""
    },

    # ── Article 2: Micron $250B Investment ───────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sanjay Mehrotra Just Raised Micron's U.S. Bet to $250 Billion. It Is Now the Largest Private Investment in New York State History.",
        "subheadline": "The Kanpur-born CEO is building a closed-loop American semiconductor supply chain — from raw silicon wafers in Texas to memory fabs in Idaho and New York — as AI-driven chip demand enters what he calls an 'unprecedented' shortage.",
        "slug": make_slug("sanjay-mehrotra-micron-250-billion-us-investment-semiconductor"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sanjay Mehrotra, born in Kanpur and a co-founder of SanDisk, is one of the highest-profile Indian-origin CEOs leading America's semiconductor resurgence. His $250 billion commitment — creating 100,000 jobs — is a visible counterpoint to the H-1B backlash narrative and a reminder that Indian immigrants are building the physical infrastructure of American economic competitiveness.",
        "tags": ["micron", "sanjay-mehrotra", "semiconductor", "ai-chips", "indian-origin-ceo", "made-in-usa"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-boosts-us-investment-plan-again-commits-250-billion-through-2035-2026-07-10/"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/technology/micron-ceo-says-ai-boom-drives-unprecedented-memory-demand-company-invests-250b"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron CEO Sanjay Mehrotra at a company event in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """When Sanjay Mehrotra stood at the construction site in Clay, New York, on Thursday and watched the first concrete pour for what will become the largest private investment in the state's history, the moment carried a weight that transcended quarterly earnings.

The Kanpur-born CEO of Micron Technology announced that the company is raising its planned U.S. manufacturing and research investment from $200 billion to $250 billion through 2035 — a figure that places a single Indian-origin executive at the helm of the most ambitious semiconductor buildout in American history.

"Because of his leadership and policies, Micron would announce today that we are ahead of schedule," Mehrotra said of President Trump, whose tariff regime and CHIPS Act incentives have accelerated the onshoring wave. But strip away the politics, and the numbers speak for themselves.

## The Architecture of a Quarter-Trillion Bet

The $250 billion commitment spans three pillars across four states:

**New York**: The Clay mega-fab, roughly 20 miles north of Syracuse, is the centrepiece. When fully operational, it will produce advanced DRAM memory chips — the silicon that makes AI inference fast enough to be useful. The project alone is expected to create 9,000 direct Micron jobs and 50,000 in the broader state economy. First production is targeted for 2030.

**Idaho**: Micron's existing Boise operations are being expanded, with the company's global R&D headquarters anchoring the state's semiconductor ecosystem.

**Virginia**: Additional manufacturing capacity is being built out at existing sites.

**Texas**: Perhaps the most strategic move — Micron is investing $500 million in a partnership with GlobalWafers to secure domestic raw silicon wafer capacity at a new facility in Sherman. The deal includes a 10-year supply agreement, effectively ensuring that Micron's fabs will never depend on trans-Pacific shipping routes for their most fundamental input material.

In total, the investment is expected to support 100,000 American jobs.

## Why Memory Is the Bottleneck

Mehrotra's urgency is grounded in simple supply-and-demand physics. Memory chips — DRAM for processing speed and NAND for storage — are the circulatory system of every AI application. Each query to ChatGPT, each frame of autonomous driving video, each recommendation on your Instagram feed consumes memory bandwidth.

"Memory is in deep shortage right now," Mehrotra told Fox Business. "The demand for memory is at unprecedented levels."

The numbers support him. Nvidia CEO Jensen Huang said last month that shortages of AI memory would persist for years. SK Hynix, Micron's Korean rival, just debuted on the U.S. stock market via an IPO that valued it at staggering levels. Bank of America estimates global hyperscaler capital expenditure will hit $851 billion this year and $1.15 trillion in 2027 — and memory will represent 35 to 40 percent of that spending.

Micron's goal: produce 40 percent of its DRAM chips in the United States, up from a fraction today. That ambition makes the company a direct beneficiary of geopolitical anxiety about Taiwan, where TSMC produces the vast majority of the world's most advanced chips.

## The Mehrotra Story

For the Indian diaspora, Mehrotra's trajectory is both familiar and instructive. Born in Kanpur, he moved to the United States for graduate school, co-founded SanDisk in 1988 — building it into a $19 billion flash storage giant — and took the CEO role at Micron in 2017. He is now one of only a handful of Indian-origin executives running a Fortune 200 company with a market capitalisation approaching $300 billion.

His $250 billion commitment arrives at a charged moment for Indian Americans in corporate leadership. Just this week, Xbox CEO Asha Sharma — born in Wisconsin to an Indian-heritage family — faced racist backlash after announcing layoffs, with critics falsely portraying her as a foreign executive displacing American workers. Mehrotra's investment in American manufacturing capacity and American jobs offers a data point that speaks louder than any social media tirade.

## What It Means for NRI Investors and Engineers

For NRI investors, Micron's stock — trading around $979 after a 6 percent premarket jump on the announcement — reflects the memory supercycle thesis that has also driven SK Hynix, Samsung, and Nvidia to extraordinary valuations. The company's price-to-earnings ratio of roughly 22 suggests the market expects sustained growth but has not yet priced in the full upside of a domestic supply chain moat.

For Indian semiconductor engineers — a growing cohort at Micron, Intel, Broadcom, and Qualcomm — the New York and Idaho buildouts will create thousands of roles in chip design, process engineering, and manufacturing management. These are not software jobs that can be done remotely from Bangalore. They are physical, on-site roles that will require visa sponsorship and local talent development for years to come.

When a Kanpur-born CEO pours $250 billion of concrete and silicon into American soil, the line between immigrant story and industrial strategy disappears entirely."""
    },

    # ── Article 3: Meta's Iris Custom AI Chip ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Will Start Making Its Own AI Chips in September. The Move Could Reshape Thousands of Indian Engineers' Careers.",
        "subheadline": "Code-named Iris, Meta's custom silicon enters production after just six weeks of testing — a breakthrough for an in-house chip programme that floundered for five years. The company plans to double its computing power to 14 gigawatts by 2027.",
        "slug": make_slug("meta-iris-ai-chip-production-indian-engineers-broadcom"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta employs thousands of Indian engineers across its AI, infrastructure, and silicon teams. The pivot from buying Nvidia GPUs to designing custom chips in-house creates an entirely new career track — one that values semiconductor design skills over pure software engineering. For Indian professionals at Meta and across Big Tech, the custom chip wave is redrawing the talent map.",
        "tags": ["meta", "ai-chips", "custom-silicon", "broadcom", "nvidia", "indian-engineers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-put-ai-chip-into-production-september-it-looks-double-computing-capacity-memo-2026-07-10/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/07/10/business/meta-aims-to-make-its-own-chips-as-ai-giants-strive-for-independence-from-strained-supply-chain/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg",
        "image_caption": "Server unit in a modern data centre environment",
        "image_attribution": "Pexels",
        "body": """For five years, Meta's in-house chip programme was Silicon Valley's most expensive science project without a shipping product. That is about to change.

An internal memo reviewed by Reuters reveals that Meta Platforms will begin manufacturing its custom AI chip, code-named Iris, in September. Bug testing took just six weeks and found no major issues — a sharp turnaround for the Meta Training and Inference Accelerator (MTIA) programme that had stumbled through delays since its launch in 2021.

The chip is designed in partnership with Broadcom and will be manufactured by TSMC. It will not replace the thousands of Nvidia and AMD GPUs that power Meta's AI infrastructure. Instead, Iris is meant to handle the massive but routine inference workloads — the billions of daily ranking, recommendation, and content-moderation decisions across Facebook, Instagram, WhatsApp, and Threads — that currently consume expensive GPU time.

The strategic logic is blunt. "Adopting the latest GPUs at Meta's scale has been a heavy lift, and it has cost us time," the memo states.

## The Scale Problem

To understand why Meta is building its own chips, consider the numbers. The company expects to spend up to $145 billion on AI infrastructure this year alone. Its current data centre fleet runs at roughly seven gigawatts of computing capacity — enough to power a mid-sized European country. By 2027, the memo shows Meta plans to double that to 14 gigawatts.

At that scale, even small efficiency gains from custom silicon translate into billions in savings. Deutsche Bank analyst Benjamin Black estimates that a combination of Iris and Nvidia chips could lower Meta's data centre costs by up to 35 percent in 2027.

Meta plans to release a new chip generation roughly every six months through 2027 — a cadence that far exceeds the typical annual-or-longer release cycle in the semiconductor industry. The MTIA 300, Iris's predecessor, already powers Meta's ranking and recommendation systems. The later generations are designed specifically for inference, the process by which AI models respond to user queries in real time.

## The Big Tech Custom Chip Race

Meta is not alone. Amazon designs its own Graviton and Trainium chips. Google has its TPU line. Microsoft is developing its Maia accelerators. OpenAI recently introduced its first custom inference chip with Broadcom, and Anthropic is reportedly in talks with Samsung about developing its own silicon.

The pattern is clear: every company spending tens of billions on AI infrastructure is trying to reduce its dependence on Nvidia, whose data centre revenue surged 92 percent to $75.2 billion last quarter. When you are negotiating with Jensen Huang for GPU allocations worth billions, having your own chip programme is not just a cost play — it is leverage.

"I want something in my pocket when I'm sitting across the table from Jensen negotiating," Bernstein analyst Stacy Rasgon told Axios, summarising the sentiment shared by every hyperscaler CTO.

## What This Means for Indian Engineers

Meta's workforce includes thousands of Indian engineers spread across its AI research, infrastructure, and — increasingly — silicon design teams. The Iris programme is creating an entirely new career vertical within the company: one that values hardware architecture, ASIC design, chip verification, and semiconductor process expertise alongside the software skills that have historically defined Big Tech hiring.

This matters for the Indian professional pipeline in two directions.

**In the U.S.**: Indian engineers at Meta, many on H-1B visas, now have a lateral career path into chip design that did not exist three years ago. The skills required — VLSI design, RTL verification, physical design — overlap heavily with the training that IIT and BITS graduates receive, making Indian engineers disproportionately well-positioned for this shift. Broadcom, which is co-designing Iris, already employs a significant Indian-origin engineering workforce.

**In India**: Meta's custom chip ambitions inevitably pull from the same talent pool that feeds India's semiconductor industry push. The India Semiconductor Mission, Tata Electronics' Dholera fab, and Micron's Gujarat facility are all competing for the same chip design engineers. Meta's Hyderabad and Bangalore offices have been expanding their silicon-adjacent teams, and a production-ready chip programme only accelerates that hiring.

For Indian semiconductor professionals, the message from 2026 is unmistakable: every major technology company now wants to be a chip company. The career ceiling for hardware engineers just rose considerably.

## The Investor Angle

Meta's stock initially fell on the 14-gigawatt spending disclosure but recovered sharply after the company announced developer access to its AI coding model, pitting it against OpenAI and Anthropic. Shares closed up 4.6 percent on the day.

The Iris announcement eases one of the market's core anxieties about Meta: that its AI spending is a black hole with no marginal cost improvement in sight. A working custom chip — produced at TSMC's massive scale — is the most tangible evidence yet that Zuckerberg's $145-billion-a-year AI infrastructure bet will eventually produce structural cost advantages, not just better recommendation algorithms.

For NRI investors watching Meta's stock trade more than 20 percent below its August highs, the chip programme adds a new dimension to the thesis. Meta is no longer just a social media company spending aggressively on AI. It is becoming a vertically integrated technology platform — one that designs its own chips, trains its own models, and may soon sell its excess computing capacity to other companies.

That is a fundamentally different business than the one Indian engineers joined five years ago. And it is one that could define the next decade of careers in Silicon Valley and Hyderabad alike."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
