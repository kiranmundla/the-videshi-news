#!/usr/bin/env python3
"""Technology writer — 3 articles for The Videshi, 2026-06-11 batch."""

import json, os, uuid, requests
from datetime import datetime, timezone

# ── Supabase config ─────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}
IMAGE_BASE = f"{SUPABASE_URL}/storage/v1/object/public/article-images"
NOW = datetime.now(timezone.utc).isoformat()

# ── Articles ─────────────────────────────────────────────────────────────

articles = [
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ARTICLE 1 — Micron HBM4 / Sanjay Mehrotra / NVIDIA Vera Rubin
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron's Sanjay Mehrotra Locks In the Memory Contract That Will Power NVIDIA's Next AI Era",
        "subheadline": "The Kanpur-born CEO's HBM4 certification for Vera Rubin cements Micron among a three-supplier oligopoly — and ties the company's Gujarat ambitions to the AI arms race.",
        "slug": "micron-sanjay-mehrotra-hbm4-nvidia-vera-rubin-20260611",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 78,
        "tags": ["micron", "sanjay-mehrotra", "hbm4", "nvidia", "vera-rubin", "semiconductors", "ai-chips", "gujarat"],
        "urgency": "medium",
        "image_url": f"{IMAGE_BASE}/sanjay_mehrotra.jpg",
        "image_caption": "Sanjay Mehrotra, Chairman, President and CEO of Micron Technology",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "diaspora_angle": "Indian-origin CEO Sanjay Mehrotra, born in Kanpur, leads Micron as it wins a critical NVIDIA certification — while the company builds a $2.75 billion assembly and test facility in Gujarat.",
        "sources": json.dumps([
            {"name": "Bloomberg via Barron's", "url": "https://www.barrons.com/articles/micron-stock-price-nvidia-hbm-10c444fc"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/nvidia-corp-nvda-strengthens-ai-platform-with-micron-hbm4-1538917/"},
            {"name": "Micron Technology – Leadership", "url": "https://www.micron.com/about/leadership/sanjay-mehrotra"},
            {"name": "Computer History Museum – Sanjay Mehrotra", "url": "https://www.computerhistory.org/collections/catalog/102740456"}
        ]),
        "published_at": NOW,
        "body": """When NVIDIA CEO Jensen Huang confirmed on June 6 that Micron Technology had earned HBM4 certification for the forthcoming Vera Rubin AI platform, the news rippled through semiconductor markets with a force that belied its dry, technical substance. For Micron's chairman and chief executive, Sanjay Mehrotra — born in Kanpur, educated at UC Berkeley, and now presiding over one of the world's most consequential memory companies — the certification was not merely a contract win. It was vindication of a multi-year bet that the age of artificial intelligence would make high-bandwidth memory as strategically important as the processors it feeds.

## The Three-Supplier Oligopoly

Vera Rubin, NVIDIA's next-generation AI platform set for full production in 2027, will succeed the current Blackwell architecture that already dominates data centre deployments worldwide. Its Rubin GPUs require HBM4, the latest iteration of stacked, high-bandwidth DRAM — a technology so demanding that only three companies on Earth can produce it. With the June 6 certification, Micron joins South Korea's SK Hynix and Samsung Electronics in a supplier trinity that will collectively underpin tens of billions of dollars in AI infrastructure spending.

The stakes are staggering. Each HBM4 unit requires roughly three times the semiconductor wafer capacity of standard memory. As TrendForce analysts noted this week, the crowding-out effect on conventional DRAM capacity is expected to intensify through 2027, handing suppliers pricing power that the commodity memory business has rarely enjoyed. Micron's revenue in fiscal 2025 hit $37.4 billion — a 49 per cent jump from the prior year — and the HBM4 pipeline could propel the next leg of growth.

KeyBanc analyst John Vinh had previously flagged that both Micron and SK Hynix were encountering difficulties meeting NVIDIA's exacting standards. The certification, then, signals that Micron's engineering teams cleared a bar that some on Wall Street doubted they could. Despite the positive news, Micron stock fell 13 per cent on Friday to $864 — its worst single-day drop since April 2025 — dragged down by a broader semiconductor rout triggered by Broadcom's weak earnings. The paradox says more about the market's mood than about Micron's fundamentals.

## From Kanpur to the AI Frontier

Mehrotra's biography reads like a template for the Indian-origin technologist who reshaped Silicon Valley. He arrived in the United States for graduate studies at Berkeley, co-founded SanDisk in 1988, and built it into a Fortune 500 flash memory giant before its $19 billion sale to Western Digital in 2016. He holds more than 70 patents, several of them foundational to the high-capacity flash storage now embedded in every smartphone and data centre on the planet. In 2022, the National Academy of Engineering inducted him — one of the profession's highest honours. BITS Pilani, Rochester Institute of Technology, and Boise State University have each awarded him honorary doctorates.

He took the helm at Micron in 2017, and the timing proved prescient. The AI revolution transformed memory from a cyclical commodity into a strategic chokepoint, and Mehrotra positioned Micron at its centre. Under his leadership, the company's market capitalisation reached $463 billion by February 2026, placing it among the 100 most valuable companies globally.

## The Gujarat Connection

For the Indian diaspora, Mehrotra's corporate triumphs carry a parallel significance. Micron is building a $2.75 billion semiconductor assembly and test facility in Sanand, Gujarat — the company's first major manufacturing investment in India. The plant, backed by incentives under India's semiconductor mission, will package and test memory chips for global markets. It will not fabricate wafers (that remains the domain of Micron's fabs in Idaho, Japan, and Singapore), but it anchors India in the HBM supply chain at a moment when the technology's strategic value has never been higher.

For the roughly 4.4 million Indian Americans in the United States, many of whom work in the technology sector that consumes Micron's products, the Mehrotra story is both familiar and extraordinary. An engineer from Kanpur now steers decisions that shape how the world's AI infrastructure gets built — and whether India captures a share of the manufacturing value.

## What Comes Next

NVIDIA's Vera Rubin platform has also attracted interest from Taiwan's Nanya Technology for LPDDR5X memory, a different component that powers the platform's CPUs rather than its GPUs. The supply chain diversification reflects NVIDIA's determination to avoid bottlenecks as AI spending accelerates past $300 billion annually in semiconductors alone.

For Mehrotra, the HBM4 certification is one piece of a larger puzzle: proving that Micron can compete at the very frontier of memory innovation, not merely survive as a scale producer. With SK Hynix entrenched as NVIDIA's largest memory partner and Samsung investing aggressively to close the gap, the three-way contest will define who profits most from the AI boom's next chapter. On the evidence of June 6, Micron — and its Kanpur-born chief executive — intend to be in that conversation.""",
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ARTICLE 2 — Intel Foundry Comeback / Google TPU / NVIDIA Evaluation
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel's Foundry Resurrection: Google's 3-Million-Chip Order and the NVIDIA Evaluation That Changed Everything",
        "subheadline": "A blockbuster TPU deal and Feynman GPU packaging talks mark Intel's return as a contract chipmaker — with implications for tens of thousands of Indian-origin engineers and the H-1B workforce that sustains it.",
        "slug": "intel-foundry-google-tpu-nvidia-feynman-evaluation-20260611",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 82,
        "tags": ["intel", "foundry", "google", "tpu", "nvidia", "feynman", "lip-bu-tan", "semiconductors", "h1b"],
        "urgency": "medium",
        "image_url": f"{IMAGE_BASE}/lip_bu_tan.jpg",
        "image_caption": "Lip-Bu Tan, CEO of Intel Corporation",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "diaspora_angle": "Intel employs tens of thousands of Indian-origin engineers across its US operations; the foundry's revival secures high-skilled roles at a time when H-1B holders face legislative headwinds.",
        "sources": json.dumps([
            {"name": "The Information via Stocktwits", "url": "https://stocktwits.com/news/intc-stock-is-soaring-today-what-is-the-googl-nvda-connection/b39c37f4"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/intels-stock-soars-as-the-companys-blue-chip-roster-of-customers-looks-to-be-growing-35e7d076"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/intel-stock-google-foundry-customer/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/google-nvidia-consider-intel-as-backup-chip-manufacturer-the-information-reports/article69671234.ece"}
        ]),
        "published_at": NOW,
        "body": """For the better part of a decade, Intel was the semiconductor industry's cautionary tale — the former king of chipmaking that lost its manufacturing edge, watched its stock languish, and ceded market after market to rivals running on TSMC-fabricated silicon. That narrative is now being rewritten at speed. On June 8, The Information reported that Alphabet's Google has ordered more than three million tensor processing units from Intel for production in 2028, while NVIDIA is evaluating Intel's advanced packaging technology for a future processor that would combine four graphics chips into a single unit. Intel stock surged 11 per cent on the day, its best performance of the year, and is now up 169 per cent year-to-date.

## The Google Deal

The TPU order is a landmark for Intel's foundry ambitions. Google's tensor processing units are custom-designed AI accelerators that power much of the company's internal machine learning infrastructure, from Search ranking to Gemini. Until now, TSMC manufactured all of Google's TPUs. But TSMC is capacity-constrained — demand from Apple, NVIDIA, AMD, and a growing roster of AI startups has stretched its fabs to the limit. Google spent months testing Intel's chip packaging technology before placing the order, according to people with direct knowledge of the discussions.

The deal validates Intel's 18A process node, the technology CEO Lip-Bu Tan has staked the company's future on. Intel will not fabricate the TPU wafers from scratch; the order centres on advanced packaging — the art of stacking and connecting multiple chiplets into a single, high-performance unit. But for a company that a year ago struggled to attract any third-party customers, landing Google is a proof point that the blue-chip market takes seriously.

## NVIDIA's Feynman Evaluation

Perhaps more intriguing is the NVIDIA angle. The Information reported that NVIDIA is assessing whether Intel can manufacture a processor for its next-generation Feynman GPU architecture — a design that combines four graphics chips into one package. No formal order has been placed, and NVIDIA's current production remains firmly with TSMC. But the evaluation alone signals that Jensen Huang's team sees Intel as a credible backup at a time when single-source dependency on TSMC carries geopolitical and capacity risk.

This follows a $5 billion equity investment NVIDIA made in Intel stock earlier this year, part of a broader partnership to develop AI infrastructure and custom x86 processors. The relationship has deepened quietly: Intel and NVIDIA have announced joint work on personal computing products, custom CPUs, and systems-on-chip.

## The Blue-Chip Roster

Intel's customer pipeline now reads like a who's who of global technology. Tesla's Elon Musk has tapped Intel's 14A node for his planned Terafab semiconductor complex in Texas. Apple has a manufacturing partnership. SoftBank has committed $2 billion. And Google's three-million-unit TPU order is the largest single foundry deal Intel has announced.

"One of the most advanced in-house AI chip programmes in the world seems willing to entrust its chip production to Intel," wrote Tigress Financial Partners analyst Ivan Feinseth. "That is highly validating for the company's ability to support large, complex designs at scale."

JPMorgan analysts offered a more cautious view, calling some of the packaging deals a "storm in a teacup" and noting that packaging revenue is a fraction of full foundry manufacturing. The distinction matters: Intel's path to genuine foundry scale requires winning not just packaging work but wafer fabrication contracts, where TSMC's lead remains formidable.

## What This Means for the Indian Diaspora

Intel is one of the largest employers of Indian-origin engineers in the United States. Its campuses in Santa Clara, Hillsboro, Chandler, and Austin house thousands of H-1B visa holders and green card applicants working on everything from chip design to process engineering. The company's revival is not an abstraction for this workforce — it is the difference between job security and another round of layoffs.

The timing carries extra weight. Just last week, a federal judge struck down the $100,000 fee on H-1B applications that would have disproportionately hit Indian IT workers. But legislative efforts to revive similar measures, including Rep. Mike Kennedy's PROTECT Act, remain active. A thriving Intel — hiring aggressively, winning major contracts, justifying its engineering headcount — strengthens the economic argument for the high-skilled immigration pipeline that Indian professionals depend on.

Intel also operates a major design centre in Bengaluru and has invested in R&D across Hyderabad and other Indian cities. A healthy foundry business in the US pulls demand through to Indian engineering teams that design verification IP, run simulations, and develop the software stack that customers need.

## The Road Ahead

Intel stock hit an all-time high of $132.75 on May 11 before pulling back, and the Google news sent it back toward those levels. But the company's foundry transformation is still early. Revenue was $13.58 billion in the first quarter — a sixth consecutive earnings beat — yet the foundry unit remains unprofitable. Converting a three-million-chip order into sustained manufacturing revenue by 2028 will require flawless execution on a process node that Intel has never mass-produced at scale.

For Lip-Bu Tan, who took the CEO role determined to restore Intel's manufacturing credibility, the Google deal is the strongest evidence yet that the market believes the comeback is real. For the Indian engineers whose careers are woven into Intel's fabric, it may matter even more.""",
    },

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ARTICLE 3 — NVIDIA Physical AI / Seoul Robotics Blitz
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang's Physical AI Offensive: Inside NVIDIA's Robotics Blitz Across Seoul",
        "subheadline": "From Boston Dynamics humanoids in Hyundai plants to LG's living-room robots, NVIDIA is building the platform layer for a post-screen world — and India's manufacturing ambitions should be paying attention.",
        "slug": "nvidia-physical-ai-robotics-seoul-hyundai-lg-boston-dynamics-20260611",
        "category": "technology",
        "vertical": "technology",
        "status": "review",
        "is_editorial": False,
        "score_total": 75,
        "tags": ["nvidia", "physical-ai", "robotics", "seoul", "hyundai", "lg", "boston-dynamics", "make-in-india"],
        "urgency": "medium",
        "image_url": f"{IMAGE_BASE}/jensen_huang.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang during his Seoul visit in June 2026",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "diaspora_angle": "India's push to become a global manufacturing hub under Make in India will increasingly depend on the kind of physical AI and industrial robotics platforms NVIDIA is building with Korean partners.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/sk-hynix-announces-multi-year-tech-deal-with-nvidia-ai-factories-2026-06-07/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/nvidia-strikes-deals-with-korean-tech-titans-for-ai-infrastructure-buildout-21a7cb38"},
            {"name": "Let's Data Science", "url": "https://letsdatascience.com/nvidia-partners-with-lg-on-humanoid-robots-data-centers/"},
            {"name": "KED Global", "url": "https://www.kedglobal.com/robotics/"}
        ]),
        "published_at": NOW,
        "body": """Jensen Huang did not come to Seoul to sell graphics cards. Over four days in early June, the NVIDIA chief executive met with the chairmen of SK Group, Hyundai Motor, LG, Doosan, and Naver — the five conglomerates that collectively anchor South Korea's industrial economy — and left behind a web of partnerships that reveal where NVIDIA believes the next trillion-dollar opportunity lies. Not in chatbots or image generators, but in physical AI: the application of large-scale machine intelligence to robots, vehicles, factories, and the built environment itself.

## The Hyundai Partnership

The centrepiece is Hyundai Motor Group. After meeting Executive Chair Euisun Chung, Huang announced that NVIDIA would deepen collaboration across autonomous mobility, industrial robotics, and AI-powered manufacturing. The language was deliberately broad, but the underlying ambition is concrete.

Boston Dynamics, a Hyundai affiliate, plans to deploy its Atlas humanoid robots across auto plants starting in 2028, with a target of 25,000 to 30,000 units produced annually. These are not demonstration prototypes. Hyundai intends to use its own manufacturing network to scale production — and NVIDIA's simulation platforms (Isaac for robotics, Omniverse for digital twins) will train the robots in virtual environments before they touch a real assembly line.

Huang referred to Hyundai's planned AI data centre in Saemangeum as an "AI Valley" comparable to Silicon Valley. "No one is in a better position to take advantage of that and to create that than Hyundai," he said. "I'm very excited to partner with Hyundai across all of these different areas of artificial intelligence — from mobility and robotics to AI factories."

The data dimension is equally significant. Analysts estimate that Hyundai's robot-equipped factories could generate a data stream worth $2.7 billion in annual profit potential — not from selling cars, but from monetising the operational intelligence that thousands of robots produce as they work.

## LG and the Living Room

With LG Group Chairman Koo Kwang-mo, Huang's focus shifted from factory floors to domestic spaces. NVIDIA is partnering with LG on motor technology, mechanical systems, and the AI stack for humanoid robots — a collaboration that builds on LG's CLOi home robot, already running on NVIDIA's Jetson Thor platform and demonstrated at CES 2026.

The partnership extends to data centre architecture. LG is moving to internalise server cooling and infrastructure components, and the two companies are jointly designing next-generation data centres including power delivery and cooling systems. It is a recognition that as AI models grow, the physical infrastructure to run them becomes as important as the silicon inside.

## Doosan, Naver, and the National AI Stack

The Seoul blitz extended further. Doosan Group, which manufactures materials used in NVIDIA's Blackwell chips and is developing its own robotics programme, will use NVIDIA's physical AI technology across its energy and industrial divisions. SK Telecom announced plans for a gigawatt-scale AI cloud in South Korea using NVIDIA technology, with the first data centre online by 2027. Naver, the country's dominant internet platform and developer of a homegrown large language model, will collaborate on AI factories and explore joint entry into European and Middle Eastern AI markets.

South Korea's government is also buying in directly. The tech ministry plans to procure 9,704 GPUs for a state AI project worth 2.08 trillion won ($1.5 billion) in 2026, including 2,016 of NVIDIA's upcoming Vera Rubin GPUs — the first confirmed sovereign purchase of the next-generation platform.

## Why India Should Be Watching

The Seoul deals sketch a blueprint for what industrial AI adoption looks like at national scale: government procurement of frontier GPUs, conglomerate-level robotics deployment, sovereign AI clouds, and a coordinated push to embed intelligence into manufacturing.

India's ambitions overlap significantly. The Make in India programme aims to position the country as a global manufacturing hub. Tata Electronics is building semiconductor fabs. Foxconn, Pegatron, and other contract manufacturers are expanding Indian operations. Yet India's industrial robotics density remains among the lowest of any major economy — roughly 5 robots per 10,000 manufacturing workers, compared with South Korea's world-leading 1,012.

The gap is not merely about hardware procurement. It is about the platform layer — the simulation tools, the digital twin environments, the training pipelines — that turn a factory into an intelligent system. NVIDIA is building that layer with Korean partners because Korea's conglomerates have the scale, the manufacturing depth, and the willingness to invest. India's conglomerates — Tata, Reliance, Mahindra, Adani — have announced comparable ambitions, but the platform partnerships to execute them remain thin.

For the Indian diaspora in technology, the Seoul blitz is a signal worth decoding. The Indian-origin engineers who build NVIDIA's Isaac and Omniverse platforms, who design autonomous systems at Hyundai's California R&D centres, and who develop robotics software at startups across the Bay Area are shaping the tools that will determine which countries capture the physical AI opportunity. Whether India is among them depends on decisions being made now — not in Seoul, but in boardrooms in Mumbai, Bengaluru, and New Delhi.""",
    },
]

# ── Insert ───────────────────────────────────────────────────────────────
url = f"{SUPABASE_URL}/rest/v1/p2_articles"

for a in articles:
    print(f"\n{'='*60}")
    print(f"Inserting: {a['headline'][:70]}...")
    print(f"  slug: {a['slug']}")
    
    resp = requests.post(url, headers=HEADERS, json=a, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        row = data[0] if isinstance(data, list) else data
        print(f"  ✅ Inserted — id: {row.get('id', 'ok')}")
    else:
        print(f"  ❌ Failed ({resp.status_code}): {resp.text[:200]}")

print(f"\n{'='*60}")
print("Done. All articles inserted with status='review'.")
