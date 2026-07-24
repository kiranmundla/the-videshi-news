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

oracle_body = """Oracle has shed about 21,000 jobs in a single fiscal year — roughly 13% of its global workforce — making it the largest one-year headcount cut in the company's history. The disclosure, buried in the annual report Oracle filed on June 22, confirms what laid-off engineers had been trading on Blind and Reddit for months: the database giant is gutting its payroll to pay for an AI infrastructure binge.

The numbers are stark. Oracle's full-time staff fell to 141,000 as of May 31, 2026, down from about 162,000 a year earlier — the first time the company has dipped below 150,000 in four years. The restructuring cost between $1.8 billion and $2.1 billion, mostly severance, against just $374 million the previous year. And in the filing's risk section, Oracle said the quiet part out loud: "the adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce."

## Why an NRI in Austin or the Bay Area Should Read the Fine Print

Oracle is not an abstraction for Indian tech workers. Its Austin and Redwood City campuses, and its sprawling Bengaluru and Hyderabad development centres, run heavily on Indian engineering talent — much of it in the US on H-1B and L-1 visas. When Oracle started issuing "terminal emails" in March, the people refreshing immigration forums were disproportionately Indian nationals, because they are the ones for whom a layoff is not just a lost paycheck but a 60-day countdown to find a new sponsor or leave the country.

The damage was uneven, and that detail matters for anyone deciding which team to join. Divisions tied to legacy software — Revenue, Health Sciences — absorbed cuts of roughly 30%, according to the filing. Teams building Oracle Cloud Infrastructure and AI were largely spared, and some even grew. The lesson for an Indian engineer reading the tea leaves: proximity to the AI data-centre buildout is now the difference between expansion and a pink slip.

## The Spend That's Driving the Squeeze

Oracle is cutting humans while pouring money into machines. The company expects net capital expenditure of around $70 billion this fiscal year, funded partly by raising another $40 billion in debt and equity. It has signed enormous data-centre deals with OpenAI — including its share of the Stargate buildout — and with Meta, betting it can muscle into a cloud market dominated by Amazon and Microsoft.

The catch is that, unlike those rivals, Oracle is funding the spree by burning cash and borrowing rather than from a fat operating cushion. Its shares are down about 10% this year even as quarterly revenue rose 22% and its remaining performance obligations — contracted future business — ballooned 325% to $553 billion. Investors like the backlog; they are nervous about the bill.

## A Pattern, Not an Outlier

Oracle is the loudest example of a sector-wide reset, not a lone case. Layoffs.fyi counts more than 119,800 tech job cuts across 196 companies so far in 2026. Jack Dorsey's Block halved its workforce; Salesforce trimmed support roles it says Agentforce now handles; Meta is mid-way through sweeping cuts even as it spends north of $100 billion on AI.

For the Indian diaspora, the through-line is uncomfortable. The same companies that built their American lives are now restructuring around AI agents that automate exactly the kind of software and support work that anchored a generation of H-1B careers. A recent Blind poll found nearly half of Indian professionals in the US would consider returning home if they lost their jobs — and India's expanding tech sector, plus Canada and Europe, are increasingly part of the contingency plan.

The takeaway for NRIs is not panic but positioning: in this cycle, the safest seat is on the team building the infrastructure, not maintaining the software it is replacing."""

