#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 batch"""
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

# ─────────────────────────────────────────────
# Article 1: Google Icefish TPU
# ─────────────────────────────────────────────
art1_body = """Google is no longer content to depend on a single chipmaker for the silicon that powers its AI empire. This week, reports emerged that Sundar Pichai's company is in talks with Samsung Electronics to manufacture part of its next-generation tensor processing unit, codenamed Icefish — while simultaneously negotiating with Intel to produce more than three million TPUs by 2028.

The arrangement, first reported by The Information, would split Icefish production across three foundries. TSMC, the Taiwanese giant that has fabricated every generation of Google's TPU to date, would handle the main compute die using its cutting-edge 1.4-nanometre process. Samsung would manufacture a separate memory input-output die on its 2nm node — the component that bridges the processor and high-bandwidth memory. Intel, which landed Tesla's Terafab project earlier this year, would serve as a second-source manufacturer for the broader TPU lineup.

It is, by any measure, the most complex chip supply chain a hyperscaler has attempted.

## Why Google is doing this

The logic is straightforward: TSMC is running out of room. At its annual shareholders' meeting on June 4, TSMC CEO C.C. Wei conceded that the company's leading-edge nodes are "capacity constrained for the foreseeable future." With Nvidia, Apple, AMD, and Broadcom all competing for the same sub-3nm wafers, even a company with Google's purchasing power cannot guarantee enough supply to train and serve the next generation of AI models.

Google's TPU business has quietly become a material revenue driver. Cloud customers — including AI startups that cannot afford or obtain enough Nvidia H100s — increasingly rely on TPU access as a reason to choose Google Cloud over AWS or Azure. Any supply disruption would dent not just Google's internal AI research but its cloud market share.

MediaTek, the Taiwanese chip design firm better known for smartphone processors, is reportedly collaborating on Icefish's design — a signal that Google is widening its engineering partnerships alongside its manufacturing ones.

## What it means for Indian engineers and NRIs

Google employs one of the largest concentrations of Indian-origin engineers in Silicon Valley, and its TPU design team is no exception. The shift to a multi-foundry strategy will create new roles in supply chain management, chip verification, and cross-fab testing — disciplines where Indian semiconductor talent, increasingly sought after by both US firms and India's own fab projects, is in high demand.

For NRI investors, the move underlines a structural shift in the $600 billion semiconductor industry: the era of TSMC as the sole chokepoint is ending. Intel's resurgence under CEO Lip-Bu Tan — its stock is up 169% this year — and Samsung's push to win 2nm orders both create new vectors of competition. India's own semiconductor ambitions, including Tata Electronics' Dholera fab and Micron's Gujarat ATMP facility, sit downstream of exactly these supply-chain diversification decisions.

If Google's three-foundry experiment works, expect every hyperscaler to follow. And the engineers designing, verifying, and managing that complexity will disproportionately be Indian.

*Sources: The Information, Reuters, SamMobile, Investors.com*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Pichai's Three-Foundry Gambit: Google Splits Its Next AI Chip Across TSMC, Samsung, and Intel",
    "subheadline": "The Icefish TPU will be the first Google chip manufactured across three separate foundries — a signal that TSMC's dominance is no longer enough for AI's insatiable demand.",
    "slug": make_slug("google-icefish-tpu-samsung-tsmc-intel-foundry"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin engineers at Google are central to TPU design, and the multi-foundry shift creates new semiconductor career paths relevant to NRIs in chip design and supply chain management.",
    "tags": ["google", "semiconductors", "sundar-pichai", "tsmc", "samsung", "intel", "ai-chips", "tpu"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/google-talks-with-samsung-make-part-next-gen-chip-information-reports-2025-06-12/"},
        {"name": "The Information", "url": "https://www.theinformation.com/"},
        {"name": "SamMobile", "url": "https://www.sammobile.com/news/samsung-could-make-part-google-next-gen-tpu-chip-2nm-tech/"},
        {"name": "CoinCentral", "url": "https://coincentral.com/alphabet-googl-stock-google-taps-samsung-and-tsmc-for-its-most-ambitious-ai-chip-yet/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ─────────────────────────────────────────────
# Article 2: Sarvam AI at G7
# ─────────────────────────────────────────────
art2_body = """When the G7 leaders sit down for a working lunch on artificial intelligence in Evian-les-Bains next week, the guest list will include the usual Western AI royalty: Sam Altman of OpenAI, Demis Hassabis of Google DeepMind, Dario Amodei of Anthropic. But one name on the roster, confirmed by French officials and reported by Reuters, stands out: Pratyush Kumar, co-founder and CEO of Sarvam AI — a Bengaluru-based startup that did not exist three years ago.

