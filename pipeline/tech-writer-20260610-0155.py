#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-10 01:55 PDT batch"""

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
# ARTICLE 1: ISRO LVM3 Tech Transfer
# ─────────────────────────────────────────────

art1_body = """India's space programme just crossed a threshold that has been decades in the making. The Indian National Space Promotion and Authorization Centre (IN-SPACe) has invited private companies to bid for the complete technology transfer of ISRO's Launch Vehicle Mark-3 — the heaviest operational rocket in India's arsenal and the machine that carried Chandrayaan-2 and Chandrayaan-3 to the moon.

The Expression of Interest, released on Tuesday, is not a partnership offer or a subcontracting arrangement. It is a full handover: end-to-end realisation, manufacturing, and commercial launch operations of the LVM3, transferred from ISRO to a private entity or consortium. ISRO will provide 42 months of handholding and infrastructure support, or until the selected company successfully launches two LVM3 vehicles on its own — whichever comes first.

## Why This Matters Now

The timing is deliberate. Last month, IN-SPACe issued a similar EOI for the technology transfer of the PSLV, India's workhorse satellite launcher. With both vehicles now on the commercialisation table, nearly all of India's key rocket systems are open to private industry for the first time.

The move is partly defensive. ISRO's launch cadence has been declining, and recent incidents involving PSLV flights have raised questions about whether the agency — stretched thin across Gaganyaan, interplanetary missions, and routine satellite deployments — can sustain operational tempo alone. "We already have various private sector infrastructure and aerospace companies who play a role in making the rockets," said Chaitanya Giri, Space Fellow at the Observer Research Foundation. "A technology transfer to such players will help improve the launch cadence."

## The Private Sector Is Ready

India's private space ecosystem is no longer theoretical. Agnikul Cosmos, valued at over $500 million, is targeting 50 annual launches by 2028 from its IIT Madras base. Skyroot Aerospace has already conducted a successful suborbital flight. Tata Advanced Systems and Larsen & Toubro have long manufactured ISRO rocket components. The question was never capability — it was access. That barrier is now formally gone.

The global context sharpens the urgency. SpaceX launches roughly twice a week. Rocket Lab has become a public company with a steady commercial cadence. India manages roughly six to eight launches per year. If the private sector can double or triple that rate, it changes India's position in the $630 billion global space economy overnight.

## What NRIs Should Watch

For the Indian diaspora, this story has three dimensions. First, investment: Indian space startups have raised over $400 million in recent years, with Agnikul, Skyroot, and Pixxel leading the way. A commercially viable LVM3 operator would be a significant new asset class. Second, talent: Indian engineers at Boeing, SpaceX, Northrop Grumman, and Blue Origin now have a reason to consider return-to-India trajectories as the domestic launch industry scales. Third, geopolitics: an India with high-frequency commercial launch capability becomes a more significant partner in the Artemis Accords and a more credible alternative to China's Long March programme for international satellite customers.

ISRO built the rocket. The private sector will now decide how often it flies."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "ISRO Just Handed Its Biggest Rocket to the Private Sector. India's Launch Cadence Depends on It.",
    "subheadline": "The LVM3 technology transfer opens India's heaviest launch vehicle to commercial manufacturing — a first that could reshape the country's position in the global space economy.",
    "slug": make_slug("isro-lvm3-technology-transfer-private-sector-space"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investment opportunities in Indian space startups; return-to-India talent pipeline for aerospace engineers at SpaceX and Boeing; India's growing weight as a commercial launch partner in the Artemis Accords",
    "tags": ["isro", "indian-space", "lvm3", "privatisation", "agnikul", "skyroot"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/in-space-invites-private-sector-interest-for-transfer-of-isros-lvm3-rocket-technology/article71081335.ece"},
        {"name": "YourStory", "url": "https://yourstory.com/2026/06/bharat-innovates-2026-iit-madras-agnikul-3d-printed-rocket-engine"},
        {"name": "Observer Research Foundation", "url": "https://www.orfonline.org/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/LVM3_M3%2C_OneWeb_India-2_campaign_07.webp/1280px-LVM3_M3%2C_OneWeb_India-2_campaign_07.webp.png",
    "image_caption": "ISRO's LVM3 rocket on the launch pad at Sriharikota during the OneWeb India-2 campaign",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ─────────────────────────────────────────────
# ARTICLE 2: IBM + Google Agentic AI Partnership
# ─────────────────────────────────────────────

art2_body = """Arvind Krishna's IBM has been quietly repositioning itself as the connective tissue between enterprise legacy systems and AI-native infrastructure. The latest move makes the strategy explicit: IBM Consulting has launched a dedicated Google Cloud Practice, built around deploying agentic AI solutions on Google's Gemini platform for large enterprises.

