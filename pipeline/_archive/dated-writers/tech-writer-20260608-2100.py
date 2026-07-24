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
        "headline": "Sriram Krishnan Is Leaving the White House. He Shaped America's AI Playbook.",
        "subheadline": "The Chennai-born former Andreessen Horowitz partner exits after 18 months of writing the rules for the world's most consequential technology race.",
        "slug": make_slug("sriram-krishnan-white-house-ai-advisor-exit"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Krishnan's departure marks the exit of the most senior Indian-American voice in US AI policymaking. His tenure shaped executive orders, model-access agreements with Google and Microsoft, and the national AI framework that directly affects every Indian engineer on an H-1B building AI systems in Silicon Valley.",
        "tags": ["ai-policy", "indian-tech", "white-house", "sriram-krishnan", "diaspora-leadership"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/white-house-ai-policy-adviser-krishnan-leave-position-2026-06-07/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/07/sriram-krishnan-is-leaving-his-role-as-white-house-ai-advisor/"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/tech-and-telecom-law/trump-ai-policy-adviser-krishnan-is-giving-up-white-house-role"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/white-house-ai-adviser-sriram-krishnan-to-step-down-at-end-of-june/article69668000.ece"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/da/MS200024.jpg",
        "image_caption": "Sriram Krishnan, the outgoing White House AI policy adviser",
        "image_attribution": "Wikimedia Commons",
        "body": """When Sriram Krishnan posted on X last Saturday that he would leave the White House at the end of June, the announcement landed with the quiet precision of a man who had spent 18 months learning how Washington actually works. No drama, no leaked departure memo. Just a graceful exit from one of the most consequential technology policy roles in the world.

"This journey has been the privilege of a lifetime," he wrote. "Without his leadership, we would not be leading in the AI race."

The "his" was Donald Trump. The AI race is the one Krishnan helped define the rules for.

## From Chennai to the West Wing

Krishnan's trajectory reads like a particularly ambitious version of the Indian tech diaspora story. Born in Chennai, he built his career across the biggest names in Silicon Valley — product roles at Microsoft, Facebook, Twitter, Yahoo, and Snap — before landing at Andreessen Horowitz as a general partner. When Elon Musk acquired Twitter in 2022, Krishnan was on the transition team that helped rebuild the platform.

That proximity to Musk and the a16z founders, who threw their considerable weight behind Trump's 2024 campaign, opened the door to the White House. In early 2025, Krishnan became the senior policy adviser on artificial intelligence, reporting alongside David Sacks, the investor-turned-crypto-and-AI czar.

## The Policy Footprint

The accomplishments Krishnan claims are not trivial. The American AI Action Plan, released in July 2025, effectively set the tone for the administration's approach: build infrastructure fast, regulate lightly, and ensure American companies stay ahead of Chinese rivals. Data center construction accelerated. State-level AI regulations were challenged through executive order. And Krishnan personally brokered agreements with Google, Microsoft, and xAI to give the US government early access to their most capable AI models for security testing.

That last point matters more than it sounds. As frontier models like Anthropic's Mythos demonstrated the ability to expose cybersecurity weaknesses in banking systems, the question of who gets to test these models before public release became urgent. Krishnan helped build the framework for that review process.

His departure comes just days after the White House signed an executive order directing federal agencies to ask leading AI developers to voluntarily submit their most powerful models for government cybersecurity tests before release.

## What It Means for the Diaspora

Krishnan was, by any measure, the most senior Indian-American voice shaping US AI policy. His exit leaves a gap at a moment when the stakes are only rising. Trump has publicly floated the idea of the government taking equity stakes in major AI companies — a proposal that would directly affect the valuations and governance structures of firms where tens of thousands of Indian engineers work.

For the roughly 300,000 Indian tech professionals on H-1B visas in the United States, the national AI framework Krishnan helped build is not abstract policy. It determines whether states can independently restrict AI development, how quickly data centers can be permitted, and whether the government's embrace of AI translates into more jobs or fewer.

Krishnan has said he plans to take a short break before launching a new initiative to "tackle some of the large challenges facing America on AI." David Sacks confirmed he will continue as an outside adviser to the White House.

## The Larger Pattern

Krishnan's departure follows Sacks's own transition from AI czar to co-chair of the President's Council of Advisors on Science and Technology earlier this year. The revolving door between Silicon Valley and Washington is spinning faster than ever, and Indian-Americans are increasingly passing through it in both directions.

Whether that proximity to power translates into durable influence — on immigration policy, on AI regulation, on the terms under which Indian tech talent can build careers in America — remains the open question. Krishnan helped write the first draft of the answer. Someone else will write the next one."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Just Built a PC Chip That Runs AI Models Locally. Apple Should Be Nervous.",
        "subheadline": "The RTX Spark, unveiled at Computex with MediaTek, packs a petaflop of AI power into a laptop. For Indian developers who've been buying MacBooks, the math just changed.",
        "slug": make_slug("nvidia-rtx-spark-arm-ai-pc-chip-apple-challenge"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian developers and AI engineers in the US — the single largest national group in Silicon Valley's technical workforce — have overwhelmingly defaulted to MacBooks for local development. The RTX Spark's ability to run large language models locally on Windows, with 128GB unified memory and CUDA cores, could shift that calculus for the tens of thousands of NRI engineers building agentic AI systems.",
        "tags": ["nvidia", "ai-pc", "arm-chip", "computex", "indian-developers", "apple"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/nvidias-ai-pc-push-banks-unproven-demand-beyond-niche-users-2026-06-08/"},
            {"name": "XDA Developers", "url": "https://www.xda-developers.com/nvidia-rtx-spark-reinvent-pc-windows-arm/"},
            {"name": "MediaTek", "url": "https://www.mediatek.com/blog/mediatek-collaborates-with-nvidia-on-rtx-spark"},
            {"name": "LinkedIn (Computex Analysis)", "url": "https://www.linkedin.com/pulse/computex-2026-worlds-largest-ai-hardware-show-signals/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Close-up of a microprocessor circuit board with intricate circuitry",
        "image_attribution": "Pexels",
        "body": """For five years, Jensen Huang has told the world that AI lives in the data centre. Last week at Computex in Taipei, he changed his mind — or at least expanded the address book. Nvidia's RTX Spark, unveiled on June 1 in a coordinated announcement with Microsoft and MediaTek, is the company's first real consumer PC chip. And it is not subtle.

The specifications read like a small server that someone accidentally put in a laptop: a 20-core ARM CPU designed with MediaTek, Blackwell-generation RTX graphics with 6,144 CUDA cores (the same as a desktop RTX 5070), up to 128GB of unified LPDDR5X memory, and 1 petaflop of AI performance. The CPU and GPU are stitched together via NVLink-C2C, an interconnect borrowed from Nvidia's data centre playbook. Power draw sits between 45 and 80 watts.

## The Pitch: Your Laptop Is Now Your AI Server

Nvidia's argument is straightforward. The cloud is expensive, latency is real, and privacy matters. If you can run a capable large language model on your own hardware — without sending your proprietary code, your medical records, or your client data to someone else's server — the economics of AI shift dramatically.

"RTX Spark doesn't make traditional PCs obsolete. It creates a new category between the workstation and the AI server," said Kevin Hein, an analyst at Tirias Research.

Six OEMs are already on board. Microsoft is building a developer workstation. Dell has the XPS 16 Creator Edition with a Tandem OLED display. ASUS, HP, Lenovo, and MSI are all shipping RTX Spark laptops. Adobe has confirmed optimised versions of Premiere Pro and Photoshop for the platform. Nvidia's own Nemotron models will run locally, and the company is pitching agentic AI workflows — where AI handles multi-step tasks like code debugging or video generation — as the core use case.

## Why This Matters for Indian Developers

Walk into any engineering floor at Google, Meta, Microsoft, or a Bay Area startup, and count the MacBooks. Apple's M-series chips have owned the local AI development conversation since 2020, offering unified memory and respectable ML performance in a package that runs cool and lasts all day. For Indian engineers — who represent the single largest national group in Silicon Valley's technical workforce — the MacBook Pro has been less a preference than a default.

The RTX Spark challenges that default directly. Its 128GB of unified memory matches the highest-end MacBook Pro. Its CUDA cores offer something Apple cannot: native compatibility with the training and inference frameworks (PyTorch, TensorFlow, CUDA itself) that the entire AI industry is built on. For developers who have been maintaining separate workflows for local experimentation (Apple Silicon) and production deployment (Nvidia GPUs in the cloud), a single architecture that bridges both is genuinely compelling.

Reuters reported that analysts remain skeptical about mainstream consumer adoption. AI PCs have been marketed for two years with modest features — transcription, image editing — and have failed to drive meaningful sales. But Nvidia is not pitching the RTX Spark to mainstream consumers. It is pitching it to the people who build AI systems, and that is a very different market.

## The Arm Angle

Notably, AMD publicly welcomed Nvidia into the Windows-on-Arm fight rather than protesting — a signal that the PC's architectural centre of gravity is genuinely shifting. Qualcomm, which has been pushing ARM-based Windows chips for years with limited traction, now faces a competitor with an entirely different value proposition. Where Qualcomm sold efficiency and battery life, Nvidia is selling raw AI computation.

For MediaTek, the collaboration is a statement of ambition. The Taiwanese chipmaker, dominant in smartphone processors but a minor player in PCs, gains instant credibility in the high-performance computing space. MediaTek's CPU design expertise handles the efficiency side while Nvidia brings the AI muscle — a division of labour that mirrors how ARM-based server chips have been carving into Intel's data centre business for years.

## The Price Question

What Nvidia has not yet revealed is pricing. The RTX Spark's specifications position it against MacBook Pros that start at $2,499 and stretch past $4,000 for the 128GB configuration. If RTX Spark laptops land in a similar range, the value proposition becomes a direct feature comparison. If they come in lower — which the MediaTek partnership and competitive OEM dynamics suggest is possible — the disruption could be more significant than the specs alone imply.

For the estimated 500,000 Indian engineers working in US tech, many of whom expense their development machines through their employers, the decision may ultimately come down to one question: can I run the same model on my laptop that I deploy to production? If the RTX Spark delivers on that promise, the MacBook's reign as the developer's default may finally face a serious challenge."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Startup Founders Are Stuck Between Seed and Scale. Global AI Is Hoarding the Capital.",
        "subheadline": "A Series A squeeze is stranding India's best seed-funded companies as global venture capital floods into American AI labs. The numbers are stark.",
        "slug": make_slug("india-startup-series-a-funding-squeeze-ai-capital"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "NRI investors and diaspora founders face a double bind: global VC capital that used to flow into India deals is being redirected to US AI companies, while Indian founders in the Bay Area trying to raise for India-focused startups find fewer co-investors willing to write Series A checks for non-AI businesses.",
        "tags": ["indian-startups", "venture-capital", "funding", "series-a", "ai-investment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/series-a-capital-squeeze-leaves-start-ups-stranded-between-seed-and-scale/article69668200.ece"},
            {"name": "Inc42", "url": "https://inc42.com/buzz/from-firstclub-to-innefu-indian-startups-raised-187-mn-this-week/"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/start-ups/indian-vcs-join-a-global-race-to-back-the-next-big-ai-disruptor-11738162989680.html"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37088158/pexels-photo-37088158.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Aerial view of Bengaluru's skyline at twilight, India's startup capital",
        "image_attribution": "Pexels",
        "body": """Something uncomfortable is happening in India's startup ecosystem, and the weekly funding numbers tell the story before any analyst needs to explain it.

Last week, Indian startups collectively raised $187 million. The headline number sounds healthy until you look at the composition: one defence-AI company (Innefu Labs, $30 million) accounted for most of the haul. The remaining deals were dominated by pre-seed and seed rounds — $2 million here, $1.5 million there. Aquapulse raised a $2.1 million Series A. Zuvees managed $1.6 million. The largest non-defence deal was a $100 million commitment from an established player, not a growth-stage startup breaking through.

The pattern is not a blip. It is a structural shift that is leaving India's most promising seed-funded companies stranded in a no-man's land between early traction and scale.

## The Series A Gap

"Two or three years ago, investors were often underwriting future potential. Today, they are underwriting demonstrated execution," Ashish Taneja, founder and CEO of growX ventures, told The Hindu Business Line.

The data backs him up. During the 2021 funding boom, global crossover funds — Tiger Global, SoftBank Vision Fund, Coatue, Insight Partners — competed fiercely for Indian Series A and B deals. They wrote $10-50 million cheques on the strength of a pitch deck and a growing user base. That era is over.

Today, those same funds are deploying the bulk of their capital into a single sector in a single geography: artificial intelligence companies in the United States. OpenAI, Anthropic, xAI, and a handful of frontier AI labs have absorbed billions in capital that would previously have been diversified across emerging markets. When a single company like OpenAI raises over $40 billion in equity, the gravitational pull on the entire venture capital ecosystem is immense.

"While there is another boom underway in the US, most of the capital is being concentrated in leading AI companies," said Bhagia, an investor tracking the India market. "As a result, you rarely hear of these funds doing deals in India."

## The Conviction Threshold

The absence of global crossover capital is only half the problem. Indian domestic VCs — Blume Ventures, Accel India, Elevation Capital, Lightspeed India — still have dry powder. But their conviction thresholds have risen sharply. Series A investors now want what seed investors used to accept as a promise: proof of product-market fit, improving unit economics, and evidence of rapid scalability.

"The challenge today is not a lack of capital in the ecosystem," Taneja said. "It's that capital has become far more selective."

The result is a growing cohort of Indian startups that successfully raised seed rounds in 2023 and 2024, built products, acquired early customers, and are now discovering that the bridge to their next round has been pulled away. They are too mature for seed funding and not yet proven enough for the new, higher bar that Series A demands.

## The AI Magnet

A significant share of venture capital attention has shifted toward AI-led opportunities, particularly companies targeting global markets. Indian VCs are not immune to this pull. Accel India has invested in Paris-based agentic AI firm H and US-based startup Ema. Blume Ventures has pivoted toward AI agents and infrastructure plays. Even within India-focused portfolios, the most competitive deals are AI-native — companies like Sarvam AI and the handful of startups building foundation models or enterprise AI tools.

For founders building in fintech, D2C, healthtech, or edtech — sectors that drove India's previous startup boom — the message is clear: the market has moved, and you need to move with it or accept a longer, leaner path to your next round.

## What It Means for NRI Investors and Founders

The Series A squeeze creates a specific dilemma for the Indian diaspora. NRI angel investors who backed Indian seed-stage companies in 2023-2024 are watching their portfolio companies struggle to raise follow-on capital. The path to returns has lengthened considerably.

For diaspora founders in the Bay Area building India-focused businesses, the fundraising environment is bifurcated. If your company is AI-native and targets a global market, capital is abundant. If it serves the Indian domestic market in a non-AI vertical, the investor pool has shrunk.

India produced 109 unicorns between 2014 and 2024, with Bengaluru, Mumbai, and Gurugram as the primary hubs. The infrastructure for startup creation — accelerators, angel networks, seed funds — has never been stronger. But the bridge from seed to scale depends on follow-on capital that is currently flowing elsewhere.

The question is whether this is a temporary reallocation driven by the AI hype cycle, or a permanent restructuring of how global capital evaluates India's startup opportunity. For the hundreds of founders currently stuck between seed and Series A, the distinction is academic. The money, for now, is somewhere else."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
