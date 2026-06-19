#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
for cand in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.supabase"]:
    if cand.exists():
        for line in cand.read_text().strip().splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
        break

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
        "headline": "Trump Says Apple Will Build Chips With Intel. The Fine Print Is Thinner Than the Headline.",
        "subheadline": "A Truth Social post sent Intel's stock to a record and revived the dream of American-made silicon. For the Indian engineers who design Apple's chips, the question is what \"made in America\" actually changes.",
        "slug": make_slug("apple-intel-foundry-deal-trump-tsmc-indian-chip-engineers"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Indian-origin engineers fill Apple's silicon teams and Intel's foundry ranks, so a US chip-reshoring push reshapes the career map for the diaspora working at the heart of America's semiconductor revival.",
        "tags": ["semiconductors", "apple", "intel", "indian-tech", "silicon-valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN", "url": "https://www.cnn.com/2026/06/18/tech/apple-intel-chips-trump"},
            {"name": "MarketWatch", "url": "https://www.marketwatch.com/story/intels-stock-jumps-even-as-analysts-say-new-apple-chip-deal-might-start-small"},
            {"name": "Reuters", "url": "https://www.reuters.com/markets/us/wall-st-indexes-advance-with-boost-chips-iran-optimism-2026-06-18/"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/apple-intel-collaborate-us-chips-trump-truth-social"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31665489/pexels-photo-31665489.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "Close-up of a computer processor, the kind of advanced silicon at the center of the Apple-Intel manufacturing talks",
        "image_attribution": "Pexels",
        "body": """President Donald Trump announced one of the most consequential deals in American chipmaking the way he announces most things these days: in a Truth Social post, in the early hours, in capital letters. "Apple has agreed to work with Intel to design and build its Chips in America," he wrote on Thursday. Intel's stock ripped as much as 11% to a record high. The Philadelphia semiconductor index outran the rest of the market. And for a few hours, the story of US technology was the story of bringing it all back home.

Then the analysts started reading the fine print, and there wasn't much of it.

Neither Apple nor Intel confirmed the arrangement. Industry reporting suggests the talks are real but early-stage and narrow — closer to Intel manufacturing *some* chips for Apple than to the deep, multi-year design partnership Apple has with Taiwan's TSMC, which still makes the overwhelming majority of the advanced processors inside every iPhone, iPad and Mac. "Intel is gaining real traction with tier-one customers," Tigress Financial analyst Ivan Feinseth told MarketWatch — while adding that the agreement remains "preliminary and narrowly defined."

### Why the timing matters

The announcement landed the same week Apple chief executive Tim Cook told the Wall Street Journal that price increases on Apple products are now "unavoidable," blaming the soaring cost of memory and storage chips driven by the AI boom. So in the space of a few days, Apple has signaled both that hardware is getting more expensive and that it is being nudged toward a US foundry whose advanced 18A process is only now entering production. Trump framed it as industrial triumph, noting the government's 10% stake in Intel — bought when the company was worth roughly $100 billion — is now worth over $60 billion. "When was the last time a President made America money?" he wrote.

The strategic logic is sound even if the deal is thin. Washington has spent two years steering its biggest chip buyers — Apple, Nvidia, and Elon Musk's chip projects — toward Intel's fabs to manufacture a credible domestic alternative to TSMC. Apple's name on that list, even tentatively, is the strongest endorsement Intel Foundry has received.

### The diaspora's stake

For the Indian diaspora, this is not abstract. The teams that design Apple's silicon in Cupertino are thick with Indian-origin engineers; the chip-design and manufacturing-engineering ranks at Intel are some of the most South-Asian-heavy in the Valley. A structural shift toward US-based advanced manufacturing reshapes where those careers go next — toward fabs in Arizona and Ohio rather than design coordination with Taiwan, and toward process and packaging engineering, which America has spent decades offshoring.

There is a sharper edge, too. Building advanced chips in America requires thousands of process engineers the US does not currently produce in sufficient numbers — exactly the kind of specialized talent that has historically arrived on H-1B and O-1 visas, disproportionately from India. A genuine reshoring of leading-edge manufacturing would intensify demand for precisely the workers whose visa pathways have become a political football. The diaspora could find itself both the beneficiary of a chip boom and the target of the backlash against the immigration that makes it possible.

### What to watch

The tell will be specifics. Watch for which chip — a leading-edge iPhone processor would be a genuine coup for Intel's 18A; a peripheral component would confirm the skeptics. Watch Apple's own statements, conspicuously absent so far. And watch whether the relationship deepens into design collaboration or stays a manufacturing handoff, because the difference determines whether Indian engineers in Cupertino end up working *with* Intel or merely sending it files.

For an NRI tracking the semiconductor trade — as an Apple shareholder, an Intel employee, or an engineer weighing the next move — the lesson of Thursday is an old one. A presidential post can move a stock 11% before breakfast. Whether it moves a single wafer is a question for the quarters ahead."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Chip Dream Has a Quieter Second Act: Packaging the World's Silicon",
        "subheadline": "While the headlines chase Tata's $11 billion fab, a Bengaluru company is selling India as the back-end of the global chip industry — and Japan is buying. It may be the more realistic bet.",
        "slug": make_slug("india-osat-chip-packaging-kaynes-japan-assam-corridor-nri"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Semiconductor packaging and test is the layer of India's chip ambition most likely to create jobs and exports first, giving diaspora professionals in the field a credible reason to weigh a move home or an investment in the sector.",
        "tags": ["semiconductors", "india-semiconductor-mission", "osat", "kaynes", "indian-tech"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "DIGITIMES", "url": "https://www.digitimes.com/news/a20260617-kaynes-japan-chip-packaging.html"},
            {"name": "EE Times", "url": "https://www.eetimes.com/indias-kaynes-semicon-fast-tracks-power-packaging-ambitions/"},
            {"name": "Evertiq", "url": "https://evertiq.com/news/kaynes-partners-with-mitsui-aoi-to-boost-chip-manufacturing"},
            {"name": "Nikkei via DIGITIMES", "url": "https://www.digitimes.com/news/a20260618-japan-india-assam-chip-corridor.html"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/28215391/pexels-photo-28215391.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A patterned silicon wafer, the raw output that semiconductor assembly and test firms cut, package and verify into finished chips",
        "image_attribution": "Pexels",
        "body": """Every story about India's semiconductor ambition opens with the same picture: Tata Electronics' $11 billion wafer fab rising out of Dholera, Gujarat, with ASML lithography machines on the way and first chips promised by December. It is the photogenic part of the dream — the front-end, where blank silicon becomes a circuit. But the front-end is also the hardest, most capital-hungry, slowest-to-pay-off corner of the business. The quieter story this month is about the back-end, and it may be where India actually wins first.

This week, Bengaluru-based Kaynes Technology said it is chasing outsourced automotive semiconductor orders in Japan — pitching India as an alternative hub for the packaging and testing that turns finished wafers into usable chips. Japanese partners are backing the push. It is a modest-sounding move with an outsized implication: India breaking into a market long monopolized by East Asia, at the layer of the industry that hires the most people fastest.

### What "OSAT" actually means

The acronym is OSAT — outsourced semiconductor assembly and test. It is the unglamorous final mile: dicing wafers, bonding them into packages, wiring them up, and verifying they work. It is less capital-intensive than fabrication, ramps faster, and is exactly where the global supply chain is most desperate to reduce its dependence on a handful of Taiwanese and Chinese players.

Kaynes' subsidiary, Kaynes Semicon, has been assembling this capability piece by piece. It signed a fiscal-support agreement under the India Semiconductor Mission. It acquired packaging lines from Japan's Fujitsu, relocating equipment to its plant in Sanand, Gujarat using a "copy-exact" approach to replicate proven processes. It struck partnerships with Japan's AOI Electronics and trading giant Mitsui for backend technology and the specialty materials — lead frames, molding compounds, specialty gases — that the process consumes. The company aims to be the first in India to ship commercially packaged chips, starting with power semiconductors for electric vehicles, satellites and consumer electronics.

### Japan is the unlock

The geopolitics are doing the heavy lifting. Japanese Prime Minister Sanae Takaichi is set to visit India's Assam state in early July to discuss a chip and infrastructure corridor, according to Nikkei — a sign Tokyo sees India not just as a market but as a manufacturing partner to de-risk away from China. For a Japanese auto-chip buyer nervous about concentration in one geography, an Indian packaging house backed by Japanese technology and trading relationships is an attractive hedge.

### Why the diaspora should care

For Indians abroad working in semiconductors — and there are tens of thousands, in design, process and test roles across Silicon Valley, Austin and beyond — the back-end story is the more honest invitation home. A leading-edge fab in Dholera will, for years, depend heavily on imported expertise and foreign technology transfer. Packaging and test is different: it scales in months, hires in the hundreds per line, and rewards exactly the manufacturing-engineering and quality discipline that diaspora professionals have spent careers accumulating at firms like Intel, Micron and Texas Instruments.

It is also where the jobs land first. India's broader tech hiring just hit a 28-month low, and the IT-services conveyor belt that built the diaspora is jamming as AI eats entry-level coding work. A hardware layer that needs technicians, process engineers and test specialists offers a different kind of career — one harder for software automation to hollow out.

### The realistic read

None of this makes India a chip superpower overnight. Packaging is lower-margin than fabrication, and competing with established players in Taiwan, Malaysia and Vietnam means winning on cost, reliability and the patience of customers willing to qualify a new supplier. Kaynes' Japan pitch is a foot in the door, not a market share.

But it is a more grounded bet than the fab headlines suggest. India does not have to build the most advanced silicon in the world to matter to the supply chain. It can start by being the place that packages it — and for a diaspora professional weighing whether the India chip story is real, the back-end is the part you can touch today."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron Reports Earnings Tuesday With Its Stock Up 245%. An Indian-American CEO Is Riding the AI Memory Boom.",
        "subheadline": "Sanjay Mehrotra's company has sold out its entire 2026 supply of the memory chips that feed AI. For NRI investors, the rally is intoxicating — and the warning signs are flashing.",
        "slug": make_slug("micron-earnings-sanjay-mehrotra-hbm-ai-memory-nri-investors"),
        "category": "technology",
        "vertical": "tech",
        "diaspora_angle": "Micron is led by an Indian-American CEO, is building a major plant in Gujarat, and has become one of the most widely held AI plays among NRI investors — making its earnings a personal event for the diaspora's portfolios.",
        "tags": ["semiconductors", "micron", "ai", "indian-tech", "markets"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Zacks", "url": "https://www.zacks.com/stock/news/micron-nvidia-upside-2026-06-10"},
            {"name": "MarketBeat", "url": "https://www.marketbeat.com/stocks/NASDAQ/MU/earnings/"},
            {"name": "CoinCentral", "url": "https://coincentral.com/micron-mu-stock-all-time-high-analysts/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "image_caption": "Sanjay Mehrotra, the Indian-American chief executive of Micron Technology",
        "image_attribution": "Wikimedia Commons",
        "body": """When Micron Technology reports fiscal third-quarter earnings on Tuesday, June 24, it will do so as one of the most improbable stories on Wall Street: a memory-chip maker, member of an industry famous for brutal boom-and-bust cycles, whose stock has climbed roughly 245% in 2026. The man at the top is Sanjay Mehrotra — born in Kanpur, educated at Berkeley, co-founder of SanDisk, and one of the Indian-American chief executives whose presence in the corner office has become a point of diaspora pride.

This quarter, that pride comes with a portfolio attached.

### The setup

The catalyst is straightforward. The AI boom runs on high-bandwidth memory, or HBM — the stacked, ultra-fast memory that sits beside every AI accelerator from Nvidia and AMD. Micron is one of only three companies on earth that can make it at scale, and it has reportedly sold out its *entire* 2026 HBM supply under long-term contracts. It has been approved to supply next-generation HBM4 to Nvidia. That kind of forward visibility is rare in memory, and Wall Street has responded with something close to euphoria: TD Cowen more than doubled its price target to $1,500; multiple firms now rate the stock a strong buy. The shares touched an all-time high above $1,130 this week.

Analysts expect fiscal Q3 earnings of roughly $20 per share — a near-tenfold jump from a year ago. The previous quarter already blew past estimates, with revenue up 196% year-over-year to $23.86 billion.

### Why it is personal for NRIs

Three reasons the diaspora is watching this one more closely than a typical chip earnings call.

First, the man. Mehrotra is among the cohort of Indian-origin CEOs — alongside Sundar Pichai, Satya Nadella, Arvind Krishna and Nikesh Arora — who have made "Indian runs the company" a recurring headline. His success is read at home and in the diaspora as a marker of how far Indian talent has climbed in American technology.

Second, the India link. Micron is building a $2.75 billion assembly-and-test facility in Sanand, Gujarat — its single largest commitment to India and an anchor of the country's semiconductor mission. The same company powering the global AI memory boom is also one of the most concrete foreign investments in India's own chip ambitions, which makes its fortunes a two-way bet for NRIs with one eye on Silicon Valley and one on Gujarat.

Third, the holdings. Micron has quietly become one of the most popular individual stocks in NRI brokerage accounts — a clean, liquid way to own the AI infrastructure trade without picking a single AI model winner. A 245% year means a lot of diaspora investors are sitting on large, and largely unrealized, gains.

### The warning signs

Which is exactly when caution is hardest and most necessary. The same reports cheering Micron's run are flagging that the stock is extended. The average analyst price target sits *below* the recent close — implying the shares have run ahead of even bullish fundamentals. Memory is a cyclical business; the bigger the up-cycle, the harder the eventual down-cycle. Options traders are pricing in a large swing around Tuesday's print, meaning a strong report that merely meets sky-high expectations could still send the stock lower.

The honest framing for an NRI investor is this: Micron's business is genuinely excellent right now, and its stock has priced in a great deal of that excellence already. Sold-out HBM and HBM4 approval are real, durable advantages. But a 245% rally leaves little room for disappointment, and "buy the rumor, sell the news" has humbled better stories than this one.

### What to watch Tuesday

Guidance, not the headline number. The market already knows this quarter was strong; what it wants is Mehrotra's read on HBM pricing into 2027, on whether the supply-demand imbalance holds, and on capital spending. If the guidance confirms the rally, the believers get their validation. If it merely meets expectations, a stock priced for perfection may remind the diaspora's newest chip investors what the word "cyclical" actually means."""
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

print(f"\n{len(inserted)} of {len(articles)} inserted.")
for h in inserted:
    print(" -", h)
