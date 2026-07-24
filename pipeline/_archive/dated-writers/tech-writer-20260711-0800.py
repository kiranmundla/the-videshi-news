#!/usr/bin/env python3
"""Technology writer — July 11, 2026 08:00 PT run"""
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

# ─── ARTICLE 1: AWS $48 Billion India Bet ───

art1_body = """Amazon has raised its India investment commitment to $48 billion through 2030, adding $13 billion in fresh spending on artificial intelligence and cloud infrastructure. The announcement, made by CEO Andy Jassy, comes just six months after the company pledged $35 billion and makes India one of Amazon's largest single-country bets outside the United States.

## Where the Money Goes

The additional $13 billion will expand AWS data centre capacity in Mumbai and Hyderabad, India's two cloud regions. AWS launched in Mumbai in 2016 and added Hyderabad in 2022; between them, the two regions now underpin everything from Indian fintech apps to government digital identity systems. Earlier this year, AWS also revealed plans for a $430 million facility near Taloja, in Navi Mumbai, suggesting the buildout is accelerating across the western corridor.

Jassy framed the investment in terms that deliberately echo New Delhi's own vocabulary. "Our business priorities align with India's priorities of democratising access to AI, digitising small businesses, creating jobs, and enabling exports," he said, invoking Prime Minister Narendra Modi's "Viksit Bharat" vision of a developed India by 2047.

## The Hyperscaler Land Grab

Amazon is not investing in a vacuum. Google broke ground on a $15 billion AI hub in Visakhapatnam in April 2026, anchored by a gigawatt-scale data centre campus and three new subsea cables connecting India to the United States. Microsoft committed $17.5 billion to Indian AI infrastructure in December 2025, its largest single-country spend in Asia. Meta, meanwhile, has been quietly expanding compute capacity across Indian metros for its Facebook and Instagram workloads.

Together, the three American hyperscalers have pledged more than $80 billion to Indian infrastructure in the past eighteen months — a figure that dwarfs India's own ₹10,000 crore IndiaAI Mission budget and underscores how deeply the country's digital future is being underwritten by foreign capital.

## Why Indian Americans Should Watch This

For the roughly 300,000 Indians working on H-1B and L-1 visas at American tech firms, the data centre arms race in India carries a dual signal. On one hand, it creates thousands of high-skill jobs in India — cloud architects, AI researchers, security engineers — that could make "return migration" more financially attractive than it has been in years. On the other, it deepens the cross-border dependencies that make Indo-American tech careers uniquely resilient: an Indian-American AWS engineer in Virginia is now part of the same infrastructure story as a site reliability engineer in Hyderabad.

For NRI investors, the sheer density of hyperscaler commitments is turning Indian data centre real estate and supporting infrastructure — from power generation to fibre optics — into a distinct asset class. Yotta Data Services raised $150 million this week at a valuation of roughly ₹37,000 crore, and its IPO plans remain on track.

The question is no longer whether India becomes a global AI infrastructure hub. It is whether the country can train, retain, and deploy enough engineers to fill the data centres it is building."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Amazon Raises Its India Bet to $48 Billion. That Is More Than Most Countries Spend on AI.",
    "subheadline": "A fresh $13 billion for data centres in Mumbai and Hyderabad puts AWS at the centre of a hyperscaler land grab that Google and Microsoft are already waging across the subcontinent.",
    "slug": make_slug("amazon-aws-48-billion-india-ai-cloud-infrastructure"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "The hyperscaler investment wave creates thousands of cloud and AI jobs in India while deepening the cross-border career pathways that Indian-American tech professionals depend on.",
    "tags": ["aws", "amazon", "india-tech", "ai-infrastructure", "data-centers", "cloud-computing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Data Center Dynamics", "url": "https://www.datacenterdynamics.com/en/news/aws-pledges-further-13bn-investment-in-ai-and-cloud-infrastructure-in-india/"},
        {"name": "Barron's / BofA Securities", "url": "https://www.barrons.com/articles/ai-spending-alphabet-amazon-meta-e63f4dac"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/google-amazon-increase-data-center-capacity-plans/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Amazon_AWS_us-west-2_beach_AZ.jpg/1280px-Amazon_AWS_us-west-2_beach_AZ.jpg",
    "image_caption": "An Amazon Web Services data centre facility in the western United States",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ─── ARTICLE 2: EXL Acquires iMerit for $310M ───

art2_body = """Two Indian-origin companies have struck the kind of deal that defines where the AI industry is actually headed. EXL, the Nasdaq-listed data analytics firm led by chairman and CEO Rohit Kapoor, has agreed to acquire iMerit, a California-based AI data training company founded by Radha Basu, for up to $310 million. The transaction — $170 million upfront, with $140 million in earnouts over two years — is expected to close this quarter.

