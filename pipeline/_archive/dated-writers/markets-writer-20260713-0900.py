#!/usr/bin/env python3
"""Markets & Finance writer — 2026-07-13 09:00 PT batch."""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

# ─────────────────────────────────────────────
# ARTICLE 1: Rupee + Trade Deficit
# ─────────────────────────────────────────────
art1_headline = "Rupee Slides to One-Month Low as India's Trade Deficit Balloons to $30.43 Billion — What NRI Remitters Need to Know"
art1_subheadline = "Brent crude's 3% spike to $78 on renewed Hormuz tensions, a wider-than-expected trade gap, and looming CPI data are piling pressure on the Indian currency — and creating a narrow window for diaspora money movers."
art1_slug = make_slug("rupee-one-month-low-trade-deficit-30-billion-nri-remittance")
art1_body = """The Indian rupee closed at 95.62 per dollar on Monday, its weakest level in more than a month, after touching an intraday low of 95.85 as a fresh round of U.S.-Iran military strikes sent oil prices surging and revived fears of a prolonged Strait of Hormuz closure.

Brent crude jumped 3% to $78 per barrel after Tehran said it had again shut the vital shipping chokepoint through which roughly a fifth of the world's oil transits. For India — the world's third-largest energy importer — the timing could hardly be worse.

## A Trade Gap That Caught Markets Off Guard

Data released Monday showed India's merchandise trade deficit widened to $30.43 billion in June, sharply overshooting the $26.63 billion Reuters consensus and up from $28.21 billion in May. Merchandise exports fell to $40.41 billion from $45.2 billion the previous month, while imports eased only modestly to $70.84 billion from $73.41 billion.

The silver lining: India's services trade surplus stood at an estimated $15.11 billion in June, driven by IT exports and professional services, partially offsetting the goods gap. On a quarterly basis, overall goods exports still rose about 15% year-on-year in April-June despite the Middle East disruptions, buoyed by pricier petroleum shipments.

But currency traders aren't looking at the bright side. The 1-month 25-delta dollar-rupee risk reversal — a key options market gauge of depreciation risk — drifted to 0.3 from nearly zero at the start of July, signaling that bets on a weaker rupee have decisively overtaken wagers on appreciation.

"The rupee's sensitivity to headlines will likely remain elevated in the near future and demand a more assertive market presence by the Reserve Bank of India to limit sharp moves," a trader at a state-run bank told Reuters.

## Rate Hikes Are Coming

The rupee's decline arrives just as India prepares to release June consumer inflation data, which a Reuters poll expects to show CPI breaching the RBI's 4% medium-term target for the first time in 16 months. India's inflation rate had already risen to 3.9% in May from 3.5% in April.

Goldman Sachs analysts now expect the RBI to hike rates by 25 basis points each in October and December 2026, while swap markets are pricing in a similar quantum of tightening over the next 12 months. OCBC Bank's Lavanya Venkateswaran projects a "shallow rate hiking cycle" of a cumulative 50 basis points through early 2027.

Higher rates would support the rupee but could slow growth and weigh on equity valuations — a trade-off the central bank has been trying to avoid after cutting rates earlier this year to stimulate the economy.

## What This Means for NRI Money

For the Indian American diaspora, the rupee's slide is a double-edged sword.

**Remittances get a boost.** At 95.62 to the dollar, a $1,000 remittance converts to roughly ₹95,620 — about ₹2,300 more than the same transfer would have yielded at the year's best rate of 93.30 in late June. For families sending $2,000-3,000 home monthly, that's a meaningful difference over a year.

**But the window may not last.** Goldman's upgraded growth forecast of 6.8% for India in 2026, combined with anticipated RBI intervention and the potential resolution of Hormuz tensions, suggests the rupee's weakness could be temporary. Traders noted that Monday's losses would have been steeper without suspected central bank dollar sales.

**NRE/NRO depositors face a crossroads.** If the RBI does hike rates later this year, NRE fixed deposit rates — currently hovering around 6.5-7% for one-year tenures at major banks — could tick higher, making rupee deposits more attractive for NRIs willing to take the currency risk.

**Bond investors should watch the Bloomberg decision.** India's potential inclusion in the Bloomberg Global Aggregate Index, expected to be announced this month, could channel billions more in foreign inflows into government bonds. Foreign investors have already net bought over $4.1 billion in bonds since June 1 under the Fully Accessible Route. An index inclusion would structurally support the rupee and compress yields, rewarding early movers.

The bottom line: the rupee is under genuine pressure from oil, inflation, and a ballooning trade deficit, but India's macro fundamentals — resilient exports, strong services surplus, and a $667 billion forex reserve war chest — argue against a sustained rout. For NRIs timing remittances or evaluating rupee-denominated investments, the next two weeks of data (CPI, WPI, Bloomberg index decision, forex reserves) will be decisive."""

