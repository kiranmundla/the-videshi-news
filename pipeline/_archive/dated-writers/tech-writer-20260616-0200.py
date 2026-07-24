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

PICHAI_IMG = "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg"
MEHROTRA_IMG = "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg"
CHANDRA_IMG = "https://upload.wikimedia.org/wikipedia/commons/4/46/Natarajan_Chandrasekaran_-_India_Economic_Summit_2011.jpg"

article1_body = """For a decade, Apple sold a simple promise: the company that made your phone also made the brain inside it. At its developer conference on June 8, that promise quietly expired. The new Siri arriving with iOS 27 this autumn does not run on Apple's own technology. It runs on Gemini, the family of artificial-intelligence models built by Google — a company Apple has spent years framing as its philosophical opposite on privacy.

The arrangement, which Bloomberg's Mark Gurman pegs at roughly $1 billion a year, is the clearest sign yet that no single company can build everything in the AI era. Apple confirmed the collaboration but is careful to keep its own label on the experience: the assistant is still "Apple Intelligence," the models still run on-device and through Apple's Private Cloud Compute, and Apple says it used "the technologies behind Gemini" to develop its next-generation foundation models rather than simply renting Google's chatbot.

## Why this is a Sundar Pichai win

Strip away the branding and the story is about leverage. Google already pays Apple an estimated $20 billion a year to remain the default search engine on the iPhone — an arrangement a US federal judge has called an illegal monopoly. Now Apple is paying Google. The most valuable consumer-hardware company on earth has concluded that the most capable general-purpose AI it can buy comes from a firm run by a Chennai-born, IIT-Kharagpur-trained engineer who took over Google barely a decade ago.

For Sundar Pichai, the deal lands at a useful moment. Alphabet has been pouring capital into AI at a pace that has unnerved some investors — Pichai told this year's Google I/O that capital spending would reach roughly $180–190 billion, nearly six times the 2022 figure. Winning the contract to power Siri is precisely the kind of proof point that justifies the bill: even Apple, the one company with the cash and motive to build its own models, decided Gemini was better.

## What it means for the diaspora

For the tens of thousands of Indian engineers working across Silicon Valley, the deal is a quiet status marker. The two most consequential AI franchises in consumer technology — the iPhone's assistant and Google's own stack — now both depend on infrastructure shaped under Indian-origin leadership, from Pichai at Alphabet to the large contingent of Indian researchers inside Google DeepMind.

It also reshapes the job market that diaspora families watch closely. Apple's decision signals that the premium is shifting from teams that build foundation models from scratch toward teams that integrate, fine-tune and deploy them safely — orchestration, on-device optimisation, privacy engineering. Those are the roles multiplying at Apple, Google and the start-ups in between, and they are disproportionately staffed by Indian and Indian-American talent.

There is a consumer angle, too. The new Siri can read what is on your screen, remember the thread of a conversation and act across apps — searching Photos for pictures of specific family members, drafting a message in your own writing style, planning a route with a stop along the way. For an NRI juggling family logistics across time zones, an assistant that can finally string several steps together without giving up is more than a gimmick. It works on the iPhone 11 and newer, so the upgrade does not require new hardware.

## The catch

Apple is still presenting all of this as its own. Gurman reports that a broader plan — letting users swap in ChatGPT, Claude or Gemini through a Siri "extensions" framework — exists in the first iOS 27 beta but was held back, partly to avoid muddying the message about why Apple leaned on Google in the first place. Regulators are watching: Apple's existing search deal with Google is already in the crosshairs, and a second large payment flowing the other way will draw scrutiny on both sides of the Atlantic.

For now, the takeaway is blunt. The smartest thing about your next iPhone will be built on technology from Apple's biggest rival — and the executive who delivered it grew up in Chennai. In the AI economy, the diaspora is no longer adjacent to the action. It is the action."""