## The Unsexy Layer That Makes AI Work

If the AI supply chain were a restaurant, the foundation model companies would be the celebrity chefs and the GPU makers would be the equipment suppliers. iMerit is the prep kitchen — the company that labels, annotates, and curates the data that those models are trained on. It is not glamorous work, but without it, every large language model would hallucinate more than it already does.

Founded in 2012 and backed by Khosla Ventures and the Michael & Susan Dell Foundation, iMerit has built a proprietary platform called Ango that supports chain-of-thought reasoning evaluation, red teaming, and multimodal assessments for foundation models. It also maintains what it calls a Scholars network — physicians, scientists, engineers, and linguists who provide expert feedback for reinforcement learning workflows. In short, iMerit occupies the exact layer where AI models are taught to be less wrong.

## What EXL Gets

EXL plans to integrate Ango with its own suite of AI platforms — EXLerate.ai, EXLdata.ai, and EXLdecision.ai — to build what it calls an end-to-end system covering data preparation, model evaluation, and enterprise-scale deployment. The combined entity will serve healthcare, insurance, banking, and capital markets, with a new push into autonomous systems, robotics, and physical AI.

"As organisations reimagine their businesses with AI, success requires industry-specific data, rigorous evaluation and reinforcement learning," Kapoor said. "The acquisition of iMerit strengthens EXL's AI strategy and ability to help clients move from experimentation to production."

Basu, iMerit's founder, framed it in complementary terms: "We see EXL as an ideal leader in this defining moment for AI. We can build on our work with AI innovators and bring those insights to companies seeking to unlock their proprietary data."

## The Diaspora Thread

Both companies are products of the Indian tech diaspora. EXL was founded in 1999 and is headquartered in New York, with significant operations in India. Kapoor, who has led the company since 2012, has steered it from a traditional business process outsourcing outfit into a data and AI company with a $4.5 billion market capitalisation. Basu, a veteran of Hewlett-Packard's Indian operations, started iMerit with a social mission — many of its data annotators were recruited from underserved communities in Kolkata and other Indian cities.

The deal follows EXL's 2024 acquisition of ITI Data and arrives as McKinsey estimates that 78 per cent of organisations now use AI in at least one business function, up from 55 per cent in 2023. The AI data services market, worth roughly $3 billion today, is projected to grow at 25 per cent annually through 2030.

