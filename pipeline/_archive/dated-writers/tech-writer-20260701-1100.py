#!/usr/bin/env python3
"""Technology writer — 2026-07-01 11:00 PT batch"""
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
    return slug[:70].rstrip('-') + "-20260701"

# ── Article 1: Together AI $800M raise ──────────────────────────────────
art1_body = """A twelve-year-old boy in Noida typed a program in BASIC that said "Hi Vipul, how are you?" and felt, for the first time, that a machine could think. Three decades later, that boy — Vipul Ved Prakash — has built an $8.3 billion company whose entire purpose is to make sure machines think on terms that aren't dictated by a handful of Silicon Valley gatekeepers.

Together AI announced on Wednesday that it has raised $800 million in a Series C round led by Saudi Aramco's venture arm, more than doubling its valuation from $3.3 billion just seventeen months ago. Nvidia, Salesforce Ventures, Vista Equity Partners, General Catalyst, and MediaTek parent Pegatron are among the backers. Annual bookings have crossed $1.15 billion. For a company barely four years old, those numbers border on absurd.

## The Anti-OpenAI

What makes Together AI unusual in a landscape of AI fundraising superlatives is what it is *not*. It doesn't build proprietary models. It doesn't compete with OpenAI or Anthropic for the crown of most powerful AI. Instead, it provides the cloud infrastructure — optimised, affordable, fast — on which open-source models like DeepSeek, MiniMax, and Kimi actually run.

Think of it as the power grid for the open-source AI movement. Enterprises that don't want to hand their data and their dependence to a single vendor can train, fine-tune, and deploy any model on Together's platform at costs the company claims are significantly lower than AWS, Azure, or Google Cloud.

"The future of AI won't be owned by a few companies," Prakash said in a statement. "It will be built by millions of developers and businesses, and open-source models are making that possible."

## A Noida-to-Cupertino Arc

Prakash's career reads like a chapter from the diaspora playbook. He grew up in Noida, went from building anti-spam systems (Cloudmark, Vipul's Razor — still used today) to founding Topsy Labs, a social search company that Apple acquired in 2013 for over $200 million. He spent five years as a senior director inside Apple's engineering machine before leaving to start Together AI in 2022.

That trajectory — deep technical credibility built in India, scaled in the Valley, then deployed to challenge the industry's biggest incumbents — is becoming a recurring pattern. Prakash now sits alongside Sundar Pichai, Satya Nadella, and Arvind Krishna as Indian-origin founders and executives shaping how the world's most transformative technology gets built.

## Why NRIs Should Care

The $800 million raise matters beyond the headline for at least three reasons.

First, Together AI's open-source posture directly benefits Indian AI startups that can't afford the API costs of OpenAI or Anthropic. Companies like Sarvam AI and Krutrim — building India-specific language models — need affordable inference infrastructure. Together AI is becoming it.

Second, the company's infrastructure expansion plans are enormous: a 50-fold increase in computing capacity over five years, including clusters of 36,000 Nvidia GB200 chips. That kind of build-out means hiring — and the talent pipeline for AI infrastructure engineering runs heavily through IITs and India's deep-tech ecosystem.

Third, the Saudi Aramco Ventures lead is telling. Gulf sovereign capital is placing bets on AI infrastructure the way it once bet on petrochemical pipelines. For Indian engineers and entrepreneurs navigating the AI economy, Together AI's model — infrastructure-as-a-platform rather than model-as-a-product — represents a category with fewer competitors and more durable margins.

Prakash, characteristically, would rather talk about the engineering than the money. In an earlier interview with Forbes India, he recalled that first BASIC program in Noida: "It still gives me goosebumps." At $8.3 billion, the goosebumps are probably mutual."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "A Noida Kid's BASIC Program Led to an $8.3 Billion AI Company. Together AI Just Raised $800 Million.",
    "subheadline": "Vipul Ved Prakash's open-source cloud platform, backed by Aramco, Nvidia and Salesforce, is becoming the infrastructure layer the AI industry didn't know it needed.",
    "slug": make_slug("together-ai-800m-vipul-prakash-noida-open-source"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin founder from Noida builds $8.3B AI infrastructure company; platform enables affordable AI for Indian startups like Sarvam AI and Krutrim; major hiring pipeline from Indian engineering talent.",
    "tags": ["ai", "indian-tech", "startup-funding", "open-source", "silicon-valley", "together-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/together-ai-raises-800-million-83-billion-valuation-2026-07-01/"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/ai/togetherais-vipul-ved-prakash-democratising-ai-access-with-opensource-solutions/95095/1"},
        {"name": "SiliconANGLE", "url": "https://siliconangle.com/2025/02/04/together-ai-raises-305m-ai-optimized-public-cloud/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/07/Vipul_Ved_Prakash.jpg",
    "image_caption": "Vipul Ved Prakash, co-founder and CEO of Together AI",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ── Article 2: Meta enters the cloud business ──────────────────────────
art2_body = """Mark Zuckerberg's company spent $135 billion building data centres this year. Now it wants to rent some of them out.