The partnership, announced last week, pairs thousands of Google Cloud-certified IBM consultants and engineers with industry-specific AI agents developed through IBM's Consulting Advantage platform. The companies are calling it a "multi-billion-dollar opportunity" — a phrase typically reserved for investor calls, not press releases.

## What IBM Is Actually Selling

The core offering is not a new product. It is a service layer. IBM will help enterprises deploy Gemini-powered AI agents, modernise legacy environments, and manage hybrid cloud landscapes that span on-premises systems and multiple cloud providers. Mohamad Ali, who runs IBM Consulting, framed it bluntly: "Enterprises are facing one of the most complex modernization cycles in decades."

That complexity is IBM's business model. Most Fortune 500 companies run on a tangle of SAP, Oracle, mainframe, and bespoke systems that cannot simply be replaced. They need to be migrated, wrapped, or augmented — work that requires deep industry knowledge and a tolerance for unglamorous plumbing. IBM has 160,000 consultants who do this for a living. Google has the AI models but not the enterprise delivery apparatus. The marriage is logical.

This is not IBM's first hyperscaler partnership. Last month, IBM announced that its Enterprise Advantage agentic AI platform was generally available on Amazon Web Services. The company is positioning itself as model-agnostic — a Switzerland of enterprise AI — which may be the only sustainable strategy for a company that chose not to build its own frontier model.

## Krishna's Quantum Hedge

IBM's stock has surged nearly 40 per cent since late May, driven partly by a $1 billion Department of Commerce grant for a quantum chip foundry and partly by a $10 billion five-year quantum investment commitment. HSBC recently valued IBM's quantum business alone at $35 to $51 billion. Krishna has been explicit that quantum will solve problems AI cannot: "AI is great at predicting a bit of the future. Quantum computes the future."

The dual bet — agentic AI consulting today, quantum advantage by 2029 — gives Krishna a narrative that spans both the immediate enterprise modernisation cycle and the longer-horizon technology shift. It is a more nuanced story than pure-play AI companies can tell, and investors are responding.

## The Indian Angle Is Structural

IBM employs over 150,000 people in India, making it one of the country's largest private-sector technology employers. The Google Cloud Practice will generate significant work for IBM's India delivery centres, particularly in Bengaluru and Hyderabad, where the bulk of enterprise consulting work is executed. For Indian IT professionals — whether in India or on H-1B visas at IBM's US offices — the partnership signals continued demand for cloud migration and AI integration skills.

