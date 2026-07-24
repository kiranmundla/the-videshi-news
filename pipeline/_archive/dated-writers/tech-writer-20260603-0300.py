#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-03 03:00 UTC run"""

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

# Validate image URL
def validate_image(url):
    try:
        r = requests.head(url, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            return True
    except Exception:
        pass
    return False


articles = [
    # -------------------------------------------------------------------
    # ARTICLE 1: Computex 2026 — Year of Agents
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Computex 2026 Declared the Year of AI Agents. Perplexity's Aravind Srinivas Was on Stage to Prove It.",
        "subheadline": "Qualcomm launched Dragonfly to challenge Nvidia in data centres, Intel showed hybrid agent inference with an Indian-origin AI founder, and AMD warned the memory crisis has years to run.",
        "slug": make_slug("computex-2026-qualcomm-dragonfly-aravind-srinivas-agents"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Aravind Srinivas, the Indian-origin CEO of Perplexity, demonstrated hybrid agent inference alongside Intel's CEO — a rare moment of Indian founder visibility at the world's biggest hardware event. Qualcomm and Intel both employ thousands of Indian engineers on Snapdragon and Xeon teams. The agent-driven chip upgrade cycle creates new career lanes for diaspora engineers in edge AI and data centre architecture.",
        "tags": ["computex", "qualcomm", "dragonfly", "aravind-srinivas", "perplexity", "ai-agents", "intel", "amd"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/tech-leaders-signal-the-agent-led-era-of-personal-computing-at-computex-2026/article69643210.ece"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/qualcomm-says-2026-is-the-year-of-agents-unveils-dragonfly-ai-data-center-brand/"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-launches-new-chip-bring-ai-directly-personal-computers-2026-06-02/"},
            {"name": "StockTwits", "url": "https://stocktwits.com/news/qcom-stock-slides-premarket-qualcomms-dragonfly-ai-push-gets-overshadowed-by-nvidias-computex-blitz/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Computex 2026 opened in Taipei this week with a declaration that would have sounded absurd two years ago: the personal computer is being redesigned not for the human sitting in front of it, but for the AI agent running behind it.

Qualcomm's CEO Cristiano Amon made the claim explicitly. "Future devices will have two personalities," he said during his keynote ahead of the trade show's June 2–5 run. "One personality serves the human user. The other serves the AI agent. Future devices will be used at the same time by both humans and agents working in the background."

## Qualcomm's Data Centre Gambit

The headline product was Dragonfly, Qualcomm's new umbrella brand for data centre compute — a direct challenge to Nvidia's dominance in AI infrastructure. Details were sparse by design. Amon said more would follow at Qualcomm's Investor Day on June 24. But the strategic intent was unmistakable: the company that built its empire on mobile Snapdragon chips now wants a piece of the data centre market that Nvidia has made the most valuable real estate in technology.

The timing matters. Qualcomm shares had surged nearly 40 per cent in May, their best month since September 2019. But the Dragonfly announcement was immediately overshadowed by Nvidia's own Computex reveal — the Vera Rubin AI chip entering full production and the N1X AI PC processor — sending Qualcomm stock down 7 per cent in premarket trading.

## An Indian Founder on the Intel Stage

The most striking moment for the Indian technology diaspora came not from Qualcomm but from Intel. CEO Lip Bu Tan brought Aravind Srinivas, the Indian-origin co-founder and CEO of Perplexity AI, on stage to demonstrate what Intel calls "hybrid agent inference."

The concept is elegantly simple and potentially transformative: within the same system, local AI agents running on Intel chips handle tasks involving sensitive private data — financial documents, medical records, proprietary code — while computationally heavier reasoning tasks are routed to cloud models. Privacy stays on device. Power stays in the cloud.

For Srinivas, a graduate of IIT Madras who built Perplexity into a search-engine challenger valued at over $9 billion, the Computex stage was a validation of a thesis he has been articulating for months: that AI agents need to be distributed across hardware, not centralised in a handful of cloud data centres. That an Indian-origin founder was chosen to make this case alongside the CEO of Intel, at the world's most important hardware conference, was not lost on the audience.

## The Memory Crisis Nobody Is Solving Fast Enough

Away from the keynote stages, AMD's David McAfee, who leads the Ryzen processor products team, offered a sobering counterpoint to the agent euphoria. The global memory market, he said, is in the midst of a structural undersupply that AI demand has made significantly worse.

"Memory has historically gone through these mega cycles where prices get really high because the market is undersupplied and then prices normalise when the market is oversupplied," McAfee told *BusinessLine*. "We are on the undersupplied side of things now. It will take a few years for the capacity to catch up. But it's not a forever problem."

The qualifier — "not a forever problem" — is doing a lot of work. New fab capacity takes three to five years to bring online. In the interim, every AI workstation, every autonomous agent running locally, every Dragonfly-branded data centre server will compete for the same constrained pool of high-bandwidth memory.

## What the Token Math Means

Amon offered a projection that crystallises the scale of what agents will demand from hardware. He estimated that a single conversational AI prompt requires roughly 10,000 tokens. A reasoning task needs about 100,000. An agentic AI task — where the system plans, executes, and iterates autonomously — consumes approximately 1 million tokens.

Global token demand within a 10-second window, he said, is estimated at 31.7 billion tokens in 2026. By 2030, that number is projected to reach 1.27 trillion tokens. If those numbers hold, every layer of the compute stack — from the chip to the memory to the network — must be rebuilt.

For Indian engineers working across Qualcomm's Snapdragon teams, Intel's design centres in Bengaluru and Hyderabad, and AMD's verification labs, this is not an abstract technology shift. It is the operating reality of the next decade of their careers. The companies building agents need the people who can build the silicon to run them. And a disproportionate share of those people are Indian."""
    },

    # -------------------------------------------------------------------
    # ARTICLE 2: India Tech Hiring 28-Month Low
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Tech Job Market Just Hit a 28-Month Low. More Indians May Now Be Returning from America Than Leaving for It.",
        "subheadline": "Active tech openings fell to 93,000 in June, entry-level hiring collapsed 44 per cent, and staffing firm Xpheno says H-1B returnees could outnumber outbound workers for the first time.",
        "slug": make_slug("india-tech-hiring-28-month-low-h1b-returnees-xpheno"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "The convergence of a weak Indian hiring market with rising H-1B uncertainty creates an unprecedented squeeze for Indian tech professionals on both sides of the Pacific. Those in the US face the 60-day clock after layoffs; those returning find a domestic market at its weakest in over two years. For NRI families weighing the stay-or-return decision, the data suggests neither option is comfortable right now.",
        "tags": ["h-1b", "india-hiring", "tech-jobs", "return-migration", "xpheno", "it-services"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "People Matters", "url": "https://www.peoplematters.in/article/talent-acquisition/indias-tech-hiring-drops-to-28-month-low-as-active-openings-fall-to-93000-44846"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/india-incs-fresher-hiring-sees-steep-drop-amid-ai-adoption"},
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/nvidia-expands-h1b-hiring-amid-job-loss-reports-due-to-ai"},
            {"name": "VisaVerge", "url": "https://www.visaverge.com/immigration-news/nvidia-h-1b-hiring-rises-as-100k-fee-bites-fy-2026/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/7581038/pexels-photo-7581038.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """The numbers arrived this week with the quiet brutality of a spreadsheet that contains no good news. India's active technology job openings fell to 93,000 in June 2026, according to specialist staffing firm Xpheno's latest Active Tech Jobs Outlook report — the lowest in 28 months and a 14 per cent decline from the previous month.

The year-on-year picture is worse. Tech openings are down 17 per cent. Entry-level positions — the on-ramp for India's annual flood of engineering graduates — have cratered 44 per cent year-on-year, falling to just 10,000 openings. Senior-level positions dropped 67 per cent. Even mid-level roles, which account for the largest share at 46,000 openings, are contracting.

Technology, which once accounted for well over half of all active talent demand in India, has now fallen below the 50 per cent contribution mark for three consecutive months. The sector that defined India's white-collar economy is retreating.

## The Reverse Migration Problem

But the most consequential finding in the Xpheno report is not about India at all. It is about America.

The staffing firm noted that "the number of technology professionals returning from the US could potentially exceed the number of professionals moving there this year." If confirmed, it would mark the first time in the modern history of India's IT industry that the flow of technical talent between the two countries has reversed direction.

The mechanism is straightforward. Over 140,000 tech workers have been laid off in the US in 2026 so far. Companies like Meta, Google, and Amazon have cut H-1B visa certifications by nearly 40 per cent. Under American immigration rules, most H-1B holders get 60 days after losing a job to find a new sponsor or leave the country. With fewer companies sponsoring, the arithmetic turns harsh quickly.

Meanwhile, the $100,000 overseas filing surcharge introduced for H-1B petitions has raised the cost of sponsorship, making smaller companies — the ones most likely to hire displaced workers — reluctant to file new petitions. A weighted lottery system now favours higher-paid applicants, further stratifying the market.

## AI Is Not Creating, It Is Compressing

The domestic picture is not offering much of a cushion. IT services hiring in India declined 16 per cent month-on-month. Global Capability Centre hiring, which had been the one bright spot — up 31 per cent year-on-year — fell 6 per cent in the most recent month.

At a Reuters summit last week, executives from multinational firms including Novo Nordisk, Daimler Truck, and Epsilon all said the same thing in slightly different ways: their India operations are growing, but with AI doing more, they need fewer people to deliver the growth.

Lalit Ahuja, CEO of ANSR, which helps multinationals set up GCCs in India, was blunt. "Companies are hiring fewer people, just as a matter of abundant caution," he said.

The irony is acute. Indian IT was built on the promise that a well-trained engineer in Bengaluru could do the same work as one in San Jose at a fraction of the cost. Now AI is making the same promise about software itself — that code can be written, tested, and deployed with dramatically fewer humans in the loop. The productivity advantage that made Indian IT indispensable is being replicated by the technology Indian IT workers helped build.

## The Structural Shift Beneath the Cycle

For Indian professionals weighing the stay-or-return calculus, the Xpheno data points to an uncomfortable conclusion: this is not a cyclical downturn. Technology's share of total hiring demand has been declining for three consecutive months, even as the broader Indian economy — manufacturing, infrastructure, services — continues to grow.

TCS laid off approximately 12,000 employees this year. Accenture is spending $1 billion retraining staff with an explicit warning that those who cannot adapt will be let go. Infosys, which hired 50,000 freshers in a single year not long ago, has dramatically scaled back campus recruitment.

The question for the diaspora is no longer "should I stay in America or go home?" It is something harder: "which version of professional uncertainty do I prefer?" For the first time in a generation, there is no obviously right answer."""
    },

    # -------------------------------------------------------------------
    # ARTICLE 3: Coinbase Relaunches in India
    # -------------------------------------------------------------------
    {
        "id": str(uuid.uuid4()),
        "headline": "Coinbase Just Relaunched in India with Direct Rupee Trading. The Last Time It Tried, It Lasted Three Days.",
        "subheadline": "The world's largest publicly listed crypto exchange is back with IMPS deposits, local rupee order books, and perpetual futures — four years after its UPI launch was shut down within 72 hours.",
        "slug": make_slug("coinbase-india-relaunch-inr-rupee-trading-crypto"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors who hold crypto through US-based accounts on Coinbase can now see the same platform operational in India — potentially simplifying cross-border portfolio management. The 30 per cent tax on Indian crypto gains matters for anyone considering moving assets back. And the Indian developer ecosystem on Coinbase's Base L2 network — over 4,000 builders, 150 startups — represents a growing career path for diaspora engineers interested in blockchain.",
        "tags": ["coinbase", "india", "cryptocurrency", "inr", "crypto-regulation", "fintech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/coinbase-offers-trading-using-indian-rupee-2026-06-01/"},
            {"name": "Livemint", "url": "https://www.livemint.com/market/cryptocurrency/coinbase-launches-in-india-with-direct-inr-support-11748725145698.html"},
            {"name": "CoinCentral", "url": "https://coincentral.com/coinbase-adds-direct-rupee-rails-as-india-crypto-push-expands/"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/cryptocurrency/coinbase-launches-in-india-with-direct-inr-support-for-crypto-trading"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6770521/pexels-photo-6770521.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """In April 2022, Coinbase launched in India with UPI support, a press release, and considerable fanfare. Within 72 hours, the National Payments Corporation of India publicly said it was not aware of any UPI arrangement involving a cryptocurrency exchange. The service was suspended. Brian Armstrong later attributed the shutdown to informal pressure from the Reserve Bank of India. It was, by any measure, a humiliation.

Four years later, Coinbase is back. And this time, it has done its homework.

## The Mechanics of a Second Try

The world's largest publicly listed cryptocurrency exchange announced on Monday that Indian customers can now deposit and withdraw rupees directly through the Immediate Payment Service channel — bypassing the UPI infrastructure that proved so politically fraught in 2022.

The offering includes spot trading across a range of crypto assets, perpetual futures contracts for eligible users, and local rupee order books that provide dedicated liquidity for the Indian market while maintaining access to Coinbase's global exchange. For active traders, Coinbase Advanced brings institutional-grade APIs, TradingView charting integration, and advanced order tools. Deposits carry zero fees.

"India has long been one of the most important markets in crypto: in terms of developer talent, trading activity, and the broader adoption of blockchain technology," said John O'Loghlen, Coinbase's regional managing director for Asia Pacific.

## The Market Coinbase Is Chasing

The flattery is not undeserved. Chainalysis ranked India first in its Global Crypto Adoption Index for the third consecutive year in 2025. The country's crypto market reached approximately $3 billion last year, and IMARC Group projects it could grow to $14.2 billion by 2034, implying a compound annual growth rate of nearly 19 per cent.

Those numbers exist despite what might be the most punitive crypto tax regime of any major economy. India levies a flat 30 per cent tax on cryptocurrency trading gains — with no provision for offsetting losses from other crypto trades. On top of that, a 1 per cent tax deducted at source applies to every transaction. The combination has driven significant volumes offshore and into peer-to-peer channels that operate in regulatory grey zones.

Coinbase's bet is that institutional-grade infrastructure and direct banking access can pull some of that volume back onshore. The zero-fee deposit structure is clearly designed to undercut the friction that has kept some Indian retail investors on less regulated platforms.

## What Changed Since 2022

The regulatory landscape, while still lacking a dedicated crypto law, has shifted in Coinbase's favour. India's Financial Intelligence Unit now maintains a registry of virtual digital asset service providers, and Coinbase has secured registration. The company has complied with anti-money laundering requirements and says it follows local taxation rules.

The approach is markedly different from the 2022 attempt. Instead of trying to plug into India's payment infrastructure and hoping regulators would look the other way, Coinbase has spent the intervening years building relationships. It invested in CoinDCX, one of India's leading domestic crypto exchanges. It funded over $1 million in grants, hackathons, and fellowships for Indian developers building on Base, its Ethereum Layer 2 network. More than 4,000 builders in India have built on Base, and roughly 150 of those projects have grown into startups.

## The NRI Calculus

For Indian Americans and other NRI investors, the relaunch creates a potentially interesting symmetry. Many already use Coinbase through their US-based accounts. Having the same platform operational in India — with local rupee liquidity and Indian banking integration — could simplify portfolio management for those who maintain financial lives across both countries.

But the tax implications are a wall. The 30 per cent flat rate on gains in India, combined with no loss offset, means that the cost of trading on the Indian platform is structurally higher than doing so through a US account where crypto is taxed as property at capital gains rates. For high-volume traders, the difference is material.

Coinbase is positioning the launch around trust, compliance, and execution quality rather than price. O'Loghlen pointed to the company's Nasdaq listing and institutional custody track record as differentiators. The implicit argument: in a market where exchanges have collapsed, been hacked, or been banned, the most valuable feature is not the cheapest fee but the highest probability that your money is still there tomorrow.

Whether India's retail investors — who have spent four years navigating the market through P2P workarounds and domestic exchanges — will find that argument compelling enough to move remains the open question. Coinbase is betting they will. It has, after all, tried this before."""
    },
]

# Validate images and insert
for art in articles:
    img = art.get("image_url", "")
    if img and not validate_image(img):
        print(f"⚠️  Image validation failed for {art['slug']}, proceeding anyway")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