Bloomberg reported on Wednesday that Meta Platforms is building a cloud computing business to sell excess AI capacity to outside developers and enterprises — a move that sent Meta's stock surging 11 percent and cratered shares of neocloud providers CoreWeave (down 14 percent) and Nebius (down 12 percent) in a single morning.

The project, internally called Meta Compute, would do two things. First, it would let developers access AI models hosted on Meta's infrastructure — including its Muse Spark models — and pay for the computing power to run them, similar to how Amazon Web Services' Bedrock platform works. Second, it would sell raw AI computing capacity, the kind of brute-force GPU access that neoclouds like CoreWeave and Lambda have built entire businesses around.

## The Numbers Are Staggering

Meta has projected capital expenditures of $125 billion to $145 billion in 2026 alone, nearly all of it on AI infrastructure. Big Tech collectively is expected to spend more than $700 billion on AI infrastructure this year, up from around $400 billion in 2025. The question the market has been asking — politely at first, now insistently — is: what is the return on all this concrete and silicon?

Selling cloud access is one answer. It turns a cost centre into a revenue stream and a strategic moat, positioning Meta alongside Amazon, Microsoft, and Google as the fourth hyperscaler with a commercial cloud offering.

Zuckerberg himself hinted at this in late May when he said a public cloud business was "on the table" if Meta accumulated more data centre capacity than it needed. The Bloomberg report suggests that table now has blueprints on it.

## The Carnage Downstream

The immediate casualties are the neoclouds. CoreWeave holds $35.2 billion in contracts with Meta alone — over a third of its total backlog. Nebius signed a $27 billion infrastructure deal with Meta just four months ago. Both companies are now watching their largest customer potentially become their fiercest competitor.

"This is very similar to the situation SpaceX found itself in," Gil Luria of D.A. Davidson told Reuters. "The impact of adding Meta's capacity to the market is more likely to be on neoclouds than the big hyperscalers."

For Indian engineers and product managers at these companies — and there are many — the strategic uncertainty is personal. A neocloud whose anchor client becomes a rival has a very different hiring trajectory than one whose revenue is secure.

## What It Means for the Indian Tech Ecosystem

The ripple effects run deeper than share prices.

**Indian IT services firms** — TCS, Infosys, Wipro, HCL Tech — have been building cloud migration and managed services practices around AWS, Azure, and Google Cloud for a decade. A fourth hyperscaler would mean a fourth ecosystem to staff, certify, and sell. That's opportunity if they move early. It's commoditisation if they don't.

**Indian AI startups** benefit from more competition among cloud providers. If Meta's entry drives down the cost of inference compute — already falling sharply — the economics of building AI products in India improve further. A company training a Hindi language model on Together AI today might run inference on Meta Compute tomorrow at a fraction of the cost.

**Meta's India workforce**, numbering in the thousands, is at the centre of this pivot. Santosh Janardhan, Meta's head of infrastructure, has been a key figure in the company's chip partnerships with Nvidia, AMD, and Amazon. If Meta Compute becomes a real product, its engineering leadership will draw heavily from the same Indian talent pool that built the first three hyperscaler clouds.

