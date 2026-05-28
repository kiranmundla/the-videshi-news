#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-28 06:00 UTC run"""
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
    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 1: Marvell Technology Q1 earnings
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Marvell's AI Chip Bet Is Paying Off. Its India Engineers Are a Big Reason Why.",
        "subheadline": "The semiconductor company posted record revenue and raised its outlook to $16.5 billion, powered by custom silicon that Indian design teams helped build.",
        "slug": make_slug("marvell-ai-chip-india-engineers-custom-silicon"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Marvell employs thousands of chip design engineers across Pune, Bangalore, and Hyderabad — the people literally designing the custom AI accelerators that hyperscalers are spending hundreds of billions on. For NRI semiconductor professionals and investors, this is a company where Indian talent directly drives the growth story.",
        "tags": ["semiconductors", "marvell", "ai-chips", "custom-silicon", "india-engineering", "nvidia"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/marvell-technology-first-quarter-revenue-soars-profit-slims-down-7e170136"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/marvell-forecasts-quarterly-revenue-above-estimates-ai-chip-demand-2026-05-27/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/earnings/call-transcripts/2026/05/27/marvell-mrvl-q1-2027-earnings-transcript/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/marvell-technology-earnings-stock-price-ai-0f8a2eb7"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A closeup of a microprocessor circuit board — the kind of custom silicon driving Marvell's AI-fueled growth.",
        "body": """When Matt Murphy, Marvell Technology's CEO, told analysts on Wednesday that his company was seeing "exceptional AI-related bookings," the stock jumped 6.5% in after-hours trading. But the real story behind Marvell's blowout quarter isn't just about numbers — it's about the thousands of Indian engineers designing the silicon that the world's AI infrastructure runs on.

## The Numbers That Matter

Marvell reported fiscal first-quarter revenue of $2.42 billion, up 28% year-over-year. The data center business — which now accounts for 76% of total revenue at $1.8 billion — grew 27% from a year ago. Adjusted earnings hit $0.80 per share, matching estimates.

But the forward guidance is where things get interesting. Marvell now expects $2.7 billion in Q2 revenue (above the $2.6 billion analysts projected), quarterly revenue hitting $3 billion by Q3, and full fiscal year 2027 revenue of nearly $11.5 billion — roughly 40% annual growth. The company also raised its fiscal 2028 outlook to $16.5 billion, a $1.5 billion increase from just last quarter.

The engine behind this: custom AI chips, optical interconnects, and Ethernet switching gear that hyperscale cloud operators are devouring as they spend over $700 billion collectively on AI infrastructure this year.

## The NVIDIA Alliance

Perhaps the most consequential announcement was an expanded partnership with NVIDIA spanning three pillars: silicon photonics collaboration for high-speed optical connectivity, NVLink fusion integration that lets hyperscalers mix custom and merchant chips seamlessly, and AI RAN technology that merges wireless telecom workloads with AI processing.

"Both teams are off to the races," Murphy said. Marvell is positioning itself as the essential bridge between NVIDIA's ecosystem and the custom silicon that cloud giants increasingly prefer for their specific AI workloads.

Custom silicon revenue is expected to more than double in fiscal 2028. The company has line-of-sight to over $10 billion in annual custom silicon revenue by fiscal 2029 — a staggering trajectory for a business segment that barely registered five years ago.

## Where India Fits In

This is where the diaspora angle sharpens. Marvell's India operations — spanning major R&D centres in Pune, Bangalore, and Hyderabad — are not back-office support functions. They are core design centres where engineers architect the custom ASICs, DSPs, and photonic components that power the company's growth.

India's semiconductor design talent is increasingly central to the global chip supply chain. While fabs may be in Taiwan and the US, the design IP that makes a custom AI accelerator valuable originates substantially from Indian engineering teams. When Murphy talks about "every program we looked at a year ago being larger when we look a year later," that expansion requires more designers — and India is where much of that scaling happens.

For the roughly 50,000 Indian semiconductor professionals working in the US, and the larger pool working for chip companies' India offices, Marvell's trajectory is a signal that demand for their skills is accelerating, not plateauing.

## The Investment Case for NRIs

Marvell's stock has more than doubled this year. At a market cap approaching $182 billion, it's no longer the scrappy underdog it once was. But with fiscal 2028 revenue guided to $16.5 billion and operating margins expected to reach 38-40%, the growth runway remains compelling.

The risk? Marvell is prepaying $1 billion to suppliers to secure production capacity, and the GAAP profit actually shrank this quarter due to acquisition-related charges from buying Celestial AI (photonic fabric technology) and XConn Technologies. The company is spending aggressively to capture what it sees as a generational opportunity.

For NRI investors who already track NVIDIA and Micron (which just crossed $1 trillion this week under Sanjay Mehrotra), Marvell represents the other critical layer of the AI stack — the custom silicon and optical plumbing that connects everything together. Indian engineers built a lot of it."""
    },

    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 2: Salesforce Q1 / Agentforce
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Salesforce's Agentforce Hit $1.2 Billion. Indian IT Services Should Be Worried.",
        "subheadline": "The CRM giant beat earnings estimates but its AI agent platform threatens the consulting-heavy model that employs hundreds of thousands of Indians globally.",
        "slug": make_slug("salesforce-agentforce-indian-it-services-threat"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Salesforce is among the top H-1B employers in the US, and Indian IT services firms like TCS, Infosys, Wipro, and HCL derive billions from Salesforce consulting and implementation. The rise of Agentforce — AI agents that automate CRM workflows — directly threatens this labor-intensive model. For Indian-origin Salesforce developers, consultants, and IT services investors, this earnings report is a weather vane.",
        "tags": ["salesforce", "agentforce", "ai-agents", "indian-it-services", "h1b", "enterprise-software"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/salesforce-first-quarter-sales-profit-rise-amid-agentforce-efforts-797ac52f"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/salesforce-sees-quarterly-revenue-below-estimates-amid-ai-disruption-fears-2026-05-27/"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/salesforce-stock-slips-as-earnings-top-estimates-but-outlook-disappoints-11736362"},
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2452127/salesforce-crm-surpasses-q1-earnings-and-revenue-estimates"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804612/pexels-photo-6804612.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern tech workspace — the kind of environment where Salesforce's AI agents may soon replace human consultants.",
        "body": """Salesforce beat Wall Street expectations on Wednesday. Revenue rose 13% to $11.13 billion. Adjusted earnings came in at $3.88 per share, crushing the $3.13 consensus. And yet the stock fell 3% in extended trading, because investors are asking a question that should keep every Indian IT services professional up at night: what happens when AI agents replace the consultants?

## The Agentforce Moment

The centrepiece of Salesforce's earnings call wasn't revenue growth — it was the trajectory of Agentforce, the company's AI agent platform. In its first full year, Agentforce and the broader Data 360 suite reached $3.4 billion in annual recurring revenue. Strip out the $1.1 billion from the Informatica acquisition, and Agentforce alone is at $1.2 billion ARR.

That's not a science project. That's a business.

CEO Marc Benioff has spent months shrugging off the existential dread that AI will shrink the enterprise software market. His pitch: Salesforce isn't selling software licences to human workers — it's selling AI agents that work alongside them, handling tasks that once required armies of consultants to configure, customise, and maintain.

More than half of Agentforce bookings came from existing customers — companies that already have Salesforce implementations and are now layering AI agents on top. Token volumes exploded 152% quarter-over-quarter, a metric that suggests real usage, not just pilot-stage curiosity.

## Why Indian IT Should Pay Attention

Here's the maths that matters for the Indian diaspora: TCS, Infosys, Wipro, HCL Tech, and Cognizant collectively generate billions of dollars annually from Salesforce consulting, implementation, and managed services. These practices employ hundreds of thousands of professionals — many of them in India, many more in the US on H-1B visas.

The Salesforce ecosystem has been a reliable career factory for Indian tech workers. A Salesforce administrator certification was practically a visa to a middle-class American life. But Agentforce changes the unit economics. If an AI agent can handle routine CRM configuration, data migration, and workflow automation — tasks that currently require human consultants billing at $150-300 per hour — the demand curve for those humans bends.

Benioff isn't subtle about this. He's described Agentforce as creating a "digital labour" market. The 2.4 billion "agentic work units" Salesforce delivered last quarter represent tasks that would have previously required human intervention. Scale that by another order of magnitude, and the consulting headcount implications become unavoidable.

## The Soft Guidance Problem

The reason Salesforce stock fell despite the earnings beat: Q2 revenue guidance of $11.27-$11.35 billion came in at the low end of the $11.35 billion consensus. The company also cut its cash flow growth outlook from 9-10% to 4-5%, partly due to a $25 billion debt issuance for an accelerated share buyback.

Investors read this as a signal that even Salesforce isn't immune to the broader concern: if AI makes software cheaper and more efficient, does the total addressable market for enterprise CRM actually shrink? Anthropic and other AI labs are building agent frameworks that could compete directly with Agentforce, and Salesforce's stock has lost a third of its value this year on those fears.

For Indian-origin investors who hold CRM — or Indian IT services stocks that derive revenue from the Salesforce ecosystem — this tension between strong current results and uncertain long-term economics is the central puzzle.

## The Career Calculus

The practical takeaway for Indian tech professionals in the Salesforce orbit: the floor for valuable skills is rising. Basic administration, point-and-click configuration, and report building are exactly the tasks AI agents excel at automating. The premium will shift toward architects who can design complex multi-agent workflows, data engineers who can build the pipelines that feed those agents, and domain specialists who understand the business logic that no AI can intuit from training data alone.

Indian IT services companies are already repositioning. TCS has an AI practice; Infosys has Topaz; Wipro has AI360. But the transition from billing for human hours to delivering AI-augmented outcomes requires fundamentally different economics — and the companies that adapt fastest will capture disproportionate value.

Salesforce's $1.2 billion Agentforce ARR is still small relative to the company's $46 billion revenue target. But it's growing at a pace that suggests this isn't a cycle — it's a structural shift. The Indian IT ecosystem, which built its fortune on labour-cost arbitrage, now faces a world where the arbitrage is between humans and machines."""
    },

    # ──────────────────────────────────────────────────────────────────────
    # ARTICLE 3: India AI Startup Funding Record
    # ──────────────────────────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's AI Startups Raised $5 Billion in One Quarter. The Diaspora Is Watching.",
        "subheadline": "A 73% funding surge, a $600 million sovereign AI bet, and Sarvam's potential unicorn status are reshaping India's claim to be more than just an AI talent exporter.",
        "slug": make_slug("india-ai-startups-5-billion-funding-sovereign"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For NRIs weighing return-to-India decisions or angel investments, India's AI funding surge signals that staying in Silicon Valley is no longer the only path to the AI frontier. Sovereign AI infrastructure (Neysa) and indigenous foundation models (Sarvam) are creating an ecosystem where Indian-origin AI researchers can build world-class companies at home — with Indian investors, Indian data, and Indian government backing.",
        "tags": ["india-ai", "startups", "funding", "sovereign-ai", "neysa", "sarvam", "venture-capital", "nri-investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "StartupPoint.in", "url": "https://startuppoint.in/indian-ai-startups-see-record-q1-funding/"},
            {"name": "Crunchbase News", "url": "https://news.crunchbase.com/venture/global-funding-record-q1-2026/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/ai/artificial-intelligence/as-openai-and-anthropic-soar-where-do-indias-ai-startups-stand-11747844840613.html"},
            {"name": "Inc42", "url": "https://inc42.com/features/shastra-vc-launches-100-mn-fund-to-back-deeptech-startups/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8849295/pexels-photo-8849295.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An abstract illustration of artificial intelligence — the technology powering India's fastest-growing startup category.",
        "body": """Global venture capital deployed a record $330 billion in the first quarter of 2026. Roughly 80% of it went to AI companies. But buried inside that headline number is a subplot that should matter deeply to every NRI with a LinkedIn connection to Bangalore: India's AI startups raised nearly $5 billion in those same three months, up 73% from a year ago.

That's not a rounding error. It's a signal that India is building its own AI economy — not just exporting talent to build someone else's.

## The Numbers

Indian AI-related startups collectively raised approximately $4.96 billion across hundreds of deals in Q1 2026, making AI the third most-funded category in India's startup ecosystem, behind only e-commerce and fintech. The growth is striking: while overall Indian startup funding actually declined 26% year-over-year to $2.3 billion (the denominator that excludes AI-integrated companies across sectors), pure AI investment surged.

AI now accounts for 22-24% of all Indian startup deals, up from roughly 12% two years ago. More telling: 48% of Indian VCs surveyed by Inc42 named AI as the most investment-ready sector. The money is following the conviction.

## Neysa's $600 Million Statement

The single largest deal tells the most important story. Neysa, a Mumbai-based AI cloud platform, raised $600 million in a Series B round — the kind of cheque that was unthinkable for an Indian infrastructure startup just three years ago.

What Neysa is building is sovereign AI infrastructure: high-end GPU clusters that allow Indian enterprises and government agencies to train and run AI models locally, without routing data through American or Chinese cloud providers. In a world where AI sovereignty is becoming a geopolitical priority — the EU has its own push, the UAE has its own — India is making its own play.

For NRIs who've watched India's digital public infrastructure story unfold (UPI, Aadhaar, DigiLocker), this is the AI-native sequel. The government's $1.2 billion AI Mission has already committed funding to 12 startups, including Sarvam (backed by Peak XV and Lightspeed, reportedly in discussions for a $1.5 billion valuation) and Fractal Analytics.

## Beyond Bangalore

One underappreciated trend: AI startup activity is spreading beyond India's traditional tech hubs. Coimbatore-based Aivar Innovations raised $4.6 million in seed funding and has onboarded over 80 customers across fintech, healthcare, logistics, and retail. The team of 100+ is primarily based in Coimbatore, not Bangalore.

Emergent Labs raised $70 million for its AI coding platform. Rocketlane, a Chennai-born enterprise SaaS startup, pulled in $60 million. Temple, working on brain-computer interfaces, raised $54 million. The geographic and sectoral diversity suggests this isn't a single-narrative boom — it's a broad-based shift in where Indian entrepreneurs and investors see opportunity.

## The Diaspora Calculation

For Indian-origin AI researchers and engineers in the US, the career calculus is shifting in ways that would have been absurd five years ago. An AI researcher at Google DeepMind or Meta FAIR earns $400-600K in total compensation, lives in a $3,000/month apartment in the Bay Area, and worries about H-1B renewal timelines. A comparable researcher joining Sarvam or Neysa in Bangalore earns less in absolute terms but enters an ecosystem with government backing, rapidly growing compute infrastructure, and the leverage of building for a 1.4-billion-person market.

The gap isn't closed — American AI labs still lead on frontier research — but it's narrowing faster than anyone projected. And for NRIs who want to invest rather than relocate, India's AI sector now offers real deal flow. Shastra VC launched a $100 million fund specifically for deep-tech startups. Peak XV Partners was the most active AI investor in Q1 with 16 deals.

## The Sobriety Check

Not everything is rosy. Fewer than 10% of Indian VCs are willing to pay premium valuations for AI startups, and 56% believe India's AI ecosystem still trails China. The country's AI infrastructure — particularly GPU availability — remains constrained relative to the US and China. And the government's AI Mission, while directionally right, has been criticised for prioritising large-platform infrastructure over startup-specific incentives.

There's also the concentration risk: strip out Neysa's $600 million, and the remaining AI deals average much smaller. India's AI ecosystem is producing volume but not yet the kind of $10-billion-plus outcomes that define the US and Chinese AI landscapes.

Still, the trajectory is unmistakable. India raised more in AI funding in one quarter than it did in the entire calendar year of 2023. For a diaspora that has spent decades building AI infrastructure for American companies, the notion that India might build its own is no longer aspirational. It's underway."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n📊 Published {len(articles)} articles at {now}")
