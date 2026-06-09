#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 15:00 UTC run"""
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
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ─────────────────────────────────────────────
# Article 1: Zepto IPO Filing
# ─────────────────────────────────────────────

art1_body = """Zepto filed updated draft papers with SEBI on Monday to raise up to ₹8,010 crore ($837 million) through a fresh issue of shares, setting the stage for what could be India's most closely watched tech listing of 2026. The filing also includes an offer-for-sale of 11.35 crore equity shares by existing investors, bringing the total issue size to an estimated ₹11,000 crore.

If the July listing goes as planned, Zepto will join Eternal (Zomato's parent, which owns Blinkit) and Swiggy on the stock exchanges — completing a public-market trifecta for Indian quick commerce that would have seemed absurd four years ago when the category barely existed.

## The Numbers Tell Two Stories

The revenue story is extraordinary. Zepto's operating revenue more than doubled year-over-year to ₹22,624 crore in the fiscal year ending March 2026. Advertising revenue, a metric Wall Street will scrutinise heavily, surged 151% to ₹1,640 crore. The gross merchandise value of orders grew by 98%, suggesting demand is growing alongside its footprint.

The loss story is less comfortable. Net losses widened to ₹5,905 crore from ₹4,700 crore the previous year. The startup acknowledged in its filing that it "may continue to incur losses and may not be able to sustain its historical growth rates" — standard disclosure, but telling for a company asking public-market investors to take a position before profitability materialises.

## Stanford to Dalal Street

Founders Aadit Palicha and Kaivalya Vohra, who dropped out of Stanford to launch the company in 2021, have built Zepto's 10-minute delivery model across India's major cities using a network of dark stores — compact warehouses in densely populated neighbourhoods that make the speed promise logistically possible.

The IPO proceeds will fund more dark stores, technology and cloud infrastructure, marketing, and acquisitions. That last item is worth watching. In a sector where Blinkit, Instamart, Amazon, Flipkart, and BigBasket are all spending aggressively, Zepto's willingness to acquire suggests consolidation is coming.

## The Valuation Question Nobody Has Answered

Zepto was valued at $7 billion in its last private round in October, when it raised $450 million. Several notable investors — Y Combinator, Lightspeed, StepStone, and Glade Brook — are not selling in the offer-for-sale, opting to hold their stakes through the listing. That confidence is worth something.

But it cuts both ways. Some mutual funds and family offices that reviewed Zepto ahead of the IPO have signalled valuations well below the $7 billion private mark, according to people familiar with the discussions. The gap between what private markets priced and what public markets will accept is the central tension of this offering.

Axis Capital, Morgan Stanley, Goldman Sachs, Motilal Oswal, HSBC, JM Financial, and IIFL Capital are managing the IPO — a heavyweight roster that reflects the scale of the listing and the complexity of the sell.

## Why This Matters If You Wire Money Home

For NRI investors already holding Swiggy and Eternal shares, Zepto's listing forces a portfolio question. All three companies are burning cash to win the same consumer, in the same cities, with the same 10-minute promise. Blinkit has Zomato's food delivery ecosystem behind it. Instamart has Swiggy's. Zepto has speed, execution, and now the most current financial data of any quick-commerce company in India — which is either a competitive advantage or an uncomfortably transparent look at an unprofitable business.

The $837 million fresh issue will dilute existing holders, but it gives Zepto a war chest for the next phase. For Indian Americans tracking India's consumer tech story, this is the most significant listing since Swiggy's debut — and a real-time stress test of whether India's grocery wars have a profitable endgame or just a very expensive middle game."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Zepto Just Filed for an $837 Million IPO. India's Grocery Wars Are Heading to the Stock Market.",
    "subheadline": "The Stanford dropouts who bet on 10-minute delivery have doubled revenue to ₹22,624 crore. Losses doubled too. The July listing will test whether quick commerce has a profitable endgame.",
    "slug": make_slug("zepto-ipo-837-million-quick-commerce-nri-investors"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors already holding Swiggy and Eternal shares now face a third listing in the same sector. Zepto's ad revenue growth hints at a platform play, but widening losses to ₹5,905 crore will test whether diaspora capital chases growth or demands profitability.",
    "tags": ["zepto", "ipo", "quick-commerce", "indian-startup", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indian-quick-commerce-firm-zepto-raise-up-837-million-ipo-2026-06-09/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/09/zeptos-ipo-filing-reveals-fast-growth-bigger-losses/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/markets/zepto-files-8010-crore-ipo-papers/article69671234.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8939267/pexels-photo-8939267.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A smartphone displays a delivery confirmation surrounded by fresh vegetables, illustrating India's quick commerce boom",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────
# Article 2: Intel's CPU Renaissance Under Lip-Bu Tan
# ─────────────────────────────────────────────

art2_img = "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg"

art2_body = """For the better part of a decade, Intel was the semiconductor industry's most reliable punchline — a manufacturing giant that missed mobile, fumbled AI, and watched NVIDIA sprint past it to become the world's most valuable company. Then something unexpected happened: the AI agents that everyone is building turned out to need CPUs.

