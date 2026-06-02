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
        "headline": "Satya Nadella's Microsoft Used AI to Redesign a Quantum Chip. Critics Say It Still Doesn't Work.",
        "subheadline": "The Majorana 2 chip promises a 1,000-fold improvement and commercially useful quantum computers by 2029. Physicists are unconvinced the underlying science holds up.",
        "slug": make_slug("microsoft-majorana-2-quantum-chip-ai-nadella-critics"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian quantum computing researchers at Microsoft, IBM, and Google are at the centre of this race. India's National Quantum Mission has committed ₹6,000 crore, and IISc just launched InQubate — a startup accelerator for quantum ventures. For NRI physicists and engineers, this is both a career signal and a potential investment thesis.",
        "tags": ["quantum-computing", "microsoft", "satya-nadella", "ai", "majorana"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-reveals-new-quantum-chip-made-with-ai-says-it-will-have-systems-by-2029-2026-06-02/"},
            {"name": "Science News", "url": "https://www.sciencenews.org/article/microsoft-quantum-chip-majorana-2-upgrade-skepticism"},
            {"name": "Scientific American", "url": "https://www.scientificamerican.com/article/microsofts-upgraded-majorana-quantum-computing-chip-fizzles-with-physicists/"},
            {"name": "Microsoft Blog", "url": "https://news.microsoft.com/2026/06/02/majorana-2-made-more-reliable-with-microsoft-discovery-agentic-ai/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "is_editorial": False,
        "body": """Microsoft unveiled Majorana 2 at its Build conference in San Francisco on Tuesday — a quantum computing chip that the company says was fundamentally redesigned using its own artificial intelligence tools. The result, according to Microsoft, is a 1,000-fold improvement in qubit reliability and a firm target date: commercially useful quantum computers by 2029.

The announcement lands Satya Nadella's company in a direct timeline race with IBM, which last month committed $10 billion to quantum machines and spun out a dedicated chip-making subsidiary with Trump administration backing. Alphabet's Google, Amazon, and several Chinese labs round out a field where the prize — cracking problems in drug discovery, materials science, cryptography, and climate modelling that would take classical supercomputers millennia — justifies the billions being poured in.

## What Changed in the Chip

Majorana 2 ditches aluminium, the standard superconducting material used by Google, IBM, and most other quantum hardware makers, and replaces it with lead. The switch sounds simple. It was not.

Lead is water-soluble. Using it on a chip without the material dissolving during manufacturing required what Jason Zander, the Microsoft executive vice president overseeing quantum, described as an AI-driven materials science breakthrough. Microsoft's Discovery platform — an agentic AI system purpose-built for scientific research — screened candidate materials and predicted how they would behave at the cryogenic temperatures quantum chips demand.

The payoff in the lab data is striking. The first Majorana chip, released last year, maintained qubit coherence for milliseconds. Majorana 2 holds it for a mean of 20 seconds, with some instances lasting a full minute. Microsoft's analogy: a phone battery that lasts three years instead of dying in a day. The qubits themselves are tiny — one-hundredth of a millimetre — and operate in one-microsecond cycles, a combination the company says puts it on a path to millions of qubits on a single chip.

## Why Physicists Are Pushing Back

The trouble is that independent scientists have questioned the foundations of Microsoft's approach for over a year, and Majorana 2 has not silenced them.

Microsoft's quantum strategy relies on topological qubits — a theoretical concept in which electrons are coaxed to behave collectively as so-called Majorana quasiparticles. If real, these particles would be inherently resistant to the noise and errors that cripple other quantum architectures. It is an elegant idea with one persistent problem: proving the quasiparticles actually exist in the devices Microsoft is building.

Scientific American reported on Tuesday that several physicists remain unconvinced. The Majorana 2 paper, posted as a preprint on arXiv and on a Microsoft site, has not been peer-reviewed. Science News noted that last year's Majorana chip "immediately drew skepticism from scientists," and the upgrade "hasn't convinced harsh critics." The concern is not that lead is worse than aluminium. It is that the entire topological framework may be measuring artefacts rather than genuine Majorana quasiparticles.

Chetan Nayak, a Microsoft technical fellow leading the effort, was measured: "We've got to keep marching to that roadmap. Where are we relative to last year? We're 1,000 times better."

## Where India and the Diaspora Fit

This race is not abstract for Indian professionals. Indian-origin researchers occupy senior positions across Microsoft's Azure Quantum division, IBM Research, and Google's quantum AI lab. India's National Quantum Mission, funded at ₹6,003 crore (roughly $720 million), is building domestic capacity in quantum computing, communications, and sensing. Just last week, IISc Bangalore launched InQubate, a startup accelerator for quantum ventures emerging from its research park.

For NRI engineers and physicists, the 2029 timeline — whether credible or aspirational — shapes career decisions. If topological qubits deliver, Microsoft gains a structural advantage that could define the next decade of cloud computing. If the critics are right, billions will have been spent on elegant physics that never became engineering.

The quantum race is also an investment signal. IBM's quantum spinout is already seeking external capital. Alphabet's $80 billion equity raise announced this week funds AI infrastructure but explicitly includes quantum ambitions. Indian investors tracking the next compute paradigm have a narrowing window to understand which bets are science and which are marketing.

What is clear is that AI is no longer just the product these companies sell. It is now the tool they use to build the hardware that will succeed AI itself. Whether Majorana 2 represents a genuine breakthrough or a beautifully optimised dead end will probably not be settled by a press conference. It will be settled by peer review, replication, and time — three things the quantum computing industry has historically found inconvenient."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Is Sending 120 Deep-Tech Startups to France. This Is Not a Trade Show.",
        "subheadline": "Bharat Innovates 2026 in Nice features companies building satellite propulsion, sovereign AI, and iron-air batteries — the hardware India needs to stop being called a back-office.",
        "slug": make_slug("bharat-innovates-2026-nice-france-deep-tech-startups"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors managing patient capital in deep tech now have a curated pipeline of 120 ventures across 13 frontier sectors. For diaspora founders considering a return to India, this cohort signals a maturing ecosystem — 4,200+ deep-tech startups, $2.3 billion in funding, and government-backed global exposure that did not exist three years ago.",
        "tags": ["india-deep-tech", "bharat-innovates", "startups", "france", "semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "YourStory", "url": "https://yourstory.com/2026/06/india-120-deep-tech-startups-bharat-innovates-2026-france"},
            {"name": "Press Information Bureau", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2112345"},
            {"name": "Nasscom-Zinnov India Tech Startup Report 2025", "url": "https://nasscom.in/knowledge-center/publications/india-tech-startup-report-2025"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8348739/pexels-photo-8348739.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "is_editorial": False,
        "body": """In twelve days, 120 Indian startups will set up in Nice, France, to pitch international investors, defence procurement offices, and industrial partners on technology that has nothing to do with software services. Bharat Innovates 2026, running from 14 to 16 June as part of the India-France Year of Innovation, is the Indian government's most deliberate attempt yet to reposition the country as a builder of frontier hardware and deep science — not just a supplier of programmers.

The cohort was announced by Prime Minister Narendra Modi in February and curated through a national pre-summit at IIT Bombay in March, where 137 companies were shortlisted from over 3,000 applications. The final 120 span 13 technology sectors. Space and Defence leads with 22 startups. Healthcare and MedTech follows with 20. Energy, Sustainability and Climate accounts for 16, Advanced Computing for 13, and Biotechnology for 11. Semiconductors, Manufacturing, Smart Cities, Agri-Tech, and Next-Gen Communications fill out the rest.

## Who Is Going

Some names are already familiar. Ather Energy, the electric two-wheeler company that went public last year, is in the cohort alongside ideaForge, the drone manufacturer that dominates Indian military contracts. Agnikul Cosmos, which conducted India's first privately built single-piece 3D-printed rocket engine test, will be there. So will Sarvam AI, the Bengaluru-based sovereign AI company building large language models trained on Indian languages, and Qure.ai, whose chest X-ray analysis tool is deployed in over 90 countries.

But the more interesting names are the ones most people have not heard of — companies working on iron-air batteries, quantum cybersecurity, brain-mapping platforms, and green satellite propulsion. These are ventures that need years, not quarters, to commercialise. That timeline has historically made them nearly impossible to fund in India.

## The Numbers Behind the Pitch

The cohort arrives at a moment when the underlying data has started to shift. According to the Nasscom-Zinnov India Tech Startup Report, India now hosts more than 4,200 deep-tech startups, including over 550 founded in 2025 alone. Deep-tech funding rose 37 per cent last year to $2.3 billion, even as broader venture capital turned more cautious and milestone-linked. Artificial intelligence accounted for a staggering 91 per cent of that capital.

Ahead of Nice, the Ministry of Education and the Indian Venture and Alternate Capital Association held an investor showcase in Bengaluru on 19 May. Twenty-four startups from the cohort pitched to more than 90 investors managing over $85 billion in combined assets. The pipeline, at least, is being taken seriously.

## What the Diaspora Should Watch

For NRI investors, Bharat Innovates is not a feel-good government expo. It is a curated deal flow pipeline.

The event is designed to generate pilots, co-development agreements, and research partnerships — not just photo opportunities. Several investors from the Bengaluru round reportedly expressed interest in continuing conversations beyond the showcase. France, for its part, has its own strategic interest: the India-France Year of Innovation was conceived in part to diversify European technology supply chains away from singular dependence on Chinese and American providers.

The diaspora angle is layered. Indian-origin venture capitalists in Silicon Valley and London increasingly run deep-tech funds that struggle to find enough qualified deal flow outside the United States. Bharat Innovates is packaging 120 ventures — screened, mentored, and categorised by sector — into one accessible event. For NRI founders considering a return to India or a cross-border co-founding arrangement, the ecosystem signal is clearer than it has ever been.

India spent the 2010s proving it could build consumer internet companies. The 2020s tested whether it could build fintech at scale. The question for the rest of this decade is whether it can build hard technology — chips, rockets, batteries, quantum systems — that the world actually needs. Bharat Innovates 2026 is India's most public answer so far. The real test, as always, will be what happens after the founders come home from Nice."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "142,000 Tech Workers Have Lost Their Jobs in 2026. The Companies Cutting Them Have Never Been More Profitable.",
        "subheadline": "Amazon, Oracle, Meta, and Cisco are posting record earnings while slashing headcount and blaming AI. Sam Altman calls it 'AI washing.' For Indian H-1B holders, the euphemism doesn't matter — the 60-day clock does.",
        "slug": make_slug("ai-washing-tech-layoffs-142000-h1b-indian-workers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indians hold 71-73% of all H-1B visas. With 142,000 tech jobs cut and median Bay Area hiring time stretching from 38 to 67 days, the 60-day grace period is no longer a formality — it is a ticking deadline. This story directly affects tens of thousands of Indian families in the US.",
        "tags": ["layoffs", "h1b", "ai-washing", "indian-tech-workers", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "LinkedIn / Roger McCoy", "url": "https://www.linkedin.com/pulse/ai-job-apocalypse-washing-real-story-behind-2026s-tech-roger-mccoy/"},
            {"name": "Skillsyncer Layoffs Tracker", "url": "https://skillsyncer.com/layoffs-tracker"},
            {"name": "TechTimes / Stanford HAI", "url": "https://www.techtimes.com/articles/stanford-hai-software-developer-employment-2026.htm"},
            {"name": "Memeburn / Sam Altman", "url": "https://memeburn.com/2026/05/sam-altman-dario-amodei-ai-jobs-apocalypse-2026/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7640810/pexels-photo-7640810.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "is_editorial": False,
        "body": """The numbers are not subtle. As of 1 June 2026, 142,000 technology workers have lost their jobs across 212 separate layoff events — roughly 897 people per day since January. Amazon eliminated 16,000 corporate roles in Q1 alone. Oracle cut approximately 30,000. Meta shed over 8,000 in May, the same month it reported its best revenue growth since 2021. Cisco trimmed 4,000. Block, Atlassian, Pinterest, Coinbase, and Webflow have all cited AI efficiencies while restructuring.

What makes this cycle genuinely new is not the volume. The 2022-23 layoff wave was comparable in raw numbers. What is different is that every company executing major cuts is simultaneously filing the strongest earnings in its history. Profit margins are up. Share prices are up. And the explanation offered to employees, shareholders, and regulators is increasingly the same three letters: AI.

## The 'AI Washing' Debate

Sam Altman said the quiet part out loud. The OpenAI CEO told attendees at a BlackRock event this month that "some companies are blaming AI for layoffs they would have made anyway." He is not alone in that assessment.

Oxford Economics data cited by multiple analysts suggests firms are not replacing workers with AI at any significant scale — not yet. The actual drivers, according to a Forrester analysis and a New York Times investigation from earlier this year, are more familiar: pandemic-era overhiring, the compounding weight of elevated interest rates, and the strategic reallocation of operating budgets toward massive AI infrastructure investments. The companies are not spending less. They are spending differently — pouring billions into GPU clusters, data centres, and AI talent while trimming headcount in functions they have decided are automatable in principle, even if the automation does not yet exist in practice.

A Yale Budget Lab study found "no meaningful change in unemployment rates for AI-exposed workers" since ChatGPT launched in late 2022. Broad US unemployment remains stable at roughly 4.3 per cent. The Jevons Paradox — the observation that making work cheaper with technology often increases demand for it rather than reducing it — appears to be holding, at the macro level.

But macro statistics provide cold comfort to individuals.

## The H-1B Pressure Cooker

For Indian technology professionals in the United States, a layoff is never just a job loss. It is an immigration event.

H-1B status is employer-sponsored. When the employment ends, the visa status technically lapses from that date. USCIS grants a 60-day grace period to find a new sponsor, change status, or leave the country. Sixty days used to feel manageable. It no longer does.

Median time-to-hire in the Bay Area has stretched from 38 days in Q3 2025 to 67 days in Q1 2026, according to data tracked by Invezz. That means the average job search now takes longer than the grace period allows. For H-1B holders who are also in the green card backlog — and most Indian applicants are, given wait times that can stretch beyond a decade — an interrupted stay can mean losing years of accumulated immigration progress.

The demographic weight is enormous. Indians account for 71 to 73 per cent of all approved H-1B beneficiaries, according to USCIS data. At the companies executing the largest cuts — Amazon, Meta, Oracle — Indian professionals make up a disproportionate share of the engineering workforce. Meta's WARN notice for 3,270 Bay Area positions, filed last month, explicitly triggered the clock for hundreds of H-1B holders in a region where the next job is no longer guaranteed to arrive in time.

Stanford HAI tracked software developer employment for workers under 26 and found it has fallen nearly 20 per cent since 2024. That cohort includes a significant share of recent H-1B and OPT holders — people at the most vulnerable point in their immigration journey.

## What Is Actually Happening

The honest answer is that both things are true at once. AI is genuinely reshaping some job functions, particularly in coding, analysis, content generation, and quality assurance. GitHub data shared at Computex this week showed code commits nearly tripling in early 2026, driven largely by AI coding agents. Cognition's Devin, the autonomous coding system, now writes 90 per cent of its own company's code. These are not hypothetical capabilities.

But the gap between AI's actual displacement of workers and the narrative companies are deploying to justify restructuring is wide, growing, and convenient. A layoff attributed to AI flatters the executive team's strategic vision. A layoff attributed to overhiring and margin pressure does not.

On 21 May, California Governor Gavin Newsom signed an executive order directing state agencies to study AI-driven displacement and develop policy responses. Governors do not sign executive orders when a problem is theoretical. They sign them when constituent pressure makes inaction politically untenable.

For the Indian engineer in Sunnyvale reading a severance letter that cites "AI-driven organisational efficiency," the distinction between real automation and narrative convenience is academic. The 60-day clock does not care about taxonomy. It just ticks."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
