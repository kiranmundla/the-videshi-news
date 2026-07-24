#!/usr/bin/env python3
"""Tech writer run: 2026-07-14 20:00 PDT — 3 articles"""

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
    # ── Article 1: IBM Crash / Arvind Krishna ──────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Arvind Krishna Admits IBM 'Faltered.' The Stock Just Had Its Worst Day Since 1968.",
        "subheadline": "IBM lost $70 billion in market value in a single session after its Indian-born CEO warned that customers are abandoning software for AI hardware. The shockwave dragged Adobe, ServiceNow and Salesforce down with it.",
        "slug": make_slug("arvind-krishna-ibm-faltered-worst-day-1968-ai-software"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "IBM's Indian-born CEO is navigating the company's worst crisis in decades, while the selloff hit other Indian-led companies like Adobe (Shantanu Narayen) — and thousands of Indian engineers at IBM face an uncertain future as the company restructures around AI hardware.",
        "tags": ["ibm", "arvind-krishna", "ai-spending", "software-stocks", "wall-street", "indian-tech-ceos"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ibm-warns-ai-boom-squeezing-software-budgets-shares-sink-sector-rout-2026-07-14/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/earnings/ibm-loses-69-billion-of-market-value-in-one-day-in-latest-ai-fueled-selloff-4d2a8a13"},
            {"name": "Investopedia", "url": "https://www.investopedia.com/ibm-stock-plunges-after-weak-q2-results-ceo-admits-tech-giant-faltered-11739849"},
            {"name": "New York Post", "url": "https://nypost.com/2026/07/14/business/ibm-shares-plunge-27-as-ai-spending-boom-hammers-business/"}
        ]),
        "score_total": 88,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Arvind_Krishna_at_SXSW_2025.jpg/1280px-Arvind_Krishna_at_SXSW_2025.jpg",
        "image_caption": "IBM CEO Arvind Krishna at SXSW 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """It was supposed to be a routine quarter. Instead, IBM's Arvind Krishna delivered a letter to investors on Tuesday that read more like a confession.

"We did not adapt and move quickly enough, and numerous large deals failed to close on the timelines we expected, driving the majority of our shortfall," Krishna wrote. "These conditions require our teams to execute perfectly, and this quarter we faltered."

The market's response was swift and merciless. IBM shares cratered 25% on Tuesday — the company's worst single-day loss since 1968, according to Bloomberg data. Roughly $70 billion in market capitalisation evaporated in a matter of hours, dragging the Dow Jones Industrial Average down by more than 400 points.

## What Went Wrong

The problem, Krishna explained, was a spending shift that caught IBM off guard. Enterprise customers began redirecting quarterly budgets away from software — particularly IBM's flagship mainframe transaction-processing stack — and toward servers, storage and memory chips. Companies are stockpiling AI hardware before prices climb further, a pattern driven by the semiconductor supply crunch and the insatiable demand for data-centre infrastructure.

IBM now expects second-quarter revenue of $17.2 billion, up just 1% year over year. That is the company's weakest growth rate since early 2025, and well below the $17.86 billion Wall Street had pencilled in. Earnings per share are expected at $2.27 — a dramatic miss against the $3.02 consensus.

Krishna pointed to one additional factor: cybersecurity. The release of Anthropic's Claude Mythos model this year, which demonstrated an unprecedented ability to identify and exploit software vulnerabilities, has jolted enterprise buyers into reassessing their security spending. That distraction, Krishna said, contributed to several large deals stalling in the final weeks of June.

## The Ripple Across Indian-Led Tech

The damage was not confined to IBM. The selloff tore through the broader software sector, hitting several companies led by Indian-origin executives. Adobe, where Shantanu Narayen has served as CEO since 2007, fell 4.3%. ServiceNow dropped 5.8%. Salesforce slid 2.1%. Microsoft, led by Satya Nadella, also retreated, though by a more modest margin.

Investors are now openly using the term "SaaS-pocalypse" to describe the risk that AI model makers — OpenAI, Anthropic and their peers — will gradually replace traditional per-seat software licensing with outcome-based AI workflows. IBM's stumble has given that thesis its starkest piece of supporting evidence yet.