At Computex in Taipei last week, NVIDIA CEO Jensen Huang — the man who has done more than anyone to make GPUs the centre of computing — stood on stage and declared that "the CPU is now the conductor, and the GPU is the orchestra." It was meant as a product pitch for NVIDIA's own Vera CPU. For Intel's new CEO Lip-Bu Tan, it was a validation of the bet he has staked his turnaround on.

## The Agent Economy Needs a Different Chip

The shift is architectural, not cosmetic. Training an AI model is a GPU-intensive job: massive parallel computation, brute-force matrix multiplication. But deploying AI agents — software that autonomously executes tasks, orchestrates tool calls, manages workflows — is a CPU-heavy operation. Agents need low latency, high instruction-per-cycle throughput, and the ability to coordinate thousands of simultaneous operations. That is precisely what CPUs were designed for.

OpenAI, Anthropic, Google, and every enterprise deploying agentic AI are discovering that their inference infrastructure needs far more CPU muscle than their training clusters did. Tan told reporters at Computex that "many CEOs have been calling him asking for more CPUs over the last month." If demand holds, Intel could ride several years of renewed processor relevance.

## Tan's Ruthless Reset

The opportunity alone would not save Intel. Tan's restructuring has been the most aggressive in the company's 58-year history. He has cut approximately 34% of Intel's workforce — tens of thousands of jobs. He paused planned manufacturing expansions in Germany and Poland. He flattened corporate bureaucracy, centralised engineering reporting directly to himself, and brought in senior talent from Qualcomm and Arm to lead the data centre and AI divisions.

"At our heart, Intel is an engineering company," Tan said during his Computex keynote. "And that's what I decided from Day 1. I have all the engineering report to me."

He has also secured strategic investments from NVIDIA and SoftBank — a remarkable development given that NVIDIA is Intel's primary competitor in the data centre. The investments signal that even Jensen Huang sees value in Intel's manufacturing capabilities, particularly for foundry services where TSMC's dominance creates supply chain risk.

## Bengaluru Is Central to the Turnaround

Intel's India operations, centred in Bengaluru with additional sites in Hyderabad and Pune, constitute one of the company's largest engineering centres globally. More than 10,000 engineers in India work on chip design, validation, software, and AI development. As Tan reshapes Intel's product roadmap around agentic AI and inference chips, Bengaluru's design teams are doing critical work on the architectures that will determine whether the turnaround succeeds.

For Indian engineers at Intel — both in India and on H-1B visas in the US — Tan's restructuring has been a double-edged sword. The layoffs have been severe: colleagues in Santa Clara, Hillsboro, and Folsom have lost jobs, and H-1B holders face the 60-day grace period clock when terminated. But the engineers who remain are working on what may be Intel's most consequential product generation since the Pentium era.

## The Stock Tells the Story

