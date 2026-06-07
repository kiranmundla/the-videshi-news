#!/usr/bin/env python3
import json, os, uuid, re, requests, urllib.parse
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
    except Exception:
        pass
    return None

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Just Declared War on Apple and Intel. His Weapon Fits in a Laptop.",
        "subheadline": "NVIDIA's RTX Spark superchip brings a petaFLOP of AI compute to Windows PCs this fall — and Indian engineers helped build every layer of it.",
        "slug": make_slug("nvidia-rtx-spark-jensen-huang-pc-market-apple-intel"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers comprise a significant share of NVIDIA's workforce and helped architect RTX Spark. NRI investors holding NVDA stock — up 73% YTD even after Friday's selloff — are watching this diversification into a new $300B+ PC silicon market. Indian AI developers who've relied on cloud GPUs may finally get affordable local AI compute.",
        "tags": ["nvidia", "rtx-spark", "jensen-huang", "ai-pc", "arm", "computex-2026", "apple-silicon"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/"},
            {"name": "Engadget", "url": "https://www.engadget.com/computing/nvidia-rtx-spark-chip-windows-apple-silicon-moment/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/05/nvidia-wants-reinvent-pc-what-means-intel-amd-qualcomm/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/nvidia-bets-on-ai-pcs-with-new-rtx-spark-windows-laptops-and-desktops"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/nvidia-plots-multi-generation-assault-on-pc-processors-with-rtx-spark-and-successors/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang, who unveiled the RTX Spark superchip at Computex 2026 in Taipei",
        "image_attribution": "Wikimedia Commons",
        "body": """For forty years, you launched apps. Click. Type. Wait. Jensen Huang wants to end that era — and he just dropped the silicon to prove it.

At Computex 2026 in Taipei, the NVIDIA CEO unveiled the RTX Spark, the company's first processor designed for Windows laptops and desktops. It is not a graphics card that happens to fit in a PC. It is a full system-on-chip: a 20-core Arm-based Grace CPU fused with a Blackwell RTX GPU packing 6,144 CUDA cores, fifth-generation Tensor Cores, and up to 128GB of unified LPDDR5X memory — all connected via NVLink-C2C interconnect. NVIDIA claims it delivers one petaFLOP of AI performance in a form factor slim enough for a 14-millimetre laptop.

The pitch is deceptively simple. Instead of launching applications, your machine responds to instructions. AI agents run locally — no cloud required, no data leaving your device. "We're reinventing the personal computer," Huang told the Computex audience, with Microsoft CEO Satya Nadella appearing alongside to confirm deep Windows integration.

## The Real Target Is Cupertino

The architecture will sound familiar to anyone who has used a MacBook in the past five years. Unified memory. Arm cores mixing performance and efficiency clusters. GPU and CPU on a single die. Apple's M-series chips pioneered this approach and gave Macs a generational lead over Windows PCs. RTX Spark is NVIDIA's answer — with one critical addition: AI-specific hardware that Apple's chips lack.

Where Apple's M5 Neural Engine handles on-device ML tasks, RTX Spark's Tensor Cores are designed for full-scale large language model inference, image generation, and multi-agent orchestration. NVIDIA is betting that the next PC upgrade cycle will be driven not by faster browsers or better spreadsheets, but by AI agents that actually do work.

MediaTek, the Taiwanese chip designer, co-developed the CPU portion. Dell, HP, Lenovo, Microsoft's Surface line, ASUS, MSI, Acer, and GIGABYTE have committed to shipping RTX Spark systems this fall. Base configurations are expected to start around $1,799, with premium builds reaching $2,899 or higher.

## What Intel and AMD Stand to Lose

For Intel and AMD, this is an existential incursion. NVIDIA already dominates data centre AI with over 90% market share. Now Huang is moving downstream — into the $300 billion PC processor market that Intel and AMD have controlled for decades.

Intel's new CEO Lip-Bu Tan was in Taipei the same week, pitching TSMC partnerships and 3nm Xeon server chips. AMD countered with its Ryzen AI Ultra lineup, which supports up to 192GB of unified memory. Qualcomm's Snapdragon Elite Oryon cores remain competitive on CPU benchmarks. But none of them can match NVIDIA's GPU horsepower, its CUDA software ecosystem, or its brand cachet among developers and enterprises.

The competitive dynamics are further complicated by RTX Spark's use of Arm architecture. Decades of Windows software were written for x86. App compatibility — the same problem that hobbled early Windows on Arm laptops — could slow adoption. NVIDIA says it supports legacy x86 applications through emulation, but real-world performance will determine whether that promise holds.

## Why This Matters for Indian Tech Professionals

The implications extend well beyond Silicon Valley. Indian engineers represent a substantial share of NVIDIA's global workforce, particularly in GPU architecture, CUDA development, and AI research. The RTX Spark project pulled from these teams across Bangalore, Hyderabad, and Pune.

For the roughly 300,000 Indian tech workers in the United States on H-1B visas — many of whom hold NVDA stock as part of their compensation — this is a portfolio-level event. NVIDIA's shares fell 6% on Friday in the broader chip selloff triggered by Broadcom's disappointing earnings, but the stock remains up 73% year-to-date. A successful PC entry would open an entirely new revenue stream beyond the data centre business that currently generates 92% of NVIDIA's $81.6 billion quarterly revenue.

Indian AI developers and startups may have the most to gain. Running large language models locally — without paying cloud inference costs — has been a persistent bottleneck for smaller teams and bootstrapped founders. A laptop with 128GB of unified memory and a petaFLOP of AI compute could shift the economics of Indian AI development materially.

## The Stakes and the Scepticism

This is NVIDIA's second attempt at PC processors. Its Tegra chip line, launched over a decade ago for mobile devices, faded into irrelevance. Huang acknowledged the history but argued that AI has changed the calculus: the demand for on-device intelligence did not exist in 2013.

Financially, even a wildly successful PC chip line would be a rounding error for NVIDIA. Data centre revenue was $75.2 billion in the most recent quarter alone. But the strategic value is different. If AI agents become the primary interface for personal computing — replacing app stores, search bars, and file systems — the company that controls the silicon wins the platform war.

Huang has already mapped out successors. The N2X and N3 series chips are in development, promising continued advances in architecture, memory, and efficiency. NVIDIA is not making a one-time bet. It is building a multi-generational assault on the PC market.

The real test arrives this fall, when the first RTX Spark machines ship and buyers decide whether on-device AI is worth $1,800."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Five Indian States Flew to Taipei to Sell Themselves to Taiwan's Chip Industry. Here's What They Offered.",
        "subheadline": "At Computex 2026, India mounted its most aggressive semiconductor charm offensive yet — pitching packaging hubs, fab-ready land, and a pipeline of homegrown chip startups.",
        "slug": make_slug("india-five-states-computex-2026-semiconductor-taiwan-pitch"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI semiconductor professionals in the US, many working at Intel, TSMC, Qualcomm, and AMD, are watching India's chip push as a potential return-to-India opportunity. The deepening India-Taiwan semiconductor corridor also opens cross-border investment and consulting avenues for diaspora engineers and venture capital.",
        "tags": ["india-semiconductor", "computex-2026", "taiwan", "chip-manufacturing", "andhra-pradesh", "indian-startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DIGITIMES Asia", "url": "https://apps.digitimes.com/tag/south+asia"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/indian-companies-pitch-products-seek-partnerships-at-mega-tech-trade-event-in-taiwan"},
            {"name": "Reuters", "url": "https://www.reuters.com/breakingviews/taiwan-forges-thicker-silicon-shield-2026-06-05/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Close-up of electronic microchips on a circuit board, representing India's growing semiconductor ambitions",
        "image_attribution": "Pexels",
        "body": """When the 2026 Taiwan–India Semiconductor Forum convened on the sidelines of Computex in Taipei last week, the delegation from India was not a token presence. Five of India's most industrialised states — including Andhra Pradesh, Gujarat, and Tamil Nadu — sent senior officials to pitch their regions as the next anchors for global electronics and AI supply chains. It was India's most coordinated semiconductor lobbying effort at a major international trade show to date.

The timing was not accidental. As the US-China chip war intensifies and Taiwanese manufacturers look to diversify beyond their island, India is positioning itself as a credible alternative — not for cutting-edge fabrication, which remains years away, but for the adjacent steps in the semiconductor value chain that are moving fastest.

## Andhra Pradesh Bets on Packaging

Andhra Pradesh made the most concrete pitch. Speaking on the sidelines of Computex, state officials outlined a strategy focused on semiconductor packaging — the back-end process of encasing fabricated chips in protective casings, connecting them to circuit boards, and testing them for functionality. It is not as glamorous as chip fabrication, but it is where much of the industry's near-term growth is concentrated.

Advanced packaging, which includes technologies like chip-on-wafer-on-substrate (CoWoS) and fan-out wafer-level packaging, has become a critical bottleneck in the AI supply chain. TSMC's advanced packaging capacity is sold out through 2027. India's proposition: we have the land, the engineering workforce, and the government incentives to absorb overflow demand.

Gujarat, home to Micron's $2.75 billion assembly and test plant in Sanand and Tata Electronics' 300mm wafer fab under construction in Dholera, positioned itself as the state with the most advanced semiconductor infrastructure. Tamil Nadu emphasised its existing electronics manufacturing base — Foxconn's iPhone plants, Dell and Lenovo assembly lines — as proof of supply chain readiness.

## Indian Companies Step Onto the Floor

It was not just state officials doing the pitching. Indian electronics manufacturer Sahasra showcased its microSD cards to buyers from China, the US, and Europe. Zoho Corporation, the Chennai-based software giant, targeted Taiwan's small and medium enterprises with its cloud-based business applications.

"We are getting very, very good responses," said Ankur Dwivedi, strategic account manager at Sahasra, which used the event to explore technology collaborations and potential joint ventures for implementing manufacturing capabilities in India.

Zoho's presence signalled a different dimension of India-Taiwan tech ties. "People have recognised Indian expertise in terms of technology, in terms of software development — there is a trust," said Eng Kit Goh, Zoho's market lead for Hong Kong, South Korea, and Taiwan.

The exhibition itself — featuring a record 6,000 booths from 1,500 exhibitors across 33 countries and drawing 111,312 visitors from 152 countries — provided the backdrop India needed to make its case on the global stage.

## From Design to Pilot Production

Perhaps the most significant development was not visible on the Computex floor at all. According to DIGITIMES Asia, India's emerging semiconductor startups — companies such as Netrasemi, Mindgrove Technologies, and Agnit Semiconductors — are entering a crucial phase, moving from chip design into customer-facing pilot production.

This transition matters because it closes the gap between India's abundant chip design talent (a legacy of decades of R&D centres run by Intel, Qualcomm, Texas Instruments, and Broadcom) and actual silicon output. India has long been where chips were designed but never where they were made. The startup cohort, backed by the India Semiconductor Mission's design-linked incentive scheme, is beginning to change that equation.

Infineon Technologies' India operations are also moving up the value chain. The German chipmaker's Indian engineering teams are transitioning from traditional support roles to global ownership positions, driven by rising demand from AI data centres for power semiconductor design — a shift from cost-centre to profit-centre that mirrors broader structural changes in how multinationals deploy Indian engineering talent.

## The Diaspora Calculus

For the estimated 40,000 Indian-origin semiconductor professionals working in the United States — at Intel, TSMC's Arizona fab, Qualcomm, AMD, and scores of fabless design firms — India's chip push carries a personal dimension. Every Dholera update, every Andhra Pradesh pitch deck, every new startup fundraise is data in a calculation many of them are running privately: is this the decade to go back?

The math is improving. India has now approved six semiconductor plants. Micron's Gujarat facility is under construction. Tata Electronics is working with Taiwan's PSMC on a 300mm fab. HCL and Foxconn just received approval for a new plant at Jewar, near Delhi. The ecosystem is incomplete — India still lacks a single operational fab producing commercial silicon — but the trajectory is unmistakable.

Taiwan's trade council chairman, James C.F. Huang, extended "a warm invitation to India's vibrant tech industry," encouraging stronger participation in future editions of Computex. The diplomatic language masked a commercial reality: Taiwan needs diversification partners, and India needs semiconductor know-how. Each side has something the other wants.

## What Comes Next

India faces a PCB supply squeeze that could slow its ambitions. Raw material inflation, logistics disruptions, and structural dependence on Chinese and Taiwanese imports for printed circuit boards are driving costs higher. Building chips is one challenge; building the full supply chain around them is another.

But the Computex showing represented something that did not exist three years ago: a coordinated, multi-state, multi-company Indian presence at the world's most important computing trade show, backed by a government willing to spend $10 billion on semiconductor incentives. India is no longer waiting to be invited to the chip table. It is pulling up a chair."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