"This is an ugly moment for IBM and software stocks," said Chris Beauchamp, chief market analyst at IG Group. "The big question will be how long the shift to infrastructure and cybersecurity lasts. A few more months might be bearable, but more than that and serious questions will be asked all over again."

## Why NRIs Should Pay Attention

For Indian Americans in the technology sector, the IBM warning lands on three levels.

First, the professional. IBM employs tens of thousands of engineers and consultants in India and the United States, many on H-1B and L-1 visas. A company that just admitted it "faltered" is a company that will restructure — and restructuring, in the current environment, means cutting traditional software roles while hiring for AI-native ones.

Second, the leadership story. Krishna, who took the helm in 2020, has been trying to pivot IBM toward hybrid cloud and AI through its Red Hat acquisition and its Watsonx platform. That strategy is now colliding with a market that wants to buy hardware, not software. The pressure on him personally will intensify when IBM reports full results on July 22.

Third, the portfolio. Many NRI investors hold IBM — it is a Dow component, a dividend staple, and historically a "safe" technology stock. With shares now down 27% year to date and trading at levels last seen in mid-May, the safety premium has evaporated. IBM's quantum-computing bets (including the $1 billion Anderon unit backed by the Trump administration) are still years from contributing meaningful revenue.

Krishna ended his letter on a note of determination: "Our job is to help our clients through uncertainty, to find paths forward to grow their businesses no matter what is happening in the external environment." Whether Wall Street gives him the time to do that is another question entirely."""
    },

    # ── Article 2: Meta AI Layoff Lawsuit ──────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Used AI to Decide Who Gets Fired. Twenty-Six Workers Are Suing.",
        "subheadline": "A landmark lawsuit alleges Meta relied on its own Llama-powered tools — including keystroke monitoring and AI-token usage scores — to build a termination list that disproportionately targeted employees on medical leave. It is the first case of its kind.",
        "slug": make_slug("meta-ai-layoff-lawsuit-metamate-discrimination"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta employs thousands of Indian engineers on H-1B visas. If AI-driven layoff tools become standard and courts find them discriminatory, the precedent could reshape how every major tech employer makes workforce decisions — with outsized consequences for visa-dependent workers.",
        "tags": ["meta", "ai-layoffs", "discrimination", "metamate", "llama", "h-1b", "workplace-ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/meta-used-ai-target-workers-with-medical-conditions-layoffs-lawsuit-claims-2026-07-14/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/meta-workers-accuse-it-of-using-ai-to-conduct-discriminatory-layoffs-f76e45b4"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/money/2026/07/15/meta-lawsuit-ai-layoffs-disabled-workers/"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/technology/meta-employees-sue-allegations-company-used-ai-target-workers-medical-parental-leave-layoffs"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meta_Platforms_Headquarters_Menlo_Park_California.jpg/1280px-Meta_Platforms_Headquarters_Menlo_Park_California.jpg",
        "image_caption": "Meta Platforms headquarters in Menlo Park, California",
        "image_attribution": "Wikimedia Commons",
        "body": """When Meta slashed 8,000 jobs in May — nearly 10% of its global workforce — Mark Zuckerberg framed the cuts as a necessary step toward becoming an "AI-first" company. On Monday, twenty-six of those fired employees filed a lawsuit claiming Meta took that philosophy too literally: they allege the company used its own artificial intelligence to choose who would lose their jobs.

The lawsuit, filed in federal court in Oakland, California, may be the first in the United States to directly challenge the use of AI in conducting mass layoffs at a major corporation. If it succeeds, the implications will extend far beyond Meta's campus in Menlo Park.

## The Machines That Made the List

According to the complaint, Meta deployed what it calls a "constellation of internal artificial-intelligence systems" to score, rank and select employees for termination. The tools are now at the centre of the case.

**Metamate**, a large language model assistant built on Meta's own Llama architecture, was used for coding, research and drafting communications. The lawsuit alleges its usage data fed into productivity rankings.

A **"second brain"** tool tracked employees' communications, documents and work output — effectively creating an AI-powered surveillance layer that learned each worker's patterns.

