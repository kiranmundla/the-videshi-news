#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 18:00 UTC batch"""

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


# ─── ARTICLE 1: Zepto IPO ───────────────────────────────────────────────────

art1_body = """Zepto, the quick-commerce company founded by Stanford dropouts Aadit Palicha and Kaivalya Vohra, has filed updated IPO papers with SEBI seeking to raise up to ₹8,010 crore ($837 million) in fresh equity — setting the stage for one of India's most closely watched listings this year.

The filing, which landed on Monday, also includes an offer-for-sale window for early backers Nexus Venture Partners and Contrary Capital. Axis Capital, Morgan Stanley, Goldman Sachs, and four other banks are managing the offering. A July listing is reportedly the target.

## The Numbers Tell Two Stories

Revenue more than doubled to ₹22,624 crore in FY26 from ₹11,110 crore the year before. Gross margins expanded to 18.6 per cent from 12.8 per cent. The adjusted EBITDA loss per order improved from ₹136 to ₹79. By the standards of Indian consumer-tech startups preparing for public markets, the trajectory looks right.

But losses also widened — to ₹5,905 crore from ₹4,700 crore — as Zepto doubled down on dark-store expansion, logistics, and customer acquisition. At its current quarterly cash burn of ₹882 crore and a net liquidity position of roughly ₹2,970 crore, the company has about ten months of runway. For context, Blinkit's parent Zomato and Swiggy each sit on cash reserves north of ₹12,000 crore. The IPO is not a luxury. It is oxygen.

## The Marketplace Pivot

Buried in the filing is a disclosure that may matter more than the headline number: Zepto is transitioning from an inventory-led model to a marketplace structure, where third-party sellers list products and the platform earns commissions, advertising revenue, and service fees. The company itself acknowledged it has "limited operating history" under this model.

If the pivot sticks, it could meaningfully improve margins. Marketplace businesses are structurally lighter. But it also means Zepto is asking public investors to bet on a business model it has barely tested at scale — while simultaneously burning through cash in a market where Amazon, Flipkart, and BigBasket are all now running their own quick-commerce operations.

## Why the Kirana Lobby Is Furious

The All India Consumer Products Distributors Federation, which represents 4.5 lakh distributors serving over 1.3 crore retail outlets, has called on the PMO, SEBI, and the CCI to suspend the IPO entirely. In a scathing press note, the federation described Zepto's listing as a "Black Day for India's Retailers, Distributors, Small Traders, MSMEs, Employees and Retail Investors."

The argument is familiar but gaining political weight: quick-commerce platforms use venture-backed discounting to undercut traditional retailers, creating unsustainable pricing distortions. Allowing a loss-making company to raise thousands of crores from public markets, the federation warns, will only fuel more of the same.

## What NRIs Should Watch

For Indian Americans tracking the Indian market, Zepto's IPO is a bellwether for three things at once.

First, whether India's retail-investor base — which powered the listings of Zomato, Paytm, and Nykaa — still has an appetite for high-growth, high-loss consumer-tech stories. The market mood has soured since those listings, and Paytm's post-IPO collapse remains a cautionary tale.

Second, whether quick commerce as a category has staying power beyond India's top eight cities. Zepto's valuation was $7 billion at its last private round; the IPO pricing will reveal how much of that holds in public markets.

Third, and most practically: for NRIs with Indian brokerage accounts, Zepto's prospectus is a window into the speed at which consumer behaviour in urban India is shifting. Ten-minute grocery delivery is no longer a novelty. It is a ₹22,000-crore-a-year business with three serious competitors, deep-pocketed entrants, and a very angry traditional trade lobby. The listing will price all of that."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Zepto Wants $837 Million From Public Markets. It Has Ten Months of Cash Left.",
    "subheadline": "The quick-commerce unicorn's updated IPO filing reveals soaring revenue, widening losses, and a marketplace pivot it has barely tested — all while India's kirana lobby demands regulators block the listing.",
    "slug": make_slug("zepto-ipo-837-million-quick-commerce-kirana"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors tracking Indian tech IPOs get a stress test for the quick-commerce thesis — and a front-row seat to the most politically charged listing of 2026.",
    "tags": ["zepto", "ipo", "quick-commerce", "india-startups", "sebi"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indian-quick-commerce-firm-zepto-raise-up-837-million-ipo-2026-06-09/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/does-zepto-deserve-a-10-bn-valuation-decoding-the-numbers-and-narrative"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/zeptos-marketplace-pivot-may-hold-key-to-profitability-as-it-heads-for-ipo/article69659321.ece"},
        {"name": "Outlook Business (AICPDF)", "url": "https://www.outlookbusiness.com/markets/aicpdf-seeks-suspension-of-zepto-ipo-calls-it-black-day-for-retail-trade"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8939510/pexels-photo-8939510.jpeg",
    "image_caption": "A smartphone displays a grocery delivery app surrounded by fresh produce",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ─── ARTICLE 2: NVIDIA RTX Spark AI PCs ─────────────────────────────────────

art2_body = """Jensen Huang walked onto the Computex 2026 stage in Taipei holding two laptops — one running a James Bond game, the other Forza Horizon 6 — and declared that NVIDIA was reinventing the personal computer. Two weeks on, the industry is still working out whether he is right.

