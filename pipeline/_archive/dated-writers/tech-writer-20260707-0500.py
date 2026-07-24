#!/usr/bin/env python3
"""
Technology writer — July 7 2026, 05:00 UTC run
Articles:
  1. Washington AI governance: OpenAI 5% stake, GPT-5.6 restrictions
  2. Anthropic $965B valuation, IPO race
  3. AI credit wars and Indian founders
"""
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

# ─── ARTICLE 1: Washington AI governance ────────────────────────────────

art1_body = """Sam Altman has a proposition for Washington: take a 5 per cent slice of the most valuable artificial intelligence company on Earth, and perhaps the government will ease up on deciding who gets to use its products.

OpenAI has proposed giving the Trump administration a stake worth roughly $42 billion at its current valuation, the Financial Times reported last week. The offer came with a twist — Altman suggested other leading AI firms hand over similar equity, a move that would effectively create a government portfolio of Silicon Valley's most powerful technologies.

## The Crackdown No One Predicted

The gesture did not arrive in a vacuum. Days earlier, the White House formally asked OpenAI to restrict the release of its newest model, GPT-5.6, to a small group of government-vetted partners rather than opening it to the public. An internal memo from Altman acknowledged the company was complying with the request, even as he called the approval process unsustainable.

The intervention followed the Commerce Department's export controls on Anthropic's most advanced models, Fable 5 and Mythos 5, which were pulled from circulation for nearly three weeks over fears that their cybersecurity capabilities could be weaponised by foreign adversaries. Those restrictions were lifted on 30 June, but the message was clear: the era of build-first, regulate-later in AI is over.

Washington is now in advanced talks with AI companies to establish voluntary standards for model releases, Reuters reported, with an announcement potentially arriving this week. The framework would set benchmarks for advanced models and clarify who can access them, both domestically and abroad.

## What This Means for Indian Tech

For the estimated 300,000-plus Indian professionals working in AI and adjacent roles across the United States, the regulatory pivot creates a new variable in an already uncertain landscape. Stricter model-release protocols could slow hiring at labs that are already selective, while government-directed access restrictions raise questions about which clients — and which countries — get frontier AI capabilities.

Sriram Krishnan, the Indian-American entrepreneur now serving as the White House's senior AI policy advisor, sits at the centre of these negotiations. His presence ensures India's interests are at least visible in the room, but visibility is not the same as guarantee. India's own $67.5 billion AI investment push, anchored by the IndiaAI Mission's 18,000-plus GPUs, could be constrained if Washington decides its most advanced models are too sensitive for broad international deployment.

Indian AI startups like Sarvam AI and Krutrim, which depend on fine-tuning frontier models from OpenAI and Anthropic, face a practical risk: if new release protocols add weeks or months before models reach international developers, India's AI builders would operate on a delay that their Chinese counterparts — who are building independent models on domestic chips — would not face.

## The IPO Calculation

The stake proposal is also deeply tied to OpenAI's path toward an initial public offering. The company burned through $3.7 billion in cash in Q1 alone while tripling revenue to $5.7 billion. Managing regulatory goodwill is critical before going public — a government that owns equity is a government less likely to regulate aggressively.

Senator Bernie Sanders has pushed for a 50 per cent government stake in major AI companies, arguing the technology was trained on human knowledge used without permission. The 5 per cent offer looks like Altman drawing a line before someone else draws it higher.

For NRI investors eyeing the AI sector, the calculus has shifted. These are no longer pure growth stories — they are companies navigating a regulatory environment that is evolving faster than their models. The question is no longer just how powerful the next model will be, but who gets to use it."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sam Altman Offered Washington 5% of OpenAI. The Government Wants More.",
    "subheadline": "The White House restricted GPT-5.6, lifted Anthropic's export ban, and is drafting voluntary AI standards — all in one week. Indian AI builders may feel the squeeze first.",
    "slug": make_slug("openai-government-stake-gpt56-ai-regulation"),
    "category": "technology",
    "vertical": "ai",
    "diaspora_angle": "Indian AI startups dependent on frontier models face delays if new US release protocols add wait times; Sriram Krishnan sits at the centre of negotiations as White House AI advisor; 300,000+ Indian AI professionals in the US affected by regulatory shifts.",
    "tags": ["ai", "openai", "regulation", "sriram-krishnan", "indian-tech", "silicon-valley", "government"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/openai-proposes-handing-trump-administration-5-stake-ft-reports-2026-07-03/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/us-talks-with-ai-companies-voluntary-model-standards-ft-reports-2026-07-02/"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/anthropic-ipo-openai-ipo-ai-stocks/"},
        {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/07/06/white-house-requests-openai-restrict-release-of-new-gpt-5-6-model-citing-national-security-risks/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/5a/Meeting_with_Masayoshi_Son_and_Sam_Altman_%28February_3%2C_2025%29_%283x4_cropped_on_Altman%29.jpg",
    "image_caption": "Sam Altman, CEO of OpenAI, in February 2025",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip()
}

# ─── ARTICLE 2: Anthropic IPO ───────────────────────────────────────────

art2_body = """Anthropic, the artificial intelligence company behind Claude, has quietly become the most valuable private technology firm on the planet — and it is heading for Wall Street at a pace that makes SpaceX's blockbuster debut look leisurely.

