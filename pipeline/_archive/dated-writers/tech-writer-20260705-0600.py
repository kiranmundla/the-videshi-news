#!/usr/bin/env python3
"""Tech writer — 2026-07-05 06:00 PT run. 3 articles."""

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


# ---------- ARTICLE 1: Bhavin Turakhia's Neo ----------

art1_body = """Bhavin Turakhia has spent two decades building companies from scratch — Directi, Radix, Titan, and fintech unicorn Zeta. Now the 46-year-old serial entrepreneur is putting $30 million of his own money behind his boldest bet yet: an AI-native enterprise platform called Neo that aims to take on Microsoft 365 and Google Workspace.

The thesis is simple, if audacious. Turakhia argues that workplace software designed before generative AI cannot be meaningfully upgraded with chatbots bolted on after the fact. The entire stack, he says, must be rebuilt around AI as a first-class participant in daily work — not a sidebar you open when you're stuck.

## What Neo actually is

Neo bundles four products into a single platform. **Friday** is an AI assistant and agent layer connected to over 1,000 external applications. **Tasket** handles project management. **Studio** manages documents, spreadsheets, and diagrams. And **Drive** is a collaborative file-sharing workspace where both humans and AI agents operate on the same files.

The platform is model-agnostic — enterprises can switch between AI models from Anthropic, OpenAI, or others without being locked to a single provider. That's a direct shot at Microsoft's Copilot, which has been tightly coupled with OpenAI models (a constraint Microsoft itself recently acknowledged was a mistake, admitting it should have been multi-model from the start).

Neo has been running internally across Turakhia's other companies — Zeta, Titan, and Radix — since April. The team is small: roughly 50 employees, including about 18 engineers. An external launch for select customers in India and the United States is planned for August, with a public release in January 2027.

## The switching-cost problem

"If you want to build an iPhone, you can't take the parts of a Nokia and somehow convert it into an iPhone," Turakhia told TechCrunch. It's a compelling analogy, but it glosses over the central challenge: enterprise software isn't just a product category. It's embedded in email, calendars, permissions, document workflows, and years of institutional muscle memory. Convincing companies to migrate their core productivity stack is among the hardest sells in enterprise tech.

Turakhia is targeting mid-sized businesses first — knowledge workers in technology, consulting, and professional services — where switching costs are lower and AI adoption appetite is higher. He has said that even 2 to 5 per cent market share would be larger than anything he has built before.

## Why NRIs should pay attention

For Indian tech professionals in the US, Turakhia's move is more than a product launch. It's a signal about where Indian-origin founders are aiming. This isn't another India-first fintech or a domestic SaaS play. Neo is a direct global competitor to the two most entrenched productivity suites in the world, built by a founder whose previous companies collectively generated over $2 billion in value.

The timing is also notable. Microsoft just launched its $2.5 billion AI implementation arm, Frontier Co., acknowledging that enterprises need hands-on help adopting AI — an admission that bolting AI onto existing tools isn't enough. If that problem is real enough for Microsoft to throw billions at, Turakhia might be asking the right question, even if his $30 million answer is a rounding error by comparison.

The enterprise AI workspace race is heating up. Whether Neo can convert that opening into actual enterprise contracts will become clearer after the August launch. For now, it's a $30 million bet that the AI era demands new software, not upgraded old software — and that an Indian founder can build it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian Founder Just Bet $30 Million That Microsoft Office Needs to Be Rebuilt From Scratch",
    "subheadline": "Bhavin Turakhia's Neo is an AI-native enterprise platform designed to replace, not upgrade, the workplace software stack. He's bootstrapping it himself.",
    "slug": make_slug("bhavin-turakhia-neo-ai-enterprise-microsoft-challenge"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "An Indian serial entrepreneur with a $2 billion track record is taking on Microsoft and Google head-on — a signal that Indian founders are no longer limiting their ambitions to domestic or fintech plays.",
    "tags": ["ai", "indian-founder", "enterprise-software", "startup", "neo", "bhavin-turakhia"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/02/indian-tech-tycoon-bets-30m-of-his-own-money-to-build-ai-alternative-to-microsoft-office/"},
        {"name": "Entrepreneur India", "url": "https://india.entrepreneur.com/article/bhavin-turakhia-launches-neo-commits-30-million-to-ai-work-platform/"},
        {"name": "TechCircle", "url": "https://www.techcircle.in/2026/07/02/bhavin-turakhia-bets-30-mn-on-neo-says-enterprises-need-ai-native-work-platforms"},
        {"name": "The Sheffield Press", "url": "https://thesheffieldpress.com/2026/07/02/bhavin-turakhia-backs-neo-an-ai-work-platform-to-challenge-microsoft-and-google/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Bhavin_Turakhia.jpg",
    "image_caption": "Bhavin Turakhia, serial entrepreneur and founder of Neo, Zeta, and Directi",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ---------- ARTICLE 2: TSMC Price Hikes & Expansion ----------

art2_body = """The company that manufactures virtually every advanced chip on the planet is about to make them more expensive. TSMC is raising prices on its 3-nanometre manufacturing node by up to 15 per cent in the second half of 2026, with a further 5 to 10 per cent increase expected in 2027, according to industry reports. Advanced nodes below 5nm — which account for 74 per cent of TSMC's revenue — are getting 3 to 5 per cent annual hikes across the board.

