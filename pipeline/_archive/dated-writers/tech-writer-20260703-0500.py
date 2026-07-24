#!/usr/bin/env python3
"""Videshi Tech Writer — July 3, 2026 05:00 PDT run"""
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

# ─────────────────────────────────────────────────────────
# ARTICLE 1: Microsoft Frontier + AWS FDE arms race
# ─────────────────────────────────────────────────────────

article1_body = """In the span of 48 hours, the two largest cloud companies on the planet announced they would embed thousands of AI engineers directly inside their customers' offices. The message to Indian IT services firms was hard to miss: we're coming for your business.

On June 30, Amazon Web Services committed $1 billion to a new Forward Deployed Engineering division. Two days later, Microsoft raised the stakes with a $2.5 billion investment in a standalone entity called Microsoft Frontier Company, staffed by 6,000 industry and engineering specialists. Together, the two announcements represent the largest single-week commitment to enterprise AI deployment in history.

## What forward-deployed engineers actually do

The concept is borrowed from Palantir, which popularised it over a decade ago. Small pods of five or six engineers embed directly inside a client organisation for roughly 45 days. They work alongside the client's own teams — not to train them on software, but to build production-grade AI systems from the inside out. When the engagement ends, the customer owns the code, the models, and the workflows.

AWS vice president Francessca Vasquez told CNBC that the model is a direct response to a fundamental shift in corporate appetite. "The currency that customers are always talking about right now is speed," she said. Early clients include the NBA, the NFL, Southwest Airlines, and Ricoh.

Microsoft's version is arguably more ambitious. Judson Althoff, CEO of Microsoft Commercial Business, explicitly positioned the Frontier Company as larger than anything competitors have built. "This goes beyond what has been labelled as Forward-Deployed Engineering," he wrote. The entity will partner with the London Stock Exchange Group, Unilever, Land O'Lakes, and — in a telling detail — Accenture itself.

## Why Indian IT should pay attention

The uncomfortable truth is that forward-deployed engineering is a repackaging of what TCS, Infosys, Wipro, and HCLTech have done for three decades: send skilled engineers to client sites to build and implement technology systems. The Indian IT services industry generates $283 billion in annual revenue largely on this model.

The difference is that Microsoft and Amazon are bundling their own AI platforms into the engagement. A TCS consultant might recommend Azure or AWS; a Microsoft Frontier engineer *is* Azure. The neutrality that Indian IT firms sell as a strength could become a weakness when the cloud vendor shows up with both the tools and the talent.

The timing compounds the threat. Palantir CEO Alex Karp last week called the token-based pricing of AI labs like OpenAI and Anthropic a "wealth tax" that drains enterprise budgets without producing durable outcomes. Nifty IT surged 4.6% on the back of his remarks. But if the implication was that enterprises would turn to IT services firms for help, Microsoft and Amazon have now offered a third option: let the cloud provider itself do the deployment.

Accenture's inclusion as a Microsoft Frontier launch partner hints at how the relationship might evolve — less a replacement and more a reshuffling, where Indian IT firms become subcontractors to the platform's own deployment arm rather than the primary integrators.

## The diaspora calculus

For Indian tech professionals in the US, the FDE expansion is a mixed signal. Microsoft plans to hire 6,000 specialists; AWS is building a team of "thousands." Many of these positions will demand the exact skills that Indian engineers on H-1B visas carry — cloud architecture, machine learning engineering, enterprise data systems. The forward-deployed model could create thousands of new high-skilled jobs even as it pressures the offshore delivery centres that employ hundreds of thousands back in India.

The question for the next earnings season is whether Indian IT chiefs frame this as a competitive threat or a partnership opportunity. If the last week is any guide, the answer will be both — and the companies nimble enough to ride the wave, rather than fight it, will come out ahead."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Microsoft and Amazon Just Bet $3.5 Billion That They Can Replace Your IT Consulting Firm",
    "subheadline": "Both cloud giants launched enterprise AI deployment armies within 48 hours of each other. For TCS, Infosys, and the rest of Indian IT, the forward-deployed engineer era is a reckoning and an opportunity.",
    "slug": make_slug("microsoft-amazon-fde-ai-deployment-indian-it"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT services firms that employ hundreds of thousands of H-1B professionals are directly threatened by Microsoft and Amazon building in-house deployment arms — but the FDE hiring boom could also create thousands of new high-skilled roles for Indian engineers in the US.",
    "tags": ["microsoft", "amazon", "aws", "ai-deployment", "indian-it", "forward-deployed-engineers", "satya-nadella"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/microsoft-launches-firm-help-companies-adopt-ai-with-25-billion-2026-07-02/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/07/02/microsoft-launches-its-own-ai-deployment-company-with-2-5-billion-commitment/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/amazons-aws-commits-1-billion-toward-new-unit-embedded-ai-engineers-2026-06-30/"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/amazon-doubles-down-on-enterprise-ai-bet"},
        {"name": "CNBC", "url": "https://www.cnbc.com/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg/330px-MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
    "image_caption": "Satya Nadella, CEO of Microsoft, whose company launched a $2.5 billion AI deployment venture",
    "image_attribution": "Wikimedia Commons",
    "body": article1_body
}


# ─────────────────────────────────────────────────────────
# ARTICLE 2: SK Hynix $29.4B Nasdaq listing
# ─────────────────────────────────────────────────────────

article2_body = """SK Hynix, the South Korean company that makes the memory chips powering nearly every major AI system on the planet, is about to become available on Wall Street. Its planned Nasdaq listing on July 10 aims to raise up to $29.4 billion — a figure that would make it one of the largest stock offerings in market history, rivalling Saudi Aramco's 2019 debut.

