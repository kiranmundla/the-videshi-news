#!/usr/bin/env python3
"""Videshi Tech Writer — Sat 2026-06-27 23:00 PDT run.

Two technology articles:
1. Micron overtakes Meta/Tesla — Sanjay Mehrotra's $22B take-or-pay revolution
2. GPT-5.6 restricted by US government — what it means for Indian developers
"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Load env ──────────────────────────────────────────────────────────
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
    return slug[:70].rstrip("-") + "-20260628"

# ── ARTICLE 1: Micron / Sanjay Mehrotra ───────────────────────────────
art1_body = """Sanjay Mehrotra has spent the better part of four decades in semiconductors, but last Thursday may have been the week that rewrote his legacy. Micron Technology, the Boise-based memory chipmaker he has led since 2017, briefly surpassed both Meta and Tesla in market capitalisation — touching $1.4 trillion after a quarter so strong it made Wall Street's already-bullish estimates look timid.

The numbers were staggering. Third-quarter revenue came in at $41.5 billion, beating analyst expectations of $35.9 billion by a mile. Adjusted earnings per share hit $25.11, against a consensus of $20.78. And then the guidance: Micron expects fourth-quarter earnings of $31 per share, roughly 20% above what the Street had pencilled in. Shares surged 18% in the session that followed.

## The $22 Billion Lock-In

But the headline number was not on the income statement. It was in a disclosure that may reshape the memory chip industry for the next decade.

Micron announced that 16 customers — spanning data centres, consumer electronics, and automotive — have signed "strategic customer agreements" committing a total of $22 billion in cash deposits and financial guarantees, with $18 billion in cash alone. These are five-year, take-or-pay contracts: customers must either buy at pre-negotiated prices or forfeit their deposits. Price bands set floors and ceilings, renegotiated quarterly but never breachable.

"These are fundamentally different from anything we've done before," Manish Bhatia, Micron's executive vice president of global operations, told Investor's Business Daily. "Our previous long-term agreements were annual. Now we're talking about five-year commitments where customers have much more skin in the game."

The remaining performance obligations — a measure of future contracted revenue — stand at roughly $100 billion.

## Why Memory Became Strategic

For decades, memory chips were the semiconductor industry's commodity play. Prices swung wildly with supply cycles, and chipmakers had little pricing power. The AI boom has upended that calculus entirely.

High-bandwidth memory (HBM) chips — the ultra-fast modules stacked alongside Nvidia's AI processors — are now so scarce that hyperscale data centre operators are willing to pre-pay billions to guarantee supply. Micron is the sole American manufacturer of these chips, and CEO Mehrotra was blunt about the outlook: "We expect tight conditions to persist beyond calendar 2027. Even as industry supply improves gradually in 2028, we currently do not have line of sight as to when supply will catch up with demand."

SK Hynix and Samsung have also locked in long-term deals, but Micron's take-or-pay structure with deposited cash is the most aggressive version yet. When these agreements are fully operational, Micron expects half or more of its revenue to come from contracted sources — a transformation from commodity supplier to strategic partner.

## The Gujarat Connection

For the Indian diaspora, Micron's ascent carries a particular resonance. Mehrotra, born in Kanpur and educated at the Indian Institute of Technology, co-founded SanDisk in 1988 before taking the helm at Micron. He is one of a small cohort of Indian-origin CEOs running the companies that supply the physical infrastructure of the AI revolution.

And the India connection runs deeper than the corner office. Micron is building a $2.75 billion semiconductor assembly and test facility in Sanand, Gujarat — its first in India — supported by significant government subsidies under the India Semiconductor Mission. The facility, expected to be operational by late 2026, will package and test memory chips for global markets. It is also the proving ground for whether India can move from consuming chips to processing them.

With Micron's stock up more than threefold this year and its market cap now rivalling the largest technology companies on earth, NRI investors who bet on the memory trade early have been handsomely rewarded. But the deeper story is structural: the AI economy runs on memory, and the man who controls America's only HBM supply chain was born in Uttar Pradesh.

## What Comes Next

Micron's fourth-quarter guidance implies continued acceleration. Analysts at TD Cowen raised their price target to $1,600, estimating the 16 strategic agreements will account for 20-25% of revenue by calendar 2027. The critical question is whether the take-or-pay model can genuinely break the boom-bust cycle that has defined memory chips for half a century — or whether it merely delays the reckoning.

