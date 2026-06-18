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

EBAY_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/EBay_headquarters_2018.jpg/1280px-EBay_headquarters_2018.jpg"
NADELLA_IMG = "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg"
ACCENTURE_IMG = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg/1280px-Accenture_office_building_in_Gachibowli_%28August_2019%29.jpg"

ebay_body = """eBay wants to lay off 639 American workers this year. It also wants to hire 429 people on H-1B visas. Those two numbers, sitting side by side in public filings, are the cleanest illustration yet of a pattern the entire technology industry would rather not explain out loud.

The figures come from workforce-tracking platform Cutoffs.io and were surfaced this week by The American Bazaar. eBay filed 360 H-1B labor condition applications in the second quarter of its fiscal year and 69 in the first, totalling 429. Meanwhile, Worker Adjustment and Retraining Notification filings — the legally mandated warnings companies must give before mass layoffs — point to hundreds of US roles disappearing in 2026. eBay cut roughly 800 jobs earlier this year, about 6% of its workforce, after acquiring the fashion-resale site Depop.

## The overlap nobody will connect

There is, to be precise, no record linking the laid-off employees to the visa applications. The affected workers and the incoming H-1B hires need not sit on the same teams, in the same offices, or do the same jobs. eBay says it continues to hire in "high-priority areas," shorthand for the AI, machine-learning and data-science roles every technology company is now scrambling to fill while trimming elsewhere.

But the optics are radioactive, and Washington has noticed. Last September, Senators Dick Durbin and Chuck Grassley — a Democrat and a Republican, rarely aligned on anything — wrote to ten of the largest H-1B users demanding data on exactly this question: why file thousands of visa petitions while ordering mass layoffs of American staff? eBay was not on that original list, but the eBay numbers are precisely the kind of evidence that keeps the letter relevant.

## Why an NRI engineer should read the fine print

For the Indian professional, this is not an abstract policy debate. Indians receive roughly 70% of all H-1B visas issued each year, which means "the company is hiring H-1B workers" almost always means "the company is hiring Indians." When a firm simultaneously lays off domestic staff and files for foreign-worker visas, the visa holder becomes the lightning rod in a fight that is really about corporate cost structure and AI automation.

That has two consequences worth internalising. First, political risk now attaches to the visa itself, not just to your employer's business performance. A Texas congressman has already introduced a bill — the American White-Collar Worker Jobs Act of 2026 — to replace the H-1B lottery with a wage-based system, bar companies that have recently conducted layoffs from sponsoring H-1B workers, and scrap the Optional Practical Training programme that lets graduates work after university. If a version of that "no layoffs, then no sponsorship" rule becomes law, an engineer's ability to stay in the country could hinge on their employer's headcount decisions, over which they have zero control.

Second, the 60-day grace period remains the single most important number in an H-1B holder's life, and the eBay story is a reminder of how fast it can start ticking. The clock begins on your last actual day of employment — not when severance ends, not when COBRA lapses, not when HR finishes offboarding. Workers who misread that distinction risk accruing unlawful presence, which can trigger a three- or ten-year bar from re-entering the United States.

## The structural read

eBay is not unusual; it is representative. Across the sector, companies are flattening management layers, automating routine engineering and support work, and concentrating new hiring in a narrow band of AI specialists. The H-1B pipeline keeps flowing because the specific skills firms want are genuinely scarce — but it flows into the same companies that are shrinking overall.

For the Indian diaspora, the lesson is to treat visa status as a portfolio risk to be actively managed rather than a settled fact. That means knowing your priority date, understanding H-1B portability, keeping an EB-5 or green-card pathway in view, and not assuming that a company hiring people who look like you is a company that will protect you. The numbers in eBay's filings suggest those can be two very different things."""

