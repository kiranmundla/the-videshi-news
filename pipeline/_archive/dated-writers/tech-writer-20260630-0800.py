#!/usr/bin/env python3
"""Videshi Technology Writer – 2026-06-30 08:00 run."""
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


# ── Article 1: IBM Sub-1nm Chip ──────────────────────────────────────────────

art1_body = """If Moore's Law were a patient, most doctors would have pulled the plug years ago. Instead, Arvind Krishna's IBM just administered a jolt of electricity.

Last week, IBM Research unveiled the world's first sub-1 nanometre chip technology — a fingernail-sized slab of silicon packing nearly 100 billion transistors at the 0.7 nanometre node, or 7 angstroms, a scale where dimensions approach the width of individual atoms. The announcement, presented at the VLSI 2026 symposium, represents what IBM calls a "completely new paradigm" in chip design.

At its heart is a novel architecture IBM dubs "nanostack." Instead of continuing to shrink transistors laterally — the approach that has driven the semiconductor industry for six decades — nanostack stacks them vertically in three dimensions. Think of it as going from single-storey suburban sprawl to a high-rise: same footprint, dramatically more capacity.

The numbers are striking. Compared with IBM's own 2 nm node, unveiled in 2021, the new technology delivers up to 50 per cent more performance or 70 per cent greater energy efficiency. It achieves nearly twice the transistor density. And IBM's researchers demonstrated a 40 per cent improvement in SRAM scaling, a critical metric for the bandwidth-hungry workloads that define modern AI.

"With our new nanostack architecture, we're not just making smaller transistors, we're reinventing how chips are built," said Jay Gambetta, director of IBM Research.

## Why this matters for AI

Today, the world's most advanced AI chips — Nvidia's Blackwell, Apple's M-series, Qualcomm's Snapdragon — are built on 3 nm and 4 nm fabrication processes, almost exclusively by Taiwan Semiconductor Manufacturing Company. Nvidia's forthcoming Vera Rubin platform uses TSMC's 3 nm family. TSMC has already begun mass-producing 2 nm chips.

IBM's breakthrough suggests there is at least a decade of headroom beyond that. In an industry where companies like OpenAI, Microsoft, and Google are spending a combined $725 billion on AI infrastructure this year alone, every incremental gain in transistor efficiency translates to meaningful savings in power and compute cost — the twin constraints throttling AI's expansion.

IBM itself does not manufacture chips at scale. It licenses its research to foundries. Its 2 nm node is now in production at Samsung, TSMC, and Intel. The 0.7 nm architecture could follow the same path within five years, according to IBM.

## The Krishna factor

For Indian Americans watching this space, the subtext is hard to miss. Arvind Krishna, the IIT Kanpur and University of Illinois alumnus who has led IBM since 2020, has methodically repositioned the 114-year-old company around hybrid cloud and AI — shedding its managed infrastructure business, acquiring HashiCorp, and investing heavily in semiconductor research and quantum computing. IBM's market capitalisation has roughly doubled under his watch.

Krishna is not the only Indian-origin chief executive shaping the chip landscape. Sanjay Mehrotra's Micron just posted a record $41.5 billion quarter. Nikesh Arora's Palo Alto Networks hit an all-time high. Jayshree Ullal's Arista Networks built the networking infrastructure that Nvidia now competes in. But Krishna's IBM is arguably the most consequential: its research lab has been the birthplace of semiconductor breakthroughs since the 1960s, and the chips that emerge from Yorktown Heights tend to define the industry's trajectory a decade later.

## India's angle

The breakthrough also intersects with India's own semiconductor ambitions. New Delhi has approved 12 chip manufacturing projects under the India Semiconductor Mission with an investment pipeline of nearly ₹1.64 lakh crore. Tata Electronics is building a fab in Dholera, Gujarat. Intel and 3DGS announced a $3.3 billion substrate plant in Bhubaneswar. Odisha just laid the foundation for the country's first 3D chip packaging unit.

But India's current capabilities are in packaging and assembly — the downstream end of the value chain. The kind of foundational transistor research IBM does at Yorktown Heights is where value is truly created, and it remains concentrated in the United States, Taiwan, South Korea, and the Netherlands. For the tens of thousands of Indian semiconductor engineers working at these facilities abroad, the nanostack announcement is both a professional milestone and a reminder of the gap India still has to close.

IBM has built a chip the size of a fingernail that approaches atomic dimensions. Whether India can build the ecosystem to manufacture it is the question that matters next."""


