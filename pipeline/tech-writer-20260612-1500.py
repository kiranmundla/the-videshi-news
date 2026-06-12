#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-12 15:00 UTC batch"""
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


# ── Article 1 ─────────────────────────────────────────────────────────
art1_body = """NVIDIA has begun pitching its Vera central processing unit to Chinese clients, telling them the ARM-based chip could ship as early as August, according to three people familiar with the matter. The outreach marks an audacious new front for the world's most valuable company: having conquered GPU-powered AI training, it now wants the CPU business that Intel and AMD have dominated for decades.

The stakes are considerable. Vera is NVIDIA's first standalone server CPU, built specifically for agentic AI — the fast-growing class of systems that carry out complex tasks with minimal human oversight. The chip is in full production and, according to NVIDIA, runs up to 1.8 times faster than comparable rival processors in agentic workloads. A single Vera chip will cost "well north of $20,000" before bulk discounts, according to SemiAnalysis, and a fully loaded rack of 256 chips would run to roughly $10 million.

## ARM Takes the Fight to x86

What makes Vera strategically important is its architecture. Built on ARM designs rather than the x86 instruction set that has underpinned the server market for four decades, the chip signals NVIDIA's bet that the agentic AI era will break Intel and AMD's structural lock on data-centre CPUs. Jensen Huang has called Vera a future "multibillion-dollar business" and told investors the company expects $20 billion in Vera revenue by the end of its fiscal year in January 2027.

Chinese interest, while early, is notable. Reuters reports that one major cloud company plans to order more than 300 two-socket Vera servers for testing before committing to larger procurement. Alibaba and ByteDance are also collaborating with NVIDIA on Vera deployments, though both declined to comment. Chinese clients plan to deploy the chips first in overseas data centres — a pragmatic workaround while domestic regulatory signals remain mixed.

## Why the Diaspora Should Watch This

For the tens of thousands of Indian engineers working in the semiconductor and cloud-infrastructure sectors in the United States, Vera represents both opportunity and disruption.

The chip's ARM architecture gives it a philosophical kinship with the processor designs powering smartphones and, increasingly, laptops — a space where Indian chip designers, from Qualcomm's Hyderabad campus to Apple's Bengaluru silicon team, have been quietly ascendant. If ARM dislodges x86 in the data centre, the engineering expertise that the Indian diaspora has built over two decades of mobile chip design becomes directly transferable to the highest-margin corner of enterprise computing.

At the same time, the CPU shortage is real. Intel has warned Chinese customers of server-CPU delivery lead times stretching to six months. AMD has flagged that global CPU supply is "tight," with demand outpacing forecasts. For NRI engineers at Intel and AMD, the entry of a deep-pocketed competitor like NVIDIA means their employers must execute flawlessly or cede ground they have held since the 1990s.

The broader shift from training-centric GPU spend to inference-centric CPU spend is also reshaping hiring. Agentic AI workloads are CPU-heavy, and the talent pipeline for designing and optimising ARM server processors is thinner than for GPUs. That scarcity is good news for experienced semiconductor professionals — and India's engineering colleges, which have been producing ARM-literate graduates at scale, stand to benefit disproportionately.

NVIDIA's Vera gambit is, at bottom, a bet that the age of the monolithic GPU data centre is giving way to something more hybrid. For Indian Americans who built their careers in chips, that transition will create as many winners as it displaces."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "NVIDIA's Vera CPU Lands in China, Opening a $20 Billion Front Against Intel and AMD",
    "subheadline": "The ARM-based chip, built for agentic AI, could reshape the server market — and the careers of thousands of Indian semiconductor engineers.",
    "slug": make_slug("nvidia-vera-cpu-china-arm-server-intel-amd"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian chip designers' ARM expertise becomes directly valuable in enterprise data centres as NVIDIA's Vera challenges the x86 duopoly that Intel and AMD have held for decades.",
    "tags": ["nvidia", "vera-cpu", "arm", "semiconductors", "china", "agentic-ai", "intel", "amd"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/china/nvidia-begins-vera-cpu-sales-pitch-chinese-clients-sources-say-2026-06-12/"},
        {"name": "SemiAnalysis (via Reuters)", "url": "https://www.reuters.com/world/china/nvidia-begins-vera-cpu-sales-pitch-chinese-clients-sources-say-2026-06-12/"},
        {"name": "StockTwits / BofA Analysis", "url": "https://stocktwits.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Server racks inside a modern data centre — the infrastructure at the heart of the CPU wars",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}


# ── Article 2 ─────────────────────────────────────────────────────────
art2_body = """Monterey Park, a city of 60,000 in California's San Gabriel Valley, has become the first municipality in the United States to permanently ban data centres within its limits. Voters approved Measure NDC by an 88-to-12 margin — 10,321 votes to 1,362 — making the prohibition as emphatic as ballot measures get.

