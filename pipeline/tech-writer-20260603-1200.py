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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Filed to Go Public at $965 Billion. It Beat OpenAI to the Punch.",
        "subheadline": "The Claude AI maker submitted a confidential S-1 to the SEC, kicking off what could become the largest tech IPO in history — and the first shot in a three-way listing race with OpenAI and SpaceX.",
        "slug": make_slug("anthropic-ipo-s1-filing-965-billion-openai-spaceX"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian AI researchers at Anthropic, OpenAI, and DeepMind helped build the models driving these trillion-dollar valuations. For NRI investors, the trio of AI IPOs this year represents the first chance to own shares in frontier AI labs — and the stakes for Indian-origin engineers holding equity at these companies are staggering.",
        "tags": ["ai", "anthropic", "ipo", "openai", "wall-street", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Anthropic Official Statement", "url": "https://www.anthropic.com"},
            {"name": "The Verge", "url": "https://www.theverge.com"},
            {"name": "The Motley Fool", "url": "https://www.fool.com"},
            {"name": "Verdict", "url": "https://www.verdict.co.uk/anthropic-ipo-sec-draft-filing/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """Anthropic, the San Francisco-based AI company behind the Claude family of models, filed a confidential draft registration statement — a Form S-1 — with the US Securities and Exchange Commission on Monday. The filing does not guarantee an IPO. But at a private valuation of $965 billion, Anthropic is now formally closer to a public listing than any other AI lab on Earth.

The company has beaten OpenAI, its older and better-known rival, to this particular milestone. OpenAI, last valued at $852 billion, is reportedly preparing its own confidential filing. SpaceX has already filed and is targeting a June 12 listing at a $1.75 trillion valuation. If all three reach public markets this year, 2026 will produce the largest cluster of tech IPOs since the dot-com era.

## A Revenue Machine That Appeared Almost Overnight

Anthropic's numbers have escalated at a pace that would make most SaaS companies uncomfortable. Its annualised revenue run rate has reached $47 billion, up from $10 billion a year ago — a nearly fivefold increase driven largely by enterprise adoption of Claude. Reports suggest the company is on track for its first profitable quarter in Q2 2026, targeting an operating profit of $559 million.

The growth engine is Claude Code, Anthropic's AI-powered coding tool, which has rapidly gained ground among enterprise engineering teams. More recently, Claude for Small Business expanded the company's addressable market further downstream. The latest flagship model, Claude Opus 4.8, debuted last week with improved reasoning and multi-step task completion — capabilities that directly serve the agentic AI applications corporate customers are racing to deploy.

In its most recent funding round in late May, Anthropic raised $65 billion at a post-money valuation of $965 billion, surpassing OpenAI for the first time and cementing its status as the world's most valuable startup.

## What This Structure Means for Investors

Anthropic is incorporated as a public benefit corporation, a legal structure that allows management to balance shareholder returns against a stated social mission. In practice, this means Dario Amodei, the company's CEO, and his leadership team have some legal insulation from the kind of shareholder pressure that could push the company toward unsafe deployments. It also means potential investors need to understand that Anthropic's governance is deliberately different from a conventional corporation.

The S-1 filing is confidential under Rule 135 of the Securities Act. The number of shares, the price range, and the listing timeline remain undisclosed. The SEC's review process will take weeks, possibly months, and the actual offering depends on market conditions.

## Why Indian Tech Workers Should Pay Attention

The trio of AI mega-IPOs — Anthropic, OpenAI, and SpaceX — represent a generational wealth event for the engineers who built these companies. Indian-origin researchers occupy critical roles across all three organisations, from safety teams to model architecture to infrastructure. Many hold equity that, upon a public listing, will be liquid for the first time.

For NRI investors in the Bay Area, New Jersey, and beyond, these IPOs also represent the first opportunity to buy into frontier AI companies on public markets. Until now, exposure required either working at these companies or investing through late-stage venture funds with high minimums.

Sriram Krishnan, the Indian-American technologist who serves as the White House's AI policy advisor, is shaping the regulatory environment under which these listings will proceed. His role places an Indian diaspora member at the intersection of AI governance and capital markets at a moment when the stakes could not be higher.

Wedbush Securities called the filings "an opening of the floodgates for the IPO market." The floodgates are open. The question is whether the market can absorb what comes through.

https://x.com/AnthropicAI/status/1929925789456486400"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Broadcom Reports Earnings Tonight With AI Revenue That Has Doubled in a Year. The Pressure Is Enormous.",
        "subheadline": "Wall Street expects $22 billion in quarterly revenue and confirmation that custom AI silicon — not just Nvidia's GPUs — is the new centre of gravity in the $800 billion AI infrastructure build-out.",
        "slug": make_slug("broadcom-q2-earnings-ai-silicon-revenue-22-billion"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Broadcom's India engineering centres in Bangalore and Hyderabad are critical to its custom ASIC design pipeline — the very products driving its AI revenue explosion. For NRI investors, Broadcom has quietly become one of the best-performing semiconductor stocks of 2026, and tonight's earnings will determine whether its $2.1 trillion valuation holds.",
        "tags": ["broadcom", "ai-chips", "earnings", "semiconductor", "asic", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Broadcom Q1 2026 Earnings", "url": "https://www.broadcom.com"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/AVGO/earnings/"},
            {"name": "Barchart / HSBC Research", "url": "https://www.barchart.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "body": """Broadcom reports its fiscal second-quarter earnings after the bell today, and the numbers Wall Street has pencilled in are extraordinary even by AI-era standards. Analysts expect revenue of approximately $22 billion — a 47 per cent increase from the same quarter last year — with adjusted earnings per share of $2.40, up 52 per cent. The headline within the headline is AI semiconductor revenue, which management has guided to $10.7 billion for the quarter, following Q1's $8.4 billion that itself was up 106 per cent year-on-year.

These are not GPU numbers. Broadcom does not make GPUs. Its AI business is built on custom application-specific integrated circuits — ASICs — designed in close collaboration with hyperscale cloud customers who want silicon tailored to their specific workloads rather than Nvidia's general-purpose graphics processors.

## The Custom Silicon Thesis Gets Its Biggest Test

Broadcom has publicly stated that it secured more than $10 billion in AI infrastructure orders from a single new customer, and that four additional prospects were "deeply engaged" on custom chip programmes earlier this year. At least one of those prospects has since been upgraded to a qualified customer.

This matters because it suggests Broadcom's AI revenue is not a cyclical windfall but an architectural shift. Hyperscalers are designing their own chips and hiring Broadcom to manufacture and integrate them. Google's TPU programme, one of Broadcom's longest-standing custom silicon relationships, is the template. The question is whether Meta, Amazon, and potentially Apple are following the same path at similar scale.

In Q1, Broadcom generated $8.01 billion in free cash flow, representing 41 per cent of revenue. It announced a $10 billion share repurchase programme and continued its quarterly dividend of $0.65 per share. The company's market capitalisation stands at approximately $2.1 trillion, and shares are up roughly 30 per cent year-to-date.

## Why Bangalore Is Central to This Story

Broadcom's engineering operations in India are not a support function. The company's design centres in Bangalore and Hyderabad are deeply embedded in the ASIC development pipeline — the custom chip work that constitutes Broadcom's fastest-growing revenue stream. Indian engineers at these centres work on the physical design, verification, and validation of the custom silicon that hyperscalers are ordering in increasing volume.

For the thousands of Indian-origin engineers at Broadcom, both in India and in the company's San Jose headquarters, tonight's earnings carry direct implications for compensation, stock vesting, and team expansion. Broadcom's headcount decisions in India tend to track its AI order book closely.

## The NRI Investor Angle

Among NRI investors tracking the AI semiconductor space, Broadcom has emerged as the second-largest pure-play AI chip company after Nvidia. But where Nvidia sells standardised GPUs at scale, Broadcom's business model — deeply customised, relationship-driven, and sticky — arguably has more durable economics. HSBC's Frank Lee raised his price target to $600 on Monday, representing 34 per cent upside from recent levels, on the thesis that AI revenue in the second half of 2026 will exceed current Street estimates.

The risk is execution. Custom silicon programmes are long-cycle commitments. A single customer delay or design respin can shift revenue from one quarter to the next. Broadcom's guidance for Q2 was set three months ago. Tonight's results will reveal whether the demand behind that guidance has held, strengthened, or shown the first cracks.

The report drops after 4 PM Eastern. For anyone with Broadcom shares in a brokerage account — or considering buying them — the next twelve hours are the ones that matter."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Lip-Bu Tan Told Computex That CPUs Are Back. Intel's 18A Chip Is His Opening Argument.",
        "subheadline": "At Computex 2026, Intel's CEO unveiled the Xeon 6+ — the first server processor built on America's most advanced chipmaking process — and made a pointed case for why AI's next act belongs to the CPU.",
        "slug": make_slug("intel-lip-bu-tan-computex-xeon-6-plus-18a-cpu-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Intel's India engineering operation — one of its largest R&D centres globally, based in Bangalore — contributed to the 18A process development and Xeon design work. For the thousands of Indian engineers at Intel, the Xeon 6+ launch validates a multi-year bet. For NRI investors, Intel's stock has more than quintupled since Lip-Bu Tan took over.",
        "tags": ["intel", "computex", "18a", "xeon", "cpu", "agentic-ai", "semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Intel Computex 2026 Keynote", "url": "https://www.intel.com"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/intel-ceo-says-he-wants-to-capitalize-on-full-ai-ecosystem"},
            {"name": "Digit", "url": "https://www.digit.in/computing/computex-2026-intel-announces-xeon-6-processors-says-ai-will-make-cpus-important-again.html"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """Lip-Bu Tan climbed the 1,000 steps of Taipei's Elephant Mountain before his Computex keynote on Tuesday, a detail he shared with the audience to light laughter. The metaphor was not lost on anyone who has followed Intel's trajectory over the past two years. The climb has been steep, and the CEO wanted people to know he made it to the top in one piece.

What followed was the most consequential product announcement of Tan's tenure. Intel unveiled the Xeon 6+ processor — a next-generation server CPU built on Intel's 18A process node, a 2nm-class manufacturing technology that is now in volume production at Fab 52 in Chandler, Arizona. It is, according to Intel, the most advanced semiconductor process developed and manufactured in the United States.

## The Numbers That Matter

A single liquid-cooled rack loaded with Xeon 6+ processors can deliver 36,864 compute cores within 32U of rack space, operating at approximately 100 kilowatts. Intel is positioning this as a density and efficiency argument — not raw speed, but the ability to run more AI inference workloads per watt than competing architectures.

The pitch is tied to a structural shift in AI infrastructure. Ben Bajarin, CEO of Creative Strategies, framed it in terms that Intel is now using as its rallying cry: during the training era, the typical ratio in AI deployments was one CPU for every four GPUs. In the agentic inference era — where AI models run autonomously, making decisions and taking actions — that ratio compresses to roughly one CPU per GPU, or even less.

If Bajarin is correct, the CPU is not a commodity connector between GPUs. It is a co-equal participant in the AI stack. Intel's entire strategy rests on this thesis.

## 18A: The Process That Was Supposed to Be Impossible

Intel's 18A process uses two technologies that no other chipmaker has yet combined at scale: RibbonFET, a gate-all-around transistor architecture, and PowerVia, a backside power delivery system that routes electrical power through the back of the chip rather than competing for space with data signals on the front. The result is a claimed 15 per cent improvement in performance per watt and 30 per cent better chip density compared to Intel's previous node.

Fab 52 is part of a $100 billion manufacturing buildout across Intel's US facilities. The company has stated that at least three generations of products will be built on 18A, signalling that this is not a one-off process but a platform intended to anchor Intel's foundry ambitions for years.

Intel also announced a partnership with SambaNova and Foxconn to build rackscale AI infrastructure combining Xeon processors with specialised AI accelerators — an acknowledgement that Intel does not expect to win the AI market on CPUs alone but intends to ensure its silicon is present in every configuration.

## Bangalore's Fingerprints on the Design

Intel's India development centre in Bangalore is one of the company's largest engineering operations outside the United States. Indian engineers have contributed to the 18A process development, Xeon architecture design, and the verification workflows that bring a chip from tape-out to volume production. The Xeon 6+ is not a chip that was designed in Oregon and handed to India for testing. It was co-developed across continents.

For the thousands of Indian engineers at Intel — both in Bangalore and across US offices — the Xeon 6+ launch is a professional vindication. Intel's stock has risen from roughly $19 to over $107 since Tan took over as CEO, more than quintupling in value. For employees holding restricted stock units, the difference between Intel at $19 and Intel at $107 is the difference between a good year and a life-changing one.

Tan laid out four pillars for Intel's future at Computex: PCs, edge and agentic AI, foundational data centres, and what he calls "intelligence centres." Each pillar, he argued, represents a generational opportunity. The market will decide whether the 18A process and Xeon 6+ are enough to credibly claim all four.

He did make it down the mountain. Whether Intel has truly made it back from its own descent remains the more interesting question."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