quantum_body = """President Donald Trump signed two executive orders on Monday to fast-track American quantum computing, setting a goal of building "the first-ever quantum computer powerful enough for scientific research" at a national laboratory by 2028 — a deadline more aggressive than anything IBM, Google or Microsoft has publicly committed to. The second order accelerates the federal government's migration to post-quantum cryptography, with high-value systems due to switch to quantum-resistant encryption by 2030 or 2031.

"We believe this can happen by 2028," said Michael Kratsios, director of the White House Office of Science and Technology Policy, framing the push as part of a race with China across quantum, AI and nuclear energy. The orders direct the Departments of Energy, Commerce and War, plus the intelligence community, to coordinate the buildout, set technical specifications, deploy quantum sensors, and stand up "National Quantum Workforce Development Institutes."

## Why This Lands Differently for the Indian Diaspora

Two reasons make this more than a Washington science story for NRIs.

First, the talent pipeline. Quantum information science sits at the intersection of physics, electrical engineering and computer science — fields where Indian-origin researchers are heavily represented in American universities and national labs. A federal program that funds apprenticeships, credentials and dedicated workforce institutes is, in effect, a hiring surge for exactly the kind of STEM graduate who arrives on an F-1 visa and hopes to stay. For Indian students weighing PhD programs, quantum just became a beat with guaranteed government demand behind it.

Second, India is running its own version of this race. New Delhi launched a roughly ₹6,000 crore National Quantum Mission in 2023, and the country has been positioning itself as a quantum talent exporter much as it did with software. The IBM quantum system that Indian officials demonstrated in Delhi is a reminder that the diaspora increasingly straddles both ecosystems — engineers who train in the US, then advise or invest back home, or vice versa.

## The Encryption Clock Everyone Should Watch

The less glamorous of the two orders may matter more, and sooner. A mature quantum computer could, in theory, break the public-key cryptography that secures bank transfers, medical records and government secrets. "As quantum rolls forward, it will challenge public key cryptography, which is what secures everything," said National Cyber Director Sean Cairncross.

This is why the "harvest now, decrypt later" threat is real: adversaries can hoover up encrypted data today and unscramble it once a capable machine exists. The order forces federal agencies onto NIST's quantum-resistant standards by 2031 — and where Washington's procurement goes, enterprise IT follows. For the thousands of Indian engineers working in American cybersecurity, cloud and fintech, post-quantum migration is about to become a multi-year line item on their roadmaps, and a fast-growing specialty to build a career around.

## A Deadline Ahead of the Science

The 2028 target is deliberately ambitious. IBM does not expect a fault-tolerant supercomputer until 2029, and most of the sector is pacing toward 2030 or later. White House officials called the government machine a "stepping stone" for research in energy, physics and advanced modelling rather than a commercial product. Last month, the Commerce Department took $2 billion in equity stakes across nine quantum-computing firms, including a new IBM venture — a sign Washington is willing to put public money directly into the cap table.

For NRI investors, the listed quantum names — IBM, IonQ, Rigetti, D-Wave — jumped on the news, but the more durable signal is structural: quantum is now a funded national priority on both sides of the US-India relationship. The engineers who understand both systems will be the ones writing the next chapter, and getting paid to do it."""

