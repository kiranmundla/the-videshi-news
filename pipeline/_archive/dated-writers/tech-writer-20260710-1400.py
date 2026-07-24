#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-07-10 14:00 PDT run"""

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


# ── ARTICLE 1 ──────────────────────────────────────────────────────────

art1_body = """Samsung Electronics just posted the most profitable quarter in its history. Operating profit surged 19-fold year-on-year to 89.4 trillion won — roughly $58.5 billion — on revenue of 171 trillion won, more than double the same period last year. By any textbook measure, the numbers were spectacular. Analysts had expected big things. Samsung delivered bigger.

Wall Street's response? Sell.

Samsung shares plunged nearly seven per cent in Seoul within hours of the announcement. SK Hynix, its nearest rival in memory chips, fell in sympathy. In New York, the selling spread fast: Intel dropped 9.7 per cent — its worst single-day loss in months — while Micron Technology shed 4.7 per cent and AMD slipped 6.5 per cent. The Philadelphia Semiconductor Index lost 4.7 per cent in a single session. For the Indian-American engineer with a concentrated tech portfolio, or the NRI investor who loaded up on chip stocks during the AI rally, Tuesday's carnage was a jarring wake-up call.

## The paradox, explained

The mechanics are straightforward, even if the optics look absurd. Samsung's profit was driven overwhelmingly by high-bandwidth memory (HBM) chips — the specialised DRAM modules that Nvidia's data-centre GPUs devour in vast quantities. Demand from hyperscalers building AI infrastructure has tightened supply across the memory industry. Citi Research estimates that average selling prices for DRAM rose 44 per cent and NAND jumped 53 per cent quarter-on-quarter in the period. Gross margins at Samsung's memory division likely exceeded 79 per cent, a number that would make most software companies jealous.

But investors had already priced in this bonanza. Memory stocks had surged for months — SK Hynix alone was up roughly 260 per cent year-to-date before Tuesday's report. The blowout earnings became the textbook catalyst for "sell the news." Morningstar analyst Jing Jie Yu pointed to a subtle wrinkle: Samsung's revenue, while enormous, was slightly below expectations, suggesting that DRAM price hikes may have been "more moderate than expected." For a stock priced for perfection, even a whisper of moderation was enough.

Adding to the unease, Reuters reported on the same day that China's DeepSeek — the AI startup that shook Silicon Valley last year with its hyper-efficient models — is developing its own inference chip. If successful, DeepSeek would reduce its dependence on both Nvidia and Huawei hardware. While the immediate revenue impact on Nvidia is minimal (China is a shrinking share of its sales), the signal rattled sentiment: every major AI company, from Meta to Microsoft to now DeepSeek, is racing to build custom silicon, threatening the GPU monopoly that underpins the entire chip trade.

## Then came the rebound

Two days after the Samsung selloff, investors got a very different data point. SK Hynix debuted on the Nasdaq on Friday in the biggest foreign IPO in American history, raising $26.5 billion. The offering was more than seven times oversubscribed. Shares opened at $170, well above the $149 offer price, and closed up 12.8 per cent on their first day.

The message was unmistakable: institutional money still believes in the AI memory thesis. It just wants to own it at the right price. SK Hynix, the world's largest maker of HBM chips with 58 per cent market share, offers what investors call the "purest large-cap way to own the AI-memory theme," as one analyst put it. The company plans to use the proceeds for new factories and advanced chipmaking equipment — a bet that demand will keep outstripping supply for several more quarters.

## What NRI investors should watch

For Indian Americans working in the semiconductor industry — and there are tens of thousands at Nvidia, Intel, Micron, AMD, and Qualcomm — the rotation is more than an abstraction. It affects RSUs, stock-heavy compensation packages, and retirement accounts loaded with chip names.

Sanjay Mehrotra, Micron's Indian-born CEO, offered a counterpoint to the bearish narrative this week. In a Fox Business interview, he described AI-driven memory demand as "unprecedented" and announced plans for $250 billion in long-term investment, including $3 billion in domestic US manufacturing. "Despite our best efforts to accelerate bringing up supply," Mehrotra said, "the demand continues to build up and we do not see when supply catches up." That's bullish language from a man whose company competes directly with both Samsung and SK Hynix.

India's own semiconductor ambitions add another layer. The country has switched on three chip plants in five months — Tata Electronics in Dholera, Micron's facility in Gujarat, and CG Semi in Sanand — all of them riding the same memory and packaging supercycle that powered Samsung's record quarter. If the AI memory trade proves durable, these plants are well-timed. If it peaks sooner than expected, India's $21 billion in approved semiconductor projects will face a harsher cost-benefit calculus.

For now, the market's verdict is nuanced rather than negative. Samsung's profits proved the supercycle is real. The selloff proved the easy gains are over. And SK Hynix's blockbuster debut proved that new money is still lining up to get in — just not at any price."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Samsung Minted a Record $58.5 Billion in Profit. Wall Street Dumped the Stock.",
    "subheadline": "The biggest quarter in memory-chip history triggered a global semiconductor selloff. Two days later, SK Hynix pulled off America's largest foreign IPO. The AI trade is not dead — but it is getting expensive.",
    "slug": make_slug("samsung-record-profit-chip-selloff-sk-hynix-ipo"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "Tens of thousands of Indian Americans work at Nvidia, Intel, Micron, AMD and Qualcomm — the companies whose stocks whipsawed this week. For NRIs with concentrated tech portfolios, the sell-the-news rotation is a reminder that the AI memory trade requires more discipline than conviction.",
    "tags": ["samsung", "semiconductor", "sk-hynix", "micron", "ai-memory", "nri-investors", "chip-stocks"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/samsung-flags-19-fold-jump-profit-2026-07-07/"},
        {"name": "Reuters — SK Hynix IPO", "url": "https://www.reuters.com/technology/sk-hynix-shares-jump-marquee-us-debut-2026-07-10/"},
        {"name": "Stocktwits / Market Analysis", "url": "https://stocktwits.com/news/mag-7-big-tech-resurgence-chip-stocks-step-back-july-2026"},
        {"name": "Fox Business — Micron CEO", "url": "https://www.foxbusiness.com/technology/micron-ceo-ai-boom-unprecedented-memory-demand"},
        {"name": "Reuters — DeepSeek chip", "url": "https://www.reuters.com/technology/chinas-deepseek-developing-its-own-ai-chip-2026-07-07/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/3665442/pexels-photo-3665442.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Close-up of a semiconductor microchip on a printed circuit board",
    "image_attribution": "Pexels",
    "body": art1_body.strip()
}


# ── ARTICLE 2 ──────────────────────────────────────────────────────────

art2_body = """In the space of six weeks, Tata Consultancy Services signed strategic partnerships with two of the most sought-after AI companies on the planet. In May, TCS became the first global systems integrator for Mistral Forge, the enterprise AI platform built by France's Mistral AI. In June, it struck a sweeping alliance with Anthropic, the San Francisco lab behind Claude, gaining early access to new model releases and committing 50,000 of its employees to Anthropic's tools. Dario Amodei, Anthropic's co-founder and CEO, said the deal "deepens our commitment to India, our second-largest market."

