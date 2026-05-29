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
        "headline": "Meta Wants You to Pay for WhatsApp. Here's What That Means for 500 Million Indians.",
        "subheadline": "Facebook Plus, Instagram Plus, and WhatsApp Plus subscriptions are rolling out globally. India pricing is still TBD — but the diaspora's most essential app just entered the subscription era.",
        "slug": make_slug("meta-whatsapp-plus-instagram-subscription-india"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "WhatsApp is the connective tissue of the Indian diaspora — the family group chat, the money transfer coordination, the NRI grapevine. Any monetization move by Meta here touches every Indian abroad personally. Creator and business tiers also reshape the economics for India's massive influencer and SMB ecosystem.",
        "tags": ["meta", "whatsapp", "instagram", "subscriptions", "india", "social-media", "creators"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fox Business", "url": "https://foxbusiness.com/fox-news-tech/meta-paid-subscriptions-facebook-instagram-whatsapp"},
            {"name": "Gadgets 360", "url": "https://www.gadgets360.com/apps/news/meta-facebook-plus-instagram-plus-whatsapp-plus-subscription-plans-price-features-8090245"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/meta-subscription-plans-ai-ambitions"},
            {"name": "Smartprix", "url": "https://www.smartprix.com/bytes/meta-subscription-models-platforms/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/267389/pexels-photo-267389.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Meta's subscription push spans Facebook, Instagram, and WhatsApp — apps used by hundreds of millions of Indians daily.",
        "body": """WhatsApp is not a messaging app for Indians. It is the infrastructure. The family group chat that coordinates festivals across three time zones. The forwarded voice note from an uncle in Hyderabad. The payment confirmation screenshot shared between siblings splitting a parent's medical bill. It is, for the 500-million-strong Indian user base and millions more in the diaspora, something closer to a utility than a product.

Meta now wants to charge for premium access to it.

## The Three-App Subscription Push

On Wednesday, Meta announced paid subscription tiers for its three flagship platforms: **Facebook Plus** and **Instagram Plus** at $3.99 per month each, and **WhatsApp Plus** at $2.99. The plans are rolling out globally over the coming weeks.

WhatsApp Plus subscribers will get premium stickers, custom app themes, personalised ringtones, and expanded pinned chat capabilities. Instagram Plus offers enhanced Story controls, audience insights, profile customisation, and additional profile pins. Facebook Plus includes animated reactions and profile personalisation tools.

None of this is earth-shattering. The real signal is in what comes next.

## Meta One: The AI Paywall

Meta is also testing a broader subscription umbrella called **Meta One**, with AI-focused tiers priced at $7.99 and $19.99 per month — and a reported premium tier reaching $49.99. These would bundle access to more compute-intensive AI features across all three platforms, including advanced reasoning capabilities, image generation, and video creation tools.

"We're also testing new subscription plans that offer premium features for those who want to unlock more from our apps and AI glasses," said Naomi Gleit, Meta's head of product.

Separate creator and business plans are also coming, featuring enhanced profile visibility, clickable links in Instagram posts and Reels, collaboration tools, and dedicated account support. These will initially launch in select test markets.

## The India Question

India pricing has not been announced. This is the single most consequential detail for the diaspora, and Meta is clearly still working it out.

India is WhatsApp's largest market by a wide margin. It is also a market where average revenue per user is a fraction of what Meta earns in North America. The company's existing Meta Verified subscription — focused on account verification — already offers India-specific pricing well below US rates.

The likely scenario: India gets significantly discounted tiers. But even at ₹149 or ₹249 per month, the psychological shift matters. WhatsApp has been free for a decade. Asking Indian users to pay — even for optional premium features — changes the relationship.

For **Indian creators and small businesses**, the calculus is different. Clickable links in Reels, audience insights, and enhanced visibility are the exact tools that India's booming creator economy has been demanding. Instagram has an estimated 360 million Indian users. If the business tier is priced right, adoption could be explosive.

## Why Now? Follow the Capex

The timing is not subtle. Meta has committed up to $135 billion in capital expenditure this year, almost entirely on AI infrastructure — data centres, GPU clusters, the computational backbone for everything from Meta AI to Ray-Ban smart glasses. The company cut 8,000 jobs last week while simultaneously moving 7,000 employees into AI-focused roles.

Advertising alone cannot absorb that level of spending indefinitely. Subscriptions represent Meta's first serious attempt at diversifying revenue beyond ads since its ill-fated NFT push in 2022.

Meta shares rose on the announcement. Investors clearly see the logic: even modest subscription revenue from a user base of 3.3 billion monthly actives adds up fast.

## What NRIs Should Watch

If you are an Indian American running a small business through Instagram, the creator and business tiers could be genuinely useful — once they arrive. If you are coordinating family logistics through WhatsApp, the core experience remains free. The premium stickers and custom themes are cosmetic.

The deeper question is whether Meta One's AI tiers create a two-tier experience where paying users get meaningfully better AI features. If Meta AI becomes the default assistant for a billion Indians, gating its best capabilities behind a paywall has implications far beyond social media.

For now, the free WhatsApp group chat lives on. But the era of "if you're not paying, you're the product" just got a companion principle at Meta: if you are paying, you might still be the product too."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Anthropic Just Dethroned OpenAI. Its $965 Billion Valuation Makes It Bigger Than Walmart.",
        "subheadline": "A $65 billion Series H round makes the Claude maker the world's most valuable AI startup. Revenue has hit $47 billion annualised. An IPO is likely this year. And India is its second-largest market.",
        "slug": make_slug("anthropic-965-billion-valuation-openai-dethroned"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian engineers and researchers are heavily represented at Anthropic and across AI labs vying for talent. India is Claude's second-biggest market globally. For NRI investors watching the AI space, this valuation reshuffles the landscape ahead of what could be the biggest tech IPO since Meta itself.",
        "tags": ["anthropic", "claude", "ai", "valuation", "openai", "ipo", "venture-capital"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/anthropic-raises-65-billion-now-valued-965-billion-2026-05-28/"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/livecoverage/stock-market-today-dow-sp-500-nasdaq-05-28-2026/card/anthropic-is-new-ai-front-runner-doubling-its-valuation-in-latest-funding-round-lm7DpaPYHeTkOfRUDxxv"},
            {"name": "Reuters (Apollo/Blackstone)", "url": "https://www.reuters.com/business/apollo-blackstone-work-36-billion-debt-deal-anthropic-bloomberg-news-reports-2026-05-28/"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/livecoverage/stock-market-today-dow-sp-500-nasdaq-05-28-2026/card/anthropic-nears-1-trillion-valuation-leapfrogging-openai"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
        "image_caption": "Anthropic CEO Dario Amodei. His company is now valued higher than OpenAI.",
        "body": """Four years ago, Anthropic was a safety-focused research lab staffed by ex-OpenAI researchers with a modest pitch: build AI carefully, or don't build it at all. On Thursday, that lab announced a $65 billion fundraise at a $965 billion post-money valuation — making it, by the cold arithmetic of venture capital, the most valuable AI company on Earth.

OpenAI, valued at $852 billion after its March round, is now the underdog. At least on paper.

## The Numbers Behind the Crown

The Series H round was led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital, with Coatue and ICONIQ as co-leads. The round includes $15 billion of previously committed investments from hyperscalers, including $5 billion from Amazon.

Amazon's total commitment to Anthropic now stands at $33 billion, after a $25 billion pledge in April tied to a deal requiring Anthropic to spend more than $100 billion over the next decade on Amazon Web Services infrastructure.

More striking than the equity raise: Apollo Global Management and Blackstone are simultaneously assembling a $36 billion debt financing package for Anthropic, according to Bloomberg. The debt would be used to purchase custom tensor processing units (TPUs) from Google, which Anthropic would then lease. Broadcom, which helps Google develop the chips, is backstopping payments on the largest portions.

A startup raising $65 billion in equity and $36 billion in debt in the same week would have been inconceivable two years ago. In the current AI capital cycle, it barely raised eyebrows.

## Revenue That Justifies the Hype — Mostly

Anthropic's revenue has crossed $47 billion on an annualised run-rate basis, the company said. Second-quarter revenue is expected to more than double to $10.9 billion, which could make it the first quarter Anthropic turns an operating profit.

The growth is real. Claude has become the default coding assistant for a significant slice of the developer population, and enterprise adoption has accelerated sharply. The company has been so capacity-constrained that it has had to impose usage limits during peak hours and incentivise off-peak usage.

Sceptics note that annualising a single strong quarter can flatter the trajectory. Reuters' Breakingviews pointed out that using first-half revenue more conservatively yields roughly $31 billion annualised — still enormous, but making the $965 billion valuation about 30 times revenue rather than 20.

Both Anthropic and OpenAI are reportedly preparing IPOs as early as this year. If Anthropic goes public at anything near this valuation, it would be the largest technology IPO in history.

## The Indian Dimension

India is Claude's second-largest market globally, a fact that underscores how deeply AI tools have penetrated the Indian developer and enterprise ecosystem. From Bangalore startups building on Claude's API to Indian IT services firms integrating it into client workflows, Anthropic's reach in the subcontinent is substantial and growing.

For Indian AI researchers, the valuation matters in a more personal way. Anthropic, like OpenAI, Google DeepMind, and Meta AI, employs a meaningful number of Indian-origin engineers and researchers. The company's safety-first positioning has made it a particularly attractive destination for technically rigorous talent from IITs and IISc.

For NRI investors, the picture is murkier. There is no public stock to buy yet. But the impending IPO — and the question of whether the company can sustain growth rates that justify a near-trillion-dollar valuation — will be one of the defining investment narratives of the year.

## The Infrastructure Arms Race

The Anthropic round also highlights something broader: the AI industry's capital requirements have entered a phase that looks less like software and more like industrial buildout.

Anthropic's infrastructure partners — Micron, Samsung, and SK Hynix — joined this funding round as investors. These are memory chip manufacturers, not the venture capitalists of the last decade's tech boom. Their participation signals that the AI supply chain itself is becoming a web of strategic equity relationships.

Amazon is paying billions for the right to be Anthropic's cloud provider. Apollo and Blackstone are structuring debt deals to finance chip purchases. Google is both a supplier of TPUs and a competitor in the foundation model space. The lines between investor, customer, and rival have blurred beyond recognition.

## What Comes Next

The $965 billion valuation sets a benchmark that Anthropic will have to justify quarterly. The IPO, when it comes, will test whether public markets agree with private investors that safety-focused AI is worth almost as much as the entire economy of Turkey.

For the Indian tech community — builders, investors, and workers — the message is simpler: the AI frontier is moving at a pace where the most valuable startup in the world can change from one quarter to the next. Staying close to the frontier is no longer optional."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ByteDance Is Designing Its Own CPUs. The AI Chip Shortage Is That Bad.",
        "subheadline": "TikTok's parent is pursuing custom processors on both ARM and RISC-V architectures as CPU prices surge 35% and Intel delivery times stretch to six months.",
        "slug": make_slug("bytedance-custom-cpu-chip-arm-riscv-ai-shortage"),
        "category": "technology",
        "vertical": "technology",
        "diaspora_angle": "Indian chip design engineers are among the most sought-after professionals in the semiconductor industry. ByteDance's entry into custom silicon expands the addressable market for this talent. India's own RISC-V push through the India Semiconductor Mission gains relevance as major players validate the open-source architecture.",
        "tags": ["bytedance", "cpu", "semiconductor", "arm", "risc-v", "ai-chips", "india-semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/china/bytedance-developing-custom-cpu-chips-support-ai-rollout-sources-say-2026-05-28/"},
            {"name": "Barron's", "url": "https://www.barrons.com/articles/chip-rally-parabolic-semiconductor-stocks"},
            {"name": "Reuters (TSMC)", "url": "https://www.reuters.com/technology/energy-use-forcing-rethink-ai-chip-design-tsmc-says-2026-05-28/"}
        ]),
        "score_total": 75,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The AI boom is no longer just a GPU story — central processors are now the bottleneck.",
        "body": """The AI boom has a new bottleneck, and it is not the one everyone has been talking about.

For two years, the narrative has been about GPUs — specifically Nvidia's — and the frantic scramble to secure enough graphics processors to train and run the large language models reshaping every industry. But a quieter crisis has emerged in the shadow of that GPU frenzy: the world is running out of CPUs.

ByteDance, the Beijing-based parent of TikTok, is the latest tech giant to conclude that the economics of buying off-the-shelf processors no longer work. According to Reuters, the company is developing its own custom CPUs, pursuing two architecture tracks simultaneously — one based on ARM, the other on the open-source RISC-V instruction set.

## Why CPUs, Why Now

The shift is driven by "inference" — the phase where trained AI models are deployed to actually do things. Unlike training, which is GPU-intensive, inference workloads depend heavily on CPUs working alongside GPUs to handle the orchestration, data routing, and decision-making that agentic AI systems require.

As AI moves from chatbots that answer questions to agents that book flights, write code, and manage supply chains, CPU demand has surged. ByteDance is preparing a massive rollout of agent-based products through its Coze platform, and its existing CPU supply from Intel and AMD is neither cheap enough nor reliable enough.

Intel has warned Chinese customers of server CPU delivery lead times stretching to six months. AMD CEO Lisa Su said last week that the global CPU market is "tight," with demand outpacing forecasts. Quarter-over-quarter price increases of 10 to 35 per cent have become routine.

ByteDance is not waiting around. It has approached external partners for chip design assistance and foundry manufacturing capacity, though the project remains at an early stage.

## The Custom Silicon Club

ByteDance joins a growing cohort of tech giants that have decided designing their own chips is cheaper than buying them. Google has its Tensor Processing Units and custom ARM-based CPUs. Amazon has Graviton processors powering a growing share of AWS workloads. Apple's M-series chips remade the Mac. Microsoft is building custom AI accelerators.

The common thread: when you operate at hyperscale, even a 10 per cent efficiency gain on every server translates to billions in savings. And when your supplier is raising prices by 35 per cent per quarter, the business case for custom silicon goes from interesting to urgent.

ByteDance's dual-track approach — ARM and RISC-V — is itself telling. ARM is the proven, commercially mature path, backed by an ecosystem that SoftBank-owned Arm Holdings has spent decades cultivating. RISC-V is the insurgent: an open-source instruction set architecture that eliminates licensing fees and gives designers more flexibility.

Running both in parallel is a common hedge among large technology companies exploring custom silicon. It allows ByteDance to benchmark the two against each other before committing to a costly manufacturing run.

## What This Means for Indian Chip Engineers

India's semiconductor design talent is already stretched thin. The country's chip design centres — in Bangalore, Hyderabad, Pune, and Noida — employ tens of thousands of engineers working for Qualcomm, Intel, AMD, ARM, Broadcom, Samsung, and dozens of fabless startups.

ByteDance's entry into custom silicon expands the demand pool further. Whether the company builds its design team in-house or contracts with external design firms, Indian engineers are likely to be involved. ARM-based design expertise is concentrated in India, and RISC-V talent — while nascent — is growing rapidly, partly driven by India's own semiconductor mission.

The India Semiconductor Mission has explicitly backed RISC-V as a strategic architecture, funding academic research and startups exploring open-source chip design. If RISC-V gains validation from a company the size of ByteDance, it strengthens the case for India's bet on the architecture.

## The Bigger Picture

The CPU shortage is a structural consequence of an industry that spent three years fixated on GPUs while inference demand quietly ate the world. Nvidia itself recognised the opportunity, unveiling its Vera CPU — an ARM-based processor — in a bid to capture what Jensen Huang described as a $200 billion market.

The PHLX Semiconductor Index (SOX) has risen for 18 consecutive trading days, gaining 47 per cent in one stretch and 80 per cent since late March. The surge has drawn comparisons to the dot-com era, with analysts warning that the rally has become "indiscriminate" — lifting low-margin chip makers alongside the genuine AI beneficiaries.

For NRI investors tracking semiconductor stocks, the ByteDance story adds a data point to the bull case: demand for chips, including CPUs, is so intense that even a Chinese social media giant is designing its own. The supply-demand imbalance is not a quarter-long blip. It is the new baseline.

For Indian chip designers, the message is even clearer. Whether you are working on ARM cores at Qualcomm's Hyderabad campus or exploring RISC-V at a Bangalore startup, your skills have never been more valuable — or more contested."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
