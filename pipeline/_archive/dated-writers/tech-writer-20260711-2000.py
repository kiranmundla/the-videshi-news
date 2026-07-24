#!/usr/bin/env python3
"""Technology writer — 2026-07-11 20:00 PT run. Three articles."""

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

# ─── ARTICLE 1: Apple Sues OpenAI ─────────────────────────────

art1_body = """Apple filed a federal lawsuit against OpenAI on Friday, accusing Sam Altman's company of orchestrating a systematic campaign to steal trade secrets and confidential hardware designs. The complaint, filed in the U.S. District Court for the Northern District of California, marks a dramatic rupture between two companies that were, until recently, business partners.

The allegations centre on two former Apple employees now working at OpenAI: Tang Yew Tan, who spent 24 years at Apple as vice president of product design for the iPhone and Apple Watch, and Chang Liu, a former senior electrical engineer. Tan is now OpenAI's chief hardware officer. Apple accuses both of directing a coordinated effort to extract confidential information about unreleased devices, components, manufacturing processes, and supplier relationships.

## The 'Show and Tell' Sessions

The most striking allegation involves what Apple describes as "show and tell" sessions during OpenAI job interviews. According to the filing, Tan instructed Apple employees interviewing with OpenAI to bring physical parts — batteries, logic boards, system-in-package components — from Apple's offices. One candidate reportedly told interviewers he "didn't even know we could take those from the office."

Liu, the complaint alleges, failed to return his company-issued laptop after departing for OpenAI in January, then used an authentication bug to access Apple's internal network and download "dozens of Apple's confidential hardware-related files." A colleague, Alyssa Peng, who subsequently left Apple for OpenAI in April, allegedly assisted in the effort.

Apple claims more than 400 former employees now work at OpenAI. While hiring from competitors is legal in California — it is, in fact, the cultural norm that built Silicon Valley — the company argues that OpenAI went far beyond legitimate talent acquisition. "That OpenAI now employs people who were once entrusted with Apple's trade secrets does not entitle OpenAI to use that information to jumpstart its hardware efforts," the filing reads.

## A Partnership Turns to Rivalry

The lawsuit's timing is striking. In 2024, Apple announced the integration of ChatGPT into its devices, with Altman appearing at Apple's headquarters for the announcement. That partnership allowed iPhone users to access ChatGPT through Siri and subscribe to memberships directly from iOS settings.

But the relationship has soured. Apple's long-delayed Siri overhaul, which finally shipped last month, is now built on Google's Gemini models rather than ChatGPT. OpenAI, meanwhile, acquired io Products — the hardware startup founded by former Apple design chief Jony Ive — for $6.5 billion last year, signalling its ambitions to move beyond software and into consumer devices.

"Apple sees OpenAI moving from partner to potential rival, while OpenAI is trying to reduce its dependence on the iPhone and build a direct relationship with consumers," said PP Foresight analyst Paolo Pescatore.

OpenAI denied the allegations. "We have no interest in other companies' trade secrets," the company said. "We remain focused on building innovative technology that empowers people everywhere."

## What It Means for the Diaspora

The lawsuit exposes a tectonic shift in how Silicon Valley's biggest companies compete for talent — and Indian engineers are squarely in the middle of it. Apple, Google, and OpenAI collectively employ tens of thousands of Indian-origin engineers, many on H-1B visas. A legal precedent that tightens what departing employees can carry to new employers could reshape mobility across the industry.

Stanford Law School professor Mark Lemley noted that Apple's complaint "has the potential to be a very big case," though he cautioned that much of what Apple alleges — including mass hiring from a competitor — is not illegal under California law. "But if Apple's claims that the employees took confidential documents with them — and that OpenAI is using those documents — are true, that is a problem for OpenAI," he said.

For the estimated 400-plus former Apple employees now at OpenAI, the lawsuit raises uncomfortable questions about the line between personal expertise and proprietary knowledge — a distinction that matters enormously to anyone who has ever changed jobs in the Valley."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Just Declared War on OpenAI. The Lawsuit Could Reshape How Silicon Valley Hires.",
    "subheadline": "Cupertino accuses Sam Altman's company of orchestrating a campaign to poach over 400 employees and steal hardware secrets, including asking job candidates to smuggle iPhone parts into interviews.",
    "slug": make_slug("apple-sues-openai-trade-secrets-hardware-talent-war"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Hundreds of Indian engineers at both Apple and OpenAI are caught in an escalating talent war that could tighten employment mobility across Silicon Valley, where tens of thousands of Indians work on H-1B visas.",
    "tags": ["apple", "openai", "trade-secrets", "silicon-valley", "talent-war", "hardware"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/litigation/apple-sues-openai-alleging-misappropriation-trade-secrets-court-records-show-2026-07-10/"},
        {"name": "MacRumors", "url": "https://www.macrumors.com/2026/07/10/apple-sues-openai-trade-secrets/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/apple-sues-openai-trade-secrets-laptop-b5f10c20"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Apple_Park.jpg/1280px-Apple_Park.jpg",
    "image_caption": "Apple Park headquarters in Cupertino, California",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ─── ARTICLE 2: OpenAI ChatGPT Work + GPT-5.6 ────────────────

art2_body = """OpenAI launched its most ambitious product overhaul yet on Thursday, unveiling ChatGPT Work — a new AI agent that merges the company's chatbot with its Codex coding tool — alongside GPT-5.6, its latest and most powerful model. The twin release represents OpenAI's clearest bid to move beyond the chatbot paradigm and into the enterprise software business, where the real money is.

