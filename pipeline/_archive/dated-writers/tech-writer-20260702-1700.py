#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 17:00 PT run.
Inserts 2 technology articles into Supabase p2_articles.
"""
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
    # ── Article 1: Oracle 21K layoffs, half in India ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Oracle Cut 21,000 Jobs Last Year. Nearly Half Were in India.",
        "subheadline": "The database giant spent $1.84 billion on severance while tripling its capital spending on AI infrastructure. Its latest annual filing says the hardest part hasn't started.",
        "slug": make_slug("oracle-21000-jobs-cut-india-ai-infrastructure"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Oracle employs tens of thousands of Indian engineers in Bengaluru, Hyderabad, and on H-1B visas in the US. With 10,000 of its 21,000 cuts falling on India, the restructuring directly reshaped the Indian tech job market.",
        "tags": ["oracle", "layoffs", "ai-infrastructure", "india-tech", "h-1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "People Matters", "url": "https://www.peoplematters.in/news/ai-and-emerging-tech/after-cutting-21000-jobs-oracle-says-ais-biggest-challenge-isnt-people-anymore-50633"},
            {"name": "The Register", "url": "https://www.theregister.com/"},
            {"name": "Oracle FY2026 Annual Report (via Gizmodo)", "url": "https://gizmodo.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Oracle-October2011.JPG/1280px-Oracle-October2011.JPG",
        "image_caption": "Oracle Corporation headquarters in Redwood City, California",
        "image_attribution": "Wikimedia Commons",
        "body": """Oracle's fiscal 2026 annual report, filed this week, is a document of contradictions. The company spent $1.84 billion on severance and restructuring — nearly five times the $374 million it spent the year before — while simultaneously tripling its capital expenditure to $55.7 billion. It eliminated roughly 21,000 positions, or 13% of its global workforce, shrinking headcount from 162,000 to 141,000. And then it warned investors that cutting people was the easy part.

Nearly half of those job losses fell on India. According to reports by The Economic Times and LiveMint, Oracle cut approximately 10,000 roles across its Indian operations, including about 1,000 positions at Oracle Financial Software Services. For a company that has long relied on India as a centre for engineering, support, and back-office operations, the scale of the reduction was striking.

## The infrastructure wall

What makes Oracle's filing unusual is not the layoffs — those have become a quarterly ritual across the industry — but the shift in what the company now considers its primary risk. The annual report identifies a list of constraints that reads less like a tech company's worries and more like a power utility's: electricity shortages, GPU scarcity, construction delays, permitting bottlenecks, grid capacity limits, and rising energy costs.

Oracle stated bluntly that expanding Oracle Cloud Infrastructure "requires increased computing capacity" and that the company "must incur significant capital and operating expenditures" to keep pace with demand. It flagged supply chain disruptions, cybersecurity threats, export controls, and even the possibility that some AI customers — many of them unprofitable startups burning through venture capital — might not be able to pay their bills.

The spending numbers back up the anxiety. Oracle's capital expenditure hit $55.7 billion in fiscal 2026, up from $21.2 billion the previous year. It expects to spend between $90 billion and $95 billion in fiscal 2027. Much of that money is flowing into AI-ready data centres built to serve customers like OpenAI and Meta, both of which have signed major cloud agreements with Oracle.

## Stargate and the scale problem

Oracle is also a partner in Stargate, the massive AI infrastructure initiative it announced alongside OpenAI, SoftBank, and the US government. The project has outlined plans to invest up to $500 billion in AI infrastructure over the coming years, an ambition that makes Oracle's current spending look like a down payment.

Delivering projects at that scale depends on securing land, power, chips, and regulatory approvals across multiple jurisdictions — precisely the constraints Oracle is now flagging as risks. The company warned of "excess capacity" if demand doesn't materialise, "fixed-price contracts" that could squeeze margins, and "hardware obsolescence" as AI architectures evolve faster than data centres can be built.

## What it means for Indian tech workers

The India-specific impact is hard to overstate. Oracle has been one of the largest enterprise technology employers in Bengaluru and Hyderabad for two decades. Losing 10,000 roles in a single fiscal year doesn't just affect the individuals who lost their jobs — it reshapes salary benchmarks, hiring timelines, and negotiating power across the Indian IT services market.

For Indian professionals working at Oracle in the United States on H-1B visas, the restructuring carried an additional burden. Under USCIS rules, H-1B holders who lose their positions have a 60-day grace period to find a new sponsoring employer or leave the country. The compressed timeline turns a corporate restructuring into a personal immigration crisis.

Oracle's pivot also sends a signal to the broader Indian IT workforce. The company didn't just cut headcount — it identified AI deployment as one of the reasons. The jobs that disappeared were not temporary roles awaiting backfill. They were positions Oracle concluded it no longer needed because AI and automation had compressed the work.

Indian IT services firms like TCS, Infosys, and Wipro face a version of the same pressure. JP Morgan analysts warned earlier this week that AI is structurally deflating parts of the Indian IT sector, as clients need fewer engineers to accomplish the same tasks. Oracle's annual report, with its blunt language about AI-driven workforce reductions, is the enterprise equivalent of the same message.

