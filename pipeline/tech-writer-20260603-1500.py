#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-03 15:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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
    # ─────────────────────────────────────────────────────
    # ARTICLE 1: India IT Stocks Crash
    # Beat: B (Top Employers) + C (Indian Tech Ecosystem)
    # ─────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Lost 9 Per Cent in a Single Day. The Market Is Pricing in the End of Indian IT as We Know It.",
        "subheadline": "India's Nifty IT index suffered its worst session in four months as analysts warned that AI-driven deflation could permanently shrink the $300 billion outsourcing industry's addressable market by a quarter.",
        "slug": make_slug("tcs-nifty-it-crash-ai-disruption-outsourcing"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian IT stocks are among the most widely held equities in NRI portfolios. TCS, Infosys and Wipro collectively employ over a million people, many of them on cross-border assignments. A structural decline doesn't just hit stock returns — it reshapes career trajectories for an entire generation of Indian tech workers in the US and India alike.",
        "tags": ["tcs", "infosys", "wipro", "indian-it", "ai-disruption", "nifty-it", "stock-market"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg",
        "body": """The numbers arrived like a verdict. Tata Consultancy Services, India's largest software exporter and the flagship stock of its $300 billion IT industry, fell 8.95 per cent on Wednesday to close at Rs 2,229 — its sharpest single-day decline in months. LTIMindtree dropped over 8 per cent. Infosys lost 4.3 per cent, HCL Technologies 5 per cent, Tech Mahindra nearly 6 per cent. Coforge and Persistent Systems each shed close to 6 per cent. By the close of trading, the Nifty IT index had fallen 5.8 per cent to 29,301 points, its worst session since February.

The rout erased three days of gains in a single afternoon.

## What Triggered the Selloff

The proximate cause was profit-booking after a short-lived rally that had lifted the IT index roughly 7 per cent over the previous three sessions. Investors had briefly bought into beaten-down IT names, betting that AI spending might generate fresh demand for Indian services firms. That optimism evaporated on Wednesday.

But the underlying cause runs deeper. The selloff coincided with a broad correction in global software stocks. In the US, the iShares Expanded Tech-Software Sector ETF declined 3 per cent. Atlassian fell 8 per cent. HubSpot, Okta and ServiceNow each dropped 6 to 7 per cent. Accenture, the closest global analogue to Indian IT services firms, slid 7 per cent intraday to $183.41. The American Depository Receipts of Infosys and Wipro had already fallen as much as 8 per cent on Wall Street before Indian markets opened.

The message from multiple brokerages was blunt. Kotak Institutional Equities, led by analyst Kawaljeet Saluja, wrote that while opportunities like legacy modernisation would grow, "we do not expect them to compensate for the deflation enough." Ambit Capital was even more direct: "We believe deflation will exceed incremental demand." Rishubh Vasa at Indsec Securities estimated that the total addressable market for Indian IT companies could shrink by 20 to 25 per cent.

## The AI Arithmetic Problem

The core anxiety is structural, not cyclical. India's IT services industry was built on one premise: that it was cheaper to have an Indian engineer in Bangalore or Hyderabad write code, test software and manage systems than to hire locally in New York or London. That arbitrage powered three decades of growth, created millionaires at scale, and turned TCS, Infosys and Wipro into household names in every Indian city with an engineering college.

Artificial intelligence is now compressing that arbitrage from the other direction. When global banks like HSBC, Citi and NatWest are reporting "significant improvements in coding productivity" through agentic AI tools — as Kotak's latest sector note documented — the question is no longer whether AI will affect Indian IT, but how fast. Every percentage point of productivity gained by an AI copilot is a percentage point of billable hours that never gets staffed.

The Nifty IT index has now fallen 22 per cent in 2026, following a 26 per cent decline in 2025. That is a cumulative destruction of nearly half the sector's market capitalisation in under two years.

## Why NRIs Should Pay Attention

For Indian Americans, this isn't just a market story. It is a structural question about the industry that brought many of them to the United States in the first place. TCS, Infosys and Wipro remain among the largest sponsors of H-1B and L-1 visas. A sustained contraction in their US operations would mean fewer visa slots, fewer rotational assignments and a narrower pipeline for the kind of global mobility that has defined Indian tech careers for a generation.

On the investment side, Indian IT stocks have long been considered defensive blue chips in NRI portfolios. TCS alone was once valued at a premium to the broader Nifty 50. It now trades at a 30 per cent discount to its historical price-to-earnings ratio, according to analysts at Bonanza. The question every NRI investor faces: is that a buying opportunity, or a value trap in a structurally declining industry?

Nitant Darekar at Bonanza framed the dilemma precisely: "Valuations at a 30 per cent discount to historical P/E offer comfort, but a durable re-rating needs demand recovery — not just AI optimism."

The Indian IT industry has reinvented itself before — from Y2K remediation to dotcom services to cloud migration. Whether it can reinvent itself again around AI, rather than be consumed by it, may be the most consequential question in Indian technology this decade. Wednesday's market offered its preliminary assessment. It was not encouraging."""
    },

    # ─────────────────────────────────────────────────────
    # ARTICLE 2: NVIDIA-TSMC AI in Fabs
    # Beat: D (Semiconductor/AI)
    # ─────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "NVIDIA Is Now Using AI to Make the Chips That Run AI. TSMC's Fabs Are the First Proving Ground.",
        "subheadline": "At GTC Taipei, Jensen Huang revealed that TSMC is deploying NVIDIA's CUDA-X libraries across lithography, simulation and defect detection — cutting cycle times by up to 50 per cent and chemistry simulations by 50x.",
        "slug": make_slug("nvidia-tsmc-ai-fabs-culitho-cuda-x-gtc-taipei"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian semiconductor engineers are among the largest cohorts at both NVIDIA and TSMC's partner firms. As India builds its own fabs in Dholera and Gujarat, the NVIDIA-TSMC playbook for AI-powered manufacturing is precisely the technology those facilities will need to be competitive.",
        "tags": ["nvidia", "tsmc", "semiconductor", "ai-manufacturing", "culitho", "gtc-taipei", "india-semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "NVIDIA / GlobeNewswire", "url": "https://www.globenewswire.com/"},
            {"name": "Manufacturing Digital", "url": "https://manufacturingdigital.com/"},
            {"name": "Business 2.0 News", "url": "https://business20channel.tv/"},
            {"name": "Investing News", "url": "https://investingnews.com/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Building_of_Taiwan_Semiconductor_Manufacturing_Fab_12B_at_dusk1.jpg/1280px-Building_of_Taiwan_Semiconductor_Manufacturing_Fab_12B_at_dusk1.jpg",
        "body": """The recursion is now complete. The company that makes the most important chips for artificial intelligence is using artificial intelligence to make those chips better. At NVIDIA's GTC Taipei conference on 1 June, Jensen Huang and TSMC chairman C.C. Wei announced that TSMC is deploying NVIDIA's accelerated computing and AI tools across its most advanced semiconductor fabrication facilities — from the lithography machines that print transistors to the scheduling systems that optimise entire fabs.

The announcement marks the most concrete public evidence yet that AI has moved from designing chips to manufacturing them.

## What TSMC Is Actually Using

The deployment spans six distinct NVIDIA technologies, each targeting a different bottleneck in the chipmaking process.

**Computational lithography** uses NVIDIA's cuLitho library. Lithography — the process of projecting circuit patterns onto silicon wafers using light — is the most computationally intensive step in chipmaking. TSMC reports that cuLitho delivers a 20 to 50 per cent improvement in either cost-effectiveness or cycle time compared with CPU-based computation. For an industry where a single fab costs $20 billion and runs 24 hours a day, shaving even 20 per cent off lithography turnaround is not a marginal improvement. It is a competitive weapon.

**Transistor and process simulation** uses cuEST, a GPU-accelerated electronic structure simulation library. The result: chemistry simulations for material design that run approximately 50 times faster than their CPU equivalents. When engineers are testing how new materials will behave at the 2-nanometre node, a 50x speedup means the difference between exploring five candidates and exploring two hundred.

**Advanced process control** relies on cuML, NVIDIA's machine learning library, to accelerate the large-scale analytics that keep fab yields high. **Fab scheduling** uses raw CUDA acceleration to optimise the movement of thousands of wafer lots through hundreds of processing steps. **Defect inspection** employs NVIDIA Metropolis and the TAO Toolkit for vision AI, detecting nanometre-scale defects that would otherwise require repeated manual labelling and retraining cycles.

The sixth technology — NVIDIA Omniverse, used to build a "FabTwin" digital replica of the physical fab — remains exploratory. But the other five are in production.

## The India Connection

This matters for India on two levels.

First, Indian engineers are deeply embedded in both companies' workforces. NVIDIA's engineering teams in Bangalore and Hyderabad work on CUDA libraries and AI infrastructure. TSMC's design partners — including Qualcomm, MediaTek and Broadcom — employ thousands of Indian chip designers. The tools TSMC is adopting are, in many cases, tools that Indian engineers helped build.

Second, India is about to become a chip manufacturer. The Tata Electronics fab in Dholera, Gujarat, is under construction and expected to begin production in the next few years. Micron's Gujarat facility is building memory packaging capacity. The India Semiconductor Mission has committed billions of dollars to make India a credible node in the global semiconductor supply chain. Last week, India and the United States signed a semiconductor partnership pact.

None of these facilities will be competitive if they rely on the CPU-based manufacturing tools that defined chipmaking a decade ago. The NVIDIA-TSMC partnership is effectively writing the operating manual for how modern fabs will run. India's fabs will either adopt this playbook or start behind.

## Why It Matters Beyond the Fab

"NVIDIA and TSMC have worked together for nearly three decades to push the limits of computing," Huang said at the announcement. "TSMC is bringing NVIDIA AI and accelerated computing into the fab itself."

C.C. Wei's framing was more revealing: "By using NVIDIA accelerated computing and AI across fab operations, TSMC is strengthening our technology leadership and manufacturing excellence to support our customers' future products and success."

The subtext is competitive. Samsung, Intel and SMIC are all investing in AI-accelerated manufacturing. The question is no longer whether AI will transform how chips are made, but who gets there first — and whether India's nascent semiconductor ambitions can keep pace with a manufacturing revolution that is already under way in Taipei."""
    },

    # ─────────────────────────────────────────────────────
    # ARTICLE 3: Alphabet $80B Equity Raise
    # Beat: A (Sundar Pichai/Alphabet)
    # ─────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai's Alphabet Just Sold $80 Billion in Stock. It Still Won't Be Enough.",
        "subheadline": "Google's parent company tapped public equity markets for the first time since its 2004 IPO, with Berkshire Hathaway buying $10 billion of the offering. The money funds a $190 billion AI infrastructure buildout that even Alphabet's enormous cash flow cannot cover.",
        "slug": make_slug("alphabet-80-billion-equity-raise-ai-capex-berkshire"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai is leading the largest corporate capital raise of the AI era. For the tens of thousands of Indian engineers at Google's offices in Mountain View, Hyderabad and Bangalore, this $190 billion buildout will define the next decade of their careers. For NRI investors holding GOOGL, the calculus between dilution and growth just got more urgent.",
        "tags": ["alphabet", "google", "sundar-pichai", "ai-infrastructure", "berkshire-hathaway", "capex", "equity-offering"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Barron's", "url": "https://www.barrons.com/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
            {"name": "GSMArena", "url": "https://www.gsmarena.com/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "body": """Alphabet Inc. has not sold new shares to the public since August 2004, when two Stanford graduate students took their search engine public at $85 a share. Twenty-two years later, Sundar Pichai's company is going back to equity markets — this time for $80 billion, in what may be the largest corporate capital raise in history. The reason is as simple as it is staggering: Google is spending so much money on artificial intelligence that even its own cash machine cannot keep up.

The announcement, made Monday evening, sent Alphabet shares down roughly 2 per cent in after-hours trading. Investors are weighing the dilution. But the more consequential number is the one that forced the raise in the first place: Alphabet now expects to spend between $180 billion and $190 billion on capital expenditures in 2026. That figure will, in the company's own words, "significantly increase" in 2027.

## The Structure of an Unprecedented Raise

The $80 billion breaks into three tranches. Roughly $30 billion comes through concurrent underwritten offerings of Class A and Class C shares, plus mandatory convertible preferred stock. Another $40 billion will flow via an at-the-market programme beginning in the third quarter, primarily to cover tax obligations as employee equity awards vest. The remaining $10 billion is a private placement from Berkshire Hathaway, Warren Buffett's conglomerate, which is buying half in Class A shares at $351.81 and half in Class C at $348.20 — a 6.5 per cent discount to Monday's closing prices.

Berkshire already held approximately $16.6 billion in Alphabet stock before this deal. The private placement will increase its holding by roughly 49 per cent. For a conglomerate that historically avoided technology investments, the scale of commitment is a signal. One analyst called it "an ideal long-term shareholder endorsement."

## Why Cash Alone Won't Do

Alphabet generated strong operating cash flow last year — Wall Street estimates roughly $214 billion for 2026. But subtract a $10 billion annual dividend, and the remaining cash barely covers $190 billion in capex. The company has already borrowed over $85 billion across six currencies since May 2025. Its total debt now exceeds $100 billion, up from $28 billion just fourteen months ago. It has also issued a 100-year bond — one of only a handful ever sold by a technology company.

Last quarter, Alphabet did not buy back any shares for the first time since 2017. The suspension of buybacks, combined with the equity raise, tells a clear story: every available dollar is being redirected toward AI infrastructure.

The company's official statement framed it as demand-driven: Google is experiencing "strong demand for its AI solutions and services from enterprises and consumers, at levels that are exceeding the company's available supply." The $80 billion will "expand its foundational infrastructure to support the significant growth opportunity ahead."

## The Bigger Picture: $750 Billion and Counting

Alphabet is not alone. In 2026, five companies — Alphabet, Microsoft, Amazon, Meta and Oracle — will collectively spend approximately three-quarters of a trillion dollars on AI data centres. That figure exceeds the GDP of most countries. It represents a bet that artificial intelligence will generate returns large enough to justify infrastructure spending on a scale previously reserved for nation-states building railways and power grids.

https://x.com/sundarpichai/status/1929685453627801845

For Alphabet specifically, the spending funds the compute that powers Gemini (its flagship AI model family), Google Cloud's enterprise AI products, YouTube's recommendation and content systems, and the custom Tensor Processing Units that Broadcom designs for Google — now in their eighth generation.

## What This Means for Indian Engineers and NRI Investors

Sundar Pichai, born in Chennai and educated at IIT Kharagpur, is now overseeing the largest infrastructure investment in his company's history. For the estimated 30,000-plus Indian engineers at Google's offices across Mountain View, New York, Hyderabad and Bangalore, this spending translates directly into the projects they will work on for the next five to ten years. Google's Hyderabad campus — already its largest outside the US — is likely to see further expansion as the company scales AI operations.

For NRI investors, the calculus is more nuanced. The $80 billion equity raise dilutes existing shareholders. Alphabet stopped buying back stock. Debt has ballooned. But revenue grew 22 per cent year-on-year to $110 billion in the first quarter, Google reached 350 million paid subscriptions, and Berkshire Hathaway's participation suggests the smartest capital allocator in American history sees long-term value in Google's AI bet.

The question for every Indian American holding GOOGL in their portfolio is the same question facing Pichai himself: whether $190 billion a year in AI spending is an investment in the future or a leap of faith. The answer will define Silicon Valley's next decade — and the careers of the Indian engineers building it."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
