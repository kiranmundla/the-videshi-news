#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-01 02:00 PDT batch"""

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


# ──────────────────────────────────────────────
# ARTICLE 1: Persistent Systems / Nagarro
# ──────────────────────────────────────────────

art1_body = """\
Persistent Systems, the Pune-based mid-tier IT company that has spent years cultivating a reputation as India's most disciplined growth engine, just made the boldest bet in its three-decade history. Over the weekend, its wholly-owned subsidiary Galaxy Germany Holding launched a voluntary public takeover offer for every outstanding share of Nagarro, a Berlin-headquartered digital engineering firm, at €81 per share — a premium of roughly 100 per cent to Nagarro's undisturbed Friday close.

The market's verdict was immediate and punishing. Persistent's stock crashed 11.2 per cent on Monday to a 15-month low. Nagarro's soared 90 per cent. Between the two moves lies a €1 billion question: can an Indian mid-tier IT firm absorb a European counterpart twice its size in employee count and nearly two-thirds its revenue — and come out stronger?

## The arithmetic of ambition

The combined entity would generate roughly $2.65 billion in annual revenue, with over 46,000 employees across more than 40 countries. More importantly, it would shift Persistent's geographic centre of gravity. Europe's share of revenue would jump from a meagre 9 per cent to approximately 22 per cent, creating a genuinely balanced global footprint for the first time. Persistent CEO Sandeep Kalra has framed the deal as creating a "$2.9 billion global AI-led engineering powerhouse" and projected $5 billion in annual revenue by 2031.

Analysts are less enchanted. UBS called the valuation "excessive" given Nagarro's sluggish growth — organic revenue fell 1.1 per cent in Q1 2026, and its operating margins of 10.9 per cent trail Persistent's 15.6 per cent. Emkay flagged earnings-per-share dilution and elevated balance-sheet leverage from the €1.4 billion bridge facility needed to fund the deal. Dolat Capital warned of "immediate margin dilution."

Kalra pushed back, attributing Nagarro's recent softness to internal distractions — the firm spent much of 2025 pursuing a take-private transaction that ultimately fizzled. On a constant-currency basis, Nagarro still grew over 5 per cent, he argued.

## The insider trading shadow

Complicating matters is a suspicious pre-announcement price surge. Nagarro shares jumped nearly 20 per cent on Friday, hours before the deal was publicly disclosed. Nagarro CEO Manas Human told Reuters he expects Germany's financial watchdog BaFin to investigate. "I would be very shocked" if inside information had been exploited, Kalra said, adding that the merger team was kept deliberately small.

BaFin declined to comment specifically but confirmed it was "continuously monitoring the market for any signs of market manipulation."

## A bigger pattern

Persistent is not alone. In December, Coforge announced a $2.35 billion acquisition of California-based Encora, the largest-ever acquisition by an Indian IT services firm. Both deals signal a structural shift: India's mid-tier IT companies can no longer grow fast enough organically. AI-driven deflation is compressing delivery timelines and team sizes, making revenue growth harder to sustain without bolting on capabilities. Acquisitions are becoming the primary growth strategy — and they are getting larger.

## Why NRIs should care

For Indian-origin tech professionals in the US and Europe, the implications are direct. Persistent employs thousands of engineers on H-1B and L-1 visas. A merger of this scale typically triggers integration-driven restructuring — rationalising overlapping roles, consolidating delivery centres, and reshuffling leadership. The deal also redraws the competitive map for mid-tier IT, affecting where Indian engineers build their careers and which companies can offer the scale to win large transformation deals.

For NRI investors, Persistent's stock is now trading at a near 15-month low with a heavy debt overhang. The market is pricing in execution risk. Whether this deal creates a new global champion or a margin-dilutive anchor will depend entirely on integration — the hardest part of any acquisition and one that Indian IT companies have historically struggled with.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Persistent Just Bet €1 Billion on a German Firm It Barely Knows. The Market Thinks It Overpaid.",
    "subheadline": "India's fastest-growing mid-tier IT company launched its biggest acquisition ever — and its stock hit a 15-month low while regulators probe a suspicious price surge.",
    "slug": make_slug("persistent-nagarro-acquisition-insider-probe"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Persistent employs thousands of Indian engineers on H-1B visas in the US; the merger reshapes the mid-tier IT career landscape and affects NRI investors holding the stock at a 15-month low.",
    "tags": ["indian-it", "mergers-acquisitions", "persistent-systems", "nagarro", "europe", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/markets/deals/indias-persistent-shares-slump-after-11-billion-offer-buy-germanys-nagarro-2026-06-30/"},
        {"name": "Communications Today", "url": "https://communicationstoday.co.in/mid-tier-it-firms-turn-to-acquisitions-to-drive-growth/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/persistent-systems-shares-fall-after-1-billion-nagarro-acquisition-offer/article69764321.ece"},
        {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/persistent-eyes-5-billion-annual-revenue-by-2031-with-mega-nagarro-buyout-11751193399891.html"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/33175650/pexels-photo-33175650.jpeg",
    "image_caption": "Two business leaders shaking hands after a corporate deal",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 2: Enterprise AI Token Price War
# ──────────────────────────────────────────────

art2_body = """\
The AI industry is heading into its first real price war — and for the engineers and IT services companies that deploy these models, the economics of their daily work are about to change dramatically.

