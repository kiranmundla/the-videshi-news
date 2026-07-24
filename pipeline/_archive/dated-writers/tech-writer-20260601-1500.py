#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-01 15:00 UTC run"""
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
    # ── Article 1: Intel 18A Clearwater Forest ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Just Shipped Its Most Advanced Chip Ever. Nobody Noticed.",
        "subheadline": "The Clearwater Forest Xeon 6+ is built on 18A — the first 2nm-class processor manufactured in the United States. But Jensen Huang stole the show.",
        "slug": make_slug("intel-clearwater-forest-18a-xeon-computex-overshadowed"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Intel employs tens of thousands of Indian engineers across its Bangalore R&D campus and US design centres. Its Odisha substrate investment and the 18A manufacturing revival directly shape career trajectories and India's semiconductor ambitions.",
        "tags": ["intel", "semiconductor", "18a", "computex-2026", "xeon", "indian-engineers"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WCCFTech", "url": "https://wccftech.com/intel-288-core-clearwater-forest-xeon-6-plus-lands-on-18a-claiming-30-percent-performance-lead-over-amd-192-core-epyc/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-launches-new-chip-bring-ai-directly-personal-computers-2026-06-01/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/06/01/intel_diamond_rapids/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-rtx-spark-chip-intel-amd-stock-price-today-fda59c51"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Intel chose the worst possible Monday to launch the most important chip it has built in a decade.

At Computex 2026 in Taipei, the company unveiled Clearwater Forest — the Xeon 6+ E-core processor that packs 288 efficient cores into a single socket and is built on Intel 18A, a 2nm-class process node manufactured at the company's Fab 52 in Chandler, Arizona. It is the first data centre processor at this node to be fabricated entirely in the United States.

The chip claims a 30 per cent per-thread performance advantage over AMD's 192-core EPYC 9965 and up to 30 per cent better power efficiency. Intel says it achieves a 17 per cent improvement in instructions per cycle over its predecessor, Sierra Forest, along with five times more last-level cache and 25 per cent faster memory support. Supermicro, one of Intel's closest server partners, has already announced 12 new platforms built around the chip, offering up to 576 cores per dual-socket server.

## The Problem With Timing

None of that mattered on Monday morning. Hours before Intel's server announcement, Jensen Huang walked onto a stage two kilometres away and unveiled RTX Spark — Nvidia's first consumer PC processor, built on ARM architecture with MediaTek and Microsoft. Huang called x86 architecture "obsolete." Intel's stock dropped 5 to 6 per cent in pre-market trading. AMD fell nearly 4 per cent. Qualcomm lost 9 per cent.

The irony is brutal. Intel's 18A is arguably the most significant American semiconductor manufacturing achievement since TSMC began pulling ahead in the mid-2010s. RibbonFET gate-all-around transistors and PowerVia backside power delivery are genuine technical innovations. But the market priced in Nvidia's narrative — the AI PC, agentic computing, the end of the traditional CPU — before Intel could finish its presentation.

Independent analyst Richard Windsor put it plainly: "Intel's x86 architecture was effectively called out as obsolete in both the data centre and the PC, both of which are Intel's core markets."

## What Indian Engineers Should Know

Intel employs an estimated 30,000-plus engineers in India, with its Bangalore campus serving as one of the company's largest design and validation centres globally. Teams there have worked on successive Xeon generations, including validation for Clearwater Forest's 18A process. A successful 18A ramp matters directly to those careers — it validates Intel's manufacturing comeback narrative and secures the design pipeline for Diamond Rapids (Xeon 7, due 2027, on refined 18A-P) and Coral Rapids after that.

Intel's $3.3 billion substrate investment in Odisha, announced earlier this year, is a separate but parallel bet on India's role in semiconductor packaging. If 18A delivers on its promises, more of the production ecosystem flows toward India.

For Indian engineers working at Intel in the United States, the stock price whiplash is personal. Intel is up 211 per cent year-to-date — a staggering recovery from its 2024-2025 nadir. Monday's drop is noise against that trend, but the existential question remains: can Intel stay relevant in a world where Nvidia defines the architecture conversation?

## The Bigger Picture

Intel teased Diamond Rapids at Computex — 192 P-cores on 18A-P, dropping Hyperthreading entirely (though it returns in Coral Rapids). AMD is preparing its 256-core Venice EPYC on TSMC 2nm. The server market is fragmenting into efficiency cores, performance cores, and GPU-centric compute, with each vendor claiming a different sweet spot.

For the Indian diaspora watching this from both sides of the Pacific — working at Intel in Santa Clara or Bangalore, investing in chip stocks, or following India's fab ambitions — the Clearwater Forest launch is a technical milestone worth noting. It just had the misfortune of sharing a news cycle with the loudest man in semiconductors."""
    },

    # ── Article 2: Anthropic $965B valuation ────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Is Now Worth More Than OpenAI. Its CFO Is Indian-Origin. Its IPO May Be Months Away.",
        "subheadline": "A $65 billion Series H values the Claude maker at $965 billion. For NRI investors and AI professionals, the real question is what happens in October.",
        "slug": make_slug("anthropic-965-billion-valuation-krishna-rao-ipo-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Anthropic's CFO Krishna Rao is of Indian origin. The company just expanded into Bengaluru. An October IPO would be the first trillion-dollar AI listing — directly relevant to NRI investors, Indian AI researchers considering offers, and the diaspora professionals building on Claude.",
        "tags": ["anthropic", "ai", "ipo", "valuation", "krishna-rao", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fast Company", "url": "https://www.fastcompany.com/91355230/anthropic-just-topped-openai-on-a-major-metric-ahead-of-rival-ipos"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/anthropic-surges-to-965-billion-as-ai-funding-hits-new-stratosphere/"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/anthropic-is-now-worth-more-than-openai/"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/05/anthropic-valuation-965b-ai-complexity-india"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/14314636/pexels-photo-14314636.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Five years ago, Anthropic did not exist. Last week, it raised $65 billion in a single funding round and became the most valuable AI company on the planet.

The Series H, announced on May 28, values the San Francisco-based maker of Claude at $965 billion post-money — leapfrogging OpenAI's $852 billion and placing Anthropic within striking distance of a trillion-dollar valuation. The round was led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital, with strategic participation from Amazon ($5 billion of a $15 billion hyperscaler commitment), Google, Broadcom, SpaceX, and memory giants Micron, Samsung, and SK hynix.

The numbers are staggering even by AI industry standards. Anthropic's annualised run-rate revenue crossed $47 billion in May — nearly doubling from its February rate and almost twice OpenAI's reported $25 billion. In just three months, the company has nearly tripled its valuation from $380 billion at its Series G close.

## Why NRI Investors Should Pay Attention

This is widely expected to be Anthropic's final private round before an October 2026 IPO. If that timeline holds, it would be the largest technology listing since Meta's 2012 debut — and the first by an AI-native company at this scale.

For Indian-American investors, the IPO presents both opportunity and caution. The opportunity: Anthropic is growing revenue faster than any enterprise software company in history, with Claude embedded in core operations across Fortune 500 companies. The caution: profitability remains unproven at scale. The company turned an operating profit for one quarter, but as the Wall Street Journal noted, it is unclear what accounting methods were used, and Anthropic has committed hundreds of billions in compute spending over the next decade — $1.5 billion per month to SpaceX alone, plus massive commitments to AWS, Google Cloud, and Broadcom.

Krishna Rao, Anthropic's Chief Financial Officer, is of Indian origin and has been the public voice of the company's financial strategy. "Claude is increasingly indispensable to our growing global community of customers," Rao said in the funding announcement. "This funding will help us serve the historic demand we are experiencing."

## The India Angle Goes Deeper

Anthropic's Bengaluru expansion, announced just days ago, signals more than token presence. The company is actively hiring AI researchers and enterprise sales teams in India, where Claude's enterprise business has already doubled. For Indian engineers weighing offers from Google, Microsoft, and OpenAI, an Anthropic pre-IPO equity package now carries a different calculus — if the October listing lands near a trillion-dollar valuation, early employees stand to see significant returns.

The broader context matters too. Indian IT services companies — TCS, Infosys, Wipro, Cognizant — are all rushing to build AI practices around foundational models. Claude is emerging as a preferred choice for enterprise deployments where safety and reliability matter. Anthropic's new Claude for Small Business package, launched earlier this month, automates payroll, invoicing, and content strategy — precisely the kind of workflow that Indian IT companies resell to global clients.

## What the Valuation Really Means

Critics, including HSBC analysts and prominent tech commentator Ed Zitron, have questioned whether AI companies can sustain these valuations. The compute costs are enormous, the competitive moat is unclear (OpenAI, Google DeepMind, and Meta AI are all capable), and the revenue growth, while explosive, depends on enterprise customers continuing to expand their AI budgets at current rates.

But the market has made its bet. Anthropic's investor list — spanning sovereign wealth funds (GIC, Temasek), private equity (Blackstone, Brookfield), and the world's largest technology companies — represents a broad consensus that Claude's trajectory justifies near-trillion-dollar pricing.

For the Indian diaspora professional community — whether you are an engineer evaluating an offer, an investor watching the IPO calendar, or a founder building on Claude's API — October 2026 is now a date worth circling."""
    },

    # ── Article 3: Indian Startup Funding Drought ───────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Startups Raised $66 Million Last Week. Anthropic Raised $65 Billion. Read That Again.",
        "subheadline": "The last week of May was the worst for Indian startup funding in 2026. The gap with global AI companies is no longer a gap — it is a chasm.",
        "slug": make_slug("indian-startup-funding-drought-66-million-anthropic-gap"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI founders debating whether to build in India or the US face a stark funding reality. Indian investors are sitting out the AI wave. For diaspora professionals sending capital or talent back home, the structural deficit in Indian AI requires honest assessment.",
        "tags": ["indian-startups", "funding", "venture-capital", "ai-gap", "nri-founders"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/05/weekly-funding-roundup-may-25-31-vc-inflow-drops-lowest-2026"},
            {"name": "LinkedIn / GrowthList", "url": "https://www.linkedin.com/pulse/startup-venture-capital-report-usa-canada-india-may-25-31-2026"},
            {"name": "Inc42", "url": "https://inc42.com/features/union-budget-2026-ai-platforms-startups/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6913351/pexels-photo-6913351.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Here is a number that should keep every Indian tech founder awake at night: between 2022 and May 2026, the entire Indian startup ecosystem raised approximately $62 billion. In a single transaction last week, Anthropic raised $65 billion.

One company. One round. More than four years of Indian startup funding combined.

The comparison is not entirely fair — Anthropic is arguably the most aggressively funded private company in history, operating in a sector experiencing unprecedented capital inflows. But it illustrates a structural reality that the Indian tech ecosystem has been slow to confront: the country has no credible contender in the global AI race, and the funding drought is making it harder to build one.

## The Numbers Are Grim

Data compiled by YourStory shows that Indian startups raised just $66 million across 16 transactions in the last week of May 2026. It was the lowest weekly total of the year and the fifth time weekly funding dropped below $100 million. Not a single deal exceeded $15 million.

This is not a cyclical blip. It reflects a structural capital migration toward AI-native companies, almost all of which are based in the United States. Anthropic's $965 billion valuation, OpenAI's $852 billion, and Cognition's $26 billion (for an AI coding startup with $492 million in annual revenue) are pulling institutional capital into a narrow set of bets — bets that Indian companies are not part of.

The bright spots are narrow. C2i Semiconductors raised $16.7 million (led by TDK Ventures) for an AI power chip. StrainX Bioworks secured $13 million from IIT Delhi for precision fermentation. Fairdeal.Market raised $15 million for B2B quick-commerce. These are real companies solving real problems, but none operates at the frontier-model scale that commands ten-figure cheques.

## Why This Matters for the Diaspora

For NRI founders weighing whether to start their next company in Bangalore or San Francisco, the funding gap is a practical constraint, not just an abstract metric. An AI startup in the Bay Area can raise a $50 million Series A on a strong demo and a credible team. The same team in Bangalore might struggle to close $5 million.

The talent pipeline compounds the problem. India produces 1.5 million engineers annually, but the top AI researchers — the ones training frontier models and publishing at NeurIPS and ICML — are overwhelmingly at American labs. Google DeepMind, OpenAI, Anthropic, and Meta AI employ significant numbers of Indian-origin researchers, but that talent creates value in the US, not in India.

India's government-backed IndiaAI Mission has expanded GPU capacity from 10,000 to 38,000, and platforms like AIKosh host over 5,500 datasets. Sarvam AI and Krutrim are building multilingual models. But the scale gap is enormous — Anthropic alone has committed 10 gigawatts of compute across Amazon, Google, Broadcom, and SpaceX. India's entire AI compute infrastructure would not fill one of those contracts.

## The Profitability Counter-Narrative

There is a silver lining, though it requires squinting. Several Indian startups turned profitable in recent months — Cashfree achieved EBITDA positivity, Pepperfry posted its first-ever profit, PhysicsWallah grew revenue 50 per cent, and Kissht expanded 52 per cent. Indian startups may not be raising billions, but some are learning to survive without it.

Meanwhile, 120 Indian deeptech startups will travel to Nice, France in mid-June for Bharat Innovates 2026, coinciding with Prime Minister Modi's visit. The event covers AI, healthcare, aerospace, biotech, and agritech — a showcase of India's emerging innovation ecosystem, even if the cheque sizes trail the rhetoric.

## The Honest Assessment

India's startup ecosystem is not dying — it is being eclipsed. The global capital cycle has pivoted to AI, and India does not have a company that can absorb or justify that capital at scale. The $66 million weekly total is not evidence of failure; it is evidence of a market that has not yet produced its Anthropic, its OpenAI, or even its Cognition.

For NRI investors, the implication is uncomfortable but clear: the highest-returning AI bets are in the US, and the Indian ecosystem needs patient, strategic capital — not just cheerleading — if it is ever going to close the gap."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
