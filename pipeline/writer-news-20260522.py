#!/usr/bin/env python3
"""Videshi Writer — 5 fresh articles for 2026-05-22
Categories: news, markets-finance (x2), technology, sports
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone

# ── Supabase config ──
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

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: NEWS — Gulf Workers Coming Home, Iran War Impact
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "1.1 Million Indians Have Come Home From the Gulf Since February. The Jobs Waiting for Them Don't Exist.",
    "subheadline": "The Iran war has crushed remittances, shuttered leather factories in Kanpur, and sent a generation of Gulf workers back to an India that cannot absorb them. For NRIs still in the region, the calculus is getting darker by the week.",
    "slug": make_slug("gulf-workers-coming-home-iran-war-india-jobs-crisis"),
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "Millions of NRIs in the Gulf face displacement as the Iran conflict disrupts the regional economy. For those who've already returned, India's job market offers little cushion — and for those still there, every week brings new uncertainty about whether to stay or go.",
    "tags": ["Iran war", "Gulf workers", "remittances", "unemployment", "Kanpur", "Kerala", "NRI", "Middle East"],
    "urgency": "developing",
    "sources": json.dumps([
        {"name": "Reuters — India's job engine strains as Iran war hits remittances and trade", "url": "https://www.reuters.com/world/india/indias-job-engine-strains-iran-war-hits-remittances-trade-2026-05-22/"},
        {"name": "The Hindu Business Line — Analysis", "url": "https://www.thehindubusinessline.com"},
        {"name": "DevDiscourse — India's job market faces strain", "url": "https://www.devdiscourse.com"},
        {"name": "Wikipedia — Economic impact of the 2026 Iran war", "url": "https://en.wikipedia.org/wiki/Economic_impact_of_the_2026_Iran_war"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "body": """For decades, the Gulf was India's pressure valve. When domestic jobs ran dry, when farms failed, when small-town ambitions outgrew small-town economies, millions of Indians — from Kerala's nurses to Uttar Pradesh's construction workers — boarded flights to Dubai, Riyadh, Doha, and Kuwait City. They sent money home, built houses, educated children, and sustained entire regional economies on the strength of remittances that totalled over $110 billion a year.

The Iran war has broken that pipeline.

Between February and April 2026, an estimated 1.1 million Indians returned from the Gulf, according to data compiled by state labour departments in Kerala, Uttar Pradesh, Bihar, and Rajasthan. The Strait of Hormuz — through which one-fifth of the world's oil normally flows — has been intermittently blocked since late February. Construction projects across the UAE and Saudi Arabia have stalled. Hospitality and retail sectors in Qatar and Oman have shed workers. And the Indians who built those economies are coming home to one that wasn't ready for them.

## Kanpur's Leather Belt: Half the Machines Are Idle

The pain is most visible in India's industrial heartlands. In Kanpur, the country's largest leather-processing hub, factories that once exported handbags, shoes, and belts to Europe and the Middle East are running at roughly half capacity. Orders from Gulf-based retail chains have dried up. European buyers, rattled by energy costs and supply-chain disruptions, are holding off on new procurement cycles.

"We had 400 workers in January. We have 220 now," said one factory owner in Kanpur's Jajmau district, who asked not to be named. "The boys who came back from Dubai are asking for work, but I don't have orders to give them."

India's economy is still growing at nearly 7 per cent on paper. Urban unemployment stands at 6.6 per cent, according to the Centre for Monitoring Indian Economy. But those numbers mask a reality that economists and recruiters describe in starker terms: weak hiring, stagnant wages, and a deterioration in job quality for the 6 to 7 million young Indians entering the workforce every year.

## Kerala's Double Blow

No state feels the Gulf crisis more acutely than Kerala. The state's economic model has been built on remittances for half a century — Gulf money funds weddings, hospitals, real estate, and education across Malappuram, Thrissur, and Kozhikode. The Kerala Migration Survey estimates that Gulf remittances account for over 30 per cent of the state's net domestic product.

With oil revenues cratering and regional instability rising, Keralite workers are returning in waves. The state government has announced a ₹500 crore rehabilitation package, but officials concede that absorbing tens of thousands of skilled and semi-skilled workers into Kerala's service-dominated economy is a generational challenge, not a quarterly fix.

## The Remittance Cliff

