#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 06:00 UTC run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / "workspace" / ".env.supabase"
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


# ═══════════════════════════════════════════
# ARTICLE 1: Meta Muse Spark API Delays
# ═══════════════════════════════════════════

art1_body = """Meta's newest AI model has a problem that no amount of compute can fix: it cannot get its software out the door.

According to a Wall Street Journal report published on June 3, Meta Platforms has repeatedly pushed back plans to release the application programming interface for Muse Spark, the proprietary AI model it unveiled in April. As of Tuesday, there was no scheduled launch date. A Meta spokesperson told Reuters the company is testing the API with early partners and expects to release it "this month," but the timeline has slipped multiple times since Meta AI chief Alexandr Wang promised in April that access would arrive "soon."

## The Model That Changed Meta's Playbook

Muse Spark is not just another model refresh. It is Meta's first proprietary, closed-source AI system — a sharp departure from the company's years-long bet on open-weight models through the Llama family. Built over nine months by Meta's newly formed Superintelligence Labs under Wang's leadership, Muse Spark was designed to close the performance gap with OpenAI and Anthropic on multimodal reasoning, agentic tasks, and tool use. Internal benchmarks reportedly showed it competitive with GPT-5.5 and Claude Opus on most evaluations.

But without an API, developers cannot build on it. And in the AI market of mid-2026, where OpenAI, Anthropic, and Google are fighting for every integration and every enterprise contract, two months of silence is an eternity.

## Why Indian Developers Should Care

The delay is not just a Silicon Valley inside-baseball story. It strikes at the heart of an ecosystem that Indian developers and startups helped build.

For the past three years, Meta's open-source Llama models formed the backbone of AI development across India's startup ecosystem. Sarvam AI, Krutrim, BharatGPT, and dozens of smaller firms fine-tuned Llama weights for Indian languages, healthcare, and agricultural applications. Llama's open-weight licence — free for organisations with fewer than 700 million monthly active users — made frontier AI accessible to companies that could never afford to train their own models.

With Muse Spark, Meta has signalled a strategic pivot toward monetisation. The model is closed. Access requires an API key, and presumably, a credit card. Indian teams that bet on Meta's open ecosystem are now watching the company move in the opposite direction, at exactly the moment when the API they were promised keeps not arriving.

## The Bigger Picture

Meta employs more than 20,000 workers in India across engineering, content moderation, and operations — one of its largest international workforces. The company's $115 to $135 billion capital expenditure plan for 2026, mostly directed at AI infrastructure, will flow through contracts and partnerships that touch Indian engineering talent at every level.

Meanwhile, Meta also unveiled a business AI agent on June 3, aimed at helping companies manage day-to-day operations — a direct shot at OpenAI's enterprise ambitions and Anthropic's fast-growing business revenue. The company clearly has the product vision. Whether it can execute on the developer tooling side is another question entirely.

For Indian engineers at Meta and Indian developers waiting for Muse Spark access, the message is uncomfortable but clear: the company that once gave away its best models for free is now struggling to sell them. In a market where Anthropic just filed for an IPO at $965 billion and OpenAI is preparing GPT-5.6, Meta's delay is not merely inconvenient. It is strategically expensive."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Keeps Delaying Its Muse Spark API. Indian Developers Who Built on Llama Are Left Waiting.",
    "subheadline": "Two months after Alexandr Wang promised the API would arrive 'soon,' Meta still has no launch date. The open-source ecosystem that Indian startups relied on is fading.",
    "slug": make_slug("meta-muse-spark-api-delay-indian-developers-llama"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian startups built products on Meta's open-source Llama ecosystem. The shift to proprietary Muse Spark — now delayed — threatens their roadmaps. Meta's 20K+ Indian workforce is also directly affected by the company's AI monetisation struggles.",
    "tags": ["meta", "muse-spark", "ai-models", "indian-startups", "llama", "open-source"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/meta-keeps-delaying-the-release-of-its-new-ai-model-to-developers"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-repeatedly-pushes-back-new-ai-model-release-developers-wsj-says-2026-06-03/"},
        {"name": "Stratechery", "url": "https://stratechery.com/2026/mythos-muse-and-the-opportunity-cost-of-compute/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Server racks in a data center powering the AI models that Meta, OpenAI, and Anthropic are racing to ship",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art1_body.strip()
}


# ═══════════════════════════════════════════
# ARTICLE 2: Cognizant-Snowflake AI Agents
# ═══════════════════════════════════════════

art2_body = """While India's legacy IT giants are watching their market capitalisation evaporate — TCS shed 9 per cent in a single session last week — Cognizant Technology Solutions just collected a trophy that tells a different story.