TCS is not alone. Infosys signed its own Anthropic partnership in February. OpenAI has roped in both Infosys and HCLTech as enterprise distribution partners. And HCLTech went a step further in June, leading a $234 million investment in Sarvam AI — a Bengaluru startup building Indian-language foundation models — at a $1.5 billion valuation, making Sarvam India's newest AI unicorn.

The pattern is unmistakable. Every major frontier AI lab now wants an Indian IT giant in its corner. And every Indian IT giant is scrambling to sign up before the music stops.

## Why the labs need India's IT firms

The reason is not charity. Anthropic, OpenAI, and Mistral have all discovered the same problem: building a brilliant model is one thing; selling it to a risk-averse Fortune 500 bank or a European insurance company is quite another. Enterprise customers in regulated industries want bespoke deployments, compliance frameworks, integration with legacy systems, and someone to call at 3 a.m. when the model hallucinates a loan approval.

Indian IT services firms have spent decades doing precisely this kind of work — wrapping technology in governance, process, and human hand-holding. They employ millions of engineers who understand banking middleware, insurance claims workflows, and hospital information systems. The AI labs have the models. The IT firms have the Rolodex, the project managers, and the regulatory muscle.

As Anthropic's Amodei put it: the value of enterprise AI "comes from understanding business context, orchestrating complex systems, and applying deep AI engineering talent." That is a near-perfect description of what TCS, Infosys, and HCLTech have been selling for 30 years — just dressed in new vocabulary.

## The TCS playbook

TCS is moving fastest. Under its partnership with Anthropic, the company is positioning itself as "customer zero" — deploying Claude across its own engineering, finance, legal, marketing, and sales teams before selling it to clients. Diligenta, TCS's UK-based life and pensions business serving more than 22 million policyholders, will use Claude for customer service automation. TCS's banking and financial services teams are already using Claude Code to accelerate software development. And TCS iON, which runs 75 million assessments a year across 1,500 Indian cities, will offer Claude training and certification.

The Mistral partnership adds a different dimension. Mistral Forge is designed for organisations that want to fine-tune AI models on their own proprietary data — a growing requirement for companies wary of sending sensitive information to American cloud providers. TCS will set up a dedicated Centre of Excellence for Mistral, targeting banking, manufacturing, healthcare, and public-sector clients. For European customers in particular, a French AI company paired with an Indian integrator may be a more palatable option than an American lab.

