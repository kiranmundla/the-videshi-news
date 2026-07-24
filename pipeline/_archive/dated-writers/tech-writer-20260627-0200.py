#!/usr/bin/env python3
"""Videshi Tech Writer — 2026-06-27 02:00 PDT run"""

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

# ─────────────────────────────────────────────
# ARTICLE 1: Apple / CXMT / Memory Chip Geopolitics
# ─────────────────────────────────────────────

article1_body = """Apple has gone to the White House with a request that would have been unthinkable two years ago: permission to buy memory chips from a Chinese company the Pentagon has classified as a military-linked entity.

According to the Financial Times, Apple has been lobbying the Trump administration for clearance to purchase DRAM from ChangXin Memory Technologies, or CXMT — China's top memory chipmaker and a company on the Defence Department's list of Communist Chinese Military Companies. Apple approached the Commerce Department more than a month ago and has since engaged other administration officials and Washington allies to press the case.

The timing is not subtle. On Thursday, Apple raised prices across its iPad and MacBook lines, with Tim Cook citing soaring memory and storage chip costs that the company could no longer absorb. Cook called the memory shortage a "hundred-year flood" — the most dire language he has used about component costs in his tenure. The average MacBook Pro is now roughly $200 more expensive than it was at the start of the year.

## The AI shortage that broke the supply chain

The root cause is the AI data centre buildout. Hyperscalers — Amazon, Google, Microsoft, Meta — are consuming memory chips at historic rates to power GPU clusters for training and running large language models. Amazon alone committed $48 billion to Indian data centre expansion this week. Google's capital expenditure for 2026 is forecast at $180 billion to $190 billion, more than double last year's $91 billion. This insatiable demand has drained the global DRAM supply, leaving consumer electronics manufacturers scrambling.

Samsung, SK Hynix, and Micron Technology — the "big three" of memory — control over 95 per cent of the DRAM market. All three have prioritised high-margin, AI-grade High Bandwidth Memory (HBM) over the commodity DRAM that goes into phones and laptops, pushing prices for consumer-grade chips sharply higher.

That is where CXMT enters. The Hefei-based firm has been rapidly scaling commodity DRAM production and is reportedly approaching mass production of HBM3 chips. For Apple, the appeal is obvious: a fourth supplier would provide both pricing leverage and supply chain insurance.

## Why Indian Americans should pay attention

The story is personal for the diaspora on at least two fronts. The first is the price tag. Indian American households are disproportionately heavy Apple consumers — iPhones, MacBooks, and iPads are the default kit of the Bay Area engineer and the East Coast professional. Every price increase lands directly in the family budget, especially for those equipping children heading to college this fall.

The second front is Micron. The company's CEO, Sanjay Mehrotra — born in Kanpur, educated at UC Berkeley — has positioned Micron as the American answer to Chinese memory dominance. Micron's $2.75 billion Gujarat fabrication facility, backed by India's Semiconductor Mission, is designed to produce memory chips in India for the first time. If Apple begins sourcing from CXMT, it undercuts the market position of the very company building India's first memory fab.

The geopolitics cut even deeper. The Biden administration originally designated CXMT as a Chinese military company and moved to add it to the Commerce Department's Entity List, which would restrict its access to American technology. Apple is now asking the Trump administration to create an exception. The precedent, if set, would reshape the semiconductor supply chain in ways that India's nascent chip industry is watching closely.

## The uncomfortable arithmetic

Apple's dilemma captures a broader tension in American tech: the same AI boom that is minting fortunes in Silicon Valley is also breaking the supply chains that consumer electronics depend on. Cook has historically absorbed component cost swings rather than passing them on. That he broke that pattern this week — and is simultaneously lobbying for access to a military-blacklisted Chinese supplier — tells you how severe the squeeze has become.

For NRI investors tracking both Apple and Micron, the question is whether Washington blinks. If CXMT gets a license, it gains legitimacy as a global supplier and Micron's pricing power weakens. If Apple is denied, the price hikes are just the beginning."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Apple Is Lobbying the White House to Buy Chips From a Blacklisted Chinese Firm. The Memory Crisis Left It No Choice.",
    "subheadline": "Tim Cook's company approached the Commerce Department weeks ago, seeking clearance to buy from Chang Xin Memory Technologies. Days later, Apple raised iPad and MacBook prices and called the shortage a 'hundred-year flood.'",
    "slug": make_slug("apple-cxmt-blacklisted-chinese-memory-chip-lobbying-cook"),
    "category": "technology",
    "vertical": "semiconductor-geopolitics",
    "diaspora_angle": "Apple price hikes hit Indian American consumers directly; Micron CEO Sanjay Mehrotra's Gujarat fab is the American answer to CXMT, and Apple sourcing from the Chinese rival would undercut it.",
    "tags": ["apple", "semiconductor", "cxmt", "micron", "china", "memory-chip", "geopolitics"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/apple-seeks-approval-buy-chips-blacklisted-chinese-company-ft-reports-2026-06-27/"},
        {"name": "Financial Times", "url": "https://www.ft.com/content/apple-cxmt-memory-chips"},
        {"name": "MacRumors", "url": "https://www.macrumors.com"},
        {"name": "Wccftech", "url": "https://wccftech.com/apple-eyeing-partnership-chinese-memory-makers-ymtc-cxmt/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Closeup of electronic microchips on a circuit board",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 2: Nvidia / Jensen Huang / Zero China Revenue / Vera CPU
# ─────────────────────────────────────────────

article2_body = """Jensen Huang has always been blunt, but his message to Nvidia shareholders on June 24 contained an admission that no amount of optimism could sugarcoat: the company's AI chip market share in China has dropped to zero.