Intel's share price has climbed from below $19 at its 52-week low to above $107 — a more than fivefold recovery. The market is pricing in Tan's credibility, the CPU demand surge, and a CHIPS Act tailwind that has delivered billions in US government support for domestic semiconductor manufacturing.

The question is whether execution matches ambition. Intel must ship competitive chips on time, ramp its foundry business to attract customers beyond NVIDIA and SoftBank, and prove that its manufacturing process can match TSMC and Samsung at advanced nodes. For Indian Americans in semiconductor engineering — a community that has built careers at Intel since the 1990s — the next eighteen months will determine whether this comeback is real or just a dead-cat bounce with a better CEO."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Intel Was Dying. Then AI Agents Needed CPUs. Lip-Bu Tan Is Riding the Accident.",
    "subheadline": "The new CEO has fired a third of Intel's workforce, flattened its bureaucracy, and bet the company on a world where software agents need orchestration chips. Bengaluru's 10,000 Intel engineers are central to the plan.",
    "slug": make_slug("intel-lip-bu-tan-cpu-agentic-ai-turnaround-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Intel employs over 10,000 engineers in Bengaluru, one of its largest global design centres. Indian Americans in semiconductor engineering built careers at Intel since the 1990s. Tan's 34% workforce cuts hit H-1B holders hard, but the survivors are working on Intel's most important product generation in decades.",
    "tags": ["intel", "lip-bu-tan", "cpu", "agentic-ai", "semiconductor", "indian-engineers"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2025/06/09/tech/intel-cpu-agentic-ai-turnaround/index.html"},
        {"name": "UnderCode News", "url": "https://undercodenews.com/intels-fight-for-survival-lip-bu-tan-cpu-revival/"},
        {"name": "LinkedIn/Computex Analysis", "url": "https://www.linkedin.com/pulse/computex-2026-what-worlds-largest-ai-hardware-show-signals/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img,
    "image_caption": "Intel CEO Lip-Bu Tan, who has led the chipmaker's aggressive restructuring since taking the helm",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────
# Article 3: Qualcomm's Strategic Crisis from RTX Spark
# ─────────────────────────────────────────────

art3_img = "https://upload.wikimedia.org/wikipedia/commons/6/6e/Cristiano_Amon_%28President_%26_CEOQualcomm%29_%2854916855494%29_%28cropped%29.jpg"

art3_body = """Qualcomm spent three years telling Wall Street that the PC was its next growth engine. Windows on Arm, powered by Snapdragon X chips, would crack the laptop market wide open and reduce the company's dependence on smartphone modems. Then Jensen Huang walked on stage at Computex and built a better version of everything Qualcomm was selling — with an ecosystem Qualcomm could never match.

Since NVIDIA unveiled RTX Spark on June 1, Qualcomm's stock has dropped by double digits. The magnitude of the decline tells you what the market thinks: this is not a competitive skirmish. It is an existential threat to a growth strategy that Qualcomm's leadership had staked real capital on.

## What RTX Spark Actually Threatens

The numbers explain the panic. NVIDIA's RTX Spark combines a CPU, GPU, and up to 128 gigabytes of unified memory on a single chip, capable of running large AI models locally — something Qualcomm's Snapdragon X series simply cannot do at the same scale. NVIDIA claims up to one petaflop of AI computing capability. But the hardware is not even the most dangerous part.

NVIDIA's software ecosystem — CUDA, RTX, and DLSS — has been the industry standard for developers, gamers, and content creators for years. More than 100 software companies and game studios have already committed support for RTX Spark. Qualcomm's Snapdragon X, by contrast, spent its first two years fighting app compatibility issues on Windows on Arm.

"Nvidia just has more clout and more industry weight to push and make things happen that Qualcomm couldn't do early on," said Ryan Shrout, president at Signal65. "They can get game developers on board, and get software developers in the emerging AI space to pay attention."

Six PC manufacturers — Microsoft, Asus, HP, Lenovo, Dell, and MSI — will ship RTX Spark laptops, with Acer and Gigabyte to follow. These are the same companies Qualcomm spent years courting for Snapdragon X. The premium AI PC tier that Qualcomm was building toward now belongs to NVIDIA before Qualcomm could fully occupy it.

## Qualcomm's Retreat to the Budget Tier

The strategic response has been swift and telling. Qualcomm recently announced the Snapdragon C platform, targeting Windows laptops starting around $300 — a sharp pivot from the premium positioning of Snapdragon X. It is a rational move: if NVIDIA is going to own the high end, Qualcomm can try to own volume at the low end. But it is a fundamentally different business with thinner margins and less strategic value.

CEO Cristiano Amon faces an uncomfortable portfolio review. Qualcomm's core smartphone modem business remains strong, and the company's automotive platform (Snapdragon Digital Chassis) is winning design wins in connected vehicles. But the PC diversification story — which was supposed to be the catalyst for multiple expansion — now looks significantly impaired.

## 13,000 Indian Engineers in the Middle

Qualcomm employs approximately 13,000 people across India, with major centres in Hyderabad, Bengaluru, and Chennai. These engineers work on everything from Snapdragon chip design and 5G modem architecture to AI inference optimisation. In San Diego, Qualcomm has historically been one of the top H-1B employers in the semiconductor industry, with thousands of Indian-origin engineers in critical design and leadership roles.

The stock decline matters directly to these workers. Qualcomm's equity compensation is a significant component of total pay, particularly for senior engineers. A sustained share price decline erodes RSU values and makes retention harder — especially when NVIDIA, Apple, and Google are aggressively hiring chip designers.

For Indian American engineers who chose Qualcomm over FAANG offers — attracted by the semiconductor work, the San Diego lifestyle, or the promise that Qualcomm was diversifying beyond mobile — the RTX Spark moment forces a career reassessment. Qualcomm is not going under. Its $218 stock price and 5G patent portfolio guarantee relevance. But the growth narrative that justified premium compensation is under strain.

## What Happens Next

IDC estimates global PC shipments will decline 11.3% in 2026, which means the AI PC market that NVIDIA and Qualcomm are fighting over is shrinking in total volume even as the premium segment grows. The winner will be whoever owns the developer ecosystem, and right now that is NVIDIA by a wide margin.

DigiTimes analyst Jason Tsai warns that RTX Spark risks "remaining confined to specialty applications unless manufacturers can bring complete systems to market near the $1,500 threshold." That is Qualcomm's only hope in the premium PC tier: that NVIDIA prices itself out of mass adoption. It is a bet on the competitor's failure, which is not a strategy. It is a prayer."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA Dropped a Bomb on Qualcomm's PC Strategy. The Stock Says Everything.",
    "subheadline": "Qualcomm's shares have cratered by double digits since RTX Spark's Computex debut. The company is retreating to $300 laptops. For 13,000 Indian engineers at Qualcomm, the pivot is personal.",
    "slug": make_slug("qualcomm-nvidia-rtx-spark-crisis-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Qualcomm employs approximately 13,000 people in India (Hyderabad, Bengaluru, Chennai) and is a top H-1B employer in San Diego. A sustained stock decline erodes RSU values for Indian engineers who chose Qualcomm over FAANG. The growth story that justified premium compensation is now under serious strain.",
    "tags": ["qualcomm", "nvidia", "rtx-spark", "semiconductor", "indian-engineers", "h1b"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/09/nvidia-ceo-jensen-huang-declared-war-intel-amd-qualcomm/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidias-ai-pc-push-banks-unproven-demand-beyond-niche-users-2026-06-09/"},
        {"name": "Blockonomi", "url": "https://blockonomi.com/nvidia-nvda-rtx-spark-challenges-intel-amd-qualcomm/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art3_img,
    "image_caption": "Qualcomm CEO Cristiano Amon, who faces a strategic reckoning as NVIDIA enters the PC chip market",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