# ─────────────────────────────────────────────
# ARTICLE 2: IT Stocks Rally / AI Deals
# ─────────────────────────────────────────────
art2_headline = "India's IT Stocks Stage a 10% July Rally as AI Deals Reshape the Sector — Why the Street Is Still Skeptical"
art2_subheadline = "TCS, HCLTech, and LTIMindtree surged on Monday as Anthropic partnerships and a mega ABB deal gave the beaten-down sector its best month of 2026 — but analysts warn this is trading, not conviction."
art2_slug = make_slug("india-it-stocks-10-percent-july-rally-ai-deals-tcs-hcltech")
art2_body = """India's IT stocks soared 3.6% on Monday to a one-month high, capping a remarkable July rally that has seen the Nifty IT index climb 10.3% even as the sector remains down nearly 23% for the year.

The catalyst: a wave of high-profile AI partnerships that suggest India's $315 billion IT services industry may be finding its footing in the age of artificial intelligence, rather than being disrupted by it.

## The Deals Driving the Rally

**Tata Consultancy Services** jumped 5.4% on Monday after announcing a multi-million dollar deal with Swiss industrial giant ABB, adding to the momentum from its June partnership with Anthropic. Under that earlier agreement, TCS created a dedicated business unit for deploying Anthropic's Claude AI models, gained early access to new model releases, and committed to providing Claude to its 50,000-strong workforce. The ABB deal signals that the Anthropic investment is already translating into enterprise revenue.

**LTIMindtree** rose 2.2% on news of its own partnership with Anthropic to accelerate Claude adoption across enterprise clients, joining a growing roster of Indian IT firms embedding frontier AI into their service offerings.

**HCLTech** climbed 4.9% ahead of its quarterly earnings release later Monday, with investors betting that the company — which has its own partnerships with OpenAI — would deliver results in line with TCS's recent beat.

The broader context: Anthropic has described India as its second-largest market and has opened offices, hired leadership, and expanded ties with every major Indian IT services firm over the past year. Infosys announced its own Anthropic collaboration in late June, while OpenAI has roped in both Infosys and HCLTech.

## Why Analysts Are Cautious

Despite the rally, the Street isn't declaring victory.

"What we are seeing in the IT sector is more of trading and tactical calls in beaten-down stocks rather than a structural buy call," said Dharmesh Kant, head of equity research at Cholamandalam Securities.

The math supports the skepticism. IT stocks are still down 23% year-to-date, reflecting deep investor anxiety about whether AI will ultimately reduce demand for the labor-intensive services model that Indian IT companies have built over three decades. TCS and Infosys shares have fallen roughly 34% and 31% respectively in 2026 alone.

The fear: if tools like Claude Code can write, test, and debug software autonomously — and Anthropic now holds over half the AI coding market — enterprise clients may need fewer human developers, not more. Every AI partnership announcement carries this tension: Indian IT firms are simultaneously selling AI deployment services and facing the possibility that AI could cannibalize their core business.

## The Global Rotation Angle

There's another force behind the rally that has nothing to do with AI deals. South Korea's benchmark KOSPI index sank 7.6% on Monday — having already lost almost 8% the previous week — as leveraged bets on semiconductor shares came under intense pressure.

"The drawdown in AI-heavy markets clearly indicates that investors are churning money out of heavily bought-into markets and looking at other emerging markets like India, which also benefits from easing of crude oil prices," said Sunny Agrawal, head of fundamental equity research at SBICAPS Securities.

In other words, some of the money flowing into Indian IT isn't a vote of confidence in the sector — it's capital fleeing overheated AI plays elsewhere and looking for relatively cheaper emerging market exposure.

## What NRI Investors Should Consider

For diaspora investors with exposure to Indian IT — through direct equity holdings, ETFs like the iShares MSCI India ETF (INDA), or NRI demat accounts — the July rally raises a tactical question: is this the start of a genuine re-rating, or a bear market bounce?

**The bull case:** India's IT firms are repositioning as AI implementation partners, not just body shops. TCS's AI business has already crossed $2.6 billion in revenue (as reported in its Q1 FY27 results last week). Anthropic's aggressive courting of Indian partners suggests the industry has distribution advantages that pure AI companies need.

**The bear case:** The 23% YTD decline reflects structural concerns that won't be resolved by a few partnership announcements. AI coding tools are getting better faster than Indian IT firms can retrain their workforce. And the sector's traditional growth engine — discretionary tech spending by Western enterprises — remains under pressure from higher interest rates and geopolitical uncertainty.

**The pragmatic move:** With Nifty IT still trading at a significant discount to its October 2024 highs, cost-averaging into quality names (TCS, Infosys, HCLTech) during dips has historically rewarded patient NRI investors over three-to-five-year horizons. But this is not the time for concentrated bets on a sector in the middle of an existential transition."""

