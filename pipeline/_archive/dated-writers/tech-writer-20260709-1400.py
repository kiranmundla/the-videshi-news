#!/usr/bin/env python3
"""Tech writer — 2026-07-09 14:00 PT run. Three articles."""

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


# ── Article 1: Meta Iris AI Chip ──────────────────────────────────────────

art1_body = """Meta Platforms is about to cross a threshold that most of Big Tech has been chasing for years: manufacturing its own artificial intelligence chip at scale. According to an internal memo reviewed by Reuters, the company will begin production of its custom AI accelerator, code-named "Iris," in September — the clearest sign yet that the era of total reliance on Nvidia's GPUs is ending.

Iris is the third generation of Meta's MTIA programme — short for Meta Training and Inference Accelerators — and it represents the most advanced in-house silicon the company has ever attempted. Built on TSMC's cutting-edge 3-nanometre process with design support from Broadcom, the chip passed bug testing in just six weeks with no major issues. That speed matters. Meta's custom chip ambitions have floundered for more than half a decade; Iris's smooth path to production suggests the engineering team has finally found its stride.

## The Numbers Behind the Ambition

The stakes are staggering. Meta currently operates roughly seven gigawatts of computing power across its global data centre fleet. With Iris and its successors, the company plans to double that to 14 gigawatts by next year. To put that in perspective, 14 gigawatts could power a small country.

Meta isn't replacing Nvidia overnight. Iris is designed to *augment* the GPUs it already buys in bulk from Nvidia and AMD, specifically optimised for the deep learning recommendation models that decide what 3.3 billion people see on Facebook, Instagram, and WhatsApp every day. But the direction is unmistakable: Meta wants to design the silicon that runs its own AI, not rent it.

The company has already committed to deploying one gigawatt of MTIA capacity under an expanded partnership with Broadcom that runs through 2029. Three more chip generations — the MTIA 400, 450, and 500 — are scheduled to roll out roughly every six months through 2027, each with progressively higher memory bandwidth for the explosion in generative AI inference workloads.

## Why This Matters to the Diaspora

Meta is one of the largest employers of Indian engineers in Silicon Valley. Thousands of H-1B visa holders work across its AI research, infrastructure, and product teams — the very teams building and deploying chips like Iris. A shift toward custom silicon doesn't eliminate those jobs, but it reshapes them. The skill sets that matter are evolving from GPU programming toward ASIC design, chip architecture, and specialised inference optimisation.

Broadcom, Meta's chip design partner, has its own deep Indian engineering bench. And TSMC's emerging operations in India — including the Tata Electronics fab in Dholera, Gujarat — mean that some of the manufacturing supply chain for chips like Iris may eventually run through Indian facilities.

For NRI investors tracking META stock, the custom silicon programme is a double-edged bet. It promises lower per-inference costs and greater independence from Nvidia's pricing power. But as Emarketer analyst Jacob Bourne noted, "in the near term it's accompanied by enormous capex, growing financing needs, and more questions about when those investments translate into meaningful returns."

Meta's AI spending is already eye-watering — the company has projected capital expenditure of $60 billion to $65 billion this year alone. Iris is a bet that building your own chips is cheaper than buying someone else's at scale. For the Indian professionals designing those chips and the investors weighing that trade-off, the September production date is the first real proof point."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Is About to Manufacture Its Own AI Chip. It Took Five Years to Get Here.",
    "subheadline": "Code-named Iris, the custom accelerator will enter production in September as Meta races to double its computing power to 14 gigawatts and reduce its dependence on Nvidia.",
    "slug": make_slug("meta-iris-ai-chip-production-broadcom-tsmc"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Meta employs thousands of Indian engineers on H-1B visas across its AI and infrastructure teams; the shift to custom silicon reshapes career demand toward chip design, while Broadcom's Indian engineering bench and India's emerging fab ecosystem stand to benefit.",
    "tags": ["meta", "custom-silicon", "ai-chips", "broadcom", "tsmc", "nvidia", "semiconductor"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-put-ai-chip-into-production-september-it-looks-double-computing-capacity-2026-07-09/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/meta-to-put-ai-chip-into-production-in-september/article69787251.ece"},
        {"name": "TechSpot", "url": "https://www.techspot.com/news/107903-meta-doubles-down-custom-ai-chips-broadcom-deal.html"},
        {"name": "The Register", "url": "https://www.theregister.com/2025/03/12/meta_custom_ai_chips/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg",
    "image_caption": "A close-up of microchips and circuits on a motherboard, illustrating the custom silicon Meta is designing in-house",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ── Article 2: Nvidia Vera CPU ────────────────────────────────────────────

art2_body = """Nvidia has spent the AI boom selling GPUs — the specialised processors that train and run the world's most powerful AI models. Now it wants to sell the *other* chip in the data centre, too. Its new Vera CPU, purpose-built for the age of AI agents, just landed its latest high-profile customer: Perplexity, the AI search startup valued at $20 billion.

