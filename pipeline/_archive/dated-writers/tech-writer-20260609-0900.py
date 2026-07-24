#!/usr/bin/env python3
"""Videshi Technology Writer — 2026-06-09 09:00 UTC batch"""

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


# ─── ARTICLE 1 ───────────────────────────────────────────────────────
art1_body = """Sundar Pichai's Alphabet just wrote one of the strangest cheques in corporate history: $920 million a month to rent 110,000 NVIDIA GPUs from Elon Musk's SpaceX.

The deal, disclosed in a SpaceX SEC filing on June 5 ahead of the company's planned June 12 IPO, will run from October 2026 through June 2029. Payments begin at a reduced rate during a ramp-up period this summer before hitting the full monthly fee in October. If SpaceX fails to deliver the promised GPU capacity by September 30, Google can walk away entirely or accept fewer chips at a pro-rata discount.

Google Cloud described the arrangement as a "short-term, timely agreement to ensure we have bridge capacity to meet surging customer demand for our agent platform, Gemini Enterprise, which has been even higher than we expected."

## Musk's Data Centres Were Built for Grok

The infrastructure SpaceX is renting out sits in its Colossus data centres — facilities originally built to train Grok, the AI model behind Musk's xAI. With excess capacity now available, SpaceX has found a lucrative side business: leasing compute to the very companies it competes with.

Google is not the first tenant. In May, Anthropic committed to a separate $1.25 billion-per-month deal for full access to SpaceX's Colossus 1 facility in Memphis, Tennessee, which houses more than 220,000 NVIDIA processors. Together, the Google and Anthropic contracts are expected to generate approximately $26 billion annually for SpaceX — a staggering revenue line for a company still better known for rockets than racks.

x-official:https://x.com/sundarpichai/status/2062203848673161267

## A $1.77 Trillion Debut

The timing is no coincidence. SpaceX has filed to raise $75 billion by selling 555.6 million shares at $135 each, which would value the company at nearly $1.77 trillion — making it the largest IPO in history. Goldman Sachs, Morgan Stanley, and JPMorgan Chase are leading the offering.

SpaceX has also pitched investors on plans to build data centres in space, a nascent technology gaining traction as terrestrial facilities face spiralling energy costs. Google, separately, is working on orbital data centres under a project called Suncatcher, aiming for a 2027 launch using satellites built with Planet Labs.

## Why NRIs Should Watch

For Indian Americans in tech, this deal is a study in the economics of AI infrastructure. Pichai — born in Chennai, educated at IIT Kharagpur — now runs a company that is spending so aggressively on AI compute that it cannot build fast enough and must rent from a rival.

The SpaceX IPO is attracting significant global liquidity: Alpha AMC founder Rajesh Singla noted that the offering, along with capital market activity around leading AI companies, is driving "temporary capital rotation away from emerging markets, including India." For NRI investors deciding between the SpaceX IPO and Indian equities, the contrast is stark — one market is building the AI future, the other is still waiting for its first commercial chip to roll off the line.

Google executive Donald Harrison sits on the SpaceX board, and Alphabet was an early SpaceX investor. The relationship between the two companies is collaborative as much as competitive — a dynamic that is likely to define the AI infrastructure market for years to come."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sundar Pichai Is Paying Elon Musk $920 Million a Month to Rent GPUs. That's the AI Economy Now.",
    "subheadline": "Google's Alphabet signs a $920M monthly deal with SpaceX for 110,000 NVIDIA GPUs, just days before SpaceX's record-breaking $1.77 trillion IPO.",
    "slug": make_slug("google-spacex-920m-gpu-deal-pichai-musk-ipo"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Sundar Pichai, born in Chennai and educated at IIT Kharagpur, is at the helm of the company signing one of the largest compute rental deals in history. For NRI investors, the SpaceX IPO is pulling global capital away from Indian markets — forcing a portfolio decision between the AI infrastructure buildout and emerging-market exposure.",
    "tags": ["ai-infrastructure", "sundar-pichai", "spacex-ipo", "google-cloud", "nvidia-gpu", "nri-investing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/spacex-lands-google-ai-compute-deal-after-anthropic-pact-ahead-ipo-2026-06-06/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/business/google-to-pay-spacex-nearly-1-billion-a-month-in-cloud-computing-deal"},
        {"name": "Motley Fool", "url": "https://www.fool.com/investing/2026/06/08/did-anthropic-google-give-investors-reasons-spacex-ipo/"},
        {"name": "Verdict", "url": "https://www.verdict.co.uk/spacex-signs-920m-monthly-cloud-deal-with-google-ahead-of-ipo/"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Sundar_Pichai_-_2023_%28cropped%29.jpg",
    "image_caption": "Sundar Pichai, CEO of Alphabet and Google, whose company signed the $920M monthly GPU deal with SpaceX",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body
}

# ─── ARTICLE 2 ───────────────────────────────────────────────────────
art2_body = """On Friday, June 5, the semiconductor sector suffered its worst single-day rout since the early weeks of the Covid-19 pandemic. The PHLX chip index plunged 10.3%, erasing $1.3 trillion in market value in a single session. By Monday afternoon, the bounce was already under way — but for the millions of Indian Americans with portfolios heavily weighted toward chip stocks, the whiplash carried lessons that won't fade with the rebound.

