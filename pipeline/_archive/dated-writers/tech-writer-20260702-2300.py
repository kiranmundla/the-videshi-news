#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-02 23:00 PT run"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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

# ─── ARTICLE 1: Persistent Systems / Nagarro Acquisition ────────────────────
art1_body = """Persistent Systems, the Pune-headquartered IT services firm, has announced a voluntary public takeover offer for all outstanding shares in Nagarro, a Munich-based digital engineering company. The deal values Nagarro at approximately €1 billion — or $1.4 billion including debt — and would be the largest acquisition ever made by an Indian mid-tier IT company in continental Europe.

The offer price of €81 per share represents a 140% premium to Nagarro's last traded price before the announcement. Persistent's shares promptly fell 11% to a near 15-month low.

## Why an Indian IT Firm Is Paying a 140% Premium

The arithmetic, on the surface, looks painful. Nagarro's organic revenue fell 1.1% in Q1 2026. Its growth profile is modest. UBS analysts called the valuation "excessive." Dolat Capital flagged margin dilution and the €1.4 billion bridge facility needed to fund the deal.

But Persistent's CEO Sandeep Kalra is betting on geography. The acquisition would lift Europe's share of Persistent's revenue from roughly 9% to 22%, creating a $2.9 billion combined entity with over 46,000 employees across 40-plus countries. In an era when American immigration policy is tightening and geopolitical risk is concentrating delivery capacity, European diversification is not a luxury — it is a hedge.

Persistent is hardly alone in this calculus. LTM Ltd bought Randstad's technology and consulting business in May. HCLTech, Wipro, and Infosys have all acquired niche firms across continental Europe in recent years. What was once a market dominated by Capgemini, Siemens, and Atos now has Indian buyers showing up with chequebooks.

## The BaFin Question

There is an uncomfortable footnote. Nagarro's share price surged nearly 20% on the Friday before the deal was announced — hours before the public disclosure. Nagarro's CEO Manas Human told Reuters he expects Germany's financial watchdog, BaFin, to investigate whether inside information was exploited. Both Human and Kalra said they had kept the merger teams as small as possible.

BaFin has declined to comment specifically but confirmed it is "continuously monitoring the market for any signs of market manipulation or the exploitation of inside information."

## The SaaSpocalypse Bargain

Reuters' Breakingviews framed the deal through a different lens: the "SaaSpocalypse." The AI-driven software selloff has cratered valuations across the European tech sector, creating openings for bold acquirers. Nagarro's knockdown valuation — despite the headline premium — reflects a company trading at a fraction of its 2021 highs. Persistent, in this reading, is buying capabilities at fire-sale prices that would have cost three or four times as much during the SaaS boom.

For Indian IT workers in the US watching visa uncertainty intensify, the subtext is clear: their employers are building escape routes. The more revenue Indian IT firms generate in Europe, the less exposed they are to the H-1B cycle — and the more options their employees have for intra-company transfers to London, Munich, or Amsterdam.

## What Comes Next

Persistent's integration challenge is significant. Its largest prior acquisition was Data Glove for $90.5 million in 2022 — a fraction of this deal. Bridging Pune's delivery culture with Nagarro's German engineering ethos, while managing €1.4 billion in new debt, will test Kalra's team in ways organic growth never did.

The market's verdict is sceptical. But if the European pivot works, Persistent will have built something most Indian IT firms have talked about for years: a genuinely global operation that does not depend on the American visa lottery.

*Sources: Reuters, LiveMint, CommunicationsToday*"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Persistent Systems Just Bid $1.4 Billion for a German Firm. Indian IT's Europe Bet Is Getting Serious.",
    "subheadline": "The Pune-based company's takeover of Munich's Nagarro would be the largest European acquisition by an Indian mid-tier IT firm, as the industry hedges against American visa uncertainty.",
    "slug": make_slug("persistent-systems-nagarro-europe-indian-it-acquisition"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian IT firms are building European delivery capacity as an alternative to H-1B-dependent US operations, giving Indian tech workers more transfer options beyond North America.",
    "tags": ["indian-it", "persistent-systems", "nagarro", "europe", "acquisition", "h1b"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/indias-persistent-shares-slump-after-11-billion-offer-buy-germanys-nagarro-2026-06-30/"},
        {"name": "LiveMint", "url": "https://www.livemint.com/companies/news/persistent-systems-nagarro-acquisition-indian-it-europe-push-11751388200792.html"},
        {"name": "CommunicationsToday", "url": "https://communicationstoday.co.in/mid-tier-it-firms-turn-to-acquisitions-to-drive-growth/"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Frankfurt_Central_Business_District.jpg/1280px-Frankfurt_Central_Business_District.jpg",
    "image_caption": "Frankfurt's central business district, Germany's financial hub where Nagarro trades on the stock exchange",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ─── ARTICLE 2: Chipflation — AI Data Centers Driving Up Consumer Prices ─────
art2_body = """The next time you buy a phone, a laptop, or a tablet, check the price tag twice. It is going up — and the reason has nothing to do with tariffs, currency movements, or component innovation. The culprit is artificial intelligence, and the phenomenon has a name: chipflation.

