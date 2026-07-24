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
        "headline": "Oracle Just Told the SEC That AI Cost 21,000 Jobs. India Took More Than Half of Them.",
        "subheadline": "The most candid admission yet that AI is replacing tech workers came in a regulatory filing — and roughly 12,000 of the cuts landed in India, where Oracle's largest workforce sits.",
        "slug": make_slug("oracle-21000-ai-layoffs-india-12000-cuts-h1b-nri-tech-workers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Oracle is the first major tech firm to put AI job losses in writing to regulators, and with India absorbing the largest share, it is a warning shot for every Indian engineer on an H-1B watching the same companies spend on data centers while thinning their ranks.",
        "tags": ["ai", "layoffs", "oracle", "h1b", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/oracle-workforce-shrinks-about-21000-employees-amid-ai-adoption-2026-06-23/"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/oracle-stock-annual-filing-21000-jobs-cut-ai-spending/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/tech-layoffs-2026-list/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489151/pexels-photo-17489151.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Servers in a data center, the infrastructure Oracle is spending tens of billions to expand even as it cuts staff",
        "image_attribution": "Pexels",
        "body": """Tech companies have spent the past two years insisting that layoffs were about "efficiency," "rebalancing," or "right-sizing" — anything but the obvious. Oracle just dropped the euphemisms. In its annual report filed with the U.S. Securities and Exchange Commission this week, the company stated plainly that "the adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce."

That is the bluntest acknowledgement yet from a major employer that artificial intelligence is taking jobs. And the number is large: Oracle's headcount fell from roughly 162,000 a year ago to 141,000 as of May 31, a cut of about 21,000 people, or 13% of its global workforce. The company spent $1.84 billion on severance and exit costs in the fiscal year, nearly five times the $374 million it spent the year before.

## Where the cuts landed

For Indian readers, the geography matters more than the headline. India is Oracle's single largest employee base outside the United States, and reports indicate that roughly 12,000 of the eliminated positions — more than half the global total — were in India. Many were mid- and senior-level engineers, not entry-level staff. The March round, which preceded this filing, was abrupt: termination emails reportedly arrived as early as 6 a.m., with system access revoked immediately.

This is not a company in distress papering over weakness. Oracle's cloud revenue has grown sharply, and its backlog of contracted future business has swelled past half a trillion dollars on the strength of data-center deals with OpenAI and Meta. The cuts are a deliberate trade: human capital for compute power. Oracle plans capital expenditure of around $70 billion this fiscal year, funded partly by raising $40 billion in fresh debt and equity, to build the AI infrastructure it is betting its future on.

## Why the NRI engineer should pay attention

The diaspora angle is not abstract. Hundreds of thousands of Indians work at the U.S. tech and enterprise firms now cutting staff — Oracle, Amazon, Meta, Microsoft, Intel — and tens of thousands hold those jobs on H-1B or L-1 visas. For a visa holder, a layoff is not just a lost paycheck. It starts a 60-day clock to find a new sponsoring employer or leave the country. In a market where 196 tech firms have shed more than 119,800 workers this year, according to tracker Layoffs.fyi, that clock is unforgiving.

Oracle's filing also matters because it sets a precedent. Companies have legal incentives to be careful about what they attribute to AI in regulatory documents — overstating it invites scrutiny, understating it invites shareholder lawsuits. By naming AI directly, Oracle has effectively given other firms cover to do the same. Microsoft has already introduced its first-ever voluntary buyouts in its 51-year history; Amazon, Meta and Intuit have all cut deeply while pouring money into data centers.

For the Indian professional, the lesson cuts two ways. The roles most exposed are precisely the kind of mid-level engineering and support functions that powered the H-1B pipeline for two decades — work that AI coding agents now do faster. But the same buildout is creating demand for a narrower, higher-value set of skills: people who can design, train and operate AI systems rather than maintain legacy ones. Oracle itself warned in its filing that aggressive restructuring risks "shortages of sufficiently skilled employees" and "loss of valuable institutional knowledge."

## What's next

Oracle has signaled that more cuts may come as AI deployment deepens. For the diaspora, the takeaway is to treat the AI transition as a skills question, not a loyalty one. The companies are being explicit that they will spend on silicon over salaries when the math favors it. The engineers who thrive will be the ones who move up the stack toward AI infrastructure — and who keep a clear-eyed read on which side of the trade their own role sits on."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Got Its First 'Sovereign AI' Unicorn. The Twist Is Who Wrote the Biggest Cheque.",
        "subheadline": "Bengaluru's Sarvam AI raised $234 million at a $1.5 billion valuation — but the lead investor was not a global VC. It was HCLTech, an Indian IT giant betting $150 million on homegrown models.",
        "slug": make_slug("sarvam-ai-unicorn-hcltech-150-million-sovereign-ai-india-nri-bessemer"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Sarvam's round is the clearest sign yet that India intends to build its own AI stack rather than rent one from Silicon Valley — a shift that reshapes where diaspora engineers and NRI investors place their bets on the next decade of Indian tech.",
        "tags": ["ai", "indian-tech", "sarvam", "hcltech", "startups", "sovereign-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/sarvam-ai-unicorn-234-million-hcltech/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-hcltech-buy-105-stake-sarvam-ai-2026-06-15/"},
            {"name": "Inc42", "url": "https://inc42.com/features/hcltech-sarvam-ai-bet-patient-capital/"},
            {"name": "Mint", "url": "https://www.livemint.com/companies/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A microprocessor circuit board, the kind of compute infrastructure underpinning India's push to build sovereign AI models",
        "image_attribution": "Pexels",
        "body": """India has plenty of engineers building AI for American companies. What it has lacked is its own foundational models — the kind a government or a bank can run without depending on a system controlled in San Francisco or Beijing. Sarvam AI just became the marquee test of whether that can change.

The Bengaluru startup raised $234 million at a $1.5 billion valuation, making it India's second AI unicorn after the troubled Ola Krutrim. It is now widely described as the country's first true "sovereign AI" unicorn. But the round's real significance is not the size. It is the lead investor.

## Not a VC — an IT giant

The $234 million was led not by a global venture firm but by HCLTech, the IT-services arm of the HCL conglomerate, which committed $150 million for a roughly 10.5% stake. Bessemer Venture Partners co-led, with continued participation from existing backers Khosla Ventures and Peak XV Partners.

This is the largest capital infusion by an Indian IT-services company into an AI startup, and analysts are treating it as a possible turning point. Nomura called it the first investment of its kind by an Indian IT firm in a sovereign AI platform. The comparison being drawn — imperfect but telling — is to Microsoft's early backing of OpenAI: a deep-pocketed incumbent using legacy profits to underwrite a frontier bet.

HCLTech is not just writing a cheque. It brings enterprise relationships, a global delivery workforce and government clients. The plan is to fuse Sarvam's models — open-source releases at 30 billion and 105 billion parameters, designed for Indian languages — with HCLTech's enterprise muscle to sell AI products to businesses and governments wary of routing sensitive data through foreign systems. Sarvam's models are already being deployed in banking, insurance, government services and defense.

## Why "sovereign" is the operative word

The timing is not coincidental. Brokerage Bernstein warned investors this week that India risks becoming dependent on foreign AI unless it builds its own large language models, comparing AI to strategic assets like "fighter jets" that could be subject to export controls. That fear is not hypothetical: the U.S. government's recent move to restrict access to a frontier model from Anthropic for foreign nationals sent a jolt through India's tech policy circles. "India's core intelligence layer, from enterprise software to defence and space, could be powered by foreign LLMs," the Bernstein note read. "Enter a geopolitical disruption, and that access could be curtailed overnight."

## What it means for the diaspora

For NRI investors and engineers, Sarvam reframes the India opportunity. For years the diaspora's mental model of Indian tech was either outsourcing (TCS, Infosys) or consumer apps (Flipkart, Swiggy). Sovereign deep tech is a third category — and it is the one drawing strategic, patient capital rather than quick-flip venture money. Celesta Capital's Sriram Viswanathan, an early backer of drone maker IdeaForge, predicts India's deep-tech startups will attract sharply higher capital over the next year as the ecosystem matures.

There is also a talent signal. One of the diaspora's quiet anxieties is the "reverse brain drain" running the wrong way — India's most ambitious deep-tech founders still buying one-way tickets to America. A credible, well-funded sovereign AI champion gives the most senior Indian-origin AI researchers in the Bay Area and London a reason to at least consider building at home, or advising those who do.

The caution is real: Krutrim's collapse is a recent reminder that valuation is not vindication, and building foundational models is brutally capital-intensive. But for the first time, an Indian incumbent has decided the country's AI future is worth bankrolling itself. For a diaspora that has spent a generation building other people's AI, that is a story worth watching closely."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Gets the Headlines. But an Indian-Origin CEO Sells the One Chip AI Data Centers Can't Run Without.",
        "subheadline": "SiTime, led by Rajesh Vashist, makes the timing chips that keep AI clusters in sync. Revenue jumped 88%, the stock has roughly tripled this year, and inference may need four times more of its product.",
        "slug": make_slug("sitime-rajesh-vashist-ai-timing-chips-data-center-nvidia-nri-semiconductor"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "While the diaspora obsesses over Nvidia, an Indian-origin CEO is quietly riding the same AI wave from an unglamorous corner of the chip stack — a reminder that the semiconductor boom NRI investors and engineers are tracking runs far deeper than GPUs.",
        "tags": ["semiconductor", "ai", "indian-tech", "sitime", "data-center", "stocks"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/research/ibd-50-stocks-to-watch/sitime-stock-ai-data-center-chipmaker/"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/symbol/SITM"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/SITM/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A close-up of a motherboard and microchips, the kind of precision components SiTime designs for AI data centers",
        "image_attribution": "Pexels",
        "body": """Ask anyone in the Indian diaspora to name the company powering the AI boom and you will hear "Nvidia" before you finish the sentence. Ask about the chip that keeps Nvidia's GPUs talking to each other in perfect lockstep, and you will get a blank stare. That chip — the precision clock — is SiTime's business. And its CEO, Rajesh Vashist, is having the best year of his career.

SiTime designs MEMS-based timing semiconductors: tiny components that act as the metronome for electronic systems, generating the precise clock signals that synchronize data movement. They are used in more than 400 applications, from autonomous vehicles and drones to military aerospace. But the explosive demand is coming from one place: AI data centers.

## The math behind the boom

Here is the part the GPU headlines miss. An AI cluster is only as fast as its slowest, least-synchronized link. As models move from training to inference — the stage where they actually answer queries at scale — the timing requirements multiply. By SiTime's own estimate, inference infrastructure needs two to four times more timing content than conventional systems. Every rack of accelerators is, in effect, a new customer for clock chips.

The financials reflect it. Revenue surged 88% to $113.6 million in the most recent quarter, with AI-focused product revenue jumping 158% to roughly two-thirds of sales. Gross margin expanded to 64.5%, and operating cash flow more than doubled year-over-year. Management raised full-year growth guidance to at least 80%. Vashist, in a recent CNBC interview, pointed to eight straight quarters of triple-digit earnings growth and 80% growth in the AI data-center business this year.

The market has noticed. SiTime stock has roughly tripled in 2026, peaking above $900 in May before settling into a volatile consolidation around $700 — a $19 billion company now, up from relative obscurity. Wall Street is split on valuation: Goldman Sachs and Roth carry buy ratings with targets up to $900, while the consensus flags the stock as richly priced after its run.

## Why this matters to the diaspora

For NRI investors, SiTime is a lesson in where the real semiconductor leverage sits. The diaspora's portfolios are heavy on the obvious AI names, but the supply chain that feeds the boom is full of less-visible Indian-origin leadership. Vashist — who has spent decades in Silicon Valley's chip industry and acquired Renesas's timing business to expand SiTime's data-center exposure — is running one of the purest plays on AI infrastructure that most retail investors have never heard of.

There is a broader pattern here that should resonate with Indian engineers in the Bay Area and beyond. The semiconductor opportunity is not just GPUs and fabs. It is the entire stack — timing, networking, memory, packaging, power — and Indian-origin executives and engineers are embedded across all of it. The same week SiTime's numbers drew attention, Indian-American-led firms were in the news across memory chips, AI networking and data-center software. For a diaspora professional weighing where to specialize, the message is that the highest-leverage corners of the chip world are often the least glamorous.

## The caution

SiTime's stock is not for the faint-hearted: a beta near three and a 21-day average true range above 7% mean stomach-churning swings. The company is still posting GAAP losses on a trailing basis as it invests for growth. But the structural story — that AI clusters cannot scale without ever more precise synchronization — is exactly the kind of unglamorous, picks-and-shovels bet that tends to reward patience. And it is being run by someone whose name the diaspora ought to know better than it does."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
