#!/usr/bin/env python3
"""Technology writer — 2026-07-14 02:00 PDT run"""

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


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-20260714"


articles = [
    # ── Article 1: LTIMindtree + Anthropic ─────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "LTIMindtree Just Signed Anthropic and Disclosed $150 Million in AI Revenue. The Indian IT Playbook Is Changing Fast.",
        "subheadline": "CEO Venu Lambu says AI revenue will outpace traditional services as LTM bets that deploying Claude to enterprise clients creates a new market, not a disruption.",
        "slug": make_slug("ltimindtree-anthropic-ai-revenue-150-million-venu-lambu"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "LTIMindtree is a major employer of Indian tech talent on H-1B visas in the US. Its AI pivot signals whether tens of thousands of Indian IT workers will be retraining as AI deployment engineers or watching their roles shrink.",
        "tags": ["indian-it", "ai", "anthropic", "ltimindtree", "enterprise-ai", "claude"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-ltm-expects-ai-revenue-outpace-traditional-services-ceo-says-2026-07-14/"},
            {"name": "Business Wire — LTIMindtree Anthropic Partnership", "url": "https://www.businesswire.com/news/home/ltimindtree-anthropic-partnership"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Server racks inside a modern data center — the infrastructure underpinning enterprise AI deployments",
        "image_attribution": "Pexels",
        "body": """LTIMindtree's CEO has made a declaration that would have sounded delusional two years ago: he expects AI revenue to outpace the company's traditional services business. Given that LTIMindtree — formerly Larsen & Toubro Infotech and Mindtree — was built on the classic Indian IT model of labour arbitrage, project delivery and staff augmentation, the statement is worth parsing carefully.

Venu Lambu, who took over as CEO earlier this year, told Reuters on Monday that LTIMindtree has signed a strategic partnership with Anthropic to deploy Claude, the AI lab's frontier model, to enterprise clients. In the same breath, the company disclosed its AI revenue for the first time: $150 million on a quarterly run-rate basis, or roughly 12 percent of total revenue, across what it calls three "AI-native" businesses.

## The Number in Context

That 12 percent figure is striking. Larger peer HCLTech, which reported its Q1 results last week, disclosed $171 million in "advanced AI" revenue for the June quarter — but that represented only 4.6 percent of its overall sales. LTIMindtree, a smaller company, is running a higher AI revenue concentration.

The distinction matters because LTM draws a sharp line between "AI-native" work — products and services where AI is designed as a core component from the ground up — and "enterprise AI," which involves embedding AI into clients' existing technology stacks. The company does not count the latter in its AI revenue bucket. If it did, the number would be significantly larger.

## The Anthropic Bet

The Anthropic partnership is the more forward-looking move. While TCS has committed to building up to 8,900 forward-deployed engineers and HCLTech has been growing its advanced AI practice, LTIMindtree is betting on a platform partnership model — essentially becoming the systems integrator that helps enterprises adopt specific frontier models.

"Pretty much all deals have an AI component to them," Lambu told Reuters, but added that expensive frontier models are not needed for every business scenario. The implementation market, he argued, is where IT firms can "add the right context at the right costs."

This is a pointed rebuttal to the bear case that has hammered Indian IT stocks this year. The Nifty IT index has fallen more than 23 percent year-to-date, on course for its second-biggest annual loss since 2008, as investors worry that AI tools will shrink the need for large engineering teams and compress project timelines.

## What This Means for Indian Tech Workers

Lambu's framing offers a cautiously optimistic counter-narrative, but it comes with caveats. Enterprise AI adoption, he acknowledged, is still in early stages — he expects it to accelerate in the second half of fiscal year 2027. And a "big concern" for clients remains token costs, with AI firms increasingly shifting to usage-based pricing that can spiral unpredictably.

For the tens of thousands of Indian professionals working at LTIMindtree and its peers on H-1B and L-1 visas in the United States, the strategic bet has direct career implications. Companies that build credible AI deployment practices will likely reskill and redeploy their workforces into higher-value roles — forward-deployed engineers, AI governance consultants, model fine-tuning specialists. Companies that don't will find their traditional project pipelines shrinking.

LTIMindtree's Q1 revenue rose 6.1 percent year-on-year, a respectable if unspectacular number. The real question is whether the Anthropic partnership and the broader AI-native strategy can drive the kind of non-linear growth that would justify a re-rating of the stock — and a rethinking of what "Indian IT" actually means in the age of foundation models.

For NRI investors tracking the $315 billion sector, the signal is clear: the companies that are disclosing AI revenue with confidence are the ones betting they can make the transition. The ones staying quiet may have less to show.""",
    },
    # ── Article 2: Nvidia Asia whitelist ────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Nvidia Just Cut More Than Half Its Asian Customers From Its AI Chip Buyer List. India's AI Ambitions Could Feel the Chill.",
        "subheadline": "A new compliance whitelist aimed at blocking Chinese diversion has excluded over half of Nvidia's previous customers in Singapore, Malaysia and Japan — and the ripple effects extend well beyond those three countries.",
        "slug": make_slug("nvidia-halves-asia-ai-chip-whitelist-india-impact"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "India's booming AI data centre buildout, led by Yotta, Nxtra and the Tata-Nvidia partnership, depends on reliable access to Nvidia GPUs. Tighter US export compliance could slow India's AI infrastructure just as the government bets big on sovereign AI.",
        "tags": ["nvidia", "ai-chips", "export-controls", "semiconductor", "us-china", "india-ai"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/nvidia-halves-asia-buyer-list-china-chip-crackdown-ft-reports-2026-07-14/"},
            {"name": "Financial Times", "url": "https://www.ft.com/content/nvidia-asia-ai-chip-whitelist"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Jen-Hsun_Huang_2025.jpg",
        "image_caption": "Nvidia CEO Jensen Huang, whose company has intensified compliance checks on its Asian AI chip buyers",
        "image_attribution": "Wikimedia Commons",
        "body": """Nvidia has more than halved the number of Asian companies authorised to buy its AI chips, according to a Financial Times report that landed Monday and immediately reframed the debate about who gets to build AI infrastructure in Asia.

The chipmaker has created a new "white list" of approved customers — companies that have passed significantly tougher compliance checks designed to prevent its cutting-edge Blackwell processors from reaching China through third-country intermediaries. Over the last few months, Nvidia has intensified due diligence in Singapore, Malaysia and Japan, three countries where neo-cloud providers had been rapidly scaling GPU clusters.

Under the renewed review, more than half of Nvidia's previous customers — especially smaller cloud providers — were excluded from the approved buyer list. Companies that failed the initial review can make changes and reapply, but the barrier to entry has risen sharply.

## Why This Is Happening

The crackdown follows guidance issued by the U.S. Commerce Department in May, which aimed specifically at curbing advanced AI chips from reaching overseas subsidiaries of Chinese companies. The concern, according to Commerce officials, is that Nvidia's Blackwell processors — the most powerful AI training chips commercially available — may have been exported to Chinese-linked entities operating in Malaysia and other Southeast Asian nations, despite existing U.S. export restrictions.

The move is part of a broader tightening. Washington has already blocked Nvidia from selling its most advanced chips directly to China, forced the cancellation of the scaled-down B30A chip designed as a workaround, and pressured the company to implement know-your-customer checks on its global distribution network.

## The India Question

While the FT report names Singapore, Malaysia and Japan as the focus of Nvidia's compliance review, the implications extend to India — a country that has been racing to build sovereign AI infrastructure with Nvidia hardware at its core.

India's AI data centre buildout is accelerating on multiple fronts. Yotta Data Services, which raised $150 million last week specifically to expand its Nvidia GPU cluster, is one of several Indian operators banking on reliable access to Blackwell chips. The Tata Group has partnered with Nvidia to deploy AI infrastructure across India, and the government's India AI Mission has earmarked billions for compute capacity — nearly all of it Nvidia-dependent.

If Nvidia's compliance apparatus expands its scrutiny to Indian buyers, or if the tighter controls create supply bottlenecks that push Indian data centre operators down the queue, the consequences could slow India's AI timeline at a critical moment.

Indian cloud operators are not subject to the same diversion risk as Southeast Asian entities with Chinese ownership ties. But the compliance infrastructure Nvidia is building does not distinguish between strategic intent and operational geography — it applies a single, rigorous standard across Asia.

## What NRI Investors Should Watch

For Indian-origin investors with exposure to the semiconductor supply chain — whether through Nvidia stock, Indian data centre plays, or the broader AI infrastructure thesis — the whitelist development introduces a new risk vector. Nvidia's due diligence is not a one-time event; it is an ongoing compliance regime that could expand in scope.

TSMC, which manufactures Nvidia's Blackwell chips, is due to report its Q2 earnings on Thursday. Any commentary from TSMC management about regional demand patterns or customer allocation will be closely watched for clues about how the whitelist is affecting order books.

For Indian tech professionals working at Nvidia — a company with significant engineering teams in Bangalore, Hyderabad and Pune — the compliance tightening also adds a layer of complexity to cross-border collaboration with Southeast Asian teams and customers.

The larger strategic picture is this: the AI chip market is no longer a simple matter of supply and demand. It is now a regulated market, shaped as much by geopolitical compliance as by commercial appetite. India, which positioned itself as a neutral beneficiary of both American technology and global demand, may need to navigate that regulatory landscape more carefully than it expected.""",
    },
    # ── Article 3: Microsoft MAI / Satya Nadella ────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "Satya Nadella Is Quietly Building Microsoft's Own AI Models. The Goal: Stop Paying OpenAI and Anthropic.",
        "subheadline": "Microsoft has launched seven in-house MAI models and is routing tens of thousands of Copilot prompts through them. The Indian-born CEO's margin play could redefine who controls the AI stack.",
        "slug": make_slug("satya-nadella-microsoft-mai-models-openai-anthropic"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Satya Nadella, the Indian-born CEO who transformed Microsoft, is making the boldest strategic bet of his tenure. For the thousands of Indian engineers at Microsoft's Hyderabad and Bangalore offices working on AI, MAI could determine the trajectory of their careers.",
        "tags": ["microsoft", "satya-nadella", "ai", "openai", "anthropic", "copilot", "mai"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/microsoft-bets-on-in-house-ai-to-cut-openai-and-anthropic-costs/"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/microsoft-mai-models-office"},
            {"name": "Reuters — Major AI Offerings", "url": "https://www.reuters.com/technology/artificial-intelligence/major-ai-offerings-glance-2026-07-09/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft CEO Satya Nadella, who has reportedly said he feared Microsoft becoming 'the next IBM'",
        "image_attribution": "Wikimedia Commons",
        "body": """Satya Nadella has spent three years positioning Microsoft as the company that brought AI to the enterprise. He invested $13 billion in OpenAI, embedded GPT into Office, and turned Copilot into a $30-per-seat subscription used by hundreds of millions. Now, quietly but unmistakably, he is building a Plan B.

At Build 2026 in June, Microsoft unveiled seven proprietary AI models under the banner "Microsoft AI," or MAI. The lineup includes MAI-Thinking-1, a reasoning model that the company claims matches Anthropic's Claude Opus 4.6 on coding benchmarks. AI chief Mustafa Suleyman, who joined Microsoft after co-founding DeepMind, put the logic in plain terms: "We pay a lot of money to Anthropic, so our goal is to reduce and ultimately eliminate that cost."

## The Quiet Rerouting

Bloomberg subsequently reported that Microsoft has begun routing some Excel and Outlook prompts to MAI rather than to OpenAI or Anthropic. Tens of thousands of prompts per week are already running on Microsoft's own models — a small slice of total Copilot traffic, but a deliberate one.

The economics are straightforward. Every time a user asks Copilot to summarise an email or generate a spreadsheet formula, Microsoft pays OpenAI or Anthropic for the inference. Multiply that across the company's Office user base — north of 400 million seats — and the cost structure becomes a serious drag on margins. MSFT stock has declined roughly 20 percent year-to-date, and the $30 Copilot subscription has struggled to deliver the profitability Wall Street expected.

Owning the model changes the equation. Microsoft does not need MAI to outperform GPT-5.6 on frontier reasoning tasks. It just needs MAI to be good enough for routine office work — drafting emails, parsing data, suggesting formulas — at a fraction of the per-token cost. For these bread-and-butter tasks, "good enough" is a viable standard.

## Nadella's IBM Fear

According to MarketBeat, Nadella has privately expressed concern about Microsoft becoming "the next IBM" — a company that let someone else own the most important technology layer. That fear now drives a three-way hedge: Microsoft holds a stake in OpenAI, embeds Anthropic's Claude in Copilot, and increasingly leans on its own models where the economics make sense.

The strategy also gives Microsoft leverage in future negotiations. Its current discounted pricing deal with OpenAI runs through 2032, but building a credible in-house alternative means Microsoft will not be hostage to whatever OpenAI or Anthropic decide to charge when that deal expires.

## What This Means for Indian Engineers

Microsoft employs tens of thousands of Indian engineers, both in its U.S. offices (where Indians are among the largest H-1B holder groups) and in its massive India Development Centre in Hyderabad and Bangalore. The MAI initiative is likely to create significant internal demand for model training, fine-tuning and deployment talent — roles that sit at the intersection of machine learning and enterprise product engineering.

For Indian AI researchers, the opportunity is notable. Microsoft's India engineering teams have historically focused on Azure, Office and enterprise services. An in-house model family means more ML research and inference optimisation work flowing to India, competing directly with Google's Gemini teams in Bangalore and Amazon's AI labs in Hyderabad.

The signal for NRI tech professionals is broader: the era of "rent AI from a lab and wrap it in a product" is giving way to a hybrid model where large companies build their own AI for commodity tasks and reserve frontier models for the hardest problems. Engineers who can work across both regimes — fine-tuning proprietary models and integrating third-party APIs — will be in the strongest position.

## The Bear Case

The transition is still incremental. OpenAI and Anthropic handle the bulk of Copilot's AI traffic today, and Microsoft has not published a timeline for expanding MAI's scope. There is also a quality risk: if MAI-powered features noticeably underperform, customer goodwill could erode faster than costs drop.

For Anthropic, which filed confidentially for an IPO in June, and OpenAI, which is reportedly preparing a similar filing, the development is a warning. Their biggest enterprise distribution partner is now also a competitor. The "picks and shovels" thesis for AI lab stocks just got a complication.

MSFT currently trades at roughly 22 times forward earnings — a discount to both the S&P 500 and its own five-year average. Whether Nadella's hedge pays off will depend on how quickly MAI can absorb routine workloads without degrading the Copilot experience. For now, the Indian-born CEO who bet the company on AI is quietly ensuring Microsoft does not become captive to the technology it helped popularise.""",
    },
]

# ── Insert ──────────────────────────────────────────────────────────────
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
