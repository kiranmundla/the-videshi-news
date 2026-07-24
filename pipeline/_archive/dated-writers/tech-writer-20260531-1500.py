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
        "headline": "Nvidia Is About to Launch Its First Laptop Chip in a Decade. Your Next Work PC Might Run on It.",
        "subheadline": "Jensen Huang and Satya Nadella are joining forces to put Nvidia's ARM-based N1X processor into Windows laptops — threatening Intel, AMD, and Qualcomm in one swing.",
        "slug": make_slug("nvidia-n1x-laptop-chip-microsoft-windows-arm-computex"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella's Microsoft is a co-architect of this move. Tens of thousands of Indian engineers at Microsoft, Nvidia, Intel, AMD, and Qualcomm will feel the competitive shockwave. For H-1B holders at Intel or AMD, an Nvidia-led ARM shift could reshape which chip teams are hiring — and which are cutting.",
        "tags": ["nvidia", "microsoft", "arm", "laptops", "computex", "satya-nadella", "chips"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/first-windows-pc-powered-nvidia-chips-debut-next-week-axios-reports-2026-05-31/"},
            {"name": "Axios (via ainvest)", "url": "https://www.ainvest.com/news/nvidia-and-microsoft-to-unveil-first-windows-pcs-powered-by-nvidia-chips-at-industry-conferences-next-week-2605/"},
            {"name": "WCCFTech", "url": "https://wccftech.com/computex-2026-will-be-nvidias-biggest-event-of-the-year-heres-what-to-expect/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """For the first time since it abandoned its Tegra line, Nvidia is putting its name on a laptop processor. And this time, it is not settling for a supporting role.

Microsoft and Nvidia are expected to unveil the first Windows PCs powered by Nvidia's N1X chip at Computex in Taipei and Microsoft's Build conference in San Francisco next week. Reuters confirmed that Microsoft's Surface lineup and Dell will be among the first manufacturers shipping devices with Nvidia silicon as the primary processor — not a discrete GPU bolted onto someone else's CPU, but the whole package.

The coordinated tease was not subtle. On Friday, the official X accounts of Windows, Nvidia, and Arm posted the same three words — "A new era of PC" — alongside coordinates pointing to Taipei Music Center, where Jensen Huang will deliver his keynote on Monday.

## What the N1X actually is

The N1X is an ARM-based APU (accelerated processing unit) that combines 20 CPU cores with 6,144 CUDA cores — roughly equivalent to a desktop RTX 5070's GPU — all sharing a unified memory pool over a 256-bit LPDDR5X bus. In theory, this allows users to allocate enormous amounts of VRAM from shared memory to run 100-billion-parameter AI models locally, something AMD's Strix Halo can already do in its 128 GB configuration.

Nvidia's advantage is software. CUDA remains the dominant framework for AI inference workloads on consumer hardware. While AMD has made real progress with ROCm, most AI applications — image generation, local LLMs, video processing — still assume CUDA is available. An N1X laptop with 128 GB of unified memory and native CUDA support would be, for many AI developers, the first truly portable AI workstation.

ASUS, Dell, and Lenovo have either leaked or hinted at N1X models. Pricing is expected to start north of $3,000, putting these firmly in the professional and creator tier rather than the consumer mainstream.

## Why this is a four-way war

The laptop processor market has been a two-player game — Intel and AMD — for two decades. Apple broke that duopoly in 2020 with M-series silicon. Qualcomm followed with Snapdragon X chips for Windows on ARM. Now Nvidia makes it a five-way contest.

For Intel, which is already burning through cash on its foundry turnaround, another ARM competitor in its core PC business is the last thing it needs. For Qualcomm, which just launched the Snapdragon C at the $300 price point, Nvidia's entry at the premium end squeezes its growth ceiling. For AMD, whose Strix Halo and Gorgon Halo chips target the same high-end AI workstation niche, the competition just got a name that enterprise buyers trust instinctively.

## The Indian engineering angle

This story is really about two companies run by Indian-origin CEOs — Satya Nadella's Microsoft and, on the other side of the table, the chipmakers whose lunch is being eaten. Qualcomm's Snapdragon X was designed by a team led by Indian-origin engineer Mandar Deshpande. AMD's Lisa Su has built one of the deepest engineering benches in the industry, with significant Indian representation in Austin, Santa Clara, and Hyderabad.

For the tens of thousands of Indian engineers employed across Intel, AMD, Qualcomm, Nvidia, and Microsoft in the United States — many on H-1B or green card tracks — this competitive reshuffling has direct career implications. If ARM-based Windows laptops take meaningful share from x86, the teams designing legacy architectures could face restructuring. If Nvidia's entry catalyses a wave of AI-optimised laptop software, the developers building for CUDA will be in higher demand than ever.

Microsoft is also expected to unveil software enabling AI agents to perform tasks locally on Windows PCs, according to the Axios report. That means the N1X is not just a hardware play — it is the compute layer for Nadella's vision of Copilot running everywhere, including offline.

## What NRI investors should watch

Nvidia stock closed Friday at $211.14, down 1.45%, but up 15% year-to-date. The Computex keynote on Monday evening (8 PM Pacific, Sunday May 31) could move the stock significantly if the N1X benchmarks impress. Intel, trading near 52-week lows, and Qualcomm, which has underperformed despite Snapdragon X's solid reviews, could face pressure.

The broader signal is harder to trade but more important: the era of one chip architecture dominating the PC is over. ARM, x86, and now Nvidia's CUDA-native hybrid are all competing for the same desk. For Indian professionals building careers around any one of these stacks, the next twelve months will determine which bets pay off."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic's Opus 4.8 Is the AI Model That Admits When It's Wrong. That Might Matter More Than Speed.",
        "subheadline": "The $965 billion AI lab shipped its most 'honest' model yet and kept its most dangerous one, Mythos, locked away. For Indian enterprises deploying Claude at scale, reliability just trumped raw performance.",
        "slug": make_slug("anthropic-opus-48-honest-ai-mythos-indian-enterprise"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian IT firms including TCS and Infosys are increasingly deploying Claude for enterprise workflows. Anthropic's India expansion under Sangeeta Bavi makes Opus 4.8's reliability-first approach directly relevant to the thousands of Indian developers building agentic AI systems. For NRI investors watching Anthropic's pre-IPO trajectory at $965B valuation, the model quality story is inseparable from the business story.",
        "tags": ["anthropic", "claude", "ai-models", "opus", "enterprise-ai", "indian-it"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fast Company", "url": "https://www.fastcompany.com/91355678/anthropic-just-topped-openai-on-major-metric-ahead-rival-ipos"},
            {"name": "WebProNews", "url": "https://www.webpronews.com/anthropic-overtakes-openai-at-965-billion-as-opus-4-8-accelerates-the-ai-race/"},
            {"name": "The Street", "url": "https://www.thestreet.com/technology/anthropic-drops-new-claude-model-as-openai-ipo-race-heats-up"},
            {"name": "Talk Android", "url": "https://talkandroid.com/ai-wars-intensify-as-openai-cuts-models-and-anthropic-releases-a-new-flagship/"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Anthropic released Claude Opus 4.8 on Wednesday, less than six weeks after its previous version. The headline metric is not speed or benchmark dominance — though it has both — but honesty. The model is roughly four times less likely than its predecessor to let flawed code or unsupported claims pass without flagging them. In an industry addicted to bigger and faster, Anthropic is betting that more careful will win the enterprise.

The release landed alongside a $65 billion Series H funding round that values Anthropic at $965 billion, surpassing OpenAI's $852 billion. Led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital, the round nearly tripled Anthropic's valuation from $380 billion in February. To put the number in perspective: only 21 national economies produce more than $1 trillion in annual GDP. A five-year-old AI lab now sits just below that threshold.

## What Opus 4.8 actually does differently

The model leads on several agentic benchmarks — it outperforms OpenAI's GPT-5.5 and Google's Gemini 3.1 Pro on agentic coding, financial analysis, and computer-use tasks. It became the first model to break 10 per cent all-pass on the Legal Agent Benchmark and scores 84 per cent on Online-Mind2Web for browser-based task automation.

But the real differentiator is behavioural. Bridgewater Associates, one of the world's largest hedge funds, said the biggest improvement is "Opus 4.8's tendency to proactively flag issues with the inputs and outputs of an analysis, something other models routinely missed and left to the users to catch." In enterprise deployments where a model runs hundreds of financial calculations or migrates tens of thousands of lines of code, a model that says "this looks wrong" before you deploy is worth more than one that runs three per cent faster.

Anthropic has also introduced two new features: "effort control," which lets users dial up or down how much computational effort Claude applies to a response, and "dynamic workflows," which orchestrate hundreds of sub-agents for complex, long-running tasks like massive code migrations.

## The Mythos question

The more intriguing development is what Anthropic did not ship. Mythos, the company's most powerful model, remains restricted to a select group of trusted partners and government agencies. The reason: Mythos demonstrated an exceptional ability to discover and exploit cybersecurity vulnerabilities. Anthropic has been testing it in controlled environments and says safeguards are progressing toward broader release "in the coming weeks."

This creates a strange dynamic. Anthropic is simultaneously marketing reliability and restraint while sitting on a model that, by its own admission, is too dangerous for general use. The tension is deliberate — it positions Anthropic as the responsible lab in contrast to competitors who ship first and patch later. Whether that positioning holds when revenue targets meet board pressure is a separate question.

## Why Indian enterprises should care

About 80 per cent of Anthropic's revenue comes from enterprise products, mostly flowing through cloud computing partners like Amazon Web Services. Indian IT services firms — TCS, Infosys, Wipro, HCL Tech — are increasingly integrating Claude into client workflows. OpenAI's own Codex platform has seen a 27x surge in weekly users in India since the start of 2026, with TCS and Infosys among its enterprise partners. But for mission-critical enterprise deployments — financial analysis, legal document review, large-scale code migration — the model that catches its own mistakes has a structural advantage over the model that is merely fastest.

Anthropic's India push is accelerating. Sangeeta Bavi was named to lead the company's India operations earlier this month, focusing on both enterprise sales and startup ecosystem development. Anthropic's Claude Code for knowledge workers, branded as Cowork, has already disrupted the software services sector — it is one reason Indian IT stocks hit three-year lows this month.

## The pre-IPO calculus

Both Anthropic and OpenAI are expected to file for IPOs later this year. For NRI investors, the valuation gap is notable but misleading. Anthropic recognises cloud revenue on a gross basis — if an AWS customer buys $1 of Claude API usage, Anthropic records the full dollar. OpenAI uses net revenue recognition through Azure, recording only its share. Same market, different accounting, vastly different headline numbers.

What is not different: the pace at which these companies are scaling. Anthropic's annual recurring revenue has overtaken OpenAI's, according to CNBC. The AI model race is no longer just about who builds the smartest system. It is about who builds the most trustworthy one. For the millions of Indian developers and IT professionals whose livelihoods depend on which AI platform their employers adopt, the answer to that question is not academic."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "OpenAI's Codex Usage in India Has Surged 27x This Year. Five Million Developers Should Be Paying Attention.",
        "subheadline": "India is now among the top five countries globally for Codex adoption, with TCS, Infosys, and Razorpay among enterprise partners. Nandan Nilekani says AI will create 78 million jobs. The numbers suggest something more complicated.",
        "slug": make_slug("openai-codex-india-27x-surge-tcs-infosys-developers"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's 5 million software developers — many aspiring to work at FAANG companies or Indian IT majors — are the workforce most directly affected. For H-1B holders and OPT students in the US, AI coding tools are reshaping which skills employers value. For NRIs watching Indian IT stocks, the Codex adoption data is both a growth signal and an existential warning.",
        "tags": ["openai", "codex", "india-tech", "tcs", "infosys", "ai-coding", "developers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://storyboard18.com/how-it-satisfies/agentic-platform-codex-users-in-india-surged-27x-since-start-of-2026-says-openai-61946.htm"},
            {"name": "Inshorts", "url": "https://inshorts.com/news/codex-weekly-users-surged-27x-in-india-since-start-of-2026-openai-1748579100"},
            {"name": "Inshorts (Nilekani)", "url": "https://inshorts.com/news/infosys-chairman-predicts-78-cr-new-jobs-due-to-ai-by-2030-1748569300"},
            {"name": "LinkedIn Analysis", "url": "https://www.linkedin.com/pulse/i-just-watched-it-services-industry-concede-future/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36706459/pexels-photo-36706459.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """OpenAI disclosed on Friday that weekly users of its AI-powered coding agent Codex in India have increased by 27 times since the start of 2026. Daily interactions with the platform have grown by more than 20 times since late April alone. India is now among the top five countries globally for Codex adoption — a statistic that should make every Indian software professional sit up, whether they work in Bengaluru, Hyderabad, or San Jose.

The enterprise adoption pipeline is the part that matters most. OpenAI confirmed that TCS, Infosys, and Razorpay are among the companies driving Codex usage in India, deploying it across software engineering and enterprise workflow operations. When the country's two largest IT services firms — which collectively employ over 800,000 people — are actively integrating an AI coding agent into their workflows, the implications ripple through an entire industry.

## What Codex actually does

Codex is OpenAI's agentic coding platform, distinct from the ChatGPT interface that most people associate with the company. It operates as an autonomous agent: given a task description, it writes code, runs tests, debugs failures, and iterates — often completing in minutes what a junior developer might take hours to produce. The "agentic" part is critical: Codex does not just suggest code snippets. It executes multi-step development workflows with minimal human oversight.

For a senior engineer, Codex is a productivity multiplier. For a junior developer whose primary contribution was writing boilerplate code and running through test matrices, it is a direct substitute. The distinction matters because India's IT services industry was built on the availability of large numbers of capable junior engineers willing to work at rates that made offshoring irresistible to Western enterprises.

## Nilekani's optimistic counter

Infosys chairman Nandan Nilekani offered the industry's official counter-narrative on Friday. He said AI will create 78 million new jobs by 2030 and that Infosys plans to use AI-driven productivity gains to grow revenue rather than cut headcount. The framing is familiar — it is the same argument the industry made about automation in the 2010s — but this time the productivity gains are not incremental. A five-person team augmented by modern AI tooling now ships what fifty engineers shipped a decade ago, according to industry analysis.

The tension between these two narratives — AI as job creator versus AI as labour substitute — is not abstract for Indian IT workers. Infosys CEO Salil Parekh earned $8.69 million in fiscal 2026, a 2.5 per cent increase, while the company forecast revenue growth of just 1.5 to 3.5 per cent for fiscal 2027. The gap between executive compensation growth and revenue growth tells its own story about where the value in AI-augmented services is accruing.

## The Indian IT services dilemma

The structural challenge is straightforward. India's $315 billion IT sector charges clients by the hour or by the engineer. AI tools like Codex compress the number of hours and engineers required to deliver a given project. If a migration that once required 50 engineers for six months now requires 10 engineers and Codex for three months, the client pays less. The services firm either absorbs the revenue decline or finds new, higher-value work to sell.

Both paths are happening simultaneously. TCS was named America's most reliable IT services company in Newsweek's 2026 rankings. Wipro's ADR surged 18 per cent on a single day last week after landing a ServiceNow agentic AI deal. The companies that can sell AI implementation and orchestration — rather than bodies — are finding premiums. The ones still running on the old model are watching margins compress.

OpenAI's enterprise push is accelerating this reckoning. Earlier this month, the company announced a services-led venture that sent Indian IT stocks to three-year lows. The message was unambiguous: OpenAI is not content to sell the tools. It wants to sell the services too.

## What this means for developers

For the roughly five million software developers working in India, and the hundreds of thousands of Indian-origin developers in the United States, the Codex numbers are a skills signal. Fluency with AI coding tools is no longer optional — it is table stakes. The developers who thrive will be those who can architect systems, evaluate AI-generated code, and solve problems that Codex cannot: ambiguous requirements, cross-functional coordination, and domain-specific engineering.

For OPT students and H-1B holders competing in an increasingly tight American job market — where some applicants report submitting over 1,500 applications without a callback — the calculus is shifting. Employers are less likely to sponsor visas for roles that AI can partially automate. They are more likely to sponsor for roles that require judgement, domain expertise, and the ability to manage AI-augmented workflows.

Codex usage surging 27x in India is not just an adoption metric. It is a preview of how the next decade of Indian technology employment will be structured. The question is whether India's developers — and the companies that employ them — are building for that future or hoping it arrives slowly."""
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
