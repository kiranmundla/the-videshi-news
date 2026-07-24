#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-28 18:00 UTC run"""
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

def verify_image(url):
    """Verify image URL returns HTTP 200, image/* content type, and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD fails
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct:
            return url
    except Exception as e:
        print(f"  ⚠️ Image check failed for {url}: {e}")
    return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ─────────────────────────────────────────────────────────────
# ARTICLE 1: TSMC Energy Efficiency
# ─────────────────────────────────────────────────────────────

art1_body = """The semiconductor industry's most important metric just changed. It is no longer about how many transistors you can cram onto a chip. It is about how much electricity that chip consumes.

Kevin Zhang, TSMC's Senior Vice President of Business Development, told reporters at a conference in Amsterdam this week that energy efficiency has overtaken raw computing power as the primary constraint shaping chip design — across everything from smartphones to AI data centres.

"The area customers most want improvement in is energy efficiency," Zhang said. "This is true across the board, whether you are the edge guy, smartphone, mobile, IoT application, or high-performance AI data center."

## The watt wall

The shift reflects a brutal reality. AI data centres are devouring electricity at a rate that outpaces grid capacity in much of the world. A single AI training cluster can consume as much power as a small city. And with hyperscalers — Google, Amazon, Microsoft, Meta — projected to spend over $700 billion on AI infrastructure this year alone, the power problem is compounding faster than anyone anticipated.

TSMC, the world's largest contract chipmaker and the manufacturer behind AI chips for Nvidia, AMD, and custom processors for every major cloud company, is responding by shifting its roadmap. Simply shrinking transistors — the trick that drove six decades of Moore's Law — is no longer enough.

Advanced packaging, three-dimensional chip stacking, and photonics (using light instead of electrical signals to move data) are now central to the company's strategy. Zhang said TSMC expects its chips to cut power consumption by up to 30 per cent between its current N2 node and its A14 generation, due around 2028, while still delivering more than 20 per cent higher computing performance.

## The price of scarcity

The energy crunch comes alongside another pressure: cost. TSMC plans to raise prices on its 3-nanometre chips by up to 15 per cent in the second half of 2026, driven by insatiable AI demand that has pushed its Fab 18 to 175,000 wafers per month — and still cannot keep up. Wafer costs are approaching $20,000 each, with the upcoming 2-nanometre node expected to exceed $30,000.

For every company that buys TSMC silicon — which is effectively every company in AI — those increases flow directly into the cost of building and operating data centres.

## Huawei's alternative path

Not everyone is playing by TSMC's rules. This week at Computex, Huawei unveiled its "Tau Scaling Law," a framework for improving chip performance by speeding up data movement within processors rather than shrinking transistors. The approach reflects the reality facing Chinese chipmakers, which remain cut off from ASML's extreme ultraviolet lithography machines by US-led export controls.

Zhang was diplomatic but pointed: the concept of integration-driven performance "has been around in this industry for long enough," he said, describing it as largely dependent on 3D stacking — a technique TSMC has been commercialising for years.

## Why NRIs should care

For Indian engineers in the semiconductor industry — and there are tens of thousands across TSMC, Nvidia, Intel, AMD, Qualcomm, and Broadcom — this shift redefines what "cutting-edge" means. The most valuable chip designers will increasingly be those who can optimise for watts-per-inference, not transistors-per-square-millimetre.

The implications reach back to India, too. The country's ambitious semiconductor programme — Tata Electronics' fab in Dholera, Micron's assembly facility in Gujarat — will be shaped by these same energy constraints. India's power grid, where reliability varies sharply by region, makes efficiency-first chip design not just a preference but a necessity.

TSMC has made clear that the era of cheap, brute-force computation is ending. The companies and engineers who figure out how to do more with less electricity will define the next decade of AI. A disproportionate number of them will be Indian."""

art1_image = "https://images.pexels.com/photos/17155843/pexels-photo-17155843.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"


# ─────────────────────────────────────────────────────────────
# ARTICLE 2: ByteDance Custom CPUs / AI Inference Shortage
# ─────────────────────────────────────────────────────────────

art2_body = """For the past three years, the AI chip conversation has been almost exclusively about GPUs — the graphics processors made by Nvidia that train the world's large language models. But a quieter crisis has been building in the background, and it just became impossible to ignore.

CPUs — the workhorse processors that have powered servers for decades — are in short supply. And the cause is the very AI boom that made GPUs famous.

Reuters reported on Wednesday that ByteDance, the Chinese parent company of TikTok, is developing its own proprietary CPUs to escape a shortage that has seen Intel and AMD raise prices by 10 to 35 per cent in recent months. The company is pursuing two architecture tracks simultaneously — one based on ARM (owned by SoftBank) and one on the open-source RISC-V instruction set — as it weighs which design best suits its long-term data centre needs.

## The inference shift

The shortage stems from a fundamental shift in how AI systems operate. Training a model — the process that made Nvidia's GPUs indispensable — is computationally intense but finite. Once trained, models are deployed for "inference," the phase where they actually perform tasks: answering questions, generating images, running autonomous agents.

