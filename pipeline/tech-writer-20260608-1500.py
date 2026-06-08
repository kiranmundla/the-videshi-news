#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-08 15:00 UTC run"""
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
    # ── ARTICLE 1: Satya Nadella / Microsoft Build 2026 ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella's Build Week Went Sideways. The Stakes Have Never Been Higher.",
        "subheadline": "A leaked 'addiction' memo, a training-data scandal, and seven new in-house AI models — Microsoft's most important developer conference in a decade delivered fireworks nobody planned.",
        "slug": make_slug("nadella-microsoft-build-scout-mai-controversy"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Satya Nadella remains the most powerful Indian-origin CEO in global tech. Microsoft employs tens of thousands of Indian engineers on H-1B visas across Redmond, Hyderabad, and Bangalore. Build 2026's push toward in-house AI models and agentic platforms directly shapes the roles — and job security — of this workforce.",
        "tags": ["satya-nadella", "microsoft", "build-2026", "ai-agents", "mai", "scout"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post", "url": "https://nypost.com/2026/06/06/business/microsofts-satya-nadella-slams-company-exec-for-outlining-plan-to-make-people-addicted-to-scout-ai-tool/"},
            {"name": "The420.in", "url": "https://the420.in/microsoft-mai-models-unlicensed-web-data/"},
            {"name": "Kotaku", "url": "https://kotaku.com/microsoft-scout-ai-addictive-leak-build-2026/"},
            {"name": "Fast Company", "url": "https://fastcompany.com/how-microsoft-is-bringing-openclaw-to-the-masses/"},
            {"name": "Digit.in", "url": "https://digit.in/news/general/microsoft-ceo-satya-nadella-says-ai-agents-need-identities-permissions-and-policies-like-employees/"}
        ]),
        "score_total": 85,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella at a company event",
        "image_attribution": "Wikimedia Commons",
        "body": """Microsoft Build 2026 was supposed to be Satya Nadella's coronation lap. The company unveiled seven in-house AI models, a custom chip that outperforms Nvidia's hardware on specific workloads, and a full agentic-AI platform designed to transform how every knowledge worker on earth interacts with software. Instead, the Hyderabad-born CEO spent the back half of the week putting out fires that his own lieutenants lit.

## The Scout Memo

On Tuesday, tech watchdog 404 Media published an internal Microsoft document credited to Corporate Vice President Omar Shahine — the project lead behind Scout, Microsoft's new personal AI agent. The memo outlined a three-phase rollout plan. Phase one's heading was blunt: "Make people addicted."

The document described building features that "make people depend on it daily," noting that this pattern was "already happening organically" among the 1,000-plus Microsoft employees using the tool internally — Nadella himself among them.

Within hours, Nadella fired back on an internal message board shared with roughly 50 senior engineers. "This is absolutely a non-goal," he wrote. "If anything we are doing the exact opposite. We want to make sure AI empowers and adds real value to human endeavor and broad economic growth." Then the knife twist: "Not sure what this document is or who is writing and leaking this nonsense! They may want to go work elsewhere."

The optics were terrible. Shahine is not a rogue middle manager — he authored the official Microsoft blog post introducing Scout to the world. His memo wasn't a brainstorm scrawled on a whiteboard; it was a strategic planning document for the company's flagship consumer AI product.

## The Training Data Problem

The second blow landed almost simultaneously. Researchers reviewing the technical preprint for MAI-Thinking-1 — Microsoft's new 35-billion-parameter reasoning model, built entirely in-house as a declaration of independence from OpenAI — discovered that the model's foundational data architecture relies heavily on billions of pages of unlicensed web content, including Common Crawl.

This directly contradicted Nadella's keynote messaging, where the leadership team pitched MAI as built on "enterprise-grade, clean, and commercially licensed data." Corporate procurement teams in finance, healthcare, and government — precisely the customers Microsoft was targeting — have since begun re-evaluating their assessments.

## What Actually Shipped

Buried beneath the controversy, Build 2026's technical announcements were genuinely significant. MAI-Thinking-1 runs on Microsoft's custom Maia 200 chip and delivers 1.4x performance-per-watt over Nvidia's GB-200 infrastructure. Microsoft claims an internal MAI model tuned for Excel performs on par with GPT-5.4 at one-tenth the cost. McKinsey, an early partner, reportedly achieved similar results against GPT-5.5 on its proprietary workflows.

The company also introduced Autopilots — autonomous, long-running agents with full enterprise compliance that operate within a customer's tenant. And Nadella himself acknowledged the management challenge. He told the *Possible Podcast* that he personally runs about 100 AI coding agents simultaneously, and the "cognitive load" of managing them is enormous. His proposed solution: treating AI agents like employees, with identities, sandboxes, audit trails, and governance policies through a new platform called Agent 365.

## What Indian Tech Workers Should Watch

For the estimated 35,000-plus Indian-origin professionals at Microsoft — many on H-1B visas in Redmond and across the company's sprawling Hyderabad and Bangalore campuses — Build 2026 sends a mixed signal. The company is building more AI infrastructure in-house, creating new engineering roles in custom silicon, model training, and agent orchestration. But it is also openly replacing commodity engineering tasks with the very agents it just unveiled. Nadella's 100-agent workflow is not a party trick. It is a preview of how the company expects its own managers to operate.

The MAI pivot also recalibrates Microsoft's relationship with OpenAI. As Microsoft builds its own model family, the strategic rationale for its multi-billion-dollar OpenAI investment shifts from dependency to optionality. For Indian engineers who joined Microsoft specifically for its OpenAI-powered Copilot stack, the ground is moving.

Microsoft's stock dropped roughly 5% during the week, shedding about $700 billion in market capitalisation — though much of that tracked the broader Nasdaq selloff rather than Build-specific news. The question for Nadella is whether the substance of Build 2026 can outlast the noise. The products are real. The contradictions are also real. For now, both coexist in the same keynote."""
    },

    # ── ARTICLE 2: EU Tech Sovereignty Package ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Europe Just Built a Firewall Around Its Cloud. Indian IT's Biggest Clients Are on the Other Side.",
        "subheadline": "The EU's new Technological Sovereignty Package creates a four-tier classification system for cloud services that could lock out American hyperscalers — and the Indian firms that depend on them.",
        "slug": make_slug("eu-tech-sovereignty-indian-it-cloud-threat"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian IT services giants — TCS, Infosys, Wipro, HCL Tech — derive billions in revenue from European clients, largely through AWS, Azure, and GCP partnerships. A sovereignty framework that restricts hyperscaler access to sensitive EU contracts directly threatens this revenue stream and the thousands of Indian tech workers deployed in Europe.",
        "tags": ["eu-sovereignty", "indian-it", "tcs", "infosys", "wipro", "cloud-computing", "regulation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WebProNews", "url": "https://webpronews.com/europe-draws-a-line-how-the-new-tech-sovereignty-package-challenges-us-cloud-giants/"},
            {"name": "Le Monde", "url": "https://lemonde.fr/en/opinion/article/2026/06/05/europe-s-painful-awakening-on-digital-sovereignty.html"},
            {"name": "The Times", "url": "https://thetimes.com/business-money/technology/article/eu-efforts-to-combat-us-tech-dominance-may-backfire"},
            {"name": "The Hindu Business Line", "url": "https://thehindubusinessline.com/info-tech/wipro-tcs-drag-nifty-it-2-lower-after-nasdaq-crash-ai-selloff/"},
            {"name": "TradingView", "url": "https://tradingview.com/news/nifty-it-falls-global-tech-selloff-infosys-tcs-wipro/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5480781/pexels-photo-5480781.jpeg",
        "image_caption": "Server infrastructure inside a modern data center",
        "image_attribution": "Pexels",
        "body": """On June 3, the European Commission unveiled a package of legislative proposals that, if enacted, will fundamentally reshape how cloud computing works across the continent. For Indian IT services firms — TCS, Infosys, Wipro, HCL Tech, Tech Mahindra — the timing could hardly be worse.

The European Technological Sovereignty Package, led by Executive Vice-President Henna Virkkunen, introduces the Cloud and AI Development Act. At its core is a four-tier classification system for cloud services. The most restrictive tier demands that technology providers be European-owned, controlled by EU nationals, and insulated from foreign laws — including, pointedly, the U.S. Cloud Act. Public authorities in healthcare, banking, energy, and justice must route sensitive workloads only to providers meeting the highest standards.

"We want to be sure nobody has a kill switch," Virkkunen told CNBC, referencing a recent incident where Microsoft suspended the email account of the International Criminal Court's chief prosecutor following U.S. sanctions.

## The Indian IT Problem

The implications cascade quickly. Indian IT services firms do not sell cloud infrastructure directly — they build, manage, and operate on top of it. TCS runs SAP workloads on Azure. Infosys manages enterprise migrations to AWS. Wipro builds hybrid-cloud architectures on GCP. When Brussels restricts which cloud platforms can handle sensitive European data, it does not merely inconvenience Amazon, Microsoft, and Google. It pulls the rug from under the Indian firms whose entire European value proposition rests on those platforms.

Europe is not a marginal market. TCS derived approximately 31% of its FY26 revenue from Europe and the UK. Infosys drew about 25%. Wipro reported similar exposure. Across the sector, European contracts represent tens of billions of dollars in annual revenue — a share that has been growing as American tech spending has slowed.

The proposed framework does not ban non-European providers outright. Lower-tier classifications still allow AWS, Azure, and GCP to operate. But the most lucrative contracts — government IT modernisation, healthcare data platforms, financial infrastructure — will increasingly require sovereignty-compliant providers. Indian firms that cannot partner with qualifying European cloud vendors will simply be locked out of the bid.

## Nifty IT's Brutal Week

The regulatory threat arrives as Indian IT stocks are already under severe pressure. The Nifty IT index fell 8.4% over four consecutive sessions through Monday, erasing the gains from a preceding three-session rally that had been driven by AI spending optimism. Wipro was the worst hit, plunging 8.3% to ₹181.80 — within touching distance of its 52-week low of ₹186.50 — on volume nearly double its 50-day average. TCS fell 2.2%. Infosys declined 1.3%.

The proximate cause was a global tech selloff triggered by a hotter-than-expected U.S. jobs report and Broadcom's disappointing AI guidance. But the structural overhang for Indian IT in Europe is harder to dismiss. Analysts at HDFC Securities noted that semiconductor losses drove the immediate correction, but the "demand visibility" concerns from Infosys's FY27 guidance — which projected constant-currency growth of just 1.5% at the high end — reflect deeper anxieties about where the next wave of enterprise spending will come from.

## The ASML Wrinkle

Even within Europe, the sovereignty push is generating friction. Christophe Fouquet, CEO of ASML — the Dutch company that holds a near-monopoly on extreme ultraviolet lithography machines — publicly urged Brussels to "step back" from top-down management of strategic tech projects. He endorsed the demand-driven elements of the package but warned that layers of political review and bureaucratic criteria risk slowing progress and raising costs. The concern is shared by European startups: DeepL founder Jarek Kutylowski said the framework's requirements "are so stringent that even homegrown European companies like DeepL will struggle to meet them."

## What NRIs Should Watch

For Indian professionals working in European IT — and there are thousands, particularly in the UK, Germany, and the Netherlands — the sovereignty package creates a new category of career risk. Projects involving sensitive public-sector data may increasingly require European-national oversight, potentially limiting the roles available to non-EU workers.

For NRI investors, the immediate concern is earnings exposure. If even 10-15% of European revenue becomes contested territory due to sovereignty requirements, the margin impact on TCS, Infosys, and Wipro would be material. The proposals are in early stages — legislation must pass the European Parliament and be adopted by member states — but the direction is clear. Europe is building walls around its digital infrastructure, and Indian IT services sit squarely on the wrong side."""
    },

    # ── ARTICLE 3: Marvell S&P 500 / Jensen Huang Endorsement ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Jensen Huang Called Marvell the Next Trillion-Dollar Company. Now It's Joining the S&P 500.",
        "subheadline": "Marvell Technology enters the benchmark index after a 59% surge in two weeks, fuelled by an Nvidia endorsement, a custom AI chip boom, and a market that cannot get enough of the silicon behind the silicon.",
        "slug": make_slug("marvell-sp500-jensen-huang-trillion-dollar-custom-ai-chips"),
        "category": "technology",
        "vertical": "technology",
        "is_editorial": False,
        "diaspora_angle": "Indian chip designers are central to the custom silicon revolution powering Marvell, Broadcom, and hyperscaler in-house chip teams. Marvell's design centres in India contribute to the networking and optical interconnect chips driving its AI growth. For NRI investors, the S&P 500 inclusion triggers passive fund inflows that typically lift newly added stocks.",
        "tags": ["marvell", "nvidia", "sp500", "custom-chips", "semiconductor", "jensen-huang", "ai-infrastructure"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://reuters.com/technology/marvell-shares-jump-after-chipmaker-wins-spot-sp-500-2026-06-08/"},
            {"name": "Motley Fool", "url": "https://fool.com/investing/2026/06/06/jensen-huang-just-said-this-ai-chip-stock-could-be-the-next-1-trillion-company/"},
            {"name": "AInvest", "url": "https://ainvest.com/post/the-way-to-a-trillion-dollars-is-not-to-make-gpus/"},
            {"name": "Barron's", "url": "https://barrons.com/articles/micron-stock-rising-sk-hynix-nvidia-deal/"}
        ]),
        "score_total": 75,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg",
        "image_caption": "Close-up of a semiconductor microchip on a circuit board",
        "image_attribution": "Pexels",
        "body": """On Friday evening, S&P Dow Jones Indices announced that Marvell Technology would replace swimming pool equipment distributor Pool Corp in the S&P 500. The change takes effect before markets open on June 22. In pre-market trading Monday, Marvell shares climbed another 7%, adding to a run that has seen the stock surge 59% in barely two weeks.

The trigger was a single sentence from Nvidia CEO Jensen Huang at Computex 2026 in Taipei. On stage with Marvell CEO Matt Murphy on June 2, Huang interrupted his counterpart mid-sentence to declare: "That's why you're going to be the next trillion-dollar company, ladies and gentlemen."

The stock jumped 32.5% the following day.

## The Company Behind the Companies

Marvell does not make the GPUs that dominate AI headlines. It makes something arguably more strategic: the custom silicon and networking chips that allow hyperscalers to build differentiated AI infrastructure around Nvidia's base hardware. Google designs its own TPUs. Microsoft has Maia. Amazon has Trainium. All of them need someone to fabricate and deliver purpose-built silicon — and increasingly, that someone is Marvell.

The company's fiscal 2026 revenue hit $8.2 billion. Its custom chip business is projected to exceed $10 billion in revenue by fiscal 2029, and total revenue to reach $16.5 billion by fiscal 2028. Nvidia's $2 billion investment in Marvell, announced in March, formalised a partnership around NVLink Fusion — a rack-scale platform that lets customers build semi-custom AI infrastructure using Nvidia's NVLink interconnect ecosystem.

Marvell's market capitalisation now sits around $230 billion. To reach Huang's trillion-dollar prophecy, it would need to roughly quadruple — an enormous ask, but not an absurd one given the trajectory. The company trades at about 65 times this year's earnings estimates and 43 times next year's. Not cheap. Not unprecedented in the AI semiconductor cycle either.

## The S&P 500 Effect

Index inclusion is more than a prestige marker. Exchange-traded funds tracking the S&P 500 must buy shares of newly added companies to rebalance their portfolios. For a company Marvell's size, the passive inflow around the June 22 inclusion date could be substantial. The Philadelphia Semiconductor Index is already up more than 72% year-to-date; Marvell has more than tripled.

The timing is fortunate. Friday's brutal chip selloff — which erased $1.3 trillion in market value across the sector — hit Marvell with a 16.7% single-day decline. The S&P 500 announcement provides a near-term catalyst to stabilise the stock and attract fresh institutional capital.

## The Custom Silicon Revolution

Huang's endorsement reveals a deeper structural shift in the AI hardware stack. The largest cloud companies are no longer content to buy Nvidia's GPUs off the shelf. They want custom chips optimised for their specific workloads — chips that squeeze more inference throughput per watt, handle proprietary model architectures more efficiently, and reduce dependency on a single supplier.

This trend is excellent for companies like Marvell and its larger rival Broadcom, which design tailor-made data centre chips. It is potentially less excellent for Nvidia's long-term GPU monopoly pricing, though Huang has elegantly positioned Nvidia as the ecosystem anchor rather than the competitor — investing in Marvell rather than fighting it.

## The India Angle

Marvell's rise is inextricable from Indian engineering talent. The company maintains significant design centres in India, where teams work on the networking, optical interconnect, and custom silicon solutions that drive its AI growth. Across the industry, Indian chip designers at Marvell, Broadcom, Qualcomm, and the in-house silicon teams at Google, Amazon, and Microsoft are at the centre of the custom chip revolution.

For NRI investors, Marvell's S&P 500 entry offers a distinct angle on the AI trade. While Nvidia remains the consensus AI semiconductor play, Marvell represents a bet on the next layer of the stack — the custom infrastructure that hyperscalers are building to differentiate their AI platforms. The stock is volatile, richly valued, and dependent on a handful of hyperscaler customers. But if Huang is right about the direction of the industry, the company building the transmission may end up mattering as much as the one building the engine.

The risk is concentration. Marvell's custom chip revenue is driven by a small number of very large customers. If any single hyperscaler shifts its silicon strategy — or brings more design work in-house — the impact would be immediate. Nvidia's endorsement provides a buffer, but it is worth remembering that Huang's $2 billion investment also means his praise is not entirely disinterested. When the CEO of your largest partner calls you a trillion-dollar company, the market listens. Whether the earnings follow is a different question entirely."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