The product in question is RTX Spark, NVIDIA's first consumer-grade system-on-chip for Windows laptops. It is ARM-based, built in partnership with MediaTek, and represents the company's most direct challenge yet to the Intel–AMD duopoly that has ruled PC silicon for three decades. Six OEMs — Microsoft, Lenovo, Dell, HP, Asus, and MSI — have already committed to building machines around it.

## What Is Actually Inside the Chip

The N1X, the first chip in the RTX Spark family, pairs a 20-core Grace CPU — the same architecture NVIDIA uses in data-centre Grace Hopper superchips — with a Blackwell-generation GPU carrying 6,144 CUDA cores and fifth-generation Tensor Cores. It supports up to 128GB of unified memory and delivers, by NVIDIA's count, one petaflop of AI performance.

In practical terms, that means the chip can run a 120-billion-parameter large language model entirely on-device — no cloud call, no API bill, no rate limits. Adobe says Photoshop and Premiere run roughly twice as fast on RTX Spark hardware compared to current-generation machines. Huang confirmed that follow-up chips, the N2X and N3X, are already in development.

## The Real Target: Apple's MacBook Pro

Reuters put it plainly: RTX Spark is aimed less at traditional PC buyers and more at the developers and content creators who have drifted to Apple's high-end MacBook Pro over the past five years. NVIDIA is making a simple bet — that a Windows machine with a petaflop of local AI compute, Blackwell-class graphics, and deep integration with Microsoft's Copilot stack can pull that audience back.

Whether it works is another question. Qualcomm's Snapdragon X series, the previous ARM-based challenger in the Windows ecosystem, struggled with legacy app compatibility and failed to move the needle on AI PC sales. NVIDIA claims RTX Spark will handle "every application that Windows has ever run," but the company has not published independent benchmarks to back that assertion.

Tirias Research analyst Kevin Hein offered a middle-ground take: "RTX Spark doesn't make traditional PCs obsolete. It creates a new category between the workstation and the AI server."

## Why Indian Engineers Should Pay Attention

NVIDIA's pitch matters to the Indian tech workforce for reasons that go beyond consumer electronics.

The company's partnership with MediaTek — a Taiwanese chipmaker with substantial engineering teams in Bengaluru and Noida — means Indian engineers are directly involved in the silicon underpinning RTX Spark. MediaTek's India headcount has grown steadily as the company expanded its work on 5G modems and now AI SoCs.