Perplexity joins a list that already includes OpenAI, Anthropic, SpaceX, and Oracle. Jensen Huang's company expects Vera to generate $20 billion in standalone CPU revenue this fiscal year, with a total addressable market it pegs at $200 billion. That puts Nvidia on a direct collision course with Intel and AMD, the two companies that have dominated server CPUs for decades.

## Built for Machines That Never Sleep

The pitch is simple but potent. Traditional CPUs from Intel and AMD were designed for human users — people who type, click, pause, and context-switch. AI agents don't. They run continuous loops: execute a task, evaluate the result, decide what to do next, repeat. There are no coffee breaks.

Vera's 88 custom Olympus cores, built on ARM architecture, are engineered for exactly this pattern. In Perplexity's testing, the chip completed AI agent coding tasks roughly 1.5 times faster than conventional CPUs. "Vera really stood out to us as just like a dead-on fit for a lot of the core workloads that we have," said Nate Kupp, Perplexity's VP for Enterprise and Infrastructure.

The technical specifications underline the point: 1.2 terabytes per second of LPDDR5X memory bandwidth at under 40 watts of memory power, a monolithic compute die delivering 3.4 terabytes per second of core-to-core bandwidth — more than three times any competing data centre CPU — and a 50 per cent IPC improvement over Nvidia's prior-generation Grace chip. Independent benchmarks from Phoronix called it "the most performant ARM Linux server processor" ever tested, with a 10 per cent advantage over AMD's high-frequency EPYC 9575F.

## The Bigger Play

Vera is not just about winning CPU benchmarks. It is the centrepiece of Nvidia's strategy to own the entire data centre compute stack — GPUs, CPUs, networking, and software — rather than ceding the CPU layer to Intel and AMD. With AI companies like DeepSeek and Meta now designing their own AI accelerators, Nvidia needs new revenue streams to sustain its growth trajectory. CPUs are the obvious next frontier.

The timing is sharp. Intel and AMD shares have outperformed Nvidia in recent months as investors rotated out of AI's biggest winners. Vera is Nvidia's answer: a product that exploits a workload category — agentic AI — where its rivals' existing architectures are structurally disadvantaged.

## What Indian Engineers Should Watch

The Vera CPU war will be fought partly in India. Nvidia's Indian engineering centres — particularly in Bengaluru and Hyderabad — are central to its chip design and software ecosystem. Intel and AMD have similarly deep Indian operations. The professionals working on server CPU architecture at any of these three companies are now in the most contested market in semiconductors.

