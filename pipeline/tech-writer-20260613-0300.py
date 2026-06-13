#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-13 03:00 UTC batch"""

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
    return slug[:70].rstrip('-') + "-20260613"

# ─────────────────────────────────────────────────────
# ARTICLE 1: Anthropic Fable 5 / Mythos 5 Export Ban
# ─────────────────────────────────────────────────────

art1_body = """The Trump administration has taken the most aggressive step yet in controlling the flow of frontier AI technology. On Friday evening, Commerce Secretary Howard Lutnick sent a letter to Anthropic CEO Dario Amodei placing the company's two most powerful models — Fable 5 and Mythos 5 — under export controls. No foreign government, company, or individual may use them. Foreign nationals inside the United States are also barred.

The scope is extraordinary. Because many of Anthropic's own employees are foreign-born, the company had to shut off access to the two models for *everyone* while it works out compliance. Other Anthropic products, including earlier Claude models, remain available.

## What Triggered the Ban

The Commerce Department acted after another company claimed it had found a method to jailbreak Mythos, the cybersecurity-focused model that governments and critical-infrastructure firms have been using to patch software vulnerabilities. Anthropic called the claim overblown. "We reviewed a demonstration of this specific technique being used to identify a small number of previously known, minor vulnerabilities," the company said in a statement posted within hours of the letter. "These vulnerabilities all appear relatively simple, and we have found that other publicly-available models are able to discover them as well without requiring a bypass."

The move caps a months-long feud between the Trump administration and Anthropic. In February, the Pentagon labelled the company a "supply-chain risk" after it refused to let the military use Claude for mass domestic surveillance and fully autonomous weapons. That designation is being challenged in court. Yet relations had recently shown signs of thawing as Anthropic prepares for a highly anticipated initial public offering.

## Why Indian Tech Should Be Watching

The immediate blast radius extends well beyond Silicon Valley. Tata Consultancy Services announced just days ago that it is deploying Claude across 50,000 employees as part of a new AI business unit. How much of that deployment depends on Fable 5 or Mythos 5 is unclear, but the signal is unmistakable: Indian IT services companies that have hitched their AI strategies to Anthropic now face a regulatory variable they did not price in.

Then there is the workforce angle. Anthropic employs hundreds of engineers on H-1B and other work visas. Under the letter's language, any foreign national — even one sitting in Anthropic's San Francisco headquarters — is prohibited from accessing the restricted models. For Indian engineers who make up a significant share of Silicon Valley's AI workforce, this introduces a strange new hierarchy: you can build the model, but you cannot use it.

India's own enterprise customers are also exposed. Companies in banking, energy, and IT services had begun using Mythos to identify and patch software vulnerabilities — a use case that is now paused indefinitely. The timing is awkward. India's IT minister Ashwini Vaishnaw said just this week that India's digital laws were not built for AI and that new regulation is coming. Washington's unilateral action underscores how little say even major markets have when frontier models are controlled at the source.

## The Bigger Picture

This is the first time the U.S. government has imposed export controls on a specific set of AI models produced by an American company. The precedent it sets is broader than Anthropic. If the Commerce Department can shut off access to Fable 5 on a Friday evening with a single letter, every frontier AI developer — OpenAI, Google DeepMind, Meta — now operates under the implicit threat that their best work could be classified overnight.

For NRI investors tracking Anthropic's IPO trajectory, the calculus just shifted. The company was reportedly approaching profitability and eyeing a public listing later this year. An export control that bans your most capable products from the global market is not the kind of story you want in your S-1.

For the Indian diaspora in tech, the message is more personal. The AI tools they build, sell, and depend on are now subject to a national security apparatus that can move faster than any corporate compliance team. Friday's letter will not be the last."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The US Just Blocked Foreigners From Anthropic's Best AI. Indian Engineers Are in the Crossfire.",
    "subheadline": "Commerce Secretary Lutnick's export ban on Fable 5 and Mythos 5 hits Anthropic's foreign-born workforce, TCS's new Claude deployment, and every Indian company that was using these models to patch vulnerabilities.",
    "slug": make_slug("us-blocks-anthropic-fable-mythos-export-ban-india"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian engineers at Anthropic are barred from using the models they helped build, TCS's 50,000-employee Claude deployment faces regulatory uncertainty, and Indian enterprise customers lose access to critical cybersecurity tools.",
    "tags": ["anthropic", "fable-5", "export-controls", "indian-tech", "ai-regulation", "tcs"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/anthropic-halts-access-to-top-ai-models-after-u-s-ban-on-foreign-use-69f33375"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/us-blocks-foreign-access-anthropics-most-advanced-ai-models-axios-reports-2025-06-12/"},
        {"name": "Anthropic Official Statement", "url": "https://www.anthropic.com/news/statement-on-the-us-government-directive-to-suspend-access-to-fable-5-and-mythos-5"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Anthropic CEO Dario Amodei at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─────────────────────────────────────────────────────
# ARTICLE 2: GitHub Copilot Metered Billing
# ─────────────────────────────────────────────────────

art2_body = """On June 1, Microsoft's GitHub flipped a switch that turned its most popular AI coding assistant from a flat-rate subscription into a metered service. Within hours, developers began posting screenshots of projected monthly bills that had ballooned from $29 to $750 — and in some cases, to more than $3,000. The GitHub discussion thread announcing the change accumulated over 900 downvotes in its first week.

