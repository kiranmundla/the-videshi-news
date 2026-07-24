#!/usr/bin/env python3
import json, os, uuid, re, requests, urllib.parse
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

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


articles = [
    # ── Article 1: Microsoft Build 2026 ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Has 48 Hours to Prove Microsoft's $190 Billion AI Bet Isn't Just Capex Theatre",
        "subheadline": "Build 2026 kicks off Tuesday with a new reasoning model, a Copilot 'super app,' and a joint NVIDIA deal to turn Windows into an AI runtime. For the 30,000-plus Indian engineers at Microsoft, the stakes are personal.",
        "slug": make_slug("satya-nadella-microsoft-build-2026-ai-copilot-nvidia"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Microsoft employs more than 30,000 engineers in India and is one of the largest H-1B sponsors in the US. Nadella's AI strategy directly shapes career trajectories for Indian tech workers across Hyderabad, Bengaluru, Redmond, and the Bay Area. The NVIDIA partnership could also shift demand toward new skill sets — local AI inference, agent frameworks, security primitives — that Indian engineers will need to master or risk obsolescence.",
        "tags": ["microsoft", "satya-nadella", "build-2026", "copilot", "nvidia", "ai-agents", "indian-tech-leaders"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Engadget", "url": "https://www.engadget.com/ai/how-to-watch-microsoft-build-2026-182505498.html"},
            {"name": "StockTwits / The Verge", "url": "https://stocktwits.com/news/article/microsoft-gears-up-to-unveil-new-ai-models-in-windows"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/32920981/dear-microsoft-stock-fans-mark-your-calendars-for-june-2"},
            {"name": "NVIDIA GlobeNewsWire", "url": "https://www.globenewswire.com/news-release/2026/06/01/nvidia-and-microsoft-reinvent-windows-pcs.html"},
            {"name": "Digit.in", "url": "https://www.digit.in/features/tech/microsoft-build-2026-5-ways-it-might-be-entirely-about-ai.html"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_attribution": "Wikimedia Commons",
        "body": """When Satya Nadella takes the stage at the Moscone Center in San Francisco on Tuesday morning, he will face a room full of developers who already know the pitch: AI changes everything. What they want to hear is what, specifically, it changes for them this week.

Microsoft's Build 2026 developer conference, running June 2–3, arrives at an awkward inflection point. The company has committed a staggering $190 billion in capital expenditure over the coming years to build out data centre infrastructure for AI workloads. Its stock is up roughly 3 per cent on the news. But investors remain skittish about when that spending converts into durable revenue, and a growing backlash against Windows 11's AI integrations has forced Microsoft to quietly pull Copilot from some applications and redesign its enterprise version.

## The Tuesday Menu

According to reports from The Verge, the keynote will feature at least three headline announcements. First, a new reasoning model from Microsoft's internal AI division — not OpenAI, whose partnership with Microsoft shifted to a more 'open' structure in April 2026. Second, a redesigned Copilot positioned as a 'super app' that consolidates AI capabilities across Office 365, coding workflows, and Windows system functions. Third, and perhaps most consequential, details on how Windows is adapting to new silicon like NVIDIA's RTX Spark.

That last item is worth lingering on. Earlier this week, NVIDIA unveiled RTX Spark, a chip bringing up to one petaflop of AI compute and 128GB of unified memory to consumer laptops. Microsoft and NVIDIA announced a joint initiative to build new Windows security primitives and an open-source runtime called OpenShell, designed to let AI agents run locally on PCs with full user control and privacy safeguards. The idea: your personal AI agent runs on your machine, not in a data centre, handling everything from cross-app workflows to local file search.

## Agent Mode, Not Just Chat Mode

The broader theme at Build will be what Microsoft calls the shift from 'AI as chatbot' to 'AI as agent.' Microsoft Agent 365, its enterprise management system for AI agents, hit general availability on 1 May 2026. GitHub Copilot is moving beyond auto-completion into debugging, code analysis, and proactive suggestion across the full development cycle. And the Copilot Runtime in Windows 11 is being positioned as a local AI inference layer — a bet that some workloads are better processed on-device than routed to the cloud.

Qualcomm CEO Cristiano Amon, speaking ahead of Computex, put it bluntly: '2026 is the year of agents. All of these devices today have been built for actions initiated by the user, not by the agents.' NVIDIA's Jensen Huang echoed the sentiment, noting that early adopters of its Vera CPU include OpenAI, Anthropic, and SpaceX.

## Why Indian Engineers Should Be Watching

Microsoft employs more than 30,000 people in India, with Hyderabad hosting its largest campus outside Redmond. The company has committed over ₹15,000 crore to Indian data centre infrastructure, with the first phase in Hyderabad expected to be operational this year.

For the tens of thousands of Indian engineers at Microsoft — and the broader ecosystem of H-1B workers at the company's US offices — Build 2026 is not an abstract developer conference. It is a signal about which skills will matter in six months. Agent frameworks, on-device inference, security primitives for AI runtimes, OpenShell integration: these are the competencies that will define the next hiring cycle. The shift from cloud-first to hybrid-local AI could also reshape the economics of Indian IT services firms like TCS, Infosys, and Wipro, which have built substantial Microsoft practices around cloud migration and Copilot deployment.

Nadella's keynote begins at 12:30 PM ET on Tuesday. For a Hyderabad-born engineer who once said 'I always knew I wanted to build things,' the next 48 hours are about proving that $190 billion buys something more than server racks."""
    },

    # ── Article 2: Salesforce Q1 FY2027 Earnings ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Salesforce Just Posted Its Best Quarter Ever. Indian IT Services Should Be Nervous.",
        "subheadline": "Revenue hit $11.13 billion, earnings per share surged 50 per cent, and the stock jumped 10 per cent — partly because its Anthropic stake is now worth $5 billion. But Agentforce's rise threatens the army of Indian consultants who built their careers on Salesforce implementations.",
        "slug": make_slug("salesforce-q1-fy2027-agentforce-indian-it-services"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Salesforce implementation and customisation is a multi-billion-dollar business for Indian IT services firms. TCS, Infosys, Wipro, and Cognizant collectively employ tens of thousands of Salesforce consultants. As Agentforce automates configuration, testing, and even coding, the traditional Salesforce implementation pyramid — with junior Indian developers at the base — faces structural compression. For NRIs working at these firms in the US, the question is whether upskilling into agentic AI architect roles can offset shrinking demand for manual CRM work.",
        "tags": ["salesforce", "agentforce", "indian-it-services", "ai-agents", "crm", "tcs", "infosys", "enterprise"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Futurum Group", "url": "https://futurumgroup.com/research-notes/salesforce-q1-fy-2027/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/anthropic-ipo-filing-ratifies-wall-streets-ai-obsession/"},
            {"name": "Forbes India", "url": "https://www.forbesindia.com/article/technology/inside-salesforces-agentic-ai-bet/"},
            {"name": "SendTech Times", "url": "https://stechtimes.com/salesforce-headless-360-ai-agents/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5380618/pexels-photo-5380618.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_attribution": "Pexels",
        "body": """Marc Benioff does not do understatement. 'This was an outstanding quarter for Salesforce — record revenue, record deals, and cash flow,' the CEO declared after the company reported Q1 FY2027 results that comfortably beat Wall Street expectations. Revenue came in at $11.13 billion, up 13 per cent year-on-year, against a consensus of $11.05 billion. Non-GAAP earnings per share hit $3.88, a 50 per cent jump. The stock surged 10 per cent on Monday, adding roughly $30 billion in market capitalisation in a single session.

Part of that rally was driven by a detail buried in the Anthropic coverage: Salesforce's early investment in the AI lab is now reportedly worth $5 billion, a windfall that was not lost on investors watching Anthropic file its S-1 the same day.

But the story that matters for India's $250 billion IT services industry is not Salesforce's balance sheet. It is Agentforce.

## The Agentic Enterprise, Explained

Agentforce, Salesforce's AI agent platform, now powers every Customer 360 application and is being adopted by 'tens of thousands of businesses,' according to Benioff. The platform has evolved rapidly: Agentforce 360 embeds AI agents across sales, service, marketing, commerce, IT, HR, and supply chain workflows. A new 'vibe coding' tool called Agentforce Vibes lets non-developers build applications from natural-language descriptions. And Headless 360, announced at a briefing in Japan on 27 May, exposes over 60 MCP-related tools, 4,000-plus APIs, and 220 CLI tools — letting external AI agents connect directly to Salesforce data and business logic.

The subscription numbers tell the adoption story. Agentforce Apps subscription and support revenue was $6.91 billion in Q1, up from $6.34 billion a year ago. Data 360 and other platform revenue hit $3.68 billion, up from $2.95 billion. Non-GAAP operating margin expanded to 34.8 per cent from 32.3 per cent.

## The Indian IT Problem

For India's IT services giants, Salesforce has been a reliable growth engine. TCS, Infosys, Wipro, and Cognizant maintain large Salesforce practices — implementing, customising, and managing CRM deployments for enterprise clients worldwide. These engagements are typically structured as pyramid projects: a small team of senior architects, a larger layer of mid-level developers, and a base of junior consultants who handle configuration, testing, and data migration.

Agentforce threatens to flatten that pyramid. When an AI agent can handle routine CRM configuration, auto-complete Apex code, build applications from English-language prompts, and manage testing workflows, the demand for junior human consultants compresses. It is not that Salesforce implementation work disappears — it is that fewer people are needed to do it, and the people who remain need fundamentally different skills.

Arundhati Bhattacharya, the former SBI chairwoman who led Salesforce India, has publicly noted that Indian companies lag in AI adoption. The irony is that the companies most exposed to Agentforce's disruption are the very Indian IT firms whose consultants have been evangelising the platform to enterprise clients for years.

## What NRIs Should Watch

For Indian-origin Salesforce professionals in the US — and there are thousands, many on H-1B visas — the calculus is shifting. The premium roles are now in agentic AI architecture, MCP integration, and security governance for AI workflows. Traditional CRM implementation skills are becoming table stakes. The 50 per cent EPS growth at Salesforce is a celebration in San Francisco. In Bengaluru and Hyderabad, it reads more like a warning.

The Anthropic stake adding $5 billion in implied value is a nice bonus. But the real story is that Salesforce is building the tools that could make the Indian Salesforce consultant — once the backbone of every enterprise CRM rollout — structurally redundant. The services firms that adapt fastest will survive. The rest will discover that record quarters for platform companies do not always translate into record quarters for the people who implement them."""
    },

    # ── Article 3: Indian IT Fresher Hiring Crisis ──
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Are Getting Older. That's a Problem for Everyone.",
        "subheadline": "Infosys's under-30 workforce just hit a 15-year low. TCS cut 12,000 jobs. Fresher hiring has collapsed from 380,000 to 95,000 in two years. The pipeline that feeds Silicon Valley's Indian talent is narrowing fast.",
        "slug": make_slug("india-it-fresher-hiring-crisis-tcs-infosys-aging"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's IT services firms have historically been the primary feeder system for Indian tech talent entering the US on H-1B visas. A structural decline in fresher hiring means fewer entry-level engineers gaining the experience that eventually leads to international postings. For NRIs already in the US, it means the next generation of Indian colleagues may look very different — fewer generalists, more AI specialists, and a much smaller pipeline overall. For NRI investors holding TCS or Infosys stock, the demographic shift raises questions about long-term labour cost structures.",
        "tags": ["indian-it-services", "tcs", "infosys", "wipro", "fresher-hiring", "ai-jobs", "h1b", "workforce"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/infosys-is-aging-as-young-employees-count-lowest-in-15-years"},
            {"name": "The Economic Times via LinkedIn", "url": "https://www.linkedin.com/news/story/freshers-lose-out-in-it-sector/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/india-at-a-crossroads/"},
            {"name": "The Register", "url": "https://www.theregister.com/2024/05/31/india_outsourcers_hiring/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_attribution": "Pexels",
        "body": """Here is a number that should unsettle anyone who works in Indian tech or invests in it: Infosys, India's second-largest IT services company, now has the smallest share of employees under 30 in fifteen years. The precise figures have not been disclosed in the latest filings, but the trend is unmistakable and mirrors a pattern across the sector.

Tata Consultancy Services, the industry leader with roughly 584,000 employees, laid off approximately 12,000 people last year — its largest reduction in recent memory. Employees under 30 accounted for about 48 per cent of TCS's workforce in FY25, the lowest since FY22. Fresher intake across the Indian IT industry has cratered from roughly 380,000 in 2021–22 to 95,000 in 2023–24, before recovering modestly to around 120,000 openings in FY25.

The numbers are striking. But the structural forces behind them are what matter for the diaspora.

## AI Is Eating the Base of the Pyramid

The traditional Indian IT business model runs on a pyramid: hire vast numbers of fresh engineering graduates at low cost, train them on client technologies, bill them to global enterprises, and use the margin spread between Indian salaries and Western billing rates to generate profit. It has worked spectacularly for three decades, creating millions of jobs and turning companies like TCS, Infosys, Wipro, and HCL into global brands.

Artificial intelligence is compressing that pyramid from the bottom. Repetitive coding, basic testing, helpdesk support, and data migration — the tasks that once absorbed tens of thousands of freshers each year — are increasingly handled by AI tools. Emerging technology roles now account for nearly 52 per cent of hiring demand at major IT firms, and that share is expected to reach 60 per cent by the end of 2026, according to staffing industry estimates.

'Enterprises are increasing AI funding, but cost optimisation pressures remain strong,' observes Biswajit Maity, a senior principal analyst at Gartner. The implication: clients want AI capabilities, but they also want fewer humans delivering them.

TCS, which once hired 50,000 freshers annually, has roughly halved that number. But there is a countervailing force. At Infosys, freshers in AI and digital specialisations can earn up to ₹21 lakh — a figure that would have been unthinkable for entry-level hires five years ago, when starting salaries typically ranged from ₹3.5 to ₹6 lakh. The premium for AI skills is real; it is just not available to everyone.

## The GCC Alternative

Global Capability Centres — the in-house technology operations that companies like Goldman Sachs, Google, and JPMorgan run in India — are absorbing some of the displaced demand. GCCs typically pay 20–30 per cent more than IT outsourcers for equivalent roles, and their hiring has remained comparatively robust. But GCCs employ a fraction of the people that the outsourcing giants do. They are not a substitute for mass employment.

Consultant Pareekh Jain of Pareekh Consulting frames it starkly: 'AI will reduce bulk hiring in the Indian software services industry. Fresh graduates will have fewer mass-employment options. They may have to look elsewhere — manufacturing, construction, government jobs, start-ups, or entrepreneurship.'

## What This Means for NRIs

For the Indian diaspora in the US, the fresher hiring collapse is not an abstract labour market statistic. India's IT services firms have historically been the primary pipeline for H-1B visa holders arriving in the US. TCS, Infosys, Wipro, and Cognizant are among the top H-1B sponsors year after year. Fewer freshers entering the system today means a narrower funnel of experienced mid-career engineers eligible for international postings three to five years from now.

The $100,000 H-1B visa surcharge introduced under the current US administration has already made it economically painful for IT services firms to send employees to the US. Combined with collapsing fresher intake and AI-driven productivity gains that reduce headcount requirements, the era of mass Indian engineer migration through the IT services pipeline may be ending.

TCS is responding by pivoting hard into infrastructure: a $7 billion, 1-gigawatt data centre in Visakhapatnam signals a shift from labour arbitrage to capital-intensive AI infrastructure. Accenture is spending $1 billion retraining its workforce and has been blunt about parting ways with employees who cannot adapt.

For NRI investors, the demographic data raises a specific question: if the companies that powered India's IT boom can no longer hire at the base of the pyramid, what does their long-term cost structure look like? Higher salaries for fewer, more specialised workers may preserve margins in the short term. But the growth model that turned Indian IT into a $250 billion industry was built on scale. Without it, the sector needs a new story — and right now, 'AI will fix everything' is doing most of the narrative heavy lifting."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
