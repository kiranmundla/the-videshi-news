#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-30 18:00 UTC batch"""

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

# ── Validate images before using ──
def validate_image(url):
    """Return True if URL returns an image with Content-Length > 5000."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False

# ── Image URLs ──
img_datacenter = "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img_chip = "https://images.pexels.com/photos/163170/board-printed-circuit-board-computer-electronics-163170.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img_memory = "https://images.pexels.com/photos/6636474/pexels-photo-6636474.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

# Validate all images
for label, url in [("datacenter", img_datacenter), ("chip", img_chip), ("memory", img_memory)]:
    if not validate_image(url):
        print(f"⚠️  Image validation failed for {label}: {url}")

articles = [
    # ════════════════════════════════════════════════════════════════════
    # ARTICLE 1: ByteDance Custom CPUs
    # ════════════════════════════════════════════════════════════════════
    {
        "id": str(uuid.uuid4()),
        "headline": "ByteDance Is Building Its Own CPUs. That's a Job Listing for Ten Thousand Indian Chip Designers.",
        "subheadline": "The TikTok parent is designing custom data-centre processors on Arm and RISC-V as Intel and AMD raise server chip prices by up to 35 per cent a quarter. The global custom-silicon rush is creating a talent vacuum that India is uniquely positioned to fill.",
        "slug": make_slug("bytedance-custom-cpu-arm-riscv-indian-chip-design"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian chip designers at Intel, AMD, Qualcomm, Arm, and RISC-V startups are the direct beneficiaries of the custom-silicon boom. As every hyperscaler — Google, Amazon, Microsoft, and now ByteDance — builds in-house processors, demand for verification engineers, RTL designers, and physical design specialists (roles where Indians dominate globally) is surging. RISC-V's open-source model also aligns with India's semiconductor mission: IITs have been running RISC-V curriculum programmes, and Bengaluru is already a RISC-V design hub.",
        "tags": ["bytedance", "cpu", "arm", "risc-v", "chip-design", "indian-engineers", "semiconductor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/bytedance-developing-custom-cpu-chips-support-ai-rollout-sources-say-2026-05-28/"},
            {"name": "TrendForce", "url": "https://www.trendforce.com/news/2026/05/28/bytedance-reportedly-explores-arm-and-risc-v-paths-for-in-house-cpus/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-computex-taiwan-stock-catalyst-2026-05-30"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": img_datacenter,
        "body": """ByteDance, the Beijing-based parent of TikTok that spent roughly $29 billion on AI infrastructure this year, is designing its own data-centre central processing units. Reuters reported the programme on Thursday, citing people with direct knowledge of the project.

The company is running two parallel architecture tracks — one on Arm, the proven server-chip instruction set behind Amazon's Graviton, Microsoft's Cobalt, and Google's Axion, and another on RISC-V, the open-source alternative that carries no licensing fees and no Western export-control exposure. ByteDance plans to evaluate both before committing to a large-scale manufacturing run.

## The economics are brutal

The trigger is price. Intel and AMD, ByteDance's current CPU suppliers, have raised server-chip prices by 10 to 35 per cent quarter over quarter in recent months, Reuters reported. Intel has warned Chinese customers of delivery lead times stretching to six months. AMD CEO Lisa Su said last week that the global CPU market is "tight," with demand outpacing forecasts.

ByteDance's 2026 AI-infrastructure budget reportedly grew 25 per cent to roughly 200 billion yuan ($29.4 billion). At that spending level, even single-digit percentage savings on CPU procurement translate into hundreds of millions of dollars.

The shift also reflects a structural change in AI workloads. As more AI moves from training (GPU-intensive) to inference (running models for real users), CPUs play a larger coordinating role — managing data flow, orchestrating agent calls, and handling the non-matrix-math work that GPUs ignore. Agentic AI, in particular, is a CPU-hungry paradigm. Uber blew through its entire 2026 AI budget by March, largely on token costs from agentic workflows that chain dozens of model calls per user prompt.

## The custom-silicon club keeps growing

ByteDance joins a roster that now reads like a who's who of global tech. Amazon has Graviton (fourth generation shipping). Google has Axion. Microsoft has Cobalt. Apple has been designing its own chips for years. Nvidia, not content with dominating GPUs, is pushing its Vera CPU line into a market CEO Jensen Huang pegs at $200 billion.