At Snowflake Summit 26 on June 3, Cognizant was named Snowflake's CoCo Catalyst Partner of the Year for Impactful Customer Story. More importantly, the Teaneck, New Jersey-based company announced an expanded collaboration with Snowflake to deploy production-grade AI agents across enterprise data engineering, analytics, and decision workflows using the Snowflake CoCo platform.

## From Pilot Projects to Production AI

"When the data foundation is AI-ready and business context is built in, build cycles collapse," said Naveen Sharma, Senior Vice President and Practice Head for AI & Analytics at Cognizant. "With Snowflake CoCo, we are putting production-grade AI into enterprise workflows in hours, not weeks."

The word "production" is doing heavy lifting in that sentence, and intentionally so. The knock against Indian IT services companies for the past two years has been that they excel at running AI pilots and proofs of concept but struggle to deliver systems that work at enterprise scale. Cognizant is making a deliberate counter-argument: it is not just experimenting with AI agents, it is deploying them into live business operations.

Snowflake CoCo, the cloud data company's coding agent platform, has become its fastest-growing product ever, with more than 7,100 users since launch. It is powered by Anthropic's Claude models and designed to translate a single prompt into production-ready data pipelines and applications. Cognizant's approach layers its own industry expertise on top — what the company calls its "AI Builder" strategy — to compress the timeline from semantic model generation through agent orchestration to governed analytics.

## What This Means for 300,000 Workers

Cognizant employs roughly 350,000 people worldwide, the vast majority based in India. For these workers, the question is not whether AI will change their jobs — it already has. The question is whether their employer will be on the building side or the disrupted side of that change.

The Snowflake partnership suggests Cognizant is trying to position itself on the right side. Rather than competing on headcount — the traditional Indian IT model of billing clients for thousands of engineers writing and maintaining code — Cognizant is pivoting toward selling outcomes powered by AI agents. Fewer people, more intelligence, higher margins.

This is the same strategic pivot that TCS, Infosys, and Wipro are attempting with Microsoft Copilot licences. But Cognizant's approach is different in one crucial respect: it is building the agents, not just buying someone else's tool. The CoCo Catalyst award recognises delivery, not procurement.

## The Diaspora Dimension

For the roughly 300,000 Indian-Americans who work in IT services — many of them on H-1B visas at Cognizant, TCS, Infosys, and their competitors — the AI transition carries existential stakes. If Indian IT companies successfully pivot to AI-powered delivery, the sector survives and immigration sponsorship continues. If they fail, the layoffs and visa clock start ticking.

Cognizant's Snowflake bet is not a guarantee. The company's stock is down significantly this year, and its market capitalisation trails TCS and Infosys by wide margins. But in the AI agent economy, a well-placed partnership may matter more than a well-padded headcount.