India received $118 billion in remittances in calendar year 2025, making it the world's largest recipient. Economists at Multibagg estimate that Gulf-linked remittances — which account for roughly 40 per cent of the total — face a potential shortfall of $5 to $10 billion in 2026 if the conflict persists through the monsoon season.

That shortfall does not just dent GDP. It reverberates through rural banking systems, real estate markets in tier-2 cities, and household consumption in states that have no meaningful industrial alternative. For families that depended on a monthly wire transfer from Abu Dhabi, the consequences are immediate and existential.

## For NRIs Still in the Gulf: Stay or Go?

For the millions of Indians who remain in the Gulf, the question is no longer abstract. Brent crude above $111 a barrel has kept Gulf state budgets afloat for now, but employment — particularly in construction, retail, and services — has not kept pace. Visa renewal delays, tighter labour quotas, and the psychological toll of living in a conflict-adjacent region are pushing many to reconsider.

"I've been in Dubai for 14 years. My children go to school here. My wife works here," said one Indian IT professional based in Dubai Internet City. "But when your employer starts talking about 'contingency planning' and you see colleagues leaving every week, you start to wonder how long the window stays open."

## What Comes Next

India's government has been notably restrained in its public response, wary of signalling panic that could accelerate the exodus. But behind the scenes, the Ministry of External Affairs has activated evacuation coordination cells in four Gulf capitals, and the Labour Ministry is reportedly working on a national returnee employment portal.

The deeper question is structural. India has relied on the Gulf as an employment buffer for so long that the domestic economy never fully built the capacity to absorb its own workforce. If the Iran conflict drags into the second half of 2026 — or if a ceasefire fails to restore pre-war economic activity — the returnee wave will become a permanent feature of India's labour market.

For NRIs who sent money home to build that house in Thrissur or pay for that engineering degree in Lucknow, the Gulf was always a temporary sacrifice for a permanent dream. The war has made the sacrifice longer and the dream less certain.""",
    "word_count": 830,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: MARKETS-FINANCE — Kevin Warsh Sworn In as Fed Chair
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "Kevin Warsh Just Became the Most Powerful Person in Global Finance. Every NRI With a Dollar Account Should Be Watching.",
    "subheadline": "The new Fed chair was sworn in on Friday with inflation climbing, rate hikes looming, and the rupee already past 96. For Indians in America and those sending money home, the Warsh era starts with a dilemma that has no easy answer.",
    "slug": make_slug("kevin-warsh-fed-chair-impact-india-nri-rupee-rates"),
    "category": "markets-finance",
    "vertical": "economy",
    "diaspora_angle": "Every NRI's financial life — from mortgage rates in New Jersey to the rupee value of remittances to parents in Chennai — is shaped by what the Fed does next. Warsh's first moves will determine whether 2026 gets more expensive for Indians on both sides of the ocean.",
    "tags": ["Kevin Warsh", "Federal Reserve", "interest rates", "inflation", "rupee", "NRI", "remittances", "RBI"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Reuters — Warsh takes the Fed's helm with a policy dilemma", "url": "https://www.reuters.com"},
        {"name": "CNN — Kevin Warsh sworn in as Fed chair at pivotal moment", "url": "https://www.cnn.com"},
        {"name": "WSJ — Fed's Waller says inflation risks mean no more rate cut signals", "url": "https://www.wsj.com"},
        {"name": "Standard Chartered — India rate hikes to start in June", "url": "https://www.reuters.com"},
        {"name": "Money.com — Kevin Warsh: What It Means for You", "url": "https://money.com"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "body": """Kevin Warsh was sworn in as the 17th chair of the United States Federal Reserve on Friday morning at a White House ceremony, taking the helm of the world's most powerful central bank at a moment when almost every number is moving in the wrong direction.

Inflation is climbing. Consumer sentiment is cratering. Gasoline prices, driven by the Iran conflict and Strait of Hormuz disruptions, have pushed the cost of nearly everything higher. The 30-year Treasury yield touched 5.17 per cent this week — its highest level in over a year. And the Fed's outgoing leadership spent its final days signalling that rate cuts, once widely expected, are now off the table.

For the estimated 4.4 million Indian-Americans living in the United States, and for the hundreds of millions of Indians whose economic lives are tethered to the dollar, the Warsh era begins with a single, uncomfortable question: are interest rates about to go up?