Each of these programmes needs thousands of chip designers — verification engineers, RTL architects, physical design specialists, firmware developers. The talent pool for this work is deep but finite, and a disproportionate share of it is Indian.

## Why Indian engineers should pay attention

India produces more chip-design engineers per year than any country outside the United States and China. Bengaluru alone hosts design centres for Intel, Qualcomm, AMD, Arm, Samsung, Texas Instruments, and a growing cluster of RISC-V startups. IIT Madras runs one of the world's leading RISC-V research programmes. The India Semiconductor Mission has given 270 universities access to advanced chip-design tools, logging 1.2 million student design hours in 2025 alone.

The custom-silicon boom is already tightening the market. Experienced verification engineers in the Bay Area are commanding $250,000-plus packages. In Bengaluru, senior chip-design salaries have risen 20 to 30 per cent in the past 18 months, according to industry recruiters.

For NRI engineers at Intel or Qualcomm weighing their next move, the signal is clear: the companies building the largest AI infrastructure on earth — from Cupertino to Beijing — all want to own their silicon. The question is no longer whether custom chips are worth the complexity. It is whether your team can tape one out fast enough.

ByteDance's dual-track Arm-and-RISC-V bet also carries a geopolitical edge. RISC-V sidesteps the licensing and export-control dependencies that come with Arm's UK-headquartered, SoftBank-owned IP — a consideration that matters increasingly as US-China tech decoupling deepens. For Indian engineers skilled in RISC-V, that geopolitical friction is, perversely, a career tailwind: both sides of the divide want what they can design."""
    },

    # ════════════════════════════════════════════════════════════════════
    # ARTICLE 2: C2i Semiconductors AI Power Chip Tapeout
    # ════════════════════════════════════════════════════════════════════
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bengaluru Startup Just Taped Out India's First AI Power Chip. It Took Eleven Months.",
        "subheadline": "C2i Semiconductors, backed by Peak XV Partners and TDK Ventures, has sent a smart power-stage chip for AI data centres to fabrication — designed end-to-end in India by an Indian engineering team. For the country's semiconductor ambitions, it is a small chip with outsized symbolism.",
        "slug": make_slug("c2i-semiconductors-india-ai-power-chip-tapeout"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRI semiconductor engineers at Texas Instruments, Analog Devices, Infineon, or ON Semiconductor, C2i's tapeout is a signal that India's chip ecosystem has moved beyond design services into original product development. The startup was founded in June 2024 and taped out in May 2026 — a pace that would be aggressive anywhere. Peak XV (formerly Sequoia India) and TDK Ventures backing a power-semiconductor play suggests that institutional capital now sees India as a viable location for chip-product companies, not just chip-service shops. For engineers considering a return-to-India move, the calculus just shifted.",
        "tags": ["c2i-semiconductors", "india-semiconductor", "chip-design", "ai-infrastructure", "power-management", "peak-xv", "deep-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/c2i-semiconductor-tapes-out-ai-power-chip-signalling-indias-push-into-advanced-chip-design/article69632000.ece"},
            {"name": "Entrepreneur India", "url": "https://www.entrepreneur.com/en-in/news-and-trends/c2i-semiconductors-extends-series-a-round-to-usd-167-mn/492000"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/corporate/c2i-semiconductor-tapes-out-ai-power-chip-signalling-indias-push-into-advanced-chip-design"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": img_chip,
        "body": """India has been talking about making chips for a decade. On Thursday, a Bengaluru startup demonstrated it can actually design one.

C2i Semiconductors announced the tapeout of a smart power-stage chip engineered specifically for AI data-centre infrastructure. Tapeout — the stage where a finalised chip design is sent to a foundry for fabrication — is the semiconductor industry's equivalent of pressing "publish." It means the design has passed verification, timing closure, and physical design review. It is ready to become silicon.

The chip was conceived, architected, and verified entirely in India by C2i's in-house engineering team. That distinction matters. India has hosted chip-design centres for decades — Intel's Bengaluru campus alone employs thousands of engineers who contribute to global processor programmes. But those engineers design *for* Intel, *inside* Intel's IP framework. C2i's chip is an Indian company's own product, built on its own intellectual property, aimed at its own customers.

## What the chip actually does

C2i's power-stage chip regulates and optimises power delivery across AI data-centre infrastructure. This is not the glamorous end of the semiconductor stack — no one writes breathless headlines about voltage regulators — but it is arguably the most critical bottleneck in the AI buildout.