nadella_body = """Microsoft has made Copilot Cowork — its most ambitious attempt yet to turn its AI assistant from a suggestion engine into an actual co-worker — generally available to Microsoft 365 customers worldwide. The product can take a multi-step task, go away, and come back with finished work rather than a draft. For the millions of Indians who keep the world's enterprise software running, it is both the tool they will be asked to deploy and the tool that is quietly redrawing their job descriptions.

The timing is pointed. Just days before the rollout, CEO Satya Nadella published a long warning on X about the very future his company is building. A handful of dominant AI models, he cautioned, could end up "eating everything they see" — absorbing the proprietary knowledge of entire industries and leaving the firms that supplied that data as little more than feeders to someone else's system. "There is no societal permission for an AI future that hollows out entire industries," he wrote, drawing a deliberate parallel to the way early globalisation gutted industrial economies while the GDP figures still looked healthy.


## What Cowork actually does

Cowork runs in the cloud, draws on a company's Microsoft 365 data, and executes extended workflows autonomously. The general-availability release widens the menu of underlying models — Anthropic's Opus 4.8 and Sonnet 4.6 are supported, with GPT 5.5 available through Microsoft's Frontier programme — and adds a new in-house model, Cowork 1, built to run enterprise workloads at lower cost. Microsoft has also wired in the enterprise-governance machinery that large customers demand: audit logs, eDiscovery, insider-risk management and data-lifecycle controls, with browser-based actions available through Edge.

The governance layer matters because of a number buried in a shareholder lawsuit filed against Microsoft this month: the company has sold only around 15 million paid Microsoft 365 Copilot seats. Investors point to that as evidence of slower-than-expected enterprise uptake. Cowork is, in part, Microsoft's answer — a bet that businesses will pay for AI that completes work, not AI that merely assists with it.

## The diaspora angle: two futures at once

For the Indian technology workforce, Cowork represents a fork in the road, and Nadella's warning is the signpost. The optimistic reading is the one he offered alongside his caution: "human capital does not become less valuable as token capital grows. It only becomes more valuable." In this telling, the Indian engineer who learns to design, govern and supervise agentic systems becomes more indispensable, not less — the person who sets the goals the machines pursue and catches the mistakes they make.

The pessimistic reading is structural and is already visible in India's own IT sector. The work Cowork automates — extended, multi-step office workflows — is precisely the kind of repeatable process work that has employed hundreds of thousands of Indians at the Cognizants, Infosyses and TCSes of the world, and tens of thousands more in back-office and support functions at US firms. When a tool returns finished output instead of a draft, the layer of people who used to produce that draft is the layer most exposed.

## Read it as a manual, not a memo

Nadella's post doubles as a checklist for any professional trying to stay on the right side of this shift. Can you export the operational knowledge your AI systems accumulate, or does it live at an address you do not control? Can a human on your team read why the system made a given decision? Do your costs fall as you use the tool more, or do your switching costs rise? Those questions, aimed at enterprises, apply just as sharply to a career.

For an Indian engineer in Bengaluru, Hyderabad or New Jersey, the practical move is to migrate up the stack — toward the design, oversight and judgment roles that Cowork cannot fill — before the migration is forced. Microsoft has just shipped the clearest signal yet of where the floor is rising. The people who read it as instruction rather than threat are the ones who will still be standing on it."""