The company filed an amended S-1 with the SEC this week, planning to issue up to 17.79 million new shares as American Depositary Receipts under the ticker SKHY. Ten ADRs will represent one common share. Bookbuilding begins July 6, with final pricing on July 9. Goldman Sachs, JPMorgan, Citigroup, and Bank of America are managing the sale.

## Where the money goes

Every dollar raised goes to the company, not to existing shareholders cashing out. The capital will fund a massive semiconductor buildout: $21.5 billion for a new fabrication plant at the Yongin Semiconductor Cluster, due for completion in February 2027; $12.9 billion for a high-bandwidth memory packaging plant in Cheongju; and the remainder for EUV lithography equipment from ASML, expected by December 2027.

The listing landed one day after Samsung Electronics, SK Hynix, and the South Korean government announced a combined $590 billion plan for a new chip manufacturing hub — a national bet that memory semiconductors will remain the foundation of AI infrastructure for the foreseeable future.

## The AI memory bottleneck

SK Hynix's pitch to investors rests on a simple thesis: artificial intelligence runs on memory, and there is not nearly enough of it. The company is the dominant supplier of high-bandwidth memory (HBM) chips to Nvidia, the components that allow AI accelerators to process the enormous datasets required for training and running frontier models.

The company's shares have quadrupled in 2026, outperforming both Samsung and US rival Micron Technology. It recently overtook Samsung as South Korea's most valuable publicly traded company — a remarkable reversal for a firm that nearly collapsed under debt two decades ago.

"Memory, not processing power, will determine who wins the artificial intelligence race," industry analysts at KED Global noted this week, projecting that demand for AI-grade memory could rise by a factor of one million over the next decade.

## What this means for Micron and India's chip ambitions

For Sanjay Mehrotra's Micron Technology, the listing intensifies an already fierce rivalry. Micron posted a record $41 billion quarter in its latest earnings, driven by the same HBM demand. But SK Hynix's war chest — potentially $29 billion in fresh capital — will allow it to outspend Micron on next-generation fabrication at a scale that is difficult to match.

The implications reach India directly. Micron's $2.75 billion assembly, testing, and packaging plant in Sanand, Gujarat — India's first major semiconductor facility — began commercial production earlier this year. A better-capitalised SK Hynix could put pressure on Micron's margins, indirectly affecting how aggressively Mehrotra invests in expanding India operations.

For Indian semiconductor engineers, the listing creates opportunity in a different direction. SK Hynix's expansion plans will require thousands of specialised engineers for its new fabs and packaging facilities. South Korea's chip industry has increasingly recruited from Indian technical universities, a pipeline that this capital infusion will accelerate.

## The NRI investor angle

The ADR listing also matters for the tens of thousands of Indian professionals working in the US semiconductor industry. For the first time, they can invest directly in one of AI's most critical supply chain companies without navigating foreign exchange or Korean brokerage accounts. The ticker SKHY will trade on Nasdaq alongside Micron, Nvidia, and Intel.

But the valuation demands caution. SK Hynix is currently valued at roughly $1.2 trillion on the Korean exchange. Analysts at CLSA note that if it achieves even Micron's valuation multiple in the US, the Korean-listed shares would need to rise further to match. The bet is that American investors will pay a premium for pure-play AI memory exposure that the diversified semiconductor giants cannot offer.

The listing window is narrow. With OpenAI and Anthropic both preparing their own IPOs, and SpaceX having just completed a record $75 billion offering, the market's appetite for massive tech listings may not last indefinitely. As Deutsche Bank's Adrian Cox put it this week: "There is no guarantee that there will be enough investor appetite to absorb hundreds of billions of dollars in rapid-fire demand."

SK Hynix is striking while the iron is hot. Whether the iron stays hot through July 10 is the $29 billion question."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "SK Hynix Wants $29 Billion From Nasdaq. It Could Be the Largest Tech Listing in a Decade.",
    "subheadline": "The South Korean chipmaker that supplies Nvidia's AI memory is about to go public in the US. For Sanjay Mehrotra's Micron and India's semiconductor ambitions, the stakes just went up.",
    "slug": make_slug("sk-hynix-29-billion-nasdaq-listing-ai-memory"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors and Indian semiconductor professionals in the US can invest directly in AI's most critical memory supplier via Nasdaq ADRs, while the listing intensifies competition for Micron's India fab in Gujarat.",
    "tags": ["sk-hynix", "nasdaq", "ipo", "semiconductor", "ai-memory", "micron", "sanjay-mehrotra", "nvidia"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/sk-hynix-raise-up-29-billion-us-listing-2026-06-25/"},
        {"name": "TheStreet", "url": "https://www.thestreet.com/technology/after-beating-samsung-tech-titan-files-for-ipo"},
        {"name": "CoinCentral", "url": "https://coincentral.com/sk-hynix-stock-nasdaq-debut/"},
        {"name": "KED Global", "url": "https://www.kedglobal.com/semiconductor-investment/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/openai-anthropic-ipo-ai-stock/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37052613/pexels-photo-37052613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "A close-up of a microprocessor circuit board with intricate chip components",
    "image_attribution": "Pexels",
    "body": article2_body
}


# ─────────────────────────────────────────────────────────
# Insert articles
# ─────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