The company's May funding round valued it at $965 billion, surpassing OpenAI's most recent $852 billion mark. Its annualised revenue run rate has crossed $47 billion, with Q2 revenue alone expected to reach $10.9 billion. To put that in perspective: Anthropic's revenue was roughly $4 billion as recently as July 2025. In twelve months, it has grown more than tenfold.

On 1 June, Anthropic filed confidentially with the Securities and Exchange Commission to go public. If it follows SpaceX's template — which filed on 1 April and listed two and a half months later — shares could trade as early as this autumn, likely at a valuation exceeding $1 trillion.

## Claude Code Changed Everything

The engine behind this growth has a name: Claude Code. Anthropic's AI coding agent, which generates, reviews and ships production-grade software, has driven massive enterprise adoption since late 2025. Data from business fintech Ramp shows Anthropic capturing significant market share from OpenAI in enterprise AI spending throughout 2026.

The product's grip on developer workflows is so strong that it has effectively become infrastructure — the kind of tool companies stop evaluating and start depending on. That stickiness is what makes Wall Street confident enough to price Anthropic at nearly a trillion dollars.

Meanwhile, OpenAI is reportedly weighing a delay of its own IPO to 2027 after advisors warned it could struggle to reach a trillion-dollar valuation in the current market. The company burned $3.7 billion in Q1 and is racing to build competitive coding agents, having dropped "side quest" products like Sora to focus its resources.

## The Indian Engineers Building the Models

Anthropic's research and engineering ranks include a significant number of Indian-origin AI scientists who left Google, Meta and OpenAI to join the company. While the firm does not disclose demographic breakdowns, its technical leadership reflects Silicon Valley's broader pattern: Indian professionals hold an outsized share of senior AI engineering roles across the industry.

For these researchers, an Anthropic IPO is not just a corporate milestone — it is a personal one. Early employees with equity could see life-changing liquidity events, adding to the growing wealth created by Indian-origin technologists in the AI boom.

## How NRI Investors Can Get Exposure

Individual investors cannot buy Anthropic shares directly until the IPO, but two public companies offer indirect exposure through their substantial stakes.

Amazon has invested roughly $12 billion in Anthropic through convertible notes and holds one of the largest external positions. The Anthropic stake, while not separately valued on Amazon's balance sheet, represents a paper windfall that could run into tens of billions once the company trades publicly. Alphabet, through Google, also holds a significant stake from multiple investment rounds.

For NRI investors already holding Amazon or Alphabet in their portfolios, the Anthropic IPO adds a hidden lever. For those who do not, the coming listing creates a decision point: buy pre-IPO exposure through these proxies, or wait for what will likely be one of 2026's most anticipated debut days.

## The Data Centre Appetite

Anthropic's growth requires staggering infrastructure. This week, the company signed a 20-year, $19 billion lease with TeraWulf for a 401-megawatt data centre campus in Kentucky — a single deal that underscores the sheer physical footprint that frontier AI demands. The facility, a former aluminium smelter, will begin operating in late 2027.

India's data centre industry, which just received tax-free status until 2047, could eventually serve as a lower-cost option for AI companies seeking to diversify their compute footprint. But for now, the vast majority of frontier AI training happens in the United States, where power, chips and regulatory certainty converge.