The backlash is loud, messy, and entirely predictable. And it matters to Indian tech workers more than most.

## How the New Pricing Works

Under the old model, GitHub Copilot Pro cost $10 per month and Pro+ cost $39, each offering a fixed pool of requests regardless of complexity. The new system replaces requests with AI Credits, where one credit equals one cent of compute usage. Pro users get 1,500 credits per month, Pro+ gets 7,000, and the new Max tier — at $100 per month — gets 20,000.

The catch is that credit consumption varies wildly depending on which AI model a developer selects, how much code context they feed it, and how complex the response is. A developer who used Copilot for a single feature refactoring request reported burning through $6 in credits — not after a day of usage, but after one prompt.

GitHub says overages only kick in if users explicitly set an additional spending budget. Leave that at zero, and Copilot simply stops working when credits run out. The result is a productivity cliff: mid-sprint, mid-feature, your AI assistant goes dark until the calendar flips.

## The Industry Is Moving in Lockstep

GitHub is not alone. Cursor, Windsurf, and the Anthropic API all adjusted pricing within weeks. Claude Fable 5, which became available inside Copilot on June 9, lists at $10 per million input tokens and $50 per million output tokens — double the rate of the previous generation. Google's persistent AI agent runs $100 per month. The all-you-can-eat era of AI tooling is definitively over.

https://www.instagram.com/reel/DZFTOFXkjg0/

## Why This Hits India Hardest

India has one of the largest developer populations on GitHub, and Indian IT services companies — TCS, Infosys, Wipro, HCL Tech, Cognizant — have been rolling out Copilot to tens of thousands of engineers as a competitive differentiator. For these firms, where margins are already under pressure from AI-driven automation, the shift from predictable licensing to usage-based billing introduces a cost variable that is hard to model and harder to cap.

The math is blunt. A team of 500 developers on Pro+ was paying $19,500 per month. Under metered billing, if each developer burns through credits at the rates being reported, that same team could face six-figure monthly bills — or lose access to their AI tools partway through each billing cycle.

Indian freelance developers and startup engineers face a different version of the same problem. Many relied on Copilot's flat rate as an equaliser — a $10-per-month tool that put a solo developer in Bengaluru on roughly the same footing as a team at a San Francisco startup. Metered billing tilts that back. Developers who use AI heavily, particularly for the agentic multi-step workflows that GitHub has been aggressively promoting, will pay dramatically more.

## The Irony of Satya Nadella's Microsoft

There is a particular sting for the Indian tech diaspora in watching Satya Nadella's Microsoft make this move. Nadella built his reputation on the idea that Microsoft's tools should be accessible and developer-friendly. "Democratising AI" was the pitch. Usage-based billing that can turn a $29 subscription into a $750 invoice is a different kind of democracy.

The counterargument — and it has some merit — is that the flat-rate model was always a subsidy. Heavy users were being cross-subsidised by light ones, and as Copilot's capabilities grew, the economics became unsustainable. Microsoft is not wrong that running frontier AI models costs real money per token. But the transition has been handled with all the grace of a surprise toll booth on a highway that was free yesterday.

