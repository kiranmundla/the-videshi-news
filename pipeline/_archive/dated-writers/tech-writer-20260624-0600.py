#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for env_name in [".env.supabase"]:
    for base in [Path.home(), Path.home() / "workspace"]:
        env_file = base / env_name
        if env_file.exists():
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
        "headline": "Satya Nadella Spent a Decade Cheering AI On. Now He Wants the Industry to Slow Its Own Hype.",
        "subheadline": "Microsoft's chief executive is warning that AI power is dangerously concentrated — and quietly opening Azure to cheaper models, including China's DeepSeek, to break the logjam.",
        "slug": make_slug("satya-nadella-microsoft-ai-concentration-deepseek-azure-warning-nri-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For the tens of thousands of Indian engineers inside Microsoft and its enterprise customers, Nadella's pivot from a single-model bet to a multi-model marketplace decides whose AI skills stay in demand and whose roles get automated first.",
        "tags": ["satya-nadella", "microsoft", "ai", "azure", "openai", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Wall Street Journal", "url": "https://www.wsj.com/tech/ai/microsoft-satya-nadella-ai-economy"},
            {"name": "CoinCentral", "url": "https://coincentral.com/microsoft-ceo-satya-nadella-ai-power-concentrated"},
            {"name": "AInvest", "url": "https://www.ainvest.com/news/nadella-warns-ai-monopoly-microsoft-190b-bet-tests-market"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/78/MS-Exec-Nadella-Satya-2017-08-31-22_%28cropped%29.jpg",
        "image_caption": "Microsoft chief executive Satya Nadella, who is pressing the AI industry to spread its gains more widely.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Satya Nadella helped start the fire. Microsoft's early billions turned OpenAI from a research lab into the colossus that kicked off the generative-AI race. Now the man who lit the match is asking everyone to stop pouring on accelerant.

In a Wall Street Journal interview this week, Microsoft's chief executive delivered an unusually blunt warning: AI power is becoming dangerously concentrated, and the companies building it cannot keep insisting that white-collar work is about to vanish while simultaneously demanding ever more compute to make it happen. "You can't say, hey, all white-collar jobs are gone and this could even be a weapon and we will use all the power to build data centers," he said. AI firms, he argued, must "earn the social permission" to reorganize how people work — not just eliminate jobs and bank the savings.

This is a striking turn from the executive who has played elder statesman in the trillion-dollar AI contest. And it is not only rhetoric.

### A quiet shift under the Azure hood

Microsoft started the month by launching its own family of in-house AI models, tuned for specific corporate tasks at a fraction of the cost of frontier systems from OpenAI, Anthropic and Google. More provocatively, the company is weighing whether to host a version of DeepSeek, the ultralow-cost Chinese model that OpenAI and Anthropic have accused of distilling — essentially copying — their best work. Hosting it on Azure would hand the Chinese model-maker a dramatic surge in usage, and pile fresh price pressure on the very partners Microsoft helped build.

The strategic logic is cold. In the second half of 2025, Microsoft's Copilot users were increasingly defecting to Google's Gemini, according to Recon Analytics. Without a top-tier model of its own, Microsoft is choosing to become the neutral marketplace — the place where any model, cheap or premium, runs on its cloud. Nadella's framing: companies should build systems that let them swap the underlying model without losing their proprietary expertise, keeping the "learning loop" inside the firm rather than renting a brain from a single vendor.

### Why an engineer in Redmond should read the fine print

For the Indian diaspora, this is not abstract boardroom philosophy. Microsoft employs a vast cohort of Indian and Indian-American engineers, and its enterprise customers — the banks, insurers and consultancies that hire H-1B talent by the thousand — take their cues from whatever Azure decides to favor.

A multi-model Azure changes the skill map. Engineers who bet their careers purely on OpenAI's stack now have reason to broaden out; fluency across models, orchestration layers and cost optimization becomes the durable skill. The shift toward cheaper, task-specific models also means more of the grunt work gets automated sooner, even as the architecture work — wiring these systems together securely — grows. Nadella's warning that productivity gains could "accrue so narrowly that the political system intervenes" is, read another way, a warning that the people who merely operate AI are more exposed than those who design how it is governed inside a company.

### The money behind the message

The reset comes with a price tag that explains the anxiety. Microsoft's last earnings report disclosed that total capital spending will hit roughly $190 billion this calendar year, pushing adjusted free cash flow uncomfortably close to negative territory. Jefferies analyst Brent Thill notes Microsoft has "no self-imposed ceiling" on that spending relative to cash flow. The stock has slummped more than 20% this year — the worst performer among the big-tech names — and the company has shed over $1 trillion in market value since last fall.

Wall Street, for now, is forgiving: 35 of 37 analysts rate the shares a Buy, with an average target well above today's price. But the patience is conditional on the spending converting into durable revenue rather than an open-ended burn.

### What's next

Watch whether the DeepSeek hosting actually happens — it would be the loudest signal yet that Microsoft is serious about commoditizing the model layer it once tried to monopolize. For NRI professionals, the practical takeaway is to treat model-agnostic skills, security, and AI governance as the safer bets. Nadella is telling the industry the era of one model to rule them all is ending. The engineers who internalize that first will be the ones still standing when the capex bill comes due.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron Is About to Post a 1,000% Profit Jump. The Indian-Born CEO Behind It Is Sitting on a Memory Shortage With No End in Sight.",
        "subheadline": "Sanjay Mehrotra's company has become one of the AI boom's biggest winners — its high-bandwidth memory sold out through 2026 — as it builds a fab in Gujarat that could anchor India's chip ambitions.",
        "slug": make_slug("micron-sanjay-mehrotra-q3-earnings-hbm-shortage-gujarat-fab-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Micron is the rare AI trade that connects an NRI investor's brokerage account to Modi's semiconductor push — its Gujarat plant is India's first major memory facility, and its stock has become a diaspora favorite for betting on the chip supercycle.",
        "tags": ["micron", "sanjay-mehrotra", "semiconductors", "hbm", "india-fab", "indian-tech"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/ai-boom-hbm-demand-micron-dram-revenues-q3"},
            {"name": "Barchart", "url": "https://www.barchart.com/story/news/micron-q3-earnings-mu-stock"},
            {"name": "Stocktwits", "url": "https://stocktwits.com/news/micron-anthropic-alliance-q3-results"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Micron chief executive Sanjay Mehrotra, who is steering the memory maker through an AI-driven supply crunch.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When Micron Technology reports earnings after the bell on June 24, the headline will write itself: profit up roughly 1,000% from a year ago. The number is real. It is also, in a sense, the least interesting thing about the quarter.

Analysts expect Micron to report revenue near $35 billion — nearly quadruple last year's figure — with adjusted earnings somewhere around $20 a share, against $1.91 in the year-ago quarter. Management has guided to an 81% gross margin, up from 39% a year earlier. Those are not numbers a memory-chip company is supposed to produce. Memory has always been the brutal, cyclical, commodity end of the semiconductor world, where gluts crush prices and good years are short. The man who has steered Micron into this once-unthinkable position is Sanjay Mehrotra, the Kanpur-born, IIT-adjacent engineer who co-founded SanDisk before taking over Micron in 2017.

### The bottleneck is the business

The reason for the eye-watering margins is not clever pricing. It is scarcity. Micron's high-bandwidth memory — the stacked chips that sit beside Nvidia's GPUs and feed them data fast enough to train large AI models — is sold out through the end of 2026. The company confirmed that on an earlier call and has not walked it back. Its two rivals, SK Hynix and Samsung, are hitting the same capacity walls. Three companies sit at a physical chokepoint in the AI supply chain, and when supply cannot stretch, price does the work.

The position got stronger this week. Micron extended a strategic partnership with Anthropic covering AI memory architecture and long-term supply, just weeks after participating in the Claude-maker's enormous Series H round. Bernstein's Mark Li responded by lifting his price target sharply, citing improved visibility into both conventional and HBM pricing.

### A word of caution on the stock

Diaspora investors who have ridden Micron up roughly 280% this year should note the other side. Options markets are signaling a possible post-earnings pullback — the put-to-call ratio sits near parity, the stock's relative strength index is brushing overbought territory, and Micron has a seasonal habit of losing ground in July. A blowout quarter does not guarantee a blowout reaction, especially when expectations are this stretched. The risk in a "priced for perfection" name is not that results are bad; it is that they are merely excellent.

### Why this lands differently for Indians

Two reasons make Micron more than another AI ticker for the diaspora. First, it is one of the most accessible ways for an NRI to bet on the memory side of the AI supercycle — less crowded than Nvidia, more leveraged to the raw scarcity of chips. Second, and more durably, Micron is building a major assembly and test facility in Sanand, Gujarat, the first big memory plant under India's Semiconductor Mission. It is the marquee proof point for Modi's pitch that India can move up the chip value chain from design services into actual fabrication.

For an Indian semiconductor professional weighing whether the India fab story is real or political theater, Micron's Gujarat plant is the answer that matters. A company posting these margins, run by an Indian-origin chief executive, putting capital into Indian soil, is the clearest signal yet that the global memory map now runs through Gujarat — not just Boise and Hiroshima.

### What's next

Listen past the EPS number on the call. The questions that matter are whether HBM remains sold out into 2027, how fast the Gujarat facility ramps, and whether management dares to call a top to the pricing cycle. Memory has always punished investors who mistook a peak for a plateau. Mehrotra has navigated more of these cycles than almost anyone alive. Whether he signals confidence or caution will tell you more than the 1,000% will.
"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India Just Shipped $2.4 Billion of Phones to America in a Single Month. Apple Is Carrying Almost All of It.",
        "subheadline": "Smartphone exports to the US jumped 47% in April even after India lost its tariff edge over China — and Trump is openly pressuring Tim Cook to build at home instead.",
        "slug": make_slug("india-smartphone-exports-us-surge-47-percent-apple-trump-cook-make-in-india-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Every iPhone an NRI buys in the US is now likely assembled in Tamil Nadu or Karnataka, turning India into a load-bearing pillar of Apple's supply chain — and a flashpoint in the US-India trade fight that could reshape diaspora business ties.",
        "tags": ["apple", "iphone", "make-in-india", "manufacturing", "trade", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "AInvest", "url": "https://www.ainvest.com/news/india-smartphone-exports-us-surge-47-april-apple"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/tata-electronics-cyber-breach-apple-tesla"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/apple-iphone-exports-india-h1-fy26"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/5554948/pexels-photo-5554948.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Workers on an electronics assembly line, the kind of operation now driving India's record smartphone exports.",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": """The number is the kind that ends arguments. In April, India shipped $2.43 billion worth of smartphones to the United States — a 47% jump from a year earlier — and Apple accounted for roughly 78% of it. Across the full fiscal year, smartphone exports to the US from India rose 86% to $19.67 billion. The iPhone is now, by value, India's single largest branded export, ahead of diamonds, automotive fuel and medicines.

What makes the figure remarkable is that it came after India lost the advantage that was supposed to be doing the work. For a stretch, India enjoyed a duty edge over China that made shifting production look like a tariff arbitrage. That edge has narrowed, and yet the exports kept climbing — a sign that the move out of China is now driven by structural diversification, not just a temporary trade loophole.

### Five factories and counting

Apple's India assembly network has grown to five plants, anchored by Foxconn's operations and Tata Electronics, which has emerged as the most important Apple manufacturing partner outside China. In April 2025, US-bound iPhone shipments from India rose 76% to about 3 million units in a single month, even as shipments from China fell 76% to 900,000. The center of gravity is visibly tilting.

It has not been frictionless. Tata Electronics disclosed a cybersecurity incident this week after a ransomware group claimed to have posted design and specification documents belonging to Apple and Tesla, both Tata customers — more than 200,000 files, according to security researchers. A separate Tamil Nadu plant faces a state health probe over farmer complaints about contamination. These are the growing pains of a supply chain being assembled at speed, and they matter to anyone betting that "Make in India" can match China's quality and scale.

### Trump enters the chat

The bigger threat is political. President Trump has said publicly that he told Tim Cook he has "a little problem" with Apple's India build-out: "I don't want you building in India... You can build in India, if you want to take care of India." With Apple having pledged $500 billion of US investment, the pressure to repatriate iPhone assembly is real, and it collides head-on with India's manufacturing ambitions. India's commerce ministry, meanwhile, is deep in trade negotiations with Washington that Jaishankar has described as complicated and unfinished.

### Why the diaspora is in the middle of this

For Indian Americans, this is one of those rare stories where the personal and the geopolitical converge in your own pocket. The iPhone you buy in California or New Jersey is now, with high probability, assembled in Sriperumbudur or near Bengaluru. That makes the diaspora both consumer and stakeholder in whether India can hold its place in Apple's chain.

It also reshapes opportunity. The build-out has created a wave of supply-chain, quality-engineering and operations roles in India that increasingly recruit returning NRIs with global manufacturing experience. And for diaspora investors, Apple's India bet has become a proxy for the entire electronics-manufacturing thesis — including the component and contract-manufacturing firms riding its coattails. A Trump-forced reversal would not just dent a Modi talking point; it would reprice that whole basket.

### What's next

The next inflection is the US-India trade deal. If it lands with smartphones protected, India's role hardens into permanence. If Trump's pressure on Cook turns into policy, the math changes overnight. Either way, a country that barely assembled phones a decade ago now sends America $2.4 billion of them in a month — and that fact alone has rewritten where the diaspora's economic interests sit on the map.
"""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"\u2705 {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"\u274c {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
for h in inserted:
    print(" -", h)
