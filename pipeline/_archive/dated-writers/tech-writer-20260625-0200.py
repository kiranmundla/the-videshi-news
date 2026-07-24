#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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
        "headline": "Amazon Just Added $13 Billion to Its India Bet. The Money Is Going Where the H-1B Jobs Used to Go.",
        "subheadline": "A fresh AWS commitment pushes Amazon's India spend toward $75 billion by 2030 — and it lands as the company builds the AI and cloud capacity at home that once required sending engineers abroad.",
        "slug": make_slug("amazon-13-billion-india-aws-ai-cloud-investment-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For Indian engineers weighing a US move against staying put, Amazon is quietly answering the question: the best-paid cloud and AI work is increasingly being built inside India, not just in Seattle.",
        "tags": ["amazon", "aws", "india", "ai", "cloud", "indian-tech", "jobs"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/amazon-invest-additional-13-billion-india-2026-06-25/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/"},
            {"name": "TradingView News", "url": "https://www.tradingview.com/news/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A data center server hall of the kind Amazon Web Services is scaling across Telangana and Maharashtra",
        "image_attribution": "Pexels",
        "body": """Amazon said on Thursday it will pour an additional $13 billion into India by 2030, on top of an already announced $35 billion, to expand the artificial-intelligence and cloud infrastructure underpinning Amazon Web Services. The fresh outlay takes the company's cumulative India commitment toward $75 billion by the end of the decade — one of the largest single-country bets any American technology firm has made outside its home market.

The headline number is easy to gloss over. What it actually buys is more interesting: construction of data centers, server computers, and the high-speed networking that AI workloads devour, concentrated in Telangana and Maharashtra where AWS already runs facilities in Hyderabad and Mumbai. Amazon framed the money around three pillars — AI-driven digitisation, export growth, and job creation — and said it intends to create roughly a million additional job opportunities and bring AI tools to 15 million small businesses by 2030.

## Why the location matters

For two decades, the standard career path for an ambitious Indian software engineer ran through an H-1B visa and a desk in California, Texas, or New Jersey. The work that paid the most — frontier cloud architecture, large-scale machine learning, the systems that hyperscalers guard most closely — lived in America. That logic is now bending.

When Amazon, Microsoft (which recently committed $17.5 billion, its largest Asia investment), and Google build their most advanced compute inside India, the gravitational pull shifts. The engineer who once had to emigrate to touch a state-of-the-art GPU cluster can increasingly do it from Bengaluru or Hyderabad, on a local salary that, adjusted for cost of living, no longer looks like a consolation prize. This is the structural backdrop to a year in which the top four H-1B sponsors are, for the first time, all US firms hiring locally rather than Indian IT outsourcers shipping bodies across the Pacific.

## What it means for the diaspora

For NRIs in the Bay Area or London, the read is double-edged. Indian Americans who have spent careers building these cloud platforms are now watching their employers replicate that capability at home — a hedge against US immigration tightening, but also a quiet redistribution of where the next decade of hiring happens. The grace-period anxiety that follows every Meta or Amazon layoff in the US has a flip side: there is now a credible, well-capitalized landing pad in India for the same skills.

For the investor class among the diaspora, the signal is about India's compute economy reaching escape velocity. India's data-center pipeline has swelled to a reported 8.33 gigawatts — more than five times current live capacity — and the cloud market is growing more than 20% a year. Amazon's check is a vote that the demand is real, not speculative. The companies supplying power, cooling, land, and networking into that build-out are the picks-and-shovels play, and several are headed for public markets.

There is a catch worth naming. Big Tech's India investments are heavily weighted toward infrastructure and small-business tooling — agentic seller assistants, generative listing tools, AI literacy for government-school students — rather than the kind of deep research roles that define Silicon Valley careers. A data center employs fewer engineers per dollar than a product org. The million jobs Amazon cites are spread across logistics, operations, and a long tail of small businesses, not a million senior machine-learning posts.

## The bigger pattern

Amazon's announcement came within hours of Microsoft's, and follows Google and others pledging billions into the same market. Read together, they describe a single trend: the world's largest technology companies have decided India is not merely a labor pool to be tapped through visas, but a market and a compute base to be built out on the ground.

That is a more durable form of investment than the body-shopping model that defined the 1990s and 2000s — and a more complicated one for the diaspora to navigate. The American dream that pulled a generation of Indian engineers west is not dead, but it now has a serious competitor being built, brick by brick and rack by rack, back home."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sundar Pichai's Gemini Can Now Run Your Browser, Phone, and Desktop. The Race Just Moved From Chatbots to Agents.",
        "subheadline": "Google opened up Gemini 3.5 Flash to build custom agents that take actions across platforms — the clearest sign yet that the AI fight has shifted from answering questions to doing the work.",
        "slug": make_slug("google-gemini-3-5-flash-agents-pichai-cross-platform-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers building on AI — at Google, at Indian startups, or on the side — now have a cheaper agent platform to ship on, but also a sharper reason to worry about which of their own tasks the agents automate first.",
        "tags": ["google", "gemini", "sundar-pichai", "ai-agents", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Seeking Alpha", "url": "https://seekingalpha.com/news/google-gemini-3-5-flash-agents"},
            {"name": "PR Newswire (Nokia / Google Cloud)", "url": "https://www.prnewswire.com/"},
            {"name": "LinkedIn — The June 2026 Model Avalanche", "url": "https://www.linkedin.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
        "image_caption": "Alphabet and Google CEO Sundar Pichai",
        "image_attribution": "Wikimedia Commons",
        "body": """Google has upgraded Gemini 3.5 Flash so that developers can build custom agents capable of taking actions across browser, mobile, and desktop environments, the company said. It is a small-sounding feature with a large implication: the contest among AI labs is no longer about who writes the best paragraph, but about who can reliably get software to *do things* — click, type, navigate, and finish a task — without a human in the loop.

Gemini 3.5 Flash, the cheaper and faster sibling to the still-in-preview Pro model, was released only weeks ago. Turning it into an agent platform, rather than a conversational model, is Sundar Pichai's answer to a market that has grown impatient with chatbots. The same week, Google Cloud said it would embed six specialized Gemini agents into Nokia's network software to help telecom operators move toward self-driving operations — a real, enterprise-grade deployment of exactly this idea.

## From a model avalanche to an agent war

June 2026 has been a blur of releases — Google positioning Gemini 3.5 Pro for imminent launch, OpenAI's GPT-5.6 in tester evaluation, and Anthropic's abrupt suspension of its Claude Fable 5 model. Analysts have started calling it the end of single-model dependence: enterprises now spread bets across providers to hedge against delays and regulatory shocks. The differentiator in that crowded field is no longer raw intelligence but agency — can the model act?

Google's pitch with the Flash upgrade is that agents are now cheap enough to deploy at scale. A model that can drive a browser or operate a phone, billed at Flash prices rather than frontier prices, changes the math for anyone building automation on top of it.

## Why Indian engineers should read this twice

The diaspora angle cuts both ways. On the upside, Indian developers — whether inside Google's own ranks, at India's sovereign-AI startups like Sarvam, or moonlighting on a side project — get a low-cost, action-capable platform to build real products on. India has one of the largest developer populations in the world, and agent tooling that is genuinely affordable lowers the barrier to shipping something that competes globally.

On the downside, agents that can operate a browser, a phone, and a desktop are, in plain terms, software that does the repetitive digital labor that a great deal of the Indian IT services industry still sells by the hour. The same week Google shipped this, Indian outsourcers were telling shareholders that AI would reshape their workforces. An agent that can navigate an enterprise application and resolve a ticket is competing directly with the offshore support seat. For the Indian-American engineer managing those teams, or the relative back home whose job is exactly that kind of process work, the technology is not abstract.

## The Pichai throughline

Pichai has spent the past year insisting Google's enormous AI investment will pay off in products people actually use, against skepticism that the company moved too slowly after ChatGPT. Embedding agents into Gemini Flash, and landing deployments like the Nokia deal, is the evidence he needs: not a flashy demo, but AI quietly wired into the plumbing of other companies' operations.

For the diaspora that has watched an Indian-born engineer run one of the world's most valuable companies, there is a familiar tension here. The technology that vaults Indian leadership to the top of global tech is the same technology reshaping — and in places shrinking — the Indian tech-services workforce that produced that leadership in the first place. Both things are true at once, and this week's quiet feature release is a marker of how fast the second half of that story is arriving."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Giants Used to Run on H-1B Visas. New Data Shows They've Quietly Stopped Needing Them.",
        "subheadline": "H-1B approvals for the top seven Indian IT firms fell 37% in a year and 70% from a decade ago, as localization, automation, and AI rewrite the offshore business model that built the industry.",
        "slug": make_slug("indian-it-h1b-approvals-collapse-localization-ai-tcs-infosys-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The visa pipeline that brought a generation of Indian engineers to America is narrowing not just because of Washington, but because the IT industry itself no longer needs it — a structural shift every NRI with family in the sector should understand.",
        "tags": ["h1b", "indian-it", "tcs", "infosys", "automation", "ai", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The American Bazaar", "url": "https://www.americanbazaaronline.com/"},
            {"name": "NASSCOM Community", "url": "https://community.nasscom.in/"},
            {"name": "National Foundation for American Policy", "url": "https://nfap.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Software engineers at work in a technology services office",
        "image_attribution": "Pexels",
        "body": """For thirty years, the deal was simple: India's IT services giants won contracts in America, then flew in armies of engineers on H-1B visas to deliver them. That model is unwinding — and the most striking part is how little of the unwinding is about immigration policy.

New analysis of USCIS data by the National Foundation for American Policy, the most rigorous independent research on the program, shows the top seven India-based IT firms received 4,573 initial-employment H-1B approvals in FY2025. That is a 37% drop from the prior year and a 70% collapse from FY2015. For the first time, the four largest H-1B employers in the country were all American companies — Amazon, Meta, Microsoft, and Google. Amazon alone secured more initial approvals than the top seven Indian IT companies combined.

## Not just Washington

It is tempting to pin this entirely on the Trump administration's $100,000 H-1B application fee and the new weighted-selection rule that favors higher-paid workers, both of which genuinely raise the cost of sponsoring a visa. But NFAP attributes the shift mainly to industry forces, not enforcement: increased local US hiring by Indian firms, the ability to perform more work offshore from India, and technology change — chiefly automation and AI.

The tell is in the companies' own words. TCS has said it will not hire new H-1B employees in the coming year. The top Tier-I firms already report 60% to 70% US localization, leaning on local hires, US-based subcontractors, and automation to reduce visa dependence. When the cost of a visa rises, a firm that has already built a domestic American workforce simply shrugs. The body-shop model — labor arbitrage delivered through a visa — is being replaced by a model where the work is either done by locals in America or by software anywhere.

## What it means for the diaspora

For NRIs, this reframes a story usually told as political. The narrowing path to America for Indian tech workers is real — Indians still make up roughly 70% of H-1B recipients, and a graduate who took on six figures of debt for a US master's now faces a $100,000 fee standing between them and a work visa. But the deeper change is that the industry that historically sponsored those visas has decided it can grow without them.

That has uneven consequences. The Indian-American who already holds a green card or citizenship and works at one of the big US sponsors is relatively insulated — those firms are hiring locally and that is now the dominant channel. The recent graduate on OPT hoping an Infosys or Wipro will sponsor them is far more exposed, because that door is closing from both sides at once: policy and business model. And the relative back in India whose career was built on the expectation of an eventual US rotation may find that rotation no longer exists as a rung on the ladder.

## The automation undertow

The uncomfortable part is what replaces the offshore seat. Indian IT leaders are telling investors that AI will reshape — and in many functions shrink — the workforce. Agentic AI tools that can navigate enterprise applications and resolve support tickets compete directly with the entry-level offshore roles that once absorbed hundreds of thousands of new engineering graduates each year. Nandan Nilekani has argued the opposite at Infosys's AGM, insisting AI will expand the addressable market rather than gut headcount, but the broader industry signal is one of caution on hiring.

The bottom line for the diaspora is that two myths are dying together. One is that the H-1B is simply being taken away by hostile politics; in fact the industry is walking away from it. The other is that an Indian engineering degree is an automatic ticket to a US tech career; increasingly, it is a ticket to a domestic Indian tech economy that — as Amazon's and Microsoft's multibillion-dollar India build-outs suggest — may end up being the more interesting place to be."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