Goldman Sachs estimates that AI agent-driven token consumption will increase 24 times over the next four years, and 55 times by 2040. That is not a theoretical projection. CVS Health is already hiring an "AI Ops Engineering" director with specific expertise in "GPU cost governance." Qualcomm's CIO, Atilla Tinic, told the Wall Street Journal his company has placed hard caps on how many tokens individual engineering teams can consume. OpenText's chief digital officer said chargeback models — showing each department the dollar cost of their token usage — have cut AI spending by 20 to 30 per cent.

The corporate AI bill is becoming the new headcount budget. And companies are managing it with the same intensity.

## The open-source surge

The cost pressure is already reshaping which models companies choose. Open-source tokens processed on OpenRouter, an AI marketplace that routes queries to the cheapest capable model, jumped from 34 per cent in January to 65 per cent in June, according to a Citi research note. That is a dramatic shift in six months. China's DeepSeek and other open-weight model makers are the primary beneficiaries, winning adoption among startups and increasingly among mid-market enterprises.

Palo Alto Networks CEO Nikesh Arora — one of the most prominent Indian-origin tech executives in the US — offered a characteristically blunt take. "If you want to win enterprise, you should be forward-pricing tokens," he wrote on X, urging AI labs to charge today at the lower rates that tokens will inevitably command in a few years. It is the kind of advice that only someone who has watched enterprise pricing cycles for decades would give — and it puts OpenAI and Anthropic in an awkward position.

Both companies are reportedly considering significant price cuts. Both have also confidentially filed for IPOs. A price war immediately before a public listing is, to put it mildly, unhelpful for valuation narratives. The tension between growing revenue and retaining enterprise customers is becoming the central strategic question in frontier AI.

## When tokens cost more than developers

Gartner estimates that by 2028, the cost of running AI coding assistants will surpass the average developer's salary. That projection would have seemed absurd two years ago. It does not seem absurd now. A Bain & Company analysis found that while model prices fell roughly 50 per cent between December 2024 and December 2025, tokens consumed grew 4.5 times over the same period. The maths is simple: even with cheaper tokens, the total bill goes up when agents consume vastly more of them.

AI agents are the accelerant. Unlike a simple chatbot query, an agent completing a multi-step task can require 50 times as much computing power, Goldman Sachs analyst Jim Schneider estimates. When agents start orchestrating other agents — and they already are — token consumption compounds.

## Why this matters for Indian tech

India's IT services industry — TCS, Infosys, Wipro, HCL — is caught in the middle of this transition. These companies deploy AI models on behalf of thousands of global clients. When token costs spiral, they absorb the margin hit or pass it through. Either way, the commercial model for delivering AI-powered services is still being invented in real time.

For Indian-origin engineers in Silicon Valley and Bengaluru alike, the price war carries a personal implication. If AI coding costs surpass developer salaries, the economic logic of engineering teams changes. Companies will optimise not just for who writes the best code, but for who uses AI most cost-effectively. Token efficiency could become as important a skill as algorithmic efficiency.

