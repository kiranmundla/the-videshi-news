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
        "headline": "Trump Just Gave the Government a 30-Day Preview Window on Frontier AI Models. India's Builders Should Watch Closely.",
        "subheadline": "The executive order is voluntary, slimmed down from a 90-day version that spooked Silicon Valley, and it expands Anthropic's Mythos access to 150 organisations worldwide. But for Indian AI companies eyeing the American market, the signal matters more than the mandate.",
        "slug": make_slug("trump-ai-executive-order-30-day-model-review-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian AI startups building frontier models — Sarvam, Krutrim, and others — will need to understand this framework if they plan to deploy in the US. Indian-origin White House AI advisor Sriram Krishnan helped shape the policy environment. For Indian engineers at companies building these models, the order redefines what 'responsible deployment' means in practice.",
        "tags": ["ai-regulation", "trump", "frontier-ai", "india-ai", "cybersecurity", "sriram-krishnan"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/trump-signs-ai-executive-order-to-increase-government-oversight-1d1aa3c8"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/technology/3443981/trump-signs-ai-order-voluntary-early-government-access-new-models/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/ai-executive-order-companies-early-model-access-7f3c7dc2"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/02/trump-executive-order-ai-innovation-security/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/5473956/pexels-photo-5473956.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Two weeks ago, Donald Trump shelved an executive order on artificial intelligence after a last-minute intervention from David Sacks, his venture capitalist-turned-AI adviser. On Tuesday, he signed a slimmer version — one that asks AI companies to let the federal government preview frontier models 30 days before public release, down from the 90-day window that had spooked the industry.

The order is voluntary. It says so explicitly: nothing in the text authorises "a mandatory governmental licensing, preclearance, or permitting requirement" for AI models. But voluntary in Washington has a way of becoming expected, and the architecture it establishes — classified benchmarking, interagency review, early government access — lays groundwork that future administrations can harden into mandate.

## What the order actually does

The executive order directs the Treasury Department, the National Security Agency, CISA, and NIST to develop a classified benchmarking process within 60 days. The process will assess the cyber capabilities of advanced AI models and determine at what point a model qualifies as a "covered frontier model" subject to the 30-day preview.

The impetus is Anthropic's Mythos. The model's hacking capabilities alarmed national security officials enough that the company initially restricted access to roughly 50 organisations. On Tuesday, Anthropic expanded that number to about 150 companies and organisations across more than 15 countries, now spanning healthcare, power, and water infrastructure — sectors that had been excluded from the first tranche.

The White House framed the order as a cybersecurity measure. Michael Kratsios, director of the Office of Science and Technology Policy, said it "keeps America leading in AI while putting these frontier capabilities to work strengthening our cyber defenses." Treasury Secretary Scott Bessent, who has warned that advanced AI models could destabilise the financial system, helped broker the final compromise during a Monday evening Oval Office meeting.

## The Sacks compromise

The backstory matters. When Trump pulled the original order on May 21, it was because Sacks argued that even voluntary model testing could metastasise into mandatory regulation. National Cyber Director Sean Cairncross and other security officials pushed back, insisting that models like Mythos demanded some form of oversight.

The result is a split-the-difference document. The 30-day window is short enough that it should not meaningfully delay product launches. The voluntary label gives companies legal cover to participate without setting a compliance precedent. But the classified benchmarking process — run by intelligence and defence agencies — introduces a layer of government technical involvement in AI development that did not exist before.

## Why Indian AI builders should care

For India's emerging crop of frontier AI companies — Sarvam AI, now valued at $1.5 billion after raising from Nvidia and Amazon; Bhavish Aggarwal's Krutrim; and others building large-parameter models — the executive order is a preview of the regulatory terrain they will face if they ever deploy in the American market.

Indian-origin Sriram Krishnan, who serves as White House AI advisor, has been navigating this policy space from inside the administration. His presence does not guarantee favourable treatment for Indian companies, but it does mean someone in the room understands the Indian tech ecosystem's ambitions.

The sovereign AI dimension cuts both ways. As Barron's noted, if the US government gets early access to the most advanced models, other countries may accelerate efforts to build their own — precisely the argument Zoho's Sridhar Vembu made at ImagiNxt 2026 in Mumbai last week when he said India "cannot afford to remain only a consumer of global technology platforms."

For Indian engineers working at companies that build frontier models — Anthropic, OpenAI, Google DeepMind, Meta — the order redefines the deployment pipeline. Models will now pass through a government review layer, however thin, before reaching users. The 60-day window to establish benchmarking criteria means the rules of the game will be written this summer.

## The bottom line

The executive order is modest by design. It avoids the mandatory licensing that Europe has embraced and that Sacks explicitly warned against. But it establishes institutional machinery — classified benchmarks, interagency coordination, early access protocols — that tends to grow rather than shrink. For anyone building at the frontier of AI, whether in San Francisco or Bengaluru, this is the starting gun for a regulatory framework that will take years to fully materialise."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Called It a 'Dream Machine.' Microsoft Build 2026 Just Showed What Happens When Nvidia Powers Windows.",
        "subheadline": "The Surface RTX Spark Dev Box runs 120-billion-parameter models locally. OpenClaw lets AI agents control your PC. And Nadella is on the waitlist for his own product. Here is what Indian developers and NRI tech workers need to know from Build 2026.",
        "slug": make_slug("microsoft-build-2026-rtx-spark-openclaw-nadella"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella is the most prominent Indian-origin CEO in global tech, and Build 2026 is his flagship developer event. India has one of the largest Windows developer communities globally. The RTX Spark platform could reshape the tools Indian engineers use daily, and the agentic AI push on Windows has direct implications for the hundreds of thousands of Indian developers building on Microsoft's stack.",
        "tags": ["microsoft", "build-2026", "satya-nadella", "nvidia", "rtx-spark", "openclaw", "agentic-ai", "windows"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-showcases-new-pc-cloud-ai-tools-developer-conference-2026-06-02/"},
            {"name": "TechRepublic", "url": "https://www.techrepublic.com/article/nvidia-microsoft-rtx-spark-pcs-ai-agents/"},
            {"name": "Channel Life", "url": "https://channellife.co.nz/story/microsoft-nvidia-launch-rtx-spark-windows-ai-pc-lineup"},
            {"name": "GlobeNewsWire / Nvidia", "url": "https://www.globenewswire.com/news-release/2026/06/01/NVIDIA-and-Microsoft-Reinvent-Windows-PCs.html"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "body": """Satya Nadella stood on stage in San Francisco on Tuesday and called the Surface RTX Spark Dev Box a "dream machine." Then he mentioned, with the precise deadpan of a man who has spent $190 billion on AI infrastructure, that he had put himself on the waitlist to buy one.

The quip landed because the product behind it is genuinely unusual. The RTX Spark Dev Box is a compact desktop built around Nvidia's new superchip — a 20-core Grace CPU fused to a Blackwell RTX GPU via NVLink, sharing up to 128GB of unified memory. It runs a 120-billion-parameter AI model locally, on a machine that sits on a desk. Most laptops cannot even load a model that size.

This was the centrepiece of Microsoft Build 2026, but it was not the only signal. The two-day developer conference, running June 2-3, is Nadella's annual attempt to prove that Microsoft's AI spending — now larger than the GDP of several small countries — is translating into products developers will actually use.

## The hardware story

The Surface RTX Spark Dev Box is the desktop variant. Microsoft also unveiled the Surface Laptop Ultra, the first Surface device with an Nvidia Blackwell GPU and full CUDA support. It targets developers, AI builders, and creative professionals who have outgrown conventional hardware.

Manufacturing partners followed suit. Asus, Dell, HP, Lenovo, and MSI all announced RTX Spark laptops and desktops arriving this fall. The devices are priced to compete with Apple's premium offerings, though Nvidia did not disclose exact pricing.

The unified memory architecture is the technical differentiator. Unlike traditional PCs where the CPU and GPU maintain separate memory pools, RTX Spark shares one pool dynamically — the same approach Apple pioneered with its M-series silicon. This is what allows a thin laptop to run large local models without hitting memory walls.

For Indian hardware enthusiasts and NRI engineers who have watched Apple's M-series dominate the premium segment, RTX Spark is Windows finally arriving at the same architectural party — with Nvidia's AI accelerator advantage on top.

## The software story: OpenClaw and agentic AI

The more consequential announcement may be OpenClaw, an open-source framework that lets groups of AI agents carry out tasks on Windows PCs. Think of it as an operating system layer where you state your intent — "book my travel," "refactor this codebase," "find and summarise these documents" — and a coordinated swarm of agents picks the right tools, accesses local files, and executes.

OpenClaw has already gained traction in China and, somewhat embarrassingly for Microsoft, helped Apple sell Mac computers. The Build 2026 pitch is about making it safe enough for enterprises and Windows' billion-user base. Microsoft and Nvidia introduced OpenShell, a security runtime that defines what agents can do, decides when to route requests locally versus to the cloud, and masks personal data before anything leaves the device.

"NVIDIA and Microsoft share a vision that agents are the future of personal computing," said Jeff Fisher, Nvidia's senior vice president of personal computing. The statement is corporate-speak, but the underlying claim is radical: your PC is no longer a tool you operate. It becomes an agent you instruct.

## What Indian developers should watch

India has one of the world's largest concentrations of Windows developers, Azure customers, and .NET professionals. The shift to agentic AI on Windows has direct implications for how Indian engineers build software.

First, the local AI story matters. Running models on-device — without cloud round-trips — is particularly valuable in markets where latency and bandwidth are constraints. An Indian developer building AI features for domestic users could run inference on RTX Spark hardware without paying per-token cloud costs.

Second, the agent framework introduces a new application layer. OpenClaw and OpenShell will spawn a new category of agent-native applications, much as mobile app stores created a new developer economy. Indian IT services firms — TCS, Infosys, HCL Tech — will need to decide whether they build on this layer or get built over by it.

Third, there is the Nadella factor. The Hyderabad-born CEO continues to be the most visible Indian-origin executive in global tech. His bet on AI-first Windows, executed in partnership with Jensen Huang's Nvidia, is reshaping the platform that hundreds of millions of Indian professionals use daily. Whether it succeeds or becomes another Copilot-era disappointment will be visible by this time next year.

## The competitive picture

The RTX Spark launch is also a shot across Qualcomm's bow. When Nvidia unveiled the chip on Monday, Qualcomm's stock dropped 7.5 per cent. The ARM-based PC processor market, which Qualcomm had been quietly building with its Snapdragon X series, now faces a competitor with vastly superior AI capabilities and the full CUDA ecosystem behind it. Twenty thousand Indian engineers work at Qualcomm. They are watching.

Microsoft spent two years trying to lead the AI PC story with Copilot, and it underwhelmed. The RTX Spark partnership with Nvidia is a harder, more silicon-grounded bet. For Indian developers deciding where to invest their learning hours, Build 2026's message is clear: the agent era is arriving on Windows, and it is arriving with Nvidia inside."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Zoho's Sridhar Vembu Says the AI Bubble Is 'Even Bigger Than 1999.' NRI Investors Should Do the Maths.",
        "subheadline": "The bootstrapped billionaire who built Zoho from rural Tamil Nadu is warning that Nvidia at 20x sales, Apple at 10x, and Micron at 19x look like a repeat of the dot-com era. For Indian Americans with heavy tech portfolios, his argument deserves scrutiny.",
        "slug": make_slug("sridhar-vembu-zoho-ai-bubble-bigger-than-1999-nri"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "NRI investors are disproportionately concentrated in US tech stocks — many hold NVIDIA, Apple, Microsoft, and Micron in their portfolios. Vembu's warning about price-to-sales ratios exceeding dot-com levels is directly relevant to their wealth. Separately, Vembu's ImagiNxt speech on sovereign AI and Zoho's rural R&D model offers an alternative vision for Indian tech self-reliance that resonates with diaspora entrepreneurs.",
        "tags": ["sridhar-vembu", "zoho", "ai-bubble", "stock-market", "nri-investors", "sovereign-ai", "india-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Storyboard18", "url": "https://www.storyboard18.com/this-is-an-insane-bubble-zohos-sridhar-vembu-says-ai-driven-tech-valuations-look-bigger-than-1999-bubble"},
            {"name": "IANS / Zoho Vembu X post", "url": "https://www.ianslive.in/news/zoho-founder-sridhar-vembu-warns-of-ai-driven-tech-bubble-says-valuations-are-even-bigger-than-1999-20260531"},
            {"name": "ImagiNxt 2026 / Local Business News", "url": "https://newslocalbiz.com/imaginxt-2026-industry-leaders-advocate-indigenous-ai-deeptech-innovation/"},
            {"name": "Hindu Business Line / Can India reap AI gains?", "url": "https://www.thehindubusinessline.com/opinion/can-india-reap-ai-gains/article69636422.ece"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://images.pexels.com/photos/6770610/pexels-photo-6770610.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": """Sridhar Vembu does not raise money from venture capitalists, does not plan an IPO, and runs much of Zoho's R&D from a village in Tamil Nadu. When he calls the current AI-driven tech rally "an insane bubble, even bigger than 1999," it carries a different weight than the same warning from a short-seller or a cable news pundit. He has no position to talk his own book.

In a post on X last week, Vembu laid out the numbers. Nvidia trades at roughly 20 times its annual sales. Apple and Microsoft sit at about 10 times. Alphabet is at 11 times. Meta is at 7.5 times. Micron, riding the AI memory chip wave under Indian-origin CEO Sanjay Mehrotra, trades at 19 times sales.

Then Vembu reached for a quote that technology veterans of a certain vintage will remember. In 2002, after the dot-com crash had vaporised trillions, Scott McNealy of Sun Microsystems offered a mea culpa: "At 10x revenues, to give you a ten-year payback, I have to pay you 100% of revenues for 10 straight years in dividends. That assumes I can get that by my shareholders. That assumes zero cost of goods sold, which is very hard for a computer company. That assumes zero expenses, which is really hard with 39,000 employees."

Vembu's point is plain. Several of today's largest technology companies are trading at or above the multiples that McNealy called mathematically absurd — and doing so with real costs, real employees, and real infrastructure bills. Nvidia alone is spending billions on AI chip fabrication. Alphabet just asked shareholders for $80 billion in fresh equity to fund AI data centres. Anthropic, still private, raised $65 billion last week at a $965 billion valuation.

## The NRI portfolio problem

This matters to Indian Americans in a specific, concrete way. NRI tech workers are disproportionately concentrated in US technology stocks. Many hold Nvidia, Apple, Microsoft, and Micron through 401(k) plans, RSUs, ESPPs, and brokerage accounts. A correction in AI-linked equities would not be an abstract market event — it would hit the net worth of hundreds of thousands of Indian families in the Bay Area, Seattle, Austin, and New Jersey.

The counterargument is that today's AI companies are not 1999's dot-coms. Nvidia has real revenue — over $130 billion annually — and real demand from every hyperscaler on Earth. Microsoft's Azure is growing at 30 per cent year-over-year. Apple's services business generates margins that would make a software company envious. These are not Pets.com.

But Vembu is not arguing that the companies are fraudulent. He is arguing that the prices have outrun even excellent fundamentals. A stock can be a great company and a terrible investment at the same time, and at 20 times sales, the mathematics of a reasonable return become punishing over any normal time horizon.

## The sovereign AI counterpoint

Three days after his X post, Vembu delivered a different message at ImagiNxt 2026 in Mumbai. Speaking at the Jio World Convention Centre, he argued that India "cannot afford to remain only a consumer of global technology platforms" and called for sustained investment in indigenous AI, semiconductors, and quantum sensing.

Zoho practises what Vembu preaches. The company has filed over 30 patents through its rural R&D teams and is investing in chips and advanced materials. It runs a profitable SaaS business with over 100 products — all built without external funding. In a world where Anthropic burns 71 cents on compute for every dollar of revenue, Zoho's bootstrapped discipline looks less like quaintness and more like a hedge.

For NRI entrepreneurs watching from abroad, Vembu's twin message — that American tech valuations are dangerously stretched, and that India should build its own AI stack — presents an interesting convergence. If the bubble does correct, capital will flow to cheaper markets. India, with its growing AI ecosystem (Sarvam AI, valued at $1.5 billion; Zoho; Freshworks) and government-backed initiatives like the India Semiconductor Mission, could be a beneficiary.

## What to make of it

Bubble warnings have a dismal track record for timing. The phrase "irrational exuberance" was coined in December 1996; the market did not peak until March 2000. Vembu may be right about the fundamentals and still wrong about the timeline by years.

But his underlying arithmetic is hard to dismiss. When even value-conscious investors like Warren Buffett are piling into AI-era equity raises — Berkshire participated in Alphabet's $80 billion offering — the enthusiasm has moved well beyond the risk-tolerant fringe.

For Indian American tech workers sitting on concentrated positions in Nvidia, Microsoft, or Micron stock, the prudent response is not panic but diversification. Vembu is not telling anyone to sell everything. He is telling everyone to count — and to remember what happened the last time people stopped counting."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