# ── Article 2: OpenAI Jalapeño Chip ──────────────────────────────────────────

art2_body = """Nine months. That is all it took OpenAI, working with chip giant Broadcom, to go from initial design to manufacturing tape-out on its first custom artificial intelligence processor.

The chip, codenamed Jalapeño, was unveiled on June 24 when Broadcom CEO Hock Tan personally delivered engineering samples to OpenAI CEO Sam Altman at the company's San Francisco headquarters. It is a custom-built inference processor — an application-specific integrated circuit designed from the ground up to run large language models after they have been trained, not to train them in the first place.

The early results, if they hold, are significant. Broadcom's Tan told Reuters and Bloomberg that initial lab testing shows approximately 50 per cent lower inference cost per token compared with current-generation Nvidia GPUs. OpenAI's own announcement was more carefully worded, describing performance per watt as "substantially better than current state-of-the-art." A detailed technical report is expected in the coming months.

The speed of development is itself a statement. Nine months is blisteringly fast for a high-performance semiconductor — most ASICs take two to three years from concept to tape-out. OpenAI credits part of that acceleration to its own AI models, which assisted in the chip's design and optimisation process. AI designing the chips that run AI is no longer a thought experiment; it is now an engineering reality.

## Full-stack ambitions

Jalapeño is not a one-off experiment. OpenAI described it as the first element of a "multi-generation compute platform" and laid out a vision where it controls the entire stack: chip architecture, kernels, memory systems, networking, scheduling, deployment, and the product experience layer on top. OpenAI wants to be the Apple of artificial intelligence — owning the silicon, the software, and the service.

The economic logic is compelling. OpenAI reportedly spent approximately $14 billion serving ChatGPT in 2025, primarily on rented Nvidia GPUs. A 50 per cent reduction in inference costs at that scale is not a marginal optimisation; it is a profitability-defining lever. Broadcom expects prototype data centre deployments by late 2026, production ramp in 2027, and full-scale deployment — at gigawatt scale with Microsoft and other partners — through 2029.

OpenAI joins an exclusive club. Google has its TPUs. Amazon has Trainium and Inferentia. Microsoft is building Maia. Meta has its MTIA chip. Each is trying to reduce dependence on Nvidia, whose GPUs currently command roughly 80 per cent of the AI accelerator market and carry the pricing power to match.

## The diaspora dimension

For the Indian tech community, this announcement reverberates on several levels.

Broadcom, Jalapeño's implementation partner, has deep ties to Indian engineering talent. The chip was manufactured by TSMC, where thousands of Indian-origin engineers work across design, process, and packaging roles. And OpenAI itself just hired Prabhjeet Singh, an IIT-IIM graduate and former Uber India chief, as its managing director for India — a signal that the company's ambitions extend well beyond San Francisco.

For Indian IT services companies, the implications are more sobering. Every dollar OpenAI shaves off inference costs makes AI-powered coding tools cheaper to run, intensifying the pressure on companies like Infosys, TCS, and Wipro, whose business models still depend heavily on human-delivered software services. JP Morgan recently warned that Indian IT faces a second year of "AI deflation" — declining revenue per unit of work as AI compresses delivery timelines.

For NRI investors, the chip war between OpenAI, Google, Amazon, and Nvidia is worth watching closely. Nvidia's stock has been essentially flat for 2026 despite massive revenue growth, partly because the market is pricing in exactly this kind of competitive pressure. If custom chips from OpenAI and others erode Nvidia's pricing power, the ripple effects will reach every AI-adjacent portfolio.

Jalapeño is, for now, a lab project running an unreleased GPT-5.3-Codex-Spark model. But the message is clear: the companies building AI are no longer content to rent their compute. They are building it themselves, nine months at a time."""


