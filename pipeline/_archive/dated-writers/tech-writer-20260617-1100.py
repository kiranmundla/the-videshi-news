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
        "headline": "Razorpay Files Quietly for a $600 Million IPO. The Valuation Cut Tells the Real Story.",
        "subheadline": "Bengaluru's biggest payments gateway is targeting a year-end listing at roughly $5–6 billion — well below its 2021 peak. For NRIs who shifted money into India's startup story, the reset is the point.",
        "slug": make_slug("razorpay-600-million-confidential-ipo-valuation-reset-nri-investors"),
        "category": "technology",
        "vertical": "fintech",
        "diaspora_angle": "NRIs weighing India's fintech boom now have a marquee payments listing to price — but at a valuation a third below its peak, Razorpay is a test of whether the diaspora's India bets have to be repriced too.",
        "tags": ["fintech", "indian-startups", "ipo", "upi", "razorpay"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-razorpay-files-ipo-papers-confidentially-2026-06-15/"},
            {"name": "Mint", "url": "https://www.livemint.com/market/ipo/razorpay-confidentially-files-draft-paper-for-ipo-looks-to-raise-600-million-report"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/razorpay-files-confidential-ipo-papers-to-raise-600-mn/"},
            {"name": "PYMNTS", "url": "https://www.pymnts.com/news/ipo/2026/indian-payment-fintech-razorpay-planning-600-million-ipo/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6406691/pexels-photo-6406691.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A hand holds a smartphone displaying a digital wallet, the rails on which India's payments fintechs like Razorpay run.",
        "image_attribution": "Pexels",
        "body": """Razorpay has done the thing Indian startups now do when they want to test the public markets without committing in public: it filed confidentially. A newspaper advertisement on Monday confirmed the Bengaluru payments company had submitted a pre-filed draft red herring prospectus to SEBI, with people familiar with the deal pegging the issue at roughly $600 million and the company at $5–6 billion. The bankers — Axis Capital, JPMorgan, Citi and Kotak Mahindra Capital — are lined up. The target is a debut by the end of 2026.

**The number that matters is the one going down.** Razorpay was valued at $7.5 billion in 2021, at the top of the last funding cycle. A listing at $5–6 billion is not a victory lap; it is a markdown of as much as a third. That is the real signal here, and it is one the Indian diaspora should read carefully. For five years, NRIs in the Bay Area and New Jersey have been told India's digital-payments story is a one-way bet. Razorpay is the first large, pure-play test of whether that story has to be repriced at the same time it goes public.

### What Razorpay actually is

Founded in 2014 by Harshil Mathur and Shashank Kumar, Razorpay is the plumbing behind a large slice of Indian online commerce. It lets businesses accept payments across cards, net banking, UPI, wallets and buy-now-pay-later, and earns a fee on each transaction. It has since pushed into payroll, lending and business banking — the familiar fintech move from a single product into a "full-stack" platform. For the year ending March 2025 it reported about $407 million in revenue and a $130 million net loss.

That loss is the catch. Razorpay is entering a market that has grown sceptical of unprofitable tech. It also made a costly housekeeping decision: it shifted its domicile back to India in 2025, reportedly at a price of around $150 million in taxes, precisely so it could list at home. The "reverse flip" is becoming standard for India-born companies that incorporated abroad and now want a domestic listing — and it is expensive.

### Why the diaspora should care

Three reasons, in plain terms.

First, **price discovery.** Many NRIs hold India exposure through funds, family offices, or direct angel and pre-IPO positions in exactly this class of company. Razorpay's listing will set a public benchmark for what a scaled, still-loss-making Indian fintech is worth in 2026. If it lists well, peer valuations firm up. If the issue shrinks or the debut is soft, the markdown spreads.

Second, **the IPO pipeline behind it.** Razorpay is not alone. Quick-commerce player Zepto has filed an updated prospectus to raise around ₹8,010 crore. PhonePe filed in January, secured approval, then deferred, citing market volatility. The order in which these come to market — and how they price — will shape how the diaspora's India allocation performs over the next year.

Third, **cross-border ambition.** Razorpay has set up a US team to build payments rails between America and India, and integrated its infrastructure with OpenAI's Codex. For NRIs who send money home, run businesses across both countries, or invest in the remittance-and-payments layer, the company is not an abstraction — it is increasingly part of the pipe their money travels through.

### The cautious trade

The confidential route is itself a tell. It lets Razorpay quietly gauge investor appetite and pick its moment rather than commit to a calendar in a jittery market. The signals to watch when it goes public: the final issue size, how much is fresh capital versus existing investors cashing out, and whether the roadshow firms up the $5–6 billion range or forces another trim.

For the NRI investor, the lesson is the same one the whole Indian startup cohort is learning at once. The growth story is intact; the prices that story commanded in 2021 are not. Razorpay going public at a haircut is not a failure. It is the market doing the repricing that private rounds spent two years avoiding — and it is happening in full view, which is exactly why it is worth watching."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Salesforce Just Paid $3.6 Billion for an AI Agent. It's Buying Insurance Against Its Own Obsolescence.",
        "subheadline": "Marc Benioff's acquisition of Fin — the company formerly known as Intercom — is the 15th deal in a year-long spree. For the tens of thousands of Indians who build on Salesforce, the agentic shift is now the job.",
        "slug": make_slug("salesforce-fin-intercom-3-6-billion-agentforce-ai-agents-indian-engineers"),
        "category": "technology",
        "vertical": "enterprise-ai",
        "diaspora_angle": "Salesforce employs and certifies a vast Indian-origin engineering and admin workforce; its pivot from selling software seats to selling autonomous AI agents reshapes the careers of every NRI who built a living on the platform.",
        "tags": ["ai", "salesforce", "enterprise-ai", "agentic-ai", "silicon-valley"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/salesforce-buy-ai-agent-platform-fin-about-36-billion-2026-06-15/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/salesforce-stock-fin-acquisition-ai-agent/"},
            {"name": "CoinCentral", "url": "https://coincentral.com/salesforce-crm-stock-rises-as-3-6-billion-fin-acquisition-announced/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8204312/pexels-photo-8204312.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Customer-service agents at work — the exact function Salesforce is now racing to automate with AI agents.",
        "image_attribution": "Pexels",
        "body": """Salesforce said on Monday it has agreed to buy Fin, the AI-agent company formerly known as Intercom, for about $3.6 billion. On paper it is a tuck-in: Fin makes an autonomous agent that handles customer-support queries across live chat, email, WhatsApp, SMS, phone and Slack, and it folds into Salesforce's Agentforce platform. Look closer and it is something more revealing — a company that built its empire selling software seats paying billions to make sure it owns the thing that might replace those seats.

### The spree, and what it's defending against

This is Salesforce's 15th acquisition since May 2025, and the strategy behind the buying binge is not subtle. Salesforce stock is down roughly 37% in 2026, and the bear case is brutally simple: if AI coding tools let companies build their own customer-service agents, why keep paying Salesforce per user, per month, forever? Wall Street has been pricing in that "SaaSpocalypse" — the fear that do-anything chatbots render traditional business applications obsolete.

Benioff's answer is to stop fighting the shift and to sell it instead. Fin is, as William Blair's analyst put it, "one of the best examples in the market of an incumbent software vendor disrupting and reinventing itself for the AI era." Fin's agent runs on its own model, Apex, which Salesforce claims outperforms top commercial models on support-resolution rates. Crucially, Fin prices on outcomes — you pay when a query is resolved — not on seats. That is the business model Salesforce is buying its way into.

> "We're excited to share that we just signed an agreement for Salesforce to acquire Fin for ~$3.6B... Fin started as Intercom 15 years ago."

The math underneath: Agentforce, Salesforce's existing AI platform, grew annual recurring revenue 20% to $1.2 billion in fiscal Q1 2027. The company beat earnings, reporting $11.13 billion in quarterly revenue, up 13.3%. The growth is real. The anxiety is also real — fifteen deals in thirteen months is not the behaviour of a company that feels safe.

### Why this lands on Indian desks

Few platforms employ and certify as many Indian-origin professionals as Salesforce. From engineers in San Francisco and Hyderabad to the enormous ecosystem of Salesforce admins, consultants and "trailblazers" — many of them NRIs who built entire careers on certifications — the platform is a livelihood, not just a tool. The pivot from seats to agents rewrites what that livelihood looks like.

When the unit Salesforce sells is an autonomous agent that resolves tickets on its own, the value of being the human who configures dashboards, writes workflows, or staffs a support queue changes. Some of that work compresses. Some of it moves up the stack — into designing, supervising and auditing fleets of agents, the people who decide what an agent is allowed to do and who catches it when it goes wrong. For Indian professionals on the platform, the safe assumption is the same one playing out at TCS, Wipro and Cognizant: the layer that AI automates first is the repetitive middle, and the premium shifts to whoever can govern the machines doing it.

### The H-1B overhang

There is a second-order effect worth naming. Salesforce, like Meta and Amazon, employs a large H-1B and L-1 workforce. Every dollar of efficiency the company extracts from agents is a dollar it does not need to spend on a seat — or, eventually, a headcount. In a year when more than 110,000 tech workers have already been cut globally and Indian visa holders are among the most exposed, "the software now does the support" is not an abstract product strategy. It is a question about whose jobs the agents are built to do.

### What to watch

The deal is expected to close in the fourth quarter of Salesforce's fiscal 2027. The signals that matter for the diaspora workforce: how aggressively Salesforce pushes outcome-based pricing into its installed base, whether Agentforce ARR keeps compounding, and how the company frames the human role around its agents. Benioff calls Fin "a natural fit." For the Indian engineer or admin reading the announcement from a cubicle in Santa Clara or a GCC in Bengaluru, the more useful question is whether they are building the agents — or being automated by them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Gave Companies 12 Hours to Patch a Hacked System. AI Is the Reason the Clock Got So Short.",
        "subheadline": "CERT-In's new blueprint says internet-facing 'crown jewel' systems with known exploited bugs should be fixed within half a day. The squeeze lands hardest on the Indian IT firms that run the diaspora's back office.",
        "slug": make_slug("cert-in-12-hour-patching-ai-cyberattacks-indian-it-firms-diaspora"),
        "category": "technology",
        "vertical": "cybersecurity",
        "diaspora_angle": "The Indian IT majors and GCCs subject to CERT-In's faster patching rules also run payroll, banking and healthcare systems for clients across the US and UK — meaning the diaspora's data and the firms that employ NRIs both sit inside this tightening window.",
        "tags": ["cybersecurity", "ai", "cert-in", "indian-tech", "data-security"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Register", "url": "https://www.theregister.com/2026/05/cert-in-12-hour-patching-ai-attacks/"},
            {"name": "The Hacker News", "url": "https://thehackernews.com/2026/cert-in-recommends-12-hour-patching.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/cybersecurity/us-shortens-cyber-fix-window-three-days-ai-threats-rise-2026-06-10/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5380603/pexels-photo-5380603.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Code displayed across monitors in a darkened operations room, where patching windows are now measured in hours, not weeks.",
        "image_attribution": "Pexels",
        "body": """India's Computer Emergency Response Team has issued a 38-page blueprint with one headline number: 12 hours. That is how fast CERT-In now says defenders should patch, mitigate, or remove exposure for known-exploited vulnerabilities on internet-facing or "crown jewel" systems — where feasible. For a standard critical bug on an internal system, the window stretches to a still-tight 24 hours. The old reality, where teams took weeks to roll out fixes, is officially over.

The reason CERT-In gives is blunt: artificial intelligence. "AI-assisted cyber exploitation reduces the time required for adversaries to identify, weaponize, and exploit vulnerabilities, exposed services, weak identities, insecure APIs, and misconfigured systems," the report reads. When attackers can use models to find a hole and write a working exploit in hours, defenders cannot afford to take days. India's move mirrors Washington's — the U.S. cyber agency CISA just compressed its own federal fix window to three days, citing the same AI pressure.

### Why a patching deadline is a diaspora story

On its face this is dry infrastructure policy. It is not. The organizations CERT-In is leaning on — the Indian IT majors, the global capability centers, the cloud and data-center operators on Indian soil — are the same firms that run the back office for a large chunk of corporate America and Britain. TCS, Infosys, Wipro, HCLTech and Cognizant process payroll, manage banking systems, and handle healthcare and insurance data for Western clients. A lot of that runs through Indian operations now governed by a 12-hour clock.

So when an NRI in New Jersey wonders who is guarding the systems holding their employer's customer data, or their own medical and financial records processed by an offshore vendor, the answer increasingly involves a CERT-In-regulated entity racing a half-day deadline. The tightening standard is, in effect, a tightening of the floor under the diaspora's own data.

### The operational squeeze on Indian IT

A 12-hour window is easy to write into a guideline and brutally hard to hit in practice. Patching is delayed by exactly the things enterprises cannot wave away: testing requirements, brittle legacy systems, fear of production downtime, and tangled third-party dependencies. Plenty of the systems Indian IT firms maintain for Western clients are decades-old and fragile. Telling an operations team to "patch, mitigate, or remove exposure within 12 hours" collides with the reality that one bad patch can take a bank's core system offline.

That gap is already spawning a market. Vendors are pitching "virtual patching" — AI-generated, application-specific shields that block exploitation while a real fix is tested — precisely to cover the dangerous interval between a bug's discovery and its remediation. For the Indian cybersecurity industry, and for the security engineers inside the IT majors, this is a hiring and skilling signal: continuous threat assessment, automated exposure reduction, and round-the-clock readiness are becoming table stakes, not premium add-ons.

### The AI-on-both-sides reality

The uncomfortable truth running through CERT-In's blueprint is that AI now sits on both sides of the fight. Attackers use it to compress attack timelines and generate convincing phishing and malware. Defenders use it to find flaws faster — Microsoft's record June Patch Tuesday, fixing more than 200 vulnerabilities, was driven in large part by AI-assisted vulnerability discovery. And AI systems themselves become targets, vulnerable to prompt injection, data leakage, jailbreaking and model theft.

For the diaspora professional, the practical takeaways are concrete. If you work in or near security at one of these firms, the pace of your job just changed. If you are a customer of Indian IT services, the new standard is, on balance, protective. And the personal hygiene CERT-In keeps repeating — strong unique passwords, multi-factor authentication, passkeys — matters more in a world where exploitation is automated and the window between flaw and attack is collapsing to almost nothing.

India set the clock at 12 hours because the attackers got faster. Whether the firms that run so much of the diaspora's digital life can actually hit that mark is the question the next breach will answer."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")

print(f"\n{len(inserted)} inserted:")
for h in inserted:
    print(" -", h)
