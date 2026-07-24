#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-26 23:00 PDT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ---------------------------------------------------------------------------
# ARTICLE 1 — Satya Nadella AI Warning + Project Kilby + Copilot Cowork
# ---------------------------------------------------------------------------

article1_body = """Satya Nadella does not usually pick fights in public. The Microsoft chief executive tends toward the diplomatic — a habit of speaking in abstractions about platforms and ecosystems, always generous enough to leave rivals unnamed. So when he published an essay on X on June 14 titled *"A frontier without an ecosystem is not stable,"* and then sharpened the argument in a Wall Street Journal interview a week later, the sheer directness was the story as much as the words.

His thesis is blunt: a handful of frontier AI labs are accumulating too much leverage over how artificial intelligence develops, what it costs, and who gets access. If left unchecked, Nadella argues, every company in every sector will eventually cede its competitive knowledge to a few models "that eat everything they see."

"You can't say, hey, all white-collar jobs are gone and this could even be a weapon and we will use all the power to build data centres," he told the Journal.

The timing is strategic. Microsoft trailed its peers in developing its own frontier model through late 2025, watching Copilot subscribers drift toward Google's Gemini. Rather than pour more billions into a single model bet, Nadella has pivoted: he wants to commoditise frontier models entirely.

## The Copilot Cowork play

That vision materialised on June 16, when Microsoft launched Copilot Cowork to general availability worldwide. The product — a long-running AI agent that can perform multi-step tasks across Microsoft 365 even when a user's laptop is shut — now ships with multi-model support. Anthropic's Claude reviews GPT's output for accuracy before delivering it to the user. A "Model Council" feature lets enterprise customers compare answers from different models side by side.

Usage-based billing runs at one cent per Copilot Credit, which sounds modest until the maths lands. A heavy Cowork user can add $400 to $700 per month on top of the existing $30 Copilot seat. A team of fifty, used moderately, racks up $5,000 to $15,000 monthly. Microsoft's bet is that the productivity gain justifies the bill — and that locking organisations into the Microsoft 365 workflow matters more than locking them into a single model.

## A city's worth of power in West Texas

If Copilot Cowork is the software play, Project Kilby is the hardware one. On June 22, Chevron and Microsoft signed a 20-year power purchase agreement for a co-located natural-gas plant in Pecos, Texas. At 2.67 gigawatts — enough to power a city the size of San Francisco — it is among the largest dedicated AI power projects ever announced.

The deal sidesteps what may be AI's most binding constraint. Utility interconnect queues now stretch three to seven years. Microsoft cannot wait that long. By co-locating the plant beside the data centre, it avoids both the grid bottleneck and the transmission buildout. First power is expected in 2028, with a final investment decision from Chevron by year's end. The campus is projected to generate $10 billion in state and local tax revenue and support 2,000 permanent jobs.

## What this means for Indian tech workers

Nadella's warning resonates differently in Hyderabad, Bengaluru, and Cupertino than it does on Sand Hill Road. Indian engineers have been disproportionately responsible for building the AI infrastructure he now says must be democratised. At Microsoft alone, Indians comprise a significant share of the Azure AI, Copilot, and cloud engineering teams.

His call to "reorganise the job" rather than eliminate it — treating companies as a "continuous learning system" of human wisdom and AI tokens — speaks directly to the anxieties of H-1B professionals watching their employers rewrite headcount plans around automation. If Nadella is right that the winning model is multi-model commodity intelligence layered on top of proprietary enterprise data, Indian engineers are well-positioned: they already sit at the intersection of enterprise IT integration and AI deployment.

If he is wrong, and a single lab runs the table, the value of that integration work shrinks. For the hundreds of thousands of Indian-origin professionals in Microsoft's orbit, the outcome of Nadella's bet is not academic. It is personal."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella Says a Few AI Labs Are Eating the World. He Just Signed a 20-Year Deal to Build His Own.",
    "subheadline": "The Microsoft CEO published an essay, gave a pointed interview, launched a multi-model agent platform, and locked in 2.67 gigawatts of Texas power — all in two weeks. The strategy is clear: commoditise the model layer before it commoditises you.",
    "slug": make_slug("nadella-ai-ecosystem-warning-project-kilby-copilot-cowork"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CEO of the world's most valuable tech company is reshaping the AI power structure — with direct implications for H-1B engineers and Indian IT professionals in Microsoft's orbit.",
    "tags": ["satya-nadella", "microsoft", "copilot", "ai", "data-centers", "indian-tech-leaders"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/microsofts-satya-nadella-we-cant-let-ai-giants-eat-the-economy-f2e9da45"},
        {"name": "The Street", "url": "https://www.thestreet.com/technology/microsofts-ceo-sends-the-ai-industry-a-strong-warning"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/energy/chevron-signs-power-supply-deal-with-microsoft-texas-data-center-2026-06-22/"},
        {"name": "Computerworld", "url": "https://www.computerworld.com/article/microsoft-launches-copilot-cowork-with-usage-based-pricing/"},
        {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/msft-stock-and-cvx-sign-20-year-deal-to-power-ai-data-centers/"},
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg/330px-MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, CEO of Microsoft",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body,
}


# ---------------------------------------------------------------------------
# ARTICLE 2 — Google Gemini 3.5 Pro delayed, Flash gets computer use
# ---------------------------------------------------------------------------

article2_body = """Sundar Pichai stood on stage at Google I/O in May and promised Gemini 3.5 Pro would arrive in June. It will not. According to a Business Insider report published this week, the launch has slipped to July — a delay that Google has neither confirmed nor denied. A company spokesperson "declined to comment."