The new rule amends Monterey Park's General Plan to forbid data-centre construction citywide. It can only be reversed by another public vote. For a community that sits barely ten miles east of downtown Los Angeles, surrounded by the roar of the AI infrastructure buildout, it is a pointed declaration: not here.

## What Sparked It

The catalyst was a proposal by HMC StratCap, an Australian investment firm operating through its DigiCo platform, to convert a 218,400-square-foot site on Saturn Avenue into a data centre capable of handling 50 megawatts of peak electrical load. The project promised roughly $5 million a year in tax revenue. Opponents argued the electricity demand, water consumption and noise far outweighed those dollars. The project was withdrawn, but the backlash it generated did not retreat with it.

"Data centres bring no long-term benefits to local communities, and they come with serious risks," one resident said during a public comment session. Mayor Elizabeth Yang, who opposed the development, celebrated with a blunt post: "Landslide win!! Congratulations to our city on making history!!!"

## The Numbers Behind the Backlash

There are now more than 3,069 data centres operating in the United States, with another 1,489 planned or under construction. Microsoft Azure alone relies on an estimated 500 facilities across 80 regions. The global industry will spend over $1 trillion on data-centre infrastructure this year. Monterey Park's vote is a rounding error by revenue — but as a political signal, it is loud.

Similar resistance is building in Northern Virginia's Loudoun County, parts of Arizona, and rural Georgia. Local governments are being squeezed between Big Tech's chequebooks and residents who see water bills rising and electrical grids straining. A typical hyperscale data centre employs only 30 to 50 permanent staff, making the jobs-versus-impact trade-off lopsided.

## Why NRIs Should Care

The San Gabriel Valley, where Monterey Park sits, has one of the densest Asian-American populations in the country. Indian American communities in neighbouring cities — Arcadia, Temple City, Alhambra — are watching closely. Many are themselves employees of the very companies building these facilities: Meta, Google, Microsoft, Amazon.

The tension is personal. An NRI engineer at Meta's data-centre division may spend the week designing the cooling architecture for a Louisiana hyperscale facility, then come home to a neighbourhood where a ballot measure banning the same kind of building has passed with near-unanimous support. That cognitive dissonance is increasingly common in the Indian tech diaspora.

There is also a property-value dimension. Monterey Park's median home value sits at $863,000. Residents calculated that a data centre next door, with its generator hum and truck traffic, would erode the real-estate premiums they depend on. For Indian American homeowners who entered the California market at already-stretched prices, that calculus matters viscerally.