And for the roughly 300,000 Indian professionals on H-1B visas at the companies deploying these models — from Google to Salesforce to Accenture — the organisational restructuring that follows an AI cost reckoning is rarely abstract. It shows up in headcount reviews, project staffing, and budget allocations. The price war is not just about OpenAI versus Anthropic. It is about the cost structure of every technology team in the world.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "AI Tokens Now Cost More Than Some Developers. Companies Are Budgeting Them Like Salaries.",
    "subheadline": "Goldman predicts a 24-fold surge in enterprise AI token consumption. Companies are capping usage, and a price war between OpenAI and Anthropic is reshaping how every tech team spends.",
    "slug": make_slug("ai-token-price-war-enterprise-costs-indian-tech"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT services companies deploy AI models for global clients and face margin pressure as token costs spike; Indian engineers on H-1B visas at tech companies will be directly affected by AI cost restructuring.",
    "tags": ["ai", "enterprise-ai", "openai", "anthropic", "indian-it", "silicon-valley", "nikesh-arora"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/cio-journal/how-companies-are-managing-ai-token-spend-833b6f7e"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/cheaper-ai-is-better-soaring-bills-are-reshaping-how-businesses-choose-models-2026-06-29/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/openais-reported-ipo-delay-is-the-latest-complication-for-tech-stocks-97a5cef1"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg",
    "image_caption": "Server racks in a data center powering enterprise AI workloads",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ──────────────────────────────────────────────
# ARTICLE 3: RBI AI Risk Management Guidelines
# ──────────────────────────────────────────────

art3_body = """\
India's central bank has quietly issued what may be the most consequential set of rules for the country's banking sector since its data localisation mandate in 2018. Draft guidelines released on 25 June require every bank in India to treat artificial intelligence models with the same rigour they apply to financial risk models — board-approved policies, independent validation, model inventories, human oversight, and the power to decommission any AI system that poses excessive risk.

The Reserve Bank of India is not experimenting. It is building a regulatory architecture for a financial system that is already deeply AI-dependent — and it wants comments by 24 July.

## What the rules demand

The draft framework is precise. Banks must establish a board-approved risk management framework covering all AI and machine-learning models, whether built in-house or procured from third parties. Every model must be logged in a central inventory. Risk assessment must happen at both the individual model level and across the enterprise, on an ongoing basis.

If any model's risks are found to be excessive, corrective action must be taken — enhanced controls, restrictions on use, remediation, or outright decommissioning — with a report submitted to the board's risk management committee. For generative AI models that interact with customers or external users, additional cybersecurity controls are mandatory.

Crucially, all models — including those from third-party vendors such as OpenAI, Google, or Anthropic — must undergo independent validation. In an era when banks are rushing to integrate frontier AI into everything from credit assessments to fraud detection to customer service chatbots, that requirement alone could slow adoption significantly.

## The broader context

The RBI has been building toward this moment. In August 2025, an eight-member committee chaired by IIT Bombay's Professor Pushpak Bhattacharyya released the Framework for Responsible and Ethical Enablement of Artificial Intelligence (FREE-AI). That framework recommended indigenous AI model development, AI innovation sandboxes, and audit mechanisms for the financial sector. It also flagged the growing reliance on third-party AI providers, recommending AI-specific contractual safeguards around bias, accountability, and data use.

The June draft guidelines operationalise many of those recommendations. They move from principles to mandates — from "should consider" to "must comply."

Separately, the RBI has been in talks with global regulators and banks to review the risks posed by Anthropic's advanced Mythos and Claude models, which are being deployed by some international banks with Indian operations. The central bank is preparing broader guidelines for enterprise partnerships with frontier AI models, insisting that all analytics based on Indian customer data comply with domestic data localisation rules.

## The fintech impact

India's fintech ecosystem — one of the most dynamic in the world, built on the UPI payments backbone that now processes over 14 billion transactions a month — will feel these rules acutely. Companies like PhonePe, Razorpay, and CRED use AI models for credit scoring, fraud detection, and personalised financial recommendations. Requiring independent validation of every third-party model introduces cost and friction into a sector that has thrived on speed.

For NRI investors, the stakes are substantial. HDFC Bank, ICICI Bank, SBI, and Kotak Mahindra — staples of every India-focused equity portfolio — are among the heaviest AI adopters in Indian banking. Their compliance costs will rise. Their pace of AI-driven product innovation may slow. But the regulatory clarity could also reduce tail risks, making Indian banks more attractive to institutional investors who have been wary of ungoverned AI deployment in emerging markets.

## What NRI fintech founders need to know

For Indian-origin fintech founders — whether building in Bengaluru, Singapore, or the Bay Area — the message is plain. If your product touches Indian banking rails, your AI models are now subject to RBI oversight. Third-party model validation, board-level governance, and customer-facing AI cybersecurity controls are not optional. The July 24 deadline for feedback is the window to shape how these rules are implemented.

India is not banning AI in finance. It is insisting that AI in finance be treated like finance — regulated, audited, and accountable. Whether that discipline accelerates trust or decelerates innovation will depend on how the final rules land.
"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Told Its Banks to Treat Every AI Model Like a Risk Model. The Rules Are Sweeping.",
    "subheadline": "The RBI's draft guidelines mandate board-approved AI policies, independent model validation, and human oversight — reshaping how HDFC, ICICI, and every fintech in the country deploys artificial intelligence.",
    "slug": make_slug("rbi-ai-risk-management-guidelines-banks-fintech"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors in Indian bank stocks face rising compliance costs; Indian-origin fintech founders building products on Indian banking rails must now comply with AI model governance mandates.",
    "tags": ["ai-regulation", "rbi", "indian-fintech", "banking", "ai-governance", "nri-investors"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/rbi-proposes-guidelines-banks-manage-ai-risks-2026-06-25/"},
        {"name": "Law.asia", "url": "https://law.asia/rbi-free-ai-framework/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-central-bank-talks-with-global-regulators-banks-review-mythos-risks-2026-04-23/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Mumbai%2C_reserve_bank_of_india_02.jpg/1280px-Mumbai%2C_reserve_bank_of_india_02.jpg",
    "image_caption": "The Reserve Bank of India headquarters building in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}


# ──────────────────────────────────────────────
# Insert all articles
# ──────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
