#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-30 02:00 PDT run"""

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


# ────────────────────────────────────────────────────────────────────────
# ARTICLE 1: OpenAI India MD
# ────────────────────────────────────────────────────────────────────────

art1_body = """OpenAI has done something it rarely does: it has hired a country head before it has a country-sized business to manage. Prabhjeet Singh, who spent the last eleven years building Uber's Indian operations from a handful of cities into a ride-hailing, auto-rickshaw, and shuttle empire, will join as OpenAI's first Managing Director for India in September.

The appointment is less about what Singh will manage today than what OpenAI expects to manage tomorrow. India is already the company's second-largest market globally, with over 100 million weekly active ChatGPT users and a top-five ranking for API usage. The country generates enormous consumer traffic but relatively modest enterprise revenue — exactly the gap Singh has been hired to close.

## The Uber Playbook, Reloaded

Singh's career reads like a case study in scaling American platforms for Indian conditions. After degrees from IIT Kharagpur and IIM Ahmedabad — credentials that need no translation in Silicon Valley — he cut his teeth at Lehman Brothers in London and McKinsey before joining Uber in 2015 as head of strategy.

At Uber, he didn't just localise the app. He rebuilt its product lines: Auto for the three-wheeler market, Moto for two-wheelers, Shuttle for fixed-route commuters. He integrated Uber with ONDC, India's open commerce network, and pushed electric mobility partnerships. By the time he left, Uber India was no longer the American ride-hailing app that happened to operate in India — it was, functionally, a different product.

OpenAI needs a similar transformation. ChatGPT's free tier has massive adoption in India, driven by students, developers, and curious professionals. But converting that into paid subscriptions, enterprise contracts, and government partnerships requires someone who understands how Indian institutions buy software — slowly, with committees, and almost never at American price points.

## The Competitive Landscape

Singh walks into a market where the competition is closing fast. Google's Gemini has deep integration with Android, which commands over 95% smartphone market share in India. Anthropic recently reopened access to its Mythos 5 model after initially restricting Indian users. Meta's Llama models are free and increasingly capable. Sarvam AI, backed by India's own government-funded compute, is building domain-specific models in Indian languages.

OpenAI's edge is brand recognition and developer loyalty. Its risk is pricing itself out of a market where monthly ChatGPT Plus subscriptions cost more than many Indians' daily wages.

## What This Means for NRIs

For Indian tech professionals in the US, this appointment signals a structural shift. OpenAI is not just hiring an India head — it's building an India operation. New offices in Mumbai and Bengaluru are planned for later this year, joining the existing New Delhi presence established in November 2025. That means AI engineering jobs, partnership roles, and product positions that didn't exist six months ago.

For NRI investors watching the AI infrastructure play, the question is whether OpenAI can replicate the consumer-to-enterprise conversion that Jio managed with telecom. Singh's Uber tenure suggests he understands that Indian market share and Indian revenue are related but distinct achievements. The first is easy. The second is the actual job."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Hired an IIT-IIM Grad to Run India. He Built Uber's Indian Empire First.",
    "subheadline": "Prabhjeet Singh, who turned Uber from a ride-hailing app into an auto-rickshaw platform, will lead OpenAI's push into its second-largest market.",
    "slug": make_slug("openai-prabhjeet-singh-india-md-uber-iit"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "IIT-IIM alumni pipeline now reaches frontier AI leadership; OpenAI's India expansion means new AI jobs in Mumbai/Bengaluru for returning NRIs and signals pricing/product changes that affect diaspora developers using ChatGPT APIs.",
    "tags": ["openai", "india", "ai", "iit", "uber", "chatgpt", "silicon-valley"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/"},
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/tech/openai-appoints-former-uber-india-chief-prabhjeet-singh-as-its-first-india-managing-director"},
        {"name": "afaqs!", "url": "https://www.afaqs.com/news/digital/uber-india-head-prabhjeet-singh-joins-openai-as-india-managing-director"},
        {"name": "Techlusive", "url": "https://www.techlusive.in/news/openai-makes-a-big-india-bet-hires-former-uber-india-chief-to-lead-operations"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman; the company has appointed former Uber India president Prabhjeet Singh as its first India Managing Director",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ────────────────────────────────────────────────────────────────────────
# ARTICLE 2: Taiwan Raids Super Micro / Nvidia Chip Smuggling
# ────────────────────────────────────────────────────────────────────────

art2_body = """Taiwanese prosecutors raided the offices of Super Micro Computer, data centre operator Chief Telecom, and distributor Albatron Technology on Monday, widening an investigation into the alleged smuggling of Nvidia AI chips to China worth $2.5 billion. Shares of Super Micro fell more than 7% in US trading.