More broadly, the shift toward on-device AI compute is a potential inflection point for India's developer ecosystem. Running large models locally eliminates the cloud-inference costs that have priced many Indian startups and independent developers out of serious AI work. A petaflop on a laptop is not a data-centre replacement, but for prototyping, testing, and deploying smaller agentic workflows, it could meaningfully lower the barrier to entry.

The catch, for now, is price. RTX Spark laptops will debut at premium price points — likely above $2,000 — putting them out of reach for most Indian buyers in the near term. Huang has not announced a lower-end, non-"X" variant. Until NVIDIA does, the AI PC remains a tool for the top of the market, not the mass of it.

## The Agentic Angle

Huang's most revealing comment in Taipei was not about the chip but about what it is built to do. "Humans rent cores," he told journalists. "But agents — they want to use the CPU to get the job done."

The implication: NVIDIA envisions PCs running all day as local AI agent platforms, handling tasks autonomously while the user does other things. It is a vision of the personal computer as an always-on assistant, not a tool you open and close. Whether consumers want their laptops to work that way is unresolved. But for the first time, the hardware to support it exists in a portable form factor."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA's First PC Chip Has Arrived. It Runs a 120-Billion-Parameter AI Model Without the Cloud.",
    "subheadline": "RTX Spark, unveiled at Computex 2026, is Jensen Huang's ARM-based bet that a petaflop of local AI compute can lure developers away from MacBooks and reshape the PC market.",
    "slug": make_slug("nvidia-rtx-spark-ai-pc-computex-jensen-huang"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at MediaTek are building the silicon, and the death of cloud-inference costs could unlock local AI for India's startup ecosystem — if the price comes down.",
    "tags": ["nvidia", "rtx-spark", "ai-pc", "computex-2026", "jensen-huang", "arm"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Gizmodo", "url": "https://gizmodo.com/nvidia-now-has-a-laptop-chip-and-you-can-probably-guess-what-its-built-for-2000612987"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidias-ai-pc-push-banks-unproven-demand-beyond-niche-users-2025-06-08/"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/post/rtx-spark-is-not-a-pc-chip-it-is-a-platform-enclosure-play-68494c0ce40cd4f9ff22d44d/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "NVIDIA CEO Jensen Huang, who unveiled the RTX Spark chip at Computex 2026 in Taipei",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ─── ARTICLE 3: Opendoor India Exit ─────────────────────────────────────────

art3_body = """On Wednesday, Opendoor CEO Kaz Nejatian posted a note on X that amounted to four sentences of corporate prose and one very loud signal. "Today we began to say goodbye to our colleagues in India as we wind down our India operations," he wrote. "Our customers are in America, and that's where our operational work belongs."

The US real estate technology company is shutting down its offices in Chennai, Hyderabad, and Bengaluru, laying off all 250 India-based employees. The work those employees handled — back-office operations, manual workflows across fragmented systems — will not be rehired in the United States. It will, in large part, be replaced by AI.

## How It Happened

Opendoor set up its India operations in 2022, hiring across multiple technology hubs to manage the operational complexity of its online home-buying platform. For two years, the India team handled the kind of labour-intensive, process-heavy work that has been the bread and butter of Indian IT outsourcing for decades.

Then came what the company calls "Opendoor 2.0" — a restructuring initiative built around automation, unified systems, and what Nejatian describes as "small AI-native customer-facing teams" in the United States. As AI tools consolidated previously fragmented processes, the need for large offshore teams managing manual work diminished. The India shutdown is the final phase of that restructuring.

Affected employees will receive severance packages and outplacement services. A small number will stay temporarily to oversee the transfer of remaining functions.

## The Outsourcing Industry Is Watching

What makes the Opendoor story consequential is not its scale — 250 jobs is a rounding error in an Indian IT sector that employs millions — but its framing. This is a US company explicitly stating that AI has made its India operations unnecessary. Not redundant as part of cost-cutting. Not relocated to another country. Eliminated because machines can now do the work.

Keshav Lohia, a venture capitalist at Emergent Ventures, called it a "watershed moment" for AI-driven operations. Sheel Mohnot, co-founder of Better Tomorrow Ventures, was blunter: "As manual work gets replaced by AI, a lot of jobs will be lost in India."

Phil Fersht, chief executive of HFS Research, pushed back on the simplistic reading. The real shift, he argued, is not about jobs moving from India to the US — it is about AI reducing the total amount of operational labour companies require, regardless of location. He described the emerging model as "services-as-software": companies that combine AI, automation, and a thin layer of human expertise to deliver outcomes without continually adding headcount.

## The Bigger Picture for Indian IT

Opendoor's exit lands at a bruising moment for India's technology services sector. The Nifty IT index has fallen roughly 27 per cent over six months, hammered by concerns that advanced AI models — particularly Anthropic's Claude Fable 5, which approaches human-level code quality — are eroding the demand for traditional application development and maintenance contracts.

TCS, Infosys, and Wipro have collectively shed over 42,000 employees in recent periods. TCS chairman N. Chandrasekaran told shareholders last week that the company expects to have as many AI agents as human employees — half a million of each — within a few years. New hiring across the sector has slowed to a trickle.

The structural question is stark. India's IT services industry accounts for 80 per cent of the country's total services exports. NITI Aayog's 2025 report projected that in the worst case, AI could displace up to two million tech jobs in India by 2031. In the best case — if the country scales its AI workforce strategically — the sector could add four million jobs in five years. The gap between those scenarios is enormous, and Opendoor's India exit is a data point for the pessimistic end.

## What This Means for NRIs in Tech

For Indian-origin engineers and managers working in US technology companies, Opendoor's decision crystallises an uncomfortable reality. The cost-arbitrage model that created India's IT boom — the same model that produced the H-1B pipeline, the offshore development centres, the global capability centres — is being compressed from both ends: AI from above, and political pressure to reshore from below.

Nejatian's framing — "our customers are in America, and that's where our operational work belongs" — echoes rhetoric from Washington that has intensified under the current administration. When a CEO can cite both AI efficiency and patriotic optics in the same announcement, the incentive to bring work back is doubly reinforced.

For NRIs with family in India's IT sector, the practical advice from industry veterans is consistent: move toward AI-native roles, or risk being in the part of the workforce that AI is designed to replace. Nandan Nilekani put it most directly at Infosys's investor day in February: "Talent will have to deal with a world where writing code will not be the goal. The goal will be making AI work.\""""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Opendoor Just Shut Its Entire India Operation. It Replaced 250 Workers With AI.",
    "subheadline": "The US real estate firm's decision to close offices in Chennai, Hyderabad, and Bengaluru is being called a watershed moment for AI-driven outsourcing — and a warning shot for India's $315 billion IT sector.",
    "slug": make_slug("opendoor-india-shutdown-ai-outsourcing-watershed"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRIs with family in India's IT sector are watching AI compress the cost-arbitrage model that built the H-1B pipeline and offshore development centres.",
    "tags": ["opendoor", "ai-outsourcing", "india-it", "layoffs", "ai-disruption"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/us-real-estate-firm-opendoor-shuts-india-operations-lays-off-250-2026-06-12/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/12/opendoors-india-exit-is-fueling-a-bigger-conversation-about-ai-and-outsourcing/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/us-based-real-estate-tech-firm-opendoor-shuts-down-india-operations/article69669382.ece"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/post/opendoors-india-exit-sparks-debate-on-ais-impact-on-outsourcing-684ad15fe40cd4f9ff248e35/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33827306/pexels-photo-33827306.jpeg",
    "image_caption": "An office space in Mohali, Punjab — the kind of modern Indian tech office now at the centre of AI-driven restructuring",
    "image_attribution": "Pexels",
    "body": art3_body,
}


# ─── INSERT ──────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