The question for Indian tech professionals — whether in Hyderabad, Bengaluru, or the Bay Area — is not whether their employers will restructure around AI. It is whether they will be on the right side of the restructuring when it happens."""
    },

    # ── Article 2: Zuckerberg admits AI agents not delivering ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Zuckerberg Just Admitted Meta's AI Bets 'Haven't Come to Fruition.' The Stock Fell 5%.",
        "subheadline": "At an internal town hall on Thursday, the Meta CEO said AI agent development has been slower than expected and that the restructuring which cost thousands of jobs was not as clean as it should have been.",
        "slug": make_slug("zuckerberg-meta-ai-agents-slower-town-hall"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Meta employs thousands of Indian engineers on H-1B visas and runs major AI research operations in India. Zuckerberg's admission that the AI agent thesis hasn't materialised raises questions about whether the layoffs and team reshuffles that displaced Indian workers were premature.",
        "tags": ["meta", "mark-zuckerberg", "ai-agents", "layoffs", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/zuckerberg-says-ai-agent-development-going-slower-than-expected-2026-07-02/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/"},
            {"name": "Fox Business", "url": "https://www.foxbusiness.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
        "image_caption": "Meta CEO Mark Zuckerberg at the White House in September 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Mark Zuckerberg told Meta employees on Thursday what the stock market had been saying for weeks: the AI-driven restructuring that reshaped the company this year hasn't produced the results he expected.

At an internal town hall, a recording of which was heard by Reuters, Zuckerberg said the "trajectory of agentic development over at least the last four months hasn't really accelerated in the way that we expected." The company's bets on AI agents — automated systems designed to execute tasks on behalf of users — "haven't come to fruition yet," he added.

Meta shares fell nearly 5% on Thursday, closing at $582.90. The stock is down roughly 27% from its 52-week high.

## The restructuring that wasn't clean

The admission carries weight because of what Meta did to position itself for the AI agent future. In May, the company laid off approximately 10% of its global workforce and reassigned roughly 7,000 employees to AI-focused teams. The moves prompted widespread employee pushback and raised concerns about morale, retention, and whether the company was cutting too fast.

Zuckerberg acknowledged the execution was flawed. The reorganisation, he said, was not as "clean" as it could have been, and executives had "miscalculated on the timing of the changes."

When the restructuring was being planned in January and February, Zuckerberg said he and his leadership team were "super optimistic" about tools like Claude Code from Anthropic. Conversations with "our top people" at the time suggested the company wasn't moving fast enough to adapt to the AI shift.

Four months later, the optimism has faded. The AI agent technology that was supposed to justify the restructuring has not advanced on schedule.

## Selling what you can't use

The mismatch between Meta's infrastructure spending and its AI output is already visible in the company's finances. Meta has been pouring billions into AI compute capacity — its capital expenditure is projected to push free cash flow negative in the second quarter of 2026.

But the company's internal utilisation rate for that infrastructure sits at around 65%, according to Jefferies. The remaining 35% is idle capacity that Meta is now looking to monetise by selling cloud computing access to third parties — a business it has never operated before.

Some analysts see the cloud pivot as a sign that Meta's internal AI products aren't scaling fast enough to justify the build-out. If Meta's own AI agents were consuming the capacity, there would be no surplus to sell. The fact that surplus exists suggests the demand forecasts that drove the spending were too aggressive.

Jefferies analyst Brent Thill pushed back on that reading, calling overbuilding concerns "backward" and arguing that demand for computing power continues to outstrip supply across the industry. But the timing of the cloud announcement, coming alongside Zuckerberg's admission that AI agents are lagging, makes the optimistic interpretation harder to sustain.

## What it means for Indian engineers

Meta employs a large concentration of Indian engineers, both at its headquarters in Menlo Park and across its global operations. Many of them hold H-1B visas and were directly affected by the May restructuring — either through layoffs or mandatory reassignment to AI-focused teams.

For those who were reassigned, Zuckerberg's admission raises an uncomfortable question: if the AI agent technology that justified their new roles hasn't advanced as planned, what happens to those roles when the next performance review cycle arrives?

Meta's chief people officer, Janelle Gale, addressed the anxiety indirectly in a previous employee meeting. "Will there be more layoffs? The question always comes up," she said. "I'd love to say that there are no more layoffs, but I can't say something we can't deliver."

The company is also planning further layoffs in the second half of the year, Reuters has reported, citing unnamed sources. Meta could cut nearly 20% of its total workforce by the end of 2026.

## A broader reckoning

Zuckerberg's town hall comments matter beyond Meta. Every major technology company — Google, Microsoft, Amazon, Apple — has restructured around the assumption that AI will compress the amount of human labour needed to build and maintain software products. Headcount reductions across the industry have been explicitly tied to AI-driven productivity gains.

If those gains are materialising more slowly than expected, the restructuring rationale weakens. Companies that cut too aggressively may find themselves short-staffed for the work AI can't yet do, while paying the morale and institutional knowledge costs of the layoffs they already made.

For Indian tech professionals in Silicon Valley, the calculus is stark. The industry that brought them to America on the promise of stable, high-skilled employment is now restructuring around a technology whose trajectory even its biggest champion admits he misjudged. The 60-day clock that starts when an H-1B holder loses a job doesn't pause for a CEO's mea culpa."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
