#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-28 20:00 PDT run."""

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

# ── Article 1: OpenAI Jalapeño Chip ──────────────────────────────────

art1_body = """OpenAI has spent the last three years as Nvidia's most visible customer. Last Tuesday, it served notice that the arrangement has an expiry date.

The company unveiled Jalapeño, a custom-designed inference chip built with Broadcom, its first piece of proprietary silicon. The chip is an application-specific integrated circuit — an ASIC — engineered for one job: running large language models in production. Not training them. Running them. Every ChatGPT message, every API call, every Codex query. That is where OpenAI burns the most compute and, by extension, the most money.

## Nine Months, Tape-Out to Testing

The development timeline is the headline within the headline. OpenAI and Broadcom took Jalapeño from initial architecture to tape-out in nine months — roughly half the industry standard for an advanced semiconductor. Greg Brockman, OpenAI's president, told CNBC that the company's own AI models accelerated the chip's design, a recursive loop where the product helped build the hardware that will run the product. Engineering samples are already processing live workloads, including GPT-5.3-Codex-Spark.

The chip is optimised around the specific bottlenecks of LLM inference: data movement between compute and memory, networking efficiency across server clusters, and tight serving-loop latency. Early results claim performance-per-watt that exceeds current state-of-the-art hardware, though OpenAI has withheld detailed benchmarks pending a technical report later this year.

Broadcom's role extends beyond fabrication. The company supplied its Tomahawk networking silicon and handled system integration. Celestica built the board and rack assembly. The collaboration is structured as a multi-generation partnership, with deployment at gigawatt scale beginning late 2026 — tied to the Stargate data centre project with Microsoft.

## What This Means for the Chip Wars

Jalapeño accelerates a pattern that should worry Nvidia's shareholders and excite India's semiconductor ecosystem in equal measure. Google, Meta, Amazon, and now OpenAI are all designing custom inference silicon, commoditising the very GPUs that powered the AI boom. Broadcom, which also builds custom chips for Alphabet, Meta, and ByteDance, expects AI semiconductor revenue to exceed $100 billion by 2027.

For Indian engineers, this is a job-creation engine hiding inside a corporate strategy story. Broadcom employs thousands of chip designers across its Hyderabad and Bengaluru centres — the same teams that will iterate on Jalapeño's successors. OpenAI's own engineering ranks are dense with Indian-origin talent, from infrastructure to model architecture. And the broader shift from renting Nvidia GPUs to designing bespoke ASICs is precisely the kind of work India's semiconductor mission aspires to support: chip design, not just fabrication.

## The Nvidia Question

Jensen Huang is not losing sleep yet. Nvidia still dominates AI training, and its H200 and Blackwell architectures remain the infrastructure standard for frontier model development. But inference is where the volume lives — and increasingly, where the margins will be contested. Every major hyperscaler now has a custom-silicon programme, and Jalapeño is the clearest signal yet that the inference market will not belong to any single chipmaker.

For NRI investors tracking the semiconductor stack, the takeaway is structural: Broadcom (up 85% over the past year) and the custom-ASIC ecosystem are capturing value that once flowed exclusively to Nvidia. The AI chip market is no longer a monopoly. It is a supply chain — and Indian engineers sit at critical nodes across it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Built Its Own Chip in Nine Months. Nvidia Should Pay Attention.",
    "subheadline": "Jalapeño, a custom inference processor designed with Broadcom, marks OpenAI's first step toward owning the silicon that runs ChatGPT — and Indian chip designers are at the centre of what comes next.",
    "slug": make_slug("openai-jalapeno-chip-broadcom-nvidia-inference-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Broadcom's Indian design centres in Hyderabad and Bengaluru will iterate on Jalapeño's successors, and the custom-ASIC boom is creating high-value chip design jobs that align with India's semiconductor mission — directly relevant for NRI engineers and investors.",
    "tags": ["openai", "broadcom", "nvidia", "semiconductor", "ai-chips", "silicon-valley", "indian-engineers"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/technology/openai-broadcom-jalapeno-chip"},
        {"name": "CNBC / Zacks", "url": "https://www.zacks.com/stock/news/2470894/broadcom-openai-unveil-jalapeno-ai-chip"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/06/openai-jalapeno-ai-chip/"},
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/32916041/broadcom-just-quietly-became-openai-s-preferred-choice-for-ai-inference"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/40848/pins-cpu-processor-macro-40848.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Closeup of a processor chip's pin array, illustrating the silicon hardware powering AI inference",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}

# ── Article 2: Google Brain Drain ────────────────────────────────────

art2_body = """Sundar Pichai had a plan for last week. Google would launch Gemini 2.5 Pro with Deep Think, posting benchmark scores above every publicly available model. It would be a statement of intent from the company that invented the transformer architecture.