Kumar's invitation to the June 15–17 summit marks the first time an Indian-origin AI company founder has been seated alongside the chief executives of the world's most powerful AI labs at the G7's highest diplomatic table. It is a recognition not just of Sarvam but of India's accelerating claim to being a builder, not merely a consumer, of frontier AI.

## From IIT Madras to the G7

Sarvam AI was founded in August 2023 by Kumar and Vivek Raghavan, both previously associated with the AI4Bharat initiative at IIT Madras. The company builds large language models and multimodal AI systems optimised for Indian languages — a market of 1.45 billion people, the vast majority of whom cannot type fluently in English.

In February 2026, Sarvam unveiled its 30-billion and 105-billion parameter models at Prime Minister Modi's India AI Impact Summit. The models support 22 Indian languages and compete with global peers on maths, coding, and reasoning benchmarks. The company has since signed agreements with Tamil Nadu, Madhya Pradesh, and other state governments to deploy AI in citizen-facing services.

The commercial traction followed. In April, Sarvam closed a $300–350 million funding round at a $1.5 billion valuation, led by Bessemer Venture Partners with participation from Nvidia, Amazon, and Saudi Arabia's Prosperity7 Ventures. That valuation makes it India's most valuable homegrown AI company.

## What the G7 seat signals

The summit agenda, crafted by France's Macron, centres on AI regulation, infrastructure, and the protection of minors online. The full attendee list — which includes Marc Benioff of Salesforce, Arthur Mensch of Mistral AI, and Robin Rombach of Black Forest Labs — tilts heavily toward companies that are building foundational models, not just deploying them.

Kumar's presence reflects a deliberate choice by the French hosts to include a voice from the Global South at a table historically dominated by American and European firms. India has made no secret of its ambition to chart an independent AI path. Modi has repeatedly argued that countries beyond the US and China need to "control their own destiny" with AI, and the $67.5 billion in AI investment commitments from American firms at the India AI Impact Summit underscored that this is more than rhetoric.

## Why NRIs should be watching

For Indian Americans in the AI industry — and there are tens of thousands across OpenAI, Anthropic, Google, Meta, and Microsoft — Sarvam's trajectory reframes the calculus of where to build a career. The company's pitch is that India's digital infrastructure layer (UPI, Aadhaar, DigiLocker) and its linguistic diversity create a natural moat for locally built AI — one that Silicon Valley's English-first models cannot easily breach.

For NRI investors, Sarvam's valuation leap from zero to $1.5 billion in under three years, backed by Nvidia and Amazon, signals that India's AI startup ecosystem has graduated from the "interesting but early" category to one demanding serious capital allocation.

Kumar will be sitting three chairs from Sam Altman. That alone tells you something has shifted.