The postponement is not a catastrophe, but it is a tell. Google introduced the 3.5 model family as its answer to the breakneck releases from OpenAI and Anthropic, which have been shipping powerful coding and reasoning models at a pace that has left Google looking like the slow giant it once mocked Microsoft for being. A missed self-imposed deadline does not help.

## What held it up

Early testers reportedly flagged issues with how Gemini 3.5 Pro handles long, multi-step tasks — precisely the kind of agentic workloads that enterprise customers care most about. The model's predecessor, Gemini 3.5 Flash, shipped with a persistent complaint about burning through tokens too quickly. Google appears to want the Pro model to land cleanly enough that it does not inherit the same criticism.

The company is collecting feedback through its Antigravity development environment and the LMArena benchmarking service. Engineers are reportedly focused on chaining complex reasoning steps — the same capability that Anthropic's Claude and OpenAI's GPT-5.5 have been sharpening in real-world deployments.

## Flash, meanwhile, just learned to use a computer

While Pro waits, Gemini 3.5 Flash got a notable upgrade on June 24: built-in computer use. The feature lets developers build AI agents that can see a screen, navigate applications, click buttons, type text, and scroll through pages — all through visual understanding rather than APIs.

This is not new territory. Anthropic offered computer use in Claude last year, and Google had released a standalone computer-use model earlier. What matters is the consolidation: computer use is now baked into the main Flash model rather than requiring a separate, specialised model. Developers building agents that operate across browsers, mobile interfaces, and desktop applications can do so without juggling multiple models.

Google says the system includes safety guardrails: it can require user confirmation before irreversible actions, and it can halt tasks automatically if it detects a prompt-injection attack. Apple, for its part, added Gemini as a coding assistant in Xcode 26.6 this week, placing it alongside Claude and OpenAI's Codex in the developer toolchain.

## The competitive pressure is real

The delay arrives against a backdrop of intensifying competition. OpenAI and Broadcom unveiled Jalapeño, OpenAI's first custom inference chip, earlier this week. Anthropic launched an AI accelerator in Bengaluru with AWS. Microsoft's Copilot Cowork went live with multi-model support. Each move chips away at a window Google cannot afford to leave open.

Google's advantage remains scale — billions of users, deep integration with Search, YouTube, Android, and Workspace — but its model releases have been uneven. Gemini 2.0 Ultra was considered overhyped on arrival. Flash 3.5's token efficiency drew complaints. Pro needs to be good enough to reset the narrative.

## Why Indian engineers are watching closely

Google employs tens of thousands of Indian-origin engineers across its AI research, cloud, and product teams. Many of the researchers behind Gemini — and behind the computer-use capabilities now shipping in Flash — are Indian-origin scientists at Google DeepMind.

For the broader diaspora, the stakes are both professional and financial. Alphabet just joined the Dow Jones Industrial Average, and the stock has taken a hit alongside the broader tech selloff. Indian professionals at Google who hold RSUs are watching their compensation fluctuate with every model announcement and every missed deadline.

The bigger question is whether Google's deliberate approach — delay, refine, ship cleanly — pays off against rivals that ship fast and fix in production. Pichai has bet his company on AI. July will show whether the bet is still on schedule, or whether the schedule is just the first thing that slipped."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Sundar Pichai Promised Gemini 3.5 Pro in June. Google Just Pushed It to July.",
    "subheadline": "The delay comes as Flash 3.5 gains computer-use capability and Apple adds Gemini to Xcode — but OpenAI and Anthropic are not waiting.",
    "slug": make_slug("google-gemini-35-pro-delayed-july-flash-computer-use-pichai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin Alphabet CEO navigates a competitive AI race while thousands of Indian engineers at Google DeepMind build the models — and watch their RSU-heavy compensation move with every announcement.",
    "tags": ["sundar-pichai", "google", "gemini", "ai", "deepmind", "indian-tech-leaders"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/is-google-delaying-gemini-3-5-pro-launch-to-july-for-further-testing"},
        {"name": "Digit.in", "url": "https://www.digit.in/news/general/google-reportedly-postpones-gemini-35-pro-launch-here-is-why.html"},
        {"name": "Google Blog", "url": "https://blog.google/technology/google-deepmind/gemini-computer-use/"},
        {"name": "Android Authority", "url": "https://www.androidauthority.com/gemini-3-5-flash-computer-use/"},
        {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/26/apple-adds-google-gemini-coding-assistant-in-xcode-26-6-update/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg/330px-Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body,
}


# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