## What Triggered the Crash

The proximate cause was Broadcom. Its quarterly report showed demand for custom AI chips falling short of lofty expectations, and guidance for $16 billion in Q3 AI-chip revenue came in a hair below consensus. That was enough to shatter the thesis that AI chipmakers could do no wrong.

Then came the May jobs report: stronger than expected, with the economy adding well above forecast. Traders immediately repriced interest-rate expectations, pushing the probability of at least one rate increase this year to roughly 70% on the CME FedWatch tool. Higher rates are kryptonite for richly valued growth stocks — and few sectors had been priced more richly than semiconductors, which had already rallied 75% year-to-date before Friday's collapse.

The carnage was concentrated but severe. NVIDIA, the world's most valuable chipmaker, lost roughly 6% — cleaving more than $300 billion from its market capitalisation. Micron Technology, led by Indian-American CEO Sanjay Mehrotra, tumbled 13%, erasing approximately $150 billion. Marvell Technology gave back 17%. AMD shed nearly 11%.

## The Monday Rebound

By Monday, bargain hunters were back. The catalyst: a report from The Information that Google had placed an order with Intel to manufacture more than 3 million tensor processing units for 2028 production, with NVIDIA also evaluating Intel as a backup manufacturer.

x-official:https://x.com/intel/status/2063999492425134329

Intel surged 11.19%, closing at $110.27. AMD recovered 5.14%. NVIDIA clawed back 1.73%. The S&P 500 technology sector and the SOX index both advanced, helping stabilise broader market sentiment.

"Today looks like a day where investors are doing a little bit of bargain hunting off the big tech selloff," said Rick Meckler, partner at Cherry Lane Investments. "What normally happens after that is you get analysts coming in and reiterating buys."

## What NRI Investors Should Know

The June 5-8 swing matters disproportionately for Indian Americans. Industry surveys consistently show that Indian-origin tech professionals in the US hold outsized positions in semiconductor and AI-adjacent stocks — often through employer equity in companies like NVIDIA, Intel, Qualcomm, and Micron, as well as through concentrated bets in ETFs like SMH and SOXX.

The VanEck Semiconductor ETF (SMH) lost 9.2% on Friday alone; by Monday's close, it had recovered roughly 5%. That kind of round-trip is manageable for diversified portfolios, but it can be devastating for employees whose net worth is tied to a single chip stock.

The other factor NRI investors should watch is the Federal Reserve. New Chair Kevin Warsh's first policy meeting runs June 16-17 — and with strong employment data undermining the case for cuts, the direction of rates will determine whether the AI trade resumes its march or enters a longer consolidation. President Trump has repeatedly pushed for lower rates, but the data is now pushing back.