"Nvidia had 90-some-odd percent of the world's market share," Huang told investors at the annual stockholder meeting. "Today in China, we have now dropped to zero."

The collapse is the direct result of U.S. export controls that have progressively tightened since 2022, making it illegal to ship Nvidia's most advanced AI accelerators to Chinese customers. Last year, China accounted for roughly 9 per cent of Nvidia's revenue — nearly $20 billion. In the most recent quarter, that number had already halved to approximately $4.5 billion. Huang's remarks suggest it has since fallen to effectively nothing.

But the meeting was not a eulogy. It was a product launch wrapped in a shareholder address.

## The Vera CPU: replacing China with a new market entirely

Nvidia's answer to the China revenue gap is not a diplomatic workaround. It is a new chip architecture. The Vera central processing unit represents Nvidia's entry into the CPU market that Intel and AMD have dominated for decades, and management expects it to generate nearly $20 billion in revenue this year alone — almost exactly the amount China used to contribute.

The Vera Rubin computing platform, scheduled to begin shipping later this year, is designed specifically for agentic AI — the next phase of artificial intelligence where autonomous agents perform multi-step reasoning and take action without human intervention. The platform features seven purpose-built chips and promises up to 35x higher inference throughput than previous architectures. Analysts currently project Nvidia's full-year revenue will hit $391 billion, an 81 per cent increase over last year.

Huang framed the opportunity in characteristically expansive terms. He declared that AI has entered a "profitability era," citing GitHub data showing that pull requests nearly tripled this year because of AI-assisted coding. "Nvidia systems may not be the cheapest to purchase," he said, "but Nvidia generates the lowest cost tokens, the highest token throughput, and the most revenues."

## National security comes first

Huang also used the meeting to address the Supermicro smuggling case — the $2.5 billion scheme in which the company's co-founder allegedly used heat guns to swap serial numbers and staged warehouses of fake servers to route Nvidia hardware into China.

"National security comes first," Huang said flatly. He warned that anyone attempting to build AI data centres with smuggled Nvidia chips would find them useless without ongoing software updates, networking support, and system integration. "Advanced AI data centres are massive integrated systems that require trusted hardware, software, networking, and continuing support," he said. Smuggled systems, he argued, are a "dead end."

## What this means for Indian tech professionals