# ─────────────────────────────────────────────
# ARTICLE 3: India-US Trade Talks
# ─────────────────────────────────────────────
art3_headline = "India Isn't Rushing Into a US Trade Deal — And Goldman Sachs Just Gave Modi Another Reason to Wait"
art3_subheadline = "With exports up 15%, a UK free trade pact about to kick in, and an upgraded 6.8% growth forecast, New Delhi is playing the long game on tariffs — even as Washington threatens to raise the stakes this month."
art3_slug = make_slug("india-us-trade-deal-standoff-goldman-growth-uk-fta-nri")
art3_body = """India and the United States failed to finalize an interim trade agreement during U.S. Trade Representative Jamieson Greer's visit to New Delhi last month, despite expectations on both sides that a limited deal was within reach. But unlike previous rounds of trade friction, this time India doesn't appear worried.

"Our position is clear — we don't intend to rush into a deal that is not on favourable terms or compromise on red lines like ceding ground on agriculture," an Indian government official aware of the talks told Reuters on Monday.

The reason for New Delhi's confidence is increasingly quantifiable.

## The Numbers Behind India's Leverage

Goldman Sachs has raised its 2026 growth forecast for India to 6.8%, up from its earlier estimate, citing the interim U.S.-Iran peace deal that briefly eased oil prices and improved India's economic outlook. The bank has simultaneously lowered its inflation and current-account deficit projections, giving New Delhi more room to negotiate from a position of strength.

India's overall goods exports rose approximately 15% year-on-year in April-June 2026, even as the Middle East conflict disrupted shipping through the Strait of Hormuz. Exports to Gulf countries recovered to pre-war levels, hitting $5.3 billion in May versus $2.62 billion in March, as Indian traders shifted to alternative shipping routes. Exports to the United States edged up to $17.29 billion during April and May combined.

And India is diversifying its trade relationships at speed. A UK free trade agreement is set to take effect this month — India's first comprehensive FTA with a major developed economy. An EU trade deal is expected by early next year.

"Indian negotiators have gained some leverage in the talks, given its strong economy, diversification initiatives with other partners, and its strategic standing in the world," said Wendy Cutler, senior vice president at the Washington-based Asia Society Policy Institute and a former U.S. trade negotiator.

## What India Wants — And What Washington Won't Give

The sticking points are specific and politically charged.

India's two core demands: a preferential tariff rate that gives it an edge over competitors like China, and a guarantee that Washington won't impose additional tariffs after the deal is signed. Both are likely non-starters for the Trump administration, which has built its trade policy around flexibility and maximum leverage.

Currently, the bulk of Indian goods face a 10% U.S. tariff — the baseline rate that applies to most countries following the Supreme Court's ruling invalidating President Trump's sweeping global tariff regime. But the administration is expected to introduce steeper tariffs later this month through probes into excess industrial capacity, a charge India has denied.

On top of that, Washington has proposed new tariffs of up to 12.5% on dozens of nations, including India, over allegations that they failed to curb trade in goods produced with forced labor. U.S.-India Business Council President Atul Keshap characterized this as "certainly an element of the negotiation" rather than a standalone punitive measure.

India's Trade Secretary Rajesh Agrawal struck a measured tone: "The framework deal is ready. Whenever it is the right time, it will be signed."

A U.S. official, speaking anonymously, said Washington remained engaged but added that India had at times been "slow, bureaucratic and difficult" in negotiations.

## Why India Is Betting on Time

New Delhi's calculus extends beyond economics. Indian officials believe some U.S. trade measures could face legal or political setbacks at home. A group of 22 Democratic state attorneys general have already filed objections to the Trump administration's proposed forced labor tariffs, and the Supreme Court ruling that struck down the initial tariff wave has created a legal cloud over new measures.

Prime Minister Modi's recent state election victories have also strengthened his domestic position, giving him more room to resist a rushed deal. Senior BJP leaders have publicly argued that any trade agreement must protect Indian farmers and small businesses — two politically influential constituencies that New Delhi has historically shielded.

"India realises that delaying — or even abandoning — a rushed deal may be more prudent than locking into obligations whose costs could far exceed any temporary tariff relief," said Ajay Srivastava, founder of the Global Trade Research Initiative and a former Indian trade negotiator.

## The NRI Stakes

For the Indian American diaspora, the trade standoff cuts multiple ways.

**IT services are the big exposure.** Indian IT companies — TCS, Infosys, Wipro, HCLTech — derive 50-60% of their revenue from U.S. clients. Any escalation in tariffs or trade friction could chill the enterprise spending environment that these firms depend on. The sector is already down 23% year-to-date.

**The $500 billion bilateral trade aspiration.** Keshap of the U.S.-India Business Council called the current $180-odd billion in annual bilateral trade "woefully underpowered" and urged both sides to close a deal that could push the relationship toward $500 billion. For NRI entrepreneurs and investors operating across both economies, a comprehensive trade agreement would reduce compliance costs, ease cross-border investment flows, and unlock opportunities in sectors like defense, agriculture, and digital services.

**Remittances and capital flows.** The rupee's weakness — it closed at 95.62 on Monday — is partly a function of trade uncertainty. A deal that stabilizes expectations would support the currency and reduce volatility in NRE/NRO deposit returns.

The bottom line: India is playing a longer game than Washington expected, and the math increasingly supports New Delhi's patience. For the diaspora community watching from both sides, the question isn't whether a deal happens — it's whether either side can afford the political cost of the one they'll eventually have to sign."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": art1_headline,
        "subheadline": art1_subheadline,
        "slug": art1_slug,
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Rupee weakness creates remittance opportunity for NRIs; NRE deposit rates may rise if RBI hikes; Bloomberg index inclusion could reward early bond investors.",
        "tags": ["markets", "finance", "rupee", "trade-deficit", "nri-investing", "remittance", "rbi"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/rupee-braces-pressure-with-oil-taking-centre-stage-us-iran-flare-up-2026-07-13/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-rupee-bonds-likely-track-mideast-developments-inflation-data-2026-07-13/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-june-merchandise-trade-deficit-widens-3043-bln-2026-07-13/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg/1280px-BSE_-_Bombay_Stock_Exchange_Building.jpg",
        "image_caption": "The Bombay Stock Exchange building on Dalal Street, Mumbai",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art2_headline,
        "subheadline": art2_subheadline,
        "slug": art2_slug,
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "NRI investors hold significant IT stock exposure through direct equity and ETFs; AI partnerships could signal a structural shift or just a bear market bounce — the distinction matters for long-term portfolios.",
        "tags": ["markets", "finance", "it-stocks", "tcs", "hcltech", "ltimindtree", "anthropic", "ai", "nri-investing"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-shares-seen-opening-lower-fresh-mideast-tensions-lift-oil-prices-2026-07-13/"},
            {"name": "TechCrunch", "url": "https://techcrunch.com/2026/06/11/anthropic-taps-tcs-to-scale-its-enterprise-ai-deployments/"},
            {"name": "Cholamandalam Securities / Reuters", "url": "https://www.reuters.com/world/india/indian-shares-seen-opening-lower-fresh-mideast-tensions-lift-oil-prices-2026-07-13/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg/1280px-Aerial_view_of_the_Glass_Pyramid_at_the_Infosys_Campus.jpg",
        "image_caption": "The glass pyramid at Infosys campus in Bangalore, a symbol of India's IT industry",
        "image_attribution": "Wikimedia Commons, CC BY-SA 4.0",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": art3_headline,
        "subheadline": art3_subheadline,
        "slug": art3_slug,
        "category": "markets-finance",
        "vertical": "markets-finance",
        "diaspora_angle": "Trade deal impacts IT services revenue (50-60% from US), bilateral trade aspiration to $500B affects NRI entrepreneurs, and trade uncertainty contributes to rupee volatility affecting remittances and NRE deposits.",
        "tags": ["markets", "finance", "india-us-trade", "tariffs", "nri-business", "trade-deal", "exports"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/markets/emerging/an-emboldened-india-holds-out-better-terms-us-trade-talks-2026-07-13/"},
            {"name": "Reuters", "url": "https://www.reuters.com/world/india/india-us-trade-talks-progressing-well-india-trade-secretary-says-2026-07-13/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/proposed-12-5-us-tariff-over-forced-labor-on-indian-goods-is-part-of-trade-negotiations-atul-keshap/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "Indian Commerce Minister Piyush Goyal has described the trade talks as balanced and productive",
        "image_attribution": "Government of India / Wikimedia Commons, GODL-India",
        "body": art3_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
