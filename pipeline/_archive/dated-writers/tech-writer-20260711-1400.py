#!/usr/bin/env python3
"""Technology writer — July 11, 2026, 2:00 PM PT run."""

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
    # ─── Article 1: Fundamentum Fund III ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Nandan Nilekani Just Made His Largest Venture Bet Ever. He Is Hunting for India's Next AI Champions.",
        "subheadline": "The Infosys co-founder's VC firm Fundamentum has launched a ₹2,200 crore fund to back 8-10 early-growth startups, with AI and small language models emerging as a core investment thesis.",
        "slug": make_slug("nilekani-fundamentum-2200-crore-fund-iii-ai-startups"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Nilekani is arguably the most consequential Indian tech figure after the CEO cohort — the architect of Aadhaar, co-founder of Infosys, and now India's most prominent growth-stage VC. His thesis that India will become 'a factory for small language models' has direct implications for NRI engineers and investors watching India's AI ecosystem mature.",
        "tags": ["venture-capital", "nandan-nilekani", "ai", "indian-startups", "fundamentum", "fintech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/companies/fundamentum-launches-2200-crore-third-fund-bets-on-ai-and-indias-series-b-opportunity/article71203056.ece"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/fundamentum-nandan-nilekani-venture-fund-fintech-investments-11747648930474.html"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/05/nandan-nilekani-fundamentum-f2a-frontier-advisors-ai"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Nandan_M._Nilekani.jpg",
        "image_caption": "Nandan Nilekani, co-founder of Infosys and anchor investor of Fundamentum Partnership",
        "image_attribution": "Wikimedia Commons",
        "body": """When Nandan Nilekani writes a cheque, India's tech ecosystem pays attention. The Infosys co-founder has just committed his largest personal investment to any venture capital firm, anchoring Fundamentum Partnership's third fund — a ₹2,200 crore ($260 million) vehicle aimed squarely at India's next generation of technology startups.

The fund, which includes a ₹400 crore greenshoe option, will make concentrated bets on just 8-10 early-growth companies. Initial cheque sizes will range between ₹100 crore and ₹150 crore ($12-18 million), with the firm taking board seats — the kind of active, hands-on backing that distinguishes Fundamentum from the scattershot approach of many Indian VCs.

## The AI Thesis: Small Language Models, Not Frontier Wars

What makes this fund interesting is not just its size but its investment thesis. While global capital floods into frontier AI labs chasing the next GPT or Claude, Fundamentum is looking in a different direction entirely.

"India is going to be a factory for small language models," said Sanjeev Aggarwal, co-founder and general partner. "A lot of these unique India problems will be solved through these small language models which are designed for India." He cited land records, financial services, and other India-specific applications as use cases.

The firm expects AI-focused companies to account for roughly 20% of Fund III's deployments, with consumer technology and fintech absorbing the rest. The first cheque tends to average about $10 million, according to general partner Prateek Jain.

## Discipline Over Hype

Fundamentum's track record — built through 17 investments across its first two funds — reflects a philosophy that might feel old-fashioned in an era of frothy AI valuations. The firm demands unit economics before it considers a company to have achieved product-market fit.

"Our definition of product-market fit essentially starts with unit economics," said Mayank Kachhwaha, who leads the firm's fintech investments. "If the unit economics is not figured out, we do not think that is product-market fit."

Founded in 2017 by Nilekani and Aggarwal, the firm has backed companies including Spinny, PharmEasy, Kuku, AppsForBharat, Stable Money, FlexiLoans, and ProcMart.

## The Diaspora Dimension

For NRI investors and entrepreneurs watching India's technology landscape from the Bay Area, New Jersey, or London, Nilekani's fund represents a clear signal: India's Series B market has matured enough to absorb large, disciplined cheques.

The timing matters. India's startup funding environment has grown more disciplined over the past two years, with investors prioritising sustainable growth over the aggressive valuation spirals that defined the 2021 funding bubble. Fundamentum sees an increasingly mature exit environment emerging — beyond IPOs, large private equity firms and global institutions now provide liquidity through secondary transactions.

The firm expects to announce its first Fund III investments after the initial close, with two to three deals likely before the end of the calendar year. For Indian-origin entrepreneurs in growth mode, the message is straightforward: Nilekani is open for business, but only if your numbers work."""
    },

    # ─── Article 2: Mowito Robotics ───
    {
        "id": str(uuid.uuid4()),
        "headline": "A Bengaluru Robotics Startup Just Raised $3 Million to Teach American Factory Robots to Learn by Watching.",
        "subheadline": "Mowito's physical AI platform lets industrial robot arms learn tasks by observing human operators — no coding required. It already runs on a Fortune 500 automaker's production line in Detroit.",
        "slug": make_slug("mowito-robotics-3-million-bengaluru-detroit-physical-ai"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Mowito represents a new archetype of Indian deep-tech company: built in Bengaluru, deployed on American factory floors, and competing directly with Silicon Valley robotics startups for the physical AI market. For Indian engineers in the US, it is a reminder that the talent pipeline now runs both ways.",
        "tags": ["robotics", "physical-ai", "indian-startups", "manufacturing", "deep-tech", "bengaluru"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inc42", "url": "https://inc42.com/buzz/robotics-startup-mowito-raises-3-mn-to-expand-us-presence/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34207359/pexels-photo-34207359.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An industrial robotic arm operating on a modern manufacturing production line",
        "image_attribution": "Pexels",
        "body": """The pitch is disarmingly simple: robots should learn the same way people do — by watching and repeating.

Mowito, a Bengaluru-based robotics startup, has raised $3 million in pre-seed funding to bring that vision to the factory floors of Detroit and beyond. The round was led by Version One Ventures, with participation from All In Capital, Unisol, and iSeed. Angel investors included Soumith Chintala, CTO of Thinking Machines Lab, and Vaibhav Domkundwar, founder of Better Capital.

## Physical AI for the Factory Floor

Founded in 2024 by Puru Rastogi and Adityanag Nagesh, Mowito is building AI models that run on standard industrial robot arms. The company's core technology — what the industry calls "physical AI" — enables robots to learn new tasks directly from human operators on the factory floor, without writing a single line of code.

This is not a research project. Mowito-powered robots already operate on manufacturing lines at a Fortune 500 automotive company and at one of the world's largest electronics contract manufacturers. The startup operates out of both Bengaluru and Detroit, straddling two of the world's most important manufacturing corridors.

"We believe robots should learn the same way people do: by observing and repeating," said Rastogi. "This funding allows us to accelerate that vision, expand globally, and bring physical AI to more manufacturing environments."

## A $3 Million Bet With Global Ambitions

The capital will be deployed across three priorities: expanding Mowito's US footprint, strengthening engineering and go-to-market teams, and scaling deployments across automotive and electronics manufacturers. For a pre-seed round, the ambition is notable — most startups at this stage are still searching for product-market fit, not running on Fortune 500 production lines.

The investment comes at a time when Nvidia CEO Jensen Huang has been evangelising "physical AI" as the next great frontier, and major robotics players are racing to make industrial automation more adaptive. Mowito's approach — training standard robot arms through observation rather than bespoke programming — directly addresses one of manufacturing's oldest bottlenecks: the cost and complexity of retooling robots for new tasks.

## The Bengaluru-to-Detroit Pipeline

Mowito fits a pattern that is becoming increasingly visible in India's deep-tech ecosystem. Unlike the previous generation of Indian startups that built software products for global markets, a new cohort is building physical technology — chips, robots, satellites, drones — that competes directly with Western counterparts.

Ethereal Machines, another Indian deep-tech manufacturing startup, raised $28.5 million in its Series B round in June to expand in the US and Europe. Skyroot Aerospace recently became India's first space-tech unicorn. HRDWYR is designing AI chips in Bengaluru.

For NRI engineers working at American robotics companies, Mowito's trajectory offers a different narrative about where deep-tech innovation is emerging. The talent pipeline between Bengaluru and Silicon Valley has long been a one-way street. Companies like Mowito suggest the traffic is beginning to flow in both directions — with Indian-built physical AI arriving on American factory floors, rather than just Indian engineers arriving at American tech companies."""
    },

    # ─── Article 3: NPCI's AI-Powered UPI Protocol ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India Wants AI Agents to Pay Your Bills. NPCI Is Building the Rails.",
        "subheadline": "The National Payments Corporation of India is developing a Unified Agent Protocol that would let AI assistants make UPI transactions on behalf of users — potentially making India the first country with national infrastructure for agentic payments.",
        "slug": make_slug("npci-unified-agent-protocol-upi-ai-payments"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "UPI has become the payments layer NRIs encounter every time they visit India — and increasingly, when they send money home. If NPCI succeeds in building AI-agent infrastructure into UPI, it would position India's digital payments stack ahead of anything available in the US, where agentic commerce is still a collection of private initiatives by Visa, Google, and OpenAI.",
        "tags": ["upi", "ai-agents", "npci", "digital-payments", "fintech", "agentic-commerce"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/india-plans-ai-powered-upi-payments-framework-through-unified-agent-protocol"},
            {"name": "Business Standard", "url": "https://www.business-standard.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/12935064/pexels-photo-12935064.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A contactless payment being made using a smartphone and QR code scanner at a modern retail counter",
        "image_attribution": "Pexels",
        "body": """Here is a question nobody was asking five years ago: when your AI assistant orders groceries on your behalf, who authorises the payment?

India thinks it has the answer. The National Payments Corporation of India (NPCI) is developing what it calls the Unified Agent Protocol (UAP) — a framework that would allow AI agents to make transactions through UPI on behalf of human users. If it works, India would become one of the first countries in the world to build national payments infrastructure for agentic commerce.

## What the Protocol Actually Does

UPI's existing trust architecture was designed around a simple assumption: a human user on a human-owned device initiates every transaction. The rise of AI assistants capable of shopping, booking services, and making purchases independently breaks that assumption.

The UAP would create a common, interoperable layer that registers, verifies, and authorises AI agents to transact across the UPI ecosystem — without changing the underlying payment rails that already process 22.71 billion transactions per month.

Under the proposed framework, NPCI's role would remain limited to validating whether a payment request is genuine, similar to how the current system works. The protocol would verify whether an AI agent is authorised to act on behalf of a user, define the limits of that authority, and establish accountability if something goes wrong.

AI agents could originate from merchant apps, payment platforms, AI assistants such as ChatGPT or Claude, or dedicated agentic platforms. The key design principle: any authorised agent should be able to transact with any UPI-connected merchant, preserving the interoperability that made UPI dominant in the first place.

## Groceries First, Everything Else Later

The protocol is being developed in consultation with industry stakeholders, and the early consensus is that low-value, repetitive purchases will lead adoption. Think groceries, dairy products, and daily essentials — the kind of transactions where an AI agent could reasonably anticipate what you need and execute the purchase without bothering you for approval each time.

A senior executive at a digital payments company told *Business Standard* that this could create new opportunities for India's quick-commerce platforms, which already operate on razor-thin delivery windows.

## India vs. The World

NPCI's initiative is not happening in a vacuum. Visa is building AI-agent commerce capabilities. Google is exploring similar infrastructure. OpenAI and Pine Labs are developing their own protocols. But there is a critical difference: most of these are private, proprietary initiatives.

India's approach is to build agent commerce into a public digital infrastructure layer — the same philosophy that turned UPI from a government project into a system processing nearly ₹29 trillion ($345 billion) per month, with 63.5% of transactions now flowing through merchant payments rather than peer-to-peer transfers.

## What It Means for the Diaspora

For NRIs, UPI has already transformed the experience of visiting India. The "UPI One World" wallet — launched at the India AI Impact Summit in February for delegates from over 40 countries — hinted at where things were heading: a world where digital payments in India work seamlessly regardless of where you bank.

If NPCI pulls off the UAP, the implications go further. NRIs who manage household expenses in India — paying domestic staff, topping up a parent's mobile plan, ordering groceries for family — could delegate these to an AI agent that transacts through UPI on their behalf, across time zones, without a phone call.

Consumer protection mechanisms including chargebacks and dispute resolution will need to evolve alongside AI-led transactions, industry participants acknowledge. But the ambition is clear: India wants its payments infrastructure to stay ahead of the AI curve, not catch up to it.

The protocol does not yet have a public timeline. But in a country where UPI went from zero to 22 billion monthly transactions in under a decade, betting against NPCI's ability to ship is a risky proposition."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
