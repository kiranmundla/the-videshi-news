#!/usr/bin/env python3
"""Videshi Technology Writer — July 7 2026 evening run."""
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


# ── ARTICLE 1: Beijing AI Model Restrictions ──

article1_body = """China is no longer content to let its best artificial intelligence walk out the front door.

In meetings held over the past month, officials from China's Ministry of Commerce sat down with executives from Alibaba, ByteDance, and the Hong Kong-listed startup Z.ai to discuss something that would have been unthinkable a year ago: restricting overseas access to the country's most advanced AI models, including systems that haven't been released yet.

The discussions, first reported by Reuters on Tuesday, mark a dramatic pivot for a country that spent the past 18 months celebrating the global spread of models like DeepSeek's R1 and Alibaba's Qwen as proof of Chinese AI prowess. Now, Beijing wants that prowess kept closer to home.

## The New AI Nationalism

The scope of the potential restrictions is still being debated. According to people familiar with the talks, limits could apply to both closed-source and open-weight models — a particularly aggressive stance, given that open-weight availability is what made Chinese AI competitive with Silicon Valley in the first place.

Officials also discussed making any leak or theft of proprietary AI technology a criminal offence under China's national security law, and raised the possibility of restricting foreign investment into domestic AI startups. The message is unmistakable: AI is now a strategic national asset in Beijing's eyes, no different from semiconductors or rare earths.

This mirrors what Washington is already doing. In June, the U.S. government ordered Anthropic to suspend overseas access to its Fable 5 and Mythos 5 models for foreign nationals. Days later, Beijing-linked commentators seized on the contrast, portraying China as the open alternative. That narrative may not survive these new discussions.

## India Gets Squeezed From Both Sides

For India's AI ecosystem, the implications are severe. Hundreds of Indian startups have built products on top of cheap, capable Chinese models — DeepSeek's inference costs are a fraction of OpenAI's or Anthropic's, and Alibaba's Qwen has become a quiet workhorse in Indian enterprise software. If Beijing restricts API access or model downloads, these companies face overnight cost increases or, worse, the need to rearchitect their entire stack.

The timing is particularly painful. American AI models are already getting harder to access. The Anthropic restriction affects any non-U.S. national, which includes Indian engineers in Bengaluru who were accessing Claude's most advanced capabilities through their companies' API keys. India's own sovereign AI efforts — Sarvam AI, Ola's Krutrim, IIT-led BharatGPT — are promising but years behind the frontier.

"India risks becoming an AI colony," warned a column in The Hindu Business Line this week, arguing that the country's engineers run global tech companies but "instead of owning technology, we have become the world's digital workforce."

## What NRIs Should Watch

For Indian-origin professionals in Silicon Valley and beyond, this creates a strange new landscape. AI researchers at Google, Meta, and Microsoft find themselves building models that their counterparts in India may not be able to fully access. Indian-American founders raising capital for AI startups must now factor in model-access risk alongside the usual concerns about compute costs and talent.

The geopolitical squeeze also reshapes investment logic. India's $400 billion IT sector, already under pressure from AI-driven automation, needs to accelerate its shift from services consumption to technology ownership. The Persistent Systems–Nagarro deal, HCLTech's recent $1.14 billion AI contract win, and the growing semiconductor push under the India Semiconductor Mission are early signs that industry recognises this. But the clock is ticking.

Beijing hasn't finalised anything yet. The restrictions may only apply to future models, and the scope remains under negotiation. But the direction is clear: the era of cheap, open, globally available AI from either superpower is ending. For India, caught between two closing doors, the only durable answer is building its own."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Beijing Is Building an Iron Curtain Around Its AI. Indian Startups Should Be Worried.",
    "subheadline": "Chinese authorities are in talks with Alibaba, ByteDance and Z.ai about restricting overseas access to the country's most advanced AI models — a move that could squeeze hundreds of Indian companies built on cheap Chinese AI.",
    "slug": make_slug("beijing-ai-iron-curtain-india-startups-deepseek"),
    "category": "technology",
    "vertical": "geopolitics",
    "diaspora_angle": "Indian-origin tech workers and founders who built products on cheap Chinese AI face sudden cost pressure; India's sovereign AI efforts are years behind, leaving the diaspora-linked ecosystem exposed on both the American and Chinese fronts.",
    "tags": ["ai", "china", "geopolitics", "deepseek", "indian-startups", "sovereign-ai"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/beijing-is-looking-at-curbing-overseas-access-chinas-top-ai-models-sources-say-2026-07-07/"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/opinion/how-india-can-cut-dependency-on-global-ai-platforms/article69768294.ece"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/3452813/americas-ai-edge-is-trust-china-is-betting-well-squander-it/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Server racks in a modern data centre — the infrastructure at the centre of the US-China AI arms race",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ── ARTICLE 2: Meta Muse Image ──

article2_body = """Meta just handed half a billion Indians an AI image generator — whether they asked for one or not.

