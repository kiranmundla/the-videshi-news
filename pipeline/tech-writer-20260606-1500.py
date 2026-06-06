#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-06 15:00 UTC batch"""
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


# ── ARTICLE 1: Skyroot Aerospace ──────────────────────────────────────────

art1_body = """Skyroot Aerospace has become India's first space-technology unicorn, raising $60 million in a funding round that values the Hyderabad-based rocket maker at $1.1 billion. For the Indian diaspora, the deal's real signal is not the number but the name behind it: Ram Shriram, the man who wrote Google's founding cheque, co-led the round through Sherpalo Ventures alongside Singapore's sovereign wealth fund GIC.

BlackRock, the world's largest asset manager, also participated, as did the founders of renewable energy firm Greenko Group and the family office of Sun Pharma founder Dilip Shanghvi. The round brings Skyroot's total funding past $160 million — a figure that would have seemed fantastical for an Indian space startup five years ago.

## Two ISRO Scientists and a Rocket

Skyroot was founded in 2018 by Pawan Kumar Chandana and Naga Bharath Daka, both former scientists at the Indian Space Research Organisation. They left stable government careers to bet on a sector that barely existed: India's private space industry didn't gain legal footing until policy reforms in 2020 opened ISRO's launch sites, testing facilities, and data to commercial players.

The bet has paid off incrementally. In November 2022, Skyroot launched Vikram-S from Sriharikota — the first privately developed rocket to fly from Indian soil. It was a suborbital test, reaching about 89.5 kilometres, but the symbolism mattered. India joined a small club of nations with a functioning private launch ecosystem.

The real test comes next: Vikram-1, India's first private orbital rocket. The fresh capital will fund high-cadence Vikram-1 launches and the development of Vikram-2, a larger vehicle with an advanced cryogenic upper stage capable of placing one-tonne payloads into orbit. A KPMG valuation report projects revenue jumping from ₹100.6 crore in FY26 to ₹977 crore by FY27, with EBITDA turning positive by FY29 at ₹285 crore. The startup plans to scale its workforce from 1,163 to 5,749 employees by FY32.

## Why This Matters for NRIs

Ram Shriram's involvement connects Skyroot to the deepest veins of Silicon Valley capital. Shriram, who moved from Chennai to the United States and became an early Amazon executive before backing Google, has spent three decades identifying transformative bets. His conviction here suggests India's private space sector has moved past the science-project phase into genuine commercial territory.

For NRI investors and engineers, the timing is notable. The global space economy is projected to reach $1.8 trillion by 2035, according to McKinsey. SpaceX has demonstrated what a private launch provider can become — it's currently seeking a $1.75 trillion IPO valuation. India's advantages are familiar: deep engineering talent, lower costs, and an institutional base (ISRO) that provides the technical bedrock.

Skyroot is not alone. Agnikul Cosmos, which test-fired the world's first single-piece 3D-printed rocket engine, and Pixxel, which builds hyperspectral earth-observation satellites, are among two dozen Indian space startups that have collectively raised over $400 million. But Skyroot is the first to cross the unicorn threshold, and the calibre of its backers — Shriram, GIC, BlackRock — suggests the capital pipeline is only widening.

The question is whether India's regulatory and launch infrastructure can keep pace. ISRO's launch manifest is crowded, and Skyroot's planned high-cadence operations will require dedicated launch windows and ground support. The Telangana state government signed an MoU in January 2025 for a private rocket manufacturing and testing facility, but construction timelines remain uncertain.

For now, the numbers speak clearly enough. India's first space unicorn exists, and Google's original backer thinks it's worth over a billion dollars. That combination tends to attract attention — and capital — in ways that compound quickly."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "India's First Private Rocket Company Just Hit $1.1 Billion. Google's Original Backer Lit the Fuse.",
    "subheadline": "Skyroot Aerospace, founded by two ex-ISRO scientists, has become India's first space-tech unicorn — backed by Ram Shriram, the same investor who wrote Google's founding cheque.",
    "slug": make_slug("skyroot-aerospace-india-first-space-unicorn-ram-shriram"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Ram Shriram, one of Silicon Valley's most prominent Indian-American investors (Google's original backer), co-led the round. NRI investors now have a direct proxy for India's private space boom. The deal connects India's deeptech ecosystem to the same capital networks that built Google and SpaceX.",
    "tags": ["skyroot-aerospace", "space-tech", "indian-startup", "ram-shriram", "unicorn", "isro"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "The Indian EYE", "url": "https://theindianeye.com/skyroot-aerospace-becomes-indias-first-space-tech-unicorn/"},
        {"name": "StartupPoint", "url": "https://startuppoint.in/skyroot-aerospace-targets-977-crore-revenue-by-fy27/"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/bharat-innovates-2026-isc-lab-orbit-startup-india-satellite-economy"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/Skyroot_Aerospace"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/90/Vikram-S_rocket%27s_Mission_Prarambh_04.webp",
    "image_caption": "Skyroot's Vikram-S rocket during Mission Prarambh at Sriharikota, India's first private rocket launch",
    "image_attribution": "Wikimedia Commons",
    "is_editorial": False,
    "body": art1_body
}


# ── ARTICLE 2: GitHub Copilot Credit Pricing Shock ────────────────────────

art2_body = """On June 1, GitHub flipped a switch that every Indian developer felt immediately. The Microsoft-owned platform moved its Copilot AI coding assistant from flat-rate subscriptions to a credit-based billing model, and the backlash has been swift, vocal, and particularly acute in India — the world's second-largest developer population on the platform.

