#!/usr/bin/env python3
"""Tech writer for The Videshi — 2026-07-09 08:10 PDT run."""
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


# ── Article 1: TCS Q1 Results ──────────────────────────────────────────

art1_body = """Tata Consultancy Services just posted its first-quarter results, and the numbers carry a quiet message for the 600,000-plus Indians working in America's technology corridors: the biggest Indian IT firm is not shrinking. It is hiring.

TCS reported consolidated revenue of ₹722.75 billion ($7.58 billion) for the April–June quarter, a 14 per cent increase year-over-year that beat analysts' consensus estimate of ₹720.30 billion. Net profit rose 4.6 per cent to ₹133.49 billion, even after absorbing a one-time charge related to its intellectual-property dispute settlement with DXC Technology.

## The AI Number That Matters

The headline buried inside the earnings deck is this: TCS's annualised AI revenue crossed $2.6 billion, up from $2.3 billion in the previous quarter. That is a $300-million jump in three months — faster than most standalone AI startups grow in a year.

The acceleration reflects a shift from experimentation to production-grade AI deployments across TCS's client base. Banking, financial services and insurance — the vertical that contributes the most revenue — grew 2.4 per cent sequentially, fuelled by two mega-deals signed last fiscal year now ramping up.

## 9,300 New Hires — The Highest in Three Years

Perhaps the most striking data point is headcount. In a quarter when Microsoft cut 4,800 jobs and the broader tech industry shed over 119,000 positions globally, TCS added approximately 9,300 employees — its highest quarterly intake in more than three years.

For Indian professionals on H-1B visas watching layoff trackers with growing anxiety, the signal is worth parsing. The jobs are not vanishing from Indian IT services. They are shifting. TCS Chairman N. Chandrasekaran has said the "day is not far" when the company would have an equal number of AI agents and human employees — but for now, the humans are still being hired.

## The Rupee Tailwind

A weaker rupee provided a meaningful boost. Indian IT companies bill most clients in dollars and euros but incur the bulk of their costs in rupees. With the rupee hovering near ₹95.4 to the dollar, that spread widened, flattering reported revenue growth. Strip out currency effects, and the industry's constant-currency growth is a more modest 2.8 per cent — a number that keeps analysts cautious.

JPMorgan sees revenue growth staying below 3-4 per cent for the "foreseeable future." Citi expects a fourth straight year of subdued organic expansion. The Nifty IT index fell 9.5 per cent in the June quarter even as the broader Nifty 50 gained 6.9 per cent.

## What NRIs Should Watch

TCS is the first major Indian IT company to report this earnings season. Infosys reports on July 23, HCLTech and Wipro later this month. Their numbers will reveal whether TCS's beat is a sector-wide uptick or a company-specific story.

For the Indian diaspora, the stakes are personal. These companies collectively employ hundreds of thousands of workers in the United States, many on work visas tied to their employment. A quarter of modest growth is less reassuring than a quarter of clear acceleration — but it is far better than the contraction many feared. The order book, at $9.5 billion, shrank from $12 billion last quarter, suggesting deal momentum may be cooling. AI revenue, however, is moving in the other direction.

The bellwether has spoken. Now the rest of the sector has to answer."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "TCS Beat Expectations and Hired 9,300 People. Its AI Revenue Just Crossed $2.6 Billion.",
    "subheadline": "India's largest IT exporter posted a 14 per cent revenue rise and its biggest quarterly hiring in three years — but the order book shrank and organic growth remains thin.",
    "slug": make_slug("tcs-q1-fy27-ai-revenue-hiring-beat"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "TCS employs tens of thousands of H-1B workers in the US; its hiring surge and AI revenue growth counter the prevailing narrative of mass layoffs hitting Indian tech professionals.",
    "tags": ["tcs", "indian-it", "ai-revenue", "earnings", "h1b", "hiring"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-tcs-beats-first-quarter-revenue-view-2026-07-09/"},
        {"name": "Reuters — Indian IT firms face muted Q1", "url": "https://www.reuters.com/technology/indian-it-firms-face-muted-q1-as-ai-shift-weak-demand-weigh-2026-07-06/"},
        {"name": "LKP Securities analyst note", "url": "https://www.reuters.com/world/india/indias-tcs-beats-first-quarter-revenue-view-2026-07-09/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Tata_Consultancy_Services_Madhapur_Hyderabad.jpg/1280px-Tata_Consultancy_Services_Madhapur_Hyderabad.jpg",
    "image_caption": "Tata Consultancy Services campus in Madhapur, Hyderabad",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}


# ── Article 2: SpaceXAI Grok 4.5 ──────────────────────────────────────

art2_body = """Elon Musk picked the busiest day in AI this year to make his move. On Wednesday evening, SpaceXAI — the freshly rebranded AI arm of his rocket and satellite empire — launched Grok 4.5, a frontier model it calls its most intelligent to date. Hours earlier, OpenAI had confirmed that GPT-5.6 would ship on Thursday. The two announcements landed within the same news cycle, turning a routine product launch into a public showdown.

