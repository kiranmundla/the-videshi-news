#!/usr/bin/env python3
"""Tech writer — 2026-06-28 02:00 PDT run. 3 articles."""

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
    return slug[:70].rstrip('-') + "-20260628"


# ─────────────────────────────────────────────
# ARTICLE 1: OpenAI hires Prabhjeet Singh
# ─────────────────────────────────────────────

art1_body = """OpenAI has named Prabhjeet Singh, the outgoing president of Uber India and South Asia, as its first managing director for India — the clearest signal yet that the ChatGPT maker considers the subcontinent central to its commercial future, not merely a source of engineering talent.

Singh will join in September and report to Kiran Mani, the recently appointed managing director for Asia Pacific and Japan. His mandate spans consumer growth, enterprise adoption, partnerships, regulatory engagement and day-to-day operations — essentially everything that determines whether OpenAI's products become as embedded in Indian daily life as the ride-hailing service he helped scale.

## Why India, and Why Now

India is already OpenAI's second-largest market after the United States, measured by weekly active ChatGPT users, and ranks among its top five for API usage. The company opened its first office in New Delhi last August and has since announced expansions into Mumbai and Bengaluru. It has struck partnerships spanning higher education, enterprise payments, AI-powered commerce and data-centre infrastructure, with Reliance and Tata Group among its early corporate allies.

The timing is strategic. Anthropic's decision on 12 June to restrict access to its latest models outside the United States rattled Indian developers and policymakers, raising the spectre of an AI access divide between countries that build frontier models and those that merely consume them. OpenAI's aggressive India push — appointing a senior country head, opening multiple offices, courting enterprise clients — positions it as the reliable Western AI partner India can lean on while its own sovereign-model ambitions (BharatGen's Param-2, Sarvam AI, Krutrim) mature.

## The Uber Playbook

Singh spent nearly eleven years at Uber, joining in 2015 as head of strategy and rising to president in 2020. He oversaw operations across India, Sri Lanka and Bangladesh — markets defined by fierce local competition, regulatory complexity and price-sensitive consumers. Before Uber, he worked at McKinsey and Lehman Brothers, the latter giving him a front-row seat to institutional collapse, an experience unlikely to breed complacency.

The Uber years are directly relevant. OpenAI faces the same challenges in India that Uber once did: a vast addressable market, entrenched local competitors (Google's Gemini is deeply embedded through Android and Search), regulatory uncertainty, and a user base that expects world-class products at Indian price points. Singh's track record suggests he understands this terrain.

## What It Means for Indian Tech Workers

For the tens of thousands of Indian engineers working on AI — whether at OpenAI's own expanding India team, at its enterprise partners, or at rival firms — the appointment signals a market maturing beyond early adoption. OpenAI is not just selling ChatGPT subscriptions; it is building an ecosystem. It has been hiring AI deployment engineers, developer experience engineers, a developer marketing lead and solutions engineers in India.

For NRIs in the Valley and elsewhere, the move reinforces a pattern: India is no longer the back office. It is the frontline market where AI's consumer economics will be won or lost. An Indian professional running OpenAI's second-largest market is not a diversity checkbox — it is an operational necessity.

## The Road Ahead

Singh inherits a market where competition is intensifying by the week. Google recently launched expanded Gemini features for Indian languages. Anthropic and AWS opened an agentic AI accelerator in Bengaluru. India's own sovereign-AI startups have collectively raised over $1 billion in recent months. The question is not whether India will be an AI power — it is which platforms Indian businesses and consumers will build on.

OpenAI is betting that the person who figured out ride-hailing in one of the world's most complex markets can now do the same for artificial intelligence. It is a bet on execution, not just technology — and in India, execution has always been the harder problem."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Poaches Uber India's President to Run Its Second-Largest Market",
    "subheadline": "Prabhjeet Singh, who spent a decade scaling Uber across India, Sri Lanka and Bangladesh, becomes OpenAI's first managing director for the country as the AI race in the subcontinent intensifies.",
    "slug": make_slug("openai-prabhjeet-singh-uber-india-md-chatgpt"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is OpenAI's second-largest market; the appointment signals that Indian professionals aren't just building AI — they're running the business, with direct implications for NRI engineers, enterprise partners, and investors tracking the AI race.",
    "tags": ["openai", "india-ai", "indian-tech-leaders", "chatgpt", "uber"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-taps-ex-uber-regional-chief-india-leadership-2026-06-27/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/27/openai-poaches-uber-india-chief-to-lead-its-biggest-market-outside-the-us/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/amp/economy-and-policy/openai-names-ex-uber-india-president-prabhjeet-singh-as-india-md"},
        {"name": "Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/openai-appoints-prabhjeet-singh-as-india-managing-director/article69748260.ece"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16587315/pexels-photo-16587315.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A smartphone displaying the ChatGPT app by OpenAI, whose India market has grown into its second-largest globally",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Qualcomm / Akash Palkhiwala
# ─────────────────────────────────────────────

art2_body = """Qualcomm's stock surged more than 12 per cent in after-hours trading on Wednesday after the company's Indian-origin CFO and COO, Akash Palkhiwala, unveiled a data-centre revenue target that would have been unthinkable for a smartphone-chip company five years ago: $15 billion by fiscal 2029.