The implications ripple directly through the Indian diaspora. Nvidia is one of Silicon Valley's largest employers of Indian-origin engineers — from GPU architects to AI researchers to the networking teams building the connective tissue of modern data centres. The company's pivot to Vera CPUs and agentic AI infrastructure represents a massive new engineering frontier, one where Indian talent is already disproportionately represented.

The India connection runs deeper. Huang told investors that the compute needed for agentic AI has increased 1,000 per cent compared to generative AI in just two years. If that trajectory holds, the AI infrastructure buildout is still in its earliest stages. Amazon's fresh $48 billion commitment to Indian data centres, Google's $15 billion, and Microsoft's $17.5 billion all depend on Nvidia hardware. India is not just consuming this technology — it is becoming a critical node in the global compute supply chain.

For NRI investors, the takeaway is that Nvidia's China loss is already priced in — and already replaced. The stock trades at 22 times this year's earnings estimate, and Wall Street projects 45 per cent annualised earnings growth over the next several years. The question is no longer whether Nvidia survives without China, but whether the rest of the world can build fast enough to absorb what Nvidia is making."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Jensen Huang Says Nvidia's China Revenue Has Dropped to Zero. The $20 Billion Vera CPU Is His Answer.",
    "subheadline": "At his annual shareholder meeting, the Nvidia CEO declared the AI profitability era has arrived — and admitted China is lost. The Vera Rubin platform, designed for agentic AI, replaces that revenue entirely.",
    "slug": make_slug("nvidia-jensen-huang-china-zero-vera-cpu-20-billion-agentic-ai"),
    "category": "technology",
    "vertical": "ai-infrastructure",
    "diaspora_angle": "Nvidia is one of Silicon Valley's largest H-1B employers of Indian engineers; India's data centre buildout — $48B from Amazon, $15B from Google — runs on Nvidia hardware, making this a direct diaspora infrastructure story.",
    "tags": ["nvidia", "jensen-huang", "ai", "vera-cpu", "china", "semiconductor", "agentic-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/26/jensen-huang-nvidias-china-zero-20-billion-plan/"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/latest-news/nvidia-ceo-sends-serious-wake-up-call-to-all-americans"},
        {"name": "CNBC", "url": "https://www.cnbc.com/2026/06/24/nvidia-shareholder-meeting.html"},
        {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/nvidia-nvda-shareholder-analyst-call-slideshow-2026-06-25"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Nvidia CEO Jensen Huang at a 2025 event",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}

# ─────────────────────────────────────────────
# ARTICLE 3: India AI Funding / Sovereign AI / VC Ecosystem
# ─────────────────────────────────────────────

article3_body = """For years, the polite consensus on India and artificial intelligence was that the country would be a consumer, not a builder. That consensus is quietly breaking down.

In the past three months, three Indian AI companies have closed funding rounds that collectively exceed $1 billion. Neysa, an AI acceleration cloud provider, raised $600 million from Blackstone, Teachers' Venture Growth, and Nexus Venture Partners. Sarvam, the Bengaluru-based foundational model company, raised $234 million at a $1.5 billion valuation, with HCLTech investing $150 million as lead strategic partner. Uniphore, a conversational AI firm, raised $250 million at a $2.25 billion valuation late last year. These are no longer seed-stage experiments. They are infrastructure bets.

The shift has been accelerated by a geopolitical event that most Indians did not expect to affect them directly. Earlier this month, the U.S. government ordered Anthropic to disable access to Fable 5 and Mythos 5, its most advanced AI models. The restriction, framed as a national security measure, sparked a furious debate in India about the risks of depending on American-built AI for critical applications — from banking to government services to defence.

## The sovereign AI thesis

Subrata Mitra, founding partner of Accel's India arm, offered a more nuanced reading in an interview with Mint this week. "I wouldn't put a country winner on the AI problem," he said. "Winning is company-specific. It is very specific problem statements that people are trying to solve for."

Accel is deploying capital across AI, consumer tech, fintech, and manufacturing from its $650 million eighth India fund, launched in January 2025. Mitra's argument — that India does not need to compete with OpenAI or DeepSeek on foundation models but can build globally significant AI companies by solving sector-specific problems — is gaining traction among investors who have watched India's digital public infrastructure transform payments and identity verification at national scale.

The numbers support the thesis. Indian deeptech startups have raised $1.23 billion so far in 2026, according to Tracxn data, already approaching last year's full-year total of $1.5 billion. The flow is not limited to AI models. Neysa's $600 million raise targets AI cloud infrastructure — the GPU clusters and data centres that companies need to train and run models without depending on foreign hyperscalers. Sarvam's models are designed specifically for Indian languages and deployed across banking, insurance, and government services.

## Building versus buying

The distinction between building AI capabilities and buying them matters more than most Indian professionals realise. When Anthropic's most powerful models were restricted this month, every Indian company running production workloads on Fable 5 faced an overnight reclassification of its AI stack from asset to liability.

The sovereign AI push is India's hedge against that risk. The government's IndiaAI Mission has already signalled it may take equity stakes in domestic AI companies — a striking departure from India's traditionally arms-length approach to industrial policy. HCLTech's $150 million investment in Sarvam is not philanthropy; it is a bet that enterprise customers, particularly government agencies and defence contractors, will increasingly demand AI models that cannot be switched off by a foreign executive order.

## What this means for NRI investors and professionals

For the diaspora, the India AI story presents a rare alignment of professional expertise and investment opportunity. Indian-origin engineers dominate the AI research teams at Google DeepMind, OpenAI, Anthropic, and Meta — and a growing number are starting to redirect that expertise toward Indian companies. The talent pipeline that once flowed exclusively from IIT to Silicon Valley is developing a branch that runs through Bengaluru.

The investment arithmetic is also shifting. India minted five unicorns in the first half of 2026 — Juspay, KreditBee, Skyroot Aerospace, Sarvam, and Square Yards — a pace that would produce eight to ten for the year, ahead of 2025's tally. The AI names on that list, unlike the consumer internet unicorns of the 2021 boom, are building durable infrastructure rather than chasing user acquisition metrics.

The question for NRI investors is no longer whether India can produce AI companies. It is whether those companies can sustain margins and market position when the hyperscalers — Amazon, Google, Microsoft — are pouring tens of billions into Indian data centres of their own. The answer will depend on whether sovereign AI is a lasting competitive advantage or a temporary policy preference. Either way, the cheques being written today are large enough to reshape the answer."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "India's AI Startups Just Raised Over $1 Billion in Back-to-Back Rounds. The Bet Is Sovereignty.",
    "subheadline": "Neysa, Sarvam, and Uniphore have collectively raised over $1 billion. After the U.S. restricted Anthropic's most advanced models, the case for Indian-built AI infrastructure is no longer theoretical.",
    "slug": make_slug("india-ai-startups-billion-dollar-rounds-sovereign-neysa-sarvam"),
    "category": "technology",
    "vertical": "indian-tech-ecosystem",
    "diaspora_angle": "NRI investors and engineers are watching India's AI ecosystem mature from services to infrastructure; the sovereign AI push triggered by Anthropic's Fable 5 restriction affects every Indian company running U.S.-built models.",
    "tags": ["india-ai", "sovereign-ai", "sarvam", "neysa", "accel", "deeptech", "venture-capital"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "LiveMint", "url": "https://www.livemint.com/companies/ai-companies-india-accel-india-subrata-mitra-openai-anthropic-ai-deeptech-11782363361891.html"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/16/sarvam-ai-unicorn-234-million-hcltech/"},
        {"name": "Inc42", "url": "https://inc42.com/infocus/indian-unicorn-tracker/"},
        {"name": "Tracxn", "url": "https://tracxn.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Server racks inside a modern data centre facility",
    "image_attribution": "Pexels",
    "body": article3_body.strip()
}

# ─────────────────────────────────────────────
# INSERT ALL ARTICLES
# ─────────────────────────────────────────────

articles = [article1, article2, article3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