# ── Article 3: Infosys / Nilekani AGM ────────────────────────────────────────

art3_body = """It is the question that 5.3 million Indian IT workers would rather not hear, and Nandan Nilekani said it out loud.

"If coding becomes automated, then why are we needed at all?"

The Infosys co-founder and chairman posed the existential query at the company's annual general meeting last week, then spent his address explaining why the answer is not as dire as it sounds — at least, not for the companies willing to evolve.

Nilekani's argument is straightforward, even if his audience's nerves were not. AI can generate code, he conceded. But enterprise software is not code. It is context. "Solutions must complement existing investments," he told shareholders. "They demand rigorous testing, resilient architecture, and foundational cybersecurity." A vibe-coded prototype may impress on a demo stage, but plugging it into a Fortune 500 bank's legacy stack with 30 years of accumulated technical debt is a different proposition entirely.

The timing of the speech was deliberate. Infosys shares have fallen more than 28 per cent since the start of the year, battered by investor fears that AI-native tools — Anthropic's Claude Cowork, OpenAI's Codex, GitHub Copilot — are compressing the work that has powered India's IT industry for three decades. Earlier this month, both Anthropic and OpenAI announced partnerships with private equity firms to enter the enterprise services market directly, sending the Nifty IT index into a 5.5 per cent single-day plunge.

## The deflation dilemma

Nilekani did not deny the pressure. He acknowledged that AI is "compressing delivery timelines and team sizes," which in plain terms means clients are getting the same output with fewer billable hours. JP Morgan recently warned of a second year of "AI deflation" hitting Indian IT margins.

But Nilekani pivoted to what he sees as the other side of the ledger. "The AI revolution has made legacy modernisation urgent in a way nothing else has," he said. Clients who have deferred cleaning up decades of technical debt — the mainframe spaghetti, the custom COBOL, the duct-taped middleware — can no longer afford to wait. AI tools now make it possible to rewrite those systems faster, but someone still has to do the rewriting. Someone still has to understand the business logic those systems encode. And that someone, Nilekani argues, is Infosys.

He went further: organisations adopting AI will increasingly prefer custom-built solutions over packaged software, because AI enables bespoke development at speeds and costs that previously only made sense for off-the-shelf products. "The defining opportunity lies in integrating intelligent AI systems with mission-critical enterprise platforms," he said. "That convergence is where the next wave of opportunities will emerge."

## Sceptics remain

Not everyone is buying it. Analysts noted drily that Nilekani made no direct mention of "AI deflation" — the very revenue erosion that Infosys itself has acknowledged in earnings calls. Infosys ended its last fiscal year with $20.16 billion in revenue, up 4.6 per cent, but a third of that incremental growth came from manufacturing clients, not the banking and tech sectors that form its traditional core.

The market's scepticism has a quantitative basis. If AI coding tools reduce a $10 million project to $6 million, Nilekani's argument is that AI modernisation creates two new $6 million projects. The maths works only if the total addressable market expands faster than AI compresses individual engagements — a bet, not a certainty.

## What it means for NRIs

For the estimated 300,000-plus Indian IT professionals working in the United States on H-1B visas, Nilekani's speech lands differently than it does for shareholders. Their visas are tied to specific employers, and their immigration timelines stretch decades for Indian nationals. If AI-driven workforce reductions reach Infosys's US operations — or those of TCS, Wipro, and HCL — the consequences extend well beyond severance packages.

Yet Nilekani's core point deserves serious consideration. Every major technology transition — client-server, internet, mobile, cloud — prompted the same existential panic in Indian IT, and each time the industry emerged larger, not smaller. AI may be the biggest transition of them all. Whether Infosys can navigate it as successfully as it navigated cloud migration remains the $20 billion question.

Nilekani, characteristically, is not worried. "More than three years after GenAI's launch, Infosys is more relevant than ever," he told shareholders. The stock market's 28 per cent haircut suggests investors are still making up their minds."""