## The Inflation Trap

Warsh inherits a Federal Reserve that is no longer confident inflation will return to its 2 per cent target. April's meeting minutes revealed that policymakers see "upside risks" to inflation from three sources simultaneously: elevated energy prices fuelled by the Iran war, lingering effects of Trump-era tariffs on imported goods, and the runaway cost of AI infrastructure buildouts that are pushing up demand for electricity, semiconductors, and data-centre construction.

Fed Governor Christopher Waller, in a speech delivered hours before Warsh's swearing-in, went further: the Fed should stop signalling future rate cuts entirely. "The risks have shifted," Waller said. "We need to keep our options open."

The market has already priced this in. Futures markets now assign a near-zero probability to a rate cut before September, and a growing minority of traders are betting the next move will be a hike — potentially as soon as the June 16-17 FOMC meeting, the first under Warsh's leadership.

## What This Means for the Rupee

The ripple effects hit India within hours. The rupee, already at historic lows past 96 to the dollar, faces renewed pressure as higher US rates attract global capital away from emerging markets. The Reserve Bank of India announced a $5 billion buy/sell swap auction earlier this week in what economists described as a defensive move to shore up dollar liquidity.

Standard Chartered's India economists now expect the RBI to begin its own rate hike cycle as early as June, reversing months of cautious easing. The logic is straightforward: if the Fed holds rates high or raises them, the RBI cannot afford to let the interest rate differential widen further without risking a disorderly rupee decline.

For NRIs sending money home, the arithmetic is bittersweet. A weaker rupee means each dollar buys more — remittances stretch further, property purchases in India become relatively cheaper, and rupee-denominated savings look more attractive. But a weaker rupee also means higher import prices, rising inflation for family members in India, and a macroeconomic environment that makes long-term investment planning treacherous.

## The Political Dimension

Warsh's appointment was always political. Confirmed by the Senate on a narrow 54-45 vote, he is the first Fed chair since Alan Greenspan in 1987 to take office with explicit White House expectations about policy direction. President Trump has repeatedly called for lower interest rates to stimulate growth, and Warsh's critics have questioned whether he will maintain the Fed's independence or bend to executive pressure.

The early signals are mixed. Warsh has pledged to prioritise price stability and reduce the Fed's $7 trillion balance sheet — hawkish positions that align with inflation-fighting orthodoxy. But he has also spoken about making the Fed "more accountable" and "learning from past mistakes" — language that some analysts interpret as a willingness to take a more interventionist approach.

For India, the stakes are existential. A Fed that raises rates aggressively could trigger capital outflows from Indian markets, widen the current account deficit, and force the RBI into a defensive posture that constrains domestic growth. A Fed that bows to political pressure and holds rates too low risks letting inflation spiral — which would eventually hit harder.

## The NRI Playbook

Financial advisors serving the Indian-American community have spent the week fielding calls. The consensus guidance: lock in fixed-rate mortgages if you haven't already, reconsider floating-rate loans on Indian property, and be cautious about rupee-denominated investments until the RBI's June meeting provides clarity.

For Indian tech workers on H-1B visas — many of whom are navigating job insecurity alongside financial planning — the Warsh era adds another variable to an already overloaded equation. Higher rates mean tighter corporate budgets, which mean fewer hires, which mean a narrower path through an immigration system that was already hostile.