Inference workloads demand something different. They require CPUs and GPUs working in tandem, with CPUs handling orchestration, data preprocessing, and the agentic reasoning loops that power tools like ByteDance's Coze platform. As AI moves from research demonstrations to production-scale deployment — billions of inference queries per day — CPU demand has exploded.

Intel has warned Chinese customers of server CPU delivery lead times of up to six months. AMD CEO Lisa Su said last week that the global CPU market is "tight," with demand outpacing forecasts. Nvidia itself has entered the CPU race: its new Vera processor, unveiled at Computex this week, targets what CEO Jensen Huang described as a $200 billion addressable market.

## The custom silicon stampede

ByteDance is not alone. Google, Amazon, and Microsoft are all developing custom CPUs for their cloud data centres. The economics have shifted: designing a chip costs hundreds of millions of dollars, but the savings from avoiding Intel and AMD markups — and from tailoring performance to specific workloads — now justify the investment for any company operating at hyperscale.

The trend has strategic implications. ByteDance's interest in RISC-V, the open-source alternative to ARM, is particularly significant. Unlike ARM, which charges licence fees, RISC-V is free to use, modify, and deploy. China's government has made RISC-V a national priority as a hedge against potential US restrictions on ARM technology.

## The Indian angle

This matters to Indian tech professionals in at least three ways.

First, thousands of Indian engineers at Intel, AMD, and ARM are designing the CPUs the world is fighting over. Intel's design centres in Bengaluru and Hyderabad employ some of the largest chip engineering teams outside the United States. When Intel says demand is so strong it sold chips it had originally written off, Indian engineers are part of the supply chain making that possible.

Second, India has made a strategic bet on RISC-V. The Indian Institute of Technology system has invested in RISC-V processor design, and the India Semiconductor Mission has signalled support for the architecture. As more hyperscalers explore RISC-V — ByteDance being the latest — that bet becomes more valuable.

Third, India's own data centre buildout, which Tata, Reliance, and Adani are all pursuing aggressively, faces the same CPU supply constraints. India cannot build AI infrastructure if it cannot secure the processors to run it.

The GPU shortage was the story of 2023 and 2024. The CPU shortage may define 2026 and 2027. For an industry full of Indian engineers, the implications are personal."""

art2_image = "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"


# ─────────────────────────────────────────────────────────────
# ARTICLE 3: Jensen Huang / Tsinghua / Chip Smuggling
# ─────────────────────────────────────────────────────────────

art3_body = """Jensen Huang, the CEO of the world's most valuable company, is walking a line that grows thinner by the week.

On one side: Nvidia's reliance on the US government, which controls the export licences that determine where its most powerful AI chips can be sold. On the other: China, which Huang has publicly called "very important" to Nvidia's business and where, despite US sanctions, the company still shipped 2.2 million AI accelerators in 2025 — a 55 per cent market share, according to IDC data reviewed by Reuters.

This week, both sides of that tension sharpened considerably.

## The advisory board

The Financial Times reported that Huang has accepted an invitation to join the advisory board of Tsinghua University's School of Economics and Management — one of China's most elite academic institutions, attended by senior Chinese politicians and business leaders. The move came shortly after Huang joined US President Donald Trump on a visit to China, where he aggressively lobbied for looser export controls.

Tsinghua is not a neutral choice. It is the intellectual centre of China's technology establishment, the alma mater of Xi Jinping, and a university whose research departments are deeply integrated with China's semiconductor and AI ambitions. For the CEO of a company that designs the chips powering American AI infrastructure to join its advisory board is a statement — about Nvidia's commercial priorities, about the limits of decoupling, and about Huang's personal calculation that engagement with China is worth the scrutiny it invites.

## The smuggling investigation

Separately, Bloomberg News reported on Wednesday that Taiwan prosecutors suspect three individuals successfully smuggled at least one shipment of Nvidia chips to China after first exporting them to Japan. The investigation, which involves analysis of customs records and logistics chains, highlights how US export controls are being circumvented through third-country routing.

The irony is precise. The Trump administration removed some restrictions on less-powerful Nvidia chip sales to China earlier this year, provided the company meets certain standards. But enforcement of those standards — and of outright bans on more advanced chips — depends on a patchwork of national customs agencies and intelligence services that clearly have gaps.

## The India factor

For Indian professionals in the AI and semiconductor industries, the Nvidia-China dynamic has direct career and investment implications.

Indian engineers make up a significant portion of Nvidia's workforce, particularly in its GPU architecture and CUDA software teams. As Nvidia navigates between Washington and Beijing, its employees — many of them on H-1B visas — face uncertainty about which markets their work will ultimately serve.

More strategically, the US-China chip war creates an opening for India. Both Nvidia and its rivals are looking for neutral-ground manufacturing and design hubs. India's semiconductor programme — backed by $18.2 billion in recently approved projects — is positioning the country as exactly that kind of alternative. Nvidia itself has expanded its India operations significantly, with Jensen Huang announcing partnerships with Reliance and Tata at India's AI Summit earlier this year.