A separate **productivity-scoring system** drew from keystroke monitoring, screen content, emails and browser history to assign numerical performance ratings.

Finally, **AI-token usage dashboards** measured how frequently employees used Meta's internal AI tools — with higher usage apparently counting in their favour.

The 26 plaintiffs — anonymous managers, engineers, scientists and researchers from six states — argue that none of these systems accounted for legally protected time off. Employees on medical leave, disability accommodation, pregnancy leave or family-care leave simply registered lower activity. The AI scored them accordingly.

"The result was that employees who took protected leaves were disproportionately selected for layoff, based on scoring that not only failed to account for their protected leaves, but in effect penalized the employees for exercising their legal rights," the complaint states.

One plaintiff was notified she was being laid off two days before giving birth.

## Meta's Defence

A Meta spokesperson rejected the claims. "These claims lack merit and are not based on facts. Workforce management and organizational decisions were and are made by people, not AI," the company said.

That distinction — human decisions informed by AI versus AI decisions rubber-stamped by humans — is likely to become the central legal battleground. The plaintiffs allege that Meta's process was so automated that human managers were effectively ratifying a machine-generated list.

The lawsuit invokes the Americans with Disabilities Act, the Family and Medical Leave Act, the Pregnancy Discrimination Act and the Pregnant Workers Fairness Act. It also cites recently adopted laws in California and New York City that specifically require companies to test AI systems used in employment decisions for bias.

## The Diaspora Stakes

For Indian tech workers, this case matters in ways that go beyond Meta's walls.

Meta is one of the largest H-1B sponsors in the technology sector, with thousands of Indian engineers and researchers across its Menlo Park, New York and Seattle offices. When a company of Meta's size uses algorithmic tools to determine layoffs, H-1B holders face a compounded vulnerability: they lose not only their jobs but their immigration status, with just 60 days to find new employment or leave the country.

If AI-driven termination scoring becomes industry standard — and every sign suggests it will, given that companies like Thomson Reuters are already restructuring around "AI-native" roles — the question of whether these tools are fair to workers on protected leave becomes existential for the entire sector.

The broader pattern is clear. Earlier this year, Meta also laid off another 7,000 workers who were reassigned to AI-focused roles. CEO Zuckerberg has since said he does not expect additional company-wide layoffs this year. But the 26 plaintiffs whose jobs are set to be eliminated on July 22 are asking the court to block those terminations while they pursue arbitration.