indiait_body = """Three months into the new fiscal year, the optimism India's IT giants sold investors in April is already wilting. At least four brokerages now expect the country's Big Five — Tata Consultancy Services, Infosys, Wipro, HCLTech and Tech Mahindra — to grow more slowly in FY27 than the guidance they issued just weeks ago, squeezed between AI-led automation and the drag of war in West Asia.

"From what we see right now, FY27 might not be better than the preceding year," said Amit Chandra, vice-president at HDFC Securities, citing the prolonged impact of the conflict. The warning follows Accenture's disappointing results, a bellwether the Indian majors are routinely measured against. Wipro has already guided for a revenue decline in the June quarter, while Infosys and HCLTech have hinted at "revenue deflation" from AI — HCLTech's management flagging 2% to 3% — in areas where foundation models and coding tools are simply more efficient than billable human hours.

## The Math That Worries the Diaspora

The fear is not abstract. Automation has helped send the Big Five's share prices down more than 30% since the start of the year, erasing billions in market value. The structural problem is that India's $315 billion IT sector built its fortune on labour arbitrage — armies of engineers doing application development and maintenance — and AI agents are coming straight for that revenue line.

The companies' own actions tell the story. TCS, Infosys and Wipro have together deployed over 300,000 Microsoft Copilot licences, double the December figure, across roughly a quarter of their combined 1.15 million workforce. Wipro has opened a Bengaluru Center of Excellence to train 10,000 employees on Anthropic's Claude; TCS struck its own Anthropic alliance on June 11. Each deal makes the firms more efficient — and quietly undercuts the headcount-based billing model that funded decades of hiring.

## Why NRIs Are Watching Two Things at Once

For the Indian diaspora, this hits on two fronts. Many NRIs in the US, UK and Canada hold these stocks directly or through India-focused funds, and the 30%-plus drawdown has already bruised portfolios. Wipro's US-listed shares (NYSE: WIT) trade at a price-to-earnings ratio of 14.7 against a sector average of 24.9 — cheap enough that some value investors are circling, betting the AI panic is overdone and pointing to a ₹15,000 crore buyback and an expanded ServiceNow partnership as floors under the price.

The second front is family. A vast share of the diaspora has relatives, classmates or former colleagues inside these campuses in Bengaluru, Hyderabad, Pune and Chennai. TCS's headcount already fell by 23,460 last year in its largest-ever layoff drive; Infosys and Wipro added staff, but the hiring math for the next graduating class looks tighter. When venture capitalist Vinod Khosla warned that India's $200 billion IT and BPO industry "will be gone" unless it adapts fast, he was describing the career ladder a generation of Indian families climbed into the middle class.

## The Bull Case Hiding in the Gloom

It is not all downside. Khosla, an early OpenAI backer, also argued India is uniquely positioned to lead the global deployment of AI across industries — turning the same engineering depth into an advantage rather than a liability. The Copilot and Claude rollouts, viewed less darkly, are the Big Five repositioning from selling hours to selling AI-rebuilt workflows, a larger addressable market if they can climb the value chain fast enough.

Earnings season starts in July, when TCS, Infosys, Wipro, HCLTech and Tech Mahindra report first-quarter numbers. For NRI investors and the families watching from inside the campuses, those results will be the first hard read on whether AI is eating Indian IT — or whether Indian IT is learning to eat with it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Oracle Just Cut 21,000 Jobs in a Year — Its Biggest Purge Ever. The Filing Names AI as the Reason.",
        "subheadline": "The database giant shed 13% of its workforce to bankroll a $70 billion AI data-centre spree. For Indian engineers on H-1B visas, the safe seat is now on the team building the machines, not maintaining the software.",
        "slug": make_slug("oracle-21000-job-cuts-ai-restructuring-h1b-indian-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Oracle's US and India campuses run heavily on Indian H-1B and L-1 talent, and the cuts hit legacy-software teams hardest while sparing AI and cloud — a stark signal for NRI engineers deciding where to sit.",
        "tags": ["oracle", "layoffs", "h1b", "ai", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/oracle-workforce-shrinks-by-about-21000-employees-amid-ai-adoption-2026-06-22/"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/oracle-cuts-21000-jobs-in-one-year-blames-ai-for-at-least-some"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/22/the-running-list-major-tech-layoffs-in-2026-where-employers-cited-ai/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Oracle-October2011.JPG/1280px-Oracle-October2011.JPG",
        "image_caption": "Oracle's corporate headquarters towers in Redwood City, California",
        "image_attribution": "Wikimedia Commons",
        "body": oracle_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Trump Wants a Working Quantum Computer by 2028 — Sooner Than IBM Plans One. Indian Talent Is Already in the Race.",
        "subheadline": "Two executive orders fast-track a national quantum machine and an encryption overhaul. The funded workforce push is a hiring surge for exactly the STEM graduates the diaspora supplies — and India is running its own version.",
        "slug": make_slug("trump-quantum-computing-executive-orders-2028-india-diaspora-talent"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Quantum sits at the physics-engineering-CS crossroads where Indian-origin researchers are heavily represented, and a federally funded workforce push plus India's own National Quantum Mission make this a two-country opportunity for NRIs.",
        "tags": ["quantum-computing", "trump", "post-quantum-cryptography", "india", "stem", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/trump-signs-orders-calling-powerful-quantum-computer-targeting-2028-2026-06-22/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/trump-quantum-computing-executive-orders"},
            {"name": "The White House", "url": "https://www.whitehouse.gov/fact-sheets/2026/06/fact-sheet-president-donald-j-trump-ushers-in-the-next-frontier-of-quantum-innovation/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/IBM_Quantum_Computer_Demo_at_ITUWTSA_2024%2C_Delhi_1.jpg/1280px-IBM_Quantum_Computer_Demo_at_ITUWTSA_2024%2C_Delhi_1.jpg",
        "image_caption": "An IBM quantum computer on display at a technology summit in Delhi",
        "image_attribution": "Wikimedia Commons",
        "body": quantum_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Promised a Better Year in April. Three Months In, Analysts Already See FY27 Slipping.",
        "subheadline": "AI automation and the West Asia war are squeezing TCS, Infosys, Wipro and peers, whose shares are down 30% in 2026. For NRIs, it's both a bruised portfolio and a worry about family inside the Bengaluru campuses.",
        "slug": make_slug("india-it-fy27-outlook-ai-automation-tcs-infosys-wipro-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Many NRIs hold Indian IT stocks directly and have relatives working inside these campuses, so the AI-driven squeeze on the $315 billion sector is at once a portfolio question and a family one.",
        "tags": ["indian-it", "tcs", "infosys", "wipro", "ai", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Mint", "url": "https://www.livemint.com/companies/news/ai-weak-demand-cloud-fy27-outlook-for-indian-it-11718000000000.html"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-wipro-opens-ai-center-anthropics-claude-bengaluru-2026-06-17/"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/wipro-limited-wit-gains-due-to-share-buyback-program-and-servicenow-partnership"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg/1280px-Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg",
        "image_caption": "The glass pyramid at the Infosys campus in Bengaluru, India",
        "image_attribution": "Wikimedia Commons",
        "body": indiait_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"  words={wc}  headline_len={len(art['headline'])}  {art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
