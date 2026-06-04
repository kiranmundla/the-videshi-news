#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-04 12:00 UTC run"""
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
# ARTICLE 1: Anthropic Claude Mythos / India
# ─────────────────────────────────────────────

article1_body = """India is now among 15 countries granted access to Claude Mythos Preview, Anthropic's most powerful AI model built specifically to find and exploit cybersecurity vulnerabilities. The expansion, announced on Tuesday under the company's Project Glasswing initiative, brings 150 new organisations into a programme that was previously restricted to about 50 partners in the United States and United Kingdom.

The implications for India's digital infrastructure are significant. The organisations gaining access operate across critical sectors — financial services, healthcare, telecommunications, power grids, and water systems. In a country that processes more than 14 billion UPI transactions a month and runs Aadhaar-linked systems touching 1.4 billion citizens, the attack surface is enormous.

## What Mythos Actually Does

Claude Mythos is not a chatbot. It is a frontier AI model that Anthropic itself initially deemed too dangerous to release broadly. In testing, the model demonstrated an ability to rapidly surface thousands of zero-day vulnerabilities — the kind of software flaws that attackers can exploit before developers even know they exist.

The early results from Project Glasswing's first 50 partners are striking. Within weeks, they identified over 10,000 high and critical-severity vulnerabilities across their codebases. For context, that is more than what most enterprise security teams find in a year using conventional scanning tools.

"For most partners, we estimate that a major attack could affect more than 100 million people, with important ramifications for both global and national security," Anthropic wrote in its announcement.

The expanded cohort includes companies such as Okta, Samsung, SK Hynix, SK Telecom, and financial infrastructure giants Euroclear, Intercontinental Exchange, and SWIFT. NATO and the European Union's cybersecurity agency ENISA have also been granted access, according to the Financial Times.

## The India Context

India's inclusion arrives at a particularly tense moment. Finance Minister Nirmala Sitharaman recently warned banks and financial institutions about imminent cybersecurity threats from AI models like Mythos. Market regulator SEBI has announced a new task force called Cyber Suraksha AI to examine the risks these frontier models pose to financial markets.

Anthropic confirmed to multiple Indian outlets that both public and private organisations in India have received access, though specific names remain confidential for security reasons. The access is tightly controlled, focused on entities defending critical infrastructure across finance, healthcare, communications, and national security.

This is not Anthropic's only play in India. The company has been building its Indian presence methodically. India is now Claude's second-largest market globally, contributing 7.2 per cent of worldwide usage — with coding tasks accounting for half of that activity, well above the global average of 33 per cent. Anthropic appointed former Microsoft India executive Irina Ghose to lead India operations earlier this year, brought on Amlan Mohanty for policy, and most recently hired Sangeeta Bavi — formerly COO of YourStory and a veteran of Microsoft's startup ecosystem — to run startups and growth. A Bengaluru office is in the works.

## Why NRIs Should Care

For Indian cybersecurity professionals working in the US — and there are tens of thousands of them at firms like Palo Alto Networks, CrowdStrike, and the Big Four consulting firms — Mythos represents both an opportunity and a disruption. The model can do in minutes what entire penetration testing teams take weeks to accomplish. The professionals who learn to work alongside these tools will be indispensable. Those who do not may find their roles automated faster than they expected.

For NRI investors tracking Anthropic's trajectory, the timing is also notable. The Glasswing expansion came one day after Anthropic filed confidentially for an IPO at a valuation approaching a trillion dollars, following a $65 billion funding round. The company is no longer a research lab with ambitions. It is a business with India as a core growth market.

Anthropic warned that AI models with Mythos-level capabilities could become widely available within six to twelve months. The race is not to build the best vulnerability finder. It is to find the vulnerabilities first."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic Just Gave India Access to Its Most Dangerous AI. Only 150 Organisations Made the Cut.",
    "subheadline": "Claude Mythos can find thousands of zero-day vulnerabilities in weeks. India's banks, power grids, and Aadhaar-linked systems are now in its crosshairs — as both targets and beneficiaries.",
    "slug": make_slug("anthropic-claude-mythos-india-project-glasswing"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian cybersecurity professionals in the US face both opportunity and disruption as Mythos automates penetration testing. NRI investors should note Anthropic's IPO trajectory with India as its second-largest market.",
    "tags": ["anthropic", "cybersecurity", "claude-mythos", "india-ai", "project-glasswing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/03/anthropic-scales-claude-mythos-to-critical-infrastructure-in-15-countries/"},
        {"name": "Inc42", "url": "https://inc42.com/buzz/india-gets-access-to-anthropics-mythos-under-project-glasswing/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/india-gets-access-to-claude-mythos-ai-model/article69637241.ece"},
        {"name": "Digit.in", "url": "https://www.digit.in/news/general/anthropic-expands-claude-mythos-cybersecurity-initiative-across-15-countries-includes-india.html"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Anthropic CEO Dario Amodei at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Meta Business AI Agent / WhatsApp
# ─────────────────────────────────────────────

article2_body = """Meta just made its most aggressive move yet into enterprise AI, and it is betting on the one app that already runs Indian commerce: WhatsApp.

