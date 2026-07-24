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
        "headline": "Satya Nadella's Microsoft Just Built Its Own AI Brain. OpenAI Should Be Worried.",
        "subheadline": "Seven new MAI models, including a trillion-parameter reasoning engine trained from scratch, signal that Microsoft no longer needs its most famous AI partner to compete at the frontier.",
        "slug": make_slug("microsoft-mai-thinking-1-satya-nadella-frontier-lab"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella, the Indian-origin CEO who transformed Microsoft into a $3 trillion company, is now building the AI models that could make OpenAI redundant. For the thousands of Indian engineers at Microsoft — many on H-1B visas — this pivot reshapes their career trajectories. Microsoft AI roles become frontier research positions, not just integration work. And for NRI investors holding MSFT stock, the margin story shifts dramatically when Microsoft runs its own models instead of paying OpenAI per token.",
        "tags": ["microsoft", "ai-models", "satya-nadella", "mustafa-suleyman", "mai-thinking", "frontier-ai", "openai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Microsoft AI Blog", "url": "https://microsoft.ai"},
            {"name": "PureAI", "url": "https://pureai.com"},
            {"name": "FourWeekMBA", "url": "https://fourweekmba.com"},
            {"name": "TechRepublic", "url": "https://techrepublic.com"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/20/Mustafa_Suleyman_photo_%28cropped%29.jpg",
        "image_caption": "Mustafa Suleyman, CEO of Microsoft AI, who unveiled seven new MAI models at Build 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """For years, Microsoft's AI strategy had a simple summary: write large cheques to OpenAI, wrap GPT models in Azure and Copilot branding, and collect enterprise subscription fees. It was lucrative, predictable, and — increasingly — a strategic liability.

At Build 2026 this week, Microsoft tore up that playbook. Mustafa Suleyman, the DeepMind co-founder who now runs Microsoft AI, walked onstage and unveiled seven proprietary MAI models, headlined by MAI-Thinking-1 — a reasoning engine with 35 billion active parameters drawn from roughly one trillion total. The claim that turned heads: it matches GPT-5.4 on enterprise reasoning tasks while costing up to ten times less to run.

## Trained from scratch, not borrowed

The pointed emphasis throughout Suleyman's presentation was provenance. MAI-Thinking-1 was trained from scratch on commercially licensed data. No distillation from OpenAI. No borrowed weights. No ambiguous data lineage that could spook a Fortune 500 compliance team. "We don't distil from other labs and we don't rely on unlicensed or opaque data," the MAI team wrote in a technical blog post. "Every component of the system — from architecture to training pipeline to post-training — we built ourselves."

That sentence is aimed directly at enterprise procurement officers who have spent two years asking their lawyers whether the AI models in their stack have copyright exposure. It is also aimed at OpenAI.

The mixture-of-experts architecture is noteworthy. Only 35 billion of the model's roughly one trillion parameters activate per token — keeping inference costs low without sacrificing reasoning depth. Microsoft says it achieves 97 per cent on AME 2025 reasoning benchmarks and is competitive with Claude Opus 4.6 on SWE-Bench Pro, the software engineering benchmark that matters most to developer tool customers.

## Seven models, one strategy

MAI-Thinking-1 is not a standalone product. It anchors a family of seven models spanning every modality Microsoft needs:

**MAI-Code-1-Flash** handles text-to-code generation and is rolling out across GitHub Copilot and VS Code. From August, it will run alongside Project Polaris, which replaces GPT-4 Turbo in Copilot entirely.

**MAI-Image-2.5** ranked second on Arena's image editing leaderboard at launch — a credible threat to Midjourney and DALL-E in enterprise creative workflows.

**MAI-Voice-2** delivers multilingual speech synthesis across 16 languages with emotional range — angry, confused, embarrassed tones — targeting the voice agent market that every enterprise is scrambling to build.

**MAI-Transcribe-1.5** claims the lowest word error rate across 43 languages, outperforming both Google and OpenAI on speech-to-text benchmarks.

The full stack is designed to run on Microsoft's own Maia 200 silicon, with a reported 1.4x efficiency boost from hardware-software co-design. That vertical integration — custom models on custom chips — mirrors what Google has done with TPUs and Gemini.

## What Microsoft Frontier Tuning means for enterprise AI

The most commercially significant announcement may have been Microsoft Frontier Tuning, a platform that lets organisations create custom fine-tuned versions of MAI models using their own data. In a live demonstration, a Frontier-Tuned MAI model built for Excel matched GPT-5.4 performance at a fraction of the compute cost.

The economics are straightforward. Instead of paying per-token for the most powerful OpenAI API, an enterprise fine-tunes a smaller MAI model on its specific workflows and runs it for pennies. Microsoft captures the customer either way — but the margin structure shifts dramatically in Microsoft's favour when the customer runs Redmond's own model rather than routing through San Francisco.

## Why this matters to Indian tech professionals

For the estimated 35,000-plus Indian engineers at Microsoft — a significant portion on H-1B visas — the MAI pivot transforms what "working in AI at Microsoft" means. These are no longer integration roles wrapping someone else's model in an API. They are frontier research positions, training models from scratch, designing inference infrastructure, and building the post-training reinforcement learning pipelines that turn a base model into a product.

Satya Nadella, who has spent a decade as perhaps the most consequential Indian-origin CEO in tech history, is making a bet that Microsoft can be both a platform for other labs' models and a frontier lab itself. The OpenAI partnership remains — the two companies still share infrastructure and revenue — but the dependency is visibly shrinking.

For NRI investors holding MSFT, the calculus has changed. Every dollar of AI revenue Microsoft generates on its own models, rather than OpenAI's, flows through at higher margins. Nadella is building a moat, not renting one."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "NVIDIA Just Open-Sourced the Biggest AI Model in America. It Runs on a Single Server.",
        "subheadline": "Nemotron 3 Ultra packs 550 billion parameters into a hybrid architecture that is five times faster than rivals — and Jensen Huang is giving it away for free.",
        "slug": make_slug("nvidia-nemotron-3-ultra-550b-open-weight-model-agents"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NVIDIA employs thousands of Indian engineers across its Santa Clara headquarters, Bangalore R&D centre, and Pune offices. Open-weight models like Nemotron 3 Ultra are particularly significant for India's AI ecosystem: startups like Sarvam AI and Krutrim that cannot afford API costs for proprietary frontier models can now run a competitive alternative on their own infrastructure. For Indian AI researchers and ML engineers at NVIDIA, this release — trained on 20 trillion tokens with open training recipes — represents publishable, career-defining work in the open.",
        "tags": ["nvidia", "nemotron", "open-source-ai", "agentic-ai", "jensen-huang", "mamba-transformer"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NVIDIA Research", "url": "https://research.nvidia.com"},
            {"name": "AWS Machine Learning Blog", "url": "https://aws.amazon.com"},
            {"name": "Awesome Agents", "url": "https://awesomeagents.ai"},
            {"name": "Geeky Gadgets", "url": "https://geeky-gadgets.com"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Jensen Huang, NVIDIA CEO, who announced Nemotron 3 Ultra at Computex 2026 in Taipei",
        "image_attribution": "Wikimedia Commons",
        "body": """Two days after Jensen Huang teased it from the Computex stage in Taipei, NVIDIA released Nemotron 3 Ultra on June 4 — the largest open-weight AI model ever shipped by an American company. At 550 billion total parameters, it immediately became the best-performing US open model on the Artificial Analysis Intelligence Index, scoring 48 points and leaving every other domestic open release behind.

The number that matters more than parameter count: five times faster. NVIDIA claims Nemotron 3 Ultra delivers 5.9 times the throughput of comparable open models on standard benchmarks, while costing 30 per cent less per completed task. On an OpenRouter endpoint, it runs at $0.50 per million input tokens — with a free tier available for developers who want to test it without a credit card.

## A new architecture for agents that never stop

Nemotron 3 Ultra is not a standard transformer. NVIDIA built it on a hybrid Mamba-Transformer Mixture-of-Experts architecture — a mouthful that solves a real problem.

Traditional transformers scale quadratically with context length. Every new token attends to every previous token, which means costs explode as conversations or documents grow longer. Mamba layers, by contrast, use a state-space approach that retains distant context without the quadratic penalty. NVIDIA interleaves both: Mamba handles long-range memory efficiently, while transformer attention layers handle precise fact retrieval when the model needs to zero in on a specific detail.

The result is a model with a one-million-token context window on Blackwell hardware — roughly the length of three novels — that maintains coherence across multi-hundred-turn agent workflows. Only 55 billion of the 550 billion parameters activate per token, keeping per-inference costs manageable even at scale.

This architecture was designed for a specific use case: autonomous AI agents. Not chatbots that answer one question at a time, but software agents that plan, call tools, delegate to sub-agents, check results, and keep working across hundreds of turns. Every step adds tokens and cost, so the metric that matters is not peak intelligence on a benchmark — it is task completion rate per dollar.

## Everything is open

What makes this release unusual for a company that sells hardware is how much NVIDIA gave away. The full package includes:

- Pre-trained, post-trained, and quantised checkpoints in BF16 and NVFP4 formats
- 173 billion tokens of fresh code training data from GitHub (through September 2025)
- Synthetic datasets for legal reasoning, moral scenarios, and factual recall
- Complete post-training datasets for SFT and reinforcement learning
- The GenRM model used for RLHF
- Full model training recipes

The training data release is the real story. Most AI labs treat their datasets as crown jewels. NVIDIA is publishing the recipe book alongside the finished dish — a signal that it wants developers building on Nemotron, not competing with it. If your agent runs on Nemotron, you probably run it on NVIDIA hardware.

## The competitive landscape

NVIDIA is not hiding from the scoreboard. Nemotron 3 Ultra scores 48 on the Artificial Analysis Intelligence Index. That makes it the best US open model — but Moonshot AI's Kimi K2.6 from China scores 54 on the same index. NVIDIA's counter-argument is throughput: over 300 tokens per second on benchmark endpoints, roughly six times faster than Chinese frontier open models.

The non-hallucination score tells another story. At 78.7 per cent on AA-Omniscience, Nemotron 3 Ultra has the best factual accuracy in its comparison set. For enterprises deploying agents that handle customer data, compliance documents, or financial analysis, hallucination rate matters more than benchmark leaderboard position.

## What this means for India's AI builders

For Indian AI startups, Nemotron 3 Ultra changes the calculus on build-versus-buy. Companies like Sarvam AI in Bangalore, which is building Indian-language AI models, or Krutrim, Ola's AI venture, now have access to a frontier-class base model with open training recipes — the kind of foundation that previously required tens of millions in compute budget to create.

The model runs on a single 8-GPU node with NVIDIA's latest hardware, or a 16-GPU H100 cluster — infrastructure that is increasingly available at Indian cloud providers and data centres being built by Reliance and Adani.

NVIDIA's Bangalore and Pune R&D centres, which employ thousands of Indian engineers, contributed to the Nemotron family's development. For those engineers, this is not just a product release — it is career-defining, published research with their names on it, in the open, advancing the state of the art in how AI models reason over long contexts."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "IIT Delhi and Cadence Just Opened a Chip Design Lab. It Could Train India's Missing Semiconductor Workforce.",
        "subheadline": "The new innovation lab gives students access to the exact EDA tools used by Intel and TSMC — and offers pre-seed startups a path to first silicon.",
        "slug": make_slug("iit-delhi-cadence-semiconductor-innovation-lab"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's semiconductor mission has six approved fabs and a $10 billion government commitment — but the country faces a projected shortage of 75,000 chip design engineers by 2027. For NRI engineers at Cadence, Synopsys, Intel, and Qualcomm, this lab represents the kind of talent pipeline that could eventually supply their teams with India-trained engineers who have worked with the same tools they use daily. For diaspora professionals considering a return to India, the semiconductor sector is becoming a viable career destination — not just in MNC R&D centres but in homegrown startups getting incubation support and a path to tape-out.",
        "tags": ["iit-delhi", "cadence", "semiconductor", "chip-design", "india-semiconductor-mission", "eda-tools"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://thehindubusinessline.com"},
            {"name": "Communications Today", "url": "https://communicationstoday.co.in"},
            {"name": "FoneArena", "url": "https://fonearena.com"},
            {"name": "Semiconductor for You", "url": "https://semiconductorforu.com"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/2105927/pexels-photo-2105927.jpeg",
        "image_caption": "A computer processor chip with gold pins — the kind of component that IIT Delhi students will now learn to design",
        "image_attribution": "Pexels",
        "body": """India has approved six semiconductor fabrication plants, committed over $10 billion in government incentives, and spent two years telling the world it is serious about chips. There is one problem that no amount of money can solve overnight: the country does not have enough engineers who know how to design them.

The gap, by most industry estimates, is roughly 75,000 chip design professionals by 2027. India produces plenty of electrical engineering graduates. What it lacks are engineers who have spent years working with the specific electronic design automation tools — EDA software from companies like Cadence and Synopsys — that are used to design every chip in your phone, your laptop, and the data centre running this article.

On June 4, Cadence and the Indian Institute of Technology Delhi announced a step toward closing that gap: the IIT Delhi-Cadence Innovation Lab, a centre of excellence that gives students, researchers, and early-stage startups access to over 200 industry-grade Cadence EDA tools — the exact same software used by design teams at Intel, TSMC, Samsung, and Qualcomm.

## Real tools, not textbook exercises

The distinction matters. Most Indian engineering curricula teach semiconductor theory — transistor physics, VLSI architecture, digital logic — using open-source or academic-grade simulation tools that bear little resemblance to what a working chip designer uses on day one at a job. The gap between classroom and industry has been a persistent complaint from employers.

The IIT Delhi-Cadence lab bridges this by embedding Cadence-developed courses that combine theoretical instruction with project-based labs using production tools. Students will work on real design challenges across four domains: chip design verification, digital implementation, analogue design, and system design and analysis. Guest lectures from Cadence professionals and industry practitioners keep the curriculum aligned with current technology roadmaps.

The AI integration is worth noting. The lab emphasises what Cadence calls "design with AI" — using machine learning to accelerate EDA workflows. This is the direction the entire semiconductor design industry is heading. AI-assisted place-and-route, timing closure, and verification are becoming standard at leading design houses. Students trained on these workflows will arrive at their first job already fluent in the tools reshaping the industry.

## A path from IIT lab to first silicon

The most ambitious element of the new lab is its startup incubation programme. Pre-seed chip design startups — the kind of companies that have a promising architecture on paper but cannot afford the millions in licensing fees and fabrication costs needed to reach first tape-out — can apply for support through the lab.

Cadence is offering these startups a low-cost route to their first working prototype, handling the EDA tool access that would otherwise be a prohibitive expense. For context, Cadence's Virtuoso and Innovus tool suites can cost hundreds of thousands of dollars in annual licenses. A pre-seed startup with three engineers and an angel round simply cannot afford them. This programme removes that barrier.

The lab is also introducing an Early Master's Research pathway for select fourth-year undergraduates from IITs and NITs. Mentored jointly by Cadence experts and IIT Delhi faculty, these students will work on advanced semiconductor research before they even begin formal graduate programmes — creating a pipeline of researchers who have already published and prototyped before entering the workforce.

## India's semiconductor talent pipeline has a diaspora problem

India's chip design workforce exists — it is just mostly employed abroad. An estimated 20 per cent of semiconductor engineers at American chip companies are of Indian origin. Cadence itself employs thousands of engineers in India across its Noida, Bangalore, and Hyderabad R&D centres. Synopsys, its primary competitor, has similarly large Indian operations.

The IIT Delhi-Cadence lab is designed to grow the domestic pipeline so that India's new fabs — the Tata Electronics plant in Dholera, the Micron facility in Gujarat, the HCL-Foxconn plant near Jewar — have trained engineers to staff them. Without that talent pipeline, the hardware investments risk becoming expensive shells.

For NRI chip professionals at Cadence, Intel, Qualcomm, and the broader semiconductor industry, this lab represents something more personal: the emergence of India as a place where serious chip design happens, not just verification and physical design services. The country that trained them is finally building the infrastructure to keep the next generation at home.

The lab aligns with India's Semiconductor Mission and the Design-Linked Incentive scheme, both of which aim to expand domestic chip design capacity. If it works — if the model scales to other IITs, NITs, and private universities — India might finally have an answer to its most persistent semiconductor bottleneck: not capital, not fabs, but the engineers who know how to fill them."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
