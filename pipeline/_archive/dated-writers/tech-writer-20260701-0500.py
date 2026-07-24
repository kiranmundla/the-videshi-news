#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-01 05:00 PT run"""
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

# ─── ARTICLE 1: Oracle AI Purge ─────────────────────────────────────────

oracle_body = """Oracle has disclosed in its annual 10-K filing with the Securities and Exchange Commission that it eliminated 21,000 employees over the past fiscal year — a reduction far larger than the company had previously acknowledged. Global headcount fell from 162,000 to 141,000 as of May 31, 2026, a 13% decline that ranks among the biggest workforce cuts in enterprise technology history.

The company was blunt about the cause. "The adoption and deployment of AI technologies across our operations have resulted, and may continue to result, in reductions to our workforce," Oracle stated in the filing.

## India Bore the Heaviest Blow

According to reporting by Mint and The Hindu Business Line, between 12,000 and 15,000 of those cuts fell on Oracle's Indian operations — roughly half the global total. India is Oracle's single largest workforce base outside the United States, with approximately 50,000 employees spread across Bengaluru, Hyderabad, Mumbai, and other cities before the restructuring began.

The cuts spanned Oracle Health, AI security programmes, SaaS, NetSuite India Development, and cloud operations. They hit every level — from entry-level individual contributors to senior vice presidents.

The manner of departure made headlines across India's tech community. Workers received termination emails at 6 AM, before many had reached their desks. No prior conversations with managers. No HR calls. Just a message from "Oracle Leadership" informing them that their position "will become redundant," followed by an immediate lockout from internal systems.

Severance, while not negligible, was modest relative to the disruption: 30 days of gross pay per year of service, one month of garden leave, two additional months' pay, and limited insurance benefits.

## The $70 Billion Bet Behind the Bloodletting

Oracle is not struggling financially. It reported $3.7 billion in quarterly net income last quarter, a 27% year-over-year increase. Revenue from its cloud infrastructure business has been growing at double-digit rates.

The cuts are about reallocation, not survival.

Larry Ellison's company is in the middle of a $70 billion capital expenditure programme to build AI data centres, anchored by its role in the $500 billion Stargate initiative alongside OpenAI and SoftBank. Analysts at TD Cowen estimate that eliminating 30,000 roles — some estimates run higher than the 10-K figure — could free up $8 billion to $10 billion in annual cash flow. Unlike Google or Microsoft, Oracle funds its AI buildout primarily through debt issuance rather than operating cash flow, making the human cost a direct line item in its financing strategy.

The restructuring has already cost $1.84 billion in severance and related expenses, nearly five times the $374 million Oracle spent on restructuring a year earlier. The company has raised its restructuring budget ceiling to $2.1 billion.

## What This Means for Indian Tech Professionals

Oracle India is not a back-office outpost. Its Bengaluru and Hyderabad teams build core database engines, cloud infrastructure, and health-care software. Eliminating 12,000-plus roles from that talent base signals a structural shift.

For Oracle employees in the United States on H-1B visas, the layoffs carry an additional dimension. H-1B holders who lose their jobs have a 60-day grace period to find a new sponsor, switch visa categories, or leave the country. In a year where Meta, PayPal, Cisco, GitLab, and Intuit have all announced AI-driven layoffs — totalling more than 185,000 cuts across the industry — finding a new sponsor within two months is no longer a safe assumption.

Oracle's own filing warns that further reductions "may continue" as AI adoption deepens. The company that once powered the back end of half the Fortune 500 now sees its future in renting GPU clusters to OpenAI. Whether that trade pays off is a question for shareholders. For 12,000 Indian families who opened a termination email at dawn, the answer has already arrived."""

# ─── ARTICLE 2: SpaceX Nasdaq-100 ───────────────────────────────────────

