#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
        "headline": "OpenAI Built Its Own AI Chip and Called It Jalapeño. The Real Target Is Nvidia's Fattest Margin.",
        "subheadline": "Designed with Broadcom and fabbed at TSMC, the inference chip promises 50% cheaper compute — and a quiet escape from the GPU that made every Indian AI engineer's resume valuable.",
        "slug": make_slug("openai-broadcom-jalapeno-custom-ai-chip-nvidia-inference-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers staff the inference, infra, and silicon teams at OpenAI, Broadcom, and TSMC's US operations — and a shift from buying Nvidia GPUs to designing custom chips reshapes which skills get hired and which get commoditized.",
        "tags": ["ai", "semiconductors", "openai", "broadcom", "nvidia", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-unveils-custom-chip-it-designed-with-broadcom-2026-06-24/"},
            {"name": "Morningstar / MarketWatch", "url": "https://www.morningstar.com/news/marketwatch/20260624/broadcom-unveils-a-custom-chip-for-openai-as-it-challenges-nvidias-dominance"},
            {"name": "TheStreet", "url": "https://www.thestreet.com/technology/broadcom-gets-major-openai-boost-in-ai-chip-race"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/34924856/pexels-photo-34924856.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A semiconductor wafer under magnification, the kind of inference silicon now being custom-designed by AI labs.",
        "image_attribution": "Pexels",
        "body": """OpenAI spent three years buying Nvidia's graphics chips by the warehouse-load to run ChatGPT. On Wednesday it showed off the way out: its own custom processor, designed with Broadcom and manufactured by Taiwan's TSMC. The company gave it a name that is hard to take entirely seriously — **Jalapeño** — and a job that is deadly serious: cutting the cost of answering every query a chatbot fields.

Broadcom shares rose around 2% on the news; Nvidia slipped a fraction. Beneath the modest market reaction is a structural shift that matters to anyone whose career runs through Silicon Valley's AI machine — which describes a large share of the Indian diaspora.

## What Jalapeño actually is

Jalapeño is an ASIC — an application-specific integrated circuit. Unlike Nvidia's general-purpose GPUs, which can train and run almost any model, an ASIC trades flexibility for a single talent done cheaply. Jalapeño's talent is **inference**: the act of generating responses, the part of AI that happens billions of times a day once a model is trained.

Broadcom CEO Hock Tan told Reuters that early samples are running at roughly **50% lower cost** than typical AI GPUs, and that the chip is "as good as" Nvidia's Blackwell line or Google's tensor processing units. OpenAI says samples are already crunching workloads in its labs against its GPT-5.3-Codex-Spark model, with deployment planned by year-end. Its engineers finished the design in about nine months — fast for silicon — partly by using AI tools to speed the work. Canada's Celestica will build the server systems; the chips and servers will be used only by OpenAI.

## Why the diaspora should read past the headline

For an Indian engineer at Google, Microsoft, or a startup, the instinct is to file this under "more AI infrastructure news." It is more than that, for three reasons.

First, **the skills market is rebalancing**. For years, the safe career bet was the Nvidia/CUDA stack — the software layer that made GPUs the only game in town. Custom silicon shifts value toward chip architecture, compiler engineering, and hardware-software co-design. Reuters reports that Meta, Amazon, and Alphabet are all leaning on Broadcom and Marvell for the same kind of work. Indian-origin engineers are heavily represented in exactly these inference and infrastructure teams; the ones who move toward silicon, not just model training, are positioning for the next decade.

Second, **TSMC is the choke point, and India is watching**. Jalapeño, like nearly every advanced chip, is fabbed in Taiwan. That single-country dependency is precisely the argument India's Semiconductor Mission and the Tata fab in Gujarat are built around. Every custom-chip announcement strengthens the case that fabrication, not design, is where geopolitical leverage now sits — a case that determines whether the semiconductor professionals among the diaspora build careers in Hsinchu, Phoenix, or Dholera.

Third, **it pressures the AI economics that justify diaspora salaries**. The entire AI hiring boom rests on the bet that inference can eventually be cheap enough to be everywhere. If labs can halve compute costs by designing their own chips, the path to profitability shortens — good for the companies, but also a reminder that the most expensive line item in AI is being engineered down. That discipline tends to flow through to headcount.

## The catch nobody is naming loudly

Designing a chip is the easy half. Funding the factories to make it at volume is the hard half. Reports suggest the first production phase could cost roughly $18 billion, and OpenAI cannot underwrite that scale alone — which is why partners and capacity guarantees keep surfacing in the coverage. Tan describes demand as effectively unlimited, yet the first phase still needs a buyer to absorb the risk. For all the bravado, OpenAI is still renting its independence.

## What's next

Jalapeño is the first step in a multi-generation roadmap, with the next version reportedly targeted for 2028. The lesson for the diaspora is not that Nvidia is finished — it dominates training, and will for years — but that the AI stack is fragmenting. The engineers who thrive will be the ones who can move between layers: model, compiler, and now silicon. For a community that has spent a decade making itself indispensable to one chip, the smart play is to stop betting on the chip and start betting on the layer below it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Wipro Just Posted $10.5 Billion in Revenue and Spun Up an 'AI-Native' Unit. The Subtext Is About Who It Stops Hiring.",
        "subheadline": "Stable margins, a new forward-deployed engineering arm, and small language models for clients — Wipro's FY26 results map the exact direction India's IT giants are pulling the diaspora's careers.",
        "slug": make_slug("wipro-fy26-results-ai-native-business-unit-it-services-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Hundreds of thousands of Indian engineers — many on H-1B and L-1 visas at Wipro's US client sites — are watching whether 'AI-native' delivery means a promotion path or a pink slip as the services model gets rebuilt around agents.",
        "tags": ["it-services", "wipro", "ai", "h1b", "indian-tech", "careers"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "StockTitan (Wipro 6-K SEC filing)", "url": "https://www.stocktitan.net/news/WIT/"},
            {"name": "The Register", "url": "https://www.theregister.com/2026/04/ai_deflation_indian_it/"},
            {"name": "Microsoft News (Source Asia)", "url": "https://news.microsoft.com/source/asia/2026/06/03/infosys-tcs-and-wipro-scale-microsoft-365-copilot-to-over-300000-employees/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Wipro_EC2%2C_Gate_6_entrance_view.jpg/1280px-Wipro_EC2%2C_Gate_6_entrance_view.jpg",
        "image_caption": "A gate entrance at Wipro's Electronic City campus in Bengaluru.",
        "image_attribution": "Wikimedia Commons",
        "body": """Wipro's annual numbers, disclosed this week in a US securities filing, read like a company that has stopped trying to grow fast and started trying to grow differently. FY26 revenue came in at **$10.5 billion** with margins the company called stable — respectable, unspectacular, and beside the point. The headline buried in the filing is structural: Wipro has stood up a dedicated **AI-Native Business & Platforms unit**, launched in April 2026, and says it is among the first of the big Indian IT firms to do so.

For the Indian diaspora, especially the large contingent working Wipro accounts at American banks, insurers, and retailers on H-1B and L-1 visas, this is the document to read closely. It describes the machine that issues their paychecks rebuilding itself.

## What "AI-native" means in practice

Strip the corporate language and the new unit does four things: modernize existing client platforms, build new AI-led businesses, develop **small language models (SLMs)** tailored to specific clients, and field "forward-deployed engineering" teams that embed with customers. That last phrase — borrowed from the AI-lab playbook — signals a shift away from the old model of staffing armies of generalist engineers and toward smaller, senior, AI-fluent teams that ship faster.

It is the same direction every major Indian IT firm is now pointed. In June, Microsoft said Infosys, TCS, and Wipro had each scaled Microsoft 365 Copilot past 100,000 employees — over 300,000 seats combined in under six months. The companies frame this as becoming "Frontier Firms" where AI agents work alongside people. The quieter reading is that the per-engineer output is being engineered upward, which means the same revenue needs fewer engineers.

## The deflation problem

Wipro's CFO has pointed to lower margins on some deals and the need for continuous operational improvement. Her peers have been blunter. HCL's CEO has warned of **"AI deflation"** — the expectation that future services revenue dips 3% to 5% as automation eats into billable hours. TCS's chief called the same phenomenon "degrowth." Infosys expects deflation to become a factor too.

For diaspora engineers, deflation is not an abstraction. The Indian IT services model has long run on a simple arithmetic: bill clients for hours, staff those hours with engineers, many deployed to the US on visas. When AI compresses the hours, it compresses the staffing — and the visa pipeline that has carried Indian talent to New Jersey, Texas, and the Bay Area for thirty years tightens with it. Recent data already shows India's IT majors filing for dramatically fewer H-1Bs than they once did, having localized US hiring and leaned on automation.

## Where the opportunity sits

The picture is not uniformly grim, and the diaspora professional reading this should resist the doom framing. Wipro's filing is explicit that the AI-native unit is a **growth bet**, not just a cost cut — building and scaling new platforms, owning product management and engineering end to end. Those are higher-value, higher-paid roles than the maintenance work AI is absorbing. The engineers who climb into them — the ones who can architect an SLM for a regulated bank, not just keep a legacy system running — are more valuable than they were a year ago, not less.

The split is the story. The same announcement that threatens the commodity tier of Indian IT work creates a premium tier for those who move up the stack. For a diaspora that has historically entered the US workforce through the services door, the message is to stop optimizing for the door and start optimizing for the room beyond it.

## What's next

Watch the headcount line in the next two quarters. Infosys and Wipro added employees in the most recent period even as Copilot adoption surged — a sign that, for now, AI is augmenting rather than replacing. If that reverses while revenue holds, deflation will have arrived in full, and the H-1B math will shift again. Either way, "AI-native" is no longer a slide in an investor deck. At Wipro, it is now an org chart — and the diaspora is on it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's IT Titans Lost ₹8.5 Lakh Crore in Five Years. The Money Walked Into AI Startups That Didn't Exist Then.",
        "subheadline": "A new Hurun ranking shows TCS, Infosys, and Wipro as the only major sector to shed value, while pure-play AI names like Sarvam climb the charts — a wealth migration NRI investors can't afford to misread.",
        "slug": make_slug("india-it-giants-value-decline-ai-startups-hurun-sarvam-nri-investors"),
        "category": "technology",
        "vertical": "economy",
        "diaspora_angle": "NRIs allocating to India through IT-heavy index funds and ADRs may be over-indexed on yesterday's winners; the value shift toward homegrown AI signals where the next decade of returns — and return-to-India bets — may actually sit.",
        "tags": ["markets", "it-services", "ai-startups", "sarvam", "investing", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/deeptech/tcs-infosys-wipro-shed-85-lakh-cr-in-five-yrs-as-ai-startups-enter-indias-value-charts"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/15/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding-round-led-by-hcltech/"},
            {"name": "MediaNama", "url": "https://www.medianama.com/2026/06/223-sarvam-raises-234-million-ai-unicorn/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange building in Mumbai, India's oldest equity market.",
        "image_attribution": "Wikimedia Commons",
        "body": """Here is a number that should give pause to any NRI who treats Indian tech as a single, ever-rising bet: over five years, **TCS, Infosys, and Wipro collectively shed ₹8.5 lakh crore in value** — making IT the only major sector to post a cumulative decline, according to a Hurun India ranking summarized this week by Outlook Business. The companies that built the diaspora's wealth, hired its parents, and sponsored its visas are no longer the companies the market is paying up for.

The money did not vanish. It moved. Four pure-play AI companies, including **Sarvam AI** — India's first homegrown large-language-model developer — debuted on the 2025 Hurun India 500. The center of gravity in Indian tech value is migrating from the services giants to the model-builders.

## What the ranking is really measuring

Hurun's report notes that markets have turned "sharply selective": only 198 of 500 companies gained value over the year. Investors are rewarding fundamentals — return on equity, cash generation, balance-sheet strength — over narrative. That selectivity cuts against the IT majors in a specific way. Their core business, billing clients for engineering hours, is exactly the model that AI deflation is squeezing. Their growth has slowed; TCS even posted a slight annual revenue decline. The market has noticed.

Meanwhile, capital is flowing toward companies that own intellectual property rather than rent out labor. Sarvam's trajectory makes the point. Just over a week ago it became India's newest AI unicorn, raising **$234 million** at a **$1.5 billion valuation** in the first close of a $300 million Series B — led by HCLTech, with Bessemer Venture Partners joining existing backers Khosla Ventures and Peak XV Partners. HCLTech alone put in $150 million for a 10.46% stake. It is one of only two Indian AI unicorns, alongside Ola's Krutrim.

## Why this is an NRI portfolio problem

Most diaspora investors get their India exposure through blunt instruments: an India index fund, a handful of ADRs (Infosys and Wipro both trade in New York), or an emerging-markets ETF. Those vehicles are heavily weighted toward exactly the large-cap IT and financial names that defined the last decade. An NRI who set up an India allocation in 2018 and left it alone is, without realizing it, over-indexed on the sector that just underperformed every other.

The harder truth is that the most interesting Indian tech value — the AI model-builders, the deep-tech startups — is largely **private and hard to reach from abroad**. Sarvam is not listed. Krutrim sits inside Ola. The diaspora capital that wants exposure to India's AI shift cannot simply buy it on the Nasdaq. That gap is itself a signal: it pushes some NRIs toward India-focused venture funds, toward GIFT City structures, and in a growing number of cases toward the "return-to-India" decision — joining or founding the companies directly because that is the only clean way in.

## The counter-argument worth holding

None of this means the IT giants are dead money. They generate enormous cash, pay dividends, and are themselves pivoting hard into AI — HCLTech's bet on Sarvam is a services giant buying its way into the model layer. A contrarian NRI investor might read the ₹8.5 lakh crore decline not as a verdict but as a discount on companies that still have the client relationships and engineering depth to reinvent themselves. The Hurun number is a warning against complacency, not necessarily a sell signal.

## What's next

The tell will be how the IT majors deploy capital. If they keep buying stakes in AI startups and standing up genuine AI-native units, the value gap could narrow. If they defend the old hours-for-dollars model, the migration continues. For NRIs, the practical move is unglamorous: look at what your India allocation actually holds. If it is three IT names and a bank, you own the last decade. The next one is being built by companies you can't yet buy — which is precisely why they're worth understanding now."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