Instead, the week became a case study in how quickly talent can undo a narrative.

## Two Departures, $225 Billion Gone

On Wednesday, Noam Shazeer — co-author of "Attention Is All You Need," the 2017 paper that created the transformer — announced he was leaving Google for OpenAI. This was the second time Shazeer had left. Google brought him back in 2024 through a $2.7 billion licensing deal with his startup, Character.AI. Two years and billions of dollars later, OpenAI pulled him away again, this time as lead for architecture research.

Two days later, John Jumper, a Nobel laureate whose AlphaFold system mapped over 200 million protein structures, announced he was departing DeepMind after nine years for Anthropic.

Alphabet's stock fell 7% on Monday, erasing $225 billion in market capitalisation — its largest single-day loss ever, according to Dow Jones Market Data. By Tuesday, the decline had deepened further, with the stock down more than 8% for the month.

"Google had the state-of-the-art model for a few weeks last year, which helped it get credit as an AI winner, but has fallen off since, and these departures may mean it is falling behind," D.A. Davidson managing director Gil Luria told MarketWatch.

## Gemini 3.5 Pro Pushed to July

Compounding the narrative damage, Google has quietly delayed the release of Gemini 3.5 Pro — the model that was supposed to demonstrate the company's frontier capabilities — from June to July. Reports indicate the model underwhelmed during early testing on complex, multi-step tasks, prompting the postponement.

Google introduced the Gemini 3.5 family at its I/O developer conference in May, with Pichai personally promising the Pro variant within weeks. Gemini 3.5 Flash shipped on schedule, but Pro's delay leaves a conspicuous gap in the lineup at precisely the moment investors are questioning whether the company can retain the people who build these systems.

## The Pichai Question

For the Indian diaspora, this is personal. Pichai, 54, is the most prominent Indian-origin CEO in global technology — the man who transformed a search company into what he calls an "AI-first" enterprise. His track record is formidable: Alphabet's stock is up 270% since ChatGPT's debut, revenue and profits are at records, and the company has committed $180 billion to $190 billion in AI infrastructure spending for fiscal 2026.

But the talent exodus tests a different dimension of leadership. Retaining researchers is not the same as cutting costs or expanding cloud margins. The AI race is, at bottom, a war for a few hundred people who can build frontier systems. Google has lost at least four senior researchers to Anthropic and OpenAI in the past month alone. Demis Hassabis, DeepMind's CEO, has insisted the company has the "biggest and broadest research bench." The options market, where call volume at $390 still outpaces puts, tentatively agrees.

The question for Indian tech professionals — many of whom work at Google and hold significant equity — is whether this is a buying opportunity or the start of a structural decline. The talent that made Google's AI models best-in-class is now building the competition. Pichai's next move will determine which reading is correct.