A single Nvidia Vera Rubin AI server consumes the power equivalent of 14,500 laptops' worth of memory chips alone. At rack scale, AI data centres are pushing electrical grids to breaking point. The companies building these facilities — Microsoft, Google, Meta, Amazon — need every watt managed with precision. Power delivery, conversion, and thermal management are where billions of dollars of efficiency gains hide.

C2i's platform includes what it calls the Manas Controller, a software-defined power management system, and the Sarayu Power Stage, designed for modular scalability across different processor and power-delivery architectures. The names — drawn from Sanskrit — are a quiet assertion of origin.

## The money trail

The startup extended its Series A to $16.7 million this week, with TDK Ventures participating in both the initial round and the extension. Peak XV Partners (formerly Sequoia India) led the original tranche in February. Yali Deeptech, an Indian deep-tech venture fund, was also in.

C2i was founded in June 2024 by six engineers: Ram Anant, Vikram Gakhar, Preetam Tadeparthy, Dattatreya Suryanarayana, Harsha S B, and Muthusubramanian N V. Tapeout in under eleven months is a pace that semiconductor veterans will recognise as unusual. Typical analogue mixed-signal tapeouts take 18 to 24 months at established companies.

## What it means for the semiconductor mission

Amitesh Sinha, chief executive of the India Semiconductor Mission and additional secretary at the Ministry of Electronics and IT, called the tapeout "a powerful demonstration that Indian innovation can extend across the technology stack, from the power grid to the chip level."

The DLI (Design Linked Incentive) Scheme, India's programme for supporting chip-design startups, has backed 24 projects and 105 companies with advanced design tools. C2i is among the first to convert that support into a physical tapeout.

For context, India's semiconductor story to date has been about fabrication: Tata Electronics building a fab in Dholera with PSMC, Micron assembling memory chips in Sanand, Intel announcing a $3.3 billion substrate plant in Odisha. These are essential — but they are manufacturing stories. C2i represents something different: an Indian company creating original chip IP for a global market.

## The NRI calculus

For the estimated 50,000 Indian-origin semiconductor engineers working in the United States — at Texas Instruments in Dallas, Analog Devices in Wilmington, Infineon in San Jose, ON Semiconductor in Scottsdale — C2i's trajectory reframes the return-to-India conversation.

The question has always been: can I do world-class chip design in India, on Indian IP, for global customers? For most of the past two decades, the honest answer was no. The ecosystem lacked the venture capital, the foundry relationships, and the product-company culture to support it. Peak XV and TDK writing cheques for a power-semiconductor startup suggests that constraint is loosening.

C2i says it is engaging customers and partners in India and overseas. If the fabricated chip performs to spec — the step that separates tapeout from product — it will be among the first AI-infrastructure semiconductors designed and brought to market by an Indian company. The chip is small. The signal is not."""
    },

    # ════════════════════════════════════════════════════════════════════
    # ARTICLE 3: Memory Shortage Consumer Impact
    # ════════════════════════════════════════════════════════════════════
    {
        "id": str(uuid.uuid4()),
        "headline": "AI Servers Are Eating the World's Memory Chips. Your Next Phone Will Cost $100 More.",
        "subheadline": "DDR5 spot prices have doubled since November. Android phone sales are expected to drop 14 per cent this year — the steepest decline ever recorded. The culprit: AI data centres are hoovering up every memory chip Micron, SK Hynix, and Samsung can produce.",
        "slug": make_slug("memory-chip-shortage-smartphone-prices-ai-servers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRIs routinely buy phones for family in India, and the Indian smartphone market is acutely price-sensitive below $200 — exactly the tier being crushed by memory inflation. For NRI investors, the memory shortage explains Micron's surge past $1 trillion (led by Indian-origin CEO Sanjay Mehrotra). And Micron's $2.75 billion assembly plant in Sanand, Gujarat, is part of the industry's long-term supply response — but it won't ease the current crunch, which has no relief until mid-2027.",
        "tags": ["memory-chips", "smartphone", "ddr5", "micron", "sk-hynix", "samsung", "ai-infrastructure", "consumer-impact"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/articles/memory-shortage-smartphones-ai-consumer-prices-2026-05-30"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/stocks/chip-rally-semiconductor-stocks-nvidia-amd-2026-05-29"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-29/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": img_memory,
        "body": """The numbers are startling even by the standards of a semiconductor cycle that has defied every historical pattern.

