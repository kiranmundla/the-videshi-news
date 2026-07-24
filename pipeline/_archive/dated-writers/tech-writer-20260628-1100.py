#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-28 11:00 PDT run"""

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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────
art1_body = """Google has turned the taps down on Meta.

According to a Financial Times report published on Sunday, Alphabet's cloud division told Meta around March that it could not meet the full capacity the social media giant had sought for its Gemini AI models. The shortfall has disrupted and delayed several of Meta's internal AI projects, and the company has since asked employees to be more efficient with the AI tokens they consume.

It is a remarkable inversion. A decade ago, Meta was the company everyone wanted compute from — its open-source PyTorch framework ran most of the world's machine learning research. Now Mark Zuckerberg's engineers are queuing at Sundar Pichai's door, and Pichai's team is rationing access.

## The scarcity behind the power play

The restriction is not, by all accounts, punitive. Google Cloud's revenue hit $20 billion in the first quarter of 2026, but Pichai told analysts that computing power constraints had prevented even stronger growth and contributed to the cloud unit's backlog nearly doubling quarter on quarter. Meta is simply the biggest customer in the queue — its exceptionally high demand for Gemini capacity made it the first to feel the squeeze.

Several other Google Cloud clients have also been affected, though to a lesser degree. The episode exposes a deeper structural problem: even as hyperscalers pour hundreds of billions into chips and data centres, they still cannot build capacity fast enough to keep up with the demand their own AI models have unleashed.

## Why NRIs should care

For the tens of thousands of Indian engineers working at both companies — Google employs more than 40,000 people in India, and Meta has a significant Hyderabad and Bengaluru presence — this is not an abstract boardroom story. It is the daily reality of their work: project timelines being reshuffled, internal tooling being rationed, and teams being told to optimise what they already have rather than scale up.

It also sharpens the context around the hyperscaler land grab in India. Amazon last week committed an additional $13 billion to expand AI data centre capacity in Mumbai and Hyderabad, bringing its total planned India investment to $48 billion through 2030. Google itself has pledged $15 billion for data centres in Andhra Pradesh. Microsoft has earmarked $17.5 billion. The race to build compute in India is not just about serving Indian customers — it is about relieving global capacity constraints that are now severe enough to ration a company the size of Meta.

## The Pichai factor

The dynamic is not lost on the diaspora. Sundar Pichai, the Chennai-born CEO of Alphabet, now presides over an AI infrastructure so essential that even a $1.6 trillion rival cannot get enough of it. Google Cloud's backlog, the value of contracts signed but not yet delivered, is growing faster than its revenue — a sign that demand is outstripping supply by a widening margin.

For NRI investors tracking the hyperscaler complex, the takeaway is straightforward: the AI boom is not compute-limited in theory but in practice. Every dollar Amazon, Google and Microsoft spend on Indian data centres is a dollar spent on solving a global bottleneck. The companies that control the infrastructure — and ration it — hold the power.

Pichai, characteristically, has been understated about the position. But the numbers speak loudly enough. When your biggest competitor has to ask you for permission to run their AI projects, you have already won a round that no earnings call can adequately capture."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Pichai's Google Just Told Meta to Get in Line. The AI Compute War Has a Waitlist.",
    "subheadline": "Google has restricted Meta's access to Gemini AI models after Zuckerberg's team demanded more computing capacity than Alphabet could deliver. For Indian engineers at both companies, the rationing is reshaping daily work.",
    "slug": make_slug("pichai-google-meta-gemini-ai-compute-rationing"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Sundar Pichai's Google now controls AI infrastructure so essential that even Meta must queue for access — a power shift felt daily by tens of thousands of Indian engineers at both companies, and one driving the hyperscaler data centre race in India.",
    "tags": ["google", "meta", "sundar-pichai", "gemini", "ai-infrastructure", "cloud-computing", "indian-tech-leaders"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Financial Times", "url": "https://www.ft.com/content/google-limits-meta-gemini-ai"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/google-limits-metas-use-its-gemini-ai-models-ft-reports-2026-06-28/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/amazon-investing-13-billion-india-ai-data-centers-c0b5f14f"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, in 2023",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────
art2_body = """Harvey AI, the world's most valuable legal technology startup, is building its future from India.

The San Francisco-based company, valued at $11 billion after a $200 million raise led by Sequoia Capital in March, has opened an engineering hub in Bengaluru, hired Indian-origin leadership to run it, and signed enterprise clients including Flipkart and the Reliance group. It is also building at least three new products out of its India operations, according to Siva Gurumurthy, Harvey's head of India business.

For a company that barely existed three years ago, the India expansion is strikingly ambitious. And for the thousands of Indian lawyers and technologists watching the legal AI revolution from afar, it is a signal that the revolution is coming home.

## The court backlog argument

