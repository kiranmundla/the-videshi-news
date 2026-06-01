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

def verify_image(url):
    """Check that an image URL returns a valid image > 5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" in ct and cl > 5000:
            return True
        # HEAD might not return Content-Length, try GET
        if "image" in ct:
            r2 = requests.get(url, timeout=10, stream=True,
                              headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
    except Exception as e:
        print(f"  Image check failed for {url}: {e}")
    return False

# ─── ARTICLE 1 ───────────────────────────────────────────────────────────────

art1_image = "https://upload.wikimedia.org/wikipedia/commons/6/6e/Cristiano_Amon_%28President_%26_CEOQualcomm%29_%2854916855494%29_%28cropped%29.jpg"
if not verify_image(art1_image):
    print("⚠️  Art1 image failed verification, using anyway (Wikimedia)")

art1_body = """Qualcomm's stock dropped 7.5 per cent in pre-market trading on Monday morning. The trigger was not an earnings miss or a product recall. It was a keynote speech by another company's CEO, delivered 8,000 miles away in Taipei.

Jensen Huang's unveiling of the RTX Spark superchip at Computex marked Nvidia's formal entry into the Windows PC processor market — a space Qualcomm had spent years cultivating almost entirely alone. The San Diego chipmaker's Snapdragon X series had been the sole credible Arm-based alternative to Intel and AMD inside Windows laptops. That exclusivity ended on a Monday morning in Taiwan.

## The Scale of the Challenge

The numbers frame the problem starkly. Nvidia closed fiscal 2026 with revenue of $215.9 billion, up 65 per cent year over year. Qualcomm's annual revenue sits around $39 billion. The company entering Qualcomm's newest market has five times its resources and, crucially, a software moat — CUDA, RTX, DLSS — that Qualcomm never built for PCs.

