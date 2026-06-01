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
        "headline": "Zoho's Sridhar Vembu Says Big Tech Is Trading in an 'Insane Bubble.' NRI Portfolios Are Deeply Exposed.",
        "subheadline": "India's most prominent bootstrapped tech founder warns that AI-driven valuations — NVIDIA at 20x sales, Apple at 10x — have surpassed dot-com era excess. Separately, he argues AI itself is rapidly commoditising. Both claims land squarely on the Indian American investor class.",
        "slug": make_slug("sridhar-vembu-zoho-big-tech-insane-bubble-nri-portfolios"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian Americans are the highest-earning ethnic group in the US and disproportionately concentrated in tech sector stocks — NVIDIA, Apple, Google, Meta. Vembu's bubble warning and his AI commoditisation thesis together challenge the two pillars of NRI tech wealth: equity portfolios and career moats.",
        "tags": ["zoho", "sridhar-vembu", "stock-market", "ai-bubble", "nri-investors", "big-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://storyboard18.com/"},
            {"name": "IANS via ianslive.in", "url": "https://ianslive.in/"},
            {"name": "Inshorts", "url": "https://inshorts.com/"},
            {"name": "Storyboard18 (AI commoditising)", "url": "https://storyboard18.com/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/16594725/pexels-photo-16594725.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Sridhar Vembu does not say things for the audience. The Zoho founder and chief scientist — a man who moved his headquarters from Silicon Valley to a village in Tamil Nadu and built a $1 billion-plus revenue company without a single dollar of outside funding — posted a short, blunt assessment on X this weekend: Big Tech stock valuations are in an "insane bubble, even bigger than 1999."

He brought receipts. NVIDIA is trading at roughly 20 times its annual sales. Apple and Microsoft sit at about 10x each. Alphabet at 11x. Meta at 7.5x. Micron at 19x. These are not price-to-earnings ratios, which can be massaged with buybacks and accounting choices. These are price-to-*sales* multiples — the rawest measure of what the market is willing to pay per dollar a company actually brings in.

## The Scott McNealy Test

To drive the point home, Vembu invoked the ghost of the last crash. After Sun Microsystems' stock collapsed in the early 2000s, its CEO Scott McNealy told investors what 10x revenue really meant: "To give you a ten-year payback, I have to pay you 100 per cent of revenues for 10 straight years in dividends. That assumes I can get that by my shareholders. That assumes I have zero cost of goods sold, which is very hard for a computer company. That assumes zero expenses — which is really hard with 39,000 employees."

McNealy's punchline: "What were you thinking?"

The comparison is not exact. Today's Big Tech companies are vastly more profitable than Sun Microsystems ever was. NVIDIA's gross margins hover near 75 per cent. Apple's services business throws off cash at extraordinary rates. These are not pre-revenue startups burning through venture capital. But Vembu's argument is not that these companies are bad businesses — it is that the market has priced them as though the current trajectory of AI-driven growth will compound indefinitely, and history suggests that assumption breaks.

## AI Is Rapidly Commoditising

In a separate but related post, Vembu endorsed a view from Oracle CTO Larry Ellison: that the real value in AI will not reside in the models themselves but in the private enterprise data and applications built around them. "AI is rapidly commoditising," Vembu wrote. "The value shifts to what is built around it."

This is a more structural claim. If foundational AI models — GPT, Claude, Gemini, Llama — converge in capability and price (as DeepSeek's recent permanent price cuts suggest they are), then the companies building the models face margin pressure, and the companies integrating AI into specific business workflows capture the upside. That is a thesis with direct implications for Indian IT services firms like TCS, Infosys and Wipro, which sit on decades of enterprise client relationships and proprietary process knowledge.

## Why NRIs Should Care

Indian Americans are the highest-earning ethnic group in the United States, with a median household income nearly double the national average. A disproportionate share of that wealth sits in technology stocks, both through direct holdings and through retirement accounts heavily weighted toward the Nasdaq. When NVIDIA trades at 20x sales and an Indian engineer in Santa Clara holds company RSUs worth more than their house, Vembu's warning is not abstract.

The AI commoditisation thesis cuts even deeper. If AI tools increasingly replace the routine software engineering and consulting work that forms the backbone of H-1B employment, then Indian tech professionals face a squeeze from both directions: their stock portfolios are overvalued and their career moats are eroding.

Vembu, of course, has his own interests. Zoho competes with the very companies he is criticising, and a market correction that reprices Big Tech could benefit smaller, profitable, self-funded companies like his. But the data he cites — price-to-sales ratios that would have made even 1999-era analysts nervous — stands on its own.

The question for the average NRI investor is not whether NVIDIA will keep growing. It probably will. The question is whether 20x sales already prices in a decade of that growth, leaving no margin of safety for the inevitable quarter when guidance disappoints. Scott McNealy learned the answer the hard way. Vembu is suggesting the class has not changed, only the students."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Just Shipped a 24/7 AI Agent That Works While You Sleep. It Costs $100 a Month.",
        "subheadline": "Gemini Spark, now live for Google AI Ultra subscribers, runs autonomously across Gmail, Docs and the web — even when your phone is off. Built on Gemini 3.5 and Google's Antigravity platform, it is the clearest signal yet that the AI assistant wars have moved from chatbots to autonomous agents.",
        "slug": make_slug("sundar-pichai-gemini-spark-ai-agent-google-io"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Google's CEO is Indian-origin. Thousands of Indian engineers at Google built the underlying Gemini models and Antigravity infrastructure. For Indian developers and tech workers in the US, Spark sets the benchmark for what AI agents can do — and raises the bar for what employers will expect from human workers.",
        "tags": ["google", "sundar-pichai", "gemini-spark", "ai-agent", "google-io", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Android Police", "url": "https://www.androidpolice.com/"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/"},
            {"name": "Memeburn", "url": "https://memeburn.com/"},
            {"name": "Google Blog", "url": "https://blog.google/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "body": """Close your laptop. Lock your phone. Go to sleep. When you wake up, the emails have been drafted, the research has been compiled, and the meeting agenda is sitting in your Google Doc. That is the pitch behind Gemini Spark, Google's new persistent AI agent that began rolling out to US-based AI Ultra subscribers this week at $99.99 per month.

Announced by Alphabet CEO Sundar Pichai at Google I/O 2026 on May 19 and now reaching its first production users, Spark represents a decisive shift in how Google thinks about artificial intelligence. This is not a chatbot you talk to. It is an agent you assign work to — and it keeps working in the background, 24 hours a day, on Google's cloud servers, regardless of whether your device is on.

## How It Works

Spark runs on Gemini 3.5, Google's latest model family, and operates through a framework called Antigravity — Google's cloud-based agent runtime that executes multi-step tasks without requiring an active client session. Josh Woodward, Google's vice president for the Gemini app, described it vividly: "Even when you close your laptop or turn off your phone, Spark can keep working in the background. It almost feels like you're tossing things over your shoulder, Spark's catching them, and gets the job done."

The agent is built around three components. **Tasks** are one-off assignments: "summarise my unread emails about the Johnson contract and draft a reply." **Skills** are reusable capabilities that Spark learns from your patterns: how you format meeting notes, which colleagues you loop into project updates, your preferred level of detail in research summaries. **Schedules** allow recurring automation: a daily digest of competitor news, a weekly status report pulled from your project docs, a nightly scan of your calendar for conflicts.

Connections to Gmail, Calendar, Drive, Docs, Sheets and Slides are available but turned off by default. Users must explicitly activate each integration. Spark does not scan inboxes indiscriminately — it acts only on assigned tasks, schedules or activated skills. Google has also designed the agent to pause and ask for confirmation before taking actions it classifies as "major," such as sending an email or modifying a shared document.

## The Pricing Question

At $99.99 per month, AI Ultra is not casual spending. It sits alongside Google AI Pro ($19.99/month) and the free tier, creating a three-layer pricing architecture that mirrors enterprise software stratification. For a senior engineer or product manager in the Bay Area earning $300,000 or more, $100 per month for a persistent assistant is a rounding error. For an Indian developer in Bengaluru or a graduate student on OPT in the US, it is a meaningful barrier.

Google has not announced plans for India-specific pricing or a timeline for expanding Spark beyond the US. Given that India is already one of Google's largest markets for Gemini adoption — ChatGPT had roughly 72 million daily users in India by late 2025, and Google is fighting hard for that market — the pricing gap is conspicuous.

## What This Means for Indian Tech Workers

The diaspora angle here runs in two directions. On the supply side, thousands of Indian engineers at Google built the Gemini models, the Antigravity runtime, and the infrastructure that makes Spark possible. Pichai himself, born in Madurai, Tamil Nadu, described Spark as "your personal AI agent that helps you navigate your digital life, taking action on your behalf and under your direction." The product is, in a very literal sense, built by Indians.

On the demand side, Spark raises the productivity baseline. If a $100-per-month agent can handle email triage, document synthesis, scheduling and research — tasks that currently occupy hours of knowledge worker time — then the expectation for what a human worker should accomplish in a day shifts upward. For Indian H-1B holders in tech roles, who already face performance scrutiny in a tightening job market, the bar just moved.

## The Competitive Landscape

Spark does not exist in isolation. Microsoft's Copilot is deeply integrated into Office 365 and Teams. Anthropic's Claude handles long-context document work. OpenAI's Codex is surging in India with 27x user growth since January. But none of these competitors currently offer a persistent, always-on agent that runs independently of the user's device. That is Spark's differentiator — and it is the feature that makes the $100 price point defensible for power users.

The AI assistant wars have officially moved from "talk to me" to "work for me." The question is no longer whether you want an AI assistant. It is whether you can afford one that never clocks out."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