article2_body = """On June 24, Micron Technology will report earnings that almost nobody expects to surprise. Revenue of roughly $33.5 billion, up about 40% from the prior quarter and nearly triple a year ago. Gross margins near 81% — a number unheard of for a company that makes memory chips, historically the most brutally cyclical corner of the semiconductor industry. The stock has already run past $980, pushing Micron's market value above $1.1 trillion.

The quarter, in other words, is priced in. What matters is the guidance for the one after — and the answer will tell every Indian-American investor and chip engineer watching whether the AI memory boom has peaked or has years left to run.

## The HBM machine

Micron's transformation rests on one product: high-bandwidth memory, or HBM, the specialised DRAM stacked vertically and bonded directly to AI accelerators like Nvidia's Blackwell and Vera Rubin chips. Demand is growing roughly 70% a year, and HBM now consumes about a quarter of the world's DRAM wafer capacity. Crucially, Micron has its entire 2026 HBM output not merely reserved but contracted — sold out. Data-center sales now make up more than half the company's revenue.

Analysts have been falling over themselves. Ahead of earnings, TD Cowen's Krish Sankar lifted his price target to $1,500 from $660; RBC's Srini Pajjuri went to $1,200 from $525, arguing the current DRAM upcycle — now in its twelfth quarter — could run another five or six, because HBM "should be largely immune to cyclical declines" as a non-commodity product.

## The bear case the diaspora should not ignore

Here is the uncomfortable arithmetic. Micron holds roughly 21% of the HBM market. South Korea's SK Hynix holds about 62% and owns the deepest relationship with Nvidia. Micron is riding the wave, not steering it. At 46 times trailing earnings, the market is pricing flawless execution for quarters that have not happened. Memory cycles do not announce their turns — margins stay fat until one quarter they slip, and by the time the story changes the stock has already moved. A single soft guidance number on Q4 could compress the multiple back into the 20s or 30s, the difference between a 10% dip and a 40% drawdown.

For NRI investors — many of whom hold Micron, Nvidia and Broadcom as the core of their US tech exposure — June 24 is less an earnings date than a temperature check on the entire AI-infrastructure trade.

## The India thread that gets overlooked

Micron is run by Sanjay Mehrotra, the Kanpur-born, BITS Pilani-educated co-founder of SanDisk who has spent a career inside memory. Under him, Micron became the first major American chipmaker to commit serious manufacturing to India: a $2.75 billion assembly, test and packaging facility in Sanand, Gujarat, the anchor project of the India Semiconductor Mission.

That plant matters beyond symbolism. India's IT minister Ashwini Vaishnaw said this week he expects more memory investment to flow into the country as AI data centres widen the global demand-supply gap — with both existing players scaling up and new entrants arriving. Tata Electronics' $10.9 billion fab with Taiwan's PSMC, also in Gujarat, rounds out the picture. For a diaspora professional weighing whether to relocate to Bengaluru or Gujarat for a semiconductor role, Micron's India footprint is no longer a press-release ambition. It is a working facility with Mehrotra's name behind it.

## What to watch

Ignore the headline beat or miss on June 24; it is noise. Watch three things: the Q4 revenue guide, what management says about HBM pricing into the back half of 2027, and any hint about ramping HBM-capable capacity in India. The first tells you where the cycle is. The second tells you whether the moat holds. The third tells you whether the diaspora's bet on a "Make in India" chip industry is about to get a memory chapter — written by one of its own."""

