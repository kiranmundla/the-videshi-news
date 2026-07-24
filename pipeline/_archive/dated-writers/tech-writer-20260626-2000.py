#!/usr/bin/env python3
"""
Videshi Technology Writer — 2026-06-26 20:00 PDT
3 articles: tech sell-off, Anthropic/AWS Bengaluru accelerator, Mirendil AI startup
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
    return slug[:70].rstrip('-') + "-20260627"


# ─────────────────────────────────────────────
# ARTICLE 1: Global Tech Sell-Off
# ─────────────────────────────────────────────
art1_body = """The numbers are ugly and they arrive at exactly the wrong moment for anyone whose pay slip lists restricted stock units as a major line item.

The Nasdaq Composite slumped 4.6 per cent this week, its worst five-day stretch since early June. The S&P 500 shed 2 per cent. And the so-called Magnificent Seven — Apple, Microsoft, Alphabet, Amazon, Meta, Nvidia, and Tesla — collectively lost nearly $2.8 trillion in market capitalisation this month alone, a record monthly wipeout if it holds through Monday.

## The trigger

A chain reaction that started with Micron Technology's blockbuster earnings on Wednesday and ended with a sell-off that spanned Seoul, Tokyo, and Wall Street. Micron reported record quarterly revenue of $41.5 billion, confirming what the market already suspected: AI-grade memory chips are in ferocious demand, supply is constrained through 2027, and prices are surging. That sounds like a good-news story — until you follow the cost chain upward.

Apple and Microsoft both announced consumer price hikes this week, blaming rising memory costs. MacBooks, iPads, and Xbox hardware all got more expensive. Investors did the maths: if Micron's windfall is everyone else's margin squeeze, the AI infrastructure buildout may be eating its own returns. Alphabet, which disclosed $180–190 billion in planned 2026 capital expenditures — more than double last year — saw its stock slide despite its impending addition to the Dow Jones Industrial Average on Sunday.

Then came Friday's sucker punch. The New York Times reported that OpenAI is considering pushing its initial public offering into 2027, seeking a $1 trillion valuation that the current market plainly will not support. SoftBank, OpenAI's largest backer, tumbled 12 per cent in Tokyo. SpaceX shares, already down more than 30 per cent from their post-IPO highs, slid further. South Korea's Kospi index dropped 5.8 per cent, tripping circuit breakers for the second time in a week as memory-chip stocks cratered. SanDisk fell 10 per cent. Broadcom gave back 4 per cent. Intel and AMD each dropped more than 2 per cent.

## Why this hits the diaspora hard

For the estimated 300,000-plus Indian tech workers in the United States — many of them at the very companies bleeding market value — the sell-off is not an abstraction. At Google, Microsoft, Meta, and Amazon, equity compensation routinely accounts for 40 to 60 per cent of total pay for mid-to-senior engineers. A 15–25 per cent drawdown in a single month does not just dent net worth; it resets the math on down payments, children's college funds, and the perennial question of whether to stay in the Valley or return to Bengaluru.

H-1B holders face an additional wrinkle. Unlike citizens who can ride out volatility, visa-dependent workers whose companies announce layoffs as part of AI-driven restructuring — Oracle just shed 21,000 roles — have 60 days to find a new sponsor or leave the country. A falling stock price does not trigger layoffs on its own, but it compresses the margin of error.

NRI investors in India-listed IT stocks are not insulated either. TCS, Infosys, and Wipro have all flagged AI's disruptive potential for the traditional services model. A sustained US tech correction would slow the deal pipeline that feeds Indian IT's $315 billion revenue base.

## What comes next

Wall Street enters the final week of the first half bruised but not broken. The Nasdaq is still up roughly 20 per cent on the year, and memory-chip demand is structurally real — Micron's $100 billion in contracted floor-price revenue is not a mirage. But the market is clearly repricing the assumption that every dollar spent on AI infrastructure yields a dollar of near-term profit. Inflation breaking above 4 per cent and the Federal Reserve signalling a possible September rate hike only sharpen the anxiety.

