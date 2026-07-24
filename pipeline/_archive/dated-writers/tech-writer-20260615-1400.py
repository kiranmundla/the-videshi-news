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

PEXELS = "Pexels"

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Court Is Deciding Whether Your AI Assistant Is Allowed to Shop for You",
        "subheadline": "Amazon v. Perplexity, argued before the Ninth Circuit, turns on a 1986 hacking law — and the answer will govern every AI agent built by an Indian engineer in the Valley.",
        "slug": make_slug("amazon-perplexity-ninth-circuit-ai-agent-cfaa-precedent"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin founders and engineers are building the agentic-AI products at the heart of this case, and the ruling will set the rules for every assistant they ship to American consumers.",
        "tags": ["ai", "agentic-ai", "perplexity", "amazon", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — US appeals court tests limits of 1986 computer fraud law", "url": "https://www.reuters.com/legal/litigation/"},
            {"name": "Reuters — Amazon wins order blocking Perplexity's AI shopping agent", "url": "https://www.reuters.com/technology/"},
            {"name": "Search Engine Journal — The CFAA case that decides whether AI agents can visit your website", "url": "https://www.searchenginejournal.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7620626/pexels-photo-7620626.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "image_caption": "A shopper browses an online store on a laptop, the kind of logged-in account at the center of the Amazon-Perplexity dispute",
        "image_attribution": PEXELS,
        "body": """A three-judge panel of the Ninth U.S. Circuit Court of Appeals sat in Seattle last week to chew on a question that sounds almost philosophical but carries very real money behind it: when you tell an AI assistant to buy something on Amazon, who exactly is doing the shopping — you, or the machine?

The case is *Amazon.com Services LLC v. Perplexity AI Inc.* Amazon sued the Aravind Srinivas-led startup in November, accusing its Comet browser and built-in AI agent of logging into customers' Amazon accounts and placing orders without the retailer's permission. Amazon's weapon is the Computer Fraud and Abuse Act of 1986, a law written when "hacking" meant a teenager with a modem, long before anyone imagined software that could reason and act on a user's behalf.

In March, U.S. District Judge Maxine Chesney sided with Amazon, granting a preliminary injunction that blocked Comet from accessing Amazon's logged-in pages. She found Amazon had presented "strong evidence" that Perplexity's agent reached its systems unlawfully. A week later the Ninth Circuit paused that order while it heard the appeal — which is what brought the two sides to Seattle.

**The argument that matters**

Perplexity's pitch is blunt: a CFAA theory built for intruders is "a fundamental misfit" for an AI agent that visits a website under a user's explicit authorization, using that user's own credentials. The company argues Amazon is really trying to block its customers from using a competing AI, and put it more colorfully in earlier filings — agents "don't have eyeballs to see the pervasive advertising Amazon bombards its users with."

The judges, by accounts of the hearing, were not interested in slogans. They pressed on the mechanics: was it the AI or the human who "accessed" Amazon under the statute, and did Perplexity have the "intent" the law requires? Those are narrow doctrinal questions, but the answers will ripple far beyond one shopping cart.

**Why this is bigger than Amazon**

This is the first federal appellate test of what lawyers are calling "agent-as-visitor" rights. Every retailer, booking site, bank portal and SaaS product is about to face the same question: when a human delegates a logged-in task to an AI, is that authorized access or trespass? Whatever the Ninth Circuit decides becomes the template, and most of the industry will be litigating versions of it within a year.

**The diaspora angle**

This is not abstract for Indian Americans — it cuts close to home twice over. Perplexity is run by Srinivas, a Chennai-born IIT Madras and Berkeley graduate who left OpenAI to build the company, and India is central to his strategy: an Airtel bundling deal pushed Perplexity to the top of India's app charts, and the company has leaned on Indian engineering talent and a planned lower-priced India tier.

More broadly, agentic AI — software that books, buys and fills forms on your behalf — is being built disproportionately by Indian-origin engineers across the Bay Area, from frontier labs to startups. If the court rules that an AI agent acting on a user's instruction is an unauthorized intruder, it constrains an entire product category that thousands of these engineers are shipping. If it rules the other way, it hands them a green light to embed agents into shopping, travel and finance at scale.

For an NRI in New Jersey who already lets an assistant manage a calendar, the practical stakes are immediate: the difference between an AI that can complete a purchase and one that hits a legal wall at the checkout page. For the engineer in Sunnyvale who codes those features, it is the difference between a roadmap and a liability memo.

**What's next**

The Ninth Circuit's ruling is not expected immediately; appellate decisions of this weight often take months. Until then, the administrative stay means Comet can keep operating on Amazon, but the underlying injunction looms. Srinivas, for his part, has said Perplexity is still targeting a 2028 IPO regardless of how the case or rival listings shake out — a reminder that the company is betting the legal question breaks its way. The judges in Seattle will decide whether that bet, and an entire category of software, has a future inside America's largest store."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Cognizant Slows Its India Listing Even as It Sets Aside $270 Million to Cut Jobs",
        "subheadline": "The New Jersey-based IT giant says its India share sale is still 'ongoing' amid market volatility — while Project Leap reshapes a workforce that is overwhelmingly Indian.",
        "slug": make_slug("cognizant-india-listing-delay-project-leap-layoffs-ai"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cognizant's workforce is heavily Indian on both sides of the ocean, so its layoffs, fresher hiring reset, and India listing plans land directly on diaspora families and H-1B holders.",
        "tags": ["cognizant", "it-services", "layoffs", "h1b", "indian-tech", "ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine — Cognizant's India listing plans go slow amid market volatility and AI impact", "url": "https://www.thehindubusinessline.com/info-tech/"},
            {"name": "CRN — Cognizant sets aside $270 million for layoffs in 'Project Leap'", "url": "https://www.crn.com/"},
            {"name": "DQIndia — Cognizant to cut 4,000 jobs under Project Leap", "url": "https://www.dqindia.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3861967/pexels-photo-3861967.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "image_caption": "Software engineers at work — Cognizant employs hundreds of thousands across India and the United States",
        "image_attribution": PEXELS,
        "body": """Cognizant wants to be clear about one thing: it has not shelved its plan to list shares in India. It has just slowed it down.

In a statement reported June 15, a company spokesperson said Cognizant continues "to make progress and advance on our evaluation of a potential primary offering and secondary listing in India," and that "that process is ongoing." The careful phrasing comes against a backdrop of market volatility and a souring mood around IT-services valuations — the same forces that have pushed several India-bound technology firms to delay their public debuts over a valuation mismatch.

The Nasdaq-listed company, headquartered in New Jersey but built on Indian delivery centers, first floated the idea of an India listing as a way to bring its stock closer to the country where most of its employees actually work. The logic is sound; the timing is the problem. With the broader IT sector under pressure — Indian IT stocks have shed more than a quarter of their value this year on AI-disruption fears — a listing at a disappointing price would do more harm than good.

**Project Leap, and the human cost**

The listing caution sits awkwardly next to the other half of Cognizant's 2026 story: cutting jobs. When it reported first-quarter earnings in April, the company announced a restructuring program called Project Leap and said it expects to incur $200 million to $270 million in employee severance and personnel-related costs this year, with total restructuring costs of up to $320 million.

The program is pitched as a transformation, not just a downsizing. Cognizant plans to trim roughly 4,000 roles — about 1% of global headcount — concentrated in mid-level management, while simultaneously hiring around 20,000 freshers in 2026. CEO Ravi Kumar S has framed it as an "AI builder" strategy: thin out the middle, bring in cheaper early-career talent, and lean on an Anthropic-anchored partnership ecosystem to monetize agentic AI in regulated workflows.

Cognizant is far from alone. Bernstein singled it out alongside Accenture, Deloitte and Infosys as system integrators with deep Anthropic investments positioned to profit from agentic AI. And it joins Oracle, Amazon Web Services, Atlassian and Autodesk among firms cutting staff this year while pouring money into AI infrastructure. Even Cognizant's own chief AI officer, Babak Hodjat, has been skeptical of the narrative, telling Nikkei Asia that AI "becomes the scapegoat from a financial perspective" when companies over-hired and want to resize.

**Why the diaspora should read the fine print**

For Indian American families, Cognizant is not an abstraction — it is a household employer. Its workforce skews heavily Indian both in India's delivery hubs and across its U.S. operations, where a significant share of staff are on H-1B or L-1 visas. When a company like this announces severance reserves and a "reset" of its talent pyramid, the consequences land directly on diaspora kitchens: a mid-career manager in Dallas facing the 60-day grace-period clock if cut, or a recent graduate weighing a fresher role that pays less than what the same job commanded two years ago.

The dual strategy — fewer experienced hands, more freshers — also reshapes the classic NRI playbook. For two decades, the IT-services ladder was a reliable path from a campus in Hyderabad to a green card in suburban America. Project Leap signals that the middle rungs of that ladder are being sawed off, even as the bottom rung widens. The people most exposed are exactly the 4-to-12-year-experience professionals who form the backbone of the diaspora tech middle class.

**What's next**

Cognizant's India listing remains a "when, not if" in the company's telling, but the slowdown suggests it will wait for both market sentiment and IT valuations to recover before pulling the trigger. In the meantime, Project Leap's severance charges will flow through 2026, and the fresher hiring will test whether an AI-restructured services firm can grow on a leaner, younger base. For diaspora workers, the message is unsentimental: the AI transition inside India's IT giants is no longer a forecast — it is the payroll."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta's First AI Data Center in India Will Be Built — and Owned — by Reliance",
        "subheadline": "A 168 MW, seawater-cooled facility in Jamnagar deepens the Ambani-Zuckerberg alliance and plants Meta's AI infrastructure on Indian soil for the first time.",
        "slug": make_slug("meta-reliance-jamnagar-ai-data-center-india"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Meta building AI capacity inside India means faster, locally-hosted services for the diaspora's families back home — and a signal to NRI investors tracking the Reliance-Meta infrastructure bet.",
        "tags": ["meta", "reliance", "data-center", "ai-infrastructure", "indian-tech", "jamnagar"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Meta deepens partnership with Ambani's Reliance with AI data centre", "url": "https://www.reuters.com/technology/"},
            {"name": "OEM Update — Meta partners with Reliance to develop AI-enabled data centre in Jamnagar", "url": "https://www.oemupdate.com/"},
            {"name": "IndexBox — Meta and Reliance announce AI data center in Jamnagar, Gujarat", "url": "https://www.indexbox.io/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "image_caption": "Rows of servers in a data center, the kind of AI-ready facility Reliance will build for Meta in Jamnagar",
        "image_attribution": PEXELS,
        "body": """Meta is finally putting AI hardware on Indian ground — but it will not own the building. On June 10, the company announced a deal with Mukesh Ambani's Reliance Industries to develop a 168-megawatt, AI-ready data center in Jamnagar, Gujarat, Meta's first such facility in the country. Reliance designs, builds, powers and operates it; Meta leases the capacity and runs its services on top.

The structure is telling. Rather than buy land, fight for grid power and manage construction in an unfamiliar regulatory environment, Meta is renting infrastructure from a partner that already runs one of the world's largest data-center campuses next door to its flagship Jamnagar energy complex. Reliance handles the design, utilities, renewable generation, network services and day-to-day operations. Meta brings the AI workloads and, per some accounts, foots the energy and water bill.

**The Jamnagar logic**

The site choice is not sentimental — it is physics and economics. Jamnagar sits on the Gujarat coast, which lets the facility use seawater for cooling, one of the single largest operating costs for any data center. It draws on Reliance's captive renewable-power assets, sidestepping costlier and less reliable grid electricity. At 168 MW, the first phase matches the capacity of Meta's data center in Oregon and is designed to scale.

For Meta, the appeal is speed and risk transfer. India's data-center market is projected to nearly double to roughly $13 billion by 2034, and New Delhi has dangled a more than two-decade tax break for companies using local facilities — sweetened further by a Union Budget 2026 holiday for data centers stretching to 2047. Building from scratch would take years; leasing from Reliance gets Meta into the market now.

**A deepening alliance**

This is the latest chapter in a partnership that keeps widening. Meta invested $5.7 billion in Reliance's Jio Platforms in 2020. Last year the two formed a joint venture to build enterprise AI tools on Meta's Llama models, with an initial commitment of about ₹855 crore split 70-30 in Reliance's favor. The Jamnagar data center now adds physical infrastructure to a relationship that already spans connectivity, commerce and AI software.

It also fits a larger land grab. Reliance has committed roughly $110 billion and the Adani Group around $100 billion to position India as an AI hub, and U.S. hyperscalers — Amazon, Microsoft and Google among them — are racing to build local capacity. Just this week, Apple supplier Jabil and Adani announced a separate alliance to manufacture AI data-center hardware in India. The Meta-Reliance deal is one piece of a multi-hundred-billion-dollar buildout.

**Why it matters to the diaspora**

For NRIs, the immediate payoff is mundane but real: latency. When Meta runs AI features — from Instagram recommendations to WhatsApp business tools to Llama-powered apps — on servers inside India, those services get faster and more reliable for the family members back home that the diaspora stays connected to. Data localization rules under India's Digital Personal Data Protection Act also mean more Indian user data stays in India, a point that matters to diaspora users who shuttle between jurisdictions.

For the investor slice of the community, the deal is a data point in the Reliance thesis. Jio Platforms is IPO-bound, and Reliance's pivot from refining and retail toward digital infrastructure is exactly the story NRI investors tracking the stock have been pricing in. A built-to-suit, hyperscaler-grade facility with Meta as anchor tenant is the kind of recurring, dollar-linked revenue that strengthens that case. And for diaspora engineers, a wave of domestic AI infrastructure means more high-end cloud and ML roles inside India — a factor in the return-to-India calculus that more mid-career NRIs are quietly running.

**What's next**

Meta has not disclosed financial terms or a completion date, and similar lease agreements typically run five to ten years. The first 168 MW phase can be scaled if demand holds, and given the pace of India's AI buildout, it likely will. The bigger question is whether the lease model — global AI giant on top, Indian conglomerate underneath — becomes the default template for how Silicon Valley plants itself in India. On the evidence of Jamnagar, it already is."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
