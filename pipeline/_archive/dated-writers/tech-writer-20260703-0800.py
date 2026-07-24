#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-03 08:00 PT"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────
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

def verify_image(url):
    """Return True if url returns HTTP 200 with image/* content and >5KB."""
    if not url:
        return False
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, stream=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        # For streaming, read first 6000 bytes if CL is 0
        if cl == 0:
            data = r.raw.read(6000)
            cl = len(data)
        return r.status_code == 200 and "image" in ct and cl > 5000
    except Exception:
        return False

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-20260703"


# ── Image sourcing ────────────────────────────────────────────────

# Article 1: Tim Cook at European Commission (perfect match for EU article)
img1_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Visit_of_Tim_Cook_to_the_European_Commission_-_P061904-946789.jpg/1280px-Visit_of_Tim_Cook_to_the_European_Commission_-_P061904-946789.jpg"
img1_caption = "Apple CEO Tim Cook at the European Commission headquarters in Brussels"
img1_attr = "Wikimedia Commons"
if not verify_image(img1_url):
    # Fallback to Wikipedia portrait
    img1_url = "https://upload.wikimedia.org/wikipedia/commons/f/f7/Tim_Cook_March_2026_%28cropped_2%29.jpg"
    img1_caption = "Apple CEO Tim Cook"
    if not verify_image(img1_url):
        img1_url = None
        print("⚠️ No image for Article 1")

# Article 2: Data center server room (chip selloff / AI compute story)
img2_url = "https://images.pexels.com/photos/5203849/pexels-photo-5203849.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
img2_caption = "Server racks inside a data center powering AI workloads"
img2_attr = "Pexels"
if not verify_image(img2_url):
    img2_url = None
    print("⚠️ No image for Article 2")

# Article 3: Infosys campus glass pyramid (IT sector story)
img3_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg/1280px-Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg"
img3_caption = "The glass pyramid at Infosys' Electronic City campus in Bengaluru"
img3_attr = "Wikimedia Commons"
if not verify_image(img3_url):
    img3_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/InfosysBanglore.jpg/1280px-InfosysBanglore.jpg"
    img3_caption = "The Infosys campus in Bengaluru, one of India's largest IT employers"
    img3_attr = "Wikimedia Commons"
    if not verify_image(img3_url):
        img3_url = None
        print("⚠️ No image for Article 3")

print(f"Image 1: {img1_url}")
print(f"Image 2: {img2_url}")
print(f"Image 3: {img3_url}")


# ── Articles ──────────────────────────────────────────────────────

