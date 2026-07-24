#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-05-31 06:00 UTC run"""
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

def verify_image(url):
    """Verify image URL returns HTTP 200 with image content type and >5KB."""
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return url
        # Try GET if HEAD doesn't give content-length
        r2 = requests.get(url, timeout=10, stream=True, allow_redirects=True,
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct2 = r2.headers.get("Content-Type", "")
        cl2 = int(r2.headers.get("Content-Length", 0))
        if r2.status_code == 200 and "image" in ct2 and cl2 > 5000:
            return url
    except Exception as e:
        print(f"  ⚠️ Image verification failed for {url}: {e}")
    return None

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

articles = [
    # ── Article 1: Intel $3.3B Odisha Substrate Plant ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Intel Just Made Its First Manufacturing Move in India. The $3.3 Billion Bet Is on Packaging, Not Chips.",
        "subheadline": "A new substrate facility in Odisha positions India inside the advanced packaging supply chain that powers every AI server and smartphone on the planet.",
        "slug": make_slug("intel-odisha-33-billion-substrate-semiconductor-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian semiconductor professionals in the US — many of whom work at Intel, TSMC, and Applied Materials — now have a credible career path in India's chip ecosystem. For NRI investors, the broader India Semiconductor Mission portfolio (Tata Dholera, Micron Gujarat, CG Semi Sanand, and now Intel Odisha) is becoming a real asset class.",
        "tags": ["semiconductor", "intel", "india-semiconductor-mission", "odisha", "manufacturing", "advanced-packaging"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/intel-3dgs-set-up-33-billion-substrate-plant-indias-odisha-state-2026-05-29/"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/intel-joins-hands-with-odisha-govt-to-boost-indias-semiconductor-ecosystem/article69632145.ece"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/technology/3399234-intel-collaborates-with-odisha-for-advanced-substrate-manufacturing-in-india"},
            {"name": "India Education Diary", "url": "https://indiaeducationdiary.in/mou-signed-to-bring-substrate-manufacturing-technology-to-india/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """When Intel CEO Lip-Bu Tan joined a video call on Friday to watch an MoU signing between his company, 3D Glass Solutions, and the Odisha state government, it marked something that has eluded India's semiconductor ambitions for decades: Intel's name on an Indian manufacturing deal.

The project is not a chip fabrication plant. It is a $3.3 billion advanced packaging substrate facility — a glass core substrate manufacturing unit in the Bhubaneswar-Khurda corridor, to be built over five to six years. The distinction matters, because substrates are the bedrock layer on which semiconductor devices are mounted, and advanced glass core substrates are the next frontier in chip packaging for AI accelerators, high-bandwidth memory, and high-performance computing.

## What Intel Is Actually Building

The facility will manufacture advanced packaging glass core substrates and high-density interconnect substrates, with Intel providing technology know-how and process expertise. Glass substrates are considered a potential successor to the organic substrates used in most chip packages today — they offer superior flatness, thermal stability, and the ability to support finer wiring at higher densities. Intel has been developing glass substrate technology at its labs in Arizona and Chandler for years. Transferring production capability to India is a significant move.

3DGS, the Albuquerque-based company co-signing the deal, specialises in glass-based semiconductor packaging. Through its Indian subsidiary, Heterogeneous Integration Packaging Solutions, the venture will produce 70,000 glass panels annually, along with 50 million assembled units and roughly 13,000 advanced 3D heterogeneous integration modules. Commercial production is targeted for August 2028, with full-scale volume by 2030.

## The India Semiconductor Mission Scorecard

Union IT Minister Ashwini Vaishnaw, who witnessed the signing, framed the deal as the latest domino in India's semiconductor buildout. The roster now reads: Tata Electronics and PSMC running trial wafer production at Dholera (28nm to 110nm), Micron's $2.75 billion ATMP facility in Sanand producing enterprise-grade DRAM and NAND, CG Semi's OSAT pilot line in Gujarat, and now Intel's glass substrate play in Odisha. Equipment majors Applied Materials, Lam Research, Tokyo Electron, and Merck Electronics have all established Indian operations. Tata Electronics has signed with ASML, the Dutch lithography monopolist.

The total approved investment under the India Semiconductor Mission stands at roughly ₹1.6 lakh crore across ten projects in six states. The 1,800 direct high-skilled jobs Intel's Odisha facility will generate are a fraction of the ecosystem employment — ancillary suppliers, chemical processors, and equipment maintenance firms tend to multiply semiconductor headcount by three to five times.

## Why This Matters for the Diaspora

For Indian semiconductor professionals in the United States — and there are thousands at Intel, Qualcomm, Broadcom, Applied Materials, and TSMC's Arizona fabs — the Odisha announcement creates something that didn't exist three years ago: a plausible career path in India's chip industry that doesn't involve a downgrade.

Advanced packaging is where much of the semiconductor industry's innovation is concentrated right now. TSMC's CoWoS technology, Intel's Foveros, and AMD's 3D V-Cache all depend on substrate quality. India entering this segment — rather than just assembly and test — puts it closer to the value-dense part of the supply chain.

For NRI investors, the picture is more complex. None of these ventures are publicly traded in India yet, but the supplier ecosystem around them is growing. The broader signal is that India is no longer a chip-design-only story. It is building physical manufacturing capability, and the companies enabling that build — from speciality chemicals to cleanroom equipment — represent an emerging investment theme.

The challenge, as always, is execution. India has announced semiconductor ambitions before. What's different this time is that the money is real, the partners are tier-one, and the first wafers are already rolling off the line in Dholera. Intel's entry — even in packaging, not logic fabrication — gives the mission a credibility it previously lacked."""
    },

    # ── Article 2: Bajaj Finserv Intelligence ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Bajaj Finserv Is Spending ₹2,000 Crore to Build India's AI Startup Factory. IIT Bombay Is the Lab.",
        "subheadline": "The financial conglomerate's new Finserv Intelligence programme blends venture capital, academic research, and enterprise access — a model India's deep-tech ecosystem has been missing.",
        "slug": make_slug("bajaj-finserv-intelligence-ai-startup-iit-bombay"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI founders building in AI, cybersecurity, or quantum computing now have a serious Indian corporate backer that offers more than capital — Bajaj Finserv's ecosystem includes Bajaj Finance, India's largest NBFC, plus insurance, asset management, and consumer lending arms. For diaspora technologists considering a return-to-India startup, this is the kind of institutional backing that previously only existed in the Valley.",
        "tags": ["ai", "fintech", "bajaj-finserv", "iit-bombay", "startup-ecosystem", "venture-capital", "quantum-computing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/money-and-banking/bajaj-finserv-to-invest-1500-2000-crore-in-ai-innovation-startups-over-5-yrs/article69624798.ece"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/business/3398734-bajaj-finserv-plans-rs-2000-crore-investment-in-ai-and-tech-startups"},
            {"name": "Express Computer", "url": "https://www.expresscomputer.in/news/bajaj-finserv-launches-finserv-intelligence/120853/"},
            {"name": "IBS Intelligence", "url": "https://ibsintelligence.com/ibsi-news/bajaj-finserv-partners-iit-bombay-on-high-tech-scalable-solutions/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f4/Sanjiv_Bajaj.jpg",
        "body": """India's financial sector has spent the past five years adopting AI. Bajaj Finserv wants to build the ecosystem that produces it.

The Pune-headquartered financial conglomerate launched Finserv Intelligence last week, committing ₹1,500 to ₹2,000 crore over five years to back AI, cybersecurity, quantum computing, and fintech startups from seed stage through Series B. But the money is not the most interesting part of the announcement. The structure is.

## More Than a Cheque

Unlike a conventional corporate venture arm, Finserv Intelligence is designed as an integrated innovation ecosystem with a five-to-ten-year horizon. The programme pairs capital with something Indian deep-tech startups have historically struggled to find: enterprise access.

Startups accepted into the programme will plug directly into Bajaj Finserv's enterprise ecosystem — which includes Bajaj Finance (India's largest non-banking financial company by market capitalisation), Bajaj Life Insurance, Bajaj General Insurance, Bajaj Health Insurance, and Bajaj Finserv Asset Management. That is not a mentorship programme. It is a distribution pipeline.

"Finserv Intelligence offers founders something fundamentally different from capital alone," said Rajeev Jain, Vice Chairman and Managing Director of Bajaj Finance. "Startups will plug directly into our governance frameworks, financial discipline, operational depth and market insight."

The company is also offering structured growth playbooks, hands-on mentorship, and what it calls "flexible ticket sizes and committed follow-on investment" — a signal that portfolio companies won't face the funding cliff that kills promising Indian startups between seed and Series A.

## The IIT Bombay Partnership

The academic anchor is a collaboration with IIT Bombay through a formal MoU and Master Collaboration Agreement. The two will establish a joint research centre focused on AI, cybersecurity, quantum technologies, and "reimagining physical retail experience" — a nod to Bajaj Finserv's extensive branch and partner network.

The partnership extends to R&D labs, centres of excellence, and a Scholars-in-Residence programme. Professor Shireesh Kedare, Director of IIT Bombay, called it a model for "translating research into technologies and solutions that create meaningful, real-world impact."

This is the piece India's startup ecosystem has been asking for. Indian IITs produce world-class research in AI and quantum computing, but the commercialisation pipeline — the bridge between a lab breakthrough and a funded startup with paying customers — has been conspicuously thin. Israel's model of military R&D feeding into startups, or Stanford's relationship with Silicon Valley, has no Indian equivalent. Bajaj Finserv is attempting to build one.

## What This Means for NRI Founders

For diaspora technologists weighing a return-to-India startup, the calculus just shifted. The traditional complaint about building in India — that corporate buyers are slow, funding is scarce past seed, and distribution requires years of relationship-building — is exactly what Finserv Intelligence is designed to address.

A cybersecurity startup building for Indian financial institutions, for instance, would gain immediate access to Bajaj Finance's 90-million-plus customer base and the regulatory compliance infrastructure that comes with it. An AI startup building fraud detection models would have real transaction data to train on, not synthetic datasets.

The ₹2,000 crore commitment translates to roughly $240 million at current rates — not SoftBank-scale, but serious money by Indian standards, and specifically targeted at the seed-to-Series-B gap where most deep-tech ventures die. Sanjiv Bajaj, Chairman and Managing Director of Bajaj Finserv, framed the ambition plainly: "The next decade of value creation in financial services will belong to those who build technology that powers it. We have chosen to build, and to build in India."

The deeper signal is structural. India's largest financial conglomerates — Bajaj, Reliance, Tata — are no longer content to be technology consumers. They are positioning themselves as technology producers. For NRI investors tracking the Indian AI ecosystem, the shift from adoption to creation is the trend worth watching."""
    },

    # ── Article 3: H-1B Developers vs AI Coding Assistants ──
    {
        "id": str(uuid.uuid4()),
        "headline": "AI Coding Assistants Are Rewriting the H-1B Job Market. The Engineers They Replace Won't Get a 60-Day Grace Period.",
        "subheadline": "Companies are hiring fewer developers, paying more for AI talent, and increasingly preferring green card holders. For hundreds of thousands of Indian H-1B workers, the shift is existential.",
        "slug": make_slug("h1b-developers-ai-coding-assistants-hiring-shift"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "An estimated 300,000-plus Indian nationals hold H-1B visas in the United States, a disproportionate number of them software developers at FAANG companies, Indian IT services firms, and mid-size tech employers. The shift from hiring coders to hiring AI-augmented systems thinkers directly threatens the traditional career path that brought most of them to America.",
        "tags": ["h1b", "ai", "coding-assistants", "github-copilot", "hiring", "silicon-valley", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "InfoWorld", "url": "https://www.infoworld.com/article/4178167/developers-on-h-1b-face-a-tighter-job-market-as-ai-shifts-hiring-priorities.html"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/4178167/developers-on-h-1b-face-a-tighter-job-market-as-ai-shifts-hiring-priorities.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/h-1b-returnees-face-cautious-ai-led-job-market-in-india-say-experts/article69621384.ece"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5483070/pexels-photo-5483070.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The job market for software developers on H-1B visas was always precarious — a 60-day window to find new employment after a layoff, an annual lottery for renewals, and the constant awareness that your right to live in America is stapled to your employer's willingness to sponsor you. Now, the tools that were supposed to make developers more productive are making some of them unnecessary.

GitHub Copilot, Claude, ChatGPT, and a growing fleet of AI coding assistants are changing the economics of software development. Companies are not hiring fewer engineers because the work disappeared. They are hiring fewer because the remaining engineers, augmented by AI, can do more. The result is a structural contraction in demand for the kind of mid-level coding work that has employed hundreds of thousands of Indian H-1B holders for two decades.

## "Companies Are Not Looking for H-1B Now"

Pareekh Jain, CEO of Pareekh Consulting, put it bluntly in an InfoWorld interview: "Companies are not looking for H-1B now. They are building a local workforce and preferring green card holders and citizens."

The logic is straightforward. If AI tools reduce the number of developers needed for a given project, employers become pickier about who they hire. Sponsoring an H-1B visa adds cost, paperwork, and legal risk. When the talent pool of available permanent residents and citizens grows — fed partly by the same layoffs that freed them — the case for H-1B sponsorship weakens.

Jain said companies are now more likely to consider H-1B candidates only for immediate project needs, rather than building a long-term bench of visa-dependent workers. The bench model — where IT services firms and even product companies stockpiled H-1B developers against future demand — is eroding.

## Junior Developers Hit Hardest

The squeeze is particularly brutal at the entry level. Adarsh ML, a product engineer at Ather Energy who tracks global hiring trends, described the structural shift: "Job opportunities for people with zero to three or four years of experience are not really there anymore."

The math is simple. Tasks that once occupied junior developers — writing boilerplate code, building CRUD applications, debugging routine errors — are exactly the tasks AI coding assistants handle well. Companies that previously hired three junior developers under a senior engineer now hire one senior developer who uses Copilot.

That creates what Adarsh calls a pipeline paradox: "If companies only want people with five years of experience to manage AI agents today, who will have that experience five years from now? There may not be enough experienced developers left."

For Indian students on F-1 visas hoping to transition through OPT to H-1B, the numbers are stark. USCIS received 343,981 eligible H-1B registrations for fiscal year 2026 and selected 120,141 — a 35 per cent hit rate. Of those selected, many are now competing for jobs against AI tools that can do entry-level work faster and cheaper.

## AI Literacy Is the New Excel

Not every developer is equally exposed. Sophia James, an Indian software professional working in database monitoring in the US, said AI has not dramatically changed her team's daily workflow. But the expectation is shifting. "Managers are trying to understand whether we are keeping up with the changes happening in the market," she said.

Jain framed the new baseline clearly: "Being AI-literate is a must now, even if the role is not directly in AI development. This is like knowing Excel even if you are not from finance in the earlier era."

The developers who survive the contraction will be those who can validate AI-generated code, secure it, integrate it into production systems, and take responsibility for the result. Sanchit Vir Gogia, chief analyst at Greyhound Research, drew the line: "The engineer who only produces output grows easier to replace as the output grows easier to generate. The engineer who can validate it, secure it, situate it in a real business, and stand behind the result becomes harder to replace."

## The 60-Day Clock

For H-1B holders, the stakes are uniquely high. A layoff triggers a 60-day grace period to find new H-1B-sponsoring employment, transfer to another visa status, or leave the country. In a market where fewer companies are willing to sponsor and more prefer local hires, that window has become a trap rather than a safety net.

Gogia's advice is practical: understand portability rules and employer sponsorship timelines before a job loss forces urgent decisions. "The strategic error is treating that window as a safety net rather than a planning horizon," he said.

Meanwhile, the return-to-India option is no better than tepid. Kamal Karanth, co-founder of staffing firm Xpheno, warned that India's tech hiring has not stabilised since the 2021 boom. "After the hiring buoyancy of 2021, the Indian tech sector has not had a period of stability extending beyond a quarter," he said. Indian tech demand in May was lower than the previous month, and GenAI tools are compressing traditional roles there too.

The uncomfortable truth for Indian H-1B developers is that neither staying nor returning offers the security it once did. The only durable strategy is the one nobody wants to hear: become the engineer the AI cannot replace. That means moving from writing code to architecting systems, from building features to governing AI outputs, from being productive to being irreplaceable. The 60-day grace period doesn't cover career transitions."""
    },
]

# Verify images first
for art in articles:
    img = verify_image(art["image_url"])
    if img:
        print(f"✅ Image OK: {art['slug']}")
    else:
        print(f"⚠️ Image failed verification for {art['slug']}, keeping URL anyway")

print()

# Insert articles
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ Published: {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
