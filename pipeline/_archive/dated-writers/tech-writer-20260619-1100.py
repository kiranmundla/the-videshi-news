#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Accenture's Stock Just Cratered to a 7-Year Low. The Company That Employs the Most Indians Is Flashing a Warning.",
        "subheadline": "Bookings shrank, AI clients are stalling at the pilot stage, and the firm has stopped breaking out its AI revenue. For Indian engineers, the world's biggest consultancy is the canary in the coal mine.",
        "slug": make_slug("accenture-q3-fy26-earnings-bookings-decline-ai-indian-it-workers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Accenture employs more Indians than any other firm on earth; its stalling bookings and AI-driven caution are an early signal for the hundreds of thousands of Indian engineers whose careers run through global IT services.",
        "tags": ["accenture", "indian-it", "ai", "tech-jobs", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/business/accenture-forecast-iran-war-shares-tumble"},
            {"name": "Investor's Business Daily", "url": "https://www.investors.com/news/technology/accenture-stock-fiscal-q3-2026-results/"},
            {"name": "StockTitan", "url": "https://www.stocktitan.net/news/ACN/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/45/Julie_Sweet_at_the_World_Economic_Forum.jpg",
        "image_caption": "Accenture chair and CEO Julie Sweet speaking at the World Economic Forum",
        "image_attribution": "Wikimedia Commons",
        "body": """Accenture's shares fell more than 17% on Thursday, sliding toward a seven-and-a-half-year low after the world's largest consulting firm reported fiscal third-quarter results that missed on the one number Wall Street cares about most right now: new business.

Revenue rose 6% to $18.72 billion for the quarter ended May 31, just short of the $18.75 billion analysts expected. Earnings of $3.80 a share beat estimates. But new bookings — the pipeline of future revenue — fell 2% in dollars to $19.32 billion, against forecasts that they would *grow* nearly 5%. The company also trimmed the top of its full-year revenue forecast to 3-4% growth from 3-5%, and warned that the conflict in the Middle East shaved $100 million off the quarter's revenue and $400 million off bookings as clients slowed decisions.

For most readers this is a line in the markets section. For the Indian diaspora, it is something closer to a weather report on their own industry. Accenture employs roughly 800,000 people, and more of them are in India than in any other country — Bengaluru, Hyderabad, Chennai and Pune together form the firm's largest delivery base on the planet. When Accenture catches a cold, the question for an Indian engineer in New Jersey or a delivery lead in Hyderabad is whether it is contagious.

### The AI paradox

The most telling detail is one Accenture chose to bury: it will no longer break out its "AI bookings" as a separate figure. For two years, AI was the headline number management waved at investors. Quietly retiring it suggests the gap between AI demand and AI dollars has become awkward to display.

The pattern echoes what India's own IT majors reported this earnings season. Pipelines look healthy; revenue conversion does not. Clients commission proof-of-concept AI projects, then stall before scaling them into the large, multi-year contracts that actually pay salaries. Generative AI is simultaneously the thing clients want to buy and the thing that lets a vendor deliver the same work with fewer people — which is precisely why "more bookings" no longer translates neatly into "more hiring."

CEO Julie Sweet leaned into the parts of the story that still sell: 104 client bookings of $100 million or more this year, up 13%, and a $4.2 billion bet on cybersecurity through majority stakes in Dragos and acquisitions of runZero and NetRise. The company plans to spend $9 billion on acquisitions this year, nearly double last year's $5 billion, concentrating on AI, cloud, data and security. The message to staff: the work is moving up the value chain, toward AI orchestration and operational-technology security, and away from the labour-arbitrage model that built the industry.

### Why the diaspora should read the fine print

That shift is the whole story for Indian professionals. The old escalator — join an IT services firm in India, prove yourself, get deputed to a US client site on an L-1 or H-1B, build a life in the Bay Area or Dallas — was powered by selling hours. The new model sells outcomes, and outcomes need fewer hands. Accenture's caution lands the same week India's domestic tech hiring hit a 28-month low and TCS confirmed deep cuts to its mid-level ranks.

There is a sharper edge for visa holders. When a firm's growth slows, the H-1B workforce is the most exposed: a layoff starts a 60-day clock to find a new sponsor or leave the country. Accenture is not announcing layoffs here, but a lowered forecast from the sector's bellwether tightens the entire job market that those workers depend on for a soft landing.

The optimistic read is that Accenture is reinventing faster than its Indian peers, pivoting into security and agentic AI before the bottom falls out of commodity coding. The pessimistic read is that even the best-positioned firm in the business can no longer convert AI hype into the kind of growth that hires people. For a diaspora built substantially on the global services economy, the difference between those two readings is not academic — it is the next decade.

What comes next is the July-August earnings run from TCS, Infosys, Wipro and Cognizant. If they echo Accenture's bookings weakness, the message will be unmistakable: the conveyor belt that carried a generation of Indian engineers to America is not broken, but it is slowing — and it will demand different skills from whoever wants to ride it next."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "An American Manufacturer Is Teaming With Adani to Build India's AI Backbone. The Diaspora Should Watch Where the Racks Get Made.",
        "subheadline": "Jabil and the Adani Group plan a vertically integrated factory for AI data-center hardware in India — racks, cooling, power — chasing a market they peg at over $3 trillion. It is the unglamorous half of the AI boom, and India wants it.",
        "slug": make_slug("jabil-adani-ai-data-center-manufacturing-india-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "For NRIs weighing whether India can move up the AI value chain beyond software services, a US-India factory making the physical hardware of data centers is the most concrete test yet of the 'build it at home' thesis.",
        "tags": ["adani", "data-centers", "ai-infrastructure", "make-in-india", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/jabil-bets-big-on-indias-ai-infrastructure-push"},
            {"name": "Jabil / Adani Group announcement", "url": "https://www.jabil.com/news.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/37730211/pexels-photo-37730211.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Server racks lit blue inside a modern data center",
        "image_attribution": "Pexels",
        "body": """The glamorous half of the AI boom is the models — the Geminis and GPTs that make headlines. The unglamorous half is the physical plant: the steel racks, the liquid-cooling loops, the power-distribution units and the miles of cabling that turn a building into a brain. That second half is suddenly where India wants to plant a flag, and a new partnership shows how.

Jabil, the Florida-based contract manufacturer, has formed a strategic collaboration with the Adani Group to build what the companies call a "vertically integrated" AI and data-center hardware platform in India. The plan: manufacture AI server racks and the supporting infrastructure — GPU servers, networking switches, storage, power distribution, liquid cooling, cabling and management hardware — domestically, for the hyperscalers racing to deploy high-density AI workloads. Jabil frames the addressable opportunity at more than $3 trillion over seven years.

The logic of the pairing is tidy. Jabil brings the engineering discipline and hyperscale-manufacturing know-how; Adani brings land, logistics, green-energy assets and a fast-growing data-center business. The combination is meant to make India a credible place to *build* the guts of an AI data center rather than merely host one.

### Why this is a different story than "India writes code"

For three decades, India's tech identity has been software and services — the back office of the world. The criticism, voiced even by India's own commentators this month, is that the country never built a deep hardware or R&D culture to match. A factory stamping out AI racks does not, by itself, change that. But it is a meaningful step up the physical value chain, the same chain that runs from chip fabs (Tata in Dholera, Micron in Gujarat) through assembly and packaging to the finished, rack-scale systems Jabil and Adani are targeting.

For NRI investors, this is where the story gets practical. The diaspora has spent two years asking a recurring question: is India's AI moment real, or is it a slide deck? Hardware manufacturing is harder to fake than a funding announcement. Racks either ship or they don't; hyperscalers either qualify a supplier or they walk. A working Jabil-Adani line, qualified by an Amazon or a Microsoft, would be tangible proof that "Make in India" can reach the most demanding tier of global tech procurement.

### The Adani factor

There is a complication NRIs will recognize: the partner is Adani. The conglomerate carries governance baggage from past short-seller allegations and remains a polarizing name in diaspora WhatsApp groups and investment circles. An American manufacturer choosing Adani as its India anchor is a vote of confidence in the group's execution muscle on infrastructure — but also a reminder that India's biggest industrial bets still flow through a handful of family conglomerates. For a diaspora investor deciding whether to buy into the India AI-infrastructure theme, the counterparty risk is part of the calculation, not a footnote.

The broader context is a global scramble for data-center capacity that is straining power grids and supply chains from Virginia to Mumbai. Hyperscalers are deploying thousands of high-density racks; every one needs cooling, power and assembly that someone, somewhere, has to manufacture. India's pitch is that it can be that someone — close to a booming domestic cloud market, backed by cheap renewable power, and staffed by exactly the kind of engineers the diaspora is full of.

### What to watch

Three things will tell NRIs whether this is substance or signaling. First, a named hyperscaler customer — Jabil's racks are only as valuable as the cloud giants willing to qualify them. Second, a real location and timeline; vertically integrated factories are announced far more often than they are commissioned. Third, whether the work stays high-value (design, integration, testing) or settles into low-margin assembly that any country could do.

If it clears those bars, the Jabil-Adani plant becomes a small but real piece of evidence that India is climbing from the software floor toward the hardware ceiling of the AI economy. For a diaspora that has long exported its engineers to build other countries' technology, a factory at home making the physical spine of the AI era is a homecoming of a different kind — and, potentially, an investment thesis with steel behind it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "DeepSeek Just Raised $7.4 Billion to Stay Chinese. India's AI Startups Are Watching the Playbook Closely.",
        "subheadline": "The lab that rattled Silicon Valley took outside money for the first time — through a structure designed so its founder never loses control. For India's sovereign-AI push and the diaspora that funds it, it is a lesson in how to scale without selling out.",
        "slug": make_slug("deepseek-7-4-billion-funding-founder-control-india-sovereign-ai-diaspora"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "DeepSeek's founder-control funding model is a template India's own AI champions — and the NRI investors backing them — are studying as they try to build sovereign AI without ceding control to foreign capital.",
        "tags": ["deepseek", "ai", "sovereign-ai", "india-ai", "nri-investors"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/tech/ai/deepseek-funding-round-valuation"},
            {"name": "Reuters", "url": "https://www.reuters.com/technology/chinas-deepseek-closes-funding-unusual-structure"},
            {"name": "Ventureburn", "url": "https://ventureburn.com/2026/06/deepseek-raises-7-4b/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17489163/pexels-photo-17489163.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern server unit in a blue-lit data center, representing AI compute infrastructure",
        "image_attribution": "Pexels",
        "body": """DeepSeek, the Hangzhou lab that humbled Silicon Valley last year with cheap, capable open-source models, has done the one thing it long swore it never would: take outside money. It raised more than $7.4 billion (50 billion yuan) in its first external round, vaulting its valuation past $50 billion and making it China's most valuable AI startup. The striking part is not the size of the check. It is the lengths the company went to so that the money would change as little as possible.

Founder Liang Wenfeng — who controlled nearly 90% of DeepSeek going in — put in about $3 billion of his own, the largest single contribution, drawn from the fortune of his quant hedge fund, High-Flyer. Most external backers, including Tencent (~$1.5 billion) and battery giant CATL (~$740 million), did not invest in DeepSeek directly. They put their capital into a limited partnership that Liang manages, accepting a five-year lock-up and no voting rights. Only China's state-backed National AI Fund got a direct stake with voting rights — and even it scaled its bet down to roughly $150 million.

In plain terms: investors handed over billions for economic exposure while surrendering any say in how the company is run. It is one of the largest private AI financings ever, structured so the founder keeps absolute control.

### Why a Chinese deal matters in Bengaluru

This is not just a China story, and for the Indian diaspora it lands at a pointed moment. India spent the past month consumed by the question of "sovereign AI" — building models, chips and data centers that the country owns and controls, after Washington moved to restrict foreign nationals' access to the most advanced American AI systems. The lesson Indian founders and policymakers took was blunt: technological dependence is a strategic vulnerability, no matter how friendly the relationship looks.

DeepSeek offers a parallel lesson on the *financing* side. India's emerging AI champions — Sarvam, which just sold a 10.5% stake to HCLTech at a $1.5 billion valuation; Krutrim, Ola's AI arm; the IIT-Bombay-backed BharatGen — all face the same tension. They need enormous capital to buy compute and train frontier models. But the deepest pools of that capital sit with US and Chinese giants whose interests may not align with India's sovereign ambitions. Take too much foreign money on standard terms, and a "sovereign" AI champion can quietly become a subsidiary of someone else's strategy.

Liang's structure is a possible answer: raise the billions, ring-fence control. India's founders, and the NRI investors who increasingly back them, are studying exactly this kind of arrangement.

### The diaspora's dual role

Here the diaspora occupies an unusually powerful seat. Indian-origin investors and operators sit on both sides of the table — as limited partners in the venture funds writing checks into Indian AI, and as the engineers and executives building the models themselves. The DeepSeek deal is a live case study in a question they will face directly: how do you fund a national champion at the scale frontier AI demands without handing the steering wheel to whoever brings the most cash?

There is a cautionary note, too. DeepSeek's founder-control model concentrates enormous power in one person and leans heavily on state-aligned capital — a structure that fits China's system but sits awkwardly with the open, foreign-investment-friendly model India has spent decades cultivating to attract exactly the diaspora dollars now in play. Copying the control mechanism without China's state backstop is harder than it looks.

### What to watch

DeepSeek's next move is its agent-focused V4 model, which the company claims redefined the state of the art for open-source systems even as third-party evaluations suggest it still trails the best models from US and Chinese rivals. The capital is earmarked for compute — the single biggest constraint on any frontier lab, in Hangzhou or Hyderabad.

For India, the takeaway is not to mimic DeepSeek's politics but to absorb its discipline: scale demands capital, capital demands structure, and structure decides who actually controls the technology a nation calls its own. The diaspora helped build the AI labs of America. The open question is whether it will help India build one it gets to keep."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"ERR {art['slug']}: {e}")

print(f"\n{len(inserted)} of {len(articles)} inserted")
for h in inserted:
    print(" -", h)