On Tuesday, Meta Platforms rolled out Muse Image, the first image-generation model from its Superintelligence Labs division, integrating it across Instagram Stories and WhatsApp chats. The model can interpret complex text prompts, accept photos as inputs, and let users edit AI-generated images through sketches and annotations — all within the apps that dominate India's digital life.

## More Than a Filter Upgrade

Muse Image will power more than 30 new AI effects for Instagram Stories, turning what was previously a collection of static overlays into a generative playground. Users can ask Meta AI in a WhatsApp chat to create images from scratch, describe edits to existing photos, or combine multiple visual elements through natural language.

The rollout begins in "select countries," but given India's strategic importance to Meta — over 500 million WhatsApp users and the largest Instagram market outside the United States — early access is all but guaranteed. Meta has confirmed plans to expand Muse Image to Facebook and Messenger in the coming months.

Basic image generation through Meta AI will remain free. More advanced creation tools will sit behind Meta's subscription plans, a monetisation model that signals how seriously Zuckerberg's company views generative AI as a revenue line beyond advertising.

The company also previewed Muse Video, a video-generation model still in early testing. If it follows the same integration path, India's 200 million-plus Instagram Reels creators could eventually generate short-form video content through a text prompt — a prospect that both excites content creators and terrifies anyone concerned about synthetic media at scale.

## The Superintelligence Labs Gambit

Muse Image is the second major model from Meta Superintelligence Labs, the division assembled last year under former Scale AI CEO Alexandr Wang to help Meta catch up with OpenAI, Anthropic, and Google DeepMind. In April, the team launched Muse Spark, a text-and-reasoning model that debuted at number four on the Artificial Analysis Intelligence Index — a meaningful comeback for a company that had been written off as an AI also-ran after Llama 4's tepid reception.

Meta's strategy differs from its competitors in one critical respect: distribution. Where OpenAI and Anthropic build standalone products, Meta pushes AI directly into apps that people already open dozens of times a day. In India, that advantage is enormous. ChatGPT has roughly 30 million Indian users. WhatsApp has 500 million. The AI that shows up inside WhatsApp doesn't need to convince anyone to download a new app.

## What This Means for the Indian Tech Diaspora

For Indian-American engineers at Meta's Menlo Park and New York offices — Meta employs thousands of Indian-origin engineers across its AI, infrastructure, and product teams — Muse Image represents the kind of work that directly touches their families back home. The model's multilingual capabilities and India-first distribution mirror a pattern that Indian-origin tech leaders have long advocated: building for scale markets, not just premium ones.

For NRI investors, Meta's AI push is the main story behind its $115 billion to $135 billion capital expenditure plan for 2026. The company's stock has already priced in significant AI upside, but the subscription model around Muse Image adds a new revenue stream that analysts haven't fully modelled.