The raids searched six residences and three affiliated companies, according to Bloomberg. Taiwan's Keelung District Prosecutors Office confirmed the action was part of an ongoing probe into the illegal export of Super Micro servers containing advanced Nvidia GPUs — the same chips the United States has banned from reaching China since 2022.

## Hair Dryers and Hollow Servers

The scheme, as laid out in a US Department of Justice indictment filed in March, is almost comically elaborate. Super Micro's co-founder Yih-Shyan Liaw, sales manager Ruei-Tsang Chang, and a contractor were charged with routing US-made servers from Taiwan through a Southeast Asian intermediary — reportedly Bangkok-based OBON Corp, linked to Thailand's national AI initiative — and onwards to China.

The intermediary's staff allegedly used hair dryers to transfer serial number stickers from real servers to dummy units, which were then warehoused to pass audits. The actual GPU-laden servers, stripped of identifying marks, were shipped to China in unmarked boxes. The auditor tasked with checking compliance was reportedly "off-site enjoying entertainment" paid for by the pass-through company when inspections were due.

Between 2024 and 2025, the operation moved approximately $2.5 billion in servers, including Nvidia's latest B200 and H200 chips. Bloomberg has reported that Alibaba was among the end customers, though the company has denied any relationship with Super Micro or the intermediaries named in the indictment.

## The Indian Semiconductor Connection

For Indian tech professionals and policymakers, this story is instructive in two ways.

First, enforcement is tightening. Taiwan's willingness to raid a major American-founded company's local offices signals that chip export controls are no longer just a US-China bilateral issue — they are becoming a supply-chain-wide compliance regime. Indian companies building hardware for global markets, including Tata Electronics (which assembles iPhones and manufactures chips at Dholera) and the upcoming Micron fabrication plant in Gujarat, will need to demonstrate they can operate within this regime. Being "trusted" in the semiconductor supply chain is increasingly a competitive advantage, not just a regulatory checkbox.

Second, the demand is real. China was willing to pay billions to circumvent export controls because it cannot manufacture these chips domestically. That same demand, served legally, is what India's semiconductor mission is trying to capture. When the US and its allies restrict chip flows to adversaries, they need alternative manufacturing hubs. India has positioned itself as one, but the Tata breach and ongoing fab delays suggest the gap between aspiration and execution remains wide.

## What This Means for NRIs

For Indian engineers working at Nvidia, Qualcomm, Broadcom, or any chip-adjacent company in the Bay Area, this probe is a reminder that export compliance is now a career-affecting issue, not just a legal department concern. The DOJ charges carry up to 20 years in prison. Companies are placing employees on leave and terminating contractors over these allegations.