The announcement, made at the chipmaker's investor day in San Diego, came packaged with two headline customers — Meta and Microsoft — and a new CPU architecture called Dragonfly C1000 designed specifically for AI workloads. Qualcomm also raised its total non-handset revenue target to $40 billion by 2029, nearly double its previous guidance of $22 billion, and said handsets would account for just one-third of its chip revenue by then.

"We will be truly diversified," Palkhiwala said — a line that reads as both a promise and a concession that Qualcomm's phone-chip dependency has become a strategic liability.

## Palkhiwala's Quiet Rise

Akash Palkhiwala does not carry the public profile of a Sundar Pichai or a Satya Nadella, but the Ahmedabad-born engineer may be orchestrating one of the most consequential corporate pivots in the semiconductor industry. A mechanical engineering graduate from L.D. College of Engineering in Gujarat, he earned an MBA from the University of Maryland and joined Qualcomm in 2001 — effectively spending his entire career at one company. He became CFO in 2019 and was elevated to the dual CFO-COO role in 2024.

What sets Palkhiwala apart is the scope of his remit. As both finance chief and operations chief, he controls not just the numbers but also Qualcomm's global go-to-market strategy and IT infrastructure. When he says the data-centre business will generate $5 billion in fiscal 2027 alone — with $1 billion from custom-chip customers — he is the person accountable for delivering it.

## The Meta and Microsoft Deals

The investor day's centrepiece was the Dragonfly C1000, a 250-plus-core CPU designed for AI data centres with high memory bandwidth, PCIe Gen 7 and CXL connectivity. Meta CEO Mark Zuckerberg tied the partnership to power efficiency: Qualcomm, he said, has spent decades figuring out how to get "the most performance out of every watt." The Dragonfly C1000 will power Meta's next-generation server fleet when it enters production in the second half of 2028.

Microsoft, for its part, will use Qualcomm's new High Bandwidth Compute (HBC) chip architecture — a novel packaging of logic and memory that uses cheaper smartphone-grade memory instead of the pricey high-bandwidth chips that Nvidia relies on. Microsoft said the approach could unlock "significant improvements in cost and performance" for next-generation AI infrastructure. This matters because data centres are the fastest-growing and most capital-intensive segment of the tech industry, and power consumption is the binding constraint.

Qualcomm's pitch is essentially that the engineering discipline that made it the undisputed leader in mobile processors — wringing maximum performance from minimal power — translates directly to data centres, where every watt saved at hyperscale is multiplied millions of times.

## The Nvidia Challenge

None of this happens in a vacuum. Qualcomm is taking on Nvidia's dominant CUDA ecosystem, which has locked in millions of AI developers. To that end, Qualcomm's $3.9 billion acquisition of Modular — an AI software startup that has built a neutral programming layer across chips from Nvidia, AMD and others — is a direct assault on CUDA's moat. CEO Cristiano Amon has been frank about the timing: "A lot of people ask, is that too late? It's never too late for Qualcomm."

