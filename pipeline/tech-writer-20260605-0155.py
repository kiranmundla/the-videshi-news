#!/usr/bin/env python3
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Just Raised $85 Billion in a Single Week. It's the Largest Tech Equity Offering Ever.",
        "subheadline": "Alphabet's oversubscribed capital raise, anchored by a $10 billion Berkshire Hathaway bet, will fund $180 billion in AI infrastructure spending this year alone.",
        "slug": make_slug("alphabet-85-billion-equity-raise-sundar-pichai-ai-infrastructure"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Sundar Pichai, the IIT Kharagpur alumnus who runs the most consequential AI company in the world, is staking an unprecedented sum on infrastructure that will employ thousands of Indian engineers. Google Cloud's $460 billion backlog means years of enterprise AI work ahead — much of it built and maintained by the Indian talent pipeline that already dominates Google's engineering ranks.",
        "tags": ["alphabet", "sundar-pichai", "google", "ai-infrastructure", "berkshire-hathaway", "equity-raise"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Alphabet Investor Presentation", "url": "https://blog.google/alphabet/investor-presentation-june-2026/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/pinterest-ibm-ai-deals-amazon-google"},
            {"name": "The Information", "url": "https://www.theinformation.com/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Sundar Pichai, CEO of Google and Alphabet, in 2023",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When Alphabet announced an $80 billion equity raise on Monday, Wall Street treated it as the opening bid. By the time the underwritten portion closed, investors had oversubscribed the offering, pushing the total to roughly $85 billion — the largest equity capital raise in technology history.

The headline number is staggering, but the signal underneath it is what matters. Sundar Pichai, the Chennai-born CEO who has run Google since 2015, is making the single biggest infrastructure bet any technology company has ever placed in peacetime. And the money is going almost entirely into one thing: AI compute.

## The Numbers Behind the Bet

Alphabet expects to spend between $180 billion and $190 billion on capital expenditure in 2026. That is six times its 2022 CapEx of $31 billion and double last year's figure. Next year, the company says the number will "significantly increase" again. The equity raise, alongside operating cash flow and debt issuances, will fund this expansion.

The demand side justifies the ambition. Google Cloud's backlog nearly doubled quarter-over-quarter to more than $460 billion. Revenue grew 63% year-over-year in Q1. Across the company, Alphabet added $63 billion in revenue over the trailing twelve months, pushing total annual revenue past $400 billion.

"We are experiencing strong demand for our AI solutions and services from enterprises and consumers, at levels that are meaningfully exceeding our available supply," Pichai told investors.

## Berkshire's Quiet Vote of Confidence

Warren Buffett's Berkshire Hathaway put up $10 billion — a notable endorsement from an investor historically sceptical of technology valuations. Berkshire joining a growth-stage tech capital raise is unusual enough to merit its own reading: the Omaha firm sees Alphabet's AI infrastructure as closer to a utility investment than a speculative bet.

The oversubscription from institutional investors suggests Berkshire was not alone in that assessment. The original $30 billion underwritten tranche ballooned to roughly $35 billion in allocations.

## What This Means for Indian Tech Professionals

The practical consequence of $180 billion in infrastructure spending is thousands of new engineering, cloud architecture, and AI research positions. Google already employs more Indians in senior technical roles than any other Western technology company. Its Hyderabad and Bangalore campuses are among its largest outside the United States.

Pichai's investor presentation highlighted that 8.5 million developers now build with Google's AI models monthly, and the company processes 3.2 quadrillion tokens per month — up from 9.7 trillion just two years ago. That 300-fold increase in compute demand directly translates into sustained hiring for the engineers who build, train, and serve these models.

For the estimated 300,000-plus Indian professionals working at Alphabet globally, the raise signals job security in a year when other Big Tech firms have pulled back. For NRI investors, Alphabet's growth trajectory — 22% revenue growth, 30% operating income growth — offers a counterpoint to the broader semiconductor selloff triggered by Broadcom's guidance miss this week.

The IIT Kharagpur graduate who once joined Google as a product manager is now deploying more capital than most sovereign wealth funds. The scale of the bet reflects a conviction that AI infrastructure will be as foundational to the next decade as cloud computing was to the last — and that the Indian talent pipeline will be central to building it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nikesh Arora's Palo Alto Networks Hit $3 Billion in Quarterly Revenue. AI Is the Reason.",
        "subheadline": "The former Google executive's cybersecurity empire posted 31% revenue growth, tripled its AI security customer base, and raised guidance — then watched the stock drop 6%.",
        "slug": make_slug("palo-alto-networks-q3-earnings-nikesh-arora-ai-security"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Nikesh Arora is the highest-profile Indian-origin CEO in cybersecurity, running a $242 billion company from Santa Clara. His success story — from Uttar Pradesh to Google's chief business officer to Palo Alto Networks CEO — is a template for Indian executives moving beyond traditional software into vertical leadership. The AI security market he is building will require thousands of Indian-origin security engineers and consultants who already dominate the cybersecurity workforce at major enterprises.",
        "tags": ["palo-alto-networks", "nikesh-arora", "cybersecurity", "ai-security", "earnings", "prisma-airs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Zacks Investment Research", "url": "https://www.zacks.com/stock/news/2931787/palo-alto-networks-q3-earnings-and-revenues-surpass-estimates"},
            {"name": "CoinCentral", "url": "https://coincentral.com/palo-alto-networks-panw-stock-drops-6-after-strong-earnings/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/news/palo-alto-networks-raises-2026-forecast-as-ai-cybersecurity-demand-accelerates"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Nikesh_Arora_TechCrunch_Disrupt_2015.jpg",
        "image_caption": "Nikesh Arora, CEO of Palo Alto Networks, at TechCrunch Disrupt",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Palo Alto Networks crossed the $3 billion quarterly revenue mark for the first time, and the architect of that milestone is a man who spent his formative years in Ghaziabad before becoming one of the highest-paid executives in American technology.

Nikesh Arora, the company's CEO since 2018, delivered fiscal third-quarter results this week that beat Wall Street expectations on every metric that matters. Revenue rose 31% year-over-year to $3.0 billion. Earnings came in at 85 cents per share, clearing the consensus estimate of 81 cents. And the forward guidance — full-year revenue of $11.42 billion, implying 24% annual growth — was lifted above what analysts had modelled.

The stock still fell 6% in after-hours trading. When you are priced for perfection, beating perfection by a modest margin is apparently insufficient.

## The AI Security Thesis Is Working

The headline buried in the earnings release was not revenue. It was Prisma AIRS, Palo Alto Networks' AI security platform. Customer count tripled from roughly 100 in the prior quarter to approximately 300. In an industry where enterprise sales cycles typically measure in quarters, tripling adoption in three months is an acceleration that suggests real pull rather than vendor push.

Arora has been making the case for over a year that the explosion in enterprise AI deployments — agents, models, cloud-native applications — creates an entirely new attack surface that legacy cybersecurity tools cannot protect. Every company deploying a Gemini agent or fine-tuning an internal LLM needs security controls specifically designed for AI workloads. That is the market Prisma AIRS targets.

"Customers are seeking broader platforms that can help them manage threats across several parts of their technology systems," management noted. Next-Generation Security annual recurring revenue climbed to $8.13 billion, up 60% year-over-year. Remaining performance obligations hit $18.4 billion, up 36%.

## The Financial Discipline

For a growth company posting 31% top-line expansion, the cash generation is notable. Adjusted free cash flow was $910 million in the quarter, pushing the trailing twelve-month FCF margin to 38.5%. Arora has told analysts that a 40% free cash flow margin by 2028 is within reach. At the projected $15.6 billion in fiscal 2028 revenue, that would translate to roughly $6.2 billion in annual free cash flow.

The company's acquisition strategy has been aggressive but disciplined. The integration of CyberArk — rebranded as "Idira" for identity security — is progressing ahead of schedule. Oppenheimer raised its price target to $350, the highest on the Street, citing strong renewal activity and no observable churn from the acquisition.

## What Indian Cybersecurity Professionals Should Know

Palo Alto Networks employs thousands of engineers in India, primarily in Bangalore. The AI security wave Arora is riding creates specific demand for Indian professionals with dual expertise in AI/ML systems and security architecture — a skill combination that is relatively scarce and commands premium compensation.

For NRI investors, PANW's fiscal 2026 trajectory offers an interesting contrast to the pure-play semiconductor companies. While Broadcom dropped on guidance concerns and NVIDIA trades on supply chain anxiety, Palo Alto Networks is selling into the inevitable downstream consequence of the AI buildout: the need to secure everything being built. That demand curve does not depend on chip supply cycles.

Arora has taken a company that was a firewall vendor when he arrived and turned it into the most valuable pure-play cybersecurity firm on the planet, worth $242 billion. The Ghaziabad-to-Santa-Clara pipeline has produced another durable franchise."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Arvind Krishna's IBM Just Partnered With Google Cloud on Agentic AI. The $1 Billion Quantum Grant Helps Too.",
        "subheadline": "IBM and Google are building industry-specific AI agents for banking, healthcare, and government — while a Department of Commerce grant will fund America's first quantum chip foundry under IBM's roof.",
        "slug": make_slug("ibm-google-cloud-agentic-ai-partnership-arvind-krishna-quantum"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Arvind Krishna, the IIT Kanpur alumnus who has led IBM since 2020, is positioning the company at the centre of two transformational bets — agentic AI and quantum computing. IBM's consulting arm employs tens of thousands of Indian-origin professionals globally, and the new Google Cloud Practice will create substantial demand for engineers who can build enterprise AI agents. For Indian IT professionals at TCS, Infosys, and Wipro watching the consulting landscape shift, IBM's play is both a competitive threat and a career signal: the premium work is moving to AI agent deployment.",
        "tags": ["ibm", "arvind-krishna", "google-cloud", "agentic-ai", "quantum-computing", "enterprise-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Morningstar", "url": "https://www.morningstar.com/news/dow-jones/2026060410627/google-ibm-form-enterprise-ai-partnership"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/ibm-stock-google-agentic-ai-partnership/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/pinterest-ibm-ai-deals-amazon-google"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg",
        "image_caption": "Arvind Krishna, Chairman and CEO of IBM, in 2025",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Two announcements from IBM this week, taken together, tell a coherent story about where Arvind Krishna is steering the 114-year-old technology company. The first was a strategic partnership with Google Cloud to build and deploy enterprise AI agents. The second was a $1 billion Department of Commerce grant to build a quantum chip foundry. Both bets have the same underlying logic: IBM wants to own the infrastructure layer that enterprises cannot avoid.

## The Google Cloud Play

IBM and Google Cloud announced on Thursday the launch of a new Google Cloud Practice within IBM Consulting. The structure is straightforward: thousands of Google Cloud-certified IBM consultants will design, build, and govern enterprise-grade AI agents directly on Google's platform, using Google's Gemini models as the foundation.

IBM is calling it a "multi-billion-dollar opportunity." The agents will target banking, government, retail, telecommunications, energy, insurance, and life sciences — sectors where IBM's consulting relationships are deepest and where AI adoption has been slower than in consumer technology.

The partnership builds on IBM's Consulting Advantage platform, an AI-powered delivery system that helps IBM's own teams work faster. Combined with Google Cloud's Gemini Enterprise Agent Platform, the idea is to move clients from AI pilots — which IBM has observed stalling across industries — to production deployments with governance and compliance controls baked in.

"Enterprises are facing one of the most complex modernisation cycles in decades," said Mohamad Ali, head of IBM Consulting. The subtext is more pointed: most Fortune 500 companies have experimented with AI but have not scaled it into core operations. IBM and Google are betting they can be the bridge.

## The Quantum Foundry

Separately, IBM has secured a $1 billion letter of intent from the Department of Commerce to build a quantum chip foundry — the first dedicated quantum semiconductor manufacturing facility in the United States. The grant, part of the Trump administration's broader industrial policy push, has energised IBM's stock, which has surged nearly 40% since May 21.

Quantum computing remains years away from commercial disruption, but the foundry investment positions IBM as the physical manufacturer of quantum hardware, not just a researcher. For a company that exited the semiconductor business a decade ago, it is a quiet return to chipmaking through a door that did not exist before.

## The Krishna Playbook

Arvind Krishna, who earned his electrical engineering degree from IIT Kanpur before joining IBM in 1990, has spent his tenure as CEO on a single strategic question: what does a post-mainframe IBM look like? His answer has been hybrid cloud (via the $34 billion Red Hat acquisition) and AI consulting (via Watsonx and now the Google partnership).

The Google deal is notable because IBM is not building its own frontier models. It is building the deployment and governance layer around someone else's models — a pragmatic bet that the consulting margin on AI agents will be larger and more durable than the model margin itself. Red Hat OpenShift is now available directly in the Google Cloud Console, tightening the integration between IBM's infrastructure tooling and Google's cloud.

## What This Means for Indian IT

The immediate read for Indian IT professionals is competitive. IBM's consulting arm competes directly with TCS, Infosys, and Wipro for enterprise transformation contracts. A Google-partnered IBM with pre-built AI agents and cloud-certified engineers raises the bar for what Indian IT services firms need to offer.

The opportunity side is equally real. IBM employs roughly 100,000 people in India — its largest workforce outside the United States. The new Google Cloud Practice will need engineers who can build agentic AI systems, integrate Gemini models into regulated environments, and manage hybrid cloud deployments. That skill profile maps precisely to the Indian engineering talent that already fills IBM's India labs.

Krishna's week — a multi-billion-dollar AI partnership and a billion-dollar quantum grant — is the kind of one-two punch that makes Wall Street reconsider a company it had written off. For the IIT Kanpur alumnus running it, the thesis is simple: be indispensable to the enterprises that are building with AI, even if you are not building the AI itself."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