For Indian-American professionals working at AI companies across the Bay Area, the EXL-iMerit combination is a signal: the diaspora is not just building AI at Google and Microsoft. It is quietly assembling the infrastructure that makes everyone else's AI work."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Two Indian-Origin Companies Just Struck a $310 Million Deal for the Unsexy Work That Makes AI Actually Function",
    "subheadline": "EXL's acquisition of iMerit brings together Indian-diaspora-led data analytics and AI model training into one company that covers the full pipeline from data labelling to enterprise deployment.",
    "slug": make_slug("exl-acquires-imerit-310-million-ai-data-training"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Both EXL and iMerit are led by Indian-origin founders and employ thousands across India and the US — the deal shows diaspora companies shaping the AI data value chain, not just consuming it.",
    "tags": ["ai", "acquisitions", "indian-tech", "data-labeling", "enterprise-ai", "exl", "imerit"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/exl-to-acquire-ai-data-firm-imerit-for-310-million-11750858024082.html"},
        {"name": "EXL Official", "url": "https://www.exlservice.com/newsroom/exl-to-acquire-imerit"},
        {"name": "Entrepreneur India", "url": "https://india.entrepreneur.com/article/exl-to-acquire-imerit-in-310-million-ai-deal/484093"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17483871/pexels-photo-17483871.png?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A 3D visualization of neural network connections representing AI data infrastructure",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ─── ARTICLE 3: Infosys Agentic AI in US Hospitals ───

art3_body = """India's second-largest IT services company is embedding artificial intelligence agents inside American hospitals. Infosys has entered a strategic collaboration with Sentara, a not-for-profit healthcare system operating across Virginia and North Carolina, to deploy its Topaz Fabric platform across hospital operations, IT systems, and clinical support functions.

## What Topaz Fabric Actually Does

Topaz Fabric is Infosys's answer to a problem every large enterprise is wrestling with: how to move AI from isolated pilot projects to production-grade systems that run at scale. Described internally as a "purpose-built agentic services suite," the platform unifies infrastructure, models, data, applications, and workflows into a composable, agent-ready ecosystem. In plainer English, it lets hospitals connect AI tools to their existing systems — electronic health records, scheduling software, billing platforms — without rebuilding everything from scratch.

The collaboration with Sentara spans three domains: care management, employee productivity, and digital front-office experiences. The intent, according to Infosys, is to align AI initiatives with "real-world healthcare priorities" while maintaining the enterprise guardrails and regulatory compliance that healthcare demands.

Venky Ananth, executive vice president and global head of healthcare at Infosys, said the partnership would "unlock AI value by building a strong enterprise AI foundation" and "accelerate operationalising across hospital systems, leading to real efficiency gains for patients."

## The AI-First Pivot

The Sentara deal is part of a broader transformation at Infosys under CEO Salil Parekh, who has repositioned the company around what he calls an "AI-first strategy" spanning six core areas: AI engineering, data, process transformation, legacy modernisation, physical AI, and trust. Every client conversation now includes AI, Parekh told analysts during the company's most recent earnings call — a structural shift rather than a marketing exercise.

That shift is showing up in the numbers, albeit with a paradox attached. Infosys won $14.9 billion in large deals in Q4 FY26, with AI embedded in virtually all of them. Yet its revenue guidance for FY27 — growth of just 1.5 to 3.5 per cent — reflects the compression that AI simultaneously creates. Tasks that once required hundreds of billable hours are now executed faster and cheaper. Infosys itself describes the tension as a balance between "growth and compression," where new AI-led opportunities must outrun the decline in legacy revenue.

## Why the Diaspora Should Pay Attention

For the tens of thousands of Indian engineers working at Infosys's US offices — and the many more supporting American clients from Bengaluru, Pune, and Hyderabad — the Sentara partnership signals what the next decade of Indian IT looks like. It is not about staffing help desks or maintaining legacy Java applications. It is about deploying autonomous AI agents inside regulated American industries where mistakes carry real consequences.

Healthcare, in particular, is a proving ground. Unlike retail or finance, where an AI error costs money, a healthcare AI failure can cost lives. Infosys's ability to demonstrate responsible, production-grade AI in hospital settings could unlock a much larger market: American healthcare IT spending exceeds $200 billion annually, and the share allocated to AI is growing rapidly.

For NRI healthcare professionals — doctors, administrators, and health tech entrepreneurs — the Infosys-Sentara model also represents an emerging opportunity. As AI agents handle administrative burden, the clinical workforce can focus on what machines still cannot do: exercise judgment, build trust, and treat patients as people rather than data points."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Infosys Is Putting AI Agents Inside American Hospitals. The Proving Ground Is a Virginia Health System.",
    "subheadline": "India's second-largest IT firm deploys its Topaz Fabric agentic platform across Sentara's hospital operations, betting that healthcare is where enterprise AI either earns trust or loses it.",
    "slug": make_slug("infosys-sentara-agentic-ai-hospitals-topaz-fabric"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian engineers at Infosys are building production-grade AI systems for regulated American healthcare — a shift from legacy IT services that redefines what Indian tech talent does in the US.",
    "tags": ["infosys", "ai", "healthcare", "agentic-ai", "indian-it", "enterprise-ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Infosys Official", "url": "https://www.infosys.com/newsroom/press-releases/2026/collaborates-sentara-ai-healthcare.html"},
        {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/infosys-limited-infy-partners-with-sentara-to-enable-ai-integration-and-use-in-hospitals-1503817/"},
        {"name": "PR Newswire", "url": "https://www.prnewswire.com/news-releases/infosys-collaborates-with-sentara-to-unlock-ai-value-and-scale-enterprise-ai-adoption-in-healthcare-services-302463217.html"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6011598/pexels-photo-6011598.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A clinician using a digital tablet, representing the integration of AI technology in healthcare settings",
    "image_attribution": "Pexels",
    "body": art3_body,
}

# ─── INSERT ───

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:70]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