## What NRIs Should Watch

For Indian American engineers and investors, the Qualcomm transformation story has several implications. Qualcomm employs thousands of Indian engineers across its San Diego headquarters and its Hyderabad and Bengaluru design centres. A pivot toward data-centre chips means new hiring in areas such as server architecture, AI inference and custom silicon — skills that overlap heavily with India's engineering talent base. And for NRI investors, the $40 billion non-handset revenue target reframes Qualcomm from a cyclical phone-chip play into an AI infrastructure bet — a fundamentally different investment thesis."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Qualcomm's Indian-Origin CFO Just Unveiled a $15 Billion Data Centre Bet. Meta and Microsoft Signed Up.",
    "subheadline": "Akash Palkhiwala, an Ahmedabad-born engineer who has spent his entire career at Qualcomm, is steering the chipmaker's most ambitious pivot — from phone chips to AI infrastructure — with backing from two of tech's biggest spenders.",
    "slug": make_slug("qualcomm-palkhiwala-15-billion-data-centre-meta-microsoft"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Qualcomm's Indian-origin CFO Akash Palkhiwala is leading a $40 billion diversification bet; the pivot means new hiring in server and AI chip design — areas that overlap with India's engineering talent and Qualcomm's large Hyderabad and Bengaluru design centres.",
    "tags": ["qualcomm", "indian-tech-leaders", "semiconductors", "ai-infrastructure", "data-centres"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-forecasts-15-billion-data-center-chip-sales-by-2029-shares-soar-2026-06-25/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-stock-price-data-center-meta-investor-day-c3ab8d04"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/qualcomms-stock-is-soaring-as-these-big-numbers-excite-wall-street-6e3e5eae"},
        {"name": "Qualcomm Investor Relations", "url": "https://investor.qualcomm.com/news-events/press-releases/detail/qualcomm-appoints-akash-palkhiwala-chief-financial-officer"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Qualcomm_Headquarters_La_Jolla.jpg/1280px-Qualcomm_Headquarters_La_Jolla.jpg",
    "image_caption": "Qualcomm headquarters in San Diego, where the company unveiled its $15 billion data centre revenue roadmap",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 3: Nasscom AI $400B opportunity
# ─────────────────────────────────────────────

art3_body = """India's technology services industry — the $315 billion juggernaut that TCS, Infosys, Wipro and HCL Tech built on the back of cheap, abundant labour — has spent the past year staring at artificial intelligence with a mixture of dread and ambition. On Thursday, the industry's lobbying body chose the ambitious narrative.

At a forum held at the Consulate General of India in the United States, the National Association of Software and Service Companies (Nasscom) declared that AI could unlock a $400 billion market opportunity for Indian IT services companies by 2030. The figure, drawn from research by ICICI Direct and Nasscom's own projections, reframes the AI story for India's outsourcing giants: not as a job-killing automation wave, but as a new market large enough to absorb — and then exceed — the revenue lost from legacy services.

## From Headcount to Outcome

The Nasscom thesis is straightforward. Enterprises globally are moving from AI experimentation to production deployment. Making AI systems work at scale requires exactly the kind of heavy lifting that Indian IT services firms have done for decades: data readiness, workflow redesign, secure deployment, governance, change management and integration across complex technology stacks. The twist is that the billing model has to change.

"The value of IT services will increasingly lie in making these systems work together securely, efficiently and at scale," said Nasscom president Rajesh Nambiar. Translation: the era of billing by the headcount is ending; the era of billing by the outcome is beginning.

Cognizant CEO Ravi Kumar S, who chairs the Nasscom US CEO Forum, was more direct. "Enterprises now need to convert AI capability into production value. That requires data readiness, workflow redesign, secure deployment, governance and change management. These are areas where Indian technology services companies have deep experience and a strong opportunity to lead."

## The Numbers Behind the Pivot

Indian IT's top five — TCS, Infosys, HCL Tech, Wipro and Tech Mahindra — closed fiscal year 2026 at what analysts describe as a structural inflection point. AI-driven productivity is already causing an estimated 2-3 per cent annual deflation in traditional IT services revenues, according to ICICI Direct. Legacy maintenance contracts are shrinking as AI agents handle tasks that once required teams of mid-level engineers.

But the countervailing force is real. TCS reported annualised AI services revenue exceeding $2.3 billion — more than 6 per cent of its overall revenue. Infosys has committed to hiring 20,000 freshers in fiscal year 2027, though increasingly from AI, data science and cybersecurity programmes rather than the general engineering pipeline that sustained the old model.

The industry already generates an estimated $10-12 billion annually from AI-related services. Nasscom's $400 billion projection is a 2030 addressable-market figure, not a revenue forecast — but even reaching a fraction of it would represent a transformation in what Indian IT companies sell and how they sell it.

## What Changes for Indian Professionals

The shift has immediate workforce implications. Nasscom's own research indicates that future growth will be "less dependent on linear headcount additions and more reliant on platforms, domain solutions, proprietary assets, and outcome-based delivery." Business process services will move from routine transaction execution to intelligence operations, with humans shifting toward supervision, exception handling and decision support.

For Indian professionals — whether working at TCS in Chennai, Infosys in Bengaluru, or Cognizant in New Jersey — the message is clear: the mid-tier, task-execution layer of IT services is the layer most exposed to AI displacement. The opportunities are in AI deployment, data engineering, cybersecurity and domain consulting — areas that require both technical depth and client-facing judgment.

For NRIs working in the US for Indian IT firms on H-1B visas, the pivot adds both risk and opportunity. The old model of sending large onsite teams for infrastructure and application management is under pressure. The new model — smaller, higher-skilled teams deploying AI platforms — may mean fewer visa-dependent positions but higher-value ones. Companies like Wipro have already slashed fresher hiring targets and shifted toward specialised AI and cybersecurity recruits from university partnerships.

## The Honest Assessment

Nasscom's $400 billion figure is aspirational, and it knows it. The industry body is a lobbying organisation whose job is to paint its members in the most favourable light. The real question is not whether AI creates a large new market — it clearly does — but whether Indian IT firms can capture it against Silicon Valley-native competitors, cloud hyperscalers that are vertically integrating AI services, and the AI-native startups that are eating SaaS incumbents for breakfast.

What Indian IT does have is scale, client relationships, regulatory knowledge and delivery infrastructure that no startup can replicate overnight. Whether that is enough depends on how fast the incumbents can retool — not their pitch decks, but their actual workforce and delivery models. The next two years will tell."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nasscom Says AI Will Create a $400 Billion Market for Indian IT. Its Old Model Won't Get It There.",
    "subheadline": "The industry body pitched AI as the next growth engine for India's outsourcing giants at a forum in the US. But the pivot from headcount billing to outcome-based delivery requires a workforce transformation that is barely under way.",
    "slug": make_slug("nasscom-400-billion-ai-opportunity-indian-it-services"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "For NRIs working at Indian IT firms on H-1B visas, the AI pivot means fewer task-execution roles but higher-value AI deployment and consulting positions — a workforce reshaping with direct implications for immigration and career planning.",
    "tags": ["nasscom", "indian-it-services", "ai-transformation", "tcs", "infosys", "cognizant"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/nasscom-says-ai-could-unlock-usd-400-billion-opportunity-for-indian-it-services/article69746089.ece"},
        {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/indian-it-industry-generates-up-to-12b-from-ai-services-nasscom/"},
        {"name": "ICICI Direct Research", "url": "https://www.icicidirect.com/research/equity/companies"},
        {"name": "The Hindu BusinessLine (FY26 results)", "url": "https://www.thehindubusinessline.com/info-tech/indian-it-faces-ai-reset-top-5-firms-post-mixed-fy26-amid-macro-headwinds/article69490072.ece"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16323394/pexels-photo-16323394.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Software professionals at work in a modern office — India's IT services industry sees AI as a $400 billion growth opportunity",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