Meanwhile, tens of thousands of Indian engineers at Google face a more immediate calculus. If the best researchers are leaving, does the institution still offer the career trajectory it once did? For those on H-1B visas, the question is sharper: stability matters more when your right to stay in the country is tied to your employer."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Pichai's Worst Week: Google Lost a Nobel Laureate, a Transformer Co-Author, and $225 Billion",
    "subheadline": "Two of AI's most important researchers left Google for its rivals in the same week. The stock recorded its largest-ever single-day market cap loss, and Gemini 3.5 Pro has been pushed to July.",
    "slug": make_slug("google-brain-drain-pichai-shazeer-jumper-alphabet-225-billion"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Sundar Pichai is the most prominent Indian-origin CEO in tech, and tens of thousands of Indian engineers at Google — many on H-1B visas — face career and equity implications from the talent exodus and stock decline.",
    "tags": ["google", "sundar-pichai", "alphabet", "deepmind", "ai-talent", "openai", "anthropic", "indian-tech-leaders"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "New York Post", "url": "https://nypost.com/2026/06/23/business/google-loses-270b-in-market-cap-over-concerns-its-falling-behind-rivals-in-race-for-ai-talent/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/alphabet-sees-225-billion-market-cap-wipeout-as-investors-fear-its-losing-the-war-for-ai-talent/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/google-brain-drain-alphabet-stock-anthropic/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/is-google-delaying-gemini-3-5-pro-launch-to-july-for-further-testing"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, at a 2023 event",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ── Article 3: NPCI / UPI AI Push ────────────────────────────────────

art3_body = """India's Unified Payments Interface processes more than 750 million transactions every day. Its overseer wants artificial intelligence to push that number past a billion — and to fundamentally reshape what "paying for something" looks like along the way.

In an interview with TechCrunch at Mumbai Tech Week 2026, Dilip Asbe, the managing director and CEO of the National Payments Corporation of India, laid out a vision that goes well beyond fraud detection. AI, he argued, will drive the next half-billion UPI users, distribute credit to merchants with digital footprints, and make voice-first onboarding viable in a country where literacy and language diversity remain real barriers to financial inclusion.

"AI will be used very effectively when we look at the next wave of UPI," Asbe said. "We must use AI to look at the voice and multilingual solutions to make onboarding simpler."

## FIMI: India's Own Payments AI

The ambition is not theoretical. NPCI has already deployed FiMI — Finance Model for India — a domain-specific language model built in-house and purpose-trained on Indian payment data. Launched in February at the India AI Impact Summit, FiMI handles transaction disputes, mandate lifecycle management, and regulatory queries through the UPI Help Assistant. It currently supports English, Hindi, Telugu, and Bengali, with more languages planned. Asbe says it is already serving over a million users.

FiMI represents something larger than a chatbot. It is India's first sovereign AI model for financial infrastructure — trained on Indian payment patterns, speaking Indian languages, and deployed at national scale. In a world where OpenAI, Anthropic, and Google dominate the model layer, FiMI is a quiet but significant assertion of technological self-determination.

Asbe is explicit about the opportunity: Indian banks and fintechs should build their own small language models rather than depending on American frontier labs. "We believe that the models will differentiate from each other based on the data sets that are made available to them," he said. "There is a big opportunity for Indian companies to create small language models which are sharp, specific, and as deterministic as possible."

## Agentic Commerce: When AI Pays on Your Behalf

Perhaps the most consequential development is NPCI's push into agentic payments. Last year, the corporation demonstrated a prototype with Razorpay and OpenAI where a user could tell ChatGPT what they wanted to buy, the AI would shop and select products, and the user would simply confirm the payment via UPI. No app-switching, no checkout flow, no friction.

NPCI has since introduced UPI Reserve Pay, a feature that lets users pre-authorise spending limits for AI agents — effectively giving a bot a controlled wallet. The framework includes consent tracking and instruction logging, so if something goes wrong, regulators can audit exactly what the AI was told to do.

This puts India ahead of most Western payment systems on agentic commerce infrastructure. Coinbase and Robinhood in the US are experimenting with AI-driven trading, but neither has a government-backed payment rail designed for agent-to-merchant transactions at population scale.

## The 30% Cap and What Comes Next

UPI's competitive structure remains lopsided. PhonePe and Google Pay control over 80% of transaction volume, and a regulatory cap limiting any single app to 30% market share is set to take effect on December 31 — unless NPCI defers the deadline again. Asbe acknowledged the concentration risk but argued that new commercial models, not regulatory mandates, will bring balance. "The moment we see the commercial model being available to the ecosystem, I believe newer players will start investing very heavily," he said.

For the Indian diaspora, UPI's evolution matters on multiple fronts. NRIs increasingly use UPI-linked systems for remittances and payments during India visits. International expansion — UPI now works in Singapore, the UAE, Sri Lanka, France, and several other markets — is turning it into a portable payment identity for Indians abroad. And for NRI investors watching India's fintech sector, the AI layer on top of UPI represents the next wave of value creation: companies that can build domain-specific models, agentic interfaces, and credit-scoring engines on the world's largest real-time payment network.

India did not wait for Silicon Valley to figure out AI payments. It switched them on."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Payment Network Just Built Its Own AI. It Already Serves a Million Users.",
    "subheadline": "NPCI's in-house language model FiMI is processing disputes in four languages, agentic payments are live in prototype, and the man who runs UPI says AI will bring the next 500 million users.",
    "slug": make_slug("npci-upi-fimi-ai-agentic-payments-dilip-asbe-india-fintech"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "UPI's international expansion makes it a portable payment identity for NRIs abroad, and the AI layer — from FiMI to agentic commerce — represents the next wave of fintech value creation for diaspora investors watching India's digital infrastructure.",
    "tags": ["upi", "npci", "india-fintech", "ai-payments", "fimi", "agentic-commerce", "digital-india", "razorpay"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/27/indian-payments-chief-thinks-ai-will-be-heavily-involved-in-next-era-of-digital-payment-growth/"},
        {"name": "MediaNama", "url": "https://www.medianama.com/2026/02/223-npci-launches-fimi-ai-model-for-upi-ecosystem/"},
        {"name": "NPCI Official", "url": "https://www.npci.org.in/what-we-do/upi/fimi-announcement"},
        {"name": "Gadgets 360", "url": "https://www.gadgets360.com/apps/features/openai-npci-upi-payments-chatgpt-explained-7192621"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4226272/pexels-photo-4226272.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A customer making a contactless mobile payment at a point-of-sale terminal",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ── Insert ───────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