spacex_body = """On July 7, SpaceX will be added to the Nasdaq-100 index — just three weeks after its initial public offering on June 12. It will be the fastest inclusion of a newly public company in the index's history, made possible by a rule change Nasdaq adopted in May: mega-cap IPOs that would rank among the 40 largest Nasdaq-100 components can now enter the index after just 15 trading days, with previous float requirements waived.

For a company valued at roughly $2 trillion, the eligibility was never in question. SpaceX trades under the ticker SPCX and currently sits around $171, down from a post-IPO peak near $226 but well above its first-day range.

## The Mechanics of Forced Buying

Index inclusion is not a symbolic honour. It triggers real money.

Every fund that tracks the Nasdaq-100 — including the Invesco QQQ Trust, one of the world's most widely held ETFs with over $300 billion in assets — will be required to buy SpaceX shares to match the index weighting. MarketBeat estimates this will generate approximately $4.3 billion in forced institutional buying. Other analysts put the figure closer to $10 billion when accounting for the full ecosystem of Nasdaq-100-tracking products.

SpaceX was already added to the FTSE Russell indices last Friday. Combined with the Nasdaq-100 on July 7, the company will be a mandatory holding in the Russell 1000, Russell 3000, and Nasdaq-100 simultaneously — a trifecta of passive demand hitting a stock with an unusually small public float.

That float constraint matters. SpaceX's lockup agreements prevent insiders from selling until late July at the earliest. Until then, the supply of tradeable shares is limited, and the wave of index-mandated buying could push prices sharply upward, at least temporarily.

## Why NRIs Should Pay Attention

Millions of Indian Americans have their retirement savings in index funds. If you hold QQQ, QQQM, or a target-date fund through your 401(k), IRA, or brokerage account that benchmarks to the Nasdaq-100, you will own SpaceX by next week. No action required — and no opt-out available.

This is not trivial exposure. SpaceX operates two massive businesses: Starlink, the satellite internet constellation generating billions in annual revenue, and the launch division, which commands roughly two-thirds of the global commercial launch market. Its valuation, however, has been volatile — swinging from nearly $3 trillion in market cap (briefly exceeding Microsoft) to its current level in just two weeks of trading.

For NRI investors who prefer low-volatility, diversified index exposure, the addition of a company with this kind of price movement to a core portfolio holding deserves scrutiny. SpaceX is not a mature compounder like Apple or Microsoft. It is a capital-intensive infrastructure company that has never reported public financials, whose revenue mix between government contracts and consumer broadband is evolving, and whose valuation rests on the assumption that Starlink will dominate global connectivity.

Implied volatility on SpaceX options has declined from 110% at listing to around 72% — but that still implies daily moves under 5%, a range most index-fund investors are not accustomed to from a single holding.

## The India Connection

SpaceX's relationship with India remains unresolved. Starlink has applied for satellite broadband licences but has not received regulatory clearance. Reliance Jio's competing satellite broadband ambitions have complicated the regulatory landscape. If Starlink enters India, it could reshape rural connectivity — a prospect that matters to NRIs with family across India's smaller cities and towns.

ISRO, meanwhile, competes with SpaceX on the commercial launch front, offering significantly cheaper satellite deployment through its PSLV and LVM3 vehicles. SpaceX's entry into major stock indices will also draw comparisons with India's own space-tech ecosystem — Agnikul Cosmos, Skyroot Aerospace, Pixxel — none of which have access to the capital markets that just valued a single American rocket company at $2 trillion.

The immediate question for most NRI investors is simpler: check your index fund holdings before July 7. A rocket company is about to land in your retirement portfolio."""

# ─── ARTICLE 3: India-US AI Alliance ────────────────────────────────────