# ── Define articles ──────────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Krishna's IBM Just Built a Chip Smaller Than One Nanometre. It Packs 100 Billion Transistors.",
        "subheadline": "The 'nanostack' architecture stacks transistors in 3D for the first time, pointing to a decade of continued scaling — and raising questions about where India fits in the atomic-scale chip race.",
        "slug": make_slug("ibm-arvind-krishna-sub-1nm-nanostack-chip-100-billion-transistors"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "IBM's Indian-origin CEO Arvind Krishna leads the company behind the world's most consequential chip breakthrough, while India's own semiconductor ambitions remain focused on packaging and assembly rather than foundational transistor research.",
        "tags": ["ibm", "semiconductors", "arvind-krishna", "ai-chips", "nanostack"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/ibm-unveils-tech-chip-smaller-than-1-nanometer-ai-computing-push-2026-06-25/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ibm-chip-nanometer-stock-price-5d4a5e34"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/ibm-stock-sub-1-nanometer-chip-technology/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Arvind_Krishna_at_SXSW_2025.jpg/1280px-Arvind_Krishna_at_SXSW_2025.jpg",
        "image_caption": "IBM CEO Arvind Krishna at SXSW 2025",
        "image_attribution": "Wikimedia Commons",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI Built Its First Chip in Nine Months. It Used AI to Design It.",
        "subheadline": "The Jalapeño inference processor, developed with Broadcom, could cut ChatGPT's serving costs by half — and signals that AI companies are done renting Nvidia's hardware.",
        "slug": make_slug("openai-jalapeno-chip-broadcom-nine-months-inference-ai"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers are deeply embedded across Broadcom, TSMC, and OpenAI's own India operation under new MD Prabhjeet Singh; cheaper AI inference accelerates the disruption pressure on Indian IT services companies.",
        "tags": ["openai", "ai-chips", "broadcom", "inference", "jalapeno"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Register", "url": "https://www.theregister.com/ai-and-ml/2026/06/24/openai-gets-chippy-with-broadcom/5261697"},
            {"name": "The Bridge Chronicle", "url": "https://www.thebridgechronicle.com/technology/openai-and-broadcoms-jalapeno-chip-what-it-is-and-why-its-important"},
            {"name": "SiliconANGLE", "url": "https://siliconangle.com/2026/06/24/openai-broadcom-debut-custom-jalapeno-chip-ai-inference/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36169774/pexels-photo-36169774.jpeg",
        "image_caption": "Close-up of electronic microchips on a circuit board",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "'If Coding Becomes Automated, Why Are We Needed?' Nilekani Has an Answer.",
        "subheadline": "The Infosys chairman used his annual general meeting speech to confront AI's existential threat to Indian IT — arguing that the bigger the disruption, the bigger the opportunity for services firms.",
        "slug": make_slug("nilekani-infosys-agm-coding-automated-ai-indian-it"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Over 300,000 Indian IT professionals in the US on H-1B visas face direct career implications as AI reshapes the services industry that employs them; Infosys's 28% stock decline this year has hit NRI investor portfolios hard.",
        "tags": ["infosys", "nilekani", "indian-it", "ai-disruption", "vibe-coding"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Register", "url": "https://www.theregister.com/channel/2026/06/25/infosys-boss-says-vibe-coding-is-no-threat-because-theres-more-to-writing-software-than-writing-software/5261900"},
            {"name": "Livemint", "url": "https://www.livemint.com/companies/news/if-coding-becomes-automated-why-are-we-needed-at-all-infosys-chairman-nilekani-answers-11749553437746.html"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Nandan_M._Nilekani.jpg",
        "image_caption": "Infosys co-founder and chairman Nandan Nilekani",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body,
    },
]

# ── Insert ───────────────────────────────────────────────────────────────────

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