At its Conversations conference in London on Wednesday, Meta unveiled a new AI-powered Business Agent that can do more than answer questions. It can book calendar appointments, qualify sales leads, process payments, place orders, and escalate complex queries to human staff — all within WhatsApp, Messenger, and, for the first time, Instagram.

This is not a chatbot with canned responses. Meta is calling it "agentic AI," a system that takes actions on behalf of businesses rather than simply surfacing information.

## From Chat to Commerce Engine

"We actually want to take actions now. We actually want it to be able to complete the payment, to process the booking, to place the order," said Naomi Gleit, Meta's head of product, in a Reuters interview. She drew a sharp line between the new agent and the "rule-based automations" that powered earlier WhatsApp bots.

The numbers behind the launch are substantial. More than one million businesses already use earlier chatbot versions on WhatsApp and Messenger. The new Business Agent upgrades their capabilities from scripted responses to autonomous task execution.

Businesses will initially get the tool for free. Paid subscription tiers are planned for the coming months — a pricing strategy that mirrors how Meta monetised business tools on Facebook and Instagram before.

Alongside the in-app agent, Meta is also launching a Business Agent Platform that gives companies the infrastructure to build custom AI agents for operations beyond Meta's own apps. This is a clear signal that Meta views itself not just as a social media company, but as an enterprise AI platform.

## India Is the Obvious Battleground

No market in the world is more primed for this than India. WhatsApp has over 500 million users in the country. For millions of small businesses — from kirana stores in Hyderabad to jewellers in Surat to immigration consultants in Chandigarh — WhatsApp is not just a messaging app. It is their storefront, their customer relationship management tool, and their payment channel.

The JioMart-WhatsApp integration already demonstrated the model: customers browse catalogues, place orders, and pay without leaving the chat. Meta's new Business Agent extends this from structured catalogue shopping to freeform AI-driven interactions. A customer could message a restaurant, describe dietary preferences, get a personalised menu recommendation, and book a table — all handled by the agent.

For NRI entrepreneurs who run businesses in India remotely — and there are thousands of them, from e-commerce brands to real estate consultancies — this changes the economics of customer service. A single AI agent handling first-contact queries on WhatsApp could replace two or three customer service representatives, operating around the clock across time zones.

## The Competitive Landscape

Meta is not alone in this space. Google has been pushing Business Messages through its Maps and Search surfaces. Salesforce has been embedding AI agents into its CRM. But Meta has something neither competitor can match: distribution. WhatsApp is already where Indian customers are. There is no adoption barrier, no app download, no login flow. The agent lives inside a conversation the customer was already having.

The enterprise AI market is projected to exceed $300 billion by 2028. Meta's entry — backed by its Llama AI models and the massive infrastructure behind WhatsApp — puts it in direct competition with Salesforce, Microsoft, and Google for the small and mid-market segment that has historically been underserved by enterprise software.

For India's IT services companies — Infosys, TCS, Wipro — this is both a threat and an opportunity. The threat is obvious: if businesses can deploy AI agents through WhatsApp with a few clicks, the demand for custom chatbot development shrinks. The opportunity lies in building custom integrations, training, and enterprise deployment on top of Meta's platform.

## What Comes Next

Meta has not disclosed specific pricing for the paid tiers or a timeline for the India rollout, though the global launch was confirmed. The Muse Spark API — Meta's flagship AI model API — continues to face delays, with no scheduled launch date as of this week. But the Business Agent operates on existing Meta AI infrastructure, meaning the delay does not affect its deployment.

