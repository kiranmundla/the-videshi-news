#!/usr/bin/env python3
"""Tech writer batch — 2026-07-02 07:00 UTC"""
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
    return slug[:70].rstrip('-') + "-20260702"

articles = [
    # ---- ARTICLE 1: JP Morgan / Indian IT Deflation ----
    {
        "id": str(uuid.uuid4()),
        "headline": "JP Morgan Says AI Is Deflating India's IT Giants. It Picked Two Winners.",
        "subheadline": "The brokerage expects only 3-4% growth for Indian IT services as AI compresses delivery timelines. TCS and Infosys are favoured; HCLTech and Wipro are not.",
        "slug": make_slug("jp-morgan-ai-deflation-indian-it-tcs-infosys-wipro"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Hundreds of thousands of NRIs work at Indian IT firms or hold their stocks — this downgrade signals structural change in the industry that built the diaspora's professional class.",
        "tags": ["indian-it", "tcs", "infosys", "wipro", "hcltech", "ai-disruption", "jp-morgan"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/technology/as-ai-slows-it-growth-jp-morgan-expects-tcs-and-infosys-to-outperform-wipro-hcl-tech"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indian-it-firms-near-term-outlook-muted-clients-cut-spending-ai-risks-mount-2026-04-14/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/market/stock-market-news/nifty-it-plunges-over-2-infosys-ltimindtree-tcs-among-top-laggards"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg",
        "image_caption": "Aerial view of the glass pyramid at the Infosys campus in Mysore, India",
        "image_attribution": "Wikimedia Commons",
        "body": """For the better part of three decades, India's IT services industry has been the conveyor belt that delivered a generation of Indian engineers to the American middle class. TCS, Infosys, Wipro, HCLTech — these were not just employers. They were immigration sponsors, career launchpads, and, for millions of NRI families, the reason the move to New Jersey or the Bay Area happened at all.

Now JP Morgan is telling investors that the conveyor belt is slowing down.

In a report published this week, the brokerage projected that large Indian IT services firms will deliver only 3-4% medium-term revenue growth — well below the mid-single-digit rates the industry has historically targeted and a far cry from the double-digit expansions that defined its golden years. The culprit, predictably, is artificial intelligence.

## The deflation phase

JP Morgan describes the current moment as the "deflation phase" of AI adoption in the enterprise. Clients are discovering that AI-driven productivity gains — automated testing, AI-assisted code generation, faster delivery cycles — are shrinking demand for traditional IT services faster than new AI-related spending is materialising.

The arithmetic is straightforward. When a generative AI tool can compress a 200-person testing engagement into a 50-person one, the services company does not bill for the other 150. ICICI Direct estimates that AI could cause 2-3% annual revenue deflation in traditional IT services over the next couple of years, though it also projects an incremental AI-led addressable market of $300-400 billion by 2030. The gap between those two timelines is where the pain lives.

The first-half recovery that Indian IT companies typically enjoy each fiscal year is unlikely this time, JP Morgan warned, citing delayed deal closures, slower project ramp-ups, cautious enterprise spending, geopolitical uncertainty, and — most pointedly — rapid AI-driven changes in client priorities.

## Two winners, two laggards

JP Morgan is not bearish on everyone equally. It favours **Infosys** and **TCS** over **HCLTech** and **Wipro**, a hierarchy that reflects each company's positioning in the AI transition.

TCS, India's largest IT exporter, posted annualised AI services revenue of $2.3 billion in its most recent fiscal year — more than 6% of overall revenue. The company has signalled that the worst macro headwinds are behind it. Infosys, under CEO Salil Parekh, has been aggressive about embedding AI into client delivery and counts several large AI transformation deals in its pipeline.

HCLTech and Wipro, by contrast, have flagged continued volatility and soft discretionary spending. Following weaker guidance from Accenture — often a bellwether for the sector — JP Morgan expects Infosys, HCLTech, and Wipro to either lower or soften their FY27 revenue guidance.

The Nifty IT index fell more than 2% on June 30, with LTIMindtree, Infosys, and TCS among the sharpest decliners. Year to date, the IT index has been the worst-performing sector on India's benchmark exchange.

## What this means for the diaspora

The implications ripple outward from Dalal Street. Indian IT services employ roughly 5.9 million people and generate $283 billion in annual revenue. The sector is the single largest employer of H-1B visa holders in the United States. Every earnings miss, every guidance cut, every hiring freeze at these firms affects immigration pipelines, campus placement seasons in India, and household wealth across the Indian American community.

For NRI investors with exposure to Indian IT stocks — and the Nifty IT index has shed roughly $26 billion in market value this year — the signal is clear: the industry that built India's global technology brand is being repriced. Not destroyed, but repriced.

The companies that survive the deflation will be the ones that sell AI, not the ones that sell the bodies AI replaces. TCS and Infosys appear to be further along that curve. Whether the others follow quickly enough is the $283 billion question."""
    },

    # ---- ARTICLE 2: OpenAI Codex Macro Pad ----
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI's First Hardware Is a Macro Pad for Coders. It Launches July 15.",
        "subheadline": "The Codex Micro, built with keyboard maker Work Louder, gives developers physical buttons for AI-assisted coding shortcuts. It is not the Jony Ive device.",
        "slug": make_slug("openai-codex-micro-hardware-macro-pad-work-louder"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India has the world's second-largest developer community and OpenAI just hired ex-Uber India chief Prabhjeet Singh as its India MD — this hardware play signals growing investment in the developer ecosystem Indian engineers dominate.",
        "tags": ["openai", "codex", "developer-tools", "hardware", "ai-coding", "indian-developers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/digital/openais-first-hardware-isnt-a-phone-its-designed-for-codex"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/simon-says-buy-this-openai-mechanical-keyboard-thingy"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/06/29/openai-teases-codex-branded-hardware-collaboration-coming/"},
            {"name": "The Verge (via Storyboard18)", "url": "https://www.storyboard18.com/digital/openais-first-hardware-isnt-a-phone-its-designed-for-codex"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36363144/pexels-photo-36363144.jpeg",
        "image_caption": "A mechanical keyboard and macro pad with LED lighting on an ergonomic desk setup",
        "image_attribution": "Pexels",
        "body": """OpenAI's long-rumoured collaboration with Jony Ive — the former Apple design chief working on a mysterious AI companion device — has sucked up most of the oxygen around the company's hardware ambitions. So it came as a mild surprise when OpenAI's first actual hardware product turned out to be something considerably more modest: a macro pad for programmers.

On June 29, the @OpenAIDevs account on X posted a teaser video showing a compact, square-shaped device studded with illuminated buttons, captioned: "Your favourite Codex shortcuts are getting an upgrade. July 15th."

The device is the Codex Micro, a collaboration between OpenAI and Work Louder, a boutique keyboard maker that specialises in programmable mechanical macro pads for developers and creative professionals. Work Louder previously partnered with Figma on a similar custom device in 2023.

## What it does

A macro pad is a small auxiliary keypad that sits beside your main keyboard. Each key can be programmed to fire a specific shortcut, macro, or command with a single press — replacing the muscle memory required to remember multi-key combinations.

The Codex Micro appears to be modelled on Work Louder's existing Creator Micro 2, which features 13 mechanical switches, a joystick, and a touch-sensitive control surface. The OpenAI version will likely ship with programmable controls preconfigured for common Codex actions: running a command, accepting a suggestion, switching between coding sessions, or triggering code review.

OpenAI spokesperson Dominik Kundel described the device at the AI Engineer World's Fair in San Francisco as a keyboard "designed to supercharge people's Codex usage." Pricing, supported platforms, and market availability have not been announced.

## A developer-first strategy

The macro pad is a niche product by any measure. But it signals something broader about OpenAI's strategic direction: the company is investing seriously in developer tooling, not just model capabilities.

Codex — OpenAI's AI coding assistant — has become one of the company's fastest-growing enterprise products. It powers GitHub Copilot's backend, drives millions of lines of AI-assisted code daily, and has become the default tool for a generation of developers who write prompts instead of functions. The practice has acquired its own label: "vibe coding."

A dedicated hardware accessory for Codex users is, at one level, a marketing device. But it also reflects a genuine workflow insight: developers who spend hours inside AI coding tools benefit from tactile feedback and dedicated controls that reduce context-switching. Click a button, accept a suggestion. Click another, roll it back. The friction savings are small per action but compound over a full coding session.

## Why Indian developers should care

India is GitHub's second-largest contributor community, and Indian engineers are among the world's heaviest users of AI coding tools. OpenAI's decision to hire Prabhjeet Singh — the former president of Uber India and South Asia — as its India managing director, effective September, underscores how seriously the company views India as a growth market.

Singh's mandate includes consumer growth, enterprise adoption, and partnerships in India. A Codex hardware ecosystem would fit neatly into that strategy, particularly as India's IT services firms — TCS, Infosys, Wipro — are training hundreds of thousands of developers on AI-assisted coding workflows through NVIDIA partnerships.

The Codex Micro is not the device that will define OpenAI's hardware ambitions. The Jony Ive collaboration, expected in late 2026 or 2027, will carry that weight. But for the Indian engineers and developers who have made Codex part of their daily toolkit, July 15 offers a small, tangible preview of what an AI-native developer workflow might feel like — one button at a time.

The Ive device can wait. The vibe coders cannot."""
    },

    # ---- ARTICLE 3: EB-1A surge among Indian tech workers ----
    {
        "id": str(uuid.uuid4()),
        "headline": "Indian Tech Workers Are Self-Sponsoring Their Green Cards. EB-1A Filings Have Jumped 50%.",
        "subheadline": "With H-1B costs soaring and layoffs triggering 60-day exit clocks, senior Indian engineers are bypassing employer-sponsored immigration entirely. The EB-1A 'extraordinary ability' visa is their escape hatch.",
        "slug": make_slug("eb1a-green-card-indian-tech-workers-h1b-self-sponsor"),
        "category": "technology",
        "vertical": "immigration",
        "diaspora_angle": "EB-1A self-petitions directly affect tens of thousands of Indian H-1B professionals in the US — this is the immigration strategy shift of a generation for the tech diaspora.",
        "tags": ["eb-1a", "h-1b", "immigration", "green-card", "indian-tech-workers", "silicon-valley", "self-petition"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/the-ai-restructuring-shock-why-elite-tech-talents-are-decoupling-their-immigration-status-through-eb1a-experts-from-big-tech"},
            {"name": "CXOToday", "url": "https://www.cxotoday.com/news-analysis/eb-1a-visa-filings-surge-as-indian-professionals-shift-away-from-h-1b/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/us/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/layoffs/indian-h-1b-workers-caught-in-fresh-wave-of-meta-amazon-tech-layoffs"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/8/8e/H-1B_Visa_Updates.jpg",
        "image_caption": "H-1B visa application documents at the US Citizenship and Immigration Services",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, the calculus for Indian engineers in America was simple, if brutal: find a sponsor, file the H-1B, join the green card queue, and wait. The queue for Indians in the EB-2 and EB-3 employment-based categories stretches decades. But the alternative — leaving the country you have built a life in — was worse. So people waited.

That calculus is changing. Rapidly.

USCIS data shows that approximately 7,300 EB-1A "extraordinary ability" petitions were filed in the first quarter of 2025, a 50% jump from the prior quarter. Total filings for the year are tracking nearly 50% higher than the previous year. Indians, who account for roughly 70% of all approved H-1B petitions, are driving the surge.

The EB-1A is not new. But the desperation fuelling its adoption is.

## The 60-day trap

The trigger is structural, not cyclical. More than 185,000 tech workers have been laid off globally in 2026 alone. Oracle confirmed it cut 21,000 employees — 13% of its workforce — citing AI-driven restructuring. Meta laid off roughly 8,000. Amazon, Cisco, and Microsoft have each announced rounds of their own.

For an American worker, a layoff is painful. For an Indian H-1B holder, it is existential. The moment an employer terminates a sponsorship, a 60-day clock begins. Within that window, the worker must find a new H-1B sponsor, switch visa categories, or leave the United States. Sixty days to upend a mortgage, a school district, a spouse's career, a life.

Immigration experts describe scenes of panic. "Many of them lose one or two weeks just in that shock," said Khanderao Kand, founder of the Global Indian Technology Professionals Association. The remaining weeks are consumed by frantic applications to companies that may themselves be in the middle of hiring freezes.

## Why EB-1A is different

The EB-1A visa category offers something the H-1B never has: independence from an employer. It is a self-petitioned green card pathway for individuals who can demonstrate "extraordinary ability" in their field — a standard that sounds rarefied but has been broadened considerably by recent USCIS guidance.

Applicants must meet at least three of ten criteria, which can include published work, significant contributions to a field, high remuneration, or evidence of original work of major significance. Critically, modern forms of evidence — product adoption metrics, venture-backed growth, patents, and GitHub contributions — now qualify.

For a senior software engineer who has led teams at Google, shipped products used by millions, or published papers at NeurIPS, the bar is achievable. Not easy. But achievable.

The appeal is obvious. An EB-1A green card does not depend on an employer's willingness to sponsor. It does not reset if you change jobs. It does not evaporate if a CEO decides to "pivot to AI" and restructure your division on a Tuesday morning. If the petition is filed and you are laid off the next day, the application keeps moving.

## The $100,000 accelerant

The Trump administration's September 2025 proclamation imposing a $100,000 fee on new H-1B visa applications added urgency to the shift. Though a federal judge in Boston struck down the fee in June, ruling it an unlawful tax Congress never authorised, the legal landscape remains unsettled. A Washington, D.C. court had earlier upheld the fee, and the administration has promised to appeal. The fee is technically scheduled to expire in September 2026, but nobody in the Indian tech community is counting on that.

The uncertainty itself is the problem. When the cost of an H-1B petition can swing from a few thousand dollars to $100,000 based on a presidential proclamation and a judicial coin flip, employers recalculate. Some pull back from sponsorship altogether. Others shift hiring to cheaper jurisdictions. Either way, the Indian professional in Cupertino or Redmond is left holding the risk.

## A structural shift, not a moment

Immigration attorneys report that the EB-1A surge is not a momentary spike. "This is a clear strategic move by global talent, especially Indian professionals, to secure a stable pathway into the US without being dependent on a single employer," said Frederick Ng, co-founder of immigration firm Beyond Border.

The shift carries irony. The H-1B programme was designed to tie foreign workers to employers, ensuring that immigration served corporate labour needs. The EB-1A was designed for Nobel laureates and Olympic athletes. What is happening now is that a generation of Indian engineers — people who built the infrastructure of American technology — are discovering that their careers qualify them as extraordinary by the government's own criteria.

They are filing the paperwork themselves. And they are not waiting for permission."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