India's judiciary has roughly 50 million pending cases across its district, high and supreme courts — a backlog that has resisted every government reform effort for decades. The median time to resolve a commercial dispute is about four years. For NRIs dealing with property claims, inheritance disputes or business litigation in India, the system's sluggishness is not an abstraction; it is a direct drain on time, money and family relationships.

Legal AI does not fix a systemic judicial shortfall. But it can compress the hours lawyers spend on document review, case research and drafting — the labour-intensive groundwork that inflates both timelines and bills. Harvey's core product uses large language models to help lawyers review contracts, draft arguments and extract relevant precedent from vast legal databases in minutes rather than days.

The company now claims more than 1,000 clients across 60 countries, including a majority of the top ten American law firms. In India, it has partnered with prominent firms including Shardul Amarchand Mangaldas & Co and S&A Law Offices. Cyril Amarchand Mangaldas, one of India's largest corporate practices, has also adopted the platform.

## The Bengaluru bet

Harvey's Bengaluru office, announced last year, is not a support outpost. It houses engineering, sales and operations teams, led by Pradeep Reddy as Head of India Engineering and Site Lead. The hire of Sakshi Pratap — the Indian-origin founder of Hexus, a product demo startup Harvey acquired — brought additional engineering leadership with prior experience at Walmart, Oracle and Google.

"India is an essential part of our global strategy," Harvey co-founder and CEO Winston Weinberg said when announcing the expansion. "By investing in Bengaluru, we're tapping into an exceptional talent pool and deepening our ability to serve the Indian legal market."

The company's agentic AI platform, which functions as a collaborative review table between law firms and their corporate clients, is the product closest to Indian enterprise needs. Gurumurthy described it as saving companies "hundreds of hours of manpower effort" in real-time document review and legal argument assessment.

## What the diaspora should watch

Harvey's India play sits at the intersection of three trends that matter to NRIs. First, India's legal market — historically fragmented and relationship-driven — is being prised open by technology in ways that could make legal services faster and cheaper for anyone with cross-border needs. Second, the Bengaluru engineering centre represents a new category of high-value AI jobs in India, distinct from the traditional IT services model. Third, the competitive landscape is heating up: Sweden-based Legora, backed by Nvidia, recently hit a $5.6 billion valuation and is also eyeing the Indian market, while homegrown startups like Lucio are building India-specific legal AI tools.

For an NRI investor, the question is whether legal AI becomes the next SaaS category where India produces both globally competitive builders and a large domestic market. For an NRI with a pending property dispute in Delhi or a family business succession plan in Chennai, the question is simpler: will this make the process any less painful?