For Indian developers who built their workflows around Copilot's predictability, the adjustment period will be measured in cancelled subscriptions, budget renegotiations, and a quiet migration to open-source alternatives that never send a bill."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "GitHub Copilot's $29 Bill Just Became $750 — and India's Developer Army Is Doing the Maths",
    "subheadline": "Microsoft's switch to metered AI billing has sparked a developer revolt. For Indian IT firms deploying Copilot at scale, the cost implications are staggering.",
    "slug": make_slug("github-copilot-metered-billing-india-developers"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian IT services companies deploying Copilot to tens of thousands of engineers face unpredictable costs, while Indian freelance developers lose the flat-rate equaliser that put them on par with Silicon Valley teams.",
    "tags": ["github", "copilot", "microsoft", "satya-nadella", "indian-developers", "ai-pricing"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/01/what-a-joke-github-copilots-new-token-based-billing-spurs-consternation-among-devs/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/06/03/github_copilot_billing/"},
        {"name": "TechSpot", "url": "https://www.techspot.com/news/108200-github-switched-copilot-metered-billing-developers-watching-months.html"},
        {"name": "Developer-Tech", "url": "https://developer-tech.com/news/the-flat-rate-era-of-ai-coding-tools-is-over/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6424583/pexels-photo-6424583.jpeg",
    "image_caption": "Programming code displayed on a computer monitor",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ─────────────────────────────────────────────────────
# ARTICLE 3: Pine Labs P3P Agentic Payment Protocol
# ─────────────────────────────────────────────────────

art3_body = """India's Unified Payments Interface was built for humans. You open an app, enter an amount, type your MPIN, and the money moves. It is fast, free, and absurdly successful — processing over 16 billion transactions a month. But it has a problem that nobody thought about when it was designed: what happens when the buyer is not a person but an AI agent?

Pine Labs thinks it has the answer. This week, the Noida-headquartered fintech company launched the Pine Labs Payment Protocol, or P3P — what it calls India's first agentic payment infrastructure built on top of UPI. The protocol is already live in production, and it could quietly reshape how India's digital economy handles the next generation of AI-powered commerce.

## How P3P Works

The core idea is simple. Today, every UPI transaction requires a human to authenticate it — tap the app, confirm the amount, enter the PIN. That works when you are buying coffee. It breaks when an AI agent is supposed to monitor gold prices around the clock and buy ₹500 worth the moment the rate drops below ₹16,000 per gram.

P3P solves this by extending UPI's existing mandate framework. Users set up a one-time authorisation that defines what an AI agent is allowed to do: spending limits, transaction types, specific merchants, price thresholds. Once approved, the agent operates autonomously within those bounds. No MPIN required for each transaction. No human in the loop for every purchase.

Pine Labs has partnered with Grantex, a delegated-authorisation startup, to handle identity verification, spending controls, and audit trails. The protocol uses HTTP 402, an obscure but increasingly important web standard for machine-readable payment requests that allows AI agents to negotiate and settle payments with each other programmatically.

"In India, UPI's mandate framework was already architected for agentic commerce," Pine Labs CEO Amrish Rau said. "P3P is that layer."

## Who Is Using It

The first commercial deployment is with Gullak, a digital gold savings platform. Users can set a rule — buy ₹500 of gold if the price drops below a threshold — and Gullak's AI agent executes the purchase automatically when the condition is met. No notification, no approval screen, no missed opportunity because you were asleep or at work.

Vijay Sales, the electronics retail chain with more than 150 stores, is running a proof-of-concept deployment. The use case there: letting customers set price-based buying rules for smartphones or appliances. When the price hits their target, the agent buys it.

Pine Labs is also in conversations with companies across travel, fintech, and quick commerce. The protocol is currently restricted to UPI rails but the company is working with card networks to extend it to card-based transactions.

## Why NRIs Should Care

For the Indian diaspora, P3P is significant for two reasons. First, it is another signal that India's payments infrastructure is pulling ahead of the rest of the world in ways that matter. UPI already processes more real-time transactions than any other system on the planet. Adding an agentic layer on top of it positions India as the first major economy to build native payment rails for AI commerce.

Second, UPI is going international. It already works in Nepal, Singapore, the UAE, Sri Lanka, Bhutan, and France. If P3P becomes standard on UPI's domestic rails, it is only a matter of time before it follows UPI abroad — giving NRIs the ability to set up automated investment or remittance rules that execute through the same familiar system they already use to send money home.

For NRI investors tracking India's fintech landscape, Pine Labs itself is worth watching. Listed on the NSE, the company's stock jumped 3.7 per cent on the day of the P3P announcement. In a market where fintech valuations have been under pressure, the ability to claim a foundational layer of AI commerce infrastructure is a meaningful differentiator.

The bigger question is whether India's regulators will move as fast as its engineers. The Reserve Bank of India has been cautious about automated payments, and expanding mandate limits for AI agents will require both regulatory clarity and consumer trust. But if P3P works — and the early deployments suggest it does — India may have just built the plumbing that every country's AI commerce will eventually need."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Pine Labs Just Taught AI Agents to Spend Money Through UPI — and It Is Already Live",
    "subheadline": "India's first agentic payment protocol lets AI systems buy digital gold, electronics, and more without human authentication. The implications for India's payment infrastructure are enormous.",
    "slug": make_slug("pine-labs-p3p-agentic-payment-upi-ai-commerce"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "India's UPI is going international and P3P positions it as the first major economy with native AI payment rails — NRIs could eventually use the same system for automated remittances and investments back home.",
    "tags": ["pine-labs", "upi", "fintech", "agentic-ai", "india-payments", "digital-commerce"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Gadgets 360", "url": "https://www.gadgets360.com/ai/news/pine-labs-p3p-agentic-payment-protocol-upi-india-8286901"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/pine-labs-ai-powered-payments-protocol-upi-transactions"},
        {"name": "Fintech Singapore", "url": "https://fintechnews.sg/114207/india/pine-labs-brings-ai-agent-payments-to-indias-upi/"},
        {"name": "AInvest", "url": "https://www.ainvest.com/news/ai-agent-can-make-upi-payments-at-your-target-price-2506129093/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4226272/pexels-photo-4226272.jpeg",
    "image_caption": "A contactless smartphone payment at a terminal",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ─────────────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
