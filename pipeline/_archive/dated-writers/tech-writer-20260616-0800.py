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
        "headline": "Wipro Just Opened a Claude Lab in Bengaluru. The Company AI Was Supposed to Gut Is Now Its Best Customer.",
        "subheadline": "India's third-largest IT firm will train 10,000 engineers on Anthropic's models — a tacit admission that the only way to survive AI deflation is to sell it.",
        "slug": make_slug("wipro-anthropic-claude-coe-bengaluru-ai-deflation-it-jobs"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Hundreds of thousands of Indian engineers — at Wipro's Bengaluru towers and on H-1B desks in New Jersey and the Bay Area — are watching their employers race to befriend the same AI that analysts say is eating their jobs.",
        "tags": ["ai", "indian-it", "wipro", "anthropic", "h1b", "jobs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-wipro-opens-ai-center-anthropics-claude-bengaluru-2026-06-16/"},
            {"name": "Reuters — HCLTech / Sarvam AI", "url": "https://www.reuters.com/world/india/indias-hcltech-buy-105-stake-sarvam-ai-valuing-startup-15-billion-2026-06-15/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/29505140/pexels-photo-29505140.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An engineer works across multiple code screens at a software development desk",
        "image_attribution": "Pexels",
        "body": """India's IT industry spent the early part of this year watching its own obituary being written. When Anthropic released an AI agent tool in February, investors did the math on what a machine that writes and reviews code means for a $315 billion sector built on renting out human coders by the thousand. Indian IT stocks shed billions in market value in a single stretch.

On Tuesday, Wipro gave its answer: if you can't beat the model, build a temple to it. The Bengaluru-based firm announced a Center of Excellence for applied AI built specifically around Anthropic's Claude models, and said it will train 10,000 of its own employees to use Claude over the next 18 months.

## From threat to product line

The logic is the same one Nikesh Arora has been preaching at Palo Alto Networks all year — that frontier AI, rather than killing the incumbents, scares enterprises into spending more. Wipro is betting the same dynamic rescues IT services. The pitch to clients is no longer "we have 5,000 engineers who can build your software." It is "we have a Claude Center of Excellence that can rebuild your software, redesign your workflows, and retrain your staff."

The center is aimed at helping Wipro develop AI platforms and industry-specific tools, and at threading Claude through its own finance, HR, and sales functions first. That last part matters. A services company that cannot run its own back office on AI has no credibility selling AI transformation to a bank in Frankfurt or an insurer in Hartford.

Wipro is not alone, and it is not even first. On June 11, larger rival TCS announced an alliance with Anthropic to drive enterprise AI scaling. A day before Wipro's move, HCLTech took a 10.5% stake in Indian AI startup Sarvam, valuing it at $1.5 billion — buying a seat at the model-building table rather than just licensing someone else's. The pattern across the top tier is unmistakable: the IT giants have stopped treating AI as weather to be survived and started treating it as inventory to be sold.

## The catch analysts keep flagging

Jefferies analysts noted the uncomfortable part out loud. Wipro itself expects compression in services revenue to weigh on growth in the coming quarters. AI may widen the total addressable market through application rebuilds and workflow redesign — but the old model, billing for armies of people doing repetitive work, is the very thing under pressure. You cannot train 10,000 engineers on Claude and simultaneously promise investors that headcount-linked revenue is safe.

That tension is the whole story for the diaspora.

## Why an NRI engineer should read past the headline

For the tens of thousands of Indian professionals who power these firms — in Bengaluru and Pune, and on client sites across New Jersey, Texas, and the Bay Area on H-1B and L-1 visas — "Center of Excellence" is a phrase to parse carefully. In the best reading, it is a genuine escalator: engineers who become Claude-fluent become more valuable, harder to automate, and more mobile across the global job market. The skills are portable in a way a visa is not.

In the worse reading, "train 10,000 to use AI" is the polite preamble to "need fewer people to do the same work." Indian IT has run that play before, quietly rebadging roles and trimming benches while the official line stayed upbeat. A US-based H-1B worker has a sharper stake than a Bengaluru colleague: a role made redundant is not just a job lost but a 60-day clock to find a new sponsor or leave the country.

The honest verdict is that this is both an opportunity and a warning. The engineers who treat Claude fluency as the new baseline — the way cloud certification became table stakes a decade ago — will be fine, probably better than fine. The ones who assume the CoE is someone else's problem are the ones the next restructuring will find first. Wipro just told its workforce which way the wind is blowing. The smart move is to read it as a memo, not a press release."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chip Startups Found Money This Year. Now They Want Something Harder: Customers and the Right to Stay Indian.",
        "subheadline": "Funding quadrupled in five months, but founders heading to a Nice deep-tech stage warn that without domestic buyers and IP protection, the next round will be raised — and owned — abroad.",
        "slug": make_slug("india-semiconductor-startups-funding-ip-protection-foreign-ownership"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "NRI investors and returning chip engineers keep hearing that India's semiconductor story is finally real — but the founders living it say the ownership of that story is still up for grabs, and diaspora capital could decide whose flag flies over it.",
        "tags": ["semiconductors", "india-chips", "deep-tech", "startups", "ism", "investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts / Economic Times", "url": "https://inshorts.com/en/news/chip-startups-seek-better-market-access--ip-protection--report-1781347630716"},
            {"name": "Indian Infrastructure", "url": "https://indianinfrastructure.com/2026/06/02/indian-semiconductor-startups-raise-92-million-in-first-five-months-of-2026/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31665489/pexels-photo-31665489.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a semiconductor wafer showing densely patterned microchips",
        "image_attribution": "Pexels",
        "body": """The numbers look like a breakout. Indian semiconductor startups raised $92 million across 12 deals in the first five months of 2026 — nearly four times the total for all of 2025, when six deals scraped together $25 million. Companies like Constelli, C2i Semiconductors, HrdWyr, and VerveSemi each pulled in more than $10 million. At least six startups have reached tape-out, the moment a design is finalized and shipped to a foundry to be physically made. This week, three of them — VerveSemi, AGNIT Semiconductors, and Netrasemi — are representing India on a deep-tech stage at Bharat Innovates in Nice.

So why are the founders sounding less like a victory lap and more like a warning?

## The two things money can't buy yet

Speaking to The Economic Times, chip founders said the funding is welcome but exposes two gaps that capital alone won't close: market access and intellectual-property protection. The first is the harder one. A chip designed in Bengaluru still needs someone to buy it, and India's electronics manufacturers have a long habit of reaching for established foreign parts over an unproven domestic one. Development costs for a single design can run to ₹70 crore — roughly $7.5 million — and you cannot amortize that without volume orders.

The IP worry cuts deeper into national pride. Founders cautioned that limited domestic funding could push them toward foreign investors, and that taking that money tends to dilute Indian ownership of both the company and the patents it generates. The government's Design-Linked Incentive scheme and the broader India Semiconductor Mission have done a real job de-risking the earliest stage — about two dozen companies are now approved, and Mission 2.0 is shifting focus from fabrication to chip design and equipment. But incentives that get a company to tape-out don't guarantee the cap table stays in Indian hands by Series B.

## A different kind of chip story

This is not the Micron-in-Gujarat or Tata-in-Dholera headline, the multibillion-dollar fab that makes for good ribbon-cuttings. This is the design layer — the fabless startups carving out narrow, defensible niches in AI inference chips and power management for data centers, leaning on engineers who came home from Intel, AMD, and Texas Instruments. It is lower-profile and, arguably, more strategically valuable. Fabs can be bought; design talent and owned IP are what actually determine whether India captures the margin or just the assembly fee.

## Where the diaspora comes in

For NRI investors, this is the part worth slowing down on. The conventional wisdom — that you can't get exposure to India's chip ambition without buying Tata or Micron stock — is becoming outdated. A genuine venture layer now exists, with companies at tape-out and entering production later this year. But the founders' own warning is also an investment thesis in disguise: the capital that fills the domestic gap gets to keep the ownership Indian. Diaspora money, with its patience and its India ties, is precisely the kind that could fund the next round without forcing a founder to choose between growth and sovereignty.

That cuts both ways. Returning Indian-American engineers — the cohort that built credibility at Western chip giants — are exactly who these startups want, and exactly who can command real equity in a way a US megacap will never offer. For an Indian semiconductor veteran in Austin or San Jose weighing a move home, the calculus has shifted from "is the ecosystem real" to "do I want a salary at Nvidia or a founding stake in the company that becomes India's first chip champion."

The risk is just as concrete. Market access is not solved, IP rules are still being argued over, and a single missed product cycle can end a fabless startup that has already spent ₹70 crore proving its design works. This is venture-stage exposure with venture-stage mortality.

What changed in 2026 is that the question is no longer whether India can design chips. Six tape-outs and a Nice showcase settle that. The open question is who will own them when they finally sell — and that answer is still being written, one funding round at a time."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An Indian Startup Says It Can Make AI Video in Four Steps Instead of Fifty. It's Giving the Model Away.",
        "subheadline": "Avataar.ai's Varya, backed by the India AI Mission, claims a tenfold speed jump over global rivals — and will release as an open-weight model, betting that cheap and free beats Hollywood-grade and locked.",
        "slug": make_slug("avataar-ai-varya-india-video-ai-model-open-weight"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRI creators, founders, and small businesses, a free Indian video model that runs cheap could undercut the per-clip subscription costs of Western tools — and quietly tilt who gets to make slick content from a laptop in Edison or Wembley.",
        "tags": ["ai", "india-ai", "generative-video", "open-source", "startups"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/avataar-ai-unveils-varya-india-indigenous-video-ai-model-nationwide-accessibility-2606/"},
            {"name": "Inc42 — Indian startup funding", "url": "https://inc42.com/buzz/from-gps-renewables-to-equal-ai-indian-startups-raised-243-mn-this-week/"}
        ]),
        "score_total": 71,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Rows of servers in a data center, the kind of GPU infrastructure that powers AI video generation",
        "image_attribution": "Pexels",
        "body": """The global race in AI video has so far been a contest of spectacle: who can make the most cinematic eight seconds, render the most convincing water, fool the most eyes. Avataar.ai, an Indian startup, has decided to compete on a different axis entirely — speed and price — and then do the thing the leaders won't: give the model away.

Its new model, Varya, generates video in four steps instead of the roughly 50 that comparable systems require. The company claims that translates to a tenfold efficiency gain over leading models such as Wan 2.2, producing content significantly faster and at lower cost. Varya will be released as an open-weight model on India's AI Kosh portal, meaning developers can download it, self-host it, and modify it for their own needs rather than paying per generation through a locked API.

## Why "four steps" is the whole pitch

Most diffusion-based video models work by starting with noise and refining it over many passes; each pass costs compute, and compute costs money and time. Cutting 50 steps to four is not a cosmetic tweak — it is the difference between a clip that takes a minute and a few cents to make and one that takes ten and a few dollars. For e-commerce listings, classroom material, or social content produced at scale, that ratio is the entire business case. Avataar is explicitly aiming Varya at exactly those volume use cases — e-commerce and education — rather than at filmmakers chasing the next viral demo.

The startup is one of 12 selected under the India AI Mission, the government program that hands out subsidized GPU compute in exchange for public access to the resulting models. That is the quiet engine behind the "open-weight" decision: the public funding comes with a public-good string attached. Avataar also plans to explore tie-ins with video tools like Higgsfield and Adobe Firefly, suggesting it sees Varya as plumbing other products can build on, not just a consumer app.

## The sovereign-AI logic underneath

Varya lands in the same week that India's bigger sovereign-AI bet, Sarvam, became a unicorn on a $234 million round, and the same month the India AI Mission has been seeding language and now video models built for local conditions and local languages. The thesis tying them together: India does not want to rent its core AI capabilities from Silicon Valley any more than it wants to import all its chips. A homegrown, open, cheap-to-run video model is a small piece of that — but an unusually accessible one, because anyone can download it.

## What it means for the diaspora

For Indian-American creators and small-business owners, the appeal is blunt: cost. The Western video tools that dominate today charge subscription and per-clip fees that add up fast for anyone producing content regularly — a Diwali promo for a restaurant in Edison, course videos for a tutoring side hustle in Wembley, product clips for a Shopify store run out of a spare bedroom. An open-weight model that runs cheaply, even on rented cloud GPUs, changes who can afford to make polished video at all.

There is a serious catch, and it deserves equal billing. "Open-weight" and "fast" are not the same as "good," and Avataar's tenfold-efficiency and quality claims are the company's own, not yet independently benchmarked. A model optimized for speed and low cost may show its seams against the premium tools on anything demanding. The honest read for a diaspora creator is to treat Varya as a high-upside experiment, not a verified replacement — worth testing the moment it hits AI Kosh, worth nothing until the output holds up on your own screen.

The deeper signal, though, is structural. The interesting Indian AI story of mid-2026 is not a single model beating a Western benchmark. It is the steady accumulation of open, locally funded, cheap-to-run pieces — language models, Earth-observation models, and now video — each chipping at the assumption that serious AI must be expensive and American. For a diaspora that straddles both economies, that is a shift worth watching, and increasingly, one worth downloading."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
