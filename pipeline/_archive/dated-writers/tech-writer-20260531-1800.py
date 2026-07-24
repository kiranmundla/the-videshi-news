#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 18:00 UTC batch"""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


articles = [
    # ─── ARTICLE 1: Indian IT's Agentic AI Pivot ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Wipro and TCS Just Made Their Biggest AI Bets Yet. One Stock Surged 21 Per Cent.",
        "subheadline": "In the same week, Wipro partnered with ServiceNow on agentic AI and TCS became Mistral's first global systems integrator. Indian IT is done waiting.",
        "slug": make_slug("wipro-tcs-agentic-ai-servicenow-mistral-indian-it"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Tens of thousands of NRIs hold TCS and Wipro shares through Indian brokerage accounts or ADRs. These partnerships signal that legacy IT services firms are repositioning as AI deployment partners — the kind of strategic shift that determines whether these stocks stagnate or re-rate. For Indian engineers at US enterprises, TCS and Wipro are increasingly the teams deploying AI tooling into their own workflows.",
        "tags": ["indian-it", "ai", "agentic-ai", "wipro", "tcs", "servicenow", "mistral"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-wipro-rises-after-expanded-partnership-scale-ai-adoption-2026-05-30/"},
            {"name": "Livemint", "url": "https://www.livemint.com/market/stock-market-news/wipro-share-price-jumps-over-4-on-ai-partnership-boost-turns-top-nifty-it-gainer-today-11748499692908.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tcs-mistral-partner-to-become-first-global-systems-integrator-for-enterprises/article69622589.ece"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/post/tcs-mistral-first-mover-ai-rail/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804612/pexels-photo-6804612.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For years, India's IT services giants occupied a specific lane: they took Western companies' technology requirements, broke them into manageable chunks, and executed them reliably at scale. It was a $250 billion industry built on trust, process rigour, and — critics would say — a reluctance to lead.

This week, two of the sector's largest players signalled they are done being passengers in the AI revolution.

## Wipro's ServiceNow Gambit

On May 28, Wipro announced an expanded partnership with ServiceNow to deploy agentic AI workflows across core enterprise functions — IT, HR, procurement, and cybersecurity. The deal integrates Wipro's Intelligence platform, its unified suite of AI-powered offerings, with ServiceNow's AI Platform.

Wall Street noticed. Wipro's American Depositary Receipt surged over 21 per cent on the NYSE in a single session, hitting $2.49 before settling at $2.43. In Mumbai, the stock gapped up 4.5 per cent at the open the next morning.

The partnership is not a vague AI collaboration. It names specific products: SmartProcure for procurement automation, Telco Autonomous Networks for telecom operations, and Cyber Transform for cybersecurity. Each is designed to deploy agentic AI — systems that can initiate, orchestrate, and execute work across enterprise systems with minimal human intervention.

"This is Wipro saying: we are not just implementing someone else's AI. We are building the deployment layer," said one Mumbai-based IT analyst.

## TCS Goes to Paris

The same week, Tata Consultancy Services became the first global systems integrator partner for Mistral Forge, the enterprise AI platform built by the French AI lab Mistral. TCS will use Forge to build custom AI models for enterprise customers using their proprietary data and domain-specific knowledge, targeting banking, manufacturing, healthcare, and the public sector.

TCS is also establishing a dedicated Centre of Excellence for Mistral — a hub for joint innovation, industry-specific solutions, and early access to Mistral's beta models.

"TCS' global scale and contextual industry knowledge make them an ideal partner for Mistral," said Arthur Mensch, Mistral's CEO and co-founder. TCS CEO K Krithivasan framed the partnership as part of the company's broader "Infrastructure to Intelligence" strategy.

The significance lies in the orchestration layer. TCS's WisdomNext platform — a GenAI aggregation engine with thousands of pre-built agents, governance controls, and enterprise data pipelines — is designed to sit above individual AI models and manage the messy reality of deploying AI into regulated, complex enterprises. If TCS can sell the control plane rather than just the model call, it moves from services vendor to infrastructure provider.

## The Bigger Picture

The Indian IT sector's Nifty IT index rose 3 per cent on the week, buoyed not just by these deals but by a broader re-rating of Indian IT companies as AI deployment partners. TCS was named America's most reliable IT services company in Newsweek's 2026 rankings. Mistral's CEO described an Indian IT major as an "ideal partner" for scaling trusted enterprise AI.

For NRI investors who have held TCS and Wipro through years of single-digit revenue growth, the question is whether these partnerships translate into higher-margin, stickier revenue — or remain announcement-stage optics. The answer depends on whether WisdomNext and Wipro Intelligence become the operating layers inside enterprise environments, with governance and workflows that are genuinely hard to replace.

With over 300,000 associates trained on AI and ML fundamentals, TCS alone has one of the largest AI-ready workforces in the world. The talent is there. Whether the ambition matches it is what the next four quarters will reveal."""
    },

    # ─── ARTICLE 2: IBM's $15 Billion Quantum-AI Bet ───
    {
        "id": str(uuid.uuid4()),
        "headline": "Arvind Krishna Just Bet $15 Billion on Quantum Computing and Cybersecurity. IBM Had Its Best Week in Years.",
        "subheadline": "The IIT Kanpur graduate's biggest move as CEO: a $10 billion quantum push, a $1 billion chip foundry, and a cybersecurity initiative that puts 20,000 engineers to work.",
        "slug": make_slug("arvind-krishna-ibm-15-billion-quantum-cybersecurity"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Arvind Krishna, born in Andhra Pradesh and an IIT Kanpur alumnus, is making the largest quantum computing investment in corporate history. For Indian engineers in the US — many of whom work at IBM's research labs in Yorktown Heights and Almaden — this is a direct bet on the kind of deep-tech careers that H-1B holders have historically excelled at. For NRI investors, IBM stock's 19% weekly surge is a reminder that Indian-origin CEOs are not just maintaining American tech empires — they are reshaping them.",
        "tags": ["ibm", "arvind-krishna", "quantum-computing", "cybersecurity", "indian-tech-leaders"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CoinCentral", "url": "https://coincentral.com/ibm-stock-quantum-ai-investment/"},
            {"name": "IBM Newsroom", "url": "https://newsroom.ibm.com/announcements"},
            {"name": "CRN", "url": "https://www.crn.com/news/cloud/ibm-touts-ai-hybrid-cloud-demand-for-our-solutions-remains-strong"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg",
        "body": """When Arvind Krishna took over as IBM's CEO in April 2020, the company was a 109-year-old institution that had spent two decades watching younger rivals eat its lunch. Six years later, the IIT Kanpur graduate just made the largest single investment bet in IBM's modern history — and the market responded with the stock's best week in years.

IBM announced a $15 billion investment package spanning quantum computing and AI-driven cybersecurity. The stock opened at $298.26 on Friday, up nearly 19 per cent over the past week, pushing IBM's market capitalisation past $280 billion.

## The Quantum Moonshot

The centrepiece is a $10 billion commitment over five years to scale quantum computing operations. This is not a research grant or an exploratory partnership. It includes $1 billion for Anderon, a dedicated quantum chip foundry that would be the first of its kind in the United States. The US Department of Commerce is expected to contribute a further $1 billion through the CHIPS Act.

IBM already operates more than 90 deployed quantum systems and has built a partner network that spans major financial institutions, pharmaceutical companies, and national laboratories. The Anderon foundry is designed to move quantum from laboratory curiosity to manufacturing-scale reality — fabricating the specialised superconducting chips that no existing semiconductor foundry can produce.

For context, quantum computing has been IBM's long game since the 1990s. In May 2016, IBM put the first quantum computer on the cloud. A decade later, the company is betting that the technology is approaching the threshold of practical utility — solving problems in drug discovery, materials science, financial modelling, and cryptography that classical computers cannot touch.

## Project Lightwell: Security at Scale

The second pillar is Project Lightwell, a $5 billion enterprise security initiative co-developed with Red Hat. The project puts 20,000 engineers to work helping large enterprises — including major US banks — identify and remediate vulnerabilities in open-source software.

Krishna pointed to the rise of powerful AI models as an accelerating threat vector. As enterprises embed AI into critical systems, the attack surface for open-source dependencies grows exponentially. Project Lightwell is IBM's bet that the companies deploying AI fastest will also need security infrastructure fastest — and that a company with Red Hat's open-source pedigree is uniquely positioned to provide it.

## What It Means for Indian Engineers

IBM employs thousands of Indian-origin engineers across its research labs in Yorktown Heights, Almaden, and Bengaluru. The quantum computing division, in particular, has been a magnet for physics and engineering PhDs from IITs and IISc. Krishna's investment ensures these roles are not going anywhere — if anything, the Anderon foundry and expanded quantum operations will create new positions in hardware engineering, cryogenics, and quantum error correction.

For NRI investors, IBM's transformation under Krishna offers a counternarrative to the familiar story of Indian-origin CEOs as stewards of existing empires. Satya Nadella pivoted Microsoft to cloud. Sundar Pichai bet Alphabet on AI. Krishna is now staking IBM's future on quantum and security — technologies that may take a decade to fully mature but could define the next era of computing.

Management reaffirmed its 2026 outlook for steady revenue and cash-flow growth, giving investors confidence that the new investments sit on top of a stable base. The message: IBM is not gambling its present to fund its future. It is doing both.

Whether the $15 billion delivers returns commensurate with the ambition will take years to judge. But this week, at least, the market decided that Arvind Krishna's bet was worth backing."""
    },

    # ─── ARTICLE 3: RBI Digital Rupee Goes International ───
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Digital Rupee Is Going International. For NRIs Sending Money Home, That Changes Everything.",
        "subheadline": "The RBI's annual report reveals cross-border CBDC pilots with Singapore and the UAE, a new cloud platform for financial firms, and a vision for programmable welfare payments.",
        "slug": make_slug("rbi-digital-rupee-cbdc-cross-border-singapore-uae"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The UAE is home to over four million Indians and is one of the largest remittance corridors to India. A cross-border CBDC link between the RBI and the UAE central bank could slash transfer fees and settlement times for millions of NRIs sending money home. The Singapore pilot matters for the tens of thousands of Indian tech professionals working there. This is India's digital public infrastructure — the same system that produced UPI — now being exported for the diaspora's direct benefit.",
        "tags": ["digital-rupee", "cbdc", "rbi", "cross-border-payments", "upi", "fintech", "remittances"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-rbi-plans-expansion-digital-rupee-through-welfare-schemes-cross-border-2026-05-29/"},
            {"name": "Livemint", "url": "https://www.livemint.com/economy/rbi-to-expand-e-rupee-pilot-to-include-cross-border-payments-welfare-transfers-and-domestic-retail-11748522222150.html"},
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/economy/rbi-to-expand-digital-rupee-pilots-explore-cross-border-cbdc-transactions-in-fy27"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3349182-rbi-plans-expansion-of-cbdc-for-cross-border-transactions"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6205512/pexels-photo-6205512.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The Reserve Bank of India's 2025-26 annual report, released on Friday, contains a quiet but significant signal for the Indian diaspora: the digital rupee is preparing to cross borders.

The RBI disclosed that it has signed a memorandum of understanding with Singapore's Monetary Authority on digital asset collaboration, and is holding bilateral discussions with the Central Bank of the UAE to operationalise a cross-border CBDC pilot. It has also joined multilateral initiatives led by the Bank for International Settlements' Innovation Hub, including Project Rialto and Phase 2 of Project Mandala.

For the four million Indians living in the UAE and the tens of thousands of tech professionals in Singapore, this is not an abstract policy document. It is the infrastructure for a future where sending money home does not require a 3-5 per cent remittance fee and a two-day settlement window.

## The Remittance Angle

India received $129 billion in remittances in 2025, more than any other country. The UAE-India corridor is among the busiest in the world. Today, an NRI in Dubai sending ₹1 lakh to a family member in Kerala pays anywhere from ₹1,500 to ₹5,000 in transfer fees plus unfavourable exchange rate margins, and the money takes one to three business days to arrive.

A cross-border CBDC link could compress that to near-zero cost and near-instant settlement — the same transformation that UPI brought to domestic payments. The RBI's annual report does not promise this by next quarter, but it lays the regulatory and technical groundwork.

Livemint reported in March that instant money transfers between India and the UAE may become a reality soon, with the two central banks actively working to link their sovereign digital currencies.

## Programmable Money Arrives

Domestically, the RBI has been running CBDC pilots in welfare payments across Gujarat, Puducherry, and Chandigarh, where beneficiaries received food subsidies through the digital rupee. The key innovation is programmability: the ability to design money that can only be spent on specific categories, expires after a certain period, or automatically routes to designated recipients.

"Multiple government agencies commenced pilots in various direct benefit transfer schemes leveraging programmability feature of CBDC to ensure productive utilisation of public funds," the RBI noted.

This is India's digital public infrastructure philosophy — the same thinking that produced Aadhaar, UPI, and DigiLocker — applied to the currency itself. Over eight million Indians currently use the e-rupee, with 120 million transactions valued at ₹28,000 crore conducted since its 2022 launch.

## The Cloud Surprise

Buried in the same annual report is another first: the RBI's cloud platform for financial firms has gone live in beta mode with nine users. The RBI is among the first central banks in the world to offer cloud infrastructure to its regulated entities.

"The work on phase I of the IFS cloud services is in advanced stage," the RBI said. This is significant because it gives the RBI direct oversight of the infrastructure that India's banks and fintech companies run on — a level of control that most central banks do not possess.

## The Catch

For all the ambition, the numbers tell a more complicated story. The value of digital rupee banknotes in circulation actually fell — from ₹1,016 crore in March 2025 to ₹772 crore in March 2026, a 24 per cent decline. Domestic adoption has plateaued, and the e-rupee remains a rounding error next to UPI's monthly volumes.

The RBI's bet is that cross-border use cases and programmable welfare payments will provide the utility that domestic retail has not yet delivered. Whether that bet pays off depends on execution speed and political will from partner countries.

For NRIs, the practical impact is still a few years away. But the direction is clear: India is building the rails for a world where the digital rupee works as seamlessly across borders as UPI works within them. The diaspora stands to be among its biggest beneficiaries."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
