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
        "headline": "DeepSeek Just Made Its 75 Per Cent Price Cut Permanent. Indian AI Startups Should Pay Attention.",
        "subheadline": "The Chinese AI lab's flagship model now costs a tenth of OpenAI's equivalent — and the pricing floor it sets will reshape how Indian developers build.",
        "slug": make_slug("deepseek-v4-pro-75-percent-price-cut-indian-ai-startups"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian AI startups and developers building on cloud APIs — from Bengaluru to the Bay Area — now face a radically different cost structure. For NRI founders bootstrapping AI products, DeepSeek's pricing makes frontier-class inference accessible at a fraction of what it cost six months ago. The implications ripple through the Indian startup ecosystem, where capital efficiency is existential.",
        "tags": ["deepseek", "ai-pricing", "indian-startups", "openai", "api", "ai-infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "SendTech Times", "url": "https://stechtimes.com/en/article/deepseek-slashes-v4pro-api-pricing-by-75-as-outside-fundraising-nears-mptcrb50"},
            {"name": "VentureBeat", "url": "https://venturebeat.com/ai/deepseeks-new-v3-2-exp-model-cuts-api-pricing-in-half/"},
            {"name": "Medium / Aiexpo", "url": "https://medium.com/@aiexpo/deepseek-just-made-its-75-price-cut-permanent"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """DeepSeek, the Chinese AI lab that rattled Silicon Valley earlier this year with an open-weight model that matched GPT-4 at a fraction of the training cost, has taken another swing at the industry's pricing consensus. On May 22, the company announced that its temporary promotional rate for the DeepSeek-V4-Pro API would become permanent. The cache-miss input price is now 3 yuan per million tokens — roughly $0.44. That is less than one-tenth of what OpenAI charges for GPT-5.5, and well below Kimi, DeepSeek's closest Chinese rival, at $0.95.

The numbers are stark enough on their own. But the timing makes them more interesting.

## The Model Behind the Price Tag

V4-Pro is DeepSeek's flagship: a 1.6 trillion-parameter open-weight model that the company describes as the world's largest in its class. On VALS AI, a third-party benchmark aggregator, V4-Pro ranks ninth globally with an average accuracy score of 63.87 per cent — respectable but not dominant. The model sits behind Anthropic's Claude Opus 4 and OpenAI's GPT-5.5 on most reasoning tasks, but ahead of dozens of competitors that charge significantly more.

On OpenRouter, a popular API aggregation platform, DeepSeek's market share climbed to 23.1 per cent. Its lighter sibling, V4-Flash, ranked first on the platform with 3.43 trillion tokens consumed — a volume figure that suggests developers are not merely testing DeepSeek but building on it.

## Why Indian Developers Should Care

For AI startups in India and the diaspora, the pricing shift is not abstract. Indian AI companies raised approximately $1.5 billion in 2025, according to Inc42, with the majority flowing into application-layer businesses rather than foundational model development. These are companies that buy inference by the token. A permanent 75 per cent reduction in a frontier-class API changes their unit economics overnight.

Consider a Bengaluru startup building an AI-powered customer service agent for Indian banks. At OpenAI's current GPT-5.5 pricing of roughly $5 per million input tokens, scaling to a million daily conversations gets expensive fast. At DeepSeek's $0.44, the same workload costs a small fraction — freeing capital for distribution, hiring, or the next product iteration.

The catch, of course, is trust. DeepSeek is a Chinese company, and its models have been restricted by government agencies in the United States, India, Italy, Canada, Australia, and Taiwan. NASA, the Pentagon, and India's CERT-In have all implemented internal bans. For Indian startups serving enterprise clients in the US — a large share of India's SaaS and AI services exports — routing production traffic through DeepSeek carries regulatory and reputational risk that no pricing advantage can fully offset.

## The Broader Price War

DeepSeek's move does not happen in isolation. OpenAI's GPT-5 Nano is priced at $0.05 per million input tokens — cheaper still, albeit for a much smaller model. Google's Gemini 2.5 Flash-Lite sits at $0.10. Anthropic's Claude Haiku 3.5, the budget option in its lineup, costs $0.80. The inference price floor is collapsing across the board, and the primary beneficiaries are the builders who consume these APIs.

For NRI founders and Indian tech workers at companies like Google, Microsoft, and Meta — many of whom are building AI-powered tools on the side or evaluating startup ideas — the calculus has shifted. The cost of experimenting with frontier AI is approaching zero. The cost of ignoring it is not.

## What Comes Next

DeepSeek is also raising its first round of external financing at a reported $44 billion valuation. Making flagship pricing permanent while courting outside capital is a deliberate signal: the company is prioritising developer adoption over short-term revenue maximisation, betting that scale will justify the valuation.

For Indian AI entrepreneurs, the message is simpler. The tools are cheaper than ever. The question is no longer whether you can afford to build with frontier AI. It is whether you can afford not to."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Meta Is Building an AI Pendant That Records Your Life. It Also Wants to Sell 10 Million Wearables This Year.",
        "subheadline": "A leaked internal memo reveals Meta's plan to turn AI-powered glasses and a Limitless-derived pendant into a subscription business — while Reality Labs bleeds $4 billion a quarter.",
        "slug": make_slug("meta-ai-pendant-wearables-10-million-target-reality-labs"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Meta employs tens of thousands of Indian engineers and H-1B workers across its AI, hardware, and infrastructure teams. As Reality Labs pivots from metaverse to AI wearables, the strategic shift determines which teams grow and which face cuts — directly affecting Indian professionals who make up a significant share of Meta's technical workforce in the Bay Area and Seattle.",
        "tags": ["meta", "ai-wearables", "smart-glasses", "mark-zuckerberg", "reality-labs", "h1b"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Hypebeast", "url": "https://hypebeast.com/2026/5/meta-ai-pendant-and-supersensing-glasses-roadmap-leaks"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/01/meta-is-reportedly-developing-an-ai-pendant/"},
            {"name": "The Information (via Storyboard18)", "url": "https://storyboard18.com/technology/after-smart-glasses-meta-is-reportedly-working-on-an-ai-pendant-75348.htm"},
            {"name": "LinkedIn / Engadget analysis", "url": "https://www.linkedin.com/pulse/apple-takes-aim-meta-smart-glasses-its-own/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/F20250904AH-2824_%2854778373111%29_%283x4_cropped_on_Zuckerberg_following_the_rule_of_thirds%29.jpg",
        "body": """Mark Zuckerberg has spent $83 billion on Reality Labs since late 2020 and has a $4 billion quarterly loss to show for it. His answer, according to an internal memo leaked to The Information last week, is not to retreat from hardware but to push deeper — with an AI-powered pendant, an expanded smart glasses lineup, and an enterprise subscription service designed to turn all of it into recurring revenue.

The memo, authored by Alex Himel, Meta's Vice President of Wearables, lays out an ambitious roadmap. The centrepiece is a pendant-style device derived from Limitless, the AI wearables startup Meta acquired in late 2025. Limitless built a clip-on Bluetooth recorder that listened to conversations, generated transcripts, and created a searchable database of a user's day. Meta's version will expand on that concept, positioning the pendant as a personal AI assistant that summarises daily interactions.

Internal testing — Meta calls it dogfooding — is scheduled for spring 2027. Production timelines remain unclear.

## Four New Smart Glasses Before December

The pendant is only one piece. Himel's memo outlines four new smart glasses models launching before year-end. The first, codenamed Modelo, arrives in June. Two more — Luna and RBM2 Refresh — follow in autumn. A fourth, Mojito VIP, ships in December. Beyond these, Meta is developing what it calls supersensing models: glasses with cameras and sensors that remain active for extended periods, allowing the AI to track a user's environment continuously. The idea is that the glasses could remember where you left your keys or suggest tasks based on what they observe.

Meta's current glasses are made through partnerships with EssilorLuxottica, the parent company of Ray-Ban and Oakley. The roadmap suggests bringing additional eyewear brands into the fold to widen the audience and improve gross margins.

## The Subscription Bet

What makes this hardware push different from Meta's earlier metaverse ambitions is the explicit focus on software revenue. Himel's memo introduces Wearables for Work, a subscription-based enterprise service targeting corporate customers willing to pay a premium for industry-specific AI features. The logic is straightforward: hardware margins are thin and getting thinner, but a subscription attached to each device compounds over time.

Himel set an internal target of 10 million wearable devices sold in the second half of 2026 and 6.8 million monthly active users by year-end. If every one of those users subscribed to Meta AI at $8 a month — a best-case scenario — the annual software revenue would be roughly $653 million. That covers about 3.4 per cent of Reality Labs' annual operating loss.

The maths, in other words, does not yet work. But Meta is betting that the installed base needs to reach critical mass before the software economics kick in.

## What This Means for Indian Engineers at Meta

Meta's hardware pivot carries direct implications for the thousands of Indian-origin engineers who work across its AI, infrastructure, and product teams. Just last week, Meta filed WARN Act notices for 3,270 positions in the Bay Area, many of which affect H-1B visa holders who face a 60-day window to find new sponsorship.

The wearables push, however, creates countervailing demand. Building AI agents that run on constrained hardware — glasses with limited battery and compute, pendants with always-on microphones — requires deep expertise in on-device inference, model compression, and sensor fusion. These are specialities where Indian engineers at Meta have historically been well-represented.

The question for Indian professionals inside the company is which side of the rebalancing they land on. Meta is simultaneously cutting roles in areas it considers mature while hiring aggressively for AI hardware and wearable software. For H-1B workers, whose ability to switch teams depends on internal mobility and immigration constraints, the uncertainty is acute.

## The Competitive Landscape

Meta is not alone in the AI wearables race. Apple is reportedly developing its own smart glasses. OpenAI has invested in hardware concepts. Lenskart, the Indian eyewear company, launched India's first AI smart glasses last week to a waitlist of 35,000.

But Meta has something its competitors do not: distribution at scale. With 3 billion monthly active users across its apps, the ability to push AI wearables through Instagram and WhatsApp marketing is a structural advantage. Whether that translates into 10 million devices sold remains the open question."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India and the US Just Signed a Semiconductor Pact. The Real Story Is What Gets Built Next.",
        "subheadline": "The PAX Silica Declaration and TRUST Initiative have moved from diplomatic communiqués to industrial execution — with American chip companies, Indian fabs, and critical mineral deals at the centre.",
        "slug": make_slug("india-us-semiconductor-pact-pax-silica-trust-chip-partnership"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "For the estimated 300,000 Indian-origin semiconductor professionals working across the US chip industry — at Intel, Qualcomm, NVIDIA, Texas Instruments, Broadcom, and dozens of design firms — the India-US chip partnership creates a two-way corridor. It opens career paths back to India without abandoning the US ecosystem, and it positions Indian professionals as connective tissue between the two nations' semiconductor ambitions.",
        "tags": ["india-us", "semiconductors", "pax-silica", "trust-initiative", "chip-manufacturing", "critical-minerals", "nri"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "IANS", "url": "https://ianslive.in/india-us-tech-partnership-in-semiconductors-ai-enters-industrial-phase--20260601133903"},
            {"name": "Analytics Insight", "url": "https://www.analyticsinsight.net/semiconductor/semiconductor-dreams-can-india-build-a-chip-industry-from-scratch"},
            {"name": "Communications Today", "url": "https://communicationstoday.co.in/indias-chip-designers-are-finally-building-for-themselves/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169775/pexels-photo-36169775.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For years, the India-US semiconductor relationship was a story told in design centres and PowerPoint decks. Indian engineers designed chips in Bengaluru, Hyderabad, and Noida for companies headquartered in Santa Clara and San Jose. The chips themselves were manufactured in Taiwan, South Korea, or the American Southwest. India contributed talent. It did not contribute silicon.

That narrative is changing — and the speed of the change over the past six months deserves closer attention than it has received.

## From Dialogue to Execution

During US Secretary of State Marco Rubio's visit to India in recent weeks, the two countries formalised a series of agreements that move the semiconductor partnership from strategic aspiration to industrial execution. The anchoring frameworks are the TRUST Initiative — Transforming the Relationship Utilizing Strategic Technologies, first outlined by Prime Minister Modi and President Trump in February 2025 — and the PAX Silica Declaration, a US-led coalition aimed at building secure supply chains for AI chips, semiconductors, and critical minerals.

India's accession to PAX Silica places it in a select group of nations the US considers trusted partners for semiconductor supply chain diversification. The practical effect is that American chip companies can now engage with Indian entities on terms that include shared design validation, workforce training, and potentially access to controlled technology that would otherwise face export restrictions.

## What Is Actually Being Built

The partnership is producing tangible projects. The Shakti Semiconductor Fab is developing compound semiconductors for electric vehicles and aerospace — a niche that sidesteps the cutting-edge logic fabrication dominated by TSMC and Samsung, but addresses a real and growing market. US companies General Atomics and Synopsys are partnering with 3rdiTech, an Indian semiconductor startup, to validate chip designs and train engineering teams.

Separately, the India Semiconductor Mission's second phase — ISM 2.0, announced in the Union Budget for 2026-27 — allocates Rs 8,000 crore specifically for manufacturing and design support. The ambition, according to government officials, is for India to design and manufacture chips for 70 to 75 per cent of its own needs by 2029, spanning consumer electronics to defence systems.

At least half a dozen Indian chip startups have now completed tape-outs — the critical milestone where a finalised design is sent to a fabrication facility. C2i Semiconductors, founded by Texas Instruments veterans, taped out a power management chip for AI data centres last week. Mindgrove Technologies and Agnit Semiconductors are expected to move into production before year-end. These are not paper companies. They are domain specialists who spent careers at Intel, AMD, and TI before returning to India to build.

## The Critical Minerals Angle

Perhaps the most consequential element of the recent agreements is the cooperation on critical minerals and rare earths — the raw materials without which no chip gets made. China controls roughly 60 per cent of global rare earth mining and 90 per cent of processing. The India-US pact opens the door for joint financing and investment in alternative mining and processing ventures.

Rubio was blunt about the rationale: "Vibrant innovation economies such as ours cannot afford to leave the foundational materials of these industries vulnerable to single-source monopolies." For India, which has significant rare earth deposits in Rajasthan, Kerala, and Odisha, the agreement provides both capital and diplomatic cover to develop them.

## The Diaspora Corridor

For Indian-origin semiconductor professionals in the United States — and there are an estimated 300,000 of them across design, verification, process engineering, and management — the bilateral partnership creates something that did not previously exist at scale: a professional corridor.

An Indian engineer at Qualcomm in San Diego can now contemplate a move to India's semiconductor ecosystem without feeling like they are stepping off a cliff. The companies being built in India are staffed by people from their professional networks, working on problems they understand, with access to validation partnerships with the same American firms they currently work for. The return-to-India calculation, for this specific cohort, has never looked more rational.

The partnership is jointly steered by the National Security Advisors of both countries — a signal that this is not a trade agreement dressed up as technology cooperation, but a strategic alignment with security at its core. For Indian Americans working in the chip industry, that dual framing is both an opportunity and a constraint. The work is important. The stakes are real. And the window, for once, is open."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