Naveen Sharma's team will need to prove that Indian IT can do more than implement someone else's AI. This week in San Francisco, they at least showed they are trying."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Cognizant Won Snowflake's Top AI Award. It May Be Indian IT's Best Argument for Survival.",
    "subheadline": "At Snowflake Summit 26, Cognizant deployed production-grade AI agents in hours, not weeks. For 350,000 employees, the pivot from headcount to intelligence is now existential.",
    "slug": make_slug("cognizant-snowflake-coco-ai-agents-indian-it-pivot"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Cognizant employs 350K people, mostly in India, and sponsors thousands of H-1B visas. Its pivot to AI agent delivery — not just procurement — signals whether Indian IT services can survive the AI transition. The 300K+ Indian-Americans in IT services are directly affected.",
    "tags": ["cognizant", "snowflake", "ai-agents", "indian-it", "enterprise-ai", "coco"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "PR Newswire / Cognizant", "url": "https://www.morningstar.com/news/pr-newswire/20260603ny27234/cognizant-accelerates-enterprise-ai-adoption-with-snowflakes-cortex-powered-intelligent-agents"},
        {"name": "Barchart / Business Wire", "url": "https://www.barchart.com/story/news/33367982/cognizant-accelerates-enterprise-ai-adoption-with-snowflakes-cortex-powered-intelligent-agents"},
        {"name": "Snowflake Summit 26 Newsroom", "url": "https://www.snowflake.com/en/newsroom/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Cognizant_Technology_Solutions_-_Kolkata_2011-08-29_4824.JPG/1280px-Cognizant_Technology_Solutions_-_Kolkata_2011-08-29_4824.JPG",
    "image_caption": "Cognizant Technology Solutions office in Kolkata, one of the company's major India engineering centres",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art2_body.strip()
}


# ═══════════════════════════════════════════
# ARTICLE 3: OpenAI Codex Sites + Business Platform
# ═══════════════════════════════════════════

art3_body = """On June 2, OpenAI announced something that should give every Indian IT services executive a long, uncomfortable pause.

Codex, the company's AI coding agent, is now embedded across all of ChatGPT. It can create interactive, hosted websites and applications from a single prompt. It can read a Salesforce database, annotate a slide deck, build a project dashboard, and share it with a team via URL — all inside a chat window. Six new business plugins ship out of the box, including integrations with Salesforce data and enterprise workflows. OpenAI calls the feature "Sites," and it is rolling out first to Business and Enterprise plan subscribers.

## What Sites Actually Does

The concept is deceptively simple. A product manager at a Fortune 500 company asks ChatGPT to build a quarterly review dashboard. Codex generates the application, hosts it, and gives the team a link. Anyone in the workspace can view it, interact with it, and provide feedback. The PM can point to a specific chart, annotate it, and ask Codex to change the label. The change happens instantly.

This is not a toy demo. The annotations feature already exists for code and Markdown files. Developers have been using it to review and refine code in Codex for months. OpenAI is now extending the same workflow to business content: documents, spreadsheets, slides, and full web applications.

"Building apps has never been easier," OpenAI posted on X alongside the launch. It is the kind of claim that tech companies make every quarter. But this time, the underlying capability is real enough that Wall Street noticed: Salesforce dropped 4.1 per cent on June 3, even as analysts maintained buy ratings.

## The Indian IT Problem

Here is why this matters for the diaspora.

The Indian IT services industry — TCS, Infosys, Wipro, Cognizant, HCL Tech, and their peers — generates roughly $254 billion in annual revenue, employs more than 5 million people in India, and sponsors tens of thousands of H-1B visas in the United States every year. The core business model has been consistent for three decades: take requirements from Western companies, deploy large teams of engineers in India to build and maintain software, and bill by the hour or by the headcount.

OpenAI's Sites feature attacks that model at its foundation. When a business user can prompt an AI to build a functional dashboard, data pipeline, or internal tool in minutes, the demand for a 20-person offshore team to do the same work over six weeks drops sharply. Codex does not eliminate the need for complex enterprise software engineering. But it eliminates a category of work — internal tools, lightweight apps, data visualisation, workflow automation — that accounts for a significant share of Indian IT services revenue.

## Not the First Threat, But the Most Tangible

Indian IT bulls will point out that predictions of automation-driven disruption have circled for a decade without materialising. They are right. But earlier waves of automation — robotic process automation, low-code platforms, cloud migration — primarily targeted repetitive tasks and freed up engineers for higher-value work.

Codex Sites is different because it targets the output, not the process. It generates the finished application. The business user who receives it does not need to know or care whether an offshore team or an AI agent built it. If the result is good enough, the team was never needed.

The Indian IT stocks are already pricing in this reality. TCS lost 9 per cent in a single session last week. The Nifty IT index has underperformed the broader market by a wide margin in 2026. But the human cost runs deeper than the ticker. For the Indian-American engineer in New Jersey whose visa is tied to a services company, or the mid-career developer in Bengaluru whose team builds exactly the kind of internal tools Codex now generates, the question is no longer theoretical.

OpenAI is not the only threat — Anthropic, Google, and Microsoft are all building similar capabilities. But OpenAI just made the threat concrete, named it Sites, and put it inside the most widely used AI product on the planet."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Turned ChatGPT Into a Business App Builder. Five Million Indian IT Jobs Are in the Crosshairs.",
    "subheadline": "Codex can now generate hosted websites, dashboards, and enterprise tools from a single prompt. The $254 billion Indian IT services industry was built to do exactly this work.",
    "slug": make_slug("openai-codex-sites-business-apps-indian-it-threat"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "OpenAI's Codex Sites directly automates the internal tools, dashboards, and lightweight apps that Indian IT services companies bill millions to build. This threatens 5M+ Indian tech jobs and tens of thousands of H-1B visa holders whose immigration status depends on services company sponsorship.",
    "tags": ["openai", "codex", "chatgpt", "indian-it-services", "enterprise-ai", "automation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/02/openai-codex-chatgpt-business-plugins/"},
        {"name": "OpenAI on X", "url": "https://x.com/OpenAI/status/1929953827682"},
        {"name": "MarketBeat / Salesforce", "url": "https://www.marketbeat.com/stocks/NYSE/CRM/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/12969403/pexels-photo-12969403.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "An analytics dashboard on a laptop screen — the kind of business tool OpenAI's Codex can now generate from a single prompt",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art3_body.strip()
}


# ═══════════════════════════════════════════
# INSERT ALL
# ═══════════════════════════════════════════

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