For Indian businesses already living on WhatsApp, the question is not whether to adopt this tool. It is how quickly they can configure it before their competitors do."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Just Turned WhatsApp Into an AI Sales Agent. India's Small Businesses Are First in Line.",
    "subheadline": "The new Business Agent can book appointments, process payments, and close sales inside WhatsApp. With 500 million Indian users, Meta is betting that enterprise AI starts in a chat window.",
    "slug": make_slug("meta-whatsapp-business-ai-agent-india-enterprise"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI entrepreneurs running Indian businesses remotely can replace customer service teams with Meta's AI agent. Indian IT services firms face disrupted chatbot demand but new integration opportunities.",
    "tags": ["meta", "whatsapp", "enterprise-ai", "india-business", "ai-agents"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-enters-enterprise-ai-race-with-new-business-agent-2026-06-04/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-repeatedly-pushes-back-new-ai-model-release-developers-wsj-says-2026-06-04/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/meta-muse-spark-api-delay-2026/"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
    "image_caption": "Meta CEO Mark Zuckerberg, whose company is pushing AI agents into WhatsApp commerce",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 3: Microsoft Build 2026 / MAI models
# ─────────────────────────────────────────────

article3_body = """Satya Nadella stood on stage at Microsoft Build in San Francisco on Tuesday and did something he has been avoiding for years: he showed the world Microsoft's own AI models.

Not OpenAI's models. Not a rebadged GPT. Microsoft's own in-house creations, built from scratch by the company's AI Superintelligence Team. The message was unmistakable. After spending billions on its partnership with OpenAI, Microsoft is hedging its bets — and building its own arsenal.

## The MAI Family

The headline model is MAI-Thinking-1, Microsoft's first reasoning model. At 35 billion active parameters, it is deliberately mid-sized — designed for efficiency and low token costs rather than raw scale. Microsoft emphasised that it was built on clean data without distillation from third-party frontier models. That last detail matters: it means Microsoft can deploy this model without any dependency on OpenAI's intellectual property.

MAI-Thinking-1 is engineered for complex multi-step instructions, long-context reasoning, and code generation — the exact capabilities that Indian IT services companies rely on when building enterprise applications for clients.

But the reasoning model was just one of several announcements. MAI-Image-2.5 handles both text-to-image and image-to-image workloads. MAI-Code-1-Flash is purpose-built for GitHub Copilot and VS Code, designed to deliver faster completions at lower cost. MAI-Voice-2 now supports more than ten additional languages. MAI-Transcribe-1.5 adds entity biasing for more accurate speech-to-text. All image, transcription, and voice models are generally available on Microsoft Foundry and the MAI Playground.

## The Hardware Play

Alongside the software, Nadella unveiled the Surface RTX Spark Dev Box, a developer workstation powered by an Nvidia chip capable of running a 120-billion-parameter AI model locally — something most PCs cannot do. "This is a dream machine," Nadella said, adding that he had put himself on the waitlist.

The Dev Box is priced to compete with Apple's premium offerings, a direct assault on the MacBook Pro's dominance among developers. For the tens of thousands of Indian engineers working at Microsoft, Amazon, and Google in the US, the machine is designed to let them run large AI models on their desks rather than burning cloud compute credits.

Microsoft also showcased OpenClaw, an open-source software tool that can direct groups of AI agents to carry out everyday tasks. The tool has already gained popularity in China and has helped rival Apple sell Mac computers — a detail that Microsoft is now trying to turn to its own advantage by making OpenClaw work better on Windows.

## What This Means for Indian IT

The implications for India's $250 billion IT services industry are layered. On one hand, Microsoft's in-house models create a new dependency. If Indian IT firms have been building their AI practices around OpenAI's GPT family through Microsoft's Azure, they now have to contend with a parallel model ecosystem. Clients will ask which model is cheaper, which is faster, which is more appropriate for their use case. The answer will increasingly be one of Microsoft's own.

On the other hand, the move creates opportunity. MAI-Code-1-Flash inside GitHub Copilot directly affects the productivity of Indian developers, who make up one of the largest national cohorts on GitHub. Faster, cheaper code completions mean more output per developer-hour — a metric that every Indian IT services company tracks obsessively.

The language and voice models are particularly relevant for India. MAI-Voice-2's expansion to new languages could include Hindi and other Indic languages, though Microsoft has not confirmed the specific additions. If it does, the impact on voice-first applications in India — from customer service bots to government service portals — would be substantial.

## The Strategic Calculus

Microsoft's relationship with OpenAI has always been complicated. Microsoft invested $13 billion. It got Azure as the exclusive cloud provider for OpenAI's models and early access to every new release. But OpenAI has been pushing for more independence — exploring deals with Oracle, launching its own consumer products, and now competing directly with Microsoft in code generation through Codex.

The MAI models are Nadella's insurance policy. If the OpenAI relationship frays further, Microsoft now has its own reasoning, code, image, and voice models to fall back on. The Surface RTX Spark Dev Box ensures the hardware exists to run them locally.

For the Indian technology ecosystem — from the developers building on Azure to the IT services firms selling Microsoft solutions to the startups in Bengaluru building on GitHub Copilot — the message is clear. Microsoft is no longer just a platform for other companies' AI. It is becoming an AI company in its own right. Nadella, the Hyderabad-born engineer who took over a company in decline and turned it into a $3 trillion juggernaut, is now doing what he does best: playing both sides of a disruption until one of them wins."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Satya Nadella Just Revealed Microsoft's Own AI Models. The OpenAI Safety Net Is Fraying.",
    "subheadline": "MAI-Thinking-1, a reasoning model built without OpenAI's help, headlines Microsoft Build 2026. For Indian IT, the implications are profound.",
    "slug": make_slug("satya-nadella-microsoft-build-mai-models-openai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CEO Satya Nadella's strategic hedge affects the entire Indian IT ecosystem — from developers on GitHub Copilot to services firms building on Azure to startups in Bengaluru.",
    "tags": ["microsoft", "satya-nadella", "mai-models", "microsoft-build", "indian-tech-leaders", "ai-models"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-showcases-new-pc-cloud-ai-tools-developer-conference-2026-06-03/"},
        {"name": "Microsoft Blog", "url": "https://news.microsoft.com/build-2026/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/alphabet-stock-deal-big-tech-ai-offerings-2026/"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Microsoft CEO Satya Nadella at a company event",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body.strip()
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