ChatGPT Work is designed for non-coders who want access to what coding tools can do: create documents, presentations, spreadsheets, and even full websites, then hand them off to the tools professionals already use. It can pull context from Slack, Microsoft Teams, Google Drive, SharePoint, email, calendars, CRMs, and project trackers, either automatically or when explicitly directed.

"You can apply the model's ability to code to solve problems across every industry," said Ty Geri, OpenAI's product manager for ChatGPT Work.

## Three Models, One Strategy

GPT-5.6 arrives in three tiers under a new naming system: Sol, Terra, and Luna. Sol is the flagship — OpenAI's most capable reasoning model, designed for complex coding, knowledge work, cybersecurity, and scientific tasks. Terra matches GPT-5.5's performance at roughly half the cost. Luna is the fastest and cheapest, aimed at high-volume, cost-sensitive applications.

API pricing tells the story: Sol costs $5 per million input tokens and $30 per million output tokens; Terra runs at $2.50/$15; Luna at $1/$6. For Indian startups operating on tighter budgets, Luna's price point opens a tier of AI capability that was, until recently, affordable only to well-funded Silicon Valley ventures.

The model's launch was delayed last month at the U.S. government's request over national security concerns — a sign of how seriously Washington is now scrutinising frontier AI releases.

## The Atlas Experiment Ends

The launch also marks the quiet death of Atlas, OpenAI's experimental AI-first web browser, which never made it to its first birthday. Atlas is being replaced by a built-in browser within the ChatGPT desktop app, which lets the AI gather web information and work with cloud-based files directly.

OpenAI is also merging its standalone Codex application into the unified ChatGPT desktop app. The company says more than five million people already use Codex weekly, with over one million using it for tasks outside software development — in sales, finance, and marketing workflows. The old desktop app has been renamed "ChatGPT Classic."

A new Scheduled Tasks feature lets the agent continue working even when a user is away, converting new Slack or Teams messages into updated documents and flagging changes automatically. A Computer Use feature on Windows lets ChatGPT operate keyboard and mouse commands in the background, automating routine desktop operations.

## The Enterprise AI Arms Race