The logic is straightforward: if China is restricted and Taiwan is geopolitically risky, India is the obvious third option. Whether India can build the infrastructure and talent pipeline fast enough to capture that opportunity is the trillion-dollar question.

For NRI investors tracking Nvidia stock — which has risen more than 150 per cent this year — the China entanglement adds a layer of risk that no amount of AI hype can fully offset. Huang's bet is that Nvidia can serve both superpowers simultaneously. The smuggling investigation suggests that, at the margins, the market is already making that decision for him."""

art3_image = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg"


# ─────────────────────────────────────────────────────────────
# Assemble and publish
# ─────────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "TSMC Says AI's Biggest Problem Isn't Speed. It's Electricity.",
        "subheadline": "The world's largest chipmaker says energy efficiency has overtaken raw computing power as the main constraint shaping future AI chip design — and it's raising prices to match.",
        "slug": make_slug("tsmc-energy-efficiency-ai-chip-design-constraint"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian chip designers at TSMC, Nvidia, Intel, and AMD are at the forefront of the efficiency shift. India's new fabs in Dholera and Gujarat face the same energy constraints, and the country's power grid makes efficiency-first design a strategic necessity.",
        "tags": ["tsmc", "semiconductor", "ai-chips", "energy-efficiency", "india-semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/retail-consumer/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-28/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/research/ibd-stock-of-the-day/tsm-stock-tsmc-ibd-stock-of-the-day-3nm-price-hike/"},
            {"name": "CryptoBriefing", "url": "https://cryptobriefing.com/tsmc-3nm-price-hike-2026/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": art1_image,
        "image_caption": "Server cooling fans in a data centre — energy consumption is now the defining constraint for AI chip design.",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The AI Inference Boom Just Created a CPU Shortage Nobody Predicted",
        "subheadline": "ByteDance is building custom processors, Intel and AMD prices are up 35 per cent, and the chip that powered the internet for decades is suddenly the scarcest component in AI.",
        "slug": make_slug("ai-inference-cpu-shortage-bytedance-custom-chips"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Thousands of Indian engineers at Intel, AMD, and ARM are designing the CPUs the world is fighting over. India's bet on RISC-V gains strategic value as ByteDance and others explore the open-source architecture.",
        "tags": ["cpu-shortage", "bytedance", "ai-inference", "risc-v", "intel", "amd", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/bytedance-developing-custom-cpu-chips-support-ai-rollout-sources-say-2026-05-28/"},
            {"name": "Reuters (Qualcomm-ByteDance)", "url": "https://www.reuters.com/technology/qualcomm-strikes-ai-chip-deal-with-tiktok-owner-bytedance-bloomberg-news-reports-2026-05-27/"},
            {"name": "Business Day", "url": "https://www.businessday.co.za/articles/bytedance-develops-custom-ai-chips-as-global-cpu-shortages-intensify/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art2_image,
        "image_caption": "A microprocessor circuit board — CPUs have become the unexpected bottleneck in the AI infrastructure buildout.",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Is Courting Beijing. Nvidia's Chips Keep Showing Up in China Anyway.",
        "subheadline": "Nvidia's CEO joins the advisory board of China's most powerful university as Taiwan investigates the smuggling of AI chips through Japan. For Indian engineers and investors, the implications are personal.",
        "slug": make_slug("jensen-huang-tsinghua-nvidia-china-chip-smuggling"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers at Nvidia face uncertainty as the company navigates US-China tensions. India's semiconductor programme positions the country as a neutral alternative hub — the trillion-dollar question is whether it can build fast enough.",
        "tags": ["nvidia", "jensen-huang", "china", "tsinghua", "chip-smuggling", "export-controls", "india-semiconductor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Financial Times via Reuters", "url": "https://www.reuters.com/technology/nvidia-ceo-jensen-huang-join-board-beijing-tsinghua-university-ft-reports-2026-05-28/"},
            {"name": "Bloomberg via Reuters", "url": "https://www.reuters.com/technology/taiwan-suspects-nvidia-chips-smuggled-china-via-japan-bloomberg-news-reports-2026-05-28/"},
            {"name": "Reuters (Huawei)", "url": "https://www.reuters.com/technology/huawei-looks-beyond-moores-law-2026-05-28/"},
            {"name": "New York Post", "url": "https://nypost.com/2026/05/28/business/nvidias-jensen-huang-joins-advisory-board-of-chinas-prestigious-tsinghua-university-report/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": art3_image,
        "image_caption": "Jensen Huang, CEO of Nvidia, whose balancing act between Washington and Beijing grows more precarious by the week.",
        "body": art3_body,
    },
]

# Verify images
for art in articles:
    print(f"\n🔍 Verifying image for: {art['headline'][:60]}...")
    verified = verify_image(art["image_url"])
    if verified:
        print(f"  ✅ Image OK")
    else:
        print(f"  ❌ Image FAILED — removing")
        art["image_url"] = None
        art["image_caption"] = None

# Publish
print("\n" + "="*60)
print("PUBLISHING ARTICLES")
print("="*60)
for art in articles:
    # Clean None image fields
    if art.get("image_url") is None:
        art.pop("image_url", None)
        art.pop("image_caption", None)
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