alliance_body = """While the headlines of Prime Minister Narendra Modi's latest US visit focused on defence deals and trade corridors, a quieter but potentially more consequential alignment was taking shape in the technology sphere.

India's Ambassador to the United States, Vinay Mohan Kwatra, held a series of meetings with senior American corporate and technology leaders that signal a deepening of bilateral AI cooperation. Among his interlocutors: Chris Nicholas, CEO of Walmart, on India supply chain investments; and Ylli Bajraktari, head of the Special Competitive Studies Project (SCSP), a think tank led by former Google CEO Eric Schmidt that advises Washington on AI competitiveness.

Kwatra described the SCSP discussion as covering "the trajectory of advanced technologies including Quantum, and the future of AI, including Physical AI and the expanding India-USA cooperation in tech space." Bajraktari was preparing for an upcoming visit to New Delhi for the India-US Forum, where bilateral AI policy will be a central agenda item.

## The Research Pipeline Is Already Open

The diplomatic layer is visible. Underneath, a research infrastructure is being built.

Earlier this year, researchers from both countries convened at Plaksha University in Mohali for a workshop on building US-India research collaborations in AI, organised with the US Embassy in New Delhi. The stated goal: move beyond dialogue and establish sustained, working partnerships.

Rajesh Gupta, distinguished professor and dean at UC San Diego's School of Computing, Information and Data Science, described collaboration as "very high" and revealed a detail that has received almost no coverage: he is involved in building six AI schools across India, funded by American foundations.

"The complementarity is clear," said Rajeev Barua, professor of electrical and computer engineering at the University of Maryland. "The US contributes depth in frontier AI research and global product ecosystems, while India contributes exceptional talent at scale and diverse real-world deployment contexts."

This addresses a concrete market reality. American AI companies need talent, and India produces more AI and machine learning engineers than any other country outside the United States. The collaboration is designed as a bidirectional pipeline — Indian researchers trained to US standards, American companies gaining access to India's deployment scale, and joint research that neither side could produce alone.

## The Diaspora as Infrastructure

The Indian American community is not a bystander in this alignment. It is the connective tissue.

Indian-origin executives run Alphabet, Microsoft, IBM, Adobe, Palo Alto Networks, Micron, and FedEx. Indian researchers hold senior positions at Google DeepMind, OpenAI, Meta AI, and Anthropic. Indians constitute the largest national group among H-1B visa holders, and Indian Americans are among Silicon Valley's most prolific angel investors.

When Sriram Krishnan was appointed as the White House's Senior Advisor for AI policy, it formalised a structural reality: Indian Americans sit at the intersection of American AI capability and Indian deployment potential. The diaspora does not just participate in both systems — it translates between them.

This is why the current moment is significant. Amazon has committed $48 billion to India through 2030, primarily for AI and cloud infrastructure. Google pledged $15 billion for data centres in southern India. Microsoft earmarked $17.5 billion. These are bets that India will become one of the world's largest AI consumption markets — and that the diaspora will supply the engineering talent to build for it.

## What to Watch

The India-US Forum in New Delhi, where Ambassador Kwatra's groundwork is expected to yield specific cooperation frameworks, will be the next milestone. Three areas deserve attention: joint semiconductor research, where India's $12 billion chip programme needs US expertise and equipment; AI governance alignment, as India drafts its own regulatory framework while America debates executive orders; and defence AI, where India's status as a "Major Defence Partner" creates technology transfer pathways that do not exist with most US allies.

For Indian Americans working in technology, this is not distant geopolitics. It shapes visa policy, research funding, hiring priorities, and where careers are built. The bridge between the world's largest AI producer and its largest talent exporter is already constructed. The traffic on it is about to accelerate."""