For NRI investors holding semiconductor stocks, the market's 7% haircut on Super Micro is a preview of the volatility that enforcement actions can trigger across the chip supply chain. India's semiconductor ambitions — and the stocks of companies like Tata Electronics and Vedanta-Foxconn that are tied to them — will increasingly be priced not just on technical execution but on geopolitical trust."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Taiwan Just Raided Super Micro's Offices Over $2.5 Billion in Missing Nvidia Chips. India Should Be Watching.",
    "subheadline": "The chip smuggling probe expands as prosecutors search six homes and three companies. For India's semiconductor ambitions, the lesson is about trust as much as technology.",
    "slug": make_slug("taiwan-super-micro-raid-nvidia-chip-smuggling-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian engineers at chip companies face heightened export compliance scrutiny; India's semiconductor ambitions (Tata, Micron Gujarat) depend on being seen as a trusted manufacturing hub in the US-led chip export control regime.",
    "tags": ["nvidia", "semiconductor", "super-micro", "taiwan", "china", "chips", "export-controls", "india-semiconductor"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Bloomberg via Inshorts", "url": "https://inshorts.com/en/news/taiwan-raids-super-micro-in-nvidia-chip-smuggling-probe-report-1751227800368"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/taiwanese-authorities-reportedly-raid-supermicro-in-move-that-could-signal-big-change-for-ai-chip-exporters-2000643908"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/us-suspects-nvidia-chips-smuggled-alibaba-via-thailand-bloomberg-news-reports-2026-05-09/"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/article/smci-stock-slides-7-taiwan-authorities-raid-super-micro-offices-in-ai-chip-export-probe-says-report-2000643867"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Data centre server racks of the kind used in alleged Nvidia chip smuggling operations",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ────────────────────────────────────────────────────────────────────────
# ARTICLE 3: Nasscom Indian IT $12B AI Revenue
# ────────────────────────────────────────────────────────────────────────

art3_body = """Indian IT services companies are already generating $10 to $12 billion in annual revenue from artificial intelligence work, according to new data from Nasscom presented at its US CEO Forum in New York. Nearly a quarter of technology services firms have moved AI projects from experimentation into production, and 85% of the top 25 providers now operate agentic AI platforms.

The numbers land at a peculiar moment. Two days earlier, JP Morgan cut its outlook for the Indian IT sector, warning that AI-driven productivity gains are compressing project sizes and deflating revenue per engagement. Nasscom's data tells the opposite story — that AI is creating new categories of work faster than it is destroying old ones.

Both can be true simultaneously. The question for investors and professionals is which effect dominates.

## The Bull Case, in Nasscom's Numbers

The industry body's argument rests on three pillars. First, the current $10-12 billion in AI services revenue represents roughly 3-4% of the Indian IT sector's total $315 billion annual revenue — small but growing at a rate that dwarfs the overall sector's 6% growth. Second, more than 2 million professionals across the industry are now skilled in AI, with 100,000 to 200,000 trained in advanced capabilities like model fine-tuning, retrieval-augmented generation, and agent orchestration. Third, agentic AI alone is expected to unlock $300 to $400 billion in new addressable spending by 2030 — spanning legacy modernisation, AI operations, cybersecurity, and governance.

"The next phase of AI is not about experimentation alone," said Cognizant CEO Ravi Kumar S., who chairs the Nasscom US CEO Forum. "Enterprises now need to convert AI capability into production value. That requires data readiness, workflow redesign, secure deployment, governance and change management. These are areas where Indian technology services companies have deep experience."

## The Bear Case, in Plain Sight

The counterargument is structural. AI compresses delivery timelines. A testing suite that took a 50-person team three months can now be generated in days. Code migration projects that drove large-deal revenue are increasingly handled by AI agents with human supervision. When the unit of work shrinks, revenue per project falls — even if the number of projects rises.

Wipro CEO Srini Pallia acknowledged the tension earlier this year at Davos: AI-assisted software development costs about 25% less, with significant productivity gains in coding and testing. His bet is that this translates into "new and more projects" rather than a shrinking pie. But JP Morgan's analysts remain unconvinced, noting that FY27 guidance from major Indian IT firms has been cut for the second consecutive year.

## The Agentic Wildcard

The variable that could tilt the balance is agentic AI — autonomous software agents that can execute multi-step workflows, not just answer questions. If enterprises adopt agents at the rate Nasscom projects, Indian IT companies are well-positioned as orchestrators: the firms that connect AI models to legacy enterprise systems, manage data pipelines, handle compliance, and keep the whole stack running.

This is, essentially, the same systems integration work that built the industry — repackaged for the AI era. Whether that repackaging commands premium pricing or commodity margins will determine whether the $300-400 billion addressable market materialises as revenue or remains a PowerPoint projection.

## What This Means for NRIs

For Indian Americans working in or investing in the IT services sector, the Nasscom data offers cautious reassurance. The industry is not being made obsolete by AI — it is adapting, as it has through every previous technology wave. TCS, Infosys, and HCL are hiring AI specialists, not just cutting traditional headcount.

But the transition is uneven. Engineers who can build and deploy AI systems command premium compensation. Those doing routine coding, testing, or documentation face automation pressure. For NRIs considering a return to India's tech sector, the landing zone has shifted: Bengaluru and Hyderabad want AI engineers, not more Java developers. The $12 billion figure is real. The question is whether your skill set is part of it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian IT Is Already Making $12 Billion from AI. The Hard Part Is What Comes Next.",
    "subheadline": "Nasscom says a quarter of Indian tech firms have moved AI from pilot to production. But JP Morgan's analysts see revenue compression, not expansion. Both sides have a point.",
    "slug": make_slug("nasscom-indian-it-12-billion-ai-revenue-agentic"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors tracking Indian IT stocks (TCS, Infosys, Wipro) need to parse the gap between Nasscom's bullish AI revenue data and JP Morgan's bearish guidance cuts; engineers considering return-to-India moves should note the shift toward AI-specialist hiring.",
    "tags": ["nasscom", "indian-it", "ai", "tcs", "infosys", "wipro", "cognizant", "agentic-ai", "nri-investors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/indian-it-industry-generates-up-to-12b-from-ai-services-nasscom/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/nasscom-says-ai-could-unlock-usd-400-billion-opportunity-for-indian-it-services/article69737490.ece"},
        {"name": "USA Today", "url": "https://usatodaycom.com/indias-ai-services-revenue-touches-12-billion-as-adoption-moves-beyond-pilots-nasscom/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/wipro-ceo-sees-growing-demand-indias-it-services-ai-2026-01-21/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16323580/pexels-photo-16323580.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Software developers at an Indian technology services firm; the industry now generates $10-12 billion annually from AI services",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ────────────────────────────────────────────────────────────────────────
# INSERT
# ────────────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