The early financial results are visible. TCS reported this week that its annualised AI revenue crossed $2.6 billion in the June quarter, up from $2.3 billion three months earlier — a 13 per cent sequential jump. The company also hired 9,300 people in the quarter, its fastest pace in more than three years, even as its overall headcount has been shrinking.

## The existential bet

The partnerships are not just about growth. They are about survival. India's $315 billion IT services sector is facing what Nomura analysts have called a "perfect storm." AI tools are compressing delivery timelines and team sizes, pushing down the per-project revenue that has been the industry's lifeblood. Citi expects a fourth straight year of subdued constant-currency growth. IT stocks fell 9.5 per cent in the June quarter even as India's benchmark Nifty 50 index gained 6.9 per cent.

TCS Chairman N. Chandrasekaran captured the mood at the company's annual general meeting last month when he said "the day is not far" when TCS would have an equal number of AI agents and employees. That is a staggering statement from the leader of a company that employs more than 600,000 people. It implies not replacement but transformation — a workforce where every human consultant is paired with, and amplified by, an AI counterpart.

The question for Indian tech workers, many of them in the United States on H-1B visas, is what this transformation means for career trajectories. If TCS and Infosys become primarily AI distribution platforms — aggregating models from Anthropic, Mistral, and OpenAI and packaging them for enterprise clients — the premium will shift from coding volume to AI orchestration, compliance engineering, and domain expertise. The engineer who understands both Claude's capabilities and a bank's Basel III obligations will be worth more than one who can write Java faster.

## The risks

Not every bet will pay off. The AI lab landscape is shifting fast; today's partner could be tomorrow's competitor. Anthropic and OpenAI are both building their own enterprise sales teams, and there is no guarantee they will need middlemen forever. Mistral, still a young company, could be acquired or could pivot. And the economics of the distribution model remain unproven — if AI truly automates large chunks of IT services work, the margins on "AI implementation" may be thinner than the margins on traditional outsourcing.

HCLTech's $150 million bet on Sarvam AI represents a different hedge entirely: owning a piece of the model layer, not just distributing someone else's. If Sarvam's Indian-language models find traction in government services, banking, and insurance — sectors where English-only models fall short — HCLTech will have both the technology and the implementation muscle.

For now, the race is on. The $315 billion question is whether Indian IT firms can reinvent themselves fast enough to ride the AI wave rather than be swallowed by it. The partnerships with Anthropic, Mistral, and OpenAI are their best bet. Whether they are enough is a story that will unfold over the next three to five years — and one that matters deeply to every Indian professional whose career was built on the outsourcing model that AI is now reshaping."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Every Major AI Lab Is Racing to Sign an Indian IT Giant. The $315 Billion Industry's Survival Depends on It.",
    "subheadline": "TCS partnered with Anthropic and Mistral in six weeks. Infosys and HCLTech signed their own deals. The frontier AI labs need enterprise distributors. India's IT firms need a reason to exist. It is a marriage of mutual desperation — and it might just work.",
    "slug": make_slug("indian-it-anthropic-mistral-openai-ai-distribution-race"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "For the hundreds of thousands of Indian tech professionals in the US and UK — many at TCS, Infosys, and HCLTech — the AI partnership race will determine whether their employers reinvent or decline. The premium is shifting from coding volume to AI orchestration and domain expertise.",
    "tags": ["tcs", "anthropic", "mistral", "infosys", "hcltech", "openai", "sarvam-ai", "indian-it", "ai-enterprise"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "TechCrunch — Anthropic taps TCS", "url": "https://techcrunch.com/2026/06/11/anthropic-taps-tcs-to-scale-its-enterprise-ai-deployments/"},
        {"name": "Reuters — TCS partners Anthropic", "url": "https://www.reuters.com/technology/indias-tcs-partners-anthropic-drive-enterprise-ai-scaling-2026-06-11/"},
        {"name": "TechCircle — TCS Mistral partnership", "url": "https://www.techcircle.in/2026/05/28/tcs-partners-with-mistral-to-bring-enterprise-ai-platform-forge-to-global-clients"},
        {"name": "TechCrunch — Sarvam AI unicorn", "url": "https://techcrunch.com/2026/06/16/sarvam-becomes-indias-newest-ai-unicorn-with-234-million-funding/"},
        {"name": "Reuters — Indian IT muted Q1", "url": "https://www.reuters.com/technology/indian-it-firms-face-muted-q1-2026-07-06/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1148820/pexels-photo-1148820.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Server racks in a modern data centre powering AI workloads",
    "image_attribution": "Pexels",
    "body": art2_body.strip()
}


# ── INSERT ──────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:80]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