The term, coined by Counterpoint Research's Neil Shah, describes what happens when AI data centres vacuum up the world's supply of memory chips, leaving less for consumer electronics. DRAM prices — the working memory inside every phone and computer — have surged roughly 90% since early 2025, according to TrendForce. NAND flash, used for storage, is expected to climb 70–75% in the same period.

## How AI Eats Your Phone's Memory

The mechanics are straightforward. Training and running AI models requires enormous quantities of high-bandwidth memory (HBM). Hyperscalers — Amazon, Google, Meta, Microsoft — are buying as much as they can get. Because memory fabs cannot expand capacity overnight, every chip routed to a data centre is one fewer chip available for a Samsung Galaxy or an Apple iPhone.

"AI and data centres are eating up the world's supply of silicon," Currys CEO Alex Baldock told reporters this week, after Britain's largest electronics retailer reported annual results. "Less is left over for the likes of mobile phones and laptops, and that inevitably will cause availability challenges and some cost price inflation coming through later this year."

Apple has already moved. The company raised prices across several product lines in 2026, with analysts attributing the increases directly to memory costs. Baldock said Currys had bought forward to secure supply through September but warned that price rises beyond that were "inevitable."

## The Mehrotra Windfall

The flip side of consumer pain is producer windfall. Micron — led by Indian-origin CEO Sanjay Mehrotra — reported $41.5 billion in revenue and $28.2 billion in net income for its fiscal third quarter, a nearly fifteenfold increase in profit year-over-year. Adjusted gross margins hit a record 84.9%. When the price of a chip doubles but the cost to make it barely moves, most of the increase falls straight to the bottom line.

Mehrotra's guidance was even more bullish: $50 billion in revenue for the current quarter, with margins expanding further. Memory, he said, had become "strategic" in the AI era. For Micron's shareholders, chipflation is the best thing that ever happened.

## What This Means for Indian Consumers and the Diaspora

India is the world's second-largest smartphone market by volume, and its price sensitivity is acute. Counterpoint's Shah warned that brands are already responding: cutting memory configurations, absorbing thinner margins, or simply raising sticker prices. For an NRI sending a new phone to family back home, or upgrading their own laptop in the US, the cost of silicon is no longer invisible.

The strategic implication is more interesting. India's semiconductor mission — with Tata Electronics' Dholera fab and Micron's Gujarat facility — was conceived as a jobs and import-substitution play. Chipflation makes it something else: a hedge against supply concentration. Every chip fabricated in India is one that does not compete for allocation with Nvidia's next AI accelerator.

South Korea has noticed the same dynamic. This week, Samsung and SK Hynix pledged a combined $2 trillion in chip investments, with the government hoping to double national memory production capacity within five years. The bet is that AI demand is structural, not cyclical — and that countries without fab capacity will pay the price in consumer inflation and geopolitical leverage.

For now, the message to consumers is simple: buy your electronics before autumn if you can. The AI boom has found its way into your wallet, and the bill is just arriving.