For NRI investors, the CPU battle adds a new variable to the Nvidia thesis. The GPU story is well-understood and, some argue, fully priced. The CPU story — $20 billion this year, $200 billion addressable — is what could reignite growth if adoption scales as Nvidia projects. But Intel and AMD are not standing still. AMD's next-generation EPYC Venice, based on Zen 6, is already in mass production. Qualcomm is pushing its own data centre ARM chips. The agentic AI CPU market is about to get very crowded."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Nvidia Built a CPU for AI Agents That Never Sleep. Perplexity Just Signed Up.",
    "subheadline": "The Vera chip — already chosen by OpenAI, Anthropic, and SpaceX — runs agentic AI workloads 1.5 times faster than traditional processors. Nvidia expects $20 billion in CPU sales this year.",
    "slug": make_slug("nvidia-vera-cpu-perplexity-ai-agents-intel-amd"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Nvidia, Intel, and AMD all run major chip design operations in Bengaluru and Hyderabad; the CPU war directly shapes career demand for thousands of Indian semiconductor engineers, while NRI investors weigh Nvidia's new revenue stream against Intel and AMD's counterattack.",
    "tags": ["nvidia", "vera-cpu", "ai-agents", "perplexity", "intel", "amd", "semiconductor", "arm"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/perplexity-says-it-plans-use-nvidias-new-cpu-2026-07-08/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/nvidia-stock-price-perplexity-vera-cpu-a3b2c1d0"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/deeptech/why-perplexity-is-choosing-nvidias-vera-cpu-over-traditional-intel-and-amd-chips"},
        {"name": "NVIDIA Blog", "url": "https://blogs.nvidia.com/blog/vera-cpu-benchmarks/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
    "image_caption": "Nvidia CEO Jensen Huang, whose company is challenging Intel and AMD with its Vera CPU designed for the agentic AI era",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}


# ── Article 3: India Data Centre Boom ─────────────────────────────────────

art3_body = """When Sundar Pichai took the stage at the India AI Impact Summit in February, he announced that Google would build a gigawatt-scale AI hub in Visakhapatnam — the quiet coastal city he used to pass through on the Coromandel Express as a student. Microsoft committed $17.5 billion, its largest-ever investment in Asia. Meta, Amazon, and OpenAI are all building or expanding. India is becoming a global data centre superpower, and unlike in America, almost nobody is fighting it.

That is the central finding of a recent Barron's investigation into India's data centre surge. Capacity is expected to grow tenfold over the next decade, according to Nomura. India currently accounts for 1.3 per cent of the world's data centre capacity; within five years, that figure is projected to reach 3 per cent. "That may not sound like a big shift, but these are percentages of enormous numbers," said John Dinsdale, chief analyst at Synergy Research Group.

## The Policy Machine

What makes India different is the policy environment. In the United States, communities wage fierce battles against data centre construction — fighting noise, water usage, energy demands, and disrupted landscapes. Some win. India operates on a different model entirely: data centres get approved without public hearings, and the government has rolled out an array of incentives to accelerate construction.

The most striking is a tax provision declared in February: zero taxes until 2047 on overseas services by foreign companies that operate data centres in India. That is a twenty-year runway of tax-free operations for any American or European cloud provider willing to build on Indian soil. Combined with cheaper land, streamlined approvals, and a government that has made AI infrastructure a national priority, the incentive structure is hard to match anywhere else in the developing world.

"Work with India and deliver for all," Prime Minister Narendra Modi said at an AI summit in June — a line that doubles as both invitation and instruction.

## Why Big Tech Wants India

The business case is straightforward. Data centres must be physically close to their users to minimise latency — the delay that makes a chatbot feel slow or a video call stutter. Indians are the second-largest users of both ChatGPT and Claude globally. Serving them from data centres in Virginia or Singapore adds unnecessary milliseconds and cost.

Google's $15 billion investment will fund three data centre campuses in Vizag, anchored by an international subsea cable gateway that connects India to the United States and the broader southern hemisphere. Microsoft's commitment spans multiple Indian cities. Amazon Web Services has been expanding its Mumbai and Hyderabad regions steadily. The combined investment from these companies alone exceeds $50 billion.

The construction is also pulling in a network of Indian infrastructure companies. Real estate developers, power companies, and cooling technology firms are building the physical layer. Engineering talent is flowing from IT services into data centre operations and cloud architecture.

## The Diaspora Calculation

For Indians in the United States, the data centre boom creates an unusual set of intersections. The companies they work for — Google, Microsoft, Meta, Amazon — are simultaneously their employers in America and the largest infrastructure investors in the country many left behind. That dynamic shapes everything from career mobility (transfers to India operations are increasingly viable) to investment decisions (Indian real estate and infrastructure near data centre clusters is appreciating rapidly).

NRI investors who have watched India's semiconductor ambitions with cautious interest now have a different asset class to evaluate. Data centres are not speculative chip fabs — they are operational infrastructure with contractual tenants and predictable revenue. The zero-tax provision through 2047 makes the economics even more compelling for companies listed on Indian exchanges that service these facilities.

The risks are real. India's power grid is stretched. Water scarcity is acute in several states where data centres are planned. And the absence of public hearings, while accelerating construction, means environmental and community concerns are being deferred rather than resolved.

But the trajectory is set. The world's biggest technology companies have collectively bet tens of billions of dollars that India's data centre market will be one of the largest on Earth within a decade. For the diaspora, the question is no longer whether this will happen — it is how to position for it."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Is Building the World's Next Great Data Centre Hub. Nobody Is Allowed to Object.",
    "subheadline": "Microsoft, Google, Meta, and Amazon are pouring more than $50 billion into Indian data centres. A zero-tax regime through 2047 and no public hearings are accelerating construction at a pace the West cannot match.",
    "slug": make_slug("india-data-center-boom-microsoft-google-meta-tax"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "NRI professionals at Google, Microsoft, and Meta are seeing their employers become India's largest infrastructure investors, opening career transfer paths and investment opportunities in Indian data centre real estate and operations.",
    "tags": ["data-centers", "india", "microsoft", "google", "meta", "amazon", "cloud-infrastructure", "ai-infrastructure"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Barron's", "url": "https://www.barrons.com/articles/india-data-center-hub-ai-big-tech-7a8b9c0d"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indian-shares-advance-led-by-it-easing-us-rate-hike-worries-2026-07-04/"},
        {"name": "Google Blog", "url": "https://blog.google/inside-google/message-ceo/sundar-pichai-ai-impact-summit-2026/"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/info-tech/google-unveils-india-america-sub-sea-cable-initiative-to-boost-ai-connectivity/article69243889.ece"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4508751/pexels-photo-4508751.jpeg",
    "image_caption": "Server racks inside a modern data centre, the kind of infrastructure India is building at unprecedented scale",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}


# ── Insert ────────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