article3_body = """India's largest IT exporter has spent the year being cast as artificial intelligence's most obvious victim. Tata Consultancy Services cut more than 12,000 jobs last July and saw headcount fall by over 23,000 on a net basis in the year to March. Its chairman now openly says the firm is moving toward a workforce with roughly equal numbers of humans and AI agents. So when TCS announced a "Global Premier Partnership" with Anthropic, the maker of the Claude models, the move read less like a press release and more like a survival strategy.

## The deal

TCS will equip 50,000 of its associates with Anthropic's Claude and jointly take AI solutions to market, with an early focus on regulated industries — banking, insurance, lending advisory — where accuracy and auditability are non-negotiable. Anthropic's chief executive Dario Amodei called India the company's "second-largest market." Tata Sons chairman N. Chandrasekaran framed it as nation-building, pledging to "equip India's youth with the skills to lead in the AI era."

The irony is hard to miss. In February, Indian IT services firms shed more than $62 billion in market value, in part after Anthropic released an AI coding agent that investors feared would gut the labour-intensive outsourcing model. Now the largest of those firms is partnering with the company that spooked the market — and rival Infosys struck a similar Anthropic deal months earlier.

## "AI deflation" is the real story

The phrase doing the rounds in Indian IT earnings calls is "AI deflation": the idea that as AI makes delivery more efficient, the per-project revenue clients are willing to pay falls. HCLTech's chief executive told investors to expect revenue to dip three to five percent. TCS saw annual revenue slip 0.5%, with its CEO calling the trend "degrowth." Across the big four — TCS, Infosys, Wipro, HCL — the old formula of adding tens of thousands of bodies each quarter has broken; combined hiring slowed to a trickle, and FY26 saw a collective net reduction of thousands of staff.

The TCS-Anthropic alliance is a bet that the way out is up the value chain: stop selling cheap labour by the hour, start selling AI-augmented transformation by the outcome. Whether clients pay enough to offset the deflation is the open question.

## Why the diaspora should read the fine print

For the Indian-American professional, this is not distant news. The big four are among the largest sponsors of H-1B and L-1 visas, and TCS, Wipro and Tech Mahindra already saw US visa approvals fall roughly 40% year-on-year in FY26 as wage-linked selection norms bit. As these firms pivot from headcount to AI agents, the nature of the US-based job changes: fewer entry-level support and testing roles shipped onshore, more demand for people who can architect, govern and sell AI deployments to American enterprises.

That is a double-edged sword for diaspora families. The cousin in Hyderabad hoping for an onsite posting on the old model will find fewer doors. But the engineer already in New Jersey or the Bay Area who can speak both "regulated enterprise" and "frontier AI" is suddenly more valuable, not less. The partnership explicitly targets exactly that skill set — Claude plus domain expertise in banking and insurance, the sectors where the diaspora is heavily represented.

## What to watch

Three signals will reveal whether this is substance or theatre. First, does TCS's revenue per employee keep climbing even as headcount stays flat — the tell that AI augmentation is actually generating premium work? Second, do the 50,000 Claude-equipped associates translate into named, large-deal wins in regulated sectors, or stay a training-slide statistic? Third, does Washington's tightening visa regime push more of this AI-transformation work onto US soil, reshaping where the diaspora's next generation of jobs actually sits?

For now, the message from Mumbai is clear. India's IT giants have stopped renting their intelligence and started buying a seat at the frontier. Whether that seat pays for itself is the trillion-rupee question."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple Just Handed Siri's Brain to Sundar Pichai's Google",
        "subheadline": "The new Siri in iOS 27 runs on Google's Gemini in a reported $1 billion-a-year deal. For the diaspora, the two biggest AI franchises in consumer tech now both run on Indian-led infrastructure.",
        "slug": make_slug("apple-siri-google-gemini-sundar-pichai-ios-27"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Apple's decision to power Siri with Sundar Pichai's Gemini cements Indian-origin leadership at the center of consumer AI and shifts Silicon Valley's hiring premium toward the integration and deployment roles heavily staffed by Indian and Indian-American engineers.",
        "tags": ["ai", "apple", "google", "sundar-pichai", "gemini", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MacRumors — Siri AI in iOS 27", "url": "https://www.macrumors.com/guide/siri-ai-ios-27/"},
            {"name": "Fox News — WWDC 2026 takeaways", "url": "https://www.foxnews.com/tech/12-biggest-apple-wwdc-2026-takeaways"},
            {"name": "9to5Mac — iOS 27 Siri extensions", "url": "https://9to5mac.com/2026/06/14/apple-still-has-three-unannounced-ios-27-features-in-the-pipeline-report/"},
            {"name": "CRN — Google I/O 2026 keynote", "url": "https://www.crn.com/news/ai/2026/google-ceo-explains-6-big-ai-and-gemini-launches-at-google-i-o-keynote"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": PICHAI_IMG,
        "image_caption": "Alphabet and Google CEO Sundar Pichai, whose Gemini models will now power Apple's new Siri",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron Reports June 24. The Quarter Is Priced In — the One After Isn't.",
        "subheadline": "With margins near 81% and HBM sold out, Sanjay Mehrotra's memory giant is worth $1.1 trillion. NRI investors should watch the Q4 guidance, not the headline beat.",
        "slug": make_slug("micron-earnings-june-24-hbm-mehrotra-gujarat-fab"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Micron is a core AI holding for many NRI investors and is run by Kanpur-born Sanjay Mehrotra, who committed the first major US chip plant to India in Gujarat — making its earnings both a portfolio bellwether and a Make-in-India semiconductor milestone.",
        "tags": ["semiconductors", "micron", "sanjay-mehrotra", "hbm", "ai-chips", "india-fab"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "MarketWatch — Micron bulls ahead of earnings", "url": "https://www.marketwatch.com/story/micron-bulls-are-getting-even-more-optimistic-about-memory-trends-as-earnings-draw-closer"},
            {"name": "AInvest — The Micron number everyone's watching", "url": "https://www.ainvest.com/news/micron-number-watching-known/"},
            {"name": "AInvest — India semiconductor investment (Vaishnaw)", "url": "https://www.ainvest.com/news/india-aims-boost-semiconductor-production-new-investments/"},
            {"name": "Seeking Alpha — Holding every Micron share", "url": "https://seekingalpha.com/article/why-im-still-holding-every-micron-share"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": MEHROTRA_IMG,
        "image_caption": "Micron Technology CEO Sanjay Mehrotra, who anchored the company's $2.75 billion chip facility in Gujarat",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "TCS Bet Against AI Was Killing It. Now It's Partnering With the Company That Started the Panic.",
        "subheadline": "Tata's IT giant will put Anthropic's Claude in the hands of 50,000 employees. It's a wager that the way past 'AI deflation' is up the value chain — and the diaspora's next jobs hang on whether it works.",
        "slug": make_slug("tcs-anthropic-claude-partnership-ai-deflation-h1b"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "As India's largest IT employer pivots from headcount to AI agents, the nature of US-based diaspora jobs is changing — fewer entry-level offshore-onsite roles, more demand for engineers who can architect and sell AI transformation to American enterprises.",
        "tags": ["ai", "tcs", "anthropic", "claude", "indian-it", "h1b", "ai-deflation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — TCS partners with Anthropic", "url": "https://www.reuters.com/technology/indias-tcs-partners-with-anthropic-drive-enterprise-ai-scaling/"},
            {"name": "India Education Diary — TCS-Anthropic partnership", "url": "https://indiaeducationdiary.in/tcs-and-anthropic-launch-global-premier-partnership/"},
            {"name": "The Register — AI deflation at India's IT giants", "url": "https://www.theregister.com/2026/ai-deflation-india-tech-services/"},
            {"name": "People Matters — H-1B approvals fall in FY26", "url": "https://www.peoplematters.in/news/tcs-wipro-tech-mahindra-h1b-approvals-fall-fy26"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": CHANDRA_IMG,
        "image_caption": "Tata Sons chairman N. Chandrasekaran, who framed the TCS-Anthropic deal as equipping India's youth for the AI era",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']} — {wc} words")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
