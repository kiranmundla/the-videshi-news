#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-08 03:00 UTC run."""

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
    # ── Article 1: Jensen Huang's South Korea Tour / NVIDIA-SK Hynix ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Is in Seoul Eating Fried Chicken. He Left With a Memory Empire.",
        "subheadline": "NVIDIA and SK Hynix just signed a multiyear deal to co-develop next-generation memory for AI data centres. The memory shortage, Huang says, will last 'quite a few years.'",
        "slug": make_slug("nvidia-sk-hynix-jensen-huang-seoul-memory-ai-factories"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian semiconductor engineers at Micron's Gujarat facility and Samsung's India R&D centre are directly affected by how the global HBM supply chain shakes out. Sanjay Mehrotra's Micron is both a competitor and a supplier in this memory arms race.",
        "tags": ["nvidia", "sk-hynix", "jensen-huang", "memory-chips", "ai-infrastructure", "semiconductors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidia-announces-deals-with-south-koreas-sk-hynix-naver-doosan-ai-data-centres-2026-06-08/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/nvidia-strikes-a-new-memory-chip-deal-but-sk-hynix-and-samsung-shares-are-under-heavy-pressure/"},
            {"name": "NVIDIA GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/06/07/nvidia-sk-hynix-multiyear-partnership.html"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "NVIDIA CEO Jensen Huang at a 2025 keynote event",
        "image_attribution": "Wikimedia Commons",
        "body": """Jensen Huang arrived in Seoul on Friday with the swagger of a head of state and the appetite of a tourist. Over the weekend he threw a first pitch at a Korean baseball game, met a famous gamer on camera, and sat down with SK Group chairman Chey Tae-won over fried chicken and beer — a Korean ritual known as *chimaek*. Then, on Monday morning, he signed the deal that actually mattered.

NVIDIA and SK Hynix announced a multiyear technology partnership to co-develop next-generation memory for what Huang now calls "AI factories" — the specialised data centres that train and run the world's largest AI models. The deal covers memory for NVIDIA's upcoming Vera Rubin AI supercomputers, Vera CPUs, RTX Spark PCs, and Jetson Thor robotics platforms. SK Hynix will also use NVIDIA's Omniverse and cuOpt platforms to build digital twins of its own semiconductor fabs.

"AI factories are the engines of the next industrial revolution, and advanced memory is essential to their performance," Huang said in a statement. "SK Hynix has been an extraordinary partner to NVIDIA."

## The Shortage That Won't Quit

The partnership announcement landed against a grim backdrop for memory supply. Huang told reporters in Seoul that the global shortage of memory chips, wafers, packaging capacity, and silicon photonics would persist for "quite a few years." The demand from AI data centres has simply outpaced the industry's ability to manufacture high-bandwidth memory (HBM) — the specialised DRAM that sits on top of AI processors and feeds them data at extraordinary speeds.

SK Hynix and Samsung, the world's two largest memory chipmakers, have been running at full capacity to meet HBM orders. Yet every new generation of NVIDIA GPUs demands more memory per chip, and the global build-out of AI data centres shows no sign of slowing. Hyperscalers are collectively spending over $820 billion on AI infrastructure in 2026 alone.

## Caught in the Crossfire: Asian Markets

Ironically, the partnership announcement did nothing to arrest a brutal sell-off in Korean chip stocks. SK Hynix opened 10.3% lower on Monday; Samsung fell 10.9%. The Kospi index, which had rallied 94% in 2026 on the back of the AI memory boom, dropped 6.1% in early trading as Friday's $1.3 trillion semiconductor rout on Wall Street rippled through Asian markets.

"When the market's hottest AI playground suddenly turns into a fire drill, traders tend to notice," said Stephen Innes, managing partner at SPI Asset Management.

## What It Means for Indian Tech

The NVIDIA-SK Hynix axis has direct implications for India's semiconductor ambitions. Sanjay Mehrotra's Micron Technology — SK Hynix's primary global competitor in HBM — is building a $2.75 billion assembly and test facility in Gujarat. The plant, part of India's Semiconductor Mission, will package memory chips destined for AI data centres. How Micron positions itself against the deepening NVIDIA-SK Hynix alliance will shape whether India becomes a meaningful node in the AI memory supply chain or remains on its periphery.

For Indian engineers in the semiconductor industry — and there are tens of thousands of them across Samsung's R&D centres in Bangalore and Noida, Micron's design teams in Hyderabad, and SK Hynix's growing India hiring — the stakes are personal. The memory shortage means job security and rising compensation in the near term. But the tightening partnership between NVIDIA and SK Hynix also concentrates power in ways that could marginalise smaller players and the ecosystems that depend on them.

The fried chicken, it seems, was just the appetiser."""
    },

    # ── Article 2: Intel's CPU Revival ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Every CEO Is Calling Lip-Bu Tan for More Chips. Intel's Comeback Is Real.",
        "subheadline": "Agentic AI is driving a spike in CPU demand, and Intel — left for dead in the GPU wars — is suddenly the company everyone needs. Its stock is up 120% this year.",
        "slug": make_slug("intel-lip-bu-tan-cpu-agentic-ai-comeback-stock-surge"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Intel employs over 10,000 engineers in India and is one of the largest H-1B sponsors in the US. After years of layoff anxiety, the CPU demand surge is the best news Indian Intel employees have had in a decade.",
        "tags": ["intel", "lip-bu-tan", "cpu", "agentic-ai", "semiconductors", "h-1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/07/tech/intel-agentic-ai-cpu-revival/"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/intel-cfo-ai-boom-set-to-drive-significant-growth-in-global-cpu-demand/"},
            {"name": "Webull", "url": "https://www.webull.com.my/news/ceo-lip-bu-tan-fantastic-news-intel-shareholders"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/10/Howard_Lutnick_with_Intel_CEO_Lip-Bu_Tan_%282025%29_%28cropped3%29.jpg",
        "image_caption": "Intel CEO Lip-Bu Tan at a 2025 event in Washington",
        "image_attribution": "Wikimedia Commons",
        "body": """For three years, Intel was the semiconductor industry's cautionary tale — the once-dominant chipmaker that missed the AI boom, bled market share to NVIDIA, and watched its stock crater by two-thirds. Its former CEO was ousted. Its fabs were underutilised. Wall Street whispered about break-ups and fire sales.

Then Lip-Bu Tan arrived, and the phone started ringing.

"Almost every CEO calls me up and says, 'Lip-Bu, can I have more?'" Tan told investors at Computex last week. He wasn't talking about GPUs. He was talking about CPUs — the traditional server processors that Intel has been making for decades, and that the AI industry has suddenly realised it cannot live without.

## The Agentic Twist

The shift is structural, not cyclical. The first wave of AI — training massive models — was all about GPUs. NVIDIA owned that market. But the second wave, now arriving, is about deploying those models as autonomous agents that execute tasks, search databases, manage workflows, and coordinate multi-step operations in real time. This is called agentic AI, and it is deeply CPU-intensive.

"The CPU is now the conductor, and the GPU is the orchestra," Jensen Huang said at his own Computex keynote — an acknowledgement, from NVIDIA's own CEO, that Intel's core product has become essential to the AI stack.

Intel CFO David Zinsner confirmed the trend at a Bank of America conference: the CPU-to-GPU ratio in data centres is increasing. CPUs are needed for orchestrating tasks, managing data pipelines, and supporting real-time operations. And Intel, despite everything, still commands the overwhelming majority of the server CPU market.

## The Numbers

Intel's stock has surged more than 120% in 2026. Its 18A manufacturing process — the critical node that will determine whether Intel can compete as a contract chipmaker — is ramping at the fastest pace in five years. The company plans to raise server CPU prices by 10% for Chinese customers, a move it can make only because demand exceeds supply.

Tan, who spent 13 years as CEO of chip design powerhouse Cadence before taking over Intel, has moved quickly to cut costs, shed non-core businesses, and refocus the company on engineering execution. His mantra: "First-time pass" quality, no exceptions.

## Why Indian Engineers Should Care

Intel's Bangalore campus is the company's largest design centre outside the United States. More than 10,000 Indian engineers work on everything from Xeon server chips to process node development. Intel is also one of the largest H-1B sponsors among chip companies, with thousands of Indian-origin employees in its Oregon, Arizona, and California facilities.

For these engineers, the past three years were nerve-shredding. Intel laid off more than 15,000 workers in 2024. Morale cratered. Many shifted to NVIDIA, AMD, or the cloud hyperscalers.

Now the calculus is reversing. CPU demand is surging, headcount is stabilising, and stock options that looked worthless a year ago are suddenly worth something again. Intel isn't out of the woods — NVIDIA just launched its own Vera CPU for data centres, and AMD's EPYC processors continue to gain share. But for the first time in years, staying at Intel doesn't feel like a losing bet.

Lip-Bu Tan doesn't make promises. He ships product. And right now, that's exactly what every CEO in America is asking him to do."""
    },

    # ── Article 3: Sundar Pichai's $80B Raise ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai Just Raised $80 Billion. Warren Buffett Wrote the Biggest Check.",
        "subheadline": "Alphabet's record-breaking equity offering — backed by a $10 billion Berkshire Hathaway bet — will fund the largest AI infrastructure build-out in corporate history. Google Cloud hit $20 billion in quarterly revenue for the first time.",
        "slug": make_slug("sundar-pichai-alphabet-80-billion-berkshire-ai-infrastructure"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Pichai's Alphabet is the single largest employer of Indian-origin engineers in Silicon Valley. The $190 billion capex plan means thousands of new roles in AI infrastructure — and for NRI investors, a signal that the IIT-Madras graduate is betting the company on AI.",
        "tags": ["sundar-pichai", "alphabet", "google", "berkshire-hathaway", "ai-infrastructure", "capex"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/article/still-bullish-on-alphabet-stock-after-85b-capital-raise"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/first-google-now-meta-big-tech-may-increasingly-sell-stock-to-bankroll-820-billion-ai-boom/"},
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/06/berkshire-hathaway-bets-big-on-alphabet/"},
            {"name": "Insider Monkey", "url": "https://www.insidermonkey.com/blog/is-alphabet-inc-the-best-goldman-sachs-tech-stock-to-buy-now/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet CEO Sundar Pichai at a public event in 2023",
        "image_attribution": "Wikimedia Commons",
        "body": """When Alphabet announced an $80 billion equity offering on June 2, it set three records simultaneously: the largest equity raise in US corporate history, the largest single bet on AI infrastructure by any company, and the most expensive vote of confidence a Chennai-born engineer has ever received from Warren Buffett.

Berkshire Hathaway's $10 billion private placement — split evenly between Class A common stock at $351.81 and Class C capital stock at $348.20, both below market price — was the centrepiece. Greg Abel, Buffett's successor as CEO, had already been building a position: Berkshire bought nearly $17 billion worth of Alphabet shares over the prior three quarters. The new infusion makes Alphabet Berkshire's fourth-largest equity holding.

The message from Omaha is unambiguous: the AI infrastructure build-out is as durable an investment as railroads, utilities, and energy grids were in prior decades. And Sundar Pichai's Alphabet is the safest way to ride it.

## Where the Money Goes

Alphabet plans to spend between $180 billion and $190 billion in capital expenditures in 2026, with plans to raise that figure further in 2027. The money flows into data centres, custom TPU chips, fibre-optic networks, and the physical infrastructure required to run AI models at global scale.

The numbers behind the spend are staggering. Google Cloud hit $20 billion in quarterly revenue for the first time in Q1 2026, growing 63% year over year. Cloud backlog has doubled to over $460 billion. Gemini, Google's flagship AI model family, saw 40% quarter-over-quarter growth in paid monthly active users. Advertising revenue — still the majority of Alphabet's business — climbed 19% to $77.25 billion.

In other words, Pichai isn't raising capital because Alphabet is struggling. He's raising it because demand for AI compute is growing faster than even Alphabet's prodigious cash flows can fund.

## The Dilution Question

Alphabet is engineering the raise to minimise shareholder pain. The $80 billion breaks into three tranches: a $30 billion underwritten offering ($15 billion in common stock, $15 billion in convertible preferred), a $40 billion at-the-market programme that will drip-feed shares from Q3 onwards, and Berkshire's $10 billion private placement. The total represents less than 2% of Alphabet's roughly $4.2 trillion market capitalisation.

Alphabet stock dipped about 3% in the week following the announcement — a remarkably muted reaction for an offering of this scale. Meta is reportedly considering a similar move, signalling that Big Tech has entered a new era where even the world's most profitable companies must tap equity markets to finance AI ambitions.

## The Indian Diaspora Calculation

For Indian-origin professionals, Pichai's bet has layered implications. Alphabet is the single largest employer of Indian-origin engineers in Silicon Valley. Its India operations in Bangalore, Hyderabad, and Gurgaon employ tens of thousands more. A $190 billion capex programme means years of hiring ahead — cloud architects, chip designers, data centre engineers, and AI researchers.

For NRI investors, the calculus is more nuanced. Alphabet remains one of the most widely held US stocks in Indian brokerage accounts, and the dilution from an $80 billion raise is real, if modest. But Berkshire's endorsement at a discount — from an institution that has historically avoided technology bets — is a powerful signal. When the stewards of American value investing decide that Sundar Pichai's AI infrastructure build is worth a $10 billion check, it is worth paying attention.

The boy from Madurai who grew up without a computer in his house is now directing the largest corporate capital expenditure programme in history. That, more than any quarterly earnings beat, is the story."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