articles = [

    # ━━━ ARTICLE 1: Apple Siri AI / Gemini / EU ━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "Apple's New Siri Runs on Google's Brain. In Europe, It Runs on Nothing.",
        "subheadline": "Tim Cook held 'constructive' talks with EU regulators this week as Apple's Gemini-powered Siri AI remains blocked across the bloc — a standoff that could reshape AI regulation globally.",
        "slug": make_slug("apple-siri-ai-gemini-eu-cook-brussels"),
        "category": "technology",
        "vertical": "ai-regulation",
        "diaspora_angle": "Thousands of Indian engineers at Apple and Google built the Siri AI features now blocked in Europe, while the EU precedent could influence India's own draft AI governance framework.",
        "tags": ["apple", "google", "gemini", "siri-ai", "eu-dma", "ai-regulation", "tim-cook", "sundar-pichai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-eu-siri-ai-cook-virkkunen-2026-07-02/"},
            {"name": "9to5Mac", "url": "https://9to5mac.com/2026/07/02/tim-cook-eu-siri-ai-meeting/"},
            {"name": "MacRumors", "url": "https://www.macrumors.com/2026/07/01/tim-cook-constructive-eu-siri-ai/"},
            {"name": "Financial Times", "url": "https://www.ft.com/content/apple-siri-eu-cook-talks"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img1_url,
        "image_caption": img1_caption,
        "image_attribution": img1_attr,
        "body": """Apple's new Siri AI, the most significant overhaul of its voice assistant in over a decade, will launch this September powered by an unlikely engine: Google's Gemini large language models, running on Nvidia's Blackwell server chips. But for 450 million iPhone users in the European Union, it will not launch at all.

On Tuesday, Apple CEO Tim Cook held a virtual meeting with EU tech chief Henna Virkkunen to discuss a path forward. An EU spokesperson described the call as "a constructive exchange on topics of common interest, on which the work continues." It was the most conciliatory signal yet in a dispute that has turned genuinely nasty.

## The Architecture of Dependence

The Siri AI Apple unveiled at its Worldwide Developers Conference last month represents a fundamental architectural shift. On-device processing handles basic queries using Apple's own models, but anything requiring deeper reasoning or multi-turn conversation gets routed to Google's Gemini models running on Nvidia Blackwell-powered servers in Google Cloud.

The irony is not subtle. Apple, which spent years positioning itself as a privacy-first alternative to Google's data-hungry empire, is now relying on its oldest rival to power its most personal product. Craig Federighi, Apple's software engineering chief, defended the choice by launching a standalone Siri app — a chatbot interface the company had previously dismissed as contrary to its strategy.

Analyst Ming-Chi Kuo argues the real question from WWDC is whether Apple can deliver better AI experiences than Google using the same underlying Gemini models. If it cannot, Apple's AI ambitions have a ceiling set by Sundar Pichai's company.

## The DMA Wall

The problem is the Digital Markets Act, the EU's sweeping competition rules for Big Tech. The DMA requires Apple to give third-party AI assistants — Google's own Gemini, Samsung's Bixby, and others — the same deep access to iPhone capabilities that Siri enjoys: reading messages, controlling apps, accessing files.

Apple proposed a compromise called the "Trusted System Agent," intermediary software that would let competitors tap into iPhone features securely. Apple wanted an 18-month transition period during which Siri AI would launch while the interoperability framework was built. The Commission rejected both the concept and the timeline.

The public sparring that followed was uncommonly blunt. Apple blamed regulators for "failing to acknowledge" security risks. Commission spokesperson Thomas Regnier fired back: "The decision not to roll out Siri AI in the EU is Apple's and Apple's only, because absolutely nothing in the DMA prohibits Apple from introducing new products."

A Commission official told the Financial Times that Apple "focused on obtaining a green light to delay compliance" rather than building a workable solution. The official added that Apple's proposal "would have risked leading to the entrenchment of its service before others would get a chance to compete for at least two years."

## Why the Diaspora Should Pay Attention

The standoff matters well beyond Brussels. India is developing its own draft AI governance framework, and the EU–Apple dispute is creating the first real-world template for how sovereign regulators can constrain AI distribution by platform gatekeepers.

For thousands of Indian engineers at Apple's campuses in Cupertino, Hyderabad, and Bengaluru — many of whom built the very features now frozen — the delay is professionally frustrating. And the deeper story is structural: Sundar Pichai's Google is powering Tim Cook's flagship product, a partnership that would have seemed implausible five years ago. The two companies, both led by executives who grew up in India, are now intertwined in ways that reshape both their competitive positions.

For NRI investors holding Apple stock, the calculus is straightforward. Europe accounted for 27% of Apple's total sales last fiscal year. Every quarter of delay in Siri AI's EU launch is a quarter where Apple's strongest product upgrade cannot drive device sales in its second-largest market. Apple has not publicly commented on the latest discussions, and no timeline has been set for a European launch."""
    },

    # ━━━ ARTICLE 2: Meta Cloud Compute / Chip Selloff ━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Wants to Sell Its Spare AI Compute. It Just Spooked the Entire Chip Sector.",
        "subheadline": "A report that Meta plans to become a cloud computing provider sent semiconductor stocks tumbling — SK Hynix fell 15%, CoreWeave lost $7.5 billion — while SoftBank announced its own AI cloud venture the very next day.",
        "slug": make_slug("meta-cloud-excess-compute-chip-selloff-overcapacity"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "NRI investors are heavily exposed to the semiconductor boom — Micron gained 240% last quarter alone — and the overcapacity fears directly affect India's own chip buildout plans in Gujarat and Dholera.",
        "tags": ["meta", "semiconductors", "ai-compute", "sk-hynix", "coreweave", "nvidia", "softbank", "chip-selloff"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-building-cloud-business-sell-excess-ai-capacity-2026-07-01/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/finance/stocks/whats-weighing-on-chip-stocks-2026-07-02"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/coreweave-stock-meta-cloud-ai-computing-2026-07-03"},
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/ai-infra-chip-stocks-fall-meta-cloud-business"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img2_url,
        "image_caption": img2_caption,
        "image_attribution": img2_attr,
        "body": """For the past two years, the biggest question in technology has been whether anyone was spending enough on artificial intelligence. On Tuesday, the market briefly considered the opposite possibility — and panicked.

Bloomberg News reported that Meta Platforms is building a cloud business to sell its excess AI computing power to outside customers, including Anthropic. Meta stock surged nearly 11% on the news, its best day since April 2025. Everything else in the AI supply chain fell hard.

## The Damage

SK Hynix, the South Korean memory chip maker that had tripled in value this year on booming AI demand, dropped 15% in a single session. Samsung fell 9%. CoreWeave, the neocloud company that rents GPU capacity to enterprises, lost 14% — wiping out $7.5 billion in market value in one day. Even Nvidia, the undisputed king of AI chips, slid 1.7%, dragging the PHLX Semiconductor Index down 4.7%.

The logic was simple and brutal: if Meta has so much AI computing power that it can sell the surplus, perhaps the industry has overbuilt. Every company that manufactures, sells, or resells AI chips took the hit.

## SoftBank Piles On

The timing was exquisite. Just one day after the Meta report, Japan's SoftBank announced it would launch its own U.S. neocloud business, tentatively called SB Neo, to sell AI computing power to hyperscalers and enterprises. SB Neo plans to scale to a staggering 10 gigawatts of AI infrastructure capacity — a figure that would dwarf most existing operations.

SoftBank's Japanese telecom unit separately announced an AI Data Center GPU Cloud offering built on Nvidia GB200 NVL72 systems, launching in October.

The combined announcements raised an uncomfortable question: are we entering an era where there are more sellers of AI compute than buyers?

## Zuckerberg Had Warned

This was not entirely a surprise. At Meta's annual shareholder meeting in May, Mark Zuckerberg acknowledged that companies were approaching Meta "almost every week" to buy its compute capacity. "We haven't done that yet because we think that we have a use for the compute," he said. "But obviously if we get to a point where we feel that we have overbuilt, then that is an option."

That option, it appears, is now being exercised. Meta is projected to spend as much as $145 billion on AI infrastructure this year. Total Big Tech AI spending exceeds $700 billion. The company is also reportedly considering selling raw computing capacity like neoclouds do — directly competing with CoreWeave and Nebius, both of which count Meta as a customer.

Michael Burry, the investor whose successful bet against the housing market in 2008 was immortalised in "The Big Short," weighed in via his subscriber-only Substack. After SK Hynix announced its $64 billion NAND flash investment, Burry called the semiconductor spending surge "the beginning of the end," and disclosed bearish bets against AI-related stocks.

## The Bull Case

Not everyone agrees. Rosenblatt Securities called the CoreWeave selloff "a buying opportunity," noting that GPU shortages remain "the norm right now across the industry." Their analysts wrote that more investment in the AI ecosystem "reinforces what we're seeing every day: a rapidly expanding market, not a zero-sum game." CoreWeave itself issued a statement emphasising "incredibly strong demand across a growing and increasingly diverse customer base."

D.A. Davidson analyst Gil Luria offered a more nuanced take: "The impact of adding Meta's capacity to the market is more likely to be on neoclouds than the big hyperscalers." In other words, Meta entering the market could crush smaller GPU rental businesses without meaningfully affecting AWS or Azure.

## The India Angle

Indian diaspora investors have been among the biggest beneficiaries of the semiconductor boom. Sanjay Mehrotra's Micron alone added 240% in market value last quarter, and AI chip stocks have been a favourite among NRI portfolios on both U.S. and Indian exchanges. The chip selloff directly threatens those gains.

For India's own semiconductor ambitions — Tata Electronics' fab in Dholera, Micron's packaging plant in Gujarat — the implications are more complex. If global AI chip demand genuinely cools, the case for India's $10 billion semiconductor buildout weakens at the margins. But if the overcapacity fear is overdone, as the bulls argue, India's timing could prove fortunate: building supply infrastructure just as the next wave of enterprise AI adoption begins.

The answer likely depends on a question nobody can settle yet: how much AI compute the world actually needs."""
    },

    # ━━━ ARTICLE 3: Indian IT Sector Q1 Preview ━━━
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Sector Has Lost a Third of Its Value This Year. The Next Two Weeks Will Tell If It's Over.",
        "subheadline": "TCS reports July 9, Infosys follows, and the Nifty IT sits at a five-year low. With AI eating into margins and global tech budgets frozen, India's $250 billion software industry faces its hardest reckoning since the dot-com bust.",
        "slug": make_slug("indian-it-nifty-33-crash-q1-tcs-infosys-preview"),
        "category": "technology",
        "vertical": "indian-it",
        "diaspora_angle": "NRI investors hold significant positions in Indian IT stocks, and millions of Indian tech workers depend on the health of TCS, Infosys, and HCLTech — making the Q1 results deeply personal for the diaspora.",
        "tags": ["indian-it", "tcs", "infosys", "hcltech", "wipro", "nifty-it", "ai-disruption", "nri-investors"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/markets/ai-fears-cheap-valuations-weak-earnings-indian-it-stocks"},
            {"name": "Communications Today", "url": "https://www.communicationstoday.co.in/india-it-firms-likely-to-post-muted-june-quarter-results/"},
            {"name": "Ainvest", "url": "https://www.ainvest.com/news/indias-nifty-it-index-falls/"},
            {"name": "DQ India", "url": "https://www.dqindia.com/news/top-indian-it-firms-net-loss-3000-employees-q3-fy26/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": img3_url,
        "image_caption": img3_caption,
        "image_attribution": img3_attr,
        "body": """The Nifty IT index has now fallen more than 33% from its February peak, making it one of the worst-performing segments of the Indian market in 2026. This week, it hit a five-year low before a sharp one-day bounce of 4.6% on bargain buying. That bounce did not last. On Tuesday, the index slipped another 1.1%, extending a pattern that has wiped out years of gains and left investors wondering whether the correction has found its floor.

The answer arrives starting next week. Tata Consultancy Services reports its June quarter results on July 9, followed by Infosys, HCL Technologies, Wipro, and Tech Mahindra in the days after. Together, these companies employ over 1.5 million people — roughly the population of Philadelphia — and their quarterly numbers will either confirm or challenge the market's darkest fears about AI-driven disruption.

## What the Numbers Are Expected to Show

The previews are not encouraging. Brokerage Emkay Global expects TCS to deliver just 0.2% sequential growth in dollar revenue, with margins declining 90 basis points to 26.5% as annual wage hikes take effect. Revenue is estimated at ₹72,392 crore for the quarter, up 14.1% year-on-year but barely moving quarter-on-quarter.

Infosys is expected to be the brightest spot among tier-one peers, with 2.1% sequential dollar revenue growth — though nearly half of that is attributable to two recent acquisitions, Stratus and Optimum, rather than organic wins. Revenue is forecast at ₹48,791 crore. Emkay expects Infosys to raise its FY27 constant currency revenue growth guidance from 1.5–3.5% to 2–4%.

HCL Technologies may report a 1% sequential revenue decline, dragged by productivity pass-throughs and weakness in two large client accounts. The silver lining: margins could expand 60 basis points as restructuring costs normalise.

## The AI Fear Premium

The selloff is about more than one soft quarter. The market is pricing in a structural question: can Indian IT services companies protect their business models in a world where AI can do an increasing share of what their engineers do?

The fear is not abstract. JP Morgan recently argued that AI is creating "deflationary pressure" across the Indian IT sector. Concentrix, a major BPO company, lost a quarter of its value in a single week after reporting results that suggested AI was cannibalising traditional call centre work. Oracle cut 21,000 jobs globally last year, nearly half of them in India.

The aggregate workforce numbers tell a quiet but relentless story. Across TCS, Infosys, Wipro, HCL Technologies, Tech Mahindra, and LTTS, the industry shed nearly 3,000 employees net in a single recent quarter. TCS alone cut over 11,000 positions, though Infosys and Wipro added headcount in their own restructuring cycles.

Global spending on discretionary technology projects — the bread and butter of India's IT giants — has been frozen by high interest rates, persistent inflation, and geopolitical uncertainty in the US and Europe. These two regions account for roughly 70% of India's IT revenue. Any shift in their procurement cycles has an immediate ripple effect on hiring in Bengaluru, Hyderabad, and Pune.

## The Countervailing Signals

It is not all decline. HCLTech this week won a $1.14 billion AI deal in Europe, suggesting that companies that can retool as AI integrators rather than body shops still have a path to growth. Persistent Systems bid $1.4 billion for Germany's Nagarro, signalling that consolidation and geographical expansion remain viable strategies.

Palantir CEO Alex Karp's characterisation of OpenAI's model as a "wealth tax" — essentially arguing that enterprise AI is too expensive to displace traditional IT at scale — sent Indian IT stocks rallying briefly. The comment pointed to a fundamental question the market has not resolved: is AI a near-term threat to IT services margins, or is the disruption five to ten years away?

## What NRI Investors Should Watch

For the millions of NRI investors who hold TCS, Infosys, and HCLTech in their portfolios, the Q1 earnings season is the most consequential in years. The numbers matter, but the commentary matters more. Pay attention to three signals: whether management teams raise or lower full-year revenue guidance, how they quantify AI-related deal wins versus traditional services, and whether hiring plans suggest confidence or continued contraction.

At current valuations, Indian IT stocks are trading near historic lows on a price-to-earnings basis. If Q1 results come in roughly as expected and management commentary hints at a spending recovery in the second half, the sector could snap back sharply — it remains deeply under-owned by institutional investors. But if the results disappoint, or if guidance drops, the correction has room to deepen. The next two weeks will not settle the AI question for good. But they will tell investors whether the market has been right to panic."""
    },
]


# ── Insert ────────────────────────────────────────────────────────

for art in articles:
    if not art.get("image_url"):
        print(f"⚠️ Skipping {art['slug']} — no image")
        continue
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