The increases are being driven by a reality that has become impossible to ignore: demand for advanced chips is outstripping supply, and TSMC has the pricing power to capitalise. AI server refresh cycles, custom chip programmes from every major cloud provider, and an insatiable appetite for GPU compute have pushed utilisation at TSMC's main 3nm facility, Fab 18, to near-maximum capacity. Monthly 3nm wafer output rose from around 130,000 in early 2026 to roughly 175,000 by the second quarter, and it still isn't enough.

## The ripple effect

These price hikes will flow through to nearly every consumer and enterprise device that matters. Nvidia's next-generation Vera Rubin processors, Apple's A-series and M-series chips, AMD's latest GPUs, and Qualcomm's Snapdragon processors are all manufactured on TSMC's advanced nodes. When TSMC raises prices, the cost trickles down — to data centres, to AI startups burning through compute budgets, and eventually to the smartphones and laptops that consumers buy.

Nomura analysts are projecting an "unprecedented" component-supply mismatch in the second half of 2026 that could worsen into 2027, particularly as Nvidia's Vera Rubin and Amazon's Trainium 3 chips ramp up production. The squeeze extends to non-AI sectors — automotive and consumer electronics could face further shortages.

## A $165 billion bet on American soil

Simultaneously, TSMC is accelerating the biggest overseas expansion in semiconductor history. The company has committed $165 billion to its Arizona campus, which will eventually include six fabs, two advanced packaging facilities, and an R&D centre across more than 2,000 acres. The first Arizona fab already turned a $514 million profit in its first year of production. Phase two, running at 3nm, is on track for 2027 — a full year ahead of schedule.

TSMC is also adding 3nm capacity in Taiwan (volume production in the first half of 2027) and Japan (2028). The company projects N3 gross margins will exceed the corporate average in the second half of 2026, signalling that these investments are already paying for themselves.

## What this means for India's chip ambitions

For the Indian semiconductor ecosystem, TSMC's dominance — a 70 per cent global foundry market share that climbed to 73 per cent in Q1 2026 — is both a sobering benchmark and a strategic opportunity. India's Semiconductor Mission, the Tata Electronics fab at Dholera, and Micron's Gujarat facility are all targeting mature nodes (28nm and above), not the cutting-edge processes where TSMC's pricing power is most formidable.

That's not necessarily a weakness. As TSMC shifts engineers and equipment away from older nodes to prioritise 3nm and 2nm, it creates openings for competitors in the mature-node market. The challenge for India is execution: building fab capacity, training a workforce, and hitting yield targets, all while the advanced-node leaders keep moving further ahead.