The honest answer is not yet. But the pieces are being assembled faster than most expected."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The $11 Billion AI Lawyer Just Opened a Bengaluru Office. India Has 50 Million Reasons It Needs One.",
    "subheadline": "Harvey AI, the world's most valued legal tech startup, is building products out of India, signing Flipkart and Reliance as clients, and hiring Indian-origin engineers to run its Bengaluru hub. India's clogged courts are the pitch.",
    "slug": make_slug("harvey-ai-legal-tech-bengaluru-india-flipkart-reliance"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRIs dealing with India's notoriously slow legal system — property disputes, inheritance claims, business litigation — stand to benefit as legal AI compresses the hours (and bills) lawyers spend on document review and case research.",
    "tags": ["legal-tech", "harvey-ai", "bengaluru", "ai-startups", "india-courts", "flipkart", "reliance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/ai/artificial-intelligence/harvey-ai-world-s-largest-legal-ai-startup-india-demand-siva-gurumurthy-11782392272928.html"},
        {"name": "Bar and Bench", "url": "https://www.barandbench.com/news/harvey-ai-bengaluru-office"},
        {"name": "Express Computer", "url": "https://www.expresscomputer.in/artificial-intelligence-ai/why-india-is-becoming-central-to-harveys-enterprise-ai-roadmap/120217/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2025/12/18/legal-ai-giant-harvey-acquires-hexus/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8439082/pexels-photo-8439082.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Legal professionals reviewing documents — the labour AI tools like Harvey aim to compress",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ── ARTICLE 3 ──────────────────────────────────────────────────────────
art3_body = """While Silicon Valley's AI labs compete over English-language benchmarks, India has quietly built a sovereign AI system that speaks 22 languages — and almost nobody outside the country noticed.

BharatGen, a consortium of AI labs across nine Indian institutes led by IIT Bombay, has released Param-2, a 17-billion-parameter foundational text model trained on all 22 of India's scheduled languages, from Hindi and Tamil to Maithili and Sindhi. Alongside it, the consortium launched Shrutam (speech-to-text in 12 languages), Sooktam (text-to-speech in 12 languages), and Patram, a document vision-language system designed to make complex Indian government documents accessible in multiple languages.

The initiative is backed by a ₹1,058-crore (roughly $125 million) grant from India's AI Mission, making BharatGen the largest recipient of government AI funding in the country. Prime Minister Narendra Modi personally launched the latest models. And yet, the project has received a fraction of the global attention lavished on OpenAI's latest release or Anthropic's export control saga.

## Why it matters — and why it struggles

"We can only truly understand AI models when we build them from scratch," said Ganesh Ramakrishnan, chair professor of computer science at IIT Bombay and BharatGen's founding director. His argument is simple: if India relies entirely on American and Chinese models to power its AI applications, it will remain "at the consumption layer" — using tools without understanding or controlling the technology underneath.

BharatGen has already released domain-specific fine-tuned models: Ayur Param for Ayurveda, Agri Param for agriculture, and Legal Param for India's legal system. Pilots have been conducted in governance, agriculture and defence, with plans to deploy applications across all states and districts.

But the project faces a structural challenge that no amount of government funding can solve alone. India has a severe deep tech talent deficit, particularly in the kind of researchers who can train foundational models from scratch — the ML engineers, data scientists and compute infrastructure specialists who are overwhelmingly concentrated in American labs. A recent Livemint analysis warned that the talent gap "could stall broader industry progress" even as investment pours in.

## The diaspora's role

This is where the Indian diaspora enters the picture — not as passive observers, but as a potential talent pipeline.

Indian-origin researchers are among the most prolific contributors to the global AI research ecosystem. They hold senior positions at Google DeepMind, OpenAI, Anthropic, Meta AI and every major university lab. The question BharatGen implicitly poses is whether any of that talent can be channelled back, whether through sabbaticals, advisory roles, collaborative research or permanent returns.

India's digital public infrastructure — Aadhaar, UPI, DigiLocker — was built with significant contributions from the diaspora. BharatGen's backers hope the same model can work for sovereign AI. The consortium spans IIT Bombay, IIIT Hyderabad, IIT Hyderabad, IIT Mandi, IIT Kanpur, IIM Indore and IIT Madras, with IBM India as a commercial partner.

For NRIs in the AI industry, the project raises practical questions. Can a $125 million government grant compete with the billions flowing into American labs? Can academic consortiums match the engineering velocity of a well-funded startup? And if BharatGen's models are genuinely useful — say, for rural healthcare delivery in Marathi or legal document processing in Bengali — does that create business opportunities worth pursuing?

## The sovereignty argument

The timing of BharatGen's push is not accidental. Washington's recent export control order restricted access to Anthropic's most advanced models over national security concerns. India's developers found themselves on the outside of GPT-5.6's restricted launch. In a world where access to frontier AI is increasingly gated by geopolitics, a sovereign foundational model — even a less capable one — is an insurance policy.

Param-2's 17 billion parameters are modest by Silicon Valley standards, where the frontier models run into the trillions. But for India-specific tasks — government document processing, agricultural extension services, legal assistance in regional languages — a well-tuned smaller model may actually outperform a general-purpose giant that was never trained on Konkani.

India has spent years proving that digital public infrastructure can work at population scale. BharatGen is the bet that the same approach can work for AI. Whether the talent to make it real stays at home — or can be coaxed back from Mountain View — remains the open question."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Government Built Its Own GPT. It Speaks 22 Languages. The Talent to Scale It Lives Abroad.",
    "subheadline": "BharatGen, the IIT Bombay-led AI consortium backed by a ₹1,058-crore government grant, has launched Param-2 — a 17-billion-parameter model covering all of India's scheduled languages. The problem is not funding. It is the deep tech talent deficit that only the diaspora can fill.",
    "slug": make_slug("bharatgen-param-2-india-sovereign-ai-iit-bombay-diaspora"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-origin AI researchers dominate Silicon Valley labs but India's own sovereign AI push faces a severe talent deficit — BharatGen's success may depend on whether NRI talent can be channelled back through sabbaticals, advisory roles or returns.",
    "tags": ["bharatgen", "sovereign-ai", "iit-bombay", "india-ai-mission", "foundational-models", "indian-languages", "diaspora-talent"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Livemint", "url": "https://www.livemint.com/ai/artificial-intelligence/bharatgen-india-ai-mission-sovereign-ai-india-11782380654091.html"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2130457"},
        {"name": "IBM Newsroom", "url": "https://newsroom.ibm.com/2025-09-18-IBM-and-BharatGen-Collaborate-to-Accelerate-AI-Adoption-in-India"},
        {"name": "YourStory", "url": "https://yourstory.com/2025/11/iit-bombay-launches-bharatgen-indias-multilingual-ai-foundation"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Night_view_of_campus_buildings_at_IIT_Bombay.jpg/1280px-Night_view_of_campus_buildings_at_IIT_Bombay.jpg",
    "image_caption": "IIT Bombay campus — home to the BharatGen consortium leading India's sovereign AI mission",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}


# ── PUBLISH ────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