The case now moves into early proceedings, where Meta's internal AI systems — and the data they produced — will face their first real legal scrutiny. For every company building AI tools to manage its workforce, the outcome will be precedent-setting. For every H-1B engineer wondering whether an algorithm just decided their future, it already is."""
    },

    # ── Article 3: AI Engineer Replacement Wave ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Thomson Reuters Is Cutting 500 Engineers and Hiring 250 AI-Native Ones. That Swap Is the Entire Tech Industry Now.",
        "subheadline": "The company's layoffs are part of a staggering pattern: 120,000 tech workers fired across 228 companies in 2026, with projections reaching 342,000 by year's end. For Indian engineers on work visas, the maths is getting hostile.",
        "slug": make_slug("thomson-reuters-ai-native-engineer-replacement-wave"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Software engineering is the single largest H-1B occupation category. As companies replace traditional engineering roles with AI-native positions that demand different skills, hundreds of thousands of Indian visa holders face a narrowing window to retool or risk losing their immigration status.",
        "tags": ["ai-layoffs", "software-engineering", "h-1b", "thomson-reuters", "tech-jobs", "ai-native"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/media-telecom/thomson-reuters-cut-small-number-engineering-jobs-2026-07-14/"},
            {"name": "Challenger, Gray & Christmas via PYMNTS", "url": "https://www.pymnts.com/news/artificial-intelligence/2026/tech-layoffs-hit-2-year-high-as-companies-embrace-ai/"},
            {"name": "Le Monde", "url": "https://www.lemonde.fr/en/economy/article/2026/07/11/when-it-comes-to-ai-nothing-s-right-silicon-valley-is-torn_6756901_19.html"},
            {"name": "Layoffs.fyi", "url": "https://layoffs.fyi/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg",
        "image_caption": "A software developer working at a dual-monitor setup in a modern office",
        "image_attribution": "Pexels",
        "body": """Thomson Reuters announced on Monday that it is cutting "a small number" of engineering roles. The actual figure, according to an employee who attended the internal meeting, is closer to 500 — roughly 5.2% of the company's 9,400-strong operations and technology unit.

In isolation, 500 jobs at a content and technology company would barely register. What makes the number worth paying attention to is the other half of the announcement: Thomson Reuters expects to hire more than 250 new engineering roles over the next two years. The large majority, the company said, will be "senior and AI-native."

Kill 500 traditional roles. Hire 250 AI-fluent ones. The arithmetic is blunt, and it is now the operating playbook of the entire technology sector.

## The Numbers Are Getting Severe

According to the jobs tracker Layoffs.fyi, approximately 120,000 tech workers have lost their jobs across 228 companies in 2026. Challenger, Gray & Christmas, the outplacement firm that has tracked layoffs for decades, reports that artificial intelligence has been the leading reason cited by employers for job cuts for three consecutive months, with technology the largest sector by volume.

In May alone, 38,242 tech jobs were eliminated — the steepest monthly cut since early 2023, even as the sector simultaneously posted the most hiring plans of any industry. The paradox is now structural: companies are shedding one type of engineer and aggressively recruiting another.

Bloomberg analysts project that AI-related job displacement could affect up to 502,000 roles economy-wide in 2026. The website TrueUp estimates that the technology sector alone will finish the year with approximately 342,000 job cuts, up from 246,000 in 2025.

The pattern across companies is remarkably consistent. Meta cut 8,000 in May and reassigned 7,000 more to AI-focused roles. Intuit eliminated approximately 3,000 positions. Oracle, LinkedIn and Amazon have all made significant reductions. Thomson Reuters is simply the latest company to make the swap explicit.

## The Two-Speed Workforce

What is emerging is a bifurcated labour market within technology. On one side, engineers who write traditional software — the kind of work that has sustained hundreds of thousands of H-1B careers — are watching AI coding tools eat into their value proposition. On the other, a smaller cohort of engineers who know how to build, fine-tune and deploy AI systems are commanding premium salaries and multiple competing offers.

Le Monde reported this month on the phenomenon in San Francisco, where engineers described working "like crazy" alongside AI agents that write code, replacing some of their colleagues. The newspaper quoted one founder who compared the capability jump from recent AI models to "going from the level of a not-so-great intern to that of an engineer with two or three years of experience."

Job-search timelines have stretched accordingly. Industry data from outplacement firms suggests the average time to find a new tech role is now three to six months for experienced engineers, with senior and executive positions taking six to nine months. Workers in AI-adjacent roles — machine learning engineers, data scientists, AI product managers — report shorter searches averaging two to three months.

## The H-1B Calculus

For Indian engineers on work visas, the maths is especially unforgiving.

Software engineering is the single largest occupational category for H-1B visa holders. When a company like Thomson Reuters eliminates 500 traditional engineering positions, a disproportionate share of those affected are likely to be visa-dependent workers — the same workers who, under immigration law, have just 60 days to find new sponsorship or face departure from the country.

The skills gap compounds the problem. An engineer who has spent a decade building Java enterprise applications or maintaining legacy systems cannot overnight become a machine-learning specialist. The "AI-native" roles that companies are creating demand fundamentally different expertise: model training, prompt engineering, retrieval-augmented generation, agentic workflow design. These are skills that most computer-science programmes did not teach even two years ago.

Thomson Reuters put it plainly: it is "focusing our capacity where it matters most to customers." For engineers on the wrong side of that focus, the message is equally plain. Retool, or risk becoming the role that gets automated.

The cruel irony is that the very AI systems making some engineers redundant are also the tools that could help them learn new skills faster than any previous technology. Whether that opportunity window stays open long enough — particularly for visa holders who cannot afford a career gap — is the question that will define the next chapter of the Indian technology diaspora in America."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
