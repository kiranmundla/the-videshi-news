#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "Qualcomm Wants Out of Your Pocket and Into the Data Center. The Bet Is on AI Inference.",
        "subheadline": "The chipmaker that put Snapdragon in nearly every Android phone is now chasing a $35 billion data-center market by 2031 — and Indian engineers across its design and India teams are central to the pivot.",
        "slug": make_slug("qualcomm-data-center-ai-pivot-35-billion-snapdragon"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Qualcomm's pivot into AI data-center silicon reshapes the career map for thousands of Indian-origin chip designers in San Diego and Hyderabad — and signals where the next wave of semiconductor hiring will land.",
        "tags": ["qualcomm", "semiconductors", "ai-chips", "data-center", "indian-tech", "snapdragon"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/qualcomm-ai-infrastructure-qcom-stock"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/QCOM/"},
            {"name": "CRN", "url": "https://www.crn.com/news/components-peripherals/qualcomm-hires-amd-pc-exec"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Rows of servers in a data center, the market Qualcomm is now targeting with AI inference chips",
        "image_attribution": "Pexels",
        "body": """For two decades, Qualcomm has been the company you never see but always use. Its Snapdragon processors hum inside most of the world's Android phones; its modems connect them to cellular networks; its patents collect a toll on nearly every handset shipped. It is one of the most quietly profitable arrangements in technology. And Qualcomm now wants to walk away from leaning on it.

The San Diego chipmaker is making an aggressive push into three markets it has long circled but never owned: data centers, automotive, and the internet of things. The most consequential of those is the data center, where Qualcomm is wading into a fight currently dominated by Nvidia, AMD, and Intel.

## The Numbers Behind the Pivot

J.P. Morgan analyst Samik Chatterjee put Qualcomm on a positive catalyst watch this month, projecting the company can build a data-center business generating over $3 billion by 2027 and $35 billion by 2031. He expects roughly 70% of Qualcomm's chip revenue to come from outside handsets by 2031 — a startling reversal for a firm where more than 66% of chip revenue still flows from phones.

Chatterjee raised his price target from $160 to $265 while keeping a neutral rating, a hedge that captures the mood around Qualcomm: the opportunity is real, the execution risk is steep. Wells Fargo separately lifted its target to $230. The company will lay out its long-term targets at an investor day on June 24.

The strategic logic is sound. The AI boom has split into two phases: training the giant models, which Nvidia dominates, and running them — inference — which is a far larger and more cost-sensitive market over time. Qualcomm's decades of work squeezing performance out of power-constrained phone chips is, in theory, exactly the expertise that inference at scale rewards. Efficiency, not raw horsepower, is the constraint.

## Why an Indian Engineer Should Care

Qualcomm is one of the largest employers of Indian-origin semiconductor talent in the United States, and its India design centers in Hyderabad, Bengaluru, and Chennai are among the company's biggest engineering hubs outside San Diego. A pivot of this scale is not just a stock-market story — it redraws the internal career map. Data-center silicon, custom Arm-based server CPUs, and AI accelerators are where the headcount and the promotions will flow. Phone-modem veterans will need to retool or relocate toward the new priorities.

That matters for the H-1B engineer weighing whether to stay at a maturing handset business or chase the frontier. It matters for the recent IIT graduate deciding between an Nvidia offer and a Qualcomm one. And it matters for the Indian fab ecosystem: if Qualcomm scales server chips, more of that design and validation work plausibly lands in its Indian centers, which already handle a disproportionate share of its core engineering.

Qualcomm has also been restocking its bench for the fight. It recently hired Jason Banta, a 23-year AMD veteran who ran AMD's PC business with OEMs, to lead global compute sales — a signal that the company is serious about pushing its Snapdragon X-series chips against Intel and AMD in laptops, the beachhead before the data center.

## The Risk

None of this is guaranteed. Qualcomm has tried to break into servers before — its Centriq chip effort in the late 2010s was quietly shelved. The data-center market is brutal, the incumbents are entrenched, and Nvidia's software moat around AI is the deepest in the industry. Qualcomm's shares have also been caught in the broader semiconductor pullback, shedding ground after Nvidia's RTX Spark announcement squeezed the PC-chip story.

For the diaspora professional, the read is simpler than the stock call. When a company this large reorients its entire revenue base, the people who position themselves at the new center of gravity tend to do well. The pocket is no longer where the growth is. The data center is — and Qualcomm has just told 50,000 employees, a large share of them Indian, where to point their careers."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's First Private Orbital Rocket Just Cleared Its Biggest Engine Test. Skyroot's Launch Window Is Open.",
        "subheadline": "A successful KALAM-1200 motor test puts Hyderabad's Skyroot Aerospace — now India's first space-tech unicorn — on the final approach to a maiden Vikram-1 flight that could rewrite who launches satellites for the world.",
        "slug": make_slug("skyroot-vikram-1-kalam-1200-test-private-orbital-launch"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "A private Indian company launching its own orbital rocket is a credibility marker NRIs have waited a generation for — and a live investment thesis as global funds like GIC and BlackRock pile into India's space sector.",
        "tags": ["skyroot", "isro", "space-tech", "vikram-1", "indian-startups", "spacetech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/skyroot-vikram-1-kalam-1200-motor-test/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/skyroot-india-first-space-tech-unicorn-vikram-1"},
            {"name": "Reuters", "url": "https://www.reuters.com/skyroot-1-billion-space-tech-startup-gic-sherpalo-blackrock"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Vikram-S_rocket%27s_Mission_Prarambh_%28cropped_wide%29.png/1280px-Vikram-S_rocket%27s_Mission_Prarambh_%28cropped_wide%29.png",
        "image_caption": "Skyroot Aerospace's Vikram-S rocket during Mission Prarambh, India's first private rocket launch",
        "image_attribution": "Wikimedia Commons",
        "body": """For decades, "Indian space program" meant one thing: ISRO, the state agency that put a probe around Mars on a shoestring budget and became a point of diaspora pride. The next chapter is being written by a startup. Skyroot Aerospace, founded in 2018 by two former ISRO engineers in Hyderabad, has just cleared one of the last technical hurdles before attempting India's first orbital launch by a private company.

ISRO confirmed this week that Skyroot successfully test-fired its KALAM-1200 motor, a critical propulsion milestone for the Vikram-1 rocket. The rocket's stages and nose cone have already been dispatched to the Satish Dhawan Space Centre at Sriharikota, and the company is in the final integration and launch-campaign phase. A maiden flight is targeted for the coming weeks.

## From ISRO Cubicle to Unicorn

Skyroot's rise has been fast. In May, the company raised $60 million at a $1.1 billion valuation, becoming India's first space-tech unicorn. The round was co-led by Singapore's sovereign wealth fund GIC and Silicon Valley's Sherpalo Ventures, with participation from BlackRock-managed funds, Playbook Partners, and Arkam Ventures. Ram Shriram — an early Google backer and Alphabet board member — is joining Skyroot's board.

That investor list is the story within the story. When GIC, BlackRock, and a sitting Alphabet director put money and time into a Hyderabad rocket company, it sends what the Indian Space Association's director general called "a strong signal to global investors" about the credibility of India's private space sector.

Vikram-1 is a three-stage, 23-meter rocket built with an all-carbon composite structure, capable of carrying payloads up to 350 kilograms into low Earth orbit. That puts it in direct competition with U.S. small-launch players like Rocket Lab and Firefly Aerospace. Founders Pawan Kumar Chandana and Naga Bharath Daka are betting that on-demand, low-cost small-satellite launches are a fast-growing global market — and that India can be the cheapest credible supplier.

## Why It Lands Differently for NRIs

For the Indian diaspora, space has always carried symbolic weight beyond the engineering. Chandrayaan, the Mars Orbiter Mission, Aditya-L1 — these were the stories NRIs forwarded to skeptical colleagues as proof of what India could build. A private company joining that club changes the texture of the pride: it is no longer just government achievement, but a venture-backed industry that diaspora investors and engineers can actually participate in.

That participation is increasingly literal. India recently wrote its first government cheques to private space startups through its IN-SPACe technology fund, and global capital is flowing in. For an NRI tracking where to deploy investment dollars or where to send an engineering resume, India's space sector has gone from a curiosity to a category in under two years.

## The Stakes — and the Shadow

The timing is not without pressure. ISRO suffered consecutive PSLV launch failures, including the loss of the PSLV-C62 mission carrying the DRDO's Anvesha satellite earlier this year. A clean Skyroot debut would offer a confidence boost for the broader Indian launch ecosystem at a moment when it badly needs one. A failure, conversely, would test investor patience in a sector that is still proving it can deliver.

Skyroot says the new funding will let it ramp Vikram-1's launch cadence, expand manufacturing, and develop Vikram-2, a one-tonne-class vehicle with an advanced cryogenic stage. But all of that hinges on the next few weeks. The hardware is at the pad. The engine has passed its test. India's private space age is one successful liftoff away from becoming real."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Salesforce Just Paid $3.6 Billion to Buy the Robot That Answers Your Support Tickets",
        "subheadline": "The acquisition of Fin — formerly Intercom — supercharges Benioff's Agentforce push and accelerates a shift that lands hardest on the Indian BPO and customer-support workforce.",
        "slug": make_slug("salesforce-fin-intercom-3-6-billion-agentforce-ai-agents"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Salesforce's bet on autonomous customer-service agents threatens the millions of Indian jobs built on call centers and IT support — even as it expands the AI engineering roles Indian talent is racing to fill.",
        "tags": ["salesforce", "ai-agents", "agentforce", "enterprise-saas", "automation", "indian-it"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Salesforce Newsroom", "url": "https://www.salesforce.com/news/press-releases/2026/06/15/salesforce-signs-agreement-to-acquire-fin/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/15/salesforce-acquires-ai-customer-service-platform-fin-for-3-6-billion/"},
            {"name": "Reuters", "url": "https://www.reuters.com/salesforce-buy-ai-agent-platform-fin-3-6-billion"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Salesforce_Tower_SF_2017.jpg/1280px-Salesforce_Tower_SF_2017.jpg",
        "image_caption": "Salesforce Tower in San Francisco, headquarters of the CRM giant now betting heavily on AI agents",
        "image_attribution": "Wikimedia Commons",
        "body": """Salesforce announced on Monday that it will acquire Fin — the customer-service AI company formerly known as Intercom — for roughly $3.6 billion. The deal is the clearest sign yet that the enterprise-software giant intends to win the race to replace human support agents with autonomous software, and it lands squarely on an industry the Indian diaspora knows intimately: customer support.

Fin's product is an AI agent that resolves customer queries end to end across live chat, email, WhatsApp, SMS, phone, and Slack. It runs on a proprietary model called Apex, purpose-built for support, which Fin claims outperforms top frontier models on resolution rates. Salesforce will fold Fin's team and technology into Agentforce, the platform it has been pushing as the centerpiece of its "agentic enterprise" pitch.

"Fin brings proven agent technology, a deep commitment to customer success, and an incredible AI team that will complement Agentforce," said Salesforce chair and CEO Marc Benioff. The transaction is expected to close in the fourth quarter of Salesforce's fiscal 2027, in early 2027.

## A Bet Made From a Position of Anxiety

The deal arrives with Salesforce stock down 37% in 2026, dragged by exactly the fear this acquisition is meant to answer: that AI-native upstarts like OpenAI and Anthropic will eat the traditional software business from below, and that goal-driven AI agents will erode the per-seat subscription model Salesforce was built on. Benioff's response is to buy the disruption rather than wait for it. Salesforce has already announced a $50 billion buyback and repurchased $25 billion of its own stock in a single quarter — a company spending aggressively to defend its narrative.

## Why This Is Personal for the Indian Diaspora

No country has more at stake in the automation of customer service than India. The country's IT services and business-process outsourcing sector — TCS, Infosys, Wipro, HCLTech, Cognizant, Genpact, and thousands of smaller firms — employs millions of people whose work includes precisely the support functions Fin's AI agent is designed to absorb. The "voice and chat support" job has been a reliable on-ramp to the middle class for a generation of Indians. Agentforce, now armed with Fin, is engineered to do that job without them.

This is not a distant threat. Just this month, Opendoor shut its entire India operation and replaced 250 workers with AI. Freshworks — itself an Indian-founded SaaS company — cut 500 jobs after AI took over half its codebase. The pattern is consistent: AI is hitting the support and routine-engineering layers first, and India's workforce is concentrated there.

## The Other Side of the Ledger

There is a more optimistic reading, and the diaspora sits on both sides of it. Building, deploying, and governing these AI agents requires a new class of engineers, and Indian talent is racing to fill those roles — at Salesforce's large India operations, at the U.S. headquarters staffed heavily by Indian-origin engineers, and across the enterprise-AI startups now hiring aggressively. The same wave that threatens the support agent in Pune creates the prompt engineer, the AI-ops lead, and the agent-orchestration architect in Bengaluru and the Bay Area.

For NRIs working in or invested in Indian IT services, the Salesforce-Fin deal is a data point that demands attention. The companies that have long sold India's labor cost advantage to Western clients are now competing against software that has no labor cost at all. The firms that move fastest to sell AI agents rather than headcount — TCS is already arming 50,000 workers with Claude — will survive the transition. The ones that don't will discover that Marc Benioff just spent $3.6 billion to make their core business obsolete."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