Daily spot rates for DDR5 — the type of memory chip used in everything from gaming PCs to AI servers — have more than doubled since November, rising to $22.50 per unit, according to semiconductor pricing firm Ornn. The average selling price of a smartphone climbed $100 year-over-year to $550. Android phone unit sales are projected to fall 14 per cent in 2026, the steepest decline IDC has ever recorded.

The cause is not a manufacturing defect or a natural disaster. It is artificial intelligence.

## The arithmetic of scarcity

One Nvidia Vera Rubin AI server — the next-generation system shipping later this year — uses the memory equivalent of approximately 14,500 MacBook Neos. A single hyperscale data centre might deploy thousands of these servers. Microsoft, Google, Meta, and Amazon are building dozens of such facilities simultaneously.

The three companies that manufacture nearly all of the world's memory chips — Micron Technology (led by Indian-origin CEO Sanjay Mehrotra), SK Hynix of South Korea, and Samsung Electronics — do not have significant new manufacturing capacity coming online until mid-2027. All of 2026's supply is already spoken for. Order books for 2027 are filling fast.

"For consumers, it means the era of ultracheap smartphones is over," Nabila Popal of IDC said in a research note. "For vendors, it means only those that can adapt their strategies to this new cost environment and sustain demand at elevated price points will survive."

## High-bandwidth memory is the bottleneck

The tightest segment is High Bandwidth Memory (HBM), the stacked memory chips that sit directly on top of AI processors to feed them data at extreme speeds. HBM is manufactured by SK Hynix, Samsung, and Micron using specialised stacking and bonding techniques that cannot be easily retrofitted from standard DRAM production lines.

Nvidia's latest GPUs each require multiple HBM stacks. The company is expected to surpass Apple this year as TSMC's largest single customer — and the memory paired with each GPU is orders of magnitude more than what goes into any consumer device.

The pricing mechanism is straightforward: memory fabs are allocating capacity to the highest-margin products first. HBM for AI servers commands premium pricing that consumer DRAM and NAND flash cannot match. Phone makers, PC manufacturers, and gaming console producers are left competing for whatever remains.

## The Indian consumer squeeze

The impact is particularly acute in India, which is the world's second-largest smartphone market by volume but acutely price-sensitive. The sub-$200 segment — where brands like Xiaomi, Realme, Vivo, and Samsung's Galaxy A series compete for hundreds of millions of buyers — is the most exposed to memory-cost inflation.

For NRIs who routinely purchase phones for family in India, the sticker shock is already visible. A Redmi or Realme device that cost ₹12,000 a year ago may now be ₹15,000 or more for equivalent specifications, or ship with less RAM and storage at the old price.

Indian OEMs have limited leverage. Unlike Apple, which can use its purchasing scale to secure supply and absorb cost increases into its margins, Indian-market brands operate on razor-thin margins and cannot easily pass through a $100-per-unit memory cost increase to buyers spending $150 on a phone.

## Micron's Gujarat plant is part of the answer — eventually

Micron's $2.75 billion assembly, testing, marking, and packaging (ATMP) facility in Sanand, Gujarat, has moved into commercial production. The plant produces high-density DRAM and NAND flash modules optimised for enterprise AI servers — precisely the products commanding the highest margins.

The facility is part of India's broader semiconductor push, but it is not a demand-side relief valve for the current shortage. ATMP plants assemble and test chips; they do not fabricate the underlying silicon. Wafer production remains concentrated in South Korea, Japan, and Taiwan, where capacity additions require years of construction and billions of dollars of capital.

## What NRI investors should understand

The memory shortage explains the extraordinary stock performance of Micron, which crossed $1 trillion in market capitalisation this week. The company's shares have risen roughly tenfold from their 52-week low of $92 as AI demand sent earnings estimates soaring.

But memory is cyclical — historically the most cyclical segment of the semiconductor industry. The current supply-demand imbalance is real and will persist through at least mid-2027. Beyond that, the calculus changes. SK Hynix is building a massive new facility in Yongin, South Korea. Samsung is expanding its Pyeongtaek campus. Micron is adding capacity in Hiroshima and Boise.

The hourly cost to rent an Nvidia B200 GPU has nearly doubled in three months, from $2.66 to $5.27, per Ornn data. When that rental rate eventually falls — because capacity catches up, or because AI workload growth moderates — memory pricing will follow. Cycles always turn.

For now, though, the physics are inescapable: AI's appetite for memory is insatiable, the supply response is years away, and your next phone will be more expensive because of it."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