accenture_body = """Accenture reports earnings this week, and the consulting giant that employs more Indians than almost any company on earth is walking into the results under a cloud it cannot quite dispel: the fear that artificial intelligence will automate away the very work it sells.

For the fiscal third quarter, analysts polled by FactSet expect adjusted earnings of $3.71 a share on revenue of $18.8 billion — roughly 6% growth from a year earlier. Respectable numbers. But the stock has spent 2026 fighting a narrative rather than a balance sheet. When the AI-disruption panic swept consulting and IT-services shares at the start of the year, Accenture was caught in the downdraft, on the theory that tools from OpenAI and Anthropic could do the analysis and implementation work that has long justified consulting day rates.

## Doubling down, not backing away

Accenture's response has been to run toward the fire. On Wednesday, a day before its earnings report, it announced the acquisitions of Alfahealth and the Industries eXcellence Group — moves that sent shares lower, investors apparently unconvinced that more dealmaking is the answer. The deeper strategy is partnership: rather than trying to out-build OpenAI and Anthropic, Accenture has joined them, striking alliances to deploy agents that automate customer support, advertising and other functions, while developing its own tools to license directly to clients. CEO Julie Sweet has pointed repeatedly to "AI-driven growth" as the engine of the firm's next phase.

Analysts are split on whether it will work. Morgan Stanley calls Accenture "well positioned for an eventual recovery, given its scale, enterprise relationships, and exposure to large transformational programs," while warning that "the timing of any reacceleration remains increasingly uncertain." TD Cowen argues the firm is turning AI from a threat into a product line.

## Why this lands harder in the diaspora

Accenture's fate is not a distant Wall Street story for Indian families — it is a household one. The firm's single largest concentration of employees is in India, and its US operations are staffed heavily by Indian professionals on H-1B and L-1 visas. When Accenture sneezes, lakhs of Indian careers catch cold, on both sides of the Pacific.

And the structural shift the firm is navigating is the same one tearing through India's home-grown IT champions. TCS retrenched roughly 12,000 employees in FY26, primarily in middle and senior grades; chairman N. Chandrasekaran told shareholders bluntly that AI will "absolutely" reduce hiring and that the company expects to run as many AI agents as human staff. Cognizant is cutting about 4,000 jobs under a restructuring it calls Project Leap while still hiring 20,000 freshers — a reshaping that hollows out the middle, not the bottom.

That middle layer is the heart of the matter. As HFS Research's Phil Fersht puts it, IT services "built its entire economic model on the middle layer" — the delivery managers, project leads and specialists who coordinated armies of junior coders. AI now does much of what the juniors did, which means firms need fewer juniors, which means they need far fewer of the middle managers who existed to coordinate them. For the mid-career Indian professional who climbed that exact ladder, Accenture's earnings call is effectively a referendum on whether the ladder still exists.

## What to listen for

The headline numbers will matter less than the commentary. Watch for what Sweet says about "bookings" — the pipeline of signed future work — because a slowdown there is the leading indicator of trouble that revenue lags by quarters. Watch the split between "GenAI bookings" and traditional services: if the new business is all AI-deflationary work that does the same job with fewer people, growth in dollars can mask shrinkage in headcount. And watch the tone on hiring, particularly entry-level hiring, which is the canary for the broader services labour market.

For the Indian diaspora, the read-through extends well beyond one company. Accenture, TCS, Infosys, Cognizant and their peers collectively employ the single largest concentration of Indian technology talent on the planet. They are all running the same experiment at once: can a business built on selling human hours survive in a world where the hours are increasingly machine-supplied? This week's earnings are one of the first real data points on the answer."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "eBay Is Cutting 639 American Jobs While Filing for 429 H-1B Workers. Indians Will Wear the Backlash.",
        "subheadline": "The e-commerce firm's own filings put layoffs and visa applications side by side — handing Washington exactly the ammunition it has been hunting for.",
        "slug": make_slug("ebay-layoffs-h1b-filings-indian-tech-workers-visa-backlash"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indians get ~70% of H-1B visas, so when a company lays off Americans while filing for foreign workers, Indian professionals become the lightning rod in a political fight over corporate cost-cutting and AI automation.",
        "tags": ["h1b", "ebay", "tech-layoffs", "indian-tech", "immigration", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "HRKatha", "url": "https://www.hrkatha.com/news/ebay-faces-scrutiny-over-h-1b-hiring-amid-fresh-layoffs/"},
            {"name": "Reuters (eBay layoffs)", "url": "https://www.reuters.com/business/retail-consumer/ebay-slashes-6-workforce-e-commerce-firm-realigns-operations/"},
            {"name": "Senator Dick Durbin (H-1B scrutiny letters)", "url": "https://www.durbin.senate.gov/newsroom/press-releases/durbin-grassley-take-aim-at-labor-exploitation-in-tech-finance-retail-sectors"},
            {"name": "Sambad English (Chip Roy H-1B bill)", "url": "https://sambadenglish.com/us-congressman-proposes-major-h-1b-visa-overhaul-seeks-end-to-lottery-system-and-opt-programme/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": EBAY_IMG,
        "image_caption": "eBay's Silicon Valley headquarters in San Jose, California",
        "image_attribution": "Wikimedia Commons",
        "body": ebay_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Microsoft Just Shipped an AI That Finishes Your Work, Not Drafts It. Satya Nadella Warns It Could Hollow Out Industries.",
        "subheadline": "Copilot Cowork goes global the same week its own CEO cautions that a few AI models could 'eat everything they see' — and Indian tech workers sit on both sides of that bet.",
        "slug": make_slug("microsoft-copilot-cowork-global-nadella-ai-warning-indian-tech"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Cowork automates the multi-step office workflows that employ hundreds of thousands of Indians at firms like TCS and Cognizant, making Nadella's 'move up the stack' warning a direct career instruction for the diaspora.",
        "tags": ["microsoft", "satya-nadella", "ai-agents", "copilot", "indian-tech", "enterprise-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Gadgets360 (Copilot Cowork GA)", "url": "https://www.gadgets360.com/ai/news/microsoft-copilot-cowork-feature-global-rollout-microsoft-365"},
            {"name": "The Hindu BusinessLine (Nadella token capital)", "url": "https://www.thehindubusinessline.com/info-tech/microsoft-ceo-calls-for-frontier-ai-ecosystem-to-ensure-broad-value-creation/article.ece"},
            {"name": "WebProNews (Nadella warning)", "url": "https://www.webpronews.com/satya-nadella-warns-ai-winners-risk-hollowing-out-industries/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": NADELLA_IMG,
        "image_caption": "Microsoft CEO Satya Nadella",
        "image_attribution": "Wikimedia Commons",
        "body": nadella_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Accenture Reports Earnings Under an AI Cloud. The Company That Employs the Most Indians Is a Referendum on the Whole Sector.",
        "subheadline": "Wall Street wants to know whether a business built on selling human hours can survive when the hours go machine-supplied — and lakhs of Indian careers ride on the answer.",
        "slug": make_slug("accenture-earnings-ai-disruption-indian-it-jobs-tcs-cognizant"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Accenture's largest employee base is in India and its US ops run heavily on Indian H-1B/L-1 talent, so its earnings double as a verdict on whether AI is hollowing out the mid-career IT jobs the diaspora climbed toward.",
        "tags": ["accenture", "indian-it", "ai-disruption", "tcs", "cognizant", "tech-jobs"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Barron's (Accenture earnings preview)", "url": "https://www.barrons.com/articles/accenture-stock-earnings-ai"},
            {"name": "Mint (India's middle managers obsolete)", "url": "https://www.livemint.com/companies/news/natural-intelligence-on-the-ropes-why-indias-middle-managers-are-becoming-obsolete.html"},
            {"name": "Mint (Cognizant 4,000 job cuts)", "url": "https://www.livemint.com/companies/news/cognizant-to-cut-4000-jobs-as-ai-push-weak-demand-weigh-on-outlook.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": ACCENTURE_IMG,
        "image_caption": "Accenture's office building in Gachibowli, Hyderabad",
        "image_attribution": "Wikimedia Commons",
        "body": accenture_body
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        wc = len(art["body"].split())
        print(f"OK  {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