For NRI investors, the implications are clearer. TSMC stock has risen 111 per cent in the past year, and analysts project a 48 per cent earnings-per-share increase in 2026. The price hikes only strengthen that trajectory. But the semiconductor cycle can turn, and a serious escalation across the Taiwan Strait remains the risk that no analyst can fully price. For now, the company that makes everyone else's chips is getting paid more — and no one has a choice about it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "TSMC Is Raising Chip Prices Again. Every Device You Own Will Feel It.",
    "subheadline": "The world's dominant chipmaker is hiking 3nm prices by up to 15 per cent as AI demand overwhelms supply. Its $165 billion Arizona expansion is a year ahead of schedule.",
    "slug": make_slug("tsmc-3nm-price-hike-arizona-expansion-ai-demand"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "TSMC makes the chips inside every device Indian tech workers use and invest in — from Nvidia GPUs to iPhones. The price hikes affect AI startup costs, consumer electronics, and India's own semiconductor ambitions.",
    "tags": ["semiconductors", "tsmc", "ai-chips", "chip-prices", "india-semiconductor", "arizona"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TrendForce", "url": "https://www.trendforce.com/news/2026/05/27/news-tsmc-reportedly-eyes-up-to-15-3nm-price-hike-in-2h26-further-5-10-seen-in-2027-amid-ai-asic-demand/"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/07/04/artificial-intelligence-ai-chip-giant-profit-making-machine/"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2547283/how-taiwan-semiconductors-global-n3-expansion-plan-is-taking-shape"},
        {"name": "MarketWatch / Nomura Research", "url": "https://www.marketwatch.com/story/overlooked-bottlenecks-and-hyperscalers-forced-to-keep-spending-will-keep-the-chip-stock-rally-alive-says-nomura-team/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Building_of_Taiwan_Semiconductor_Manufacturing_Fab_12B_at_dusk1.jpg/1280px-Building_of_Taiwan_Semiconductor_Manufacturing_Fab_12B_at_dusk1.jpg",
    "image_caption": "TSMC's Fab 12B semiconductor manufacturing facility in Tainan, Taiwan",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ---------- ARTICLE 3: Anthropic Drug Discovery ----------

art3_body = """Anthropic, the company behind the Claude AI models, has done something no frontier AI lab has attempted before: it is building its own drug discovery pipeline, complete with wet laboratories and a team that includes AlphaFold co-creator John Jumper. The company announced the initiative alongside Claude Science, a dedicated AI workbench for researchers and pharmaceutical teams, at an "AI for Science" event in San Francisco this week.

This is not a partnership announcement or a licensing deal. Anthropic is conducting actual pre-clinical drug discovery — designing molecules, running experiments, and targeting diseases that traditional pharmaceutical companies ignore because the economics don't work.

## Claude Science: the research platform

Claude Science is a beta workbench available to Pro, Team, and Enterprise subscribers. It runs locally on macOS and Linux or connects remotely via SSH to high-performance computing clusters, a deliberate design choice that keeps sensitive research data on institutional infrastructure rather than sending it to the cloud.

The platform integrates generalist and specialist AI agents across more than 60 pre-configured scientific skills and over 60 databases — UniProt, PDB, Ensembl, and others that bioinformatics researchers rely on daily. It renders 3D protein structures, chemical molecules, and genomic tracks natively. A dedicated "reviewer agent" flags incorrect citations and untraceable numbers, maintaining an auditable history for reproducibility.

The integration with Nvidia's BioNeMo Agent Toolkit is notable. It means Claude Science can orchestrate tasks across molecular dynamics, protein structure prediction, and drug-target interaction analysis — the computationally intensive work that previously required stitching together multiple specialised tools.

## Why neglected diseases?

Eric Kauderer-Abrams, Anthropic's head of life sciences, framed the drug discovery programme as a direct consequence of the company's public benefit structure. "We're doing this because we believe first and foremost that to build the right models, products and tools to accelerate the industry, we need to live it," he said. The company is targeting diseases that fall outside the scope of commercial biopharma — conditions where patient populations are too small or too poor to justify traditional R&D investment.

It's a shrewd positioning move ahead of Anthropic's expected IPO. The company gets a high-visibility public benefit narrative, real scientific data to improve its models, and a testing ground that generates insights without competing directly with its pharmaceutical customers.

## The Indian connection

India produces more than 60 per cent of the world's vaccines and about 20 per cent of global generic drugs. The country's pharmaceutical industry, valued at roughly $50 billion, has long been the world's pharmacy for exactly the kind of neglected and tropical diseases Anthropic is targeting — malaria, tuberculosis, dengue, and a range of conditions that disproportionately affect developing nations.

Indian researchers are also heavily represented in both AI and life sciences at US institutions. The intersection of computational biology and machine learning — the exact space Claude Science occupies — has become one of the fastest-growing career paths for Indian-origin scientists. Jumper's move from Google DeepMind to Anthropic signals that the best talent in AI-driven biology is gravitating toward companies willing to invest in their own research, not just sell tools.

For NRI investors tracking the AI sector, Anthropic's pivot adds a new dimension. The company raised $65 billion in late May at a valuation approaching $965 billion, and an IPO is widely expected. Claude Science and the drug discovery programme give Anthropic a revenue story beyond chatbots — enterprise life sciences subscriptions and, potentially, drug candidates with real commercial value.

The question is whether an AI company can do what the pharmaceutical industry has been organised around for a century: discover drugs that actually work. The track record of AI-first drug discovery is still thin. But Anthropic has the capital, the talent, and the models. And it has chosen a starting point — neglected diseases — where the bar for impact is high and the competition is almost nonexistent."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic Just Hired the Co-Creator of AlphaFold. It Wants to Discover Drugs, Not Just Chat.",
    "subheadline": "The Claude maker is building wet labs, launching a dedicated science platform, and targeting diseases that Big Pharma won't touch. An IPO looms.",
    "slug": make_slug("anthropic-claude-science-drug-discovery-jumper-ipo"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India is the world's pharmacy for neglected diseases — exactly what Anthropic is targeting. Indian researchers dominate computational biology, and Anthropic's IPO is a key investment event for NRI tech investors.",
    "tags": ["ai", "anthropic", "drug-discovery", "biotech", "claude-science", "ipo"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/07/01/ai-company-anthropic-unveils-new-drug-discovery-program/"},
        {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/06/30/anthropic-launches-claude-sonnet-5-ai-model-coding-safety-upgrades-fable-mythos-controls-lifted/"},
        {"name": "LinkedIn / Albert Au", "url": "https://www.linkedin.com/pulse/anthropic-moves-beyond-general-ai-direct-drug-discovery/"},
        {"name": "WebProNews", "url": "https://www.webpronews.com/anthropic-launches-claude-sonnet-5-0-with-measured-gains-in-coding-and-reasoning/"}
    ]),
    "score_total": 74,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8539653/pexels-photo-8539653.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Laboratory equipment including test tubes and petri dishes used in pharmaceutical research",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ---------- INSERT ----------

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