The deeper question is whether embedding generative AI into social media creates the same engagement flywheel that Stories and Reels did — or whether it introduces new risks around misinformation and deepfakes that Indian regulators are only beginning to grapple with. For now, Meta is betting that creation beats caution. And with half a billion WhatsApp users as the test market, India will be where that bet gets settled first."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Meta Just Gave 500 Million Indians an AI Image Generator. Here's What Muse Image Does.",
    "subheadline": "Muse Image, the first image-generation model from Meta Superintelligence Labs, is rolling out across Instagram Stories and WhatsApp — putting AI-powered visual creation inside apps that dominate India's digital life.",
    "slug": make_slug("meta-muse-image-instagram-whatsapp-india"),
    "category": "technology",
    "vertical": "consumer-tech",
    "diaspora_angle": "Indian-origin engineers at Meta built Muse Image for the company's largest non-US market; NRI investors watching Meta's $115B AI spend should note the new subscription revenue stream targeting India's 500M WhatsApp users.",
    "tags": ["meta", "ai", "instagram", "whatsapp", "india", "muse-image", "generative-ai"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/meta-expands-generative-ai-tools-with-muse-image-rollout-2026-07-07/"},
        {"name": "eWeek", "url": "https://www.eweek.com/artificial-intelligence/meta-muse-spark/"},
        {"name": "AI Tech News India", "url": "https://aitechnews.in/meta-launches-muse-spark-ai-model-2026/"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16229745/pexels-photo-16229745.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "Social media app icons on a smartphone screen — Meta is pushing AI image generation into apps Indians use daily",
    "image_attribution": "Pexels",
    "body": article2_body.strip()
}


# ── ARTICLE 3: Samsung Q2 Profit Paradox ──

article3_body = """Samsung Electronics just delivered the kind of quarter most companies dream about. Investors responded by hitting the sell button.

The South Korean memory chip giant flagged a 19-fold jump in second-quarter operating profit on Tuesday, its third consecutive record quarter, powered by insatiable demand for the AI chips that train and run the world's large language models. Estimates had already been bullish. Samsung beat them anyway.

And then its shares dropped as much as 10.1 per cent before finishing the day down 6.9 per cent. Rival SK Hynix fell 6 per cent. The VanEck Semiconductor ETF shed nearly 4 per cent in New York.

## The Paradox of Peak Earnings

The market's logic is brutally simple: if this is as good as it gets, the only direction is down.

Samsung's profits have been climbing a nearly vertical line since early 2025, driven by a global chip shortage that sent DRAM and NAND prices to levels not seen since the cryptocurrency mining boom. AI data centres, which consume vast quantities of high-bandwidth memory, have been the primary demand driver. Every new GPU cluster that Nvidia, AMD, or a hyperscaler deploys needs memory chips to match.

But investors are starting to ask whether the spending can continue at this pace. Big Tech — Amazon, Alphabet, Microsoft, and Meta — is on track to spend more than $700 billion on AI infrastructure this year. Amazon alone tapped debt markets on Tuesday for a $25 billion bond sale, its second mega-raise in four months, specifically to fund AI capital expenditure. Demand for the offering peaked at $62 billion, suggesting bondholders still believe the story. Equity investors are less sure.

The fear isn't that AI demand disappears. It's that the rate of spending growth slows, which would ease the chip shortage, bring down memory prices, and compress Samsung's extraordinary margins. Wall Street has a name for this: the earnings peak trade.

## The Indian Investor's Dilemma

For NRI investors who piled into semiconductor stocks over the past year, Samsung's result is a wake-up call. The thesis that drove chip stocks to record highs — AI demand creates shortage, shortage drives prices, prices drive profits — hasn't broken. But it's being stress-tested.

Micron Technology, led by Indian-origin CEO Sanjay Mehrotra, faces the same dynamic. Its shares have risen roughly ninefold from their 52-week low, largely on the AI memory thesis. SK Hynix, which listed on Nasdaq to great fanfare just last week, saw its debut enthusiasm evaporate in Tuesday's selloff. AMD and Intel, which crushed Nvidia in the first half with gains of 171 per cent and 278 per cent respectively, also got caught in the downdraft — AMD fell 6.5 per cent and Intel dropped nearly 10 per cent.

The rotation tells a story. Investors who chased chip stocks for the AI boom are now rotating into what they see as safer ground. BlackRock recently highlighted India itself as a beneficiary of AI caution — arguing that India's economy, less exposed to AI hype cycles, offers a hedge against a potential tech correction in the US.

## What Happens Next

The bull case remains intact on paper. Samsung's own executives have said memory supply will fall "far short" of customer demand through 2027, with the shortage expected to deepen, not ease. Contract DRAM prices are projected to rise again this quarter. And Amazon's $25 billion bond sale suggests the hyperscalers aren't about to stop building.

But markets don't trade on today's reality. They trade on tomorrow's fear. The question for NRI investors — many of whom hold significant positions in US tech and semiconductor stocks through 401(k) plans, brokerage accounts, and RSUs from their employers — is whether Samsung's 19-fold profit jump marks the crescendo of the AI hardware cycle or merely the end of the beginning.

History suggests that chip cycles peak when everyone agrees they won't. We may not be there yet. But Tuesday's selloff is the market's way of saying it's starting to wonder."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "Samsung Just Posted a 19-Fold Profit Jump. Investors Dumped the Stock Anyway.",
    "subheadline": "The memory chip giant's record quarter should be a celebration. Instead, a 7% share price crash signals growing fear that the AI hardware boom may be cresting — and NRI investors holding chip stocks should pay close attention.",
    "slug": make_slug("samsung-19x-profit-ai-boom-peak-nri-investors"),
    "category": "technology",
    "vertical": "semiconductor",
    "diaspora_angle": "NRI investors who loaded up on semiconductor stocks — Micron, SK Hynix, AMD, Intel — through 401(k) plans, RSUs, and brokerage accounts face a classic peak-earnings trade as Samsung's blowout quarter triggers a sector-wide selloff.",
    "tags": ["samsung", "semiconductor", "ai-boom", "memory-chips", "nri-investors", "sk-hynix", "micron"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/samsung-flags-19-fold-jump-profit-shares-slump-jitters-ai-boom-may-stall-2026-07-07/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/amazon-aims-raise-25-billion-bond-sale-source-says-2026-07-07/"},
        {"name": "The Motley Fool", "url": "https://www.fool.com/investing/2026/07/06/amd-stock-and-intel-crushed-nvidia-in-the-first-ha/"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg",
    "image_caption": "Samsung Electronics headquarters in Suwon, South Korea — the memory chip giant's record quarter failed to reassure investors",
    "image_attribution": "Wikimedia Commons",
    "body": article3_body.strip()
}


# ── INSERT ──

articles = [article1, article2, article3]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:70]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