*Sources: Reuters, YourStory, The Hindu BusinessLine, Livemint*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India's Sarvam AI Gets a Seat at the G7 — Alongside Altman, Hassabis, and Amodei",
    "subheadline": "Pratyush Kumar will be the first Indian AI startup founder to join the G7's top tech table when leaders convene in France next week.",
    "slug": make_slug("sarvam-ai-g7-summit-pratyush-kumar-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "An Indian AI startup founder sitting alongside OpenAI and Anthropic CEOs at the G7 signals that India is now seen as an AI builder, not just a market — reshaping career and investment decisions for NRIs in tech.",
    "tags": ["sarvam-ai", "g7", "pratyush-kumar", "india-ai", "sovereign-ai", "startups"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/tech-executives-attend-g7-summit-leaders-address-ai-online-safety-2025-06-12/"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/02/sarvam-ai-roadmap-build-models-beyond-languages"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/indias-homegrown-ai-start-up-sarvam-raises-funds-at-15-billion-valuation/article69486293.ece"},
        {"name": "Livemint", "url": "https://www.livemint.com/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/51st_G7_Summit_Family_photo.jpg/1280px-51st_G7_Summit_Family_photo.jpg",
    "image_caption": "World leaders at the 51st G7 Summit in Kananaskis, Canada (2025)",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ─────────────────────────────────────────────
# Article 3: Microsoft Agent 365 / Nadella agentic AI
# ─────────────────────────────────────────────
art3_body = """Satya Nadella's Microsoft has spent two years convincing enterprises that AI copilots are worth paying for. Now it is making a harder pitch: that autonomous AI agents — software that acts on a company's behalf, not just advises — are ready for production. And the numbers from the past week suggest the market is buying.

On June 9, two of the world's largest consulting firms signed up in a single day. KPMG announced it would deploy Microsoft 365 Copilot across all 276,000 of its global employees and adopt Agent 365 — Microsoft's new control plane for AI agents — to govern how autonomous agents are built, monitored, and secured across its organisation. Microsoft designated KPMG a "Frontier Firm," a new classification for clients that are deploying agents at enterprise scale.

Hours later, Atos Group, the European IT services firm, expanded its own Microsoft partnership: 56,000 employees getting Copilot E7, plus a fleet of 19,000 AI agents managed through Agent 365. In total, more than 332,000 consultants and IT professionals at just two firms were handed AI assistants in a single business day.

## The numbers behind the push

Microsoft's latest disclosures paint a picture of a company whose AI bet is converting into revenue at an accelerating rate. Azure revenue grew 40% year over year. Copilot seats have surpassed 20 million. The company's AI annual run rate has hit $437 billion. Capital expenditure is projected to exceed $40 billion next quarter alone, with full-year 2026 spending approaching $190 billion — the vast majority earmarked for data centres and AI infrastructure.

At Build 2026, Microsoft unveiled Azure Cobalt 200, its second-generation Arm-based processor designed specifically for agentic workloads. The chip delivers 50% better performance than its predecessor, is deployed across more than 10 global regions, and is purpose-built for the Linux-based infrastructure that most AI agents run on. Microsoft also debuted Multipath Reliable Connection, an open networking protocol co-developed with AMD, Broadcom, Intel, Nvidia, and OpenAI.

The Microsoft Foundry catalog now includes both OpenAI's GPT-5.5 (generally available since June 3) and multiple Anthropic Claude models in public preview. Agent 365 itself became generally available last month at $15 per user per month, with registry sync to AWS Bedrock and Google Cloud in preview — a notable concession to multi-cloud reality.

## What "agentic AI" actually means at this scale

The distinction between a copilot and an agent matters. A copilot summarises your emails, drafts a slide, suggests code. An agent books the meeting, files the expense report, routes the customer query, and escalates when it is unsure. KPMG's deployment means AI agents will handle audit workflows, tax analysis, and client advisory tasks across 54 countries — tasks that currently employ hundreds of thousands of human professionals.

Atos's 19,000-agent fleet is not a pilot. It is a parallel workforce operating alongside 56,000 humans, each agent with identity-aware permissions managed through Microsoft Entra. The governance layer — who an agent can talk to, what data it can access, when it should stop and ask a human — is what Agent 365 is designed to enforce.

## The Indian workforce question

Microsoft employs tens of thousands of Indian-origin engineers and product managers. TCS, Infosys, and Wipro — which collectively employ over a million people, many on H-1B visas serving US clients — are all Microsoft ecosystem partners. When KPMG and Atos deploy 19,000 agents to do work that consultants currently do, the downstream effects ripple through Indian IT services firms that staff those same engagements.

For Indian tech workers in the US, the agentic AI shift is more immediate than the usual automation anxiety. The question is not whether AI will replace jobs in 2035. It is whether the consulting engagement you are staffed on today will need the same headcount next quarter.

Nadella, characteristically, frames it as augmentation. The market will decide whether it is replacement.

*Sources: Zacks, TechTimes, HR Chief Magazine, VentureBeat, Microsoft Security Blog*"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Nadella's Agent 365 Goes Live — and 332,000 Consultants Just Got AI Copilots in a Single Day",
    "subheadline": "KPMG and Atos deployed Microsoft's autonomous AI agent platform across their entire global workforces within hours of each other. The Indian IT services industry should be paying attention.",
    "slug": make_slug("microsoft-agent-365-kpmg-atos-nadella-agentic-ai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CEO Satya Nadella leads the enterprise AI agent revolution; the downstream effects on Indian IT services firms like TCS, Infosys, and Wipro — and their H-1B workforce — are immediate and material.",
    "tags": ["microsoft", "satya-nadella", "agent-365", "copilot", "enterprise-ai", "kpmg", "atos", "agentic-ai", "indian-it"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2467849/microsoft-deepens-agentic-ai-push-and-collaborations-whats-ahead"},
        {"name": "TechTimes", "url": "https://www.techtimes.com/articles/310622/20250609/kpmg-deploys-microsoft-agent-365-govern-ai-agents-across-global-firms.htm"},
        {"name": "HR Chief Magazine", "url": "https://hrchiefmagazine.com/kpmg-hands-microsoft-copilot-to-all-276000-staff/"},
        {"name": "VentureBeat", "url": "https://venturebeat.com/ai/microsofts-agent-365-shifts-ai-agents-from-sandbox-tools-to-enterprise-grade-infrastructure/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, CEO of Microsoft",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ─────────────────────────────────────────────
# Insert all articles
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