The Philadelphia Semiconductor Index remains up more than 70% for 2026 even after Friday's rout. That is not a bubble popping. It is a market reminding participants that even the best trades carry risk — and that the Indian tech professionals most exposed to these names should be thinking about concentration, hedging, and the distinction between conviction and complacency."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "A $1.3 Trillion Chip Rout, Then a Monday Bounce. NRI Portfolios Felt Every Dollar.",
    "subheadline": "The worst semiconductor selloff since 2020 erased $1.3 trillion in market value, hitting Indian-led companies hardest. Monday's Intel-fuelled rebound helped — but the deeper risk remains.",
    "slug": make_slug("chip-selloff-1-trillion-rebound-nri-investors"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "Indian Americans hold outsized positions in semiconductor stocks through employer equity and concentrated ETF bets. The June 5 rout hit Indian-led companies like Micron (Sanjay Mehrotra) and Marvell hardest. NRI tech professionals with wealth tied to single chip stocks face concentration risk that this episode exposed.",
    "tags": ["semiconductor", "chip-selloff", "nvidia", "micron", "intel", "nri-investing", "federal-reserve"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/technology/chip-selloff-erases-over-1-trillion-stock-market-value-2026-06-06/"},
        {"name": "Reuters", "url": "https://www.reuters.com/business/sp-500-nasdaq-end-up-tech-chipmakers-rebound-2026-06-09/"},
        {"name": "Zacks", "url": "https://www.zacks.com/stock/news/2475641/a-few-reasons-to-buy-the-dip-in-ai-chip-etfs"},
        {"name": "Barron's", "url": "https://www.barrons.com/articles/stock-market-interest-rates-solar-ai-d05aeb4b"},
        {"name": "TBS News", "url": "https://www.tbsnews.net/economy/stocks/chip-slump-erases-13t-stock-market-value-1078341"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/6755078/pexels-photo-6755078.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Semiconductor chips on a circuit board — the sector lost $1.3 trillion in a single Friday session",
    "image_attribution": "Pexels",
    "body": art2_body
}

# ─── ARTICLE 3 ───────────────────────────────────────────────────────
art3_body = """India's stock market was once emerging Asia's undisputed champion. It is not any more.

In the space of a few weeks, both Taiwan and South Korea have overtaken India in global market capitalisation, pushing what was once the world's fifth-largest equity market to seventh. The reason is no mystery: those countries sit at the heart of the AI supply chain, and India does not.

## The Numbers Tell the Story

Foreign Portfolio Investors (FPIs) pulled ₹43,000 crore (roughly $4.5 billion) from Indian equities in the first week of June alone. That brings total outflows for 2026 to ₹2.67 lakh crore — approximately $26.4 billion — already surpassing the entire ₹1.66 lakh crore withdrawn in all of 2025, according to data from the National Securities Depository.

The exodus has been relentless. FPIs sold in January (₹35,962 crore), paused briefly in February (inflows of ₹22,615 crore, the highest in 17 months), then resumed selling with record ferocity: ₹1.17 lakh crore in March, ₹60,847 crore in April, ₹32,963 crore in May, and now ₹43,000 crore in early June.

India's share in the MSCI Global Standard index has shrunk from a peak of 21% in September 2024 to 12.3% today. Goldman Sachs, meanwhile, has upgraded both Taiwan and South Korea — home to TSMC, Samsung Electronics, and SK Hynix, the companies physically manufacturing the AI revolution.

## The AI Gap

The structural problem is simple: India has no equivalent of TSMC. No SK Hynix. No Samsung foundry. The India Semiconductor Mission has approved 12 projects, including facilities by Micron, Tata Electronics, and CG Power, but none have reached commercial production at scale. The first assembly and packaging plants are expected to go live in 2026-2027; actual chip fabrication is optimistically projected for 2028, with pessimists saying 2030.

Meanwhile, global capital is flowing toward companies that are not planning to build chips but are actually shipping them — right now, at scale, into the teeth of the AI boom.

"Apart from higher US yields and dollar strength, global investors are also reallocating capital towards some of the largest technology and AI-related public market opportunities currently emerging globally," noted Alpha AMC founder Rajesh Singla. He specifically pointed to the upcoming SpaceX IPO and capital market activity around leading AI companies as liquidity magnets.

## The Rupee Problem

The currency has compounded the pain. The rupee crossed Rs 95 per US dollar in early May 2026, hitting a historic low. The depreciation — driven by high import costs, declining foreign direct investment, and increased dollar demand from Indian corporates themselves — makes Indian equities even less attractive to foreign holders who book returns in dollars.

Indian conglomerates are increasingly redirecting capital to the United States, where deep consumer markets, AI leadership, and manufacturing incentives under the CHIPS Act are drawing global firms.

## A Picks-and-Shovels Play?

Not everyone is bearish. Abhay Laijawala, managing director and India chief investment officer at Lighthouse Canton, argues that India offers a "picks-and-shovels" opportunity in the AI era — through investments in electricity infrastructure, cooling systems, physical data centres, and the digital backbone that AI requires regardless of where the chips are made.

India's data centre capacity is expanding rapidly, driven by global hyperscalers and domestic players like Adani and Reliance. And the country's massive pool of AI and software talent — the same engineers powering Silicon Valley's AI labs — represents an enduring competitive advantage, even if it does not translate into market-cap weight the way a TSMC does.

## The NRI Dilemma

For Indian Americans with dual-market exposure, the numbers demand attention. An NRI with a typical India-US split portfolio has likely watched the India allocation shrink in value while US tech holdings surged — a divergence that raises uncomfortable questions about rebalancing, home-country bias, and where the next decade of returns will come from.

The answer may not be either-or. But India's absence from the AI hardware supply chain is no longer a future risk. It is a present one, measured in trillions of dollars of capital that has already moved elsewhere."""

art3 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Got Demoted. Taiwan and South Korea Stole Its Place in the Global AI Economy.",
    "subheadline": "Foreign investors have pulled $26.4 billion from Indian equities in 2026 — more than all of 2025. The reason: India has no TSMC, and the AI boom is not waiting.",
    "slug": make_slug("india-overtaken-taiwan-south-korea-ai-fpi-exodus"),
    "category": "technology",
    "vertical": "technology",
    "diaspora_angle": "NRI investors with dual India-US portfolios are watching the India allocation shrink while US tech surges. India's absence from the AI hardware supply chain — no TSMC, no SK Hynix — is driving a historic capital flight that directly affects diaspora wealth and the return-to-India investment thesis.",
    "tags": ["india-markets", "fpi-exodus", "semiconductor", "ai-economy", "taiwan", "south-korea", "nri-investing"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-file-india-overtaken-south-korea-taiwan-ride-ai-wave-2026-06-09/"},
        {"name": "Outlook Business", "url": "https://business.outlookindia.com/markets/fpi-exodus-deepens-foreign-investors-withdraw-more-in-five-months-than-entire-2025"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/markets/fpis-pull-out-43000-crore-in-first-week-of-jun-as-ai-trade-rupee-weakness-weigh-on-indian-equities/article69669213.ece"},
        {"name": "Ainvest", "url": "https://www.ainvest.com/news/fpis-withdraw-43000-crore-from-indian-equities-in-june-amid-global-ai-investments/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
    "image_caption": "The Bombay Stock Exchange building in Mumbai — India's equity market has fallen to seventh globally as AI-driven capital flows elsewhere",
    "image_attribution": "Wikimedia Commons",
    "body": art3_body
}


# ─── INSERT ───────────────────────────────────────────────────────────
articles = [art1, art2, art3]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nDone. {len(articles)} articles submitted for review.")