More broadly, Krishna's tenure as CEO has been a masterclass in corporate reinvention by an Indian-origin leader. He took over a company in secular decline, shed the managed infrastructure business (now Kyndryl), acquired HashiCorp and Confluent, and bet decisively on hybrid cloud and AI. IBM's market capitalisation has roughly doubled since he became CEO. For the Indian diaspora, Krishna's story is a quiet but significant data point: the era of Indian-origin CEOs in Big Tech is producing not just stewardship, but transformation."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Arvind Krishna's IBM Just Bet on Google's AI. The Multi-Billion-Dollar Play Is Enterprise Plumbing.",
    "subheadline": "IBM Consulting launches a dedicated Google Cloud Practice to deploy Gemini-powered AI agents across legacy enterprise systems — and it may be the company's most important move since shedding Kyndryl.",
    "slug": make_slug("ibm-arvind-krishna-google-cloud-agentic-ai-enterprise"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "IBM employs 150K+ in India; Google Cloud Practice generates work for Bengaluru/Hyderabad delivery centres; Krishna's reinvention of IBM is a significant Indian-origin CEO transformation story; H-1B implications for cloud/AI consulting roles",
    "tags": ["ibm", "arvind-krishna", "google-cloud", "agentic-ai", "enterprise", "indian-ceo"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/ibm-stock-rises-google-cloud-partnership-agentic-ai/"},
        {"name": "Barchart", "url": "https://www.barchart.com/story/news/32746655/as-ibm-unlocks-a-multi-billion-dollar-opportunity-with-google-the-stock-is-a-buy"},
        {"name": "IBM Newsroom", "url": "https://newsroom.ibm.com/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg",
    "image_caption": "IBM CEO Arvind Krishna at a company event in 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ─────────────────────────────────────────────
# ARTICLE 3: The Tokenpocalypse
# ─────────────────────────────────────────────

art3_body = """Uber burned through its entire annual AI budget in four months. GitHub just shifted Copilot to usage-based token billing, prompting developers to coin a new term: the Tokenpocalypse. And Goldman Sachs estimates that global token consumption will increase twenty-four-fold by 2030, to roughly 120 quadrillion tokens per month.

The enterprise AI cost crisis is no longer hypothetical. It is showing up in CFO reports, developer Slack channels, and procurement spreadsheets — and it has particular implications for the Indian tech workforce that builds and maintains much of the world's software.

## What Changed

For two years, AI coding assistants operated under a simple bargain: pay a flat monthly subscription, get unlimited AI help. GitHub Copilot cost $10 per month for individuals and $19 for businesses. The economics never worked — Microsoft was subsidising inference costs to drive adoption — but nobody complained while the subsidy lasted.

That era ended this month. GitHub's new pricing model charges by token consumption, including input, output, and cached tokens. Agentic coding tasks — where AI reads large contexts, iterates over entire codebases, retries failed attempts, and calls external tools — consume roughly a thousand times more tokens than simple chat interactions, according to a University of Michigan and Stanford study published in April. A single agentic coding task averages 4.17 million tokens and costs $1.86.

Scale that across a 500-person engineering team making dozens of AI-assisted commits per day, and the numbers become uncomfortable quickly.

## Uber's Budget Blowout

Uber's experience is the most vivid case study. According to The Information, employees consumed enough AI services to exhaust the company's annual AI budget allocation within four months. The company had rolled out AI tools across engineering, operations, and customer support without usage caps — a common pattern at tech companies that prioritised adoption speed over cost governance.

The problem is structural, not behavioural. Agentic AI systems are inherently expensive because they consume tokens at every step of multi-step workflows: reading context, generating plans, executing tasks, evaluating results, and retrying failures. As AI moves from a chatbot in a sidebar to an autonomous agent that can write, test, and deploy code, the token bill follows an exponential curve.

## Why Indian Tech Workers Should Care

The Tokenpocalypse lands hardest on three groups — and Indian engineers are disproportionately represented in all three.

**Enterprise engineering teams.** At companies like Google, Microsoft, Amazon, and Meta, where tens of thousands of Indian-origin engineers work on H-1B and L-1 visas, AI coding tools have become integral to daily workflow. If companies respond to cost pressure by restricting tool access — limiting Copilot to senior engineers, capping monthly token budgets, or downgrading to cheaper but less capable models — productivity gains could evaporate for the workers who rely on them most.

**Indian IT services firms.** TCS, Infosys, Wipro, and HCL Tech have been aggressively integrating AI tools into their delivery processes, promising clients faster turnaround and lower headcount per project. Token costs flow directly to project margins. A services firm billing $50 per hour for a developer whose AI tools cost $200 per day in tokens faces a fundamental arithmetic problem. The sector's AI productivity narrative depends on inference costs declining faster than usage grows — a bet that is currently going the wrong direction.

**Open-source model migration.** As Gizmodo reported, some developers have already resorted to using free chatbots — including Chipotle's customer service AI — to bypass expensive proprietary models. The more rational response is migration to open-source models like Meta's Llama or Alibaba's Qwen, which can run on private infrastructure at a fraction of the token cost. Indian engineers and IT firms with the skills to deploy, fine-tune, and operate open-source models have a structural advantage in this shift.

## The Subsidy Era Is Over

The fundamental tension is simple. AI companies need revenue to justify their valuations — OpenAI just filed for an IPO, Anthropic is preparing one — and flat-rate subscriptions at below-cost pricing are not a path to profitability. Token-based pricing is the honest model, but it exposes the true cost of AI at scale.

For Indian tech workers, the message is clear: the tools are not getting cheaper. The question is whether you are on the side of the cost curve that benefits from AI, or the side that absorbs it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The Tokenpocalypse Is Here. Indian Engineers Are on the Front Line.",
    "subheadline": "GitHub's shift to token-based billing and Uber's AI budget blowout signal the end of subsidised AI coding tools — with outsized implications for Indian tech workers and IT services firms.",
    "slug": make_slug("tokenpocalypse-ai-coding-cost-crisis-indian-engineers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian H-1B engineers at FAANG rely heavily on AI coding tools now facing cost pressure; Indian IT services firms (TCS, Infosys, Wipro) face margin squeeze from token costs; open-source model deployment skills become structural advantage for Indian engineers",
    "tags": ["ai-costs", "github-copilot", "tokenpocalypse", "indian-engineers", "h1b", "it-services"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "TechCrunch", "url": "https://techcrunch.com/podcast/is-this-the-dawn-of-the-tokenpocalypse/"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/article/what-is-ai-tokenomics-uber-ai-spending"},
        {"name": "Gizmodo", "url": "https://gizmodo.com/big-tech-is-quietly-admitting-that-if-it-wants-to-sell-people-on-ai-it-better-be-cheap/"},
        {"name": "BusinessWire (Codestrap/arXiv study)", "url": "https://www.businesswire.com/news/home/20260609005086/en/Codestrap-Redefines-Architecture-of-Agentic-Work"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6424583/pexels-photo-6424583.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "A software developer working at a screen — the AI tools they rely on are about to get expensive",
    "image_attribution": "Pexels",
    "body": art3_body,
}

# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