Under the old regime, a $10-per-month Pro plan bought essentially unlimited AI-assisted code completions. Under the new system, that same $10 buys 1,000 AI credits, with each request priced dynamically based on the model used, the length of the prompt, and the complexity of the response. The premium Claude Opus model, popular among professional developers, saw its token multiplier jump from 3x to 15x overnight.

## The Bills Are Already In

The sticker shock is not theoretical. Vikash Srivastava, CTO of AI infrastructure startup Vobiz, told Inc42 that his company's monthly Copilot spend — previously a predictable $500 to $700 — exhausted its entire allocation within a single week under the new model. "My consumption has increased by more than 300 percent," he said, adding that the company is now evaluating Google's Gemini and Alibaba-backed Qwen models as alternatives.

On Reddit, one developer reported burning 1,180 credits — 16 percent of a Pro+ monthly allocation — on a single debugging session that didn't even solve the problem. "For basically nothing," the user wrote. GitHub's community forums and Reddit threads are filled with similar accounts, with users announcing plans to switch to Anthropic's Claude directly, OpenAI's API, or open-source alternatives like RooCode and LM Studio.

The timing is instructive. Just this week, Microsoft announced that Infosys, TCS, and Wipro have each scaled Copilot deployments to over 100,000 employees, pushing the combined rollout past 300,000 seats. But even as Microsoft celebrates that enterprise milestone, the ground is shifting underneath it. A viral Reddit post from a developer at one of India's WITCH companies (Wipro, Infosys, TCS, Cognizant, HCL) described how management had been "pressuring and hosting multiple sessions" to push heavy Copilot usage — and then, after June 1, reversed course to urge employees to "be mindful" of model selection and reduce Opus usage.

## Why This Matters

GitHub's reasoning is straightforward: the product has evolved. What started as a simple autocomplete tool now powers agentic workflows — multi-step coding tasks where AI agents plan, execute, and iterate through entire development cycles. Running these operations costs significantly more compute than suggesting the next line of code. As GitHub's team put it, Copilot is "not the same product it was a year ago."

That argument has merit. Structurally, usage-based billing aligns costs with value delivered. But the transition has been abrupt, and the pricing opacity is the real irritant. Developers cannot easily predict how many credits a given task will consume, making budgeting difficult for individuals and nearly impossible for large engineering teams.

## The Diaspora Impact