RTX Spark combines a 20-core Arm CPU (co-designed with Taiwan's MediaTek) with Nvidia's Blackwell GPU architecture, delivering what Nvidia claims is 1 petaflop of AI performance and up to 128GB of unified memory. Laptops from Dell, Lenovo, HP, Asus, Microsoft Surface, and MSI will ship this autumn. Over 100 software providers and game studios have already committed support.

Qualcomm's Snapdragon X chips, by contrast, still struggle with app compatibility gaps. The developer ecosystem Qualcomm painstakingly assembled over three years could now benefit a rival with deeper pockets and broader software reach.

## "Welcome to the Family"

Qualcomm's public response was notably relaxed. Kedar Kondap, Senior Vice President overseeing compute and gaming, told reporters: "Welcome to the family." The framing was deliberate — more players entering Arm-based Windows validates the ecosystem Qualcomm pioneered, rather than fragmenting it.

There is logic to this. A larger Arm-on-Windows market means more developers building native Arm applications, which helps every Arm chipmaker, including Qualcomm. The alternative — remaining the only Arm option in a market still dominated by x86 — was not producing transformative market share gains anyway.

Qualcomm also signalled where it intends to compete. Its newly announced Snapdragon C platform targets budget Windows laptops starting around $300, positioned against Apple's $600 MacBook Neo. Nvidia's RTX Spark will debut in premium machines likely priced above $1,500. The segmentation may prove workable.

## What This Means for Indian Engineers in San Diego

Qualcomm's San Diego headquarters and engineering centres employ thousands of Indian-origin engineers, many on H-1B visas. The company's R&D operations in Hyderabad and Bangalore add tens of thousands more. For this workforce, Nvidia's entry creates both pressure and opportunity.

The pressure is straightforward: if Qualcomm's PC chip division loses momentum, teams working on Snapdragon compute products face uncertain headcount decisions. H-1B holders at Qualcomm's San Diego campus have the added constraint of a 60-day grace period if positions are eliminated — a timeline that concentrates minds.

The opportunity is subtler. A growing Arm-on-Windows ecosystem means more jobs across the semiconductor industry building Arm-compatible software, drivers, and system-level integrations. Engineers with experience in Arm architecture — which Qualcomm's workforce has in abundance — become more valuable, not less, as the market expands.

For NRI investors holding QCOM, the 7.5 per cent pre-market drop may have already priced in the competitive shock. Qualcomm's smartphone modem business, its largest revenue driver, remains untouched by Nvidia's PC ambitions. The real question is whether Snapdragon C can hold the budget tier while Nvidia takes the premium end — or whether Nvidia's ecosystem gravity pulls the entire Windows-on-Arm market toward Santa Clara.

The Arm PC war just gained a combatant with a $5.1 trillion market cap. Qualcomm's next twelve months will determine whether "welcome to the family" was confidence or whistling past the graveyard."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Qualcomm Dropped 7.5% the Morning Nvidia Entered Its Market. Twenty Thousand Indian Engineers Are Watching.",
    "subheadline": "Nvidia's RTX Spark superchip turned Computex into a reckoning for Qualcomm's Arm PC ambitions — and for the massive Indian workforce in San Diego that built them.",
    "slug": make_slug("qualcomm-nvidia-rtx-spark-arm-pc-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Qualcomm's San Diego HQ and India R&D centres employ tens of thousands of Indian-origin engineers, many on H-1B visas. Nvidia's entry into the Windows-on-Arm market directly threatens Qualcomm's PC chip division, creating workforce uncertainty for H-1B holders with 60-day grace period constraints. NRI investors in QCOM face a repricing event.",
    "tags": ["qualcomm", "nvidia", "arm-pc", "h1b", "semiconductor", "computex"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-launches-new-chip-bring-ai-directly-personal-computers-2026-06-01/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/intel-and-amd-shares-fall-more-than-nvidia-rises-on-new-pc-superchip"},
        {"name": "UnderCode News", "url": "https://undercodenews.com/welcome-to-the-family-qualcomm-shrugs-at-nvidias-entry-into-the-arm-pc-war-with-rtx-spark/"},
        {"name": "CoinCentral", "url": "https://coincentral.com/nvidia-rtx-spark-chip-explained/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": art1_image,
    "is_editorial": False,
    "body": art1_body
}

# ─── ARTICLE 2 ───────────────────────────────────────────────────────────────

art2_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg/1280px-SXSW-2024-alih-OB7A0861-Lisa_Su_%28cropped_2%29.jpg"
if not verify_image(art2_image):
    print("⚠️  Art2 image failed verification, using anyway (Wikimedia)")

art2_body = """Advanced Micro Devices has begun ramping production of Venice, its next-generation EPYC server processor, on TSMC's 2-nanometre process technology. It is the first high-performance computing chip in the industry to enter production at this node — a milestone that matters far beyond the data centre.

AMD announced on 21 May that Venice had entered production ramp at TSMC's facilities in Taiwan, with plans to expand manufacturing to TSMC's Arizona fab. A follow-on chip called Verano, integrating LPDDR memory for AI workloads, is already in the pipeline.

## Why 2nm Matters

Every new process node represents a step change in transistor density, power efficiency, and performance. At 2nm, TSMC can pack more compute into less silicon while drawing less electricity — a critical advantage as AI data centres consume staggering amounts of power.

For AMD, Venice represents the sharpest weapon yet in its decade-long war against Intel's server dominance. EPYC processors have steadily gained market share in cloud data centres, and Venice on 2nm should widen AMD's performance-per-watt advantage over Intel's current offerings, which remain on older process nodes.

The timing is pointed. On the same day Venice entered production ramp, Nvidia was preparing to launch the Vera Rubin, its next-generation data centre GPU — and Intel was watching its stock drop 5 per cent on Nvidia's PC chip announcement. The server chip market is a three-front war, and AMD just upgraded its arsenal.

## The Stock Story NRI Investors Should Understand

AMD's stock has gained roughly 125 per cent year-to-date, making it one of the best-performing semiconductor names in 2026. The rally reflects both the Venice milestone and AMD's broader positioning across AI inference, gaming GPUs, and adaptive computing.

For NRI investors with exposure to US tech through direct holdings, 401(k) plans, or index funds, AMD's run matters. The stock sits in every major semiconductor ETF and in the S&P 500. Understanding why it moved — and whether the rally has further room — requires understanding what 2nm production actually unlocks.

Venice targets the hyperscale cloud operators — Amazon Web Services, Microsoft Azure, Google Cloud — that are spending hundreds of billions on AI infrastructure. These companies care about two things above all: performance per dollar and performance per watt. A 2nm EPYC processor that delivers both puts AMD in a position to take further share from Intel's Xeon line, which still dominates by installed base but trails on process technology.

## The Arizona Connection

AMD plans to manufacture Venice at TSMC's Arizona facility, part of the US government's CHIPS Act push to reshore semiconductor production. The Arizona fab employs a growing number of Indian-origin engineers — TSMC has recruited heavily from India's IITs and semiconductor programmes to staff its US operations.

For the Indian semiconductor diaspora, the Arizona fabs represent a new career pathway that did not exist five years ago. Engineers who might have worked exclusively in design roles at AMD, Intel, or Qualcomm now have manufacturing and process engineering options on American soil. The US semiconductor workforce is becoming visibly more Indian, and AMD's 2nm production ramp accelerates that trend.

## What Comes Next

AMD CEO Lisa Su has built her tenure on a disciplined cadence: announce a roadmap, hit the milestones, take share. Venice follows the pattern. The Verano follow-on, with LPDDR memory integration tailored for AI workloads, suggests AMD sees inference — running trained AI models — as the next growth pocket in servers.

The competitive picture is evolving rapidly. Nvidia dominates AI training with its GPUs but is increasingly pushing into CPUs with the Vera line. Intel is restructuring under CEO Lip-Bu Tan, cutting over 20 per cent of its workforce while trying to modernise its foundry. AMD occupies the middle ground: large enough to compete on both fronts, nimble enough to ride TSMC's leading edge.

Venice at 2nm is not just a chip announcement. It is AMD's declaration that the company intends to lead the next generation of data centre computing — and NRI investors who have ridden the 125 per cent rally should understand exactly what they own."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "AMD Just Put the First 2nm Server Chip Into Production. Its Stock Has Doubled This Year.",
    "subheadline": "Venice, AMD's next-generation EPYC processor built on TSMC's most advanced process, marks a milestone in the data centre wars — and a turning point for NRI investors tracking the semiconductor rally.",
    "slug": make_slug("amd-venice-2nm-epyc-tsmc-nri-investors"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "AMD's 125% YTD stock rally directly affects NRI investors with US tech exposure through direct holdings, 401(k)s, and index funds. TSMC's Arizona fab, where Venice will also be manufactured, is recruiting heavily from India's IITs. The Indian semiconductor diaspora is gaining new career pathways in US-based chip manufacturing.",
    "tags": ["amd", "semiconductor", "tsmc", "2nm", "data-center", "nri-investors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/advanced-micro-devices-inc-amd-starts-venice-epyc-processor-production-ramp-1519875/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-29/"},
        {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260530PD224/amd-2nm-samsung-tsmc.html"}
    ]),
    "score_total": 76,
    "status": "published",
    "published_at": now,
    "image_url": art2_image,
    "is_editorial": False,
    "body": art2_body
}

# ─── ARTICLE 3 ───────────────────────────────────────────────────────────────

art3_image = "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
if not verify_image(art3_image):
    print("⚠️  Art3 image failed verification")
    art3_image = "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"

art3_body = """On Monday, Nvidia announced that TSMC — the foundry that manufactures nearly every advanced AI chip on the planet — is deploying Nvidia's accelerated computing and AI systems inside its own fabrication facilities. The partnership, revealed at GTC Taipei on 1 June, means the company that makes AI chips is now using AI to make AI chips. The recursion is not accidental.

## What TSMC Is Actually Doing

TSMC has integrated Nvidia's CUDA-X libraries and Blackwell GPU architecture across four critical manufacturing stages: computational lithography, transistor simulation, advanced process control, and wafer inspection.

The most significant deployment is cuLitho, Nvidia's computational lithography platform. Lithography — the process of etching circuit patterns onto silicon wafers using light — is the single most compute-intensive step in chip manufacturing. At 2nm and below, the calculations required to account for how light bends around nanometre-scale features are so immense that traditional CPU-based methods have become a bottleneck.

TSMC reports that cuLitho accelerates lithography workflows by 25 times compared to conventional approaches. A generative AI layer adds another 2x improvement on top. Combined, this reduces what was once a multi-day computation to hours.

Beyond lithography, Nvidia's vision AI tools — Metropolis and TAO Toolkit — are being used for automated defect inspection, detecting flaws at the nanometre scale that human operators and older machine-vision systems would miss.

## Why This Matters for India's Semiconductor Ambitions

India's semiconductor mission is no longer aspirational — it is operational. Micron's assembly and test facility in Sanand, Gujarat, began commercial production in February 2026. Tata Electronics is building a fabrication plant in Dholera with ASML equipment. Intel announced a $3.3 billion substrate packaging facility in Odisha. C2i Semiconductors just taped out India's first homegrown AI power chip.

But assembly, testing, and packaging are the simpler end of the semiconductor value chain. Fabrication — actually making chips on wafers — is where the extreme complexity lives, and where AI-assisted manufacturing will determine which fabs succeed and which become expensive monuments to ambition.

The TSMC-Nvidia partnership sets the technology bar that Indian fabs must eventually meet. Tata's Dholera facility, when it reaches volume production, will face the same lithography bottlenecks, the same defect detection challenges, and the same process control requirements that TSMC addresses with Nvidia's AI. Whether India develops or licenses equivalent AI manufacturing tools will shape the competitiveness of its entire semiconductor ecosystem.

## The Indian Engineering Talent Pipeline

There is a second diaspora angle, less obvious but arguably more consequential. TSMC's Arizona fabs have been recruiting Indian engineers at scale — IIT graduates, semiconductor programme alumni, and experienced process engineers from Intel and Samsung. These engineers are learning to operate the world's most advanced fabs.

When India's own fabrication facilities reach more advanced nodes, the engineers who return from TSMC Arizona, Intel Oregon, Samsung Austin, and Micron Boise will carry institutional knowledge that cannot be taught in classrooms. The TSMC-Nvidia AI manufacturing toolkit is part of that knowledge base.

C.C. Wei, TSMC's chairman and CEO, framed the partnership as foundational: "By using Nvidia accelerated computing and AI across fab operations, TSMC is strengthening our technology leadership and manufacturing excellence." For Indian semiconductor planners watching from New Delhi, the message is that building fabs is necessary but not sufficient. Making them intelligent is what separates functional facilities from world-class ones.

## The Broader Competitive Picture

The announcement also sharpens the divide between TSMC and its rivals. Samsung Foundry, which is preparing its $17 billion Taylor, Texas fab for 2nm production starting in 2027, has not disclosed comparable AI manufacturing partnerships. Intel Foundry, under restructuring, faces the same challenge.

For NRI investors and Indian semiconductor professionals, the TSMC-Nvidia deepening signals that the AI chip supply chain is becoming self-reinforcing: Nvidia's AI makes TSMC's fabs better, TSMC's fabs make Nvidia's chips faster, and the cycle accelerates. Breaking into this loop — as India hopes to do — requires not just capital and equipment, but the AI infrastructure to operate at the frontier."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA and TSMC Are Now Using AI to Make AI Chips. India's Fabs Should Be Taking Notes.",
    "subheadline": "TSMC has deployed Nvidia's CUDA and AI systems inside its own fabrication lines, accelerating lithography by 25x. For India's nascent semiconductor mission, this sets the technology bar.",
    "slug": make_slug("nvidia-tsmc-ai-chip-manufacturing-india-fabs"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India's semiconductor mission — Micron Sanand, Tata Dholera, Intel Odisha — must eventually match the AI-assisted manufacturing capabilities TSMC is deploying. Indian engineers at TSMC Arizona are learning these systems firsthand. The diaspora talent pipeline between US fabs and India's future facilities is a critical knowledge transfer channel.",
    "tags": ["tsmc", "nvidia", "semiconductor-manufacturing", "india-semiconductor", "ai-fabs", "computex"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "GlobeNewsWire / Nvidia", "url": "https://www.globenewswire.com/news-release/2026/06/01/3033486/0/en/NVIDIA-and-TSMC-Bring-AI-Into-Fabs-to-Advance-Semiconductor.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-29/"},
        {"name": "Nvidia Stock Titan", "url": "https://stocktitan.net/press-releases/NVDA/nvidia-tsmc-ai-semiconductor-fabs/"}
    ]),
    "score_total": 74,
    "status": "published",
    "published_at": now,
    "image_url": art3_image,
    "is_editorial": False,
    "body": art3_body
}

# ─── INSERT ──────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