As Big Tech pivots toward smaller, quieter, less power-hungry facilities — or relocates entirely to rural areas willing to accept the trade-off — the geography of the AI boom is shifting. The NIMBY moment for data centres has arrived, and Indian Americans are on both sides of the argument."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Monterey Park Just Became the First U.S. City to Permanently Ban Data Centres",
    "subheadline": "An 88 per cent landslide in California's San Gabriel Valley signals that the NIMBY movement has caught up with the AI boom — and NRIs are on both sides.",
    "slug": make_slug("monterey-park-bans-data-centers-nimby-ai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian American communities in the San Gabriel Valley live next door to proposed data-centre sites while working at the companies building them — the ban crystallises a growing tension in the diaspora.",
    "tags": ["data-centers", "nimby", "california", "monterey-park", "ai-infrastructure", "real-estate", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/technology/california-city-votes-permanently-ban-data-centers-first-of-its-kind-measure"},
        {"name": "IndexBox", "url": "https://www.indexbox.io/blog/monterey-park-measure-ndc-voters-overwhelmingly-approve-permanent-data-center-ban/"},
        {"name": "Realtor.com", "url": "https://www.realtor.com/news/trends/can-ai-solve-americas-132k-regulatory-housing-problem/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Green_Datacenter_AG.jpg",
    "image_caption": "A data-centre facility — the kind of structure Monterey Park voters just banned permanently",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ── Article 3 ─────────────────────────────────────────────────────────
art3_body = """Meta will spend $115 million this year on a programme called America's Workforce Academy, training electricians, welders, plumbers and fibre-optic technicians and guaranteeing every graduate a job. Google followed days later with $50 million to prepare 300,000 workers for skilled-trades careers across more than 20 states. Together, the two AI giants are putting $165 million behind a single proposition: the artificial-intelligence revolution needs hardhats, not just hoodies.

Meta's programme launches in four pilot states — Louisiana, Ohio, Indiana and Texas — each home to major data-centre construction. Training lasts four to five weeks. Meta covers tuition, airfare, lodging and a daily stipend. Graduates earn credentials from the National Center for Construction Education and Research and walk into contractor roles at Meta-affiliated sites. No prior experience is required.

Google's parallel initiative funds training experts affiliated with 14 labour unions and four trade associations, covering welders, pipefitters, sheet-metal workers and electricians. Ruth Porat, Alphabet's president and chief investment officer, framed it bluntly: "America's digital economy relies on our physical infrastructure and the electricians, pipefitters, welders, manufacturing workers and more who build and maintain it."

## The Labour Maths

The numbers explain the urgency. A typical hyperscale data centre requires hundreds of electricians, welders and mechanical tradespeople during its construction phase — and the United States has 1,489 new facilities planned or under construction. The Bureau of Labor Statistics projects a shortage of hundreds of thousands of skilled-trades workers over the next decade, a gap that existed before AI and is now widening sharply.

David Sacks, the venture capitalist and former White House AI adviser, praised Meta's initiative on X: "The AI infrastructure boom is generating strong demand for skilled blue-collar workers. In fact, there's a shortage of electricians, fibre technicians, and mechanical tradespeople needed to build and maintain AI data centres." Chamath Palihapitiya, a former Meta executive, called the programme "transformational" — estimating it could create upwards of one million jobs if scaled across the full AI buildout.

Meta's earlier pilot, a fibre-installation programme called Level-Up, drew 35,000 applications in its first week. The demand, clearly, is there.

## The Diaspora's White-Collar Blind Spot

For Indian Americans, the announcement exposes a structural assumption baked into decades of immigration patterns: that "working in tech" means writing code.

The H-1B visa system funnels Indian professionals overwhelmingly into software engineering, data science and management roles. The cultural expectation in Indian American families — a computer-science degree from a good university, a six-figure offer from a FAANG company — has produced a generation of white-collar tech workers who are among the highest-earning demographic groups in America.

But the AI boom is creating jobs that do not require a CS degree. An electrician trained through Meta's programme can earn over $100,000 a year. A certified fibre technician is in such demand that contractors are offering signing bonuses. These are not marginal roles. They are load-bearing positions in the physical infrastructure that makes artificial intelligence possible.

The question for the Indian American community is whether the next generation will consider these paths. Indian families in the United States have historically underinvested in vocational training, viewing it as a step down from professional careers. That cultural bias may be costing second-generation Indian Americans access to a booming labour market where supply has not caught up to demand.

There is also a policy dimension. The trades-training programmes are open to veterans, recent graduates and career changers — but they are not explicitly tied to any immigration pathway. For Indian nationals on H-1B visas who lose their jobs in a tech layoff, retraining as a fibre technician is not a viable option under current immigration rules. The 60-day grace period does not accommodate a five-week vocational course plus a job transition.

Meta and Google are not building altruistic academies. They are solving a supply-chain problem: they need people to pour concrete and pull cable faster than the labour market can produce them. But in doing so, they are also redrawing the map of what a "tech job" looks like — and the Indian diaspora would do well to update its mental model accordingly."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta and Google Are Spending $165 Million to Train Plumbers and Electricians. That's an AI Story.",
    "subheadline": "The two tech giants need blue-collar workers to build their data centres — and the Indian American community's white-collar assumptions are about to be tested.",
    "slug": make_slug("meta-google-trades-training-data-centers-blue-collar"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian Americans have been overwhelmingly white-collar tech workers; the AI infrastructure boom is creating high-paying blue-collar jobs that challenge the diaspora's cultural assumptions about what 'working in tech' means.",
    "tags": ["meta", "google", "skilled-trades", "data-centers", "blue-collar", "h1b", "workforce", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/technology/meta-launches-115m-skilled-trades-academy-guaranteed-jobs"},
        {"name": "Inc.", "url": "https://www.inc.com/kit-eaton/why-meta-is-suddenly-hiring-plumbers-electricians-and-welders/91153026"},
        {"name": "LinkedIn (Ruth Porat / Google)", "url": "https://www.linkedin.com/posts/google-pledges-50m-skilled-trades"},
        {"name": "StockTwits (David Sacks, Chamath comments)", "url": "https://stocktwits.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/27928759/pexels-photo-27928759.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A technician works on an electrical panel — the kind of skilled-trades role Big Tech is racing to fill",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}


# ── Insert ─────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