# ─── Define articles ────────────────────────────────────────────────────

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Oracle's AI Purge Hit India Hardest. 12,000 Workers Got an Email at 6 AM.",
        "subheadline": "The world's largest enterprise software company cut 21,000 jobs in twelve months. Roughly half were in India — its biggest hub outside the United States.",
        "slug": make_slug("oracle-ai-purge-21000-layoffs-india-hub"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "12,000-15,000 Indian workers lost jobs at Oracle's largest international hub; H-1B holders in the US face the 60-day clock in an industry that has shed 185,000 jobs this year.",
        "tags": ["oracle", "layoffs", "ai", "india-tech", "enterprise", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fast Company", "url": "https://www.fastcompany.com/91352867/oracle-layoffs-21000-jobs-cut-ai-saaspocalypse"},
            {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/oracle-layoffs-21000-employees-let-go-in-12-months-company-says-ai-replaced-some-roles-11750699236052.html"},
            {"name": "eWeek", "url": "https://www.eweek.com/news/oracle-axes-up-to-12000-jobs-in-india/"},
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/info-tech/oracle-cuts-12000-india-jobs-in-global-ai-led-restructuring-drive/article69394997.ece"},
            {"name": "The Street", "url": "https://www.thestreet.com/technology/ai-blamed-for-21000-layoffs-at-tech-giant"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Oracle_Headquarters_in_Redwood_City.jpg/1280px-Oracle_Headquarters_in_Redwood_City.jpg",
        "image_caption": "Oracle headquarters campus in Redwood City, California",
        "image_attribution": "Wikimedia Commons",
        "body": oracle_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "SpaceX Joins the Nasdaq-100 on July 7. Your 401(k) Is About to Own a Rocket Company.",
        "subheadline": "Elon Musk's $2 trillion space and AI company enters the most popular growth index after just 15 trading days. If you hold QQQ in your retirement account, you will become a SpaceX investor next week — whether you planned to or not.",
        "slug": make_slug("spacex-nasdaq-100-july-7-nri-401k-index"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Millions of NRIs hold QQQ and Nasdaq-100 index funds in their 401(k) and IRA accounts; SpaceX's forced inclusion changes their portfolio exposure, and Starlink's pending India entry adds a personal stake.",
        "tags": ["spacex", "nasdaq-100", "index-funds", "investing", "starlink", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/06/29/reasons-july-7-monster-day-spacex/"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/articles/spcx-stock-faces-43b-index-inflow-and-august-lock-up-risk-2026-06-30/"},
            {"name": "Investors Business Daily", "url": "https://www.investors.com/research/options/spacex-stock-options-cheap-nasdaq-100-inclusion/"},
            {"name": "TradersUnion", "url": "https://tradersunion.com/interesting-articles/view/spacex-index-inclusion-triggers-fresh-gains-for-nasdaq-100/"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/CRS-9_mission_%2828348649546%29.jpg/1280px-CRS-9_mission_%2828348649546%29.jpg",
        "image_caption": "A SpaceX Falcon 9 rocket during launch",
        "image_attribution": "Wikimedia Commons",
        "body": spacex_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India and America Are Quietly Building an AI Pact. The Diaspora Is the Bridge.",
        "subheadline": "As Modi visits Washington, India's ambassador met with top US tech and defence leaders while American universities build AI schools across India. The alliance is deeper than the headlines suggest.",
        "slug": make_slug("india-us-ai-alliance-diaspora-kwatra-modi"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian Americans sit at the intersection of US AI capability and Indian deployment potential — running the companies, staffing the labs, and now shaping the policy frameworks that govern both sides.",
        "tags": ["india-us-relations", "ai", "research", "diaspora", "tech-policy", "modi"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indian-envoy-meets-us-corporate-and-tech-leaders/"},
            {"name": "SPAN Magazine / US Embassy New Delhi", "url": "https://theindianeye.com/forging-the-next-wave-of-ai-innovation/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/amazon-india-ai-data-centers-investment-e8ee46c9"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/apple-google-strike-gemini-deal-revamped-siri-major-win-alphabet-2026-01-13/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Prime_Minister_Modi_in_a_family_photograph_during_the_AI_Action_Summit%2C_in_Paris%2C_France_on_February_11%2C_2025.jpg/1280px-Prime_Minister_Modi_in_a_family_photograph_during_the_AI_Action_Summit%2C_in_Paris%2C_France_on_February_11%2C_2025.jpg",
        "image_caption": "Prime Minister Modi with world leaders at the AI Action Summit in Paris, February 2025",
        "image_attribution": "Wikimedia Commons",
        "body": alliance_body,
    },
]

# ─── Insert ─────────────────────────────────────────────────────────────

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  —  {art['headline']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