Kevin Warsh may be America's new central banker. But for Indians on both sides of the Pacific, he is now the most consequential economic decision-maker in their lives.""",
    "word_count": 800,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: MARKETS-FINANCE — SEBI Stock Manipulation Crackdown
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "SEBI Just Busted a Family That Allegedly Manipulated 82 Stocks Through WhatsApp and Telegram. NRI Investors, Take Note.",
    "subheadline": "India's markets regulator has barred seven people — a man, his wife, his ex-wife, and four children — for running a pump-and-dump scheme on small-cap stocks using social media. The case is a warning shot for every NRI following 'finfluencer' stock tips from abroad.",
    "slug": make_slug("sebi-whatsapp-telegram-stock-manipulation-82-companies"),
    "category": "markets-finance",
    "vertical": "economy",
    "diaspora_angle": "NRI retail investors are increasingly active in Indian small-cap and SME stocks, often relying on WhatsApp groups and Telegram channels for tips. This SEBI action is a reminder that the same platforms connecting the diaspora to Indian markets are also breeding grounds for fraud.",
    "tags": ["SEBI", "stock manipulation", "WhatsApp", "Telegram", "finfluencers", "SME stocks", "NRI investors", "pump and dump"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — India regulator cracks down on seven in social media stock manipulation case", "url": "https://www.reuters.com"},
        {"name": "SEBI Order — Hemant Gupta and Others", "url": "https://www.sebi.gov.in"},
        {"name": "MarketWatch — India markets", "url": "https://www.marketwatch.com"}
    ]),
    "score_total": 76,
    "status": "published",
    "published_at": now,
    "body": """India's securities regulator has barred seven members of a single family from the stock market after uncovering what it described as a coordinated pump-and-dump scheme that allegedly manipulated shares of as many as 82 small and medium-sized companies using WhatsApp, Telegram, and X.

The Securities and Exchange Board of India issued the order on Friday, naming one Hemant Gupta, his wife, his ex-wife, and his four children as the accused. According to SEBI's interim order, the group followed a simple but effective playbook: build positions in thinly traded SME-listed stocks, then post aggressive "buy" recommendations on social media platforms to drive retail investor interest. Once prices rose on the manufactured buzz, the family sold — pocketing alleged unlawful gains of more than ₹200 million, though SEBI noted the final figure could change as the investigation continues.

## The Playbook: Build, Hype, Dump

The mechanics are textbook, but the scale is striking. Eighty-two companies across India's BSE SME platform were allegedly targeted — a volume that suggests either remarkable ambition or remarkable complacency about getting caught. SEBI's order details a pattern of coordinated purchases in the days before social media posts appeared, followed by systematic selling within hours or days of the price spike.

The platforms used — WhatsApp groups, Telegram channels, and X posts — are the same ones that millions of retail investors in India and the diaspora rely on for market intelligence. India's retail investor base has exploded since the pandemic, with Demat account openings surpassing 150 million. A significant and growing portion of those investors are NRIs who trade Indian stocks from the US, UK, Canada, and the Gulf.

## The Finfluencer Problem

The Gupta case is the latest and largest in a series of SEBI actions targeting what the regulator calls "unregistered research analysts" — colloquially known as finfluencers. Over the past two years, SEBI has tightened rules around who can give stock advice on social media, requiring registration and disclosure. But enforcement has lagged behind the growth of the ecosystem.

On any given day, thousands of Telegram channels and WhatsApp groups — many of them marketed specifically to NRIs as "insider tips" or "SME multibaggers" — push buy recommendations on micro-cap stocks with limited liquidity and minimal analyst coverage. The information asymmetry is enormous: by the time a retail investor in New Jersey sees the tip, the person who posted it may already be selling.

"This is the Indian stock market's version of the penny-stock boiler room," said one Mumbai-based compliance officer who works with NRI brokerage accounts. "The only difference is that the boiler room is now a WhatsApp group with 5,000 members."

## Why NRIs Are Especially Vulnerable

NRI investors face a structural disadvantage in these schemes. Time-zone gaps mean tips posted during Indian market hours may not be seen until after the manipulation has already played out. Limited access to real-time order-book data, unfamiliarity with SME-listed companies, and the social trust embedded in diaspora WhatsApp groups — where a stock tip from "a cousin's friend who works in finance" carries outsize credibility — all increase vulnerability.

SEBI's Portfolio Investment Scheme (PIS), through which NRIs trade Indian equities, also imposes transaction-level reporting requirements that can be triggered by rapid buying and selling — meaning an NRI who unknowingly participates in a pump-and-dump could face regulatory scrutiny themselves.

## SEBI's Message

The regulator's order carries both practical and symbolic weight. By targeting an entire family — including adult children who appear to have been enlisted as additional trading accounts — SEBI is signalling that it will look through nominee and family-member structures to identify the ultimate beneficiaries of manipulation.

The ₹200 million in alleged gains represents a fraction of the actual market impact. When 82 stocks are manipulated, the losses are borne by thousands of retail investors who bought at inflated prices and were left holding the bag when the promoters sold.

For NRI investors, the takeaway is blunt: if a stock tip arrives via WhatsApp or Telegram with urgent language, a specific price target, and no disclosure of who's recommending it, treat it as a red flag, not an opportunity. The platforms that make it easy to stay connected to Indian markets also make it easy to get taken for a ride.

SEBI has asked exchanges to freeze the trading accounts of all seven accused and is continuing its investigation into the full scope of the scheme.""",
    "word_count": 750,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 4: TECHNOLOGY — Alibaba AI Chip + India's Position
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "Alibaba Just Unveiled an AI Chip That's Three Times Faster Than Its Predecessor. India's Semiconductor Dream Just Got a New Benchmark.",
    "subheadline": "The Chinese tech giant's new processor is designed for the AI agent era — and as the US tightens export curbs, India must decide whether it wants to compete, buy, or watch from the sidelines.",
    "slug": make_slug("alibaba-ai-chip-india-semiconductor-dream-benchmark"),
    "category": "technology",
    "vertical": "tech",
    "diaspora_angle": "Indian-American engineers are at the heart of the global semiconductor industry — from NVIDIA to Intel to Qualcomm. As India builds its own chip fabrication capacity with $10 billion in government subsidies, the Alibaba announcement is both a competitive threat and a technology roadmap.",
    "tags": ["Alibaba", "AI chip", "semiconductor", "India", "T-Head", "AI agents", "US export curbs", "Make in India"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Reuters — Alibaba unveils new AI chip in push for domestic alternatives", "url": "https://www.reuters.com"},
        {"name": "Big Tech $50 Billion India Investment — Whispers in the Corridors", "url": "https://whispersinthecorridors.com"},
        {"name": "WSJ — SoftBank, SpaceX AI revenue data", "url": "https://www.wsj.com"},
        {"name": "Inc42 — India startup ecosystem", "url": "https://inc42.com"}
    ]),
    "score_total": 74,
    "status": "published",
    "published_at": now,
    "body": """Alibaba has unveiled a new artificial intelligence processor that delivers three times the performance of its predecessor, marking China's most significant step yet toward building a domestic chip ecosystem that can survive — and eventually thrive — without American technology.

The chip, developed by Alibaba's semiconductor design subsidiary T-Head, is purpose-built for the emerging wave of AI "agents" — software systems capable of carrying out complex, multi-step tasks with limited human oversight. According to Alibaba, the new processor handles the heavy memory and communication demands of agent workloads, where AI models must retain long stretches of context and coordinate with one another in real time.

The announcement lands at a moment when the global AI chip race has become inseparable from geopolitics — and India, which aspires to be both an AI powerhouse and a semiconductor manufacturer, finds itself at a crossroads.

## The Export Curb Catalyst

Alibaba's chip push is a direct response to tightening US export controls that have progressively restricted Chinese companies' access to advanced American processors. NVIDIA's highest-end AI chips are now effectively banned for sale to China, and even downgraded versions face scrutiny. The result has been a forced march toward self-sufficiency, with Alibaba, Huawei, and Baidu all investing billions in domestic chip design.

The T-Head processor is not yet competitive with NVIDIA's H100 or the forthcoming B200 in raw performance. But it doesn't need to be. For the Chinese domestic market — which represents the world's second-largest AI workload — a chip that is "good enough" and available without geopolitical risk is a powerful proposition.

## Where India Fits

India's semiconductor ambitions have been loudly declared but slowly executed. The government has committed $10 billion through the India Semiconductor Mission to attract chip fabrication plants, and the Tata Group's partnership with Taiwan's PSMC to build a fab in Gujarat has been celebrated as a milestone. But India's first commercial chips are years away from production, and the country remains almost entirely dependent on imports for the processors that power its growing AI ecosystem.

Meanwhile, Big Tech is pouring money into India at an unprecedented rate. Microsoft, Amazon, and Google have collectively committed over $50 billion in Indian AI and cloud infrastructure over the next five to seven years, following Prime Minister Modi's meetings with tech CEOs. But that investment is in data centres and cloud services — not in the chips that run inside them.

The Alibaba announcement poses a pointed question: if China can design competitive AI processors under sanctions pressure, why can't India? The answer is partly time — India's chip ecosystem is a decade behind China's — and partly talent, which is the one area where India has an undeniable advantage.

## The Diaspora Chip Connection

Indian-American engineers are not just participants in the global semiconductor industry; they lead it. NVIDIA's Jensen Huang relies heavily on Indian engineering talent in his chip design teams. AMD's CEO Lisa Su competes with teams that include hundreds of Indian-origin engineers. Qualcomm's largest R&D centre outside the US is in Hyderabad. And a generation of Indian chip designers trained at Texas Instruments' Bangalore campus in the 1990s now hold senior positions across Silicon Valley's semiconductor firms.

The question India faces is whether it can attract that talent back — or at least harness it remotely — to accelerate its own chip design capabilities. The government's Semicon India programme has earmarked funds for design-linked incentives, but the payoffs are measured in decades, not quarters.

## The AI Agent Angle

Alibaba's specific focus on AI agent workloads is significant because it reflects where the industry is heading. Google CEO Sundar Pichai declared 2026 "the year of the AI agent" at Google I/O. OpenAI, Anthropic, and Microsoft are all building agent frameworks that require sustained, memory-intensive computation — exactly the kind of workload that needs specialised silicon rather than general-purpose GPUs.

India's AI startups — now numbering over 3,000 according to NASSCOM — are largely consumers of American chips through cloud providers. If the chip supply chain fragments further along geopolitical lines, Indian companies could find themselves choosing between American, Chinese, and eventually domestic silicon based on cost, availability, and political alignment.

For Indian-American engineers straddling both worlds, the Alibaba chip is a reminder that the industry they helped build is fracturing — and that India's role in the next chapter is still being written.""",
    "word_count": 750,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 5: SPORTS — IPL 2026 Playoffs, CSK-MI Dynasty Ends
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "The IPL's Two Greatest Dynasties Just Died Together. CSK and MI Are Both Out — and Indian Cricket May Never Be the Same.",
    "subheadline": "For the first time since 2022, neither Chennai Super Kings nor Mumbai Indians made the IPL playoffs. With Dhoni's future in doubt and Rohit ageing out of T20 dominance, the league's power centre has shifted to Bengaluru, Hyderabad, and Ahmedabad.",
    "slug": make_slug("ipl-2026-csk-mi-out-playoffs-dynasty-ends-rcb-gt-srh"),
    "category": "sports",
    "vertical": "sports",
    "diaspora_angle": "CSK and MI aren't just cricket teams for NRIs — they're cultural identities. In sports bars from Edison to Fremont, the yellow and blue jerseys defined IPL watch parties for over a decade. Their simultaneous exit marks the end of an era that shaped how the diaspora consumed Indian cricket.",
    "tags": ["IPL 2026", "CSK", "MI", "playoffs", "MS Dhoni", "RCB", "Gujarat Titans", "Sunrisers Hyderabad", "cricket"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Mykhel — IPL 2026 Points Table after SRH beat RCB", "url": "https://www.mykhel.com"},
        {"name": "Mykhel — IPL Seasons When CSK-MI Duopoly Ended", "url": "https://www.mykhel.com"},
        {"name": "LatestLY — CSK defeat impacts playoff scenarios", "url": "https://www.latestly.com"},
        {"name": "Sporting News — Teams eliminated from IPL 2026", "url": "https://www.sportingnews.com"},
        {"name": "MensXP — LSG and MI still have a hand in fates", "url": "https://www.mensxp.com"}
    ]),
    "score_total": 78,
    "status": "published",
    "published_at": now,
    "body": """It happened quietly, the way dynasties usually end — not with a dramatic last stand but with a slow bleed of dropped catches, failed run chases, and a points table that stopped caring about legacy.

Chennai Super Kings were officially eliminated from IPL 2026 on Wednesday night after an 89-run demolition at the hands of Gujarat Titans. Mumbai Indians had already been mathematically dead for a week. Lucknow Super Giants joined them in the departure lounge. And just like that, for the first time since 2022, the two franchises that have defined the Indian Premier League for the better part of two decades will watch the playoffs from home.

Combined, CSK and MI have won 10 IPL titles. They have produced the tournament's two most iconic captains in MS Dhoni and Rohit Sharma. They have shaped auction strategy, defined franchise culture, and generated more WhatsApp-group arguments among NRIs than any other topic short of India-Pakistan matches.

Their simultaneous exit is not a blip. It is a generational shift.

## How CSK Fell

CSK's 2026 season was defined by inconsistency masked as competitiveness. They won enough matches early to stay in the conversation, but their net run rate — the tiebreaker that ultimately matters in a 10-team league — was bleeding from mid-April onward. The Gujarat loss was merely the final arithmetic.

The larger story is biological. Dhoni, at 44, was ruled out of CSK's final league match with an undisclosed injury, and the franchise's reluctance to name a succession plan has left them in a strategic limbo that no amount of auction spending can fix. Ruturaj Gaikwad has captained admirably in Dhoni's absences, but CSK's identity has been so tightly wound around one man that his eventual departure — whenever it comes — will require a reinvention, not a transition.

## MI's Quiet Decline

Mumbai Indians' fall has been less dramatic but more structural. The team that won five titles between 2013 and 2020 has now missed the playoffs in four of the last six seasons. Rohit Sharma, who turned 39 during the tournament, no longer dominates T20 bowling the way he once did. The mega-auction acquisitions that were supposed to rebuild the squad around Suryakumar Yadav have produced uneven returns.

MI's problem is not talent — it's configuration. In an IPL increasingly dominated by explosive top-order batting and death-overs specialists, MI's squad balance has looked a step behind the pace. Their bowling attack, once the tournament's most feared, has been inconsistent, and the middle-order collapses that were rare in the Rohit-Hardik era have become a pattern.

## The New Power Centre

The playoffs will be contested by Royal Challengers Bengaluru, Gujarat Titans, and Sunrisers Hyderabad, with the fourth spot still being fought over by Rajasthan Royals, Punjab Kings, Kolkata Knight Riders, and Delhi Capitals as the league stage enters its final weekend.

RCB, leading the table with 18 points, are having their best season in years — a vindication of the Virat Kohli-led batting machine and a bowling unit that has finally found consistency. Gujarat Titans, the 2022 champions, have powered through on the back of ruthless middle-overs batting and Rashid Khan's continued brilliance. SRH's explosive style — they chased down a target in 11 overs earlier this week — has made them the most watchable team in the tournament.

The subplot to watch is whether this year produces a first-time champion. Among the still-alive franchises, Punjab Kings, Delhi Capitals, and Lucknow Super Giants have never won the title. If one of them sneaks into the fourth playoff spot and rides momentum, the IPL's competitive landscape will have fundamentally changed.

## What the Diaspora Feels

In NRI cricket communities from New Jersey's Edison to the Bay Area's Fremont, the CSK-MI rivalry was the IPL's emotional backbone. Watch parties organised around the four annual CSK-MI fixtures drew crowds that rivalled India-Pakistan viewership. Fantasy leagues were built on the assumption that Dhoni would find a way and Rohit would come good.

This season, those watch parties have thinned. The die-hards remain, but the casual fans — the ones who tuned in because CSK vs MI was an event, not just a match — have drifted toward RCB's storyline or checked out of the league stage entirely, waiting for the playoffs.

## What Comes Next

The IPL's structure ensures that no dynasty is truly dead — the mega-auction cycle, scheduled for next year, will give both CSK and MI the chance to rebuild from scratch. But rebuilding requires hard choices: releasing ageing stars, investing in unproven domestic talent, and accepting that the next era will look nothing like the last one.

For Dhoni, the question is whether he returns at all. For Rohit, it is whether he accepts a diminished role. For the millions of NRI fans who grew up believing that yellow and blue would always be in the final four, it is something simpler and harder: learning to love a league that no longer revolves around them.""",
    "word_count": 850,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# INSERT ALL ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"Inserting {len(articles)} articles...")
success = 0
for i, article in enumerate(articles):
    try:
        result = sb_post("p2_articles", article)
        if isinstance(result, list) and len(result) > 0:
            print(f"  ✅ [{article['category']}] {article['headline'][:70]}...")
            success += 1
        elif isinstance(result, dict) and result.get("id"):
            print(f"  ✅ [{article['category']}] {article['headline'][:70]}...")
            success += 1
        else:
            print(f"  ⚠️  [{article['category']}] Response: {json.dumps(result)[:200]}")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ [{article['category']}] Error: {e}")
        print(f"     Response: {e.response.text[:300]}")
    except Exception as e:
        print(f"  ❌ [{article['category']}] Error: {e}")

print(f"\nDone: {success}/{len(articles)} articles published.")
