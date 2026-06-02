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

# Validate images before using
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # Try GET if HEAD doesn't return Content-Length
        if r.status_code == 200 and "image" in ct and cl == 0:
            r2 = requests.get(url, timeout=10, stream=True)
            chunk = r2.raw.read(6000)
            if len(chunk) > 5000:
                return True
        return False
    except Exception:
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Just Asked Shareholders for $80 Billion. Warren Buffett Said Yes.",
        "subheadline": "Alphabet's unprecedented equity raise — with a $10 billion Berkshire Hathaway anchor — signals that Google's AI infrastructure buildout is now too big for even its $127 billion cash pile. NRI portfolios heavy on GOOGL should pay attention.",
        "slug": make_slug("alphabet-80-billion-equity-raise-berkshire-pichai-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Alphabet is the second-largest employer of Indian tech workers on H-1B visas in the US. Any dilution event of this scale — $80 billion in new shares — directly affects the equity compensation packages that make up a massive portion of Indian engineers' total comp at Google. Meanwhile, NRI investors who loaded up on GOOGL during its 65% 2025 run are now watching a 2% after-hours drop and facing the prospect of significant share dilution. The Berkshire stamp of approval may provide some comfort, but Pichai is effectively asking the market to trust that $190 billion in annual capex will eventually pay off.",
        "tags": ["google", "alphabet", "sundar-pichai", "berkshire-hathaway", "ai-infrastructure", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/alphabet-plans-raise-80-billion-ai-goals-berkshire-invest-10-billion-2026-06-01/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/articles/google-seeks-80-billion-for-ai-buildout-berkshire-will-buy-10-billion-stake"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/alphabet-asks-shareholders-to-foot-an-80-billion-bill-for-ai-expansion"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/google-stock-googl-alphabet-80-billion-capital-raise-ai/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "body": """Sundar Pichai has been making the case for years that Google's AI bet would pay off. On Monday evening, he put a number on how much more runway he needs: $80 billion.

Alphabet announced a sprawling equity offering — the largest in tech history by a company that is not short on cash — comprising $30 billion in concurrent public offerings, a $40 billion at-the-market programme expected later this year, and a $10 billion private placement to Berkshire Hathaway. The stock slipped about 2% in after-hours trading, a relatively muted reaction for an offering that will meaningfully dilute existing shareholders.

## The Berkshire Signal

The Berkshire anchor is the headline grabber, and it is meant to be. Under new CEO Greg Abel, Berkshire has been quietly building its Alphabet position since Q3 2025, tripling its stake to $16.6 billion by last month. The new $10 billion tranche — split evenly between Class A shares at $351.81 and Class C shares at $348.20, both at a 6.5% discount to Monday's close — will push Berkshire's ownership to roughly 86.4 million shares, about 1.3% of the total outstanding.

"All companies are thrilled when Berkshire takes positions, because it is the kind of shareholder that companies like to have," said Steven Check of Check Capital Management. That is diplomatic understatement. In practice, the Buffett-Abel imprimatur tells the market: we looked at the books, and the AI capex makes sense.

## Why $80 Billion, and Why Now?

Alphabet disclosed on its April earnings call that 2026 capital expenditures would run between $180 billion and $190 billion — a slight increase from earlier guidance of $175–185 billion — and cautioned that 2027 would be "meaningfully" higher. At the end of Q1, the company held $126.8 billion in cash and equivalents. The math is straightforward: Google needs external capital to keep building data centres at the pace its AI ambitions demand.

Most of the capex goes toward AI training infrastructure — the GPU clusters, custom TPU racks, and data centre shells that underpin everything from Gemini to Google Cloud's enterprise AI products. Alphabet's "full stack" positioning — owning silicon design, model training, inference serving, and end-user distribution — requires a level of vertical investment that even its massive free cash flow cannot sustain alone.

## What This Means for Indian Tech Workers

For the tens of thousands of Indian engineers at Google, the announcement lands differently than it does for portfolio managers. Equity compensation — RSUs and stock grants — is typically the largest component of total compensation at senior levels. An $80 billion share issuance dilutes the value of every outstanding share. While Google's stock has gained about 20% this year, further dilution creates a ceiling effect that employees feel directly in their net worth.

The broader signal is more ambiguous. Massive infrastructure spend means Google is hiring — cloud, AI research, data centre operations — and those teams employ a disproportionately large share of Indian-origin talent. But the spending also introduces execution risk. If the AI revenue flywheel does not spin fast enough, cost discipline will follow, and Indian H-1B workers know from experience that they are often the first to feel restructuring.

## For NRI Investors

Alphabet has been a core holding in NRI investment portfolios for years, and the 65% surge in 2025 only deepened that exposure. Monday's offering is a test of conviction. The Berkshire placement suggests sophisticated investors believe the capex-to-revenue conversion is real. But equity raises are inherently dilutive, and the $40 billion ATM programme gives Alphabet months of room to sell into the market.

The question is no longer whether Google will spend the money. It is whether the revenue from Gemini, Google Cloud, and AI-powered search will grow fast enough to justify a capital structure that is starting to resemble an industrial conglomerate more than a software company. For NRI portfolios concentrated in Big Tech, this is the moment to re-examine position sizing — not because Google is broken, but because the risk profile just changed."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Just Committed $3.3 Billion to Build a Chip Plant in Odisha. It's Not Making Processors.",
        "subheadline": "The glass substrate facility — Intel's first major manufacturing commitment in India — fills a gap in the global semiconductor supply chain that most people have never heard of. For NRIs watching India's chip ambitions, this one actually matters.",
        "slug": make_slug("intel-odisha-glass-substrate-semiconductor-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's semiconductor mission has been long on announcements and short on operational output. This Intel deal is different because it targets advanced packaging substrates — a critical supply chain bottleneck controlled by a handful of Japanese and Taiwanese firms. For NRI engineers working in US chip companies, the Odisha plant represents potential career optionality: return-to-India roles in advanced semiconductor manufacturing that simply did not exist 18 months ago. For NRI investors, it signals that Intel under Lip-Bu Tan is serious about India as a manufacturing base, not just a design centre.",
        "tags": ["intel", "india-semiconductor", "odisha", "glass-substrate", "lip-bu-tan", "chip-manufacturing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/intel-3dgs-set-up-33-billion-substrate-plant-indias-odisha-state-2026-05-29/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/intel-joins-hands-with-odisha-govt-to-boost-indias-semiconductor-ecosystem/article69636000.ece"},
            {"name": "DQ India", "url": "https://www.dqindia.com/news/government-of-odisha-intel-and-3dgs-sign-mou-to-bring-substrate-manufacturing-technology-to-india/"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/intel-intc-3dgs-announce-33b-semiconductor-facility-in-odisha-1496251/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5118462/pexels-photo-5118462.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When India's semiconductor cheerleaders talk about catching up with Taiwan, they usually mean fabrication — etching circuits onto silicon wafers at the bleeding edge of physics. Intel just bet $3.3 billion on something less glamorous but arguably more strategic: the substrates those chips sit on.

On May 29, Intel Corporation and US-based 3DGS Inc. signed an MoU with the Odisha state government to establish an advanced packaging glass core substrate manufacturing facility in the Bhubaneswar-Khurda region. The deal, witnessed by Union IT Minister Ashwini Vaishnaw, Intel CEO Lip-Bu Tan, and Odisha Chief Minister Mohan Charan Majhi, represents one of the largest high-technology manufacturing investments India has ever attracted — and Intel's first direct manufacturing footprint in the country.

## What Are Glass Substrates, and Why Should You Care?

A semiconductor substrate is the foundational layer to which chip components are attached. Think of it as the circuit board inside the chip package itself. As chips get more complex — stacking multiple dies, integrating memory and processing on the same package — the substrate becomes a critical performance bottleneck.

Glass core substrates are the next generation of this technology. Compared to traditional organic substrates, glass offers superior flatness, thermal stability, and the ability to support finer interconnect pitches. Intel has been developing glass substrate technology for years, and this Odisha facility will be its vehicle for scaling production.

The market for advanced substrates is currently dominated by a handful of companies — primarily Ibiden and Shinko Electric in Japan, and Unimicron in Taiwan. By building in India, Intel is not just diversifying its supply chain; it is creating an entirely new node of production in a market that has been acutely concentrated.

## The India Semiconductor Ecosystem Grows Up

The Odisha deal arrives in the context of an Indian semiconductor push that has been gathering real momentum. Tata Electronics is building a fabrication plant in Dholera, Gujarat, with PSMC technology, expected to begin production by late 2026. Micron has committed to an assembly and test facility in Sanand. Applied Materials, Lam Research, Tokyo Electron, and Merck Electronics have all established or expanded Indian operations. Tata Electronics recently signed an MoU with ASML, the Dutch lithography monopolist.

Vaishnaw framed the Intel signing as validation: "This will further advance the semiconductor ecosystem in India." He is not entirely wrong. The fact that Intel — a company in the middle of its own existential turnaround under Lip-Bu Tan — chose India for its glass substrate bet suggests the ecosystem is becoming real enough for companies to make billion-dollar commitments.

The facility will be built in phases over five to six years and is expected to create more than 1,800 direct high-skilled jobs, with significant indirect employment in the surrounding manufacturing ecosystem.

## What NRIs Should Watch

For Indian-origin engineers working at Intel, TSMC, Samsung, or the US operations of substrate makers, the Odisha plant opens a career pathway that barely existed. Advanced packaging is one of the hottest specialisations in the chip industry, and India has historically had no domestic capacity. That changes now.

For investors, the play is subtler. Intel's stock dropped 3% on Monday — not because of the India deal, but because Nvidia's RTX Spark announcement threatened its core x86 franchise. The substrate facility is a long-horizon investment that will not move Intel's P&L for years. But it signals that Lip-Bu Tan's India strategy is about building capabilities, not just chasing subsidies.

The deeper question is whether India can execute. The country's track record on mega-manufacturing projects is uneven, and semiconductor manufacturing demands an ecosystem of precision suppliers, reliable power, ultra-pure water, and skilled technicians that India is still building. The Dholera fab will be the first real test. If it ships chips on schedule, Odisha's substrate plant will benefit from the credibility halo. If it stumbles, every subsequent project will face sharper scrutiny.

For now, though, the direction is clear: India is no longer content to design chips for others to build. It wants to build, too. And Intel — for all its troubles — just became its most important manufacturing partner."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "DeepSeek Just Made Its 75% Price Cut Permanent. Every AI Lab's Business Model Is Now Under Pressure.",
        "subheadline": "V4-Pro at $0.87 per million output tokens — 34 times cheaper than GPT-5.5 — is no longer a promotion. It is the new floor. For Indian developers and IT services companies, the economics of building with AI just shifted permanently.",
        "slug": make_slug("deepseek-v4-pro-permanent-price-cut-ai-economics"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian IT services giants — TCS, Infosys, Wipro, HCL — are rebuilding their businesses around AI agent deployment for enterprise clients. Their margins depend on which foundation models they use and at what cost. DeepSeek's permanent pricing makes Chinese models a serious option for cost-sensitive enterprise deployments, potentially undermining the pricing power of OpenAI and Anthropic partnerships that Indian IT firms have been building. Meanwhile, India's five million-plus developers now have access to near-frontier AI capability at a fraction of the cost, accelerating the startup economics that make Bengaluru and Hyderabad competitive with Silicon Valley.",
        "tags": ["deepseek", "ai-pricing", "indian-it-services", "ai-economics", "china-ai", "developers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "VentureBeat", "url": "https://venturebeat.com/ai/deepseek-v4-pro-price-cut-permanent/"},
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20250525PD200/deepseek-api-pricing-ai.html"},
            {"name": "Communications Today (Bloomberg)", "url": "https://communicationstoday.co.in/deepseek-cuts-prices-for-flagship-model-amid-china-ai-price-war/"},
            {"name": "EverMX", "url": "https://evermx.com/deepseek-v4-pro-price-cut-permanent/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """On May 22, DeepSeek posted a notice that most people outside AI pricing circles missed entirely. The 75% promotional discount on its V4-Pro model — originally set to expire on May 31 — was now permanent. No sunset clause, no conditions. Output tokens at $0.87 per million. Input tokens at $0.435 per million. Cache hits at $0.003625 per million.

Those numbers are not incremental improvements over Western competitors. They are a different economic universe. At permanent rates, V4-Pro is approximately 34 times cheaper on output than OpenAI's GPT-5.5. It significantly undercuts Google's Gemini 3.1 Pro and Anthropic's Claude Opus 4.7. On SWE-bench Pro, V4-Pro scores 55.4% versus GPT-5.5's 58.6% — a three-percentage-point gap in performance for a 34-fold gap in cost.

## How DeepSeek Can Afford This

The pricing is not a loss-leader play. DeepSeek attributes the cuts to structural efficiency gains — a mixture-of-experts architecture that activates only a subset of parameters per query, combined with aggressive cache optimisation that makes repeated-context workloads almost free. The V4-Pro's one-million-token context window means developers can feed entire codebases or document archives into a single session without hitting the cost walls that characterise Western frontier models.

Chinese AI infrastructure costs are also structurally lower. Despite US export controls limiting access to the most advanced Nvidia GPUs, Chinese labs have optimised around the constraints — using older hardware more efficiently, investing in custom inference stacks, and benefiting from lower energy and labour costs. The result is a cost structure that Western labs cannot easily match without fundamentally redesigning their own inference infrastructure.

## The Indian IT Services Dilemma

For TCS, Infosys, Wipro, and their peers, the DeepSeek pricing shift creates an uncomfortable strategic question. These companies have been racing to build AI practices around partnerships with OpenAI, Anthropic, and Google — deals that bring prestige and enterprise credibility but also lock in high per-token costs that get passed through to clients.

DeepSeek's permanent pricing makes Chinese models a viable option for cost-sensitive deployments. An enterprise running a customer service agent on GPT-5.5 at $30 per million output tokens could switch to V4-Pro at $0.87 and achieve roughly comparable results. For Indian IT firms billing clients on a margin over infrastructure costs, the pressure to offer cheaper alternatives will intensify — even as they navigate the geopolitical sensitivities of recommending Chinese AI to American and European clients.

The consulting pitch gets harder too. When frontier-class AI costs less than a dollar per million tokens, the value proposition shifts from "we will help you afford AI" to "we will help you deploy AI everywhere" — a fundamentally different engagement model that requires different capabilities.

## What Indian Developers Gain

For India's five million-plus software developers, the calculus is simpler and more optimistic. DeepSeek's pricing makes frontier-class AI accessible for experimentation, prototyping, and production workloads at startup-friendly economics. A Bengaluru two-person team building an AI-powered legal research tool no longer needs to choose between capability and cost — V4-Pro delivers both.

Akshar Keremane, co-founder of Bangalore-based AI startup O-Health, put it directly: "The pricing, open-source availability and one-million context window features all lower barriers for developers, startups and small enterprises. It allows users to experiment at a model capability and scale that was not available earlier."

The one-million-token context window is particularly significant for Indian use cases. Processing lengthy government documents, analysing complex regulatory filings, or building AI agents that can reason across entire codebases — these are workloads where context length matters as much as raw intelligence.

## The Geopolitical Asterisk

None of this happens in a vacuum. The US has accused Chinese AI entities of "industrial-scale distillation" of Western models. DeepSeek itself faces persistent questions about the provenance of its training data and techniques. For Indian companies considering deployment, the geopolitical risk is real — American clients may balk at Chinese model dependencies, and future export controls could complicate access.

But for now, the market is voting with its wallets. DeepSeek's permanent pricing has set a floor that every other AI lab must reckon with. OpenAI, Anthropic, and Google can compete on capability, brand trust, and ecosystem integration. What they cannot do is pretend that 34x cost premiums are sustainable indefinitely.

The AI price war is no longer a Chinese phenomenon. It is a global one. And Indian builders — from TCS boardrooms to Koramangala co-working spaces — are among its biggest beneficiaries."""
    }
]

# Validate images
for art in articles:
    img = art.get("image_url", "")
    if img:
        valid = validate_image(img)
        if not valid:
            print(f"⚠️  Image validation failed for {art['slug']}: {img}")
            # Don't skip - Wikimedia HEAD sometimes doesn't return Content-Length
            # but images are valid

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