The irony is thick: Meta, which built the world's most visited social apps, may end up being more valuable to Wall Street as a plumbing company. For the Indian tech ecosystem, the plumbing matters more than the photos."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Is Building a Cloud Business. The Neoclouds It Hired Are Already Bleeding.",
    "subheadline": "Zuckerberg's company plans to sell excess AI computing capacity, sending CoreWeave and Nebius stocks into freefall and reshaping the cloud landscape Indian IT firms depend on.",
    "slug": make_slug("meta-cloud-business-ai-compute-coreweave-nebius"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Thousands of Indian engineers work at Meta and neocloud firms facing strategic upheaval; Indian IT services giants (TCS, Infosys, Wipro) may need to build expertise around a fourth hyperscaler; cheaper AI compute benefits Indian startups.",
    "tags": ["meta", "cloud-computing", "ai-infrastructure", "coreweave", "indian-it", "silicon-valley"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-building-cloud-business-sell-excess-ai-capacity-bloomberg-news-reports-2026-07-01/"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/meta-stock-cloud-business-coreweave-ae9fc31a"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/metas-reported-cloud-push-weighs-on-ai-compute-and-data-center-stocks-8b11e024"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/meta-stock-rallies-ai-cloud-business-coreweave/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "Server racks in a modern data centre — the infrastructure Meta wants to rent out",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}

# ── Article 3: Anthropic export ban lifted, IPO runway clears ────────
art3_body = """For seventeen days, Anthropic's most powerful AI models were frozen. Not by a technical failure or a funding shortfall, but by the United States government.

On Tuesday evening, the Commerce Department lifted export controls on Claude Fable 5 and Mythos 5, Anthropic's frontier AI models that had been suspended since mid-June over national security concerns. "We'll begin restoring access tomorrow," Anthropic said in a statement. Commerce Secretary Howard Lutnick framed the resolution as a win for American AI leadership.

What happened in those seventeen days — and what it reveals about the emerging regulatory architecture around AI — should concern every Indian professional working at the frontier of the technology.

## What Went Wrong

The trouble started when Amazon, Anthropic's largest backer with over $13 billion invested, identified a jailbreak in Fable 5 — a way to circumvent the model's safety guardrails that could, in theory, enable cyberattacks. The Commerce Department responded with an export control order that required Anthropic to suspend all access by foreign nationals, regardless of where they were located.

That last clause is the one that stung. It meant that Anthropic's own employees — including engineers on H-1B and other work visas — could not access the models they helped build. Indian nationals, who constitute a significant share of AI research teams across Silicon Valley labs, found themselves locked out of their own work product overnight.

Anthropic disabled public access to both Fable 5 and Mythos 5 entirely. For a company that confidentially filed for an IPO just weeks earlier — with valuations being discussed north of $1 trillion — the timing was exquisitely bad.

## The IPO Runway Clears

With the ban lifted, Anthropic can now proceed toward what would be one of the largest technology IPOs in history. Polymarket odds put the probability of an Anthropic IPO in 2026 at 76 percent. OpenAI, facing its own regulatory friction with GPT-5.6 models restricted to government-approved customers, has just a 24 percent probability.

The resolution also matters for Anthropic's commercial partners. Amazon Web Services, which hosts Anthropic's models through its Bedrock service, and Broadcom, which has committed to supply 3.5 gigawatts of computing capacity through Google's AI processors starting in 2027, both needed regulatory clarity to plan their own capital allocation.

Deutsche Bank analyst Adrian Cox noted that the Anthropic and OpenAI listings would provide investors with "a pure-play benchmark" for valuing AI companies — something the market desperately needs as it tries to separate genuine capability from hype.

## The Regulation Problem Nobody Wants to Talk About

The deeper issue isn't about one company or one model. It's about a regulatory framework that can freeze a company's products — and by extension, its employees' livelihoods — with essentially no notice.

For Indian AI professionals in the United States, the episode adds a new dimension of precarity. An H-1B visa holder working on frontier AI models now faces a double vulnerability: the immigration system's existing constraints, plus the possibility that their employer's product could be suspended by executive action, making their role itself temporarily impossible to perform.

India's own AI governance framework is still taking shape. The country signed the Pax Silica accord with 34 other nations last week and has been developing draft AI regulation that tries to balance innovation with oversight. But the Anthropic precedent — a government unilaterally disabling a company's most advanced product — is the kind of regulatory risk that Indian AI startups building on American infrastructure should be stress-testing against.

The resolution, for now, is a relief. Anthropic's models are coming back online. The IPO machine is whirring again. But somewhere in the seventeen-day gap, the AI industry learned something it already suspected: the biggest risk to frontier AI isn't technical. It's political.

And in a workforce where Indian talent is disproportionately represented at the frontier, the politics are personal."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "The US Government Froze Anthropic's Best AI for 17 Days. Then It Unfroze It. The Damage Was Already Done.",
    "subheadline": "Export controls on Claude Fable 5 locked out foreign-national employees — including Indian engineers — and threw a trillion-dollar IPO into doubt. The ban is lifted. The precedent is not.",
    "slug": make_slug("anthropic-export-ban-lifted-claude-ipo-ai-regulation"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian AI researchers on H-1B visas were locked out of their own models at Anthropic; episode exposes a new regulatory risk for Indian professionals at frontier AI labs; India's own AI governance framework must account for this kind of precedent.",
    "tags": ["ai-regulation", "anthropic", "ipo", "h1b", "indian-tech", "export-controls"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/anthropic-gets-all-clear-to-let-foreigners-use-latest-model-ahead-of-crucial-ipo-d4a65d56"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/07/01/tech/anthropic-export-control-lifted/index.html"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/anthropic-ai-model-export-ban-lift-amazon-broadcom-de25d9e1"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/article/anthropic-clears-major-ipo-hurdle-us-lifts-export-controls"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Dario Amodei, CEO of Anthropic, at TechCrunch Disrupt",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body.strip()
}

# ── Insert ──────────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
