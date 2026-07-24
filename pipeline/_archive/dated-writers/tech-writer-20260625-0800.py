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
        "headline": "India Won't Ban Crypto. It Just Made Sure It Can See Every Trade Over $10,000.",
        "subheadline": "A new reporting order for over-the-counter deals, plus fresh Travel Rule pop-ups on Binance, signal the government's real crypto policy: tolerate it, tax it, and trace it.",
        "slug": make_slug("india-crypto-aml-otc-10000-binance-travel-rule-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRIs who move money between Indian and US wallets, or hold Indian-exchange accounts from abroad, now face name-and-PAN disclosure on transfers — a compliance headache that turns cross-border crypto into a paper trail.",
        "tags": ["crypto", "india-tech", "fintech", "regulation", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CoinCentral", "url": "https://coincentral.com/india-tightens-aml-scrutiny-on-crypto-transactions-above-10000/"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/binance-tightens-reporting-rules-for-p2p-crypto-transactions-in-india/"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/crypto/crypto-exchange-binance-tightens-crypto-rules-for-indian-users"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7267491/pexels-photo-7267491.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A stack of Bitcoin tokens, the asset class India is choosing to surveil rather than ban.",
        "image_attribution": "Pexels",
        "body": """India's crypto policy has always been easier to describe by what it is not. It is not a ban. It is not, despite years of speculation, a green light. This week the contours of what it actually *is* came into sharper focus — and the answer is surveillance.

India's Financial Intelligence Unit (FIU-IND) has instructed registered crypto exchanges to report every over-the-counter trade above $10,000, roughly ₹9.44 lakh. OTC desks — the back channels where large buyers and sellers transact away from the public order book — must now collect ownership records, funding evidence, the stated reason for a transaction, and the destination wallet before settling. Where a private company, trust, or layered intermediary is involved, platforms can demand incorporation papers, shareholder lists, and board details. Trades can be held when the paperwork is incomplete.

It does not, crucially, ban anything. Owning, trading, and legal OTC activity remain permitted. What shrinks is anonymity.

### The Binance pop-up tells the same story

Days earlier, Binance — which restarted Indian operations in August 2024 after registering with the FIU — began rolling out fresh data requirements for deposits and withdrawals. Send crypto to another exchange or a self-hosted wallet and a pop-up now asks for the beneficiary's full name, country, and city. Receive funds and you supply the originator's name, PAN or national ID, and address. Binance frames this as its existing "Travel Rule" compliance, not a new rule. The effect on a user's screen is the same: the days of frictionless, identity-light transfers on regulated Indian platforms are over.

The backdrop is an unmistakable tightening. The Enforcement Directorate recently searched five Bengaluru platforms over alleged unauthorised cross-border transfers via crypto. In January, exchanges added live-selfie KYC, geolocation, and IP tracking at onboarding. Government officials have told a parliamentary committee that virtual digital assets are "high risk." And the tax regime — a flat 30% on gains plus 1% TDS on every transaction — remains the bluntest deterrent of all.

### Why the diaspora should read the fine print

For Indian Americans, this is not abstract. A large share of NRI crypto activity is precisely the cross-wallet, cross-border movement these rules target — sending value home, moving holdings between an Indian exchange account opened years ago and a US wallet, or settling with family through OTC desks to avoid the spread on small transfers.

Three practical consequences stand out. First, the name-and-PAN disclosure on transfers means an NRI's Indian crypto footprint is now legible to authorities in a way bank wires already were — except crypto carries that punishing 30% gains tax with no offset for losses against other income. Second, the $10,000 OTC threshold is low enough to catch ordinary diaspora-sized transactions, not just whales. A single repatriation of savings can trip it. Third, the compliance burden falls on the user: incomplete documentation can freeze a trade mid-flight.

There is a quieter strategic message too. India is deliberately *not* legislating comprehensive crypto regulation, leaning instead toward partial oversight — taxing and tracing without legitimising. For an NRI weighing whether to custody assets in India or keep them in the better-regulated, lower-tax US market, the math increasingly favours staying offshore. The friction is the policy.

### What's next

Expect the reporting net to widen. India has flagged that crypto derivatives — currently untaxed — are "under study," and officials have signalled they will "tread carefully" before formulating policy on them. The direction of travel, though, is set: more disclosure, refreshed KYC every six to twelve months on higher-risk accounts, and steady enforcement against offshore platforms serving Indian users without FIU registration.

For the diaspora, the takeaway is simple. India will not stop you from holding crypto. It will, increasingly, know exactly what you hold — and tax it accordingly. Anyone running money across the India-US corridor should assume every transfer above a modest threshold is now a reportable event, and plan their custody, and their tax filings, on both sides accordingly."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Qualcomm Spent 25 Years Selling Phone Chips. It Just Told Wall Street Two-Thirds of Its Future Isn't Phones.",
        "subheadline": "An Investor Day blitz — a $40 billion non-handset target, Meta and Microsoft as data-center customers, and a $3.9 billion software buy — repositions the company as an AI infrastructure player. The talent it needs is heavily Indian.",
        "slug": make_slug("qualcomm-investor-day-data-center-meta-azure-modular-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Qualcomm's pivot into AI data-center chips is a hiring story as much as a strategy story — it opens a new front in the Silicon Valley engineering job market just as legacy IT firms shed roles, and Indian chip-design talent sits at the center of it.",
        "tags": ["semiconductors", "qualcomm", "ai", "data-center", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/qualcomm-forecasts-15-billion-data-center-chip-sales-by-2029-shares-soar-2026-06-24/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/qualcomm-stock-price-data-center-chip-meta"},
            {"name": "Business Wire", "url": "https://www.businesswire.com/news/home/qualcomm-data-center-2026-investor-day"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6636463/pexels-photo-6636463.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A microprocessor on a motherboard — the AI data-center silicon Qualcomm is betting its next chapter on.",
        "image_attribution": "Pexels",
        "body": """For a quarter of a century, the question to ask about Qualcomm was simple: how are phone sales? On Wednesday, the company spent its Investor Day trying to make that question irrelevant.

The headline number was stark. Qualcomm raised its fiscal 2029 non-handset revenue target to $40 billion — roughly double its previous guidance — and within that, set a data-center chip goal of more than $15 billion. The company expects handsets to shrink from 72% of revenue in fiscal 2025 to just one-third by 2029. The stock did what stocks do when a company convincingly changes its story: shares jumped as much as 11% to $218.60, helped along by blowout earnings from memory-chip maker Micron the same morning.

### The customers, named

What gave the targets teeth was the customer roster. Qualcomm revealed that Meta will use its Dragonfly C1000 central processing units when they arrive in 2028, and that Microsoft's Azure cloud division will adopt Qualcomm's new High Bandwidth Compute architecture, expected in mid-2027. Chief executive Cristiano Amon said hyperscalers were "pulling us in" rather than the other way around — a notable claim for a company that has tried and failed to crack data centers more than once.

The strategy has a software leg too. Qualcomm agreed to buy AI infrastructure firm Modular in an all-stock deal worth about $3.9 billion. Modular's platform lets developers run AI models efficiently across different chips, and its programming language is positioned as a rival to Nvidia's CUDA — the software moat that locks millions of developers into Nvidia hardware. Owning a "neutral" layer that runs on Nvidia, AMD, and Qualcomm silicon alike is how Amon hopes to pry open a market Nvidia dominates. Separately, Qualcomm is reported to be circling AI chip startup Tenstorrent in a deal valued at $8–10 billion.

Not everyone is sold. KeyBanc called the data-center targets early days; Susquehanna kept a Neutral rating, citing mobile headwinds. Smartphone shipments are headed for their steepest annual contraction on record, squeezed by surging memory prices — the very tailwind lifting Micron is a drag on Qualcomm's core.

### Why this is a diaspora story

Strip away the slide deck and Qualcomm's pivot is, at bottom, a demand for engineers — CPU architects, inference-accelerator designers, ASIC and high-speed-connectivity specialists. That is a labor market in which Indian-origin talent is disproportionately represented, both among H-1B holders in the US and across Qualcomm's large engineering presence in Hyderabad and Bengaluru.

The timing matters for the diaspora. The dominant tech-employment narrative of 2026 has been contraction: AI-driven layoffs at Oracle, hiring freezes at Google and Amazon, and a brutal squeeze on H-1B workers given just 60 days to find a new sponsor. Qualcomm building out an entirely new product line is one of the few counter-currents — a company that needs to *add* deep silicon talent, not shed it, just as Nvidia has kept expanding its own H-1B hiring while peers retrench.

There is an India-ecosystem angle as well. Qualcomm's design centers in India are among the company's largest outside the US, and a data-center roadmap stretching to 2029 implies sustained investment in exactly the chip-design skills India's semiconductor mission has been racing to cultivate. For an Indian engineer weighing a US offer against staying home, a Qualcomm betting its future on silicon designed partly in Hyderabad changes the calculus.

### What's next

The proof points come in waves: Azure's High Bandwidth Compute chips in mid-2027, Meta's Dragonfly CPUs in 2028, and revenue from two unnamed hyperscaler custom-chip wins starting before the end of this calendar year. Each is a milestone the market will use to judge whether Amon's $40 billion promise is real or aspirational.

For the diaspora's engineers, the bet to watch is narrower and more personal: whether one of the few large US chipmakers actively expanding becomes a genuine alternative employer in a year when most of the industry has its hiring doors half-shut."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic and Amazon Just Picked 40 Indian Startups to Build the Next Wave of AI Agents. The Catch: No Equity, Big Strings.",
        "subheadline": "An India-first accelerator hands early-stage founders Claude access and $70,000 in credits. It is also a quiet land-grab for the developer loyalty that will decide who owns India's AI stack.",
        "slug": make_slug("anthropic-aws-agentic-ai-accelerator-bengaluru-40-startups-nri-founders"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI founders and angel investors, this is the clearest signal yet that the agentic-AI startup action is moving to Bengaluru — and that US frontier labs, not just US capital, now compete directly for India's best builders.",
        "tags": ["ai", "startups", "anthropic", "india-tech", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/press-release/anthropic-and-aws-select-bengaluru-based-swishx-for-their-inaugural-agentic-ai-accelerator-2026"},
            {"name": "Agentic AI Accelerator", "url": "https://www.agentic-ai-accelerator.com/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/anthropic-opens-bengaluru-office-partners-with-air-india-pratham"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Developers at work — the agentic-AI builders Anthropic and AWS are courting in Bengaluru.",
        "image_attribution": "Pexels",
        "body": """When two of the biggest names in American AI hold an "India-first" demo day, the gift on offer is real — and so is the strategy behind it.

On June 26, Anthropic and Amazon Web Services kick off the inaugural Agentic AI Accelerator 2026 in Bengaluru, a cohort of 40 early-stage startups building "agentic" AI — software designed to autonomously execute multi-step workflows rather than just answer questions. The program is open to founders from bootstrapped through Series A, runs from May to September, and is explicitly aimed at startups based in India or going to market there. The first named participant is SwishX, a Bengaluru company building agentic AI for the heavily regulated pharma and medtech sector.

The terms are generous on paper. Each startup gets $50,000 in AWS cloud credits and $20,000 in Anthropic credits, plus access to Anthropic's frontier Claude models, AWS infrastructure, technical mentorship, and an investor demo day. Crucially, the program takes no equity. For a cash-strapped seed-stage founder, $70,000 in compute and direct access to a frontier lab's engineers is a meaningful runway extension.

### Generosity with a strategy attached

Equity-free does not mean string-free. The credits come with a default platform: AWS for cloud, Claude for models. Startups on other stacks are welcome "as long as you're open to building on AWS." This is how platform loyalty is manufactured — get founders to build their first production systems on your infrastructure, and switching costs do the rest. The accelerator is, in effect, a customer-acquisition program disguised as philanthropy, and a smart one.

It also slots into a much larger India push. Anthropic is opening a Bengaluru office — its second in Asia after Tokyo — and has lined up marquee partners: Air India using Claude Code to ship software faster, Cognizant deploying Claude to 350,000 employees, and CRED and Razorpay wiring it into their risk and decision systems. CEO Dario Amodei has called India "compelling because of the scale of its technical talent." Rival OpenAI is registering in India and opening a Delhi office; Google's Gemini and Perplexity are flooding the consumer market with free advanced tiers. India has become the contested ground of the global AI build-out.

### Why the diaspora is watching closely

For Indian Americans, this lands at the intersection of two trends they straddle. The first is capital: a large slice of India's startup funding flows through diaspora angels and US venture firms — Khosla Ventures, Peak XV, Lightspeed, and others were just on Sarvam AI's $300 million round. An accelerator that surfaces 40 vetted agentic-AI startups is, for NRI investors, a curated deal-flow pipeline.

The second is talent gravity. For years the default path for India's top engineers ran one way — to Silicon Valley, on an H-1B. With US visa costs spiking, AI layoffs mounting, and frontier labs now planting offices and accelerators in Bengaluru, the pull is weakening. A founder who once would have moved to San Francisco to be near Anthropic can now build with Claude, on AWS, with the lab's engineers on a Slack channel, from Koramangala. That is a structural shift in where diaspora-adjacent careers get made.

There is a competitive wrinkle for India's own ambitions, too. The country has been backing "sovereign AI" champions like Sarvam, partly to avoid dependence on foreign models — a worry a Wall Street bank recently dramatised by calling India's AI a "fighter jet it doesn't own." An accelerator that hooks 40 of India's most promising agentic startups onto Claude and AWS pulls in the opposite direction, deepening reliance on American infrastructure even as policymakers preach independence.

### What's next

The in-person kickoff is June 26; a demo day in Bengaluru follows for selected startups, where the credits convert into the only currency that ultimately matters — follow-on funding. AWS credits stay valid for a year, Anthropic's for six months, and high performers get pulled into deeper engagement.

For the diaspora, the signal is louder than any single startup's fortunes: the agentic-AI race has a serious India front now, and the American labs are no longer waiting for India's builders to come to them."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