## What Grok 4.5 Actually Is

Grok 4.5 is a coding and reasoning model built on SpaceXAI's 1.5-trillion-parameter V9 foundation. It was trained, SpaceXAI said, across "tens of thousands" of Nvidia's latest GB300 graphics processing units — the same silicon that powers the most expensive AI clusters on Earth.

Independent benchmarks from Artificial Analysis rank Grok 4.5 third in overall intelligence among large language models, behind only Anthropic's Claude Fable 5 and OpenAI's ChatGPT 5.5. Musk claims the model is "roughly comparable to Opus 4.7, but much faster" — and, crucially, cheaper. At $2 per million input tokens and $6 per million output tokens, Grok 4.5 undercuts Anthropic's Claude Opus 4.8 ($5 input, $25 output) by a wide margin.

## The Cursor Connection

The model is the first to emerge from SpaceXAI's $60-billion acquisition of Anysphere, the startup behind the wildly popular AI coding assistant Cursor. Anysphere founder Michael Truell had teased a Cursor-native model last month; Grok 4.5 is that model, now integrated as the default engine inside Cursor and available through Grok Build, SpaceXAI's coding platform.

For Indian software engineers — who represent the largest cohort of Cursor's professional user base in Asia — this matters practically. Grok 4.5 is immediately available through Cursor and through SpaceXAI's developer console. EU availability is expected in mid-July.

## Why Indian Developers Should Pay Attention

The pricing is the headline. Indian AI startups, many of which operate on shoestring compute budgets, have been priced out of frontier models. Anthropic's top tier costs $25 per million output tokens. OpenAI's GPT-5.6 Luna — the cheaper variant — costs $1 input and $6 output. Grok 4.5 sits in between: cheaper than Anthropic, roughly on par with OpenAI's budget option, but with Opus-class capability.

For a Bengaluru startup processing a million customer queries a day, the difference between $25 and $6 per million output tokens is the difference between a viable product and a burn-rate crisis.

## The SpaceXAI Rebrand

The launch also marks the first major product since xAI formally ceased to exist. SpaceX acquired Musk's AI venture in February, and on Monday the company rebranded as SpaceXAI — a tidying-up exercise that ties Grok, Cursor, and SpaceX's satellite infrastructure under one publicly traded entity.

SpaceXAI's stock, listed as SPCX on the Nasdaq, now carries the weight of Musk's AI ambitions alongside his space business. The xAI unit reportedly spent $6.4 billion last year — twice its revenue. Grok 4.5 is the first model that needs to prove the investment was worth it.

## The Bigger Picture

