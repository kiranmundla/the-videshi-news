#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-07 21:00 UTC run"""
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
    # ─────────────────────────────────────────────────
    # ARTICLE 1: India Supreme Court AI Regulations
    # ─────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Supreme Court Just Drew the Line on AI in Courtrooms",
        "subheadline": "Draft regulations ban algorithmic sentencing, risk scoring for bail, and AI-only judicial decisions — while explicitly encouraging courts to adopt the technology for everything else.",
        "slug": make_slug("india-supreme-court-ai-regulations-courts-ban-algorithmic-sentencing"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian-American lawyers, legal tech professionals, and NRI investors in judicial AI companies need to understand India's sweeping new framework — it will shape the largest common-law AI governance experiment in the world.",
        "tags": ["ai-regulation", "supreme-court", "india-judiciary", "legal-tech", "ai-governance"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "SCC Times", "url": "https://www.scconline.com/post/2026/06/05/sc-issues-draft-ai-regulations-for-courts/"},
            {"name": "IndiaLaw.in", "url": "https://www.indialaw.in/blog/cyber-law/supreme-court-ai-framework-courts-india/"},
            {"name": "Nagaland Post (PTI)", "url": "https://www.nagalandpost.com/national-news/ai-no-longer-speculative-tech-but-an-operational-reality-cji/"},
            {"name": "Legal Bites", "url": "https://www.legalbites.in/supreme-court-ai-governance-framework/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Supreme_Court_of_India%2C_inside_buildings_03.jpg/1280px-Supreme_Court_of_India%2C_inside_buildings_03.jpg",
        "image_caption": "The Supreme Court of India complex in New Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": """On June 3, the AI Committee of the Supreme Court of India published what may become the most consequential AI governance document in the common-law world: a preliminary draft of the Regulations for Use of Artificial Intelligence in Courts, 2026. Stakeholders have until June 20 to submit comments. After that, the rules get teeth.

The draft is long, technically precise, and unambiguous in its central message: AI may assist judges, but it may never replace them.

## What the Regulations Allow

The permitted uses read like a modernisation wishlist for a judiciary that processes roughly 50 million pending cases. Courts can deploy AI for case management and scheduling, automated transcription with mandatory human review, translation of judgments across India's official languages, legal research and citation verification, chatbots for litigant assistance, accessibility tools for persons with disabilities, document fraud detection, and the auto-generation of notices and summons.

These are not aspirational suggestions. Regulation 16 establishes a "Presumption in Favour of Responsible AI Adoption," meaning courts must actively seek opportunities to deploy AI where it demonstrably improves access to justice. Any refusal to permit AI use must be justified in writing. The message to institutional inertia: the default is adoption, not caution.

## What Is Absolutely Banned

The prohibitions are non-derogable — not even the Chief Justice of India can override them. No court may use AI for algorithmic sentencing or adjudication without mandatory human oversight. No risk scoring for bail eligibility, recidivism prediction, or witness credibility. No profiling of accused persons, parties, or lawyers. No surveillance of judges or advocates. No AI-generated material submitted as evidence without full disclosure.

The ban on risk scoring is the sharpest departure from global practice. In the United States, tools like COMPAS have been used in sentencing decisions for years, despite documented racial bias. India's draft says: not here, not ever.

"Accountability for all decisions made by any officer with the assistance of AI shall rest exclusively upon such officer," the draft states. "It shall not be permissible to invoke the outputs of an AI System, the opaqueness of a Black Box system, or the occurrence of hallucination, as a ground for avoiding accountability."

## The Governance Architecture

A permanent Apex Body at the Supreme Court — chaired by a sitting judge nominated by the CJI — will set standards, coordinate with High Courts, and publish annual governance reports. Each High Court must constitute its own AI Committee, backed by a dedicated AI Secretariat. A Centre of Research and Excellence on Artificial Intelligence (CoRE-AI) will conduct original research, evaluate tools, and track international developments.

Every AI system proposed for court use must first pass a Technical and Ethical Impact Assessment examining its architecture, training data quality, bias risks, hallucination tendencies, and explainability. Annual audits are mandatory, and critically, they must be conducted in-house — source code and datasets may not be shared with any third party.

## Why Indian Americans Should Care

For the estimated 30,000-plus Indian-origin lawyers practising in the United States, and the growing number of Indian-American legal tech professionals building tools like Harvey AI, CoCounsel, and similar platforms, these regulations define the rules of engagement for the world's second-largest legal system.

Any practitioner or vendor who files AI-assisted pleadings in an Indian court must now submit a prescribed declaration disclosing AI involvement. Fabricated or misleading AI-generated content attracts full personal liability. For US-based legal tech companies eyeing the Indian market — worth an estimated $1.3 billion by 2028 — the procurement rules are stringent: prior written approval, source code transparency, prohibition on retraining models with court data, and mandatory indemnity clauses.

Chief Justice Surya Kant, speaking at Birkbeck College, University of London, on June 5, framed the stakes plainly: "AI does not merely enhance human capacity; it increasingly participates in decision-making processes that were historically considered uniquely human. The responsibility of law is to ensure that technological power remains accountable to constitutional values."

The consultation window closes on June 20. For a judiciary that has struggled for decades with case backlogs, the promise of AI is clear. These regulations are India's attempt to claim the upside without importing the damage."""
    },
    # ─────────────────────────────────────────────────
    # ARTICLE 2: Zepto IPO
    # ─────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Zepto Is Filing Its IPO Papers This Week. India's Quick-Commerce War Goes Public.",
        "subheadline": "The 10-minute grocery delivery startup is targeting a ₹11,000 crore listing by July — one of the largest Indian tech IPOs of 2026.",
        "slug": make_slug("zepto-ipo-filing-drhp-quick-commerce-india-listing"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors tracking India's consumer tech boom have a new decision to make: Zepto's July IPO will test whether quick commerce can generate public-market returns, not just venture capital enthusiasm.",
        "tags": ["zepto", "ipo", "quick-commerce", "indian-startups", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Storyboard18 / Moneycontrol", "url": "https://www.storyboard18.com/digital/zepto-ipo-drhp-filing-roadshow/"},
            {"name": "NDTV Profit / Inshorts", "url": "https://www.inshorts.com/en/news/zepto-ipo-drhp-filing"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/markets/ipo/zepto-ipo-drhp-filing"},
            {"name": "Inc42 IPO Tracker", "url": "https://inc42.com/features/indian-startup-ipo-tracker/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/8939510/pexels-photo-8939510.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Smartphone displaying a grocery delivery order — the interface Zepto's 2.5 million daily users know well",
        "image_attribution": "Pexels",
        "body": """Zepto, the Mumbai-headquartered quick-commerce startup that delivers groceries in ten minutes or less, is expected to file an updated Draft Red Herring Prospectus with SEBI this week. Investor roadshows will follow immediately. If the timeline holds, India's public markets could see one of their biggest tech listings by late July.

The numbers are no longer startup-scale. Zepto is now targeting a raise of more than ₹11,000 crore ($1.3 billion) through the IPO. Daily order volumes have crossed 2.5 million, up from roughly 1.5 to 1.7 million earlier this year. The company's quarterly Net Realizing Value — its preferred metric, which includes advertising revenue — is approaching $1 billion, double what it was in late 2025.

## How Zepto Got Here

Founded in 2021 by Aadit Palicha and Kaivalya Vohra — both Stanford dropouts who were 19 and 20 at the time — Zepto entered a market that most investors considered insane. Ten-minute grocery delivery required a dense network of dark stores, a logistics stack built for speed rather than cost, and the willingness to burn capital while Indian consumers decided whether they actually wanted mangoes delivered faster than a pizza.

They decided they did. India's quick-commerce market has grown from nearly nothing in 2021 to an estimated $6 billion in gross merchandise value in 2026, according to industry estimates. Zepto, Blinkit (owned by Zomato), Swiggy Instamart, and the newer Flipkart Minutes are locked in a four-way fight for dark-store density and delivery times.

Zepto had confidentially filed its IPO papers in December 2025, a route that let the startup receive iterative feedback from SEBI without exposing sensitive financials to listed rivals like Zomato. SEBI issued its formal observations in early May 2026, clearing the regulatory hurdle.

## The IPO Landscape

Zepto is entering a crowded IPO calendar. PhonePe has filed for a ₹10,700 to ₹13,400 crore offering. OYO has SEBI approval for a ₹6,650 crore issue. Flipkart, OfBusiness, and Razorpay are all in various stages of IPO preparation. The pipeline is the deepest India's tech sector has ever seen.

But the reception is uncertain. Foreign institutional investors have pulled back from Indian markets amid geopolitical tensions, and retail subscription levels for recent tech IPOs have been modest. The quick-commerce sector, specifically, faces persistent questions about unit economics: can 10-minute delivery ever be sustainably profitable, or does it require permanent subsidy from advertising and private-label margins?

Zepto's answer has been to lean into advertising. The company's ad platform — which lets FMCG brands pay for prominent placement in the app — has become a meaningful revenue stream, folded into the Net Realizing Value metric. It is, effectively, the same playbook that turned Amazon from an e-commerce company into an advertising giant.

## What NRI Investors Need to Know

For the Indian diaspora investor class — which has poured billions into Indian equities through Liberalised Remittance Scheme (LRS) channels, NRE accounts, and platforms like Vested and INDmoney — Zepto's IPO is a direct bet on India's urban consumer evolution.

The bull case: India's top 50 cities are rapidly adopting convenience commerce, dark-store density creates natural moats, and advertising revenue can subsidise delivery costs the way it does for Amazon. The bear case: quick commerce is a feature, not a platform, and Zomato's Blinkit (backed by a listed parent with deep pockets) or Flipkart Minutes (backed by Walmart) could outspend Zepto into irrelevance.

Neither Palicha nor Vohra are expected to sell shares in the IPO, according to reports — a signal of founder conviction that public-market investors tend to reward.

The filing this week marks the point of no return. For a company that didn't exist five years ago, the speed of the journey mirrors the speed of its deliveries: fast, aggressive, and leaving very little time for second thoughts."""
    },
    # ─────────────────────────────────────────────────
    # ARTICLE 3: Innefu Labs Sovereign AI Defense
    # ─────────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Sovereign AI Defense Startup Just Raised $30 Million. It Powers the Country's Counter-Terrorism Nerve Centre.",
        "subheadline": "Innefu Labs builds the AI that India's intelligence agencies use daily — and it just secured funding to go global and prepare for an IPO.",
        "slug": make_slug("innefu-labs-sovereign-ai-defense-30-million-ipo"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For Indian Americans in cybersecurity and defense tech — and NRI investors watching India's emerging defense-industrial complex — Innefu Labs represents a rare bet: an indigenous AI company that already has ₹100 crore in government contracts.",
        "tags": ["innefu-labs", "cybersecurity", "sovereign-ai", "indian-defense-tech", "startup-funding"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/innefu-labs-series-b-panthera-growth-partners"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/cybersecurity-startup-innefu-labs-raises-30-mn/"},
            {"name": "Entrepreneur India", "url": "https://india.entrepreneur.com/article/innefu-labs-series-b-panthera/"},
            {"name": "CIOL", "url": "https://www.ciol.com/innefu-labs-30-million-defense-ai/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/37730211/pexels-photo-37730211.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Server racks in a secure data centre — the infrastructure backbone for sovereign AI systems",
        "image_attribution": "Pexels",
        "body": """Most AI startups want to help you write emails faster. Innefu Labs wants to help India find terrorists.

The New Delhi-headquartered cybersecurity company, founded in 2010 by Tarun Wig and Abhishek Sharma, has raised $30 million in a Series B round led by Singapore-based Panthera Growth Partners. The funding — a mix of primary and secondary transactions from Panthera's second fund, backed by institutional investors from India, the EU, and the US — positions Innefu for global expansion and an eventual IPO.

What makes Innefu unusual in India's startup landscape is not the funding amount. It is the client list.

## The Business of National Security

Innefu Labs has over 100 installations across the Indian subcontinent, the Middle East, and Southeast Asia. Its platforms power India's national terrorism data fusion centre, revenue intelligence fusion platforms, predictive policing systems, and open-source intelligence tools used by defence and intelligence agencies. The company holds a growing pipeline of contracts worth more than ₹100 crore spanning defence, intelligence, law enforcement, and revenue intelligence.

This is not a company pitching decks to venture capitalists about total addressable market. Innefu's market is the sovereign security apparatus of the world's most populous nation.

"The next wave of technological leadership will belong to nations that own their intelligence capabilities," CEO Tarun Wig said in a statement. "Innefu is committed to ensuring that India stands at the forefront of that transformation."

## Sovereign AI: The Thesis

The concept of sovereign AI — artificial intelligence infrastructure that a nation controls entirely, from training data to inference — has become one of the most consequential ideas in geopolitics. France has Mistral. The UAE has Falcon. Saudi Arabia is building SDAIA. India, despite producing a disproportionate share of the world's AI researchers, has been conspicuously dependent on American foundation models for most commercial applications.

Innefu is betting on the opposite approach. The fresh capital will fund three priorities: scaling its proprietary Agentic AI platform, establishing a dedicated Physical AI and robotics division, and building domain-specific language models designed for high-security environments where OpenAI's API is not an option.

Shilpa Kulkarni, founder and managing director of Panthera Growth Partners, framed the investment in capability terms: "Our investment decision is based on their proprietary technology, deep domain expertise, and a proven track record in high-stakes, mission-critical environments."

## Why This Matters for the Indian Diaspora

India's defence budget crossed $75 billion in FY2026, with the government actively channelling procurement toward indigenous companies. The Defence Acquisition Procedure now explicitly favours Indian-designed and Indian-manufactured systems. For the thousands of Indian-origin cybersecurity and defence professionals working at Palo Alto Networks, CrowdStrike, Palantir, Raytheon, and Lockheed Martin in the US, Innefu represents a mirror-image opportunity: a company doing the same class of work, but for India.

The NRI investment angle is equally direct. Innefu's IPO preparation — being the explicit purpose of this funding round — means the company could list on Indian exchanges within 18 to 24 months. For diaspora investors already tracking India's defence sector (Bharat Electronics, HAL, and Mazagon Dock have all delivered multi-bagger returns), Innefu would be the first pure-play AI defence listing.

The sovereign AI market is small today. But in a world where the US restricts chip exports, the EU regulates foundation models, and China builds its own stack, every major nation will eventually need indigenous AI infrastructure for defence and intelligence. India is starting late, but Innefu has been building quietly for 16 years.

The $30 million is the signal. The IPO will be the test."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
