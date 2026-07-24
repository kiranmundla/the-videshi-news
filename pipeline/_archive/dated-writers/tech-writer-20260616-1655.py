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
        "headline": "Arvind Krishna Just Tied IBM to ServiceNow. The Bet: Companies Want Plumbing, Not Chatbots.",
        "subheadline": "IBM's long-term alliance with ServiceNow targets the messy data and legacy code that stall enterprise AI — the exact work that keeps thousands of Indian engineers and IT-services firms employed.",
        "slug": make_slug("ibm-servicenow-arvind-krishna-enterprise-ai-plumbing"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "The 'unglamorous' integration work IBM is betting on is precisely what employs tens of thousands of Indian engineers and props up the US revenue of TCS, Infosys and Wipro.",
        "tags": ["ibm", "arvind-krishna", "enterprise-ai", "indian-tech", "it-services"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks (IBM-ServiceNow deal)", "url": "https://www.zacks.com/stock/news/2756001/can-ibms-extended-servicenow-deal-accelerate-enterprise-ai-adoption"},
            {"name": "CRN Australia (IBM Think 2026)", "url": "https://www.crn.com.au/news/ibm-think-2026-showcases-agentic-ai-and-sovereign-cloud-strategy"},
            {"name": "Morningstar / PR Newswire (IBM Think 2026)", "url": "https://www.morningstar.com/news/pr-newswire/20260505bo12345/think-2026-ibm-delivers-the-blueprint-for-the-ai-operating-model-as-the-ai-divide-widens"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Arvind_Krishna_in_2025_%28cropped%29.jpg",
        "image_caption": "IBM Chairman and CEO Arvind Krishna, pictured in 2025.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """IBM has deepened its alliance with ServiceNow into a long-term strategic partnership, the two companies said this week, pitching it as a cure for the two ailments that quietly kill most enterprise AI projects: scattered data and brittle legacy systems.

The framing matters more than the press release. Under Chairman and CEO Arvind Krishna, IBM has spent the past year arguing that the companies winning with AI are not the ones buying the most of it. "The enterprises pulling ahead are not deploying more AI — they're redesigning how their business operates," Krishna said at IBM's Think conference earlier this year. The ServiceNow deal is that thesis turned into a sales motion.

### What the deal actually does

IBM will fold its data-management, automation and AI tooling into ServiceNow's platform to help large organizations run AI "at scale" — corporate shorthand for getting models to work across systems that were never designed to talk to each other. Three areas are named: modernizing legacy applications so they can take AI at all, cleaning and governing enterprise data so the models have something trustworthy to chew on, and automating IT operations so problems get caught before they hit customers.

None of this is glamorous. There is no consumer chatbot, no viral demo. And that is precisely the point Krishna keeps making. "That is the value that enterprises need — not just a chatbot or a consumerish application," he told reporters at Think. "Those are important, but they only get to the first 20 percent of the value. The next value comes from deploying hybrid cloud technologies." The ServiceNow tie-up sits alongside IBM's recent partnerships with Google Cloud and its own Red Hat unit — all aimed at the same plumbing.

### Why an NRI engineer should care

Here is the diaspora angle that rarely makes the headline. The work IBM is describing — connecting data sources, rewriting decades-old code, wiring governance into AI workflows — is exactly the labor that employs a vast share of the Indian-origin tech workforce, both inside IBM and across the Indian IT-services giants that live or die on US enterprise contracts.

When TCS, Infosys, Wipro, HCLTech and Cognizant report earnings, the swing factor is increasingly "AI deflation": the fear that automation shrinks the billable hours these firms sell. IBM's bet cuts the other way. If the real money in enterprise AI is in integration and modernization, the firms with armies of engineers who understand messy legacy estates are positioned to win, not be gutted. Infosys CEO Salil Parekh has made the same case, saying AI is producing "compression" in some service lines but growth overall, with clients moving fast on agentic AI.

For an Indian engineer at IBM in Armonk, Bengaluru or Bratislava, that distinction is the difference between a reskilling memo and a pink slip. IBM's "Bob" agentic-developer product, now generally available, leans on Anthropic's Claude, Mistral models and IBM's own Granite to accelerate exactly this modernization work — meaning the human engineers move up the stack rather than out the door, at least in IBM's telling.

### The skeptic's read

Krishna has been notably calm about the "is AI a bubble" question that haunts the rest of the sector, arguing enterprise adoption is still in its "early innings." That optimism is convenient for a company selling the picks and shovels. The risk is that "AI operating model" becomes another consulting buzzword that enterprises nod at and underfund — IBM itself concedes many companies have spent heavily on AI and few believe it is paying off.

But for the diaspora, the structural story is encouraging. The center of gravity in enterprise AI is shifting from flashy models to the durable, integration-heavy work where Indian engineering talent has spent two decades building an edge. IBM, Infosys and ServiceNow are all betting that the next decade of AI money is in the plumbing.

### What's next

Watch IBM's next earnings call for whether the ServiceNow and Google Cloud partnerships translate into "partner-touched" revenue — Krishna's stated goal is to get that to half of IBM's total. And watch the Indian IT majors: if their commentary keeps shifting from "AI threatens billings" to "AI drives integration demand," it confirms the IBM thesis. For the diaspora workforce, that is the number that matters."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ISRO Hasn't Launched a Rocket Since January. A Return-to-Flight Is Now Weeks Away.",
        "subheadline": "After two PSLV failures, India's space agency is targeting a late-June or early-July comeback — with the first uncrewed Gaganyaan test and a private Skyroot orbital launch waiting behind it.",
        "slug": make_slug("isro-pslv-return-to-flight-gaganyaan-skyroot-launch"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs who treat ISRO milestones as a source of pride and increasingly as an investable space economy, the agency's return to flight is the credibility test that unlocks both.",
        "tags": ["isro", "space-tech", "gaganyaan", "skyroot", "india-space"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "News Dive (PSLV return-to-flight)", "url": "https://newsdive.net/isro-set-to-make-another-attempt-at-pslv-launch-by-late-june-or-early-july"},
            {"name": "PIB (Gaganyaan programme)", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2127312"},
            {"name": "Reuters (Skyroot $1bn valuation)", "url": "https://www.reuters.com/business/aerospace-defense/indias-skyroot-becomes-first-1-bln-space-tech-startup-2026/"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/PSLVC62.webp/1280px-PSLVC62.webp.png",
        "image_caption": "An ISRO Polar Satellite Launch Vehicle (PSLV) on the pad at the Satish Dhawan Space Centre, Sriharikota.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """India's space agency has not put a rocket into orbit since January. That drought is about to end. Union Science Minister Jitendra Singh said this week that the next Polar Satellite Launch Vehicle (PSLV) flight could lift off by late June or early July — a return-to-flight that carries far more weight than a single satellite deployment.

The pause was not planned. ISRO's last PSLV mission, in January, failed to place the EOS-N1 Earth-observation satellite into orbit, the second failure in a row after a May 2025 PSLV mission lost the EOS-09 satellite. Both faltered at the third stage. Investigators traced the trouble to specific components from outside suppliers rather than ISRO-built hardware, and the agency has since changed vendors for those parts.

### Why a single launch matters so much

For a space program that built its global brand on reliability and frugality — landing near the Moon's south pole, reaching Mars on a shoestring — two consecutive failures are a reputational dent, not just an engineering one. ISRO's pitch to commercial customers, foreign governments and India's own surging private space sector rests on the idea that its rockets are dependable and cheap. A clean return-to-flight is how it rebuilds that case.

And the queue behind this launch is consequential. ISRO is preparing the first uncrewed test of Gaganyaan, India's human-spaceflight program, which will carry the half-humanoid robot Vyommitra to rehearse astronaut conditions in low Earth orbit. Singh said he is optimistic the necessary test flights can be completed by year's end, with the first crewed mission targeted for 2027. If it succeeds, India becomes only the fourth nation — after the Soviet Union, the United States and China — to independently send humans to space.

Meanwhile, the private firm Skyroot Aerospace is expected to attempt its maiden orbital launch of Vikram-1, India's first privately developed orbital rocket, with the payload fairing already delivered to Sriharikota. Skyroot recently became India's first space-tech unicorn, raising fresh capital from Singapore's GIC, Sherpalo Ventures and BlackRock at a $1.1 billion valuation.

### The diaspora angle: pride, and now portfolio

For the Indian diaspora, ISRO milestones have long been a shared point of pride — the kind of news that lands in family WhatsApp groups from San Jose to Slough within minutes. But the relationship is changing. India's space sector has been opened to private firms, backed by a 10-billion-rupee government fund and a separate Rs 500 crore Technology Adoption Fund that just made its first three picks: Astrobase, SatSure and TM2SPACE.

That turns a source of sentiment into a source of investment. NRI investors and diaspora-led venture funds are increasingly eyeing Indian space startups, and a name like Skyroot — already backed by GIC and BlackRock — is the kind of company that could eventually offer the diaspora a direct stake in India's launch economy. Ram Shriram, the Sherpalo founder known for his early Google bet, has joined Skyroot's board, a signal Silicon Valley's Indian-American investor class is paying attention.

But the entire edifice depends on launch reliability. Private satellite makers like Dhruva Space, analytics firms like SatSure and propulsion startups like Astrobase all ultimately need rockets that work — whether ISRO's or Skyroot's. A successful PSLV comeback de-risks the whole ecosystem; another failure would chill the investor enthusiasm that the diaspora is part of fueling.

### What's next

Three things to watch over the coming weeks. First, the PSLV launch itself, expected to carry an Oceansat satellite plus an Indo-Mauritius joint satellite and Dhruva Space's LEAP-2 — a vendor change put to the test. Second, Skyroot's Vikram-1 maiden flight, which would prove India's private sector can reach orbit. Third, the Gaganyaan-1 uncrewed test, the gateway to India's human-spaceflight ambitions.

For a diaspora that has spent decades cheering ISRO from afar, the next month is less about a single rocket and more about whether India's space story — increasingly a private, investable one — gets back on schedule."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Built a CPU 'for Agents, Not Humans.' Indian Engineers Are About to Build the Apps That Run on It.",
        "subheadline": "Jensen Huang's new Vera processor is going into production just as India lines up $50 billion in AI data-center spending — putting the diaspora at both ends of the agentic-AI supply chain.",
        "slug": make_slug("nvidia-vera-cpu-agents-india-ai-data-center-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian engineers write a huge share of the world's enterprise software and India is now building the data centers to run it — so Nvidia's agent-first chip lands squarely on the diaspora's turf.",
        "tags": ["nvidia", "jensen-huang", "ai-chips", "india-data-center", "agentic-ai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CRN (Vera CPU at Computex 2026)", "url": "https://www.crn.com/news/components-peripherals/2026/jensen-huang-uses-computex-2026-to-showcase-nvidia-s-next-ai-push"},
            {"name": "Reuters (Nvidia Vera CPU)", "url": "https://www.reuters.com/technology/nvidia-begins-vera-cpu-sales-pitch-chinese-clients-2026/"},
            {"name": "Reuters (Jabil-Adani India AI data centers)", "url": "https://www.reuters.com/business/apple-supplier-jabil-adani-partner-build-ai-data-center-infra-platform-india-2026/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia co-founder and CEO Jensen Huang, pictured in 2025.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Nvidia has begun pitching its new Vera processor to customers and moved it into full production, the company has confirmed — a chip CEO Jensen Huang describes in unusually blunt terms. "All the CPUs of the past we built for humans," Huang said when he unveiled Vera. "This CPU is built for agents."

That sentence is a thesis about where computing is headed, and it lands directly on the Indian diaspora's turf at both ends of the supply chain.

### What Vera is

Vera is Nvidia's first standalone CPU built specifically for "agentic" AI — software that performs tasks autonomously rather than waiting for a human to click. Nvidia says it runs up to 1.8 times faster than comparable x86 processors from Intel and AMD on the kind of behind-the-scenes work that AI agents rely on: reinforcement learning, data processing, orchestrating other systems. Huang expects it to become Nvidia's next multibillion-dollar business, and the company is already telling some clients they can place orders, with availability as soon as August.

The strategic logic is that AI agents, not people, will soon be the heaviest users of computing. "AI agents will be the largest users of computing," Huang said. "Vera is the first CPU designed for that future — built to run agentic AI at hyperscale." If he is right, the economics of every data center shift toward chips optimized for autonomous software.

### The diaspora's first stake: who writes the agents

Here is the part that should interest an Indian engineer in the Bay Area, Bengaluru or New Jersey. The agentic software that Vera is built to run is increasingly written by Indian-origin talent and Indian IT-services firms. Infosys says it has already built 300 AI agents across business and IT operations for clients. TCS, Wipro and HCLTech are racing to do the same, and India's "global capability centers" — the in-house tech hubs multinationals run in India — now employ a workforce heading toward 2.36 million, much of it focused on exactly this kind of work.

In other words, the people building the demand for agent-optimized silicon are disproportionately Indian. The narrative that AI would simply gut Indian IT jobs is giving way to a more nuanced one: the firms that move up the stack to build and orchestrate agents become the customers of chips like Vera, not its casualties.

### The diaspora's second stake: where the agents run

The other end of the chain is physical, and it is increasingly in India. This week, Apple supplier Jabil and India's Adani Group announced a partnership to build AI data-center hardware in India at gigawatt scale, aimed at serving global hyperscalers and anchoring India as an export hub for AI-ready infrastructure. The companies pointed to more than $50 billion in planned Indian spending across data centers, cloud and AI, and Adani's own $100 billion renewable-powered data-center ambition by 2035.

Huang has been explicit that India belongs in this build-out. "There is no question in my mind there will be artificial intelligence infrastructure in India," he has said, calling AI "infrastructure" on par with water and electricity, and arguing that India's linguistic diversity makes home-grown AI a necessity rather than a luxury. India's 2026 budget added a 20-year tax holiday for data centers to court exactly this investment.

For NRI investors, that creates a tangible thread: Nvidia's agent-first chips at the top of the stack, Indian engineers writing the agents in the middle, and India-built, India-powered data centers at the bottom. India's first pure AI-infrastructure public listings — GPU operators going public at home — are beginning to give the diaspora a way to own a slice of it.

### The caution

None of this is frictionless. Nvidia's China business has effectively collapsed under US export controls, a reminder that geopolitics can reroute the entire chip supply chain overnight — and that India's positioning is partly a beneficiary of that very tension. Data-center build-outs are capital-hungry and power-hungry; Adani's renewable bet is as much about electricity as about silicon.

### What's next

Watch whether Vera orders ramp through the second half of the year, and whether Indian IT firms start citing agent deployment as a revenue line rather than a defensive talking point. And watch the Jabil-Adani platform: if India can manufacture AI racks for export, the diaspora's stake in the agentic-AI era stops being just about the code, and starts being about the factories too."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
for h in inserted:
    print(f" - {h}")