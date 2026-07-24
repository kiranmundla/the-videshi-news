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

# Verify images
def verify_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
        # fallback to GET for servers that don't support HEAD properly
        r = requests.get(url, timeout=10, stream=True, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", "0"))
        return r.status_code == 200 and "image" in ct
    except Exception as e:
        print(f"  ⚠️ Image verification failed for {url}: {e}")
        return False

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Is Hiring Foreign Workers Faster Than Ever. Google and Amazon Are Pulling Back.",
        "subheadline": "Federal filings show Nvidia certified nearly 1,200 H-1B positions in six months — a 20 per cent jump — while Google's approvals fell 57 per cent and Amazon's dropped 30 per cent. For Indian engineers, the divergence is not academic.",
        "slug": make_slug("nvidia-h1b-hiring-surge-google-amazon-decline"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indians hold 71-73% of all approved H-1B visas. Nvidia's hiring surge is a lifeline for Indian engineers facing layoffs elsewhere in Silicon Valley. The salary data — up to ₹3.74 crore at senior levels — also resets expectations for what top Indian talent can command in the AI economy.",
        "tags": ["nvidia", "h1b-visa", "indian-tech-workers", "silicon-valley", "ai-hiring"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/nvidia-salaries-revealed-software-engineers-can-earn-up-to-3-74-crore-11748814563285.html"},
            {"name": "News Ei Samay", "url": "https://newseisamay.com/nvidia-ramps-up-h1b-hiring-amid-layoffs-offers-rs-4-64-crore-pay/"},
            {"name": "Business Insider (via 7Globe)", "url": "https://7globe.in/h-1b-hiring-boost-nvidia-offers-top-salaries-despite-slowdown-in-foreign-recruitment/"},
            {"name": "NDTV", "url": "https://www.ndtv.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "body": """The numbers are stark. In the first two quarters of fiscal 2026, Nvidia secured certification for nearly 1,200 H-1B positions, up from roughly 1,000 during the same period last year. Google's approved H-1B hires, meanwhile, collapsed from about 5,100 to 2,200. Amazon's fell from 6,100 to 4,300. Meta is actively laying off thousands.

For the tens of thousands of Indian engineers whose right to remain in the United States is tethered to an employer's willingness to sponsor a visa, this divergence is not a data point. It is a map of where to apply next.

## The Only Door That's Opening Wider

The contrast matters because of who holds H-1B visas. Indians account for 71 to 73 per cent of all approved H-1B beneficiaries, according to USCIS-linked data — a dominance that makes every shift in Big Tech hiring policy land disproportionately on Indian households. When Google cuts its H-1B approvals by more than half, the statistical impact falls overwhelmingly on Indian professionals.

Nvidia is moving in the opposite direction, and its compensation packages explain why. Federal labour filings show base salaries for H-1B roles at Nvidia reaching up to ₹3.74 crore (roughly $450,000) for senior positions in software engineering, chip design, and AI research. These figures exclude stock awards, which at Nvidia's current valuation can dwarf base pay.

Jensen Huang, the company's Taiwanese-born chief executive, has been explicit about why. "Immigrants are crucial to the company's mission," he has said repeatedly, and last year he told employees that Nvidia would continue sponsoring H-1B applicants and cover all associated fees — including the $100,000 per-petition charge imposed by the Trump administration.

## Why Nvidia Can Afford to Be Generous

Nvidia's willingness to absorb $100,000 visa fees while Google and Amazon retrench is not philanthropy. It is supply-demand arithmetic. The company sits at the centre of the global AI infrastructure build-out, producing the GPUs that power everything from OpenAI's models to India's emerging sovereign AI ambitions. Its revenue has grown more than fivefold in two years. Its market capitalisation now exceeds $5 trillion.

That growth requires a specific kind of engineer — people who understand chip architecture, CUDA programming, AI model optimisation, and data centre networking at deep technical levels. India's engineering pipeline, particularly the IITs and NITs, produces exactly this talent. Companies that are still hiring aggressively need them. Companies that are cutting costs are giving them up.

The result is an unusual labour-market dynamic: Indian engineers laid off from Meta, Google, or Amazon now have a 60-day window to find a new sponsor or leave the country. Nvidia's hiring surge creates a landing zone that did not exist at this scale a year ago.

## The Salary Floor Is Moving

Beyond the headline numbers, Nvidia's H-1B filings reveal a compensation structure that is reshaping expectations across the industry. Mid-level software engineers are being certified at base salaries of $200,000 to $280,000. Senior research scientists command $300,000 or more before stock. AI infrastructure roles — the people who keep GPU clusters running at hyperscale — are pulling $250,000-plus.

For Indian professionals in the US, these figures establish a new floor for what top AI talent can demand. They also sharpen a dilemma that has defined diaspora life for decades: stay in the US where the pay is highest but the visa anxiety is real, or return to India where Nvidia, Google, Microsoft, and a wave of domestic startups are building AI research labs in Bengaluru and Hyderabad.

## What It Means for the Ecosystem

The divergence in H-1B hiring tracks a deeper structural shift. Companies whose revenue depends on AI are adding headcount. Companies that are deploying AI to reduce headcount are cutting. That is not a temporary mismatch — it is the new shape of the technology labour market.

For Indian engineers, the strategic calculation has changed. A decade ago, any FAANG offer was the golden ticket. Today, the question is whether your employer is selling AI or being disrupted by it. Nvidia, for now, is the clearest answer to that question — and it is hiring.

The 60-day clock keeps ticking. The question is whether enough doors stay open."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An AI Agent Now Writes 90% of Its Own Company's Code. Indian Engineers Should Read the Fine Print.",
        "subheadline": "Cognition just raised $1 billion at a $26 billion valuation for Devin, an autonomous coding agent with $492 million in annual revenue. Goldman Sachs and the US military are already customers. The Indian tech workforce, built on the promise that the world needs more software engineers, has reason to pay close attention.",
        "slug": make_slug("cognition-devin-ai-coding-agent-billion-indian-engineers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India supplies the world's largest cohort of software engineers, many working in the US on H-1B visas and hundreds of thousands employed by TCS, Infosys, and Wipro. If autonomous coding agents can handle enterprise development at Devin's scale, the economic foundation beneath Indian IT services and diaspora tech employment faces its most direct challenge yet.",
        "tags": ["cognition-ai", "devin", "ai-coding", "indian-it-services", "automation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/"},
            {"name": "TradingView", "url": "https://www.tradingview.com/news/te_news:466850:0-cognition-ai-secures-1-billion-at-26-billion-valuation/"},
            {"name": "Memeburn", "url": "https://memeburn.com/2026/06/cognition-ai-raises-1-billion-devin/"},
            {"name": "eWeek", "url": "https://www.eweek.com/news/cognition-ai-26b-valuation-1b-raise/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5483070/pexels-photo-5483070.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Cognition AI announced on May 27 that it had raised more than $1 billion in a Series D round at a $26 billion post-money valuation. Eight months earlier, the company was worth $10.2 billion. The pace of that ascent is unusual even by the standards of AI fundraising. What makes it unsettling for a large segment of the Indian technology workforce is what Cognition actually does.

The company makes Devin, an autonomous AI coding agent that handles software engineering tasks — writing, debugging, testing, deploying — with minimal human involvement. According to Cognition, more than 90 per cent of its own internal code is now written by Devin. That is not a marketing claim about potential. It is a reported operational fact.

## The Numbers Behind the Bet

The round was co-led by Lux Capital, General Catalyst, and 8VC, with participation from Founders Fund, Ribbit Capital, and Atreides. Cognition's annualised revenue run rate has climbed to $492 million, up from $37 million in May 2025 — a thirteen-fold increase in twelve months. Enterprise usage has grown more than 50 per cent month-over-month for six consecutive months.

The customer list explains the velocity. Goldman Sachs, Mercedes-Benz, Dell, Santander, the US Army, the US Navy, and NASA are all using Devin. These are not pilot programmes. At $492 million in run-rate revenue, Cognition is collecting real money from organisations that have concluded autonomous coding agents work well enough to deploy at scale.

CEO Scott Wu has said Cognition is targeting $1 billion in annualised revenue later this year. If it hits that mark, the company will have gone from launch to ten-figure revenue faster than Slack, Zoom, or most enterprise SaaS companies in history.

## What This Means for Indian IT

India's technology services industry — TCS, Infosys, Wipro, HCL Tech, Cognizant — employs roughly five million people, most of whom write, test, maintain, or manage software. The industry generated over $250 billion in export revenue in the last fiscal year. Its foundational promise is simple: Indian engineers are excellent, abundant, and cost-effective. Hire ten of them to do what five American engineers would cost.

Devin threatens that arithmetic directly. If an autonomous agent can handle routine software engineering — the bug fixes, feature implementations, test suite expansions, and migration tasks that constitute the bulk of IT services work — the cost advantage of offshore labour shrinks. Not because Indian engineers become worse, but because the baseline comparison is no longer an American engineer at $200,000 a year. It is an AI agent at a fraction of that.

The threat is not speculative. Cognition acquired the remaining assets of Windsurf last year, consolidating its position in AI coding. Anthropic's Claude Code, OpenAI's Codex, and Google's Jules are all competing in the same space. This is a category with multiple well-funded entrants, which means the technology will improve rapidly regardless of which company leads.

## The H-1B Dimension

For the roughly 300,000 Indian H-1B holders currently working in the US, the implications are more personal. Many hold positions as software engineers, systems architects, and full-stack developers — exactly the roles that autonomous coding agents are designed to absorb. If enterprise adoption of tools like Devin accelerates, the demand for mid-level coding talent may soften precisely when immigration policy makes job transitions harder.

The 60-day grace period after a layoff is already anxiety-inducing. Add the possibility that some employers may conclude they need fewer sponsored engineers and the calculus shifts further.

## The Counterargument

Not everyone in the industry sees doom. The optimistic read is that AI coding agents eliminate the tedious parts of software engineering while creating demand for engineers who can architect systems, define product requirements, review AI-generated code, and manage the agents themselves. In this framing, Indian engineers move up the value chain — from writing code to directing machines that write code.

There is historical precedent for this. The introduction of cloud computing was supposed to devastate Indian IT services, and instead created an entirely new category of migration and managed-services work. DevOps automation was going to eliminate operations teams, and instead spawned a new discipline.

But the speed of Devin's adoption — and the fact that it writes its own company's code — suggests this transition may be faster and more disruptive than previous ones. The question for Indian engineers is not whether AI coding agents will change their work. It is whether they can adapt before the change arrives.

For a workforce that built its global reputation on writing software, that question is existential."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chip Designers Are Finally Building for Themselves. Six Startups Have Reached Tape-Out.",
        "subheadline": "A new generation of Indian semiconductor startups founded by veterans of Intel, AMD, and Texas Instruments is crossing the industry's hardest milestone. At least two expect to ship production silicon before year-end.",
        "slug": make_slug("india-chip-design-startups-tapeout-mindgrove-agrani"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For decades, Indian engineers designed chips for Intel, Qualcomm, and AMD — in Bengaluru, but for American companies. Now the founders are coming home, backed by $100M+ in aggregate venture funding and India's semiconductor policy push. NRI engineers and investors watching the India fab story should know: design is where the real ecosystem begins.",
        "tags": ["india-semiconductors", "chip-design", "mindgrove", "agrani-labs", "make-in-india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-chip-designers-are-finally-building-for-themselves/"},
            {"name": "DIGITIMES Asia", "url": "https://www.digitimes.com/news/south-asia.html"},
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/mindgrove-pinetics-partnership-to-bring-india-designed-chip-into-smart-devices/article69522832.ece"},
            {"name": "YourStory", "url": "https://yourstory.com/2026/01/semiconductor-startup-agrani-labs-raises-8m-seed-funding"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For thirty years, Bengaluru was where American semiconductor companies sent their chip designs to be worked on. Indian engineers at Intel, AMD, Qualcomm, Texas Instruments, and Broadcom did the detailed RTL coding, verification, and physical design — then sent the files back to headquarters in Santa Clara or Austin for tape-out and production. The IP left India. The products carried American brands. The value accrued elsewhere.

That pattern is breaking. At least half a dozen Indian semiconductor startups have now reached tape-out — the moment a chip design is finalised and sent to a fabrication facility. In an industry where most startups never get past PowerPoint, reaching tape-out is the clearest signal that a company has crossed from concept to execution.

## Who Is Building What

The roster is specific and growing. C2i Semiconductors, founded by Texas Instruments veterans in Bengaluru, has taped out a smart power stage chip for AI data centres. Its platform claims over 96 per cent power conversion efficiency — meaningful in a world where data centre electricity bills are the binding constraint on AI growth. The company recently extended its Series A to $16.7 million, with Peak XV Partners and TDK Ventures backing the round.

Mindgrove Technologies, based at the IIT Madras Research Park, has taped out a Secure IoT system-on-chip at 28nm running at 700 MHz. In May, it signed a commercial partnership with Pune-based Pinetics to integrate the chip into biometric access control systems, smart locks, and camera applications — the first time an India-designed chip will ship in a finished commercial product. Its Vision SoC, supported by India's Design Linked Incentive scheme, targets dashcams, ADAS, and smart TVs.

Agrani Labs, founded by four people who held senior positions at Intel and AMD, is targeting AI inference chips — the accelerators that deploy trained models at the point of use. The company raised $8 million in seed funding led by Peak XV, with Vinod Dham — widely known as the Father of the Pentium — serving as founding adviser. VerveSemi and Calligo Technologies have both engaged foundries in Taiwan and South Korea. BigEndian Semiconductors raised $6 million after completing its own tape-out of a commercial chip.

Agnit Semiconductors and Mindgrove are both expected to cross into production before the end of 2026 — shipping finished silicon, not just design files.

## Why This Cohort Is Different

Previous waves of Indian semiconductor ambition foundered on the gap between design capability and commercial execution. India had the engineers but not the ecosystem — no foundries, limited packaging facilities, and venture capital that preferred software's faster returns.

Three things have changed. First, the founders. These are not first-time entrepreneurs trying to learn semiconductors. They are domain specialists with decades of experience inside global chip companies who have decided to build at home. When C2i's team left Texas Instruments, they brought deep knowledge of power delivery architectures. When Agrani's founders left Intel and AMD, they brought processor design expertise that does not exist in textbooks.

Second, the capital. Peak XV Partners (formerly Sequoia India) has backed multiple chip startups. TDK Ventures, Vertex Ventures, IvyCap, and Yali Deeptech are all active. The aggregate venture investment in Indian chip design startups now exceeds $100 million — small by global semiconductor standards, but unprecedented for India.

Third, the policy. The India Semiconductor Mission, the Design Linked Incentive scheme, and the production-linked incentives for electronics manufacturing have created a framework that did not exist five years ago. The government's commitment is real enough that Intel signed an MoU last week to build an advanced glass substrate facility in Odisha, and Micron's Gujarat fab is under construction.

## The NRI Angle

For Indian-origin engineers still at Intel, Qualcomm, or Broadcom in the United States, the shift creates a genuine career question. The founders of these startups were their colleagues. The problems being solved — AI inference, power management, IoT security — are problems they know intimately. The difference is that these chips will carry Indian brands, generate Indian IP, and build Indian wealth.

For NRI investors, the signal is equally clear. India's semiconductor story is no longer just about Tata Electronics and Micron building fabs. It is about a design ecosystem that can generate the intellectual property those fabs will eventually manufacture. Design is where margins live in semiconductors. Intel's margins come from designing x86 processors, not from operating foundries. TSMC is the exception that proves the rule.

The question is whether India's chip design startups can survive the valley of death between tape-out and volume production. Manufacturing a chip is expensive. Qualifying it with customers takes months. Scaling production requires relationships with foundries that prioritise large-volume customers.

But for the first time, the problem is execution, not ambition. India has semiconductor startups that have designed real chips, taped them out at real foundries, and signed real customers. That is new. And it matters."""
    }
]

for art in articles:
    img = art.get("image_url", "")
    if img:
        ok = verify_image(img)
        print(f"🖼️ Image for '{art['headline'][:50]}...': {'✅ OK' if ok else '❌ FAILED'}")
        if not ok:
            art["image_url"] = ""
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