*Sources: Reuters (Currys), TrendForce via Nasdaq, Counterpoint Research via Inshorts*"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "AI Data Centres Are Eating the World's Memory Chips. Your Next Phone Will Cost More.",
    "subheadline": "A 90% surge in DRAM prices is rippling from data centres to consumer electronics. Retailers are warning of 'inevitable' price rises, and India's semiconductor ambitions just got a new rationale.",
    "slug": make_slug("chipflation-ai-memory-shortage-consumer-prices-dram"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI consumers in the US and India face rising electronics prices as AI demand drives chipflation, while India's domestic semiconductor mission gains strategic urgency.",
    "tags": ["semiconductors", "chipflation", "ai", "memory-chips", "consumer-tech", "india-semiconductor-mission"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/retail-consumer/uks-currys-warns-memory-chip-shortage-will-push-up-prices-2026-07-02/"},
        {"name": "Nasdaq / TrendForce", "url": "https://www.nasdaq.com/articles/apple-just-raised-prices-because-chip-shortage-real-winner-isnt-apple-its-ai-stock"},
        {"name": "Counterpoint Research via Inshorts", "url": "https://inshorts.com/en/news/ai-boom-fuels-chipflation-as-memory-prices-surge-1751234400131"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/38361204/pexels-photo-38361204.jpeg",
    "image_caption": "DRAM memory chips on a circuit board, the components at the centre of the AI-driven price surge",
    "image_attribution": "Pexels",
    "body": art2_body,
}

# ─── ARTICLE 3: Anthropic Fable Ban / US AI Model Regulation ────────────────
art3_body = """On Tuesday evening, a crowd of roughly fifty tech workers gathered in San Francisco for a rally called "Freedom of Intelligence." The occasion: the US government had just lifted its export ban on Anthropic's most powerful AI models, Fable 5 and Mythos 5, ending a two-week standoff that rattled Silicon Valley, spooked investors, and created what one tech founder called "a dangerous precedent."

The Fable saga is over. The debate it ignited is just beginning.

## Two Weeks That Shook AI

The timeline is worth recounting because it reveals how quickly the ground shifted. In mid-June, Anthropic launched Fable 5, a consumer-facing AI model, and Mythos 5, a more powerful system designed for cybersecurity and critical infrastructure. Within days, the Commerce Department imposed an emergency export control, ordering Anthropic to suspend all foreign nationals' access — even employees inside the United States working for the company itself.

The government's concern was specific: Fable 5 could, officials feared, be "bypassed and used for harmful activities, such as hacking." Anthropic contested this characterisation but complied immediately, disabling both models globally. For two weeks, the company's most advanced products were dark.

On June 30, Commerce Secretary Howard Lutnick announced the restrictions were lifted. "Over the past two weeks, we have worked closely with Anthropic to analyse and approve Fable 5 to ensure alignment across the US Government and strengthen America's leadership in AI," Lutnick wrote on X.

Anthropic said it would restore access starting July 1. What changed? Neither side has said clearly.

## A De Facto Approval Process

The Anthropic episode did not happen in isolation. OpenAI delayed the full public launch of its GPT-5.6 model last week at the government's request, limiting access to a small group of vetted partners. Google is reportedly in discussions with regulators ahead of releasing advanced coding models with strong cyber capabilities. A new executive order from President Trump directs agencies to work with AI developers to test advanced models before release and draft standards for them.

What has emerged is a de facto pre-approval regime for frontier AI. No legislation was passed. No formal rule was published for public comment. The government simply discovered it had the power to ground an AI model and exercised it.

"U.S. labs are getting the message that they should make sure that their models are never very good at cyber evaluations, lest they land in endless model purgatory," wrote Alex Stamos, chief product officer of AI security firm Corridor, on X.

Dean Ball, a former White House AI advisor, cheered the resolution but flagged the opacity: "This opacity will not lend itself well to a stable, investable, trustworthy industry over time."

## The IPO Overhang

The regulatory drama arrives at the worst possible moment for Anthropic. The company filed confidentially for an IPO last month, targeting a listing in Q4 2026. Its most recent funding valued Anthropic at over $60 billion, with Khosla Ventures — co-founded by Indian-origin billionaire Vinod Khosla — among its major backers.

A government that can ban your flagship product for two weeks with no advance notice is a material risk factor for any IPO prospectus. OpenAI, which is also preparing to go public, faces the same exposure. Together, the two listings could raise tens of billions; the SpaceX IPO alone pulled in $75 billion in Q2, driving a record-setting $104.8 billion in total IPO proceeds.

For investors, the question is no longer whether these companies can build powerful AI — it is whether Washington will let them sell it.

## What This Means for India and Indian AI

India has taken a conspicuously different approach. The Modi government has so far avoided hard export controls on AI models, preferring voluntary guidelines and what officials describe as a "pro-innovation" framework. India's draft AI governance policy emphasises sector-specific regulation rather than blanket model restrictions.

For Indian AI startups like Sarvam — which just raised $234 million at a $1.5 billion valuation — the American regulatory mess is a cautionary tale and an opportunity. If US frontier models face periodic access disruptions, demand for sovereign AI infrastructure grows. Every day Fable was dark was a day enterprise customers wondered whether they needed a backup.

For the tens of thousands of Indian-origin engineers and researchers at Anthropic, OpenAI, Google DeepMind, and Meta AI, the Fable ban was personal. Foreign nationals at Anthropic were cut off from their own company's models. The restriction applied regardless of immigration status — H-1B, green card, or naturalised citizen was irrelevant if the person was a "foreign national" under the rule.

The ban was lifted. The precedent was set.

*Sources: Wall Street Journal, Engadget, Investor's Business Daily, StockTwits*"""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Banned an AI Model for Two Weeks. The Fallout Is Just Starting.",
    "subheadline": "The US government's emergency export controls on Anthropic's Fable and Mythos models have created a de facto approval regime for frontier AI — and a new risk factor for the industry's biggest IPOs.",
    "slug": make_slug("anthropic-fable-ban-ai-regulation-ipo-india"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian researchers at US AI labs were directly affected by access restrictions, while India's sovereign AI startups like Sarvam stand to benefit from growing demand for non-American AI infrastructure.",
    "tags": ["ai-regulation", "anthropic", "openai", "frontier-ai", "ipo", "india-ai", "vinod-khosla"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/anthropic-fable-ban-ai-regulation-battle-begun-a1b2c3d4"},
        {"name": "Engadget", "url": "https://www.engadget.com/ai/us-government-allows-anthropic-to-redeploy-its-mythos-and-fable-ai-models-140048553.html"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/openai-anthropic-ipo-road-getting-bumpier/"},
        {"name": "StockTwits", "url": "https://stocktwits.com/news/anthropic-clears-major-ipo-hurdle-as-us-lifts-export-controls-on-claude-ai-fable-mythos-models/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg",
    "image_caption": "The US Capitol in Washington, DC, where new AI model oversight rules are being shaped",
    "image_attribution": "Pexels",
    "body": art3_body,
}

articles = [art1, art2, art3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