The question for India's tech ecosystem is not whether Anthropic matters — it clearly does. The question is whether Indian infrastructure, talent and capital can capture a meaningful share of the value that companies like Anthropic are creating, rather than simply supplying the engineers who build it."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Anthropic Is Worth More Than OpenAI. Its Trillion-Dollar IPO Could Come This Fall.",
    "subheadline": "Claude Code turned an AI lab into a $965 billion juggernaut. For Indian engineers with early equity and NRI investors eyeing Amazon and Alphabet, the stakes are enormous.",
    "slug": make_slug("anthropic-965-billion-ipo-claude-code-nri-investors"),
    "category": "technology",
    "vertical": "ai",
    "diaspora_angle": "Indian-origin AI researchers at Anthropic stand to gain from IPO equity; NRI investors can access exposure through Amazon and Alphabet stakes; India's data centre industry could benefit from AI companies diversifying compute footprints.",
    "tags": ["ai", "anthropic", "ipo", "claude", "silicon-valley", "indian-tech", "nri-investors"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/07/06/anthropic-could-be-next-mega-ipo-how-to-invest/"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/07/05/anthropic-could-be-1-trillion-ipo-2-stocks-own-piece/"},
        {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/terawulfs-stock-gains-after-a-19-billion-deal-with-anthropic"},
        {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/anthropic-ipo-openai-ipo-ai-stocks/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Dario_Amodei_at_TechCrunch_Disrupt_2023_01_%28cropped%29.jpg",
    "image_caption": "Dario Amodei, CEO of Anthropic, at TechCrunch Disrupt 2023",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip()
}

# ─── ARTICLE 3: AI Credit Wars ──────────────────────────────────────────

art3_body = """Across Silicon Valley, startup founders are fielding competing offers from the world's biggest artificial intelligence companies — and some of them are so generous that early-stage companies may not need to raise venture capital at all.

OpenAI, Anthropic, Google Cloud and Amazon Web Services are locked in an escalating battle to win startup customers, handing out computing credits worth millions of dollars apiece, the Wall Street Journal reported. In some cases, founders have received offers totalling more than $3 million in combined credits from multiple companies — roughly the size of a median US seed round, according to PitchBook data.

Google Cloud is offering select startups up to $500,000 in cloud credits with early access to Gemini models. In some cases, it throws in access to DeepMind engineers — the kind of technical mentorship that money alone cannot buy. Microsoft Azure provides credits usable for OpenAI's models, while AWS has expanded its programme to cover third-party models on its Bedrock platform, including Anthropic's Claude and Meta's Llama.

## The Economics of Desperation

The credit war might look like generosity, but it is strategic urgency dressed in corporate philanthropy. AI companies face three simultaneous pressures: both OpenAI and Anthropic are preparing for IPOs that demand demonstrable customer growth, cheaper open-source models from China (including DeepSeek and Z.ai's GLM-52) are eating into their market share, and the cost of AI inference — the computing power needed to run models — remains stubbornly high.

Winning a startup today means locking in a customer whose usage will scale as the company grows. The credits are not gifts; they are customer acquisition costs amortised over years.

For some founders, the maths has changed fundamentally. AI-voice startup founder Hans Ibarra told the Journal that the competing offers have effectively extended his runway, reducing the urgency to raise outside capital. Others have played AI companies against each other, leveraging one offer to extract better terms from a rival.

## Where Indian Founders Fit

Indian-origin founders are uniquely positioned to benefit. They represent one of the largest and most active founder demographics in Silicon Valley, and many are building AI-native companies that are precisely the targets these credit programmes are designed for.

Google has gone further in India specifically. Its AI Futures Fund, in partnership with venture capital firm Accel, is investing up to $2 million per startup through the Atoms programme, with up to $350,000 in additional cloud and AI credits per company. The programme explicitly targets both India-based founders and those of Indian origin, with a focus on agentic AI, multimodal systems, sovereign AI and physical AI applications.

The first cohort, selected from more than 4,000 applications, deliberately excluded "wrapper" startups — companies that merely layer chatbot features over existing software without reimagining workflows. Roughly 70 per cent of rejected applications fell into that category, according to Accel partner Prayank Swaroop.

For Indian AI companies like Sarvam AI, BrowserStack's AI testing suite and Krutrim, access to free inference at scale can accelerate product development in ways that matter commercially. Fine-tuning a large language model on domain-specific Indian data — court documents in Hindi, medical records in Telugu, financial reports in Marathi — requires significant compute. Free credits turn that from a fundraising milestone into a Tuesday.

## The Catch

There is always a catch. Credits create dependency. A startup built on Google Cloud credits will likely stay on Google Cloud. One that trains on AWS Bedrock credits will find it expensive and disruptive to migrate. The AI giants are not subsidising startups out of altruism — they are building moats, one free GPU-hour at a time.

For Indian founders weighing these offers, the decision is partly technical and partly strategic. Choosing a cloud provider in 2026 is not just about uptime and pricing — it is about which AI ecosystem a company wants to grow into, which models it wants to build on, and which platform's lock-in it can most comfortably live with.

The credit wars will not last forever. When OpenAI and Anthropic are public companies answering to quarterly earnings calls, the free-credit taps will tighten. The founders who use this window to build real products on real customers — rather than optimising for runway extension — will be the ones who survive the transition."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "AI's Biggest Companies Are Giving Away Millions in Free Credits. Indian Founders Are Cashing In.",
    "subheadline": "OpenAI, Anthropic and Google are in a credit war for startup customers. For Indian-origin founders in the Valley and in Bengaluru, the free compute changes everything — for now.",
    "slug": make_slug("ai-credit-wars-startup-indian-founders-google-openai"),
    "category": "technology",
    "vertical": "ai",
    "diaspora_angle": "Indian-origin founders are among the largest beneficiaries of AI credit programmes in Silicon Valley; Google's dedicated India AI fund with Accel offers $2M plus $350K in credits per startup; Indian AI companies like Sarvam AI benefit from free compute for domain-specific model training.",
    "tags": ["ai", "startups", "indian-founders", "google-cloud", "openai", "silicon-valley", "venture-capital"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/ai-giants-are-handing-out-tons-of-free-computing-power-to-grab-startup-share"},
        {"name": "Google Blog", "url": "https://blog.google/technology/developers/google-startups-accelerator-india-ai/"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/2026/03/17/google-accel-india-accelerator/"},
        {"name": "Reuters", "url": "https://www.reuters.com/technology/google-accel-partner-back-indian-ai-startups-2025-11-27/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg",
    "image_caption": "Server rack in a blue-lit data centre — the physical infrastructure behind AI's credit wars",
    "image_attribution": "Pexels",
    "body": art3_body.strip()
}

# ─── INSERT ──────────────────────────────────────────────────────────────

articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