For Indian engineers on H-1B visas at American tech companies, the shift is a minor budget headache — their employers absorb Copilot costs. For Indian startups, it is a genuine financial blow. India's startup ecosystem runs lean, and a 300 percent jump in developer tooling costs directly impacts runway.

The broader signal is harder to ignore. The era of subsidised AI — where companies like Microsoft, OpenAI, and Anthropic absorbed enormous inference costs to acquire users — appears to be ending. Anthropic has reportedly considered removing Claude Code from its Pro plan entirely. OpenAI has tightened rate limits. The AI industry is discovering what the cloud industry learned a decade ago: usage-based pricing is inevitable when compute costs are real.

For the 15 million-plus Indian developers on GitHub, the message is clear: the tools that made them more productive are about to get more expensive. The winners will be those who learn to optimise — choosing the right model for the right task, using lighter models for routine work, reserving premium compute for genuinely hard problems. The losers will be anyone who built workflows assuming infinite AI at a flat rate."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "GitHub Copilot Just Killed Flat-Rate AI Coding. Indian Developers Got the Biggest Bill.",
    "subheadline": "After June 1, the era of $10-a-month unlimited AI assistance is over. For the world's second-largest developer population, the credit crunch hits different.",
    "slug": make_slug("github-copilot-credit-pricing-indian-developers-cost-shock"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is GitHub's second-largest developer base with 15M+ users. Indian IT services firms (TCS, Infosys, Wipro) deployed 300K+ Copilot seats — now facing surprise cost spikes. Indian startups on tight budgets report 300% increases. H-1B engineers at US companies feel the ripple as teams rethink AI tooling budgets.",
    "tags": ["github-copilot", "ai-pricing", "developer-tools", "indian-tech", "microsoft", "coding"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Inc42", "url": "https://inc42.com/features/the-ai-bill-is-coming-due-githubs-copilot-move-has-startups-on-alert/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/04/github_copilot_users_threaten_exit/"},
        {"name": "Memeburn", "url": "https://memeburn.com/2026/06/github-copilot-pricing-shock-developers/"},
        {"name": "InfoWorld", "url": "https://www.infoworld.com/article/github-adds-new-copilot-features-as-usage-based-billing-takes-effect.html"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6424583/pexels-photo-6424583.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Programming code displayed on a developer's monitor — the AI tools powering this workflow just got more expensive",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art2_body
}


# ── ARTICLE 3: OpenAI / Anthropic Becoming Consultancies ──────────────────

art3_body = """In mid-May, OpenAI quietly did something more threatening to Indian IT services than any amount of AI hype: it launched a consultancy. The OpenAI Deployment Company, a joint venture with more than $4 billion in committed backing and a reported $14 billion valuation, exists for a single purpose — sending engineers into enterprises to build and deploy AI systems. Anthropic followed almost immediately, acquiring San Francisco-based Fractional AI to seed its own implementation arm.

The model both labs have adopted is borrowed directly from Palantir: Forward Deployed Engineers who embed inside client organisations, understand their data and workflows, and build bespoke AI systems on-site. Palantir pioneered this approach to sell intelligence software to governments and defence contractors. OpenAI is now using it to sell large language models to banks, pharmaceutical companies, and logistics firms.

For TCS, Infosys, Wipro, HCL, and Cognizant — the companies that collectively generate over $250 billion in annual revenue from precisely this kind of work — the implications are difficult to overstate.

## What Changed

Until recently, OpenAI and Anthropic were platform companies. They built models, published APIs, and let systems integrators handle the messy work of enterprise deployment. Indian IT services firms were natural partners in that value chain — they had the client relationships, the domain knowledge, and the armies of engineers needed to wire AI into legacy systems.

The Deployment Company changes the equation. When OpenAI acquired Tomoro, an Edinburgh-based applied-AI consultancy with approximately 150 Forward Deployed Engineers, it acquired something Indian IT firms had assumed was their moat: the last mile of implementation. Anthropic's acquisition of Fractional AI follows the same logic.

The AI labs are no longer content to sell raw compute. They want the integration margin — the lucrative, sticky business of making AI work inside specific enterprises with specific data and specific regulatory requirements. That is precisely the business model that built India's $250 billion IT services industry over three decades.

## The Indian IT Calculation

The threat is not that OpenAI replaces TCS overnight. With 614,000 employees, TCS operates at a scale that a 150-person Forward Deployed team cannot match. The threat is subtler: OpenAI captures the highest-value engagements — the $50 million AI transformation deals that shape a client's entire technology strategy — while Indian IT firms are left with lower-margin maintenance and scale-up work.

This bifurcation is already visible. Microsoft's partnership with TCS, Infosys, and Wipro for 300,000 Copilot seats is impressive at the deployment level but thin at the strategy level. Indian IT firms are scaling the tools; they are not building the tools or choosing which tools to scale. When a Fortune 500 CFO asks "how do we use AI to reshape our supply chain," the answer increasingly begins with an OpenAI or Anthropic sales call rather than an Infosys engagement letter.

The financial implications flow directly to Indian diaspora professionals. Indian IT services companies are the single largest category of H-1B visa sponsors. TCS, Infosys, and Wipro together employ tens of thousands of Indian engineers in the United States, many of whom are embedded in exactly the kind of enterprise consulting engagements that the AI labs now want to own.

## A Familiar Pattern

The pattern has precedent. Cloud computing was supposed to eliminate the need for infrastructure management — instead, it created an entirely new consulting layer. Indian IT firms successfully repositioned from on-premises support to cloud migration and management, and revenue grew.

AI could follow the same path: the technology creates new complexity, which creates new demand for implementation expertise, which Indian IT firms are well-positioned to serve. Bulls point to the 300,000 Copilot seats and the rapid scaling as evidence that Indian IT can adapt faster than sceptics assume.

But the sceptics have a stronger case this time. Cloud computing required human expertise at every layer — provisioning, security, compliance, migration. AI agents are designed to replace human expertise at every layer. When the tool itself can write code, test code, and deploy code, the value of an army of engineers who do the same shrinks. Not to zero — but enough to compress margins in an industry that already runs on single-digit operating margins.

For the Indian diaspora professional watching from Cupertino or Jersey City, the calculus is personal: the industry that sponsored your visa, trained your peers, and built the consulting model that defines Indian tech in America is now facing its most sophisticated competitor yet. Not a cheaper offshore provider. Not a rival with better client relationships. But the technology itself, packaged as a service, and priced at $14 billion."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI Just Launched a $14 Billion Consultancy. TCS and Infosys Should Be Nervous.",
    "subheadline": "With Forward Deployed Engineers and Palantir-style integration deals, the AI labs are stepping onto the territory Indian IT has owned for three decades.",
    "slug": make_slug("openai-deployment-company-threat-indian-it-services-tcs-infosys"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT services firms (TCS, Infosys, Wipro, HCL, Cognizant) are the largest H-1B sponsors. If AI labs eat the consulting layer, the model that funds Indian tech immigration is at risk. Every NRI who works at or has family at an Indian IT firm faces a strategic reshaping of their industry.",
    "tags": ["openai", "anthropic", "indian-it", "tcs", "infosys", "ai-consulting", "enterprise-ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "AI Tech Connect (Inc42 network)", "url": "https://aitechconnect.in/openai-and-anthropic-become-consultancies-the-14b-bet/"},
        {"name": "Storyboard18", "url": "https://storyboard18.com/tech-worker-flags-ai-u-turn-at-witch-firm/"},
        {"name": "PeopleMatters", "url": "https://peoplematters.in/article/ai/infosys-tcs-and-wipro-now-have-300000-employees-using-copilot-44739"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Server racks inside a modern data centre — the infrastructure powering AI labs' move into enterprise consulting",
    "image_attribution": "Pexels",
    "is_editorial": False,
    "body": art3_body
}


# ── INSERT ────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