The launch pits OpenAI directly against Anthropic's Claude Cowork, which debuted in January with similar multi-step task automation, and Microsoft's Copilot — an awkward dynamic given that Microsoft is OpenAI's largest investor.

Both OpenAI and Anthropic are preparing for potential initial public offerings, making enterprise revenue critical. ChatGPT Work is available immediately to Pro, Enterprise, and Education users, with Plus and Business tiers gaining access within days. The updated desktop app is available globally on Mac and Windows for all users, including those on the free plan.

## Why Indian Tech Workers Should Pay Attention

Indian developers and engineers are among the largest cohorts of AI tool power users globally. The Luna tier's pricing — one-fifth the cost of Sol — makes enterprise-grade AI affordable for the tens of thousands of Indian startups that lack the capital to run frontier models at scale.

For the estimated 1.5 million Indian tech professionals working in the United States, the shift from chatbot to autonomous work agent has more immediate implications. If ChatGPT Work delivers on its promise of handling hours-long projects independently, it accelerates the very AI-driven productivity gains that are simultaneously creating new opportunities and compressing the headcount at companies where many Indians are employed.

Max Weinbach, analyst at consulting firm Creative Strategies, noted that the smallest version of GPT-5.6 can complete tasks roughly as well as the largest version — at one-fifth the cost. "This is the first time where I've seen the small models complete these kinds of tasks," he said. For Indian IT services firms already navigating AI-driven pricing pressure, that sentence should land heavily."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "OpenAI's New 'Super App' Can Work for Hours Without You. Its Cheapest Model Is the One to Watch.",
    "subheadline": "ChatGPT Work merges the chatbot with Codex under a single roof, powered by GPT-5.6 in three tiers. The smallest model does the same work at one-fifth the price — a detail that should worry Indian IT giants and excite Indian startups.",
    "slug": make_slug("openai-chatgpt-work-gpt-56-super-app-enterprise-ai"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian developers are among the largest non-American cohort of AI tool power users, and GPT-5.6's aggressive Luna pricing makes enterprise-grade AI accessible to Indian startups while accelerating the automation pressure on IT services firms that employ hundreds of thousands of Indians.",
    "tags": ["openai", "chatgpt", "gpt-5.6", "ai-agents", "enterprise-ai", "codex"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/openai-launches-chatgpt-work-its-super-app-enterprises-2026-07-10/"},
        {"name": "The Register", "url": "https://www.theregister.com/2026/07/11/openai_atlas_chatgpt_work/"},
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/openais-chatgpt-work-brings-gpt-5-6-and-codex-together-for-smarter-workflows"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/deeptech/artificial-intelligence/openai-just-turned-chatgpt-into-your-new-coworker-heres-how-to-get-started"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "OpenAI CEO Sam Altman at a meeting in February 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ─── ARTICLE 3: H-1B Rule Changes Coming in August ────────────

art3_body = """The Trump administration is preparing the most sweeping overhaul of the H-1B visa system in years, with a regulatory package expected as early as August that would tighten third-party placements, raise minimum salary thresholds for Green Cards, and strip international students of the open-ended stays they have relied on for decades. For India's $315 billion IT services industry, the changes threaten the core business model.

The proposals, outlined in the Unified Regulatory Agendas released by the Departments of Homeland Security, Labour, and State, are not yet in effect. But their scope — spanning H-1B visas, Green Cards, OPT work permits, and H-4 spousal employment authorisation — suggests a coordinated effort to fundamentally restructure how skilled foreign workers enter and remain in the American labour market.

## Third-Party Placements Under Fire

The most consequential proposal for Indian IT companies targets third-party client-site placements — the operational backbone of firms like TCS, Infosys, Wipro, and HCL Technologies, which deploy tens of thousands of engineers at American corporate clients.

A DHS rule expected in August would impose stricter employer-employee relationship requirements for these placements and trigger enhanced scrutiny of employers with prior compliance violations. The 85,000-unit annual H-1B cap would remain unchanged, but exemptions available to universities and research organisations would be tightened.

A separate provision would extend the existing supplemental fee — currently covering only initial petitions and employer changes — to extension applications as well, targeting companies with more than 50 U.S. employees where over half the workforce holds H-1B or L-1 visas. That description fits the American operations of most major Indian IT firms almost precisely.

## The Green Card Gets More Expensive

The Department of Labour is revising the wage levels used in H-1B and PERM labour certification cases. The entry-level benchmark would jump from the 17th percentile to the 34th percentile, with higher tiers also increasing. In practical terms, this means employers would need to pay significantly more to sponsor foreign workers for permanent residency.

Additional PERM changes covering recruitment standards, layoffs of American workers, and anti-discrimination provisions are also planned. The combined effect would make existing Green Card pathways substantially more expensive and administratively burdensome — a particular blow for Indian professionals, who already face the longest wait times of any nationality due to per-country caps.

## Students Lose Their Safety Net

India sent 360,000 students to the United States in 2024-25, making it the single largest source of international students. The DHS plans to replace the current "duration of status" system — which allows students to remain as long as they meet programme requirements — with fixed-period stays requiring extension applications.

A separate proposal, expected in February 2027, would restrict the two-year STEM Optional Practical Training extension and Curricular Practical Training, the most commonly used pathways for Indian students to gain American work experience after completing their degrees.

## H-4 Spouses Face a Gap

Perhaps the most immediately consequential change is a final rule, expected this month, ending automatic Employment Authorisation Document extensions that were introduced under an October 2025 interim rule. H-4 holders — predominantly Indian spouses of H-1B workers caught in Green Card backlogs — could temporarily lose work authorisation if renewal processing is delayed, even when applications are filed within the required 180-day window.

## The Bigger Picture

Indians account for 73 per cent of all approved H-1B petitions, according to USCIS data — roughly 284,000 out of 406,000 approved in fiscal year 2025. They represent the largest share of Green Card applicants and a significant portion of the international student cohort.

The regulatory push arrives at an already difficult moment. Vice President JD Vance announced this week a large-scale investigation into H-1B visa fraud, and Microsoft's Xbox division laid off 1,600 workers while holding approval to hire over 2,200 H-1B employees — a juxtaposition that has fuelled bipartisan anger on Capitol Hill.

For the 1.5 million-odd Indian tech professionals in the United States, the message from Washington is unmistakable: the era of relatively frictionless skilled immigration is yielding to one in which every visa renewal, every client placement, and every Green Card application will cost more and require more justification than it did a year ago. Whether that makes America more competitive or merely more expensive remains an open question."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Is About to Rewrite the H-1B Playbook. Indian IT Giants Should Be Worried.",
    "subheadline": "A sweeping regulatory package expected in August would tighten third-party placements, raise Green Card wage floors, and end open-ended student stays. For TCS, Infosys, and Wipro, the operating model itself is on trial.",
    "slug": make_slug("h1b-visa-rules-august-overhaul-indian-it-third-party"),
    "category": "technology",
    "vertical": "immigration",
    "diaspora_angle": "Indians account for 73 per cent of all approved H-1B petitions. The proposed rules directly target the third-party placement model used by Indian IT firms and would raise costs for Green Card sponsorship, restrict student work permits, and create gaps in spousal employment authorisation.",
    "tags": ["h-1b", "immigration", "indian-it", "visa-policy", "green-card", "tcs", "infosys"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/h-1bs-opt-and-h-4-visas-whats-changing-for-indians-under-trumps-immigration-plan"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-wage-proposal-slotted-for-august-as-dhs-plots-slew-of-rules"},
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Capitol_at_Dusk_2.jpg/1280px-Capitol_at_Dusk_2.jpg",
    "image_caption": "The United States Capitol building at dusk in Washington, D.C.",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body,
}

# ─── INSERT ───────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:60]}...")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