For now, the market is betting on structural change. And Sanjay Mehrotra, the quiet engineer from Kanpur, is the person they are betting on."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sanjay Mehrotra's Micron Just Passed Meta in Market Value. His Secret Weapon: $22 Billion in Contracts Nobody Can Cancel.",
    "subheadline": "The Indian-born CEO's take-or-pay revolution has made memory chips the hottest trade in AI — and his Gujarat fab the next frontier.",
    "slug": make_slug("sanjay-mehrotra-micron-meta-market-cap-take-or-pay"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian-origin CEO Sanjay Mehrotra (IIT, born Kanpur) runs America's only HBM chipmaker, now worth more than Meta; Micron's $2.75B Gujarat fab is India's biggest semiconductor investment.",
    "tags": ["micron", "sanjay-mehrotra", "semiconductor", "ai-chips", "hbm", "indian-ceo", "gujarat"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-forecasts-strong-quarterly-results-soaring-memory-chip-demand-2026-06-25/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-joins-rivals-pitching-ai-deals-cure-memorys-boom-bust-cycle-2026-06-26/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/micron-overtakes-meta-tesla-market-value-amid-relentless-ai-infrastructure-demand-2026-06-26/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/micron-stock-mu-earnings-q3-2026/"},
        {"name": "WCCFTech", "url": "https://wccftech.com/micron-signs-up-16-strategic-customer-agreements-for-memory/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
    "image_caption": "Sanjay Mehrotra, CEO of Micron Technology, at a 2025 industry event",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body,
}

# ── ARTICLE 2: GPT-5.6 restricted launch ─────────────────────────────
art2_body = """OpenAI launched GPT-5.6 on Friday — its most powerful AI model yet — and then did something it has never done before: restricted who could use it.

At the request of President Donald Trump's administration, the ChatGPT maker said the model would initially be available only to a "small group of trusted partners" whose identities were shared with the government. CEO Sam Altman told staff internally that the White House would be "approving access customer by customer." The broader public rollout, originally planned for the same day, has been pushed to an unspecified date "in the coming weeks."

The move marks the clearest signal yet that Washington views frontier AI models not as consumer products, but as dual-use technologies with national security implications — akin to advanced encryption or satellite imagery.

## Three Models, One Gatekeeper

GPT-5.6 comes in three variants. Sol, the flagship, is described as OpenAI's strongest model ever, with particular advances in coding, biology, and cybersecurity — the last category being precisely what has Washington worried. Terra matches GPT-5.5 performance at half the cost. Luna is the budget tier.

The restricted launch follows Trump's executive order earlier this month establishing a voluntary framework under which AI developers offer frontier models to the government for up to 30 days of review before releasing them to trusted partners. OpenAI, Anthropic, Google, xAI, and Microsoft have all been providing early access; Meta has been the sole holdout, with the government reportedly pressuring it to comply.

OpenAI was diplomatic but pointed in its response. "We don't believe this kind of government access process should become the long-term default," the company said. "It keeps the best tools from users, developers, enterprises, cyber defenders, and global partners who need them."

## The Anthropic Precedent

The GPT-5.6 rollout cannot be understood without the Anthropic crisis that preceded it. Two weeks earlier, the government ordered Anthropic to disable global access to its two most powerful models — Claude Mythos 5 and Claude Fable 5 — citing national security concerns. Officials had grown alarmed after Anthropic disclosed that Mythos 5 was unusually adept at discovering software vulnerabilities, a capability that could be weaponised by malicious actors.

Anthropic complied, pulling the models offline and entering a protracted negotiation with Washington. As of this writing, neither has been restored. The episode sent a chill through the AI industry — and through every company that depends on frontier model access.

OpenAI's phased rollout appears designed to avoid the same fate. By proactively limiting access and sharing its customer list with the government, Altman is betting that cooperation now buys broader access later.

## What This Means for Indian Developers

India is OpenAI's second-largest market after the United States. Millions of Indian developers, startups, and enterprises rely on the ChatGPT API for everything from customer service automation to code generation. The restricted launch means they will be among the last to access GPT-5.6's capabilities — an asymmetry that could widen the gap between American and Indian AI product development, at least temporarily.

The timing is awkward. OpenAI just this week hired Prabhjeet Singh, former president of Uber India, as its first managing director for the country, and has opened offices in Delhi, Mumbai, and Bengaluru. It has partnered with Reliance and Tata Group. The India bet is real. But the government's national security framework does not distinguish between a Bengaluru AI startup and a Beijing military lab — both fall outside the "trusted partners" circle until further notice.

The implications extend beyond OpenAI. If the 30-day review framework becomes standard — as the executive order envisions — every frontier model launch will carry a geography-based access delay. Indian companies building on top of these models will consistently trail American competitors by weeks or months.

## The Sovereign AI Argument Gets Louder

This is precisely the scenario India's sovereign AI advocates have been warning about. Sarvam, which raised $234 million last month at a $1.5 billion valuation, builds full-stack AI models designed for Indian languages and use cases. Its pitch — that India cannot afford to depend on foreign models it neither owns nor controls — just gained a powerful piece of evidence.

"If your entire product stack runs on someone else's model, and that model can be turned off by a government order on a different continent, you don't have a technology business," one Indian AI founder told TechCrunch this month. "You have a dependency."

India's approach to AI governance has been pragmatic rather than restrictive, avoiding the heavy regulatory frameworks favoured by the US and EU. But the GPT-5.6 episode illustrates a different kind of risk: not that India's regulators will constrain its AI industry, but that America's will.

For Indian engineers at Google, Microsoft, and Meta — and for the thousands of startups building on the ChatGPT API — the message is uncomfortable but clear: access to the most powerful AI on earth is now a privilege, not a product. And the privilege is being rationed from Washington."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Just Put a Padlock on GPT-5.6. Indian Developers Are on the Outside.",
    "subheadline": "OpenAI's most powerful model launched to just 20 government-approved partners. For India's second-largest ChatGPT market, the wait has only begun.",
    "slug": make_slug("gpt-56-restricted-launch-india-developers-sovereign-ai"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "India is OpenAI's second-largest market; millions of Indian developers and NRI-founded startups rely on ChatGPT API — the restricted GPT-5.6 launch means they trail American competitors by weeks.",
    "tags": ["openai", "gpt-5.6", "ai-regulation", "india-ai", "sovereign-ai", "sarvam", "national-security"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-defers-public-rollout-gpt-56-us-seeks-early-access-frontier-ai-models-2026-06-27/"},
        {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/openai-limits-access-to-new-models-citing-government-security-concerns-2026-06-27/"},
        {"name": "Engadget", "url": "https://www.engadget.com/ai/openai-launches-a-limited-preview-of-gpt-5-6-2026-06-27/"},
        {"name": "The Daily Caller", "url": "https://dailycaller.com/2026/06/27/trump-administration-seeks-limited-release-openai-model-anthropic-shutdown/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/26/openai-poaches-uber-india-chief/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "Sam Altman, CEO of OpenAI, at a meeting in February 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body,
}

# ── Insert ────────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
