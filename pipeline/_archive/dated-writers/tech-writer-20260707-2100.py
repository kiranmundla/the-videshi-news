#!/usr/bin/env python3
"""Tech writer — July 7 2026, 2100 UTC run"""
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
    # ── Article 1: Samsung Q2 profit surges 19x but shares plunge ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Samsung Just Posted a 19-Fold Profit Jump. Investors Wiped $80 Billion Off Its Stock Anyway.",
        "subheadline": "The AI memory chip boom delivered Samsung's biggest quarter in years — then the market asked: how long can this last?",
        "slug": make_slug("samsung-q2-19-fold-profit-shares-plunge-ai-memory-chip"),
        "category": "technology",
        "vertical": "semiconductors",
        "diaspora_angle": "NRI investors in semiconductor ETFs face a paradox: record profits but deepening market anxiety over the sustainability of the AI chip cycle that also underpins India's own data-centre ambitions.",
        "tags": ["samsung", "memory-chips", "ai-infrastructure", "semiconductors", "nri-investors", "sk-hynix"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/samsung-flags-19-fold-jump-profit-shares-slump-jitters-ai-boom-may-stall-2026-07-07/"},
            {"name": "Citi Research", "url": "https://www.reuters.com/technology/"},
            {"name": "Morningstar", "url": "https://www.morningstar.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e2/Samsung_headquarters.jpg",
        "image_caption": "Samsung Electronics headquarters in Suwon, South Korea",
        "image_attribution": "Wikimedia Commons",
        "body": """Samsung Electronics just delivered what should have been the earnings report of the decade. Instead, it became a cautionary tale about what happens when even blowout results can't keep up with market expectations.

On Tuesday, the South Korean chipmaking giant estimated its April–June operating profit at 89.4 trillion won — roughly $58.4 billion — a staggering 19-fold surge from the 4.7 trillion won it reported a year earlier. Revenue rose 129 per cent to 171 trillion won. Both figures beat analyst consensus, including the LSEG SmartEstimate of 87.3 trillion won.

The market's response? Samsung shares dropped as much as 10.1 per cent, eventually closing down 6.9 per cent. Rival SK Hynix fell 6 per cent. South Korea's benchmark KOSPI index plunged 4.9 per cent — its sharpest single-day decline in months.

## What's rattling investors

The culprit is not what Samsung did. It's what comes next.

The AI data-centre boom has sent memory chip prices to record highs. Citi Research estimates that average selling prices for DRAM and NAND climbed 44 per cent and 53 per cent quarter-on-quarter, respectively, in Q2. Samsung's windfall is a direct product of that pricing power — artificial intelligence workloads are voracious consumers of high-bandwidth memory (HBM), the specialised chips that sit atop AI accelerators from Nvidia and AMD.

But the very companies driving that demand — Microsoft, Meta, Amazon, Alphabet — are now under intense scrutiny for their combined AI infrastructure spending, which is set to exceed $700 billion this year. Morgan Stanley warned on Monday that semiconductor stocks would face continued pressure as hyperscalers exercise "more capex discipline in the near-term."

"Samsung's strong earnings were widely expected and had largely been priced in after its shares rallied ahead of the results," said Albert Yong, a managing partner at Petra Capital Management. "Investors remain concerned about the sustainability of the AI boom and the risk of slower AI infrastructure spending by major U.S. technology firms."

## The memory cycle's fragile logic

Morningstar analyst Jing Jie Yu noted that Samsung's revenue estimate was not as strong as hoped, suggesting that DRAM price hikes may have already begun to moderate. "We believe the slight revenue miss was largely driven by more moderate DRAM price hikes than expected, which likely spooked investors who are increasingly pricing in structural strength in memory prices," Yu said.

The paradox is structural. The explosive growth in HBM production has tightened supply of conventional memory chips used in smartphones, PCs, and servers — propping up prices across the board. But if AI spending slows even modestly, the pricing cascade could reverse.

Samsung set aside substantial funds for employee bonuses linked to operating profit, a provision agreed in a May wage deal. Without those provisions, its profit would have exceeded 100 trillion won — a number that would have been unthinkable eighteen months ago.

## Where India fits in

For NRI investors, the Samsung story is impossible to ignore. Semiconductor ETFs have been among the most popular holdings in Indian-American portfolios during the AI bull run, and Samsung is the world's largest memory chipmaker by revenue. Its results have direct implications for Micron Technology, run by Indian-origin CEO Sanjay Mehrotra, which is building a $2.75 billion chip packaging facility in Gujarat — India's first major memory-chip investment.

India's own AI ambitions are built on the assumption that compute will remain abundant and infrastructure spending will keep growing. The data-centre boom that Delhi has courted with tax-free status through 2047, and the hundreds of billions pledged by Reliance, Adani, and Tata at the India AI Summit, all depend on the very cycle Samsung's stock price is now questioning.

SK Hynix, which listed on the Nasdaq on Monday, will be another test of investor confidence. If the market's appetite for memory-chip stocks continues to weaken, it could cool the enthusiasm for India's own semiconductor ambitions — or, conversely, make India's lower-cost positioning more attractive.

## The bottom line

Samsung's earnings prove the AI memory trade works — for now. But the market is pricing in a future where the music slows. For the Indian diaspora, the stakes go beyond portfolio returns: the chips Samsung and its rivals build are the raw material of India's AI infrastructure dreams. If the boom falters, those dreams get more expensive.

Samsung will announce detailed divisional results on July 30. Until then, the biggest question in semiconductors is whether the AI spending machine can keep accelerating fast enough to justify valuations that have already priced in a revolution."""
    },
    # ── Article 2: Beijing mulls curbing overseas access to Chinese AI models ──
    {
        "id": str(uuid.uuid4()),
        "headline": "Beijing Is Considering Building a Great Wall Around Its AI Models. Indian Startups Should Be Paying Attention.",
        "subheadline": "Chinese authorities have been meeting with Alibaba, ByteDance, and Z.ai about restricting overseas access to their most advanced models — both open-source and closed.",
        "slug": make_slug("beijing-china-restrict-ai-models-overseas-india-sovereign"),
        "category": "technology",
        "vertical": "ai-geopolitics",
        "diaspora_angle": "Indian AI startups heavily reliant on cheap Chinese open-source models face a potential supply shock; India's sovereign AI push through Sarvam and BharatGPT looks increasingly prescient.",
        "tags": ["china", "ai-regulation", "deepseek", "sovereign-ai", "india-ai", "geopolitics", "open-source"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/technology/artificial-intelligence/beijing-is-looking-curbing-overseas-access-chinas-top-ai-models-sources-say-2026-07-07/"},
            {"name": "Devdiscourse", "url": "https://www.devdiscourse.com/article/technology/3389791-china-considers-tightening-control-over-ai-models"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730212/pexels-photo-37730212.jpeg",
        "image_caption": "Server racks in a modern data centre — AI model access may soon be treated as a sovereign asset",
        "image_attribution": "Pexels",
        "body": """For the past year, the story of Chinese AI has been one of aggressive openness. DeepSeek's R1 model stunned Silicon Valley with its efficiency. Alibaba's Qwen family became a workhorse for developers on every continent. ByteDance's models powered a generation of global apps. The message was clear: Chinese AI was cheap, capable, and available to anyone willing to use it.

That era may be ending.

Reuters reported on Tuesday that Chinese authorities have spent the past month holding meetings with top tech firms — including Alibaba, ByteDance, and the startup Z.ai — about potentially restricting overseas access to China's most advanced AI models. The discussions, led by China's Ministry of Commerce, cover both closed-source and open-source versions, and include models that have not yet been released.

## What's on the table

Officials discussed making the leak or theft of proprietary AI technology an offence under China's stringent national security law, according to sources familiar with the talks. They also raised the possibility of new measures to restrict who can fund domestic AI startups — a clear signal that Beijing views its AI models not merely as commercial products, but as strategic national assets.

The scope of the potential restrictions is still being debated. They may apply only to future, more advanced models, and it remains unclear when — or whether — formal rules will materialise. But the direction of travel is unmistakable.

If Beijing follows through, the global implications are significant. Since DeepSeek's breakthrough, Chinese AI models have made substantial inroads internationally, largely on the strength of their low cost and open availability. Restricting access to those products would ripple across AI markets worldwide, pushing costs higher for the thousands of companies that have built workflows around Chinese models.

## The mirror image of Washington

The irony is that Beijing's deliberations mirror moves Washington has already made. The Trump administration has restricted exports of frontier AI models on national security grounds, with OpenAI limiting access to its newest GPT-5.6 models and the White House temporarily banning Anthropic's most capable system from overseas deployment before reversing course. Both superpowers are arriving at the same conclusion: cutting-edge AI is too important to share freely.

For the rest of the world — and for India in particular — this creates an increasingly uncomfortable two-track AI ecosystem.

## What it means for Indian AI

Indian startups and enterprises have been among the most enthusiastic adopters of Chinese open-source AI. DeepSeek's models are widely used by Indian developers for inference workloads precisely because they are cheap and performant. Alibaba's Qwen models power applications ranging from customer service bots to code generation across Indian IT firms. For bootstrapped Indian AI companies that cannot afford OpenAI or Anthropic pricing, Chinese models have been the default option.

A partial or full restriction on access to advanced Chinese models would force a recalibration. Indian companies would need to rely more heavily on American models — which carry their own access restrictions and are considerably more expensive — or accelerate the development of homegrown alternatives.

India's own sovereign AI push, once dismissed by some as nationalistic posturing, suddenly looks far more strategic. Sarvam AI, which raised $234 million from HCLTech and Bessemer Venture Partners to build India-specific models, is positioned to benefit directly from any bifurcation in global AI supply chains. The broader IndiaAI Mission, which has funded foundational model development by companies including BharatGPT and CoRover, gains new urgency if Chinese models are no longer freely available.

## The NRI calculus

For Indian-origin AI researchers working in the United States and Europe, the emerging AI Cold War raises uncomfortable questions about access and collaboration. Many have contributed to models on both sides of the divide, and a more restrictive global regime could limit the cross-pollination that has driven much of AI's progress.

The pattern is familiar from semiconductors: first the US restricted chip exports to China, then China restricted rare-earth exports to the US. Now, AI models themselves are becoming the contested resource. India, which has positioned itself as a bridge between the two technology blocs, may find that the bridge is getting narrower.

## What comes next

No formal restrictions have been announced, and the discussions may yet fizzle. But the fact that China's Ministry of Commerce is convening these talks at all — and that companies like Alibaba and ByteDance are participating — suggests the conversation has moved beyond the theoretical.

For Indian technologists, whether building startups in Bengaluru or leading AI teams in San Francisco, the message is clear: the era of globally accessible, borderless AI is not guaranteed. Sovereign capability is no longer a luxury. It may soon be a necessity."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