For the diaspora professional watching their Schwab account turn red, the message is unsettling but not unfamiliar: the industry that made your career can also revalue it overnight."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The AI Trade Just Had Its Worst Week in Months. For Indian Tech Workers, the Pain Is Personal.",
    "subheadline": "The Nasdaq lost 4.6 per cent, the Magnificent Seven shed $2.8 trillion in a month, and the stock-heavy pay packets that anchor diaspora life in Silicon Valley are shrinking fast.",
    "slug": make_slug("ai-trade-worst-week-nasdaq-mag-seven-indian-tech-workers"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian tech workers at FAANG companies derive 40-60% of compensation from stock — a 15-25% monthly drawdown directly hits down payments, college savings, and stay-vs-return calculations, while H-1B holders face layoff vulnerability with only 60 days to find new sponsors.",
    "tags": ["ai", "stock-market", "silicon-valley", "indian-tech-workers", "h1b", "magnificent-seven", "nasdaq"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/tech-stocks-just-had-one-of-their-worst-weeks-in-a-year-heres-how-ai-momentum-went-off-the-rails-37034c00"},
        {"name": "Investopedia", "url": "https://www.investopedia.com/markets-news-june-26-2026-11943246"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/investing/stock-market-today-june-26-2026"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/livecoverage/stock-market-today-dow-sp500-nasdaq-live-06-26-2026"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/534216/pexels-photo-534216.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Stock market trading screen displaying financial data and price movements",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 2: Anthropic/AWS Bengaluru Accelerator
# ─────────────────────────────────────────────
art2_body = """Anthropic and Amazon Web Services launched their first joint startup accelerator on Friday — and they chose Bengaluru, not San Francisco or London, as the venue. The India-first programme, which began accepting its inaugural cohort of 40 startups on June 26, is designed to nurture companies building agentic AI: systems that do not merely generate text or images but autonomously execute complex, multi-step workflows.

The accelerator is the latest signal that India is graduating from its long-standing role as a talent pipeline for Western AI labs to something more consequential — a place where frontier AI products are being conceived, built, and deployed.

## What the programme offers

Participating startups receive technical mentorship from Anthropic's research team, access to Claude's frontier models, AWS cloud infrastructure and credits, and introductions to enterprise customers. The cohort was selected from a pool that Anthropic described only as "highly competitive." Among the first confirmed participants is SwishX, a Bengaluru-based company building agentic AI for pharmaceutical and medtech companies — automating the fragmented, spreadsheet-heavy operational workflows that still dominate commercial pharma operations globally.

The format is multi-month, hands-on, and distinctly product-oriented. This is not a hackathon or a demo day incubator. The goal, according to programme materials, is to produce startups capable of shipping autonomous systems into regulated, high-stakes industries.

## Bengaluru's quiet AI ascent

The accelerator's location is no accident. Anthropic opened its first India office in Bengaluru earlier this year, following its announcement that India had become Claude's second-largest consumer market globally. OpenAI, which formally registered in India in 2025, appointed Prabhjeet Singh — formerly president of Uber India — as its managing director for the country just this week. Google has committed $15 billion to an AI hub in Visakhapatnam. Amazon upped its India infrastructure pledge to $48 billion through 2030 just days ago.

The numbers suggest a structural shift, not a publicity exercise. India's deeptech funding hit $1.23 billion in the first half of 2026 alone, according to Tracxn, already approaching the $1.5 billion raised in all of 2025. Venture firms like Accel, now deploying its $650 million eighth India fund, are allocating 10 to 15 per cent of their corpus to manufacturing and deeptech — a sector they barely touched five years ago.

Sarvam, the Bengaluru-based sovereign AI startup, reached unicorn status last week with a $234 million raise led by HCLTech, pushing its valuation to $1.5 billion. Upscale AI, a networking infrastructure firm backed by Premji Invest and Nvidia, hit a $2 billion valuation in its latest funding extension. India now has two AI unicorns — Sarvam and Ola's Krutrim — with a pipeline that suggests more are coming.

## The diaspora calculus

For NRIs watching from Cupertino or Jersey City, the accelerator crystallises a question that has been building for years: is India becoming a place to build an AI company, not just a place to hire engineers for one?

The answer is increasingly yes — with caveats. Compute access remains a bottleneck; India's sovereign GPU capacity is a fraction of what US hyperscalers deploy in a single data centre. Regulatory frameworks for AI are still in draft. And the talent drain to US labs continues, even as Sarvam's co-founder Vivek Raghavan has begun recruiting exceptional Indians based in the United States to "help India in this mission."

But the structural ingredients — capital, customers, regulatory ambition, and now direct support from the world's leading AI labs — are assembling faster than most diaspora professionals expected. The agentic AI accelerator is one more brick in a foundation that is starting to look load-bearing."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic and AWS Just Launched an AI Accelerator in Bengaluru. The Bet Is That India Builds, Not Just Codes.",
    "subheadline": "The India-first programme selects 40 startups building autonomous AI agents, marking another step in Bengaluru's quiet transformation from talent pool to AI product hub.",
    "slug": make_slug("anthropic-aws-agentic-ai-accelerator-bengaluru-india-startups"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRIs are watching India transition from an AI talent farm to an AI product hub — the accelerator alongside Sarvam's unicorn status and $48B in hyperscaler commitments is forcing the diaspora to reassess whether India is now a viable place to build, not just work remotely for US companies.",
    "tags": ["ai", "anthropic", "aws", "bengaluru", "indian-startups", "agentic-ai", "deeptech"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/artificial-intelligence/anthropic-and-aws-select-bengaluru-based-swishx-for-their-inaugural-agentic-ai-accelerator-2026"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/anthropic-open-first-india-office-2026-demand-ai-tools-grows-2025-10-07/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/14/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"},
        {"name": "Livemint", "url": "https://www.livemint.com/companies/news/india-can-still-build-ai-winners-despite-us-china-lead-says-accels-subrata-mitra-11750880756698.html"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Team of developers working together on computers in a modern tech office",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ─────────────────────────────────────────────
# ARTICLE 3: Mirendil — Harsh Mehta's $1B AI startup
# ─────────────────────────────────────────────
art3_body = """When Harsh Mehta cold-emailed Behnam Neyshabur at Google in 2019, the Iranian-born researcher was already a minor celebrity in machine-learning circles, known for foundational work on why deep learning generalises. Mehta, an Indian-origin engineer, wanted to collaborate. Seven years, two companies, and one of the largest seed rounds in Silicon Valley history later, they are co-founders of Mirendil — a startup that raised $200 million this week at a $1 billion valuation to build AI that accelerates AI research itself.

The round, announced Wednesday, was led by Andreessen Horowitz and Kleiner Perkins, with Nvidia also investing. It is among the largest seed financings ever for an AI company and arrives at a moment when the field's biggest labs are racing to automate their own research pipelines.

## What Mirendil actually does

The pitch sounds circular until you unpack it: AI for AI for science. Today's frontier labs — OpenAI, Anthropic, Google DeepMind — use AI internally to speed up model development, but they restrict outsiders from using those tools. Mirendil's bet is that it can build and distribute self-improving AI systems that let any research team — a university biology lab, a materials science startup, a pharmaceutical company — develop specialised models without depending on a frontier lab's proprietary infrastructure.

"What we are doing is kind of AI for AI for science, as opposed to AI for science," Neyshabur, who serves as CEO, told the Wall Street Journal. He cited predicting Alzheimer's risk as one application customers might build on the platform.

Mehta, who serves as CTO, is perhaps uniquely qualified for the job. At Anthropic, he built the first version of the company's autoresearch platform — the internal system that allows AI models to contribute to their own improvement — initially as a team of one. Before that, at Google, he co-drove pretraining and reasoning work on the Gemini model family. Neyshabur, meanwhile, co-led the Discovery team at Anthropic, which aimed to build an AI scientist, and helped develop the computer-use capabilities behind Claude.

## The Indian thread

Mehta's trajectory is a familiar one in Silicon Valley's AI aristocracy. An Indian-origin researcher moves through Google and Anthropic, works on systems that define the frontier, then spins out with the institutional knowledge and relationships to build something independent. It is the same arc that produced Sriram Krishnan (now White House AI advisor), Parag Agrawal (post-Twitter ventures), and Mustafa Suleyman (who left DeepMind to co-found Inflection, then joined Microsoft).

What makes Mirendil's founding team notable is the specific capability they are commercialising. Automated AI research — the ability for models to run experiments, evaluate results, and iterate on their own architectures — is widely regarded as the single most consequential technical frontier in the field. If Mirendil succeeds, it could democratise capabilities that are currently the exclusive province of labs that spend billions on compute.

The team also includes Shayan Salehian, a core engineer from xAI who worked across post-training and reasoning on the Grok models, and Tara Rezaei, a 23-year-old MIT graduate and Olympiad medallist who interned at OpenAI.

## The bigger picture

Mirendil's raise reflects a broader pattern: the talent that built the frontier is leaving the frontier to specialise. OpenAI has lost researchers to at least a dozen startups. Google DeepMind has hemorrhaged talent to Anthropic and beyond — a brain drain that contributed to Alphabet's stock weakness this week. The labs that trained the world's most capable models are now, inadvertently, seeding the ecosystem that may eventually compete with them.

For the diaspora, the story is less about one startup and more about positioning. Indian-origin researchers sit at the core of nearly every major AI lab. As those labs fragment and their alumni spin out, the question is whether that distributed talent translates into distributed ownership — equity, board seats, and founding stakes — or whether it remains, as it has for decades, a story of excellence without commensurate control.

Mehta's $1 billion starting line suggests the answer may be changing."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "An Indian-Origin Engineer Built Anthropic's Self-Improving AI. Now His Startup Is Worth $1 Billion.",
    "subheadline": "Harsh Mehta's Mirendil raised $200 million from Nvidia, Andreessen Horowitz, and Kleiner Perkins to let any lab build AI that accelerates its own research — a capability the frontier giants keep to themselves.",
    "slug": make_slug("mirendil-harsh-mehta-ai-startup-billion-anthropic-nvidia"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CTO Harsh Mehta's trajectory from Google to Anthropic to a $1B startup illustrates how diaspora researchers at frontier AI labs are beginning to convert technical contributions into founding stakes and ownership, not just salaries.",
    "tags": ["ai", "indian-founders", "silicon-valley", "mirendil", "anthropic", "nvidia", "deeptech", "startup"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/anthropic-veterans-startup-seeks-to-help-scientists-develop-their-own-ai-b0134c48"},
        {"name": "Andreessen Horowitz", "url": "https://a16z.com/investing-in-mirendil/"},
        {"name": "Kleiner Perkins", "url": "https://www.kleinerperkins.com/perspectives/mirendil-building-the-system-that-builds-systems/"},
        {"name": "The Decoder", "url": "https://the-decoder.com/ex-anthropic-researchers-launch-ai-startup-mirendil-to-tackle-scientific-research/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/8851456/pexels-photo-8851456.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Scientists collaborating in a modern laboratory with computers and research equipment",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ─────────────────────────────────────────────
# INSERT ALL
# ─────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