Wednesday's model drops — Grok 4.5, GPT-Live, and Thursday's GPT-5.6 — compress what used to be a year's worth of AI capability releases into a single 24-hour window. For Indian engineers choosing which API to build on, the calculus is shifting from "which model is best" to "which model is best per dollar." Musk is betting that Grok 4.5, backed by SpaceX's infrastructure and Cursor's developer trust, can win that argument."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "SpaceXAI Launches Grok 4.5 on AI's Biggest Day. It Was Trained on Tens of Thousands of Nvidia Chips.",
    "subheadline": "Elon Musk's newly rebranded AI unit released its most capable model hours before OpenAI ships GPT-5.6 — and it costs a fifth of what Anthropic charges.",
    "slug": make_slug("spacexai-grok-45-launch-cursor-nvidia-ai-wars"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian developers and AI startups are the largest non-US user base for coding tools like Cursor; Grok 4.5's competitive pricing could reshape which frontier models Indian companies build on.",
    "tags": ["spacexai", "grok", "elon-musk", "nvidia", "cursor", "ai-models", "indian-startups"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/spacexai-launches-grok-45-model-coding-agentic-tasks-2026-07-09/"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/technology/3493126/spacex-grok-45-same-day-openai-new-model/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-stock-price-spacex-grok-ai-model-85a77a02"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/spacexai-will-reportedly-release-a-major-new-ai-model-this-week-2000627896"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5e/Elon_Musk_-_54820081119_%28cropped%29.jpg",
    "image_caption": "Elon Musk, whose SpaceXAI launched Grok 4.5 as its most capable AI model yet",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}


# ── Article 3: OpenAI GPT-Live Voice Models ────────────────────────────

art3_body = """OpenAI on Wednesday launched GPT-Live, a new family of voice models that can listen and speak at the same time — a technical leap that sounds incremental on paper but could reshape how voice-driven software works in practice.

The two models, GPT-Live-1 and GPT-Live-1 mini, are available globally starting Wednesday. They join a crowded week for OpenAI, which is also rolling out GPT-5.6 on Thursday. But GPT-Live addresses a different frontier altogether: real-time, full-duplex voice interaction, where the AI does not wait for you to finish speaking before it starts responding.

## What Full-Duplex Means

Today's voice assistants — Siri, Alexa, Google Assistant — operate in half-duplex mode. You speak, you wait, the assistant responds. GPT-Live breaks that pattern. The model can process incoming speech while simultaneously generating its own output, enabling conversations that feel closer to speaking with a human than issuing commands to a machine.

OpenAI had already signalled this direction in May, when it launched GPT-Realtime-2, GPT-Realtime-Translate (covering 70-plus input languages into 13 output languages), and GPT-Realtime-Whisper for live transcription. GPT-Live builds on that stack, packaging simultaneous listening and speaking into a single model designed for consumer and enterprise voice agents.

## The India Angle: Voice Is Everything

For India's technology ecosystem, voice AI is not a novelty — it is an existential category. India has over a billion mobile phone users, many of whom interact with digital services primarily through voice rather than text. The country's $64-billion IT outsourcing industry still runs millions of voice-based customer support calls daily. And Indian startups like Sarvam AI and Krutrim are building language models specifically for India's 22 officially recognised languages.

GPT-Live's pricing — $32 per million audio input tokens for GPT-Live-1 — is steep for most Indian use cases at scale. But the mini variant, designed for lower-cost applications, could open doors for Indian developers building voice agents for healthcare, education, and government services where latency and naturalness matter.

## What Indian Developers Can Build

The practical applications extend well beyond customer support chatbots. Consider a voice-powered Aadhaar helpline that answers questions while simultaneously verifying the caller's identity. Or an educational tutoring agent that listens to a student reading aloud in Hindi and provides real-time corrections without interrupting the flow. Or a telehealth system where a doctor speaks with a patient in Tamil while the AI simultaneously transcribes, translates for a specialist listening in English, and flags medical keywords.

These use cases demand exactly what GPT-Live offers: the ability to listen, process, and respond in parallel, without the stilted turn-taking that makes current voice assistants feel robotic.

## The Competitive Landscape

OpenAI is not alone in the voice AI race. Google's Gemini powers the rebuilt Siri AI launching later this year. Amazon has been quietly upgrading Alexa's conversational capabilities. And India's own Bhashini platform — the government's multilingual translation initiative — is building voice infrastructure for public services.

But GPT-Live's simultaneous listening-and-speaking capability is, for now, a technical first among commercially available models. The question for Indian developers is whether they can afford to build on it — and whether OpenAI will offer India-specific pricing tiers as it has for ChatGPT subscriptions.

## What Comes Next

The voice AI market is projected to reach $50 billion globally by 2029, and India is expected to be among the fastest-growing segments. For Indian engineers at companies like Infosys and TCS — both of which now offer AI services to their clients — GPT-Live represents both a tool and a competitive threat. The tool: a ready-made voice engine to embed in client solutions. The threat: a demonstration that AI can now do what armies of human agents used to do, in real time, in multiple languages, around the clock.

OpenAI's bet is that developers will choose GPT-Live over building their own voice stack. For Indian AI builders, the bet is whether to ride OpenAI's wave or build something that works better for a billion people who do not speak English as their first language."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI's GPT-Live Can Listen and Talk at the Same Time. India's Voice AI Race Just Accelerated.",
    "subheadline": "The new models enable full-duplex voice conversations — and they matter more for India's billion-phone, voice-first market than any text-based model release this year.",
    "slug": make_slug("openai-gpt-live-voice-models-india-developers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian developers building voice AI for the subcontinent's 22-language, voice-first market now have a commercially available full-duplex engine — but pricing and language support will determine whether it works for India-scale deployments.",
    "tags": ["openai", "gpt-live", "voice-ai", "indian-startups", "sarvam-ai", "ai-models"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-launches-gpt-live-voice-models-that-listen-speak-simultaneously-2026-07-09/"},
        {"name": "Reuters — OpenAI audio models (May 2026)", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-unveils-three-audio-models-real-time-voice-tasks-2026-05-07/"},
        {"name": "OpenAI Developer Community", "url": "https://community.openai.com/t/new-realtime-voice-models-in-the-api/1225381"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "Sam Altman, CEO of OpenAI, which launched GPT-Live voice models capable of simultaneous listening and speaking",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}


# ── Insert all articles ────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
