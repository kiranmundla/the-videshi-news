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
        "headline": "NVIDIA Is Hiring 1,200 Foreign Workers While Google and Amazon Cut Theirs in Half",
        "subheadline": "As Big Tech slashes H-1B sponsorships amid AI restructuring, Jensen Huang's chipmaker is offering Indian engineers up to $391,000 in base pay — and absorbing a $100,000-per-visa government fee to do it.",
        "slug": make_slug("nvidia-h1b-hiring-surge-indian-engineers-big-tech-cuts"),
        "category": "technology",
        "vertical": "immigration",
        "diaspora_angle": "Indian professionals hold 71-73% of all H-1B visas — NVIDIA's counter-cyclical hiring expansion is a rare lifeline for thousands of Indian engineers facing layoffs and the 60-day grace period crunch at other tech giants.",
        "tags": ["nvidia", "h-1b", "immigration", "indian-engineers", "silicon-valley", "jensen-huang", "hiring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/amp/corporate/inside-nvidias-global-talent-push-h-1b-surge-and-467-crore-salaries-for-ai-researchers-architects-and-engineers"},
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com/2026/06/03/nvidia-tackles-tech-layoffs-with-high-paying-ai-hiring/"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/nvidia-expands-h1b-hiring-amid-job-loss-reports-due-to-ai-1717322040234"},
            {"name": "Computerworld", "url": "https://www.computerworld.com/article/3749849/restrictive-h-1b-policies-drive-tech-talent-back-to-india-reshaping-global-it.html"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang at a company event in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Something unusual is happening in Silicon Valley's immigration landscape. While Google, Amazon, and Meta are pulling back from foreign talent sponsorship — slashing H-1B visa certifications by as much as 50 per cent — NVIDIA is doing the opposite. The AI chipmaker secured approximately 1,200 H-1B certifications during the first two quarters of fiscal year 2026, a 20 per cent increase from the 1,000 it filed during the same period last year.

The numbers tell a stark divergence story. Google's approved H-1B hires dropped to roughly 2,200, down from 5,100 a year earlier. Amazon's fell to about 4,300 from 6,100. The pattern across Big Tech is unmistakable: companies are trimming the foreign workforce even as they pour hundreds of billions into AI infrastructure. NVIDIA, which sits at the centre of that infrastructure build, is moving in the opposite direction.

## The pay is not subtle

Federal labour filings reveal the scale of NVIDIA's compensation. Software engineers command base salaries of up to $391,000. Architecture directors — the engineers designing the GPU pipelines that underpin every major AI model — earn up to $488,750 in base pay alone, before stock options, bonuses, or restricted stock units that have ballooned alongside NVIDIA's stratospheric share price.

Research scientists start at roughly $120,000 and climb past $410,000. Hardware engineering managers land between $225,000 and $425,000. These are not Silicon Valley outliers; they are the going rate at a company that posted $81.62 billion in quarterly revenue on the back of insatiable data-centre demand.

For context, the Trump administration's $100,000 fee on new H-1B petitions — imposed in September 2025 — would add roughly $120 million to NVIDIA's annual visa costs. The company is absorbing it without flinching. As Jensen Huang, who was born in Taiwan and has repeatedly championed legal immigration, put it: talent is not a cost centre. It is the business.

## Why this matters to Indian engineers

Indians hold between 71 and 73 per cent of all approved H-1B visas in the United States. They are disproportionately concentrated in the technology sector — at exactly the companies now trimming headcount. When Meta lays off a team or Google restructures a division, the American workers get severance and a job search. The Indian worker on an H-1B gets 60 days.

That is not a policy nuance. It is a life-altering countdown. Within two months of losing a role, an H-1B holder must either secure a new employer willing to sponsor a transfer or leave the country — often uprooting a family, pulling children from schools, and abandoning a decade of accumulated life in the US.

NVIDIA's expansion offers a counter-narrative. The company is not just maintaining its foreign workforce; it is actively growing it, in roles that sit at the highest end of the technical spectrum: GPU architecture, CUDA optimisation, AI model training infrastructure, and hardware-software co-design. These are specialisations where Indian engineers from IITs, BITS, and other top institutions have built deep expertise over decades.

## The broader structural shift

LinkedIn's most recent Labour Market Report paints a wider picture. India's technology hiring has surged 40 per cent above pre-pandemic levels, while the US and other advanced economies have seen a 23 per cent decline. Companies headquartered in the US, UK, Germany, and France are all increasing their share of India-based hiring.

The $100,000 H-1B fee is accelerating this rebalancing. For mid-tier IT services firms — the TCSes, Infosyses, and Wipros that once sponsored thousands of visas annually — the economics of sending an engineer to Cupertino are becoming prohibitive. The result is a structural pull toward hiring in Bengaluru and Hyderabad instead.

But NVIDIA's calculus is different. At the frontier of AI hardware, where a single architectural decision can determine whether a $500 million data-centre deployment succeeds or fails, the company cannot afford to limit its talent pool by geography. The H-1B fee is a rounding error on a $120 billion annual revenue run.

## The two-speed immigration economy

What is emerging is a bifurcated landscape for Indian tech professionals in America. At one end, NVIDIA and a handful of AI-focused companies are offering extraordinary compensation and visa stability. At the other, tens of thousands of experienced engineers at enterprise software, consulting, and legacy tech firms face a labour market that is simultaneously automating their roles and making their immigration status more precarious.

For the Indian professional weighing a career in the US, the message is increasingly clear: the visa system rewards the apex of technical specialisation. Generalist software engineering — the bread and butter of the Indian IT boom for two decades — is losing its immigration economics. The engineers who can design a GPU memory subsystem or optimise a transformer model's inference pipeline have never been more valued. Everyone else is watching the ground shift beneath them."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Freshworks Cuts 500 Jobs After AI Takes Over Half Its Codebase",
        "subheadline": "The Chennai-born SaaS company's revenue is up 16 per cent. Its headcount is down 11 per cent. Welcome to the new math of AI-native software development.",
        "slug": make_slug("freshworks-layoffs-500-ai-code-indian-saas"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Freshworks was the poster child of India's SaaS ambitions — the first Indian-founded company to IPO on the Nasdaq. Its decision to slash 500 jobs because AI writes half the code raises uncomfortable questions about the future of Indian software engineering talent.",
        "tags": ["freshworks", "layoffs", "ai-coding", "indian-saas", "automation", "software-engineering"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Computer Weekly", "url": "https://www.computerweekly.com/news/366623527/Freshworks-Refresh-2026-pivot-to-AI-driven-employee-experience"},
            {"name": "Moneycontrol", "url": "https://www.moneycontrol.com/news/business/tech3-flipkarts-ai-a-team-anthropic-backtracks-after-blowup-and-more-13107891.html"},
            {"name": "Freshworks Investor Relations", "url": "https://ir.freshworks.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg",
        "image_caption": "A software developer working on code at a dual-monitor setup in a modern office",
        "image_attribution": "Pexels",
        "body": """Freshworks, the customer-service and IT-management software company founded in Chennai by Girish Mathrubootham, has laid off roughly 500 employees — about 11 per cent of its workforce. The reason, stated with remarkable candour by CEO Dennis Woodside during the company's Q1 2026 earnings call: more than half of Freshworks' code is now written by artificial intelligence.

"About over half of our code is originated in AI today," Woodside told analysts. "That is definitely changing how we build products, how fast we can build products, and the amount of people who we need to build products."

The quarterly numbers, taken on their own, are healthy. Revenue rose 16 per cent year-over-year to $228.6 million. The company's product suite — spanning customer service, IT service management, and CRM — continues to grow. But the workforce shrinking alongside growing revenue is precisely the pattern that has Silicon Valley's software engineers, and India's IT workforce in particular, watching with unease.

## From Chennai to Nasdaq — and back to fewer desks

Freshworks occupies a singular place in the Indian tech diaspora's imagination. When Mathrubootham listed the company on the Nasdaq in September 2021, the stock surged 32 per cent on its first day. Here was a company conceived in India, built substantially by Indian engineers, competing head-on with Salesforce and ServiceNow on Wall Street. It was proof that Indian-founded enterprise software could scale globally without being an outsourcing play.

The irony of its current moment is difficult to ignore. The company that employed thousands of Indian software engineers is now shedding them because AI tools — GitHub Copilot, Amazon CodeWhisperer, and their ilk — have made each remaining engineer dramatically more productive. The same engineers who once wrote the code are being replaced by the code they helped make possible.

Freshworks is hardly alone. Across the enterprise software landscape, companies are reporting similar patterns: faster development cycles, fewer engineers needed per feature, and a growing portion of production code that originates from AI suggestions rather than human keystrokes. Klarna cut its engineering team and credited AI for maintaining output. Duolingo reduced contractor reliance for the same reason.

## The Indian IT ripple effect

For the roughly five million people employed by India's IT services industry — at TCS, Infosys, Wipro, HCL Tech, Cognizant, and hundreds of smaller firms — the Freshworks announcement is less a single data point than a confirmation of what many already feared.

The traditional Indian IT model is built on labour arbitrage: a software engineer in Bengaluru costs a fraction of one in San Francisco, and the difference funds the entire services business. But when AI compresses the denominator — when fewer engineers produce the same or greater output — the arbitrage narrows. A company that once needed 200 engineers for a product now needs 120. The ones retained are the architects, the system designers, the engineers who can evaluate and integrate AI-generated code. The ones let go were writing the boilerplate that machines now handle faster.

Freshworks' pivot at its Refresh 2026 conference in New York made the strategic direction explicit. The company is repositioning around agentic AI — autonomous systems that can handle customer queries, triage IT tickets, and manage workflows without human intervention. Pradeep Rathinam, who oversees the company's AI and customer experience strategy, described it as a shift from "AI as a tool" to "AI as a colleague."

## What this means for NRI engineers

For Indian-origin software engineers in the US — whether at Freshworks, a FAANG company, or one of the thousands of mid-market SaaS firms that employ H-1B holders — the lesson is structural, not cyclical.

The roles that are expanding require a different kind of engineer: one who can design system architectures, evaluate AI output for correctness and security, manage complex integrations, and work at the intersection of product strategy and technical execution. The roles that are contracting are the ones that produced volume — lines of code, test cases, feature implementations — without deep architectural judgment.

India's engineering colleges produce roughly 1.5 million computer science graduates each year. The subset that can compete at the level now being demanded by companies like Freshworks and its peers is considerably smaller. That gap — between the volume of trained engineers and the quality demanded by an AI-augmented workplace — is becoming the defining challenge for India's technology workforce.

Mathrubootham, who stepped down as CEO in 2024 but remains executive chairman, built Freshworks on the conviction that world-class software could be built from India. The company's latest move suggests a refinement of that thesis: world-class software can still be built from India, but with significantly fewer people, and an entirely different skill set."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "China's $295 Billion AI Grid Bans NVIDIA and AMD. Thousands of Indian Engineers Are Caught in Between.",
        "subheadline": "Beijing's five-year data-centre plan mandates 80 per cent domestic technology, squeezing out the US chipmakers where tens of thousands of Indians design the silicon. India's own AI infrastructure spend is a fraction of either rival.",
        "slug": make_slug("china-295-billion-ai-grid-nvidia-amd-indian-engineers"),
        "category": "technology",
        "vertical": "geopolitics",
        "diaspora_angle": "Tens of thousands of Indian engineers at NVIDIA, AMD, and other US chipmakers design the very silicon that China's domestic mandate aims to replace — putting their work at the centre of an escalating superpower tech war while India's own AI infrastructure spend remains a rounding error.",
        "tags": ["china", "ai-infrastructure", "nvidia", "amd", "semiconductor", "geopolitics", "india-chip-mission"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/china-prepares-295-billion-plan-fund-nationwide-ai-buildout-bloomberg-news-2026-06-09/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/china-to-spend-300-billion-on-data-centers-boosting-high-tech-manufacturing-and-ai-infrastructure-5044/"},
            {"name": "KED Global", "url": "https://www.kedglobal.com/korean-chipmakers/samsung-likely-to-make-part-of-googles-icefish-ai-chip-after-winning-165-bn-tesla-order/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-06-09/china-drafts-plan-to-spend-295-billion-on-nationwide-ai-buildout"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg",
        "image_caption": "Server racks inside a modern data centre facility",
        "image_attribution": "Pexels",
        "body": """China is preparing to spend 2 trillion yuan — roughly $295 billion — over the next five years to build a nationwide grid of interconnected AI data centres. The plan, drafted by the National Development and Reform Commission and reported by Bloomberg, has a stipulation that should concern every Indian engineer working at an American chipmaker: at least 80 per cent of the technology inside these data centres must be sourced from domestic Chinese suppliers.

That means Huawei, not NVIDIA. SMIC, not TSMC. Cambricon and Enflame, not AMD. The world's second-largest economy is explicitly building its AI future without the companies where tens of thousands of Indian engineers design the most advanced silicon on the planet.

## The scale of the squeeze

To understand the magnitude, consider the spending comparison. US Big Tech companies — Meta, Microsoft, Google, Amazon — are collectively expected to invest more than $700 billion in AI infrastructure this year alone. China's $295 billion over five years is smaller in absolute terms, but it comes with structural advantages: lower construction costs, state-directed land allocation, and no NIMBYism to delay permitting.

State-owned enterprises China Mobile and China Telecom will operate the bulk of the data centres and ensure their interconnection, creating a national computing grid that can distribute AI workloads across the country. Beijing has already required that any data-centre project receiving state funds use only domestically manufactured AI chips — a policy that has been in place since last year. The new plan formalises and massively expands that mandate.

For NVIDIA, which derives a meaningful portion of its revenue from the Chinese market despite escalating US export controls, the signal is unambiguous: China is not just adapting to the chip embargo. It is building an alternative ecosystem designed to make American semiconductors permanently irrelevant within its borders.

## Where Indian engineers sit in this fault line

The geopolitical dimension is abstract until you consider who actually designs these chips. At NVIDIA's headquarters in Santa Clara, Indian engineers constitute a significant fraction of the workforce — particularly in GPU architecture, CUDA software development, and AI model optimisation. The same is true at AMD in San Jose, at Intel's design centres, and at Qualcomm in San Diego.

These are the engineers who secured H-1B visas, built careers in the US, and now find their professional output at the centre of a superpower technology war. The chips they design are simultaneously the most valuable technology in the world and the technology that one of the world's two largest markets has decided to stop buying.

The dynamic creates a peculiar exposure. An Indian GPU architect at NVIDIA is not losing her job — demand from US hyperscalers is still overwhelming. But the addressable market for her work is shrinking geographically. Revenue ceilings, export compliance reviews, and the strategic risk of customer concentration in the US and allied markets are all consequences of China's domestic pivot.

## India's position: a rounding error in a trillion-dollar race

This is where the story becomes uncomfortable for anyone who cares about India's technological sovereignty. While the US spends $700 billion a year and China commits $295 billion over five years, India's entire semiconductor mission amounts to roughly ₹76,000 crore ($9 billion) — a figure that covers everything from the Tata Electronics fab in Dholera to the Micron assembly plant in Gujarat. The annual budget outlay is a fraction of what NVIDIA alone spends on R&D.

Mohandas Pai, former Infosys CFO, put the gap bluntly last week when he called for an annual ₹50,000 crore ($6 billion) fund for deep tech and AI, along with a ₹2 lakh crore guarantee fund for hypercloud infrastructure. His remarks came after Anthropic restricted access to its Fable 5 and Mythos 5 models outside the US, prompting Zoho's Sridhar Vembu to argue that India must chart its own technological path.

Both are right about the diagnosis. But the prescription remains aspirational. India's AI compute capacity is negligible by global standards. The country has no domestic GPU manufacturer, no foundry capable of advanced nodes, and no hyperscaler with meaningful international scale. The engineers who could build this capacity are, overwhelmingly, in California — designing chips for American companies that are locked out of China.

## The three-way race nobody asked for

What is emerging is a technology cold war with three distinct strategies. The US relies on private-sector spending, global talent (heavily Indian), and export controls to maintain its lead. China relies on state capital, domestic mandates, and a controlled internet to build a parallel stack. India relies on rhetoric, a handful of assembly plants, and the hope that its diaspora engineers will eventually come home.

For the Indian professional navigating this landscape — whether an H-1B engineer at NVIDIA watching China build around her, or a tech policy wonk in Delhi watching both superpowers outspend India by orders of magnitude — the strategic implication is the same. India is a supplier of talent to both sides of the AI arms race, but a principal in neither. Until that changes, its engineers will continue to be the most valuable export from a country that has not yet figured out how to keep them."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
